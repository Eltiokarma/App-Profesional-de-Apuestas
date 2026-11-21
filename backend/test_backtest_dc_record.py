"""El backtest de la racha sin perder en récord detecta un efecto real, no
inventa uno y no mira el resultado del partido que evalúa.

    python -m backend.test_backtest_dc_record
"""
import random
import sys

from backend.backtest_dc_record import (MIN_PREFIJO, EstadoDC, _nivel_antes, contra_mercado, correr,
                                        observaciones)
from backend.backtest_familias import perfil_dc

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _fecha(i: int) -> str:
    return f"{2015 + i // 336}-{1 + (i // 28) % 12:02d}-{1 + i % 28:02d}T20:00:00Z"


RIVALES = {9001 + k: 1.0 + 0.25 * k for k in range(8)}      # niveles fijos de los rivales


def _historias(n_equipos: int, partidos: int, efecto: float, semilla: int, amistoso_cada: int = 0):
    """Equipos sintéticos. P(gana) sale de la ventaja de nivel; con la racha sin
    perder de la condición en récord, `efecto` de la victoria pasa a empate.
    Devuelve (historias, probabilidad verdadera de ganar por fixture)."""
    rnd = random.Random(semilla)
    hist, verdad = {}, {}
    fx = 1
    for t in range(1, n_equipos + 1):
        nivel = rnd.uniform(1.5, 3.5)
        estados = {"Local": EstadoDC(), "Visita": EstadoDC()}
        filas = []
        for i in range(partidos):
            cond = "Local" if i % 2 == 0 else "Visita"
            rid = rnd.choice(list(RIVALES))
            v = nivel - RIVALES[rid] + (0.3 if cond == "Local" else -0.3)
            pg = min(0.9, max(0.1, 0.45 + 0.25 * v))
            pe = 0.27 * (1 - pg) + 0.12
            e = estados[cond]
            en_rec = e.burbuja() > 0 and e.record() >= 1
            if en_rec:
                pg, pe = pg - efecto, pe + efecto
            x = rnd.random()
            gf, gc = (1, 0) if x < pg else (1, 1) if x < pg + pe else (0, 1)
            liga = 667 if amistoso_cada and i % amistoso_cada == 0 else 39
            filas.append({"fixtureId": fx, "fecha": _fecha(i), "condicion": cond, "rivalId": rid,
                          "ligaId": liga, "golesFavor": gf, "golesContra": gc})
            # como la cuota real: (gana el local, empate, gana el visitante)
            verdad[fx] = (pg, pe, 1 - pg - pe) if cond == "Local" else (1 - pg - pe, pe, pg)
            e.sumar(gf >= gc)
            fx += 1
        # un nivel por partido, fechado el día del partido (ya lo trae: no se usa para ese partido)
        hist[t] = {"filas": filas, "niveles": [{"fecha": _fecha(i), "nivel": nivel} for i in range(partidos)]}
    for rid, nv in RIVALES.items():
        hist[rid] = {"filas": [], "niveles": [{"fecha": "2000-01-01T00:00:00Z", "nivel": nv}]}
    return hist, verdad


def main():
    # ── 1 · la racha incremental es la misma que perfil_dc ──────────────────
    rnd = random.Random(3)
    iguales = True
    for _ in range(300):
        serie = [rnd.choice([(1, 0), (1, 1), (0, 1), (2, 0)]) for _ in range(rnd.randint(1, 60))]
        filas = [{"fecha": _fecha(i), "condicion": "Local", "golesFavor": g, "golesContra": c}
                 for i, (g, c) in enumerate(serie)]
        e = EstadoDC()
        for g, c in serie:
            e.sumar(g >= c)
        p = perfil_dc(filas, True)
        if (e.burbuja(), e.record(), e.partidos) != (p["burbuja"], p["record"], p["partidos"]):
            iguales = False
            break
    check("la racha y el récord incrementales coinciden con perfil_dc (300 secuencias)", iguales)

    # ── 2 · sin fuga ─────────────────────────────────────────────────────────
    hist, _ = _historias(3, 80, 0.0, semilla=1)
    base = {(o["team"], o["fixtureId"]): o for o in observaciones(hist)}
    t, fila = 1, hist[1]["filas"][40]
    fila["golesFavor"], fila["golesContra"] = (0, 3) if fila["golesFavor"] >= fila["golesContra"] else (3, 0)
    cambiado = {(o["team"], o["fixtureId"]): o for o in observaciones(hist)}
    k = (t, fila["fixtureId"])
    check("el resultado del partido evaluado no cambia lo que se sabía antes",
          k in base and all(base[k][c] == cambiado[k][c] for c in ("racha", "enRecord", "ventaja")),
          (base.get(k), cambiado.get(k)))
    check("el nivel del día del partido no se usa: el previo es el ESTRICTAMENTE anterior",
          _nivel_antes(["2025-01-01", "2025-01-08"], [1.0, 2.0], "2025-01-08") == 1.0
          and _nivel_antes(["2025-01-08"], [2.0], "2025-01-08") is None)
    check("solo se evalúa con MIN_PREFIJO partidos previos en la condición",
          all(o["fecha"] >= _fecha(2 * MIN_PREFIJO)[:10] for o in base.values()))

    hist, _ = _historias(2, 60, 0.0, semilla=2, amistoso_cada=5)
    ligas = {o["liga"] for o in observaciones(hist)}
    check("los amistosos cuentan en la historia pero no se evalúan", 667 not in ligas and ligas == {39}, ligas)

    # ── 3 · detecta un efecto plantado y no inventa uno ─────────────────────
    hist, verdad = _historias(150, 240, 0.15, semilla=11)
    r = correr(hist)
    e = r["estandarizado"]
    check("con el efecto plantado (−15 pts de victoria en récord) el residuo es positivo y separa",
          e.get("separa") and e["ic95"][0] > 0.05, e)
    check("y se repite en las dos épocas", all(x["estandarizado"].get("ic95", [0])[0] > 0 for x in r["porEpoca"]),
          r["porEpoca"])

    hist0, verdad0 = _historias(150, 240, 0.0, semilla=12)
    e0 = correr(hist0)["estandarizado"]
    check("sin efecto, el intervalo contiene el cero (no inventa)", e0["ic95"][0] <= 0 <= e0["ic95"][1], e0)

    # ── 4 · contra la cuota ──────────────────────────────────────────────────
    obs = observaciones(hist)
    cobra = {fx: (*p, 5, 0.05) for fx, p in verdad.items()}              # la casa sabe el efecto
    m1 = contra_mercado(obs, cobra)["residuo"]
    check("si la casa ya cobra el efecto, el residuo contra la cuota no separa",
          m1["ic95"][0] <= 0 <= m1["ic95"][1], m1)
    _, sin_efecto = _historias(150, 240, 0.0, semilla=11)               # misma fuerza, sin el efecto
    no_cobra = {fx: (*sin_efecto[fx], 5, 0.05) for fx in verdad}
    m2 = contra_mercado(obs, no_cobra)["residuo"]
    check("si la casa no lo cobra, el residuo contra la cuota es positivo y separa", m2["ic95"][0] > 0.05, m2)
    check("con pocas cuotas no se compara", "porTramo" not in contra_mercado(obs, {}), "")

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
