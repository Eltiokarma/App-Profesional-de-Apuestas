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

    # padrón y filtro por liga: la lista de ligas importantes es UNA (extractor.ligas_vivo)
    pad = bt.padron()
    check("el padrón sale de extractor.ligas_vivo() con nombres", len(pad) > 5 and all(isinstance(v, str) for v in pad.values()), len(pad))
    liga_demo = obs[0]["ligaId"]
    rl = bt.correr_backtest(liga=liga_demo, horizonte=1)
    check("--liga: solo se evalúan partidos de esa liga (la historia previa sigue completa)",
          all(l["ligaId"] == liga_demo for l in rl["porLiga"]) and rl["porLiga"], rl["porLiga"])
    check("--liga: ligasEvaluadas trae el nombre de la liga y el conteo de equipos",
          rl["ligasEvaluadas"] and rl["equipos"] >= 1, (rl["ligasEvaluadas"], rl["equipos"]))
    check("por liga: cada fila cierra (bajo + medio + alto/muy alto ≤ todas) y viene ordenada por n",
          all(l["bajo"]["n"] + l["altoMuyAlto"]["n"] <= l["todas"]["n"] for l in r["porLiga"])
          and [l["todas"]["n"] for l in r["porLiga"]] == sorted((l["todas"]["n"] for l in r["porLiga"]), reverse=True))
    rp = bt.correr_backtest(padron_=True, horizonte=1)
    check("--padron: evalúa solo ligas del padrón (o ninguna si la demo no lo cruza) y lo declara",
          all(l["ligaId"] in pad for l in rp["porLiga"]) and rp["ligasEvaluadas"], rp["ligasEvaluadas"][:3])
    rm = bt.correr_backtest(muestra=2, horizonte=1)
    check("--muestra acota los equipos", rm["equipos"] == 2, rm["equipos"])

    # calibración: logística sobre celdas, puntos enteros y tabla propuesta
    rc = bt.correr_backtest(horizonte=1, calibrar_=True)
    cal = rc["calibracion"]
    check("calibrar: coeficientes y puntos para las 7 señales", set(cal["coeficientes"]) == set(bt.SENALES)
          and all(isinstance(cal["puntosPropuestos"][s], int) and cal["puntosPropuestos"][s] >= 0 for s in bt.SENALES), cal.get("aviso"))
    check("calibrar: AUC del logit y de los puntos propuestos en [0, 1]",
          0 <= cal["aucLogit"] <= 1 and 0 <= cal["aucPuntosPropuestos"] <= 1, (cal["aucLogit"], cal["aucPuntosPropuestos"]))
    check("calibrar: la tabla por puntos cierra al total calibrado",
          sum(f["n"] for f in cal["porPuntosPropuestos"]) == cal["n"])
    check("calibrar: cada fila de puntos lleva un nivel y hay cortes propuestos",
          all(f["nivel"] in ("bajo", "medio", "alto", "muy alto") for f in cal["porPuntosPropuestos"]) and cal["cortesPropuestos"])
    check("calibrar: declara que es ajuste en muestra", "en muestra" in cal["aviso"])
    # la logística recupera un patrón conocido: celdas sintéticas donde solo una señal manda
    celdas = {}
    for k in (0, 1):
        for j in (0, 1):
            patron = (k, 0, j, 0, 0, 0, 0)
            n = 1000
            p = 0.3 + 0.4 * j          # solo la 3ª señal (rachaGeMediana) sube la tasa
            celdas[patron] = [n, int(n * p)]
    beta = bt._logistica(celdas)
    check("logística sintética: la señal que manda sale positiva (~1.7) y la que no, ~0",
          1.4 < beta[3] < 2.0 and abs(beta[1]) < 0.05, [round(b, 3) for b in beta])
    check("sin muestra suficiente: aviso, no coeficientes inventados", "aviso" in bt.calibrar(obs[:50]) and "coeficientes" not in bt.calibrar(obs[:50]))
    check("isotónica: aplana los retrocesos con media ponderada y respeta lo que ya crece",
          bt._isotonica([(0.2, 10), (0.6, 10), (0.4, 10), (0.9, 10)]) == [0.2, 0.5, 0.5, 0.9]
          and bt._isotonica([(0.1, 1), (0.2, 1), (0.3, 1)]) == [0.1, 0.2, 0.3])
    iso = [f["tasaIso"] for f in cal["porPuntosPropuestos"]]
    orden = ["bajo", "medio", "alto", "muy alto"]
    niveles = [orden.index(f["nivel"]) for f in cal["porPuntosPropuestos"]]
    check("los niveles por puntos propuestos no retroceden (van sobre la isotónica)",
          iso == sorted(iso) and niveles == sorted(niveles), list(zip(iso, niveles)))
    bt.imprimir(rc)

    # el informe se imprime sin romperse
    bt.imprimir(r)

    print(f"\n{fallos} FALLAS" if fallos else "\nTODO OK")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
