"""FASE 0 · ¿qué ligas sumar? (29/10/2026, pedido del usuario)

Solo lee la base: 0 requests, 0 tokens, no escribe nada fuera de
$SAD_DATA_DIR/fase0. Va dentro de backend/ porque la imagen de Railway copia
solo esa carpeta (Dockerfile): un script en scripts/ no llega al servidor.

    nohup python -m backend.fase0_ligas > "$SAD_DATA_DIR/fase0.log" 2>&1 &
    tail -1 "$SAD_DATA_DIR/fase0.log"          # «fase 0 terminada» cuando acaba
    cat "$SAD_DATA_DIR/fase0/resumen.txt"

Deja:
1. el inventario por liga: partidos, temporadas, si está en el padrón o es
   menor, de los últimos 60 días cuántos tienen cuotas 1X2 capturadas, y de
   las fichas pedidas cuántas trajeron el once;
2. la μ calibrada por liga (`backtest_gap --por-liga`: localía y peso del
   nivel, la medida de «cuánto se parece a Juliaca»);
3. el reventón liga por liga (`backtest_burbuja --liga`) para Perú 1 y 2 (la
   2 es el control de que en segunda las burbujas fallan más), las cinco
   grandes con sus segundas, y la fase liga de Europa League y Conference;
4. un resumen corto para pegar en el chat.

Los backtests corren en SUBPROCESOS (su memoria vuelve al terminar) y SIN
--calibrar ni --lecciones: esos guardan la guía que leen los partes y la
pisarían con la de una sola liga.
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys

LIGAS_REVENTON = (281, 282, 39, 40, 140, 141, 135, 136, 78, 79, 61, 62, 3, 848)


def carpeta() -> str:
    f = os.path.join(os.environ.get("SAD_DATA_DIR", "."), "fase0")
    os.makedirs(f, exist_ok=True)
    return f


def inventario() -> str:
    from backend.ingesta.extractor import LIGAS, LIGAS_MENORES, ligas_vivo
    ruta = os.path.join(os.environ.get("SAD_DATA_DIR", "."), "sad.db")
    db = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    vivo = ligas_vivo()
    nombres = {i: f"{p or ''} {n or ''}".strip() for i, n, p in db.execute("SELECT id, name, country FROM leagues")}
    fichas = {lid: (n, ali or 0) for lid, n, ali in db.execute(
        "SELECT f.league_id, COUNT(*), SUM(m.alineaciones > 0) FROM fichas_meta m "
        "JOIN fixtures f ON f.id = m.fixture_id GROUP BY f.league_id")}
    filas = db.execute("""
        SELECT f.league_id, COUNT(*), COUNT(DISTINCT f.league_season),
               SUM(f.date >= date('now', '-60 day')),
               SUM(f.date >= date('now', '-60 day') AND EXISTS (
                   SELECT 1 FROM odds o WHERE o.fixture_id = f.id AND o.bet_name = 'Match Winner'))
        FROM fixtures f WHERE f.status_short IN ('FT', 'AET', 'PEN')
        GROUP BY f.league_id HAVING COUNT(*) >= 100 ORDER BY COUNT(*) DESC""").fetchall()
    lineas = [f"{'id':>5}  {'liga':40} {'estado':7} {'jugados':>7} {'temp':>4} {'60d':>4} "
              f"{'cuotas':>7} {'fichas':>6} {'c/once':>7}"]
    for lid, n, temp, u60, c60 in filas:
        estado = "padrón" if lid in vivo else ("menor" if lid in LIGAS_MENORES else "fuera")
        nf, ali = fichas.get(lid, (0, 0))
        nombre = (LIGAS.get(lid) or nombres.get(lid) or f"liga {lid}")[:40]
        lineas.append(f"{lid:>5}  {nombre:40} {estado:7} {n:>7} {temp:>4} {u60 or 0:>4} "
                      f"{(100 * c60 / u60 if u60 else 0):>6.0f}% {nf:>6} {(100 * ali / nf if nf else 0):>6.0f}%")
    return "\n".join(lineas)


def _correr(args: list[str], salida: str) -> None:
    env = {**os.environ, "SAD_SIN_HILOS": "1"}
    with open(salida, "w", encoding="utf-8") as f:
        subprocess.run([sys.executable, "-m", *args], stdout=f, stderr=subprocess.STDOUT, env=env, check=False)


def resumen(f: str) -> str:
    partes = [open(os.path.join(f, "1_inventario.txt"), encoding="utf-8").read(), ""]
    motor = open(os.path.join(f, "2_motor_por_liga.txt"), encoding="utf-8").read()
    i = motor.find("— calibración")
    partes += [motor[i:] if i >= 0 else motor[-3000:], ""]
    partes.append("— reventón por liga: tasa en riesgo bajo · medio · alto · muy alto · AUC · observaciones —")
    for lid in LIGAS_REVENTON:
        ruta = os.path.join(f, f"3_burbuja_{lid}.json")
        try:
            r = json.load(open(ruta, encoding="utf-8"))
        except (OSError, ValueError):
            partes.append(f"  {lid}: sin resultado (ver 3_burbuja_{lid}.txt)")
            continue
        liga = f"{lid} " + (r.get("ligasEvaluadas") or ["sin partidos"])[0][:24]
        pn = r.get("porNivel") or {}
        tasas = " · ".join(f"{100 * pn[nv]['tasa']:.0f}%" if pn.get(nv, {}).get("tasa") is not None else "—"
                           for nv in ("bajo", "medio", "alto", "muy alto"))
        partes.append(f"  {liga:30} {tasas} · AUC {r.get('aucPuntos')} · n {r.get('observaciones')}")
    return "\n".join(partes)


def main() -> int:
    f = carpeta()
    print("1/3 inventario por liga…", flush=True)
    with open(os.path.join(f, "1_inventario.txt"), "w", encoding="utf-8") as out:
        out.write(inventario() + "\n")
    print("2/3 motor por liga (backtest_gap --por-liga)…", flush=True)
    _correr(["backend.backtest_gap", "--por-liga", "60", "--muestra", "800"],
            os.path.join(f, "2_motor_por_liga.txt"))
    for k, lid in enumerate(LIGAS_REVENTON, 1):
        print(f"3/3 reventón liga {lid} ({k}/{len(LIGAS_REVENTON)})…", flush=True)
        _correr(["backend.backtest_burbuja", "--liga", str(lid), "--json", os.path.join(f, f"3_burbuja_{lid}.json")],
                os.path.join(f, f"3_burbuja_{lid}.txt"))
    with open(os.path.join(f, "resumen.txt"), "w", encoding="utf-8") as out:
        out.write(resumen(f) + "\n")
    print(f"fase 0 terminada: {os.path.join(f, 'resumen.txt')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
