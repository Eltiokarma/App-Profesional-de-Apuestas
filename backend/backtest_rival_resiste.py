"""¿El RIVAL que resiste le baja la victoria al favorito? Validación del
candidato del 21/11/2026 por liga, en los años sin cuotas y con las burbujas.

El candidato (docs/METODO_APUESTA.md, «El equipo contra sí mismo»), congelado
el 22/11/2026: favorito de la casa entre 50 y 70 % contra un rival que no
perdió 6+ de sus últimos 10 oficiales → no apostar. Salió de
`backtest_forma_cuota` con 1.249 favoritos con cuota (23/08 a 20/11/2026):
−5,2 pts contra la casa (IC −10,4 a +0,1), solo en la segunda mitad. El
usuario: «¿no hay forma de confirmar eso por liga? ¿validar con burbujas?».

Esto NO cambia la regla: la pone a prueba de tres maneras.

1. **Contra el nivel, en los años que la regla no vio** (2019 → hoy, sin
   cuotas): el favorito es el que tiene 0,5+ de nivel PREVIO sobre el rival
   (los dos niveles anteriores al partido, §13.1 de REVENTON). Lo esperado
   sale de los casos SIN la señal del mismo tramo de ventaja y condición; el
   residuo (no ganó − esperado) del grupo con la señal, con IC por bootstrap
   de equipos y por época. Si el efecto no existe ni contra el nivel, no hay
   nada que la casa pueda estar dejando pasar.
2. **Contra la casa** (los partidos con cuota): lo mismo que
   `backtest_forma_cuota`, con el tramo 50-70 % del candidato aparte.
3. **Por liga**: en cada liga con 30+ casos con la señal, el signo del
   residuo; cuántas ligas van en el sentido del candidato y la prueba del
   signo. Un efecto real aparece en la mayoría de las ligas.

Y la «resistencia» del rival medida de cuatro maneras, todas en su condición
de HOY y solo con lo anterior:

  forma      no perdió 6+ de sus últimos 10 oficiales (la regla congelada)
  burbuja    su racha sin perder de la condición tiene 3+ partidos
  récord     esa racha está en su récord (iguala o supera, perfil_dc)
  perfil     no pierde el 60 %+ de su historia en esa condición (perfil DC)

Si son la misma cosa, deberían ir para el mismo lado.

Los amistosos no se evalúan ni cuentan en la forma (sí en la historia de la
burbuja y del perfil, como en `perfil_dc`). Copas nacionales fuera. Lee, no
escribe.

    python -m backend.backtest_rival_resiste --padron --json $SAD_DATA_DIR/rival_resiste.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from bisect import bisect_left
from collections import defaultdict, deque

from backend.backtest_dc_record import EstadoDC

AMISTOSOS = {667}
ULTIMOS = 10
FAVORITO_NIVEL = 0.5
FAVORITO_CASA = 0.5
BOOTSTRAP = 500
MIN_LIGA = 30
TRAMOS_VENTAJA = ((0.5, 1.0, "favorito (0,5-1,0)"), (1.0, 99.0, "muy favorito (≥ 1,0)"))
TRAMOS_CASA = ((0.5, 0.7, "casa 50-70 %"), (0.7, 1.01, "casa 70 %+"))

SENALES = {
    "forma": lambda r: r["formaNoPierde"] is not None and r["formaNoPierde"] >= 0.6,
    "burbuja": lambda r: r["racha"] >= 3,
    "record": lambda r: r["racha"] > 0 and r["record"] >= 1,
    "perfil": lambda r: r["perfilNoPierde"] is not None and r["perfilNoPierde"] >= 0.6,
}
NOMBRES = {"forma": "no perdió 6+ de sus últimos 10 (la regla congelada)",
           "burbuja": "racha sin perder de la condición de 3+",
           "record": "racha sin perder de la condición en su récord",
           "perfil": "no pierde el 60 %+ de su historia en la condición"}


def _nivel_antes(fechas: list[str], niveles: list[float], fecha: str) -> float | None:
    i = bisect_left(fechas, fecha)
    return niveles[i - 1] if i > 0 else None


# ── lo que se sabía de cada lado antes del partido ──────────────────────────

def lados(historias: dict[int, dict], nivel_rival=None, ultimos: int = ULTIMOS) -> dict[tuple[int, int], dict]:
    """{(fixture, equipo): rasgos previos + resultado}. `historias[t] = {"filas", "niveles"}`."""
    niv = {t: ([n["fecha"] for n in h.get("niveles") or []], [float(n["nivel"]) for n in h.get("niveles") or []])
           for t, h in historias.items()}
    out = {}
    for team, h in historias.items():
        filas = sorted((f for f in h["filas"] if f.get("golesFavor") is not None and f.get("golesContra") is not None),
                       key=lambda f: str(f.get("fecha") or ""))
        estados = {"Local": EstadoDC(), "Visita": EstadoDC()}
        cuenta = {"Local": [0, 0], "Visita": [0, 0]}          # [no perdió, jugados] en la condición
        ventana: deque = deque(maxlen=ultimos)
        pendientes, dia = [], None
        for f in filas:
            fecha = str(f.get("fecha") or "")
            if fecha[:10] != dia:
                ventana.extend(pendientes)
                pendientes, dia = [], fecha[:10]
            cond = f.get("condicion")
            if cond not in estados:
                continue
            gf, gc = int(f["golesFavor"]), int(f["golesContra"])
            oficial = f.get("ligaId") not in AMISTOSOS
            if oficial:
                e, c = estados[cond], cuenta[cond]
                propio = _nivel_antes(*niv[team], fecha) if niv.get(team) and niv[team][0] else None
                rid = f.get("rivalId")
                if rid in niv and niv[rid][0]:
                    rival = _nivel_antes(*niv[rid], fecha)
                elif nivel_rival is not None and rid is not None:
                    rival = nivel_rival(rid, fecha)
                else:
                    rival = None
                out[(f["fixtureId"], team)] = {
                    "fecha": fecha[:10], "local": cond == "Local", "liga": f.get("ligaId"), "rival": rid,
                    "nivel": propio, "nivelRival": rival, "gana": gf > gc, "empata": gf == gc,
                    "formaNoPierde": (sum(1 for a, b in ventana if a >= b) / len(ventana)) if len(ventana) == ultimos else None,
                    "racha": e.burbuja(), "record": e.record(),
                    "perfilNoPierde": ((c[0] + 1) / (c[1] + 2)) if c[1] >= 10 else None,
                }
                pendientes.append((gf, gc))
            estados[cond].sumar(gf >= gc)
            cuenta[cond][0] += 1 if gf >= gc else 0
            cuenta[cond][1] += 1
    return out


def casos(historias: dict[int, dict], cuotas: dict | None = None, excluir: set | None = None,
          nivel_rival=None) -> list[dict]:
    """Un caso por partido con favorito: por NIVEL (0,5+ de ventaja previa) y, si
    hay cuota, por CASA (≥ 50 % sin margen). El rival es el otro lado."""
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
            ventaja = (yo["nivel"] - otro["nivel"]) if yo["nivel"] is not None and otro["nivel"] is not None else None
            p = (c[0] if yo["local"] else c[2]) if c else None
            por_nivel = ventaja is not None and ventaja >= FAVORITO_NIVEL
            por_casa = p is not None and p >= FAVORITO_CASA
            if not (por_nivel or por_casa):
                continue
            out.append({"fixtureId": fx, "team": team, "fecha": yo["fecha"], "liga": yo["liga"], "local": yo["local"],
                        "gana": yo["gana"], "empata": yo["empata"], "ventaja": ventaja, "porNivel": por_nivel,
                        "nivel": yo["nivel"],
                        "p": p, "porCasa": por_casa, "cuota": (1 / (p * (1 + c[4]))) if por_casa else None,
                        "riv": otro})
    out.sort(key=lambda x: (x["fecha"], x["fixtureId"]))
    return out


# ── la cuenta ────────────────────────────────────────────────────────────────

def _tramo(v: float, tramos) -> str:
    for a, b, n in tramos:
        if a <= v < b:
            return n
    return tramos[-1][2]


def _boot(residuos_por_equipo: list[list[float]], semilla: int = 7) -> tuple[float, float, float] | None:
    eq = [e for e in residuos_por_equipo if e[1]]
    n = sum(e[1] for e in eq)
    if n < 30 or len(eq) < 5:
        return None
    media = sum(e[0] for e in eq) / n
    rnd = random.Random(semilla)
    bs = []
    for _ in range(BOOTSTRAP):
        m = [eq[rnd.randrange(len(eq))] for _ in eq]
        bs.append(sum(e[0] for e in m) / sum(e[1] for e in m))
    bs.sort()
    return media, bs[int(0.025 * BOOTSTRAP)], bs[int(0.975 * BOOTSTRAP) - 1]


def residuo_nivel(cs: list[dict], senal) -> dict:
    """Favoritos por nivel: no ganó − lo esperado por los SIN señal del mismo tramo y condición.
    Positivo = con el rival que resiste el favorito gana MENOS."""
    base = defaultdict(lambda: [0, 0])
    nv = [c for c in cs if c["porNivel"]]
    for c in nv:
        if not senal(c["riv"]):
            k = (_tramo(c["ventaja"], TRAMOS_VENTAJA), c["local"])
            base[k][0] += 0 if c["gana"] else 1
            base[k][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n >= 30}
    por_eq = defaultdict(lambda: [0.0, 0])
    con = 0
    for c in nv:
        k = (_tramo(c["ventaja"], TRAMOS_VENTAJA), c["local"])
        if senal(c["riv"]) and k in esp:
            por_eq[c["team"]][0] += (0 if c["gana"] else 1) - esp[k]
            por_eq[c["team"]][1] += 1
            con += 1
    b = _boot(list(por_eq.values()))
    if not b:
        return {"n": con, "sinDato": "menos de 30 casos o de 5 equipos"}
    return {"n": con, "residuo": round(b[0], 4), "ic95": [round(b[1], 4), round(b[2], 4)], "separa": b[1] > 0 or b[2] < 0}


def residuo_casa(cs: list[dict], senal, tramo: tuple[float, float] | None = None) -> dict:
    """Favoritos de la casa: no ganó − (1 − p), con la señal; y la plana a la cuota media."""
    sel = [c for c in cs if c["porCasa"] and senal(c["riv"]) and (tramo is None or tramo[0] <= c["p"] < tramo[1])]
    por_eq = defaultdict(lambda: [0.0, 0])
    for c in sel:
        por_eq[c["team"]][0] += (0 if c["gana"] else 1) - (1 - c["p"])
        por_eq[c["team"]][1] += 1
    b = _boot(list(por_eq.values()))
    roi = round(sum((c["cuota"] - 1) if c["gana"] else -1 for c in sel) / len(sel), 4) if sel else None
    if not b:
        return {"n": len(sel), "roiPlano": roi, "sinDato": "menos de 30 casos o de 5 equipos"}
    return {"n": len(sel), "residuo": round(b[0], 4), "ic95": [round(b[1], 4), round(b[2], 4)],
            "separa": b[1] > 0 or b[2] < 0, "roiPlano": roi}


def _signo(k: int, n: int) -> float:
    """P de la prueba del signo, a dos colas (binomial 1/2)."""
    if not n:
        return 1.0
    m = min(k, n - k)
    p = sum(math.comb(n, i) for i in range(0, m + 1)) / 2 ** n
    return round(min(1.0, 2 * p), 4)


def por_liga(cs: list[dict], senal) -> dict:
    """En cada liga con MIN_LIGA+ casos con la señal (favorito por nivel): el residuo
    crudo contra lo esperado por tramo y condición de TODAS las ligas sin la señal."""
    base = defaultdict(lambda: [0, 0])
    nv = [c for c in cs if c["porNivel"]]
    for c in nv:
        if not senal(c["riv"]):
            k = (_tramo(c["ventaja"], TRAMOS_VENTAJA), c["local"])
            base[k][0] += 0 if c["gana"] else 1
            base[k][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n}
    ligas = defaultdict(list)
    for c in nv:
        k = (_tramo(c["ventaja"], TRAMOS_VENTAJA), c["local"])
        if senal(c["riv"]) and k in esp:
            ligas[c["liga"]].append((0 if c["gana"] else 1) - esp[k])
    filas = [{"liga": lg, "n": len(v), "residuo": round(sum(v) / len(v), 4)}
             for lg, v in ligas.items() if len(v) >= MIN_LIGA]
    filas.sort(key=lambda x: -x["n"])
    pos = sum(1 for f in filas if f["residuo"] > 0)
    return {"ligas": filas, "conMasDerrotas": pos, "conMenos": len(filas) - pos,
            "pSigno": _signo(pos, len(filas)),
            "nota": "residuo > 0 = con el rival que resiste el favorito no gana MÁS de lo esperado en esa liga (el sentido del candidato)"}


# ── por segmento: dónde NO entrar (21/11/2026) ───────────────────────────────
# El usuario apuesta por ACIERTO, no por valor: «aprovechamos que un partido se
# vaya a dar con seguridad; si no estamos seguros, no apostamos». La pregunta
# por segmento es entonces: dentro de un grupo de favoritos (los gigantes tipo
# Bayern o Arsenal, la casa 70 %+…), ¿la señal del rival separa a los que
# fallan? Se mide la PRECISIÓN (cuánto falla el favorito con la señal contra
# sin ella, en el mismo segmento) y la COBERTURA (qué parte de los tropiezos
# del segmento caza). Para no confundir la señal con la ventaja, el «sin la
# señal» se toma del MISMO tramo fino de ventaja (0,1) y condición. Con
# tramos de 0,25 quedaba un sesgo de ~0,7 pts cuando la señal va pegada a la
# ventaja chica (lo encontró el test con 30.000 casos sintéticos).

SEGMENTOS = {
    "favorito por nivel (0,5+)": lambda c: c["porNivel"],
    "muy favorito por nivel (1,0+)": lambda c: c["porNivel"] and c["ventaja"] >= 1.0,
    "gigante: nivel 3,5+ y 1,0+ de ventaja": lambda c: c["porNivel"] and c["ventaja"] >= 1.0 and (c["nivel"] or 0) >= 3.5,
    "gigante con 1,5+ de ventaja": lambda c: c["porNivel"] and c["ventaja"] >= 1.5 and (c["nivel"] or 0) >= 3.5,
    "gigante de local": lambda c: c["porNivel"] and c["ventaja"] >= 1.0 and (c["nivel"] or 0) >= 3.5 and c["local"],
    "casa 70 %+": lambda c: c["porCasa"] and c["p"] >= 0.70,
    "casa 80 %+": lambda c: c["porCasa"] and c["p"] >= 0.80,
}
SENALES_SEG = {
    "forma 6+": SENALES["forma"],
    "forma 7+": lambda r: r["formaNoPierde"] is not None and r["formaNoPierde"] >= 0.7,
    "perfil 60 %+": SENALES["perfil"],
    "perfil 70 %+": lambda r: r["perfilNoPierde"] is not None and r["perfilNoPierde"] >= 0.7,
    "forma 6+ y perfil 60 %+": lambda r: SENALES["forma"](r) and SENALES["perfil"](r),
}


def _bin(c: dict) -> tuple:
    v = c["ventaja"] if c["ventaja"] is not None else -9.0
    return (min(int(v / 0.1), 30), c["local"])


def separa_en(seg: list[dict], senal, semilla: int = 7) -> dict:
    """Con la señal contra sin ella, dentro del segmento. `diferencia` = cuánto más
    falla el favorito con la señal que lo esperado por los SIN señal de su mismo
    tramo fino de ventaja y condición (> 0 = la señal marca dónde no entrar)."""
    con = [c for c in seg if senal(c["riv"])]
    sin = [c for c in seg if not senal(c["riv"])]
    tropiezos = sum(1 for c in seg if not c["gana"])
    out = {"n": len(seg), "conSenal": len(con), "parte": round(len(con) / len(seg), 4) if seg else None,
           "fallaCon": round(sum(1 for c in con if not c["gana"]) / len(con), 4) if con else None,
           "fallaSin": round(sum(1 for c in sin if not c["gana"]) / len(sin), 4) if sin else None,
           "caza": round(sum(1 for c in con if not c["gana"]) / tropiezos, 4) if tropiezos else None}
    base = defaultdict(lambda: [0, 0])
    for c in sin:
        base[_bin(c)][0] += 0 if c["gana"] else 1
        base[_bin(c)][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n >= 10}
    por_eq = defaultdict(lambda: [0.0, 0])
    for c in con:
        if _bin(c) in esp:
            por_eq[c["team"]][0] += (0 if c["gana"] else 1) - esp[_bin(c)]
            por_eq[c["team"]][1] += 1
    b = _boot(list(por_eq.values()), semilla)
    if b:
        out.update({"diferencia": round(b[0], 4), "ic95": [round(b[1], 4), round(b[2], 4)], "separa": b[1] > 0 or b[2] < 0})
    return out


def segmentos(cs: list[dict]) -> list[dict]:
    nv = [c for c in cs if c["porNivel"]]
    corte = sorted(c["fecha"] for c in nv)[len(nv) // 2] if nv else ""
    out = []
    for sn, sf in SEGMENTOS.items():
        seg = [c for c in cs if c["ventaja"] is not None and sf(c)]
        if len(seg) < 50:
            out.append({"segmento": sn, "n": len(seg), "sinDato": "menos de 50 favoritos"})
            continue
        fila = {"segmento": sn, "n": len(seg), "falla": round(sum(1 for c in seg if not c["gana"]) / len(seg), 4), "senales": []}
        for kn, kf in SENALES_SEG.items():
            r = separa_en(seg, kf)
            r["porEpoca"] = [separa_en([c for c in seg if c["fecha"] < corte], kf),
                             separa_en([c for c in seg if c["fecha"] >= corte], kf)]
            r["seRepite"] = bool(r.get("separa")) and all(
                e.get("separa") and e["diferencia"] > 0 for e in r["porEpoca"]) and r["diferencia"] > 0
            fila["senales"].append({"senal": kn, **r})
        out.append(fila)
    return out


def evaluar(cs: list[dict]) -> dict:
    if not cs:
        return {"casos": 0, "lectura": "sin casos"}
    nv = [c for c in cs if c["porNivel"]]
    corte = sorted(c["fecha"] for c in nv)[len(nv) // 2] if nv else ""
    sin_cuota = [c for c in nv if c["p"] is None]
    out = {"casos": len(cs), "porNivel": len(nv), "porCasa": sum(1 for c in cs if c["porCasa"]),
           "desde": cs[0]["fecha"], "hasta": cs[-1]["fecha"], "corteEpoca": corte, "senales": []}
    for clave, f in SENALES.items():
        out["senales"].append({
            "senal": clave, "nombre": NOMBRES[clave],
            "nivel": residuo_nivel(cs, f),
            "nivelSinCuota": residuo_nivel(sin_cuota, f),
            "nivelPorEpoca": [{"epoca": et, **residuo_nivel(sub, f)} for et, sub in
                              ((f"antes de {corte}", [c for c in nv if c["fecha"] < corte]),
                               (f"desde {corte}", [c for c in nv if c["fecha"] >= corte]))],
            "casa": residuo_casa(cs, f),
            "casaPorTramo": [{"tramo": tn, **residuo_casa(cs, f, (a, b))} for a, b, tn in TRAMOS_CASA],
            "porLiga": por_liga(cs, f),
        })
    out["segmentos"] = segmentos(cs)
    out["lectura"] = lectura(out)
    return out


def lectura(r: dict) -> str:
    partes = []
    for s in r["senales"]:
        n = s["nivelSinCuota"]
        if "residuo" not in n:
            partes.append(f"{s['senal']}: sin muestra")
            continue
        ep = [e for e in s["nivelPorEpoca"] if "residuo" in e]
        repite = len(ep) == 2 and all(e["separa"] and e["residuo"] > 0 for e in ep)
        lg = s["porLiga"]
        partes.append(f"{s['senal']}: {n['residuo']:+.1%} contra el nivel en los años sin cuota (IC {n['ic95'][0]:+.1%} a "
                      f"{n['ic95'][1]:+.1%}, n {n['n']}), " + ("separa y se repite" if n["separa"] and repite
                                                               else "separa sin repetirse" if n["separa"] else "no separa")
                      + f"; ligas en el sentido del candidato {lg['conMasDerrotas']} de {lg['conMasDerrotas'] + lg['conMenos']}"
                      f" (p signo {lg['pSigno']})")
    return " · ".join(partes)


# ── de dónde salen los datos ─────────────────────────────────────────────────

def _copas(fixture_ids: list[int]) -> set[int]:
    """`escala.copas_nacionales` en lotes: con decenas de miles de ids una sola
    consulta pasa el límite de variables de SQLite y su except devuelve {} callado."""
    from backend.analisis.escala import copas_nacionales
    ids = sorted(set(fixture_ids))
    out: set[int] = set()
    for i in range(0, len(ids), 500):
        out |= set(copas_nacionales(ids[i:i + 500]))
    return out


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
    r.update({"equipos": len(historias), "partidosConCuota": len(cuotas), "copasNacionalesFuera": len(excluir)})
    return r


def _imprimir(r: dict) -> None:
    if not r.get("casos"):
        print(r.get("lectura"))
        return
    print(f"\n{r['casos']:,} favoritos ({r['porNivel']:,} por nivel, {r['porCasa']:,} por casa) · {r['desde']} → {r['hasta']}"
          f" · copas nacionales fuera: {r.get('copasNacionalesFuera', 0)}\n")

    def x(d):
        if "residuo" not in d:
            return f"n {d.get('n', 0):>6}  {d.get('sinDato', '')}"
        roi = f"  roi {d['roiPlano']:+.1%}" if d.get("roiPlano") is not None else ""
        return (f"n {d['n']:>6}  {d['residuo']:+6.1%}  IC [{d['ic95'][0]:+.1%}, {d['ic95'][1]:+.1%}]"
                + ("  SEPARA" if d["separa"] else "") + roi)
    for s in r["senales"]:
        print(f"RIVAL: {s['nombre']}")
        print(f"  contra el nivel, todo            {x(s['nivel'])}")
        print(f"  contra el nivel, años sin cuota  {x(s['nivelSinCuota'])}")
        for e in s["nivelPorEpoca"]:
            print(f"    {e['epoca']:<28}   {x(e)}")
        print(f"  contra la casa                   {x(s['casa'])}")
        for t in s["casaPorTramo"]:
            print(f"    {t['tramo']:<28}   {x(t)}")
        lg = s["porLiga"]
        print(f"  por liga: {lg['conMasDerrotas']} en el sentido del candidato, {lg['conMenos']} al revés (p signo {lg['pSigno']})")
        for f in lg["ligas"][:12]:
            print(f"    liga {f['liga']:<6} n {f['n']:>5}  {f['residuo']:+.1%}")
        print()
    print("POR SEGMENTO: dónde no entrar (falla con la señal / sin ella; caza = parte de los tropiezos con la señal;"
          " diferencia = contra los sin señal del mismo tramo fino de ventaja)")
    for sg in r.get("segmentos", []):
        if "falla" not in sg:
            print(f"  {sg['segmento']}: {sg.get('sinDato')}")
            continue
        print(f"  {sg['segmento']} · n {sg['n']:,} · el favorito no gana {sg['falla']:.1%}")
        for k in sg["senales"]:
            d = (f"  diferencia {k['diferencia']:+.1%} IC [{k['ic95'][0]:+.1%}, {k['ic95'][1]:+.1%}]"
                 + ("  SEPARA" if k["separa"] else "") + ("  y se repite" if k["seRepite"] else "")) if "diferencia" in k else ""
            if k["conSenal"]:
                print(f"    {k['senal']:<24} {k['parte']:4.0%} de los partidos · falla {k['fallaCon']:5.1%} con, "
                      f"{(k['fallaSin'] or 0):5.1%} sin · caza {(k['caza'] or 0):4.0%} de los tropiezos{d}")
    print()
    print("(residuo > 0 = con ese rival el favorito NO GANA más de lo esperado: el sentido del candidato)")
    print(r["lectura"])


def main() -> None:
    ap = argparse.ArgumentParser(description="¿El rival que resiste le baja la victoria al favorito? Por liga, sin cuota y con burbujas")
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
