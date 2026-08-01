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
    ligas_marcadas_en_juego,
    orden_por_antiguedad,
    preparar_consultas,
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


def item_odds(fid: int, minuto: int = 43, liga: int | None = None) -> dict:
    return {
        "fixture": {"id": fid, "status": {"elapsed": minuto}},
        **({"league": {"id": liga}} if liga else {}),
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

    def __init__(self, feed: dict, presupuesto: int = 99, caen: "set | None" = None,
                 por_fixture: "dict | None" = None, limite: int | None = None,
                 usadas: int = 0, emergencia: "dict | None" = None,
                 tope_emergencia: int = 300, marcadores: "list | None" = None):
        self.marcadores = marcadores or []  # respuesta de /fixtures?ids=
        # emergencia: {"fixtures": [items de /fixtures?ids=], fid: [items odds]}
        # None = sin SAD_EMERGENCIA_KEY configurada
        self.emergencia_feed = emergencia
        self.tope_emergencia = tope_emergencia
        self.usadas_emergencia = 0
        self.feed = feed              # {league_id | None: [items]}
        self.presupuesto = presupuesto
        # el freno de presupuesto lee limite/usadas como el Cliente real; por
        # defecto van holgados para que los demás tests no lo noten
        self.limite = limite if limite is not None else 10**6
        self.usadas = usadas
        self.caen = caen or set()     # ligas cuya request FALLA (red/HTTP/errors)
        self.por_fixture = por_fixture or {}   # {fixture_id: [items]} de ?fixture=
        self.fallos = 0               # el contador que distingue fallo de feed vacío
        self.hechas = 0               # requests de ESTE ciclo (usadas puede venir sembrada)
        self.pedidos: list = []

    def quedan(self, n: int = 1) -> bool:
        return self.presupuesto - self.hechas >= n

    def emergencia_disponible(self, n: int = 1) -> bool:
        return self.emergencia_feed is not None and self.tope_emergencia - self.usadas_emergencia >= n

    def get_emergencia(self, endpoint: str, params: dict):
        if not self.emergencia_disponible():
            return None
        self.usadas_emergencia += 1
        self.pedidos.append(("EMERGENCIA:" + endpoint, params.get("fixture"), params.get("ids")))
        if endpoint == "fixtures":
            return {"response": self.emergencia_feed.get("fixtures", [])}
        return {"response": self.emergencia_feed.get(params.get("fixture"), [])}

    def get(self, endpoint: str, params: dict):
        if not self.quedan():
            return None
        self.usadas += 1
        self.hechas += 1
        if params.get("ids") is not None:
            self.pedidos.append((endpoint, None, params.get("ids")))
            return {"response": self.marcadores, "paging": {"current": 1, "total": 1}}
        self.pedidos.append((endpoint, params.get("league"), params.get("page", 1)))
        liga = params.get("league")
        if liga in self.caen:
            self.fallos += 1          # como el Cliente real ante red/HTTP/errors
            return None
        if params.get("fixture") is not None:
            items = self.por_fixture.get(params["fixture"], [])
        elif liga:
            items = self.feed.get(liga, [])
        else:
            items = [it for lista in self.feed.values() for it in lista]
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

# el esquema real de guardar_fixtures (INSERT OR REPLACE con 25 columnas):
# lo usan los tests del refresco forzado, que guardan la respuesta completa
DDL_FIXTURES_FULL = """
CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT, country TEXT, founded INTEGER, logo TEXT);
CREATE TABLE leagues (id INTEGER PRIMARY KEY, name TEXT, country TEXT, logo TEXT, flag TEXT, season INTEGER);
CREATE TABLE fixtures (id INTEGER PRIMARY KEY, timezone TEXT, date TEXT, timestamp INTEGER,
    venue_id INTEGER, venue_name TEXT, venue_city TEXT, status_long TEXT, status_short TEXT,
    elapsed INTEGER, league_id INTEGER, league_season INTEGER, league_round TEXT,
    home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
    halftime_home INTEGER, halftime_away INTEGER, fulltime_home INTEGER, fulltime_away INTEGER,
    extratime_home INTEGER, extratime_away INTEGER, penalty_home INTEGER, penalty_away INTEGER);
"""


def item_marcador(fid: int, liga: int, status: str = "2H", gh: int = 1, ga: int = 0) -> dict:
    """Item de /fixtures?ids= con lo mínimo que guardar_fixtures exige."""
    return {
        "fixture": {"id": fid, "date": "2026-07-30T22:30:00+00:00",
                    "status": {"long": "x", "short": status, "elapsed": 50}},
        "league": {"id": liga, "name": f"Liga {liga}", "season": 2026},
        "teams": {"home": {"id": 7001, "name": "Local"}, "away": {"id": 7002, "name": "Visita"}},
        "goals": {"home": gh, "away": ga},
        "score": {},
    }


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

    # EL CASO ARGENTINA (29/07/2026, Gimnasia LP–River Plate en el minuto 3 sin
    # cuotas): `por_liga` mezcla las ligas del feed live con las que solo
    # tienen un NS/TBD dentro de una ventana de 3h45, y la cola las trataba
    # igual. Con tope por ciclo, una liga sin nadie jugando le ganaba el turno
    # a otra con el partido corriendo — y el partido se termina, la ventana no.
    con = db()
    con.executemany(
        "INSERT INTO odds_live_consultas (league_id, consultada_en, con_datos) VALUES (?,?,?)",
        [(PERU, "2026-07-29 23:59:00.000", 1)],  # Perú, la única en juego, recién consultada
    )
    con.commit()
    mezcla = {PERU: {MELGAR_CRISTAL}, PREMIER: {OTRO_PAIS}}  # PREMIER solo tiene un NS en ventana
    check("con partido EN JUEGO va primera aunque la hayan consultado recién",
          orden_por_antiguedad(con, mezcla, {PERU}) == [PERU, PREMIER],
          orden_por_antiguedad(con, mezcla, {PERU}))
    check("sin el set de en juego, el orden es el de antes (llamada vieja)",
          orden_por_antiguedad(con, mezcla) == [PREMIER, PERU],
          orden_por_antiguedad(con, mezcla))

    con = db()
    cliente = ClienteFalso(feed)
    en_vivo_mod.TOPE_LIGAS = 1
    try:
        _, cf = capturar_odds_live(cliente, con, mezcla, ids_vivos,
                                   "2026-07-29 23:59:30.000", en_juego={PERU})
    finally:
        en_vivo_mod.TOPE_LIGAS = tope_original
    check("con un solo cupo, el cupo es del partido que se está jugando",
          MELGAR_CRISTAL in cf and OTRO_PAIS not in cf
          and [p[1] for p in cliente.pedidos] == [PERU],
          (cf, cliente.pedidos))

    # POR QUÉ no hubo cuotas: el booleano con_datos mezclaba cuatro causas en
    # una, y la pantalla acabó diciendo "la API no cubre esta liga" en las
    # cuatro (Gimnasia LP-River y Mirassol-Remo, 29/07/2026, con cobertura
    # real). `estado` las separa; solo `vacia` se acerca a falta de cobertura.
    def estado_de_liga(con, lid):
        return con.execute(
            "SELECT estado, items, nuestros, ajenos FROM odds_live_consultas WHERE league_id=?",
            (lid,)).fetchone()

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso(feed)
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-29 23:00:00.000")
    check("liga que devuelve nuestros partidos → estado ok",
          estado_de_liga(con, PERU)[0] == "ok", estado_de_liga(con, PERU))

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso({PERU: [], PREMIER: feed[PREMIER]})
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-29 23:01:00.000")
    check("feed realmente vacío → estado vacia (lo único parecido a sin cobertura)",
          estado_de_liga(con, PERU) == ("vacia", 0, 0, 0), estado_de_liga(con, PERU))

    con = db()
    preparar_consultas(con)
    # la API devuelve partidos, pero de OTRA liga: el filtro ?league= no filtró
    cliente = ClienteFalso({PERU: [item_odds(700001, liga=61), item_odds(700002, liga=61)],
                            PREMIER: feed[PREMIER]})
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-29 23:02:00.000")
    check("feed con partidos ajenos → estado ajena, con los ajenos contados",
          estado_de_liga(con, PERU) == ("ajena", 2, 0, 2), estado_de_liga(con, PERU))

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso(feed, caen={PERU})
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-29 23:03:00.000")
    check("request caída → estado fallo (NO 'la API no cubre esta liga')",
          estado_de_liga(con, PERU)[0] == "fallo", estado_de_liga(con, PERU))
    check("una caída no contamina a las demás ligas",
          estado_de_liga(con, PREMIER)[0] == "ok", estado_de_liga(con, PREMIER))

    # RESCATE POR FIXTURE: si la ronda por liga no trajo un partido que SÍ se
    # está jugando, se le pregunta directamente. Es lo que salva la curva
    # cuando el feed por liga falla por cualquiera de las tres causas de arriba.
    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso({PERU: [], PREMIER: []},
                           por_fixture={MELGAR_CRISTAL: [item_odds(MELGAR_CRISTAL)]})
    n, con_feed = capturar_odds_live(cliente, con, por_liga, ids_vivos,
                                     "2026-07-29 23:04:00.000",
                                     ids_en_juego={MELGAR_CRISTAL, OTRO_PAIS})
    check("con el feed por liga vacío, el rescate por fixture trae la cuota igual",
          MELGAR_CRISTAL in con_feed and n == 3, (con_feed, n))
    check("el rescate pregunta por fixture, no por liga",
          any(p[0] == "odds/live" and p[1] is None for p in cliente.pedidos), cliente.pedidos)

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso(feed)
    tope_fx = en_vivo_mod.TOPE_FIXTURES
    en_vivo_mod.TOPE_FIXTURES = 0
    try:
        _, con_feed = capturar_odds_live(cliente, con, {PERU: {MELGAR_CRISTAL}}, ids_vivos,
                                         "2026-07-29 23:05:00.000",
                                         ids_en_juego={MELGAR_CRISTAL})
    finally:
        en_vivo_mod.TOPE_FIXTURES = tope_fx
    check("con SAD_LIVE_ODDS_FIXTURES=0 el rescate queda apagado",
          all(p[1] is not None for p in cliente.pedidos), cliente.pedidos)

    # FRENO DE PRESUPUESTO (29/07/2026: 7496/7495 y el respaldo agotado — cero
    # requests, cero cuotas, cero marcador, y las copas que funcionaban paradas
    # a mitad de partido). Un ciclo por minuto sin freno propio se come el plan
    # del día y deja sin datos a TODO, incluida la ingesta diaria.
    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso(feed, limite=7495, usadas=7400)  # dentro de la reserva
    n, con_feed = capturar_odds_live(cliente, con, por_liga, ids_vivos,
                                     "2026-07-29 23:35:00.000", ids_en_juego=ids_vivos)
    check("con el plan dentro de la reserva NO se piden cuotas (ni el rescate)",
          cliente.pedidos == [] and n == 0 and con_feed == set(),
          (cliente.pedidos, n, con_feed))
    check("y no se escribe ninguna ronda: no hubo consulta que registrar",
          con.execute("SELECT COUNT(*) FROM odds_live_consultas").fetchone()[0] == 0)

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso(feed, limite=7495, usadas=5990)  # margen justo: 5 sobre reserva
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-29 23:36:00.000")
    check("con margen justo el cupo se encoge en vez de chocar contra la pared",
          0 < len({p[1] for p in cliente.pedidos}) < 2, cliente.pedidos)

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso(feed, limite=7495, usadas=0)
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-29 23:37:00.000")
    check("con el plan holgado se sirven todas las ligas del tope",
          {p[1] for p in cliente.pedidos} == {PERU, PREMIER}, cliente.pedidos)

    check("el tope por ciclo vuelve a 6: 12 duplicaba el consumo del ciclo",
          en_vivo_mod.TOPE_LIGAS == 6, en_vivo_mod.TOPE_LIGAS)

    # VIP "sí o sí" + MODO EMERGENCIA (la lección cara del 29/07/2026: plan y
    # respaldo muertos con Vasco-Medellín y Gimnasia-River en juego, y ninguna
    # forma de pagar solo por lo importante)
    import json as _json
    import tempfile

    def vip_json(marcas: dict) -> str:
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        _json.dump(marcas, f)
        f.close()
        return f.name

    con = db(con_fixtures=True)
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    vieja = (datetime.now(timezone.utc) - timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
    con.executemany(
        "INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?,?,?,?)",
        [(MELGAR_CRISTAL, hace(20), "1H", 282),   # ¡liga MENOR! la marca manda
         (OTRO_PERU, hace(30), "1H", PERU),       # marca caducada
         (OTRO_PAIS, hace(600), "FT", PREMIER)],  # terminado: fuera de ventana
    )
    con.commit()
    ruta = vip_json({str(MELGAR_CRISTAL): ahora, str(OTRO_PERU): vieja, str(OTRO_PAIS): ahora})
    vip = en_vivo_mod.fixtures_vip(con, ruta)
    check("VIP: la marca manda aunque la liga sea menor", MELGAR_CRISTAL in vip, vip)
    check("VIP: la marca caducada (>8h) no cuenta — nadie paga por un olvido",
          OTRO_PERU not in vip, vip)
    check("VIP: un partido fuera de ventana no entra aunque esté marcado",
          OTRO_PAIS not in vip, vip)

    # emergencia: marcador para todos los VIP sin servir, cuotas SOLO para los
    # que ese marcador confirma en juego
    con = db(con_fixtures=True)
    preparar_ficha(con)
    cliente = ClienteFalso({}, presupuesto=0, emergencia={
        "fixtures": [{"fixture": {"id": MELGAR_CRISTAL, "status": {"short": "2H"}}},
                     {"fixture": {"id": OTRO_PERU, "status": {"short": "NS"}}}],
        MELGAR_CRISTAL: [item_odds(MELGAR_CRISTAL)],
        OTRO_PERU: [item_odds(OTRO_PERU)],
    })
    n = en_vivo_mod.capturar_emergencia(cliente, con, [MELGAR_CRISTAL, OTRO_PERU],
                                        "2026-07-29 23:40:00.000")
    check("emergencia: cuotas del VIP confirmado en juego", n == 3, n)
    check("emergencia: al NS solo se le pagó el marcador compartido, no cuotas",
          cliente.usadas_emergencia == 2 and not any(
              p[1] == OTRO_PERU for p in cliente.pedidos if p[0].startswith("EMERGENCIA:odds")),
          (cliente.usadas_emergencia, cliente.pedidos))
    guardadas = con.execute("SELECT COUNT(*) FROM odds_live WHERE fixture_id=?",
                            (MELGAR_CRISTAL,)).fetchone()[0]
    check("emergencia: las cuotas quedan en odds_live como las normales", guardadas == 3, guardadas)

    cliente = ClienteFalso({}, presupuesto=0, emergencia=None)
    check("sin SAD_EMERGENCIA_KEY la emergencia no hace nada (0 requests)",
          en_vivo_mod.capturar_emergencia(cliente, con, [MELGAR_CRISTAL], "x") == 0
          and cliente.pedidos == [], cliente.pedidos)

    cliente = ClienteFalso({}, presupuesto=0, tope_emergencia=1,
                           emergencia={"fixtures": [], MELGAR_CRISTAL: [item_odds(MELGAR_CRISTAL)]})
    check("el tope de emergencia manda: sin techo para 2 requests ni empieza",
          en_vivo_mod.capturar_emergencia(cliente, con, [MELGAR_CRISTAL], "x") == 0
          and cliente.usadas_emergencia == 0, cliente.usadas_emergencia)

    # REFRESCO FORZADO DE LIGA (el botón ⟳ de Partidos): el pedido en
    # .refresco_ligas.json actualiza el marcador de la liga aunque sea menor,
    # se consume al atenderse, y caducado no gasta nada
    def refresco_json(marcas: dict) -> str:
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        _json.dump(marcas, f)
        f.close()
        return f.name

    import os as _os
    con = sqlite3.connect(":memory:")
    con.executescript(DDL_ODDS_LIVE + DDL_FIXTURES_FULL)
    preparar_ficha(con)
    # NS congelado de una liga MENOR (282) que en realidad ya se juega
    con.execute("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?,?,?,?)",
                (MELGAR_CRISTAL, hace(20), "NS", 282))
    con.commit()
    ruta = refresco_json({"282": ahora})
    cliente = ClienteFalso({}, marcadores=[item_marcador(MELGAR_CRISTAL, 282)])
    n = en_vivo_mod.refrescar_ligas_pedidas(cliente, con, ya_frescos=set(), ruta=ruta)
    fila = con.execute("SELECT status_short, goals_home FROM fixtures WHERE id=?",
                       (MELGAR_CRISTAL,)).fetchone()
    check("refresco forzado: el NS congelado de una liga menor pasa a su estado real",
          n == 1 and fila == ("2H", 1), (n, fila))
    check("refresco forzado: el pedido se consume (el archivo desaparece)",
          not _os.path.exists(ruta))
    check("refresco forzado: costó 1 request de marcador",
          [p[0] for p in cliente.pedidos] == ["fixtures"], cliente.pedidos)

    ruta = refresco_json({"282": vieja})  # pedido caducado (>30 min... 9h)
    cliente = ClienteFalso({})
    check("refresco forzado: un pedido caducado no gasta nada",
          en_vivo_mod.refrescar_ligas_pedidas(cliente, con, ya_frescos=set(), ruta=ruta) == 0
          and cliente.pedidos == [], cliente.pedidos)

    # LA VENTANA (bug 30/07/2026: el ⟳ daba ✓ y no pasaba nada). El forzado
    # tiene su PROPIA ventana ancha: usaba la de juego (−210 min/+15 min) y
    # dejaba fuera justo lo que el usuario quiere arreglar — los NS congelados
    # de hace horas y los partidos que arrancan más tarde.
    con2 = sqlite3.connect(":memory:")
    con2.executescript(DDL_ODDS_LIVE + DDL_FIXTURES_FULL)
    con2.executemany("INSERT INTO fixtures (id,date,status_short,league_id) VALUES (?,?,?,?)", [
        (901, hace(30), "NS", 11),         # dentro de la ventana de juego
        (902, hace(250), "NS", 11),        # congelado hace 4h10 — antes FUERA
        (903, hace(-90), "NS", 11),        # arranca en 1h30  — antes FUERA
        (904, hace(60), "FT", 11),         # terminado: no se toca
        (905, hace(60), "NS", 71),         # otra liga: no se pide
        (906, hace(60 * 20), "NS", 11),    # hace 20 h: fuera hasta del forzado
    ])
    con2.commit()
    check("la ventana del forzado abarca congelados viejos y próximos, no los terminados",
          en_vivo_mod.fixtures_para_refresco(con2, {11}) == [902, 901, 903],  # asc por fecha
          en_vivo_mod.fixtures_para_refresco(con2, {11}))

    # el pedido SOBREVIVE si no hubo con qué servirlo (antes se borraba igual y
    # el click se evaporaba en silencio: ✓ en pantalla y nada más, para siempre)
    ruta = refresco_json({"11": ahora})
    cliente = ClienteFalso({}, presupuesto=0, emergencia=None)
    n = en_vivo_mod.refrescar_ligas_pedidas(cliente, con2, ya_frescos=set(), ruta=ruta)
    check("sin presupuesto ni emergencia, el pedido NO se consume: sigue vivo",
          n == 0 and _os.path.exists(ruta) and cliente.pedidos == [], (n, cliente.pedidos))
    cliente = ClienteFalso({}, marcadores=[item_marcador(902, 11)])
    check("y el ciclo siguiente, con presupuesto, lo atiende",
          en_vivo_mod.refrescar_ligas_pedidas(cliente, con2, ya_frescos=set(), ruta=ruta) == 1
          and not _os.path.exists(ruta))

    # "nada que refrescar" sí consume el pedido: no hay nada que esperar
    ruta = refresco_json({"71": ahora})
    con2.execute("UPDATE fixtures SET status_short='FT' WHERE league_id=71")
    con2.commit()
    cliente = ClienteFalso({})
    check("sin partidos que refrescar, el pedido se consume y no gasta requests",
          en_vivo_mod.refrescar_ligas_pedidas(cliente, con2, ya_frescos=set(), ruta=ruta) == 0
          and not _os.path.exists(ruta) and cliente.pedidos == [], cliente.pedidos)

    # con el plan muerto, el marcador sale por la clave de emergencia
    con.execute("UPDATE fixtures SET status_short='NS', goals_home=NULL, date=? WHERE id=?",
                (hace(20), MELGAR_CRISTAL))
    con.commit()
    ruta = refresco_json({"282": ahora})
    cliente = ClienteFalso({}, presupuesto=0,
                           emergencia={"fixtures": [item_marcador(MELGAR_CRISTAL, 282)]})
    n = en_vivo_mod.refrescar_ligas_pedidas(cliente, con, ya_frescos=set(), ruta=ruta)
    check("refresco forzado con plan muerto: el marcador sale por la emergencia",
          n == 1 and cliente.usadas_emergencia == 1
          and any(p[0] == "EMERGENCIA:fixtures" for p in cliente.pedidos),
          (n, cliente.pedidos))

    # LAS DOS RESERVAS (30/07/2026: 309 ciclos con las cuotas en juego EN
    # PAUSA, 5 h 30 min de prime time sudamericano, y el plan ni se agotó —
    # 6.670/7.495). La ingesta en bloque paraba al dejar 1.500 y el ciclo en
    # vivo se apaga por debajo de 1.500: el margen real del vivo era CERO.
    # Con fútbol cerca, el bloque tiene que ceder — la ficha de un partido
    # terminado se baja mañana; la curva de uno en juego pasa una vez.
    from backend.ingesta.extractor import hay_partidos_cerca, reserva_del_dia

    con3 = sqlite3.connect(":memory:")
    con3.executescript(DDL_FIXTURES)
    check("sin fútbol cerca, el bloque usa su reserva base y avanza",
          reserva_del_dia(7495, con3) == 1500 and hay_partidos_cerca(con3) == 0,
          reserva_del_dia(7495, con3))
    con3.execute("INSERT INTO fixtures (id,date,status_short,league_id) VALUES (?,?,?,?)",
                 (1, hace(-120), "NS", 11))  # Sudamericana en 2 h
    con3.commit()
    check("con fútbol nuestro cerca, la reserva del bloque SUBE",
          reserva_del_dia(7495, con3) == 3500, reserva_del_dia(7495, con3))
    check("y así el ciclo en vivo tiene margen real en vez de cero",
          reserva_del_dia(7495, con3) - en_vivo_mod.RESERVA_VIVO >= 1500,
          reserva_del_dia(7495, con3) - en_vivo_mod.RESERVA_VIVO)
    con3.execute("UPDATE fixtures SET status_short='FT'")
    con3.commit()
    check("un partido ya terminado no cuenta como fútbol cerca",
          hay_partidos_cerca(con3) == 0, hay_partidos_cerca(con3))
    con3.execute("UPDATE fixtures SET status_short='NS', league_id=282")
    con3.commit()
    check("una liga menor tampoco frena al bloque (no recibe ciclo en vivo)",
          hay_partidos_cerca(con3) == 0, hay_partidos_cerca(con3))

    # BACKOFF POR LIGA (auditoría del 31/07/2026: 506 rondas por liga vacías +
    # 290 rescates por fixture con CERO aciertos = 796 requests tiradas, el 11%
    # del plan, en confirmar 115 veces la misma noche que la API no cubre
    # Bolivia). Preguntar una vez está bien; insistir cada ciclo, no.
    check("el backoff crece con las rondas vacías y topa BAJO (10 min)",
          [en_vivo_mod.espera_backoff(v) for v in (0, 1, 3, 10, 50)] == [0, 3, 9, 10, 10],
          [en_vivo_mod.espera_backoff(v) for v in (0, 1, 3, 10, 50)])
    # EL CASO LOS CHANKAS: la liga estuvo 45 min vacía y luego dio 227 capturas
    # seguidas. Un feed vacío es TEMPORAL casi siempre, así que el tope no puede
    # ser grande: lo que se espera de más se pierde de la apertura del mercado.
    check("esperar de más no ahorra: en 45 min de vacío el tope alto casi no baja consultas",
          en_vivo_mod.BACKOFF_MAX_MIN <= 10, en_vivo_mod.BACKOFF_MAX_MIN)

    con = db()
    preparar_consultas(con)
    ahora_s = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    con.executemany(
        "INSERT INTO odds_live_consultas (league_id, consultada_en, con_datos, estado, vacias_seguidas) "
        "VALUES (?,?,?,?,?)",
        [(PERU, ahora_s, 1, "ok", 0),          # trae datos: nunca duerme
         (PREMIER, ahora_s, 0, "vacia", 10)],  # 10 vacías seguidas: tope (10 min)
    )
    con.commit()
    check("una liga que trae datos no entra nunca en espera",
          PERU not in en_vivo_mod.ligas_en_backoff(con, {PERU, PREMIER}))
    check("una liga con 10 rondas vacías seguidas espera el tope",
          PREMIER in en_vivo_mod.ligas_en_backoff(con, {PERU, PREMIER}))
    con.execute("UPDATE odds_live_consultas SET consultada_en=? WHERE league_id=?",
                ((datetime.now(timezone.utc) - timedelta(minutes=11)).strftime("%Y-%m-%d %H:%M:%S"), PREMIER))
    con.commit()
    check("pasado el tope se le vuelve a preguntar (el mercado pudo abrir)",
          PREMIER not in en_vivo_mod.ligas_en_backoff(con, {PERU, PREMIER}))

    # el contador: 'ok' resetea · 'vacia' suma · 'fallo' NO castiga
    def vacias(con, lid):
        return con.execute("SELECT vacias_seguidas FROM odds_live_consultas WHERE league_id=?",
                           (lid,)).fetchone()[0]

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso({PERU: [], PREMIER: feed[PREMIER]})
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-31 23:00:00.000")
    check("una ronda vacía suma al contador", vacias(con, PERU) == 1, vacias(con, PERU))
    check("una ronda con datos lo deja en cero", vacias(con, PREMIER) == 0, vacias(con, PREMIER))

    con = db()
    preparar_consultas(con)
    cliente = ClienteFalso(feed, caen={PERU})
    capturar_odds_live(cliente, con, por_liga, ids_vivos, "2026-07-31 23:01:00.000")
    check("un FALLO de red no castiga a la liga (no dice nada de la cobertura)",
          vacias(con, PERU) == 0, vacias(con, PERU))

    # y el rescate por fixture no insiste en una liga dormida
    con = db()
    preparar_consultas(con)
    con.execute("INSERT INTO odds_live_consultas (league_id, consultada_en, con_datos, estado, "
                "vacias_seguidas) VALUES (?,?,0,'vacia',10)", (PERU, ahora_s))
    con.commit()
    cliente = ClienteFalso({PERU: [], PREMIER: []},
                           por_fixture={MELGAR_CRISTAL: [item_odds(MELGAR_CRISTAL)]})
    capturar_odds_live(cliente, con, {PERU: {MELGAR_CRISTAL}}, ids_vivos,
                       "2026-07-31 23:02:00.000", ids_en_juego={MELGAR_CRISTAL})
    check("liga dormida: ni ronda ni rescate por fixture (0 requests)",
          cliente.pedidos == [], cliente.pedidos)

    # ROTACIÓN DEL RESCATE (01/08/2026, México): con 6 partidos en juego y
    # tope 4, `sorted(faltan)[:4]` servía SIEMPRE a los mismos ids bajos — los
    # dos de id más alto no se rescataban nunca. Hoy no se nota porque los 4
    # devuelven vacío, pero en cuanto vuelva la cobertura quedarían ciegos.
    con = db()
    preparar_consultas(con)
    seis = [1505482, 1519436, 1549698, 1550912, 1581376, 1607654]
    check("sin intentos previos, el orden es estable",
          en_vivo_mod.orden_rescate(con, seis) == sorted(seis))
    con.executemany(
        "INSERT INTO odds_live_rescates (fixture_id, intentado_en) VALUES (?,?)",
        [(f, "2026-08-01 00:10:00.000") for f in seis[:4]])  # los 4 primeros ya tuvieron turno
    con.commit()
    check("los que ya tuvieron turno van al final: entran los que nunca entraron",
          en_vivo_mod.orden_rescate(con, seis)[:2] == [1581376, 1607654],
          en_vivo_mod.orden_rescate(con, seis))

    con = db(con_fixtures=True)
    preparar_consultas(con)
    preparar_ficha(con)
    # dos ciclos seguidos con tope 2: los 4 fixtures tienen que entrar todos
    por_liga_6 = {PERU: set(seis)}
    tope_fx = en_vivo_mod.TOPE_FIXTURES
    en_vivo_mod.TOPE_FIXTURES = 2
    try:
        pedidos = []
        for i in range(3):
            cliente = ClienteFalso({PERU: []})
            capturar_odds_live(cliente, con, por_liga_6, set(seis),
                               f"2026-08-01 01:0{i}:00.000", ids_en_juego=set(seis))
            pedidos += [p[1] for p in cliente.pedidos if p[0] == "odds/live" and p[1] is None]
    finally:
        en_vivo_mod.TOPE_FIXTURES = tope_fx
    atendidos = {f for f, _ in con.execute("SELECT fixture_id, intentado_en FROM odds_live_rescates")}
    check("en 3 ciclos con tope 2, TODOS los 6 fixtures tuvieron su turno",
          atendidos == set(seis), sorted(atendidos))

    # y si el feed live tuvo un hipo, la liga sigue contando como en juego:
    # el estado EN_JUEGO de nuestra base no se pone solo, lo escribió el feed
    con = db(con_fixtures=True)
    con.executemany(
        "INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?,?,?,?)",
        [(MELGAR_CRISTAL, hace(20), "1H", PERU),   # jugando según nuestra base
         (OTRO_PAIS, hace(5), "NS", PREMIER)],     # solo un NS en ventana
    )
    con.commit()
    check("una liga marcada en juego cuenta aunque el feed no la devuelva",
          ligas_marcadas_en_juego(con, {PERU, PREMIER}) == {PERU},
          ligas_marcadas_en_juego(con, {PERU, PREMIER}))

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
    check(f"con {len(ligas_vivo())} ligas nuestras se pide live=all (el filtro por ids no da)",
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
