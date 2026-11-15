"""El backtest del 1X2 del motor desde μ (backend/backtest_unxdos_motor.py).

Era el único backtest sin test (FALLAS.md clase 8: «todo backtest nuevo lleva
un test que plante la fuga y la detecte»; mantenimiento del 15/11/2026). Con
historias SINTÉTICAS donde se sabe la verdad:

- la fuga plantada: el nivel guardado con la fecha DEL partido ya trae su
  resultado; si entrara a μ, el backtest se vería mejor de lo que es (deuda 13).
- un partido es una observación, vista desde el local, aunque viaje en las
  filas de los dos equipos;
- el corte es temporal (se entrena con lo viejo y se prueba con lo nuevo);
- con el nivel que mueve el resultado la logística le gana a la frecuencia, y
  con un resultado que no depende del nivel no inventa ventaja.

    python -m backend.test_backtest_unxdos_motor
"""
from __future__ import annotations

import os
import random
import sys

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend import backtest_unxdos_motor as bt  # noqa: E402
from backend.app import mu  # noqa: E402

fallas = 0


def check(nombre, ok, detalle=""):
    global fallas
    print(("OK  " if ok else "FALLA ") + nombre + ("" if ok else f" -> {detalle}"))
    fallas += 0 if ok else 1


def _fecha(i: int) -> str:
    return f"20{24 + i // 336:02d}-{1 + (i // 28) % 12:02d}-{1 + i % 28:02d}T20:00:00Z"


def liga(equipos: int, jornadas: int, semilla: int, efecto: float, fuga: bool = False) -> dict[int, dict]:
    """Todos contra todos, un partido por día. La fuerza de cada equipo mueve el
    resultado con `efecto` (0 = ruido) y el nivel guardado la mide con ruido.
    Con `fuga`, el nivel de la fecha del partido sube o baja con su resultado
    (como la fila real de /niveles, que ya lo trae)."""
    rnd = random.Random(semilla)
    fuerza = {t: rnd.gauss(0, 0.5) for t in range(1, equipos + 1)}
    h = {t: {"filas": [], "niveles": []} for t in fuerza}
    n = 0
    for _ in range(jornadas):
        orden = list(fuerza)
        rnd.shuffle(orden)
        for a, b in zip(orden[::2], orden[1::2]):
            fecha, fx = _fecha(n), 10_000 + n
            n += 1
            z = efecto * (fuerza[a] - fuerza[b]) + 0.25
            u = rnd.random()
            pl = 1 / (1 + 2.718281828 ** (-z)) * 0.75
            gl, gv = (1, 0) if u < pl else (0, 0) if u < pl + 0.27 else (0, 1)
            for t, r, cond, gf, gc in ((a, b, "Local", gl, gv), (b, a, "Visita", gv, gl)):
                h[t]["filas"].append({"fixtureId": fx, "fecha": fecha, "condicion": cond, "rivalId": r,
                                      "ligaId": 1, "golesFavor": gf, "golesContra": gc})
                nivel = 1.4 + fuerza[t] + rnd.gauss(0, 0.15)
                if fuga:
                    nivel += 1.5 * ((gf > gc) - (gf < gc))
                h[t]["niveles"].append({"fecha": fecha, "nivel": round(nivel, 4)})
    return h


def main():
    # ── 1 · la fuga plantada no entra a μ ───────────────────────────────────
    filas_a, filas_b, niv_a, niv_b = [], [], [], []
    for i in range(8):
        f = _fecha(i)
        filas_a.append({"fixtureId": 500 + i, "fecha": f, "condicion": "Local", "rivalId": 2, "ligaId": 1,
                        "golesFavor": 2, "golesContra": 0})
        filas_b.append({"fixtureId": 500 + i, "fecha": f, "condicion": "Visita", "rivalId": 1, "ligaId": 1,
                        "golesFavor": 0, "golesContra": 2})
        # el nivel de la fecha del partido es el que ya trae el resultado: 99
        niv_a.append({"fecha": f, "nivel": 1.5 if i < 7 else 99.0})
        niv_b.append({"fecha": f, "nivel": 1.2})
    obs = bt.observaciones({1: {"filas": filas_a, "niveles": niv_a}, 2: {"filas": filas_b, "niveles": niv_b}})
    ultimo = [o for o in obs if o["fixtureId"] == 507]
    check("fuga: el nivel con la fecha DEL partido no entra (μ sale del de antes)",
          ultimo and abs(ultimo[0]["muL"] - mu(1.5, 1.2, 1.0)) < 1e-9, ultimo)
    check("fuga: ningún μ local sale del nivel plantado",
          not any(abs(o["muL"] - mu(99.0, 1.2, 1.0)) < 1e-9 for o in obs), obs[-1:])
    check(f"sin {bt.MIN_PARTIDOS} partidos previos del local no hay observación",
          sorted(o["fixtureId"] for o in obs) == [500 + i for i in range(bt.MIN_PARTIDOS, 8)],
          [o["fixtureId"] for o in obs])
    check("un partido es UNA observación, vista desde el local",
          len({o["fixtureId"] for o in obs}) == len(obs) and all(o["y"] == "L" for o in obs), obs)

    # ── 2 · el corte es temporal ────────────────────────────────────────────
    h = liga(20, 120, semilla=3, efecto=2.5)
    obs = bt.observaciones(h)
    corte = int(len(obs) * (1 - bt.PRUEBA))
    check("las observaciones van ordenadas por fecha (se entrena con lo viejo)",
          all(obs[i]["fecha"] <= obs[i + 1]["fecha"] for i in range(len(obs) - 1)))
    r = bt.evaluar(obs)
    check("evaluar separa por fecha: el corte es la fecha de la primera de la prueba",
          "error" not in r and r["corte"] == obs[corte]["fecha"][:10] and r["prueba"] == len(obs) - corte, r.get("error"))

    # ── 3 · detecta lo que hay ──────────────────────────────────────────────
    vs = r["logisticaVsFrecuencia"]
    check("con el nivel que mueve el resultado, la logística le gana a la frecuencia (IC entero < 0)",
          vs["ic95"] and vs["ic95"][1] < 0, vs)
    probs = bt.poisson_sobre_mu(1.8, 0.9)
    check("el Poisson sobre μ (la referencia improvisada) suma 1", abs(sum(probs) - 1) < 1e-9, probs)

    # ── 4 · …y no inventa lo que no hay ──────────────────────────────────────
    r0 = bt.evaluar(bt.observaciones(liga(20, 120, semilla=5, efecto=0.0)))
    vs0 = r0["logisticaVsFrecuencia"]
    check("con un resultado que no depende del nivel, la logística no le gana a la frecuencia",
          "error" not in r0 and not (vs0["ic95"][1] < 0), vs0)

    # ── 5 · la fuga, si entrara, se notaría ─────────────────────────────────
    # Liga de RUIDO con el nivel de la fecha del partido movido por su resultado.
    # Con la regla de hoy (el nivel de ANTES) no aparece ventaja; con una
    # _nivel_antes que tomara la fila del partido (bisect_right), sí: el test
    # detecta la fuga plantada.
    hf = liga(20, 120, semilla=5, efecto=0.0, fuga=True)
    rf = bt.evaluar(bt.observaciones(hf))
    vsf = rf["logisticaVsFrecuencia"]
    check("la fuga plantada en los niveles no fabrica ventaja (la fila del partido no entra)",
          "error" not in rf and not (vsf["ic95"][1] < 0), vsf)
    from bisect import bisect_right
    sano = bt._nivel_antes
    bt._nivel_antes = lambda fechas, niveles, fecha: (niveles[bisect_right(fechas, fecha) - 1]
                                                      if bisect_right(fechas, fecha) else None)
    try:
        rl = bt.evaluar(bt.observaciones(hf))
    finally:
        bt._nivel_antes = sano
    vsl = rl["logisticaVsFrecuencia"]
    check("con la fuga abierta a propósito la ventaja aparece (el método la detectaría)",
          "error" not in rl and vsl["ic95"][1] < 0, vsl)

    print("\n" + ("TODO OK" if fallas == 0 else f"{fallas} FALLAS"))
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
