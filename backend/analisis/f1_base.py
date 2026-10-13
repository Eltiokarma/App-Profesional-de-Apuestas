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

from backend import jugadores as jug
from backend.analisis import bloque_f

CANDIDATOS = 16          # lo que pide el protocolo: 14-16 jugadores
TF_PCT, TH_PCT, ROT_PCT = 0.75, 0.5, 0.25
DECISIVO_PCT = 0.75      # titular habitual: ≥ 75 % de los minutos del que más jugó
DECISIVO_MIN_MINUTOS = 450   # con menos, la temporada recién arranca y el % no dice nada
DECISIVO_GA = 3          # top 3 en goles+asistencias, con al menos esto
_ZONA = {"Portero": "GK", "Defensa": "DEF", "Centrocampista": "MID", "Delantero": "ATK"}


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


def tabla_equipo(team_id: int, nombre: str) -> dict:
    p = jug.plantilla_de(team_id)
    js = p.get("jugadores") or []
    dec = {d["id"]: d["porQue"] for d in decisivos(p)}
    elegidos = js[:CANDIDATOS]                       # ya vienen por minutos
    ids = {j["id"] for j in elegidos}
    elegidos += [j for j in js if j["id"] in dec and j["id"] not in ids]
    return {
        "equipo": nombre, "teamId": team_id, "temporada": p.get("temporada"),
        "origenTemporada": p.get("origenTemporada"),
        "candidatos": [{**_fila(j), "decisivo": dec.get(j["id"], "")} for j in elegidos],
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
        "a": tabla_equipo(fx["home_team_id"], fx["home_name"]),
        "b": tabla_equipo(fx["away_team_id"], fx["away_name"]),
        "nota": ("punto de partida de la tabla F1, calculado de la temporada ingestada: copiá el "
                 "`jugadorId` (es el cruce exacto con la hoja del partido) y confirmá el rol con la "
                 "prensa —`rolSugerido` sale solo de los minutos y no sabe de un DT nuevo ni de una "
                 "lesión larga—. Los `decisivo` no pueden faltar: si faltan, el parte avisa "
                 "F1-DECISIVO-FUERA"),
    }


def _en_tabla(j: dict, plantel: list[dict]) -> bool:
    for p in plantel:
        if p.get("jugadorId") and int(p["jugadorId"]) == int(j["id"]):
            return True
    tok_api = bloque_f._tokens(j["nombre"])
    return any(bloque_f._casa(bloque_f._tokens(p.get("nombre") or ""), tok_api)
               or bloque_f._casa(tok_api, bloque_f._tokens(p.get("nombre") or ""))
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
