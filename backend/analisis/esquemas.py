"""JSON Schema del contrato EFE_COMPARATIVO (structured outputs).

Espejo del esquema definido en prompts/SYSTEM_PROMPT_SAD_API.md, endurecido
para `output_config.format`: todos los objetos con additionalProperties=false
y todas las claves en required (lo opcional se modela como nullable). Así la
API garantiza JSON válido — sin "sin preámbulo, sin backticks" frágil.
"""


def _obj(props: dict) -> dict:
    return {
        "type": "object",
        "properties": props,
        "required": list(props),
        "additionalProperties": False,
    }


def _nul(tipo: str) -> dict:
    return {"anyOf": [{"type": tipo}, {"type": "null"}]}


def _arr(items: dict) -> dict:
    return {"type": "array", "items": items}


_ESTADO_IND = {"type": "string", "enum": ["verde", "ambar", "rojo"]}

INDICADOR = _obj({
    "id": {"type": "string"},
    "estado": _ESTADO_IND,
    "justificacion": {"type": "string"},
    "fuente": _nul("string"),
})

# Forma única para los bloques A-E: los campos que no aplican van en null.
BLOQUE = _obj({
    "score": {"type": "number"},
    "max": {"type": "number"},
    "ponderado": _nul("number"),          # solo B y E
    "excluido": _nul("boolean"),          # solo C (SIN DATOS K / R-KT.2)
    "motivo_exclusion": _nul("string"),
    "d3_cap_aplicado": _nul("boolean"),   # solo D
    "ppp": _nul("number"),                # solo E
    "indicadores": _arr(INDICADOR),
})

JUGADOR = _obj({
    "nombre": {"type": "string"},
    "posicion": {"type": "string"},
    "zona": {"type": "string", "enum": ["GK", "DEF", "MID", "ATK"]},
    "rol": {"type": "string", "enum": ["TF", "TH", "ROT", "SUP"]},
    "apps": _nul("string"),
    "estado": {"type": "string", "enum": ["disponible", "baja", "duda"]},
    "motivo": _nul("string"),
})

DISPONIBILIDAD = _obj({
    "jugadores": _arr(JUGADOR),
    "ip": {"type": "number"},
    "ip_nivel": {"type": "string", "enum": ["verde", "ambar", "rojo"]},
    "multiplicador_gk_aplicado": {"type": "boolean"},
    "reduccion_zonas": _obj({
        "GK": {"type": "number"}, "DEF": {"type": "number"},
        "MID": {"type": "number"}, "ATK": {"type": "number"},
    }),
    "f4": _obj({"rotados": {"type": "integer"}, "diagnostico": {"type": "string"}}),
    "f5_factor_x": _arr(_obj({"nombre": {"type": "string"}, "contexto": {"type": "string"}})),
})

CALENDARIO_ITEM = _obj({
    "rival": {"type": "string"},
    "fecha": _nul("string"),
    "condicion": {"type": "string", "enum": ["L", "V"]},
    "etiquetas": _arr({"type": "string"}),
    "posicion": _nul("integer"),
    "nota": _nul("string"),
})

EQUIPO = _obj({
    "color": {"type": "string"},
    "color_light": {"type": "string"},
    "color_mid": {"type": "string"},
    "bloques": _obj({"A": BLOQUE, "B": BLOQUE, "C": BLOQUE, "D": BLOQUE, "E": BLOQUE}),
    "total": {"type": "number"},
    "maximo_alcanzable": {"type": "number"},
    "porcentaje": {"type": "number"},
    "clasificacion": {"type": "string", "enum": ["FORMADO", "EN_FORMACION", "SIN_FORMACION"]},
    "disponibilidad": DISPONIBILIDAD,
    "dt": _obj({"nombre": {"type": "string"}, "asuncion": _nul("string"), "meses": _nul("number")}),
    "calendario": _arr(CALENDARIO_ITEM),
})

PERFIL_TACTICO = _obj({
    "sistema": _nul("string"),
    "estilo": _nul("string"),
    "fortaleza": _nul("string"),
    "vulnerabilidad": _nul("string"),
})

EFE_COMPARATIVO = _obj({
    "version_efe": {"type": "string"},
    "partido": _obj({
        "equipo_a": {"type": "string"},
        "equipo_b": {"type": "string"},
        "torneo": _nul("string"),
        "fase": _nul("string"),
        "estadio": _nul("string"),
        "fecha": _nul("string"),
        "hora": _nul("string"),
        "condicion": _obj({"a": {"type": "string", "enum": ["L", "V"]},
                           "b": {"type": "string", "enum": ["L", "V"]}}),
    }),
    "equipos": _obj({"a": EQUIPO, "b": EQUIPO}),
    "matchup_h": _obj({
        "perfil_a": PERFIL_TACTICO,
        "perfil_b": PERFIL_TACTICO,
        "h2a": _nul("string"),
        "h2b": _nul("string"),
        "h2c": _nul("string"),
        "diagnostico": {"type": "string", "enum": ["FAVORABLE", "NEUTRO", "DESFAVORABLE"]},
        "razon": {"type": "string"},
    }),
    "alertas": _arr(_obj({
        "codigo": {"type": "string"},
        "tipo": {"type": "string", "enum": ["estructural", "fecha"]},
        "equipo": _nul("string"),  # "a" | "b" | null (global)
        "detalle": {"type": "string"},
    })),
    "lectura_sad": _obj({
        "modulo_operativo": {"type": "string"},
        "un_x_dos": _obj({"texto": {"type": "string"}, "rango_ampliado": {"type": "boolean"}}),
        "contexto_emocional": {"type": "string"},
        "dato_estructural": {"type": "string"},
        "paradoja": _nul("string"),
    }),
    "datos_faltantes": _arr({"type": "string"}),
    "fuentes": _arr({"type": "string"}),
})
