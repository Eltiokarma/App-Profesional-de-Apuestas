"""Backtest de las burbujas de las OTRAS familias (pedido del usuario, 17/10/2026).

La K de resultado ya tiene su backtest (`backtest_burbuja`, docs/REVENTON.md):
el riesgo de reventón separa (AUC 0.615) pero ni la burbuja ni las K mejoran
el 1X2 del motor (§13.3-13.4). Esto pregunta lo mismo para las burbujas que
la app dibuja y el análisis todavía no lee:

- doble oportunidad: no pierde (1X / X2 según la condición) · no gana
- márgenes: gana por 1+ … 4+ · pierde por 1+ … 4+
- goles: anota · anota 2+ · recibe · recibe 2+ · ambos marcan · más de 2,5

Cada familia es un SÍ/NO por partido. La burbuja abierta es la racha del valor
del último partido (racha si fue sí, SEQUÍA si fue no) dentro del ámbito
(total, solo de local, solo de visita). En cada partido con al menos
MIN_PREFIJO partidos previos del ámbito se reconstruye, SOLO con lo anterior:

  p        frecuencia propia del equipo en el ámbito (Laplace) → P(sigue) base
  largo    partidos de la burbuja abierta
  récord   la burbuja SUPERA su máximo previo del mismo valor · lo IGUALA ·
           ninguna de las dos (solo con ≥ 3 burbujas previas de ese valor)

y se mira el partido siguiente del ámbito: ¿sigue o se corta?

LA PREGUNTA no es «¿cuánto dura?» —eso es descripción— sino «¿el largo y el
récord dicen algo que la frecuencia del equipo no diga?». Por eso se comparan
dos predictores en un corte TEMPORAL (el 80 % más viejo ajusta, el 20 % más
nuevo prueba), los dos calibrados en el tramo de ajuste:

  A  P(sigue) por decil de la frecuencia propia
  B  lo mismo, más el tramo del largo y el estado de récord

Δ = log-loss(B) − log-loss(A) en la prueba, con intervalo por bootstrap de
EQUIPOS (los partidos de un equipo no son independientes). Δ < 0 con el
intervalo entero bajo cero = la burbuja aporta. Si no, es descripción y va al
análisis como dato, sin peso: la misma regla que para la K de resultado.

Sin fuga: todo sale del prefijo. Los amistosos CUENTAN (decisión del usuario,
14/10/2026). No usa el nivel del rival: así no hereda la fuga de §13.1.

    python -m backend.backtest_familias --padron              # en el servidor, con las .db
    python -m backend.backtest_familias --desde-json h.json   # historias bajadas de /constantes
    python -m backend.backtest_familias --desde-json h.json --json salida.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from collections import defaultdict

MIN_PREFIJO = 10        # partidos previos del ámbito para evaluar una burbuja
MIN_RACHAS_RECORD = 3   # burbujas previas del mismo valor para hablar de récord
CORTE_TEMPORAL = 0.8
BOOTSTRAP = 300
AMBITOS = ("total", "local", "visita")

FAMILIAS: dict[str, callable] = {
    "noPierde": lambda gf, gc: gf >= gc,
    "noGana": lambda gf, gc: gf <= gc,
    **{f"gana{n}+": (lambda n: lambda gf, gc: gf - gc >= n)(n) for n in (1, 2, 3, 4)},
    **{f"pierde{n}+": (lambda n: lambda gf, gc: gc - gf >= n)(n) for n in (1, 2, 3, 4)},
    "anota": lambda gf, gc: gf >= 1,
    "anota2+": lambda gf, gc: gf >= 2,
    "recibe": lambda gf, gc: gc >= 1,
    "recibe2+": lambda gf, gc: gc >= 2,
    "ambosMarcan": lambda gf, gc: gf >= 1 and gc >= 1,
    "mas2.5": lambda gf, gc: gf + gc >= 3,
}

TRAMOS_LARGO = ((1, 1), (2, 2), (3, 3), (4, 5), (6, 9), (10, 10 ** 6))


def _tramo(largo: int) -> int:
    for i, (a, b) in enumerate(TRAMOS_LARGO):
        if a <= largo <= b:
            return i
    return len(TRAMOS_LARGO) - 1


def _filas_validas(filas: list[dict]) -> list[dict]:
    out = [f for f in filas if f.get("golesFavor") is not None and f.get("golesContra") is not None]
    return sorted(out, key=lambda f: str(f.get("fecha") or ""))


def observar_equipo(team: int, filas: list[dict]) -> list[tuple]:
    """(familia, ámbito, valor, tramo, récord, p_sigue, sigue, fecha, team) por
    cada partido evaluable. `récord`: 2 supera · 1 iguala · 0 no · -1 sin base."""
    filas = _filas_validas(filas)
    obs = []
    for ambito in AMBITOS:
        sub = filas if ambito == "total" else [
            f for f in filas if f.get("condicion") == ("Local" if ambito == "local" else "Visita")]
        if len(sub) <= MIN_PREFIJO:
            continue
        for fam, pred in FAMILIAS.items():
            serie = [bool(pred(int(f["golesFavor"]), int(f["golesContra"]))) for f in sub]
            si = 0                        # cuántos «sí» en el prefijo
            largo = 0                     # burbuja abierta
            maximos = {True: 0, False: 0}  # máximo previo de cada valor (burbujas YA cortadas)
            cortadas = {True: 0, False: 0}
            for t in range(len(serie)):
                if t >= MIN_PREFIJO:
                    v = serie[t - 1]
                    p_si = (si + 1) / (t + 2)
                    p = p_si if v else 1 - p_si
                    if cortadas[v] < MIN_RACHAS_RECORD:
                        rec = -1
                    else:
                        rec = 2 if largo > maximos[v] else 1 if largo == maximos[v] else 0
                    obs.append((fam, ambito, v, _tramo(largo), rec, p, serie[t] == v,
                                str(sub[t].get("fecha") or ""), team))
                # avanzar con el partido t
                x = serie[t]
                if t > 0 and x != serie[t - 1]:
                    prev = serie[t - 1]
                    maximos[prev] = max(maximos[prev], largo)
                    cortadas[prev] += 1
                    largo = 1
                else:
                    largo += 1
                si += 1 if x else 0
    return obs


def redondear(x: float, decimales: int = 0) -> float:
    """Redondeo hacia arriba en el .5, igual que Math.round del espejo TS
    (src/lib/familias.ts): el round de Python va al par (12,5 → 12) y un
    texto distinto en cada lado tumbaría los vectores dorados."""
    f = 10 ** decimales
    return math.floor(x * f + 0.5) / f


def _logit(p: float) -> float:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def perfil_dc(prefijo: list[dict], local_hoy: bool) -> dict:
    """El perfil de DOBLE OPORTUNIDAD del equipo en la condición en que juega
    HOY, solo con los partidos anteriores (el backtest del 1X2 lo usa sin fuga
    y la narrativa del análisis lo cuenta): con qué frecuencia no pierde y no
    gana de local (o de visita), la burbuja abierta de «no pierde» con signo
    (+ racha sin perder · − racha perdiendo) y si está en su récord.

    El usuario (17/10/2026): «hay equipos que, como no tienen tan buen
    rendimiento, pueden empatar como locales o jugarse un empate como
    visitas». El perfil es eso; la racha es lo que el §15 ya midió."""
    cond = "Local" if local_hoy else "Visita"
    sub = [f for f in _filas_validas(prefijo) if f.get("condicion") == cond]
    n = len(sub)
    np_ = sum(1 for f in sub if int(f["golesFavor"]) >= int(f["golesContra"]))
    ng = sum(1 for f in sub if int(f["golesFavor"]) <= int(f["golesContra"]))
    serie = [int(f["golesFavor"]) >= int(f["golesContra"]) for f in sub]
    largo, maximos, cortadas = 0, {True: 0, False: 0}, {True: 0, False: 0}
    for t, x in enumerate(serie):
        if t > 0 and x != serie[t - 1]:
            maximos[serie[t - 1]] = max(maximos[serie[t - 1]], largo)
            cortadas[serie[t - 1]] += 1
            largo = 1
        else:
            largo += 1
    v = serie[-1] if serie else None
    rec = 0
    if v is not None and cortadas[v] >= MIN_RACHAS_RECORD:
        rec = 2 if largo > maximos[v] else 1 if largo == maximos[v] else 0
    return {
        "condicion": cond, "partidos": n,
        "noPierde": redondear((np_ + 1) / (n + 2), 4), "noGana": redondear((ng + 1) / (n + 2), 4),
        "burbuja": (largo if v else -largo) if v is not None else 0,
        "maximoPrevio": maximos[v] if v is not None else 0,
        "record": rec,                       # 2 supera · 1 iguala · 0 no (o sin base)
    }


def _decil(p: float) -> int:
    return min(9, int(p * 10))


def _ll(p: float, y: bool) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log(p if y else 1 - p)


def _ajustar(train: list[tuple], clave) -> dict:
    c = defaultdict(lambda: [0, 0])
    for o in train:
        k = clave(o)
        c[k][0] += 1 if o[6] else 0
        c[k][1] += 1
    return c


def _predecir(tabla: dict, k, respaldo: float, peso: float = 4.0) -> float:
    """Tasa de la celda suavizada hacia el respaldo (una celda chica no manda)."""
    s, n = tabla.get(k, (0, 0))
    return (s + peso * respaldo) / (n + peso)


def comparar(obs: list[tuple], semilla: int = 42) -> dict:
    """A (decil de frecuencia) contra B (+ tramo del largo + récord), corte temporal."""
    if len(obs) < 200:
        return {"n": len(obs), "sinDato": "menos de 200 observaciones"}
    fechas = sorted(o[7] for o in obs)
    corte = fechas[int(len(fechas) * CORTE_TEMPORAL)]
    train = [o for o in obs if o[7] < corte]
    test = [o for o in obs if o[7] >= corte]
    if len(train) < 100 or len(test) < 100:
        return {"n": len(obs), "sinDato": "corte temporal sin muestra"}
    clave_a = lambda o: (o[2], _decil(o[5]))
    clave_b = lambda o: (o[2], _decil(o[5]), o[3], o[4])
    ta, tb = _ajustar(train, clave_a), _ajustar(train, clave_b)
    base = sum(1 for o in train if o[6]) / len(train)
    por_equipo = defaultdict(lambda: [0.0, 0.0, 0])
    for o in test:
        pa = _predecir(ta, clave_a(o), base)
        pb = _predecir(tb, clave_b(o), pa)
        e = por_equipo[o[8]]
        e[0] += _ll(pa, o[6])
        e[1] += _ll(pb, o[6])
        e[2] += 1
    equipos = list(por_equipo.values())
    n = sum(e[2] for e in equipos)
    delta = (sum(e[1] for e in equipos) - sum(e[0] for e in equipos)) / n
    rnd = random.Random(semilla)
    boots = []
    for _ in range(BOOTSTRAP):
        m = [equipos[rnd.randrange(len(equipos))] for _ in equipos]
        nn = sum(e[2] for e in m)
        boots.append((sum(e[1] for e in m) - sum(e[0] for e in m)) / nn)
    boots.sort()
    lo, hi = boots[int(0.025 * BOOTSTRAP)], boots[int(0.975 * BOOTSTRAP) - 1]
    return {"n": len(obs), "nPrueba": len(test), "corte": corte[:10],
            "logLossA": round(sum(e[0] for e in equipos) / n, 5),
            "deltaLogLoss": round(delta, 5), "ic95": [round(lo, 5), round(hi, 5)],
            "aporta": hi < 0}


def _tasas(sub: list[tuple], clave) -> list[dict]:
    """Observado contra lo que la frecuencia propia esperaba, por celda: el
    residuo es lo que la burbuja dice de más (negativo = se corta más de lo
    esperado, «revienta»; positivo = se sostiene más, «inercia»)."""
    c = defaultdict(lambda: [0, 0.0, 0])
    for o in sub:
        k = clave(o)
        c[k][0] += 1 if o[6] else 0
        c[k][1] += o[5]
        c[k][2] += 1
    out = []
    for k in sorted(c):
        s, esp, n = c[k]
        out.append({"celda": k, "n": n, "sigue": round(s / n, 3), "esperado": round(esp / n, 3),
                    "residuo": round((s - esp) / n, 3)})
    return out


def resumir(obs: list[tuple]) -> dict:
    grupos = defaultdict(list)
    for o in obs:
        grupos[(o[0], o[1])].append(o)
    familias = []
    for (fam, amb), sub in sorted(grupos.items()):
        etiqueta = {True: "racha", False: "sequía"}
        por_largo = {etiqueta[v]: [{**x, "largo": "-".join(map(str, TRAMOS_LARGO[x["celda"]]))
                                   .replace(f"-{10 ** 6}", "+")}
                                  for x in _tasas([o for o in sub if o[2] == v], lambda o: o[3])]
                     for v in (True, False)}
        nombres_rec = {-1: "sin base", 0: "lejos del récord", 1: "iguala el récord", 2: "supera el récord"}
        por_record = {etiqueta[v]: [{**x, "estado": nombres_rec[x["celda"]]}
                                    for x in _tasas([o for o in sub if o[2] == v], lambda o: o[4])]
                      for v in (True, False)}
        familias.append({"familia": fam, "ambito": amb, "comparacion": comparar(sub),
                         "porLargo": por_largo, "porRecord": por_record})
    aportan = [f"{f['familia']}·{f['ambito']}" for f in familias if f["comparacion"].get("aporta")]
    return {
        "observaciones": len(obs),
        "equipos": len({o[8] for o in obs}),
        "aportan": aportan,
        "lectura": ("ninguna familia mejora la predicción del partido siguiente sobre la frecuencia propia "
                    "del equipo: van al análisis como DESCRIPCIÓN, sin peso"
                    if not aportan else
                    f"{len(aportan)} de {len(familias)} combinaciones mejoran la predicción con el intervalo "
                    "entero bajo cero; el resto es descripción"),
        "familias": familias,
    }


def historias_padron(min_filas: int = 12) -> dict[int, list[dict]]:
    """En el servidor: las historias de los equipos de las ligas del padrón."""
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.app import constantes_de
    from backend.backtest_burbuja import _equipos, padron
    return {t: constantes_de(t, 5000) for t in _equipos(min_filas, set(padron()))}


def correr(historias: dict) -> dict:
    obs = []
    for team, filas in historias.items():
        obs += observar_equipo(int(team), filas)
    return resumir(obs)


def _imprimir(r: dict) -> None:
    print(f"\n{r['observaciones']:,} observaciones · {r['equipos']} equipos\n{r['lectura']}\n")
    print(f"{'familia':<12} {'ámbito':<7} {'n':>8} {'Δ log-loss':>11}  IC95                aporta")
    for f in r["familias"]:
        c = f["comparacion"]
        if "deltaLogLoss" not in c:
            print(f"{f['familia']:<12} {f['ambito']:<7} {c['n']:>8}  {c.get('sinDato')}")
            continue
        print(f"{f['familia']:<12} {f['ambito']:<7} {c['n']:>8} {c['deltaLogLoss']:>+11.5f}  "
              f"[{c['ic95'][0]:+.5f}, {c['ic95'][1]:+.5f}]  {'SÍ' if c['aporta'] else '—'}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Backtest de las burbujas de doble oportunidad, márgenes y goles")
    ap.add_argument("--padron", action="store_true", help="historias de las ligas del padrón (en el servidor)")
    ap.add_argument("--desde-json", help="historias {team: {filas: [...]}} bajadas de /constantes")
    ap.add_argument("--json", help="guardar el resumen en este archivo")
    a = ap.parse_args()
    if a.desde_json:
        crudo = json.load(open(a.desde_json))
        historias = {int(t): (v["filas"] if isinstance(v, dict) else v) for t, v in crudo.items()}
    else:
        historias = historias_padron()
    r = correr(historias)
    _imprimir(r)
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)
        print(f"\nresumen en {a.json}")


if __name__ == "__main__":
    main()
