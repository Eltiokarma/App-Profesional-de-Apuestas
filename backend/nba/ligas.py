"""Básquet · ¿hasta qué escalón baja la teoría? (docs/NBA_FASE0.md §7)

El fase0_ligas del fútbol llevado al básquet. Con la vara del sistema (win
rate y dónde poner la plata, docs/METODO_APUESTA.md; SIN cuotas), mide en
cada liga los tramos de momentum que funcionaron en la NBA (§6 y §6.1):

  A · los de ARRIBA, burbuja de victorias, riesgo bajo  → la racha sigue
  B · los de ARRIBA, burbuja de derrotas, riesgo muy alto → la mala racha se corta
  C · los de ABAJO, burbuja de derrotas, riesgo bajo   → la mala racha sigue
  D · los de ABAJO, burbuja de victorias, riesgo muy alto → la racha buena se corta

«Arriba / abajo» = tercio de nivel del motor AL ARRANCAR cada temporada (sin
sesgo). Y por liga: el acierto del nivel (gana el de más nivel) y la
SEPARACIÓN de la guía (tasa de corte en riesgo muy alto − en bajo), como
`separacionLiga` del fútbol. En la NCAA, además, los mismos tramos por la
fuerza de la CONFERENCIA (el escalón subregional).

Escalones: NBA (referencia, últimas 4 temporadas) · G League (la liga B) ·
NBL Australia (otro país) · WNBA (otra liga) · NCAA D1 (~360 equipos).
Solo lee lo que bajó `python -m backend.nba.descarga --liga …` (marcadores).

    python -m backend.nba.ligas                  # todas las que haya en disco
    python -m backend.nba.ligas --liga wnba
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

from backend.nba import burbujas, descarga, motor

MIN_PARTIDOS = 10          # por temporada: menos que esto es un rival de otra división
NBA_DESDE = 2023           # la NBA de referencia: las últimas 4 temporadas
N_FIRME = 30               # un tramo con menos casos en la temporada no opina
ACIERTO_FIRME = 0.65       # el tramo se sostiene si TODAS sus temporadas con n ≥ 30 llegan acá
TRAMOS = {
    "A": ("arriba", "victorias", "bajo", "racha de victorias sigue"),
    "B": ("arriba", "derrotas", "muy alto", "mala racha se corta"),
    "C": ("abajo", "derrotas", "bajo", "mala racha sigue"),
    "D": ("abajo", "victorias", "muy alto", "racha buena se corta"),
}


def _filtrar(partidos: list[dict]) -> list[dict]:
    """Solo partidos entre equipos que juegan la temporada entera en esta liga."""
    cuenta = defaultdict(int)
    for p in partidos:
        cuenta[(p["temporada"], p["localId"])] += 1
        cuenta[(p["temporada"], p["visitaId"])] += 1
    return [p for p in partidos if cuenta[(p["temporada"], p["localId"])] >= MIN_PARTIDOS
            and cuenta[(p["temporada"], p["visitaId"])] >= MIN_PARTIDOS]


def _tercio(valores: dict, clave) -> str:
    orden = sorted(valores, key=lambda k: -valores[k])
    i, n = orden.index(clave), len(orden)
    return "arriba" if i < n / 3 else "abajo" if i >= 2 * n / 3 else "medio"


def estudiar(liga: str, desde_temporada: int | None = None) -> dict | None:
    partidos = _filtrar(descarga.cargar_partidos(descarga.carpeta(liga)))
    if len(partidos) < 200:
        return None
    previos = motor.construir(partidos, escala_g=burbujas.ESCALA_G)
    temporadas = sorted({p["temporada"] for p in partidos})
    medir = [t for t in temporadas[1:] if desde_temporada is None or t >= desde_temporada]  # la 1.ª calienta

    # nivel al ARRANCAR cada temporada (el de su primer partido) y su conferencia
    ini, conf = {}, {}
    for p in partidos:
        for lado, t, c in (("local", p["localId"], p.get("localConf")), ("visita", p["visitaId"], p.get("visitaConf"))):
            key = (p["temporada"], t)
            if key not in ini and previos[p["id"]][lado]["nivel"] is not None:
                ini[key] = previos[p["id"]][lado]["nivel"]
            if c is not None:
                conf.setdefault(key, c)
    por_temp = defaultdict(dict)
    for (temp, t), v in ini.items():
        por_temp[temp][t] = v
    # fuerza de cada conferencia por temporada = media del nivel de arranque de sus equipos
    conf_tier = {}
    for temp in medir:
        sumas = defaultdict(list)
        for t, v in por_temp[temp].items():
            if (temp, t) in conf:
                sumas[conf[(temp, t)]].append(v)
        medias = {c: sum(v) / len(v) for c, v in sumas.items() if len(v) >= 4}
        for c in medias:
            conf_tier[(temp, c)] = _tercio(medias, c)

    out = {"liga": liga, "nombre": descarga.LIGAS.get(liga, {}).get("nombre", "NBA"), "temporadas": {}}
    tramos = {k: defaultdict(lambda: [0, 0]) for k in TRAMOS}
    tramos_conf = {k: defaultdict(lambda: [0, 0]) for k in TRAMOS}
    guia = defaultdict(lambda: [0, 0])           # (familia, riesgo) → [cortes, n]
    nivel_ok = nivel_n = 0
    for temp in medir:
        ps = [p for p in partidos if p["temporada"] == temp]
        equipos = {p["localId"] for p in ps} | {p["visitaId"] for p in ps}
        out["temporadas"][str(temp)] = {"equipos": len(equipos), "partidos": len(ps)}
        for p in ps:
            f = previos[p["id"]]
            gana_local = p["ptsLocal"] > p["ptsVisita"]
            if f["local"]["nivel"] is not None and f["visita"]["nivel"] is not None and f["local"]["nivel"] != f["visita"]["nivel"]:
                nivel_n += 1
                nivel_ok += (f["local"]["nivel"] > f["visita"]["nivel"]) == gana_local
            for lado, t in (("local", p["localId"]), ("visita", p["visitaId"])):
                if (temp, t) not in ini:
                    continue
                tercio = _tercio(por_temp[temp], t)
                ct = conf_tier.get((temp, conf.get((temp, t))))
                gana = gana_local == (lado == "local")
                for fam, vista in f[lado]["familias"].items():
                    r = burbujas.riesgo(vista)
                    if r is None:
                        continue
                    corto = gana if fam == "derrotas" else not gana
                    guia[(fam, r["nivel"])][0] += corto
                    guia[(fam, r["nivel"])][1] += 1
                    for k, (quien, fam_k, riesgo_k, lectura) in TRAMOS.items():
                        if fam != fam_k or r["nivel"] != riesgo_k:
                            continue
                        cumple = corto if "corta" in lectura else not corto
                        if tercio == quien:
                            tramos[k][temp][0] += cumple
                            tramos[k][temp][1] += 1
                        if ct == quien:
                            tramos_conf[k][temp][0] += cumple
                            tramos_conf[k][temp][1] += 1

    def resumen(tabla):
        res = {}
        for k, (quien, fam, riesgo_k, lectura) in TRAMOS.items():
            filas = {str(t): {"cumple": v[0], "n": v[1]} for t, v in sorted(tabla[k].items())}
            tot = [sum(v[0] for v in tabla[k].values()), sum(v[1] for v in tabla[k].values())]
            opinan = [v[0] / v[1] for v in tabla[k].values() if v[1] >= N_FIRME]
            res[k] = {"quien": quien, "familia": fam, "riesgo": riesgo_k, "lectura": lectura, "porTemporada": filas,
                      "total": {"cumple": tot[0], "n": tot[1], "acierto": round(tot[0] / tot[1], 3) if tot[1] else None},
                      "firme": bool(opinan) and min(opinan) >= ACIERTO_FIRME}
        return res

    tasa = lambda fam, niv: guia[(fam, niv)][0] / guia[(fam, niv)][1] if guia[(fam, niv)][1] else None  # noqa: E731
    out["aciertoNivel"] = round(nivel_ok / nivel_n, 3) if nivel_n else None
    out["guia"] = {f"{fam} · {niv}": {"cortes": guia[(fam, niv)][0], "n": guia[(fam, niv)][1]}
                   for fam in motor.FAMILIAS for niv in ("bajo", "medio", "alto", "muy alto")}
    out["separacion"] = {fam: (round(tasa(fam, "muy alto") - tasa(fam, "bajo"), 3)
                               if tasa(fam, "muy alto") is not None and tasa(fam, "bajo") is not None else None)
                         for fam in motor.FAMILIAS}
    out["tramos"] = resumen(tramos)
    if conf:
        out["tramosPorConferencia"] = resumen(tramos_conf)
    return out


def texto(res: list[dict]) -> str:
    L = ["BÁSQUET · ¿hasta qué escalón baja la teoría? (sin cuotas: % de veces que se cumplió la lectura)", ""]
    L.append(f"{'liga':28s} {'equipos':>8s} {'nivel acierta':>14s} {'separación v/d':>16s}   "
             + "   ".join(f"{k}·{TRAMOS[k][0]} {TRAMOS[k][1][:4]} {TRAMOS[k][2]}" for k in TRAMOS))
    for r in res:
        eq = max(v["equipos"] for v in r["temporadas"].values())
        sep = r["separacion"]
        celdas = []
        for k in TRAMOS:
            t = r["tramos"][k]["total"]
            celdas.append(("—" if not t["n"] else f"{t['acierto']:.0%} ({t['n']})") + (" ✓" if r["tramos"][k]["firme"] else ""))
        L.append(f"{r['nombre'][:28]:28s} {eq:8d} {r['aciertoNivel']:14.1%} "
                 f"{sep['victorias']:+7.2f}/{sep['derrotas']:+.2f}   " + "   ".join(f"{c:>22s}" for c in celdas))
    L += ["", "✓ = firme: en TODAS sus temporadas con 30+ casos acertó 65 % o más.", ""]
    for r in res:
        L.append(f"{r['nombre']} · por temporada")
        for k in TRAMOS:
            tr = r["tramos"][k]
            L.append(f"  {k} {tr['quien']:6s} {tr['lectura']:26s} " + " · ".join(
                f"{t}: {v['cumple'] / v['n']:.0%} ({v['n']})" if v["n"] else f"{t}: —" for t, v in tr["porTemporada"].items()))
        if "tramosPorConferencia" in r:
            L.append("  por fuerza de la CONFERENCIA (tercio de conferencias por nivel medio):")
            for k in TRAMOS:
                tr = r["tramosPorConferencia"][k]
                t = tr["total"]
                L.append(f"  {k} conf. {tr['quien']:6s} {tr['lectura']:26s} "
                         + (f"{t['acierto']:.0%} ({t['n']})" if t["n"] else "—") + (" ✓" if tr["firme"] else ""))
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--liga", default=None)
    a = ap.parse_args()
    ligas = [a.liga] if a.liga else ["nba", *descarga.LIGAS]
    res = []
    for liga in ligas:
        r = estudiar(liga, NBA_DESDE if liga == "nba" else None)
        if r:
            res.append(r)
        else:
            print(f"{liga}: sin datos suficientes (python -m backend.nba.descarga --liga {liga})")
    with open(os.path.join(descarga.carpeta(), "ligas.json"), "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    t = texto(res)
    with open(os.path.join(descarga.carpeta(), "ligas.txt"), "w") as f:
        f.write(t + "\n")
    print(t)


if __name__ == "__main__":
    main()
