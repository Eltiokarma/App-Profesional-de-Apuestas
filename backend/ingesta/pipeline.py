"""Orquestador del pipeline de cálculo: sad.db → levels/constants/discreto.

Recompute COMPLETO (drop + regenerar): el pipeline viejo era incremental y por
eso acumuló staleness (INFORME_INGESTA.md); con 117k fixtures el recálculo
entero tarda segundos, así que la simplicidad gana.

Solo lee sad.db; escribe las tres DBs derivadas en --out (nunca en sitio sin
pedirlo explícitamente).

Uso: PYTHONUTF8=1 python -m backend.ingesta.pipeline --out ./derivadas [--sad sad.db]
"""
import argparse
import os
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import datetime

from backend.ingesta.constantes import COLUMNAS, calcular_constantes
from backend.ingesta.discretizador import DiscretizadorUniforme, fusion
from backend.ingesta.niveles import CacheNiveles, calcular_niveles

DDL_LEVELS = """
DROP TABLE IF EXISTS team_levels;
CREATE TABLE team_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    fixture_id INTEGER NOT NULL,
    date DATETIME NOT NULL,
    level FLOAT NOT NULL,
    UNIQUE (team_id, fixture_id)
);
CREATE INDEX idx_levels_team_date ON team_levels(team_id, date);
"""

DDL_CONSTANTS = """
DROP TABLE IF EXISTS constants;
CREATE TABLE constants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    fixture_id INTEGER NOT NULL,
    date DATETIME NOT NULL,
    {cols},
    UNIQUE (team_id, fixture_id)
);
CREATE INDEX idx_constants_team_date ON constants(team_id, date);
"""

DDL_DISCRETO = """
DROP TABLE IF EXISTS processed_matches;
CREATE TABLE processed_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATETIME,
    fixture_id INTEGER,
    equipo_id INTEGER,
    equipo_nombre VARCHAR,
    rival_id INTEGER,
    rival_nombre VARCHAR,
    condicion VARCHAR,
    status_long VARCHAR,
    league_id INTEGER,
    league_season VARCHAR,
    goals_home INTEGER,
    goals_away INTEGER,
    nivel_equipo INTEGER,
    nivel_rival INTEGER,
    k FLOAT,
    k_local FLOAT,
    k_visita FLOAT,
    k_goles_anotado FLOAT,
    k_goles_recibido FLOAT,
    k_goles_local_anotado FLOAT,
    k_goles_local_recibido FLOAT,
    k_goles_visita_anotado FLOAT,
    k_goles_visita_recibido FLOAT,
    processed_at DATETIME,
    UNIQUE (fixture_id, equipo_id)
);
CREATE INDEX idx_fecha_equipo ON processed_matches(fecha, equipo_id);
CREATE INDEX idx_status ON processed_matches(status_long);
CREATE INDEX idx_league ON processed_matches(league_id);
"""


def leer_fixtures(sad_path: str) -> list[tuple]:
    """Partidos terminados con goles, orden (date, id) — el orden del motor.

    REGLA SAGRADA: la K se calcula con el resultado DENTRO DE LOS 90 MINUTOS
    (fulltime_*), no con el final tras prórroga o penales — en un AET/PEN
    goals_* trae el marcador de los 120'. COALESCE cubre DBs sin fulltime.
    El filtro por status_short incluye AET/PEN (su status_long varía)."""
    with sqlite3.connect(f"file:{sad_path}?mode=ro", uri=True) as con:
        return con.execute(
            """SELECT id, date, home_team_id, away_team_id,
                      COALESCE(fulltime_home, goals_home) AS goals_home,
                      COALESCE(fulltime_away, goals_away) AS goals_away,
                      status_long, league_id, league_season
               FROM fixtures
               WHERE (status_short IN ('FT', 'AET', 'PEN') OR status_long = 'Match Finished')
                 AND COALESCE(fulltime_home, goals_home) IS NOT NULL
                 AND COALESCE(fulltime_away, goals_away) IS NOT NULL
               ORDER BY date, id"""
        ).fetchall()


def leer_nombres(sad_path: str) -> dict[int, str]:
    with sqlite3.connect(f"file:{sad_path}?mode=ro", uri=True) as con:
        return dict(con.execute("SELECT id, name FROM teams"))


def construir_historias(fixtures) -> dict[int, list[tuple]]:
    """team_id → [(fixture_id, date, is_local, gf, ga, rival_id)] ordenada."""
    hist: dict[int, list[tuple]] = defaultdict(list)
    for fid, date, home, away, gh, ga, *_ in fixtures:
        hist[home].append((fid, date, True, gh, ga, away))
        hist[away].append((fid, date, False, ga, gh, home))
    return hist


def _crear_db(path: str, ddl: str) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.executescript(ddl)
    return con


def etapa_niveles(hist, out_dir: str) -> list[tuple]:
    filas = []
    for team_id, h in hist.items():
        propia = [(f, d, gf, ga) for f, d, _, gf, ga, _ in h]
        filas.extend((team_id, f, d, lvl) for f, d, lvl in calcular_niveles(propia))
    con = _crear_db(os.path.join(out_dir, "levels.db"), DDL_LEVELS)
    with con:
        con.executemany(
            "INSERT INTO team_levels (team_id, fixture_id, date, level) VALUES (?, ?, ?, ?)",
            filas,
        )
    con.close()
    return filas


def etapa_constantes(hist, niveles: CacheNiveles, out_dir: str) -> dict[tuple, dict]:
    por_clave: dict[tuple, dict] = {}
    for team_id, h in hist.items():
        for fila in calcular_constantes(h, niveles):
            por_clave[(team_id, fila["fixture_id"])] = fila
    ddl = DDL_CONSTANTS.format(cols=",\n    ".join(f"{c} FLOAT" for c in COLUMNAS))
    con = _crear_db(os.path.join(out_dir, "constants.db"), ddl)
    marcas = ", ".join("?" * (3 + len(COLUMNAS)))
    with con:
        con.executemany(
            f"INSERT INTO constants (team_id, fixture_id, date, {', '.join(COLUMNAS)}) "
            f"VALUES ({marcas})",
            (
                (t, f, fila["date"], *(fila[c] for c in COLUMNAS))
                for (t, f), fila in por_clave.items()
            ),
        )
    con.close()
    return por_clave


def etapa_discreto(fixtures, filas_niveles, constantes, nombres, out_dir: str) -> int:
    exacto = {(t, f): lvl for t, f, _, lvl in filas_niveles}
    niveles = [lvl for *_, lvl in filas_niveles]
    disc = DiscretizadorUniforme(min(niveles), max(niveles))
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    filas = []
    for fid, date, home, away, gh, ga, status, liga, season in fixtures:
        for equipo, rival, es_local in ((home, away, True), (away, home, False)):
            c = constantes[(equipo, fid)]
            filas.append((
                date, fid, equipo, nombres.get(equipo), rival, nombres.get(rival),
                "Local" if es_local else "Visita", status, liga, str(season), gh, ga,
                disc.bin(exacto[(equipo, fid)]), disc.bin(exacto[(rival, fid)]),
                fusion(c["k_positivo"], c["k_negativo"]),
                fusion(c["k_positivo_local"], c["k_negativo_local"]),
                fusion(c["k_positivo_visita"], c["k_negativo_visita"]),
                c["k_goles_anotado"], c["k_goles_recibido"],
                c["k_goles_local_anotado"], c["k_goles_local_recibido"],
                c["k_goles_visita_anotado"], c["k_goles_visita_recibido"],
                ahora,
            ))
    con = _crear_db(os.path.join(out_dir, "discreto.db"), DDL_DISCRETO)
    with con:
        con.executemany(
            """INSERT INTO processed_matches (fecha, fixture_id, equipo_id, equipo_nombre,
               rival_id, rival_nombre, condicion, status_long, league_id, league_season,
               goals_home, goals_away, nivel_equipo, nivel_rival, k, k_local, k_visita,
               k_goles_anotado, k_goles_recibido, k_goles_local_anotado,
               k_goles_local_recibido, k_goles_visita_anotado, k_goles_visita_recibido,
               processed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            filas,
        )
    con.close()
    return len(filas)


def main() -> int:
    ap = argparse.ArgumentParser(description="Pipeline sad.db → levels/constants/discreto")
    ap.add_argument("--sad", default="sad.db", help="ruta a sad.db (solo lectura)")
    ap.add_argument("--out", required=True, help="directorio de salida para las DBs derivadas")
    args = ap.parse_args()

    if not os.path.exists(args.sad):
        print(f"No existe {args.sad}", file=sys.stderr)
        return 1
    os.makedirs(args.out, exist_ok=True)

    t0 = time.perf_counter()
    fixtures = leer_fixtures(args.sad)
    nombres = leer_nombres(args.sad)
    hist = construir_historias(fixtures)
    print(f"sad.db: {len(fixtures)} partidos terminados · {len(hist)} equipos")

    filas_niveles = etapa_niveles(hist, args.out)
    print(f"levels.db: {len(filas_niveles)} filas")

    cache = CacheNiveles((t, d, lvl) for t, _, d, lvl in filas_niveles)
    constantes = etapa_constantes(hist, cache, args.out)
    print(f"constants.db: {len(constantes)} filas")

    n = etapa_discreto(fixtures, filas_niveles, constantes, nombres, args.out)
    print(f"discreto.db: {n} filas")
    print(f"listo en {time.perf_counter() - t0:.1f} s → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
