"""¿La burbuja mejora el 1X2 del motor? (docs/REVENTON.md §13)

El riesgo de reventón está calibrado para decir si una RACHA se corta, no
quién gana: una racha de victorias se corta también con un empate. Antes de
meter la burbuja en la fórmula del 1X2 hay que ver si agrega algo a lo que el
motor ya sabe. Este backtest lo mide con la historia, sin cuotas:

  M0 · motor     — el 1X2 solo con la diferencia de μ_partido (nivel, rival y
                   localía: lo mismo que ve el analista en la ficha).
  M1 · + racha   — más la racha abierta de cada lado (signo y largo). Separa
                   «la burbuja existe» de «la burbuja está por reventar».
  M2 · + riesgo  — más los puntos del riesgo de reventón de cada lado, con el
                   signo de la racha (riesgo alto en una racha + empuja contra
                   que ese equipo gane).
  M3 · + extremo — más el récord y el «cerca del extremo», que hoy NO puntúan
                   pero sí frenan la carga en el prompt.

Cada modelo es una logística multinomial (local · empate · visita) ajustada
con los partidos más VIEJOS y evaluada en los más NUEVOS (corte temporal, 80/20):
sin eso, cualquier variable extra «mejora» en muestra. Se compara log-loss y
Brier en la prueba, con un intervalo bootstrap de la diferencia contra M0
emparejada por partido. Si el intervalo de M2 − M1 no cruza cero, el riesgo
aporta al resultado más allá de la racha; si cruza, la burbuja se queda como
freno de la carga y no entra a la fórmula.

Sin fuga: la burbuja y el riesgo salen SOLO de las filas anteriores al partido
(igual que backtest_burbuja), y el nivel de cada equipo es el último guardado
con fecha anterior. Solo entran partidos en los que los DOS equipos tienen
historia suficiente (un lado sin datos no es un lado sin burbuja).

    python -m backend.backtest_burbuja_1x2 --padron          # las ligas importantes
    python -m backend.backtest_burbuja_1x2 --liga 281        # una liga
    python -m backend.backtest_burbuja_1x2 --muestra 300     # equipos al azar (prueba rápida)
    SAD_DATA_DIR=demo_data python -m backend.backtest_burbuja_1x2

Guarda el resumen en $SAD_DATA_DIR/.backtest_1x2.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from datetime import datetime, timezone

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend import db  # noqa: E402
from backend.analisis import burbuja  # noqa: E402
from backend.app import constantes_de, mu, niveles_de  # noqa: E402
from backend.backtest_burbuja import (MIN_PREFIJO, _equipos, _nivel_a_fecha, _nombres_ligas,  # noqa: E402
                                      _resolver, nivel_rival_previo, padron)

GUARDADO = ".backtest_1x2.json"
CLASES = ("L", "E", "V")          # local · empate · visita (E es la referencia)
RIDGE = 1e-2
NEWTON_ITER = 15
BOOTSTRAP = 500
PRUEBA = 0.2                      # el 20 % más reciente es la prueba

MODELOS = {
    "M0 motor": ["d", "d2"],
    "M1 + racha": ["d", "d2", "rachaL", "rachaV"],
    "M2 + riesgo": ["d", "d2", "rachaL", "rachaV", "riesgoL", "riesgoV"],
    "M3 + extremo": ["d", "d2", "rachaL", "rachaV", "riesgoL", "riesgoV", "extremoL", "extremoV"],
    # LAS CONSTANTES MISMAS (14/10/2026, pedido del usuario): M1-M3 solo miraban
    # el signo y el largo de la burbuja total. Acá entra el VALOR de cada K antes
    # del partido, cruzando la condición: la K local del que juega de local con
    # la K visita del que juega de visita (lo mismo con los goles).
    "M4 + K resultado": ["d", "d2", "kL", "kV", "kCondL", "kCondV"],
    "M5 + K goles": ["d", "d2", "gaL", "grL", "gaV", "grV", "gaCondL", "grCondL", "gaCondV", "grCondV"],
    "M6 + todas las K": ["d", "d2", "kL", "kV", "kCondL", "kCondV",
                         "gaL", "grL", "gaV", "grV", "gaCondL", "grCondL", "gaCondV", "grCondV"],
}


# ── observaciones ────────────────────────────────────────────────────────────

_CLAVES_K = ("k", "kCond", "ga", "gr", "gaCond", "grCond")


def _slog(x) -> float:
    """sign(x)·log(1+|x|): la K crece sin techo (rachas de 30 partidos); sin
    comprimirla, un puñado de valores extremos manda en la logística."""
    x = float(x or 0.0)
    return math.copysign(math.log1p(abs(x)), x)


def _ks(prev: dict, local_hoy: bool) -> dict:
    f = prev["fusion"]
    cond = "Local" if local_hoy else "Visita"
    return {"k": _slog(f["k"]), "kCond": _slog(f["k" + cond]),
            "ga": _slog(f["golesAnotado"]), "gr": _slog(f["golesRecibido"]),
            "gaCond": _slog(f[f"goles{cond}Anotado"]), "grCond": _slog(f[f"goles{cond}Recibido"])}

def lado_equipo(team_id: int, ligas: set[int] | None) -> dict[int, dict]:
    """Por fixture: lo que se sabía de ESTE equipo antes del partido."""
    filas = list(reversed(constantes_de(team_id, 500)))
    niveles = list(reversed(niveles_de(team_id, 500)))
    estab = burbuja.estabilidad_de(None, "1970-01-01")
    out = {}
    for i in range(MIN_PREFIJO, len(filas)):
        fila = filas[i]
        if ligas and fila["ligaId"] not in ligas:
            continue
        nv = _nivel_a_fecha(niveles, fila["fecha"])
        if nv is None:
            continue
        proximo = {
            "fixtureId": fila["fixtureId"], "fecha": fila["fecha"], "rivalId": fila["rivalId"],
            "rival": fila["rivalNombre"], "condicion": "L" if fila["condicion"] == "Local" else "V",
            # el nivel del rival ANTES del partido (el de la fila ya trae el resultado)
            "nivelRival": nivel_rival_previo(fila["rivalId"], fila["fecha"]),
        }
        fam = burbuja._analizar_familia(filas[:i], "total", proximo, estab, nivel_equipo=nv)
        act, rg, ext = fam["actual"], fam["riesgo"], fam["extremo"] or {}
        s = 0 if not act else (1 if act["signo"] == "+" else -1)
        con_base = bool(rg) and rg["nivel"] != "sin base"
        out[fila["fixtureId"]] = {
            "local": fila["condicion"] == "Local", "nivel": nv, "fecha": fila["fecha"], "liga": fila["ligaId"],
            "gf": fila["golesFavor"], "ga": fila["golesContra"],
            # con signo: + = racha que empuja a que ESTE equipo gane
            "racha": s * math.log1p(act["partidos"]) if act else 0.0,
            "riesgo": s * rg["puntos"] if (act and con_base) else 0.0,
            "riesgoNivel": rg["nivel"] if (act and con_base) else None,
            "extremo": s * (2 if ext.get("activo") else 1 if ext.get("cerca") else 0) if act else 0,
            # las K tal como estaban ANTES del partido: la fila anterior (la de
            # este partido ya trae su resultado). La de la condición es la del
            # lado en que juega HOY: local para el local, visita para el visitante.
            **_ks(filas[i - 1], fila["condicion"] == "Local"),
        }
    return out


def observaciones(equipos: list[int], ligas: set[int] | None) -> list[dict]:
    por_fx: dict[int, list[dict]] = {}
    for t in equipos:
        for fx, o in lado_equipo(t, ligas).items():
            por_fx.setdefault(fx, []).append(o)
    obs = []
    for fx, lados in por_fx.items():
        loc = [o for o in lados if o["local"]]
        vis = [o for o in lados if not o["local"]]
        if len(loc) != 1 or len(vis) != 1:
            continue  # un lado sin historia suficiente: fuera, no «sin burbuja»
        L, V = loc[0], vis[0]
        mu_l, mu_v = mu(L["nivel"], V["nivel"], 1.0), mu(V["nivel"], L["nivel"], 0.0)
        d = mu_l - mu_v
        y = "L" if L["gf"] > L["ga"] else "V" if L["gf"] < L["ga"] else "E"
        obs.append({
            "fixtureId": fx, "fecha": L["fecha"], "liga": L["liga"], "y": y,
            # la racha del visitante con signo invertido: todo «a favor del local»
            "x": {"d": d, "d2": d * d,
                  "rachaL": L["racha"], "rachaV": -V["racha"],
                  "riesgoL": L["riesgo"], "riesgoV": -V["riesgo"],
                  "extremoL": L["extremo"], "extremoV": -V["extremo"],
                  # las K van con su signo propio, una variable por equipo: la
                  # logística aprende el sentido de cada una (sin invertir nada)
                  **{f"{k}L": L[k] for k in _CLAVES_K}, **{f"{k}V": V[k] for k in _CLAVES_K}},
            "riesgoAlto": any(n in ("alto", "muy alto") for n in (L["riesgoNivel"], V["riesgoNivel"])),
            "conExtremo": bool(L["extremo"] or V["extremo"]),
        })
    obs.sort(key=lambda o: o["fecha"])
    return obs


# ── logística multinomial (Newton, sin numpy) ────────────────────────────────

def _probs(beta: list[float], x: list[float], p: int) -> tuple[float, float, float]:
    zl = max(-30.0, min(30.0, sum(b * xi for b, xi in zip(beta[:p], x))))
    zv = max(-30.0, min(30.0, sum(b * xi for b, xi in zip(beta[p:], x))))
    el, ev = math.exp(zl), math.exp(zv)
    s = 1.0 + el + ev
    return el / s, 1.0 / s, ev / s


def ajustar(X: list[list[float]], Y: list[str]) -> list[float]:
    """β = [local (p) | visita (p)], empate de referencia."""
    p = len(X[0])
    q = 2 * p
    beta = [0.0] * q
    for _ in range(NEWTON_ITER):
        g = [0.0] * q
        H = [[0.0] * q for _ in range(q)]
        for x, y in zip(X, Y):
            pl, _pe, pv = _probs(beta, x, p)
            rl, rv = (y == "L") - pl, (y == "V") - pv
            wll, wvv, wlv = pl * (1 - pl), pv * (1 - pv), -pl * pv
            for i in range(p):
                xi = x[i]
                if not xi:
                    continue
                g[i] += rl * xi
                g[p + i] += rv * xi
                for j in range(p):
                    xx = xi * x[j]
                    if not xx:
                        continue
                    H[i][j] += wll * xx
                    H[p + i][p + j] += wvv * xx
                    H[i][p + j] += wlv * xx
                    H[p + i][j] += wlv * xx
        for i in range(q):
            g[i] -= RIDGE * beta[i]
            H[i][i] += RIDGE
        paso = _resolver(H, g)
        beta = [b + d for b, d in zip(beta, paso)]
        if max(abs(d) for d in paso) < 1e-7:
            break
    return beta


def _matriz(obs: list[dict], vars_: list[str], escala: dict[str, tuple[float, float]]) -> list[list[float]]:
    return [[1.0] + [(o["x"][v] - escala[v][0]) / escala[v][1] for v in vars_] for o in obs]


def _escala(obs: list[dict], vars_: list[str]) -> dict[str, tuple[float, float]]:
    out = {}
    for v in vars_:
        xs = [o["x"][v] for o in obs]
        m = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs)) or 1.0
        out[v] = (m, sd)
    return out


def _perdidas(beta, X, Y) -> tuple[list[float], list[float], list[int]]:
    p = len(X[0])
    ll, br, ac = [], [], []
    for x, y in zip(X, Y):
        pr = dict(zip(CLASES, _probs(beta, x, p)))
        ll.append(-math.log(max(pr[y], 1e-12)))
        br.append(sum((pr[c] - (c == y)) ** 2 for c in CLASES))
        ac.append(int(max(pr, key=pr.get) == y))
    return ll, br, ac


def _ic_dif(a: list[float], b: list[float], semilla: int = 7) -> dict:
    """Diferencia media b − a (negativa = b mejor) con bootstrap emparejado."""
    n = len(a)
    if not n:
        return {"media": None, "ic95": None}
    dif = [y - x for x, y in zip(a, b)]
    rnd = random.Random(semilla)
    medias = sorted(sum(dif[rnd.randrange(n)] for _ in range(n)) / n for _ in range(BOOTSTRAP))
    return {"media": round(sum(dif) / n, 5),
            "ic95": [round(medias[int(0.025 * BOOTSTRAP)], 5), round(medias[int(0.975 * BOOTSTRAP) - 1], 5)]}


# ── el backtest ──────────────────────────────────────────────────────────────

def correr(obs: list[dict]) -> dict:
    corte = int(len(obs) * (1 - PRUEBA))
    train, test = obs[:corte], obs[corte:]
    if len(train) < 50 or len(test) < 20:
        return {"error": f"muy pocos partidos ({len(obs)}) para separar entrenamiento y prueba"}
    Ytr, Yte = [o["y"] for o in train], [o["y"] for o in test]
    res, perd = {}, {}
    for nombre, vars_ in MODELOS.items():
        esc = _escala(train, vars_)
        beta = ajustar(_matriz(train, vars_, esc), Ytr)
        ll, br, ac = _perdidas(beta, _matriz(test, vars_, esc), Yte)
        perd[nombre] = (ll, br)
        p = len(vars_) + 1
        res[nombre] = {
            "logLoss": round(sum(ll) / len(ll), 5), "brier": round(sum(br) / len(br), 5),
            "acierto": round(sum(ac) / len(ac), 4),
            # coeficientes estandarizados: cuánto mueve 1 desvío de cada variable
            "coefLocal": {v: round(b, 4) for v, b in zip(vars_, beta[1:p])},
            "coefVisita": {v: round(b, 4) for v, b in zip(vars_, beta[p + 1:])},
        }
    nombres = list(MODELOS)
    comparaciones = {}
    for a, b in ((nombres[0], nombres[1]), (nombres[0], nombres[2]), (nombres[1], nombres[2]), (nombres[2], nombres[3]),
                 (nombres[0], nombres[4]), (nombres[0], nombres[5]), (nombres[0], nombres[6]), (nombres[3], nombres[6])):
        comparaciones[f"{b} vs {a}"] = {"logLoss": _ic_dif(perd[a][0], perd[b][0]),
                                        "brier": _ic_dif(perd[a][1], perd[b][1])}
    # dónde debería notarse: partidos con algún lado en riesgo alto / con extremo
    subgrupos = {}
    for clave, filtro in (("riesgoAlto", lambda o: o["riesgoAlto"]), ("conExtremo", lambda o: o["conExtremo"])):
        idx = [i for i, o in enumerate(test) if filtro(o)]
        subgrupos[clave] = {"n": len(idx)}
        for a, b in ((nombres[1], nombres[2]), (nombres[0], nombres[3]), (nombres[0], nombres[6])):
            subgrupos[clave][f"{b} vs {a}"] = _ic_dif([perd[a][0][i] for i in idx], [perd[b][0][i] for i in idx])
    base = {c: round(sum(1 for y in Yte if y == c) / len(Yte), 4) for c in CLASES}
    return {"partidos": len(obs), "entrenamiento": len(train), "prueba": len(test),
            "desde": train[0]["fecha"][:10], "corte": test[0]["fecha"][:10], "hasta": test[-1]["fecha"][:10],
            "frecuenciasPrueba": base, "modelos": res, "comparaciones": comparaciones, "subgrupos": subgrupos,
            "lectura": lectura(comparaciones)}


def lectura(comp: dict) -> str:
    """Lo que el backtest permite concluir, calculado (no opinado)."""
    def veredicto(clave):
        ic = comp[clave]["logLoss"]["ic95"]
        if not ic:
            return "sin datos"
        return "mejora" if ic[1] < 0 else "empeora" if ic[0] > 0 else "no se distingue"
    r1 = veredicto("M1 + racha vs M0 motor")
    r2 = veredicto("M2 + riesgo vs M1 + racha")
    r3 = veredicto("M3 + extremo vs M2 + riesgo")
    txt = [f"la racha sobre el motor: {r1}", f"el riesgo sobre la racha: {r2}", f"el extremo sobre el riesgo: {r3}"]
    if r2 == "mejora":
        txt.append("→ el riesgo de reventón AGREGA al 1X2: tiene sentido llevarlo a la fórmula con estos coeficientes")
    else:
        txt.append("→ el riesgo no agrega al 1X2 más allá de lo que ya hay: se queda como freno de la carga, "
                   "no entra a la fórmula")
    if "M6 + todas las K vs M0 motor" in comp:
        r4 = veredicto("M4 + K resultado vs M0 motor")
        r5 = veredicto("M5 + K goles vs M0 motor")
        r6 = veredicto("M6 + todas las K vs M0 motor")
        txt += [f"las K de resultado (total y por condición) sobre el motor: {r4}",
                f"las K de goles sobre el motor: {r5}", f"todas las K juntas: {r6}"]
        txt.append("→ las constantes AGREGAN al 1X2: candidatas a la fórmula (con estos coeficientes)" if r6 == "mejora"
                   else "→ las constantes no agregan al 1X2 más allá del nivel que ya usa el motor")
    return " · ".join(txt)


def correr_backtest(*, padron_: bool = False, liga: int | None = None, muestra: int = 0,
                    min_filas: int = 12, semilla: int = 42) -> dict:
    ligas, nombres = None, {}
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
    obs = observaciones(equipos, ligas)
    r = correr(obs)
    r["equipos"] = len(equipos)
    r["ligasEvaluadas"] = sorted(nombres.values()) if ligas else ["todas"]
    return r


def guardar(r: dict) -> str:
    ruta = os.path.join(db.BASE_DIR, GUARDADO)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({**r, "corridoEn": datetime.now(timezone.utc).isoformat(timespec="seconds")}, f, ensure_ascii=False)
    return ruta


def imprimir(r: dict):
    if r.get("error"):
        print(r["error"])
        return
    print(f"partidos: {r['partidos']} ({r['equipos']} equipos) · entrenamiento {r['desde']} → {r['corte']} "
          f"({r['entrenamiento']}) · prueba {r['corte']} → {r['hasta']} ({r['prueba']})")
    print(f"frecuencias en la prueba: {r['frecuenciasPrueba']}\n")
    print(f"{'modelo':<16}{'log-loss':>10}{'Brier':>9}{'acierto':>9}")
    for n, m in r["modelos"].items():
        print(f"{n:<16}{m['logLoss']:>10.4f}{m['brier']:>9.4f}{m['acierto']:>9.1%}")
    print("\ndiferencia de log-loss (negativa = mejora), IC 95 % bootstrap emparejado:")
    for k, v in r["comparaciones"].items():
        print(f"  {k:<28} {v['logLoss']['media']:+.5f}  {v['logLoss']['ic95']}")
    for k, v in r["subgrupos"].items():
        print(f"\nsubgrupo {k} (n={v['n']}):")
        for kk, vv in v.items():
            if kk != "n" and vv["media"] is not None:
                print(f"  {kk:<28} {vv['media']:+.5f}  {vv['ic95']}")
    m2 = r["modelos"]["M2 + riesgo"]
    print(f"\ncoeficientes de M2 (por desvío; local / visita contra empate):")
    for v in m2["coefLocal"]:
        print(f"  {v:<10} {m2['coefLocal'][v]:+.3f} / {m2['coefVisita'][v]:+.3f}")
    m6 = r["modelos"].get("M6 + todas las K")
    if m6:
        print(f"\ncoeficientes de M6 (por desvío; local / visita contra empate; L = el local, V = el visitante):")
        for v in m6["coefLocal"]:
            print(f"  {v:<10} {m6['coefLocal'][v]:+.3f} / {m6['coefVisita'][v]:+.3f}")
    print(f"\n{r['lectura']}")


def main():
    ap = argparse.ArgumentParser(description="¿La burbuja mejora el 1X2 del motor?")
    ap.add_argument("--padron", action="store_true", help="solo las ligas importantes")
    ap.add_argument("--liga", type=int, help="solo partidos de esta league_id")
    ap.add_argument("--muestra", type=int, default=0, help="equipos al azar (0 = todos)")
    ap.add_argument("--min-filas", type=int, default=12)
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--json", help="guardar también en este archivo")
    a = ap.parse_args()
    r = correr_backtest(padron_=a.padron, liga=a.liga, muestra=a.muestra, min_filas=a.min_filas, semilla=a.semilla)
    imprimir(r)
    if not r.get("error"):
        print(f"\nguardado en {guardar(r)}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
