"""Test del DTP (backend/analisis/motor.py, fase B) — sin red y sin API.

Blinda las dos reglas que le dan valor a la cadena y que son fáciles de romper
sin que salte ningún error:

1. **Anti-hindsight**: el cierre de N−1 solo contrasta contra un pronóstico
   escrito ANTES de que N−1 se jugara. Sin él, veredicto vacío.
2. **Sin búsqueda web**: el DTP razona sobre la ficha de partido; lo que falte
   se declara. Si un día alguien pone con_busqueda=True, esto lo caza.

    python -m backend.test_dtp
"""
import os
import sqlite3
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="sad-dtp-")
os.environ["SAD_DATA_DIR"] = _TMP

from backend.analisis import db as efedb  # noqa: E402
from backend.analisis import motor  # noqa: E402
from backend.analisis.esquemas import DTP, ajustar  # noqa: E402
from backend.ingesta.ficha_partido import guardar_alineaciones, guardar_eventos, preparar_tablas  # noqa: E402

fallos = 0
FOCO, RIVAL, OTRO = 100, 200, 300


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


LINEUPS = [
    {"team": {"id": FOCO}, "coach": {"name": "DT Foco"}, "formation": "4-3-3",
     "startXI": [{"player": {"id": 1 + i, "name": f"J{i}", "number": i + 1,
                             "pos": "G" if i == 0 else "D" if i < 5 else "M" if i < 8 else "F",
                             "grid": f"{1 if i == 0 else 2 if i < 5 else 3 if i < 8 else 4}:{(i % 4) + 1}"}}
                 for i in range(11)],
     "substitutes": []},
    {"team": {"id": RIVAL}, "coach": {"name": "DT Rival"}, "formation": "3-5-2",
     "startXI": [{"player": {"id": 51, "name": "R1", "number": 1, "pos": "G", "grid": "1:1"}}],
     "substitutes": []},
]
EVENTOS = [{"time": {"elapsed": 34, "extra": None}, "team": {"id": RIVAL},
            "player": {"id": 51, "name": "R1"}, "assist": {"id": None, "name": None},
            "type": "Goal", "detail": "Normal Goal"}]


def sad() -> sqlite3.Connection:
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.executescript("""
        CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS leagues (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT,
            status_long TEXT, league_id INTEGER, league_season INTEGER, home_team_id INTEGER,
            away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER);
    """)
    preparar_tablas(con)
    return con


def montar():
    con = sad()
    con.executemany("INSERT OR REPLACE INTO teams (id, name) VALUES (?,?)",
                    [(FOCO, "Equipo Foco"), (RIVAL, "Equipo Rival"), (OTRO, "Otro Equipo")])
    con.execute("INSERT OR REPLACE INTO leagues (id, name) VALUES (1,'Liga Test')")
    con.executemany(
        "INSERT OR REPLACE INTO fixtures (id, date, status_short, status_long, league_id, "
        "league_season, home_team_id, away_team_id, goals_home, goals_away) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [(10, "2026-07-05 20:00:00", "FT", "Match Finished", 1, 2026, FOCO, OTRO, 2, 0),
         (11, "2026-07-12 20:00:00", "FT", "Match Finished", 1, 2026, OTRO, FOCO, 1, 1),  # el N−1
         (12, "2026-07-19 20:00:00", "NS", "Not Started", 1, 2026, FOCO, RIVAL, None, None)],  # el N
    )
    guardar_alineaciones(con, 11, LINEUPS)
    guardar_eventos(con, {"fixture_id": 11, "eventos": EVENTOS})
    con.commit()
    con.close()


def main():
    montar()

    # ── cronología de la cadena ────────────────────────────────────────────
    check("N = posición cronológica del equipo en la temporada",
          motor._partido_n(FOCO, "2026-07-19 20:00:00") == 3, motor._partido_n(FOCO, "2026-07-19 20:00:00"))
    ant = motor._anterior_de(FOCO, "2026-07-19 20:00:00")
    check("N−1 = último TERMINADO antes de la fecha", ant and ant["id"] == 11, ant and ant["id"])

    # ── el payload: sin web, con la ficha, y avisando de lo que falta ──────
    capturado = {}

    def falso_analizar(payload, esquema, con_busqueda, **kw):
        capturado.update(payload=payload, con_busqueda=con_busqueda, salida=kw.get("salida"))
        return ajustar({"apertura": {"m1": {"sistema": "4-3-3"},
                                     "m2": {"choque_sistemas": "4-3-3 vs 3-5-2"}},
                        "cierre": {"m4_goles": [{"gol": "0-1", "minuto": 34}],
                                   "m5": {"peligro_real": "dos llegadas"},
                                   "registro": {"veredicto": "parcial", "leccion": "x"}}}, DTP), {}

    motor.cliente.analizar = falso_analizar
    motor.cliente.hay_clave = lambda: True

    dto = motor.generar_dtp(12, FOCO)
    check("nunca busca en la web", capturado["con_busqueda"] is False, capturado["con_busqueda"])
    p = capturado["payload"]
    check("sin apertura previa → modo dtp_apertura", p["modo"] == "dtp_apertura", p["modo"])
    check("avisa de que no puede haber veredicto (anti-hindsight)",
          "aviso_cadena" in p, sorted(p))
    check("declara lo que falta en vez de inventarlo",
          "apertura_previa" in p["campos_faltantes"] and "xi_oficial_n" in p["campos_faltantes"],
          p["campos_faltantes"])
    check("lleva la ficha del partido anterior (M4)",
          p["datos_cacheados"]["anterior"]["ficha"]["capturada"] is True,
          p["datos_cacheados"]["anterior"])
    check("y su marcador real", p["datos_cacheados"]["anterior"]["partido"]["marcador"] == "1-1",
          p["datos_cacheados"]["anterior"]["partido"])
    check("con grid, no avisa de carriles aproximados", "aviso_carriles" not in p, sorted(p))

    # ── qué quedó escrito en la cadena ─────────────────────────────────────
    check("el DTO trae la apertura del partido N", bool(dto["resultado"]["apertura"]), dto)
    esl_n = efedb.eslabon("Equipo Foco", 3)
    check("la apertura se escribe en el eslabón N", bool(esl_n and esl_n["apertura"]), esl_n)
    esl_ant = efedb.eslabon("Equipo Foco", 2)
    check("el CIERRE se escribe en el eslabón N−1, no en el de N",
          bool(esl_ant and esl_ant["cierre"]) and not (esl_n or {}).get("cierre"),
          {"n-1": bool(esl_ant and esl_ant["cierre"]), "n": bool((esl_n or {}).get("cierre"))})
    check("un eslabón con cierre pero sin apertura NO cuenta como DTP listo",
          motor._dto_dtp(esl_ant) is None, esl_ant)

    # ── anti-hindsight: una apertura escrita antes NO se pisa ──────────────
    efedb.guardar_cadena("Equipo Foco", 2, "Otro Equipo", "2026-07-12", 11,
                         {"m1": {"sistema": "PRONÓSTICO ORIGINAL"}})
    efedb.guardar_cadena("Equipo Foco", 2, "Otro Equipo", "2026-07-12", 11,
                         {"m1": {"sistema": "REESCRITO DESPUÉS DEL PARTIDO"}})
    esl = efedb.eslabon("Equipo Foco", 2)
    check("la apertura previa no se puede reescribir a posteriori",
          esl["apertura"]["m1"]["sistema"] == "PRONÓSTICO ORIGINAL", esl["apertura"])

    # ── con apertura previa, el modo cambia a completo ─────────────────────
    capturado.clear()
    motor.generar_dtp(12, FOCO)
    p = capturado["payload"]
    check("con apertura previa → modo dtp_completo", p["modo"] == "dtp_completo", p["modo"])
    check("y la lleva en datos_cacheados para M5",
          p["datos_cacheados"]["apertura_previa"]["m1"]["sistema"] == "PRONÓSTICO ORIGINAL",
          p["datos_cacheados"]["apertura_previa"])
    check("ya no avisa de la cadena rota", "aviso_cadena" not in p, sorted(p))

    # ── sin grid: M2 no puede hablar de carriles y se le dice ──────────────
    con = sad()
    con.execute("UPDATE alineaciones SET grid=NULL WHERE fixture_id=11")
    con.commit()
    con.close()
    capturado.clear()
    motor.generar_dtp(12, FOCO)
    check("sin grid, ordena no inventar duelos por carril",
          "aviso_carriles" in capturado["payload"], sorted(capturado["payload"]))

    # ── sin ficha ninguna: se niega en vez de pagar por inventar ───────────
    con = sad()
    con.execute("DELETE FROM alineaciones")
    con.execute("DELETE FROM fixture_eventos")
    con.commit()
    con.close()
    try:
        motor.generar_dtp(12, FOCO)
        check("sin ficha del anterior ni XI, se niega a abrir", False, "no lanzó excepción")
    except RuntimeError as e:
        check("sin ficha del anterior ni XI, se niega a abrir", "ficha_partido" in str(e), str(e))

    # ── el equipo tiene que jugar el partido ───────────────────────────────
    try:
        motor.generar_dtp(12, OTRO)
        check("un equipo que no juega el fixture → error", False, "no lanzó excepción")
    except motor.FixtureNoExiste:
        check("un equipo que no juega el fixture → error", True)

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
