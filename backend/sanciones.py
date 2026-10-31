"""LAS SUSPENSIONES QUE SALEN DE LA BASE (30/10/2026, incidencias 772, 778 y 835).

Neymar vio la roja el 25/10 contra el Vasco y el parte del Santos–Palmeiras
del 28/10 lo tenía disponible y primer ejecutor de penales; Bryan Castillo
(Carabobo) se fue expulsado por doble amarilla al 81' y la tabla F1 no lo
decía; Vitor Hugo (Atlético-MG) cumplía la tercera amarilla. Las bajas venían
SOLO de la lista de la API (`/injuries`), que llega tarde o no trae la sanción,
y la ficha del partido anterior —con la tarjeta adentro— estaba en la base sin
que nadie la leyera. Es teoría básica del fútbol: no se espera a que la prensa
la confirme.

Reglas (solo lectura, cero requests; lee `fixtures`, `fixture_eventos` y
`alineaciones` como estén):
- ROJA (directa o doble amarilla) en el ÚLTIMO partido terminado del equipo en
  la MISMA competición y temporada → se pierde ESTE partido, si este es de esa
  competición. Una roja de la liga no suspende en la copa (la regla general).
  La roja directa puede valer más de una fecha: eso no se sabe de la base y
  se dice.
- AMARILLAS ACUMULADAS → solo en las competiciones con la regla conocida
  (`UMBRALES`), con la amarilla que completa el ciclo en el último partido de
  la competición y con los eventos de TODOS sus partidos de la temporada en
  la base (un conteo parcial no afirma nada: viaja como `conteoParcial`). La
  amarilla de un partido en que el mismo jugador vio la roja (doble amarilla)
  no suma al ciclo.
- Un jugador que está en la hoja de ESTE partido (once o banco) no está
  suspendido: la hoja manda sobre la inferencia.
Todo sale con `certeza: probable` y la fuente: es la regla de la competición
aplicada a nuestra base, no un comunicado. La prensa la confirma o la desmiente.
"""
from __future__ import annotations

import re

from backend import db

FIN = ("FT", "AET", "PEN")

# Amarillas que suspenden un partido, por competición (league_id de la API).
# Solo las reglas conocidas; las demás no se infieren (la tabla dice cuántas
# lleva cada uno y la prensa decide). `cada` = múltiplos; `en` = lista fija.
UMBRALES: dict[int, dict] = {
    71: {"cada": 3, "regla": "Brasileirão: cada 3 amarillas"},
    72: {"cada": 3, "regla": "Série B: cada 3 amarillas"},
    140: {"cada": 5, "regla": "LaLiga: cada 5 amarillas"},
    78: {"cada": 5, "regla": "Bundesliga: cada 5 amarillas"},
    128: {"cada": 5, "regla": "Liga Profesional Argentina: cada 5 amarillas"},
    262: {"cada": 5, "regla": "Liga MX: cada 5 amarillas"},
    135: {"en": (5, 10, 14, 17), "regla": "Serie A: a la 5.ª, 10.ª, 14.ª y 17.ª amarilla"},
    39: {"en": (5, 10, 15), "regla": "Premier League: a la 5.ª, 10.ª y 15.ª (con tope de fecha)"},
    2: {"en": (3, 5, 7, 9), "regla": "UEFA: a la 3.ª, 5.ª, 7.ª… amarilla"},
    3: {"en": (3, 5, 7, 9), "regla": "UEFA: a la 3.ª, 5.ª, 7.ª… amarilla"},
    848: {"en": (3, 5, 7, 9), "regla": "UEFA: a la 3.ª, 5.ª, 7.ª… amarilla"},
}

_ROJA = re.compile(r"red card|second yellow|roja", re.I)
_AMARILLA = re.compile(r"^yellow card$|^amarilla$", re.I)


def suspende(liga: int, n: int) -> bool:
    """¿La amarilla número `n` en la competición completa un ciclo?"""
    u = UMBRALES.get(liga)
    if not u or n <= 0:
        return False
    return n % u["cada"] == 0 if "cada" in u else n in u["en"]


def _fase(ronda: str | None) -> str:
    """Apertura y Clausura (o 1st/2nd stage) son torneos aparte: el ciclo de
    amarillas arranca de cero en cada uno."""
    r = (ronda or "").lower()
    for clave in ("apertura", "clausura", "1st", "2nd", "first", "second"):
        if clave in r:
            return clave
    return ""


# LA ROJA QUE SE CUMPLE EN CUALQUIER COMPETICIÓN DOMÉSTICA (incidencia 958,
# Cole Palmer: doble amarilla en la Premier el 24/10, cumplida en la Copa de la
# Liga el 28/10, y la base lo daba suspendido para la Premier siguiente). En
# Inglaterra la suspensión por roja corre sobre los partidos domésticos del
# club, sea la competición que sea: la «misma competición» es el grupo.
ROJA_DOMESTICA = ({39, 40, 41, 42, 45, 48},)


def _grupo_roja(liga: int) -> tuple:
    return next((tuple(sorted(g)) for g in ROJA_DOMESTICA if liga in g), (liga,))


def _previos(team_id: int, liga: int | tuple, temporada, antes: str, fase: str) -> list:
    ligas = liga if isinstance(liga, tuple) else (liga,)
    temp = "" if len(ligas) > 1 else " AND league_season=?"
    filas = db.query(
        "sad", "SELECT id, date, league_round, home_team_id, away_team_id FROM fixtures "
               f"WHERE (home_team_id=? OR away_team_id=?) AND league_id IN ({','.join('?' * len(ligas))}){temp} "
               f"AND status_short IN ({','.join('?' * len(FIN))}) AND date < ? ORDER BY date DESC",
        (team_id, team_id, *ligas, *(() if len(ligas) > 1 else (temporada,)), *FIN, antes))
    return [f for f in filas if len(ligas) > 1 or _fase(f["league_round"]) == fase]


def _tarjetas(fixture_id: int, team_id: int) -> list:
    return db.query(
        "sad", "SELECT minuto, detalle, jugador, jugador_id FROM fixture_eventos "
               "WHERE fixture_id=? AND equipo_id=? AND tipo='Card' ORDER BY minuto", (fixture_id, team_id))


def _tarjetas_de(ids: list[int], team_id: int) -> dict[int, list]:
    """Las tarjetas del equipo en TODOS esos partidos, en UNA consulta (antes
    era una por partido: ~30 por equipo con una temporada en la base)."""
    if not ids:
        return {}
    out: dict[int, list] = {i: [] for i in ids}
    vistos: set = set()
    for r in db.query(
            "sad", f"SELECT fixture_id, minuto, detalle, jugador, jugador_id FROM fixture_eventos "
                   f"WHERE fixture_id IN ({','.join('?' * len(ids))}) AND equipo_id=? AND tipo='Card' "
                   "ORDER BY fixture_id, minuto", (*ids, team_id)):
        # EL MISMO EVENTO DOS VECES NO SON DOS AMARILLAS (incidencia 971, Pathé
        # Ciss con 6 contadas y la 5.ª en la prensa): fixture, minuto, jugador y tipo
        k = (r["fixture_id"], r["minuto"], r["jugador_id"] or (r["jugador"] or "").strip().lower(), r["detalle"])
        if k in vistos:
            continue
        vistos.add(k)
        out.setdefault(r["fixture_id"], []).append(r)
    return out


def _con_eventos(ids: list[int]) -> set[int]:
    if not ids:
        return set()
    return {r["fixture_id"] for r in db.query(
        "sad", f"SELECT DISTINCT fixture_id FROM fixture_eventos WHERE fixture_id IN ({','.join('?' * len(ids))})",
        tuple(ids))}


def _en_la_hoja(fixture_id: int, team_id: int) -> tuple[set, set]:
    try:
        filas = db.query("sad", "SELECT player_id, jugador FROM alineaciones WHERE fixture_id=? AND team_id=?",
                         (fixture_id, team_id))
    except Exception:  # noqa: BLE001 — base sin alineaciones
        return set(), set()
    return ({r["player_id"] for r in filas if r["player_id"]},
            {(r["jugador"] or "").strip().lower() for r in filas if r["jugador"]})


def _clave(t) -> tuple:
    return (t["jugador_id"],) if t["jugador_id"] else ("nombre", (t["jugador"] or "").strip().lower())


def _cuerpo_tecnico(fixture_id: int, team_id: int, rojas: list[dict]) -> set[int]:
    """Las rojas (por `id()`) que la regla de la ficha da al cuerpo técnico."""
    if not rojas:
        return set()
    try:
        from backend.ficha_tactica import _cuerpo_tecnico_e_ids
    except Exception:  # noqa: BLE001 — sin la capa de la ficha, todas siguen siendo de jugadores
        return set()
    ev = [{"equipoId": team_id, "jugador": r["nombre"], "jugadorId": r["jugadorId"], "tipo": "Card", "_r": r}
          for r in rojas]
    try:
        _cuerpo_tecnico_e_ids(fixture_id, ev)
    except Exception:  # noqa: BLE001 — base sin entrenadores ni alineaciones: no se reclasifica
        return set()
    return {id(e["_r"]) for e in ev if e.get("cuerpoTecnico")}


def del_equipo(team_id: int, fx) -> dict:
    """Los sancionados de `team_id` para el partido `fx` (fila de fixtures con
    id, date, league_id, league_season, league_round)."""
    out = {"sancionados": [], "amarillas": [], "conteoParcial": None, "regla": None}
    try:
        fase = _fase(fx["league_round"] if "league_round" in fx.keys() else None)
        previos = _previos(team_id, fx["league_id"], fx["league_season"], str(fx["date"]), fase)
    except Exception:  # noqa: BLE001 — base sin la tabla o sin columnas: no se infiere nada
        return out
    # la roja mira el último partido del GRUPO doméstico (958); las amarillas,
    # la competición. Un primer partido de copa también hereda la roja de la liga
    grupo = _grupo_roja(fx["league_id"])
    previos_r = previos
    if len(grupo) > 1:
        try:
            previos_r = _previos(team_id, grupo, fx["league_season"], str(fx["date"]), fase) or previos
        except Exception:  # noqa: BLE001 — sin el grupo, la regla de la competición
            previos_r = previos
    if not previos_r:
        return out
    ultimo = previos[0] if previos else previos_r[0]
    en_ids, en_nombres = _en_la_hoja(fx["id"], team_id)

    def en_hoja(t) -> bool:
        return (t["jugador_id"] in en_ids) if t["jugador_id"] else ((t["jugador"] or "").strip().lower() in en_nombres)

    ids = [p["id"] for p in previos]
    ultimo_r = previos_r[0]
    try:
        por_partido = _tarjetas_de(sorted({*ids, ultimo_r["id"]}), team_id)
    except Exception:  # noqa: BLE001
        return out
    tarj_ultimo = por_partido.get(ultimo_r["id"]) or []
    rival = ultimo_r["away_team_id"] if ultimo_r["home_team_id"] == team_id else ultimo_r["home_team_id"]
    fecha = str(ultimo_r["date"])[:10]
    rojas = {}
    for t in tarj_ultimo:
        if _ROJA.search(t["detalle"] or "") and not en_hoja(t):
            doble = (re.search(r"second", t["detalle"] or "", re.I)
                     or any(_clave(y) == _clave(t) and _AMARILLA.search(y["detalle"] or "")
                            and (y["minuto"] or 0) <= (t["minuto"] or 0) for y in tarj_ultimo))
            rojas[_clave(t)] = {
                "jugadorId": t["jugador_id"], "nombre": t["jugador"], "tipo": "doble_amarilla" if doble else "roja",
                "partido": ultimo_r["id"], "fecha": fecha, "minuto": t["minuto"], "rivalId": rival,
                "certeza": "probable",
                "detalle": (f"{'doble amarilla' if doble else 'roja directa'} al {t['minuto']}' el {fecha} en el "
                            "último partido de esta competición: se pierde este partido"
                            + ("" if doble else " (una roja directa puede valer más fechas: confirmar en prensa)")),
            }
    # LA ROJA AL DT NO ES DE UN JUGADOR (incidencia 919: Almirón y Peirano, sin
    # id, entraban en `sancionados` y SANCION-SIN-DECLARAR pedía ponerlos en
    # `fuera`, donde pesarían en el IP). La misma regla que la ficha
    # (`ficha_tactica._cuerpo_tecnico_e_ids`): va aparte, para `dt.banco`.
    ct = _cuerpo_tecnico(ultimo["id"], team_id, [rojas[k] for k in rojas])
    for k in list(rojas):
        if id(rojas[k]) in ct:
            r = rojas.pop(k)
            r["tipo"] = "expulsion_dt"
            r["detalle"] = (f"expulsado al {r['minuto']}' el {fecha} en el último partido de esta competición: "
                            "no se sienta en el banco hoy (confirmar la pena en prensa); va en `dt.banco`, "
                            "no en `fuera`")
            out.setdefault("cuerpoTecnico", []).append(r)
    out["sancionados"].extend(rojas.values())

    # AMARILLAS ACUMULADAS: solo con la regla de la competición y el conteo completo
    regla = UMBRALES.get(fx["league_id"])
    out["regla"] = regla["regla"] if regla else None
    if not regla:
        # SIN REGLA SE DICE (incidencia 1011, Ligue 1 y Paraguay: 4 y 5 amarillas
        # sin marca): el conteo viaja, el ciclo no se afirma
        out["sinRegla"] = ("sin la regla de amarillas de esta competición en `sanciones.UMBRALES`: el conteo "
                           "viaja, el ciclo no se afirma (confirmar en prensa)")
    try:
        cubiertos = _con_eventos(ids)
    except Exception:  # noqa: BLE001
        return out
    conteo: dict[tuple, dict] = {}
    for p in previos:
        if p["id"] not in cubiertos:
            continue
        tarj = por_partido.get(p["id"]) or []
        con_roja = {_clave(t) for t in tarj if _ROJA.search(t["detalle"] or "")}
        for t in tarj:
            if _AMARILLA.search(t["detalle"] or "") and _clave(t) not in con_roja:
                c = conteo.setdefault(_clave(t), {"jugadorId": t["jugador_id"], "nombre": t["jugador"], "n": 0,
                                                  "enElUltimo": False})
                c["n"] += 1
                if p["id"] == ultimo["id"]:
                    c["enElUltimo"] = True
    out["amarillas"] = [{"jugadorId": c["jugadorId"], "nombre": c["nombre"], "amarillas": c["n"]}
                        for c in sorted(conteo.values(), key=lambda c: -c["n"])]
    if len(cubiertos) < len(ids):
        out["conteoParcial"] = f"{len(cubiertos)} de {len(ids)} partidos de la competición con eventos en la base"
        return out
    # EN EL UMBRAL SE DICE SI YA CUMPLIÓ (incidencia 1043, Monterrey: I. Tona
    # con 5 amarillas y suspensión cada 5, fuera de `sancionados` y sin nada
    # que dijera por qué): la amarilla del ciclo en un partido ANTERIOR al
    # último de la competición ya se cumplió; en el último, suspende (o la
    # hoja de hoy lo desmiente)
    ciclo = {}
    for k, c in conteo.items():
        if not suspende(fx["league_id"], c["n"]):
            continue
        en_hoja = (c["jugadorId"] in en_ids) if c["jugadorId"] else ((c["nombre"] or "").strip().lower() in en_nombres)
        ciclo[k] = ("cumplido" if not c["enElUltimo"] else "enLaHoja" if en_hoja
                    else "roja" if k in rojas else "suspende")
    for a, (k, c) in zip(out["amarillas"], sorted(conteo.items(), key=lambda kc: -kc[1]["n"])):
        if k in ciclo:
            a["ciclo"] = ciclo[k]
    for k, c in conteo.items():
        if k in rojas or not c["enElUltimo"] or not suspende(fx["league_id"], c["n"]):
            continue
        if (c["jugadorId"] in en_ids) if c["jugadorId"] else ((c["nombre"] or "").strip().lower() in en_nombres):
            continue
        out["sancionados"].append({
            "jugadorId": c["jugadorId"], "nombre": c["nombre"], "tipo": "amarillas", "amarillas": c["n"],
            "partido": ultimo["id"], "fecha": fecha, "rivalId": rival, "certeza": "probable",
            "detalle": f"{c['n']}.ª amarilla el {fecha} ({regla['regla']}): se pierde este partido",
        })
    return out


def de_fixture(fixture_id: int) -> dict:
    """{'a': …, 'b': …} con los sancionados de cada lado para este partido."""
    try:
        fx = db.query_one("sad", "SELECT id, date, league_id, league_season, league_round, home_team_id, "
                                 "away_team_id FROM fixtures WHERE id=?", (fixture_id,))
    except Exception:  # noqa: BLE001
        return {}
    if not fx:
        return {}
    return {"a": del_equipo(fx["home_team_id"], fx), "b": del_equipo(fx["away_team_id"], fx)}
