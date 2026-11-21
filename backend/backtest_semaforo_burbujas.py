"""¿Las burbujas SOLAS pintan un semáforo que el pasado sostenga? Y el cruce
de las dos burbujas del partido (REVENTON §19, 21/11/2026).

El usuario, tras Sportivo Ameliano 1-0 Sportivo Luqueño (1632063): «no hemos
analizado las burbujas como tal y no le hemos vuelto un skill que pueda tener
un semáforo confiable con información del pasado». Y: «cuando se cruzan dos
burbujas que están creciendo, una tiene que reventar».

Lo que había medido (REVENTON §13-§14): el riesgo dice si una RACHA se corta
(AUC 0,63 sin fuga) y las K no agregan al 1X2 del motor. Lo que NO se midió:

1. **El semáforo de las tarjetas.** El semáforo de hoy (`analisis/semaforo.py`)
   sale de las espinas que ESCRIBE el analista: solo se puede medir hacia
   adelante (~10 % de no-verdes, 15 en una semana). Acá se pinta con la
   ESPINA DE LA TARJETA de cada lado (`burbuja.espina_tarjeta`, la guía
   calibrada: el movimiento más probable de la K total), con la MISMA regla:
   rojo = la tarjeta del elegido dice que pierde; amarillo = la del elegido
   dice empate o la del rival dice que gana o empata; verde = la del elegido
   dice que gana y la del rival no; sin dato = el elegido sin burbuja abierta.
   Eso se puede medir en 2019-2026: si con rojo o amarillo el elegido pierde
   más, el semáforo tiene un piso que no depende de cómo escriba el analista;
   si no, su valor está en lo que el analista agrega a la tarjeta (y se sigue
   midiendo hacia adelante).
2. **Señales sueltas del elegido y del rival** (riesgo, extremo, signo).
3. **El cruce de las dos burbujas** (las totales de los dos, abiertas):
   - ACUERDAN: signos opuestos (uno viene ganando y el otro perdiendo). Un
     mismo resultado sigue las dos (gana el de la racha +) y cualquier otro
     las revienta a las dos: Ameliano (−23, cerca del extremo) contra
     Luqueño (+15, en su récord), y ganó Ameliano.
   - CHOCAN: mismo signo (los dos ganando, o los dos perdiendo). Una de las
     dos revienta por definición; la pregunta útil es si sale MÁS EMPATE
     (que corta las dos) que el esperado (1.7 a del skill, candidato v4.5).
   Por cuántas están en el extremo o cerca (0, 1, 2), contra lo esperado por
   el nivel (el mismo tramo de 0,1 de ventaja y condición, en todos los
   partidos).

El ELEGIDO es el favorito: por nivel (más nivel previo que el rival, todos
los años) o por casa (la probabilidad más alta entre local y visita, que es
como se elige y en qué tramo se apuesta). Lo que se mide es SOLO lo que el
usuario usa: **cuándo no apostar** (21/11/2026: «no nos importa si la casa ya
cobra… solo queremos saber cuándo no apostar»). Por señal y segmento: cuánto
más pierde o empata el elegido con ella que sin ella (`avisa`, con IC por
equipos), qué parte de los partidos marca, qué parte de los tropiezos caza,
si se repite en las dos épocas y en cuántas ligas. Nada contra la casa.

Sin fuga: la burbuja, su riesgo y la tarjeta salen de
`backtest_burbuja.observar_equipo` (historia anterior, nivel del rival
PREVIO); los niveles de los dos, de antes del partido. Copas nacionales y
amistosos fuera de la evaluación. Lee, no escribe. No cambia ningún punto ni
el semáforo: mide.

    python -m backend.backtest_semaforo_burbujas --padron --json $SAD_DATA_DIR/semaforo_burbujas.json
"""
from __future__ import annotations

import argparse
import json
import os
import random
from collections import defaultdict

from backend.analisis import burbuja
from backend.backtest_rival_resiste import AMISTOSOS, _copas, _signo

BOOTSTRAP = 500
MIN_LIGA = 30
RIESGO_ALTO = ("alto", "muy alto")


# ── el estado de cada burbuja antes del partido ─────────────────────────────

def estado_de_obs(o: dict) -> dict:
    """De una observación de `observar_equipo` (familia total) al estado que se usa
    acá, con la tarjeta dicha como resultado del equipo (gana · empata · pierde)."""
    mov = burbuja._movimiento_esperado("total", o["signo"], o["nivel"])
    t = burbuja.espina_tarjeta(o["signo"], mov)
    tarjeta = None if not t else {"positiva": "gana", "cero": "empata", "negativa": "pierde"}[t["lectura"]]
    return {"signo": o["signo"], "riesgo": o["nivel"], "extremo": bool(o.get("extremo")),
            "cerca": bool(o.get("cerca")), "partidos": o.get("partidos"), "tarjeta": tarjeta,
            "fuerte": bool(t and t["fuerza"] == "fuerte")}


def franja(b: dict | None) -> bool:
    return bool(b and (b["extremo"] or b["cerca"]))


# ── los partidos ────────────────────────────────────────────────────────────

def partidos(lados: dict, burb: dict, cuotas: dict | None = None, excluir: set | None = None) -> list[dict]:
    """Un registro por partido con los dos lados (nivel previo de los dos) y su
    burbuja total abierta (None si no había: venía de empatar). `lados` es el de
    `backtest_rival_resiste.lados`; `burb[(fixture, equipo)]` = `estado_de_obs`."""
    por_fx = defaultdict(dict)
    for (fx, team), o in lados.items():
        por_fx[fx][team] = o
    out = []
    for fx, par in por_fx.items():
        if (excluir and fx in excluir) or len(par) != 2:
            continue
        (ta, a), (tb, b) = par.items()
        if a["local"] == b["local"] or a["rival"] != tb or b["rival"] != ta:
            continue
        (tl, l), (tv, v) = ((ta, a), (tb, b)) if a["local"] else ((tb, b), (ta, a))
        if l["nivel"] is None or v["nivel"] is None:
            continue
        c = (cuotas or {}).get(fx)
        out.append({"fixtureId": fx, "fecha": l["fecha"], "liga": l["liga"], "tL": tl, "tV": tv,
                    "nL": l["nivel"], "nV": v["nivel"],
                    "res": "L" if l["gana"] else "E" if l["empata"] else "V",
                    "p": (c[0], c[1], c[2]) if c else None, "margen": c[4] if c else None,
                    "bL": burb.get((fx, tl)), "bV": burb.get((fx, tv))})
    out.sort(key=lambda m: (m["fecha"], m["fixtureId"]))
    return out


def elegidos(ms: list[dict], por: str) -> list[dict]:
    """El favorito de cada partido, por `nivel` (más nivel previo) o por `casa`
    (la probabilidad más alta entre local y visita, sin margen)."""
    out = []
    for m in ms:
        if por == "casa":
            if not m["p"]:
                continue
            lado = "L" if m["p"][0] >= m["p"][2] else "V"
            p = m["p"][0] if lado == "L" else m["p"][2]
        else:
            if m["nL"] == m["nV"]:
                continue
            lado = "L" if m["nL"] > m["nV"] else "V"
            p = None if not m["p"] else (m["p"][0] if lado == "L" else m["p"][2])
        loc = lado == "L"
        ventaja = (m["nL"] - m["nV"]) * (1 if loc else -1)
        out.append({"fixtureId": m["fixtureId"], "fecha": m["fecha"], "liga": m["liga"],
                    "team": m["tL"] if loc else m["tV"], "local": loc, "ventaja": ventaja, "p": p,
                    "margen": m["margen"], "gana": m["res"] == lado, "empata": m["res"] == "E",
                    "yo": m["bL"] if loc else m["bV"], "riv": m["bV"] if loc else m["bL"]})
    return out


# ── el semáforo de las tarjetas y las señales del elegido ───────────────────

def color(c: dict) -> str:
    """La regla del semáforo de hoy (`analisis/semaforo.py`) con la TARJETA en
    lugar de la espina del analista."""
    yo, riv = c["yo"], c["riv"]
    if not yo or not yo["tarjeta"]:
        return "sinDato"
    if yo["tarjeta"] == "pierde":
        return "rojo"
    if yo["tarjeta"] == "empata" or (riv and riv["tarjeta"] in ("gana", "empata")):
        return "amarillo"
    return "verde"


def _acuerdan(c, contra: bool) -> bool:
    """Las dos en el extremo o cerca y con signos opuestos: un solo resultado
    sigue las dos. `contra` = ese resultado es que el elegido PIERDA."""
    yo, riv = c["yo"], c["riv"]
    if not (franja(yo) and franja(riv)) or yo["signo"] == riv["signo"]:
        return False
    return yo["signo"] == ("-" if contra else "+")


SENALES = {
    "semáforo de las tarjetas: no verde": lambda c: color(c) in ("amarillo", "rojo"),
    "semáforo de las tarjetas: rojo": lambda c: color(c) == "rojo",
    "el elegido viene perdiendo (racha −)": lambda c: bool(c["yo"]) and c["yo"]["signo"] == "-",
    "el elegido sin burbuja (viene de empatar)": lambda c: not c["yo"],
    "el elegido con racha + en riesgo alto o muy alto": lambda c: bool(c["yo"]) and c["yo"]["signo"] == "+" and c["yo"]["riesgo"] in RIESGO_ALTO,
    "el elegido con racha + en el extremo o cerca": lambda c: franja(c["yo"]) and c["yo"]["signo"] == "+",
    "el rival viene ganando (racha +)": lambda c: bool(c["riv"]) and c["riv"]["signo"] == "+",
    "el rival con racha + en el extremo o cerca": lambda c: franja(c["riv"]) and c["riv"]["signo"] == "+",
    "el rival con racha − en el extremo o cerca": lambda c: franja(c["riv"]) and c["riv"]["signo"] == "-",
    "las dos en el extremo o cerca (cualquiera)": lambda c: franja(c["yo"]) and franja(c["riv"]),
    "las dos en el extremo, acuerdan CON el elegido": lambda c: _acuerdan(c, contra=False),
    "las dos en el extremo, acuerdan CONTRA el elegido": lambda c: _acuerdan(c, contra=True),
    "las dos en el extremo, chocan (mismo signo)": lambda c: franja(c["yo"]) and franja(c["riv"]) and c["yo"]["signo"] == c["riv"]["signo"],
    "las dos en riesgo alto o muy alto": lambda c: bool(c["yo"] and c["riv"]) and c["yo"]["riesgo"] in RIESGO_ALTO and c["riv"]["riesgo"] in RIESGO_ALTO,
}

SEGMENTOS = {
    "favorito por nivel (todos)": ("nivel", lambda c: True),
    "favorito por nivel 0,5+": ("nivel", lambda c: c["ventaja"] >= 0.5),
    "favorito por nivel 1,0+": ("nivel", lambda c: c["ventaja"] >= 1.0),
    "favorito de la casa (todos)": ("casa", lambda c: True),
    "casa 45-60 % (el medio)": ("casa", lambda c: 0.45 <= c["p"] < 0.60),
    "casa 60 %+": ("casa", lambda c: c["p"] >= 0.60),
    "casa 70 %+": ("casa", lambda c: c["p"] >= 0.70),
}


def _bin(c: dict) -> tuple:
    return (max(-30, min(int(c["ventaja"] / 0.1), 30)), c["local"])


def _boot(por_eq: list[list[float]], semilla: int = 7) -> tuple[float, float, float] | None:
    eq = [e for e in por_eq if e[1]]
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


def _boot_dif(con: list[dict], sin: list[dict], semilla: int = 7) -> tuple[float, float, float] | None:
    """falla con − falla sin, con IC remuestreando EQUIPOS (los dos grupos a la vez)."""
    if len(con) < 30 or len(sin) < 30:
        return None
    eq = defaultdict(lambda: [0, 0, 0, 0])      # [falla con, n con, falla sin, n sin]
    for c in con:
        eq[c["team"]][0] += 0 if c["gana"] else 1
        eq[c["team"]][1] += 1
    for c in sin:
        eq[c["team"]][2] += 0 if c["gana"] else 1
        eq[c["team"]][3] += 1
    v = list(eq.values())
    if len(v) < 5:
        return None

    def d(m):
        nc, ns = sum(e[1] for e in m), sum(e[3] for e in m)
        return (sum(e[0] for e in m) / nc - sum(e[2] for e in m) / ns) if nc and ns else 0.0
    rnd = random.Random(semilla)
    bs = sorted(d([v[rnd.randrange(len(v))] for _ in v]) for _ in range(BOOTSTRAP))
    return d(v), bs[int(0.025 * BOOTSTRAP)], bs[int(0.975 * BOOTSTRAP) - 1]


def separa(seg: list[dict], senal, semilla: int = 7) -> dict:
    """Con la señal contra sin ella, DENTRO del segmento: lo que se juzga es
    `avisa` = falla con − falla sin (cuánto más pierde o empata el elegido
    cuando la señal aparece), con IC por equipos, la parte de los partidos que
    marca y la parte de los tropiezos que caza. El método apuesta por ACIERTO:
    si la casa ya lo cobra no importa (usuario, 21/11/2026: «solo queremos saber
    cuándo no apostar»). `diferencia` (contra los sin señal del mismo tramo de
    ventaja) queda como dato: dice si la señal es algo más que «favorito más
    flojo», no si sirve para no apostar."""
    con = [c for c in seg if senal(c)]
    sin = [c for c in seg if not senal(c)]
    tropiezos = sum(1 for c in seg if not c["gana"])
    out = {"n": len(seg), "conSenal": len(con), "parte": round(len(con) / len(seg), 4) if seg else None,
           "fallaCon": round(sum(1 for c in con if not c["gana"]) / len(con), 4) if con else None,
           "fallaSin": round(sum(1 for c in sin if not c["gana"]) / len(sin), 4) if sin else None,
           "caza": round(sum(1 for c in con if not c["gana"]) / tropiezos, 4) if tropiezos else None}
    a = _boot_dif(con, sin, semilla)
    if a:
        out.update({"avisa": round(a[0], 4), "avisaIc95": [round(a[1], 4), round(a[2], 4)], "avisaSepara": a[1] > 0 or a[2] < 0})
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


def _epocas(seg: list[dict], senal) -> tuple[list[dict], bool]:
    if not seg:
        return [], False
    corte = sorted(c["fecha"] for c in seg)[len(seg) // 2]
    ep = [separa([c for c in seg if c["fecha"] < corte], senal), separa([c for c in seg if c["fecha"] >= corte], senal)]
    return ep, all(e.get("avisaSepara") and e["avisa"] > 0 for e in ep)


def por_liga(seg: list[dict], senal) -> dict:
    """En cada liga con MIN_LIGA+ casos con la señal: no ganó − lo esperado (sin
    la señal, mismo tramo, todas las ligas). Cuántas van en el sentido de
    «no entrar» y la prueba del signo."""
    base = defaultdict(lambda: [0, 0])
    for c in seg:
        if not senal(c):
            base[_bin(c)][0] += 0 if c["gana"] else 1
            base[_bin(c)][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n >= 10}
    ligas = defaultdict(list)
    for c in seg:
        if senal(c) and _bin(c) in esp:
            ligas[c["liga"]].append((0 if c["gana"] else 1) - esp[_bin(c)])
    filas = sorted(({"liga": lg, "n": len(v), "residuo": round(sum(v) / len(v), 4)}
                    for lg, v in ligas.items() if len(v) >= MIN_LIGA), key=lambda x: -x["n"])
    pos = sum(1 for f in filas if f["residuo"] > 0)
    return {"ligas": filas, "enContra": pos, "aFavor": len(filas) - pos, "pSigno": _signo(pos, len(filas))}


def semaforo_tabla(cs: list[dict]) -> list[dict]:
    """Por color: n y cuánto gana el elegido (lo que importa para no apostar), y
    lo esperado por su nivel (todos los del mismo tramo) como dato."""
    base = defaultdict(lambda: [0, 0])
    for c in cs:
        base[_bin(c)][0] += 1 if c["gana"] else 0
        base[_bin(c)][1] += 1
    out = []
    for col in ("verde", "amarillo", "rojo", "sinDato"):
        sub = [c for c in cs if color(c) == col]
        if not sub:
            out.append({"color": col, "n": 0})
            continue
        esp = sum(base[_bin(c)][0] / base[_bin(c)][1] for c in sub) / len(sub)
        out.append({"color": col, "n": len(sub), "parte": round(len(sub) / len(cs), 4),
                    "gana": round(sum(c["gana"] for c in sub) / len(sub), 4), "esperadoNivel": round(esp, 4)})
    return out


# ── el cruce de las dos burbujas, por partido ───────────────────────────────

def cruce(ms: list[dict]) -> list[dict]:
    """Partidos con las dos burbujas totales abiertas. ACUERDAN (signos
    opuestos): ¿sale el resultado que sigue las dos (gana el de la racha +) lo
    que dice el nivel? CHOCAN (mismo signo): ¿sale más empate? Por
    cuántas están en el extremo o cerca."""
    gana_base = defaultdict(lambda: [0, 0])     # (tramo de ventaja del lado, local) → [ganó, n]
    emp_base = defaultdict(lambda: [0, 0])      # tramo de |ventaja| → [empate, n]
    for m in ms:
        d = m["nL"] - m["nV"]
        for loc, v, g in ((True, d, m["res"] == "L"), (False, -d, m["res"] == "V")):
            k = (max(-30, min(int(v / 0.1), 30)), loc)
            gana_base[k][0] += g
            gana_base[k][1] += 1
        ka = min(int(abs(d) / 0.1), 30)
        emp_base[ka][0] += m["res"] == "E"
        emp_base[ka][1] += 1
    grupos = defaultdict(list)
    for m in ms:
        bl, bv = m["bL"], m["bV"]
        if not bl or not bv:
            continue
        tipo = "acuerdan" if bl["signo"] != bv["signo"] else ("chocan +" if bl["signo"] == "+" else "chocan −")
        grupos[(tipo, int(franja(bl)) + int(franja(bv)))].append(m)
    out = []
    for (tipo, nf), sub in sorted(grupos.items()):
        fila = {"tipo": tipo, "enExtremo": nf, "n": len(sub)}
        por_eq = defaultdict(lambda: [0.0, 0])
        obs = esp = 0.0
        for m in sub:
            d = m["nL"] - m["nV"]
            if tipo == "acuerdan":
                loc = m["bL"]["signo"] == "+"             # el resultado que sigue las dos: gana el de la racha +
                v = d if loc else -d
                k = (max(-30, min(int(v / 0.1), 30)), loc)
                e = gana_base[k][0] / gana_base[k][1]
                o = m["res"] == ("L" if loc else "V")
                team = m["tL"] if loc else m["tV"]
            else:
                ka = min(int(abs(d) / 0.1), 30)
                e = emp_base[ka][0] / emp_base[ka][1]
                o = m["res"] == "E"
                team = m["tL"]
            obs += o
            esp += e
            por_eq[team][0] += o - e
            por_eq[team][1] += 1
        fila.update({"mide": "gana el de la racha + (sigue las dos)" if tipo == "acuerdan" else "empate (corta las dos)",
                     "observado": round(obs / len(sub), 4), "esperadoNivel": round(esp / len(sub), 4)})
        b = _boot(list(por_eq.values()))
        if b:
            fila.update({"diferencia": round(b[0], 4), "ic95": [round(b[1], 4), round(b[2], 4)], "separa": b[1] > 0 or b[2] < 0})
        out.append(fila)
    return out


# ── todo junto ──────────────────────────────────────────────────────────────

def evaluar(ms: list[dict]) -> dict:
    if not ms:
        return {"partidos": 0, "lectura": "sin partidos"}
    pob = {"nivel": elegidos(ms, "nivel"), "casa": elegidos(ms, "casa")}
    out = {"partidos": len(ms), "desde": ms[0]["fecha"], "hasta": ms[-1]["fecha"],
           "conCuota": sum(1 for m in ms if m["p"]),
           "conLasDos": sum(1 for m in ms if m["bL"] and m["bV"]),
           "semaforo": {"nivel": semaforo_tabla(pob["nivel"]), "casa": semaforo_tabla(pob["casa"])},
           "cruce": cruce(ms), "segmentos": []}
    for sn, (p, f) in SEGMENTOS.items():
        seg = [c for c in pob[p] if f(c)]
        fila = {"segmento": sn, "n": len(seg), "senales": []}
        if len(seg) < 50:
            fila["sinDato"] = "menos de 50 elegidos"
            out["segmentos"].append(fila)
            continue
        fila["falla"] = round(sum(1 for c in seg if not c["gana"]) / len(seg), 4)
        for kn, kf in SENALES.items():
            r = separa(seg, kf)
            if not r["conSenal"]:
                continue
            r["porEpoca"], r["seRepite"] = _epocas(seg, kf)
            r["seRepite"] = r["seRepite"] and bool(r.get("avisaSepara")) and r["avisa"] > 0
            if p == "nivel" and sn == "favorito por nivel (todos)":
                r["porLiga"] = por_liga(seg, kf)
            fila["senales"].append({"senal": kn, **r})
        out["segmentos"].append(fila)
    out["lectura"] = lectura(out)
    return out


def lectura(r: dict) -> str:
    partes = []
    tn = {x["color"]: x for x in r["semaforo"]["nivel"]}
    if tn.get("verde", {}).get("n") and tn.get("rojo", {}).get("n"):
        partes.append(f"semáforo de las tarjetas (favorito por nivel): verde gana {tn['verde']['gana']:.1%} "
                      f"(esperado {tn['verde']['esperadoNivel']:.1%}), rojo {tn['rojo']['gana']:.1%} "
                      f"(esperado {tn['rojo']['esperadoNivel']:.1%})")
    for f in r["cruce"]:
        if f["enExtremo"] == 2 and "diferencia" in f:
            partes.append(f"{f['tipo']} con las dos en el extremo: {f['mide']} {f['observado']:.1%} contra "
                          f"{f['esperadoNivel']:.1%} por nivel ({f['diferencia']:+.1%}, "
                          + ("SEPARA" if f["separa"] else "no separa") + f", n {f['n']})")
    for s in r["segmentos"]:
        avisan = [f"{k['senal']} ({k['fallaCon']:.0%} contra {k['fallaSin']:.0%})" for k in s.get("senales", [])
                  if k.get("avisaSepara") and k["avisa"] > 0]
        if avisan:
            partes.append(f"{s['segmento']}: no apostar con " + "; ".join(avisan))
    return " · ".join(partes)


# ── de dónde salen los datos ────────────────────────────────────────────────

def correr_padron() -> dict:
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.backtest_burbuja import nivel_rival_previo, observar_equipo
    from backend.backtest_burbuja_1x2 import cuotas_1x2
    from backend.backtest_dc_record import historias_padron
    from backend.backtest_rival_resiste import lados
    historias = historias_padron()
    burb = {}
    for t in historias:
        for o in observar_equipo(t, 1):
            if o["familia"] == "total":
                burb[(o["fixtureId"], t)] = estado_de_obs(o)
    fxs = sorted({f["fixtureId"] for h in historias.values() for f in h["filas"]
                  if f.get("ligaId") not in AMISTOSOS and f.get("golesFavor") is not None})
    cuotas = cuotas_1x2(fxs)
    excluir = _copas(fxs)
    r = evaluar(partidos(lados(historias, nivel_rival_previo), burb, cuotas, excluir))
    r.update({"equipos": len(historias), "burbujas": len(burb), "copasNacionalesFuera": len(excluir)})
    return r


def _x(d: dict) -> str:
    if "diferencia" not in d:
        return ""
    return (f"  dif {d['diferencia']:+.1%} [{d['ic95'][0]:+.1%}, {d['ic95'][1]:+.1%}]"
            + ("  SEPARA" if d["separa"] else ""))


def _imprimir(r: dict) -> None:
    if not r.get("partidos"):
        print(r.get("lectura"))
        return
    print(f"\n{r['partidos']:,} partidos · {r['conLasDos']:,} con las dos burbujas abiertas · {r['conCuota']:,} con cuota"
          f" · {r['desde']} → {r['hasta']} · copas nacionales fuera: {r.get('copasNacionalesFuera', 0)}\n")
    print("1. EL SEMÁFORO DE LAS TARJETAS (la regla de hoy con la tarjeta en lugar de la espina del analista)")
    for p, nombre in (("nivel", "favorito por nivel, todos los años"), ("casa", "favorito de la casa, con cuota")):
        print(f"  {nombre}:")
        for x in r["semaforo"][p]:
            if not x["n"]:
                continue
            print(f"    {x['color']:<9} {x['parte']:5.1%} de los partidos (n {x['n']:,}) · el elegido gana {x['gana']:.1%}"
                  f" (por su nivel se esperaba {x['esperadoNivel']:.1%})")
    print("\n2. EL CRUCE DE LAS DOS BURBUJAS (por cuántas en el extremo o cerca: 0, 1, 2)")
    for f in r["cruce"]:
        print(f"  {f['tipo']:<9} {f['enExtremo']} en extremo · n {f['n']:>6,} · {f['mide']}: {f['observado']:.1%}"
              f" contra {f['esperadoNivel']:.1%} por nivel{_x(f)}")
    print("\n3. POR SEGMENTO: CUÁNDO NO APOSTAR (falla = el elegido no gana; avisa = falla con − falla sin, con IC por"
          " equipos; caza = parte de los tropiezos que la señal marca; se repite = avisa en las dos épocas)")
    for sg in r["segmentos"]:
        if "falla" not in sg:
            print(f"  {sg['segmento']}: {sg.get('sinDato')}")
            continue
        print(f"  {sg['segmento']} · n {sg['n']:,} · el elegido no gana {sg['falla']:.1%}")
        for k in sg["senales"]:
            lg = k.get("porLiga")
            liga = f"  ligas {lg['enContra']}/{lg['enContra'] + lg['aFavor']} (p {lg['pSigno']})" if lg and lg["ligas"] else ""
            av = (f"  avisa {k['avisa']:+.1%} [{k['avisaIc95'][0]:+.1%}, {k['avisaIc95'][1]:+.1%}]"
                  + ("  SÍ" if k["avisaSepara"] and k["avisa"] > 0 else "  al revés" if k["avisaSepara"] else "")) if "avisa" in k else "  (pocos casos)"
            print(f"    {k['senal']:<50} marca {k['parte']:5.1%} · falla {k['fallaCon']:5.1%} con, {(k['fallaSin'] or 0):5.1%} sin"
                  f"{av} · caza {(k['caza'] or 0):4.0%}" + ("  y se repite" if k.get("seRepite") else "") + liga)
    print()
    print("(avisa > 0 = con la señal el elegido pierde o empata MÁS: no apostar. «al revés» = con la señal falla MENOS)")
    print(r["lectura"])


def main() -> None:
    ap = argparse.ArgumentParser(description="¿Las burbujas solas pintan un semáforo que el pasado sostenga? Y el cruce de las dos")
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
