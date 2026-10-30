"""El backtest de la localía por liga detecta una diferencia real entre ligas y
no inventa una (30/10/2026, tras la incidencia 860).

Con datos SINTÉTICOS donde se sabe la verdad: tres ligas de 20 equipos con
fuerza fija y una localía DISTINTA en cada una (fuerte, media y nula). La
variante `porLiga` tiene que estimarlas en ese orden y acertar mejor el 1X2;
con la MISMA localía en las tres, el encogimiento las tiene que juntar y la
variante no puede salir mejor.

    python -m backend.test_backtest_localia_liga
"""
import math
from datetime import datetime, timedelta
import os
import random
import sys
import tempfile

os.environ.setdefault("SAD_SIN_HILOS", "1")
_TMP = tempfile.mkdtemp(prefix="sad-btll-")
from backend.seed_demo import seed  # noqa: E402
seed(_TMP)
os.environ["SAD_DATA_DIR"] = _TMP
import backend.db as _dbmod  # noqa: E402
_dbmod.BASE_DIR = _TMP

from backend import backtest_localia_liga as bt  # noqa: E402

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


def sinteticos(localia: dict[int, float], semilla: int = 5, temporadas: int = 8):
    """Por liga, 20 equipos con fuerza fija, ida y vuelta cada temporada. El
    local mete goles con λ·(1 + localía) y el visitante con λ·(1 − localía/2)."""
    rnd = random.Random(semilla)
    fx, fid = [], 1
    for liga, loc in localia.items():
        fuerza = {liga * 100 + t: rnd.uniform(0.5, 2.2) for t in range(20)}
        for anio in range(2014, 2014 + temporadas):
            equipos, hora = list(fuerza), 0
            for vuelta in range(2):
                for i, a in enumerate(equipos):
                    for b in equipos[i + 1:]:
                        home, away = (a, b) if vuelta == 0 else (b, a)
                        hora += 3
                        fecha = (datetime(anio, 8, 1) + timedelta(hours=hora)).strftime("%Y-%m-%d %H:%M:%S")
                        gl = _pois(rnd, fuerza[home] * 0.8 * (1 + loc))
                        gv = _pois(rnd, fuerza[away] * 0.8 * (1 - loc / 2))
                        fx.append((fid, fecha, home, away, gl, gv, "Match Finished", liga, anio))
                        fid += 1
    fx.sort(key=lambda r: (r[1], r[0]))
    return fx


# ── ligas con localías distintas: la tiene que ver y aprovechar ────────────
obs, _ = bt.observaciones(sinteticos({39: 0.45, 61: 0.2, 140: 0.0}), None)
r = bt.evaluar(obs)
loc = {x["liga"]: x["encogida"] for x in r["localiaEntrenamiento"]}
check("la localía estimada sale en el orden real (fuerte > media > nula)",
      loc.get(39, 0) > loc.get(61, 0) > loc.get(140, 0), loc)
ic = r["todos"]["vsGlobal"]["porLiga"]
check("con localías distintas, la localía por liga acierta mejor el 1X2 (IC bajo cero)",
      ic["ic95"] and ic["ic95"][1] < 0, ic)
check("…y la lectura lo dice", "todos: porLiga MEJORA" in r["lectura"], r["lectura"])
check("el encogimiento queda finito: hay variación real entre ligas",
      r["encogimiento"]["K"] is not None and r["encogimiento"]["tau"] > 0.05, r["encogimiento"])

# ── la misma localía en las tres: no puede inventar una diferencia ─────────
obs0, _ = bt.observaciones(sinteticos({39: 0.25, 61: 0.25, 140: 0.25}, semilla=11), None)
r0 = bt.evaluar(obs0)
ic0 = r0["todos"]["vsGlobal"]["porLiga"]
check("con la misma localía en todas, porLiga NO sale mejor (no inventa)",
      ic0["ic95"] and ic0["ic95"][1] >= 0, ic0)
enc = [x["encogida"] for x in r0["localiaEntrenamiento"]]
cru = [x["cruda"] for x in r0["localiaEntrenamiento"]]
check("…y el encogimiento las junta más que la estimación cruda",
      max(enc) - min(enc) <= max(cru) - min(cru) + 1e-9, (enc, cru))

# ── sin fuga y el caso ─────────────────────────────────────────────────────
check("la localía se estima SOLO con el entrenamiento (la prueba no la toca)",
      sum(x["n"] for x in r["localiaEntrenamiento"]) == r["entrenamiento"], r["entrenamiento"])
o = obs[-1]
rc = bt.evaluar(obs, casos=[o["fixtureId"]])
c = rc["casos"][0] if rc["casos"] else {}
check("el caso muestra la localía de su liga y el 1X2 en cada variante",
      set(c) >= {"global", "porLiga", "porLigaCruda", "produccion"} and "localia" in c.get("porLiga", {}), c)
check("el d de la variante es el d del motor con la localía de su liga en vez de la global",
      abs(c["porLiga"]["d"] - (c["global"]["d"] - bt.LOCALIA + c["porLiga"]["localia"])) < 2e-3, c)

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
