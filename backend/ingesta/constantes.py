"""Motor de Constantes K (§3) — espejo de src/motor/constants.ts.

Paso 1: valores instantáneos q* ponderados por el nivel del rival A LA FECHA
del partido (fallback 1.0, settings.py del pipeline original).
Paso 2: acumuladores de racha k* con reseteo al cambiar el signo.
Las familias nuevas (k_dc, márgenes) se delegan a backend.familias_k para que
la fórmula viva en un único sitio.
"""
from backend.familias_k import FAMILIAS0, FAMILIAS_COLS, step_familias

VISITOR_MULTIPLIER = 1.4
CONSTANTS_LEVEL_FALLBACK = 1.0

# Columnas de la tabla constants que produce este módulo (mismo orden del INSERT).
COLUMNAS = (
    "q_local", "q_visita", "q_negativo",
    "q_goles_anotado", "q_goles_recibido",
    "q_goles_local_anotado", "q_goles_local_recibido",
    "q_goles_visita_anotado", "q_goles_visita_recibido",
    "k_positivo", "k_negativo",
    "k_positivo_local", "k_negativo_local",
    "k_positivo_visita", "k_negativo_visita",
    "k_goles_anotado", "k_goles_recibido",
    "k_goles_local_anotado", "k_goles_local_recibido",
    "k_goles_visita_anotado", "k_goles_visita_recibido",
    "q_dc",
) + FAMILIAS_COLS

_K0 = {
    "k_positivo": 0.0, "k_negativo": 0.0,
    "k_positivo_local": 0.0, "k_negativo_local": 0.0,
    "k_positivo_visita": 0.0, "k_negativo_visita": 0.0,
    "k_goles_anotado": 0.0, "k_goles_recibido": 0.0,
    "k_goles_local_anotado": 0.0, "k_goles_local_recibido": 0.0,
    "k_goles_visita_anotado": 0.0, "k_goles_visita_recibido": 0.0,
}


def q_valores(is_local: bool, gf: int, ga: int, nivel: float) -> dict:
    """Valores instantáneos q* de un partido (§3.2)."""
    dif = abs(gf - ga)
    res = 1 if gf > ga else 0 if gf == ga else -1
    q_anotado = gf * nivel
    q_recibido = -ga * nivel
    return {
        "q_local": dif * res * nivel if is_local else None,
        "q_visita": None if is_local else VISITOR_MULTIPLIER * dif * res * nivel,
        "q_negativo": dif * res * nivel if res == -1 else 0.0,
        "q_goles_anotado": q_anotado,
        "q_goles_recibido": q_recibido,
        "q_goles_local_anotado": q_anotado if is_local else None,
        "q_goles_local_recibido": q_recibido if is_local else None,
        "q_goles_visita_anotado": None if is_local else q_anotado,
        "q_goles_visita_recibido": None if is_local else q_recibido,
    }


def paso_k(prev: dict, is_local: bool, gf: int, ga: int, nivel: float) -> tuple[dict, dict]:
    """Un partido de avance de los 12 acumuladores núcleo (§3.3).

    Regla general: acumulan mientras el signo se mantiene y se resetean a 0 al
    cambiar (o en empate). Los k local/visita SOLO se actualizan en su condición
    (si no, conservan valor); k_goles_recibido acumula valor absoluto.
    Devuelve (q, k) como dicts con nombres de columna reales.
    """
    q = q_valores(is_local, gf, ga, nivel)
    q_any = q["q_local"] if is_local else q["q_visita"]
    k = dict(prev)

    # k_positivo también se resetea si q_any es None (goles nulos)
    k["k_positivo"] = prev["k_positivo"] + q_any if q_any is not None and q_any > 0 else 0.0
    k["k_negativo"] = prev["k_negativo"] + q["q_negativo"] if q["q_negativo"] < 0 else 0.0

    qa, qr = q["q_goles_anotado"], q["q_goles_recibido"]
    if is_local:
        ql = q["q_local"]
        k["k_positivo_local"] = prev["k_positivo_local"] + ql if ql is not None and ql > 0 else 0.0
        k["k_negativo_local"] = prev["k_negativo_local"] + ql if ql is not None and ql < 0 else 0.0
        k["k_goles_local_anotado"] = prev["k_goles_local_anotado"] + qa if qa > 0 else 0.0
        k["k_goles_local_recibido"] = prev["k_goles_local_recibido"] + abs(qr) if qr < 0 else 0.0
    else:
        qv = q["q_visita"]
        k["k_positivo_visita"] = prev["k_positivo_visita"] + qv if qv is not None and qv > 0 else 0.0
        k["k_negativo_visita"] = prev["k_negativo_visita"] + qv if qv is not None and qv < 0 else 0.0
        k["k_goles_visita_anotado"] = prev["k_goles_visita_anotado"] + qa if qa > 0 else 0.0
        k["k_goles_visita_recibido"] = prev["k_goles_visita_recibido"] + abs(qr) if qr < 0 else 0.0

    k["k_goles_anotado"] = prev["k_goles_anotado"] + qa if qa > 0 else 0.0
    k["k_goles_recibido"] = prev["k_goles_recibido"] + abs(qr) if qr < 0 else 0.0
    return q, k


def calcular_constantes(hist: list[tuple], niveles) -> list[dict]:
    """Historia de un equipo → una fila de constants por partido.

    `hist`: [(fixture_id, date, is_local, gf, ga, rival_id)] ordenada por
    (date, fixture_id). `niveles`: CacheNiveles para el nivel del rival a la
    fecha del partido (fallback 1.0, §3.1).
    Devuelve dicts con fixture_id, date y todas las COLUMNAS.
    """
    filas = []
    k = dict(_K0)
    fam = dict(FAMILIAS0)
    for fixture_id, date, is_local, gf, ga, rival_id in hist:
        nivel = niveles.nivel_a_fecha(rival_id, date, CONSTANTS_LEVEL_FALLBACK)
        q, k = paso_k(k, is_local, gf, ga, nivel)
        q_dc, fam = step_familias(fam, is_local, gf, ga, nivel)
        fila = {"fixture_id": fixture_id, "date": date, "q_dc": q_dc}
        fila.update(q)
        fila.update(k)
        fila.update(fam)
        filas.append(fila)
    return filas
