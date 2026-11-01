"""Las otras burbujas contadas (backend/analisis/familias.py): el texto dice lo
que el backtest midió, y el espejo TS (src/lib/familias.ts) da lo mismo sobre
scripts/casos_familias.json.

    python -m backend.test_familias            # chequea
    python -m backend.test_familias --regenerar  # reescribe los vectores dorados
"""
import json
import os
import random
import sys

from backend.analisis.familias import describir

CASOS = os.path.join(os.path.dirname(__file__), "..", "scripts", "casos_familias.json")
fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _filas(res, conds):
    return [{"fecha": f"2025-{1 + i // 28:02d}-{1 + i % 28:02d}T20:00:00Z", "condicion": c,
             "golesFavor": a, "golesContra": b} for i, ((a, b), c) in enumerate(zip(res, conds))]


def casos():
    rnd = random.Random(2026)
    out = []
    for i in range(12):
        n = rnd.randint(8, 70)
        res = [(rnd.choice([0, 0, 1, 1, 1, 2, 2, 3, 4]), rnd.choice([0, 0, 0, 1, 1, 2, 3])) for _ in range(n)]
        conds = [rnd.choice(["Local", "Visita"]) for _ in range(n)]
        if i % 4 == 0:   # una racha larga al final, para que haya récord
            res[-6:] = [(2, 0)] * 6
            conds[-6:] = ["Local"] * 6
        out.append({"nombre": f"Equipo {i}", "condicion": ["L", "V", None][i % 3], "filas": _filas(res, conds)})
    # Everton antes del 0-2 con Chelsea: 4 de local sin perder, récord previo 3
    loc = [(1, 0), (1, 1), (2, 0), (0, 1), (1, 0), (0, 1), (2, 1), (1, 1), (0, 2), (1, 0), (1, 1), (2, 2), (1, 0)]
    out.append({"nombre": "Everton", "condicion": "L", "filas": _filas(loc, ["Local"] * len(loc))})
    # una racha de 7 de local sin perder sobre un récord de 5: CUIDADO (texto del TS incluido)
    larga = [(1, 0), (0, 1)] * 2 + [(1, 1)] * 5 + [(0, 2)] + [(2, 0), (0, 1), (1, 1)] + [(0, 1)] + [(1, 0)] * 7
    out.append({"nombre": "Racha larga", "condicion": "L", "filas": _filas(larga, ["Local"] * len(larga))})
    # incidencias 420/450: sequía de «gana por 3+» en su récord pero HABITUAL para el equipo
    seq = ([(1, 0)] * 10 + [(3, 0)] + [(1, 0)] * 12 + [(3, 0)] + [(1, 1)] * 8 + [(4, 0)] + [(1, 0)] * 14)
    out.append({"nombre": "Sequía habitual", "condicion": "L", "filas": _filas(seq, ["Local"] * len(seq))})
    out.append({"nombre": "Vacío", "condicion": "V", "filas": []})
    return [{**c, "esperado": describir(c["filas"], c["condicion"], c["nombre"])} for c in out]


def main():
    if "--regenerar" in sys.argv:
        json.dump(casos(), open(CASOS, "w"), ensure_ascii=False, indent=1)
        print(f"vectores dorados reescritos en {CASOS}")
        return
    guardados = json.load(open(CASOS))
    check("los vectores dorados siguen siendo los del Python (si cambió la regla: --regenerar y el TS)",
          all(describir(c["filas"], c["condicion"], c["nombre"]) == c["esperado"] for c in guardados),
          [c["nombre"] for c in guardados if describir(c["filas"], c["condicion"], c["nombre"]) != c["esperado"]])
    ev = next(c for c in guardados if c["nombre"] == "Everton")["esperado"]
    np_local = next(f for f in ev["familias"] if f["familia"] == "noPierde" and f["ambito"] == "local")
    check("Everton: 4 de local sin perder, supera su récord de 3, y va destacada",
          np_local["partidos"] == 4 and np_local["record"] == "supera" and np_local["destacada"], np_local)
    check("un récord corto (4) va destacado pero SIN cuidado: no grita",
          not np_local["cuidado"] and "CUIDADO" not in np_local["texto"], np_local)
    from backend.analisis.familias import _texto, es_cuidado
    grande = {"valor": True, "partidos": 9, "maximoPrevio": 8, "burbujasPrevias": 4, "record": "supera",
              "frecuencia": 0.6, "n": 20, "probRacha": 0.0101, "improbable": True}
    t = _texto("Everton", "local", grande, "sin perder", "perdiendo")
    check("un récord grande (9, 5+) es CUIDADO con la carga, sin decir que revienta",
          es_cuidado(grande) and "CUIDADO con cargar" in t and "causa que buscar" in t and "revient" not in t, t)
    check("una burbuja grande que NO es récord no es cuidado",
          not es_cuidado({**grande, "record": "no"}))
    check("el perfil de doble oportunidad va primero y dice que SÍ agrega al 1X2",
          ev["lineas"][0].startswith("Perfil de doble oportunidad de local") and "SÍ agrega" in ev["lineas"][0],
          ev["lineas"][:1])
    check("sin próximo solo se cuenta el total y no hay perfil",
          all(f["ambito"] == "total" for c in guardados if c["condicion"] is None for f in c["esperado"]["familias"])
          and all("perfilDc" not in c["esperado"] for c in guardados if c["condicion"] is None))
    habitual = {**grande, "frecuencia": 0.8, "probRacha": 0.1342, "improbable": False}
    t = _texto("Everton", "local", habitual, "sin perder", "perdiendo")
    check("un récord grande pero HABITUAL para su frecuencia no es cuidado y lo dice (420, 450)",
          not es_cuidado(habitual) and "CUIDADO" not in t and "esperable" in t and "13 %" in t, t)
    gremio = {**grande, "valor": False, "frecuencia": 0.07, "partidos": 70, "probRacha": 0.006, "improbable": True,
              "record": "supera"}
    check("834: un estado que el equipo vive el 90 %+ (Grêmio, 70 de local sin ganar por 3+) no es CUIDADO "
          "aunque la racha salga improbable", not es_cuidado(gremio) and es_cuidado({**gremio, "frecuencia": 0.2}))
    sh = next(c for c in guardados if c["nombre"] == "Sequía habitual")["esperado"]
    g3 = next(f for f in sh["familias"] if f["familia"] == "gana3+" and f["ambito"] == "local")
    check("vectores: 14 sin ganar por 3+ en su récord, pero con 94 % de frecuencia: sin CUIDADO",
          g3["partidos"] == 14 and g3["record"] == "supera" and not g3["improbable"] and not g3["cuidado"]
          and "esperable" in g3["texto"], g3)
    rl = next(c for c in guardados if c["nombre"] == "Racha larga")["esperado"]
    check("los vectores dorados traen un caso con CUIDADO (lo prueba también el TS)",
          any(f["cuidado"] and "CUIDADO" in f["texto"] for f in rl["familias"]),
          [(f["familia"], f["partidos"], f["record"]) for f in rl["familias"] if f["destacada"]])
    vacio = next(c for c in guardados if c["nombre"] == "Vacío")["esperado"]
    check("sin historia no se inventa nada", not vacio["familias"] and not vacio["lineas"], vacio)
    check("la nota dice que es descripción, no riesgo", "descripción, no riesgo" in ev["nota"])
    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
