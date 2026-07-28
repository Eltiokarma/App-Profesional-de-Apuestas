"""Test del ciclo EN VIVO (backend/ingesta/en_vivo.py) — sin red ni sad.db.

Blinda la regla que rompió la cobertura de cuotas en juego: /odds/live viene
PAGINADO (~10 fixtures por página) y sin filtro las primeras páginas son de
cualquier liga del mundo, así que hay que pedirlo POR LIGA.

    python -m backend.test_en_vivo
"""
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

from backend.ingesta import en_vivo as en_vivo_mod
from backend.ingesta.en_vivo import (
    DDL_ODDS_LIVE,
    TOPE_LIGAS_LIVE,
    XI_REINTENTO_MIN,
    candidatos_por_liga,
    capturar_odds_live,
    capturar_xi,
    fixtures_para_xi,
    ligas_de_vivos,
    orden_por_antiguedad,
)
from backend.ingesta.extractor import ligas_vivo
from backend.ingesta.ficha_partido import preparar_tablas as preparar_ficha

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


PERU, PREMIER = 281, 39
MELGAR_CRISTAL, OTRO_PERU, OTRO_PAIS = 900001, 900002, 900003


def item_odds(fid: int, minuto: int = 43) -> dict:
    return {
        "fixture": {"id": fid, "status": {"elapsed": minuto}},
        "odds": [{"id": 59, "name": "Fulltime Result", "values": [
            {"value": "Home", "odd": "1.69"},
            {"value": "Draw", "odd": "3.75"},
            {"value": "Away", "odd": "4.52", "suspended": True},
        ]}],
    }


class ClienteFalso:
    """Emula /odds/live de API-Football: paginado a 2 fixtures por página y con
    el mundo entero delante cuando no se filtra por liga."""

    PAGINA = 2

    def __init__(self, feed: dict, presupuesto: int = 99):
        self.feed = feed              # {league_id | None: [items]}
        self.presupuesto = presupuesto
        self.usadas = 0
        self.pedidos: list = []

    def quedan(self, n: int = 1) -> bool:
        return self.presupuesto - self.usadas >= n

    def get(self, endpoint: str, params: dict):
        if not self.quedan():
            return None
        self.usadas += 1
        self.pedidos.append((endpoint, params.get("league"), params.get("page", 1)))
        liga = params.get("league")
        items = self.feed.get(liga, []) if liga else [
            it for lista in self.feed.values() for it in lista
        ]
        pagina = int(params.get("page", 1))
        total = max(1, -(-len(items) // self.PAGINA))
        trozo = items[(pagina - 1) * self.PAGINA: pagina * self.PAGINA]
        return {"response": trozo, "paging": {"current": pagina, "total": total}}

    def paginado(self, endpoint: str, params: dict, tope_paginas: int = 0) -> list:
        data = self.get(endpoint, params)
        if not data:
            return []
        filas = list(data["response"])
        total = data["paging"]["total"]
        ultima = min(total, tope_paginas) if tope_paginas > 0 else total
        for pagina in range(2, ultima + 1):
            data = self.get(endpoint, {**params, "page": pagina})
            if not data:
                break
            filas.extend(data["response"])
        return filas


DDL_FIXTURES = """
CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT,
                       league_id INTEGER, goals_home INTEGER, goals_away INTEGER);
"""


def db(con_fixtures: bool = False) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.executescript(DDL_ODDS_LIVE)
    if con_fixtures:
        con.executescript(DDL_FIXTURES)
    return con


def hace(minutos: int) -> str:
    """Fecha en el formato de sad.db, `minutos` antes de ahora (negativo = futuro)."""
    return (datetime.now(timezone.utc) - timedelta(minutes=minutos)).strftime("%Y-%m-%d %H:%M:%S.%f")


def main():
    vivos = [
        {"fixture": {"id": MELGAR_CRISTAL}, "league": {"id": PERU}},
        {"fixture": {"id": OTRO_PERU}, "league": {"id": PERU}},
        {"fixture": {"id": OTRO_PAIS}, "league": {"id": PREMIER}},
    ]
    ids_vivos = {MELGAR_CRISTAL, OTRO_PERU, OTRO_PAIS}

    por_liga = ligas_de_vivos(vivos)
    check("agrupa los vivos por liga", por_liga == {PERU: {MELGAR_CRISTAL, OTRO_PERU}, PREMIER: {OTRO_PAIS}}, por_liga)

    # el mundo entero delante: 20 partidos de otras ligas ocupan las primeras
    # páginas del feed sin filtro (el caso real que dejaba a Perú sin cuotas)
    ruido = [item_odds(700000 + i) for i in range(20)]
    feed = {
        None: ruido,  # solo llega si alguien pide sin filtrar
        PERU: [item_odds(MELGAR_CRISTAL), item_odds(OTRO_PERU)],
        PREMIER: [item_odds(OTRO_PAIS)],
    }
    feed[None] = ruido + feed[PERU] + feed[PREMIER]

    con = db()
    cliente = ClienteFalso(feed)
    n, con_feed = capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-26 20:43:00.000")
    check("pide /odds/live filtrado por liga (nunca el feed global)",
          all(p[0] == "odds/live" and p[1] in (PERU, PREMIER) for p in cliente.pedidos), cliente.pedidos)
    check("una request por liga, no por partido", len(cliente.pedidos) == 2, cliente.pedidos)
    check("captura las cuotas de los 3 partidos vivos", con_feed == ids_vivos, con_feed)
    check("guarda 3 valores por partido (9)", n == 9, n)
    guardadas = con.execute("SELECT COUNT(*) FROM odds_live WHERE fixture_id=?", (MELGAR_CRISTAL,)).fetchone()[0]
    check("el partido de Perú - Primera División queda en odds_live", guardadas == 3, guardadas)
    susp = con.execute("SELECT COUNT(*) FROM odds_live WHERE suspendida=1").fetchone()[0]
    check("marca las suspendidas", susp == 3, susp)
    minuto = con.execute("SELECT minuto FROM odds_live WHERE fixture_id=? LIMIT 1", (MELGAR_CRISTAL,)).fetchone()[0]
    check("guarda el minuto de la captura", minuto == 43, minuto)

    # la liga sin cobertura real de la API no rompe a las demás
    con = db()
    cliente = ClienteFalso({PERU: feed[PERU], PREMIER: []})
    n, con_feed = capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-26 20:44:00.000")
    check("sin cobertura en una liga, las otras igual capturan",
          con_feed == {MELGAR_CRISTAL, OTRO_PERU}, con_feed)

    # EL CASO GRUESO: /fixtures?live= no devolvió el partido peruano (recorte
    # del filtro, hipo de la API…). Las cuotas se piden igual porque la liga
    # entra por nuestros candidatos locales, no solo por ese feed.
    con = db()
    cliente = ClienteFalso(feed)
    solo_premier = ligas_de_vivos([{"fixture": {"id": OTRO_PAIS}, "league": {"id": PREMIER}}])
    union = {**solo_premier, PERU: {MELGAR_CRISTAL, OTRO_PERU}}  # como lo arma main()
    n, con_feed = capturar_odds_live(cliente, con, union, ids_vivos, "2026-07-26 20:46:00.000")
    check("si el feed de fixtures se deja una liga, sus cuotas se piden igual",
          MELGAR_CRISTAL in con_feed, con_feed)

    # rotación: con tope de ligas por ciclo va primero la de CONSULTA más vieja
    # (no la de captura: eso era el bug de Ecuador, ver más abajo)
    con = db()
    con.execute(
        "INSERT INTO odds_live_consultas (league_id, consultada_en, con_datos) VALUES (?,?,?)",
        (PREMIER, "2026-07-26 20:40:00.000", 1),
    )
    con.commit()
    orden = orden_por_antiguedad(con, por_liga)
    check("la liga nunca consultada va primera", orden[0] == PERU, orden)
    con.execute(
        "INSERT INTO odds_live_consultas (league_id, consultada_en, con_datos) VALUES (?,?,?)",
        (PERU, "2026-07-26 20:42:00.000", 1),
    )
    con.commit()
    check("con ambas consultadas manda la más vieja",
          orden_por_antiguedad(con, por_liga) == [PREMIER, PERU], orden_por_antiguedad(con, por_liga))

    # EL CASO ECUADOR (27/07/2026, Guayaquil City–U. Católica): una liga donde
    # la API no da odds live nunca captura nada; rotando por CAPTURA quedaba
    # pegada al frente de la cola para siempre y, con el tope de ligas por
    # ciclo, acaparaba los cupos — a las ligas con cobertura ni se les
    # preguntaba y la ficha decía "sin cobertura" siendo mentira. Rotando por
    # CONSULTA, la liga vacía también gasta su turno y el siguiente ciclo le
    # toca a la que sí tiene cuotas.
    con = db()
    cliente = ClienteFalso({PERU: feed[PERU], PREMIER: []})  # PREMIER sin cobertura
    tope_original = en_vivo_mod.TOPE_LIGAS
    en_vivo_mod.TOPE_LIGAS = 1
    try:
        _, cf1 = capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-26 20:50:00.000")
        _, cf2 = capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-26 20:51:00.000")
    finally:
        en_vivo_mod.TOPE_LIGAS = tope_original
    check("una liga sin cobertura no acapara el tope: el turno rota a la que sí tiene",
          cf1 | cf2 == {MELGAR_CRISTAL, OTRO_PERU}, (cf1, cf2))
    fila = con.execute(
        "SELECT con_datos FROM odds_live_consultas WHERE league_id=?", (PREMIER,)).fetchone()
    check("odds_live_consultas registra la consulta vacía (con_datos=0)",
          fila is not None and fila[0] == 0, fila)

    # presupuesto agotado a media lista: no se cae, deja el resto al próximo ciclo
    con = db()
    cliente = ClienteFalso(feed, presupuesto=1)
    n, con_feed = capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-26 20:45:00.000")
    check("con presupuesto justo captura lo que puede y no revienta",
          0 < len(con_feed) < 3 and cliente.usadas == 1, (con_feed, cliente.usadas))

    # --- ventana de candidatos: quién entra al ciclo (0 requests) ------------
    con = db(con_fixtures=True)
    filas = [
        (1, hace(30), "NS", PERU),        # arrancó hace 30': aún sin voltear el estado
        (2, hace(30), "TBD", PERU),       # hora por confirmar y ya se juega
        (3, hace(-10), "NS", PERU),       # arranca en 10': saque adelantado / hora desfasada
        (4, hace(-90), "NS", PERU),       # arranca en hora y media: todavía no
        (5, hace(400), "NS", PERU),       # zombi viejo, fuera de la ventana
        (6, hace(50), "1H", PREMIER),     # marcado en juego
        (7, hace(20), "NS", 282),         # liga menor: fuera del ciclo en vivo
        (8, hace(200), "FT", PERU),       # terminado
    ]
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?,?,?,?)", filas)
    con.commit()
    cand = candidatos_por_liga(con, {PERU, PREMIER})
    ids = {fid for fids in cand.values() for fid in fids}
    check("NS recién arrancado entra", 1 in ids, ids)
    check("TBD en juego entra (antes quedaba fuera del ciclo)", 2 in ids, ids)
    check("NS que arranca en minutos entra (margen previo)", 3 in ids, ids)
    check("NS lejano NO entra", 4 not in ids, ids)
    check("zombi fuera de la ventana NO entra", 5 not in ids, ids)
    check("estado en juego entra siempre", 6 in ids, ids)
    check("liga menor NO entra al ciclo en vivo", 7 not in ids, ids)
    check("terminado NO entra", 8 not in ids, ids)
    check("agrupa candidatos por liga", cand[PREMIER] == {6}, cand)

    # /fixtures?live=: con la lista real de ligas hay que ir por live=all
    check("con 37 ligas nuestras se pide live=all (el filtro por ids no da)",
          len(ligas_vivo()) > TOPE_LIGAS_LIVE, len(ligas_vivo()))

    # --- alineaciones prepartido: la ventana del XI y su captura -------------
    con = db(con_fixtures=True)
    preparar_ficha(con)  # tabla alineaciones (la misma de la ficha post-partido)
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?,?,?,?)", [
        (11, hace(-30), "NS", PERU),      # arranca en 30': el XI ya debería estar
        (12, hace(-200), "NS", PERU),     # arranca en 3h20: demasiado pronto
        (13, hace(20), "1H", PERU),       # en juego sin XI: la liga lo publicó tarde
        (14, hace(120), "2H", PERU),      # en juego hace 2 h: su XI ya no se persigue
        (15, hace(-30), "NS", 282),       # liga menor: fuera del ciclo
        (16, hace(-30), "NS", PERU),      # ya tiene XI capturado
        (17, hace(-30), "NS", PERU),      # intento hace 2 min: aún no se reintenta
        (18, hace(-30), "NS", PERU),      # intento viejo: se reintenta
    ])
    con.execute("INSERT INTO alineaciones (fixture_id, team_id, formacion, entrenador, "
                "player_id, jugador, numero, posicion, grid, titular) "
                "VALUES (16, 1, '4-4-2', 'DT', 5, 'Alguien', 1, 'G', '1:1', 1)")
    con.executemany("INSERT INTO xi_intentos (fixture_id, intentada_en, con_datos) VALUES (?,?,0)",
                    [(17, hace(2)), (18, hace(XI_REINTENTO_MIN + 3))])
    con.commit()
    xi = fixtures_para_xi(con, {PERU})
    check("XI: el que arranca en minutos entra", 11 in xi, xi)
    check("XI: el que arranca en horas NO entra (aún no está publicado)", 12 not in xi, xi)
    check("XI: en juego sin XI sigue entrando (publicación tardía)", 13 in xi, xi)
    check("XI: en juego hace horas ya NO se persigue", 14 not in xi, xi)
    check("XI: liga menor NO entra", 15 not in xi, xi)
    check("XI: con alineación ya capturada NO se repite", 16 not in xi, xi)
    check("XI: intento reciente espera su reintento", 17 not in xi, xi)
    check("XI: intento viejo se reintenta", 18 in xi, xi)

    lineups = {11: [
        {"team": {"id": 1}, "formation": "4-4-2", "coach": {"name": "DT Local"},
         "startXI": [{"player": {"id": 100 + i, "name": f"J{i}", "number": i + 1,
                                 "pos": "G" if i == 0 else "D", "grid": f"1:{i + 1}"}} for i in range(11)],
         "substitutes": [{"player": {"id": 200, "name": "Suplente", "number": 12, "pos": "M"}}]},
        {"team": {"id": 2}, "formation": "4-3-3", "coach": {"name": "DT Visita"},
         "startXI": [{"player": {"id": 300 + i, "name": f"V{i}", "number": i + 1,
                                 "pos": "G" if i == 0 else "M", "grid": f"1:{i + 1}"}} for i in range(11)],
         "substitutes": []},
    ]}

    class ClienteXi:
        def __init__(self, feed):
            self.feed, self.usadas, self.pedidos = feed, 0, []

        def quedan(self, n: int = 1) -> bool:
            return True

        def get(self, endpoint, params):
            self.usadas += 1
            self.pedidos.append((endpoint, params.get("fixture")))
            return {"response": self.feed.get(params.get("fixture"), [])}

    cliente = ClienteXi(lineups)
    n_xi = capturar_xi(cliente, con, [11, 13], "2026-07-26 19:05:00.000")
    check("XI: pide fixtures/lineups por fixture",
          all(p[0] == "fixtures/lineups" for p in cliente.pedidos), cliente.pedidos)
    filas_xi = con.execute("SELECT COUNT(*) FROM alineaciones WHERE fixture_id=11 AND titular=1").fetchone()[0]
    check("XI: guarda los 22 titulares del partido publicado", n_xi == 1 and filas_xi == 22, (n_xi, filas_xi))
    intentos = dict(con.execute("SELECT fixture_id, con_datos FROM xi_intentos WHERE fixture_id IN (11,13)"))
    check("XI: anota el intento con y sin datos (el vacío se reintenta luego)",
          intentos == {11: 1, 13: 0}, intentos)
    check("XI: capturado no vuelve a entrar en la ventana", 11 not in fixtures_para_xi(con, {PERU}),
          fixtures_para_xi(con, {PERU}))

    # --- cambios de formación ANTES del saque: refresco único cerca del KO ---
    # 21: XI capturado 1 h antes del saque y el partido arranca en 10 min → un
    #     refresco por si el DT lo cambió. 22: capturado hace nada → no.
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?,?,?,?)", [
        (21, hace(-10), "NS", PERU),
        (22, hace(-10), "NS", PERU),
        (23, hace(-40), "NS", PERU),  # capturado temprano pero faltan 40 min: aún no
    ])
    con.executemany(
        "INSERT INTO alineaciones (fixture_id, team_id, formacion, entrenador, player_id, "
        "jugador, numero, posicion, grid, titular) VALUES (?, 1, '4-4-2', 'DT', 5, 'Alguien', 1, 'G', '1:1', 1)",
        [(21,), (22,), (23,)])
    con.executemany("INSERT INTO xi_intentos (fixture_id, intentada_en, con_datos) VALUES (?,?,1)",
                    [(21, hace(50)), (22, hace(3)), (23, hace(20))])
    con.commit()
    xi = fixtures_para_xi(con, {PERU})
    check("XI: capturado temprano se refresca una vez cerca del saque", 21 in xi, xi)
    check("XI: capturado hace nada NO se refresca", 22 not in xi, xi)
    check("XI: el refresco espera a los últimos minutos antes del saque", 23 not in xi, xi)

    lineups[21] = [
        {"team": {"id": 1}, "formation": "4-3-3", "coach": {"name": "DT Local"},
         "startXI": [{"player": {"id": 400, "name": "Nuevo", "number": 9, "pos": "F", "grid": "4:1"}}],
         "substitutes": []},
    ]
    cliente = ClienteXi(lineups)
    capturar_xi(cliente, con, [21], hace(0))  # el intento del refresco es AHORA
    formacion = con.execute("SELECT formacion FROM alineaciones WHERE fixture_id=21").fetchone()[0]
    check("XI: el refresco reemplaza el once (la formación nueva manda)", formacion == "4-3-3", formacion)
    check("XI: tras el refresco la condición se apaga sola", 21 not in fixtures_para_xi(con, {PERU}),
          fixtures_para_xi(con, {PERU}))

    # hipo de la API en el refresco: la respuesta vacía NO borra el XI que había
    con.execute("UPDATE xi_intentos SET intentada_en=? WHERE fixture_id=21", (hace(50),))
    con.commit()
    cliente = ClienteXi({})  # la API responde vacío
    capturar_xi(cliente, con, [21], "2026-07-26 19:21:00.000")
    quedan = con.execute("SELECT COUNT(*) FROM alineaciones WHERE fixture_id=21").fetchone()[0]
    check("XI: una respuesta vacía no pisa el XI ya capturado", quedan == 1, quedan)

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
