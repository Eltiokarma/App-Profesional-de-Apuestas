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

POSICIONES = {
    "Goalkeeper": "Portero",
    "Defender": "Defensa",
    "Midfielder": "Centrocampista",
    "Attacker": "Delantero",
}

_FIN90 = "(status_short IN ('FT','AET','PEN') OR status_long='Match Finished')"


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
    if not filas:
        return base

    hoy = datetime.now(timezone.utc)
    corte_llegada = (hoy - timedelta(days=RECIEN_LLEGADO_DIAS)).strftime("%Y-%m-%d")
    llegadas = {
        r["player_id"]: r for r in _query(
            "SELECT player_id, fecha, team_out_nombre FROM traspasos "
            "WHERE team_in=? AND fecha >= ? ORDER BY fecha DESC",
            (team_id, corte_llegada),
        )
    }
    bajas = {
        r["player_id"]: r for r in _query(
            "SELECT player_id, tipo, detalle FROM jugador_bajas WHERE team_id=?", (team_id,)
        )
    }

    max_minutos = max(r["minutos"] or 0 for r in filas) or 1
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
            "nombre": r["nombre"] or "?",
            "edad": r["edad"],
            "foto": r["foto"],
            "posicion": POSICIONES.get(posicion or "", posicion or ""),
            "partidos": r["partidos"] or 0,
            "titularidades": r["titularidades"] or 0,
            "minutos": minutos,
            "pctMinutos": round(minutos / max_minutos, 3),
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
            "baja": {"tipo": baja["tipo"], "detalle": baja["detalle"]} if baja else None,
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

    dt_filas = _query(
        "SELECT nombre, desde FROM entrenadores WHERE team_id=? ORDER BY actualizado_en DESC LIMIT 1",
        (team_id,),
    )
    salidas = _query(
        "SELECT COUNT(*) AS n FROM traspasos WHERE team_out=? AND fecha >= ?",
        (team_id, (hoy - timedelta(days=REVOLUCION_DIAS)).strftime("%Y-%m-%d")),
    )
    llegadas_n = _query(
        "SELECT COUNT(*) AS n FROM traspasos WHERE team_in=? AND fecha >= ?",
        (team_id, (hoy - timedelta(days=REVOLUCION_DIAS)).strftime("%Y-%m-%d")),
    )
    base.update({
        "entrenador": {"nombre": dt_filas[0]["nombre"], "desde": dt_filas[0]["desde"]} if dt_filas else None,
        "dependencia": {
            "hhi": hhi,
            "top": [
                {"jugadorId": j["id"], "nombre": j["nombre"], "participacion": j["participacionOfensiva"]}
                for j in top
            ],
        },
        "revolucion": {
            "llegadas": llegadas_n[0]["n"] if llegadas_n else 0,
            "salidas": salidas[0]["n"] if salidas else 0,
            "ventanaDias": REVOLUCION_DIAS,
        },
        "jugadores": jugadores,
        # goles del equipo según la plantilla (denominador de participación)
        "golesPlantilla": goles_equipo,
    })
    return base


def _congestion(team_id: int, fecha_fixture: str) -> dict:
    """Días de descanso y partidos en los últimos 21 días ANTES del fixture —
    sale de fixtures ya capturados (spec §11, 0 requests)."""
    fecha = fecha_fixture.replace("T", " ").rstrip("Z")
    previos = _query(
        f"""SELECT date FROM fixtures
            WHERE (home_team_id=? OR away_team_id=?) AND date < ? AND {_FIN90}
            ORDER BY date DESC LIMIT 12""",
        (team_id, team_id, fecha),
    )
    if not previos:
        return {"diasDescanso": None, "partidos21d": 0}
    d_fix = datetime.strptime(fecha[:10], "%Y-%m-%d")
    ultimo = datetime.strptime(str(previos[0]["date"])[:10], "%Y-%m-%d")
    corte = d_fix - timedelta(days=CONGESTION_DIAS)
    en_ventana = sum(
        1 for r in previos if datetime.strptime(str(r["date"])[:10], "%Y-%m-%d") >= corte
    )
    return {"diasDescanso": (d_fix - ultimo).days, "partidos21d": en_ventana}


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
    return {
        "fixtureId": fixture_id,
        "generadoEn": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "local": lados["local"],
        "visitante": lados["visitante"],
    }


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
    if j["baja"]:
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
    if rev["llegadas"] or rev["salidas"]:
        extra += f" Ventana reciente ({rev['ventanaDias']}d): {rev['llegadas']} llegadas, {rev['salidas']} salidas."
    out["plantel"] = (f"Plantilla con indicadores calculados de nuestra base (temporada {p['temporada']}): "
                      + lineas + "." + extra + " [fuente: sad.db jugadores]")
    if p["entrenador"]:
        out["dt"] = (f"DT actual: {p['entrenador']['nombre']}"
                     + (f", en el cargo desde {p['entrenador']['desde']}" if p["entrenador"]["desde"] else "")
                     + ". [fuente: sad.db entrenadores]")
    bajas = [j for j in p["jugadores"] if j["baja"]]
    if bajas:
        out["bajas"] = ("Bajas con su peso real: " + "; ".join(
            f"{j['nombre']} ({j['baja']['detalle'] or j['baja']['tipo'] or 'baja'}) — "
            f"{round(j['pctMinutos'] * 100)}% de minutos, "
            f"{round(j['participacionOfensiva'] * 100)}% de la producción"
            for j in bajas
        ) + ". [fuente: sad.db jugador_bajas]")
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
