"""¿Por cuánto gana el favorito grande? El hándicap y dónde no entrar
(pedido del usuario, 21/11/2026, tras Bayern 1-1 Köln).

El usuario: «la gente pierde plata en estos partidos por los hándicaps: cree
que el favorito va a ganar por 2, 3, 4 goles; una cuota de 1,10 que tiene que
ganar por 2 se convierte en 1,5 y parece jugosa… muchos de esos partidos
terminan con una diferencia mínima». Bayern llegaba con 11 partidos de local
con más de 2,5 goles y la burbuja que no reventó fue la de no perder; la que
sí pudo hablar es la de la diferencia de goles. Esto lo mide.

1. **Cuánto gana el favorito** por segmento (por nivel previo: favorito,
   muy favorito, gigante —nivel 3,5+ y 1,0+—, gigante con 1,5+, gigante de
   local; por casa: 70, 80 y 85 %+): gana por 1, por 2+, por 3+, empata,
   pierde, y la CUOTA JUSTA de «gana por 2+» (hándicap −1,5) y de «gana por
   3+» (−2,5). La base no guarda la cuota del hándicap −1,5 (solo ±0,5): la
   justa se compara a mano con la que da la casa.
2. **Dónde no entrar en el hándicap**: dentro de cada segmento, señales
   PREVIAS del rival (casi nunca lo golean en esa condición, viene sin perder
   por 2+, esa racha en su récord, su perfil de doble oportunidad) y del
   favorito (no viene goleando, sequía de goleadas en la condición): cuánto
   deja de cubrir el −1,5 con y sin la señal, qué parte de los «no cubre»
   caza, y la diferencia contra los sin señal del mismo tramo de 0,1 de
   ventaja y condición, por época.
3. **Por liga**: en los muy favoritos, cubrir el −1,5 contra lo esperado por
   su tramo de ventaja en todas las ligas: dónde el favorito gana apretado.

Las burbujas son las de la app: la racha o sequía de «pierde por 2+» del
rival y de «gana por 2+» del favorito en la condición de hoy (familias de
REVENTON §15), con su récord. Todo con lo ANTERIOR al partido; amistosos ni
en la forma ni evaluados; copas nacionales fuera. Lee, no escribe.

    python -m backend.backtest_margen --padron --json $SAD_DATA_DIR/margen.json
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict, deque

from backend.backtest_dc_record import EstadoDC
from backend.backtest_rival_resiste import AMISTOSOS, _boot, _copas, _nivel_antes

ULTIMOS = 10
MIN_LIGA = 60

SEGMENTOS = {
    "favorito por nivel (0,5+)": lambda c: c["ventaja"] is not None and c["ventaja"] >= 0.5,
    "muy favorito por nivel (1,0+)": lambda c: c["ventaja"] is not None and c["ventaja"] >= 1.0,
    "gigante: nivel 3,5+ y 1,0+ de ventaja": lambda c: c["ventaja"] is not None and c["ventaja"] >= 1.0 and c["nivel"] >= 3.5,
    "gigante con 1,5+ de ventaja": lambda c: c["ventaja"] is not None and c["ventaja"] >= 1.5 and c["nivel"] >= 3.5,
    "gigante de local": lambda c: c["ventaja"] is not None and c["ventaja"] >= 1.0 and c["nivel"] >= 3.5 and c["local"],
    "casa 70 %+": lambda c: c["p"] is not None and c["p"] >= 0.70,
    "casa 80 %+": lambda c: c["p"] is not None and c["p"] >= 0.80,
    "casa 85 %+": lambda c: c["p"] is not None and c["p"] >= 0.85,
}

SENALES = {
    "rival: casi nunca lo golean en la condición (≤ 15 %)": lambda c: c["riv"]["perfilGoleado"] is not None and c["riv"]["perfilGoleado"] <= 0.15,
    "rival: viene 5+ sin perder por 2+ en la condición": lambda c: c["riv"]["sequiaGoleada"] >= 5,
    "rival: esa racha sin perder por 2+ en su récord": lambda c: c["riv"]["sequiaGoleada"] > 0 and c["riv"]["recordSequia"] >= 1,
    "rival: no perdió por 2+ en 9+ de sus últimos 10": lambda c: c["riv"]["formaNoGoleado"] is not None and c["riv"]["formaNoGoleado"] >= 0.9,
    "rival: perfil DC 60 %+ en la condición": lambda c: c["riv"]["perfilNoPierde"] is not None and c["riv"]["perfilNoPierde"] >= 0.6,
    "favorito: ganó por 2+ en 3 o menos de sus últimos 10": lambda c: c["fav"]["formaGoleo"] is not None and c["fav"]["formaGoleo"] <= 0.3,
    "favorito: viene 3+ sin ganar por 2+ en la condición": lambda c: c["fav"]["sequiaGoleo"] >= 3,
    "las dos: rival que casi no golean y favorito que no viene goleando":
        lambda c: (c["riv"]["perfilGoleado"] is not None and c["riv"]["perfilGoleado"] <= 0.15
                   and c["fav"]["formaGoleo"] is not None and c["fav"]["formaGoleo"] <= 0.3),
}


# ── lo que se sabía de cada lado antes del partido ──────────────────────────

def lados(historias: dict[int, dict], nivel_rival=None) -> dict[tuple[int, int], dict]:
    niv = {t: ([n["fecha"] for n in h.get("niveles") or []], [float(n["nivel"]) for n in h.get("niveles") or []])
           for t, h in historias.items()}
    out = {}
    for team, h in historias.items():
        filas = sorted((f for f in h["filas"] if f.get("golesFavor") is not None and f.get("golesContra") is not None),
                       key=lambda f: str(f.get("fecha") or ""))
        goleo = {"Local": EstadoDC(), "Visita": EstadoDC()}       # serie «gana por 2+»
        goleado = {"Local": EstadoDC(), "Visita": EstadoDC()}     # serie «pierde por 2+»
        cuenta = {"Local": [0, 0, 0], "Visita": [0, 0, 0]}        # [pierde por 2+, no pierde, jugados]
        ventana: deque = deque(maxlen=ULTIMOS)
        pendientes, dia = [], None
        for f in filas:
            fecha = str(f.get("fecha") or "")
            if fecha[:10] != dia:
                ventana.extend(pendientes)
                pendientes, dia = [], fecha[:10]
            cond = f.get("condicion")
            if cond not in goleo:
                continue
            gf, gc = int(f["golesFavor"]), int(f["golesContra"])
            if f.get("ligaId") not in AMISTOSOS:
                g, gd, c = goleo[cond], goleado[cond], cuenta[cond]
                propio = _nivel_antes(*niv[team], fecha) if niv[team][0] else None
                rid = f.get("rivalId")
                if rid in niv and niv[rid][0]:
                    rival = _nivel_antes(*niv[rid], fecha)
                elif nivel_rival is not None and rid is not None:
                    rival = nivel_rival(rid, fecha)
                else:
                    rival = None
                lleno = len(ventana) == ULTIMOS
                out[(f["fixtureId"], team)] = {
                    "fecha": fecha[:10], "local": cond == "Local", "liga": f.get("ligaId"), "rival": rid,
                    "nivel": propio, "nivelRival": rival, "margen": gf - gc,
                    "formaGoleo": (sum(1 for a, b in ventana if a - b >= 2) / ULTIMOS) if lleno else None,
                    "formaNoGoleado": (sum(1 for a, b in ventana if b - a < 2) / ULTIMOS) if lleno else None,
                    "sequiaGoleo": -g.burbuja() if g.burbuja() < 0 else 0,
                    "sequiaGoleada": -gd.burbuja() if gd.burbuja() < 0 else 0,
                    "recordSequia": gd.record() if gd.burbuja() < 0 else 0,
                    "perfilGoleado": ((c[0] + 1) / (c[2] + 2)) if c[2] >= 10 else None,
                    "perfilNoPierde": ((c[1] + 1) / (c[2] + 2)) if c[2] >= 10 else None,
                }
                pendientes.append((gf, gc))
            goleo[cond].sumar(gf - gc >= 2)
            goleado[cond].sumar(gc - gf >= 2)
            cuenta[cond][0] += 1 if gc - gf >= 2 else 0
            cuenta[cond][1] += 1 if gf >= gc else 0
            cuenta[cond][2] += 1
    return out


def casos(historias: dict[int, dict], cuotas: dict | None = None, excluir: set | None = None,
          nivel_rival=None) -> list[dict]:
    """El favorito de cada partido (0,5+ de nivel previo, o ≥ 50 % de la casa) con su margen."""
    ls = lados(historias, nivel_rival)
    por_fx = defaultdict(dict)
    for (fx, team), o in ls.items():
        por_fx[fx][team] = o
    out = []
    for fx, par in por_fx.items():
        if (excluir and fx in excluir) or len(par) != 2:
            continue
        (ta, a), (tb, b) = par.items()
        if a["local"] == b["local"] or a["rival"] != tb or b["rival"] != ta:
            continue
        c = (cuotas or {}).get(fx)
        for team, yo, otro in ((ta, a, b), (tb, b, a)):
            v = (yo["nivel"] - otro["nivel"]) if yo["nivel"] is not None and otro["nivel"] is not None else None
            p = (c[0] if yo["local"] else c[2]) if c else None
            if not ((v is not None and v >= 0.5) or (p is not None and p >= 0.5)):
                continue
            out.append({"fixtureId": fx, "team": team, "fecha": yo["fecha"], "liga": yo["liga"], "local": yo["local"],
                        "ventaja": v, "nivel": yo["nivel"] or 0.0, "p": p, "margen": yo["margen"],
                        "fav": yo, "riv": otro})
    out.sort(key=lambda x: (x["fecha"], x["fixtureId"]))
    return out


# ── la cuenta ────────────────────────────────────────────────────────────────

def reparto(sub: list[dict]) -> dict:
    n = len(sub)
    if not n:
        return {"n": 0}
    m = [c["margen"] for c in sub]
    g2 = sum(1 for x in m if x >= 2) / n
    g3 = sum(1 for x in m if x >= 3) / n
    return {"n": n, "ganaPor1": round(sum(1 for x in m if x == 1) / n, 4), "ganaPor2oMas": round(g2, 4),
            "ganaPor3oMas": round(g3, 4), "empata": round(sum(1 for x in m if x == 0) / n, 4),
            "pierde": round(sum(1 for x in m if x < 0) / n, 4), "margenMedio": round(sum(m) / n, 3),
            "cuotaJustaMenos1_5": round(1 / g2, 2) if g2 else None, "cuotaJustaMenos2_5": round(1 / g3, 2) if g3 else None,
            "casaDecia": round(sum(c["p"] for c in sub) / n, 4) if all(c["p"] is not None for c in sub) else None}


def _bin(c: dict) -> tuple:
    return (min(int((c["ventaja"] if c["ventaja"] is not None else -1) / 0.1), 30), c["local"])


def separa(seg: list[dict], senal, umbral: int = 2) -> dict:
    """«No cubre» = el favorito no gana por `umbral`+. Con la señal contra sin ella,
    y la diferencia contra los sin señal del mismo tramo de 0,1 de ventaja (> 0 = la
    señal marca un hándicap donde no entrar)."""
    falla = lambda c: c["margen"] < umbral  # noqa: E731
    con = [c for c in seg if senal(c)]
    sin = [c for c in seg if not senal(c)]
    tot = sum(1 for c in seg if falla(c))
    out = {"n": len(seg), "conSenal": len(con), "parte": round(len(con) / len(seg), 4) if seg else None,
           "noCubreCon": round(sum(1 for c in con if falla(c)) / len(con), 4) if con else None,
           "noCubreSin": round(sum(1 for c in sin if falla(c)) / len(sin), 4) if sin else None,
           "caza": round(sum(1 for c in con if falla(c)) / tot, 4) if tot else None}
    base = defaultdict(lambda: [0, 0])
    for c in sin:
        if c["ventaja"] is not None:
            base[_bin(c)][0] += 1 if falla(c) else 0
            base[_bin(c)][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n >= 10}
    por_eq = defaultdict(lambda: [0.0, 0])
    for c in con:
        if c["ventaja"] is not None and _bin(c) in esp:
            por_eq[c["team"]][0] += (1 if falla(c) else 0) - esp[_bin(c)]
            por_eq[c["team"]][1] += 1
    b = _boot(list(por_eq.values()))
    if b:
        out.update({"diferencia": round(b[0], 4), "ic95": [round(b[1], 4), round(b[2], 4)], "separa": b[1] > 0 or b[2] < 0})
    return out


def por_liga(cs: list[dict], segmento) -> list[dict]:
    """Cubrir el −1,5 en el segmento, contra lo esperado por tramo de 0,1 de ventaja y condición en TODAS las ligas."""
    seg = [c for c in cs if c["ventaja"] is not None and segmento(c)]
    base = defaultdict(lambda: [0, 0])
    for c in seg:
        base[_bin(c)][0] += 1 if c["margen"] >= 2 else 0
        base[_bin(c)][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n}
    ligas = defaultdict(list)
    for c in seg:
        ligas[c["liga"]].append((1 if c["margen"] >= 2 else 0, esp[_bin(c)]))
    filas = [{"liga": lg, "n": len(v), "cubre": round(sum(a for a, _ in v) / len(v), 4),
              "esperado": round(sum(b for _, b in v) / len(v), 4),
              "diferencia": round(sum(a - b for a, b in v) / len(v), 4)}
             for lg, v in ligas.items() if len(v) >= MIN_LIGA]
    filas.sort(key=lambda x: x["diferencia"])
    return filas


def evaluar(cs: list[dict]) -> dict:
    if not cs:
        return {"casos": 0}
    nv = [c for c in cs if c["ventaja"] is not None]
    corte = sorted(c["fecha"] for c in nv)[len(nv) // 2] if nv else ""
    segs = []
    for sn, sf in SEGMENTOS.items():
        seg = [c for c in cs if sf(c)]
        fila = {"segmento": sn, "reparto": reparto(seg), "senales": []}
        if len(seg) >= 50:
            for kn, kf in SENALES.items():
                r = separa(seg, kf)
                r["noCubre2_5"] = separa(seg, kf, umbral=3)
                r["porEpoca"] = [separa([c for c in seg if c["fecha"] < corte], kf),
                                 separa([c for c in seg if c["fecha"] >= corte], kf)]
                r["seRepite"] = (bool(r.get("separa")) and r["diferencia"] > 0
                                 and all(e.get("separa") and e["diferencia"] > 0 for e in r["porEpoca"]))
                fila["senales"].append({"senal": kn, **r})
        segs.append(fila)
    return {"casos": len(cs), "desde": cs[0]["fecha"], "hasta": cs[-1]["fecha"], "corteEpoca": corte,
            "segmentos": segs, "porLiga": por_liga(cs, SEGMENTOS["muy favorito por nivel (1,0+)"]),
            "porLigaGigante": por_liga(cs, SEGMENTOS["gigante: nivel 3,5+ y 1,0+ de ventaja"])}


# ── de dónde salen los datos ─────────────────────────────────────────────────

def correr_padron() -> dict:
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.backtest_burbuja import nivel_rival_previo
    from backend.backtest_burbuja_1x2 import cuotas_1x2
    from backend.backtest_dc_record import historias_padron
    historias = historias_padron()
    fxs = sorted({f["fixtureId"] for h in historias.values() for f in h["filas"]
                  if f.get("ligaId") not in AMISTOSOS and f.get("golesFavor") is not None})
    cuotas = cuotas_1x2(fxs)
    excluir = _copas(fxs)
    r = evaluar(casos(historias, cuotas, excluir, nivel_rival_previo))
    try:
        from backend.backtest_burbuja import _nombres_ligas
        nombres = _nombres_ligas({f["liga"] for f in r.get("porLiga", []) + r.get("porLigaGigante", [])})
        for f in r.get("porLiga", []) + r.get("porLigaGigante", []):
            f["nombre"] = nombres.get(f["liga"], "")
    except Exception:  # noqa: BLE001 — sin nombres se imprime el id de la liga
        pass
    r.update({"equipos": len(historias), "copasNacionalesFuera": len(excluir)})
    return r


def _imprimir(r: dict) -> None:
    if not r.get("casos"):
        print("sin casos")
        return
    print(f"\n{r['casos']:,} favoritos · {r['desde']} → {r['hasta']} · copas nacionales fuera: {r.get('copasNacionalesFuera', 0)}\n")
    print("1 · POR CUÁNTO GANA EL FAVORITO (y la cuota justa del hándicap; compará con la que da la casa)")
    for s in r["segmentos"]:
        x = s["reparto"]
        if not x["n"]:
            continue
        casa = f" · la casa le daba {x['casaDecia']:.0%} de ganar" if x.get("casaDecia") else ""
        print(f"  {s['segmento']:<40} n {x['n']:>6} · gana por 1 {x['ganaPor1']:5.1%} · por 2+ {x['ganaPor2oMas']:5.1%} · "
              f"por 3+ {x['ganaPor3oMas']:5.1%} · empata {x['empata']:5.1%} · pierde {x['pierde']:5.1%}{casa}")
        print(f"  {'':<40} cuota justa: −1,5 → {x['cuotaJustaMenos1_5']} · −2,5 → {x['cuotaJustaMenos2_5']}")
    print("\n2 · DÓNDE NO ENTRAR EN EL HÁNDICAP −1,5 (no cubre con / sin la señal; caza = parte de los «no cubre»;"
          " diferencia contra el mismo tramo de 0,1 de ventaja)")
    for s in r["segmentos"]:
        if not s["senales"]:
            continue
        print(f"  {s['segmento']}")
        for k in s["senales"]:
            if not k["conSenal"]:
                continue
            d = (f" · dif {k['diferencia']:+.1%} IC [{k['ic95'][0]:+.1%}, {k['ic95'][1]:+.1%}]"
                 + (" SEPARA" if k["separa"] else "") + (" y se repite" if k["seRepite"] else "")) if "diferencia" in k else ""
            print(f"    {k['senal']:<64} {k['parte']:4.0%} · no cubre {k['noCubreCon']:5.1%} con, "
                  f"{(k['noCubreSin'] or 0):5.1%} sin · caza {(k['caza'] or 0):4.0%}{d}")
    for titulo, clave in (("muy favoritos (1,0+)", "porLiga"), ("gigantes", "porLigaGigante")):
        print(f"\n3 · POR LIGA, {titulo}: cubre el −1,5 contra lo esperado por su ventaja (las más apretadas primero)")
        for f in r[clave]:
            print(f"    liga {f['liga']:<6} {f.get('nombre', '')[:26]:<26} n {f['n']:>5} · cubre {f['cubre']:5.1%}"
                  f" · esperado {f['esperado']:5.1%} · {f['diferencia']:+.1%}")


def main() -> None:
    ap = argparse.ArgumentParser(description="¿Por cuánto gana el favorito grande? El hándicap y dónde no entrar")
    ap.add_argument("--padron", action="store_true", help="historias, niveles y cuotas del padrón (en el servidor)")
    ap.add_argument("--json", help="guardar el resumen en este archivo")
    a = ap.parse_args()
    if not a.padron:
        ap.error("corre en el servidor con --padron")
    r = correr_padron()
    _imprimir(r)
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)
        print(f"\nresumen en {a.json}")


if __name__ == "__main__":
    main()
