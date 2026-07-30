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
import json
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


def _tope(nombre: str, defecto: int) -> int:
    """Env var numérica que NO puede tumbar el ciclo si viene mal escrita.

    Los topes de abajo son CANTIDADES, pero se llaman SAD_LIVE_ODDS_LIGAS y
    SAD_LIVE_ODDS_FIXTURES: el nombre invita a poner una lista de IDs ahí. Con
    `int()` a pelo, un `SAD_LIVE_ODDS_LIGAS=128,71` reventaba el import y el
    ciclo en vivo moría entero cada minuto, en silencio y sin cuotas de nadie.
    Ahora avisa y sigue con el default. (Las ligas se eligen en LIGAS del
    extractor, y se sacan del ciclo en vivo con SAD_LIGAS_MENORES.)"""
    crudo = os.environ.get(nombre, "").strip()
    if not crudo:
        return defecto
    try:
        return int(crudo)
    except ValueError:
        print(f"{nombre}={crudo!r} no es un número: es una CANTIDAD, no una lista de ligas. "
              f"Sigo con {defecto} (las ligas se configuran en SAD_LIGAS_MENORES / "
              f"SAD_LIGAS_EXTRA).", file=sys.stderr)
        return defecto

# Cuotas en juego: 1 request por LIGA con partido nuestro vivo (todos los
# partidos simultáneos de esa liga vienen en la misma respuesta). Topes para que
# un ciclo que corre cada minuto no se coma el presupuesto del día:
#   SAD_LIVE_ODDS_LIGAS=6   ligas por ciclo (0 = sin tope). Las que no entran no
#                           se pierden: el orden es EN JUEGO primero y luego por
#                           antigüedad de CONSULTA (odds_live_consultas), así
#                           que rotan y en el ciclo siguiente van primeras. OJO:
#                           no por antigüedad de captura — ver orden_por_antiguedad.
#   SAD_LIVE_ODDS_PAGINAS=3 páginas por liga (~10 fixtures por página).
# Estuvo en 12 unas horas, subido con la premisa de que el plan diario no se
# tocaba. Los logs del 29/07/2026 la desmintieron: 7496/7495 usadas y el
# respaldo también a cero, con el ciclo en vivo haciendo CERO requests y
# TODO parado — incluidas las copas que sí funcionaban. Un ciclo por minuto
# con 12 ligas (y hasta 3 páginas cada una) puede pedir >30 requests/minuto:
# se come un plan de 7.500 en una tarde. Vuelve a 6, y ahora con freno propio
# (cupo_del_ciclo) para que no pueda vaciar el plan aunque se suba a mano.
TOPE_LIGAS = _tope("SAD_LIVE_ODDS_LIGAS", 6)
TOPE_PAGINAS = max(1, _tope("SAD_LIVE_ODDS_PAGINAS", 3))
# Rescate por partido: /odds/live?fixture= cuando la ronda de la liga no trajo
# un partido que SÍ se está jugando. La vía por liga es la barata (1 request
# cubre todos sus simultáneos) y sigue siendo la primera, pero cuando falla
# —feed vacío, filtro ?league= que no filtra, request caída— dejaba al partido
# sin curva y a la pantalla culpando a la cobertura de la API. Preguntar por el
# fixture no depende de nada de eso. 0 = apagado.
TOPE_FIXTURES = _tope("SAD_LIVE_ODDS_FIXTURES", 4)

# PARTIDOS VIP: "este partido lo quiero sí o sí, aunque cueste". Se marcan
# desde la app (POST /fixtures/{id}/vip → .vip_fixtures.json en la raíz de
# datos) o por liga con SAD_EMERGENCIA_LIGAS="13,11". Dos efectos:
# 1. Con el plan sano, el VIP entra al rescate por fixture aunque su liga sea
#    menor: la marca manda sobre LIGAS_MENORES para ESE partido.
# 2. Con el plan (y el respaldo) agotados, el modo emergencia les mantiene
#    marcador y cuotas con la clave SAD_EMERGENCIA_KEY — la que puede facturar
#    excedente — sin gastar un centavo en nada que no esté marcado.
# Las marcas caducan solas (VIP_CADUCIDAD_H): nadie paga por un olvido.
VIP_PATH = ".vip_fixtures.json"
VIP_CADUCIDAD_H = 8
LIGAS_EMERGENCIA = {
    int(x) for x in os.environ.get("SAD_EMERGENCIA_LIGAS", "").split(",") if x.strip().isdigit()
}

# FRENO DE PRESUPUESTO. El ciclo corre cada minuto y, sin freno propio, se come
# el plan del día y deja sin datos a TODO lo demás: la ingesta diaria, el
# refresco de cuotas prepartido y el propio marcador en vivo. Es exactamente lo
# que pasó el 29/07/2026 (7496/7495 y el respaldo agotado: cero requests, cero
# cuotas, cero marcador — y las copas que funcionaban se pararon a mitad de
# partido). La reserva es lo que el ciclo en vivo NO puede tocar.
RESERVA_VIVO = _tope("SAD_LIVE_RESERVA", 1500)
# Requests que se le suponen a una liga por ronda (1 request + su paginado):
# el cupo se calcula con esto para degradar suave en vez de chocar contra la pared.
COSTE_LIGA = 3


def cupo_del_ciclo(cliente, tope: int) -> int:
    """Cuántas ligas puede pedir ESTE ciclo sin comerse la reserva del día.

    Con margen de sobra devuelve el tope entero; según se acerca a la reserva
    va bajando, y al llegar sale 0: el ciclo sigue pidiendo marcador y minuto
    (1 request, lo más barato y lo más valioso) pero deja de pedir cuotas.
    Así el plan nunca se agota por el ciclo en vivo."""
    if tope <= 0:  # 0 = sin tope explícito: igual se respeta la reserva
        tope = 10**6
    margen = (cliente.limite - cliente.usadas) - RESERVA_VIVO
    if margen <= 0:
        return 0
    return max(0, min(tope, margen // COSTE_LIGA))

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
# La formación PUEDE cambiar entre la publicación y el saque (un XI temprano o
# probable que el DT corrige). Un XI capturado más de XI_CAPTURA_VIEJA_MIN
# antes del saque se refresca UNA vez al entrar en los últimos
# XI_REFRESCO_ANTES_MIN minutos: tras ese refresco su intento queda reciente y
# la condición se apaga sola (1 request extra por partido, como mucho).
XI_CAPTURA_VIEJA_MIN = 30
XI_REFRESCO_ANTES_MIN = 15

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
-- Una fila por liga con la ÚLTIMA ronda de /odds/live. `con_datos` era un
-- booleano que mezclaba cuatro cosas distintas — feed vacío, feed que no traía
-- nuestro partido, request fallida y presupuesto agotado — y la pantalla
-- acabó afirmando "la API no cubre esta liga" en los cuatro casos. `estado`
-- las separa; `items`/`nuestros`/`ajenos` dejan la evidencia cruda.
CREATE TABLE IF NOT EXISTS odds_live_consultas (
    league_id INTEGER PRIMARY KEY,
    consultada_en TEXT NOT NULL,
    con_datos INTEGER NOT NULL DEFAULT 0,
    estado TEXT,      -- ok | vacia | ajena | fallo
    items INTEGER,    -- cuántos items devolvió el feed de la liga
    nuestros INTEGER, -- cuántos de esos eran partidos que seguimos
    ajenos INTEGER    -- cuántos venían de OTRA liga (el filtro no filtró)
);
CREATE TABLE IF NOT EXISTS xi_intentos (
    fixture_id INTEGER PRIMARY KEY,
    intentada_en TEXT NOT NULL,
    con_datos INTEGER NOT NULL DEFAULT 0
);
"""


def fixtures_vip(con: sqlite3.Connection, ruta: str = VIP_PATH) -> set[int]:
    """Fixtures marcados VIP que AHORA están en ventana de juego (0 requests):
    las marcas de la app (caducadas fuera) + los partidos de las ligas de
    SAD_EMERGENCIA_LIGAS. Sin filtro de liga importante/menor: la marca es
    'este partido sí o sí' y manda sobre esa clasificación."""
    marcados: set[int] = set()
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        limite = datetime.now(timezone.utc) - timedelta(hours=VIP_CADUCIDAD_H)
        for fid, marcado_en in (datos.items() if isinstance(datos, dict) else []):
            try:
                cuando = datetime.strptime(str(marcado_en)[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                if cuando >= limite:
                    marcados.add(int(fid))
            except (ValueError, TypeError):
                continue
    except (OSError, ValueError):
        pass  # sin archivo o corrupto: sin marcas manuales
    ahora = datetime.now(timezone.utc)
    desde = (ahora - timedelta(minutes=VENTANA_JUEGO_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    hasta = (ahora + timedelta(minutes=VENTANA_PREVIA_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    filtros, args = [], []
    if marcados:
        filtros.append(f"id IN ({','.join('?' * len(marcados))})")
        args.extend(sorted(marcados))
    if LIGAS_EMERGENCIA:
        filtros.append(f"league_id IN ({','.join('?' * len(LIGAS_EMERGENCIA))})")
        args.extend(sorted(LIGAS_EMERGENCIA))
    if not filtros:
        return set()
    marcas = ",".join("?" * len(EN_JUEGO))
    previos = ",".join("?" * len(PREVIOS))
    return {
        fila[0] for fila in con.execute(
            f"""SELECT id FROM fixtures WHERE ({' OR '.join(filtros)})
                AND ((status_short IN ({previos}) AND date BETWEEN ? AND ?)
                     OR status_short IN ({marcas}))""",
            (*args, *PREVIOS, desde, hasta, *EN_JUEGO))
    }


def capturar_emergencia(cliente, con: sqlite3.Connection, vip_sin: list[int],
                        capturado: str) -> int:
    """Marcador + cuotas de los VIP que el flujo normal no pudo servir, con la
    clave de EMERGENCIA (la que factura excedente). 1 request de /fixtures?ids=
    para el marcador de todos + 1 de /odds/live?fixture= por partido. Cada
    request es dinero: solo VIP, solo lo mínimo, y el tope diario manda."""
    if not vip_sin or not cliente.emergencia_disponible(2):
        return 0
    print(f"modo EMERGENCIA: {len(vip_sin)} VIP sin servir con el plan agotado {sorted(vip_sin)}")
    data = cliente.get_emergencia("fixtures", {"ids": "-".join(map(str, sorted(vip_sin)[:20]))})
    items = (data or {}).get("response", [])
    guardar_fixtures(con, items)
    for item in items:
        guardar_eventos(con, item)
    # cuotas SOLO para los que el marcador recién pedido confirma en juego: un
    # VIP que aún no arranca cuesta 1 request por ciclo (marcador), no 2
    jugando = {
        (item.get("fixture") or {}).get("id")
        for item in items
        if ((item.get("fixture") or {}).get("status") or {}).get("short") in EN_JUEGO
    }
    n_odds = 0
    for fid in sorted(set(vip_sin) & jugando):
        if not cliente.emergencia_disponible():
            print(f"  tope de emergencia alcanzado ({cliente.tope_emergencia}/día): el resto espera")
            break
        data = cliente.get_emergencia("odds/live", {"fixture": fid})
        for item in (data or {}).get("response", []):
            if (item.get("fixture") or {}).get("id") == fid:
                n_odds += guardar_odds_live(con, item, capturado)
    con.commit()
    print(f"  emergencia: {n_odds} cuotas de {len(set(vip_sin) & jugando)} en juego "
          f"· usadas {cliente.usadas_emergencia}/{cliente.tope_emergencia} hoy")
    return n_odds


def preparar_consultas(con: sqlite3.Connection) -> None:
    """Columnas nuevas de odds_live_consultas en DBs que ya existen (la de
    producción se creó con solo `con_datos`)."""
    existentes = {f[1] for f in con.execute("PRAGMA table_info(odds_live_consultas)")}
    for col, tipo in (("estado", "TEXT"), ("items", "INTEGER"),
                      ("nuestros", "INTEGER"), ("ajenos", "INTEGER")):
        if col not in existentes:
            con.execute(f"ALTER TABLE odds_live_consultas ADD COLUMN {col} {tipo}")
    con.commit()


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




def ligas_marcadas_en_juego(con: sqlite3.Connection, ligas: "set[int]") -> set[int]:
    """Ligas que NUESTRA base ya tiene con un partido en juego (0 requests).

    Se suman a las del feed live para la prioridad de la cola: si el feed tuvo
    un hipo y no devolvió el partido, la liga seguiría teniendo el partido
    corriendo — mandarla al fondo por eso sería reabrir la misma puerta que
    cierra `en_juego`. Un estado EN_JUEGO en fixtures no se pone solo: lo
    escribió un ciclo anterior desde el propio feed."""
    if not ligas:
        return set()
    marcas = ",".join("?" * len(EN_JUEGO))
    ligas_marcas = ",".join("?" * len(ligas))
    return {
        fila[0]
        for fila in con.execute(
            f"SELECT DISTINCT league_id FROM fixtures "
            f"WHERE league_id IN ({ligas_marcas}) AND status_short IN ({marcas})",
            (*sorted(ligas), *EN_JUEGO))
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


def orden_por_antiguedad(con: sqlite3.Connection, por_liga: dict[int, set[int]],
                         en_juego: "set[int] | None" = None) -> list[int]:
    """Ligas ordenadas para el tope por ciclo: primero las que tienen un partido
    EN JUEGO confirmado, y dentro de cada grupo por CONSULTA más vieja (las
    nunca consultadas, delante). Así se reparte el presupuesto sin que una liga
    con partido corriendo pierda el cupo.

    La antigüedad es la de odds_live_consultas (cuándo se le PIDIÓ /odds/live a
    esa liga), no la de la última captura en odds_live. Ordenar por captura era
    un bug (27/07/2026, Guayaquil City–U. Católica en Ecuador - Liga Pro sin
    cuotas en juego): una liga donde la API no devuelve odds live nunca captura
    nada, así que quedaba pegada al frente de la cola PARA SIEMPRE — y con el
    tope de ligas por ciclo, varias así acaparaban todos los cupos y a las
    demás ni se les preguntaba. La ficha decía "sin cobertura de cuotas en vivo
    en esta liga" sin ser verdad: nunca se hizo la request.

    `en_juego` cierra la puerta hermana (29/07/2026, Gimnasia LP–River Plate en
    Argentina - Liga Profesional en el minuto 3 sin cuotas): `por_liga` mezcla
    las ligas del feed live con las que solo tienen un NS/TBD en una ventana de
    3h45, y la cola las trataba igual. Una liga sin nadie jugando le ganaba el
    turno a otra con el partido en marcha — y el partido termina, la ventana
    no. Sin el set (llamada vieja) el orden es el de antes."""
    if not por_liga:
        return []
    en_juego = en_juego or set()
    marcas = ",".join("?" * len(por_liga))
    ultima = {
        lid: cap
        for lid, cap in con.execute(
            f"SELECT league_id, consultada_en FROM odds_live_consultas "
            f"WHERE league_id IN ({marcas})",
            tuple(sorted(por_liga)))
    }
    return sorted(por_liga, key=lambda lid: (lid not in en_juego, ultima.get(lid, ""), lid))


def fixtures_para_xi(con: sqlite3.Connection, ligas: "set[int]") -> list[int]:
    """Fixtures de las ligas en vivo cuya alineación conviene pedir YA. Dos
    casos, orden por saque más próximo primero:
    1. SIN XI capturado, con saque entre XI_VENTANA_PREVIA_MIN antes y
       XI_VENTANA_TARDE_MIN después de ahora (previos o ya en juego), sin
       intento reciente (XI_REINTENTO_MIN).
    2. CON XI, pero capturado temprano (> XI_CAPTURA_VIEJA_MIN antes del
       saque): un refresco único al entrar en los últimos
       XI_REFRESCO_ANTES_MIN minutos, por si la formación cambió — tras ese
       intento la condición deja de cumplirse sola."""
    if not ligas or TOPE_XI <= 0:
        return []
    ahora = datetime.now(timezone.utc)
    desde = (ahora - timedelta(minutes=XI_VENTANA_TARDE_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    hasta = (ahora + timedelta(minutes=XI_VENTANA_PREVIA_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    hasta_refresco = (ahora + timedelta(minutes=XI_REFRESCO_ANTES_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    corte_intento = (ahora - timedelta(minutes=XI_REINTENTO_MIN)).strftime("%Y-%m-%d %H:%M:%S")
    estados = PREVIOS + EN_JUEGO
    marcas_e = ",".join("?" * len(estados))
    marcas_l = ",".join("?" * len(ligas))
    return [fid for fid, _ in con.execute(
        f"""SELECT f.id, f.date FROM fixtures f
            WHERE f.league_id IN ({marcas_l})
              AND f.status_short IN ({marcas_e})
              AND f.date BETWEEN ? AND ?
              AND NOT EXISTS (SELECT 1 FROM alineaciones a WHERE a.fixture_id = f.id)
              AND NOT EXISTS (SELECT 1 FROM xi_intentos i
                              WHERE i.fixture_id = f.id AND i.intentada_en > ?)
            UNION
            SELECT f.id, f.date FROM fixtures f
            WHERE f.league_id IN ({marcas_l})
              AND f.status_short IN ({marcas_e})
              AND f.date BETWEEN ? AND ?
              AND EXISTS (SELECT 1 FROM alineaciones a WHERE a.fixture_id = f.id)
              AND COALESCE((SELECT MAX(i.intentada_en) FROM xi_intentos i
                            WHERE i.fixture_id = f.id), '')
                  < datetime(f.date, '-{XI_CAPTURA_VIEJA_MIN} minutes')
            ORDER BY 2""",
        (*sorted(ligas), *estados, desde, hasta, corte_intento,
         *sorted(ligas), *estados, desde, hasta_refresco))]


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
        respuesta = (data or {}).get("response", [])
        ya_tenia = bool(con.execute(
            "SELECT 1 FROM alineaciones WHERE fixture_id=? LIMIT 1", (fid,)).fetchone())
        # una respuesta vacía NO pisa un XI ya capturado: guardar_alineaciones
        # borra antes de insertar, y el refresco cerca del saque no puede dejar
        # la ficha peor de lo que estaba por un hipo de la API
        n = guardar_alineaciones(con, fid, respuesta) if respuesta else 0
        con.execute(
            "INSERT INTO xi_intentos (fixture_id, intentada_en, con_datos) VALUES (?, ?, ?) "
            "ON CONFLICT(fixture_id) DO UPDATE SET intentada_en=excluded.intentada_en, "
            "con_datos=excluded.con_datos",
            (fid, capturado, 1 if (n or ya_tenia) else 0),
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
                       ids_objetivo: set, capturado: str,
                       en_juego: "set[int] | None" = None,
                       ids_en_juego: "set[int] | None" = None) -> tuple[int, set]:
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

    `en_juego` (ligas con partido confirmado en el feed live) manda en el orden:
    con tope por ciclo, primero se sirve a quien tiene el partido corriendo.

    `ids_en_juego` (FIXTURES confirmados en juego) son los que, si su ronda de
    liga no los trajo, se rescatan uno a uno con /odds/live?fixture=.
    Devuelve (valores_guardados, fixtures_con_cuotas).
    """
    if not por_liga or not cliente.quedan():
        return 0, set()
    orden = orden_por_antiguedad(con, por_liga, en_juego)
    cupo = cupo_del_ciclo(cliente, TOPE_LIGAS)
    if cupo <= 0:
        print(f"  cuotas en juego EN PAUSA: quedan {cliente.limite - cliente.usadas} requests y "
              f"la reserva del día es {RESERVA_VIVO} (SAD_LIVE_RESERVA). El marcador sigue; "
              f"las cuotas vuelven cuando el plan resetee")
        return 0, set()
    if cupo < min(len(orden), TOPE_LIGAS if TOPE_LIGAS > 0 else len(orden)):
        print(f"  presupuesto justo: este ciclo pide {cupo} ligas en vez de {TOPE_LIGAS} "
              f"(quedan {cliente.limite - cliente.usadas}, reserva {RESERVA_VIVO})")
    atendidas = orden[:cupo]
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
        fallos_antes = cliente.fallos
        filas = cliente.paginado("odds/live", {"league": lid}, tope_paginas=TOPE_PAGINAS)
        consultadas.append(lid)
        antes = len(con_feed)
        ajenos = 0
        for item in filas:
            fid = (item.get("fixture") or {}).get("id")
            if (item.get("league") or {}).get("id") not in (None, lid):
                ajenos += 1  # el filtro ?league= no filtró: feed de otra liga
            if fid in ids_objetivo:
                n_odds += guardar_odds_live(con, item, capturado)
                con_feed.add(fid)
        nuestros = len(con_feed) - antes
        # POR QUÉ no hubo cuotas: cuatro causas que el booleano viejo mezclaba
        # en una sola, y la pantalla acababa culpando a la cobertura de la API
        if cliente.fallos > fallos_antes:
            estado = "fallo"      # red, HTTP, errors de la API o presupuesto
        elif not filas:
            estado = "vacia"      # la liga existe y el feed vino sin nada
        elif not nuestros:
            estado = "ajena"      # trajo partidos, pero ninguno de los nuestros
        else:
            estado = "ok"
        if estado != "ok":
            sin_cobertura.append(lid)
        if estado == "ajena":
            ligas_feed = sorted({(it.get("league") or {}).get("id") for it in filas} - {None})
            print(f"  liga {lid}: el feed trajo {len(filas)} partidos pero ninguno nuestro "
                  f"(ligas en la respuesta: {ligas_feed[:6]}) — si ahí no está {lid}, el "
                  f"filtro ?league= no está filtrando")
        elif estado == "fallo":
            print(f"  liga {lid}: la consulta FALLÓ (no es falta de cobertura); reintenta sola")
        # la rotación va por ESTA marca, no por las capturas: una liga sin
        # cobertura también gastó su turno y pasa al final de la cola
        con.execute(
            "INSERT INTO odds_live_consultas (league_id, consultada_en, con_datos, estado, "
            "items, nuestros, ajenos) VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(league_id) DO UPDATE SET consultada_en=excluded.consultada_en, "
            "con_datos=excluded.con_datos, estado=excluded.estado, items=excluded.items, "
            "nuestros=excluded.nuestros, ajenos=excluded.ajenos",
            (lid, capturado, 1 if estado == "ok" else 0, estado, len(filas), nuestros, ajenos),
        )
    con.commit()

    # RESCATE POR PARTIDO: lo de arriba es la vía barata (1 request cubre toda
    # la liga), pero cuando falla nos deja sin curva de un partido que SÍ se
    # está jugando. /odds/live?fixture= pregunta por él directamente, sin
    # depender de que el filtro por liga se porte bien. Solo para partidos
    # confirmados en juego que la ronda de su liga no trajo, y con tope propio.
    faltan = sorted((ids_en_juego or set()) - con_feed)
    # el rescate también gasta: se le aplica la misma reserva que a las ligas
    # (si no, el freno de arriba sería un colador)
    if faltan and TOPE_FIXTURES > 0 and cupo_del_ciclo(cliente, TOPE_FIXTURES) > 0:
        for fid in faltan[:TOPE_FIXTURES]:
            if not cliente.quedan() or cupo_del_ciclo(cliente, TOPE_FIXTURES) <= 0:
                break
            filas = cliente.paginado("odds/live", {"fixture": fid}, tope_paginas=1)
            for item in filas:
                if (item.get("fixture") or {}).get("id") == fid:
                    n_odds += guardar_odds_live(con, item, capturado)
                    con_feed.add(fid)
        rescatados = sorted(set(faltan[:TOPE_FIXTURES]) & con_feed)
        print(f"  rescate por fixture: {len(rescatados)} de {len(faltan[:TOPE_FIXTURES])} "
              f"pedidos trajeron cuotas {rescatados}")
        if len(faltan) > TOPE_FIXTURES:
            print(f"  (quedaron {len(faltan) - TOPE_FIXTURES} para el próximo ciclo; "
                  f"tope SAD_LIVE_ODDS_FIXTURES={TOPE_FIXTURES})")
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
        # aplazar una liga SIN partido en juego es gratis; aplazar una CON
        # partido corriendo es perder curva que no vuelve: se avisa aparte
        vivas = sorted(set(aplazadas) & (en_juego or set()))
        if vivas:
            print(f"  ATENCIÓN: {len(vivas)} de ellas tienen partido EN JUEGO {vivas} — "
                  f"sube SAD_LIVE_ODDS_LIGAS (0 = sin tope) o baja las que no te interesen "
                  f"a SAD_LIGAS_MENORES")
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
    preparar_consultas(con)  # columnas nuevas en DBs ya creadas
    preparar_ficha(con)  # fixture_eventos y sus columnas nuevas

    # solo las ligas importantes reciben el ciclo en vivo (las menores —Liga 2,
    # copas nacionales— se ingestan igual en fixtures/histórico/cuotas prepartido)
    vivo = ligas_vivo()
    locales = candidatos_por_liga(con, vivo)
    candidatos = {fid for fids in locales.values() for fid in fids}
    # la ventana del XI arranca ANTES que la de juego: puede haber alineaciones
    # que pedir cuando todavía no hay ningún partido en juego
    xi_pendientes = fixtures_para_xi(con, vivo)
    # los VIP entran aunque su liga sea menor: la marca manda para ESE partido
    vip = fixtures_vip(con)
    if not candidatos and not xi_pendientes and not vip:
        con.close()
        print("sin partidos en ventana de juego ni alineaciones que pedir · 0 requests")
        return 0

    cliente = Cliente(leer_clave())
    capturado = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

    # el XI primero: es lo que le falta al análisis prepartido y caduca al saque
    if xi_pendientes:
        capturar_xi(cliente, con, xi_pendientes, capturado)
    if not candidatos and not vip:
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
        or item.get("fixture", {}).get("id") in vip
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
    # un partido, sus cuotas se piden igual (una request por liga las cubre).
    # Las del feed son las que TIENEN partido corriendo: con tope por ciclo van
    # primeras (las locales pueden ser solo un NS dentro de la ventana).
    por_liga = ligas_de_vivos(vivos)
    # ANTES de sumarle los candidatos locales (que pueden ser un simple NS en
    # ventana), más las que nuestra base ya tiene jugando por si el feed falló
    en_juego_ligas = set(por_liga) | ligas_marcadas_en_juego(con, vivo)
    for lid, fids in locales.items():
        por_liga.setdefault(lid, set()).update(fids)
    # los fixtures que de verdad se están jugando (feed + lo que nuestra base
    # ya tiene marcado): si su ronda de liga no los trae, se rescatan uno a uno.
    # Los VIP entran aquí aunque su liga sea menor: el rescate por fixture les
    # da cuotas con el presupuesto normal mientras lo haya.
    ids_en_juego = ids_vivos | (fixtures_marcados_en_juego(con) & (candidatos | vip))
    n_odds, con_feed = capturar_odds_live(con=con, cliente=cliente, por_liga=por_liga,
                                          ids_objetivo=candidatos | ids_vivos | vip,
                                          capturado=capturado,
                                          en_juego=en_juego_ligas, ids_en_juego=ids_en_juego)

    # MODO EMERGENCIA: VIP en juego que el flujo normal no pudo servir porque
    # el plan (y el respaldo) no dan más — la clave de emergencia les mantiene
    # marcador y cuotas. Solo se dispara con el presupuesto normal muerto: si
    # hay plan, el rescate de arriba ya lo intentó gratis.
    # (vip entero, no solo los "en juego" según la DB: con el plan muerto el
    # estado local puede estar viejo — el marcador de emergencia lo actualiza
    # y las cuotas solo se pagan para los confirmados jugando)
    vip_sin = sorted(vip - con_feed)
    if vip_sin and not cliente.quedan(2):
        n_odds += capturar_emergencia(cliente, con, vip_sin, capturado)

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
          f"· purgadas: {borradas} · requests usadas: {cliente.usadas}/{cliente.limite} "
          f"· consumo del día: {cliente.resumen()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
