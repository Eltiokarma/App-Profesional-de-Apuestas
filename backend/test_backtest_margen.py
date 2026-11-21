"""El backtest del margen del favorito (el hándicap) cuenta bien, no mira el
resultado que evalúa, caza un efecto plantado, no inventa uno y marca la liga
donde el favorito gana apretado.

    python -m backend.test_backtest_margen
"""
import random
import sys

from backend import backtest_margen as bm

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _hist(resultados, cond="Visita", team=7, rival=8):
    return {team: {"filas": [{"fixtureId": i + 1, "fecha": f"2025-{1 + i // 28:02d}-{1 + i % 28:02d}T20:00:00Z",
                              "condicion": cond, "rivalId": rival, "ligaId": 39, "golesFavor": gf, "golesContra": gc}
                             for i, (gf, gc) in enumerate(resultados)],
                   "niveles": [{"fecha": "2000-01-01", "nivel": 2.0}]}}


def main():
    # ── 1 · las burbujas del margen y sin fuga ──────────────────────────────
    serie = [(0, 3)] * 3 + [(0, 1), (1, 1), (2, 0), (0, 1), (1, 0), (1, 2), (0, 0), (2, 2), (0, 1)]
    ls = bm.lados(_hist(serie))
    ult = ls[(len(serie), 7)]
    # 12 partidos: 3 goleadas y 9 sin perder por 2+; el último es el evaluado, así que antes hay 8
    check("la sequía de goleadas del rival cuenta los partidos SIN perder por 2+ previos (8)", ult["sequiaGoleada"] == 8, ult)
    check("su perfil de goleado sale de la historia previa en la condición (3 de 11, Laplace)",
          abs(ult["perfilGoleado"] - (3 + 1) / (11 + 2)) < 1e-9, ult["perfilGoleado"])
    check("la forma de 10 previos cuenta los que no perdió por 2+ (8 de 10: entran 2 goleadas)", ult["formaNoGoleado"] == 0.8, ult)
    h = _hist(serie)
    h[7]["filas"][-1]["golesFavor"], h[7]["filas"][-1]["golesContra"] = 0, 5
    ult2 = bm.lados(h)[(len(serie), 7)]
    check("el resultado evaluado no cambia lo que se sabía antes",
          all(ult[k] == ult2[k] for k in ("sequiaGoleada", "perfilGoleado", "formaNoGoleado", "recordSequia")), (ult, ult2))
    check("pero sí el margen que se evalúa", ult["margen"] == -1 and ult2["margen"] == -5)

    # ── 2 · el reparto y la cuota justa ─────────────────────────────────────
    cs = [{"margen": m, "p": None} for m in (3, 2, 1, 1, 0, -1, 4, 2)]
    r = bm.reparto(cs)
    total = r["ganaPor1"] + r["ganaPor2oMas"] + r["empata"] + r["pierde"]
    check("el reparto suma 1", abs(total - 1) < 1e-9, r)
    check("la cuota justa del −1,5 es 1 / P(gana por 2+)", r["cuotaJustaMenos1_5"] == round(1 / (4 / 8), 2), r)

    # ── 3 · caza lo plantado, no inventa, y la liga apretada sale primero ──
    def casos(efecto, semilla):
        rnd = random.Random(semilla)
        out = []
        for i in range(24000):
            v = rnd.uniform(1.0, 2.2)
            seq = rnd.choice([0, 1, 2, 6, 8])                 # sequía de goleadas del rival
            liga = 1 + i % 6
            p2 = min(0.8, 0.15 + 0.3 * v)                     # P(gana por 2+) según la ventaja
            if efecto and seq >= 5:
                p2 -= efecto
            if liga == 6:
                p2 -= 0.12                                    # la liga donde se gana apretado
            m = 2 if rnd.random() < p2 else rnd.choice([1, 0, -1])
            out.append({"team": i % 300, "fecha": f"{2019 + i // 4000}-06-01", "liga": liga, "local": i % 2 == 0,
                        "ventaja": v, "nivel": 3.8, "p": None, "margen": m,
                        "fav": {"formaGoleo": 0.5, "sequiaGoleo": 0},
                        "riv": {"perfilGoleado": 0.3, "sequiaGoleada": seq, "recordSequia": 0,
                                "formaNoGoleado": 0.7, "perfilNoPierde": 0.5}})
        return out
    senal = bm.SENALES["rival: viene 5+ sin perder por 2+ en la condición"]
    k = bm.separa(casos(0.15, 1), senal)
    check("con el efecto plantado, la señal separa y en el sentido de «no entrar»", k.get("separa") and k["diferencia"] > 0.08, k)
    k0 = bm.separa(casos(0.0, 2), senal)
    check("sin efecto no separa (no inventa)", not k0.get("separa"), k0)
    lg = bm.por_liga(casos(0.0, 3), lambda c: True)
    check("por liga, la liga donde se gana apretado sale primera y por debajo de lo esperado",
          lg and lg[0]["liga"] == 6 and lg[0]["diferencia"] < -0.05, lg[:2])

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
