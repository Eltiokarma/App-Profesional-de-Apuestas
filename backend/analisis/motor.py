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
        "SELECT f.id, f.date, ht.name AS local, at.name AS visitante, l.name AS liga "
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
        resultado, _uso = cliente.analizar(payload, EFE_COMPARATIVO,
                                           con_busqueda=bool(faltantes))
        # Un análisis sin contenido real (ambos equipos en 0) NO se guarda:
        # cachearlo dejaría al usuario sin forma de regenerar.
        if analisis_vacio(resultado):
            raise RuntimeError(
                "El análisis llegó vacío (scores en 0 — investigación fallida). "
                "No se guardó: vuelve a pulsar «Generar análisis EFE» para reintentar."
            )

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


def iniciar_efe(fixture_id: int, estado: str = "preliminar") -> dict:
    """Respuesta inmediata: listo (con registro), generando, o lanza el hilo."""
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
