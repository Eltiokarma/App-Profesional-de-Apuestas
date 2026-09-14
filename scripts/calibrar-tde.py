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
import hashlib
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "docs/skills/teorema-del-echado/assets/casos/registro.csv"
# el estado vigente del registro, fijado a mano cuando se declara un alta
SHA_ESPERADO = "4a315dd9ca46db1b265435a214dbfa74545c7e38eeff00d84d1e158a8af0861a"

# las clases que el skill EXCLUYE de toda métrica de frecuencia
CLASES_FUERA = ("rama_abandonada",)
SELECCIONES_FUERA = ("por_resultado", "post_resultado")
# `modo` = cuándo se escribió el análisis. RETRO = con el partido jugado.
MODO_FUERA = "RETRO"
BANDAS = ((3.0, 5.0, "3-5"), (5.0, 7.0, "5-7"), (7.0, 8.5, "7-8.5"))


def num(s):
    """UNA convención para los rangos: el PUNTO MEDIO, en toda columna.

    Antes esto tomaba el extremo bajo para `IE` y el punto medio para
    `p_echada`, así que el mismo caso pesaba distinto según qué se estuviera
    contando. Dos convenciones conviviendo en un script de calibración es un
    sesgo que nadie ve.
    """
    t = str(s or "").strip().replace("%", "")
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*-\s*([0-9]*\.?[0-9]+)\s*$", t)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)", t)
    return float(m.group(1)) if m else None


def prob(s):
    """Las columnas de probabilidad traen CUATRO formatos: «38», «35%», «70-90%»
    y «0.40». Un parser que divida siempre entre 100 lee 0.40 como 0.4%; uno que
    no divida nunca lee 38 como 3800%. Se decide por el valor, no por la forma."""
    v = num(s)
    return None if v is None else (v if v <= 1 else v / 100)


def se_echo(f) -> bool:
    return not f["se_echo"].strip().lower().startswith("no")


def main() -> int:
    if not REGISTRO.exists():
        print(f"no está el registro: {REGISTRO}")
        return 1
    crudo = REGISTRO.read_bytes()
    filas = list(csv.DictReader(REGISTRO.open(encoding="utf-8")))
    sha = hashlib.sha256(crudo).hexdigest()
    print(f"registro: {len(filas)} filas · {filas[0]['id'].strip()} … {filas[-1]['id'].strip()}")
    # EL ESTADO SE IDENTIFICA POR SHA, NO POR CONTEO DE FILAS. De las tres
    # desincronizaciones que ya hubo, dos no cambiaban el conteo: contar filas
    # no habría detectado ni la resincronización de v0.1.7 ni la canonización
    # de categorías. Ver docs/skills/teorema-del-echado/REGISTRO.md.
    print(f"  sha256 {sha[:16]} · {len(crudo)} bytes", end="")
    if sha == SHA_ESPERADO:
        print("  ✓ el esperado")
    else:
        print(f"\n  ⚠ CAMBIÓ: se esperaba {SHA_ESPERADO[:16]}. Si es un alta legítima, "
              f"actualizá SHA_ESPERADO en este script y declará el conteo y los IDs.")

    # HIGIENE: una columna con varias redacciones para el mismo valor fragmenta
    # cualquier agrupación EN SILENCIO. Se avisa antes de contar nada. El
    # registro llegó canonizado a estos vocabularios; si aparece uno nuevo,
    # salta acá antes de que contamine una frecuencia.
    for col, esperado in (("clase_caso", {"normal", "rama_abandonada"}),
                          ("esquema_P", {"sin_esquema", "4ind", "5ind", "6ind"}),
                          ("seleccion", {"ciega", "por_resultado", "post_resultado"}),
                          ("se_echo", {"si", "no", "parcial"}),
                          ("estado_recomputo_esq6",
                           {"hecho", "hecho_sin_procedencia", "no_requiere",
                            "bloqueado", "pre_rubrica"})):
        vistos = {f[col].strip() for f in filas if f[col].strip()}
        raros = sorted(vistos - esperado)
        if raros:
            print(f"  ⚠ `{col}` trae valores fuera del vocabulario canónico: {raros}")

    cerrados = [f for f in filas if f["se_echo"].strip()]
    ciegos = [f for f in cerrados
              if f["seleccion"].strip() not in SELECCIONES_FUERA
              and f["modo_evaluacion"].strip() == "PRE"]
    limpios = [f for f in ciegos if f["clase_caso"].strip().lower() not in CLASES_FUERA]
    # LA EXCLUSIÓN QUE FALTABA. Hay DOS columnas de modo y dicen cosas distintas:
    # `modo_evaluacion` (PRE/COND/RETRO) dice con qué escala se puntuó P1a;
    # `modo` (PRE/RETRO/DECLARADO/CERRADO) dice CUÁNDO se escribió el análisis.
    # Un RETRO se puntuó con el partido jugado, así que no es una predicción:
    # `seleccion = ciega` garantiza que el caso no se eligió porque pasara algo,
    # no que se puntuara a ciegas. Es la misma distinción que la disciplina 31
    # hace para `post_resultado` — allí falla el partido, acá falla el analista.
    computables = [f for f in limpios if f["modo"].strip().upper() != MODO_FUERA]
    fuera = [f["id"].strip() for f in ciegos if f not in limpios]
    fuera_retro = [f["id"].strip() for f in limpios if f not in computables]

    pos = [f for f in computables if se_echo(f)]
    ies = [num(f["IE"]) for f in computables if num(f["IE"]) is not None]
    tasa = 100 * len(pos) / len(computables) if computables else 0.0

    print()
    print(f"ciegos + PRE + cerrados      n={len(ciegos)}")
    print(f"  menos {CLASES_FUERA[0]:18} n={len(limpios)}   (fuera: {', '.join(fuera)})")
    print(f"  menos modo=RETRO           n={len(computables)}   (fuera: {', '.join(fuera_retro)})")
    print(f"  positivos                  {len(pos)}  → tasa base {tasa:.1f}%")
    print(f"  IE medio                   {sum(ies)/len(ies):.2f}")
    print()
    for lo, hi, etiq in BANDAS:
        g = [f for f in computables if lo <= (num(f["IE"]) or -1) < hi]
        e = [f for f in g if se_echo(f)]
        print(f"  banda {etiq:6} n={len(g):2}  positivos={len(e)}  {[x['id'].strip() for x in e]}")

    # la condición (c): los positivos tienen que estar en el esquema VIGENTE
    print()
    # LA (c) SE LEE DE LA COLUMNA, YA NO SE INFIERE. Antes esta distinción vivía
    # en este script: si alguien calculaba la frecuencia con otra herramienta,
    # la perdía. Ahora está en el dato, que es donde tiene que estar.
    #
    # Y hay DOS formas de no estar en el esquema vigente, con salidas opuestas:
    # `bloqueado` es reexpresable y falta una decisión, así que BLOQUEA la (c);
    # `pre_rubrica` no es reexpresable —la fila se puntuó con escala continua y
    # no hay indicadores que convertir— así que no bloquea nada: sale del
    # conteo. Si bloqueara, (c) equivaldría a «nunca», porque esas filas no se
    # pueden arreglar ni con todo el trabajo del mundo.
    viejos = [f["id"].strip() for f in pos
              if f["estado_recomputo_esq6"].strip() == "bloqueado"]
    fuera_conteo = [f["id"].strip() for f in pos
                    if f["estado_recomputo_esq6"].strip() == "pre_rubrica"]
    en_esquema = [f["id"].strip() for f in pos
                  if f["estado_recomputo_esq6"].strip() not in ("bloqueado", "pre_rubrica")]
    from collections import Counter
    est = Counter(f["estado_recomputo_esq6"].strip() for f in filas)
    print()
    print(f"  recomputo al esquema 6: hecho {est['hecho']} · sin procedencia "
          f"{est['hecho_sin_procedencia']} · no requiere {est['no_requiere']} · "
          f"BLOQUEADO {est['bloqueado']}")
    sp = [f["id"].strip() for f in filas
          if f["estado_recomputo_esq6"].strip() == "hecho_sin_procedencia"]
    if sp:
        print(f"    · sin procedencia (valor que no reproduce ni el IE ni v0.1.5): {sp}")
        print("      no contamina: queda fuera del filtro por modo y no es positivo")
    if fuera_conteo:
        print(f"  · positivos PRE-RÚBRICA, fuera del conteo (no reexpresables): {fuera_conteo}")
    if viejos:
        print(f"  ⚠ positivos BLOQUEADOS, que sí bloquean la (c): {viejos}")
    print(f"  → positivos que cuentan para el alta del semáforo: {len(en_esquema)} "
          f"{en_esquema} · hacen falta 5, con ≥2 fuera de la banda 3-5")

    # ¿LOS BLOQUES SON PROMEDIOS POSIBLES DE LA RÚBRICA? Cada indicador vale
    # 0/0.5/1, así que un bloque solo puede valer (m/2)/k. Un valor que no
    # encaja con ningún denominador no se puntuó con la rúbrica de indicadores
    # — se puntuó con una escala continua, y entonces no hay nada que
    # reexpresar. Es lo que pasa con TDE-001…006.
    def _formable(v, nmax, tol=0.006):
        """¿v puede ser el promedio de k indicadores 0/0.5/1, con 1 ≤ k ≤ nmax?

        El denominador es VARIABLE por diseño —un indicador `sin dato` o `n/a`
        sale del promedio— así que el test tiene que barrer k, no clavarlo en
        el nominal. Con k fijo en 4, TDE-025 (F=0.667=2/3) y TDE-026
        (F=0.167=1/6) saldrían marcadas como pre-rúbrica, y son filas de
        rúbrica con un indicador de F fuera del promedio.

        Pero k tampoco puede pasarse del nominal: F tiene 4 indicadores y C y S
        tienen 3, así que promediar sobre 5 o 6 es imposible. El techo es el
        nominal del bloque, no 6 para todos.
        """
        return any(abs((m_ / 2) / k - v) <= tol
                   for k in range(1, nmax + 1) for m_ in range(0, 2 * k + 1))

    pre = []
    for f in filas:
        vals = [(l, num(f[l]), nm) for l, nm in (("F", 4), ("C", 3), ("P", 6), ("S", 3))]
        malos = [l for l, v, nm in vals if v is not None and not _formable(v, nm)]
        if malos:
            pre.append((f["id"].strip(), malos))
    if pre:
        print()
        print(f"  anteriores a la rúbrica de indicadores: {len(pre)} filas")
        for i, malos in pre:
            print(f"    {i}: bloques no formables → {', '.join(malos)}")
        print("    → se puntuaron con escala continua por bloque; no hay indicadores "
              "que reexpresar, así que NO son reexpresables al esquema 6")

    # BRIER Y SU LÍNEA DE BASE. Un Brier suelto no dice nada: hay que compararlo
    # con lo que saca predecir SIEMPRE la tasa base. Si el modelo no le gana a
    # eso, sus probabilidades restan en vez de sumar.
    usable = [(prob(f["p_echada"]), 1 if se_echo(f) else 0)
              for f in computables if prob(f["p_echada"]) is not None]
    if usable:
        br = sum((p - o) ** 2 for p, o in usable) / len(usable)
        tasa_u = sum(o for _, o in usable) / len(usable)
        ref = sum((tasa_u - o) ** 2 for _, o in usable) / len(usable)
        print()
        print(f"  Brier                      {br:.4f}  (n={len(usable)})")
        print(f"  p media declarada          {sum(p for p, _ in usable)/len(usable):.3f}  "
              f"contra {tasa_u:.3f} observado")
        print(f"  Brier de la tasa base      {ref:.4f}  → el módulo "
              f"{'PIERDE' if br > ref else 'gana'} contra no saber nada")
        print(f"  skill score (1 - br/ref)   {1 - br/ref:+.2f}")
        if len([o for _, o in usable if o]) < 5:
            print("  ⚠ con menos de 5 positivos el skill score es ruidoso; lo robusto "
                  "es la brecha entre la p media declarada y la observada")

    # LA VÍA 2, Y LA PRUEBA DE QUE EL FILTRO RETRO NO ES UN CAPRICHO.
    # El ISE tiene positivos de sobra, así que ahí el skill score sí es legible.
    # Si con los RETRO adentro el módulo "predice" y sin ellos no, lo que se
    # estaba midiendo no era capacidad predictiva: era el analista mirando el
    # resultado. Es el contraste que delata la contaminación.
    def _brier(grupo, col_p, col_o):
        u = [(prob(f[col_p]), 0 if f[col_o].strip().lower().startswith("no") else 1)
             for f in grupo if f[col_o].strip()]
        u = [(x, o) for x, o in u if x is not None]
        if not u:
            return None
        br = sum((x - o) ** 2 for x, o in u) / len(u)
        t = sum(o for _, o in u) / len(u)
        ref = sum((t - o) ** 2 for _, o in u) / len(u)
        return dict(n=len(u), pos=sum(o for _, o in u), p=sum(x for x, _ in u) / len(u),
                    obs=t, br=br, ref=ref, skill=(1 - br / ref) if ref else None)

    ciegos2 = [f for f in filas if f["se_expuso"].strip()
               and f["seleccion"].strip() not in SELECCIONES_FUERA
               and f["modo_evaluacion"].strip() == "PRE"
               and f["clase_caso"].strip().lower() not in CLASES_FUERA]
    print()
    print("  vía 2 · ISE → P(sobreexposición)")
    for etq, g in (("con RETRO", ciegos2),
                   ("sin RETRO", [f for f in ciegos2 if f["modo"].strip().upper() != MODO_FUERA])):
        r = _brier(g, "p_sobreexposicion", "se_expuso")
        if not r or r["skill"] is None:
            print(f"    {etq}: sin datos suficientes")
            continue
        print(f"    {etq}  n={r['n']:2} pos={r['pos']} · declara {r['p']*100:.1f}% "
              f"contra {r['obs']*100:.1f}% observado · skill {r['skill']:+.2f}")
    print("    → si el skill cae al sacar los RETRO, lo que medía era el analista "
          "mirando el resultado, no el módulo prediciendo")

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
