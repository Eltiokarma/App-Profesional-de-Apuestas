"""Test de las suspensiones que salen de la base (backend/sanciones.py) — sin red.

Neymar vio la roja directa el 25/10 y el parte del 28/10 lo tenía disponible;
Bryan Castillo (Carabobo) se fue por doble amarilla y la tabla F1 no lo decía;
Vitor Hugo cumplía la 3.ª amarilla en el Brasileirão (incidencias 772, 778 y
835). Este test arma esos casos y sus contrarios: la roja de la liga no
suspende en la copa, el que está en la hoja juega, un conteo parcial no afirma
nada y la amarilla de la doble amarilla no suma al ciclo.

    python -m backend.test_sanciones
"""
import os
import sqlite3
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="sad-sanc-")
os.environ["SAD_DATA_DIR"] = _TMP
os.environ.setdefault("SAD_SIN_HILOS", "1")

fallos = 0
SAN, VAS, PAL, CAR, LGU, ATL = 128, 133, 121, 2810, 2813, 1062
BRA, VEN, COPA = 71, 281, 73


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def montar():
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.executescript("""
        CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT, status_long TEXT,
            league_id INTEGER, league_season INTEGER, league_round TEXT,
            home_team_id INTEGER, away_team_id INTEGER);
        CREATE TABLE fixture_eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL,
            minuto INTEGER, extra INTEGER, tipo TEXT, detalle TEXT, equipo_id INTEGER, jugador TEXT,
            jugador_id INTEGER, asistente TEXT, asistente_id INTEGER);
        CREATE TABLE alineaciones (fixture_id INTEGER, team_id INTEGER, formacion TEXT, entrenador TEXT,
            player_id INTEGER, jugador TEXT, numero INTEGER, posicion TEXT, grid TEXT, titular INTEGER);
    """)
    fx = [
        # Santos: la roja de Neymar el 25/10 (31' amarilla, 45' roja: doble amarilla en la API real; aquí directa)
        (10, "2026-10-18 22:00:00", "FT", BRA, "Regular Season - 30", SAN, ATL),
        (11, "2026-10-25 00:00:00", "FT", BRA, "Regular Season - 31", VAS, SAN),
        (12, "2026-10-28 22:30:00", "NS", BRA, "Regular Season - 32", SAN, PAL),
        # Santos en la COPA después de la roja de la liga: no está suspendido ahí
        (13, "2026-10-27 22:00:00", "NS", COPA, "Round of 16", SAN, VAS),
        # Carabobo: doble amarilla de Castillo al 81'
        (20, "2026-10-25 21:30:00", "FT", VEN, "Clausura - 10", CAR, LGU),
        (21, "2026-10-28 23:30:00", "NS", VEN, "Clausura - 11", CAR, LGU),
        # Atlético-MG: Vitor Hugo, amarillas en 30, 31 y 32 → la 3.ª en el último
        (30, "2026-10-12 22:00:00", "FT", BRA, "Regular Season - 30", ATL, PAL),
        (31, "2026-10-19 22:00:00", "FT", BRA, "Regular Season - 31", PAL, ATL),
        (32, "2026-10-26 22:00:00", "FT", BRA, "Regular Season - 32", ATL, VAS),
        (33, "2026-10-30 22:00:00", "NS", BRA, "Regular Season - 33", VAS, ATL),
    ]
    con.executemany("INSERT INTO fixtures VALUES (?,?,?,'',?,2026,?,?,?)", fx)
    ev = [
        (10, 60, "Card", "Yellow Card", SAN, "Neymar", 276),
        (11, 45, "Card", "Red Card", SAN, "Neymar", 276),
        (11, 89, "Card", "Yellow Card", SAN, "João Schmidt", 32901),
        (20, 70, "Card", "Yellow Card", CAR, "Bryan Castillo", 52722),
        (20, 81, "Card", "Red Card", CAR, "Bryan Castillo", 52722),
        (20, 35, "Card", "Yellow Card", CAR, "Alexander González", 2441),
        (30, 20, "Card", "Yellow Card", ATL, "Vitor Hugo", 30398),
        (31, 33, "Card", "Yellow Card", ATL, "Vitor Hugo", 30398),
        (32, 70, "Card", "Yellow Card", ATL, "Vitor Hugo", 30398),
        # Arroyo: dos amarillas, una de ellas en el último: no completa el ciclo de 3
        (31, 10, "Card", "Yellow Card", ATL, "K. Arroyo", 414405),
        (32, 15, "Card", "Yellow Card", ATL, "K. Arroyo", 414405),
        # Hulk: amarilla + roja en el 31 (doble amarilla) y amarilla en el 32: la del 31 no suma
        (30, 50, "Card", "Yellow Card", ATL, "Hulk", 10),
        (31, 60, "Card", "Yellow Card", ATL, "Hulk", 10),
        (31, 80, "Card", "Red Card", ATL, "Hulk", 10),
        (32, 80, "Card", "Yellow Card", ATL, "Hulk", 10),
    ]
    con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
                    "VALUES (?,?,?,?,?,?,?)", ev)
    con.commit()
    return con


con = montar()
from backend import sanciones  # noqa: E402

s12 = sanciones.de_fixture(12)
n12 = {x["jugadorId"]: x for x in s12["a"]["sancionados"]}
check("772: Neymar, roja en el último partido de la liga, se pierde el siguiente de la liga",
      276 in n12 and n12[276]["tipo"] == "roja" and n12[276]["partido"] == 11, s12)
check("…con la advertencia de que una roja directa puede valer más fechas", "más fechas" in n12[276]["detalle"])
check("…y la amarilla suelta de Schmidt no suspende", 32901 not in n12)
check("la roja de la LIGA no suspende en la COPA", not sanciones.de_fixture(13)["a"]["sancionados"])

s21 = sanciones.de_fixture(21)
n21 = {x["jugadorId"]: x for x in s21["a"]["sancionados"]}
check("778: Castillo, doble amarilla (amarilla 70' + roja 81'), se pierde el siguiente",
      52722 in n21 and n21[52722]["tipo"] == "doble_amarilla", s21)
check("Venezuela sin regla de amarillas conocida: no infiere ciclos", s21["a"]["regla"] is None
      and len(n21) == 1)

s33 = sanciones.de_fixture(33)
n33 = {x["jugadorId"]: x for x in s33["b"]["sancionados"]}
check("835: Vitor Hugo, 3.ª amarilla en el Brasileirão (cada 3), se pierde el siguiente",
      30398 in n33 and n33[30398]["tipo"] == "amarillas" and n33[30398]["amarillas"] == 3, s33)
check("Arroyo con 2 amarillas no está sancionado", 414405 not in n33)
check("la amarilla de la doble amarilla no suma al ciclo (Hulk 2, no 3)",
      10 not in n33 and next(a["amarillas"] for a in s33["b"]["amarillas"] if a["jugadorId"] == 10) == 2,
      s33["b"]["amarillas"])
check("la regla de la competición viaja", "cada 3" in (s33["b"]["regla"] or ""))

# conteo parcial: sin los eventos de un partido de la temporada no se afirma un ciclo
con.execute("DELETE FROM fixture_eventos WHERE fixture_id=30")
con.commit()
s33p = sanciones.de_fixture(33)
check("con un partido sin eventos, el ciclo de amarillas no se infiere (conteoParcial)",
      not any(x["tipo"] == "amarillas" for x in s33p["b"]["sancionados"]) and s33p["b"]["conteoParcial"], s33p["b"])
con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
            "VALUES (30, 20, 'Card', 'Yellow Card', ?, 'Vitor Hugo', 30398)", (ATL,))
con.commit()

# la hoja de ESTE partido manda: Neymar en el once → no estaba suspendido
con.execute("INSERT INTO alineaciones VALUES (12, ?, '4-3-3', 'DT', 276, 'Neymar', 10, 'F', '4:2', 1)", (SAN,))
con.commit()
check("en la hoja del partido: juega, no se infiere sanción",
      not any(x["jugadorId"] == 276 for x in sanciones.de_fixture(12)["a"]["sancionados"]))
con.execute("DELETE FROM alineaciones")
con.commit()

# la tabla F1 lleva la sanción en la fila y la lista del lado
from backend.analisis import f1_base  # noqa: E402
t = {"candidatos": [{"jugadorId": 276, "nombre": "Neymar"}, {"jugadorId": 32901, "nombre": "João Schmidt"}]}
t = f1_base._con_sanciones(t, sanciones.de_fixture(12)["a"])
check("F1: la fila del sancionado lleva `sancion` y el lado `sancionados`",
      t["candidatos"][0].get("sancion", {}).get("tipo") == "roja" and len(t["sancionados"]) == 1
      and "sancion" not in t["candidatos"][1], t)
check("F1: cada fila lleva sus amarillas en la competición", t["candidatos"][1].get("amarillasEnLaCompeticion") == 1)

# la alerta del parte
fx12 = {"id": 12}
parte = {"equipos": {"a": {"fuera": [], "bloques": {}}, "b": {"fuera": [], "bloques": {}}}}
al = f1_base.alertas_sancion(parte, fx12, {"a": "Santos", "b": "Palmeiras"})
check("SANCION-SIN-DECLARAR: Neymar sancionado y fuera de `fuera`",
      len(al) == 1 and al[0]["codigo"] == "SANCION-SIN-DECLARAR" and "Neymar" in al[0]["detalle"], al)
parte["equipos"]["a"]["fuera"] = [{"nombre": "Neymar", "estado": "baja", "motivo": "sanción", "jugadorId": 276}]
check("declarado en `fuera`: no suena", not f1_base.alertas_sancion(parte, fx12, {"a": "Santos", "b": "Palmeiras"}))
parte["equipos"]["a"]["fuera"] = []
parte["equipos"]["a"]["bloques"] = {"F": {"nota": "Neymar juega: la sanción se apeló y el tribunal la suspendió"}}
check("la nota que trata la sanción: no suena",
      not f1_base.alertas_sancion(parte, fx12, {"a": "Santos", "b": "Palmeiras"}))

# el ejecutor de penales sancionado baja al final de la lista del DTP (772)
from backend.analisis import dtp_cowork  # noqa: E402
lados = {"a": {"penales": {"ejecutores": [{"nombre": "Neymar da Silva Santos Júnior", "jugadorId": 276,
                                           "convertidos": 3, "errados": 0},
                                          {"nombre": "J. Schmidt", "jugadorId": 32901, "convertidos": 1,
                                           "errados": 0}], "nota": "x"}},
         "b": {"penales": {"ejecutores": [], "nota": "y"}}}
dtp_cowork._ejecutor_sancionado(12, lados)
_ej = lados["a"]["penales"]["ejecutores"]
check("772: el ejecutor sancionado (Neymar) lleva `sancionado` y baja al final; la nota lo dice",
      _ej[0]["jugadorId"] == 32901 and "sancionado" in _ej[1] and "sancionados para este partido"
      in lados["a"]["penales"]["nota"], lados)

# ── EL ESCANEO PREVENTIVO (backend/analisis/escaneo.py) ─────────────────────
from datetime import datetime, timezone  # noqa: E402
from backend.analisis import escaneo  # noqa: E402
con.executescript("""
    CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE alineaciones_versiones (fixture_id INTEGER, team_id INTEGER, formacion TEXT, capturada_en TEXT);
""")
con.executemany("INSERT INTO teams VALUES (?,?)", [(SAN, "Santos"), (VAS, "Vasco"), (PAL, "Palmeiras"),
                (CAR, "Carabobo"), (LGU, "La Guaira"), (ATL, "Atlético-MG")])
con.commit()
check("escaneo: dos filas con el mismo jugador en la tabla F1 son un hallazgo (y las fundidas no)",
      escaneo._duplicados([{"jugadorId": 1, "nombre": "Y. Guzmán"}, {"jugadorId": 2, "nombre": "Y. Guzman"},
                           {"jugadorId": 3, "nombre": "J. Peña", "idsAlternos": [4]},
                           {"jugadorId": 4, "nombre": "J. Pena"}]) == ["«Y. Guzmán» 1 y «Y. Guzman» 2"])
_ahora = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
# 887 (31/10/2026): lo marcado `posibleMismoQue` ya está cubierto y dos ids que
# compartieron una hoja son dos personas (los dos «T. Palacios» de Estudiantes)
_dos = [{"jugadorId": 311360, "nombre": "T. Palacios"}, {"jugadorId": 206984, "nombre": "T. Palacios"}]
check("887: dos homónimos que compartieron una hoja no son un hallazgo; sin esa prueba, sí",
      escaneo._duplicados(_dos, lambda a, b: True) == [] and len(escaneo._duplicados(_dos, lambda a, b: False)) == 1)
check("887: el par marcado posibleMismoQue por la tabla F1 ya está cubierto",
      escaneo._duplicados([{**_dos[0], "posibleMismoQue": 206984}, {**_dos[1], "posibleMismoQue": 311360}],
                          lambda a, b: False) == [])
_pre = escaneo._pre({"fixtureId": 12, "partido": "Santos vs Palmeiras", "fecha": "2026-10-28", "hora": "22:30",
                     "equipoA": "Santos", "equipoB": "Palmeiras", "conflicto": "Santos también juega el 28/10",
                     "dt": {"a": {"nombre": "X", "fiable": True}, "b": None}}, _ahora)
_ch = {(h["chequeo"], h.get("lado")) for h in _pre}
check("escaneo: el sancionado, el DT sin confirmar y el doble partido salen como hallazgos",
      ("sancion", "a") in _ch and ("dt-sin-confirmar", "b") in _ch and ("dos-partidos", None) in _ch
      and ("dt-sin-confirmar", "a") not in _ch, _pre)
# jugados: el 11 con parte, sin ninguna versión del once antes del pitazo y con eventos
from backend.analisis import parte as _parte  # noqa: E402
with _parte._conectar() as _c:
    _c.execute("INSERT INTO parte_cowork (fixture_id, fecha, parte_json, creado_en, actualizado_en) "
               "VALUES (11, '2026-10-25', '{}', '2026-10-24', '2026-10-24')")
    _c.execute("INSERT INTO parte_cowork (fixture_id, fecha, parte_json, creado_en, actualizado_en) "
               "VALUES (20, '2026-10-25', '{}', '2026-10-24', '2026-10-24')")
con.execute("INSERT INTO alineaciones_versiones VALUES (20, ?, '4-4-2', '2026-10-25 21:00:00')", (CAR,))
con.commit()
_post, _n = escaneo._post(72, datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc))
_cp = {(h["chequeo"], h["fixtureId"]) for h in _post}
check("escaneo: partido con parte jugado sin once antes del pitazo → once-tarde (y el que lo tuvo, no)",
      ("once-tarde", 11) in _cp and ("once-tarde", 20) not in _cp and _n == 2, (_post, _n))
# 953/941: si la ficha post-partido se selló SIN alineaciones (la API no las dio
# nunca: Copa del Rey con clubes de Tercera), no es un once tarde
con.execute("CREATE TABLE IF NOT EXISTS fichas_meta (fixture_id INTEGER PRIMARY KEY, capturado_en TEXT, "
            "alineaciones INTEGER, eventos INTEGER, stats INTEGER)")
con.execute("INSERT OR REPLACE INTO fichas_meta VALUES (11, '2026-10-26 03:00:00', 0, 12, 0)")
con.commit()
_post2, _ = escaneo._post(72, datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc))
check("953: con la ficha sellada sin alineaciones el partido no sale como once-tarde",
      ("once-tarde", 11) not in {(h["chequeo"], h["fixtureId"]) for h in _post2}, _post2)
check("escaneo: todos los chequeos tienen título, área, severidad y la regla que cuidan",
      all({"titulo", "area", "severidad", "regla"} <= set(v) for v in escaneo.CHEQUEOS.values()))

# ── EL PESO: la base no se recorre de más ────────────────────────────────────
from backend import db as _dbm  # noqa: E402
_n = {"q": 0}
_q0, _q1 = _dbm.query, _dbm.query_one


def _cq(*a, **k):
    _n["q"] += 1
    return _q0(*a, **k)


_dbm.query = _cq
_n["q"] = 0
sanciones.de_fixture(33)
_antes = _n["q"]
# cinco partidos más de la temporada, con tarjetas: las consultas NO crecen con ellos
for k in range(5):
    con.execute("INSERT INTO fixtures VALUES (?, ?, 'FT', '', ?, 2026, ?, ?, ?)",
                (40 + k, f"2026-09-{10 + k:02d} 20:00:00", BRA, f"Regular Season - {20 + k}", ATL, PAL))
    con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
                "VALUES (?, 10, 'Card', 'Yellow Card', ?, 'Otro', 99)", (40 + k, ATL))
con.commit()
_n["q"] = 0
sanciones.de_fixture(33)
check("peso: las consultas de las sanciones no crecen con los partidos de la temporada (sin N+1)",
      _n["q"] == _antes, (_antes, _n["q"]))
_veces = {"n": 0}
_df0 = sanciones.de_fixture


def _df(fid):
    _veces["n"] += 1
    return _df0(fid)


sanciones.de_fixture = _df
escaneo._pre({"fixtureId": 33, "partido": "Vasco vs Atlético-MG", "fecha": "2026-10-30", "hora": "22:00",
              "tieneParte": True, "dt": {}}, _ahora)
check("peso: el escaneo calcula las sanciones UNA vez por partido (la tabla F1 y la alerta las reciben)",
      _veces["n"] == 1, _veces)
sanciones.de_fixture = _df0
_dbm.query = _q0
check("el escaneo se guarda unos minutos (la segunda llamada sale de la caché)",
      escaneo.CACHE_S >= 300 and "fresco" in escaneo.escanear.__code__.co_varnames)

# 919/920 (Almirón, Peirano): la roja al DT —sin id, nombre del banco— no es un
# jugador sancionado: va aparte, en `cuerpoTecnico`, y la agenda lo marca
con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
            "VALUES (20, 88, 'Card', 'Red Card', ?, 'Pablo Peirano', NULL)", (CAR,))
con.execute("INSERT INTO alineaciones VALUES (20, ?, '4-4-2', 'Pablo Peirano', 52722, 'Bryan Castillo', 8, 'M', '3:2', 1)",
            (CAR,))
con.commit()
s21b = sanciones.de_fixture(21)["a"]
check("919: la roja al DT no entra en `sancionados` (Castillo sí) y va en `cuerpoTecnico`",
      [x["nombre"] for x in s21b["sancionados"]] == ["Bryan Castillo"]
      and [x["nombre"] for x in s21b.get("cuerpoTecnico") or []] == ["Pablo Peirano"]
      and s21b["cuerpoTecnico"][0]["tipo"] == "expulsion_dt", s21b)
from backend.analisis.parte import _dt_con_expulsion
_dts = _dt_con_expulsion(21, {"a": {"nombre": "Pablo Peirano"}, "b": None})
check("920: el DT de la agenda trae `expulsado` cuando viene de una roja; el otro lado queda igual",
      (_dts["a"].get("expulsado") or {}).get("nombre") == "Pablo Peirano" and _dts["b"] is None, _dts)

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
