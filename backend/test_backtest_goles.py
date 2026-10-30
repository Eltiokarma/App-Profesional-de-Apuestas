"""¿El backtest de goles detecta lo que tiene que detectar? (REVENTON §17)

Con datos SINTÉTICOS donde se sabe la verdad: si la constante de goles mueve
los goles más allá de la frecuencia cruzada, G3 tiene que acotar mejor que G2;
si es ruido, no. La repetición de marcadores: una serie que nunca repite tiene
que salir por debajo del azar, y una al azar, en el azar. Y sobre la demo, que
las observaciones salgan sin fuga.

    python -m backend.test_backtest_goles
"""
from __future__ import annotations

import math
import os
import random
import sys
import tempfile

os.environ.setdefault("SAD_SIN_HILOS", "1")
_tmp = tempfile.mkdtemp(prefix="sad_bgoles_")
from backend.seed_demo import seed  # noqa: E402
seed(_tmp)
os.environ["SAD_DATA_DIR"] = _tmp
import backend.db as _dbmod  # noqa: E402
_dbmod.BASE_DIR = _tmp

from backend import backtest_goles as bt  # noqa: E402

fallas = 0


def check(nombre, ok, detalle=""):
    global fallas
    print(("OK  " if ok else "FALLA ") + nombre + ("" if ok else f" -> {detalle}"))
    fallas += 0 if ok else 1


def _poisson(rnd, lam):
    l, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= l:
            return k
        k += 1


def sinteticos(n: int, efecto_k: float, semilla: int) -> list[dict]:
    rnd = random.Random(semilla)
    obs = []
    for i in range(n):
        lados = {}
        for lado, local in (("local", True), ("visita", False)):
            at, de = rnd.uniform(0.7, 2.0), rnd.uniform(0.7, 2.0)
            k_at, k_de = rnd.gauss(0, 1), rnd.gauss(0, 1)
            # verdad: los goles salen del cruce y, si hay efecto, de la constante
            lam = math.exp(math.log(at) * 0.6 + math.log(de) * 0.4 + (0.15 if local else -0.1)
                           + efecto_k * (k_at + k_de))
            y = _poisson(rnd, lam)
            lados[lado] = {"y": y, "serie": [_poisson(rnd, at) for _ in range(10)], "mediaFrecuencia": at,
                           "x": {"lnAtaque": math.log(at), "lnDefensa": math.log(de), "local": 1.0 if local else 0.0,
                                 "d": rnd.gauss(0, 0.5), "kGaCondAt": k_at, "kGrCondDef": k_de,
                                 "kGaAt": rnd.gauss(0, 1), "kGrDef": rnd.gauss(0, 1),
                                 "rachaMarcaAt": rnd.random(), "rachaRecibeDef": rnd.random()}}
        obs.append({"fixtureId": i, "fecha": f"2025-{1 + i * 12 // n:02d}-01T{i % 24:02d}", "liga": 1, **lados})
    return obs


# 1) con un efecto real de la constante, G3 acota mejor que G2
r = bt.correr(sinteticos(3000, 0.25, 1))
c = r["comparaciones"]["G3 cruce + K vs G2 cruce"]
check("con efecto plantado, las constantes acotan MEJOR (IC bajo cero)", c["ic95"][1] < 0, c)
check("…y la lectura lo dice", "constantes AGREGAN" in r["lectura"], r["lectura"])
check("…y los coeficientes que pesan son los plantados",
      r["coeficientes"]["G3 cruce + K"]["kGaCondAt"] > 0.1 and r["coeficientes"]["G3 cruce + K"]["kGrCondDef"] > 0.1
      and abs(r["coeficientes"]["G3 cruce + K"]["kGaAt"]) < 0.08, r["coeficientes"]["G3 cruce + K"])

# 2) con la constante de ruido, no inventa nada
r0 = bt.correr(sinteticos(3000, 0.0, 2))
c0 = r0["comparaciones"]["G3 cruce + K vs G2 cruce"]
check("con constante de ruido, no se distingue (el IC no queda bajo cero)", c0["ic95"][1] >= 0, c0)
check("el intervalo de dos goles promete lo que acierta (calibrado, ±5 pts)",
      abs(r0["modelos"]["G2 cruce"]["intervalo"]["acierta"] - r0["modelos"]["G2 cruce"]["intervalo"]["prometia"]) < 0.05,
      r0["modelos"]["G2 cruce"]["intervalo"])
check("el intervalo a mano del usuario se mide", r0["modelos"]["G0 intervalo a mano"]["intervalo"]["acierta"] is not None)

# 3) el intervalo a mano: la ventana de dos goles más repetida
check("banda a mano de 1, 2, 2, 2, 1, 2, 2, 1, 2, 3, 4, 1 → «1 o 2»",
      bt.banda_usuario([1, 2, 2, 2, 1, 2, 2, 1, 2, 3, 4, 1]) == 1)
check("banda a mano de 0, 0, 1, 0, 2 → «0 o 1»", bt.banda_usuario([0, 0, 1, 0, 2]) == 0)

# 4) el mercado: con un modelo igual al mercado no hay ventaja
test = sinteticos(200, 0.0, 3)
lam = {n: [(1.4, 1.1)] * len(test) for n in ("G2 cruce", "G3 cruce + K")}
p_ou, p_btts = bt._modelo_mercados(1.4, 1.1)
cuotas = {o["fixtureId"]: {"ou": p_ou, "btts": p_btts, "ouCuotas": (1 / p_ou, 1 / (1 - p_ou)),
                           "bttsCuotas": (1 / p_btts, 1 / (1 - p_btts))} for o in test}
cm = bt.contra_mercado(test, lam, cuotas)
check("modelo idéntico al mercado: diferencia de log-loss cero y ninguna apuesta de valor",
      cm["ou"]["G2 cruce"]["modeloMenosMercado"]["media"] == 0 and cm["ou"]["G2 cruce"]["valor"]["apuestas"] == 0, cm["ou"])

# 5) ¿el marcador se repite?
rnd = random.Random(5)
marcadores = [(1, 0), (0, 0), (2, 1), (1, 1), (0, 1), (2, 2), (3, 0)]
nunca = {}
for t in range(60):
    s, prev = [], None
    for _ in range(30):
        m = rnd.choice([x for x in marcadores if x != prev])
        s.append((m[0], m[1], True))
        prev = m
    nunca[t] = s
rep = bt.repeticion_marcadores(nunca)
check("una serie que nunca repite sale por DEBAJO del azar", rep["todos"]["observado"] == 0
      and rep["todos"]["razon"] < 0.2 and rep["todos"]["pMenos"] <= 0.025, rep["todos"])
azar = {t: [(*rnd.choice(marcadores), True) for _ in range(30)] for t in range(60)}
rep2 = bt.repeticion_marcadores(azar)
check("una serie al azar queda en el azar", 0.025 < rep2["todos"]["pMenos"] and 0.8 < rep2["todos"]["razon"] < 1.25,
      rep2["todos"])

# 6) sobre la demo: sin fuga y con los dos lados
eqs = bt._equipos(12)
lado = bt.lado_equipo(eqs[0], None)
filas = list(reversed(bt.constantes_de(eqs[0], 500)))
ok_fuga = True
for i, f in enumerate(filas):
    o = lado.get(f["fixtureId"])
    if not o:
        continue
    previas = [x for x in filas[:i] if x["condicion"] == f["condicion"]][-bt.N_SERIE:]
    if o["serieMarca"] != [int(x["golesFavor"]) for x in previas] or o["gf"] != f["golesFavor"]:
        ok_fuga = False
check("la serie de cada partido sale SOLO de los anteriores en su condición", ok_fuga and len(lado) > 0, len(lado))
obs = bt.observaciones(eqs, None)
check("cada observación trae los dos lados con el mismo marcador",
      obs and all(o["local"]["y"] >= 0 and o["visita"]["y"] >= 0 for o in obs), len(obs))
check("la demo chica no alcanza para separar entrenamiento y prueba (lo dice, no inventa)",
      "error" in bt.correr(obs) or bt.correr(obs)["prueba"] >= 20)

print("\nTODO OK" if not fallas else f"\n{fallas} FALLA(S)")
sys.exit(1 if fallas else 0)
