"""JSON Schema del contrato EFE_COMPARATIVO (structured outputs).

Espejo del esquema de prompts/SYSTEM_PROMPT_SAD_API.md, endurecido para
`output_config.format`: todos los objetos con additionalProperties=false y
todas las claves requeridas.

REGLA DURA de structured outputs: máximo 16 parámetros con uniones de tipos
(anyOf / type arrays) — la primera versión tenía 92 nullables y la API la
rechazó con 400. Por eso aquí NO hay nullables: lo que no aplica va como
"" (texto), 0 (número) o false (booleano), y el frontend lo trata igual.
"""


def _obj(props: dict) -> dict:
    return {
        "type": "object",
        "properties": props,
        "required": list(props),
        "additionalProperties": False,
    }


def _arr(items: dict) -> dict:
    return {"type": "array", "items": items}


_STR = {"type": "string"}          # "" si no aplica / se desconoce
_NUM = {"type": "number"}          # 0 si no aplica
_BOOL = {"type": "boolean"}
_ESTADO_IND = {"type": "string", "enum": ["verde", "ambar", "rojo"]}
_ESTADO_H2 = {"type": "string", "enum": ["verde", "ambar", "rojo", "na"]}

INDICADOR = _obj({
    "id": _STR,
    "estado": _ESTADO_IND,
    "justificacion": _STR,
    "fuente": _STR,  # "" si no hay fuente puntual
})

# Forma única para los bloques A-E: los campos que no aplican van en 0/false/"".
BLOQUE = _obj({
    "score": _NUM,
    "max": _NUM,
    "ponderado": _NUM,           # score × peso (igual al score en A, C y D)
    "excluido": _BOOL,           # solo C (SIN DATOS K / R-KT.2)
    "motivo_exclusion": _STR,
    "d3_cap_aplicado": _BOOL,    # solo D
    "ppp": _NUM,                 # solo E; 0 si no aplica
    "indicadores": _arr(INDICADOR),
})

JUGADOR = _obj({
    "nombre": _STR,
    "posicion": _STR,
    "zona": {"type": "string", "enum": ["GK", "DEF", "MID", "ATK"]},
    "rol": {"type": "string", "enum": ["TF", "TH", "ROT", "SUP"]},
    "apps": _STR,
    "estado": {"type": "string", "enum": ["disponible", "baja", "duda"]},
    "motivo": _STR,
})

DISPONIBILIDAD = _obj({
    "jugadores": _arr(JUGADOR),
    "ip": _NUM,
    "ip_nivel": _ESTADO_IND,
    "multiplicador_gk_aplicado": _BOOL,
    "reduccion_zonas": _obj({"GK": _NUM, "DEF": _NUM, "MID": _NUM, "ATK": _NUM}),
    "f4": _obj({"rotados": {"type": "integer"}, "diagnostico": _STR}),
    "f5_factor_x": _arr(_obj({"nombre": _STR, "contexto": _STR})),
})

CALENDARIO_ITEM = _obj({
    "rival": _STR,
    "fecha": _STR,
    "condicion": {"type": "string", "enum": ["L", "V"]},
    "etiquetas": _arr(_STR),
    "posicion": {"type": "integer"},  # 0 si se desconoce
    "nota": _STR,
})

EQUIPO = _obj({
    "color": _STR,
    "color_light": _STR,
    "color_mid": _STR,
    "bloques": _obj({"A": BLOQUE, "B": BLOQUE, "C": BLOQUE, "D": BLOQUE, "E": BLOQUE}),
    "total": _NUM,
    "maximo_alcanzable": _NUM,
    "porcentaje": _NUM,
    "clasificacion": {"type": "string", "enum": ["FORMADO", "EN_FORMACION", "SIN_FORMACION"]},
    "disponibilidad": DISPONIBILIDAD,
    "dt": _obj({"nombre": _STR, "asuncion": _STR, "meses": _NUM}),
    "calendario": _arr(CALENDARIO_ITEM),
})

PERFIL_TACTICO = _obj({
    "sistema": _STR,
    "estilo": _STR,
    "fortaleza": _STR,
    "vulnerabilidad": _STR,
})

EFE_COMPARATIVO = _obj({
    "version_efe": _STR,
    "partido": _obj({
        "equipo_a": _STR,
        "equipo_b": _STR,
        "torneo": _STR,
        "fase": _STR,
        "estadio": _STR,
        "fecha": _STR,
        "hora": _STR,
        "condicion": _obj({"a": {"type": "string", "enum": ["L", "V"]},
                           "b": {"type": "string", "enum": ["L", "V"]}}),
    }),
    "equipos": _obj({"a": EQUIPO, "b": EQUIPO}),
    "matchup_h": _obj({
        "perfil_a": PERFIL_TACTICO,
        "perfil_b": PERFIL_TACTICO,
        "h2a": _ESTADO_H2,
        "h2b": _ESTADO_H2,
        "h2c": _ESTADO_H2,
        "diagnostico": {"type": "string", "enum": ["FAVORABLE", "NEUTRO", "DESFAVORABLE"]},
        "razon": _STR,
    }),
    "alertas": _arr(_obj({
        "codigo": _STR,
        "tipo": {"type": "string", "enum": ["estructural", "fecha"]},
        "equipo": {"type": "string", "enum": ["a", "b", "ambos", "global"]},
        "detalle": _STR,
    })),
    "lectura_sad": _obj({
        "modulo_operativo": _STR,
        "un_x_dos": _obj({"texto": _STR, "rango_ampliado": _BOOL}),
        "contexto_emocional": _STR,
        "dato_estructural": _STR,
        "paradoja": _STR,  # "" si no hay paradoja
    }),
    "datos_faltantes": _arr(_STR),
    "fuentes": _arr(_STR),
})
