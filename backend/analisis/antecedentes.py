"""Fase A del bucle de aprendizaje: los ANTECEDENTES (docs/APRENDIZAJE.md § A).

Cowork analizaba cada partido desde cero, sin recordar que dos fechas atrás
dijo algo de ese mismo equipo y cómo salió. Esto le devuelve, por equipo, lo
que el sistema ya dijo en partidos ANTERIORES y cómo terminó: la clasificación
del EFE, el pronóstico de la cadena, el 1X2, la ventana del TDE, la clase del
bloque del DTP, el marcador, el veredicto y la lección; más el acierto a
ciegas del equipo y las lecciones que siguen abiertas.

La regla que lo hace utilizable sin romper nada: **solo partidos ANTERIORES al
que se analiza** (fecha estrictamente menor y otro fixture). El caso nuevo
sigue siendo `ciega`: lo que se lee son desenlaces de otros partidos, nunca el
de este. Y un antecedente en cuarentena viaja marcado: su insumo estaba roto y
no se cita como precedente.
"""
from __future__ import annotations

import json

from backend import db as saddb
from backend.analisis import db as efedb

LADOS = ("a", "b")
N_DEFECTO = 5


def _fixture(fixture_id: int):
    return saddb.query_one(
        "sad",
        "SELECT f.id, f.date, f.home_team_id, f.away_team_id, ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        "WHERE f.id=?", (fixture_id,))


def _fixtures_de(ids: list[int]) -> dict[int, dict]:
    if not ids:
        return {}
    marcas = ",".join("?" * len(ids))
    filas = saddb.query(
        "sad",
        f"SELECT id, date, home_team_id, away_team_id, status_short, "
        f"COALESCE(fulltime_home, goals_home) AS gh, COALESCE(fulltime_away, goals_away) AS ga "
        f"FROM fixtures WHERE id IN ({marcas})", tuple(ids))
    return {f["id"]: dict(f) for f in filas}


def _resumen_parte(fila, fx: dict, lado: str, cuarentenas: dict) -> dict:
    """Lo que se dijo de ESTE equipo en ESE parte y cómo salió."""
    from backend.analisis.parte import _totales, bloques_tde
    parte = json.loads(fila["parte_json"])
    ver = json.loads(fila["veredicto_json"]) if fila["veredicto_json"] else None
    rival_lado = "b" if lado == "a" else "a"
    eq = (parte.get("equipos") or {}).get(lado) or {}
    try:
        tot = _totales(eq) if eq.get("bloques") else {}
    except (KeyError, TypeError):
        tot = {}
    pron = parte.get("pronostico") or {}
    tde = next((b for b in bloques_tde(parte.get("tde") or {}) if b.get("equipo") == lado), None)
    dtp = next((b for b in ((parte.get("dtp") or {}).get("bloques") or []) if b.get("equipo") == rival_lado), None)
    clase_bloque = ""
    if dtp:
        from backend.analisis.dtp_cowork import clasificar_bloque
        clase_bloque = clasificar_bloque(dtp["apertura"]["m2"]["checklistBloqueRival"])["clase"]
    gf, gc = (fx["gh"], fx["ga"]) if lado == "a" else (fx["ga"], fx["gh"])
    lv = ((ver or {}).get("porLado") or {}).get(lado) or {}
    cuar = cuarentenas.get(fila["fixture_id"])
    return {
        "fixtureId": fila["fixture_id"],
        "fecha": (fila["fecha"] or "")[:10],
        "rival": fila["equipo_b"] if lado == "a" else fila["equipo_a"],
        "condicion": "L" if lado == "a" else "V",
        "cohorte": fila["cohorte"] or "rodaje",
        # lo que se DIJO antes del partido
        "clasificacion": tot.get("clasificacion", ""),
        "porcentaje": tot.get("porcentaje"),
        "pronosticoCadena": ((parte.get("cadena") or {}).get(lado) or ""),
        "unXDos": pron.get("probabilidades") or {},
        "marcadorPronosticado": pron.get("marcador", ""),
        "tde": ({"ie": tde.get("ie"), "ieNivel": tde.get("ieNivel", ""), "ventana": tde.get("ventana", "")}
                if tde else None),
        # la clase del bloque de ESTE equipo que calculó el DTP del rival
        "claseBloque": clase_bloque,
        # cómo SALIÓ
        "marcador": (f"{gf}-{gc}" if gf is not None and gc is not None else ""),
        "terminado": (fx.get("status_short") or "") in ("FT", "AET", "PEN", "AWD", "WO"),
        "veredicto": lv.get("veredicto", ""),
        "queP": lv.get("queP", ""),
        "leccion": lv.get("leccion", ""),
        "skill": lv.get("skill", ""),
        "seleccion": (ver or {}).get("seleccion", ""),
        "acredita": bool((ver or {}).get("acredita")),
        "cuarentena": cuar or "",
    }


def _acierto_ciego(partes: list[dict]) -> dict:
    """Solo lo acreditable (ciega + PRE) y fuera de cuarentena: lo mismo que
    cuenta el aprendizaje. Con n chico se dice, no se promedia a ciegas."""
    val = [p for p in partes if p["acredita"] and not p["cuarentena"] and p["veredicto"]]
    n = len(val)
    return {
        "n": n,
        "aciertos": sum(1 for p in val if p["veredicto"] == "acierto"),
        "parciales": sum(1 for p in val if p["veredicto"] == "parcial"),
        "fallos": sum(1 for p in val if p["veredicto"] == "fallo"),
        "nota": ("sin casos ciegos cerrados de este equipo" if not n else
                 "muestra corta: es memoria del equipo, no una tasa" if n < 5 else ""),
    }


def antecedentes(fixture_id: int, n: int = N_DEFECTO) -> dict | None:
    fx = _fixture(fixture_id)
    if not fx:
        return None
    from backend.analisis import lecciones as lec
    from backend.analisis.parte import _conectar
    fecha = str(fx["date"])
    with _conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b, parte_json, veredicto_json, cohorte "
            "FROM parte_cowork WHERE fixture_id<>? ORDER BY fecha DESC LIMIT 800",
            (fixture_id,)).fetchall()
    fxs = _fixtures_de([f["fixture_id"] for f in filas])
    # la cuarentena (manual o automática) como la ve el aprendizaje
    cuarentenas = {c["fixtureId"]: (c.get("cuarentena") or {}).get("motivo", "")
                   for c in lec._casos() if c.get("cuarentena")}
    inv = lec.inventario()
    out = {"fixtureId": fixture_id,
           "partido": {"equipoA": fx["home_name"], "equipoB": fx["away_name"], "fecha": fecha[:10]}}
    for lado, tid, nombre in (("a", fx["home_team_id"], fx["home_name"]),
                              ("b", fx["away_team_id"], fx["away_name"])):
        partes = []
        for f in filas:
            ofx = fxs.get(f["fixture_id"])
            # ANTI-HINDSIGHT: solo partidos anteriores a este
            if not ofx or str(ofx["date"]) >= fecha:
                continue
            if tid == ofx["home_team_id"]:
                partes.append(_resumen_parte(f, ofx, "a", cuarentenas))
            elif tid == ofx["away_team_id"]:
                partes.append(_resumen_parte(f, ofx, "b", cuarentenas))
            if len(partes) >= n:
                break
        vigentes = [{"clave": i["clave"], "skill": i["skill"], "leccion": i["leccion"],
                     "reglaTocada": i["reglaTocada"], "veredicto": i["veredicto"],
                     "estado": i["estado"], "puedeMoverNumeros": i["puedeMoverNumeros"],
                     "fecha": i["fecha"]}
                    for i in inv["items"]
                    if i["equipo"] == nombre and i["estado"] in ("pendiente", "en_revision")
                    and str(i["fecha"]) < fecha[:10]]
        out[lado] = {"equipoId": tid, "equipo": nombre, "partes": partes,
                     "aciertoCiego": _acierto_ciego(partes), "leccionesVigentes": vigentes}
    out["nota"] = ("solo partidos ANTERIORES a este (fecha menor, otro fixture): el caso nuevo sigue "
                   "siendo ciego. Lo que ya dijiste y sigue siendo cierto, no lo vuelvas a investigar: "
                   "cítalo con su fixtureId. Lo que fallaste, corrígelo y di por qué. Un antecedente con "
                   "`cuarentena` tenía el insumo roto: no se cita como precedente.")
    out["generadoEn"] = efedb.ahora()
    return out
