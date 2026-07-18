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
from backend.analisis.esquemas import EFE_COMPARATIVO, TIMELINE, analisis_vacio, timeline_vacio

VERSION_EFE = "1.5"

# trabajos en curso / fallidos, por "tipo:fixture" (en memoria: un solo proceso)
_trabajos: dict[str, dict] = {}
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


def _xi_de_item(item: dict, titulo: str) -> str:
    xi = [f"{(j.get('player') or {}).get('name') or '?'} ({(j.get('player') or {}).get('pos') or '?'})"
          for j in item.get("startXI") or []]
    if not xi:
        return ""
    dt = (item.get("coach") or {}).get("name") or "?"
    return (f"{titulo} (formación {item.get('formation') or '?'}, DT {dt}): "
            + ", ".join(xi) + " [fuente: API-Football lineups]")


def _xi_ultimo_partido(api, team_id: int) -> str:
    """Formación y XI del ÚLTIMO partido jugado, desde la API (1 request del
    plan ya pagado) — evita que el EFE busque la formación en la web cuando el
    XI oficial de hoy aún no se publicó."""
    fila = saddb.query_one(
        "sad",
        "SELECT id, date FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
        "AND (status_short IN ('FT','AET','PEN') OR status_long='Match Finished') "
        "ORDER BY date DESC LIMIT 1",
        (team_id, team_id),
    )
    if not fila or not api.quedan():
        return ""
    data = api.get("fixtures/lineups", {"fixture": fila["id"]})
    for item in (data or {}).get("response", []):
        if (item.get("team") or {}).get("id") == team_id:
            return _xi_de_item(item, f"XI del último partido jugado ({str(fila['date'])[:10]})")
    return ""


def _xi_y_bajas(fixture_id: int, home_id: int, away_id: int) -> dict[str, dict[str, str]]:
    """XI oficial y lesionados desde API-Football (2-4 requests contra el
    presupuesto de la ingesta, con su respaldo incluido). El XI se publica
    ~20-40 min antes del pitazo: si aún no está, se sirve la formación del
    ÚLTIMO partido jugado (también de la API) — nada de esto debe terminar en
    búsqueda web, que es lo caro y poco fiable en ligas chicas."""
    out: dict[str, dict[str, str]] = {"equipo_a": {}, "equipo_b": {}}
    try:
        from backend.ingesta.extractor import Cliente, leer_clave
        api = Cliente(leer_clave())
    except BaseException:  # sin API_FOOTBALL_KEY (p. ej. entorno local)
        return out

    def lado_de(team: dict | None) -> str | None:
        tid = (team or {}).get("id")
        return "equipo_a" if tid == home_id else "equipo_b" if tid == away_id else None

    data = api.get("fixtures/lineups", {"fixture": fixture_id})
    for item in (data or {}).get("response", []):
        lado = lado_de(item.get("team"))
        if not lado:
            continue
        xi = _xi_de_item(item, "XI OFICIAL confirmado")
        if xi:
            out[lado]["xi_reciente"] = xi
    # sin XI oficial todavía: la formación del último partido, de la API
    for lado, tid in (("equipo_a", home_id), ("equipo_b", away_id)):
        if "xi_reciente" not in out[lado]:
            xi = _xi_ultimo_partido(api, tid)
            if xi:
                out[lado]["xi_reciente"] = xi

    data = api.get("injuries", {"fixture": fixture_id})
    bajas: dict[str, list[str]] = {"equipo_a": [], "equipo_b": []}
    for item in (data or {}).get("response", []):
        lado = lado_de(item.get("team"))
        if not lado:
            continue
        p = item.get("player") or {}
        bajas[lado].append(f"{p.get('name') or '?'} ({p.get('reason') or p.get('type') or 'baja'})")
    for lado, lista in bajas.items():
        if lista:
            out[lado]["bajas"] = "Bajas/lesiones reportadas: " + ", ".join(lista) + " [fuente: API-Football injuries]"
    return out


def _asegurar_plantillas(fx: dict) -> None:
    """Ingesta de jugadores de ambos equipos ANTES del análisis si falta:
    plantel/DT/bajas salen de API-Football (plan ya pagado, ~5-6 requests por
    equipo) en vez de búsquedas web (lo caro, por uso). El subproceso mantiene
    la escritura en la capa de ingesta; si falla o no hay clave, el análisis
    sigue y esos campos se investigan por la vía de siempre."""
    import subprocess
    import sys as _sys
    from backend import jugadores as jugcapa
    temporada = fx.get("league_season")
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = {**os.environ, "PYTHONPATH": raiz, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    for tid in (fx["home_team_id"], fx["away_team_id"]):
        try:
            if jugcapa.plantilla_de(tid)["jugadores"]:
                continue
            print(f"[efe] equipo {tid} sin plantilla: ingesta previa (API-Football, no web)", flush=True)
            cmd = [_sys.executable, "-u", "-m", "backend.ingesta.jugadores", "--equipo", str(tid)]
            if temporada:
                cmd += ["--temporada", str(temporada)]
            subprocess.run(cmd, cwd=saddb.BASE_DIR, env=env, timeout=180)
        except Exception as e:  # sin clave / timeout: no bloquea el análisis
            print(f"[efe] ingesta previa de {tid} no disponible: {e}", flush=True)


def _demo_activo() -> bool:
    return os.environ.get("SAD_EFE_DEMO", "").strip() == "1"


def _respuesta(estado: str, detalle: str | None = None, registro: dict | None = None) -> dict:
    return {"estado": estado, "detalle": detalle, "registro": registro}


def generar_efe(fixture_id: int, estado: str = "preliminar", permitir_frio: bool = False) -> dict:
    """Corre el análisis completo y guarda el veredicto (SÍNCRONO: solo para
    el hilo de trabajo y el modo demo). `permitir_frio` desactiva el candado
    de análisis frío para ESTA corrida (opt-in explícito a pagar el frío)."""
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
        _asegurar_plantillas(fx)  # plantel/DT/bajas por API-Football, no por web
        frescos_a, faltan_a = efedb.investigacion_de(equipo_a)
        frescos_b, faltan_b = efedb.investigacion_de(equipo_b)
        # solo los tipos del EFE: la despensa también guarda timeline_eventos
        # y meterlos aquí inflaría el prompt sin aportar al protocolo
        frescos_a = {k: v for k, v in frescos_a.items() if k in efedb.TIPOS}
        frescos_b = {k: v for k, v in frescos_b.items() if k in efedb.TIPOS}
        # lo que ya tenemos en sad.db (tabla, resultados, próximos partidos)
        # entra como dato cacheado y NO se busca en la web: costo cero.
        # XI oficial y lesiones vienen de API-Football (2 requests baratas).
        locales = _datos_locales(fx)
        xi_bajas = _xi_y_bajas(fixture_id, fx["home_team_id"], fx["away_team_id"])
        for frescos, faltan, lado in ((frescos_a, faltan_a, "equipo_a"),
                                      (frescos_b, faltan_b, "equipo_b")):
            for tipo, txt in {**locales[lado], **xi_bajas[lado]}.items():
                if txt and tipo in faltan:
                    frescos[tipo] = txt
                    faltan.remove(tipo)
        # cruce con la capa de jugadores (docs/JUGADORES.md): los indicadores
        # de NUESTRA base mandan sobre la búsqueda web en plantel/dt, y las
        # bajas se enriquecen con su PESO real (minutos, producción). Sin
        # ingesta de jugadores el resumen viene vacío y nada cambia.
        from backend import jugadores as jugcapa
        for frescos, faltan, tid in ((frescos_a, faltan_a, fx["home_team_id"]),
                                     (frescos_b, faltan_b, fx["away_team_id"])):
            for tipo, txt in jugcapa.resumen_para_skills(tid).items():
                if tipo == "bajas" and frescos.get("bajas"):
                    frescos["bajas"] = f"{frescos['bajas']} || {txt}"
                else:
                    frescos[tipo] = txt
                if tipo in faltan:
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
        # CANDADO DE ANÁLISIS FRÍO: cada campo faltante son ~1-2 búsquedas web
        # (lo caro). Sin despensa cargada, el análisis frío sale $0.6-1.2 — se
        # BLOQUEA antes de gastar un centavo y se guía al flujo gratis; pagar
        # el frío es opt-in explícito (permitir_frio / botón «Generar igual»).
        umbral_frio = int(os.environ.get("SAD_EFE_MAX_FALTANTES", "6"))
        if not permitir_frio and len(faltantes) > umbral_frio:
            raise RuntimeError(
                f"Análisis FRÍO bloqueado para no gastar de más: faltan {len(faltantes)} campos "
                f"({', '.join(faltantes)}). Carga la despensa gratis (botón «Copiar prompt» → "
                "Claude de escritorio → pegar el JSON aquí) y reintenta (~$0.10-0.20), o pulsa "
                "«Generar igual (frío)» si prefieres pagarlo ahora (~$0.6-1.2)."
            )

        # presupuesto de búsquedas PROPORCIONAL a lo faltante: con la despensa +
        # la capa de jugadores lo típico son 2-4 campos, no los 14 de un EFE
        # frío — dejar el techo fijo quemaba ~18 búsquedas (y sus tokens) igual.
        # El presupuesto viaja también en el payload para que el modelo lo
        # administre (sin esto, agotaba max_uses y concluía "sin herramienta").
        tope_busquedas = min(3 + 2 * len(faltantes), cliente.MAX_BUSQUEDAS)
        if faltantes:
            payload["presupuesto_busquedas"] = (
                f"Tienes {tope_busquedas} búsquedas web como máximo: adminístralas — "
                "una por campo faltante y solo repite si el resultado fue inútil."
            )
        print(f"[efe] faltantes ({len(faltantes)}): {', '.join(faltantes) or 'ninguno'}", flush=True)
        resultado, _uso = cliente.analizar(
            payload, EFE_COMPARATIVO, con_busqueda=bool(faltantes),
            max_busquedas=tope_busquedas,
            # caliente (0 faltantes): no re-emitir la despensa en el output
            salida=cliente.SALIDA_EFE if faltantes else cliente.SALIDA_EFE_CALIENTE,
        )

        # LA DESPENSA: lo investigado se separa del análisis y se deposita por
        # equipo con TTL — el siguiente análisis de estos equipos lo recibe en
        # datos_cacheados y busca solo lo vencido (de ~$0.50 a ~$0.10-0.20).
        # Solo los tipos que FALTABAN: lo que ya estaba fresco no se re-sella.
        def _depositar(res: dict) -> int:
            inv = res.pop("investigacion", None) or {}
            n = 0
            for lado, equipo, faltan in (("equipo_a", equipo_a, faltan_a),
                                         ("equipo_b", equipo_b, faltan_b)):
                datos = inv.get(lado) or {}
                for tipo in faltan:
                    contenido = (datos.get(tipo) or "").strip() if isinstance(datos.get(tipo), str) else ""
                    if contenido:
                        efedb.guardar_investigacion(equipo, tipo, contenido)
                        n += 1
            return n

        # Un análisis sin contenido real (ambos equipos en 0) NO se guarda
        # (cachearlo dejaría al usuario sin forma de regenerar), pero lo que SÍ
        # se investigó se salva IGUAL a la despensa: ya está pagado — el
        # reintento lo recibe como datos_cacheados y cuesta una fracción, en
        # vez de repagar el análisis fallido completo.
        if analisis_vacio(resultado):
            salvados = _depositar(resultado)
            print(f"[efe] análisis vacío: {salvados} datos investigados salvados a la despensa", flush=True)
            raise RuntimeError(
                "El análisis llegó vacío (scores en 0 — investigación fallida). No se guardó"
                + (f"; {salvados} datos investigados quedaron en la despensa y el reintento los aprovecha"
                   if salvados else "")
                + ": vuelve a pulsar «Generar análisis EFE» para reintentar."
            )
        depositados = _depositar(resultado)
        print(f"[efe] despensa: {depositados} datos depositados "
              f"({equipo_a} / {equipo_b})", flush=True)

    return efedb.guardar_analisis(
        "efe", fixture_id, equipo_a, equipo_b, fecha or "", estado,
        resultado, resultado.get("version_efe", VERSION_EFE),
    )


# ── infraestructura común de trabajos (EFE y TIMELINE) ──────────────────────

def _lanzar(tipo: str, fixture_id: int, generar, forzar: bool, nombre_boton: str) -> dict:
    """Patrón compartido: listo si ya existe, generando si hay hilo en curso,
    o lanza el trabajo. `generar` es el callable síncrono del modo."""
    clave = f"{tipo}:{fixture_id}"
    with _lock:
        trabajo = _trabajos.get(clave)
        if trabajo and trabajo["estado"] == "generando":
            return _respuesta("generando", detalle="análisis en curso")

    if forzar:
        efedb.borrar_analisis(tipo, fixture_id)
        print(f"[{tipo}] fixture {fixture_id}: regeneración forzada (previo descartado)", flush=True)
    else:
        existente = efedb.analisis_existente(tipo, fixture_id, "confirmado") \
            or efedb.analisis_existente(tipo, fixture_id, "preliminar")
        if existente:
            return _respuesta("listo", registro=existente)
    _fixture(fixture_id)  # 404 antes de encolar nada

    if _demo_activo():  # demo: rápido y sin API → síncrono
        return _respuesta("listo", registro=generar(fixture_id))
    if not cliente.hay_clave():
        raise SinClave("Falta ANTHROPIC_API_KEY en el entorno")

    def _trabajo() -> None:
        try:
            generar(fixture_id)
            with _lock:
                _trabajos.pop(clave, None)
            print(f"[{tipo}] fixture {fixture_id}: análisis guardado", flush=True)
        except Exception as e:  # el error queda consultable vía /estado
            with _lock:
                _trabajos[clave] = {"estado": "error", "detalle": str(e)}
            print(f"[{tipo}] ERROR fixture {fixture_id}: {e}", flush=True)

    with _lock:
        trabajo = _trabajos.get(clave)
        if trabajo and trabajo["estado"] == "generando":
            return _respuesta("generando", detalle="análisis en curso")
        # sin trabajo, o el anterior falló: se (re)lanza
        _trabajos[clave] = {"estado": "generando", "detalle": None}
    threading.Thread(target=_trabajo, daemon=True, name=f"{tipo}-{fixture_id}").start()
    print(f"[{tipo}] fixture {fixture_id}: análisis lanzado", flush=True)
    return _respuesta("generando", detalle=f"{nombre_boton} lanzado")


def _estado(tipo: str, fixture_id: int) -> dict:
    """Para el sondeo del frontend: listo / generando / error / nada."""
    existente = efedb.analisis_existente(tipo, fixture_id, "confirmado") \
        or efedb.analisis_existente(tipo, fixture_id, "preliminar")
    if existente:
        return _respuesta("listo", registro=existente)
    with _lock:
        trabajo = _trabajos.get(f"{tipo}:{fixture_id}")
    if trabajo:
        return _respuesta(trabajo["estado"], detalle=trabajo.get("detalle"))
    return _respuesta("nada")


def iniciar_efe(fixture_id: int, estado: str = "preliminar", forzar: bool = False,
                permitir_frio: bool = False) -> dict:
    return _lanzar("efe", fixture_id, lambda fid: generar_efe(fid, estado, permitir_frio),
                   forzar, "análisis EFE")


def estado_efe(fixture_id: int) -> dict:
    return _estado("efe", fixture_id)


# ── TIMELINE (modo futbol-timeline, prompts/TIMELINE_prompt.md) ──────────────

def generar_timeline(fixture_id: int, estado: str = "preliminar") -> dict:
    """Timeline comparativo de los dos equipos del fixture (SÍNCRONO: para el
    hilo de trabajo y el modo demo). Período: últimos 6 meses (default del
    protocolo); si hay EFE previo, hereda alertas y colores sin re-buscar."""
    existente = efedb.analisis_existente("timeline", fixture_id, estado)
    if existente:
        return existente

    fx = _fixture(fixture_id)
    equipo_a, equipo_b = fx["local"], fx["visitante"]
    fecha = (fx["date"] or "")[:10] or None

    if _demo_activo():
        resultado = demo.timeline_demo(equipo_a, equipo_b)
    else:
        if not cliente.hay_clave():
            raise SinClave("Falta ANTHROPIC_API_KEY en el entorno")
        from datetime import datetime, timedelta, timezone
        hasta = datetime.now(timezone.utc).date()
        desde = hasta - timedelta(days=182)  # default del protocolo: 6 meses

        # contexto del EFE previo (si existe): alertas activas y colores —
        # cero búsquedas duplicadas entre los dos modos
        contexto: dict = {}
        efe_previo = efedb.analisis_existente("efe", fixture_id, "confirmado") \
            or efedb.analisis_existente("efe", fixture_id, "preliminar")
        if efe_previo:
            r = efe_previo["resultado"]
            contexto = {
                "alertas_activas": [a.get("codigo", "") for a in r.get("alertas", [])],
                "colores": {equipo_a: r.get("equipos", {}).get("a", {}).get("color", ""),
                            equipo_b: r.get("equipos", {}).get("b", {}).get("color", "")},
                "hitos_detectados": [],
            }

        # datos cacheados: eventos de timelines previos (despensa) + resultados
        # reales de NUESTRA base (costo cero, la web solo completa el contexto)
        cacheados: dict = {}
        from backend import jugadores as jugcapa
        for equipo, tid in ((equipo_a, fx["home_team_id"]), (equipo_b, fx["away_team_id"])):
            frescos, _falt = efedb.investigacion_de(equipo)
            entrada: dict = {"resultados_db": _resultados_de(tid)}
            if "timeline_eventos" in frescos:
                entrada["timeline_eventos"] = frescos["timeline_eventos"]
            # traspasos y DT con fechas exactas de nuestra base: eventos
            # confirmados — la web queda para el contexto narrativo
            movimientos = jugcapa.movimientos_para_timeline(tid)
            if movimientos:
                entrada["movimientos_db"] = movimientos
            cacheados[equipo] = entrada

        payload = {
            "modo": "timeline",
            "equipos": [equipo_a, equipo_b],
            "periodo": {"desde": desde.isoformat(), "hasta": hasta.isoformat()},
            "tipos": ["todos"],
            "contexto_efe": contexto,
            "datos_cacheados": cacheados,
        }
        resultado, _uso = cliente.analizar(
            payload, TIMELINE, con_busqueda=True,
            system=cliente.bloques_system_timeline(), salida=cliente.SALIDA_TIMELINE,
            max_busquedas=cliente.BUSQUEDAS_TIMELINE, modelo=cliente.MODELO_TIMELINE,
        )
        if timeline_vacio(resultado):
            raise RuntimeError(
                "El timeline llegó sin eventos (investigación fallida). "
                "No se guardó: vuelve a pulsar «Generar timeline» para reintentar."
            )
        # despensa del timeline: eventos confirmados por equipo, reutilizables
        # por el próximo timeline que solape el período (tipo timeline_eventos)
        por_equipo: dict[str, list] = {equipo_a: [], equipo_b: []}
        for ev in resultado.get("eventos", []):
            if ev.get("equipo") == "ambos":
                por_equipo[equipo_a].append(ev)
                por_equipo[equipo_b].append(ev)
            elif ev.get("equipo") in por_equipo:
                por_equipo[ev["equipo"]].append(ev)
        for equipo, evs in por_equipo.items():
            if evs:
                efedb.guardar_investigacion(equipo, "timeline_eventos", evs,
                                            resultado.get("fuentes", []))

    return efedb.guardar_analisis(
        "timeline", fixture_id, equipo_a, equipo_b, fecha or "", estado,
        resultado, VERSION_EFE,
    )


def iniciar_timeline(fixture_id: int, forzar: bool = False) -> dict:
    return _lanzar("timeline", fixture_id, generar_timeline, forzar, "timeline")


def estado_timeline(fixture_id: int) -> dict:
    return _estado("timeline", fixture_id)


def analisis_del_partido(fixture_id: int) -> list[dict]:
    """Todo lo emitido para un fixture (lectura pura, cero créditos)."""
    return efedb.analisis_de_fixture(fixture_id)
