"""Crea los índices que el backend necesita sobre las .db del pipeline.

El pipeline genera sad.db y levels.db SIN índices: cada request de /fixtures,
/cuotas o /stats escanea tablas completas (sad.db ~900 MB). Este script los
crea una vez; es idempotente (IF NOT EXISTS) y hay que re-correrlo cada vez
que el pipeline regenere las bases, igual que los backfills.

    python -m backend.crear_indices              # usa SAD_DATA_DIR o la raíz del repo
    python -m backend.crear_indices ./demo_data
"""
import os
import sqlite3
import sys
import time

from backend.db import BASE_DIR

INDICES = {
    "sad.db": [
        ("idx_fixtures_date", "fixtures(date)"),
        ("idx_fixtures_home_date", "fixtures(home_team_id, date)"),
        ("idx_fixtures_away_date", "fixtures(away_team_id, date)"),
        ("idx_fixtures_league_season", "fixtures(league_id, league_season)"),
        ("idx_odds_fixture", "odds(fixture_id)"),
    ],
    "levels.db": [
        ("idx_team_levels_team_date", "team_levels(team_id, date)"),
    ],
    "discreto.db": [
        ("idx_processed_at", "processed_matches(processed_at)"),
    ],
}


def crear(base_dir):
    for db_file, indices in INDICES.items():
        path = os.path.join(base_dir, db_file)
        if not os.path.exists(path):
            print(f"— {db_file}: no existe, se omite")
            continue
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA temp_store=MEMORY")  # el temp en C: suele estar lleno
        print(f"== {db_file}")
        for nombre, definicion in indices:
            t0 = time.time()
            try:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {nombre} ON {definicion}")
                conn.commit()
                print(f"   {nombre} → OK ({time.time() - t0:.1f}s)")
            except sqlite3.OperationalError as e:
                print(f"   {nombre} → omitido ({e})")
        t0 = time.time()
        conn.execute("ANALYZE")
        conn.commit()
        print(f"   ANALYZE → OK ({time.time() - t0:.1f}s)")
        conn.close()
    print("LISTO")


if __name__ == "__main__":
    crear(sys.argv[1] if len(sys.argv) > 1 else BASE_DIR)
