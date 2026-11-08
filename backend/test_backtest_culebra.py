"""El backtest de la ley anticulebras detecta una culebra plantada, no inventa
una en datos independientes y no mira lo que el apostador no sabía en el pitazo.

    python -m backend.test_backtest_culebra
"""
from __future__ import annotations

import datetime as dt
import random
import sys

from backend import backtest_culebra as bc

fallas = 0


def check(nombre, cond, detalle=""):
    global fallas
    print(("ok   " if cond else "FALLA") + " " + nombre + ("" if cond else f"  → {detalle}"))
    fallas += 0 if cond else 1


def partido(i, liga, hora, gl, gv, temporada=2025, cuotas=None):
    return {"id": i, "ligaId": liga, "temporada": temporada, "fecha": hora.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "golesLocal": gl, "golesVisitante": gv, "cuotas": cuotas}


GOLES = {"1": (1, 0), "X": (1, 1), "2": (0, 1)}
PROBS = {"1": 0.45, "X": 0.27, "2": 0.28}
CUOTAS = {s: round(1 / p / 1.05, 2) for s, p in PROBS.items()}   # con margen


def sortear(rng, probs=PROBS):
    u, acc = rng.random(), 0.0
    for s, p in probs.items():
        acc += p
        if u < acc:
            return s
    return "2"


def jornada(culebra: bool, semilla: int, dias: int = 1500) -> list[dict]:
    """Ligas con 4 partidos por día a las 15, 17:30, 20 y 22:30 de Lima (2 h y media
    de separación). Con culebra, si todos los previos terminados fueron del local,
    el siguiente EMPATA con 60 %."""
    rng, out, i = random.Random(semilla), [], 0
    for d in range(dias):
        base = dt.datetime(2025, 1, 1, 20) + dt.timedelta(days=d)     # 15:00 de Lima
        res = []
        for j in range(4):
            hora = base + dt.timedelta(minutes=150 * j)
            if culebra and j > 0 and all(r == "1" for r in res):
                r = "X" if rng.random() < 0.6 else sortear(rng)
            else:
                r = sortear(rng)
            res.append(r)
            i += 1
            out.append(partido(i, 10 + d % 3, hora, *GOLES[r], cuotas=dict(CUOTAS)))
    return out


# ── unidad: el día de Lima, sin repetidos, el margen ─────────────────────────
t = dt.datetime(2025, 3, 1, 3, 0)            # 03:00 UTC = 22:00 del día anterior en Lima
g = bc.liga_dias([partido(1, 5, t, 1, 0), partido(2, 5, t, 0, 0), partido(3, 5, t, 2, 1),
                  partido(3, 5, t, 2, 1)])
check("el liga-día es el día de Lima (03:00 UTC cae el día anterior)", list(g) == [(5, "2025-02-28")], list(g))
check("un id repetido entra una vez", len(next(iter(g.values()))) == 3)
check("menos de 3 partidos no forman liga-día", bc.liga_dias([partido(1, 5, t, 1, 0), partido(2, 5, t, 1, 0)]) == {})
p = bc.sin_margen({"1": 2.0, "X": 3.2, "2": 3.8})
check("sin margen: las tres suman 1", abs(sum(p.values()) - 1) < 1e-9, p)
check("sin las tres cuotas no hay probabilidad", bc.sin_margen({"1": 2.0, "X": 3.2}) is None)

# ── anti-fuga: un partido que arrancó hace menos de 2 h no es «previo» ────────
d = [partido(1, 5, t, 1, 0), partido(2, 5, t + dt.timedelta(minutes=90), 1, 0),
     partido(3, 5, t + dt.timedelta(minutes=150), 1, 0)]
check("anti-fuga: a los 90 min el primero no terminó", bc._previos(d, 1) == [])
check("anti-fuga: a los 150 min el primero sí, el de los 90 no", [x["id"] for x in bc._previos(d, 2)] == [1])

# ── no inventa: datos independientes ─────────────────────────────────────────
r = bc.analizar(jornada(False, 1), permutaciones=60)
lin = r["conCuotas"]["previos2+"]["localesGanaron→empate"]
check("independiente: el empate tras locales no se aparta (|dif| ≤ IC)",
      abs(lin["dif"]) <= lin["ic95"], lin)
apu = r["conCuotas"]["apuestaEmpate"]["tras1+Locales"]["roi"]
check("independiente: la apuesta al empate pierde lo del margen (ROI < 0)", apu < 0, apu)
z = r["extremos"]["todosLocales"]["z"]
check("independiente: los días extremos salen como la permutación (|z| < 3)", abs(z) < 3, z)

# ── detecta: culebra plantada ────────────────────────────────────────────────
r = bc.analizar(jornada(True, 2), permutaciones=60)
lin = r["conCuotas"]["previos1+"]["localesGanaron→empate"]
check("culebra plantada: el empate tras locales sale por encima (dif > IC)", lin["dif"] > lin["ic95"], lin)
sc = r["sinCuotas"]["1|todosLocal|X"]
check("culebra plantada: también sin cuotas", sc["dif"] > sc["ic95"], sc)
apu = r["conCuotas"]["apuestaEmpate"]["tras1+Locales"]["roi"]
check("culebra plantada: la apuesta al empate gana (ROI > 0)", apu > 0, apu)
z = r["extremos"]["todosLocales"]["z"]
check("culebra plantada: menos días con todos los locales que la permutación (z < −3)", z < -3, z)

print(f"\n{'TODO OK' if not fallas else f'{fallas} FALLA(S)'}")
sys.exit(1 if fallas else 0)
