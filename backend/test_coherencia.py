"""Tests del guardrail de coherencia del parte (Jev) — sin red y sin clave.

    python3 -m backend.test_coherencia

Lo que se verifica es la frontera: que Jev solo etiquete PROSA y el código
compare con el número; que sin clave no haya hallazgo posible (simulado =
confianza 0); que un hallazgo salga solo con confianza suficiente y solo
cuando etiqueta y número se contradicen de verdad; y que en modo sombra nada
llegue a la tira de alertas.
"""
import json
import os
import sys
import tempfile

fallos = 0

os.environ.pop("TYPESAFE_API_KEY", None)
os.environ.pop("SAD_JEV_GUION", None)
os.environ["SAD_JEV_COHERENCIA"] = "sombra"

from backend.analisis import coherencia, jev  # noqa: E402


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
        print(f"  FALLA  {nombre}" + (f" — {detalle}" if detalle else ""))
    else:
        print(f"  ok     {nombre}")


NOMBRES = {"a": "Alianza Lima", "b": "Sporting Cristal"}


def bloque(score, maximo, nota, declarado=True, excluido=False):
    return {"score": score, "max": maximo, "nota": nota, "declarado": declarado, "excluido": excluido}


PARTE = {
    "equipos": {
        "a": {"bloques": {"A": bloque(4, 4, "El DT lleva tres temporadas, respaldado por la dirigencia; ciclo consolidado."),
                          "B": bloque(1, 6, "Perdió a seis titulares en el mercado y el reemplazo no llegó."),
                          "C": bloque(2, 4, ""),  # sin nota: no se pregunta
                          "D": bloque(3, 4, "Idea clara y sostenida.", declarado=False),  # sin declarar: no se pregunta
                          "E": bloque(2, 3, "Rachas irregulares.", excluido=True)},  # excluido: no se pregunta
              "perfil": {"sistema": "4-2-3-1"}, "factorX": []},
        "b": {"bloques": {"A": bloque(1, 4, "Tercer entrenador del año, asumió hace nueve días con el plantel en contra.")},
              "perfil": {}, "factorX": [{"nombre": "Yotún", "contexto": "vuelve tras lesión"}]},
    },
    "lecturaSad": {"moduloOperativo": "…", "unXDos": {"texto": "Todo inclina al local: forma, plantel y localía."},
                   "reventon": "Alianza lleva racha larga y el rival es de zona: riesgo alto. Cristal sin base."},
    "matchup": {"favorece": "a", "razon": "Alianza domina los duelos por fuera y Cristal no tiene laterales."},
    "pronostico": {"probabilidades": {"local": 55, "empate": 25, "visita": 20}, "motor": "", "matriz": "", "mercado": "", "marcador": ""},
}
REVENTON = {"a": {"riesgo": {"nivel": "alto", "puntos": 5}}, "b": {"riesgo": {"nivel": "sin base", "puntos": 0}}}

print("\n== qué se pregunta y qué no ==")
preg, comp = coherencia.preguntas_de(PARTE, NOMBRES, REVENTON)
check("se pregunta por las notas declaradas y no excluidas (A y B del local, A de la visita)",
      {"nota_a_A", "nota_a_B", "nota_b_A"} <= set(preg))
check("un bloque sin nota no se pregunta", "nota_a_C" not in preg)
check("un bloque sin declarar no se pregunta", "nota_a_D" not in preg)
check("un bloque excluido no se pregunta", "nota_a_E" not in preg)
check("el 1X2 se pregunta porque el reparto se inclina (55 vs 25)", "unXDos" in preg)
check("el matchup se pregunta porque hay lado y razón", "matchup" in preg)
check("el reventón se pregunta solo del lado con número (b es «sin base»)",
      "reventon_a" in preg and "reventon_b" not in preg)
check("la comparación guarda el tercio del sub-score (A=4/4 → alto, B=1/6 → bajo)",
      comp["nota_a_A"]["tercio"] == 2 and comp["nota_a_B"]["tercio"] == 0)
check("las preguntas son solo puntaje o elección (nada de noul: se compara con confianza)",
      all(q["type"] in ("score", "choice") for q in preg.values()))

print("\n== el texto de Cowork va en el estado, nunca en las instrucciones ==")
estado = coherencia._estado(PARTE, NOMBRES)
prosa = PARTE["equipos"]["a"]["bloques"]["B"]["nota"]
check("la nota está en el estado", prosa in json.dumps(estado, ensure_ascii=False))
check("ninguna instrucción contiene prosa del parte",
      all(prosa not in q["instructions"] for q in preg.values()))
# (la palabra «plantel» sí puede aparecer dentro de la prosa: lo que no debe
# haber es la LISTA de jugadores ni los sub-scores como claves)
check("el estado no lleva la lista del plantel ni los números de los bloques",
      all("plantel" not in e and "bloques" not in e for e in estado["equipos"].values())
      and '"score"' not in json.dumps(estado))

print("\n== el 1X2 parejo no se compara ==")
parejo = {**PARTE, "pronostico": {**PARTE["pronostico"], "probabilidades": {"local": 36, "empate": 32, "visita": 32}}}
preg2, _ = coherencia.preguntas_de(parejo, NOMBRES, None)
check("con 36/32/32 no hay pregunta del 1X2", "unXDos" not in preg2)

print("\n== sin clave: corre y no decide ==")
ev = coherencia.evaluar(PARTE, NOMBRES, REVENTON)
check("se evaluó en modo sombra", ev["modo"] == "sombra")
check("se marca simulado", ev["simulado"] is True)
check("se contaron las preguntas", ev["preguntas"] == len(preg))
check("no hay hallazgos posibles sin confianza", ev["hallazgos"] == [])
check("todas quedan como sin confianza, marcadas simuladas",
      len(ev["sinConfianza"]) == len(preg) and all(x["simulado"] for x in ev["sinConfianza"]))
check("el modelo sellado dice simulado", ev["modelo"] == "simulado")
check("y el sello dice por dónde pasó: simulado, no oficial", ev["via"] == "simulado" and ev["oficial"] is False)
check("en sombra no va nada a la tira", coherencia.alertas_de(ev) == [])

print("\n== con guion: la comparación la hace el código ==")
guion = {
    # A del local: nota «consolidado» → nivel 2, score 4/4 → tercio 2: concuerda
    "nota_a_A": {"valor": 2.0, "confianza": 0.95, "comoReal": True},
    # B del local: nota «perdió seis titulares» → nivel 0, score 1/6 → tercio 0: concuerda
    "nota_a_B": {"valor": 0.1, "confianza": 0.9, "comoReal": True},
    # A de la visita: nota de crisis → nivel 0, pero el score dice 1/4 → tercio 0: concuerda.
    # Lo forzamos al revés para ver el hallazgo: Jev dice «bueno» (2) con 1/4 declarado
    "nota_b_A": {"valor": 2.0, "confianza": 0.92, "comoReal": True},
    # 1X2: el texto inclina a la visita, el reparto pone 55 en local → hallazgo
    "unXDos": {"valor": "visita", "confianza": 0.88, "comoReal": True},
    # matchup: concuerda (favorece a Alianza)
    "matchup": {"valor": "Alianza Lima", "confianza": 0.9, "comoReal": True},
    # reventón: el texto dice alto, el cálculo dice alto → concuerda
    "reventon_a": {"valor": "alto", "confianza": 0.85, "comoReal": True},
}
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
    json.dump(guion, fh)
    ruta = fh.name
os.environ["SAD_JEV_GUION"] = ruta
ev = coherencia.evaluar(PARTE, NOMBRES, REVENTON)
codigos = sorted(h["codigo"] for h in ev["hallazgos"])
check("dos hallazgos: el bloque A de la visita y el 1X2", codigos == ["COHERENCIA-1X2", "COHERENCIA-BLOQUE"],
      str(codigos))
bloq = next(h for h in ev["hallazgos"] if h["codigo"] == "COHERENCIA-BLOQUE")
check("el hallazgo del bloque apunta al lado y la letra", bloq["equipo"] == "b" and "bloque A" in bloq["detalle"])
check("el hallazgo lleva la respuesta de Jev sellada", bloq["jev"]["pregunta"] == "nota_b_A" and bloq["jev"]["confianza"] == 0.92)
check("con guion el sello dice guion y el host del endpoint", ev["via"] == "guion" and "oficial" in ev)
check("lo que concuerda se lista aparte", {"nota_a_A", "nota_a_B", "matchup", "reventon_a"} <= set(ev["concuerdan"]))
check("un hallazgo es siempre tipo dato", all(h["tipo"] == "dato" for h in ev["hallazgos"]))
check("sigue sin ir a la tira en modo sombra", coherencia.alertas_de(ev) == [])

print("\n== una discrepancia de UN tercio no es hallazgo ==")
g2 = {**guion, "nota_a_A": {"valor": 1.0, "confianza": 0.95, "comoReal": True}}  # «intermedio» con 4/4
with open(ruta, "w", encoding="utf-8") as fh:
    json.dump(g2, fh)
ev2 = coherencia.evaluar(PARTE, NOMBRES, REVENTON)
check("intermedio contra tercio alto no salta (hace falta distancia 2)",
      not any(h["codigo"] == "COHERENCIA-BLOQUE" and h["equipo"] == "a" for h in ev2["hallazgos"]))

print("\n== la confianza baja no produce hallazgo aunque contradiga ==")
g3 = {**guion, "unXDos": {"valor": "visita", "confianza": 0.4, "comoReal": True}}
with open(ruta, "w", encoding="utf-8") as fh:
    json.dump(g3, fh)
ev3 = coherencia.evaluar(PARTE, NOMBRES, REVENTON)
check("el 1X2 contradictorio con confianza 0.4 queda en sinConfianza, no en hallazgos",
      not any(h["codigo"] == "COHERENCIA-1X2" for h in ev3["hallazgos"])
      and any(x["pregunta"] == "unXDos" for x in ev3["sinConfianza"]))

print("\n== «ninguno» y «no lo dice» nunca contradicen ==")
g4 = {**guion, "unXDos": {"valor": "ninguno", "confianza": 0.95, "comoReal": True},
      "reventon_a": {"valor": "no lo dice", "confianza": 0.95, "comoReal": True},
      "matchup": {"valor": "ninguno", "confianza": 0.95, "comoReal": True}}
with open(ruta, "w", encoding="utf-8") as fh:
    json.dump(g4, fh)
ev4 = coherencia.evaluar(PARTE, NOMBRES, REVENTON)
check("abstenerse no es contradecir",
      not any(h["codigo"] in ("COHERENCIA-1X2", "COHERENCIA-REVENTON", "COHERENCIA-MATCHUP") for h in ev4["hallazgos"]))

print("\n== modo alertas: los hallazgos van a la tira, sellados ==")
with open(ruta, "w", encoding="utf-8") as fh:
    json.dump(guion, fh)
ev5 = {**coherencia.evaluar(PARTE, NOMBRES, REVENTON), "modo": "alertas", "modelo": "jev-1.13.0"}
tira = coherencia.alertas_de(ev5)
check("salen las dos alertas", len(tira) == 2)
check("cada una dice que vino de Jev y con qué modelo",
      all(a["origen"] == "jev" and a["modelo"] == "jev-1.13.0" and a["evaluadoEn"] for a in tira))

print("\n== el recibo: en sombra conteos, en alertas el detalle ==")
rs = coherencia.resumen_recibo({**ev5, "modo": "sombra"})
check("en sombra el recibo trae cuántos, no cuáles", rs["hallazgos"] == 2 and "detalle" not in rs)
ra = coherencia.resumen_recibo(ev5)
check("en alertas el recibo trae el detalle", len(ra["detalle"]) == 2 and ra["detalle"][0]["codigo"].startswith("COHERENCIA-"))
check("y le dice a Cowork qué hacer (y qué no)", "Nunca cambies un número" in ra["queHacer"])
check("un recibo sin evaluación no rompe", coherencia.resumen_recibo(None)["preguntas"] == 0)

print("\n== la tira del parte no acepta estos códigos desde el depósito ==")
from backend.analisis import parte as parte_mod  # noqa: E402
check("los cuatro códigos están en la lista de capturadas",
      {"COHERENCIA-BLOQUE", "COHERENCIA-1X2", "COHERENCIA-MATCHUP", "COHERENCIA-REVENTON"} == parte_mod._ALERTAS_CAPTURADAS)
rech = []
check("una COHERENCIA-* depositada por Cowork se descarta",
      parte_mod._alerta({"codigo": "COHERENCIA-1X2", "detalle": "inyectada"}, rech, "alertas[0]") is None and not rech)

print("\n== off: no se pregunta nada ==")
coherencia.MODO = "off"
ev6 = coherencia.evaluar(PARTE, NOMBRES, REVENTON)
check("en off no hay preguntas ni hallazgos", ev6["preguntas"] == 0 and ev6["hallazgos"] == [])
coherencia.MODO = "sombra"

os.environ.pop("SAD_JEV_GUION", None)
os.unlink(ruta)
print(f"\n{'TODO OK' if not fallos else str(fallos) + ' FALLAS'}")
sys.exit(1 if fallos else 0)
