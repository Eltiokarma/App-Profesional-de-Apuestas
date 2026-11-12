"""CUÁNTO SEPARA EL RIESGO DEL REVENTÓN EN CADA LIGA (29/10/2026, usuario).

La fase 0 de ligas nuevas (`python -m backend.fase0_ligas` y
`backtest_burbuja --liga`, sin fuga) midió el AUC de los puntos del riesgo
liga por liga: cuánto revienta más una burbuja en riesgo alto que en bajo.
Salió una regla limpia: el AUC sube con el PESO DEL NIVEL de la liga en la μ
(`backtest_gap --por-liga`), r = 0,89 sobre 23 ligas. Donde hay jerarquía
(Eredivisie, Serie A, Grecia) una burbuja «fuera de lugar» dice algo; en las
ligas de paridad (Argentina, Colombia, las segundas de Europa) las rachas se
cortan casi al azar y el riesgo «bajo» ya revienta la mitad de las veces.

Esto NO mueve ningún punto ni ningún corte del riesgo (son los calibrados con
el backtest del padrón): viaja en `/burbujas` como `separacionLiga` para que
quien escribe el parte sepa cuánto pesar la guía en esa liga. Es una medición
fechada: con cada backtest nuevo se rehace la tabla.
"""
from __future__ import annotations

import re

MEDIDO_EN = "2026-10-29"
# liga → (AUC de los puntos, observaciones). backtest_burbuja --liga, horizonte 1.
SEPARACION = {
    88: (0.679, 5818),    # Países Bajos · Eredivisie
    135: (0.676, 6684),   # Italia · Serie A
    197: (0.669, 4136),   # Grecia · Super League 1
    344: (0.656, 2269),   # Bolivia · Primera División
    282: (0.649, 2839),   # Perú · Liga 2
    39: (0.648, 7032),    # Inglaterra · Premier League
    140: (0.648, 6789),   # España · LaLiga
    78: (0.644, 5616),    # Alemania · Bundesliga
    61: (0.641, 6154),    # Francia · Ligue 1
    203: (0.632, 6246),   # Turquía · Süper Lig
    262: (0.627, 6090),   # México · Liga MX
    281: (0.626, 6860),   # Perú · Liga 1
    242: (0.622, 5712),   # Ecuador · Liga Pro
    848: (0.609, 5326),   # UEFA Conference League
    3: (0.593, 3855),     # UEFA Europa League
    136: (0.593, 6229),   # Italia · Serie B
    71: (0.590, 7417),    # Brasil · Serie A
    79: (0.590, 5463),    # Alemania · 2. Bundesliga
    239: (0.581, 7586),   # Colombia · Primera A
    40: (0.578, 10052),   # Inglaterra · Championship
    128: (0.577, 8037),   # Argentina · Liga Profesional
    62: (0.575, 6018),    # Francia · Ligue 2
    141: (0.572, 7969),   # España · Segunda División
    # COPAS NACIONALES (29/10/2026, misma medición): donde un grande cruza con
    # uno de tercera o cuarta el riesgo separa MÁS que en cualquier liga —la
    # diferencia de nivel es enorme y se lee fácil—; la EFL Cup no, porque los
    # grandes la juegan con suplentes y la burbuja no es la del once que sale.
    96: (0.746, 1203),    # Portugal · Taça de Portugal
    66: (0.736, 1184),    # Francia · Coupe de France
    143: (0.727, 1215),   # España · Copa del Rey
    81: (0.652, 1042),    # Alemania · DFB Pokal
    45: (0.611, 3776),    # Inglaterra · FA Cup
    137: (0.601, 744),    # Italia · Coppa Italia
    48: (0.555, 1310),    # Inglaterra · EFL Cup
}
COPAS_MEDIDAS = {96, 66, 143, 81, 45, 137, 48}

# SELECCIONES (12/11/2026, REVENTON §16.2). Medido con la historia que la base
# ya tenía (el Mundial, las eliminatorias de cinco confederaciones, la Euro 2024
# y los amistosos, 2020-2026) bajada de la API con el token de Cowork y pasada
# por `backtest_burbuja.observar_equipo` (horizonte 1, sin fuga): 1.845 burbujas
# evaluadas en torneos de selecciones, de 143 selecciones absolutas, riesgo bajo
# 32 % → muy alto 77 %, AUC 0,697, monótona y estable en los cuatro tramos de
# tiempo (0,66-0,78). Separa más
# donde la jerarquía es enorme (eliminatorias de la UEFA: Inglaterra contra
# Andorra) y menos entre pares (el Mundial). La Liga de las Naciones no estaba en
# la base: hasta que se mida va con la de todas las selecciones.
MEDIDO_SELECCIONES = "2026-11-12"
SEPARACION_SELECCIONES = {
    32: (0.743, 236),     # Mundial · eliminatorias UEFA
    30: (0.742, 188),     # Mundial · eliminatorias AFC
    29: (0.718, 131),     # Mundial · eliminatorias CAF
    34: (0.697, 348),     # Mundial · eliminatorias CONMEBOL
    10: (0.685, 602),     # amistosos de selecciones
    1: (0.647, 277),      # Copa del Mundo 2026
}
SELECCIONES_TODAS = (0.697, 1845)


def _es_de_selecciones(liga_id: int | None) -> bool:
    if not liga_id:
        return False
    from backend.analisis.escala import torneos_selecciones
    return liga_id in torneos_selecciones()


def de_selecciones(liga_id: int, nombre: str | None = None) -> dict:
    """La separación de un torneo de selecciones: la suya si está medida, si no
    la de todas las selecciones (con la nota que lo dice)."""
    liga = nombre or f"liga {liga_id}"
    propia = SEPARACION_SELECCIONES.get(liga_id)
    auc, n = propia or SELECCIONES_TODAS
    nivel = nivel_de(auc)
    if propia:
        nota = (f"en {liga} el riesgo del reventón separa {'bien' if nivel == 'alta' else 'a medias'} "
                f"(AUC {auc:.2f}, {n} burbujas): entre selecciones la jerarquía se lee; la guía pesa "
                "en la lectura. Que se lea fácil no quiere decir que pague: la casa también la ve")
    else:
        nota = (f"{liga} sin medir por sí sola (no estaba en la base): va la separación de TODAS las "
                f"selecciones (AUC {auc:.2f}, {n} burbujas, alta). Entre pares separa menos —el Mundial, "
                "0,65—, y la Liga de las Naciones agrupa por nivel: pesá la guía con esa cautela")
    return {"ligaId": liga_id, "liga": nombre, "auc": auc, "n": n, "nivel": nivel, "competicion": "liga",
            "medidoEn": MEDIDO_SELECCIONES, "nota": nota}
# las copas entran a la agenda según cuánto separa el riesgo en ellas (decisión
# del usuario, 29/10/2026): alta → siempre, al final · media → desde cuartos ·
# baja → nunca. El 1X2 de un partido de copa sale del MERCADO y de los skills,
# no del motor: en las copas la localía sale negativa (el chico juega en casa).
_RONDA_CUARTOS = ("quarter", "semi", "cuartos")
CORTE_ALTA = 0.64     # separa como las grandes ligas
CORTE_MEDIA = 0.60    # por debajo, liga de paridad


def nivel_de(auc: float | None) -> str:
    if auc is None:
        return "sin medir"
    return "alta" if auc >= CORTE_ALTA else ("media" if auc >= CORTE_MEDIA else "baja")


def de_liga(liga_id: int | None, nombre: str | None = None) -> dict:
    """Lo que viaja en `/burbujas.separacionLiga` para la liga doméstica del equipo."""
    if _es_de_selecciones(liga_id):
        return de_selecciones(liga_id, nombre)
    auc, n = SEPARACION.get(liga_id, (None, None)) if liga_id else (None, None)
    nivel = nivel_de(auc)
    liga = nombre or (f"liga {liga_id}" if liga_id else "su liga")
    if liga_id in COPAS_MEDIDAS:
        # el próximo partido es de COPA: manda cuánto separa el riesgo en esa copa
        nota = (f"el próximo partido es de {liga}: en esta copa el riesgo separa "
                f"{'alto' if nivel == 'alta' else 'a medias' if nivel == 'media' else 'poco'} (AUC {auc:.2f}). "
                "El nivel del rival puede venir de otra categoría (ver `escala`) y el 1X2 sale del "
                "mercado, no del motor: en las copas la localía sale negativa")
        return {"ligaId": liga_id, "liga": nombre, "auc": auc, "n": n, "nivel": nivel, "competicion": "copa",
                "medidoEn": MEDIDO_EN, "nota": nota}
    if nivel == "alta":
        nota = (f"en {liga} el riesgo del reventón separa bien (AUC {auc:.2f}): liga con jerarquía, "
                "una burbuja fuera de lugar dice algo; la guía pesa en la lectura")
    elif nivel == "media":
        nota = (f"en {liga} el riesgo separa (AUC {auc:.2f}), algo menos que en las grandes ligas; "
                "la guía pesa, con la confianza de su tarjeta")
    elif nivel == "baja":
        nota = (f"en {liga} el riesgo separa poco (AUC {auc:.2f}): liga de paridad, las rachas se cortan "
                "casi al azar y el riesgo «bajo» ya revienta la mitad de las veces. La guía pesa MENOS en "
                "la lectura; sus puntos no cambian")
    else:
        nota = (f"{liga}: sin medir liga por liga; la guía es la calibrada sobre el padrón")
    return {"ligaId": liga_id, "liga": nombre, "auc": auc, "n": n, "nivel": nivel, "competicion": "liga",
            "medidoEn": MEDIDO_EN if auc is not None else None, "nota": nota}


def del_partido(base_id: int | None, base_nombre: str | None,
                liga_px: int | None, liga_px_nombre: str | None = None) -> dict:
    """La separación que va con el PRÓXIMO partido: la de su competición si está
    medida (copa medida o liga del padrón medida), si no la de la liga
    doméstica del equipo. Incidencia 869: Elversberg, ascendido, salía con la
    «baja» de la 2. Bundesliga (su base del último año) en un partido de
    Bundesliga (alta)."""
    if liga_px and liga_px != base_id and (liga_px in COPAS_MEDIDAS or liga_px in SEPARACION
                                            or _es_de_selecciones(liga_px)):
        # una selección juega cada torneo con otra escala (la Liga de las
        # Naciones entre pares, las eliminatorias contra Andorra): manda el del partido
        return de_liga(liga_px, liga_px_nombre)
    return de_liga(base_id, base_nombre)


_RONDA_1_N = re.compile(r"\b1\s*/\s*(\d+)\s*-?\s*finals?\b")


def equipos_de_ronda(ronda: str | None) -> int | None:
    """«1/8-finals» = octavos = ronda de 16; «1/128-finals» = ronda de 256. La
    API nombra así las rondas de algunas copas (Coupe de France, 04/11/2026,
    incidencia 1200): el texto CONTIENE «final» y no es la final."""
    m = _RONDA_1_N.search((ronda or "").strip().lower())
    return 2 * int(m.group(1)) if m else None


def _es_la_final(r: str) -> bool:
    return equipos_de_ronda(r) is None and (r == "final" or r.startswith("final"))


def es_desde_cuartos(ronda: str | None) -> bool:
    r = (ronda or "").strip().lower()
    n = equipos_de_ronda(r)
    if n is not None:
        return n <= 8
    return _es_la_final(r) or any(x in r for x in _RONDA_CUARTOS)


def entra_desde(ronda: str | None, rondas: tuple, equipos_max: int) -> bool:
    """¿La ronda entra a la agenda de una copa con `DESDE_RONDA`? La «1/N-finals»
    se lee por su número (entra con 2N ≤ `equipos_max`), la final por nombre
    entero y el resto por las palabras de la lista (sin «final», que casaba con
    «1/128-finals»: Sporting Baie-Mahault–Siroco, Guadalupe, 1200)."""
    r = (ronda or "").strip().lower()
    n = equipos_de_ronda(r)
    if n is not None:
        return n <= equipos_max
    return _es_la_final(r) or any(x in r for x in rondas if x != "final")


# Copas que traen rondas de equipos amateurs y de ultramar sin datos: entran
# desde la ronda indicada (01/11/2026, incidencia 990, decisión del usuario: la
# Coupe de France metía a la agenda el 7.º tour de Martinica, Franciscain–Aiglon,
# sin plantilla, cuotas, once ni historia).
DESDE_RONDA = {66: ("round of 64", "round of 32", "round of 16", "quarter", "semi", "final")}
DESDE_RONDA_EQUIPOS = {66: 64}   # la misma regla para la ronda escrita «1/N-finals» (1200)


def copa_en_agenda(liga_id: int | None, ronda: str | None, nombre: str) -> tuple[int, str] | None:
    """Prioridad de agenda de un partido de copa nacional medida; None si no es una."""
    if liga_id not in COPAS_MEDIDAS:
        return None
    auc = SEPARACION[liga_id][0]
    nivel = nivel_de(auc)
    pie = "; el 1X2 sale del mercado, no del motor (en copas la localía sale negativa)"
    rondas = DESDE_RONDA.get(liga_id)
    if rondas and not entra_desde(ronda, rondas, DESDE_RONDA_EQUIPOS.get(liga_id, 64)):
        return 0, (f"{nombre} · {ronda or 'ronda temprana'}: esta copa entra desde la ronda de 64 (las "
                   "anteriores son de amateurs y de ultramar, sin datos)")
    if nivel == "alta":
        return 8, f"{nombre} · {ronda or 'copa'} (copa nacional: el riesgo separa alto, AUC {auc:.2f}; al final{pie})"
    if nivel == "media":
        if es_desde_cuartos(ronda):
            return 8, f"{nombre} · {ronda} (copa nacional desde cuartos: AUC {auc:.2f}; al final{pie})"
        return 0, (f"{nombre} · {ronda or 'ronda temprana'}: en esta copa el riesgo separa a medias "
                   f"(AUC {auc:.2f}) y entra solo desde cuartos")
    return 0, (f"{nombre}: el riesgo no separa en esta copa (AUC {auc:.2f}: los grandes la juegan con "
               "suplentes y la burbuja no es la del once que sale); no entra a la agenda")
