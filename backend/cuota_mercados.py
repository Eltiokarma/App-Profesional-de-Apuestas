"""Los mercados que el contrato entiende — UNA sola tabla para leer y para escribir.

`cuota_key(bet_name, value)` traduce el catálogo de API-Football a los mercados
del contrato (1x2, doble oportunidad, más/menos 2.5, ambos marcan, hándicap
±0.5) y devuelve None para todo lo demás: medios tiempos, córners, tarjetas,
prórroga, otras líneas de goles, marcador exacto…

Lo usan las pantallas al leer y —desde el 18/09/2026— la ingesta al ESCRIBIR:
`sad.db` llegó a 30 GB (190 millones de filas en odds_history, 62 en odds_live)
guardando decenas de mercados que ninguna pantalla mira, y Railway cobra esa
base como memoria cada vez que algo la lee. Lo que `cuota_key` no mapea no se
guarda. Sin efectos al importar: este módulo no toca la app ni arranca hilos.
"""

# El catálogo trae los MISMOS mercados en versión 1er/2º tiempo, córners,
# tarjetas o prórroga ("Goals Over/Under First Half", "Asian Handicap First
# Half"…): si se cuelan bajo la misma clave, la serie alterna partido
# completo / medio tiempo en cada captura y la gráfica zigzaguea. Aquí solo
# pasan mercados del partido completo.
_BETS_FUERA = ("half", "1st", "2nd", "first", "second", "corner", "card", "extra", "period", "halftime")


def cuota_key(bet_name, value):
    # el feed trae valores NUMÉRICOS en algunos mercados («Exact Goals
    # Number»: 0, 1, 2…). Con `(value or "").strip()` el primer int tumbaba
    # el extractor entero: del 18/09 al 11/10/2026 no entró ni una cuota
    # prepartido y cada corrida quemaba sus requests de /odds para nada.
    b = str(bet_name or "").lower()
    v = "" if value is None else str(value).strip()
    if any(t in b for t in _BETS_FUERA):
        return None
    # "fulltime result": nombre del 1X2 en el catálogo de /odds/live
    if "match winner" in b or "fulltime result" in b or b == "1x2":
        return {"Home": ("1x2", "1"), "Draw": ("1x2", "X"), "Away": ("1x2", "2"),
                "1": ("1x2", "1"), "X": ("1x2", "X"), "2": ("1x2", "2")}.get(v)
    if "double chance" in b:
        return {"Home/Draw": ("dc", "1X"), "Home/Away": ("dc", "12"), "Draw/Away": ("dc", "X2"),
                "1X": ("dc", "1X"), "12": ("dc", "12"), "X2": ("dc", "X2")}.get(v)
    if "over/under" in b or b == "goals over/under":
        return {"Over 2.5": ("ou", "O"), "Under 2.5": ("ou", "U")}.get(v)
    if "both teams" in b:
        return {"Yes": ("btts", "Y"), "No": ("btts", "N")}.get(v)
    if "asian handicap" in b:
        if v.startswith("Home -0.5"):
            return ("ah", "H1")
        if v.startswith("Away +0.5"):
            return ("ah", "H2")
    return None


# LA DOBLE OPORTUNIDAD TIENE QUE CUADRAR CON EL 1X2 DE LA MISMA CASA. El
# 21/10/2026 1xBet mandó en Villa–Viking 1X 2.60 · X2 1.32 · 12 1.01 con el
# local a 1.29 (el 16/10 la misma casa daba 1X 1.04): la media de /cuotas
# subió el 1X a 1.46 y tres partes leyeron «la doble oportunidad más cara que
# el resultado simple» (incidencia 68). La probabilidad de «1 o X» no puede
# ser menor que la de «1» ni mayor que la de «1» más la de «X»: se tolera el
# margen de la casa (TOLERANCIA_DC en probabilidad implícita).
_DC_PARTES = {"1X": ("1", "X"), "12": ("1", "2"), "X2": ("X", "2")}
TOLERANCIA_DC = 0.05
# …y por ABAJO la cuenta es la misma suma, no el mayor de los dos (incidencia
# 412, Brest–Nice 23/10/2026): 1xBet dio 1X 1.80 con su 1X2 en 2.31/3.50 (1X
# ≈ 1.39); quedaba entre «1» y «1 + X» y pasaba, y la media subía a 1.52. En
# las otras siete casas del mismo partido la DC cayó a ≤ 0.04 de la suma.
TOLERANCIA_DC_SUMA = 0.10


def dc_incoherente(seleccion: str, odd, x12: dict) -> bool:
    """True si la cuota de doble oportunidad `seleccion` (1X · 12 · X2) no
    cuadra con el 1X2 `x12` {"1", "X", "2": cuota} de la MISMA casa. Sin el
    1X2 completo de esa casa no se puede juzgar: False."""
    partes = _DC_PARTES.get(seleccion)
    if not partes or not odd:
        return False
    try:
        pa, pb, p = 1 / float(x12[partes[0]]), 1 / float(x12[partes[1]]), 1 / float(odd)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False
    return (p < max(pa, pb) - TOLERANCIA_DC or p < pa + pb - TOLERANCIA_DC_SUMA
            or p > pa + pb + TOLERANCIA_DC)


def sin_dc_incoherente(filas: list[dict]) -> list[dict]:
    """Saca de `filas` ({casa, mercado, seleccion, cuota}) la doble oportunidad
    que no cuadra con el 1X2 de su casa."""
    x12: dict[str, dict] = {}
    for f in filas:
        if f["mercado"] == "1x2":
            x12.setdefault(f["casa"], {})[f["seleccion"]] = f["cuota"]
    return [f for f in filas if not (f["mercado"] == "dc"
                                     and dc_incoherente(f["seleccion"], f["cuota"], x12.get(f["casa"], {})))]


# LOS MERCADOS DE DOS SALIDAS (ambos marcan, más/menos 2.5) TAMBIÉN TIENEN QUE
# CUADRAR (incidencia 717, 27/10/2026): en 1576182 cinco casas daban «ambos
# marcan» Sí 1.40-1.50 / No 2.50-2.63 y Marathonbet Sí 7.8 / No 1.04, otro
# mercado con el mismo nombre. La media subía el Sí a 2.5: en 2.355 partidos
# la suma implícita de la media quedaba bajo 1 en el 47 % (imposible con
# margen) y «ambos marcan sí» salía con un ROI de +25 % que era el artefacto.
# Una casa sale de ESE mercado si su par no suma lo que suma un par con margen
# o si su probabilidad sin margen se aparta de la mediana de las otras casas
# (con 3+ casas: con dos no se sabe cuál es la rara). El par de Marathonbet
# suma 1.09 —parece sano solo— y se va por el consenso (0.12 contra 0.64).
_DOS_SALIDAS = {"btts": ("Y", "N"), "ou": ("O", "U")}
SUMA_DOS_SALIDAS = (0.98, 1.25)
DESVIO_CONSENSO = 0.25


def casas_dos_salidas_incoherentes(filas: list[dict]) -> set[tuple[str, str]]:
    """Las (casa, mercado) de `filas` ({casa, mercado, seleccion, cuota}) cuyo
    par de dos salidas no cuadra. Un par incompleto no se juzga."""
    pares: dict[str, dict[str, dict[str, float]]] = {}
    for f in filas:
        if f["mercado"] in _DOS_SALIDAS:
            pares.setdefault(f["mercado"], {}).setdefault(f["casa"], {})[f["seleccion"]] = f["cuota"]
    fuera: set[tuple[str, str]] = set()
    for mercado, por_casa in pares.items():
        a, b = _DOS_SALIDAS[mercado]
        prob: dict[str, float] = {}
        for casa, sel in por_casa.items():
            try:
                pa, pb = 1 / float(sel[a]), 1 / float(sel[b])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not SUMA_DOS_SALIDAS[0] <= pa + pb <= SUMA_DOS_SALIDAS[1]:
                fuera.add((casa, mercado))
            else:
                prob[casa] = pa / (pa + pb)
        if len(prob) >= 3:
            for casa, p in prob.items():
                otras = sorted(v for c, v in prob.items() if c != casa)
                n = len(otras)
                med = otras[n // 2] if n % 2 else (otras[n // 2 - 1] + otras[n // 2]) / 2
                if abs(p - med) > DESVIO_CONSENSO:
                    fuera.add((casa, mercado))
    return fuera


def sin_incoherentes(filas: list[dict]) -> list[dict]:
    """`sin_dc_incoherente` y, además, sin las casas cuyo par de dos salidas
    (btts, ou) no cuadra: lo que entra a una media entre casas."""
    fuera = casas_dos_salidas_incoherentes(filas)
    return [f for f in sin_dc_incoherente(filas) if (f["casa"], f["mercado"]) not in fuera]


def es_del_contrato(bet_name, value) -> bool:
    """¿Esta fila de cuotas la lee alguna pantalla? Si no, no se guarda."""
    return cuota_key(bet_name, value) is not None
