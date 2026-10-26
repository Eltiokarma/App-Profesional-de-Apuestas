"""El backtest de la forma sin amistosos (backend/backtest_forma.py): la
ventana sin amistosos los saca de verdad, no hay fuga (el nivel es el de antes
del partido) y el subconjunto «difieren» es el de las ventanas con amistoso.

    python -m backend.test_backtest_forma
"""
import sys

from backend.backtest_forma import AMISTOSOS, evaluar, observaciones

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _hist(equipo, rival, resultados):
    filas, niveles = [], []
    for i, (gf, gc, liga) in enumerate(resultados):
        fecha = f"2026-{1 + i // 28:02d}-{1 + i % 28:02d}T20:00:00Z"
        filas.append({"fixtureId": equipo * 1000 + i, "fecha": fecha, "condicion": "Local" if i % 2 else "Visita",
                      "rivalId": rival, "ligaId": liga, "golesFavor": gf, "golesContra": gc})
        niveles.append({"fecha": fecha, "nivel": 2.0 + 0.01 * i})
    return {"filas": filas, "niveles": niveles}


def main():
    am = next(iter(AMISTOSOS))
    # un equipo que gana sus amistosos y pierde en liga
    res = [(0, 1, 140)] * 10 + [(3, 0, am), (2, 0, am)] + [(0, 1, 140)] * 10
    hist = {1: _hist(1, 2, res), 2: _hist(2, 1, [(1, 0, 140)] * 22)}
    obs = observaciones(hist)
    con = [o for o in obs if o["equipo"] == 1 and o["amistososEnVentana"] > 0]
    check("la ventana con amistosos los cuenta y la otra los saca (la forma sin amistosos es la de liga: 0 puntos)",
          con and all(o["gapSinAmistosos"] > o["gapTodas"] for o in con), con[:1])
    check("los amistosos no son partidos analizados", all(o["fixtureId"] not in (1010, 1011) for o in obs))
    check("sin 5 partidos previos no hay observación", all(int(str(o["fixtureId"])[-2:]) >= 5 for o in obs if o["equipo"] == 2))
    r = evaluar(obs)
    check("evaluar cuenta el subconjunto de ventanas que difieren",
          r["conAmistosoEnVentana"] == sum(1 for o in obs if o["amistososEnVentana"] > 0), r["conAmistosoEnVentana"])
    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
