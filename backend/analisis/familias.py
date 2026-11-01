"""Las OTRAS burbujas, contadas: doble oportunidad, márgenes y goles.

La K de resultado tiene su reventón calculado (`burbuja.py`, docs/REVENTON.md).
Las demás familias que la app dibuja —doble oportunidad, gana o pierde por 2+
y 3+, anota, recibe, ambos marcan, más de 2,5— no tenían lectura: el análisis
no las veía. Esto las DESCRIBE para la narrativa del parte y de /burbujas
(pedido del usuario, 17/10/2026), con lo que los backtests dejaron dicho:

- §15: ni el largo de la burbuja ni su récord predicen el partido siguiente
  mejor que la frecuencia propia del equipo, y en su récord estas burbujas se
  SOSTIENEN algo más de lo esperado (no revientan). Por eso aquí no hay
  riesgo ni puntos: la burbuja es descripción.
- Pero una burbuja GRANDE en su récord es terreno sin precedente, y se lee
  como CUIDADO (`cuidado`, alerta FAMILIA-RECORD del parte; usuario,
  17/10/2026, tras el Everton 0-2 Chelsea con su doble oportunidad de local
  enorme): prudencia con la carga, igual que K-EXTREMO, no probabilidad. Y
  como el récord no se corta más que lo normal, un corte tiene una causa que
  el veredicto tiene que poder rastrear (`objetivo.otrasFamilias`).
- §15.1: el PERFIL de doble oportunidad por condición (con qué frecuencia no
  pierde y no gana de local, o de visita) SÍ agrega al 1X2 del motor. Va
  aparte, como dato que pesa.

Todo sale de la historia que se le pasa (cronológica y, en la vista «al día
del partido», ya cortada antes del fixture): 0 requests, 0 tokens, sin modelo.
"""
from __future__ import annotations

from backend.backtest_familias import FAMILIAS, MIN_RACHAS_RECORD, _filas_validas, perfil_dc, redondear

# qué se cuenta y cómo se dice: (clave, cuando es SÍ, cuando es NO)
NARRADAS = (
    # «perdiendo»/«ganando» se leían como ir abajo/arriba en el marcador, o al
    # revés de la racha (incidencia 578): el NO de estas dos es el resultado
    ("noPierde", "sin perder", "con derrota"),
    ("noGana", "sin ganar", "con victoria"),
    ("gana2+", "ganando por 2 o más", "sin ganar por 2 o más"),
    ("gana3+", "ganando por 3 o más", "sin ganar por 3 o más"),
    ("pierde2+", "perdiendo por 2 o más", "sin perder por 2 o más"),
    ("anota", "anotando", "sin anotar"),
    ("recibe", "recibiendo gol", "con la valla invicta"),
    ("ambosMarcan", "con goles de los dos", "sin que marquen los dos"),
    ("mas2.5", "con más de 2,5 goles", "con 2 goles o menos"),
)
DESTACADA_DESDE = 3      # una burbuja de 3+ partidos (o en su récord) va a las líneas
CUIDADO_DESDE = 5        # en su récord y de 5+ partidos: cuidado con la carga
# ...y RARA para ese equipo (usuario, 24/10/2026, incidencias 420 y 450): «58 de
# local sin ganar por 3+» es récord, pero a quien gana por 3+ una vez cada 40 una
# racha así le sale sola. `probRacha` = frecuencia propia del estado de hoy
# elevada al largo (la chance de encadenar tantos seguidos); cuidado solo < 5 %.
IMPROBABLE_BAJO = 0.05
# ...y nunca con un estado que el equipo vive el 90 %+ de las veces (01/11/2026,
# incidencia 834, decisión del usuario: Grêmio «70 de local sin ganar por 3+», un
# estado del 93 %; elevado a 70 da < 5 %, pero la racha larga es lo normal del equipo)
FRECUENCIA_BANAL = 0.9
_AMBITO = {"local": "de local", "visita": "de visita", "total": "en total"}


def _burbuja(filas: list[dict], clave: str) -> dict | None:
    pred = FAMILIAS[clave]
    serie = [bool(pred(int(f["golesFavor"]), int(f["golesContra"]))) for f in filas]
    if not serie:
        return None
    largo, maximos, cortadas = 0, {True: 0, False: 0}, {True: 0, False: 0}
    for t, x in enumerate(serie):
        if t > 0 and x != serie[t - 1]:
            maximos[serie[t - 1]] = max(maximos[serie[t - 1]], largo)
            cortadas[serie[t - 1]] += 1
            largo = 1
        else:
            largo += 1
    v = serie[-1]
    rec = None
    if cortadas[v] >= MIN_RACHAS_RECORD:
        rec = "supera" if largo > maximos[v] else "iguala" if largo == maximos[v] else "no"
    frec = redondear(sum(serie) / len(serie), 3)
    prob = redondear((frec if v else 1 - frec) ** largo, 4)
    return {"valor": v, "partidos": largo, "maximoPrevio": maximos[v] if cortadas[v] else None,
            "burbujasPrevias": cortadas[v], "record": rec,
            "frecuencia": frec, "n": len(serie), "probRacha": prob, "improbable": prob < IMPROBABLE_BAJO}


def es_cuidado(b: dict) -> bool:
    estado = b["frecuencia"] if b["valor"] else 1 - b["frecuencia"]
    return (b["record"] in ("supera", "iguala") and b["partidos"] >= CUIDADO_DESDE and b["improbable"]
            and estado < FRECUENCIA_BANAL)


def _pct(p: float) -> str:
    x = redondear(p * 100)
    return f"{int(x)} %" if x >= 1 else "menos del 1 %"


def _texto(nombre: str, ambito: str, b: dict, si: str, no: str) -> str:
    estado = si if b["valor"] else no
    t = f"{nombre} lleva {b['partidos']} {'partido' if b['partidos'] == 1 else 'partidos'} {_AMBITO[ambito]} {estado}"
    if b["maximoPrevio"] is not None:
        t += f" (su máximo previo era {b['maximoPrevio']})"
    if b["record"] in ("supera", "iguala"):
        t += (": está en terreno nuevo, por encima de su récord" if b["record"] == "supera"
              else ": iguala su récord")
        if es_cuidado(b):
            t += " — CUIDADO con cargar a que siga: no hay precedente. El backtest no dice que se corte más " \
                 "(§15), así que si se corta hay una causa que buscar"
        elif b["partidos"] >= CUIDADO_DESDE:
            t += f" — pero con su frecuencia una racha así es esperable (sale el {_pct(b['probRacha'])} de las " \
                 "veces): no es terreno raro"
    # la frecuencia del ESTADO en que está hoy, para que la línea no se contradiga
    frec = b["frecuencia"] if b["valor"] else 1 - b["frecuencia"]
    t += f". En {b['n']} partidos {_AMBITO[ambito]} va {estado} el {int(redondear(frec * 100))} %."
    return t


def describir(filas: list[dict], condicion: str | None, nombre: str = "El equipo") -> dict:
    """`filas` en orden cronológico (o el que sea: se ordenan); `condicion` =
    "L"/"V" del próximo partido (None = sin próximo: solo el total)."""
    filas = _filas_validas(filas)
    ambitos = ["total"]
    cond = {"L": "local", "V": "visita"}.get(condicion or "")
    if cond:
        ambitos.insert(0, cond)
    out = {
        "nota": ("descripción, no riesgo: el largo y el récord de estas burbujas no predicen el partido "
                 "siguiente mejor que la frecuencia del equipo, y en su récord se sostienen algo más, no "
                 "revientan (REVENTON §15). El PERFIL de doble oportunidad por condición sí agrega al 1X2 "
                 "del motor (§15.1)"),
        "condicion": cond, "familias": [], "lineas": [],
    }
    if cond:
        p = perfil_dc(filas, condicion == "L")
        if p["partidos"]:
            # el texto cuenta lo observado; noPierde/noGana van suavizados para el modelo (§15.1)
            sub = [f for f in filas if f.get("condicion") == p["condicion"]]
            n_np = sum(1 for f in sub if f["golesFavor"] >= f["golesContra"])
            n_ng = sum(1 for f in sub if f["golesFavor"] <= f["golesContra"])
            n = p["partidos"]
            out["perfilDc"] = {**p, "texto": (
                f"Perfil de doble oportunidad {_AMBITO[cond]}: no pierde {n_np} de {n} "
                f"({int(redondear(n_np / n * 100))} %) y no gana {n_ng} de {n} "
                f"({int(redondear(n_ng / n * 100))} %). Este perfil SÍ agrega al 1X2 del motor (REVENTON §15.1): un equipo que "
                f"{_AMBITO[cond]} empata mucho o se planta a no perder no está del todo en el nivel")}
            out["lineas"].append(out["perfilDc"]["texto"])
    for ambito in ambitos:
        sub = filas if ambito == "total" else [
            f for f in filas if f.get("condicion") == ("Local" if ambito == "local" else "Visita")]
        for clave, si, no in NARRADAS:
            b = _burbuja(sub, clave)
            if not b:
                continue
            texto = _texto(nombre, ambito, b, si, no)
            destacada = b["partidos"] >= DESTACADA_DESDE or b["record"] in ("supera", "iguala")
            out["familias"].append({"familia": clave, "ambito": ambito, **b, "destacada": destacada,
                                    "cuidado": es_cuidado(b), "texto": texto})
            if destacada:
                out["lineas"].append(texto)
    return out
