"""EL SEMÁFORO DEL ELEGIDO (11/11/2026, usuario: «me apoyaré de ese semáforo»).

El usuario no lee la prosa del parte: mira la etiqueta del elegido. Esto le
pone un color, CALCULADO —el parte no declara nada de esto—:

- 🟢 `confirma`: nuestro 1X2 queda a ≤ `UMBRAL_CASA` puntos de la casa (sin
  margen) en LOS TRES resultados, y el marcador declarado va con el elegido
  (mismo signo: gana el local, empate o gana la visita).
- 🟡 `duda`: falla una de las dos (o las dos); `motivos` dice cuál.
- ⚪ `sinDato`: sin cuotas del 1X2, sin el 1X2 del parte o sin un marcador
  legible.

Medido el 11/11/2026 sobre 374 partes (15/09-01/11): a ≤ 2 pts de la casa el
elegido ganó 66,7 % contra 53,7 % que daba la cuota (n 177), y cuando se
aparta más rinde por debajo de su cuota (−2,5 a −5); con el marcador en
contra del elegido (83 de 374) acierta 39,8 %, y apostando solo cuando lo
acompaña, 60,1 % contra 55,6 % (291 de 374). Medido sobre lo mismo donde se
encontró: por eso cuenta hacia adelante desde `DESDE` con un criterio fijo
(`simulacion.resumen_semaforo`, `docs/METODO_APUESTA.md`).

REGLA ANTI-GOODHART: el semáforo NO se le muestra a Cowork ni al analista
—ni en el recibo, ni en el prompt, ni en un endpoint que lea su token—. Si lo
viera, aprendería a «pintarse de verde» pegándose a la casa y la señal
moriría. Viaja en `/analisis/simulacion` y en `/analisis/semaforo`, que el
token de Cowork no abre (`backend/app.py`, `_COWORK_PERMITIDO`).
"""
from __future__ import annotations

import re

CLAVES = ("local", "empate", "visita")
# a cuántos puntos de probabilidad de la casa (sin margen), en cada resultado
UMBRAL_CASA = 2.0
# el criterio cuenta desde los partidos del 11/11/2026, 00:00 de Lima (UTC−5)
DESDE = "2026-11-11 05:00:00"

ESTADOS = ("confirma", "duda", "sinDato")


def _pct(probs) -> dict | None:
    """El 1X2 normalizado a 100, o None si no está completo."""
    try:
        vals = {k: float(probs[k]) for k in CLAVES}
    except (KeyError, TypeError, ValueError):
        return None
    tot = sum(vals.values())
    if tot <= 0 or any(v < 0 for v in vals.values()):
        return None
    return {k: 100 * v / tot for k, v in vals.items()}


def signo_marcador(marcador) -> str | None:
    """local · empate · visita del marcador declarado («2-1», «1-1 (o 2-2)»:
    manda el primero, como en el veredicto). None si no hay un N-N."""
    m = re.search(r"(\d+)\s*[-–:]\s*(\d+)", str(marcador or ""))
    if not m:
        return None
    gl, gv = int(m.group(1)), int(m.group(2))
    return "local" if gl > gv else "visita" if gv > gl else "empate"


def semaforo(probs, mercado, marcador) -> dict:
    """`probs` = `pronostico.probabilidades` del parte (en % o en fracción,
    se normaliza); `mercado` = el 1X2 de la casa SIN margen, en % (o None);
    `marcador` = `pronostico.marcador`."""
    p = _pct(probs)
    m = _pct(mercado) if mercado else None
    signo = signo_marcador(marcador)
    elegido = max(CLAVES, key=lambda k: p[k]) if p else None
    motivos = []
    if not p:
        motivos.append({"codigo": "SIN-1X2", "detalle": "el parte no trae el 1X2 completo"})
    if not m:
        motivos.append({"codigo": "SIN-CUOTAS", "detalle": "sin las tres cuotas del 1X2 capturadas"})
    if signo is None:
        motivos.append({"codigo": "SIN-MARCADOR", "detalle": "el parte no trae un marcador legible"})
    distancia = round(max(abs(p[k] - m[k]) for k in CLAVES), 1) if p and m else None
    base = {"elegido": elegido, "distancia": distancia, "marcadorSigno": signo, "umbral": UMBRAL_CASA}
    if motivos:
        return {"estado": "sinDato", "motivos": motivos, **base}
    k_lejos = max(CLAVES, key=lambda k: abs(p[k] - m[k]))
    if max(abs(p[k] - m[k]) for k in CLAVES) > UMBRAL_CASA:
        motivos.append({"codigo": "LEJOS-DE-LA-CASA",
                        "detalle": f"en {k_lejos} le damos {p[k_lejos]:.1f} % y la casa {m[k_lejos]:.1f} % "
                                   f"({p[k_lejos] - m[k_lejos]:+.1f} pts; el verde pide ≤ {UMBRAL_CASA:g} en los tres)"})
    if signo != elegido:
        motivos.append({"codigo": "MARCADOR-CONTRADICE",
                        "detalle": f"el marcador {marcador} dice {signo} y el elegido es {elegido}"})
    return {"estado": "duda" if motivos else "confirma", "motivos": motivos, **base}


def del_parte(parte: dict, mercado) -> dict:
    """El semáforo de un parte ya leído, con el mercado sin margen en %."""
    pron = (parte or {}).get("pronostico") or {}
    return semaforo(pron.get("probabilidades") or {}, mercado, pron.get("marcador"))


def de_partidos(ids) -> dict[int, dict]:
    """{fixtureId: semáforo} de los partidos con parte, para la web. La cuota
    es la misma de la simulación (`lecciones.cuotas_mercado`: la última
    captura prepartido, media de las casas, sin margen)."""
    import json

    from backend.analisis.lecciones import cuotas_mercado
    from backend.analisis.parte import _conectar
    ids = sorted({int(i) for i in ids})[:300]
    if not ids:
        return {}
    with _conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, parte_json FROM parte_cowork "
            f"WHERE fixture_id IN ({','.join('?' * len(ids))})", tuple(ids)).fetchall()
    mercados = cuotas_mercado([f["fixture_id"] for f in filas])
    out = {}
    for f in filas:
        try:
            parte = json.loads(f["parte_json"])
        except (TypeError, ValueError):
            continue
        out[f["fixture_id"]] = del_parte(parte, (mercados.get(f["fixture_id"]) or {}).get("prob"))
    return out
