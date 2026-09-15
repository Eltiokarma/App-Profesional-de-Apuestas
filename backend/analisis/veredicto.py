"""El veredicto del parte — lo objetivo se calcula, el juicio lo escribe Cowork.

Fase B de docs/APRENDIZAJE.md. Doce horas después del partido, alguien tiene
que decir si el pronóstico acertó. La mitad de esa respuesta ya está en
nuestra base y no hace falta preguntársela a nadie:

  lo calcula este módulo          lo escribe Cowork
  ─────────────────────────────   ─────────────────────────────
  marcador final y ganador        por qué falló
  ¿acertó el 1X2 declarado?       qué mecanismo no vio
  ¿acertó el marcador exacto?     la lección, en una frase
  Brier del caso                  a qué skill le toca
  ¿cayó gol en la ventana del TDE? si el caso es ciego o está contaminado
  la evidencia (goles con minuto)  si el falsador se cumplió

La última línea es la frontera honesta del módulo. El falsador es prosa —"si
el visitante abre el marcador antes del 20'"— y verificar prosa arbitraria no
es algo que este código pueda hacer bien. Lo que sí hace es servir la
evidencia con la que se comprueba (los goles con su minuto y su lado) y dejar
que Cowork declare el resultado. Un verificador que acierte el 80% de las
veces sería peor que no tenerlo: nadie sabría de cuál 20% desconfiar.

La regla que ordena todo lo demás está en docs/APRENDIZAJE.md: los casos
contaminados fijan rúbrica pero NO acreditan. Este módulo no decide la
población —eso lo declara quien escribe el veredicto— pero la guarda con el
caso para que nadie pueda contar una tasa de acierto mezclada sin verlo.
"""
import re

from backend import db as saddb

# el resultado se liquida a los 90' (misma regla que el resto del backend)
_G90_LOCAL = "COALESCE(f.fulltime_home, f.goals_home)"
_G90_VISITA = "COALESCE(f.fulltime_away, f.goals_away)"

# el mismo padrón de estados terminados que usa el resto del backend
FIN_SHORT = {"FT", "AET", "PEN", "AWD", "WO"}
SELECCIONES = ("ciega", "por_resultado", "post_resultado")
MODOS = ("PRE", "COND")
VEREDICTOS = ("acierto", "parcial", "fallo")
# solo esta combinación acredita validación predictiva (CALIBRACION.md del TDE
# y el registro de la cadena del DTP dicen lo mismo con otras palabras)
def acredita(seleccion: str, modo: str) -> bool:
    return seleccion == "ciega" and modo == "PRE"


def _fixture(fixture_id: int):
    return saddb.query_one(
        "sad",
        f"SELECT f.id, f.date, f.status_short, f.status_long, "
        f"{_G90_LOCAL} AS g_local, {_G90_VISITA} AS g_visita, "
        "f.home_team_id, f.away_team_id, ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
        "JOIN teams at ON at.id=f.away_team_id WHERE f.id=?",
        (fixture_id,),
    )


def _goles(fixture_id: int, home_id: int) -> list[dict]:
    """Goles con minuto y lado. El autogol cuenta para el rival del que lo hizo.

    Si la ficha del partido no se capturó, la lista sale vacía: el marcador
    sigue siendo bueno (viene del fixture) pero la ventana del TDE no se puede
    comprobar, y eso se dice en vez de darse por comprobada.
    """
    try:
        filas = saddb.query(
            "sad",
            "SELECT minuto, extra, detalle, equipo_id, jugador FROM fixture_eventos "
            "WHERE fixture_id=? AND tipo='Goal' ORDER BY minuto, id",
            (fixture_id,),
        )
    except Exception:
        return []  # DB anterior a la migración de eventos
    out = []
    for f in filas:
        autogol = "own" in (f["detalle"] or "").lower()
        de_local = (f["equipo_id"] == home_id) != autogol
        # `minuto` ya trae sumado el añadido (ficha_partido.guardar_eventos:
        # 90+4 se guarda como minuto 94, extra 4). Sumarlo otra vez ponía ese
        # gol en el 98 y lo sacaba de la ventana 75-90 en la que cayó.
        out.append({
            "minuto": f["minuto"] or 0,
            "lado": "a" if de_local else "b",
            "jugador": f["jugador"] or "",
            "autogol": autogol,
        })
    return out


def _brier(reparto: dict, real: str) -> float | None:
    """Brier de tres resultados: Σ(pᵢ − oᵢ)². 0 es perfecto, 2 es el máximo.

    OJO con compararlo contra el objetivo del TDE (< 0.20): ese es un Brier
    BINARIO y este es de tres categorías. No están en la misma escala y
    ponerlos en la misma tabla sería un error de lectura, no de cálculo.
    """
    claves = ("local", "empate", "visita")
    total = sum(float(reparto.get(k) or 0) for k in claves)
    if total <= 0:
        return None
    return round(sum((float(reparto.get(k) or 0) / total - (1.0 if k == real else 0.0)) ** 2
                     for k in claves), 4)


def _ventana(texto: str) -> tuple[int, int] | None:
    """"75-90'" → (75, 90). Sin dos números no hay ventana que comprobar."""
    m = re.search(r"(\d{1,3})\s*[-–a]+\s*(\d{1,3})", texto or "")
    if not m:
        return None
    desde, hasta = int(m.group(1)), int(m.group(2))
    return (desde, hasta) if desde <= hasta else (hasta, desde)


def objetivo(fixture_id: int, parte: dict) -> dict:
    """Todo lo que la base puede responder sola sobre cómo salió el pronóstico."""
    fx = _fixture(fixture_id)
    if not fx:
        return {"jugado": False, "motivo": f"el fixture {fixture_id} no está en nuestra base"}
    gl, gv = fx["g_local"], fx["g_visita"]
    if gl is None or gv is None:
        return {"jugado": False, "motivo": "el partido todavía no tiene marcador en nuestra base"}

    real = "local" if gl > gv else ("visita" if gv > gl else "empate")
    pron = parte.get("pronostico") or {}
    reparto = pron.get("probabilidades") or {}
    # el 1X2 declarado es la selección con más probabilidad; un empate técnico
    # entre dos no se desempata a ojo: se declara y no cuenta como acierto
    ordenadas = sorted(("local", "empate", "visita"),
                       key=lambda k: float(reparto.get(k) or 0), reverse=True)
    top = float(reparto.get(ordenadas[0]) or 0)
    empatadas = [k for k in ordenadas if float(reparto.get(k) or 0) == top]
    declarado = ordenadas[0] if (top > 0 and len(empatadas) == 1) else ""

    goles = _goles(fixture_id, fx["home_team_id"])
    marcador_texto = f"{gl}-{gv}"
    exacto = (pron.get("marcador") or "").strip().replace(" ", "")

    out = {
        "jugado": True,
        "marcador": {
            "local": gl, "visitante": gv, "texto": marcador_texto,
            "ganador": "a" if real == "local" else ("b" if real == "visita" else "empate"),
            # un marcador de un partido en curso NO es un resultado: se sirve
            # igual (para eso existe el modo COND) pero se dice cuál es
            "terminado": (fx["status_short"] or "") in FIN_SHORT,
        },
        "unXDos": {
            "declarado": declarado, "real": real,
            "acerto": bool(declarado) and declarado == real,
            "probabilidadDeclarada": top if declarado else 0.0,
            "reparto": {k: float(reparto.get(k) or 0) for k in ("local", "empate", "visita")},
            "nota": ("" if declarado else
                     "sin 1X2 declarado (o con dos selecciones empatadas): no se cuenta acierto"),
        },
        "marcadorExacto": {"declarado": exacto, "real": marcador_texto,
                           "acerto": bool(exacto) and exacto == marcador_texto},
        "brier": {"valor": _brier(reparto, real),
                  "escala": "0 perfecto · 2 máximo · tres resultados (NO comparable con un Brier binario)"},
        "evidencia": {
            "goles": goles,
            "primerGol": goles[0] if goles else None,
            "conFicha": bool(goles) or (gl + gv == 0),
            "nota": ("" if goles or gl + gv == 0 else
                     "el partido tuvo goles pero la ficha no está capturada: "
                     "corre `python -m backend.ingesta.ficha_partido` si quieres comprobar minutos"),
        },
    }

    # ── la ventana del TDE: esto SÍ se comprueba ────────────────────────────
    # UNA COMPROBACIÓN POR BLOQUE. El índice es por equipo: si el parte declaró
    # los dos, son dos ventanas y dos veredictos. Antes solo se miraba uno y el
    # otro no existía para ninguna métrica.
    from backend.analisis.parte import bloques_tde
    bloques = []
    for tde in bloques_tde(parte.get("tde") or {}):
        rango = _ventana(tde.get("ventana") or "")
        if not rango:
            bloques.append({"ventana": tde.get("ventana", ""), "equipo": tde.get("equipo") or "",
                            "comprobable": False, "golEnVentana": None,
                            "nota": "la ventana declarada no trae dos minutos: no hay nada que comprobar"})
            continue
        desde, hasta = rango
        foco = tde.get("equipo") or ""
        # la echada del equipo foco se observa en los goles que RECIBE
        contra = "b" if foco == "a" else ("a" if foco == "b" else "")
        en_ventana = [g for g in goles if desde <= g["minuto"] <= hasta
                      and (not contra or g["lado"] == contra)]
        bloques.append({
            "ventana": tde.get("ventana"), "desde": desde, "hasta": hasta,
            "equipo": foco,
            "comprobable": out["evidencia"]["conFicha"],
            "golEnVentana": bool(en_ventana) if out["evidencia"]["conFicha"] else None,
            "goles": en_ventana,
            "nota": ("" if out["evidencia"]["conFicha"] else
                     "sin ficha de eventos no se puede comprobar la ventana: queda sin veredicto"),
        })
    if bloques:
        out["tde"] = {"bloques": bloques}
    return out
