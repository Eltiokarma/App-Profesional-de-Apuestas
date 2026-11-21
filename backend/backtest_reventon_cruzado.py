"""¿Cuándo revienta una burbuja? Lo que el riesgo no mira: los GOLES de la
misma racha y la PERIODICIDAD (REVENTON §20, 21/11/2026).

El usuario, para cerrar el capítulo de las burbujas: «¿lo hiciste con las
constantes generales o también con las específicas de local y visita? La
constante de goles anotados o recibidos puede influir en la otra. Y a que las
burbujas revientan se le añaden consideraciones de periodicidad. El frontend
nunca estuvo orientado a predecir cuándo revienta».

Lo que ya estaba medido: el riesgo calibrado con las tres familias (total,
local y visita: §12.2, §14.1) separa poco (AUC ~0,63) y la K misma no
puntúa; las K de goles no mejoran el 1X2 (§13.4) y las burbujas de goles no
predicen su propio partido siguiente (§15). Lo que NO: (1) si los goles de la
racha de RESULTADO avisan su corte —ganar recibiendo, ganar por la mínima,
perder sin anotar—; (2) si la burbuja revienta cuando llega a su LARGO
TÍPICO, y si el típico de la temporada o del último año sirve más que el de
toda la historia (la gráfica dibuja los dos, §10-bis, sin backtest).

Por cada burbuja abierta de las tres familias antes de un partido (la misma
observación de `backtest_burbuja.observar_equipo`, sin fuga: historia
anterior y nivel del rival previo), se mide:

1. **Periodicidad**: cuánto revienta según el largo de la racha contra su
   largo típico (mediana de las burbujas del mismo signo ya cerradas), con
   tres referencias: toda la historia, la temporada en curso y los últimos
   365 días.
2. **Goles de la racha**: con racha + (viene ganando): ganó TODA la racha
   recibiendo gol; ganó toda la racha por un gol; la valla invicta en el
   último; viene anotando 5+ seguidos. Con racha − (viene perdiendo): perdió
   toda la racha por un gol; no anotó en los dos últimos; anotó en toda la
   racha.
3. Cada señal contra los sin señal de la **misma familia, signo y nivel de
   riesgo** (lo que el riesgo de hoy ya dice): cuánto más revienta, IC por
   equipos, por época.
4. **Cuándo no apostar** (el criterio del método: acierto, nunca la casa):
   el favorito (0,5+ de nivel sobre el rival) que viene ganando, en su
   familia total. Que su burbuja reviente ES que no gane: falla con / sin
   cada señal, qué parte de los partidos marca y de sus tropiezos caza.

Lee, no escribe. No cambia ningún punto ni la tarjeta: mide.

    python -m backend.backtest_reventon_cruzado --padron --json $SAD_DATA_DIR/reventon_cruzado.json
"""
from __future__ import annotations

import argparse
import json
import os
import random
from bisect import bisect_left
from collections import defaultdict
from statistics import median

from backend.analisis import burbuja

BOOTSTRAP = 500
FAVORITO = 0.5
TRAMOS_LARGO = ((0.0, 0.5, "menos de la mitad"), (0.5, 1.0, "de la mitad al típico"),
                (1.0, 1.5, "del típico a 1,5×"), (1.5, 2.0, "de 1,5× a 2×"), (2.0, 99.0, "2× o más"))
REFERENCIAS = ("global", "temporada", "anio")
NOMBRE_REF = {"global": "toda la historia", "temporada": "la temporada en curso", "anio": "los últimos 365 días"}

SENALES = {
    "+": {
        "gana recibiendo en toda la racha": lambda o: o["racha"] and all(gc > 0 for _, gc in o["racha"]),
        "gana por la mínima en toda la racha": lambda o: o["racha"] and all(gf - gc == 1 for gf, gc in o["racha"]),
        "valla invicta en el último": lambda o: o["racha"] and o["racha"][-1][1] == 0,
        "viene anotando 5+ seguidos": lambda o: o["anotaSeguidos"] >= 5,
        "racha de 2+ partidos": lambda o: len(o["racha"]) >= 2,
    },
    "-": {
        "pierde por la mínima en toda la racha": lambda o: o["racha"] and all(gc - gf == 1 for gf, gc in o["racha"]),
        "sin anotar en los dos últimos": lambda o: o["sinAnotar"] >= 2,
        "anotó en toda la racha": lambda o: o["racha"] and all(gf > 0 for gf, _ in o["racha"]),
        "racha de 2+ partidos": lambda o: len(o["racha"]) >= 2,
    },
}


# ── lo que se sabía antes de cada partido ───────────────────────────────────

def _en(fila: dict, familia: str) -> bool:
    return familia == "total" or fila.get("condicion") == ("Local" if familia == "local" else "Visita")


def rasgos(filas: list[dict], familia: str) -> dict:
    """{fixtureId: rasgos previos} para la familia: los goles de la racha abierta
    y los largos típicos (global, temporada, 365 días) de las burbujas del
    mismo signo ya cerradas. Una pasada por la historia (sin rehacer los
    episodios por cada partido)."""
    cerrados, _, _ = burbuja.episodios(filas, familia)
    fechas_cierre = [str(r["fecha"]) for r in cerrados]      # cronológicas
    inicio_temp: dict = {}
    for f in filas:
        t = f.get("temporada")
        if t is not None and t not in inicio_temp:
            inicio_temp[t] = str(f["fecha"])
    out = {}
    previas: list[dict] = []
    for f in filas:
        fecha = str(f["fecha"])
        if _en(f, familia):
            hasta = bisect_left(fechas_cierre, fecha)            # cerradas ANTES de este partido
            antes = cerrados[:hasta]
            # la racha abierta: del final hacia atrás, mientras el resultado tenga el mismo signo
            racha, signo = [], None
            for p in reversed(previas):
                s = (p["golesFavor"] > p["golesContra"]) - (p["golesFavor"] < p["golesContra"])
                if s == 0 or (signo is not None and s != signo):
                    break
                signo = s
                racha.append((int(p["golesFavor"]), int(p["golesContra"])))
            racha.reverse()
            anota = sin = 0
            for p in reversed(previas):
                if p["golesFavor"] > 0:
                    anota += 1
                else:
                    break
            for p in reversed(previas):
                if p["golesFavor"] == 0:
                    sin += 1
                else:
                    break
            t0 = inicio_temp.get(f.get("temporada"), "")
            un_anio = f"{int(fecha[:4]) - 1}{fecha[4:10]}"

            def tipico(sel):
                return {sg: (median(r["partidos"] for r in sel if r["signo"] == sg)
                             if sum(1 for r in sel if r["signo"] == sg) >= 3 else None) for sg in "+-"}
            out[f["fixtureId"]] = {
                "racha": racha, "anotaSeguidos": anota, "sinAnotar": sin,
                "tipico": {"global": tipico(antes),
                           "temporada": tipico([r for r in antes if t0 and str(r["fecha"]) >= t0]),
                           "anio": tipico([r for r in antes if str(r["fecha"])[:10] >= un_anio])},
            }
            previas.append(f)
    return out


def observaciones(obs_burbuja: list[dict], rasgos_por_familia: dict) -> list[dict]:
    """Junta la observación de `observar_equipo` (familia, signo, riesgo, si
    reventó, ventaja) con los rasgos de goles y de largo típico."""
    out = []
    for o in obs_burbuja:
        r = rasgos_por_familia.get(o["familia"], {}).get(o["fixtureId"])
        if not r:
            continue
        # la racha de goles debe ser la de la burbuja: si los largos no coinciden
        # (un amistoso u otra regla de la K) se toman solo los últimos `partidos`
        racha = r["racha"][-o["partidos"]:] if o["partidos"] else []
        out.append({"coincide": len(r["racha"]) == o["partidos"], "team": o["equipoId"], "fecha": str(o["fecha"])[:10], "familia": o["familia"],
                    "signo": o["signo"], "riesgo": o["nivel"], "revento": bool(o["reventoAhora"]),
                    "partidos": o["partidos"], "gFavor": o.get("gFavor"),
                    "racha": racha, "anotaSeguidos": r["anotaSeguidos"], "sinAnotar": r["sinAnotar"],
                    "tipico": {ref: r["tipico"][ref][o["signo"]] for ref in REFERENCIAS}})
    return out


# ── la cuenta ────────────────────────────────────────────────────────────────

def _boot(por_eq: list[list[float]], semilla: int = 7):
    eq = [e for e in por_eq if e[1]]
    n = sum(e[1] for e in eq)
    if n < 30 or len(eq) < 5:
        return None
    media = sum(e[0] for e in eq) / n
    rnd = random.Random(semilla)
    bs = sorted(sum(e[0] for e in m) / sum(e[1] for e in m)
                for m in ([eq[rnd.randrange(len(eq))] for _ in eq] for _ in range(BOOTSTRAP)))
    return media, bs[int(0.025 * BOOTSTRAP)], bs[int(0.975 * BOOTSTRAP) - 1]


def _tramo(x: float) -> str:
    for a, b, n in TRAMOS_LARGO:
        if a <= x < b:
            return n
    return TRAMOS_LARGO[-1][2]


def periodicidad(obs: list[dict]) -> dict:
    """Cuánto revienta según el largo de la racha contra su típico, con cada
    referencia. `separa` = revienta en «2× o más» − en «menos de la mitad»."""
    out = {}
    for ref in REFERENCIAS:
        tramos = defaultdict(lambda: [0, 0])
        con = 0
        for o in obs:
            t = o["tipico"][ref]
            if not t:
                continue
            con += 1
            k = _tramo(o["partidos"] / t)
            tramos[k][0] += o["revento"]
            tramos[k][1] += 1
        filas = [{"tramo": n, "n": tramos[n][1], "revienta": round(tramos[n][0] / tramos[n][1], 4) if tramos[n][1] else None}
                 for _, _, n in TRAMOS_LARGO]
        bajo, alto = filas[0]["revienta"], filas[-1]["revienta"]
        out[ref] = {"conTipico": con, "tramos": filas,
                    "separa": round(alto - bajo, 4) if bajo is not None and alto is not None else None}
    return out


def senal(obs: list[dict], f, semilla: int = 7) -> dict:
    """Con la señal contra sin ella, en la MISMA familia, signo y nivel de riesgo:
    `diferencia` = cuánto más revienta con la señal que lo esperado (IC por equipos)."""
    clave = lambda o: (o["familia"], o["signo"], o["riesgo"])  # noqa: E731
    base = defaultdict(lambda: [0, 0])
    con = [o for o in obs if f(o)]
    for o in obs:
        if not f(o):
            base[clave(o)][0] += o["revento"]
            base[clave(o)][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n >= 20}
    por_eq = defaultdict(lambda: [0.0, 0])
    for o in con:
        if clave(o) in esp:
            por_eq[o["team"]][0] += o["revento"] - esp[clave(o)]
            por_eq[o["team"]][1] += 1
    sin = [o for o in obs if not f(o)]
    r = {"n": len(obs), "conSenal": len(con), "parte": round(len(con) / len(obs), 4) if obs else None,
         "revientaCon": round(sum(o["revento"] for o in con) / len(con), 4) if con else None,
         "revientaSin": round(sum(o["revento"] for o in sin) / len(sin), 4) if sin else None}
    b = _boot(list(por_eq.values()), semilla)
    if b:
        r.update({"diferencia": round(b[0], 4), "ic95": [round(b[1], 4), round(b[2], 4)], "separa": b[1] > 0 or b[2] < 0})
    return r


def _epocas(obs: list[dict], f) -> bool:
    if not obs:
        return False
    corte = sorted(o["fecha"] for o in obs)[len(obs) // 2]
    ep = [senal([o for o in obs if o["fecha"] < corte], f), senal([o for o in obs if o["fecha"] >= corte], f)]
    return all(e.get("separa") and e["diferencia"] > 0 for e in ep)


def no_apostar(obs: list[dict], f) -> dict:
    """El favorito (0,5+ de nivel) que viene ganando, familia total: que su burbuja
    reviente es que no gane. Falla con / sin la señal, qué marca y qué caza."""
    fav = [o for o in obs if o["familia"] == "total" and o["signo"] == "+" and (o["gFavor"] or 0) >= FAVORITO]
    con = [o for o in fav if f(o)]
    sin = [o for o in fav if not f(o)]
    tropiezos = sum(o["revento"] for o in fav)
    return {"n": len(fav), "parte": round(len(con) / len(fav), 4) if fav else None,
            "fallaCon": round(sum(o["revento"] for o in con) / len(con), 4) if con else None,
            "fallaSin": round(sum(o["revento"] for o in sin) / len(sin), 4) if sin else None,
            "caza": round(sum(o["revento"] for o in con) / tropiezos, 4) if tropiezos else None}


def evaluar(obs: list[dict]) -> dict:
    if not obs:
        return {"observaciones": 0, "lectura": "sin observaciones"}
    out = {"observaciones": len(obs), "desde": min(o["fecha"] for o in obs), "hasta": max(o["fecha"] for o in obs),
           "rachaCoincide": round(sum(1 for o in obs if o.get("coincide", True)) / len(obs), 4),
           "revientaBase": round(sum(o["revento"] for o in obs) / len(obs), 4),
           "periodicidad": {}, "goles": [], "noApostar": []}
    for fam in ("total", "local", "visita"):
        for sg in "+-":
            sub = [o for o in obs if o["familia"] == fam and o["signo"] == sg]
            if sub:
                out["periodicidad"][f"{fam} {sg}"] = periodicidad(sub)
    for sg, senales in SENALES.items():
        sub = [o for o in obs if o["signo"] == sg]
        for nombre, f in senales.items():
            r = senal(sub, f)
            r["seRepite"] = bool(r.get("separa")) and r.get("diferencia", 0) > 0 and _epocas(sub, f)
            out["goles"].append({"signo": sg, "senal": nombre, **r})
    largo = {f"racha ≥ {x}× su típico ({NOMBRE_REF[ref]})": (lambda o, ref=ref, x=x: bool(o["tipico"][ref]) and o["partidos"] >= x * o["tipico"][ref])
             for ref in REFERENCIAS for x in (1.0, 2.0)}
    for nombre, f in {**SENALES["+"], **largo}.items():
        out["noApostar"].append({"senal": nombre, **no_apostar(obs, f)})
    out["lectura"] = lectura(out)
    return out


def lectura(r: dict) -> str:
    partes = []
    p = r["periodicidad"].get("total +")
    if p:
        mejor = max(REFERENCIAS, key=lambda ref: p[ref]["separa"] if p[ref]["separa"] is not None else -9)
        partes.append("periodicidad (total, racha +): " + ", ".join(
            f"{NOMBRE_REF[ref]} separa {p[ref]['separa']:+.1%}" for ref in REFERENCIAS if p[ref]["separa"] is not None)
            + f"; la que más, {NOMBRE_REF[mejor]}")
    sirven = [f"{g['senal']} ({g['signo']}, {g['diferencia']:+.1%})" for g in r["goles"] if g.get("seRepite")]
    partes.append("goles de la racha que agregan al riesgo y se repiten: " + (", ".join(sirven) if sirven else "ninguno"))
    avisan = [f"{x['senal']} ({x['fallaCon']:.0%} contra {x['fallaSin']:.0%})" for x in r["noApostar"]
              if x["fallaCon"] is not None and x["fallaSin"] is not None and x["fallaCon"] - x["fallaSin"] >= 0.05]
    partes.append("favorito que viene ganando, no apostar con: " + ("; ".join(avisan) if avisan else "ninguna señal de 5+ pts"))
    return " · ".join(partes)


# ── de dónde salen los datos ─────────────────────────────────────────────────

def observar(equipos: list[int]) -> list[dict]:
    from backend.app import constantes_de
    from backend.backtest_burbuja import observar_equipo
    obs = []
    for t in equipos:
        filas = list(reversed(constantes_de(t, 500)))
        rs = {fam: rasgos(filas, fam) for fam in ("total", "local", "visita")}
        obs += observaciones(observar_equipo(t, 1), rs)
    return obs


def correr_padron() -> dict:
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.backtest_burbuja import _equipos, padron
    from backend.backtest_dc_record import MIN_PREFIJO
    equipos = _equipos(MIN_PREFIJO + 2, set(padron()))
    r = evaluar(observar(equipos))
    r["equipos"] = len(equipos)
    return r


def _imprimir(r: dict) -> None:
    if not r.get("observaciones"):
        print(r.get("lectura"))
        return
    print(f"\n{r['observaciones']:,} burbujas abiertas antes de un partido (total, local y visita) · {r['desde']} → {r['hasta']}"
          f" · revientan en el partido {r['revientaBase']:.1%}"
          f" · la racha de goles tiene el largo de la burbuja en el {r['rachaCoincide']:.1%}\n")
    print("1. PERIODICIDAD: ¿revienta cuando llega a su largo típico? (revienta = no sigue en ese partido)")
    for k, p in r["periodicidad"].items():
        print(f"  {k}")
        for ref in REFERENCIAS:
            x = p[ref]
            fila = " · ".join(f"{t['tramo']} {t['revienta']:.0%} (n {t['n']:,})" for t in x["tramos"] if t["n"])
            sep = f"  separa {x['separa']:+.1%}" if x["separa"] is not None else ""
            print(f"    típico de {NOMBRE_REF[ref]:<22} {fila}{sep}")
    print("\n2. LOS GOLES DE LA RACHA: ¿avisan el corte más allá del riesgo de hoy? (dif = contra los sin señal de la misma"
          " familia, signo y nivel de riesgo)")
    for g in r["goles"]:
        d = (f"  dif {g['diferencia']:+.1%} [{g['ic95'][0]:+.1%}, {g['ic95'][1]:+.1%}]" + ("  SEPARA" if g["separa"] else "")
             + ("  y se repite" if g.get("seRepite") else "")) if "diferencia" in g else ""
        print(f"  racha {g['signo']} · {g['senal']:<40} marca {g['parte']:5.1%} · revienta {g['revientaCon']:.1%} con,"
              f" {g['revientaSin']:.1%} sin{d}")
    print("\n3. CUÁNDO NO APOSTAR: el favorito (0,5+ de nivel) que viene ganando (falla = no gana; caza = parte de sus"
          " tropiezos que la señal marca)")
    for x in r["noApostar"]:
        if x["fallaCon"] is None:
            continue
        print(f"  {x['senal']:<52} marca {x['parte']:5.1%} · falla {x['fallaCon']:5.1%} con, {x['fallaSin']:5.1%} sin"
              f" · caza {x['caza']:4.0%}  (n {x['n']:,})")
    print()
    print(r["lectura"])


def main() -> None:
    ap = argparse.ArgumentParser(description="¿Cuándo revienta una burbuja? Goles de la racha y periodicidad")
    ap.add_argument("--padron", action="store_true", help="historias y niveles del padrón (en el servidor)")
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
