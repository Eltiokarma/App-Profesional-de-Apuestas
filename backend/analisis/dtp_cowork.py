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

from datetime import datetime
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
        return saddb.query(
            "sad", "SELECT player_id, jugador, posicion FROM alineaciones "
                   "WHERE fixture_id=? AND team_id=? AND titular=1", (fixture_id, team_id))
    except Exception:  # noqa: BLE001 — DB anterior a la fase A del DTP
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
    cuadran = gf is not None and gc is not None and \
        sum(g["aFavor"] for g in goles) == gf and len(recibidos) == gc
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
            "m1": {"sistema": _txt(m1.get("sistema")), "xiReferencia": _txt(m1.get("xiReferencia")),
                   "senalXi": _txt(m1.get("senalXi")), "rolesReasignados": _lista_txt(m1.get("rolesReasignados")),
                   "vulnerabilidad": _txt(m1.get("vulnerabilidad")), "formaSinBalon": _txt(m1.get("formaSinBalon")),
                   "minutosCompartidos": _txt(m1.get("minutosCompartidos"))},
            "m2": {"choqueSistemas": _txt(m2.get("choqueSistemas")),
                   "duelosCarril": [{"carril": _txt(_dict(d).get("carril")), "duelo": _txt(_dict(d).get("duelo")),
                                     "mismatch": _txt(_dict(d).get("mismatch"))}
                                    for d in (m2.get("duelosCarril") or []) if _txt(_dict(d).get("duelo"))],
                   "checklistBloqueRival": {**{p: _col(chk.get(p)) for p in PREGUNTAS},
                                            "casoP6": _txt(chk.get("casoP6")), "notas": _txt(chk.get("notas"))},
                   "viasGol": {"foco": _lista_txt(vias.get("foco")), "rival": _lista_txt(vias.get("rival"))},
                   "restDefense": {"foco": _txt(rest.get("foco")), "rival": _txt(rest.get("rival")),
                                   "nivelFoco": _nivel_seguro(rest.get("nivelFoco")),
                                   "nivelRival": _nivel_seguro(rest.get("nivelRival"))},
                   "posesion": {"valor": _txt(pos.get("valor")), "contraQuien": _txt(pos.get("contraQuien")),
                                "marcador": _txt(pos.get("marcador")), "sede": _txt(pos.get("sede"))},
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
                                 if isinstance(mec.get("correccionEnVivo"), bool) else None},
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
            out[rival]["C1"] = {"valor": clase["c1Tde"], "de": f"checklist del DTP del lado {foco}: "
                                                               f"bloque {clase['clase']}"}
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
        bloques.append(_bloque(y, lado))
    return {"bloques": bloques} if bloques else {}


def leer_dtp(dtp: dict) -> dict:
    """Lo guardado + lo calculado al leer (la clase del bloque rival). Lo
    calculado no se guarda: una regla que cambia no deja copias viejas."""
    out = []
    for b in (dtp or {}).get("bloques") or []:
        clase = clasificar_bloque(b["apertura"]["m2"]["checklistBloqueRival"])
        rival = "b" if b["equipo"] == "a" else "a"
        out.append({**b, "calculado": {"bloqueRival": {**clase, "equipoDelBloque": rival}}})
    return {"bloques": out}


def apertura_para_cadena(bloque: dict) -> dict:
    """Lo que se guarda en `cadena_dtp.apertura_json` para que el PRÓXIMO parte
    cierre contra esto (y no contra la memoria)."""
    ap = bloque["apertura"]
    return {"fuente": "cowork", "m1": ap["m1"], "m2": ap["m2"], "m3Fases": ap["m3Fases"], "m6": ap["m6"],
            "bloqueRival": clasificar_bloque(ap["m2"]["checklistBloqueRival"])}
