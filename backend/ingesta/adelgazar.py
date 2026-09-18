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

En Railway NO se corre desde la consola web: la sesión se cierra sola a los
minutos y se lleva el proceso (pasó el 18/09 durante el primer conteo). Se pone
`SAD_ADELGAZAR=1` en las variables, el backend lo lanza en un subproceso al
arrancar (`backend/app.py`), la salida va a los Deploy Logs y al terminar deja
`.adelgazar_hecho.json` junto a la base para no repetirse; después se quita la
variable. Con --aplicar NO hay pasada de conteo previa (sobre 190 M filas era
un recorrido entero de la base solo para informar): borra directo por lotes
de rowid, con commit por lote, así el ciclo en vivo se cuela entre lotes. El
VACUUM final escribe su copia temporal JUNTO a la base (SQLITE_TMPDIR), no en
el disco efímero del contenedor, que es más chico. El VACUUM necesita
disco libre por el tamaño final de la base y bloquea escrituras mientras dura
(minutos): los ciclos en vivo de ese rato fallan y el siguiente sigue solo.
"""
import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone

from backend.cuota_mercados import es_del_contrato

TABLAS = ("odds_history", "odds_live", "odds")
LOTE = 500_000  # rowids por transacción
MARCA = ".adelgazar_hecho.json"  # junto a la base: cuándo se aplicó y qué borró


def _fuera_del_contrato(bet_name, value) -> int:
    """Función SQL registrada: 1 si la fila no la lee ninguna pantalla."""
    return 0 if es_del_contrato(bet_name, value) else 1


def _pares_a_conservar(con: sqlite3.Connection, tabla: str) -> tuple[list, int]:
    """(bet_name, value) que el contrato lee, entre los que hay en la tabla."""
    pares = con.execute(f"SELECT bet_name, value, COUNT(*) FROM {tabla} GROUP BY bet_name, value").fetchall()
    conservar = [(b, v) for b, v, _ in pares if es_del_contrato(b, v)]
    fuera = sum(n for b, v, n in pares if not es_del_contrato(b, v))
    return conservar, fuera


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
    carpeta = os.path.dirname(os.path.abspath(a.db))
    # el temporal del VACUUM (del tamaño de la base final) va junto a la base,
    # no al /tmp del contenedor
    os.environ.setdefault("SQLITE_TMPDIR", carpeta)
    con = sqlite3.connect(a.db)
    con.execute("PRAGMA busy_timeout=60000")
    con.execute("PRAGMA journal_mode=WAL")
    con.create_function("sad_fuera", 2, _fuera_del_contrato, deterministic=True)
    print(f"{a.db}: {tam0:.2f} GB · {'APLICANDO' if a.aplicar else 'solo medición (pasá --aplicar para borrar)'}",
          flush=True)

    ahora = datetime.now(timezone.utc)
    borradas: dict[str, int] = {}
    for tabla in TABLAS:
        try:
            n = con.execute(f"SELECT MAX(rowid) FROM {tabla}").fetchone()[0] or 0
        except sqlite3.OperationalError:
            continue
        if a.aplicar:
            # sin conteo previo: sobre 190 M filas era un recorrido entero de la
            # base solo para informar, y el borrado ya recorre lo mismo
            print(f"{tabla}: hasta rowid {n:,} · borrando lo fuera del contrato en lotes de {LOTE:,}…", flush=True)
            b = _borrar_por_lotes(con, tabla, "sad_fuera(bet_name, value)", [])
            borradas[tabla] = b
            print(f"  {tabla}: {b:,} filas borradas", flush=True)
        else:
            n = con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            conservar, fuera = _pares_a_conservar(con, tabla)
            print(f"{tabla}: {n:,} filas · fuera del contrato: {fuera:,} ({100 * fuera / n if n else 0:.0f} %) · "
                  f"mercados que quedan: {len(conservar)}", flush=True)
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
                borradas[tabla] = borradas.get(tabla, 0) + cur.rowcount
                print(f"  {tabla}: {cur.rowcount:,} filas borradas por retención", flush=True)

    if a.aplicar and not a.sin_vacuum:
        print("VACUUM… (bloquea escrituras mientras dura; los ciclos en vivo de este rato fallan y el siguiente sigue)", flush=True)
        t0 = time.time()
        con.execute("VACUUM")
        print(f"VACUUM listo en {int(time.time() - t0)} s")
    con.close()
    tam1 = os.path.getsize(a.db) / 2**30
    print(f"{a.db}: {tam0:.2f} GB → {tam1:.2f} GB"
          + ("" if a.aplicar else " (sin cambios: medición)"), flush=True)
    if a.aplicar:
        with open(os.path.join(carpeta, MARCA), "w", encoding="utf-8") as f:
            json.dump({"aplicado_en": ahora.isoformat(), "gb_antes": round(tam0, 2), "gb_despues": round(tam1, 2),
                       "borradas": borradas, "vacuum": not a.sin_vacuum}, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
