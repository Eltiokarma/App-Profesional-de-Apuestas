"""El backtest del rival que resiste detecta un efecto plantado contra el
nivel, contra la casa y liga por liga; no inventa uno; no mira el resultado
que evalúa; y consulta las copas nacionales en lotes.

    python -m backend.test_backtest_rival_resiste
"""
import random
import sys
from collections import deque

from backend import backtest_rival_resiste as rr

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _fecha(d: int) -> str:
    return f"{2015 + d // 336}-{1 + (d // 28) % 12:02d}-{1 + d % 28:02d}T18:00:00Z"


def simular(ligas: int, por_liga: int, jornadas: int, efecto: float, casa_sabe: bool, semilla: int):
    """Ligas sintéticas. Con efecto: si el rival del favorito (0,5+ de nivel) no
    perdió 6+ de sus últimos 10, el favorito gana `efecto` menos (pasa a empate)."""
    rnd = random.Random(semilla)
    hist, cuotas, fx = {}, {}, 1
    nivel = {}
    for lg in range(ligas):
        equipos = [lg * 100 + i for i in range(1, por_liga + 1)]
        for t in equipos:
            nivel[t] = rnd.uniform(1.0, 3.8)
            hist[t] = {"filas": [], "niveles": [{"fecha": "2000-01-01T00:00:00Z", "nivel": nivel[t]}]}
        ventana = {t: deque(maxlen=10) for t in equipos}
        for j in range(jornadas):
            orden = equipos[:]
            rnd.shuffle(orden)
            for k in range(0, len(orden) - 1, 2):
                L, V = orden[k], orden[k + 1]
                d = nivel[L] - nivel[V] + 0.3
                pl = min(0.85, max(0.06, 0.45 + 0.22 * d))
                pv = min(0.85, max(0.06, 0.28 - 0.18 * d))
                real = [pl, 1 - pl - pv, pv]
                for fav, riv, i in ((L, V, 0), (V, L, 2)):
                    w = ventana[riv]
                    if efecto and nivel[fav] - nivel[riv] >= 0.5 and len(w) == 10 and sum(w) >= 6:
                        quita = min(efecto, real[i] - 0.02)
                        real[i] -= quita
                        real[1] += quita
                cuotas[fx] = (tuple(real) if casa_sabe else (pl, 1 - pl - pv, pv)) + (6, 0.05)
                x = rnd.random()
                gl, gv = (1, 0) if x < real[0] else (1, 1) if x < real[0] + real[1] else (0, 1)
                fecha = _fecha(j * 3)
                hist[L]["filas"].append({"fixtureId": fx, "fecha": fecha, "condicion": "Local", "rivalId": V,
                                         "ligaId": 1000 + lg, "golesFavor": gl, "golesContra": gv})
                hist[V]["filas"].append({"fixtureId": fx, "fecha": fecha, "condicion": "Visita", "rivalId": L,
                                         "ligaId": 1000 + lg, "golesFavor": gv, "golesContra": gl})
                ventana[L].append(1 if gl >= gv else 0)
                ventana[V].append(1 if gv >= gl else 0)
                fx += 1
    return hist, cuotas


def _s(r, clave="forma"):
    return next(s for s in r["senales"] if s["senal"] == clave)


def main():
    # ── 1 · sin fuga ─────────────────────────────────────────────────────────
    hist, _ = simular(1, 10, 40, 0.0, False, semilla=1)
    a = rr.lados(hist)
    t = 1
    fila = hist[t]["filas"][25]
    fila["golesFavor"], fila["golesContra"] = (0, 5) if fila["golesFavor"] >= fila["golesContra"] else (5, 0)
    b = rr.lados(hist)
    k = (fila["fixtureId"], t)
    check("el resultado evaluado no cambia lo que se sabía antes (forma, racha, récord, perfil)",
          all(a[k][c] == b[k][c] for c in ("formaNoPierde", "racha", "record", "perfilNoPierde")), (a[k], b[k]))
    check("el nivel es el ESTRICTAMENTE anterior", rr._nivel_antes(["2025-01-08"], [2.0], "2025-01-08") is None)
    amist = {1: {"filas": [{"fixtureId": 1, "fecha": "2025-01-01", "condicion": "Local", "rivalId": 2, "ligaId": 667,
                            "golesFavor": 1, "golesContra": 0}], "niveles": []}}
    check("los amistosos no se evalúan", not rr.lados(amist))

    # ── 2 · detecta, no inventa, y respeta lo que la casa ya cobra ───────────
    hist, cuotas = simular(8, 16, 120, 0.15, False, semilla=11)
    r = rr.evaluar(rr.casos(hist, cuotas))
    n = _s(r)["nivel"]
    check("con el efecto plantado: contra el nivel separa, en el sentido del candidato",
          n.get("separa") and n["residuo"] > 0.05, n)
    ep = _s(r)["nivelPorEpoca"]
    check("y en las dos épocas", all(e.get("separa") and e["residuo"] > 0 for e in ep), ep)
    lg = _s(r)["porLiga"]
    check("y en la mayoría de las ligas (prueba del signo)", lg["conMasDerrotas"] >= 7 and lg["pSigno"] < 0.1, lg)
    c = _s(r)["casa"]
    check("con la casa sin saberlo, contra la casa también separa", c.get("separa") and c["residuo"] > 0, c)

    hist, cuotas = simular(8, 16, 120, 0.15, True, semilla=11)
    c = _s(rr.evaluar(rr.casos(hist, cuotas)))["casa"]
    check("si la casa ya lo cobra, contra la casa no separa", not c.get("separa"), c)

    hist, cuotas = simular(8, 16, 120, 0.0, False, semilla=12)
    r0 = rr.evaluar(rr.casos(hist, cuotas))
    n0 = _s(r0)["nivel"]
    check("sin efecto, contra el nivel no separa (no inventa)", not n0.get("separa"), n0)
    check("sin efecto, las ligas no se inclinan", _s(r0)["porLiga"]["pSigno"] > 0.05, _s(r0)["porLiga"])

    # ── 3 · las copas se consultan en lotes ──────────────────────────────────
    import backend.analisis.escala as escala
    lotes = []
    original = escala.copas_nacionales
    escala.copas_nacionales = lambda ids: (lotes.append(len(ids)) or {ids[0]: "copa"})
    try:
        fuera = rr._copas(list(range(1, 1301)))
    finally:
        escala.copas_nacionales = original
    check("las copas nacionales se piden en lotes de 500 (no una consulta gigante que falla callada)",
          lotes == [500, 500, 300] and fuera == {1, 501, 1001}, (lotes, fuera))

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
