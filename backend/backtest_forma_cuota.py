"""¿El equipo comparado contra SÍ MISMO avisa algo que la cuota no ve?
(pedido del usuario, 21/11/2026, tras Bayern 1-1 Köln)

El usuario: «si sabés que Bayern pierde 1 de cada 8, en esos 8 decime cuál es
el más bajo… el equipo puede compararse contra sí» y «no se consideraba que
fuese a responder el equipo rival». Bayern venía ganando 6 de sus últimos 10
oficiales y la casa le daba 87 %; Köln venía marcando en 8 de 10.

La pregunta, medida contra la cuota y no contra el motor: con la forma propia
de los últimos N partidos OFICIALES de cada lado (antes del partido),

1. el FAVORITO de la casa (≥ 50 % sin margen) que viene ganando mucho menos
   (o más) de lo que la casa le da hoy, ¿gana menos (o más) que la cuota?
2. el RIVAL que viene sin perder o marcando seguido, ¿le baja la victoria al
   favorito más de lo que la cuota ya cobra?
3. el favorito que viene recibiendo gol seguido, ¿gana menos que la cuota?

Medido el 21/11 sobre 385 partes acreditables (dos meses): el favorito con la
forma 14+ pts debajo de la casa ganó el 69,5 % contra el 57,6 % que decía la
casa (n 128, IC de la diferencia −0,2 a +21): AL REVÉS de la intuición y sin
probar. Esto lo mide en el padrón, con todas las cuotas guardadas.

Cómo: residuo = ganó (1/0) − probabilidad de ganar de la casa sin margen
(`backtest_burbuja_1x2.cuotas_1x2`, promedio entre casas, sin sintéticas).
Por grupo: residuo medio con intervalo por bootstrap de EQUIPOS, la
diferencia contra el resto y la plana a la cuota media aproximada (la
probabilidad sin margen con el margen medio devuelto). «Separa» = el IC de la
diferencia no toca el cero; «se repite» = separa en el mismo sentido en las
dos mitades del tiempo. Son varias preguntas a la vez: una que separa sin
repetirse es lo que se espera por azar.

Sin fuga: la forma sale SOLO de partidos con fecha anterior (los amistosos no
cuentan en la forma ni se evalúan). Las copas nacionales quedan fuera
(`escala.copas_nacionales`, regla del proyecto: un favorito contra uno de
quinta división infla todo). Lee, no escribe.

    python -m backend.backtest_forma_cuota --padron                       # en el servidor
    python -m backend.backtest_forma_cuota --padron --json $SAD_DATA_DIR/forma_cuota.json
    python -m backend.backtest_forma_cuota --padron --ultimos 5           # forma de 5 en vez de 10
"""
from __future__ import annotations

import argparse
import json
import os
import random
from collections import defaultdict, deque

AMISTOSOS = {667}
ULTIMOS = 10
FAVORITO = 0.5          # probabilidad de ganar de la casa, sin margen
BOOTSTRAP = 1000
CORTES_GAP = ((-9.0, -0.20, "forma 20+ pts debajo de la casa"), (-0.20, 0.0, "forma 0-20 pts debajo"),
              (0.0, 9.0, "forma arriba de la casa"))
TRAMOS_CASA = ((0.5, 0.7, "casa 50-70 %"), (0.7, 1.01, "casa 70 %+"))


# ── la forma de cada lado, sin fuga ──────────────────────────────────────────

def formas(historias: dict[int, list[dict]], ultimos: int = ULTIMOS) -> dict[tuple[int, int], dict]:
    """{(fixture, equipo): forma de los `ultimos` oficiales ANTERIORES + lo que pasó}.
    Partidos del mismo día no se miran entre sí: la forma usa fechas estrictamente
    anteriores (dos filas del mismo día no se filtran el resultado)."""
    out = {}
    for team, filas in historias.items():
        filas = sorted((f for f in filas if f.get("golesFavor") is not None and f.get("golesContra") is not None),
                       key=lambda f: str(f.get("fecha") or ""))
        ventana: deque = deque(maxlen=ultimos)      # (fecha, gf, gc) de los oficiales ya jugados
        pendientes: list = []                       # los del día en curso: entran cuando cambia la fecha
        dia = None
        for f in filas:
            fecha = str(f.get("fecha") or "")[:10]
            if fecha != dia:
                ventana.extend(pendientes)
                pendientes, dia = [], fecha
            gf, gc = int(f["golesFavor"]), int(f["golesContra"])
            oficial = f.get("ligaId") not in AMISTOSOS
            if oficial and len(ventana) == ultimos:
                n = len(ventana)
                out[(f["fixtureId"], team)] = {
                    "fecha": fecha, "local": f.get("condicion") == "Local", "liga": f.get("ligaId"),
                    "rival": f.get("rivalId"), "gana": gf > gc, "empata": gf == gc,
                    "formaGana": sum(1 for _, a, b in ventana if a > b) / n,
                    "formaNoPierde": sum(1 for _, a, b in ventana if a >= b) / n,
                    "formaAnota": sum(1 for _, a, _b in ventana if a >= 1) / n,
                    "formaRecibe": sum(1 for _, _a, b in ventana if b >= 1) / n,
                }
            if oficial:
                pendientes.append((fecha, gf, gc))
    return out


def casos(historias: dict[int, list[dict]], cuotas: dict, excluir: set | None = None,
          ultimos: int = ULTIMOS) -> list[dict]:
    """Un caso por partido con cuota: el favorito de la casa con su forma y la del rival.
    `cuotas[fx] = (pL, pE, pV, casas, margen)`: pL es el LOCAL, pV el VISITANTE."""
    fs = formas(historias, ultimos)
    por_fx = defaultdict(dict)
    for (fx, team), o in fs.items():
        por_fx[fx][team] = o
    out = []
    for fx, lados in por_fx.items():
        if fx not in cuotas or (excluir and fx in excluir) or len(lados) != 2:
            continue
        (ta, a), (tb, b) = lados.items()
        if a["local"] == b["local"] or a["rival"] != tb or b["rival"] != ta:
            continue
        pl, _pe, pv, _casas, margen = cuotas[fx]
        for team, yo, otro in ((ta, a, b), (tb, b, a)):
            p = pl if yo["local"] else pv
            if p < FAVORITO:
                continue
            out.append({"fixtureId": fx, "team": team, "fecha": yo["fecha"], "p": p,
                        "cuota": 1 / (p * (1 + margen)), "gana": yo["gana"], "empata": yo["empata"],
                        "gap": yo["formaGana"] - p, "fav": yo, "riv": otro})
    out.sort(key=lambda c: (c["fecha"], c["fixtureId"]))
    return out


# ── la cuenta ────────────────────────────────────────────────────────────────

def _resumen(sub: list[dict]) -> dict:
    n = len(sub)
    if not n:
        return {"n": 0}
    g = sum(1 for c in sub if c["gana"])
    return {"n": n, "gano": round(g / n, 4), "casaDecia": round(sum(c["p"] for c in sub) / n, 4),
            "residuo": round(sum((1 if c["gana"] else 0) - c["p"] for c in sub) / n, 4),
            "empata": round(sum(1 for c in sub if c["empata"]) / n, 4),
            "roiPlano": round(sum((c["cuota"] - 1) if c["gana"] else -1 for c in sub) / n, 4)}


def diferencia(con: list[dict], sin: list[dict], semilla: int = 7) -> dict:
    """Residuo(con) − residuo(sin), con IC por bootstrap de equipos (los partidos
    de un equipo no son independientes)."""
    if len(con) < 30 or len(sin) < 30:
        return {"sinDato": "menos de 30 casos en un grupo"}

    def por_equipo(sub):
        d = defaultdict(lambda: [0.0, 0])
        for c in sub:
            d[c["team"]][0] += (1 if c["gana"] else 0) - c["p"]
            d[c["team"]][1] += 1
        return list(d.values())
    ea, eb = por_equipo(con), por_equipo(sin)
    media = sum(e[0] for e in ea) / sum(e[1] for e in ea) - sum(e[0] for e in eb) / sum(e[1] for e in eb)
    rnd = random.Random(semilla)
    boots = []
    for _ in range(BOOTSTRAP):
        ma = [ea[rnd.randrange(len(ea))] for _ in ea]
        mb = [eb[rnd.randrange(len(eb))] for _ in eb]
        boots.append(sum(e[0] for e in ma) / sum(e[1] for e in ma) - sum(e[0] for e in mb) / sum(e[1] for e in mb))
    boots.sort()
    lo, hi = boots[int(0.025 * BOOTSTRAP)], boots[int(0.975 * BOOTSTRAP) - 1]
    return {"diferencia": round(media, 4), "ic95": [round(lo, 4), round(hi, 4)], "separa": lo > 0 or hi < 0}


SENALES = {
    "favorito con la forma 20+ pts debajo de la casa": lambda c: c["gap"] <= -0.20,
    "favorito con la forma arriba de la casa": lambda c: c["gap"] > 0.0,
    "favorito que recibió en 7+ de sus últimos": lambda c: c["fav"]["formaRecibe"] >= 0.7,
    "rival que no perdió 6+ de sus últimos": lambda c: c["riv"]["formaNoPierde"] >= 0.6,
    "rival que marcó en 8+ de sus últimos": lambda c: c["riv"]["formaAnota"] >= 0.8,
    "las dos: favorito 20+ pts debajo y rival que no pierde": lambda c: c["gap"] <= -0.20 and c["riv"]["formaNoPierde"] >= 0.6,
}


def evaluar(cs: list[dict]) -> dict:
    if not cs:
        return {"casos": 0, "lectura": "sin casos con cuota"}
    corte = sorted(c["fecha"] for c in cs)[len(cs) // 2]
    mitades = (("antes de " + corte, [c for c in cs if c["fecha"] < corte]), ("desde " + corte, [c for c in cs if c["fecha"] >= corte]))
    senales = []
    for nombre, f in SENALES.items():
        con, sin = [c for c in cs if f(c)], [c for c in cs if not f(c)]
        d = diferencia(con, sin)
        por_mitad = [{"epoca": et, **diferencia([c for c in sub if f(c)], [c for c in sub if not f(c)])} for et, sub in mitades]
        se_repite = bool(d.get("separa")) and all(
            m.get("separa") and (m["diferencia"] > 0) == (d["diferencia"] > 0) for m in por_mitad)
        senales.append({"senal": nombre, "con": _resumen(con), "sin": _resumen(sin), "diferencia": d,
                        "porEpoca": por_mitad, "seRepite": se_repite,
                        "porTramoCasa": [{"tramo": tn, "con": _resumen([c for c in con if a <= c["p"] < b]),
                                          "sin": _resumen([c for c in sin if a <= c["p"] < b])} for a, b, tn in TRAMOS_CASA]})
    gaps = [{"tramo": tn, **_resumen([c for c in cs if a < c["gap"] <= b])} for a, b, tn in CORTES_GAP]
    firmes = [s["senal"] for s in senales if s["seRepite"]]
    return {"casos": len(cs), "equipos": len({c["team"] for c in cs}), "desde": cs[0]["fecha"], "hasta": cs[-1]["fecha"],
            "todos": _resumen(cs), "porGap": gaps, "senales": senales, "firmes": firmes,
            "lectura": ("ninguna forma propia, del favorito ni del rival, avisa algo que la cuota no cobre: "
                        "ninguna separa y se repite en las dos mitades" if not firmes else
                        "separan y se repiten en las dos mitades: " + "; ".join(firmes) +
                        ". Antes de usarlas: mirar el roi plano a la cuota real (el margen se come la diferencia chica)")}


# ── de dónde salen los datos ─────────────────────────────────────────────────

def correr_padron(ultimos: int = ULTIMOS) -> dict:
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.analisis.escala import copas_nacionales
    from backend.app import constantes_de
    from backend.backtest_burbuja import _equipos, padron
    from backend.backtest_burbuja_1x2 import cuotas_1x2
    historias = {t: list(reversed(constantes_de(t, 500))) for t in _equipos(ultimos + 2, set(padron()))}
    fxs = sorted({f["fixtureId"] for filas in historias.values() for f in filas
                  if f.get("ligaId") not in AMISTOSOS and f.get("golesFavor") is not None})
    cuotas = cuotas_1x2(fxs)
    # en lotes: con miles de ids una sola consulta puede pasar el límite de
    # variables de SQLite, y el except de copas_nacionales devuelve {} callado
    ids = sorted(cuotas)
    excluir = set()
    for i in range(0, len(ids), 500):
        excluir |= set(copas_nacionales(ids[i:i + 500]))
    r = evaluar(casos(historias, cuotas, excluir, ultimos))
    r.update({"ultimos": ultimos, "equiposPadron": len(historias), "partidosConCuota": len(cuotas),
              "copasNacionalesFuera": len(excluir)})
    return r


def _imprimir(r: dict) -> None:
    if not r.get("casos"):
        print(r.get("lectura"))
        return
    print(f"\n{r['casos']:,} favoritos de la casa (≥ 50 %) con cuota · {r['equipos']} equipos · {r['desde']} → {r['hasta']} "
          f"· forma de los últimos {r.get('ultimos', ULTIMOS)} oficiales · copas nacionales fuera: {r.get('copasNacionalesFuera', 0)}")
    print(r["lectura"], "\n")

    def g(x):
        return (f"n {x['n']:>6}  ganó {x['gano']:6.1%}  casa {x['casaDecia']:6.1%}  residuo {x['residuo']:+6.1%}  "
                f"roi {x['roiPlano']:+6.1%}") if x.get("n") else "n      0"
    print(f"todos{'':<52}{g(r['todos'])}")
    for x in r["porGap"]:
        print(f"  {x['tramo']:<54}{g(x)}")
    print()
    for s in r["senales"]:
        d = s["diferencia"]
        dd = (f"diferencia {d['diferencia']:+.1%} IC [{d['ic95'][0]:+.1%}, {d['ic95'][1]:+.1%}]"
              + ("  SEPARA" if d["separa"] else "") + ("  y se repite" if s["seRepite"] else "")) if "diferencia" in d else d.get("sinDato")
        print(f"{s['senal']}\n  con  {g(s['con'])}\n  sin  {g(s['sin'])}\n  {dd}")
        for m in s["porEpoca"]:
            if "diferencia" in m:
                print(f"    {m['epoca']:<22} {m['diferencia']:+.1%} IC [{m['ic95'][0]:+.1%}, {m['ic95'][1]:+.1%}]")
        for t in s["porTramoCasa"]:
            print(f"    {t['tramo']:<14} con {g(t['con'])}")


def main() -> None:
    ap = argparse.ArgumentParser(description="La forma propia del favorito y del rival, contra la cuota")
    ap.add_argument("--padron", action="store_true", help="historias y cuotas de las ligas del padrón (en el servidor)")
    ap.add_argument("--ultimos", type=int, default=ULTIMOS, help="partidos oficiales de la forma (10 por defecto)")
    ap.add_argument("--json", help="guardar el resumen en este archivo")
    a = ap.parse_args()
    if not a.padron:
        ap.error("corre en el servidor con --padron (necesita las cuotas guardadas)")
    r = correr_padron(a.ultimos)
    _imprimir(r)
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)
        print(f"\nresumen en {a.json}")


if __name__ == "__main__":
    main()
