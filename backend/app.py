"""SAD API — backend FastAPI de solo lectura sobre el pipeline SQLite.

Implementa el contrato docs/openapi.yaml del repo App-Profesional-de-Apuestas
(el frontend web lo consume con VITE_DATA_SOURCE=http). v0: sin escrituras;
auth bearer opcional (SAD_API_TOKEN), rate limit por IP (SAD_RATE_LIMIT),
CORS solo local salvo SAD_CORS_ORIGINS, docs desactivables (SAD_DOCS).

Ejecutar junto a las DBs reales:
    uvicorn backend.app:app --port 8000
"""
import os
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
    allow_methods=["GET"],
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


if INGESTA_HORA:
    threading.Thread(target=_ingesta_diaria_loop, daemon=True, name="ingesta-diaria").start()

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

# Ley de la Regresión al Nivel (§5) — coeficientes de regresion_nivel_engine.py
MU = {"intercept": 1.110, "nivel": 0.686, "rival": -0.669, "localia": 0.422}
RECENT_WINDOW = 5

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
    }


FIXTURE_SQL = """
SELECT f.id, f.date, f.status_long, f.status_short, f.elapsed,
       f.league_id, f.league_season, f.venue_name,
       f.goals_home, f.goals_away,
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


def nivel_a_fecha(team_id: int, fecha_iso: str | None) -> float:
    """Último level con date <= fecha (0.5 si no hay registros — §2.3)."""
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
    return float(row["level"]) if row else 0.5


def pts_recientes(team_id: int, antes_de: str | None) -> float | None:
    """Promedio de puntos en los últimos 5 terminados (None si no hay 5)."""
    cond, params = "", [team_id, team_id]
    if antes_de:
        cond = " AND f.date < ?"
        params.append(antes_de.replace("T", " ").rstrip("Z"))
    rows = db.query(
        "sad",
        f"""SELECT f.home_team_id, f.goals_home, f.goals_away
            FROM fixtures f
            WHERE (f.home_team_id=? OR f.away_team_id=?)
              AND f.status_long='Match Finished'
              AND f.goals_home IS NOT NULL AND f.goals_away IS NOT NULL{cond}
            ORDER BY f.date DESC LIMIT {RECENT_WINDOW}""",
        tuple(params),
    )
    if len(rows) < RECENT_WINDOW:
        return None
    pts = 0
    for r in rows:
        gf, ga = (r["goals_home"], r["goals_away"]) if r["home_team_id"] == team_id else (r["goals_away"], r["goals_home"])
        pts += 3 if gf > ga else 1 if gf == ga else 0
    return pts / RECENT_WINDOW


def gap_equipo(team_id: int, fecha: str | None) -> dict:
    nivel = nivel_a_fecha(team_id, fecha)
    recientes = pts_recientes(team_id, fecha)
    esperados = mu(nivel, 2.0, 0.5)  # rival promedio, localía neutra
    gap = None if recientes is None else esperados - recientes
    senal = None
    tendencia = None
    if gap is not None:
        a = abs(gap)
        senal = "fuerte" if a > 0.5 else "leve" if a >= 0.3 else "equilibrio"
        tendencia = None if gap == 0 else ("mejora" if gap > 0 else "empeora")
    return {
        "equipoId": team_id,
        "nivel": round(nivel, 4),
        "ptsRecientes": recientes,
        "ptsEsperados": round(esperados, 4),
        "gap": None if gap is None else round(gap, 4),
        "senal": senal,
        "tendencia": tendencia,
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
            gf, ga = (f["goals_home"], f["goals_away"]) if es_local else (f["goals_away"], f["goals_home"])
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


# Mapeo bet_name/value de API-Football → mercados del contrato
def cuota_key(bet_name: str, value: str):
    b = (bet_name or "").lower()
    v = (value or "").strip()
    # "fulltime result": nombre del 1X2 en el catálogo de /odds/live
    if "match winner" in b or "fulltime result" in b or b == "1x2":
        return {"Home": ("1x2", "1"), "Draw": ("1x2", "X"), "Away": ("1x2", "2"),
                "1": ("1x2", "1"), "X": ("1x2", "X"), "2": ("1x2", "2")}.get(v)
    if "double chance" in b:
        return {"Home/Draw": ("dc", "1X"), "Home/Away": ("dc", "12"), "Draw/Away": ("dc", "X2")}.get(v)
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
    limit: int = Query(default=50, ge=1, le=200),
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
    """k_cuota (§3.8): rachas de suma de cuota 1X2, solo 2026. Vacío si no se
    ha construido constants_cuota (correr backend/backfill_cuota)."""
    return constantes_cuota_de(equipo_id)


@app.get(API + "/predicciones/{fixture_id}")
def prediccion(fixture_id: int):
    f = get_fixture(fixture_id)
    fecha = iso(f["date"])
    local = gap_equipo(f["home_team_id"], fecha)
    visitante = gap_equipo(f["away_team_id"], fecha)
    gap_diff = None
    if local["gap"] is not None and visitante["gap"] is not None:
        gap_diff = round(local["gap"] - visitante["gap"], 4)
    return {
        "fixtureId": fixture_id,
        "local": local,
        "visitante": visitante,
        "gapDiff": gap_diff,
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
        """SELECT home_team_id, goals_home, goals_away FROM fixtures
           WHERE (home_team_id=? OR away_team_id=?)
             AND status_long='Match Finished'
             AND goals_home IS NOT NULL AND goals_away IS NOT NULL
           ORDER BY date DESC LIMIT 2000""",
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


@app.get(API + "/ligas/{liga_id}")
def liga(liga_id: int):
    """Metadatos de la liga (nombre, país, logo, bandera, temporadas capturadas)."""
    meta = liga_meta(liga_id)
    if meta["pais"] is None and meta["logo"] is None and meta["nombre"] == f"Liga {liga_id}":
        raise HTTPException(404, f"liga {liga_id} no existe")
    rows = db.query(
        "sad",
        "SELECT DISTINCT league_season AS s FROM fixtures WHERE league_id=? AND league_season IS NOT NULL ORDER BY s DESC",
        (liga_id,),
    )
    return {"id": liga_id, **meta, "temporadas": [r["s"] for r in rows]}


@app.get(API + "/ligas/{liga_id}/standings")
def standings(liga_id: int, temporada: int | None = None):
    """Tabla de posiciones calculada de los fixtures terminados de la liga."""
    if temporada is None:
        row = db.query_one("sad", "SELECT MAX(league_season) AS s FROM fixtures WHERE league_id=?", (liga_id,))
        temporada = row["s"] if row and row["s"] is not None else 0
    rows = db.query(
        "sad",
        """SELECT f.home_team_id, f.away_team_id, f.goals_home, f.goals_away,
                  ht.name AS home_name, at.name AS away_name
           FROM fixtures f
           JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id
           WHERE f.league_id=? AND f.league_season=? AND f.status_long='Match Finished'
             AND f.goals_home IS NOT NULL AND f.goals_away IS NOT NULL
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
        upsert(r["home_team_id"], r["home_name"], r["goals_home"], r["goals_away"])
        upsert(r["away_team_id"], r["away_name"], r["goals_away"], r["goals_home"])
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
    cuotas = []
    serie = []
    for r in filas:
        key = cuota_key(r["bet_name"], r["value"])
        if not key:
            continue
        punto = {"mercado": key[0], "seleccion": key[1], "cuota": round(float(r["odd"]), 2)}
        if not r["suspendida"]:
            serie.append({"minuto": r["minuto"], **punto})
        if r["captured_at"] == ultima:
            cuotas.append({**punto, "suspendida": bool(r["suspendida"])})
    return {
        "fixtureId": fixture_id,
        "estado": estado_de(f["status_short"], f["status_long"]),
        "minuto": f["elapsed"],
        "golesLocal": f["goals_home"],
        "golesVisitante": f["goals_away"],
        "cuotas": cuotas,
        "serie": serie,
        "actualizadoEn": iso(ultima) if ultima else None,
    }


@app.get(API + "/cuotas/{fixture_id}/casas")
def cuotas_casas(fixture_id: int):
    """Cuota de cada casa por selección (última foto). La más alta de cada
    selección va marcada con mejor=true: ahí paga más ese acierto."""
    rows = db.query(
        "sad",
        "SELECT bookmaker_id, bookmaker_name, bet_name, value, odd FROM odds "
        "WHERE fixture_id=? AND odd IS NOT NULL AND bookmaker_id IS NOT NULL",
        (fixture_id,),
    )
    por_sel: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        key = cuota_key(r["bet_name"], r["value"])
        if key:
            por_sel.setdefault(key, []).append(
                {
                    "fixtureId": fixture_id,
                    "mercado": key[0],
                    "seleccion": key[1],
                    "casaId": r["bookmaker_id"],
                    "casa": r["bookmaker_name"] or f"casa {r['bookmaker_id']}",
                    "cuota": round(float(r["odd"]), 2),
                }
            )
    out = []
    for key in sorted(por_sel):
        filas = sorted(por_sel[key], key=lambda f: -f["cuota"])
        tope = filas[0]["cuota"]
        out.extend({**f, "mejor": f["cuota"] >= tope - 1e-9} for f in filas)
    return out


@app.get(API + "/cuotas/{fixture_id}/historial")
def cuotas_historial(fixture_id: int):
    """Snapshots prepartido de odds_history (asc por captura). [] si la DB
    aún no tiene la tabla (anterior a la fase 1 de tiempo real)."""
    try:
        rows = db.query(
            "sad",
            "SELECT bet_name, value, odd, casas, captured_at FROM odds_history "
            "WHERE fixture_id=? AND odd IS NOT NULL ORDER BY captured_at, bet_name, value",
            (fixture_id,),
        )
    except Exception:
        return []
    out = []
    for r in rows:
        key = cuota_key(r["bet_name"], r["value"])
        if key:
            out.append(
                {
                    "fixtureId": fixture_id,
                    "mercado": key[0],
                    "seleccion": key[1],
                    "cuota": round(float(r["odd"]), 2),
                    "casas": r["casas"],
                    "capturadoEn": iso(r["captured_at"]),
                }
            )
    return out
