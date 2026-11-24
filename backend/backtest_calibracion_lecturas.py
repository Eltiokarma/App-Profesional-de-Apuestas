"""¿CALIBRAR LAS DOS LECTURAS CONTRA LOS RESULTADOS MEJORA EL NÚMERO? (24/11/2026)

El usuario: «para calibrar esos porcentajes se tiene que salir de lo que dice
el analista y calibrar con los resultados; incluso podemos tomar más
resultados pasados». Este backtest dice si la curva de
`backend/analisis/calibracion_lecturas.py` acerca lo dicho a lo que pasa en
partidos que NO vio, y con qué previo.

Las lecturas salen de los partes cerrados desde el 28/10/2026:
- `publicado`: el 1X2 publicado del parte (local → «gana el local», visita →
  «gana el visitante»); es casi la casa (las reglas de anclaje lo pegan a la
  cuota), pero son muchos partidos;
- `ciego`: el ciego sellado antes de ver la cuota (desde el 22/11; pocos).

Tres pruebas, sin mirar el futuro:
1. corte temporal 80/20: la curva aprende del 80 % más viejo y se mide en el
   20 % más nuevo, por previo (PRIOR_SD);
2. semana a semana: cada semana se calibra con TODAS las anteriores, que es
   lo que haría la rutina de los lunes;
3. de un origen al otro: la curva del publicado aplicada al ciego (¿sirven
   los resultados pasados para calibrar la lectura sin la casa?).

Se mide en pérdida logarítmica y Brier binarios por lado (más bajo es mejor) y
en la tabla por tramo (lo dicho y lo calibrado contra lo que pasó). Se juzga
por calibración, no por la casa: no hay cuota en la cuenta.

    python -m backend.backtest_calibracion_lecturas --desde-json partes.json
    python -m backend.backtest_calibracion_lecturas --api [--guardar partes.json]
    python -m backend.backtest_calibracion_lecturas --desde-json partes.json --json

`--api` baja los partes con `SAD_API_BASE` y `SAD_TOKEN_COWORK` (como
`backend/contacto.py`). 0 tokens, 0 cuota de API-Football.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend.analisis import calibracion_lecturas as cal  # noqa: E402

PREVIOS = (0.25, 0.5, 1.0, 2.0)
TRAMOS = ((0, 20, "0-19"), (20, 40, "20-39"), (40, 60, "40-59"), (60, 80, "60-79"), (80, 101, "80+"))


def filas_de(apuestas: list[dict], origen: str) -> list[dict]:
    """Las apuestas armadas (`contacto.armar`) → filas {pitazo, ganaLocal,
    ganaVisita, resultado} del origen pedido, en orden de pitazo."""
    out = []
    for a in apuestas:
        if a.get("resultado") not in ("local", "empate", "visita"):
            continue
        if origen == "publicado":
            p = a.get("probabilidades") or {}
            tot = sum(float(p.get(k) or 0) for k in ("local", "empate", "visita")) or 100.0
            gl, gv = 100 * float(p.get("local") or 0) / tot, 100 * float(p.get("visita") or 0) / tot
        else:
            c = a.get("ciego")
            if not c:
                continue
            gl = c.get("ganaLocal") if c.get("ganaLocal") is not None else c.get("local")
            gv = c.get("ganaVisita") if c.get("ganaVisita") is not None else c.get("visita")
        out.append({"fixtureId": a.get("fixtureId"), "pitazo": a["pitazo"], "ganaLocal": gl,
                    "ganaVisita": gv, "resultado": a["resultado"]})
    return sorted(out, key=lambda f: f["pitazo"])


def _medir(pts: dict, coefs: dict | None) -> dict:
    out = {}
    for lado in cal.LADOS:
        p = pts[lado]
        out[lado] = {"n": len(p), "logLoss": _r(cal.log_loss(p, (coefs or {}).get(lado))),
                     "brier": _r(cal.brier(p, (coefs or {}).get(lado)))}
    return out


def _r(x, d=4):
    return None if x is None else round(x, d)


def corte(filas: list[dict], frac: float = 0.8) -> dict:
    """Aprende del `frac` más viejo y mide en el resto, por previo."""
    k = int(len(filas) * frac)
    tren, prueba = filas[:k], filas[k:]
    pts = cal.puntos_de(prueba)
    out = {"entrena": len(tren), "prueba": len(prueba),
           "desdePrueba": prueba[0]["pitazo"] if prueba else None,
           "dicho": _medir(pts, None), "porPrevio": {}}
    for sd in PREVIOS:
        coefs = cal.ajuste_de(tren, sd)
        out["porPrevio"][str(sd)] = {"curvas": coefs, **_medir(pts, coefs)}
    return out


def _semana(pitazo: str) -> str:
    d = datetime.fromisoformat(pitazo.replace(" ", "T")[:19])
    y, w, _ = d.isocalendar()
    return f"{y}-S{w:02d}"


def semanal(filas: list[dict], sd: float = cal.PRIOR_SD) -> dict:
    """Cada semana calibrada con todas las anteriores (la rutina de los lunes)."""
    semanas = sorted({_semana(f["pitazo"]) for f in filas})
    dicho = {lado: [] for lado in cal.LADOS}
    calib = {lado: [] for lado in cal.LADOS}
    detalle = []
    for s in semanas[1:]:
        antes = [f for f in filas if _semana(f["pitazo"]) < s]
        esta = [f for f in filas if _semana(f["pitazo"]) == s]
        coefs = cal.ajuste_de(antes, sd)
        pts = cal.puntos_de(esta)
        for lado in cal.LADOS:
            dicho[lado] += [(p, y) for p, y in pts[lado]]
            calib[lado] += [(cal.aplicar(coefs[lado], p), y) for p, y in pts[lado]]
        detalle.append({"semana": s, "partidos": len(esta), "conPartidosAntes": len(antes),
                        "b": {lado: coefs[lado]["b"] for lado in cal.LADOS}})
    return {"previo": sd, "semanas": detalle,
            "dicho": {lado: {"n": len(dicho[lado]), "logLoss": _r(cal.log_loss(dicho[lado])),
                             "brier": _r(cal.brier(dicho[lado]))} for lado in cal.LADOS},
            "calibrado": {lado: {"n": len(calib[lado]), "logLoss": _r(cal.log_loss(calib[lado])),
                                 "brier": _r(cal.brier(calib[lado]))} for lado in cal.LADOS}}


def tabla(filas: list[dict], coefs: dict | None) -> dict:
    """Por lado y tramo de lo dicho: cuántos, lo dicho, lo calibrado y lo que pasó."""
    out = {}
    pts = cal.puntos_de(filas)
    for lado in cal.LADOS:
        filas_t = []
        for lo, hi, t in TRAMOS:
            g = [(p, y) for p, y in pts[lado] if lo <= p < hi]
            if not g:
                continue
            filas_t.append({"tramo": t, "n": len(g), "dijo": round(sum(p for p, _ in g) / len(g), 1),
                            "calibrado": round(sum(cal.aplicar((coefs or {}).get(lado), p) for p, _ in g) / len(g), 1),
                            "paso": round(100 * sum(1 for _, y in g if y) / len(g), 1)})
        out[lado] = filas_t
    return out


def correr(apuestas: list[dict]) -> dict:
    pub = filas_de(apuestas, "publicado")
    cie = filas_de(apuestas, "ciego")
    out = {"partidos": {"publicado": len(pub), "ciego": len(cie)}}
    if pub:
        out["publicado"] = {"corte": corte(pub), "semanal": semanal(pub),
                            "curvas": cal.ajuste_de(pub), "tabla": tabla(pub, cal.ajuste_de(pub))}
    if cie:
        curvas_c = cal.ajuste_de(cie)
        out["ciego"] = {"curvas": curvas_c, "tabla": tabla(cie, curvas_c),
                        "dicho": _medir(cal.puntos_de(cie), None)}
        if pub:
            # ¿la curva del publicado sirve para el ciego? (solo partidos del publicado ANTES del ciego)
            primero = cie[0]["pitazo"]
            antes = [f for f in pub if f["pitazo"] < primero]
            coefs = cal.ajuste_de(antes)
            out["ciego"]["conCurvaDelPublicado"] = {"entrenaCon": len(antes), "curvas": coefs,
                                                    **_medir(cal.puntos_de(cie), coefs)}
    return out


def informe(r: dict) -> str:
    L = [f"Calibración de las dos lecturas · publicado {r['partidos']['publicado']} partidos · "
         f"ciego {r['partidos']['ciego']}"]

    def linea(nombre, m):
        return (f"    {nombre}: " + " · ".join(
            f"{lado} logLoss {m[lado]['logLoss']} Brier {m[lado]['brier']} (n {m[lado]['n']})"
            for lado in cal.LADOS))
    p = r.get("publicado")
    if p:
        c = p["corte"]
        L.append(f"  1) corte temporal: aprende de {c['entrena']}, mide en {c['prueba']} (desde {c['desdePrueba']})")
        L.append(linea("dicho     ", c["dicho"]))
        for sd, m in c["porPrevio"].items():
            L.append(linea(f"previo {sd:<4}", m) + f" · b local {m['curvas']['local']['b']} visita "
                     f"{m['curvas']['visita']['b']}")
        s = p["semanal"]
        L.append(f"  2) semana a semana (previo {s['previo']}, {len(s['semanas'])} semanas)")
        L.append(linea("dicho     ", s["dicho"]))
        L.append(linea("calibrado ", s["calibrado"]))
        L.append("  curva con todo el publicado: " + " · ".join(
            f"{lado}: {cal.lectura(p['curvas'][lado])}" for lado in cal.LADOS))
        for lado in cal.LADOS:
            L.append(f"  tabla {lado} (dijo → calibrado → pasó):")
            for t in p["tabla"][lado]:
                L.append(f"    {t['tramo']}: {t['n']} · {t['dijo']} → {t['calibrado']} → {t['paso']}")
    cg = r.get("ciego")
    if cg:
        L.append("  3) ciego")
        L.append(linea("dicho     ", cg["dicho"]))
        if cg.get("conCurvaDelPublicado"):
            m = cg["conCurvaDelPublicado"]
            L.append(linea(f"curva del publicado ({m['entrenaCon']})", m))
        L.append("  curva propia del ciego: " + " · ".join(
            f"{lado}: {cal.lectura(cg['curvas'][lado])}" for lado in cal.LADOS))
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--desde-json", help="partes bajados ({fixtureId: {parte, fx, cuotas}})")
    ap.add_argument("--api", action="store_true", help="bajarlos con SAD_API_BASE y SAD_TOKEN_COWORK")
    ap.add_argument("--guardar", help="con --api, dónde guardar lo bajado")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    from backend import contacto
    if a.desde_json:
        with open(a.desde_json) as fh:
            datos = json.load(fh)
    elif a.api:
        datos = contacto.bajar(os.environ["SAD_API_BASE"], os.environ["SAD_TOKEN_COWORK"])
        if a.guardar:
            with open(a.guardar, "w") as fh:
                json.dump({str(k): v for k, v in datos.items()}, fh)
    else:
        ap.error("falta --desde-json o --api")
    apuestas, _ = contacto.armar(datos)
    r = correr(apuestas)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else informe(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
