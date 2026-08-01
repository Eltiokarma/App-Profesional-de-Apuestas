"""Ingesta de jugadores (capa 1 de docs/JUGADORES.md): plantillas con stats de
temporada, bajas, traspasos y entrenador — para los equipos de NUESTRAS ligas
con partidos NS próximos.

    python -m backend.ingesta.jugadores                # NS en <= 3 días
    python -m backend.ingesta.jugadores --dias 7
    python -m backend.ingesta.jugadores --equipo 541 --temporada 2026
    python -m backend.ingesta.jugadores --ttl-horas 24 # ventana de traspasos

Escribe SOLO las tablas de jugadores de sad.db (jugadores, jugador_stats,
jugador_bajas, traspasos, entrenadores, plantillas_meta). Comparte presupuesto
con el extractor (mismo Cliente: cabeceras x-ratelimit + respaldo RapidAPI).
Costo ~5-6 requests/equipo, con TTL por equipo para no repagar plantillas
frescas. Los indicadores NO se calculan aquí: backend/jugadores.py los deriva
en lectura (0 requests)."""
import argparse
import os
import sqlite3
import sys
import unicodedata
from datetime import datetime, timedelta, timezone

from backend.ingesta.extractor import LIGAS, Cliente, leer_clave, ligas_vivo, reserva_del_dia

TTL_HORAS_DEFAULT = 168  # 7 días: fuera de ventana de traspasos alcanza de sobra
# Equipos que la API NO cubre (plantilla vacía): sellado LARGO. Repreguntarlos
# cada TTL normal quemaba 4 requests por equipo sin fruto — el 28/07/2026
# fueron 223 de 276 equipos ingestados (~78% del gasto de jugadores). La
# cobertura de la API no aparece de un día para otro.
TTL_HORAS_SIN_DATOS = int(os.environ.get("SAD_JUGADORES_TTL_SIN_DATOS", "720"))  # 30 días
# TTL de los dos datos LENTOS: traspasos y DT. Los cuatro endpoints iban con el
# mismo TTL de 7 días, y eso era la mitad del gasto de jugadores tirada: las
# bajas y las stats por-90 cambian cada semana, pero los traspasos solo se
# mueven en ventana de mercado y un DT dura meses. 30 días.
# NO se pierde el cambio de DT: cada alineación (ficha y XI prepartido) trae el
# nombre del entrenador, y si no coincide con el guardado se fuerza el refresco
# — la etiqueta "DT NUEVO" del bloque G sigue saliendo el mismo día.
TTL_HORAS_LENTO = int(os.environ.get("SAD_JUGADORES_TTL_LENTO", "720"))  # 30 días
# La ingesta de jugadores sigue las ligas IMPORTANTES, no las 56 de LIGAS: las
# copas nacionales meten cientos de equipos de ascenso (y 667 Amistosos de
# Clubes, equipos de todo el mundo) cuyas plantillas casi no alimentan el
# análisis. Un equipo de 1ª que juega copa sigue entrando por SU liga.
# SAD_JUGADORES_TODAS_LIGAS=1 vuelve al padrón completo.
JUGADORES_TODAS_LIGAS = os.environ.get("SAD_JUGADORES_TODAS_LIGAS", "").strip() == "1"
DIAS_NS_DEFAULT = 3

DDL = """
CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    edad INTEGER,
    foto TEXT,
    nacionalidad TEXT
);
CREATE TABLE IF NOT EXISTS jugador_stats (
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    posicion TEXT,
    partidos INTEGER,
    titularidades INTEGER,
    minutos INTEGER,
    rating REAL,
    capitan INTEGER,
    goles INTEGER,
    asistencias INTEGER,
    goles_encajados INTEGER,
    paradas INTEGER,
    tiros INTEGER,
    tiros_puerta INTEGER,
    pases_clave INTEGER,
    amarillas INTEGER,
    rojas INTEGER,
    penales_anotados INTEGER,
    penales_fallados INTEGER,
    actualizado_en TEXT,
    PRIMARY KEY (player_id, team_id, league_id, season)
);
CREATE INDEX IF NOT EXISTS idx_jstats_team ON jugador_stats(team_id, season);
CREATE TABLE IF NOT EXISTS jugador_bajas (
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    season INTEGER,
    tipo TEXT,
    detalle TEXT,
    fecha TEXT,
    PRIMARY KEY (player_id, team_id, season)
);
CREATE TABLE IF NOT EXISTS traspasos (
    player_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    tipo TEXT,
    team_in INTEGER,
    team_in_nombre TEXT,
    team_out INTEGER,
    team_out_nombre TEXT,
    PRIMARY KEY (player_id, fecha)
);
CREATE INDEX IF NOT EXISTS idx_traspasos_in ON traspasos(team_in, fecha);
CREATE TABLE IF NOT EXISTS entrenadores (
    team_id INTEGER NOT NULL,
    coach_id INTEGER NOT NULL,
    nombre TEXT,
    foto TEXT,
    desde TEXT,
    actualizado_en TEXT,
    PRIMARY KEY (team_id, coach_id)
);
CREATE TABLE IF NOT EXISTS plantillas_meta (
    team_id INTEGER PRIMARY KEY,
    season INTEGER,
    actualizado_en TEXT
);
"""


def preparar_tablas(con: sqlite3.Connection) -> None:
    con.executescript(DDL)
    columnas = {r[1] for r in con.execute("PRAGMA table_info(plantillas_meta)")}
    if "con_datos" not in columnas:
        # default 1: lo ya sellado sin la marca se trata como equipo con datos
        # (TTL corto), que es el comportamiento previo a la columna
        con.execute("ALTER TABLE plantillas_meta ADD COLUMN con_datos INTEGER NOT NULL DEFAULT 1")
    if "lento_en" not in columnas:
        # cuándo se pidieron por última vez traspasos y DT (los dos datos que
        # NO cambian a ritmo semanal). NULL en lo ya sellado: la primera
        # corrida tras el deploy los pide una vez y a partir de ahí rota lento
        con.execute("ALTER TABLE plantillas_meta ADD COLUMN lento_en TEXT")
    con.commit()


def _ahora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _i(v) -> int:
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0


def _rating(v) -> float | None:
    try:
        return round(float(v), 3) if v not in (None, "", "–") else None
    except (TypeError, ValueError):
        return None


def equipos_pendientes(con: sqlite3.Connection, dias: int, ttl_horas: int) -> list[tuple[int, int]]:
    """(team_id, season) de equipos de NUESTRAS ligas con NS en <= dias,
    excluyendo los refrescados dentro del TTL. La temporada es la del fixture
    próximo (así los torneos de año cruzado piden la temporada correcta)."""
    ahora = datetime.now(timezone.utc)
    ligas = set(LIGAS) if JUGADORES_TODAS_LIGAS else ligas_vivo()
    marcas = ",".join("?" * len(ligas))
    filas = con.execute(
        f"""SELECT f.home_team_id, f.away_team_id, f.league_season FROM fixtures f
            WHERE f.status_short='NS' AND f.date >= ? AND f.date <= ?
              AND f.league_id IN ({marcas})
            ORDER BY f.date""",
        (ahora.strftime("%Y-%m-%d %H:%M:%S"),
         (ahora + timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S"), *sorted(ligas)),
    ).fetchall()
    limite_ttl = (ahora - timedelta(hours=ttl_horas)).strftime("%Y-%m-%d %H:%M:%S")
    limite_sin = (ahora - timedelta(hours=max(TTL_HORAS_SIN_DATOS, ttl_horas))).strftime("%Y-%m-%d %H:%M:%S")
    frescos = {
        r[0] for r in con.execute(
            "SELECT team_id FROM plantillas_meta WHERE actualizado_en > ? "
            "OR (con_datos = 0 AND actualizado_en > ?)", (limite_ttl, limite_sin)
        ).fetchall()
    }
    vistos: dict[int, int] = {}
    for home_id, away_id, season in filas:
        for tid in (home_id, away_id):
            if tid and tid not in vistos and tid not in frescos:
                vistos[tid] = season or datetime.now(timezone.utc).year
    return list(vistos.items())


def guardar_plantilla(con: sqlite3.Connection, team_id: int, season: int, filas: list) -> int:
    """Filas de /players (paginado): stats por competición. Se conserva una
    fila por (jugador, equipo, liga, temporada); los indicadores agregan."""
    ahora, n = _ahora(), 0
    for item in filas:
        p = item.get("player") or {}
        if not p.get("id"):
            continue
        con.execute(
            "INSERT OR REPLACE INTO jugadores (id, nombre, edad, foto, nacionalidad) VALUES (?, ?, ?, ?, ?)",
            (p["id"], p.get("name"), p.get("age"), p.get("photo"), p.get("nationality")),
        )
        for st in item.get("statistics") or []:
            team, league = st.get("team") or {}, st.get("league") or {}
            if team.get("id") != team_id or not league.get("id"):
                continue
            games = st.get("games") or {}
            goals = st.get("goals") or {}
            shots = st.get("shots") or {}
            passes = st.get("passes") or {}
            cards = st.get("cards") or {}
            pen = st.get("penalty") or {}
            con.execute(
                """INSERT OR REPLACE INTO jugador_stats (
                       player_id, team_id, league_id, season, posicion, partidos,
                       titularidades, minutos, rating, capitan, goles, asistencias,
                       goles_encajados, paradas, tiros, tiros_puerta, pases_clave,
                       amarillas, rojas, penales_anotados, penales_fallados, actualizado_en
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    p["id"], team_id, league["id"], league.get("season") or season,
                    games.get("position"),
                    _i(games.get("appearences")),  # sic: así viene de la API
                    _i(games.get("lineups")), _i(games.get("minutes")),
                    _rating(games.get("rating")), 1 if games.get("captain") else 0,
                    _i(goals.get("total")), _i(goals.get("assists")),
                    _i(goals.get("conceded")), _i(goals.get("saves")),
                    _i(shots.get("total")), _i(shots.get("on")), _i(passes.get("key")),
                    _i(cards.get("yellow")), _i(cards.get("red")) + _i(cards.get("yellowred")),
                    _i(pen.get("scored")), _i(pen.get("missed")), ahora,
                ),
            )
            n += 1
    con.commit()
    return n


def guardar_bajas(con: sqlite3.Connection, team_id: int, season: int, filas: list) -> int:
    """Filas de /injuries del equipo: lesiones y sanciones reportadas. La foto
    del equipo se reemplaza completa en cada refresco (las altas desaparecen)."""
    con.execute("DELETE FROM jugador_bajas WHERE team_id=? AND (season=? OR season IS NULL)",
                (team_id, season))
    n = 0
    for item in filas:
        p = item.get("player") or {}
        fx = item.get("fixture") or {}
        if not p.get("id"):
            continue
        con.execute(
            "INSERT OR REPLACE INTO jugador_bajas (player_id, team_id, season, tipo, detalle, fecha) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (p["id"], team_id, season, p.get("type"), p.get("reason"),
             (fx.get("date") or "")[:10] or None),
        )
        n += 1
    con.commit()
    return n


def guardar_traspasos(con: sqlite3.Connection, filas: list) -> int:
    n = 0
    for item in filas:
        p = item.get("player") or {}
        if not p.get("id"):
            continue
        for t in item.get("transfers") or []:
            teams = t.get("teams") or {}
            t_in, t_out = teams.get("in") or {}, teams.get("out") or {}
            if not t.get("date"):
                continue
            con.execute(
                "INSERT OR REPLACE INTO traspasos (player_id, fecha, tipo, team_in, "
                "team_in_nombre, team_out, team_out_nombre) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (p["id"], t["date"], t.get("type"), t_in.get("id"), t_in.get("name"),
                 t_out.get("id"), t_out.get("name")),
            )
            n += 1
    con.commit()
    return n


def guardar_entrenador(con: sqlite3.Connection, team_id: int, filas: list) -> int:
    """/coachs?team= trae la carrera completa de cada DT que pasó por el club:
    se guarda SOLO el vigente (entrada de carrera en este equipo sin fecha fin)."""
    ahora, n = _ahora(), 0
    for item in filas:
        if not item.get("id"):
            continue
        for c in item.get("career") or []:
            if (c.get("team") or {}).get("id") == team_id and not c.get("end"):
                con.execute("DELETE FROM entrenadores WHERE team_id=?", (team_id,))
                con.execute(
                    "INSERT OR REPLACE INTO entrenadores (team_id, coach_id, nombre, foto, desde, actualizado_en) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (team_id, item["id"], item.get("name"), item.get("photo"),
                     c.get("start"), ahora),
                )
                n += 1
                break
        if n:
            break
    con.commit()
    return n


def necesita_lentas(con: sqlite3.Connection, team_id: int,
                    ttl_horas: int = TTL_HORAS_LENTO) -> bool:
    """¿Toca pedir traspasos y DT de este equipo? Son los dos datos que NO
    cambian a ritmo semanal, así que van con TTL propio (30 días) en vez del
    de la plantilla (7). Se piden igualmente, sin esperar al TTL, cuando la
    ÚLTIMA ALINEACIÓN capturada trae un entrenador distinto del guardado:
    esa señal llega gratis con cada ficha y cada XI prepartido, así que un
    cambio de DT se detecta el mismo día y la etiqueta "DT NUEVO" no se
    retrasa. Sin alineaciones ni marca previa, se piden."""
    fila = con.execute(
        "SELECT lento_en FROM plantillas_meta WHERE team_id=?", (team_id,)).fetchone()
    if not fila or not fila[0]:
        return True
    limite = (datetime.now(timezone.utc) - timedelta(hours=ttl_horas)).strftime("%Y-%m-%d %H:%M:%S")
    if fila[0] <= limite:
        return True
    try:
        dt_alin = con.execute(
            """SELECT a.entrenador FROM alineaciones a JOIN fixtures f ON f.id = a.fixture_id
               WHERE a.team_id=? AND a.entrenador IS NOT NULL AND a.entrenador <> ''
               ORDER BY f.date DESC LIMIT 1""", (team_id,)).fetchone()
        dt_guardado = con.execute(
            "SELECT nombre FROM entrenadores WHERE team_id=? ORDER BY actualizado_en DESC LIMIT 1",
            (team_id,)).fetchone()
    except sqlite3.Error:
        return False  # DB sin esas tablas: el TTL manda
    if dt_alin and dt_guardado and dt_alin[0] and dt_guardado[0]:
        if _norm_dt(dt_alin[0]) != _norm_dt(dt_guardado[0]):
            print(f"  equipo {team_id}: la alineación trae DT '{dt_alin[0]}' y teníamos "
                  f"'{dt_guardado[0]}' → se refresca traspasos y DT sin esperar al TTL")
            return True
    return False


def _norm_dt(nombre: str) -> str:
    """Nombres de DT comparables entre /coachs y las alineaciones (la API los
    escribe distinto: 'M. Pellegrino' vs 'Mauricio Pellegrino')."""
    n = unicodedata.normalize("NFD", (nombre or "").lower())
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    partes = [p for p in n.replace(".", " ").split() if len(p) > 1]
    return partes[-1] if partes else n.strip()


def ingestar_equipo(cliente: Cliente, con: sqlite3.Connection, team_id: int, season: int) -> bool:
    """Plantilla + bajas (+ traspasos y DT si toca) de un equipo. False si el
    presupuesto se agotó antes de completarlo (no se sella el TTL)."""
    if not cliente.quedan(2):
        return False
    filas = cliente.paginado("players", {"team": team_id, "season": season})
    stats = guardar_plantilla(con, team_id, season, filas)
    con_datos = 1 if (stats or filas) else 0
    if not con_datos:
        # sin cobertura de la API para este equipo/temporada: se sella con el
        # TTL LARGO (reintentarlo cada corrida quemaría requests sin fruto)
        print(f"  equipo {team_id} t{season}: sin datos de jugadores en la API "
              f"(se repregunta en {TTL_HORAS_SIN_DATOS // 24} días)")
    data = cliente.get("injuries", {"team": team_id, "season": season})
    bajas = guardar_bajas(con, team_id, season, (data or {}).get("response", []))
    # traspasos y DT solo si toca (TTL propio de 30 días o cambio de DT visto
    # en la alineación): eran la mitad del gasto de jugadores para datos que
    # casi nunca cambian entre corridas
    lentas = necesita_lentas(con, team_id) and cliente.quedan(2)
    trasp = dt = 0
    lento_en = None
    if lentas:
        data = cliente.get("transfers", {"team": team_id})
        trasp = guardar_traspasos(con, (data or {}).get("response", []))
        data = cliente.get("coachs", {"team": team_id})
        dt = guardar_entrenador(con, team_id, (data or {}).get("response", []))
        lento_en = _ahora()
    con.execute(
        "INSERT INTO plantillas_meta (team_id, season, actualizado_en, con_datos, lento_en) "
        "VALUES (?, ?, ?, ?, ?) ON CONFLICT(team_id) DO UPDATE SET "
        "season=excluded.season, actualizado_en=excluded.actualizado_en, "
        "con_datos=excluded.con_datos, lento_en=COALESCE(excluded.lento_en, plantillas_meta.lento_en)",
        (team_id, season, _ahora(), con_datos, lento_en),
    )
    con.commit()
    print(f"  [{cliente.usadas}/{cliente.limite}] equipo {team_id} t{season}: "
          f"{stats} filas de stats · {bajas} bajas"
          + (f" · {trasp} traspasos · DT {'sí' if dt else 'no'}" if lentas else " · (traspasos/DT al día)"))
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingesta de jugadores (plantillas, bajas, traspasos, DT)")
    ap.add_argument("--db", default="sad.db", help="ruta a sad.db")
    ap.add_argument("--dias", type=int, default=DIAS_NS_DEFAULT,
                    help=f"equipos con NS en <= N días (default {DIAS_NS_DEFAULT})")
    ap.add_argument("--ttl-horas", type=int, default=TTL_HORAS_DEFAULT,
                    help=f"no repedir equipos refrescados hace menos de N horas (default {TTL_HORAS_DEFAULT})")
    ap.add_argument("--equipo", type=int, help="ingestar SOLO este team_id (ignora ventana y TTL)")
    ap.add_argument("--temporada", type=int, help="temporada para --equipo (default: año actual)")
    ap.add_argument("--limite", type=int, default=None, help="tope fijo de requests")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"No existe {args.db}", file=sys.stderr)
        return 1
    cliente = Cliente(leer_clave(), args.limite)
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA busy_timeout=30000")  # convive con el ciclo en vivo y las lecturas
    con.execute("PRAGMA journal_mode=WAL")   # en WAL solo hay UN escritor: sin esperar, el ciclo muere
    preparar_tablas(con)

    if args.equipo:
        pendientes = [(args.equipo, args.temporada or datetime.now(timezone.utc).year)]
    else:
        pendientes = equipos_pendientes(con, args.dias, args.ttl_horas)
    # reserva CONSCIENTE DEL CALENDARIO: con fútbol nuestro cerca sube a
    # SAD_BLOQUE_RESERVA_PARTIDOS. Esta ingesta corre en bloque (~4 requests por
    # equipo × cientos de equipos) y no puede dejar sin presupuesto a las cuotas
    # live de la noche; una plantilla se baja mañana igual de bien
    reserva = 0 if args.equipo else reserva_del_dia(cliente.limite, con)
    print(f"Jugadores: {len(pendientes)} equipos pendientes (NS <= {args.dias} días, "
          f"TTL {args.ttl_horas} h) · presupuesto restante {cliente.limite - cliente.usadas}"
          f" · reserva {reserva}")
    hechos = 0
    for team_id, season in pendientes:
        if cliente.limite - cliente.usadas <= reserva:
            print(f"reserva del día alcanzada ({cliente.usadas}/{cliente.limite}, reserva {reserva}): "
                  f"{hechos}/{len(pendientes)} equipos (el resto, en la próxima corrida)")
            break
        if not ingestar_equipo(cliente, con, team_id, season):
            print(f"presupuesto agotado: {hechos}/{len(pendientes)} equipos (el resto, en la próxima corrida)")
            break
        hechos += 1
    con.close()
    print(f"plantillas al día: {hechos}/{len(pendientes)} · consumo: {cliente.resumen()} "
          f"· total {cliente.usadas}/{cliente.limite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
