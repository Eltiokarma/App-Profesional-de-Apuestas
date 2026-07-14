"""Análisis EFE de muestra para el modo demo (SAD_EFE_DEMO=1).

Determinista y con la MISMA forma que el contrato EFE_COMPARATIVO (sin
nullables: "" / 0 / false donde no aplica — regla del esquema). Permite
desarrollar la UI y correr test_api sin gastar créditos ni tener clave.
"""


def _bloque(score: float, maximo: float, indicadores: list[tuple[str, str, str]],
            ponderado: float | None = None, ppp: float = 0) -> dict:
    return {
        "score": score, "max": maximo,
        "ponderado": ponderado if ponderado is not None else score,
        "excluido": False, "motivo_exclusion": "",
        "d3_cap_aplicado": False, "ppp": ppp,
        "indicadores": [
            {"id": i, "estado": e, "justificacion": j, "fuente": "demo"}
            for i, e, j in indicadores
        ],
    }


def _equipo(nombre: str, color: str, porcentaje: float, clasificacion: str) -> dict:
    return {
        "color": color, "color_light": color + "33", "color_mid": color + "88",
        "bloques": {
            "A": _bloque(3, 4, [("A1", "verde", f"DT de {nombre} cumple 14 meses en el cargo")]),
            "B": _bloque(4.5, 6, [("B1", "verde", "78% de titulares con ≥9 meses"),
                                  ("B6", "ambar", "GK nuevo con 22 partidos en la categoría")],
                         ponderado=6.75),
            "C": _bloque(3, 4, [("C1", "verde", "Ciclos limpios en las K")]),
            "D": _bloque(3, 4, [("D3", "ambar", "Respuesta parcial a rachas negativas")]),
            "E": _bloque(2, 3, [("E2", "ambar", "1.55 puntos por partido")], ponderado=4, ppp=1.55),
        },
        "total": 21.25, "maximo_alcanzable": 27,
        "porcentaje": porcentaje, "clasificacion": clasificacion,
        "disponibilidad": {
            "jugadores": [
                {"nombre": "Portero Uno", "posicion": "GK", "zona": "GK", "rol": "TF",
                 "apps": "11/12", "estado": "disponible", "motivo": ""},
                {"nombre": "Delantero Diez", "posicion": "DC", "zona": "ATK", "rol": "TF",
                 "apps": "10/12", "estado": "duda", "motivo": "Sobrecarga muscular"},
            ],
            "ip": 1.5, "ip_nivel": "verde", "multiplicador_gk_aplicado": False,
            "reduccion_zonas": {"GK": 0, "DEF": 0, "MID": 0, "ATK": 25},
            "f4": {"rotados": 1, "diagnostico": "Rotación puntual sin caída de nivel"},
            "f5_factor_x": [],
        },
        "dt": {"nombre": f"DT de {nombre}", "asuncion": "2025-05-01", "meses": 14},
        "calendario": [
            {"rival": "Rival Próximo", "fecha": "2026-07-20", "condicion": "L",
             "etiquetas": ["🏠 LOCAL FUERTE"], "posicion": 4, "nota": ""},
        ],
    }


def efe_demo(equipo_a: str, equipo_b: str, torneo: str | None, fecha: str | None) -> dict:
    return {
        "version_efe": "1.5",
        "partido": {
            "equipo_a": equipo_a, "equipo_b": equipo_b,
            "torneo": torneo or "", "fase": "", "estadio": "",
            "fecha": fecha or "", "hora": "",
            "condicion": {"a": "L", "b": "V"},
        },
        "equipos": {
            "a": _equipo(equipo_a, "#5B8DEF", 79, "FORMADO"),
            "b": _equipo(equipo_b, "#E5484D", 58, "EN_FORMACION"),
        },
        "matchup_h": {
            "perfil_a": {"sistema": "4-3-3", "estilo": "posesión", "fortaleza": "juego aéreo",
                         "vulnerabilidad": "espaldas de los laterales"},
            "perfil_b": {"sistema": "5-3-2", "estilo": "bloque bajo", "fortaleza": "contraataque",
                         "vulnerabilidad": "centrales lentos en centros"},
            "h2a": "verde", "h2b": "ambar", "h2c": "verde",
            "diagnostico": "FAVORABLE",
            "razon": "El juego aéreo del local explota la debilidad del bloque bajo visitante",
        },
        "alertas": [
            {"codigo": "G-BLOQUE", "tipo": "fecha", "equipo": "b",
             "detalle": "Bloque bajo con vida útil táctica de 55-65 minutos"},
        ],
        "lectura_sad": {
            "modulo_operativo": "Módulos de goles por franja 60-80' especialmente relevantes",
            "un_x_dos": {"texto": "Ligero favoritismo local, sin valor claro en el empate",
                         "rango_ampliado": False},
            "contexto_emocional": "Sin carga emocional extra: partido de liga estándar",
            "dato_estructural": "El local absorbe rotaciones sin caída (F4 refuerza B5)",
            "paradoja": "",
        },
        "datos_faltantes": ["xi_confirmado_a", "xi_confirmado_b"],
        "fuentes": ["demo"],
    }
