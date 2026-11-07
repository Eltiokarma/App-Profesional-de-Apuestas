"""Backtest de la «ley anticulebras» (pedido del usuario, 07/11/2026).

La intuición del usuario: cuando en una misma liga y un mismo día ya ganaron
los locales (o los favoritos), el siguiente partido «no puede» salir igual
—la casa no dejaría que cualquiera gane yendo a todos los locales—, y ahí el
empate o la visita pagan. La Ley 5 del skill viejo (Tensión del Favorito) ya
se midió el 19/10 sobre favoritos (docs/DEUDA.md, punto 16) y no apareció;
esto la mide como la plantea el usuario: LOCAL, EMPATE y VISITA del partido
siguiente, y la apuesta concreta.

Unidad: el LIGA-DÍA (misma liga, mismo día en hora de Lima, 3+ partidos). Un
partido «ya terminó» si arrancó 2 h antes que el que se evalúa: solo lo que un
apostador sabía en el pitazo (sin fuga).

1. Sin cuotas (toda la historia): el resultado del siguiente según cómo vino el
   día, contra la tasa de su liga-temporada SIN ese día (la liga con mucha
   localía no se cuenta a sí misma).
2. Días extremos (todos los locales ganan / ninguno) contra una permutación de
   resultados dentro de la liga-temporada. Más extremos que la permutación =
   los días van en RACHA (lo contrario de una culebra); menos = equilibrio.
3. Con cuotas (sin margen): lo mismo contra la probabilidad del mercado, el
   favorito local y el visitante por separado, la combinada del día, y la
   apuesta de 1 u al EMPATE tras locales ganadores con la cuota REAL (con margen)
   contra el empate a ciegas.

Medido el 07/11/2026 (34.970 partidos de las ligas nacionales del padrón desde
2022; 1.221 con cuota en 324 liga-días desde julio): sin culebra. El empate del
siguiente no sube tras locales ganadores (+0,7 · −1,1 · −1,9 pts con 1 · 2 · 3+);
los días con todos los locales salen MÁS que la permutación (405 contra 376).
Pistas abiertas, con pocos casos, en docs/DEUDA.md (punto 24).

    python -m backend.backtest_culebra --api --desde 2022-01-01 --cache carpeta   # baja por la API (token de Cowork alcanza)
    python -m backend.backtest_culebra --cache carpeta                           # rehace con lo bajado
    python -m backend.backtest_culebra --cache carpeta --json salida.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import random
import time
import urllib.request
from collections import Counter, defaultdict

MIN_PARTIDOS_DIA = 3
TERMINADO_HORAS = 2      # un partido previo cuenta si arrancó al menos esto antes
LIMA = dt.timedelta(hours=-5)
PERMUTACIONES = 300
MIN_N = 20               # menos casos que esto: se dice «muy pocos», sin número

# Ligas nacionales del padrón (extractor.ligas_vivo() sin los internacionales):
# la jornada de una liga es la unidad de la ley; un martes de Champions no lo es.
INTERNACIONALES = {1, 2, 3, 11, 13, 848}


def ligas_nacionales_del_padron() -> set[int]:
    from backend.ingesta.extractor import ligas_vivo
    return set(ligas_vivo()) - INTERNACIONALES


# ── datos ────────────────────────────────────────────────────────────────────
def _hora(p: dict) -> dt.datetime:
    return dt.datetime.fromisoformat(p["fecha"].replace("Z", "+00:00"))


def resultado(p: dict) -> str:
    g, v = p["golesLocal"], p["golesVisitante"]
    return "1" if g > v else ("X" if g == v else "2")


def sin_margen(c: dict | None) -> dict | None:
    if not c or any(not c.get(s) for s in ("1", "X", "2")):
        return None
    inv = {s: 1 / c[s] for s in ("1", "X", "2")}
    tot = sum(inv.values())
    return {s: v / tot for s, v in inv.items()}


def liga_dias(partidos: list[dict]) -> dict[tuple, list[dict]]:
    """(liga, día de Lima) → partidos en orden de pitazo, solo con 3+; sin ids repetidos."""
    vistos, grupos = set(), defaultdict(list)
    for p in partidos:
        if p["id"] in vistos or p.get("golesLocal") is None:
            continue
        vistos.add(p["id"])
        grupos[(p["ligaId"], (_hora(p) + LIMA).date().isoformat())].append(p)
    return {k: sorted(v, key=_hora) for k, v in grupos.items() if len(v) >= MIN_PARTIDOS_DIA}


def _previos(dia: list[dict], j: int) -> list[dict]:
    t = _hora(dia[j]) - dt.timedelta(hours=TERMINADO_HORAS)
    return [q for q in dia[:j] if _hora(q) <= t]


def _linea(s: list[tuple[bool, float]]) -> dict:
    """observado vs esperado con IC 95 % (varianza de Bernoulli de lo esperado)."""
    n = len(s)
    if n < MIN_N:
        return {"n": n, "muyPocos": True}
    o = sum(y for y, _ in s) / n
    e = sum(p for _, p in s) / n
    ic = 1.96 * math.sqrt(sum(p * (1 - p) for _, p in s)) / n
    return {"n": n, "observado": round(o, 4), "esperado": round(e, 4),
            "dif": round(o - e, 4), "ic95": round(ic, 4)}


# ── 1 · sin cuotas ───────────────────────────────────────────────────────────
def _tasas_liga_temporada(dias: dict) -> dict:
    t = defaultdict(Counter)
    for v in dias.values():
        for p in v:
            t[(p["ligaId"], p["temporada"])][resultado(p)] += 1
    return t


def secuencial_sin_cuotas(dias: dict) -> dict:
    tasas = _tasas_liga_temporada(dias)
    tramos = (("1", 1, 1), ("2", 2, 2), ("3+", 3, 10**6))
    conds = {"todosLocal": lambda w, n: w == n, "ningunLocal": lambda w, n: w == 0}
    acum = defaultdict(list)
    for v in dias.values():
        for j, p in enumerate(v):
            prev = _previos(v, j)
            if not prev:
                continue
            c = tasas[(p["ligaId"], p["temporada"])].copy()
            for q in v:                       # la liga-temporada SIN este día
                if q["temporada"] == p["temporada"]:
                    c[resultado(q)] -= 1
            n = sum(c.values())
            if n <= 50:
                continue
            w = sum(resultado(q) == "1" for q in prev)
            for nt, lo, hi in tramos:
                if not lo <= len(prev) <= hi:
                    continue
                for nc, f in conds.items():
                    if f(w, len(prev)):
                        for r in ("1", "X", "2"):
                            acum[(nt, nc, r)].append((resultado(p) == r, c[r] / n))
    return {f"{nt}|{nc}|{r}": _linea(s) for (nt, nc, r), s in sorted(acum.items())}


# ── 2 · días extremos contra la permutación ──────────────────────────────────
def extremos(dias: dict, permutaciones: int = PERMUTACIONES, semilla: int = 7) -> dict:
    obs = {k: [resultado(p) == "1" for p in v] for k, v in dias.items()}

    def contar(m):
        return (sum(all(x) for x in m.values()), sum(not any(x) for x in m.values()))

    o = contar(obs)
    por_lt = defaultdict(list)
    for k, v in dias.items():
        for i, p in enumerate(v):
            por_lt[(p["ligaId"], p["temporada"])].append((k, i))
    rng = random.Random(semilla)
    sims = []
    for _ in range(permutaciones):
        m = {k: list(x) for k, x in obs.items()}
        for items in por_lt.values():
            rs = [obs[k][i] for k, i in items]
            rng.shuffle(rs)
            for (k, i), r in zip(items, rs):
                m[k][i] = r
        sims.append(contar(m))
    out = {"ligaDias": len(dias)}
    for idx, nombre in ((0, "todosLocales"), (1, "ningunLocal")):
        xs = [s[idx] for s in sims]
        mu = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / len(xs)) or 1e-9
        out[nombre] = {"observado": o[idx], "permutacion": round(mu, 1), "z": round((o[idx] - mu) / sd, 2)}
    por_n = defaultdict(lambda: [0, 0])
    for x in obs.values():
        n = min(len(x), 7)
        por_n[n][1] += 1
        por_n[n][0] += all(x)
    out["todosLocalesPorTamano"] = {("7+" if n == 7 else str(n)): {"dias": d, "todos": t}
                                    for n, (t, d) in sorted(por_n.items())}
    return out


# ── 3 · con cuotas ───────────────────────────────────────────────────────────
def con_cuotas(dias: dict) -> dict:
    gc = {}
    for k, v in dias.items():
        ps = [sin_margen(p.get("cuotas")) for p in v]
        if all(ps):
            gc[k] = list(zip(v, ps))
    fav = lambda q: max(q, key=q.get)  # noqa: E731
    out = {"ligaDias": len(gc), "partidos": sum(len(v) for v in gc.values())}

    def seq(cond, objetivo, kmin):
        s = []
        for v in gc.values():
            for j, (p, q) in enumerate(v):
                t = _hora(p) - dt.timedelta(hours=TERMINADO_HORAS)
                prev = [(a, b) for a, b in v[:j] if _hora(a) <= t]
                if len(prev) < kmin or not cond(prev):
                    continue
                sel = objetivo(q)
                if sel is not None:
                    s.append((resultado(p) == sel, q[sel]))
        return _linea(s)

    todos_loc = lambda prev: all(resultado(a) == "1" for a, _ in prev)  # noqa: E731
    todos_fav = lambda prev: all(resultado(a) == fav(b) for a, b in prev)  # noqa: E731
    for kmin in (1, 2):
        out[f"previos{kmin}+"] = {
            "localesGanaron→empate": seq(todos_loc, lambda q: "X", kmin),
            "noTodosLocales→empate": seq(lambda pr: not todos_loc(pr), lambda q: "X", kmin),
            "favoritosGanaron→empate": seq(todos_fav, lambda q: "X", kmin),
            "favoritosGanaron→favLocal": seq(todos_fav, lambda q: "1" if fav(q) == "1" else None, kmin),
            "favoritosGanaron→favVisita": seq(todos_fav, lambda q: "2" if fav(q) == "2" else None, kmin),
            "noTodosFav→favLocal": seq(lambda pr: not todos_fav(pr), lambda q: "1" if fav(q) == "1" else None, kmin),
            "noTodosFav→favVisita": seq(lambda pr: not todos_fav(pr), lambda q: "2" if fav(q) == "2" else None, kmin),
        }
    comb = {}
    for nombre, sel in (("locales", lambda q: "1"), ("favoritos", fav)):
        o = e = 0.0
        for v in gc.values():
            e += math.prod(q[sel(q)] for _, q in v)
            o += all(resultado(p) == sel(q) for p, q in v)
        comb[nombre] = {"dias": len(gc), "salio": int(o), "esperado": round(e, 1)}
    out["combinadaDelDia"] = comb

    def apuesta_empate(kmin):
        n = gan = emp = 0
        for v in gc.values():
            for j, (p, _) in enumerate(v):
                t = _hora(p) - dt.timedelta(hours=TERMINADO_HORAS)
                prev = [a for a, _ in v[:j] if _hora(a) <= t]
                if len(prev) < kmin or not all(resultado(a) == "1" for a in prev):
                    continue
                n += 1
                if resultado(p) == "X":
                    emp += 1
                    gan += p["cuotas"]["X"] - 1
                else:
                    gan -= 1
        return {"apuestas": n, "empates": emp, "ganancia": round(gan, 2), "roi": round(gan / n, 4) if n else None}

    ciegas = [p for v in gc.values() for p, _ in v]
    g = sum((p["cuotas"]["X"] - 1) if resultado(p) == "X" else -1 for p in ciegas)
    out["apuestaEmpate"] = {"tras1+Locales": apuesta_empate(1), "tras2+Locales": apuesta_empate(2),
                            "aCiegas": {"apuestas": len(ciegas), "roi": round(g / len(ciegas), 4) if ciegas else None}}
    return out


def analizar(partidos: list[dict], permutaciones: int = PERMUTACIONES) -> dict:
    dias = liga_dias(partidos)
    return {"partidos": len({p["id"] for p in partidos}), "ligaDias": len(dias),
            "sinCuotas": secuencial_sin_cuotas(dias), "extremos": extremos(dias, permutaciones),
            "conCuotas": con_cuotas(dias)}


# ── bajada por la API ────────────────────────────────────────────────────────
def _get(base: str, token: str, ruta: str):
    for intento in range(4):
        try:
            req = urllib.request.Request(base + ruta, headers={"Authorization": "Bearer " + token})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:  # red o 5xx pasajero: se reintenta y, al final, se avisa
            ultimo = e
            time.sleep(2 ** intento)
    print(f"  FALLO {ruta}: {ultimo}")
    return None


def bajar(desde: str, hasta: str, cache: str, cuotas_desde: str) -> None:
    from concurrent.futures import ThreadPoolExecutor
    base, token = os.environ["SAD_API_BASE"].rstrip("/"), os.environ.get("SAD_TOKEN_COWORK") or os.environ["SAD_API_TOKEN"]
    ligas = ligas_nacionales_del_padron()
    d0, d1 = dt.date.fromisoformat(desde), dt.date.fromisoformat(hasta)
    dias = [(d0 + dt.timedelta(i)).isoformat() for i in range((d1 - d0).days + 1)]

    def dia(d):
        xs = _get(base, token, f"/fixtures?fecha={d}&estado=finalizado&limit=500") or []
        return [x for x in xs if x["ligaId"] in ligas and x.get("golesLocal") is not None]

    with ThreadPoolExecutor(4) as ex:   # 4 a la vez: no apretar la RAM de Railway
        fx = [x for r in ex.map(dia, dias) for x in r]
    con_c = [x for x in fx if x["fecha"] >= cuotas_desde]

    def cuota(x):
        r = _get(base, token, f"/cuotas/{x['id']}") or []
        return x["id"], {c["seleccion"]: c["cuota"] for c in r if c["mercado"] == "1x2"}

    with ThreadPoolExecutor(4) as ex:
        cu = {i: c for i, c in ex.map(cuota, con_c) if len(c) == 3}
    for x in fx:
        x["cuotas"] = cu.get(x["id"])
    os.makedirs(cache, exist_ok=True)
    with open(os.path.join(cache, "partidos.json"), "w") as f:
        json.dump(fx, f)
    print(f"bajados {len(fx)} partidos, {len(cu)} con cuota 1X2 → {cache}/partidos.json")


# ── informe ──────────────────────────────────────────────────────────────────
def _fmt(nombre: str, d: dict) -> str:
    if d.get("muyPocos"):
        return f"  {nombre:40} n={d['n']:5}  (muy pocos)"
    return (f"  {nombre:40} n={d['n']:5}  salió {d['observado']:.3f}  esperado {d['esperado']:.3f}"
            f"  dif {d['dif']:+.3f} ± {d['ic95']:.3f}")


def informe(r: dict) -> None:
    print(f"Partidos {r['partidos']} · liga-días con {MIN_PARTIDOS_DIA}+ partidos: {r['ligaDias']}")
    print("\n1 · SIN CUOTAS: el siguiente, según cómo vino el día (esperado = su liga-temporada sin ese día)")
    nombres = {"1": "gana LOCAL", "X": "EMPATE", "2": "gana VISITA"}
    for clave, d in r["sinCuotas"].items():
        nt, nc, res = clave.split("|")
        print(_fmt(f"previos {nt}, {'todos' if nc == 'todosLocal' else 'ningún'} local → {nombres[res]}", d))
    e = r["extremos"]
    print("\n2 · DÍAS EXTREMOS contra la permutación (más = racha, menos = equilibrio)")
    for k in ("todosLocales", "ningunLocal"):
        print(f"  {k:14} observado {e[k]['observado']}  permutación {e[k]['permutacion']}  z {e[k]['z']:+.2f}")
    for n, d in e["todosLocalesPorTamano"].items():
        print(f"  días de {n}: todos los locales ganan en {d['todos']} de {d['dias']}")
    c = r["conCuotas"]
    print(f"\n3 · CON CUOTAS ({c['ligaDias']} liga-días, {c['partidos']} partidos)")
    for k in ("previos1+", "previos2+"):
        print(f" {k}")
        for nombre, d in c[k].items():
            print(_fmt(nombre, d))
    for k, d in c["combinadaDelDia"].items():
        print(f"  combinada de todos los {k}: salió {d['salio']} de {d['dias']} días, esperado {d['esperado']}")
    for k, d in c["apuestaEmpate"].items():
        roi = "—" if d["roi"] is None else f"{d['roi']:+.1%}"
        print(f"  1 u al EMPATE {k}: {d['apuestas']} apuestas, ROI {roi}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api", action="store_true", help="bajar por la API (SAD_API_BASE y token en el entorno)")
    ap.add_argument("--desde", default="2022-01-01")
    ap.add_argument("--hasta", default=dt.date.today().isoformat())
    ap.add_argument("--cuotas-desde", default="2026-07-01", help="antes no hay cuotas 1X2 guardadas")
    ap.add_argument("--cache", required=True, help="carpeta de partidos.json")
    ap.add_argument("--json", help="guardar el resultado")
    a = ap.parse_args()
    if a.api:
        bajar(a.desde, a.hasta, a.cache, a.cuotas_desde)
    with open(os.path.join(a.cache, "partidos.json")) as f:
        r = analizar(json.load(f))
    informe(r)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
