"""El 1X2 del motor desde μ, calibrado contra resultados (docs/MOTOR_SAD_EXTRACCION.md §5.6).

`μ_partido` son PUNTOS esperados (0 a 3), no goles. En 78 de 209 partes
(octubre de 2026) el analista armó el 1X2 con un Poisson que usaba μ como si
fuera λ de goles: un error de unidad que nadie pidió, improvisado porque el
skill `sad-analysis` describe un «modelo de goles Poisson» que en esta app no
existe. Lo que está en la base se calcula: este backtest ajusta la conversión
μ → (local · empate · visita) con la historia y la deja en
`backend/analisis/unxdos_motor.py`.

El modelo es el M0 del backtest del 1X2 (`backtest_burbuja_1x2`): una logística
multinomial sobre d = μ_local − μ_visita y d², con el empate de referencia. Se
ajusta con los partidos más VIEJOS y se evalúa en los más NUEVOS (80/20) contra
dos referencias: la frecuencia de la muestra (quien no mira el partido) y el
Poisson sobre μ (lo que se venía improvisando). Después se reajusta con todo y
se imprimen los coeficientes SIN estandarizar, listos para copiar.

Sin fuga: el nivel de cada equipo es el último guardado con fecha ANTERIOR al
partido (el de la fila ya trae el resultado), igual que `backtest_burbuja`.
Entran solo los partidos con los dos equipos con nivel previo.

    python -m backend.backtest_unxdos_motor --padron            # en el servidor, con las .db
    python -m backend.backtest_unxdos_motor --desde-dir carpeta # c/<id>.json y n/<id>.json bajados de la API
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
from bisect import bisect_left

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend.app import mu  # noqa: E402
from backend.backtest_burbuja_1x2 import _ic_dif, _probs, ajustar  # noqa: E402

PRUEBA = 0.2
MIN_PARTIDOS = 5          # filas previas del equipo para que su nivel valga algo
CLASES = ("L", "E", "V")


def _nivel_antes(fechas: list[str], niveles: list[float], fecha: str) -> float | None:
    i = bisect_left(fechas, fecha)
    return niveles[i - 1] if i > 0 else None


def observaciones(historias: dict[int, dict]) -> list[dict]:
    """`historias[team] = {"filas": [constantes asc], "niveles": [niveles asc]}`.
    Un partido por fixture, visto desde el local; los dos con nivel previo."""
    niv = {t: ([n["fecha"] for n in h["niveles"]], [float(n["nivel"]) for n in h["niveles"]])
           for t, h in historias.items()}
    obs, vistos = [], set()
    for t, h in historias.items():
        for i, f in enumerate(h["filas"]):
            if f["condicion"] != "Local" or f["fixtureId"] in vistos or i < MIN_PARTIDOS:
                continue
            r = f["rivalId"]
            if r not in niv or t not in niv:
                continue
            nl = _nivel_antes(*niv[t], f["fecha"])
            nv = _nivel_antes(*niv[r], f["fecha"])
            if nl is None or nv is None:
                continue
            gf, gc = f["golesFavor"], f["golesContra"]
            if gf is None or gc is None:
                continue
            vistos.add(f["fixtureId"])
            mu_l, mu_v = mu(nl, nv, 1.0), mu(nv, nl, 0.0)
            obs.append({"fixtureId": f["fixtureId"], "fecha": f["fecha"], "liga": f.get("ligaId"),
                        "muL": mu_l, "muV": mu_v, "d": mu_l - mu_v,
                        "y": "L" if gf > gc else "V" if gf < gc else "E"})
    obs.sort(key=lambda o: o["fecha"])
    return obs


def _x(o: dict) -> list[float]:
    return [1.0, o["d"], o["d"] * o["d"]]


def poisson_sobre_mu(mu_l: float, mu_v: float, tope: int = 10) -> tuple[float, float, float]:
    """Lo que se improvisaba: μ (puntos) como λ de goles. Solo para comparar."""
    def pmf(lam):
        lam = max(lam, 1e-6)
        return [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(tope + 1)]
    a, b = pmf(mu_l), pmf(mu_v)
    pl = sum(a[i] * b[j] for i in range(tope + 1) for j in range(tope + 1) if i > j)
    pe = sum(a[i] * b[i] for i in range(tope + 1))
    s = pl + pe + (1 - pl - pe)
    return pl / s, pe / s, (1 - pl - pe) / s


def _perdida(pr: dict, y: str) -> tuple[float, float, int]:
    return (-math.log(max(pr[y], 1e-12)),
            sum((pr[c] - (c == y)) ** 2 for c in CLASES),
            int(max(pr, key=pr.get) == y))


def evaluar(obs: list[dict]) -> dict:
    corte = int(len(obs) * (1 - PRUEBA))
    train, test = obs[:corte], obs[corte:]
    if len(train) < 200 or len(test) < 50:
        return {"error": f"muy pocos partidos ({len(obs)})"}
    beta = ajustar([_x(o) for o in train], [o["y"] for o in train])
    base = {c: sum(o["y"] == c for o in train) / len(train) for c in CLASES}
    out = {}
    perd = {}
    for nombre, prob in (
        ("logistica", lambda o: dict(zip(CLASES, _probs(beta, _x(o), 3)))),
        ("frecuencia", lambda o: base),
        ("poissonSobreMu", lambda o: dict(zip(CLASES, poisson_sobre_mu(o["muL"], o["muV"])))),
    ):
        ll, br, ac = zip(*(_perdida(prob(o), o["y"]) for o in test))
        perd[nombre] = (list(ll), list(br))
        out[nombre] = {"logLoss": round(sum(ll) / len(ll), 4), "brier": round(sum(br) / len(br), 4),
                       "acierto": round(sum(ac) / len(ac), 4)}
    # calibración por tramo: lo que dice el modelo contra lo que pasó
    tramos = []
    for lo, hi in ((-9, -0.6), (-0.6, -0.3), (-0.3, 0.0), (0.0, 0.3), (0.3, 0.6), (0.6, 0.9), (0.9, 9)):
        g = [o for o in test if lo <= o["d"] < hi]
        if len(g) < 30:
            continue
        pm = [dict(zip(CLASES, _probs(beta, _x(o), 3))) for o in g]
        tramos.append({"d": [lo, hi], "n": len(g),
                       "modelo": {c: round(sum(p[c] for p in pm) / len(g), 3) for c in CLASES},
                       "real": {c: round(sum(o["y"] == c for o in g) / len(g), 3) for c in CLASES}})
    return {
        "partidos": len(obs), "entrenamiento": len(train), "prueba": len(test),
        "desde": obs[0]["fecha"][:10], "corte": test[0]["fecha"][:10], "hasta": obs[-1]["fecha"][:10],
        "frecuenciaPrueba": {c: round(sum(o["y"] == c for o in test) / len(test), 3) for c in CLASES},
        "modelos": out,
        "logisticaVsPoisson": _ic_dif(perd["poissonSobreMu"][0], perd["logistica"][0]),
        "logisticaVsFrecuencia": _ic_dif(perd["frecuencia"][0], perd["logistica"][0]),
        "tramos": tramos,
    }


def coeficientes(obs: list[dict]) -> dict:
    """El ajuste con TODO, sin estandarizar: lo que va a unxdos_motor.COEF."""
    b = ajustar([_x(o) for o in obs], [o["y"] for o in obs])
    return {"local": [round(v, 5) for v in b[:3]], "visita": [round(v, 5) for v in b[3:]]}


def historias_desde_dir(carpeta: str) -> dict[int, dict]:
    out = {}
    for f in glob.glob(os.path.join(carpeta, "c", "*.json")):
        t = int(os.path.basename(f)[:-5])
        nf = os.path.join(carpeta, "n", f"{t}.json")
        try:
            filas, niveles = json.load(open(f)), json.load(open(nf))
        except (OSError, ValueError):
            continue
        if not isinstance(filas, list) or not isinstance(niveles, list):
            continue
        out[t] = {"filas": sorted(filas, key=lambda r: r["fecha"]), "niveles": sorted(niveles, key=lambda r: r["fecha"])}
    return out


def historias_padron() -> dict[int, dict]:
    from backend.app import constantes_de, niveles_de
    from backend.backtest_burbuja import _equipos, padron
    out = {}
    for t in _equipos(MIN_PARTIDOS + 1, set(padron())):
        out[t] = {"filas": list(reversed(constantes_de(t, 500))), "niveles": list(reversed(niveles_de(t, 500)))}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--padron", action="store_true", help="equipos del padrón, desde las .db")
    ap.add_argument("--desde-dir", help="carpeta con c/<id>.json (/constantes) y n/<id>.json (/niveles)")
    ap.add_argument("--json", help="guardar el resultado en este archivo")
    a = ap.parse_args()
    historias = historias_desde_dir(a.desde_dir) if a.desde_dir else historias_padron()
    obs = observaciones(historias)
    r = evaluar(obs)
    if "error" not in r:
        r["coeficientes"] = coeficientes(obs)
        r["equipos"] = len(historias)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
