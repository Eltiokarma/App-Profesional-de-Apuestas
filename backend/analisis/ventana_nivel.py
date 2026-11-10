"""CON QUÉ PARTIDOS SE ARMÓ EL NIVEL (30/10/2026, incidencia 860).

Konyaspor 0-4 Galatasaray: el 1X2 del motor dio 41 % al 14.º contra 31 % al
líder, con fiabilidad «alta». El nivel de Galatasaray (ventana de los últimos
20 partidos terminados, todas las competiciones: MOTOR §2) traía SEIS amistosos
de pretemporada (Monza 0-2, Venezia 0-3, Villarreal 1-2…) y tres de Champions:
1,65 puntos por partido en la ventana contra 2,44 en la liga. Lo salvó seguir
al mercado (sad v4.1).

MEDIDO el mismo día (`backend/backtest_nivel_ventana.py`, 9.191 partidos de
prueba del padrón): los amistosos NO eran la causa. Sacarlos del nivel no mejora
el 1X2 (+0,0009 de log-loss, IC cruzando cero), sacar también los
internacionales lo EMPEORA justo donde hay amistosos (+0,0066) y en el caso el
local pasa de 41,4 % a 40,8 %. El 41 % sale de un nivel que separaba al líder
del 14.º por solo 0,26, menos de lo que vale jugar en casa (0,382 de μ = 0,55 de
nivel). La localía tampoco es: la de la Süper Lig medida por liga es 0,479, de
las del medio (`backtest_localia_liga`). La forma y la regresión NO entran al
1X2 (`unXDos` solo ve nivel, rival y localía). Lo que sí se midió: con 3+ amistosos en un lado el motor queda
el doble de lejos del mercado (log-loss 0,084 peor, n = 989, contra 0,041 en el
resto). Eso sostiene el aviso.

Esto NO toca la fórmula del motor (es sagrada). Acá solo se CUENTA de qué está
hecha la ventana y se dice cuánto creerle a μ: con `UMBRAL_AMISTOSOS` amistosos
o más en la ventana de un lado, la fiabilidad de μ baja a «media» con la nota.
Solo lectura, una consulta por equipo.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from backend import db as saddb

VENTANA = 20                 # la del motor (MOTOR_SAD_EXTRACCION.md §2)
AMISTOSOS = {10, 667}        # Friendlies (selecciones) y Friendlies Clubs
UMBRAL_AMISTOSOS = 3         # desde acá la fiabilidad de μ baja a «media»
_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long = 'Match Finished')"


def _internacionales() -> set[int]:
    try:
        from backend.ingesta.extractor import LIGAS_INTERNACIONALES
        return set(LIGAS_INTERNACIONALES)
    except Exception:  # noqa: BLE001 — sin la ingesta importable: la lista conocida
        return {2, 3, 848, 13, 11}


def es_amistoso(league_id, nombre: str | None = None) -> bool:
    n = (nombre or "").lower()
    return league_id in AMISTOSOS or "friendl" in n or "amistos" in n


def composicion(team_id: int, antes: str | None) -> dict | None:
    """Los últimos `VENTANA` partidos terminados del equipo ANTES de `antes`
    (el mismo filtro y la misma deduplicación que el pipeline del motor),
    contados por tipo. None sin partidos."""
    params: list = [team_id, team_id]
    cond = ""
    if antes:
        cond = " AND f.date < ?"
        params.append(str(antes).replace("T", " ").rstrip("Z")[:19])
    try:
        filas = saddb.query(
            "sad", f"""SELECT f.id, f.date, f.league_id, f.home_team_id, f.away_team_id,
                              COALESCE(f.fulltime_home, f.goals_home) AS gh,
                              COALESCE(f.fulltime_away, f.goals_away) AS ga, l.name AS liga
                       FROM fixtures f LEFT JOIN leagues l ON l.id = f.league_id
                       WHERE (f.home_team_id=? OR f.away_team_id=?) AND {_FIN}
                         AND COALESCE(f.fulltime_home, f.goals_home) IS NOT NULL
                         AND COALESCE(f.fulltime_away, f.goals_away) IS NOT NULL{cond}
                       ORDER BY f.date DESC, f.id DESC LIMIT {VENTANA + 10}""", tuple(params))
    except Exception:  # noqa: BLE001 — base sin la tabla leagues o vieja: sin composición, no se afirma nada
        return None
    # el mismo partido con dos ids entra una vez (pipeline.sin_duplicados), en
    # el orden del motor (fecha, id)
    vistos, ventana = set(), []
    for f in sorted(filas, key=lambda r: (str(r["date"]), r["id"])):
        clave = (f["home_team_id"], f["away_team_id"], str(f["date"])[:10], f["gh"], f["ga"])
        if clave in vistos:
            continue
        vistos.add(clave)
        ventana.append(f)
    ventana = ventana[-VENTANA:]
    if not ventana:
        return None
    inter = _internacionales()
    amistosos = [f for f in ventana if es_amistoso(f["league_id"], f["liga"])]
    internacionales = [f for f in ventana if f["league_id"] in inter]
    otra = _de_otra_liga(team_id, antes, [f for f in ventana if f not in amistosos and f not in internacionales])
    nombres = [f["liga"] or f"liga {f['league_id']}" for f in otra]
    return {
        "partidos": len(ventana),
        "amistosos": len(amistosos),
        "internacionales": len(internacionales),
        "otros": len(ventana) - len(amistosos) - len(internacionales),
        "otraLiga": len(otra),
        "otraLigaNombre": max(set(nombres), key=nombres.count) if nombres else None,
        "desde": str(ventana[0]["date"])[:10],
        "hasta": str(ventana[-1]["date"])[:10],
        "completa": len(ventana) >= VENTANA,
    }


def _de_otra_liga(team_id: int, antes: str | None, filas: list) -> list:
    """Los partidos de LIGA de la ventana que no son de la liga que juega hoy
    (06/11/2026, incidencia 1251, Coventry recién ascendido: la ventana del
    nivel traía sus partidos de Championship de abril-mayo sin marcar y el motor
    le daba más nivel que a Everton). Es la misma regla que ya marca las K del
    ascendido (`escala.historia_otra_categoria`, incidencias 974 y 975): liga
    = ni copa, ni internacional, ni amistoso (`escala.es_liga`); la de hoy es
    `escala.liga_vigente`. Solo se CUENTA: μ y la fiabilidad no se tocan."""
    if not antes or not filas:
        return []
    try:
        from backend.analisis import escala
        base = escala.liga_vigente(team_id, str(antes))
        if not base:
            return []
        es = {lid: escala.es_liga(lid) for lid in {f["league_id"] for f in filas}}
    except Exception:  # noqa: BLE001 — sin la escala legible no se afirma que una liga sea otra
        return []
    return [f for f in filas if es.get(f["league_id"]) and f["league_id"] != base]


def texto(c: dict | None) -> str:
    if not c:
        return ""
    partes = []
    if c["amistosos"]:
        partes.append(f"{c['amistosos']} amistoso{'s' if c['amistosos'] != 1 else ''}")
    if c["internacionales"]:
        partes.append(f"{c['internacionales']} internacional{'es' if c['internacionales'] != 1 else ''}")
    if c.get("otraLiga"):
        partes.append(f"{c['otraLiga']} de otra liga"
                      + (f" ({c['otraLigaNombre']})" if c.get("otraLigaNombre") else ""))
    return (" y ".join(partes) + f" de {c['partidos']}") if partes else ""


VENTANA_CORTA = 10      # con menos partidos en la ventana, el nivel casi no tiene historia
VENTANA_VIEJA_DIAS = 365   # con el último partido de hace más, el nivel es de otra época
SEDE_RECIENTE_DIAS = 365   # la sede habitual del local sale de sus partidos de local de este último año (1360)


def _sede_norm(nombre) -> str:
    """El nombre del estadio para comparar: el `plano` de identidad, sin espacios de más."""
    from backend.identidad import plano
    return " ".join(plano(str(nombre or "")).split())


# las palabras que no distinguen un estadio de otro (incidencia 1165)
_SEDE_GENERICAS = frozenset(
    "estadio stadium stade stadio estadi estadio stadion stadionul arena campo field ground park parque "
    "polideportivo municipal olimpico olympic nacional national complejo coliseo coliseum club sporting "
    "sc fc cf ac de del la el los las le du des di da do dos das of the y and".split())


def _sede_tokens(nombre) -> frozenset:
    return frozenset(t for t in _sede_norm(nombre).replace("-", " ").split()
                     if len(t) >= 2 and t not in _SEDE_GENERICAS)


def misma_sede(a, b) -> bool:
    """¿Dos nombres de estadio son el mismo? Las palabras que lo distinguen de
    uno están todas en el otro (03/11/2026, incidencia 1165, reaparecida tras la
    1090: Táchira en «Pueblo Nuevo» / «Estadio Polideportivo de Pueblo Nuevo»,
    Mushuc Runa en «Estadio del Mushuc Runa Sporting Club» / «Estadio COAC
    Mushuc Runa», con otro venue_id). «Stade Louis-Achille» y «Stade
    Pierre-Aliker» no comparten nada: siguen siendo dos."""
    ta, tb = _sede_tokens(a), _sede_tokens(b)
    return bool(ta) and bool(tb) and (ta <= tb or tb <= ta)


def _admite_neutral(league_id) -> bool:
    """¿La competición juega en cancha neutral? Copa (nacional) o torneo
    internacional de clubes; ante la duda (sin poder leer la liga), sí."""
    if league_id is None:
        return True
    try:
        from backend.analisis import escala
        from backend.jugadores import _ligas_internacionales
        return league_id in _ligas_internacionales() or escala.es_copa(league_id)
    except Exception:  # noqa: BLE001 — sin la liga legible, la regla de siempre (no se calla un neutral real)
        return True


def cancha_neutral(home_id: int, sede: str | None, antes: str | None, fixture_id: int | None = None) -> bool:
    """¿El partido se juega fuera de la cancha habitual del local? La sede más
    repetida en sus últimos 20 partidos de local (con 5+), distinta de esta
    (01/11/2026, incidencia 991: Franciscain–Aiglon en el Stade Louis-Achille).

    EL MISMO ESTADIO CON OTRO NOMBRE NO ES NEUTRAL (03/11/2026, incidencia 1090,
    x10): la API renombra el estadio (patrocinio, traducción) y el texto deja de
    casar —Universidad Católica en «San Carlos de Apoquindo» / «Claro Arena»,
    Frosinone en «Stadio Benito Stirpe» / «PSC Arena», Groningen en «Euroborg» /
    «Hitachi Capital Mobility Stadion», Danubio en «Jardines Del Hipódromo» /
    «Gardens of the Hippodrome», Levadiakos en «Levadia Stadium» / «Levadia
    Municipal Stadium», Getafe en «Coliseum» / «Coliseum Alfonso Pérez»—. Por
    eso: la sede se compara por `venue_id` cuando lo hay (el estadio de la API
    no cambia de id al cambiar de nombre), los nombres se normalizan, un nombre
    vacío no es una sede, y una sede donde el local YA jugó de local 2+ veces
    en la ventana es su casa (renombrada o la de esta temporada), no neutral."""
    if not sede and fixture_id is None:
        return False
    try:
        hoy = (saddb.query_one("sad", "SELECT * FROM fixtures WHERE id=?", (fixture_id,))
               if fixture_id is not None else None)
        if not antes and hoy is not None and "date" in hoy.keys():
            antes = hoy["date"]
        params: list = [home_id]
        cond = ""
        if antes:
            corte = str(antes).replace("T", " ").rstrip("Z")[:19]
            cond = " AND date < ? AND date >= ?"
            # SIN HISTORIA DE SEDE RECIENTE NO SE AFIRMA NEUTRAL (10/11/2026,
            # incidencia 1360, reaparición de la 1207 en copa): Amorebieta–
            # Logroñés en Urritxe, Copa del Rey R128. Su última temporada de
            # local en la base es la Segunda 2023-24, jugada en Lezama (Urritxe
            # no cumplía); desde que bajó a una categoría que no ingestamos no
            # tiene partidos de local con sede. La «sede habitual» de hace dos
            # años no es la de hoy: solo cuentan los partidos de local del
            # último año (`SEDE_RECIENTE_DIAS`) y con menos de 5 no se afirma.
            try:
                desde = (datetime.fromisoformat(corte[:10]) - timedelta(days=SEDE_RECIENTE_DIAS)).date().isoformat()
            except ValueError:
                desde = "0000"
            params += [corte, desde]
        filas = saddb.query("sad", f"SELECT * FROM fixtures WHERE home_team_id=?"
                                   f"{cond} ORDER BY date DESC LIMIT 40", tuple(params))
    except Exception:  # noqa: BLE001 — base sin la sede: no se afirma cancha neutral
        return False

    def _col(f, c):
        return f[c] if c in f.keys() else None

    def _clave(f) -> str:
        if _col(f, "venue_id") is not None:
            return f"id:{_col(f, 'venue_id')}"
        n = _sede_norm(_col(f, "venue_name"))
        return f"n:{n}" if n else ""

    # EN LA LIGA NO HAY CANCHA NEUTRAL QUE SE PUEDA AFIRMAR POR EL NOMBRE
    # (04/11/2026, incidencia 1207, reaparición de la 1090): Olimpia en el
    # «Estadio Manuel Ferreira», que es el viejo nombre del Osvaldo Domínguez
    # Dibb donde jugó 29 de 39 de local; otro id y ni una palabra en común. Las
    # once marcas falsas medidas (1090, 1165, 1207) fueron todas de liga y la
    # verdadera (991, el 7.º tour de la Coupe de France en Martinica) de copa:
    # con el fixture a la vista, solo copa o torneo internacional pueden dar
    # neutral. Sin fixture (solo el nombre) queda la regla de siempre.
    if hoy is not None and not _admite_neutral(_col(hoy, "league_id")):
        return False
    previas = [f for f in filas if _clave(f)][:20]    # un nombre vacío no es una sede
    if hoy is not None and _clave(hoy):
        clave_hoy, nombre_hoy = _clave(hoy), _sede_norm(_col(hoy, "venue_name")) or _sede_norm(sede)
    else:
        nombre_hoy = _sede_norm(sede)
        clave_hoy = f"n:{nombre_hoy}" if nombre_hoy else ""
    if not clave_hoy or len(previas) < 5:
        return False
    cuenta: dict[str, int] = {}
    for f in previas:
        cuenta[_clave(f)] = cuenta.get(_clave(f), 0) + 1
    habitual = max(cuenta, key=cuenta.get)
    if cuenta[habitual] * 2 <= len(previas):
        return False
    # ya jugó ahí de local 2+ veces (por id o por el nombre normalizado): es su casa
    mismo_nombre = sum(1 for f in previas if nombre_hoy and _sede_norm(_col(f, "venue_name")) == nombre_hoy)
    if cuenta.get(clave_hoy, 0) >= 2 or mismo_nombre >= 2:
        return False
    if clave_hoy == habitual:
        return False
    # el estadio habitual con el nombre recortado o ampliado (y otro venue_id)
    # es el mismo: no es neutral (1165)
    nombres_habitual = {_col(f, "venue_name") for f in previas if _clave(f) == habitual}
    nombre_crudo_hoy = (_col(hoy, "venue_name") if hoy is not None else None) or sede
    return not any(misma_sede(nombre_crudo_hoy, n) for n in nombres_habitual if n)


SEDE_MIN_LOCAL = 3        # partidos de local con sede para afirmar cuál es la de un equipo
SEDE_TEMPORADA_DIAS = 365  # la sede de local «de la temporada»: lo jugado de local en el último año


def _col(f, c):
    return f[c] if c in f.keys() else None


def sede_de_local(team_id: int, antes: str | None) -> dict | None:
    """La sede de local del equipo en la temporada: la más repetida en sus
    últimos 20 partidos de local del último año (con `SEDE_MIN_LOCAL`+ y más de
    la mitad), por `venue_id` o, sin él, por el nombre normalizado. None si no
    se puede afirmar."""
    params: list = [team_id]
    cond = ""
    if antes:
        from datetime import datetime, timedelta
        corte = str(antes).replace("T", " ").rstrip("Z")[:19]
        cond = " AND date < ?"
        params.append(corte)
        try:
            desde = datetime.fromisoformat(corte[:10]) - timedelta(days=SEDE_TEMPORADA_DIAS)
            cond += " AND date >= ?"
            params.append(desde.strftime("%Y-%m-%d"))
        except ValueError:
            pass
    try:
        filas = saddb.query("sad", f"SELECT * FROM fixtures WHERE home_team_id=?{cond} "
                                   "ORDER BY date DESC LIMIT 40", tuple(params))
    except Exception:  # noqa: BLE001 — base sin la sede: no se afirma ninguna
        return None

    def _clave(f) -> str:
        if _col(f, "venue_id") is not None:
            return f"id:{_col(f, 'venue_id')}"
        n = _sede_norm(_col(f, "venue_name"))
        return f"n:{n}" if n else ""

    previas = [f for f in filas if _clave(f)][:20]
    if len(previas) < SEDE_MIN_LOCAL:
        return None
    cuenta: dict[str, int] = {}
    for f in previas:
        cuenta[_clave(f)] = cuenta.get(_clave(f), 0) + 1
    habitual = max(cuenta, key=cuenta.get)
    if cuenta[habitual] < SEDE_MIN_LOCAL or cuenta[habitual] * 2 <= len(previas):
        return None
    suyas = [f for f in previas if _clave(f) == habitual]
    nombres = [n for f in suyas if (n := _col(f, "venue_name"))]
    ciudades = {_sede_norm(c) for f in suyas if (c := _col(f, "venue_city")) and _sede_norm(c)}
    return {"clave": habitual, "nombre": max(set(nombres), key=nombres.count) if nombres else None,
            "nombres": set(nombres), "ciudades": ciudades, "partidos": cuenta[habitual]}


def sede_compartida(home_id: int, away_id: int, antes: str | None) -> str | None:
    """¿Los dos equipos tienen la MISMA sede de local en la temporada? Devuelve
    el nombre del estadio (o «el mismo estadio») si sí, None si no o sin dato.

    ESTADIO COMPARTIDO (10/11/2026, incidencias 1333 y su gemela del 08/11,
    decisión del usuario): Nacional Potosí–Real Potosí juegan los dos de local
    en el Víctor Agustín Ugarte (1645538) y Blooming–Oriente Petrolero en el
    Tahuichi; el motor les sumó la localía de 0,382 igual y dio 49 % al «local»
    contra 37 % del mercado. La fórmula NO se toca (es sagrada): esto se mide
    en la base y viaja como aviso de fiabilidad. Mismo `venue_id` alcanza; por
    el nombre (`misma_sede`) solo si las ciudades no se contradicen —«Estadio
    Monumental» de Lima y el de Buenos Aires son dos—."""
    a, b = sede_de_local(home_id, antes), sede_de_local(away_id, antes)
    if not a or not b:
        return None
    nombre = a["nombre"] or b["nombre"] or "el mismo estadio"
    if a["clave"] == b["clave"]:
        return nombre
    if a["ciudades"] and b["ciudades"] and not (a["ciudades"] & b["ciudades"]):
        return None
    if any(misma_sede(x, y) for x in a["nombres"] for y in b["nombres"]):
        return nombre
    return None


def _vieja_o_corta(c: dict | None, fecha: str | None) -> str:
    if not c:
        return ""
    if c["partidos"] < VENTANA_CORTA:
        return f"solo {c['partidos']} partidos en la ventana"
    if fecha and c.get("hasta"):
        try:
            from datetime import datetime
            dias = (datetime.fromisoformat(str(fecha)[:10]) - datetime.fromisoformat(c["hasta"][:10])).days
        except ValueError:
            return ""
        if dias > VENTANA_VIEJA_DIAS:
            return f"el último partido de la ventana es de hace {dias} días ({c['hasta']})"
    return ""


def nivel_por_defecto(team_id: int, fecha: str | None) -> str:
    """El motivo si el nivel del equipo a `fecha` es el POR DEFECTO del motor
    y no uno calculado; '' si es real (10/11/2026, incidencia 1366, Copa del
    Rey R128: el local de categoría inferior con 0,5 de 2 partidos y el Trival
    sin niveles salían «protector claro» en el P1a). La regla es la del motor
    (MOTOR §2.2-2.3, `ingesta.niveles.calcular_niveles`): con menos de 20
    partidos TODAS sus filas valen 0,5, y sin filas a la fecha el nivel cae al
    0,5 de `nivel_a_fecha`. Solo se lee levels.db; el nivel no se toca."""
    from backend.ingesta.niveles import DEFAULT_LEVEL
    f = str(fecha).replace("T", " ").rstrip("Z")[:19] if fecha else None
    try:
        tot = saddb.query_one("levels", "SELECT COUNT(*) AS n FROM team_levels WHERE team_id=?", (team_id,))
        hay = (saddb.query_one("levels", "SELECT 1 AS x FROM team_levels WHERE team_id=? AND date<=? LIMIT 1",
                               (team_id, f)) if f else tot and tot["n"])
    except Exception:  # noqa: BLE001 — sin levels.db legible no se afirma que el nivel sea el por defecto
        return ""
    n = int(tot["n"]) if tot else 0
    if not hay:
        return f"sin niveles a la fecha: el motor usa el {DEFAULT_LEVEL} por defecto"
    if n < VENTANA:
        return (f"{n} partidos en la base (menos de {VENTANA}): el motor le pone el nivel por defecto "
                f"{DEFAULT_LEVEL} a todos")
    return ""


def fiabilidad_con_ventana(fia: dict, comps: dict, nombres: dict | None = None,
                           fecha: str | None = None, neutral: bool = False,
                           compartida: str | None = None) -> dict:
    """La fiabilidad de μ con lo que dice la ventana de cada lado. Con
    `UMBRAL_AMISTOSOS`+ amistosos en un lado, «alta» baja a «media»; «media» y
    «baja» se quedan y la nota lo suma. Nunca la sube.

    VENTANA CORTA O VIEJA Y CANCHA NEUTRAL (01/11/2026, incidencia 991, decisión
    del usuario): con menos de `VENTANA_CORTA` partidos o el último de hace más
    de un año, la fiabilidad baja a «baja»; en cancha neutral la localía de μ no
    aplica y se dice (`canchaNeutral`). La fórmula no se toca."""
    nombres = nombres or {"local": "el local", "visitante": "el visitante"}
    con = {lado: c for lado, c in comps.items() if c and c["amistosos"] >= UMBRAL_AMISTOSOS}
    out = dict(fia or {})
    out["ventana"] = {lado: texto(c) for lado, c in comps.items() if texto(c)}
    viejas = {lado: m for lado, c in comps.items() if (m := _vieja_o_corta(c, fecha))}
    if viejas:
        out["nivel"] = "baja"
        out["porVentana"] = True
        out["nota"] = (f"{out.get('nota', '')} El nivel casi no tiene historia útil ("
                       + "; ".join(f"{nombres.get(l, l)}: {m}" for l, m in viejas.items())
                       + "): μ apenas orienta.").strip()
    if neutral:
        out["canchaNeutral"] = True
        out["nota"] = (f"{out.get('nota', '')} Se juega en cancha neutral: la localía que suma μ al local no "
                       "aplica (el motor la suma igual).").strip()
        if out.get("nivel") == "alta":
            out["nivel"] = "media"
    if compartida:
        # 1333: los dos de local en el mismo estadio; como la cancha neutral,
        # «alta» baja a «media» y la nota lo dice (μ no se toca)
        out["sedeCompartida"] = compartida
        out["nota"] = (f"{out.get('nota', '')} La localía del motor no aplica: estadio compartido "
                       f"({compartida}, sede de local de los dos en la temporada; el motor la suma igual).").strip()
        if out.get("nivel") == "alta":
            out["nivel"] = "media"
    if not con:
        return out
    detalle = "; ".join(f"{nombres.get(l, l)}: {texto(c)}" for l, c in con.items())
    nota = (f"El nivel se armó con partidos de otra exigencia ({detalle} en la ventana de {VENTANA}). "
            "En partidos así el 1X2 del motor queda el doble de lejos del mercado (log-loss 0,084 peor, "
            "contra 0,041 en el resto; backtest del 30/10/2026) y sacar los amistosos del nivel no lo "
            "arregla. μ no se toca: no te separes del mercado por el motor.")
    if out.get("nivel") == "alta":
        out["notaLiga"] = out.get("nota", "")
        out["nivel"] = "media"
        out["nota"] = nota
    else:
        out["nota"] = f"{out.get('nota', '')} Además: {nota}".strip()
    out["porVentana"] = True
    return out


def marcar_rival(familias: dict, equipo: dict | None, rival: dict | None) -> None:
    """LA DIFERENCIA DE NIVEL DEL REVENTÓN CON AMISTOSOS EN LA VENTANA
    (10/11/2026, incidencia 1104, decisión del usuario: Strasbourg 1552808
    sumó −3 por «rival muy favorito», 1,36 a favor de Auxerre, con 6 amistosos
    en la ventana; el mercado lo daba favorito por más de 20 puntos sobre el
    motor). Donde `rival.aFavor` puntúa (favorito o muy favorito), con
    `UMBRAL_AMISTOSOS`+ amistosos en la ventana del nivel de algún lado, el
    rival lleva `nivelConAmistosos` {equipo, rival, nota}. Los puntos y el
    riesgo NO se mueven (calibrados, REVENTON §13.2; sacar los amistosos del
    nivel no mejoró el 1X2, 860): se marca, como la escala."""
    ne = (equipo or {}).get("amistosos") or 0
    nr = (rival or {}).get("amistosos") or 0
    if max(ne, nr) < UMBRAL_AMISTOSOS:
        return
    n = max(ne, nr)
    quien = ("las dos ventanas" if min(ne, nr) >= UMBRAL_AMISTOSOS
             else "la ventana del equipo" if ne >= UMBRAL_AMISTOSOS else "la ventana del rival")
    nota = (f"la diferencia de nivel sale de una ventana con {n} amistoso{'s' if n != 1 else ''} "
            f"({quien}; equipo {ne}, rival {nr} de {VENTANA}): pesar con reserva")
    for fam in (familias or {}).values():
        r = (fam or {}).get("rival")
        if r and r.get("favorito") in ("favorito", "muy favorito"):
            r["nivelConAmistosos"] = {"equipo": ne, "rival": nr, "nota": nota}
