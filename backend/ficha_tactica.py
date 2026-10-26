"""Lectura de la ficha TÁCTICA de un partido: alineaciones, eventos y stats.

Solo lee (backend/ingesta/ficha_partido.py es quien escribe). Es la materia
prima de los módulos del DTP: M1/M6 leen el XI y la formación, M2 los carriles
(el `grid` de cada titular), M4 los goles con minuto, autor y asistente.

Regla "real o nada": lo que no se haya capturado va vacío. Un partido sin
alineación devuelve `alineaciones` vacías, no un XI reconstruido a ojo — el
DTP tiene que poder negarse a abrir, y para eso necesita ver el hueco.
"""
from backend.nombres import limpiar_nombre
from backend import db

# los carriles de M2 salen del grid "fila:columna" de API-Football: la fila es
# la línea (1 = arquero) y la columna, la posición de izquierda a derecha DEL
# EQUIPO. Con 3 columnas o menos no hay "carril interior" que valga.
CARRILES = ("izquierda", "centro", "derecha")


def _carril(grid: str | None, por_fila: dict[int, int]) -> str | None:
    """Carril a partir del grid, normalizado por cuánta gente hay en su línea:
    un 2:1 en línea de 4 es lateral izquierdo; en línea de 3, central izquierdo.
    Sin grid no se inventa: None (y el DTP lo verá como dato faltante)."""
    if not grid or ":" not in grid:
        return None
    try:
        fila, col = (int(x) for x in grid.split(":", 1))
    except ValueError:
        return None
    total = por_fila.get(fila, 1)
    if total <= 1:
        return "centro"
    # tercios: con 4 en la línea → 1 izq, 2-3 centro, 4 der
    idx = (col - 1) / max(total - 1, 1)
    return CARRILES[0] if idx < 0.34 else (CARRILES[2] if idx > 0.66 else CARRILES[1])


def _plantilla(team_id: int) -> list[tuple[int, str]]:
    """(id, nombre) de la plantilla del equipo en la base: stats de cualquier
    temporada y el plantel actual. Vacía si la capa de jugadores no está."""
    out: dict[int, str] = {}
    for sql in ("SELECT j.id AS id, j.nombre AS nombre FROM jugador_stats s JOIN jugadores j ON j.id = s.player_id "
                "WHERE s.team_id=?",
                "SELECT player_id AS id, nombre FROM plantel_actual WHERE team_id=?"):
        try:
            for f in db.query("sad", sql, (team_id,)):
                if f["id"] and f["id"] > 0 and f["nombre"]:
                    out.setdefault(int(f["id"]), limpiar_nombre(f["nombre"]))
        except Exception:  # noqa: BLE001 — base sin la capa de jugadores
            continue
    return list(out.items())


def _id_por_nombre(nombre: str | None, plantilla: list[tuple[int, str]]) -> int | None:
    """EL ID QUE LA API NO MANDÓ. Javier Orantes titular con id negativo
    (incidencia 125) y Kamissoko con el gol y el cambio en null (166) están en
    la plantilla con su id: si el nombre casa con UN solo jugador de la
    plantilla, ese es el id. Con dos o ninguno, se deja como vino."""
    if not nombre or not plantilla:
        return None
    from backend.analisis.bloque_f import _casa, _tokens
    th = _tokens(nombre)
    hits = [pid for pid, n in plantilla if _casa(_tokens(n), th) or _casa(th, _tokens(n))]
    return hits[0] if len(set(hits)) == 1 else None


def _lado(fixture_id: int, team_id: int) -> dict:
    filas = db.query(
        "sad",
        "SELECT formacion, entrenador, player_id, jugador, numero, posicion, grid, titular "
        "FROM alineaciones WHERE fixture_id=? AND team_id=? ORDER BY titular DESC, numero",
        (fixture_id, team_id),
    )
    if not filas:
        return {"equipoId": team_id, "formacion": None, "entrenador": None,
                "titulares": [], "suplentes": [], "conGrid": False}
    por_fila: dict[int, int] = {}
    for f in filas:
        if f["titular"] and f["grid"] and ":" in f["grid"]:
            try:
                por_fila[int(f["grid"].split(":", 1)[0])] = por_fila.get(int(f["grid"].split(":", 1)[0]), 0) + 1
            except ValueError:
                pass
    titulares, suplentes = [], []
    plantilla = None
    # un id que ya trae otro jugador de esta misma hoja no se le asigna a este:
    # «Luciano Rodriguez» #37 quedaba con el id de «L. Rodríguez» #23, otro
    # titular del mismo once (Nacional, incidencia 645)
    en_hoja = {f["player_id"] for f in filas if f["player_id"] and f["player_id"] > 0}
    for f in filas:
        pid = f["player_id"]
        j = {"jugadorId": pid, "nombre": limpiar_nombre(f["jugador"]), "numero": f["numero"],
             "posicion": f["posicion"], "grid": f["grid"],
             "carril": _carril(f["grid"], por_fila) if f["titular"] else None}
        if not pid or pid < 0:
            plantilla = _plantilla(team_id) if plantilla is None else plantilla
            resuelto = _id_por_nombre(j["nombre"], plantilla)
            if resuelto and resuelto not in en_hoja:
                j.update({"jugadorId": resuelto, "jugadorIdResuelto": True})
                en_hoja.add(resuelto)
        (titulares if f["titular"] else suplentes).append(j)
    return {
        "equipoId": team_id,
        "formacion": filas[0]["formacion"],
        "entrenador": filas[0]["entrenador"],
        "titulares": titulares,
        "suplentes": suplentes,
        # el DTP necesita saber si puede hablar de carriles o no
        "conGrid": any(t["carril"] for t in titulares),
    }


def _eventos(fixture_id: int) -> list[dict]:
    try:
        filas = db.query(
            "sad",
            "SELECT minuto, extra, tipo, detalle, equipo_id, jugador, jugador_id, "
            "asistente, asistente_id FROM fixture_eventos WHERE fixture_id=? ORDER BY minuto, id",
            (fixture_id,),
        )
    except Exception:
        return []  # DB anterior a la migración
    out = [
        {"minuto": f["minuto"], "extra": f["extra"] or 0, "tipo": f["tipo"], "detalle": f["detalle"],
         "equipoId": f["equipo_id"], "jugador": limpiar_nombre(f["jugador"]), "jugadorId": f["jugador_id"],
         "asistente": limpiar_nombre(f["asistente"]), "asistenteId": f["asistente_id"]}
        for f in filas
    ]
    _cuerpo_tecnico_e_ids(fixture_id, out)
    return out


def _dts(fixture_id: int, team_id: int) -> list[str]:
    nombres = []
    for sql, args in (("SELECT DISTINCT entrenador AS n FROM alineaciones WHERE fixture_id=? AND team_id=?",
                       (fixture_id, team_id)),
                      ("SELECT nombre AS n FROM entrenadores WHERE team_id=? ORDER BY actualizado_en DESC LIMIT 2",
                       (team_id,))):
        try:
            nombres += [limpiar_nombre(f["n"]) for f in db.query("sad", sql, args) if f["n"]]
        except Exception:  # noqa: BLE001
            continue
    return nombres


def _cuerpo_tecnico_e_ids(fixture_id: int, eventos: list[dict]) -> None:
    """LA TARJETA AL DT NO ES DE UN JUGADOR. «G. Umana» (Umaña, el DT) iba como
    amonestado sin id (incidencia 364) y la amarilla a Diego Simeone, con el id
    de Giuliano, su hijo titular (155): las dos se contaban en el once. Una
    tarjeta cuyo nombre casa con el DT del equipo, y no con el jugador del id
    que trae, se marca `cuerpoTecnico` y pierde el id. Y un evento de jugador
    sin id toma el de la plantilla si el nombre casa con uno solo (166)."""
    from backend.analisis.bloque_f import _casa, _tokens
    dts: dict[int, list[str]] = {}
    plantillas: dict[int, list[tuple[int, str]]] = {}
    for e in eventos:
        tid = e.get("equipoId")
        if not tid or not e.get("jugador"):
            continue
        te = _tokens(e["jugador"])
        if (e.get("tipo") or "").lower() == "card":
            if tid not in dts:
                dts[tid] = _dts(fixture_id, tid)
            if any(_casa(_tokens(d), te) for d in dts[tid]):
                del_id = None
                if e.get("jugadorId"):
                    if tid not in plantillas:
                        plantillas[tid] = _plantilla(tid)
                    del_id = dict(plantillas[tid]).get(e["jugadorId"])
                if not del_id or not _casa(_tokens(del_id), te):
                    e.update({"cuerpoTecnico": True, "jugadorIdApi": e.get("jugadorId"), "jugadorId": None})
                    continue
        if not e.get("jugadorId") or e["jugadorId"] < 0:
            if tid not in plantillas:
                plantillas[tid] = _plantilla(tid)
            r = _id_por_nombre(e["jugador"], plantillas[tid])
            if r:
                e.update({"jugadorId": r, "jugadorIdResuelto": True})


def _stats(fixture_id: int, team_id: int) -> dict:
    try:
        filas = db.query(
            "sad", "SELECT clave, valor FROM fixture_stats WHERE fixture_id=? AND team_id=?",
            (fixture_id, team_id),
        )
    except Exception:
        return {}
    return {f["clave"]: f["valor"] for f in filas if f["valor"] is not None}


def tactica_de(fixture_id: int, home_id: int, away_id: int) -> dict:
    """Bloque `tactica` de la ficha. Todo vacío si no se capturó nada."""
    try:
        local, visitante = _lado(fixture_id, home_id), _lado(fixture_id, away_id)
    except Exception:
        local = visitante = None
    if local is None:  # DB sin la tabla (anterior a la fase A del DTP)
        return {"alineaciones": None, "eventos": [], "estadisticas": None, "capturada": False}
    eventos = _eventos(fixture_id)
    return {
        "alineaciones": {"local": local, "visitante": visitante},
        "eventos": eventos,
        "estadisticas": {"local": _stats(fixture_id, home_id),
                         "visitante": _stats(fixture_id, away_id)},
        # lo que el DTP mira antes de decidir si puede abrir
        "capturada": bool(local["titulares"] or visitante["titulares"] or eventos),
    }


# ── promedios avanzados de un equipo (xG, posesión, tiros, córners) ──────────
# Salen de las stats por partido que ya ingestó ficha_partido. La ingesta no
# las pide para todos los partidos (solo los últimos de equipos con un NS
# próximo), así que cada promedio viaja con SU muestra: un xG sobre 2 partidos
# no es el xG del equipo, y la pantalla lo tiene que poder decir.
VENTANA_AVANZADAS = 10
_CLAVES_AVANZADAS = {
    "xg": "expected_goals",
    "posesion": "Ball Possession",
    "tirosPuerta": "Shots on Goal",
    "corners": "Corner Kicks",
}


def _num(valor) -> float | None:
    """'58%' → 58, '1.42' → 1.42. Lo que no se lee como número no cuenta
    (un null de la API es «sin dato», no un cero)."""
    if valor is None:
        return None
    try:
        return float(str(valor).strip().rstrip("%"))
    except ValueError:
        return None


def promedios_avanzados(team_id: int, ventana: int = VENTANA_AVANZADAS) -> dict:
    """Promedio de los últimos `ventana` partidos TERMINADOS del equipo que
    tienen stats capturadas. Cada métrica se promedia sobre los partidos
    donde vino (el xG llega en menos ligas que la posesión) y trae su `n`;
    sin partidos con esa métrica, None. `xgContra` es el xG del rival."""
    vacio = {"partidos": 0, **{k: None for k in _CLAVES_AVANZADAS}, "xgContra": None,
             "n": {**{k: 0 for k in _CLAVES_AVANZADAS}, "xgContra": 0}}
    try:
        fxs = db.query(
            "sad",
            "SELECT f.id FROM fixtures f "
            "WHERE (f.home_team_id=? OR f.away_team_id=?) "
            "AND (f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished') "
            "AND EXISTS (SELECT 1 FROM fixture_stats s WHERE s.fixture_id=f.id AND s.team_id=?) "
            "ORDER BY f.date DESC LIMIT ?",
            (team_id, team_id, team_id, ventana),
        )
    except Exception:
        return vacio  # DB anterior a la tabla fixture_stats
    ids = [f["id"] for f in fxs]
    if not ids:
        return vacio
    marcas = ",".join("?" * len(ids))
    filas = db.query(
        "sad",
        f"SELECT fixture_id, team_id, clave, valor FROM fixture_stats "
        f"WHERE fixture_id IN ({marcas}) AND clave IN ({','.join('?' * len(_CLAVES_AVANZADAS))})",
        (*ids, *_CLAVES_AVANZADAS.values()),
    )
    propio: dict[str, list[float]] = {k: [] for k in _CLAVES_AVANZADAS}
    xg_contra: list[float] = []
    clave_a_campo = {v: k for k, v in _CLAVES_AVANZADAS.items()}
    for f in filas:
        v = _num(f["valor"])
        if v is None:
            continue
        campo = clave_a_campo[f["clave"]]
        if f["team_id"] == team_id:
            propio[campo].append(v)
        elif campo == "xg":
            xg_contra.append(v)
    prom = lambda xs, d: round(sum(xs) / len(xs), d) if xs else None  # noqa: E731
    return {
        "partidos": len(ids),
        "xg": prom(propio["xg"], 2),
        "posesion": prom(propio["posesion"], 1),
        "tirosPuerta": prom(propio["tirosPuerta"], 1),
        "corners": prom(propio["corners"], 1),
        "xgContra": prom(xg_contra, 2),
        "n": {**{k: len(v) for k, v in propio.items()}, "xgContra": len(xg_contra)},
    }
