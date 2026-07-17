"""Construye la tabla `constants_cuota` (k_cuota, §3.8) sobre los datos reales de
2026, y opcionalmente rellena huecos de cuota con valores sintéticos.

Dos fases (idempotentes):

1. RELLENO SINTÉTICO (§7): para un puñado de equipos elegidos (SYNTH_TEAMS), a sus
   partidos 2026 SIN cuota 1X2 capturada les inyecta cuotas 1X2 aproximadas
   (derivadas de la diferencia de nivel) directamente en la tabla `odds` de sad.db,
   marcadas con `bookmaker_name='SYNTHETIC'` para poder borrarlas cuando llegue la
   cuota real:  DELETE FROM odds WHERE bookmaker_name='SYNTHETIC';
   Se re-borran y re-generan en cada corrida.

2. CONSTANTS_CUOTA: recorre, por equipo, sus partidos 2026 terminados ORDENADOS por
   fecha y acumula los 9 k_cuota (backend/cuota_engine). Reconstruye la tabla entera.

Solo escribe sad.db (odds sintéticas) y constants.db (constants_cuota); levels.db se
abre en solo-lectura. El motor mock/demo NO se toca: las barras se llenan solo aquí.

    python -m backend.backfill_cuota                # SAD_DATA_DIR o raíz; synth por defecto
    python -m backend.backfill_cuota --no-synth     # solo construir desde cuotas reales
    python -m backend.backfill_cuota 541 529 530    # synth solo para esos equipos
"""
import os
import sqlite3
import sys
from bisect import bisect_right

from backend.cuota_engine import CUOTA0, CUOTA_K_COLS, cuotas_sinteticas, step_cuota
from backend.db import BASE_DIR

# Clubes con cobertura 2026 parcial (huecos importantes) para el relleno sintético.
SYNTH_TEAMS = [541, 529, 530, 543, 536, 533, 50, 40, 505, 85]


def _connect(base_dir, name, rw=False):
    path = os.path.join(base_dir, name)
    conn = sqlite3.connect(path) if rw else sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def _levels(base_dir):
    """{team_id: (dates[], levels[])} ordenado, para bisect por fecha."""
    lv = _connect(base_dir, "levels.db")
    by = {}
    for tid, date, level in lv.execute("SELECT team_id, date, level FROM team_levels ORDER BY team_id, date"):
        d, l = by.setdefault(tid, ([], []))
        d.append(date)
        l.append(level)
    lv.close()
    return by


def _nivel_at(by, tid, date):
    d, l = by.get(tid, ([], []))
    i = bisect_right(d, date) - 1
    return l[i] if i >= 0 else 1.0


def _fixtures_2026(sad):
    """Partidos 2026 terminados: id, home, away, gh, ga, date."""
    # regla de 90': fulltime_* manda; el filtro incluye AET/PEN
    return sad.execute(
        "SELECT id, home_team_id, away_team_id, "
        "COALESCE(fulltime_home, goals_home), COALESCE(fulltime_away, goals_away), date "
        "FROM fixtures WHERE date LIKE '2026%' "
        "AND (status_short IN ('FT','AET','PEN') OR status_long='Match Finished')"
    ).fetchall()


def _mw_odds(sad):
    """{fixture_id: (home, draw, away)} promediando bookmakers del mercado 1X2."""
    rows = sad.execute(
        "SELECT fixture_id, value, AVG(odd) FROM odds WHERE bet_name='Match Winner' "
        "GROUP BY fixture_id, value"
    ).fetchall()
    agg = {}
    for fid, value, odd in rows:
        agg.setdefault(fid, {})[value] = odd
    out = {}
    for fid, m in agg.items():
        if "Home" in m and "Draw" in m and "Away" in m:
            out[fid] = (m["Home"], m["Draw"], m["Away"])
    return out


def rellenar_sinteticas(base_dir, teams):
    sad = _connect(base_dir, "sad.db", rw=True)
    lv = _levels(base_dir)
    sad.execute("DELETE FROM odds WHERE bookmaker_name='SYNTHETIC'")
    con_odds = {fid for (fid,) in sad.execute("SELECT DISTINCT fixture_id FROM odds WHERE bet_name='Match Winner'")}
    fixtures = _fixtures_2026(sad)
    por_equipo = {}
    for fid, h, a, gh, ga, date in fixtures:
        por_equipo.setdefault(h, []).append((fid, h, a, date))
        por_equipo.setdefault(a, []).append((fid, h, a, date))
    hechos, filas = set(), 0
    for t in teams:
        for fid, h, a, date in por_equipo.get(t, []):
            if fid in con_odds or fid in hechos:
                continue  # ya tiene cuota (real o de otro equipo synth) → no duplicar
            hechos.add(fid)
            liga = sad.execute("SELECT league_id FROM fixtures WHERE id=?", (fid,)).fetchone()[0]
            ch, cd, ca = cuotas_sinteticas(_nivel_at(lv, h, date), _nivel_at(lv, a, date))
            for value, odd in (("Home", ch), ("Draw", cd), ("Away", ca)):
                sad.execute(
                    "INSERT INTO odds (fixture_id, league_id, bookmaker_id, bookmaker_name, bet_id, bet_name, value, odd) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (fid, liga, 0, "SYNTHETIC", 1, "Match Winner", value, odd),
                )
                filas += 1
    sad.commit()
    sad.close()
    print(f"Relleno sintético: {len(hechos)} fixtures · {filas} filas odds (bookmaker=SYNTHETIC) para {len(teams)} equipos")


def construir_constants_cuota(base_dir, sad_path=None):
    """Reconstruye constants_cuota entera desde sad.db. La llama también el
    pipeline en cada corrida: cuando solo la construía el backfill manual, la
    tabla se congelaba en su última corrida y los "últimos partidos" de la UI
    mostraban datos de meses atrás. `sad_path` permite un sad.db fuera de
    base_dir (el pipeline separa --sad de --out)."""
    if sad_path is None:
        sad = _connect(base_dir, "sad.db")
    else:
        sad = sqlite3.connect(f"file:{sad_path}?mode=ro", uri=True)
        sad.execute("PRAGMA temp_store=MEMORY")
        sad.execute("PRAGMA busy_timeout=30000")
    mw = _mw_odds(sad)  # incluye ya las sintéticas
    fixtures = _fixtures_2026(sad)
    sad.close()

    por_equipo = {}
    for fid, h, a, gh, ga, date in fixtures:
        if gh is None or ga is None:
            continue
        por_equipo.setdefault(h, []).append((fid, True, gh, ga, date))
        por_equipo.setdefault(a, []).append((fid, False, ga, gh, date))

    co = _connect(base_dir, "constants.db", rw=True)
    co.executescript(f"""
        DROP TABLE IF EXISTS constants_cuota;
        CREATE TABLE constants_cuota (
            id INTEGER PRIMARY KEY, team_id INTEGER NOT NULL, fixture_id INTEGER NOT NULL, date DATETIME NOT NULL,
            cuota_victoria REAL, cuota_empate REAL, cuota_derrota REAL, resultado INTEGER, es_local INTEGER,
            {", ".join(f"{c} REAL" for c in CUOTA_K_COLS)});
        CREATE INDEX ix_cuota_team_date ON constants_cuota(team_id, date);
    """)
    cols = ["team_id", "fixture_id", "date", "cuota_victoria", "cuota_empate", "cuota_derrota", "resultado", "es_local", *CUOTA_K_COLS]
    ins = f"INSERT INTO constants_cuota ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})"
    total = con_cuota = 0
    for tid, partidos in por_equipo.items():
        st = dict(CUOTA0)
        filas = []
        for fid, is_local, gf, ga, date in sorted(partidos, key=lambda x: x[4]):
            r = 1 if gf > ga else 0 if gf == ga else -1
            o = mw.get(fid)
            if o:
                h, d, a = o
                cv, ce, cd = (h, d, a) if is_local else (a, d, h)  # cuota_derrota = victoria del rival
                con_cuota += 1
            else:
                cv = ce = cd = None
            st = step_cuota(st, r, is_local, cv, ce, cd)
            filas.append((tid, fid, date, cv, ce, cd, r, 1 if is_local else 0, *(st[c] for c in CUOTA_K_COLS)))
        co.executemany(ins, filas)
        total += len(filas)
    co.commit()
    co.close()
    print(f"constants_cuota: {total} filas · {len(por_equipo)} equipos · {con_cuota} partidos con cuota")


def main(argv):
    base = BASE_DIR
    synth = True
    teams = SYNTH_TEAMS
    ids = []
    for a in argv:
        if a == "--no-synth":
            synth = False
        elif a.isdigit():
            ids.append(int(a))
        else:
            base = a
    if ids:
        teams = ids
    if synth:
        rellenar_sinteticas(base, teams)
    construir_constants_cuota(base)


if __name__ == "__main__":
    main(sys.argv[1:])
