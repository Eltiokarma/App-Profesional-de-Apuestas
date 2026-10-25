"""Calendario SAD — el mapa de rivales del bloque G, calculado de NUESTRA base.

SOLO LECTURA y CERO tokens. El protocolo EFE (bloque G2) define siete etiquetas
contextuales con criterio numérico explícito, y seis se pueden calcular con lo
que ya está en sad.db — pagarle a un modelo por buscarlas en la web era pagar
por un dato propio:

| Etiqueta            | Criterio del protocolo                        | De dónde sale |
|---------------------|-----------------------------------------------|---------------|
| 🆕 RECIÉN ASCENDIDO | ascendió en la última temporada               | primera temporada del club en esa liga en nuestro histórico |
| 🔥 EQUIPO SORPRESA  | rinde por encima de su expectativa            | el gap §5 del motor (forma reciente vs μ esperada) |
| 🏠 LOCAL FUERTE     | ≥70% de victorias como local                  | cuenta de sus partidos en casa |
| ✈️ VISITA DÉBIL     | <25% de victorias como visitante              | cuenta de sus partidos fuera |
| 📉 EN CRISIS        | 3+ derrotas seguidas o cambio de DT en 4 sem. | resultados + tabla `entrenadores` |
| 🛡️ BLOQUE BAJO      | esquema con 5 defensores                      | formación dominante en `alineaciones` (fase A del DTP) |
| ⚔️ CLÁSICO          | rivalidad histórica documentada               | PARCIAL: derbi de ciudad (mismo `venue_city`); con ≥ 4 clubes de la liga en esa ciudad, solo `CLASICOS_DOCUMENTADOS` |

Cada etiqueta viaja con el DATO que la sostiene ("3 derrotas seguidas",
"78% en casa"): sin el número es una opinión, y una opinión no debería costar
ni un token ni entrar en un análisis.

`CLASICO` es el único que se queda a medias: una rivalidad nacional sin
vecindad geográfica (Boca–River es de ciudad, pero Alianza–Cienciano no) no
está en los datos. Se marca `parcial: true` para que quien lo lea sepa que ahí
la ausencia de etiqueta no prueba nada.
"""
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from backend import db

PROXIMOS_DEFAULT = 4
FORMA_N = 5              # ventana de forma reciente (misma que el gap §5)
CRISIS_DERROTAS = 3      # criterio G2
CRISIS_DT_DIAS = 28      # "cambió de DT en las últimas 4 semanas"
LOCAL_FUERTE_PCT = 0.70
VISITA_DEBIL_PCT = 0.25
MIN_PARTIDOS_PCT = 4     # sin muestra no se etiqueta (un 100% de 1 partido no dice nada)
SORPRESA_GAP = -0.35     # gap = μ esperada − forma real: negativo = sobrerrinde

_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished')"
_GH = "COALESCE(f.fulltime_home, f.goals_home)"
_GA = "COALESCE(f.fulltime_away, f.goals_away)"


def _hora() -> int:
    return int(datetime.now(timezone.utc).timestamp() // 3600)


def _q(sql: str, params: tuple = ()) -> list:
    try:
        return db.query("sad", sql, params)
    except Exception:
        return []


# ── piezas por rival (todas de sad.db) ──────────────────────────────────────

def _resultados(team_id: int, limite: int = 10) -> list[dict]:
    """Últimos partidos terminados, del más reciente al más viejo."""
    filas = _q(
        f"""SELECT f.date, f.home_team_id, {_GH} AS gh, {_GA} AS ga, f.league_id, f.league_season
            FROM fixtures f
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND {_FIN}
              AND {_GH} IS NOT NULL AND {_GA} IS NOT NULL
            ORDER BY f.date DESC LIMIT ?""",
        (team_id, team_id, limite),
    )
    out = []
    for r in filas:
        es_local = r["home_team_id"] == team_id
        gf, gc = (r["gh"], r["ga"]) if es_local else (r["ga"], r["gh"])
        out.append({"fecha": r["date"], "esLocal": es_local, "gf": gf, "gc": gc,
                    "res": 1 if gf > gc else 0 if gf == gc else -1,
                    "ligaId": r["league_id"], "temporada": r["league_season"]})
    return out


def _derrotas_seguidas(res: list[dict]) -> int:
    n = 0
    for r in res:
        if r["res"] == -1:
            n += 1
        else:
            break
    return n


def _sin_ganar(res: list[dict]) -> int:
    n = 0
    for r in res:
        if r["res"] != 1:
            n += 1
        else:
            break
    return n


def _pct_condicion(team_id: int, liga_id: int | None, temporada: int | None, local: bool) -> tuple[int, int]:
    """(victorias, jugados) del equipo en esa condición y temporada."""
    if liga_id is None or temporada is None:
        return 0, 0
    lado = "home_team_id" if local else "away_team_id"
    filas = _q(
        f"""SELECT {_GH} AS gh, {_GA} AS ga FROM fixtures f
            WHERE f.{lado}=? AND f.league_id=? AND f.league_season=? AND {_FIN}
              AND {_GH} IS NOT NULL AND {_GA} IS NOT NULL""",
        (team_id, liga_id, temporada),
    )
    ganados = sum(1 for r in filas if (r["gh"] > r["ga"]) == local and r["gh"] != r["ga"])
    return ganados, len(filas)


def _dt_reciente(team_id: int) -> str | None:
    """Fecha de asunción del DT si cambió hace poco (tabla de la capa de
    jugadores). None si no hay ingesta o el DT lleva tiempo."""
    filas = _q("SELECT desde FROM entrenadores WHERE team_id=? AND desde IS NOT NULL "
               "ORDER BY desde DESC LIMIT 1", (team_id,))
    if not filas or not filas[0]["desde"]:
        return None
    try:
        desde = datetime.strptime(str(filas[0]["desde"])[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    dias = (datetime.now(timezone.utc) - desde).days
    return str(filas[0]["desde"])[:10] if 0 <= dias <= CRISIS_DT_DIAS else None


def _formacion_dominante(team_id: int) -> str | None:
    """La formación más repetida en sus últimas alineaciones capturadas."""
    filas = _q(
        """SELECT a.formacion, COUNT(*) AS n FROM alineaciones a
           JOIN fixtures f ON f.id = a.fixture_id
           WHERE a.team_id=? AND a.formacion IS NOT NULL AND a.titular=1
           GROUP BY a.fixture_id, a.formacion ORDER BY f.date DESC LIMIT 5""",
        (team_id,),
    )
    if not filas:
        return None
    conteo: dict[str, int] = {}
    for r in filas:
        conteo[r["formacion"]] = conteo.get(r["formacion"], 0) + 1
    mejor = max(conteo, key=lambda k: conteo[k])
    # UN PARTIDO NO ES UNA FORMACIÓN DOMINANTE: Cruz Azul salía BLOQUE BAJO por
    # el 5-3-2 de un 5-0 a Juárez, con 4-2-3-1 la fecha anterior (incidencia 173)
    return mejor if conteo[mejor] >= 2 else None


# Competencias donde NO existe el ascenso: copas internacionales y copas
# nacionales. No jugar la edición anterior es lo normal —se clasifica o no—,
# así que la heurística de «no estaba el año pasado» no significa nada acá.
SIN_ASCENSO = {
    1, 2, 3, 11, 13, 848,                       # Mundial, UEFA y CONMEBOL
    73, 130, 241, 267, 501, 502, 917, 930, 1113, 1220, 1232,   # copas nacionales
    667,                                        # amistosos
}


def _es_ascendido(team_id: int, liga_id: int | None, temporada: int | None) -> bool:
    """¿Subió de categoría? Tres condiciones, y las tres hacen falta.

    La primera versión preguntaba solo «¿jugó en ESTA liga la temporada
    pasada?». En una copa eso es siempre que no, así que marcaba como recién
    ascendidos a São Paulo, Boca, Atlético-MG y Santos a la vez —los cuatro de
    una llave de Sudamericana— y les ponía las K en cuarentena (R-KT.2) sin
    ningún motivo. Un ascenso son dos o tres clubes sobre veinte, no medio
    torneo.

    Ahora hace falta que: (1) la competencia tenga ascenso —una copa no lo
    tiene—, (2) el equipo haya jugado la temporada pasada en OTRA liga de
    nuestro histórico, que es la evidencia positiva del cambio de categoría, y
    (3) no sea el torneo entero el que renovó participantes.
    """
    if liga_id is None or temporada is None or liga_id in SIN_ASCENSO:
        return False
    # ...y una copa que no está en la lista se reconoce por el nombre: Vecino
    # «RECIÉN ASCENDIDO» en la Taça de Portugal (incidencia 404)
    try:
        from backend.analisis.escala import es_copa
        if es_copa(liga_id):
            return False
    except Exception:  # noqa: BLE001 — sin metadatos de la liga, manda la lista
        pass
    previos = _q(
        "SELECT COUNT(*) AS n FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
        "AND league_id=? AND league_season=?",
        (team_id, team_id, liga_id, temporada - 1),
    )
    if previos and previos[0]["n"]:
        return False
    # EVIDENCIA POSITIVA: la temporada pasada jugó, pero en otra liga. Sin esto,
    # un equipo que simplemente no está en nuestro histórico se etiquetaría por
    # nuestra propia falta de datos.
    otra = _q(
        "SELECT COUNT(*) AS n FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
        "AND league_season=? AND league_id<>?",
        (team_id, team_id, temporada - 1, liga_id),
    )
    if not (otra and otra[0]["n"]):
        return False
    return not _renovacion_masiva(liga_id, temporada)


def _renovacion_masiva(liga_id: int, temporada: int, umbral: float = 0.5) -> bool:
    """¿Es el torneo el que cambió de participantes, y no los equipos?

    Solo se puede contestar si tenemos la temporada anterior de ESE torneo. Sin
    ella no se concluye nada: la ausencia de datos no es evidencia de nada.
    """
    filas = _q(
        "SELECT DISTINCT t FROM ("
        "  SELECT home_team_id AS t FROM fixtures WHERE league_id=? AND league_season=?"
        "  UNION SELECT away_team_id FROM fixtures WHERE league_id=? AND league_season=?)",
        (liga_id, temporada, liga_id, temporada),
    )
    equipos = [f["t"] for f in (filas or [])]
    if len(equipos) < 4:
        return False
    previa = _q("SELECT COUNT(*) AS n FROM fixtures WHERE league_id=? AND league_season=?",
                (liga_id, temporada - 1))
    if not (previa and previa[0]["n"]):
        return False   # no tenemos esa temporada: no hay renovación que medir
    marcas = ",".join("?" * len(equipos))
    antes = _q(
        f"SELECT DISTINCT t FROM ("
        f"  SELECT home_team_id AS t FROM fixtures WHERE league_id=? AND league_season=? "
        f"    AND home_team_id IN ({marcas})"
        f"  UNION SELECT away_team_id FROM fixtures WHERE league_id=? AND league_season=? "
        f"    AND away_team_id IN ({marcas}))",
        (liga_id, temporada - 1, *equipos, liga_id, temporada - 1, *equipos),
    )
    repiten = len(antes or [])
    return (len(equipos) - repiten) / len(equipos) > umbral


# CIUDAD DENSA: con 4 o más clubes de la misma liga en la misma ciudad,
# compartirla no hace derbi. En Montevideo o Asunción casi toda la primera
# juega en la capital y «misma ciudad» marcaba como clásico a medio fixture
# (Central Español–Nacional, Libertad–Guaraní, 11/10/2026), y el clásico sube
# un partido en la agenda. Ahí solo cuentan los documentados.
CIUDAD_DENSA = 4

# Rivalidades documentadas en ciudades densas, por nombre normalizado (cada
# lado se busca como texto dentro del nombre del club). Lista corta a
# propósito: un par que falta no se inventa, se agrega con su fuente.
CLASICOS_DOCUMENTADOS = (
    ("penarol", "nacional"),                       # Montevideo · Clásico del fútbol uruguayo
    ("olimpia", "cerro porteno"),                  # Asunción · Superclásico paraguayo
    ("olimpia", "guarani"),                        # Asunción · el clásico más antiguo
    ("libertad", "guarani"),                       # Asunción · «clásico moderno» (ABC Color, 09/10/2026)
    ("boca juniors", "river plate"),               # Buenos Aires · Superclásico
    ("san lorenzo", "huracan"),                    # Buenos Aires · clásico de barrio
    ("alianza lima", "universitario"),             # Lima · Clásico del fútbol peruano
    ("flamengo", "fluminense"), ("flamengo", "vasco"), ("flamengo", "botafogo"),
    ("fluminense", "vasco"), ("fluminense", "botafogo"), ("vasco", "botafogo"),  # Río · clássicos cariocas
    ("arsenal", "tottenham"), ("chelsea", "tottenham"), ("arsenal", "chelsea"),   # Londres
    ("galatasaray", "fenerbahce"), ("galatasaray", "besiktas"), ("fenerbahce", "besiktas"),  # Estambul · el Kıtalararası Derbi y los otros dos (incidencia 339)
)


# RIVALIDADES SIN VECINDAD (25/10/2026, incidencias 480 y 549): un clásico
# nacional no comparte ciudad y no sale de `venue_city`. Napoli–Roma (Derby
# del Sole) y Santos–Palmeiras (Clássico da Saudade) salían sin etiqueta y el
# F2 del TDE no veía el clásico a 3 días. Misma regla: lista corta, cada par
# con su nombre; un par que falta se agrega, no se infiere.
CLASICOS_NACIONALES = (
    ("napoli", "roma"),                            # Derby del Sole
    ("juventus", "torino"), ("juventus", "fiorentina"),
    ("real madrid", "barcelona"),                  # El Clásico
    ("athletic", "real sociedad"),                 # derbi vasco
    ("santos", "palmeiras"),                       # Clássico da Saudade
    ("santos", "corinthians"), ("santos", "sao paulo"),  # clássicos paulistas sin vecindad
    ("ajax", "feyenoord"), ("ajax", "psv"), ("psv", "feyenoord"),  # De Klassieker y los otros dos
    ("benfica", "porto"), ("porto", "sporting cp"),
    ("borussia dortmund", "schalke"), ("bayern", "borussia dortmund"),
    ("marseille", "paris saint germain"),          # Le Classique
    ("liverpool", "manchester united"),            # North West Derby
    ("alianza lima", "sporting cristal"), ("universitario", "sporting cristal"),
)

# PARES QUE COMPARTEN CIUDAD SIN SER DERBI: uno de los dos juega de local en
# estadio prestado (incidencia 422: Deportivo Recoleta, de Asunción, figura con
# `venue_city` Luque y salía «derbi de Luque» contra el Sportivo Luqueño).
NO_CLASICOS = (
    ("luqueno", "recoleta"),
)


def clasico_nacional(nombre_a: str, nombre_b: str) -> bool:
    a, b = _norm_nombre(nombre_a), _norm_nombre(nombre_b)
    return any((x in a and y in b) or (x in b and y in a) for x, y in CLASICOS_NACIONALES)


def no_clasico(nombre_a: str, nombre_b: str) -> bool:
    a, b = _norm_nombre(nombre_a), _norm_nombre(nombre_b)
    return any((x in a and y in b) or (x in b and y in a) for x, y in NO_CLASICOS)


def _norm_nombre(nombre: str) -> str:
    n = unicodedata.normalize("NFD", (nombre or "").lower())
    return "".join(c for c in n if unicodedata.category(c) != "Mn")


def clasico_documentado(nombre_a: str, nombre_b: str) -> bool:
    a, b = _norm_nombre(nombre_a), _norm_nombre(nombre_b)
    return any((x in a and y in b) or (x in b and y in a) for x, y in CLASICOS_DOCUMENTADOS)


@lru_cache(maxsize=256)
def _clubes_en_ciudad(liga_id: int | None, temporada: int | None, ciudad: str) -> int:
    """Cuántos clubes de esa liga (y temporada, si se sabe) son locales en `ciudad`."""
    if not liga_id or not ciudad:
        return 0
    cond, params = "league_id=? AND lower(trim(venue_city))=?", [liga_id, ciudad.strip().lower()]
    if temporada:
        cond += " AND league_season=?"
        params.append(temporada)
    filas = _q(f"SELECT COUNT(DISTINCT home_team_id) AS n FROM fixtures WHERE {cond}", tuple(params))
    return int(filas[0]["n"]) if filas else 0


def _nombre_equipo(team_id: int) -> str:
    filas = _q("SELECT name FROM teams WHERE id=?", (team_id,))
    return filas[0]["name"] if filas else ""


def _ciudad(team_id: int) -> str | None:
    filas = _q("SELECT venue_city, COUNT(*) AS n FROM fixtures WHERE home_team_id=? "
               "AND venue_city IS NOT NULL AND venue_city<>'' "
               "GROUP BY venue_city ORDER BY n DESC LIMIT 1", (team_id,))
    return filas[0]["venue_city"] if filas else None


# LA FASE CON TABLA PROPIA DE UN TORNEO INTERNACIONAL. La tabla del año de la
# Champions mezclaba la fase previa con la fase liga: «Arsenal 25º con 6 de 6»
# sobre 81 equipos (incidencia 293, 21/10/2026). En la fase liga o de grupos,
# la posición es la de ESA fase; Apertura/Clausura siguen con la tabla del año.
_FASE_CON_TABLA = re.compile(r"^(league stage|league phase|group\b)", re.I)


def fase_con_tabla(ronda: str | None) -> str | None:
    from backend.app import _fase_de_round
    fase = _fase_de_round(ronda)
    return fase if fase and _FASE_CON_TABLA.match(fase) else None


@lru_cache(maxsize=64)
def _posiciones(liga_id: int, temporada: int, bucket: int, fase: str | None = None) -> dict[int, int]:
    """{equipoId: posición} de la tabla del año, o de la fase si se pide (caché por hora)."""
    from backend.app import standings  # import perezoso: app importa este módulo
    try:
        return {r["equipoId"]: r["posicion"] for r in standings(liga_id, temporada, fase)}
    except Exception:
        return {}


# EL TORNEO CORTO EN CURSO, NO EL AÑO (incidencia 441): en las ligas que parten
# el año (Apertura/Clausura) la posición del rival salía de la tabla del año.
# Con la fase ya andando (FASE_MIN_PJ fechas), manda la tabla de esa fase; al
# arrancar, con dos fechas, la del año dice más.
_FASE_NACIONAL = re.compile(r"^(apertura|clausura|torneo|first stage|second stage|1st|2nd)", re.I)
FASE_MIN_PJ = 5


@lru_cache(maxsize=64)
def _max_pj_fase(liga_id: int, temporada: int, bucket: int, fase: str) -> int:
    from backend.app import standings
    try:
        return max((r.get("partidosJugados") or 0 for r in standings(liga_id, temporada, fase)), default=0)
    except Exception:
        return 0


def posiciones_y_tabla(liga_id: int, temporada: int, bucket: int, ronda: str | None) -> tuple[dict[int, int], str]:
    """(posiciones, de qué tabla salen): la fase con tabla propia de un torneo
    internacional, el torneo corto nacional en curso si ya anda, o el año."""
    fase = fase_con_tabla(ronda)
    if fase:
        return _posiciones(liga_id, temporada, bucket, fase), fase
    from backend.app import _fase_de_round
    nacional = _fase_de_round(ronda)
    if nacional and _FASE_NACIONAL.match(nacional) and _max_pj_fase(liga_id, temporada, bucket, nacional) >= FASE_MIN_PJ:
        pos = _posiciones(liga_id, temporada, bucket, nacional)
        if pos:
            return pos, nacional
    return _posiciones(liga_id, temporada, bucket), "año"


def _gap(team_id: int, fecha: str | None) -> dict | None:
    from backend.app import gap_equipo
    try:
        return gap_equipo(team_id, fecha)
    except Exception:
        return None


# ── etiquetas ───────────────────────────────────────────────────────────────

def etiquetas_de_rival(rival_id: int, rival_local: bool, liga_id: int | None,
                       temporada: int | None, fecha: str | None,
                       ciudad_equipo: str | None, equipo_id: int | None = None) -> list[dict]:
    """Las etiquetas G2 que los DATOS sostienen, cada una con su número."""
    et: list[dict] = []
    res = _resultados(rival_id)

    if _es_ascendido(rival_id, liga_id, temporada):
        et.append({"codigo": "RECIEN_ASCENDIDO", "label": "RECIÉN ASCENDIDO",
                   "dato": "primera temporada en la categoría",
                   "nota": "sus K están en cuarentena (R-KT.2): no hay línea base fiable"})

    derrotas = _derrotas_seguidas(res)
    dt_nuevo = _dt_reciente(rival_id)
    if derrotas >= CRISIS_DERROTAS or dt_nuevo:
        motivos = []
        if derrotas >= CRISIS_DERROTAS:
            motivos.append(f"{derrotas} derrotas seguidas")
        if dt_nuevo:
            motivos.append(f"DT nuevo desde {dt_nuevo}")
        et.append({"codigo": "EN_CRISIS", "label": "EN CRISIS", "dato": " · ".join(motivos),
                   "nota": "posible efecto rebote, en cualquiera de los dos sentidos"})

    ganados, jugados = _pct_condicion(rival_id, liga_id, temporada, rival_local)
    if jugados >= MIN_PARTIDOS_PCT:
        pct = ganados / jugados
        if rival_local and pct >= LOCAL_FUERTE_PCT:
            et.append({"codigo": "LOCAL_FUERTE", "label": "LOCAL FUERTE",
                       "dato": f"{round(pct * 100)}% de victorias en casa ({ganados}/{jugados})"})
        elif not rival_local and pct < VISITA_DEBIL_PCT:
            et.append({"codigo": "VISITA_DEBIL", "label": "VISITA DÉBIL",
                       "dato": f"{round(pct * 100)}% de victorias fuera ({ganados}/{jugados})"})

    g = _gap(rival_id, fecha)
    if g and g.get("gap") is not None and g["gap"] <= SORPRESA_GAP:
        et.append({"codigo": "EQUIPO_SORPRESA", "label": "EQUIPO SORPRESA",
                   "dato": f"rinde {abs(g['gap']):.2f} pts/partido por encima de su nivel",
                   "nota": "candidato a regresión: la ventaja puede no sostenerse"})

    formacion = _formacion_dominante(rival_id)
    if formacion and formacion.split("-")[0] == "5":
        et.append({"codigo": "BLOQUE_BAJO", "label": "BLOQUE BAJO",
                   "dato": f"formación dominante {formacion}"})

    nombres = (_nombre_equipo(equipo_id), _nombre_equipo(rival_id)) if equipo_id else None
    if nombres and no_clasico(*nombres):
        return et
    if nombres and clasico_nacional(*nombres):
        et.append({"codigo": "CLASICO", "label": "CLÁSICO", "dato": "clásico nacional documentado",
                   "parcial": True,
                   "nota": "rivalidad sin vecindad: sale de la lista de clásicos nacionales, no de la ciudad"})
        return et
    ciudad_rival = _ciudad(rival_id)
    if ciudad_equipo and ciudad_rival and ciudad_equipo.strip().lower() == ciudad_rival.strip().lower():
        n_clubes = _clubes_en_ciudad(liga_id, temporada, ciudad_rival)
        if n_clubes < CIUDAD_DENSA:
            et.append({"codigo": "CLASICO", "label": "CLÁSICO", "dato": f"derbi de {ciudad_rival}",
                       "parcial": True,
                       "nota": "solo detectamos derbis de ciudad: una rivalidad nacional no sale de los datos"})
        elif equipo_id and clasico_documentado(_nombre_equipo(equipo_id), _nombre_equipo(rival_id)):
            et.append({"codigo": "CLASICO", "label": "CLÁSICO",
                       "dato": f"clásico documentado de {ciudad_rival}",
                       "parcial": True,
                       "nota": f"{n_clubes} clubes de la liga en {ciudad_rival}: ahí la misma ciudad no "
                               "basta, cuenta la lista de clásicos documentados"})
    return et


# ── calendario ──────────────────────────────────────────────────────────────

def calendario_de(team_id: int, n: int = PROXIMOS_DEFAULT) -> list[dict]:
    """Los próximos `n` partidos del equipo con el mapa de rivales del bloque G.
    [] si no hay fixtures programados. 0 requests, 0 tokens."""
    filas = _q(
        """SELECT f.id, f.date, f.home_team_id, f.away_team_id, f.league_id, f.league_season,
                  f.league_round, f.venue_city, l.name AS liga,
                  ht.name AS local, at.name AS visitante
           FROM fixtures f
           JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id
           LEFT JOIN leagues l ON l.id=f.league_id
           WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.status_short IN ('NS','TBD')
             AND f.date >= ? ORDER BY f.date ASC LIMIT ?""",
        (team_id, team_id, datetime.now(timezone.utc).strftime("%Y-%m-%d 00:00:00"), n),
    )
    if not filas:
        return []
    ciudad_equipo = _ciudad(team_id)
    ultimos = _resultados(team_id, limite=1)
    previo = ultimos[0]["fecha"] if ultimos else None
    bucket = _hora()

    salida = []
    for i, f in enumerate(filas):
        es_local = f["home_team_id"] == team_id
        rival_id = f["away_team_id"] if es_local else f["home_team_id"]
        rival_nombre = f["visitante"] if es_local else f["local"]
        fecha = (f["date"] or "")[:10]
        # UNA COPA NO TIENE TABLA COMPARABLE. Delfín «2.º de 48» en la semi de
        # la Copa Ecuador, Sporting «8/8 y zona descenso» en la Taça da Liga
        # (incidencia 404): la posición del rival sale vacía, no de esa tabla.
        from backend.analisis.escala import es_copa
        copa = bool(f["league_id"]) and es_copa(f["league_id"], f["liga"])
        posiciones, tabla_de = (posiciones_y_tabla(f["league_id"], f["league_season"], bucket, f["league_round"])
                                if f["league_id"] and not copa else ({}, ""))
        pos = posiciones.get(rival_id)
        total = len(posiciones)
        # descanso: contra el partido anterior para el primero, y entre fechas
        # para los siguientes — la congestión se lee de un vistazo
        ref = previo if i == 0 else (filas[i - 1]["date"] or "")
        dias = None
        if ref and f["date"]:
            try:
                dias = (datetime.strptime(str(f["date"])[:10], "%Y-%m-%d")
                        - datetime.strptime(str(ref)[:10], "%Y-%m-%d")).days
            except ValueError:
                dias = None
        salida.append({
            "fixtureId": f["id"],
            "fecha": fecha,
            "rivalId": rival_id,
            "rival": rival_nombre,
            "condicion": "L" if es_local else "V",
            "torneo": f["liga"],
            "ronda": f["league_round"],
            "posicionRival": pos,
            "tablaDe": tabla_de if pos else "",
            "equiposEnLaTabla": total or None,
            # zona: lo que importa del rival en la tabla, sin adjetivos
            "zonaRival": None if not pos or not total else (
                "alta" if pos <= 4 else "descenso" if pos > total - 3 else "media"),
            "diasDescanso": dias,
            "etiquetas": etiquetas_de_rival(rival_id, not es_local, f["league_id"],
                                            f["league_season"], fecha, ciudad_equipo,
                                            equipo_id=team_id),
        })
    return salida


def items_para_efe(team_id: int, n: int = PROXIMOS_DEFAULT) -> list[dict]:
    """El bloque G del EFE con la forma de su esquema (CALENDARIO_ITEM), para
    RELLENARLO EN CÓDIGO en vez de pagarle al modelo por copiar lo que ya
    calculamos. Además de ahorrar tokens de salida cierra la puerta a que el
    calendario salga adornado: aquí no cabe una etiqueta sin su dato."""
    return [
        {
            "rival": c["rival"],
            "fecha": c["fecha"],
            "condicion": c["condicion"],
            "etiquetas": [f"{e['label']} ({e['dato']})" for e in c["etiquetas"]],
            "posicion": c["posicionRival"] or 0,  # 0 = se desconoce, según el esquema
            "nota": ", ".join(filter(None, [
                f"zona {c['zonaRival']}" if c["zonaRival"] else "",
                f"{c['diasDescanso']}d de descanso" if c["diasDescanso"] is not None else "",
            ])),
        }
        for c in calendario_de(team_id, n)
    ]


def texto_para_skills(team_id: int, n: int = PROXIMOS_DEFAULT) -> str:
    """El mismo calendario como texto denso para `datos_cacheados` del EFE/DTP:
    con esto el modelo NO investiga el bloque G — ni busca ni deduce lo que ya
    está calculado. Vacío si no hay fixtures."""
    cal = calendario_de(team_id, n)
    if not cal:
        return ""
    partes = []
    for c in cal:
        et = "; ".join(f"{e['label']} ({e['dato']})" for e in c["etiquetas"]) or "sin etiqueta"
        pos = f"{c['posicionRival']}º" if c["posicionRival"] else "s/pos"
        descanso = f", {c['diasDescanso']}d de descanso" if c["diasDescanso"] is not None else ""
        partes.append(f"{c['fecha']} {c['condicion']} vs {c['rival']} ({pos}"
                      f"{', zona ' + c['zonaRival'] if c['zonaRival'] else ''}{descanso}): {et}")
    return ("Calendario SAD calculado de nuestra base (bloque G ya resuelto, NO lo investigues): "
            + " | ".join(partes))
