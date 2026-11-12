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
BRA, VEN, COPA = 71, 299, 73   # 299 = Venezuela (281 es la Liga 1 de Perú, con regla desde la 1067)


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

# 1313 (Samsunspor): una amarilla sin jugador no se suma a nadie y se dice
con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
            "VALUES (32, 96, 'Card', 'Yellow Card', ?, NULL, NULL)", (ATL,))
con.commit()
s33j = sanciones.de_fixture(33)
check("1313: la amarilla sin jugador no suma a nadie y viaja en `sinJugador`",
      "sinJugador" in s33j["b"] and "1 amarilla" in s33j["b"]["sinJugador"]
      and all(a["nombre"] for a in s33j["b"]["amarillas"]), s33j["b"])
con.execute("DELETE FROM fixture_eventos WHERE fixture_id=32 AND minuto=96")
con.commit()

# 1224 (Kortrijk, M. Fofana 551229 en los eventos y 515771 en la hoja): la
# amarilla con otro id es del jugador de la hoja de ese partido
con.execute("UPDATE fixture_eventos SET jugador_id=99398 WHERE fixture_id=30 AND jugador_id=30398")
con.execute("INSERT INTO alineaciones VALUES (30, ?, '4-4-2', 'DT', 30398, 'Vitor Hugo', 3, 'D', '2:2', 1)", (ATL,))
con.commit()
n33i = {x["jugadorId"]: x for x in sanciones.de_fixture(33)["b"]["sancionados"]}
check("1224: la amarilla con otro id en el evento suma al jugador de la hoja (3.ª, sancionado)",
      30398 in n33i and n33i[30398]["amarillas"] == 3 and 99398 not in n33i, n33i)
con.execute("UPDATE fixture_eventos SET jugador_id=30398 WHERE fixture_id=30 AND jugador_id=99398")
con.execute("DELETE FROM alineaciones WHERE fixture_id=30")
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
# 1255: sin cuota es hallazgo solo cuando el refresco (<= SAD_REFRESCO_VENTANA_HORAS) ya pasó
con.execute("CREATE TABLE IF NOT EXISTS odds_history (fixture_id INTEGER, captured_at TEXT)")
con.commit()
_c7 = {h["chequeo"] for h in escaneo._pre({"fixtureId": 13, "partido": "Fortaleza vs Medellín", "fecha": "2026-10-28",
                                          "hora": "19:30", "equipoA": "Fortaleza", "equipoB": "Medellín"}, _ahora)}
_c4 = {h["chequeo"] for h in escaneo._pre({"fixtureId": 13, "partido": "Fortaleza vs Medellín", "fecha": "2026-10-28",
                                          "hora": "16:00", "equipoA": "Fortaleza", "equipoB": "Medellín"}, _ahora)}
from backend import app as _app  # noqa: E402
check("1255: a 7,5 h el refresco de cuotas todavía no lo pidió (no es hallazgo); a 4 h sin cuota, sí",
      "sin-cuotas" not in _c7 and "sin-cuotas" in _c4
      and escaneo.HORAS_CUOTAS < int(_app.REFRESCO_VENTANA_H), (_c7, _c4, escaneo.HORAS_CUOTAS))
# 1333: el clásico con estadio compartido es un chequeo INFORMATIVO (no se deposita);
# sin la sede en la base (esta no tiene venue_id) no se afirma
check("1333: `sede-compartida` es informativo y sin la sede en la base no suena",
      escaneo.CHEQUEOS["sede-compartida"].get("informativo") and ("sede-compartida", None) not in _ch)
from backend.analisis import ventana_nivel as _vn  # noqa: E402
_sc = _vn.sede_compartida
try:
    _vn.sede_compartida = lambda h, a, antes: "Estadio Víctor Agustín Ugarte" if (h, a) == (SAN, PAL) else None
    _h1333 = [h for h in escaneo._pre({"fixtureId": 12, "partido": "Santos vs Palmeiras", "fecha": "2026-10-28",
                                       "hora": "22:30", "equipoA": "Santos", "equipoB": "Palmeiras"}, _ahora)
              if h["chequeo"] == "sede-compartida"]
finally:
    _vn.sede_compartida = _sc
check("1333: con la sede compartida, el escaneo lo dice una vez por partido (sin lado) con el estadio",
      len(_h1333) == 1 and "Ugarte" in _h1333[0]["detalle"] and "lado" not in _h1333[0], _h1333)
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
# 1231 (05/11/2026, Cúcuta–Santa Fe): la primera versión del once llegó DENTRO de
# la ventana tardía del ciclo en vivo (el ciclo lo pedía y la API lo publicó
# después del pitazo): causa decidida, no hallazgo. Horas después, sí.
from backend.ingesta.en_vivo import XI_VENTANA_TARDE_MIN as _VT  # noqa: E402
with _parte._conectar() as _c:
    for _fx in (9031, 9032):
        _c.execute("INSERT INTO parte_cowork (fixture_id, fecha, parte_json, creado_en, actualizado_en) "
                   "VALUES (?, '2026-10-25', '{}', '2026-10-24', '2026-10-24')", (_fx,))
_base_fx = con.execute("SELECT * FROM fixtures WHERE id=11").fetchone()
_cols = [d[0] for d in con.execute("SELECT * FROM fixtures LIMIT 0").description]
for _fx in (9031, 9032):
    con.execute(f"INSERT INTO fixtures ({','.join(_cols)}) VALUES ({','.join('?' * len(_cols))})",
                [(_fx if c == "id" else _base_fx[i]) for i, c in enumerate(_cols)])
_pit = datetime.strptime(str(_base_fx[_cols.index("date")])[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
from datetime import timedelta as _td  # noqa: E402
# las dos con la ficha post-partido sellada CON alineaciones (1248: sin sellar no se juzga)
con.executemany("INSERT OR REPLACE INTO fichas_meta VALUES (?, '2026-10-26 03:00:00', 22, 12, 1)", [(9031,), (9032,)])
con.execute("INSERT INTO alineaciones_versiones VALUES (9031, ?, '4-3-3', ?)",
            (CAR, (_pit + _td(minutes=_VT - 10)).strftime("%Y-%m-%d %H:%M:%S")))
con.execute("INSERT INTO alineaciones_versiones VALUES (9032, ?, '4-3-3', ?)",
            (CAR, (_pit + _td(hours=4)).strftime("%Y-%m-%d %H:%M:%S")))
con.commit()
_post3, _ = escaneo._post(72, datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc))
_cp3 = {(h["chequeo"], h["fixtureId"]) for h in _post3}
check("1231: el once que la API publicó en la ventana tardía del ciclo no es once-tarde; el de horas después, sí",
      ("once-tarde", 9031) not in _cp3 and ("once-tarde", 9032) in _cp3, _post3)
# 1248 (Bolívar–Real Potosí): con la ficha post-partido sin sellar no se juzga el once
with _parte._conectar() as _c:
    _c.execute("INSERT INTO parte_cowork (fixture_id, fecha, parte_json, creado_en, actualizado_en) "
               "VALUES (9033, '2026-10-25', '{}', '2026-10-24', '2026-10-24')")
con.execute(f"INSERT INTO fixtures ({','.join(_cols)}) VALUES ({','.join('?' * len(_cols))})",
            [(9033 if c == "id" else _base_fx[i]) for i, c in enumerate(_cols)])
con.commit()
_post4, _ = escaneo._post(72, datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc))
check("1248: sin la ficha post-partido sellada el once-tarde no se juzga (nunca publicado y tarde no se distinguen)",
      ("once-tarde", 9033) not in {(h["chequeo"], h["fixtureId"]) for h in _post4}
      and ("once-tarde", 9032) in {(h["chequeo"], h["fixtureId"]) for h in _post4}, _post4)
check("1230: el hallazgo del escaneo trae la hora de Lima al lado de la UTC",
      bool(_post) and all(h.get("horaLima") for h in _post), _post[:1])
check("escaneo: todos los chequeos tienen título, área, severidad y la regla que cuidan",
      all({"titulo", "area", "severidad", "regla"} <= set(v) for v in escaneo.CHEQUEOS.values()))

# ── 1371: EL HOMÓNIMO CON EL ID CRUZADO (backend/partido_ajeno.py) ───────────
# Atlético Nacional (1137) tenía dos partidos de la Copa Perú (503) ante
# Juventud Palmeiras que son de otro club peruano con el mismo id de la API
from backend import partido_ajeno  # noqa: E402
NAC, JPA, ONC, COL, CPERU, LIBERTA = 1137, 20326, 1140, 239, 503, 13
con.executescript("CREATE TABLE IF NOT EXISTS leagues (id INTEGER PRIMARY KEY, name TEXT, country TEXT);")
con.executemany("INSERT OR REPLACE INTO leagues VALUES (?,?,?)",
                [(COL, "Primera A", "Colombia"), (CPERU, "Copa Peru", "Peru"),
                 (LIBERTA, "CONMEBOL Libertadores", "World"), (BRA, "Serie A", "Brazil")])
con.executemany("INSERT INTO teams VALUES (?,?)", [(NAC, "Atletico Nacional"), (JPA, "Juventud Palmeiras"),
                                                    (ONC, "Once Caldas")])
for k in range(4):
    con.execute("INSERT INTO fixtures VALUES (?, ?, 'FT', '', ?, 2026, 'Clausura - 1', ?, ?)",
                (70 + k, f"2026-10-{10 + 5 * k:02d} 23:00:00", COL, NAC if k % 2 else ONC, ONC if k % 2 else NAC))
con.execute("INSERT INTO fixtures VALUES (74, '2026-10-30 23:00:00', 'FT', '', ?, 2026, 'Final', ?, ?)",
            (LIBERTA, NAC, ONC))
con.execute("INSERT INTO fixtures VALUES (75, '2026-11-08 20:00:00', 'FT', '', ?, 2026, 'Etapa Nacional', ?, ?)",
            (CPERU, JPA, NAC))
con.execute("INSERT INTO fixtures VALUES (76, '2099-11-14 20:00:00', 'NS', '', ?, 2026, 'Etapa Nacional', ?, ?)",
            (CPERU, NAC, JPA))
con.execute("INSERT INTO fixtures VALUES (77, '2026-11-10 23:00:00', 'NS', '', ?, 2026, 'Clausura - 5', ?, ?)",
            (COL, ONC, NAC))
con.commit()
partido_ajeno._cache.clear()
check("1371: los partidos de la Copa Perú son ajenos a Nacional (Colombia) y la Libertadores no",
      partido_ajeno.ajenos_del_equipo(NAC) == {75, 76}, partido_ajeno.ajenos_del_equipo(NAC))
check("1371: el club peruano (todo en Perú) no tiene ajenos, y sin mayoría clara no se afirma nada",
      partido_ajeno.ajenos_del_equipo(JPA) == set()
      and partido_ajeno.ajenos([(1, COL, "Colombia"), (2, CPERU, "Peru")], set()) == (None, set()))
check("1371: un club que cruza la frontera de verdad (Toronto: MLS y Campeonato Canadiense) no se marca",
      partido_ajeno.ajenos([(i, 253, "USA") for i in range(10)] + [(99, 952, "Canada")], set())[1] == set())
check("1371/1378: el escaneo lo marca (`partido-ajeno`, informativo desde el 12/11: se cerraba siempre por diseño) en el lado de Nacional",
      escaneo.CHEQUEOS["partido-ajeno"].get("informativo")
      and [(h["chequeo"], h["lado"]) for h in escaneo._pre(
          {"fixtureId": 77, "partido": "Once Caldas vs Atletico Nacional", "fecha": "2026-11-10", "hora": "23:00",
           "equipoA": "Once Caldas", "equipoB": "Atletico Nacional"}, _ahora) if h["chequeo"] == "partido-ajeno"]
      == [("partido-ajeno", "b"), ("partido-ajeno", "b")])

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

# 958 (Cole Palmer): en Inglaterra la roja de la Premier se cumple en la Copa de la Liga
con.executemany("INSERT INTO fixtures VALUES (?,?,?,'',?,2026,?,?,?)", [
    (90, "2026-10-24 14:00:00", "FT", 39, "Regular Season - 9", 49, 50),
    (91, "2026-10-28 19:00:00", "FT", 48, "Round of 16", 49, 51),
    (92, "2026-11-01 14:00:00", "NS", 39, "Regular Season - 10", 49, 52)])
con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
            "VALUES (90, 80, 'Card', 'Red Card', 49, 'Cole Palmer', 152982)")
con.commit()
check("958: la roja de la Premier ya cumplida en la Copa de la Liga no suspende el siguiente de la Premier",
      not sanciones.de_fixture(92)["a"]["sancionados"], sanciones.de_fixture(92)["a"])
check("958: sin el partido de copa en medio, sí suspende",
      sanciones.del_equipo(49, {"id": 91, "date": "2026-10-28 19:00:00", "league_id": 48, "league_season": 2026,
                                "league_round": "Round of 16"})["sancionados"])
# 971: el mismo evento repetido no es otra amarilla
con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
                "VALUES (?, ?, 'Card', 'Yellow Card', ?, ?, ?)", [(30, 44, ATL, "Dup", 777), (30, 44, ATL, "Dup", 777)])
con.commit()
_am = {a["nombre"]: a["amarillas"] for a in sanciones.de_fixture(33)["b"]["amarillas"]}
check("971: la amarilla duplicada en los eventos cuenta una vez", _am.get("Dup") == 1, _am)
check("1011: sin la regla de la competición lo dice (`sinRegla`)",
      "sinRegla" in sanciones.de_fixture(21)["a"] and "sinRegla" not in sanciones.de_fixture(12)["a"])
# 969/959: la baja sin id casa por la fila de la tabla y la nota se lee de `notas`
from backend.analisis import f1_base as _f969  # noqa: E402
_s969 = {"a": {"sancionados": [{"jugadorId": 449509, "nombre": "Juma Bah", "detalle": "roja", "tipo": "roja"}]}, "b": {}}
_p969 = {"equipos": {"a": {"fuera": [{"nombre": "Abdulay Bah", "estado": "baja"}],
                           "plantel": [{"jugadorId": 449509, "nombre": "Abdulay Bah"}]}, "b": {}}}
_p959 = {"equipos": {"a": {"fuera": [], "plantel": [], "notas": {"B": "Juma Bah juega: la sanción se apeló"}}, "b": {}}}
check("969/959: la baja sin id que nombra la fila del mismo id apaga la alerta; la nota en `notas.B` también",
      _f969.alertas_sancion(_p969, {"id": 1}, {"a": "Augsburg"}, _s969) == []
      and _f969.alertas_sancion(_p959, {"id": 1}, {"a": "Augsburg"}, _s969) == [])

# 1043 (I. Tona): en el umbral se dice si suspende o si ya cumplió
_v33 = next(a for a in sanciones.de_fixture(33)["b"]["amarillas"] if a["jugadorId"] == 30398)
con.execute("UPDATE fixtures SET status_short='FT' WHERE id=33")
con.execute("INSERT INTO fixtures VALUES (34, '2026-11-03 22:00:00', 'NS', '', ?, 2026, 'Regular Season - 34', ?, ?)",
            (BRA, ATL, PAL))
con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
            "VALUES (33, 50, 'Card', 'Yellow Card', ?, 'Otro', 999)", (ATL,))
con.commit()
_v34 = next(a for a in sanciones.de_fixture(34)["a"]["amarillas"] if a["jugadorId"] == 30398)
check("1043: la 3.ª amarilla en el último partido suspende; un partido después, ya está cumplida",
      _v33.get("ciclo") == "suspende" and _v34.get("ciclo") == "cumplido"
      and not any(x["jugadorId"] == 30398 for x in sanciones.de_fixture(34)["a"]["sancionados"]), (_v33, _v34))

# 1080 (Monzón, Atlas, 1551020) y 1135 (F. Chamorro, 1505551): la tarjeta se
# verifica con la regla del fútbol y las stats de la ficha
MX, ATS, RIV = 262, 2283, 2314
con.executescript("""
    CREATE TABLE fixture_stats (fixture_id INTEGER NOT NULL, team_id INTEGER NOT NULL, clave TEXT, valor TEXT);
    CREATE TABLE plantel_actual (team_id INTEGER, player_id INTEGER, nombre TEXT);
""")
con.executemany("INSERT INTO fixtures VALUES (?,?,?,'',?,2026,?,?,?)", [
    (101 + k, f"2026-09-{5 + 7 * k:02d} 20:00:00", "FT", MX, f"Apertura - {k + 1}", ATS, RIV) for k in range(4)]
    + [(106, "2026-10-20 20:00:00", "NS", MX, "Apertura - 5", ATS, RIV)])
_ev = [(101 + k, 30, "Card", "Yellow Card", ATS, "Florián Monzón", 196743) for k in range(3)]
_ev += [(104, 90, "Card", "Yellow Card", ATS, "Florián Monzón", 196743),
        (104, 95, "Card", "Yellow Card", ATS, "Florián Monzón", 196743),
        # 1135: amarilla mejorada por el VAR sin su roja y con las stats en contra; Figueroa con upgrade + roja
        (104, 61, "Card", "Yellow Card", ATS, "Felipe Chamorro", 274563),
        (104, 61, "Var", "Card upgrade confirmed", ATS, "Felipe Chamorro", 274563),
        (104, 48, "Var", "Card upgrade confirmed", ATS, "G. Figueroa", 537295),
        (104, 48, "Card", "Red Card", ATS, "G. Figueroa", 537295)]
con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
                "VALUES (?,?,?,?,?,?,?)", _ev)
con.executemany("INSERT INTO fixture_stats VALUES (?,?,?,?)",
                [(101 + k, ATS, "Red Cards", "0") for k in range(3)] + [(104, ATS, "Red Cards", "1")])
con.commit()
_s106 = sanciones.de_fixture(106)["a"]
_am106 = {a["nombre"]: a["amarillas"] for a in _s106["amarillas"]}
_sn = {x["nombre"]: x["tipo"] for x in _s106["sancionados"]}
check("1080: dos amarillas al mismo jugador sin roja (90' y 90+5) cuentan UNA: 4, no 5, y no suspende",
      _am106.get("Florián Monzón") == 4 and "Florián Monzón" not in _sn, (_am106, _sn))
check("1135: el upgrade con su roja es UNA roja; el upgrade sin roja y con las stats en contra no es roja",
      _sn.get("G. Figueroa") == "roja" and "Felipe Chamorro" not in _sn and _am106.get("Felipe Chamorro") == 1,
      (_sn, _am106))
# con las stats que traen una roja de más, la segunda amarilla es la doble amarilla y el upgrade, una roja
con.execute("UPDATE fixture_stats SET valor='3' WHERE fixture_id=104")
con.commit()
_s106 = sanciones.de_fixture(106)["a"]
_sn = {x["nombre"]: x["tipo"] for x in _s106["sancionados"]}
check("1080/1135: con las stats sosteniendo las rojas que faltan, doble amarilla y roja del VAR",
      _sn.get("Florián Monzón") == "doble_amarilla" and _sn.get("Felipe Chamorro") == "roja"
      and _sn.get("G. Figueroa") == "roja", _sn)
con.execute("UPDATE fixture_stats SET valor='1' WHERE fixture_id=104")

# 1101 (Artur William Costa, 1645530): la roja sin id a alguien que no está en
# el plantel ni en la hoja es del cuerpo técnico; con el nombre de un jugador, no
con.executemany("INSERT INTO plantel_actual VALUES (?,?,?)",
                [(ATS, 196743, "Florián Monzón"), (ATS, 2405, "José Vargas")])
con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
                "VALUES (104, ?, 'Card', 'Red Card', ?, ?, NULL)", [(19, ATS, "Artur William Costa"),
                                                                   (70, ATS, "José Vargas")])
con.execute("UPDATE fixture_stats SET valor='3' WHERE fixture_id=104")
con.commit()
_s106 = sanciones.de_fixture(106)["a"]
_sn = {x["nombre"]: x["tipo"] for x in _s106["sancionados"]}
_ct = {x["nombre"]: x["tipo"] for x in _s106.get("cuerpoTecnico") or []}
check("1101: la roja sin id fuera del plantel va en `cuerpoTecnico`; la del jugador sin id sigue en `sancionados`",
      _ct == {"Artur William Costa": "expulsion_cuerpo_tecnico"} and _sn.get("José Vargas") == "roja"
      and "Artur William Costa" not in _sn, (_sn, _ct))
_dts = _dt_con_expulsion(106, {"a": {"nombre": "Benjamín Mora"}, "b": None})
check("1101: el DT de la agenda trae `expulsado` con la roja del cuerpo técnico",
      (_dts["a"].get("expulsado") or {}).get("nombre") == "Artur William Costa", _dts)
# 1126: la tabla F1 dice que no hay regla (y lleva el cuerpo técnico aparte)
_t = _f969._con_sanciones({"candidatos": []}, sanciones.de_fixture(21)["a"])
_t106 = _f969._con_sanciones({"candidatos": []}, _s106)
check("1126: sin regla, la tabla F1 trae `amarillasSinRegla`; con regla, no; y `cuerpoTecnico` viaja",
      "amarillasSinRegla" in _t and "amarillasSinRegla" not in _t106
      and [x["nombre"] for x in _t106.get("cuerpoTecnico") or []] == ["Artur William Costa"], (_t, _t106))

# EFE v1.10 (08/11/2026): la UEFA de la 2026/27 suspende a la 4.ª y a cada par
# siguiente (Škriniar 1635658, Lepinjica 1635745, Marlon Gomes 1635723 jugaron
# con «la 3.ª»); las amarillas de la previa no viajan y vencen tras cuartos
check("UEFA 2026/27: la 3.ª amarilla no suspende, la 4.ª sí, la 5.ª no, la 6.ª sí",
      [sanciones.suspende(2, n, 2026) for n in (3, 4, 5, 6)] == [False, True, False, True])
check("UEFA 2025/26 y antes: la regla vieja, a la 3.ª y a cada impar",
      [sanciones.suspende(3, n, 2025) for n in (3, 4, 5)] == [True, False, True])
check("UEFA: la previa es su propia fase (las rondas de clasificación y el play-off anterior a la fase liga)",
      {sanciones._fase(r, 848) for r in ("1st Qualifying Round", "3rd Qualifying Round", "Play-offs")} == {"previa"})
check("UEFA: la fase liga y la eliminatoria hasta cuartos cuentan juntas; semis y final, aparte",
      {sanciones._fase(r, 2) for r in ("League Stage - 4", "Knockout Round Play-offs", "Round of 16", "Quarter-finals")}
      == {""} and sanciones._fase("Semi-finals", 2) == sanciones._fase("Final", 2) == "semis")
check("fuera de la UEFA, «1st»/«2nd» siguen separando torneos cortos",
      sanciones._fase("Apertura - 3") == "apertura" and sanciones._fase("2nd Phase - 1", 128) == "2nd")

# 1067 (10/11/2026): la UEFA de punta a punta con la base. Las amarillas de la
# previa NO cuentan (P. Previa: 1 en la previa + 3 en la fase liga = 3, no
# suspende) y la 4.ª de la fase liga sí (P. Cuarta)
_UE = 9001
con.executemany("INSERT INTO fixtures VALUES (?,?,?,'',?,2026,?,?,?)", [
    (700, "2026-08-05 19:00:00", "FT", 2, "3rd Qualifying Round", _UE, 9002),
    (701, "2026-08-20 19:00:00", "FT", 2, "Play-offs", 9003, _UE),
    (702, "2026-09-16 19:00:00", "FT", 2, "League Stage - 1", _UE, 9004),
    (703, "2026-09-30 19:00:00", "FT", 2, "League Stage - 2", 9005, _UE),
    (704, "2026-10-21 19:00:00", "FT", 2, "League Stage - 3", _UE, 9006),
    (706, "2026-11-04 19:00:00", "FT", 2, "League Stage - 4", 9007, _UE),
    (707, "2026-11-25 19:00:00", "NS", 2, "League Stage - 5", _UE, 9008)])
con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
                "VALUES (?, ?, 'Card', 'Yellow Card', ?, ?, ?)",
                [(700, 30, _UE, "P. Previa", 501), (703, 30, _UE, "P. Previa", 501), (704, 30, _UE, "P. Previa", 501),
                 (706, 30, _UE, "P. Previa", 501)]
                + [(f, 50, _UE, "P. Cuarta", 502) for f in (702, 703, 704, 706)])
con.commit()
_ue = sanciones.de_fixture(707)["a"]
_ues = {x["jugadorId"] for x in _ue["sancionados"]}
_uea = {a["jugadorId"]: a["amarillas"] for a in _ue["amarillas"]}
check("1067 UEFA: la 4.ª amarilla de la fase liga suspende", 502 in _ues and _uea.get(502) == 4, _ue)
check("1067 UEFA: la amarilla de la previa no cuenta (3 de la fase liga no suspenden)",
      501 not in _ues and _uea.get(501) == 3, _ue)

# 1067: Liga 1 Perú, cada 5 POR ETAPA (art. 185.1 y 185.2). O. Núñez (1549539)
# con la 5.ª del Clausura suspende; con 3 del Apertura + 2 del Clausura, no
_PE = 9101
con.executemany("INSERT INTO fixtures VALUES (?,?,?,'',?,2026,?,?,?)",
                [(720 + i, f"2026-04-{10 + i:02d} 20:00:00", "FT", 281, f"Apertura - {i}", _PE, 9200 + i)
                 for i in (1, 2, 3)]
                + [(730 + i, f"2026-08-{10 + i:02d} 20:00:00", "FT", 281, f"Clausura - {i}", _PE, 9210 + i)
                   for i in range(1, 6)]
                + [(736, "2026-08-20 20:00:00", "NS", 281, "Clausura - 6", _PE, 9216)])
con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador, jugador_id) "
                "VALUES (?, ?, 'Card', 'Yellow Card', ?, ?, ?)",
                [(730 + i, 40, _PE, "O. Núñez", 601) for i in range(1, 6)]
                + [(720 + i, 60, _PE, "Por Etapa", 602) for i in (1, 2, 3)]
                + [(734, 60, _PE, "Por Etapa", 602), (735, 60, _PE, "Por Etapa", 602)])
con.commit()
_pe = sanciones.de_fixture(736)["a"]
_pes = {x["jugadorId"] for x in _pe["sancionados"]}
check("1067 Perú: la 5.ª amarilla del Clausura suspende (cada 5, art. 185.1)", 601 in _pes and _pe["regla"], _pe)
check("1067 Perú: las del Apertura no viajan al Clausura (art. 185.2): 3 + 2 no suspenden", 602 not in _pes, _pe)

# 1067: Eredivisie, KNVB art. 29 lid 2 (julio 2026): la 5.ª, la 10.ª y desde la 11.ª cada una
check("1067 Eredivisie: suspenden la 5.ª, 10.ª, 11.ª y 12.ª; no la 4.ª, 6.ª, 7.ª ni 9.ª",
      [sanciones.suspende(88, n, 2026) for n in (5, 10, 11, 12)] == [True] * 4
      and not any(sanciones.suspende(88, n, 2026) for n in (4, 6, 7, 9)))
check("1067: Ligue 1, Bélgica, Grecia, Süper Lig, Colombia y Ecuador siguen sin regla (no confirmadas)",
      not any(l in sanciones.UMBRALES for l in (61, 144, 197, 203, 239, 242)))

# 1332 (08/11/2026, Santa Fe–Pasto): el 1X2 del mercado salta 25+ puntos en 24 h y la base no lo ve
def _filas1332(*capturas):
    out = []
    for t, (h, d, a) in capturas:
        out += [{"t": t, "v": "Home", "odd": h}, {"t": t, "v": "Draw", "odd": d}, {"t": t, "v": "Away", "odd": a}]
    return out


_q1332 = escaneo.saddb.query
try:
    escaneo.saddb.query = lambda base, sql, args=(): _filas1332(("2026-10-27 13:00:00", (1.66, 3.8, 5.0)),
                                                                ("2026-10-28 11:00:00", (1.08, 9.0, 21.0)))
    _s1332 = escaneo._salto_mercado(1549862, _ahora)
    escaneo.saddb.query = lambda base, sql, args=(): _filas1332(("2026-10-27 13:00:00", (1.66, 3.8, 5.0)),
                                                                ("2026-10-28 11:00:00", (1.55, 4.0, 5.5)))
    _s1332b = escaneo._salto_mercado(1549862, _ahora)
    escaneo.saddb.query = lambda base, sql, args=(): _filas1332(("2026-10-28 11:00:00", (1.08, 9.0, 21.0)))
    _s1332c = escaneo._salto_mercado(1549862, _ahora)
finally:
    escaneo.saddb.query = _q1332
check("1332: local de 1,66 a 1,08 en 24 h es salto del mercado; un movimiento chico o una sola captura, no",
      "1,66".replace(",", ".") in _s1332 and "1.08" in _s1332 and _s1332b == "" and _s1332c == "",
      (_s1332, _s1332b, _s1332c))
check("1332: el chequeo mercado-salto existe y se deposita (no es informativo)",
      "mercado-salto" in escaneo.CHEQUEOS and not escaneo.CHEQUEOS["mercado-salto"].get("informativo"))

# 1371, los lectores (al final: las columnas de goles cambian la forma de la tabla)
for _col in ("goals_home", "goals_away", "fulltime_home", "fulltime_away", "venue_city"):
    con.execute(f"ALTER TABLE fixtures ADD COLUMN {_col}")
con.execute("UPDATE fixtures SET goals_home=1, goals_away=0 WHERE id BETWEEN 70 AND 75")
con.commit()
from backend import jugadores as _jug, calendario as _cal  # noqa: E402
_ant = dtp_cowork._anteriores(NAC, "2026-11-10 23:00:00", 1)
check("1371: el partido anterior del DTP es el de la Libertadores, no el 2-2 de la Copa Perú",
      [r["id"] for r in _ant] == [74], [r["id"] for r in _ant])
check("1371: F2 cuenta el descanso desde el último partido de Nacional (11 días, no 2)",
      _jug._congestion(NAC, "2026-11-10 23:00:00").get("diasDescanso") == 11,
      _jug._congestion(NAC, "2026-11-10 23:00:00"))
check("1371: la vuelta de la Copa Perú no es un próximo del calendario de Nacional",
      76 not in {p.get("fixtureId") for p in _cal.calendario_de(NAC, 10)}, _cal.calendario_de(NAC, 10))

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
