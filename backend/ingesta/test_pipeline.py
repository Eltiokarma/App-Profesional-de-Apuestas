"""El pipeline rehace las derivadas SIN dejar a quien lee sin tabla.

    python -m backend.ingesta.test_pipeline
"""
from __future__ import annotations

import os
import sqlite3
import sys
import tempfile

from backend.ingesta.pipeline import DDL_LEVELS, _crear_db

fallas = 0


def check(nombre, ok, detalle=""):
    global fallas
    print(("OK  " if ok else "FALLA ") + nombre + ("" if ok else f" -> {detalle}"))
    fallas += 0 if ok else 1


def main() -> int:
    d = tempfile.mkdtemp(prefix="sad_pipe_")
    path = os.path.join(d, "levels.db")
    # la base vieja, con otra tabla al lado que el pipeline no debe tocar
    con = sqlite3.connect(path)
    con.executescript(DDL_LEVELS)
    con.execute("INSERT INTO team_levels (team_id, fixture_id, date, level) VALUES (1, 1, '2026-01-01', 1.5)")
    con.execute("CREATE TABLE otra (x INTEGER)")
    con.execute("INSERT INTO otra VALUES (7)")
    con.commit()
    con.close()

    def leer(sql):
        r = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=0.2)
        try:
            return r.execute(sql).fetchall()
        finally:
            r.close()

    w = _crear_db(path, DDL_LEVELS)          # DROP + CREATE dentro de la transacción
    w.execute("INSERT INTO team_levels (team_id, fixture_id, date, level) VALUES (2, 2, '2026-02-01', 2.5)")
    try:
        durante = leer("SELECT team_id FROM team_levels")
    except sqlite3.Error as e:  # «no such table» es justo el error del 14/10
        durante = f"error: {e}"
    check("mientras el pipeline escribe, quien lee ve la tabla VIEJA entera (no «no such table»)",
          durante == [(1,)], durante)
    with w:
        pass                                 # el COMMIT del llamador
    w.close()
    check("después del COMMIT se ve la tabla nueva entera", leer("SELECT team_id FROM team_levels") == [(2,)])
    check("y la otra tabla del archivo sigue intacta (constants_cuota vive así en constants.db)",
          leer("SELECT x FROM otra") == [(7,)])
    check("sin archivos sueltos de la corrida", sorted(os.listdir(d)) == ["levels.db"], os.listdir(d))

    # 1371: el partido del homónimo (Copa Perú con el id de Atlético Nacional) sale del pipeline ENTERO
    from backend.ingesta.pipeline import sin_ajenos
    sad = os.path.join(d, "sad.db")
    c = sqlite3.connect(sad)
    c.executescript("""CREATE TABLE fixtures (id INTEGER PRIMARY KEY, home_team_id INTEGER, away_team_id INTEGER,
                                              league_id INTEGER);
                       CREATE TABLE leagues (id INTEGER PRIMARY KEY, name TEXT, country TEXT);
                       INSERT INTO leagues VALUES (239, 'Primera A', 'Colombia'), (503, 'Copa Peru', 'Peru'),
                                                  (13, 'CONMEBOL Libertadores', 'World');""")
    c.executemany("INSERT INTO fixtures VALUES (?,?,?,?)",
                  [(1, 1137, 1140, 239), (2, 1140, 1137, 239), (3, 1137, 1141, 239), (4, 1137, 50, 13),
                   (5, 20326, 1137, 503)])
    c.commit()
    c.close()
    fx = [(i, f"2026-11-0{i}", 0, 0, 1, 1) for i in range(1, 6)]
    quedan, fuera = sin_ajenos(fx, sad)
    check("1371: el partido de la Copa Perú sale del pipeline y los de Colombia y la Libertadores quedan",
          [f[0] for f in quedan] == [1, 2, 3, 4] and fuera == [(5, 1137)], (quedan, fuera))
    os.remove(sad)

    print("\nTODO OK" if not fallas else f"\n{fallas} FALLAS")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
