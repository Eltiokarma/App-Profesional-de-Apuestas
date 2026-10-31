"""La tabla F1 del EFE armada desde la base (`GET /analisis/cowork/f1/{id}`).

POR QUÉ. En la autopsia del 11/10/2026 (`docs/autopsias/2026-10-11.md`) al
menos 14 jugadores decisivos —goleadores, el arquero titular, el lateral que
jugaba todo— no estaban en la tabla F1 de ningún parte: la tabla se armaba con
la previa de la prensa, que nombra a los famosos y a los lesionados, no a los
que juegan. Un jugador que no está en la tabla F1 no pesa en el Impacto
Ponderado (`docs/COWORK.md`), así que su baja no existía para el bloque F.

QUÉ HACE. Dos cosas, las dos calculadas de la plantilla ingestada (minutos,
titularidades, goles y asistencias de la temporada; 0 requests):

- `tabla(fixture_id)`: por lado, los candidatos a la tabla F1 con su
  `jugadorId` —el cruce exacto con la hoja del partido—, la zona y un ROL
  SUGERIDO por la fracción de minutos. Es un punto de partida: el rol es del
  skill y lo confirma la prensa (un DT nuevo, una lesión larga), por eso viaja
  como `rolSugerido` y no se escribe solo en el parte.
- `alertas(parte, fx, nombres)`: `F1-DECISIVO-FUERA` (tipo `dato`) cuando un
  decisivo de la base no figura en la tabla F1 depositada. Se calcula al leer.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from backend import db as saddb
from backend import identidad as _id
from backend import jugadores as jug
from backend.analisis import bloque_f
from backend.nombres import _MARCAS_MOJIBAKE, limpiar_nombre
from backend.nombres import normalizar as normalizar_simple

CANDIDATOS = 16          # lo que pide el protocolo: 14-16 jugadores
TF_PCT, TH_PCT, ROT_PCT = 0.75, 0.5, 0.25
DECISIVO_PCT = 0.75      # titular habitual: ≥ 75 % de los minutos del que más jugó
DECISIVO_MIN_MINUTOS = 450   # con menos, la temporada recién arranca y el % no dice nada
DECISIVO_GA = 3          # top 3 en goles+asistencias, con al menos esto
_ZONA = {"Portero": "GK", "Defensa": "DEF", "Centrocampista": "MID", "Delantero": "ATK",
         # la API también la manda en inglés (Paulinho «Forward», Toluca, incidencia 359)
         "Goalkeeper": "GK", "Defender": "DEF", "Midfielder": "MID", "Attacker": "ATK", "Forward": "ATK"}
_ZONA_API = {"G": "GK", "D": "DEF", "M": "MID", "F": "ATK"}
ONCES_RECIENTES = 10     # onces que se miran para el rol
ONCES_FUERA_DE_PLANTILLA = 3   # titular en uno de estos últimos onces entra aunque la plantilla no lo tenga
ONCES_MINIMOS = 5        # con menos, el rol sale de los minutos de la temporada
_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished')"


def onces_recientes(team_id: int, antes: str) -> dict:
    """Titularidades en los últimos ONCES_RECIENTES partidos terminados con
    alineación, estrictamente antes de `antes`.

    POR QUÉ. Las stats de la plantilla son de la TEMPORADA, y en Sudamérica la
    temporada es el año: el rol de Millonarios del Clausura salía mezclado con
    el del Apertura (corrida del 13/10/2026). Lo que el once de hoy va a ser
    se parece más a los últimos diez onces que al año."""
    from backend.analisis.escala import AMISTOSOS
    try:
        crudo = saddb.query(
            "sad", f"""SELECT f.id, f.date FROM fixtures f
                       WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.date < ? AND {_FIN}
                         AND COALESCE(f.league_id, 0) NOT IN ({",".join("?" * len(AMISTOSOS))})
                         AND EXISTS (SELECT 1 FROM alineaciones a WHERE a.fixture_id=f.id AND a.team_id=?)
                       ORDER BY f.date DESC LIMIT ?""",
            (team_id, team_id, antes, *sorted(AMISTOSOS), team_id, ONCES_RECIENTES))
        fx = [r["id"] for r in _hasta_el_paron(crudo)]
        if not fx:
            return {"onces": 0, "jugadores": {}, "ultimo": None}
        filas = saddb.query(
            "sad", f"SELECT fixture_id, player_id, jugador, posicion, titular, grid FROM alineaciones "
                   f"WHERE team_id=? AND fixture_id IN ({','.join('?' * len(fx))})", (team_id, *fx))
        ga = saddb.query(
            "sad", f"SELECT jugador_id AS a, asistente_id AS b, detalle FROM fixture_eventos "
                   f"WHERE equipo_id=? AND tipo='Goal' AND fixture_id IN ({','.join('?' * len(fx))})",
            (team_id, *fx))
    except Exception:  # noqa: BLE001 — base sin la tabla de alineaciones
        return {"onces": 0, "jugadores": {}, "ultimo": None}
    js: dict[int, dict] = {}
    orden = {fid: i for i, fid in enumerate(fx)}
    lineas = _lineas_por_grid(filas)
    for f in filas:
        j = js.setdefault(f["player_id"], {"nombre": limpiar_nombre(f["jugador"] or ""), "posicion": f["posicion"] or "",
                                           "titular": 0, "convocado": 0, "enUltimo": False})
        j["convocado"] += 1
        j["titular"] += 1 if f["titular"] else 0
        # todos los nombres con que figura ESE id: la API a veces nombra una
        # hoja con otro jugador (Atlas, 35514 «J. Purata» en cinco y
        # «J. Sanchez» en dos, incidencia 610)
        if f["jugador"]:
            j.setdefault("nombres", set()).add(limpiar_nombre(f["jugador"]))
        if f["titular"] and f["fixture_id"] == fx[0]:
            j["enUltimo"] = True
        # titular en alguno de los ÚLTIMOS 3 onces (683): entra a la tabla aunque
        # la plantilla de la API no lo tenga
        if f["titular"] and orden[f["fixture_id"]] < ONCES_FUERA_DE_PLANTILLA:
            j["enUltimos3"] = True
        # LA POSICIÓN CON LA QUE ARRANCÓ SU ÚLTIMO ONCE (incidencias 171, 323 y
        # 66: A. García «MID» de central en la línea de 5, Tamara MID con «D» en
        # la ficha, un arquero «Defensa» que atajó el 09/10)
        # …Y CON EL GRID COMPLETO, LA LÍNEA ES LA FILA (incidencia 725: J. Parodi
        # «M» de la API siendo lateral derecho en 2:4; la misma regla que el once
        # oficial del DTP, 137)
        pos_f = lineas.get((f["fixture_id"], f["player_id"])) or f["posicion"]
        if f["titular"] and pos_f and orden[f["fixture_id"]] < j.get("_ordenPos", 99):
            j["_ordenPos"], j["posicionReciente"] = orden[f["fixture_id"]], pos_f
        if f["titular"] and pos_f:
            j.setdefault("_pos", []).append((orden[f["fixture_id"]], pos_f))
        # la posición de cualquier hoja (también del banco) para el que nunca
        # arrancó: sin ella la fila salía sin zona (897, S. Plaza en Potosí)
        if f["posicion"] and not j.get("posicionBanco"):
            j["posicionBanco"] = f["posicion"]
    for j in js.values():
        # LA POSICIÓN HABITUAL, NO LA DEL ÚLTIMO ONCE (incidencias 457 y 523):
        # Pumas salió una vez en 5-4-1 y Juninho pasó a MID y Antuna a DEF; Saka
        # «MID» por un 4-2-3-1. La más repetida en sus titularidades; empate → la
        # más reciente.
        if "nombres" in j:
            j["nombres"] = sorted(j["nombres"])
        pos = j.pop("_pos", [])
        if pos:
            cuenta: dict[str, int] = {}
            for _, x in pos:
                cuenta[x] = cuenta.get(x, 0) + 1
            j["posicionHabitual"] = max(cuenta, key=lambda x: (cuenta[x], -min(o for o, y in pos if y == x)))
    # LOS QUE DECIDEN DESDE EL BANCO (incidencia 382, Arouca: André Vidigal, gol
    # entrando y pateador de penales, fuera de la tabla por no ser titular)
    for g in ga:
        if "own" in (g["detalle"] or "").lower() or "missed" in (g["detalle"] or "").lower():
            continue
        for pid in (g["a"], g["b"]):
            if pid and pid in js:
                js[pid]["gaRecientes"] = js[pid].get("gaRecientes", 0) + 1
    return {"onces": len(fx), "jugadores": js, "ultimo": fx[0]}


def _lineas_por_grid(filas) -> dict:
    """{(fixture, jugador): G/D/M/F} de los onces con el grid completo (≥ 10
    titulares con «fila:columna»): fila 1 arquero, 2 defensa, la última
    delantera, el resto medio."""
    por_fx: dict[int, list] = {}
    for f in filas:
        if f["titular"]:
            por_fx.setdefault(f["fixture_id"], []).append(f)
    out = {}
    for fid, xi in por_fx.items():
        try:
            filas_g = [int(str(j["grid"]).split(":")[0]) for j in xi]
        except (KeyError, ValueError, TypeError, IndexError):
            continue
        if len(filas_g) < 10 or max(filas_g) < 3:
            continue
        ult = max(filas_g)
        for j, r in zip(xi, filas_g):
            out[(fid, j["player_id"])] = "G" if r == 1 else "D" if r == 2 else "F" if r == ult else "M"
    return out


PARON_DIAS = 35   # un hueco así entre dos partidos es el fin de una temporada


def _hasta_el_paron(filas: list) -> list:
    """Los partidos (del más nuevo al más viejo) hasta el primer hueco de más de
    PARON_DIAS: lo de antes es OTRA temporada, con otro plantel (incidencia 398:
    Paderborn con Seimen, que volvió a Stuttgart, de ROT; Köln y Schalke con la
    ventana mezclando la temporada anterior)."""
    from datetime import datetime
    out, previa = [], None
    for f in filas:
        try:
            d = datetime.fromisoformat(str(f["date"])[:19])
        except ValueError:
            out.append(f)
            continue
        if previa is not None and (previa - d).days > PARON_DIAS:
            break
        out.append(f)
        previa = d
    return out


CONVOCADO_MINIMO = 3   # con menos hojas, el denominador es la ventana entera


def onces_disponible(r: dict | None, onces: int) -> int:
    """En cuántos de los onces mirados ESTABA (titular o en el banco). Un
    lesionado o un recién llegado no rota: no estaba (incidencias 398 y 509:
    E. Martínez, titular en todos desde que llegó, «TH 6 de 10»; Julián Álvarez
    ROT por las fechas que se perdió). Con pocas hojas, la ventana entera."""
    conv = (r or {}).get("convocado") or 0
    # EL ARQUERO QUE NO ESTÁ EN LA HOJA FUE REEMPLAZADO POR OTRO ARQUERO: es
    # rotación, no ausencia (incidencia 879, Casa Pia: André Gomes TF con 5 de
    # 10 y tres arqueros que se alternan)
    if (r or {}).get("posicionHabitual") == "G":
        return onces
    if conv >= CONVOCADO_MINIMO:
        return max(conv, (r or {}).get("titular") or 0)
    return onces


def rol_por_onces(titular: int, onces: int) -> str:
    frac = titular / onces if onces else 0
    return "TF" if frac >= 0.8 else "TH" if frac >= 0.5 else "ROT" if frac >= 0.2 else "SUP"


def rol_sugerido(pct_minutos: float) -> str:
    if pct_minutos >= TF_PCT:
        return "TF"
    if pct_minutos >= TH_PCT:
        return "TH"
    if pct_minutos >= ROT_PCT:
        return "ROT"
    return "SUP"


def decisivos(plantilla: dict) -> list[dict]:
    """Los que no pueden faltar en la tabla F1: titulares habituales y los
    tres que más goles generan. Cada uno con su porqué."""
    js = plantilla.get("jugadores") or []
    # LAS STATS DE OTRO CLUB NO HACEN DECISIVO AQUÍ (incidencia 983, Cerro:
    # Mauro Villar «titular habitual (100 %)» por su temporada anterior en
    # Huracán, recién llegado y titular 0 de 10)
    if plantilla.get("origenTemporada") == "anterior":
        js = [j for j in js if not j.get("recienLlegado")]
    fuera: dict[int, dict] = {}
    for j in js:
        if j["minutos"] >= DECISIVO_MIN_MINUTOS and j["pctMinutos"] >= DECISIVO_PCT:
            fuera[j["id"]] = {**j, "porQue": f"titular habitual ({round(j['pctMinutos'] * 100)} % de los minutos)",
                              "porTitular": True}
    ofensivos = sorted((j for j in js if j["goles"] + j["asistencias"] >= DECISIVO_GA),
                       key=lambda j: -(j["goles"] + j["asistencias"]))[:3]
    for j in ofensivos:
        motivo = f"{j['goles']} goles y {j['asistencias']} asistencias"
        if j["id"] in fuera:
            fuera[j["id"]]["porQue"] += f" · {motivo}"
            fuera[j["id"]]["porGoles"] = True
        else:
            fuera[j["id"]] = {**j, "porQue": motivo, "porGoles": True}
    return list(fuera.values())


# EL TITULAR HABITUAL DE LA TEMPORADA TIENE QUE SERLO HOY (incidencia 387,
# decisión del usuario 23/10/2026). E. Meza (Estudiantes) salía decisivo por el
# 81 % de los minutos de la temporada con 3 titularidades en los últimos 10
# onces, y el parte gritaba F1-DECISIVO-FUERA por un jugador que hoy rota. Con
# onces recientes, el decisivo SOLO por minutos pide ser titular en al menos la
# mitad; el que lo es por goles y asistencias sigue con la regla de antes
# (titular en alguno: un goleador que entra de cambio también decide).
DECISIVO_HOY_PCT = 0.5


def decisivo_hoy(d: dict, titular: int, onces: int) -> bool:
    if d.get("porGoles"):
        return titular > 0
    return titular >= onces * DECISIVO_HOY_PCT


def nombre_sano(nombre: str, en_hoja: str = "") -> str:
    """El nombre de la plantilla limpio; si sigue roto (un mojibake a medias
    que perdió su segundo byte no se puede reparar) y la hoja del once lo trae
    bien, manda la hoja (incidencia 352: «A. MaksimoviÄ» del Leipzig en la F1,
    21/10/2026: el cruce por nombre del parte no casaba)."""
    n = limpiar_nombre(nombre or "") or ""
    if any(m in n for m in _MARCAS_MOJIBAKE) and en_hoja and not any(m in en_hoja for m in _MARCAS_MOJIBAKE):
        return en_hoja
    return n


def _fila(j: dict) -> dict:
    return {
        "jugadorId": j["id"], "nombre": j["nombre"], "zona": _ZONA.get(j["posicion"], ""),
        "posicion": j["posicion"], "rolSugerido": rol_sugerido(j["pctMinutos"]),
        "apps": j["partidos"], "titularidades": j["titularidades"], "minutos": j["minutos"],
        "pctMinutos": j["pctMinutos"], "goles": j["goles"], "asistencias": j["asistencias"],
        "baja": j.get("baja"), "recienLlegado": j.get("recienLlegado"),
        **({"minutosIncoherentes": True} if j.get("minutosIncoherentes") else {}),
        # los ids que `deduplicar` fundió en esta fila: sin esto se perdían en la
        # tabla y el bloque F no casaba la hoja con el otro id (incidencia 582)
        **({"idsAlternos": j["idsAlternos"]} if j.get("idsAlternos") else {}),
        # fundido con iniciales distintas o sin la pila entera (incidencia 673):
        # se marca para que, si alguna vez une a dos personas, se vea y se revierta
        **({"fundidoPorInicial": True} if j.get("fundidoPorInicial") else {}),
    }


def _zona_reciente(f: dict, r: dict | None) -> None:
    """La zona de la tabla es la del ÚLTIMO once en que fue titular, si lo hay;
    la de la plantilla de la temporada queda en `zonaTemporada` cuando difiere."""
    z = _ZONA_API.get((r or {}).get("posicionHabitual") or (r or {}).get("posicionReciente") or "", "")
    if not z and not f.get("zona"):
        z = _ZONA_API.get((r or {}).get("posicionBanco") or "", "")
    if z and z != f.get("zona"):
        if f.get("zona"):
            f["zonaTemporada"] = f["zona"]
        f["zona"] = z


def _tok_jugador(nombre: str) -> list[str]:
    return _id.tokens(nombre)


# la regla vive en backend/identidad.py (30/10/2026)
mismo_jugador = _id.mismo_jugador


def _sin_minutos(j: dict) -> bool:
    return not j.get("minutos") and not j.get("partidos")


def _mismas_stats(a: dict, b: dict) -> bool:
    """Los mismos partidos y minutos (> 0) en la temporada: la API duplicó el
    registro entero. Pasto (20/10/2026, 194): dos «S. Córdoba» (538162 y 64215)
    con las mismas stats, los dos decisivos."""
    return bool(a.get("minutos")) and (a.get("partidos"), a.get("minutos")) == (b.get("partidos"), b.get("minutos"))


def _mismo_nombre_completo(uno: str, otro: str) -> bool:
    """El MISMO nombre completo, con la pila entera (no una inicial): «Wesley
    Natã» / «Wesley Nata». «T. Palacios» con «T. Palacios» no alcanza: con la
    inicial sola pueden ser dos personas (incidencia 386)."""
    a, b = _tok_jugador(uno), _tok_jugador(otro)
    return len(a) >= 2 and len(a[0]) > 1 and (a == b or (all(len(t) > 1 for t in a + b) and sorted(a) == sorted(b)))


def _sumar(q: dict, j: dict) -> dict:
    """Las dos filas de la misma persona en una: minutos, partidos y goles se
    suman (la API los partió entre los dos ids)."""
    out = dict(q)
    for k in ("minutos", "partidos", "titularidades", "goles", "asistencias"):
        out[k] = (q.get(k) or 0) + (j.get(k) or 0)
    out["pctMinutos"] = round(min(1.0, (q.get("pctMinutos") or 0) + (j.get("pctMinutos") or 0)), 3)
    if j.get("minutosIncoherentes"):
        out["minutosIncoherentes"] = True
    out["idsAlternos"] = [*(q.get("idsAlternos") or []), j["id"]]
    return out


def _mismo_apellido(uno: str, otro: str) -> bool:
    """El mismo apellido (o con una letra cambiada) con la pila en INICIAL en
    al menos uno: «J. Bisanz» / «F. Bisanz». Dos pilas enteras distintas
    («Juan Bisanz» / «Pedro Bisanz») son dos personas, hermanos incluidos."""
    a, b = _tok_jugador(uno), _tok_jugador(otro)
    return (len(a) >= 2 and len(b) >= 2 and (len(a[0]) == 1 or len(b[0]) == 1)
            and a[0].isalpha() and b[0].isalpha()
            and (a[-1] == b[-1] or _casi_igual(a[-1], b[-1])))


def _mismos_ga(a: dict, b: dict) -> bool:
    """Los mismos goles y asistencias, y no cero: la API partió el registro."""
    ga = ((a.get("goles") or 0), (a.get("asistencias") or 0))
    return sum(ga) > 0 and ga == ((b.get("goles") or 0), (b.get("asistencias") or 0))


def _misma_ficha(a: dict, b: dict) -> bool:
    """La misma edad y la misma posición, las dos conocidas."""
    return (a.get("edad") is not None and a.get("edad") == b.get("edad")
            and bool(a.get("posicion")) and a.get("posicion") == b.get("posicion"))


def _sombra(j: dict) -> bool:
    """El registro roto de la API: 0 partidos con minutos en la temporada
    («Juan Bizans» 406291, 0 PJ y 1.359 minutos)."""
    return not j.get("partidos") and bool(j.get("minutos"))


def _alguna_vez_juntos(q: dict, j: dict, juntos) -> bool:
    """¿El id nuevo compartió hoja con la fila o con alguno de los ids que ya fundió?"""
    return any(juntos(j["id"], x) for x in [q["id"], *(q.get("idsAlternos") or [])])


def _se_alternan(q: dict, j: dict, alternan) -> bool:
    return bool(alternan) and not _arquero_y_no(q, j) and alternan(j["id"], q["id"])


def _sombra_sin_hojas(q: dict, j: dict, sin_hojas) -> bool:
    """¿Uno de los dos es la SOMBRA de la API —0 partidos con minutos— y nunca
    figuró en una hoja de partido? Huracán (30/10/2026, incidencia 904): «J.
    Bisanz» 304371 (el id de los onces, 6 de 10), «F. Bisanz» 304389 y «Juan
    Bizans» 406291 (0 PJ y 1.359 minutos, sin una sola hoja) salían como tres
    filas. Sin hojas, la sucesión no se puede medir; el registro roto sin hojas
    con el mismo apellido y la pila compatible es el de la temporada de la
    misma persona."""
    return bool(sin_hojas) and ((_sombra(q) and sin_hojas(q["id"])) or (_sombra(j) and sin_hojas(j["id"])))


HOJAS_ALTERNAN = 6   # hojas entre los dos ids para que «nunca juntos» sea evidencia


def _arquero_y_no(q: dict, j: dict) -> bool:
    """Un arquero y uno de campo con el mismo nombre son dos personas."""
    g = [x.get("posicion") == "Portero" for x in (q, j) if x.get("posicion")]
    return len(g) == 2 and g[0] != g[1]


def _caben(q: dict, j: dict, tope: int | None) -> bool:
    """¿Los partidos de los dos registros SUMADOS caben en los que jugó el
    equipo? Un registro partido reparte los partidos de UNA persona; si la suma
    pasa de los partidos del equipo, se pisan y son dos personas (Junior,
    27/10/2026, incidencia 741: «J. Peña» 13803 con 33 PJ y 538301 con 25 daban
    58 PJ y 4.605 minutos en una temporada que nadie del plantel pasa de 40).
    Sin tope conocido, no se juzga."""
    return tope is None or (q.get("partidos") or 0) + (j.get("partidos") or 0) <= tope


def deduplicar(js: list[dict], tit: dict[int, int], juntos=None, sucesion=None,
               tope: int | None = None, sin_hojas=None, alternan=None) -> tuple[list[dict], dict[int, int]]:
    """UN JUGADOR CON DOS IDS ES UNO. La API da a veces dos ids para la misma
    persona: el de la temporada, con sus minutos, y una copia vacía creada por
    una hoja del partido (Leones del Norte con «E. Griffa» 566349 y «Emiliano
    Griffa» 362224, Nacional Potosí con «S. Peña»/«S. Pena», 12 incidencias del
    17-19/10/2026). La copia salía en la tabla F1, Cowork la copiaba, y como no
    figuraba en la hoja del partido el bloque F la contaba como BAJA e inflaba
    el IP con un fantasma. Solo se funde una copia SIN MINUTOS en la temporada
    con su gemela: dos jugadores con minutos y el mismo nombre pueden ser dos
    personas, y esos quedan. Las titularidades de los últimos onces se suman
    en el id que queda.

    DOS CON MINUTOS Y EL MISMO NOMBRE COMPLETO SON UNO (incidencia 381,
    decisión del usuario 23/10/2026): «Wesley Natã» 515671 (71') y «Wesley
    Nata» 568706 (39') del Fluminense, el FACTOR-X del parte con los minutos
    partidos en dos filas. Se funden si la pila es entera (no una inicial) y
    nunca estuvieron en la misma hoja de partido (`juntos(a, b)`: dos ids en
    el mismo once o banco son dos personas). Los minutos se suman y el otro id
    queda en `idsAlternos`.

    CON INICIALES DISTINTAS O SIN LA PILA ENTERA TAMBIÉN (incidencias 619, 667
    y 673, decisión del usuario 27/10/2026): «J. Bisanz» 304371 (el titular
    habitual) y «F. Bisanz» 304389 (el id con que la hoja lo trae de titular)
    salían como dos, y uno de BAJA inflaba la reducción del ataque de Huracán
    al 40 %; «S. Córdoba» con dos ids sumaba sus goles dos veces. Se funden con
    minutos en los dos solo si se cumplen las tres: el mismo apellido, NUNCA en
    la misma hoja de partido, y o uno deja de aparecer cuando aparece el otro
    (`sucesion(a, b)`: las hojas de uno terminan antes de que empiecen las del
    otro) o tienen los mismos goles y asistencias (no cero). No se pide la
    misma posición (Bisanz es delantero en un id y mediocampista en el otro).
    La fila queda marcada `fundidoPorInicial`.

    Y NUNCA SE SUMA SI LA SUMA NO CABE (`tope`, los partidos del equipo en la
    temporada; incidencia 741): los dos registros se PISAN, cuentan los mismos
    partidos. Pero el mismo nombre (la tilde no cuenta), la misma edad y la
    misma posición, nunca en la misma hoja, es la MISMA persona que la API
    duplicó con estadísticas superpuestas, no dos (30/10/2026, incidencias 839
    y 724: «Y. Guzmán» 13491 con 37 PJ y «Y. Guzman» 531423 con 30 en el
    América, 27 años, delanteros, los dos decisivos; el «J. Peña»/«J. Pena» de
    la 741 era lo mismo, 26 años y defensas): se queda la fila con más minutos,
    SIN sumar, y la otra deja su id en `idsAlternos` (`superpuesto`).

    LA SOMBRA SIN HOJAS (31/10/2026, incidencia 904): en las dos reglas de la
    inicial, la sucesión se puede reemplazar por `_sombra_sin_hojas` —uno de
    los dos registros tiene 0 partidos con minutos y nunca figuró en una hoja
    (`sin_hojas(id)`)—: Juan Bizans / J. Bisanz / F. Bisanz de Huracán.

    Y LOS QUE SE ALTERNAN (31/10/2026, el mismo caso en producción): Juan
    Francisco Bisanz figuró en las hojas como 304371 (mayo a octubre), 406291
    (julio-agosto, en medio) y 304389 (desde el 15/10), nunca dos a la vez. No
    es una sucesión limpia, pero dos personas distintas del mismo plantel
    comparten alguna hoja (once o banco) en `HOJAS_ALTERNAN` hojas: con ese
    total entre los dos y nunca juntos, es la misma (`alternan(a, b)`). Un
    arquero y uno de campo no se funden nunca por esta vía."""
    tit = dict(tit)
    quedan: list[dict] = []
    for j in sorted(js, key=lambda j: (_sin_minutos(j), -(j.get("minutos") or 0), -tit.get(j["id"], 0))):
        gemela, sumar = None, False
        for i, q in enumerate(quedan):
            if not mismo_jugador(j["nombre"], q["nombre"]):
                if (_mismo_apellido(j["nombre"], q["nombre"]) and not _sin_minutos(j) and juntos
                        and _caben(q, j, tope) and not _alguna_vez_juntos(q, j, juntos)
                        and ((sucesion and sucesion(j["id"], q["id"])) or _mismos_ga(j, q)
                             or _sombra_sin_hojas(q, j, sin_hojas) or _se_alternan(q, j, alternan))):
                    gemela, sumar = q, True
                    quedan[i] = {**_sumar(q, j), "fundidoPorInicial": True}
                    break
                continue
            if _sin_minutos(j) or _mismas_stats(j, q):
                gemela = q
                break
            if (_mismo_nombre_completo(j["nombre"], q["nombre"]) and _caben(q, j, tope)
                    and not (juntos and juntos(j["id"], q["id"]))):
                gemela, sumar = q, True
                quedan[i] = _sumar(q, j)
                break
            # misma inicial pero sin la pila entera («M. Perea» y «M. Perea»): la misma
            # regla de la inicial distinta (sucesión o mismos goles y asistencias)
            if (juntos and _caben(q, j, tope) and not _alguna_vez_juntos(q, j, juntos)
                    and ((sucesion and sucesion(j["id"], q["id"])) or _mismos_ga(j, q)
                         or _sombra_sin_hojas(q, j, sin_hojas) or _se_alternan(q, j, alternan))):
                gemela, sumar = q, True
                quedan[i] = {**_sumar(q, j), "fundidoPorInicial": True}
                break
            # 839/724: la suma no cabe, pero la misma edad y posición, nunca juntos:
            # la API duplicó a la persona con estadísticas superpuestas; no se suma
            if (juntos and not _caben(q, j, tope) and not juntos(j["id"], q["id"])
                    and _misma_ficha(j, q)):
                quedan[i] = {**q, "superpuesto": True}
                gemela = quedan[i]
                break
        if gemela is None:
            quedan.append(j)
            continue
        # la copia que se descarta deja su id en la que queda: la hoja del
        # partido puede nombrarla con ESE id (Pasto, «S. Cordoba» 538162 contra
        # «S. Córdoba» 64215 con las mismas stats, incidencia 423)
        if not sumar:
            k = next(i for i, q in enumerate(quedan) if q is gemela)
            quedan[k] = {**gemela, "idsAlternos": [*(gemela.get("idsAlternos") or []), j["id"]]}
            gemela = quedan[k]
        tit[gemela["id"]] = tit.get(gemela["id"], 0) + tit.pop(j["id"], 0)
    return quedan, tit


def marcar_posibles(filas: list[dict], juntos) -> None:
    """DOS FILAS QUE PUEDEN SER LA MISMA PERSONA y los datos no alcanzan para
    fundirlas (31/10/2026, incidencias 887, 893 y 932): el mismo nombre (o el
    mismo apellido con una inicial) y NUNCA en la misma hoja de partido, pero
    sin sucesión ni los mismos goles. Se marcan las dos con `posibleMismoQue`:
    el bloque F no cuenta a una de baja si la otra jugó, y el parte no las
    suma dos veces. Dos que compartieron una hoja son dos personas (los dos
    «T. Palacios» de Estudiantes, defensa y volante) y no se marcan."""
    con_id = [f for f in filas if f.get("jugadorId") is not None]
    for i, a in enumerate(con_id):
        alt_a = {a["jugadorId"], *(a.get("idsAlternos") or [])}
        for b in con_id[i + 1:]:
            if b["jugadorId"] in alt_a or a["jugadorId"] in (b.get("idsAlternos") or []):
                continue
            if "posibleMismoQue" in a or "posibleMismoQue" in b:
                continue
            if not (mismo_jugador(a.get("nombre") or "", b.get("nombre") or "")
                    or _mismo_apellido(a.get("nombre") or "", b.get("nombre") or "")):
                continue
            if juntos(a["jugadorId"], b["jugadorId"]):
                continue
            a["posibleMismoQue"], b["posibleMismoQue"] = b["jugadorId"], a["jugadorId"]


def nunca_juntos(a: int, b: int) -> bool:
    """¿Consta que los dos ids NUNCA estuvieron en la misma hoja? Sin fichas en la
    base no consta nada: False (no se afirma lo que no se sabe)."""
    try:
        return not saddb.query(
            "sad", "SELECT 1 FROM alineaciones x JOIN alineaciones y ON x.fixture_id = y.fixture_id "
                   "AND x.team_id = y.team_id WHERE x.player_id=? AND y.player_id=? LIMIT 1", (a, b))
    except Exception:  # noqa: BLE001 — sin fichas no consta: no se marca ni se protege
        return False


def _juntos(a: int, b: int) -> bool:
    """¿Estuvieron los dos ids en la misma hoja de partido (once o banco)?"""
    try:
        return bool(saddb.query(
            "sad", "SELECT 1 FROM alineaciones x JOIN alineaciones y ON x.fixture_id = y.fixture_id "
                   "AND x.team_id = y.team_id WHERE x.player_id=? AND y.player_id=? LIMIT 1", (a, b)))
    except Exception:  # noqa: BLE001 — sin fichas: el nombre completo decide
        return False


def _alternan(a: int, b: int, team_id: int) -> bool:
    """Los dos ids tienen hojas CON ESTE EQUIPO y entre los dos suman
    `HOJAS_ALTERNAN` o más (las de otro club no cuentan: un fichaje con 30
    hojas en su club anterior y un juvenil homónimo no son evidencia). Que
    nunca estuvieron juntos lo mira quien llama."""
    try:
        n = {r["player_id"]: r["n"] for r in saddb.query(
            "sad", "SELECT player_id, COUNT(*) AS n FROM alineaciones WHERE player_id IN (?, ?) AND team_id=? "
                   "GROUP BY player_id", (a, b, team_id))}
    except Exception:  # noqa: BLE001 — sin fichas no hay evidencia de alternancia
        return False
    return bool(n.get(a)) and bool(n.get(b)) and n[a] + n[b] >= HOJAS_ALTERNAN


def _sin_hojas(pid: int) -> bool:
    """¿El id nunca figuró en una hoja de partido (once o banco)?"""
    try:
        return not saddb.query("sad", "SELECT 1 FROM alineaciones WHERE player_id=? LIMIT 1", (pid,))
    except Exception:  # noqa: BLE001 — sin fichas no se afirma que no tenga hojas
        return False


def _sucesion(a: int, b: int) -> bool:
    """¿Uno de los dos ids dejó de aparecer en las hojas cuando apareció el
    otro? Las fechas de sus hojas (once o banco) no se cruzan. Sin hojas de
    alguno de los dos, no se puede decir: no."""
    try:
        fechas = {}
        for pid in (a, b):
            fila = saddb.query_one(
                "sad", "SELECT MIN(f.date) AS desde, MAX(f.date) AS hasta FROM alineaciones x "
                       "JOIN fixtures f ON f.id = x.fixture_id WHERE x.player_id=?", (pid,))
            if not fila or not fila["desde"]:
                return False
            fechas[pid] = (str(fila["desde"]), str(fila["hasta"]))
    except Exception:  # noqa: BLE001 — sin fichas no hay sucesión que mostrar
        return False
    (da, ha), (db_, hb) = fechas[a], fechas[b]
    return ha < db_ or hb < da


def _partidos_temporada(team_id: int, temporada) -> int | None:
    """Los partidos terminados del equipo en esa temporada (todas las
    competiciones de la base). Sin temporada o sin partidos: None (no se juzga)."""
    if not temporada:
        return None
    try:
        fila = saddb.query_one(
            "sad", f"SELECT COUNT(*) AS n FROM fixtures f WHERE (f.home_team_id=? OR f.away_team_id=?) "
                   f"AND f.league_season=? AND {_FIN}", (team_id, team_id, temporada))
    except Exception:  # noqa: BLE001
        return None
    return (fila["n"] or None) if fila else None


def _con_sanciones(t: dict, sanc: dict | None) -> dict:
    """LA SANCIÓN DE LA BASE EN LA TABLA (30/10/2026, incidencias 772, 778 y
    835): cada fila del sancionado lleva `sancion` y el lado trae la lista
    entera en `sancionados` (también los que quedaron fuera del corte) y las
    amarillas que lleva cada uno en la competición."""
    if not sanc:
        return t
    por_id = {s["jugadorId"]: s for s in sanc.get("sancionados") or [] if s.get("jugadorId")}
    amar = {a["jugadorId"]: a["amarillas"] for a in sanc.get("amarillas") or [] if a.get("jugadorId")}
    for f in t["candidatos"]:
        ids = [f["jugadorId"], *(f.get("idsAlternos") or [])]
        s_ = next((por_id[i] for i in ids if i in por_id), None)
        if s_ is None:
            s_ = next((x for x in sanc.get("sancionados") or [] if not x.get("jugadorId")
                       and mismo_jugador(x.get("nombre") or "", f["nombre"])), None)
        if s_ is not None:
            f["sancion"] = s_
        n = sum(amar.get(i, 0) for i in ids)
        if n:
            f["amarillasEnLaCompeticion"] = n
    t["sancionados"] = sanc.get("sancionados") or []
    if sanc.get("regla"):
        t["reglaAmarillas"] = sanc["regla"]
    if sanc.get("conteoParcial"):
        t["amarillasConteoParcial"] = sanc["conteoParcial"]
    return t


def tabla_equipo(team_id: int, nombre: str, antes: str = "9999") -> dict:
    p = jug.plantilla_de(team_id)
    js = p.get("jugadores") or []
    dec = {d["id"]: d["porQue"] for d in decisivos(p)}
    rec = onces_recientes(team_id, antes)
    con_onces = rec["onces"] >= ONCES_MINIMOS
    tit = {pid: j["titular"] for pid, j in rec["jugadores"].items()}
    js, tit = deduplicar(js, tit, _juntos, _sucesion, _partidos_temporada(team_id, p.get("temporada")), _sin_hojas,
                         lambda a, b: _alternan(a, b, team_id))
    otro = juegan_en_otro(team_id, [j["id"] for j in js], antes)
    idos = [{"jugadorId": j["id"], "nombre": j["nombre"], **otro[j["id"]]} for j in js if j["id"] in otro]
    js = [j for j in js if j["id"] not in otro]
    # DECISIVO DE LA TEMPORADA, NO DE HOY. Elvio Vera (Ameliano) y Martín Arias
    # (Cerro) salían «titular habitual 100 %» por el Apertura con 0 de 10 en los
    # últimos onces (incidencia 45): con onces recientes, quien no fue titular
    # en ninguno no es un decisivo que no pueda faltar. Viaja aparte, como dato.
    de_temporada = {}
    if con_onces:
        por_dec = {d["id"]: d for d in decisivos(p)}
        for pid in [p for p in dec if not decisivo_hoy(por_dec.get(p, {}), tit.get(p, 0), rec["onces"])]:
            de_temporada[pid] = dec.pop(pid)
        # EL QUE SIGUE DECISIVO SOLO POR GOLES no se anuncia «titular habitual»
        # (incidencia 747, ADT: J. Bauman ROT con 4 de 10 y «titular habitual
        # (84 % de los minutos) · 5 goles» a la vez). El motivo de hoy son los
        # goles; los minutos de la temporada quedan dichos aparte.
        for pid in list(dec):
            d = por_dec.get(pid, {})
            if d.get("porTitular") and d.get("porGoles") and tit.get(pid, 0) < rec["onces"] * DECISIVO_HOY_PCT:
                goles = dec[pid].split(" · ", 1)[1] if " · " in dec[pid] else dec[pid]
                dec[pid] = f"{goles} (titular habitual en la temporada, hoy {tit.get(pid, 0)}/{rec['onces']})"
    # con onces recientes, el orden y el rol salen de ahí; la temporada desempata
    if con_onces:
        js = sorted(js, key=lambda j: (-tit.get(j["id"], 0), -j["minutos"]))
    elegidos = js[:CANDIDATOS]
    ids = {j["id"] for j in elegidos}
    # EL ÚLTIMO ONCE ENTRA ENTERO (20/10/2026: Battaglia y Ayrton Costa en Boca,
    # Dayan Pérez en Cúcuta, titulares —y goleadores— del último partido, se
    # quedaban fuera del corte de 16 porque las stats de la temporada van atrasadas)
    ultimo = {pid for pid, r in rec["jugadores"].items() if r.get("enUltimo")}
    # un titular del último once con otro id (la copia vacía que fundió deduplicar)
    # marca a su gemela de la temporada
    vivos = {j["id"] for j in js}
    for pid in [p for p in ultimo if p not in vivos]:
        gem = next((j for j in js if mismo_jugador(rec["jugadores"][pid]["nombre"], j["nombre"])), None)
        if gem is not None:
            ultimo.add(gem["id"])
    # TAMBIÉN EL DECISIVO DE LA TEMPORADA QUE HOY NO ES TITULAR (incidencias 501,
    # 515, 517: Lucas Moura que vuelve de la lesión, F. Romero con el 100 % de
    # los minutos, Corulo top 3 en goles) —va con su `decisivoTemporada`, sin
    # «decisivo»— y EL QUE DECIDE DESDE EL BANCO (382: gol o asistencia en los
    # onces mirados sin ser titular fijo)
    banco = {pid for pid, r in rec["jugadores"].items() if r.get("gaRecientes")}
    elegidos += [j for j in js if j["id"] not in ids
                 and (j["id"] in dec or j["id"] in ultimo or j["id"] in de_temporada or j["id"] in banco)]
    filas = []
    for j in elegidos:
        f = {**_fila(j), "decisivo": dec.get(j["id"], "")}
        if j["id"] in de_temporada:
            f["decisivoTemporada"] = (f"{de_temporada[j['id']]} · titular en {tit.get(j['id'], 0)} de "
                                      f"{rec['onces']} de los últimos onces")
        if con_onces:
            r_j = rec["jugadores"].get(j["id"])
            f["titularEnUltimos"] = f"{tit.get(j['id'], 0)}/{rec['onces']}"
            disp = onces_disponible(r_j, rec["onces"])
            f["rolSugerido"] = rol_por_onces(tit.get(j["id"], 0), disp)
            if disp != rec["onces"]:
                f["enLaHoja"] = f"{disp}/{rec['onces']}"
            if (r_j or {}).get("gaRecientes"):
                f["gaRecientes"] = r_j["gaRecientes"]
        if j["id"] in ultimo:
            f["titularEnElUltimo"] = True
        _zona_reciente(f, rec["jugadores"].get(j["id"]))
        # EL NOMBRE DE LA HOJA, SI ES OTRO. La base tiene al 555163 como «D. Gelvez»
        # y la alineación como «Dayan Pérez» (Cúcuta, 20/10/2026, 335): sin esto, el
        # parte lo sumaba dos veces y la fila de prensa salía de baja
        en_hoja = (rec["jugadores"].get(j["id"]) or {}).get("nombre") or ""
        f["nombre"] = nombre_sano(f["nombre"], en_hoja)
        # …solo si NINGUNA hoja lo nombra como la plantilla: una hoja que la API
        # nombró con otro jugador no le cambia la identidad (610)
        hojas = (rec["jugadores"].get(j["id"]) or {}).get("nombres") or {en_hoja}
        if en_hoja and not any(h and (mismo_jugador(h, j["nombre"])
                                      or normalizar_simple(h) == normalizar_simple(j["nombre"])) for h in hojas):
            f["nombreEnLaHoja"] = en_hoja
        filas.append(f)
    # titulares recientes que la plantilla de la temporada no tiene (fichajes,
    # juveniles subidos): sin ellos la tabla se queda con el equipo de antes
    ids = {j["id"] for j in elegidos}
    por_id = {j["id"]: j for j in js}
    # …también con menos de ONCES_MINIMOS onces (incidencia 1008, Willem II con
    # 4: el arquero titular del 24/10 quedaba fuera porque el rol sale de los
    # minutos de la temporada); con pocos, solo los titulares de los últimos 3
    if rec["onces"]:
        for pid, r in sorted(rec["jugadores"].items(), key=lambda kv: -kv[1]["titular"]):
            if not con_onces and not r.get("enUltimos3"):
                continue
            # TITULAR EN UNO DE LOS ÚLTIMOS 3 ONCES (31/10/2026, incidencia 683,
            # decisión del usuario): Bruno Gonçalves Baldini (Athletico), Diogo
            # Leite (Lazio) y Labrador (Huancayo) no estaban en la plantilla de la
            # API ni en la F1 siendo titulares recientes
            if pid in ids or pid <= 0 or (r["titular"] < 2 and not r.get("enUltimo") and not r.get("enUltimos3")):
                continue
            # YA FUNDIDO POR `deduplicar`: sus titularidades ya están en la fila
            # que lo lleva en `idsAlternos`. Sumarlas otra vez daba «12/9»
            # (Metropolitanos, I. Ramírez 406623 + 554584, incidencia 627)
            if any(pid in (f.get("idsAlternos") or []) for f in filas):
                continue
            # QUEDÓ FUERA DEL CORTE PERO ESTÁ EN LA PLANTILLA: entra con sus stats
            # (Ambríz, 16 PJ y 6 titularidades, salía «sin stats de temporada»,
            # incidencia 360)
            if pid in por_id:
                f = {**_fila(por_id[pid]), "decisivo": dec.get(pid, ""),
                     "titularEnUltimos": f"{tit.get(pid, 0)}/{rec['onces']}",
                     "rolSugerido": rol_por_onces(tit.get(pid, 0), onces_disponible(r, rec["onces"])),
                     **({"titularEnElUltimo": True} if r.get("enUltimo") else {})}
                f["nombre"] = nombre_sano(f["nombre"], r["nombre"])
                _zona_reciente(f, r)
                filas.append(f)
                ids.add(pid)
                continue
            # el mismo jugador con otro id en la hoja: sus titularidades ya
            # cuentan en la fila de la plantilla, no es un fichaje
            # …y su id de la hoja va a `idsAlternos`, para que el bloque F lo case
            # con ese id (incidencias 462, 497, 582: Portuguesa, Carabobo, Rio
            # Ave, Inter de Bogotá, Valencia con R. Sato). Si su gemela de la
            # plantilla había quedado fuera del corte, entra con sus stats.
            gemela = next((f for f in filas if mismo_jugador(r["nombre"], f["nombre"])
                           and not _juntos(pid, f["jugadorId"])), None)
            if gemela is None:
                plant = next((j for j in js if j["id"] not in ids and mismo_jugador(r["nombre"], j["nombre"])
                              and not _juntos(pid, j["id"])), None)
                if plant is not None:
                    gemela = {**_fila(plant), "decisivo": dec.get(plant["id"], ""),
                              "titularEnUltimos": f"{tit.get(plant['id'], 0)}/{rec['onces']}"}
                    gemela["nombre"] = nombre_sano(gemela["nombre"], r["nombre"])
                    _zona_reciente(gemela, r)
                    filas.append(gemela)
                    ids.add(plant["id"])
            if gemela is not None:
                gemela["idsAlternos"] = sorted({*(gemela.get("idsAlternos") or []), pid})
                if "titularEnUltimos" in gemela:
                    # dos ids en la misma hoja no son dos titularidades (994: «10/9»)
                    t = min(tit.get(gemela["jugadorId"], 0) + r["titular"], rec["onces"])
                    tit[gemela["jugadorId"]] = t
                    gemela["titularEnUltimos"] = f"{t}/{rec['onces']}"
                    gemela["rolSugerido"] = rol_por_onces(t, onces_disponible(r, rec["onces"]))
                if r.get("enUltimo"):
                    gemela["titularEnElUltimo"] = True
                continue
            filas.append({"jugadorId": pid, "nombre": r["nombre"],
                          "zona": _ZONA_API.get(r.get("posicionReciente") or r["posicion"], ""),
                          "posicion": r["posicion"], "rolSugerido": rol_por_onces(r["titular"], rec["onces"]),
                          "titularEnUltimos": f"{r['titular']}/{rec['onces']}", "apps": None, "minutos": None,
                          "decisivo": "", "sinStatsDeTemporada": True, "fueraDePlantilla": True,
                          **({"titularEnElUltimo": True} if r.get("enUltimo") else {})})
    # DOS ARQUEROS EN LA TABLA (incidencia 986, Standard: con Epolo sancionado
    # el suplente Pirard no estaba y el bloque F no tenía a quién poner): si la
    # tabla trae menos de dos, entra el de la plantilla con más minutos
    gks = [f for f in filas if f.get("zona") == "GK"]
    if len(gks) < 2:
        en = {f["jugadorId"] for f in filas}
        extra = sorted((j for j in js if _ZONA.get(j.get("posicion") or "") == "GK" and j["id"] not in en),
                       key=lambda j: -(j.get("minutos") or 0))[:2 - len(gks)]
        for j in extra:
            f = {**_fila(j), "decisivo": "", "arqueroDeReserva": True}
            if con_onces:
                f["titularEnUltimos"] = f"{tit.get(j['id'], 0)}/{rec['onces']}"
                f["rolSugerido"] = rol_por_onces(tit.get(j["id"], 0), onces_disponible(rec["jugadores"].get(j["id"]),
                                                                                         rec["onces"]))
            filas.append(f)
    marcar_posibles(filas, lambda a, b: not nunca_juntos(a, b))
    return {
        "equipo": nombre, "teamId": team_id, "temporada": p.get("temporada"),
        "origenTemporada": p.get("origenTemporada"),
        "rolPor": (f"titularidades en los últimos {rec['onces']} onces" if con_onces else
                   f"minutos de la temporada (solo {rec['onces']} onces recientes en la base)"),
        "candidatos": filas,
        # los de la plantilla cuya última hoja es con otro club (931): fuera de la tabla
        **({"jueganEnOtroEquipo": idos} if idos else {}),
        # los que la API lista sin un minuto (recién llegados): la prensa dirá
        "plantelSinStats": p.get("plantelSinStats") or [],
        "sinDato": "" if js else "sin plantilla ingestada para este equipo: la tabla sale de la prensa",
    }


def tabla(fixture_id: int, sanc: dict | None = None) -> dict | None:
    """La tabla F1 de los dos lados. `sanc`: las sanciones ya calculadas
    (`sanciones.de_fixture`), para no rehacerlas (el escaneo)."""
    from backend.analisis.parte import _fixture
    fx = _fixture(fixture_id)
    if not fx:
        return None
    if sanc is None:
        from backend import sanciones
        sanc = sanciones.de_fixture(fixture_id)
    return {
        "fixtureId": fixture_id,
        "a": _con_sanciones(tabla_equipo(fx["home_team_id"], fx["home_name"], fx["date"]), sanc.get("a")),
        "b": _con_sanciones(tabla_equipo(fx["away_team_id"], fx["away_name"], fx["date"]), sanc.get("b")),
        "nota": ("punto de partida de la tabla F1, calculado de la temporada ingestada: copiá el "
                 "`jugadorId` (es el cruce exacto con la hoja del partido) y confirmá el rol con la "
                 "prensa —`rolSugerido` sale de los últimos onces (o de los minutos, ver `rolPor`) y no sabe de un DT nuevo ni de una "
                 "lesión larga—. Los `decisivo` no pueden faltar: si faltan, el parte avisa "
                 "F1-DECISIVO-FUERA. Los `sancionados` (roja o amarillas en el último partido de esta "
                 "competición, de la base) van en `fuera` con estado baja y motivo «sanción», salvo que la "
                 "prensa diga lo contrario: si no, el parte avisa SANCION-SIN-DECLARAR"),
    }


_casi_igual = _id.apellido_casi


def _parecido(tok_api: list[str], tok_tabla: list[str]) -> bool:
    """Último recurso, solo para AVISAR que falta alguien: la misma pila (o su
    inicial) y un apellido casi igual. Un falso «está» cuesta un aviso de
    menos; un falso «no está» manda a rehacer una tabla que estaba bien."""
    if len(tok_api) < 2 or len(tok_tabla) < 2:
        return False
    if not bloque_f._misma_pila(tok_api[0], tok_tabla[0]):
        return False
    return any(_casi_igual(a, t) for a in tok_api[1:] for t in tok_tabla[1:])


def _en_tabla(j: dict, plantel: list[dict]) -> bool:
    for p in plantel:
        if p.get("jugadorId") and int(p["jugadorId"]) == int(j["id"]):
            return True
    tok_api = bloque_f._tokens(j["nombre"])
    return any(bloque_f._casa(bloque_f._tokens(p.get("nombre") or ""), tok_api)
               or bloque_f._casa(tok_api, bloque_f._tokens(p.get("nombre") or ""))
               or _parecido(tok_api, bloque_f._tokens(p.get("nombre") or ""))
               for p in plantel)


# LOS QUE YA NO ESTÁN NO SON DECISIVOS DE HOY. Medellín (17/10/2026): la
# alerta gritaba por jugadores que se habían ido del club; las stats de la
# temporada los siguen teniendo arriba en minutos y goles. Fuera de la cuenta:
# una salida registrada del club, o ninguna convocatoria en los últimos onces
# capturados (con al menos ONCES_PARA_AUSENTE para que el silencio diga algo).
ONCES_PARA_AUSENTE = 5


OTRO_EQUIPO_DIAS = 120   # la hoja con el otro club tiene que ser de esta temporada


OTRO_EQUIPO_GAP_DIAS = 3   # menos que esto entre la hoja propia y la ajena: el mismo id para dos personas


def _dias_entre(a: str, b: str) -> int:
    try:
        return abs((datetime.fromisoformat(str(b)[:10]) - datetime.fromisoformat(str(a)[:10])).days)
    except ValueError:
        return 99


def juegan_en_otro(team_id: int, ids: list[int], antes: str = "9999") -> dict[int, dict]:
    """LOS QUE YA JUEGAN EN OTRO CLUB (31/10/2026, incidencia 931: «G. Martínez»
    36088 salía candidato de Pumas con 10 partidos y el 25/10 asistió el empate
    de Tigres). La API tarda en registrar el traspaso (`salidos` no lo veía),
    pero la hoja no: la última hoja del jugador con OTRO club, posterior a la
    última con este y de los últimos `OTRO_EQUIPO_DIAS`, dice que se fue. Las
    selecciones no cuentan (en la API se llaman como su país) y el que nunca
    jugó para este equipo (un fichaje recién llegado) tampoco. Una selección
    juvenil («Mexico U20») empieza con el nombre del país y tampoco cuenta."""
    ids = [i for i in ids if i and i > 0]
    if not ids:
        return {}
    try:
        filas = saddb.query(
            "sad", f"""SELECT x.player_id, x.team_id, t.name AS equipo, MAX(f.date) AS ultima
                       FROM alineaciones x JOIN fixtures f ON f.id = x.fixture_id
                       LEFT JOIN teams t ON t.id = x.team_id
                       WHERE x.player_id IN ({','.join('?' * len(ids))}) AND f.date < ?
                         AND (t.country IS NULL OR t.name IS NULL OR t.name NOT LIKE t.country || '%')
                       GROUP BY x.player_id, x.team_id""", (*ids, antes))
    except Exception:  # noqa: BLE001 — sin fichas: nadie se afirma ido
        return {}
    por: dict[int, dict[int, tuple[str, str]]] = {}
    for r in filas:
        por.setdefault(r["player_id"], {})[r["team_id"]] = (str(r["ultima"] or ""), r["equipo"] or "")
    out = {}
    try:
        corte = (datetime.fromisoformat(str(antes)[:10]) - timedelta(days=OTRO_EQUIPO_DIAS)).strftime("%Y-%m-%d")
    except ValueError:
        corte = ""
    for pid, eqs in por.items():
        propia = eqs.get(team_id)
        if not propia:
            continue
        otra = max(((u, e, tid) for tid, (u, e) in eqs.items() if tid != team_id), default=None)
        # DOS CLUBES EN DOS DÍAS NO ES UN TRASPASO, ES UN ID CHOCADO (incidencia
        # 961: el arquero 81224 de Kifisia, titular el 24/10, «en Leones del
        # Norte» por una hoja del 25/10 de un homónimo)
        if otra and otra[0] > propia[0] and otra[0] >= corte and _dias_entre(propia[0], otra[0]) >= OTRO_EQUIPO_GAP_DIAS:
            out[pid] = {"equipo": otra[1], "teamId": otra[2], "ultimaHoja": otra[0][:10]}
    return out


def salidos(team_id: int, antes: str = "9999") -> set[int]:
    """Jugadores con una salida registrada del club antes de `antes` (y sin
    vuelta posterior)."""
    try:
        return {r["player_id"] for r in saddb.query(
            "sad", "SELECT DISTINCT t.player_id FROM traspasos t WHERE t.team_out=? AND t.fecha < ? "
                   "AND NOT EXISTS (SELECT 1 FROM traspasos v WHERE v.player_id=t.player_id "
                   "AND v.team_in=? AND v.fecha > t.fecha)", (team_id, antes, team_id))}
    except Exception:  # noqa: BLE001 — base sin la capa de jugadores
        return set()


def faltantes(team_id: int, plantel: list[dict], antes: str = "9999") -> list[dict]:
    if not plantel:
        return []          # sin tabla F1 no hay nada que comparar (ya lo dice el bloque F)
    fuera = salidos(team_id, antes)
    rec = onces_recientes(team_id, antes)
    # con pocos onces capturados el silencio no dice nada: solo cuenta la salida
    # presente = titular en alguno de los últimos onces: convocado al banco no
    # basta para que un decisivo de la temporada sea decisivo hoy (incidencia 45)
    con_onces = rec["onces"] >= ONCES_PARA_AUSENTE
    presentes = ({pid for pid, r in rec["jugadores"].items() if r["titular"] > 0} if con_onces else None)
    out = [{"jugadorId": d["id"], "nombre": d["nombre"], "porQue": d["porQue"]}
           for d in decisivos(jug.plantilla_de(team_id))
           if d["id"] not in fuera and (presentes is None or d["id"] in presentes)
           and (not con_onces or decisivo_hoy(d, (rec["jugadores"].get(d["id"]) or {}).get("titular", 0),
                                              rec["onces"]))
           and not _en_tabla(d, plantel)]
    # EL TITULAR FIJO DE LOS ÚLTIMOS ONCES CUENTA AUNQUE LA TEMPORADA NO LO
    # TENGA. Robert Sánchez atajó para el Como (17/10/2026) y no estaba en la
    # tabla F1 ni saltó la alerta: un cedido sin stats de la temporada no era
    # «decisivo» para la plantilla, y en los onces era fijo.
    if presentes is not None:
        ya = {f["jugadorId"] for f in out}
        for pid, r in rec["jugadores"].items():
            if pid in ya or pid in fuera or pid <= 0 or r["titular"] < rec["onces"] * 0.8:
                continue
            j = {"id": pid, "nombre": r["nombre"]}
            if not _en_tabla(j, plantel):
                out.append({"jugadorId": pid, "nombre": r["nombre"],
                            "porQue": f"titular en {r['titular']} de los últimos {rec['onces']} onces"})
    return out


def alertas(parte: dict, fx, nombres: dict) -> list[dict]:
    if not fx:
        return []
    fuera = []
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        try:
            faltan = faltantes(tid, ((parte.get("equipos") or {}).get(lado) or {}).get("plantel") or [],
                               str(fx["date"]))
        except Exception:  # noqa: BLE001 — base sin la capa de jugadores
            faltan = []
        if faltan:
            fuera.append({
                "codigo": "F1-DECISIVO-FUERA", "equipo": lado, "tipo": "dato",
                "detalle": f"La tabla F1 de {nombres.get(lado, lado)} no tiene a "
                           + "; ".join(f"{f['nombre']} ({f['porQue']})" for f in faltan)
                           + ". Un jugador fuera de la tabla no pesa en el Impacto Ponderado: si no "
                             "juega, su baja no existe para el bloque F. La tabla con `jugadorId` "
                             "sale de GET /analisis/cowork/f1/{id}.",
            })
    return fuera


def alertas_sancion(parte: dict, fx, nombres: dict, sanc: dict | None = None) -> list[dict]:
    """SANCION-SIN-DECLARAR (30/10/2026, incidencias 772, 778 y 835): un
    sancionado de la base (`backend/sanciones.py`) que el parte no tiene en
    `fuera`. Se declara de baja con motivo «sanción» o la nota dice por qué
    juega (la prensa manda: una sanción levantada, una roja apelada)."""
    if not fx:
        return []
    if sanc is None:
        from backend import sanciones
        try:
            sanc = sanciones.de_fixture(fx["id"])
        except Exception:  # noqa: BLE001 — sin la base de eventos no hay inferencia
            return []
    out = []
    for lado in ("a", "b"):
        eq = (parte.get("equipos") or {}).get(lado) or {}
        fuera = eq.get("fuera") or []
        ids_fuera = {f.get("jugadorId") for f in fuera if f.get("jugadorId") is not None}
        # LA BAJA DECLARADA SIN ID CASA POR LA FILA DE LA TABLA (incidencia 969,
        # Augsburg: la base dice «Juma Bah» y el parte, sin id, «Abdulay Bah»,
        # que es el nombre de la fila 449509): el id de la fila que la nombra
        for f in fuera:
            if f.get("jugadorId") is None:
                ids_fuera |= {j.get("jugadorId") for j in eq.get("plantel") or []
                              if j.get("jugadorId") is not None and mismo_jugador(j.get("nombre") or "", f.get("nombre") or "")}
        # …y la nota del bloque se lee venga en `bloques.X.nota` o en `notas.X`
        # (incidencia 959: una pisaba a la otra y solo una apagaba la alerta)
        nt = eq.get("notas")
        notas = " ".join([str((b or {}).get("nota") or "") for b in (eq.get("bloques") or {}).values()
                          if isinstance(b, dict)]
                         + ([str(v or "") for v in nt.values()] if isinstance(nt, dict) else [str(nt or "")]))
        sin = []
        for x in (sanc.get(lado) or {}).get("sancionados") or []:
            if x.get("jugadorId") in ids_fuera or any(mismo_jugador(x.get("nombre") or "", f.get("nombre") or "")
                                                       for f in fuera):
                continue
            ape = (bloque_f._tokens(x.get("nombre") or "") or [""])[-1]
            if ape and ape in bloque_f._tokens(notas) and "sancion" in normalizar_simple(notas):
                continue        # la nota lo trata: «X juega, la sanción se apeló»
            sin.append(x)
        if sin:
            out.append({
                "codigo": "SANCION-SIN-DECLARAR", "equipo": lado, "tipo": "dato",
                "detalle": f"La base dice que en {nombres.get(lado, lado)} no juegan "
                           + "; ".join(f"{x['nombre']} ({x['detalle']})" for x in sin)
                           + ", y el parte no los tiene en `fuera`. Van de baja con motivo «sanción» (su rol "
                             "pesa en el IP) o la nota dice por qué juegan, con la fuente. Lista en "
                             "GET /analisis/cowork/f1/{id} → `sancionados`.",
                "sancionados": [{k: x.get(k) for k in ("jugadorId", "nombre", "tipo", "fecha")} for x in sin],
            })
    return out
