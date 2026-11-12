"""NBA · fase 0 · el motor SAD llevado al básquet (docs/NBA_FASE0.md §2).

Es la MISMA teoría de docs/MOTOR_SAD_EXTRACCION.md con los cambios que el
básquet obliga, todos a la vista como parámetro (nada de esto toca el motor
del fútbol, que sigue sagrado):

  nivel = P + G + 1
    P = 3 × victorias/20 en la ventana de 20 (sin empate: 3/0 en vez de 3/1/0)
    G = ESCALA_G × Σ(pf − pa)/Σ(pf + pa) de los últimos 5
        (en fútbol ese cociente ronda ±0,3; en básquet ±0,05: sin escalar la G
        no pesa nada. La fase 0 elige ESCALA_G en el ENTRENAMIENTO.)
  q = (|pf − pa| / ESCALA_MARGEN) × res × nivel_rival   (× 1,4 de visita)
        ganar por 10 en básquet ≈ ganar por 1 en fútbol
  k⁺ acumula mientras gana, k⁻ mientras pierde; sin empate la K nunca queda en
  0: cada derrota corta la racha + y abre la − (reventón «al otro signo»).

Diferencias con el fútbol que importan para medir SIN FUGA:
  - El nivel de un partido es el de ANTES del partido (el del partido anterior).
    No se usa la regla retroactiva del §2.2: con menos de 20 partidos previos
    el equipo no tiene nivel y el partido no entra al backtest.
  - El nivel del rival en q también es el previo al partido (fallback 1,0).
  - Cancha neutral (burbuja 2020, partidos en México/París): sin factor de
    visita y no mueve las familias local/visita.
"""
from __future__ import annotations

from statistics import median

from backend.jugadores import dias_descanso

VENTANA = 20
ULTIMOS = 5
ESCALA_G = 10.0          # propuesta; la fase 0 la elige en el entrenamiento
ESCALA_MARGEN = 10.0     # puntos que valen «un gol» en q
VISITA_MULT = 1.4        # el del fútbol, SIN calibrar para básquet
NIVEL_RIVAL_FALLBACK = 1.0
DESCANSO_TOPE = 4        # 4 días o más es «descansado»; el primero de temporada también


def nivel_de(ventana: list[tuple], escala_g: float = ESCALA_G, por_rival: bool = False) -> float:
    """`ventana`: los últimos 20 (pf, pa) o (pf, pa, nivel_rival) en orden.
    Nivel = P + G + 1. Con `por_rival` (tenis, docs/TENIS_FASE0.md §4) la P
    pesa cada victoria por el nivel del rival: P = 3·Σ(victoria·nr)/Σ nr, que
    con todos los rivales iguales es la P de siempre (misma escala 0-3)."""
    if por_rival:
        nr = [(v[2] if len(v) > 2 and v[2] is not None else NIVEL_RIVAL_FALLBACK) for v in ventana]
        p = 3 * sum(n for v, n in zip(ventana, nr) if v[0] > v[1]) / sum(nr)
    else:
        p = 3 * sum(1 for v in ventana if v[0] > v[1]) / VENTANA
    u5 = ventana[-ULTIMOS:]
    dg = sum(v[0] - v[1] for v in u5)
    tg = sum(v[0] + v[1] for v in u5)
    g = 0.0 if tg == 0 else dg / tg
    return p + escala_g * g + 1


FAMILIAS = {"victorias": 1, "derrotas": -1}
# LA K DE PUNTOS (12/11/2026, usuario: «medir la K de goles… análisis por
# diferencia de puntos»): en el básquet todos anotan siempre, así que «anotó»
# es anotar POR ENCIMA de su media de los 20 partidos anteriores (y «recibió»,
# recibir por encima de su media). La K acumula el exceso (÷ ESCALA_MARGEN)
# por el nivel del rival y revienta a 0 la primera vez que queda por debajo.
# Puede tomar valores grandes: no importa. No toca victorias/derrotas.
FAMILIAS_PUNTOS = ("anota", "recibe")
# LA SEGUNDA VARA (12/11/2026, usuario: «la 1 más la 3»): anotar / recibir por
# encima de lo que la CASA esperaba de ese equipo en ese partido, sacado del
# más/menos y del hándicap: local = (total − hándicap del local)/2, visita =
# (total + hándicap del local)/2. Partido sin línea: estas dos no se mueven.
FAMILIAS_CASA = ("anotaCasa", "recibeCasa")


def _familia0() -> dict:
    return {"k": 0.0, "racha": 0, "kPico": 0.0, "conds": [], "reventones": []}


def _nuevo() -> dict:
    return {"res": [], "kPos": 0.0, "kNeg": 0.0, "kLoc": 0.0, "kVis": 0.0,
            "racha": 0, "kPico": 0.0, "conds": [], "reventones": {1: [], -1: []}, "ultimo": None, "nivel": None,
            "fam": {f: _familia0() for f in (*FAMILIAS, *FAMILIAS_PUNTOS, *FAMILIAS_CASA)}, "pts": []}


def _contramano(conds: list, cond: str | None) -> bool:
    """La contramano del fútbol (REVENTON §12): 2/3 o más de la racha en la
    condición contraria a la de este partido (neutral no cuenta para ninguna)."""
    contra = sum(1 for c in conds if c is not None and cond is not None and c != cond)
    return bool(conds) and cond is not None and contra * 3 >= 2 * len(conds)


def _base(rev: list[dict]) -> dict:
    niv = [r["nivelRival"] for r in rev if r["nivelRival"] is not None]
    return {"reventonesSigno": len(rev),
            "medianaPartidos": median(r["partidos"] for r in rev) if rev else None,
            "medianaKPico": median(r["kPico"] for r in rev) if rev else None,
            "medianaNivelRival": median(niv) if niv else None}


def _vista_familia(st: dict, nombre: str, cond: str | None, nivel_rival) -> dict:
    """La familia separada, como la K de goles: la de VICTORIAS acumula mientras
    gana y vuelve a 0 al perder; la de DERROTAS, al revés (su K es positiva:
    cuánto lleva perdiendo). `signo` es la dirección del riesgo (+1 victorias,
    −1 derrotas) y 0 si la familia está en cero (no hay burbuja abierta)."""
    f = st["fam"][nombre]
    return {"nivel": st["nivel"], "nivelRival": nivel_rival, "k": f["k"], "racha": f["racha"], "kPico": f["kPico"],
            "signo": FAMILIAS[nombre] if f["k"] > 0 else 0, "contramano": _contramano(f["conds"], cond),
            **_base(f["reventones"])}


def _signo(v: float) -> int:
    return 1 if v > 0 else -1 if v < 0 else 0


def _media_puntos(st: dict) -> tuple[float, float] | None:
    """Media de puntos a favor y en contra de los últimos 20 partidos (antes de este)."""
    if len(st["pts"]) < VENTANA:
        return None
    u = st["pts"][-VENTANA:]
    return sum(x[0] for x in u) / VENTANA, sum(x[1] for x in u) / VENTANA


def _vista_puntos(st: dict) -> dict:
    m = _media_puntos(st)
    out = {"mediaAnota": None if m is None else m[0], "mediaRecibe": None if m is None else m[1]}
    for n in (*FAMILIAS_PUNTOS, *FAMILIAS_CASA):
        f = st["fam"][n]
        out[n] = {"k": f["k"], "racha": f["racha"], "kPico": f["kPico"], "abierta": f["k"] > 0, **_base(f["reventones"])}
    return out


def _previo(st: dict, rival: dict, local: bool, neutral: bool, fecha: str, temporada) -> dict:
    """Lo que se sabe del equipo ANTES del partido (nada de este partido)."""
    k = st["kPos"] + st["kNeg"]
    s = _signo(k)
    rev = st["reventones"].get(s, []) if s else []
    desc = None
    if st["ultimo"] is not None:
        desc = DESCANSO_TOPE if st["ultimo"][1] != temporada else dias_descanso(st["ultimo"][0], fecha)
    cond = None if neutral else ("L" if local else "V")
    return {
        "nivel": st["nivel"], "nivelRival": rival["nivel"], "partidosPrevios": len(st["res"]),
        "k": k, "kCond": (st["kLoc"] if local else st["kVis"]) if not neutral else 0.0,
        "signo": s, "racha": st["racha"], "kPico": st["kPico"],
        "descanso": None if desc is None else max(0, min(DESCANSO_TOPE, desc)),
        **_base(rev), "contramano": _contramano(st["conds"], cond),
        "familias": {n: _vista_familia(st, n, cond, rival["nivel"]) for n in FAMILIAS},
        "puntos": _vista_puntos(st),
    }


def _avanzar(st: dict, pf: int, pa: int, nivel_rival: float | None, local: bool, neutral: bool,
             fecha: str, temporada, escala_g: float, escala_margen: float,
             cuenta_nivel: bool = True, por_rival: bool = False, externo: bool = False,
             esperado: tuple | None = None):
    res = 1 if pf > pa else -1
    nr = NIVEL_RIVAL_FALLBACK if nivel_rival is None else nivel_rival
    mult = 1.0 if (local or neutral) else VISITA_MULT
    q = (abs(pf - pa) / escala_margen) * res * nr * mult
    k_antes = st["kPos"] + st["kNeg"]
    st["kPos"] = st["kPos"] + q if q > 0 else 0.0
    st["kNeg"] = st["kNeg"] + q if q < 0 else 0.0
    if not neutral:
        clave = "kLoc" if local else "kVis"
        st[clave] = st[clave] + q if _signo(st[clave]) in (0, res) else q
    k = st["kPos"] + st["kNeg"]
    s_antes, s = _signo(k_antes), _signo(k)
    if s_antes and s != s_antes:          # revienta: se cierra la burbuja con su rival
        st["reventones"][s_antes].append({"partidos": st["racha"], "kPico": st["kPico"], "nivelRival": nivel_rival})
        st["racha"], st["kPico"], st["conds"] = 0, 0.0, []
    st["racha"] += 1
    st["conds"].append(None if neutral else ("L" if local else "V"))
    st["kPico"] = max(st["kPico"], abs(k))
    # las familias separadas (como la K de goles: «anotás o no anotás»)
    for nombre, signo in FAMILIAS.items():
        f = st["fam"][nombre]
        if res == signo:
            f["k"] += abs(q)
            f["racha"] += 1
            f["kPico"] = max(f["kPico"], f["k"])
            f["conds"].append(None if neutral else ("L" if local else "V"))
        elif f["k"] > 0:                  # revienta A CERO
            f["reventones"].append({"partidos": f["racha"], "kPico": f["kPico"], "nivelRival": nivel_rival,
                                    "fecha": fecha})
            st["fam"][nombre] = _familia0() | {"reventones": f["reventones"]}
    # la K de puntos: contra la media de los 20 anteriores (sin este partido)
    m = _media_puntos(st)
    varas = []
    if m is not None:
        varas += [("anota", pf - m[0]), ("recibe", pa - m[1])]
    if esperado is not None:              # la vara de la casa: (puntos esperados a favor, en contra)
        varas += [("anotaCasa", pf - esperado[0]), ("recibeCasa", pa - esperado[1])]
    if varas:
        for n, exceso in varas:
            f = st["fam"][n]
            if exceso > 0:
                f["k"] += (exceso / escala_margen) * nr
                f["racha"] += 1
                f["kPico"] = max(f["kPico"], f["k"])
            elif f["k"] > 0:                 # revienta A CERO
                f["reventones"].append({"partidos": f["racha"], "kPico": f["kPico"], "nivelRival": nivel_rival,
                                        "fecha": fecha})
                st["fam"][n] = _familia0() | {"reventones": f["reventones"]}
    st["pts"].append((pf, pa))
    # el nivel solo con los partidos que CUENTAN (tenis: el cuadro principal, §4);
    # los demás mueven igual la K y las burbujas
    if cuenta_nivel:
        st["res"].append((pf, pa, nivel_rival))
    st["ultimo"] = (fecha, temporada)
    if len(st["res"]) >= VENTANA and not externo:   # con nivel externo, el nivel lo pone quien llama
        st["nivel"] = nivel_de(st["res"][-VENTANA:], escala_g, por_rival)


def construir(partidos: list[dict], escala_g: float = ESCALA_G, escala_margen: float = ESCALA_MARGEN,
              estado_final: dict | None = None, nivel_por_rival: bool = False,
              cuenta_nivel=None, nivel_externo: dict | None = None,
              nivel_final: dict | None = None, linea_puntos: dict | None = None) -> dict[int, dict]:
    """Una pasada cronológica por TODOS los partidos. Devuelve, por id de
    partido, lo que se sabía de cada lado ANTES de jugarlo:
    {id: {"local": {...}, "visita": {...}}}. `partidos` ordenados por fecha.
    Con `estado_final` (un dict), deja ahí el estado de cada equipo tras su
    último partido: lo que la guía mira para el PRÓXIMO.
    `nivel_por_rival` y `cuenta_nivel(partido) -> bool` son las variantes del
    nivel del tenis (docs/TENIS_FASE0.md §4); apagadas, el motor es el de siempre.
    `nivel_externo` = {id: {"local": x, "visita": y}}: el nivel de cada lado ANTES
    del partido viene de afuera (el Elo en la escala del SAD, §5) y reemplaza al
    de la ventana en todo: la q, el riesgo, los tercios. `nivel_final` = {equipo: x},
    el nivel después de su último partido (para la foto de hoy).
    `linea_puntos` = {id: (puntos esperados del local, de la visita)} según la
    casa: mueve las familias «anotaCasa» / «recibeCasa» (§10)."""
    estado: dict[int, dict] = {} if estado_final is None else estado_final
    out: dict[int, dict] = {}
    for p in partidos:
        L = estado.setdefault(p["localId"], _nuevo())
        V = estado.setdefault(p["visitaId"], _nuevo())
        neutral = bool(p.get("neutral"))
        if nivel_externo is not None:
            ext = nivel_externo.get(p["id"]) or {}
            L["nivel"], V["nivel"] = ext.get("local"), ext.get("visita")
        out[p["id"]] = {"local": _previo(L, V, True, neutral, p["fecha"], p["temporada"]),
                        "visita": _previo(V, L, False, neutral, p["fecha"], p["temporada"])}
        nl, nv = L["nivel"], V["nivel"]   # previos: no ven este partido
        cuenta = True if cuenta_nivel is None else bool(cuenta_nivel(p))
        ext = nivel_externo is not None
        lp = (linea_puntos or {}).get(p["id"])
        _avanzar(L, p["ptsLocal"], p["ptsVisita"], nv, True, neutral, p["fecha"], p["temporada"], escala_g, escala_margen,
                 cuenta, nivel_por_rival, ext, None if lp is None else (lp[0], lp[1]))
        _avanzar(V, p["ptsVisita"], p["ptsLocal"], nl, False, neutral, p["fecha"], p["temporada"], escala_g, escala_margen,
                 cuenta, nivel_por_rival, ext, None if lp is None else (lp[1], lp[0]))
    if nivel_final is not None:
        for t, x in nivel_final.items():
            if t in estado:
                estado[t]["nivel"] = x
    return out
