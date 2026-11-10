"""EL ESCANEO PREVENTIVO (30/10/2026, pedido del usuario: «no esperar a que
salten estas cosas»).

Las incidencias llegan cuando un analista TROPIEZA con un dato malo: Neymar
disponible con una roja encima (772), un goleador con dos ids que obliga a
duplicarlo en la tabla F1 (839), el once de una copa que llega con la ficha
(737). Cada una se veía en la base ANTES del parte; nadie la miraba. Este
escaneo recorre los partidos de la agenda (y los de las partes recién jugadas)
con una lista de chequeos de lo básico —quién no puede jugar, quién es quién,
quién dirige, si el partido existe y si el mercado está— y devuelve lo que
encuentra AGRUPADO POR CHEQUEO, antes de que un parte se escriba encima.

Solo lee (0 requests, 0 tokens). El mantenimiento lo corre en su paso 0 y
deposita cada chequeo con hallazgos como UNA incidencia (`origen: escaneo`);
la corrida de partes lo lee para saber qué mirar dos veces. Un chequeo nuevo
se suma a `CHEQUEOS` con la regla que cuida: lo que se vuelve a escapar es un
chequeo que falta, no una incidencia más.
"""
from __future__ import annotations

import os

from datetime import datetime, timedelta, timezone

from backend import db as saddb

# la regla de fútbol que cuida cada chequeo, el área de la incidencia y qué tan grave es
CHEQUEOS: dict[str, dict] = {
    # INFORMATIVOS desde el 02/11/2026 (mantenimiento, prevención 7-bis): son
    # listas PARA EL PARTE, no fallas. Depositados como incidencia se cerraron
    # siempre igual, por diseño: sancion (889, 935, 954, 1024, 1049, 1073, 1146),
    # sin-plantel (890, 936, 955, 1026, 1147) y dt-sin-confirmar (933, 952,
    # 1022, 1048, 1071, 1144). Lo que cobra un parte es SANCION-SIN-DECLARAR
    # (chequeo `sancion-sin-declarar`, que sí se deposita), DT-DISCREPANCIA y
    # DT-VS-BANCO; la corrida de partes los sigue leyendo en el GET.
    "sancion": {
        "titulo": "Sancionados de la base para un partido de la agenda",
        "area": "f1", "severidad": "aviso", "informativo": True,
        "regla": "una roja (directa o doble amarilla) suspende el partido siguiente de la competición, y "
                 "el ciclo de amarillas también (backend/sanciones.py)",
    },
    "sancion-sin-declarar": {
        "titulo": "Parte que tiene disponible a un sancionado de la base",
        "area": "f1", "severidad": "error",
        "regla": "el sancionado va en `fuera` con motivo «sanción», o la nota dice por qué juega",
    },
    "jugador-duplicado": {
        "titulo": "El mismo jugador dos veces en la tabla F1",
        "area": "f1", "severidad": "error",
        "regla": "una persona es una fila: dos ids con el mismo nombre se funden (f1_base.deduplicar)",
    },
    "sin-plantel": {
        "titulo": "Equipo de la agenda sin plantilla ingestada",
        "area": "f1", "severidad": "aviso", "informativo": True,
        "regla": "sin plantilla no hay tabla F1 ni bloque F calculado: la tabla sale de la prensa",
    },
    "dt-sin-confirmar": {
        "titulo": "DT de la base sin confirmar para un partido de la agenda",
        "area": "dt", "severidad": "aviso", "informativo": True,
        "regla": "el DT viene de la alineación del último partido o de un registro de ≤ 7 días; si no, "
                 "se confirma en prensa antes del bloque A",
    },
    "dos-partidos": {
        "titulo": "Equipo con dos partidos a pocas horas",
        "area": "agenda", "severidad": "error",
        "regla": "un equipo no juega dos veces el mismo día: uno de los dos fixtures es un aplazado sin "
                 "marcar o un duplicado",
    },
    "sin-cuotas": {
        "titulo": "Partido de la agenda sin cuota prepartido a pocas horas",
        "area": "cuotas", "severidad": "aviso",
        "regla": "el 1X2 parte del mercado (sad-analysis 6-B): sin captura, el parte sale sin su ancla",
    },
    "once-tarde": {
        "titulo": "Partido con parte sin ninguna versión del once antes del pitazo",
        "area": "once", "severidad": "error",
        "regla": "el once de un partido con parte se pide antes del saque (en_vivo.fixtures_para_xi): sin "
                 "él no hay rehacer ni cierre del bloque F antes del partido",
    },
    "ficha-sin-eventos": {
        "titulo": "Partido con parte jugado hace horas sin eventos en la ficha",
        "area": "ficha", "severidad": "aviso",
        "regla": "sin eventos no hay goles con minuto, tarjetas (sanciones) ni veredicto del TDE",
    },
    # EL MERCADO SE ENTERÓ Y LA BASE NO (08/11/2026, incidencia 1332, Santa Fe–
    # Pasto: Pasto jugó con 20 canteranos por un paro del plantel y sin su DT; el
    # 1X2 del motor, los goles acotados y la F1 describían al plantel
    # profesional y solo la cuota se movió: local 1,66 → 1,08 en 24 h). Un salto
    # así sin nada en la base es un hecho que el parte tiene que buscar en prensa.
    "mercado-salto": {
        "titulo": "El 1X2 del mercado saltó en las últimas horas",
        "area": "cuotas", "severidad": "aviso",
        "regla": "un salto de más de 25 puntos en la probabilidad implícita de un resultado entre la "
                 "primera captura de las últimas 24 h y la última es un hecho (paro, once alternativo, "
                 "DT ausente) que la base no ve: se busca en prensa y el parte lo dice",
    },
    # INFORMATIVO: no es una falla de nada, es un dato para quien escribe el
    # parte. El mantenimiento NO lo deposita como incidencia (sería una por
    # pasada mientras dure la temporada); la fiabilidad de μ ya baja sola.
    "nivel-con-amistosos": {
        "titulo": "Nivel del motor armado con amistosos de pretemporada",
        "area": "otro", "severidad": "aviso", "informativo": True,
        "regla": "el nivel cuenta los últimos 20 partidos de todas las competiciones; con 3+ amistosos en un "
                 "lado el motor queda el doble de lejos del mercado y μ baja a fiabilidad «media» "
                 "(Konyaspor 0-4 Galatasaray, 860)",
    },
    # INFORMATIVO (10/11/2026, incidencia 1333, decisión del usuario): los dos
    # equipos tienen la misma sede de local en la temporada; la localía del
    # motor (0,382) no aplica y /predicciones ya lo avisa en fiabilidadMu.
    "sede-compartida": {
        "titulo": "Clásico con estadio compartido: la localía del motor no aplica",
        "area": "otro", "severidad": "aviso", "informativo": True,
        "regla": "el motor suma la localía a todo partido; con los dos equipos de local en el mismo estadio "
                 "(Nacional Potosí–Real Potosí en el Ugarte: 49 % local contra 37 % del mercado, 1333) "
                 "no hay visita real y μ baja a fiabilidad «media»",
    },
}

# A menos de esto del pitazo, sin cuota es hallazgo. LO QUE EL REFRESCO TODAVÍA
# NO INTENTÓ NO ES UNA FALLA (06/11/2026, incidencia 1255, Fortaleza–Medellín a
# 7,5 h): el refresco de cuotas mira solo los NS a <= SAD_REFRESCO_VENTANA_HORAS
# (6) del pitazo, y con 12 h acá el escaneo depositaba partidos que el refresco
# aún no había pedido (la familia 318 llegó a 8 casos). Una hora menos que esa
# ventana: para entonces el refresco ya pasó al menos una vez.
VENTANA_REFRESCO = int(os.environ.get("SAD_REFRESCO_VENTANA_HORAS", "6").strip() or "6")
HORAS_CUOTAS = max(1, VENTANA_REFRESCO - 1)
HORAS_FICHA = 6            # jugado hace más de esto, sin eventos es hallazgo
SALTO_MERCADO_PTS = 25     # puntos de probabilidad implícita (1332)
SALTO_MERCADO_HORAS = 24


def _salto_mercado(fixture_id: int, ahora: datetime) -> str:
    """El mayor salto del 1X2 (probabilidad implícita normalizada, la media de
    las casas) entre la primera captura de las últimas SALTO_MERCADO_HORAS y la
    última; "" si no pasa de SALTO_MERCADO_PTS o no hay dos capturas."""
    desde = (ahora - timedelta(hours=SALTO_MERCADO_HORAS)).strftime("%Y-%m-%d %H:%M:%S")
    filas = saddb.query(
        "sad", "SELECT captured_at AS t, value AS v, odd FROM odds_history WHERE fixture_id=? "
               "AND casa IS NULL AND lower(bet_name) IN ('match winner', '1x2', 'fulltime result') "
               "AND captured_at >= ? ORDER BY captured_at", (fixture_id, desde)) or []
    por_t: dict[str, dict] = {}
    for f in filas:
        v = {"Home": "1", "Draw": "X", "Away": "2"}.get(str(f["v"]), str(f["v"]))
        if v in ("1", "X", "2") and f["odd"] and float(f["odd"]) > 1:
            por_t.setdefault(str(f["t"]), {})[v] = float(f["odd"])
    capturas = [(t, c) for t, c in sorted(por_t.items()) if len(c) == 3]
    if len(capturas) < 2:
        return ""

    def _prob(c: dict) -> dict:
        inv = {k: 1 / o for k, o in c.items()}
        tot = sum(inv.values())
        return {k: x / tot for k, x in inv.items()}
    (t0, c0), (t1, c1) = capturas[0], capturas[-1]
    p0, p1 = _prob(c0), _prob(c1)
    k = max(p0, key=lambda x: abs(p1[x] - p0[x]))
    salto = (p1[k] - p0[k]) * 100
    if abs(salto) <= SALTO_MERCADO_PTS:
        return ""
    return (f"el {k} pasó de cuota {c0[k]:.2f} ({p0[k]:.0%}) a {c1[k]:.2f} ({p1[k]:.0%}) entre {t0[:16]} y "
            f"{t1[:16]} UTC: buscar en prensa qué pasó (paro, once alternativo, DT ausente)")


def _nunca_publicado(fixture_id: int) -> bool:
    """¿La ficha post-partido se selló SIN alineaciones y no hay ninguna en la
    base? Entonces la API no la dio nunca para ese partido."""
    try:
        meta = saddb.query_one("sad", "SELECT alineaciones FROM fichas_meta WHERE fixture_id=?", (fixture_id,))
        if not meta or (meta["alineaciones"] or 0) > 0:
            return False
        return not saddb.query_one("sad", "SELECT 1 AS x FROM alineaciones WHERE fixture_id=? LIMIT 1", (fixture_id,))
    except Exception:  # noqa: BLE001 — base sin la tabla de fichas: se cuenta como siempre
        return False


def _ficha_sellada(fixture_id: int) -> bool:
    """¿Ya se capturó la ficha post-partido? Antes de eso «nunca publicado» y
    «publicado tarde» no se distinguen (05/11/2026, incidencia 1248: Bolívar–
    Real Potosí, copa de Bolivia, que no publica onces, salía once-tarde dos
    horas después del partido, con la ficha sin sellar). La ficha que nunca se
    captura la marca `ficha-sin-eventos` a las HORAS_FICHA."""
    try:
        return bool(saddb.query_one("sad", "SELECT 1 AS x FROM fichas_meta WHERE fixture_id=?", (fixture_id,)))
    except Exception:  # noqa: BLE001 — base sin la tabla de fichas: se juzga como siempre
        return True


def _publicado_tarde(fixture_id: int, fecha_utc) -> bool:
    """¿La primera versión del once llegó ENTRE el pitazo y el fin de la
    ventana tardía del ciclo en vivo (`en_vivo.XI_VENTANA_TARDE_MIN`)? Entonces
    el ciclo lo estaba pidiendo y la API lo publicó tarde: es la causa ya
    decidida (1072, 1081, 1145; 1231: Cúcuta–Santa Fe, Liga BetPlay), no un
    once que nadie pidió. El que llega horas después —con la ficha
    post-partido— sí es hallazgo: el ciclo no lo pidió a tiempo."""
    try:
        from backend.ingesta.en_vivo import XI_VENTANA_TARDE_MIN
        pitazo = datetime.strptime(str(fecha_utc)[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
        fila = saddb.query_one("sad", "SELECT MIN(capturada_en) AS t FROM alineaciones_versiones WHERE fixture_id=?",
                               (fixture_id,))
        if not fila or not fila["t"]:
            return False
        primera = datetime.strptime(str(fila["t"])[:19], "%Y-%m-%d %H:%M:%S")
        return pitazo < primera <= pitazo + timedelta(minutes=XI_VENTANA_TARDE_MIN)
    except Exception:  # noqa: BLE001 — base sin la tabla de versiones o fecha ilegible: se marca como siempre
        return False


def _hallazgo(chequeo: str, item: dict, detalle: str, lado: str | None = None) -> dict:
    return {"chequeo": chequeo, "fixtureId": item["fixtureId"], "partido": item.get("partido", ""),
            "fecha": item.get("fecha", ""), "hora": item.get("hora", ""),
            # la hora de la base es UTC; la de Lima viaja al lado (incidencia 1230)
            "horaLima": item.get("horaLima", ""),
            **({"lado": lado, "equipo": item.get("equipoA" if lado == "a" else "equipoB", "")} if lado else {}),
            "detalle": detalle}


def _duplicados(candidatos: list[dict], juntos=None) -> list[str]:
    """El mismo jugador dos veces en la F1 que la tabla NO resolvió. Lo marcado
    `posibleMismoQue` ya está cubierto (el bloque F no lo cuenta de baja) y dos
    ids que compartieron una hoja de partido son dos personas (31/10/2026,
    incidencia 887: los dos «T. Palacios» de Estudiantes y los dos «A. Romero»
    de Monagas salían como duplicados y eran dos jugadores)."""
    from backend.analisis.f1_base import mismo_jugador
    out = []
    for i, a in enumerate(candidatos):
        alt_a = {a.get("jugadorId"), *(a.get("idsAlternos") or [])}
        for b in candidatos[i + 1:]:
            if b.get("jugadorId") in alt_a or a.get("jugadorId") in (b.get("idsAlternos") or []):
                continue
            if a.get("posibleMismoQue") == b.get("jugadorId") or b.get("posibleMismoQue") == a.get("jugadorId"):
                continue
            if (juntos and a.get("jugadorId") is not None and b.get("jugadorId") is not None
                    and juntos(a["jugadorId"], b["jugadorId"])):
                continue
            if mismo_jugador(a.get("nombre") or "", b.get("nombre") or ""):
                out.append(f"«{a['nombre']}» {a.get('jugadorId')} y «{b['nombre']}» {b.get('jugadorId')}")
    return out


def _pre(item: dict, ahora: datetime) -> list[dict]:
    from backend import sanciones
    from backend.analisis import f1_base
    out = []
    fid = item["fixtureId"]
    try:
        sanc = sanciones.de_fixture(fid)
    except Exception:  # noqa: BLE001
        sanc = {}
    for lado in ("a", "b"):
        for x in (sanc.get(lado) or {}).get("sancionados") or []:
            out.append(_hallazgo("sancion", item, f"{x['nombre']}: {x['detalle']}", lado))
    # LAS SANCIONES SE CALCULAN UNA VEZ por partido y la tabla F1 y la alerta
    # del parte las reciben hechas (antes, tres veces)
    try:
        tabla = f1_base.tabla(fid, sanc=sanc) or {}
    except Exception:  # noqa: BLE001
        tabla = {}
    for lado in ("a", "b"):
        t = tabla.get(lado) or {}
        if t.get("sinDato"):
            out.append(_hallazgo("sin-plantel", item, t["sinDato"], lado))
        for d in _duplicados(t.get("candidatos") or [], f1_base._juntos):
            out.append(_hallazgo("jugador-duplicado", item, d, lado))
        dt = (item.get("dt") or {}).get(lado)
        if not dt:
            out.append(_hallazgo("dt-sin-confirmar", item, "sin DT en la base", lado))
        elif not dt.get("fiable"):
            out.append(_hallazgo("dt-sin-confirmar", item,
                                 f"{dt.get('nombre') or '?'} (fuente {dt.get('fuente') or '?'}, "
                                 f"{dt.get('edadDias')} días)", lado))
    if item.get("conflicto"):
        out.append(_hallazgo("dos-partidos", item, item["conflicto"]))
    try:
        from backend.analisis import ventana_nivel
        fx = saddb.query_one("sad", "SELECT date, home_team_id, away_team_id FROM fixtures WHERE id=?", (fid,))
        for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])) if fx else ():
            c = ventana_nivel.composicion(tid, str(fx["date"]))
            if c and c["amistosos"] >= ventana_nivel.UMBRAL_AMISTOSOS:
                out.append(_hallazgo("nivel-con-amistosos", item, ventana_nivel.texto(c), lado))
    except Exception:  # noqa: BLE001 — sin la tabla de ligas: no se cuenta la ventana
        pass
    try:
        from backend.analisis import ventana_nivel
        fx = saddb.query_one("sad", "SELECT date, home_team_id, away_team_id FROM fixtures WHERE id=?", (fid,))
        sede = fx and ventana_nivel.sede_compartida(fx["home_team_id"], fx["away_team_id"], str(fx["date"]))
        if sede:
            out.append(_hallazgo("sede-compartida", item, f"los dos juegan de local en {sede}"))
    except Exception:  # noqa: BLE001 — sin la sede en la base: no se afirma que se comparta
        pass
    try:
        pitazo = datetime.strptime(f"{item.get('fecha')} {item.get('hora')}", "%Y-%m-%d %H:%M").replace(
            tzinfo=timezone.utc)
        if pitazo - ahora <= timedelta(hours=HORAS_CUOTAS):
            fila = saddb.query_one("sad", "SELECT 1 AS x FROM odds_history WHERE fixture_id=? LIMIT 1", (fid,))
            if not fila:
                out.append(_hallazgo("sin-cuotas", item, f"pitazo {item.get('hora')} UTC y ninguna captura "
                                                         "en odds_history"))
    except Exception:  # noqa: BLE001 — sin la tabla de historial: no se juzga
        pass
    try:
        salto = _salto_mercado(fid, ahora)
        if salto:
            out.append(_hallazgo("mercado-salto", item, salto))
    except Exception:  # noqa: BLE001 — sin el historial completo de cuotas: no se juzga
        pass
    if item.get("tieneParte"):
        try:
            import json
            from backend.analisis import parte as _parte
            with _parte._conectar() as con:
                fila = con.execute("SELECT parte_json FROM parte_cowork WHERE fixture_id=?", (fid,)).fetchone()
            p = json.loads(fila["parte_json"]) if fila else None
            if p:
                for a in f1_base.alertas_sancion(p, {"id": fid}, {"a": item.get("equipoA"), "b": item.get("equipoB")},
                                                 sanc=sanc):
                    out.append(_hallazgo("sancion-sin-declarar", item, a["detalle"], a["equipo"]))
        except Exception:  # noqa: BLE001
            pass
    return out


def _post(horas: int, ahora: datetime) -> tuple[list[dict], int]:
    """Las partes de partidos jugados en las últimas `horas`."""
    from backend.analisis import parte as _parte
    desde = (ahora - timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
    hasta = ahora.strftime("%Y-%m-%d %H:%M:%S")
    # SOLO LAS PARTES DE LA VENTANA, por la fecha del partido (índice
    # idx_parte_fecha): antes se leían todas las partes y se filtraban en sad.db
    try:
        with _parte._conectar() as con:
            ids = [r["fixture_id"] for r in con.execute(
                "SELECT fixture_id FROM parte_cowork WHERE fecha BETWEEN ? AND ?",
                ((ahora - timedelta(hours=horas + 24)).strftime("%Y-%m-%d"), ahora.strftime("%Y-%m-%d")))]
    except Exception:  # noqa: BLE001
        return [], 0
    if not ids:
        return [], 0
    out, n = [], 0
    for k in range(0, len(ids), 500):
        lote = ids[k:k + 500]
        try:
            filas = saddb.query(
                "sad", f"SELECT f.id, f.date, f.status_short, ht.name AS a, at.name AS b FROM fixtures f "
                       f"JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
                       f"WHERE f.id IN ({','.join('?' * len(lote))}) AND f.date BETWEEN ? AND ?",
                (*lote, desde, hasta))
        except Exception:  # noqa: BLE001
            continue
        for f in filas:
            if f["status_short"] in ("NS", "TBD", "PST", "CANC"):
                continue
            n += 1
            item = {"fixtureId": f["id"], "partido": f"{f['a']} vs {f['b']}", "fecha": str(f["date"])[:10],
                    "hora": str(f["date"])[11:16], **_parte.hora_lima(f["date"])}
            try:
                previa = saddb.query_one(
                    "sad", "SELECT 1 AS x FROM alineaciones_versiones WHERE fixture_id=? AND capturada_en <= ? "
                           "LIMIT 1", (f["id"], str(f["date"])[:19]))
                # LA API QUE NUNCA PUBLICÓ EL ONCE NO ES UN ONCE TARDE (incidencias
                # 934, 941, 953: 22 partidos de la Copa del Rey con clubes de Tercera
                # y regionales cada pasada, con la ficha post-partido sellada sin
                # alineaciones). Eso es cobertura (deuda 5, `nuncaVaALlegar`):
                # el chequeo es para el once que existió y llegó tarde.
                if (not previa and _ficha_sellada(f["id"]) and not _nunca_publicado(f["id"])
                        and not _publicado_tarde(f["id"], f["date"])):
                    out.append(_hallazgo("once-tarde", item, f"pitazo {item['hora']} UTC: ninguna versión del "
                                                             "once capturada antes"))
            except Exception:  # noqa: BLE001 — base sin la tabla de versiones
                pass
            try:
                fin = datetime.strptime(str(f["date"])[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                if (ahora - fin > timedelta(hours=HORAS_FICHA)
                        and not saddb.query_one("sad", "SELECT 1 AS x FROM fixture_eventos WHERE fixture_id=? "
                                                       "LIMIT 1", (f["id"],))):
                    out.append(_hallazgo("ficha-sin-eventos", item, "sin eventos en la base"))
            except Exception:  # noqa: BLE001
                pass
    return out, n


# el resultado entero se guarda unos minutos: el mantenimiento y la corrida de
# partes pueden pedirlo seguido y la base no cambia tan rápido
CACHE_S = 600
_cache: dict[tuple, tuple[float, dict]] = {}


def escanear(horas: int = 36, jugados_horas: int = 48, ahora: datetime | None = None,
             fresco: bool = False) -> dict:
    """Los chequeos sobre la agenda de las próximas `horas` y las partes jugadas
    en las últimas `jugados_horas`, agrupados por chequeo. Guardado `CACHE_S`
    segundos (`fresco` lo salta); con `ahora` dado (tests) no se guarda."""
    import time
    clave = (horas, jugados_horas)
    if ahora is None and not fresco and clave in _cache and time.time() - _cache[clave][0] < CACHE_S:
        return {**_cache[clave][1], "deCache": True}
    r = _escanear(horas, jugados_horas, ahora)
    if ahora is None:
        _cache[clave] = (time.time(), r)
    return r


def _escanear(horas: int, jugados_horas: int, ahora: datetime | None) -> dict:
    from backend.analisis import parte as _parte
    ahora = ahora or datetime.now(timezone.utc)
    try:
        ag = _parte.agenda(desde_ahora=True, horas=horas, limite=200)
        items = ag.get("analizar") or []
    except Exception as e:  # noqa: BLE001
        items, ag = [], {"error": str(e)}
    hallazgos = []
    for it in items:
        hallazgos.extend(_pre(it, ahora))
    post, jugados = _post(jugados_horas, ahora)
    hallazgos.extend(post)
    por = {}
    for h in hallazgos:
        c = por.setdefault(h["chequeo"], {**CHEQUEOS[h["chequeo"]], "hallazgos": 0, "partidos": set()})
        c["hallazgos"] += 1
        c["partidos"].add(h["fixtureId"])
    return {
        "generadoEn": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ventanaHoras": horas, "jugadosHoras": jugados_horas,
        "partidosRevisados": len(items), "jugadosRevisados": jugados,
        "porChequeo": {k: {**v, "partidos": sorted(v["partidos"])} for k, v in sorted(por.items())},
        "hallazgos": hallazgos,
        "chequeos": CHEQUEOS,
        "nota": ("escaneo preventivo: lo que la base ya dice ANTES de que un parte se escriba encima. El "
                 "mantenimiento deposita cada chequeo con hallazgos como UNA incidencia (origen escaneo); "
                 "la corrida de partes lo lee para saber qué mirar dos veces. Un dato que se escapó y no "
                 "está acá es un chequeo que falta."),
    }
