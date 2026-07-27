"""Lectura de la ficha TÁCTICA de un partido: alineaciones, eventos y stats.

Solo lee (backend/ingesta/ficha_partido.py es quien escribe). Es la materia
prima de los módulos del DTP: M1/M6 leen el XI y la formación, M2 los carriles
(el `grid` de cada titular), M4 los goles con minuto, autor y asistente.

Regla "real o nada": lo que no se haya capturado va vacío. Un partido sin
alineación devuelve `alineaciones` vacías, no un XI reconstruido a ojo — el
DTP tiene que poder negarse a abrir, y para eso necesita ver el hueco.
"""
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
    for f in filas:
        j = {"jugadorId": f["player_id"], "nombre": f["jugador"], "numero": f["numero"],
             "posicion": f["posicion"], "grid": f["grid"],
             "carril": _carril(f["grid"], por_fila) if f["titular"] else None}
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
    return [
        {"minuto": f["minuto"], "extra": f["extra"] or 0, "tipo": f["tipo"], "detalle": f["detalle"],
         "equipoId": f["equipo_id"], "jugador": f["jugador"], "jugadorId": f["jugador_id"],
         "asistente": f["asistente"], "asistenteId": f["asistente_id"]}
        for f in filas
    ]


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
