"""La tabla F1 del EFE armada desde la base (`GET /analisis/cowork/f1/{id}`).

POR QUÉ. En la autopsia del 11/10/2026 (`docs/autopsias/2026-10-11.md`) al
menos 14 jugadores decisivos —goleadores, el arquero titular, el lateral que
jugaba todo— no estaban en la tabla F1 de ningún parte: la tabla se armaba con
la previa de la prensa, que nombra a los famosos y a los lesionados, no a los
que juegan. Un jugador que no está en la tabla F1 no pesa en el Impacto
Ponderado (`docs/COWORK.md`), así que su baja no existía para el bloque F.

QUÉ HACE. Dos cosas, las dos calculadas de la plantilla ingestada (minutos,
titularidades, goles y asistencias de la temporada; 0 requests):

- `tabla(fixture_id)`: por lado, los candidatos a la tabla F1 con su
  `jugadorId` —el cruce exacto con la hoja del partido—, la zona y un ROL
  SUGERIDO por la fracción de minutos. Es un punto de partida: el rol es del
  skill y lo confirma la prensa (un DT nuevo, una lesión larga), por eso viaja
  como `rolSugerido` y no se escribe solo en el parte.
- `alertas(parte, fx, nombres)`: `F1-DECISIVO-FUERA` (tipo `dato`) cuando un
  decisivo de la base no figura en la tabla F1 depositada. Se calcula al leer.
"""
from __future__ import annotations

from backend import db as saddb
from backend import jugadores as jug
from backend.analisis import bloque_f

CANDIDATOS = 16          # lo que pide el protocolo: 14-16 jugadores
TF_PCT, TH_PCT, ROT_PCT = 0.75, 0.5, 0.25
DECISIVO_PCT = 0.75      # titular habitual: ≥ 75 % de los minutos del que más jugó
DECISIVO_MIN_MINUTOS = 450   # con menos, la temporada recién arranca y el % no dice nada
DECISIVO_GA = 3          # top 3 en goles+asistencias, con al menos esto
_ZONA = {"Portero": "GK", "Defensa": "DEF", "Centrocampista": "MID", "Delantero": "ATK"}
_ZONA_API = {"G": "GK", "D": "DEF", "M": "MID", "F": "ATK"}
ONCES_RECIENTES = 10     # onces que se miran para el rol
ONCES_MINIMOS = 5        # con menos, el rol sale de los minutos de la temporada
_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished')"


def onces_recientes(team_id: int, antes: str) -> dict:
    """Titularidades en los últimos ONCES_RECIENTES partidos terminados con
    alineación, estrictamente antes de `antes`.

    POR QUÉ. Las stats de la plantilla son de la TEMPORADA, y en Sudamérica la
    temporada es el año: el rol de Millonarios del Clausura salía mezclado con
    el del Apertura (corrida del 13/10/2026). Lo que el once de hoy va a ser
    se parece más a los últimos diez onces que al año."""
    try:
        fx = [r["id"] for r in saddb.query(
            "sad", f"""SELECT f.id FROM fixtures f
                       WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.date < ? AND {_FIN}
                         AND EXISTS (SELECT 1 FROM alineaciones a WHERE a.fixture_id=f.id AND a.team_id=?)
                       ORDER BY f.date DESC LIMIT ?""", (team_id, team_id, antes, team_id, ONCES_RECIENTES))]
        if not fx:
            return {"onces": 0, "jugadores": {}}
        filas = saddb.query(
            "sad", f"SELECT player_id, jugador, posicion, titular FROM alineaciones "
                   f"WHERE team_id=? AND fixture_id IN ({','.join('?' * len(fx))})", (team_id, *fx))
    except Exception:  # noqa: BLE001 — base sin la tabla de alineaciones
        return {"onces": 0, "jugadores": {}}
    js: dict[int, dict] = {}
    for f in filas:
        j = js.setdefault(f["player_id"], {"nombre": f["jugador"] or "", "posicion": f["posicion"] or "",
                                           "titular": 0, "convocado": 0})
        j["convocado"] += 1
        j["titular"] += 1 if f["titular"] else 0
    return {"onces": len(fx), "jugadores": js}


def rol_por_onces(titular: int, onces: int) -> str:
    frac = titular / onces if onces else 0
    return "TF" if frac >= 0.8 else "TH" if frac >= 0.5 else "ROT" if frac >= 0.2 else "SUP"


def rol_sugerido(pct_minutos: float) -> str:
    if pct_minutos >= TF_PCT:
        return "TF"
    if pct_minutos >= TH_PCT:
        return "TH"
    if pct_minutos >= ROT_PCT:
        return "ROT"
    return "SUP"


def decisivos(plantilla: dict) -> list[dict]:
    """Los que no pueden faltar en la tabla F1: titulares habituales y los
    tres que más goles generan. Cada uno con su porqué."""
    js = plantilla.get("jugadores") or []
    fuera: dict[int, dict] = {}
    for j in js:
        if j["minutos"] >= DECISIVO_MIN_MINUTOS and j["pctMinutos"] >= DECISIVO_PCT:
            fuera[j["id"]] = {**j, "porQue": f"titular habitual ({round(j['pctMinutos'] * 100)} % de los minutos)"}
    ofensivos = sorted((j for j in js if j["goles"] + j["asistencias"] >= DECISIVO_GA),
                       key=lambda j: -(j["goles"] + j["asistencias"]))[:3]
    for j in ofensivos:
        motivo = f"{j['goles']} goles y {j['asistencias']} asistencias"
        if j["id"] in fuera:
            fuera[j["id"]]["porQue"] += f" · {motivo}"
        else:
            fuera[j["id"]] = {**j, "porQue": motivo}
    return list(fuera.values())


def _fila(j: dict) -> dict:
    return {
        "jugadorId": j["id"], "nombre": j["nombre"], "zona": _ZONA.get(j["posicion"], ""),
        "posicion": j["posicion"], "rolSugerido": rol_sugerido(j["pctMinutos"]),
        "apps": j["partidos"], "titularidades": j["titularidades"], "minutos": j["minutos"],
        "pctMinutos": j["pctMinutos"], "goles": j["goles"], "asistencias": j["asistencias"],
        "baja": j.get("baja"), "recienLlegado": j.get("recienLlegado"),
    }


def tabla_equipo(team_id: int, nombre: str, antes: str = "9999") -> dict:
    p = jug.plantilla_de(team_id)
    js = p.get("jugadores") or []
    dec = {d["id"]: d["porQue"] for d in decisivos(p)}
    rec = onces_recientes(team_id, antes)
    con_onces = rec["onces"] >= ONCES_MINIMOS
    tit = {pid: j["titular"] for pid, j in rec["jugadores"].items()}
    # con onces recientes, el orden y el rol salen de ahí; la temporada desempata
    if con_onces:
        js = sorted(js, key=lambda j: (-tit.get(j["id"], 0), -j["minutos"]))
    elegidos = js[:CANDIDATOS]
    ids = {j["id"] for j in elegidos}
    elegidos += [j for j in js if j["id"] in dec and j["id"] not in ids]
    filas = []
    for j in elegidos:
        f = {**_fila(j), "decisivo": dec.get(j["id"], "")}
        if con_onces:
            f["titularEnUltimos"] = f"{tit.get(j['id'], 0)}/{rec['onces']}"
            f["rolSugerido"] = rol_por_onces(tit.get(j["id"], 0), rec["onces"])
        filas.append(f)
    # titulares recientes que la plantilla de la temporada no tiene (fichajes,
    # juveniles subidos): sin ellos la tabla se queda con el equipo de antes
    ids = {j["id"] for j in elegidos}
    if con_onces:
        for pid, r in sorted(rec["jugadores"].items(), key=lambda kv: -kv[1]["titular"]):
            if pid in ids or pid <= 0 or r["titular"] < 2:
                continue
            filas.append({"jugadorId": pid, "nombre": r["nombre"], "zona": _ZONA_API.get(r["posicion"], ""),
                          "posicion": r["posicion"], "rolSugerido": rol_por_onces(r["titular"], rec["onces"]),
                          "titularEnUltimos": f"{r['titular']}/{rec['onces']}", "apps": None, "minutos": None,
                          "decisivo": "", "sinStatsDeTemporada": True})
    return {
        "equipo": nombre, "teamId": team_id, "temporada": p.get("temporada"),
        "origenTemporada": p.get("origenTemporada"),
        "rolPor": (f"titularidades en los últimos {rec['onces']} onces" if con_onces else
                   f"minutos de la temporada (solo {rec['onces']} onces recientes en la base)"),
        "candidatos": filas,
        # los que la API lista sin un minuto (recién llegados): la prensa dirá
        "plantelSinStats": p.get("plantelSinStats") or [],
        "sinDato": "" if js else "sin plantilla ingestada para este equipo: la tabla sale de la prensa",
    }


def tabla(fixture_id: int) -> dict | None:
    from backend.analisis.parte import _fixture
    fx = _fixture(fixture_id)
    if not fx:
        return None
    return {
        "fixtureId": fixture_id,
        "a": tabla_equipo(fx["home_team_id"], fx["home_name"], fx["date"]),
        "b": tabla_equipo(fx["away_team_id"], fx["away_name"], fx["date"]),
        "nota": ("punto de partida de la tabla F1, calculado de la temporada ingestada: copiá el "
                 "`jugadorId` (es el cruce exacto con la hoja del partido) y confirmá el rol con la "
                 "prensa —`rolSugerido` sale de los últimos onces (o de los minutos, ver `rolPor`) y no sabe de un DT nuevo ni de una "
                 "lesión larga—. Los `decisivo` no pueden faltar: si faltan, el parte avisa "
                 "F1-DECISIVO-FUERA"),
    }


def _casi_igual(uno: str, otro: str) -> bool:
    """El mismo apellido mal escrito: una letra cambiada, puesta de más o de
    menos, o las mismas letras en otro orden. La API tiene a Huracán con «Juan
    Bizans» (406291) y la hoja del partido con «F. Bisanz» (304389): el mismo
    jugador con dos ids (16/10/2026). Solo apellidos de 5 letras o más: en uno
    corto una letra ya es otra persona."""
    if min(len(uno), len(otro)) < 5 or abs(len(uno) - len(otro)) > 1:
        return False
    if sorted(uno) == sorted(otro):
        return True
    if len(uno) == len(otro):
        return sum(a != b for a, b in zip(uno, otro)) <= 1
    corto, largo = sorted((uno, otro), key=len)
    return any(largo[:i] + largo[i + 1:] == corto for i in range(len(largo)))


def _parecido(tok_api: list[str], tok_tabla: list[str]) -> bool:
    """Último recurso, solo para AVISAR que falta alguien: la misma pila (o su
    inicial) y un apellido casi igual. Un falso «está» cuesta un aviso de
    menos; un falso «no está» manda a rehacer una tabla que estaba bien."""
    if len(tok_api) < 2 or len(tok_tabla) < 2:
        return False
    if not bloque_f._misma_pila(tok_api[0], tok_tabla[0]):
        return False
    return any(_casi_igual(a, t) for a in tok_api[1:] for t in tok_tabla[1:])


def _en_tabla(j: dict, plantel: list[dict]) -> bool:
    for p in plantel:
        if p.get("jugadorId") and int(p["jugadorId"]) == int(j["id"]):
            return True
    tok_api = bloque_f._tokens(j["nombre"])
    return any(bloque_f._casa(bloque_f._tokens(p.get("nombre") or ""), tok_api)
               or bloque_f._casa(tok_api, bloque_f._tokens(p.get("nombre") or ""))
               or _parecido(tok_api, bloque_f._tokens(p.get("nombre") or ""))
               for p in plantel)


def faltantes(team_id: int, plantel: list[dict]) -> list[dict]:
    if not plantel:
        return []          # sin tabla F1 no hay nada que comparar (ya lo dice el bloque F)
    return [{"jugadorId": d["id"], "nombre": d["nombre"], "porQue": d["porQue"]}
            for d in decisivos(jug.plantilla_de(team_id)) if not _en_tabla(d, plantel)]


def alertas(parte: dict, fx, nombres: dict) -> list[dict]:
    if not fx:
        return []
    fuera = []
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        try:
            faltan = faltantes(tid, ((parte.get("equipos") or {}).get(lado) or {}).get("plantel") or [])
        except Exception:  # noqa: BLE001 — base sin la capa de jugadores
            faltan = []
        if faltan:
            fuera.append({
                "codigo": "F1-DECISIVO-FUERA", "equipo": lado, "tipo": "dato",
                "detalle": f"La tabla F1 de {nombres.get(lado, lado)} no tiene a "
                           + "; ".join(f"{f['nombre']} ({f['porQue']})" for f in faltan)
                           + ". Un jugador fuera de la tabla no pesa en el Impacto Ponderado: si no "
                             "juega, su baja no existe para el bloque F. La tabla con `jugadorId` "
                             "sale de GET /analisis/cowork/f1/{id}.",
            })
    return fuera
