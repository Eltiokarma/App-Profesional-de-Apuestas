"""Discretización y fusión (§4) — espejo de discretizer_db.py.

Método A: bins uniformes 0–9 ajustados sobre TODOS los niveles de levels.db
(equivale a KBinsDiscretizer(n_bins=10, strategy='uniform')).
Fusión: k = k_positivo + k_negativo (NULL → 0); los k_goles_* pasan tal cual.
"""
from math import floor

DEFAULT_LEVEL = 0.5


class DiscretizadorUniforme:
    """bin = floor((nivel − min) / (max − min) × 10), recortado a [0, 9]."""

    def __init__(self, nivel_min: float, nivel_max: float):
        self.min = nivel_min
        self.max = nivel_max
        self._ancho = nivel_max - nivel_min

    def bin(self, nivel: float) -> int:
        if self._ancho <= 0:
            return 0
        b = floor((nivel - self.min) / self._ancho * 10)
        return 0 if b < 0 else 9 if b > 9 else b


def fusion(k_pos, k_neg) -> float:
    """Suma neta de la racha; NULL se trata como 0.0 (§4.2)."""
    return (k_pos or 0.0) + (k_neg or 0.0)
