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


def nivel_de(ventana: list[tuple[int, int]], escala_g: float = ESCALA_G) -> float:
    """`ventana`: los últimos 20 (pf, pa) en orden. Nivel = P + G + 1."""
    p = 3 * sum(1 for pf, pa in ventana if pf > pa) / VENTANA
    u5 = ventana[-ULTIMOS:]
    dg = sum(pf - pa for pf, pa in u5)
    tg = sum(pf + pa for pf, pa in u5)
    g = 0.0 if tg == 0 else dg / tg
    return p + escala_g * g + 1


def _nuevo() -> dict:
    return {"res": [], "kPos": 0.0, "kNeg": 0.0, "kLoc": 0.0, "kVis": 0.0,
            "racha": 0, "kPico": 0.0, "reventones": {1: [], -1: []}, "ultimo": None, "nivel": None}


def _signo(v: float) -> int:
    return 1 if v > 0 else -1 if v < 0 else 0


def _previo(st: dict, rival: dict, local: bool, neutral: bool, fecha: str, temporada) -> dict:
    """Lo que se sabe del equipo ANTES del partido (nada de este partido)."""
    k = st["kPos"] + st["kNeg"]
    s = _signo(k)
    rev = st["reventones"].get(s, []) if s else []
    desc = None
    if st["ultimo"] is not None:
        desc = DESCANSO_TOPE if st["ultimo"][1] != temporada else dias_descanso(st["ultimo"][0], fecha)
    med_part = median(r["partidos"] for r in rev) if rev else None
    med_pico = median(r["kPico"] for r in rev) if rev else None
    med_niv = median(r["nivelRival"] for r in rev if r["nivelRival"] is not None) if any(
        r["nivelRival"] is not None for r in rev) else None
    return {
        "nivel": st["nivel"], "nivelRival": rival["nivel"], "partidosPrevios": len(st["res"]),
        "k": k, "kCond": (st["kLoc"] if local else st["kVis"]) if not neutral else 0.0,
        "signo": s, "racha": st["racha"], "kPico": st["kPico"],
        "descanso": None if desc is None else max(0, min(DESCANSO_TOPE, desc)),
        "reventonesSigno": len(rev), "medianaPartidos": med_part, "medianaKPico": med_pico,
        "medianaNivelRival": med_niv,
    }


def _avanzar(st: dict, pf: int, pa: int, nivel_rival: float | None, local: bool, neutral: bool,
             fecha: str, temporada, escala_g: float, escala_margen: float):
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
        st["racha"], st["kPico"] = 0, 0.0
    st["racha"] += 1
    st["kPico"] = max(st["kPico"], abs(k))
    st["res"].append((pf, pa))
    st["ultimo"] = (fecha, temporada)
    if len(st["res"]) >= VENTANA:
        st["nivel"] = nivel_de(st["res"][-VENTANA:], escala_g)


def construir(partidos: list[dict], escala_g: float = ESCALA_G, escala_margen: float = ESCALA_MARGEN) -> dict[int, dict]:
    """Una pasada cronológica por TODOS los partidos. Devuelve, por id de
    partido, lo que se sabía de cada lado ANTES de jugarlo:
    {id: {"local": {...}, "visita": {...}}}. `partidos` ordenados por fecha."""
    estado: dict[int, dict] = {}
    out: dict[int, dict] = {}
    for p in partidos:
        L = estado.setdefault(p["localId"], _nuevo())
        V = estado.setdefault(p["visitaId"], _nuevo())
        neutral = bool(p.get("neutral"))
        out[p["id"]] = {"local": _previo(L, V, True, neutral, p["fecha"], p["temporada"]),
                        "visita": _previo(V, L, False, neutral, p["fecha"], p["temporada"])}
        nl, nv = L["nivel"], V["nivel"]   # previos: no ven este partido
        _avanzar(L, p["ptsLocal"], p["ptsVisita"], nv, True, neutral, p["fecha"], p["temporada"], escala_g, escala_margen)
        _avanzar(V, p["ptsVisita"], p["ptsLocal"], nl, False, neutral, p["fecha"], p["temporada"], escala_g, escala_margen)
    return out
