"""NBA · la K de PUNTOS: con la dirección elegida, ¿qué dicen los puntos? (docs/NBA_FASE0.md §10)

Pedido del usuario (12/11/2026): «medir la K de goles y combinarla en el
análisis por diferencia de puntos. Si ya elegimos bien la dirección, podemos
ver lo de los puntos que anota el equipo». Las familias «anota» / «recibe»
del motor (backend.nba.motor.FAMILIAS_PUNTOS): anotar o recibir POR ENCIMA de
su media de los 20 anteriores, con su K y su reventón a cero.

  1 · ¿La burbuja de puntos sigue? (sin cuotas): el que viene anotando de más,
      ¿vuelve a anotar de más? Por largo de racha, contra la tasa de todos.
  (dos VARAS: «propia» = la media de 20 del equipo; «casa» = lo que la casa
   esperaba de ese equipo en ese partido, (total ∓ hándicap)/2)
  2 · HÁNDICAP con la dirección ya elegida: el elegido es el favorito de la casa
      sin la alerta DESCONFIAR (el método, §9.1). ¿Cubre más o menos según el
      cruce de puntos? ataque = el elegido viene anotando de más + el rival
      viene recibiendo de más; defensa = al revés. balance = ataque − defensa.
  3 · MÁS/MENOS del partido: presión = cuántas de las 4 burbujas de puntos
      (anota y recibe de cada lado) están abiertas.

Dos períodos (2016-17 → 2022-23 y 2023-24 → hoy): una señal tiene que salir
en los DOS para tomarse en serio (se mira muchos cortes a la vez). Cuotas:
la mediana de cierre de ESPN, como en §9.

    python -m backend.nba.puntos          # → nba_data/puntos.txt y .json
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from statistics import median

from backend.analisis.simulacion import _RIESGOS_ALTOS
from backend.nba import burbujas, descarga, motor
from backend.nba.fase0 import consenso, decimal

ESCALA_G = 5.0
# las dos varas (usuario, 12/11/2026: «la 1 más la 3»): contra su propia media
# de 20 y contra lo que la casa esperaba de ese equipo en ese partido
VARAS = {"propia": ("anota", "recibe"), "casa": ("anotaCasa", "recibeCasa")}
PERIODOS = (("2016-17 → 2022-23", 2017, 2023), ("2023-24 → hoy", 2024, 9999))


def totales(filas: list[dict]) -> dict | None:
    """La línea de más/menos: mediana entre casas (sin vivo ni apertura) y sus cuotas."""
    filas = [f for f in filas if not any(x in (f.get("casa") or "").lower() for x in ("live", "opening"))]
    ou = [f["overUnder"] for f in filas if f.get("overUnder")]
    if not ou:
        return None
    ov = [decimal(f.get("overCuota")) for f in filas if decimal(f.get("overCuota"))]
    un = [decimal(f.get("underCuota")) for f in filas if decimal(f.get("underCuota"))]
    return {"linea": median(ou), "decOver": median(ov) if ov else 1.909, "decUnder": median(un) if un else 1.909}


def _tramo(n: int) -> str:
    return "1" if n == 1 else "2" if n == 2 else "3" if n == 3 else "4-5" if n <= 5 else "6+"


def _cuenta() -> list:
    return [0, 0, 0.0, 0.0]          # n, aciertos, ganancia plana, suma de 1/cuota


def _suma(x, dec, gano):
    x[0] += 1
    x[1] += gano
    x[2] += (dec - 1) if gano else -1
    x[3] += 1 / dec


def _fmt(x) -> dict:
    return {"n": x[0], "acierto": round(x[1] / x[0], 4) if x[0] else None,
            "pide": round(x[3] / x[0], 4) if x[0] else None, "roi": round(x[2] / x[0], 4) if x[0] else None}


def linea_puntos(ps: list[dict], cu: dict) -> dict:
    """{id: (esperados del local, de la visita)} según la casa: con el total y el
    hándicap del local (negativo = local favorito), local = (total − hándicap)/2."""
    out = {}
    for p in ps:
        c, t = consenso(cu.get(p["id"], [])), totales(cu.get(p["id"], []))
        if c and t and c["spreadLocal"] is not None:
            out[p["id"]] = ((t["linea"] - c["spreadLocal"]) / 2, (t["linea"] + c["spreadLocal"]) / 2)
    return out


def correr() -> dict:
    ps = descarga.cargar_partidos()
    cu = descarga.cargar_cuotas()
    lp = linea_puntos(ps, cu)
    prev = motor.construir(ps, escala_g=ESCALA_G, linea_puntos=lp)
    cont = defaultdict(lambda: [0, 0])          # (periodo, familia, tramo) → [n, siguió]
    base = defaultdict(lambda: [0, 0])          # (periodo, familia) → [n, por encima]
    hand = defaultdict(_cuenta)                 # (periodo, balance) → cuenta
    tot = defaultdict(_cuenta)                  # (periodo, presión, lado) → cuenta
    ext = defaultdict(lambda: [0, 0])          # (periodo, familia, estado) → [n, siguió]
    ext_tot = defaultdict(lambda: [0, 0])      # (periodo, clave) → [n, salió el más]
    sin_ou = 0
    for p in ps:
        per = next((n for n, a, b in PERIODOS if a <= p["temporada"] <= b), None)
        if per is None:
            continue
        f = prev[p["id"]]
        pts = {"local": (p["ptsLocal"], p["ptsVisita"]), "visita": (p["ptsVisita"], p["ptsLocal"])}
        # 1 · ¿la burbuja de puntos sigue?
        esp = lp.get(p["id"])
        for lado in ("local", "visita"):
            v = f[lado]["puntos"]
            pf, pa = pts[lado]
            refs = []
            if v["mediaAnota"] is not None:
                refs += [("anota", pf, v["mediaAnota"]), ("recibe", pa, v["mediaRecibe"])]
            if esp is not None:
                e_pf, e_pa = esp if lado == "local" else (esp[1], esp[0])
                refs += [("anotaCasa", pf, e_pf), ("recibeCasa", pa, e_pa)]
            for fam, valor, media in refs:
                encima = valor > media
                base[(per, fam)][0] += 1
                base[(per, fam)][1] += encima
                if v[fam]["abierta"]:
                    c = cont[(per, fam, _tramo(v[fam]["racha"]))]
                    c[0] += 1
                    c[1] += encima
                    if v[fam]["estado"]:
                        e = ext[(per, fam, v[fam]["estado"])]
                        e[0] += 1
                        e[1] += encima
                    if v[fam]["recordReciente"]:
                        e = ext[(per, fam, "récord reciente")]
                        e[0] += 1
                        e[1] += encima
        t0 = totales(cu.get(p["id"], []))
        if t0 is not None and p["ptsLocal"] + p["ptsVisita"] != t0["linea"]:
            subio = 0
            for lado in ("local", "visita"):
                for fam in ("anotaCasa", "recibeCasa"):
                    subio += f[lado]["puntos"][fam]["estado"] in ("extremo", "cerca")
            for k in ("todos", f"{min(subio, 2)}{'+' if subio >= 2 else ''} en extremo/cerca"):
                x = ext_tot[(per, k)]
                x[0] += 1
                x[1] += p["ptsLocal"] + p["ptsVisita"] > t0["linea"]
        c = consenso(cu.get(p["id"], []))
        if not c or c["pLocal"] in (None, 0.5):
            continue
        # el elegido: el favorito de la casa sin la alerta DESCONFIAR (§9.1)
        el = "local" if c["pLocal"] > 0.5 else "visita"
        ri = "visita" if el == "local" else "local"
        vic = f[el]["familias"]["victorias"]
        r = burbujas.riesgo(vic) if vic["signo"] else None
        if vic["signo"] and vic["racha"] == 1 and r and r["nivel"] in _RIESGOS_ALTOS:
            continue
        pe, pr = f[el]["puntos"], f[ri]["puntos"]
        if pe["mediaAnota"] is None or pr["mediaAnota"] is None:
            continue
        # 2 · hándicap del elegido, con cada vara
        if c["spreadLocal"] is not None:
            linea_el = c["spreadLocal"] if el == "local" else -c["spreadLocal"]
            margen = pts[el][0] - pts[el][1]
            if margen + linea_el != 0:
                dec = c["decSpreadLocal"] if el == "local" else c["decSpreadVisita"]
                _suma(hand[(per, "todos")], dec, margen + linea_el > 0)
                for vara, (fa, fr) in VARAS.items():
                    ataque = pe[fa]["abierta"] + pr[fr]["abierta"]
                    defensa = pe[fr]["abierta"] + pr[fa]["abierta"]
                    _suma(hand[(per, f"{vara} · balance {ataque - defensa:+d}")], dec, margen + linea_el > 0)
        # 3 · más/menos
        t = totales(cu.get(p["id"], []))
        if t is None:
            sin_ou += 1
            continue
        total = p["ptsLocal"] + p["ptsVisita"]
        if total == t["linea"]:
            continue
        claves = ["todos"]
        for vara, (fa, fr) in VARAS.items():
            presion = pe[fa]["abierta"] + pe[fr]["abierta"] + pr[fa]["abierta"] + pr[fr]["abierta"]
            claves.append(f"{vara} · presión {presion}")
        for k in claves:
            _suma(tot[(per, k, "más")], t["decOver"], total > t["linea"])
            _suma(tot[(per, k, "menos")], t["decUnder"], total < t["linea"])
    out = {"periodos": [n for n, _, _ in PERIODOS], "sinLineaDePuntos": sin_ou, "continuacion": {}, "handicap": {}, "totales": {}}
    for per, _, _ in PERIODOS:
        out["continuacion"][per] = {fam: {"base": round(base[(per, fam)][1] / base[(per, fam)][0], 4) if base[(per, fam)][0] else None,
                                          "porRacha": {t: {"n": cont[(per, fam, t)][0],
                                                           "sigue": round(cont[(per, fam, t)][1] / cont[(per, fam, t)][0], 4)
                                                           if cont[(per, fam, t)][0] else None}
                                                       for t in ("1", "2", "3", "4-5", "6+")}}
                                    for fam in (*motor.FAMILIAS_PUNTOS, *motor.FAMILIAS_CASA)}
        out.setdefault("extremo", {})[per] = {
            fam: {est: {"n": ext[(per, fam, est)][0],
                        "sigue": round(ext[(per, fam, est)][1] / ext[(per, fam, est)][0], 4) if ext[(per, fam, est)][0] else None}
                  for est in ("rango", "cerca", "extremo", "récord reciente")}
            for fam in (*motor.FAMILIAS_PUNTOS, *motor.FAMILIAS_CASA)}
        out.setdefault("extremoTotales", {})[per] = {
            k: {"n": v[0], "mas": round(v[1] / v[0], 4) if v[0] else None} for (pp, k), v in sorted(ext_tot.items()) if pp == per}
        out["handicap"][per] = {k: _fmt(v) for (pp, k), v in sorted(hand.items()) if pp == per}
        out["totales"][per] = {f"{k} · {lado}": _fmt(v) for (pp, k, lado), v in sorted(tot.items()) if pp == per}
    return out


def texto(r: dict) -> str:
    L = ["NBA · la K de PUNTOS con dos varas: «propia» = por encima de su media de 20; «casa» = por encima de lo que",
         "la casa esperaba de ese equipo ese partido ((total ∓ hándicap)/2). Con la dirección del método.", ""]
    L.append("1 · ¿LA BURBUJA DE PUNTOS SIGUE? (% de veces que el siguiente partido también queda por encima de su media)")
    for per, d in r["continuacion"].items():
        for fam, v in d.items():
            L.append(f"  {per:18s} {fam:10s} todos {v['base']:.1%} · con burbuja abierta de " + " · ".join(
                f"{t}: {x['sigue']:.1%} ({x['n']})" for t, x in v["porRacha"].items() if x["n"]))
    L += ["", "1-bis · LA K DE PUNTOS EN SU EXTREMO (regla del fútbol): ¿la racha de puntos sigue? (% que el siguiente queda arriba de su vara)"]
    for per, d in r["extremo"].items():
        for fam, v in d.items():
            L.append(f"  {per:18s} {fam:10s} " + " · ".join(
                f"{est}: {x['sigue']:.1%} ({x['n']})" for est, x in v.items() if x["n"]))
    L.append("  y el MÁS del partido según cuántas burbujas de puntos de la casa (anota/recibe, de los dos) están en extremo o cerca:")
    for per, d in r["extremoTotales"].items():
        L.append(f"  {per:18s} " + " · ".join(f"{k}: sale el más {v['mas']:.1%} ({v['n']})" for k, v in d.items()))
    L += ["", "2 · HÁNDICAP DEL ELEGIDO (favorito sin DESCONFIAR) · balance = ataque − defensa de las burbujas de puntos"]
    for per, d in r["handicap"].items():
        L.append(f"  {per}")
        for k, v in d.items():
            L.append(f"    {k:24s} {v['n']:5d} · cubre {v['acierto']:.1%} · pide {v['pide']:.1%} · ROI {v['roi']:+.1%}")
    L += ["", f"3 · MÁS/MENOS · presión = burbujas de puntos abiertas (0-4) · partidos sin línea: {r['sinLineaDePuntos']}"]
    for per, d in r["totales"].items():
        L.append(f"  {per}")
        for k, v in d.items():
            L.append(f"    {k:30s} {v['n']:5d} · sale {v['acierto']:.1%} · pide {v['pide']:.1%} · ROI {v['roi']:+.1%}")
    return "\n".join(L)


def main():
    r = correr()
    with open(os.path.join(descarga.carpeta(), "puntos.json"), "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    t = texto(r)
    with open(os.path.join(descarga.carpeta(), "puntos.txt"), "w") as f:
        f.write(t + "\n")
    print(t)


if __name__ == "__main__":
    main()
