"""Rellena las columnas de Doble Oportunidad (k_dc, §3.6) en una constants.db
ya generada por el pipeline — puente LOCAL hasta que el pipeline las emita.

No re-corre la extracción: recorre el historial de cada equipo en orden
cronológico y aplica la fórmula del motor (idéntica a src/motor y seed_demo),
reusando el MISMO nivel de rival que el pipeline ya horneó en cada fila. Ese
nivel se **recupera exacto** de las q existentes (q_goles_anotado = goles ·
nivel_rival), de modo que k_dc queda consistente con las k que ya están en la
fila. Para empates 0-0 (sin q de la que recuperar) cae al nivel continuo de
levels.db, y se reporta cuántas filas usaron ese respaldo.

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

NEW_COLS = ("q_dc", "k_dc", "k_dc_local", "k_dc_visita")


def kdc_step(prev_dc, prev_dc_local, prev_dc_visita, is_local, gf, ga, nivel):
    """Un partido de avance de k_dc (§3.6). Empate aporta 0.5·nivel; la derrota
    resetea; sin multiplicador visitante. dc_local/dc_visita solo cambian en su
    condición (si no, conservan el valor anterior)."""
    dif = abs(gf - ga)
    perdio = gf < ga
    q_dc = 0.0 if perdio else max(dif * nivel, 0.5 * nivel)
    dc = 0.0 if perdio else prev_dc + q_dc
    dc_local = prev_dc_local
    dc_visita = prev_dc_visita
    if is_local:
        dc_local = 0.0 if perdio else prev_dc_local + q_dc
    else:
        dc_visita = 0.0 if perdio else prev_dc_visita + q_dc
    return q_dc, dc, dc_local, dc_visita


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

    # fixtures: goles y local/visita, en memoria
    fixtures = {
        r[0]: (r[1], r[2], r[3], r[4])
        for r in sad.execute("SELECT id, home_team_id, away_team_id, goals_home, goals_away FROM fixtures")
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
    max_dc = 0.0
    for tid in teams:
        rows = co.execute(
            "SELECT id, fixture_id, date, q_goles_anotado, q_goles_recibido FROM constants WHERE team_id=? ORDER BY date, id",
            (tid,),
        ).fetchall()
        dc = dc_local = dc_visita = 0.0
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
            q_dc, dc, dc_local, dc_visita = kdc_step(dc, dc_local, dc_visita, is_local, gf, ga, nivel)
            updates.append((q_dc, dc, dc_local, dc_visita, row_id))
            max_dc = max(max_dc, dc)
        co.executemany(
            "UPDATE constants SET q_dc=?, k_dc=?, k_dc_local=?, k_dc_visita=? WHERE id=?", updates
        )
        total_rows += len(updates)
    co.commit()
    co.close()
    sad.close()
    lv.close()
    print(
        f"k_dc rellenado: {total_rows} filas · {len(teams)} equipos · "
        f"max k_dc={max_dc:.2f} · respaldo levels.db en 0-0={fallback_0_0}"
    )


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else BASE_DIR
    backfill(base)
