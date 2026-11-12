"""Tenis · fase 0: la descarga recorta bien (sin walkovers ni retiros, el
margen con el signo del resultado), el lado del ganador no se filtra y el
estudio mide los tramos por escalón (docs/TENIS_FASE0.md).

Sin red: todo con datos SINTÉTICOS.

    python -m backend.test_tenis_fase0
"""
from __future__ import annotations

import math
import random
import sys

from backend.nba import motor
from backend.tenis import descarga, fase0

fallas = 0


def check(nombre, ok, detalle=""):
    global fallas
    print(("OK  " if ok else "FALLA ") + nombre + ("" if ok else f" -> {detalle}"))
    fallas += 0 if ok else 1


def _comp(i, estado, a, b, sa, sb, gana_a=True, ronda="Round 1"):
    return {"id": str(i), "date": "2024-04-10T10:00Z", "round": {"displayName": ronda},
            "status": {"type": {"name": estado, "completed": True}},
            "competitors": [
                {"id": str(a), "winner": gana_a, "athlete": {"displayName": f"J{a}"}, "linescores": [{"value": v} for v in sa]},
                {"id": str(b), "winner": not gana_a, "athlete": {"displayName": f"J{b}"}, "linescores": [{"value": v} for v in sb]}]}


def liga(semilla=4, jugadores=40, años=range(2017, 2024)):
    """Jugadores con fuerza fija; ganar depende de la diferencia de fuerza."""
    rnd = random.Random(semilla)
    fuerza = {j: rnd.gauss(0, 1) for j in range(1, jugadores + 1)}
    ps, i = [], 1
    for año in años:
        for semana in range(40):
            for _ in range(30):
                a, b = rnd.sample(range(1, jugadores + 1), 2)
                pa = 1 / (1 + math.exp(-(fuerza[a] - fuerza[b]) * 1.5))
                w, l = (a, b) if rnd.random() < pa else (b, a)
                ps.append({"id": i, "fecha": f"{año}-{1 + semana // 4:02d}-{1 + (semana % 4) * 7:02d}T{i % 24:02d}:00Z",
                           "tour": "ATP" if i % 2 else "WTA", "torneo": "T", "torneoId": "t", "grandSlam": semana % 10 == 0,
                           "ronda": "Qualifying 1st Round" if semana % 3 == 0 else "Round 1", "qualy": semana % 3 == 0,
                           "ganadorId": w, "ganador": f"J{w}", "perdedorId": l, "perdedor": f"J{l}",
                           "juegosGanador": 12 + rnd.randrange(3), "juegosPerdedor": 4 + rnd.randrange(8), "sets": 2})
                i += 1
    return sorted(ps, key=lambda p: (p["fecha"], p["id"]))


def main() -> int:
    crudo = {"events": [{"name": "Monte-Carlo", "id": "1", "major": False, "groupings": [
        {"grouping": {"displayName": "Men's Singles"}, "competitions": [
            _comp(1, "STATUS_FINAL", 10, 11, [6, 6], [3, 4]),
            _comp(2, "STATUS_RETIRED", 12, 13, [6, 3], [3, 2]),
            _comp(3, "STATUS_WALKOVER", 14, 15, [], []),
            _comp(4, "STATUS_FINAL", 16, 17, [6, 6, 7], [7, 7, 6], gana_a=False),     # gana 17 con 20 juegos a 18
            _comp(5, "STATUS_FINAL", 18, 19, [7, 0, 7], [6, 6, 6], ronda="Qualifying 2nd Round"),  # gana 18 con 14 a 18
        ]},
        {"grouping": {"displayName": "Men's Doubles"}, "competitions": [_comp(9, "STATUS_FINAL", 20, 21, [6, 6], [1, 1])]},
        {"grouping": {"displayName": "Women's Singles"}, "competitions": [_comp(6, "STATUS_FINAL", 30, 31, [6, 6], [0, 0])]},
    ]}]}
    rec = {p["id"]: p for p in descarga.recortar(crudo)}
    check("descarga: afuera los retiros, los walkover y los dobles", set(rec) == {1, 4, 5, 6}, sorted(rec))
    check("descarga: el ganador sale del flag, con sus juegos", rec[4]["ganadorId"] == 17 and rec[4]["juegosGanador"] == 20
          and rec[4]["juegosPerdedor"] == 19, rec[4])
    check("descarga: si el ganador hizo MENOS juegos, se le pone uno más (el margen lleva el signo del resultado)",
          rec[5]["juegosGanador"] == 19 and rec[5]["juegosPerdedor"] == 18, rec[5])
    check("descarga: qualy y circuito", rec[5]["qualy"] and rec[6]["tour"] == "WTA" and rec[1]["tour"] == "ATP")

    ps = liga()
    m = fase0.a_motor(ps)
    loc_gana = sum(p["ptsLocal"] > p["ptsVisita"] for p in m) / len(m)
    check("a_motor: el ganador no queda siempre del mismo lado (≈ 50 %)", 0.45 < loc_gana < 0.55, loc_gana)
    check("a_motor: todo neutral (no hay localía en el tenis) y el escalón viaja",
          all(p["neutral"] for p in m) and {p["escalon"] for p in m} == {"Grand Slam", "cuadro principal", "qualy"})
    prev = motor.construir(m, escala_g=5.0, escala_margen=fase0.ESCALA_MARGEN)
    check("motor: sin localía no hay contramano ni K de condición",
          all(not d[l]["contramano"] and d[l]["kCond"] == 0 for d in prev.values() for l in ("local", "visita")))
    est = fase0.estudiar(m, prev)
    check("estudio: el nivel acierta más que la moneda con fuerza real", est["ATP"]["aciertoNivel"]["todos"] > 0.55,
          est["ATP"]["aciertoNivel"])
    check("estudio: mide solo después del año de validación (sin mirar lo que eligió la escala)",
          all(int(a) > fase0.AÑO_VALIDACION for esc in est["ATP"]["tramos"].values() for t in esc.values() for a in t["porAño"]))
    check("estudio: los cuatro tramos por escalón", set(est["WTA"]["tramos"]) == {"todos", "Grand Slam", "cuadro principal", "qualy"}
          and all(set(v) == set("ABCD") for v in est["WTA"]["tramos"].values()))
    h = fase0.hoy(m, ps, 5.0)
    check("hoy: top por circuito con las dos familias", len(h["ATP"]) > 0 and set(h["ATP"][0]["familias"]) == set(motor.FAMILIAS))

    # ── las variantes del nivel (§4) ─────────────────────────────────────────
    v = [(6, 3, 4.0)] * 10 + [(3, 6, 2.0)] * 10
    check("nivel por rival: con todos los rivales iguales es la P de siempre",
          abs(motor.nivel_de([(6, 3, 2.0)] * 10 + [(3, 6, 2.0)] * 10, 2.0, True)
              - motor.nivel_de([(6, 3)] * 10 + [(3, 6)] * 10, 2.0)) < 1e-12)
    check("nivel por rival: ganarle a los fuertes (4) y perder con los flojos (2) vale más que 10/20",
          abs(motor.nivel_de(v, 2.0, True) - (3 * 40 / 60 + 2.0 * (-15 / 45) + 1)) < 1e-12, motor.nivel_de(v, 2.0, True))
    from backend.tenis import nivel as niv
    pozos = motor.construir(m, escala_g=2.0, escala_margen=fase0.ESCALA_MARGEN, **niv.VARIANTES["pozos"])
    todos = motor.construir(m, escala_g=2.0, escala_margen=fase0.ESCALA_MARGEN)
    check("pozos: la qualy no entra al nivel (cambia) pero sí a las burbujas (misma racha y signo)",
          any(pozos[i]["local"]["nivel"] != todos[i]["local"]["nivel"] for i in pozos)
          and all((pozos[i]["local"]["racha"], pozos[i]["local"]["signo"]) == (todos[i]["local"]["racha"], todos[i]["local"]["signo"])
                  for i in pozos))
    pe, fin = niv.elo(m)
    check("Elo (vara): sin nivel antes de 20 partidos y el fuerte termina arriba",
          all(pe[p["id"]]["local"]["nivel"] is None for p in m[:5]) and len(fin) == 40)

    ext, fin_ext, conv = niv.elo_como_nivel(m, todos)
    est_ext = {}
    sobre = motor.construir(m, escala_g=2.0, escala_margen=fase0.ESCALA_MARGEN, estado_final=est_ext,
                            nivel_externo=ext, nivel_final=fin_ext)
    i0 = next(p["id"] for p in m if ext[p["id"]]["local"] is not None and ext[p["id"]]["visita"] is not None)
    check("SAD sobre Elo: el nivel previo de cada lado ES el Elo convertido (y el del rival también)",
          sobre[i0]["local"]["nivel"] == ext[i0]["local"] and sobre[i0]["local"]["nivelRival"] == ext[i0]["visita"])
    check("SAD sobre Elo: las burbujas son las mismas (racha y signo no dependen del nivel)",
          all((sobre[i]["local"]["racha"], sobre[i]["local"]["signo"]) == (todos[i]["local"]["racha"], todos[i]["local"]["signo"])
              for i in sobre))
    check("SAD sobre Elo: la conversión tiene la escala del SAD y el estado final es el Elo de cada uno",
          conv["puntosElo1Nivel"] > 0 and all(est_ext[t]["nivel"] == x for t, x in fin_ext.items()))

    print("\nTODO OK" if not fallas else f"\n{fallas} FALLAS")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
