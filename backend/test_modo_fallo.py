"""Tests del modo de fallo del veredicto (Jev) — sin red y sin clave.

    python3 -m backend.test_modo_fallo

La frontera: solo se etiquetan lados con fallo o parcial Y con prosa; sin
clave no sale ninguna etiqueta; la taxonomía es cerrada y tiene salida; el
«pide mover un número» se decide por probabilidad con zona gris; y el
agrupado del dossier cuenta sin puntuar.
"""
import json
import os
import sys
import tempfile

fallos = 0
os.environ.pop("TYPESAFE_API_KEY", None)
os.environ.pop("SAD_JEV_GUION", None)

from backend.analisis import modo_fallo as mf  # noqa: E402


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
        print(f"  FALLA  {nombre}" + (f" — {detalle}" if detalle else ""))
    else:
        print(f"  ok     {nombre}")


NOMBRES = {"a": "Alianza Lima", "b": "Sporting Cristal"}
POR_LADO = {
    "a": {"veredicto": "acierto", "queP": "ganó como se dijo", "leccion": "", "skill": ""},
    "b": {"veredicto": "fallo", "queP": "expulsión al 30' y penal en el descuento",
          "leccion": "el índice de echada tiene que subir dos puntos cuando el rival juega con diez",
          "skill": "teorema-del-echado", "reglaTocada": "escala de P(echada)"},
}

print("\n== qué se pregunta ==")
preg = mf.preguntas_de(POR_LADO, NOMBRES)
check("un acierto no se etiqueta", "modo_a" not in preg and "mueve_a" not in preg)
check("un fallo con prosa se etiqueta (modo + mueve)", {"modo_b", "mueve_b"} <= set(preg))
check("la taxonomía tiene salida «no lo dice»", "no_lo_dice" in preg["modo_b"]["criteria"])
check("las opciones son exactamente la taxonomía", set(preg["modo_b"]["criteria"]) == set(mf.MODOS))
sin_prosa = {"b": {"veredicto": "fallo", "queP": "", "leccion": ""}}
check("un fallo sin prosa no se pregunta", mf.preguntas_de(sin_prosa, NOMBRES) == {})
parcial = {"b": {**POR_LADO["b"], "veredicto": "parcial", "leccion": ""}}
p2 = mf.preguntas_de(parcial, NOMBRES)
check("un parcial con queP pero sin lección pregunta el modo y no el «mueve»",
      "modo_b" in p2 and "mueve_b" not in p2)
estado = mf._estado(POR_LADO, NOMBRES)
check("la prosa va en el estado y no en las instrucciones",
      POR_LADO["b"]["leccion"] in json.dumps(estado, ensure_ascii=False)
      and all(POR_LADO["b"]["leccion"] not in q["instructions"] for q in preg.values()))

print("\n== sin clave: nada se etiqueta ==")
ev = mf.evaluar(POR_LADO, NOMBRES)
check("se evaluó y se marcó simulado", ev["simulado"] is True and ev["preguntas"] == 2)
check("el lado con fallo queda sin modo y sin decisión sobre mover",
      ev["lados"]["b"]["modo"] is None and ev["lados"]["b"]["proponeMoverNumero"] is None, ev["lados"])
check("el lado con acierto no aparece", "a" not in ev["lados"])
check("la taxonomía viaja para que la pantalla no la adivine", ev["taxonomia"] == list(mf.MODOS))

print("\n== con guion: la etiqueta y la zona gris del «mueve» ==")
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
    json.dump({"modo_b": {"valor": "tde", "confianza": 0.9, "comoReal": True},
               "mueve_b": {"valor": 0.92, "comoReal": True}}, fh)
    ruta = fh.name
os.environ["SAD_JEV_GUION"] = ruta
ev = mf.evaluar(POR_LADO, NOMBRES)
check("con confianza el modo se etiqueta", ev["lados"]["b"]["modo"] == "tde", ev["lados"])
check("p=0.92 → pide mover un número", ev["lados"]["b"]["proponeMoverNumero"] is True)
check("el modelo sellado es el del guion", ev["modelo"] == "guion" and ev["simulado"] is False)
for p, esperado in ((0.5, None), (0.2, False), (0.7, True)):
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump({"modo_b": {"valor": "tde", "confianza": 0.9, "comoReal": True},
                   "mueve_b": {"valor": p, "comoReal": True}}, fh)
    check(f"p={p} → proponeMoverNumero={esperado}",
          mf.evaluar(POR_LADO, NOMBRES)["lados"]["b"]["proponeMoverNumero"] is esperado)
with open(ruta, "w", encoding="utf-8") as fh:
    json.dump({"modo_b": {"valor": "imprevisto", "confianza": 0.4, "comoReal": True}}, fh)
ev = mf.evaluar(POR_LADO, NOMBRES)
check("un modo con confianza baja se deja en None (no se adivina)",
      ev["lados"]["b"]["modo"] is None and ev["lados"]["b"]["modoConfianza"] == 0.4)
os.environ.pop("SAD_JEV_GUION", None)
os.unlink(ruta)

print("\n== el agrupado del dossier cuenta, no puntúa ==")
from backend.analisis.lecciones import _por_modo_fallo  # noqa: E402
items = [
    {"veredicto": "fallo", "modoFallo": "tde", "proponeMoverNumero": True, "puedeMoverNumeros": False, "clave": "1:b"},
    {"veredicto": "fallo", "modoFallo": "tde", "proponeMoverNumero": False, "puedeMoverNumeros": True, "clave": "2:b"},
    {"veredicto": "parcial", "modoFallo": None, "proponeMoverNumero": None, "puedeMoverNumeros": True, "clave": "3:a"},
    {"veredicto": "acierto", "modoFallo": None, "proponeMoverNumero": True, "puedeMoverNumeros": True, "clave": "4:a"},
]
g = _por_modo_fallo(items)
check("cuenta fallos y parciales, no aciertos", g["fallos"] == 3)
check("agrupa por modo y cuenta los sin etiqueta", g["porModo"] == {"tde": 2} and g["sinEtiqueta"] == 1, g)
check("la alarma: piden mover un número sin poder sostenerlo",
      g["pidenMoverNumero"] == 2 and g["pidenMoverSinPoder"] == ["1:b"], g)
check("y lo dice: agrupan, no puntúan", "no puntúan" in g["nota"])

print(f"\n{'TODO OK' if not fallos else str(fallos) + ' FALLAS'}")
sys.exit(1 if fallos else 0)
