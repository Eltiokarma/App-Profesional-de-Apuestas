"""El backtest del nivel sin amistosos detecta un efecto real y no inventa uno (860).

Con datos SINTÉTICOS donde se sabe la verdad: equipos con una fuerza fija que
decide sus partidos oficiales y amistosos que salen AL AZAR (la pretemporada:
rotan y pierden con cualquiera). Si los amistosos ensucian el nivel, la
variante `sinAmistosos` tiene que acertar mejor en los partidos con 3+
amistosos en la ventana; sin amistosos en la base, las variantes son la misma.

    python -m backend.test_backtest_nivel_ventana
"""
import math
from datetime import datetime, timedelta
import os
import random
import sys
import tempfile

os.environ.setdefault("SAD_SIN_HILOS", "1")
_TMP = tempfile.mkdtemp(prefix="sad-btnv-")
from backend.seed_demo import seed  # noqa: E402
seed(_TMP)
os.environ["SAD_DATA_DIR"] = _TMP
import backend.db as _dbmod  # noqa: E402
_dbmod.BASE_DIR = _TMP

from backend import backtest_nivel_ventana as bt  # noqa: E402

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(("OK  " if cond else "FALLA ") + nombre + ("" if cond else f" -> {detalle}"))


def _pois(rnd, lam):
    l, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= l:
            return k
        k += 1


def sinteticos(con_amistosos: bool, semilla: int = 3):
    """36 equipos con fuerza fija; 6 temporadas de liga (ida y vuelta) y, si se
    pide, amistosos de pretemporada contra rivales de afuera: entre 0 y 8 por
    equipo, que se suelen perder."""
    rnd = random.Random(semilla)
    fuerza = {t: rnd.uniform(0.2, 2.8) for t in range(1, 37)}
    fx, fid = [], 1
    for anio in range(2010, 2026):
        dia = 0
        if con_amistosos:
            # como en la realidad, DESPAREJO: unos juegan muchos amistosos contra
            # rivales fuertes (y los pierden: rotan) y otros casi ninguno
            for t in fuerza:
                for k in range(rnd.choice((0, 0, 0, 7, 8, 8))):
                    fx.append((fid, f"{anio}-07-{1 + k * 3:02d} 18:00:00", t, 1000 + rnd.randrange(50),
                               _pois(rnd, 0.8), _pois(rnd, 1.7), "Match Finished", 667, anio))
                    fid += 1
        equipos = list(fuerza)
        for vuelta in range(2):
            for i, a in enumerate(equipos):
                for b in equipos[i + 1:]:
                    home, away = (a, b) if vuelta == 0 else (b, a)
                    dia += 1
                    fecha = (datetime(anio, 8, 1) + timedelta(hours=dia * 3)).strftime("%Y-%m-%d %H:%M:%S")
                    gl, gv = _pois(rnd, fuerza[home] * 1.1 + 0.15), _pois(rnd, fuerza[away] * 0.9 + 0.1)
                    fx.append((fid, fecha, home, away, gl, gv, "Match Finished", 39, anio))
                    fid += 1
    fx.sort(key=lambda r: (r[1], r[0]))
    return fx


obs, _ = bt.observaciones(sinteticos(True), None)
r = bt.evaluar(obs)
sub = r["porSubconjunto"]["conAmistosos"]
check("hay partidos con 3+ amistosos en la ventana", sub["n"] >= 30, sub)
ic = sub["reajustada"]["vsActual"]["sinAmistosos"]
check("con amistosos al azar, el nivel SIN amistosos acierta mejor (IC bajo cero) en esos partidos",
      ic["ic95"] and ic["ic95"][1] < 0, ic)
check("…y la lectura lo dice", "conAmistosos: sinAmistosos MEJORA" in r["lectura"], r["lectura"])

obs0, _ = bt.observaciones(sinteticos(False), None)
iguales = all(o["actual"]["d"] == o["sinAmistosos"]["d"] for o in obs0)
check("sin amistosos en la base, la variante sin amistosos ES la actual (no inventa diferencia)", iguales and obs0)

# sin fuga: cada nivel usado es de un partido ANTERIOR (nunca el retroactivo §2.2)
hist = bt.historias(sinteticos(True), {}, set())
f, n = bt.niveles_variante(hist[1], "actual")
check("los niveles del backtest arrancan en el partido nº 20 de cada historia (sin el retroactivo)",
      len(f) == len(hist[1]) - 19, (len(f), len(hist[1])))
o = obs[len(obs) // 2]
check("el caso muestra niveles y 1X2 por variante",
      set(bt.caso(obs, None, o["fixtureId"])) >= {"actual", "sinAmistosos", "sinAmistososNiInternacionales"})

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
