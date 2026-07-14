"""Orquestación del análisis EFE (fase 1 del plan).

Flujo de POST /api/v1/analisis/efe {fixtureId}:
  1. ¿ya hay análisis para ese fixture y estado? → devolverlo (0 créditos)
  2. leer la despensa (investigacion) de ambos equipos → fresco vs faltante
  3. llamada a la API: system cacheado + user {modo, partido, datos_cacheados,
     campos_faltantes}; web search SOLO si hay faltantes
  4. structured output contra EFE_COMPARATIVO → JSON válido garantizado
  5. guardar el veredicto en analisis y devolverlo

Modo demo (SAD_EFE_DEMO=1): análisis de muestra determinista, sin API.
"""
import os

from backend import db as saddb
from backend.analisis import cliente, demo
from backend.analisis import db as efedb
from backend.analisis.esquemas import EFE_COMPARATIVO

VERSION_EFE = "1.5"


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


def generar_efe(fixture_id: int, estado: str = "preliminar") -> dict:
    """Genera (o devuelve, si ya existe) el EFE comparativo del fixture."""
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

    return efedb.guardar_analisis(
        "efe", fixture_id, equipo_a, equipo_b, fecha or "", estado,
        resultado, resultado.get("version_efe", VERSION_EFE),
    )


def analisis_del_partido(fixture_id: int) -> list[dict]:
    """Todo lo emitido para un fixture (lectura pura, cero créditos)."""
    return efedb.analisis_de_fixture(fixture_id)
