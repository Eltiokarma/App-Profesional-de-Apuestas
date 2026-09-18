"""Adelgazar sad.db: borrar lo que ninguna pantalla lee y compactar el archivo.

El 18/09/2026 sad.db pesaba 30 GB: odds_history 190 M filas, odds_live 62 M,
odds 27 M, y todo lo demás menos de 1 GB. Guardábamos decenas de mercados por
partido (córners, tarjetas, medios tiempos, todas las líneas de goles…) y las
pantallas solo leen cinco (`backend/cuota_mercados.py`). Railway cobra como
memoria la caché de archivos: cada lectura de esa base costaba 20 GB de RAM
por hora. La ingesta ya no guarda esos mercados; esto limpia lo acumulado.

    python -m backend.ingesta.adelgazar                 # solo mide: cuánto se iría
    python -m backend.ingesta.adelgazar --aplicar       # borra + retención + VACUUM
    python -m backend.ingesta.adelgazar --aplicar --sin-vacuum

Se corre desde la raíz del repo (donde está el paquete `backend`); en Railway
eso es /app, y la base la toma de $SAD_DATA_DIR (o se pasa con --db).

Corre con cwd en el directorio de las DBs (en Railway: `cd /data` primero, o
--db /data/sad.db). Borra por lotes de rowid con commit por lote, así el ciclo
en vivo (busy_timeout 30 s) se cuela entre lotes. El VACUUM final necesita
disco libre por el tamaño final de la base y bloquea escrituras mientras dura
(minutos): los ciclos en vivo de ese rato fallan y el siguiente sigue solo.
"""
import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone

from backend.cuota_mercados import es_del_contrato

TABLAS = ("odds_history", "odds_live", "odds")
LOTE = 500_000  # rowids por transacción


def _pares_a_conservar(con: sqlite3.Connection, tabla: str) -> tuple[list, int]:
    """(bet_name, value) que el contrato lee, entre los que hay en la tabla."""
    pares = con.execute(f"SELECT bet_name, value, COUNT(*) FROM {tabla} GROUP BY bet_name, value").fetchall()
    conservar = [(b, v) for b, v, _ in pares if es_del_contrato(b, v)]
    fuera = sum(n for b, v, n in pares if not es_del_contrato(b, v))
    return conservar, fuera


def _cond_fuera(conservar: list) -> tuple[str, list]:
    if not conservar:
        return "1", []
    partes = " OR ".join("(bet_name IS ? AND value IS ?)" for _ in conservar)
    return f"NOT ({partes})", [x for par in conservar for x in par]


def _borrar_por_lotes(con: sqlite3.Connection, tabla: str, cond: str, params: list) -> int:
    lo, hi = con.execute(f"SELECT MIN(rowid), MAX(rowid) FROM {tabla}").fetchone()
    if lo is None:
        return 0
    total, t0 = 0, time.time()
    a = lo
    while a <= hi:
        b = a + LOTE - 1
        cur = con.execute(f"DELETE FROM {tabla} WHERE rowid BETWEEN ? AND ? AND {cond}", [a, b, *params])
        con.commit()
        total += cur.rowcount
        if (a - lo) // LOTE % 20 == 0:
            con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            print(f"  {tabla}: rowid {a}/{hi} · borradas {total} · {int(time.time() - t0)} s", flush=True)
        a = b + 1
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description="Adelgazar sad.db: mercados fuera del contrato, retención y VACUUM")
    ap.add_argument("--db", default=os.path.join(os.environ.get("SAD_DATA_DIR", "."), "sad.db"),
                    help="ruta de sad.db (por defecto $SAD_DATA_DIR/sad.db, o ./sad.db)")
    ap.add_argument("--aplicar", action="store_true", help="sin esto solo mide")
    ap.add_argument("--sin-vacuum", action="store_true")
    ap.add_argument("--historial-dias", type=int, default=int(os.environ.get("SAD_ODDS_HISTORY_DIAS", "90") or "0"),
                    help="retención de odds_history/odds por fecha del partido (0 = no aplicar)")
    ap.add_argument("--live-dias", type=int, default=30, help="retención de odds_live por fecha del partido")
    a = ap.parse_args()
    if not os.path.exists(a.db):
        print(f"No existe {a.db}", file=sys.stderr)
        return 1
    tam0 = os.path.getsize(a.db) / 2**30
    con = sqlite3.connect(a.db)
    con.execute("PRAGMA busy_timeout=60000")
    con.execute("PRAGMA journal_mode=WAL")
    print(f"{a.db}: {tam0:.2f} GB · {'APLICANDO' if a.aplicar else 'solo medición (pasá --aplicar para borrar)'}")

    ahora = datetime.now(timezone.utc)
    for tabla in TABLAS:
        try:
            n = con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        except sqlite3.OperationalError:
            continue
        conservar, fuera = _pares_a_conservar(con, tabla)
        print(f"{tabla}: {n:,} filas · fuera del contrato: {fuera:,} ({100 * fuera / n if n else 0:.0f} %) · "
              f"mercados que quedan: {len(conservar)}")
        if a.aplicar and fuera:
            cond, params = _cond_fuera(conservar)
            print(f"  borrando en lotes de {LOTE:,} rowids…", flush=True)
            b = _borrar_por_lotes(con, tabla, cond, params)
            print(f"  {tabla}: {b:,} filas borradas")
        dias = a.live_dias if tabla == "odds_live" else a.historial_dias
        if dias > 0:
            corte = (ahora - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
            estados = "" if tabla == "odds_live" else " AND status_short IN ('FT','AET','PEN','AWD','WO','CANC','ABD')"
            sub = f"(SELECT id FROM fixtures WHERE date < ?{estados})"
            viejas = con.execute(f"SELECT COUNT(*) FROM {tabla} WHERE fixture_id IN {sub}", (corte,)).fetchone()[0]
            print(f"  retención {dias} d: {viejas:,} filas de partidos anteriores a {corte[:10]}")
            if a.aplicar and viejas:
                cur = con.execute(f"DELETE FROM {tabla} WHERE fixture_id IN {sub}", (corte,))
                con.commit()
                con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                print(f"  {tabla}: {cur.rowcount:,} filas borradas por retención")

    if a.aplicar and not a.sin_vacuum:
        print("VACUUM… (bloquea escrituras mientras dura; los ciclos en vivo de este rato fallan y el siguiente sigue)", flush=True)
        t0 = time.time()
        con.execute("VACUUM")
        print(f"VACUUM listo en {int(time.time() - t0)} s")
    con.close()
    tam1 = os.path.getsize(a.db) / 2**30
    print(f"{a.db}: {tam0:.2f} GB → {tam1:.2f} GB"
          + ("" if a.aplicar else " (sin cambios: medición)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
