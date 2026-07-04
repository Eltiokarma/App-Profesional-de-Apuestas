"""Familias K derivadas del motor SAD que NO forman parte de los 12 acumuladores
originales del pipeline: Doble Oportunidad (§3.6) y Márgenes (§3.7).

Una sola implementación en Python (espejo fiel de src/motor/constants.ts),
reusada por seed_demo (pipeline de demo) y backfill_kdc (puente sobre una
constants.db real). Así la fórmula vive en un único sitio y no puede desincronizarse.
"""

# Claves (= columnas en la tabla constants) que mantienen estas familias.
FAMILIAS_COLS = (
    "k_dc", "k_dc_local", "k_dc_visita",
    "k_vic1", "k_vic1_local", "k_vic1_visita",
    "k_vic2", "k_vic2_local", "k_vic2_visita",
    "k_vic3", "k_vic3_local", "k_vic3_visita",
    "k_der1", "k_der1_local", "k_der1_visita",
    "k_der2", "k_der2_local", "k_der2_visita",
    "k_der3", "k_der3_local", "k_der3_visita",
)
FAMILIAS0 = {k: 0.0 for k in FAMILIAS_COLS}


def step_familias(st, is_local, gf, ga, nivel):
    """Un partido de avance de las familias nuevas. `st` trae los valores previos
    (dict con las claves de FAMILIAS_COLS). Devuelve (q_dc, nuevo_dict).

    - Doble Oportunidad (§3.6): racha "sin perder"; empate aporta 0.5·nivel, la
      derrota resetea; sin multiplicador visitante.
    - Márgenes (§3.7): aporte plano nivel; solo el bucket del margen EXACTO del
      signo de este partido acumula, los demás resetean; el empate resetea todo.
    - Local/visita solo se tocan en su condición (si no, conservan el valor).
    """
    dif = abs(gf - ga)
    perdio = gf < ga

    q_dc = 0.0 if perdio else max(dif * nivel, 0.5 * nivel)
    out = {
        "k_dc": 0.0 if perdio else st["k_dc"] + q_dc,
        "k_dc_local": (0.0 if perdio else st["k_dc_local"] + q_dc) if is_local else st["k_dc_local"],
        "k_dc_visita": (0.0 if perdio else st["k_dc_visita"] + q_dc) if not is_local else st["k_dc_visita"],
    }

    gv = min(dif, 3) if gf > ga else 0  # bucket ganado (1/2/3+); 0 si no ganó
    gd = min(dif, 3) if perdio else 0    # bucket perdido (1/2/3+); 0 si no perdió
    for signo, g in (("vic", gv), ("der", gd)):
        for b in (1, 2, 3):
            base = f"k_{signo}{b}"
            kl, kv = base + "_local", base + "_visita"
            out[base] = st[base] + nivel if g == b else 0.0
            out[kl] = (st[kl] + nivel if g == b else 0.0) if is_local else st[kl]
            out[kv] = (st[kv] + nivel if g == b else 0.0) if not is_local else st[kv]
    return q_dc, out
