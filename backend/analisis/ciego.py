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
# desde cuándo cuenta (00:00 de Lima del 22/11/2026): el primer sello es de ese
# domingo a las 09:57 de Lima, antes de ver la cuota; con el 23/11 la tabla
# arrancaba vacía y los 31 primeros ciegos no se veían (usuario, 24/11/2026)
DESDE = "2026-11-22 05:00:00"

DDL = """
CREATE TABLE IF NOT EXISTS parte_ciego (
    fixture_id INTEGER PRIMARY KEY,
    local REAL NOT NULL, empate REAL NOT NULL, visita REAL NOT NULL,
    porque TEXT NOT NULL,
    pitazo TEXT,
    sellado_en TEXT NOT NULL
);
"""

# LAS DOS LECTURAS (24/11/2026, usuario: «o gana el local o no gana; y el que
# no gane involucra empate y derrota… cuando se cruzan con el otro, los dos
# tienen un evento en común»): el analista lee a cada equipo por su lado
# —¿gana o no gana?— y el empate sale de la intersección de los dos «no gana»:
# P(no gana local ∩ no gana visita) = P(empate) = 100 − ganaLocal − ganaVisita.
# Si las dos lecturas suman más de 100 se cruzan (los dos no pueden ganar): se
# CALZAN («podemos refactorizarlo y hacer que calce») con el empate del MOTOR
# —sale del nivel, no de la cuota— y local y visita se reparten el resto en la
# proporción que dijo el analista. Lo escrito queda guardado tal cual: es lo
# que se calibra, cada lectura contra si ese equipo ganó.
ESPERADO = ('{"ganaLocal": 48, "ganaVisita": 25, "porque": "lo que leíste de cada equipo en las K, '
            'las burbujas, el EFE, el TDE, el DTP y la prensa, sin la cuota"}')
# tramos de cada lectura binaria (¿gana este equipo?), para su calibración
TRAMOS_GANA = ((0, 20, "0-19"), (20, 40, "20-39"), (40, 60, "40-59"), (60, 80, "60-79"), (80, 101, "80+"))
# columnas nuevas de la tabla (las filas del 22/11 las tienen vacías: se leen
# del 1X2, que en ese formato es lo mismo)
_COLUMNAS_NUEVAS = (("gana_local", "REAL"), ("gana_visita", "REAL"), ("cruzadas", "INTEGER"),
                    ("empate_motor", "REAL"))


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
    tiene = {r[1] for r in con.execute("PRAGMA table_info(parte_ciego)")}
    for col, tipo in _COLUMNAS_NUEVAS:
        if col not in tiene:
            con.execute(f"ALTER TABLE parte_ciego ADD COLUMN {col} {tipo}")
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
    claves = f.keys()
    gl = f["gana_local"] if "gana_local" in claves else None
    gv = f["gana_visita"] if "gana_visita" in claves else None
    return {"local": p["local"], "empate": p["empate"], "visita": p["visita"],
            "elegido": max(CLAVES, key=lambda k: p[k]), "porque": f["porque"],
            # las dos lecturas como las escribió el analista (las del 1X2 del 22/11 son las mismas)
            "ganaLocal": gl if gl is not None else p["local"],
            "ganaVisita": gv if gv is not None else p["visita"],
            "formato": "lecturas" if gl is not None else "1x2",
            "cruzadas": bool(f["cruzadas"]) if "cruzadas" in claves and f["cruzadas"] is not None else False,
            "empateMotor": f["empate_motor"] if "empate_motor" in claves else None,
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


def _porque(body: dict) -> str:
    porque = str(body.get("porque") or "").strip()
    if len(porque) < 20:
        raise CiegoInvalido("falta `porque`: una o dos frases con lo que leíste de cada equipo (K, burbujas, "
                            "EFE, TDE, DTP, prensa) que sostiene el número, sin la cuota")
    return porque


def calzar(gana_local: float, gana_visita: float, empate_motor=None) -> dict:
    """Las dos lecturas → el 1X2. El empate es lo que queda en la intersección
    de los dos «no gana»: 100 − ganaLocal − ganaVisita. Si suman más de 100 se
    cruzan: el empate lo pone el motor (`empate_motor`, un número o una función
    que lo trae) y local y visita se reparten el resto en su proporción."""
    gl, gv = float(gana_local), float(gana_visita)
    tot = gl + gv
    if tot <= 100.0:
        loc, vis = round(gl, 1), round(gv, 1)
        return {"local": loc, "empate": round(100 - loc - vis, 1), "visita": vis,
                "cruzadas": False, "empateMotor": None}
    em = empate_motor() if callable(empate_motor) else empate_motor
    try:
        em = float(em)
    except (TypeError, ValueError):
        em = None
    if em is None or not 0 <= em < 100:
        raise CiegoInvalido(f"ganaLocal + ganaVisita suman {tot:g}: se cruzan (los dos no pueden ganar) y el "
                            "motor no tiene empate para calzarlas. Revisá las dos lecturas: tienen que sumar "
                            "100 o menos")
    resto = 100.0 - em
    loc = round(gl * resto / tot, 1)
    emp = round(em, 1)
    return {"local": loc, "empate": emp, "visita": round(100 - loc - emp, 1),
            "cruzadas": True, "empateMotor": emp}


def empate_motor(fixture_id: int) -> float | None:
    """El empate del 1X2 del MOTOR (`unXDos` de `GET /predicciones/{id}`): sale
    del nivel de los dos, no de la cuota. None si el motor no lo tiene."""
    try:
        from backend.app import prediccion   # app importa este módulo: se trae al usarlo
        return (prediccion(fixture_id).get("unXDos") or {}).get("empate")
    except Exception:  # noqa: BLE001 — sin motor no se calza: calzar lo dice con su motivo
        return None


def normalizar(body: dict, empate_motor=None) -> dict:
    """Las dos lecturas {ganaLocal, ganaVisita, porque} (24/11/2026) o el 1X2
    de antes {local, empate, visita, porque} → el 1X2 en % que suma 100 y las
    lecturas tal cual, o CiegoInvalido."""
    if not isinstance(body, dict):
        raise CiegoInvalido(f"el ciego tiene que ser un objeto: {ESPERADO}")
    if "ganaLocal" in body or "ganaVisita" in body:
        try:
            gl, gv = float(body["ganaLocal"]), float(body["ganaVisita"])
        except (KeyError, TypeError, ValueError):
            raise CiegoInvalido(f"faltan ganaLocal y ganaVisita como números (en %): {ESPERADO}")
        if any(math.isnan(v) or not 0 <= v <= 100 for v in (gl, gv)):
            raise CiegoInvalido("cada lectura va de 0 a 100: es el % de que ESE equipo gane")
        porque = _porque(body)
        p = calzar(gl, gv, empate_motor)
        orden = sorted((p[k] for k in CLAVES), reverse=True)
        if orden[0] == orden[1]:
            raise CiegoInvalido("dos resultados empatados arriba: el ciego tiene que elegir uno "
                                "(un punto más al que elegís)")
        return {**p, "ganaLocal": round(gl, 1), "ganaVisita": round(gv, 1), "porque": porque}
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
    porque = _porque(body)
    return {**p, "porque": porque, "ganaLocal": p["local"], "ganaVisita": p["visita"], "cruzadas": False,
            "empateMotor": None}


def sellar(fixture_id: int, body: dict, hay_parte: bool, empate_motor=None) -> dict:
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
    c = normalizar(body, empate_motor)
    ahora = efedb.ahora()
    with _conectar() as con:
        con.execute("INSERT INTO parte_ciego (fixture_id, local, empate, visita, porque, pitazo, sellado_en, "
                    "gana_local, gana_visita, cruzadas, empate_motor) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (fixture_id, c["local"], c["empate"], c["visita"], c["porque"],
                     pitazo.strftime("%Y-%m-%d %H:%M:%S"), ahora, c["ganaLocal"], c["ganaVisita"],
                     1 if c["cruzadas"] else 0, c["empateMotor"]))
    return {"fixtureId": fixture_id, "ciego": de(fixture_id),
            "siguiente": "ya podés abrir las cuotas (`GET cuotas/{id}`) y seguir con el parte: "
                         "el ciego queda como está, y tu 1X2 publicado va en `pronostico.probabilidades`"}


def _hay_parte(fixture_id: int) -> bool:
    """Un parte de ESTA fecha del partido (parte.existe_vigente): el de una fecha
    vieja (aplazado, `aRehacer`) no abre la casa ni impide sellar (1491)."""
    from backend.analisis import parte as _parte   # parte importa este módulo
    try:
        return _parte.existe_vigente(fixture_id)
    except sqlite3.OperationalError:
        return False   # sin la tabla todavía no hay ningún parte


def tapado(fixture_id: int) -> bool:
    """¿La casa de este partido se le tapa a Cowork? Sí mientras el partido no
    empezó, no hay ciego sellado y no hay parte depositado para esta fecha: con
    el parte ya depositado la casa ya se vio (el modo `rehacer` vuelve sobre partes de antes
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
        texto = ("Todavía no hay partidos cerrados con 1X2 ciego: cuenta desde los del 22/11/2026. "
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


# ── el espejo: el historial propio, SIN la casa (24/11/2026) ───────────────
# El usuario: «tenemos que sacar nuestras propias probabilidades y afinar el
# modelo… feedback inmediato y empezar a calibrar esos porcentajes». El espejo
# es lo que el analista lee ANTES de sellar: lo que dijo contra lo que pasó.
# No trae ningún número de la casa (verla antes del sello es lo que el ciego
# evita) ni plata: solo su propio 1X2 y los resultados. Se recalcula en cada
# llamada (feedback inmediato: cada veredicto cerrado ya entra) y la rutina de
# los lunes lo informa. Es una GUÍA para la lectura, no corrige ningún número
# sola: el analista decide cuánto mover y lo dice en el `porque`.

# un tramo dice algo desde 5 partidos y si se aparta 10+ puntos de lo que se dijo
ESPEJO_MIN_TRAMO = 5
ESPEJO_DESVIO = 10.0
# los últimos casos que se muestran, para leer el patrón a mano
ESPEJO_ULTIMOS = 12


def _tabla(puntos, tramos, que: str) -> tuple[list[dict], list[str]]:
    """puntos: [(lo que se dijo en %, si pasó)] → la calibración por tramo y sus
    avisos (corto / largo desde ESPEJO_MIN_TRAMO partidos y ESPEJO_DESVIO puntos)."""
    acc = {t: {"n": 0, "dijo": 0.0, "aciertos": 0} for _, _, t in tramos}
    for dijo, paso in puntos:
        for lo, hi, t in tramos:
            if lo <= dijo < hi:
                acc[t]["n"] += 1
                acc[t]["dijo"] += dijo
                acc[t]["aciertos"] += bool(paso)
                break
    filas, avisos = [], []
    for _, _, t in tramos:
        v = acc[t]
        dijo = round(v["dijo"] / v["n"], 1) if v["n"] else None
        paso = round(100 * v["aciertos"] / v["n"], 1) if v["n"] else None
        lectura = None
        if v["n"] >= ESPEJO_MIN_TRAMO:
            if paso - dijo >= ESPEJO_DESVIO:
                lectura = "corto"
                avisos.append(f"Cuando le diste {t} % a {que} (en promedio {dijo:g} %), ganó el {paso:g} % "
                              f"({v['aciertos']} de {v['n']}): te quedás CORTO. Si la lectura lo sostiene, "
                              "animate a darle más.")
            elif dijo - paso >= ESPEJO_DESVIO:
                lectura = "largo"
                avisos.append(f"Cuando le diste {t} % a {que} (en promedio {dijo:g} %), ganó el {paso:g} % "
                              f"({v['aciertos']} de {v['n']}): te pasás. Gana menos de lo que decís.")
            else:
                lectura = "bien"
        filas.append({"tramo": t, "n": v["n"], "dijo": dijo, "paso": paso,
                      "intervalo": _wilson(v["aciertos"], v["n"]), "lectura": lectura})
    return filas, avisos


def espejo(filas: list[dict]) -> dict:
    """Las filas: {fixtureId, pitazo, ciego {local, empate, visita, ganaLocal?,
    ganaVisita?, cruzadas?} | None, resultado | None, local?, visita?}. Solo las
    cerradas con ciego desde DESDE. Devuelve, sin nada de la casa:

    - `ganaLocal` / `ganaVisita`: cada lectura binaria (¿gana este equipo?)
      contra si ganó, por tramo — dos datos por partido, la calibración rápida;
    - `calibracion`: lo que el 1X2 le dio al elegido contra lo que ganó;
    - `empate`: el empate (que sale de las dos lecturas) dicho contra el que hubo;
    - `cruzadas`: los partidos en que las dos lecturas sumaron más de 100;
    - `avisos` en castellano y los últimos casos."""
    desde = _utc(DESDE)
    con = sorted((f for f in filas if f.get("ciego") and f.get("resultado") in CLAVES
                  and (_utc(f.get("pitazo")) or desde) >= desde),
                 key=lambda f: str(f.get("pitazo") or ""))
    n = len(con)
    p_el, p_gl, p_gv = [], [], []
    emp_dijo, emp_real, k = 0.0, 0, 0
    cruz = {"n": 0, "elegidoGano": 0}
    ultimos = []
    for f in con:
        cg = f["ciego"]
        c = {kk: float(cg[kk]) for kk in CLAVES}
        gl = float(cg.get("ganaLocal") if cg.get("ganaLocal") is not None else c["local"])
        gv = float(cg.get("ganaVisita") if cg.get("ganaVisita") is not None else c["visita"])
        el = max(CLAVES, key=lambda kk: c[kk])
        r = f["resultado"]
        k += el == r
        emp_dijo += c["empate"]
        emp_real += r == "empate"
        p_el.append((c[el], el == r))
        p_gl.append((gl, r == "local"))
        p_gv.append((gv, r == "visita"))
        if cg.get("cruzadas"):
            cruz["n"] += 1
            cruz["elegidoGano"] += el == r
        ultimos.append({"fixtureId": f.get("fixtureId"), "pitazo": f.get("pitazo"),
                        "partido": " - ".join(x for x in (f.get("local"), f.get("visita")) if x) or None,
                        "ganaLocal": round(gl, 1), "ganaVisita": round(gv, 1),
                        "elegido": el, "leDiste": round(c[el], 1), "empate": round(c["empate"], 1),
                        "cruzadas": bool(cg.get("cruzadas")), "resultado": r, "acerto": el == r})
    calibracion, avisos = _tabla(p_el, TRAMOS, "tu elegido")
    t_gl, a_gl = _tabla(p_gl, TRAMOS_GANA, "que gane el LOCAL")
    t_gv, a_gv = _tabla(p_gv, TRAMOS_GANA, "que gane el VISITANTE")
    avisos = a_gl + a_gv + avisos
    empate = {"dijo": round(emp_dijo / n, 1) if n else None,
              "paso": round(100 * emp_real / n, 1) if n else None, "empates": emp_real, "n": n}
    if n >= 2 * ESPEJO_MIN_TRAMO and empate["dijo"] - empate["paso"] >= ESPEJO_DESVIO:
        avisos.append(f"Al empate (lo que dejan tus dos lecturas) le diste en promedio {empate['dijo']:g} % y "
                      f"hubo {emp_real} en {n} ({empate['paso']:g} %): le das de más, o sea que te quedás "
                      "corto en alguna de las dos lecturas.")
    elif n >= 2 * ESPEJO_MIN_TRAMO and empate["paso"] - empate["dijo"] >= ESPEJO_DESVIO:
        avisos.append(f"Al empate (lo que dejan tus dos lecturas) le diste en promedio {empate['dijo']:g} % y "
                      f"hubo {emp_real} en {n} ({empate['paso']:g} %): le das de menos.")
    if not n:
        texto = "Todavía no hay partidos cerrados con tu ciego: sellá tus dos lecturas."
    else:
        texto = (f"Tu ciego en {n} partidos cerrados: tu elegido ganó {k} ({100 * k / n:.1f} %).")
        if cruz["n"]:
            texto += (f" En {cruz['n']} tus dos lecturas se cruzaron (sumaron más de 100) y el elegido ganó "
                      f"{cruz['elegidoGano']}.")
        if n < 60:
            texto += " Con menos de 60 partidos es una guía, no una regla: movete con la lectura, no con la tabla."
    # la CURVA aprendida de los resultados (24/11/2026, calibracion_lecturas):
    # lo que valen tus lecturas en realidad, con el previo que la sostiene si hay pocos
    from backend.analisis import calibracion_lecturas as _cal
    curvas = _cal.ajuste_de([{"ganaLocal": u["ganaLocal"], "ganaVisita": u["ganaVisita"], "resultado": u["resultado"],
                              "pitazo": u["pitazo"]}
                             for u in ultimos])
    curvas = {lado: {**cf, "lectura": _cal.lectura(cf)} for lado, cf in curvas.items()}
    return {"desde": DESDE, "n": n, "aciertos": k, "ganaLocal": t_gl, "ganaVisita": t_gv, "curvas": curvas,
            "calibracion": calibracion, "empate": empate, "cruzadas": cruz,
            "avisos": avisos, "ultimos": list(reversed(ultimos[-ESPEJO_ULTIMOS:])), "texto": texto,
            "nota": "Sin la casa a propósito: son tus lecturas contra lo que pasó. No es una regla que "
                    "corrija el número sola; decí en el `porque` si la usaste."}
