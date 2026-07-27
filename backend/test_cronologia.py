"""Test de la cronología SAD (backend/cronologia.py) — sin red y sin IA.

Los partidos del timeline dejaron de pagarse: se calculan de sad.db. Este test
comprueba que lo calculado sea EXACTAMENTE lo que estaba en la base —marcador,
jornada, condición, enfrentamiento directo— porque un evento mal armado es peor
que uno caro: entra al timeline con cara de dato confirmado.

    python -m backend.test_cronologia
"""
import os
import sqlite3
import sys
import tempfile
from datetime import date, timedelta

_TMP = tempfile.mkdtemp(prefix="sad-crono-")
os.environ["SAD_DATA_DIR"] = _TMP

from backend import cronologia  # noqa: E402

fallos = 0
A, B, C = 1, 2, 3
D, E = 4, 5          # el par del test del motor (fechas relativas a hoy)
LIGA, TEMP = 281, 2026
DESDE, HASTA = "2026-01-01", "2026-06-30"


def hace(dias: int) -> str:
    return (date.today() - timedelta(days=dias)).isoformat()


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def montar():
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.executescript("""
        CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE leagues (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT, status_long TEXT,
            league_id INTEGER, league_season INTEGER, league_round TEXT,
            home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
            fulltime_home INTEGER, fulltime_away INTEGER);
    """)
    con.executemany("INSERT INTO teams (id, name) VALUES (?,?)",
                    [(A, "Equipo A"), (B, "Equipo B"), (C, "Tercero FC"),
                     (D, "Motor D"), (E, "Motor E")])
    con.execute("INSERT INTO leagues (id, name) VALUES (?, 'Liga Test')", (LIGA,))

    fid = 500

    def jugado(local, visita, gh, ga, fecha, ronda="Regular Season - 1",
               ft=None, estado=("FT", "Match Finished")):
        nonlocal fid
        fid += 1
        fh, fa = (gh, ga) if ft is None else ft
        con.execute(
            "INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
            "league_round, home_team_id, away_team_id, goals_home, goals_away, fulltime_home, fulltime_away) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (fid, fecha, estado[0], estado[1], LIGA, TEMP, ronda, local, visita, gh, ga, fh, fa))

    # A: victoria de local, derrota de visita, empate; y una victoria más tarde
    jugado(A, C, 3, 1, "2026-02-10 20:00:00", "Regular Season - 3")
    jugado(C, A, 2, 0, "2026-03-05 20:00:00", "Regular Season - 6")
    jugado(A, C, 1, 1, "2026-04-01 20:00:00", "Apertura - 11")
    jugado(A, C, 2, 0, "2026-05-20 20:00:00", "Final")
    # B: una sola victoria en el período
    jugado(B, C, 4, 0, "2026-02-20 20:00:00", "Regular Season - 4")
    # enfrentamiento directo A vs B
    jugado(A, B, 1, 2, "2026-06-10 20:00:00", "Regular Season - 18")
    # fuera de ventana (no debe aparecer) y no terminado (tampoco)
    jugado(A, C, 9, 0, "2025-11-01 20:00:00")
    jugado(A, C, 0, 0, "2026-06-25 20:00:00", estado=("NS", "Not Started"))
    # regla de 90': el resultado que manda es fulltime, no goals (que trae penales)
    jugado(B, C, 5, 4, "2026-06-15 20:00:00", "Final", ft=(1, 1), estado=("PEN", "Match Finished"))

    # el par del test del motor: fechas RELATIVAS a hoy, porque generar_timeline
    # usa la ventana real de 6 meses (un test atado a 2026 caducaría solo)
    jugado(D, C, 2, 0, hace(90) + " 20:00:00", "Regular Season - 5")
    jugado(C, D, 0, 3, hace(60) + " 20:00:00", "Regular Season - 8")
    jugado(E, C, 1, 1, hace(45) + " 20:00:00", "Regular Season - 9")
    jugado(D, E, 2, 2, hace(20) + " 20:00:00", "Regular Season - 12")  # cruce directo
    con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, "
                "league_season, home_team_id, away_team_id) VALUES (900, ?, 'NS', 'Not Started', ?, ?, ?, ?)",
                ((date.today() + timedelta(days=3)).isoformat() + " 20:00:00", LIGA, TEMP, D, E))
    con.commit()
    con.close()


def motor_del_timeline():
    """El ahorro real: qué le llega al modelo y qué se le descarta al volver.

    Se sustituye `cliente.analizar` (aquí no se paga nada) para inspeccionar el
    payload y devolver una respuesta que DESOBEDECE la orden —emite partidos y
    stats propios—, que es justo el caso que el código tiene que resolver."""
    from backend.analisis import db as efedb, motor
    from backend.analisis.esquemas import TIMELINE, ajustar

    capturado = {}

    def falso_analizar(payload, esquema, con_busqueda, **kw):
        capturado.update(payload=payload, con_busqueda=con_busqueda,
                         max_busquedas=kw.get("max_busquedas"))
        return ajustar({
            "titulo": "Motor D vs Motor E",
            "equipos": [{"nombre": "Motor E", "lado": "derecha", "color": "#E5484D",
                         "stats": {"posicion": 99, "puntos": 99, "ultima_victoria": "inventada"}},
                        {"nombre": "Motor D", "lado": "izquierda", "color": "#5B8DEF"}],
            # un partido copiado (contra la orden) + dos eventos institucionales
            "eventos": [
                {"fecha": hace(70), "equipo": "Motor D", "tipo": "resultado",
                 "titulo": "COPIADO POR EL MODELO", "marcador": "9-9"},
                {"fecha": hace(75), "equipo": "Motor D", "tipo": "tecnico",
                 "titulo": "Cambio de DT", "detalle": "asume el interino"},
                {"fecha": hace(30), "equipo": "Motor E", "tipo": "sancion",
                 "titulo": "Clausura parcial del estadio"},
            ],
            "agrupacion": "mes",
            "narrativa": "arco del semestre",
            "fuentes": ["prensa"],
        }, TIMELINE), {}

    motor.cliente.analizar = falso_analizar
    motor.cliente.hay_clave = lambda: True
    dto = motor.generar_timeline(900)
    p, r = capturado["payload"], dto["resultado"]

    check("el payload lleva la orden de no copiar partidos ni stats",
          p.get("bloque_partidos") == cronologia.ORDEN_PARA_SKILLS, sorted(p))
    check("y el balance del período en vez de la lista de partidos",
          p["datos_cacheados"]["Motor D"]["resultados_db"].startswith("2G 0E 0D"),
          p["datos_cacheados"]["Motor D"]["resultados_db"])
    check("el presupuesto de búsquedas baja al tope de lo institucional",
          capturado["max_busquedas"] == motor.cliente.BUSQUEDAS_TIMELINE_CALC,
          capturado["max_busquedas"])

    tipos = [e["tipo"] for e in r["eventos"]]
    check("los partidos calculados entran al timeline",
          tipos.count("resultado") == 2 and tipos.count("empate") == 2, tipos)
    check("el partido que el modelo copió igual se descarta (manda nuestro marcador)",
          all(e["titulo"] != "COPIADO POR EL MODELO" for e in r["eventos"])
          and all(e["marcador"] != "9-9" for e in r["eventos"]),
          [e["titulo"] for e in r["eventos"]])
    check("lo institucional del modelo se conserva",
          {e["titulo"] for e in r["eventos"]} >= {"Cambio de DT", "Clausura parcial del estadio"},
          [e["titulo"] for e in r["eventos"]])
    check("el timeline queda en orden cronológico estricto tras la fusión",
          [e["fecha"] for e in r["eventos"]] == sorted(e["fecha"] for e in r["eventos"]),
          [e["fecha"] for e in r["eventos"]])
    check("el cruce directo aparece una sola vez y centrado",
          [e["equipo"] for e in r["eventos"]].count("ambos") == 1,
          [(e["fecha"], e["equipo"]) for e in r["eventos"]])

    stats = {e["nombre"]: e["stats"] for e in r["equipos"]}
    check("stats: las cifras inventadas por el modelo se pisan con las nuestras",
          stats["Motor E"]["posicion"] != 99 and stats["Motor E"]["ultima_victoria"] != "inventada",
          stats["Motor E"])
    check("stats: se rellenan por NOMBRE, no por posición en la lista",
          stats["Motor D"]["ultima_victoria"].startswith(hace(60)), stats["Motor D"])
    check("los colores del modelo no se tocan",
          {e["nombre"]: e["color"] for e in r["equipos"]}["Motor D"] == "#5B8DEF", r["equipos"])
    check("la fuente de lo calculado se declara junto a las del modelo",
          cronologia.FUENTE in r["fuentes"] and "prensa" in r["fuentes"], r["fuentes"])

    # la despensa: solo lo institucional. Sellar los partidos sería congelar
    # mañana lo que hoy se recalcula gratis.
    frescos, _ = efedb.investigacion_de("Motor D")
    guardados = frescos.get("timeline_eventos") or []
    check("la despensa guarda lo institucional y NINGÚN partido",
          guardados and all(e["tipo"] not in cronologia.TIPOS_PARTIDO for e in guardados),
          [e.get("tipo") for e in guardados])


def main():
    montar()
    ev_a = cronologia.eventos_de(A, "Equipo A", DESDE, HASTA)

    check("solo partidos terminados dentro de la ventana",
          [e["fecha"] for e in ev_a] ==
          ["2026-02-10", "2026-03-05", "2026-04-01", "2026-05-20", "2026-06-10"],
          [e["fecha"] for e in ev_a])
    check("orden cronológico ascendente (lo exige el esquema TIMELINE)",
          [e["fecha"] for e in ev_a] == sorted(e["fecha"] for e in ev_a))

    check("victoria de local: tipo, marcador y rival",
          ev_a[0]["tipo"] == "resultado" and ev_a[0]["marcador"] == "3-1"
          and "ante Tercero FC" in ev_a[0]["titulo"] and ev_a[0]["detalle"].startswith("Local"),
          ev_a[0])
    check("derrota de visita: el marcador va desde el equipo, no desde el local",
          ev_a[1]["tipo"] == "derrota" and ev_a[1]["marcador"] == "0-2"
          and ev_a[1]["detalle"].startswith("Visitante"), ev_a[1])
    check("empate", ev_a[2]["tipo"] == "empate" and ev_a[2]["marcador"] == "1-1", ev_a[2])

    check("jornada desde league_round", ev_a[0]["jornada"] == 3 and ev_a[2]["jornada"] == 11,
          [e["jornada"] for e in ev_a])
    check("ronda sin número (Final) → jornada 0, no una inventada",
          ev_a[3]["jornada"] == 0, ev_a[3])
    check("cada evento declara su fuente y no va como aproximado",
          all(e["fuente"] == cronologia.FUENTE and e["aproximada"] is False for e in ev_a))
    check("la liga viaja en el detalle", all("Liga Test" in e["detalle"] for e in ev_a[:3]),
          [e["detalle"] for e in ev_a[:3]])

    # regla de 90': PEN 5-4 con fulltime 1-1 es EMPATE en el timeline
    ev_b = cronologia.eventos_de(B, "Equipo B", DESDE, HASTA)
    pen = next((e for e in ev_b if e["fecha"] == "2026-06-15"), {})
    check("regla de 90': fulltime manda sobre goals (PEN 5-4 con 1-1 → empate)",
          pen.get("tipo") == "empate" and pen.get("marcador") == "1-1", pen)

    # enfrentamiento directo: uno solo, centrado, destacado
    ev_a_vs_b = cronologia.eventos_de(A, "Equipo A", DESDE, HASTA, rival_id=B)
    directo = [e for e in ev_a_vs_b if e["equipo"] == "ambos"]
    check("el cruce entre los dos equipos sale como 'ambos'", len(directo) == 1, directo)
    check("con el marcador del partido y destacado",
          directo and directo[0]["marcador"] == "1-2" and directo[0]["destacado"]
          and "Equipo A 1-2 Equipo B" == directo[0]["titulo"], directo)

    juntos = cronologia.eventos_del_partido(A, "Equipo A", B, "Equipo B", DESDE, HASTA)
    check("los dos equipos juntos, sin duplicar el enfrentamiento directo",
          len([e for e in juntos if e["equipo"] == "ambos"]) == 1,
          [(e["fecha"], e["equipo"]) for e in juntos])
    check("y en orden cronológico estricto",
          [e["fecha"] for e in juntos] == sorted(e["fecha"] for e in juntos),
          [e["fecha"] for e in juntos])
    check("ningún evento calculado es institucional (eso se sigue pagando)",
          all(e["tipo"] in cronologia.TIPOS_PARTIDO for e in juntos),
          {e["tipo"] for e in juntos})

    # stats de la barra superior: de la tabla, no del modelo
    st = cronologia.stats_de(A, LIGA, TEMP, DESDE, HASTA)
    check("stats: última victoria del período con fecha, marcador y rival",
          st["ultima_victoria"].startswith("2026-05-20 2-0 vs Tercero FC"), st)
    check("stats: posición y puntos son enteros de la tabla calculada",
          isinstance(st["posicion"], int) and isinstance(st["puntos"], int) and st["puntos"] > 0, st)
    sin_liga = cronologia.stats_de(A, None, None, DESDE, HASTA)
    check("sin liga/temporada la posición va en 0 (hueco declarado, no invento)",
          sin_liga["posicion"] == 0 and sin_liga["puntos"] == 0, sin_liga)
    check("un equipo sin partidos no inventa última victoria",
          cronologia.stats_de(99999, None, None, DESDE, HASTA)["ultima_victoria"] == "")

    # el orden tolera las fechas aproximadas que sí puede emitir el modelo
    mezcla = cronologia.ordenar([{"fecha": "2026-03-15"}, {"fecha": "~2026-03"},
                                 {"fecha": "2026-02-01"}])
    check("ordenar(): '~2026-03' cae al principio de su mes, no al final de todo",
          [e["fecha"] for e in mezcla] == ["2026-02-01", "~2026-03", "2026-03-15"], mezcla)

    # el resumen que reemplaza la lista de resultados en el prompt
    resumen = cronologia.resumen_para_skills(juntos, "Equipo A")
    check("resumen para el prompt: balance G/E/D del período",
          resumen.startswith("2G 1E 1D en el período"), resumen)
    check("y los últimos partidos, no los cuarenta",
          resumen.count(" · ") <= 5 and "2026-05-20" in resumen, resumen)
    check("un equipo sin eventos da resumen vacío (no se inventa un balance)",
          cronologia.resumen_para_skills(juntos, "Nadie FC") == "")

    # la orden que viaja al modelo tiene que decir las dos cosas
    check("la orden al modelo prohíbe copiar partidos y stats",
          "resultado/derrota/empate" in cronologia.ORDEN_PARA_SKILLS
          and "stats" in cronologia.ORDEN_PARA_SKILLS
          and "institucional" in cronologia.ORDEN_PARA_SKILLS)

    # ventana por defecto: 6 meses, el default del protocolo TIMELINE
    d, h = cronologia.ventana(hasta="2026-07-01")
    check("ventana(): cierra en la fecha dada y abre 182 días antes (6 meses)",
          h == "2026-07-01" and (date.fromisoformat(h) - date.fromisoformat(d)).days == 182,
          (d, h))

    motor_del_timeline()

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
