"""Los insumos del Teorema del Echado que SALEN DE NUESTRA BASE.

Esto no calcula el IE. Calcula lo que el propio skill declara que **tiene** que
venir del motor y que hasta ahora se le estaba pidiendo a Cowork que escribiera
a mano:

- **P1a** (rol de protector del resultado) es «input inviolable»: sale de
  comparar los dos `μ_partido` contra el umbral de 0.30. El skill prohíbe
  expresamente derivarlo del gap o corregirlo por localía a mano.
- **F2** (descanso y calendario) es «dato del motor o no es dato»
  (Disciplina 21): sin salida de Regresión al Nivel, el bloque F entero se
  declara sin dato.
- **F1** (rotación en los últimos 3 partidos) sale de las alineaciones que ya
  ingestamos — y la ingesta captura justo 3 fichas por equipo, que es
  exactamente la ventana que F1 mira.

Todo lo demás del TDE es lectura táctica o investigación y se queda donde está:
lo escribe quien analiza. Por eso la respuesta trae `noCalculables`, con el
motivo de cada uno: un insumo que falta tiene que verse, no adivinarse.
"""
from datetime import datetime

from backend import db as saddb
from backend.nombres import normalizar  # noqa: F401  (paridad con el resto de la capa)

LADOS = ("a", "b")

# el umbral del skill para separar «hay protector» de «están parejos». No es
# nuestro: vive en references/INDICE_IE.md y aquí solo se aplica.
UMBRAL_PROTECTOR = 0.30
VENTANA_F1 = 3          # partidos que mira F1
_FIN = "(status_short IN ('FT','AET','PEN') OR status_long='Match Finished')"


def _fixture(fixture_id: int):
    return saddb.query_one(
        "sad",
        "SELECT f.id, f.date, f.league_id, f.home_team_id, f.away_team_id, "
        "ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
        "JOIN teams at ON at.id=f.away_team_id WHERE f.id=?",
        (fixture_id,),
    )


# ── F1 · rotación en los últimos 3 ──────────────────────────────────────────

def _onces_previos(team_id: int, fecha: str, cuantos: int = VENTANA_F1) -> list[dict]:
    """Los últimos onces titulares ANTES de esta fecha, del más nuevo al más viejo."""
    filas = saddb.query(
        "sad",
        f"""SELECT f.id, f.date FROM fixtures f
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.date < ? AND {_FIN}
            ORDER BY f.date DESC LIMIT ?""",
        (team_id, team_id, fecha, cuantos),
    )
    onces = []
    for f in filas:
        jug = saddb.query(
            "sad",
            "SELECT player_id, jugador FROM alineaciones "
            "WHERE fixture_id=? AND team_id=? AND titular=1",
            (f["id"], team_id),
        )
        if not jug:
            continue  # ficha no capturada: no se inventa un once
        onces.append({
            "fixtureId": f["id"], "fecha": str(f["date"])[:10],
            # el player_id es la clave buena; el nombre solo para poder leerlo
            "ids": {j["player_id"] for j in jug if j["player_id"]},
            "nombres": [j["jugador"] for j in jug],
        })
    return onces


def f1_rotacion(team_id: int, fecha: str) -> dict:
    """Cuánto rotó el equipo en sus últimos 3 partidos.

    La rúbrica del skill es al revés de lo que sugiere la intuición: **0 rotados
    puntúa 1** (mismo once siempre = carga acumulada = más riesgo de echada) y
    3+ rotados puntúa 0. Aquí solo se cuenta; el sentido lo pone la rúbrica.
    """
    onces = _onces_previos(team_id, fecha)
    base = {"partidosMirados": len(onces), "ventana": VENTANA_F1,
            "definicion": "cambios de titulares entre onces consecutivos, promediados; "
                          "núcleo fijo = los que arrancaron en TODOS los partidos mirados"}
    if len(onces) < 2:
        return {**base, "sinDato": True,
                "porque": ("no hay dos onces titulares capturados antes de este partido: "
                           "la ficha se ingesta solo de los últimos partidos y aquí faltan"),
                "comoSeArregla": "corré `python -m backend.ingesta.ficha_partido`"}
    # los onces vienen del más nuevo al más viejo; los cambios se cuentan entre pares
    cambios = []
    for nuevo, viejo in zip(onces, onces[1:]):
        if not nuevo["ids"] or not viejo["ids"]:
            continue
        cambios.append(len(nuevo["ids"] - viejo["ids"]))
    if not cambios:
        return {**base, "sinDato": True,
                "porque": "las alineaciones capturadas no traen player_id: no se pueden cruzar"}
    prom = sum(cambios) / len(cambios)
    nucleo = set.intersection(*[o["ids"] for o in onces if o["ids"]])
    score = 1.0 if prom < 0.5 else (0.5 if prom < 3 else 0.0)
    return {
        **base,
        "cambiosPorFecha": cambios,
        "rotadosPromedio": round(prom, 2),
        "nucleoFijo": len(nucleo),
        "score": score,
        "lectura": ("mismo once: carga acumulada" if score == 1.0 else
                    "rotación parcial" if score == 0.5 else "rotación amplia: piernas frescas"),
        "onces": [{"fixtureId": o["fixtureId"], "fecha": o["fecha"], "titulares": len(o["ids"])}
                  for o in onces],
    }


# ── F2 · descanso y calendario, «dato del motor o no es dato» ────────────────

def f2_calendario(team_id: int, fecha: str, contexto: dict) -> dict:
    """Descanso antes, exigencia después. Lo que el motor ya sabe.

    El viaje y la altitud NO están en nuestra base, y son parte de la rúbrica:
    por eso esto devuelve un PISO y dice qué podría subirlo. Un score cerrado
    aquí sería inventar la mitad que falta.
    """
    from backend import jugadores as jug
    cong = jug._congestion(team_id, fecha)
    dias = cong.get("diasDescanso")
    senal = contexto.get("senalCalendario") or ""
    if dias is None:
        piso, porque = None, "no hay partido anterior en nuestra base: descanso desconocido"
    elif dias <= 3:
        piso, porque = 1.0, f"{dias} días de descanso (≤3 es el tramo alto de la rúbrica)"
    elif dias <= 5:
        piso, porque = 0.5, f"{dias} días de descanso (4-5 es el tramo medio)"
    elif senal == "duro":
        piso, porque = 0.5, f"{dias} días de descanso, pero el próximo viene marcado duro"
    else:
        piso, porque = 0.0, f"{dias} días de descanso y el próximo no aprieta"
    return {
        "diasDescanso": dias,
        "partidos21d": cong.get("partidos21d"),
        "senalCalendario": senal,
        "recuperabilidad": contexto.get("recuperabilidad"),
        "proximos": contexto.get("proximos") or [],
        "scorePiso": piso,
        "porque": porque,
        "puedeSubir": "viaje largo, cambio de altitud o calor extremo — NO están en nuestra "
                      "base y son parte de la rúbrica F2: si los hay, súbelo a mano",
    }


# ── P1a · el input inviolable ───────────────────────────────────────────────

def _amistosos_en_la_forma(team_id: int, fecha: str, cuantos: int = 5) -> dict:
    """La prohibición 3 del backtest: que la tira de 5 no sean amistosos."""
    filas = saddb.query(
        "sad",
        f"""SELECT l.name AS liga FROM fixtures f JOIN leagues l ON l.id=f.league_id
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.date < ? AND {_FIN}
            ORDER BY f.date DESC LIMIT ?""",
        (team_id, team_id, fecha, cuantos),
    )
    nombres = [str(f["liga"] or "") for f in filas]
    amistosos = [n for n in nombres if "friendl" in n.lower() or "amistoso" in n.lower()]
    return {"mirados": len(nombres), "amistosos": len(amistosos), "ligas": nombres}


def p1a_protector(mu_a, mu_b, forma_a: dict, forma_b: dict) -> dict:
    """Quién tiene algo que proteger, por μ del partido y nada más.

    El skill lo llama input inviolable y prohíbe dos atajos: derivarlo del gap
    (o del gap diferencial) y corregir μ por localía a mano. Las dos cosas se
    respetan aquí simplemente no haciéndolas: μ ya trae la localía dentro.
    """
    if mu_a is None or mu_b is None:
        return {"sinDato": True,
                "porque": "sin μ del partido no hay P1a, y sin P1a el bloque P se topa en 0.5 "
                          "por la compuerta 1"}
    margen = round(abs(mu_a - mu_b), 4)
    favorito = "a" if mu_a > mu_b else ("b" if mu_b > mu_a else "")
    if margen > UMBRAL_PROTECTOR and favorito:
        score = {favorito: 1.0, ("b" if favorito == "a" else "a"): 0.0}
        lectura = f"protector claro: {favorito} por {margen:.2f} sobre el umbral de {UMBRAL_PROTECTOR}"
    else:
        score = {"a": 0.5, "b": 0.5}
        lectura = (f"parejos: {margen:.2f} dentro del umbral de {UMBRAL_PROTECTOR}; "
                   "ningún protector declarado")
    avisos = []
    for lado, f in (("a", forma_a), ("b", forma_b)):
        if f.get("amistosos"):
            avisos.append(f"lado {lado}: {f['amistosos']} de {f['mirados']} partidos de la forma "
                          "son amistosos — el skill prohíbe puntuar P con esa tira")
    return {
        "muPartido": {"a": mu_a, "b": mu_b},
        "margen": margen,
        "umbral": UMBRAL_PROTECTOR,
        "favorito": favorito,
        "score": score,
        "modo": "PRE",
        "lectura": lectura,
        "formaMirada": {"a": forma_a, "b": forma_b},
        "avisos": avisos,
        "puedeBajar": "«necesita ganar» lleva P1a a 0 y eso NO sale de la base: si el equipo "
                      "está obligado por tabla o por torneo, bajalo a mano",
        "compuerta1": "si P1a queda en 0, el bloque P entero se topa en 0.5",
    }


# ── lo que el backend NO puede poner, y por qué ─────────────────────────────

NO_CALCULABLES = [
    {"indicador": "F3", "porque": "pide impacto documentado desde el banco en la temporada "
                                  "en curso; la ficha se ingesta solo de los últimos partidos"},
    {"indicador": "F4", "porque": "costo energético del modelo: pide PPDA o tracking, que no "
                                  "tenemos ni podemos derivar de las stats por partido"},
    {"indicador": "C1", "porque": "bloque bajo ENSAYADO y probado bajo presión; la formación "
                                  "dominante es un proxy débil y la clase «no probado» sale "
                                  "del checklist del DTP"},
    {"indicador": "C2", "porque": "coordinación línea-volantes: lectura táctica"},
    {"indicador": "C3", "porque": "ventajas de un gol sostenidas en la temporada; haría falta "
                                  "la ficha de eventos de toda la temporada, no de los últimos"},
    {"indicador": "P1b", "porque": "coste percibido de perder: juicio de contexto"},
    {"indicador": "P1c", "porque": "riesgo de descenso Y de cese; falta la tabla de promedios "
                                   "y un criterio de cese que no sea retrospectivo"},
    {"indicador": "P2", "porque": "D3 del EFE: lo escribe quien puntúa la rúbrica"},
    {"indicador": "P3", "porque": "relevancia asimétrica: juicio"},
    {"indicador": "P4", "porque": "contexto extra-cancha: es investigación, no cálculo"},
    {"indicador": "S1", "porque": "faltas por partido y jugadores al límite SÍ están en bruto, "
                                  "pero nadie los agrega todavía"},
    {"indicador": "S2", "porque": "patrón de cambios defensivos del DT: los cambios con minuto "
                                  "están en bruto, falta clasificar el perfil del que entra"},
    {"indicador": "S3", "porque": "si el rival supera la primera línea: pide PPDA"},
    {"indicador": "SOB1", "porque": "obligación de ir a buscarlo: mismo material que P1c"},
    {"indicador": "SOB2", "porque": "rest defense; se hereda del M2 del DTP"},
    {"indicador": "SOB3", "porque": "transición del rival: lectura del DTP"},
]


def ficha(fixture_id: int) -> dict | None:
    """Todo lo del TDE que sale de nuestra base, con lo que falta declarado."""
    fx = _fixture(fixture_id)
    if not fx:
        return None
    from backend import app as sad          # tardío: app importa esta capa

    fecha = sad.iso(fx["date"])
    ctx = {}
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        g = sad.gap_equipo(tid, fecha)
        g.update(sad.contexto_calendario(tid, fx, g))
        ctx[lado] = g

    p1a = p1a_protector(
        ctx["a"].get("muPartido"), ctx["b"].get("muPartido"),
        _amistosos_en_la_forma(fx["home_team_id"], fecha),
        _amistosos_en_la_forma(fx["away_team_id"], fecha),
    )
    f1 = {l: f1_rotacion(t, fecha) for l, t in
          (("a", fx["home_team_id"]), ("b", fx["away_team_id"]))}
    f2 = {l: f2_calendario(t, fecha, ctx[l]) for l, t in
          (("a", fx["home_team_id"]), ("b", fx["away_team_id"]))}

    # NIVEL DE DATO, declarado. El skill pide A/B/C y el A es imposible para
    # nosotros: no hay tracking. Decirlo es más honesto que dejar el campo.
    con_once = all(not f1[l].get("sinDato") for l in LADOS)
    nivel_dato = "B" if con_once else "C"
    return {
        "fixtureId": fixture_id,
        "partido": {"equipoA": fx["home_name"], "equipoB": fx["away_name"],
                    "fecha": (fx["date"] or "")[:10]},
        "p1a": p1a,
        "f1": f1,
        "f2": f2,
        "fiabilidadMu": sad.fiabilidad_mu(fx["league_id"]),
        "nivelDeDato": nivel_dato,
        "notaNivelDeDato": ("nivel A (tracking: altura de línea, PPDA, distancia entre líneas) "
                            "es imposible con nuestras fuentes; esto es lo que hay"
                            + ("" if con_once else " — y sin onces capturados baja a C")),
        "noCalculables": NO_CALCULABLES,
        "nota": "esto NO es el IE. Son los insumos que el skill manda tomar del motor "
                "(P1a es input inviolable; F2 es dato del motor o no es dato) más F1, "
                "que sale de las alineaciones ya ingestadas. El resto lo escribe quien analiza.",
    }


# ── la aritmética del IE y del ISE ──────────────────────────────────────────
# La fórmula se verificó contra el registro del skill: reproduce 30 de 33 casos
# con ≤0.06 de diferencia. Los tres que desvían (TDE-001, 003, 004) son los más
# viejos y los tres son `por_resultado`, de antes de que el esquema se asentara.
# Calcular esto en el backend no es una opinión sobre el método: es quitarle al
# que analiza una cuenta que se puede equivocar y unas compuertas que se pueden
# olvidar.

PESOS_BLOQUE = {"F": 3.0, "C": 2.0, "P": 2.0, "S": 1.5}
DIVISOR_IE = 8.5
# esquema 6: es el que declara el propio registro de casos (columna `esquema_P`,
# con su columna `IE_recomputado_esquema6` para reexpresar los viejos). La línea
# de SKILL.md que dice «P tiene 5 desde v0.1.1» quedó vieja cuando entró P1c.
INDICADORES = {
    "F": ("F1", "F2", "F3", "F4"),
    "C": ("C1", "C2", "C3"),
    "P": ("P1a", "P1b", "P1c", "P2", "P3", "P4"),
    "S": ("S1", "S2", "S3"),
}
INDICADORES_ISE = ("SOB1", "SOB2", "SOB3")

BANDAS_ECHADA = ((3.0, 10, 25), (5.0, 25, 45), (7.0, 45, 70), (99.0, 70, 90))
BANDAS_SOBRE = ((3.0, 10, 25), (5.0, 25, 45), (7.0, 45, 70), (99.0, 70, 90))

# Lo que el registro observó de verdad. Viaja con el índice a propósito: el
# propio skill declara su escala sobreestimada (disciplina 20) y un 5.0 leído
# como «55%» es el error que esto evita.
#
# SE CALCULÓ MAL UNA VEZ. La primera versión promedió los 21 casos ciegos y
# cerrados SIN excluir los `rama_abandonada`, que las disciplinas 24, 27 y 31
# sacan de toda métrica de frecuencia. Uno de los dos «positivos» era TDE-030,
# cuya propia lección dice «Excluida de toda metrica de frecuencia» y cuyo
# se_echo es «repliegue voluntario sostenido desde el 25» — que por la
# definición del skill no es una echada sino un bloque bajo ejecutado. Con el
# filtro puesto el resultado no se suaviza: se endurece.
#
# Se recalcula con `python3 scripts/calibrar-tde.py`, que además compara contra
# estos números y falla si se desalinean. Un número de calibración escrito a
# mano se vuelve a equivocar.
CALIBRACION = {
    "filtro": "ciega + PRE + cerrado, EXCLUYENDO clase_caso=rama_abandonada "
              "(disciplinas 24, 27 y 31)",
    "casosComputables": 17,
    "seEcharon": 1,
    "tasaObservada": 5.9,
    "ieMedio": 4.85,
    "porBanda": {"3-5": {"n": 11, "positivos": 1}, "5-7": {"n": 4, "positivos": 0},
                 "7-8.5": {"n": 2, "positivos": 0}},
    "positivosEnEsquemaVigente": 0,
    "brier": 0.2292,
    "brierTasaBase": 0.0554,
    "pMediaDeclarada": 43.3,
    "brierNota": "el 0.247 que citaba el skill se recalculó con el filtro puesto y da 0.2292 "
                 "sobre 17 casos. Lo importante no es el número suelto: predecir SIEMPRE la "
                 "tasa base saca 0.0554, así que hoy las probabilidades del módulo restan en "
                 "vez de sumar. Lo ROBUSTO de esto es la brecha —43.3% declarado contra 5.9% "
                 "observado, unas siete veces—; el skill score con un solo positivo es ruidoso.",
    "nota": "la escala del IE NO ordena el riesgo hoy: el único positivo ciego computable "
            "(TDE-005) cae en la banda MÁS BAJA y las dos bandas altas tienen cero. Y está "
            "medido con el esquema viejo de 4 indicadores, así que en el esquema vigente de "
            "6 no hay ni un positivo. La banda que el IE anuncia no es la frecuencia con "
            "que pasó.",
    "registro": "docs/skills/teorema-del-echado/assets/casos/registro.csv, 35 filas "
                "(TDE-001…048), en la versión CANONIZADA que mandó el autor del skill: "
                "clase_caso ∈ {normal, rama_abandonada}, esquema_P ∈ {4ind, 4ind_o_5ind, "
                "6ind} y se_echo ∈ {si, no, parcial}, con el detalle de las dos echadas "
                "largas conservado en `tipo_real`. Ninguna columna de números ni de "
                "lecciones se tocó (disciplina 15).",
}

# Cuándo se puede poner semáforo. Las tres a la vez, y la (c) es la que hace el
# trabajo: sin ella, dentro de tres casos alguien cumple (a) y (b) mezclando
# reglas de puntuación distintas.
ALTA_DEL_SEMAFORO = {
    "a": "N ≥ 5 echadas observadas con selección ciega (el mismo umbral binding que "
         "gobierna la revisión de pesos, CALIBRACION.md y disciplina 22)",
    "b": "al menos 2 de esos positivos FUERA de la banda 3-5: un semáforo afirma "
         "ordenamiento, y un ordenamiento sin positivos arriba no es testeable",
    "c": "todos los positivos expresados en el esquema vigente de 6 indicadores",
    "hoy": "1 positivo ciego computable, en esquema de 4 → (a) no, (b) no, (c) no",
}


def _banda(valor: float, tabla) -> dict:
    for tope, lo, hi in tabla:
        if valor < tope:
            return {"min": lo, "max": hi, "texto": f"{lo}-{hi}%"}
    return {"min": 70, "max": 90, "texto": "70-90%"}


def _promedio(ind: dict, claves) -> tuple[float | None, list[str]]:
    vals = [ind[k] for k in claves if ind.get(k) is not None]
    return (sum(vals) / len(vals), [k for k in claves if ind.get(k) is not None]) if vals else (None, [])


def indice(ind: dict) -> dict:
    """IE, ISE y sus bandas, con TODAS las compuertas declaradas.

    `ind` trae los indicadores en 0 / 0.5 / 1 (o ausentes si no hay dato). Lo
    que devuelve no es solo el número: es qué compuerta operó y sobre qué, que
    el skill obliga a declarar aunque no cambie el resultado.
    """
    ind = {k: (None if v is None else float(v)) for k, v in (ind or {}).items()}
    operadas: list[str] = []

    # Disciplina 21: F2 es dato del motor o el bloque F entero es sin dato.
    if ind.get("F2") is None:
        return {"sinDato": True, "bloque": "F",
                "porque": "F2 (descanso y calendario) no tiene dato del motor, y el skill "
                          "manda declarar el bloque F entero sin dato (Disciplina 21)",
                "comoSeArregla": "GET /analisis/cowork/tde/{fixtureId} trae F2 calculado",
                "calibracion": CALIBRACION}

    # COMPUERTA 2 — C1 sobre S2: S2 solo puede valer 1 con repliegue documentado
    if ind.get("C1") is not None and ind["C1"] < 1 and (ind.get("S2") or 0) > 0.5:
        ind["S2"] = 0.5
        operadas.append("compuerta 2 (C1<1 → S2 topado en 0.5)")
    # regla n/a de S3: bloque medio o bajo por diseño
    claves_s = INDICADORES["S"]
    if ind.get("F4") == 0 and ind.get("C1") == 0:
        claves_s = ("S1", "S2")
        operadas.append("S3 marcado n/a (F4=0 ∧ C1=0): S promedia solo S1 y S2")

    bloques, usados = {}, {}
    for letra in ("F", "C", "P"):
        bloques[letra], usados[letra] = _promedio(ind, INDICADORES[letra])
    bloques["S"], usados["S"] = _promedio(ind, claves_s)

    # regla especial F
    if ind.get("F1") == 1 and ind.get("F3") == 1 and bloques["F"] is not None and bloques["F"] < 0.75:
        bloques["F"] = 0.75
        operadas.append("regla especial F (F1=1 ∧ F3=1 → F ≥ 0.75)")
    # tope del bloque C
    if ind.get("C3") == 1 and bloques["C"] is not None and bloques["C"] < 0.60:
        bloques["C"] = 0.60
        operadas.append("tope del bloque C (C3=1 → C ≥ 0.60)")
    # COMPUERTA 1 — sin protector no hay echada psicológica. El tope se aplica
    # DESPUÉS del promedio, nunca antes: si no, el 0 de P1a entra dos veces.
    if ind.get("P1a") == 0 and bloques["P"] is not None and bloques["P"] > 0.5:
        bloques["P"] = 0.5
        operadas.append("compuerta 1 (P1a=0 → bloque P topado en 0.5, después del promedio)")
    # DENOMINADOR VARIABLE DEL BLOQUE P. `P1a` ausente no es lo mismo que `P1a`
    # en 0: sin salida del motor se declara sin dato y P se promedia sobre
    # CINCO. `_promedio` ya lo hace —solo cuenta los presentes— pero el caso se
    # declara, porque dividir cinco términos entre seis es el error silencioso
    # que esta regla existe para evitar.
    if ind.get("P1a") is None and usados["P"]:
        operadas.append(f"P1a sin dato del motor: bloque P promediado sobre "
                        f"{len(usados['P'])}, no sobre {len(INDICADORES['P'])}")

    faltan = [l for l in ("F", "C", "P", "S") if bloques[l] is None]
    if faltan:
        return {"sinDato": True, "bloques": bloques,
                "porque": f"sin ningún indicador en el bloque {', '.join(faltan)}",
                "compuertasOperadas": operadas, "calibracion": CALIBRACION}

    ie = sum(bloques[l] * PESOS_BLOQUE[l] for l in PESOS_BLOQUE) / DIVISOR_IE * 10
    ise, usados_ise = _promedio(ind, INDICADORES_ISE)
    out = {
        "ie": round(ie, 2),
        "bloques": {l: round(v, 4) for l, v in bloques.items()},
        "indicadoresUsados": usados,
        "pEchada": _banda(ie, BANDAS_ECHADA),
        "compuertasOperadas": operadas,
        "formula": "IE = (F·3 + C·2 + P·2 + S·1.5) / 8.5 × 10",
        "esquemaP": "6 indicadores (P1a, P1b, P1c, P2, P3, P4)",
        "calibracion": CALIBRACION,
        # el skill pide el máximo de las dos vías, nunca la suma
        "riesgo": {"regla": "el riesgo del tramo final es el MÁXIMO de las dos vías, "
                            "nunca la suma"},
    }
    if ise is None:
        out["ise"] = None
        out["iseNota"] = ("sin SOB1/SOB2/SOB3 no hay ISE, y el skill manda emitirlo SIEMPRE "
                          "—sobre todo con IE bajo—: el riesgo puede estar en la otra vía")
    else:
        ise_v = round(ise * 10, 2)
        out["ise"] = ise_v
        out["iseIndicadores"] = usados_ise
        out["pSobreexposicion"] = _banda(ise_v, BANDAS_SOBRE)
        out["riesgo"]["via"] = "echada" if out["ie"] >= ise_v else "sobreexposicion"
        out["riesgo"]["maximo"] = max(out["ie"], ise_v)
        if out["ie"] >= 5 and ise_v >= 5:
            out["riesgo"]["dual"] = ("configuración dual: el skill manda declarar que la vía "
                                     "echada fue 0 de 7 en el registro y publicar el IE como "
                                     "valor de referencia, no como riesgo vivo")
        if abs(out["ie"] - ise_v) < 0.5:
            out["riesgo"]["dosVentanas"] = ("las dos vías están a menos de 5 décimas: "
                                            "el skill pide declarar las DOS ventanas")
    # los umbrales de color NO se inventan: ver docs/APRENDIZAJE.md
    out["nivel"] = ""
    out["notaNivel"] = ("el IE no lleva semáforo: un color afirma que la escala ORDENA el "
                        "riesgo, y hoy no lo hace — el único positivo ciego computable cae "
                        "en la banda más baja y las dos altas tienen cero")
    out["altaDelSemaforo"] = ALTA_DEL_SEMAFORO
    return out
