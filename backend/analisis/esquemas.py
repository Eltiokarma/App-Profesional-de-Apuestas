"""Esquema del contrato EFE_COMPARATIVO + normalizador.

Historia de dos rechazos de la API con structured outputs: (1) 92 campos
anulables > límite de 16 uniones; (2) sin uniones, "compiled grammar is too
large" — el esquema del EFE es demasiado rico para ese mecanismo. Por eso el
JSON se pide POR INSTRUCCIÓN (el system prompt ya exige "exclusivamente JSON
válido") y este módulo lo NORMALIZA contra el esquema con ajustar(): claves
faltantes o null se rellenan con ""/0/false/[], enums inválidos se corrigen,
y el frontend recibe siempre la forma exacta del contrato.
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

# La DESPENSA: lo que el modelo investigó, devuelto junto al análisis para
# guardarlo por equipo con TTL y NO volver a pagarlo en el siguiente análisis.
# Claves en sintonía con db.TIPOS (dt/plantel 14d · fixture 7d · xi/bajas 48h ·
# tabla/resultados 24h). Cada campo es un resumen textual denso; "" = no investigado.
DESPENSA_EQUIPO = _obj({
    "dt": _STR, "plantel": _STR, "tabla": _STR, "resultados": _STR,
    "fixture": _STR, "xi_reciente": _STR, "bajas": _STR,
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
    # la despensa viaja DENTRO de la respuesta y el motor la separa: se guarda
    # en la tabla investigacion (no en el análisis) para abaratar los siguientes
    "investigacion": _obj({"equipo_a": DESPENSA_EQUIPO, "equipo_b": DESPENSA_EQUIPO}),
})


def ajustar(dato, esquema: dict):
    """Normaliza `dato` a la forma exacta del esquema: claves faltantes o en
    null → ""/0/false/[] según el tipo; enums inválidos → primer valor; los
    extras se descartan. Garantiza al frontend el contrato completo."""
    t = esquema.get("type")
    if t == "object":
        base = dato if isinstance(dato, dict) else {}
        return {k: ajustar(base.get(k), sub) for k, sub in esquema["properties"].items()}
    if t == "array":
        return [ajustar(x, esquema["items"]) for x in (dato if isinstance(dato, list) else [])]
    if t == "string":
        valores = esquema.get("enum")
        if valores:
            return dato if dato in valores else valores[0]
        return dato if isinstance(dato, str) else ("" if dato is None else str(dato))
    if t == "number":
        return _numero(dato, float, 0.0)
    if t == "integer":
        return _numero(dato, lambda v: int(float(v)), 0)
    if t == "boolean":
        return dato if isinstance(dato, bool) else False
    return dato


def _numero(dato, convertir, defecto):
    """Coerción numérica tolerante: acepta números y strings numéricos
    ("3.5", "3,5", "75%") — el modelo a veces emite cifras como texto y
    convertirlas a 0 destruiría un análisis válido."""
    if isinstance(dato, bool):
        return defecto
    if isinstance(dato, (int, float)):
        return convertir(dato)
    if isinstance(dato, str):
        limpio = dato.strip().replace(",", ".").rstrip("%").strip()
        try:
            return convertir(limpio)
        except ValueError:
            return defecto
    return defecto


def analisis_vacio(resultado: dict) -> bool:
    """True si un EFE_COMPARATIVO quedó sin contenido real: ambos equipos con
    total y porcentaje en 0 (síntoma de investigación fallida — p. ej. el
    modelo creyó que la búsqueda web no estaba disponible)."""
    try:
        equipos = resultado["equipos"]
        return all(
            float(equipos[k]["total"]) == 0 and float(equipos[k]["porcentaje"]) == 0
            for k in ("a", "b")
        )
    except (KeyError, TypeError, ValueError):
        return True
