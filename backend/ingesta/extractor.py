"""Extractor prepartido de API-Football (api-sports.io directo) → sad.db.

Port de la ruta A del pipeline viejo (auto_extractor_v5.py, ver
docs/INFORME_INGESTA.md §3) corrigiendo sus defectos: UNA sola lista de ligas,
fechas SIEMPRE en UTC con el formato de sad.db ('YYYY-MM-DD HH:MM:SS.ffffff'),
y sin clave hardcodeada (env API_FOOTBALL_KEY o .env de la raíz).

Flujo: /fixtures por liga en la ventana [--desde, --hasta] (default hoy−3d a
hoy+10d) y /odds de los partidos NS sin cuotas (todos los bookmakers en 1
request). Presupuesto conservador para el plan free (100/día → tope 95).

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
LIMITE_DEFAULT = 95
DELAY = 1.5

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


class Cliente:
    """El tope es DIARIO y compartido entre corridas: se persiste en
    .extractor_cuota.json (git-ignorado) porque el plan free corta a las 100/día."""

    def __init__(self, clave: str, limite: int):
        self.clave = clave
        self.limite = limite
        self.hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.usadas = self._leer_cuota()

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
                if data.get("errors"):
                    print(f"  error de la API: {data['errors']}")
                    return None
                time.sleep(DELAY)
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
                    n += 1
    con.commit()
    return n


def fixtures_sin_cuotas(con: sqlite3.Connection, dias: int = DIAS_ADELANTE) -> list[int]:
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    tope = (datetime.now(timezone.utc) + timedelta(days=dias)).strftime("%Y-%m-%d")
    return [
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
        return 0
    print("Sin conexión: revisa la clave en dashboard.api-football.com")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Extractor API-Football → sad.db (prepartido)")
    ap.add_argument("--db", default="sad.db", help="ruta a sad.db")
    ap.add_argument("--limite", type=int, default=LIMITE_DEFAULT, help="tope de requests")
    ap.add_argument("--desde", help="inicio de ventana YYYY-MM-DD (default hoy−3d)")
    ap.add_argument("--hasta", help="fin de ventana YYYY-MM-DD (default hoy+10d)")
    ap.add_argument("--solo", choices=["fixtures", "cuotas"], help="ejecutar una sola fase")
    ap.add_argument("--probar", action="store_true", help="solo verificar conexión (1 request)")
    ap.add_argument("--ligas", action="store_true",
                    help="solo rellenar la tabla leagues desde /leagues (1 request por página)")
    ap.add_argument("--torneo", action="append", metavar="LIGA[:TEMPORADA]",
                    help="ingesta completa de un torneo (temporada entera, sin ventana); repetible")
    args = ap.parse_args()

    cliente = Cliente(leer_clave(), args.limite)
    if args.probar:
        return probar(cliente)

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
        pendientes = fixtures_sin_cuotas(con)
        print(f"Cuotas: {len(pendientes)} partidos NS sin odds "
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
