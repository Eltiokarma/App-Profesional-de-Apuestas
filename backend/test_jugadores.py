"""Test del presupuesto de la ingesta de jugadores — sin red.

Blinda las dos palancas que recortaron su gasto (30/07/2026: 400 equipos/día
× 4 endpoints = 1.648 requests, el 25% del plan):

1. TTL SEPARADO. Los cuatro endpoints iban con el mismo TTL de 7 días, pero
   traspasos y DT no cambian a ritmo semanal. Con TTL propio de 30 días se
   ahorra la mitad del gasto — SIN perder el cambio de DT, que se detecta por
   el entrenador que ya viene en cada alineación capturada.
2. PADRÓN. El recorrido usaba las 56 ligas de LIGAS, incluidas las copas
   nacionales (cientos de equipos de ascenso) y los Amistosos de Clubes
   (equipos de todo el mundo). Ahora sigue las ligas importantes.

    python -m backend.test_jugadores
"""
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

from backend.ingesta import jugadores as jug
from backend.ingesta.jugadores import (
    TTL_HORAS_LENTO,
    equipos_pendientes,
    necesita_lentas,
    preparar_tablas,
    _norm_dt,
)

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def hace(horas: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")


def db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.executescript("""
        CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT,
            league_id INTEGER, league_season INTEGER, home_team_id INTEGER, away_team_id INTEGER);
        CREATE TABLE alineaciones (fixture_id INTEGER, team_id INTEGER, entrenador TEXT);
    """)
    preparar_tablas(con)
    return con


def main():
    # --- 1. TTL separado de traspasos y DT --------------------------------
    con = db()
    check("sin marca previa, traspasos y DT se piden", necesita_lentas(con, 500))

    con.execute("INSERT INTO plantillas_meta (team_id, season, actualizado_en, con_datos, lento_en) "
                "VALUES (500, 2026, ?, 1, ?)", (hace(1), hace(1)))
    con.commit()
    check("recién pedidos, NO se repiten (es el ahorro)", not necesita_lentas(con, 500))

    con.execute("UPDATE plantillas_meta SET lento_en=? WHERE team_id=500", (hace(TTL_HORAS_LENTO + 1),))
    con.commit()
    check("pasado el TTL lento (30 días) se vuelven a pedir", necesita_lentas(con, 500))

    # la plantilla sigue con SU TTL: 8 días de antigüedad en lento_en no la
    # hace vencer, y eso es justo lo que ahorra las 2 requests por equipo
    con.execute("UPDATE plantillas_meta SET lento_en=? WHERE team_id=500", (hace(24 * 8),))
    con.commit()
    check("a los 8 días (cuando la plantilla ya venció) las lentas siguen frescas",
          not necesita_lentas(con, 500))

    # --- 2. el cambio de DT no espera al TTL ------------------------------
    con.execute("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (9, ?, 'FT', 128)",
                (hace(48),))
    con.execute("INSERT INTO alineaciones (fixture_id, team_id, entrenador) VALUES (9, 500, 'M. Gallardo')")
    con.execute("INSERT INTO entrenadores (team_id, coach_id, nombre, actualizado_en) "
                "VALUES (500, 1, 'Marcelo Gallardo', ?)", (hace(48),))
    con.commit()
    check("mismo DT escrito distinto NO dispara refresco (M. Gallardo = Marcelo Gallardo)",
          not necesita_lentas(con, 500))

    con.execute("UPDATE alineaciones SET entrenador='Gustavo Costas' WHERE team_id=500")
    con.commit()
    check("DT DISTINTO en la alineación fuerza el refresco sin esperar 30 días",
          necesita_lentas(con, 500))
    check("normalización de nombres de DT",
          _norm_dt("M. Pellegrino") == _norm_dt("Mauricio Pellegrino")
          and _norm_dt("Gallardo") != _norm_dt("Costas"))

    # --- 3. el padrón: ligas importantes, no las copas ---------------------
    con = db()
    prox = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    con.executemany(
        "INSERT INTO fixtures (id, date, status_short, league_id, league_season, "
        "home_team_id, away_team_id) VALUES (?,?,'NS',?,2026,?,?)",
        [(1, prox, 128, 100, 101),   # Argentina - Liga Profesional (importante)
         (2, prox, 130, 200, 201),   # Copa Argentina (menor: equipos de ascenso)
         (3, prox, 667, 300, 301),   # Amistosos de Clubes (equipos del mundo)
         (4, prox, 282, 400, 401)],  # Perú - Liga 2 (menor)
    )
    con.commit()
    ids = {t for t, _ in equipos_pendientes(con, 3, 168)}
    check("solo entran los equipos de ligas importantes", ids == {100, 101}, sorted(ids))
    check("los de copa nacional, 2ª división y amistosos quedan fuera",
          not ({200, 201, 300, 301, 400, 401} & ids), sorted(ids))

    # el equipo de 1ª que juega copa sigue entrando POR SU LIGA
    con.execute("INSERT INTO fixtures (id, date, status_short, league_id, league_season, "
                "home_team_id, away_team_id) VALUES (5, ?, 'NS', 130, 2026, 100, 202)", (prox,))
    con.commit()
    ids = {t for t, _ in equipos_pendientes(con, 3, 168)}
    check("un equipo de 1ª que además juega copa no se pierde", 100 in ids, sorted(ids))
    check("pero su rival de ascenso sigue fuera", 202 not in ids, sorted(ids))

    # la vuelta atrás por env existe
    jug.JUGADORES_TODAS_LIGAS = True
    try:
        ids = {t for t, _ in equipos_pendientes(con, 3, 168)}
        check("SAD_JUGADORES_TODAS_LIGAS=1 devuelve el padrón completo",
              {200, 300, 400} <= ids, sorted(ids))
    finally:
        jug.JUGADORES_TODAS_LIGAS = False

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
