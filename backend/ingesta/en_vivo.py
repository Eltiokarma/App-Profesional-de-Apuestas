"""Ciclo de ingesta EN VIVO (fase 3 de docs/EXTRACCION_TIEMPO_REAL.md).

Un ciclo por invocación, pensado para el hilo SAD_LIVE_SEGUNDOS de backend.app:
1. Mira en sad.db si hay fixtures nuestros en ventana de juego (NS/TBD entre
   15' antes y 3h30 después del saque, o ya marcados en juego). Sin
   candidatos: sale con 0 requests.
2. /fixtures?live= — marcador, minuto y estado reales (1 request); las ligas
   menores (Liga 2, copas nacionales) no entran; se guardan con
   guardar_fixtures (INSERT OR REPLACE). Con más de TOPE_LIGAS_LIVE ligas se
   pide live=all y el filtro lo hacemos aquí: el parámetro hermano `ids` está
   documentado con tope de 20 y no hay forma de saber si `live` recorta la
   lista — si recortara, se caerían justo las ligas de id alto (Perú 281,
   Venezuela 299, Bolivia 344…).
3. /odds/live?league=<id> POR LIGA con partido nuestro en juego (1-2 requests
   por liga, paginado). OJO: el feed sin filtro está PAGINADO a ~10 fixtures
   por página como el prepartido, así que pedirlo entero devolvía solo los 10
   primeros partidos vivos DEL MUNDO — nuestras ligas casi nunca caían ahí y
   parecía "sin cobertura" (p. ej. Perú - Primera División). Filtrando por
   liga el feed sí llega completo. Las ligas a pedir salen del feed live MÁS
   nuestros candidatos locales: si el paso 2 se deja un partido, sus cuotas se
   piden igual. Las cuotas se apendizan a odds_live con minuto y captured_at.
   Donde la API de verdad no ofrece odds live, queda solo marcador/minuto
   (para saber cuál de los dos casos es: python -m backend.ingesta.diag_vivo).
4. Retención: borra odds_live con más de RETENCION_DIAS días.
5. Alineaciones prepartido (antes del paso 2, porque su ventana arranca antes
   que la de juego): fixtures/lineups de los partidos que arrancan en <= 75
   min o acaban de arrancar sin XI capturado → tabla `alineaciones`, la misma
   de la ficha post-partido. /fixtures/{id}/ficha las sirve en cuanto existen
   y el análisis (EFE/DTP/skills) puede completarse antes del saque.

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
# los eventos (goles con minuto, autor y asistente) los define la ficha de
# partido: el ciclo en vivo y la ingesta post-partido escriben lo mismo
from backend.ingesta.ficha_partido import (
    guardar_alineaciones,
    guardar_eventos,
    preparar_tablas as preparar_ficha,
)

VENTANA_JUEGO_MIN = 210  # arrancó hace <= 3h30: cubre alargue, penales y pausas largas
VENTANA_PREVIA_MIN = 15  # y hasta 15' ANTES: cubre saques adelantados y horas desfasadas
RETENCION_DIAS = 30  # la curva en vivo de un partido terminado es material de estudio
EN_JUEGO = ("1H", "HT", "2H", "ET", "BT", "P", "LIVE", "INT", "SUSP")
PREVIOS = ("NS", "TBD")  # estados de "aún no empezó" en esta DB (ver diagnostico.py)

# /fixtures?live= acepta lista de ligas, pero el parámetro hermano `ids` está
# documentado con tope de 20 y de `live` no hay tope publicado: con 37 ligas
# nuestras, confiar en que el filtro del servidor las respete todas es apostar
# a ciegas — y si recorta, las de id alto (Perú 281, Venezuela 299, Bolivia
# 344…) son justo las que se caen. Pasado el tope pedimos live=all y filtramos
# nosotros: mismo coste (1 request) y ninguna liga puede quedarse fuera.
TOPE_LIGAS_LIVE = 20

# Cuotas en juego: 1 request por LIGA con partido nuestro vivo (todos los
# partidos simultáneos de esa liga vienen en la misma respuesta). Topes para que
# un ciclo que corre cada minuto no se coma el presupuesto del día:
#   SAD_LIVE_ODDS_LIGAS=6   ligas por ciclo (0 = sin tope). Las que no entran no
#                           se pierden: el orden es por antigüedad de CONSULTA
#                           (odds_live_consultas), así que rotan y en el ciclo
#                           siguiente van primeras. OJO: no por antigüedad de
#                           captura — ver orden_por_antiguedad.
#   SAD_LIVE_ODDS_PAGINAS=3 páginas por liga (~10 fixtures por página).
TOPE_LIGAS = int(os.environ.get("SAD_LIVE_ODDS_LIGAS", "6"))
TOPE_PAGINAS = max(1, int(os.environ.get("SAD_LIVE_ODDS_PAGINAS", "3")))

# Alineaciones ANTES del saque: la API las publica ~20-60 min antes y el
# análisis las necesita en cuanto existen (el EFE/DTP y los skills leen la
# ficha /fixtures/{id}/ficha, que sirve la tabla `alineaciones` al instante).
# La ficha post-partido (ficha_partido.py) solo baja partidos TERMINADOS, así
# que sin este paso el XI confirmado no llegaba nunca antes del pitazo.
# 1 request por partido (fixtures/lineups), desde XI_VENTANA_PREVIA_MIN antes
# del saque hasta XI_VENTANA_TARDE_MIN después (ligas que publican tarde);
# capturado una vez, no se vuelve a pedir. Donde aún no está publicado, el
# intento queda anotado en xi_intentos y se reintenta cada XI_REINTENTO_MIN —
# no cada ciclo — para no quemar presupuesto en ligas sin cobertura.
XI_VENTANA_PREVIA_MIN = 75
XI_VENTANA_TARDE_MIN = 45
XI_REINTENTO_MIN = 5
TOPE_XI = int(os.environ.get("SAD_LIVE_XI", "4"))  # fixtures por ciclo (0 = apagado)

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
CREATE TABLE IF NOT EXISTS odds_live_consultas (
    league_id INTEGER PRIMARY KEY,
    consultada_en TEXT NOT NULL,
    con_datos INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS xi_intentos (
    fixture_id INTEGER PRIMARY KEY,
    intentada_en TEXT NOT NULL,
    con_datos INTEGER NOT NULL DEFAULT 0
);
"""


def candidatos_por_liga(con: sqlite3.Connection, ligas: "set[int]") -> dict[int, set[int]]:
    """{league_id: {fixture_id, …}} de lo que PUEDE estar en juego ahora según
    NUESTRA base (0 requests): arrancó hace poco y el estado aún no se ha
    actualizado, o ya está marcado en juego. Se limita a `ligas` (las
    importantes): las menores no entran al ciclo en vivo.

    Dos detalles que dejaban partidos fuera del ciclo:
    - `TBD` cuenta como previo, no solo `NS`. En esta DB TBD es un estado real
      y frecuente (toda la maquinaria de "zombis" de diagnostico.py va sobre
      NS/TBD); un partido con hora por confirmar jamás entraba al ciclo.
    - margen HACIA ADELANTE (VENTANA_PREVIA_MIN): si la API adelanta el saque
      o nuestra hora guardada va unos minutos tarde, el partido ya está en
      juego mientras su `date` sigue en el futuro — y el ciclo salía con
      "sin partidos en ventana · 0 requests" sin llegar a preguntar.
    """
    if not ligas:
        return {}
    ahora = datetime.now(timezone.utc)
    desde = (ahora - timedelta(minutes=VENTANA_JUEGO_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    hasta = (ahora + timedelta(minutes=VENTANA_PREVIA_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    marcas = ",".join("?" * len(EN_JUEGO))
    previos_marcas = ",".join("?" * len(PREVIOS))
    ligas_marcas = ",".join("?" * len(ligas))
    por_liga: dict[int, set[int]] = {}
    for fid, lid in con.execute(
            f"""SELECT id, league_id FROM fixtures
                WHERE league_id IN ({ligas_marcas})
                  AND ((status_short IN ({previos_marcas}) AND date BETWEEN ? AND ?)
                       OR status_short IN ({marcas}))
                ORDER BY date""",
            (*sorted(ligas), *PREVIOS, desde, hasta, *EN_JUEGO)):
        por_liga.setdefault(lid, set()).add(fid)
    return por_liga


def fixtures_en_ventana(con: sqlite3.Connection, ligas: "set[int]") -> list[int]:
    """Solo los ids de candidatos_por_liga (el ciclo necesita las dos vistas)."""
    return sorted(fid for fids in candidatos_por_liga(con, ligas).values() for fid in fids)


def fixtures_marcados_en_juego(con: sqlite3.Connection) -> set[int]:
    """Los que sad.db cree que siguen en juego: si ya no aparecen en el feed
    live es que terminaron y hay que cerrarlos (estado + marcador final)."""
    marcas = ",".join("?" * len(EN_JUEGO))
    return {
        fila[0]
        for fila in con.execute(f"SELECT id FROM fixtures WHERE status_short IN ({marcas})", EN_JUEGO)
    }




def ligas_de_vivos(vivos: list) -> dict[int, set[int]]:
    """{league_id: {fixture_id, …}} de lo que está en juego ahora mismo. Una
    request de /odds/live?league= sirve a TODOS los partidos simultáneos de esa
    liga, así que el ciclo se factura por liga y no por partido."""
    por_liga: dict[int, set[int]] = {}
    for item in vivos:
        lid = (item.get("league") or {}).get("id")
        fid = (item.get("fixture") or {}).get("id")
        if lid and fid:
            por_liga.setdefault(lid, set()).add(fid)
    return por_liga


def orden_por_antiguedad(con: sqlite3.Connection, por_liga: dict[int, set[int]]) -> list[int]:
    """Ligas ordenadas por CONSULTA más vieja primero (las nunca consultadas,
    delante). Con tope de ligas por ciclo esto reparte el presupuesto en vez de
    servir siempre a las mismas: ninguna liga se queda sin turno.

    La antigüedad es la de odds_live_consultas (cuándo se le PIDIÓ /odds/live a
    esa liga), no la de la última captura en odds_live. Ordenar por captura era
    un bug (27/07/2026, Guayaquil City–U. Católica en Ecuador - Liga Pro sin
    cuotas en juego): una liga donde la API no devuelve odds live nunca captura
    nada, así que quedaba pegada al frente de la cola PARA SIEMPRE — y con el
    tope de ligas por ciclo, varias así acaparaban todos los cupos y a las
    demás ni se les preguntaba. La ficha decía "sin cobertura de cuotas en vivo
    en esta liga" sin ser verdad: nunca se hizo la request."""
    if not por_liga:
        return []
    marcas = ",".join("?" * len(por_liga))
    ultima = {
        lid: cap
        for lid, cap in con.execute(
            f"SELECT league_id, consultada_en FROM odds_live_consultas "
            f"WHERE league_id IN ({marcas})",
            tuple(sorted(por_liga)))
    }
    return sorted(por_liga, key=lambda lid: (ultima.get(lid, ""), lid))


def fixtures_para_xi(con: sqlite3.Connection, ligas: "set[int]") -> list[int]:
    """Fixtures de las ligas en vivo cuya alineación conviene pedir YA: saque
    entre XI_VENTANA_PREVIA_MIN antes y XI_VENTANA_TARDE_MIN después de ahora
    (previos o ya en juego), sin XI capturado y sin intento reciente. Orden:
    saque más próximo primero — el XI que le falta al análisis de hoy manda."""
    if not ligas or TOPE_XI <= 0:
        return []
    ahora = datetime.now(timezone.utc)
    desde = (ahora - timedelta(minutes=XI_VENTANA_TARDE_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    hasta = (ahora + timedelta(minutes=XI_VENTANA_PREVIA_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    corte_intento = (ahora - timedelta(minutes=XI_REINTENTO_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    estados = PREVIOS + EN_JUEGO
    marcas_e = ",".join("?" * len(estados))
    marcas_l = ",".join("?" * len(ligas))
    return [fid for (fid,) in con.execute(
        f"""SELECT f.id FROM fixtures f
            WHERE f.league_id IN ({marcas_l})
              AND f.status_short IN ({marcas_e})
              AND f.date BETWEEN ? AND ?
              AND NOT EXISTS (SELECT 1 FROM alineaciones a WHERE a.fixture_id = f.id)
              AND NOT EXISTS (SELECT 1 FROM xi_intentos i
                              WHERE i.fixture_id = f.id AND i.intentada_en > ?)
            ORDER BY f.date""",
        (*sorted(ligas), *estados, desde, hasta, corte_intento))]


def capturar_xi(cliente, con: sqlite3.Connection, fixtures: list[int], capturado: str) -> int:
    """Alineaciones prepartido → tabla alineaciones (la misma que la ficha
    post-partido: /fixtures/{id}/ficha las sirve en cuanto existen y el
    análisis puede completarse). 1 request por fixture, tope TOPE_XI por
    ciclo; el intento se anota gane o pierda, para espaciar los reintentos."""
    atendidos = fixtures[:TOPE_XI] if TOPE_XI > 0 else fixtures
    con_xi = 0
    for fid in atendidos:
        if not cliente.quedan():
            break
        data = cliente.get("fixtures/lineups", {"fixture": fid})
        n = guardar_alineaciones(con, fid, (data or {}).get("response", []))
        con.execute(
            "INSERT INTO xi_intentos (fixture_id, intentada_en, con_datos) VALUES (?, ?, ?) "
            "ON CONFLICT(fixture_id) DO UPDATE SET intentada_en=excluded.intentada_en, "
            "con_datos=excluded.con_datos",
            (fid, capturado, 1 if n else 0),
        )
        if n:
            con_xi += 1
    con.commit()
    if atendidos:
        print(f"alineaciones prepartido: {con_xi} de {len(atendidos)} fixtures con XI publicado"
              + (f" · {len(fixtures) - len(atendidos)} esperan al próximo ciclo" if len(fixtures) > len(atendidos) else ""))
    return con_xi


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


def capturar_odds_live(cliente, con: sqlite3.Connection, por_liga: dict,
                       ids_objetivo: set, capturado: str) -> tuple[int, set]:
    """Cuotas en juego de nuestros partidos vivos → odds_live.

    UNA request (o dos, si pagina) por LIGA con partido nuestro en juego, no
    una por partido: /odds/live?league= devuelve todos los simultáneos de esa
    liga. Y nunca sin filtro: el feed global viene paginado a ~10 fixtures y
    las primeras páginas son de cualquier liga del mundo, así que pedir la
    página 1 entera es como no pedir nada para las nuestras.

    `por_liga` NO sale solo del feed de /fixtures?live=: se le suman nuestros
    candidatos locales. Si ese feed se deja un partido (recorte del filtro por
    ligas, hipo de la API, estado que aún no hemos volteado), sus cuotas se
    piden igual — la curva en vivo no puede depender de una segunda llamada.
    Devuelve (valores_guardados, fixtures_con_cuotas).
    """
    if not por_liga or not cliente.quedan():
        return 0, set()
    orden = orden_por_antiguedad(con, por_liga)
    atendidas = orden if TOPE_LIGAS <= 0 else orden[:TOPE_LIGAS]
    aplazadas = orden[len(atendidas):]
    n_odds = 0
    con_feed: set = set()
    consultadas: list[int] = []
    sin_cobertura: list[int] = []
    for lid in atendidas:
        if not cliente.quedan():
            aplazadas.extend(atendidas[atendidas.index(lid):])
            print("  presupuesto agotado: el resto de ligas espera al próximo ciclo")
            break
        filas = cliente.paginado("odds/live", {"league": lid}, tope_paginas=TOPE_PAGINAS)
        consultadas.append(lid)
        antes = len(con_feed)
        for item in filas:
            fid = (item.get("fixture") or {}).get("id")
            if fid in ids_objetivo:
                n_odds += guardar_odds_live(con, item, capturado)
                con_feed.add(fid)
        if len(con_feed) == antes:
            sin_cobertura.append(lid)
        # la rotación va por ESTA marca, no por las capturas: una liga sin
        # cobertura también gastó su turno y pasa al final de la cola
        con.execute(
            "INSERT INTO odds_live_consultas (league_id, consultada_en, con_datos) "
            "VALUES (?, ?, ?) ON CONFLICT(league_id) DO UPDATE SET "
            "consultada_en=excluded.consultada_en, con_datos=excluded.con_datos",
            (lid, capturado, 0 if len(con_feed) == antes else 1),
        )
    con.commit()
    # evidencia en logs: distinguir "no pedimos" de "la casa cerró el mercado"
    susp = con.execute(
        "SELECT COUNT(*) FROM odds_live WHERE captured_at=? AND suspendida=1", (capturado,)
    ).fetchone()[0]
    print(f"odds live: {n_odds} valores ({susp} suspendidos) en {len(con_feed)} fixtures "
          f"· ligas con datos: {len(consultadas) - len(sin_cobertura)}/{len(por_liga)} "
          f"(consultadas {len(consultadas)})")
    if sin_cobertura:
        print(f"  ligas sin odds en el feed live (cobertura de la API o mercado "
              f"cerrado por la casa): {sorted(sin_cobertura)}")
    if aplazadas:
        print(f"  ligas aplazadas al próximo ciclo (tope {TOPE_LIGAS}): {sorted(set(aplazadas))}")
    sin_feed = set(ids_objetivo) - con_feed
    if sin_feed:
        print(f"  fixtures sin cuotas en esta captura: {sorted(sin_feed)}")
    return n_odds, con_feed


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
    preparar_ficha(con)  # fixture_eventos y sus columnas nuevas

    # solo las ligas importantes reciben el ciclo en vivo (las menores —Liga 2,
    # copas nacionales— se ingestan igual en fixtures/histórico/cuotas prepartido)
    vivo = ligas_vivo()
    locales = candidatos_por_liga(con, vivo)
    candidatos = {fid for fids in locales.values() for fid in fids}
    # la ventana del XI arranca ANTES que la de juego: puede haber alineaciones
    # que pedir cuando todavía no hay ningún partido en juego
    xi_pendientes = fixtures_para_xi(con, vivo)
    if not candidatos and not xi_pendientes:
        con.close()
        print("sin partidos en ventana de juego ni alineaciones que pedir · 0 requests")
        return 0

    cliente = Cliente(leer_clave())
    capturado = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

    # el XI primero: es lo que le falta al análisis prepartido y caduca al saque
    if xi_pendientes:
        capturar_xi(cliente, con, xi_pendientes, capturado)
    if not candidatos:
        con.close()
        print(f"sin partidos en ventana de juego · requests usadas: {cliente.usadas}/{cliente.limite}")
        return 0

    # 1 request: marcador/minuto/estado de todo lo vivo en nuestras ligas
    # importantes. Con más de TOPE_LIGAS_LIVE ligas se pide live=all y el
    # filtro lo hacemos aquí abajo: mismo coste y ninguna liga se cae por un
    # recorte silencioso del servidor.
    filtro = ("all" if len(vivo) > TOPE_LIGAS_LIVE
              else "-".join(str(i) for i in sorted(vivo)))
    data = cliente.get("fixtures", {"live": filtro})
    vivos = [
        item for item in (data or {}).get("response", [])
        if item.get("fixture", {}).get("id") in candidatos
        or item.get("league", {}).get("id") in vivo
    ]
    n_fix = guardar_fixtures(con, vivos)
    n_ev = sum(guardar_eventos(con, item) for item in vivos)
    con.commit()
    ids_vivos = {item["fixture"]["id"] for item in vivos if item.get("fixture", {}).get("id")}
    print(f"en juego: {len(ids_vivos)} fixtures nuestros de {len(ligas_de_vivos(vivos))} ligas "
          f"(live={filtro if filtro == 'all' else str(len(vivo)) + ' ligas'}; "
          f"candidatos locales: {len(candidatos)})")

    # universo de cuotas = feed live + nuestros candidatos: si el feed se dejó
    # un partido, sus cuotas se piden igual (una request por liga las cubre)
    por_liga = ligas_de_vivos(vivos)
    for lid, fids in locales.items():
        por_liga.setdefault(lid, set()).update(fids)
    n_odds, _ = capturar_odds_live(con=con, cliente=cliente, por_liga=por_liga,
                                   ids_objetivo=candidatos | ids_vivos, capturado=capturado)

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
