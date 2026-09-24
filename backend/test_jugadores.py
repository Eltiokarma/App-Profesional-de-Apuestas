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

    # --- 2b. EL DT VIGENTE, no el saliente (17 de 22 mal en la corrida del 16/09)
    from backend.ingesta.jugadores import elegir_entrenador, guardar_entrenador
    carrera = [
        {"id": 1, "name": "S. Novoa", "career": [{"team": {"id": 700}, "start": "2019-01-01", "end": None}]},
        {"id": 2, "name": "Leonel Álvarez", "career": [{"team": {"id": 700}, "start": "2024-07-01", "end": "2026-05-01"}]},
        {"id": 3, "name": "Leonardo Peirano", "career": [{"team": {"id": 700}, "start": "2026-05-27", "end": None},
                                                         {"team": {"id": 999}, "start": "2020-01-01", "end": None}]},
    ]
    e = elegir_entrenador(carrera, 700)
    check("con dos etapas abiertas gana la de start MÁS RECIENTE (Peirano 2026, no Novoa 2019)",
          e and e["nombre"] == "Leonardo Peirano" and e["desde"] == "2026-05-27", e)
    check("una etapa cerrada más nueva que la abierta vieja no la desplaza a la abierta más nueva",
          elegir_entrenador(carrera[:2], 700)["nombre"] == "S. Novoa")
    check("sin etapas abiertas, la de start más reciente",
          elegir_entrenador([carrera[1]], 700)["nombre"] == "Leonel Álvarez")
    check("la última alineación manda cuando casa con un candidato",
          elegir_entrenador(carrera, 700, "S. Novoa")["nombre"] == "S. Novoa")
    # LA SALIDA SE VE EN LA ALINEACIÓN (18/09: Sassuolo, Aucas, Comerciantes
    # Unidos y ADT seguían con el saliente porque /coachs no lista al nuevo)
    nuevo = elegir_entrenador(carrera, 700, "Pep Guardiola", "2026-09-01")
    check("un DT que se sentó en el banco y NO está en la carrera es el vigente, con fuente alineacion",
          nuevo["nombre"] == "Pep Guardiola" and nuevo["desde"] == "2026-09-01" and nuevo["fuente"] == "alineacion", nuevo)
    check("el que sale de la carrera lleva fuente coachs", elegir_entrenador(carrera, 700)["fuente"] == "coachs")
    check("sin carrera pero con alineación, el de la alineación",
          elegir_entrenador([], 700, "Pep Guardiola", "2026-09-01")["nombre"] == "Pep Guardiola")
    from backend.ingesta.jugadores import nombre_coach, dt_de_alineaciones
    check("el nombre se arma Nombre Apellido con firstname/lastname (Tigres devolvía «Manuel Vucetich Rojas Victor»)",
          nombre_coach({"name": "Manuel Vucetich Rojas Victor", "firstname": "Víctor Manuel",
                        "lastname": "Vucetich Rojas"}) == "Víctor Manuel Vucetich Rojas")
    check("sin firstname/lastname queda name", nombre_coach({"name": "S. Novoa"}) == "S. Novoa")
    check("otra etapa del mismo DT en OTRO club no cuenta", elegir_entrenador(carrera, 999) and
          elegir_entrenador(carrera, 700)["desde"] == "2026-05-27")
    check("sin carrera en este club, nada", elegir_entrenador(carrera, 123) is None)
    con.execute("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (10, ?, 'FT', 239)", (hace(24),))
    con.execute("INSERT INTO alineaciones (fixture_id, team_id, entrenador) VALUES (10, 700, 'L. Peirano')")
    con.commit()
    check("guardar_entrenador deja UNA fila: el vigente", guardar_entrenador(con, 700, carrera) == 1
          and [r[0] for r in con.execute("SELECT nombre FROM entrenadores WHERE team_id=700")] == ["Leonardo Peirano"])
    # la racha en el banco: el `desde` del DT nuevo es su PRIMER partido, no el último
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id) VALUES (?, ?, 'FT', 239)",
                    [(11, hace(24 * 20)), (12, hace(24 * 12)), (13, hace(24 * 5))])
    con.executemany("INSERT INTO alineaciones (fixture_id, team_id, entrenador) VALUES (?, 700, ?)",
                    [(11, "L. Peirano"), (12, "Pep Guardiola"), (13, "P. Guardiola")])
    con.commit()
    dt_a, desde_a = dt_de_alineaciones(con, 700)
    check("la racha del DT en el banco arranca en su primer partido (dos grafías del mismo apellido)",
          dt_a == "L. Peirano" and desde_a == hace(24)[:10], (dt_a, desde_a))
    con.execute("UPDATE fixtures SET date=? WHERE id=10", (hace(24 * 30),))
    con.commit()
    dt_a, desde_a = dt_de_alineaciones(con, 700)
    check("cuando el último partido lo dirigió otro, la racha es la suya",
          dt_a == "P. Guardiola" and desde_a == hace(24 * 12)[:10], (dt_a, desde_a))
    guardar_entrenador(con, 700, carrera)
    fila = con.execute("SELECT nombre, desde, fuente FROM entrenadores WHERE team_id=700").fetchone()
    check("guardar_entrenador registra la salida: el del banco, con fuente alineacion y su primer partido",
          fila and fila[0] == "P. Guardiola" and fila[1] == hace(24 * 12)[:10] and fila[2] == "alineacion", fila)
    # UNA ALINEACIÓN RANCIA NO ES «LA ÚLTIMA» (Santa Fe–Cali, 22/09): si el
    # equipo jugó 3 partidos terminados DESPUÉS de la última alineación
    # capturada —la liga dejó de publicar onces—, ese DT es historia y manda
    # la carrera, no el banco de hace meses.
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id) "
                    "VALUES (?, ?, 'FT', 239, 700)",
                    [(14, hace(24 * 4)), (15, hace(24 * 3)), (16, hace(24 * 2))])
    con.commit()
    dt_r, desde_r = dt_de_alineaciones(con, 700)
    check("tres terminados después de la última alineación → la alineación no cuenta",
          dt_r is None and desde_r is None, (dt_r, desde_r))
    guardar_entrenador(con, 700, carrera)
    fila = con.execute("SELECT nombre, fuente FROM entrenadores WHERE team_id=700").fetchone()
    check("y el DT guardado vuelve a la carrera, con fuente coachs, no al del banco viejo",
          fila and fila[1] == "coachs" and fila[0] != "P. Guardiola", fila)
    con.execute("INSERT INTO fixtures (id, date, status_short, league_id, home_team_id) VALUES (17, ?, 'NS', 239, 700)",
                (hace(-24),))
    con.execute("INSERT INTO alineaciones (fixture_id, team_id, entrenador) VALUES (16, 700, 'R. Dudamel')")
    con.commit()
    dt_r, _ = dt_de_alineaciones(con, 700)
    check("una alineación de uno de los últimos 3 terminados sí cuenta",
          dt_r == "R. Dudamel", dt_r)
    con.execute("DELETE FROM alineaciones WHERE fixture_id=16")
    con.execute("INSERT INTO alineaciones (fixture_id, team_id, entrenador) VALUES (17, 700, 'XI probable')")
    con.commit()
    check("un XI probable del próximo partido es lo más fresco que hay y también cuenta",
          dt_de_alineaciones(con, 700)[0] == "XI probable")
    con.execute("DELETE FROM alineaciones WHERE fixture_id=17")
    con.execute("DELETE FROM fixtures WHERE id IN (14, 15, 16, 17)")
    con.commit()

    # --- 2c. DT FRESCO PARA LA AGENDA: alineación del último partido + /coachs ---
    from backend.ingesta.jugadores import dt_agenda, ultimo_terminado
    from backend.ingesta import ficha_partido as ficha
    con = sqlite3.connect(":memory:")   # con el esquema REAL de alineaciones (el de la ficha)
    con.executescript("""
        CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT,
            league_id INTEGER, league_season INTEGER, home_team_id INTEGER, away_team_id INTEGER);
        CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO teams VALUES (700, 'Foco'), (701, 'Rival');
    """)
    ficha.preparar_tablas(con)
    preparar_tablas(con)
    prox = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id, league_season, home_team_id, away_team_id) "
                    "VALUES (?,?,?,?,?,?,?)",
                    [(20, prox, "NS", 281, 2026, 700, 701),
                     (21, hace(24 * 4), "FT", 281, 2026, 701, 700),
                     (22, hace(24 * 30), "FT", 281, 2026, 700, 701)])
    con.execute("INSERT INTO entrenadores (team_id, coach_id, nombre, desde, actualizado_en, fuente) "
                "VALUES (700, 9, 'S. Novoa', '2019-01-01', ?, 'coachs')", (hace(24 * 40),))
    con.commit()
    check("el último partido terminado es el de hace 4 días, no el NS", ultimo_terminado(con, 700) == 21)

    class Falso:
        limite, usadas = 1000, 0
        pedidos: list = []
        def quedan(self, n=1): return True
        def resumen(self): return "falso"
        def get(self, endpoint, params):
            self.usadas += 1
            self.pedidos.append((endpoint, dict(params)))
            if endpoint == "fixtures/lineups":
                return {"response": [{"team": {"id": 700}, "coach": {"name": "P. Guardiola"}, "formation": "4-3-3",
                                      "startXI": [{"player": {"id": 1, "name": "A", "number": 1, "pos": "G"}}],
                                      "substitutes": []},
                                     {"team": {"id": 701}, "coach": {"name": "Otro"}, "formation": "4-4-2",
                                      "startXI": [{"player": {"id": 2, "name": "B", "number": 1, "pos": "G"}}],
                                      "substitutes": []}]}
            if endpoint == "coachs":
                return {"response": [{"id": 9, "name": "S. Novoa", "career": [{"team": {"id": 700}, "start": "2019-01-01", "end": None}]}]}
            return {"response": []}
    falso = Falso()
    r = dt_agenda(falso, con, dias=2, edad_dias=7)
    lineups = [p for e, p in falso.pedidos if e == "fixtures/lineups"]
    check("pide la alineación del último partido terminado de cada equipo de la agenda (una vez por fixture compartido)",
          lineups == [{"fixture": 21}], falso.pedidos)
    check("y /coachs del equipo con registro viejo (40 días > 7)",
          ("coachs", {"team": 700}) in falso.pedidos, falso.pedidos)
    fila = con.execute("SELECT nombre, fuente, desde FROM entrenadores WHERE team_id=700").fetchone()
    check("el DT queda el del banco aunque /coachs siga trayendo al saliente: fuente alineacion, desde = ese partido",
          fila and fila[0] == "P. Guardiola" and fila[1] == "alineacion" and fila[2] == hace(24 * 4)[:10], fila)
    check("el resumen cuenta el cambio", r["coachs"] >= 1 and any(c["equipo"] == 700 for c in r["cambiados"]), r)
    antes = len(falso.pedidos)
    dt_agenda(falso, con, dias=2, edad_dias=7)
    check("una segunda pasada no vuelve a pedir nada: alineación ya guardada y registro fresco",
          len(falso.pedidos) == antes, falso.pedidos[antes:])
    # SANTA FE–CALI (22/09): la liga deja de publicar onces. El equipo juega
    # tres partidos más sin alineación capturada; el registro dice «P.
    # Guardiola · alineacion» y es de hoy, pero ese banco es de hace meses.
    # Sin la regla, `viejo` y `contradice` son False y nadie lo rehace.
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id, league_season, home_team_id, away_team_id) "
                    "VALUES (?,?,'FT',281,2026,700,701)",
                    [(23, hace(24 * 3)), (24, hace(24 * 2)), (25, hace(24 * 1))])
    con.commit()
    falso.sin_onces = True
    _get = falso.get
    def get_sin_onces(endpoint, params, _g=_get):
        if endpoint == "fixtures/lineups" and params.get("fixture", 0) > 22:
            falso.usadas += 1
            falso.pedidos.append((endpoint, dict(params)))
            return {"response": []}
        return _g(endpoint, params)
    falso.get = get_sin_onces
    from backend.ingesta.jugadores import dt_de_alineaciones as _dta
    check("con tres terminados sin alineación después, la alineación vieja ya no cuenta",
          _dta(con, 700) == (None, None), _dta(con, 700))
    r3 = dt_agenda(falso, con, dias=2, edad_dias=7)
    fila = con.execute("SELECT nombre, fuente FROM entrenadores WHERE team_id=700").fetchone()
    check("un registro `alineacion` sin alineación fresca que lo sostenga se rehace con /coachs aunque sea de hoy",
          fila and fila[1] == "coachs" and fila[0] == "S. Novoa"
          and any(c["equipo"] == 700 and c["antes"] == "P. Guardiola" for c in r3["cambiados"]), (fila, r3))

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

    # --- 4. los equipos de interés: entran por el torneo, no por su liga ----
    # (deuda 6 de CLAUDE.md, corrida del 16/09: Beşiktaş y NEC con el
    # calendario vacío y cuatro planteles sin ingestar). El que juega la
    # edición vigente de un torneo internacional se sigue AUNQUE su NS
    # próximo sea en una liga fuera de LIGAS.
    from backend.ingesta.extractor import (
        LIGAS_INTERNACIONALES, equipos_de_interes, equipos_sin_liga_en_la_base,
        purgar_ns_sin_mantenimiento, _es_nuestro,
    )
    lejos = (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")
    con.executemany(
        "INSERT INTO fixtures (id, date, status_short, league_id, league_season, "
        "home_team_id, away_team_id) VALUES (?,?,?,?,?,?,?)",
        [(20, lejos, "NS", 3, 2026, 500, 501),      # Europa League 2026-27: Beşiktaş (500) vs Real Betis (501)
         (21, prox, "NS", 203, 2026, 500, 502),     # Süper Lig (fuera de LIGAS): Beşiktaş en 1 día
         (22, prox, "NS", 203, 2026, 503, 504),     # Süper Lig entre equipos que NO nos interesan
         (23, hace(24 * 400), "FT", 3, 2025, 600, 601),  # Europa League 2025-26: edición pasada
         (24, prox, "NS", 88, 2026, 600, 602)],     # Eredivisie del que ya no juega Europa
    )
    con.commit()
    interes = equipos_de_interes(con)
    check("equipos de interés = los de la edición VIGENTE del torneo internacional",
          interes == {500, 501}, sorted(interes))
    check("la edición pasada no cuenta", not ({600, 601} & interes), sorted(interes))
    check("un fixture de liga desconocida entra si lo juega un equipo de interés",
          _es_nuestro({"league": {"id": 203}, "teams": {"home": {"id": 500}, "away": {"id": 502}}}, interes))
    check("y no entra si no lo juega ninguno",
          not _es_nuestro({"league": {"id": 203}, "teams": {"home": {"id": 503}, "away": {"id": 504}}}, interes))
    check("los de LIGAS entran como siempre",
          _es_nuestro({"league": {"id": 128}, "teams": {"home": {"id": 1}, "away": {"id": 2}}}, set()))
    ids = {t for t, _ in equipos_pendientes(con, 3, 168)}
    check("el plantel del equipo de interés se pide aunque su NS próximo sea en su liga fuera del padrón",
          500 in ids, sorted(ids))
    check("su rival de esa liga y los otros de la Süper Lig siguen fuera",
          not ({502, 503, 504} & ids), sorted(ids))
    check("el que ya no juega Europa no entra por su Eredivisie", 600 not in ids, sorted(ids))
    faltan = equipos_sin_liga_en_la_base(con, interes)
    check("sin partido doméstico en la base, a los dos se les pide la temporada (1 request, una vez)",
          faltan == [(500, 2026), (501, 2026)], faltan)
    con.execute("INSERT INTO fixtures (id, date, status_short, league_id, league_season, "
                "home_team_id, away_team_id) VALUES (25, ?, 'FT', 140, 2026, 501, 505)", (hace(72),))
    con.commit()
    check("con su LaLiga en la base, el Betis sale de esa lista; Beşiktaş (Süper Lig fuera de LIGAS) queda",
          equipos_sin_liga_en_la_base(con, interes) == [(500, 2026)])
    purgados = purgar_ns_sin_mantenimiento(con)
    quedan = {r[0] for r in con.execute("SELECT id FROM fixtures WHERE status_short='NS'")}
    check("la purga de NS fuera de la lista respeta los partidos del equipo de interés",
          21 in quedan and 22 not in quedan and 24 not in quedan and purgados == 2,
          (sorted(quedan), purgados))
    check("los torneos internacionales de clubes son una sola lista (la agenda la importa)",
          LIGAS_INTERNACIONALES == {2, 3, 848, 13, 11})

    # la temporada doméstica del equipo de interés se pide UNA vez (marcador),
    # con /fixtures?team=&season= y sin tocar el guardado real (stub)
    import json as _json, tempfile as _tmp
    from backend.ingesta import extractor as _ext

    class ClienteSanar:
        limite, usadas = 10**6, 0
        pedidos: list = []

        def quedan(self, n: int = 1) -> bool:
            return True

        def paginado(self, endpoint, params, tope_paginas=0):
            self.usadas += 1
            self.pedidos.append((endpoint, dict(params)))
            return [{"fixture": {"id": 1}}, {"fixture": {"id": 2}}]

    guardados = []
    original = _ext.guardar_fixtures
    _ext.guardar_fixtures = lambda con_, filas: guardados.append(len(filas)) or len(filas)
    cwd = os.getcwd()
    with _tmp.TemporaryDirectory() as d:
        os.chdir(d)
        try:
            cl = ClienteSanar()
            n1 = _ext.sanar_equipos_interes(cl, con)
            n2 = _ext.sanar_equipos_interes(cl, con)
            marca = _json.load(open(_ext.SANARE_PATH, encoding="utf-8"))
        finally:
            os.chdir(cwd)
            _ext.guardar_fixtures = original
    check("sanar equipos: la vigente y DESPUÉS la anterior (/fixtures?team=500&season=2026, 2025)",
          n1 == 4 and cl.pedidos == [("fixtures", {"team": 500, "season": 2026}),
                                     ("fixtures", {"team": 500, "season": 2025})] and guardados == [2, 2],
          (n1, cl.pedidos, guardados))
    check("la segunda corrida no lo repite (marcador por equipo:temporada)",
          n2 == 0 and cl.usadas == 2 and sorted(marca) == ["500:2025", "500:2026"], (n2, cl.usadas, marca))

    # la vuelta atrás por env existe
    jug.JUGADORES_TODAS_LIGAS = True
    try:
        ids = {t for t, _ in equipos_pendientes(con, 3, 168)}
        check("SAD_JUGADORES_TODAS_LIGAS=1 devuelve el padrón completo",
              {200, 300, 400} <= ids, sorted(ids))
    finally:
        jug.JUGADORES_TODAS_LIGAS = False

    # --- un error de la API NO es «sin datos» (24/09: 65 equipos sellados
    #     como vacíos el mismo día, Rennes y Shakhtar incluidos) -----------
    from backend.ingesta.jugadores import ingestar_equipo

    class ClienteVacio:
        limite, usadas = 10**6, 0

        def __init__(self, falla: bool):
            self.falla, self.fallos = falla, 0

        def quedan(self, n: int = 1) -> bool:
            return True

        def paginado(self, endpoint, params, tope_paginas=0):
            self.usadas += 1
            if self.falla:
                self.fallos += 1  # lo que hace Cliente._pedir al agotar los intentos
            return []

        def get(self, endpoint, params):
            self.usadas += 1
            return {"response": []}

    con.execute("DELETE FROM plantillas_meta WHERE team_id IN (7001, 7002)")
    ok = ingestar_equipo(ClienteVacio(falla=True), con, 7001, 2026)
    check("/players que FALLA: no se sella (la próxima corrida lo reintenta)",
          ok and not con.execute("SELECT 1 FROM plantillas_meta WHERE team_id=7001").fetchone())
    ingestar_equipo(ClienteVacio(falla=False), con, 7002, 2026)
    check("/players que responde vacío de verdad: se sella con con_datos=0 (TTL largo)",
          con.execute("SELECT con_datos FROM plantillas_meta WHERE team_id=7002").fetchone() == (0,))

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
