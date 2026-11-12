"""NBA · lectura de MOMENTUM: las burbujas de esta temporada de los 20 equipos
de mayor nivel (docs/NBA_FASE0.md §5).

Es la pantalla de Burbujas del fútbol llevada a la NBA, SIN cuotas: la
burbuja es una lectura del momentum del equipo frente a su propia historia,
no una probabilidad ni una cuota.

Por equipo y por familia (la K separada como la de goles: VICTORIAS crece
mientras gana y vuelve a 0 al perder; DERROTAS al revés):
  - la burbuja abierta: racha, K, desde cuándo;
  - su POSICIÓN frente a las burbujas de esa familia que ya se cortaron:
    percentil de la K y de la racha, K sobre la mediana, récord previo;
  - la misma referencia en los ÚLTIMOS 20 cortes (el equipo de ahora, no el de
    2016: es el «período» del fútbol);
  - EXTREMO (récord: rojo) y CERCA DEL EXTREMO (franja del 90 %: ámbar) con la
    regla del fútbol (backend/analisis/burbuja._extremo, importada);
  - el riesgo de reventón con los puntos y motivos del fútbol ante el próximo
    rival (por NIVEL del motor, no por cuota);
  - la familia en cero: cuándo y cómo terminó su última burbuja.
Al final, cómo ordenó la guía en la temporada: qué parte de las burbujas se
cortó en cada nivel de riesgo, junto a la referencia del fútbol.

El motor recorre la historia entera porque la necesita (el nivel pide 20
partidos y la base son los cortes previos); lo que se muestra es la temporada.

    python -m backend.nba.burbujas               # temporada en curso, top 20 por nivel de hoy
    python -m backend.nba.burbujas --inicio      # top 20 por el nivel de antes de la temporada
"""
from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime, timedelta, timezone
from statistics import median

from backend.analisis import burbuja as fut
from backend.nba import descarga, motor

ESCALA_G = 5.0     # la que eligió la fase 0 en el entrenamiento (docs/NBA_FASE0.md §4)
ULTIMOS = fut.ULTIMOS_N   # los últimos 20 cortes: el «período» del fútbol


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
                motivos.append(f"{fav} por nivel, a favor de que siga ({fut.PUNTOS_FAVOR[fav]:+d})")
    if f.get("contramano"):
        pts += fut.PUNTOS_CONTRAMANO
        motivos.append(f"racha hecha en la otra condición (+{fut.PUNTOS_CONTRAMANO})")
    return {"puntos": pts, "nivel": fut._nivel_riesgo(pts), "tramo": tramo, "favorito": fav, "motivos": motivos}


def _pct(vals: list[float], x: float) -> int:
    """Percentil como la posición del fútbol: qué parte de los cortes queda en x o por debajo."""
    return math.floor(100 * sum(1 for v in vals if v <= x) / len(vals) + 0.5) if vals else 0


def momentum(fam: dict, nombre: str, partidos_historia: int) -> dict:
    """Dónde está la burbuja abierta de una familia frente a las que se cortaron."""
    rev = fam["reventones"]
    signo = "+" if motor.FAMILIAS[nombre] > 0 else "-"
    out = {"abierta": fam["k"] > 0, "racha": fam["racha"], "k": round(fam["k"], 2), "cortes": len(rev)}
    if not rev:
        return out
    picos, largos = [r["kPico"] for r in rev], [r["partidos"] for r in rev]
    out["historia"] = {"medianaK": round(median(picos), 2), "recordK": round(max(picos), 2),
                       "medianaRacha": median(largos), "recordRacha": max(largos)}
    rec = rev[-ULTIMOS:]
    out["ultimos"] = {"n": len(rec), "medianaK": round(median(r["kPico"] for r in rec), 2),
                      "recordK": round(max(r["kPico"] for r in rec), 2),
                      "medianaRacha": median(r["partidos"] for r in rec), "recordRacha": max(r["partidos"] for r in rec),
                      "desde": rec[0]["fecha"][:10]}
    if not out["abierta"]:
        u = rev[-1]
        out["ultima"] = {"partidos": u["partidos"], "kPico": round(u["kPico"], 2), "cortada": u["fecha"][:10]}
        return out
    k, r = fam["k"], fam["racha"]
    out["posicion"] = {"percentilK": _pct(picos, k), "percentilRacha": _pct(largos, r),
                       "kSobreMediana": round(k / median(picos), 2) if median(picos) > 0 else None,
                       "percentilKUltimos": _pct([x["kPico"] for x in rec], k),
                       "percentilRachaUltimos": _pct([x["partidos"] for x in rec], r)}
    base = {"kPico": {"max": max(picos)}, "partidos": {"max": max(largos)}}
    out["extremo"] = fut._extremo(k, r, base, partidos_historia, signo, de=rev)
    # RÉCORD DEL PERÍODO: la historia arranca en 2015 y sus récords son de
    # planteles que ya no existen; el extremo (rojo) sigue siendo contra toda la
    # historia, como en el fútbol, pero se dice aparte si la burbuja ya pasó
    # todo lo de los últimos 20 cortes (la K, o la racha con 3+ partidos).
    ku, ru = out["ultimos"]["recordK"], out["ultimos"]["recordRacha"]
    motivos = []
    if k > ku and r >= fut.RACHA_RECORD_MIN:
        motivos.append(f"K {round(k, 2)} por encima del récord de sus últimos {len(rec)} cortes ({ku})")
    if r > ru and r >= fut.RACHA_RECORD_MIN:
        motivos.append(f"{r} partidos: más que la racha más larga de sus últimos {len(rec)} cortes ({ru})")
    elif r == ru and r >= fut.RACHA_RECORD_MIN:
        motivos.append(f"{r} partidos: iguala la racha más larga de sus últimos {len(rec)} cortes")
    out["recordPeriodo"] = {"activo": bool(motivos), "motivos": motivos}
    return out


def _proximos(dias: int = 5) -> list[dict]:
    """Partidos sin jugar de los próximos días (ESPN): solo quién y cuándo."""
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
                            "neutral": bool(c.get("neutralSite"))})
    return sorted(out, key=lambda p: p["fecha"])


def _top(partidos, previos, estado, temporada, top, inicio, desde: int = 1) -> list[int]:
    """Los equipos de los puestos `desde`..`top` del ranking por nivel."""
    if inicio:
        nivel_ini = {}
        for p in partidos:
            if p["temporada"] == temporada:
                for lado, t in (("local", p["localId"]), ("visita", p["visitaId"])):
                    if t not in nivel_ini and previos[p["id"]][lado]["nivel"] is not None:
                        nivel_ini[t] = previos[p["id"]][lado]["nivel"]
        return sorted(nivel_ini, key=lambda t: -nivel_ini[t])[desde - 1:top]
    return sorted((t for t in estado if estado[t]["nivel"] is not None), key=lambda t: -estado[t]["nivel"])[desde - 1:top]


def correr(temporada: int | None = None, top: int = 20, con_proximos: bool = True, inicio: bool = False,
           desde: int = 1) -> dict:
    """`inicio`: elegir a los 20 por el nivel de ANTES de la temporada (el de su
    primer partido), no por el de hoy, que ya sabe cómo les fue en el arranque."""
    partidos = descarga.cargar_partidos()
    temporada = temporada or max(p["temporada"] for p in partidos)
    estado: dict[int, dict] = {}
    previos = motor.construir(partidos, escala_g=ESCALA_G, estado_final=estado)
    abrev = {}
    for p in partidos:
        abrev[p["localId"]], abrev[p["visitaId"]] = p["local"], p["visita"]
    los20 = _top(partidos, previos, estado, temporada, top, inicio, desde)
    rank = {t: desde + i for i, t in enumerate(los20)}

    # 1 · hoy
    proximos = _proximos() if con_proximos else []
    hoy = []
    for t in los20:
        st = estado[t]
        prox = next((q for q in proximos if t in (q["localId"], q["visitaId"])), None)
        rival = None
        if prox:
            local = prox["localId"] == t
            rival = prox["visitaId"] if local else prox["localId"]
            f = motor._previo(st, estado[rival], local, prox["neutral"], prox["fecha"], temporada)
        else:
            f = motor._previo(st, st, True, False, "", temporada)
        temp = [p for p in partidos if p["temporada"] == temporada and t in (p["localId"], p["visitaId"])]
        gan = sum(1 for p in temp if (p["ptsLocal"] > p["ptsVisita"]) == (p["localId"] == t))
        familias = {}
        for nombre in motor.FAMILIAS:
            m = momentum(st["fam"][nombre], nombre, len(st["res"]))
            m["riesgo"] = riesgo(f["familias"][nombre]) if prox and m["abierta"] else None
            familias[nombre] = m
        hoy.append({"rank": rank[t], "equipo": abrev[t], "nivel": round(st["nivel"], 3),
                    "temporada": f"{gan}-{len(temp) - gan}", "familias": familias,
                    "proximo": None if not prox else {
                        "fecha": prox["fecha"], "rival": abrev.get(rival), "condicion": "L" if prox["localId"] == t else "V",
                        "nivelRival": None if estado[rival]["nivel"] is None else round(estado[rival]["nivel"], 3)}})

    # 2 · cómo ordenó la guía en la temporada (solo partidos de los 20): qué
    # parte de las burbujas se cortó en cada nivel de riesgo. Frecuencias de lo
    # que pasó, sin cuotas; al lado, la referencia del fútbol (REVENTON §13.2).
    filas = []
    for p in partidos:
        if p["temporada"] != temporada:
            continue
        for lado, t in (("local", p["localId"]), ("visita", p["visitaId"])):
            if t not in rank:
                continue
            gana = (p["ptsLocal"] > p["ptsVisita"]) == (lado == "local")
            for nombre, vista in previos[p["id"]][lado]["familias"].items():
                r = riesgo(vista)
                if r is None:
                    continue
                filas.append({"fecha": p["fecha"][:10], "equipo": abrev[t], "familia": nombre,
                              "racha": vista["racha"], "puntos": r["puntos"], "nivel": r["nivel"],
                              # revienta a cero: la de victorias con una derrota, la de derrotas con una victoria
                              "seCorto": int(gana if nombre == "derrotas" else not gana)})
    por_familia = {}
    for nombre in motor.FAMILIAS:
        por_familia[nombre] = {}
        for niv in ("bajo", "medio", "alto", "muy alto"):
            de = [x for x in filas if x["familia"] == nombre and x["nivel"] == niv]
            por_familia[nombre][niv] = {"n": len(de), "seCortaron": sum(x["seCorto"] for x in de),
                                        "futbolBacktest": fut.TASA_BACKTEST[niv]}
    return {"generado": datetime.now(timezone.utc).isoformat(timespec="seconds"), "temporada": temporada,
            "criterio": (f"los puestos {desde} a {top}" if desde > 1 else f"los {top}")
                        + f" por nivel del motor {'al ARRANCAR la temporada' if inicio else 'hoy'}",
            "hoy": hoy, "guiaEnLaTemporada": {"burbujas": len(filas), "porFamilia": por_familia}, "detalle": filas}


def _linea_familia(nombre: str, m: dict) -> list[str]:
    h = m.get("historia")
    if not h:
        return [f"      {nombre:9s} {'ABIERTA' if m['abierta'] else 'en cero'} · sin cortes previos"]
    u = m["ultimos"]
    ref = (f"historia: {m['cortes']} cortes, K mediana {h['medianaK']} (récord {h['recordK']}), racha mediana "
           f"{h['medianaRacha']:g} (récord {h['recordRacha']}) · últimos {u['n']} (desde {u['desde']}): K mediana "
           f"{u['medianaK']} (récord {u['recordK']}), racha mediana {u['medianaRacha']:g} (récord {u['recordRacha']})")
    if not m["abierta"]:
        ul = m["ultima"]
        return [f"      {nombre:9s} en cero · la última fue de {ul['partidos']} partidos, K pico {ul['kPico']}, "
                f"cortada el {ul['cortada']}", f"                {ref}"]
    po, ex, rg = m["posicion"], m["extremo"], m["riesgo"]
    if ex["activo"]:
        marca = "🔴 EXTREMO"
    elif ex["cerca"]:
        marca = "🟠 CERCA DEL EXTREMO"
    else:
        marca = "dentro de su rango"
    out = [f"      {nombre:9s} ABIERTA {m['racha']} partidos · K {m['k']} · {marca}",
           f"                posición: K sobre el {po['percentilK']} de cada 100 cortes ({po['kSobreMediana']}× la mediana), "
           f"racha sobre el {po['percentilRacha']} · en los últimos {u['n']}: K sobre {po['percentilKUltimos']}, "
           f"racha sobre {po['percentilRachaUltimos']}",
           f"                {ref}"]
    for mo in ex["motivos"]:
        out.append(f"                ↳ {mo}")
    for mo in m["recordPeriodo"]["motivos"]:
        out.append(f"                ↳ 🟡 período reciente: {mo}")
    if rg:
        out.append(f"                riesgo de reventón {rg['nivel']} ({rg['puntos']:+d}): {' · '.join(rg['motivos']) or 'sin puntos'}")
    return out


def texto(r: dict) -> str:
    L = [f"NBA · MOMENTUM · temporada {r['temporada'] - 1}-{str(r['temporada'])[2:]} · {r['criterio']}",
         "La K separada como la de goles: VICTORIAS crece mientras gana y vuelve a 0 al perder; DERROTAS al revés.",
         "Cada burbuja se lee contra las de su familia que ya se cortaron (toda la historia y los últimos 20).",
         "Sin cuotas: es el momentum del equipo frente a sí mismo, no una probabilidad.", ""]
    for h in r["hoy"]:
        pr = h["proximo"]
        prox = ("sin próximo en 5 días" if not pr else
                f"próximo {'de local' if pr['condicion'] == 'L' else 'de visita'} con {pr['rival']} "
                f"(nivel {pr['nivelRival']}) el {pr['fecha'][5:10]}")
        L.append(f"{h['rank']:2d}  {h['equipo']} · nivel {h['nivel']:.2f} · {h['temporada']} · {prox}")
        for nombre in ("victorias", "derrotas"):
            L += _linea_familia(nombre, h["familias"][nombre])
        L.append("")
    g = r["guiaEnLaTemporada"]
    L += [f"CÓMO ORDENÓ LA GUÍA en la temporada ({g['burbujas']} burbujas abiertas con base, solo estos {len(r['hoy'])})",
          "  riesgo      victorias: se cortaron     derrotas: se cortaron      fútbol (backtest)"]
    for niv in ("bajo", "medio", "alto", "muy alto"):
        v, d = g["porFamilia"]["victorias"][niv], g["porFamilia"]["derrotas"][niv]
        fb = v["futbolBacktest"]
        tv = f"{v['seCortaron']:3d} de {v['n']:3d} ({v['seCortaron'] / v['n']:.0%})" if v["n"] else "  —"
        td = f"{d['seCortaron']:3d} de {d['n']:3d} ({d['seCortaron'] / d['n']:.0%})" if d["n"] else "  —"
        L.append(f"  {niv:9s}   {tv:24s}  {td:24s} {fb[0]:.0%}–{fb[1]:.0%}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--temporada", type=int, default=None)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--desde", type=int, default=1, help="primer puesto del ranking (21 con --top 30 = los otros 10)")
    ap.add_argument("--inicio", action="store_true", help="el ranking por el nivel de antes de la temporada (sin sesgo)")
    a = ap.parse_args()
    r = correr(a.temporada, a.top, inicio=a.inicio, desde=a.desde)
    with open(os.path.join(descarga.carpeta(), "burbujas.json"), "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    t = texto(r)
    with open(os.path.join(descarga.carpeta(), "burbujas.txt"), "w") as f:
        f.write(t + "\n")
    print(t)


if __name__ == "__main__":
    main()
