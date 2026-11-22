"""EL 1X2 CIEGO (22/11/2026, usuario: «no tenemos porcentaje propio anotado y
calibrándose. El analista se manda sus páginas de análisis, se mete sus horas
de feedback, para seguir a la casa»).

Medido ese día sobre 393 partes (28/10-22/11): el elegido fue el favorito de
la casa en el 97,5 % y nuestro 1X2 quedó a 1 punto de la casa en promedio.
Las reglas de anclaje del sad-analysis (v4.1-v4.5: «el empate parte del
mercado», «el favorito no se recorta», «no restan bajo el mercado») corrigen el
número HACIA la casa después de leerla, y la lectura propia no quedaba
guardada en ningún lado: no había forma de saber si leemos bien o mal.

El ciego es el 1X2 del analista ANTES de ver la cuota, sellado:

- se deposita con `POST /analisis/cowork/{id}/ciego` antes del parte y antes
  del pitazo; el primero manda y no se reescribe (anti-hindsight);
- con el token de Cowork, las cuotas de un partido por jugarse (`/cuotas/{id}`
  y sus subrutas) responden 409 hasta que el ciego esté sellado, y la
  `ventajaPorFuerza` del TDE (sale de la probabilidad de la casa) viaja tapada;
- se mide contra la casa y contra el 1X2 publicado en los mismos partidos
  (`resumen`), por ACIERTO, que es lo que el usuario prioriza, no por margen.

0 tokens, 0 cuota de API-Football.
"""
from __future__ import annotations

import math
import sqlite3
from datetime import datetime, timezone

from backend import db as saddb
from backend.analisis import db as efedb

CLAVES = ("local", "empate", "visita")
# la suma que se acepta antes de normalizar (el analista escribe enteros)
SUMA_MIN, SUMA_MAX = 95.0, 105.0
# tramos de lo que el ciego le da a su elegido, para la calibración
TRAMOS = ((0, 40, "<40"), (40, 50, "40-49"), (50, 60, "50-59"), (60, 70, "60-69"), (70, 101, "70+"))
# desde cuándo cuenta (00:00 de Lima del 23/11/2026): la medición es hacia adelante
DESDE = "2026-11-23 05:00:00"

DDL = """
CREATE TABLE IF NOT EXISTS parte_ciego (
    fixture_id INTEGER PRIMARY KEY,
    local REAL NOT NULL, empate REAL NOT NULL, visita REAL NOT NULL,
    porque TEXT NOT NULL,
    pitazo TEXT,
    sellado_en TEXT NOT NULL
);
"""

ESPERADO = ('{"local": 48, "empate": 27, "visita": 25, "porque": "lo que leíste en las K, las burbujas, '
            'el EFE, el TDE, el DTP y la prensa, sin la cuota"}')


class CiegoInvalido(ValueError):
    """El ciego no se puede sellar tal cual llegó (y se dice por qué)."""


class CiegoYaSellado(ValueError):
    """Ya hay un ciego para el partido: el primero manda."""

    def __init__(self, existente: dict):
        super().__init__("el 1X2 ciego de este partido ya está sellado y no se reescribe")
        self.existente = existente


def _conectar():
    con = efedb.conectar()
    con.executescript(DDL)
    return con


def _utc(t) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(t).strip().replace("Z", "+00:00").replace(" ", "T"))
    except (TypeError, ValueError):
        return None
    return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)


def _pitazo(fixture_id: int) -> datetime | None:
    f = saddb.query_one("sad", "SELECT date FROM fixtures WHERE id=?", (fixture_id,))
    return _utc(f["date"]) if f else None


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _fila(f) -> dict:
    p = {k: f[k] for k in CLAVES}
    return {"local": p["local"], "empate": p["empate"], "visita": p["visita"],
            "elegido": max(CLAVES, key=lambda k: p[k]), "porque": f["porque"],
            "pitazo": f["pitazo"], "selladoEn": f["sellado_en"]}


def de(fixture_id: int) -> dict | None:
    """El ciego sellado del partido, o None."""
    with _conectar() as con:
        f = con.execute("SELECT * FROM parte_ciego WHERE fixture_id=?", (fixture_id,)).fetchone()
    return _fila(f) if f else None


def de_varios(ids) -> dict:
    """{fixtureId: ciego} de una vez (la simulación lee cientos)."""
    ids = [int(i) for i in ids]
    if not ids:
        return {}
    out = {}
    with _conectar() as con:
        for i in range(0, len(ids), 500):
            tramo = ids[i:i + 500]
            q = "SELECT * FROM parte_ciego WHERE fixture_id IN (%s)" % ",".join("?" * len(tramo))
            for f in con.execute(q, tramo).fetchall():
                out[f["fixture_id"]] = _fila(f)
    return out


def normalizar(body: dict) -> dict:
    """{local, empate, visita, porque} → los tres en % que suman 100, o CiegoInvalido."""
    if not isinstance(body, dict):
        raise CiegoInvalido(f"el ciego tiene que ser un objeto: {ESPERADO}")
    fuente = body.get("probabilidades") if isinstance(body.get("probabilidades"), dict) else body
    try:
        vals = {k: float(fuente[k]) for k in CLAVES}
    except (KeyError, TypeError, ValueError):
        raise CiegoInvalido(f"faltan local, empate y visita como números: {ESPERADO}")
    if any(v < 0 or math.isnan(v) for v in vals.values()):
        raise CiegoInvalido("ninguna probabilidad puede ser negativa")
    tot = sum(vals.values())
    if not SUMA_MIN <= tot <= SUMA_MAX:
        raise CiegoInvalido(f"local + empate + visita suman {tot:g}: tienen que sumar 100 (en %)")
    p = {k: round(100 * v / tot, 1) for k, v in vals.items()}
    orden = sorted(p.values(), reverse=True)
    if orden[0] == orden[1]:
        raise CiegoInvalido("dos resultados empatados arriba: el ciego tiene que elegir uno "
                            "(un punto más al que elegís)")
    porque = str(body.get("porque") or "").strip()
    if len(porque) < 20:
        raise CiegoInvalido("falta `porque`: una o dos frases con lo que leíste (K, burbujas, EFE, "
                            "TDE, DTP, prensa) que sostiene el número, sin la cuota")
    return {**p, "porque": porque}


def sellar(fixture_id: int, body: dict, hay_parte: bool) -> dict:
    """Sella el ciego. Antes del pitazo y antes del parte; el primero manda."""
    previo = de(fixture_id)
    if previo:
        raise CiegoYaSellado(previo)
    pitazo = _pitazo(fixture_id)
    if pitazo is None:
        raise CiegoInvalido(f"el fixture {fixture_id} no está en nuestra base")
    if _ahora() >= pitazo:
        raise CiegoInvalido("el partido ya empezó: el ciego se sella antes del pitazo")
    if hay_parte:
        raise CiegoInvalido("este partido ya tiene parte depositado, y el parte trae la casa a la vista: "
                            "el ciego va ANTES del parte. Este partido queda sin ciego")
    c = normalizar(body)
    ahora = efedb.ahora()
    with _conectar() as con:
        con.execute("INSERT INTO parte_ciego (fixture_id, local, empate, visita, porque, pitazo, sellado_en) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (fixture_id, c["local"], c["empate"], c["visita"], c["porque"],
                     pitazo.strftime("%Y-%m-%d %H:%M:%S"), ahora))
    return {"fixtureId": fixture_id, "ciego": de(fixture_id),
            "siguiente": "ya podés abrir las cuotas (`GET cuotas/{id}`) y seguir con el parte: "
                         "el ciego queda como está, y tu 1X2 publicado va en `pronostico.probabilidades`"}


def _hay_parte(fixture_id: int) -> bool:
    with _conectar() as con:
        try:
            return con.execute("SELECT 1 FROM parte_cowork WHERE fixture_id=?", (fixture_id,)).fetchone() is not None
        except sqlite3.OperationalError:
            return False   # sin la tabla todavía no hay ningún parte


def tapado(fixture_id: int) -> bool:
    """¿La casa de este partido se le tapa a Cowork? Sí mientras el partido no
    empezó, no hay ciego sellado y no hay parte depositado: con el parte ya
    depositado la casa ya se vio (el modo `rehacer` vuelve sobre partes de antes
    del ciego y necesita la cuota). Un fixture que no está en la base no se tapa
    (su endpoint dará 404 o vacío por su cuenta)."""
    pitazo = _pitazo(fixture_id)
    if pitazo is None or _ahora() >= pitazo:
        return False
    return de(fixture_id) is None and not _hay_parte(fixture_id)


def mensaje_tapado(fixture_id: int) -> str:
    return (f"Primero el 1X2 ciego: las cuotas del partido {fixture_id} se abren cuando esté sellado "
            f"(`POST analisis/cowork/{fixture_id}/ciego` con {ESPERADO}). Es tu lectura sin la casa: "
            "se mide contra ella por acierto (docs/METODO_APUESTA.md, «El 1X2 ciego»).")


# ── la medición ─────────────────────────────────────────────────────────────

def _wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - m), 4), round(min(1.0, c + m), 4)]


def _grupo(k: int, n: int) -> dict:
    return {"n": n, "aciertos": k, "tasa": round(k / n, 4) if n else None, "intervalo": _wilson(k, n)}


def _brier(p: dict, real: str) -> float:
    return sum((p[k] / 100 - (1.0 if k == real else 0.0)) ** 2 for k in CLAVES)


def resumen(filas: list[dict]) -> dict:
    """Las filas: {fixtureId, pitazo, ciego {local, empate, visita} | None,
    probabilidades (el publicado, %), mercado (la casa sin margen, %),
    resultado | None}. Mide SOLO las cerradas con ciego, en los mismos partidos
    para los tres: el ciego, el publicado y el favorito de la casa. Por acierto
    del elegido (el usuario, 22/11/2026: «la prioridad es mejorar el acierto»);
    el Brier y la distancia a la casa van como información."""
    desde = _utc(DESDE)
    con = [f for f in filas if f.get("ciego") and f.get("resultado") in CLAVES and f.get("mercado")
           and (_utc(f.get("pitazo")) or desde) >= desde]
    sin = sum(1 for f in filas if f.get("resultado") in CLAVES and not f.get("ciego")
              and (_utc(f.get("pitazo")) or desde) >= desde)
    n = len(con)
    k_ciego = k_pub = k_casa = 0
    b_ciego = b_pub = b_casa = 0.0
    dist = 0.0
    desacuerdo = {"n": 0, "ciego": 0, "casa": 0, "ninguno": 0}
    cambio_pub = {"n": 0, "ciego": 0, "publicado": 0}
    tramos = {t: {"n": 0, "dijo": 0.0, "aciertos": 0} for _, _, t in TRAMOS}
    for f in con:
        r = f["resultado"]
        c = {k: float(f["ciego"][k]) for k in CLAVES}
        m = {k: float(f["mercado"][k]) for k in CLAVES}
        p = {k: float((f.get("probabilidades") or m)[k]) for k in CLAVES}
        tp = sum(p.values()) or 1.0
        p = {k: 100 * v / tp for k, v in p.items()}
        ec, ep, em = (max(CLAVES, key=lambda k: x[k]) for x in (c, p, m))
        k_ciego += ec == r
        k_pub += ep == r
        k_casa += em == r
        b_ciego += _brier(c, r)
        b_pub += _brier(p, r)
        b_casa += _brier(m, r)
        dist += abs(c[ec] - m[ec])
        if ec != em:
            desacuerdo["n"] += 1
            desacuerdo["ciego"] += ec == r
            desacuerdo["casa"] += em == r
            desacuerdo["ninguno"] += r not in (ec, em)
        if ec != ep:
            cambio_pub["n"] += 1
            cambio_pub["ciego"] += ec == r
            cambio_pub["publicado"] += ep == r
        for lo, hi, t in TRAMOS:
            if lo <= c[ec] < hi:
                tramos[t]["n"] += 1
                tramos[t]["dijo"] += c[ec]
                tramos[t]["aciertos"] += ec == r
                break
    calibracion = [{"tramo": t, "n": v["n"], "dijo": round(v["dijo"] / v["n"], 1) if v["n"] else None,
                    "paso": round(100 * v["aciertos"] / v["n"], 1) if v["n"] else None,
                    "intervalo": _wilson(v["aciertos"], v["n"])} for t, v in tramos.items()]
    if not n:
        texto = ("Todavía no hay partidos cerrados con 1X2 ciego: cuenta desde los del 23/11/2026. "
                 "Se juzga por acierto contra la casa en los mismos partidos.")
    else:
        texto = (f"En {n} partidos el ciego acertó {k_ciego} ({100 * k_ciego / n:.1f} %), el publicado "
                 f"{k_pub} ({100 * k_pub / n:.1f} %) y el favorito de la casa {k_casa} "
                 f"({100 * k_casa / n:.1f} %). Donde el ciego no eligió al favorito de la casa "
                 f"({desacuerdo['n']}): ciego {desacuerdo['ciego']}, casa {desacuerdo['casa']}.")
        if n < 60:
            texto += " Con menos de 60 partidos es observación, no conclusión."
    return {
        "desde": DESDE,
        "n": n,
        "sinCiego": sin,
        "ciego": _grupo(k_ciego, n),
        "publicado": _grupo(k_pub, n),
        "casa": _grupo(k_casa, n),
        "brier": ({"ciego": round(b_ciego / n, 4), "publicado": round(b_pub / n, 4), "casa": round(b_casa / n, 4)}
                  if n else None),
        "distanciaCasa": round(dist / n, 1) if n else None,
        "desacuerdo": desacuerdo,
        "publicadoCambio": cambio_pub,
        "calibracion": calibracion,
        "texto": texto,
    }
