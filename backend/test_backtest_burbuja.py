"""Test del backtest del reventón (backend/backtest_burbuja.py) sobre la demo.

No valida que la guía acierte (eso depende de los datos reales): valida que
el backtest NO haga trampa —cada observación se reconstruye solo con las filas
anteriores al partido— y que sus conteos cierren.

    python -m backend.test_backtest_burbuja
"""
import os
import sys
import tempfile

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def main():
    tmp = tempfile.mkdtemp(prefix="sad_bt_")
    from backend.seed_demo import seed
    seed(tmp)
    os.environ["SAD_DATA_DIR"] = tmp
    import backend.db as dbmod
    dbmod.BASE_DIR = tmp
    from backend import backtest_burbuja as bt
    from backend.analisis import burbuja
    from backend.app import constantes_de

    equipos = bt._equipos(12)
    check("la demo tiene equipos con ≥ 12 filas", len(equipos) >= 4, len(equipos))
    obs, r = bt.correr(equipos, horizonte=1)
    check("hay observaciones (burbujas abiertas antes de un partido)", len(obs) > 20, len(obs))
    cond_de = {}
    for o in obs:
        if o["equipoId"] not in cond_de:
            cond_de[o["equipoId"]] = {f["fixtureId"]: f["condicion"] for f in constantes_de(o["equipoId"], 500)}
    check("cada observación mueve la familia en ese partido (local solo en partidos de local, etc.)",
          all(o["familia"] == "total" or cond_de[o["equipoId"]][o["fixtureId"]] == ("Local" if o["familia"] == "local" else "Visita")
              for o in obs))

    # anti-fuga: rehacer una observación a mano solo con el prefijo y comparar
    o = next(x for x in obs if x["familia"] == "total")
    filas = list(reversed(constantes_de(o["equipoId"], 500)))
    i = next(k for k, f in enumerate(filas) if f["fixtureId"] == o["fixtureId"])
    prefijo = filas[:i]
    est = burbuja.estabilidad_de(None, "1970-01-01")
    prox = {"fixtureId": o["fixtureId"], "fecha": filas[i]["fecha"], "rivalId": filas[i]["rivalId"],
            "rival": filas[i]["rivalNombre"], "condicion": "L" if filas[i]["condicion"] == "Local" else "V",
            "nivelRival": float(filas[i]["nivelRival"])}
    fam = burbuja._analizar_familia(prefijo, "total", prox, est)
    check("sin fuga: la guía de la observación es la del prefijo (mismos puntos y nivel)",
          fam["riesgo"]["puntos"] == o["puntos"] and fam["riesgo"]["nivel"] == o["nivel"], (fam["riesgo"], o))
    check("el resultado observado es el del partido siguiente, no del prefijo",
          o["reventoAhora"] == bt._revento(filas[i], "total", fam["actual"]["signo"]))
    check("la fila evaluada tiene ≥ 10 filas previas", i >= 10, i)

    # los conteos cierran
    con_base = r["tasaBase"]["n"]
    check("sin base + con base = observaciones", r["sinBase"] + con_base == r["observaciones"])
    check("los niveles suman el total con base", sum(r["porNivel"][n]["n"] for n in bt.NIVELES) == con_base)
    check("los puntos suman el total con base", sum(t["n"] for t in r["porPuntos"].values()) == con_base)
    check("+ y − suman el total", r["porSigno"]["+"]["n"] + r["porSigno"]["-"]["n"] == con_base)
    check("manda + noManda suman el total",
          r["reglaManda"]["manda"]["todas"]["n"] + r["reglaManda"]["noManda"]["todas"]["n"] == con_base)
    check("tasas dentro de [0, 1]", all(0 <= t["tasa"] <= 1 for t in r["porNivel"].values() if t["tasa"] is not None))
    check("AUC dentro de [0, 1] o None", r["aucPuntos"] is None or 0 <= r["aucPuntos"] <= 1, r["aucPuntos"])

    # horizonte: reventar dentro de 3 partidos es al menos tan frecuente como en 1
    _, r3 = bt.correr(equipos, horizonte=3)
    check("horizonte 3 ≥ horizonte 1 en tasa base", r3["tasaBase"]["tasa"] >= r["tasaBase"]["tasa"],
          (r3["tasaBase"], r["tasaBase"]))

    # el informe se imprime sin romperse
    bt.imprimir(r)

    print(f"\n{fallos} FALLAS" if fallos else "\nTODO OK")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
