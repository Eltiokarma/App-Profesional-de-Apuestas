"""Ciclo de ingesta EN VIVO (fase 3 de docs/EXTRACCION_TIEMPO_REAL.md).

Un ciclo por invocación, pensado para el hilo SAD_LIVE_SEGUNDOS de backend.app:
1. Mira en sad.db si hay fixtures nuestros en ventana de juego (arrancaron hace
   <= 2h30 o siguen marcados en juego). Sin candidatos: sale con 0 requests.
2. /fixtures?live=<ids de las ligas importantes> — marcador, minuto y estado
   reales (1 request); las ligas menores (Liga 2, copas nacionales) no entran;
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
    guardar_fixtures,
    leer_clave,
    ligas_vivo,
)

VENTANA_JUEGO_MIN = 210  # arrancó hace <= 3h30: cubre alargue, penales y pausas largas
RETENCION_DIAS = 30  # la curva en vivo de un partido terminado es material de estudio
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

CREATE TABLE IF NOT EXISTS fixture_eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL,
    minuto INTEGER,
    tipo TEXT,
    detalle TEXT,
    equipo_id INTEGER,
    jugador TEXT
);
CREATE INDEX IF NOT EXISTS idx_eventos_fixture ON fixture_eventos(fixture_id);
"""


def fixtures_en_ventana(con: sqlite3.Connection, ligas: "set[int]") -> list[int]:
    """Nuestros fixtures que pueden estar en juego ahora: arrancaron hace poco
    (NS aún no actualizado) o ya están marcados con un estado en juego. Se
    limita a `ligas` (las importantes): las menores no entran al ciclo en vivo."""
    if not ligas:
        return []
    ahora = datetime.now(timezone.utc)
    desde = (ahora - timedelta(minutes=VENTANA_JUEGO_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    hasta = ahora.strftime("%Y-%m-%d %H:%M:%S")
    marcas = ",".join("?" * len(EN_JUEGO))
    ligas_marcas = ",".join("?" * len(ligas))
    return [
        fila[0]
        for fila in con.execute(
            f"""SELECT id FROM fixtures
                WHERE league_id IN ({ligas_marcas})
                  AND ((status_short = 'NS' AND date BETWEEN ? AND ?)
                       OR status_short IN ({marcas}))
                ORDER BY date""",
            (*sorted(ligas), desde, hasta, *EN_JUEGO),
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


def guardar_eventos(con: sqlite3.Connection, item: dict) -> int:
    """Eventos del partido (goles, tarjetas…) que traen /fixtures?live= y
    /fixtures?ids=. El feed devuelve la lista completa en cada ciclo, así que
    se reemplaza entera (idempotente)."""
    fid = item.get("fixture", {}).get("id")
    eventos = item.get("events") or []
    if not fid or not eventos:
        return 0
    con.execute("DELETE FROM fixture_eventos WHERE fixture_id=?", (fid,))
    n = 0
    for ev in eventos:
        t = ev.get("time") or {}
        minuto = (t.get("elapsed") or 0) + (t.get("extra") or 0)
        con.execute(
            "INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (fid, minuto, ev.get("type"), ev.get("detail"),
             (ev.get("team") or {}).get("id"), (ev.get("player") or {}).get("name")),
        )
        n += 1
    return n


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
            # el catálogo live manda la línea aparte: "Over" + handicap "2.5" →
            # se guarda "Over 2.5" (mismo formato que prepartido → cuota_key mapea)
            valor_txt = str(valor.get("value"))
            handicap = valor.get("handicap")
            if handicap not in (None, "") and str(handicap) not in valor_txt:
                valor_txt = f"{valor_txt} {handicap}"
            con.execute(
                "INSERT INTO odds_live (fixture_id, minuto, bet_id, bet_name, value, "
                "odd, suspendida, captured_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (fid, minuto, bet.get("id"), bet.get("name"), valor_txt,
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

    # solo las ligas importantes reciben el ciclo en vivo (las menores —Liga 2,
    # copas nacionales— se ingestan igual en fixtures/histórico/cuotas prepartido)
    vivo = ligas_vivo()
    candidatos = set(fixtures_en_ventana(con, vivo))
    if not candidatos:
        con.close()
        print("sin partidos en ventana de juego · 0 requests")
        return 0

    cliente = Cliente(leer_clave())
    capturado = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

    # 1 request: marcador/minuto/estado de todo lo vivo en nuestras ligas importantes
    ids_ligas = "-".join(str(i) for i in sorted(vivo))
    data = cliente.get("fixtures", {"live": ids_ligas})
    vivos = [
        item for item in (data or {}).get("response", [])
        if item.get("fixture", {}).get("id") in candidatos
        or item.get("league", {}).get("id") in vivo
    ]
    n_fix = guardar_fixtures(con, vivos)
    n_ev = sum(guardar_eventos(con, item) for item in vivos)
    con.commit()
    ids_vivos = {item["fixture"]["id"] for item in vivos if item.get("fixture", {}).get("id")}
    print(f"en juego: {len(ids_vivos)} fixtures nuestros (candidatos locales: {len(candidatos)})")

    # 1 request: cuotas en juego de toda la API, filtradas a lo nuestro
    n_odds = 0
    if ids_vivos and cliente.quedan():
        data = cliente.get("odds/live", {})
        con_feed: set[int] = set()
        for item in (data or {}).get("response", []):
            fid = item.get("fixture", {}).get("id")
            if fid in ids_vivos:
                n_odds += guardar_odds_live(con, item, capturado)
                con_feed.add(fid)
        con.commit()
        # evidencia en logs: distinguir "no pedimos" de "la casa cerró el mercado"
        susp = con.execute(
            "SELECT COUNT(*) FROM odds_live WHERE captured_at=? AND suspendida=1", (capturado,)
        ).fetchone()[0]
        print(f"odds live: {n_odds} valores ({susp} suspendidos) en {len(con_feed)} fixtures")
        sin_feed = ids_vivos - con_feed
        if sin_feed:
            print(f"sin odds en el feed live (cobertura o mercado cerrado por la casa): {sorted(sin_feed)}")

    # cerrar los que se cayeron del feed live (terminaron): /fixtures?ids= trae
    # su estado y marcador finales sin esperar a la corrida diaria (lotes de 20)
    terminados = sorted(fixtures_marcados_en_juego(con) - ids_vivos)
    n_fin = 0
    for i in range(0, len(terminados), 20):
        if not cliente.quedan():
            break
        data = cliente.get("fixtures", {"ids": "-".join(map(str, terminados[i:i + 20]))})
        cerrados = (data or {}).get("response", [])
        n_fin += guardar_fixtures(con, cerrados)
        n_ev += sum(guardar_eventos(con, item) for item in cerrados)  # eventos finales del partido
        con.commit()
    if terminados:
        print(f"cerrados (salieron del feed live): {n_fin} de {len(terminados)}")

    corte = (datetime.now(timezone.utc) - timedelta(days=RETENCION_DIAS)).strftime("%Y-%m-%d %H:%M:%S")
    borradas = con.execute("DELETE FROM odds_live WHERE captured_at < ?", (corte,)).rowcount
    con.commit()
    con.close()
    print(f"fixtures actualizados: {n_fix} · cuotas live: {n_odds} · eventos: {n_ev} "
          f"· purgadas: {borradas} · requests usadas: {cliente.usadas}/{cliente.limite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
