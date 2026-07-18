"""Genera las 4 SQLite del pipeline con ESQUEMAS REALES y datos de demo.

Sirve para probar el backend (y la web) sin las DBs de producción. La
matemática es la del motor (verificada contra MOTOR_SAD_EXTRACCION.md):
niveles por ventana de 20 con regla retroactiva, q* = dif × res × nivel del
rival (visitante ×1.4, fallback 1.0), acumuladores k* con reseteo y fusión.

    python3 -m backend.seed_demo [dir_destino]   # por defecto ./demo_data
"""
import os
import random
import sqlite3
import sys
from bisect import bisect_right
from datetime import datetime, timedelta

from backend.familias_k import FAMILIAS0, FAMILIAS_COLS, step_familias

# Equipos con sus ids reales de API-Football (LaLiga = 140)
TEAMS = [
    (543, "Real Betis"), (536, "Sevilla FC"), (530, "Atlético Madrid"),
    (533, "Villarreal"), (541, "Real Madrid"), (529, "Barcelona"),
]
LEAGUE_ID, SEASON = 140, 2025
STRENGTH = {543: 0.35, 536: 0.05, 530: 0.7, 533: 0.3, 541: 1.0, 529: 0.9}

BINS = [0.6, 1.3, 1.6, 1.9, 2.1, 2.35, 2.55, 2.85, 3.2]


def level_bin(level: float) -> int:
    return bisect_right(BINS, level) if level >= BINS[0] else 0


def poisson(rng: random.Random, lam: float) -> int:
    import math
    L, k, p = math.exp(-lam), 0, 1.0
    while p > L and k < 8:
        k += 1
        p *= rng.random()
    return k - 1


def round_robin(ids):
    arr, rounds = list(ids), []
    n = len(arr)
    for r in range(n - 1):
        pairs = [((arr[n - 1 - i], arr[i]) if r % 2 else (arr[i], arr[n - 1 - i])) for i in range(n // 2)]
        rounds.append(pairs)
        arr.insert(1, arr.pop())
    return rounds


def make_fixtures():
    """~40 terminados por equipo + 1 en vivo + 1 programado (con odds) +
    3 NS futuros sin cuotas (camino de recuperación §5 v2)."""
    ids = [t for t, _ in TEAMS]
    single = round_robin(ids)
    dbl = single + [[(a, h) for h, a in rd] for rd in single]
    rounds = dbl * 4  # 40 jornadas
    now = datetime(2026, 7, 2, 21, 0, 0)
    start = now - timedelta(days=4 * len(rounds))
    fixtures, fid = [], 900001
    for i, rd in enumerate(rounds):
        date = start + timedelta(days=4 * i)
        liga = 2 if i % 9 == 4 else LEAGUE_ID  # cada ~9ª jornada es Champions
        for home, away in rd:
            rng = random.Random(fid)
            sh, sa = STRENGTH[home], STRENGTH[away]
            gh = poisson(rng, max(0.25, 1.45 + 0.9 * (sh - sa) + 0.2))
            ga = poisson(rng, max(0.2, 1.25 + 0.9 * (sa - sh)))
            fixtures.append(dict(id=fid, date=date, home=home, away=away, gh=gh, ga=ga, league=liga,
                                 status_long="Match Finished", status_short="FT", elapsed=90))
            fid += 1
    # partido EN VIVO (Betis 1-0 Sevilla, 67') y PROGRAMADO (Madrid-Barça mañana)
    fixtures.append(dict(id=fid, date=now, home=543, away=536, gh=1, ga=0, league=LEAGUE_ID,
                         status_long="Second Half", status_short="2H", elapsed=67))
    fid += 1
    fixtures.append(dict(id=fid, date=now + timedelta(days=1), home=541, away=529, gh=None, ga=None, league=LEAGUE_ID,
                         status_long="Not Started", status_short="NS", elapsed=None))
    fid += 1
    # camino de recuperación (§5 v2): calendario futuro de Betis (con un grande
    # europeo intercalado) y de Sevilla, para /predicciones del partido en vivo
    fixtures.append(dict(id=fid, date=now + timedelta(days=2), home=529, away=543, gh=None, ga=None, league=2,
                         status_long="Not Started", status_short="NS", elapsed=None))  # Barça-Betis (Champions)
    fid += 1
    fixtures.append(dict(id=fid, date=now + timedelta(days=5), home=543, away=533, gh=None, ga=None, league=LEAGUE_ID,
                         status_long="Not Started", status_short="NS", elapsed=None))  # Betis-Villarreal
    fid += 1
    fixtures.append(dict(id=fid, date=now + timedelta(days=4), home=536, away=530, gh=None, ga=None, league=LEAGUE_ID,
                         status_long="Not Started", status_short="NS", elapsed=None))  # Sevilla-Atlético
    return fixtures


def compute_levels(hist):
    """§2: P (20) + G (últimos 5) + 1, con regla retroactiva del partido 20."""
    n = len(hist)
    if n == 0:
        return []
    if n < 20:
        return [0.5] * n
    levels = [0.0] * n
    for i in range(19, n):
        pts = sum(3 if h["gf"] > h["ga"] else 1 if h["gf"] == h["ga"] else 0 for h in hist[i - 19 : i + 1])
        u5 = hist[i - 4 : i + 1]
        dg = sum(h["gf"] - h["ga"] for h in u5)
        tg = sum(h["gf"] + h["ga"] for h in u5)
        levels[i] = pts / 20 + (0 if tg == 0 else dg / tg) + 1
    for i in range(19):
        levels[i] = levels[19]
    return levels


def step_k(prev, is_local, gf, ga, nivel):
    """§3: q* y los 12 acumuladores con reseteo (fiel al doc, bit a bit)."""
    dif, res = abs(gf - ga), (1 if gf > ga else 0 if gf == ga else -1)
    q_local = dif * res * nivel if is_local else None
    q_visita = 1.4 * dif * res * nivel if not is_local else None
    q_neg = dif * res * nivel if res == -1 else 0.0
    q_ga, q_gr = gf * nivel, -ga * nivel
    k = dict(prev)
    q_any = q_local if is_local else q_visita
    k["k_positivo"] = k["k_positivo"] + q_any if (q_any is not None and q_any > 0) else 0.0
    k["k_negativo"] = k["k_negativo"] + q_neg if q_neg < 0 else 0.0
    if is_local:
        k["k_positivo_local"] = k["k_positivo_local"] + q_local if q_local > 0 else 0.0
        k["k_negativo_local"] = k["k_negativo_local"] + q_local if q_local < 0 else 0.0
        k["k_goles_local_anotado"] = k["k_goles_local_anotado"] + q_ga if q_ga > 0 else 0.0
        k["k_goles_local_recibido"] = k["k_goles_local_recibido"] + abs(q_gr) if q_gr < 0 else 0.0
    else:
        k["k_positivo_visita"] = k["k_positivo_visita"] + q_visita if q_visita > 0 else 0.0
        k["k_negativo_visita"] = k["k_negativo_visita"] + q_visita if q_visita < 0 else 0.0
        k["k_goles_visita_anotado"] = k["k_goles_visita_anotado"] + q_ga if q_ga > 0 else 0.0
        k["k_goles_visita_recibido"] = k["k_goles_visita_recibido"] + abs(q_gr) if q_gr < 0 else 0.0
    k["k_goles_anotado"] = k["k_goles_anotado"] + q_ga if q_ga > 0 else 0.0
    k["k_goles_recibido"] = k["k_goles_recibido"] + abs(q_gr) if q_gr < 0 else 0.0
    # Familias derivadas en un único sitio: §3.6 Doble Oportunidad + §3.7 Márgenes.
    q_dc, fam = step_familias(k, is_local, gf, ga, nivel)
    k.update(fam)
    q = dict(q_local=q_local, q_visita=q_visita, q_negativo=q_neg,
             q_goles_anotado=q_ga, q_goles_recibido=q_gr,
             q_goles_local_anotado=q_ga if is_local else None,
             q_goles_local_recibido=q_gr if is_local else None,
             q_goles_visita_anotado=q_ga if not is_local else None,
             q_goles_visita_recibido=q_gr if not is_local else None,
             q_dc=q_dc)
    return q, k


K0 = {**{k: 0.0 for k in (
    "k_positivo", "k_negativo", "k_positivo_local", "k_negativo_local",
    "k_positivo_visita", "k_negativo_visita", "k_goles_anotado", "k_goles_recibido",
    "k_goles_local_anotado", "k_goles_local_recibido", "k_goles_visita_anotado", "k_goles_visita_recibido")},
      **FAMILIAS0}


ODDS_MARKETS = [
    ("Match Winner", [("Home", 2.4), ("Draw", 3.3), ("Away", 2.95)]),
    ("Double Chance", [("Home/Draw", 1.38), ("Home/Away", 1.30), ("Draw/Away", 1.55)]),
    ("Goals Over/Under", [("Over 2.5", 2.02), ("Under 2.5", 1.80)]),
    ("Both Teams Score", [("Yes", 1.74), ("No", 2.06)]),
    ("Asian Handicap", [("Home -0.5", 1.96), ("Away +0.5", 1.86)]),
]
BOOKMAKERS = [(8, "Bet365"), (11, "1xBet"), (32, "Pinnacle")]


def seed(base_dir: str):
    os.makedirs(base_dir, exist_ok=True)
    for f in ("sad.db", "levels.db", "constants.db", "discreto.db"):
        p = os.path.join(base_dir, f)
        if os.path.exists(p):
            os.remove(p)
    fixtures = make_fixtures()
    names = dict(TEAMS)

    # ---- sad.db -----------------------------------------------------------
    sad = sqlite3.connect(os.path.join(base_dir, "sad.db"))
    sad.executescript("""
        CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT, country TEXT, founded INTEGER, logo TEXT);
        CREATE TABLE leagues (id INTEGER PRIMARY KEY, name TEXT, country TEXT, logo TEXT, flag TEXT, season INTEGER);
        CREATE TABLE fixtures (
            id INTEGER PRIMARY KEY, referee TEXT, timezone TEXT, date DATETIME, timestamp INTEGER,
            first_half_start INTEGER, second_half_start INTEGER, venue_id INTEGER, venue_name TEXT,
            venue_city TEXT, status_long TEXT, status_short TEXT, elapsed INTEGER,
            league_id INTEGER, league_season INTEGER, league_round TEXT,
            home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
            halftime_home INTEGER, halftime_away INTEGER, fulltime_home INTEGER, fulltime_away INTEGER,
            extratime_home INTEGER, extratime_away INTEGER, penalty_home INTEGER, penalty_away INTEGER);
        CREATE TABLE odds (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER, league_id INTEGER,
            bookmaker_id INTEGER, bookmaker_name TEXT, bet_id INTEGER, bet_name TEXT, value TEXT, odd REAL);
        CREATE TABLE odds_history (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL,
            league_id INTEGER, bet_id INTEGER, bet_name TEXT, value TEXT, odd REAL, casas INTEGER,
            captured_at TEXT NOT NULL, casa_id INTEGER, casa TEXT);
        CREATE TABLE odds_live (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL,
            minuto INTEGER, bet_id INTEGER, bet_name TEXT, value TEXT, odd REAL,
            suspendida INTEGER DEFAULT 0, captured_at TEXT NOT NULL);
        CREATE TABLE fixture_eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL,
            minuto INTEGER, tipo TEXT, detalle TEXT, equipo_id INTEGER, jugador TEXT);
        CREATE TABLE jugadores (id INTEGER PRIMARY KEY, nombre TEXT, edad INTEGER, foto TEXT, nacionalidad TEXT);
        CREATE TABLE jugador_stats (player_id INTEGER NOT NULL, team_id INTEGER NOT NULL,
            league_id INTEGER NOT NULL, season INTEGER NOT NULL, posicion TEXT, partidos INTEGER,
            titularidades INTEGER, minutos INTEGER, rating REAL, capitan INTEGER, goles INTEGER,
            asistencias INTEGER, goles_encajados INTEGER, paradas INTEGER, tiros INTEGER,
            tiros_puerta INTEGER, pases_clave INTEGER, amarillas INTEGER, rojas INTEGER,
            penales_anotados INTEGER, penales_fallados INTEGER, actualizado_en TEXT,
            PRIMARY KEY (player_id, team_id, league_id, season));
        CREATE TABLE jugador_bajas (player_id INTEGER NOT NULL, team_id INTEGER NOT NULL,
            season INTEGER, tipo TEXT, detalle TEXT, fecha TEXT,
            PRIMARY KEY (player_id, team_id, season));
        CREATE TABLE traspasos (player_id INTEGER NOT NULL, fecha TEXT NOT NULL, tipo TEXT,
            team_in INTEGER, team_in_nombre TEXT, team_out INTEGER, team_out_nombre TEXT,
            PRIMARY KEY (player_id, fecha));
        CREATE TABLE entrenadores (team_id INTEGER NOT NULL, coach_id INTEGER NOT NULL,
            nombre TEXT, foto TEXT, desde TEXT, actualizado_en TEXT, PRIMARY KEY (team_id, coach_id));
        CREATE TABLE plantillas_meta (team_id INTEGER PRIMARY KEY, season INTEGER, actualizado_en TEXT);
    """)
    sad.executemany("INSERT INTO teams (id, name, country) VALUES (?,?, 'Spain')", TEAMS)
    # equipo SIN plantilla ni fixtures: prueba la degradación (jugadores=[])
    # y la señal de ingesta on-demand del endpoint /plantilla
    sad.execute("INSERT INTO teams (id, name, country) VALUES (599, 'Demo Sin Plantilla', 'Spain')")
    sad.execute(
        "INSERT INTO leagues (id, name, country, logo, flag, season) VALUES (?, 'LaLiga', 'Spain', "
        "'https://media.api-sports.io/football/leagues/140.png', 'https://media.api-sports.io/flags/es.svg', ?)",
        (LEAGUE_ID, SEASON),
    )
    # copa internacional: sin bandera de país (flag NULL), solo logo del torneo
    sad.execute(
        "INSERT INTO leagues (id, name, country, logo, flag, season) VALUES (2, 'UEFA Champions League', 'World', "
        "'https://media.api-sports.io/football/leagues/2.png', NULL, ?)",
        (SEASON,),
    )
    # ligas solo-metadata (sin fixtures) para probar fiabilidad_mu por liga
    sad.execute("INSERT INTO leagues (id, name, country, season) VALUES (667, 'Friendlies Clubs', 'World', ?)", (SEASON,))
    sad.execute("INSERT INTO leagues (id, name, country, season) VALUES (281, 'Primera División', 'Peru', ?)", (SEASON,))
    for f in fixtures:
        sad.execute(
            """INSERT INTO fixtures (id, date, venue_name, status_long, status_short, elapsed,
               league_id, league_season, home_team_id, away_team_id, goals_home, goals_away)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (f["id"], f["date"].strftime("%Y-%m-%d %H:%M:%S"), f"Estadio {names[f['home']]}",
             f["status_long"], f["status_short"], f["elapsed"], f["league"], SEASON,
             f["home"], f["away"], f["gh"], f["ga"]),
        )
    # cuotas prepartido: los últimos 10 terminados + el vivo + el programado
    # (los NS del camino de recuperación quedan sin cuotas a propósito)
    term_cuotas = [f for f in fixtures if f["status_long"] == "Match Finished"][-10:]
    con_cuotas = term_cuotas + [f for f in fixtures if f["status_long"] != "Match Finished"][:2]
    for f in con_cuotas:
        for bid, bname in BOOKMAKERS:
            rng = random.Random(f"{f['id']}|{bid}")
            for bet_id, (bet_name, sels) in enumerate(ODDS_MARKETS, start=1):
                for value, base in sels:
                    sad.execute(
                        "INSERT INTO odds (fixture_id, league_id, bookmaker_id, bookmaker_name, bet_id, bet_name, value, odd) VALUES (?,?,?,?,?,?,?,?)",
                        (f["id"], LEAGUE_ID, bid, bname, bet_id, bet_name, value,
                         round(base * (0.94 + rng.random() * 0.12), 2)),
                    )
            # trampa: la API sirve los MISMOS mercados en versión 1er tiempo;
            # si cuota_key los deja pasar, /cuotas y /casas mezclan valores
            sad.execute(
                "INSERT INTO odds (fixture_id, league_id, bookmaker_id, bookmaker_name, bet_id, bet_name, value, odd) VALUES (?,?,?,?,?,?,?,?)",
                (f["id"], LEAGUE_ID, bid, bname, 6, "Goals Over/Under First Half", "Over 2.5", 9.99),
            )
    # historial de snapshots prepartido (fase 1 de tiempo real): 3 capturas por
    # fixture con odds, derivando hacia la cuota base — como odds_history real
    for f in con_cuotas:
        rng = random.Random(f"{f['id']}|hist")
        for bet_id, (bet_name, sels) in enumerate(ODDS_MARKETS, start=1):
            for value, base in sels:
                inicio = base * (0.92 + rng.random() * 0.16)
                for i in range(3):
                    frac = i / 2
                    capt = (f["date"] - timedelta(hours=36 - 12 * i)).strftime("%Y-%m-%d %H:%M:%S")
                    odd = base if i == 2 else inicio * (1 - frac) + base * frac + (rng.random() - 0.5) * 0.04 * base
                    sad.execute(
                        "INSERT INTO odds_history (fixture_id, league_id, bet_id, bet_name, value, odd, casas, captured_at) VALUES (?,?,?,?,?,?,?,?)",
                        (f["id"], LEAGUE_ID, bet_id, bet_name, value, round(odd, 3), len(BOOKMAKERS), capt),
                    )
                    # crudo por casa de referencia (mismo instante, dispersión propia)
                    for bid, bname in BOOKMAKERS:
                        sad.execute(
                            "INSERT INTO odds_history (fixture_id, league_id, bet_id, bet_name, value, odd, casas, captured_at, casa_id, casa) VALUES (?,?,?,?,?,?,1,?,?,?)",
                            (f["id"], LEAGUE_ID, bet_id, bet_name, value,
                             round(odd * (0.96 + rng.random() * 0.08), 2), capt, bid, bname),
                        )
                    # trampa por captura: el mismo mercado en versión 1er
                    # tiempo — sin filtro en cuota_key produce el zigzag
                    if bet_name == "Goals Over/Under":
                        sad.execute(
                            "INSERT INTO odds_history (fixture_id, league_id, bet_id, bet_name, value, odd, casas, captured_at) VALUES (?,?,?,?,?,?,?,?)",
                            (f["id"], LEAGUE_ID, 6, "Goals Over/Under First Half", value, 9.99, len(BOOKMAKERS), capt),
                        )
    # cuotas EN VIVO (fase 3): serie de capturas por minuto para el partido en
    # juego, con el catálogo de /odds/live ("Fulltime Result") y una suspendida
    vivo = next(f for f in fixtures if f["status_short"] == "2H")
    rng = random.Random(f"{vivo['id']}|live")
    # DESCUENTO DEL 1T + DESCANSO: la API repite elapsed=45, retrocede un
    # minuto y manda null en el descanso — el patrón real que apilaba la curva
    # en vertical y dibujaba lazos al arrancar el 2T; el backend debe repartirlo
    # en minutos efectivos 45.x monótonos
    for minuto, tmin in [(45, 41), (45, 42), (44, 43), (None, 44), (None, 45)]:
        capt = (vivo["date"] + timedelta(minutes=tmin)).strftime("%Y-%m-%d %H:%M:%S")
        for value, base in [("Home", 1.65), ("Draw", 3.9), ("Away", 5.2)]:
            sad.execute(
                "INSERT INTO odds_live (fixture_id, minuto, bet_id, bet_name, value, odd, suspendida, captured_at) VALUES (?,?,?,?,?,?,?,?)",
                (vivo["id"], minuto, 59, "Fulltime Result", value,
                 round(base * (0.94 + rng.random() * 0.12), 2), 0, capt),
            )
    for i, minuto in enumerate(range(46, vivo["elapsed"] + 1, 3)):
        capt = (vivo["date"] + timedelta(minutes=minuto)).strftime("%Y-%m-%d %H:%M:%S")
        for value, base in [("Home", 1.65), ("Draw", 3.9), ("Away", 5.2)]:
            sad.execute(
                "INSERT INTO odds_live (fixture_id, minuto, bet_id, bet_name, value, odd, suspendida, captured_at) VALUES (?,?,?,?,?,?,?,?)",
                (vivo["id"], minuto, 59, "Fulltime Result", value,
                 round(base * (0.94 + rng.random() * 0.12), 2),
                 1 if value == "Away" and minuto == vivo["elapsed"] else 0, capt),
            )
        # línea O/U del catálogo live ya con el handicap fusionado ("Over 2.5")
        for value, base in [("Over 2.5", 1.4), ("Under 2.5", 2.9)]:
            sad.execute(
                "INSERT INTO odds_live (fixture_id, minuto, bet_id, bet_name, value, odd, suspendida, captured_at) VALUES (?,?,?,?,?,?,?,?)",
                (vivo["id"], minuto, 36, "Over/Under Line", value,
                 round(base * (0.94 + rng.random() * 0.12), 2), 0, capt),
            )
        # trampa live: el feed también trae mercados de 1er tiempo
        sad.execute(
            "INSERT INTO odds_live (fixture_id, minuto, bet_id, bet_name, value, odd, suspendida, captured_at) VALUES (?,?,?,?,?,?,?,?)",
            (vivo["id"], minuto, 13, "First Half Winner", "Home", 9.99, 0, capt),
        )
    # eventos del partido en juego (goles y tarjetas, con el catálogo crudo de la API)
    sad.executemany(
        "INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador) VALUES (?,?,?,?,?,?)",
        [
            (vivo["id"], 12, "Card", "Yellow Card", vivo["away"], "J. Pérez"),
            (vivo["id"], 34, "Goal", "Normal Goal", vivo["home"], "L. García"),
            (vivo["id"], 51, "Goal", "Penalty", vivo["away"], "M. Díaz"),
            (vivo["id"], 60, "Card", "Second Yellow card", vivo["away"], "J. Pérez"),
            (vivo["id"], 63, "subst", "Substitution 1", vivo["home"], "Suplente"),  # no debe servirse
            (vivo["id"], 65, "Goal", "Missed Penalty", vivo["home"], "R. Falla"),   # tampoco
        ],
    )
    # ---- capa de jugadores (docs/JUGADORES.md): plantillas demo -----------
    # Misma forma que deja backend.ingesta.jugadores: stats por competición,
    # una baja con peso real, un recién llegado, DT y meta con TTL.
    POSICIONES = ["Goalkeeper", "Goalkeeper", "Defender", "Defender", "Defender", "Defender",
                  "Midfielder", "Midfielder", "Midfielder", "Midfielder", "Midfielder",
                  "Attacker", "Attacker", "Attacker", "Attacker", "Defender"]
    ahora = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for tid, tname in TEAMS:
        rng = random.Random(f"{tid}|jugadores")
        for i, pos in enumerate(POSICIONES):
            pid = tid * 1000 + i
            titular = i % 2 == 0 or rng.random() > 0.35
            minutos = int((1800 if titular else 500) * (0.55 + rng.random() * 0.7))
            partidos = min(40, minutos // 70)
            es_gk, es_atk = pos == "Goalkeeper", pos == "Attacker"
            goles = 0 if es_gk else int(minutos / 90 * (0.45 if es_atk else 0.1) * (0.5 + rng.random()))
            asist = 0 if es_gk else int(minutos / 90 * 0.12 * (0.4 + rng.random()))
            sad.execute("INSERT INTO jugadores (id, nombre, edad, nacionalidad) VALUES (?,?,?, 'Spain')",
                        (pid, f"J{i + 1} {tname.split()[-1]}", 21 + i % 14))
            sad.execute(
                """INSERT INTO jugador_stats (player_id, team_id, league_id, season, posicion,
                   partidos, titularidades, minutos, rating, capitan, goles, asistencias,
                   goles_encajados, paradas, tiros, tiros_puerta, pases_clave, amarillas, rojas,
                   penales_anotados, penales_fallados, actualizado_en)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (pid, tid, LEAGUE_ID, SEASON, pos, partidos, int(partidos * 0.8), minutos,
                 round(6.4 + rng.random() * 1.2, 2), 1 if i == 2 else 0, goles, asist,
                 int(minutos / 90 * 1.1) if es_gk else 0, int(minutos / 90 * 3.1) if es_gk else 0,
                 goles * 3, goles * 2, asist * 2, rng.randrange(6), 0, 0, 0, ahora),
            )
        # baja con peso (el primer delantero), recién llegado, DT y meta
        sad.execute("INSERT INTO jugador_bajas (player_id, team_id, season, tipo, detalle, fecha) VALUES (?,?,?,?,?,?)",
                    (tid * 1000 + 11, tid, SEASON, "Missing Fixture", "Lesión muscular", ahora[:10]))
        sad.execute("INSERT INTO traspasos (player_id, fecha, tipo, team_in, team_in_nombre, team_out, team_out_nombre) VALUES (?,?,?,?,?,?,?)",
                    (tid * 1000 + 14, ahora[:10], "Loan", tid, tname, 999, "Deportivo Demo"))
        sad.execute("INSERT INTO entrenadores (team_id, coach_id, nombre, desde, actualizado_en) VALUES (?,?,?,?,?)",
                    (tid, tid + 5000, f"DT {tname.split()[-1]}", "2025-12-01", ahora))
        sad.execute("INSERT INTO plantillas_meta (team_id, season, actualizado_en) VALUES (?,?,?)",
                    (tid, SEASON, ahora))
    sad.commit()
    sad.close()

    # ---- pipeline: niveles → constantes → discreto ------------------------
    finished = [f for f in fixtures if f["status_long"] == "Match Finished"]
    hist = {tid: [] for tid, _ in TEAMS}
    for f in sorted(finished, key=lambda x: x["date"]):
        hist[f["home"]].append(dict(fixture_id=f["id"], date=f["date"], rival=f["away"], is_local=True, gf=f["gh"], ga=f["ga"], league=f["league"]))
        hist[f["away"]].append(dict(fixture_id=f["id"], date=f["date"], rival=f["home"], is_local=False, gf=f["ga"], ga=f["gh"], league=f["league"]))

    levels_by_team = {tid: compute_levels(h) for tid, h in hist.items()}

    lv = sqlite3.connect(os.path.join(base_dir, "levels.db"))
    lv.executescript("""CREATE TABLE team_levels (id INTEGER PRIMARY KEY, team_id INTEGER NOT NULL,
        fixture_id INTEGER NOT NULL, date DATETIME NOT NULL, level REAL NOT NULL);""")
    for tid, h in hist.items():
        for m, level in zip(h, levels_by_team[tid]):
            lv.execute("INSERT INTO team_levels (team_id, fixture_id, date, level) VALUES (?,?,?,?)",
                       (tid, m["fixture_id"], m["date"].strftime("%Y-%m-%d %H:%M:%S"), level))
    lv.commit()
    lv.close()

    def rival_level_at(rival_id, date):
        h, lvls = hist[rival_id], levels_by_team[rival_id]
        dates = [m["date"] for m in h]
        i = bisect_right(dates, date) - 1
        return lvls[i] if i >= 0 else 1.0  # fallback 1.0 (§3.1)

    co = sqlite3.connect(os.path.join(base_dir, "constants.db"))
    familias_ddl = ", ".join(f"{c} REAL" for c in FAMILIAS_COLS)  # k_dc + márgenes (§3.6/§3.7)
    co.executescript(f"""CREATE TABLE constants (id INTEGER PRIMARY KEY, team_id INTEGER NOT NULL,
        fixture_id INTEGER NOT NULL, date DATETIME NOT NULL,
        q_local REAL, q_visita REAL, q_negativo REAL, q_goles_anotado REAL, q_goles_recibido REAL,
        q_goles_local_anotado REAL, q_goles_local_recibido REAL, q_goles_visita_anotado REAL, q_goles_visita_recibido REAL,
        q_dc REAL,
        k_positivo REAL, k_negativo REAL, k_positivo_local REAL, k_negativo_local REAL,
        k_positivo_visita REAL, k_negativo_visita REAL, k_goles_anotado REAL, k_goles_recibido REAL,
        k_goles_local_anotado REAL, k_goles_local_recibido REAL, k_goles_visita_anotado REAL, k_goles_visita_recibido REAL,
        {familias_ddl});
        CREATE INDEX ix_constants_team_date ON constants(team_id, date);""")
    di = sqlite3.connect(os.path.join(base_dir, "discreto.db"))
    di.executescript("""CREATE TABLE processed_matches (id INTEGER PRIMARY KEY, fecha DATETIME NOT NULL,
        fixture_id INTEGER NOT NULL, equipo_id INTEGER NOT NULL, equipo_nombre TEXT NOT NULL,
        rival_id INTEGER NOT NULL, rival_nombre TEXT NOT NULL, condicion TEXT, status_long TEXT,
        league_id INTEGER, league_season TEXT, goals_home INTEGER, goals_away INTEGER,
        nivel_equipo INTEGER, nivel_rival INTEGER,
        k REAL, k_local REAL, k_visita REAL, k_goles_anotado REAL, k_goles_recibido REAL,
        k_goles_local_anotado REAL, k_goles_local_recibido REAL, k_goles_visita_anotado REAL, k_goles_visita_recibido REAL,
        processed_at DATETIME, UNIQUE(fixture_id, equipo_id));""")

    now_txt = datetime(2026, 7, 2, 20, 30, 0).strftime("%Y-%m-%d %H:%M:%S")
    for tid, h in hist.items():
        k = dict(K0)
        for idx, m in enumerate(h):
            nivel_rival = rival_level_at(m["rival"], m["date"])
            q, k = step_k(k, m["is_local"], m["gf"], m["ga"], nivel_rival)
            crow = {
                "team_id": tid, "fixture_id": m["fixture_id"],
                "date": m["date"].strftime("%Y-%m-%d %H:%M:%S"),
                "q_local": q["q_local"], "q_visita": q["q_visita"], "q_negativo": q["q_negativo"],
                "q_goles_anotado": q["q_goles_anotado"], "q_goles_recibido": q["q_goles_recibido"],
                "q_goles_local_anotado": q["q_goles_local_anotado"], "q_goles_local_recibido": q["q_goles_local_recibido"],
                "q_goles_visita_anotado": q["q_goles_visita_anotado"], "q_goles_visita_recibido": q["q_goles_visita_recibido"],
                "q_dc": q["q_dc"],
                "k_positivo": k["k_positivo"], "k_negativo": k["k_negativo"],
                "k_positivo_local": k["k_positivo_local"], "k_negativo_local": k["k_negativo_local"],
                "k_positivo_visita": k["k_positivo_visita"], "k_negativo_visita": k["k_negativo_visita"],
                "k_goles_anotado": k["k_goles_anotado"], "k_goles_recibido": k["k_goles_recibido"],
                "k_goles_local_anotado": k["k_goles_local_anotado"], "k_goles_local_recibido": k["k_goles_local_recibido"],
                "k_goles_visita_anotado": k["k_goles_visita_anotado"], "k_goles_visita_recibido": k["k_goles_visita_recibido"],
                **{c: k[c] for c in FAMILIAS_COLS},
            }
            co.execute(
                f"INSERT INTO constants ({','.join(crow)}) VALUES ({','.join('?' * len(crow))})",
                tuple(crow.values()),
            )
            di.execute(
                """INSERT INTO processed_matches (fecha, fixture_id, equipo_id, equipo_nombre, rival_id, rival_nombre,
                   condicion, status_long, league_id, league_season, goals_home, goals_away, nivel_equipo, nivel_rival,
                   k, k_local, k_visita, k_goles_anotado, k_goles_recibido,
                   k_goles_local_anotado, k_goles_local_recibido, k_goles_visita_anotado, k_goles_visita_recibido, processed_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (m["date"].strftime("%Y-%m-%d %H:%M:%S"), m["fixture_id"], tid, names[tid], m["rival"], names[m["rival"]],
                 "Local" if m["is_local"] else "Visita", "Match Finished", m["league"], str(SEASON),
                 m["gf"] if m["is_local"] else m["ga"], m["ga"] if m["is_local"] else m["gf"],
                 level_bin(levels_by_team[tid][idx]), level_bin(nivel_rival),
                 k["k_positivo"] + k["k_negativo"], k["k_positivo_local"] + k["k_negativo_local"],
                 k["k_positivo_visita"] + k["k_negativo_visita"], k["k_goles_anotado"], k["k_goles_recibido"],
                 k["k_goles_local_anotado"], k["k_goles_local_recibido"],
                 k["k_goles_visita_anotado"], k["k_goles_visita_recibido"], now_txt),
            )
    co.commit()
    co.close()
    di.commit()
    di.close()
    print(f"Demo lista en {base_dir}: {len(fixtures)} fixtures ({len(finished)} terminados) · {len(TEAMS)} equipos")


if __name__ == "__main__":
    seed(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "demo_data"))
