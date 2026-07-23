"""SAD API — backend FastAPI de solo lectura sobre el pipeline SQLite.

Implementa el contrato docs/openapi.yaml del repo App-Profesional-de-Apuestas
(el frontend web lo consume con VITE_DATA_SOURCE=http). v0: sin escrituras;
auth bearer opcional (SAD_API_TOKEN), rate limit por IP (SAD_RATE_LIMIT),
CORS solo local salvo SAD_CORS_ORIGINS, docs desactivables (SAD_DOCS).

Ejecutar junto a las DBs reales:
    uvicorn backend.app:app --port 8000
"""
import json
import os
import re
import secrets
import sqlite3
import subprocess
import sys
import threading
import time
import unicodedata
from datetime import date as date_t, datetime, timedelta, timezone
from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend import db

# /docs, /redoc y /openapi.json: encendidos en local, apagados por defecto en
# cuanto hay token (despliegue). SAD_DOCS=1/0 fuerza el comportamiento.
_DOCS_ON = os.environ.get("SAD_DOCS", "0" if os.environ.get("SAD_API_TOKEN") else "1").strip().lower() in {"1", "true", "si", "sí", "yes"}

app = FastAPI(
    title="SAD API",
    version="0.1.0",
    docs_url="/docs" if _DOCS_ON else None,
    redoc_url="/redoc" if _DOCS_ON else None,
    openapi_url="/openapi.json" if _DOCS_ON else None,
)

API = "/api/v1"

# Auth bearer opcional: sin SAD_API_TOKEN la API queda abierta (uso local);
# con token, todo salvo /health y docs exige `Authorization: Bearer <token>`.
# Se leen los globals en cada request para poder monkeypatchearlos en tests.
API_TOKEN = os.environ.get("SAD_API_TOKEN", "")
_AUTH_EXEMPT = {f"{API}/health", "/docs", "/redoc", "/openapi.json"}


@app.middleware("http")
async def auth_bearer(request: Request, call_next):
    if API_TOKEN and request.url.path not in _AUTH_EXEMPT:
        auth = request.headers.get("authorization", "")
        if not (auth.startswith("Bearer ") and secrets.compare_digest(auth[7:], API_TOKEN)):
            return JSONResponse(
                {"detail": "No autorizado"}, status_code=401, headers={"WWW-Authenticate": "Bearer"}
            )
    return await call_next(request)


# Rate limit en memoria por IP, ventana fija de 60 s (SAD_RATE_LIMIT req/min,
# 0 = apagado). Detrás de un proxy inverso la IP vista es la del proxy: en un
# despliegue real hay que limitar también en el proxy o propagar la IP real.
RATE_LIMIT = int(os.environ.get("SAD_RATE_LIMIT", "120"))
_hits: dict[str, tuple[int, int]] = {}


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    if RATE_LIMIT > 0:
        ip = request.client.host if request.client else "?"
        window = int(time.monotonic() // 60)
        prev_window, count = _hits.get(ip, (window, 0))
        if prev_window != window:
            count = 0
        if count >= RATE_LIMIT:
            return JSONResponse(
                {"detail": "Demasiadas peticiones"}, status_code=429, headers={"Retry-After": "60"}
            )
        if len(_hits) > 10_000:
            _hits.clear()
        _hits[ip] = (window, count + 1)
    return await call_next(request)


# CORS se registra el último para que envuelva a auth y rate limit (los 401/429
# también deben llevar cabeceras CORS). Sin SAD_CORS_ORIGINS solo se permiten
# los orígenes de desarrollo local; en despliegue, fijar el dominio real.
_DEV_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ.get("SAD_CORS_ORIGINS", _DEV_ORIGINS).split(",") if o.strip()],
    # POST: los endpoints de análisis EFE (/analisis/efe) — el preflight del
    # navegador se rechazaba con solo GET y el POST ni salía ("Failed to fetch")
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Ingesta programada opcional (despliegue de un solo servicio: el volumen de
# Railway solo se monta en un servicio, así que el cron vive aquí dentro).
# SAD_INGESTA_HORA=HH:MM[,HH:MM…] (UTC) lanza backend.ingesta.corrida_diaria
# en subproceso a cada hora de la lista (varias corridas/día = varios snapshots
# de cuotas en odds_history). El backend HTTP sigue siendo de solo lectura:
# quien escribe es la capa de ingesta; aquí solo se programa.
INGESTA_HORA = os.environ.get("SAD_INGESTA_HORA", "").strip()


def _ingesta_diaria_loop() -> None:
    horas = sorted(
        (int(hh), int(mm))
        for hh, mm in (x.strip().split(":") for x in INGESTA_HORA.split(",") if x.strip())
    )
    while True:
        ahora = datetime.now(timezone.utc)
        candidatos = (ahora.replace(hour=hh, minute=mm, second=0, microsecond=0) for hh, mm in horas)
        objetivo = min(c if c > ahora else c + timedelta(days=1) for c in candidatos)
        time.sleep((objetivo - ahora).total_seconds())
        print(f"[ingesta] corrida diaria {datetime.now(timezone.utc).isoformat()}", flush=True)
        subprocess.run([sys.executable, "-u", "-m", "backend.ingesta.corrida_diaria"])
        liga_meta.cache_clear()  # puede haber ligas nuevas en sad.db
        _correr_backfill("tras la corrida diaria")  # reanuda si quedó a medias


if INGESTA_HORA:
    threading.Thread(target=_ingesta_diaria_loop, daemon=True, name="ingesta-diaria").start()

# SAD_INGESTA_AL_ARRANCAR=1 dispara UNA corrida diaria completa (ventana por
# fecha + cuotas + sanar_90 + sanar_fechas + purga de ligas no seguidas) a los
# ~40 s del arranque, sin esperar a SAD_INGESTA_HORA. Para aplicar un parche de
# ingesta "lo antes posible" tras un deploy; el backfill ya corre solo al
# arrancar, esto añade la parte de curación por fecha y la limpieza de zombis.
INGESTA_AL_ARRANCAR = os.environ.get("SAD_INGESTA_AL_ARRANCAR", "").strip().lower() in (
    "1", "true", "si", "sí", "yes", "on"
)


def _corrida_al_arranque() -> None:
    time.sleep(40)  # tras el arranque; después del backfill_arranque (30 s) para no solaparse
    print(f"[ingesta] corrida diaria al arranque {datetime.now(timezone.utc).isoformat()}", flush=True)
    subprocess.run([sys.executable, "-u", "-m", "backend.ingesta.corrida_diaria"])
    liga_meta.cache_clear()


if INGESTA_AL_ARRANCAR:
    threading.Thread(target=_corrida_al_arranque, daemon=True, name="corrida-arranque").start()

# Backfill histórico: SAD_BACKFILL_DESDE=2020 trae los fixtures de TODAS las
# ligas de la lista desde esa temporada. Corre al arrancar y tras cada corrida
# diaria; el extractor lleva el progreso en .backfill_hist.json (en el volumen)
# y cuando está completo sale con 0 requests, así que puede quedarse puesta.
BACKFILL_DESDE = os.environ.get("SAD_BACKFILL_DESDE", "").strip()


def _correr_backfill(motivo: str) -> None:
    if not BACKFILL_DESDE:
        return
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = {**os.environ, "PYTHONPATH": raiz, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    print(f"[ingesta] backfill histórico desde {BACKFILL_DESDE} ({motivo})", flush=True)
    subprocess.run(
        [sys.executable, "-u", "-m", "backend.ingesta.extractor", "--historico", BACKFILL_DESDE],
        cwd=db.BASE_DIR, env=env,
    )
    # niveles/constantes de las temporadas nuevas: el pipeline es local (0 requests)
    subprocess.run(
        [sys.executable, "-u", "-m", "backend.ingesta.pipeline", "--out", "."],
        cwd=db.BASE_DIR, env=env,
    )
    liga_meta.cache_clear()


def _backfill_arranque() -> None:
    time.sleep(30)  # dejar que el server termine de arrancar y sirva tráfico
    _correr_backfill("arranque")


if BACKFILL_DESDE:
    threading.Thread(target=_backfill_arranque, daemon=True, name="backfill-historico").start()

# Relleno puntual de fechas (one-shot al arranque): SAD_RELLENO_FECHAS="2026-05-31"
# o un rango "2026-05-01:2026-06-05" re-pide /fixtures POR FECHA en ese tramo
# (todas las temporadas, filtrado a nuestras ligas) y regenera el pipeline.
# Es la palanca para tapar A MANO un hueco detectado —p. ej. el 31/05 de las
# ligas de año cruzado que la ventana por temporada nunca vio— y verlo en los
# logs sin esperar a la corrida programada. Sirve para fechas de CUALQUIER
# temporada porque pide por fecha. Es idempotente pero gasta requests en cada
# arranque: quitar la variable cuando el hueco quede tapado.
RELLENO_FECHAS = os.environ.get("SAD_RELLENO_FECHAS", "").strip()


def _relleno_fechas_arranque() -> None:
    desde, _, hasta = RELLENO_FECHAS.partition(":")
    desde, hasta = desde.strip(), (hasta.strip() or desde.strip())
    try:  # una variable con formato inválido no debe tumbar el hilo en silencio
        datetime.strptime(desde, "%Y-%m-%d")
        datetime.strptime(hasta, "%Y-%m-%d")
    except ValueError:
        print(f"[ingesta] SAD_RELLENO_FECHAS inválida ({RELLENO_FECHAS!r}; "
              f"formato YYYY-MM-DD o YYYY-MM-DD:YYYY-MM-DD) — se ignora", flush=True)
        return
    time.sleep(35)  # tras el arranque del server (y del backfill_arranque, que espera 30 s)
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = {**os.environ, "PYTHONPATH": raiz, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    print(f"[ingesta] relleno puntual de fechas {desde} → {hasta} (arranque)", flush=True)
    subprocess.run(
        [sys.executable, "-u", "-m", "backend.ingesta.extractor",
         "--desde", desde, "--hasta", hasta, "--solo", "fixtures"],
        cwd=db.BASE_DIR, env=env,
    )
    # niveles/constantes de lo recién rellenado (pipeline local, 0 requests)
    subprocess.run(
        [sys.executable, "-u", "-m", "backend.ingesta.pipeline", "--out", "."],
        cwd=db.BASE_DIR, env=env,
    )
    liga_meta.cache_clear()


if RELLENO_FECHAS:
    threading.Thread(target=_relleno_fechas_arranque, daemon=True, name="relleno-fechas").start()

# Refresco de día de partido (fase 2 de docs/EXTRACCION_TIEMPO_REAL.md):
# SAD_REFRESCO_MIN=30 corre cada N minutos un extractor ligero (--ventana-horas 6:
# SOLO cuotas de NS que empiezan en <6 h). Sin partidos próximos el extractor
# sale con 0 requests, así que el bucle puede correr ciego. Vacía = apagado.
REFRESCO_MIN = os.environ.get("SAD_REFRESCO_MIN", "").strip()
REFRESCO_VENTANA_H = os.environ.get("SAD_REFRESCO_VENTANA_HORAS", "6").strip() or "6"


def _refresco_cuotas_loop() -> None:
    minutos = max(10, int(REFRESCO_MIN))  # piso de 10 min: más fino es fase 3 (en vivo)
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = {**os.environ, "PYTHONPATH": raiz, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    while True:
        time.sleep(minutos * 60)
        print(f"[ingesta] refresco de cuotas {datetime.now(timezone.utc).isoformat()}", flush=True)
        subprocess.run(
            [sys.executable, "-u", "-m", "backend.ingesta.extractor", "--ventana-horas", REFRESCO_VENTANA_H],
            cwd=db.BASE_DIR, env=env,
        )


if REFRESCO_MIN:
    threading.Thread(target=_refresco_cuotas_loop, daemon=True, name="refresco-cuotas").start()

# En vivo (fase 3 de docs/EXTRACCION_TIEMPO_REAL.md): SAD_LIVE_SEGUNDOS=60
# corre backend.ingesta.en_vivo cada N segundos (piso 30). El módulo decide
# solo: sin partidos en ventana de juego sale con 0 requests, así que el bucle
# corre ciego sin gastar presupuesto en horas muertas. Vacía = apagado.
LIVE_SEGUNDOS = os.environ.get("SAD_LIVE_SEGUNDOS", "").strip()


def _en_vivo_loop() -> None:
    segundos = max(30, int(LIVE_SEGUNDOS))
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = {**os.environ, "PYTHONPATH": raiz, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    while True:
        time.sleep(segundos)
        subprocess.run(
            [sys.executable, "-u", "-m", "backend.ingesta.en_vivo"],
            cwd=db.BASE_DIR, env=env,
        )


if LIVE_SEGUNDOS:
    threading.Thread(target=_en_vivo_loop, daemon=True, name="ingesta-en-vivo").start()

# Primera línea de los logs tras cada deploy: confirma qué quedó encendido.
# Si no aparece, el deploy corriendo es anterior a las fases 2/3.
print(
    f"[ingesta] programación → diaria: {INGESTA_HORA or 'apagada'} · "
    f"refresco: {REFRESCO_MIN + ' min' if REFRESCO_MIN else 'apagado'} · "
    f"en vivo: {LIVE_SEGUNDOS + ' s' if LIVE_SEGUNDOS else 'apagado'} · "
    f"backfill: {'desde ' + BACKFILL_DESDE if BACKFILL_DESDE else 'apagado'}"
    + (" · corrida al arranque" if INGESTA_AL_ARRANCAR else "")
    + (f" · relleno: {RELLENO_FECHAS}" if RELLENO_FECHAS else ""),
    flush=True,
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

LIVE_SHORT = {"1H", "HT", "2H", "ET", "BT", "P", "LIVE", "INT", "SUSP"}
FIN_SHORT = {"FT", "AET", "PEN", "AWD", "WO"}

# Bins fijos v6 (Ley del Marcador) — mismos umbrales que el discretizador
BINS = [
    (0.6, "Sin datos"), (1.3, "Muy débil"), (1.6, "Débil"), (1.9, "Regular bajo"),
    (2.1, "Promedio bajo"), (2.35, "Promedio"), (2.55, "Promedio alto"),
    (2.85, "Fuerte"), (3.2, "Muy fuerte"), (float("inf"), "Élite"),
]

# Ley de la Regresión al Nivel (§5) — μ v2 (2026-07): OLS sobre 10 000 obs de
# sad.db real (backtest_gap --calibrar); la v1 heredada (1.110/0.686/−0.669/
# 0.422) sobreestimaba a los favoritos en ~0.4 pts. Ver MOTOR_SAD_EXTRACCION.md §5.
MU = {"intercept": 1.241, "nivel": 0.334, "rival": -0.357, "localia": 0.382}
RECENT_WINDOW = 5

# Camino de recuperación (§5 v2): el gap dice dirección, el calendario futuro
# dice dónde puede expresarse. Banderas descriptivas: NO entran en μ ni en el gap.
RECOVERY_NEXT = 3        # próximos fixtures considerados
CAL_UMBRAL = 0.15        # blando/duro vs la μ genérica (provisional hasta backtest)
TRAMPA_VENTANA_DIAS = 4  # "grande" a ≤4 días del partido analizado
TRAMPA_DELTA_NIVEL = 0.8 # rival de hoy claramente inferior: nivel ≤ propio − 0.8
# estados que sacan un fixture del camino (pospuesto/cancelado/abandonado)
_NO_CAMINO = ("CANC", "PST", "ABD", "AWD", "WO")

# Ligas de torneos internacionales de clubes (ids de API-Football);
# ampliable con SAD_INTL_LEAGUE_IDS="2,3,848,..."
INTL_LEAGUE_IDS = {
    int(x) for x in os.environ.get("SAD_INTL_LEAGUE_IDS", "2,3,848,13,11,15,531").split(",") if x.strip()
}


def level_bin(level: float) -> tuple[int, str]:
    for i, (mx, label) in enumerate(BINS):
        if level < mx:
            return i, label
    return 9, "Élite"


def mu(nivel: float, nivel_rival: float, localia: float) -> float:
    v = MU["intercept"] + MU["nivel"] * nivel + MU["rival"] * nivel_rival + MU["localia"] * localia
    return max(0.0, min(3.0, v))


def iso(dt_text) -> str:
    """Normaliza el DATETIME de SQLite a ISO-8601 con 'T' (y Z si es naive)."""
    if dt_text is None:
        return ""
    s = str(dt_text).replace(" ", "T")
    if "." in s:
        s = s.split(".")[0]
    if not s.endswith("Z") and "+" not in s[10:]:
        s += "Z"
    return s


def _dt(dt_text) -> datetime:
    """DATETIME de SQLite (o ISO) → datetime naive."""
    s = str(dt_text).replace("T", " ").rstrip("Z").split(".")[0]
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(s[:10], "%Y-%m-%d")


def abrev(nombre: str) -> str:
    return (nombre or "???").replace(" ", "")[:3].upper()


def equipo_dto(team_id: int, nombre: str, logo: str | None = None) -> dict:
    return {"id": team_id, "nombre": nombre, "abreviatura": abrev(nombre), "logo": logo}


def estado_de(status_short, status_long) -> str:
    ss = (status_short or "").upper()
    if ss in LIVE_SHORT:
        return "en_vivo"
    if ss in FIN_SHORT or (status_long or "") == "Match Finished":
        return "finalizado"
    return "programado"


# Equivalente SQL de estado_de(): el filtro debe aplicarse ANTES del LIMIT
# (filtrar en Python devolvía menos filas de las pedidas o ninguna).
_SS = "COALESCE(UPPER(f.status_short),'')"
_EN_VIVO_SQL = f"{_SS} IN ({','.join('?' * len(LIVE_SHORT))})"
_FIN_SQL = f"({_SS} IN ({','.join('?' * len(FIN_SHORT))}) OR COALESCE(f.status_long,'')='Match Finished')"

# Resultado DENTRO DE LOS 90 MINUTOS: toda la matemática (K, gap §5, stats,
# tabla) usa fulltime_* — en partidos con prórroga/penales (AET/PEN) goals_*
# trae el marcador de los 120'. El marcador MOSTRADO en la UI sigue siendo el
# final real (goals_*). COALESCE cubre filas sin fulltime.
_G90_H = "COALESCE(f.fulltime_home, f.goals_home)"
_G90_A = "COALESCE(f.fulltime_away, f.goals_away)"
_FIN90_SQL = "(f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished')"

# FASE del torneo (Apertura/Clausura/…): API-Football la trae en league_round
# como "<Fase> - <jornada>" ("Apertura - 5", "Clausura - 12", "Regular Season -
# 3"). Muchas ligas de la región parten el año en torneos cortos que arrancan de
# cero; otras traen una sola fase. Quitamos la jornada final para quedarnos con
# el nombre de la fase, tal cual lo nombre cada país — sin traducir ni inventar.
_RE_FASE = re.compile(r"^(.*?)\s*[-–]\s*\d+\s*$")


def _fase_de_round(ronda: str | None) -> str | None:
    if not ronda:
        return None
    m = _RE_FASE.match(ronda)
    return (m.group(1) if m else ronda).strip() or None


def _fases_liga(liga_id: int, temporada: int | None) -> list[str]:
    """Fases de una temporada, ordenadas por la fecha de su primer partido.
    [] cuando hay una sola fase (la liga no parte el año): la tabla general
    ya la cubre y no tiene sentido ofrecer un filtro con una única opción."""
    if temporada is None:
        return []
    rows = db.query(
        "sad",
        "SELECT league_round AS r, MIN(date) AS d FROM fixtures "
        "WHERE league_id=? AND league_season=? AND league_round IS NOT NULL "
        "GROUP BY league_round",
        (liga_id, temporada),
    )
    primero: dict[str, str] = {}
    for row in rows:
        fase = _fase_de_round(row["r"])
        if fase is None:
            continue
        d = row["d"]
        if fase not in primero or (d is not None and (primero[fase] is None or d < primero[fase])):
            primero[fase] = d
    if len(primero) <= 1:
        return []
    return sorted(primero, key=lambda f: (primero[f] is None, primero[f] or ""))


def estado_sql(estado: str) -> tuple[str, list]:
    live, fin = sorted(LIVE_SHORT), sorted(FIN_SHORT)
    if estado == "en_vivo":
        return _EN_VIVO_SQL, live
    if estado == "finalizado":
        return f"(NOT {_EN_VIVO_SQL} AND {_FIN_SQL})", live + fin
    return f"(NOT {_EN_VIVO_SQL} AND NOT {_FIN_SQL})", live + fin


@lru_cache(maxsize=None)
def liga_meta(league_id) -> dict:
    """Metadatos de leagues (nombre, país, logo, bandera); tolera DBs sin la tabla."""
    try:
        row = db.query_one(
            "sad", "SELECT name, country, logo, flag, season FROM leagues WHERE id=?", (league_id,)
        )
        if row and row["name"]:
            return {
                "nombre": row["name"],
                "pais": row["country"],
                "logo": row["logo"],
                "bandera": row["flag"],
                "temporada": row["season"],
            }
    except Exception:
        pass  # la tabla leagues puede no existir en DBs antiguas
    return {"nombre": f"Liga {league_id}", "pais": None, "logo": None, "bandera": None, "temporada": None}


def fixture_dto(f) -> dict:
    estado = estado_de(f["status_short"], f["status_long"])
    liga = liga_meta(f["league_id"])
    return {
        "id": f["id"],
        "fecha": iso(f["date"]),
        "ligaId": f["league_id"] or 0,
        "liga": liga["nombre"],
        "temporada": f["league_season"] or 0,
        "estado": estado,
        "minuto": f["elapsed"] if estado == "en_vivo" else None,
        "estadio": f["venue_name"] or "",
        "local": equipo_dto(f["home_team_id"], f["home_name"], f["home_logo"]),
        "visitante": equipo_dto(f["away_team_id"], f["away_name"], f["away_logo"]),
        "golesLocal": f["goals_home"] if estado != "programado" else None,
        "golesVisitante": f["goals_away"] if estado != "programado" else None,
        "ligaLogo": liga["logo"],
        "ligaBandera": liga["bandera"],
        # desambigua torneos homónimos (Copa de la Liga de Perú vs la de Chile)
        "ligaPais": liga["pais"],
    }


FIXTURE_SQL = """
SELECT f.id, f.date, f.status_long, f.status_short, f.elapsed,
       f.league_id, f.league_season, f.venue_name,
       f.goals_home, f.goals_away,
       f.fulltime_home, f.fulltime_away,
       f.home_team_id, ht.name AS home_name, ht.logo AS home_logo,
       f.away_team_id, at.name AS away_name, at.logo AS away_logo
FROM fixtures f
JOIN teams ht ON ht.id = f.home_team_id
JOIN teams at ON at.id = f.away_team_id
"""


def get_fixture(fixture_id: int):
    row = db.query_one("sad", FIXTURE_SQL + " WHERE f.id=?", (fixture_id,))
    if not row:
        raise HTTPException(404, f"fixture {fixture_id} no existe")
    return row


def nivel_a_fecha(team_id: int, fecha_iso: str | None, fallback: float = 0.5) -> float:
    """Último level con date <= fecha (fallback 0.5 — §2.3; 1.0 al ponderar
    como rival, §3.1 / discrepancia 2)."""
    if fecha_iso:
        row = db.query_one(
            "levels",
            "SELECT level FROM team_levels WHERE team_id=? AND date<=? ORDER BY date DESC, id DESC LIMIT 1",
            (team_id, fecha_iso.replace("T", " ").rstrip("Z")),
        )
    else:
        row = db.query_one(
            "levels",
            "SELECT level FROM team_levels WHERE team_id=? ORDER BY date DESC, id DESC LIMIT 1",
            (team_id,),
        )
    return float(row["level"]) if row else fallback


def forma_reciente(team_id: int, antes_de: str | None) -> list[dict] | None:
    """Últimos 5 terminados con rival, fecha y localía (None si no hay 5)."""
    cond, params = "", [team_id, team_id]
    if antes_de:
        cond = " AND f.date < ?"
        params.append(antes_de.replace("T", " ").rstrip("Z"))
    rows = db.query(
        "sad",
        f"""SELECT f.date, f.home_team_id, f.away_team_id,
                   {_G90_H} AS goals_home, {_G90_A} AS goals_away
            FROM fixtures f
            WHERE (f.home_team_id=? OR f.away_team_id=?)
              AND {_FIN90_SQL}
              AND {_G90_H} IS NOT NULL AND {_G90_A} IS NOT NULL{cond}
            ORDER BY f.date DESC LIMIT {RECENT_WINDOW}""",
        tuple(params),
    )
    if len(rows) < RECENT_WINDOW:
        return None
    forma = []
    for r in rows:
        es_local = r["home_team_id"] == team_id
        gf, ga = (r["goals_home"], r["goals_away"]) if es_local else (r["goals_away"], r["goals_home"])
        forma.append({
            "gf": gf,
            "ga": ga,
            "rival_id": r["away_team_id"] if es_local else r["home_team_id"],
            "fecha": str(r["date"]),
            "es_local": es_local,
        })
    return forma


def _senal_de(gap: float) -> str:
    a = abs(gap)
    return "fuerte" if a > 0.5 else "leve" if a >= 0.3 else "equilibrio"


def _tendencia_de(gap):
    return None if gap is None or gap == 0 else ("mejora" if gap > 0 else "empeora")


# Calibración por liga (2026-07, doc §5): países CONMEBOL donde la localía
# real (~+0.5–0.7) casi dobla la de μ v2 (+0.382)
_CONMEBOL = {"Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
             "Paraguay", "Peru", "Uruguay", "Venezuela"}


def fiabilidad_mu(league_id) -> dict:
    """Confianza en μ v2 para la liga del fixture. Reglas DESCRIPTIVAS derivadas
    de la calibración por liga (2026-07, MOTOR_SAD_EXTRACCION.md §5); no tocan μ."""
    meta = liga_meta(league_id)
    nombre = (meta["nombre"] or "").lower()
    pais = meta["pais"] or ""
    if "friendl" in nombre or "amistoso" in nombre:
        return {"nivel": "baja",
                "nota": "Amistosos: nivel y localía pesan mucho menos de lo que μ asume (rotaciones, sedes neutras) — señales de gap poco fiables."}
    if pais == "Argentina":
        return {"nivel": "media",
                "nota": "Liga de paridad: la diferencia de niveles predice ~la mitad de lo que μ asume — desconfiar de favoritismos claros."}
    if pais in _CONMEBOL or "libertadores" in nombre or "sudamericana" in nombre:
        return {"nivel": "media",
                "nota": "Sudamérica: la localía real (~+0.5–0.7) casi dobla la de μ (+0.38) — el local vale más de lo que μ dice."}
    return {"nivel": "alta",
            "nota": "Sin desviaciones detectadas para esta liga en la calibración por liga (2026-07)."}


def gap_equipo(team_id: int, fecha: str | None) -> dict:
    nivel = nivel_a_fecha(team_id, fecha)
    forma = forma_reciente(team_id, fecha)
    esperados = mu(nivel, 2.0, 0.5)  # rival promedio, localía neutra
    recientes = None
    esperados_adj = None
    if forma is not None:
        recientes = sum(3 if p["gf"] > p["ga"] else 1 if p["gf"] == p["ga"] else 0 for p in forma) / RECENT_WINDOW
        # ajuste por calendario: μ con el rival y la localía REALES de cada uno
        # de esos 5 partidos (nivel del rival a la fecha, fallback 1.0 — §3.1)
        esperados_adj = sum(
            mu(nivel, nivel_a_fecha(p["rival_id"], p["fecha"], fallback=1.0), 1.0 if p["es_local"] else 0.0)
            for p in forma
        ) / RECENT_WINDOW
    gap = None if recientes is None else esperados - recientes
    gap_adj = None if recientes is None or esperados_adj is None else esperados_adj - recientes
    return {
        "equipoId": team_id,
        "nivel": round(nivel, 4),
        "ptsRecientes": recientes,
        "ptsEsperados": round(esperados, 4),
        "gap": None if gap is None else round(gap, 4),
        "senal": None if gap is None else _senal_de(gap),
        "tendencia": _tendencia_de(gap),
        "ptsEsperadosAjustados": None if esperados_adj is None else round(esperados_adj, 4),
        "gapAjustado": None if gap_adj is None else round(gap_adj, 4),
        "senalAjustada": None if gap_adj is None else _senal_de(gap_adj),
        "tendenciaAjustada": _tendencia_de(gap_adj),
    }


def proximos_de(team_id: int, nivel: float, fixture) -> list[dict]:
    """Camino de recuperación (§5 v2): próximos fixtures del equipo tras el
    analizado, con la μ esperada contra el rival real de cada uno."""
    marks = ",".join("?" * len(_NO_CAMINO))
    rows = db.query(
        "sad",
        FIXTURE_SQL + f""" WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.id != ? AND f.date > ?
            AND {_SS} NOT IN ({marks})
            ORDER BY f.date ASC LIMIT {RECOVERY_NEXT}""",
        (team_id, team_id, fixture["id"], str(fixture["date"]), *_NO_CAMINO),
    )
    prox, prev = [], _dt(fixture["date"])
    for r in rows:
        es_local = r["home_team_id"] == team_id
        rival_id = r["away_team_id"] if es_local else r["home_team_id"]
        nivel_rival = nivel_a_fecha(rival_id, iso(r["date"]), fallback=1.0)
        d = _dt(r["date"])
        prox.append({
            "fixtureId": r["id"],
            "fecha": iso(r["date"]),
            "rival": equipo_dto(rival_id, r["away_name"] if es_local else r["home_name"],
                                r["away_logo"] if es_local else r["home_logo"]),
            "esLocal": es_local,
            "nivelRival": round(nivel_rival, 4),
            "muEsperado": round(mu(nivel, nivel_rival, 1.0 if es_local else 0.0), 4),
            "esInternacional": (r["league_id"] or 0) in INTL_LEAGUE_IDS,
            "diasDescanso": (d.date() - prev.date()).days,
        })
        prev = d
    return prox


def partido_trampa(team_id: int, fixture, nivel: float, nivel_rival_hoy: float) -> bool:
    """Rival de hoy claramente inferior + un 'grande' (internacional o nivel ≥
    propio) a ≤4 días, antes o después: candidato a rotación/cansancio."""
    if nivel_rival_hoy > nivel - TRAMPA_DELTA_NIVEL:
        return False
    d = _dt(fixture["date"])
    ini = (d - timedelta(days=TRAMPA_VENTANA_DIAS)).strftime("%Y-%m-%d %H:%M:%S")
    fin = (d + timedelta(days=TRAMPA_VENTANA_DIAS)).strftime("%Y-%m-%d %H:%M:%S")
    rows = db.query(
        "sad",
        """SELECT f.date, f.league_id, f.home_team_id, f.away_team_id FROM fixtures f
           WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.id != ? AND f.date BETWEEN ? AND ?""",
        (team_id, team_id, fixture["id"], ini, fin),
    )
    for r in rows:
        rival_id = r["away_team_id"] if r["home_team_id"] == team_id else r["home_team_id"]
        if (r["league_id"] or 0) in INTL_LEAGUE_IDS or nivel_a_fecha(rival_id, iso(r["date"]), fallback=1.0) >= nivel:
            return True
    return False


def contexto_calendario(team_id: int, fixture, g: dict) -> dict:
    """Enriquecimiento §5 v2 del GapEquipo cuando hay fixture en mano: μ del
    propio partido, camino de recuperación y bandera de partido trampa."""
    es_local = fixture["home_team_id"] == team_id
    rival_id = fixture["away_team_id"] if es_local else fixture["home_team_id"]
    nivel = g["nivel"]
    nivel_rival_hoy = nivel_a_fecha(rival_id, iso(fixture["date"]), fallback=1.0)
    prox = proximos_de(team_id, nivel, fixture)
    recup = round(sum(p["muEsperado"] for p in prox) / len(prox), 4) if prox else None
    senal_cal = None
    if recup is not None:
        dif = recup - g["ptsEsperados"]
        senal_cal = "blando" if dif > CAL_UMBRAL else "duro" if dif < -CAL_UMBRAL else "neutro"
    return {
        "muPartido": round(mu(nivel, nivel_rival_hoy, 1.0 if es_local else 0.0), 4),
        "proximos": prox,
        "recuperabilidad": recup,
        "senalCalendario": senal_cal,
        "partidoTrampa": partido_trampa(team_id, fixture, nivel, nivel_rival_hoy),
    }


def constantes_de(team_id: int, limit: int, hasta: str | None = None) -> list[dict]:
    cond, params = "", [team_id]
    if hasta:
        cond = " AND date<=?"
        params.append(hasta.replace("T", " ").rstrip("Z"))
    consts = db.query(
        "constants",
        f"SELECT * FROM constants WHERE team_id=?{cond} ORDER BY date DESC, id DESC LIMIT ?",
        (*params, limit),
    )
    if not consts:
        return []
    fixture_ids = tuple(r["fixture_id"] for r in consts)
    marks = ",".join("?" * len(fixture_ids))
    pm_rows = db.query(
        "discreto",
        f"SELECT * FROM processed_matches WHERE equipo_id=? AND fixture_id IN ({marks})",
        (team_id, *fixture_ids),
    )
    pm = {r["fixture_id"]: r for r in pm_rows}
    out = []
    z = lambda v: float(v) if v is not None else 0.0  # noqa: E731
    # Columnas opcionales: la familia Doble Oportunidad (§3.6) la emite el
    # pipeline; si esta constants.db aún no la tiene, se sirve como 0 (racha
    # vacía) sin romper el contrato — se poblará al re-correr la extracción.
    cols = set(consts[0].keys())
    col = lambda c, n: c[n] if n in cols else None  # noqa: E731
    for c in consts:
        p = pm.get(c["fixture_id"])
        if p:
            es_local = (p["condicion"] or "") == "Local"
            gf, ga = (p["goals_home"], p["goals_away"]) if es_local else (p["goals_away"], p["goals_home"])
            rival_id, rival_nombre = p["rival_id"], p["rival_nombre"]
            nivel_rival = float(p["nivel_rival"] if p["nivel_rival"] is not None else 0)
            liga_id = p["league_id"] or 0
        else:  # fallback si el discretizador va por detrás de constants
            f = db.query_one("sad", FIXTURE_SQL + " WHERE f.id=?", (c["fixture_id"],))
            if not f:
                continue
            es_local = f["home_team_id"] == team_id
            # regla de 90': fulltime_* manda (goals_* incluye la prórroga)
            g90h = f["fulltime_home"] if f["fulltime_home"] is not None else f["goals_home"]
            g90a = f["fulltime_away"] if f["fulltime_away"] is not None else f["goals_away"]
            gf, ga = (g90h, g90a) if es_local else (g90a, g90h)
            rival_id = f["away_team_id"] if es_local else f["home_team_id"]
            rival_nombre = f["away_name"] if es_local else f["home_name"]
            nivel_rival = 0.0
            liga_id = f["league_id"] or 0
        # Márgenes (§3.7): 18 columnas opcionales, leídas con degradación elegante.
        # kVicN/kDerN pasan tal cual (no llevan fusión ±) → mismo valor en k y fusion.
        mraw = {
            f"{s}{b}{suf}": z(col(c, f"k_{s}{b}{cs}"))
            for s in ("vic", "der")
            for b in (1, 2, 3)
            for suf, cs in (("", ""), ("Local", "_local"), ("Visita", "_visita"))
        }
        mfus = {"k" + kk[0].upper() + kk[1:]: v for kk, v in mraw.items()}
        out.append(
            {
                "equipoId": team_id,
                "fixtureId": c["fixture_id"],
                "fecha": iso(c["date"]),
                "condicion": "Local" if es_local else "Visita",
                "rivalId": rival_id,
                "rivalNombre": rival_nombre,
                "nivelRival": nivel_rival,
                "ligaId": liga_id,
                "esInternacional": liga_id in INTL_LEAGUE_IDS,
                "golesFavor": gf or 0,
                "golesContra": ga or 0,
                "q": {
                    "local": c["q_local"],
                    "visita": c["q_visita"],
                    "negativo": z(c["q_negativo"]),
                    "golesAnotado": z(c["q_goles_anotado"]),
                    "golesRecibido": z(c["q_goles_recibido"]),
                    "dc": z(col(c, "q_dc")),
                },
                "k": {
                    "positivo": z(c["k_positivo"]),
                    "negativo": z(c["k_negativo"]),
                    "positivoLocal": z(c["k_positivo_local"]),
                    "negativoLocal": z(c["k_negativo_local"]),
                    "positivoVisita": z(c["k_positivo_visita"]),
                    "negativoVisita": z(c["k_negativo_visita"]),
                    "golesAnotado": z(c["k_goles_anotado"]),
                    "golesRecibido": z(c["k_goles_recibido"]),
                    "golesLocalAnotado": z(c["k_goles_local_anotado"]),
                    "golesLocalRecibido": z(c["k_goles_local_recibido"]),
                    "golesVisitaAnotado": z(c["k_goles_visita_anotado"]),
                    "golesVisitaRecibido": z(c["k_goles_visita_recibido"]),
                    # Doble Oportunidad (§3.6): acumuladores no-negativos
                    "dc": z(col(c, "k_dc")),
                    "dcLocal": z(col(c, "k_dc_local")),
                    "dcVisita": z(col(c, "k_dc_visita")),
                    **mraw,  # Márgenes (§3.7)
                },
                # fusión §4.2: k = k⁺ + k⁻ (NULL→0); los k_goles y k_dc pasan tal cual
                "fusion": {
                    "k": z(c["k_positivo"]) + z(c["k_negativo"]),
                    "kLocal": z(c["k_positivo_local"]) + z(c["k_negativo_local"]),
                    "kVisita": z(c["k_positivo_visita"]) + z(c["k_negativo_visita"]),
                    "golesAnotado": z(c["k_goles_anotado"]),
                    "golesRecibido": z(c["k_goles_recibido"]),
                    "golesLocalAnotado": z(c["k_goles_local_anotado"]),
                    "golesLocalRecibido": z(c["k_goles_local_recibido"]),
                    "golesVisitaAnotado": z(c["k_goles_visita_anotado"]),
                    "golesVisitaRecibido": z(c["k_goles_visita_recibido"]),
                    "kDc": z(col(c, "k_dc")),
                    "kDcLocal": z(col(c, "k_dc_local")),
                    "kDcVisita": z(col(c, "k_dc_visita")),
                    **mfus,  # Márgenes (§3.7)
                },
            }
        )
    return out


def constantes_cuota_de(team_id: int) -> list[dict]:
    """Filas de constants_cuota (k_cuota, §3.8) del equipo, en orden cronológico.
    Si la tabla aún no existe (no se corrió backfill_cuota) devuelve []."""
    try:
        # tope de seguridad: si hubiera más de 1000 filas se conservan las más recientes
        rows = db.query(
            "constants",
            "SELECT * FROM (SELECT * FROM constants_cuota WHERE team_id=? ORDER BY date DESC, id DESC LIMIT 1000) ORDER BY date, id",
            (team_id,),
        )
    except sqlite3.OperationalError:
        return []
    out = []
    for r in rows:
        out.append(
            {
                "equipoId": team_id,
                "fixtureId": r["fixture_id"],
                "fecha": iso(r["date"]),
                "resultado": r["resultado"],
                "esLocal": bool(r["es_local"]),
                "cuota": {"victoria": r["cuota_victoria"], "empate": r["cuota_empate"], "derrota": r["cuota_derrota"]},
                "k": {
                    "victoria": r["k_cuota_victoria"], "victoriaLocal": r["k_cuota_victoria_local"], "victoriaVisita": r["k_cuota_victoria_visita"],
                    "empate": r["k_cuota_empate"], "empateLocal": r["k_cuota_empate_local"], "empateVisita": r["k_cuota_empate_visita"],
                    "derrota": r["k_cuota_derrota"], "derrotaLocal": r["k_cuota_derrota_local"], "derrotaVisita": r["k_cuota_derrota_visita"],
                },
            }
        )
    return out


def niveles_de(team_id: int, limit: int, hasta: str | None = None) -> list[dict]:
    cond, params = "", [team_id]
    if hasta:
        cond = " AND date<=?"
        params.append(hasta.replace("T", " ").rstrip("Z"))
    rows = db.query(
        "levels",
        f"SELECT fixture_id, date, level FROM team_levels WHERE team_id=?{cond} ORDER BY date DESC, id DESC LIMIT ?",
        (*params, limit),
    )
    out = []
    for r in rows:
        b, label = level_bin(float(r["level"]))
        out.append(
            {
                "equipoId": team_id,
                "fixtureId": r["fixture_id"],
                "fecha": iso(r["date"]),
                "nivel": round(float(r["level"]), 4),
                "bin": b,
                "binEtiqueta": label,
            }
        )
    return out


# Mapeo bet_name/value de API-Football → mercados del contrato.
# El catálogo trae los MISMOS mercados en versión 1er/2º tiempo, córners,
# tarjetas o prórroga ("Goals Over/Under First Half", "Asian Handicap First
# Half"…): si se cuelan bajo la misma clave, la serie alterna partido
# completo / medio tiempo en cada captura y la gráfica zigzaguea. Aquí solo
# pasan mercados del partido completo.
_BETS_FUERA = ("half", "1st", "2nd", "first", "second", "corner", "card", "extra", "period", "halftime")


def cuota_key(bet_name: str, value: str):
    b = (bet_name or "").lower()
    v = (value or "").strip()
    if any(t in b for t in _BETS_FUERA):
        return None
    # "fulltime result": nombre del 1X2 en el catálogo de /odds/live
    if "match winner" in b or "fulltime result" in b or b == "1x2":
        return {"Home": ("1x2", "1"), "Draw": ("1x2", "X"), "Away": ("1x2", "2"),
                "1": ("1x2", "1"), "X": ("1x2", "X"), "2": ("1x2", "2")}.get(v)
    if "double chance" in b:
        return {"Home/Draw": ("dc", "1X"), "Home/Away": ("dc", "12"), "Draw/Away": ("dc", "X2"),
                "1X": ("dc", "1X"), "12": ("dc", "12"), "X2": ("dc", "X2")}.get(v)
    if "over/under" in b or b == "goals over/under":
        return {"Over 2.5": ("ou", "O"), "Under 2.5": ("ou", "U")}.get(v)
    if "both teams" in b:
        return {"Yes": ("btts", "Y"), "No": ("btts", "N")}.get(v)
    if "asian handicap" in b:
        if v.startswith("Home -0.5"):
            return ("ah", "H1")
        if v.startswith("Away +0.5"):
            return ("ah", "H2")
    return None


# ---------------------------------------------------------------------------
# endpoints
# ---------------------------------------------------------------------------


@app.get(API + "/health")
def health():
    db_ok = True
    last_run = None
    try:
        for name in db.DB_FILES:
            db.query_one(name, "SELECT 1")
        row = db.query_one("discreto", "SELECT MAX(processed_at) AS m FROM processed_matches")
        last_run = iso(row["m"]) if row and row["m"] else None
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "version": app.version, "dbOk": db_ok, "lastPipelineRun": last_run}


def _norm(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(ch) != "Mn")


@lru_cache(maxsize=2)
def _equipos_norm(bucket: int) -> tuple[tuple[int, str, str | None, str], ...]:
    # caché por minuto: evita escanear y normalizar toda la tabla en cada búsqueda
    return tuple((r["id"], r["name"], r["logo"], _norm(r["name"])) for r in db.query("sad", "SELECT id, name, logo FROM teams"))


@app.get(API + "/equipos")
def buscar_equipos(buscar: str = Query(min_length=2, max_length=60), limit: int = Query(default=10, ge=1, le=25)):
    """Búsqueda inteligente: sin tildes ni mayúsculas; ranking
    prefijo > inicio de palabra > contiene."""
    q = _norm(buscar)
    scored = []
    for tid, nombre, logo, n in _equipos_norm(int(time.monotonic() // 60)):
        if q in n:
            rank = 0 if n.startswith(q) else 1 if any(w.startswith(q) for w in n.split()) else 2
            scored.append((rank, len(n), tid, nombre, logo))
    scored.sort()
    return [equipo_dto(tid, nombre, logo) for _, __, tid, nombre, logo in scored[:limit]]


@app.get(API + "/fixtures")
def fixtures(
    fecha: date_t | None = None,
    desde: date_t | None = None,
    estado: Literal["programado", "en_vivo", "finalizado"] | None = None,
    orden: Literal["asc", "desc"] = "desc",
    ligaId: int | None = None,
    temporada: int | None = None,
    equipoId: int | None = None,
    rivalId: int | None = None,
    # tope 500: un día con amistosos de clubes globales supera los 200 partidos
    limit: int = Query(default=50, ge=1, le=500),
):
    if rivalId is not None and equipoId is None:
        raise HTTPException(status_code=422, detail="rivalId requiere equipoId")
    cond, params = [], []
    if fecha:
        # rango en vez de date(f.date)=? para poder usar el índice sobre f.date
        cond.append("f.date >= ? AND f.date < ?")
        params.extend([fecha.isoformat(), (fecha + timedelta(days=1)).isoformat()])
    if desde:
        cond.append("f.date >= ?")
        params.append(desde.isoformat())
    if estado:
        sql, extra = estado_sql(estado)
        cond.append(sql)
        params.extend(extra)
    if ligaId is not None:
        cond.append("f.league_id=?")
        params.append(ligaId)
    if temporada is not None:
        cond.append("f.league_season=?")
        params.append(temporada)
    if equipoId is not None and rivalId is not None:
        cond.append("((f.home_team_id=? AND f.away_team_id=?) OR (f.home_team_id=? AND f.away_team_id=?))")
        params.extend([equipoId, rivalId, rivalId, equipoId])
    elif equipoId is not None:
        cond.append("(f.home_team_id=? OR f.away_team_id=?)")
        params.extend([equipoId, equipoId])
    where = (" WHERE " + " AND ".join(cond)) if cond else ""
    orden_sql = "ASC" if orden == "asc" else "DESC"
    rows = db.query("sad", FIXTURE_SQL + where + f" ORDER BY f.date {orden_sql} LIMIT ?", (*params, limit))
    return [fixture_dto(r) for r in rows]


@app.get(API + "/fixtures/{fixture_id}")
def fixture(fixture_id: int):
    return fixture_dto(get_fixture(fixture_id))


@app.get(API + "/niveles/{equipo_id}")
def niveles(equipo_id: int, limit: int = Query(default=50, ge=1, le=500)):
    return niveles_de(equipo_id, limit)


@app.get(API + "/constantes/{equipo_id}")
def constantes(equipo_id: int, limit: int = Query(default=50, ge=1, le=500)):
    return constantes_de(equipo_id, limit)


@app.get(API + "/constantes-cuota/{equipo_id}")
def constantes_cuota(equipo_id: int):
    """k_cuota (§3.8): rachas de suma de cuota 1X2, solo 2026. La tabla
    constants_cuota se reconstruye en cada corrida del pipeline (y también con
    backend/backfill_cuota, que además puede inyectar cuotas sintéticas)."""
    return constantes_cuota_de(equipo_id)


@app.get(API + "/predicciones/{fixture_id}")
def prediccion(fixture_id: int):
    f = get_fixture(fixture_id)
    fecha = iso(f["date"])
    local = gap_equipo(f["home_team_id"], fecha)
    local.update(contexto_calendario(f["home_team_id"], f, local))
    visitante = gap_equipo(f["away_team_id"], fecha)
    visitante.update(contexto_calendario(f["away_team_id"], f, visitante))
    gap_diff = None
    if local["gap"] is not None and visitante["gap"] is not None:
        gap_diff = round(local["gap"] - visitante["gap"], 4)
    gap_diff_adj = None
    if local["gapAjustado"] is not None and visitante["gapAjustado"] is not None:
        gap_diff_adj = round(local["gapAjustado"] - visitante["gapAjustado"], 4)
    return {
        "fixtureId": fixture_id,
        "local": local,
        "visitante": visitante,
        "gapDiff": gap_diff,
        "gapDiffAjustado": gap_diff_adj,
        "fiabilidadMu": fiabilidad_mu(f["league_id"]),
        "generadoEn": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.get(API + "/analisis-prepartido/{fixture_id}")
def analisis_prepartido(fixture_id: int):
    f = get_fixture(fixture_id)
    home_id, away_id = f["home_team_id"], f["away_team_id"]
    # foto a la fecha del fixture: para partidos pasados el análisis usa el
    # estado del motor de ese momento, no el actual (igual que /predicciones)
    fecha = iso(f["date"])
    niveles_h = niveles_de(home_id, 1, hasta=fecha)
    niveles_a = niveles_de(away_id, 1, hasta=fecha)
    const_h = constantes_de(home_id, 1, hasta=fecha)
    const_a = constantes_de(away_id, 1, hasta=fecha)
    pred = prediccion(fixture_id)

    def nv(rows, team_id):
        if rows:
            return rows[0]
        b, label = level_bin(0.5)
        return {"equipoId": team_id, "fixtureId": 0, "fecha": "", "nivel": 0.5, "bin": b, "binEtiqueta": label}

    nh, na = nv(niveles_h, home_id), nv(niveles_a, away_id)
    dir_ = lambda g: (  # noqa: E731
        "tiende a mejorar" if g["tendencia"] == "mejora" else "tiende a empeorar" if g["tendencia"] == "empeora" else "en equilibrio"
    )
    resumen = (
        f"{f['home_name']} (nivel {nh['nivel']:.2f}, {nh['binEtiqueta']}) recibe a "
        f"{f['away_name']} (nivel {na['nivel']:.2f}, {na['binEtiqueta']}). "
        f"Regresión al nivel: local {dir_(pred['local'])}, visitante {dir_(pred['visitante'])}."
    )
    return {
        "fixtureId": fixture_id,
        "niveles": {"local": nh, "visitante": na},
        "constantes": {"local": const_h[0] if const_h else None, "visitante": const_a[0] if const_a else None},
        "prediccion": pred,
        "resumen": resumen,
    }


@app.get(API + "/equipos/{equipo_id}/stats")
def equipo_stats(equipo_id: int):
    """Stats de temporada calculadas de los fixtures terminados (siempre al día).
    xG/posesión/tiros/córners quedan null en v0 (no se derivan de fixtures)."""
    team = db.query_one("sad", "SELECT id, name FROM teams WHERE id=?", (equipo_id,))
    if not team:
        raise HTTPException(404, f"equipo {equipo_id} no existe")
    rows = db.query(
        "sad",
        f"""SELECT f.home_team_id, {_G90_H} AS goals_home, {_G90_A} AS goals_away
           FROM fixtures f
           WHERE (f.home_team_id=? OR f.away_team_id=?)
             AND {_FIN90_SQL}
             AND {_G90_H} IS NOT NULL AND {_G90_A} IS NOT NULL
           ORDER BY f.date DESC LIMIT 2000""",
        (equipo_id, equipo_id),
    )
    pts = gf_tot = gc_tot = 0
    forma = []
    for i, r in enumerate(rows):
        gf, ga = (r["goals_home"], r["goals_away"]) if r["home_team_id"] == equipo_id else (r["goals_away"], r["goals_home"])
        res = "W" if gf > ga else "D" if gf == ga else "L"
        pts += 3 if res == "W" else 1 if res == "D" else 0
        gf_tot += gf
        gc_tot += ga
        if i < RECENT_WINDOW:
            forma.append(res)  # más reciente primero
    pj = len(rows)
    return {
        "equipoId": equipo_id,
        "nombre": team["name"],
        "partidosJugados": pj,
        "puntos": pts,
        "forma": forma,
        "golesFavorProm": round(gf_tot / pj, 2) if pj else 0,
        "golesContraProm": round(gc_tot / pj, 2) if pj else 0,
        "xgProm": None,
        "posesionProm": None,
        "tirosPuertaProm": None,
        "cornersProm": None,
    }


# Ingesta de plantilla BAJO DEMANDA: al entrar a un equipo sin datos de
# jugadores se lanza en segundo plano backend.ingesta.jugadores --equipo
# (mismo patrón de subprocesos que la ingesta programada: el HTTP sigue siendo
# de solo lectura, quien escribe es la capa de ingesta). Dedupe en memoria por
# equipo; SAD_PLANTILLA_ONDEMAND=0 la apaga. La UI sondea hasta que llega.
_plantillas_en_curso: set[int] = set()
_plantillas_lock = threading.Lock()


def _ondemand_activo() -> bool:
    return os.environ.get("SAD_PLANTILLA_ONDEMAND", "1").strip().lower() not in ("0", "false", "no")


def _lanzar_ingesta_plantilla(equipo_id: int) -> bool:
    """True si la ingesta del equipo quedó lanzada (o ya estaba en curso)."""
    if not _ondemand_activo():
        return False
    try:  # sin API_FOOTBALL_KEY (p. ej. demo local) no hay nada que lanzar
        from backend.ingesta.extractor import leer_clave
        leer_clave()
    except BaseException:
        return False
    with _plantillas_lock:
        if equipo_id in _plantillas_en_curso:
            return True
        _plantillas_en_curso.add(equipo_id)
    # temporada: la del último fixture conocido del equipo (torneos de año
    # cruzado incluidos); fallback al año en curso
    row = db.query_one(
        "sad",
        "SELECT league_season FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
        "AND league_season IS NOT NULL ORDER BY date DESC LIMIT 1",
        (equipo_id, equipo_id),
    )
    temporada = row["league_season"] if row else datetime.now(timezone.utc).year
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = {**os.environ, "PYTHONPATH": raiz, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}

    def _trabajo() -> None:
        try:
            print(f"[jugadores] ingesta on-demand equipo {equipo_id} t{temporada}", flush=True)
            subprocess.run(
                [sys.executable, "-u", "-m", "backend.ingesta.jugadores",
                 "--equipo", str(equipo_id), "--temporada", str(temporada)],
                cwd=db.BASE_DIR, env=env,
            )
        finally:
            with _plantillas_lock:
                _plantillas_en_curso.discard(equipo_id)

    threading.Thread(target=_trabajo, daemon=True, name=f"plantilla-{equipo_id}").start()
    return True


@app.get(API + "/equipos/{equipo_id}/plantilla")
def equipo_plantilla(equipo_id: int):
    """Plantilla con indicadores (docs/JUGADORES.md): por-90 con encogimiento,
    dependencia HHI, bajas, traspasos, DT. Calculado en lectura de las tablas
    de jugadores de sad.db (backend.ingesta.jugadores); sin ingesta aún,
    jugadores=[] + ingesta on-demand lanzada en segundo plano (ingestaLanzada
    avisa a la UI para sondear) — nada se inventa."""
    team = db.query_one("sad", "SELECT id, name FROM teams WHERE id=?", (equipo_id,))
    if not team:
        raise HTTPException(404, f"equipo {equipo_id} no existe")
    from backend import jugadores as jug
    p = jug.plantilla_de(equipo_id)
    p["nombre"] = team["name"]
    p["ingestaLanzada"] = False if p["jugadores"] else _lanzar_ingesta_plantilla(equipo_id)
    return p


@app.get(API + "/fixtures/{fixture_id}/ficha")
def fixture_ficha(fixture_id: int):
    """Ficha de partido (docs/JUGADORES.md): plantillas con indicadores +
    congestión de calendario de AMBOS equipos. Es el puente con los skills
    (EFE/DTP/timeline): JSON determinista calculado por código."""
    from backend import jugadores as jug
    ficha = jug.ficha_partido(fixture_id)
    if not ficha:
        raise HTTPException(404, f"fixture {fixture_id} no existe")
    return ficha


@app.get(API + "/ligas/{liga_id}")
def liga(liga_id: int, temporada: int | None = None):
    """Metadatos de la liga (nombre, país, logo, bandera, temporadas capturadas
    y fases del torneo —Apertura/Clausura/…— de la temporada pedida)."""
    meta = liga_meta(liga_id)
    if meta["pais"] is None and meta["logo"] is None and meta["nombre"] == f"Liga {liga_id}":
        raise HTTPException(404, f"liga {liga_id} no existe")
    rows = db.query(
        "sad",
        "SELECT DISTINCT league_season AS s FROM fixtures WHERE league_id=? AND league_season IS NOT NULL ORDER BY s DESC",
        (liga_id,),
    )
    temporadas = [r["s"] for r in rows]
    temp = temporada if temporada is not None else (temporadas[0] if temporadas else None)
    return {"id": liga_id, **meta, "temporadas": temporadas, "fases": _fases_liga(liga_id, temp)}


@app.get(API + "/ligas/{liga_id}/standings")
def standings(liga_id: int, temporada: int | None = None, fase: str | None = None):
    """Tabla de posiciones calculada de los fixtures terminados de la liga.
    Con `fase` (Apertura/Clausura/… según la región) solo cuentan los partidos
    de esa fase —cada torneo corto arranca de cero—; sin ella, la tabla del año."""
    if temporada is None:
        row = db.query_one("sad", "SELECT MAX(league_season) AS s FROM fixtures WHERE league_id=?", (liga_id,))
        temporada = row["s"] if row and row["s"] is not None else 0
    rows = db.query(
        "sad",
        f"""SELECT f.home_team_id, f.away_team_id, {_G90_H} AS goals_home, {_G90_A} AS goals_away,
                  f.league_round AS ronda, ht.name AS home_name, at.name AS away_name
           FROM fixtures f
           JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id
           WHERE f.league_id=? AND f.league_season=? AND {_FIN90_SQL}
             AND {_G90_H} IS NOT NULL AND {_G90_A} IS NOT NULL
           LIMIT 5000""",
        (liga_id, temporada),
    )
    acc: dict[int, dict] = {}

    def upsert(tid, nombre, gf, ga):
        e = acc.setdefault(tid, {"equipoId": tid, "nombre": nombre, "puntos": 0, "partidosJugados": 0, "golesFavor": 0, "golesContra": 0})
        e["partidosJugados"] += 1
        e["golesFavor"] += gf
        e["golesContra"] += ga
        e["puntos"] += 3 if gf > ga else 1 if gf == ga else 0

    for r in rows:
        if fase is not None and _fase_de_round(r["ronda"]) != fase:
            continue
        upsert(r["home_team_id"], r["home_name"], r["goals_home"], r["goals_away"])
        upsert(r["away_team_id"], r["away_name"], r["goals_away"], r["goals_home"])
    # LIGA COMPLETA: los equipos de la temporada (o de la fase) que aún no tienen
    # partidos terminados (jornada 1 a medias, pospuestos) entran con ceros — sin
    # esto la tabla salía coja y los prompts de despensa/timeline (que se arman
    # con ella) barrían solo una parte de la liga
    todos = db.query(
        "sad",
        """SELECT DISTINCT t.id AS tid, t.name AS nombre, f.league_round AS ronda FROM fixtures f
           JOIN teams t ON t.id IN (f.home_team_id, f.away_team_id)
           WHERE f.league_id=? AND f.league_season=?""",
        (liga_id, temporada),
    )
    for r in todos:
        if fase is not None and _fase_de_round(r["ronda"]) != fase:
            continue
        if r["tid"] not in acc:
            acc[r["tid"]] = {"equipoId": r["tid"], "nombre": r["nombre"], "puntos": 0,
                             "partidosJugados": 0, "golesFavor": 0, "golesContra": 0}
    tabla = sorted(acc.values(), key=lambda e: (-e["puntos"], -(e["golesFavor"] - e["golesContra"]), -e["golesFavor"], e["nombre"]))
    return [{"posicion": i + 1, **e} for i, e in enumerate(tabla)]


@app.get(API + "/cuotas/{fixture_id}")
def cuotas(fixture_id: int):
    rows = db.query(
        "sad",
        "SELECT bet_name, value, odd FROM odds WHERE fixture_id=? AND odd IS NOT NULL",
        (fixture_id,),
    )
    acc: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        key = cuota_key(r["bet_name"], r["value"])
        if key:
            acc.setdefault(key, []).append(float(r["odd"]))
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return [
        {
            "fixtureId": fixture_id,
            "mercado": mercado,
            "seleccion": seleccion,
            "cuota": round(sum(v) / len(v), 2),  # media entre bookmakers
            "actualizadoEn": now,
        }
        for (mercado, seleccion), v in sorted(acc.items())
    ]


# Mapeo de eventos crudos de API-Football → tipos del contrato
def _tipo_evento(tipo: str, detalle: str):
    t = (tipo or "").lower()
    d = (detalle or "").lower()
    if t == "goal":
        return None if "missed" in d else "gol"
    if t == "card":
        if "second yellow" in d or "red" in d:
            return "roja"
        if "yellow" in d:
            return "amarilla"
    return None  # sustituciones, VAR, etc. no se sirven (por ahora)


@app.get(API + "/fixtures/{fixture_id}/live")
def fixture_live(fixture_id: int):
    """Estado en vivo real: marcador/minuto de fixtures (refrescados por la
    ingesta en vivo) + última captura y serie de odds_live. Sin cobertura o
    con la ingesta apagada, cuotas/serie van vacías — nada se inventa."""
    f = db.query_one(
        "sad",
        "SELECT status_short, status_long, elapsed, goals_home, goals_away FROM fixtures WHERE id=?",
        (fixture_id,),
    )
    if not f:
        raise HTTPException(404, f"fixture {fixture_id} no existe")
    try:
        filas = db.query(
            "sad",
            "SELECT minuto, bet_name, value, odd, suspendida, captured_at FROM odds_live "
            "WHERE fixture_id=? ORDER BY captured_at",
            (fixture_id,),
        )
    except Exception:
        filas = []
    ultima = filas[-1]["captured_at"] if filas else None
    # MINUTO EFECTIVO por captura (monótono): en el descuento del 1er tiempo y
    # el descanso la API repite elapsed=45 (o manda null), y al arrancar el 2º
    # tiempo la curva se apilaba en vertical y dibujaba lazos hacia atrás. Los
    # null heredan el último minuto conocido, los retrocesos del feed se
    # recortan, y las capturas de un mismo minuto se reparten en fracciones
    # (45.0, 45.33, 45.67 → 46) — no se pierde ningún punto y la X siempre avanza.
    orden_capturas: list = []
    minuto_de: dict = {}
    for r in filas:
        if r["captured_at"] not in minuto_de:
            orden_capturas.append(r["captured_at"])
            minuto_de[r["captured_at"]] = r["minuto"]
    minutos, previo = [], 0
    for cap in orden_capturas:
        m = minuto_de[cap]
        m = previo if m is None else max(int(m), previo)
        minutos.append(m)
        previo = m
    minuto_efectivo: dict = {}
    i = 0
    while i < len(minutos):
        j = i
        while j < len(minutos) and minutos[j] == minutos[i]:
            j += 1
        for k in range(i, j):
            minuto_efectivo[orden_capturas[k]] = round(minutos[i] + (k - i) / (j - i), 2)
        i = j
    cuotas = []
    serie = []
    for r in filas:
        key = cuota_key(r["bet_name"], r["value"])
        if not key:
            continue
        punto = {"mercado": key[0], "seleccion": key[1], "cuota": round(float(r["odd"]), 2)}
        if not r["suspendida"]:
            serie.append({"minuto": minuto_efectivo.get(r["captured_at"], r["minuto"]), **punto})
        if r["captured_at"] == ultima:
            cuotas.append({**punto, "suspendida": bool(r["suspendida"])})
    try:
        filas_ev = db.query(
            "sad",
            "SELECT minuto, tipo, detalle, equipo_id, jugador FROM fixture_eventos "
            "WHERE fixture_id=? ORDER BY minuto, id",
            (fixture_id,),
        )
    except Exception:
        filas_ev = []
    eventos = []
    for e in filas_ev:
        tipo = _tipo_evento(e["tipo"], e["detalle"])
        if tipo:
            eventos.append(
                {"minuto": e["minuto"], "tipo": tipo, "equipoId": e["equipo_id"],
                 "jugador": e["jugador"], "detalle": e["detalle"]}
            )
    return {
        "fixtureId": fixture_id,
        "estado": estado_de(f["status_short"], f["status_long"]),
        "minuto": f["elapsed"],
        "golesLocal": f["goals_home"],
        "golesVisitante": f["goals_away"],
        "cuotas": cuotas,
        "serie": serie,
        "eventos": eventos,
        "actualizadoEn": iso(ultima) if ultima else None,
    }


@app.get(API + "/cuotas/{fixture_id}/casas")
def cuotas_casas(fixture_id: int):
    """Cuota de cada casa por selección (última foto). La más alta de cada
    selección va marcada con mejor=true: ahí paga más ese acierto."""
    rows = db.query(
        "sad",
        "SELECT id, bookmaker_id, bookmaker_name, bet_name, value, odd FROM odds "
        "WHERE fixture_id=? AND odd IS NOT NULL AND bookmaker_id IS NOT NULL",
        (fixture_id,),
    )
    # DEDUPE por casa: el upsert viejo acumulaba filas de la misma casa (ids
    # nulos / variantes del valor) y la casa salía 2-3 veces con cuotas
    # distintas — se conserva SOLO la fila más reciente por (selección, casa)
    ultima: dict[tuple, dict] = {}
    for r in rows:
        key = cuota_key(r["bet_name"], r["value"])
        if not key:
            continue
        casa = (r["bookmaker_name"] or f"casa {r['bookmaker_id']}").strip()
        ck = (key, casa.lower())
        if ck not in ultima or r["id"] > ultima[ck]["_id"]:
            ultima[ck] = {
                "_id": r["id"],
                "fixtureId": fixture_id,
                "mercado": key[0],
                "seleccion": key[1],
                "casaId": r["bookmaker_id"],
                "casa": casa,
                "cuota": round(float(r["odd"]), 2),
            }
    por_sel: dict[tuple[str, str], list[dict]] = {}
    for (key, _casa), fila in ultima.items():
        por_sel.setdefault(key, []).append({k: v for k, v in fila.items() if k != "_id"})
    out = []
    for key in sorted(por_sel):
        filas = sorted(por_sel[key], key=lambda f: -f["cuota"])
        tope = filas[0]["cuota"]
        out.extend({**f, "mejor": f["cuota"] >= tope - 1e-9} for f in filas)
    return out


@app.get(API + "/cuotas/{fixture_id}/historial/fuentes")
def cuotas_historial_fuentes(fixture_id: int):
    """Casas de referencia con historial propio para este fixture (además de
    la media). [] en DBs anteriores a la migración."""
    try:
        rows = db.query(
            "sad",
            "SELECT DISTINCT casa FROM odds_history WHERE fixture_id=? AND casa IS NOT NULL ORDER BY casa",
            (fixture_id,),
        )
        return [r["casa"] for r in rows]
    except Exception:
        return []


@app.get(API + "/cuotas/{fixture_id}/historial")
def cuotas_historial(fixture_id: int, casa: str | None = None):
    """Snapshots prepartido de odds_history (asc por captura). Sin `casa`:
    la media entre casas; con `casa`: el movimiento crudo de esa casa de
    referencia. [] si la DB aún no tiene la tabla."""
    try:
        if casa:
            rows = db.query(
                "sad",
                "SELECT bet_name, value, odd, casas, captured_at FROM odds_history "
                "WHERE fixture_id=? AND lower(casa)=lower(?) AND odd IS NOT NULL "
                "ORDER BY captured_at, bet_name, value",
                (fixture_id, casa),
            )
        else:
            rows = db.query(
                "sad",
                "SELECT bet_name, value, odd, casas, captured_at FROM odds_history "
                "WHERE fixture_id=? AND casa_id IS NULL AND odd IS NOT NULL "
                "ORDER BY captured_at, bet_name, value",
                (fixture_id,),
            )
    except Exception:
        # DB anterior a la migración (sin columna casa): todo es media
        try:
            rows = db.query(
                "sad",
                "SELECT bet_name, value, odd, casas, captured_at FROM odds_history "
                "WHERE fixture_id=? AND odd IS NOT NULL ORDER BY captured_at, bet_name, value",
                (fixture_id,),
            ) if not casa else []
        except Exception:
            return []
    # COLAPSO ANTI-DUPLICADOS: si una captura escribió más de una fila para la
    # misma selección (variantes del valor, casas repetidas del upsert viejo),
    # se funden en UNA media ponderada por nº de casas — sin esto la curva
    # zigzaguea alternando entre las filas gemelas.
    acumulado: dict[tuple, list] = {}  # (mercado, sel, captured_at) → [Σ odd·peso, Σ peso]
    orden: list[tuple] = []
    for r in rows:
        key = cuota_key(r["bet_name"], r["value"])
        if not key:
            continue
        k = (key[0], key[1], r["captured_at"])
        peso = max(int(r["casas"] or 1), 1)
        if k not in acumulado:
            acumulado[k] = [0.0, 0]
            orden.append(k)
        acumulado[k][0] += float(r["odd"]) * peso
        acumulado[k][1] += peso
    out = [
        {
            "fixtureId": fixture_id,
            "mercado": mk,
            "seleccion": sel,
            "cuota": round(suma / peso, 2),
            "casas": peso,
            "capturadoEn": iso(cap),
        }
        for (mk, sel, cap) in orden
        for (suma, peso) in (acumulado[(mk, sel, cap)],)
    ]
    return out


# ---------------------------------------------------------------------------
# análisis EFE+DTP (docs/efe-dtp/PLAN_ADAPTADO.md)
# ---------------------------------------------------------------------------
# Excepción documentada a la regla de solo lectura: estos endpoints escriben
# efe.db (propiedad exclusiva de backend/analisis/), nunca las DBs del SAD.
# El POST cuesta créditos de la API de Claude: queda protegido por el auth
# bearer global (SAD_API_TOKEN) igual que el resto de la API.


class EfeRequest(BaseModel):
    fixtureId: int
    forzar: bool = False  # regenerar: descarta el análisis guardado y relanza
    # candado de análisis frío: true = acepto pagar el análisis sin despensa
    # (~$0.6-1.2); por defecto se bloquea y se guía al flujo gratis
    permitirFrio: bool = False


class EquipoDespensa(BaseModel):
    equipo: str
    # str para los tipos del EFE; timeline_eventos acepta la LISTA de eventos
    # (o un string con el JSON de la lista, que se parsea)
    datos: dict[str, str | list]


class CargaDespensaRequest(BaseModel):
    equipos: list[EquipoDespensa]
    fuentes: list[str] = []


@app.post(API + "/analisis/despensa")
def cargar_despensa(body: CargaDespensaRequest):
    """Carga MANUAL de la despensa (docs/DESPENSA_DESKTOP.md): la investigación
    hecha gratis en el Claude de escritorio (suscripción plana) se deposita
    aquí y el EFE por API ya no busca en la web — solo razona sobre datos
    cacheados (~$0.10-0.20 en vez del análisis frío completo).

    Misma excepción documentada de solo-lectura que /analisis/efe: escribe
    efe.db (tabla investigacion), nunca las DBs del SAD. El nombre del equipo
    debe coincidir con el de la app (teams.name); los tipos fuera del catálogo
    de la despensa se ignoran."""
    from backend.analisis import db as efedb
    if not body.equipos:
        raise HTTPException(422, "equipos vacío: nada que depositar")

    # CANONIZACIÓN: el barrido de liga puede traer variantes del nombre
    # ("Universitario de Deportes" vs "Universitario"). La despensa se guarda
    # bajo teams.name (es la clave con la que el EFE la busca): match exacto
    # normalizado, o parcial ÚNICO; ambiguo o desconocido queda tal cual.
    equipos_db = [(r["name"], _norm(r["name"])) for r in db.query("sad", "SELECT name FROM teams")]

    def _canonico(nombre: str) -> str:
        q = _norm(nombre)
        exacto = [n for n, nn in equipos_db if nn == q]
        if len(exacto) == 1:
            return exacto[0]
        parcial = [n for n, nn in equipos_db if q in nn or nn in q]
        if len(parcial) == 1:
            return parcial[0]
        # tokens sin orden: "FC Cajamarca" vs "Cajamarca FC", o añadidos tipo
        # "Club Deportivo Los Chankas" vs "Los Chankas" — solo con match ÚNICO
        qt = set(q.split())
        tokens = [n for n, nn in equipos_db
                  if qt and (qt <= set(nn.split()) or set(nn.split()) <= qt)]
        return tokens[0] if len(tokens) == 1 else nombre

    depositados, ignorados = 0, []
    canonizados: dict[str, str] = {}
    tipos_validos = set(efedb.TIPOS) | {"timeline_eventos"}
    for e in body.equipos:
        nombre = (e.equipo or "").strip()
        if not nombre:
            continue
        canon = _canonico(nombre)
        if canon != nombre:
            canonizados[nombre] = canon
        for tipo, contenido in e.datos.items():
            if tipo not in tipos_validos:
                ignorados.append(tipo)
                continue
            if tipo == "timeline_eventos":
                # lista de eventos (o string con el JSON de la lista)
                if isinstance(contenido, str):
                    try:
                        contenido = json.loads(contenido)
                    except ValueError:
                        continue
                if not isinstance(contenido, list) or not contenido:
                    continue
            else:
                contenido = (contenido or "").strip() if isinstance(contenido, str) else ""
                if not contenido:
                    continue
            efedb.guardar_investigacion(canon, tipo, contenido, body.fuentes or None)
            depositados += 1
    print(f"[despensa] carga manual: {depositados} datos "
          f"({', '.join(e.equipo for e in body.equipos)})"
          + (f" · canonizados: {canonizados}" if canonizados else "")
          + (f" · tipos ignorados: {sorted(set(ignorados))}" if ignorados else ""), flush=True)
    return {
        "depositados": depositados,
        "equipos": [canonizados.get(e.equipo, e.equipo) for e in body.equipos],
        "canonizados": canonizados,
        "tiposValidos": list(efedb.TIPOS),
        "tiposIgnorados": sorted(set(ignorados)),
    }


@app.post(API + "/analisis/efe")
def analisis_efe(body: EfeRequest):
    """Lanza el análisis EFE del fixture (o lo devuelve si ya existe).

    Con `forzar` el análisis guardado se borra y se emite uno nuevo (créditos).
    Respuesta INMEDIATA — el análisis tarda 1-3 min y corre en un hilo del
    servidor: estado 'listo' (con registro), 'generando' o 'error'. El
    frontend sondea /analisis/efe/estado/{id} hasta que esté listo."""
    from backend.analisis import motor as efemotor
    try:
        return efemotor.iniciar_efe(body.fixtureId, forzar=body.forzar,
                                    permitir_frio=body.permitirFrio)
    except efemotor.FixtureNoExiste as e:
        raise HTTPException(status_code=404, detail=str(e))
    except efemotor.SinClave as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get(API + "/analisis/efe/estado/{fixture_id}")
def analisis_efe_estado(fixture_id: int):
    """Sondeo del trabajo: listo (con registro) / generando / error / nada."""
    from backend.analisis import motor as efemotor
    return efemotor.estado_efe(fixture_id)


@app.post(API + "/analisis/timeline")
def analisis_timeline(body: EfeRequest):
    """Lanza el timeline comparativo del fixture (modo futbol-timeline).

    Mismo patrón asíncrono que el EFE: respuesta inmediata y sondeo en
    /analisis/timeline/estado/{id}. Con `forzar` regenera. Hereda alertas y
    colores del EFE previo si existe (cero búsquedas duplicadas)."""
    from backend.analisis import motor as efemotor
    try:
        return efemotor.iniciar_timeline(body.fixtureId, forzar=body.forzar)
    except efemotor.FixtureNoExiste as e:
        raise HTTPException(status_code=404, detail=str(e))
    except efemotor.SinClave as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get(API + "/analisis/timeline/estado/{fixture_id}")
def analisis_timeline_estado(fixture_id: int):
    """Sondeo del trabajo de timeline: listo / generando / error / nada."""
    from backend.analisis import motor as efemotor
    return efemotor.estado_timeline(fixture_id)


@app.get(API + "/analisis/partido/{fixture_id}")
def analisis_partido(fixture_id: int):
    """Todo lo emitido para un fixture (lectura pura, cero créditos)."""
    from backend.analisis import motor as efemotor
    return efemotor.analisis_del_partido(fixture_id)
