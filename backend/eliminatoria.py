"""QUIÉN PASÓ UNA ELIMINATORIA, calculado de NUESTRA base (29/10/2026, incidencia 774).

Palmeiras pasó a la final de la Libertadores por penales (0-1 en casa, 2-2 en
el global, 5-3 en la tanda) y el parte del Palmeiras–Bragantino lo dio por
ELIMINADO: el D3, el C4, la caja de sensibilidad y el ensayo se escribieron
sobre la «resaca de la eliminación». El dato estaba en la base —la ficha traía
los nueve `Shootout`— pero ninguna salida calculada lo resumía: el timeline
decía «Derrota 0-1 ante Fluminense» y el veredicto «ganador b» (el 1X2 se juzga
a 90', y eso está bien). Quien lee «derrota 0-1, 2-2 global, penales» sin contar
la tanda completa lo que falta, y lo completó al revés.

Regla: QUIÉN AVANZA NO SE INFIERE DEL MARCADOR. Sale de acá:
- la tanda de penales (`penalty_*` del fixture o, si la ingesta no la trae,
  los `Shootout` convertidos de la ficha);
- el global con el partido de ida (misma liga, temporada y ronda, los mismos
  dos equipos con la localía invertida, terminado y a ≤ 45 días), con goles de
  prórroga incluidos;
- a partido único, el ganador del partido con su prórroga.
Sin una de esas tres cosas no se afirma nada: `avanza` queda en None.

Solo lectura y cero requests: lee `fixtures` y `fixture_eventos` como estén
(las bases viejas sin columnas de penales caen a los eventos).
"""
from __future__ import annotations

import re
from datetime import datetime

from backend import db

FIN = ("FT", "AET", "PEN")
# rondas de eliminación directa (inglés de la API y castellano)
_RONDA_KO = re.compile(r"final|semi|quarter|cuartos|octavos|round of|8th|16th|32nd|knockout|play-?offs?\b|"
                       r"preliminary|qualifying|eliminat|1/8|1/4|1/2|repechaje|dieciseisavos", re.I)
# una «fase» de grupos o de liga NO es eliminatoria aunque la ronda tenga número
_RONDA_GRUPOS = re.compile(r"group|grupo|league stage|fase liga|regular season", re.I)


def _q1(sql: str, params: tuple):
    try:
        return db.query_one("sad", sql, params)
    except Exception:  # noqa: BLE001 — base sin la tabla
        return None


def _q(sql: str, params: tuple) -> list:
    try:
        return db.query("sad", sql, params)
    except Exception:  # noqa: BLE001
        return []


def es_eliminatoria(ronda: str | None) -> bool:
    r = ronda or ""
    return bool(_RONDA_KO.search(r)) and not _RONDA_GRUPOS.search(r)


def _g(fila, clave):
    try:
        return fila[clave]
    except (IndexError, KeyError):
        return None


def _penales(f) -> tuple[int, int] | None:
    """(local, visita) de la tanda; None si no hubo o no se sabe."""
    ph, pa = _g(f, "penalty_home"), _g(f, "penalty_away")
    if ph is not None and pa is not None:
        return int(ph), int(pa)
    if (_g(f, "status_short") or "") != "PEN":
        return None
    # la ingesta no trajo la tanda: se cuenta en la ficha, solo los convertidos
    filas = _q("SELECT equipo_id, detalle FROM fixture_eventos WHERE fixture_id=? AND tipo='Shootout'", (f["id"],))
    if not filas:
        return None
    goles = {f["home_team_id"]: 0, f["away_team_id"]: 0}
    for e in filas:
        if (e["detalle"] or "").strip().lower() == "penalty" and e["equipo_id"] in goles:
            goles[e["equipo_id"]] += 1
    return goles[f["home_team_id"]], goles[f["away_team_id"]]


def _goles_totales(f) -> tuple[int, int] | None:
    """Goles con prórroga (`goals_*`); sin ellos, los de 90'."""
    gh = _g(f, "goals_home") if _g(f, "goals_home") is not None else _g(f, "fulltime_home")
    ga = _g(f, "goals_away") if _g(f, "goals_away") is not None else _g(f, "fulltime_away")
    return (int(gh), int(ga)) if gh is not None and ga is not None else None


def _ida(f):
    """El otro partido de la llave: misma liga, temporada y ronda, localía invertida."""
    filas = _q("SELECT * FROM fixtures WHERE league_id=? AND home_team_id=? AND away_team_id=? AND id<>? "
               "AND status_short IN ('FT','AET','PEN') AND date < ?",
               (_g(f, "league_id"), f["away_team_id"], f["home_team_id"], f["id"], str(f["date"])))
    def _dias(x):
        try:
            return (datetime.fromisoformat(str(f["date"])[:19]) - datetime.fromisoformat(str(x["date"])[:19])).days
        except ValueError:
            return 999
    cand = [x for x in filas if _g(x, "league_round") == _g(f, "league_round")
            and _g(x, "league_season") == _g(f, "league_season") and 0 <= _dias(x) <= 45]
    return max(cand, key=lambda x: str(x["date"])) if cand else None


def _vuelta(f) -> bool:
    """¿Hay un partido POSTERIOR de la misma llave (este es la ida)?"""
    return bool(_q("SELECT id FROM fixtures WHERE league_id=? AND home_team_id=? AND away_team_id=? AND id<>? "
                   "AND date > ? AND COALESCE(league_round,'')=? LIMIT 1",
                   (_g(f, "league_id"), f["away_team_id"], f["home_team_id"], f["id"], str(f["date"]),
                    _g(f, "league_round") or "")))


def _final_unica(ronda: str | None) -> bool:
    return (ronda or "").strip().lower() in ("final", "finals", "grand final", "gran final")


def desenlace(fixture_id: int) -> dict | None:
    """La llave que cerró este partido. None si no es de eliminación directa o
    no terminó. `avanza`/`eliminado` son ids de equipo, o None si no se sabe."""
    f = _q1("SELECT f.*, l.name AS liga FROM fixtures f LEFT JOIN leagues l ON l.id=f.league_id "
            "WHERE f.id=?", (fixture_id,))
    if not f or (_g(f, "status_short") or "") not in FIN:
        return None
    pen = _penales(f)
    if not pen and not es_eliminatoria(_g(f, "league_round")):
        return None
    tot = _goles_totales(f)
    if not tot:
        return None
    h, a = f["home_team_id"], f["away_team_id"]
    ida = _ida(f)
    glob = None
    if ida is not None and _goles_totales(ida):
        gi = _goles_totales(ida)          # en la ida, el local de hoy jugó de visita
        glob = (tot[0] + gi[1], tot[1] + gi[0])
    avanza = None
    et = (_g(f, "extratime_home"), _g(f, "extratime_away"))
    if pen and pen[0] != pen[1]:
        avanza = h if pen[0] > pen[1] else a
    elif glob and glob[0] != glob[1]:
        avanza = h if glob[0] > glob[1] else a
    elif ida is None and not _vuelta(f):
        if _g(f, "status_short") == "AET" and None not in et and et[0] != et[1]:
            # la prórroga la decide quien la gana (con ida perdida, el partido entero engaña)
            avanza = h if et[0] > et[1] else a
        elif _final_unica(_g(f, "league_round")) and tot[0] != tot[1]:
            avanza = h if tot[0] > tot[1] else a
    # el partido de IDA no cierra nada, y una ronda que no sabemos si es a uno o
    # dos partidos tampoco se afirma: `avanza` None, nunca adivinado
    return {
        "fixtureId": fixture_id, "competicion": _g(f, "liga") or "", "ronda": _g(f, "league_round") or "",
        "marcador": f"{tot[0]}-{tot[1]}", "prorroga": (_g(f, "status_short") in ("AET", "PEN")),
        "penales": f"{pen[0]}-{pen[1]}" if pen else None,
        "global": f"{glob[0]}-{glob[1]}" if glob else None,
        "ida": ida["id"] if ida is not None else None,
        "avanza": avanza, "eliminado": (a if avanza == h else h) if avanza else None,
    }


def texto_para(d: dict, team_id: int) -> str:
    """«pasa por penales (5-3) tras 2-2 en el global» desde el lado de `team_id`."""
    if not d or not d.get("avanza"):
        return ""
    pasa = d["avanza"] == team_id
    # la tanda y el global, vistos desde este equipo
    def _desde(par: str | None) -> str:
        if not par:
            return ""
        x, y = par.split("-")
        return par if team_id == _local(d) else f"{y}-{x}"
    pen, glob = _desde(d.get("penales")), _desde(d.get("global"))
    verbo = "PASA" if pasa else "ELIMINADO"
    como = (f" por penales ({pen})" if pen else (" en la prórroga" if d.get("prorroga") else ""))
    tras = f" tras {glob} en el global" if glob else ""
    ronda = f" ({d['ronda']})" if d.get("ronda") else ""
    return f"{verbo}{como}{tras}{ronda}"


def _local(d: dict) -> int | None:
    f = _q1("SELECT home_team_id FROM fixtures WHERE id=?", (d["fixtureId"],))
    return f["home_team_id"] if f else None


def recientes(team_id: int, antes: str, dias: int = 30) -> list[dict]:
    """Las llaves cerradas por el equipo en los `dias` anteriores a `antes`
    (sin incluir ese día): lo que un parte puede citar como «eliminado» o
    «clasificado»."""
    try:
        hasta = datetime.fromisoformat(str(antes)[:19])
    except ValueError:
        return []
    from datetime import timedelta
    desde = (hasta - timedelta(days=dias)).strftime("%Y-%m-%d")
    filas = _q("SELECT id FROM fixtures WHERE (home_team_id=? OR away_team_id=?) AND date >= ? AND date < ? "
               "AND status_short IN ('FT','AET','PEN') ORDER BY date",
               (team_id, team_id, desde, hasta.strftime("%Y-%m-%d %H:%M:%S")))
    out = []
    for r in filas:
        d = desenlace(r["id"])
        if d and d.get("avanza"):
            otro = d["eliminado"] if d["avanza"] == team_id else d["avanza"]
            fila = _q1("SELECT name FROM teams WHERE id=?", (otro,))
            out.append({**d, "pasa": d["avanza"] == team_id, "texto": texto_para(d, team_id),
                        "rival": (fila["name"] if fila else "") or ""})
    return out
