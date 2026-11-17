"""Test del banco probable (backend/analisis/banco.py) — sin red.

Una sola lista para EFE, DTP y TDE (A8 de la EFE v1.10, 17/11/2026). Arma un
equipo con 10 partidos jugados y comprueba la regla:
- antes del once el banco es PROBABLE: los que entraron seguido o hicieron
  goles o asistencias entrando; nunca el que nunca entra, ni el titular de hoy;
- con el once oficial y la banca completa, el banco es LA HOJA: todos los
  suplentes publicados y ningún titular, con el titular habitual primero;
- con la banca parcial (la API la sube antes que la completa) sigue probable;
- el gol en contra y el penal errado no cuentan; el lateral sale del grid.

    python -m backend.test_banco
"""
import os
import sqlite3
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="sad-banco-")
os.environ["SAD_DATA_DIR"] = _TMP
os.environ.setdefault("SAD_SIN_HILOS", "1")

fallos = 0
EQ, RIVAL, HOY = 10, 20, 500


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def montar():
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.executescript("""
        CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT,
            home_team_id INTEGER, away_team_id INTEGER);
        CREATE TABLE fixture_eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_id INTEGER NOT NULL,
            minuto INTEGER, extra INTEGER, tipo TEXT, detalle TEXT, equipo_id INTEGER, jugador TEXT,
            jugador_id INTEGER, asistente TEXT, asistente_id INTEGER);
        CREATE TABLE alineaciones (fixture_id INTEGER, team_id INTEGER, formacion TEXT, entrenador TEXT,
            player_id INTEGER, jugador TEXT, numero INTEGER, posicion TEXT, grid TEXT, titular INTEGER);
    """)
    # 10 partidos jugados (ids 1-10, el 10 el más reciente) y el de hoy sin jugar
    for i in range(1, 11):
        con.execute("INSERT INTO fixtures VALUES (?, ?, 'FT', ?, ?)", (i, f"2026-10-{i:02d}T20:00:00+00:00", EQ, RIVAL))
    con.execute("INSERT INTO fixtures VALUES (?, '2026-11-17T20:00:00+00:00', 'NS', ?, ?)", (HOY, EQ, RIVAL))
    # titulares fijos 1-11 (el 2 es lateral izquierdo, el 5 lateral derecho; línea de 4 en la fila 2)
    grid = {1: "1:1", 2: "2:1", 3: "2:2", 4: "2:3", 5: "2:4", 6: "3:1", 7: "3:2", 8: "3:3",
            9: "4:1", 10: "4:2", 11: "4:3"}
    pos = {1: "G", 2: "D", 3: "D", 4: "D", 5: "D", 6: "M", 7: "M", 8: "M", 9: "F", 10: "F", 11: "F"}
    for f in range(1, 11):
        for p in range(1, 12):
            con.execute("INSERT INTO alineaciones VALUES (?, ?, '4-3-3', 'DT', ?, ?, ?, ?, ?, 1)",
                        (f, EQ, p, f"Jugador {p}", p, pos[p], grid[p]))
        # el banco: 12 entra siempre (revulsivo), 13 entra 2 veces y marca una, 14 nunca entra,
        # 15 entra una vez y su gol es en contra, 16 entra una vez y erra un penal
        for p in (12, 13, 14, 15, 16):
            con.execute("INSERT INTO alineaciones VALUES (?, ?, '4-3-3', 'DT', ?, ?, ?, 'F', NULL, 0)",
                        (f, EQ, p, f"Suplente {p}", p))
        con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador_id, "
                    "asistente_id) VALUES (?, 60, 'subst', 'Substitution 1', ?, 9, 12)", (f, EQ))
    for f in (9, 10):
        con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador_id, "
                    "asistente_id) VALUES (?, 70, 'subst', 'Substitution 2', ?, 13, 10)", (f, EQ))
    con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador_id, "
                "asistente_id) VALUES (10, 80, 'Goal', 'Normal Goal', ?, 13, 12)", (EQ,))
    con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador_id, "
                "asistente_id) VALUES (8, 70, 'subst', 'Substitution 2', ?, 15, 11)", (EQ,))
    con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador_id, "
                "asistente_id) VALUES (8, 85, 'Goal', 'Own Goal', ?, 15, NULL)", (EQ,))
    con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador_id, "
                "asistente_id) VALUES (7, 70, 'subst', 'Substitution 2', ?, 16, 11)", (EQ,))
    con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, tipo, detalle, equipo_id, jugador_id, "
                "asistente_id) VALUES (7, 85, 'Goal', 'Missed Penalty', ?, 16, NULL)", (EQ,))
    con.commit()
    con.close()


def hoja_de_hoy(titulares, banca):
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.execute("DELETE FROM alineaciones WHERE fixture_id=?", (HOY,))
    for p in titulares:
        con.execute("INSERT INTO alineaciones VALUES (?, ?, '4-3-3', 'DT', ?, ?, ?, 'M', NULL, 1)",
                    (HOY, EQ, p, f"Jugador {p}" if p <= 11 else f"Suplente {p}", p))
    for p in banca:
        con.execute("INSERT INTO alineaciones VALUES (?, ?, '4-3-3', 'DT', ?, ?, ?, 'M', NULL, 0)",
                    (HOY, EQ, p, f"Jugador {p}" if p <= 11 else f"Suplente {p}", p))
    con.commit()
    con.close()


def main():
    montar()
    from backend.analisis import banco

    b = banco.banco_probable(HOY)
    a = b["a"]
    ids = [x["jugadorId"] for x in a["lista"]]
    check("sin once, el banco es probable", a["fuente"] == "probable", a["fuente"])
    check("sin once entran el revulsivo (10 entradas) y el que marcó entrando; no el que nunca entra",
          12 in ids and 13 in ids and 14 not in ids, ids)
    check("sin once, el gol en contra y el penal errado no lo meten (una sola entrada cada uno)",
          15 not in ids and 16 not in ids, ids)
    s13 = next(x for x in a["lista"] if x["jugadorId"] == 13)
    s12 = next(x for x in a["lista"] if x["jugadorId"] == 12)
    check("goles y asistencias entrando: 13 marcó uno asistido por 12",
          s13["golesDesdeBanco"] == 1 and s13["asistenciasDesdeBanco"] == 0 and s12["asistenciasDesdeBanco"] == 1
          and s12["entradas"] == 10 and s13["entradas"] == 2, (s12, s13))
    check("sin once ningún titular habitual es banco probable", not any(x["titularHabitual"] for x in a["lista"]),
          a["lista"])
    check("un lado sin historia sale con la lista vacía, no con un error", b["b"]["lista"] == [], b["b"])

    # el once oficial con la banca PARCIAL: sigue probable, y el que hoy es titular sale de la lista
    hoja_de_hoy([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12], [11, 13])
    a = banco.banco_probable(HOY)["a"]
    ids = [x["jugadorId"] for x in a["lista"]]
    check("con banca parcial (2 suplentes) el banco sigue probable y lo dice",
          a["fuente"] == "probable" and "parcial" in a["nota"], a)
    check("el que hoy es titular (12) deja de ser banco probable", 12 not in ids and 13 in ids, ids)

    # el once oficial con la banca completa: el banco es la hoja
    hoja_de_hoy([1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [2, 13, 14, 15, 16, 17])
    a = banco.banco_probable(HOY)["a"]
    ids = [x["jugadorId"] for x in a["lista"]]
    check("con la banca completa el banco es la hoja: todos los suplentes publicados y ningún titular",
          a["fuente"] == "hoja" and sorted(ids) == [2, 13, 14, 15, 16, 17], ids)
    check("el titular habitual que hoy arranca en el banco va primero y se nombra aparte",
          ids[0] == 2 and a["titularesHabitualesEnElBanco"] == ["Jugador 2"], (ids, a["titularesHabitualesEnElBanco"]))
    j2 = a["lista"][0]
    check("el lateral sale del grid de su último partido (punta de la línea de 4)",
          j2["lateral"] is True and any("lateral" in p for p in j2["porque"]), j2)
    s17 = next(x for x in a["lista"] if x["jugadorId"] == 17)
    check("un suplente sin historia en la base va igual (está en la hoja), en cero y sin porqué",
          s17["entradas"] == 0 and s17["porque"] == [], s17)
    check("después del titular habitual, el que hizo algo entrando", ids[1] == 13, ids)

    check("un fixture que no está en la base devuelve None", banco.banco_probable(999999) is None)

    print("\nTODO OK" if not fallos else f"\n{fallos} FALLAS")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
