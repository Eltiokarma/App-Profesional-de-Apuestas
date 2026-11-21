"""El backtest del semáforo de las burbujas y del cruce de las dos
(`backend/backtest_semaforo_burbujas.py`, REVENTON §19): la regla del color,
el armado de los partidos sin mezclar lados, y que el método detecte un efecto
plantado en el cruce sin inventar uno donde no lo hay.

    python -m backend.test_backtest_semaforo_burbujas
"""
from __future__ import annotations

import math
import random

from backend import backtest_semaforo_burbujas as sb

FALLAS: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("OK   " if cond else "FALLA") + "  " + msg)
    if not cond:
        FALLAS.append(msg)


def B(signo, riesgo="medio", franja=False, tarjeta=None):
    if tarjeta is None:   # la tarjeta de la guía calibrada: bajo y medio siguen, alto y muy alto se dan vuelta
        sigue = riesgo in ("bajo", "medio")
        tarjeta = ("gana" if signo == "+" else "pierde") if sigue else ("pierde" if signo == "+" else "gana")
    return {"signo": signo, "riesgo": riesgo, "extremo": franja, "cerca": False, "partidos": 3,
            "tarjeta": tarjeta, "fuerte": riesgo == "bajo"}


def test_estado_y_tarjeta():
    o = {"signo": "+", "nivel": "bajo", "extremo": False, "cerca": True, "partidos": 4}
    e = sb.estado_de_obs(o)
    check(e["tarjeta"] == "gana" and e["fuerte"], "racha + con riesgo bajo: la tarjeta dice que gana, fuerte")
    e = sb.estado_de_obs({**o, "nivel": "muy alto"})
    check(e["tarjeta"] == "pierde" and not e["fuerte"], "racha + con riesgo muy alto: la tarjeta dice que pierde, débil")
    e = sb.estado_de_obs({**o, "signo": "-", "nivel": "alto"})
    check(e["tarjeta"] == "gana", "racha − con riesgo alto: la tarjeta dice que se da vuelta (gana)")
    check(sb.franja(e), "cerca del extremo cuenta como franja alta")


def test_color():
    c = {"yo": B("+", "bajo"), "riv": B("-", "bajo")}
    check(sb.color(c) == "verde", "el elegido gana y el rival pierde: verde")
    c = {"yo": B("+", "bajo"), "riv": B("+", "bajo")}
    check(sb.color(c) == "amarillo", "el rival también dice que gana: amarillo")
    c = {"yo": B("+", "muy alto"), "riv": None}
    check(sb.color(c) == "rojo", "la tarjeta del elegido dice que pierde: rojo")
    c = {"yo": None, "riv": B("+")}
    check(sb.color(c) == "sinDato", "el elegido sin burbuja abierta: sin dato")
    c = {"yo": B("+", "bajo"), "riv": None}
    check(sb.color(c) == "verde", "el rival sin burbuja no pinta amarillo")
    # Ameliano–Luqueño: el elegido (local) con racha − cerca del extremo, el rival + en su récord
    c = {"yo": B("-", "bajo", True), "riv": B("+", "medio", True)}
    check(sb.color(c) == "rojo", "Ameliano: la tarjeta del elegido dice que sigue perdiendo → rojo")
    check(sb.SENALES["las dos en el extremo, acuerdan CONTRA el elegido"](c), "Ameliano: las dos acuerdan contra el elegido")
    check(not sb.SENALES["las dos en el extremo, chocan (mismo signo)"](c), "signos opuestos no chocan")


def test_partidos():
    lados = {
        (1, 10): {"fecha": "2025-01-01", "local": True, "liga": 5, "rival": 20, "nivel": 3.0, "gana": True, "empata": False},
        (1, 20): {"fecha": "2025-01-01", "local": False, "liga": 5, "rival": 10, "nivel": 2.0, "gana": False, "empata": False},
        (2, 10): {"fecha": "2025-01-08", "local": False, "liga": 5, "rival": 30, "nivel": 3.0, "gana": False, "empata": True},
        (2, 30): {"fecha": "2025-01-08", "local": True, "liga": 5, "rival": 10, "nivel": None, "gana": False, "empata": True},
    }
    burb = {(1, 20): B("-", "alto")}
    ms = sb.partidos(lados, burb, {1: (0.6, 0.25, 0.15, 0, 0.05)})
    check(len(ms) == 1, "un partido sin el nivel previo de un lado no entra")
    m = ms[0]
    check(m["tL"] == 10 and m["tV"] == 20 and m["res"] == "L", "local, visita y resultado en su lugar")
    check(m["bL"] is None and m["bV"]["signo"] == "-", "la burbuja va con su equipo; sin burbuja = None")
    e = sb.elegidos(ms, "casa")[0]
    check(e["team"] == 10 and e["local"] and abs(e["p"] - 0.6) < 1e-9 and e["gana"], "el elegido de la casa es el local de 60 %")
    check(sb.elegidos(ms, "nivel")[0]["ventaja"] == 1.0, "la ventaja del elegido por nivel, en su sentido")
    check(not sb.partidos(lados, burb, None, {1}), "las copas nacionales se excluyen")


def _sinteticos(plantar: float, n: int = 24000, semilla: int = 3) -> list[dict]:
    """Partidos con la verdad conocida: el local gana con una logística de la
    diferencia de nivel; las burbujas son ruido salvo el efecto plantado: con
    las dos en el extremo y signos opuestos, el de la racha + gana `plantar`
    menos (lo que pierde va a la derrota)."""
    rnd = random.Random(semilla)
    ms = []
    riesgos = ("bajo", "medio", "alto", "muy alto")
    for i in range(n):
        nl, nv = rnd.uniform(1.5, 3.5), rnd.uniform(1.5, 3.5)
        d = nl - nv + 0.3
        pl = 1 / (1 + math.exp(-1.3 * d)) * 0.74
        pe = 0.26
        bl = None if rnd.random() < 0.25 else B(rnd.choice("+-"), rnd.choice(riesgos), rnd.random() < 0.15)
        bv = None if rnd.random() < 0.25 else B(rnd.choice("+-"), rnd.choice(riesgos), rnd.random() < 0.15)
        r = rnd.random()
        res = "L" if r < pl else "E" if r < pl + pe else "V"
        if bl and bv and sb.franja(bl) and sb.franja(bv) and bl["signo"] != bv["signo"]:
            mas = "L" if bl["signo"] == "+" else "V"
            if res == mas and rnd.random() < plantar / (pl if mas == "L" else 1 - pl - pe):
                res = "V" if mas == "L" else "L"
        p = None
        if i % 3 == 0:
            p = (pl, pe, 1 - pl - pe)
        ms.append({"fixtureId": i, "fecha": f"20{19 + i * 7 // n}-01-01", "liga": i % 40,
                   "tL": rnd.randrange(300), "tV": rnd.randrange(300), "nL": nl, "nV": nv, "res": res,
                   "p": p, "margen": 0.05 if p else None, "bL": bl, "bV": bv})
    return ms


def test_detecta_y_no_inventa():
    r = sb.evaluar(_sinteticos(plantar=0.20))
    f2 = next(f for f in r["cruce"] if f["tipo"] == "acuerdan" and f["enExtremo"] == 2)
    check(f2.get("separa") and f2["diferencia"] < -0.08,
          f"plantado: con las dos en el extremo el resultado que sigue las dos sale menos ({f2.get('diferencia')})")
    f0 = next(f for f in r["cruce"] if f["tipo"] == "acuerdan" and f["enExtremo"] == 0)
    check(not f0.get("separa"), f"sin las dos en el extremo, nada ({f0.get('diferencia')})")
    seg = next(s for s in r["segmentos"] if s["segmento"] == "favorito por nivel (todos)")
    s = next(x for x in seg["senales"] if x["senal"] == "las dos en el extremo, acuerdan CON el elegido")
    check(s.get("separa") and s["diferencia"] > 0.08, f"la señal del elegido lo marca como dónde no entrar ({s.get('diferencia')})")
    ruido = next(x for x in seg["senales"] if x["senal"] == "el rival viene ganando (racha +)")
    check(not ruido.get("separa"), f"una señal de ruido no separa ({ruido.get('diferencia')})")
    r0 = sb.evaluar(_sinteticos(plantar=0.0))
    f2 = next(f for f in r0["cruce"] if f["tipo"] == "acuerdan" and f["enExtremo"] == 2)
    check(not f2.get("separa"), f"sin efecto plantado, el cruce no inventa uno ({f2.get('diferencia')})")
    tab = {x["color"]: x for x in r0["semaforo"]["nivel"]}
    check(all(abs(tab[c]["gana"] - tab[c]["esperadoNivel"]) < 0.03 for c in ("verde", "amarillo", "rojo")),
          "con tarjetas de ruido, cada color gana lo esperado por su nivel")
    check(r0["lectura"] and "semáforo" in r0["lectura"], "la lectura se arma")


def main() -> None:
    sb.BOOTSTRAP = 200   # el método no cambia; el test corre en CI
    test_estado_y_tarjeta()
    test_color()
    test_partidos()
    test_detecta_y_no_inventa()
    print("\nTODO OK" if not FALLAS else f"\n{len(FALLAS)} FALLA(S)")
    raise SystemExit(1 if FALLAS else 0)


if __name__ == "__main__":
    main()
