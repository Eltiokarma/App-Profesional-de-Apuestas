"""¿El 1X2 del motor mejora con el nivel SIN amistosos o SIN internacionales? (30/10/2026, incidencia 860)

Konyaspor 0-4 Galatasaray: el motor dio 41 % al 14.º y la ventana de 20 del
nivel del líder traía seis amistosos de pretemporada y tres de Champions
(1,65 pts/p en la ventana contra 2,44 en la liga). El nivel (MOTOR §2: P =
puntos de los últimos 20 + G = balance de goles de los últimos 5 + 1) cuenta
TODAS las competiciones. La fórmula es sagrada: esto MIDE, no cambia nada.

Tres variantes del nivel, con la MISMA fórmula (`ingesta.niveles.calcular_niveles`)
sobre historias distintas:
- `actual`: todas las competiciones (lo que corre hoy);
- `sinAmistosos`: la historia sin amistosos (Friendlies / Friendlies Clubs);
- `sinAmistososNiInternacionales`: además sin los torneos internacionales de clubes.

Los partidos a predecir son los MISMOS en las tres (no amistosos, con 20
partidos previos en la historia más corta de los dos equipos: sin la regla
retroactiva §2.2, que pondría en el nivel resultados del futuro). Para cada
variante: μ_partido como el motor, el 1X2 con los coeficientes de producción
(`unxdos_motor.COEF`) y con la logística REAJUSTADA a esa variante (corte
temporal 80/20), log-loss y Brier con el intervalo emparejado contra `actual`,
por subconjunto (los partidos con 3+ amistosos en la ventana de algún lado,
con 2+ internacionales, y el resto) y contra el MERCADO en los partidos de la
prueba con cuota capturada.

    python -m backend.backtest_nivel_ventana --padron --fixture 1584455
    python -m backend.backtest_nivel_ventana --json salida.json

MEDIDO el 30/10/2026 en Railway (--padron, 9.191 partidos de prueba, 2.125 con
cuota), logística reajustada, diferencia de log-loss contra `actual`:
- todos: sin amistosos +0,00090 (IC −0,00041 a +0,00234), sin amistosos ni
  internacionales +0,00053 (IC −0,00181 a +0,00281): no se distinguen;
- con 3+ amistosos (n = 2.491): +0,00480 (IC −0,00034 a +0,00900) y +0,00657
  (IC +0,00058 a +0,01186): sacar también los internacionales EMPEORA;
- con 2+ internacionales y el resto: no se distinguen.
- 1584455: el local 41,4 % → 40,8 % sin amistosos → 40,0 % sin los dos (nivel
  de Galatasaray 2,81 → 3,06 → 3,13, el de Konyaspor 2,55 → 2,75): la causa
  del 41 % es la localía (0,382 de μ = 0,55 de nivel), no la ventana.
- contra el mercado: el motor pierde 0,061 de log-loss en las tres variantes
  (1,031 contra 0,970); con 3+ amistosos pierde 0,084 (1,024 contra 0,941,
  n = 989) y en el resto 0,041. Ahí el aviso de fiabilidad «media» se sostiene.
La fórmula NO se cambia.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from bisect import bisect_left

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend import db  # noqa: E402
from backend.analisis import unxdos_motor  # noqa: E402
from backend.analisis import ventana_nivel as vn  # noqa: E402
from backend.app import mu  # noqa: E402
from backend.backtest_burbuja_1x2 import _ic_dif, _probs, ajustar, cuotas_1x2  # noqa: E402
from backend.ingesta.niveles import calcular_niveles  # noqa: E402
from backend.ingesta.pipeline import leer_fixtures, sin_duplicados  # noqa: E402

PRUEBA = 0.2
CLASES = ("L", "E", "V")
VARIANTES = ("actual", "sinAmistosos", "sinAmistososNiInternacionales")


def _nombres_ligas() -> dict[int, str]:
    try:
        return {r["id"]: r["name"] for r in db.query("sad", "SELECT id, name FROM leagues")}
    except Exception:  # noqa: BLE001 — base sin la tabla leagues: solo los ids de amistosos conocidos
        return {}


def clase(liga: int, nombres: dict[int, str], inter: set[int]) -> str:
    if vn.es_amistoso(liga, nombres.get(liga)):
        return "amistoso"
    return "internacional" if liga in inter else "otro"


def entra(variante: str, cl: str) -> bool:
    if variante == "actual":
        return True
    if variante == "sinAmistosos":
        return cl != "amistoso"
    return cl == "otro"


def historias(fixtures, nombres: dict[int, str], inter: set[int]) -> dict[int, list[tuple]]:
    """team → [(fixture_id, date, gf, ga, clase)] en el orden del motor (date, id)."""
    h: dict[int, list[tuple]] = {}
    for fid, date, home, away, gh, ga, _st, liga, *_ in fixtures:
        cl = clase(liga, nombres, inter)
        h.setdefault(home, []).append((fid, str(date), gh, ga, cl))
        h.setdefault(away, []).append((fid, str(date), ga, gh, cl))
    return h


def niveles_variante(hist: list[tuple], variante: str) -> tuple[list[str], list[float]]:
    """Fechas y niveles de la historia filtrada; solo los niveles REALES (desde el
    partido nº 20 de esa historia: el retroactivo §2.2 mira el futuro)."""
    propia = [(f, d, gf, ga) for f, d, gf, ga, cl in hist if entra(variante, cl)]
    filas = calcular_niveles(propia)
    return [d for _, d, _ in filas[19:]], [lvl for _, _, lvl in filas[19:]]


def _antes(fechas: list[str], niveles: list[float], fecha: str) -> float | None:
    i = bisect_left(fechas, fecha)
    return niveles[i - 1] if i > 0 else None


def composicion_antes(fechas: list[str], clases: list[str], fecha: str) -> dict:
    """La ventana de 20 de la variante `actual` antes de `fecha`, contada (bisect:
    sin recorrer la historia entera por partido)."""
    i = bisect_left(fechas, fecha)
    previos = clases[max(0, i - vn.VENTANA):i]
    return {"amistosos": previos.count("amistoso"), "internacionales": previos.count("internacional")}


def observaciones(fixtures, ligas_objetivo: set[int] | None) -> tuple[list[dict], dict]:
    nombres = _nombres_ligas()
    inter = vn._internacionales()
    h = historias(fixtures, nombres, inter)
    niv = {v: {t: niveles_variante(x, v) for t, x in h.items()} for v in VARIANTES}
    idx = {t: ([x[1] for x in hh], [x[4] for x in hh]) for t, hh in h.items()}
    obs = []
    for fid, date, home, away, gh, ga, _st, liga, *_ in fixtures:
        cl = clase(liga, nombres, inter)
        if cl == "amistoso" or (ligas_objetivo and liga not in ligas_objetivo and cl != "internacional"):
            continue
        fecha = str(date)
        lv = {}
        for v in VARIANTES:
            nl, nv_ = _antes(*niv[v][home], fecha), _antes(*niv[v][away], fecha)
            if nl is None or nv_ is None:
                break
            lv[v] = (nl, nv_)
        if len(lv) < len(VARIANTES):
            continue          # el mismo conjunto de partidos en las tres variantes
        ca, cb = composicion_antes(*idx[home], fecha), composicion_antes(*idx[away], fecha)
        o = {"fixtureId": fid, "fecha": fecha, "liga": liga, "clase": cl,
             "y": "L" if gh > ga else "V" if gh < ga else "E",
             "amistosos": max(ca["amistosos"], cb["amistosos"]),
             "internacionales": max(ca["internacionales"], cb["internacionales"])}
        for v, (nl, nv_) in lv.items():
            mu_l, mu_v = mu(nl, nv_, 1.0), mu(nv_, nl, 0.0)
            o[v] = {"nivelL": round(nl, 4), "nivelV": round(nv_, 4), "muL": mu_l, "muV": mu_v, "d": mu_l - mu_v}
        obs.append(o)
    obs.sort(key=lambda o: o["fecha"])
    return obs, h


def _x(d: float) -> list[float]:
    return [1.0, d, d * d]


def _perdida(pr: dict, y: str) -> tuple[float, float, int]:
    return (-math.log(max(pr[y], 1e-12)), sum((pr[c] - (c == y)) ** 2 for c in CLASES),
            int(max(pr, key=pr.get) == y))


def _prob_produccion(o: dict, v: str) -> dict:
    p = unxdos_motor.probabilidades(o[v]["muL"], o[v]["muV"])
    return {"L": p["local"] / 100, "E": p["empate"] / 100, "V": p["visita"] / 100}


def _resumen(perd: list[tuple]) -> dict:
    n = len(perd)
    return {"n": n, "logLoss": round(sum(p[0] for p in perd) / n, 5), "brier": round(sum(p[1] for p in perd) / n, 5),
            "acierto": round(sum(p[2] for p in perd) / n, 4)} if n else {"n": 0}


SUBCONJUNTOS = {
    "todos": lambda o: True,
    "conAmistosos": lambda o: o["amistosos"] >= vn.UMBRAL_AMISTOSOS,
    "conInternacionales": lambda o: o["internacionales"] >= 2,
    "resto": lambda o: o["amistosos"] < vn.UMBRAL_AMISTOSOS and o["internacionales"] < 2,
}


def evaluar(obs: list[dict], mercado: dict | None = None) -> dict:
    corte = int(len(obs) * (1 - PRUEBA))
    train, test = obs[:corte], obs[corte:]
    if len(train) < 200 or len(test) < 50:
        return {"error": f"muy pocos partidos ({len(obs)})"}
    perd: dict[str, dict[str, list]] = {}
    for v in VARIANTES:
        beta = ajustar([_x(o[v]["d"]) for o in train], [o["y"] for o in train])
        perd[v] = {
            "produccion": [_perdida(_prob_produccion(o, v), o["y"]) for o in test],
            "reajustada": [_perdida(dict(zip(CLASES, _probs(beta, _x(o[v]["d"]), 3))), o["y"]) for o in test],
        }
    out = {"partidos": len(obs), "entrenamiento": len(train), "prueba": len(test),
           "desde": obs[0]["fecha"][:10], "corte": test[0]["fecha"][:10], "hasta": obs[-1]["fecha"][:10],
           "porSubconjunto": {}}
    for nombre, cond in SUBCONJUNTOS.items():
        idx = [i for i, o in enumerate(test) if cond(o)]
        if len(idx) < 30:
            out["porSubconjunto"][nombre] = {"n": len(idx), "nota": "menos de 30 partidos: no se compara"}
            continue
        sub = {"n": len(idx)}
        for modo in ("produccion", "reajustada"):
            sub[modo] = {v: _resumen([perd[v][modo][i] for i in idx]) for v in VARIANTES}
            base = [perd["actual"][modo][i][0] for i in idx]
            sub[modo]["vsActual"] = {v: _ic_dif(base, [perd[v][modo][i][0] for i in idx])
                                     for v in VARIANTES if v != "actual"}
        out["porSubconjunto"][nombre] = sub
    if mercado:
        idx = [i for i, o in enumerate(test) if o["fixtureId"] in mercado]
        if len(idx) >= 30:
            ll_m = []
            for i in idx:
                pl, pe, pv, *_ = mercado[test[i]["fixtureId"]]
                ll_m.append(-math.log(max({"L": pl, "E": pe, "V": pv}[test[i]["y"]], 1e-12)))
            out["contraMercado"] = {
                "n": len(idx), "mercadoLogLoss": round(sum(ll_m) / len(idx), 5),
                **{v: {"logLoss": round(sum(perd[v]["reajustada"][i][0] for i in idx) / len(idx), 5),
                       "mercadoMenosVariante": _ic_dif([perd[v]["reajustada"][i][0] for i in idx], ll_m)}
                   for v in VARIANTES},
                "conAmistosos": _contra_mercado_sub(test, idx, perd, mercado,
                                                    lambda o: o["amistosos"] >= vn.UMBRAL_AMISTOSOS),
            }
        else:
            out["contraMercado"] = {"n": len(idx), "nota": "menos de 30 partidos de la prueba con cuota"}
    out["lectura"] = lectura(out)
    return out


def _contra_mercado_sub(test, idx, perd, mercado, cond) -> dict:
    sel = [i for i in idx if cond(test[i])]
    if len(sel) < 30:
        return {"n": len(sel), "nota": "menos de 30: no se compara"}
    ll_m = []
    for i in sel:
        pl, pe, pv, *_ = mercado[test[i]["fixtureId"]]
        ll_m.append(-math.log(max({"L": pl, "E": pe, "V": pv}[test[i]["y"]], 1e-12)))
    return {"n": len(sel), "mercadoLogLoss": round(sum(ll_m) / len(sel), 5),
            **{v: round(sum(perd[v]["reajustada"][i][0] for i in sel) / len(sel), 5) for v in VARIANTES}}


def lectura(r: dict) -> str:
    """Lo que se puede concluir, en una línea por subconjunto: una variante MEJORA
    si el intervalo de su diferencia de log-loss contra `actual` queda bajo cero."""
    out = []
    for nombre, sub in r["porSubconjunto"].items():
        if "reajustada" not in sub:
            continue
        for v, ic in sub["reajustada"]["vsActual"].items():
            if not ic.get("ic95"):
                continue
            a, b = ic["ic95"]
            veredicto = ("MEJORA" if b < 0 else "EMPEORA" if a > 0 else "no se distingue")
            out.append(f"{nombre}: {v} {veredicto} ({ic['media']:+.5f}, IC {a:+.5f} a {b:+.5f}, n={sub['n']})")
    return " · ".join(out) or "sin comparaciones con muestra suficiente"


def caso(obs: list[dict], hist: dict, fixture_id: int) -> dict | None:
    o = next((x for x in obs if x["fixtureId"] == fixture_id), None)
    if not o:
        return None
    out = {"fixtureId": fixture_id, "fecha": o["fecha"][:10], "resultado": o["y"],
           "amistosos": o["amistosos"], "internacionales": o["internacionales"]}
    for v in VARIANTES:
        p = unxdos_motor.probabilidades(o[v]["muL"], o[v]["muV"])
        out[v] = {"nivelL": o[v]["nivelL"], "nivelV": o[v]["nivelV"], "1x2": p}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--padron", action="store_true", help="solo partidos de las ligas del padrón (y los internacionales)")
    ap.add_argument("--fixture", type=int, action="append", default=[],
                    help="mostrar el caso (niveles y 1X2 en cada variante), p. ej. 1584455")
    ap.add_argument("--json", help="guardar el resultado en este archivo")
    a = ap.parse_args()
    ligas = None
    if a.padron:
        from backend.backtest_burbuja import padron
        ligas = set(padron())
    fixtures, _ = sin_duplicados(leer_fixtures(db.db_path("sad")))
    obs, hist = observaciones(fixtures, ligas)
    corte = int(len(obs) * (1 - PRUEBA))
    mercado = cuotas_1x2([o["fixtureId"] for o in obs[corte:]])
    r = evaluar(obs, mercado)
    r["casos"] = [c for c in (caso(obs, hist, f) for f in a.fixture) if c]
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
