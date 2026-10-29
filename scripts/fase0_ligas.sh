#!/usr/bin/env bash
# Uso (consola de Railway, desde la carpeta del repo; la consola web corta lo largo):
#   nohup bash scripts/fase0_ligas.sh > "$SAD_DATA_DIR/fase0.log" 2>&1 &
#   cat "$SAD_DATA_DIR/fase0/resumen.txt"     # cuando el log diga «fase 0 terminada»
#
# FASE 0 · ¿qué ligas sumar? Solo lee la base: 0 requests, 0 tokens, no escribe nada
# fuera de $SAD_DATA_DIR/fase0. Sin --calibrar ni --lecciones: esos guardan la guía
# que leen los partes y la pisarían con la de una sola liga.
export SAD_SIN_HILOS=1
F="${SAD_DATA_DIR:-.}/fase0"; mkdir -p "$F"

# 1) inventario por liga: partidos, temporadas, cuotas y onces
python3 - > "$F/1_inventario.txt" 2>&1 <<'EOF'
import os, sqlite3
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
print(f"{'id':>5}  {'liga':40} {'estado':7} {'jugados':>7} {'temp':>4} {'60d':>4} {'cuotas':>7} {'fichas':>6} {'c/once':>7}")
for lid, n, temp, u60, c60 in filas:
    estado = "padrón" if lid in vivo else ("menor" if lid in LIGAS_MENORES else "fuera")
    nf, ali = fichas.get(lid, (0, 0))
    nombre = (LIGAS.get(lid) or nombres.get(lid) or f"liga {lid}")[:40]
    print(f"{lid:>5}  {nombre:40} {estado:7} {n:>7} {temp:>4} {u60 or 0:>4} "
          f"{(100 * c60 / u60 if u60 else 0):>6.0f}% {nf:>6} {(100 * ali / nf if nf else 0):>6.0f}%")
EOF

# 2) el motor liga por liga: localía y peso del nivel (paridad), hasta 800 partidos por liga
python -m backend.backtest_gap --por-liga 60 --muestra 800 > "$F/2_motor_por_liga.txt" 2>&1

# 3) el reventón liga por liga: Perú 1 y 2 (control de tu intuición), las 5 grandes con su
#    segunda, y la fase liga de la Europa League y la Conference
for L in 281 282 39 40 140 141 135 136 78 79 61 62 3 848; do
  python -m backend.backtest_burbuja --liga "$L" --json "$F/3_burbuja_$L.json" > "$F/3_burbuja_$L.txt" 2>&1
done

# 4) un resumen corto para pegar en el chat
python3 - > "$F/resumen.txt" 2>&1 <<'EOF'
import glob, json, os
F = os.path.join(os.environ.get("SAD_DATA_DIR", "."), "fase0")
print(open(os.path.join(F, "1_inventario.txt")).read())
motor = open(os.path.join(F, "2_motor_por_liga.txt")).read()
print(motor[motor.find("— calibración"):] if "— calibración" in motor else motor[-3000:])
print("— reventón por liga: tasa en riesgo bajo · medio · alto · muy alto · AUC · observaciones —")
for ruta in sorted(glob.glob(os.path.join(F, "3_burbuja_*.json"))):
    try:
        r = json.load(open(ruta))
    except (OSError, ValueError):
        print(f"  {os.path.basename(ruta)}: sin resultado (ver el .txt)")
        continue
    lid = os.path.basename(ruta)[len("3_burbuja_"):-len(".json")]
    liga = f"{lid} " + (r.get("ligasEvaluadas") or ["sin partidos"])[0][:24]
    pn = r.get("porNivel") or {}
    tasas = " · ".join(f"{100 * pn[nv]['tasa']:.0f}%" if pn.get(nv, {}).get("tasa") is not None else "—"
                       for nv in ("bajo", "medio", "alto", "muy alto"))
    print(f"  {liga:30} {tasas} · AUC {r.get('aucPuntos')} · n {r.get('observaciones')}")
EOF
echo "fase 0 terminada: $F/resumen.txt"
