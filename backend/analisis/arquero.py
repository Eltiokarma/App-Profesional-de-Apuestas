"""El arquero antes del pitazo: lo que la base ya sabe, calculado (0 requests).

POR QUÉ. En los 43 estudios de reventones (Perú y 13 ligas más, 13-14/10/2026)
el arquero —propio o rival— apareció como mecanismo en 10: Valles (Betis) y
Karius (Schalke) sosteniendo el resultado, Medina (Cajamarca) el 0-0, Bacchia
(Progreso) cortando 5 derrotas, Carlos Miguel (Palmeiras) y Marquínez
(Nacional, suplente) regalando el gol. Ningún skill tiene un casillero para eso:
el TDE mira la estructura, el EFE la continuidad (B6), no la FORMA del arquero.
Antes de escribir una regla hace falta el dato, y parte del dato está en casa:

- quién ataja hoy (alineación oficial, ~60 min antes) y si es el HABITUAL;
- goles recibidos contra el xG del rival en sus últimos partidos: un arquero
  que recibe menos de lo que le patean está sosteniendo; uno que recibe más,
  regalando. Es una aproximación (el xG no mide la calidad del remate al arco
  ni los rebotes), con su `n`: sin xG en la liga, `sinDato`.
- atajadas por partido (`Goalkeeper Saves`) cuando la ficha las trae.

Es DATO, no regla: no hay umbral ni señal de forma hasta que los estudios lo
pidan con casos. La única señal calculada es objetiva: `arquero_suplente`
(el titular de hoy no es el que más atajó en los últimos partidos).
"""
from __future__ import annotations

from collections import Counter

from backend import db as saddb

VENTANA = 10
MUESTRA_MINIMA = 5   # con menos partidos con xG, una goleada domina el número (Casa Pia: el 0-7 con Benfica)
_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished')"



def goles_prevenidos_del_equipo(filas: list, team_id: int) -> float | None:
    """`goals_prevented` de la API para ESTE equipo, o None si no es suyo.
    La API lo trae a veces IGUAL para los dos lados del mismo partido
    (incidencia 565: La Louvière–Zulte −1,31/−1,31 con un arco en cero y el
    otro con tres goles; también 1558661, 1558653, 1558658): un valor que no
    se reparte por equipo no mide a ningún arquero y se descarta."""
    propio = next((_num(s["valor"]) for s in filas if s["clave"] == "goals_prevented" and s["team_id"] == team_id), None)
    ajeno = next((_num(s["valor"]) for s in filas if s["clave"] == "goals_prevented" and s["team_id"] != team_id), None)
    if propio is None or (ajeno is not None and abs(propio - ajeno) < 1e-9):
        return None
    return propio

def _num(v):
    try:
        return float(str(v).replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def titular_de(fixture_id: int, team_id: int) -> dict | None:
    try:
        f = saddb.query_one("sad", "SELECT player_id, jugador FROM alineaciones WHERE fixture_id=? AND team_id=? "
                                   "AND titular=1 AND posicion='G' LIMIT 1", (fixture_id, team_id))
    except Exception:  # noqa: BLE001 — base sin alineaciones
        return None
    return {"id": f["player_id"], "nombre": f["jugador"]} if f else None


def perfil(team_id: int, antes: str, fixture_id: int | None = None) -> dict:
    """El arquero del equipo con la historia cortada ESTRICTAMENTE antes de
    `antes` (anti-hindsight). Con `fixture_id`, el titular de ese partido."""
    try:
        fxs = saddb.query(
            "sad", f"""SELECT f.id, f.home_team_id, f.goals_home, f.goals_away, f.league_id FROM fixtures f
                       WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.date < ? AND {_FIN}
                       ORDER BY f.date DESC LIMIT ?""", (team_id, team_id, antes, VENTANA))
    except Exception:  # noqa: BLE001
        return {"sinDato": "sin partidos en la base"}
    if not fxs:
        return {"sinDato": "sin partidos terminados antes de esta fecha"}
    ids = [f["id"] for f in fxs]
    marcas = ",".join("?" * len(ids))
    try:
        gks = saddb.query("sad", f"SELECT fixture_id, player_id, jugador FROM alineaciones WHERE team_id=? "
                                 f"AND titular=1 AND posicion='G' AND fixture_id IN ({marcas})", (team_id, *ids))
        stats = saddb.query("sad", f"SELECT fixture_id, team_id, clave, valor FROM fixture_stats WHERE fixture_id "
                                   f"IN ({marcas}) AND clave IN ('expected_goals','Goalkeeper Saves','goals_prevented')", tuple(ids))
    except Exception:  # noqa: BLE001
        gks, stats = [], []
    cuenta = Counter((g["player_id"], g["jugador"]) for g in gks)
    habitual = cuenta.most_common(1)[0] if cuenta else None
    # un arquero por competición (Ajax: Paes en Europa, ter Stegen en la liga):
    # con 2+ onces de la competición de este partido, el habitual sale de ahí
    habitual_por = "todas las competiciones"
    if fixture_id is not None:
        try:
            liga = (saddb.query_one("sad", "SELECT league_id FROM fixtures WHERE id=?", (fixture_id,)) or {})["league_id"]
        except Exception:  # noqa: BLE001
            liga = None
        misma = {f["id"] for f in fxs if f["league_id"] == liga}
        c_liga = Counter((g["player_id"], g["jugador"]) for g in gks if g["fixture_id"] in misma)
        if sum(c_liga.values()) >= 2:
            habitual = c_liga.most_common(1)[0]
            habitual_por = "esta competición"
    recibidos, xg_contra, atajadas, n_xg, n_at = 0, 0.0, 0.0, 0, 0
    prevenidos, n_prev = 0.0, 0
    detalle = []
    por_fx = {}
    for s in stats:
        por_fx.setdefault(s["fixture_id"], []).append(s)
    for f in fxs:
        local = f["home_team_id"] == team_id
        ga = (f["goals_away"] if local else f["goals_home"]) or 0
        filas = por_fx.get(f["id"], [])
        xg = next((_num(s["valor"]) for s in filas if s["clave"] == "expected_goals" and s["team_id"] != team_id), None)
        at = next((_num(s["valor"]) for s in filas if s["clave"] == "Goalkeeper Saves" and s["team_id"] == team_id), None)
        gp = goles_prevenidos_del_equipo(filas, team_id)
        if gp is not None:
            prevenidos += gp
            n_prev += 1
        if xg is not None:
            detalle.append({"fixtureId": f["id"], "recibidos": ga, "xgContra": round(xg, 2),
                            "evitados": round(xg - ga, 2)})
            recibidos += ga
            xg_contra += xg
            n_xg += 1
        if at is not None:
            atajadas += at
            n_at += 1
    out = {
        "partidos": len(fxs),
        "habitual": ({"id": habitual[0][0], "nombre": habitual[0][1], "titularEn": habitual[1],
                      "onces": len({g["fixture_id"] for g in gks}), "por": habitual_por} if habitual else None),
        "golesVsXg": ({"recibidos": recibidos, "xgContra": round(xg_contra, 2),
                       "evitados": round(xg_contra - recibidos, 2), "n": n_xg,
                       "muestraCorta": n_xg < MUESTRA_MINIMA,
                       # partido a partido: que una goleada no se esconda en el total
                       "porPartido": detalle} if n_xg else None),
        "atajadasPorPartido": round(atajadas / n_at, 2) if n_at else None,
        "nAtajadas": n_at,
        # el «goals prevented» de la API (post-shot xG − goles), cuando la liga lo trae: mejor que el xG a secas
        "golesPrevenidosApi": ({"total": round(prevenidos, 2), "n": n_prev} if n_prev else None),
        "nota": ("`evitados` = xG en contra − goles recibidos en los partidos con xG: positivo, el arco "
                 "sostuvo más de lo que le patearon; negativo, recibió de más. Aproximación con su n"),
    }
    if fixture_id is not None:
        hoy = titular_de(fixture_id, team_id)
        out["hoy"] = hoy
        out["suplente"] = (None if not hoy or not habitual else hoy["id"] != habitual[0][0])
        if out["suplente"]:
            # el suplente con SUS números: el perfil del titular no le corresponde (Vroman, OH Leuven)
            suyos = {g["fixture_id"] for g in gks if g["player_id"] == hoy["id"]}
            pp = [d for d in detalle if d["fixtureId"] in suyos]
            out["hoyPerfil"] = {"titularEn": len(suyos),
                                "evitados": round(sum(d["evitados"] for d in pp), 2) if pp else None,
                                "nXg": len(pp)}
    return out
