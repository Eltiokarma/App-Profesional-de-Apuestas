"""El backtest del favorito que viene fallando detecta una crisis plantada, no
inventa una donde no la hay, no mete el partido evaluado en su propia ventana
y deja afuera amistosos, copas y lo anterior a los años pedidos.

    python -m backend.test_backtest_favorito_falla
"""
import random
import sys

from backend import backtest_favorito_falla as ff

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def _fecha(d: int) -> str:
    return f"{2020 + d // 336}-{1 + (d // 28) % 12:02d}-{1 + d % 28:02d}T18:00:00Z"


def simular(ligas: int, por_liga: int, jornadas: int, crisis: float, semilla: int) -> dict:
    """Ligas sintéticas con nivel fijo. Con `crisis`, cada equipo entra a veces en una
    mala racha de 12 partidos en la que gana `crisis` menos (pasa a empate): el que
    viene fallando sigue fallando."""
    rnd = random.Random(semilla)
    hist, nivel, mala = {}, {}, {}
    fx = 1
    for lg in range(ligas):
        equipos = [lg * 100 + i for i in range(1, por_liga + 1)]
        for t in equipos:
            nivel[t] = rnd.uniform(1.0, 3.8)
            mala[t] = 0
            hist[t] = {"filas": [], "niveles": [{"fecha": "2000-01-01T00:00:00Z", "nivel": nivel[t]}]}
        for j in range(jornadas):
            orden = equipos[:]
            rnd.shuffle(orden)
            for t in equipos:
                if crisis and mala[t] == 0 and rnd.random() < 0.03:
                    mala[t] = 12
            for k in range(0, len(orden) - 1, 2):
                L, V = orden[k], orden[k + 1]
                d = nivel[L] - nivel[V] + 0.3
                pl = min(0.85, max(0.06, 0.45 + 0.22 * d))
                pv = min(0.85, max(0.06, 0.28 - 0.18 * d))
                real = [pl, 1 - pl - pv, pv]
                for t, i in ((L, 0), (V, 2)):
                    if mala[t]:
                        q = min(crisis, real[i] - 0.02)
                        real[i] -= q
                        real[1] += q
                x = rnd.random()
                gl, gv = (1, 0) if x < real[0] else (1, 1) if x < real[0] + real[1] else (0, 1)
                fecha = _fecha(j * 3)
                hist[L]["filas"].append({"fixtureId": fx, "fecha": fecha, "condicion": "Local", "rivalId": V,
                                         "ligaId": 1000 + lg, "golesFavor": gl, "golesContra": gv})
                hist[V]["filas"].append({"fixtureId": fx, "fecha": fecha, "condicion": "Visita", "rivalId": L,
                                         "ligaId": 1000 + lg, "golesFavor": gv, "golesContra": gl})
                fx += 1
            for t in equipos:
                mala[t] = max(0, mala[t] - 1)
    return hist


# 1. Una crisis plantada se detecta contra el nivel, en las dos épocas
h = simular(ligas=30, por_liga=20, jornadas=200, crisis=0.30, semilla=3)
r = ff.evaluar(ff.casos(h))
s = next(x for x in r["senales"] if x["senal"] == "n5-1.5")
check("crisis plantada: la fijada separa contra el nivel", s["nivel"].get("separa") and s["nivel"]["diferencia"] > 0,
      s["nivel"])
check("crisis plantada: se repite en las dos mitades", s["seRepite"], s["porEpoca"])
check("crisis plantada: la mayoría de las ligas va en el sentido",
      s["porLiga"]["enElSentido"] > s["porLiga"]["alReves"], s["porLiga"])

# 2. Sin crisis no inventa: ninguna variante separa y se repite
h0 = simular(ligas=30, por_liga=20, jornadas=200, crisis=0.0, semilla=5)
r0 = ff.evaluar(ff.casos(h0))
for s0 in r0["senales"]:
    if s0["fuente"] == "nivel":
        check(f"sin crisis: {s0['senal']} no se repite", not s0["seRepite"], s0["nivel"])

# 3. El partido evaluado no entra a su propia ventana (ni los del mismo día)
mini = {1: {"filas": [], "niveles": [{"fecha": "2000-01-01", "nivel": 3.5}]},
        2: {"filas": [], "niveles": [{"fecha": "2000-01-01", "nivel": 1.0}]}}
for i in range(6):
    gl = 1 if i < 5 else 0       # gana 5, pierde el sexto
    fe = f"2024-01-{10 + i:02d}T18:00:00Z"
    mini[1]["filas"].append({"fixtureId": 10 + i, "fecha": fe, "condicion": "Local", "rivalId": 2, "ligaId": 1,
                             "golesFavor": gl, "golesContra": 1 - gl})
    mini[2]["filas"].append({"fixtureId": 10 + i, "fecha": fe, "condicion": "Visita", "rivalId": 1, "ligaId": 1,
                             "golesFavor": 1 - gl, "golesContra": gl})
cs = [c for c in ff.casos(mini) if c["team"] == 1]
ult = cs[-1]
check("ventana: el sexto partido ve los 5 anteriores", ult["nivel5"] is not None and ult["fixtureId"] == 15)
check("ventana: la derrota del sexto no está en su residuo", ult["nivel5"] > 0, ult)

# 4. Amistosos fuera de casos y ventana; copas fuera de los casos; años
mini[1]["filas"].append({"fixtureId": 99, "fecha": "2024-01-20T18:00:00Z", "condicion": "Local", "rivalId": 2,
                         "ligaId": 667, "golesFavor": 0, "golesContra": 3})
cs2 = ff.casos(mini, excluir={14})
check("amistoso no es caso", all(c["fixtureId"] != 99 for c in cs2))
check("copa excluida no es caso", all(c["fixtureId"] != 14 for c in cs2))
check("desde: lo anterior no se evalúa", not ff.casos(mini, desde="2024-02-01"))
check("_desde 5 años", ff._desde(5, ff.date(2026, 11, 25)) == "2021-11-25")

# 5. Contra la casa: la cuota de cada previo arma su propia ventana
cuotas = {10 + i: (0.8, 0.12, 0.08) for i in range(6)}
cc = [c for c in ff.casos(mini, cuotas) if c["team"] == 1 and c["fixtureId"] == 15][0]
check("casa: residuo de 5 con la cuota", cc["casa5"] is not None and abs(cc["casa5"] - 5 * 0.2) < 1e-9, cc)

print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
sys.exit(1 if fallos else 0)
