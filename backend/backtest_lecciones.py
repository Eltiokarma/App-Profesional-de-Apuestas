"""Backtest de las LECCIONES de los estudios de reventones (13-14/10/2026).

Los 52 estudios hacia atrás (`docs/autopsias/reventones-*.md`) dijeron POR QUÉ
revientan las burbujas, pero solo miraron burbujas que reventaron: no tienen
denominador. Este módulo pone cada lección contra TODAS las burbujas abiertas
del backtest (las que reventaron y las que no) y responde, para cada señal:

    ¿revienta más la burbuja cuando la señal está encendida?

con la tasa encendida/apagada, el lift, el intervalo de Wilson y el lift
ESTRATIFICADO por nivel de riesgo (una señal que solo repite lo que el riesgo
ya sabe no aporta: el lift crudo engaña cuando la señal va con el rival).

Se mide sobre la familia TOTAL (la que manda) y sin fuga: todo lo de la señal
sale de filas ANTERIORES al partido, salvo el bloque descriptivo del arquero,
que usa las estadísticas DEL partido y se declara como lo que es (autopsia,
no pronóstico).

Lecciones medidas:
- extremo / cerca / INFLADA (amistosos)            REVENTON §10, §10.2
- racha de otra competición, condición a contramano, racha concediendo,
  resaca internacional, parón largo                composición (Perú, 13/10)
- burbujas enfrentadas (el rival con la suya)       segunda tanda de Perú
- cambio de categoría (ascendido/descendido) y rival de otra base   escala
- DT distinto al de la racha, once distinto, arquero suplente (y del rival)
  — solo donde la base tiene las alineaciones; la cobertura viaja con su n
- ARQUERO-NO-FAVORITO: la burbuja depende de ganarle al arquero del débil
  (favorito con racha + o débil con racha −), y el perfil previo de ese
  arquero (goles evitados contra xG) — ¿predice? —
- región: Perú contra el resto (la «regresión al nivel» salió casi solo en Perú)
"""
from __future__ import annotations

import math
from bisect import bisect_left
from collections import Counter
from datetime import datetime
from functools import lru_cache

from backend import db

FILAS: dict[int, list[dict]] = {}          # equipo → sus constantes cronológicas (las carga el backtest)
NIVELES: dict[int, list[dict]] = {}        # equipo → niveles cronológicos
AMISTOSOS = {667}
DIAS_RESACA, PARON_DIAS, ONCE_CAMBIOS = 10, 14, 5
PERU = 281
NIVEL_FAVORITO = 0.5                       # diferencia de nivel para llamar «favorito» a un lado


IDX: dict[int, dict[int, int]] = {}        # equipo → {fixtureId: posición}
BURBUJA: dict[int, dict[int, int]] = {}    # equipo → {fixtureId: partidos de la burbuja abierta ANTES}
FECHAS_NV: dict[int, list[str]] = {}


def registrar(team_id: int, filas: list[dict], niveles: list[dict]) -> None:
    FILAS[team_id] = filas
    NIVELES[team_id] = niveles
    IDX[team_id] = {f["fixtureId"]: k for k, f in enumerate(filas)}
    FECHAS_NV[team_id] = [n["fecha"] for n in niveles]
    antes, signo, n = {}, 0, 0
    for f in filas:
        antes[f["fixtureId"]] = n
        v = float(f["fusion"]["k"])
        s_ = (v > 0) - (v < 0)
        n = n + 1 if s_ and s_ == signo else (1 if s_ else 0)
        signo = s_
    BURBUJA[team_id] = antes


def _dt(s) -> datetime | None:
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00").replace(" ", "T"))
    except ValueError:
        return None


@lru_cache(maxsize=4096)
def _es_copa(liga_id: int) -> bool:
    from backend.analisis import escala
    try:
        return escala.es_copa(liga_id)
    except Exception:  # noqa: BLE001
        return False


@lru_cache(maxsize=4096)
def _segunda(liga_id: int) -> bool:
    from backend.analisis.parte import _segunda as seg
    return seg(liga_id)


def _es_liga(liga_id, intl: bool) -> bool:
    return bool(liga_id) and not intl and liga_id not in AMISTOSOS and not _es_copa(liga_id)


def _base(filas: list[dict]) -> int | None:
    """La liga doméstica: la más frecuente de las últimas 30 filas de liga."""
    c = Counter(f["ligaId"] for f in filas[-60:] if _es_liga(f["ligaId"], f.get("esInternacional")))
    return c.most_common(1)[0][0] if c else None


def _nivel_a(team_id: int, fecha: str) -> float | None:
    nv = NIVELES.get(team_id) or []
    i = bisect_left(FECHAS_NV.get(team_id) or [], fecha)
    return nv[i - 1]["nivel"] if i > 0 else None


def _burbuja_antes(team_id: int, fixture_id: int) -> int | None:
    """Partidos de la burbuja total abierta del equipo ANTES de ese fixture."""
    return (BURBUJA.get(team_id) or {}).get(fixture_id)


# ── las alineaciones (solo donde la base las tiene) ─────────────────────────

_CON_ONCE: set[tuple[int, int]] | None = None


def _con_once() -> set[tuple[int, int]]:
    global _CON_ONCE
    if _CON_ONCE is None:
        try:
            _CON_ONCE = {(r["fixture_id"], r["team_id"]) for r in db.query(
                "sad", "SELECT fixture_id, team_id FROM alineaciones WHERE titular=1 GROUP BY fixture_id, team_id "
                       "HAVING COUNT(*) >= 11")}
        except Exception:  # noqa: BLE001
            _CON_ONCE = set()
    return _CON_ONCE


def _titulares(fixture_id: int, team_id: int) -> list[dict]:
    return db.query("sad", "SELECT player_id, posicion, entrenador FROM alineaciones WHERE fixture_id=? AND "
                           "team_id=? AND titular=1", (fixture_id, team_id))


def _arquero_suplente(team_id: int, fixture_id: int, previos: list[int]) -> bool | None:
    if (fixture_id, team_id) not in _con_once():
        return None
    hoy = next((t["player_id"] for t in _titulares(fixture_id, team_id) if t["posicion"] == "G"), None)
    c = Counter()
    for fid in previos[-10:]:
        if (fid, team_id) in _con_once():
            c.update(t["player_id"] for t in _titulares(fid, team_id) if t["posicion"] == "G")
    if hoy is None or not c:
        return None
    return hoy != c.most_common(1)[0][0]


def _once_distinto(team_id: int, fixture_id: int, previo: int | None) -> bool | None:
    if previo is None or (fixture_id, team_id) not in _con_once() or (previo, team_id) not in _con_once():
        return None
    hoy = {t["player_id"] for t in _titulares(fixture_id, team_id)}
    antes = {t["player_id"] for t in _titulares(previo, team_id)}
    return len(hoy - antes) >= ONCE_CAMBIOS


def _dt_distinto(team_id: int, fixture_id: int, primero: int | None) -> bool | None:
    if primero is None:
        return None
    a = next((t["entrenador"] for t in _titulares(fixture_id, team_id) if t["entrenador"]), "")
    b = next((t["entrenador"] for t in _titulares(primero, team_id) if t["entrenador"]), "")
    if not a or not b:
        return None
    from backend.analisis.parte import mismo_dt
    return not mismo_dt(a, b)


# ── el arquero del no favorito ──────────────────────────────────────────────

def _stats(fixture_id: int) -> dict[tuple[int, str], float]:
    try:
        filas = db.query("sad", "SELECT team_id, clave, valor FROM fixture_stats WHERE fixture_id=? AND clave IN "
                                "('Shots on Goal','Goalkeeper Saves','expected_goals')", (fixture_id,))
    except Exception:  # noqa: BLE001
        return {}
    out = {}
    for f in filas:
        try:
            out[(f["team_id"], f["clave"])] = float(str(f["valor"]).replace("%", ""))
        except (TypeError, ValueError):
            pass
    return out


# ── los rasgos de una observación ───────────────────────────────────────────

def rasgos(o: dict) -> dict:
    """Las lecciones de una observación del backtest (familia total)."""
    team, fx = o["equipoId"], o["fixtureId"]
    filas = FILAS.get(team) or []
    i = (IDX.get(team) or {}).get(fx)
    if i is None:
        return {}
    fila, prefijo = filas[i], filas[:i]
    racha = prefijo[-o["partidos"]:] if o["partidos"] else []
    n = len(racha) or 1
    hoy = _dt(fila["fecha"])
    ruido = AMISTOSOS
    amist = sum(1 for f in racha if f["ligaId"] in ruido)
    r: dict = {"extremo": bool(o["extremo"]), "cerca": bool(o["cerca"])}
    r["enAmistoso"] = fila["ligaId"] in ruido
    r["inflada"] = (o["extremo"] or o["cerca"]) and amist > 0 and amist * 2 >= len(racha)
    r["otraCompeticion"] = sum(1 for f in racha if f["ligaId"] != fila["ligaId"] or f["ligaId"] in ruido) * 2 >= n
    r["contramano"] = sum(1 for f in racha if f["condicion"] != fila["condicion"]) * 3 >= 2 * n
    r["concediendo"] = (o["signo"] == "+" and len(racha) >= 2
                        and all((f["golesContra"] or 0) > 0 for f in racha)) if o["signo"] == "+" else None
    r["resacaIntl"] = any(f.get("esInternacional") and (f["golesFavor"] or 0) < (f["golesContra"] or 0)
                          and hoy and _dt(f["fecha"]) and 0 < (hoy - _dt(f["fecha"])).days <= DIAS_RESACA
                          for f in prefijo[-6:])
    ult = next((_dt(f["fecha"]) for f in reversed(prefijo) if f["ligaId"] not in ruido), None)
    r["paronLargo"] = bool(hoy and ult and (hoy - ult).days >= PARON_DIAS)
    # escala: cambio de categoría del equipo y rival de otra base
    base = _base(prefijo)
    liga_hoy = fila["ligaId"] if _es_liga(fila["ligaId"], fila.get("esInternacional")) else None
    r["cambioCategoria"] = (None if base is None or liga_hoy is None
                            else liga_hoy != base and _segunda(liga_hoy) != _segunda(base))
    rv = FILAS.get(o["rivalId"]) if o.get("rivalId") else None
    if rv is not None:
        j = (IDX.get(o["rivalId"]) or {}).get(fx)
        base_r = _base(rv[:j]) if j is not None else None
        r["rivalOtraBase"] = None if base is None or base_r is None else (
            base != base_r and (_segunda(base) != _segunda(base_r)))
        pr = _burbuja_antes(o["rivalId"], fx)
        r["rivalEnBurbuja"] = None if pr is None else pr >= 2
    else:
        r["rivalOtraBase"] = r["rivalEnBurbuja"] = None
    # alineaciones (cobertura parcial)
    ids_prev = [f["fixtureId"] for f in prefijo]
    misma = [f["fixtureId"] for f in racha if f["ligaId"] == fila["ligaId"] and f["ligaId"] not in ruido]
    sin_am = [f["fixtureId"] for f in racha if f["ligaId"] not in ruido]
    try:
        r["arqueroSuplente"] = _arquero_suplente(team, fx, ids_prev)
        r["arqueroSuplenteRival"] = _arquero_suplente(o["rivalId"], fx, [f["fixtureId"] for f in (rv or [])
                                                      if f["fecha"] < fila["fecha"]]) if o.get("rivalId") else None
        r["onceDistinto"] = _once_distinto(team, fx, misma[-1] if misma else None)
        r["dtDistinto"] = _dt_distinto(team, fx, sin_am[0] if sin_am else None)
    except Exception:  # noqa: BLE001 — base sin alineaciones
        r["arqueroSuplente"] = r["arqueroSuplenteRival"] = r["onceDistinto"] = r["dtDistinto"] = None
    # ARQUERO-NO-FAVORITO: la burbuja depende de ganarle al arquero del débil
    ne, nr = _nivel_a(team, fila["fecha"]), fila.get("nivelRival")
    fav = None if ne is None or nr is None else (
        "equipo" if ne - nr >= NIVEL_FAVORITO else "rival" if nr - ne >= NIVEL_FAVORITO else "parejo")
    r["favorito"] = fav
    r["arqueroNoFavorito"] = None if fav is None else (
        (o["signo"] == "+" and fav == "equipo") or (o["signo"] == "-" and fav == "rival"))
    # el perfil previo del arquero del débil y lo que pasó en el partido (solo con stats)
    st = _stats(fx) if r["arqueroNoFavorito"] else {}
    if st and o.get("rivalId"):
        debil = o["rivalId"] if fav == "equipo" else team
        fuerte = team if fav == "equipo" else o["rivalId"]
        from backend.analisis import arquero
        p = arquero.perfil(debil, str(fila["fecha"]).replace("T", " ").rstrip("Z")[:19])
        gv = (p or {}).get("golesVsXg") or {}
        r["arqueroDebilEvitadosPrevio"] = gv.get("evitados") if gv.get("n", 0) >= 5 else None
        r["atajadasDebil"] = st.get((debil, "Goalkeeper Saves"))
        r["tirosAlArcoFuerte"] = st.get((fuerte, "Shots on Goal"))
    r["peru"] = fila["ligaId"] == PERU
    return r


# ── el resumen ──────────────────────────────────────────────────────────────

LECCIONES = [
    ("extremo", "récord de la burbuja (K-EXTREMO)"),
    ("cerca", "cerca del extremo (K-CERCA)"),
    ("inflada", "extremo/cerca INFLADO por amistosos"),
    ("enAmistoso", "el partido es un amistoso"),
    ("otraCompeticion", "racha de otra competición"),
    ("contramano", "racha en la condición contraria"),
    ("concediendo", "racha de victorias concediendo en todas"),
    ("resacaIntl", "derrota internacional en los 10 días previos"),
    ("paronLargo", "14+ días sin partido oficial"),
    ("rivalEnBurbuja", "el rival con su propia burbuja (2+)"),
    ("cambioCategoria", "el equipo cambió de categoría (ascendido/descendido)"),
    ("rivalOtraBase", "rival de otra base (otra división)"),
    ("dtDistinto", "DT distinto al de la racha"),
    ("onceDistinto", "5+ titulares distintos al último de la racha"),
    ("arqueroSuplente", "arquero suplente"),
    ("arqueroSuplenteRival", "arquero suplente del rival"),
    ("arqueroNoFavorito", "ARQUERO-NO-FAVORITO: hay que ganarle al arquero del débil"),
    ("peru", "partido de la Liga 1 de Perú"),
]


def _wilson(r: int, n: int) -> list[float] | None:
    if not n:
        return None
    z, p = 1.96, r / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - m, 3), round(c + m, 3)]


def _t(sub: list[dict]) -> dict:
    n = len(sub)
    r = sum(1 for o in sub if o["revento"])
    return {"n": n, "reventones": r, "tasa": round(r / n, 3) if n else None, "ic95": _wilson(r, n)}


def _estratificado(obs: list[dict], clave: str) -> float | None:
    """Lift dentro de cada nivel de riesgo, promediado con peso n_encendida:
    lo que la señal aporta POR ENCIMA de lo que el riesgo ya dice."""
    num = den = 0.0
    for nivel in ("bajo", "medio", "alto", "muy alto"):
        g = [o for o in obs if o["nivel"] == nivel]
        con = [o for o in g if o.get(clave) is True]
        sin = [o for o in g if o.get(clave) is False]
        if len(con) >= 20 and len(sin) >= 20:
            num += len(con) * (_t(con)["tasa"] - _t(sin)["tasa"])
            den += len(con)
    return round(num / den, 3) if den else None


def _terciles(obs: list[dict], clave: str) -> list[dict] | None:
    v = [o for o in obs if o.get(clave) is not None]
    if len(v) < 30:
        return None
    v.sort(key=lambda o: o[clave])
    k = len(v) // 3
    partes = [v[:k], v[k:2 * k], v[2 * k:]]
    return [{"desde": p[0][clave], "hasta": p[-1][clave], **_t(p)} for p in partes]


def resumir(obs: list[dict]) -> dict:
    tot = [o for o in obs if o["familia"] == "total" and o["nivel"] != "sin base" and "_lec" in o]
    lecciones = {}
    for clave, que in LECCIONES:
        con = [o for o in tot if o["_lec"].get(clave) is True]
        sin = [o for o in tot if o["_lec"].get(clave) is False]
        tc, ts = _t(con), _t(sin)
        lecciones[clave] = {
            "que": que, "encendida": tc, "apagada": ts,
            "lift": round(tc["tasa"] - ts["tasa"], 3) if con and sin else None,
            "liftSobreElRiesgo": _estratificado([{**o, clave: o["_lec"].get(clave)} for o in tot], clave),
            "cobertura": round((len(con) + len(sin)) / len(tot), 3) if tot else 0,
            "porSigno": {s: {"encendida": _t([o for o in con if o["signo"] == s]),
                             "apagada": _t([o for o in sin if o["signo"] == s])} for s in ("+", "-")},
        }
    anf = [o for o in tot if o["_lec"].get("arqueroNoFavorito")]
    arquero = {
        "nota": ("Descriptivo con las stats DEL partido (autopsia, no pronóstico): cuánto revienta la burbuja "
                 "que depende de ganarle al arquero del débil según cuánto atajó ese arquero y cuántos tiros "
                 "al arco tuvo el fuerte. El único insumo PREVIO es `arqueroDebilEvitadosPrevio` (goles "
                 "evitados contra xG en sus últimos 10, con n ≥ 5): si sus terciles no separan, la forma del "
                 "arquero no se puede usar para pronosticar"),
        "conStats": len([o for o in anf if o["_lec"].get("atajadasDebil") is not None]),
        "porAtajadasDelDebil": _terciles([{**o, "x": o["_lec"].get("atajadasDebil")} for o in anf], "x"),
        "porTirosAlArcoDelFuerte": _terciles([{**o, "x": o["_lec"].get("tirosAlArcoFuerte")} for o in anf], "x"),
        "porPerfilPrevioDelArquero": _terciles(
            [{**o, "x": o["_lec"].get("arqueroDebilEvitadosPrevio")} for o in anf], "x"),
    }
    return {
        "observaciones": len(tot),
        "tasaBase": _t(tot),
        "lecciones": lecciones,
        "arqueroNoFavorito": arquero,
        "region": {"peru": _t([o for o in tot if o["_lec"].get("peru")]),
                   "resto": _t([o for o in tot if not o["_lec"].get("peru")]),
                   "peruRivalEnZona": _t([o for o in tot if o["_lec"].get("peru") and o.get("rivalEnZona")]),
                   "restoRivalEnZona": _t([o for o in tot if not o["_lec"].get("peru") and o.get("rivalEnZona")])},
        "aviso": ("lift = tasa encendida − apagada; liftSobreElRiesgo = el mismo lift DENTRO de cada nivel de "
                  "riesgo (lo que la señal suma a lo calibrado). Una señal sin lift sobre el riesgo no se agrega "
                  "a los puntos aunque los estudios la hayan visto en muchos reventones: eso es lo que el "
                  "denominador corrige"),
    }


GUARDADO = ".backtest_lecciones.json"   # en SAD_DATA_DIR: lo lee GET /analisis/cowork/reventones/backtest
GUARDADO_CAL = ".backtest_calibracion.json"


def guardar(resumen: dict, clave: str = "lecciones") -> str:
    import json
    import os
    from datetime import timezone
    ruta = os.path.join(db.BASE_DIR, GUARDADO_CAL if clave == "calibracion" else GUARDADO)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({**resumen, "corridoEn": datetime.now(timezone.utc).isoformat(timespec="seconds")}, f,
                  ensure_ascii=False)
    return ruta


def leer(clave: str = "lecciones") -> dict | None:
    import json
    import os
    ruta = os.path.join(db.BASE_DIR, GUARDADO_CAL if clave == "calibracion" else GUARDADO)
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def enriquecer(obs: list[dict]) -> None:
    for o in obs:
        if o["familia"] == "total" and o["nivel"] != "sin base":
            o["_lec"] = rasgos(o)


def imprimir(r: dict) -> None:
    def pct(t):
        return "—" if t["tasa"] is None else f"{t['tasa'] * 100:.1f}%"
    print(f"\n══ LECCIONES DE LOS ESTUDIOS (familia total, {r['observaciones']} burbujas abiertas · "
          f"tasa base {pct(r['tasaBase'])}) ══")
    for clave, v in r["lecciones"].items():
        print(f"  {v['que'][:52]:52s} on {pct(v['encendida'])} (n={v['encendida']['n']}) · off "
              f"{pct(v['apagada'])} · lift {v['lift']} · sobre el riesgo {v['liftSobreElRiesgo']} · "
              f"cobertura {v['cobertura']}")
    a = r["arqueroNoFavorito"]
    print(f"\n— arquero del no favorito ({a['conStats']} con stats del partido) —")
    for k in ("porAtajadasDelDebil", "porTirosAlArcoDelFuerte", "porPerfilPrevioDelArquero"):
        print(f"  {k}: " + (" | ".join(f"{t['desde']}–{t['hasta']}: {pct(t)} (n={t['n']})" for t in a[k])
                            if a[k] else "sin muestra"))
    rg = r["region"]
    print(f"\n— región — Perú {pct(rg['peru'])} (n={rg['peru']['n']}) · resto {pct(rg['resto'])} "
          f"(n={rg['resto']['n']}) · con el rival en zona: Perú {pct(rg['peruRivalEnZona'])} · resto "
          f"{pct(rg['restoRivalEnZona'])}")
