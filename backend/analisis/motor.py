"""Orquestación del análisis EFE (fase 1 del plan).

El análisis tarda 1-3 minutos: NO se bloquea el request HTTP (los proxies
lo cortan y el navegador se rinde). POST /analisis/efe responde al instante
— "listo" con el registro si ya existe, o "generando" tras lanzar el trabajo
en un hilo — y el frontend sondea GET /analisis/efe/estado/{id} hasta que
está listo. El trabajo sobrevive aunque el usuario cierre la página.

Flujo del trabajo:
  1. ¿ya hay análisis para ese fixture y estado? → listo (0 créditos)
  2. leer la despensa (investigacion) de ambos equipos → fresco vs faltante
  3. llamada a la API: system cacheado + user {modo, partido, datos_cacheados,
     campos_faltantes}; web search SOLO si hay faltantes
  4. structured output contra EFE_COMPARATIVO → JSON válido garantizado
  5. guardar el veredicto en analisis

Modo demo (SAD_EFE_DEMO=1): análisis de muestra determinista, sin API.
"""
import os
import threading

from backend import db as saddb
from backend.analisis import cliente, demo
from backend.analisis import db as efedb
from backend.analisis.esquemas import EFE_COMPARATIVO, analisis_vacio

VERSION_EFE = "1.5"

# trabajos en curso / fallidos, por fixture (en memoria: un solo proceso web)
_trabajos: dict[int, dict] = {}
_lock = threading.Lock()


class FixtureNoExiste(Exception):
    pass


class SinClave(Exception):
    pass


def _fixture(fixture_id: int) -> dict:
    fila = saddb.query_one(
        "sad",
        "SELECT f.id, f.date, f.home_team_id, f.away_team_id, f.league_id, "
        "f.league_season, ht.name AS local, at.name AS visitante, l.name AS liga "
        "FROM fixtures f "
        "JOIN teams ht ON ht.id = f.home_team_id "
        "JOIN teams at ON at.id = f.away_team_id "
        "LEFT JOIN leagues l ON l.id = f.league_id "
        "WHERE f.id = ?",
        (fixture_id,),
    )
    if not fila:
        raise FixtureNoExiste(f"fixture {fixture_id} no existe")
    return dict(fila)


# ── datos locales: lo que YA tenemos en sad.db no se busca en la web ─────────

def _resultados_de(team_id: int) -> str:
    # regla de 90': fulltime_* manda (goals_* incluye prórroga en AET/PEN);
    # el filtro por status_short incluye AET/PEN (su status_long varía)
    filas = saddb.query(
        "sad",
        "SELECT f.date, COALESCE(f.fulltime_home, f.goals_home) AS goals_home, "
        "COALESCE(f.fulltime_away, f.goals_away) AS goals_away, "
        "ht.name AS local, at.name AS visitante "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        "WHERE (f.home_team_id=? OR f.away_team_id=?) "
        "AND (f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished') "
        "AND COALESCE(f.fulltime_home, f.goals_home) IS NOT NULL ORDER BY f.date DESC LIMIT 8",
        (team_id, team_id),
    )
    return " · ".join(
        f"{(r['date'] or '')[:10]} {r['local']} {r['goals_home']}-{r['goals_away']} {r['visitante']}"
        for r in filas
    )


def _proximos_de(team_id: int) -> str:
    filas = saddb.query(
        "sad",
        "SELECT f.date, ht.name AS local, at.name AS visitante "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        "WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.status_short='NS' "
        "ORDER BY f.date ASC LIMIT 5",
        (team_id, team_id),
    )
    return " · ".join(f"{(r['date'] or '')[:16]} {r['local']} vs {r['visitante']}" for r in filas)


def _tabla_de(league_id: int | None, season: int | None) -> str:
    if not league_id or not season:
        return ""
    filas = saddb.query(
        "sad",
        "SELECT f.home_team_id, f.away_team_id, "
        "COALESCE(f.fulltime_home, f.goals_home) AS goals_home, "
        "COALESCE(f.fulltime_away, f.goals_away) AS goals_away, "
        "ht.name AS local, at.name AS visitante "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        "WHERE f.league_id=? AND f.league_season=? "
        "AND (f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished') "
        "AND COALESCE(f.fulltime_home, f.goals_home) IS NOT NULL LIMIT 5000",
        (league_id, season),
    )
    acc: dict[int, dict] = {}
    for r in filas:
        for tid, nombre, gf, gc in ((r["home_team_id"], r["local"], r["goals_home"], r["goals_away"]),
                                    (r["away_team_id"], r["visitante"], r["goals_away"], r["goals_home"])):
            e = acc.setdefault(tid, {"n": nombre, "pts": 0, "pj": 0, "gf": 0, "gc": 0})
            e["pj"] += 1
            e["gf"] += gf
            e["gc"] += gc
            e["pts"] += 3 if gf > gc else 1 if gf == gc else 0
    tabla = sorted(acc.values(), key=lambda e: (-e["pts"], -(e["gf"] - e["gc"]), -e["gf"]))
    return " · ".join(
        f"{i + 1}. {e['n']} {e['pts']}pts (PJ {e['pj']}, {e['gf']}-{e['gc']})"
        for i, e in enumerate(tabla[:12])
    )


def _datos_locales(fx: dict) -> dict[str, dict[str, str]]:
    """resultados / fixture / tabla desde NUESTRA ingesta: gratis y al día —
    la búsqueda web queda solo para lo que no tenemos (dt, plantel, xi, bajas)."""
    tabla = _tabla_de(fx.get("league_id"), fx.get("league_season"))
    return {
        "equipo_a": {"resultados": _resultados_de(fx["home_team_id"]),
                     "fixture": _proximos_de(fx["home_team_id"]), "tabla": tabla},
        "equipo_b": {"resultados": _resultados_de(fx["away_team_id"]),
                     "fixture": _proximos_de(fx["away_team_id"]), "tabla": tabla},
    }


def _demo_activo() -> bool:
    return os.environ.get("SAD_EFE_DEMO", "").strip() == "1"


def _respuesta(estado: str, detalle: str | None = None, registro: dict | None = None) -> dict:
    return {"estado": estado, "detalle": detalle, "registro": registro}


def generar_efe(fixture_id: int, estado: str = "preliminar") -> dict:
    """Corre el análisis completo y guarda el veredicto (SÍNCRONO: solo para
    el hilo de trabajo y el modo demo)."""
    existente = efedb.analisis_existente("efe", fixture_id, estado)
    if existente:
        return existente

    fx = _fixture(fixture_id)
    equipo_a, equipo_b = fx["local"], fx["visitante"]
    fecha = (fx["date"] or "")[:10] or None

    if _demo_activo():
        resultado = demo.efe_demo(equipo_a, equipo_b, fx["liga"], fecha)
    else:
        if not cliente.hay_clave():
            raise SinClave("Falta ANTHROPIC_API_KEY en el entorno")
        frescos_a, faltan_a = efedb.investigacion_de(equipo_a)
        frescos_b, faltan_b = efedb.investigacion_de(equipo_b)
        # lo que ya tenemos en sad.db (tabla, resultados, próximos partidos)
        # entra como dato cacheado y NO se busca en la web: costo cero
        locales = _datos_locales(fx)
        for frescos, faltan, lado in ((frescos_a, faltan_a, "equipo_a"),
                                      (frescos_b, faltan_b, "equipo_b")):
            for tipo, txt in locales[lado].items():
                if txt and tipo in faltan:
                    frescos[tipo] = txt
                    faltan.remove(tipo)
        faltantes = [f"{t}_a" for t in faltan_a] + [f"{t}_b" for t in faltan_b]
        payload = {
            "modo": "efe",
            "partido": {
                "equipo_a": equipo_a,
                "equipo_b": equipo_b,
                "torneo": fx["liga"],
                "fecha": fecha,
            },
            "datos_cacheados": {"equipo_a": frescos_a, "equipo_b": frescos_b},
            "campos_faltantes": faltantes,
        }
        # el analista hace su propia lectura K en la app (sección Burbujas):
        # el bloque C no se investiga ni puntúa — ahorra las búsquedas más caras.
        # SAD_EFE_CON_K=1 lo reactiva si algún día se quiere de vuelta.
        if os.environ.get("SAD_EFE_CON_K", "").strip() != "1":
            payload["bloque_c"] = (
                "NO investigues ni puntúes el bloque C (constantes K): el analista hace su "
                "propia lectura K en la app. Aplica R-KT.2: C excluido (excluido=true, "
                "motivo_exclusion='Lectura K manual del analista en la app', score/max/"
                "ponderado en 0) y maximo_alcanzable renormalizado sin C."
            )
        resultado, _uso = cliente.analizar(payload, EFE_COMPARATIVO,
                                           con_busqueda=bool(faltantes))
        # Un análisis sin contenido real (ambos equipos en 0) NO se guarda:
        # cachearlo dejaría al usuario sin forma de regenerar.
        if analisis_vacio(resultado):
            raise RuntimeError(
                "El análisis llegó vacío (scores en 0 — investigación fallida). "
                "No se guardó: vuelve a pulsar «Generar análisis EFE» para reintentar."
            )
        # LA DESPENSA: lo investigado se separa del análisis y se deposita por
        # equipo con TTL — el siguiente análisis de estos equipos lo recibe en
        # datos_cacheados y busca solo lo vencido (de ~$0.50 a ~$0.10-0.20).
        # Solo los tipos que FALTABAN: lo que ya estaba fresco no se re-sella.
        inv = resultado.pop("investigacion", None) or {}
        depositados = 0
        for lado, equipo, faltan in (("equipo_a", equipo_a, faltan_a),
                                     ("equipo_b", equipo_b, faltan_b)):
            datos = inv.get(lado) or {}
            for tipo in faltan:
                contenido = (datos.get(tipo) or "").strip() if isinstance(datos.get(tipo), str) else ""
                if contenido:
                    efedb.guardar_investigacion(equipo, tipo, contenido)
                    depositados += 1
        print(f"[efe] despensa: {depositados} datos depositados "
              f"({equipo_a} / {equipo_b})", flush=True)

    return efedb.guardar_analisis(
        "efe", fixture_id, equipo_a, equipo_b, fecha or "", estado,
        resultado, resultado.get("version_efe", VERSION_EFE),
    )


def _trabajo(fixture_id: int, estado: str) -> None:
    try:
        generar_efe(fixture_id, estado)
        with _lock:
            _trabajos.pop(fixture_id, None)
        print(f"[efe] fixture {fixture_id}: análisis guardado", flush=True)
    except Exception as e:  # el error queda consultable vía /estado
        with _lock:
            _trabajos[fixture_id] = {"estado": "error", "detalle": str(e)}
        print(f"[efe] ERROR fixture {fixture_id}: {e}", flush=True)


def iniciar_efe(fixture_id: int, estado: str = "preliminar", forzar: bool = False) -> dict:
    """Respuesta inmediata: listo (con registro), generando, o lanza el hilo.

    `forzar` (botón Regenerar): descarta lo guardado y emite un análisis
    nuevo — salvo que ya haya un trabajo en curso, que no se duplica."""
    with _lock:
        trabajo = _trabajos.get(fixture_id)
        if trabajo and trabajo["estado"] == "generando":
            return _respuesta("generando", detalle="análisis en curso")

    if forzar:
        efedb.borrar_analisis("efe", fixture_id)
        print(f"[efe] fixture {fixture_id}: regeneración forzada (análisis previo descartado)", flush=True)
    else:
        existente = efedb.analisis_existente("efe", fixture_id, estado)
        if existente:
            return _respuesta("listo", registro=existente)
    _fixture(fixture_id)  # 404 antes de encolar nada

    if _demo_activo():  # demo: rápido y sin API → síncrono
        return _respuesta("listo", registro=generar_efe(fixture_id, estado))
    if not cliente.hay_clave():
        raise SinClave("Falta ANTHROPIC_API_KEY en el entorno")

    with _lock:
        trabajo = _trabajos.get(fixture_id)
        if trabajo and trabajo["estado"] == "generando":
            return _respuesta("generando", detalle="análisis en curso")
        # sin trabajo, o el anterior falló: se (re)lanza
        _trabajos[fixture_id] = {"estado": "generando", "detalle": None}
    threading.Thread(target=_trabajo, args=(fixture_id, estado),
                     daemon=True, name=f"efe-{fixture_id}").start()
    print(f"[efe] fixture {fixture_id}: análisis lanzado", flush=True)
    return _respuesta("generando", detalle="análisis lanzado")


def estado_efe(fixture_id: int) -> dict:
    """Para el sondeo del frontend: listo / generando / error / nada."""
    existente = efedb.analisis_existente("efe", fixture_id, "confirmado") \
        or efedb.analisis_existente("efe", fixture_id, "preliminar")
    if existente:
        return _respuesta("listo", registro=existente)
    with _lock:
        trabajo = _trabajos.get(fixture_id)
    if trabajo:
        return _respuesta(trabajo["estado"], detalle=trabajo.get("detalle"))
    return _respuesta("nada")


def analisis_del_partido(fixture_id: int) -> list[dict]:
    """Todo lo emitido para un fixture (lectura pura, cero créditos)."""
    return efedb.analisis_de_fixture(fixture_id)
