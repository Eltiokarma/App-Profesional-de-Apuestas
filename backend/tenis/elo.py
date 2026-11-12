"""Tenis · el NIVEL OFICIAL: el Elo en la escala del SAD (docs/TENIS_FASE0.md §5).

Decisión del usuario (12/11/2026): en el tenis el nivel del SAD es el Elo,
pasado a la escala del nivel SAD. Entra en la q (el peso del rival en la K),
en el riesgo (zona, fuerte, favorito) y en los tercios; las burbujas, el
extremo y el récord del período quedan iguales encima.
"""
from __future__ import annotations

from collections import defaultdict

ELO_INICIAL = 1500.0


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


def elo_como_nivel(ps: list[dict], previos_sad: dict, hasta_validacion: int = 2020) -> tuple[dict, dict, dict]:
    """El Elo en la ESCALA del nivel SAD, para que los umbrales del riesgo del
    fútbol (zona ±0,15, fuerte 0,45, favorito 0,5 / 1,0) signifiquen lo mismo:
    misma media y mismo desvío que el nivel SAD, medidos SOLO en 2017-2020
    (los años que se miden después no se miran). Devuelve el nivel previo de
    cada lado por partido, el final por jugador y la conversión usada."""
    pe, final = elo(ps)
    xs, ys = [], []
    for p in ps:
        if 2017 <= p["temporada"] <= hasta_validacion:
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
