"""La calibración de las dos lecturas (24/11/2026): detecta un analista que
comprime hacia el medio y lo corrige; no inventa una corrección cuando lo
dicho ya está calibrado; con pocos partidos casi no se mueve.

    python -m backend.test_backtest_calibracion_lecturas
"""
import os
import random

os.environ["SAD_SIN_HILOS"] = "1"

from backend.analisis import calibracion_lecturas as cal  # noqa: E402
from backend import backtest_calibracion_lecturas as bt  # noqa: E402

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'✓' if cond else '✗ FALLA'} {nombre}" + (f" — {detalle}" if detalle and not cond else ""))


def sinteticos(n, comprime: bool, semilla=7):
    """Partidos con la verdad conocida. Si `comprime`, el analista dice la
    verdad aplastada hacia el medio (su 60 es en realidad un 72)."""
    rnd = random.Random(semilla)
    filas = []
    for i in range(n):
        pl = rnd.uniform(0.15, 0.75)
        pv = rnd.uniform(0.05, min(0.6, 0.95 - pl))
        u = rnd.random()
        res = "local" if u < pl else ("visita" if u < pl + pv else "empate")
        dl, dv = (0.5 + (pl - 0.5) * 0.6, 0.5 + (pv - 0.5) * 0.6) if comprime else (pl, pv)
        filas.append({"pitazo": f"2026-11-{1 + i % 28:02d} {i % 24:02d}:00:00", "ganaLocal": 100 * dl,
                      "ganaVisita": 100 * dv, "resultado": res})
    return sorted(filas, key=lambda f: f["pitazo"])


def main():
    check("ajustar sin puntos: la identidad", cal.ajustar([]) == {"a": 0.0, "b": 1.0, "n": 0})
    check("aplicar con la identidad deja el número", cal.aplicar({"a": 0, "b": 1, "n": 0}, 63.0) == 63.0)

    comp = sinteticos(3000, comprime=True)
    c = cal.ajuste_de(comp)
    check("comprime hacia el medio → la pendiente sale > 1 en los dos lados",
          c["local"]["b"] > 1.3 and c["visita"]["b"] > 1.3, c)
    r = bt.corte(comp)
    m = r["porPrevio"][str(cal.PRIOR_SD)]
    check("corte temporal: calibrado gana a lo dicho en logLoss, en partidos que no vio (local)",
          m["local"]["logLoss"] < r["dicho"]["local"]["logLoss"], (m["local"], r["dicho"]["local"]))
    check("corte temporal: y en el visitante",
          m["visita"]["logLoss"] < r["dicho"]["visita"]["logLoss"], (m["visita"], r["dicho"]["visita"]))

    bien = sinteticos(3000, comprime=False, semilla=11)
    cb = cal.ajuste_de(bien)
    check("ya calibrado → la pendiente queda cerca de 1 y el corrimiento cerca de 0",
          all(0.85 < cb[l]["b"] < 1.15 and abs(cb[l]["a"]) < 0.2 for l in cal.LADOS), cb)
    rb = bt.corte(bien)
    mb = rb["porPrevio"][str(cal.PRIOR_SD)]
    check("ya calibrado → calibrar casi no cambia la pérdida (no inventa una corrección)",
          all(abs(mb[l]["logLoss"] - rb["dicho"][l]["logLoss"]) < 0.01 for l in cal.LADOS), (mb, rb["dicho"]))

    pocos = sinteticos(12, comprime=True, semilla=3)
    cp = cal.ajuste_de(pocos)
    check("con 12 partidos la curva casi no se mueve (el previo la sostiene)",
          all(abs(cp[l]["b"] - 1) < 0.5 for l in cal.LADOS), cp)

    v = cal.en_ventana([{"pitazo": "2026-11-24 20:00:00"}, {"pitazo": "2026-11-11 20:00:00"},
                        {"pitazo": "2026-11-05 20:00:00"}, {"pitazo": None}])
    check("la ventana: solo los últimos 14 días desde el más reciente (y sin pitazo, fuera)",
          [f["pitazo"][:10] for f in v] == ["2026-11-24", "2026-11-11"], v)
    check("la ventana en 0: todas", len(cal.en_ventana([{"pitazo": "2026-01-01 00:00:00"}, {}], 0)) == 2)
    x = cal.calibrar(55, 20, {"local": {"a": 0, "b": 1, "n": 1}, "visita": {"a": 0, "b": 1, "n": 1}})
    check("calibrar con la identidad: el 1X2 sale de calzar (empate 25)", x["empate"] == 25.0, x)
    s = bt.semanal(comp)
    check("semana a semana: cada semana con las anteriores, y calibrado gana a lo dicho",
          s["semanas"] and s["calibrado"]["local"]["logLoss"] < s["dicho"]["local"]["logLoss"], s["calibrado"])
    check("la lectura de la curva en castellano dice «te quedás corto» con pendiente > 1",
          "corto" in cal.lectura(c["local"]), cal.lectura(c["local"]))

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
    raise SystemExit(1 if fallos else 0)


if __name__ == "__main__":
    main()
