"""Jev (TypeSafe AI, System One) — capa de decisiones rápidas del backend.

Qué es y qué NO es
------------------
Jev no genera texto: recibe un estado no estructurado y devuelve VALORES
TIPADOS definidos de antemano (elección de una lista, puntaje sobre una
rúbrica ordenada, sí/no probabilístico) con su probabilidad y su confianza.
https://docs.typesafe.ai/ · POST https://api.typesafe.ai/v1/systemone

Está calibrado contra modelos de frontera, NO contra resultados deportivos:
por eso aquí es un CLASIFICADOR DE TEXTO y nunca un pronosticador. No toca
la matemática del motor (K, niveles, Poisson, burbuja, gap §5) ni nada que
salga de la base: lo que está en nuestra base se calcula, no se le pregunta
a un modelo.

Las tres reglas que impone el modelo (limitaciones declaradas de jev-1.13,
docs.typesafe.ai/model-jaggedness/jev-1.13) y que este módulo hace cumplir:

1. Nada de números ni de fechas. Cuenta mal y lee las fechas como texto, no
   como cantidades ordenadas. Comparar fechas, sumar minutos o medir edades
   es trabajo de código.
2. El estado es HOSTIL. El modelo no trata el contenido como potencialmente
   adversarial: un texto de prensa puede llevar instrucciones dentro. Por eso
   el texto de fuera viaja SIEMPRE en `estado` y JAMÁS en `instrucciones` ni
   en los criterios, y la salida es un enum de una lista que escribimos
   nosotros: lo peor que puede hacer un texto envenenado es elegir mal dentro
   de esa lista.
3. Una pregunta, un salto. Sin dobles negaciones ni encadenar razonamientos.

Sin clave (TYPESAFE_API_KEY) el cliente NO se cae: responde en modo SIMULADO,
determinista por el estado, y marca cada respuesta con `simulado=True` y
`confianza=0.0`. Es a propósito: sin credenciales el sistema puede CORRER pero
no puede DECIDIR —una confianza 0 no pasa ningún umbral—, así que un simulado
nunca se cuela como juicio en un parte. Para probar una lógica concreta se le
pone un guion: SAD_JEV_GUION=/ruta/respuestas.json.

Uso:
    from backend.analisis import jev
    r = jev.preguntar(texto_de_prensa, {
        "tipo": jev.eleccion("¿De qué trata la noticia?", {
            "cambio_dt": "Anuncia la llegada o la salida de un entrenador.",
            "sancion": "Anuncia un castigo deportivo o administrativo.",
            "ninguno": "No trata ninguno de los casos anteriores.",
        }),
    })
    if r["tipo"].fiable():       # confianza >= UMBRAL_ALTO
        ...
"""
import hashlib
import json
import os
import time
from dataclasses import dataclass, field

ENDPOINT = os.environ.get("SAD_JEV_ENDPOINT", "https://api.typesafe.ai/v1/systemone")
MODELO = os.environ.get("SAD_JEV_MODELO", "jev-latest")
TIMEOUT = float(os.environ.get("SAD_JEV_TIMEOUT", "10"))
REINTENTOS = int(os.environ.get("SAD_JEV_REINTENTOS", "2"))

# Los umbrales que recomienda la documentación (docs.typesafe.ai/confidence),
# con la lectura de este proyecto: actuar solo con confianza alta, y "actuar"
# aquí no es nunca mover un número —es levantar una alerta de tipo dato—.
# OJO: son el DEFECTO, no la política. El cookbook de guardrails usa la
# PROBABILIDAD del noul (actuar ≥ 0.70, revisar ≥ 0.35) y el de emparejamiento
# de entidades no usa umbral ninguno: redondea el score a su nivel. Cada uso
# elige el suyo y lo justifica; un 0.9 global aplicado a un noul equivale a
# exigir p ≥ 0.95, que en la práctica es no decidir nunca.
UMBRAL_ALTO = float(os.environ.get("SAD_JEV_UMBRAL", "0.9"))
UMBRAL_MEDIO = 0.5

# Límites del servicio (docs.typesafe.ai/models): 64k tokens por petición, de
# los que 32k son para el estado más la pregunta más larga; 1200 peticiones por
# minuto y 250k tokens/s, "ajustados dinámicamente". Como el estado se mide en
# tokens y aquí solo tenemos caracteres, el tope va con margen: ~4 caracteres
# por token. Pasarse no es un error del servicio que se descubre en producción:
# se corta antes y el llamador reparte el trabajo.
TOPE_ESTADO_CARACTERES = int(os.environ.get("SAD_JEV_TOPE_ESTADO", "100000"))

# $0.042 por millón de tokens de entrada; la salida es gratis. Solo para el
# log de costo por corrida, igual que en backend/analisis/cliente.py.
PRECIO_ENTRADA = 0.042


class Lote(dict):
    """Las respuestas de UNA petición, con el recibo pegado.

    Sigue siendo un dict {clave: Respuesta} para quien solo quiera leer, y
    además trae qué modelo respondió y cuántos tokens de entrada costó. El
    recibo importa porque el alias `jev-latest` se mueve solo: un cambio de
    versión puede correr un umbral, y sin el sello no hay forma de saber que
    la respuesta guardada la dio otro modelo.
    """
    modelo: str = ""
    tokens_entrada: int = 0

    @property
    def costo(self) -> float:
        return costo(self.tokens_entrada)


class JevError(RuntimeError):
    """Falla de la API que el llamador tiene que poder distinguir de un 'no sé'."""


@dataclass
class Respuesta:
    """Una respuesta tipada. `valor` es str (choice), float (score/noul).

    `modelo` es la versión EXACTA que respondió (jev-1.13.0), no el alias. Va
    en cada respuesta porque Jev NO es determinista: el propio cookbook de
    self-consistency corre la misma rúbrica 15 veces sobre el mismo texto y la
    etiqueta se mueve en los casos de borde. Una salida así no se puede
    RECALCULAR al leer, como hace el resto del proyecto con lo derivado: hay
    que guardarla sellada con su modelo y tratarla como dato capturado.
    """
    tipo: str
    valor: object
    confianza: float
    probabilidades: dict = field(default_factory=dict)
    simulado: bool = False
    modelo: str = ""

    def fiable(self, umbral: float = UMBRAL_ALTO) -> bool:
        """Confianza suficiente para actuar sin que lo mire una persona."""
        return (not self.simulado) and self.confianza >= umbral

    def probabilidad(self) -> float:
        """Solo noul: probabilidad de que la afirmación sea VERDADERA.

        No es lo mismo que la confianza, y confundirlas es el error fácil: el
        cookbook de guardrails actúa sobre esta probabilidad (≥ 0.70 actuar,
        ≥ 0.35 revisar), mientras que `fiable()` mira cuán concentrada está la
        distribución. Un noul en 0.72 es un "sí" accionable para ese cookbook
        y a la vez una confianza de 0.44 —por debajo incluso de la zona
        media—: son dos preguntas distintas, y medir una con el umbral de la
        otra es no decidir nunca.
        """
        if self.tipo != "noul":
            raise ValueError(f"probabilidad() es de noul, no de {self.tipo}")
        return float(self.valor)

    def dudosa(self) -> bool:
        """Zona media: se puede mostrar, no se puede dar por cierto."""
        return (not self.simulado) and UMBRAL_MEDIO <= self.confianza < UMBRAL_ALTO


# ---------------------------------------------------------------- preguntas

def eleccion(instrucciones: str, criterios: dict) -> dict:
    """Choice: elige UNA opción de las que escribimos nosotros (máx. 255)."""
    if len(criterios) < 2:
        raise ValueError("una elección necesita al menos dos opciones")
    if len(criterios) > 255:
        raise ValueError("Jev admite hasta 255 opciones en una elección")
    return {"type": "choice", "instructions": instrucciones, "criteria": dict(criterios)}


def puntaje(instrucciones: str, niveles: list) -> dict:
    """Score: posición en una rúbrica ORDENADA (2 a 10 niveles)."""
    if not 2 <= len(niveles) <= 10:
        raise ValueError("una rúbrica de Jev tiene entre 2 y 10 niveles")
    return {"type": "score", "instructions": instrucciones, "criteria": list(niveles)}


def sino(instrucciones: str, criterios: dict | None = None) -> dict:
    """Noul: probabilidad de que una afirmación sea verdadera (0 a 1)."""
    p = {"type": "noul", "instructions": instrucciones}
    if criterios:
        p["criteria"] = dict(criterios)
    return p


# ------------------------------------------------------------------ cliente

def _clave() -> str:
    """La clave tal como hay que mandarla. Una variable pegada con comillas o
    con `Bearer ` delante —el error de copia más común en un panel— da un 401
    idéntico al de una clave mala; se limpia acá para que un 401 signifique
    de verdad «clave inválida» y no «clave mal pegada»."""
    k = os.environ.get("TYPESAFE_API_KEY", "").strip().strip('"').strip("'").strip()
    if k.lower().startswith("bearer "):
        k = k[7:].strip()
    return k


def disponible() -> bool:
    return bool(_clave())


def _confianza_noul(p: float) -> float:
    """Noul devuelve probabilidad, no confianza: 0.5 es duda máxima."""
    return abs(float(p) - 0.5) * 2


def _normalizar(bruto: dict, preguntas: dict) -> Lote:
    salida = Lote()
    salida.modelo = str(bruto.get("model") or "")
    salida.tokens_entrada = int((bruto.get("usage") or {}).get("input_tokens") or 0)
    for clave, pregunta in preguntas.items():
        dato = (bruto.get("answers") or {}).get(clave)
        if not isinstance(dato, dict):
            raise JevError(f"la respuesta no trae la pregunta '{clave}'")
        tipo = dato.get("type") or pregunta["type"]
        if tipo != pregunta["type"]:
            raise JevError(f"'{clave}': se preguntó {pregunta['type']} y respondió {tipo}")
        if tipo == "noul":
            valor = float(dato.get("noul", 0.5))
            confianza = _confianza_noul(valor)
        elif tipo == "choice":
            valor = dato.get("choice")
            if valor not in pregunta["criteria"]:
                raise JevError(f"'{clave}': eligió '{valor}', que no está en los criterios")
            confianza = float(dato.get("confidence", 0.0))
        else:
            valor = float(dato.get("score", 0.0))
            confianza = float(dato.get("confidence", 0.0))
        salida[clave] = Respuesta(tipo=tipo, valor=valor, confianza=confianza,
                                  probabilidades=dato.get("probabilities") or {},
                                  modelo=salida.modelo)
    return salida


def _guion(estado, preguntas: dict) -> dict | None:
    """Respuestas fijas para probar una lógica concreta (SAD_JEV_GUION)."""
    ruta = os.environ.get("SAD_JEV_GUION", "").strip()
    if not ruta or not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def _simular(estado, preguntas: dict) -> Lote:
    """Determinista por el estado: la misma entrada da la misma salida.

    Confianza 0 y simulado=True SIEMPRE: sin clave se puede recorrer el
    código, no fabricar un juicio.
    """
    guion = _guion(estado, preguntas)
    semilla = hashlib.sha256(json.dumps(estado, sort_keys=True, ensure_ascii=False,
                                        default=str).encode("utf-8")).hexdigest()
    salida = Lote()
    salida.modelo = "simulado"
    for i, (clave, pregunta) in enumerate(sorted(preguntas.items())):
        if guion and clave in guion:
            fijo = guion[clave]
            salida[clave] = Respuesta(tipo=pregunta["type"], valor=fijo.get("valor"),
                                      confianza=float(fijo.get("confianza", 0.0)),
                                      probabilidades=fijo.get("probabilidades") or {},
                                      simulado=not bool(fijo.get("comoReal")),
                                      modelo="guion")
            continue
        n = int(semilla[i * 4:i * 4 + 4] or "0", 16)
        if pregunta["type"] == "choice":
            opciones = list(pregunta["criteria"])
            valor = opciones[n % len(opciones)]
        elif pregunta["type"] == "score":
            valor = float(n % len(pregunta["criteria"]))
        else:
            valor = round((n % 1000) / 1000, 3)
        salida[clave] = Respuesta(tipo=pregunta["type"], valor=valor,
                                  confianza=0.0, simulado=True, modelo="simulado")
    # un guion que pasa por real convierte el lote en «guion»: quien lo lea
    # sabe que esas respuestas cuentan, y de dónde salieron
    if any(not r.simulado for r in salida.values()):
        salida.modelo = "guion"
    return salida


def preguntar(estado, preguntas: dict, modelo: str = "") -> Lote:
    """Una llamada, todas las preguntas: cada una ve el MISMO estado.

    `estado` es texto/dict/lista sin estructurar (lo de fuera). `preguntas`
    es el mapa que arman eleccion()/puntaje()/sino(). Devuelve {clave:
    Respuesta}. Sin clave de API, modo simulado (confianza 0).
    """
    if not preguntas:
        raise ValueError("no hay nada que preguntar")
    medida = len(estado if isinstance(estado, str)
                 else json.dumps(estado, ensure_ascii=False, default=str))
    if medida > TOPE_ESTADO_CARACTERES:
        raise ValueError(
            f"el estado mide {medida} caracteres y el tope es {TOPE_ESTADO_CARACTERES}: "
            "repartilo en varias peticiones (el servicio corta en 32k tokens)")
    if not disponible():
        return _simular(estado, preguntas)

    import httpx  # import tardío: el resto del backend no lo necesita

    cuerpo = {"state": estado, "model": modelo or MODELO, "questions": preguntas}
    cabeceras = {"Authorization": f"Bearer {_clave()}",
                 "Content-Type": "application/json"}
    espera = 1.0
    ultimo = ""
    for intento in range(REINTENTOS + 1):
        try:
            r = httpx.post(ENDPOINT, json=cuerpo, headers=cabeceras, timeout=TIMEOUT)
        except Exception as exc:  # red caída: no es motivo para tumbar un parte
            ultimo = f"sin red: {exc}"
        else:
            if r.status_code == 200:
                return _normalizar(r.json(), preguntas)
            # 429 y 529 son transitorios (backoff exponencial); 401 y 422 no.
            if r.status_code not in (429, 529):
                raise JevError(f"Jev respondió {r.status_code}: {r.text[:200]}")
            ultimo = f"{r.status_code} transitorio"
        if intento < REINTENTOS:
            time.sleep(espera)
            espera *= 2
    raise JevError(f"Jev no respondió tras {REINTENTOS + 1} intentos ({ultimo})")


def costo(tokens_entrada: int) -> float:
    """Dólares de una corrida. La salida de Jev no se cobra."""
    return tokens_entrada / 1_000_000 * PRECIO_ENTRADA


def ping() -> dict:
    """¿La clave sirve? UNA llamada mínima: un noul sobre una frase fija.

    Devuelve qué modelo respondió, cuánto tardó y cuántos tokens costó (unos
    cientos: milésimas de centavo). Sin clave no sale a la red y lo dice.
    Nunca lanza: un fallo se declara en `error`, que es justamente lo que
    quien pregunta quiere ver (401 = clave mala, 429 = límite, sin red…).
    """
    import time as _t
    if not disponible():
        return {"disponible": False, "ok": False, "modelo": None, "ms": 0, "tokensEntrada": 0,
                "error": "TYPESAFE_API_KEY no está puesta: Jev corre simulado y no decide"}
    t0 = _t.monotonic()
    try:
        lote = preguntar("El partido terminó 2-1 y el equipo local ganó.",
                         {"gano_local": sino("¿El texto dice que el equipo local ganó?")})
    except (JevError, ValueError) as exc:
        return {"disponible": True, "ok": False, "modelo": None,
                "ms": int((_t.monotonic() - t0) * 1000), "tokensEntrada": 0, "error": str(exc)}
    r = lote["gano_local"]
    return {"disponible": True, "ok": r.probabilidad() >= 0.7, "modelo": lote.modelo,
            "ms": int((_t.monotonic() - t0) * 1000), "tokensEntrada": lote.tokens_entrada,
            "respuesta": {"probabilidad": round(r.probabilidad(), 3), "esperado": "≥ 0.7"},
            "error": None if r.probabilidad() >= 0.7 else
                     "respondió, pero a una pregunta trivial contestó que no: mirá el modelo"}
