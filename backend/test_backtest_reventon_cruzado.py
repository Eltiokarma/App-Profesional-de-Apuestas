"""El backtest de cuándo revienta una burbuja por sus goles y su periodicidad
(`backend/backtest_reventon_cruzado.py`, REVENTON §20): los rasgos salen solo
de lo anterior, la racha de goles es la de la burbuja, y el método detecta un
efecto plantado sin inventar uno.

    python -m backend.test_backtest_reventon_cruzado
"""
from __future__ import annotations

import random

from backend import backtest_reventon_cruzado as rc

FALLAS: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("OK   " if cond else "FALLA") + "  " + msg)
    if not cond:
        FALLAS.append(msg)


def _fila(i, gf, gc, cond="Local", temporada=2025):
    q = (gf > gc) - (gf < gc)
    k = 0.0 if q == 0 else q * (abs(gf - gc) * 2.0)
    return {"fixtureId": i, "fecha": f"2025-{1 + i // 28:02d}-{1 + i % 28:02d}T20:00:00Z", "condicion": cond,
            "temporada": temporada, "golesFavor": gf, "golesContra": gc, "ligaId": 1, "rivalId": 99,
            "rivalNombre": "R", "nivelRival": 2.0, "fusion": {"k": k, "kLocal": k if cond == "Local" else 0.0,
                                                              "kVisita": k if cond == "Visita" else 0.0}}


def test_rasgos():
    # gana 2-1, 1-0, 3-2 (racha + de 3, recibiendo en dos, por la mínima en las tres), y el 4.º partido es el próximo
    filas = [_fila(0, 0, 2), _fila(1, 2, 1), _fila(2, 1, 0), _fila(3, 3, 2), _fila(4, 0, 0)]
    r = rc.rasgos(filas, "total")
    x = r[3]
    check(x["racha"] == [(2, 1), (1, 0)], f"antes del 4.º partido la racha es la de los dos anteriores ({x['racha']})")
    x = r[4]
    check(x["racha"] == [(2, 1), (1, 0), (3, 2)], "antes del 5.º, la racha de tres victorias")
    check(not rc.SENALES["+"]["gana recibiendo en toda la racha"](x), "ganó 1-0 en el medio: no recibió en toda la racha")
    check(rc.SENALES["+"]["gana por la mínima en toda la racha"](x), "las tres por un gol: por la mínima")
    check(x["anotaSeguidos"] == 3 and x["sinAnotar"] == 0, "anota seguidos 3, sin anotar 0")
    check(r[1]["racha"] == [(0, 2)] and r[1]["sinAnotar"] == 1, "tras perder 0-2: racha − de uno, sin anotar en el último")
    # no ve el partido que se predice: el 5.º (0-0) no cambia los rasgos del 5.º
    filas2 = filas[:4] + [_fila(4, 5, 0)]
    check(rc.rasgos(filas2, "total")[4] == x, "los rasgos de un partido no dependen de su resultado (sin fuga)")
    # la familia de local solo mira los partidos de local
    fl = [_fila(0, 1, 0, "Local"), _fila(1, 0, 3, "Visita"), _fila(2, 2, 1, "Local"), _fila(3, 0, 0, "Local")]
    rl = rc.rasgos(fl, "local")
    check(rl[3]["racha"] == [(1, 0), (2, 1)] and 1 not in rl, "la racha de local salta el partido de visita")


def _sinteticos(plantar: float, n: int = 30000, semilla: int = 5) -> list[dict]:
    rnd = random.Random(semilla)
    obs = []
    for i in range(n):
        sg = rnd.choice("+-")
        riesgo = rnd.choice(("bajo", "medio", "alto", "muy alto"))
        base = {"bajo": 0.47, "medio": 0.55, "alto": 0.65, "muy alto": 0.72}[riesgo]
        partidos = rnd.randint(1, 8)
        tip = rnd.choice((2, 3, 4))
        racha = [((rnd.randint(1, 3), rnd.randint(0, 2)) if sg == "+" else (rnd.randint(0, 1), rnd.randint(2, 3)))
                 for _ in range(partidos)]
        if sg == "+":
            racha = [(max(gf, gc + 1), gc) for gf, gc in racha]
        recibe = sg == "+" and all(gc > 0 for _, gc in racha)
        p = base + (plantar if recibe else 0.0)
        obs.append({"team": rnd.randrange(400), "fecha": f"20{19 + i * 7 // n}-06-01", "familia": rnd.choice(("total", "local", "visita")),
                    "signo": sg, "riesgo": riesgo, "revento": rnd.random() < p, "partidos": partidos,
                    "gFavor": rnd.uniform(-1.5, 1.5), "racha": racha, "anotaSeguidos": rnd.randint(0, 7),
                    "sinAnotar": rnd.randint(0, 2), "tipico": {"global": tip, "temporada": tip, "anio": None}})
    return obs


def test_detecta_y_no_inventa():
    r = rc.evaluar(_sinteticos(0.15))
    g = next(x for x in r["goles"] if x["senal"] == "gana recibiendo en toda la racha")
    check(g.get("separa") and 0.10 < g["diferencia"] < 0.20, f"plantado: ganar recibiendo revienta más ({g.get('diferencia')})")
    ruido = next(x for x in r["goles"] if x["senal"] == "valla invicta en el último")
    check(not (ruido.get("separa") and ruido["diferencia"] > 0.03), f"la valla invicta, sin efecto propio, no suma ({ruido.get('diferencia')})")
    r0 = rc.evaluar(_sinteticos(0.0))
    g0 = next(x for x in r0["goles"] if x["senal"] == "gana recibiendo en toda la racha")
    check(not g0.get("separa"), f"sin efecto plantado, no lo inventa ({g0.get('diferencia')})")
    p = r0["periodicidad"]["total +"]
    check(p["anio"]["conTipico"] == 0 and p["global"]["conTipico"] > 0, "una referencia sin típico no entra")
    check(abs(p["global"]["separa"]) < 0.05, f"sin periodicidad plantada, el largo no separa ({p['global']['separa']})")
    na = next(x for x in r["noApostar"] if x["senal"] == "gana recibiendo en toda la racha")
    check(na["fallaCon"] > na["fallaSin"], "en el favorito que viene ganando, la señal plantada marca dónde no apostar")
    check(r["lectura"], "la lectura se arma")


def test_demo():
    """El camino real (constantes de la base + observar_equipo) sobre la demo."""
    import os
    import tempfile
    tmp = tempfile.mkdtemp(prefix="sad_rc_")
    from backend.seed_demo import seed
    seed(tmp)
    os.environ["SAD_DATA_DIR"] = tmp
    import backend.db as dbmod
    dbmod.BASE_DIR = tmp
    from backend.backtest_burbuja import _equipos
    obs = rc.observar(_equipos(12))
    check(len(obs) > 20, f"la demo da observaciones de burbujas abiertas ({len(obs)})")
    co = sum(1 for o in obs if o["coincide"]) / len(obs)
    check(co > 0.9, f"la racha de goles tiene el largo de la burbuja de la K ({co:.1%})")
    check({o["familia"] for o in obs} == {"total", "local", "visita"}, "entran las tres familias")
    r = rc.evaluar(obs)
    check(r["observaciones"] == len(obs) and r["periodicidad"], "la evaluación corre sobre la demo")


def main() -> None:
    rc.BOOTSTRAP = 200
    test_rasgos()
    test_detecta_y_no_inventa()
    test_demo()
    print("\nTODO OK" if not FALLAS else f"\n{len(FALLAS)} FALLA(S)")
    raise SystemExit(1 if FALLAS else 0)


if __name__ == "__main__":
    main()
