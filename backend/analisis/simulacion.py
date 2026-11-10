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
from backend.analisis import veredicto as _vered
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
}

ESTRATEGIAS = (
    ("proporcional", "Proporcional con freno",
     f"{100 * PROPORCION:g} % de la banca a nuestro elegido; un tramo de confianza se pausa si en sus últimos "
     f"{FRENO_VENTANA} partidos acertó menos de lo que pedía la cuota, y vuelve cuando se recupera"),
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
)
_MARTINGALAS = ("martingala", "martingala60")
_SOLO_ALTA = ("plana60", "martingala60")
_FRACCION_KELLY = {"kelly": 1.0, "kellyMedio": 0.5, "kellyCuarto": 0.25}


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
    if clave == "proporcional":
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
            linea = {"id": len(e["lineas"]) + 1, "proximo": UNIDAD, "libreDesde": t, "ocupada": False}
            e["lineas"].append(linea)
        previsto = linea["proximo"]
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
        elif clave == "proporcional":
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
    if clave == "proporcional":
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
        filas.append({**a, "probabilidades": {k: round(100 * p[k], 1) for k in CLAVES},
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
            "lineas": ({"abiertas": len(e["lineas"]),
                        "perdiendo": sum(1 for l in e["lineas"] if l["proximo"] > UNIDAD),
                        "proximoMayor": round(max((l["proximo"] for l in e["lineas"]), default=UNIDAD), 2)}
                       if clave in _MARTINGALAS else None),
            # solo el método: cómo está hoy el freno de cada tramo
            "tramos": ([{"tramo": tr, **freno_tramo(e["tramos"].get(tr, ()))} for tr, _, _ in TRAMOS_CONFIANZA]
                       if clave == "proporcional" else None),
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
            "CASE WHEN json_valid(parte_json) THEN json_extract(parte_json, '$.version') END AS vparte "
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


def simulacion() -> dict:
    """Arma las apuestas desde los partes y la base y las simula (con caché por huella)."""
    import time as _t
    if SIMULACION_TTL_S <= 0:
        return _simulacion()
    huella = huella_simulacion()
    hit = _SIM_CACHE.get("v")
    if hit and hit[0] == huella and _t.monotonic() - hit[1] < SIMULACION_TTL_S:
        return hit[2]
    out = _simulacion()
    _SIM_CACHE["v"] = (huella, _t.monotonic(), out)
    return out


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
                "SELECT f.id, f.date, f.status_short, ht.name AS home_name, at.name AS away_name, "
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
        apuestas.append({
            "fixtureId": fid, "pitazo": pitazo.strftime("%Y-%m-%d %H:%M:%S"), "partido": partido,
            "depositadoEn": momento,
            "versiones": {s: version_al(s, momento) for s in SKILLS},
            "versionPrompt": f["version"] or parte.get("version") or "",
            "probabilidades": probs,
            "cuotas": {k: round(m["cuota"][k], 3) for k in CLAVES},
            "mercado": {k: round(m["prob"][k], 1) for k in CLAVES},
            "resultado": reales.get(fid),
        })
    out = simular(apuestas)
    out["excluidos"] = sorted(excluidos, key=lambda x: x["pitazo"], reverse=True)
    out["nota"] = ("simulación sobre los 1X2 declarados en los partes, desde los partidos del 28/10/2026 "
                   "(hora de Lima); cuota = media de las casas en la última captura prepartido, con su margen; "
                   "se apuesta en el pitazo y se cobra dos horas después: los simultáneos se apuestan con la banca "
                   "de antes y ninguna apuesta pasa de la plata libre. No es una recomendación de apuesta")
    return out
