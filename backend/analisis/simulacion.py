"""SIMULACIÓN DE APUESTA (28/10/2026, pedido del usuario).

Qué habría pasado con una banca si se hubiera apostado con nuestros 1X2
declarados, con tres estrategias puestas lado a lado:

- **plana** (control): 1 unidad a nuestro elegido —el resultado con más
  probabilidad del pronóstico— en cada partido, a la cuota media de las casas.
- **kelly**: el criterio de Kelly sobre NUESTRAS probabilidades. Por partido,
  la selección con la fracción f* = (p·c − 1)/(c − 1) más alta. Con f* ≤ 0 no
  se apuesta: la cuota no paga lo que creemos. Se apuesta f*·banca, entero
  (`kelly`), a la mitad (`kellyMedio`) y a un cuarto (`kellyCuarto`).
- **martingala**: a nuestro elegido, 1 unidad que se DUPLICA tras cada
  derrota y vuelve a 1 tras una victoria; si la banca no alcanza, se apuesta
  lo que queda (y una derrota la quiebra).

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

Esto NO es una recomendación de apuesta. La cuota es la media de las casas
en la última captura prepartido y trae su margen; los partidos que arrancan
a la misma hora se liquidan uno detrás del otro por orden de pitazo, cosa que
en la vida real no se puede (la martingala no sabe el resultado del otro).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from backend import db as saddb
from backend.analisis import veredicto as _vered
from backend.analisis.lecciones import CORTE_VERSION, cuotas_mercado

# 00:00 de Lima (UTC−5) del 28/10/2026: «recién desde los partidos de hoy»
DESDE = "2026-10-28 05:00:00"
BANCA_INICIAL = 100.0
UNIDAD = 1.0
CLAVES = ("local", "empate", "visita")
SKILLS = ("sad-analysis", "efe-clasificador", "teorema-del-echado", "diagnostico-tactico")

# Hora (UTC) en que la versión llegó a la cuenta del usuario, cuando se sabe.
# Sin entrada, la versión rige desde las 00:00 UTC del día de su corte.
SUBIDA_VERSION = {
    # el usuario confirmó la subida de los zips el 28/10 hacia las 06:50 de Lima:
    # el tramo de las 04:47 todavía corrió con EFE v1.7 y sad v4.1
    ("efe-clasificador", "v1.8"): "2026-10-28 11:50:00",
    ("sad-analysis", "v4.2"): "2026-10-28 11:50:00",
}

ESTRATEGIAS = (
    ("plana", "Apuesta plana (control)",
     f"{UNIDAD:g} unidad a nuestro elegido en cada partido"),
    ("kelly", "Kelly completo",
     "f* = (p·c − 1)/(c − 1) de la banca a la selección con más ventaja; sin ventaja no apuesta"),
    ("kellyMedio", "Kelly ½", "la mitad de la fracción de Kelly"),
    ("kellyCuarto", "Kelly ¼", "un cuarto de la fracción de Kelly"),
    ("martingala", "Martingala",
     f"{UNIDAD:g} unidad a nuestro elegido, se duplica tras cada derrota y vuelve a {UNIDAD:g} al ganar"),
)
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


def simular(apuestas: list[dict]) -> dict:
    """El corazón, sin base: recibe las apuestas ya armadas
    ({fixtureId, pitazo, probabilidades (en %), cuotas, resultado | None, …})
    y devuelve las bancas. Las cerradas se liquidan en orden de pitazo; las
    abiertas solo dicen qué se apostaría con la banca de hoy."""
    estado = {c: {"banca": BANCA_INICIAL, "pico": BANCA_INICIAL, "caida": 0.0, "apostado": 0.0,
                  "apuestas": 0, "ganadas": 0, "quebro": None, "racha": 0,
                  "serie": [{"fixtureId": None, "pitazo": None, "banca": BANCA_INICIAL}]}
              for c, _, _ in ESTRATEGIAS}
    filas = []
    for a in sorted(apuestas, key=lambda x: (x["pitazo"], x["fixtureId"])):
        p = _normalizar(a["probabilidades"])
        cuotas = a["cuotas"]
        elegido = _elegido(p)
        sel_k, f = _mejor_kelly(p, cuotas)
        real = a.get("resultado")
        fila = {**a, "elegido": elegido,
                "kelly": {"seleccion": sel_k, "fraccion": round(f, 4),
                          "valor": round(p[sel_k] * cuotas[sel_k] - 1, 4)},
                "estado": "cerrada" if real else "pendiente", "porEstrategia": {}}
        for clave, _, _ in ESTRATEGIAS:
            e = estado[clave]
            if clave in _FRACCION_KELLY:
                sel = sel_k
                monto = _FRACCION_KELLY[clave] * f * e["banca"] if f > 0 else 0.0
            elif clave == "martingala":
                sel = elegido
                monto = min(UNIDAD * 2 ** e["racha"], e["banca"])
            else:
                sel = elegido
                monto = min(UNIDAD, e["banca"])
            monto = round(max(monto, 0.0), 4)
            if not real:
                fila["porEstrategia"][clave] = {"seleccion": sel if monto > 0 else None,
                                                "monto": monto, "ganancia": None, "banca": None}
                continue
            if monto <= 0:
                fila["porEstrategia"][clave] = {"seleccion": None, "monto": 0.0, "ganancia": 0.0,
                                                "banca": round(e["banca"], 2)}
                continue
            gano = real == sel
            ganancia = monto * (cuotas[sel] - 1) if gano else -monto
            e["banca"] += ganancia
            e["apostado"] += monto
            e["apuestas"] += 1
            e["ganadas"] += 1 if gano else 0
            if clave == "martingala":
                e["racha"] = 0 if gano else e["racha"] + 1
            e["pico"] = max(e["pico"], e["banca"])
            if e["pico"] > 0:
                e["caida"] = max(e["caida"], (e["pico"] - e["banca"]) / e["pico"])
            if e["banca"] < 0.01 and e["quebro"] is None:
                e["quebro"] = a["fixtureId"]
            e["serie"].append({"fixtureId": a["fixtureId"], "pitazo": a["pitazo"], "banca": round(e["banca"], 2)})
            fila["porEstrategia"][clave] = {"seleccion": sel, "monto": monto, "ganancia": round(ganancia, 4),
                                            "banca": round(e["banca"], 2)}
        fila["probabilidades"] = {k: round(100 * p[k], 1) for k in CLAVES}
        filas.append(fila)

    estrategias = []
    for clave, nombre, desc in ESTRATEGIAS:
        e = estado[clave]
        estrategias.append({
            "clave": clave, "nombre": nombre, "descripcion": desc,
            "banca": round(e["banca"], 2), "ganancia": round(e["banca"] - BANCA_INICIAL, 2),
            "apostado": round(e["apostado"], 2), "apuestas": e["apuestas"], "ganadas": e["ganadas"],
            "roi": round((e["banca"] - BANCA_INICIAL) / e["apostado"], 4) if e["apostado"] else None,
            "caidaMaxima": round(e["caida"], 4), "quebro": e["quebro"],
            "rachaPerdidas": e["racha"] if clave == "martingala" else None,
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
        "desde": DESDE, "bancaInicial": BANCA_INICIAL, "unidad": UNIDAD,
        "cerradas": len(cerradas), "pendientes": len(filas) - len(cerradas),
        "aciertos": sum(1 for f in cerradas if f["resultado"] == f["elegido"]),
        "estrategias": estrategias,
        "porVersion": sorted(por_version.values(), key=lambda x: x["version"]),
        # lo más nuevo arriba en la pantalla
        "apuestas": list(reversed(filas)),
    }


def simulacion() -> dict:
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
                   "los partidos se liquidan en orden de pitazo (los simultáneos, uno tras otro). No es una "
                   "recomendación de apuesta")
    return out
