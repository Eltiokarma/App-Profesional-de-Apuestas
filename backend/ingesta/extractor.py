"""Extractor prepartido de API-Football (api-sports.io directo) → sad.db.

Port de la ruta A del pipeline viejo (auto_extractor_v5.py, ver
docs/INFORME_INGESTA.md §3) corrigiendo sus defectos: UNA sola lista de ligas,
fechas SIEMPRE en UTC con el formato de sad.db ('YYYY-MM-DD HH:MM:SS.ffffff'),
y sin clave hardcodeada (env API_FOOTBALL_KEY o .env de la raíz).

Flujo: /fixtures por liga en la ventana [--desde, --hasta] (default hoy−3d a
hoy+10d) y /odds de los partidos NS (todos los bookmakers en 1 request):
primera captura para los que no tienen cuotas, y re-captura de los que
empiezan en <= 2 días para el historial de movimiento (odds_history guarda
la media entre casas por mercado/selección con captured_at; la tabla odds
queda como "última foto"). El presupuesto diario y el ritmo se leen de las
cabeceras x-ratelimit-* de cada respuesta, así que se ajustan solos al plan
contratado (fallback conservador del plan free: 95/día · 10 req/min).

Uso:
  PYTHONUTF8=1 python -m backend.ingesta.extractor                  # ventana default
  PYTHONUTF8=1 python -m backend.ingesta.extractor --desde 2026-06-08
  ... --solo fixtures | --solo cuotas · --limite N · --db ruta · --probar
  ... --torneo 1:2026 --torneo 34:2026   # temporada completa, sin ventana
"""
import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# API-Football directo (clave de dashboard.api-football.com): mismo API v3
# que servía RapidAPI, cambian solo el host y la cabecera de autenticación.
BASE_URL = "https://v3.football.api-sports.io"
SEASON = int(os.environ.get("SAD_SEASON", "2026"))
DIAS_ATRAS = 3
DIAS_ADELANTE = 10
DIAS_REFRESCO = 2  # NS que empiezan en <= N días: re-captura de cuotas para el historial

DDL_ODDS_HISTORY = """
CREATE TABLE IF NOT EXISTS odds_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL,
    league_id INTEGER,
    bet_id INTEGER,
    bet_name TEXT,
    value TEXT,
    odd REAL,
    casas INTEGER,
    captured_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_oddshist_fixture ON odds_history(fixture_id, captured_at);
"""
# Fallbacks del plan free, vigentes solo hasta que la primera respuesta traiga
# las cabeceras x-ratelimit-*: tope diario (100 − margen) y 10 req/min. Con
# cabeceras, tope y ritmo se recalculan al plan real (Pro 7500/día · 300/min, etc.).
LIMITE_DEFAULT = 95
MARGEN_DIARIO = 5
DELAY_DEFAULT = 6.5
DELAY_MIN = 0.25

# Única fuente de verdad de ligas (el viejo tenía 3 listas divergentes).
LIGAS = {
    # Mundial (jun-jul 2026: la ventana diaria mantiene resultados y cuotas al día)
    1: "Copa del Mundo",
    # Sudamérica
    128: "Argentina - Liga Profesional",
    129: "Argentina - Primera Nacional",
    71: "Brasil - Serie A",
    72: "Brasil - Serie B",
    239: "Colombia - Primera A",
    265: "Chile - Primera División",
    281: "Perú - Primera División",
    268: "Uruguay - Primera División",
    242: "Ecuador - Liga Pro",
    # México
    262: "México - Liga MX",
    263: "México - Liga de Expansión",
    # Copas CONMEBOL
    13: "CONMEBOL Libertadores",
    11: "CONMEBOL Sudamericana",
    # Copas UEFA
    2: "UEFA Champions League",
    3: "UEFA Europa League",
    848: "UEFA Conference League",
    # Europa top
    39: "Inglaterra - Premier League",
    40: "Inglaterra - Championship",
    140: "España - La Liga",
    141: "España - Segunda División",
    135: "Italia - Serie A",
    136: "Italia - Serie B",
    78: "Alemania - Bundesliga",
    79: "Alemania - 2. Bundesliga",
    61: "Francia - Ligue 1",
    62: "Francia - Ligue 2",
    # Europa otros
    94: "Portugal - Primeira Liga",
    144: "Bélgica - Pro League",
}


def _ligas_extra() -> dict[int, str]:
    """SAD_LIGAS_EXTRA="414:Copa Chile,999:Copa de la Liga Perú" añade torneos
    sin tocar código (útil para torneos nuevos; el ID se descubre con --buscar)."""
    extra: dict[int, str] = {}
    for item in os.environ.get("SAD_LIGAS_EXTRA", "").split(","):
        item = item.strip()
        if not item:
            continue
        id_txt, _, nombre = item.partition(":")
        try:
            extra[int(id_txt)] = nombre.strip() or f"liga {id_txt}"
        except ValueError:
            print(f"SAD_LIGAS_EXTRA: entrada inválida {item!r} (formato id:Nombre)", file=sys.stderr)
    return extra


LIGAS.update(_ligas_extra())


def leer_clave() -> str:
    clave = os.environ.get("API_FOOTBALL_KEY", "").strip()
    if not clave and os.path.exists(".env"):
        with open(".env", encoding="utf-8") as f:
            for linea in f:
                if linea.strip().startswith("API_FOOTBALL_KEY="):
                    clave = linea.split("=", 1)[1].strip()
    if not clave:
        raise SystemExit(
            "Falta API_FOOTBALL_KEY (variable de entorno o .env en la raíz; ver .env.example)"
        )
    return clave


def fecha_utc(iso: str) -> str:
    """ISO de la API (con zona) → 'YYYY-MM-DD HH:MM:SS.ffffff' en UTC (formato sad.db)."""
    dt = datetime.fromisoformat(iso).astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


CUOTA_PATH = ".extractor_cuota.json"


def _cabecera_int(headers, nombre: str) -> int | None:
    try:
        return int(headers.get(nombre))
    except (TypeError, ValueError):
        return None


class Cliente:
    """El tope es DIARIO y compartido entre corridas: se persiste en
    .extractor_cuota.json (git-ignorado) porque la API corta al agotar el plan.
    Tope y ritmo se leen de las cabeceras x-ratelimit-* de cada respuesta;
    --limite explícito fija el tope a mano y desactiva el autoajuste."""

    def __init__(self, clave: str, limite: int | None = None):
        self.clave = clave
        self.limite_fijo = limite is not None
        self.limite = limite if limite is not None else LIMITE_DEFAULT
        self.limite_api: int | None = None
        self.delay = DELAY_DEFAULT
        self.hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.usadas = self._leer_cuota()

    def _ajustar_por_cabeceras(self, headers) -> None:
        """x-ratelimit-requests-* traen la cuota diaria del plan; x-ratelimit-limit,
        el rate limit por minuto. El contador de la API manda sobre el local
        (cubre otras corridas u otros consumidores de la misma clave)."""
        diario = _cabecera_int(headers, "x-ratelimit-requests-limit")
        restantes = _cabecera_int(headers, "x-ratelimit-requests-remaining")
        if diario:
            self.limite_api = diario
            if not self.limite_fijo:
                self.limite = max(diario - MARGEN_DIARIO, 1)
            if restantes is not None:
                self.usadas = max(self.usadas, diario - restantes)
                self._guardar_cuota()
        por_minuto = _cabecera_int(headers, "x-ratelimit-limit")
        if por_minuto:
            self.delay = max(60.0 / por_minuto, DELAY_MIN)

    def _leer_cuota(self) -> int:
        try:
            with open(CUOTA_PATH, encoding="utf-8") as f:
                datos = json.load(f)
            return datos["usadas"] if datos.get("dia") == self.hoy else 0
        except (OSError, ValueError, KeyError):
            return 0

    def _guardar_cuota(self) -> None:
        with open(CUOTA_PATH, "w", encoding="utf-8") as f:
            json.dump({"dia": self.hoy, "usadas": self.usadas}, f)

    def quedan(self, n: int = 1) -> bool:
        return self.limite - self.usadas >= n

    def get(self, endpoint: str, params: dict) -> dict | None:
        if not self.quedan():
            print(f"  presupuesto diario agotado ({self.usadas}/{self.limite})")
            return None
        self.usadas += 1
        self._guardar_cuota()
        url = f"{BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"x-apisports-key": self.clave})
        for intento in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.load(resp)
                    self._ajustar_por_cabeceras(resp.headers)
                if data.get("errors"):
                    print(f"  error de la API: {data['errors']}")
                    return None
                time.sleep(self.delay)
                return data
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    print("  429 de la API — espero 60 s…")
                    time.sleep(60)
                    continue
                print(f"  HTTP {e.code} en {endpoint} (intento {intento + 1}/3)")
                time.sleep(3)
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"  error de red: {e} (intento {intento + 1}/3)")
                time.sleep(5)
        return None

    def paginado(self, endpoint: str, params: dict) -> list:
        """Concatena todas las páginas de una consulta (cada página = 1 request)."""
        data = self.get(endpoint, params)
        if not data:
            return []
        filas = list(data.get("response", []))
        total = data.get("paging", {}).get("total", 1)
        for pagina in range(2, total + 1):
            data = self.get(endpoint, {**params, "page": pagina})
            if not data:
                break
            filas.extend(data.get("response", []))
        return filas


def guardar_fixtures(con: sqlite3.Connection, respuesta: list) -> int:
    n = 0
    for item in respuesta:
        f = item.get("fixture", {})
        league = item.get("league", {})
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        score = item.get("score", {})
        home, away = teams.get("home", {}), teams.get("away", {})
        if not f.get("id") or not home.get("id") or not away.get("id"):
            continue
        for equipo in (home, away):
            con.execute(
                "INSERT OR REPLACE INTO teams (id, name, country, founded, logo) "
                "VALUES (?, ?, ?, ?, ?)",
                (equipo["id"], equipo.get("name"), equipo.get("country"),
                 equipo.get("founded"), equipo.get("logo")),
            )
        if league.get("id") and league.get("name"):
            con.execute(
                "INSERT OR REPLACE INTO leagues (id, name, country, logo, flag, season) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (league["id"], league["name"], league.get("country"),
                 league.get("logo"), league.get("flag"), league.get("season")),
            )
        ht, ft = score.get("halftime", {}), score.get("fulltime", {})
        et, pen = score.get("extratime", {}), score.get("penalty", {})
        con.execute(
            """INSERT OR REPLACE INTO fixtures (
                   id, timezone, date, timestamp, venue_id, venue_name, venue_city,
                   status_long, status_short, elapsed, league_id, league_season,
                   league_round, home_team_id, away_team_id, goals_home, goals_away,
                   halftime_home, halftime_away, fulltime_home, fulltime_away,
                   extratime_home, extratime_away, penalty_home, penalty_away
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f["id"], "UTC", fecha_utc(f["date"]), f.get("timestamp"),
                f.get("venue", {}).get("id"), f.get("venue", {}).get("name"),
                f.get("venue", {}).get("city"), f.get("status", {}).get("long"),
                f.get("status", {}).get("short"), f.get("status", {}).get("elapsed"),
                league.get("id"), league.get("season"), league.get("round"),
                home["id"], away["id"], goals.get("home"), goals.get("away"),
                ht.get("home"), ht.get("away"), ft.get("home"), ft.get("away"),
                et.get("home"), et.get("away"), pen.get("home"), pen.get("away"),
            ),
        )
        n += 1
    con.commit()
    return n


def guardar_odds(con: sqlite3.Connection, fixture_id: int, respuesta: list) -> int:
    n = 0
    capturado = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    medias: dict[tuple, list[float]] = {}
    for item in respuesta:
        league_id = item.get("league", {}).get("id")
        for bk in item.get("bookmakers", []):
            for bet in bk.get("bets", []):
                for valor in bet.get("values", []):
                    try:
                        odd = float(valor.get("odd"))
                    except (TypeError, ValueError):
                        odd = None
                    fila = con.execute(
                        "SELECT id FROM odds WHERE fixture_id=? AND bookmaker_id=? "
                        "AND bet_id=? AND value=?",
                        (fixture_id, bk.get("id"), bet.get("id"), valor.get("value")),
                    ).fetchone()
                    if fila:
                        con.execute("UPDATE odds SET odd=? WHERE id=?", (odd, fila[0]))
                    else:
                        con.execute(
                            "INSERT INTO odds (fixture_id, league_id, bookmaker_id, "
                            "bookmaker_name, bet_id, bet_name, value, odd) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (fixture_id, league_id, bk.get("id"), bk.get("name"),
                             bet.get("id"), bet.get("name"), valor.get("value"), odd),
                        )
                    if odd is not None:
                        medias.setdefault(
                            (league_id, bet.get("id"), bet.get("name"), valor.get("value")), []
                        ).append(odd)
                    n += 1
    # snapshot para el historial de movimiento: media entre casas por selección
    for (liga, bet_id, bet_name, value), odds in medias.items():
        con.execute(
            "INSERT INTO odds_history (fixture_id, league_id, bet_id, bet_name, "
            "value, odd, casas, captured_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (fixture_id, liga, bet_id, bet_name, value,
             round(sum(odds) / len(odds), 3), len(odds), capturado),
        )
    con.commit()
    return n


def fixtures_para_cuotas(con: sqlite3.Connection, dias: int = DIAS_ADELANTE,
                         dias_refresco: int = DIAS_REFRESCO) -> list[int]:
    """Primero los NS sin ninguna cuota (primera captura, toda la ventana);
    después los NS que empiezan en <= dias_refresco días aunque ya tengan
    (re-captura: snapshot nuevo en odds_history)."""
    ahora = datetime.now(timezone.utc)
    hoy = ahora.strftime("%Y-%m-%d")
    tope = (ahora + timedelta(days=dias)).strftime("%Y-%m-%d")
    tope_refresco = (ahora + timedelta(days=dias_refresco)).strftime("%Y-%m-%d")
    sin_cuotas = [
        fila[0]
        for fila in con.execute(
            """SELECT DISTINCT f.id FROM fixtures f
               LEFT JOIN odds o ON o.fixture_id = f.id
               WHERE f.status_short = 'NS' AND date(f.date) BETWEEN ? AND ?
                 AND o.id IS NULL
               ORDER BY f.date""",
            (hoy, tope),
        )
    ]
    refresco = [
        fila[0]
        for fila in con.execute(
            """SELECT DISTINCT f.id FROM fixtures f
               JOIN odds o ON o.fixture_id = f.id
               WHERE f.status_short = 'NS' AND date(f.date) BETWEEN ? AND ?
               ORDER BY f.date""",
            (hoy, tope_refresco),
        )
    ]
    vistos = set(sin_cuotas)
    return sin_cuotas + [f for f in refresco if f not in vistos]


def fixtures_proximos(con: sqlite3.Connection, horas: int) -> list[int]:
    """NS que arrancan entre ahora y ahora+N horas (fechas de sad.db en UTC):
    el objetivo del refresco de día de partido (fase 2)."""
    ahora = datetime.now(timezone.utc)
    desde = ahora.strftime("%Y-%m-%d %H:%M:%S")
    hasta = (ahora + timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
    return [
        fila[0]
        for fila in con.execute(
            "SELECT id FROM fixtures WHERE status_short='NS' AND date BETWEEN ? AND ? ORDER BY date",
            (desde, hasta),
        )
    ]


def guardar_ligas(con: sqlite3.Connection, respuesta: list) -> int:
    """Items de /leagues: {league: {id,name,logo}, country: {name,flag}, seasons: [...]}."""
    n = 0
    for item in respuesta:
        lg = item.get("league", {})
        pais = item.get("country", {})
        if not lg.get("id") or not lg.get("name"):
            continue
        temporadas = [s.get("year") for s in item.get("seasons", []) if s.get("year")]
        con.execute(
            "INSERT OR REPLACE INTO leagues (id, name, country, logo, flag, season) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (lg["id"], lg["name"], pais.get("name"), lg.get("logo"),
             pais.get("flag"), max(temporadas) if temporadas else None),
        )
        n += 1
    con.commit()
    return n


def probar(cliente: Cliente) -> int:
    data = cliente.get("timezone", {})
    if data and data.get("response"):
        print(f"Conexión OK — {len(data['response'])} timezones · requests usadas: {cliente.usadas}")
        if cliente.limite_api:
            print(f"plan detectado: {cliente.limite_api} req/día · ~{round(60 / cliente.delay)} req/min "
                  f"→ tope local {cliente.limite} · delay {cliente.delay:.2f} s")
        else:
            print("la API no mandó cabeceras x-ratelimit-*; sigo con los fallbacks del plan free")
        return 0
    print("Sin conexión: revisa la clave en dashboard.api-football.com")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Extractor API-Football → sad.db (prepartido)")
    ap.add_argument("--db", default="sad.db", help="ruta a sad.db")
    ap.add_argument("--limite", type=int, default=None,
                    help="tope fijo de requests (default: auto por cabeceras de la API, arranca en 95)")
    ap.add_argument("--desde", help="inicio de ventana YYYY-MM-DD (default hoy−3d)")
    ap.add_argument("--hasta", help="fin de ventana YYYY-MM-DD (default hoy+10d)")
    ap.add_argument("--solo", choices=["fixtures", "cuotas"], help="ejecutar una sola fase")
    ap.add_argument("--ventana-horas", type=int, metavar="N",
                    help="refresco ligero (fase 2): SOLO cuotas de los NS que empiezan en <= N horas")
    ap.add_argument("--probar", action="store_true", help="solo verificar conexión (1 request)")
    ap.add_argument("--buscar", metavar="TEXTO",
                    help="buscar ligas por nombre en /leagues e imprimir sus IDs (1 request)")
    ap.add_argument("--ligas", action="store_true",
                    help="solo rellenar la tabla leagues desde /leagues (1 request por página)")
    ap.add_argument("--torneo", action="append", metavar="LIGA[:TEMPORADA]",
                    help="ingesta completa de un torneo (temporada entera, sin ventana); repetible")
    args = ap.parse_args()

    cliente = Cliente(leer_clave(), args.limite)
    if args.probar:
        return probar(cliente)

    if args.buscar:
        data = cliente.get("leagues", {"search": args.buscar})
        filas = (data or {}).get("response", [])
        if not filas:
            print("sin resultados (el nombre necesita al menos 3 letras)")
            return 1
        for item in filas:
            lg, pais = item.get("league", {}), item.get("country", {})
            años = [str(s["year"]) for s in item.get("seasons", []) if s.get("year")]
            print(f"  id {lg.get('id')} · {lg.get('name')} · {pais.get('name')}"
                  f" · temporadas: {', '.join(años[-4:]) or '—'}")
        print('para ingestarla: SAD_LIGAS_EXTRA="id:Nombre[,id:Nombre]" (env) o añadirla a LIGAS')
        return 0

    if not os.path.exists(args.db):
        print(f"No existe {args.db}", file=sys.stderr)
        return 1

    if args.ligas:
        con = sqlite3.connect(args.db)
        filas = cliente.paginado("leagues", {})
        n = guardar_ligas(con, filas)
        con.close()
        print(f"ligas guardadas: {n} · requests usadas: {cliente.usadas}/{cliente.limite}")
        return 0 if n else 1

    if args.torneo:
        con = sqlite3.connect(args.db)
        total = 0
        for spec in args.torneo:
            if not cliente.quedan():
                break
            liga_txt, _, temp = spec.partition(":")
            liga_id = int(liga_txt)
            temporada = int(temp) if temp else SEASON
            filas = cliente.paginado("fixtures", {"league": liga_id, "season": temporada})
            n = guardar_fixtures(con, filas)
            total += n
            print(f"  [{cliente.usadas}/{cliente.limite}] liga {liga_id} · temporada {temporada}: {n} fixtures")
        con.close()
        print(f"fixtures guardados: {total} · requests usadas: {cliente.usadas}/{cliente.limite}")
        return 0
    hoy = datetime.now(timezone.utc)
    desde = args.desde or (hoy - timedelta(days=DIAS_ATRAS)).strftime("%Y-%m-%d")
    hasta = args.hasta or (hoy + timedelta(days=DIAS_ADELANTE)).strftime("%Y-%m-%d")
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA busy_timeout=15000")  # convive con las lecturas del backend
    con.executescript(DDL_ODDS_HISTORY)  # idempotente: prepara el historial en DBs viejas

    if args.ventana_horas:
        pendientes = fixtures_proximos(con, args.ventana_horas)
        print(f"Refresco: {len(pendientes)} NS que empiezan en <= {args.ventana_horas} h "
              f"(presupuesto restante {cliente.limite - cliente.usadas})")
        total = 0
        for fid in pendientes:
            if not cliente.quedan():
                print("  presupuesto agotado; el resto queda para el próximo refresco")
                break
            data = cliente.get("odds", {"fixture": fid})
            if data is None:
                continue
            n = guardar_odds(con, fid, data.get("response", []))
            total += n
            print(f"  [{cliente.usadas}/{cliente.limite}] fixture {fid}: {n} cuotas")
        con.close()
        print(f"cuotas refrescadas: {total} · requests usadas: {cliente.usadas}/{cliente.limite}")
        return 0

    if args.solo != "cuotas":
        print(f"Fixtures {desde} → {hasta} · temporada {SEASON} · {len(LIGAS)} ligas")
        total = 0
        for liga_id, nombre in LIGAS.items():
            if not cliente.quedan():
                break
            filas = cliente.paginado(
                "fixtures",
                {"league": liga_id, "season": SEASON, "from": desde, "to": hasta},
            )
            n = guardar_fixtures(con, filas)
            total += n
            print(f"  [{cliente.usadas}/{cliente.limite}] {nombre}: {n} fixtures")
        print(f"fixtures guardados: {total}")

    if args.solo != "fixtures":
        pendientes = fixtures_para_cuotas(con)
        print(f"Cuotas: {len(pendientes)} partidos NS (primera captura + refresco <={DIAS_REFRESCO}d) "
              f"(presupuesto restante {cliente.limite - cliente.usadas})")
        total = 0
        for fid in pendientes:
            if not cliente.quedan():
                print("  presupuesto agotado; el resto queda para la próxima corrida")
                break
            data = cliente.get("odds", {"fixture": fid})
            if data is None:
                continue
            n = guardar_odds(con, fid, data.get("response", []))
            total += n
            print(f"  [{cliente.usadas}/{cliente.limite}] fixture {fid}: {n} cuotas")
        print(f"cuotas guardadas: {total}")

    con.close()
    print(f"listo · requests usadas: {cliente.usadas}/{cliente.limite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
