"""El backtest de la forma propia contra la cuota detecta lo que la casa no
cobra, no inventa nada sin efecto y no mira el resultado que evalúa.

    python -m backend.test_backtest_forma_cuota
"""
import random
import sys
from collections import deque

from backend.backtest_forma_cuota import AMISTOSOS, ULTIMOS, casos, evaluar, formas

fallos = 0
SENAL = "favorito con la forma 20+ pts debajo de la casa"


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _fecha(d: int) -> str:
    return f"{2018 + d // 360}-{1 + (d // 30) % 12:02d}-{1 + d % 30:02d}T18:00:00Z" if d % 30 < 28 else \
        f"{2018 + d // 360}-{1 + (d // 30) % 12:02d}-28T20:00:00Z"


def simular(equipos: int, jornadas: int, efecto: float, casa_sabe: bool, semilla: int):
    """Liga sintética. P(gana el local) sale de la calidad; la casa la sabe.
    Con efecto: el favorito cuya forma de 10 está 20+ pts debajo de su probabilidad
    gana `efecto` menos (pasa a empate). `casa_sabe`: la cuota ya lo descuenta."""
    rnd = random.Random(semilla)
    q = {t: rnd.uniform(-1.2, 1.2) for t in range(1, equipos + 1)}
    hist = {t: [] for t in q}
    forma = {t: deque(maxlen=ULTIMOS) for t in q}
    cuotas, fx = {}, 1
    for j in range(jornadas):
        ts = list(q)
        rnd.shuffle(ts)
        for k in range(0, len(ts) - 1, 2):
            L, V = ts[k], ts[k + 1]
            d = q[L] - q[V] + 0.3
            pl = min(0.88, max(0.05, 0.45 + 0.28 * d))
            pv = min(0.88, max(0.05, 0.28 - 0.22 * d))
            pe = 1 - pl - pv
            real = [pl, pe, pv]
            for lado, p_i in ((L, 0), (V, 2)):
                if real[p_i] >= 0.5 and len(forma[lado]) == ULTIMOS:
                    fg = sum(1 for r in forma[lado] if r == "W") / ULTIMOS
                    if fg - [pl, pe, pv][p_i] <= -0.20 and efecto:
                        real[p_i] -= efecto
                        real[1] += efecto
            cuotas[fx] = (tuple(real) if casa_sabe else (pl, pe, pv)) + (6, 0.05)
            x = rnd.random()
            gl, gv = (1, 0) if x < real[0] else (1, 1) if x < real[0] + real[1] else (0, 1)
            fecha = _fecha(j * 4)
            liga = 667 if j % 25 == 0 else 39
            hist[L].append({"fixtureId": fx, "fecha": fecha, "condicion": "Local", "rivalId": V, "ligaId": liga,
                            "golesFavor": gl, "golesContra": gv})
            hist[V].append({"fixtureId": fx, "fecha": fecha, "condicion": "Visita", "rivalId": L, "ligaId": liga,
                            "golesFavor": gv, "golesContra": gl})
            if liga not in AMISTOSOS:
                forma[L].append("W" if gl > gv else "D" if gl == gv else "L")
                forma[V].append("W" if gv > gl else "D" if gv == gl else "L")
            fx += 1
    return hist, cuotas


def _senal(r, nombre=SENAL):
    return next(s for s in r["senales"] if s["senal"] == nombre)


def main():
    # ── 1 · sin fuga ─────────────────────────────────────────────────────────
    hist, cuotas = simular(20, 60, 0.0, False, semilla=1)
    f0 = formas(hist)
    t = 1
    fila = next(f for f in hist[t][30:] if f["ligaId"] not in AMISTOSOS)
    fila["golesFavor"], fila["golesContra"] = (0, 4) if fila["golesFavor"] >= fila["golesContra"] else (4, 0)
    f1 = formas(hist)
    k = (fila["fixtureId"], t)
    check("el resultado del partido evaluado no cambia su forma previa",
          k in f0 and all(f0[k][c] == f1[k][c] for c in ("formaGana", "formaNoPierde", "formaAnota", "formaRecibe")),
          (f0.get(k), f1.get(k)))
    check("pero sí el resultado que se evalúa", f0[k]["gana"] != f1[k]["gana"] or f0[k]["empata"] != f1[k]["empata"])
    dos = {1: [{"fixtureId": i, "fecha": "2025-01-01T12:00:00Z" if i == 11 else f"2024-0{1 + i // 9}-{1 + i % 9:02d}T12:00:00Z",
                "condicion": "Local", "rivalId": 2, "ligaId": 39, "golesFavor": 1, "golesContra": 0} for i in range(10)]
           + [{"fixtureId": 11, "fecha": "2025-01-01T12:00:00Z", "condicion": "Local", "rivalId": 2, "ligaId": 39,
               "golesFavor": 0, "golesContra": 3},
              {"fixtureId": 12, "fecha": "2025-01-01T20:00:00Z", "condicion": "Local", "rivalId": 2, "ligaId": 39,
               "golesFavor": 1, "golesContra": 0}]}
    fd = formas(dos)
    check("un partido del mismo día no entra en la forma del otro", fd[(12, 1)]["formaGana"] == 1.0, fd.get((12, 1)))
    check("los amistosos no se evalúan", not any(v["liga"] in AMISTOSOS for v in f0.values()))

    # ── 2 · la cuota del lado correcto, y las copas fuera ────────────────────
    cs = casos(hist, cuotas)
    bien = all(c["p"] == cuotas[c["fixtureId"]][0 if c["fav"]["local"] else 2] for c in cs)
    visitantes = sum(1 for c in cs if not c["fav"]["local"])
    check("la probabilidad del favorito es la de su lado (local → pL, visitante → pV)",
          bool(cs) and bien and visitantes > 0, (len(cs), visitantes))
    check("todos los casos son favoritos de la casa (≥ 50 %)", all(c["p"] >= 0.5 for c in cs))
    fuera = {cs[0]["fixtureId"]}
    check("lo que se excluye (copas nacionales) no entra", all(c["fixtureId"] not in fuera for c in casos(hist, cuotas, fuera)))

    # ── 3 · detecta lo que la casa no cobra, no inventa y respeta lo que cobra ─
    hist, cuotas = simular(60, 400, 0.20, False, semilla=11)
    s = _senal(evaluar(casos(hist, cuotas)))
    check("con el efecto plantado y la casa sin saberlo: separa, negativo y se repite",
          s["diferencia"].get("separa") and s["diferencia"]["diferencia"] < 0 and s["seRepite"], s["diferencia"])
    hist, cuotas = simular(60, 400, 0.20, True, semilla=11)
    s = _senal(evaluar(casos(hist, cuotas)))
    check("si la casa ya lo cobra, no separa", not s["diferencia"].get("separa"), s["diferencia"])
    hist, cuotas = simular(60, 400, 0.0, False, semilla=12)
    r = evaluar(casos(hist, cuotas))
    check("sin efecto, la señal no se repite (no inventa)", not _senal(r)["seRepite"], _senal(r)["diferencia"])
    check("sin efecto, ninguna señal queda firme", not r["firmes"], r["firmes"])

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
