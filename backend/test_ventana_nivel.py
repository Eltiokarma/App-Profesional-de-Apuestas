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

check("1165: Táchira en «Pueblo Nuevo» (otro venue_id, nombre recortado) no es neutral",
      not vn.cancha_neutral(_TAC, "Pueblo Nuevo", "2026-11-03T22:00:00", fixture_id=90421))
check("1165: Mushuc Runa en «Estadio del Mushuc Runa Sporting Club» (otro venue_id) no es neutral",
      not vn.cancha_neutral(_MUS, "Estadio del Mushuc Runa Sporting Club", _F, fixture_id=90520))
check("1165: misma_sede — recortado y ampliado sí; dos estadios distintos o solo palabras genéricas, no",
      vn.misma_sede("Pueblo Nuevo", "Estadio Polideportivo de Pueblo Nuevo")
      and not vn.misma_sede("Stade Louis-Achille", "Stade Pierre-Aliker")
      and not vn.misma_sede("Estadio Municipal", "Estadio Nacional")
      and not vn.misma_sede("PSC Arena", "Stadio Benito Stirpe"))

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
