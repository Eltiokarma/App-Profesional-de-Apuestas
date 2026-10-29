"""El DTP (skill `diagnostico-tactico`) por el camino de Cowork.

Dos piezas, con la misma regla que el TDE: **lo que está en nuestra base se
calcula; lo que es juicio lo escribe quien analiza, estructurado.**

1. `ficha(fixture_id)` — los insumos que salen de la ficha de partido ya
   ingestada (`GET /analisis/cowork/dtp/{id}`): el partido anterior de cada
   equipo (marcador, goles con minuto/autor/asistente, posesión con el
   marcador que la produjo), el XI de referencia con sus carriles, qué cambió
   contra el XI anterior, qué parejas de la misma línea nunca arrancaron
   juntas, los días de descanso, si es primera fecha y —lo que hace girar la
   cadena rodante— la APERTURA que se declaró antes de ese partido anterior,
   para que el cierre se valide contra ella y no contra la memoria.

2. `normalizar_dtp(x, rechazos)` / `leer_dtp(dtp)` — el DTP estructurado del
   parte, UN bloque por equipo foco (como el TDE). Cowork responde las seis
   preguntas del checklist de clasificación del bloque rival; la CLASE
   (improvisado · estructural · estructural no probado · ambiguo) y la vida
   útil las calcula `clasificar_bloque`, con la regla del skill v1.2. Antes el
   DTP era un documento en prosa más una frase: la pizarra salía vacía, la
   cadena no tenía qué cerrar y la clase del bloque no llegaba al TDE.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timedelta
from itertools import combinations

from backend import db as saddb

LADOS = ("a", "b")
_FIN = "(status_short IN ('FT','AET','PEN') OR status_long='Match Finished')"
FICHAS_PAREJAS = 5          # onces capturados que se miran para «≤ 1 vez juntos» (EFE v1.7)
PARTIDOS_PAREJAS = 15       # hasta cuántos partidos atrás se buscan esos onces
ONCES_PAREJAS_MIN = 3       # con menos onces con hoja, «≤ 1 vez juntos» no dice nada
TRAMOS = ("0-25", "25-65", "65-80+")
VIAS = ("pelota_parada", "transicion", "juego_abierto")
NIVELES_RESP = ("principal", "secundario", "estructural")

# ── 1 · insumos calculados ───────────────────────────────────────────────────


def _fixture(fixture_id: int):
    return saddb.query_one(
        "sad",
        "SELECT f.id, f.date, f.league_id, f.league_round, f.home_team_id, f.away_team_id, "
        "ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
        "JOIN teams at ON at.id=f.away_team_id WHERE f.id=?",
        (fixture_id,),
    )


def _anteriores(team_id: int, fecha: str, cuantos: int) -> list:
    return saddb.query(
        "sad",
        f"""SELECT f.id, f.date, f.league_id, f.league_round, f.home_team_id, f.away_team_id,
                   COALESCE(f.fulltime_home, f.goals_home) AS gh,
                   COALESCE(f.fulltime_away, f.goals_away) AS ga,
                   ht.name AS home_name, at.name AS away_name, l.name AS liga
            FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id
            JOIN teams at ON at.id=f.away_team_id
            LEFT JOIN leagues l ON l.id=f.league_id
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.date < ? AND {_FIN}
            ORDER BY f.date DESC LIMIT ?""",
        (team_id, team_id, fecha, cuantos),
    )


def _dias(a: str, b: str) -> int | None:
    try:
        return (datetime.strptime(str(a)[:10], "%Y-%m-%d") - datetime.strptime(str(b)[:10], "%Y-%m-%d")).days
    except ValueError:
        return None


def _titulares(fixture_id: int, team_id: int) -> list[dict]:
    try:
        from backend.nombres import limpiar_nombre
        return [{**dict(f), "jugador": limpiar_nombre(f["jugador"])} for f in saddb.query(
            "sad", "SELECT player_id, jugador, posicion, grid FROM alineaciones "
                   "WHERE fixture_id=? AND team_id=? AND titular=1", (fixture_id, team_id))]
    except Exception:  # noqa: BLE001 — DB anterior a la fase A del DTP
        return []


def _banca(fixture_id: int, team_id: int) -> list[str]:
    try:
        from backend.nombres import limpiar_nombre
        return [limpiar_nombre(f["jugador"]) or "" for f in saddb.query(
            "sad", "SELECT jugador FROM alineaciones WHERE fixture_id=? AND team_id=? AND titular=0",
            (fixture_id, team_id))]
    except Exception:  # noqa: BLE001
        return []


def _goles(tac: dict, team_id: int) -> list[dict]:
    """Los goles del partido con el lado que los recibió. Solo `Goal` (la tanda
    de penales va como `Shootout`) y sin los penales errados."""
    out = []
    for e in tac.get("eventos") or []:
        if (e.get("tipo") or "") != "Goal" or "Missed" in (e.get("detalle") or ""):
            continue
        out.append({"minuto": e.get("minuto"), "extra": e.get("extra") or 0,
                    "aFavor": e.get("equipoId") == team_id, "autor": e.get("jugador") or "",
                    "asistente": e.get("asistente") or "", "detalle": e.get("detalle") or ""})
    return out


def _estado_por_tiempo(goles: list[dict]) -> dict:
    """Minutos jugados ganando / empatando / perdiendo, desde los minutos de
    gol. Es lo que la regla de posesión condicional (skill v1.2) pide declarar
    junto al porcentaje: el marcador que lo produjo."""
    t, dif, acc = 0, 0, {"ganando": 0, "empatando": 0, "perdiendo": 0}
    for g in sorted(goles, key=lambda g: (g["minuto"] or 0, g["extra"] or 0)):
        m = min(max(int(g["minuto"] or 0), t), 90)
        acc["ganando" if dif > 0 else "perdiendo" if dif < 0 else "empatando"] += m - t
        t, dif = m, dif + (1 if g["aFavor"] else -1)
    acc["ganando" if dif > 0 else "perdiendo" if dif < 0 else "empatando"] += 90 - t
    dominante = max(acc, key=acc.get)
    return {**acc, "dominante": dominante}


def _stat(st: dict, *claves) -> str:
    for c in claves:
        if st.get(c) not in (None, ""):
            return str(st[c])
    return ""


# EJE-DEBUTANTE del EFE v1.7 (25/10/2026): la pareja que arrancó junta UNA vez
# también es nueva (Mainz: los dos penales de la pareja con un partido junta;
# Bolívar: línea de fondo con un partido). Antes era «nunca juntos».
PAREJA_MAX_JUNTOS = 1


def parejas_nuevas_de(xi: list[dict], previos: list[set]) -> list[dict]:
    """Parejas de la misma línea del XI que arrancaron juntas ≤ PAREJA_MAX_JUNTOS
    veces en los onces previos (cada uno, el conjunto de ids titulares)."""
    if not previos:
        return []
    out = []
    for linea in ("D", "M"):
        de_linea = [j for j in xi if (j.get("posicion") or "") == linea and j.get("jugadorId")]
        for x, y in combinations(de_linea, 2):
            juntos = sum(1 for p in previos if x["jugadorId"] in p and y["jugadorId"] in p)
            if juntos <= PAREJA_MAX_JUNTOS:
                out.append({"linea": "defensa" if linea == "D" else "medio",
                            "jugadores": [x["nombre"], y["nombre"]], "vecesJuntos": juntos})
    return out


def _parejas_nuevas(team_id: int, fecha: str, xi: list[dict]) -> list[dict]:
    """Parejas de la MISMA línea del XI de referencia con ≤ 1 titularidad juntas
    en los onces capturados antes (minutos compartidos; el `EJE-DEBUTANTE` del
    EFE v1.7). Es un proxy: mira titularidades en las fichas que hay, no minutos.

    EL ÚLTIMO ONCE CUENTA: el XI de referencia ES ese once, así que la pareja
    ya arrancó junta ahí. Saltarlo daba «0 juntos» a la que debutó en él
    (Barracas, Taborda–Rolón en 1493195, incidencia 623) y marcaba como nueva
    a la que tenía DOS partidos juntos, contra el «≤ 1» del EFE v1.7."""
    # LOS ONCES QUE HAY, NO LOS PARTIDOS (incidencia 777, Carabobo y La Guaira:
    # de los últimos 5 partidos solo uno tenía hoja —la liga venezolana publica
    # pocas— y cada pareja de titulares fijos salía «1 vez juntos», un
    # EJE-DEBUTANTE falso). Se buscan FICHAS_PAREJAS onces con hoja entre los
    # últimos PARTIDOS_PAREJAS; con menos de ONCES_PAREJAS_MIN no se juzga.
    previos = []
    for f in _anteriores(team_id, fecha, PARTIDOS_PAREJAS):
        ids = {j["player_id"] for j in _titulares(f["id"], team_id) if j["player_id"]}
        if ids:
            previos.append(ids)
        if len(previos) >= FICHAS_PAREJAS:
            break
    if len(previos) < ONCES_PAREJAS_MIN:
        return []
    return parejas_nuevas_de(xi, previos)


def _apertura_previa(nombre: str, fixture_id: int) -> dict | None:
    from backend.analisis import db as efedb
    e = efedb.eslabon_de_fixture(nombre, fixture_id)
    if not e:
        return None
    reg = e.get("registro") or {}
    return {"pronosticoClave": reg.get("pronostico_clave", ""), "apertura": e.get("apertura"),
            "veredicto": reg.get("veredicto", ""), "leccion": reg.get("leccion", "")}


def _primera_fecha(fx) -> bool:
    ronda = str(fx["league_round"] or "")
    return ronda.rstrip().endswith("- 1") or ronda.strip() in ("1", "Round 1", "Matchday 1")


def goles_cuadran(goles: list[dict], gf, gc) -> bool:
    """¿Los eventos de gol dan el marcador de los 90'? El marcador es el de
    `fulltime`, así que los goles de la prórroga (minuto pasado el 90 sin ser
    añadido: 102' de Keita en Mons) no cuentan: Charleroi 0-0 a los 90 salía
    «no cuadran» (incidencia 458; también Alverca y Arouca, 488)."""
    if gf is None or gc is None:
        return False
    en_90 = [g for g in goles if (g.get("minuto") or 0) - (g.get("extra") or 0) <= 90]
    return sum(1 for g in en_90 if g["aFavor"]) == gf and sum(1 for g in en_90 if not g["aFavor"]) == gc


def insumos_equipo(team_id: int, nombre: str, fx) -> dict:
    from backend.ficha_tactica import tactica_de

    fecha = str(fx["date"])
    ants = _anteriores(team_id, fecha, 2)
    faltan = []
    base = {"equipoId": team_id, "equipo": nombre, "primeraFecha": _primera_fecha(fx)}
    if not ants:
        return {**base, "partidoAnterior": None, "aperturaPrevia": None, "nivelDeDato": "C",
                "faltan": ["sin partido anterior terminado en la base: el DTP abre sin CIERRE "
                           "(«Sin partido anterior en la cadena»)"]}
    a = ants[0]
    local = a["home_team_id"] == team_id
    rival = a["away_name"] if local else a["home_name"]
    gf, gc = (a["gh"], a["ga"]) if local else (a["ga"], a["gh"])
    tac = tactica_de(a["id"], a["home_team_id"], a["away_team_id"])
    ali = (tac.get("alineaciones") or {}).get("local" if local else "visitante") or {}
    xi = ali.get("titulares") or []
    goles = _goles(tac, team_id)
    st = ((tac.get("estadisticas") or {}).get("local" if local else "visitante")) or {}
    st_r = ((tac.get("estadisticas") or {}).get("visitante" if local else "local")) or {}
    recibidos = [g for g in goles if not g["aFavor"]]
    cuadran = goles_cuadran(goles, gf, gc)
    if not xi:
        faltan.append("sin alineación capturada del partido anterior: M1 sin XI de referencia "
                      "(`ficha_partido` no la trajo o la liga no da onces)")
    if not goles and (gf or gc):
        faltan.append("hay goles en el marcador pero no eventos: M4 sin minutos ni autores")
    elif goles and not cuadran:
        faltan.append("los eventos de gol no cuadran con el marcador (autogoles mal acreditados "
                      "o eventos incompletos): contrastar con la prensa antes de la autopsia")

    anterior = {
        "fixtureId": a["id"], "fecha": str(a["date"])[:10], "rival": rival,
        "condicion": "L" if local else "V", "competicion": a["liga"] or "",
        "amistoso": "friendl" in (a["liga"] or "").lower(),
        "marcador": {"favor": gf, "contra": gc},
        "goles": goles, "golesCuadran": cuadran,
        "estadoPorTiempo": _estado_por_tiempo(goles) if cuadran else None,
        "posesion": {"valor": _stat(st, "Ball Possession"), "rival": rival,
                     "marcadorFinal": f"{gf}-{gc}",
                     "nota": "regla de posesión condicional (v1.2): el porcentaje vale contra "
                             "ESTE rival y con ESTE marcador; no se importa como rasgo del equipo"},
        "stats": {"tiros": _stat(st, "Total Shots"), "tirosAlArco": _stat(st, "Shots on Goal"),
                  "xg": _stat(st, "expected_goals"), "pases": _stat(st, "Total passes"),
                  "tirosRival": _stat(st_r, "Total Shots"), "xgRival": _stat(st_r, "expected_goals")},
        "xi": {"formacion": ali.get("formacion") or "", "entrenador": ali.get("entrenador") or "",
               "conGrid": bool(ali.get("conGrid")),
               "titulares": [{"nombre": j["nombre"], "posicion": j["posicion"], "carril": j["carril"]}
                             for j in xi]},
    }
    # un tercio de los onces capturados no trae grid (24/09: Primera Nacional
    # de Argentina, Liga de Expansión, las Primera B…). Sin grid la posición
    # dice la LÍNEA (D/M/F) pero no el lado: el carril no se deduce de ella.
    if xi and not ali.get("conGrid"):
        anterior["xi"]["sinCarriles"] = (
            "la ficha no trae grid: la posición da la línea (G/D/M/F) pero no el lado. "
            "M2 por carril solo con fuente externa (citala); si no, duelos por línea y "
            "carril «sin dato»")
    # ≥2 recibidos: el skill manda chequear MECANISMO-ABIERTO. El mecanismo en
    # sí (centro y cabezazo, rechace…) NO está en nuestros datos: se señala,
    # no se decide.
    if len(recibidos) >= 2:
        anterior["mecanismoAbiertoCandidato"] = {
            "recibidos": [{"minuto": g["minuto"], "autor": g["autor"], "detalle": g["detalle"]} for g in recibidos],
            "porque": "≥2 goles recibidos en el partido anterior: chequear si comparten mecanismo "
                      "(el mecanismo no está en nuestros datos; lo nombra quien analiza)",
        }
    cambios = None
    if len(ants) > 1 and xi:
        prev = {j["player_id"]: j["jugador"] for j in _titulares(ants[1]["id"], team_id) if j["player_id"]}
        ahora = {j["jugadorId"]: j["nombre"] for j in xi if j.get("jugadorId")}
        if prev and ahora:
            prev_ali = ((tactica_de(ants[1]["id"], ants[1]["home_team_id"], ants[1]["away_team_id"])
                         .get("alineaciones") or {}).get("local" if ants[1]["home_team_id"] == team_id
                                                          else "visitante") or {})
            cambios = {"vsFixtureId": ants[1]["id"], "vsFecha": str(ants[1]["date"])[:10],
                       "entraron": [ahora[i] for i in ahora if i not in prev],
                       "salieron": [prev[i] for i in prev if i not in ahora],
                       "formacionAntes": prev_ali.get("formacion") or "",
                       "formacionAhora": ali.get("formacion") or ""}
    return {
        **base,
        "diasDescanso": jug_dias_descanso(str(a["date"]), str(fecha)),  # por horas (769)
        "partidoAnterior": anterior,
        "cambiosXi": cambios,
        "parejasNuevas": _parejas_nuevas(team_id, fecha, xi) if xi else [],
        "aperturaPrevia": _apertura_previa(nombre, a["id"]),
        # DTP v1.4: para responder la pregunta 6 sobre ESTE bloque (la apertura
        # del rival la lee de acá)
        "casosBloque": casos_bloque(team_id, fecha),
        # DTP v1.6 (cambio 4): el ejecutor de penales sale de la base, no de la
        # «jerarquía»: los penales de la temporada con convertidos y errados
        "penales": penales_temporada(team_id, fecha),
        "nivelDeDato": "C" if anterior["amistoso"] or not xi else "B",
        "faltan": faltan,
    }


PENALES_DIAS = 365


def penales_temporada(team_id: int, antes: str, dias: int = PENALES_DIAS) -> dict:
    """Quién tiró los penales del equipo en el último año ANTES de `antes`
    (eventos de la ficha: `Goal` con «Penalty» = convertido, «Missed Penalty» =
    errado; la tanda va como `Shootout` y no cuenta). Solo cubre los partidos
    con ficha capturada: lo dice `partidosConEventos`."""
    try:
        desde = (datetime.strptime(str(antes)[:10], "%Y-%m-%d") - timedelta(days=dias)).strftime("%Y-%m-%d")
        filas = saddb.query(
            "sad",
            "SELECT e.jugador, e.jugador_id, e.detalle FROM fixture_eventos e JOIN fixtures f ON f.id = e.fixture_id "
            "WHERE e.equipo_id = ? AND e.tipo = 'Goal' AND lower(e.detalle) LIKE '%penalty%' "
            "AND lower(e.detalle) NOT LIKE '%own%' AND f.date >= ? AND f.date < ?",
            (team_id, desde, str(antes)[:19]))
        con_ev = saddb.query_one(
            "sad",
            "SELECT COUNT(DISTINCT e.fixture_id) n FROM fixture_eventos e JOIN fixtures f ON f.id = e.fixture_id "
            "WHERE (f.home_team_id = ? OR f.away_team_id = ?) AND f.date >= ? AND f.date < ?",
            (team_id, team_id, desde, str(antes)[:19]))
    except Exception:  # noqa: BLE001 — base sin eventos: sin dato, no cero
        return {"ejecutores": [], "partidosConEventos": 0, "nota": "sin eventos en la base"}
    # EL AÑO CRUZA EL MERCADO (incidencia 718, 27/10/2026): Sassuolo salía con
    # Pinamonti de ejecutor, que hoy juega en la Lazio, y la Lazio con
    # Artistico, que ya no está en su plantel. Cada ejecutor dice si sigue en
    # la plantilla de hoy (`enPlantilla`; None = sin id o sin plantilla
    # ingestada, no se juzga) y el que se fue no encabeza la lista.
    plantel = _ids_plantel(team_id)
    por = {}
    for f in filas:
        nombre = (f["jugador"] or "").strip()
        if not nombre:
            continue
        e = por.setdefault(nombre, {"nombre": nombre, "convertidos": 0, "errados": 0, "enPlantilla": None})
        jid = f["jugador_id"] if "jugador_id" in f.keys() else None
        if plantel and jid:
            e["enPlantilla"] = jid in plantel
        e["errados" if "missed" in (f["detalle"] or "").lower() else "convertidos"] += 1
    ejecutores = sorted(por.values(), key=lambda e: (e["enPlantilla"] is False,
                                                     -(e["convertidos"] + e["errados"]), -e["convertidos"]))
    idos = [e["nombre"] for e in ejecutores if e["enPlantilla"] is False]
    if not ejecutores:
        nota = "sin penales en los partidos con eventos del último año: decilo así, no «sin dato»"
    elif len(idos) == len(ejecutores):
        nota = (f"ninguno de los que tiraron penales en el año sigue en el plantel ({', '.join(idos)}): "
                "el ejecutor de hoy sale de la prensa, o se dice «sin ejecutor conocido»")
    else:
        nota = "el primero es el que más tiró: va como ejecutor salvo fuente del partido que diga otro"
        if idos:
            nota += f"; ya no están en el plantel: {', '.join(idos)}"
    return {"ejecutores": ejecutores, "partidosConEventos": (con_ev or {"n": 0})["n"], "nota": nota}


def _ejecutores_en_base(team_id, fecha: str) -> bool:
    """¿La base tiene algún penal del equipo en el año? Ante la duda (sin base), sí."""
    try:
        return bool(penales_temporada(team_id, fecha)["ejecutores"])
    except Exception:  # noqa: BLE001
        return True


def _ids_plantel(team_id: int) -> set[int]:
    """Los ids de la plantilla de HOY (con stats o solo en la lista actual).
    Vacío si no hay ingesta: entonces no se juzga quién sigue."""
    try:
        from backend.jugadores import plantilla_de
        p = plantilla_de(team_id)
    except Exception:  # noqa: BLE001
        return set()
    ids = ({j.get("id") for j in p.get("jugadores") or []}
           | {j.get("jugadorId") for j in p.get("plantelSinStats") or []}) - {None}
    if not ids:
        return ids
    # …Y QUIEN FIGURA EN LAS HOJAS RECIENTES (incidencia 767, Metropolitanos:
    # Riasco convirtió un penal el 25/10 y Ferro fue titular, y salían
    # «enPlantilla: false» porque las stats de la API van atrasadas). Jugó hace
    # días: está en el club.
    try:
        from backend.analisis.f1_base import onces_recientes
        ids |= {pid for pid in onces_recientes(team_id, "9999")["jugadores"] if pid}
    except Exception:  # noqa: BLE001 — sin hojas queda la plantilla
        pass
    return ids


NO_CALCULABLES = [
    {"modulo": "M1", "que": "señal del XI, roles reasignados, vulnerabilidad propia, forma sin balón",
     "porque": "lectura del XI: el XI y sus carriles van arriba, la interpretación es tuya"},
    {"modulo": "M2", "que": "duelos por carril, mismatches, vías de gol, rest defense",
     "porque": "cruce táctico de los dos perfiles"},
    {"modulo": "M2", "que": "las 6 preguntas del checklist del bloque rival",
     "porque": "meses con el modelo, minutos de la línea, oficio de los centrales, banco, plan de "
               "repliegue y si el bloque fue probado bajo presión: investigación. La CLASE la "
               "calcula el backend a partir de tus respuestas"},
    {"modulo": "M4", "que": "disparador, secuencia y responsables de cada gol",
     "porque": "los eventos dan minuto, autor y asistente; la mecánica no (no fabricarla)"},
    {"modulo": "M5", "que": "hasta qué minuto funcionó el plan, peligro real, cronología del giro",
     "porque": "juicio contra la apertura previa que viaja en `aperturaPrevia`"},
]


def ficha(fixture_id: int) -> dict | None:
    fx = _fixture(fixture_id)
    if not fx:
        return None
    return {
        "fixtureId": fixture_id,
        "partido": {"equipoA": fx["home_name"], "equipoB": fx["away_name"], "fecha": str(fx["date"])[:10]},
        "a": insumos_equipo(fx["home_team_id"], fx["home_name"], fx),
        "b": insumos_equipo(fx["away_team_id"], fx["away_name"], fx),
        "noCalculables": NO_CALCULABLES,
        "nota": "esto NO es el DTP: son los insumos que salen de la ficha ya ingestada. El CIERRE "
                "se valida contra `aperturaPrevia` (lo que se declaró ANTES del partido anterior), "
                "nunca contra la memoria; sin apertura previa, el cierre no emite veredicto.",
    }


# ── 2 · el DTP estructurado del parte ────────────────────────────────────────

_IZQ = {"improvisado", "izq", "izquierda", "no", "reaccion", "reacción"}
_DER = {"estructural", "der", "derecha", "si", "sí", "plan"}
PREGUNTAS = ("p1", "p2", "p3", "p4", "p5", "p6")


def _txt(v) -> str:
    return (v or "").strip() if isinstance(v, str) else ""


def _lista_txt(v) -> list[str]:
    if isinstance(v, str):
        v = [v]
    return [_txt(x) for x in (v or []) if _txt(x)] if isinstance(v, list) else []


def _dict(v) -> dict:
    return v if isinstance(v, dict) else {}


def _col(v) -> str:
    t = _txt(v).lower() if isinstance(v, str) else ("der" if v is True else "izq" if v is False else "")
    return "izq" if t in _IZQ else "der" if t in _DER else "sin dato"


# …y «banco del que persigue», «el banco» a secas: el rol ya dice que arranca
# suplente (Barracas, S. Rosané, incidencia 704)
_DESDE_BANCO = re.compile(r"desde el banco|de suplente|suplente|revulsivo|de cambio|ingresa|entra desde|\bbanco\b",
                          re.I)


def _suplentes_nombrados(banca: list[str], titulares: list[str], texto: str, crudo: str = "") -> list[str]:
    """Los de la banca que el texto nombra, sin los que el texto nombra por un
    titular. Un suplente que casa SOLO por la letra de tolerancia no cuenta si
    un titular casa exacto con esa palabra: Freiburg–Bayern (incidencia 605)
    nombraba a M. Ginter, titular, y la tolerancia lo casaba con C. Günter, del
    banco, y saltaba DTP-REHACER."""
    def exacto(n: str) -> set:
        return {a for a in _apellidos(n) if f" {a} " in f" {texto} "}
    tit_exactos = set().union(*(exacto(t) for t in titulares)) if titulares else set()
    out = []
    ap_tit = set().union(*(set(_apellidos(t)) for t in titulares)) if titulares else set()
    for n in banca:
        if not _apellidos(n) or not _en_referencia(n, texto):
            continue
        # el titular del mismo apellido tapa al suplente solo si TAMBIÉN casa
        # con la inicial: «J. Castillo» en el texto es el suplente aunque E.
        # Castillo sea titular (Alianza, incidencia 709)
        if any(_en_referencia(t, texto, crudo) and set(_apellidos(t)) & set(_apellidos(n)) for t in titulares):
            continue
        # un nombre de pila compartido no nombra al suplente: «Andrés Rentería»
        # (titular) no es «Faber Andrés Gil» (banco) (Jaguares, incidencia 686)
        if crudo and _solo_como_pila(n, crudo, ap_tit):
            continue
        if not exacto(n) and any(_casi(a, w) for a in _apellidos(n) for w in tit_exactos):
            continue
        # la inicial también nombra: «A. Terrazas» no es J. Terrazas, el arquero
        # suplente (incidencia 638)
        if _inicial_choca(n, crudo):
            continue
        out.append(n)
    return out


def _solo_como_pila(n: str, crudo: str, apellidos_titulares: set) -> bool:
    """Cada mención en el texto de las palabras de `n` va seguida (sin coma)
    del apellido de un titular: es el nombre de pila de ese titular."""
    vistas = 0
    for a in _apellidos(n):
        for m in re.finditer(r"(?:^|[\s,;:/(])([^\s,;:/()]+)", crudo):
            if _plano(m.group(1)).strip() != a:
                continue
            vistas += 1
            sig = re.match(r"\s+([^\s,;:/()]+)", crudo[m.end(1):])
            if not sig or _plano(sig.group(1)).strip() not in apellidos_titulares:
                return False
    return vistas > 0


def _xi_texto(v) -> str:
    """El XI de referencia como texto: el prompt pide «la lista de los 11» y
    varios partes la mandaron como LISTA, que `_txt` dejaba vacía y se
    rechazaba como «vacío o en prosa» (Freiburg–Bayern, Torque–Cerro, Real
    Sociedad–Levante: incidencia 574). Una lista de nombres o de `{nombre}`
    se une con comas."""
    if isinstance(v, (list, tuple)):
        nombres = [_txt(x.get("nombre") if isinstance(x, dict) else x) for x in v]
        return ", ".join(n for n in nombres if n)
    return _txt(v)


def clasificar_bloque(check: dict) -> dict:
    """La clase del bloque con la regla del skill (v1.2).

    3+ respuestas de la columna izquierda en p1-p5 → improvisado (55-65');
    3+ de la derecha → estructural (80-90'). La p6 no cuenta en el recuento:
    es una llave. Un estructural con la p6 en «no» —o sin un caso concreto
    nombrado— es `estructural no probado`: conserva la vida útil, pero la
    alerta de degradación NO se suprime y en el TDE `C1` vale 0.5. Sin 3 de un
    lado (faltan respuestas) → ambiguo: se publican las dos lecturas."""
    r = {p: _col((check or {}).get(p)) for p in PREGUNTAS}
    izq = sum(r[p] == "izq" for p in PREGUNTAS[:5])
    der = sum(r[p] == "der" for p in PREGUNTAS[:5])
    sin = 5 - izq - der
    conteo = {"izquierda": izq, "derecha": der, "sinDato": sin}
    caso = _txt((check or {}).get("casoP6"))
    if not any(v != "sin dato" for v in r.values()):
        return {"clase": "", "vidaUtilMin": "", "alertaDegradacion": None, "conteo": conteo,
                "respuestas": r, "c1Tde": None,
                "motivo": "checklist sin responder: el skill prohíbe dar minutos de vida útil sin clasificar"}
    if izq >= 3:
        return {"clase": "improvisado", "vidaUtilMin": "55-65", "alertaDegradacion": True,
                "conteo": conteo, "respuestas": r, "c1Tde": 1.0,
                "motivo": f"{izq} de 5 insumos del lado improvisado"}
    if der >= 3:
        probado = r["p6"] == "der" and bool(caso)
        motivo = (f"{der} de 5 insumos del lado estructural y probado bajo presión ({caso})" if probado else
                  f"{der} de 5 insumos del lado estructural, pero " +
                  ("la pregunta 6 dice que nunca sostuvo un resultado contra un rival obligado"
                   if r["p6"] == "izq" else
                   "sin caso concreto nombrado en la pregunta 6: sin prueba no se suprime la alerta"))
        return {"clase": "estructural" if probado else "estructural no probado", "vidaUtilMin": "80-90",
                "alertaDegradacion": not probado, "conteo": conteo, "respuestas": r,
                "c1Tde": 0.0 if probado else 0.5, "motivo": motivo}
    return {"clase": "ambiguo", "vidaUtilMin": "55-65 o 80-90", "alertaDegradacion": True,
            "conteo": conteo, "respuestas": r, "c1Tde": None,
            "motivo": f"{izq} a la izquierda, {der} a la derecha y {sin} sin dato: publicar las dos "
                      "lecturas, no elegir la que conviene a la narrativa"}


def _gol(g: dict) -> dict:
    g = _dict(g)
    via = _txt(g.get("via")).lower().replace(" ", "_")
    resp = []
    for x in g.get("responsablesError") or g.get("responsables_error") or []:
        x = _dict(x)
        nivel = _txt(x.get("nivel")).lower()
        if _txt(x.get("jugador")):
            resp.append({"jugador": _txt(x.get("jugador")),
                         "nivel": nivel if nivel in NIVELES_RESP else "",
                         "detalle": _txt(x.get("detalle"))})
    return {"gol": _txt(g.get("gol")), "minuto": g.get("minuto") if isinstance(g.get("minuto"), (int, float)) else None,
            "via": via if via in VIAS else "", "disparador": _txt(g.get("disparador")),
            "secuencia": _txt(g.get("secuencia")), "definicion": _txt(g.get("definicion")),
            "responsablesMerito": _lista_txt(g.get("responsablesMerito") or g.get("responsables_merito")),
            "responsablesError": resp, "absolucion": _txt(g.get("absolucion"))}


def _caso_bloque(x) -> dict | None:
    x = _dict(x)
    caso = _txt(x.get("caso"))
    if not caso:
        return None
    sostuvo = x.get("sostuvo") if isinstance(x.get("sostuvo"), bool) else None
    tipo = _txt(x.get("tipo")).lower().replace(" ", "_").replace("-", "_")
    # DTP v1.5 (cambio 2): el caso completo — con uno más no prueba, un 0-0
    # cuenta solo si el empate le servía al que defendía, quién sostuvo
    # (bloque o arquero) y con qué línea
    return {"sostuvo": sostuvo, "caso": caso,
            "conUnoMenos": x.get("conUnoMenos") is True,
            "conUnoMas": x.get("conUnoMas") is True,
            "tipo": tipo if tipo in TIPOS_CASO else "",
            "sostuvoArquero": x.get("sostuvoArquero") if isinstance(x.get("sostuvoArquero"), bool) else None,
            "linea": _txt(x.get("linea")),
            # DTP v1.6 (cambio 5): sede y competición del caso; si no vienen, la
            # app las toma del partido que se cierra al leer (`casos_bloque`)
            "sede": _sede(x.get("sede")), "competicion": _txt(x.get("competicion"))}


SEDES = ("local", "visita", "neutral")


def _sede(v) -> str:
    t = _txt(v).lower()
    t = {"l": "local", "v": "visita", "visitante": "visita", "de local": "local", "de visita": "visita",
         "neutro": "neutral", "neutra": "neutral"}.get(t, t)
    return t if t in SEDES else ""


TIPOS_CASO = ("ventaja", "empate_que_sirve", "cero_cero")
REGIMENES = ("cualquiera", "persiguiendo")


VEREDICTOS = ("FAVORABLE", "NEUTRO", "DESFAVORABLE")
RAMAS_VEREDICTO = ("igualadoOArriba", "persiguiendo")


def _veredicto(v) -> str:
    t = _txt(v).upper().replace("MATCHUP ", "").strip()
    return t if t in VEREDICTOS else ""


def _veredicto_ramas(x) -> dict:
    x = _dict(x)
    return {r: {"veredicto": _veredicto(_dict(x.get(r)).get("veredicto")), "razon": _txt(_dict(x.get(r)).get("razon"))}
            for r in RAMAS_VEREDICTO}


def _rama_posesion(x) -> dict:
    x = _dict(x)
    return {"valor": _txt(x.get("valor")), "contraQuien": _txt(x.get("contraQuien")),
            "marcador": _txt(x.get("marcador")), "sede": _txt(x.get("sede"))}


def _posesion(pos: dict) -> dict:
    """DTP v1.5 (cambio 3): la posesión en dos ramas, igualado o arriba y
    persiguiendo. Un parte viejo con la forma plana sigue leyéndose: la plana
    queda arriba y las ramas vacías."""
    return {**_rama_posesion(pos),
            "igualadoOArriba": _rama_posesion(pos.get("igualadoOArriba")),
            "persiguiendo": _rama_posesion(pos.get("persiguiendo"))}


def _piezas(v) -> list[dict]:
    """DTP v1.5 (cambio 6): de quién depende la capa de nombres del M2 —
    duelos con nombre, contenedor del seguro, ejecutor de penales—, con su
    lado. Si una pieza arranca en el banco, el bloque se rehace (rehacer())."""
    out = []
    for x in v or []:
        if isinstance(x, str):
            x = {"nombre": x}
        x = _dict(x)
        nombre = _txt(x.get("nombre"))
        if not nombre:
            continue
        lado = _txt(x.get("lado")).lower()
        out.append({"nombre": nombre, "lado": lado if lado in ("foco", "rival") else "foco",
                    "rol": _txt(x.get("rol"))})
    return out


def casos_bloque(team_id: int, antes: str, dias: int = 180) -> list[dict]:
    """Los casos de la pregunta 6 que dejaron los cierres sobre el bloque de
    ESTE equipo (DTP v1.4): en la cohorte c3 el propio partido fue «el caso que
    le faltaba a la 6» unas quince veces, y la apertura siguiente lo volvía a
    buscar a mano. Solo partes anteriores a `antes`, del bloque propio del foco."""
    from backend.analisis.parte import _conectar
    try:
        desde = (datetime.strptime(antes[:10], "%Y-%m-%d") - timedelta(days=dias)).strftime("%Y-%m-%d")
    except ValueError:
        return []
    with _conectar() as con:
        filas = con.execute("SELECT fixture_id, fecha, parte_json FROM parte_cowork WHERE fecha >= ? AND fecha < ? "
                            "ORDER BY fecha DESC", (desde, antes[:10])).fetchall()
    out = []
    for f in filas:
        try:
            bloques = (json.loads(f["parte_json"]).get("dtp") or {}).get("bloques") or []
        except ValueError:
            continue
        con_caso = [b for b in bloques if ((b.get("cierre") or {}).get("casoBloque") or {}).get("caso")]
        if not con_caso:
            continue
        fx = saddb.query_one("sad", "SELECT home_team_id, away_team_id FROM fixtures WHERE id=?", (f["fixture_id"],))
        if not fx:
            continue
        for b in con_caso:
            tid = fx["home_team_id"] if b.get("equipo") == "a" else fx["away_team_id"]
            if tid == team_id:
                caso = {**b["cierre"]["casoBloque"], "deParte": f["fixture_id"], "fecha": (f["fecha"] or "")[:10],
                        "fechaParte": (f["fecha"] or "")[:10]}
                # DTP v1.6: el caso es del partido que ese cierre cerró —el anterior
                # del equipo a la fecha del parte—; de ahí salen la sede y la
                # competición cuando no se escribieron, y la FECHA es la de ese
                # partido, no la del parte (incidencia 762: Rennes jugado el 22/10
                # viajaba con el 25/10 del parte que lo cerró)
                ant = _anteriores(team_id, str(f["fecha"] or ""), 1)
                if ant:
                    caso["fecha"] = str(ant[0]["date"] or "")[:10] or caso["fecha"]
                if not caso.get("sede") or not caso.get("competicion"):
                    if ant:
                        caso.setdefault("sede", "")
                        caso["sede"] = caso["sede"] or ("local" if ant[0]["home_team_id"] == team_id else "visita")
                        caso["competicion"] = caso.get("competicion") or (ant[0]["liga"] or "")
                        caso["sedeCalculada"] = True
                out.append(caso)
    return out[:6]


def _bloque(x: dict, lado: str) -> dict:
    ap, ci = _dict(x.get("apertura")), _dict(x.get("cierre"))
    m1, m2, m6 = _dict(ap.get("m1")), _dict(ap.get("m2")), _dict(ap.get("m6"))
    vias, rest, pos = _dict(m2.get("viasGol")), _dict(m2.get("restDefense")), _dict(m2.get("posesion"))
    chk = _dict(m2.get("checklistBloqueRival"))
    m5, mec = _dict(ci.get("m5")), _dict(ci.get("mecanismoAbierto"))
    contraste = _dict(m5.get("contraste"))
    fases = []
    for f in ap.get("m3Fases") or []:
        f = _dict(f)
        if _txt(f.get("tramo")) in TRAMOS:
            fases.append({"tramo": _txt(f.get("tramo")), "plan": _txt(f.get("plan")),
                          "palancas": _lista_txt(f.get("palancas"))})
    return {
        "equipo": lado,
        "apertura": {
            "m1": {"sistema": _txt(m1.get("sistema")), "xiReferencia": _xi_texto(m1.get("xiReferencia")),
                   "senalXi": _txt(m1.get("senalXi")), "rolesReasignados": _lista_txt(m1.get("rolesReasignados")),
                   "vulnerabilidad": _txt(m1.get("vulnerabilidad")), "formaSinBalon": _txt(m1.get("formaSinBalon")),
                   "minutosCompartidos": _txt(m1.get("minutosCompartidos"))},
            "m2": {"choqueSistemas": _txt(m2.get("choqueSistemas")),
                   # DTP v1.4: el carril en las dos direcciones (`vuelta`) y el duelo
                   # con nombre propio marcado condicional al once (`condicional`)
                   "duelosCarril": [{"carril": _txt(_dict(d).get("carril")), "duelo": _txt(_dict(d).get("duelo")),
                                     "mismatch": _txt(_dict(d).get("mismatch")),
                                     "vuelta": _txt(_dict(d).get("vuelta")),
                                     "condicional": _dict(d).get("condicional") is True}
                                    for d in (m2.get("duelosCarril") or []) if _txt(_dict(d).get("duelo"))],
                   "checklistBloqueRival": {**{p: _col(chk.get(p)) for p in PREGUNTAS},
                                            "casoP6": _txt(chk.get("casoP6")), "notas": _txt(chk.get("notas"))},
                   "viasGol": {"foco": _lista_txt(vias.get("foco")), "rival": _lista_txt(vias.get("rival"))},
                   "restDefense": {"foco": _txt(rest.get("foco")), "rival": _txt(rest.get("rival")),
                                   "nivelFoco": _nivel_seguro(rest.get("nivelFoco")),
                                   "nivelRival": _nivel_seguro(rest.get("nivelRival")),
                                   # v1.5: la rama persiguiendo; el SOB2 del TDE sigue
                                   # heredando nivelFoco/nivelRival hasta que el usuario decida
                                   "nivelFocoPersiguiendo": _nivel_seguro(rest.get("nivelFocoPersiguiendo")),
                                   "nivelRivalPersiguiendo": _nivel_seguro(rest.get("nivelRivalPersiguiendo"))},
                   "posesion": _posesion(pos),
                   "piezas": _piezas(m2.get("piezas")),
                   "veredicto": _txt(m2.get("veredicto")).upper().replace("MATCHUP ", ""),
                   "razon": _txt(m2.get("razon")),
                   # DTP v1.6 (cambio 1): un veredicto por rama del estado de marcador
                   "veredictoRamas": _veredicto_ramas(m2.get("veredictoRamas"))},
            "m3Fases": fases,
            "m6": {"competitivo": m6.get("competitivo") if isinstance(m6.get("competitivo"), bool) else None,
                   "rotacion": _txt(m6.get("rotacion")), "fatiga": _txt(m6.get("fatiga")),
                   "ausencias": _txt(m6.get("ausencias")), "otros": _txt(m6.get("otros"))},
        },
        "cierre": {
            "sinAnterior": bool(ci.get("sinAnterior")),
            "m4Goles": [_gol(g) for g in (ci.get("m4Goles") or [])],
            "m5": {"planFuncionoHastaMin": m5.get("planFuncionoHastaMin")
                   if isinstance(m5.get("planFuncionoHastaMin"), (int, float)) else None,
                   "peligroReal": _txt(m5.get("peligroReal")), "cronologiaGiro": _txt(m5.get("cronologiaGiro")),
                   "contraste": {"aciertos": _lista_txt(contraste.get("aciertos")),
                                 "fallos": _lista_txt(contraste.get("fallos"))},
                   "preguntaChecklistFallida": _txt(m5.get("preguntaChecklistFallida"))},
            "mecanismoAbierto": {"activo": bool(mec.get("activo")), "mecanismo": _txt(mec.get("mecanismo")),
                                 "lineaRepite": mec.get("lineaRepite") if isinstance(mec.get("lineaRepite"), bool) else None,
                                 "correccionEnVivo": mec.get("correccionEnVivo")
                                 if isinstance(mec.get("correccionEnVivo"), bool) else None,
                                 # DTP v1.4: la frecuencia se cumplió y ninguna fuente nombra
                                 # la jugada → vía a verificar, nivel C, no degrada K
                                 "sinMecanica": mec.get("sinMecanica") is True,
                                 # v1.5: el de transición vale si el equipo vuelve a perseguir
                                 "regimen": (_txt(mec.get("regimen")).lower()
                                             if _txt(mec.get("regimen")).lower() in REGIMENES else "")},
            # DTP v1.4: el caso de la pregunta 6 del bloque PROPIO del foco en el
            # partido que se cierra (¿sostuvo contra un obligado?). La apertura del
            # rival siguiente lo lee de `casosBloque` en los insumos.
            "casoBloque": _caso_bloque(ci.get("casoBloque")),
        },
    }


# SOB2 del TDE («seguro tras la pérdida») con la rúbrica de INDICE_IE.md:
# 0 pivote fijo por delante de los centrales · 0.5 depende del intérprete o
# del marcador · 1 sin contención con los dos laterales arriba. El skill manda
# que el rest defense del M2 del DTP viaje DIRECTO a SOB2, sin re-estimarlo.
SOB2_DE_NIVEL = {"fijo": 0.0, "depende": 0.5, "sin": 1.0}
_SINONIMOS_SEGURO = {"fijo": "fijo", "pivote fijo": "fijo", "con seguro": "fijo", "0": "fijo",
                     "depende": "depende", "parcial": "depende", "0.5": "depende",
                     "sin": "sin", "sin seguro": "sin", "sin contencion": "sin", "sin contención": "sin", "1": "sin"}


def _nivel_seguro(v) -> str:
    t = _txt(v).lower() if isinstance(v, str) else (str(v) if isinstance(v, (int, float)) else "")
    return _SINONIMOS_SEGURO.get(t, "")


def herencia_tde(dtp: dict) -> dict:
    """Lo que el TDE de cada equipo HEREDA del DTP, por lado.

    - C1 (repliegue entrenado) del equipo X sale de la clase del bloque de X
      que calculó el DTP del RIVAL (el checklist mira el bloque rival).
    - SOB2 (seguro tras la pérdida) de X sale del rest defense: primero del
      DTP del propio X (`nivelFoco`), si no del DTP del rival (`nivelRival`).
    """
    out: dict[str, dict] = {l: {} for l in LADOS}
    bloques = {b["equipo"]: b for b in (dtp or {}).get("bloques") or []}
    for foco, b in bloques.items():
        rival = "b" if foco == "a" else "a"
        clase = clasificar_bloque(b["apertura"]["m2"]["checklistBloqueRival"])
        if clase["c1Tde"] is not None:
            out[rival]["C1"] = {"valor": clase["c1Tde"],
                                "de": f"checklist del DTP con foco en el lado {foco}, que evalúa el bloque del "
                                      f"lado {rival}: bloque {clase['clase']}"}
        elif clase["clase"] == "ambiguo":
            # AMBIGUO NO HEREDA, Y SE DICE. Slovan (20/10/2026, incidencia 302):
            # heredadoDtp listaba solo SOB2 y nadie veía por qué C1 era el declarado
            out[rival]["C1"] = {"valor": None,
                                "de": f"checklist del DTP con foco en el lado {foco}: bloque del lado {rival} "
                                      f"ambiguo ({clase['motivo']}) — C1 NO se hereda, queda el declarado"}
    for lado in LADOS:
        rd_propio = ((bloques.get(lado) or {}).get("apertura") or {}).get("m2", {}).get("restDefense") or {}
        otro = bloques.get("b" if lado == "a" else "a") or {}
        rd_rival = (otro.get("apertura") or {}).get("m2", {}).get("restDefense") or {}
        if rd_propio.get("nivelFoco"):
            out[lado]["SOB2"] = {"valor": SOB2_DE_NIVEL[rd_propio["nivelFoco"]],
                                 "de": f"rest defense del DTP del lado {lado} ({rd_propio['nivelFoco']})"}
        elif rd_rival.get("nivelRival"):
            out[lado]["SOB2"] = {"valor": SOB2_DE_NIVEL[rd_rival["nivelRival"]],
                                 "de": f"rest defense leído desde el DTP del rival ({rd_rival['nivelRival']})"}
    return out


_SIN_DATO = {"", "sin dato", "sin_dato", "sd", "?", "n/a", "na", "-"}


def _checklist_raros(y: dict, i, rechazos: list) -> None:
    """Un valor del checklist fuera de la lista se guardaba como «sin dato» en
    silencio y bajaba el recuento sin que nadie lo viera (incidencia 321,
    20/10/2026). Se sigue guardando así —no se adivina—, pero se DICE."""
    chk = _dict(_dict(_dict(y.get("apertura")).get("m2")).get("checklistBloqueRival"))
    for p in PREGUNTAS:
        v = chk.get(p)
        if v is None or isinstance(v, bool):
            continue
        t = _txt(v).lower() if isinstance(v, str) else repr(v)
        if t in _IZQ or t in _DER or t in _SIN_DATO:
            continue
        rechazos.append({
            "donde": f"dtp.bloques[{i}].apertura.m2.checklistBloqueRival.{p}",
            "porque": f"valor fuera de la lista: {v!r} — se guardó «sin dato» y no cuenta para la clase",
            "esperado": ('"si" | "no" | "sin dato" (la p6 es la llave: ¿sostuvo un resultado contra un rival '
                         'obligado?)' if p == "p6" else
                         '"improvisado" | "estructural" | "sin dato" (se guardan como "izq" / "der")')})


def normalizar_dtp(x, rechazos: list) -> dict:
    """`{"bloques": [...]}`, `{"a": …, "b": …}` o una lista; uno por equipo foco."""
    if x is None:
        return {}
    if isinstance(x, list):
        crudos = list(enumerate(x))
    elif isinstance(x, dict) and isinstance(x.get("bloques"), list):
        crudos = list(enumerate(x["bloques"]))
    elif isinstance(x, dict) and set(x) & set(LADOS):
        crudos = [(l, {**_dict(x[l]), "equipo": l}) for l in LADOS if x.get(l) is not None]
    else:
        rechazos.append({"donde": "dtp", "porque": "forma no reconocida",
                         "esperado": '{"bloques": [{"equipo": "a", "apertura": {…}, "cierre": {…}}]}'})
        return {}
    bloques, vistos = [], set()
    for i, y in crudos:
        y = _dict(y)
        lado = _txt(y.get("equipo")).lower()
        if lado not in LADOS:
            rechazos.append({"donde": f"dtp.bloques[{i}].equipo",
                             "porque": "cada bloque es de UN equipo foco: `equipo` tiene que ser \"a\" o \"b\"",
                             "esperado": '"a" | "b"'})
            continue
        if lado in vistos:
            rechazos.append({"donde": f"dtp.bloques[{i}]", "porque": f"bloque repetido para el lado {lado}: "
                             "manda el primero", "esperado": "un bloque por equipo foco"})
            continue
        vistos.add(lado)
        _checklist_raros(y, i, rechazos)
        # v1.5 (cambio 6): sin XI de referencia el once oficial no se puede
        # comparar (Chapecoense, incidencia 525) — se dice al depositar
        xi_ref = _xi_texto(_dict(_dict(y.get("apertura")).get("m1")).get("xiReferencia"))
        if sin_referencia(xi_ref) or len(_plano(xi_ref).split()) < 8:
            rechazos.append({"donde": f"dtp.bloques[{i}].apertura.m1.xiReferencia",
                             "porque": "XI de referencia vacío o en prosa: el once oficial no se va a poder "
                                       "comparar y DTP-REHACER no saltará (DTP v1.5)",
                             "esperado": "lista de los 11 titulares; sin previa, el último once oficial, "
                                         "dicho en `senalXi`"})
        bloques.append(_bloque(y, lado))
    return {"bloques": bloques} if bloques else {}


# ── el DTP a rehacer: el once oficial contradice la apertura ───────────────
#
# En la autopsia del 11/10/2026, en 9 de 24 partidos el sistema o el once que
# salió no era el de la previa, y el mapa de duelos se quedó escrito sobre un
# equipo que no jugó (el M2 de Botafogo–Cienciano en TDE-026 ya lo había
# hecho: un mismatch contra un lateral que no fue titular). Cuando la ficha
# trae el once, la comparación es aritmética: el sistema por sus cifras y el
# XI de referencia por apellido. No reescribe nada; marca el bloque.

REHACER_AUSENTES = 3   # titulares oficiales que no figuran en el XI de referencia


def _cifras_sistema(texto: str) -> str:
    m = re.search(r"\d(?:\s*[-–]\s*\d){2,4}", texto or "")
    return re.sub(r"\D", "", m.group(0)) if m else ""


# UN SISTEMA CITADO COMO ANTECEDENTE NO ES UNA OPCIÓN DECLARADA. Inter de
# Bogotá (incidencia 706): «4-3-3 (probable sin Vásquez; el 20/10 jugó 3-4-3)»
# daba {433, 343}; salió 3-4-3 y no sonó nada con el M2 escrito sobre línea de
# cuatro. Lo que va después de «jugó», «usó», «venía», «el último», una fecha…
# en la misma cláusula es historia, no la apuesta de hoy.
_ANTECEDENTE = re.compile(r"jug[oóa]|jugaba|us[oó]\b|usaba|ven[ií]a|anterior|[uú]ltim|pasad|antes\b|"
                          r"\b\d{1,2}/\d{1,2}\b|fecha \d|jornada \d", re.I)


def _sistemas(texto: str, antecedentes: bool = False) -> set[str]:
    """TODOS los sistemas que nombra la apertura: «4-2-3-1 / 4-3-3» son dos
    opciones declaradas, y salir con cualquiera de ellas no contradice nada
    (Boca–Vasco, 15/10/2026: el aviso DTP-REHACER salía falso). Sin
    `antecedentes`, deja fuera los citados como partido anterior (706); si
    todos lo son, quedan todos (la apertura no declaró otro)."""
    texto = texto or ""
    todos, hoy = set(), set()
    for m in re.finditer(r"\d(?:\s*[-–]\s*\d){2,4}", texto):
        cifras = re.sub(r"\D", "", m.group(0))
        todos.add(cifras)
        clausula = re.split(r"[;(),.]", texto[:m.start()])[-1]
        if not _ANTECEDENTE.search(clausula):
            hoy.add(cifras)
    return todos if antecedentes or not hoy else hoy


def _forma(cifras: str) -> str:
    """Línea de atrás (4 · 3/5) y, con línea de cuatro, puntas (2 · 1/3):
    «4-3-3», «4-2-3-1» y «4-1-4-1» son una forma; «4-4-2» y «4-2-2-2» otra.
    Con línea de tres/cinco las puntas no cuentan: «3-4-3», «3-4-2-1»,
    «3-4-1-2» y «5-4-1» son la misma línea de tres con carrileros (Riestra y
    La Serena, incidencia 734: el motivo «sistema» salía con 5-4-1 contra
    3-4-1-2)."""
    if len(cifras) < 3:
        return cifras
    linea = _linea(cifras[0])
    return linea if linea != "4" else linea + ("·2" if cifras[-1] == "2" else "·1/3")


def _linea(d: str) -> str:
    """Línea de cuatro contra línea de tres/cinco. Por la POSICIÓN de los
    titulares (sin formación en la ficha) un carrilero sale a veces como D y a
    veces como M: un 5-3-2 cuenta 3 o 5 defensores según la planilla, y eso
    no es un cambio de sistema; pasar de cuatro a tres/cinco sí lo es."""
    return "4" if d == "4" else "3/5"


def _plano(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]+", " ", t)


_PARTICULAS = {"de", "del", "la", "las", "los", "da", "do", "dos", "das", "van", "von", "di", "le"}


def _apellidos(nombre: str) -> list[str]:
    """Todo lo que puede ser apellido: sin iniciales ni partículas. Con dos
    apellidos la ficha y la referencia eligen distinto —«B. Gallego» contra
    «Baltasar Gallego Rodríguez» (Estudiantes–Flamengo, 16/10/2026)— y mirar
    solo el último dejaba al jugador fuera de la referencia."""
    partes = [p for p in _plano(nombre).split() if len(p) > 1 and p not in _PARTICULAS]
    return partes[1:] if len(partes) > 1 else partes


def _sz(t: str) -> str:
    """Seseo: «Quirós» y «Quiroz» son el mismo apellido escrito por dos
    fuentes (Atlas, 17/10/2026)."""
    return t.replace("z", "s")


def _casi(uno: str, otro: str) -> bool:
    """Una letra cambiada en un apellido largo (5+), tras igualar s/z."""
    uno, otro = _sz(uno), _sz(otro)
    if uno == otro:
        return True
    return (min(len(uno), len(otro)) >= 5 and len(uno) == len(otro)
            and sum(a != b for a, b in zip(uno, otro)) <= 1)


def _pila_en(nombre: str, ref: str) -> bool:
    """LA PRIMERA PALABRA TAMBIÉN NOMBRA. La API escribe a veces el apellido
    primero («Nunes Cesar» por C. Nunes) y la referencia nombra por el nombre
    de pila o el apodo de una palabra («Gabriel» por Gabriel Magalhães,
    «Otávio» por Otávio Eleodoro…): cuatro contraElOnce falsos del 18-19/10.
    Solo palabras de 5 letras o más, para no casar un «Juan» con otro."""
    partes = [p for p in _plano(nombre).split() if len(p) > 1 and p not in _PARTICULAS]
    return bool(partes) and len(partes[0]) >= 5 and f" {partes[0]} " in f" {ref} "


def _previas(nombre: str, crudo: str) -> list[str]:
    """Por cada mención de un apellido del jugador en el texto crudo, la
    palabra con mayúscula pegada antes (sin coma), saltando las del propio
    nombre: en «Alexis Mac Allister» la previa de Allister es «alexis», no
    «mac». '' si la mención va suelta («Rossano, Álvarez»)."""
    propias = set(_plano(nombre).split()[1:])   # el nombre de pila no se salta: es la previa que vale
    out = []
    for a in _apellidos(nombre):
        for m in re.finditer(r"(?:^|[\s,;:/(])([^\s,;:/()]+)", crudo or ""):
            if _plano(m.group(1)).strip() != a:
                continue
            fin, previa = m.start(1), ""
            while True:
                antes = re.search(r"([A-ZÁÉÍÓÚÑÜ][\wÀ-ÿ'’-]*\.?)\s+$", crudo[:fin])
                previa = _plano(antes.group(1)).strip() if antes else ""
                if previa and previa in propias and len(previa) > 1:
                    fin = antes.start(1)
                    continue
                break
            out.append("" if previa in _PARTICULAS else previa)
    return out


def _anclado(nombre: str, crudo: str) -> bool:
    """El texto nombra a ESTE jugador con su nombre o su inicial pegados al
    apellido («Carlos Álvarez», «C. Álvarez»)."""
    pila = (_plano(nombre).split() or [""])[0]
    return bool(pila) and any(p and (p == pila or (len(p) == 1 and p == pila[0])) for p in _previas(nombre, crudo))


def _inicial_choca(nombre: str, crudo: str, estricto: bool = False) -> bool:
    """LA INICIAL TAMBIÉN NOMBRA. El oficial «K. Álvarez» (lateral) no es el
    «Carlos Álvarez» (enganche) de la referencia (América, incidencia 390):
    casar solo por apellido lo daba por anunciado. Choca si el oficial trae
    inicial y TODA mención de su apellido en el texto va pegada (sin coma) a
    un nombre o inicial con otra letra. Sobre el texto crudo, porque en el
    plano «Rossano, Álvarez» y «Rossano Álvarez» se ven igual. `estricto`:
    otro titular con el mismo apellido está nombrado con su inicial en el
    texto, así que los «Álvarez» sueltos son suyos («Álvarez de enganche» era
    Carlos). Sin eso (dos Parra y un «Parra» suelto) no se sabe y casa."""
    partes = _plano(nombre).split()
    if len(partes) < 2 or len(partes[0]) != 1 or not crudo:
        return False
    previas = _previas(nombre, crudo)
    for p in previas:
        if p and p[0] == partes[0]:
            return False
        if not p and not estricto:
            return False
    # DOS NOMBRES DE PILA: «Víctor Felipe Méndez» es el «V. Méndez» del oficial
    # (Colo Colo, incidencia 607). La previa pegada es «Felipe»; la inicial
    # puede ser la de cualquier nombre de la cadena pegada al apellido.
    if previas and any(partes[0] in ini for ini in _iniciales_previas(nombre, crudo)):
        return False
    return bool(previas)


def _iniciales_previas(nombre: str, crudo: str):
    """Por cada mención del apellido, las iniciales de hasta tres palabras con
    mayúscula pegadas antes (sin coma), saltando las del propio nombre."""
    propias = set(_plano(nombre).split()[1:])
    for a in _apellidos(nombre):
        for m in re.finditer(r"(?:^|[\s,;:/(])([^\s,;:/()]+)", crudo or ""):
            if _plano(m.group(1)).strip() != a:
                continue
            fin, ini = m.start(1), set()
            for _ in range(4):
                antes = re.search(r"([A-ZÁÉÍÓÚÑÜ][\wÀ-ÿ'’-]*\.?)\s+$", crudo[:fin])
                if not antes:
                    break
                w = _plano(antes.group(1)).strip()
                fin = antes.start(1)
                if not w or w in propias or w in _PARTICULAS:
                    continue
                ini.add(w[0])
                if len(ini) >= 3:
                    break
            yield ini


def _en_referencia(nombre: str, ref: str, crudo: str = "", estricto: bool = False) -> bool:
    if _inicial_choca(nombre, crudo, estricto):
        return False
    if any(f" {a} " in f" {ref} " for a in _apellidos(nombre)):
        return True
    # la tolerancia de una letra no casa con el NOMBRE DE PILA de otro: «A.
    # Alfonzo» no es el «Alfonso» de «Alfonso Parot» (Limache, incidencia 713)
    pilas = {_plano(w).strip() for w in re.findall(
        r"(?:^|[,;:/(])\s*([A-ZÁÉÍÓÚÑÜ][\wÀ-ÿ'’-]+)\s+[A-ZÁÉÍÓÚÑÜ]", crudo or "")}
    palabras = [p for p in ref.split() if p not in pilas]
    return any(_casi(a, p) for a in _apellidos(nombre) for p in palabras)


_SIN_REF = re.compile(r"^\s*(sin|no hay|ninguno|n/?a\b)|sin (dato|xi|once|referencia)|no (hay|existe|tenemos) (xi|once)", re.I)


def sin_alternativas(texto: str) -> str:
    """El texto sin lo que va entre paréntesis o corchetes. «Kerkez (o
    Tsimikas)», «Barcola (o Gakpo/Ngumoha)»: una alternativa NO es el once
    anunciado. Liverpool (20/10/2026) salió con seis titulares fuera del XI de
    referencia y contraElOnce contó dos, porque daba por anunciado a cualquiera
    nombrado entre paréntesis en `senalXi` (incidencia 334)."""
    t = texto or ""
    for _ in range(3):   # paréntesis anidados
        t = re.sub(r"\([^()]*\)|\[[^\[\]]*\]", " ", t)
    # …y la alternativa SIN paréntesis: «B. Duarte o Villanueva» (Querétaro,
    # incidencia 260) anunciaba a los dos. Solo con mayúscula después de la «o»
    t = re.sub(r"\s[oóu]\s+(?:[A-ZÁÉÍÓÚÑÜ]\.\s*)?[A-ZÁÉÍÓÚÑÜ][\wÀ-ÿ'’-]*(?:\s+[A-ZÁÉÍÓÚÑÜ][\wÀ-ÿ'’-]*)?", " ", t)
    return t


# el punto de una inicial («por C. Fuentes») no corta la frase (incidencia 714)
_SALIENTES = re.compile(r"\b(?:por|en lugar de|en vez de|reemplaz\w*(?:\s+a)?|sale[n]?|salieron|fuera)\s+"
                        r"(?:(?<![\wÀ-ÿ])[A-ZÁÉÍÓÚÑÜ]\.|[^.;:()])+", re.I)


def sin_salientes(texto: str) -> str:
    """Lo que sale no es lo que se anuncia: «entraron Bambú y Meraz por Mora y
    Galindo» daba por anunciado a Mora, que salió titular (San Luis,
    incidencia 260). Se quita lo que viene detrás de «por», «en lugar de»,
    «sale(n)», «fuera»… hasta el signo que corta la frase."""
    return _SALIENTES.sub(" ", texto or "")


# «sin Lynen», «ausente Berge»: el jugador nombrado detrás NO sostiene el
# seguro. Solo con mayúscula después (un nombre), para no comerse «sin balón».
_AUSENTES = re.compile(r"\b(?i:sin|ausente[s]?|sin contar con|baja de)\s+(?:[A-ZÁÉÍÓÚÑÜ]\.\s*)?[A-ZÁÉÍÓÚÑÜ][\wÀ-ÿ'’-]*"
                       r"(?:\s+(?:y|ni)\s+(?:[A-ZÁÉÍÓÚÑÜ]\.\s*)?[A-ZÁÉÍÓÚÑÜ][\wÀ-ÿ'’-]*)*")


def sin_ausentes(texto: str) -> str:
    """Lo que el texto dice que NO está no es en quien se apoya: «Chuky San
    José y Reis; sin Lynen, depende de que un lateral se quede» marcaba el
    seguro de Werder Bremen sobre Lynen, que arrancó en el banco, y saltaba
    DTP-REHACER falso (incidencia 526, cuatro veces)."""
    return _AUSENTES.sub(" ", texto or "")


# «pueden volver», «podría entrar», «en duda»: lo que la señal da como POSIBLE
# no es el once anunciado
_DUDA = re.compile(r"\b(?:pued[ea]n?|podr[íi]an?|quiz[áa]s?|tal vez|posibles?|posiblemente|en duda|dudas?|"
                   r"a confirmar|sin confirmar|ser[íi]an?)\b", re.I)


def sin_dudas(texto: str) -> str:
    """La señal sin las frases que solo dan un regreso como posible. Angers
    (incidencia 651): «Lefort, Camara y Kalulu pueden volver a la zaga» los
    daba por anunciados; salieron los tres y DTP-REHACER no sonó aunque el M2
    se había escrito sobre la otra zaga. Se corta por frase (punto, punto y
    coma, dos puntos o salto de línea), no por coma: la coma separa nombres."""
    trozos = re.split(r"([.;:\n]+)", texto or "")   # los separadores quedan: `sin_salientes` corta en ellos
    return "".join(" " if i % 2 == 0 and _DUDA.search(t) else t for i, t in enumerate(trozos))


def sin_referencia(texto: str) -> bool:
    """La apertura dice que no hay XI de referencia (o no dice nada). Lo que va
    entre paréntesis es una nota, no el XI: «… (el undécimo titular no viene en
    la ficha: sin dato)» marcaba como sin referencia una lista de 10 nombres
    (Defensor–Racing, incidencia 527)."""
    limpio = re.sub(r"\([^()]*\)|\[[^\[\]]*\]", " ", texto or "")
    return not limpio.strip() or bool(_SIN_REF.search(limpio))


def oficial_de(fixture_id: int) -> dict:
    """El once que salió, por lado: formación y titulares. Vacío sin ficha."""
    fx = _fixture(fixture_id)
    if not fx:
        return {}
    fuera = {}
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        xi = _titulares(fixture_id, tid)
        if not xi:
            continue
        try:
            f = saddb.query_one("sad", "SELECT formacion FROM alineaciones WHERE fixture_id=? AND team_id=? "
                                       "AND formacion IS NOT NULL LIMIT 1", (fixture_id, tid))
        except Exception:  # noqa: BLE001
            f = None
        alias: dict[str, list[str]] = {}
        try:
            ids = [j["player_id"] for j in xi if j["player_id"] and j["player_id"] > 0]
            if ids:
                nombres = {r["id"]: r["nombre"] for r in saddb.query(
                    "sad", f"SELECT id, nombre FROM jugadores WHERE id IN ({','.join('?' * len(ids))})", tuple(ids))}
                for j in xi:
                    otro = nombres.get(j["player_id"])
                    if otro and otro != j["jugador"]:
                        alias[j["jugador"] or ""] = [otro]
        except Exception:  # noqa: BLE001 — base sin la capa de jugadores
            pass
        # CON EL GRID COMPLETO, LA LÍNEA DE ATRÁS ES LA FILA 2: la API etiqueta
        # «M» a carrileros y laterales que el grid pone en la línea (UCV, fila 2
        # con cuatro y defensoresOficiales=2, incidencia 137)
        con_grid = len(xi) >= 10 and all(str(j["grid"] or "").count(":") == 1 for j in xi)
        fuera[lado] = {"formacion": (f["formacion"] if f else "") or "",
                       "titulares": [j["jugador"] or "" for j in xi],
                       "banca": _banca(fixture_id, tid),
                       "alias": alias,
                       # el arquero titular: posición G, o la fila 1 del grid
                       "arquero": next((j["jugador"] or "" for j in xi if (j["posicion"] or "") == "G"
                                        or str(j["grid"] or "") == "1:1"), ""),
                       # la casilla de cada titular, para leer los roles contra el grid (646)
                       "casillas": _casillas(xi) if con_grid else [],
                       # sin formación en la ficha, la línea de atrás se cuenta
                       # por la posición de los titulares (D)
                       # …y un titular SIN posición en la fila 2 del grid también es
                       # defensor (I. Rodríguez, Central Español, 18/10/2026)
                       "defensores": (sum(1 for j in xi if str(j["grid"]).startswith("2:")) if con_grid else
                                      sum(1 for j in xi if (j["posicion"] or "") == "D"
                                          or (not j["posicion"] and str(j["grid"] or "").startswith("2:"))))}
    return fuera


def _casillas(xi: list[dict]) -> list[dict]:
    from backend.ficha_tactica import _carril
    por_fila: dict[int, int] = {}
    for j in xi:
        f = str(j["grid"]).split(":")[0]
        if f.isdigit():
            por_fila[int(f)] = por_fila.get(int(f), 0) + 1
    return [{"nombre": j["jugador"] or "", "grid": str(j["grid"]), "carril": _carril(str(j["grid"]), por_fila)}
            for j in xi]


# ── EL ROL DE LA APERTURA CONTRA LA CASILLA DEL GRID (incidencia 646) ────────
# Gray «de pivote» jugó de lateral (Chelsea–Tottenham), Castillo «de lateral
# izquierdo» de extremo derecho (Aucas–Barcelona), Velasco «interior, no de
# central» de central: con uno o dos cambios de rol el corte de ausentes no
# llega y el M2 queda escrito sobre otro equipo. Medido el 29/10/2026 sobre 315
# partes: 15 con una contradicción (≈ 1 por día), 11 sin DTP-REHACER; una o dos
# de cada quince pueden ser el grid de la API (516). Por eso nace EN SOMBRA:
# viaja en `contraElOnce.rolesVsGrid` y en la pantalla, NO pide rehacer. Se
# promueve (ROLES_GRID_REHACE) cuando los veredictos de una semana digan cuántas
# fueron reales. Solo la LÍNEA (defensa contra medio/ataque) y la BANDA de un
# lateral, carrilero o central: un extremo que cambia de banda es del partido.
ROLES_GRID_REHACE = False
_ROL = (r"doble pivote|pivote|mediocentro|medio centro|volante|interior|lateral|central|zaguero|defensor|libero|"
        r"carrilero|extremo|mediapunta|media punta|enganche|delantero|referencia|centrodelantero|nueve|9")
_CLASE_ROL = {"lateral": {"DEF"}, "central": {"DEF"}, "zaguero": {"DEF"}, "defensor": {"DEF"}, "libero": {"DEF"},
              "carrilero": {"DEF", "MED"}, "pivote": {"MED"}, "doble pivote": {"MED"}, "mediocentro": {"MED"},
              "medio centro": {"MED"}, "volante": {"MED", "ATQ"}, "interior": {"MED", "ATQ"},
              "extremo": {"MED", "ATQ"}, "mediapunta": {"MED", "ATQ"}, "media punta": {"MED", "ATQ"},
              "enganche": {"MED", "ATQ"},
              # un 9 en la fila de la mediapunta es frontera (falso 9): solo choca en la defensa
              "delantero": {"MED", "ATQ"}, "referencia": {"MED", "ATQ"}, "centrodelantero": {"MED", "ATQ"},
              "nueve": {"MED", "ATQ"}, "9": {"MED", "ATQ"}}


def _roles_declarados(linea: str) -> list[tuple[list[str], str, str]]:
    """[(nombres, rol, banda)] de una línea de `rolesReasignados`. Un rol
    condicional («si no está…», «según el once») o doble («lateral/extremo») no
    es una afirmación; «de 9 a volante» y «de central, juega de lateral» valen
    por el destino."""
    if re.search(r"\bsi\b|\bsegun\b|\bsegún\b|\bo\b|/", re.split(r"\bsiendo\b|\(", (linea or "").lower())[0]):
        return []
    t = _plano_num(linea)
    t = re.split(r"\bsiendo\b|\bcuando\b|\bes\b", t)[0]
    t = re.sub(r"\bde origen \w+|\bde oficio\b", " ", t)
    t = re.sub(rf"\bde ({_ROL})( (?:derecho|izquierdo))? a ", " de ", t)
    t = re.sub(rf"\bde ({_ROL})\s+juega de ", " de ", t)
    out = []
    for m in re.finditer(rf"([a-z0-9 ]+?)\s+de\s+({_ROL})\b(\s+(?:derecho|izquierdo|por la derecha|por la izquierda))?", t):
        nombres = [n.strip() for n in re.split(r"\s+y\s+|\s+con\s+", m.group(1).strip()) if n.strip()]
        if " con " in f" {m.group(1)} ":
            nombres = nombres[-1:]      # «X de extremo con Y de lateral»: Y es el del segundo rol
        banda = m.group(3) or ""
        out.append((nombres, m.group(2), "derecha" if "derech" in banda else ("izquierda" if "izquierd" in banda else "")))
    return out


def _plano_num(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def roles_vs_grid(bloque: dict, of: dict) -> list[dict]:
    casillas = of.get("casillas") or []
    if len(casillas) < 10:
        return []
    filas = [int(c["grid"].split(":")[0]) for c in casillas if c["grid"].split(":")[0].isdigit()]
    if not filas:
        return []
    n = max(filas)
    tres = (of.get("formacion") or "")[:1] in ("3", "5")
    out = []
    for linea in ((bloque.get("apertura") or {}).get("m1") or {}).get("rolesReasignados") or []:
        for nombres, rol, banda in _roles_declarados(linea):
            for nombre in nombres:
                palabras = [w for w in nombre.split() if len(w) > 2]
                if not palabras:
                    continue
                cands = [c for c in casillas if palabras[-1] in _plano_num(c["nombre"]).split()]
                pila = nombre.split()[0] if len(nombre.split()) > 1 else ""
                if pila and cands and _plano_num(cands[0]["nombre"]).split()[0][:1] != pila[:1]:
                    cands = []          # «Kevin Parra» no es «N. Parra»
                if len(cands) != 1:
                    continue
                c = cands[0]
                fila = int(c["grid"].split(":")[0])
                linea_grid = "GK" if fila == 1 else "DEF" if fila == 2 else "ATQ" if fila == n else "MED"
                acepta = set(_CLASE_ROL[rol]) | ({"MED"} if rol == "lateral" and tres else set())
                motivo = []
                if linea_grid not in acepta:
                    nombre_linea = {"GK": "el arco", "DEF": "la defensa", "MED": "el medio", "ATQ": "el ataque"}
                    motivo.append(f"la apertura lo pone de {rol} y el grid oficial, en {nombre_linea[linea_grid]} "
                                  f"({c['grid']})")
                if banda and rol in ("lateral", "carrilero", "central") and c.get("carril") in ("izquierda", "derecha") \
                        and c["carril"] != banda:
                    motivo.append(f"la apertura lo pone por la {banda} y el grid, por la {c['carril']}")
                if motivo:
                    out.append({"jugador": c["nombre"], "rol": linea, "grid": c["grid"], "motivo": "; ".join(motivo)})
    return out


def rehacer(bloque: dict, oficial: dict | None) -> dict | None:
    """Si el once oficial del equipo foco contradice la apertura. None = sin
    once oficial todavía (no se sabe); {"rehacer": False} = cuadra."""
    of = (oficial or {}).get(bloque.get("equipo") or "")
    if not of:
        return None
    m1 = (bloque.get("apertura") or {}).get("m1") or {}
    motivos = []
    decl, real = _sistemas(m1.get("sistema") or ""), _cifras_sistema(of.get("formacion") or "")
    # LO QUE CAMBIA EL MAPA DE DUELOS: la línea de atrás y si juega con dos
    # puntas. Comparar primera y última cifra daba «3-4-3» ≠ «3-4-2-1» y
    # «4-3-3» ≠ «4-2-3-1», que son el mismo equipo contado distinto
    # (Atlético-MG con «3-4-3 / 5-4-1», 17/10/2026).
    al_cerrar = _cifras_sistema(of.get("formacionAlCerrar") or "")
    nota_api = ""
    if decl and real and _forma(real) not in {_forma(d) for d in decl if d}:
        if al_cerrar and _forma(al_cerrar) in {_forma(d) for d in decl if d}:
            # cuadraba con la que la API daba al cerrar el once: la corrigió después.
            # IGUAL PIDE REHACER (incidencia 735, Chapecoense 4-2-3-1 → 4-4-2,
            # Alianza Valledupar 4-2-3-1 → 3-4-3): el M2 quedó escrito sobre
            # otra forma y, antes del pitazo, la rutina de rehacer todavía
            # llega. Si llegó tarde, `momento_rehacer` lo marca `tardio` y el
            # veredicto no se lo carga al skill (la 559 ya no hace falta).
            nota_api = (f"la API corrigió la formación después del cierre ({of['formacionAlCerrar']} → "
                        f"{of['formacion']}): la apertura cuadraba con el dato del momento")
            motivos.append(f"sistema: la apertura dice {m1.get('sistema')!r}, que cuadraba con el once al "
                           f"cerrar ({of['formacionAlCerrar']}), y la API lo corrigió a {of['formacion']}")
        else:
            motivos.append(f"sistema: la apertura dice {m1.get('sistema')!r} y salió {of['formacion']}")
    elif decl and not real and 3 <= (of.get("defensores") or 0) <= 5 \
            and _linea(str(of["defensores"])) not in {_linea(d[0]) for d in decl if d}:
        # LA FICHA SIN FORMACIÓN NO TAPA UN CAMBIO DE LÍNEA. Atlas jugó con
        # cuatro atrás contra una apertura de línea de cinco y no saltó nada
        # (17/10/2026): con las posiciones de los titulares se cuenta la línea
        # de atrás, que es lo que cambia el mapa de duelos por carril.
        motivos.append(f"sistema: la apertura dice {m1.get('sistema')!r} y el once oficial salió con "
                       f"{of['defensores']} defensores (la ficha no trae la formación)")
    crudo = sin_alternativas(m1.get("xiReferencia") or "")
    ref = _plano(crudo)
    ausentes = []
    # «SIN XI DE REFERENCIA» NO ES UN XI. La frase tenía 8+ palabras y pasaba por
    # lista de nombres: los 11 titulares oficiales salían «ausentes» y saltaba
    # DTP-REHACER en ligas sin onces (Rayo Zuliano, Puerto Cabello,
    # Estudiantes de Mérida, 18/10/2026). Sin referencia no hay contra qué comparar.
    sin_ref = sin_referencia(m1.get("xiReferencia") or "")
    if not sin_ref and len(ref.split()) >= 8:   # un XI de referencia escrito, no una frase
        # LO QUE LA APERTURA YA ANUNCIÓ NO ES SORPRESA: un cambio nombrado en
        # `senalXi` o en `rolesReasignados` (Villa, 17/10/2026) no cuenta; y el
        # nombre de la plantilla, que a veces trae el apodo («Abde»), también sirve
        anunciado_crudo = sin_salientes(sin_alternativas(" ".join([sin_dudas(m1.get("senalXi") or "")]
                                                                  + list(m1.get("rolesReasignados") or []))))
        anunciado = _plano(anunciado_crudo)
        alt = of.get("alias") or {}
        def _palabra_en(x: str, texto: str) -> bool:   # el apodo puede ser la primera palabra
            return any(len(t) > 2 and f" {t} " in f" {texto} " for t in _plano(x).split())

        def _homonimo(n: str, texto: str) -> bool:   # otro titular con su apellido, nombrado con inicial
            return any(t != n and set(_apellidos(t)) & set(_apellidos(n)) and _anclado(t, texto)
                       for t in of["titulares"])

        ausentes = [n for n in of["titulares"] if _apellidos(n)
                    and not any(_en_referencia(x, ref, crudo, _homonimo(n, crudo))
                                or (_pila_en(x, ref) and not _inicial_choca(x, crudo, _homonimo(n, crudo)))
                                or (anunciado and _en_referencia(x, anunciado, anunciado_crudo,
                                                                 _homonimo(n, anunciado_crudo)))
                                for x in [n, *alt.get(n, [])])
                    and not any(_palabra_en(x, ref) for x in alt.get(n, []))]
        if len(ausentes) >= REHACER_AUSENTES:
            motivos.append(f"once: {len(ausentes)} titulares que no estaban en el XI de referencia "
                           f"({', '.join(ausentes)})")
        # OTRO ARQUERO ES UN CAMBIO AUNQUE SEA EL ÚNICO (incidencia 648:
        # Independiente con Mele, Sassuolo con Turati; el B6 y el ensayo
        # siguieron con el de la referencia). Un ausente no llega al corte de
        # tres, pero el arquero cambia el B6 del EFE y la salida desde atrás.
        if of.get("arquero") and of["arquero"] in ausentes:
            motivos.append(f"arquero: {of['arquero']} ataja hoy y no estaba en el XI de referencia "
                           "(revisar el B6 del EFE y lo que dependía del arquero)")
    # EL SEGURO DE ATRÁS EN EL BANCO. Napoli (incidencia 152): la apertura
    # sostenía el rest defense «fijo en Lobotka» y Lobotka arrancó suplente;
    # con dos ausentes no saltaba nada. Si el texto del seguro nombra a un
    # jugador que está en la BANCA del once oficial (y a ningún titular con ese
    # apellido), el M2 se escribió sobre otra pieza.
    rd = ((bloque.get("apertura") or {}).get("m2") or {}).get("restDefense") or {}
    texto_rd = _plano(sin_ausentes(sin_alternativas(rd.get("foco") or "")))
    if texto_rd.strip():
        en_banca = _suplentes_nombrados(of.get("banca") or [], of["titulares"], texto_rd,
                                        sin_ausentes(sin_alternativas(rd.get("foco") or "")))
        if en_banca:
            motivos.append(f"seguro: el rest defense de la apertura se apoyaba en {', '.join(en_banca)}, "
                           "que arrancó en el banco")
    # LAS PIEZAS DEL M2 EN EL BANCO (DTP v1.5, incidencia 525): el mapa de
    # duelos se apoyaba en un jugador —propio o rival— que arrancó suplente.
    # Con las piezas declaradas no hace falta llegar al corte de ausentes.
    rival_lado = "b" if bloque.get("equipo") == "a" else "a"
    for pz in ((bloque.get("apertura") or {}).get("m2") or {}).get("piezas") or []:
        lado_of = (oficial or {}).get(bloque.get("equipo") if pz.get("lado") == "foco" else rival_lado)
        if not lado_of:
            continue
        # UNA PIEZA DECLARADA DESDE EL BANCO NO SE CAE POR ARRANCAR EN EL BANCO
        # (Barracas, incidencia 633: «ejecutor de penales desde el banco: R. Insúa»)
        if _DESDE_BANCO.search(f"{pz.get('rol') or ''} {pz.get('nombre') or ''}"):
            continue
        texto_pz = _plano(pz.get("nombre") or "")
        en_banca = _suplentes_nombrados(lado_of.get("banca") or [], lado_of.get("titulares") or [], texto_pz,
                                        pz.get("nombre") or "")
        quien = f"pieza del M2 ({'rival' if pz.get('lado') == 'rival' else 'propia'}" \
                f"{', ' + pz['rol'] if pz.get('rol') else ''})"
        if en_banca:
            motivos.append(f"{quien}: {', '.join(en_banca)} arrancó en el banco")
        # NI TITULAR NI SUPLENTE: fuera de la convocatoria tumba la capa de
        # nombres igual que el banco (Garcés, Paciência, Cuevas: incidencias
        # 690, 702, 708). Solo con la hoja completa (once y banco).
        elif _apellidos(pz.get("nombre") or "") and len(lado_of.get("titulares") or []) >= 10 \
                and lado_of.get("banca") and not any(
                    _en_referencia(x, texto_pz, pz.get("nombre") or "") or _en_referencia(pz.get("nombre") or "", _plano(x), x)
                    for x in [*(lado_of.get("titulares") or []), *(lado_of.get("banca") or [])]):
            motivos.append(f"{quien}: {pz.get('nombre')} no figura en la hoja del partido (ni titular ni suplente)")
    # el rol contra el grid (646): en sombra hasta medirlo con los veredictos
    roles_grid = roles_vs_grid(bloque, of)
    if ROLES_GRID_REHACE:
        motivos += [f"rol: {r['jugador']}: {r['motivo']}" for r in roles_grid]
    # UNA REFERENCIA CON VARIAS PROYECCIONES NO ES UN XI (Tigres, incidencia
    # 163: «SI proyecta a E. Gómez…; Milenio, a Herrera, Simeone…» y todos
    # pasaban por la referencia: cinco titulares nuevos y ni un ausente)
    mezclada = bool(re.search(r"proyect|seg[uú]n |otra fuente|o bien\b", m1.get("xiReferencia") or "", re.I))
    return {"rehacer": bool(motivos), "motivos": motivos, "sinReferencia": sin_ref,
            "referenciaMezclada": mezclada,
            "sistemaDeclarado": m1.get("sistema") or "", "sistemaOficial": of.get("formacion") or "",
            **({"formacionCorregidaPorLaApi": nota_api} if nota_api else {}),
            "defensoresOficiales": of.get("defensores"),
            # el nombre se presta a leerlo al revés: son los TITULARES OFICIALES
            # que no estaban en el XI de referencia, no los de la referencia que
            # faltaron en el once
            "ausentesDeLaReferencia": ausentes,
            # EN SOMBRA (646): el rol de `rolesReasignados` contra la casilla del grid
            "rolesVsGrid": roles_grid,
            "nota": ("`ausentesDeLaReferencia`: titulares del once OFICIAL que no figuraban en el XI de "
                     f"referencia de la apertura; con {REHACER_AUSENTES} o más, el bloque se rehace")}


def leer_dtp(dtp: dict, oficial: dict | None = None) -> dict:
    """Lo guardado + lo calculado al leer (la clase del bloque rival y, con el
    once oficial, si la apertura hay que rehacerla). Lo calculado no se
    guarda: una regla que cambia no deja copias viejas."""
    out = []
    for b in (dtp or {}).get("bloques") or []:
        clase = clasificar_bloque(b["apertura"]["m2"]["checklistBloqueRival"])
        rival = "b" if b["equipo"] == "a" else "a"
        calc = {"bloqueRival": {**clase, "equipoDelBloque": rival}}
        r = rehacer(b, oficial)
        if r is not None:
            calc["contraElOnce"] = r
        out.append({**b, "calculado": calc})
    return {"bloques": out}


def alertas_rehacer(dtp_leido: dict, nombres: dict) -> list[dict]:
    fuera = []
    for b in dtp_leido.get("bloques") or []:
        r = (b.get("calculado") or {}).get("contraElOnce") or {}
        # SIN XI DE REFERENCIA, LA COMPARACIÓN NO SE HIZO: se dice (Aston Villa–
        # Viking, incidencia 365: cuatro piezas cambiadas y ni una línea)
        if (r.get("sinReferencia") or r.get("referenciaMezclada")) and not r.get("rehacer"):
            quien = nombres.get(b["equipo"], b["equipo"])
            fuera.append({"codigo": "DTP-SIN-REFERENCIA", "equipo": b["equipo"], "tipo": "dato",
                          "detalle": (f"La apertura del DTP de {quien} no trae XI de referencia (`xiReferencia` "
                                      "vacío o «sin XI»): el once oficial no se pudo comparar con la apertura. "
                                      "Si el once probable iba en `senalXi`, pasarlo a `xiReferencia`; si cambió "
                                      "piezas del M2, rehacer el bloque."
                                      if r.get("sinReferencia") else
                                      f"El `xiReferencia` de {quien} mezcla varias proyecciones (cita fuentes): "
                                      "todos los nombrados cuentan como referencia y un titular nuevo no se ve. "
                                      "Un solo XI de 11 en `xiReferencia`; las otras proyecciones, en `senalXi`.")})
        if r.get("rehacer"):
            fuera.append({"codigo": "DTP-REHACER", "equipo": b["equipo"], "tipo": "dato",
                          "detalle": f"El once oficial de {nombres.get(b['equipo'], b['equipo'])} contradice "
                                     f"la apertura del DTP ({'; '.join(r['motivos'])}): el mapa de duelos "
                                     "(M2) y las vías de gol se escribieron sobre otro equipo. Rehacer M1/M2 "
                                     "con el once oficial antes del pitazo, o leerlo como apertura caída en "
                                     "la autopsia."})
    return fuera


_BANDA = re.compile(r"izq|der|lateral|banda|carril|extremo|wing", re.I)


def avisos_carril(dtp: dict, nombres: dict) -> list[dict]:
    """DTP v1.5 (cambio 5): los dos carriles de cada lado, con ida y vuelta.
    Avisos del recibo, sin rechazo: menos de dos duelos de banda en un bloque,
    o un duelo con mismatch y la vuelta vacía."""
    out = []
    for b in (dtp or {}).get("bloques") or []:
        quien = nombres.get(b["equipo"], b["equipo"])
        duelos = ((b.get("apertura") or {}).get("m2") or {}).get("duelosCarril") or []
        banda = [d for d in duelos if _BANDA.search(d.get("carril") or "")]
        if duelos and len(banda) < 2:
            out.append({"bloque": f"dtp.{b['equipo']}.m2.duelosCarril",
                        "costara": f"el M2 de {quien} escribe {len(banda)} carril(es) de banda: los fallos del "
                                   "21-24/10 vinieron del carril que no se escribió (Sporting–LASK, Lille–Galatasaray)",
                        "comoSeArregla": "los dos carriles de banda de cada lado, también el «parejo» (DTP v1.5)"})
        sin_vuelta = [d.get("carril") or "?" for d in duelos if d.get("mismatch") and not d.get("vuelta")]
        if sin_vuelta:
            out.append({"bloque": f"dtp.{b['equipo']}.m2.duelosCarril",
                        "costara": f"{quien}: duelo con mismatch sin `vuelta` en {', '.join(sin_vuelta)} — "
                                   "falta lo que expone ese carril si pierde la pelota",
                        "comoSeArregla": "llenar `vuelta` en cada duelo con mismatch (DTP v1.4-1.5)"})
    return out


_MOTIVO_SISTEMA = re.compile(r"anunci|previa|prensa|confirm|expuls|roja|con diez|con 10|variante|cambi|"
                             r"vuelve|regres|probable|rotaci|interino|declar|oficial|alineaci", re.I)
from backend.jugadores import dias_descanso as jug_dias_descanso  # noqa: E402

_PENAL = re.compile(r"penal|penalt", re.I)
_SIN_EJECUTOR = re.compile(r"sin ejecutor|ejecutor (?:no|sin) (?:confirmad|defin|conocid)|por jerarqu", re.I)
# (_ejecutores_en_base decide si «sin ejecutor» es un hueco o lo que la base dice)
_SEDE_TXT = {"visita": re.compile(r"visita|visitante|\bfuera\b", re.I),
             "local": re.compile(r"\bde local\b|\ben casa\b|\blocal\)|\(local", re.I)}


def _formacion_ultima(team_id: int, fecha: str) -> tuple[str, int | None]:
    ant = _anteriores(team_id, fecha, 1)
    if not ant:
        return "", None
    f = saddb.query_one("sad", "SELECT formacion FROM alineaciones WHERE fixture_id=? AND team_id=? "
                               "AND formacion IS NOT NULL AND formacion != '' LIMIT 1", (ant[0]["id"], team_id))
    return (f["formacion"] if f else "") or "", ant[0]["id"]


def avisos_v16(dtp: dict, fx, nombres: dict) -> list[dict]:
    """DTP v1.6, avisos del recibo (sin rechazo):
    · M1-VS-ULTIMO-ONCE (cambio 3): `m1.sistema` distinto de la formación del
      último once oficial del foco, sin motivo escrito en `senalXi` ni en el
      propio `sistema`;
    · el ejecutor de penales (cambio 4): `viasGol` de un bloque sin penal de
      los dos lados;
    · la sede del caso de la 6 (cambio 5): p6 del lado estructural y todos los
      casos con sede conocida del bloque rival son de la otra sede."""
    out = []
    if not fx:
        return out
    fecha = str(fx["date"])
    for b in (dtp or {}).get("bloques") or []:
        lado = b["equipo"]
        rival = "b" if lado == "a" else "a"
        quien = nombres.get(lado, lado)
        ap = b.get("apertura") or {}
        m1, m2 = ap.get("m1") or {}, ap.get("m2") or {}
        tid = fx["home_team_id"] if lado == "a" else fx["away_team_id"]
        tid_rival = fx["away_team_id"] if lado == "a" else fx["home_team_id"]
        decl = m1.get("sistema") or ""
        try:
            ultima, fid = _formacion_ultima(tid, fecha)
        except Exception:  # noqa: BLE001 — sin alineaciones en la base no hay contra qué comparar
            ultima, fid = "", None
        # EL ONCE OFICIAL DE HOY YA RESPONDE (incidencia 671, Carabobo–La Guaira y
        # Fluminense–Internacional: rehecho con el once del día, el aviso seguía
        # comparando contra el partido anterior)
        try:
            hoy = _cifras_sistema(((oficial_de(fx["id"]) or {}).get(lado) or {}).get("formacion") or "")
        except Exception:  # noqa: BLE001
            hoy = ""
        cuadra_hoy = bool(hoy) and _forma(hoy) in {_forma(d) for d in _sistemas(decl, True)}
        if _sistemas(decl) and _cifras_sistema(ultima) and _cifras_sistema(ultima) not in _sistemas(decl, True) \
                and not cuadra_hoy and not _MOTIVO_SISTEMA.search(f"{decl} {m1.get('senalXi') or ''}"):
            out.append({"bloque": f"dtp.{lado}.m1.sistema", "codigo": "M1-VS-ULTIMO-ONCE",
                        "costara": f"{quien}: la apertura dice «{decl}» y el último once oficial (fixture {fid}) "
                                   f"salió {ultima}, sin motivo escrito: los carriles del M2 pueden estar sobre "
                                   "otro equipo (Emelec, Aucas, Torque, Rennes el 25/10)",
                        "comoSeArregla": "tomar el sistema y los carriles del último once y su grid (insumos "
                                         "`partidoAnterior.xi`), o escribir en `senalXi` por qué se aparta "
                                         "(DTP v1.6)"})
        vias = m2.get("viasGol") or {}
        # «penal: sin ejecutor confirmado» nombra la vía, no al ejecutor (792, Palmeiras)…
        # …salvo que la base no tenga ningún penal de ese equipo en el año: ahí
        # «sin ejecutor» es justo lo que la nota de `penales` pide decir (802:
        # Varea, Numancia, Águilas cobrados por escribirlo)
        sin_base = {"foco": not _ejecutores_en_base(tid, fecha), "rival": not _ejecutores_en_base(tid_rival, fecha)}
        sin_penal = [q for q, k in (("propio", "foco"), ("del rival", "rival"))
                     if not any(_PENAL.search(v or "") and (sin_base[k] or not _SIN_EJECUTOR.search(v or ""))
                                for v in vias.get(k) or [])]
        if (vias.get("foco") or vias.get("rival")) and sin_penal:
            out.append({"bloque": f"dtp.{lado}.m2.viasGol", "codigo": "DTP-PENAL-SIN-EJECUTOR",
                        "costara": f"{quien}: las vías de gol no nombran al ejecutor de penales "
                                   f"{' ni '.join(sin_penal)} (seis partidos del 25/10 sin nombrarlo, y en los "
                                   "seis hubo penal)",
                        "comoSeArregla": "el ejecutor sale de `penales` en los insumos del DTP; «por jerarquía» "
                                         "no es fuente; sin penales en el año, decirlo así (DTP v1.6)"})
        chk = m2.get("checklistBloqueRival") or {}
        if chk.get("p6") == "der":
            sede_hoy = "visita" if rival == "b" else "local"
            try:
                casos = [c for c in casos_bloque(tid_rival, fecha) if c.get("sede") in ("local", "visita")]
            except Exception:  # noqa: BLE001
                casos = []
            # el caso escrito en `casoP6` de la misma sede responde la 6 aunque la
            # cadena no lo tenga (incidencia 721: Fiorentina 1-3 Como, de visita)
            caso_p6 = _txt(chk.get("casoP6"))
            if casos and all(c["sede"] != sede_hoy for c in casos) and not _SEDE_TXT[sede_hoy].search(caso_p6):
                # los casos de ESTA cadena con su fecha; el ejemplo fijo del 25/10
                # (Leones–Libertad, Lecce–Juventus) se leía como caso propio (721, 762)
                lista = "; ".join(f"{c.get('caso') or '?'} ({c['sede']}"
                                  + (f", {c['fecha']}" if c.get("fecha") else "") + ")" for c in casos[:3])
                out.append({"bloque": f"dtp.{lado}.m2.checklistBloqueRival.p6", "codigo": "P6-OTRA-SEDE",
                            "costara": f"la 6 del bloque de {nombres.get(rival, rival)} se respondió «sí» y hoy "
                                       f"juega de {sede_hoy}: los casos de su cadena son todos de la otra sede "
                                       f"({lista}) y `casoP6` no nombra uno de {sede_hoy}",
                            "comoSeArregla": "un caso de la otra sede no responde la 6: «no» o «sin dato» → "
                                             "estructural no probado, o nombrar en `casoP6` el partido de la "
                                             "misma sede que la responde (DTP v1.6)"})
    return out


def apertura_para_cadena(bloque: dict) -> dict:
    """Lo que se guarda en `cadena_dtp.apertura_json` para que el PRÓXIMO parte
    cierre contra esto (y no contra la memoria)."""
    ap = bloque["apertura"]
    return {"fuente": "cowork", "m1": ap["m1"], "m2": ap["m2"], "m3Fases": ap["m3Fases"], "m6": ap["m6"],
            "bloqueRival": clasificar_bloque(ap["m2"]["checklistBloqueRival"])}
