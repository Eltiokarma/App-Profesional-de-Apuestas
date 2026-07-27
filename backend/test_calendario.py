"""Test del calendario SAD (backend/calendario.py) — sin red y sin IA.

Cada etiqueta del bloque G2 tiene un criterio NUMÉRICO en el protocolo. Este
test comprueba que se aplica ese criterio y no una impresión: si una etiqueta
se dispara sin el dato que la sostiene, el análisis hereda una mentira barata.

    python -m backend.test_calendario
"""
import os
import sqlite3
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="sad-cal-")
os.environ["SAD_DATA_DIR"] = _TMP

from backend import calendario  # noqa: E402

fallos = 0
FOCO, ASCENDIDO, CRISIS, LOCALON, VISITANTE_MALO, BLOQUE, VECINO = 1, 2, 3, 4, 5, 6, 7
LIGA, TEMP = 281, 2026


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
            league_id INTEGER, league_season INTEGER, league_round TEXT, venue_city TEXT,
            home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
            fulltime_home INTEGER, fulltime_away INTEGER);
        CREATE TABLE entrenadores (team_id INTEGER, coach_id INTEGER, nombre TEXT, desde TEXT);
        CREATE TABLE alineaciones (fixture_id INTEGER, team_id INTEGER, formacion TEXT,
            player_id INTEGER, titular INTEGER);
    """)
    con.executemany("INSERT INTO teams (id, name) VALUES (?,?)", [
        (FOCO, "Equipo Foco"), (ASCENDIDO, "Recién Subido"), (CRISIS, "En Caída"),
        (LOCALON, "Fortín"), (VISITANTE_MALO, "Malo Fuera"), (BLOQUE, "Muro FC"), (VECINO, "Vecino CF")])
    con.execute("INSERT INTO leagues (id, name) VALUES (?, 'Liga Test')", (LIGA,))

    fid = 1000

    def jugado(local, visita, gh, ga, fecha, ciudad="Ciudad A", temporada=TEMP):
        nonlocal fid
        fid += 1
        con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                    "venue_city, home_team_id, away_team_id, goals_home, goals_away, fulltime_home, fulltime_away) "
                    "VALUES (?,?, 'FT','Match Finished', ?,?,?,?,?,?,?,?,?)",
                    (fid, fecha, LIGA, temporada, ciudad, local, visita, gh, ga, gh, ga))

    def programado(local, visita, fecha, ciudad="Ciudad A"):
        nonlocal fid
        fid += 1
        con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                    "venue_city, home_team_id, away_team_id) VALUES (?,?, 'NS','Not Started', ?,?,?,?,?)",
                    (fid, fecha, LIGA, TEMP, ciudad, local, visita))
        return fid

    # historia del foco (para el descanso) y de cada rival
    jugado(FOCO, VECINO, 1, 1, "2026-07-20 20:00:00")

    # ASCENDIDO: sin partidos en esta liga la temporada pasada, pero con historia
    jugado(ASCENDIDO, VECINO, 0, 0, "2025-05-01 20:00:00", temporada=TEMP - 1)
    con.execute("UPDATE fixtures SET league_id=999 WHERE home_team_id=? AND league_season=?",
                (ASCENDIDO, TEMP - 1))  # jugó, pero en OTRA categoría
    # (antes de la racha de CRISIS: un empate en medio la cortaría, y con razón)
    jugado(ASCENDIDO, CRISIS, 1, 1, "2026-07-01 20:00:00")

    # CRISIS: 3 derrotas seguidas
    for i, f in enumerate(["2026-07-05", "2026-07-12", "2026-07-19"]):
        jugado(VECINO, CRISIS, 2, 0, f + " 20:00:00")

    # LOCAL FUERTE: 5 de local, 4 ganados (80%)
    for i, f in enumerate(["2026-05-01", "2026-05-08", "2026-05-15", "2026-05-22", "2026-05-29"]):
        jugado(LOCALON, VECINO, 1 if i < 4 else 0, 0 if i < 4 else 1, f + " 20:00:00", "Ciudad F")

    # VISITA DÉBIL: 5 de visita, 0 ganados
    for f in ["2026-05-02", "2026-05-09", "2026-05-16", "2026-05-23", "2026-05-30"]:
        jugado(VECINO, VISITANTE_MALO, 2, 0, f + " 20:00:00")

    # BLOQUE BAJO: formación 5-3-2 dominante
    for i in range(3):
        fid += 1
        con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                    "home_team_id, away_team_id, goals_home, goals_away, fulltime_home, fulltime_away) "
                    "VALUES (?,?, 'FT','Match Finished', ?,?,?,?,1,1,1,1)",
                    (fid, f"2026-06-0{i + 1} 20:00:00", LIGA, TEMP, BLOQUE, VECINO))
        con.execute("INSERT INTO alineaciones (fixture_id, team_id, formacion, player_id, titular) "
                    "VALUES (?,?, '5-3-2', ?, 1)", (fid, BLOQUE, 900 + i))

    # próximos del foco, uno por rival a etiquetar
    programado(FOCO, ASCENDIDO, "2026-07-29 20:00:00")
    programado(FOCO, CRISIS, "2026-08-02 20:00:00")
    programado(LOCALON, FOCO, "2026-08-09 20:00:00", "Ciudad F")
    programado(FOCO, VISITANTE_MALO, "2026-08-16 20:00:00")
    con.commit()
    con.close()


def etiquetas(cal, rival):
    for c in cal:
        if c["rival"] == rival:
            return {e["codigo"]: e for e in c["etiquetas"]}
    return {}


def main():
    montar()
    cal = calendario.calendario_de(FOCO, n=4)
    check("devuelve los próximos partidos en orden", [c["rival"] for c in cal] ==
          ["Recién Subido", "En Caída", "Fortín", "Malo Fuera"], [c["rival"] for c in cal])
    check("marca local y visitante", [c["condicion"] for c in cal] == ["L", "L", "V", "L"],
          [c["condicion"] for c in cal])
    check("calcula los días entre partidos", cal[1]["diasDescanso"] == 4, cal[1]["diasDescanso"])

    e = etiquetas(cal, "Recién Subido")
    check("RECIÉN ASCENDIDO: sin partidos en esta liga la temporada pasada",
          "RECIEN_ASCENDIDO" in e, list(e))
    check("y avisa de la cuarentena de sus K", "R-KT.2" in e.get("RECIEN_ASCENDIDO", {}).get("nota", ""), e)

    e = etiquetas(cal, "En Caída")
    check("EN CRISIS con 3 derrotas seguidas", "EN_CRISIS" in e, list(e))
    check("y el dato que lo sostiene", "3 derrotas" in e.get("EN_CRISIS", {}).get("dato", ""), e)

    e = etiquetas(cal, "Fortín")
    check("LOCAL FUERTE solo cuando el rival juega en casa", "LOCAL_FUERTE" in e, list(e))
    check("con su porcentaje real (80%)", "80%" in e.get("LOCAL_FUERTE", {}).get("dato", ""), e)

    e = etiquetas(cal, "Malo Fuera")
    check("VISITA DÉBIL cuando el rival viene de visita", "VISITA_DEBIL" in e, list(e))
    check("y NO se le cuelga LOCAL FUERTE", "LOCAL_FUERTE" not in e, list(e))

    # el criterio manda: sin muestra suficiente no se etiqueta
    cal_pocos = calendario.calendario_de(FOCO, n=1)
    check("con un solo partido pedido, devuelve uno", len(cal_pocos) == 1, len(cal_pocos))

    # BLOQUE BAJO se calcula de la formación real capturada
    et_bloque = calendario.etiquetas_de_rival(BLOQUE, True, 281, 2026, "2026-08-20", None)
    codigos = {x["codigo"] for x in et_bloque}
    check("BLOQUE BAJO desde la formación dominante (5-3-2)", "BLOQUE_BAJO" in codigos, codigos)

    # CLÁSICO: mismo municipio, y se declara parcial
    et_vecino = calendario.etiquetas_de_rival(LOCALON, True, 281, 2026, "2026-08-20", "Ciudad F")
    cl = next((x for x in et_vecino if x["codigo"] == "CLASICO"), None)
    check("CLÁSICO por derbi de ciudad", cl is not None, [x["codigo"] for x in et_vecino])
    check("y se marca PARCIAL (una rivalidad nacional no sale de los datos)",
          bool(cl and cl.get("parcial")), cl)

    # el bloque G del EFE relleno por código: lo que antes copiaba el modelo
    items = calendario.items_para_efe(FOCO)
    check("items_para_efe: un item por partido con la forma del esquema",
          len(items) == 4 and all(set(i) == {"rival", "fecha", "condicion", "etiquetas", "posicion", "nota"}
                                  for i in items), items[:1])
    crisis = next((i for i in items if i["rival"] == "En Caída"), {})
    check("items_para_efe: la etiqueta lleva su dato entre paréntesis",
          any("3 derrotas" in e for e in crisis.get("etiquetas", [])), crisis)
    check("items_para_efe: posición desconocida va 0, no null (lo pide el esquema)",
          all(isinstance(i["posicion"], int) for i in items), [i["posicion"] for i in items])

    # el texto para los skills: sin él, el modelo pagaría por deducir esto
    txt = calendario.texto_para_skills(FOCO)
    check("el texto para skills trae las etiquetas con su dato",
          "NO lo investigues" in txt and "EN CRISIS" in txt and "3 derrotas" in txt, txt[:200])
    check("un equipo sin fixtures da texto vacío (no se inventa)",
          calendario.texto_para_skills(99999) == "", calendario.texto_para_skills(99999))

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
