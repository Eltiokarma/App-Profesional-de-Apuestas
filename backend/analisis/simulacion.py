"""SIMULACIÓN DE APUESTA (28/10/2026, pedido del usuario).

Qué habría pasado con una banca si se hubiera apostado con nuestros 1X2
declarados, con tres estrategias puestas lado a lado:

- **plana** (control): 1 unidad a nuestro elegido —el resultado con más
  probabilidad del pronóstico— en cada partido, a la cuota media de las casas.
- **kelly**: el criterio de Kelly sobre NUESTRAS probabilidades. Por partido,
  la selección con la fracción f* = (p·c − 1)/(c − 1) más alta. Con f* ≤ 0 no
  se apuesta: la cuota no paga lo que creemos. Se apuesta f*·banca, entero
  (`kelly`), a la mitad (`kellyMedio`) y a un cuarto (`kellyCuarto`).
- **martingala**: a nuestro elegido, por LÍNEAS (29/10/2026, usuario): cada
  línea es una martingala propia —1 unidad, se DUPLICA tras perder, vuelve a
  1 al ganar—; una apuesta toma la línea libre que más tiempo lleva libre y,
  si todas están ocupadas con partidos en juego, abre una nueva en 1. Si se
  pierden tres a las 15:00, los tres partidos siguientes van por 2.

- **martingala60**: la misma martingala por líneas, solo con nuestro elegido a
  60 %+ (como `plana60` respecto de la plana).

- **proporcional** (EL MÉTODO, 03/11/2026, usuario: «investiguemos el método
  definitivo»): el 1 % de la banca a nuestro elegido, con un FRENO POR TRAMO
  de confianza (<40 · 40-49 · 50-59 · 60+, los de `lecciones`). El tramo se
  pausa si en sus últimos `FRENO_VENTANA` partidos cerrados acertó menos de lo
  que pedía la cuota (1/cuota media), con `FRENO_Z` errores estándar de
  tolerancia y al menos `FRENO_MINIMO` partidos; en pausa sigue ANOTANDO (los
  partidos sin apuesta cuentan), así que vuelve solo cuando el tramo se
  recupera. No busca valor contra el mercado: la cuota la pone la casa y
  nosotros elegimos dónde poner la plata. Medido el 03/11 sobre 374 partes
  (15/09-01/11) con remuestreo por días y con los resultados sorteados según
  el mercado (sin ventaja): ver `docs/METODO_APUESTA.md`.

Las COPAS NACIONALES quedan fuera (29/10/2026, usuario): se analizan, pero un
favorito al 90 % contra uno de quinta a cuota 1.02 no es la apuesta que se mide.

Cuenta SOLO desde `DESDE` (los partidos del 28/10/2026 en adelante, hora de
Lima): lo anterior no se simula. Entran los partes depositados ANTES del
pitazo (`deposito_previo_en`), sin cuarentena, con el 1X2 completo y las tres
cuotas capturadas. Se RECALCULA al leer, como todo lo derivado: un partido
que termina después mueve las bancas siguientes.

Cada apuesta viaja con la VERSIÓN de cada skill que estaba en la cuenta al
depositar el parte; la del 1X2 es la de `sad-analysis`. La versión sale de
`lecciones.CORTE_VERSION` (por día) y, cuando se sabe la hora en que el
usuario subió el zip, de `SUBIDA_VERSION`: un parte de la madrugada del día
del corte se escribió con la versión anterior.

EL TIEMPO ES EL DE LA VIDA REAL (29/10/2026, usuario): se apuesta en el
pitazo y se cobra `DURACION` después. Una apuesta solo sabe lo que ya se
liquidó: los partidos simultáneos —y los que se solapan— se apuestan con la
banca que había antes, ninguno espera el resultado de otro. Lo que está en
juego queda comprometido: una apuesta nueva no puede pasar de la plata libre
(banca − lo comprometido), así que Kelly no se pasa de la banca con ocho
partidos a la vez y la martingala no apuesta plata que ya está en otra línea.

Esto NO es una recomendación de apuesta. La cuota es la media de las casas
en la última captura prepartido y trae su margen.
"""
from __future__ import annotations

import json
import math
from collections import deque
from datetime import datetime, timedelta, timezone

from backend import db as saddb
from backend.analisis import semaforo as _sem, veredicto as _vered
from backend.analisis.escala import copas_nacionales
from backend.analisis.lecciones import CORTE_VERSION, TRAMOS_CONFIANZA, cuotas_mercado, tramo_confianza

# 00:00 de Lima (UTC−5) del 28/10/2026: «recién desde los partidos de hoy»
DESDE = "2026-10-28 05:00:00"
BANCA_INICIAL = 100.0
UNIDAD = 1.0
# el tramo alto de confianza del 1X2 (el «60+» de lecciones.TRAMOS_CONFIANZA)
CONFIANZA_ALTA = 60.0
# cuánto después del pitazo se cobra: no tenemos la hora de fin de cada
# partido, y 90 minutos con el descanso y el añadido son unas dos horas
DURACION = timedelta(minutes=120)
CLAVES = ("local", "empate", "visita")
# EL MÉTODO (docs/METODO_APUESTA.md): fracción de la banca y su freno por tramo
PROPORCION = 0.01
FRENO_VENTANA = 50     # últimos partidos cerrados del tramo que se miran
FRENO_MINIMO = 15      # con menos, el tramo no se juzga: se apuesta
FRENO_Z = 0.5          # tolerancia, en errores estándar, antes de pausar
# CRITERIO DE CONTACTO (04/11/2026, usuario: «las gráficas de la martingala son
# muy reveladoras»): ¿después de k fallos seguidos del elegido acertamos más que
# el promedio? En los 374 partes del 15/09-01/11 tras 3 fallos se acertó 20 de 30
# (66,7 %) contra el 55,6 %; en los 2.638 partidos de liga de la base, el
# favorito de la casa tras 3 fallos acertó el 51 %. Se toma en serio con
# `CONTACTO_N`+ casos tras `CONTACTO_K` fallos, una tasa de `CONTACTO_TASA`+ y el
# intervalo de confianza entero por encima del promedio. Fijado ANTES de mirar
# los datos nuevos: no se mueve para que se cumpla (docs/METODO_APUESTA.md).
TRAS_FALLOS_K = (1, 2, 3, 4)
CONTACTO_K = 3
CONTACTO_N = 100
CONTACTO_TASA = 0.65
SKILLS = ("sad-analysis", "efe-clasificador", "teorema-del-echado", "diagnostico-tactico")

# Hora (UTC) en que la versión llegó a la cuenta del usuario, cuando se sabe.
# Sin entrada, la versión rige desde las 00:00 UTC del día de su corte.
SUBIDA_VERSION = {
    # el usuario confirmó la subida de los zips el 28/10 hacia las 06:50 de Lima:
    # el tramo de las 04:47 todavía corrió con EFE v1.7 y sad v4.1
    ("efe-clasificador", "v1.8"): "2026-10-28 11:50:00",
    ("sad-analysis", "v4.2"): "2026-10-28 11:50:00",
    # el usuario subió sad v4.3 (goles acotados) el 30/10 a las 05:47 de Lima
    ("sad-analysis", "v4.3"): "2026-10-30 10:47:00",
    # 1143: el usuario subió los cuatro zips el domingo 01/11 hacia las 08:00
    # de Lima; el tramo de las 04:47 de ese día corrió con la versión anterior
    # (efe-dashboard v1.12 no tiene CORTE_VERSION: va con el EFE)
    ("teorema-del-echado", "v0.1.25"): "2026-11-01 13:00:00",
    ("diagnostico-tactico", "v1.7"): "2026-11-01 13:00:00",
    ("efe-clasificador", "v1.9"): "2026-11-01 13:00:00",
    ("sad-analysis", "v4.4"): "2026-11-01 13:00:00",
    # el usuario subió los cinco zips de la tanda del 10/11 hacia las 07:15 de
    # Lima (avisó a las 07:17): lo de la madrugada del 10/11 corrió con la anterior
    # (efe-dashboard v1.13 va con el EFE)
    ("teorema-del-echado", "v0.1.26"): "2026-11-10 12:15:00",
    ("diagnostico-tactico", "v1.8"): "2026-11-10 12:15:00",
    ("efe-clasificador", "v1.10"): "2026-11-10 12:15:00",
    ("sad-analysis", "v4.5"): "2026-11-10 12:15:00",
}

# EL MEDIO: lo que la casa (sin margen) le da al elegido, en % [desde, hasta)
MEDIO = (45.0, 60.0)
# el criterio cuenta desde los partidos del 14/11/2026, 00:00 de Lima
MEDIO_DESDE = "2026-11-14 05:00:00"
MEDIO_ESCALONES = (30, 60)
MEDIO_SEPARACION = 0.05   # pts de ventaja (acierto − lo que pide la cuota) de las puntas sobre el medio
# el tope de la martingala fuera del medio con tope: fracción de la banca
TOPE_MARTINGALA = 0.25

ESTRATEGIAS = (
    ("proporcional", "Proporcional con freno",
     f"{100 * PROPORCION:g} % de la banca a nuestro elegido; un tramo de confianza se pausa si en sus últimos "
     f"{FRENO_VENTANA} partidos acertó menos de lo que pedía la cuota, y vuelve cuando se recupera"),
    # EL MÉTODO SOLO EN VERDE (11/11/2026, usuario: «me apoyaré de ese
    # semáforo»): el mismo 1 % y el mismo freno, pero apuesta solo cuando el
    # semáforo del elegido está en verde (backend/analisis/semaforo.py). En papel
    ("metodoVerde", "Método solo en verde",
     f"el método ({100 * PROPORCION:g} % de la banca y el mismo freno por tramo) apostando solo cuando el "
     "semáforo del elegido está en verde: la espina del elegido lo acompaña y la del rival no dice que siga"),
    # EL MÉTODO FUERA DEL MEDIO (13/11/2026, usuario: «siento que hay una forma
    # correcta de apostar… por un lado un gran win rate, por otro buena ganancia
    # con bajo win rate»). Medido en 748 partes (14/09-13/11): la ventaja sobre
    # la cuota está en las dos PUNTAS de lo que la casa le da al elegido (< 40 %:
    # +8,4 pts; 60-70 %: +11,3; 70 %+: +9,0) y en el medio no hay (50-60 %: −1,5).
    # Sin el medio (45-60 %) la plana dio +11,5 % (n 465; +12,3 % y +9,9 % en las
    # dos mitades) contra +5,2 % de todos y −5,0 % del medio solo (n 283). Los
    # cortes salieron de esos datos: el criterio cuenta desde `MEDIO_DESDE`.
    # Las series con el marcador (método ⚽, 🟢⚽ y su martingala) se quitaron el
    # mismo día por decisión del usuario: el marcador alineado era la punta de
    # los favoritos; su tabla de win rate sigue.
    ("metodoFueraMedio", "Método fuera del medio",
     f"el método ({100 * PROPORCION:g} % de la banca y el mismo freno por tramo) sin apostar cuando la casa le da "
     f"al elegido entre {MEDIO[0]:g} % y {MEDIO[1]:g} % (sin margen): ahí no le sacamos nada a la cuota"),
    ("plana", "Apuesta plana (control)",
     f"{UNIDAD:g} unidad a nuestro elegido en cada partido"),
    # CONTROL DE CONFIANZA (29/10/2026, usuario): el tramo de 60 %+ es el que
    # más acierta en «Métricas · confianza»; esto mide si además gana plata,
    # porque al favorito claro la cuota le paga poco
    ("plana60", f"Plana solo {CONFIANZA_ALTA:g} %+",
     f"{UNIDAD:g} unidad a nuestro elegido solo cuando le damos {CONFIANZA_ALTA:g} % o más"),
    ("kelly", "Kelly completo",
     "f* = (p·c − 1)/(c − 1) de la banca a la selección con más ventaja; sin ventaja no apuesta"),
    ("kellyMedio", "Kelly ½", "la mitad de la fracción de Kelly"),
    ("kellyCuarto", "Kelly ¼", "un cuarto de la fracción de Kelly"),
    ("martingala", "Martingala",
     f"por líneas: cada línea va {UNIDAD:g} unidad a nuestro elegido, se duplica tras perder y vuelve a "
     f"{UNIDAD:g} al ganar; con todas en juego se abre otra"),
    # la martingala del tramo alto (29/10/2026, usuario): las mismas líneas,
    # solo con los partidos donde el elegido tiene 60 %+
    ("martingala60", f"Martingala {CONFIANZA_ALTA:g} %+",
     f"la misma martingala por líneas, solo cuando nuestro elegido tiene {CONFIANZA_ALTA:g} % o más"),
    # LA MARTINGALA AJUSTADA A LA CUOTA (13/11/2026, usuario: «agrega la
    # martingala ajustada a la cuota tanto a Martin 60 % y al Método 🟢⚽, borra
    # martingala Método 🟢⚽ sin ajuste»). La clásica duplica y solo recupera
    # con cuota 2,00+; con favoritos (1,40-1,60) dos derrotas dejan un hueco que
    # el acierto no tapa (la 🟢⚽ clásica ganó 76 de 112 y quedó en −0,8 %). La
    # ajustada apuesta lo que recupera lo perdido en la línea MÁS lo que habría
    # ganado 1 u: 1 + pérdida / (cuota − 1). Recupera de verdad, y crece más
    # rápido que duplicar: la caída máxima y la apuesta máxima lo dicen.
    ("martingala60Ajustada", f"Martingala {CONFIANZA_ALTA:g} %+ ajustada",
     f"por líneas, solo con nuestro elegido a {CONFIANZA_ALTA:g} % o más; tras perder apuesta 1 + lo perdido en "
     "la línea / (cuota − 1): recupera todo y gana lo de 1 u, con cualquier cuota"),
    # LA MARTINGALA AJUSTADA FUERA DEL MEDIO (13/11/2026, usuario: «las dos,
    # ármalas en la simulación con tope»). Reconstruida sobre 231 cerradas
    # fuera del medio (28/10-13/11, cuota de /cuotas): +105,6 u con 100 u
    # (ROI +15,9 %), sin quebrar, pero con una apuesta de 75 u en la peor
    # racha; en TODOS los partidos la misma ajustada quebraba con 200 u. Fuera
    # del medio entra la punta de cuota alta, que recupera una racha con poco.
    # La del tope no apuesta más de `TOPE_MARTINGALA` de la banca: si recorta,
    # la línea recupera lo que puede y arrastra el resto.
    ("martingalaFueraMedio", "Martingala fuera del medio ajustada",
     f"la martingala ajustada a la cuota (1 + lo perdido en la línea / (cuota − 1)), sin apostar cuando la casa "
     f"le da al elegido entre {MEDIO[0]:g} % y {MEDIO[1]:g} %"),
    ("martingalaFueraMedioTope", "Martingala fuera del medio ajustada, con tope",
     f"la misma, pero ninguna apuesta pasa del {100 * TOPE_MARTINGALA:g} % de la banca: si el tope recorta, la "
     "línea recupera lo que puede y arrastra el resto"),
)
_MARTINGALAS = ("martingala", "martingala60", "martingala60Ajustada", "martingalaFueraMedio", "martingalaFueraMedioTope")
# las que, tras perder, apuestan lo que recupera según la cuota (no duplican)
_AJUSTADAS = ("martingala60Ajustada", "martingalaFueraMedio", "martingalaFueraMedioTope")
# las que no apuestan en el medio (lo que la casa le da al elegido, 45-60 %)
_FUERA_MEDIO = ("metodoFueraMedio", "martingalaFueraMedio", "martingalaFueraMedioTope")
# las que no apuestan más de TOPE_MARTINGALA de la banca
_CON_TOPE = ("martingalaFueraMedioTope",)
# las series con el freno por tramo (anotan todo partido cerrado del tramo)
_CON_FRENO = ("proporcional", "metodoVerde", "metodoFueraMedio")
_SOLO_ALTA = ("plana60", "martingala60", "martingala60Ajustada")
_FRACCION_KELLY = {"kelly": 1.0, "kellyMedio": 0.5, "kellyCuarto": 0.25}


# LA OTRA MITAD DEL ANÁLISIS: EN QUIÉN DESCONFIAR (10/11/2026, usuario: «tal vez
# no podemos elegir quién va a ganar, pero podemos elegir en quién desconfiar»).
# Del estudio de los 107 fallos del 01-09/11 (docs/revisiones/ESTUDIO_ECHADOS_2026-11.md,
# §7-§8) salieron dos señales previas que separan: nuestra probabilidad del
# elegido 2+ puntos SOBRE la de la casa (nunca se adelantó en el 57 %, base
# 26,5 %) y una «burbuja» de UN solo partido positivo con riesgo alto o muy
# alto (39 %, contra 11 % de las de 3+ partidos). Con alerta, el elegido acertó
# 50 % (n 28) y sin alerta 61 % (n 236): medido sobre la misma semana donde se
# encontraron, por eso se REGISTRA desde ya y se mide hacia adelante. No cambia
# el elegido ni ninguna estrategia: es una marca por apuesta y un resumen.
ALERTA_DESDE = "2026-11-10 05:00:00"   # 00:00 de Lima del 10/11/2026
ALERTA_SOBRE_CASA = 2.0                # puntos de probabilidad sobre la casa (sin margen)
_RIESGOS_ALTOS = ("alto", "muy alto")


def alerta_confianza(probs: dict, mercado: dict | None, burbuja: dict | None) -> dict:
    """La alerta de confianza de una apuesta. `probs` y `mercado` en % (el
    mercado sin margen); `burbuja` = {signo, partidos, riesgo} de la familia
    total del ELEGIDO al día del partido, o None si no se pudo calcular."""
    p = _normalizar(probs)
    motivos = []
    if not p:
        return {"activa": False, "motivos": motivos}
    e = _elegido(p)
    if mercado and mercado.get(e) is not None:
        d = 100 * p[e] - float(mercado[e])
        if d > ALERTA_SOBRE_CASA:
            motivos.append({"codigo": "SOBRE-LA-CASA",
                            "detalle": f"le damos {100 * p[e]:.1f} % al elegido y la casa {float(mercado[e]):.1f} % (+{d:.1f} pts)"})
    if e != "empate" and burbuja and burbuja.get("signo") == "+" and burbuja.get("partidos") == 1 \
            and burbuja.get("riesgo") in _RIESGOS_ALTOS:
        motivos.append({"codigo": "BURBUJA-DE-UN-PARTIDO",
                        "detalle": f"la racha del elegido es de un solo partido con riesgo {burbuja['riesgo']}"})
    return {"activa": bool(motivos), "motivos": motivos}


def resumen_alerta(cerradas: list[dict]) -> dict:
    """Con alerta contra sin alerta, sobre las cerradas que la registran: el
    acierto del elegido, lo que pedía la cuota, la plana a 1 u y la doble
    oportunidad elegido-o-empate. Y el DESCARTE: cuánto salió lo que menos
    probable le dimos, contra lo que le daba la casa (bajar de 3 a 2)."""
    con = [f for f in cerradas if f.get("alerta") is not None]

    def grupo(fs):
        n = len(fs)
        if not n:
            return {"n": 0, "aciertos": 0, "tasa": None, "pide": None, "roiPlano": None,
                    "dobleOportunidad": None, "intervalo": None}
        ac = sum(1 for f in fs if f["resultado"] == f["elegido"])
        dc = [f for f in fs if f["elegido"] != "empate"]
        dca = sum(1 for f in dc if f["resultado"] in (f["elegido"], "empate"))
        gan = sum((f["cuotas"][f["elegido"]] - 1) if f["resultado"] == f["elegido"] else -1 for f in fs)
        return {"n": n, "aciertos": ac, "tasa": round(ac / n, 4), "intervalo": _wilson(ac, n),
                "pide": round(sum(1 / f["cuotas"][f["elegido"]] for f in fs) / n, 4),
                "roiPlano": round(gan / n, 4),
                "dobleOportunidad": ({"n": len(dc), "aciertos": dca, "tasa": round(dca / len(dc), 4),
                                      "pide": round(sum((f["mercado"][f["elegido"]] + f["mercado"]["empate"]) / 100
                                                        for f in dc) / len(dc), 4)} if dc else None)}

    desc = []
    for f in con:
        d = min(CLAVES, key=lambda k: f["probabilidades"][k])
        desc.append((f["resultado"] == d, f["mercado"][d] / 100))
    motivos: dict[str, int] = {}
    for f in con:
        for m in f["alerta"]["motivos"]:
            motivos[m["codigo"]] = motivos.get(m["codigo"], 0) + 1
    return {
        "desde": ALERTA_DESDE, "sobreCasa": ALERTA_SOBRE_CASA,
        "conAlerta": grupo([f for f in con if f["alerta"]["activa"]]),
        "sinAlerta": grupo([f for f in con if not f["alerta"]["activa"]]),
        "porMotivo": motivos,
        "descarte": ({"n": len(desc), "salio": sum(1 for s, _ in desc if s),
                      "tasa": round(sum(1 for s, _ in desc if s) / len(desc), 4),
                      "casaLeDaba": round(sum(p for _, p in desc) / len(desc), 4)} if desc else None),
        "nota": ("la alerta no cambia el elegido ni ninguna estrategia: se registra por apuesta desde el 10/11/2026 "
                 "y se mide hacia adelante (docs/revisiones/ESTUDIO_ECHADOS_2026-11.md). Con 100+ partidos con alerta "
                 "se decide si frena la carga del método"),
    }


# EL CRITERIO DEL SEMÁFORO DE LAS ESPINAS (13/11/2026, usuario: el semáforo
# dice dónde NO meter plata; «no por el value, no por el valor de la cuota»).
# Fijado ANTES de que haya partidos nuevos y, como el de contacto, NO se mueve.
# Cuenta desde los partidos del 13/11/2026 (`semaforo.DESDE`). Lo que se
# juzga es si la DESCONFIANZA acierta: el elegido en no-verde (amarillo +
# rojo) tiene que ganar MENOS que en verde. n = no-verdes nuevos cerrados
# (son los raros: ~10 % de los partes), IC = Wilson 95 % de su acierto:
#   - n < 30: en observación (faltan hasta el escalón 30).
#   - en cualquier escalón: `no_se_sostiene` si los no-verdes aciertan lo
#     mismo o más que los verdes (la desconfianza no separa).
#   - escalón 30: `prometedor` si los verdes aciertan ≥ 10 pts más; si no,
#     en observación.
#   - escalón 60: `confirmado` si los verdes aciertan ≥ 10 pts más y el
#     límite SUPERIOR del IC de los no-verdes queda por debajo del acierto de
#     los verdes; si no, `sin_contacto`.
# La cuota viaja como información (`pide`): no decide.
SEMAFORO_ESCALONES = (30, 60)
SEMAFORO_N = SEMAFORO_ESCALONES[-1]
SEMAFORO_SEPARACION = 0.10


def _grupo_semaforo(fs: list[dict]) -> dict:
    n = len(fs)
    if not n:
        return {"n": 0, "aciertos": 0, "tasa": None, "intervalo": None, "pide": None, "ventaja": None,
                "roiPlano": None}
    ac = sum(1 for f in fs if f["resultado"] == f["elegido"])
    pide = sum(1 / f["cuotas"][f["elegido"]] for f in fs) / n
    gan = sum((f["cuotas"][f["elegido"]] - 1) if f["resultado"] == f["elegido"] else -1 for f in fs)
    return {"n": n, "aciertos": ac, "tasa": round(ac / n, 4), "intervalo": _wilson(ac, n),
            "pide": round(pide, 4), "ventaja": round(ac / n - pide, 4), "roiPlano": round(gan / n, 4)}


def criterio_semaforo(v: dict, nv: dict) -> dict:
    """El estado del criterio por escalones con los verdes (`v`) y los
    no-verdes —amarillos + rojos— (`nv`) NUEVOS, cada uno como lo arma
    `_grupo_semaforo`."""
    n = nv["n"]
    escalon = max((e for e in SEMAFORO_ESCALONES if n >= e), default=0)
    proximo = next((e for e in SEMAFORO_ESCALONES if n < e), None)
    tv, tnv, ic = v["tasa"], nv["tasa"], nv["intervalo"]
    sep = None if tv is None or tnv is None else tv - tnv
    debajo = ic is not None and tv is not None and ic[1] < tv
    if escalon == 0:
        estado = "en_observacion"
    elif sep is None or sep <= 0:
        estado = "no_se_sostiene"
    elif escalon < SEMAFORO_N:
        estado = "prometedor" if sep >= SEMAFORO_SEPARACION - 1e-9 else "en_observacion"
    else:
        estado = "confirmado" if sep >= SEMAFORO_SEPARACION - 1e-9 and debajo else "sin_contacto"
    pct = lambda x: f"{100 * x:.1f} %"  # noqa: E731
    cifras = (f"el elegido gana {pct(tv)} en verde ({v['n']}) y {pct(tnv)} en amarillo o rojo ({n}, IC "
              f"{100 * ic[0]:.0f}-{100 * ic[1]:.0f} %): {100 * sep:+.1f} pts"
              if sep is not None else "")
    sigue = f" · faltan {proximo - n} no-verdes para el escalón {proximo}" if proximo else ""
    if estado == "confirmado":
        texto = (f"CONFIRMADO en el escalón {escalon}: {cifras}, {100 * SEMAFORO_SEPARACION:.0f}+ pts con el "
                 "intervalo de los no-verdes entero por debajo: la desconfianza de las espinas separa")
    elif estado == "no_se_sostiene":
        texto = (f"NO SE SOSTIENE en el escalón {escalon}: "
                 + (f"{cifras}; el amarillo y el rojo no aciertan menos que el verde" if cifras
                    else "sin verdes con que comparar"))
    elif estado == "prometedor":
        texto = f"PROMETEDOR en el escalón {escalon}: {cifras}{sigue}"
    elif estado == "sin_contacto":
        texto = (f"sin contacto en el escalón {escalon}: {cifras}; pide {100 * SEMAFORO_SEPARACION:.0f}+ pts con "
                 "el intervalo de los no-verdes entero por debajo del verde")
    else:
        texto = (f"en observación{f' (escalón {escalon})' if escalon else ''}: {n} amarillos o rojos nuevos"
                 + (f", {cifras}" if cifras else "") + sigue)
    return {
        "escalon": escalon, "proximoEscalon": proximo, "escalones": list(SEMAFORO_ESCALONES),
        "faltan": (proximo - n) if proximo else 0, "n": n,
        "verdes": {"n": v["n"], "tasa": tv},
        "noVerdes": {"n": n, "tasa": tnv, "intervalo": ic},
        "separacion": None if sep is None else round(sep, 4),
        "nMinimo": SEMAFORO_N, "separacionMinima": SEMAFORO_SEPARACION,
        "noVerdesDebajo": debajo,
        "cumple": estado == "confirmado", "estado": estado, "texto": texto,
    }


# EL CRITERIO DEL MARCADOR (13/11/2026, usuario: «no era medir contra la cuota,
# era medir si nuestro win rate mejoraba»). Fijado ANTES de los partidos nuevos
# y, como el del semáforo, NO se mueve. Cuenta desde `MARCADOR_DESDE` (00:00 de
# Lima del 14/11: la regla salió de los partes hasta el 13/11). Se juzga el
# WIN RATE del elegido con el marcador más probable alineado contra el resto
# (1-1, 0-0 o contrario). n = alineados nuevos cerrados (~28 % de los partes),
# IC = Wilson 95 % de su acierto, con los escalones del semáforo:
#   - n < 30: en observación.
#   - en cualquier escalón: `no_se_sostiene` si los alineados ganan lo mismo
#     o menos que el resto.
#   - escalón 30: `prometedor` con 10+ pts sobre el resto; si no, en observación.
#   - escalón 60: `confirmado` con 10+ pts y el límite INFERIOR del IC de los
#     alineados por encima del win rate del resto; si no, `sin_contacto`.
# La cuota viaja como información (`pide`, `roiPlano`): no decide.
MARCADOR_DESDE = "2026-11-14 05:00:00"
MARCADOR_ESCALONES = (30, 60)
MARCADOR_SEPARACION = 0.10


def criterio_marcador(al: dict, resto: dict) -> dict:
    """El estado del criterio con los alineados (`al`) y el resto NUEVOS, cada
    uno como lo arma `_grupo_semaforo`."""
    n = al["n"]
    escalon = max((e for e in MARCADOR_ESCALONES if n >= e), default=0)
    proximo = next((e for e in MARCADOR_ESCALONES if n < e), None)
    ta, tr, ic = al["tasa"], resto["tasa"], al["intervalo"]
    sep = None if ta is None or tr is None else ta - tr
    encima = ic is not None and tr is not None and ic[0] > tr
    if escalon == 0:
        estado = "en_observacion"
    elif sep is None or sep <= 0:
        estado = "no_se_sostiene"
    elif escalon < MARCADOR_ESCALONES[-1]:
        estado = "prometedor" if sep >= MARCADOR_SEPARACION - 1e-9 else "en_observacion"
    else:
        estado = "confirmado" if sep >= MARCADOR_SEPARACION - 1e-9 and encima else "sin_contacto"
    pct = lambda x: f"{100 * x:.1f} %"  # noqa: E731
    cifras = (f"el elegido gana {pct(ta)} con el marcador alineado ({n}, IC {100 * ic[0]:.0f}-{100 * ic[1]:.0f} %)"
              f" y {pct(tr)} con el resto ({resto['n']}): {100 * sep:+.1f} pts" if sep is not None else "")
    sigue = f" · faltan {proximo - n} alineados para el escalón {proximo}" if proximo else ""
    textos = {
        "confirmado": f"CONFIRMADO en el escalón {escalon}: {cifras}, {100 * MARCADOR_SEPARACION:.0f}+ pts con el "
                      "intervalo de los alineados entero por encima del resto: el marcador separa",
        "no_se_sostiene": f"NO SE SOSTIENE en el escalón {escalon}: " + (
            f"{cifras}; con el marcador alineado no se gana más" if cifras else "sin partidos con que comparar"),
        "prometedor": f"PROMETEDOR en el escalón {escalon}: {cifras}{sigue}",
        "sin_contacto": f"sin contacto en el escalón {escalon}: {cifras}; pide {100 * MARCADOR_SEPARACION:.0f}+ pts "
                        "con el intervalo de los alineados entero por encima del resto",
    }
    texto = textos.get(estado) or (f"en observación{f' (escalón {escalon})' if escalon else ''}: {n} alineados "
                                   "nuevos" + (f", {cifras}" if cifras else "") + sigue)
    return {"escalon": escalon, "proximoEscalon": proximo, "escalones": list(MARCADOR_ESCALONES),
            "faltan": (proximo - n) if proximo else 0, "n": n,
            "alineados": {"n": n, "tasa": ta, "intervalo": ic}, "resto": {"n": resto["n"], "tasa": tr},
            "separacion": None if sep is None else round(sep, 4),
            "nMinimo": MARCADOR_ESCALONES[-1], "separacionMinima": MARCADOR_SEPARACION,
            "alineadosEncima": encima, "cumple": estado == "confirmado", "estado": estado, "texto": texto}


def resumen_marcador(cerradas: list[dict]) -> dict:
    """Alineados contra el resto (y sin marcador), en todo lo simulado y en lo
    NUEVO (desde `MARCADOR_DESDE`), que es lo único que cuenta para el criterio."""
    def al(f):
        return (f.get("marcador") or {}).get("alineado")

    def grupos(fs):
        con = [f for f in fs if f.get("marcador")]
        return {"alineado": _grupo_semaforo([f for f in con if al(f)]),
                "resto": _grupo_semaforo([f for f in con if not al(f)]),
                "sinMarcador": _grupo_semaforo([f for f in fs if not f.get("marcador")]),
                "verdeAlineado": _grupo_semaforo([f for f in con if al(f) and
                                                  (f.get("semaforo") or {}).get("estado") == "confirma"])}
    desde = _utc(MARCADOR_DESDE)
    nuevas = [f for f in cerradas if (_utc(f["pitazo"]) or desde) >= desde]
    todo, nuevo = grupos(cerradas), grupos(nuevas)
    return {"desde": MARCADOR_DESDE, "todo": todo, "nuevo": nuevo,
            "criterio": criterio_marcador(nuevo["alineado"], nuevo["resto"]),
            "nota": ("el marcador más probable del modelo de goles (el de la lista de Partidos), con la historia "
                     "anterior al partido: el mismo al minuto 0. Se juzga el win rate; la cuota es información")}


def en_el_medio(mercado_elegido: float | None) -> bool:
    return mercado_elegido is not None and MEDIO[0] <= float(mercado_elegido) < MEDIO[1]


def criterio_medio(puntas: dict, medio: dict) -> dict:
    """EL CRITERIO DEL MEDIO (fijado el 13/11/2026, no se mueve). Acá lo que se
    juzga SÍ es contra la cuota —la ventaja = acierto − lo que pedía—, porque
    el hallazgo es ese: dónde le sacamos algo a la casa. n = partidos NUEVOS
    cerrados del medio (el grupo chico, ~38 %):
      - n < 30: en observación.
      - en cualquier escalón: `no_se_sostiene` si la ventaja del medio es
        igual o mayor que la de las puntas.
      - escalón 30: `prometedor` si las puntas le sacan 5+ pts de ventaja al medio.
      - escalón 60: `confirmado` con 5+ pts y la plana de las puntas en
        positivo y por encima de la del medio; si no, `sin_contacto`."""
    n = medio["n"]
    escalon = max((e for e in MEDIO_ESCALONES if n >= e), default=0)
    proximo = next((e for e in MEDIO_ESCALONES if n < e), None)
    vp, vm = puntas["ventaja"], medio["ventaja"]
    sep = None if vp is None or vm is None else vp - vm
    rp, rm = puntas["roiPlano"], medio["roiPlano"]
    plata = rp is not None and rm is not None and rp > 0 and rp > rm
    if escalon == 0:
        estado = "en_observacion"
    elif sep is None or sep <= 0:
        estado = "no_se_sostiene"
    elif escalon < MEDIO_ESCALONES[-1]:
        estado = "prometedor" if sep >= MEDIO_SEPARACION - 1e-9 else "en_observacion"
    else:
        estado = "confirmado" if sep >= MEDIO_SEPARACION - 1e-9 and plata else "sin_contacto"
    pts = lambda x: f"{100 * x:+.1f} pts"  # noqa: E731
    cifras = (f"la ventaja sobre la cuota es {pts(vp)} en las puntas ({puntas['n']}, plana {100 * rp:+.1f} %) y "
              f"{pts(vm)} en el medio ({n}, plana {100 * rm:+.1f} %): {pts(sep)}" if sep is not None else "")
    sigue = f" · faltan {proximo - n} partidos del medio para el escalón {proximo}" if proximo else ""
    textos = {
        "confirmado": f"CONFIRMADO en el escalón {escalon}: {cifras}; la plata está en las puntas",
        "no_se_sostiene": f"NO SE SOSTIENE en el escalón {escalon}: " + (
            f"{cifras}; el medio no rinde menos que las puntas" if cifras else "sin partidos con que comparar"),
        "prometedor": f"PROMETEDOR en el escalón {escalon}: {cifras}{sigue}",
        "sin_contacto": f"sin contacto en el escalón {escalon}: {cifras}; pide {100 * MEDIO_SEPARACION:.0f}+ pts "
                        "y la plana de las puntas en positivo y sobre la del medio",
    }
    texto = textos.get(estado) or (f"en observación{f' (escalón {escalon})' if escalon else ''}: {n} partidos "
                                   "nuevos del medio" + (f", {cifras}" if cifras else "") + sigue)
    return {"escalon": escalon, "proximoEscalon": proximo, "escalones": list(MEDIO_ESCALONES),
            "faltan": (proximo - n) if proximo else 0, "n": n,
            "puntas": {"n": puntas["n"], "ventaja": vp, "roiPlano": rp},
            "medio": {"n": n, "ventaja": vm, "roiPlano": rm},
            "separacion": None if sep is None else round(sep, 4),
            "nMinimo": MEDIO_ESCALONES[-1], "separacionMinima": MEDIO_SEPARACION,
            "cumple": estado == "confirmado", "estado": estado, "texto": texto}


def resumen_medio(cerradas: list[dict]) -> dict:
    """Las puntas (baja: la casa le da < MEDIO[0]; alta: ≥ MEDIO[1]) contra el
    medio, en todo lo simulado y en lo NUEVO (desde `MEDIO_DESDE`)."""
    def pm(f):
        return f["mercado"][f["elegido"]]

    def grupos(fs):
        return {"puntaBaja": _grupo_semaforo([f for f in fs if pm(f) < MEDIO[0]]),
                "medio": _grupo_semaforo([f for f in fs if f.get("enElMedio")]),
                "puntaAlta": _grupo_semaforo([f for f in fs if pm(f) >= MEDIO[1]]),
                "puntas": _grupo_semaforo([f for f in fs if not f.get("enElMedio")])}
    desde = _utc(MEDIO_DESDE)
    nuevas = [f for f in cerradas if (_utc(f["pitazo"]) or desde) >= desde]
    todo, nuevo = grupos(cerradas), grupos(nuevas)
    return {"desde": MEDIO_DESDE, "medio": list(MEDIO), "todo": todo, "nuevo": nuevo,
            "criterio": criterio_medio(nuevo["puntas"], nuevo["medio"]),
            "nota": ("lo que la casa le da al elegido, sin margen. La ventaja es el acierto menos lo que pedía la "
                     "cuota: acá el criterio SÍ mira la cuota, porque el hallazgo es dónde le sacamos algo")}


def resumen_semaforo(cerradas: list[dict]) -> dict:
    """Verdes, amarillos, rojos y sin dato: el acierto del elegido (con lo que
    pedía la cuota y la plana a 1 u como información), en todo lo simulado y
    en lo NUEVO (desde `semaforo.DESDE`), que es lo único que cuenta para el
    criterio."""
    def est(f):
        return (f.get("semaforo") or {}).get("estado")

    def por_estado(fs):
        return {"verde": _grupo_semaforo([f for f in fs if est(f) == "confirma"]),
                "amarillo": _grupo_semaforo([f for f in fs if est(f) == "duda"]),
                "rojo": _grupo_semaforo([f for f in fs if est(f) == "noApostar"]),
                "sinDato": _grupo_semaforo([f for f in fs if est(f) not in ("confirma", "duda", "noApostar")])}
    desde = _utc(_sem.DESDE)
    nuevas = [f for f in cerradas if (_utc(f["pitazo"]) or desde) >= desde]
    todo, nuevo = por_estado(cerradas), por_estado(nuevas)
    criterio = criterio_semaforo(nuevo["verde"],
                                 _grupo_semaforo([f for f in nuevas if est(f) in ("duda", "noApostar")]))
    return {
        "desde": _sem.DESDE, "regla": _sem.REGLA,
        "todo": todo, "nuevo": nuevo,
        "criterio": criterio,
        "nota": ("verde = la espina del elegido lo acompaña y la del rival no dice que siga; amarillo = la espina "
                 "del elegido dice empate o la del rival dice que gana o empata; rojo = la espina del elegido dice "
                 "que pierde (no apostar). Sale de las espinas del parte, no de la cuota. Calculado, nunca "
                 "declarado, y fuera de la vista del analista (no va al recibo ni a un endpoint del token de "
                 "Cowork). El criterio cuenta solo los partidos desde el 13/11/2026"),
    }


def _utc(t) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(t).strip().replace("Z", "+00:00").replace(" ", "T"))
    except (TypeError, ValueError):
        return None
    return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)


def version_al(skill: str, momento: str) -> str:
    """La versión del skill que estaba en la cuenta en ese instante (UTC)."""
    t = _utc(momento)
    historial = sorted(CORTE_VERSION.get(skill, []), key=lambda vc: vc[1])
    if not historial or not t:
        return ""
    vigente = ""
    for v, corte in historial:
        inicio = _utc(SUBIDA_VERSION.get((skill, v)) or f"{corte} 00:00:00")
        if inicio and inicio <= t:
            vigente = v
    return vigente or f"anterior a {historial[0][0]}"


def kelly(p: float, cuota: float) -> float:
    """La fracción de Kelly para una apuesta simple: (p·c − 1)/(c − 1).
    Negativa = la cuota no paga lo que creemos."""
    if cuota <= 1:
        return 0.0
    return (p * cuota - 1) / (cuota - 1)


def _normalizar(probs: dict) -> dict | None:
    try:
        vals = {k: float(probs[k]) for k in CLAVES}
    except (KeyError, TypeError, ValueError):
        return None
    tot = sum(vals.values())
    if tot <= 0 or any(v < 0 for v in vals.values()):
        return None
    return {k: v / tot for k, v in vals.items()}


def _elegido(p: dict) -> str:
    return max(CLAVES, key=lambda k: p[k])


def _mejor_kelly(p: dict, cuotas: dict) -> tuple[str, float]:
    s = max(CLAVES, key=lambda k: kelly(p[k], cuotas[k]))
    return s, kelly(p[s], cuotas[s])


def _wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - m) / d, 4), round((c + m) / d, 4)]


def tras_fallos(secuencia: list[bool]) -> dict:
    """Con la secuencia de aciertos del elegido en orden de pitazo: cuánto se
    acierta en general y justo después de k fallos seguidos, y cómo va el
    criterio de contacto. Los simultáneos van por pitazo y fixture: el orden
    entre ellos no lo sabe nadie de antemano, y ninguno ve el resultado del otro."""
    n = len(secuencia)
    k_base = sum(1 for g in secuencia if g)
    base = {"n": n, "aciertos": k_base, "tasa": round(k_base / n, 4) if n else None,
            "intervalo": _wilson(k_base, n)}
    filas = []
    for k in TRAS_FALLOS_K:
        casos = [secuencia[i] for i in range(k, n) if not any(secuencia[i - k:i])]
        a = sum(1 for g in casos if g)
        filas.append({"k": k, "n": len(casos), "aciertos": a,
                      "tasa": round(a / len(casos), 4) if casos else None, "intervalo": _wilson(a, len(casos))})
    c = next(f for f in filas if f["k"] == CONTACTO_K)
    cumple = (c["n"] >= CONTACTO_N and c["tasa"] is not None and c["tasa"] >= CONTACTO_TASA
              and base["tasa"] is not None and c["intervalo"][0] > base["tasa"])
    if cumple:
        texto = (f"CONTACTO: tras {CONTACTO_K} fallos seguidos se acierta el {100 * c['tasa']:.1f} % en {c['n']} casos, "
                 f"con el intervalo entero sobre el promedio ({100 * base['tasa']:.1f} %): tomarlo en serio")
    elif c["n"] < CONTACTO_N:
        texto = (f"en observación: {c['n']} de {CONTACTO_N} casos tras {CONTACTO_K} fallos"
                 + (f", acierta el {100 * c['tasa']:.1f} % (pide {100 * CONTACTO_TASA:.0f} % y el intervalo sobre el "
                    f"promedio)" if c["tasa"] is not None else ""))
    else:
        texto = (f"sin contacto: con {c['n']} casos tras {CONTACTO_K} fallos se acierta el {100 * c['tasa']:.1f} %"
                 f" (pide {100 * CONTACTO_TASA:.0f} % y el intervalo sobre el promedio)")
    return {"base": base, "porK": filas,
            "contacto": {"k": CONTACTO_K, "nMinimo": CONTACTO_N, "tasaMinima": CONTACTO_TASA,
                         "n": c["n"], "tasa": c["tasa"], "intervalo": c["intervalo"],
                         "faltan": max(0, CONTACTO_N - c["n"]), "cumple": cumple,
                         "estado": "contacto" if cumple else ("en_observacion" if c["n"] < CONTACTO_N else "sin_contacto"),
                         "texto": texto}}


def freno_tramo(historia) -> dict:
    """El estado del freno de UN tramo con su historia [(acertó, 1/cuota), …]:
    cuánto acertó, cuánto pedía la cuota y si está en pausa."""
    n = len(historia)
    aciertos = sum(1 for g, _ in historia if g)
    pide = sum(x for _, x in historia) / n if n else None
    tasa = aciertos / n if n else None
    z = None
    if n and pide is not None and 0 < pide < 1:
        z = (tasa - pide) / math.sqrt(pide * (1 - pide) / n)
    pausado = n >= FRENO_MINIMO and z is not None and z < -FRENO_Z
    return {"n": n, "aciertos": aciertos, "tasa": round(tasa, 4) if tasa is not None else None,
            "pide": round(pide, 4) if pide is not None else None,
            "z": round(z, 2) if z is not None else None, "pausado": pausado}


def _apostar(e: dict, clave: str, fila: dict, t: datetime) -> None:
    """Arma la apuesta de una estrategia en el pitazo, con lo que ya se cobró."""
    libre = max(e["banca"] - e["comprometido"], 0.0)
    linea = None
    if clave == "metodoVerde" and (fila.get("semaforo") or {}).get("estado") != "confirma":
        estado = (fila.get("semaforo") or {}).get("estado") or "sinDato"
        fila["porEstrategia"][clave] = {
            "seleccion": None, "monto": 0.0, "ganancia": None, "banca": None, "linea": None,
            "motivo": {"duda": "semáforo en amarillo", "noApostar": "semáforo en rojo: no apostar"}.get(
                estado, "semáforo sin dato")}
        return
    if clave in _FUERA_MEDIO and fila.get("enElMedio"):
        fila["porEstrategia"][clave] = {
            "seleccion": None, "monto": 0.0, "ganancia": None, "banca": None, "linea": None,
            "motivo": (f"la casa le da {fila['mercado'][fila['elegido']]:.0f} % al elegido: en el medio "
                       f"({MEDIO[0]:g}-{MEDIO[1]:g} %)")}
        return
    if clave in _CON_FRENO:
        sel = fila["elegido"]
        tr = tramo_confianza(fila["probabilidades"][sel])
        f = freno_tramo(e["tramos"].setdefault(tr, deque(maxlen=FRENO_VENTANA)))
        if f["pausado"]:
            fila["porEstrategia"][clave] = {
                "seleccion": None, "monto": 0.0, "ganancia": None, "banca": None, "linea": None,
                "motivo": (f"tramo {tr} en pausa: acertó {f['aciertos']} de {f['n']} "
                           f"({100 * f['tasa']:.0f} %) y la cuota pedía {100 * f['pide']:.0f} %")}
            return
        # la banca de AHORA (lo cobrado), como Kelly
        previsto = PROPORCION * e["banca"]
    elif clave in _FRACCION_KELLY:
        sel = fila["kelly"]["seleccion"]
        # la banca de AHORA: lo cobrado; lo que está en juego no cuenta todavía
        previsto = _FRACCION_KELLY[clave] * fila["_f"] * e["banca"] if fila["_f"] > 0 else 0.0
    elif clave in _MARTINGALAS:
        sel = fila["elegido"]
        if clave in _SOLO_ALTA and fila["probabilidades"][sel] < CONFIANZA_ALTA:
            # bajo el 60 % no se apuesta ni se toca una línea
            fila["porEstrategia"][clave] = {"seleccion": None, "monto": 0.0, "ganancia": None, "banca": None,
                                            "linea": None, "motivo": f"bajo {CONFIANZA_ALTA:g} %"}
            return
        libres = [l for l in e["lineas"] if not l["ocupada"]]
        if libres:
            linea = min(libres, key=lambda l: (l["libreDesde"], l["id"]))
        else:
            linea = {"id": len(e["lineas"]) + 1, "proximo": UNIDAD, "libreDesde": t, "ocupada": False,
                     "perdida": 0.0}
            e["lineas"].append(linea)
        previsto = linea["proximo"]
        if clave in _AJUSTADAS:
            c = fila["cuotas"][sel]
            previsto = UNIDAD + (linea["perdida"] / (c - 1) if c > 1 else 0.0)
        if clave in _CON_TOPE:
            # la banca de AHORA (lo cobrado), como el método
            previsto = min(previsto, TOPE_MARTINGALA * e["banca"])
    elif clave == "plana60":
        sel = fila["elegido"]
        previsto = UNIDAD if fila["probabilidades"][sel] >= CONFIANZA_ALTA else 0.0
    else:
        sel = fila["elegido"]
        previsto = UNIDAD
    monto = round(max(min(previsto, libre), 0.0), 4)
    if monto <= 0:
        if previsto > 0:
            motivo = "sin plata libre"
        elif clave in _SOLO_ALTA:
            motivo = f"bajo {CONFIANZA_ALTA:g} %"
        elif clave in _CON_FRENO:
            motivo = "banca en cero"
        else:
            motivo = "sin ventaja"
        fila["porEstrategia"][clave] = {"seleccion": None, "monto": 0.0, "ganancia": None, "banca": None,
                                        "linea": None, "motivo": motivo}
        return
    e["comprometido"] += monto
    e["exposicion"] = max(e["exposicion"], e["comprometido"])
    e["montoMax"] = max(e["montoMax"], monto)
    if linea is not None:
        linea["ocupada"] = True
    fila["porEstrategia"][clave] = {"seleccion": sel, "monto": monto, "ganancia": None, "banca": None,
                                    "linea": linea["id"] if linea else None, "motivo": "",
                                    "_previsto": previsto}


def _cobrar(e: dict, clave: str, fila: dict, t: datetime) -> None:
    """Liquida la apuesta del partido (o solo anota la banca si no hubo)."""
    r = fila["porEstrategia"][clave]
    if r["monto"] > 0:
        gano = fila["resultado"] == r["seleccion"]
        ganancia = r["monto"] * (fila["cuotas"][r["seleccion"]] - 1) if gano else -r["monto"]
        e["banca"] += ganancia
        e["comprometido"] -= r["monto"]
        e["apostado"] += r["monto"]
        e["apuestas"] += 1
        e["ganadas"] += 1 if gano else 0
        if r["linea"]:
            l = e["lineas"][r["linea"] - 1]
            if clave in _AJUSTADAS:
                # lo perdido en la línea: un acierto lo descuenta (entero si la apuesta no se recortó)
                l["perdida"] = max(0.0, l["perdida"] - ganancia) if gano else l["perdida"] + r["monto"]
                l.update(ocupada=False, libreDesde=t, proximo=UNIDAD)
            else:
                # una derrota duplica lo que la línea IBA a apostar, aunque la plata libre lo haya recortado
                l.update(ocupada=False, libreDesde=t, proximo=UNIDAD if gano else r["_previsto"] * 2)
        r["ganancia"] = round(ganancia, 4)
        e["pico"] = max(e["pico"], e["banca"])
        if e["pico"] > 0:
            e["caida"] = max(e["caida"], (e["pico"] - e["banca"]) / e["pico"])
        if e["banca"] < 0.01 and e["quebro"] is None:
            e["quebro"] = fila["fixtureId"]
    else:
        r["ganancia"] = 0.0
    if clave in _CON_FRENO:
        # el freno anota TODO partido cerrado del tramo, se haya apostado o no
        sel = fila["elegido"]
        e["tramos"].setdefault(tramo_confianza(fila["probabilidades"][sel]), deque(maxlen=FRENO_VENTANA)).append(
            (fila["resultado"] == sel, 1 / fila["cuotas"][sel]))
    r["banca"] = round(e["banca"], 2)
    e["serie"].append({"fixtureId": fila["fixtureId"], "pitazo": fila["pitazo"], "banca": round(e["banca"], 2)})


def simular(apuestas: list[dict]) -> dict:
    """El corazón, sin base: recibe las apuestas ya armadas
    ({fixtureId, pitazo, probabilidades (en %), cuotas, resultado | None, …})
    y las corre en una línea de tiempo: se apuesta en el pitazo y se cobra
    `DURACION` después. A la misma hora, primero se cobra y después se
    apuesta (la línea que se libera a las 17:00 sirve al partido de las
    17:00). Las abiertas se apuestan pero no se cobran: dicen el monto."""
    orden = sorted(apuestas, key=lambda x: (x["pitazo"], x["fixtureId"]))
    filas, eventos = [], []
    for i, a in enumerate(orden):
        p = _normalizar(a["probabilidades"])
        sel_k, f = _mejor_kelly(p, a["cuotas"])
        # sin semáforo armado por quien llama (una apuesta de prueba), sin dato
        sem = a.get("semaforo") or _sem.semaforo(a["probabilidades"], None)
        # el mercado sin margen: de quien llama o, si no vino, de las cuotas
        mer = a.get("mercado")
        if not mer:
            inv = {k: 1 / a["cuotas"][k] for k in CLAVES}
            mer = {k: round(100 * inv[k] / sum(inv.values()), 1) for k in CLAVES}
        filas.append({**a, "semaforo": sem, "probabilidades": {k: round(100 * p[k], 1) for k in CLAVES},
                      "mercado": mer, "enElMedio": en_el_medio(mer[_elegido(p)]),
                      "elegido": _elegido(p), "_f": f,
                      "kelly": {"seleccion": sel_k, "fraccion": round(f, 4),
                                "valor": round(p[sel_k] * a["cuotas"][sel_k] - 1, 4)},
                      "estado": "cerrada" if a.get("resultado") else "pendiente", "porEstrategia": {}})
        t0 = _utc(a["pitazo"])
        eventos.append((t0, 1, i))                       # 1 = apostar
        if a.get("resultado"):
            eventos.append((t0 + DURACION, 0, i))        # 0 = cobrar (va antes a la misma hora)
    eventos.sort(key=lambda e: (e[0], e[1], e[2]))

    estado = {c: {"banca": BANCA_INICIAL, "comprometido": 0.0, "pico": BANCA_INICIAL, "caida": 0.0,
                  "apostado": 0.0, "apuestas": 0, "ganadas": 0, "quebro": None,
                  "exposicion": 0.0, "montoMax": 0.0, "lineas": [], "tramos": {},
                  "serie": [{"fixtureId": None, "pitazo": None, "banca": BANCA_INICIAL}]}
              for c, _, _ in ESTRATEGIAS}

    for t, tipo, i in eventos:
        fila = filas[i]
        for clave, _, _ in ESTRATEGIAS:
            e = estado[clave]
            if tipo == 1:
                _apostar(e, clave, fila, t)
            else:
                _cobrar(e, clave, fila, t)

    for f in filas:
        f.pop("_f", None)
        for r in f["porEstrategia"].values():
            r.pop("_previsto", None)

    estrategias = []
    for clave, nombre, desc in ESTRATEGIAS:
        e = estado[clave]
        estrategias.append({
            "clave": clave, "nombre": nombre, "descripcion": desc,
            "banca": round(e["banca"], 2), "ganancia": round(e["banca"] - BANCA_INICIAL, 2),
            "apostado": round(e["apostado"], 2), "apuestas": e["apuestas"], "ganadas": e["ganadas"],
            "roi": round((e["banca"] - BANCA_INICIAL) / e["apostado"], 4) if e["apostado"] else None,
            "caidaMaxima": round(e["caida"], 4), "quebro": e["quebro"],
            # lo más que estuvo en juego a la vez y la apuesta más grande
            "exposicionMaxima": round(e["exposicion"], 2), "montoMaximo": round(e["montoMax"], 2),
            "lineas": (({"abiertas": len(e["lineas"]),
                         "perdiendo": sum(1 for l in e["lineas"] if l.get("perdida", 0) > 0.005),
                         "proximoMayor": UNIDAD,
                         # la ajustada no tiene un «próximo» fijo (depende de la cuota): lo que lleva perdido
                         "perdidaMayor": round(max((l.get("perdida", 0) for l in e["lineas"]), default=0.0), 2)}
                        if clave in _AJUSTADAS else
                        {"abiertas": len(e["lineas"]),
                         "perdiendo": sum(1 for l in e["lineas"] if l["proximo"] > UNIDAD),
                         "proximoMayor": round(max((l["proximo"] for l in e["lineas"]), default=UNIDAD), 2)})
                       if clave in _MARTINGALAS else None),
            # solo el método: cómo está hoy el freno de cada tramo
            "tramos": ([{"tramo": tr, **freno_tramo(e["tramos"].get(tr, ()))} for tr, _, _ in TRAMOS_CONFIANZA]
                       if clave in _CON_FRENO else None),
            "serie": e["serie"],
        })

    # por versión de sad-analysis (la del 1X2): cuánto ganó cada estrategia con cada una
    por_version: dict[str, dict] = {}
    for f in filas:
        if f["estado"] != "cerrada":
            continue
        v = (f.get("versiones") or {}).get("sad-analysis") or "sin versión"
        pv = por_version.setdefault(v, {"version": v, "partidos": 0, "aciertos": 0, "estrategias": {}})
        pv["partidos"] += 1
        pv["aciertos"] += 1 if f["resultado"] == f["elegido"] else 0
        for clave, r in f["porEstrategia"].items():
            ev = pv["estrategias"].setdefault(clave, {"apostado": 0.0, "ganancia": 0.0, "apuestas": 0})
            if r["monto"] > 0:
                ev["apostado"] = round(ev["apostado"] + r["monto"], 4)
                ev["ganancia"] = round(ev["ganancia"] + (r["ganancia"] or 0), 4)
                ev["apuestas"] += 1
    for pv in por_version.values():
        for ev in pv["estrategias"].values():
            ev["roi"] = round(ev["ganancia"] / ev["apostado"], 4) if ev["apostado"] else None

    cerradas = [f for f in filas if f["estado"] == "cerrada"]
    return {
        # el criterio de contacto: acierto del elegido justo después de k fallos seguidos
        "trasFallos": tras_fallos([f["resultado"] == f["elegido"] for f in cerradas]),
        "desde": DESDE, "bancaInicial": BANCA_INICIAL, "unidad": UNIDAD,
        "cerradas": len(cerradas), "pendientes": len(filas) - len(cerradas),
        "aciertos": sum(1 for f in cerradas if f["resultado"] == f["elegido"]),
        "estrategias": estrategias,
        "porVersion": sorted(por_version.values(), key=lambda x: x["version"]),
        # en quién desconfiar (10/11/2026): con alerta contra sin alerta, y el descarte
        "alertaConfianza": resumen_alerta(cerradas),
        # el semáforo del elegido (11/11/2026): verdes contra amarillos y su criterio fijo
        "semaforo": resumen_semaforo(cerradas),
        # el marcador más probable con el elegido (13/11/2026): alineados contra el resto y su criterio
        "marcador": resumen_marcador(cerradas),
        # las puntas contra el medio de lo que la casa le da al elegido (13/11/2026)
        "medio": resumen_medio(cerradas),
        # lo más nuevo arriba en la pantalla
        "apuestas": list(reversed(filas)),
    }


# LA SIMULACIÓN SE REHACE SOLO SI CAMBIÓ ALGO QUE ENTRA (10/11/2026, usuario:
# «Simulación es bien lenta»). Se sigue recalculando al leer —un partido que
# termina mueve las bancas siguientes—, pero antes se mira la HUELLA de todo lo
# que la decide: de cada parte desde el 28/10, lo único que la simulación lee
# (si el JSON es válido, el 1X2, la versión, el depósito previo y la
# cuarentena); de cada partido su fila (fecha, estado, goles, liga) con el
# nombre de la liga (las copas quedan fuera por nombre), y sus cuotas (filas,
# última y suma). Si la huella es la misma, la salida también: se devuelve la
# misma. `SAD_CACHE_SIMULACION_S` es la red de seguridad (una hora; 0 apaga).
SIMULACION_TTL_S = float(__import__("os").environ.get("SAD_CACHE_SIMULACION_S", "3600") or "0")
_SIM_CACHE: dict[str, tuple] = {}


def huella_simulacion() -> tuple:
    from backend.analisis.parte import _conectar
    with _conectar() as con:
        partes = con.execute(
            "SELECT fixture_id, version, creado_en, deposito_previo_en, cuarentena_json, json_valid(parte_json) AS ok, "
            "CASE WHEN json_valid(parte_json) THEN json_extract(parte_json, '$.pronostico.probabilidades') END AS probs, "
            "CASE WHEN json_valid(parte_json) THEN json_extract(parte_json, '$.version') END AS vparte, "
            "CASE WHEN json_valid(parte_json) THEN json_extract(parte_json, '$.pronostico.marcador') END AS marcador, "
            # el semáforo sale de las espinas (13/11/2026): una espina re-declarada cambia la huella
            "CASE WHEN json_valid(parte_json) THEN json_extract(parte_json, '$.lecturaSad.espina') END AS espinas "
            "FROM parte_cowork WHERE fecha >= ? ORDER BY fixture_id", (DESDE[:10],)).fetchall()
    ids = [f["fixture_id"] for f in partes]
    fx, cu = (), ()
    if ids:
        marcas = ",".join("?" * len(ids))
        fx = tuple(tuple(r) for r in saddb.query(
            "sad", f"SELECT f.*, l.name AS liga_nombre FROM fixtures f LEFT JOIN leagues l ON l.id=f.league_id "
                   f"WHERE f.id IN ({marcas}) ORDER BY f.id", tuple(ids)))
        try:
            cu = tuple(saddb.query_one(
                "sad", f"SELECT COUNT(*), MAX(id), TOTAL(odd), TOTAL(LENGTH(bet_name) + LENGTH(value)) FROM odds "
                       f"WHERE fixture_id IN ({marcas})", tuple(ids)))
        except Exception:  # noqa: BLE001 — sin la tabla de cuotas la simulación tampoco las lee: la huella lo dice
            cu = ("sin cuotas",)
    return (tuple(tuple(f) for f in partes), fx, cu)


def simulacion(pagina: int | None = None, por_pagina: int | None = None) -> dict:
    """Arma las apuestas desde los partes y la base y las simula (con caché por
    huella). Con `por_pagina`, la lista de apuestas viene paginada (la más nueva
    primero) y la gráfica sale de `linea` + `estrategias[].serie`: la cuenta es
    la misma, solo se manda menos (13/11/2026, usuario: «esa página demora mucho
    en cargarse, se cargan muchos partidos… poner # de páginas»)."""
    import time as _t
    if SIMULACION_TTL_S <= 0:
        out = _simulacion()
    else:
        huella = huella_simulacion()
        hit = _SIM_CACHE.get("v")
        if hit and hit[0] == huella and _t.monotonic() - hit[1] < SIMULACION_TTL_S:
            out = hit[2]
        else:
            out = _simulacion()
            _SIM_CACHE["v"] = (huella, _t.monotonic(), out)
    return paginar(out, pagina, por_pagina) if por_pagina else out


def paginar(out: dict, pagina: int | None, por_pagina: int) -> dict:
    """Una página de `apuestas` (sin tocar la salida en caché) más `linea`: lo
    mínimo de cada partido cerrado, en el orden de `estrategias[].serie`, para
    la gráfica y su tooltip sin mandar las ~400 apuestas con sus 13 series."""
    todas = out["apuestas"]
    por_pagina = max(1, int(por_pagina))
    paginas = max(1, math.ceil(len(todas) / por_pagina))
    pagina = min(max(1, int(pagina or 1)), paginas)
    cerradas = [a for a in reversed(todas) if a["estado"] == "cerrada"]
    return {**out, "apuestas": todas[(pagina - 1) * por_pagina: pagina * por_pagina],
            "paginacion": {"pagina": pagina, "porPagina": por_pagina, "total": len(todas), "paginas": paginas},
            "linea": [{"fixtureId": a["fixtureId"], "pitazo": a["pitazo"], "local": a["partido"]["local"],
                       "visita": a["partido"]["visita"], "resultado": a["resultado"],
                       "sad": (a.get("versiones") or {}).get("sad-analysis") or ""} for a in cerradas]}


# EL MARCADOR MÁS PROBABLE de cada partido (13/11/2026): el del modelo de
# goles con la historia ANTERIOR al pitazo, así que al minuto 0 es el mismo que
# en cualquier lectura. Se calcula una vez por proceso y por partido.
_MARCADOR: dict[int, dict | None] = {}


def marcador_de(fx, elegido: str) -> dict | None:
    """{masProbable, prob, signo, alineado} o None sin modelo o sin historia."""
    if not fx:
        return None
    if fx["id"] not in _MARCADOR:
        try:
            from backend.analisis import goles
            # sin la marca de la ventana (`goles._ventana`): no cambia el marcador y cuesta
            g = goles._acotar_fixture(dict(fx))
            mp = (g.get("masProbables") or [None])[0] if not g.get("sinDato") else None
            _MARCADOR[fx["id"]] = {"masProbable": mp["marcador"], "prob": mp["prob"]} if mp else None
        except Exception:  # noqa: BLE001 — sin goles acotados la apuesta va «sin marcador»: las series del marcador no apuestan
            _MARCADOR[fx["id"]] = None
    m = _MARCADOR[fx["id"]]
    if not m:
        return None
    signo = _sem.signo_marcador(m["masProbable"])
    return {**m, "signo": signo, "alineado": signo == elegido}


# la burbuja del elegido «al día del partido» no cambia una vez fijada: se
# calcula UNA vez por proceso y por partido (la simulación se lee seguido)
_BURBUJA_ELEGIDO: dict[tuple, dict | None] = {}


def _burbuja_elegido(fx, elegido: str) -> dict | None:
    """{signo, partidos, riesgo} de la familia total del elegido, con la misma
    cuenta que el parte (`parte._reventon_calculado`). None con empate o sin dato."""
    lado = {"local": "a", "visita": "b"}.get(elegido)
    if not lado or not fx:
        return None
    clave = (fx["id"], lado)
    if clave not in _BURBUJA_ELEGIDO:
        try:
            from backend.analisis.parte import _reventon_calculado
            r = (_reventon_calculado(dict(fx)) or {}).get(lado) or {}
            act = r.get("actual") or {}
            _BURBUJA_ELEGIDO[clave] = {"signo": act.get("signo"), "partidos": act.get("partidos"),
                                       "riesgo": (r.get("riesgo") or {}).get("nivel")} if act else None
        except Exception:  # noqa: BLE001 — sin la burbuja la alerta mira solo la casa; no tumba la simulación
            _BURBUJA_ELEGIDO[clave] = None
    return _BURBUJA_ELEGIDO[clave]


def _simulacion() -> dict:
    """Arma las apuestas desde los partes y la base y las simula."""
    from backend.analisis.parte import _conectar
    with _conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, parte_json, version, creado_en, deposito_previo_en, cuarentena_json "
            "FROM parte_cowork WHERE fecha >= ?", (DESDE[:10],)).fetchall()
    ids = [f["fixture_id"] for f in filas]
    fx = {}
    if ids:
        for r in saddb.query(
                "sad",
                "SELECT f.id, f.date, f.status_short, f.home_team_id, f.away_team_id, f.league_id, "
                "ht.name AS home_name, at.name AS away_name, "
                "l.name AS liga FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
                "JOIN teams at ON at.id=f.away_team_id LEFT JOIN leagues l ON l.id=f.league_id "
                f"WHERE f.id IN ({','.join('?' * len(ids))})", tuple(ids)):
            fx[r["id"]] = r
    reales = _vered.resultados(ids)
    mercados = cuotas_mercado(ids)
    copas = copas_nacionales(ids)
    desde = _utc(DESDE)
    apuestas, excluidos = [], []
    for f in filas:
        fid = f["fixture_id"]
        r = fx.get(fid)
        pitazo = _utc(r["date"]) if r else None
        if not r or not pitazo or pitazo < desde:
            continue
        partido = {"local": r["home_name"], "visita": r["away_name"], "liga": r["liga"] or ""}

        def fuera(motivo: str):
            excluidos.append({"fixtureId": fid, "pitazo": pitazo.strftime("%Y-%m-%d %H:%M:%S"),
                              "partido": partido, "motivo": motivo})

        if (r["status_short"] or "") in ("PST", "CANC", "ABD"):
            fuera("partido aplazado, cancelado o suspendido")
            continue
        if not f["deposito_previo_en"]:
            fuera("el parte no se depositó antes del pitazo")
            continue
        if f["cuarentena_json"]:
            fuera("en cuarentena: fuera de toda métrica")
            continue
        if fid in copas:
            # COPA NACIONAL, FUERA (29/10/2026, usuario: «no hay que contaminar
            # las tablas»): el favorito al 90 % contra uno de quinta a cuota 1.02
            fuera(f"copa nacional ({copas[fid]}): se analiza, pero no entra a las tablas")
            continue
        try:
            parte = json.loads(f["parte_json"])
        except (TypeError, ValueError):
            fuera("el parte guardado no se puede leer")
            continue
        probs = (parte.get("pronostico") or {}).get("probabilidades") or {}
        if not _normalizar(probs):
            fuera("el pronóstico no trae el 1X2 completo")
            continue
        m = mercados.get(fid)
        if not m:
            fuera("sin las tres cuotas del 1X2 capturadas")
            continue
        momento = f["deposito_previo_en"]
        mercado_pct = {k: round(m["prob"][k], 1) for k in CLAVES}
        alerta = None
        if pitazo >= _utc(ALERTA_DESDE):
            alerta = alerta_confianza(probs, mercado_pct, _burbuja_elegido(r, _elegido(_normalizar(probs))))
        apuestas.append({
            "fixtureId": fid, "pitazo": pitazo.strftime("%Y-%m-%d %H:%M:%S"), "partido": partido,
            "depositadoEn": momento,
            "versiones": {s: version_al(s, momento) for s in SKILLS},
            "versionPrompt": f["version"] or parte.get("version") or "",
            "probabilidades": probs,
            "cuotas": {k: round(m["cuota"][k], 3) for k in CLAVES},
            "mercado": mercado_pct,
            "resultado": reales.get(fid),
            "alerta": alerta,
            # el marcador más probable del modelo de goles contra el elegido (13/11/2026)
            "marcador": marcador_de(r, _elegido(_normalizar(probs))),
            # el semáforo del elegido con el mercado SIN redondear (11/11/2026)
            "semaforo": _sem.del_parte(parte, m["prob"]),
        })
    out = simular(apuestas)
    out["excluidos"] = sorted(excluidos, key=lambda x: x["pitazo"], reverse=True)
    out["nota"] = ("simulación sobre los 1X2 declarados en los partes, desde los partidos del 28/10/2026 "
                   "(hora de Lima); cuota = media de las casas en la última captura prepartido, con su margen; "
                   "se apuesta en el pitazo y se cobra dos horas después: los simultáneos se apuestan con la banca "
                   "de antes y ninguna apuesta pasa de la plata libre. No es una recomendación de apuesta")
    return out
