"""La escala entre divisiones: de qué base sale el nivel de cada equipo.

POR QUÉ. El nivel SAD es puntos y goles contra los rivales de cada uno: el de
un equipo de Liga 2 se mide contra Liga 2. Cuando se cruzan dos bases —una
copa nacional (Copa Bicentenario, FA Cup, Copa del Rey), un ascendido, un
amistoso internacional— el número de los dos NO mide lo mismo, y el reventón
compara el nivel del rival con los niveles que reventaron las burbujas del
equipo EN SU LIGA. Bentín (Liga 2) le salió a Sporting Cristal como un rival
«fuerte» en la Copa (tercera tanda de Perú, 13/10/2026): era el nivel de la
cima de Liga 2 leído en la escala de Liga 1.

QUÉ HACE. Calculado de la base, 0 requests:

- `base_de(equipo, fecha)`: la liga doméstica (la más frecuente del último
  año, sin copas, internacionales ni amistosos) y su CATEGORÍA. Un equipo que
  en la base solo tiene partidos de copa juega en una liga que no seguimos:
  `categoria: "fuera del padrón"` —casi siempre inferior—, no «primera».
- `entre(equipo, rival, fecha)`: las dos bases y la RELACIÓN (misma · rival
  de categoría inferior · superior · otra liga · rival fuera del padrón).
- `historial(equipo, filas, cerrados)`: cómo le fue al equipo contra rivales
  de otra base, partido a partido, y cuántos de esos partidos reventaron una
  burbuja. Es el dato que hace falta para leer un cruce de copa.

No mueve el riesgo calibrado (los puntos del rival salen del backtest): avisa
que el nivel del rival no es comparable y trae lo que sí lo es.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from backend import db as saddb

# Copas nacionales conocidas; el resto se reconoce por el nombre.
COPAS = {
    45, 48, 528,          # Inglaterra: FA Cup, EFL Cup, Community Shield
    143, 556,             # España: Copa del Rey, Supercopa
    137, 547,             # Italia: Coppa Italia, Supercoppa
    81, 529,              # Alemania: DFB Pokal, Supercup
    66, 526,              # Francia: Coupe de France, Trophée des Champions
    96, 550,              # Portugal: Taça de Portugal, Supertaça
    147, 519,             # Bélgica: Copa, Supercopa (ids confirmados con --buscar, 23/10/2026)
    90, 199, 206,         # Países Bajos, Grecia, Turquía: copas (en la base desde la fase 0, 29/10/2026)
    130, 73, 241, 267, 1220, 502, 1232, 930, 917, 501, 1113,  # Sudamérica (LIGAS_MENORES)
}
_COPA_RE = re.compile(r"\b(cup|copa|coppa|pokal|coupe|ta[cç]a|trophy|troph[ée]e|shield|super ?cup|supercopa|"
                      r"supercoppa|bicentenario)\b", re.I)
AMISTOSOS = {667}
HISTORIAL_MAX = 40       # filas de copa que se miran hacia atrás


def es_copa(liga_id: int | None, nombre: str | None = None) -> bool:
    if liga_id in COPAS:
        return True
    if nombre is None and liga_id is not None:
        from backend.app import liga_meta
        nombre = liga_meta(liga_id).get("nombre")
    return bool(nombre) and bool(_COPA_RE.search(nombre))


_INTERNACIONAL_RE = re.compile(r"uefa|conmebol|concacaf|fifa|caf |afc |recopa|leagues cup|club world|"
                               r"intercontinental|libertadores|sudamericana", re.I)


def copas_nacionales(fixture_ids) -> dict[int, str]:
    """{fixture: nombre de la copa} de los que son de una COPA NACIONAL (29/10/2026,
    usuario: «no hay que contaminar las tablas»). Se analizan igual, pero no
    entran a las métricas ni a la simulación: un favorito al 90 % contra uno
    de quinta división infla el acierto y el tramo alto de confianza. Los
    torneos internacionales de clubes NO son copa nacional aunque el nombre
    diga «Cup» (la Champions Cup de la Concacaf)."""
    ids = sorted({int(i) for i in fixture_ids or []})
    if not ids:
        return {}
    try:
        from backend.ingesta.extractor import LIGAS_INTERNACIONALES
        internacionales = set(LIGAS_INTERNACIONALES)
    except Exception:  # noqa: BLE001
        internacionales = set()
    out = {}
    try:
        for r in saddb.query("sad", "SELECT f.id, f.league_id, l.name FROM fixtures f "
                                    "LEFT JOIN leagues l ON l.id=f.league_id "
                                    f"WHERE f.id IN ({','.join('?' * len(ids))})", tuple(ids)):
            if r["league_id"] in internacionales or r["league_id"] in AMISTOSOS \
                    or _INTERNACIONAL_RE.search(r["name"] or ""):
                continue
            if es_copa(r["league_id"], r["name"] or ""):
                out[r["id"]] = r["name"] or f"liga {r['league_id']}"
    except Exception:  # noqa: BLE001 — sin la base no se marca nada
        return {}
    return out


def _fuera_de_liga() -> set[int]:
    from backend.analisis.parte import _internacionales_de_clubes
    return _internacionales_de_clubes() | {1} | AMISTOSOS


def categoria(liga_id: int, nombre: str | None = None) -> str:
    from backend.analisis.parte import _segunda
    return "segunda" if _segunda(liga_id, nombre) else "primera"


BASE_RECIENTES = 5   # partidos de liga seguidos en la misma que cambian la base del año


def _liga_reciente(team_id: int, hasta: str, desde: str, fuera: list) -> int | None:
    """La liga de los últimos BASE_RECIENTES partidos de LIGA (sin copas), si
    son todos de la misma; None si no hay tantos o si se mezclan."""
    try:
        filas = saddb.query(
            "sad",
            f"""SELECT league_id FROM fixtures
                WHERE (home_team_id=? OR away_team_id=?) AND date < ? AND date >= ?
                  AND (status_short IN ('FT','AET','PEN') OR status_long='Match Finished')
                  AND league_id IS NOT NULL AND league_id NOT IN ({",".join("?" * len(fuera))})
                ORDER BY date DESC LIMIT 40""",
            (team_id, team_id, hasta, desde, *fuera))
    except Exception:  # noqa: BLE001 — sin la base se queda la regla del año
        return None
    ligas = [f["league_id"] for f in filas if es_liga(f["league_id"])][:BASE_RECIENTES]
    return ligas[0] if len(ligas) == BASE_RECIENTES and len(set(ligas)) == 1 else None


def base_de(team_id: int, fecha: str | None) -> dict | None:
    """La base del nivel de un equipo. None si no tiene partidos terminados en
    el año (equipo nuevo en la base)."""
    from backend.app import liga_meta
    hasta = (fecha or datetime.utcnow().strftime("%Y-%m-%d")).replace("T", " ").rstrip("Z")
    try:
        desde = (datetime.strptime(hasta[:10], "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
    except ValueError:
        return None
    fuera = sorted(_fuera_de_liga())
    filas = saddb.query(
        "sad",
        f"""SELECT league_id, COUNT(*) AS n FROM fixtures
            WHERE (home_team_id=? OR away_team_id=?) AND date < ? AND date >= ?
              AND (status_short IN ('FT','AET','PEN') OR status_long='Match Finished')
              AND league_id IS NOT NULL AND league_id NOT IN ({",".join("?" * len(fuera))})
            GROUP BY league_id ORDER BY n DESC, league_id""",
        (team_id, team_id, hasta, desde, *fuera),
    )
    if not filas:
        return None
    # LA TEMPORADA EN CURSO MANDA SOBRE EL AÑO (incidencias 824 y 826: Racing de
    # Santander con 10 jornadas de LaLiga salía «Segunda División» porque el año
    # todavía tenía más partidos de Segunda; el Alavés de enero de 2024 figuraba
    # de categoría inferior estando en LaLiga). Si los últimos BASE_RECIENTES
    # partidos de liga son todos de la misma, esa es la base.
    reciente = _liga_reciente(team_id, hasta, desde, fuera)
    if reciente is not None and reciente != filas[0]["league_id"]:
        filas = sorted(filas, key=lambda f: f["league_id"] != reciente)
    copas = []
    for f in filas:
        meta = liga_meta(f["league_id"])
        if es_copa(f["league_id"], meta.get("nombre")):
            copas.append(meta.get("nombre"))
            continue
        return {"id": f["league_id"], "nombre": meta.get("nombre"), "pais": meta.get("pais"),
                "partidos": f["n"], "categoria": categoria(f["league_id"], meta.get("nombre"))}
    # solo copas: su liga no está en la base
    return {"id": None, "nombre": None, "pais": None, "partidos": 0, "categoria": "fuera del padrón",
            "soloCopa": copas[:3]}


_ORDEN = {"primera": 0, "segunda": 1, "fuera del padrón": 2}


# SIN PARTIDOS OFICIALES EN LA BASE ES ESTAR FUERA DEL PADRÓN (incidencias 801 y
# 798, Copa del Rey 29/10/2026: Varea y Laredo, de Tercera RFEF, contra Andorra
# y Burgos de Segunda salían «sin dato» y comparables, sin ESCALA-LIGAS ni
# fiabilidad baja; Coruxo–Zamora, dos de Federación, igual). Un equipo que juega
# hoy y no tiene un partido de liga ni de copa terminado en el año juega una liga
# que la base no sigue.
SIN_BASE = {"id": None, "nombre": None, "pais": None, "partidos": 0, "categoria": "fuera del padrón",
            "sinPartidos": True}


def relacion(a: dict | None, b: dict | None) -> str:
    """Cómo es la base de `b` (el rival) frente a la de `a` (el equipo)."""
    a, b = a or SIN_BASE, b or SIN_BASE
    if a.get("id") is not None and a.get("id") == b.get("id"):
        return "misma"
    ca, cb = _ORDEN[a["categoria"]], _ORDEN[b["categoria"]]
    if cb > ca:
        return "rival de categoría inferior" if b["categoria"] != "fuera del padrón" else "rival fuera del padrón"
    if cb < ca:
        return "rival de categoría superior"
    if a.get("pais") and a.get("pais") == b.get("pais"):
        return "misma"          # Apertura/Clausura con dos ids, misma categoría
    return "otra liga"


def cambio_de_categoria(base: dict | None, liga_partido: int | None) -> str:
    """«ascendido» / «descendido» si el partido es de liga y de otra categoría
    que la base donde el equipo armó su historia (West Ham en el Championship,
    Coventry en la Premier: las medianas del reventón son de la otra)."""
    if not base or base.get("id") is None or not liga_partido or liga_partido == base["id"]:
        return ""
    if liga_partido in _fuera_de_liga() or es_copa(liga_partido):
        return ""
    nueva = categoria(liga_partido)
    if nueva == base["categoria"]:
        return ""
    return "ascendido" if _ORDEN[nueva] < _ORDEN[base["categoria"]] else "descendido"


RECESO_DIAS = 60   # cuánto hacia adelante se busca la liga de la temporada que arranca


def es_liga(liga_id: int | None) -> bool:
    return bool(liga_id) and liga_id not in _fuera_de_liga() and not es_copa(liga_id)


def liga_vigente(team_id: int, fecha: str | None) -> int | None:
    """La liga de la temporada que se está jugando o que arranca: la del
    próximo partido de LIGA del equipo desde `fecha` (hasta RECESO_DIAS). En
    pretemporada la base del último año es la temporada vieja: Mallorca
    (descendido) y Elversberg (ascendido) se cruzaron en un amistoso con la
    escala al revés (14/10/2026)."""
    if not fecha:
        return None
    desde = fecha.replace("T", " ").rstrip("Z")[:19]
    try:
        hasta = (datetime.strptime(desde[:10], "%Y-%m-%d") + timedelta(days=RECESO_DIAS)).strftime("%Y-%m-%d")
        filas = saddb.query("sad", "SELECT league_id FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
                                   "AND date >= ? AND date < ? AND league_id IS NOT NULL ORDER BY date",
                            (team_id, team_id, desde, hasta))
    except Exception:  # noqa: BLE001
        return None
    return next((f["league_id"] for f in filas if es_liga(f["league_id"])), None)


def _cambio_en_receso(base: dict | None, team_id: int, fecha: str | None, liga_partido: int | None) -> str:
    vig = liga_partido if es_liga(liga_partido) else liga_vigente(team_id, fecha)
    return cambio_de_categoria(base, vig)


def entre(team_id: int, rival_id: int, fecha: str | None, liga_partido: int | None = None) -> dict:
    a, b = base_de(team_id, fecha), base_de(rival_id, fecha)
    cambio = _cambio_en_receso(a, team_id, fecha, liga_partido)
    cambio_r = _cambio_en_receso(b, rival_id, fecha, liga_partido)
    if not es_liga(liga_partido) and (cambio or cambio_r):
        # amistoso o copa en pretemporada: alguno de los dos ya cambió de categoría
        partes = []
        if cambio:
            partes.append(f"el equipo {cambio} (su historia es de {a.get('nombre')}, {a['categoria']})")
        if cambio_r:
            partes.append(f"el rival {cambio_r} (su nivel es de {b.get('nombre')}, {b['categoria']})")
        return {"equipo": a, "rival": b, "relacion": f"equipo {cambio}" if cambio else f"rival {cambio_r}",
                "comparable": False, "cambioDeCategoria": cambio or None, "cambioDeCategoriaRival": cambio_r or None,
                "nota": ("cambio de categoría en el receso: " + " y ".join(partes) + ". La base mira el año "
                         "anterior, así que la relación entre los dos está medida en la temporada vieja · "
                         "tomalo con esa reserva")}
    if cambio and b and b.get("id") == liga_partido:
        # el rival es de la liga nueva del equipo: lo que no compara es la HISTORIA del equipo
        from backend.app import liga_meta
        nueva = liga_meta(liga_partido).get("nombre")
        return {"equipo": a, "rival": b, "relacion": f"equipo {cambio}", "comparable": False,
                "cambioDeCategoria": cambio,
                "nota": (f"el equipo armó su historia en {a.get('nombre')} ({a['categoria']}) y ahora juega "
                         f"{nueva} ({categoria(liga_partido)}): las medianas del reventón (K, partidos, nivel "
                         f"del rival que la revienta) son de la categoría vieja. "
                         + ("Recién descendido: casi todo rival le queda «lejos» y el riesgo sale bajo por la "
                            "escala, no por el partido" if cambio == "descendido" else
                            "Recién ascendido: casi todo rival le queda «fuerte» y cualquier mala racha supera "
                            "su récord (el extremo grita en parte por la escala)")
                         + " · tomalo con esa reserva")}
    rel = relacion(a, b)
    comparable = rel in ("misma", "sin dato")
    nota = ""
    if not comparable:
        nota = {
            "rival de categoría inferior": "el nivel del rival se midió contra SU división (más floja): leído "
                                           "en la escala del equipo, lo sobrestima. Un rival «fuerte» de abajo "
                                           "puede ser la cima de su liga, no un rival fuerte de la tuya",
            "rival fuera del padrón": "el rival solo tiene partidos de copa en la base: su liga no se sigue y su "
                                      "nivel no tiene escala (casi siempre es de categoría inferior)",
            "rival de categoría superior": "el nivel del rival se midió contra una división más fuerte: leído en "
                                           "la escala del equipo, lo subestima",
            "otra liga": "bases de países distintos: los niveles no comparan entre ligas",
        }[rel]
    return {"equipo": a, "rival": b, "relacion": rel, "comparable": comparable,
            "nota": nota + (" · el riesgo del reventón compara ese nivel con los rivales que reventaron las "
                            "burbujas del equipo en SU liga: tomalo con esa reserva" if nota else "")}


HISTORIA_VENTANA = 20


def historia_otra_categoria(filas: list[dict], base_id: int | None) -> dict | None:
    """¿Las K de hoy se armaron en OTRA liga? (incidencias 974 y 975: Beveren y
    Cambuur, ascendidos, con «escala misma» y la racha hecha casi entera en la
    categoría de abajo). De los últimos HISTORIA_VENTANA partidos de liga (sin
    copas, internacionales ni amistosos), los de una liga que no es la base de
    hoy; con la mitad o más, se marca. Solo marca: no mueve ningún número."""
    if not base_id:
        return None
    ligas = [f.get("ligaId") for f in filas if es_liga(f.get("ligaId"))][-HISTORIA_VENTANA:]
    otras = [l for l in ligas if l != base_id]
    if not ligas or len(otras) * 2 < len(ligas):
        return None
    return {"partidos": len(otras), "de": len(ligas),
            "nota": f"{len(otras)} de los últimos {len(ligas)} partidos de liga son de otra categoría: "
                    "las K y las rachas se armaron contra otros rivales (el ascendido); leer la tarjeta con reserva"}


def historial(team_id: int, filas: list[dict], cerrados: set[int] | None = None) -> dict:
    """Los partidos del equipo contra rivales de otra base (copas, amistosos
    internacionales fuera), con el resultado y si reventaron una burbuja.
    `filas` son las constantes del equipo (cronológicas)."""
    cerrados = cerrados or set()
    fuera = _fuera_de_liga()
    casos = [f for f in filas if f.get("ligaId") not in fuera and es_copa(f.get("ligaId"))][-HISTORIAL_MAX:]
    por: dict[str, dict] = {}
    partidos = []
    for f in casos:
        fecha = str(f.get("fecha"))[:10]
        rel = relacion(base_de(team_id, fecha), base_de(f["rivalId"], fecha))
        if rel in ("misma", "sin dato"):
            continue
        gf, gc = f.get("golesFavor") or 0, f.get("golesContra") or 0
        res = "G" if gf > gc else "E" if gf == gc else "P"
        g = por.setdefault(rel, {"partidos": 0, "G": 0, "E": 0, "P": 0, "reventones": 0})
        g["partidos"] += 1
        g[res] += 1
        g["reventones"] += 1 if f.get("fixtureId") in cerrados else 0
        partidos.append({"fixtureId": f.get("fixtureId"), "fecha": fecha, "rival": f.get("rivalNombre"),
                         "ligaId": f.get("ligaId"), "relacion": rel, "resultado": f"{gf}-{gc}",
                         "reventoBurbuja": f.get("fixtureId") in cerrados})
    # `porRelacion` cuenta TODOS los casos y la lista trae los últimos 10 (826):
    # se dice, para que los conteos no parezcan descuadrados
    return {"porRelacion": por, "partidos": partidos[-10:], "partidosTotal": len(partidos),
            "nota": "partidos de copa contra rivales de otra base; un E o P contra un rival de categoría "
                    "inferior es el reventón que el nivel no ve venir"}


def bajar_confianza(familias: dict, esc: dict) -> None:
    """LA ESCALA MUEVE LA CONFIANZA, NUNCA EL RIESGO: con el rival o la historia
    en otra categoría, los puntos comparan cosas distintas. Una sola regla para
    la tarjeta (/burbujas) y el reventón del parte (incidencia 295: Sabah traía
    «escala distinta» en /burbujas y no en reventonCalculado)."""
    if esc.get("comparable", True):
        return
    for fam in (familias or {}).values():
        rg = (fam or {}).get("riesgo")
        if rg and rg.get("nivel") != "sin base":
            rg["confianza"] = "baja"
            motivo = (f"escala distinta ({esc.get('relacion')}): el nivel del rival o las medianas "
                      "no están en la misma escala")
            if motivo not in rg.setdefault("confianzaMotivos", []):
                rg["confianzaMotivos"].append(motivo)


# ── la MARCA de escala: se dice dónde, no se mueve ningún número ─────────────
# Decisión del usuario (22/10/2026, incidencias 300, 309, 294 y 79): con la
# escala distinta, los puntos del rival, la tarjeta de la espina, el perfil de
# doble oportunidad y el P1a del TDE SIGUEN como están —son números calibrados
# o insumos del skill— y llevan la marca en el sitio donde se leen. Vasco–Boca
# sumó «rival muy fuerte» comparando el Brasileirão con la liga argentina;
# Sporting–LASK siguió una tarjeta «fuerte» medida con un rival austríaco. La
# confianza baja ya estaba; faltaba que lo dijera la línea que se usa.

def nota_escala(esc: dict) -> str:
    return (f"escala distinta ({esc.get('relacion')}): este número compara niveles de bases distintas; "
            "se muestra igual, pero no se lo sigue por sí solo")


def marcar(familias: dict, esc: dict) -> None:
    """Marca el rival y la tarjeta de la espina de cada familia (no los cambia)."""
    if esc.get("comparable", True):
        return
    for fam in (familias or {}).values():
        if not fam:
            continue
        if fam.get("rival"):
            fam["rival"]["escalaComparable"] = False
            fam["rival"]["notaEscala"] = nota_escala(esc)
        marcar_tarjeta(fam.get("espinaTarjeta"), esc)


def marcar_tarjeta(tarjeta: dict | None, esc: dict) -> dict | None:
    """La tarjeta «fuerte» con escala distinta sigue fuerte —es la guía
    calibrada— pero dice que no se la sigue POR ser fuerte (Sporting–LASK)."""
    if tarjeta and not esc.get("comparable", True):
        tarjeta["escala"] = esc.get("relacion")
        tarjeta["notaEscala"] = nota_escala(esc) + (
            ": la fuerza sale de una guía medida con rivales de su propia liga" if tarjeta.get("fuerza") == "fuerte" else "")
    return tarjeta


def marcar_perfil(otras: dict | None, esc: dict) -> None:
    """El perfil de doble oportunidad cuenta la historia del equipo en su
    condición; si viene de otra división o el rival es de otra base, lo dice
    (Estudiantes RC: «no pierde 79 %» mezclaba Primera Nacional y Primera)."""
    p = (otras or {}).get("perfilDc")
    if p and not esc.get("comparable", True):
        p["escala"] = esc.get("relacion")
        p["notaEscala"] = (f"escala distinta ({esc.get('relacion')}): la frecuencia sale de partidos contra "
                           "rivales de su propia base; contra este rival puede no valer")
