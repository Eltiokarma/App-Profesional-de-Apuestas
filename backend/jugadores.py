"""Indicadores de jugadores (capa 1 de docs/JUGADORES.md) — SOLO LECTURA.

Deriva de las tablas de jugadores de sad.db (escritas por
backend.ingesta.jugadores) los indicadores de la spec: por-90 con
encogimiento bayesiano hacia la media de la posición, grado de confianza por
minutos, dependencia HHI, flags de baja / recién llegado / en capilla,
métricas de portero y congestión de calendario. 0 requests: todo sale de la
base. Sin tablas o sin datos, degrada a plantilla vacía — nada se inventa.

Consumidores: los endpoints /equipos/{id}/plantilla y /fixtures/{id}/ficha
(backend/app.py) y el cruce con los skills (backend/analisis/motor.py).
"""
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from backend import db

# Encogimiento (spec §2): con M=900 min (≈10 partidos) manda el prior; el
# doble de minutos ya inclina la mezcla hacia los datos del jugador.
SHRINK_M = 900
# Grados de confianza por minutos jugados (spec §3)
CONF_A_MIN = 1800
CONF_B_MIN = 600
PRIOR_MIN_MINUTOS = 180   # muestra mínima para entrar al prior de la posición
RECIEN_LLEGADO_DIAS = 90
REVOLUCION_DIAS = 120
CONGESTION_DIAS = 21
EN_CAPILLA_AMARILLAS = 4
# El flag «Missing Fixture» de /injuries como SEÑAL CON UMBRAL. La corrida de
# Cowork del 16/09/2026 lo contrastó con prensa en 23 partes: acertó 10, con
# separación clara por DENSIDAD —pocos jugadores marcados = baja real; media
# plantilla marcada = ruido de la API (marca a todo el que no estuvo en un
# partido, convocados o no)—. Se había catalogado como artefacto y se tiraba
# entero; ahora cada baja viaja con su lectura y el resumen que llega al skill,
# la estabilidad de la burbuja y las pantallas solo cuentan las de señal.
# Umbral: por encima de este porcentaje de la plantilla marcada, es ruido.
# Primer corte a partir de esa corrida (n=23): se recalibra con más casos.
UMBRAL_MISSING_FIXTURE = 0.25

POSICIONES = {
    "Goalkeeper": "Portero",
    "Defender": "Defensa",
    "Midfielder": "Centrocampista",
    "Attacker": "Delantero",
}

_FIN90 = "(status_short IN ('FT','AET','PEN') OR status_long='Match Finished')"


MINUTOS_POR_PARTIDO_MAX = 125   # 90 + alargue + descuentos: más que esto por partido no es un dato

def _query(sql: str, params: tuple = ()) -> list:
    """query sobre sad.db tolerante a DBs sin las tablas de jugadores."""
    try:
        return db.query("sad", sql, params)
    except Exception:
        return []


def _p90(valor: int, minutos: int) -> float | None:
    return round(valor / minutos * 90, 3) if minutos else None


@lru_cache(maxsize=4)
def _priors_posicion(bucket: int) -> dict[str, float]:
    """Media liga-completa de (G+A)/90 por posición sobre TODOS los jugadores
    capturados con >= PRIOR_MIN_MINUTOS (caché por hora: cambia con la ingesta)."""
    filas = _query(
        f"""SELECT posicion, SUM(goles + asistencias) AS ga, SUM(minutos) AS minutos
            FROM jugador_stats GROUP BY player_id, posicion
            HAVING SUM(minutos) >= {PRIOR_MIN_MINUTOS}"""
    )
    acc: dict[str, list[float]] = {}
    for r in filas:
        pos = r["posicion"] or ""
        acc.setdefault(pos, []).append(r["ga"] / r["minutos"] * 90)
    priors = {pos: sum(v) / len(v) for pos, v in acc.items() if v}
    todos = [x for v in acc.values() for x in v]
    priors[""] = sum(todos) / len(todos) if todos else 0.25  # fallback global
    return priors


def _prior_de(posicion: str | None) -> float:
    priors = _priors_posicion(int(datetime.now(timezone.utc).timestamp() // 3600))
    return priors.get(posicion or "", priors.get("", 0.25))


def _temporada_de(team_id: int) -> int | None:
    filas = _query("SELECT season FROM plantillas_meta WHERE team_id=?", (team_id,))
    if filas and filas[0]["season"]:
        return filas[0]["season"]
    filas = _query("SELECT MAX(season) AS s FROM jugador_stats WHERE team_id=?", (team_id,))
    return filas[0]["s"] if filas and filas[0]["s"] else None


def _confianza(minutos: int, recien_llegado: bool) -> str:
    grado = "A" if minutos >= CONF_A_MIN else "B" if minutos >= CONF_B_MIN else "C"
    if recien_llegado and grado != "C":
        # regla de reseteo (spec §9): sus stats vienen de otro contexto
        grado = "B" if grado == "A" else "C"
    return grado


def _entrenador_filas(team_id: int) -> list:
    try:
        return _query(
            "SELECT nombre, desde, actualizado_en, fuente FROM entrenadores WHERE team_id=? "
            "ORDER BY actualizado_en DESC LIMIT 1", (team_id,))
    except sqlite3.OperationalError:  # base anterior a la columna `fuente`
        return _query(
            "SELECT nombre, desde, actualizado_en, 'coachs' AS fuente FROM entrenadores WHERE team_id=? "
            "ORDER BY actualizado_en DESC LIMIT 1", (team_id,))


def _entrenador_dto(fila) -> dict:
    """El DT con su procedencia y su edad: quien lo lee decide si se fía.
    Sobre 19 verificados contra prensa el 18/09, 4 eran el saliente (de 3 a
    27 meses atrás), y sin `actualizadoEn` no había forma de marcarlos."""
    act = fila["actualizado_en"]
    return {"nombre": fila["nombre"], "desde": fila["desde"],
            "actualizadoEn": (act.replace(" ", "T") + "Z") if act and "T" not in act else act,
            "fuente": fila["fuente"] or "coachs"}


def _origen_de(team_id: int) -> str:
    try:
        filas = _query("SELECT origen FROM plantillas_meta WHERE team_id=?", (team_id,))
    except sqlite3.OperationalError:  # base anterior a la columna
        return "vigente"
    return (filas[0]["origen"] if filas and filas[0]["origen"] else "vigente")


def _plantel_sin_stats(team_id: int, con_stats: set) -> list[dict]:
    """Los del plantel ACTUAL (/players/squads) que no tienen stats en la
    temporada servida: los que llegaron después, o todos si solo hay lista."""
    try:
        filas = _query("SELECT player_id, nombre, posicion, numero FROM plantel_actual WHERE team_id=? "
                       "ORDER BY posicion, numero", (team_id,))
    except sqlite3.OperationalError:  # base sin la tabla
        return []
    return [{"jugadorId": f["player_id"], "nombre": f["nombre"] or "?",
             "posicion": POSICIONES.get(f["posicion"] or "", f["posicion"] or ""), "numero": f["numero"]}
            for f in filas if f["player_id"] not in con_stats]


# LA REVOLUCIÓN SE CUENTA CON MINUTOS (incidencia 43, decisión del usuario
# 23/10/2026). Se contaban todos los traspasos de 120 días: la Juventus salía
# con 85 (41 llegadas, 44 salidas) cuando de las 41 llegadas solo 8 estaban en
# el plantel y 7 habían jugado —el resto, vueltas de cesión que se volvieron a
# ir, juveniles y papeleo—, y 58 de los 60 equipos de la agenda del 23/10
# salían «inestables»: la etiqueta ya no separaba a nadie. Ahora cuenta el
# jugador (una vez por dirección) que jugó en el primer equipo: minutos en
# `jugador_stats` con este club, o titular en un once capturado del último
# año. El total en papeles viaja aparte (`enPapeles`) para que el analista vea
# las dos cosas. Límite declarado: la base solo trae las stats de la temporada
# vigente y los onces que se capturaron, así que una salida de un titular de
# hace dos temporadas puede no verse.
# CON MINUTOS EN SU MOMENTO (23/10/2026, primera medición en producción): la
# Juventus salía con 13 llegadas «con minutos» porque una vuelta de cesión
# contaba con minutos de temporadas viejas. La LLEGADA cuenta si jugó DESPUÉS
# de llegar (minutos en la temporada vigente o titular en un once posterior);
# la SALIDA, si jugó en la vigente o la anterior, o fue titular en el año
# previo a irse.
REVOLUCION_JUGO_DIAS = 400


def revolucion_de(team_id: int, hoy: datetime | None = None) -> dict:
    hoy = hoy or datetime.now(timezone.utc)
    corte = (hoy - timedelta(days=REVOLUCION_DIAS)).strftime("%Y-%m-%d")
    movs = _query("SELECT player_id, fecha, team_in, team_out FROM traspasos "
                  "WHERE (team_in=? OR team_out=?) AND fecha >= ?", (team_id, team_id, corte))
    # la fecha que importa por jugador: la última llegada y la última salida
    llegan: dict[int, str] = {}
    salen: dict[int, str] = {}
    for m in movs:
        d = llegan if m["team_in"] == team_id else salen
        d[m["player_id"]] = max(d.get(m["player_id"], ""), str(m["fecha"])[:10])
    n_lleg = n_sal = 0
    if llegan or salen:
        temp = _temporada_de(team_id) or hoy.year
        stats = {r["player_id"]: r["seasons"] for r in _query(
            "SELECT player_id, GROUP_CONCAT(DISTINCT season) AS seasons FROM jugador_stats "
            "WHERE team_id=? AND COALESCE(minutos, 0) > 0 GROUP BY player_id", (team_id,))}
        temporadas = {pid: {int(s) for s in str(v or "").split(",") if s.strip().lstrip("-").isdigit()}
                      for pid, v in stats.items()}
        try:
            onces = _query(
                "SELECT a.player_id, f.date FROM alineaciones a JOIN fixtures f ON f.id = a.fixture_id "
                "WHERE a.team_id=? AND a.titular=1 AND f.date >= ?",
                (team_id, (hoy - timedelta(days=REVOLUCION_DIAS + REVOLUCION_JUGO_DIAS)).strftime("%Y-%m-%d")))
        except Exception:  # noqa: BLE001 — base sin fichas: cuentan solo las stats
            onces = []
        fechas_once: dict[int, list[str]] = {}
        for o in onces:
            fechas_once.setdefault(o["player_id"], []).append(str(o["date"])[:10])
        for pid, f in llegan.items():
            if temp in temporadas.get(pid, set()) or any(d >= f for d in fechas_once.get(pid, [])):
                n_lleg += 1
        for pid, f in salen.items():
            antes = (datetime.strptime(f, "%Y-%m-%d") - timedelta(days=REVOLUCION_JUGO_DIAS)).strftime("%Y-%m-%d")
            if temporadas.get(pid, set()) & {temp, temp - 1} or any(antes <= d <= f for d in fechas_once.get(pid, [])):
                n_sal += 1
    return {
        "llegadas": n_lleg,
        "salidas": n_sal,
        "ventanaDias": REVOLUCION_DIAS,
        "criterio": "con minutos en el primer equipo",
        "enPapeles": {"llegadas": len(llegan), "salidas": len(salen)},
    }


def plantilla_de(team_id: int) -> dict:
    """PlantillaDTO del contrato: jugadores con indicadores + agregados del
    equipo (dependencia HHI, DT, revolución). Vacía si no hay ingesta."""
    temporada = _temporada_de(team_id)
    meta = _query("SELECT actualizado_en FROM plantillas_meta WHERE team_id=?", (team_id,))
    base = {
        "equipoId": team_id,
        "temporada": temporada,
        "actualizadoEn": (meta[0]["actualizado_en"].replace(" ", "T") + "Z") if meta else None,
        "entrenador": None,
        "dependencia": {"hhi": None, "top": []},
        "revolucion": {"llegadas": 0, "salidas": 0, "ventanaDias": REVOLUCION_DIAS},
        "jugadores": [],
        "golesPlantilla": 0,
        "missingFixture": None,
        # de qué temporada salen las stats: la API publica la nueva con
        # semanas de retraso en muchas ligas; mientras tanto se sirven las de
        # la ANTERIOR de los que siguen en el club, y se dice
        "origenTemporada": _origen_de(team_id),
        "plantelSinStats": [],
    }
    if temporada is None:
        return base

    # agregado por jugador entre competiciones de la MISMA temporada y equipo;
    # posición y rating: los de la competición con más minutos / media ponderada
    filas = _query(
        """SELECT s.player_id, j.nombre, j.edad, j.foto,
                  SUM(s.partidos) AS partidos, SUM(s.titularidades) AS titularidades,
                  SUM(s.minutos) AS minutos, SUM(s.goles) AS goles,
                  SUM(s.asistencias) AS asistencias, SUM(s.goles_encajados) AS goles_encajados,
                  SUM(s.paradas) AS paradas, SUM(s.amarillas) AS amarillas,
                  SUM(s.rojas) AS rojas,
                  SUM(s.rating * s.minutos) AS rating_pond,
                  SUM(CASE WHEN s.rating IS NOT NULL THEN s.minutos ELSE 0 END) AS min_con_rating,
                  MAX(s.minutos) AS max_min_comp,
                  (SELECT s2.posicion FROM jugador_stats s2
                    WHERE s2.player_id=s.player_id AND s2.team_id=s.team_id AND s2.season=s.season
                    ORDER BY s2.minutos DESC LIMIT 1) AS posicion
           FROM jugador_stats s JOIN jugadores j ON j.id = s.player_id
           WHERE s.team_id=? AND s.season=?
           GROUP BY s.player_id
           ORDER BY SUM(s.minutos) DESC""",
        (team_id, temporada),
    )
    # solo cuando la lista actual se pidió POR esto (vigente vacía): con la
    # vigente publicada, plantel_actual puede ser de hace semanas
    if base["origenTemporada"] != "vigente":
        base["plantelSinStats"] = _plantel_sin_stats(team_id, {r["player_id"] for r in filas})
    if not filas:
        return base

    hoy = datetime.now(timezone.utc)
    corte_llegada = (hoy - timedelta(days=RECIEN_LLEGADO_DIAS)).strftime("%Y-%m-%d")
    llegadas = ultima_llegada(_query(
        "SELECT player_id, fecha, team_out, team_out_nombre FROM traspasos "
        "WHERE team_in=? AND fecha >= ? ORDER BY fecha DESC",
        (team_id, corte_llegada),
    ), team_id)
    bajas = {
        r["player_id"]: r for r in _query(
            "SELECT player_id, tipo, detalle, fecha FROM jugador_bajas WHERE team_id=?", (team_id,)
        )
    }
    # LAS ROJAS DE NUESTRAS FICHAS (incidencias 410 y 599): la API tarda en
    # listar la suspensión y el expulsado del último partido salía disponible.
    # La de la API, si está, manda; la de la ficha solo llena el hueco.
    for pid, b in sanciones_de_ficha(team_id).items():
        bajas.setdefault(pid, b)
    jugo = ultimo_partido_jugado(team_id)
    missing = lectura_missing_fixture(bajas, {r["player_id"] for r in filas}, jugo)

    # MINUTOS QUE NO CABEN EN LOS PARTIDOS. La API dio a J. García (Tigres,
    # 20/10/2026) 1 partido y 1.708 minutos: salía «titular habitual (81 %)» y
    # el parte gritaba F1-DECISIVO-FUERA por un suplente. El dato crudo se
    # sirve igual (con `minutosIncoherentes`), pero el % de minutos —de donde
    # salen el rol y el decisivo— se cuenta con lo que cabe en sus partidos.
    def _min_creibles(r) -> int:
        m = r["minutos"] or 0
        tope = max(r["partidos"] or 0, r["titularidades"] or 0) * MINUTOS_POR_PARTIDO_MAX
        return min(m, tope)

    max_minutos = max(_min_creibles(r) for r in filas) or 1
    goles_equipo = sum(r["goles"] or 0 for r in filas)
    ga_equipo = sum((r["goles"] or 0) + (r["asistencias"] or 0) for r in filas)

    jugadores = []
    for r in filas:
        minutos = r["minutos"] or 0
        goles, asist = r["goles"] or 0, r["asistencias"] or 0
        posicion = r["posicion"]
        es_gk = posicion == "Goalkeeper"
        ga90 = _p90(goles + asist, minutos)
        # encogimiento hacia la media de su posición (spec §2)
        ga90_aj = None
        if minutos:
            ga90_aj = round((minutos * (ga90 or 0) + SHRINK_M * _prior_de(posicion)) / (minutos + SHRINK_M), 3)
        llegada = llegadas.get(r["player_id"])
        baja = bajas.get(r["player_id"])
        rating = None
        if r["min_con_rating"]:
            rating = round((r["rating_pond"] or 0) / r["min_con_rating"], 2)
        jugadores.append({
            "id": r["player_id"],
            # el mismo id con el nombre de la tabla F1 y del bloque F (incidencia
            # 473: Cowork copiaba `id` de acá y `jugadorId` de /f1 y los mezclaba)
            "jugadorId": r["player_id"],
            "nombre": r["nombre"] or "?",
            "edad": r["edad"],
            "foto": r["foto"],
            "posicion": POSICIONES.get(posicion or "", posicion or ""),
            "partidos": r["partidos"] or 0,
            "titularidades": r["titularidades"] or 0,
            "minutos": minutos,
            "pctMinutos": round(_min_creibles(r) / max_minutos, 3),
            **({"minutosIncoherentes": True} if _min_creibles(r) < minutos else {}),
            "rating": rating,
            "confianza": _confianza(minutos, llegada is not None),
            "goles": goles,
            "asistencias": asist,
            "golesP90": _p90(goles, minutos),
            "asistenciasP90": _p90(asist, minutos),
            "gaP90Ajustado": ga90_aj,
            "participacionOfensiva": round((goles + asist) / ga_equipo, 3) if ga_equipo else 0.0,
            "amarillas": r["amarillas"] or 0,
            "rojas": r["rojas"] or 0,
            "enCapilla": (r["amarillas"] or 0) >= EN_CAPILLA_AMARILLAS and not (r["rojas"] or 0),
            "paradasP90": _p90(r["paradas"] or 0, minutos) if es_gk else None,
            "golesEncajadosP90": _p90(r["goles_encajados"] or 0, minutos) if es_gk else None,
            "baja": (_baja_dto(baja, missing, jugo.get(r["player_id"])) if baja else None),
            "recienLlegado": (
                {"desde": llegada["team_out_nombre"], "fecha": llegada["fecha"]} if llegada else None
            ),
        })

    # dependencia HHI (spec §6): shares de G+A al cuadrado; ~1/n coral, →1 él-dependiente
    shares = [
        ((j["goles"] + j["asistencias"]) / ga_equipo)
        for j in jugadores if (j["goles"] + j["asistencias"]) > 0
    ] if ga_equipo else []
    hhi = round(sum(s * s for s in shares), 3) if shares else None
    top = sorted(
        (j for j in jugadores if j["participacionOfensiva"] > 0),
        key=lambda j: -j["participacionOfensiva"],
    )[:3]

    dt_filas = _entrenador_filas(team_id)
    rev = revolucion_de(team_id, hoy)
    base.update({
        "entrenador": _entrenador_dto(dt_filas[0]) if dt_filas else None,
        "dependencia": {
            "hhi": hhi,
            "top": [
                {"jugadorId": j["id"], "nombre": j["nombre"], "participacion": j["participacionOfensiva"]}
                for j in top
            ],
        },
        "revolucion": rev,
        "jugadores": jugadores,
        # goles del equipo según la plantilla (denominador de participación)
        "golesPlantilla": goles_equipo,
        # el flag Missing Fixture leído por densidad (ver UMBRAL_MISSING_FIXTURE)
        "missingFixture": missing if (missing["marcados"] or missing["desmentidas"]) else None,
    })
    return base


def ultima_llegada(filas, team_id: int) -> dict:
    """{jugador: su llegada MÁS RECIENTE}. Las filas vienen de la más nueva a la
    más vieja y el diccionario por comprensión se quedaba con la ÚLTIMA leída,
    o sea la más vieja: «desde León» para dos jugadores que no venían de ahí
    (incidencia 543). Una «llegada» desde el propio club (vuelta registrada
    con el mismo equipo de los dos lados) no dice de dónde vino: se salta."""
    out: dict = {}
    for r in filas:
        if r["player_id"] in out:
            continue
        if "team_out" in r.keys() and r["team_out"] == team_id:
            continue
        out[r["player_id"]] = r
    return out


def sanciones_de_ficha(team_id: int) -> dict[int, dict]:
    """{jugador: baja} por roja directa o doble amarilla en el ÚLTIMO partido
    terminado del equipo, sacada de nuestras fichas. Se lee como sanción
    (`es_sancion`), y si después jugó otro partido queda desmentida sola (la
    fecha de la baja es la del partido de la roja)."""
    try:
        ult = _query(f"SELECT id, date FROM fixtures WHERE (home_team_id=? OR away_team_id=?) AND {_FIN90} "
                     "ORDER BY date DESC LIMIT 1", (team_id, team_id))
        if not ult:
            return {}
        filas = _query("SELECT jugador_id, detalle FROM fixture_eventos WHERE fixture_id=? AND equipo_id=? "
                       "AND tipo='Card' AND jugador_id > 0", (ult[0]["id"], team_id))
    except Exception:  # noqa: BLE001 — base sin la ficha de partido
        return {}
    fecha = str(ult[0]["date"] or "")[:10]
    out = {}
    for f in filas:
        det = (f["detalle"] or "").lower()
        if "red" in det or "second yellow" in det:
            out[f["jugador_id"]] = {"player_id": f["jugador_id"], "tipo": "Suspended",
                                    "detalle": f"Red Card ({f['detalle']} el {fecha}, de nuestra ficha)",
                                    "fecha": fecha}
    return out


def ultimo_partido_jugado(team_id: int) -> dict[int, str]:
    """{jugador: fecha del último partido TERMINADO del equipo en que fue
    titular o figura en un evento (gol, tarjeta, cambio)}. Es lo que desmiente
    una baja: Prass titular y goleador del Hoffenheim, Lerma entrando al 53'
    del Palace, Brugui titular con dos goles, todos «de baja» en la base."""
    out: dict[int, str] = {}
    for sql in (f"""SELECT a.player_id AS pid, MAX(f.date) AS d FROM alineaciones a
                    JOIN fixtures f ON f.id = a.fixture_id
                    WHERE a.team_id=? AND a.titular=1 AND {_FIN90.replace('status', 'f.status')} GROUP BY a.player_id""",
                f"""SELECT e.jugador_id AS pid, MAX(f.date) AS d FROM fixture_eventos e
                    JOIN fixtures f ON f.id = e.fixture_id
                    WHERE e.equipo_id=? AND e.jugador_id > 0 AND {_FIN90.replace('status', 'f.status')} GROUP BY e.jugador_id""",
                f"""SELECT e.asistente_id AS pid, MAX(f.date) AS d FROM fixture_eventos e
                    JOIN fixtures f ON f.id = e.fixture_id
                    WHERE e.equipo_id=? AND e.asistente_id > 0 AND {_FIN90.replace('status', 'f.status')} GROUP BY e.asistente_id"""):
        try:
            for r in _query(sql, (team_id,)):
                if r["pid"] and r["d"] and str(r["d"]) > out.get(r["pid"], ""):
                    out[r["pid"]] = str(r["d"])
        except Exception:  # noqa: BLE001 — base sin la ficha de partido
            continue
    return out


def _baja_dto(baja, missing: dict, jugo_el: str | None) -> dict:
    """La baja con su lectura. `desmentida`: el jugador jugó (titular o con un
    evento) un partido POSTERIOR a la fecha de la baja —la API la dejó vieja—,
    y entonces no cuenta como baja en ningún lado (incidencias 2, 132, 142,
    143, 149, 167, 312; pedido del usuario 22/10/2026). Sin fecha de la baja no
    hay contra qué comparar y queda como venía."""
    lectura = missing["lectura"] if _es_missing(baja["tipo"]) else "senal"
    # UNA SANCIÓN ES SEÑAL SIEMPRE (incidencias 71 y 415, usuario 24/10/2026):
    # roja, acumulación de amarillas o suspensión son registros disciplinarios
    # de la liga, no la marca genérica de «no jugó». Vinícius (4 fechas por
    # roja) y Taliari (amarillas) salían «ruido» por la densidad del equipo.
    sancion = es_sancion(baja["detalle"])
    if sancion and lectura == "ruido":
        lectura = "senal"
    fecha = str(baja["fecha"] or "")[:10] if "fecha" in baja.keys() else ""
    out = {"tipo": baja["tipo"], "detalle": baja["detalle"], "lectura": lectura,
           **({"sancion": True} if sancion else {})}
    if fecha and jugo_el and jugo_el[:10] > fecha:
        out.update({"lectura": "desmentida", "lecturaApi": lectura,
                    "desmentidaPorOnce": {"fechaBaja": fecha, "jugoEl": jugo_el[:10]}})
    return out


def _es_missing(tipo) -> bool:
    return (tipo or "").strip().lower() == "missing fixture"


_SANCION = ("red card", "yellow card", "suspen", "sanci", "ban")


def es_sancion(detalle) -> bool:
    """«Red Card», «Yellow Cards», «Suspended»…: el motivo es disciplinario."""
    d = (detalle or "").strip().lower()
    return any(d.startswith(s) or f" {s}" in d for s in _SANCION)


def _desmentida(b, jugo_el: str | None) -> bool:
    fecha = str(b["fecha"] or "")[:10] if "fecha" in b.keys() else ""
    return bool(fecha and jugo_el and jugo_el[:10] > fecha)


def lectura_missing_fixture(bajas: dict, plantilla_ids: set, jugo: dict | None = None) -> dict:
    """Cuántos de la plantilla trae marcados como «Missing Fixture» y qué
    lectura merece: `senal` (pocos: bajas reales) o `ruido` (media plantilla:
    la API marcó a todo el que no jugó un partido). La densidad se mide
    contra la plantilla capturada, no contra la lista de bajas.

    SOLO CUENTAN LAS MARCAS VIGENTES (incidencias 71, 312 y 415, usuario
    24/10/2026): la API deja la marca puesta después de que el jugador volvió
    a jugar, y esas viejas —ya `desmentida`— inflaban la densidad. El Real
    Madrid tenía 10 de 30 marcados (33 %, todo «ruido», Vinícius incluido),
    pero 7 ya habían jugado después: vigentes, 3 de 30 (10 %, señal)."""
    jugo = jugo or {}
    total = len(plantilla_ids)
    marcas = [(pid, b) for pid, b in bajas.items() if pid in plantilla_ids and _es_missing(b["tipo"])]
    vigentes = [pid for pid, b in marcas if not _desmentida(b, jugo.get(pid))]
    marcados = len(vigentes)
    densidad = round(marcados / total, 3) if total else 0.0
    return {
        "marcados": marcados,
        "desmentidas": len(marcas) - marcados,
        "plantilla": total,
        "densidad": densidad,
        "umbral": UMBRAL_MISSING_FIXTURE,
        "lectura": "ruido" if (marcados and densidad > UMBRAL_MISSING_FIXTURE) else "senal",
    }


def es_baja_real(j: dict) -> bool:
    """Baja que cuenta: la que trae lectura de señal (o sin lectura, por si
    llega de un DTO viejo). Un flag de ruido no es una baja."""
    b = j.get("baja")
    return bool(b) and b.get("lectura") not in ("ruido", "desmentida")


def _congestion(team_id: int, fecha_fixture: str) -> dict:
    """Días de descanso y partidos en los últimos 21 días ANTES del fixture —
    sale de fixtures ya capturados (spec §11, 0 requests). Sin amistosos: el
    de Mainz con el Waldhof Mannheim contaba como partido de los 21 días en el
    F2 del TDE (incidencia 471)."""
    from backend.analisis.escala import AMISTOSOS
    fecha = fecha_fixture.replace("T", " ").rstrip("Z")
    previos = _query(
        f"""SELECT date FROM fixtures
            WHERE (home_team_id=? OR away_team_id=?) AND date < ? AND {_FIN90}
              AND COALESCE(league_id, 0) NOT IN ({",".join("?" * len(AMISTOSOS))})
            ORDER BY date DESC LIMIT 12""",
        (team_id, team_id, fecha, *sorted(AMISTOSOS)),
    )
    if not previos:
        return {"diasDescanso": None, "partidos21d": 0}
    d_fix = datetime.strptime(fecha[:10], "%Y-%m-%d")
    ultimo = datetime.strptime(str(previos[0]["date"])[:10], "%Y-%m-%d")
    corte = d_fix - timedelta(days=CONGESTION_DIAS)
    en_ventana = sum(
        1 for r in previos if datetime.strptime(str(r["date"])[:10], "%Y-%m-%d") >= corte
    )
    return {"diasDescanso": dias_descanso(str(previos[0]["date"]), fecha), "partidos21d": en_ventana}


def dias_descanso(desde: str, hasta: str) -> int | None:
    """Días ENTEROS entre dos saques, por las horas y no por el día del
    calendario en UTC (incidencia 769: Inter de Bogotá del 25/10 21:05 al 29/10
    01:05 UTC son ~3,2 días y salían 4 —el partido de la noche de Sudamérica cae
    al día siguiente en UTC—, y el F2 del TDE quedaba en el tramo de 4-5)."""
    def _dt(t: str) -> datetime | None:
        t = str(t or "").replace("T", " ").rstrip("Z")[:19]
        for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(t, f)
            except ValueError:
                continue
        return None
    a, b = _dt(desde), _dt(hasta)
    if not a or not b:
        return None
    return int((b - a).total_seconds() // 86400)


def ficha_partido(fixture_id: int) -> dict | None:
    """FichaPartidoDTO: plantilla + congestión de ambos equipos. None si el
    fixture no existe (el endpoint lo convierte en 404)."""
    fila = db.query_one(
        "sad",
        "SELECT f.id, f.date, f.home_team_id, f.away_team_id, "
        "ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
        "JOIN teams at ON at.id=f.away_team_id WHERE f.id=?",
        (fixture_id,),
    )
    if not fila:
        return None
    lados = {}
    for lado, tid, nombre in (("local", fila["home_team_id"], fila["home_name"]),
                              ("visitante", fila["away_team_id"], fila["away_name"])):
        p = plantilla_de(tid)
        p["nombre"] = nombre
        p["congestion"] = _congestion(tid, str(fila["date"]))
        lados[lado] = p
    from backend import ficha_tactica
    return {
        "fixtureId": fixture_id,
        "generadoEn": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "local": lados["local"],
        "visitante": lados["visitante"],
        # materia prima del DTP (docs/efe-dtp/DTP_DISENO.md): XI con carriles,
        # goles con autor y asistente, y métricas del partido. Vacío si la
        # ingesta aún no capturó la ficha — nunca reconstruido a ojo.
        "tactica": ficha_tactica.tactica_de(fixture_id, fila["home_team_id"], fila["away_team_id"]),
        # QUIÉN PASÓ LA LLAVE (incidencia 774): los `Shootout` de los eventos no
        # se cuentan a mano; null si no es eliminatoria o no se sabe
        "eliminatoria": _eliminatoria(fixture_id, fila["home_team_id"]),
    }


def _eliminatoria(fixture_id: int, local_id: int) -> dict | None:
    from backend import eliminatoria
    d = eliminatoria.desenlace(fixture_id)
    if not d:
        return None
    lado = ("local" if d["avanza"] == local_id else "visitante") if d.get("avanza") else None
    return {**d, "avanzaLado": lado}


# ── resúmenes de texto para el cruce con los skills (EFE / timeline) ─────────

def _linea_jugador(j: dict) -> str:
    partes = [f"{j['nombre']} ({j['posicion'] or '?'})",
              f"{j['minutos']} min ({round(j['pctMinutos'] * 100)}%)"]
    if j["paradasP90"] is not None:
        partes.append(f"{j['paradasP90']} paradas/90, {j['golesEncajadosP90']} GC/90")
    else:
        partes.append(f"{j['goles']}G+{j['asistencias']}A"
                      + (f" ({round(j['participacionOfensiva'] * 100)}% del equipo)"
                         if j["participacionOfensiva"] >= 0.1 else ""))
    if j["rating"] is not None:
        partes.append(f"rating {j['rating']}")
    partes.append(f"confianza {j['confianza']}")
    if es_baja_real(j):
        partes.append(f"BAJA: {j['baja']['detalle'] or j['baja']['tipo'] or 'sin detalle'}")
    if j["enCapilla"]:
        partes.append(f"en capilla ({j['amarillas']} amarillas)")
    if j["recienLlegado"]:
        partes.append(f"recién llegado de {j['recienLlegado']['desde'] or '?'} ({j['recienLlegado']['fecha']})")
    return " · ".join(partes)


def resumen_para_skills(team_id: int) -> dict[str, str]:
    """Textos cuantitativos para datos_cacheados del EFE (tipos plantel/dt/bajas)
    y para el timeline (movimientos_db). {} si no hay ingesta de jugadores:
    el skill sigue con búsqueda web como siempre."""
    p = plantilla_de(team_id)
    if not p["jugadores"]:
        return {}
    out: dict[str, str] = {}
    relevantes = [j for j in p["jugadores"] if j["pctMinutos"] >= 0.25][:18]
    lineas = "; ".join(_linea_jugador(j) for j in relevantes)
    dep = p["dependencia"]
    extra = ""
    if dep["hhi"] is not None and dep["top"]:
        tops = ", ".join(
            "{} {}%".format(t["nombre"], round(t["participacion"] * 100)) for t in dep["top"]
        )
        extra = f" Dependencia ofensiva HHI {dep['hhi']} (top: {tops})."
    rev = p["revolucion"]
    pap = rev.get("enPapeles") or {}
    if rev["llegadas"] or rev["salidas"] or pap.get("llegadas") or pap.get("salidas"):
        extra += (f" Ventana reciente ({rev['ventanaDias']}d): {rev['llegadas']} llegadas y {rev['salidas']} salidas "
                  "con minutos en el primer equipo"
                  + (f" (en papeles: {pap.get('llegadas', 0)} y {pap.get('salidas', 0)}, con cesiones y juveniles)"
                     if pap else "") + ".")
    if p.get("origenTemporada") == "anterior":
        extra += (f" OJO: la API aún no publica la temporada en curso; estas stats son de la ANTERIOR "
                  f"({p['temporada']}), solo de los que siguen en el plantel.")
    if p.get("plantelSinStats"):
        extra += (" En el plantel actual sin stats de esa temporada (llegaron después): "
                  + ", ".join(j["nombre"] for j in p["plantelSinStats"][:12]) + ".")
    out["plantel"] = (f"Plantilla con indicadores calculados de nuestra base (temporada {p['temporada']}): "
                      + lineas + "." + extra + " [fuente: sad.db jugadores]")
    if p["entrenador"]:
        out["dt"] = (f"DT actual: {p['entrenador']['nombre']}"
                     + (f", en el cargo desde {p['entrenador']['desde']}" if p["entrenador"]["desde"] else "")
                     + ". [fuente: sad.db entrenadores]")
    bajas = [j for j in p["jugadores"] if es_baja_real(j)]
    mf = p.get("missingFixture")
    ruido = (f" La API marca «Missing Fixture» a {mf['marcados']} de {mf['plantilla']} jugadores "
             f"({round(mf['densidad'] * 100)}% de la plantilla, umbral {round(mf['umbral'] * 100)}%): "
             "densidad de ruido, no se listan como bajas; confirmá las bajas en prensa."
             if mf and mf["lectura"] == "ruido" else "")
    if bajas:
        out["bajas"] = ("Bajas con su peso real: " + "; ".join(
            f"{j['nombre']} ({j['baja']['detalle'] or j['baja']['tipo'] or 'baja'}) — "
            f"{round(j['pctMinutos'] * 100)}% de minutos, "
            f"{round(j['participacionOfensiva'] * 100)}% de la producción"
            for j in bajas
        ) + "." + ruido + " [fuente: sad.db jugador_bajas]")
    elif ruido:
        out["bajas"] = "Sin bajas de señal en la base." + ruido + " [fuente: sad.db jugador_bajas]"
    return out


def movimientos_para_timeline(team_id: int, dias: int = 182) -> str:
    """Traspasos (in/out) y DT vigente con fechas exactas, como eventos
    confirmados para el timeline. '' si no hay nada."""
    corte = (datetime.now(timezone.utc) - timedelta(days=dias)).strftime("%Y-%m-%d")
    movs = _query(
        """SELECT t.fecha, t.tipo, t.team_in, t.team_in_nombre, t.team_out_nombre, j.nombre
           FROM traspasos t JOIN jugadores j ON j.id = t.player_id
           WHERE (t.team_in=? OR t.team_out=?) AND t.fecha >= ? ORDER BY t.fecha DESC LIMIT 20""",
        (team_id, team_id, corte),
    )
    partes = [
        f"{m['fecha']}: {m['nombre']} "
        + (f"llega de {m['team_out_nombre'] or '?'}" if m["team_in"] == team_id
           else f"sale hacia {m['team_in_nombre'] or '?'}")
        + (f" ({m['tipo']})" if m["tipo"] else "")
        for m in movs
    ]
    dt = _query("SELECT nombre, desde FROM entrenadores WHERE team_id=? LIMIT 1", (team_id,))
    if dt:
        partes.append(f"DT vigente: {dt[0]['nombre']}"
                      + (f" desde {dt[0]['desde']}" if dt[0]["desde"] else ""))
    return ("Movimientos confirmados de nuestra base: " + " · ".join(partes)
            + " [fuente: sad.db traspasos/entrenadores]") if partes else ""
