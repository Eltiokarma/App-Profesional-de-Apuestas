"""NBA · las burbujas de ESTA temporada, de los 20 equipos de mayor nivel
(docs/NBA_FASE0.md §5).

No es un backtest de miles de partidos: es la pantalla de Burbujas del fútbol
llevada a la NBA, sobre la temporada en curso.

  1 · HOY: la burbuja abierta de cada uno de los 20, su base (cómo se le
      cortaron antes las rachas de ese signo), el próximo partido con su
      cuota y el riesgo de reventón con las MISMAS reglas y puntos del fútbol
      (backend/analisis/burbuja.py: racha ≥ mediana, rival en la dirección
      del riesgo, favorito, contramano). Guía, no probabilidad.
  2 · CÓMO LE FUE A LA GUÍA en lo que va de la temporada: en cada partido ya
      jugado de esos 20, el riesgo que se habría leído antes contra si la
      racha se cortó, y contra lo que decía la cuota.

El motor recorre la historia entera porque la necesita: el nivel pide 20
partidos (en noviembre nadie llegó a 20 en la temporada) y la base de cada
equipo son sus reventones previos (como en el fútbol, que usa todos). Lo que
se MIDE y se muestra es solo la temporada.

    python -m backend.nba.burbujas               # temporada en curso
    python -m backend.nba.burbujas --temporada 2027 --top 20
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone

from backend.analisis import burbuja as fut
from backend.nba import descarga, motor
from backend.nba.fase0 import consenso

ESCALA_G = 5.0     # la que eligió la fase 0 en el entrenamiento (docs/NBA_FASE0.md §4)


def riesgo(f: dict) -> dict | None:
    """Los puntos del fútbol sobre lo que se sabe de un lado ANTES de jugar.
    None si no hay burbuja o no hay base (menos de MUESTRA_BAJA reventones)."""
    s = f["signo"]
    if not s or f["reventonesSigno"] < fut.MUESTRA_BAJA:
        return None
    pts, motivos = 0, []
    if f["racha"] >= f["medianaPartidos"]:
        pts += fut.PUNTOS_RACHA
        motivos.append(f"racha {f['racha']} ≥ mediana {f['medianaPartidos']:g} (+{fut.PUNTOS_RACHA})")
    tramo = fav = None
    if f["nivelRival"] is not None and f["medianaNivelRival"] is not None:
        d = s * (f["nivelRival"] - f["medianaNivelRival"])
        tramo = ("lejos" if d < -fut.ZONA_TOLERANCIA else "zona" if d < fut.ZONA_TOLERANCIA
                 else "fuerte" if d < fut.RIVAL_FUERTE else "muy fuerte")
        if fut.PUNTOS_RIVAL[tramo]:
            pts += fut.PUNTOS_RIVAL[tramo]
            motivos.append(f"rival {tramo} en la dirección del riesgo (+{fut.PUNTOS_RIVAL[tramo]})")
        if f["nivel"] is not None:
            g = s * (f["nivel"] - f["nivelRival"])
            fav = "muy favorito" if g >= fut.MUY_FAVORITO else "favorito" if g >= fut.FAVORITO else "no"
            if fut.PUNTOS_FAVOR[fav]:
                pts += fut.PUNTOS_FAVOR[fav]
                motivos.append(f"{fav} a favor de que siga ({fut.PUNTOS_FAVOR[fav]:+d})")
    if f.get("contramano"):
        pts += fut.PUNTOS_CONTRAMANO
        motivos.append(f"racha hecha en la otra condición (+{fut.PUNTOS_CONTRAMANO})")
    return {"puntos": pts, "nivel": fut._nivel_riesgo(pts), "tramo": tramo, "favorito": fav, "motivos": motivos}


def _proximos(dias: int = 5) -> list[dict]:
    """Partidos sin jugar de los próximos días (ESPN), con su cuota si ya está."""
    hoy = datetime.now(timezone.utc).date()
    out = []
    for k in range(dias):
        crudo = descarga._get(descarga.URL_DIA.format(d=(hoy + timedelta(days=k)).strftime("%Y%m%d"))) or {}
        for e in crudo.get("events", []):
            c = (e.get("competitions") or [{}])[0]
            if ((c.get("status") or {}).get("type") or {}).get("completed"):
                continue
            lados = {t.get("homeAway"): t for t in c.get("competitors", [])}
            if set(lados) != {"home", "away"}:
                continue
            li, vi = int(lados["home"]["team"]["id"]), int(lados["away"]["team"]["id"])
            if li in descarga.FRANQUICIAS and vi in descarga.FRANQUICIAS:
                out.append({"id": int(e["id"]), "fecha": e["date"], "localId": li, "visitaId": vi,
                            "local": lados["home"]["team"]["abbreviation"],
                            "visita": lados["away"]["team"]["abbreviation"],
                            "neutral": bool(c.get("neutralSite"))})
    return sorted(out, key=lambda p: p["fecha"])


def _p_corte(signo: int, p_gana: float | None) -> float | None:
    if p_gana is None:
        return None
    return (1 - p_gana) if signo > 0 else p_gana


def correr(temporada: int | None = None, top: int = 20, con_proximos: bool = True) -> dict:
    partidos = descarga.cargar_partidos()
    cuotas = descarga.cargar_cuotas()
    temporada = temporada or max(p["temporada"] for p in partidos)
    estado: dict[int, dict] = {}
    previos = motor.construir(partidos, escala_g=ESCALA_G, estado_final=estado)
    abrev = {}
    for p in partidos:
        abrev[p["localId"]], abrev[p["visitaId"]] = p["local"], p["visita"]
    los20 = sorted((t for t in estado if estado[t]["nivel"] is not None),
                   key=lambda t: -estado[t]["nivel"])[:top]
    rank = {t: i + 1 for i, t in enumerate(los20)}

    # 1 · hoy
    proximos = _proximos() if con_proximos else []
    hoy = []
    for t in los20:
        st = estado[t]
        prox = next((q for q in proximos if t in (q["localId"], q["visitaId"])), None)
        f, rival, cuota = None, None, None
        if prox:
            local = prox["localId"] == t
            rival = prox["visitaId"] if local else prox["localId"]
            f = motor._previo(st, estado[rival], local, prox["neutral"], prox["fecha"], temporada)
            c = consenso(descarga.recortar_cuotas(descarga._get(descarga.URL_CUOTAS.format(i=prox["id"])) or {}))
            if c and c["pLocal"] is not None:
                cuota = c["pLocal"] if local else 1 - c["pLocal"]
        else:
            f = motor._previo(st, st, True, False, "", temporada)
        temp = [p for p in partidos if p["temporada"] == temporada and t in (p["localId"], p["visitaId"])]
        gan = sum(1 for p in temp if (p["ptsLocal"] > p["ptsVisita"]) == (p["localId"] == t))
        familias = {}
        for nombre, vista in f["familias"].items():
            familias[nombre] = {
                "abierta": bool(vista["signo"]), "racha": vista["racha"], "k": round(vista["k"], 2),
                "base": {"reventones": vista["reventonesSigno"], "medianaRacha": vista["medianaPartidos"],
                         "medianaKPico": None if vista["medianaKPico"] is None else round(vista["medianaKPico"], 2),
                         "medianaNivelRival": None if vista["medianaNivelRival"] is None else round(vista["medianaNivelRival"], 3)},
                "pCorteCuota": None if cuota is None or not vista["signo"] else round(_p_corte(vista["signo"], cuota), 3),
                "riesgo": riesgo(vista) if prox else None}
        hoy.append({"rank": rank[t], "equipo": abrev[t], "nivel": round(st["nivel"], 3),
                    "temporada": f"{gan}-{len(temp) - gan}", "familias": familias,
                    "proximo": None if not prox else {
                        "fecha": prox["fecha"], "rival": abrev.get(rival), "condicion": "L" if prox["localId"] == t else "V",
                        "nivelRival": None if estado[rival]["nivel"] is None else round(estado[rival]["nivel"], 3),
                        "pGanaCuota": None if cuota is None else round(cuota, 3)}})

    # 2 · cómo le fue a la guía en la temporada (solo partidos de los 20)
    filas = []
    for p in partidos:
        if p["temporada"] != temporada:
            continue
        c = consenso(cuotas.get(p["id"], []))
        for lado, t in (("local", p["localId"]), ("visita", p["visitaId"])):
            if t not in rank:
                continue
            gana = (p["ptsLocal"] > p["ptsVisita"]) == (lado == "local")
            p_gana = None if not c or c["pLocal"] is None else (c["pLocal"] if lado == "local" else 1 - c["pLocal"])
            for nombre, vista in previos[p["id"]][lado]["familias"].items():
                r = riesgo(vista)
                if r is None:
                    continue
                filas.append({"fecha": p["fecha"][:10], "equipo": abrev[t], "familia": nombre,
                              "racha": vista["racha"], "puntos": r["puntos"], "nivel": r["nivel"],
                              # revienta a cero: la de victorias con una derrota, la de derrotas con una victoria
                              "seCorto": int(gana if nombre == "derrotas" else not gana),
                              "pCorteCuota": _p_corte(vista["signo"], p_gana)})
    por_familia = {}
    for nombre in motor.FAMILIAS:
        por_familia[nombre] = {}
        for niv in ("bajo", "medio", "alto", "muy alto"):
            de = [x for x in filas if x["familia"] == nombre and x["nivel"] == niv]
            cq = [x["pCorteCuota"] for x in de if x["pCorteCuota"] is not None]
            por_familia[nombre][niv] = {
                "n": len(de), "seCorta": round(sum(x["seCorto"] for x in de) / len(de), 3) if de else None,
                "cuotaDecia": round(sum(cq) / len(cq), 3) if cq else None, "futbolBacktest": fut.TASA_BACKTEST[niv]}
    return {"generado": datetime.now(timezone.utc).isoformat(timespec="seconds"), "temporada": temporada,
            "criterio": f"los {top} de mayor nivel del motor hoy (ESCALA_G {ESCALA_G})",
            "hoy": hoy, "guiaEnLaTemporada": {"lados": len(filas), "porFamilia": por_familia}, "detalle": filas}


def texto(r: dict) -> str:
    L = [f"NBA · burbujas de la temporada {r['temporada'] - 1}-{str(r['temporada'])[2:]} · {r['criterio']}",
         "Dos familias separadas, como la K de goles: VICTORIAS (crece mientras gana, a 0 al perder) y",
         "DERROTAS (crece mientras pierde, a 0 al ganar). Siempre hay una abierta y la otra en cero.", ""]
    for h in r["hoy"]:
        pr = h["proximo"]
        prox = "sin próximo" if not pr else (f"próximo {pr['condicion']} {pr['rival']} {pr['fecha'][5:10]}"
                                            + ("" if pr["pGanaCuota"] is None else f" · la cuota le da {pr['pGanaCuota']:.0%}"))
        L.append(f"{h['rank']:2d}  {h['equipo']:5s} nivel {h['nivel']:.2f} · {h['temporada']} · {prox}")
        for nombre, fa in h["familias"].items():
            b = fa["base"]
            base = (f"base {b['reventones']} reventones, mediana racha {b['medianaRacha']:g}, "
                    f"K pico {b['medianaKPico']}, rival {b['medianaNivelRival']}") if b["reventones"] else "sin base"
            if not fa["abierta"]:
                L.append(f"      {nombre:9s} en cero · {base}")
                continue
            rg = fa["riesgo"]
            pc = "" if fa["pCorteCuota"] is None else f" · cuota del corte {fa['pCorteCuota']:.0%}"
            rgt = "" if not rg else f" · riesgo {rg['nivel']} ({rg['puntos']:+d}): {' · '.join(rg['motivos']) or 'sin puntos'}"
            L.append(f"      {nombre:9s} ABIERTA {fa['racha']} partidos, K {fa['k']:.2f} · {base}{pc}{rgt}")
    g = r["guiaEnLaTemporada"]
    L += ["", f"CÓMO LE FUE A LA GUÍA en la temporada ({g['lados']} burbujas abiertas con base, solo los 20)"]
    for nombre, tabla in g["porFamilia"].items():
        L += [f"  {nombre.upper()}", "  riesgo     n   se cortó   la cuota decía   fútbol (backtest)"]
        for k, v in tabla.items():
            sc = "—" if v["seCorta"] is None else f"{v['seCorta']:.0%}"
            cq = "—" if v["cuotaDecia"] is None else f"{v['cuotaDecia']:.0%}"
            fb = v["futbolBacktest"]
            L.append(f"  {k:9s} {v['n']:3d}   {sc:>7s}   {cq:>13s}    {fb[0]:.0%}–{fb[1]:.0%}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--temporada", type=int, default=None)
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args()
    r = correr(a.temporada, a.top)
    with open(os.path.join(descarga.carpeta(), "burbujas.json"), "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    t = texto(r)
    with open(os.path.join(descarga.carpeta(), "burbujas.txt"), "w") as f:
        f.write(t + "\n")
    print(t)


if __name__ == "__main__":
    main()
