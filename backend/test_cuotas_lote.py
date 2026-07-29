"""Test de la estrategia de cuotas prepartido (capturar_cuotas_lote) — sin red.

Blinda la cuenta que agotó el plan el 29/07/2026: /odds?date= trae el día
entero DEL MUNDO (40-90 páginas un día cargado), y el refresco de cada 30 min
lo pagaba completo para re-capturar un puñado de partidos nuestros — ~2.000-
4.300 requests/día él solo. La regla: pocos pendientes → /odds?fixture= (1
request exacta por partido); muchos → el lote por fecha de siempre.

    python -m backend.test_cuotas_lote
"""
import sqlite3
import sys

from backend.ingesta import extractor as ex
from backend.ingesta.extractor import capturar_cuotas_lote

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


DDL = """
CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT, league_id INTEGER);
CREATE TABLE odds (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER, league_id INTEGER,
    bookmaker_id INTEGER, bookmaker_name TEXT, bet_id INTEGER, bet_name TEXT, value TEXT, odd REAL);
CREATE TABLE odds_history (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL,
    league_id INTEGER, bet_id INTEGER, bet_name TEXT, value TEXT, odd REAL, casas INTEGER,
    captured_at TEXT NOT NULL, casa_id INTEGER, casa TEXT);
"""


def item_odds(fid: int) -> dict:
    return {
        "fixture": {"id": fid},
        "league": {"id": 128},
        "bookmakers": [{"id": 8, "name": "Bet365", "bets": [
            {"id": 1, "name": "Match Winner", "values": [
                {"value": "Home", "odd": "1.80"},
                {"value": "Draw", "odd": "3.40"},
                {"value": "Away", "odd": "4.20"},
            ]}]}],
    }


class ClienteFalso:
    """Emula /odds: por fixture responde SOLO ese partido (1 página); por fecha
    responde el día del MUNDO — nuestros partidos + `mundo` ajenos, paginado."""

    PAGINA = 10

    def __init__(self, nuestros: list[int], mundo: int):
        self.items = [item_odds(f) for f in nuestros] + [item_odds(10_000 + i) for i in range(mundo)]
        self.usadas = 0
        self.limite = 10**6
        self.usadas_por: dict[str, int] = {}
        self.pedidos: list = []

    def quedan(self, n: int = 1) -> bool:
        return True

    def get(self, endpoint: str, params: dict):
        self.usadas += 1
        self.pedidos.append((endpoint, params.get("fixture"), params.get("date"), params.get("page", 1)))
        if params.get("fixture") is not None:
            items = [it for it in self.items if it["fixture"]["id"] == params["fixture"]]
        else:
            items = self.items
        pagina = int(params.get("page", 1))
        total = max(1, -(-len(items) // self.PAGINA))
        return {"response": items[(pagina - 1) * self.PAGINA: pagina * self.PAGINA],
                "paging": {"current": pagina, "total": total}}

    def paginado(self, endpoint: str, params: dict, tope_paginas: int = 0) -> list:
        data = self.get(endpoint, params)
        filas = list(data["response"])
        for pagina in range(2, data["paging"]["total"] + 1):
            filas.extend(self.get(endpoint, {**params, "page": pagina})["response"])
        return filas


def db(fixtures: list[tuple]) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.executescript(DDL)
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?,?,?,128)", fixtures)
    con.commit()
    return con


def main():
    # EL CASO DEL REFRESCO: 4 pendientes de hoy, 300 partidos ajenos en el
    # feed mundial (30 páginas). En lote costaba 30 requests; por fixture, 4.
    nuestros = [900001, 900002, 900003, 900004]
    con = db([(f, "2026-07-30 20:00:00", "NS") for f in nuestros])
    cliente = ClienteFalso(nuestros, mundo=300)
    total, cubiertos = capturar_cuotas_lote(cliente, con, nuestros)
    check("pocos pendientes → una request exacta por fixture (4, no 31 páginas del mundo)",
          cliente.usadas == 4 and all(p[1] is not None for p in cliente.pedidos),
          (cliente.usadas, cliente.pedidos[:6]))
    check("y las cuotas de los 4 quedan guardadas",
          cubiertos == 4 and con.execute("SELECT COUNT(DISTINCT fixture_id) FROM odds").fetchone()[0] == 4,
          (total, cubiertos))

    # EL CASO MUNDIAL: 60 pendientes el mismo día → el lote amortiza (7 páginas
    # de 100 items contra 60 requests por fixture)
    muchos = list(range(900100, 900160))
    con = db([(f, "2026-07-30 20:00:00", "NS") for f in muchos])
    cliente = ClienteFalso(muchos, mundo=40)
    total, cubiertos = capturar_cuotas_lote(cliente, con, muchos)
    check("muchos pendientes → lote por fecha (páginas del día, no 60 requests)",
          cliente.usadas == 10 and all(p[2] == "2026-07-30" for p in cliente.pedidos),
          (cliente.usadas, cliente.pedidos[:3]))
    check("el lote cubre los 60", cubiertos == 60, cubiertos)

    # cada fecha decide su propia vía: 3 pendientes hoy + 40 mañana
    hoy3 = [900201, 900202, 900203]
    man40 = list(range(900300, 900340))
    con = db([(f, "2026-07-30 20:00:00", "NS") for f in hoy3]
             + [(f, "2026-07-31 20:00:00", "NS") for f in man40])
    cliente = ClienteFalso(hoy3 + man40, mundo=50)
    capturar_cuotas_lote(cliente, con, hoy3 + man40)
    por_fixture = [p for p in cliente.pedidos if p[1] is not None]
    por_fecha = {p[2] for p in cliente.pedidos if p[2]}
    check("la vía se decide POR FECHA: hoy por fixture, mañana en lote",
          len(por_fixture) == 3 and por_fecha == {"2026-07-31"},
          (por_fixture, por_fecha))

    # el umbral es configurable y 0 lo apaga (siempre lote, como antes)
    umbral = ex.UMBRAL_LOTE
    ex.UMBRAL_LOTE = 0
    try:
        con = db([(f, "2026-07-30 20:00:00", "NS") for f in nuestros])
        cliente = ClienteFalso(nuestros, mundo=20)
        capturar_cuotas_lote(cliente, con, nuestros)
        check("con umbral 0 todo va en lote (comportamiento anterior)",
              all(p[1] is None for p in cliente.pedidos), cliente.pedidos[:3])
    finally:
        ex.UMBRAL_LOTE = umbral

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
