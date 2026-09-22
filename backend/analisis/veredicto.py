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

    # ── el reventón de la burbuja: lo que se dijo antes y lo que pasó ───────
    out["reventon"] = reventon_objetivo(fixture_id, fx, declarado)
    return out


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
