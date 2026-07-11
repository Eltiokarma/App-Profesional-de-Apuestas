"""Ciclo de ingesta EN VIVO (fase 3 de docs/EXTRACCION_TIEMPO_REAL.md).

Un ciclo por invocación, pensado para el hilo SAD_LIVE_SEGUNDOS de backend.app:
1. Mira en sad.db si hay fixtures nuestros en ventana de juego (arrancaron hace
   <= 2h30 o siguen marcados en juego). Sin candidatos: sale con 0 requests.
2. /fixtures?live=<ids de LIGAS> — marcador, minuto y estado reales (1 request);
   se guardan con guardar_fixtures (INSERT OR REPLACE).
3. /odds/live — cuotas en juego de la API (1 request); se filtran a nuestros
   fixtures y se apendizan a odds_live con minuto y captured_at. La cobertura
   varía por liga: donde la API no ofrece odds live, queda solo marcador/minuto.
4. Retención: borra odds_live con más de 7 días.

Activa WAL en sad.db (persistente): con escrituras cada minuto conviviendo con
las lecturas del backend, el modo journal clásico daría "database is locked".

Uso manual: PYTHONUTF8=1 python -m backend.ingesta.en_vivo [--db sad.db]
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

from backend.ingesta.extractor import (
    Cliente,
    LIGAS,
    guardar_fixtures,
    leer_clave,
)

VENTANA_JUEGO_MIN = 150  # arrancó hace <= 2h30 → puede seguir en juego
RETENCION_DIAS = 7
EN_JUEGO = ("1H", "HT", "2H", "ET", "BT", "P", "LIVE", "INT", "SUSP")

DDL_ODDS_LIVE = """
CREATE TABLE IF NOT EXISTS odds_live (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL,
    minuto INTEGER,
    bet_id INTEGER,
    bet_name TEXT,
    value TEXT,
    odd REAL,
    suspendida INTEGER DEFAULT 0,
    captured_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_oddslive_fixture ON odds_live(fixture_id, captured_at);
"""


def fixtures_en_ventana(con: sqlite3.Connection) -> list[int]:
    """Nuestros fixtures que pueden estar en juego ahora: arrancaron hace poco
    (NS aún no actualizado) o ya están marcados con un estado en juego."""
    ahora = datetime.now(timezone.utc)
    desde = (ahora - timedelta(minutes=VENTANA_JUEGO_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    hasta = ahora.strftime("%Y-%m-%d %H:%M:%S")
    marcas = ",".join("?" * len(EN_JUEGO))
    return [
        fila[0]
        for fila in con.execute(
            f"""SELECT id FROM fixtures
                WHERE (status_short = 'NS' AND date BETWEEN ? AND ?)
                   OR status_short IN ({marcas})
                ORDER BY date""",
            (desde, hasta, *EN_JUEGO),
        )
    ]


def fixtures_marcados_en_juego(con: sqlite3.Connection) -> set[int]:
    """Los que sad.db cree que siguen en juego: si ya no aparecen en el feed
    live es que terminaron y hay que cerrarlos (estado + marcador final)."""
    marcas = ",".join("?" * len(EN_JUEGO))
    return {
        fila[0]
        for fila in con.execute(f"SELECT id FROM fixtures WHERE status_short IN ({marcas})", EN_JUEGO)
    }


def guardar_odds_live(con: sqlite3.Connection, item: dict, capturado: str) -> int:
    """Un item de /odds/live: {fixture:{id,status:{elapsed}}, odds:[{id,name,values:[…]}]}."""
    f = item.get("fixture", {})
    fid = f.get("id")
    if not fid:
        return 0
    minuto = (f.get("status") or {}).get("elapsed")
    n = 0
    for bet in item.get("odds", []):
        for valor in bet.get("values", []):
            try:
                odd = float(valor.get("odd"))
            except (TypeError, ValueError):
                continue
            con.execute(
                "INSERT INTO odds_live (fixture_id, minuto, bet_id, bet_name, value, "
                "odd, suspendida, captured_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (fid, minuto, bet.get("id"), bet.get("name"), str(valor.get("value")),
                 odd, 1 if valor.get("suspended") else 0, capturado),
            )
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Un ciclo de ingesta en vivo → sad.db")
    ap.add_argument("--db", default="sad.db", help="ruta a sad.db")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"No existe {args.db}", file=sys.stderr)
        return 1
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA busy_timeout=15000")
    con.execute("PRAGMA journal_mode=WAL")  # persistente; requisito de la fase 3
    con.executescript(DDL_ODDS_LIVE)

    candidatos = set(fixtures_en_ventana(con))
    if not candidatos:
        con.close()
        print("sin partidos en ventana de juego · 0 requests")
        return 0

    cliente = Cliente(leer_clave())
    capturado = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

    # 1 request: marcador/minuto/estado de todo lo vivo en nuestras ligas
    ids_ligas = "-".join(str(i) for i in sorted(LIGAS))
    data = cliente.get("fixtures", {"live": ids_ligas})
    vivos = [
        item for item in (data or {}).get("response", [])
        if item.get("fixture", {}).get("id") in candidatos
        or item.get("league", {}).get("id") in LIGAS
    ]
    n_fix = guardar_fixtures(con, vivos)
    ids_vivos = {item["fixture"]["id"] for item in vivos if item.get("fixture", {}).get("id")}
    print(f"en juego: {len(ids_vivos)} fixtures nuestros (candidatos locales: {len(candidatos)})")

    # 1 request: cuotas en juego de toda la API, filtradas a lo nuestro
    n_odds = 0
    if ids_vivos and cliente.quedan():
        data = cliente.get("odds/live", {})
        for item in (data or {}).get("response", []):
            if item.get("fixture", {}).get("id") in ids_vivos:
                n_odds += guardar_odds_live(con, item, capturado)
        con.commit()

    # cerrar los que se cayeron del feed live (terminaron): /fixtures?ids= trae
    # su estado y marcador finales sin esperar a la corrida diaria (lotes de 20)
    terminados = sorted(fixtures_marcados_en_juego(con) - ids_vivos)
    n_fin = 0
    for i in range(0, len(terminados), 20):
        if not cliente.quedan():
            break
        data = cliente.get("fixtures", {"ids": "-".join(map(str, terminados[i:i + 20]))})
        n_fin += guardar_fixtures(con, (data or {}).get("response", []))
    if terminados:
        print(f"cerrados (salieron del feed live): {n_fin} de {len(terminados)}")

    corte = (datetime.now(timezone.utc) - timedelta(days=RETENCION_DIAS)).strftime("%Y-%m-%d %H:%M:%S")
    borradas = con.execute("DELETE FROM odds_live WHERE captured_at < ?", (corte,)).rowcount
    con.commit()
    con.close()
    print(f"fixtures actualizados: {n_fix} · cuotas live: {n_odds} · purgadas: {borradas} "
          f"· requests usadas: {cliente.usadas}/{cliente.limite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
