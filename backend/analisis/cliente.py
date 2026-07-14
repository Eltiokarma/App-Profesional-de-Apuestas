"""Cliente de la API de Claude para la capa EFE+DTP.

- System de dos bloques con prompt caching (protocolo EFE + instrucciones API);
  en caché caliente la lectura cuesta ~10% del precio de input.
- El JSON se pide POR INSTRUCCIÓN (el system prompt exige "exclusivamente
  JSON válido") y se normaliza con esquemas.ajustar() — structured outputs
  rechazó el esquema del EFE dos veces (límite de uniones y "compiled
  grammar is too large"): es demasiado rico para ese mecanismo.
- Web search (web_search_20260209) SOLO cuando hay campos faltantes: es lo
  caro (~$10/1000 búsquedas + tokens).
- El modelo se elige por tarea: Sonnet 5 para razonar el protocolo, Haiku
  para normalizaciones mecánicas (modo extraccion, futuro).
"""
import json
import os

from backend.analisis.esquemas import ajustar

MODELO = os.environ.get("SAD_EFE_MODELO", "claude-sonnet-5")
# Con la investigación real activa (18 búsquedas) el razonamiento + el JSON
# del EFE no cabían en 16k → stop_reason=max_tokens. Tope amplio + STREAMING
# (obligatorio por encima de ~16k para no chocar con timeouts HTTP del SDK).
MAX_TOKENS = int(os.environ.get("SAD_EFE_MAX_TOKENS", "64000"))
# Un EFE completo investiga ~7 tipos de datos por equipo (14 en total): con un
# tope bajo el modelo agota las búsquedas, recibe bloques de error
# (max_uses_exceeded) y concluye "herramienta no disponible" → análisis en ceros.
MAX_BUSQUEDAS = int(os.environ.get("SAD_EFE_BUSQUEDAS", "18"))

# Precios de claude-sonnet-5 por millón de tokens (intro hasta 2026-08-31:
# $2 input / $10 output; caché: escritura 1.25×, lectura 0.1×) y $10 por
# 1000 búsquedas web. Solo para el log de costo estimado por corrida.
_PRECIO = {"input": 2.0, "output": 10.0, "cache_write": 2.5, "cache_read": 0.2}
_PRECIO_BUSQUEDA = 0.01

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
_MARCA_BLOQUE2 = "## INSTRUCCIONES DE EJECUCIÓN API"


def _leer(nombre: str) -> str:
    with open(os.path.join(_PROMPTS_DIR, nombre), encoding="utf-8") as f:
        return f.read()


def bloques_system() -> list[dict]:
    """[protocolo EFE, instrucciones API] — ambos con cache_control."""
    efe = _leer("EFE_v1_5_prompt.md")
    api = _leer("SYSTEM_PROMPT_SAD_API.md")
    # el archivo trae una cabecera de uso; el bloque real arranca en la marca
    pos = api.find(_MARCA_BLOQUE2)
    if pos != -1:
        api = api[pos:]
    return [
        {"type": "text", "text": efe, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": api, "cache_control": {"type": "ephemeral"}},
    ]


def hay_clave() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def _extraer_json(texto: str) -> dict:
    """JSON del texto del modelo, tolerante a envoltorios (```json … ```)."""
    t = texto.strip()
    inicio, fin = t.find("{"), t.rfind("}")
    if inicio == -1 or fin <= inicio:
        raise RuntimeError("la respuesta no contiene JSON")
    try:
        return json.loads(t[inicio:fin + 1])
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON inválido en la respuesta: {e}") from e


def analizar(payload: dict, esquema: dict, con_busqueda: bool) -> tuple[dict, dict]:
    """Una llamada al modo del payload. Devuelve (resultado, uso).

    `uso` trae los contadores de tokens para vigilar caché y costo en logs.
    Lanza RuntimeError si no hay ANTHROPIC_API_KEY.
    """
    if not hay_clave():
        raise RuntimeError("Falta ANTHROPIC_API_KEY (variable de entorno en Railway)")
    import anthropic  # import tardío: el resto del backend no lo necesita

    client = anthropic.Anthropic()
    # refuerzo explícito: la salida es SOLO el objeto JSON del esquema del modo
    payload = {**payload, "salida": "EXCLUSIVAMENTE el objeto JSON del esquema del modo, sin texto adicional ni markdown"}
    kwargs: dict = {
        "model": MODELO,
        "max_tokens": MAX_TOKENS,
        "system": bloques_system(),
        "messages": [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
    }
    if con_busqueda:
        kwargs["tools"] = [{"type": "web_search_20260209", "name": "web_search",
                            "max_uses": MAX_BUSQUEDAS}]

    # STREAMING: con max_tokens grandes (64k) el create() normal choca con los
    # timeouts HTTP del SDK; el stream mantiene la conexión viva los 1-5 min.
    def _llamada():
        with client.messages.stream(**kwargs) as stream:
            return stream.get_final_message()

    # el uso se ACUMULA entre reanudes: cada pause_turn es otra request cobrada
    uso = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    hechas = 0
    errores: list[str] = []

    def _sumar(r) -> None:
        nonlocal hechas
        uso["input"] += r.usage.input_tokens
        uso["output"] += r.usage.output_tokens
        uso["cache_write"] += getattr(r.usage, "cache_creation_input_tokens", 0) or 0
        uso["cache_read"] += getattr(r.usage, "cache_read_input_tokens", 0) or 0
        stu = getattr(r.usage, "server_tool_use", None)
        hechas += getattr(stu, "web_search_requests", 0) or 0
        # los errores de búsqueda NO lanzan excepción: llegan como bloques de
        # resultado con error_code (p. ej. max_uses_exceeded) — se registran aquí
        for b in r.content:
            if getattr(b, "type", "") == "web_search_tool_result" \
                    and not isinstance(getattr(b, "content", None), list):
                code = getattr(b.content, "error_code", None)
                if code:
                    errores.append(code)

    respuesta = _llamada()
    _sumar(respuesta)
    # las herramientas de servidor pueden pausar el turno: se reanuda tal cual
    reanudes = 0
    while respuesta.stop_reason == "pause_turn" and reanudes < 5:
        kwargs["messages"] = kwargs["messages"] + [
            {"role": "assistant", "content": respuesta.content}
        ]
        respuesta = _llamada()
        _sumar(respuesta)
        reanudes += 1

    costo = (uso["input"] * _PRECIO["input"] + uso["output"] * _PRECIO["output"]
             + uso["cache_write"] * _PRECIO["cache_write"]
             + uso["cache_read"] * _PRECIO["cache_read"]) / 1_000_000 \
        + hechas * _PRECIO_BUSQUEDA
    print(f"[efe] {MODELO} · in={uso['input']} out={uso['output']} "
          f"cache_write={uso['cache_write']} cache_read={uso['cache_read']} "
          f"busqueda={'sí' if con_busqueda else 'no'} hechas={hechas} "
          f"max={MAX_BUSQUEDAS} costo≈${costo:.2f}"
          + (f" errores_busqueda={errores}" if errores else ""), flush=True)

    texto = next((b.text for b in reversed(respuesta.content) if b.type == "text"), None)
    if respuesta.stop_reason == "refusal" or texto is None:
        raise RuntimeError(f"La API no devolvió análisis (stop_reason={respuesta.stop_reason})")
    if respuesta.stop_reason == "max_tokens":
        raise RuntimeError(
            f"Análisis truncado (max_tokens={MAX_TOKENS}): pulsa Regenerar; "
            "si se repite, sube SAD_EFE_MAX_TOKENS en Railway"
        )

    # normalizado contra el esquema: el frontend recibe SIEMPRE la forma exacta
    return ajustar(_extraer_json(texto), esquema), uso
