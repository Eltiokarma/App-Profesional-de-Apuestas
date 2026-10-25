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
            ]},
            # lo que el feed trae de más y NINGUNA pantalla lee: no se guarda
            # (sad.db llegó a 30 GB guardándolo, docs/DESPLIEGUE.md)
            {"id": 45, "name": "Corners Over/Under", "values": [{"value": "Over 9.5", "odd": "1.85"}]},
            {"id": 5, "name": "Goals Over/Under", "values": [
                {"value": "Over 1.5", "odd": "1.30"}, {"value": "Over 2.5", "odd": "1.90"}, {"value": "Under 2.5", "odd": "1.95"},
            ]},
            {"id": 8, "name": "Goals Over/Under First Half", "values": [{"value": "Over 0.5", "odd": "1.40"}]},
            # el feed real trae valores NUMÉRICOS: tumbaron el extractor del
            # 18/09 al 11/10/2026 (AttributeError: 'int' object has no attribute 'strip')
            {"id": 38, "name": "Exact Goals Number", "values": [{"value": 0, "odd": "9.00"},
                                                                 {"value": 1, "odd": "4.50"}]},
        ]}],
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
    mercados = sorted({(b, v) for b, v in con.execute("SELECT bet_name, value FROM odds")})
    check("solo se guardan los mercados del contrato: 1X2 y más/menos 2.5, ni córners ni 1.5 ni 1er tiempo",
          mercados == [("Goals Over/Under", "Over 2.5"), ("Goals Over/Under", "Under 2.5"),
                       ("Match Winner", "Away"), ("Match Winner", "Draw"), ("Match Winner", "Home")], mercados)
    hist = sorted({(b, v) for b, v in con.execute("SELECT bet_name, value FROM odds_history")})
    check("el historial de movimiento tampoco guarda lo que nadie lee", hist == mercados, hist)

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

    # un valor numérico en el feed no tumba la captura ni se guarda
    from backend.cuota_mercados import cuota_key
    check("cuota_key con un valor numérico devuelve None (no AttributeError)",
          cuota_key("Exact Goals Number", 1) is None and cuota_key("Match Winner", None) is None)
    con = db([(700001, "2026-07-30 20:00:00", "NS")])
    total, cub = capturar_cuotas_lote(ClienteFalso([700001], mundo=0), con, [700001])
    filas = {r[0] for r in con.execute("SELECT bet_name FROM odds WHERE fixture_id=700001")}
    check("un feed con valores numéricos guarda el 1X2 y descarta el resto",
          cub == 1 and "Match Winner" in filas and "Exact Goals Number" not in filas, (total, cub, filas))

    # una excepción en un partido no tumba a los demás
    original = ex.guardar_odds
    def guardar_que_falla(con, fid, items):
        if fid == 700011:
            raise ValueError("feed roto")
        return original(con, fid, items)
    ex.guardar_odds = guardar_que_falla
    try:
        con = db([(700011, "2026-07-30 20:00:00", "NS"), (700012, "2026-07-30 21:00:00", "NS")])
        total, cub = capturar_cuotas_lote(ClienteFalso([700011, 700012], mundo=0), con, [700011, 700012])
        check("un partido que falla al guardar no corta la captura de los otros",
              cub == 1 and con.execute("SELECT COUNT(*) FROM odds WHERE fixture_id=700012").fetchone()[0] > 0,
              (total, cub))
    finally:
        ex.guardar_odds = original

    # LA DOBLE OPORTUNIDAD QUE NO CUADRA CON EL 1X2 DE SU CASA NO SE GUARDA
    # (incidencia 68: 1xBet en Villa–Viking 21/10/2026, 1X 2.60 · X2 1.32 · 12
    # 1.01 con el 1 a 1.29; la media del 1X subía de ~1.05 a 1.46)
    from backend.cuota_mercados import dc_incoherente, sin_dc_incoherente
    _x = {"1": 1.29, "X": 6.91, "2": 10.7}
    check("DC de 1xBet incoherente con su 1X2 (1X 2.60, X2 1.32, 12 1.01); la de Betano (1X 1.08, X2 3.85, 12 1.12) cuadra",
          all(dc_incoherente(s, o, _x) for s, o in (("1X", 2.6), ("X2", 1.32), ("12", 1.01)))
          and not any(dc_incoherente(s, o, {"1": 1.29, "X": 6.5, "2": 10.5}) for s, o in (("1X", 1.08), ("X2", 3.85), ("12", 1.12))))
    check("sin el 1X2 de la casa no se juzga", not dc_incoherente("1X", 2.6, {}))
    _b412 = {"1": 2.31, "X": 3.5, "2": 3.38}
    check("412: la DC muy por debajo de la suma de su 1X2 (1xBet 1X 1.80 con 1X ≈ 1.39) es incoherente; las de las otras casas no",
          dc_incoherente("1X", 1.8, _b412) and not dc_incoherente("12", 1.35, _b412) and not dc_incoherente("X2", 1.61, _b412)
          and not dc_incoherente("1X", 1.36, {"1": 2.25, "X": 3.4, "2": 3.1})
          and not dc_incoherente("1X", 1.3, {"1": 2.25, "X": 3.5, "2": 3.2}))
    _f = [{"casa": "a", "mercado": "1x2", "seleccion": "1", "cuota": 1.29}, {"casa": "a", "mercado": "1x2", "seleccion": "X", "cuota": 6.91},
          {"casa": "a", "mercado": "1x2", "seleccion": "2", "cuota": 10.7}, {"casa": "a", "mercado": "dc", "seleccion": "1X", "cuota": 2.6},
          {"casa": "b", "mercado": "dc", "seleccion": "1X", "cuota": 1.06}]
    check("sin_dc_incoherente saca solo la fila rota", [f["casa"] for f in sin_dc_incoherente(_f) if f["mercado"] == "dc"] == ["b"])
    con3 = db([(900010, "2026-10-21 19:00:00", "NS")])
    it = item_odds(900010)
    it["bookmakers"].append({"id": 11, "name": "1xBet", "bets": [
        {"id": 1, "name": "Match Winner", "values": [{"value": "Home", "odd": "1.29"}, {"value": "Draw", "odd": "6.91"},
                                                     {"value": "Away", "odd": "10.7"}]},
        {"id": 12, "name": "Double Chance", "values": [{"value": "Home/Draw", "odd": "2.60"}, {"value": "Home/Away", "odd": "1.01"},
                                                       {"value": "Draw/Away", "odd": "1.32"}]}]})
    it["bookmakers"][0]["bets"].append({"id": 12, "name": "Double Chance", "values": [
        {"value": "Home/Draw", "odd": "1.20"}, {"value": "Home/Away", "odd": "1.27"}, {"value": "Draw/Away", "odd": "1.85"}]})
    ex.guardar_odds(con3, 900010, [it])
    dc = dict(((c, v), o) for c, v, o in con3.execute(
        "SELECT bookmaker_name, value, odd FROM odds WHERE fixture_id=900010 AND bet_name='Double Chance'"))
    hist = [r[0] for r in con3.execute("SELECT casas FROM odds_history WHERE fixture_id=900010 AND bet_name='Double Chance' "
                                       "AND value='Home/Draw' AND casa IS NULL")]
    check("al guardar: la DC rota de 1xBet queda NULL, la de Bet365 se guarda, y la media del historial cuenta 1 casa",
          dc[("1xBet", "Home/Draw")] is None and dc[("Bet365", "Home/Draw")] == 1.2 and hist == [1], (dc, hist))

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
