"""PARTIDOS AJENOS: el homónimo con el id cruzado por la API (10/11/2026, incidencia 1371).

Atlético Nacional de Colombia (team 1137) tenía en la base dos partidos de la
Copa Perú (liga 503) ante Juventud Palmeiras —un 2-2 el 08/11 y la vuelta el
14/11— que son de OTRO club peruano que se llama igual: API-Football le asignó
a ese club el id 1137. Como Nacional juega la Libertadores, es «equipo de
interés» y la ingesta guarda todos sus partidos del feed por fecha, los ajenos
incluidos. Efectos: la K total y la de visita en 0 (/burbujas sin riesgo ni
tarjeta), el DTP sin partido anterior, F2 con 2 días de descanso en vez de 3,
dos «próximos» que no existen y una forma con un partido de liga que no jugó.

La regla de la CLASE, en UN lugar: un partido de una competición NACIONAL (ni
internacional de clubes, ni amistoso, ni de un país «World») de un país
distinto al del equipo no es de ese equipo. El país del equipo NO sale de
`teams.country` (la ingesta lo guarda de /fixtures, que no lo trae, y Cardiff
es de Gales y juega en Inglaterra): sale de sus partidos, el país con más
partidos nacionales. Para no llamar ajeno a lo que no lo es:
- el país propio necesita `MIN_PROPIOS` partidos y el doble que el ajeno
  (sin mayoría clara no se afirma nada);
- los pares de países con clubes que cruzan la frontera de verdad
  (`FRONTERAS`: Toronto juega la MLS y el Campeonato Canadiense, Vaduz la
  Challenge League suiza y la Copa de Liechtenstein) no se marcan.

Quien arma la historia o el calendario de un equipo la usa: el pipeline saca
el partido entero (`ajenos_de_la_base`, la K y el nivel del rival también
salían de un 1137 que no era) y los lectores de `sad.db` suman
`sql_fuera(team_id)` a su WHERE. Solo lee, 0 requests. No borra nada de la base.
"""
from __future__ import annotations

import time
from collections import Counter, defaultdict

from backend import db as saddb

MIN_PROPIOS = 3          # partidos nacionales del país propio para afirmar el país
RAZON_MAYORIA = 2        # el país propio, al menos el doble que el ajeno
SIN_PAIS = {"", "world"}
FRONTERAS = {frozenset(p) for p in (
    ("USA", "Canada"), ("England", "Wales"), ("Switzerland", "Liechtenstein"),
    ("France", "Monaco"), ("Spain", "Andorra"), ("Italy", "San-Marino"),
    ("Ireland", "Northern-Ireland"), ("Australia", "New-Zealand"),
)}
AMISTOSOS = {667}
_CACHE_SEG = 60.0
_cache: dict[tuple, tuple[float, set[int]]] = {}


def _internacionales() -> set[int]:
    try:
        from backend.ingesta.extractor import LIGAS_INTERNACIONALES
        return set(LIGAS_INTERNACIONALES)
    except Exception:  # noqa: BLE001 — sin la ingesta importable: Champions, Europa, Conference, Libertadores, Sudamericana
        return {2, 3, 848, 13, 11}


def _pais_nacional(league_id, pais, internacionales: set[int]) -> str | None:
    """El país de una competición NACIONAL; None si es internacional, amistosa o sin país."""
    if league_id in internacionales or league_id in AMISTOSOS:
        return None
    p = (pais or "").strip()
    return None if p.lower() in SIN_PAIS else p


def ajenos(filas, internacionales: set[int] | None = None) -> tuple[str | None, set[int]]:
    """(país del equipo, fixtures ajenos) de UN equipo. `filas`: sus partidos
    como (fixture_id, league_id, país de la liga). La regla, pura."""
    internacionales = _internacionales() if internacionales is None else internacionales
    por_pais: dict[str, list[int]] = defaultdict(list)
    for fid, liga, pais in filas:
        p = _pais_nacional(liga, pais, internacionales)
        if p:
            por_pais[p].append(fid)
    if not por_pais:
        return None, set()
    conteo = Counter({p: len(v) for p, v in por_pais.items()})
    (propio, n), *resto = conteo.most_common()
    if n < MIN_PROPIOS or (resto and resto[0][1] == n):
        return None, set()
    fuera = set()
    for p, m in resto:
        if n >= RAZON_MAYORIA * m and frozenset((propio, p)) not in FRONTERAS:
            fuera.update(por_pais[p])
    return propio, fuera


_SQL_EQUIPO = ("SELECT f.id, f.league_id, l.country FROM fixtures f LEFT JOIN leagues l ON l.id=f.league_id "
               "WHERE f.home_team_id=? UNION ALL "
               "SELECT f.id, f.league_id, l.country FROM fixtures f LEFT JOIN leagues l ON l.id=f.league_id "
               "WHERE f.away_team_id=?")


def ajenos_del_equipo(team_id: int | None, con=None) -> set[int]:
    """Los fixtures de `team_id` que son del homónimo. Con caché corta por
    proceso: el calendario, el TDE y el DTP lo piden varias veces por parte."""
    if not team_id:
        return set()
    ahora = time.monotonic()
    clave = (saddb.db_path("sad"), team_id)
    if con is None:
        hit = _cache.get(clave)
        if hit and ahora - hit[0] < _CACHE_SEG:
            return hit[1]
    try:
        filas = (con.execute(_SQL_EQUIPO, (team_id, team_id)).fetchall() if con is not None
                 else saddb.query("sad", _SQL_EQUIPO, (team_id, team_id)))
        _, fuera = ajenos([tuple(r) for r in filas])
    except Exception:  # noqa: BLE001 — base sin la tabla de ligas: no se afirma que nada sea ajeno
        fuera = set()
    if con is None:
        _cache[clave] = (ahora, fuera)
    return fuera


def sql_fuera(team_id: int | None, alias: str = "f", con=None) -> tuple[str, tuple]:
    """El fragmento que un lector suma a su WHERE: (« AND f.id NOT IN (…)», params)."""
    fuera = sorted(ajenos_del_equipo(team_id, con))
    if not fuera:
        return "", ()
    col = f"{alias}.id" if alias else "id"
    return f" AND {col} NOT IN ({','.join('?' * len(fuera))})", tuple(fuera)


def ajenos_de_la_base(con) -> dict[int, set[int]]:
    """{team_id: fixtures ajenos} de TODA la base, en una pasada (el pipeline)."""
    por_equipo: dict[int, list[tuple]] = defaultdict(list)
    try:
        filas = con.execute("SELECT f.id, f.home_team_id, f.away_team_id, f.league_id, l.country "
                            "FROM fixtures f LEFT JOIN leagues l ON l.id=f.league_id").fetchall()
    except Exception:  # noqa: BLE001 — base sin la tabla de ligas (DBs viejas): nada se marca
        return {}
    for fid, home, away, liga, pais in filas:
        for t in (home, away):
            if t:
                por_equipo[t].append((fid, liga, pais))
    internacionales = _internacionales()
    out = {}
    for t, fs in por_equipo.items():
        _, fuera = ajenos(fs, internacionales)
        if fuera:
            out[t] = fuera
    return out


def detalle(team_id: int, con=None) -> list[dict]:
    """Los ajenos de un equipo con su liga y país, para el escaneo."""
    fuera = sorted(ajenos_del_equipo(team_id, con))
    if not fuera:
        return []
    sql = ("SELECT f.id, f.date, f.league_id, l.name AS liga, l.country AS pais FROM fixtures f "
           f"LEFT JOIN leagues l ON l.id=f.league_id WHERE f.id IN ({','.join('?' * len(fuera))}) ORDER BY f.date")
    filas = con.execute(sql, tuple(fuera)).fetchall() if con is not None else saddb.query("sad", sql, tuple(fuera))
    return [{"fixtureId": r[0], "fecha": str(r[1])[:10], "ligaId": r[2], "liga": r[3] or "", "pais": r[4] or ""}
            for r in filas]
