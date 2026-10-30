"""¿El 1X2 del motor mejora con la LOCALÍA POR LIGA? (30/10/2026, tras la incidencia 860)

Konyaspor 0-4 Galatasaray: el backtest del nivel (`backtest_nivel_ventana`)
mostró que el 41 % del local no venía de los amistosos sino de la LOCALÍA. μ
le suma 0,382 al local (`app.MU`, MOTOR §2), lo que vale una diferencia de
nivel de 0,55, y es UNA para el mundo. La calibración por liga de §5 ya la había
visto ir de +0,23 (amistosos) a +0,73 (Perú), sin decidir nada. Esto MIDE si
una localía por liga predice mejor el 1X2. La fórmula es sagrada: no cambia
sin el visto bueno del usuario.

La localía de una liga se estima SOLO con el entrenamiento (los partidos más
viejos, corte temporal 80/20). En puntos, es la diferencia local − visitante
que el nivel no explica:

    h_liga = media(pts_L − pts_V − d) + 0,382      (d = μ_L − μ_V del motor)

y se ENCOGE hacia la de todas las ligas juntas con un peso empírico (Bayes
empírico: cuánto varían de verdad las ligas contra cuánto ruido trae la media
de cada una):

    h* = (n·h_liga + K·h_todas) / (n + K),   K = σ² / τ²

El 1X2 de cada variante usa d' = d − 0,382 + h* con la logística multinomial
REAJUSTADA en el mismo entrenamiento (la de producción está ajustada a la d
global; un corrimiento parejo de todas las ligas lo absorbe el reajuste, así
que lo único que se mide es la diferencia ENTRE ligas). Variantes: `global`
(lo de hoy), `porLiga` (encogida) y `porLigaCruda` (sin encoger: para ver
cuánto sobreajusta). Log-loss con el intervalo emparejado contra `global`, en
todos, por liga y contra el MERCADO en los partidos de la prueba con cuota; y
la localía por liga calculada con TODO, lista para copiar si el usuario
decide usarla.

    python -m backend.backtest_localia_liga --padron --fixture 1584455
    python -m backend.backtest_localia_liga --padron --json salida.json

MEDIDO el 30/10/2026 en Railway (9.538 partidos de prueba, 2.126 con cuota):
- todos: porLiga −0,00171 (IC −0,00303 a −0,00054), porLigaCruda −0,00183
  (IC −0,00341 a −0,00052): MEJORA, pero poco;
- por liga: de 27 con 150+ de prueba, 4 mejoran y ninguna empeora;
- con cuota: porLiga +0,00023, no se distingue; el mercado le gana a global
  por 0,06083 y a porLiga por 0,06105;
- localías: Sudamérica ~0,57-0,77, Europa ~0,30-0,51; la Süper Lig 0,479;
- 1584455: el local 41,0 % (global reajustada) → 41,2 % (porLiga): la
  localía no explica el caso.
La fórmula NO se cambia: lo que gana en todos no aparece en los partidos que
se analizan, y el motor sigue 0,061 detrás del mercado.
"""
from __future__ import annotations

import argparse
import json
import math
import os

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend import backtest_nivel_ventana as bnv  # noqa: E402
from backend import db  # noqa: E402
from backend.analisis import unxdos_motor  # noqa: E402
from backend.app import MU, mu  # noqa: E402
from backend.backtest_burbuja_1x2 import _ic_dif, _probs, ajustar, cuotas_1x2  # noqa: E402
from backend.ingesta.pipeline import leer_fixtures, sin_duplicados  # noqa: E402

PRUEBA = 0.2
CLASES = ("L", "E", "V")
VARIANTES = ("global", "porLiga", "porLigaCruda")
LOCALIA = MU["localia"]
MIN_LIGA = 30            # partidos de entrenamiento para estimar la localía de una liga
MIN_PRUEBA_LIGA = 150    # partidos de prueba para comparar dentro de una liga


def _pts(a: int, b: int) -> int:
    return 3 if a > b else 1 if a == b else 0


def observaciones(fixtures, ligas_objetivo: set[int] | None) -> tuple[list[dict], dict[int, str]]:
    """Un partido por fixture (sin amistosos), con el nivel ANTERIOR de cada lado
    (sin el retroactivo §2.2, como `backtest_nivel_ventana`)."""
    nombres = bnv._nombres_ligas()
    inter = bnv.vn._internacionales()
    h = bnv.historias(fixtures, nombres, inter)
    niv = {t: bnv.niveles_variante(x, "actual") for t, x in h.items()}
    obs = []
    for fid, date, home, away, gh, ga, _st, liga, *_ in fixtures:
        cl = bnv.clase(liga, nombres, inter)
        if cl == "amistoso" or (ligas_objetivo and liga not in ligas_objetivo and cl != "internacional"):
            continue
        fecha = str(date)
        nl, nv = bnv._antes(*niv[home], fecha), bnv._antes(*niv[away], fecha)
        if nl is None or nv is None:
            continue
        d = mu(nl, nv, 1.0) - mu(nv, nl, 0.0)
        obs.append({"fixtureId": fid, "fecha": fecha, "liga": liga, "nivelL": round(nl, 4),
                    "nivelV": round(nv, 4), "d": d, "dif": _pts(gh, ga) - _pts(ga, gh),
                    "y": "L" if gh > ga else "V" if gh < ga else "E"})
    obs.sort(key=lambda o: (o["fecha"], o["fixtureId"]))
    return obs, nombres


def localias(obs: list[dict]) -> dict:
    """La localía de cada liga con `MIN_LIGA`+ partidos, cruda y encogida, y los
    parámetros del encogimiento. `todas` es la de todas las ligas juntas: la de
    las ligas sin muestra y hacia la que se encoge."""
    por: dict[int, list[float]] = {}
    for o in obs:
        por.setdefault(o["liga"], []).append(o["dif"] - o["d"])
    res = [r for rs in por.values() for r in rs]
    if len(res) < 2:
        return {"tabla": {}, "todas": LOCALIA, "K": None, "tau2": None, "sigma2": None}
    m = sum(res) / len(res)
    sigma2 = sum((r - m) ** 2 for r in res) / (len(res) - 1)
    todas = m + LOCALIA
    ligas = {l: rs for l, rs in por.items() if len(rs) >= MIN_LIGA}
    medias = {l: sum(rs) / len(rs) + LOCALIA for l, rs in ligas.items()}
    tau2 = 0.0
    if len(medias) >= 2:
        mm = sum(medias.values()) / len(medias)
        var_medias = sum((v - mm) ** 2 for v in medias.values()) / (len(medias) - 1)
        ruido = sum(sigma2 / len(ligas[l]) for l in medias) / len(medias)
        tau2 = max(var_medias - ruido, 0.0)
    # sin variación real entre ligas, K infinito: todas quedan en la de todas
    K = sigma2 / tau2 if tau2 > 1e-9 else math.inf
    tabla = {}
    for l, v in medias.items():
        n = len(ligas[l])
        enc = todas if math.isinf(K) else (n * v + K * todas) / (n + K)
        tabla[l] = {"n": n, "cruda": v, "encogida": enc}
    return {"tabla": tabla, "todas": todas, "K": K, "tau2": tau2, "sigma2": sigma2}


def d_variante(o: dict, v: str, loc: dict) -> float:
    if v == "global":
        return o["d"]
    t = loc["tabla"].get(o["liga"])
    h = (t["encogida"] if v == "porLiga" else t["cruda"]) if t else loc["todas"]
    return o["d"] - LOCALIA + h


def _x(d: float) -> list[float]:
    return [1.0, d, d * d]


def _perdida(pr: dict, y: str) -> tuple[float, float, int]:
    return (-math.log(max(pr[y], 1e-12)), sum((pr[c] - (c == y)) ** 2 for c in CLASES),
            int(max(pr, key=pr.get) == y))


def _resumen(perd: list[tuple]) -> dict:
    n = len(perd)
    return {"n": n, "logLoss": round(sum(p[0] for p in perd) / n, 5), "brier": round(sum(p[1] for p in perd) / n, 5),
            "acierto": round(sum(p[2] for p in perd) / n, 4)} if n else {"n": 0}


def _veredicto(ic: dict) -> str:
    a, b = ic["ic95"]
    return "MEJORA" if b < 0 else "EMPEORA" if a > 0 else "no se distingue"


def _tabla_json(loc: dict, nombres: dict[int, str]) -> list[dict]:
    return sorted(({"liga": l, "nombre": nombres.get(l, f"liga {l}"), "n": t["n"],
                    "cruda": round(t["cruda"], 3), "encogida": round(t["encogida"], 3)}
                   for l, t in loc["tabla"].items()), key=lambda r: -r["encogida"])


def evaluar(obs: list[dict], mercado: dict | None = None, nombres: dict[int, str] | None = None,
            casos: list[int] | None = None) -> dict:
    nombres = nombres or {}
    corte = int(len(obs) * (1 - PRUEBA))
    train, test = obs[:corte], obs[corte:]
    if len(train) < 200 or len(test) < 50:
        return {"error": f"muy pocos partidos ({len(obs)})"}
    loc = localias(train)
    betas, perd = {}, {}
    for v in VARIANTES:
        betas[v] = ajustar([_x(d_variante(o, v, loc)) for o in train], [o["y"] for o in train])
        perd[v] = [_perdida(dict(zip(CLASES, _probs(betas[v], _x(d_variante(o, v, loc)), 3))), o["y"])
                   for o in test]

    def prod(o):
        p = unxdos_motor.probabilidades(o["d"], 0.0)
        return {"L": p["local"] / 100, "E": p["empate"] / 100, "V": p["visita"] / 100}

    base = [p[0] for p in perd["global"]]
    out = {"partidos": len(obs), "entrenamiento": len(train), "prueba": len(test),
           "desde": obs[0]["fecha"][:10], "corte": test[0]["fecha"][:10], "hasta": obs[-1]["fecha"][:10],
           "encogimiento": {"K": None if math.isinf(loc["K"] or 0) else round(loc["K"], 1),
                            "tau": round(math.sqrt(loc["tau2"]), 4) if loc["tau2"] is not None else None,
                            "localiaTodas": round(loc["todas"], 4), "ligas": len(loc["tabla"])},
           "todos": {"n": len(test),
                     "produccion": _resumen([_perdida(prod(o), o["y"]) for o in test]),
                     **{v: _resumen(perd[v]) for v in VARIANTES},
                     "vsGlobal": {v: _ic_dif(base, [p[0] for p in perd[v]]) for v in VARIANTES if v != "global"}}}

    # por liga: la localía estimada en el entrenamiento y si mejora ADENTRO de la liga
    por_liga = []
    idx_liga: dict[int, list[int]] = {}
    for i, o in enumerate(test):
        idx_liga.setdefault(o["liga"], []).append(i)
    for l, idx in idx_liga.items():
        t = loc["tabla"].get(l)
        if len(idx) < MIN_PRUEBA_LIGA or not t:
            continue
        ic = _ic_dif([perd["global"][i][0] for i in idx], [perd["porLiga"][i][0] for i in idx])
        por_liga.append({"liga": l, "nombre": nombres.get(l, f"liga {l}"), "nEntrenamiento": t["n"],
                         "localia": {"cruda": round(t["cruda"], 3), "encogida": round(t["encogida"], 3)},
                         "nPrueba": len(idx),
                         "logLoss": {v: round(sum(perd[v][i][0] for i in idx) / len(idx), 5) for v in VARIANTES},
                         "porLigaVsGlobal": ic, "veredicto": _veredicto(ic) if ic.get("ic95") else None})
    out["porLiga"] = sorted(por_liga, key=lambda r: -r["localia"]["encogida"])

    if mercado:
        idx = [i for i, o in enumerate(test) if o["fixtureId"] in mercado]
        if len(idx) >= 30:
            ll_m = []
            for i in idx:
                pl, pe, pv, *_ = mercado[test[i]["fixtureId"]]
                ll_m.append(-math.log(max({"L": pl, "E": pe, "V": pv}[test[i]["y"]], 1e-12)))
            out["contraMercado"] = {
                "n": len(idx), "mercadoLogLoss": round(sum(ll_m) / len(idx), 5),
                **{v: {"logLoss": round(sum(perd[v][i][0] for i in idx) / len(idx), 5),
                       "mercadoMenosVariante": _ic_dif([perd[v][i][0] for i in idx], ll_m)} for v in VARIANTES},
                "porLigaVsGlobal": _ic_dif([perd["global"][i][0] for i in idx], [perd["porLiga"][i][0] for i in idx]),
            }
        else:
            out["contraMercado"] = {"n": len(idx), "nota": "menos de 30 partidos de la prueba con cuota"}

    out["casos"] = []
    en_train = {o["fixtureId"] for o in train}
    for fid in casos or []:
        o = next((x for x in test if x["fixtureId"] == fid), None) or next((x for x in train if x["fixtureId"] == fid), None)
        if not o:
            continue
        c = {"fixtureId": fid, "fecha": o["fecha"][:10], "liga": o["liga"], "nombre": nombres.get(o["liga"], ""),
             "resultado": o["y"], "nivelL": o["nivelL"], "nivelV": o["nivelV"],
             "enEntrenamiento": fid in en_train, "produccion": {k: round(100 * v, 1) for k, v in prod(o).items()}}
        for v in VARIANTES:
            t = loc["tabla"].get(o["liga"])
            c[v] = {"d": round(d_variante(o, v, loc), 4),
                    "1x2": {k: round(100 * p, 1) for k, p in zip(CLASES, _probs(betas[v], _x(d_variante(o, v, loc)), 3))}}
            if v != "global":
                c[v]["localia"] = round((t["encogida"] if v == "porLiga" else t["cruda"]) if t else loc["todas"], 3)
        out["casos"].append(c)

    out["localiaEntrenamiento"] = _tabla_json(loc, nombres)
    out["lectura"] = lectura(out)
    return out


def lectura(r: dict) -> str:
    """En una línea: la localía por liga MEJORA si el intervalo de su diferencia
    de log-loss contra la global queda bajo cero. Por liga se cuentan las que
    mejoran y empeoran: con ~40 ligas, el azar solo da 1 o 2 de cada lado."""
    out = []
    for v, ic in r["todos"]["vsGlobal"].items():
        if ic.get("ic95"):
            a, b = ic["ic95"]
            out.append(f"todos: {v} {_veredicto(ic)} ({ic['media']:+.5f}, IC {a:+.5f} a {b:+.5f}, n={r['todos']['n']})")
    pl = [x for x in r["porLiga"] if x["veredicto"]]
    if pl:
        mej = [x["nombre"] for x in pl if x["veredicto"] == "MEJORA"]
        emp = [x["nombre"] for x in pl if x["veredicto"] == "EMPEORA"]
        out.append(f"por liga ({len(pl)} con {MIN_PRUEBA_LIGA}+ de prueba): mejoran {len(mej)}"
                   + (f" ({', '.join(mej)})" if mej else "") + f", empeoran {len(emp)}"
                   + (f" ({', '.join(emp)})" if emp else ""))
    cm = r.get("contraMercado") or {}
    if cm.get("porLigaVsGlobal", {}).get("ic95"):
        ic = cm["porLigaVsGlobal"]
        out.append(f"con cuota: porLiga {_veredicto(ic)} ({ic['media']:+.5f}, n={cm['n']}); "
                   f"el mercado le gana a global por {-cm['global']['mercadoMenosVariante']['media']:.5f} "
                   f"y a porLiga por {-cm['porLiga']['mercadoMenosVariante']['media']:.5f}")
    return " · ".join(out) or "sin comparaciones con muestra suficiente"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--padron", action="store_true", help="solo partidos de las ligas del padrón (y los internacionales)")
    ap.add_argument("--fixture", type=int, action="append", default=[],
                    help="mostrar el caso (localía de su liga y 1X2 en cada variante), p. ej. 1584455")
    ap.add_argument("--json", help="guardar el resultado en este archivo")
    a = ap.parse_args()
    ligas = None
    if a.padron:
        from backend.backtest_burbuja import padron
        ligas = set(padron())
    fixtures, _ = sin_duplicados(leer_fixtures(db.db_path("sad")))
    obs, nombres = observaciones(fixtures, ligas)
    corte = int(len(obs) * (1 - PRUEBA))
    mercado = cuotas_1x2([o["fixtureId"] for o in obs[corte:]])
    r = evaluar(obs, mercado, nombres, a.fixture)
    if "error" not in r:
        # la tabla con TODO (entrenamiento y prueba): lo que iría al motor si el usuario lo decide
        completa = localias(obs)
        r["localiaPorLiga"] = {"K": None if math.isinf(completa["K"] or 0) else round(completa["K"], 1),
                               "todas": round(completa["todas"], 4), "tabla": _tabla_json(completa, nombres)}
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
