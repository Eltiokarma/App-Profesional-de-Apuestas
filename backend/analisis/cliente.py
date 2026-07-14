"""Cliente de la API de Claude para la capa EFE+DTP.

- System de dos bloques con prompt caching (protocolo EFE + instrucciones API);
  en caché caliente la lectura cuesta ~10% del precio de input.
- Structured outputs (`output_config.format`): el JSON llega válido contra el
  esquema, sin parseos frágiles.
- Web search (web_search_20260209) SOLO cuando hay campos faltantes: es lo
  caro (~$10/1000 búsquedas + tokens).
- El modelo se elige por tarea: Sonnet 5 para razonar el protocolo, Haiku
  para normalizaciones mecánicas (modo extraccion, futuro).
"""
import json
import os

MODELO = os.environ.get("SAD_EFE_MODELO", "claude-sonnet-5")
MAX_TOKENS = 16_000
MAX_BUSQUEDAS = 6

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


def analizar(payload: dict, esquema: dict, con_busqueda: bool) -> tuple[dict, dict]:
    """Una llamada al modo del payload. Devuelve (resultado, uso).

    `uso` trae los contadores de tokens para vigilar caché y costo en logs.
    Lanza RuntimeError si no hay ANTHROPIC_API_KEY.
    """
    if not hay_clave():
        raise RuntimeError("Falta ANTHROPIC_API_KEY (variable de entorno en Railway)")
    import anthropic  # import tardío: el resto del backend no lo necesita

    client = anthropic.Anthropic()
    kwargs: dict = {
        "model": MODELO,
        "max_tokens": MAX_TOKENS,
        "system": bloques_system(),
        "messages": [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        "output_config": {"format": {"type": "json_schema", "schema": esquema}},
    }
    if con_busqueda:
        kwargs["tools"] = [{"type": "web_search_20260209", "name": "web_search",
                            "max_uses": MAX_BUSQUEDAS}]

    respuesta = client.messages.create(**kwargs)
    # las herramientas de servidor pueden pausar el turno: se reanuda tal cual
    reanudes = 0
    while respuesta.stop_reason == "pause_turn" and reanudes < 5:
        kwargs["messages"] = kwargs["messages"] + [
            {"role": "assistant", "content": respuesta.content}
        ]
        respuesta = client.messages.create(**kwargs)
        reanudes += 1

    texto = next((b.text for b in reversed(respuesta.content) if b.type == "text"), None)
    if respuesta.stop_reason == "refusal" or texto is None:
        raise RuntimeError(f"La API no devolvió análisis (stop_reason={respuesta.stop_reason})")
    if respuesta.stop_reason == "max_tokens":
        raise RuntimeError("Análisis truncado (max_tokens): reintentar")

    uso = {
        "input": respuesta.usage.input_tokens,
        "output": respuesta.usage.output_tokens,
        "cache_write": getattr(respuesta.usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read": getattr(respuesta.usage, "cache_read_input_tokens", 0) or 0,
    }
    print(f"[efe] {MODELO} · in={uso['input']} out={uso['output']} "
          f"cache_write={uso['cache_write']} cache_read={uso['cache_read']} "
          f"busqueda={'sí' if con_busqueda else 'no'}", flush=True)
    return json.loads(texto), uso
