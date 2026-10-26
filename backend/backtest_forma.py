"""¿La forma de 5 partidos SIN AMISTOSOS hace mejor al gap §5? (incidencia 504)

La Ley de la Regresión al Nivel (`docs/skills/sad-analysis/references/
ley_regresion_nivel.md`) ya dice que un bajón armado sobre amistosos «es
ruido», y el backtest de julio dejó «tratamiento especial de amistosos» como
refinamiento candidato sin decidir (MOTOR §5, resultado 3). Hoy
`app.forma_reciente` cuenta los últimos 5 de cualquier competición: La
Louvière salía con 1,8 puntos de forma (un amistoso y una copa) con 0,5 en liga.

Esto compara las dos ventanas sobre los MISMOS partidos, sin fuga (nivel del
equipo y del rival estrictamente ANTES de cada partido):

  gap = μ(nivel, 2.0, 0.5) − forma        (la definición del motor)
  objetivo = residual del motor (pts − μ_partido) en el partido analizado y
             la media de los próximos 5 partidos oficiales (el horizonte de la ley)

Si la ventana sin amistosos es mejor, su gap tiene que correlacionar MÁS con el
residual futuro (gap > 0 = sub-rinde = tiende a mejorar = residual > 0). Lo que
importa es el subconjunto donde las dos ventanas DIFIEREN (algún amistoso en
los últimos 5): en el resto son el mismo número. Se reporta con un intervalo
bootstrap de la diferencia de correlaciones.

    python -m backend.backtest_forma --desde-dir carpeta   # c/<id>.json y n/<id>.json de la API
    python -m backend.backtest_forma --padron              # contra la base (Railway)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
from bisect import bisect_left

AMISTOSOS = {667}
VENTANA = 5
HORIZONTE = 5
RIVAL_PROMEDIO, LOCALIA_NEUTRA = 2.0, 0.5
MU = {"intercept": 1.241, "nivel": 0.334, "rival": -0.357, "localia": 0.382}   # μ v2 (MOTOR §5)
UMBRALES = ((0.5, "fuerte mejora"), (0.3, "leve mejora"), (-0.3, "equilibrio"), (-0.5, "leve empeora"))


def mu(nivel: float, rival: float, localia: float) -> float:
    v = MU["intercept"] + MU["nivel"] * nivel + MU["rival"] * rival + MU["localia"] * localia
    return max(0.0, min(3.0, v))


def puntos(gf: int, gc: int) -> int:
    return 3 if gf > gc else 1 if gf == gc else 0


def bucket(gap: float) -> str:
    for corte, nombre in UMBRALES:
        if gap > corte:
            return nombre
    return "fuerte empeora"


def _nivel_antes(serie: tuple[list[str], list[float]], fecha: str) -> float | None:
    fechas, niveles = serie
    i = bisect_left(fechas, fecha)
    return niveles[i - 1] if i > 0 else None


def observaciones(historias: dict[int, dict]) -> list[dict]:
    """Por equipo y partido OFICIAL: el gap con la ventana de siempre y sin
    amistosos, y el residual del partido y de los próximos HORIZONTE."""
    niv = {t: ([n["fecha"] for n in h["niveles"]], [float(n["nivel"]) for n in h["niveles"]])
           for t, h in historias.items() if h.get("niveles")}
    obs = []
    for t, h in historias.items():
        if t not in niv:
            continue
        filas = [f for f in h["filas"] if f.get("golesFavor") is not None and f.get("golesContra") is not None]
        # el residual de cada partido oficial con nivel previo de los dos lados
        resid: dict[int, float] = {}
        for j, f in enumerate(filas):
            if f.get("ligaId") in AMISTOSOS or f.get("rivalId") not in niv:
                continue
            nl, nr = _nivel_antes(niv[t], f["fecha"]), _nivel_antes(niv[f["rivalId"]], f["fecha"])
            if nl is None or nr is None:
                continue
            resid[j] = puntos(f["golesFavor"], f["golesContra"]) - mu(nl, nr, 1.0 if f["condicion"] == "Local" else 0.0)
        oficiales = [j for j, f in enumerate(filas) if f.get("ligaId") not in AMISTOSOS]
        for k, i in enumerate(oficiales):
            if i not in resid:
                continue
            previas = filas[:i]
            todas = previas[-VENTANA:]
            sin_am = [f for f in previas if f.get("ligaId") not in AMISTOSOS][-VENTANA:]
            if len(todas) < VENTANA or len(sin_am) < VENTANA:
                continue
            nivel = _nivel_antes(niv[t], filas[i]["fecha"])
            if nivel is None:
                continue
            futuros = [resid[j] for j in oficiales[k:k + HORIZONTE] if j in resid]
            if len(futuros) < 3:
                continue
            esperados = mu(nivel, RIVAL_PROMEDIO, LOCALIA_NEUTRA)
            forma = lambda fs: sum(puntos(f["golesFavor"], f["golesContra"]) for f in fs) / VENTANA  # noqa: E731
            obs.append({
                "equipo": t, "fixtureId": filas[i]["fixtureId"], "fecha": filas[i]["fecha"],
                "amistososEnVentana": sum(1 for f in todas if f.get("ligaId") in AMISTOSOS),
                "gapTodas": esperados - forma(todas), "gapSinAmistosos": esperados - forma(sin_am),
                "residual": resid[i], "residualHorizonte": sum(futuros) / len(futuros),
            })
    obs.sort(key=lambda o: o["fecha"])
    return obs


def _corr(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 10:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else None


def _por_bucket(obs: list[dict], campo: str, objetivo: str) -> list[dict]:
    out = []
    for nombre in [u[1] for u in UMBRALES] + ["fuerte empeora"]:
        g = [o[objetivo] for o in obs if bucket(o[campo]) == nombre]
        out.append({"senal": nombre, "n": len(g), "residualMedio": round(sum(g) / len(g), 3) if g else None})
    return out


def _ic_dif_corr(obs: list[dict], objetivo: str, n_boot: int = 1000, semilla: int = 2026) -> dict:
    """corr(gap sin amistosos) − corr(gap con todas), con IC bootstrap al 95 %
    remuestreando EQUIPOS (las observaciones de un equipo no son independientes)."""
    por_eq: dict[int, list[dict]] = {}
    for o in obs:
        por_eq.setdefault(o["equipo"], []).append(o)
    equipos = list(por_eq)
    rnd = random.Random(semilla)

    def dif(muestra):
        ys = [o[objetivo] for o in muestra]
        a = _corr([o["gapSinAmistosos"] for o in muestra], ys)
        b = _corr([o["gapTodas"] for o in muestra], ys)
        return None if a is None or b is None else a - b

    punto = dif(obs)
    difs = []
    for _ in range(n_boot):
        m = [o for e in (rnd.choice(equipos) for _ in equipos) for o in por_eq[e]]
        d = dif(m)
        if d is not None:
            difs.append(d)
    difs.sort()
    if not difs or punto is None:
        return {"dif": punto, "ic95": None}
    return {"dif": round(punto, 4), "ic95": [round(difs[int(0.025 * len(difs))], 4), round(difs[int(0.975 * len(difs)) - 1], 4)]}


def evaluar(obs: list[dict]) -> dict:
    difieren = [o for o in obs if o["amistososEnVentana"] > 0]
    out = {"observaciones": len(obs), "conAmistosoEnVentana": len(difieren),
           "equipos": len({o["equipo"] for o in obs}),
           "desde": obs[0]["fecha"][:10] if obs else None, "hasta": obs[-1]["fecha"][:10] if obs else None}
    for nombre, sub in (("todas", obs), ("difieren", difieren)):
        r = {}
        for objetivo in ("residual", "residualHorizonte"):
            ys = [o[objetivo] for o in sub]
            r[objetivo] = {
                "corrConTodas": _r(_corr([o["gapTodas"] for o in sub], ys)),
                "corrSinAmistosos": _r(_corr([o["gapSinAmistosos"] for o in sub], ys)),
                "difSinMenosCon": _ic_dif_corr(sub, objetivo) if len(sub) >= 50 else None,
                "bucketsConTodas": _por_bucket(sub, "gapTodas", objetivo),
                "bucketsSinAmistosos": _por_bucket(sub, "gapSinAmistosos", objetivo),
            }
        out[nombre] = r
    # cuántas veces la señal CAMBIA de bucket al sacar los amistosos (La Louvière)
    out["cambiaDeSenal"] = sum(1 for o in difieren if bucket(o["gapTodas"]) != bucket(o["gapSinAmistosos"]))
    out["inviertenSigno"] = sum(1 for o in difieren if o["gapTodas"] * o["gapSinAmistosos"] < 0
                                and abs(o["gapTodas"]) > 0.3 and abs(o["gapSinAmistosos"]) > 0.3)
    return out


def _r(v):
    return None if v is None else round(v, 4)


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
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend import db
    from backend.app import constantes_de, niveles_de
    from backend.ingesta.extractor import LIGAS_INTERNACIONALES, ligas_vivo
    ligas = sorted(ligas_vivo() - LIGAS_INTERNACIONALES - {1})
    marcas = ",".join("?" * len(ligas))
    equipos = {r["t"] for r in db.query("sad", f"SELECT DISTINCT home_team_id AS t FROM fixtures WHERE league_id IN ({marcas})", tuple(ligas))}
    return {t: {"filas": list(reversed(constantes_de(t, 500))), "niveles": list(reversed(niveles_de(t, 500)))}
            for t in equipos}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--desde-dir", help="carpeta con c/<id>.json (/constantes) y n/<id>.json (/niveles)")
    ap.add_argument("--padron", action="store_true", help="las ligas del padrón, desde la base")
    ap.add_argument("--json", help="guardar el resultado en este archivo")
    a = ap.parse_args()
    historias = historias_desde_dir(a.desde_dir) if a.desde_dir else historias_padron()
    res = evaluar(observaciones(historias))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if a.json:
        json.dump(res, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
