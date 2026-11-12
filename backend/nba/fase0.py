"""NBA · fase 0 · ¿la teoría SAD ve algo en la NBA que la cuota no? (docs/NBA_FASE0.md)

Solo mide; no construye nada. Corre sobre lo que bajó `backend.nba.descarga`
y responde, con el MISMO método que el backtest del 1X2 del fútbol
(docs/REVENTON.md §13: corte temporal 80/20, bootstrap emparejado por partido,
el mercado sobre los mismos partidos):

  0 · Inventario y localía: partidos y cuotas por temporada, cuánto gana el local.
  1 · GANADOR: ¿el nivel predice? ¿descanso, racha, K y reventón agregan al
      nivel? ¿y agregan SOBRE la cuota de cierre (lo único que importa para
      apostar)? Con una simulación plana contra la cuota, indicativa.
  2 · HÁNDICAP: ¿el motor sabe de qué lado cae la línea? (la cuota del
      hándicap es ~50/50 por construcción: la vara es ln 2 y el 52,4 % de -110).
  3 · REVENTÓN: con una racha abierta, ¿se corta más (o menos) de lo que la
      cuota dice? Tabla por largo de racha y logística mercado vs mercado + burbuja.

Sin fuga: todo lo de un partido sale de lo previo a él (backend.nba.motor);
la ESCALA_G se elige mirando solo el entrenamiento; la prueba es el 20 % más
reciente.

    python -m backend.nba.fase0                 # lee $SAD_NBA_DIR (./nba_data)
    python -m backend.nba.fase0 --json          # además, el resumen entero
Guarda $SAD_NBA_DIR/fase0.json y fase0.txt.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from datetime import datetime, timezone
from statistics import median

from backend.nba import descarga, motor

PRUEBA = 0.2
BOOTSTRAP = 500
RIDGE = 1e-2
NEWTON_ITER = 25
TEMPORADA_MIN = 2017            # 2015-16 es el arranque: ahí se llenan las ventanas de 20
ESCALAS_G = (0.0, 2.0, 5.0, 10.0, 20.0, 40.0)
UMBRAL_VALOR = 0.03             # ventaja mínima sobre la cuota para la simulación plana
REVENTONES_MIN = 3              # como MUESTRA_BAJA del fútbol: con menos no hay base del equipo
CASAS_FUERA = ("live", "opening")


# ── la cuota ─────────────────────────────────────────────────────────────────

def decimal(americana: float | None) -> float | None:
    if americana is None or americana == 0 or abs(americana) < 100:
        return None
    return 1 + (americana / 100 if americana > 0 else 100 / -americana)


def consenso(filas: list[dict]) -> dict | None:
    """Ganador sin margen (1/cuota normalizado) y hándicap del local: la
    MEDIANA entre casas (una casa vieja o mal cargada no mueve la mediana).
    Afuera las líneas en vivo y la de apertura."""
    filas = [f for f in filas if not any(x in (f.get("casa") or "").lower() for x in CASAS_FUERA)]
    pl, decl, decv, spr, sdl, sdv = [], [], [], [], [], []
    for f in filas:
        dl, dv = decimal(f.get("mlLocal")), decimal(f.get("mlVisita"))
        if dl and dv:
            il, iv = 1 / dl, 1 / dv
            pl.append(il / (il + iv))
            decl.append(dl)
            decv.append(dv)
        if f.get("spreadLocal") is not None:
            spr.append(f["spreadLocal"])
            a, b = decimal(f.get("spreadCuotaLocal")), decimal(f.get("spreadCuotaVisita"))
            if a and b:
                sdl.append(a)
                sdv.append(b)
    if not pl and not spr:
        return None
    return {"pLocal": median(pl) if pl else None,
            "decLocal": median(decl) if decl else None, "decVisita": median(decv) if decv else None,
            "spreadLocal": median(spr) if spr else None,
            "decSpreadLocal": median(sdl) if sdl else 1.909, "decSpreadVisita": median(sdv) if sdv else 1.909,
            "casas": len(filas)}


# ── logística binaria (Newton con ridge), sin dependencias ──────────────────

def _resolver(A: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        if abs(M[c][c]) < 1e-12:
            continue
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                if f:
                    for k in range(c, n + 1):
                        M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]


def _sig(z: float) -> float:
    z = max(-30.0, min(30.0, z))
    return 1 / (1 + math.exp(-z))


def ajustar(X: list[list[float]], y: list[int]) -> list[float]:
    p = len(X[0])
    beta = [0.0] * p
    for _ in range(NEWTON_ITER):
        g = [0.0] * p
        H = [[0.0] * p for _ in range(p)]
        for x, yi in zip(X, y):
            pr = _sig(sum(b * v for b, v in zip(beta, x)))
            r, w = yi - pr, pr * (1 - pr)
            for i in range(p):
                g[i] += r * x[i]
                for j in range(i, p):
                    H[i][j] += w * x[i] * x[j]
        for i in range(p):
            for j in range(i):
                H[i][j] = H[j][i]
            g[i] -= RIDGE * beta[i]
            H[i][i] += RIDGE
        paso = _resolver(H, g)
        beta = [b + d for b, d in zip(beta, paso)]
        if max(abs(d) for d in paso) < 1e-8:
            break
    return beta


def escala_de(obs: list[dict], vars_: list[str]) -> dict:
    out = {}
    for v in vars_:
        xs = [o[v] for o in obs]
        m = sum(xs) / len(xs)
        out[v] = (m, math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs)) or 1.0)
    return out


def matriz(obs: list[dict], vars_: list[str], esc: dict) -> list[list[float]]:
    return [[1.0] + [(o[v] - esc[v][0]) / esc[v][1] for v in vars_] for o in obs]


def modelo(train: list[dict], test: list[dict], vars_: list[str], clave_y: str = "y") -> dict:
    """Ajusta en `train`, devuelve probabilidades y pérdidas por partido en `test`."""
    esc = escala_de(train, vars_) if vars_ else {}
    beta = ajustar(matriz(train, vars_, esc), [o[clave_y] for o in train])
    probs = [_sig(sum(b * v for b, v in zip(beta, x))) for x in matriz(test, vars_, esc)]
    ll = [-math.log(max(p if o[clave_y] else 1 - p, 1e-12)) for p, o in zip(probs, test)]
    br = [(p - o[clave_y]) ** 2 for p, o in zip(probs, test)]
    ac = [int((p > 0.5) == bool(o[clave_y])) for p, o in zip(probs, test)]
    return {"probs": probs, "ll": ll, "br": br, "ac": ac,
            "coef": {v: round(b, 4) for v, b in zip(["intercepto"] + vars_, beta)}}


def resumen(m: dict) -> dict:
    n = len(m["ll"])
    return {"logLoss": round(sum(m["ll"]) / n, 5), "brier": round(sum(m["br"]) / n, 5),
            "acierto": round(sum(m["ac"]) / n, 4), "coef": m["coef"]}


def ic_dif(a: list[float], b: list[float], semilla: int = 7) -> dict:
    """b − a por partido (negativo = b mejor), bootstrap emparejado."""
    n = len(a)
    if not n:
        return {"media": None, "ic95": None, "n": 0}
    dif = [y - x for x, y in zip(a, b)]
    rnd = random.Random(semilla)
    medias = sorted(sum(dif[rnd.randrange(n)] for _ in range(n)) / n for _ in range(BOOTSTRAP))
    lo, hi = medias[int(0.025 * BOOTSTRAP)], medias[int(0.975 * BOOTSTRAP) - 1]
    return {"media": round(sum(dif) / n, 5), "ic95": [round(lo, 5), round(hi, 5)], "n": n,
            "veredicto": "mejora" if hi < 0 else "empeora" if lo > 0 else "nada (el IC cruza 0)"}


def roi(apuestas: list[tuple[float, int]], semilla: int = 11) -> dict:
    """[(cuota decimal, ganó)] a 1 unidad. ROI con IC bootstrap."""
    n = len(apuestas)
    if not n:
        return {"apuestas": 0, "roi": None, "ic95": None}
    gan = [(d - 1) if w else -1.0 for d, w in apuestas]
    rnd = random.Random(semilla)
    medias = sorted(sum(gan[rnd.randrange(n)] for _ in range(n)) / n for _ in range(BOOTSTRAP))
    return {"apuestas": n, "aciertos": sum(w for _, w in apuestas), "roi": round(sum(gan) / n, 4),
            "ic95": [round(medias[int(0.025 * BOOTSTRAP)], 4), round(medias[int(0.975 * BOOTSTRAP) - 1], 4)]}


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _slog(x: float) -> float:
    return math.copysign(math.log1p(abs(x)), x)


# ── las observaciones ────────────────────────────────────────────────────────

def _lado(f: dict, rival: dict) -> dict:
    """Variables de la teoría para un lado, con el signo de la racha a favor
    de ESE equipo (positivo = empuja a que gane)."""
    s = f["signo"]
    con_base = f["reventonesSigno"] >= REVENTONES_MIN
    sobre = 1.0 if con_base and f["racha"] >= f["medianaPartidos"] else 0.0
    k_rel = (abs(f["k"]) / f["medianaKPico"]) if con_base and f["medianaKPico"] else 0.0
    # rival en la dirección del riesgo (como el fútbol): racha + con rival más
    # fuerte que con el que suele cortarse, racha − con rival más flojo
    delta = 0.0
    if con_base and f["medianaNivelRival"] is not None and f["nivelRival"] is not None:
        delta = s * (f["nivelRival"] - f["medianaNivelRival"])
    return {"racha": s * f["racha"], "k": _slog(f["k"]), "kCond": _slog(f["kCond"]),
            "descanso": f["descanso"] if f["descanso"] is not None else motor.DESCANSO_TOPE,
            "b2b": 1.0 if f["descanso"] is not None and f["descanso"] <= 1 else 0.0,
            "sobreMediana": s * sobre, "kSobreMediana": s * k_rel, "rivalRiesgo": delta}


def observaciones(partidos: list[dict], previos: dict, cuotas: dict) -> list[dict]:
    obs = []
    for p in partidos:
        if (p["temporada"] or 0) < TEMPORADA_MIN:
            continue
        f = previos[p["id"]]
        L, V = f["local"], f["visita"]
        if L["nivel"] is None or V["nivel"] is None:
            continue
        c = consenso(cuotas.get(p["id"], []))
        o = {"id": p["id"], "fecha": p["fecha"], "temporada": p["temporada"], "tipo": p["tipo"],
             "y": int(p["ptsLocal"] > p["ptsVisita"]), "margen": p["ptsLocal"] - p["ptsVisita"],
             "d": L["nivel"] - V["nivel"], "neutral": 1.0 if p["neutral"] else 0.0,
             "playoffs": 1.0 if p["tipo"] != "regular" else 0.0, "cuota": c, "previoL": L, "previoV": V}
        for lado, mio, otro in (("L", L, V), ("V", V, L)):
            for k, v in _lado(mio, otro).items():
                o[k + lado] = v
        obs.append(o)
    return obs


V_MOTOR = ["d", "neutral"]
V_DESCANSO = V_MOTOR + ["b2bL", "b2bV", "descansoL", "descansoV"]
V_RACHA = V_DESCANSO + ["rachaL", "rachaV", "kL", "kV", "kCondL", "kCondV"]
V_TEORIA = V_RACHA + ["sobreMedianaL", "sobreMedianaV", "kSobreMedianaL", "kSobreMedianaV",
                      "rivalRiesgoL", "rivalRiesgoV"]


def _partir(obs: list[dict]) -> tuple[list[dict], list[dict]]:
    corte = int(len(obs) * (1 - PRUEBA))
    return obs[:corte], obs[corte:]


def elegir_escala_g(partidos: list[dict], cuotas: dict) -> dict:
    """La ESCALA_G que mejor predice el ganador SOLO con el nivel, mirando solo
    el entrenamiento (sus primeros 80 % contra sus últimos 20 %)."""
    tabla = {}
    for e in ESCALAS_G:
        obs = observaciones(partidos, motor.construir(partidos, escala_g=e), cuotas)
        train, _ = _partir(obs)
        a, b = _partir(train)
        tabla[e] = resumen(modelo(a, b, V_MOTOR))["logLoss"]
    mejor = min(tabla, key=tabla.get)
    return {"elegida": mejor, "logLossValidacion": {str(k): v for k, v in tabla.items()}}


# ── 0 · inventario ──────────────────────────────────────────────────────────

def inventario(partidos: list[dict], cuotas: dict) -> dict:
    por = {}
    for p in partidos:
        t = por.setdefault(p["temporada"], {"partidos": 0, "playoffs": 0, "neutral": 0, "conGanador": 0,
                                            "conHandicap": 0, "ganaLocal": 0, "noNeutral": 0, "margenLocal": 0})
        t["partidos"] += 1
        t["playoffs"] += p["tipo"] != "regular"
        t["neutral"] += bool(p["neutral"])
        c = consenso(cuotas.get(p["id"], []))
        t["conGanador"] += bool(c and c["pLocal"] is not None)
        t["conHandicap"] += bool(c and c["spreadLocal"] is not None)
        if not p["neutral"]:
            t["noNeutral"] += 1
            t["ganaLocal"] += p["ptsLocal"] > p["ptsVisita"]
            t["margenLocal"] += p["ptsLocal"] - p["ptsVisita"]
    for t in por.values():
        n = t.pop("noNeutral") or 1
        t["pctGanaLocal"] = round(t.pop("ganaLocal") / n, 4)
        t["margenLocalMedio"] = round(t.pop("margenLocal") / n, 2)
    return {str(k): v for k, v in sorted(por.items())}


# ── 1 · ganador ─────────────────────────────────────────────────────────────

def ganador(obs: list[dict]) -> dict:
    con = [o for o in obs if o["cuota"] and o["cuota"]["pLocal"] is not None]
    for o in con:
        o["mercado"] = _logit(o["cuota"]["pLocal"])
    train, test = _partir(con)
    mods = {"G0 · motor (nivel + localía)": V_MOTOR, "G1 · + descanso": V_DESCANSO,
            "G2 · + racha y K": V_RACHA, "G3 · + reventón (la teoría entera)": V_TEORIA,
            "MK0 · mercado solo": ["mercado"], "MK1 · mercado + la teoría": ["mercado"] + V_TEORIA,
            "MK2 · mercado + descanso": ["mercado", "b2bL", "b2bV", "descansoL", "descansoV"]}
    res = {n: modelo(train, test, v) for n, v in mods.items()}
    n = list(mods)
    comp = {f"{b} vs {a}": ic_dif(res[a]["ll"], res[b]["ll"]) for a, b in (
        (n[0], n[1]), (n[1], n[2]), (n[2], n[3]), (n[0], n[3]), (n[4], n[0]), (n[4], n[5]), (n[4], n[6]))}
    # simulación plana: cuando MK1 ve ≥ 3 puntos más que la cuota sin margen
    apuestas = []
    for p, o in zip(res[n[5]]["probs"], test):
        c = o["cuota"]
        if p - c["pLocal"] >= UMBRAL_VALOR and c["decLocal"]:
            apuestas.append((c["decLocal"], o["y"]))
        elif (1 - p) - (1 - c["pLocal"]) >= UMBRAL_VALOR and c["decVisita"]:
            apuestas.append((c["decVisita"], 1 - o["y"]))
    return {"partidos": len(con), "entrenamiento": len(train), "prueba": len(test),
            "corte": test[0]["fecha"][:10], "hasta": test[-1]["fecha"][:10],
            "ganaLocalPrueba": round(sum(o["y"] for o in test) / len(test), 4),
            "modelos": {k: resumen(v) for k, v in res.items()}, "comparaciones": comp,
            "simulacionPlana": {"regla": f"MK1 ve ≥ {UMBRAL_VALOR:.0%} más que la cuota sin margen, a la cuota mediana",
                                **roi(apuestas)}}


# ── 2 · hándicap ────────────────────────────────────────────────────────────

def _regresion(train: list[dict], vars_: list[str]) -> tuple[list[float], dict]:
    """Margen del local ~ variables (mínimos cuadrados con ridge chico)."""
    esc = escala_de(train, vars_)
    X = matriz(train, vars_, esc)
    p = len(X[0])
    A = [[sum(x[i] * x[j] for x in X) + (RIDGE if i == j else 0) for j in range(p)] for i in range(p)]
    b = [sum(x[i] * o["margen"] for x, o in zip(X, train)) for i in range(p)]
    return _resolver(A, b), esc


def handicap(obs: list[dict]) -> dict:
    con = []
    for o in obs:
        c = o["cuota"]
        if not c or c["spreadLocal"] is None:
            continue
        cubre = o["margen"] + c["spreadLocal"]
        if cubre == 0:
            continue                       # push: se devuelve la apuesta
        con.append({**o, "yH": int(cubre > 0)})
    train, test = _partir(con)
    out = {"partidos": len(con), "entrenamiento": len(train), "prueba": len(test),
           "corte": test[0]["fecha"][:10], "cubreLocalPrueba": round(sum(o["yH"] for o in test) / len(test), 4)}
    base = modelo(train, test, [], "yH")
    res = {"H0 · base (frecuencia)": base}
    for nombre, vars_ in (("H1 · motor (nivel + localía)", V_MOTOR), ("H2 · la teoría entera", V_TEORIA)):
        beta, esc = _regresion(train, vars_)
        for o in train + test:
            x = [1.0] + [(o[v] - esc[v][0]) / esc[v][1] for v in vars_]
            o["ventaja"] = sum(b * v for b, v in zip(beta, x)) + o["cuota"]["spreadLocal"]
        res[nombre] = modelo(train, test, ["ventaja"], "yH")
        res[nombre]["rmseMargen"] = round(math.sqrt(sum(
            (o["ventaja"] - o["cuota"]["spreadLocal"] - o["margen"]) ** 2 for o in test) / len(test)), 2)
    # la línea misma como predictor del margen (la vara del mercado)
    out["rmseMargenDeLaLinea"] = round(math.sqrt(sum((-o["cuota"]["spreadLocal"] - o["margen"]) ** 2
                                                     for o in test) / len(test)), 2)
    n = list(res)
    out["modelos"] = {k: {**resumen(v), **({"rmseMargen": v["rmseMargen"]} if "rmseMargen" in v else {})}
                      for k, v in res.items()}
    out["comparaciones"] = {f"{b} vs {n[0]}": ic_dif(res[n[0]]["ll"], res[b]["ll"]) for b in n[1:]}
    out["logLossMonedaAlAire"] = round(math.log(2), 5)
    sims = {}
    for nombre in n[1:]:
        ap = []
        for p, o in zip(res[nombre]["probs"], test):
            c = o["cuota"]
            if p * c["decSpreadLocal"] - 1 >= UMBRAL_VALOR:
                ap.append((c["decSpreadLocal"], o["yH"]))
            elif (1 - p) * c["decSpreadVisita"] - 1 >= UMBRAL_VALOR:
                ap.append((c["decSpreadVisita"], 1 - o["yH"]))
        sims[nombre] = roi(ap)
    out["simulacionPlana"] = {"regla": f"valor esperado ≥ {UMBRAL_VALOR:.0%} a la cuota mediana del hándicap", **sims}
    return out


# ── 3 · reventón ────────────────────────────────────────────────────────────

def _tramo(n: int) -> str:
    return "1" if n == 1 else "2" if n == 2 else "3" if n == 3 else "4-5" if n <= 5 else "6-8" if n <= 8 else "9+"


def reventon(obs: list[dict]) -> dict:
    """Una observación por LADO con burbuja abierta y base propia (≥ 3
    reventones del signo). y = la racha se corta en este partido. La cuota
    del corte: perder para la racha +, ganar para la racha −."""
    filas = []
    for o in obs:
        c = o["cuota"]
        if not c or c["pLocal"] is None:
            continue
        for lado, f in (("L", o["previoL"]), ("V", o["previoV"])):
            if not f["signo"] or f["reventonesSigno"] < REVENTONES_MIN:
                continue
            gana = o["y"] if lado == "L" else 1 - o["y"]
            p_gana = c["pLocal"] if lado == "L" else 1 - c["pLocal"]
            corte = (1 - gana) if f["signo"] > 0 else gana
            p_corte = (1 - p_gana) if f["signo"] > 0 else p_gana
            filas.append({"fecha": o["fecha"], "signo": f["signo"], "racha": f["racha"], "y": corte,
                          "mercado": _logit(p_corte), "pMercado": p_corte,
                          "sobreMediana": 1.0 if f["racha"] >= f["medianaPartidos"] else 0.0,
                          "kSobreMediana": abs(f["k"]) / f["medianaKPico"] if f["medianaKPico"] else 0.0,
                          "rivalRiesgo": (f["signo"] * (f["nivelRival"] - f["medianaNivelRival"])
                                          if f["medianaNivelRival"] is not None and f["nivelRival"] is not None else 0.0),
                          "largo": math.log(f["racha"])})
    filas.sort(key=lambda r: r["fecha"])
    tabla = {}
    for r in filas:
        t = tabla.setdefault(("+" if r["signo"] > 0 else "−") + " " + _tramo(r["racha"]), [0, 0, 0.0])
        t[0] += 1
        t[1] += r["y"]
        t[2] += r["pMercado"]
    orden = sorted(tabla, key=lambda k: (k[0] != "+", ["1", "2", "3", "4-5", "6-8", "9+"].index(k[2:])))
    por_largo = {k: {"n": tabla[k][0], "seCorta": round(tabla[k][1] / tabla[k][0], 4),
                     "mercadoDecia": round(tabla[k][2] / tabla[k][0], 4),
                     "diferencia": round((tabla[k][1] - tabla[k][2]) / tabla[k][0], 4)} for k in orden}
    train, test = _partir(filas)
    teoria = ["sobreMediana", "kSobreMediana", "rivalRiesgo", "largo"]
    res = {"R0 · mercado solo": modelo(train, test, ["mercado"]),
           "R1 · mercado + burbuja": modelo(train, test, ["mercado"] + teoria),
           "R2 · burbuja sola (sin cuota)": modelo(train, test, teoria)}
    n = list(res)
    return {"observaciones": len(filas), "entrenamiento": len(train), "prueba": len(test),
            "tasaCortePrueba": round(sum(r["y"] for r in test) / len(test), 4),
            "porLargo": por_largo, "modelos": {k: resumen(v) for k, v in res.items()},
            "comparaciones": {f"{n[1]} vs {n[0]}": ic_dif(res[n[0]]["ll"], res[n[1]]["ll"]),
                              f"{n[0]} vs {n[2]}": ic_dif(res[n[2]]["ll"], res[n[0]]["ll"])}}


# ── corrida ─────────────────────────────────────────────────────────────────

def correr(base: str | None = None) -> dict:
    partidos = descarga.cargar_partidos(base)
    cuotas = descarga.cargar_cuotas(base)
    if len(partidos) < 500:
        raise SystemExit(f"solo {len(partidos)} partidos en {base or descarga.carpeta()}: correr antes "
                         "python -m backend.nba.descarga")
    esc = elegir_escala_g(partidos, cuotas)
    previos = motor.construir(partidos, escala_g=esc["elegida"])
    obs = observaciones(partidos, previos, cuotas)
    return {"generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "fuente": "ESPN (marcador por día y cuotas de cierre por partido)",
            "parametros": {"ventana": motor.VENTANA, "ultimos": motor.ULTIMOS, "escalaG": esc,
                           "escalaMargen": motor.ESCALA_MARGEN, "visitaMult": motor.VISITA_MULT,
                           "temporadaMin": TEMPORADA_MIN, "prueba": PRUEBA, "bootstrap": BOOTSTRAP},
            "inventario": inventario(partidos, cuotas),
            "ganador": ganador(obs), "handicap": handicap(obs), "reventon": reventon(obs)}


def _ic(c: dict) -> str:
    return f"{c['media']:+.4f} [{c['ic95'][0]:+.4f}, {c['ic95'][1]:+.4f}] → {c['veredicto']}"


def texto(r: dict) -> str:
    L = [f"NBA · fase 0 · {r['generado']}", ""]
    L.append("0 · INVENTARIO (temporada = año en que termina)")
    L.append("  temp  partidos  playoffs  neutral  c/ganador  c/hándicap  gana local  margen local")
    for t, v in r["inventario"].items():
        L.append(f"  {t}  {v['partidos']:8d}  {v['playoffs']:8d}  {v['neutral']:7d}  {v['conGanador']:9d}  "
                 f"{v['conHandicap']:10d}  {v['pctGanaLocal']:10.1%}  {v['margenLocalMedio']:+12.2f}")
    e = r["parametros"]["escalaG"]
    L += ["", f"ESCALA_G elegida en el entrenamiento: {e['elegida']} (log-loss de validación: {e['logLossValidacion']})"]
    for clave, titulo in (("ganador", "1 · GANADOR"), ("handicap", "2 · HÁNDICAP")):
        g = r[clave]
        L += ["", f"{titulo} · {g['partidos']} partidos · prueba {g['prueba']} desde {g['corte']}"]
        if clave == "handicap":
            L.append(f"  error del margen (RMSE, pts): la línea {g['rmseMargenDeLaLinea']} · "
                     + " · ".join(f"{k.split(' · ')[0]} {v['rmseMargen']}" for k, v in g["modelos"].items()
                                  if "rmseMargen" in v))
            L.append(f"  cubre el local en la prueba: {g['cubreLocalPrueba']:.1%} · moneda al aire = log-loss {g['logLossMonedaAlAire']}")
        for k, v in g["modelos"].items():
            L.append(f"  {k:40s} log-loss {v['logLoss']:.4f}  Brier {v['brier']:.4f}  acierto {v['acierto']:.1%}")
        for k, v in g["comparaciones"].items():
            L.append(f"  {k}: {_ic(v)}")
        s = g["simulacionPlana"]
        L.append(f"  simulación plana ({s['regla']}):")
        for k, v in s.items():
            if isinstance(v, dict) and v.get("apuestas"):
                L.append(f"    {k}: {v['apuestas']} apuestas, ROI {v['roi']:+.1%} IC [{v['ic95'][0]:+.1%}, {v['ic95'][1]:+.1%}]")
        if s.get("apuestas"):
            L.append(f"    {s['apuestas']} apuestas, ROI {s['roi']:+.1%} IC [{s['ic95'][0]:+.1%}, {s['ic95'][1]:+.1%}]")
    rv = r["reventon"]
    L += ["", f"3 · REVENTÓN · {rv['observaciones']} lados con burbuja y base · prueba {rv['prueba']}"]
    L.append("  racha        n   se corta   la cuota decía   diferencia")
    for k, v in rv["porLargo"].items():
        L.append(f"  {k:8s} {v['n']:6d}   {v['seCorta']:7.1%}   {v['mercadoDecia']:13.1%}   {v['diferencia']:+9.1%}")
    for k, v in rv["modelos"].items():
        L.append(f"  {k:32s} log-loss {v['logLoss']:.4f}  acierto {v['acierto']:.1%}  coef {v['coef']}")
    for k, v in rv["comparaciones"].items():
        L.append(f"  {k}: {_ic(v)}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = correr()
    base = descarga.carpeta()
    with open(os.path.join(base, "fase0.json"), "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    t = texto(r)
    with open(os.path.join(base, "fase0.txt"), "w") as f:
        f.write(t + "\n")
    print(t)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
