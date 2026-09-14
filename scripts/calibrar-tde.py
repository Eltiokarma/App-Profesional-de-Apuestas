#!/usr/bin/env python3
"""Recalcula la calibración del TDE desde el registro de casos del skill.

    python3 scripts/calibrar-tde.py

Existe porque el número se calculó mal una vez: se promediaron los 21 casos
ciegos y cerrados SIN excluir los `rama_abandonada`, que las disciplinas 24, 27
y 31 del skill sacan de toda métrica de frecuencia. Uno de los dos positivos
era TDE-030, cuya propia lección dice «Excluida de toda metrica de frecuencia»
y cuyo `se_echo` es «repliegue voluntario sostenido desde el 25» — que por la
definición del skill no es una echada sino un bloque bajo ejecutado.

Un número de calibración escrito a mano se vuelve a equivocar. Este se
recalcula y se compara contra el que tiene el backend.
"""
import csv
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "docs/skills/teorema-del-echado/assets/casos/registro.csv"

# las clases que el skill EXCLUYE de toda métrica de frecuencia
CLASES_FUERA = ("rama_abandonada",)
SELECCIONES_FUERA = ("por_resultado", "post_resultado")
BANDAS = ((3.0, 5.0, "3-5"), (5.0, 7.0, "5-7"), (7.0, 8.5, "7-8.5"))


def num(s):
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)", str(s or ""))
    return float(m.group(1)) if m else None


def se_echo(f) -> bool:
    return not f["se_echo"].strip().lower().startswith("no")


def main() -> int:
    if not REGISTRO.exists():
        print(f"no está el registro: {REGISTRO}")
        return 1
    filas = list(csv.DictReader(REGISTRO.open(encoding="utf-8")))
    print(f"registro: {len(filas)} filas · {filas[0]['id'].strip()} … {filas[-1]['id'].strip()}")

    # HIGIENE: una columna con varias redacciones para el mismo valor fragmenta
    # cualquier agrupación EN SILENCIO. Se avisa antes de contar nada.
    for col in ("clase_caso", "esquema_P", "seleccion", "modo_evaluacion"):
        vistos = sorted({f[col].strip() for f in filas if f[col].strip()})
        if col in ("clase_caso",) and len(vistos) > 2:
            print(f"  ⚠ `{col}` tiene {len(vistos)} redacciones: {vistos}")
        elif col == "esquema_P" and len(vistos) > 3:
            print(f"  ⚠ `{col}` tiene {len(vistos)} redacciones para 3 esquemas")

    cerrados = [f for f in filas if f["se_echo"].strip()]
    ciegos = [f for f in cerrados
              if f["seleccion"].strip() not in SELECCIONES_FUERA
              and f["modo_evaluacion"].strip() == "PRE"]
    computables = [f for f in ciegos if f["clase_caso"].strip().lower() not in CLASES_FUERA]
    fuera = [f["id"].strip() for f in ciegos if f not in computables]

    pos = [f for f in computables if se_echo(f)]
    ies = [num(f["IE"]) for f in computables if num(f["IE"]) is not None]
    tasa = 100 * len(pos) / len(computables) if computables else 0.0

    print()
    print(f"ciegos + PRE + cerrados      n={len(ciegos)}")
    print(f"  menos {CLASES_FUERA[0]:18} n={len(computables)}   (fuera: {', '.join(fuera)})")
    print(f"  positivos                  {len(pos)}  → tasa base {tasa:.1f}%")
    print(f"  IE medio                   {sum(ies)/len(ies):.2f}")
    print()
    for lo, hi, etiq in BANDAS:
        g = [f for f in computables if lo <= (num(f["IE"]) or -1) < hi]
        e = [f for f in g if se_echo(f)]
        print(f"  banda {etiq:6} n={len(g):2}  positivos={len(e)}  {[x['id'].strip() for x in e]}")

    # la condición (c): los positivos tienen que estar en el esquema VIGENTE
    print()
    viejos = [f["id"].strip() for f in pos
              if not f["IE_recomputado_esquema6"].strip()
              and "6" not in f["esquema_P"].strip()[:2]]
    if viejos:
        print(f"  ⚠ positivos medidos en un esquema de P que NO es el vigente: {viejos}")
        print("    → no son comparables con las filas nuevas: positivos en esquema 6 = "
              f"{len(pos) - len(viejos)}")

    # contraste con lo que tiene el backend
    sys.path.insert(0, str(RAIZ))
    from backend.analisis.tde import CALIBRACION as C
    print()
    esperado = {"casosComputables": len(computables), "seEcharon": len(pos),
                "tasaObservada": round(tasa, 1)}
    real = {k: C.get(k) for k in esperado}
    if real == esperado:
        print(f"backend AL DÍA con este registro: {real}")
        return 0
    print(f"backend DESALINEADO:\n  registro dice {esperado}\n  backend tiene {real}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
