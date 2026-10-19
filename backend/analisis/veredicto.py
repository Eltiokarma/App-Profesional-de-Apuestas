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
  ¿reventó la burbuja de cada lado? si el falsador se cumplió
  la evidencia (goles con minuto)

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
    """Goles con minuto y lado.

    En API-Football el `team` de un autogol es el equipo BENEFICIADO, no el del
    jugador (Libertad–Guaraní 2-2 del 11/10/2026 sumaba 3-1 al invertirlo), así
    que el lado sale del equipo del evento tal cual, como en `dtp_cowork`. Un
    penal errado viaja como `Goal` / `Missed Penalty` y no es gol.

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
        detalle = (f["detalle"] or "").lower()
        if "missed" in detalle:
            continue
        autogol = "own" in detalle
        de_local = f["equipo_id"] == home_id
        # `minuto` ya trae sumado el añadido (ficha_partido.guardar_eventos:
        # 90+4 se guarda como minuto 94, extra 4). Sumarlo otra vez ponía ese
        # gol en el 98 y lo sacaba de la ventana 75-90 en la que cayó.
        out.append({
            "minuto": f["minuto"] or 0,
            "lado": "a" if de_local else "b",
            "jugador": f["jugador"] or "",
            "autogol": autogol,
            # EL AÑADIDO NO TIENE VENTANA (disciplina 23 del TDE): las seis
            # ventanas de 15' terminan en el 45 y en el 90. Un 45+2 guardado
            # como 47 caía en la 45-60 (Westerlo–Antwerp, Pumas–Cruz Azul).
            "enAnadido": bool(f["extra"]),
            # 45 o 90: el tiempo al que se sumó el añadido (45+4 → minuto 49,
            # extra 4 → base 45). Sirve para no listarlo en ventanas lejanas
            "baseAnadido": ((f["minuto"] or 0) - (f["extra"] or 0)) if f["extra"] else None,
        })
    return out


def _rojas(fixture_id: int, home_id: int) -> list[dict]:
    """Expulsiones de JUGADORES con minuto y lado. Una roja reordena el partido
    entero (disciplina 16 del TDE): un gol en la ventana que llega después ya
    no comprueba el mecanismo declarado (disciplina 24). La roja a un
    entrenador también viaja como `Card` y no reordena nada: sin jugador_id no
    se cuenta."""
    try:
        filas = saddb.query(
            "sad",
            "SELECT minuto, detalle, equipo_id, jugador, jugador_id FROM fixture_eventos "
            "WHERE fixture_id=? AND tipo='Card' ORDER BY minuto, id",
            (fixture_id,),
        )
    except Exception:
        return []
    out = []
    for f in filas:
        detalle = (f["detalle"] or "").lower()
        if "red" not in detalle and "second yellow" not in detalle:
            continue
        if not f["jugador_id"]:
            continue
        out.append({"minuto": f["minuto"] or 0, "lado": "a" if f["equipo_id"] == home_id else "b",
                    "jugador": f["jugador"] or ""})
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


# UNA VENTANA RELATIVA AL GOL NO SON MINUTOS DEL RELOJ. «15-30' desde la
# ventaja» se leía como 15-30 y Feyenoord–Como daba por buena la ventana con
# el gol del 18' (veredictos del 17/10/2026; Sarmiento–River igual).
_RELATIVA = re.compile(r"desde (la|el|que)|tras (el|la)|despu[eé]s de|luego de|del gol|de la ventaja|"
                       r"relativ|\+\s*\d+\s*(min|')|post[- ]gol", re.I)


def clase_ventana(goles: list[dict], desde: int, contra: str) -> tuple[str, int, int]:
    """(clase, goles recibidos por el foco, diferencia) ANTES de la ventana.
    `roto`: el foco ya recibió 3 (disciplina 3); `rama_abandonada`: el
    marcador ya estaba 3 arriba (disciplina 24); "" si la ventana se juega."""
    previos = [g for g in goles
               if (not g.get("enAnadido") and g["minuto"] < desde)
               or (g.get("enAnadido") and (g.get("baseAnadido") or 0) < desde)]
    recibidos = sum(1 for g in previos if contra and g["lado"] == contra)
    dif = abs(sum(1 for g in previos if g["lado"] == "a") - sum(1 for g in previos if g["lado"] == "b"))
    return ("roto" if recibidos >= 3 else "rama_abandonada" if dif >= 3 else ""), recibidos, dif


def ventana_relativa(texto: str) -> bool:
    return bool(_RELATIVA.search(texto or ""))


def _ventana(texto: str) -> tuple[int, int] | None:
    """"75-90'" → (75, 90). Sin dos números, o relativa a un gol, no hay
    ventana de reloj que comprobar."""
    if ventana_relativa(texto):
        return None
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
    rojas = _rojas(fixture_id, fx["home_team_id"])
    bloques = []
    for tde in bloques_tde(parte.get("tde") or {}):
        reasig = rama_jugada(tde, goles, gl + gv, out["evidencia"]["conFicha"])
        # LA VENTANA DE LA RAMA QUE SE JUGÓ, si la declaró (disciplina 44)
        texto_v = tde.get("ventana") or ""
        de_rama = ((reasig or {}).get("loDeclarado") or {}).get("ventana") or ""
        if de_rama:
            texto_v = de_rama
        rango = _ventana(texto_v)
        if not rango:
            rel = ventana_relativa(texto_v)
            bloques.append({"ventana": texto_v, "equipo": tde.get("equipo") or "",
                            "comprobable": False, "golEnVentana": None, "reasignacion": reasig,
                            "ventanaDeRama": bool(de_rama),
                            "nota": ("la ventana es relativa a un gol, no al reloj: no se cobra en minutos; "
                                     "se juzga en la autopsia" if rel else
                                     "la ventana declarada no trae dos minutos: no hay nada que comprobar")})
            continue
        desde, hasta = rango
        foco = tde.get("equipo") or ""
        # la echada del equipo foco se observa en los goles que RECIBE
        contra = "b" if foco == "a" else ("a" if foco == "b" else "")
        en_ventana = [g for g in goles if desde <= g["minuto"] <= hasta and not g.get("enAnadido")
                      and (not contra or g["lado"] == contra)]
        # el añadido se anota aparte, y solo en la ventana que cierra ESE tiempo
        # (la que termina en el 45 o en el 90): un 45+4 aparecía también en la
        # 60-75 (Chankas–ADT, 17/10/2026)
        en_anadido = [g for g in goles if g.get("enAnadido") and (not contra or g["lado"] == contra)
                      and (g.get("baseAnadido") is None or g["baseAnadido"] == hasta)]
        # UN GOL EN LA VENTANA DESPUÉS DE UNA ROJA NO COMPRUEBA EL MECANISMO
        # (disciplinas 16 y 24): Liverpool 0-3 City, Pumas 3-3 Cruz Azul y
        # América 1-2 Medellín se contaban como acierto de ventana con goles
        # que llegaron con un hombre menos. Se sigue diciendo que hubo gol en la
        # ventana, pero no se cobra.
        primera = min((g["minuto"] for g in en_ventana), default=None)
        # SIN GOL TAMBIÉN: una roja antes de que termine la ventana reordena el
        # partido (disciplinas 16 y 17) y el «no hubo gol» deja de ser un
        # acierto limpio. ABB (roja al 45+3) y Mirassol (roja al 14') se
        # cobraban como ventana sin gol (17/10/2026).
        corte = primera if primera is not None else hasta
        rojas_antes = [r for r in rojas if r["minuto"] < corte]
        # ROTO O RESUELTO ANTES DE LA VENTANA (disciplinas 3 y 24): el equipo
        # que ya recibió 3 no está echado, está roto; un marcador 3 arriba
        # antes de la ventana abandona la rama. City–PSG, LASK–Liverpool y
        # Villa–Fenerbahçe se cobraban igual (17/10/2026).
        clase, recibidos, dif = clase_ventana(goles, desde, contra)
        cobrable = None if not out["evidencia"]["conFicha"] else (not rojas_antes and not clase)
        bloques.append({
            "ventana": tde.get("ventana"), "desde": desde, "hasta": hasta,
            "equipo": foco,
            "comprobable": out["evidencia"]["conFicha"],
            "golEnVentana": bool(en_ventana) if out["evidencia"]["conFicha"] else None,
            "goles": en_ventana,
            "golesEnAnadido": en_anadido,
            "rojasAntes": rojas_antes,
            "cobrable": cobrable,
            "clase": clase or None,
            "ventanaDeRama": bool(de_rama),
            "reasignacion": reasig,
            "nota": ("sin ficha de eventos no se puede comprobar la ventana: queda sin veredicto"
                     if not out["evidencia"]["conFicha"] else
                     f"el equipo recibió {recibidos} goles antes de la ventana: no se echó, se rompió "
                     "(disciplina 3); no se cobra en ninguna métrica"
                     if clase == "roto" else
                     f"el marcador ya estaba {dif} goles arriba antes de la ventana: la rama quedó abandonada "
                     "(disciplina 24); no se cobra en ninguna métrica"
                     if clase == "rama_abandonada" else
                     "hubo una roja antes del gol de la ventana: el mecanismo declarado no se puso a "
                     "prueba (disciplina 24, acierto no testeado) y no cuenta en ninguna métrica"
                     if rojas_antes and en_ventana else
                     "hubo una roja antes de que terminara la ventana y no hubo gol en ella: el partido "
                     "se jugó con otro mecanismo (disciplinas 16 y 17), queda no testeada y no cuenta "
                     "en ninguna métrica"
                     if rojas_antes else
                     "gol(es) en el añadido: no tienen ventana (disciplina 23), se anotan aparte"
                     if en_anadido and not en_ventana else ""),
        })
    if bloques:
        out["tde"] = {"bloques": bloques}

    # ── el reventón de la burbuja: lo que se dijo antes y lo que pasó ───────
    out["reventon"] = reventon_objetivo(fixture_id, fx, declarado)
    # ── las OTRAS burbujas que este partido cortó: lo que hay que rastrear ──
    out["otrasFamilias"] = familias_objetivo(fx)
    # ── la buena espina de la burbuja: la lectura del analista, contra el resultado
    _esp = (parte.get("lecturaSad") or {}).get("espina") or {}
    _calc = None
    if any((x or {}).get("guia") == "condicion" for x in _esp.values() if isinstance(x, dict)):
        try:
            from backend.analisis.parte import _reventon_calculado
            _calc = _reventon_calculado(fx)
        except Exception:  # noqa: BLE001 — sin la tarjeta de la condición, el veredicto sigue
            _calc = None
    out["espina"] = espina_objetivo(_esp, real, out.get("reventon"), _calc)
    # ── la matriz: qué escenario se jugó y qué se había escrito para él ────
    out["matriz"] = matriz_objetivo(parte.get("matriz") or {}, real)
    return out


_ESCENARIO_DE = {"gana": "ganar", "empata": "empatar", "pierde": "perder"}


def matriz_objetivo(matriz: dict, real: str) -> dict:
    """Por lado, el escenario que el marcador dice que se jugó (ganar · empatar
    · perder) y lo que la matriz había escrito para ese escenario. No hay
    acierto: la matriz es narrativa. Si lo escrito apareció lo juzga quien
    cierra el caso (`porLado.*.escenario`)."""
    out = {"nota": "la matriz es narrativa: el escenario lo da el marcador; si la palanca o el "
                   "gatillo escrito fue el que apareció es juicio de la autopsia, sin tasa"}
    if not any((matriz or {}).get(l) for l in ("a", "b")):
        # no es un fallo del depósito: los partes anteriores al 15/10/2026
        # (12:05 UTC) traían la matriz solo en prosa, en `documentos`
        out["sinMatriz"] = ("el parte no trae la matriz estructurada (`matriz`): si se depositó antes "
                            "del 15/10/2026 la tenía solo en prosa (`documentos`); el escenario se "
                            "juzga contra esa prosa y no cuenta como «no declarada»")
    for lado in ("a", "b"):
        gana = (real == "local") if lado == "a" else (real == "visita")
        esc = _ESCENARIO_DE["gana" if gana else ("empata" if real == "empate" else "pierde")]
        escrito = ((matriz or {}).get(lado) or {}).get(esc) or {}
        out[lado] = {"escenario": esc, "escrito": escrito, "declarado": bool(escrito)}
    return out


_MOVIMIENTO_DE = {"gana": "positiva", "empata": "cero", "pierde": "negativa"}


def _tarjeta_lado(reventon: dict | None, lado: str, movimiento_real: str,
                  condicion: dict | None = None) -> dict | None:
    """La espina de la tarjeta de ESE día y si se cumplió. Sin burbuja abierta
    no hay tarjeta.

    CON LA GUÍA DE LA CONDICIÓN, LA TARJETA ES LA DE LA CONDICIÓN. Monza 4-0
    Cagliari (19/10/2026): la K total del Cagliari estaba en 0 tras un 1-1, el
    parte leyó con razón su K de VISITA (+8.97, tres victorias, récord) y esa
    tarjeta decía «pierde» (cambio 38 %). Cagliari perdió 4-0, pero el
    veredicto buscaba la tarjeta en la total, no la encontraba y el acierto de
    la tarjeta no se contaba. `condicion` es el bloque `condicion` del reventón
    calculado al día del partido."""
    from backend.analisis import burbuja
    if condicion and condicion.get("espinaTarjeta"):
        t = condicion["espinaTarjeta"]
        return {**t, "nivel": (condicion.get("riesgo") or {}).get("nivel"),
                "signo": (condicion.get("actual") or {}).get("signo"), "guia": "condicion",
                "cumplida": t["lectura"] == movimiento_real}
    dec = ((reventon or {}).get(lado) or {}).get("declarado") or {}
    nivel = (dec.get("riesgo") or {}).get("nivel")
    t = burbuja.espina_tarjeta(dec.get("signo"), burbuja._movimiento_esperado("total", dec.get("signo"), nivel)
                               if nivel else None)
    if not t:
        return None
    return {**t, "nivel": nivel, "signo": dec.get("signo"), "cumplida": t["lectura"] == movimiento_real}


def espina_objetivo(espina: dict, real: str, reventon: dict | None = None,
                    calculado: dict | None = None) -> dict:
    """Por lado: adónde dijo el analista que iba la K total (positiva · cero ·
    negativa) y adónde fue. Después de un partido la K total es positiva si el
    equipo ganó, 0 si empató y negativa si perdió (MOTOR_SAD_EXTRACCION §3.3:
    la victoria suma o arranca k⁺, el empate resetea las dos, la derrota abre
    k⁻), así que se comprueba con el marcador. `neutra` no se juzga. La K de la
    condición (`guia: condicion`) se mueve en la misma dirección: el marcador
    la comprueba igual."""
    out = {"nota": "positiva = la K creció o arrancó (ganó) · cero = se reinició (empató) · negativa = "
                   "perdió · neutra no se juzga. Lo que mide si la lectura sirve es la tasa en las "
                   "lecciones contra la frecuencia de cada movimiento, no un caso suelto"}
    for lado in ("a", "b"):
        e = espina.get(lado) or {}
        lectura = e.get("lectura") or ""
        gana = (real == "local") if lado == "a" else (real == "visita")
        resultado = "gana" if gana else ("empata" if real == "empate" else "pierde")
        movimiento = _MOVIMIENTO_DE[resultado]
        # LA TARJETA AL LADO DEL ANALISTA (19/10/2026): la espina que da la guía
        # calibrada sola y si el analista la siguió o fue contra ella. Es lo que
        # dice, con casos, si leer los skills encima de la tarjeta suma o resta.
        cond = (((calculado or {}).get(lado) or {}).get("condicion")
                if (e.get("guia") or "total") == "condicion" else None)
        tarjeta = _tarjeta_lado(reventon, lado, movimiento, cond)
        vs = (None if not tarjeta or not lectura or lectura == "neutra" else
              "sigue" if lectura == tarjeta["lectura"] else "contra")
        if not lectura:
            out[lado] = {"lectura": None, "resultado": resultado, "movimiento": movimiento, "cumplida": None,
                         "tarjeta": tarjeta, "vsTarjeta": None}
            continue
        out[lado] = {"lectura": lectura, "guia": e.get("guia") or "total",
                     "porque": e.get("porque") or "", "resultado": resultado,
                     "movimiento": movimiento,
                     "cumplida": None if lectura == "neutra" else lectura == movimiento,
                     "tarjeta": tarjeta, "vsTarjeta": vs}
    return out


def rama_jugada(tde: dict, goles: list[dict], total_goles: int, con_ficha: bool) -> dict:
    """Qué rama de la reasignación (disciplina 44) jugó el partido para el
    equipo del bloque, y si estaba declarada. Es observación: no hay acierto
    —la rama no es un pronóstico—, pero un lado sin la rama que se dio es la
    lección que la autopsia del 11/10 encontró once veces."""
    foco = tde.get("equipo") or ""
    declarada = tde.get("reasignacion") or {}
    if not foco:
        return {"rama": None, "declarada": bool(declarado_ok(declarada)), "nota": "bloque sin lado"}
    if total_goles == 0:
        return {"rama": "sinGoles", "minuto": None, "declarada": bool(declarado_ok(declarada)),
                "loDeclarado": None, "nota": "sin goles: ninguna rama se activó"}
    if not con_ficha or not goles:
        return {"rama": None, "minuto": None, "declarada": bool(declarado_ok(declarada)),
                "loDeclarado": None, "nota": "sin ficha de eventos no se sabe quién marcó primero"}
    primero = goles[0]
    rama = "siMarcaPrimero" if primero["lado"] == foco else "siRecibePrimero"
    lo = declarada.get(rama)
    return {"rama": rama, "minuto": primero["minuto"], "declarada": lo is not None, "loDeclarado": lo,
            "nota": "" if lo is not None else
                    "la rama que jugó el partido no estaba declarada (disciplina 44): "
                    "el bloque P quedó viejo desde ese minuto sin nada escrito"}


def declarado_ok(reasig: dict) -> bool:
    return all(r in (reasig or {}) for r in ("siMarcaPrimero", "siRecibePrimero"))


# ── el reventón, comprobado ─────────────────────────────────────────────────
#
# El parte trae, por lado, la burbuja abierta y su riesgo (`reventonCalculado`,
# docs/REVENTON.md). Eso se recalcula al leer, así que después del partido ya
# no dice lo que decía antes: el «declarado» de acá se reconstruye con la
# vista «al día del partido» (§9: historia ESTRICTAMENTE anterior al fixture y
# el fixture como próximo), que es la misma construcción anti-hindsight del
# backtest y da exactamente los números que el parte mostraba antes del pitazo.
# Lo observado sale de la K fusionada de ESE partido, con la misma función que
# detecta los reventones en la historia (`burbuja.episodios`): si el fixture
# figura como el que cerró la burbuja, reventó; si no, siguió.
#
# Lo que esto NO dice: si Cowork leyó bien. Un riesgo alto que revienta no es
# «acierto» y uno bajo que revienta no es «fallo» —el riesgo es una tasa, no
# un pronóstico—; por eso acá no hay veredicto, hay observación, y la tasa se
# arma en las lecciones sobre los casos ciegos, contra la del backtest.

def reventon_objetivo(fixture_id: int, fx, declarado_1x2: str = "") -> dict:
    """Por lado: la burbuja total tal como estaba ANTES del partido (signo, K,
    racha, riesgo, extremo) y si ese partido la reventó. `comprobable` es
    False cuando el pipeline aún no calculó la constante del partido; sin
    burbuja abierta antes no hay nada que observar (`sinBurbuja`).

    Y, por lado, si el 1X2 declarado FUE A FAVOR de la racha o en contra
    (`pronosticoVsRacha`) y, cuando el riesgo era alto, si el pronóstico lo
    respetó (`respetoRiesgo`). Es lo que hace medible la pregunta que importa:
    ¿el Brier es mejor cuando Cowork le hace caso al riesgo que cuando no?"""
    out = {"nota": ("declarado = la burbuja total con la historia anterior al partido (vista "
                    "«al día del partido», §9 de docs/REVENTON.md); observado = si la K "
                    "fusionada de ESTE partido cerró la burbuja. Es observación, no veredicto: "
                    "el riesgo es una tasa, y la tasa se compara con la del backtest en las lecciones. "
                    "pronosticoVsRacha = si el 1X2 declarado apostó a que la racha SIGUE (aFavor) "
                    "o se corta (enContra); respetoRiesgo solo se juzga con riesgo alto o muy alto")}
    fecha = str(fx["date"])
    lados = (("a", fx["home_team_id"], fx["away_team_id"], fx["away_name"], "L"),
             ("b", fx["away_team_id"], fx["home_team_id"], fx["home_name"], "V"))
    for lado, tid, rid, rival, cond in lados:
        try:
            out[lado] = _reventon_lado(fixture_id, fecha, tid, rid, rival, cond)
        except Exception as e:  # noqa: BLE001 — se declara, no tumba el veredicto
            out[lado] = {"comprobable": False, "sinBurbuja": False, "declarado": None,
                         "observado": None, "nota": f"no se pudo calcular: {e}"}
        out[lado].update(pronostico_vs_racha(lado, out[lado].get("declarado"), declarado_1x2))
    return out


# LAS OTRAS BURBUJAS, DESPUÉS DEL PARTIDO (usuario, 17/10/2026: «un 0 a 2 para
# alguien que al menos marca gol de local debe ser entendible y rastreable»).
# Se reconstruyen las destacadas con la historia ESTRICTAMENTE anterior al
# fixture (la misma vista del parte) y se mira si el marcador las cortó. Un
# corte de una burbuja grande o en su récord queda `porExplicar`: como el
# récord no se corta más que lo normal (REVENTON §15), algo lo causó, y quien
# cierra el caso lo escribe en `porLado.*.cortes` con un mecanismo de la lista
# cerrada del estudio de reventones. Observación, sin acierto ni tasa.
POR_EXPLICAR_DESDE = 5


def familias_objetivo(fx) -> dict:
    out = {"nota": ("las burbujas de doble oportunidad, márgenes y goles destacadas ANTES del partido "
                    "(vista «al día del partido») y cuáles cortó este marcador; `porExplicar` = grande o en "
                    "su récord: el corte tiene una causa que va en porLado.*.cortes (mecanismo de la lista "
                    "del estudio de reventones). Observación, sin tasa")}
    fecha = str(fx["date"])
    lados = (("a", fx["home_team_id"], fx["home_name"], "L", fx["g_local"], fx["g_visita"]),
             ("b", fx["away_team_id"], fx["away_name"], "V", fx["g_visita"], fx["g_local"]))
    for lado, tid, nombre, cond, gf, gc in lados:
        try:
            out[lado] = _familias_lado(tid, nombre, cond, fecha, int(gf), int(gc))
        except Exception as e:  # noqa: BLE001 — se declara, no tumba el veredicto
            out[lado] = {"cortadas": [], "siguieron": 0, "nota": f"no se pudo calcular: {e}"}
    return out


def _familias_lado(tid: int, nombre: str, cond: str, fecha: str, gf: int, gc: int) -> dict:
    from backend.analisis import familias
    from backend.app import constantes_de
    from backend.backtest_familias import FAMILIAS
    previas = list(reversed(constantes_de(tid, 500, antes=fecha)))
    desc = familias.describir(previas, cond, nombre)
    cortadas, siguieron = [], 0
    for f in desc["familias"]:
        if not f["destacada"]:
            continue
        if bool(FAMILIAS[f["familia"]](gf, gc)) == f["valor"]:
            siguieron += 1
            continue
        cortadas.append({
            "familia": f["familia"], "ambito": f["ambito"], "partidos": f["partidos"],
            "record": f["record"], "cuidado": f["cuidado"], "antes": f["texto"],
            "porExplicar": f["cuidado"] or f["partidos"] >= POR_EXPLICAR_DESDE,
        })
    return {"cortadas": cortadas, "siguieron": siguieron,
            "porExplicar": sum(1 for c in cortadas if c["porExplicar"])}


def pronostico_vs_racha(lado: str, declarado: dict | None, unxdos: str) -> dict:
    """¿El 1X2 declarado apostó a que la racha de este lado SIGUE o se corta?

    Una burbuja «+» es una racha de resultados por encima del nivel (el equipo
    viene ganando más de lo que le toca); «−», por debajo. Seguir la racha es
    pronosticar que el equipo gana con «+» o pierde con «−»; ir en contra, lo
    opuesto; el empate es neutro. Sin 1X2 declarado no hay nada que juzgar.

    `respetoRiesgo` se juzga SOLO con riesgo alto o muy alto: ahí «no seguir
    la racha» es lo que el protocolo pide (prompt v2.5, lecturaSad.reventon).
    Con riesgo bajo o medio seguirla no es un error, así que queda en None,
    no en False: un None es «no aplica», no «falló».
    """
    if not declarado or not unxdos or unxdos not in ("local", "empate", "visita"):
        return {"pronosticoVsRacha": None, "respetoRiesgo": None}
    signo = declarado.get("signo")
    if unxdos == "empate":
        vs = "neutro"
    else:
        gana = (unxdos == "local") if lado == "a" else (unxdos == "visita")
        sigue = gana if signo == "+" else (not gana)
        vs = "aFavor" if sigue else "enContra"
    nivel = (declarado.get("riesgo") or {}).get("nivel") or ""
    respeto = (vs != "aFavor") if nivel in ("alto", "muy alto") else None
    return {"pronosticoVsRacha": vs, "respetoRiesgo": respeto}


def _reventon_lado(fixture_id: int, fecha: str, tid: int, rid: int, rival: str, cond: str) -> dict:
    from backend.analisis import burbuja
    from backend.app import constantes_de, niveles_de
    # antes del partido: estrictamente anterior (la constante del partido lleva su misma fecha)
    previas = list(reversed(constantes_de(tid, 500, antes=fecha)))
    nv, nr = niveles_de(tid, 1, antes=fecha), niveles_de(rid, 1, antes=fecha)
    prox = {"fixtureId": fixture_id, "fecha": fecha[:10], "rivalId": rid, "rival": rival,
            "condicion": cond, "nivelRival": nr[0]["nivel"] if nr else 1.0}
    pre = burbuja.analizar(previas, equipo_id=tid, nivel=nv[0]["nivel"] if nv else 0.5,
                           bin_=nv[0]["bin"] if nv else 0, proximo=prox, plantilla=None,
                           hoy=fecha[:10])["familias"]["total"]
    actual = pre.get("actual")
    if not actual:
        return {"comprobable": False, "sinBurbuja": True, "declarado": None, "observado": None,
                "nota": "sin burbuja abierta antes del partido: no había nada que reventar"}
    riesgo = pre.get("riesgo") or {}
    declarado = {
        "signo": actual["signo"], "k": actual["k"], "partidos": actual["partidos"],
        "riesgo": {"nivel": riesgo.get("nivel", "sin base"), "puntos": riesgo.get("puntos", 0)},
        "rivalTramo": (pre.get("rival") or {}).get("tramo"),
        "extremo": bool((pre.get("extremo") or {}).get("activo")),
    }
    # después: la constante de ESTE partido, si el pipeline ya la calculó
    hasta_hoy = list(reversed(constantes_de(tid, 500, hasta=fecha)))
    fila = next((f for f in hasta_hoy if f["fixtureId"] == fixture_id), None)
    if not fila:
        return {"comprobable": False, "sinBurbuja": False, "declarado": declarado, "observado": None,
                "nota": "el pipeline todavía no calculó la constante de este partido: "
                        "corre `python -m backend.ingesta.pipeline` y vuelve a leer"}
    cerrados, abierta, _n = burbuja.episodios(hasta_hoy, "total")
    cerro = next((r for r in cerrados if r["fixtureId"] == fixture_id), None)
    k_despues = float(fila["fusion"]["k"])
    revento = cerro is not None
    return {
        "comprobable": True, "sinBurbuja": False,
        "declarado": declarado,
        "observado": {
            "revento": revento,
            "kDespues": burbuja._r2(k_despues),
            "signoDespues": "+" if k_despues > 0 else "-" if k_despues < 0 else "0",
            "kPico": cerro["kPico"] if cerro else None,
            "partidos": cerro["partidos"] if cerro else (abierta or {}).get("partidos"),
        },
        "nota": (f"reventó: la burbuja {declarado['signo']} de {declarado['partidos']} partidos "
                 f"(K {declarado['k']:+.2f}) cerró con este partido"
                 if revento else
                 f"siguió: la burbuja {declarado['signo']} llega a "
                 f"{(abierta or {}).get('partidos', '?')} partidos (K {k_despues:+.2f})"),
    }
