"""Motor de Niveles (§2) — espejo de src/motor/levels.ts.

Nivel = P + G + 1: P = puntos/20 en ventana móvil de 20 partidos terminados,
G = balance de goles de los últimos 5 de esa ventana.
"""
from bisect import bisect_right

DEFAULT_LEVEL = 0.5


def calcular_niveles(hist: list[tuple]) -> list[tuple]:
    """Historia completa de un equipo → una fila de nivel por partido.

    `hist`: [(fixture_id, date, gf, ga)] ordenada por (date, fixture_id).
    Regla retroactiva (§2.2): con <20 partidos todos valen 0.5; en el partido
    nº 20 se calcula el primer nivel real y se asigna a los 20 primeros.
    Devuelve [(fixture_id, date, level)].
    """
    n = len(hist)
    if n == 0:
        return []
    if n < 20:
        return [(f, d, DEFAULT_LEVEL) for f, d, _, _ in hist]
    pts = [3 if gf > ga else 1 if gf == ga else 0 for _, _, gf, ga in hist]
    levels = [0.0] * n
    for i in range(19, n):
        p = sum(pts[i - 19 : i + 1]) / 20
        dg = tg = 0
        for j in range(i - 4, i + 1):
            _, _, gf, ga = hist[j]
            dg += gf - ga
            tg += gf + ga
        g = 0.0 if tg == 0 else dg / tg
        levels[i] = p + g + 1
    for i in range(19):
        levels[i] = levels[19]
    return [(h[0], h[1], levels[i]) for i, h in enumerate(hist)]


class CacheNiveles:
    """Cache en memoria de team_levels con lookup por bisect (§3.4).

    `filas`: iterable de (team_id, date, level) — no requiere orden previo.
    """

    def __init__(self, filas):
        por_equipo: dict[int, list[tuple]] = {}
        for team_id, date, level in filas:
            por_equipo.setdefault(team_id, []).append((date, level))
        self._fechas: dict[int, list[str]] = {}
        self._niveles: dict[int, list[float]] = {}
        for team_id, pares in por_equipo.items():
            pares.sort()
            self._fechas[team_id] = [p[0] for p in pares]
            self._niveles[team_id] = [p[1] for p in pares]

    def nivel_a_fecha(self, team_id: int, date: str, fallback: float) -> float:
        """Último nivel con date <= fecha; `fallback` si no hay (§2.3).

        Incluye la fila del propio partido si comparte fecha exacta — misma
        semántica que levelAt() del motor TS.
        """
        fechas = self._fechas.get(team_id)
        if not fechas:
            return fallback
        i = bisect_right(fechas, date)
        return self._niveles[team_id][i - 1] if i > 0 else fallback
