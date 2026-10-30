"""CON QUÉ PARTIDOS SE ARMÓ EL NIVEL (30/10/2026, incidencia 860).

Konyaspor 0-4 Galatasaray: el 1X2 del motor dio 41 % al 14.º contra 31 % al
líder, con fiabilidad «alta». El nivel de Galatasaray (ventana de los últimos
20 partidos terminados, todas las competiciones: MOTOR §2) traía SEIS amistosos
de pretemporada (Monza 0-2, Venezia 0-3, Villarreal 1-2…) y tres de Champions:
1,65 puntos por partido en la ventana contra 2,44 en la liga. Con ese nivel
bajo, su forma de 2,4 parecía «rendir de más» y el motor le restó otra vez por
regresión. Lo salvó seguir al mercado (sad v4.1).

Esto NO toca la fórmula del motor (es sagrada; el backtest
`backend/backtest_nivel_ventana.py` mide si sacar los amistosos o los
internacionales del nivel mejora el 1X2). Acá solo se CUENTA de qué está hecha
la ventana y se dice cuánto creerle a μ: con `UMBRAL_AMISTOSOS` amistosos o más
en la ventana de un lado, la fiabilidad de μ baja a «media» con la nota.
Solo lectura, una consulta por equipo.
"""
from __future__ import annotations

from backend import db as saddb

VENTANA = 20                 # la del motor (MOTOR_SAD_EXTRACCION.md §2)
AMISTOSOS = {10, 667}        # Friendlies (selecciones) y Friendlies Clubs
UMBRAL_AMISTOSOS = 3         # desde acá la fiabilidad de μ baja a «media»
_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long = 'Match Finished')"


def _internacionales() -> set[int]:
    try:
        from backend.ingesta.extractor import LIGAS_INTERNACIONALES
        return set(LIGAS_INTERNACIONALES)
    except Exception:  # noqa: BLE001 — sin la ingesta importable: la lista conocida
        return {2, 3, 848, 13, 11}


def es_amistoso(league_id, nombre: str | None = None) -> bool:
    n = (nombre or "").lower()
    return league_id in AMISTOSOS or "friendl" in n or "amistos" in n


def composicion(team_id: int, antes: str | None) -> dict | None:
    """Los últimos `VENTANA` partidos terminados del equipo ANTES de `antes`
    (el mismo filtro y la misma deduplicación que el pipeline del motor),
    contados por tipo. None sin partidos."""
    params: list = [team_id, team_id]
    cond = ""
    if antes:
        cond = " AND f.date < ?"
        params.append(str(antes).replace("T", " ").rstrip("Z")[:19])
    try:
        filas = saddb.query(
            "sad", f"""SELECT f.id, f.date, f.league_id, f.home_team_id, f.away_team_id,
                              COALESCE(f.fulltime_home, f.goals_home) AS gh,
                              COALESCE(f.fulltime_away, f.goals_away) AS ga, l.name AS liga
                       FROM fixtures f LEFT JOIN leagues l ON l.id = f.league_id
                       WHERE (f.home_team_id=? OR f.away_team_id=?) AND {_FIN}
                         AND COALESCE(f.fulltime_home, f.goals_home) IS NOT NULL
                         AND COALESCE(f.fulltime_away, f.goals_away) IS NOT NULL{cond}
                       ORDER BY f.date DESC, f.id DESC LIMIT {VENTANA + 10}""", tuple(params))
    except Exception:  # noqa: BLE001 — base sin la tabla leagues o vieja: sin composición, no se afirma nada
        return None
    # el mismo partido con dos ids entra una vez (pipeline.sin_duplicados), en
    # el orden del motor (fecha, id)
    vistos, ventana = set(), []
    for f in sorted(filas, key=lambda r: (str(r["date"]), r["id"])):
        clave = (f["home_team_id"], f["away_team_id"], str(f["date"])[:10], f["gh"], f["ga"])
        if clave in vistos:
            continue
        vistos.add(clave)
        ventana.append(f)
    ventana = ventana[-VENTANA:]
    if not ventana:
        return None
    inter = _internacionales()
    amistosos = [f for f in ventana if es_amistoso(f["league_id"], f["liga"])]
    internacionales = [f for f in ventana if f["league_id"] in inter]
    return {
        "partidos": len(ventana),
        "amistosos": len(amistosos),
        "internacionales": len(internacionales),
        "otros": len(ventana) - len(amistosos) - len(internacionales),
        "desde": str(ventana[0]["date"])[:10],
        "hasta": str(ventana[-1]["date"])[:10],
        "completa": len(ventana) >= VENTANA,
    }


def texto(c: dict | None) -> str:
    if not c:
        return ""
    partes = []
    if c["amistosos"]:
        partes.append(f"{c['amistosos']} amistoso{'s' if c['amistosos'] != 1 else ''}")
    if c["internacionales"]:
        partes.append(f"{c['internacionales']} internacional{'es' if c['internacionales'] != 1 else ''}")
    return (" y ".join(partes) + f" de {c['partidos']}") if partes else ""


def fiabilidad_con_ventana(fia: dict, comps: dict, nombres: dict | None = None) -> dict:
    """La fiabilidad de μ con lo que dice la ventana de cada lado. Con
    `UMBRAL_AMISTOSOS`+ amistosos en un lado, «alta» baja a «media»; «media» y
    «baja» se quedan y la nota lo suma. Nunca la sube."""
    nombres = nombres or {"local": "el local", "visitante": "el visitante"}
    con = {lado: c for lado, c in comps.items() if c and c["amistosos"] >= UMBRAL_AMISTOSOS}
    out = dict(fia or {})
    out["ventana"] = {lado: texto(c) for lado, c in comps.items() if texto(c)}
    if not con:
        return out
    detalle = "; ".join(f"{nombres.get(l, l)}: {texto(c)}" for l, c in con.items())
    nota = (f"El nivel se armó con partidos de otra exigencia ({detalle} en la ventana de {VENTANA}). "
            "En pretemporada los grandes rotan y pierden con cualquiera, y el motor los cuenta igual que la "
            "liga: el nivel puede estar mal medido y la regresión castigar dos veces (Konyaspor 0-4 "
            "Galatasaray, 30/10/2026). μ no se toca: no te separes del mercado por el motor.")
    if out.get("nivel") == "alta":
        out["notaLiga"] = out.get("nota", "")
        out["nivel"] = "media"
        out["nota"] = nota
    else:
        out["nota"] = f"{out.get('nota', '')} Además: {nota}".strip()
    out["porVentana"] = True
    return out
