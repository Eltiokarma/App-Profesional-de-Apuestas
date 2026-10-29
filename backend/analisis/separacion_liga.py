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


def es_desde_cuartos(ronda: str | None) -> bool:
    r = (ronda or "").strip().lower()
    return r == "final" or r.startswith("final") or any(x in r for x in _RONDA_CUARTOS)


def copa_en_agenda(liga_id: int | None, ronda: str | None, nombre: str) -> tuple[int, str] | None:
    """Prioridad de agenda de un partido de copa nacional medida; None si no es una."""
    if liga_id not in COPAS_MEDIDAS:
        return None
    auc = SEPARACION[liga_id][0]
    nivel = nivel_de(auc)
    pie = "; el 1X2 sale del mercado, no del motor (en copas la localía sale negativa)"
    if nivel == "alta":
        return 8, f"{nombre} · {ronda or 'copa'} (copa nacional: el riesgo separa alto, AUC {auc:.2f}; al final{pie})"
    if nivel == "media":
        if es_desde_cuartos(ronda):
            return 8, f"{nombre} · {ronda} (copa nacional desde cuartos: AUC {auc:.2f}; al final{pie})"
        return 0, (f"{nombre} · {ronda or 'ronda temprana'}: en esta copa el riesgo separa a medias "
                   f"(AUC {auc:.2f}) y entra solo desde cuartos")
    return 0, (f"{nombre}: el riesgo no separa en esta copa (AUC {auc:.2f}: los grandes la juegan con "
               "suplentes y la burbuja no es la del once que sale); no entra a la agenda")
