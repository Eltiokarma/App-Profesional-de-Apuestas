"""EL SEMÁFORO DEL ELEGIDO, POR LAS ESPINAS (13/11/2026; antes, 11/11/2026).

El usuario no lee la prosa del parte: mira la etiqueta del elegido, y este
color le dice si meter plata a ese lado o no. NO mira la cuota: «no
encontramos value a la cuota; el semáforo es el veredicto que dice: por más
que la casa diga esto, estas otras cosas hacen que mejor no apostemos».
Desde el 13/11/2026 el color sale de las ESPINAS que el analista escribió en
el parte (`lecturaSad.espina.{a,b}.lectura`, su lectura de las K de cada
equipo), CALCULADO aquí:

- 🟢 `confirma`: la espina del elegido lo acompaña (positiva = su K sigue
  ganando) y la del rival dice que el rival no sigue (negativa o neutra).
- 🟡 `duda`: la espina del elegido es cero (empate), o la del rival dice que
  el rival sigue (positiva) o empata (cero). `motivos` dice cuál.
- 🔴 `noApostar`: la espina del propio elegido es NEGATIVA: el analista leyó
  que su elegido pierde y lo eligió igual (Italia 3-1 Francia, 12/11/2026).
- ⚪ `sinDato`: sin el 1X2 o sin la espina del elegido (falta o es neutra).
- El elegido EMPATE: verde si las dos espinas dicen cero; si no, amarillo.

Medido el 13/11/2026 sobre 721 partes acreditables (14/09-12/11, sin copas
nacionales): con la espina del elegido positiva el elegido ganó 59 % (n 601),
con cero 44 % (34) y con negativa 26 % (19); la regla del amarillo («espina
del elegido negativa o cero, o la del rival positiva o cero») dio verde 59 %
contra amarillo 43 % (n 75), +16 pts al elegirla (hasta el 01/11) y +17 al
comprobarla (02/11-12/11). Se encontró en esos datos: cuenta hacia adelante
desde `DESDE` con un criterio fijo (`simulacion.resumen_semaforo`,
`docs/METODO_APUESTA.md`). La regla del 11/11 (≤ 2 pts de la casa y el
marcador con el elegido) quedó atrás: medía cercanía a la cuota, no
desconfianza, y pintaba verde casi todo.

`distancia` (nuestro 1X2 contra la casa) y `marcadorSigno` viajan como
información: NO deciden el color.

REGLA ANTI-GOODHART: el semáforo NO se le muestra a Cowork ni al analista
—ni en el recibo, ni en el prompt, ni en un endpoint que lea su token—. Lee
su espina; si viera el color, aprendería a escribirla a favor de su elegido.
Viaja en `/analisis/simulacion` y en `/analisis/semaforo`, que el token de
Cowork no abre (`backend/app.py`, `_COWORK_PERMITIDO`).
"""
from __future__ import annotations

import re

CLAVES = ("local", "empate", "visita")
# el criterio de las espinas cuenta desde los partidos del 13/11/2026, 00:00
# de Lima (UTC−5): la regla se eligió con los partidos hasta el 12/11
DESDE = "2026-11-13 05:00:00"
REGLA = "espinas"

ESTADOS = ("confirma", "duda", "noApostar", "sinDato")
LECTURAS = ("positiva", "cero", "negativa")
# qué lado es el elegido y cuál el rival, por equipo del parte (a = local)
_LADO = {"local": ("a", "b"), "visita": ("b", "a")}


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


def _lectura(espinas, lado: str) -> str | None:
    """positiva · cero · negativa de la espina de un lado; None si falta o es
    neutra (la neutra no se juzga)."""
    e = (espinas or {}).get(lado)
    lec = e.get("lectura") if isinstance(e, dict) else e
    lec = str(lec or "").strip().lower()
    return lec if lec in LECTURAS else None


def semaforo(probs, espinas, mercado=None, marcador=None) -> dict:
    """`probs` = `pronostico.probabilidades` del parte (en % o en fracción, se
    normaliza); `espinas` = `lecturaSad.espina` ({a, b}, cada una con su
    `lectura`, o la lectura sola); `mercado` (el 1X2 de la casa SIN margen, en
    %) y `marcador` solo viajan como información."""
    p = _pct(probs)
    m = _pct(mercado) if mercado else None
    elegido = max(CLAVES, key=lambda k: p[k]) if p else None
    distancia = round(max(abs(p[k] - m[k]) for k in CLAVES), 1) if p and m else None
    lec_a, lec_b = _lectura(espinas, "a"), _lectura(espinas, "b")
    if elegido in _LADO:
        lado_e, lado_r = _LADO[elegido]
        esp_e, esp_r = (lec_a, lec_b) if lado_e == "a" else (lec_b, lec_a)
    else:
        esp_e = esp_r = None
    base = {"elegido": elegido, "regla": REGLA, "espinaElegido": esp_e, "espinaRival": esp_r,
            "espinas": {"a": lec_a, "b": lec_b},
            "distancia": distancia, "marcadorSigno": signo_marcador(marcador)}
    motivos = []
    if not p:
        motivos.append({"codigo": "SIN-1X2", "detalle": "el parte no trae el 1X2 completo"})
        return {"estado": "sinDato", "motivos": motivos, **base}
    if elegido == "empate":
        if lec_a is None or lec_b is None:
            motivos.append({"codigo": "SIN-ESPINA",
                            "detalle": "el elegido es el empate y falta la espina de un equipo (o es neutra)"})
            return {"estado": "sinDato", "motivos": motivos, **base}
        fuera = [x for x, lec in (("local", lec_a), ("visita", lec_b)) if lec != "cero"]
        if fuera:
            motivos.append({"codigo": "ESPINA-NO-EMPATA",
                            "detalle": "el elegido es el empate y la espina de " + " y ".join(
                                f"{x} dice {lec_a if x == 'local' else lec_b}" for x in fuera)})
        return {"estado": "duda" if motivos else "confirma", "motivos": motivos, **base}
    if esp_e is None:
        motivos.append({"codigo": "SIN-ESPINA",
                        "detalle": f"falta la espina del elegido ({elegido}) o es neutra: no se juzga"})
        return {"estado": "sinDato", "motivos": motivos, **base}
    if esp_e == "negativa":
        motivos.append({"codigo": "ESPINA-CONTRA-EL-ELEGIDO",
                        "detalle": f"la espina del elegido ({elegido}) dice que pierde: se lo eligió contra su propia lectura"})
    elif esp_e == "cero":
        motivos.append({"codigo": "ESPINA-ELEGIDO-EMPATA",
                        "detalle": f"la espina del elegido ({elegido}) dice empate, no que gane"})
    if esp_r in ("positiva", "cero"):
        motivos.append({"codigo": "ESPINA-RIVAL-SIGUE",
                        "detalle": f"la espina del rival dice {esp_r}: "
                                   + ("que gana" if esp_r == "positiva" else "que no pierde")})
    estado = "noApostar" if esp_e == "negativa" else "duda" if motivos else "confirma"
    return {"estado": estado, "motivos": motivos, **base}


def del_parte(parte: dict, mercado=None) -> dict:
    """El semáforo de un parte ya leído; el mercado sin margen en % (solo
    para `distancia`, que no decide)."""
    pron = (parte or {}).get("pronostico") or {}
    espinas = ((parte or {}).get("lecturaSad") or {}).get("espina") or {}
    return semaforo(pron.get("probabilidades") or {}, espinas, mercado, pron.get("marcador"))


def de_partidos(ids) -> dict[int, dict]:
    """{fixtureId: semáforo} de los partidos con parte, para la web. La cuota
    (solo para `distancia`) es la misma de la simulación
    (`lecciones.cuotas_mercado`: la última captura prepartido, media de las
    casas, sin margen)."""
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
