"""Rellena las columnas de las familias K derivadas (Doble Oportunidad §3.6 y
Márgenes §3.7) en una constants.db ya generada por el pipeline — puente LOCAL
hasta que el pipeline las emita.

No re-corre la extracción: recorre el historial de cada equipo en orden
cronológico y aplica la fórmula del motor (backend/familias_k.py, espejo de
src/motor), reusando el MISMO nivel de rival que el pipeline ya horneó en cada
fila. Ese nivel se **recupera exacto** de las q existentes (q_goles_anotado =
goles · nivel_rival), de modo que las familias quedan consistentes con las k que
ya están en la fila. Para empates 0-0 (sin q de la que recuperar) cae al nivel
continuo de levels.db, y se reporta cuántas filas usaron ese respaldo.

Idempotente: recalcula desde cero en cada corrida. Antes de escribir hace una
copia de seguridad pristina (constants.db.bak, solo la primera vez). Solo
modifica constants.db; sad.db y levels.db se abren en solo-lectura.

    python -m backend.backfill_kdc            # usa SAD_DATA_DIR o la raíz del repo
    python -m backend.backfill_kdc ./demo_data
"""
import os
import shutil
import sqlite3
import sys
from bisect import bisect_right

from backend.db import BASE_DIR
from backend.familias_k import FAMILIAS0, FAMILIAS_COLS, step_familias

NEW_COLS = ("q_dc", *FAMILIAS_COLS)  # todas las columnas que rellena el puente


def backfill(base_dir):
    const_path = os.path.join(base_dir, "constants.db")
    if not os.path.exists(const_path):
        raise FileNotFoundError(f"No existe {const_path}")

    bak = const_path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(const_path, bak)
        print(f"Copia de seguridad → {bak}")
    else:
        print(f"Copia de seguridad ya existe (se conserva) → {bak}")

    co = sqlite3.connect(const_path)  # lectura-escritura
    co.execute("PRAGMA busy_timeout=30000")
    sad = sqlite3.connect(f"file:{os.path.join(base_dir, 'sad.db')}?mode=ro", uri=True)
    lv = sqlite3.connect(f"file:{os.path.join(base_dir, 'levels.db')}?mode=ro", uri=True)

    # columnas nuevas (idempotente)
    existing = {r[1] for r in co.execute("PRAGMA table_info(constants)")}
    for c in NEW_COLS:
        if c not in existing:
            co.execute(f"ALTER TABLE constants ADD COLUMN {c} REAL")
    co.commit()
    set_clause = ", ".join(f"{c}=?" for c in NEW_COLS)

    # fixtures: goles y local/visita, en memoria
    fixtures = {
        r[0]: (r[1], r[2], r[3], r[4])
        # regla de 90': fulltime_* manda (goals_* incluye la prórroga en AET/PEN)
        for r in sad.execute("SELECT id, home_team_id, away_team_id, "
                             "COALESCE(fulltime_home, goals_home), COALESCE(fulltime_away, goals_away) FROM fixtures")
    }
    # levels por equipo para el respaldo de los 0-0 (bisect por fecha)
    lv_by_team = {}
    for tid, date, level in lv.execute("SELECT team_id, date, level FROM team_levels ORDER BY team_id, date"):
        d, l = lv_by_team.setdefault(tid, ([], []))
        d.append(date)
        l.append(level)

    def nivel_levels(tid, date):
        d, l = lv_by_team.get(tid, ([], []))
        i = bisect_right(d, date) - 1
        return l[i] if i >= 0 else 1.0

    teams = [r[0] for r in co.execute("SELECT DISTINCT team_id FROM constants")]
    total_rows = fallback_0_0 = 0
    max_dc = max_der = 0.0
    for tid in teams:
        rows = co.execute(
            "SELECT id, fixture_id, date, q_goles_anotado, q_goles_recibido FROM constants WHERE team_id=? ORDER BY date, id",
            (tid,),
        ).fetchall()
        st = dict(FAMILIAS0)
        updates = []
        for row_id, fx, date, qga, qgr in rows:
            f = fixtures.get(fx)
            if not f or f[2] is None or f[3] is None:  # sin fixture o sin marcador → no se toca
                continue
            home, away, gh, ga_ = f
            is_local = home == tid
            gf, ga = (gh, ga_) if is_local else (ga_, gh)
            rival = away if is_local else home
            # nivel del rival: EXACTO recuperado de las q; respaldo levels.db en 0-0
            if gf and qga is not None:
                nivel = abs(qga) / gf
            elif ga and qgr is not None:
                nivel = abs(qgr) / ga
            else:
                nivel = nivel_levels(rival, date)
                fallback_0_0 += 1
            q_dc, st = step_familias(st, is_local, gf, ga, nivel)
            updates.append((q_dc, *(st[c] for c in FAMILIAS_COLS), row_id))
            max_dc = max(max_dc, st["k_dc"])
            max_der = max(max_der, st["k_der1"], st["k_der2"], st["k_der3"])
        co.executemany(f"UPDATE constants SET {set_clause} WHERE id=?", updates)
        total_rows += len(updates)
    co.commit()
    co.close()
    sad.close()
    lv.close()
    print(
        f"Familias K rellenadas: {total_rows} filas · {len(teams)} equipos · "
        f"max k_dc={max_dc:.2f} · max k_derrota={max_der:.2f} · respaldo levels.db en 0-0={fallback_0_0}"
    )


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else BASE_DIR
    backfill(base)
