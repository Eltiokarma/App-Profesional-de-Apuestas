"""¿El favorito gana MENOS cuando su racha SIN PERDER de la condición de hoy
está en su récord? (pedido del usuario, 21/11/2026, tras Bayern 1-1 Köln)

Bayern llegaba con 21 partidos de local sin perder, uno más que su récord
(20), y empató en casa con el 15.º. La app lo mostraba como dato («no es
terreno raro») y el §15 de docs/REVENTON.md dice que una racha en su récord
SE SOSTIENE algo más: es cierto, pero el §15 preguntó si la burbuja «no
pierde» sigue, no si el favorito GANA. Un empate no corta la racha sin perder
y sí corta la victoria: las dos cosas pueden ser verdad a la vez.

Medido el 21/11 sobre 73 equipos bajados de /constantes (sin el padrón y sin
cuotas): el muy favorito no ganó el 29 % con la racha en récord contra el
20 % debajo (n 148 y 887), casi todo por empates, y se repitió en las dos
mitades del tiempo. Esto lo mide como corresponde:

1. en el PADRÓN entero (no 73 equipos alemanes y europeos);
2. con los niveles ANTERIORES al partido de los dos lados (el `nivelRival`
   de la fila ya trae el resultado: §13.1 de REVENTON, `nivel_rival_previo`);
3. estandarizado por fuerza y condición: lo esperado de cada caso sale de
   los casos SIN récord del mismo tramo de ventaja de nivel y la misma
   condición; el residuo (observado − esperado) del grupo con récord, con
   intervalo por bootstrap de EQUIPOS;
4. por época (las dos mitades del tiempo) y por tramo de ventaja;
5. CONTRA LA CUOTA (solo en el servidor): residuo contra la probabilidad de
   ganar del mercado sin margen, por tramo de cuota, y lo que habría dado
   apostar a ese favorito a la cuota media. Si la casa ya lo cobra, es
   lectura y no apuesta.

El récord es el de `backtest_familias.perfil_dc` (iguala o supera el máximo
previo, con ≥ 3 rachas sin perder ya cortadas en la condición). Los
amistosos CUENTAN en la historia (decisión del usuario, 14/10/2026) pero no
se evalúan como partido: no tienen cuota ni se analizan. Lee, no escribe.

    python -m backend.backtest_dc_record --padron          # en el servidor, con las .db y las cuotas
    python -m backend.backtest_dc_record --desde-dir carpeta # c/<id>.json (/constantes) y n/<id>.json (/niveles), sin cuotas
    python -m backend.backtest_dc_record --padron --json salida.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import random
from bisect import bisect_left
from collections import defaultdict

from backend.backtest_familias import MIN_PREFIJO, MIN_RACHAS_RECORD

AMISTOSOS = {667}
BOOTSTRAP = 500
# ventaja de nivel propio − rival ANTES del partido (los mismos cortes que
# burbuja.FAVORITO = 0.5 y MUY_FAVORITO = 1.0)
TRAMOS_VENTAJA = ((-99.0, 0.0, "no favorito (< 0)"), (0.0, 0.5, "parejo (0-0,5)"),
                  (0.5, 1.0, "favorito (0,5-1,0)"), (1.0, 99.0, "muy favorito (≥ 1,0)"))
TRAMOS_MERCADO = ((0.0, 0.5, "< 50 %"), (0.5, 0.7, "50-70 %"), (0.7, 1.01, "70 %+"))


# ── la racha sin perder de cada condición, incremental y sin fuga ────────────

class EstadoDC:
    """La burbuja de «no pierde» de una condición, como `perfil_dc` pero
    incremental (el padrón tiene ~700 equipos × 500 partidos: recalcular el
    prefijo en cada partido es cuadrático). `test_backtest_dc_record` la
    compara contra `perfil_dc` en secuencias al azar."""

    def __init__(self):
        self.partidos = 0
        self.ultimo = None                 # valor del último partido (True = no perdió)
        self.largo = 0
        self.maximos = {True: 0, False: 0}
        self.cortadas = {True: 0, False: 0}

    def record(self) -> int:
        """2 supera · 1 iguala · 0 no (o sin base), del valor del último partido."""
        v = self.ultimo
        if v is None or self.cortadas[v] < MIN_RACHAS_RECORD:
            return 0
        return 2 if self.largo > self.maximos[v] else 1 if self.largo == self.maximos[v] else 0

    def burbuja(self) -> int:
        """Con signo: + racha sin perder · − racha perdiendo (como `perfil_dc`)."""
        if self.ultimo is None:
            return 0
        return self.largo if self.ultimo else -self.largo

    def sumar(self, no_perdio: bool) -> None:
        if self.ultimo is not None and no_perdio != self.ultimo:
            self.maximos[self.ultimo] = max(self.maximos[self.ultimo], self.largo)
            self.cortadas[self.ultimo] += 1
            self.largo = 1
        else:
            self.largo += 1
        self.ultimo = no_perdio
        self.partidos += 1


def _nivel_antes(fechas: list[str], niveles: list[float], fecha: str) -> float | None:
    """El nivel ESTRICTAMENTE anterior a la fecha (el de la fecha ya trae el partido)."""
    i = bisect_left(fechas, fecha)
    return niveles[i - 1] if i > 0 else None


def _tramo(x: float, tramos) -> str:
    for a, b, nombre in tramos:
        if a <= x < b:
            return nombre
    return tramos[-1][2]


def observaciones(historias: dict[int, dict], nivel_rival=None) -> list[dict]:
    """Un caso por equipo y partido oficial: lo que se sabía ANTES (racha sin
    perder de la condición de hoy, su récord, los dos niveles previos) y lo que
    pasó. `historias[team] = {"filas": [constantes asc], "niveles": [niveles asc]}`.
    `nivel_rival(rival_id, fecha)` da el nivel previo de un rival sin historia
    en `historias` (en el servidor, `nivel_rival_previo`); sin él, ese caso sale."""
    niv = {t: ([n["fecha"] for n in h["niveles"]], [float(n["nivel"]) for n in h["niveles"]])
           for t, h in historias.items()}
    obs = []
    for team, h in historias.items():
        if team not in niv:
            continue
        estados = {"Local": EstadoDC(), "Visita": EstadoDC()}
        for f in sorted(h["filas"], key=lambda r: str(r.get("fecha") or "")):
            gf, gc, cond = f.get("golesFavor"), f.get("golesContra"), f.get("condicion")
            if gf is None or gc is None or cond not in estados:
                continue
            e = estados[cond]
            fecha = str(f.get("fecha") or "")
            if f.get("ligaId") not in AMISTOSOS and e.partidos >= MIN_PREFIJO:
                propio = _nivel_antes(*niv[team], fecha)
                rid = f.get("rivalId")
                if rid in niv:
                    rival = _nivel_antes(*niv[rid], fecha)
                elif nivel_rival is not None and rid is not None:
                    rival = nivel_rival(rid, fecha)
                else:
                    rival = None
                if propio is not None and rival is not None:
                    rec = e.record()
                    racha = e.burbuja()
                    obs.append({
                        "fixtureId": f.get("fixtureId"), "team": team, "fecha": fecha[:10],
                        "local": cond == "Local", "liga": f.get("ligaId"),
                        "ventaja": float(propio) - float(rival), "nivel": float(propio),
                        "racha": racha, "enRecord": racha > 0 and rec >= 1, "supera": racha > 0 and rec == 2,
                        "gana": int(gf) > int(gc), "empata": int(gf) == int(gc),
                    })
            e.sumar(int(gf) >= int(gc))
    obs.sort(key=lambda o: (o["fecha"], o["team"]))
    return obs


# ── la cuenta ────────────────────────────────────────────────────────────────

def _wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - r) / d, 3), round((c + r) / d, 3)]


def _grupo(sub: list[dict]) -> dict:
    n = len(sub)
    ng = sum(1 for o in sub if not o["gana"])
    em = sum(1 for o in sub if o["empata"])
    return {"n": n, "noGana": round(ng / n, 4) if n else None, "intervalo": _wilson(ng, n),
            "empata": round(em / n, 4) if n else None,
            "pierde": round((ng - em) / n, 4) if n else None}


def _residuo_por_equipo(obs: list[dict], esperado) -> dict:
    """Residuo medio (no ganó − lo esperado) de los casos CON récord, con
    intervalo por bootstrap de equipos. Positivo = gana menos de lo esperado."""
    por_eq = defaultdict(lambda: [0.0, 0])
    for o in obs:
        if o["enRecord"]:
            e = por_eq[o["team"]]
            e[0] += (0 if o["gana"] else 1) - esperado(o)
            e[1] += 1
    equipos = list(por_eq.values())
    n = sum(e[1] for e in equipos)
    if n < 20 or len(equipos) < 5:
        return {"n": n, "equipos": len(equipos), "sinDato": "menos de 20 casos con récord o de 5 equipos"}
    media = sum(e[0] for e in equipos) / n
    rnd = random.Random(7)
    boots = []
    for _ in range(BOOTSTRAP):
        m = [equipos[rnd.randrange(len(equipos))] for _ in equipos]
        nn = sum(e[1] for e in m)
        boots.append(sum(e[0] for e in m) / nn)
    boots.sort()
    lo, hi = boots[int(0.025 * BOOTSTRAP)], boots[int(0.975 * BOOTSTRAP) - 1]
    return {"n": n, "equipos": len(equipos), "residuo": round(media, 4), "ic95": [round(lo, 4), round(hi, 4)],
            "separa": lo > 0 or hi < 0}


def estandarizado(obs: list[dict]) -> dict:
    """Lo esperado de cada caso = la tasa de «no gana» de los casos SIN récord
    del mismo tramo de ventaja y la misma condición (estandarización indirecta)."""
    base = defaultdict(lambda: [0, 0])
    for o in obs:
        if not o["enRecord"]:
            k = (_tramo(o["ventaja"], TRAMOS_VENTAJA), o["local"])
            base[k][0] += 0 if o["gana"] else 1
            base[k][1] += 1
    tasa = {k: s / n for k, (s, n) in base.items() if n}
    con = [o for o in obs if (_tramo(o["ventaja"], TRAMOS_VENTAJA), o["local"]) in tasa]
    return _residuo_por_equipo(con, lambda o: tasa[(_tramo(o["ventaja"], TRAMOS_VENTAJA), o["local"])])


def por_tramo(obs: list[dict]) -> list[dict]:
    out = []
    for _, _, nombre in TRAMOS_VENTAJA:
        for local in (True, False):
            sub = [o for o in obs if _tramo(o["ventaja"], TRAMOS_VENTAJA) == nombre and o["local"] == local]
            out.append({"ventaja": nombre, "condicion": "local" if local else "visita",
                        "conRecord": _grupo([o for o in sub if o["enRecord"]]),
                        "sinRecord": _grupo([o for o in sub if not o["enRecord"] and o["racha"] > 0]),
                        "todos": _grupo(sub)})
    return out


def contra_mercado(obs: list[dict], cuotas: dict) -> dict:
    """`cuotas[fx] = (pL, pE, pV, casas, margen)` sin margen (backtest_burbuja_1x2.cuotas_1x2).
    Residuo contra lo que la casa le daba a ESE equipo, y la plana a la cuota media."""
    con = []
    for o in obs:
        c = cuotas.get(o["fixtureId"])
        if not c:
            continue
        p = c[0] if o["local"] else c[2]
        if not 0 < p < 1:
            continue
        con.append({**o, "pMercado": p, "cuota": 1 / (p * (1 + c[4]))})
    if len(con) < 50:
        return {"partidos": len(con), "nota": "menos de 50 casos con cuota 1X2: no se compara"}
    out = {"partidos": len(con), "residuo": _residuo_por_equipo(con, lambda o: 1 - o["pMercado"]), "porTramo": []}
    for a, b, nombre in TRAMOS_MERCADO:
        fila = {"mercado": nombre}
        for clave, sel in (("conRecord", lambda o: o["enRecord"]), ("sinRecord", lambda o: not o["enRecord"] and o["racha"] > 0)):
            sub = [o for o in con if a <= o["pMercado"] < b and sel(o)]
            n = len(sub)
            fila[clave] = {"n": n,
                           "noGana": round(sum(1 for o in sub if not o["gana"]) / n, 4) if n else None,
                           "casaDecia": round(sum(1 - o["pMercado"] for o in sub) / n, 4) if n else None,
                           "roiPlano": round(sum((o["cuota"] - 1) if o["gana"] else -1 for o in sub) / n, 4) if n else None}
        out["porTramo"].append(fila)
    out["nota"] = ("residuo = no ganó − (1 − probabilidad de ganar de la casa sin margen), en los casos con récord; "
                   "positivo y con el intervalo sobre cero = la casa NO lo cobra. roiPlano = 1 unidad al equipo a la "
                   "cuota media aproximada (la probabilidad sin margen con el margen medio devuelto)")
    return out


def correr(historias: dict[int, dict], nivel_rival=None, cuotas_de=None) -> dict:
    obs = observaciones(historias, nivel_rival)
    if not obs:
        return {"casos": 0, "lectura": "sin casos"}
    fechas = sorted(o["fecha"] for o in obs)
    corte = fechas[len(fechas) // 2]
    muy = [o for o in obs if o["ventaja"] >= 1.0]
    r = {
        "casos": len(obs), "equipos": len({o["team"] for o in obs}), "conRecord": sum(1 for o in obs if o["enRecord"]),
        "desde": fechas[0], "hasta": fechas[-1],
        "estandarizado": estandarizado(obs),
        "muyFavorito": {"conRecord": _grupo([o for o in muy if o["enRecord"]]),
                        "sinRecord": _grupo([o for o in muy if not o["enRecord"] and o["racha"] > 0]),
                        "estandarizado": estandarizado(muy)},
        "porEpoca": [{"epoca": nombre, "estandarizado": estandarizado(sub)}
                     for nombre, sub in ((f"antes de {corte}", [o for o in obs if o["fecha"] < corte]),
                                         (f"desde {corte}", [o for o in obs if o["fecha"] >= corte]))],
        "porTramo": por_tramo(obs),
    }
    if cuotas_de is not None:
        r["contraMercado"] = contra_mercado(obs, cuotas_de([o["fixtureId"] for o in obs]))
    r["lectura"] = lectura(r)
    return r


def lectura(r: dict) -> str:
    e = r["estandarizado"]
    if "residuo" not in e:
        return f"sin muestra para decir nada ({e.get('sinDato')})"
    ep = [x["estandarizado"] for x in r["porEpoca"]]
    replica = all("residuo" in x and x["ic95"][0] > 0 for x in ep)
    txt = (f"con la racha sin perder de la condición en su récord, el equipo no gana {e['residuo']:+.1%} "
           f"más de lo esperado por su fuerza y condición, IC {e['ic95'][0]:+.1%} a {e['ic95'][1]:+.1%} "
           f"(n {e['n']}); " + ("separa y se repite en las dos épocas" if e["separa"] and replica
                                else "separa pero no se repite en las dos épocas" if e["separa"]
                                else "no separa"))
    mk = (r.get("contraMercado") or {}).get("residuo") or {}
    if "residuo" in mk:
        txt += (f". Contra la casa: {mk['residuo']:+.1%}, IC {mk['ic95'][0]:+.1%} a {mk['ic95'][1]:+.1%} (n {mk['n']}): "
                + ("la casa NO lo cobra" if mk["ic95"][0] > 0 else "la casa ya lo cobra o no hay diferencia"))
    return txt


# ── de dónde salen los datos ─────────────────────────────────────────────────

def historias_desde_dir(carpeta: str) -> dict[int, dict]:
    out = {}
    for f in glob.glob(os.path.join(carpeta, "c", "*.json")):
        t = int(os.path.basename(f)[:-5])
        try:
            filas = json.load(open(f))
            niveles = json.load(open(os.path.join(carpeta, "n", f"{t}.json")))
        except (OSError, ValueError):
            continue   # sin /niveles el equipo no tiene nivel previo: sale entero
        if isinstance(filas, list) and isinstance(niveles, list):
            out[t] = {"filas": sorted(filas, key=lambda r: r["fecha"]), "niveles": sorted(niveles, key=lambda r: r["fecha"])}
    return out


def historias_padron() -> dict[int, dict]:
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.app import constantes_de, niveles_de
    from backend.backtest_burbuja import _equipos, padron
    return {t: {"filas": list(reversed(constantes_de(t, 500))), "niveles": list(reversed(niveles_de(t, 500)))}
            for t in _equipos(MIN_PREFIJO + 2, set(padron()))}


def _imprimir(r: dict) -> None:
    if not r.get("casos"):
        print(r.get("lectura"))
        return
    print(f"\n{r['casos']:,} casos · {r['equipos']} equipos · {r['conRecord']:,} con récord · {r['desde']} → {r['hasta']}")
    print(r["lectura"], "\n")

    def g(x):
        return f"n {x['n']:>5}  no gana {x['noGana']:6.1%}  empata {x['empata']:5.1%}" if x["n"] else "n     0"
    m = r["muyFavorito"]
    print("muy favorito (≥ 1,0 de nivel):")
    print(f"  con récord  {g(m['conRecord'])}\n  sin récord  {g(m['sinRecord'])}")
    for x in r["porEpoca"]:
        e = x["estandarizado"]
        print(f"  {x['epoca']:<20} residuo {e.get('residuo', float('nan')):+.1%}  IC {e.get('ic95')}  n {e.get('n')}")
    print("\npor tramo (racha sin perder con récord / sin récord):")
    for t in r["porTramo"]:
        print(f"  {t['ventaja']:<22} {t['condicion']:<7} con récord {g(t['conRecord'])}   sin récord {g(t['sinRecord'])}")
    mk = r.get("contraMercado")
    if mk:
        print("\ncontra la casa:")
        if "porTramo" not in mk:
            print(f"  {mk['nota']} (casos: {mk['partidos']})")
        else:
            for t in mk["porTramo"]:
                for k in ("conRecord", "sinRecord"):
                    x = t[k]
                    if x["n"]:
                        print(f"  casa {t['mercado']:<8} {k:<10} n {x['n']:>5}  no gana {x['noGana']:6.1%}  "
                              f"la casa decía {x['casaDecia']:6.1%}  roi plano {x['roiPlano']:+.1%}")


def main() -> None:
    ap = argparse.ArgumentParser(description="¿El favorito gana menos con su racha sin perder de la condición en récord?")
    ap.add_argument("--padron", action="store_true", help="historias y cuotas de las ligas del padrón (en el servidor)")
    ap.add_argument("--desde-dir", help="carpeta con c/<id>.json (/constantes) y n/<id>.json (/niveles); sin cuotas")
    ap.add_argument("--json", help="guardar el resumen en este archivo")
    a = ap.parse_args()
    if a.desde_dir:
        r = correr(historias_desde_dir(a.desde_dir))
    else:
        from backend.backtest_burbuja import nivel_rival_previo
        from backend.backtest_burbuja_1x2 import cuotas_1x2
        r = correr(historias_padron(), nivel_rival=nivel_rival_previo, cuotas_de=cuotas_1x2)
    _imprimir(r)
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)
        print(f"\nresumen en {a.json}")


if __name__ == "__main__":
    main()
