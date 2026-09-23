"""Backtest hacia atrás del reventón de burbuja (docs/REVENTON.md §8).

Recorre la historia de cada equipo y, en cada partido donde había una burbuja
ABIERTA, reconstruye la guía tal como estaba ANTES de ese partido (solo con
las filas previas, y con el rival real de ese partido como «próximo») para
compararla con lo que pasó: ¿reventó en ese partido (o dentro de --horizonte
partidos de la condición)?

Si la guía sirve, la tasa de reventón tiene que CRECER de «bajo» a «muy alto»
y cada señal (K ≥ mediana, racha ≥ mediana, rival en zona) tiene que reventar
más cuando está encendida que cuando no. Con eso se calibran los puntos y la
tolerancia de zona, y se contrasta la regla «a nivel alto o bajo mandan las
globales, a nivel medio las específicas»: se compara la separación de tasas
de la familia que manda contra la de las que no mandan.

Sin fuga: el nivel del equipo (para el bin) se toma del último nivel con
fecha ANTERIOR al partido, y la estabilidad va «sin dato» porque la plantilla
de hoy no es la de entonces — el backtest mide el RIESGO, no la confianza.

    python -m backend.backtest_burbuja --padron            # las ligas importantes (padrón de las cuotas en vivo)
    python -m backend.backtest_burbuja                     # todos los equipos con ≥ 12 filas
    python -m backend.backtest_burbuja --muestra 200 --horizonte 2
    python -m backend.backtest_burbuja --liga 281 --json salida.json
    SAD_DATA_DIR=demo_data python -m backend.backtest_burbuja   # contra la demo

También corre en el servidor, donde viven las .db: `GET /analisis/burbujas/backtest`
(token maestro; no está abierto a Cowork porque no es un dato del parte, es
calibración). El padrón de ligas es UNO solo: `extractor.ligas_vivo()`.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from bisect import bisect_left

import os

# importar backend.app arranca sus hilos de fondo (ingesta, backfill, en vivo)
# si el entorno los tiene configurados —en el servidor, siempre—: un backtest
# no puede disparar un backfill. Ver SIN_HILOS en backend/app.py.
os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend import db  # noqa: E402
from backend.analisis import burbuja  # noqa: E402
from backend.app import constantes_de, niveles_de  # noqa: E402

NIVELES = ["bajo", "medio", "alto", "muy alto"]
FAMILIAS = ("total", "local", "visita")
MIN_PREFIJO = 10          # filas previas mínimas para evaluar una burbuja


def padron() -> dict[int, str]:
    """Las ligas importantes con su nombre: el padrón de las cuotas en vivo,
    la ÚNICA lista (dos listas de «ligas importantes» se separan solas)."""
    from backend.ingesta.extractor import LIGAS, ligas_vivo
    return {lid: LIGAS.get(lid, f"liga {lid}") for lid in ligas_vivo()}


def _nombres_ligas(ids: set[int]) -> dict[int, str]:
    if not ids:
        return {}
    marks = ",".join("?" * len(ids))
    rows = db.query("sad", f"SELECT id, name FROM leagues WHERE id IN ({marks})", tuple(ids))
    return {r["id"]: r["name"] for r in rows}


def _equipos(min_filas: int, ligas: set[int] | None = None) -> list[int]:
    """Equipos con ≥ min_filas de constantes; con `ligas`, solo los que tienen
    partidos en alguna de ellas (su historia completa se usa igual)."""
    rows = db.query("constants", "SELECT team_id, COUNT(*) AS n FROM constants GROUP BY team_id HAVING n >= ?",
                    (min_filas,))
    ids = [r["team_id"] for r in rows]
    if not ligas:
        return ids
    marks = ",".join("?" * len(ligas))
    en_liga = {r["equipo_id"] for r in db.query(
        "discreto", f"SELECT DISTINCT equipo_id FROM processed_matches WHERE league_id IN ({marks})", tuple(ligas))}
    return [t for t in ids if t in en_liga]


def _bin_a_fecha(niveles: list[dict], fecha: str) -> int:
    """Último bin con fecha < fecha (sin fuga). Sin niveles previos: bin de 0.5 = 0."""
    fechas = [n["fecha"] for n in niveles]
    i = bisect_left(fechas, fecha)
    return niveles[i - 1]["bin"] if i > 0 else 0


def _revento(fila: dict, familia: str, signo: str) -> bool:
    v = float(fila["fusion"][burbuja.CLAVE_FUSION[familia]])
    return v == 0 or (v > 0) != (signo == "+")


def _en_condicion(fila: dict, familia: str) -> bool:
    return familia == "total" or fila["condicion"] == ("Local" if familia == "local" else "Visita")


def observar_equipo(team_id: int, horizonte: int, min_prefijo: int = MIN_PREFIJO,
                    ligas: set[int] | None = None) -> list[dict]:
    """Una observación por (partido con burbuja abierta, familia que ese partido mueve).
    Con `ligas`, solo se EVALÚAN los partidos de esas ligas; la historia previa
    (la K y sus reventones) usa todos los partidos, como en la app."""
    filas = list(reversed(constantes_de(team_id, 500)))
    niveles = list(reversed(niveles_de(team_id, 500)))
    estab = burbuja.estabilidad_de(None, "1970-01-01")
    obs = []
    for i in range(min_prefijo, len(filas)):
        fila = filas[i]
        if ligas and fila["ligaId"] not in ligas:
            continue
        prefijo = filas[:i]
        bin_ = _bin_a_fecha(niveles, fila["fecha"])
        proximo = {
            "fixtureId": fila["fixtureId"], "fecha": fila["fecha"], "rivalId": fila["rivalId"],
            "rival": fila["rivalNombre"], "condicion": "L" if fila["condicion"] == "Local" else "V",
            "nivelRival": float(fila["nivelRival"]),
        }
        mandan = burbuja.mandan_de(bin_, proximo)
        for familia in FAMILIAS:
            if not _en_condicion(fila, familia):
                continue
            fam = burbuja._analizar_familia(prefijo, familia, proximo, estab, franja=True)
            act, rg = fam["actual"], fam["riesgo"]
            if not act or not rg:
                continue
            # qué pasó: reventó en este partido o en los próximos `horizonte` de la condición
            siguientes = [f for f in filas[i:] if _en_condicion(f, familia)][:horizonte]
            revento = any(_revento(f, familia, act["signo"]) for f in siguientes)
            revento_ahora = _revento(fila, familia, act["signo"])
            base = fam["historial"]["positivo" if act["signo"] == "+" else "negativo"]
            obs.append({
                "equipoId": team_id, "fixtureId": fila["fixtureId"], "fecha": fila["fecha"], "ligaId": fila["ligaId"],
                "familia": familia, "signo": act["signo"], "manda": familia in mandan["familias"],
                "bin": bin_, "nivel": rg["nivel"], "puntos": rg["puntos"], "n": base["n"] if base else 0,
                "kGeMediana": bool(base) and abs(act["k"]) >= base["kPico"]["mediana"],
                "kGeMax": bool(base) and abs(act["k"]) >= base["kPico"]["max"],
                "rachaGeMediana": bool(base) and act["partidos"] >= base["partidos"]["mediana"],
                "rivalEnZona": None if not fam["rival"] else fam["rival"]["enZona"],
                "distanciaRival": None if not fam["rival"] else fam["rival"]["distancia"],
                "rachaGeMax": bool(base) and act["partidos"] >= base["partidos"]["max"],
                # distancia del rival EN LA DIRECCIÓN DEL RIESGO: burbuja + revienta ante
                # rivales más fuertes que la mediana; la − se corta ante más flojos
                "dRival": None if not fam["rival"] else (fam["rival"]["distancia"] if act["signo"] == "+" else -fam["rival"]["distancia"]),
                "kActual": abs(act["k"]), "partidos": act["partidos"],
                # la franja alta (docs/REVENTON.md §10.1): récord y percentiles estrictos
                "extremo": bool((fam["extremo"] or {}).get("activo")),
                "cerca": bool((fam["extremo"] or {}).get("cerca")),
                "pctK": (fam.get("_franja") or {}).get("pctK"),
                "pctR": (fam.get("_franja") or {}).get("pctR"),
                "revento": revento, "reventoAhora": revento_ahora,
            })
    return obs


# ── agregación ───────────────────────────────────────────────────────────────

def _tasa(sub: list[dict]) -> dict:
    n = len(sub)
    r = sum(1 for o in sub if o["revento"])
    return {"n": n, "reventones": r, "tasa": round(r / n, 3) if n else None}


def _auc(obs: list[dict], clave: str) -> float | None:
    """AUC de Mann-Whitney: P(puntos del que reventó > puntos del que no)."""
    pos = [o[clave] for o in obs if o["revento"]]
    neg = [o[clave] for o in obs if not o["revento"]]
    if not pos or not neg:
        return None
    neg_s = sorted(neg)
    tot = 0.0
    for p in pos:
        lo = bisect_left(neg_s, p)
        hi = bisect_left(neg_s, p + 1e-12)
        tot += lo + 0.5 * (hi - lo)
    # empates: bisect_left(p) cuenta los estrictamente menores; los iguales van a mitad
    return round(tot / (len(pos) * len(neg)), 3)


def _separacion(sub: list[dict]) -> float | None:
    """Tasa de (alto + muy alto) − tasa de bajo: cuánto separa la guía en ese grupo."""
    alto = [o for o in sub if o["nivel"] in ("alto", "muy alto")]
    bajo = [o for o in sub if o["nivel"] == "bajo"]
    if not alto or not bajo:
        return None
    return round(_tasa(alto)["tasa"] - _tasa(bajo)["tasa"], 3)


def _por_liga(con_base: list[dict], nombres: dict[int, str]) -> list[dict]:
    """Por liga: tasa base, tasa en bajo, tasa en alto/muy alto, separación y AUC.
    Ordenado por n; con n chico la separación es ruido y se ve por el n."""
    grupos: dict[int, list[dict]] = {}
    for o in con_base:
        grupos.setdefault(o["ligaId"], []).append(o)
    salida = []
    for lid, g in grupos.items():
        salida.append({
            "ligaId": lid, "liga": nombres.get(lid, f"liga {lid}"),
            "todas": _tasa(g),
            "bajo": _tasa([o for o in g if o["nivel"] == "bajo"]),
            "altoMuyAlto": _tasa([o for o in g if o["nivel"] in ("alto", "muy alto")]),
            "separacion": _separacion(g), "auc": _auc(g, "puntos"),
        })
    return sorted(salida, key=lambda x: -x["todas"]["n"])


# ── la franja alta: con qué umbral avisar «cerca del extremo» ─────────────────
# La K no adelanta el reventón (§8), así que el umbral NO se elige por tasa:
# se elige por RUIDO. Un aviso que salta en un tercio de los partidos se deja
# de leer (la regla del latido). Por cada umbral candidato: en qué fracción de
# las burbujas abiertas saltaría (sin contar las que ya son récord) y cuánto
# revientan ahí, al lado de la tasa del récord y de la del resto.
UMBRALES_CERCA = (75, 80, 85, 90, 95)
TECHO_AVISO = 0.10   # un aviso ámbar que salta en más del 10 % de las burbujas es ruido


def _franja_alta(con_base: list[dict]) -> dict:
    con = [o for o in con_base if o.get("pctK") is not None]
    n = len(con)
    if not n:
        return {"n": 0}
    rec = [o for o in con if o["extremo"]]
    no_rec = [o for o in con if not o["extremo"]]
    umbrales = []
    for u in UMBRALES_CERCA:
        k_ = [o for o in no_rec if o["pctK"] >= u]
        r_ = [o for o in no_rec if o["pctR"] >= u]
        am = [o for o in no_rec if o["pctK"] >= u or o["pctR"] >= u]
        umbrales.append({"umbral": u,
                         "soloK": {**_tasa(k_), "frecuencia": round(len(k_) / n, 3)},
                         "soloRacha": {**_tasa(r_), "frecuencia": round(len(r_) / n, 3)},
                         "kORacha": {**_tasa(am), "frecuencia": round(len(am) / n, 3)}})
    # propuesta: el umbral más bajo cuyo aviso (K o racha) no pasa del techo
    ok = [u for u in umbrales if u["kORacha"]["frecuencia"] <= TECHO_AVISO]
    return {
        "n": n,
        "record": {**_tasa(rec), "frecuencia": round(len(rec) / n, 3)},
        "resto": _tasa([o for o in no_rec if not o["cerca"]]),
        "cercaVigente": {**_tasa([o for o in no_rec if o["cerca"]]),
                         "frecuencia": round(sum(1 for o in no_rec if o["cerca"]) / n, 3)},
        "umbrales": umbrales,
        "techo": TECHO_AVISO,
        "propuesto": ok[0]["umbral"] if ok else None,
        "aviso": ("el umbral se elige por ruido, no por tasa: la K no adelanta el reventón (§8). "
                  "Propuesto = el más bajo cuyo aviso salta en ≤ el techo de las burbujas abiertas"),
    }


def resumir(obs: list[dict], horizonte: int, nombres: dict[int, str] | None = None) -> dict:
    con_base = [o for o in obs if o["nivel"] != "sin base"]
    por_nivel = {nv: _tasa([o for o in con_base if o["nivel"] == nv]) for nv in NIVELES}
    tasas = [por_nivel[nv]["tasa"] for nv in NIVELES if por_nivel[nv]["tasa"] is not None]
    monotona = all(a <= b for a, b in zip(tasas, tasas[1:])) and len(tasas) >= 2
    senales = {}
    for s in ("kGeMediana", "kGeMax", "rachaGeMediana", "rivalEnZona"):
        con = [o for o in con_base if o[s] is True]
        sin = [o for o in con_base if o[s] is False]
        senales[s] = {"encendida": _tasa(con), "apagada": _tasa(sin),
                      "lift": round(_tasa(con)["tasa"] - _tasa(sin)["tasa"], 3) if con and sin else None}
    familias = {f: {"todas": _tasa([o for o in con_base if o["familia"] == f]),
                    "separacion": _separacion([o for o in con_base if o["familia"] == f])} for f in FAMILIAS}
    manda = {k: {"todas": _tasa(g), "separacion": _separacion(g), "auc": _auc(g, "puntos")}
             for k, g in (("manda", [o for o in con_base if o["manda"]]),
                          ("noManda", [o for o in con_base if not o["manda"]]))}
    # la regla de nivel, mirada del otro lado: en equipos de nivel medio, ¿la
    # específica separa más que la total? y en extremos, ¿al revés?
    medio = [o for o in con_base if 2 < o["bin"] < 7]
    extremo = [o for o in con_base if not (2 < o["bin"] < 7)]
    regla_nivel = {
        "nivelMedio": {"total": _separacion([o for o in medio if o["familia"] == "total"]),
                       "especificas": _separacion([o for o in medio if o["familia"] != "total"])},
        "nivelExtremo": {"total": _separacion([o for o in extremo if o["familia"] == "total"]),
                         "especificas": _separacion([o for o in extremo if o["familia"] != "total"])},
    }
    return {
        "horizonte": horizonte,
        "observaciones": len(obs),
        "sinBase": len(obs) - len(con_base),
        "tasaBase": _tasa(con_base),
        "porSigno": {s: _tasa([o for o in con_base if o["signo"] == s]) for s in ("+", "-")},
        "porNivel": por_nivel,
        "monotona": monotona,
        "porPuntos": {str(p): _tasa([o for o in con_base if o["puntos"] == p])
                      for p in range(0, max((o["puntos"] for o in con_base), default=0) + 1)},
        "aucPuntos": _auc(con_base, "puntos"),
        "senales": senales,
        "porFamilia": familias,
        "reglaManda": manda,
        "reglaNivel": regla_nivel,
        "porMuestra": {"n<3": _tasa([o for o in con_base if o["n"] < 3]),
                       "3-5": _tasa([o for o in con_base if 3 <= o["n"] < 6]),
                       "≥6": _tasa([o for o in con_base if o["n"] >= 6])},
        "porLiga": _por_liga(con_base, nombres or {}),
        "franjaAlta": _franja_alta(con_base),
    }


def correr(equipos: list[int], horizonte: int, min_prefijo: int = MIN_PREFIJO,
           ligas: set[int] | None = None, nombres: dict[int, str] | None = None) -> tuple[list[dict], dict]:
    obs = []
    for t in equipos:
        obs.extend(observar_equipo(t, horizonte, min_prefijo, ligas))
    if nombres is None:
        nombres = _nombres_ligas({o["ligaId"] for o in obs})
    return obs, resumir(obs, horizonte, nombres)


# ── calibración (--calibrar) ─────────────────────────────────────────────────
# Regresión logística sobre las señales de la guía, con el rival GRADUADO por
# distancia a la mediana de reventón (lejos = referencia · zona · fuerte · muy
# fuerte). Como todas las señales son binarias, las observaciones se agrupan
# por patrón (≤ 2^4·4 = 64 celdas) y Newton-Raphson converge en un puñado de
# iteraciones sin numpy. Es AJUSTE EN MUESTRA: sirve para ver qué pesa y
# proponer puntos enteros, no para prometer una tasa.

SENALES = ["kGeMediana", "kGeMax", "rachaGeMediana", "rachaGeMax", "rivalZona", "rivalFuerte", "rivalMuyFuerte"]
RIVAL_FUERTE = 0.45           # distancia a la mediana desde la que el rival es «muy fuerte»
PASO_PUNTO = 0.25             # un punto por cada 0.25 de log-odds (≈ 6 % de tasa cerca del 50 %)
RIDGE = 1e-3
NEWTON_ITER = 12


def _senales_de(o: dict) -> tuple[int, ...] | None:
    d = o["dRival"]
    if d is None:
        return None
    tol = burbuja.ZONA_TOLERANCIA
    return (
        int(o["kGeMediana"]), int(o["kGeMax"]), int(o["rachaGeMediana"]), int(o["rachaGeMax"]),
        int(-tol <= d < tol), int(tol <= d < RIVAL_FUERTE), int(d >= RIVAL_FUERTE),
    )


def _resolver(A: list[list[float]], b: list[float]) -> list[float]:
    """Gauss con pivoteo parcial (sistemas chicos: 8×8)."""
    n = len(b)
    M = [fila[:] + [b[i]] for i, fila in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        if abs(M[c][c]) < 1e-12:
            continue
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]


def _logistica(celdas: dict[tuple[int, ...], list[int]]) -> list[float]:
    """β (intercepto + una por señal) por Newton-Raphson sobre celdas (n, reventones)."""
    p = len(SENALES) + 1
    beta = [0.0] * p
    for _ in range(NEWTON_ITER):
        g = [0.0] * p
        H = [[0.0] * p for _ in range(p)]
        for patron, (n, r) in celdas.items():
            x = (1,) + patron
            z = sum(b * xi for b, xi in zip(beta, x))
            z = max(-30.0, min(30.0, z))
            pr = 1.0 / (1.0 + math.exp(-z))
            w = n * pr * (1 - pr)
            res = r - n * pr
            for i in range(p):
                if not x[i]:
                    continue
                g[i] += res
                for j in range(p):
                    if x[j]:
                        H[i][j] += w
        for i in range(p):
            g[i] -= RIDGE * beta[i]
            H[i][i] += RIDGE
        paso = _resolver(H, g)
        beta = [b + d for b, d in zip(beta, paso)]
        if max(abs(d) for d in paso) < 1e-7:
            break
    return beta


def _isotonica(pares: list[tuple[float, int]]) -> list[float]:
    """Regresión isotónica creciente (pool-adjacent-violators) de (valor, peso)."""
    bloques: list[list[float]] = []  # [suma ponderada, peso, largo]
    for v, w in pares:
        bloques.append([v * w, w, 1])
        while len(bloques) > 1 and bloques[-2][0] / bloques[-2][1] > bloques[-1][0] / bloques[-1][1]:
            a = bloques.pop()
            bloques[-1] = [bloques[-1][0] + a[0], bloques[-1][1] + a[1], bloques[-1][2] + a[2]]
    out: list[float] = []
    for s, w, largo in bloques:
        out.extend([s / w if w else 0.0] * largo)
    return out


def calibrar(obs: list[dict]) -> dict:
    con_base = [o for o in obs if o["nivel"] != "sin base" and o["dRival"] is not None]
    if len(con_base) < 200:
        return {"n": len(con_base), "aviso": "muestra insuficiente para calibrar (mínimo 200 observaciones con rival)"}
    celdas: dict[tuple[int, ...], list[int]] = {}
    for o in con_base:
        s = _senales_de(o)
        c = celdas.setdefault(s, [0, 0])
        c[0] += 1
        c[1] += int(o["revento"])
    beta = _logistica(celdas)
    coefs = {s: round(beta[i + 1], 3) for i, s in enumerate(SENALES)}
    puntos = {s: max(0, math.floor(beta[i + 1] / PASO_PUNTO + 0.5)) for i, s in enumerate(SENALES)}

    # evaluar la tabla de puntos propuesta sobre las mismas observaciones
    for o in con_base:
        s = _senales_de(o)
        o["_logit"] = sum(b * xi for b, xi in zip(beta, (1,) + s))
        o["_puntosProp"] = sum(puntos[n] for n, xi in zip(SENALES, s) if xi)
    base = _tasa(con_base)["tasa"]
    por_puntos = []
    for pts in sorted({o["_puntosProp"] for o in con_base}):
        g = [o for o in con_base if o["_puntosProp"] == pts]
        por_puntos.append({"puntos": pts, **_tasa(g)})
    # los niveles se asignan sobre la tasa ISOTÓNICA (pool-adjacent-violators,
    # ponderada por n): con n chico la tasa cruda sube y baja, y cortar sobre
    # ella da niveles desordenados. La cruda se conserva para verla.
    for f, iso in zip(por_puntos, _isotonica([(f["tasa"], f["n"]) for f in por_puntos])):
        f["tasaIso"] = round(iso, 3)
        f["nivel"] = ("bajo" if iso < base - 0.10 else "medio" if iso < base
                      else "alto" if iso < base + 0.10 else "muy alto")
    cortes = {}
    for fila in por_puntos:
        cortes.setdefault(fila["nivel"], fila["puntos"])
    tasas = [f["tasa"] for f in por_puntos]
    nivel_de = {f["puntos"]: f["nivel"] for f in por_puntos}
    alto = [o for o in con_base if nivel_de[o["_puntosProp"]] in ("alto", "muy alto")]
    bajo = [o for o in con_base if nivel_de[o["_puntosProp"]] == "bajo"]
    return {
        "n": len(con_base),
        "celdas": len(celdas),
        "intercepto": round(beta[0], 3),
        "coeficientes": coefs,
        "aporta": {s: coefs[s] > 0.1 for s in SENALES},
        "puntosPropuestos": puntos,
        "pasoPunto": PASO_PUNTO,
        "aucLogit": _auc(con_base, "_logit"),
        "aucPuntosPropuestos": _auc(con_base, "_puntosProp"),
        "porPuntosPropuestos": por_puntos,
        "monotona": all(a <= b for a, b in zip(tasas, tasas[1:])),
        "cortesPropuestos": cortes,
        "separacionPropuesta": round(_tasa(alto)["tasa"] - _tasa(bajo)["tasa"], 3) if alto and bajo else None,
        "aviso": "ajuste en muestra: dice qué señal pesa y propone puntos enteros; no es una tasa prometida",
    }


def correr_backtest(*, padron_: bool = False, liga: int | None = None, horizonte: int = 1,
                    muestra: int = 0, min_filas: int = 12, semilla: int = 42,
                    calibrar_: bool = False) -> dict:
    """Lo que corren el CLI y el endpoint: elige los equipos y devuelve el resumen
    con la lista de ligas evaluadas (para que se vea QUÉ se calibró)."""
    ligas: set[int] | None = None
    nombres: dict[int, str] = {}
    if padron_:
        nombres = padron()
        ligas = set(nombres)
    if liga:
        ligas = {liga}
        nombres = _nombres_ligas(ligas)
    equipos = _equipos(min_filas, ligas)
    if muestra and muestra < len(equipos):
        random.seed(semilla)
        equipos = random.sample(equipos, muestra)
    obs, resumen = correr(equipos, horizonte, MIN_PREFIJO, ligas, nombres or None)
    resumen["equipos"] = len(equipos)
    resumen["ligasEvaluadas"] = sorted(nombres.values()) if ligas else ["todas"]
    if calibrar_:
        resumen["calibracion"] = calibrar(obs)
        # POR SIGNO, aparte: la logística conjunta puede esconder un efecto que
        # va al revés en cada lado. Que la K alta no adelante el reventón en la
        # burbuja + (equipo fuerte) no dice nada de la burbuja − (equipo hundido,
        # donde la regresión a la media empuja a que se corte). Si los pesos
        # difieren de verdad, la tabla de puntos tiene que ser una por signo.
        resumen["calibracionPorSigno"] = {s: calibrar([o for o in obs if o["signo"] == s]) for s in ("+", "-")}
    return resumen


# ── informe ──────────────────────────────────────────────────────────────────

def _pct(t: dict) -> str:
    return "—" if t["tasa"] is None else f"{100 * t['tasa']:5.1f}%"


def imprimir(r: dict):
    h = r["horizonte"]
    print(f"\n=== Backtest del reventón · horizonte {h} partido{'s' if h != 1 else ''} ===")
    print(f"observaciones: {r['observaciones']} (sin base: {r['sinBase']}) · "
          f"tasa base de reventón: {_pct(r['tasaBase'])} sobre {r['tasaBase']['n']}")
    print(f"burbujas +: {_pct(r['porSigno']['+'])} ({r['porSigno']['+']['n']}) · "
          f"burbujas −: {_pct(r['porSigno']['-'])} ({r['porSigno']['-']['n']})")

    print("\n— por nivel de riesgo (debe crecer) —")
    for nv in NIVELES:
        t = r["porNivel"][nv]
        print(f"  {nv:9s} {_pct(t)}  n={t['n']}")
    print(f"  monótona: {'sí' if r['monotona'] else 'NO'} · AUC de los puntos: {r['aucPuntos']}")

    print("\n— por puntos —")
    for p, t in r["porPuntos"].items():
        if t["n"]:
            print(f"  {p} pts  {_pct(t)}  n={t['n']}")

    print("\n— cada señal encendida vs apagada (lift = diferencia de tasa) —")
    for s, v in r["senales"].items():
        print(f"  {s:15s} on {_pct(v['encendida'])} (n={v['encendida']['n']}) · off {_pct(v['apagada'])} "
              f"(n={v['apagada']['n']}) · lift {v['lift']}")

    print("\n— por familia (separación = tasa alto/muy alto − tasa bajo) —")
    for f, v in r["porFamilia"].items():
        print(f"  {f:7s} tasa {_pct(v['todas'])} n={v['todas']['n']} · separación {v['separacion']}")

    print("\n— regla «qué constante manda» —")
    for k, v in r["reglaManda"].items():
        print(f"  {k:8s} tasa {_pct(v['todas'])} n={v['todas']['n']} · separación {v['separacion']} · AUC {v['auc']}")
    rn = r["reglaNivel"]
    print(f"  nivel medio  → separación total {rn['nivelMedio']['total']} · específicas {rn['nivelMedio']['especificas']}")
    print(f"  nivel extremo→ separación total {rn['nivelExtremo']['total']} · específicas {rn['nivelExtremo']['especificas']}")

    print("\n— por tamaño de la muestra de reventones previos —")
    for k, t in r["porMuestra"].items():
        print(f"  {k:4s} {_pct(t)}  n={t['n']}")

    if r.get("porLiga"):
        print("\n— por liga (tasa base · bajo · alto/muy alto · separación · AUC) —")
        for l in r["porLiga"]:
            print(f"  {l['liga'][:34]:34s} {_pct(l['todas'])} n={l['todas']['n']:4d} · bajo {_pct(l['bajo'])} · "
                  f"alto+ {_pct(l['altoMuyAlto'])} · sep {l['separacion']} · AUC {l['auc']}")
    fa = r.get("franjaAlta") or {}
    if fa.get("n"):
        print("\n— franja alta: umbral del aviso «cerca del extremo» (frecuencia = en qué parte de las burbujas salta) —")
        print(f"  récord (EXTREMO): {_pct(fa['record'])} n={fa['record']['n']} · frecuencia {100 * fa['record']['frecuencia']:.1f}%")
        print(f"  cerca con el umbral vigente: {_pct(fa['cercaVigente'])} n={fa['cercaVigente']['n']} · "
              f"frecuencia {100 * fa['cercaVigente']['frecuencia']:.1f}% · resto {_pct(fa['resto'])} n={fa['resto']['n']}")
        print(f"  {'umbral':>6s}  {'solo K':>22s}  {'solo racha':>22s}  {'K o racha':>22s}")
        for u in fa["umbrales"]:
            c = lambda t: f"{_pct(t)} · {100 * t['frecuencia']:4.1f}% n={t['n']}"  # noqa: E731
            print(f"  {u['umbral']:>6d}  {c(u['soloK']):>22s}  {c(u['soloRacha']):>22s}  {c(u['kORacha']):>22s}")
        print(f"  propuesto: {fa['propuesto']} (techo {100 * fa['techo']:.0f}%) · {fa['aviso']}")
    cal = r.get("calibracion")
    if cal:
        print("\n=== Calibración (regresión logística sobre las señales; ajuste en muestra) ===")
        if "coeficientes" not in cal:
            print(f"  {cal['aviso']} (n={cal['n']})")
        else:
            print(f"  n={cal['n']} · celdas={cal['celdas']} · intercepto {cal['intercepto']} · "
                  f"AUC logit {cal['aucLogit']} · AUC puntos propuestos {cal['aucPuntosPropuestos']}")
            print(f"  {'señal':16s} {'coef':>7s} {'pts':>4s}  aporta")
            for s in SENALES:
                print(f"  {s:16s} {cal['coeficientes'][s]:7.3f} {cal['puntosPropuestos'][s]:4d}  {'sí' if cal['aporta'][s] else 'no'}")
            print("\n  — tasa por puntos propuestos (cruda · isotónica) → nivel (bajo < base−10 · medio < base · alto < base+10 · muy alto) —")
            for f in cal["porPuntosPropuestos"]:
                print(f"  {f['puntos']:2d} pts  {_pct(f)} · iso {100 * f['tasaIso']:5.1f}%  n={f['n']:6d}  {f['nivel']}")
            print(f"  cortes propuestos: {cal['cortesPropuestos']} · monótona: {'sí' if cal['monotona'] else 'NO'} · "
                  f"separación propuesta {cal['separacionPropuesta']}")
            print(f"  {cal['aviso']}")
    por_signo = r.get("calibracionPorSigno")
    if por_signo:
        print("\n— calibración POR SIGNO (¿la K pesa distinto en la burbuja + y en la −?) —")
        print(f"  {'señal':16s} {'coef +':>8s} {'pts +':>6s} {'coef −':>8s} {'pts −':>6s}")
        for s in SENALES:
            cp, cn = por_signo["+"], por_signo["-"]
            fp = (f"{cp['coeficientes'][s]:8.3f} {cp['puntosPropuestos'][s]:6d}" if "coeficientes" in cp else f"{'—':>8s} {'—':>6s}")
            fn = (f"{cn['coeficientes'][s]:8.3f} {cn['puntosPropuestos'][s]:6d}" if "coeficientes" in cn else f"{'—':>8s} {'—':>6s}")
            print(f"  {s:16s} {fp} {fn}")
        for s, cs in por_signo.items():
            if "coeficientes" in cs:
                print(f"  signo {s}: n={cs['n']} · AUC logit {cs['aucLogit']} · AUC puntos {cs['aucPuntosPropuestos']} · "
                      f"cortes {cs['cortesPropuestos']}")
    if r.get("ligasEvaluadas"):
        print(f"\nligas evaluadas: {', '.join(r['ligasEvaluadas'])} · equipos: {r.get('equipos')}")

    print("\nLectura: si «alto/muy alto» no revienta más que «bajo», los puntos no están "
          "calibrados para esta base; si una señal tiene lift ≤ 0, no aporta y hay que "
          "bajarle el peso. Si en nivel medio las específicas separan más que la total "
          "(y al revés en los extremos), la regla de qué constante manda se confirma.")


def main():
    ap = argparse.ArgumentParser(description="Backtest hacia atrás del reventón de burbuja")
    ap.add_argument("--padron", action="store_true",
                    help="solo las ligas importantes (padrón de las cuotas en vivo: extractor.ligas_vivo())")
    ap.add_argument("--muestra", type=int, default=0, help="equipos al azar (0 = todos)")
    ap.add_argument("--liga", type=int, help="solo partidos de esta league_id")
    ap.add_argument("--horizonte", type=int, default=1, help="revienta dentro de N partidos de la condición (default 1)")
    ap.add_argument("--min-filas", type=int, default=12, help="filas mínimas por equipo")
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--calibrar", action="store_true",
                    help="ajusta una regresión logística sobre las señales y propone la tabla de puntos")
    ap.add_argument("--json", help="guardar el resumen en este archivo")
    a = ap.parse_args()

    resumen = correr_backtest(padron_=a.padron, liga=a.liga, horizonte=a.horizonte, muestra=a.muestra,
                              min_filas=a.min_filas, semilla=a.semilla, calibrar_=a.calibrar)
    print(f"equipos evaluados: {resumen['equipos']}")
    imprimir(resumen)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(resumen, f, ensure_ascii=False, indent=1)
        print(f"\nresumen guardado en {a.json}")


if __name__ == "__main__":
    main()
