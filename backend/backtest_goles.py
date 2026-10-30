"""¿Las constantes de goles ACOTAN los goles? (docs/REVENTON.md §17, 30/10/2026)

Pedido del usuario: «las constantes de goles no predicen el resultado, acotan
los goles. Goles anotados, goles en contra. Esto va con un marcador. Puede
definir al ganador, pero no necesariamente acierta. Era una herramienta que
acotaba. Y teníamos dos, local y visita: era brutal». Su método: mirar los
goles de cada equipo (Alianza mete 1, 2, 2, 2, 1, 2, 2, 1, 2, 3, 4, 1…) y
quedarse con un INTERVALO («1 o 2»), y cruzarlo con lo que recibe el rival.

Lo que ya se midió NO es esta pregunta: §13.4 probó las K de goles contra el
1X2 (no agregan) y §15 la burbuja de goles contra la frecuencia propia del
partido siguiente. Acá se mide si acotan LOS GOLES de cada equipo:

  G1 · frecuencia — el método del usuario: lo que el equipo mete en su
                    condición de hoy en sus últimos N partidos (sin ajuste).
  G2 · cruce      — Poisson con lo que mete el local DE LOCAL, lo que recibe
                    el visitante DE VISITA (y al revés) y la μ del motor.
  G3 · + K        — G2 más las constantes de goles (anotado del que ataca,
                    recibido del que defiende; de la condición y totales) y
                    la racha abierta de marcar / de recibir en la condición.

Ajuste con el 80 % de partidos más VIEJOS, prueba en el 20 % más nuevo, todo
sacado de la historia ANTERIOR al partido. Se mide:

- log-loss de los goles de cada equipo (0 · 1 · 2 · 3+), por partido, con
  bootstrap emparejado de G3 − G2 y G2 − G1;
- ACOTAR: cuánto acierta el intervalo de dos goles más probable («1 o 2») y el
  marcador acotado (los 4 marcadores de los dos intervalos), contra lo que
  prometía cada modelo; y el intervalo «a mano» del usuario (la ventana de dos
  goles más repetida en su serie);
- el MERCADO en los mismos partidos: más/menos 2,5 goles y ambos marcan.

Y aparte, **¿el marcador se repite?** (el usuario: «el marcador no se repite
tanto; cierto equipo que empata mucho empata con marcador diferente»): por
equipo, cuántas veces un partido repite el marcador del anterior (y un empate,
el del empate anterior) contra lo que daría el azar con LOS MISMOS marcadores
del equipo en otro orden (permutaciones).

    python -m backend.backtest_goles --padron           # las ligas importantes
    python -m backend.backtest_goles --liga 281         # una liga
    python -m backend.backtest_goles --muestra 300      # prueba rápida

Solo lee. Guarda el resumen en $SAD_DATA_DIR/.backtest_goles.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from datetime import datetime, timezone

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend import db  # noqa: E402
from backend.app import constantes_de, mu, niveles_de  # noqa: E402
from backend.backtest_burbuja import (MIN_PREFIJO, _equipos, _nivel_a_fecha, _nombres_ligas,  # noqa: E402
                                      _resolver, padron)

GUARDADO = ".backtest_goles.json"
N_SERIE = 10            # partidos de la serie en la condición (el «1, 2, 2, 2, 1…»)
PREVIA = 3.0            # cuántos partidos «imaginarios» con la media de la condición
MEDIA_LOCAL, MEDIA_VISITA = 1.45, 1.15   # goles por partido de referencia (sin mirar la prueba)
PRUEBA = 0.2
RIDGE = 1e-2
NEWTON_ITER = 25
BOOTSTRAP = 500
PERMUTACIONES = 200
MAX_GOLES = 10
CLASES = ("0", "1", "2", "3+")

MODELOS = {
    "G2 cruce": ["lnAtaque", "lnDefensa", "local", "d"],
    "G3 cruce + K": ["lnAtaque", "lnDefensa", "local", "d",
                     "kGaCondAt", "kGrCondDef", "kGaAt", "kGrDef", "rachaMarcaAt", "rachaRecibeDef"],
}


def _slog(x) -> float:
    x = float(x or 0.0)
    return math.copysign(math.log1p(abs(x)), x)


def _media(serie: list[int], previa: float) -> float:
    """Lo que mete (o recibe) en la condición, encogido hacia la referencia:
    con 3 partidos no se sabe lo mismo que con 10."""
    return (sum(serie) + PREVIA * previa) / (len(serie) + PREVIA)


def _racha(serie: list[int]) -> int:
    """Partidos seguidos, contando desde el último, con al menos un gol."""
    n = 0
    for g in reversed(serie):
        if g < 1:
            break
        n += 1
    return n


def banda_usuario(serie: list[int]) -> int | None:
    """El intervalo «a mano»: la ventana de dos goles (k, k+1) que más se
    repite en la serie; empate → la más baja. None sin serie."""
    if not serie:
        return None
    cuenta = {k: sum(1 for g in serie if k <= min(g, 9) <= k + 1) for k in range(0, 5)}
    return max(cuenta, key=lambda k: (cuenta[k], -k))


# ── observaciones ────────────────────────────────────────────────────────────

def lado_equipo(team_id: int, ligas: set[int] | None) -> dict[int, dict]:
    """Por fixture: lo que se sabía de los goles de ESTE equipo antes del partido."""
    filas = list(reversed(constantes_de(team_id, 500)))
    niveles = list(reversed(niveles_de(team_id, 500)))
    out = {}
    for i in range(MIN_PREFIJO, len(filas)):
        fila = filas[i]
        if fila["golesFavor"] is None or fila["golesContra"] is None:
            continue
        if ligas and fila["ligaId"] not in ligas:
            continue
        nv = _nivel_a_fecha(niveles, fila["fecha"])
        if nv is None:
            continue
        cond = fila["condicion"]
        previas = [f for f in filas[:i] if f["golesFavor"] is not None and f["golesContra"] is not None]
        en_cond = [f for f in previas if f["condicion"] == cond][-N_SERIE:]
        if len(en_cond) < 3:
            continue
        marca = [int(f["golesFavor"]) for f in en_cond]
        recibe = [int(f["golesContra"]) for f in en_cond]
        k = filas[i - 1]["fusion"]          # la fila de ESTE partido ya trae su resultado
        c = "Local" if cond == "Local" else "Visita"
        out[fila["fixtureId"]] = {
            "local": cond == "Local", "nivel": nv, "fecha": fila["fecha"], "liga": fila["ligaId"],
            "gf": int(fila["golesFavor"]), "ga": int(fila["golesContra"]),
            "serieMarca": marca, "serieRecibe": recibe,
            "mediaMarca": _media(marca, MEDIA_LOCAL if cond == "Local" else MEDIA_VISITA),
            "mediaRecibe": _media(recibe, MEDIA_VISITA if cond == "Local" else MEDIA_LOCAL),
            "kGaCond": _slog(k[f"goles{c}Anotado"]), "kGrCond": _slog(k[f"goles{c}Recibido"]),
            "kGa": _slog(k["golesAnotado"]), "kGr": _slog(k["golesRecibido"]),
            "rachaMarca": math.log1p(_racha(marca)), "rachaRecibe": math.log1p(_racha(recibe)),
        }
    return out


def _ataque(at: dict, de: dict, d: float) -> dict:
    """Una observación por equipo que ATACA: sus goles contra la defensa del otro."""
    return {"y": at["gf"], "serie": at["serieMarca"], "mediaFrecuencia": at["mediaMarca"],
            "x": {"lnAtaque": math.log(at["mediaMarca"]), "lnDefensa": math.log(de["mediaRecibe"]),
                  "local": 1.0 if at["local"] else 0.0, "d": d,
                  "kGaCondAt": at["kGaCond"], "kGrCondDef": de["kGrCond"],
                  "kGaAt": at["kGa"], "kGrDef": de["kGr"],
                  "rachaMarcaAt": at["rachaMarca"], "rachaRecibeDef": de["rachaRecibe"]}}


def observaciones(equipos: list[int], ligas: set[int] | None) -> list[dict]:
    por_fx: dict[int, list[dict]] = {}
    for t in equipos:
        for fx, o in lado_equipo(t, ligas).items():
            por_fx.setdefault(fx, []).append(o)
    obs = []
    for fx, lados in por_fx.items():
        loc = [o for o in lados if o["local"]]
        vis = [o for o in lados if not o["local"]]
        if len(loc) != 1 or len(vis) != 1:
            continue
        L, V = loc[0], vis[0]
        if L["gf"] != V["ga"] or L["ga"] != V["gf"]:
            continue   # los dos lados no cuentan el mismo marcador: fuera
        d = mu(L["nivel"], V["nivel"], 1.0) - mu(V["nivel"], L["nivel"], 0.0)
        obs.append({"fixtureId": fx, "fecha": L["fecha"], "liga": L["liga"],
                    "local": _ataque(L, V, d), "visita": _ataque(V, L, -d)})
    obs.sort(key=lambda o: o["fecha"])
    return obs


# ── Poisson (Newton, sin numpy) ──────────────────────────────────────────────

def ajustar(X: list[list[float]], Y: list[int]) -> list[float]:
    p = len(X[0])
    beta = [0.0] * p
    beta[0] = math.log(max(sum(Y) / len(Y), 1e-3))
    for _ in range(NEWTON_ITER):
        g = [0.0] * p
        H = [[0.0] * p for _ in range(p)]
        for x, y in zip(X, Y):
            lam = math.exp(max(-20.0, min(5.0, sum(b * xi for b, xi in zip(beta, x)))))
            r = y - lam
            for i in range(p):
                g[i] += r * x[i]
                for j in range(p):
                    H[i][j] += lam * x[i] * x[j]
        for i in range(1, p):
            g[i] -= RIDGE * beta[i]
            H[i][i] += RIDGE
        paso = _resolver(H, g)
        beta = [b + s for b, s in zip(beta, paso)]
        if max(abs(s) for s in paso) < 1e-8:
            break
    return beta


def _escala(filas: list[dict], vars_: list[str]) -> dict:
    out = {}
    for v in vars_:
        xs = [f["x"][v] for f in filas]
        m = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs)) or 1.0
        out[v] = (m, sd)
    return out


def _fila(f: dict, vars_: list[str], esc: dict) -> list[float]:
    return [1.0] + [(f["x"][v] - esc[v][0]) / esc[v][1] for v in vars_]


def poisson(lam: float) -> list[float]:
    """P(0..MAX_GOLES) con la cola en el último."""
    ps = [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(MAX_GOLES)]
    return ps + [max(0.0, 1.0 - sum(ps))]


def _clase(y: int) -> int:
    return min(y, 3)


def _ll(ps: list[float], y: int) -> float:
    p = ps[y] if y < 3 else sum(ps[3:])
    return -math.log(max(p, 1e-12))


def mejor_banda(ps: list[float]) -> int:
    """La ventana (k, k+1) más probable."""
    return max(range(0, 5), key=lambda k: (ps[k] + ps[k + 1], -k))


def _ic_dif(a: list[float], b: list[float], semilla: int = 7) -> dict:
    n = len(a)
    if not n:
        return {"media": None, "ic95": None}
    dif = [y - x for x, y in zip(a, b)]
    rnd = random.Random(semilla)
    medias = sorted(sum(dif[rnd.randrange(n)] for _ in range(n)) / n for _ in range(BOOTSTRAP))
    return {"media": round(sum(dif) / n, 5),
            "ic95": [round(medias[int(0.025 * BOOTSTRAP)], 5), round(medias[int(0.975 * BOOTSTRAP) - 1], 5)]}


def _wilson(k: int, n: int) -> list[float] | None:
    if not n:
        return None
    z, p = 1.96, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(c - m, 3), round(c + m, 3)]


def correr(obs: list[dict], mercado_de=None) -> dict:
    corte = int(len(obs) * (1 - PRUEBA))
    train, test = obs[:corte], obs[corte:]
    if len(train) < 50 or len(test) < 20:
        return {"error": f"muy pocos partidos ({len(obs)}) para separar entrenamiento y prueba"}
    ataques_tr = [o[lado] for o in train for lado in ("local", "visita")]
    lam: dict[str, list[tuple[float, float]]] = {}
    coefs = {}
    for nombre, vars_ in MODELOS.items():
        esc = _escala(ataques_tr, vars_)
        beta = ajustar([_fila(a, vars_, esc) for a in ataques_tr], [a["y"] for a in ataques_tr])
        coefs[nombre] = {v: round(b, 4) for v, b in zip(vars_, beta[1:])}
        lam[nombre] = [tuple(math.exp(max(-20.0, min(5.0, sum(b * xi for b, xi in zip(beta, _fila(o[l], vars_, esc))))))
                             for l in ("local", "visita")) for o in test]
    # G1: la frecuencia del equipo en su condición, sin ajuste
    lam["G1 frecuencia"] = [(o["local"]["mediaFrecuencia"], o["visita"]["mediaFrecuencia"]) for o in test]
    nombres = ["G1 frecuencia", "G2 cruce", "G3 cruce + K"]

    perd, res = {}, {}
    for n in nombres:
        ll_partido, banda_ok, banda_p, marc_ok, marc_p, exacto_ok = [], 0, 0.0, 0, 0.0, 0
        for o, (ll_, lv_) in zip(test, lam[n]):
            pl, pv = poisson(ll_), poisson(lv_)
            yl, yv = o["local"]["y"], o["visita"]["y"]
            ll_partido.append(_ll(pl, yl) + _ll(pv, yv))
            bl, bv = mejor_banda(pl), mejor_banda(pv)
            okl, okv = bl <= yl <= bl + 1, bv <= yv <= bv + 1
            banda_ok += okl + okv
            banda_p += (pl[bl] + pl[bl + 1]) + (pv[bv] + pv[bv + 1])
            marc_ok += okl and okv
            marc_p += (pl[bl] + pl[bl + 1]) * (pv[bv] + pv[bv + 1])
            el = max(range(MAX_GOLES), key=lambda k: pl[k])
            ev = max(range(MAX_GOLES), key=lambda k: pv[k])
            exacto_ok += (el == yl and ev == yv)
        m = len(test)
        perd[n] = ll_partido
        res[n] = {"logLoss": round(sum(ll_partido) / m, 5),
                  "intervalo": {"acierta": round(banda_ok / (2 * m), 4), "prometia": round(banda_p / (2 * m), 4),
                                "ic95": _wilson(banda_ok, 2 * m)},
                  "marcadorAcotado": {"acierta": round(marc_ok / m, 4), "prometia": round(marc_p / m, 4),
                                      "ic95": _wilson(marc_ok, m)},
                  "marcadorExacto": round(exacto_ok / m, 4)}
    # el intervalo «a mano» del usuario: la ventana más repetida de la serie
    ok, n_ = 0, 0
    for o in test:
        for l in ("local", "visita"):
            b = banda_usuario(o[l]["serie"])
            if b is not None:
                n_ += 1
                ok += b <= o[l]["y"] <= b + 1
    res["G0 intervalo a mano"] = {"intervalo": {"acierta": round(ok / n_, 4) if n_ else None, "ic95": _wilson(ok, n_)}}
    comparaciones = {"G2 cruce vs G1 frecuencia": _ic_dif(perd["G1 frecuencia"], perd["G2 cruce"]),
                     "G3 cruce + K vs G2 cruce": _ic_dif(perd["G2 cruce"], perd["G3 cruce + K"])}
    goles = [o[l]["y"] for o in test for l in ("local", "visita")]
    media = sum(goles) / len(goles)
    if not 0.8 <= media <= 2.2:
        raise SystemExit(f"GOLES ROTOS: {media:.2f} por equipo y partido en la prueba (fuera de 0,8-2,2)")
    out = {"partidos": len(obs), "entrenamiento": len(train), "prueba": len(test),
           "desde": train[0]["fecha"][:10], "corte": test[0]["fecha"][:10], "hasta": test[-1]["fecha"][:10],
           "golesPorEquipo": round(media, 3), "modelos": res, "comparaciones": comparaciones,
           "coeficientes": coefs, "lectura": lectura(res, comparaciones)}
    if mercado_de is not None:
        out["mercado"] = contra_mercado(test, lam, mercado_de([o["fixtureId"] for o in test]))
    return out


# ── el mercado de goles en los mismos partidos ───────────────────────────────

def cuotas_goles(fixture_ids: list[int]) -> dict:
    """{fx: {"ou": P(más de 2,5), "btts": P(ambos marcan), "cuotas": {...}}} sin
    margen, promedio entre casas; sin cuotas sintéticas."""
    from backend.cuota_mercados import cuota_key
    por_fx: dict[int, dict] = {}
    ids = list(dict.fromkeys(fixture_ids))
    for i in range(0, len(ids), 500):
        lote = ids[i:i + 500]
        try:
            filas = db.query(
                "sad", f"SELECT fixture_id, bookmaker_id, bookmaker_name, bet_name, value, odd FROM odds "
                       f"WHERE fixture_id IN ({','.join('?' * len(lote))}) AND odd > 1 "
                       f"AND (bookmaker_name IS NULL OR bookmaker_name <> 'SYNTHETIC')", tuple(lote))
        except Exception:  # noqa: BLE001
            return {}
        for f in filas:
            k = cuota_key(f["bet_name"], f["value"])
            if not k or k[0] not in ("ou", "btts"):
                continue
            casa = f["bookmaker_id"] if f["bookmaker_id"] is not None else f["bookmaker_name"]
            por_fx.setdefault(f["fixture_id"], {}).setdefault(k[0], {}).setdefault(casa, {})[k[1]] = float(f["odd"])
    out = {}
    for fx, mercados in por_fx.items():
        r = {}
        for m, (si, no) in (("ou", ("O", "U")), ("btts", ("Y", "N"))):
            casas = [c for c in (mercados.get(m) or {}).values() if si in c and no in c]
            if casas:
                ps = [(1 / c[si]) / (1 / c[si] + 1 / c[no]) for c in casas]
                r[m] = sum(ps) / len(ps)
                r[m + "Cuotas"] = (sum(c[si] for c in casas) / len(casas), sum(c[no] for c in casas) / len(casas))
        if r:
            out[fx] = r
    return out


def _bin_ll(p: float, y: bool) -> float:
    return -math.log(max(p if y else 1 - p, 1e-12))


def _modelo_mercados(ll_: float, lv_: float) -> tuple[float, float]:
    """P(más de 2,5) y P(ambos marcan) con los dos Poisson independientes."""
    total = poisson(ll_ + lv_)
    return 1 - sum(total[:3]), (1 - math.exp(-ll_)) * (1 - math.exp(-lv_))


def contra_mercado(test: list[dict], lam: dict, cuotas: dict) -> dict:
    out = {}
    for m, idx_p in (("ou", 0), ("btts", 1)):
        idx = [i for i, o in enumerate(test) if m in cuotas.get(o["fixtureId"], {})]
        if len(idx) < 30:
            out[m] = {"partidos": len(idx), "nota": "menos de 30 partidos de la prueba con esta cuota: no se compara"}
            continue
        ll_merc = []
        por_modelo = {}
        for n in ("G2 cruce", "G3 cruce + K"):
            lls, ganancia = [], []
            for i in idx:
                o = test[i]
                yl, yv = o["local"]["y"], o["visita"]["y"]
                y = (yl + yv >= 3) if m == "ou" else (yl >= 1 and yv >= 1)
                p = _modelo_mercados(*lam[n][i])[idx_p]
                lls.append(_bin_ll(p, y))
                pm = cuotas[o["fixtureId"]][m]
                c_si, c_no = cuotas[o["fixtureId"]][m + "Cuotas"]
                # apuesta de 1 unidad donde el modelo ve 5+ puntos de ventaja sobre el mercado
                if p - pm >= 0.05:
                    ganancia.append(c_si - 1 if y else -1.0)
                elif pm - p >= 0.05:
                    ganancia.append(c_no - 1 if not y else -1.0)
            por_modelo[n] = {"logLoss": round(sum(lls) / len(lls), 5), "_ll": lls, "apuestas": ganancia}
        for i in idx:
            o = test[i]
            yl, yv = o["local"]["y"], o["visita"]["y"]
            y = (yl + yv >= 3) if m == "ou" else (yl >= 1 and yv >= 1)
            ll_merc.append(_bin_ll(cuotas[o["fixtureId"]][m], y))
        r = {"partidos": len(idx), "mercado": {"logLoss": round(sum(ll_merc) / len(ll_merc), 5)}}
        for n, v in por_modelo.items():
            g = v["apuestas"]
            r[n] = {"logLoss": v["logLoss"], "modeloMenosMercado": _ic_dif(ll_merc, v["_ll"]),
                    "valor": {"apuestas": len(g), "roi": round(sum(g) / len(g), 4) if g else None,
                              "ic95": _ic_dif([0.0] * len(g), g)["ic95"] if len(g) >= 20 else None}}
        out[m] = r
    out["nota"] = ("más/menos 2,5 goles y ambos marcan, en los MISMOS partidos de la prueba con cuota; mercado sin "
                   "margen, promedio entre casas. modeloMenosMercado negativo = el modelo acota mejor que el mercado. "
                   "`valor`: 1 unidad donde el modelo ve 5+ puntos sobre el mercado, a la cuota media (con margen)")
    return out


# ── ¿el marcador se repite? ──────────────────────────────────────────────────

def _repeticiones(seq: list[tuple[int, int]]) -> int:
    return sum(1 for a, b in zip(seq, seq[1:]) if a == b)


def repeticion_marcadores(series: dict[int, list[tuple[int, int, bool]]], semilla: int = 11) -> dict:
    """`series`: por equipo, sus partidos en orden ((gf, ga, local)). Cuenta
    cuántas veces un partido repite el marcador del anterior (desde el equipo)
    y cuántas un empate repite el del empate anterior, contra el promedio de
    PERMUTACIONES del orden de los mismos marcadores del equipo."""
    rnd = random.Random(semilla)
    obs_todos = obs_emp = 0
    esp_todos = [0] * PERMUTACIONES
    esp_emp = [0] * PERMUTACIONES
    pares_todos = pares_emp = 0
    for seq in series.values():
        s = [(gf, ga) for gf, ga, _ in seq]
        e = [(gf, ga) for gf, ga in s if gf == ga]
        obs_todos += _repeticiones(s)
        obs_emp += _repeticiones(e)
        pares_todos += max(0, len(s) - 1)
        pares_emp += max(0, len(e) - 1)
        for k in range(PERMUTACIONES):
            s2, e2 = s[:], e[:]
            rnd.shuffle(s2)
            rnd.shuffle(e2)
            esp_todos[k] += _repeticiones(s2)
            esp_emp[k] += _repeticiones(e2)

    def resumen(obs: int, esp: list[int], pares: int) -> dict:
        esp_s = sorted(esp)
        m = sum(esp) / len(esp)
        menor = sum(1 for x in esp if x <= obs) / len(esp)
        return {"pares": pares, "observado": obs, "esperadoAlAzar": round(m, 1),
                "rangoAlAzar95": [esp_s[int(0.025 * len(esp))], esp_s[int(0.975 * len(esp)) - 1]],
                "razon": round(obs / m, 3) if m else None,
                # fracción de permutaciones con tantas o menos repeticiones que lo observado
                "pMenos": round(menor, 3)}
    return {"todos": resumen(obs_todos, esp_todos, pares_todos),
            "empates": resumen(obs_emp, esp_emp, pares_emp),
            "nota": "razón < 1 con pMenos ≤ 0,025: el marcador se repite MENOS que con los mismos marcadores en "
                    "cualquier orden; ≈ 1: lo que da el azar"}


def series_de(equipos: list[int], ligas: set[int] | None) -> dict[int, list[tuple[int, int, bool]]]:
    out = {}
    for t in equipos:
        filas = list(reversed(constantes_de(t, 500)))
        s = [(int(f["golesFavor"]), int(f["golesContra"]), f["condicion"] == "Local") for f in filas
             if f["golesFavor"] is not None and f["golesContra"] is not None
             and (not ligas or f["ligaId"] in ligas)]
        if len(s) >= 10:
            out[t] = s
    return out


def lectura(res: dict, comp: dict) -> str:
    def v(clave):
        ic = comp[clave]["ic95"]
        if not ic:
            return "sin datos"
        return "acota MEJOR" if ic[1] < 0 else "acota PEOR" if ic[0] > 0 else "no se distingue"
    g3 = res["G3 cruce + K"]
    txt = [f"el cruce local × visita sobre la frecuencia sola: {v('G2 cruce vs G1 frecuencia')}",
           f"las constantes de goles sobre el cruce: {v('G3 cruce + K vs G2 cruce')}",
           f"el intervalo de dos goles de G3 acierta {g3['intervalo']['acierta']:.0%} (prometía "
           f"{g3['intervalo']['prometia']:.0%}) y el marcador acotado {g3['marcadorAcotado']['acierta']:.0%}"]
    txt.append("→ las constantes AGREGAN a acotar los goles: candidatas a la lectura del marcador"
               if v("G3 cruce + K vs G2 cruce") == "acota MEJOR"
               else "→ las constantes no acotan más que la frecuencia cruzada de local y visita")
    return " · ".join(txt)


def correr_backtest(*, padron_: bool = False, liga: int | None = None, muestra: int = 0,
                    min_filas: int = 12, semilla: int = 42) -> dict:
    ligas, nombres = None, {}
    if padron_:
        nombres = padron()
        ligas = set(nombres)
    if liga:
        ligas = {liga}
        nombres = _nombres_ligas(ligas)
    equipos = _equipos(min_filas, ligas)
    if muestra and muestra < len(equipos):
        random.seed(semilla)
        equipos = random.sample(equipos, muestra)
    r = correr(observaciones(equipos, ligas), mercado_de=cuotas_goles)
    r["repeticion"] = repeticion_marcadores(series_de(equipos, ligas))
    r["equipos"] = len(equipos)
    r["ligasEvaluadas"] = sorted(nombres.values()) if ligas else ["todas"]
    return r


def guardar(r: dict) -> str:
    ruta = os.path.join(db.BASE_DIR, GUARDADO)
    limpio = json.loads(json.dumps(r, default=str))
    for m in ("ou", "btts"):
        for n in ("G2 cruce", "G3 cruce + K"):
            ((limpio.get("mercado") or {}).get(m) or {}).get(n, {}).pop("_ll", None)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({**limpio, "corridoEn": datetime.now(timezone.utc).isoformat(timespec="seconds")}, f, ensure_ascii=False)
    return ruta


def imprimir(r: dict):
    if r.get("error"):
        print(r["error"])
    else:
        print(f"partidos: {r['partidos']} ({r['equipos']} equipos) · entrenamiento {r['desde']} → {r['corte']} "
              f"({r['entrenamiento']}) · prueba {r['corte']} → {r['hasta']} ({r['prueba']}) · "
              f"{r['golesPorEquipo']} goles por equipo y partido\n")
        print(f"{'modelo':<22}{'log-loss':>10}{'intervalo 2 goles':>22}{'marcador acotado':>22}{'exacto':>8}")
        for n, m in r["modelos"].items():
            it = m["intervalo"]
            ll = f"{m['logLoss']:.4f}" if "logLoss" in m else "—"
            prom = f" (prometía {it['prometia']:.0%})" if "prometia" in it else ""
            ma = m.get("marcadorAcotado")
            mtxt = f"{ma['acierta']:.0%} (prometía {ma['prometia']:.0%})" if ma else "—"
            ex = f"{m['marcadorExacto']:.1%}" if "marcadorExacto" in m else "—"
            itxt = (f"{it['acierta']:.0%}" if it["acierta"] is not None else "—") + prom
            print(f"{n:<22}{ll:>10}{itxt:>22}{mtxt:>22}{ex:>8}")
        print("\ndiferencia de log-loss por partido (negativa = acota mejor), IC 95 % bootstrap:")
        for k, v in r["comparaciones"].items():
            print(f"  {k:<30} {v['media']:+.5f}  {v['ic95']}")
        print("\ncoeficientes de G3 (por desvío; positivo = más goles):")
        for v, b in r["coeficientes"]["G3 cruce + K"].items():
            print(f"  {v:<16} {b:+.3f}")
        mk = r.get("mercado") or {}
        for m, titulo in (("ou", "más/menos 2,5 goles"), ("btts", "ambos marcan")):
            x = mk.get(m)
            if not x:
                continue
            print(f"\n— el mercado: {titulo} —")
            if "mercado" not in x:
                print(f"  {x['nota']} (partidos: {x['partidos']})")
                continue
            print(f"  {x['partidos']} partidos · log-loss mercado {x['mercado']['logLoss']:.4f}")
            for n in ("G2 cruce", "G3 cruce + K"):
                y = x[n]
                d = y["modeloMenosMercado"]
                vl = y["valor"]
                roi = f"{vl['roi']:+.1%}" if vl["roi"] is not None else "—"
                print(f"  {n:<14} log-loss {y['logLoss']:.4f} · modelo − mercado {d['media']:+.5f} {d['ic95']} · "
                      f"valor: {vl['apuestas']} apuestas, roi {roi} {vl['ic95'] or ''}")
        print(f"\n{r['lectura']}")
    rep = r.get("repeticion")
    if rep:
        print("\n— ¿el marcador se repite? (contra los mismos marcadores en cualquier orden) —")
        for k, titulo in (("todos", "un partido repite el marcador del anterior"),
                          ("empates", "un empate repite el marcador del empate anterior")):
            x = rep[k]
            print(f"  {titulo}: {x['observado']} de {x['pares']} · al azar {x['esperadoAlAzar']} "
                  f"{x['rangoAlAzar95']} · razón {x['razon']} · pMenos {x['pMenos']}")


def main():
    ap = argparse.ArgumentParser(description="¿Las constantes de goles acotan los goles?")
    ap.add_argument("--padron", action="store_true", help="solo las ligas importantes")
    ap.add_argument("--liga", type=int, help="solo partidos de esta league_id")
    ap.add_argument("--muestra", type=int, default=0, help="equipos al azar (0 = todos)")
    ap.add_argument("--min-filas", type=int, default=12)
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--json", help="guardar también en este archivo")
    a = ap.parse_args()
    r = correr_backtest(padron_=a.padron, liga=a.liga, muestra=a.muestra, min_filas=a.min_filas, semilla=a.semilla)
    imprimir(r)
    if not r.get("error"):
        print(f"\nguardado en {guardar(r)}")
    if a.json:
        limpio = json.loads(json.dumps(r, default=str))
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(limpio, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
