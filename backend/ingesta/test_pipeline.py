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

    print("\nTODO OK" if not fallas else f"\n{fallas} FALLAS")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
