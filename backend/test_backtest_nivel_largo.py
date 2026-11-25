"""El backtest del nivel largo: reconstruye el nivel de §2.1 solo con lo anterior,
detecta que una fuerza de fondo (que el nivel de 20 no ve entero) se predice
mejor con el largo, no inventa ventaja donde la fuerza es solo la reciente, y
el grupo de los grandes no se elige con el futuro.

    python -m backend.test_backtest_nivel_largo
"""
import random
import sys

from backend import backtest_favorito_falla as ff
from backend import backtest_nivel_largo as nl

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _fecha(d: int) -> str:
    return f"{2021 + d // 336}-{1 + (d // 28) % 12:02d}-{1 + d % 28:02d}T18:00:00Z"


def simular(fondo: float, semilla: int, equipos: int = 40, jornadas: int = 330) -> dict:
    """Cada equipo tiene una fuerza de FONDO fija (peso `fondo`) y una fuerza que cambia
    cada 15 jornadas. Con fondo alto, el promedio largo la ve y el de 20 no del todo."""
    rnd = random.Random(semilla)
    base = {t: rnd.gauss(0, 1) for t in range(1, equipos + 1)}
    hist = {t: {"filas": [], "niveles": []} for t in base}
    ahora = dict.fromkeys(base, 0.0)
    fx = 1
    for j in range(jornadas):
        if j % 15 == 0:
            ahora = {t: rnd.gauss(0, 1) for t in base}
        orden = list(base)
        rnd.shuffle(orden)
        for k in range(0, len(orden) - 1, 2):
            L, V = orden[k], orden[k + 1]
            d = fondo * (base[L] - base[V]) + (1 - fondo) * (ahora[L] - ahora[V]) + 0.3
            pl = 1 / (1 + 2.7 ** (-1.2 * d + 0.4))
            pv = 1 / (1 + 2.7 ** (1.2 * d + 0.4))
            x = rnd.random()
            gl, gv = (2, 0) if x < pl else (0, 2) if x < pl + pv else (1, 1)
            fecha = _fecha(j * 3)
            for t, c, gf, gc in ((L, "Local", gl, gv), (V, "Visita", gv, gl)):
                hist[t]["filas"].append({"fixtureId": fx, "fecha": fecha, "condicion": c, "rivalId": V if t == L else L,
                                         "ligaId": 1, "golesFavor": gf, "golesContra": gc})
            fx += 1
    for t, h in hist.items():          # el nivel de §2.1, escrito DESPUÉS de cada partido
        f = h["filas"]
        for i in range(19, len(f)):
            w = f[i - 19:i + 1]
            p = sum(nl._pts(x) for x in w) / 20
            u = w[-5:]
            gf, gc = sum(x["golesFavor"] for x in u), sum(x["golesContra"] for x in u)
            h["niveles"].append({"fecha": f[i]["fecha"], "nivel": 1 + p + ((gf - gc) / (gf + gc) if gf + gc else 0)})
    return hist


# 1. La serie usa solo lo anterior: el nivel actual de un partido es el guardado tras el ANTERIOR
h = simular(0.8, 3)
t = 1
ser = nl.series(h[t])
filas = h[t]["filas"]
fx = filas[80]["fixtureId"]
guardado = [n["nivel"] for n in h[t]["niveles"] if n["fecha"] < filas[80]["fecha"]][-1]
check("serie: A del partido = nivel guardado tras el anterior", abs(ser[fx]["A actual"] - guardado) < 1e-9,
      (ser[fx]["A actual"], guardado))

# 2. Con fuerza de fondo, el largo (D) y el combinado (F) predicen mejor que A
r = nl.evaluar(nl.partidos(h, "2021-01-01"))
v = r["subconjuntos"]["todos"]["variantes"]
check("fondo: D mejor que A", v["D media3a"]["ic95"][1] < 0, v["D media3a"])
check("fondo: F mejor que A", v["F actual+3a"]["ic95"][1] < 0, v["F actual+3a"])

# 3. Sin fondo (solo la fuerza del momento), el largo no le gana al actual
h0 = simular(0.0, 5)
v0 = nl.evaluar(nl.partidos(h0, "2021-01-01"))["subconjuntos"]["todos"]["variantes"]
check("sin fondo: D no es mejor que A", v0["D media3a"]["ic95"][1] >= 0, v0["D media3a"])

# 4. Los grandes no se eligen con el futuro
hg = {1: {"filas": [], "niveles": [{"fecha": f"{a}-{m:02d}-{d:02d}", "nivel": 3.6}
                                   for a in range(2023, 2030) for m in range(1, 13) for d in (1, 15)]}}
hg[1]["filas"] = [{"fixtureId": i, "fecha": "2025-01-01", "ligaId": 39} for i in range(5)]
hg[2] = {"filas": hg[1]["filas"], "niveles": [{"fecha": n["fecha"], "nivel": 1.5 if n["fecha"] < "2026" else 4.5}
                                               for n in hg[1]["niveles"]]}
check("grandes con hasta: el que subió después no entra", ff.grandes(hg, 3.0, hasta="2026-01-01") == {1},
      ff.grandes(hg, 3.0, hasta="2026-01-01"))
check("grandes sin hasta: con el futuro sí entraba", 2 in ff.grandes(hg, 2.5))

print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
sys.exit(1 if fallos else 0)
