"""Backtest hacia atrás del reventón de burbuja (docs/REVENTON.md §8).

Recorre la historia de cada equipo y, en cada partido donde había una burbuja
ABIERTA, reconstruye la guía tal como estaba ANTES de ese partido (solo con
las filas previas, y con el rival real de ese partido como «próximo») para
compararla con lo que pasó: ¿reventó en ese partido (o dentro de --horizonte
partidos de la condición)?

Si la guía sirve, la tasa de reventón tiene que CRECER de «bajo» a «muy alto»
y cada señal (K ≥ mediana, racha ≥ mediana, rival en zona) tiene que reventar
más cuando está encendida que cuando no. Con eso se calibran los puntos y la
tolerancia de zona, y se contrasta la regla «a nivel alto o bajo mandan las
globales, a nivel medio las específicas»: se compara la separación de tasas
de la familia que manda contra la de las que no mandan.

Sin fuga: el nivel del equipo (para el bin) se toma del último nivel con
fecha ANTERIOR al partido, y la estabilidad va «sin dato» porque la plantilla
de hoy no es la de entonces — el backtest mide el RIESGO, no la confianza.

    python -m backend.backtest_burbuja                     # todos los equipos con ≥ 12 filas
    python -m backend.backtest_burbuja --muestra 200 --horizonte 2
    python -m backend.backtest_burbuja --liga 281 --json salida.json
    SAD_DATA_DIR=demo_data python -m backend.backtest_burbuja   # contra la demo
"""
from __future__ import annotations

import argparse
import json
import random
from bisect import bisect_left

from backend import db
from backend.analisis import burbuja
from backend.app import constantes_de, niveles_de

NIVELES = ["bajo", "medio", "alto", "muy alto"]
FAMILIAS = ("total", "local", "visita")
MIN_PREFIJO = 10          # filas previas mínimas para evaluar una burbuja


def _equipos(min_filas: int) -> list[int]:
    rows = db.query("constants", "SELECT team_id, COUNT(*) AS n FROM constants GROUP BY team_id HAVING n >= ?",
                    (min_filas,))
    return [r["team_id"] for r in rows]


def _bin_a_fecha(niveles: list[dict], fecha: str) -> int:
    """Último bin con fecha < fecha (sin fuga). Sin niveles previos: bin de 0.5 = 0."""
    fechas = [n["fecha"] for n in niveles]
    i = bisect_left(fechas, fecha)
    return niveles[i - 1]["bin"] if i > 0 else 0


def _revento(fila: dict, familia: str, signo: str) -> bool:
    v = float(fila["fusion"][burbuja.CLAVE_FUSION[familia]])
    return v == 0 or (v > 0) != (signo == "+")


def _en_condicion(fila: dict, familia: str) -> bool:
    return familia == "total" or fila["condicion"] == ("Local" if familia == "local" else "Visita")


def observar_equipo(team_id: int, horizonte: int, min_prefijo: int = MIN_PREFIJO) -> list[dict]:
    """Una observación por (partido con burbuja abierta, familia que ese partido mueve)."""
    filas = list(reversed(constantes_de(team_id, 500)))
    niveles = list(reversed(niveles_de(team_id, 500)))
    estab = burbuja.estabilidad_de(None, "1970-01-01")
    obs = []
    for i in range(min_prefijo, len(filas)):
        fila = filas[i]
        prefijo = filas[:i]
        bin_ = _bin_a_fecha(niveles, fila["fecha"])
        proximo = {
            "fixtureId": fila["fixtureId"], "fecha": fila["fecha"], "rivalId": fila["rivalId"],
            "rival": fila["rivalNombre"], "condicion": "L" if fila["condicion"] == "Local" else "V",
            "nivelRival": float(fila["nivelRival"]),
        }
        mandan = burbuja.mandan_de(bin_, proximo)
        for familia in FAMILIAS:
            if not _en_condicion(fila, familia):
                continue
            fam = burbuja._analizar_familia(prefijo, familia, proximo, estab)
            act, rg = fam["actual"], fam["riesgo"]
            if not act or not rg:
                continue
            # qué pasó: reventó en este partido o en los próximos `horizonte` de la condición
            siguientes = [f for f in filas[i:] if _en_condicion(f, familia)][:horizonte]
            revento = any(_revento(f, familia, act["signo"]) for f in siguientes)
            revento_ahora = _revento(fila, familia, act["signo"])
            base = fam["historial"]["positivo" if act["signo"] == "+" else "negativo"]
            obs.append({
                "equipoId": team_id, "fixtureId": fila["fixtureId"], "fecha": fila["fecha"],
                "familia": familia, "signo": act["signo"], "manda": familia in mandan["familias"],
                "bin": bin_, "nivel": rg["nivel"], "puntos": rg["puntos"], "n": base["n"] if base else 0,
                "kGeMediana": bool(base) and abs(act["k"]) >= base["kPico"]["mediana"],
                "kGeMax": bool(base) and abs(act["k"]) >= base["kPico"]["max"],
                "rachaGeMediana": bool(base) and act["partidos"] >= base["partidos"]["mediana"],
                "rivalEnZona": None if not fam["rival"] else fam["rival"]["enZona"],
                "distanciaRival": None if not fam["rival"] else fam["rival"]["distancia"],
                "kActual": abs(act["k"]), "partidos": act["partidos"],
                "revento": revento, "reventoAhora": revento_ahora,
            })
    return obs


# ── agregación ───────────────────────────────────────────────────────────────

def _tasa(sub: list[dict]) -> dict:
    n = len(sub)
    r = sum(1 for o in sub if o["revento"])
    return {"n": n, "reventones": r, "tasa": round(r / n, 3) if n else None}


def _auc(obs: list[dict], clave: str) -> float | None:
    """AUC de Mann-Whitney: P(puntos del que reventó > puntos del que no)."""
    pos = [o[clave] for o in obs if o["revento"]]
    neg = [o[clave] for o in obs if not o["revento"]]
    if not pos or not neg:
        return None
    neg_s = sorted(neg)
    tot = 0.0
    for p in pos:
        lo = bisect_left(neg_s, p)
        hi = bisect_left(neg_s, p + 1e-12)
        tot += lo + 0.5 * (hi - lo)
    # empates: bisect_left(p) cuenta los estrictamente menores; los iguales van a mitad
    return round(tot / (len(pos) * len(neg)), 3)


def _separacion(sub: list[dict]) -> float | None:
    """Tasa de (alto + muy alto) − tasa de bajo: cuánto separa la guía en ese grupo."""
    alto = [o for o in sub if o["nivel"] in ("alto", "muy alto")]
    bajo = [o for o in sub if o["nivel"] == "bajo"]
    if not alto or not bajo:
        return None
    return round(_tasa(alto)["tasa"] - _tasa(bajo)["tasa"], 3)


def resumir(obs: list[dict], horizonte: int) -> dict:
    con_base = [o for o in obs if o["nivel"] != "sin base"]
    por_nivel = {nv: _tasa([o for o in con_base if o["nivel"] == nv]) for nv in NIVELES}
    tasas = [por_nivel[nv]["tasa"] for nv in NIVELES if por_nivel[nv]["tasa"] is not None]
    monotona = all(a <= b for a, b in zip(tasas, tasas[1:])) and len(tasas) >= 2
    senales = {}
    for s in ("kGeMediana", "kGeMax", "rachaGeMediana", "rivalEnZona"):
        con = [o for o in con_base if o[s] is True]
        sin = [o for o in con_base if o[s] is False]
        senales[s] = {"encendida": _tasa(con), "apagada": _tasa(sin),
                      "lift": round(_tasa(con)["tasa"] - _tasa(sin)["tasa"], 3) if con and sin else None}
    familias = {f: {"todas": _tasa([o for o in con_base if o["familia"] == f]),
                    "separacion": _separacion([o for o in con_base if o["familia"] == f])} for f in FAMILIAS}
    manda = {k: {"todas": _tasa(g), "separacion": _separacion(g), "auc": _auc(g, "puntos")}
             for k, g in (("manda", [o for o in con_base if o["manda"]]),
                          ("noManda", [o for o in con_base if not o["manda"]]))}
    # la regla de nivel, mirada del otro lado: en equipos de nivel medio, ¿la
    # específica separa más que la total? y en extremos, ¿al revés?
    medio = [o for o in con_base if 2 < o["bin"] < 7]
    extremo = [o for o in con_base if not (2 < o["bin"] < 7)]
    regla_nivel = {
        "nivelMedio": {"total": _separacion([o for o in medio if o["familia"] == "total"]),
                       "especificas": _separacion([o for o in medio if o["familia"] != "total"])},
        "nivelExtremo": {"total": _separacion([o for o in extremo if o["familia"] == "total"]),
                         "especificas": _separacion([o for o in extremo if o["familia"] != "total"])},
    }
    return {
        "horizonte": horizonte,
        "observaciones": len(obs),
        "sinBase": len(obs) - len(con_base),
        "tasaBase": _tasa(con_base),
        "porSigno": {s: _tasa([o for o in con_base if o["signo"] == s]) for s in ("+", "-")},
        "porNivel": por_nivel,
        "monotona": monotona,
        "porPuntos": {str(p): _tasa([o for o in con_base if o["puntos"] == p]) for p in range(0, 8)},
        "aucPuntos": _auc(con_base, "puntos"),
        "senales": senales,
        "porFamilia": familias,
        "reglaManda": manda,
        "reglaNivel": regla_nivel,
        "porMuestra": {"n<3": _tasa([o for o in con_base if o["n"] < 3]),
                       "3-5": _tasa([o for o in con_base if 3 <= o["n"] < 6]),
                       "≥6": _tasa([o for o in con_base if o["n"] >= 6])},
    }


def correr(equipos: list[int], horizonte: int, min_prefijo: int = MIN_PREFIJO) -> tuple[list[dict], dict]:
    obs = []
    for t in equipos:
        obs.extend(observar_equipo(t, horizonte, min_prefijo))
    return obs, resumir(obs, horizonte)


# ── informe ──────────────────────────────────────────────────────────────────

def _pct(t: dict) -> str:
    return "—" if t["tasa"] is None else f"{100 * t['tasa']:5.1f}%"


def imprimir(r: dict):
    h = r["horizonte"]
    print(f"\n=== Backtest del reventón · horizonte {h} partido{'s' if h != 1 else ''} ===")
    print(f"observaciones: {r['observaciones']} (sin base: {r['sinBase']}) · "
          f"tasa base de reventón: {_pct(r['tasaBase'])} sobre {r['tasaBase']['n']}")
    print(f"burbujas +: {_pct(r['porSigno']['+'])} ({r['porSigno']['+']['n']}) · "
          f"burbujas −: {_pct(r['porSigno']['-'])} ({r['porSigno']['-']['n']})")

    print("\n— por nivel de riesgo (debe crecer) —")
    for nv in NIVELES:
        t = r["porNivel"][nv]
        print(f"  {nv:9s} {_pct(t)}  n={t['n']}")
    print(f"  monótona: {'sí' if r['monotona'] else 'NO'} · AUC de los puntos: {r['aucPuntos']}")

    print("\n— por puntos —")
    for p, t in r["porPuntos"].items():
        if t["n"]:
            print(f"  {p} pts  {_pct(t)}  n={t['n']}")

    print("\n— cada señal encendida vs apagada (lift = diferencia de tasa) —")
    for s, v in r["senales"].items():
        print(f"  {s:15s} on {_pct(v['encendida'])} (n={v['encendida']['n']}) · off {_pct(v['apagada'])} "
              f"(n={v['apagada']['n']}) · lift {v['lift']}")

    print("\n— por familia (separación = tasa alto/muy alto − tasa bajo) —")
    for f, v in r["porFamilia"].items():
        print(f"  {f:7s} tasa {_pct(v['todas'])} n={v['todas']['n']} · separación {v['separacion']}")

    print("\n— regla «qué constante manda» —")
    for k, v in r["reglaManda"].items():
        print(f"  {k:8s} tasa {_pct(v['todas'])} n={v['todas']['n']} · separación {v['separacion']} · AUC {v['auc']}")
    rn = r["reglaNivel"]
    print(f"  nivel medio  → separación total {rn['nivelMedio']['total']} · específicas {rn['nivelMedio']['especificas']}")
    print(f"  nivel extremo→ separación total {rn['nivelExtremo']['total']} · específicas {rn['nivelExtremo']['especificas']}")

    print("\n— por tamaño de la muestra de reventones previos —")
    for k, t in r["porMuestra"].items():
        print(f"  {k:4s} {_pct(t)}  n={t['n']}")

    print("\nLectura: si «alto/muy alto» no revienta más que «bajo», los puntos no están "
          "calibrados para esta base; si una señal tiene lift ≤ 0, no aporta y hay que "
          "bajarle el peso. Si en nivel medio las específicas separan más que la total "
          "(y al revés en los extremos), la regla de qué constante manda se confirma.")


def main():
    ap = argparse.ArgumentParser(description="Backtest hacia atrás del reventón de burbuja")
    ap.add_argument("--muestra", type=int, default=0, help="equipos al azar (0 = todos)")
    ap.add_argument("--liga", type=int, help="solo equipos con filas en esta league_id")
    ap.add_argument("--horizonte", type=int, default=1, help="revienta dentro de N partidos de la condición (default 1)")
    ap.add_argument("--min-filas", type=int, default=12, help="filas mínimas por equipo")
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--json", help="guardar el resumen en este archivo")
    a = ap.parse_args()

    equipos = _equipos(a.min_filas)
    if a.liga:
        equipos = [t for t in equipos if db.query_one(
            "discreto", "SELECT 1 FROM processed_matches WHERE equipo_id=? AND league_id=? LIMIT 1", (t, a.liga))]
    if a.muestra and a.muestra < len(equipos):
        random.seed(a.semilla)
        equipos = random.sample(equipos, a.muestra)
    print(f"equipos evaluados: {len(equipos)}")
    _, resumen = correr(equipos, a.horizonte)
    imprimir(resumen)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(resumen, f, ensure_ascii=False, indent=1)
        print(f"\nresumen guardado en {a.json}")


if __name__ == "__main__":
    main()
