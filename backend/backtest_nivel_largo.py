"""¿Un nivel LARGO predice mejor que el de 20 partidos + goles de 5? (25/11/2026)

El caso: el nivel del Manchester City cayó de 4,08 (11/10) a 2,87 (07/11)
—−0,86 de los goles de sus últimos 5 y −0,35 de los puntos de 20— y ante
Fulham y Napoli dejó de ser favorito por nivel mientras la casa le daba 69 y
75 %. El usuario: «mi lógica de separar el nivel era como por hype e
hinchada, lo intentaba resumir con el promedio de varios años… la matemática
le sacó la vuelta a mis principios, me da miedo». Esto lo mide en vez de
discutirlo.

Las versiones del nivel de cada equipo AL DÍA del partido (solo partidos
anteriores; MOTOR §2.1 para la actual):

  A actual        1 + puntos promedio de 20 + saldo de goles de 5 (§2.1)
  B solo20        1 + puntos promedio de 20 (sin los goles de 5)
  C media1a       promedio del nivel actual en los 365 días previos
  D media3a       promedio del nivel actual en los 1.095 días previos
  E puntos60      1 + puntos promedio de 60 (largo, sin goles)
  F actual+3a     A y D juntos: ¿el largo le agrega algo al actual?

Cada versión se convierte al 1X2 con SU logística multinomial (como §5.6:
d = nivel local − nivel visita y d², empate de referencia; F con las dos
diferencias), ajustada en el 80 % más viejo y medida en el 20 % más nuevo
(corte temporal). Se compara en pérdida logarítmica, Brier y acierto, con la
diferencia contra A e IC por bootstrap de partidos; también en los partidos
de los grandes (`backtest_favorito_falla.grandes`) y donde A y D discrepan
en 0,5 o más. Oficiales sin copas nacionales, últimos `--anos` años. No toca
el motor: si una versión gana, el cambio va por MOTOR §2 con su backtest.

    python -m backend.backtest_nivel_largo --padron [--anos 5] [--json salida.json]
    python -m backend.backtest_nivel_largo --desde-dir carpeta [--anos 5]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from bisect import bisect_left
from datetime import date, timedelta

from backend.backtest_favorito_falla import AMISTOSOS, _desde, grandes

VARIANTES = ("A actual", "B solo20", "C media1a", "D media3a", "E puntos60", "F actual+3a")
BOOTSTRAP = 500


def _pts(f: dict) -> int:
    gf, gc = int(f["golesFavor"]), int(f["golesContra"])
    return 3 if gf > gc else 1 if gf == gc else 0


def series(h: dict) -> dict:
    """Por partido del equipo (TODOS, como el nivel: amistosos incluidos), lo que se sabía
    ANTES: las versiones del nivel con los partidos anteriores. {fixtureId: {variante: valor}}."""
    filas = sorted((f for f in h["filas"] if f.get("golesFavor") is not None and f.get("golesContra") is not None),
                   key=lambda f: str(f["fecha"]))
    niv = sorted(((str(n["fecha"]), float(n["nivel"])) for n in h.get("niveles") or []), key=lambda x: x[0])
    nf = [x[0] for x in niv]
    acum = [0.0]
    for _, v in niv:
        acum.append(acum[-1] + v)
    out = {}
    for i, f in enumerate(filas):
        prev = filas[:i]
        if len(prev) < 60:
            continue
        w20, u5, w60 = prev[-20:], prev[-5:], prev[-60:]
        p20 = sum(_pts(x) for x in w20) / 20
        gf = sum(int(x["golesFavor"]) for x in u5)
        gc = sum(int(x["golesContra"]) for x in u5)
        g5 = (gf - gc) / (gf + gc) if gf + gc else 0.0
        fecha = str(f["fecha"])
        fin = bisect_left(nf, fecha)
        med = {}
        for clave, dias in (("C media1a", 365), ("D media3a", 1095)):
            lim = (date.fromisoformat(fecha[:10]) - timedelta(days=dias)).isoformat()
            ini = bisect_left(nf, lim)
            med[clave] = (acum[fin] - acum[ini]) / (fin - ini) if fin - ini >= 10 else None
        out[f["fixtureId"]] = {"fecha": fecha[:10], "liga": f.get("ligaId"), "local": f.get("condicion") == "Local",
                               "gf": int(f["golesFavor"]), "gc": int(f["golesContra"]),
                               "A actual": 1 + p20 + g5, "B solo20": 1 + p20, **med,
                               "E puntos60": 1 + sum(_pts(x) for x in w60) / 60}
    return out


def partidos(historias: dict, desde: str, excluir: set | None = None) -> list[dict]:
    """Un renglón por partido oficial (desde el local) con las versiones de los dos lados."""
    s = {t: series(h) for t, h in historias.items()}
    por_fx: dict[int, dict] = {}
    for t, ser in s.items():
        for fx, r in ser.items():
            if r["fecha"] < desde or r["liga"] in AMISTOSOS or (excluir and fx in excluir):
                continue
            por_fx.setdefault(fx, {})["L" if r["local"] else "V"] = (t, r)
    out = []
    for fx, par in por_fx.items():
        if "L" not in par or "V" not in par:
            continue
        (tl, a), (tv, b) = par["L"], par["V"]
        if any(a.get(k) is None or b.get(k) is None for k in ("C media1a", "D media3a")):
            continue
        res = 0 if a["gf"] > a["gc"] else 1 if a["gf"] == a["gc"] else 2
        out.append({"fixtureId": fx, "fecha": a["fecha"], "local": tl, "visita": tv, "res": res,
                    **{k: a[k] - b[k] for k in VARIANTES if k in a}})
    out.sort(key=lambda r: (r["fecha"], r["fixtureId"]))
    return out


# ── la logística multinomial (Newton; local y visita contra el empate) ─────────

def _x(r: dict, var: str) -> list[float]:
    if var == "F actual+3a":
        a, d = r["A actual"], r["D media3a"]
        return [1.0, a, a * a, d, d * d]
    d = r[var]
    return [1.0, d, d * d]


def _probs(beta: list[list[float]], x: list[float]) -> list[float]:
    zl = sum(b * v for b, v in zip(beta[0], x))
    zv = sum(b * v for b, v in zip(beta[1], x))
    m = max(0.0, zl, zv)
    el, ee, ev = math.exp(zl - m), math.exp(-m), math.exp(zv - m)
    s = el + ee + ev
    return [el / s, ee / s, ev / s]


def ajustar(filas: list[dict], var: str, iters: int = 25) -> list[list[float]]:
    import numpy as np
    X = np.array([_x(r, var) for r in filas])
    y = np.array([r["res"] for r in filas])
    k = X.shape[1]
    beta = np.zeros(2 * k)
    Y = np.stack([(y == 0), (y == 2)], axis=1).astype(float)
    for _ in range(iters):
        B = beta.reshape(2, k)
        Z = X @ B.T
        m = np.maximum(0, Z.max(axis=1, keepdims=True))
        E = np.exp(Z - m)
        den = np.exp(-m) + E.sum(axis=1, keepdims=True)
        P = E / den
        g = ((Y - P).T @ X).reshape(-1) - 1e-6 * beta
        H = np.zeros((2 * k, 2 * k))
        for i in range(2):
            for j in range(2):
                w = P[:, i] * ((1.0 if i == j else 0.0) - P[:, j])
                H[i * k:(i + 1) * k, j * k:(j + 1) * k] = -(X * w[:, None]).T @ X
        H -= 1e-6 * np.eye(2 * k)
        paso = np.linalg.solve(H, g)
        beta = beta - paso
        if np.abs(paso).max() < 1e-9:
            break
    return beta.reshape(2, k).tolist()


def _metricas(filas: list[dict], var: str, beta) -> list[tuple[float, float, int]]:
    out = []
    for r in filas:
        p = _probs(beta, _x(r, var))
        ll = -math.log(max(1e-12, p[r["res"]]))
        br = sum((p[i] - (1.0 if i == r["res"] else 0.0)) ** 2 for i in range(3))
        out.append((ll, br, 1 if max(range(3), key=lambda i: p[i]) == r["res"] else 0))
    return out


def evaluar(filas: list[dict], frac: float = 0.8, grupo=None) -> dict:
    """`grupo` = set de equipos, o una función fecha → set que se llama con el inicio
    de la prueba (el grupo de los grandes no puede verse con la prueba)."""
    if len(filas) < 200:
        return {"partidos": len(filas), "sinDato": "menos de 200 partidos"}
    corte = int(len(filas) * frac)
    ent, prueba = filas[:corte], filas[corte:]
    if callable(grupo):
        grupo = grupo(prueba[0]["fecha"])
    m = {v: _metricas(prueba, v, ajustar(ent, v)) for v in VARIANTES}
    subconj = {"todos": lambda r: True,
               "grandes (uno de los dos)": lambda r: bool(grupo) and (r["local"] in grupo or r["visita"] in grupo),
               "A y D discrepan 0,5+": lambda r: abs(r["A actual"] - r["D media3a"]) >= 0.5}
    out = {"partidos": len(filas), "entrenamiento": len(ent), "prueba": len(prueba),
           "desdePrueba": prueba[0]["fecha"], "hasta": prueba[-1]["fecha"], "subconjuntos": {}}
    rnd = random.Random(7)
    for nombre, f in subconj.items():
        idx = [i for i, r in enumerate(prueba) if f(r)]
        if len(idx) < 100:
            out["subconjuntos"][nombre] = {"n": len(idx), "sinDato": "menos de 100 partidos"}
            continue
        boots = [[rnd.choice(idx) for _ in idx] for _ in range(BOOTSTRAP)]
        filas_v = {}
        for v in VARIANTES:
            ll = sum(m[v][i][0] for i in idx) / len(idx)
            br = sum(m[v][i][1] for i in idx) / len(idx)
            ac = sum(m[v][i][2] for i in idx) / len(idx)
            dif = sorted(sum(m[v][i][0] - m["A actual"][i][0] for i in b) / len(b) for b in boots)
            filas_v[v] = {"logLoss": round(ll, 5), "brier": round(br, 5), "acierto": round(ac, 4),
                          "difLogLossContraA": round(ll - sum(m["A actual"][i][0] for i in idx) / len(idx), 5),
                          "ic95": [round(dif[int(0.025 * BOOTSTRAP)], 5), round(dif[int(0.975 * BOOTSTRAP) - 1], 5)]}
        out["subconjuntos"][nombre] = {"n": len(idx), "variantes": filas_v}
    return out


# ── de dónde salen los datos ─────────────────────────────────────────────────

def correr_dir(carpeta: str, anos: int) -> dict:
    from backend.analisis.escala import es_copa_nacional
    from backend.backtest_dc_record import historias_desde_dir
    historias = historias_desde_dir(carpeta)
    nombres = {}
    if os.path.exists(os.path.join(carpeta, "ligas.json")):
        nombres = {int(k): v for k, v in json.load(open(os.path.join(carpeta, "ligas.json"))).items()}
    copas = {lg for lg, nom in nombres.items() if es_copa_nacional(lg, nom or "", set())}
    excluir = {f["fixtureId"] for h in historias.values() for f in h["filas"] if f.get("ligaId") in copas}
    d = _desde(anos)
    r = evaluar(partidos(historias, d, excluir), grupo=lambda f: grandes(historias, 3.0, d, hasta=f))
    r.update({"equipos": len(historias), "anos": anos, "copasNacionalesFuera": len(excluir)})
    return r


def correr_padron(anos: int) -> dict:
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.backtest_dc_record import historias_padron
    from backend.backtest_rival_resiste import _copas
    historias = historias_padron()
    fxs = sorted({f["fixtureId"] for h in historias.values() for f in h["filas"]})
    excluir = _copas(fxs)
    d = _desde(anos)
    r = evaluar(partidos(historias, d, excluir), grupo=lambda f: grandes(historias, 3.0, d, hasta=f))
    r.update({"equipos": len(historias), "anos": anos, "copasNacionalesFuera": len(excluir)})
    return r


def _imprimir(r: dict) -> None:
    if "subconjuntos" not in r:
        print(r)
        return
    print(f"\n{r['partidos']:,} partidos oficiales · {r.get('equipos', 0):,} equipos · prueba {r['prueba']:,} "
          f"desde {r['desdePrueba']} (entrenamiento {r['entrenamiento']:,}) · copas nacionales fuera\n")
    for nombre, s in r["subconjuntos"].items():
        print(f"{nombre} · n {s['n']:,}")
        if "variantes" not in s:
            print(f"  {s['sinDato']}")
            continue
        for v, m in s["variantes"].items():
            mejor = "  MEJOR que A" if m["ic95"][1] < 0 else "  PEOR que A" if m["ic95"][0] > 0 else ""
            print(f"  {v:<13} log-loss {m['logLoss']:.4f}  Brier {m['brier']:.4f}  acierto {m['acierto']:.1%}  "
                  f"contra A {m['difLogLossContraA']:+.4f} IC [{m['ic95'][0]:+.4f}, {m['ic95'][1]:+.4f}]{mejor}")
        print()
    print("(log-loss más bajo es mejor; «contra A» < 0 = esa versión predice mejor que el nivel actual)")


def main() -> None:
    ap = argparse.ArgumentParser(description="¿Un nivel largo predice mejor que el de 20 + goles de 5?")
    ap.add_argument("--padron", action="store_true")
    ap.add_argument("--desde-dir")
    ap.add_argument("--anos", type=int, default=5)
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.desde_dir:
        r = correr_dir(a.desde_dir, a.anos)
    elif a.padron:
        r = correr_padron(a.anos)
    else:
        ap.error("falta --padron (en el servidor) o --desde-dir")
    _imprimir(r)
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
