"""GOLES ACOTADOS (30/10/2026, pedido del usuario; docs/REVENTON.md §17).

Las constantes de goles no adivinan el 1X2: ACOTAN los goles. El backtest
(`backend/backtest_goles.py`, 50.821 partidos del padrón) midió que el cruce
de lo que mete el local DE LOCAL con lo que recibe el visitante DE VISITA
(y al revés), más la μ del motor y las constantes de goles, da un intervalo
de dos goles que acierta lo que promete (64 % contra 65 %) y un marcador
acotado de cuatro marcadores que acierta 41 %. Contra el mercado de goles
(más/menos 2,5, ambos marcan) NO hay ventaja: esto es LECTURA del marcador,
no una señal de apuesta.

Todo sale de la historia ESTRICTAMENTE anterior al partido y de las MISMAS
variables que el backtest (`variables_de` y `vector_ataque` las usan los dos):
lo que se muestra es lo que se midió. El modelo calibrado vive acá
(`MODELO_GOLES`), como los puntos del reventón: se rehace con
`python -m backend.backtest_goles --padron --modelo` y se pega.
"""
from __future__ import annotations

import math

N_SERIE = 10            # partidos de la serie en la condición (el «1, 2, 2, 2, 1…»)
PREVIA = 3.0            # cuántos partidos «imaginarios» con la media de la condición
MEDIA_LOCAL, MEDIA_VISITA = 1.45, 1.15   # goles por partido de referencia
MAX_GOLES = 10
VARIABLES = ["lnAtaque", "lnDefensa", "local", "d",
             "kGaCondAt", "kGrCondDef", "kGaAt", "kGrDef", "rachaMarcaAt", "rachaRecibeDef"]

# El modelo G3 (cruce + K) ajustado con TODO el padrón (`backtest_goles --padron
# --modelo`, 30/10/2026: 50.823 partidos; en la prueba del corte temporal el
# intervalo de dos goles acertó 64,3 % y el marcador acotado 41,1 %). Con None
# no se acota nada (se dice, no se inventa). Rehacerlo con el mismo comando.
MODELO_GOLES: dict | None = {
    "vars": ["lnAtaque", "lnDefensa", "local", "d", "kGaCondAt", "kGrCondDef", "kGaAt", "kGrDef",
             "rachaMarcaAt", "rachaRecibeDef"],
    "intercepto": 0.239914,
    "media": {"lnAtaque": 0.25493, "lnDefensa": 0.194148, "local": 0.5, "d": 0.0, "kGaCondAt": 1.858406,
              "kGrCondDef": 1.819846, "kGaAt": 1.833707, "kGrDef": 1.819239, "rachaMarcaAt": 1.024254,
              "rachaRecibeDef": 0.961377},
    "desvio": {"lnAtaque": 0.31961, "lnDefensa": 0.305696, "local": 0.5, "d": 0.741049, "kGaCondAt": 1.393559,
               "kGrCondDef": 1.396259, "kGaAt": 1.371474, "kGrDef": 1.385278, "rachaMarcaAt": 0.801768,
               "rachaRecibeDef": 0.775419},
    "beta": {"lnAtaque": 0.100109, "lnDefensa": 0.069641, "local": -0.013141, "d": 0.153472, "kGaCondAt": 0.091563,
             "kGrCondDef": -0.00722, "kGaAt": 0.022105, "kGrDef": 0.010056, "rachaMarcaAt": -0.094557,
             "rachaRecibeDef": 0.00496},
    "calibradoEn": "2026-10-30", "partidos": 50823, "intervaloAcierta": 0.6427, "marcadorAcotadoAcierta": 0.4113,
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


def variables_de(previas: list[dict], condicion: str) -> dict | None:
    """Lo que se sabía de los goles de un equipo ANTES del partido, con las
    filas de `/constantes` anteriores (cronológicas) y la condición de hoy
    («Local» / «Visita»). None con menos de 3 partidos en esa condición."""
    if not previas:
        return None
    jugadas = [f for f in previas if f.get("golesFavor") is not None and f.get("golesContra") is not None]
    en_cond = [f for f in jugadas if f["condicion"] == condicion][-N_SERIE:]
    if len(en_cond) < 3:
        return None
    marca = [int(f["golesFavor"]) for f in en_cond]
    recibe = [int(f["golesContra"]) for f in en_cond]
    k = previas[-1]["fusion"]          # la K antes del partido: la de la fila anterior
    c = "Local" if condicion == "Local" else "Visita"
    local = condicion == "Local"
    return {
        "serieMarca": marca, "serieRecibe": recibe,
        "mediaMarca": _media(marca, MEDIA_LOCAL if local else MEDIA_VISITA),
        "mediaRecibe": _media(recibe, MEDIA_VISITA if local else MEDIA_LOCAL),
        "kGaCond": _slog(k.get(f"goles{c}Anotado")), "kGrCond": _slog(k.get(f"goles{c}Recibido")),
        "kGa": _slog(k.get("golesAnotado")), "kGr": _slog(k.get("golesRecibido")),
        "rachaMarca": math.log1p(_racha(marca)), "rachaRecibe": math.log1p(_racha(recibe)),
    }


def vector_ataque(at: dict, de: dict, local: bool, d: float) -> dict:
    """Las variables del equipo que ATACA contra la defensa del otro."""
    return {"lnAtaque": math.log(at["mediaMarca"]), "lnDefensa": math.log(de["mediaRecibe"]),
            "local": 1.0 if local else 0.0, "d": d,
            "kGaCondAt": at["kGaCond"], "kGrCondDef": de["kGrCond"],
            "kGaAt": at["kGa"], "kGrDef": de["kGr"],
            "rachaMarcaAt": at["rachaMarca"], "rachaRecibeDef": de["rachaRecibe"]}


def lambda_de(x: dict, modelo: dict | None = None) -> float | None:
    m = modelo or MODELO_GOLES
    if not m:
        return None
    z = m["intercepto"] + sum(m["beta"][v] * (x[v] - m["media"][v]) / m["desvio"][v] for v in m["vars"])
    return math.exp(max(-20.0, min(5.0, z)))


def poisson(lam: float) -> list[float]:
    """P(0..MAX_GOLES) con la cola en el último."""
    ps = [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(MAX_GOLES)]
    return ps + [max(0.0, 1.0 - sum(ps))]


def mejor_banda(ps: list[float], ancho: int = 2) -> int:
    """El primer gol de la ventana de `ancho` goles más probable."""
    return max(range(0, 6), key=lambda k: (sum(ps[k:k + ancho]), -k))


def _intervalo(ps: list[float], ancho: int) -> dict:
    k = mejor_banda(ps, ancho)
    return {"desde": k, "hasta": k + ancho - 1, "prob": round(sum(ps[k:k + ancho]), 3)}


def lado(lam: float, equipo: str) -> dict:
    ps = poisson(lam)
    return {"equipo": equipo, "esperados": round(lam, 2),
            "distribucion": {"0": round(ps[0], 3), "1": round(ps[1], 3), "2": round(ps[2], 3),
                             "3+": round(sum(ps[3:]), 3)},
            "intervalo": _intervalo(ps, 2),            # «mete 1 o 2»
            "intervaloAmplio": _intervalo(ps, 3)}      # más confianza, más ancho


def acotar_lambdas(lam_l: float, lam_v: float, local: str, visita: str, modelo: dict | None = None) -> dict:
    """El marcador acotado con los goles esperados de cada lado."""
    m = modelo or MODELO_GOLES or {}
    pl, pv = poisson(lam_l), poisson(lam_v)
    L, V = lado(lam_l, local), lado(lam_v, visita)
    il, iv = L["intervalo"], V["intervalo"]
    marcadores = [f"{a}-{b}" for a in range(il["desde"], il["hasta"] + 1) for b in range(iv["desde"], iv["hasta"] + 1)]
    celdas = sorted(((pl[a] * pv[b], f"{a}-{b}") for a in range(6) for b in range(6)), reverse=True)
    total = poisson(lam_l + lam_v)
    return {
        "local": L, "visita": V,
        "marcadorAcotado": {"marcadores": marcadores, "prob": round(il["prob"] * iv["prob"], 3)},
        "masProbables": [{"marcador": s, "prob": round(p, 3)} for p, s in celdas[:5]],
        "masDe2_5": round(1 - sum(total[:3]), 3),
        "ambosMarcan": round((1 - pl[0]) * (1 - pv[0]), 3),
        "modelo": {k: m.get(k) for k in ("calibradoEn", "partidos", "intervaloAcierta", "marcadorAcotadoAcierta")},
        "nota": ("lectura del marcador, calculada (0 tokens): el intervalo de dos goles de cada equipo y los "
                 "cuatro marcadores que salen de cruzarlos, con su probabilidad. Medido sobre el padrón: el "
                 "intervalo acierta lo que promete y el cruce local × visita es lo que más pesa; contra el "
                 "mercado de goles no hay ventaja (REVENTON §17): no es una señal de apuesta"),
    }


def acotar_fixture(fx) -> dict:
    """Los goles acotados de un fixture (`fx` con id, date, home/away), con la
    historia estrictamente anterior al partido. Sin modelo calibrado o sin
    historia suficiente lo dice en `sinDato`."""
    if not MODELO_GOLES:
        return {"sinDato": "el modelo de goles todavía no está calibrado (backtest_goles --modelo)"}
    from backend.app import constantes_de, iso, mu, niveles_de
    antes = iso(fx["date"])
    vs = {}
    for clave, tid, cond in (("L", fx["home_team_id"], "Local"), ("V", fx["away_team_id"], "Visita")):
        previas = list(reversed(constantes_de(tid, 500, antes=antes)))
        v = variables_de(previas, cond)
        nv = niveles_de(tid, 1, antes=antes)
        if v is None or not nv:
            return {"sinDato": f"{fx['home_name'] if clave == 'L' else fx['away_name']} tiene menos de 3 partidos "
                               f"de {'local' if clave == 'L' else 'visita'} o sin nivel antes del partido"}
        vs[clave] = (v, nv[0]["nivel"])
    (vl, nl), (vv, nvv) = vs["L"], vs["V"]
    d = mu(nl, nvv, 1.0) - mu(nvv, nl, 0.0)
    lam_l = lambda_de(vector_ataque(vl, vv, True, d))
    lam_v = lambda_de(vector_ataque(vv, vl, False, -d))
    return acotar_lambdas(lam_l, lam_v, fx["home_name"], fx["away_name"])


def desde_equipo(acotado: dict, es_local: bool) -> dict:
    """La misma lectura dicha desde un equipo (la tarjeta de burbujas):
    cuánto mete y cuánto recibe contra su próximo rival."""
    if acotado.get("sinDato"):
        return acotado
    propio, rival = (acotado["local"], acotado["visita"]) if es_local else (acotado["visita"], acotado["local"])
    return {"mete": propio, "recibe": {**rival, "equipo": rival["equipo"]},
            "marcadorAcotado": acotado["marcadorAcotado"], "masProbables": acotado["masProbables"],
            "masDe2_5": acotado["masDe2_5"], "ambosMarcan": acotado["ambosMarcan"],
            "modelo": acotado["modelo"], "nota": acotado["nota"]}


def objetivo(acotado: dict, gl: int, gv: int) -> dict | None:
    """Para el veredicto: si los goles reales cayeron en lo acotado."""
    if not acotado or acotado.get("sinDato"):
        return None
    il, iv = acotado["local"]["intervalo"], acotado["visita"]["intervalo"]
    ok_l = il["desde"] <= gl <= il["hasta"]
    ok_v = iv["desde"] <= gv <= iv["hasta"]
    return {"intervaloLocal": ok_l, "intervaloVisita": ok_v, "marcadorAcotado": ok_l and ok_v,
            "probPrometida": acotado["marcadorAcotado"]["prob"], "real": f"{gl}-{gv}"}
