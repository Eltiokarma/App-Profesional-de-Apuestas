"""Test de la ficha de partido (backend/ingesta/ficha_partido.py) — sin red.

Es la fase A del DTP: si esto se rompe, M1/M2 (carriles), M4 (autopsia de
goles) y M6 (rotación) se quedan sin materia prima y el DTP no puede abrir.

    python -m backend.test_ficha
"""
import sqlite3
import sys

from backend.ingesta.ficha_partido import (
    fixtures_pendientes,
    guardar_alineaciones,
    guardar_eventos,
    guardar_stats,
    ingestar_fixture,
    preparar_tablas,
)

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


# respuestas con la forma REAL de API-Football (recortadas)
LINEUPS = [
    {"team": {"id": 100, "name": "Local FC"}, "coach": {"id": 9, "name": "DT Local"},
     "formation": "4-2-3-1",
     "startXI": [
         {"player": {"id": 1, "name": "Portero", "number": 1, "pos": "G", "grid": "1:1"}},
         {"player": {"id": 2, "name": "Lateral Izq", "number": 3, "pos": "D", "grid": "2:1"}},
         {"player": {"id": 3, "name": "Extremo Der", "number": 7, "pos": "F", "grid": "4:3"}},
     ],
     "substitutes": [{"player": {"id": 20, "name": "Suplente", "number": 15, "pos": "M", "grid": None}}]},
    {"team": {"id": 200, "name": "Visita CF"}, "coach": {"id": 8, "name": "DT Visita"},
     "formation": "3-5-2",
     "startXI": [{"player": {"id": 30, "name": "Arquero V", "number": 12, "pos": "G", "grid": "1:1"}}],
     "substitutes": []},
]

EVENTOS = [
    {"time": {"elapsed": 23, "extra": None}, "team": {"id": 100}, "player": {"id": 3, "name": "Extremo Der"},
     "assist": {"id": 2, "name": "Lateral Izq"}, "type": "Goal", "detail": "Normal Goal"},
    {"time": {"elapsed": 90, "extra": 4}, "team": {"id": 200}, "player": {"id": 30, "name": "Arquero V"},
     "assist": {"id": None, "name": None}, "type": "Card", "detail": "Yellow Card"},
]

STATS = [
    {"team": {"id": 100}, "statistics": [{"type": "Ball Possession", "value": "62%"},
                                          {"type": "expected_goals", "value": "1.84"},
                                          {"type": "Shots on Goal", "value": 7}]},
    {"team": {"id": 200}, "statistics": [{"type": "Ball Possession", "value": "38%"},
                                          {"type": "Shots on Goal", "value": None}]},
]


class ClienteFalso:
    def __init__(self, presupuesto=99):
        self.presupuesto, self.usadas, self.limite = presupuesto, 0, presupuesto
        self.pedidos = []

    def quedan(self, n=1):
        return self.presupuesto - self.usadas >= n

    def get(self, endpoint, params):
        if not self.quedan():
            return None
        self.usadas += 1
        self.pedidos.append(endpoint)
        return {"response": {"fixtures/lineups": LINEUPS, "fixtures/events": EVENTOS,
                             "fixtures/statistics": STATS}[endpoint]}

    def resumen(self):
        return " ".join(sorted(set(self.pedidos)))


def db(vieja=False) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    if vieja:
        # tabla como la creaba el ciclo en vivo ANTES de la ficha: sin extra,
        # sin jugador_id y sin asistente
        con.executescript("""CREATE TABLE fixture_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL, minuto INTEGER,
            tipo TEXT, detalle TEXT, equipo_id INTEGER, jugador TEXT);""")
    preparar_tablas(con)
    con.executescript("""CREATE TABLE IF NOT EXISTS fixtures (
        id INTEGER PRIMARY KEY, date TEXT, status_short TEXT, league_id INTEGER,
        home_team_id INTEGER, away_team_id INTEGER);""")
    return con


def main():
    # ── migración: la tabla vieja gana las columnas de M4 sin perder datos ──
    con = db(vieja=True)
    cols = {f[1] for f in con.execute("PRAGMA table_info(fixture_eventos)")}
    check("migra fixture_eventos (extra, jugador_id, asistente)",
          {"extra", "jugador_id", "asistente", "asistente_id"} <= cols, sorted(cols))
    preparar_tablas(con)  # segunda pasada: idempotente
    check("preparar_tablas es idempotente", True)

    # ── alineaciones: XI, banco, formación, DT y GRID (el carril de M2) ─────
    n = guardar_alineaciones(con, 555, LINEUPS)
    check("guarda titulares y suplentes", n == 5, n)
    fila = con.execute("SELECT formacion, entrenador, grid, titular, numero, posicion FROM alineaciones "
                       "WHERE fixture_id=555 AND player_id=3").fetchone()
    check("titular con formación, DT, grid y dorsal",
          fila == ("4-2-3-1", "DT Local", "4:3", 1, 7, "F"), fila)
    suplente = con.execute("SELECT titular FROM alineaciones WHERE player_id=20").fetchone()[0]
    check("el banco queda marcado como no titular", suplente == 0, suplente)
    check("las dos alineaciones del partido",
          con.execute("SELECT COUNT(DISTINCT team_id) FROM alineaciones WHERE fixture_id=555").fetchone()[0] == 2)
    # re-ingesta: reemplaza, no duplica (un XI probable puede volverse oficial)
    guardar_alineaciones(con, 555, LINEUPS)
    check("re-ingestar no duplica filas",
          con.execute("SELECT COUNT(*) FROM alineaciones WHERE fixture_id=555").fetchone()[0] == 5)

    # ── eventos: minuto+añadido, autor y ASISTENTE (M4) ────────────────────
    n = guardar_eventos(con, {"fixture_id": 555, "eventos": EVENTOS})
    check("guarda los eventos", n == 2, n)
    gol = con.execute("SELECT minuto, extra, jugador, jugador_id, asistente, asistente_id, tipo "
                      "FROM fixture_eventos WHERE tipo='Goal'").fetchone()
    check("el gol trae minuto, autor y asistente",
          gol == (23, 0, "Extremo Der", 3, "Lateral Izq", 2, "Goal"), gol)
    tarjeta = con.execute("SELECT minuto, extra, asistente FROM fixture_eventos WHERE tipo='Card'").fetchone()
    check("el minuto añadido se suma (90+4 = 94)", tarjeta == (94, 4, None), tarjeta)
    # la forma que manda el ciclo EN VIVO (envoltorio de /fixtures)
    n = guardar_eventos(con, {"fixture": {"id": 555}, "events": EVENTOS})
    check("acepta también la forma del ciclo en vivo", n == 2, n)
    check("y reemplaza en vez de acumular",
          con.execute("SELECT COUNT(*) FROM fixture_eventos WHERE fixture_id=555").fetchone()[0] == 2)

    # ── stats en formato largo ─────────────────────────────────────────────
    n = guardar_stats(con, 555, STATS)
    check("guarda las métricas de ambos equipos", n == 5, n)
    pos = con.execute("SELECT valor FROM fixture_stats WHERE fixture_id=555 AND team_id=100 "
                      "AND clave='Ball Possession'").fetchone()[0]
    check("posesión tal cual la sirve la API", pos == "62%", pos)
    xg = con.execute("SELECT valor FROM fixture_stats WHERE clave='expected_goals'").fetchone()
    check("xG entra sin migrar esquema (formato largo)", xg == ("1.84",), xg)
    nulo = con.execute("SELECT valor FROM fixture_stats WHERE team_id=200 AND clave='Shots on Goal'").fetchone()
    check("un valor nulo se guarda como NULL, no como 'None'", nulo == (None,), nulo)

    # ── a quién se le pide ficha ───────────────────────────────────────────
    con = db()
    from datetime import datetime, timedelta, timezone

    from backend.ingesta.extractor import LIGAS
    liga = sorted(LIGAS)[0]
    # fechas relativas a hoy: con fechas fijas el test caducaba en cuanto el
    # "NS próximo" quedaba en el pasado
    def dia(delta: int) -> str:
        return (datetime.now(timezone.utc) + timedelta(days=delta)).strftime("%Y-%m-%d 20:00:00")
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id) "
                    "VALUES (?,?,?,?,?,?)", [
        (1, dia(+1), "NS", liga, 100, 200),      # el próximo
        (2, dia(-8), "FT", liga, 100, 300),      # anterior del 100
        (3, dia(-15), "FT", liga, 400, 100),     # el de antes
        (4, dia(-22), "FT", liga, 100, 500),     # más viejo aún
        (5, dia(-7), "FT", liga, 200, 600),      # anterior del 200
        (6, dia(-9), "FT", 999999, 700, 800),    # liga que no seguimos
    ])
    con.commit()
    pend = fixtures_pendientes(con, dias=3, ultimos=2)
    check("solo partidos terminados de los equipos con NS próximo", set(pend) == {2, 3, 5}, pend)
    check("el más reciente primero (si el presupuesto corta, la cadena se salva)",
          pend[0] == 2, pend)
    check("respeta el tope de últimos por equipo (4 queda fuera)", 4 not in pend, pend)
    check("no se mete en ligas que no seguimos", 6 not in pend, pend)

    # ── sellado: aunque venga vacío, no se repregunta para siempre ─────────
    cliente = ClienteFalso()
    ok = ingestar_fixture(cliente, con, 2)
    check("una ficha = 3 requests", ok and cliente.usadas == 3, cliente.usadas)
    check("sella la ficha", con.execute("SELECT COUNT(*) FROM fichas_meta WHERE fixture_id=2").fetchone()[0] == 1)
    check("lo sellado ya no está pendiente", 2 not in fixtures_pendientes(con, dias=3, ultimos=2))

    # ── presupuesto: media ficha no se sella ───────────────────────────────
    cliente = ClienteFalso(presupuesto=2)
    ok = ingestar_fixture(cliente, con, 3)
    check("sin presupuesto para las 3 requests, no empieza", ok is False and cliente.usadas == 0, cliente.usadas)
    check("y no queda ficha a medias sellada",
          con.execute("SELECT COUNT(*) FROM fichas_meta WHERE fixture_id=3").fetchone()[0] == 0)

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
