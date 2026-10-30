"""Test de quién pasó una llave (backend/eliminatoria.py, incidencia 774) — sin red.

Palmeiras pasó a la final de la Libertadores por penales (2-1 de visita en la
ida, 0-1 en casa en la vuelta, 5-3 en la tanda) y un parte lo dio por
eliminado. Este test arma esa llave y comprueba que la base diga quién pasó en
la ficha, el timeline y el veredicto, y que el parte que lo contradice suene.

    python -m backend.test_eliminatoria
"""
import os
import sqlite3
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="sad-elim-")
os.environ["SAD_DATA_DIR"] = _TMP
os.environ.setdefault("SAD_SIN_HILOS", "1")

fallos = 0
PAL, FLU, BRA, OTRO, X, Y = 121, 124, 794, 900, 901, 902
LIB, BRA_LIGA, COPA = 13, 71, 73


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def montar():
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.executescript("""
        CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE leagues (id INTEGER PRIMARY KEY, name TEXT, country TEXT);
        CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT, status_long TEXT,
            league_id INTEGER, league_season INTEGER, league_round TEXT,
            home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
            fulltime_home INTEGER, fulltime_away INTEGER, extratime_home INTEGER, extratime_away INTEGER,
            penalty_home INTEGER, penalty_away INTEGER);
        CREATE TABLE fixture_eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL,
            minuto INTEGER, extra INTEGER, tipo TEXT, detalle TEXT, equipo_id INTEGER, jugador TEXT,
            jugador_id INTEGER, asistente TEXT, asistente_id INTEGER);
    """)
    con.executemany("INSERT INTO teams VALUES (?,?)", [(PAL, "Palmeiras"), (FLU, "Fluminense"),
                    (BRA, "Bragantino"), (OTRO, "Otro FC"), (X, "Equis"), (Y, "Ye")])
    con.executemany("INSERT INTO leagues VALUES (?,?,?)", [(LIB, "CONMEBOL Libertadores", "World"),
                    (BRA_LIGA, "Serie A", "Brazil"), (COPA, "Copa do Brasil", "Brazil")])
    filas = [
        # la llave de Palmeiras: ida 1-2 en Río, vuelta 0-1 en São Paulo, 5-3 en la tanda
        (1001, "2026-10-15 00:30:00", "FT", LIB, "Semi-finals", FLU, PAL, 1, 2, 1, 2, None, None, None, None),
        (1002, "2026-10-22 00:30:00", "PEN", LIB, "Semi-finals", PAL, FLU, 0, 1, 0, 1, None, None, 5, 3),
        # el partido del parte
        (1003, "2026-10-24 22:00:00", "NS", BRA_LIGA, "Regular Season - 31", PAL, BRA, None, None, None, None,
         None, None, None, None),
        # tanda SIN columnas de penales: se cuenta en los Shootout (gana la visita 4-2)
        (1004, "2026-10-10 20:00:00", "PEN", COPA, "Quarter-finals", X, Y, 1, 1, 1, 1, 0, 0, None, None),
        # ida de una llave con la vuelta programada: no cierra nada
        (1005, "2026-10-20 20:00:00", "FT", COPA, "Semi-finals", X, OTRO, 3, 0, 3, 0, None, None, None, None),
        (1006, "2026-10-29 20:00:00", "NS", COPA, "Semi-finals", OTRO, X, None, None, None, None,
         None, None, None, None),
        # partido único con prórroga: 1-1 a 90', 2-1 en el alargue para la visita
        (1007, "2026-10-12 20:00:00", "AET", COPA, "Round of 16", OTRO, Y, 1, 2, 1, 1, 0, 1, None, None),
        # final única
        (1008, "2026-10-18 20:00:00", "FT", COPA, "Final", Y, OTRO, 0, 2, 0, 2, None, None, None, None),
        # 846: Copa del Rey (143) a partido único, resuelta a 90'; y su semifinal (ida y vuelta) no
        (1010, "2026-10-29 19:00:00", "FT", 143, "Round of 128", X, OTRO, 0, 6, 0, 6, None, None, None, None),
        (1011, "2026-10-29 19:00:00", "FT", 143, "Semi-finals", Y, OTRO, 2, 1, 2, 1, None, None, None, None),
        (1012, "2026-10-29 19:00:00", "FT", COPA, "Round of 32", X, Y, 1, 0, 1, 0, None, None, None, None),
        # fase de grupos: nunca es una llave
        (1009, "2026-10-05 20:00:00", "FT", LIB, "Group Stage - 3", PAL, OTRO, 2, 0, 2, 0, None, None, None, None),
    ]
    con.executemany("INSERT INTO fixtures (id, date, status_short, league_id, league_season, league_round, "
                    "home_team_id, away_team_id, goals_home, goals_away, fulltime_home, fulltime_away, "
                    "extratime_home, extratime_away, penalty_home, penalty_away) "
                    "VALUES (?,?,?,?,2026,?,?,?,?,?,?,?,?,?,?,?)", filas)
    tanda = [(X, "Penalty"), (Y, "Penalty"), (X, "Missed Penalty"), (Y, "Penalty"), (X, "Penalty"),
             (Y, "Penalty"), (X, "Missed Penalty"), (Y, "Penalty")]
    con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id) "
                    "VALUES (1004, 91, 'Shootout', ?, ?)", [(d, e) for e, d in tanda])
    con.commit()
    con.close()


montar()
from backend import cronologia, eliminatoria  # noqa: E402

d = eliminatoria.desenlace(1002)
check("774: la vuelta 0-1 con 2-2 en el global y 5-3 en la tanda la pasa Palmeiras",
      d and d["avanza"] == PAL and d["eliminado"] == FLU and d["penales"] == "5-3" and d["global"] == "2-2"
      and d["ida"] == 1001 and d["marcador"] == "0-1", d)
check("774: el texto desde Palmeiras dice PASA y desde Fluminense ELIMINADO, con la tanda de su lado",
      eliminatoria.texto_para(d, PAL).startswith("PASA por penales (5-3) tras 2-2")
      and eliminatoria.texto_para(d, FLU).startswith("ELIMINADO por penales (3-5) tras 2-2"),
      (eliminatoria.texto_para(d, PAL), eliminatoria.texto_para(d, FLU)))
d4 = eliminatoria.desenlace(1004)
check("sin columnas de penales, la tanda se cuenta en los Shootout convertidos (2-4, pasa la visita)",
      d4 and d4["penales"] == "2-4" and d4["avanza"] == Y, d4)
check("la ida con la vuelta programada no cierra la llave (avanza None, nunca adivinado)",
      eliminatoria.desenlace(1005)["avanza"] is None, eliminatoria.desenlace(1005))
d7 = eliminatoria.desenlace(1007)
check("partido único con prórroga: pasa quien ganó el alargue", d7 and d7["avanza"] == Y and d7["prorroga"], d7)
check("final única: pasa el ganador", eliminatoria.desenlace(1008)["avanza"] == OTRO)
check("la fase de grupos no es una llave", eliminatoria.desenlace(1009) is None)
check("846: Copa del Rey a partido único resuelta a 90' (0-6): pasa la visita",
      eliminatoria.desenlace(1010)["avanza"] == OTRO, eliminatoria.desenlace(1010))
check("846: la semifinal de la Copa del Rey es a ida y vuelta: a 90' no se afirma",
      eliminatoria.desenlace(1011)["avanza"] is None, eliminatoria.desenlace(1011))
check("846: una copa fuera de la lista sigue sin afirmar a 90'",
      eliminatoria.desenlace(1012)["avanza"] is None, eliminatoria.desenlace(1012))
check("un partido sin terminar no es una llave", eliminatoria.desenlace(1003) is None)
rec = eliminatoria.recientes(PAL, "2026-10-24 22:00:00")
check("las llaves recientes de Palmeiras antes del Bragantino: la semifinal, pasada",
      [(r["fixtureId"], r["pasa"]) for r in rec] == [(1002, True)], rec)

# el timeline: el marcador sigue siendo el de 90', la llave va en el título
ev = cronologia.eventos_de(PAL, "Palmeiras", "2026-10-01", "2026-10-23")
vuelta = [e for e in ev if e["fecha"] == "2026-10-22"]
check("774: el timeline dice «Derrota 0-1 ante Fluminense · PASA por penales (5-3)…» y lo destaca",
      vuelta and vuelta[0]["tipo"] == "derrota" and "PASA por penales (5-3)" in vuelta[0]["titulo"]
      and vuelta[0]["marcador"] == "0-1" and vuelta[0]["destacado"], vuelta)
ev_flu = cronologia.eventos_de(FLU, "Fluminense", "2026-10-01", "2026-10-23")
check("desde Fluminense la misma noche es una victoria a 90' y ELIMINADO",
      any("ELIMINADO por penales (3-5)" in e["titulo"] and e["tipo"] == "resultado" for e in ev_flu), ev_flu)
directo = cronologia.eventos_de(PAL, "Palmeiras", "2026-10-01", "2026-10-23", rival_id=FLU)
check("el enfrentamiento directo dice quién pasa", any("pasa Palmeiras por penales (5-3)" in e["titulo"]
                                                       for e in directo if e["equipo"] == "ambos"), directo)

# el parte que lo contradice
from backend.analisis import parte  # noqa: E402

fx = {"id": 1003, "date": "2026-10-24 22:00:00", "home_team_id": PAL, "away_team_id": BRA}
nombres = {"a": "Palmeiras", "b": "Bragantino"}
malo = {"equipos": {"a": {"bloques": {"C": {"nota": "C4 🔶: la racha se cortó el 22/10 con la eliminación en "
                                                    "semifinales de Libertadores (0-1, 2-2 global, penales)."}}},
                    "b": {}},
        "lecturaSad": {"contextoEmocional": "Palmeiras quedó eliminado de la Libertadores por penales hace 48 h."}}
al = parte.alertas_eliminatoria(malo, fx, nombres)
check("774: el parte que da a Palmeiras eliminado suena ELIMINATORIA-AL-REVES (una por lado)",
      [a["codigo"] for a in al] == ["ELIMINATORIA-AL-REVES"] and al[0]["equipo"] == "a"
      and "PASA por penales" in al[0]["detalle"], al)
bueno = {"equipos": {"a": {"bloques": {"D": {"nota": "pasó a la final de la Libertadores por penales hace 48 h; "
                                                     "evitó la eliminación en la tanda"}}}, "b": {}},
         "documentos": [{"id": "ensayo", "cuerpo": "Bragantino quedó eliminado de la Copa do Brasil en agosto."}]}
check("lo correcto, la negación («evitó la eliminación») y la eliminación de OTRO equipo no suenan",
      parte.alertas_eliminatoria(bueno, fx, nombres) == [], parte.alertas_eliminatoria(bueno, fx, nombres))
activa = {"equipos": {"a": {"bloques": {"D": {"nota": "eliminó a Fluminense en la Libertadores por penales."}}},
                      "b": {}},
          "lecturaSad": {"contextoEmocional": "Palmeiras clasificó a la final eliminando a Fluminense por "
                                             "penales en la Libertadores; Fluminense quedó eliminado."}}
check("«eliminó a Fluminense» y la frase que nombra a los dos equipos no suenan",
      parte.alertas_eliminatoria(activa, fx, nombres) == [], parte.alertas_eliminatoria(activa, fx, nombres))
fx_flu = {"id": 1010, "date": "2026-10-25 22:00:00", "home_team_id": FLU, "away_team_id": BRA}
al_flu = parte.alertas_eliminatoria({"equipos": {"a": {"bloques": {"D": {"nota": "llega finalista de la "
                                                                                  "Libertadores, con la moral alta."}}},
                                                 "b": {}}}, fx_flu, {"a": "Fluminense", "b": "Bragantino"})
check("al revés también: dar por finalista al eliminado suena", [a["equipo"] for a in al_flu] == ["a"], al_flu)

print()
print("TODO OK" if not fallos else f"{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
