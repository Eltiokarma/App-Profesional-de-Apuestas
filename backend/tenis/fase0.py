"""Tenis · fase 0 · ¿la teoría del momentum aguanta en el tenis? (docs/TENIS_FASE0.md)

Con la vara del sistema (win rate y dónde poner la plata, docs/METODO_APUESTA.md;
SIN cuotas), la misma lectura que en el básquet (docs/NBA_FASE0.md §6-§7):

  - el motor por JUGADOR (backend.nba.motor): nivel = 3·victorias/20 + G + 1,
    con G = ESCALA_G × Σ(juegos ganados − perdidos)/Σ juegos de los últimos 5;
    q = (margen de juegos / ESCALA_MARGEN) × nivel del rival. No hay localía:
    todo partido es neutral (sin factor de visita ni contramano).
  - la K separada como la de goles: burbuja de VICTORIAS y de DERROTAS, con
    el riesgo de reventón del fútbol (backend.nba.burbujas.riesgo).
  - los cuatro tramos (A-D de backend.nba.ligas) con «arriba / abajo» =
    tercio de nivel del circuito al ARRANCAR cada año (sin sesgo).
  - los escalones: Grand Slam, cuadro principal y QUALY (donde juegan los
    del nivel Challenger: el escalón de abajo que ESPN deja ver).
  - HOY: la lectura de momentum de los 20 de mayor nivel de cada circuito.

El tenis es por torneos: casi todos pierden una vez por semana, así que las
rachas cruzan torneos (la K no se reinicia al cambiar de torneo).

    python -m backend.tenis.fase0          # → tenis_data/fase0.txt y .json
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import date, timedelta

from backend.nba import burbujas, motor
from backend.nba.ligas import ACIERTO_FIRME, N_FIRME, TRAMOS, _tercio
from backend.tenis import descarga
from backend.tenis.elo import elo_como_nivel

ESCALA_MARGEN = 5.0     # 5 juegos de diferencia ≈ «un gol» (un 6-3 6-4 da 5)
ESCALAS_G = (2.0, 5.0, 10.0)
AÑO_VALIDACION = 2020   # la ESCALA_G se elige con los años hasta acá (y se mide de ahí en adelante)
MIN_PARTIDOS = 10       # en el año, para entrar a los tercios del circuito
TOP = 20
ACTIVO_DIAS = 60        # la foto de hoy: jugó en los últimos 60 días
MIN_CUADRO = 10         # … y 10+ partidos de cuadro principal en el último año


def a_motor(ps: list[dict]) -> list[dict]:
    """Al formato del motor. El lado «local» se sortea por el id (fijo y
    reproducible): si el ganador fuera siempre el local, nada lo ve antes del
    partido (todo es neutral), pero así no queda ni la tentación."""
    out = []
    for p in ps:
        w_local = p["id"] % 2 == 0
        L, V = (p["ganadorId"], p["perdedorId"]) if w_local else (p["perdedorId"], p["ganadorId"])
        gl, gv = (p["juegosGanador"], p["juegosPerdedor"]) if w_local else (p["juegosPerdedor"], p["juegosGanador"])
        out.append({"id": p["id"], "fecha": p["fecha"], "temporada": int(p["fecha"][:4]), "tipo": "regular",
                    "localId": L, "visitaId": V, "ptsLocal": gl, "ptsVisita": gv, "neutral": True,
                    "tour": p["tour"], "escalon": "Grand Slam" if p["grandSlam"] and not p["qualy"]
                    else "qualy" if p["qualy"] else "cuadro principal"})
    return out


def _acierto_nivel(ps, previos, desde: int, hasta: int | None = None) -> float | None:
    ok = n = 0
    for p in ps:
        if p["temporada"] < desde or (hasta and p["temporada"] > hasta):
            continue
        a, b = previos[p["id"]]["local"]["nivel"], previos[p["id"]]["visita"]["nivel"]
        if a is None or b is None or a == b:
            continue
        n += 1
        ok += (a > b) == (p["ptsLocal"] > p["ptsVisita"])
    return ok / n if n else None


def elegir_escala(ps) -> dict:
    tabla = {}
    for e in ESCALAS_G:
        prev = motor.construir(ps, escala_g=e, escala_margen=ESCALA_MARGEN)
        tabla[e] = _acierto_nivel(ps, prev, 2017, AÑO_VALIDACION)
    return {"elegida": max(tabla, key=tabla.get), "aciertoValidacion": {str(k): round(v, 4) for k, v in tabla.items()}}


def estudiar(ps: list[dict], previos: dict) -> dict:
    años = sorted({p["temporada"] for p in ps})
    medir = [a for a in años if a > AÑO_VALIDACION]
    # nivel al ARRANCAR el año, por circuito, solo quien juega MIN_PARTIDOS en el año
    cuenta = defaultdict(int)
    for p in ps:
        cuenta[(p["temporada"], p["localId"])] += 1
        cuenta[(p["temporada"], p["visitaId"])] += 1
    ini = {}
    for p in ps:
        for lado, t in (("local", p["localId"]), ("visita", p["visitaId"])):
            k = (p["tour"], p["temporada"], t)
            if k not in ini and cuenta[(p["temporada"], t)] >= MIN_PARTIDOS and previos[p["id"]][lado]["nivel"] is not None:
                ini[k] = previos[p["id"]][lado]["nivel"]
    grupos = defaultdict(dict)
    for (tour, año, t), v in ini.items():
        grupos[(tour, año)][t] = v

    res = {}
    for tour in ("ATP", "WTA"):
        r = {"partidosMedidos": 0, "aciertoNivel": {}, "tramos": {}, "guia": {}}
        tramos = {(k, esc): defaultdict(lambda: [0, 0]) for k in TRAMOS for esc in ("todos", "Grand Slam", "cuadro principal", "qualy")}
        guia = defaultdict(lambda: [0, 0])
        nivel = defaultdict(lambda: [0, 0])
        for p in ps:
            if p["tour"] != tour or p["temporada"] not in medir:
                continue
            r["partidosMedidos"] += 1
            f = previos[p["id"]]
            gana_local = p["ptsLocal"] > p["ptsVisita"]
            a, b = f["local"]["nivel"], f["visita"]["nivel"]
            if a is not None and b is not None and a != b:
                for esc in ("todos", p["escalon"]):
                    nivel[esc][1] += 1
                    nivel[esc][0] += (a > b) == gana_local
            for lado, t in (("local", p["localId"]), ("visita", p["visitaId"])):
                if (tour, p["temporada"], t) not in ini:
                    continue
                tercio = _tercio(grupos[(tour, p["temporada"])], t)
                gana = gana_local == (lado == "local")
                for fam, vista in f[lado]["familias"].items():
                    rg = burbujas.riesgo(vista)
                    if rg is None:
                        continue
                    corto = gana if fam == "derrotas" else not gana
                    guia[(fam, rg["nivel"])][0] += corto
                    guia[(fam, rg["nivel"])][1] += 1
                    for k, (quien, fam_k, riesgo_k, lectura) in TRAMOS.items():
                        if fam == fam_k and rg["nivel"] == riesgo_k and tercio == quien:
                            cumple = corto if "corta" in lectura else not corto
                            for esc in ("todos", p["escalon"]):
                                tramos[(k, esc)][p["temporada"]][0] += cumple
                                tramos[(k, esc)][p["temporada"]][1] += 1
        r["aciertoNivel"] = {esc: round(v[0] / v[1], 3) for esc, v in nivel.items() if v[1]}
        r["guia"] = {f"{fam} · {niv}": {"cortes": v[0], "n": v[1]} for (fam, niv), v in sorted(guia.items())}
        for (k, esc), tabla in tramos.items():
            tot = [sum(v[0] for v in tabla.values()), sum(v[1] for v in tabla.values())]
            opinan = [v[0] / v[1] for v in tabla.values() if v[1] >= N_FIRME]
            r["tramos"].setdefault(esc, {})[k] = {
                "lectura": f"{TRAMOS[k][0]} · {TRAMOS[k][3]}",
                "porAño": {str(a): {"cumple": v[0], "n": v[1]} for a, v in sorted(tabla.items())},
                "total": {"cumple": tot[0], "n": tot[1], "acierto": round(tot[0] / tot[1], 3) if tot[1] else None},
                "firme": bool(opinan) and min(opinan) >= ACIERTO_FIRME}
        res[tour] = r
    return res


def hoy(ps: list[dict], crudos: list[dict], escala_g: float, **variante) -> dict:
    """La lectura de momentum de los 20 de mayor nivel de cada circuito HOY.
    `variante`: las opciones del nivel de motor.construir (§4)."""
    estado: dict[int, dict] = {}
    motor.construir(ps, escala_g=escala_g, escala_margen=ESCALA_MARGEN, estado_final=estado, **variante)
    nombre, tour_de, ultimo = {}, {}, {}
    for p in crudos:
        nombre[p["ganadorId"]], nombre[p["perdedorId"]] = p["ganador"], p["perdedor"]
        tour_de[p["ganadorId"]] = tour_de[p["perdedorId"]] = p["tour"]
        ultimo[p["ganadorId"]] = ultimo[p["perdedorId"]] = p["fecha"][:10]
    # ACTIVOS Y DEL CIRCUITO: el nivel del motor mide FORMA (victorias y juegos),
    # no la calidad del rival, y en el tenis todos van al mismo pozo: quien gana
    # mucho en la qualy o en torneos chicos sube igual. Para la foto de hoy:
    # jugó en los últimos ACTIVO_DIAS y tiene MIN_CUADRO partidos de cuadro
    # principal en el último año (docs/TENIS_FASE0.md §3).
    fin = date.fromisoformat(max(p["fecha"] for p in crudos)[:10])
    desde_activo = (fin - timedelta(days=ACTIVO_DIAS)).isoformat()
    desde_año = (fin - timedelta(days=365)).isoformat()
    cuadro = defaultdict(int)
    for p in crudos:
        if not p["qualy"] and p["fecha"][:10] >= desde_año:
            cuadro[p["ganadorId"]] += 1
            cuadro[p["perdedorId"]] += 1
    out = {}
    for tour in ("ATP", "WTA"):
        cand = [t for t, st in estado.items() if tour_de.get(t) == tour and st["nivel"] is not None
                and ultimo.get(t, "") >= desde_activo and cuadro[t] >= MIN_CUADRO]
        top = sorted(cand, key=lambda t: -estado[t]["nivel"])[:TOP]
        filas = []
        for i, t in enumerate(top, 1):
            st = estado[t]
            fams = {n: burbujas.momentum(st["fam"][n], n, len(st["res"])) for n in motor.FAMILIAS}
            filas.append({"rank": i, "jugador": nombre.get(t), "nivel": round(st["nivel"], 3),
                          "ultimoPartido": ultimo.get(t), "familias": fams})
        out[tour] = filas
    return out


def correr() -> dict:
    """Con el NIVEL OFICIAL del tenis: el Elo en la escala del SAD (§5). La
    conversión se mide con 2017-2020 sobre el nivel SAD de la ventana, y de ahí
    en adelante todo (q, riesgo, tercios, foto de hoy) usa el Elo convertido."""
    crudos = descarga.cargar()
    if len(crudos) < 2000:
        raise SystemExit("faltan datos: python -m backend.tenis.descarga")
    ps = a_motor(crudos)
    esc = elegir_escala(ps)
    sad = motor.construir(ps, escala_g=esc["elegida"], escala_margen=ESCALA_MARGEN)
    ext, fin_ext, conv = elo_como_nivel(ps, sad, AÑO_VALIDACION)
    previos = motor.construir(ps, escala_g=esc["elegida"], escala_margen=ESCALA_MARGEN, nivel_externo=ext)
    inv = defaultdict(lambda: defaultdict(int))
    for p in ps:
        inv[p["temporada"]][f"{p['tour']} {p['escalon']}"] += 1
    return {"parametros": {"nivel": "Elo en la escala del SAD (oficial, §5)", "conversion": conv,
                           "escalaG": esc, "escalaMargen": ESCALA_MARGEN, "minPartidos": MIN_PARTIDOS,
                           "midesDesde": AÑO_VALIDACION + 1},
            "inventario": {str(a): dict(v) for a, v in sorted(inv.items())},
            "estudio": estudiar(ps, previos),
            "hoy": hoy(ps, crudos, esc["elegida"], nivel_externo=ext, nivel_final=fin_ext)}


def texto(r: dict) -> str:
    L = ["TENIS · fase 0 · momentum sin cuotas (% de veces que se cumplió la lectura)", ""]
    e = r["parametros"]["escalaG"]
    c = r["parametros"]["conversion"]
    L.append(f"NIVEL OFICIAL: Elo en la escala del SAD · nivel = {c['nivelMedia']} + (Elo − {c['eloMedia']}) / "
             f"{c['puntosElo1Nivel']} (conversión con 2017-{AÑO_VALIDACION}); se mide desde {r['parametros']['midesDesde']}")
    L.append("partidos por año: " + " · ".join(f"{a}: {sum(v.values())}" for a, v in r["inventario"].items()))
    for tour, s in r["estudio"].items():
        L += ["", f"{tour} · {s['partidosMedidos']} partidos medidos · el de más nivel gana: "
              + " · ".join(f"{k} {v:.0%}" for k, v in s["aciertoNivel"].items())]
        L.append(f"  {'escalón':18s} " + "  ".join(f"{k}·{TRAMOS[k][0]} {TRAMOS[k][3]:26s}" for k in TRAMOS))
        for esc in ("todos", "Grand Slam", "cuadro principal", "qualy"):
            celdas = []
            for k in TRAMOS:
                t = s["tramos"][esc][k]
                tot = t["total"]
                celdas.append(("—" if not tot["n"] else f"{tot['acierto']:.0%} ({tot['n']})") + (" ✓" if t["firme"] else ""))
            L.append(f"  {esc:18s} " + "  ".join(f"{c:>35s}" for c in celdas))
        L.append("  por año (todos): " + " | ".join(
            f"{k} " + " ".join(f"{a[2:]}:{v['cumple'] / v['n']:.0%}" for a, v in s["tramos"]["todos"][k]["porAño"].items() if v["n"])
            for k in TRAMOS))
    L += ["", "✓ = firme: en TODOS sus años con 30+ casos acertó 65 % o más.", ""]
    for tour, filas in r["hoy"].items():
        L.append(f"HOY · {tour} · los {TOP} de mayor nivel (activos en {ACTIVO_DIAS} días, {MIN_CUADRO}+ partidos de cuadro principal en el año)")
        for f in filas:
            partes = []
            for n, m in f["familias"].items():
                if not m["abierta"]:
                    continue
                ex = m.get("extremo") or {}
                marca = " 🔴 EXTREMO" if ex.get("activo") else " 🟠 cerca del extremo" if ex.get("cerca") else ""
                rp = " 🟡 récord del período" if (m.get("recordPeriodo") or {}).get("activo") else ""
                pos = m.get("posicion") or {}
                partes.append(f"{n} {m['racha']} seguidas, K {m['k']}"
                              + (f" (sobre el {pos['percentilK']} de cada 100 cortes, {pos['kSobreMediana']}× la mediana)" if pos else "")
                              + marca + rp)
            L.append(f"  {f['rank']:2d} {f['jugador'][:24]:24s} nivel {f['nivel']:.2f} · último {f['ultimoPartido']} · " + "; ".join(partes))
        L.append("")
    return "\n".join(L)


def main():
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    r = correr()
    with open(os.path.join(descarga.carpeta(), "fase0.json"), "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    t = texto(r)
    with open(os.path.join(descarga.carpeta(), "fase0.txt"), "w") as f:
        f.write(t + "\n")
    print(t)


if __name__ == "__main__":
    main()
