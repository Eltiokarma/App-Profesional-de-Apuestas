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
FICHAS_PAREJAS = 5          # onces capturados que se miran para «nunca juntos»
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


def _parejas_nuevas(team_id: int, fecha: str, xi: list[dict]) -> list[dict]:
    """Parejas de la MISMA línea del XI de referencia que no arrancaron juntas
    en ninguno de los onces capturados antes (minutos compartidos, v1.1; el
    `EJE-DEBUTANTE` del EFE). Es un proxy: mira titularidades en las fichas
    que hay, no minutos."""
    previos = []
    for f in _anteriores(team_id, fecha, FICHAS_PAREJAS + 1)[1:]:
        ids = {j["player_id"] for j in _titulares(f["id"], team_id) if j["player_id"]}
        if ids:
            previos.append(ids)
    if not previos:
        return []
    out = []
    for linea in ("D", "M"):
        de_linea = [j for j in xi if (j.get("posicion") or "") == linea and j.get("jugadorId")]
        for x, y in combinations(de_linea, 2):
            if not any(x["jugadorId"] in p and y["jugadorId"] in p for p in previos):
                out.append({"linea": "defensa" if linea == "D" else "medio",
                            "jugadores": [x["nombre"], y["nombre"]]})
    return out


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
        "diasDescanso": _dias(fecha, a["date"]),
        "partidoAnterior": anterior,
        "cambiosXi": cambios,
        "parejasNuevas": _parejas_nuevas(team_id, fecha, xi) if xi else [],
        "aperturaPrevia": _apertura_previa(nombre, a["id"]),
        # DTP v1.4: para responder la pregunta 6 sobre ESTE bloque (la apertura
        # del rival la lee de acá)
        "casosBloque": casos_bloque(team_id, fecha),
        "nivelDeDato": "C" if anterior["amistoso"] or not xi else "B",
        "faltan": faltan,
    }


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


def _suplentes_nombrados(banca: list[str], titulares: list[str], texto: str) -> list[str]:
    """Los de la banca que el texto nombra, sin los que el texto nombra por un
    titular. Un suplente que casa SOLO por la letra de tolerancia no cuenta si
    un titular casa exacto con esa palabra: Freiburg–Bayern (incidencia 605)
    nombraba a M. Ginter, titular, y la tolerancia lo casaba con C. Günter, del
    banco, y saltaba DTP-REHACER."""
    def exacto(n: str) -> set:
        return {a for a in _apellidos(n) if f" {a} " in f" {texto} "}
    tit_exactos = set().union(*(exacto(t) for t in titulares)) if titulares else set()
    out = []
    for n in banca:
        if not _apellidos(n) or not _en_referencia(n, texto):
            continue
        if any(_en_referencia(t, texto) and set(_apellidos(t)) & set(_apellidos(n)) for t in titulares):
            continue
        if not exacto(n) and any(_casi(a, w) for a in _apellidos(n) for w in tit_exactos):
            continue
        out.append(n)
    return out


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
            "linea": _txt(x.get("linea"))}


TIPOS_CASO = ("ventaja", "empate_que_sirve", "cero_cero")
REGIMENES = ("cualquiera", "persiguiendo")


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
                out.append({**b["cierre"]["casoBloque"], "deParte": f["fixture_id"], "fecha": (f["fecha"] or "")[:10]})
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
                   "razon": _txt(m2.get("razon"))},
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


def _sistemas(texto: str) -> set[str]:
    """TODOS los sistemas que nombra la apertura: «4-2-3-1 / 4-3-3» son dos
    opciones declaradas, y salir con cualquiera de ellas no contradice nada
    (Boca–Vasco, 15/10/2026: el aviso DTP-REHACER salía falso)."""
    return {re.sub(r"\D", "", m) for m in re.findall(r"\d(?:\s*[-–]\s*\d){2,4}", texto or "")}


def _forma(cifras: str) -> str:
    """Línea de atrás (4 · 3/5) y puntas (2 · 1/3): «4-3-3», «4-2-3-1» y
    «4-1-4-1» son una forma; «4-4-2» y «4-2-2-2» otra; «3-4-3», «3-4-2-1» y
    «5-4-1» otra."""
    if len(cifras) < 3:
        return cifras
    return _linea(cifras[0]) + ("·2" if cifras[-1] == "2" else "·1/3")


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
    return bool(previas)


def _en_referencia(nombre: str, ref: str, crudo: str = "", estricto: bool = False) -> bool:
    if _inicial_choca(nombre, crudo, estricto):
        return False
    if any(f" {a} " in f" {ref} " for a in _apellidos(nombre)):
        return True
    palabras = ref.split()
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


_SALIENTES = re.compile(r"\b(?:por|en lugar de|en vez de|reemplaz\w*(?:\s+a)?|sale[n]?|salieron|fuera)\s+"
                        r"[^.;:()]+", re.I)


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


def sin_referencia(texto: str) -> bool:
    """La apertura dice que no hay XI de referencia (o no dice nada)."""
    return not (texto or "").strip() or bool(_SIN_REF.search(texto))


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
                       # sin formación en la ficha, la línea de atrás se cuenta
                       # por la posición de los titulares (D)
                       # …y un titular SIN posición en la fila 2 del grid también es
                       # defensor (I. Rodríguez, Central Español, 18/10/2026)
                       "defensores": (sum(1 for j in xi if str(j["grid"]).startswith("2:")) if con_grid else
                                      sum(1 for j in xi if (j["posicion"] or "") == "D"
                                          or (not j["posicion"] and str(j["grid"] or "").startswith("2:"))))}
    return fuera


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
    if decl and real and _forma(real) not in {_forma(d) for d in decl if d}:
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
        anunciado_crudo = sin_salientes(sin_alternativas(" ".join([m1.get("senalXi") or ""]
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
    # EL SEGURO DE ATRÁS EN EL BANCO. Napoli (incidencia 152): la apertura
    # sostenía el rest defense «fijo en Lobotka» y Lobotka arrancó suplente;
    # con dos ausentes no saltaba nada. Si el texto del seguro nombra a un
    # jugador que está en la BANCA del once oficial (y a ningún titular con ese
    # apellido), el M2 se escribió sobre otra pieza.
    rd = ((bloque.get("apertura") or {}).get("m2") or {}).get("restDefense") or {}
    texto_rd = _plano(sin_ausentes(sin_alternativas(rd.get("foco") or "")))
    if texto_rd.strip():
        en_banca = _suplentes_nombrados(of.get("banca") or [], of["titulares"], texto_rd)
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
        texto_pz = _plano(pz.get("nombre") or "")
        en_banca = _suplentes_nombrados(lado_of.get("banca") or [], lado_of.get("titulares") or [], texto_pz)
        if en_banca:
            motivos.append(f"pieza del M2 ({'rival' if pz.get('lado') == 'rival' else 'propia'}"
                           f"{', ' + pz['rol'] if pz.get('rol') else ''}): {', '.join(en_banca)} arrancó en el banco")
    # UNA REFERENCIA CON VARIAS PROYECCIONES NO ES UN XI (Tigres, incidencia
    # 163: «SI proyecta a E. Gómez…; Milenio, a Herrera, Simeone…» y todos
    # pasaban por la referencia: cinco titulares nuevos y ni un ausente)
    mezclada = bool(re.search(r"proyect|seg[uú]n |otra fuente|o bien\b", m1.get("xiReferencia") or "", re.I))
    return {"rehacer": bool(motivos), "motivos": motivos, "sinReferencia": sin_ref,
            "referenciaMezclada": mezclada,
            "sistemaDeclarado": m1.get("sistema") or "", "sistemaOficial": of.get("formacion") or "",
            "defensoresOficiales": of.get("defensores"),
            # el nombre se presta a leerlo al revés: son los TITULARES OFICIALES
            # que no estaban en el XI de referencia, no los de la referencia que
            # faltaron en el once
            "ausentesDeLaReferencia": ausentes,
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


def apertura_para_cadena(bloque: dict) -> dict:
    """Lo que se guarda en `cadena_dtp.apertura_json` para que el PRÓXIMO parte
    cierre contra esto (y no contra la memoria)."""
    ap = bloque["apertura"]
    return {"fuente": "cowork", "m1": ap["m1"], "m2": ap["m2"], "m3Fases": ap["m3Fases"], "m6": ap["m6"],
            "bloqueRival": clasificar_bloque(ap["m2"]["checklistBloqueRival"])}
