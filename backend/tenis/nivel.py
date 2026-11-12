"""Tenis · ¿con qué nivel? Las variantes del nivel, lado a lado (docs/TENIS_FASE0.md §4).

El nivel del motor mide FORMA (victorias y juegos), no la calidad del rival, y
en el tenis todos van al mismo pozo. Variantes:

  actual   · P = 3·victorias/20 (la de siempre)
  rival    · P pesa cada victoria por el nivel del rival (la P mira al rival como ya lo hace la q)
  pozos    · el nivel solo con partidos de cuadro principal (la qualy es «otra liga», como la liga B;
             la K y las burbujas siguen con todos los partidos)
  rival+pozos · las dos
  Elo      · la VARA de afuera (no es la teoría): el estándar del tenis, solo para comparar

Las tres pruebas: (1) el de más nivel gana (validación 2017-2020 y 2021 en
adelante); (2) los tramos A-D de momentum siguen firmes (2021 en adelante);
(3) la foto de hoy tiene sentido (el top 10 de cada circuito).

    python -m backend.tenis.nivel      # → tenis_data/nivel.txt y .json
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import date, timedelta

from backend.nba import motor
from backend.nba.ligas import TRAMOS
from backend.tenis import descarga, fase0

ESCALA_G = 2.0          # la elegida en la fase 0, igual para todas: así se compara solo la P
VARIANTES = {
    "actual": {},
    "rival": {"nivel_por_rival": True},
    "pozos": {"cuenta_nivel": lambda p: p["escalon"] != "qualy"},
    "rival+pozos": {"nivel_por_rival": True, "cuenta_nivel": lambda p: p["escalon"] != "qualy"},
}
ELO_INICIAL = 1500.0


def _acierto(ps, previos, desde, hasta=None, tour=None) -> dict:
    ok = n = 0
    for p in ps:
        a = p["temporada"]
        if a < desde or (hasta and a > hasta) or (tour and p["tour"] != tour):
            continue
        x, y = previos[p["id"]]["local"]["nivel"], previos[p["id"]]["visita"]["nivel"]
        if x is None or y is None or x == y:
            continue
        n += 1
        ok += (x > y) == (p["ptsLocal"] > p["ptsVisita"])
    return {"acierto": round(ok / n, 4) if n else None, "n": n}


def elo(ps: list[dict]) -> tuple[dict, dict]:
    """Elo con el k que decrece con los partidos jugados (el de FiveThirtyEight
    para tenis: 250/(n+5)^0.4). Devuelve el Elo PREVIO de cada lado y el final."""
    r, n, previos = defaultdict(lambda: ELO_INICIAL), defaultdict(int), {}
    for p in ps:
        a, b = p["localId"], p["visitaId"]
        previos[p["id"]] = {"local": {"nivel": r[a] if n[a] >= 20 else None},
                            "visita": {"nivel": r[b] if n[b] >= 20 else None}}
        ea = 1 / (1 + 10 ** ((r[b] - r[a]) / 400))
        sa = 1.0 if p["ptsLocal"] > p["ptsVisita"] else 0.0
        ka, kb = 250 / (n[a] + 5) ** 0.4, 250 / (n[b] + 5) ** 0.4
        r[a], r[b] = r[a] + ka * (sa - ea), r[b] + kb * ((1 - sa) - (1 - ea))
        n[a] += 1
        n[b] += 1
    return previos, dict(r)


def elo_como_nivel(ps: list[dict], previos_sad: dict) -> tuple[dict, dict, dict]:
    """El Elo en la ESCALA del nivel SAD, para que los umbrales del riesgo del
    fútbol (zona ±0,15, fuerte 0,45, favorito 0,5 / 1,0) signifiquen lo mismo:
    misma media y mismo desvío que el nivel SAD, medidos SOLO en 2017-2020
    (los años que se miden después no se miran). Devuelve el nivel previo de
    cada lado por partido, el final por jugador y la conversión usada."""
    pe, final = elo(ps)
    xs, ys = [], []
    for p in ps:
        if 2017 <= p["temporada"] <= fase0.AÑO_VALIDACION:
            for lado in ("local", "visita"):
                e, s_ = pe[p["id"]][lado]["nivel"], previos_sad[p["id"]][lado]["nivel"]
                if e is not None:
                    xs.append(e)
                if s_ is not None:
                    ys.append(s_)
    me, ms = sum(xs) / len(xs), sum(ys) / len(ys)
    de = (sum((x - me) ** 2 for x in xs) / len(xs)) ** 0.5
    ds = (sum((y - ms) ** 2 for y in ys) / len(ys)) ** 0.5
    a = lambda e: None if e is None else ms + (e - me) * ds / de  # noqa: E731
    ext = {i: {"local": a(v["local"]["nivel"]), "visita": a(v["visita"]["nivel"])} for i, v in pe.items()}
    return ext, {t: a(e) for t, e in final.items()}, {"eloMedia": round(me, 1), "eloDesvio": round(de, 1),
                                                     "nivelMedia": round(ms, 3), "nivelDesvio": round(ds, 3),
                                                     "puntosElo1Nivel": round(de / ds, 1)}


def _activos(crudos) -> tuple[dict, dict, set]:
    fin = date.fromisoformat(max(p["fecha"] for p in crudos)[:10])
    d_act, d_año = (fin - timedelta(days=fase0.ACTIVO_DIAS)).isoformat(), (fin - timedelta(days=365)).isoformat()
    nombre, tour, ultimo, cuadro = {}, {}, {}, defaultdict(int)
    for p in crudos:
        for i, nm in ((p["ganadorId"], p["ganador"]), (p["perdedorId"], p["perdedor"])):
            nombre[i], tour[i], ultimo[i] = nm, p["tour"], p["fecha"][:10]
            if not p["qualy"] and p["fecha"][:10] >= d_año:
                cuadro[i] += 1
    ok = {i for i in nombre if ultimo[i] >= d_act and cuadro[i] >= fase0.MIN_CUADRO}
    return nombre, tour, ok


def correr() -> dict:
    crudos = descarga.cargar()
    ps = fase0.a_motor(crudos)
    nombre, tour_de, activos = _activos(crudos)
    out = {}
    for nom, kw in VARIANTES.items():
        estado: dict[int, dict] = {}
        previos = motor.construir(ps, escala_g=ESCALA_G, escala_margen=fase0.ESCALA_MARGEN, estado_final=estado, **kw)
        est = fase0.estudiar(ps, previos)
        top = {}
        for tour in ("ATP", "WTA"):
            cand = [t for t in activos if tour_de[t] == tour and estado.get(t, {}).get("nivel") is not None]
            top[tour] = [nombre[t] for t in sorted(cand, key=lambda t: -estado[t]["nivel"])[:10]]
        out[nom] = {"validacion": _acierto(ps, previos, 2017, fase0.AÑO_VALIDACION),
                    "prueba": {t: _acierto(ps, previos, fase0.AÑO_VALIDACION + 1, tour=t) for t in ("ATP", "WTA")},
                    "tramos": {t: {k: {"acierto": v["total"]["acierto"], "n": v["total"]["n"], "firme": v["firme"]}
                                   for k, v in est[t]["tramos"]["todos"].items()} for t in ("ATP", "WTA")},
                    "top10": top}
    # EL ELO COMO NIVEL DEL SAD (decisión del usuario, §5): el mismo motor, las
    # mismas burbujas y el mismo riesgo, con el Elo en el lugar del nivel
    sad = motor.construir(ps, escala_g=ESCALA_G, escala_margen=fase0.ESCALA_MARGEN)
    ext, fin_ext, conv = elo_como_nivel(ps, sad)
    estado = {}
    previos = motor.construir(ps, escala_g=ESCALA_G, escala_margen=fase0.ESCALA_MARGEN, estado_final=estado,
                              nivel_externo=ext, nivel_final=fin_ext)
    est = fase0.estudiar(ps, previos)
    out["SAD sobre Elo"] = {
        "conversion": conv,
        "validacion": _acierto(ps, previos, 2017, fase0.AÑO_VALIDACION),
        "prueba": {t: _acierto(ps, previos, fase0.AÑO_VALIDACION + 1, tour=t) for t in ("ATP", "WTA")},
        "tramos": {t: {k: {"acierto": v["total"]["acierto"], "n": v["total"]["n"], "firme": v["firme"]}
                       for k, v in est[t]["tramos"]["todos"].items()} for t in ("ATP", "WTA")},
        "tramosPorEscalon": {t: {esc: {k: {"acierto": v["total"]["acierto"], "n": v["total"]["n"], "firme": v["firme"]}
                                       for k, v in tab.items()} for esc, tab in est[t]["tramos"].items()}
                             for t in ("ATP", "WTA")},
        "top10": {t: [nombre[i] for i in sorted((i for i in activos if tour_de[i] == t and fin_ext.get(i) is not None),
                                                key=lambda i: -fin_ext[i])[:10]] for t in ("ATP", "WTA")},
        "hoy": fase0.hoy(ps, crudos, ESCALA_G, nivel_externo=ext, nivel_final=fin_ext)}
    previos, final = elo(ps)
    out["Elo (vara)"] = {
        "validacion": _acierto(ps, previos, 2017, fase0.AÑO_VALIDACION),
        "prueba": {t: _acierto(ps, previos, fase0.AÑO_VALIDACION + 1, tour=t) for t in ("ATP", "WTA")},
        "tramos": None,
        "top10": {t: [nombre[i] for i in sorted((i for i in activos if tour_de[i] == t), key=lambda i: -final.get(i, 0))[:10]]
                  for t in ("ATP", "WTA")}}
    return out


def texto(r: dict) -> str:
    L = ["TENIS · ¿con qué nivel? (ESCALA_G 2 en todas; prueba = 2021 en adelante)", "",
         f"{'variante':14s} {'valid. 17-20':>12s} {'ATP 21+':>8s} {'WTA 21+':>8s}   tramos ATP (A B C D)            tramos WTA (A B C D)"]
    for nom, v in r.items():
        def tr(t):
            if not v["tramos"]:
                return "—"
            return " ".join(f"{v['tramos'][t][k]['acierto']:.0%}{'✓' if v['tramos'][t][k]['firme'] else ' '}" for k in TRAMOS)
        L.append(f"{nom:14s} {v['validacion']['acierto']:12.1%} {v['prueba']['ATP']['acierto']:8.1%} "
                 f"{v['prueba']['WTA']['acierto']:8.1%}   {tr('ATP'):30s}  {tr('WTA')}")
    L += ["", "✓ = firme (todos sus años con 30+ casos ≥ 65 %)", ""]
    se = r.get("SAD sobre Elo")
    if se:
        c = se["conversion"]
        L += [f"SAD sobre Elo · conversión: nivel = {c['nivelMedia']} + (Elo − {c['eloMedia']}) / {c['puntosElo1Nivel']}"
              f" (1 punto de nivel = {c['puntosElo1Nivel']} de Elo)", "  tramos por escalón (A B C D):"]
        for t in ("ATP", "WTA"):
            for esc, tab in se["tramosPorEscalon"][t].items():
                L.append(f"    {t} {esc:17s} " + " ".join(
                    (f"{tab[k]['acierto']:.0%}({tab[k]['n']}){'✓' if tab[k]['firme'] else ' '}" if tab[k]["n"] else "—") for k in TRAMOS))
        L.append("")
        for t in ("ATP", "WTA"):
            L.append(f"SAD sobre Elo · HOY · {t} · momentum de los 20 de mayor nivel")
            for f in se["hoy"][t]:
                partes = []
                for n, m in f["familias"].items():
                    if not m["abierta"]:
                        continue
                    ex, pos = m.get("extremo") or {}, m.get("posicion") or {}
                    marca = " 🔴 EXTREMO" if ex.get("activo") else " 🟠 cerca" if ex.get("cerca") else ""
                    rp = " 🟡 récord del período" if (m.get("recordPeriodo") or {}).get("activo") else ""
                    partes.append(f"{n} {m['racha']}, K {m['k']}" + (f" (sobre {pos['percentilK']}/100)" if pos else "") + marca + rp)
                L.append(f"  {f['rank']:2d} {f['jugador'][:22]:22s} nivel {f['nivel']:.2f} · " + "; ".join(partes))
            L.append("")
    for nom, v in r.items():
        L.append(f"{nom} · top 10 de hoy")
        for t in ("ATP", "WTA"):
            L.append(f"  {t}: " + ", ".join(v["top10"][t]))
    return "\n".join(L)


def main():
    r = correr()
    with open(os.path.join(descarga.carpeta(), "nivel.json"), "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    t = texto(r)
    with open(os.path.join(descarga.carpeta(), "nivel.txt"), "w") as f:
        f.write(t + "\n")
    print(t)


if __name__ == "__main__":
    main()
