"""Ficha de partido: alineaciones, eventos y estadísticas — fase A del DTP.

Por qué existe (docs/efe-dtp/DTP_DISENO.md §2): tres de los seis módulos del
DTP no tienen materia prima sin esto.

- **M1/M6** necesitan el XI y la formación del partido ANTERIOR para leer
  "cambios vs anterior" y rotación. Hoy el XI se pide en el momento del EFE y
  se guarda como texto en la despensa: no hay histórico ni estructura.
- **M2** necesita la posición de cada titular EN EL CAMPO — el `grid`
  ("fila:columna") de /fixtures/lineups. Sin él, un "duelo por carril
  izquierdo" sería inventado.
- **M4** necesita los goles del partido anterior con minuto, autor y
  asistente. `fixture_eventos` solo tenía lo que el ciclo EN VIVO vio en
  directo: un partido no seguido minuto a minuto no tenía ni un gol.

Alcance deliberado: SOLO los partidos ya terminados de los equipos con un
fixture NS próximo, y solo los últimos N (default 3). Para la cadena del DTP
basta el inmediatamente anterior; los otros dos dan el contraste de M1/M6.
NO hay barrido histórico: ingestar fichas de temporadas pasadas serían decenas
de miles de requests para un dato que el DTP solo mira del partido anterior.

Costo: 3 requests por partido (lineups + events + statistics). Un partido de
la jornada = 2 equipos × 1 anterior × 3 = 6 requests.

    python -m backend.ingesta.ficha_partido               # NS en <= 3 días
    python -m backend.ingesta.ficha_partido --dias 7 --ultimos 5
    python -m backend.ingesta.ficha_partido --fixture 1234567
    python -m backend.ingesta.ficha_partido --estado      # qué hay, 0 requests
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

from backend.ingesta.extractor import LIGAS, LIGAS_RUIDO, Cliente, leer_clave, reserva_del_dia

DIAS_NS_DEFAULT = 3
ULTIMOS_DEFAULT = int(os.environ.get("SAD_FICHA_PARTIDOS", "3"))
TERMINADOS = ("FT", "AET", "PEN")

# Cobertura APRENDIDA por liga (24/09/2026: 2.959 de 6.651 fichas sin
# alineaciones; seis ligas no dieron un once NUNCA en 50-100 partidos, y cada
# partido nuevo de esas ligas seguía pagando las 3 requests). Si una liga lleva
# >= COBERTURA_MIN fichas selladas y NINGUNA trajo ese endpoint, se deja de
# pedir. Una de cada COBERTURA_SONDA fichas se pide entera igual: si la liga
# empieza a dar alineaciones, la sonda lo ve y la regla se levanta sola.
COBERTURA_MIN = int(os.environ.get("SAD_FICHA_COBERTURA_MIN", "10"))
COBERTURA_SONDA = int(os.environ.get("SAD_FICHA_SONDA", "20"))
ENDPOINTS = ("alineaciones", "eventos", "stats")

DDL = """
CREATE TABLE IF NOT EXISTS alineaciones (
    fixture_id INTEGER NOT NULL,
    team_id    INTEGER NOT NULL,
    formacion  TEXT,
    entrenador TEXT,
    player_id  INTEGER NOT NULL,
    jugador    TEXT,
    numero     INTEGER,
    posicion   TEXT,          -- G|D|M|F según la API
    grid       TEXT,          -- "fila:columna" — el carril de M2
    titular    INTEGER NOT NULL,
    PRIMARY KEY (fixture_id, team_id, player_id)
);
CREATE INDEX IF NOT EXISTS idx_alineaciones_fixture ON alineaciones(fixture_id);

CREATE TABLE IF NOT EXISTS fixture_stats (
    fixture_id INTEGER NOT NULL,
    team_id    INTEGER NOT NULL,
    clave      TEXT NOT NULL,
    valor      TEXT,
    PRIMARY KEY (fixture_id, team_id, clave)
);

-- sello por fixture: sin esto, un partido de una liga SIN cobertura de
-- alineaciones se volvería a pedir en cada corrida, para siempre
CREATE TABLE IF NOT EXISTS fichas_meta (
    fixture_id INTEGER PRIMARY KEY,
    capturado_en TEXT NOT NULL,
    alineaciones INTEGER DEFAULT 0,
    eventos INTEGER DEFAULT 0,
    stats INTEGER DEFAULT 0
);

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

# columnas que fixture_eventos NO tenía cuando la creó el ciclo en vivo: el
# minuto añadido y el asistente son de M4 (disparador → secuencia → definición)
COLUMNAS_EVENTOS = {
    "extra": "INTEGER",
    "jugador_id": "INTEGER",
    "asistente": "TEXT",
    "asistente_id": "INTEGER",
}


def preparar_tablas(con: sqlite3.Connection) -> None:
    """DDL + migración de fixture_eventos. Idempotente: se puede llamar en
    cada arranque (lo hacen la ingesta y el ciclo en vivo)."""
    con.executescript(DDL)
    existentes = {f[1] for f in con.execute("PRAGMA table_info(fixture_eventos)")}
    for col, tipo in COLUMNAS_EVENTOS.items():
        if col not in existentes:
            con.execute(f"ALTER TABLE fixture_eventos ADD COLUMN {col} {tipo}")
    retagear_tandas(con)
    con.commit()


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# ── guardado (compartido con el ciclo en vivo) ──────────────────────────────

# LA TANDA DE PENALES NO SON GOLES. API-Football manda cada disparo de la
# definición como un evento type=Goal / detail=Penalty (o Missed Penalty) con
# elapsed=120 y `extra` creciente, y lo marca solo en `comments`. Guardado a
# pelo, un Santa Fe–River terminaba con 24 «goles» entre el 121' y el 142':
# el veredicto los contaba en la ventana del TDE y la ficha se los daba al DTP
# como si fueran juego. Se guardan con tipo `Shootout`: siguen ahí para quien
# los quiera, pero ningún lector que pida `tipo='Goal'` los ve.
TIPO_TANDA = "Shootout"
MINUTO_FIN_ALARGUE = 120
MINIMO_TANDA = 3  # tres penales «después del 120» no son juego: son la definición


def _es_tanda(ev: dict) -> bool:
    return "shootout" in str(ev.get("comments") or "").lower()


def _tanda_por_forma(eventos: list[dict]) -> set[int]:
    """Índices de los penales que SON tanda aunque la API no lo diga en
    `comments` (a veces viene null): penales con elapsed=120 y `extra`, y al
    menos MINIMO_TANDA de ellos en el mismo partido. Un penal real al 120+2 en
    el alargue existe, pero no vienen tres."""
    idx = []
    for i, ev in enumerate(eventos):
        t = ev.get("time") or {}
        if (str(ev.get("type") or "").lower() == "goal"
                and "penalty" in str(ev.get("detail") or "").lower()
                and _i(t.get("elapsed")) == MINUTO_FIN_ALARGUE and (_i(t.get("extra")) or 0) >= 1):
            idx.append(i)
    return set(idx) if len(idx) >= MINIMO_TANDA else set()


def retagear_tandas(con: sqlite3.Connection) -> int:
    """Lo ya ingestado como gol y que era tanda pasa a `Shootout`. Idempotente
    y sin red: se corre en preparar_tablas, así que el ciclo en vivo lo aplica
    solo en su próxima vuelta."""
    filas = con.execute(
        "SELECT fixture_id, COUNT(*) AS n FROM fixture_eventos WHERE tipo='Goal' "
        "AND lower(detalle) LIKE '%penalty%' AND extra >= 1 AND minuto - extra = ? "
        "GROUP BY fixture_id HAVING n >= ?", (MINUTO_FIN_ALARGUE, MINIMO_TANDA)).fetchall()
    n = 0
    for fid, _ in filas:
        cur = con.execute(
            "UPDATE fixture_eventos SET tipo=? WHERE fixture_id=? AND tipo='Goal' "
            "AND lower(detalle) LIKE '%penalty%' AND extra >= 1 AND minuto - extra = ?",
            (TIPO_TANDA, fid, MINUTO_FIN_ALARGUE))
        n += cur.rowcount
    return n


def guardar_eventos(con: sqlite3.Connection, item: dict) -> int:
    """Eventos de un item de /fixtures?live=, /fixtures?ids= o /fixtures/events.
    El feed devuelve SIEMPRE la lista completa, así que se reemplaza entera
    (idempotente). Acepta tanto el envoltorio de fixtures ({fixture:…,
    events:[…]}) como la respuesta pelada de /fixtures/events."""
    if "events" in item:
        fid = (item.get("fixture") or {}).get("id")
        eventos = item.get("events") or []
    else:  # {"fixture_id": N, "eventos": [...]}
        fid = item.get("fixture_id")
        eventos = item.get("eventos") or []
    if not fid or not eventos:
        return 0
    con.execute("DELETE FROM fixture_eventos WHERE fixture_id=?", (fid,))
    n = 0
    tanda_forma = _tanda_por_forma(eventos)
    for i, ev in enumerate(eventos):
        t = ev.get("time") or {}
        extra = _i(t.get("extra")) or 0
        minuto = (_i(t.get("elapsed")) or 0) + extra
        jug = ev.get("player") or {}
        asi = ev.get("assist") or {}
        tipo = TIPO_TANDA if (_es_tanda(ev) or i in tanda_forma) else ev.get("type")
        con.execute(
            "INSERT INTO fixture_eventos (fixture_id, minuto, extra, tipo, detalle, "
            "equipo_id, jugador, jugador_id, asistente, asistente_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (fid, minuto, extra, tipo, ev.get("detail"),
             (ev.get("team") or {}).get("id"), jug.get("name"), _i(jug.get("id")),
             asi.get("name"), _i(asi.get("id"))),
        )
        n += 1
    return n


def guardar_alineaciones(con: sqlite3.Connection, fixture_id: int, respuesta: list) -> int:
    """Un item por equipo: {team, coach, formation, startXI[], substitutes[]}.
    Se reemplaza entero: la alineación de un partido no cambia, pero un XI
    probable puede volverse oficial."""
    con.execute("DELETE FROM alineaciones WHERE fixture_id=?", (fixture_id,))
    n = 0
    for lado in respuesta:
        tid = (lado.get("team") or {}).get("id")
        if not tid:
            continue
        formacion = lado.get("formation")
        dt = (lado.get("coach") or {}).get("name")
        for titular, lista in ((1, lado.get("startXI") or []), (0, lado.get("substitutes") or [])):
            for it in lista:
                p = it.get("player") or {}
                pid = _i(p.get("id"))
                if pid is None:
                    continue  # sin id no hay clave: la API a veces manda null
                con.execute(
                    "INSERT OR REPLACE INTO alineaciones (fixture_id, team_id, formacion, "
                    "entrenador, player_id, jugador, numero, posicion, grid, titular) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (fixture_id, tid, formacion, dt, pid, p.get("name"),
                     _i(p.get("number")), p.get("pos"), p.get("grid"), titular),
                )
                n += 1
    return n


def guardar_stats(con: sqlite3.Connection, fixture_id: int, respuesta: list) -> int:
    """Formato largo a propósito: la API añade y quita métricas (xG entró
    tarde) y un esquema por columnas obligaría a migrar cada vez."""
    con.execute("DELETE FROM fixture_stats WHERE fixture_id=?", (fixture_id,))
    n = 0
    for lado in respuesta:
        tid = (lado.get("team") or {}).get("id")
        if not tid:
            continue
        for st in lado.get("statistics") or []:
            clave = (st.get("type") or "").strip()
            if not clave:
                continue
            valor = st.get("value")
            con.execute(
                "INSERT OR REPLACE INTO fixture_stats (fixture_id, team_id, clave, valor) "
                "VALUES (?, ?, ?, ?)",
                (fixture_id, tid, clave, None if valor is None else str(valor)),
            )
            n += 1
    return n


# ── selección de objetivos ──────────────────────────────────────────────────

def fixtures_pendientes(con: sqlite3.Connection, dias: int, ultimos: int) -> list[int]:
    """Los últimos `ultimos` partidos TERMINADOS de cada equipo con un NS en
    <= `dias`, que aún no tengan ficha sellada. Ordenados del más reciente al
    más viejo: si el presupuesto se corta, lo primero que entra es lo que la
    cadena del DTP necesita sí o sí (el partido anterior)."""
    ahora = datetime.now(timezone.utc)
    marcas = ",".join("?" * len(LIGAS))
    equipos: list[int] = []
    for home, away in con.execute(
            f"""SELECT home_team_id, away_team_id FROM fixtures
                WHERE status_short='NS' AND date >= ? AND date <= ?
                  AND league_id IN ({marcas}) ORDER BY date""",
            (ahora.strftime("%Y-%m-%d %H:%M:%S"),
             (ahora + timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S"), *LIGAS)):
        for tid in (home, away):
            if tid and tid not in equipos:
                equipos.append(tid)
    if not equipos:
        return []
    sellados = {r[0] for r in con.execute("SELECT fixture_id FROM fichas_meta")}
    # amistosos de clubes (LIGAS_RUIDO): 1.893 de 2.416 fichas sin once (24/09)
    # y M6 los marca no competitivos. Fuera de la consulta, así los «últimos N»
    # son los N últimos partidos que cuentan, no un amistoso de pretemporada
    ruido = tuple(LIGAS_RUIDO) or (-1,)
    marcas_fin = ",".join("?" * len(TERMINADOS))
    pendientes: list[int] = []
    for tid in equipos:
        for (fid,) in con.execute(
                f"""SELECT id FROM fixtures
                    WHERE (home_team_id=? OR away_team_id=?) AND status_short IN ({marcas_fin})
                      AND COALESCE(league_id, -1) NOT IN ({",".join("?" * len(ruido))})
                    ORDER BY date DESC LIMIT ?""",
                (tid, tid, *TERMINADOS, *ruido, ultimos)):
            if fid not in sellados and fid not in pendientes:
                pendientes.append(fid)
    return pendientes


def cobertura_por_liga(con: sqlite3.Connection) -> dict[int, dict]:
    """Por liga: cuántas fichas selladas y cuántas trajeron cada endpoint."""
    out: dict[int, dict] = {}
    for liga, n, ali, ev, st in con.execute(
            "SELECT f.league_id, COUNT(*), SUM(m.alineaciones>0), SUM(m.eventos>0), SUM(m.stats>0) "
            "FROM fichas_meta m JOIN fixtures f ON f.id=m.fixture_id GROUP BY f.league_id"):
        out[liga] = {"n": n, "alineaciones": ali or 0, "eventos": ev or 0, "stats": st or 0}
    return out


def endpoints_a_pedir(fixture_id: int, liga: int | None, cobertura: dict[int, dict]) -> tuple[str, ...]:
    """Los endpoints que vale la pena pedir para este partido: los que su liga
    alguna vez dio, o todos si todavía no hay muestra o si es la sonda."""
    c = cobertura.get(liga) if liga is not None else None
    if not c or c["n"] < COBERTURA_MIN or (COBERTURA_SONDA and fixture_id % COBERTURA_SONDA == 0):
        return ENDPOINTS
    return tuple(e for e in ENDPOINTS if c[e] > 0)


def ingestar_fixture(cliente: Cliente, con: sqlite3.Connection, fixture_id: int,
                     cobertura: dict[int, dict] | None = None) -> bool:
    """Hasta 3 requests por partido (las que su liga alguna vez dio: ver
    `endpoints_a_pedir`). False si el presupuesto no da para todas: media
    ficha no se sella (se repetiría entera igual)."""
    fila = con.execute("SELECT league_id FROM fixtures WHERE id=?", (fixture_id,)).fetchone()
    pedir = endpoints_a_pedir(fixture_id, fila[0] if fila else None,
                              cobertura if cobertura is not None else {})
    if not cliente.quedan(len(pedir)):
        return False
    n_ali = n_ev = n_st = 0
    if "alineaciones" in pedir:
        data = cliente.get("fixtures/lineups", {"fixture": fixture_id})
        n_ali = guardar_alineaciones(con, fixture_id, (data or {}).get("response", []))
    if "eventos" in pedir:
        data = cliente.get("fixtures/events", {"fixture": fixture_id})
        n_ev = guardar_eventos(con, {"fixture_id": fixture_id, "eventos": (data or {}).get("response", [])})
    if "stats" in pedir:
        data = cliente.get("fixtures/statistics", {"fixture": fixture_id})
        n_st = guardar_stats(con, fixture_id, (data or {}).get("response", []))
    # se sella aunque venga vacío: hay ligas sin cobertura de alineaciones y
    # repreguntarlas cada corrida quemaría requests para siempre
    con.execute(
        "INSERT OR REPLACE INTO fichas_meta (fixture_id, capturado_en, alineaciones, eventos, stats) "
        "VALUES (?, ?, ?, ?, ?)",
        (fixture_id, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), n_ali, n_ev, n_st),
    )
    con.commit()
    salteados = [e for e in ENDPOINTS if e not in pedir]
    print(f"  [{cliente.usadas}/{cliente.limite}] fixture {fixture_id}: "
          f"{n_ali} en alineaciones · {n_ev} eventos · {n_st} stats"
          + (f"  (no pedidos, su liga nunca los dio: {', '.join(salteados)})" if salteados else
             "" if n_ali else "  ⚠ sin alineaciones (¿liga sin cobertura?): M1/M2 del DTP no podrán abrir"))
    return True


def _estado(con: sqlite3.Connection) -> None:
    """Qué hay ya capturado, sin gastar requests.

    Los porcentajes van sobre lo que corresponde: el grid solo lo traen los
    TITULARES (la banca no tiene carril), y el xG se mide por ficha, no por su
    puesto en el catálogo (el 24/09 el aviso «sin expected_goals» salía porque
    no estaba entre las 12 métricas más vistas, no porque faltara)."""
    uno = lambda sql, *a: con.execute(sql, a).fetchone()[0]  # noqa: E731
    pct = lambda a, b: f"{100 * a / b:.0f} %" if b else "—"  # noqa: E731
    fichas = uno("SELECT COUNT(*) FROM fichas_meta")
    sin_ali = uno("SELECT COUNT(*) FROM fichas_meta WHERE alineaciones=0")
    print(f"fichas selladas: {fichas} ({sin_ali} sin alineaciones, {pct(sin_ali, fichas)})")

    total_ali = uno("SELECT COUNT(*) FROM alineaciones")
    tit = uno("SELECT COUNT(*) FROM alineaciones WHERE titular=1")
    tit_grid = uno("SELECT COUNT(*) FROM alineaciones WHERE titular=1 AND grid IS NOT NULL AND grid<>''")
    lados = uno("SELECT COUNT(*) FROM (SELECT 1 FROM alineaciones GROUP BY fixture_id, team_id)")
    lados_grid = uno("SELECT COUNT(*) FROM (SELECT 1 FROM alineaciones WHERE titular=1 "
                     "GROUP BY fixture_id, team_id HAVING SUM(grid IS NOT NULL AND grid<>'') >= 10)")
    print(f"filas de alineación: {total_ali} · titulares {tit}, con grid {tit_grid} ({pct(tit_grid, tit)})")
    print(f"onces (equipo × partido): {lados} · con grid completo {lados_grid} ({pct(lados_grid, lados)})"
          " ← los que M2 puede leer por carril")
    if tit and not tit_grid:
        print("  ⚠ NINGUNA trae grid: M2 tendría que degradarse a carriles por posición (G/D/M/F)")

    con_stats = uno("SELECT COUNT(DISTINCT fixture_id) FROM fixture_stats")
    con_xg = uno("SELECT COUNT(DISTINCT fixture_id) FROM fixture_stats WHERE clave='expected_goals' "
                 "AND valor IS NOT NULL")
    claves = [r[0] for r in con.execute(
        "SELECT clave FROM fixture_stats GROUP BY clave ORDER BY COUNT(*) DESC LIMIT 12")]
    print(f"métricas de stats más vistas: {', '.join(claves) if claves else '—'}")
    print(f"fichas con stats: {con_stats} · con xG: {con_xg} ({pct(con_xg, con_stats)})")
    if con_stats and not con_xg:
        print("  ⚠ ninguna ficha trae expected_goals: M5 y el xG de Equipo/Estadísticas quedan sin dato")

    # por liga: dónde faltan onces y dónde falta el grid (lo que decide si
    # para esa liga el pantallazo es el procedimiento o M2 va por posición)
    try:
        filas = con.execute(
            "SELECT COALESCE(l.name, '?') AS liga, COALESCE(l.country, '') AS pais, f.league_id, "
            "COUNT(*) AS n, SUM(m.alineaciones=0) AS sin_ali "
            "FROM fichas_meta m JOIN fixtures f ON f.id=m.fixture_id "
            "LEFT JOIN leagues l ON l.id=f.league_id "
            "GROUP BY f.league_id HAVING n >= 5 ORDER BY sin_ali DESC, n DESC").fetchall()
    except sqlite3.Error:
        filas = []
    sin = [r for r in filas if r[4]]
    if sin:
        print("ligas con fichas SIN alineaciones (≥ 5 fichas; sin/total):")
        for liga, pais, lid, n, s_ali in sin[:12]:
            print(f"  {s_ali:>4}/{n:<4} {pais} · {liga} (id {lid})" + ("  ← nunca" if s_ali == n else ""))
    try:
        grid_liga = con.execute(
            "SELECT COALESCE(l.name, '?'), COALESCE(l.country, ''), f.league_id, COUNT(*) AS t, "
            "SUM(a.grid IS NOT NULL AND a.grid<>'') AS g "
            "FROM alineaciones a JOIN fixtures f ON f.id=a.fixture_id "
            "LEFT JOIN leagues l ON l.id=f.league_id WHERE a.titular=1 "
            "GROUP BY f.league_id HAVING t >= 110 AND g * 1.0 / t < 0.5 ORDER BY t DESC").fetchall()
    except sqlite3.Error:
        grid_liga = []
    if grid_liga:
        print("ligas CON onces pero sin grid (< 50 % de titulares; M2 por posición):")
        for liga, pais, lid, t, g in grid_liga[:12]:
            print(f"  {pct(g, t):>5} de {t:<5} {pais} · {liga} (id {lid})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Ficha de partido (alineaciones, eventos, stats) → sad.db")
    # en Railway las bases viven en el volumen ($SAD_DATA_DIR = /data), no en
    # /app: con «sad.db» a secas, `--estado` desde la consola decía «No existe»
    ap.add_argument("--db", default=os.path.join(os.environ.get("SAD_DATA_DIR", "."), "sad.db"))
    ap.add_argument("--dias", type=int, default=DIAS_NS_DEFAULT,
                    help=f"equipos con NS en <= N días (default {DIAS_NS_DEFAULT})")
    ap.add_argument("--ultimos", type=int, default=ULTIMOS_DEFAULT,
                    help=f"partidos terminados por equipo (default {ULTIMOS_DEFAULT})")
    ap.add_argument("--fixture", type=int, action="append", default=[],
                    help="ingestar SOLO estos fixtures (ignora ventana y sello)")
    ap.add_argument("--limite", type=int, default=None, help="tope fijo de requests")
    ap.add_argument("--estado", action="store_true", help="qué hay capturado; 0 requests")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"No existe {args.db}", file=sys.stderr)
        return 1
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA busy_timeout=30000")  # convive con el ciclo en vivo y las lecturas
    con.execute("PRAGMA journal_mode=WAL")   # en WAL solo hay UN escritor: sin esperar, el ciclo muere
    preparar_tablas(con)

    if args.estado:
        _estado(con)
        con.close()
        return 0

    pendientes = args.fixture or fixtures_pendientes(con, args.dias, args.ultimos)
    if not pendientes:
        con.close()
        print("ficha de partido: nada pendiente · 0 requests")
        return 0

    cliente = Cliente(leer_clave(), args.limite)
    # reserva CONSCIENTE DEL CALENDARIO: con fútbol nuestro cerca sube a
    # SAD_BLOQUE_RESERVA_PARTIDOS. Una corrida con backlog grande (300+ partidos
    # × 3 requests) no puede dejar sin presupuesto a las cuotas live de la noche
    # — y la ficha de un partido TERMINADO se baja mañana sin perder nada,
    # mientras que la curva de uno en juego pasa una vez (30/07/2026: 309 ciclos
    # con las cuotas en pausa por culpa de este bloque)
    reserva = 0 if args.fixture else reserva_del_dia(cliente.limite, con)
    print(f"Ficha de partido: {len(pendientes)} partidos pendientes "
          f"(NS <= {args.dias} días, últimos {args.ultimos} por equipo) · "
          f"hasta 3 requests c/u · presupuesto restante {cliente.limite - cliente.usadas}"
          f" · reserva {reserva}")
    hechos = 0
    cobertura = cobertura_por_liga(con)
    for fid in pendientes:
        if cliente.limite - cliente.usadas <= reserva:
            print(f"reserva del día alcanzada ({cliente.usadas}/{cliente.limite}, reserva {reserva}): "
                  f"{hechos}/{len(pendientes)} partidos (el resto, en la próxima corrida)")
            break
        if not ingestar_fixture(cliente, con, fid, cobertura):
            print(f"presupuesto agotado: {hechos}/{len(pendientes)} partidos "
                  f"(el resto, en la próxima corrida)")
            break
        hechos += 1
    con.close()
    print(f"fichas al día: {hechos}/{len(pendientes)} · consumo: {cliente.resumen()} "
          f"· total {cliente.usadas}/{cliente.limite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
