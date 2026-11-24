"""El modo de fallo de un veredicto — etiqueta para el dossier (fase D), con Jev.

Qué hueco tapa. Cada veredicto deja, por lado, un juicio en prosa: `queP` (qué
pasó) y `leccion`. La fase D del bucle (docs/APRENDIZAJE.md) arma un dossier
cada N fallos del mismo skill, y hoy ese dossier solo puede LISTAR los fallos:
nadie los agrupa por causa. Cuatro fallos que son cuatro imprevistos no piden
lo mismo que cuatro fallos de la misma lectura del EFE.

Acá Jev lee SOLO la prosa del veredicto y la ubica en una taxonomía cerrada
—de qué naturaleza fue el fallo— y responde una segunda cosa que al dossier le
importa aún más: si la lección PIDE MOVER UN NÚMERO del skill (un peso, un
umbral, una escala) o solo aclarar cómo se aplica una regla. Cruzado con
`puedeMoverNumeros` —que sale de la población, no del texto— da la alarma que
el dossier necesita: una lección de un caso contaminado que pide mover un peso.

Lo que esto NO hace, y es definitivo (docs/JEV.md):
- no toca la población del caso (`ciega` / `por_resultado` / `post_resultado`):
  esa la declara quien analizó y es lo que decide si acredita;
- no entra en ninguna métrica: ni tasa de acierto, ni Brier, ni reventón;
- no cambia el estado de una lección ni pone nada en cuarentena;
- no juzga si el veredicto es correcto: etiqueta de qué habla.

Se evalúa AL CERRAR el caso (POST veredicto) y se guarda sellada con el modelo
(`modo_fallo_json`): Jev no es determinista y rehacerla al leer haría que el
dossier cambiara de forma solo. Sin clave, simulado con confianza 0: ninguna
etiqueta se emite. Un fallo de Jev se declara y el veredicto se guarda igual.
"""
import json
from datetime import datetime, timezone

from backend.analisis import jev

# La taxonomía. Cerrada a propósito y con «no lo dice» como salida: el modelo
# es literal y sin escape elige el parecido más cercano aunque no lo sea.
MODOS = {
    "insumo": "el dato de entrada estaba mal o faltaba ANTES del partido: DT viejo o desconocido, "
              "plantel incompleto, once que no llegó, ficha sin eventos, cuota no capturada",
    # `lectura` (17/11/2026, decisión del usuario del 10/11, A0 de la EFE v1.10): era
    # `lectura_efe` y Jev la usaba para CUALQUIER regla mal aplicada —de 107 fallos del
    # TDE con esa etiqueta, 7 hablaban del EFE—. El dossier ya es por skill: `lectura`
    # en el dossier del DTP es lectura del DTP.
    "lectura": "una regla del propio skill del que habla el texto se aplicó mal: un bloque o un "
               "indicador puntuó lo que el texto no sostenía, se apartó del defecto sin el sostén que "
               "pide la regla, se ignoró una alerta, o se tomó una referencia de otra condición",
    "tde": "el tramo final: la ventana o el índice de echada / sobreexposición no describieron lo "
           "que pasó en los últimos minutos",
    "reventon": "la racha: se apostó a que la burbuja seguía (o se cortaba) contra lo que decía el "
                "riesgo de reventón, o se ignoró la alerta de extremo",
    "mercado": "el reparto 1X2 o la lectura de la cuota no reflejaban lo que el propio análisis "
               "decía: el número y el texto apuntaban a resultados distintos",
    "imprevisto": "algo no analizable antes del partido: expulsión, lesión en juego, penal dudoso, "
                  "error arbitral, gol en el descuento, clima, suspensión",
    "varianza": "el análisis era razonable y salió el resultado menos probable: el texto no señala "
                "ningún error y no propone corregir nada",
    "no_lo_dice": "el texto no permite ubicar el fallo en ninguna de las anteriores, o no explica "
                  "por qué falló",
}
# LO YA SELLADO NO SE RE-ETIQUETA (decisión del 10/11): al leer, la etiqueta vieja
# cuenta como la nueva
LEGADO = {"lectura_efe": "lectura"}


def canonico(modo: str | None) -> str | None:
    """La etiqueta sellada con el nombre de hoy (`lectura_efe` → `lectura`)."""
    return LEGADO.get(modo, modo) if modo else modo


# probabilidad del noul «pide mover un número»: actuar ≥ 0.70, negar ≤ 0.30
# (los umbrales del cookbook de guardrails de Jev); en medio, no se sabe
P_SI, P_NO = 0.70, 0.30
UMBRAL_MODO = 0.6   # confianza del choice; primer corte, se calibra con el reporte
VEREDICTOS_CON_FALLO = ("fallo", "parcial")


def _estado(por_lado: dict, nombres: dict) -> dict:
    return {"lados": {lado: {"equipo": nombres.get(lado, lado), "veredicto": v.get("veredicto"),
                             "quePaso": v.get("queP") or "", "leccion": v.get("leccion") or "",
                             "reglaTocada": v.get("reglaTocada") or "", "skill": v.get("skill") or ""}
                      for lado, v in por_lado.items()}}


def preguntas_de(por_lado: dict, nombres: dict) -> dict:
    preguntas = {}
    for lado, v in por_lado.items():
        if v.get("veredicto") not in VEREDICTOS_CON_FALLO:
            continue
        if not ((v.get("queP") or "").strip() or (v.get("leccion") or "").strip()):
            continue  # sin prosa no hay nada que etiquetar
        quien = nombres.get(lado, lado)
        preguntas[f"modo_{lado}"] = jev.eleccion(
            f"Leé SOLO lados.{lado} (el veredicto sobre {quien}: quePaso, leccion, reglaTocada). "
            "¿De qué naturaleza fue el fallo que describe ese texto?", MODOS)
        if (v.get("leccion") or "").strip():
            preguntas[f"mueve_{lado}"] = jev.sino(
                f"Leé SOLO lados.{lado}.leccion. ¿La lección pide cambiar un NÚMERO del skill "
                "—un peso, un umbral, una escala, una puntuación— y no solo aclarar cómo se "
                "aplica una regla?",
                {"true": "propone subir, bajar o recalibrar un valor numérico del skill",
                 "false": "aclara, precisa o reordena una regla sin tocar ningún número, "
                          "o no propone ningún cambio"})
    return preguntas


def evaluar(por_lado: dict, nombres: dict) -> dict:
    """La etiqueta por lado, lista para sellarse. Nunca lanza."""
    base = {"evaluadoEn": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "modelo": "", "simulado": not jev.disponible(), "preguntas": 0,
            "lados": {}, "error": None, "taxonomia": list(MODOS)}
    preguntas = preguntas_de(por_lado, nombres)
    base["preguntas"] = len(preguntas)
    if not preguntas:
        return base
    try:
        lote = jev.preguntar(_estado(por_lado, nombres), preguntas)
    except (jev.JevError, ValueError) as exc:
        base["error"] = str(exc)
        return base
    base["modelo"] = lote.modelo
    base["simulado"] = all(r.simulado for r in lote.values())
    # POR DÓNDE PASÓ. Un intermediario no afiliado no vale lo que el oficial:
    # la evaluación se sella con el host para poder apartarla después.
    base["via"] = lote.via
    base["oficial"] = jev.oficial() and not all(r.simulado for r in lote.values())
    base["tokensEntrada"] = lote.tokens_entrada
    for lado in por_lado:
        modo_r, mueve_r = lote.get(f"modo_{lado}"), lote.get(f"mueve_{lado}")
        if not modo_r:
            continue
        salida = {"modo": None, "modoConfianza": round(modo_r.confianza, 3),
                  "proponeMoverNumero": None, "proponeMoverP": None}
        if modo_r.fiable(UMBRAL_MODO):
            salida["modo"] = modo_r.valor
        if mueve_r and not mueve_r.simulado:
            p = mueve_r.probabilidad()
            salida["proponeMoverP"] = round(p, 3)
            salida["proponeMoverNumero"] = True if p >= P_SI else (False if p <= P_NO else None)
        base["lados"][lado] = salida
    return base


# ── LA ETIQUETA QUE NO LLEGÓ (24/11/2026) ────────────────────────────────────
# Desde el 22/11 a la 01:31 UTC Jev respondió 402 «Insufficient credits» a cada
# veredicto: el error quedó sellado en `modo_fallo_json` y nadie lo vio hasta el
# estudio de lecciones del 24/11 (0 de 39 lados fallados etiquetados el 22/11).
# Dos arreglos de la CLASE: el escaneo lo grita (chequeo `jev-caido`) y esto
# rehace lo que nunca se etiquetó. NO contradice «lo sellado no se re-etiqueta»:
# un sello con `error` no tiene etiqueta que proteger. Lo que sí tiene una (o es
# de antes de que existiera, `null`) no se toca.

def _sin_etiqueta_por_error(m: dict | None) -> bool:
    return bool(m) and bool(m.get("error")) and not m.get("lados")


def reetiquetar(aplicar: bool = False, limite: int = 300) -> dict:
    """Vuelve a preguntarle a Jev por los veredictos cuyo sello quedó en error.

    Sin `aplicar` solo cuenta. Sin clave no hace nada (una respuesta simulada
    pisaría el error con un vacío que parece evaluado). Corta en el primer
    error nuevo: si el crédito sigue agotado, no se gasta el resto en 402."""
    from backend.analisis import parte as _parte
    with _parte._conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, veredicto_json, modo_fallo_json FROM parte_cowork "
            "WHERE veredicto_json IS NOT NULL AND modo_fallo_json LIKE '%\"error\"%' "
            "ORDER BY fecha, fixture_id").fetchall()
    pendientes = []
    for f in filas:
        try:
            m = json.loads(f["modo_fallo_json"])
        except (TypeError, ValueError):
            continue
        if _sin_etiqueta_por_error(m):
            pendientes.append((f["fixture_id"], json.loads(f["veredicto_json"]), m))
    errores = {}
    for _, _, m in pendientes:
        clave = str(m.get("error"))[:120]
        errores[clave] = errores.get(clave, 0) + 1
    out = {"pendientes": len(pendientes), "erroresSellados": errores, "aplicar": aplicar,
           "disponible": jev.disponible(), "reetiquetados": [], "sinCambio": [], "cortadoPor": None}
    if not aplicar:
        return out
    if not jev.disponible():
        out["cortadoPor"] = "sin TYPESAFE_API_KEY: no se re-etiqueta con respuestas simuladas"
        return out
    for fixture_id, vered, previo in pendientes[:max(0, limite)]:
        fx = _parte._fixture(fixture_id)
        nombres = {"a": fx["home_name"], "b": fx["away_name"]} if fx else {}
        nuevo = evaluar(vered.get("porLado") or {}, nombres)
        if nuevo.get("error"):
            out["cortadoPor"] = f"{fixture_id}: {nuevo['error']}"
            break
        if nuevo.get("simulado"):
            out["sinCambio"].append(fixture_id)
            continue
        nuevo["reetiquetado"] = {"en": nuevo["evaluadoEn"], "errorAnterior": previo.get("error"),
                                 "evaluadoAntesEn": previo.get("evaluadoEn")}
        with _parte._conectar() as con:
            con.execute("UPDATE parte_cowork SET modo_fallo_json=? WHERE fixture_id=?",
                        (json.dumps(nuevo, ensure_ascii=False), fixture_id))
        out["reetiquetados"].append(fixture_id)
    out["quedan"] = out["pendientes"] - len(out["reetiquetados"])
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="re-etiqueta los veredictos cuyo sello de Jev quedó en error")
    ap.add_argument("--aplicar", action="store_true", help="sin esto solo cuenta")
    ap.add_argument("--limite", type=int, default=300)
    a = ap.parse_args()
    print(json.dumps(reetiquetar(a.aplicar, a.limite), ensure_ascii=False, indent=1))
