"""EN QUIÉN DESCONFIAR, en el parte (10/11/2026, usuario: «tal vez no podemos
elegir quién va a ganar, pero podemos elegir en quién desconfiar… bajar de 3 a 2
es muchísimo»). Calculado AL LEER, como el reventón: el parte no lo trae y, si
llega en el eco, se ignora.

De `docs/revisiones/ESTUDIO_ECHADOS_2026-11.md` y `DESCONFIAR_propuesta.md`. Por
indicación del usuario, cada pieza tiene su peso en la pantalla:

- **A · la ventaja por fuerza** (en negrita): con 1 de ventaja al descanso, cuánto
  NO gana un equipo según su probabilidad previa sin margen. Tabla de 53.108
  partidos (football-data, 11 ligas europeas, 2012-2026, cuota de cierre); el CSV
  no trae minutos, por eso es la ventaja del DESCANSO. Igual en las dos mitades y
  de local o de visita. Es referencia provisional hasta rehacerla por minuto con
  la base (`ventajaPorMinuto` del TDE ya existe, sin la fuerza).
- **B y C · la alerta** (DESCONFIAR, a la tira): nuestra prob. del elegido 2+
  puntos SOBRE la casa (B) o su racha + de UN solo partido con riesgo alto o muy
  alto (C). La misma regla que la simulación (`simulacion.alerta_confianza`).
- **D · el descarte** (muy resaltado cuando hay alerta): «el otro lado no gana»
  —elegido o empate— con nuestra probabilidad y la de la casa. Es lectura, no
  una apuesta: qué se juega lo decide el método con 100+ casos.
- **E · para el analista**: la tipología ECHADA / SOB del TDE no separó quién
  pierde la ventaja (17,6 % contra 17,5 %); el número lo pone la fuerza (A).

No mueve el 1X2 ni ningún número del parte (decisión del usuario del 03/11).
"""
from __future__ import annotations

# (desde, hasta, rótulo, no gana con 1 de ventaja, no gana con 2+), en 0-1
TABLA_VENTAJA = (
    (0.00, 0.35, "< 35 %", 0.469, 0.174),
    (0.35, 0.48, "35-48 %", 0.310, 0.081),
    (0.48, 0.60, "48-60 %", 0.244, 0.054),
    (0.60, 0.75, "60-75 %", 0.157, 0.034),
    (0.75, 1.01, "75 %+", 0.094, 0.013),
)
FUENTE_VENTAJA = ("53.108 partidos de football-data (11 ligas europeas, 2012-2026, cuota de cierre sin margen), "
                  "ventaja al descanso: docs/revisiones/ESTUDIO_ECHADOS_2026-11.md §9")
PARA_EL_ANALISTA = ("la tipología ECHADA / SOB del TDE no separó quién pierde la ventaja (17,6 % contra 17,5 % "
                    "en 37 partidos perdidos y 157 sostenidos, 01-09/11): describe la VÍA por la que llega el "
                    "empate (banco rival, contra, pelota parada); el NÚMERO del desenlace lo pone la fuerza "
                    "previa (la ventaja por fuerza de arriba)")
CLAVES = ("local", "empate", "visita")
LADO = {"local": "a", "visita": "b"}


def ventaja_por_fuerza(prob_pct: float | None) -> dict | None:
    """La fila de la tabla para un equipo con esa probabilidad previa (en %)."""
    if prob_pct is None:
        return None
    p = float(prob_pct) / 100
    for desde, hasta, rot, uno, dos in TABLA_VENTAJA:
        if desde <= p < hasta:
            return {"prob": round(float(prob_pct), 1), "tramo": rot, "noGanaCon1": uno, "noGanaCon2": dos}
    return None


def de_fixture(fixture_id: int) -> dict:
    """LA VENTAJA POR FUERZA ANTES DE ESCRIBIR LAS RAMAS (17/11/2026, TDE v0.1.27 punto 2,
    «Para la app» A1). Hasta hoy vivía solo en el bloque `desconfianza`, que se arma al
    leer el parte YA depositado: quien escribía la rama de ventaja del TDE no la tenía.
    La misma tabla y la misma cuota (1X2 de la casa sin margen, última captura
    prepartido), por lado; sin cuota, `sinCuota` y los lados en None."""
    from backend.analisis.lecciones import cuotas_mercado
    try:
        m = cuotas_mercado([fixture_id]).get(fixture_id)
    except Exception:  # noqa: BLE001 — sin cuotas no hay fuerza que leer; se dice
        m = None
    mercado = {k: m["prob"][k] for k in CLAVES} if m else None
    return {"a": ventaja_por_fuerza(mercado["local"]) if mercado else None,
            "b": ventaja_por_fuerza(mercado["visita"]) if mercado else None,
            "sinCuota": mercado is None,
            "fuente": FUENTE_VENTAJA, "paraElAnalista": PARA_EL_ANALISTA,
            "nota": "con 1 de ventaja (o 2+) al DESCANSO, cuánto NO gana un equipo según su probabilidad "
                    "previa sin margen (`noGanaCon1`, `noGanaCon2`, en 0-1). La rama de ventaja cita el campo: "
                    "el número del desenlace lo pone la fuerza y la tipología describe la vía"}


def _burbuja(reventon: dict | None, lado: str | None) -> dict | None:
    if not reventon or not lado:
        return None
    r = reventon.get(lado) or {}
    act = r.get("actual") or {}
    if not act:
        return None
    return {"signo": act.get("signo"), "partidos": act.get("partidos"), "riesgo": (r.get("riesgo") or {}).get("nivel")}


def leer(pron: dict | None, mercado: dict | None, reventon: dict | None, nombres: dict) -> dict | None:
    """El bloque `desconfianza` del parte. `mercado` = {local, empate, visita}
    sin margen en %; sin 1X2 declarado no hay bloque."""
    from backend.analisis.simulacion import alerta_confianza, _normalizar, _elegido
    probs = (pron or {}).get("probabilidades") or {}
    p = _normalizar(probs)
    if not p:
        return None
    e = _elegido(p)
    nuestras = {k: round(100 * p[k], 1) for k in CLAVES}
    burb = _burbuja(reventon, LADO.get(e))
    alerta = alerta_confianza(probs, mercado, burb)
    descartado = min(CLAVES, key=lambda k: nuestras[k])
    out = {
        "elegido": e,
        "alerta": alerta,
        "burbujaElegido": burb,
        "descarte": {"resultado": descartado, "nuestra": nuestras[descartado],
                     "casa": round(float(mercado[descartado]), 1) if mercado else None},
        "dobleOportunidad": None,
        # el elegido, nuestro número contra el de la casa (para 1X2-CARGA-CONTRA-RIESGO)
        "probElegido": {"nuestra": nuestras[e], "casa": round(float(mercado[e]), 1) if mercado else None},
        "ventajaPorFuerza": {lado: ventaja_por_fuerza(mercado.get(k)) if mercado else None
                             for k, lado in LADO.items()},
        "fuenteVentaja": FUENTE_VENTAJA,
        "paraElAnalista": PARA_EL_ANALISTA,
        "nota": ("no mueve el 1X2: dice en quién desconfiar. Se mide en la Simulación desde el 10/11/2026; "
                 "qué se juega con la alerta lo decide el método con 100+ casos"),
    }
    if e != "empate":
        otro = "visita" if e == "local" else "local"
        out["dobleOportunidad"] = {
            "texto": f"{nombres.get(LADO[otro], otro)} no gana: {nombres.get(LADO[e], e)} o empate",
            "seleccion": [e, "empate"],
            "nuestra": round(nuestras[e] + nuestras["empate"], 1),
            "casa": round(float(mercado[e]) + float(mercado["empate"]), 1) if mercado else None,
            "resaltar": alerta["activa"],
        }
    return out


_EXTREMOS = ("K-EXTREMO", "K-CERCA-EXTREMO", "K-EXTREMO-CONDICION", "K-CERCA-EXTREMO-CONDICION")


def alerta_carga(bloque: dict | None, reventon: dict | None, alertas: list, nombres: dict) -> list[dict]:
    """1X2-CARGA-CONTRA-RIESGO (17/11/2026, aprobada en la sad-analysis v4.4 y pedida otra vez
    en la v4.6, «Para la app» 3): el 1X2 declarado sigue una racha con riesgo alto o muy alto
    (o en K-EXTREMO / K-CERCA-EXTREMO) y el número del elegido queda SOBRE el de la casa. Es la
    guardia de «con riesgo alto, el número del lado de la racha no sube sobre el mercado»: el
    cumplimiento se frena en el recibo, no repitiendo la regla. Tipo dato; no mueve nada.
    Armenia–Chipre 1528959, Once Caldas 1648691, Llaneros 1549870."""
    from backend.analisis.veredicto import pronostico_vs_racha
    if not bloque or bloque.get("elegido") in (None, "empate"):
        return []
    pe = bloque.get("probElegido") or {}
    if pe.get("casa") is None or pe.get("nuestra") is None or pe["nuestra"] <= pe["casa"]:
        return []
    extremos = {a.get("equipo") for a in alertas or [] if isinstance(a, dict) and a.get("codigo") in _EXTREMOS}
    motivos = []
    for lado in ("a", "b"):
        act = ((reventon or {}).get(lado) or {})
        signo = (act.get("actual") or {}).get("signo")
        nivel = (act.get("riesgo") or {}).get("nivel") or ""
        if not signo or not (nivel in ("alto", "muy alto") or lado in extremos):
            continue
        if pronostico_vs_racha(lado, {"signo": signo, "riesgo": {"nivel": "alto"}},
                               bloque["elegido"])["pronosticoVsRacha"] != "aFavor":
            continue
        por = f"riesgo {nivel}" if nivel in ("alto", "muy alto") else "en el extremo de su K"
        motivos.append(f"{nombres.get(lado, lado)}: racha {signo} ({por}) y el 1X2 apuesta a que sigue")
    if not motivos:
        return []
    return [{"codigo": "1X2-CARGA-CONTRA-RIESGO", "equipo": "global", "tipo": "dato", "motivos": motivos,
             "detalle": "; ".join(motivos) + f". El elegido quedó en {pe['nuestra']:g} % contra {pe['casa']:g} % "
                        "de la casa: con riesgo alto, el número del lado de la racha no sube sobre el mercado "
                        "(sad-analysis 1.6) y el `porque` del 1X2 nombra el riesgo"}]


def alerta_tira(bloque: dict | None, nombres: dict) -> list[dict]:
    """DESCONFIAR a la tira de alertas (tipo dato), con sus motivos."""
    if not bloque or not (bloque.get("alerta") or {}).get("activa"):
        return []
    e = bloque["elegido"]
    motivos = bloque["alerta"]["motivos"]
    do = bloque.get("dobleOportunidad") or {}
    return [{
        "codigo": "DESCONFIAR", "equipo": LADO.get(e, "global"), "tipo": "dato",
        "motivos": [m["codigo"] for m in motivos],
        "detalle": ("desconfiar del elegido (" + nombres.get(LADO.get(e, ""), e) + "): "
                    + "; ".join(m["detalle"] for m in motivos)
                    + (f". La lectura que restringe: {do['texto']}" if do.get("texto") else "")
                    + ". No mueve el 1X2 (ESTUDIO_ECHADOS_2026-11.md)"),
    }]
