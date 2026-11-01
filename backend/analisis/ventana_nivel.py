"""CON QUÉ PARTIDOS SE ARMÓ EL NIVEL (30/10/2026, incidencia 860).

Konyaspor 0-4 Galatasaray: el 1X2 del motor dio 41 % al 14.º contra 31 % al
líder, con fiabilidad «alta». El nivel de Galatasaray (ventana de los últimos
20 partidos terminados, todas las competiciones: MOTOR §2) traía SEIS amistosos
de pretemporada (Monza 0-2, Venezia 0-3, Villarreal 1-2…) y tres de Champions:
1,65 puntos por partido en la ventana contra 2,44 en la liga. Lo salvó seguir
al mercado (sad v4.1).

MEDIDO el mismo día (`backend/backtest_nivel_ventana.py`, 9.191 partidos de
prueba del padrón): los amistosos NO eran la causa. Sacarlos del nivel no mejora
el 1X2 (+0,0009 de log-loss, IC cruzando cero), sacar también los
internacionales lo EMPEORA justo donde hay amistosos (+0,0066) y en el caso el
local pasa de 41,4 % a 40,8 %. El 41 % sale de un nivel que separaba al líder
del 14.º por solo 0,26, menos de lo que vale jugar en casa (0,382 de μ = 0,55 de
nivel). La localía tampoco es: la de la Süper Lig medida por liga es 0,479, de
las del medio (`backtest_localia_liga`). La forma y la regresión NO entran al
1X2 (`unXDos` solo ve nivel, rival y localía). Lo que sí se midió: con 3+ amistosos en un lado el motor queda
el doble de lejos del mercado (log-loss 0,084 peor, n = 989, contra 0,041 en el
resto). Eso sostiene el aviso.

Esto NO toca la fórmula del motor (es sagrada). Acá solo se CUENTA de qué está
hecha la ventana y se dice cuánto creerle a μ: con `UMBRAL_AMISTOSOS` amistosos
o más en la ventana de un lado, la fiabilidad de μ baja a «media» con la nota.
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


VENTANA_CORTA = 10      # con menos partidos en la ventana, el nivel casi no tiene historia
VENTANA_VIEJA_DIAS = 365   # con el último partido de hace más, el nivel es de otra época


def cancha_neutral(home_id: int, sede: str | None, antes: str | None) -> bool:
    """¿El partido se juega fuera de la cancha habitual del local? La sede más
    repetida en sus últimos 20 partidos de local (con 5+), distinta de esta
    (01/11/2026, incidencia 991: Franciscain–Aiglon en el Stade Louis-Achille)."""
    if not sede:
        return False
    params: list = [home_id]
    cond = ""
    if antes:
        cond = " AND date < ?"
        params.append(str(antes).replace("T", " ").rstrip("Z")[:19])
    try:
        filas = saddb.query("sad", f"SELECT venue_name FROM fixtures WHERE home_team_id=? AND venue_name IS NOT NULL"
                                   f"{cond} ORDER BY date DESC LIMIT 20", tuple(params))
    except Exception:  # noqa: BLE001 — base sin la sede: no se afirma cancha neutral
        return False
    if len(filas) < 5:
        return False
    cuenta: dict[str, int] = {}
    for f in filas:
        cuenta[f["venue_name"]] = cuenta.get(f["venue_name"], 0) + 1
    habitual = max(cuenta, key=cuenta.get)
    return cuenta[habitual] * 2 > len(filas) and habitual.strip().lower() != sede.strip().lower()


def _vieja_o_corta(c: dict | None, fecha: str | None) -> str:
    if not c:
        return ""
    if c["partidos"] < VENTANA_CORTA:
        return f"solo {c['partidos']} partidos en la ventana"
    if fecha and c.get("hasta"):
        try:
            from datetime import datetime
            dias = (datetime.fromisoformat(str(fecha)[:10]) - datetime.fromisoformat(c["hasta"][:10])).days
        except ValueError:
            return ""
        if dias > VENTANA_VIEJA_DIAS:
            return f"el último partido de la ventana es de hace {dias} días ({c['hasta']})"
    return ""


def fiabilidad_con_ventana(fia: dict, comps: dict, nombres: dict | None = None,
                           fecha: str | None = None, neutral: bool = False) -> dict:
    """La fiabilidad de μ con lo que dice la ventana de cada lado. Con
    `UMBRAL_AMISTOSOS`+ amistosos en un lado, «alta» baja a «media»; «media» y
    «baja» se quedan y la nota lo suma. Nunca la sube.

    VENTANA CORTA O VIEJA Y CANCHA NEUTRAL (01/11/2026, incidencia 991, decisión
    del usuario): con menos de `VENTANA_CORTA` partidos o el último de hace más
    de un año, la fiabilidad baja a «baja»; en cancha neutral la localía de μ no
    aplica y se dice (`canchaNeutral`). La fórmula no se toca."""
    nombres = nombres or {"local": "el local", "visitante": "el visitante"}
    con = {lado: c for lado, c in comps.items() if c and c["amistosos"] >= UMBRAL_AMISTOSOS}
    out = dict(fia or {})
    out["ventana"] = {lado: texto(c) for lado, c in comps.items() if texto(c)}
    viejas = {lado: m for lado, c in comps.items() if (m := _vieja_o_corta(c, fecha))}
    if viejas:
        out["nivel"] = "baja"
        out["porVentana"] = True
        out["nota"] = (f"{out.get('nota', '')} El nivel casi no tiene historia útil ("
                       + "; ".join(f"{nombres.get(l, l)}: {m}" for l, m in viejas.items())
                       + "): μ apenas orienta.").strip()
    if neutral:
        out["canchaNeutral"] = True
        out["nota"] = (f"{out.get('nota', '')} Se juega en cancha neutral: la localía que suma μ al local no "
                       "aplica (el motor la suma igual).").strip()
        if out.get("nivel") == "alta":
            out["nivel"] = "media"
    if not con:
        return out
    detalle = "; ".join(f"{nombres.get(l, l)}: {texto(c)}" for l, c in con.items())
    nota = (f"El nivel se armó con partidos de otra exigencia ({detalle} en la ventana de {VENTANA}). "
            "En partidos así el 1X2 del motor queda el doble de lejos del mercado (log-loss 0,084 peor, "
            "contra 0,041 en el resto; backtest del 30/10/2026) y sacar los amistosos del nivel no lo "
            "arregla. μ no se toca: no te separes del mercado por el motor.")
    if out.get("nivel") == "alta":
        out["notaLiga"] = out.get("nota", "")
        out["nivel"] = "media"
        out["nota"] = nota
    else:
        out["nota"] = f"{out.get('nota', '')} Además: {nota}".strip()
    out["porVentana"] = True
    return out
