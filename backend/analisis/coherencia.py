"""Coherencia del parte de Cowork — el guardrail semántico, con Jev.

Qué hueco tapa. `parte.py` atrapa errores de TIPO y de ESTRUCTURA (un número
en `ieNivel`, una oración como nombre de DT, un sub-score fuera de rango) y los
devuelve en `rechazos`. Lo que nada atrapa hoy es la INCOHERENCIA SEMÁNTICA:
una nota que describe un cuerpo técnico recién llegado y en crisis con el
bloque A en 4 de 4; una lectura del 1X2 que inclina a la visita con el 55 %
puesto en el local; un texto de reventón que dice «riesgo alto» donde el
cálculo dice «bajo». Eso es juicio de sentido común sobre prosa: el único
trabajo del parte que no es calculable ni es análisis, y el dominio de Jev.

Cómo se reparte el trabajo (docs/JEV.md). Jev NO compara números: lee la PROSA
y devuelve una etiqueta cerrada («la nota describe un estado malo / intermedio
/ bueno»). El CÓDIGO compara esa etiqueta con el número que Cowork declaró.
Contar y comparar es la falla declarada del modelo; etiquetar texto es lo que
hace bien.

Tres reglas que este módulo hace cumplir:

1. El texto de Cowork es el ESTADO y nunca las instrucciones. Los criterios y
   las preguntas los escribimos nosotros; lo peor que puede hacer un parte
   envenenado es elegir mal dentro de nuestra lista.
2. La salida no se recalcula al leer. Jev no es determinista: dos lecturas del
   mismo parte darían hallazgos distintos. Se evalúa AL DEPOSITAR, se guarda
   sellada con el modelo que respondió (`coherencia_json`), y se rehace solo
   con el próximo depósito.
3. Un hallazgo es una alerta de tipo `dato`. No mueve un número, no cambia la
   clasificación, no pone en cuarentena. Dice «esto no cuadra, miralo».

Modos (SAD_JEV_COHERENCIA): `off` no evalúa; `sombra` evalúa y guarda pero
NO saca alertas ni le muestra el detalle a Cowork —para medir contra el
criterio humano—; `alertas` (defecto desde el 22/09) las saca en la tira, le
da el detalle a Cowork en el recibo, y el reporte del día (`parte.revisor()`,
GET /analisis/cowork/revisor) dice qué hizo Cowork con cada una. Sin clave de Jev el
adaptador responde simulado con confianza 0 y no hay hallazgo posible: el
código corre entero y decide nada, que es lo que se quiere sin credenciales.
"""
import os
from datetime import datetime, timezone

from backend.analisis import jev

# Por defecto ALERTAS (decisión del 22/09: sin apuestas de por medio, Cowork
# reacciona solo y el usuario mira el reporte del día, `revisor()`). `sombra`
# sigue disponible para medir sin que Cowork vea el detalle.
MODO = os.environ.get("SAD_JEV_COHERENCIA", "alertas").strip().lower() or "alertas"
MODOS = ("off", "sombra", "alertas")

# Primer corte, a calibrar en sombra con partes reales (docs/JEV.md, criterio
# de aceptación). Es la CONFIANZA de la distribución de un choice/score, no
# la probabilidad de un noul: acá todas las preguntas son de esos dos tipos.
UMBRAL = float(os.environ.get("SAD_JEV_COHERENCIA_UMBRAL", "0.7"))

# Lo que mide cada bloque del EFE (backend/analisis/prompts/EFE_v1_5_prompt.md).
# Va en la pregunta para que el modelo sepa QUÉ aspecto describe la nota: sin
# esto, una nota del bloque B que menciona al DT de pasada se lee como del A.
BLOQUES = {
    "A": "la estabilidad del cuerpo técnico (continuidad y respaldo del entrenador)",
    "B": "la estabilidad del plantel (bajas, llegadas, salidas, núcleo titular)",
    "C": "la coherencia de las constantes K (si las rachas del equipo son legibles y estables)",
    "D": "la coherencia táctica y de estilo (si el equipo tiene una idea reconocible y la sostiene)",
    "E": "el rendimiento en cancha (resultados y juego recientes)",
}
NIVELES_NOTA = [
    "malo o inestable: la nota describe problemas, ruptura, crisis o ausencia de lo que mide el bloque",
    "intermedio o con dudas: la nota describe una situación mixta, en transición o con reservas",
    "bueno o estable: la nota describe continuidad, solidez o normalidad en lo que mide el bloque",
]
RESULTADOS = {
    "local": "el texto inclina el pronóstico hacia la victoria del equipo local",
    "empate": "el texto inclina el pronóstico hacia el empate",
    "visita": "el texto inclina el pronóstico hacia la victoria del equipo visitante",
    "ninguno": "el texto no se pronuncia por un resultado o los deja parejos",
}
RIESGOS = {
    "alto": "el texto dice que el riesgo de que la racha se corte es alto o muy alto",
    "medio": "el texto dice que el riesgo es medio, moderado o «a vigilar»",
    "bajo": "el texto dice que el riesgo es bajo o que la racha puede seguir",
    "no lo dice": "el texto no habla del riesgo de reventón de este equipo",
}
# el reventón calculado tiene cuatro niveles; para compararlo con la prosa
# «muy alto» y «alto» son la misma dirección
_RIESGO_A_ETIQUETA = {"muy alto": "alto", "alto": "alto", "medio": "medio", "bajo": "bajo"}


def modo() -> str:
    return MODO if MODO in MODOS else "sombra"


def _tercio(score: float, maximo: float) -> int:
    """0 · 1 · 2 según el sub-score caiga en el tercio bajo, medio o alto."""
    if not maximo:
        return 1
    f = max(0.0, min(1.0, score / maximo))
    return 0 if f < 1 / 3 else (1 if f < 2 / 3 else 2)


def _estado(parte: dict, nombres: dict) -> dict:
    """Solo la PROSA del parte: sin plantel, sin números, sin timeline. El
    modelo pierde precisión con contenido irrelevante, y los números no son
    suyos —los compara el código—."""
    eq = {}
    for lado in ("a", "b"):
        e = parte.get("equipos", {}).get(lado) or {}
        eq[nombres[lado]] = {
            "notasPorBloque": {l: (e.get("bloques", {}).get(l) or {}).get("nota") or ""
                               for l in BLOQUES},
            "perfil": e.get("perfil") or {},
            "factorX": [x.get("contexto") or x.get("nombre") for x in (e.get("factorX") or [])],
        }
    ls = parte.get("lecturaSad") or {}
    return {
        "local": nombres["a"], "visitante": nombres["b"],
        "equipos": eq,
        "lecturaSad": {k: ls.get(k) for k in ("moduloOperativo", "contextoEmocional",
                                              "datoEstructural", "paradoja", "reventon")}
                      | {"unXDos": (ls.get("unXDos") or {}).get("texto") or ""},
        "matchup": {"razon": (parte.get("matchup") or {}).get("razon") or ""},
        "pronostico": {k: (parte.get("pronostico") or {}).get(k) or ""
                       for k in ("motor", "matriz", "mercado", "marcador")},
    }


def preguntas_de(parte: dict, nombres: dict, reventon: dict | None) -> tuple[dict, dict]:
    """Arma las preguntas y, aparte, con QUÉ se compara cada una (el número
    que Cowork declaró). Devuelve (preguntas, comparaciones)."""
    preguntas, comparar = {}, {}
    for lado in ("a", "b"):
        e = parte.get("equipos", {}).get(lado) or {}
        for letra, que in BLOQUES.items():
            b = e.get("bloques", {}).get(letra) or {}
            nota = (b.get("nota") or "").strip()
            if not nota or not b.get("declarado") or b.get("excluido"):
                continue
            clave = f"nota_{lado}_{letra}"
            preguntas[clave] = jev.puntaje(
                f"Leé SOLO la nota del bloque {letra} de {nombres[lado]} en "
                f"equipos.{nombres[lado]}.notasPorBloque.{letra}. El bloque mide {que}. "
                "¿Cómo describe la nota ese aspecto?", NIVELES_NOTA)
            comparar[clave] = {"tipo": "bloque", "equipo": lado, "letra": letra,
                               "score": float(b.get("score") or 0), "max": float(b.get("max") or 0),
                               "tercio": _tercio(float(b.get("score") or 0), float(b.get("max") or 0))}
    prob = (parte.get("pronostico") or {}).get("probabilidades") or {}
    texto_1x2 = ((parte.get("lecturaSad") or {}).get("unXDos") or {}).get("texto") or ""
    if texto_1x2.strip() and sum(prob.values()):
        orden = sorted(prob.items(), key=lambda kv: -kv[1])
        # solo hay algo que comparar si el reparto se inclina de verdad
        if orden[0][1] - orden[1][1] >= 10:
            preguntas["unXDos"] = jev.eleccion(
                "Leé SOLO lecturaSad.unXDos. ¿Hacia qué resultado inclina ese texto el "
                f"pronóstico del partido {nombres['a']} (local) contra {nombres['b']} (visitante)?",
                RESULTADOS)
            comparar["unXDos"] = {"tipo": "1x2", "declarado": orden[0][0], "reparto": dict(prob)}
    fav = (parte.get("matchup") or {}).get("favorece") or ""
    razon = (parte.get("matchup") or {}).get("razon") or ""
    if fav in ("a", "b") and razon.strip():
        preguntas["matchup"] = jev.eleccion(
            "Leé SOLO matchup.razon. ¿A qué equipo favorece el matchup según ese texto?",
            {nombres["a"]: f"favorece a {nombres['a']} (el local)",
             nombres["b"]: f"favorece a {nombres['b']} (el visitante)",
             "ninguno": "el texto no favorece a ninguno o los deja parejos"})
        comparar["matchup"] = {"tipo": "matchup", "declarado": nombres[fav], "lado": fav}
    texto_rev = ((parte.get("lecturaSad") or {}).get("reventon") or "").strip()
    if texto_rev and reventon:
        for lado in ("a", "b"):
            nivel = ((reventon.get(lado) or {}).get("riesgo") or {}).get("nivel")
            etiqueta = _RIESGO_A_ETIQUETA.get(nivel or "")
            if not etiqueta:
                continue  # «sin base» o error: no hay número con qué comparar
            clave = f"reventon_{lado}"
            preguntas[clave] = jev.eleccion(
                f"Leé SOLO lecturaSad.reventon. ¿Qué riesgo de reventón de la racha le "
                f"asigna ese texto a {nombres[lado]}?", RIESGOS)
            comparar[clave] = {"tipo": "reventon", "equipo": lado, "calculado": nivel, "etiqueta": etiqueta}
    return preguntas, comparar


def _hallazgo(clave: str, r: jev.Respuesta, c: dict, nombres: dict) -> dict | None:
    """Compara la etiqueta de Jev con lo declarado. None si concuerda."""
    jv = {"pregunta": clave, "valor": r.valor, "confianza": round(r.confianza, 3)}
    if c["tipo"] == "bloque":
        nivel = int(round(float(r.valor)))
        if abs(nivel - c["tercio"]) < 2:
            return None
        return {"codigo": "COHERENCIA-BLOQUE", "equipo": c["equipo"], "tipo": "dato",
                "detalle": f"la nota del bloque {c['letra']} de {nombres[c['equipo']]} describe un estado "
                           f"«{NIVELES_NOTA[nivel].split(':')[0]}» y el sub-score declarado es "
                           f"{c['score']:g} de {c['max']:g}. Uno de los dos no es lo que Cowork quiso decir",
                "jev": jv}
    if c["tipo"] == "1x2":
        if r.valor in ("ninguno", c["declarado"]):
            return None
        rep = c["reparto"]
        return {"codigo": "COHERENCIA-1X2", "equipo": "global", "tipo": "dato",
                "detalle": f"la lectura del 1X2 inclina a «{r.valor}» y el reparto declarado pone "
                           f"{rep.get(c['declarado']):g} % en «{c['declarado']}». El texto y el número "
                           "apuntan a resultados distintos",
                "jev": jv}
    if c["tipo"] == "matchup":
        if r.valor in ("ninguno", c["declarado"]):
            return None
        return {"codigo": "COHERENCIA-MATCHUP", "equipo": "global", "tipo": "dato",
                "detalle": f"la razón del matchup favorece a {r.valor} y `favorece` declara al lado "
                           f"{c['lado']} ({c['declarado']})",
                "jev": jv}
    if c["tipo"] == "reventon":
        if r.valor in ("no lo dice", c["etiqueta"]):
            return None
        return {"codigo": "COHERENCIA-REVENTON", "equipo": c["equipo"], "tipo": "dato",
                "detalle": f"el texto de reventón le da a {nombres[c['equipo']]} riesgo «{r.valor}» y el "
                           f"cálculo dice «{c['calculado']}». La lectura debe mirar el número, no "
                           "copiarlo ni contradecirlo sin decir por qué",
                "jev": jv}
    return None


def evaluar(parte: dict, nombres: dict, reventon: dict | None) -> dict:
    """La evaluación entera, lista para guardarse sellada. Nunca lanza: un
    fallo de Jev se declara en `error` y el depósito sigue."""
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base = {"modo": modo(), "evaluadoEn": ahora, "modelo": "", "simulado": not jev.disponible(),
            "umbral": UMBRAL, "preguntas": 0, "hallazgos": [], "concuerdan": [], "sinConfianza": [],
            "error": None}
    if modo() == "off":
        return base
    preguntas, comparar = preguntas_de(parte, nombres, reventon)
    base["preguntas"] = len(preguntas)
    if not preguntas:
        return base
    try:
        lote = jev.preguntar(_estado(parte, nombres), preguntas)
    except (jev.JevError, ValueError) as exc:
        base["error"] = str(exc)
        return base
    base["modelo"] = lote.modelo
    base["tokensEntrada"] = lote.tokens_entrada
    # simulada es la evaluación cuyas respuestas fueron TODAS simuladas; un
    # guion que pasa por real (tests, casetes) cuenta como evaluación real
    base["simulado"] = all(r.simulado for r in lote.values())
    for clave, r in lote.items():
        if not r.fiable(UMBRAL):
            base["sinConfianza"].append({"pregunta": clave, "confianza": round(r.confianza, 3),
                                         "simulado": r.simulado})
            continue
        h = _hallazgo(clave, r, comparar[clave], nombres)
        if h:
            base["hallazgos"].append(h)
        else:
            base["concuerdan"].append(clave)
    return base


def alertas_de(coherencia: dict | None) -> list[dict]:
    """Las alertas que van a la tira del parte: solo en modo `alertas`, y
    sellando de dónde salieron. En sombra la evaluación se ve en `coherencia`
    y no en la tira."""
    if not coherencia or coherencia.get("modo") != "alertas":
        return []
    return [{**h, "origen": "jev", "modelo": coherencia.get("modelo"),
             "evaluadoEn": coherencia.get("evaluadoEn")} for h in coherencia.get("hallazgos") or []]


def resumen_recibo(coherencia: dict | None) -> dict:
    """Lo que Cowork ve en el recibo del POST.

    En SOMBRA solo los conteos: si Cowork viera el detalle corregiría para
    conformar al revisor y la medición contra el criterio humano quedaría
    sesgada. En ALERTAS va el detalle, porque ahí el flujo es «leer el recibo
    → re-depositar corregido o sostener y explicar en `notas`», igual que
    con `rechazos` (docs/COWORK.md).
    """
    c = coherencia or {}
    out = {"modo": c.get("modo"), "preguntas": c.get("preguntas", 0),
           "hallazgos": len(c.get("hallazgos") or []),
           "simulado": bool(c.get("simulado")), "error": c.get("error")}
    if c.get("modo") == "alertas" and c.get("hallazgos"):
        out["detalle"] = [{"codigo": h["codigo"], "equipo": h["equipo"], "detalle": h["detalle"]}
                          for h in c["hallazgos"]]
        out["queHacer"] = ("cada hallazgo es una contradicción entre un texto tuyo y un número tuyo: "
                           "o re-depositás el parte corregido, o lo sostenés y decís por qué en "
                           "`notas`. Nunca cambies un número solo para conformar al revisor")
    return out
