"""El backtest del semáforo calibrado por razones: aprende el peso de una razón
plantada que hace perder a los verdes, lo comprueba en la etapa nueva y en los
amarillos (que no vio), no inventa pesos donde no hay efecto, no lee el
veredicto y deja afuera el empate y las copas.

    python -m backend.test_backtest_semaforo_razones
"""
import random
import sys

from backend import backtest_semaforo_razones as bt

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def parte(fid, rnd, efecto, amarillo=False, copa=False, empate=False):
    """Un parte enriquecido sintético. Con la alerta X sobre el elegido (1 de cada 4),
    el elegido gana `efecto` menos. El veredicto trae el resultado: no debe leerse."""
    mala = rnd.random() < 0.25
    pe = rnd.uniform(45, 70)
    probs = {"local": 20, "empate": 60, "visita": 20} if empate else {"local": pe, "empate": 25, "visita": 75 - pe}
    gana = rnd.random() < (pe / 100 - (efecto if mala else 0))
    gl, gv = (2, 0) if gana else (rnd.choice([(0, 0), (0, 1)]))
    dia = 1 + fid % 28
    mes = 9 + (fid * 3) // 1000
    return str(fid), {
        "parte": {
            "pronostico": {"probabilidades": probs, "marcador": "1-0"},
            "lecturaSad": {"espina": {"a": {"lectura": "cero" if amarillo else "positiva"}, "b": {"lectura": "negativa"}}},
            "alertas": ([{"codigo": "X", "equipo": "a"}] if mala else []) + ([{"codigo": "RUIDO", "equipo": "b"}] if rnd.random() < 0.3 else []),
            "veredicto": {"objetivo": {"unXDos": {"acerto": gana}}, "notas": "PERDIO" if not gana else "GANO"},
        },
        "fx": {"fecha": f"2026-{mes:02d}-{dia:02d}T20:00:00Z", "ligaId": 999 if copa else 1, "liga": "Copa X" if copa else "Liga",
               "local": {"nombre": "A"}, "visitante": {"nombre": "B"}, "golesLocal": gl, "golesVisitante": gv},
    }


def datos(efecto, semilla, n=2400):
    rnd = random.Random(semilla)
    d = dict(parte(i, rnd, efecto, amarillo=(i % 7 == 0)) for i in range(1, n))
    d.update(dict([parte(9000, rnd, efecto, copa=True), parte(9001, rnd, efecto, empate=True)]))
    return d


copa = lambda fx: fx.get("ligaId") == 999  # noqa: E731

# 1. Con efecto: la alerta X sobre el elegido sale con peso, y el semáforo calibrado separa en la comprobación
fs = bt.filas(datos(0.30, 3), copa)
check("filas: copas y elegido empate afuera", all(r["fixtureId"] not in (9000, 9001) for r in fs))
check("filas: el veredicto no entra a las razones", not any("PERDIO" in x or "acerto" in x for r in fs for x in r["razones"]))
r = bt.evaluar(fs)
pesos = bt.aprender([x for x in fs if x["base"] == "confirma"])
check("aprende la razón plantada con peso positivo", pesos.get("AL-X@ELEGIDO", 0) > 0.5, pesos)
check("y no le da peso al ruido", abs(pesos.get("AL-RUIDO@RIVAL", 0)) < bt.MIN_PESO or "AL-RUIDO@RIVAL" not in pesos, pesos)
cal = r["comprobacionTabla"]["calibrado"]
no_verde = [cal[c] for c in ("amarillo", "rojo") if c in cal]
tasa_nv = sum(c["gana"] for c in no_verde) / max(1, sum(c["n"] for c in no_verde))
check("comprobación: lo que deja de ser verde (amarillo o rojo) gana menos que el verde calibrado",
      no_verde and tasa_nv < cal["verde"]["tasa"] - 0.1, cal)
am = r["amarillosConPesosDelVerde"]
check("los amarillos (no vistos) con la razón ganan menos que sin ella",
      am["conRazones"]["amarillo"]["tasa"] < am["sinRazones"]["amarillo"]["tasa"], am)

# 2. Sin efecto: el semáforo calibrado no separa (no inventa)
fs0 = bt.filas(datos(0.0, 5), copa)
r0 = bt.evaluar(fs0)
c0 = r0["comprobacionTabla"]["calibrado"]
check("sin efecto: el amarillo calibrado no gana claramente menos que el verde",
      "amarillo" not in c0 or c0["amarillo"]["tasa"] > c0["verde"]["tasa"] - 0.1, c0)

# 3. La tabla para semaforo.py
t = bt.tabla(fs)
check("la tabla trae CALIBRACION, CORTE, CORTE_ROJO y PESOS listos para pegar",
      t.startswith("CALIBRACION = {") and "\nCORTE = " in t and "\nCORTE_ROJO = " in t and '"AL-X@ELEGIDO":' in t, t[:200])
check("todas las combinaciones de color y tramo, en las dos etapas",
      any(k.startswith("verde · ") for k in r["combinaciones"]) and any(k.startswith("amarillo · ") for k in r["combinaciones"]),
      list(r["combinaciones"])[:4])

print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
sys.exit(1 if fallos else 0)
