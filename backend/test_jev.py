"""Tests del adaptador de Jev — sin red y sin clave de API.

    python3 -m backend.test_jev

Lo que se verifica es la frontera del módulo: que sin credenciales se pueda
correr pero NO decidir (simulado con confianza 0), que una respuesta de la API
que se sale del contrato se rechace en vez de colarse, y que los errores
transitorios se distingan de los definitivos.
"""
import json
import os
import sys
import tempfile

fallos = 0

from backend.analisis import jev


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
        print(f"  FALLA  {nombre}" + (f" — {detalle}" if detalle else ""))
    else:
        print(f"  ok     {nombre}")


print("\n== preguntas bien formadas ==")
try:
    jev.eleccion("x", {"a": "sola"})
    check("elección de una sola opción se rechaza", False)
except ValueError:
    check("elección de una sola opción se rechaza", True)

try:
    jev.puntaje("x", [f"n{i}" for i in range(11)])
    check("rúbrica de 11 niveles se rechaza", False)
except ValueError:
    check("rúbrica de 11 niveles se rechaza", True)

check("sino sin criterios es válido", jev.sino("¿llueve?")["type"] == "noul")
check("la elección viaja con sus criterios",
      jev.eleccion("x", {"a": "1", "b": "2"})["criteria"] == {"a": "1", "b": "2"})

print("\n== sin clave: corre pero no decide ==")
os.environ.pop("TYPESAFE_API_KEY", None)
os.environ.pop("SAD_JEV_GUION", None)
check("disponible() es False sin clave", jev.disponible() is False)

preguntas = {
    "tipo": jev.eleccion("¿de qué trata?", {"dt": "cambio de entrenador",
                                            "sancion": "castigo",
                                            "ninguno": "ninguno de los dos"}),
    "urgente": jev.sino("¿es de hoy?"),
    "gravedad": jev.puntaje("¿qué tan grave?", ["nada", "poco", "mucho"]),
}
r1 = jev.preguntar("El club anunció la salida del entrenador.", preguntas)
r2 = jev.preguntar("El club anunció la salida del entrenador.", preguntas)

check("el simulado responde todas las preguntas", set(r1) == set(preguntas))
check("el simulado es determinista",
      [x.valor for x in r1.values()] == [x.valor for x in r2.values()])
check("toda respuesta simulada se marca", all(x.simulado for x in r1.values()))
check("toda respuesta simulada tiene confianza 0",
      all(x.confianza == 0.0 for x in r1.values()))
check("un simulado NUNCA es fiable", not any(x.fiable() for x in r1.values()))
check("un simulado tampoco entra en la zona media",
      not any(x.dudosa() for x in r1.values()))
check("la elección simulada sale de los criterios",
      r1["tipo"].valor in preguntas["tipo"]["criteria"])
otro = jev.preguntar("otra cosa completamente distinta", preguntas)
check("cada estado tiene su propia huella",
      [x.valor for x in otro.values()] != [x.valor for x in r1.values()])

print("\n== guion: probar una lógica concreta ==")
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
    json.dump({"tipo": {"valor": "dt", "confianza": 0.97, "comoReal": True}}, fh)
    ruta = fh.name
os.environ["SAD_JEV_GUION"] = ruta
rg = jev.preguntar("cualquier cosa", preguntas)
check("el guion fija la respuesta", rg["tipo"].valor == "dt")
check("el guion puede pasar por real", rg["tipo"].fiable())
check("lo que el guion no fija sigue simulado", rg["urgente"].simulado)
os.environ.pop("SAD_JEV_GUION", None)
os.unlink(ruta)

print("\n== normalización de la respuesta real ==")
crudo = {"model": "jev-1.13.0",
         "answers": {"tipo": {"type": "choice", "choice": "dt", "confidence": 0.93,
                              "probabilities": {"dt": 0.93, "sancion": 0.05, "ninguno": 0.02}},
                     "urgente": {"type": "noul", "noul": 0.98},
                     "gravedad": {"type": "score", "score": 1.4, "confidence": 0.6}},
         "usage": {"input_tokens": 392, "output_tokens": 65}}
n = jev._normalizar(crudo, preguntas)
check("la elección conserva su valor", n["tipo"].valor == "dt")
check("la elección conserva su distribución", n["tipo"].probabilidades["dt"] == 0.93)
check("una elección con 0.93 es fiable", n["tipo"].fiable())
check("noul deriva confianza de la probabilidad",
      abs(n["urgente"].confianza - 0.96) < 1e-9)
check("un score de confianza media es dudoso, no fiable",
      n["gravedad"].dudosa() and not n["gravedad"].fiable())
check("nada de lo real se marca simulado", not any(x.simulado for x in n.values()))

# Un noul en 0.5 es duda máxima, no un "sí" flojo.
n2 = jev._normalizar({"answers": {"urgente": {"type": "noul", "noul": 0.5}}},
                     {"urgente": preguntas["urgente"]})
check("noul 0.5 da confianza 0", n2["urgente"].confianza == 0.0)

print("\n== la respuesta que no cumple el contrato se rechaza ==")
for nombre, cuerpo in [
    ("falta una pregunta", {"answers": {"urgente": {"type": "noul", "noul": 1.0}}}),
    ("responde otro tipo", {"answers": {"tipo": {"type": "noul", "noul": 1.0}}}),
    ("elige fuera de los criterios",
     {"answers": {"tipo": {"type": "choice", "choice": "inventada", "confidence": 1.0}}}),
]:
    try:
        jev._normalizar(cuerpo, {"tipo": preguntas["tipo"]})
        check(nombre, False, "pasó sin error")
    except jev.JevError:
        check(nombre, True)

print("\n== el recibo y el sello de versión ==")
check("el lote sigue siendo un dict de respuestas", n["tipo"].valor == "dt" and len(n) == 3)
check("el lote sella qué modelo respondió", n.modelo == "jev-1.13.0")
check("cada respuesta lleva su modelo", n["tipo"].modelo == "jev-1.13.0")
check("el lote trae los tokens de entrada", n.tokens_entrada == 392)
check("y su costo", abs(n.costo - jev.costo(392)) < 1e-12)
check("el simulado se sella como simulado", r1.modelo == "simulado")

print("\n== probabilidad y confianza no son lo mismo ==")
n3 = jev._normalizar({"answers": {"urgente": {"type": "noul", "noul": 0.72}}},
                     {"urgente": preguntas["urgente"]})
check("un noul de 0.72 es un sí utilizable", n3["urgente"].probabilidad() == 0.72)
# 0.72 → confianza |0.72-0.5|*2 = 0.44: ni fiable ni zona media. Medir una
# probabilidad con el umbral de la confianza es no decidir nunca.
check("...pero su confianza (0.44) no llega ni a la zona media",
      not n3["urgente"].dudosa() and not n3["urgente"].fiable())
check("la confianza del noul se deriva de su distancia a 0.5",
      abs(n3["urgente"].confianza - 0.44) < 1e-9)
try:
    n3["urgente"] = n["tipo"]
    n["tipo"].probabilidad()
    check("probabilidad() sobre una elección se rechaza", False)
except ValueError:
    check("probabilidad() sobre una elección se rechaza", True)

print("\n== el estado que no cabe se corta antes de salir ==")
try:
    jev.preguntar("x" * (jev.TOPE_ESTADO_CARACTERES + 1), preguntas)
    check("un estado gigante se rechaza", False, "pasó sin error")
except ValueError as exc:
    check("un estado gigante se rechaza", "repartilo" in str(exc))

print("\n== una clave mal pegada no es una clave mala ==")
for cruda, limpia in (('"ts-abc"', "ts-abc"), ("'ts-abc'", "ts-abc"), ("Bearer ts-abc", "ts-abc"),
                      ("  ts-abc  ", "ts-abc"), ('"Bearer ts-abc"', "ts-abc")):
    os.environ["TYPESAFE_API_KEY"] = cruda
    check(f"{cruda!r} → {limpia!r}", jev._clave() == limpia and jev.disponible(), jev._clave())
os.environ["TYPESAFE_API_KEY"] = '""'
check("solo comillas es no tener clave", not jev.disponible())
os.environ.pop("TYPESAFE_API_KEY", None)

print("\n== costo ==")
check("la salida no se cobra y la entrada es calderilla",
      abs(jev.costo(392) - 392 / 1_000_000 * 0.042) < 1e-12)
check("un millón de tokens cuesta 4,2 centavos", abs(jev.costo(1_000_000) - 0.042) < 1e-12)

print(f"\n{'TODO OK' if not fallos else str(fallos) + ' FALLAS'}")
sys.exit(1 if fallos else 0)
