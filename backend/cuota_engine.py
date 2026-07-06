"""Motor de la K de cuotas (k_cuota) — familia por MERCADO sobre la cuota 1X2
prepartido capturada (tabla odds, bet_name='Match Winner'). Vive en su propia
tabla `constants_cuota` (constants.db), independiente de `constants`.

Regla (definición final del proyecto):
- 3 rachas por equipo, SUMA PURA de la cuota (sin ponderar por nivel):
    k_cuota_victoria: si GANA → += su cuota de victoria; si no gana → 0 (revienta).
    k_cuota_empate:   si EMPATA → += cuota de empate;    si no empata → 0.
    k_cuota_derrota:  si PIERDE → += cuota de derrota (= victoria del rival); si no → 0.
- Variantes _local/_visita: misma regla pero SOLO se tocan en su contexto
  (si el partido no fue en ese contexto, conservan valor) — como k_positivo_local/visita.
- Partido SIN cuota capturada: se SALTA (no aporta ni revienta; la racha continúa
  como si el partido no existiera).
- Alcance: solo partidos de 2026.

El motor mock/demo NO usa esto: las barras de k_cuota se llenan solo con datos reales.
"""
import math

# Los 9 acumuladores de constants_cuota, en orden.
CUOTA_K_COLS = (
    "k_cuota_victoria", "k_cuota_victoria_local", "k_cuota_victoria_visita",
    "k_cuota_empate", "k_cuota_empate_local", "k_cuota_empate_visita",
    "k_cuota_derrota", "k_cuota_derrota_local", "k_cuota_derrota_visita",
)
CUOTA0 = {k: 0.0 for k in CUOTA_K_COLS}


def step_cuota(st, resultado, is_local, cuota_v, cuota_e, cuota_d):
    """Avanza los 9 acumuladores un partido. `st` = valores previos (dict con
    CUOTA_K_COLS). `resultado` = 1 gana / 0 empata / -1 pierde. Si `cuota_v is None`
    (partido sin cuota) se SALTA: devuelve el estado sin cambios."""
    if cuota_v is None:
        return dict(st)  # sin cuota → la racha continúa como si no existiera
    r = resultado
    out = dict(st)
    # TOTAL: suma pura mientras se mantiene la condición; 0 al romperse.
    out["k_cuota_victoria"] = st["k_cuota_victoria"] + cuota_v if r == 1 else 0.0
    out["k_cuota_empate"] = st["k_cuota_empate"] + cuota_e if r == 0 else 0.0
    out["k_cuota_derrota"] = st["k_cuota_derrota"] + cuota_d if r == -1 else 0.0
    # LOCAL / VISITA: solo se tocan en su contexto; en el otro conservan valor.
    if is_local:
        out["k_cuota_victoria_local"] = st["k_cuota_victoria_local"] + cuota_v if r == 1 else 0.0
        out["k_cuota_empate_local"] = st["k_cuota_empate_local"] + cuota_e if r == 0 else 0.0
        out["k_cuota_derrota_local"] = st["k_cuota_derrota_local"] + cuota_d if r == -1 else 0.0
    else:
        out["k_cuota_victoria_visita"] = st["k_cuota_victoria_visita"] + cuota_v if r == 1 else 0.0
        out["k_cuota_empate_visita"] = st["k_cuota_empate_visita"] + cuota_e if r == 0 else 0.0
        out["k_cuota_derrota_visita"] = st["k_cuota_derrota_visita"] + cuota_d if r == -1 else 0.0
    return out


# --- cuotas sintéticas (relleno de huecos §7) -------------------------------
HOME_ADV = 0.35   # ventaja de localía en "niveles"
P_DRAW = 0.26     # masa fija de empate
OVERROUND = 1.06  # margen de casa (para que 1/cuotas sume >1)


def cuotas_sinteticas(nivel_home, nivel_away):
    """Cuotas 1X2 (home, draw, away) aproximadas desde la diferencia de nivel.
    Devuelve odds decimales redondeadas. Determinista."""
    diff = (nivel_home - nivel_away) + HOME_ADV
    s = 1.0 / (1.0 + math.exp(-1.1 * diff))  # cuota (share) de local sobre el no-empate
    p_home = (1.0 - P_DRAW) * s
    p_away = (1.0 - P_DRAW) * (1.0 - s)
    # odd = 1/(p·margen): con margen>1 la suma de 1/odds queda >1 (overround de casa)
    odd = lambda p: round(1.0 / (max(p, 1e-6) * OVERROUND), 2)
    return odd(p_home), odd(P_DRAW), odd(p_away)
