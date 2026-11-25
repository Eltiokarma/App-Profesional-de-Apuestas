"""EL SEMÁFORO CALIBRADO POR RAZONES, hacia atrás (25/11/2026).

El usuario, tras Manchester City (1 victoria en 7, seis veces en verde): «el
analista dice semáforo en amarillo por tal razón, en rojo por tal razón, en
verde por tal razón… viendo cuál razón se repite más y dándole más peso, a eso
me refiero con calibrar. Eso incluye hacer que el verde no diga verde cuando
perdimos». Y: «nada se mide hacia adelante esta vez, solo hacia atrás».

Qué hace, con los partes ya cerrados (`--desde-json`, lo que devuelve el GET
del parte más su fixture):

1. Las RAZONES de cada parte (`semaforo.razones`, lo que se sabía antes del
   pitazo; el `veredicto` no se lee) y el color de las espinas (`del_parte` sin
   enriquecer).
2. El PESO de cada razón, aprendido SOLO con los verdes: log(frecuencia en los
   verdes que perdimos / en los que ganamos), con suavizado de medio caso, para
   razones con 15+ verdes, en menos del 80 % de ellos y con |peso| ≥ 0,25.
3. El CORTE: el puntaje que deja en amarillo el cuarto de los verdes con más
   razones en contra.
4. La COMPROBACIÓN: pesos y corte aprendidos con el 60 % más viejo; el
   semáforo completo (verde → amarillo con puntaje alto, amarillo → verde con
   puntaje bajo, rojo se queda) medido en el 40 % más nuevo, contra el de hoy.
   Y los amarillos y rojos con los pesos de los verdes (que no los vieron).

Se mide como pide el usuario: cuánto gana el elegido en cada color, qué parte
de los partidos marca y qué parte de las derrotas tiene cada color; al lado,
lo que decíamos (lo publicado), para ver que no sea solo el porcentaje.
Copas nacionales fuera. El elegido empate no se calibra.

    python -m backend.backtest_semaforo_razones --desde-json a.json [b.json …]
    python -m backend.backtest_semaforo_razones --desde-json a.json --tabla   # los pesos para semaforo.py
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import sys

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend.analisis import semaforo as sem  # noqa: E402

MIN_N = 15
MIN_PESO = 0.25
MAX_PREV = 0.80
CUANTIL_CORTE = 0.75
CUANTIL_ROJO = 0.90
FRAC = 0.6
COLOR = {"confirma": "verde", "duda": "amarillo", "noApostar": "rojo", "sinDato": "sin dato"}


def filas(datos: dict, copa=None) -> list[dict]:
    """{fixture: {parte, fx}} → una fila por parte cerrado con elegido local o visita."""
    out = []
    for fid, v in datos.items():
        p, fx = (v or {}).get("parte"), (v or {}).get("fx")
        if not isinstance(p, dict) or not isinstance(fx, dict) or fx.get("golesLocal") is None:
            continue
        if copa and copa(fx):
            continue
        base = sem.del_parte(p)
        e = base.get("elegido")
        if e not in ("local", "visita"):
            continue
        p1 = sem._pct((p.get("pronostico") or {}).get("probabilidades") or {})
        gl, gv = int(fx["golesLocal"]), int(fx["golesVisitante"])
        out.append({"fixtureId": int(fid), "fecha": str(fx.get("fecha") or "")[:10], "elegido": e,
                    "pe": p1[e] if p1 else None, "gana": gl > gv if e == "local" else gv > gl,
                    "base": base["estado"], "razones": sem.razones(p, e),
                    "partido": f"{(fx.get('local') or {}).get('nombre')} {gl}-{gv} {(fx.get('visitante') or {}).get('nombre')}"})
    out.sort(key=lambda r: (r["fecha"], r["fixtureId"]))
    return out


def aprender(verdes: list[dict], min_n: int = MIN_N) -> dict[str, float]:
    perd = [r for r in verdes if not r["gana"]]
    gan = [r for r in verdes if r["gana"]]
    if not perd or not gan:
        return {}
    c = collections.Counter(x for r in verdes for x in r["razones"])
    pesos = {}
    for x, n in c.items():
        if n < min_n or n > MAX_PREV * len(verdes):
            continue
        fp = (sum(x in r["razones"] for r in perd) + 0.5) / (len(perd) + 1)
        fg = (sum(x in r["razones"] for r in gan) + 0.5) / (len(gan) + 1)
        w = math.log(fp / fg)
        if abs(w) >= MIN_PESO:
            pesos[x] = round(w, 3)
    return dict(sorted(pesos.items(), key=lambda kv: -kv[1]))


def puntaje(r: dict, pesos: dict) -> float:
    return sum(pesos.get(x, 0.0) for x in r["razones"])


def corte_de(verdes: list[dict], pesos: dict, cuantil: float = CUANTIL_CORTE) -> float:
    ps = sorted(puntaje(r, pesos) for r in verdes)
    if not ps or not pesos:
        return 99.0          # sin pesos no hay razón que mueva un color
    return round(ps[int(len(ps) * cuantil)], 3)


def calibrado(r: dict, pesos: dict, corte: float, corte_rojo: float = 99.0) -> str:
    return sem.calibrar({"estado": r["base"], "elegido": r["elegido"]}, r["razones"], pesos, corte, corte_rojo)["estado"]


def resumen(g: list[dict], color) -> dict:
    perd = sum(not r["gana"] for r in g) or 1
    out = {}
    for est, nombre in COLOR.items():
        h = [r for r in g if color(r) == est]
        if not h:
            continue
        k = sum(r["gana"] for r in h)
        dichos = [r["pe"] for r in h if r["pe"] is not None]
        out[nombre] = {"n": len(h), "gana": k, "tasa": round(k / len(h), 4),
                       "decíamos": round(sum(dichos) / len(dichos) / 100, 4) if dichos else None,
                       "marca": round(len(h) / len(g), 4),
                       "derrotas": round(sum(not r["gana"] for r in h) / perd, 4)}
    return out


def evaluar(fs: list[dict], frac: float = FRAC) -> dict:
    if len(fs) < 50:
        return {"partes": len(fs), "sinDato": "menos de 50 partes"}
    corte_f = fs[int(len(fs) * frac)]["fecha"]
    ent = [r for r in fs if r["fecha"] < corte_f]
    pru = [r for r in fs if r["fecha"] >= corte_f]
    pesos = aprender([r for r in ent if r["base"] == "confirma"])
    corte = corte_de([r for r in ent if r["base"] == "confirma"], pesos)
    corte_rojo = corte_de([r for r in ent if r["base"] == "confirma"], pesos, CUANTIL_ROJO)
    out = {"partes": len(fs), "desde": fs[0]["fecha"], "hasta": fs[-1]["fecha"], "corteFecha": corte_f,
           "aprendizaje": len(ent), "comprobacion": len(pru), "pesosAprendidos": len(pesos), "corte": corte,
           "corteRojo": corte_rojo}
    for nombre, g in (("aprendizaje", ent), ("comprobacion", pru)):
        out[nombre + "Tabla"] = {"hoy": resumen(g, lambda r: r["base"]),
                                 "calibrado": resumen(g, lambda r: calibrado(r, pesos, corte, corte_rojo))}
    # todas las combinaciones: color de las espinas × tramo del puntaje, en las dos etapas
    def tramo(p):
        return ("sin razones en contra" if p <= 0 else "bajo el corte" if p < corte
                else "sobre el corte" if p < corte_rojo else "muy alto")
    comb = {}
    for est, nombre in COLOR.items():
        for t in ("sin razones en contra", "bajo el corte", "sobre el corte", "muy alto"):
            fila = {}
            for et, g in (("aprendizaje", ent), ("comprobacion", pru)):
                h = [r for r in g if r["base"] == est and tramo(puntaje(r, pesos)) == t]
                if h:
                    fila[et] = {"n": len(h), "tasa": round(sum(r["gana"] for r in h) / len(h), 4),
                                "decíamos": round(sum(r["pe"] for r in h if r["pe"] is not None) / len(h) / 100, 4)}
            if fila:
                comb[f"{nombre} · {t}"] = fila
    out["combinaciones"] = comb
    # los amarillos y rojos de TODO el período con los pesos de los verdes del aprendizaje
    for est, nombre in (("duda", "amarillos"), ("noApostar", "rojos")):
        g = [r for r in fs if r["base"] == est]
        out[nombre + "ConPesosDelVerde"] = {
            "conRazones": resumen([r for r in g if puntaje(r, pesos) >= corte], lambda r: r["base"]),
            "sinRazones": resumen([r for r in g if puntaje(r, pesos) < corte], lambda r: r["base"])}
    return out


def tabla(fs: list[dict]) -> str:
    """Los pesos y el corte con TODOS los verdes, listos para pegar en semaforo.py."""
    v = [r for r in fs if r["base"] == "confirma"]
    pesos = aprender(v)
    corte = corte_de(v, pesos)
    corte_rojo = corte_de(v, pesos, CUANTIL_ROJO)
    lineas = [f'CALIBRACION = {{"fecha": "{fs[-1]["fecha"]}", "partes": {len(fs)}, "verdes": {len(v)}, '
              f'"desde": "{fs[0]["fecha"]}", "hasta": "{fs[-1]["fecha"]}"}}',
              f"CORTE = {corte}", f"CORTE_ROJO = {corte_rojo}", "PESOS: dict[str, float] = {"]
    lineas += [f'    {json.dumps(k, ensure_ascii=False)}: {w},' for k, w in pesos.items()]
    lineas.append("}")
    return "\n".join(lineas)


def _copa_por_nombre():
    from backend.analisis.escala import es_copa_nacional
    try:
        from backend.ingesta.extractor import LIGAS_INTERNACIONALES
        inter = set(LIGAS_INTERNACIONALES)
    except Exception:  # noqa: BLE001 — sin el extractor, el nombre basta para las internacionales
        inter = set()
    return lambda fx: es_copa_nacional(fx.get("ligaId"), fx.get("liga") or "", inter)


def _imprimir(r: dict) -> None:
    if "sinDato" in r:
        print(r)
        return
    print(f"\n{r['partes']} partes ({r['desde']} → {r['hasta']}) · aprendizaje {r['aprendizaje']} (hasta el "
          f"{r['corteFecha']}) · comprobación {r['comprobacion']} · {r['pesosAprendidos']} razones con peso · "
          f"corte {r['corte']} · corte del rojo {r['corteRojo']}")

    def linea(d):
        return (f"gana {d['gana']}/{d['n']} = {100 * d['tasa']:5.1f} % · decíamos "
                f"{'—' if d['decíamos'] is None else f'{100 * d['decíamos']:.1f}'} · marca {100 * d['marca']:3.0f} % · "
                f"tiene {100 * d['derrotas']:3.0f} % de las derrotas")
    for et in ("aprendizaje", "comprobacion"):
        print(f"\n{et.upper()}")
        for cual in ("hoy", "calibrado"):
            print(f"  {cual}")
            for c, d in r[et + "Tabla"][cual].items():
                print(f"    {c:9s} {linea(d)}")
    print("\nTODAS LAS COMBINACIONES (color de las espinas · tramo de razones en contra)")
    for k, f in r["combinaciones"].items():
        partes = [f"{et} {d['n']:3d} gana {100 * d['tasa']:5.1f} % (decíamos {100 * d['decíamos']:.1f})"
                  for et, d in f.items()]
        print(f"  {k:38s} " + " | ".join(partes))
    for nombre in ("amarillos", "rojos"):
        print(f"\n{nombre.upper()} con los pesos de los verdes (no los vieron)")
        for k, t in r[nombre + "ConPesosDelVerde"].items():
            for c, d in t.items():
                print(f"  {k:11s} {linea(d)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="El semáforo calibrado por razones, hacia atrás")
    ap.add_argument("--desde-json", nargs="+", required=True, help="partes bajados ({fixture: {parte, fx}})")
    ap.add_argument("--tabla", action="store_true", help="imprimir los pesos y el corte con TODOS los verdes")
    ap.add_argument("--json", help="guardar el resumen")
    a = ap.parse_args(argv)
    datos = {}
    for ruta in a.desde_json:
        datos.update(json.load(open(ruta)))
    fs = filas(datos, _copa_por_nombre())
    if a.tabla:
        print(tabla(fs))
        return 0
    r = evaluar(fs)
    _imprimir(r)
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
