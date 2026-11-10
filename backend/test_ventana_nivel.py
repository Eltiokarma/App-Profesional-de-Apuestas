"""De qué está hecho el nivel del motor (backend/analisis/ventana_nivel.py) — sin red.

Konyaspor 0-4 Galatasaray (30/10/2026, incidencia 860): el motor dio 41 % al
14.º y la ventana de 20 del nivel del líder traía seis amistosos de
pretemporada y tres de Champions (no eran la causa: ver ventana_nivel.py). Este test arma esa ventana y comprueba que
se cuente bien (con la deduplicación del pipeline), que la fiabilidad de μ
baje a «media» con 3+ amistosos y no con menos, y que el escaneo lo marque
como chequeo informativo.

    python -m backend.test_ventana_nivel
"""
import os
import sqlite3
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="sad-ventana-")
os.environ["SAD_DATA_DIR"] = _TMP
os.environ.setdefault("SAD_SIN_HILOS", "1")

fallos = 0
GAL, KON = 645, 607


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
con.executescript("""
    CREATE TABLE leagues (id INTEGER PRIMARY KEY, name TEXT, country TEXT, logo TEXT, flag TEXT, season INTEGER);
    CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT, status_long TEXT, league_id INTEGER,
        league_season INTEGER, home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
        fulltime_home INTEGER, fulltime_away INTEGER);
""")
con.executemany("INSERT INTO leagues (id, name, country) VALUES (?,?,?)",
                [(203, "Süper Lig", "Turkey"), (667, "Friendlies Clubs", "World"), (2, "UEFA Champions League", "World")])
# la ventana real de Galatasaray antes del 30/10: 11 de liga, 6 amistosos, 3 de Champions
partidos = [("2026-05-09", 203, 4, 2), ("2026-05-17", 203, 0, 1), ("2026-07-17", 667, 5, 1), ("2026-07-24", 667, 0, 2),
            ("2026-07-27", 667, 0, 3), ("2026-08-02", 667, 3, 3), ("2026-08-08", 667, 1, 2), ("2026-08-14", 203, 2, 2),
            ("2026-08-21", 203, 4, 0), ("2026-08-29", 203, 3, 2), ("2026-09-04", 203, 3, 2), ("2026-09-09", 2, 1, 3),
            ("2026-09-13", 203, 1, 0), ("2026-09-19", 203, 0, 4), ("2026-10-02", 667, 3, 3), ("2026-10-09", 203, 3, 1),
            ("2026-10-13", 2, 1, 4), ("2026-10-17", 203, 1, 0), ("2026-10-21", 2, 4, 2), ("2026-10-26", 203, 2, 1)]
for i, (d, liga, gf, gc) in enumerate(partidos):
    con.execute("INSERT INTO fixtures VALUES (?,?, 'FT', 'Match Finished', ?, 2026, ?, ?, ?, ?, ?, ?)",
                (1000 + i, d + " 18:00:00", liga, GAL, 9000 + i, gf, gc, gf, gc))
# un partido viejo que ya quedó fuera de la ventana, y el MISMO partido con dos ids (pipeline.sin_duplicados)
con.execute("INSERT INTO fixtures VALUES (999, '2026-04-01 18:00:00', 'FT', '', 667, 2026, ?, 8999, 1, 0, 1, 0)", (GAL,))
con.execute("INSERT INTO fixtures VALUES (2000, '2026-10-26 18:00:00', 'FT', '', 203, 2026, ?, 9019, 2, 1, 2, 1)", (GAL,))
# el partido analizado (NS) y Konyaspor con una ventana de liga
con.execute("INSERT INTO fixtures VALUES (3000, '2026-10-30 17:00:00', 'NS', '', 203, 2026, ?, ?, NULL, NULL, NULL, NULL)",
            (KON, GAL))
for i in range(20):
    con.execute("INSERT INTO fixtures VALUES (?, ?, 'FT', '', ?, 2026, ?, ?, 1, 1, 1, 1)",
                (4000 + i, f"2026-{5 + i // 4:02d}-{1 + (i % 4) * 7:02d} 18:00:00", 667 if i < 2 else 203, KON, 9500 + i))
con.commit()

from backend.analisis import ventana_nivel as vn  # noqa: E402

c = vn.composicion(GAL, "2026-10-30T17:00:00Z")
check("860: la ventana de Galatasaray son 20, con 6 amistosos y 3 de Champions",
      c and c["partidos"] == 20 and c["amistosos"] == 6 and c["internacionales"] == 3 and c["otros"] == 11, c)
check("…el mismo partido con dos ids entra una vez y el viejo queda fuera (desde el 09/05)",
      c["desde"] == "2026-05-09" and c["hasta"] == "2026-10-26", c)
check("el texto dice «6 amistosos y 3 internacionales de 20»", vn.texto(c) == "6 amistosos y 3 internacionales de 20",
      vn.texto(c))
ck = vn.composicion(KON, "2026-10-30T17:00:00Z")
check("Konyaspor con 2 amistosos en la ventana", ck["amistosos"] == 2 and ck["internacionales"] == 0, ck)

alta = {"nivel": "alta", "nota": "Sin desviaciones detectadas para esta liga."}
f = vn.fiabilidad_con_ventana(alta, {"local": ck, "visitante": c}, {"local": "Konyaspor", "visitante": "Galatasaray"})
check("860: con 6 amistosos en un lado, la fiabilidad de μ baja de «alta» a «media», con la nota y la liga guardada",
      f["nivel"] == "media" and f["porVentana"] is True and "Galatasaray: 6 amistosos" in f["nota"]
      and f["notaLiga"] == alta["nota"] and f["ventana"]["visitante"].startswith("6 amistosos"), f)
f2 = vn.fiabilidad_con_ventana(alta, {"local": ck, "visitante": ck})
check("con 2 amistosos (debajo del umbral) queda «alta» y solo informa la composición",
      f2["nivel"] == "alta" and "porVentana" not in f2 and f2["ventana"]["local"] == "2 amistosos de 20", f2)
baja = {"nivel": "baja", "nota": "Bases distintas."}
f3 = vn.fiabilidad_con_ventana(baja, {"local": c, "visitante": ck})
check("una «baja» no sube: queda baja y la nota suma la ventana", f3["nivel"] == "baja" and "Además" in f3["nota"], f3)
check("sin composición (base vieja) no se afirma nada",
      vn.fiabilidad_con_ventana(alta, {"local": None, "visitante": None})["nivel"] == "alta")

# el escaneo lo marca como chequeo informativo (no se deposita como incidencia)
from datetime import datetime, timezone  # noqa: E402
from backend.analisis import escaneo  # noqa: E402
h = escaneo._pre({"fixtureId": 3000, "partido": "Konyaspor vs Galatasaray", "fecha": "2026-10-30", "hora": "17:00",
                  "dt": {"a": {"fiable": True}, "b": {"fiable": True}}}, datetime(2026, 10, 30, 12, tzinfo=timezone.utc))
nv = [x for x in h if x["chequeo"] == "nivel-con-amistosos"]
check("escaneo: `nivel-con-amistosos` marca a Galatasaray (lado b) y no a Konyaspor",
      len(nv) == 1 and nv[0]["lado"] == "b" and "6 amistosos" in nv[0]["detalle"], nv)
check("…y es informativo: el mantenimiento no lo deposita", escaneo.CHEQUEOS["nivel-con-amistosos"].get("informativo"))
# 02/11/2026 (prevención): las listas para el parte que se cerraban siempre por
# diseño (sancion 1146, sin-plantel 1147, dt-sin-confirmar 1144) son informativas;
# lo que cobra un parte se sigue depositando.
check("escaneo: sancion, sin-plantel y dt-sin-confirmar son informativos",
      all(escaneo.CHEQUEOS[k].get("informativo") for k in ("sancion", "sin-plantel", "dt-sin-confirmar")))
check("…y sancion-sin-declarar, once-tarde, dos-partidos y jugador-duplicado no",
      not any(escaneo.CHEQUEOS[k].get("informativo")
              for k in ("sancion-sin-declarar", "once-tarde", "dos-partidos", "jugador-duplicado")))

# 991 (01/11/2026, decisión del usuario): ventana corta o vieja → baja; cancha neutral se dice
_corta = {"partidos": 7, "amistosos": 0, "internacionales": 0, "otros": 7, "desde": "2021-08-01",
          "hasta": "2022-05-01", "completa": False}
_f991 = vn.fiabilidad_con_ventana(alta, {"local": _corta, "visitante": None}, fecha="2026-10-31")
check("991: 7 partidos en la ventana, el último de 2022 → fiabilidad «baja» con el motivo",
      _f991["nivel"] == "baja" and "solo 7 partidos" in _f991["nota"], _f991)
_vieja = {**_corta, "partidos": 20, "completa": True}
_f991b = vn.fiabilidad_con_ventana(alta, {"local": _vieja, "visitante": None}, fecha="2026-10-31")
check("991: 20 partidos pero el último de hace más de un año → «baja»",
      _f991b["nivel"] == "baja" and "hace" in _f991b["nota"], _f991b)
_f991c = vn.fiabilidad_con_ventana(alta, {"local": None, "visitante": None}, fecha="2026-10-31", neutral=True)
check("991: en cancha neutral la fiabilidad lo dice (canchaNeutral) y «alta» baja a «media»",
      _f991c.get("canchaNeutral") and _f991c["nivel"] == "media" and "neutral" in _f991c["nota"], _f991c)

# 1090 (03/11/2026, x10): el mismo estadio con otro nombre NO es cancha neutral.
# Universidad Católica «San Carlos de Apoquindo» / «Claro Arena», Frosinone
# «Stadio Benito Stirpe» → «PSC Arena», Levadiakos «Levadia Stadium» → «Levadia
# Municipal Stadium» (el mismo venue_id): /predicciones marcaba canchaNeutral.
_c = sqlite3.connect(os.path.join(_TMP, "sad.db"))
_c.execute("ALTER TABLE fixtures ADD COLUMN venue_id INTEGER")
_c.execute("ALTER TABLE fixtures ADD COLUMN venue_name TEXT")
_FRO, _LEV, _UC, _FRA = 512, 957, 2994, 9991


def _sede_fx(fid, equipo, dia, vid, nombre):
    _c.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id, venue_id, "
               "venue_name) VALUES (?,?,?,?,?,?,?,?)", (fid, f"2026-{dia} 18:00:00", "FT", 203, equipo, 1, vid, nombre))


# Frosinone: 11 en el Benito Stirpe, 6 sin nombre, 2 ya en «PSC Arena»; sin venue_id
for _i in range(11):
    _sede_fx(90000 + _i, _FRO, f"0{1 + _i % 8}-1{_i % 9}", None, "Stadio Benito Stirpe")
for _i in range(6):
    _sede_fx(90020 + _i, _FRO, f"09-2{_i}", None, "")
_sede_fx(90030, _FRO, "10-16", None, "PSC Arena")
_sede_fx(90031, _FRO, "10-29", None, "PSC Arena")
_sede_fx(90032, _FRO, "11-01", None, "PSC Arena")
# Levadiakos: 16 en «Levadia Stadium» (venue 777), hoy «Levadia Municipal Stadium» con el mismo id
for _i in range(16):
    _sede_fx(90100 + _i, _LEV, f"0{1 + _i % 9}-0{1 + _i % 9}", 777, "Levadia Stadium")
_sede_fx(90120, _LEV, "11-01", 777, "Levadia Municipal Stadium")
# UC: el nombre viejo y el nuevo, mismo id
for _i in range(10):
    _sede_fx(90200 + _i, _UC, f"0{1 + _i % 9}-0{1 + _i % 9}", 555, "Claro Arena" if _i % 2 else "San Carlos de Apoquindo")
_sede_fx(90220, _UC, "11-01", 555, "San Carlos de Apoquindo")
# el caso de 991 sigue: 10 en su estadio, hoy en otro id que nunca usó
for _i in range(10):
    _sede_fx(90300 + _i, _FRA, f"0{1 + _i % 9}-0{1 + _i % 9}", 100, "Stade Pierre-Aliker")
_sede_fx(90320, _FRA, "10-31", 200, "Stade Louis-Achille")
# el 991 real era de la Coupe de France (66): ese partido va con su copa
_c.execute("UPDATE fixtures SET league_id=66 WHERE id=90320")
# 1207: Olimpia de local en «Manuel Ferreira» (el nombre viejo del Osvaldo
# Domínguez Dibb, otro id), en la liga paraguaya; y el mismo caso en copa
_OLI = 1182
for _i in range(17):
    _sede_fx(90600 + _i, _OLI, f"0{1 + _i % 9}-0{1 + _i % 9}", 600, "Estadio Osvaldo Dominguez Dibb")
_sede_fx(90620, _OLI, "11-04", 601, "Estadio Manuel Ferreira")
_c.execute("UPDATE fixtures SET league_id=252 WHERE id=90620")
_sede_fx(90621, _OLI, "11-04", 602, "Estadio Hipotético")
_c.execute("UPDATE fixtures SET league_id=66 WHERE id=90621")
# 1165 (reapareció tras la 1090): Táchira en «Pueblo Nuevo» con otro venue_id
# que el «Estadio Polideportivo de Pueblo Nuevo» de siempre; Mushuc Runa igual
_TAC, _MUS = 2807, 1162
for _i in range(12):
    _sede_fx(90400 + _i, _TAC, f"0{1 + _i % 9}-0{1 + _i % 9}", 300, "Estadio Polideportivo de Pueblo Nuevo")
_sede_fx(90420, _TAC, "10-27", 301, "Pueblo Nuevo")
_sede_fx(90421, _TAC, "11-03", 301, "Pueblo Nuevo")
for _i in range(12):
    _sede_fx(90500 + _i, _MUS, f"0{1 + _i % 9}-0{1 + _i % 9}", 400, "Estadio COAC Mushuc Runa")
_sede_fx(90520, _MUS, "11-01", 401, "Estadio del Mushuc Runa Sporting Club")
_c.commit()
_c.close()
_F = "2026-11-01T18:00:00"
check("1090: Frosinone en «PSC Arena», donde ya jugó de local 2 veces, no es neutral (sin venue_id)",
      not vn.cancha_neutral(_FRO, "PSC Arena", _F, fixture_id=90032))
check("1090: Levadiakos con el estadio renombrado (mismo venue_id) no es neutral",
      not vn.cancha_neutral(_LEV, "Levadia Municipal Stadium", _F, fixture_id=90120))
check("1090: …ni sin pasar el fixture si el nombre es el mismo normalizado («LEVADIA  stadium»)",
      not vn.cancha_neutral(_LEV, "LEVADIA  stadium", _F))
check("1090: Universidad Católica en San Carlos / Claro Arena (mismo id) no es neutral",
      not vn.cancha_neutral(_UC, "San Carlos de Apoquindo", _F, fixture_id=90220))
check("991 sigue: el local en un estadio de otro id que nunca usó SÍ es neutral",
      vn.cancha_neutral(_FRA, "Stade Louis-Achille", "2026-10-31T18:00:00", fixture_id=90320))
check("991 sigue: …también solo por el nombre",
      vn.cancha_neutral(_FRA, "Stade Louis-Achille", "2026-10-31T18:00:00"))

check("1207: Olimpia en «Manuel Ferreira» (su estadio con el nombre viejo, otro id) en la LIGA no es neutral",
      not vn.cancha_neutral(_OLI, "Estadio Manuel Ferreira", "2026-11-04T22:00:00", fixture_id=90620))
check("1207: un estadio que nunca usó en un partido de COPA sigue pudiendo ser neutral (991)",
      vn.cancha_neutral(_OLI, "Estadio Hipotético", "2026-11-04T22:00:00", fixture_id=90621))
check("1165: Táchira en «Pueblo Nuevo» (otro venue_id, nombre recortado) no es neutral",
      not vn.cancha_neutral(_TAC, "Pueblo Nuevo", "2026-11-03T22:00:00", fixture_id=90421))
check("1165: Mushuc Runa en «Estadio del Mushuc Runa Sporting Club» (otro venue_id) no es neutral",
      not vn.cancha_neutral(_MUS, "Estadio del Mushuc Runa Sporting Club", _F, fixture_id=90520))
check("1165: misma_sede — recortado y ampliado sí; dos estadios distintos o solo palabras genéricas, no",
      vn.misma_sede("Pueblo Nuevo", "Estadio Polideportivo de Pueblo Nuevo")
      and not vn.misma_sede("Stade Louis-Achille", "Stade Pierre-Aliker")
      and not vn.misma_sede("Estadio Municipal", "Estadio Nacional")
      and not vn.misma_sede("PSC Arena", "Stadio Benito Stirpe"))

# 1360 (10/11/2026, reaparición de la 1207 en copa): Amorebieta–Logroñés en
# Urritxe, Copa del Rey R128. Su historia de local en la base es la Segunda
# 2023-24 en Lezama; después bajó a una categoría no ingestada (solo un
# amistoso en Urritxe en 2024 y uno sin sede en 2026). La sede «habitual» de
# hace dos años no es la de hoy: sin 5 partidos de local del último año, no
# se afirma neutral.
_AMO = 9380
_c = sqlite3.connect(os.path.join(_TMP, "sad.db"))
for _i in range(18):
    _c.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id, venue_id, "
               "venue_name) VALUES (?,?,?,?,?,?,?,?)",
               (90700 + _i, f"2023-{9 + _i % 4:02d}-{1 + _i:02d} 18:00:00", "FT", 141, _AMO, 1, 700,
                "Instalaciones de Lezama Campo 2"))
_c.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id, venue_id, venue_name) "
           "VALUES (90720, '2024-08-09 18:00:00', 'FT', 667, ?, 1, 701, 'Campo Municipal de Urritxe')", (_AMO,))
_c.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id, venue_id, venue_name) "
           "VALUES (90721, '2026-08-08 18:00:00', 'FT', 667, ?, 1, NULL, '')", (_AMO,))
_c.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id, venue_id, venue_name) "
           "VALUES (90722, '2026-11-10 19:00:00', 'NS', 143, ?, 1, 701, 'Campo Municipal de Urritxe')", (_AMO,))
_c.commit()
_c.close()
check("1360: Amorebieta en Urritxe (copa) con la sede «habitual» de hace dos años en la base no es neutral",
      not vn.cancha_neutral(_AMO, "Campo Municipal de Urritxe", "2026-11-10T19:00:00", fixture_id=90722))
check("1360: …tampoco sin la fecha (la toma del fixture) ni solo por el nombre",
      not vn.cancha_neutral(_AMO, "Campo Municipal de Urritxe", None, fixture_id=90722)
      and not vn.cancha_neutral(_AMO, "Campo Municipal de Urritxe", "2026-11-10T19:00:00"))
check("1360: la misma historia vista en 2024 (sede del último año) sí podía dar neutral en copa",
      vn.cancha_neutral(_AMO, "Estadio Hipotético", "2024-06-01T18:00:00"))


# 1251 (06/11/2026): Coventry, recién ascendido, con su Championship de abril-mayo
# en la ventana del nivel; la liga de hoy es la del partido analizado (Premier)
COV = 1346
con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
con.executemany("INSERT OR IGNORE INTO leagues (id, name, country) VALUES (?,?,?)",
                [(39, "Premier League", "England"), (40, "Championship", "England"), (48, "League Cup", "England")])
_cov = [("2026-04-0%d" % (i + 1), 40) for i in range(7)] + [("2026-08-28", 48)] \
    + [("2026-09-%02d" % (i + 1), 39) for i in range(12)]
for i, (d, liga) in enumerate(_cov):
    con.execute("INSERT INTO fixtures VALUES (?,?, 'FT', 'Match Finished', ?, 2026, ?, ?, 1, 1, 1, 1, NULL, NULL)",
                (7000 + i, d + " 15:00:00", liga, COV, 9700 + i))
con.execute("INSERT INTO fixtures VALUES (7100, '2026-11-07 15:00:00', 'NS', '', 39, 2026, ?, 9800, NULL, NULL, NULL, NULL, "
            "NULL, NULL)",
            (COV,))
con.commit()
cc = vn.composicion(COV, "2026-11-07T15:00:00Z")
check("1251: la ventana del ascendido cuenta 7 de otra liga (Championship); la copa no cuenta como otra liga",
      cc and cc["otraLiga"] == 7 and cc["otraLigaNombre"] == "Championship" and cc["otros"] == 20, cc)
check("1251: el texto lo dice", vn.texto(cc) == "7 de otra liga (Championship) de 20", vn.texto(cc))
check("1251: Galatasaray (toda la liga es la de hoy) no trae otra liga", c["otraLiga"] == 0, c)
check("1251: solo se cuenta: sin amistosos, la fiabilidad «alta» no baja por la otra liga",
      vn.fiabilidad_con_ventana(alta, {"local": cc})["nivel"] == "alta")


# 1104 (10/11/2026, decisión del usuario): el rival del reventón con la
# diferencia de nivel a favor lleva la marca si alguna ventana trae 3+ amistosos
# (Strasbourg 1552808: −3 por «rival muy favorito» con 6 amistosos). Solo marca.
_fams = {"total": {"rival": {"aFavor": 1.36, "favorito": "muy favorito"}, "riesgo": {"puntos": -2, "nivel": "bajo"}},
         "local": {"rival": {"aFavor": 0.2, "favorito": "no"}}, "visita": {"rival": None}}
vn.marcar_rival(_fams, ck, c)
_m = _fams["total"]["rival"].get("nivelConAmistosos")
check("1104: «muy favorito» con 6 amistosos en la ventana del rival lleva nivelConAmistosos con los dos conteos",
      _m and _m["equipo"] == 2 and _m["rival"] == 6 and "6 amistosos" in _m["nota"] and "reserva" in _m["nota"], _m)
check("1104: los puntos y el riesgo no se tocan",
      _fams["total"]["riesgo"] == {"puntos": -2, "nivel": "bajo"} and _fams["total"]["rival"]["aFavor"] == 1.36)
check("1104: donde la diferencia no puntúa (favorito «no») no se marca",
      "nivelConAmistosos" not in _fams["local"]["rival"])
_fams2 = {"total": {"rival": {"aFavor": 1.1, "favorito": "muy favorito"}}}
vn.marcar_rival(_fams2, ck, ck)
check("1104: con 2 amistosos de cada lado (debajo del umbral) no hay marca",
      "nivelConAmistosos" not in _fams2["total"]["rival"])

# 1108 (10/11/2026, decisión del usuario): los goles acotados llevan el mismo
# porVentana que fiabilidadMu (Kasımpaşa–Beşiktaş 1584453, 6 amistosos en el local)
from backend.analisis import goles as _goles  # noqa: E402
_fx = {"id": 3000, "date": "2026-10-30 17:00:00", "home_team_id": GAL, "away_team_id": KON,
       "home_name": "Galatasaray", "away_name": "Konyaspor"}
_v = _goles._ventana(_fx, {"local": c, "visitante": ck})
check("1108: con 6 amistosos en el local, golesAcotados trae porVentana, la ventana y la nota",
      _v.get("porVentana") is True and _v["ventana"]["local"].startswith("6 amistosos")
      and "Galatasaray: 6 amistosos" in _v["notaVentana"], _v)
check("1108: es el MISMO porVentana que fiabilidadMu",
      _v.get("porVentana") == vn.fiabilidad_con_ventana({}, {"local": c, "visitante": ck}).get("porVentana"))
check("1108: debajo del umbral no se marca", _goles._ventana(_fx, {"local": ck, "visitante": ck}) == {})
check("1108: sin la ventana pasada, se lee de la base (la misma marca)",
      _goles._ventana(_fx).get("porVentana") is True)
_ac = {"local": {"equipo": "Galatasaray"}, "visita": {"equipo": "Konyaspor"}, "marcadorAcotado": {}, "masProbables": [],
       "masDe2_5": 0.5, "ambosMarcan": 0.5, "modelo": {}, "nota": "", **_v}
check("1108: la marca viaja también desde el equipo (la tarjeta de /burbujas)",
      _goles.desde_equipo(_ac, False).get("porVentana") is True
      and "porVentana" not in _goles.desde_equipo({k: x for k, x in _ac.items() if k not in _v}, True))
# 1333 (10/11/2026, decisión del usuario): ESTADIO COMPARTIDO. Nacional Potosí–
# Real Potosí, los dos de local en el Víctor Agustín Ugarte (1645538): el motor
# sumó la localía (49 % local contra 37 % del mercado). Blooming–Oriente en el
# Tahuichi, con otro venue_id y el nombre recortado. Y dos «Monumental» de
# ciudades distintas, que NO son el mismo estadio.
con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
con.execute("ALTER TABLE fixtures ADD COLUMN venue_city TEXT")
_NAC, _REA, _BLO, _ORI, _UNI, _RIV, _NUE = 3901, 3902, 3903, 3904, 3905, 3906, 3907


def _local(fid, equipo, dia, vid, nombre, ciudad=None, liga=344):
    con.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id, venue_id, "
                "venue_name, venue_city) VALUES (?,?,?,?,?,?,?,?,?)",
                (fid, f"2026-{dia} 20:00:00", "FT", liga, equipo, 1, vid, nombre, ciudad))


for _i in range(8):
    _d = f"{3 + _i:02d}-1{_i % 9}"
    _local(95000 + _i, _NAC, _d, 900, "Estadio Víctor Agustín Ugarte", "Potosí")
    _local(95010 + _i, _REA, _d, 900, "Estadio Víctor Agustín Ugarte", "Potosí")
    _local(95020 + _i, _BLO, _d, 910, "Estadio Ramón Tahuichi Aguilera", "Santa Cruz de la Sierra")
    _local(95030 + _i, _ORI, _d, None, "Tahuichi Aguilera", None)
    _local(95040 + _i, _UNI, _d, 920, "Estadio Monumental", "Lima")
    _local(95050 + _i, _RIV, _d, 921, "Estadio Monumental", "Buenos Aires")
for _i in range(2):   # recién llegado: dos de local no alcanzan para afirmar su sede
    _local(95060 + _i, _NUE, f"10-0{1 + _i}", 900, "Estadio Víctor Agustín Ugarte", "Potosí")
con.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id, away_team_id, venue_id, "
            "venue_name) VALUES (1645538, '2026-11-08 20:00:00', 'NS', 344, ?, ?, 900, "
            "'Estadio Víctor Agustín Ugarte')", (_NAC, _REA))
con.commit()
con.close()
_F13 = "2026-11-08T20:00:00"
check("1333: Nacional Potosí y Real Potosí, mismo venue_id de local → estadio compartido",
      vn.sede_compartida(_NAC, _REA, _F13) == "Estadio Víctor Agustín Ugarte", vn.sede_compartida(_NAC, _REA, _F13))
check("1333: Blooming–Oriente, el Tahuichi con otro venue_id y el nombre recortado → compartido",
      bool(vn.sede_compartida(_BLO, _ORI, _F13)))
check("1333: dos «Estadio Monumental» de Lima y Buenos Aires (otro id, otra ciudad) NO son el mismo",
      vn.sede_compartida(_UNI, _RIV, _F13) is None)
check("1333: dos estadios distintos no se comparten", vn.sede_compartida(_NAC, _BLO, _F13) is None)
check("1333: con 2 partidos de local no se afirma la sede (ni que se comparta)",
      vn.sede_compartida(_NAC, _NUE, _F13) is None)
check("1333: lo de hace más de un año no es la sede de esta temporada",
      vn.sede_compartida(_NAC, _REA, "2028-01-01T00:00:00") is None)
_f13 = vn.fiabilidad_con_ventana(alta, {"local": None, "visitante": None}, compartida="Estadio Víctor Agustín Ugarte")
check("1333: la fiabilidad lo avisa (sedeCompartida), «alta» baja a «media» y la nota dice que la localía no aplica",
      _f13.get("sedeCompartida") == "Estadio Víctor Agustín Ugarte" and _f13["nivel"] == "media"
      and "estadio compartido" in _f13["nota"] and "no aplica" in _f13["nota"], _f13)
check("1333: sin sede compartida no aparece la marca",
      "sedeCompartida" not in vn.fiabilidad_con_ventana(alta, {"local": None, "visitante": None}))
_h13 = escaneo._pre({"fixtureId": 1645538, "partido": "Nacional Potosí vs Real Potosí", "fecha": "2026-11-08",
                     "hora": "20:00", "dt": {"a": {"fiable": True}, "b": {"fiable": True}}},
                    datetime(2026, 11, 8, 12, tzinfo=timezone.utc))
check("1333: el escaneo marca `sede-compartida` en el clásico de Potosí",
      any(x["chequeo"] == "sede-compartida" and "Ugarte" in x["detalle"] for x in _h13), _h13)

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
