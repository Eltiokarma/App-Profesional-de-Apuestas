"""¿El backtest de la burbuja en el 1X2 detecta lo que tiene que detectar?

Con datos SINTÉTICOS donde se sabe la verdad: si el riesgo mueve el resultado,
M2 tiene que mejorar a M1; si es ruido, no. Y sobre la demo, que las
observaciones salgan sin fuga y con los dos lados.

    python -m backend.test_backtest_1x2
"""
from __future__ import annotations

import math
import os
import random
import sys
import tempfile

os.environ.setdefault("SAD_SIN_HILOS", "1")
# la demo se siembra en una carpeta temporal (las .db no viajan en el repo)
_tmp = tempfile.mkdtemp(prefix="sad_b1x2_")
from backend.seed_demo import seed  # noqa: E402
seed(_tmp)
os.environ["SAD_DATA_DIR"] = _tmp
import backend.db as _dbmod  # noqa: E402
_dbmod.BASE_DIR = _tmp

from backend import backtest_burbuja_1x2 as bt  # noqa: E402

fallas = 0


def check(nombre, ok, detalle=""):
    global fallas
    print(("OK  " if ok else "FALLA ") + nombre + ("" if ok else f" -> {detalle}"))
    fallas += 0 if ok else 1


def sinteticos(n: int, efecto_riesgo: float, semilla: int, efecto_goles: float = 0.0) -> list[dict]:
    rnd = random.Random(semilla)
    obs = []
    for i in range(n):
        d = rnd.gauss(0, 0.6)
        rl = rnd.choice([0, 0, 0, 1, 2, 3, 5, -1, -2, -4]) * rnd.choice([1, -1])
        rv = rnd.choice([0, 0, 0, 1, 2, 3, 5, -1, -2, -4]) * rnd.choice([1, -1])
        racha_l, racha_v = rnd.gauss(0, 1), rnd.gauss(0, 1)
        ks = {f"{k}{lado}": rnd.gauss(0, 1) for k in bt._CLAVES_K for lado in "LV"}
        # verdad opcional: el local que viene anotando de local contra el visitante
        # que viene recibiendo de visita (el cruce de condiciones)
        cruce = efecto_goles * (ks["gaCondL"] + ks["grCondV"])
        # verdad: el riesgo con signo EMPUJA contra el lado que trae la racha
        zl = 0.3 + 1.6 * d - efecto_riesgo * rl + efecto_riesgo * rv + cruce
        zv = 0.0 - 1.6 * d + efecto_riesgo * rl - efecto_riesgo * rv - cruce
        el, ev = math.exp(zl), math.exp(zv)
        s = 1 + el + ev
        u = rnd.random()
        y = "L" if u < el / s else "V" if u < (el + ev) / s else "E"
        obs.append({"fixtureId": i, "fecha": f"2025-{1 + i * 12 // n:02d}-01T{i % 24:02d}", "liga": 1, "y": y,
                    "x": {"d": d, "d2": d * d, "rachaL": racha_l, "rachaV": racha_v,
                          "riesgoL": -rl, "riesgoV": rv,
                          "extremoL": 0, "extremoV": 0, **ks},
                    "riesgoAlto": abs(rl) >= 2 or abs(rv) >= 2, "conExtremo": False})
    obs.sort(key=lambda o: o["fecha"])
    return obs


def main() -> int:
    bt.BOOTSTRAP = 200
    r = bt.correr(sinteticos(4000, 0.25, 1))
    c = r["comparaciones"]
    check("con un efecto real del riesgo, M2 mejora a M1 (IC por debajo de 0)",
          c["M2 + riesgo vs M1 + racha"]["logLoss"]["ic95"][1] < 0, c["M2 + riesgo vs M1 + racha"])
    check("y la lectura dice que agrega", "AGREGA" in r["lectura"], r["lectura"])
    check("el motor solo ya acierta más que el azar (d manda)", r["modelos"]["M0 motor"]["acierto"] > 0.45,
          r["modelos"]["M0 motor"])

    r = bt.correr(sinteticos(4000, 0.0, 2))
    ic = r["comparaciones"]["M2 + riesgo vs M1 + racha"]["logLoss"]["ic95"]
    check("con el riesgo como ruido, M2 no se distingue de M1 (el IC cruza 0 o empeora)", ic[1] >= 0, ic)
    check("y la lectura no lo lleva a la fórmula", "no agrega" in r["lectura"], r["lectura"])
    check("la prueba son los partidos MÁS NUEVOS (corte temporal, no al azar)", r["corte"] >= r["desde"]
          and r["hasta"] >= r["corte"], (r["desde"], r["corte"], r["hasta"]))

    lect = r["lectura"]
    check("con las K como ruido, M6 no se distingue del motor y la lectura no las lleva a la fórmula",
          r["comparaciones"]["M6 + todas las K vs M0 motor"]["logLoss"]["ic95"][1] >= 0
          and "las constantes no agregan" in lect, (r["comparaciones"]["M6 + todas las K vs M0 motor"], lect))
    r = bt.correr(sinteticos(4000, 0.0, 4, efecto_goles=0.3))
    c = r["comparaciones"]
    check("con un cruce real de K de goles por condición, M5 y M6 mejoran al motor",
          c["M5 + K goles vs M0 motor"]["logLoss"]["ic95"][1] < 0 and c["M6 + todas las K vs M0 motor"]["logLoss"]["ic95"][1] < 0,
          (c["M5 + K goles vs M0 motor"], c["M6 + todas las K vs M0 motor"]))
    check("y la lectura dice que las constantes agregan", "las constantes AGREGAN" in r["lectura"], r["lectura"])
    co = r["modelos"]["M6 + todas las K"]["coefLocal"]
    check("los coeficientes que pesan son los del cruce (gaCondL y grCondV), no el ruido",
          min(co["gaCondL"], co["grCondV"]) > 2 * max(abs(co[k]) for k in co if k not in ("d", "d2", "gaCondL", "grCondV")), co)
    check("con pocos partidos no inventa un resultado", "error" in bt.correr(sinteticos(30, 0.2, 3)))

    # sobre la demo: observaciones reales del pipeline, sin fuga
    equipos = bt._equipos(12, None)
    lados = bt.lado_equipo(equipos[0], None) if equipos else {}
    check("la demo da lados con nivel previo y resultado", bool(lados) and all(
        o["nivel"] is not None and o["gf"] is not None for o in lados.values()), len(lados))
    obs = bt.observaciones(equipos, None)
    check("cada partido trae los DOS lados (un fixture no aparece dos veces)",
          len({o["fixtureId"] for o in obs}) == len(obs) and len(obs) > 0, len(obs))
    check("las observaciones van ordenadas por fecha", [o["fecha"] for o in obs] == sorted(o["fecha"] for o in obs))
    check("las K de la demo entran con los dos lados y la de la condición de hoy",
          all(all(k + lado in o["x"] for k in bt._CLAVES_K for lado in "LV") for o in obs), obs[0]["x"] if obs else None)
    check("el riesgo solo viaja con racha abierta (sin burbuja, 0)",
          all(not (o["x"]["riesgoL"] and not o["x"]["rachaL"]) for o in obs))

    print("\nTODO OK" if not fallas else f"\n{fallas} FALLAS")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
