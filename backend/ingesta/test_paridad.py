"""Test dorado: valida el port recomputando y comparando contra las DBs reales.

Metodología — el pipeline viejo era incremental y NUNCA propagaba retro-updates
(INFORME_INGESTA.md), así que sus DBs mezclan vintages: comparar contra la
historia de HOY da falsos negativos. En su lugar, cada capa se recomputa sobre
LA HISTORIA QUE EL VIEJO VIO (las filas guardadas por equipo, en su orden) y se
aísla el staleness con cohortes limpias:

  1. niveles:    fórmula sobre la secuencia guardada en team_levels.
  2. constantes: fórmula sobre la secuencia guardada en constants; la cohorte
     limpia son los equipos cuyas q* coinciden todas (niveles de rival no
     rancios) — ahí las k deben clavar.
  3. discreto:   fusión + bins desde constants/levels actuales; la cohorte
     limpia son las filas cuyos k_goles_* (pass-through) coinciden (la fila
     de constants no cambió desde el insert con DO NOTHING del viejo).

Solo lectura (mode=ro). Uso: PYTHONUTF8=1 python -m backend.ingesta.test_paridad
"""
import sqlite3
import sys
from collections import defaultdict

from backend.ingesta.constantes import COLUMNAS, calcular_constantes
from backend.ingesta.discretizador import DEFAULT_LEVEL, DiscretizadorUniforme, fusion
from backend.ingesta.niveles import CacheNiveles, calcular_niveles

TOL = 1e-6
Q_COLS = tuple(c for c in COLUMNAS if c.startswith("q_"))


def _ro(path: str) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def _igual(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


def _pct(ok: int, total: int) -> str:
    return f"{ok} de {total} ({100 * ok / total:.2f} %)" if total else "sin filas"


def cargar_info_fixtures() -> dict[int, tuple]:
    """fixture_id → (home_id, away_id, goals_home, goals_away)."""
    with _ro("sad.db") as con:
        return {
            fid: (h, a, gh, ga)
            for fid, h, a, gh, ga in con.execute(
                """SELECT id, home_team_id, away_team_id, goals_home, goals_away
                   FROM fixtures
                   WHERE goals_home IS NOT NULL AND goals_away IS NOT NULL"""
            )
        }


def capa_niveles(info) -> None:
    with _ro("levels.db") as con:
        filas = con.execute(
            "SELECT team_id, fixture_id, date, level FROM team_levels ORDER BY date, fixture_id"
        ).fetchall()
    por_equipo: dict[int, list[tuple]] = defaultdict(list)
    for t, f, d, lvl in filas:
        por_equipo[t].append((f, d, lvl))
    total = ok = sin_goles = 0
    peor = (0.0, None)
    for team_id, guardado in por_equipo.items():
        h = []
        for f, d, _ in guardado:
            g = info.get(f)
            if g is None:
                h = None
                break
            home, _, gh, ga = g
            h.append((f, d, gh, ga) if home == team_id else (f, d, ga, gh))
        if h is None:
            sin_goles += len(guardado)
            continue
        calc = {f: lvl for f, _, lvl in calcular_niveles(h)}
        for f, _, lvl in guardado:
            total += 1
            if _igual(calc[f], lvl):
                ok += 1
            else:
                d = abs(calc[f] - lvl)
                if d > peor[0]:
                    peor = (d, (team_id, f, lvl, calc[f]))
    print(f"\n[1] NIVELES — fórmula sobre la secuencia guardada ({len(filas)} filas)")
    print(f"    coinciden: {_pct(ok, total)} · saltadas sin goles en sad.db: {sin_goles}")
    if peor[1]:
        print(f"    peor diferencia: {peor[0]:.6g} en (equipo,fixture,guardado,calculado)={peor[1]}")


def capa_constantes(info) -> None:
    with _ro("levels.db") as con:
        cache = CacheNiveles(con.execute("SELECT team_id, date, level FROM team_levels"))
    cols = ", ".join(COLUMNAS)
    with _ro("constants.db") as con:
        filas = con.execute(
            f"SELECT team_id, fixture_id, date, {cols} FROM constants ORDER BY date, fixture_id"
        ).fetchall()
    por_equipo: dict[int, list[tuple]] = defaultdict(list)
    for fila in filas:
        por_equipo[fila[0]].append(fila[1:])
    total = ok = saltadas = 0
    c_total = c_ok = c_equipos = 0
    difcol: dict[str, int] = defaultdict(int)
    for team_id, guardado in por_equipo.items():
        h = []
        for fila in guardado:
            g = info.get(fila[0])
            if g is None:
                h = None
                break
            home, away, gh, ga = g
            h.append(
                (fila[0], fila[1], True, gh, ga, away)
                if home == team_id
                else (fila[0], fila[1], False, ga, gh, home)
            )
        if h is None:
            saltadas += len(guardado)
            continue
        calc = {c["fixture_id"]: c for c in calcular_constantes(h, cache)}
        limpio = True
        resultados = []
        for fila in guardado:
            mio = calc[fila[0]]
            malas = [c for c, v in zip(COLUMNAS, fila[2:]) if not _igual(mio[c], v)]
            resultados.append(malas)
            if any(c in Q_COLS for c in malas):
                limpio = False
        for malas in resultados:
            total += 1
            if not malas:
                ok += 1
            if limpio:
                c_total += 1
                if not malas:
                    c_ok += 1
                else:
                    for c in malas:
                        difcol[c] += 1
        c_equipos += limpio
    print(f"\n[2] CONSTANTES — fórmula sobre la secuencia guardada ({len(filas)} filas)")
    print(f"    filas 100% iguales (global): {_pct(ok, total)} · saltadas: {saltadas}")
    print(f"    cohorte limpia (q* al día, {c_equipos} equipos): {_pct(c_ok, c_total)}")
    if difcol:
        top = sorted(difcol.items(), key=lambda x: -x[1])[:6]
        print("    difieren en cohorte:", ", ".join(f"{c}={n}" for c, n in top))


def capa_discreto(info) -> None:
    with _ro("levels.db") as con:
        filas_lvl = con.execute(
            "SELECT team_id, fixture_id, date, level FROM team_levels"
        ).fetchall()
        nmin, nmax = con.execute("SELECT MIN(level), MAX(level) FROM team_levels").fetchone()
    exacto = {(t, f): lvl for t, f, _, lvl in filas_lvl}
    cache = CacheNiveles((t, d, lvl) for t, _, d, lvl in filas_lvl)
    disc = DiscretizadorUniforme(nmin, nmax)

    def nivel_bin(team_id: int, fixture_id: int, fecha: str) -> int:
        lvl = exacto.get((team_id, fixture_id))
        if lvl is None:
            lvl = cache.nivel_a_fecha(team_id, fecha, DEFAULT_LEVEL)
        return disc.bin(lvl)

    with _ro("constants.db") as con:
        consts = {
            (t, f): resto
            for t, f, *resto in con.execute(
                """SELECT team_id, fixture_id, k_positivo, k_negativo,
                          k_positivo_local, k_negativo_local,
                          k_positivo_visita, k_negativo_visita,
                          k_goles_anotado, k_goles_recibido,
                          k_goles_local_anotado, k_goles_local_recibido,
                          k_goles_visita_anotado, k_goles_visita_recibido
                   FROM constants"""
            )
        }
    fusiones = ("k", "k_local", "k_visita")
    paso = ("k_goles_anotado", "k_goles_recibido", "k_goles_local_anotado",
            "k_goles_local_recibido", "k_goles_visita_anotado", "k_goles_visita_recibido")
    bins = ("nivel_equipo", "nivel_rival")
    with _ro("discreto.db") as con:
        guardadas = con.execute(
            f"""SELECT fixture_id, equipo_id, rival_id, fecha,
                       {', '.join(fusiones + paso + bins)}
                FROM processed_matches"""
        ).fetchall()
    total = ok = sin_constante = 0
    c_total = c_fusion_ok = c_bins_ok = 0
    for fila in guardadas:
        fid, eq, rival, fecha = fila[0], fila[1], fila[2], fila[3]
        total += 1
        c = consts.get((eq, fid))
        if c is None:
            sin_constante += 1
            continue
        mias_fusion = (fusion(c[0], c[1]), fusion(c[2], c[3]), fusion(c[4], c[5]))
        mias_paso = tuple(x or 0.0 for x in c[6:12])
        mias_bins = (nivel_bin(eq, fid, fecha), nivel_bin(rival, fid, fecha))
        v_fusion, v_paso, v_bins = fila[4:7], fila[7:13], fila[13:15]
        fusion_ok = all(_igual(a, b) for a, b in zip(mias_fusion, v_fusion))
        paso_ok = all(_igual(a, b) for a, b in zip(mias_paso, v_paso))
        bins_ok = mias_bins == tuple(v_bins)
        if fusion_ok and paso_ok and bins_ok:
            ok += 1
        if paso_ok:  # la fila de constants no cambió desde el insert del viejo
            c_total += 1
            c_fusion_ok += fusion_ok
            c_bins_ok += bins_ok
    print(f"\n[3] DISCRETO — fusión + bins desde constants/levels actuales ({total} filas)")
    print(f"    filas 100% iguales (global): {_pct(ok, total)} · sin constante: {sin_constante}")
    print(f"    cohorte limpia (constants sin cambiar desde el insert): {c_total} filas")
    print(f"      fusión k/k_local/k_visita: {_pct(c_fusion_ok, c_total)}")
    print(f"      bins nivel_equipo/rival:   {_pct(c_bins_ok, c_total)}")


def main() -> None:
    print("Test dorado de paridad — recomputo vs DBs reales (solo lectura)")
    info = cargar_info_fixtures()
    print(f"sad.db: {len(info)} fixtures con goles")
    capa_niveles(info)
    capa_constantes(info)
    capa_discreto(info)


if __name__ == "__main__":
    sys.exit(main())
