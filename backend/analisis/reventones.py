"""El estudio de los reventones hacia atrás (`/analisis/cowork/reventones`).

POR QUÉ. Una burbuja que revienta es el momento en que el partido dejó de
parecerse a la racha, y entender QUÉ pasó ahí —con el Teorema del Echado de
los DOS equipos, la autopsia de goles del DTP y el EFE de ese día— es lo que
nos da probabilidades propias, no las de la casa (13/10/2026, el usuario: «una
burbuja de victorias que revienta es donde el TDE brilla; y cuando un equipo
con racha negativa la rompe, hay que estudiar al rival con el TDE, porque
alguien con tan bajo rendimiento termina ganando»).

QUÉ HACE. Tres cosas, con lo que ya está en la base:

- `candidatos(...)`: los reventones que valen un estudio —burbujas de ≥ 3
  partidos, o de 2 con la K pico por encima de la mediana del equipo— en una
  liga y un período, con si hay ficha del partido (once y goles con minuto) y
  si ya están estudiados. Calculado, 0 tokens.
- `ficha(fixture, equipo)`: el reventón «al día del partido» —la burbuja y
  el nivel de los dos equipos con la historia cortada ANTES de ese partido
  (`antesDe`), la ficha táctica del partido y el DT de cada banco—. Lo que
  la base no tiene (prensa de esa fecha) lo busca quien estudia.
- `guardar_estudio(...)`: lo que concluyó el estudio, con el MECANISMO del
  reventón de una lista cerrada, las SEÑALES PREVIAS de otra lista cerrada
  (lo que se podía ver antes del pitazo) y las lecciones por skill.

LA POBLACIÓN ES `post_resultado` Y ESO NO SE DISCUTE: el caso se elige
porque ya reventó y se estudia con el marcador a la vista. Sus lecciones
FIJAN RÚBRICA y no mueven ningún número (la regla de docs/APRENDIZAJE.md), y
el resumen por mecanismo es una frecuencia descriptiva de los reventones, no
una probabilidad de que revienten: para eso falta el denominador de las
burbujas que NO reventaron, que es lo que mide el backtest.
"""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta, timezone

from backend import db as saddb
from backend.analisis import burbuja, db as efedb

TIPOS = {"+": "racha_positiva_revienta", "-": "racha_negativa_se_corta"}
MECANISMOS = {
    "echada_del_que_ganaba": "el de la racha se replegó sin control y concedió",
    "sobreexposicion_del_que_ganaba": "el de la racha se expuso de más y concedió de contra",
    "rival_se_echo": "el rival se replegó sin control y el de la racha lo aprovechó",
    "rival_se_sobreexpuso": "el rival se expuso de más y el de la racha lo castigó",
    "roja": "una expulsión cambió el partido",
    "error_arquero": "un gol pasó por un error del arquero",
    "balon_parado": "lo decidió una pelota parada",
    "penal": "lo decidió un penal",
    "rotacion_o_fatiga": "rotación, fatiga o calendario cargado",
    "cambio_dt": "un DT nuevo (propio o del rival) cambió el plan",
    "superioridad_rival": "el rival fue simplemente mejor: el nivel mandó",
    "altura": "la altura decidió: el de llano no sostuvo el ritmo a 2.500+ m (o al revés al bajar)",
    "racha_de_otra_competicion": "la racha se armó en otra competición (copa, amistosos, alternativos) y no "
                                 "representaba al equipo que jugó este partido",
    "bloque_bajo_del_rival": "el rival se cerró atrás POR PLAN desde el arranque (no una echada tras ponerse "
                             "arriba) y el de la racha no supo romperlo",
    "arquero_rival": "el arquero rival sostuvo el resultado con atajadas decisivas",
    "regresion_al_nivel": "sin un hecho que lo explique: la racha corta se cortó ante un rival de su nivel y "
                          "el equipo volvió a rendir lo suyo",
    "varianza": "sin mecanismo identificable: el partido no explica el resultado",
    "otro": "otro (se explica en notas)",
}
SENALES = {
    "dt_nuevo_propio": "el de la racha tenía DT nuevo (< 3 meses)",
    "dt_nuevo_rival": "el rival tenía DT nuevo (< 3 meses)",
    "rival_necesitado": "el rival necesitaba el resultado (descenso, clasificación, eliminatoria)",
    "rival_superior": "el rival era de nivel claramente superior",
    "rival_inferior": "el rival era de nivel claramente inferior",
    "bajas_clave": "el de la racha tenía bajas de titulares fijos",
    "bajas_clave_rival": "el rival tenía bajas de titulares fijos",
    "rotacion": "el de la racha rotó (copa, internacional cerca)",
    "fatiga_calendario": "partido a ≤ 3 días del anterior o viaje largo",
    "localia": "condición de local/visita a contramano de la racha",
    "altura": "partido en altura para uno de los dos",
    "racha_en_extremo": "la burbuja estaba en su récord o cerca (K-EXTREMO / K-CERCA)",
    "riesgo_alto": "el riesgo calculado del reventón era alto o muy alto",
    "racha_en_otra_competicion": "la mitad o más de la racha se jugó en otra competición que este partido "
                                 "(o en amistosos) — CALCULADA",
    "condicion_a_contramano": "dos tercios o más de la racha se jugaron en la condición contraria "
                              "(local/visita) a la de este partido — CALCULADA (no salta si el partido es "
                              "en su propio estadio, como un clásico de estadio compartido)",
    "rival_tambien_en_burbuja": "el rival llegaba con su propia burbuja abierta de 2+ partidos — CALCULADA",
    "racha_concediendo": "racha positiva en la que el equipo recibió gol en todos los partidos — CALCULADA",
    "derrota_internacional_reciente": "perdió un partido internacional en los 10 días previos (resaca de "
                                      "una eliminación) — CALCULADA",
    "clasico": "clásico o derbi: la paridad propia del cruce, que la regla del nivel no ve",
    "rival_directo": "rival directo en la tabla (descenso, clasificación): los dos necesitaban el resultado",
    "once_distinto": "el once del partido cambió 5 o más titulares respecto del último de la racha EN LA MISMA "
                     "competición "
                     "(se ve ~60 min antes del pitazo) — CALCULADA, solo con los dos onces en la base",
    "rival_de_otra_base": "el rival venía de otra división o de una liga que no se sigue (copa nacional), o "
                          "el equipo acaba de cambiar de categoría (ascendido/descendido): el nivel o las "
                          "medianas no están en la misma escala — CALCULADA",
    "ninguna_visible": "nada visible antes del pitazo",
}
LECCIONES_MAX = 8
SENALES_CALCULADAS = ("racha_en_otra_competicion", "condicion_a_contramano", "rival_tambien_en_burbuja",
                      "racha_concediendo", "derrota_internacional_reciente", "once_distinto", "rival_de_otra_base")
ONCE_CAMBIOS = 5         # Cienciano en Sullana (tercera tanda): 6 cambios, el alterno
DIAS_RESACA = 10
# el reventón no es un skill: sus reglas (docs/REVENTON.md) viven en sad-analysis.
# La primera tanda (13/10/2026) dejó lecciones con «reventon» como skill y el
# dossier las abría en un grupo aparte que nadie revisa.
_ALIAS_SKILL = {"reventon": "sad-analysis", "reventón": "sad-analysis", "burbuja": "sad-analysis",
                "sad": "sad-analysis"}


def skill_canonico(s: str) -> str:
    s = (s or "").strip()
    return _ALIAS_SKILL.get(s.lower(), s)
DDL = """
CREATE TABLE IF NOT EXISTS reventon_estudio (
    fixture_id   INTEGER NOT NULL,
    team_id      INTEGER NOT NULL,
    estudio_json TEXT NOT NULL,
    creado_en    TEXT NOT NULL,
    actualizado_en TEXT NOT NULL,
    PRIMARY KEY (fixture_id, team_id)
);
"""


class EstudioInvalido(ValueError):
    pass


def _conectar():
    con = efedb.conectar()
    con.executescript(DDL)
    return con


def _app():
    from backend import app as sadapp   # constantes_de / niveles_de / get_fixture
    return sadapp


# ── los candidatos ──────────────────────────────────────────────────────────

def _equipos_de_liga(liga_id: int, desde: str) -> list[int]:
    filas = saddb.query(
        "sad", "SELECT DISTINCT home_team_id AS t FROM fixtures WHERE league_id=? AND date>=? "
               "UNION SELECT DISTINCT away_team_id FROM fixtures WHERE league_id=? AND date>=?",
        (liga_id, desde, liga_id, desde))
    return [f["t"] for f in filas]


def _con_ficha(fixture_id: int) -> dict:
    try:
        ev = saddb.query_one("sad", "SELECT COUNT(*) AS n FROM fixture_eventos WHERE fixture_id=?",
                             (fixture_id,))["n"]
        xi = saddb.query_one("sad", "SELECT COUNT(*) AS n FROM alineaciones WHERE fixture_id=? AND titular=1",
                             (fixture_id,))["n"]
    except Exception:  # noqa: BLE001 — base sin las tablas de la ficha
        ev = xi = 0
    return {"eventos": ev > 0, "once": xi >= 20}


def significativo(r: dict, medianas: dict) -> bool:
    """≥ 3 partidos, o 2 con la K pico por encima de la mediana de su signo.
    Las de un partido son ruido: la K salta y vuelve sin que haya racha."""
    if r["partidos"] >= 3:
        return True
    med = medianas.get(r["signo"])
    return r["partidos"] >= 2 and med is not None and r["kPico"] >= med


def _ligas_ruido() -> set[int]:
    try:
        from backend.ingesta.extractor import LIGAS_RUIDO
        return set(LIGAS_RUIDO)
    except Exception:  # noqa: BLE001
        return {667}


def composicion(racha: list[dict], fila: dict, previas: list[dict] | None = None,
                en_su_estadio: bool = False) -> dict:
    """De qué estaba hecha la racha, contra el partido que la cerró. Las dos
    señales que se repitieron en la primera tanda de Perú (13/10/2026) y que la
    base sabe sola: rachas armadas en la Copa de la Liga o en amistosos durante
    la pausa que reventaron al volver la liga (Alianza Lima, Huancayo, Cienciano,
    Alianza Atlético), y rachas de local que revientan de visita."""
    ruido = _ligas_ruido()
    otra = [f for f in racha if f.get("ligaId") != fila.get("ligaId") or f.get("ligaId") in ruido]
    contra = [f for f in racha if f.get("condicion") != fila.get("condicion")]
    n = len(racha) or 1
    senales = []
    if len(otra) * 2 >= n and racha:
        senales.append("racha_en_otra_competicion")
    # en su propio estadio (Cienciano–Garcilaso comparten el Inca Garcilaso)
    # la visita es nominal: ni viaje ni altura (segunda tanda, 13/10/2026)
    # (solo cuenta si figura de VISITA: de local en su estadio es lo normal y la
    # racha de visita a contramano sí pesa — Cristal 2-0 JP2, tercera tanda)
    if len(contra) * 3 >= 2 * n and racha and not (en_su_estadio and fila.get("condicion") == "Visita"):
        senales.append("condicion_a_contramano")
    # una racha de victorias que concede en todos los partidos es frágil
    # (Universitario 3-2 y 4-2 antes del 2-2 con Comerciantes)
    signo = "+" if racha and all((f.get("golesFavor") or 0) >= (f.get("golesContra") or 0) for f in racha) else ""
    if signo and len(racha) >= 2 and all((f.get("golesContra") or 0) > 0 for f in racha):
        senales.append("racha_concediendo")
    # la resaca de una eliminación continental (Cienciano tras Torque: ADT y Chankas)
    try:
        hoy = datetime.fromisoformat(str(fila["fecha"]).replace("Z", "+00:00"))
        for f in previas or []:
            d = datetime.fromisoformat(str(f["fecha"]).replace("Z", "+00:00"))
            if (f.get("esInternacional") and 0 < (hoy - d).days <= DIAS_RESACA
                    and (f.get("golesFavor") or 0) < (f.get("golesContra") or 0)):
                senales.append("derrota_internacional_reciente")
                break
    except (KeyError, ValueError, TypeError):
        pass
    return {
        "partidos": [{"fixtureId": f["fixtureId"], "fecha": str(f["fecha"])[:10], "ligaId": f.get("ligaId"),
                      "condicion": "L" if f.get("condicion") == "Local" else "V",
                      "resultado": f"{f.get('golesFavor')}-{f.get('golesContra')}",
                      "amistoso": f.get("ligaId") in ruido} for f in racha],
        "enOtraCompeticion": len(otra), "aContramano": len(contra),
        "ligaDelReventon": fila.get("ligaId"),
        "senalesCalculadas": senales,
    }


def cambios_en_el_once(fixture_id: int, team_id: int, previo_id: int) -> int | None:
    """Cuántos titulares de este partido no fueron titulares en `previo_id`.
    `None` si falta alguno de los dos onces: sin dato no es «sin cambios»."""
    try:
        filas = saddb.query("sad", "SELECT fixture_id, player_id FROM alineaciones WHERE team_id=? AND titular=1 "
                                   "AND fixture_id IN (?,?)", (team_id, fixture_id, previo_id))
    except Exception:  # noqa: BLE001 — base sin la tabla de alineaciones
        return None
    hoy = {f["player_id"] for f in filas if f["fixture_id"] == fixture_id}
    antes = {f["player_id"] for f in filas if f["fixture_id"] == previo_id}
    if len(hoy) < 11 or len(antes) < 11:
        return None
    return len(hoy - antes)


def _sede_propia(team_id: int):
    """El estadio donde más juega de local (venue_id más frecuente)."""
    try:
        f = saddb.query_one("sad", "SELECT venue_id, COUNT(*) AS n FROM fixtures WHERE home_team_id=? "
                                   "AND venue_id IS NOT NULL GROUP BY venue_id ORDER BY n DESC LIMIT 1", (team_id,))
    except Exception:  # noqa: BLE001
        return None
    return f["venue_id"] if f else None


def _sede_de(fixture_id: int):
    try:
        f = saddb.query_one("sad", "SELECT venue_id FROM fixtures WHERE id=?", (fixture_id,))
    except Exception:  # noqa: BLE001
        return None
    return f["venue_id"] if f else None


def reventones_de(team_id: int) -> list[dict]:
    filas = list(reversed(_app().constantes_de(team_id, 2000)))
    cerrados, _, _ = burbuja.episodios(filas, "total")
    medianas = {s: statistics.median([r["kPico"] for r in cerrados if r["signo"] == s])
                for s in ("+", "-") if any(r["signo"] == s for r in cerrados)}
    pos = {f["fixtureId"]: i for i, f in enumerate(filas)}
    sede = _sede_propia(team_id)
    ruido = _ligas_ruido()
    fuera = []
    for r in cerrados:
        if not significativo(r, medianas):
            continue
        i = pos.get(r["fixtureId"])
        # un amistoso que cierra la burbuja es ruido: pretemporada, once de
        # prueba (Aston Villa–Porto, Roma–Cannes en la lista de otras ligas)
        if i is not None and filas[i].get("ligaId") in ruido:
            continue
        comp = (composicion(filas[max(0, i - r["partidos"]):i], filas[i], filas[max(0, i - 6):i],
                            en_su_estadio=bool(sede) and _sede_de(r["fixtureId"]) == sede)
                if i is not None else None)
        fuera.append({**r, "medianaKPico": medianas.get(r["signo"]), "composicion": comp})
    return fuera


def estudiados() -> dict[tuple[int, int], dict]:
    with _conectar() as con:
        return {(f[0], f[1]): json.loads(f[2]) for f in
                con.execute("SELECT fixture_id, team_id, estudio_json FROM reventon_estudio")}


def candidatos(liga_id: int, meses: int = 6, limite: int = 60, solo_con_ficha: bool = False) -> dict:
    desde = (datetime.now(timezone.utc) - timedelta(days=int(meses * 30.5))).strftime("%Y-%m-%d")
    hechos = estudiados()
    nombres = {}
    lista = []
    for tid in _equipos_de_liga(liga_id, desde):
        for r in reventones_de(tid):
            if str(r["fecha"])[:10] < desde:
                continue
            if tid not in nombres:
                t = saddb.query_one("sad", "SELECT name FROM teams WHERE id=?", (tid,))
                nombres[tid] = t["name"] if t else str(tid)
            ficha = _con_ficha(r["fixtureId"])
            if solo_con_ficha and not ficha["eventos"]:
                continue
            lista.append({
                "fixtureId": r["fixtureId"], "fecha": str(r["fecha"])[:10],
                "equipoId": tid, "equipo": nombres[tid],
                "rivalId": r["rivalId"], "rival": r["rival"], "condicion": r["condicion"],
                "tipo": TIPOS[r["signo"]], "signo": r["signo"], "partidos": r["partidos"],
                "kPico": r["kPico"], "medianaKPico": r["medianaKPico"], "nivelRival": r["nivelRival"],
                "resultado": r["resultado"], "esInternacional": r["esInternacional"],
                "senalesCalculadas": (r.get("composicion") or {}).get("senalesCalculadas") or [],
                "conFicha": ficha, "estudiado": (r["fixtureId"], tid) in hechos,
            })
    # primero lo que tiene ficha y no está estudiado; dentro, las rachas más largas
    lista.sort(key=lambda c: (c["estudiado"], not c["conFicha"]["eventos"], -c["partidos"], -c["kPico"]))
    return {
        "ligaId": liga_id, "desde": desde, "total": len(lista),
        "porTipo": {t: sum(1 for c in lista if c["tipo"] == t) for t in TIPOS.values()},
        "estudiados": sum(1 for c in lista if c["estudiado"]),
        "candidatos": lista[:limite],
        "criterio": "burbuja de la familia total con ≥ 3 partidos, o de 2 con la K pico por encima de la "
                    "mediana de su signo en ese equipo; primero los que tienen ficha y no están estudiados",
        "resumen": resumen([hechos[k] for k in hechos if any(
            (c["fixtureId"], c["equipoId"]) == k for c in lista)]),
    }


# ── la ficha del reventón, al día del partido ───────────────────────────────

def _burbuja_al_dia(team_id: int, fixture_id: int) -> dict:
    try:
        r = _app().equipo_burbujas(team_id, antesDe=fixture_id)
    except Exception as e:  # noqa: BLE001
        return {"sinDato": f"no se pudo armar la burbuja al día: {e}"}
    t = (r.get("familias") or {}).get("total") or {}
    return {"nivel": r.get("nivel"), "actual": t.get("actual"), "riesgo": t.get("riesgo"),
            "extremo": t.get("extremo"), "rival": t.get("rival"), "historial": t.get("historial")}


def _dt_en_el_banco(fixture_id: int, team_id: int) -> str:
    try:
        f = saddb.query_one("sad", "SELECT entrenador FROM alineaciones WHERE fixture_id=? AND team_id=? "
                                   "AND entrenador IS NOT NULL AND entrenador<>'' LIMIT 1", (fixture_id, team_id))
    except Exception:  # noqa: BLE001
        f = None
    return (f["entrenador"] if f else "") or ""


def _escala(team_id: int, rival: int, fecha: str, liga: int | None = None) -> dict:
    """De qué base sale el nivel de cada uno (Cristal–Bentín: Liga 1 contra Liga 2)."""
    from backend.analisis import escala
    try:
        return escala.entre(team_id, rival, fecha, liga)
    except Exception as e:  # noqa: BLE001
        return {"relacion": "sin dato", "comparable": True, "nota": f"no se pudo calcular: {e}"}


def ficha(fixture_id: int, team_id: int) -> dict | None:
    from backend import ficha_tactica
    fx = _app().get_fixture(fixture_id)
    if team_id not in (fx["home_team_id"], fx["away_team_id"]):
        raise EstudioInvalido(f"el equipo {team_id} no juega el fixture {fixture_id}")
    r = next((x for x in reventones_de(team_id) if x["fixtureId"] == fixture_id), None)
    rival = fx["away_team_id"] if fx["home_team_id"] == team_id else fx["home_team_id"]
    hechos = estudiados()
    return {
        "fixtureId": fixture_id, "equipoId": team_id, "rivalId": rival,
        "partido": f"{fx['home_name']} vs {fx['away_name']}", "fecha": str(fx["date"])[:10],
        "reventon": ({**r, "tipo": TIPOS[r["signo"]]} if r else None),
        "esCandidato": r is not None,
        "alDia": {"equipo": _burbuja_al_dia(team_id, fixture_id), "rival": _burbuja_al_dia(rival, fixture_id),
                  "nota": "historia cortada ESTRICTAMENTE antes de este partido (antesDe): lo que se "
                          "podía ver antes del pitazo"},
        "escala": _escala(team_id, rival, str(fx["date"])[:10], fx["league_id"]),
        "dtEnElBanco": {"equipo": _dt_en_el_banco(fixture_id, team_id),
                        "rival": _dt_en_el_banco(fixture_id, rival)},
        "tactica": ficha_tactica.tactica_de(fixture_id, fx["home_team_id"], fx["away_team_id"]),
        "estudio": hechos.get((fixture_id, team_id)),
        "listas": {"mecanismos": MECANISMOS, "senales": SENALES},
    }


# ── el estudio ──────────────────────────────────────────────────────────────

def _txt(v) -> str:
    return str(v).strip() if v is not None else ""


def guardar_estudio(fixture_id: int, team_id: int, cuerpo: dict) -> dict:
    fx = _app().get_fixture(fixture_id)
    if team_id not in (fx["home_team_id"], fx["away_team_id"]):
        raise EstudioInvalido(f"el equipo {team_id} no juega el fixture {fixture_id}")
    if not any(r["fixtureId"] == fixture_id for r in reventones_de(team_id)):  # noqa: SIM102
        raise EstudioInvalido("ese partido no cerró una burbuja significativa de ese equipo: "
                              "pedí la lista en GET /analisis/cowork/reventones")
    rechazos = []
    mec = _txt(cuerpo.get("mecanismo"))
    if mec not in MECANISMOS:
        raise EstudioInvalido(f"`mecanismo` tiene que ser uno de: {', '.join(MECANISMOS)}")
    sec = _txt(cuerpo.get("mecanismoSecundario"))
    if sec and sec not in MECANISMOS:
        rechazos.append({"donde": "mecanismoSecundario", "porque": f"{sec!r} no está en la lista: no se guardó"})
        sec = ""
    senales = []
    for s in cuerpo.get("senales") or []:
        s = _txt(s)
        if s in SENALES:
            senales.append(s)
        else:
            rechazos.append({"donde": "senales", "porque": f"{s!r} no está en la lista: no se guardó",
                             "esperado": ", ".join(SENALES)})
    lecciones = []
    for i, x in enumerate(cuerpo.get("lecciones") or []):
        if not isinstance(x, dict) or not _txt(x.get("skill")) or not _txt(x.get("leccion")):
            rechazos.append({"donde": f"lecciones[{i}]", "porque": "una lección necesita `skill` y `leccion`"})
            continue
        lecciones.append({"skill": skill_canonico(_txt(x["skill"])), "reglaTocada": _txt(x.get("reglaTocada")),
                          "leccion": _txt(x["leccion"])})
    if len(lecciones) > LECCIONES_MAX:
        rechazos.append({"donde": "lecciones", "porque": f"se guardan las primeras {LECCIONES_MAX}"})
        lecciones = lecciones[:LECCIONES_MAX]

    def _dict(k):
        v = cuerpo.get(k)
        return v if isinstance(v, dict) else {}

    # LAS SEÑALES QUE LA BASE SABE SOLA ENTRAN SOLAS: un estudio que se las
    # olvida no puede bajar su frecuencia en el resumen
    r_ = next(x for x in reventones_de(team_id) if x["fixtureId"] == fixture_id)
    calculadas = list((r_.get("composicion") or {}).get("senalesCalculadas") or [])
    # la otra burbuja del partido (3 casos de la segunda tanda: el empate cortó las dos)
    rival = fx["away_team_id"] if fx["home_team_id"] == team_id else fx["home_team_id"]
    act = (_burbuja_al_dia(rival, fixture_id) or {}).get("actual") or {}
    if (act.get("partidos") or 0) >= 2:
        calculadas.append("rival_tambien_en_burbuja")
    # el once que armó la racha no es el que jugó (Cienciano en Sullana: 6 cambios)
    # contra el último de la MISMA competición: el de copa con 9 rotados
    # disparaba la señal con el once tipo en cancha (Arsenal en Brighton)
    comp = r_.get("composicion") or {}
    previos = [p for p in comp.get("partidos") or [] if p.get("ligaId") == comp.get("ligaDelReventon")]
    if previos:
        cambios = cambios_en_el_once(fixture_id, team_id, previos[-1]["fixtureId"])
        if cambios is not None and cambios >= ONCE_CAMBIOS:
            calculadas.append("once_distinto")
    if not _escala(team_id, rival, str(fx["date"])[:10], fx["league_id"]).get("comparable", True):
        calculadas.append("rival_de_otra_base")
    senales = [x for x in senales if x not in SENALES_CALCULADAS] + list(calculadas)
    estudio = {
        "mecanismo": mec, "mecanismoSecundario": sec, "senales": senales,
        "senalesCalculadas": list(calculadas),
        "senalPrevia": _txt(cuerpo.get("senalPrevia")),
        "queP": _txt(cuerpo.get("queP")),
        "tde": {"equipo": _dict("tde").get("equipo") or {}, "rival": _dict("tde").get("rival") or {}},
        "dtp": _dict("dtp"), "efe": _dict("efe"),
        "lecciones": lecciones,
        "fuentes": [_txt(f) for f in (cuerpo.get("fuentes") or []) if _txt(f)],
        "notas": _txt(cuerpo.get("notas")),
        # la población no se declara: es siempre esta (ver el docstring)
        "seleccion": "post_resultado",
    }
    ahora = efedb.ahora()
    with _conectar() as con:
        previo = con.execute("SELECT creado_en FROM reventon_estudio WHERE fixture_id=? AND team_id=?",
                             (fixture_id, team_id)).fetchone()
        con.execute("INSERT INTO reventon_estudio (fixture_id, team_id, estudio_json, creado_en, actualizado_en) "
                    "VALUES (?,?,?,?,?) ON CONFLICT(fixture_id, team_id) DO UPDATE SET "
                    "estudio_json=excluded.estudio_json, actualizado_en=excluded.actualizado_en",
                    (fixture_id, team_id, json.dumps(estudio, ensure_ascii=False),
                     previo[0] if previo else ahora, ahora))
    print(f"[reventon] estudio {fixture_id}/{team_id}: {mec} · {len(lecciones)} lecciones", flush=True)
    return {"fixtureId": fixture_id, "equipoId": team_id, "estado": "actualizado" if previo else "guardado",
            "estudio": estudio, "rechazos": rechazos}


# ── lo que dicen los estudios juntos ────────────────────────────────────────

def resumen(estudios: list[dict]) -> dict:
    por_mec: dict[str, int] = {}
    por_senal: dict[str, int] = {}
    for e in estudios:
        por_mec[e["mecanismo"]] = por_mec.get(e["mecanismo"], 0) + 1
        for s in e.get("senales") or []:
            por_senal[s] = por_senal.get(s, 0) + 1
    return {
        "estudios": len(estudios),
        "porMecanismo": dict(sorted(por_mec.items(), key=lambda kv: -kv[1])),
        "porSenal": dict(sorted(por_senal.items(), key=lambda kv: -kv[1])),
        "nota": "frecuencia entre reventones ESTUDIADOS, no probabilidad de reventar: falta el "
                "denominador de las burbujas que no reventaron (eso lo mide el backtest)",
    }


def resumen_global(liga_id: int | None = None) -> dict:
    """Por tipo de reventón, el reparto de mecanismos y señales de todo lo estudiado."""
    hechos = estudiados()
    out = {}
    for (fx, tid), e in hechos.items():
        r = next((x for x in reventones_de(tid) if x["fixtureId"] == fx), None)
        if not r:
            continue
        if liga_id is not None:
            f = saddb.query_one("sad", "SELECT league_id FROM fixtures WHERE id=?", (fx,))
            if not f or f["league_id"] != liga_id:
                continue
        out.setdefault(TIPOS[r["signo"]], []).append(e)
    return {t: resumen(es) for t, es in out.items()}


def items_leccion(estados: dict, cohorte: str) -> list[dict]:
    """Las lecciones de los estudios como items del inventario de Aprendizaje
    (`lecciones.inventario`). Clave `rev:fixture:equipo:n`; población
    `post_resultado`: fijan rúbrica, nunca mueven un número."""
    fuera = []
    hechos = estudiados()
    for (fx, tid), e in hechos.items():
        f = saddb.query_one("sad", "SELECT f.date, ht.name AS a, at.name AS b, f.home_team_id FROM fixtures f "
                                   "JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
                                   "WHERE f.id=?", (fx,))
        if not f:
            continue
        local = f["home_team_id"] == tid
        for n, lx in enumerate(e.get("lecciones") or [], start=1):
            clave = f"rev:{fx}:{tid}:{n}"
            st = estados.get(clave) or {}
            fuera.append({
                "clave": clave, "orden": n, "origen": "reventon", "mecanismo": e.get("mecanismo"),
                "fixtureId": fx, "lado": "a" if local else "b",
                "equipo": f["a"] if local else f["b"], "rival": f["b"] if local else f["a"],
                "partido": f"{f['a']} vs {f['b']}", "fecha": str(f["date"])[:10],
                "skill": skill_canonico(lx["skill"]), "veredicto": "", "queP": e.get("queP", ""),
                "leccion": lx["leccion"], "reglaTocada": lx.get("reglaTocada", ""),
                "seleccion": "post_resultado", "modoEvaluacion": "PRE", "acredita": False,
                "mancha": "", "cohorte": cohorte, "cuarentena": "", "cuarentenaAutomatica": False,
                "dtEquivocado": [], "modoFallo": None, "modoFalloConfianza": None, "proponeMoverNumero": None,
                "puedeMoverNumeros": False,
                "queAutoriza": "estudio de un reventón con el resultado a la vista: fija rúbrica, "
                               "no mueve ningún número",
                "estado": st.get("estado") or "pendiente", "aplicadaEn": st.get("aplicada_en") or "",
                "nota": st.get("nota") or "", "actualizadoEn": st.get("actualizado_en") or "",
            })
    return fuera
