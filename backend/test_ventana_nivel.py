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

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
