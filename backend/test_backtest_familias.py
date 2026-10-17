"""El backtest de las otras familias detecta un efecto real y no inventa uno.

    python -m backend.test_backtest_familias
"""
import random
import sys

from backend.backtest_familias import MIN_PREFIJO, comparar, observar_equipo, perfil_dc

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _filas(resultados: list[tuple[int, int]], local=True) -> list[dict]:
    return [{"fecha": f"2025-{1 + i // 28:02d}-{1 + i % 28:02d}T20:00:00Z",
             "condicion": "Local" if (local or i % 2 == 0) else "Visita",
             "golesFavor": gf, "golesContra": gc} for i, (gf, gc) in enumerate(resultados)]


def _solo(obs, familia, ambito="total"):
    return [o for o in obs if o[0] == familia and o[1] == ambito]


def main():
    # ── el largo y el récord se reconstruyen SOLO con lo anterior ──────────
    secuencia = [(1, 0)] * 3 + [(0, 1)] + [(1, 0)] * 2 + [(0, 1)] + [(1, 0)] * 4 + [(0, 1)] * 2 + [(1, 1)] * 3
    obs = _solo(observar_equipo(1, _filas(secuencia)), "gana1+")
    check("solo se evalúa con al menos MIN_PREFIJO partidos previos", len(obs) == len(secuencia) - MIN_PREFIJO,
          len(obs))
    primero = obs[0]   # partido 10: venía de 3 victorias (7-9), 8 victorias en los 10 previos
    check("la racha abierta y su valor salen del partido anterior (3 victorias)",
          primero[2] is True and primero[3] == 2, primero)
    check("sin 3 rachas previas del mismo valor no hay récord", primero[4] == -1, primero)
    check("la frecuencia propia es la del prefijo, no la de toda la historia",
          abs(primero[5] - (8 + 1) / (10 + 2)) < 1e-9, primero[5])
    check("y lo que pasó es el partido siguiente (volvió a ganar: la racha sigue)", primero[6] is True, primero)
    corte = obs[1]     # partido 11: venía de 4 victorias y perdió
    check("la racha de 4 se corta en el partido 11", corte[3] == 3 and corte[6] is False, corte)

    # ── sin efecto: resultados independientes → no aporta ──────────────────
    rnd = random.Random(7)
    obs_iid = []
    for team in range(300):
        res = [(1, 0) if rnd.random() < 0.45 else (0, 0) if rnd.random() < 0.5 else (0, 1) for _ in range(120)]
        obs_iid += _solo(observar_equipo(team, _filas(res)), "noPierde")
    c = comparar(obs_iid)
    check("con resultados independientes el largo y el récord NO aportan (intervalo cruza cero)",
          c.get("aporta") is False and c["ic95"][0] <= 0 <= c["ic95"][1] + 0.002, c)

    # ── con efecto: las rachas de «no pierde» se cortan al llegar a 3 ───────
    obs_ef = []
    for team in range(300):
        res, racha = [], 0
        for _ in range(120):
            corta = racha >= 3 and rnd.random() < 0.8
            no_pierde = (not corta) and rnd.random() < 0.65
            res.append((1, 0) if no_pierde else (0, 1))
            racha = racha + 1 if no_pierde else 0
        obs_ef += _solo(observar_equipo(team, _filas(res)), "noPierde")
    c2 = comparar(obs_ef)
    check("con un reventón plantado al tercer partido, el método lo detecta (aporta, intervalo bajo cero)",
          c2.get("aporta") is True, c2)

    # ── de local y de visita se miran por separado ─────────────────────────
    alterna = [(1, 0), (0, 1)] * 20
    obs_l = _solo(observar_equipo(9, _filas(alterna, local=False)), "gana1+", "local")
    check("el ámbito local solo mira partidos de local (ahí siempre gana: la racha siempre sigue)",
          obs_l and all(o[6] for o in obs_l if o[2]), obs_l[:2])

    # ── el perfil de doble oportunidad en la condición de HOY ─────────────
    # de local: G E G P G G G G (racha de 4 sin perder, récord previo 3 con 3 cortadas)
    loc = [(1, 0), (1, 1), (2, 0), (0, 1), (1, 0), (0, 1), (2, 1), (1, 1), (0, 2),
           (1, 0), (1, 1), (2, 2), (1, 0)]
    filas = [{"fecha": f"2025-02-{i + 1:02d}T20:00:00Z", "condicion": "Local", "golesFavor": a, "golesContra": b}
             for i, (a, b) in enumerate(loc)]
    filas += [{"fecha": f"2025-03-{i + 1:02d}T20:00:00Z", "condicion": "Visita", "golesFavor": 0, "golesContra": 3}
              for i in range(5)]
    pl = perfil_dc(filas, True)
    check("el perfil de local cuenta solo los de local (13) y no pierde 10 de 13",
          pl["partidos"] == 13 and abs(pl["noPierde"] - (10 + 1) / (13 + 2)) < 1e-4, pl)
    check("la burbuja de «no pierde» abierta es de 4 y supera su récord de 3", pl["burbuja"] == 4 and pl["record"] == 2, pl)
    pv = perfil_dc(filas, False)
    check("de visita perdió las 5: no pierde casi nunca y su burbuja es negativa (−5)",
          pv["noPierde"] < 0.2 and pv["burbuja"] == -5, pv)

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
