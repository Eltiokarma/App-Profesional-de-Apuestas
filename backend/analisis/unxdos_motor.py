"""El 1X2 del motor: μ_partido de los dos lados → (local · empate · visita).

`μ_partido` son PUNTOS esperados, no goles: meterlo en un Poisson como λ es un
error de unidad (se hizo en 78 de 209 partes, octubre de 2026). Esta es la
conversión calibrada contra resultados reales con
`python -m backend.backtest_unxdos_motor` (docs/MOTOR_SAD_EXTRACCION.md §5.6):
logística multinomial sobre d = μ_local − μ_visita y d², empate de referencia.

Es la fuente «motor» de las tres del pronóstico (disciplina 33): no mira la
forma, las K, el once ni el mercado. No toca μ ni el gap: solo traduce el
número que el motor ya da a la escala del 1X2. Espejo TS en src/lib/unxdos.ts,
los dos contra scripts/casos_unxdos.json.
"""
from __future__ import annotations

import math

# [intercepto, d, d²] por clase, contra el empate. Recalibrar = correr el
# backtest, copiar `coeficientes` acá Y en src/lib/unxdos.ts, y rehacer los
# vectores dorados (scripts/casos_unxdos.json).
COEF = {
    "local": (0.29851, 0.44446, 0.03539),
    "visita": (0.18515, -0.48092, 0.04911),
}

CALIBRACION = {
    "fecha": "2026-10-21",
    "partidos": 51254,
    "equipos": 707,
    "desde": "2019-02-17",
    "hasta": "2026-10-21",
    # prueba temporal (el 20 % más reciente, 10.251 partidos, desde el 01/12/2025)
    "logLoss": 1.0512,
    "logLossFrecuencia": 1.0707,
    "logLossPoissonSobreMu": 1.0590,
    "acierto": 0.4647,
}

NOTA = ("probabilidades del MOTOR solo (nivel, rival y localía, μ v2): logística calibrada "
        "sobre 51.254 partidos del padrón 2019-2026. Es una de las tres fuentes del pronóstico, "
        "no el pronóstico: no ve once, forma, K ni mercado")


def probabilidades(mu_local: float | None, mu_visita: float | None) -> dict | None:
    """Porcentajes que suman 100 (una decimal). None si falta un μ."""
    if mu_local is None or mu_visita is None:
        return None
    d = float(mu_local) - float(mu_visita)
    x = (1.0, d, d * d)
    zl = sum(b * v for b, v in zip(COEF["local"], x))
    zv = sum(b * v for b, v in zip(COEF["visita"], x))
    el, ev = math.exp(max(-30.0, min(30.0, zl))), math.exp(max(-30.0, min(30.0, zv)))
    s = 1.0 + el + ev
    loc, emp = round(100 * el / s, 1), round(100 / s, 1)
    return {"local": loc, "empate": emp, "visita": round(100 - loc - emp, 1)}


def del_partido(mu_local: float | None, mu_visita: float | None) -> dict | None:
    p = probabilidades(mu_local, mu_visita)
    if p is None:
        return None
    return {**p, "d": round(float(mu_local) - float(mu_visita), 4), "modelo": "logistica-mu-v1",
            "calibracion": CALIBRACION, "nota": NOTA}
