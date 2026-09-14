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
