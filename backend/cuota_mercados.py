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


def cuota_key(bet_name: str, value: str):
    b = (bet_name or "").lower()
    v = (value or "").strip()
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


def es_del_contrato(bet_name, value) -> bool:
    """¿Esta fila de cuotas la lee alguna pantalla? Si no, no se guarda."""
    return cuota_key(bet_name, value) is not None
