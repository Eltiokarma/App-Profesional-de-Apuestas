"""Motor de la K de cuotas (k_cuota) — familia por MERCADO sobre las cuotas
prepartido capturadas (tabla odds): el 1X2 (`bet_name='Match Winner'`) y la
Doble Oportunidad (`bet_name='Double Chance'`). Vive en su propia tabla
`constants_cuota` (constants.db), independiente de `constants`.

Regla (definición final del proyecto):
- 6 rachas por equipo, SUMA PURA de la cuota (sin ponderar por nivel):
    1X2 (el evento exacto):
      k_cuota_victoria: si GANA → += su cuota de victoria; si no gana → 0 (revienta).
      k_cuota_empate:   si EMPATA → += cuota de empate;    si no empata → 0.
      k_cuota_derrota:  si PIERDE → += cuota de derrota (= victoria del rival); si no → 0.
    Doble Oportunidad, SIEMPRE desde la perspectiva del equipo analizado
    (para el visitante, "1" es su victoria: 1X = Draw/Away del mercado):
      k_cuota_dc1x: si NO PIERDE (gana o empata) → += cuota 1X; si pierde → 0.
      k_cuota_dc12: si NO EMPATA (gana o pierde) → += cuota 12; si empata → 0.
      k_cuota_dcx2: si NO GANA (empata o pierde) → += cuota X2; si gana  → 0.
- Variantes _local/_visita: misma regla pero SOLO se tocan en su contexto
  (si el partido no fue en ese contexto, conservan valor) — como k_positivo_local/visita.
- Partido SIN cuota capturada: se SALTA (no aporta ni revienta; la racha continúa
  como si el partido no existiera). Los dos mercados se saltan por SEPARADO: un
  partido con 1X2 pero sin Doble Oportunidad mueve el primero y salta el segundo.
- Alcance: solo partidos de 2026.

El motor mock/demo NO usa esto: las barras de k_cuota se llenan solo con datos reales.
"""
import math

# Familias por mercado: (nombre, ¿la racha sigue viva con este resultado?).
# El resultado `r` es 1 gana · 0 empata · -1 pierde, del equipo analizado.
FAMILIAS_1X2 = (
    ("victoria", lambda r: r == 1),
    ("empate", lambda r: r == 0),
    ("derrota", lambda r: r == -1),
)
FAMILIAS_DC = (
    ("dc1x", lambda r: r >= 0),   # no pierde
    ("dc12", lambda r: r != 0),   # no empata
    ("dcx2", lambda r: r <= 0),   # no gana
)

# Los 18 acumuladores de constants_cuota, en orden (los 9 del 1X2 primero: el
# orden es el de las columnas de la tabla y de los INSERT).
CUOTA_K_COLS = tuple(
    f"k_cuota_{nombre}{suf}"
    for familias in (FAMILIAS_1X2, FAMILIAS_DC)
    for nombre, _ in familias
    for suf in ("", "_local", "_visita")
)
CUOTA0 = {k: 0.0 for k in CUOTA_K_COLS}


def _paso_mercado(out, st, familias, cuotas, r, is_local):
    """Avanza las 3 rachas (total + la del contexto) de un mercado. Si alguna
    cuota del mercado falta, el mercado entero se SALTA (estado sin cambios)."""
    if any(c is None for c in cuotas):
        return
    suf = "_local" if is_local else "_visita"
    for (nombre, sigue_viva), cuota in zip(familias, cuotas):
        base = f"k_cuota_{nombre}"
        viva = sigue_viva(r)
        # TOTAL: suma pura mientras se mantiene la condición; 0 al romperse.
        out[base] = st[base] + cuota if viva else 0.0
        # LOCAL / VISITA: solo se toca la del contexto; la otra conserva valor.
        out[base + suf] = st[base + suf] + cuota if viva else 0.0


def step_cuota(st, resultado, is_local, cuota_v, cuota_e, cuota_d,
               cuota_1x=None, cuota_12=None, cuota_x2=None):
    """Avanza los 18 acumuladores un partido. `st` = valores previos (dict con
    CUOTA_K_COLS). `resultado` = 1 gana / 0 empata / -1 pierde. Las cuotas de
    Doble Oportunidad ya vienen en la perspectiva del equipo. Un mercado con
    alguna cuota None se salta; si faltan los dos, devuelve el estado igual."""
    out = dict(st)
    _paso_mercado(out, st, FAMILIAS_1X2, (cuota_v, cuota_e, cuota_d), resultado, is_local)
    _paso_mercado(out, st, FAMILIAS_DC, (cuota_1x, cuota_12, cuota_x2), resultado, is_local)
    return out


# --- favorito / tapado (ROADMAP_BURBUJAS §3) --------------------------------
# Se derivan AL LEER (como todo lo derivado): de la cuota 1X2 de cada fila y
# del nivel del rival de /constantes. Ponderan por nivel —a diferencia de las
# 6 de arriba, que son suma pura— porque la spec lo pide: ganar como favorito
# ante un rival fuerte vale más, y la sorpresa grande (cuota alta) contra uno
# fuerte, más todavía.
#   favorito: el equipo cierra FAVORITO (su cuota de victoria es la menor del
#             1X2). Gana → += (1/cuota) × nivel_rival. No gana → 0 (revienta).
#   tapado:   cierra NO favorito (el rival paga menos por ganar). Gana →
#             += cuota × nivel_rival. No gana → 0.
# El partido donde no aplica (sin cuota, sin nivel, o el otro rol) se SALTA:
# no aporta ni revienta, como los huecos de cuota de §3.8.
FAV_K_COLS = tuple(f"{b}{suf}" for b in ("favorito", "tapado") for suf in ("", "Local", "Visita"))


def rol_de_mercado(cuota_v, cuota_e, cuota_d):
    """True favorito · False tapado · None sin cuota o parejo (sin rol claro)."""
    if cuota_v is None or cuota_d is None:
        return None
    if cuota_v < cuota_d and (cuota_e is None or cuota_v < cuota_e):
        return True
    if cuota_v > cuota_d:
        return False
    return None


def favorito_tapado(filas: list[dict], nivel_rival: dict) -> list[dict]:
    """Por fila (en orden cronológico): {rol, k: {favorito, favoritoLocal, …}}.
    `filas` = [{fixtureId, esLocal, resultado, cuotaV, cuotaE, cuotaD}];
    `nivel_rival` = {fixtureId: nivel} (sin nivel, la fila se salta)."""
    st = {k: 0.0 for k in FAV_K_COLS}
    out = []
    for f in filas:
        rol = rol_de_mercado(f.get("cuotaV"), f.get("cuotaE"), f.get("cuotaD"))
        nivel = nivel_rival.get(f["fixtureId"])
        if rol is not None and nivel is not None:
            base = "favorito" if rol else "tapado"
            aporte = (1.0 / f["cuotaV"]) * nivel if rol else f["cuotaV"] * nivel
            suf = "Local" if f["esLocal"] else "Visita"
            gana = f["resultado"] == 1
            st[base] = st[base] + aporte if gana else 0.0
            st[base + suf] = st[base + suf] + aporte if gana else 0.0
        out.append({"rol": rol, "k": {k: round(v, 4) for k, v in st.items()}})
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


def dc_desde_1x2(cuota_home, cuota_draw, cuota_away):
    """Doble Oportunidad (Home/Draw, Home/Away, Draw/Away) derivada del MISMO
    1X2: se suman las probabilidades implícitas de sus dos patas. Solo se usa
    para el relleno SINTÉTICO (odds marcadas bookmaker_name='SYNTHETIC'); la
    cuota real de Doble Oportunidad, cuando existe, manda siempre."""
    p_h, p_d, p_a = 1.0 / cuota_home, 1.0 / cuota_draw, 1.0 / cuota_away
    odd = lambda p: round(1.0 / max(p, 1e-6), 2)
    return odd(p_h + p_d), odd(p_h + p_a), odd(p_d + p_a)
