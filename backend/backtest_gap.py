"""Backtest muestreado de la Ley de la Regresión al Nivel (§5) y sus extensiones.

Recorre una MUESTRA de fixtures terminados (para no saturar la DB) y
reconstruye cada señal tal como estaba ANTES del partido — nivel y forma a
fecha − 1 s, sin fuga: la fila de team_levels del propio fixture ya incluye
su resultado — para compararla con lo que pasó de verdad:

  1. señal clásica del gap   → residual del partido (pts − μ_partido)
  2. señal ajustada          → ídem
  3. señal de calendario     → residual del SIGUIENTE partido (¿la mejora
                               llega antes con calendario blando?)
  4. partido trampa          → residual vs favoritos claros SIN grande cerca

Si la ley funciona, los buckets "mejora" deben tener residual > 0, los
"empeora" residual < 0, y el efecto crecer de leve a fuerte. Con eso se
validan (o recalibran) los umbrales 0.3/0.5 del gap y ±0.15 del calendario.

Extras:
  --horizonte N   además del partido analizado, residual MEDIO de los próximos
                  N partidos por bucket de señal (¿a qué plazo aparece la
                  regresión si el partido siguiente es momentum?)
  --calibrar      reajusta los 4 coeficientes de μ por OLS sobre la muestra y
                  compara RMSE contra los heredados (μ descalibrada en los
                  extremos = residuales espurios en todos los buckets)

    python -m backend.backtest_gap                       # 300 fixtures al azar
    python -m backend.backtest_gap --muestra 1500 --horizonte 5 --calibrar
    python -m backend.backtest_gap --muestra 800 --liga 140 --temporada 2025
    SAD_DATA_DIR=demo_data python -m backend.backtest_gap  # contra la demo
"""
import argparse
import random
from datetime import timedelta

from backend import db
from backend.app import (
    _dt, _FIN90_SQL, _G90_A, _G90_H, _NO_CAMINO, _SS, CAL_UMBRAL, gap_equipo,
    INTL_LEAGUE_IDS, MU, mu, nivel_a_fecha, RECOVERY_NEXT, TRAMPA_DELTA_NIVEL,
    TRAMPA_VENTANA_DIAS,
)

BUCKETS_SENAL = ["fuerte mejora", "leve mejora", "equilibrio", "leve empeora", "fuerte empeora"]


def _puntos(gf: int, ga: int) -> int:
    return 3 if gf > ga else 1 if gf == ga else 0


def _bucket(senal, tendencia) -> str:
    if senal is None:
        return "equilibrio"
    return "equilibrio" if senal == "equilibrio" or tendencia is None else f"{senal} {tendencia}"


def _stats(pares: list[tuple[float, float]]) -> dict:
    """[(pts, μ)] → n, medias y residual medio con su error estándar."""
    n = len(pares)
    if n == 0:
        return {"n": 0, "pts": None, "mu": None, "residual": None, "err": None}
    res = [p - m for p, m in pares]
    media = sum(res) / n
    var = sum((r - media) ** 2 for r in res) / (n - 1) if n > 1 else 0.0
    return {
        "n": n,
        "pts": sum(p for p, _ in pares) / n,
        "mu": sum(m for _, m in pares) / n,
        "residual": media,
        "err": (var / n) ** 0.5,
    }


def _es_terminado90(r) -> bool:
    return ((r["status_short"] or "").upper() in ("FT", "AET", "PEN") or (r["status_long"] or "") == "Match Finished") \
        and r["gh"] is not None and r["ga"] is not None


def _proximos(team_id: int, fecha, excluir_id: int) -> list:
    marks = ",".join("?" * len(_NO_CAMINO))
    return db.query(
        "sad",
        f"""SELECT f.id, f.date, f.league_id, f.home_team_id, f.away_team_id,
                   f.status_short, f.status_long, {_G90_H} AS gh, {_G90_A} AS ga
            FROM fixtures f
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.id != ? AND f.date > ?
              AND {_SS} NOT IN ({marks})
            ORDER BY f.date ASC LIMIT {RECOVERY_NEXT}""",
        (team_id, team_id, excluir_id, str(fecha), *_NO_CAMINO),
    )


def _siguientes(team_id: int, fecha, excluir_id: int, n: int) -> list:
    """Próximos n partidos TERMINADOS del equipo tras `fecha` (para --horizonte)."""
    return db.query(
        "sad",
        f"""SELECT f.id, f.date, f.home_team_id, f.away_team_id,
                   {_G90_H} AS gh, {_G90_A} AS ga
            FROM fixtures f
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.id != ? AND f.date > ?
              AND {_FIN90_SQL} AND {_G90_H} IS NOT NULL AND {_G90_A} IS NOT NULL
            ORDER BY f.date ASC LIMIT {int(n)}""",
        (team_id, team_id, excluir_id, str(fecha)),
    )


def _ols(filas: list[tuple]) -> list[float] | None:
    """OLS de pts ~ 1 + nivel + rival + localía (ecuaciones normales 4×4,
    eliminación gaussiana con pivoteo; solo stdlib). None si no hay datos."""
    if len(filas) < 20:
        return None
    X = [(1.0, f[0], f[1], f[2]) for f in filas]
    y = [f[3] for f in filas]
    A = [[sum(xi[i] * xi[j] for xi in X) for j in range(4)] + [sum(xi[i] * yk for xi, yk in zip(X, y))]
         for i in range(4)]
    for c in range(4):
        p = max(range(c, 4), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-12:
            return None
        A[c], A[p] = A[p], A[c]
        for r in range(4):
            if r != c and A[r][c]:
                factor = A[r][c] / A[c][c]
                A[r] = [a - factor * b for a, b in zip(A[r], A[c])]
    return [A[i][4] / A[i][i] for i in range(4)]


def _rmse(filas: list[tuple], coefs: list[float]) -> float:
    """RMSE con la predicción recortada a [0,3] (μ también recorta)."""
    err = 0.0
    for nv, rv, lc, pts in filas:
        pred = max(0.0, min(3.0, coefs[0] + coefs[1] * nv + coefs[2] * rv + coefs[3] * lc))
        err += (pts - pred) ** 2
    return (err / len(filas)) ** 0.5


def _grande_cerca(team_id: int, fixture_id: int, fecha, nivel: float, antes: str) -> bool:
    d = _dt(fecha)
    ini = (d - timedelta(days=TRAMPA_VENTANA_DIAS)).strftime("%Y-%m-%d %H:%M:%S")
    fin = (d + timedelta(days=TRAMPA_VENTANA_DIAS)).strftime("%Y-%m-%d %H:%M:%S")
    rows = db.query(
        "sad",
        """SELECT f.league_id, f.home_team_id, f.away_team_id FROM fixtures f
           WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.id != ? AND f.date BETWEEN ? AND ?""",
        (team_id, team_id, fixture_id, ini, fin),
    )
    for r in rows:
        rival_id = r["away_team_id"] if r["home_team_id"] == team_id else r["home_team_id"]
        if (r["league_id"] or 0) in INTL_LEAGUE_IDS or nivel_a_fecha(rival_id, antes, fallback=1.0) >= nivel:
            return True
    return False


def backtest(muestra: int = 300, liga: int | None = None, temporada: int | None = None,
             desde: str | None = None, hasta: str | None = None, semilla: int = 42,
             horizonte: int = 1, calibrar: bool = False) -> dict:
    cond, params = [_FIN90_SQL, f"{_G90_H} IS NOT NULL", f"{_G90_A} IS NOT NULL"], []
    if liga is not None:
        cond.append("f.league_id=?")
        params.append(liga)
    if temporada is not None:
        cond.append("f.league_season=?")
        params.append(temporada)
    if desde:
        cond.append("f.date>=?")
        params.append(desde)
    if hasta:
        cond.append("f.date<=?")
        params.append(hasta)
    universo = db.query(
        "sad",
        f"""SELECT f.id, f.date, f.league_id, f.home_team_id, f.away_team_id,
                   {_G90_H} AS gh, {_G90_A} AS ga
            FROM fixtures f WHERE {' AND '.join(cond)}""",
        tuple(params),
    )
    fixtures = random.Random(semilla).sample(universo, min(muestra, len(universo)))

    clasica = {b: [] for b in BUCKETS_SENAL}
    ajustada = {b: [] for b in BUCKETS_SENAL}
    horiz_clasica = {b: [] for b in BUCKETS_SENAL}
    horiz_ajustada = {b: [] for b in BUCKETS_SENAL}
    calib: list[tuple] = []
    # señal de calendario: outcome = residual del SIGUIENTE partido
    calendario = {lado: {s: [] for s in ("blando", "neutro", "duro")} for lado in ("subrinde", "sobrerinde")}
    trampa = {"trampa": [], "favorito sin grande": []}
    n_obs = descartadas = 0

    for f in fixtures:
        antes = (_dt(f["date"]) - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
        for team_id, rival_id, es_local, gf, ga in (
            (f["home_team_id"], f["away_team_id"], True, f["gh"], f["ga"]),
            (f["away_team_id"], f["home_team_id"], False, f["ga"], f["gh"]),
        ):
            g = gap_equipo(team_id, antes)
            nivel = g["nivel"]
            nivel_rival = nivel_a_fecha(rival_id, antes, fallback=1.0)
            if calibrar:
                calib.append((nivel, nivel_rival, 1.0 if es_local else 0.0, float(_puntos(gf, ga))))
            if g["gap"] is None:
                descartadas += 1
                continue
            n_obs += 1
            mu_partido = mu(nivel, nivel_rival, 1.0 if es_local else 0.0)
            par = (float(_puntos(gf, ga)), mu_partido)
            b_cla = _bucket(g["senal"], g["tendencia"])
            b_adj = _bucket(g["senalAjustada"], g["tendenciaAjustada"])
            clasica[b_cla].append(par)
            ajustada[b_adj].append(par)

            # horizonte > 1: residual MEDIO de los próximos N terminados
            if horizonte > 1:
                sigs = _siguientes(team_id, f["date"], f["id"], horizonte)
                if sigs:
                    pares_h = []
                    for r in sigs:
                        s_local = r["home_team_id"] == team_id
                        rid = r["away_team_id"] if s_local else r["home_team_id"]
                        mu_s = mu(nivel, nivel_a_fecha(rid, antes, fallback=1.0), 1.0 if s_local else 0.0)
                        pts_s = _puntos(r["gh"] if s_local else r["ga"], r["ga"] if s_local else r["gh"])
                        pares_h.append((float(pts_s), mu_s))
                    par_h = (sum(p for p, _ in pares_h) / len(pares_h), sum(m for _, m in pares_h) / len(pares_h))
                    horiz_clasica[b_cla].append(par_h)
                    horiz_ajustada[b_adj].append(par_h)

            # partido trampa: favoritos claros, con vs sin "grande" a ±4 días
            if nivel_rival <= nivel - TRAMPA_DELTA_NIVEL:
                grupo = "trampa" if _grande_cerca(team_id, f["id"], f["date"], nivel, antes) else "favorito sin grande"
                trampa[grupo].append(par)

            # calendario: solo con señal de gap activa (|gap| ≥ 0.3)
            if abs(g["gap"]) >= 0.3:
                prox = _proximos(team_id, f["date"], f["id"])
                if prox:
                    # μ de los próximos con el nivel del rival A LA FECHA DEL ANÁLISIS
                    # (lo que se sabía entonces), no a la fecha futura
                    mus = [
                        mu(nivel, nivel_a_fecha(r["away_team_id"] if r["home_team_id"] == team_id else r["home_team_id"], antes, fallback=1.0),
                           1.0 if r["home_team_id"] == team_id else 0.0)
                        for r in prox
                    ]
                    recup = sum(mus) / len(mus)
                    dif = recup - g["ptsEsperados"]
                    senal_cal = "blando" if dif > CAL_UMBRAL else "duro" if dif < -CAL_UMBRAL else "neutro"
                    sig = next((r for r in prox if _es_terminado90(r)), None)
                    if sig is not None:
                        sig_local = sig["home_team_id"] == team_id
                        pts_sig = _puntos(sig["gh"] if sig_local else sig["ga"], sig["ga"] if sig_local else sig["gh"])
                        mu_sig = mus[prox.index(sig)]
                        lado = "subrinde" if g["gap"] > 0 else "sobrerinde"
                        calendario[lado][senal_cal].append((float(pts_sig), mu_sig))

    calibracion = None
    if calibrar:
        actual = [MU["intercept"], MU["nivel"], MU["rival"], MU["localia"]]
        coefs = _ols(calib)
        calibracion = {
            "n": len(calib),
            "actual": {"coefs": actual, "rmse": _rmse(calib, actual) if calib else None},
            "ols": None if coefs is None else {"coefs": coefs, "rmse": _rmse(calib, coefs)},
        }

    return {
        "universo": len(universo),
        "muestra": len(fixtures),
        "observaciones": n_obs,
        "descartadas": descartadas,
        "clasica": {b: _stats(v) for b, v in clasica.items()},
        "ajustada": {b: _stats(v) for b, v in ajustada.items()},
        "horizonte": None if horizonte <= 1 else {
            "n": horizonte,
            "clasica": {b: _stats(v) for b, v in horiz_clasica.items()},
            "ajustada": {b: _stats(v) for b, v in horiz_ajustada.items()},
        },
        "calendario": {lado: {s: _stats(v) for s, v in d.items()} for lado, d in calendario.items()},
        "trampa": {k: _stats(v) for k, v in trampa.items()},
        "calibracion": calibracion,
    }


def _fila(nombre: str, s: dict) -> str:
    if s["n"] == 0:
        return f"  {nombre:<22} n=0"
    return (f"  {nombre:<22} n={s['n']:<4} pts={s['pts']:.2f}  μ={s['mu']:.2f}  "
            f"residual={s['residual']:+.3f} ± {s['err']:.3f}")


def _tabla(titulo: str, filas: dict, orden: list[str]):
    print(f"\n— {titulo} —")
    for b in orden:
        print(_fila(b, filas[b]))


def main():
    ap = argparse.ArgumentParser(description="Backtest muestreado de la Regresión al Nivel (§5)")
    ap.add_argument("--muestra", type=int, default=300, help="fixtures al azar (default 300, para no saturar)")
    ap.add_argument("--liga", type=int, help="filtrar por league_id (p.ej. 140)")
    ap.add_argument("--temporada", type=int, help="filtrar por league_season")
    ap.add_argument("--desde", help="fecha mínima yyyy-mm-dd")
    ap.add_argument("--hasta", help="fecha máxima yyyy-mm-dd")
    ap.add_argument("--semilla", type=int, default=42, help="semilla del muestreo (reproducible)")
    ap.add_argument("--horizonte", type=int, default=1,
                    help="además del partido: residual medio de los próximos N partidos por bucket")
    ap.add_argument("--calibrar", action="store_true",
                    help="reajustar los 4 coeficientes de μ por OLS sobre la muestra y comparar RMSE")
    a = ap.parse_args()

    r = backtest(a.muestra, a.liga, a.temporada, a.desde, a.hasta, a.semilla, a.horizonte, a.calibrar)
    print(f"Universo: {r['universo']} fixtures terminados · muestra: {r['muestra']} "
          f"· observaciones: {r['observaciones']} (equipo-partido) · sin forma de 5: {r['descartadas']}")
    print("residual = pts reales − μ_partido (rival y localía reales). "
          "Si la ley funciona: mejora → residual > 0, empeora → residual < 0, y fuerte > leve.")

    _tabla("señal CLÁSICA del gap → residual del partido", r["clasica"], BUCKETS_SENAL)
    _tabla("señal AJUSTADA por calendario → residual del partido", r["ajustada"], BUCKETS_SENAL)
    if r["horizonte"]:
        h = r["horizonte"]
        _tabla(f"señal CLÁSICA → residual medio de los PRÓXIMOS {h['n']} partidos", h["clasica"], BUCKETS_SENAL)
        _tabla(f"señal AJUSTADA → residual medio de los PRÓXIMOS {h['n']} partidos", h["ajustada"], BUCKETS_SENAL)
    _tabla("SUBRINDE (gap ≥ +0.3): señal de calendario → residual del SIGUIENTE partido",
           r["calendario"]["subrinde"], ["blando", "neutro", "duro"])
    _tabla("SOBRERINDE (gap ≤ −0.3): señal de calendario → residual del SIGUIENTE partido",
           r["calendario"]["sobrerinde"], ["blando", "neutro", "duro"])
    _tabla("PARTIDO TRAMPA (favorito claro, con vs sin grande a ±4 días) → residual del partido",
           r["trampa"], ["trampa", "favorito sin grande"])
    if r["calibracion"]:
        c = r["calibracion"]
        act = c["actual"]
        print(f"\n— calibración de μ (OLS sobre {c['n']} observaciones, predicción recortada a [0,3]) —")
        print(f"  μ actual : {act['coefs'][0]:+.3f} {act['coefs'][1]:+.3f}·nivel {act['coefs'][2]:+.3f}·rival "
              f"{act['coefs'][3]:+.3f}·localía   RMSE={act['rmse']:.4f}")
        if c["ols"] is None:
            print("  μ OLS    : no se pudo ajustar (muestra insuficiente o matriz singular)")
        else:
            o = c["ols"]
            print(f"  μ OLS    : {o['coefs'][0]:+.3f} {o['coefs'][1]:+.3f}·nivel {o['coefs'][2]:+.3f}·rival "
                  f"{o['coefs'][3]:+.3f}·localía   RMSE={o['rmse']:.4f}")
            print("  (μ es sagrada: estos coeficientes NO se aplican solos — son evidencia para decidir "
                  "una recalibración documentada en MOTOR_SAD_EXTRACCION.md)")

    print("\nUmbrales vigentes: gap 0.3/0.5 · calendario ±0.15 · trampa Δnivel 0.8, ±4 días. "
          "Con n bajos (err alto) ampliar --muestra antes de sacar conclusiones.")


if __name__ == "__main__":
    main()
