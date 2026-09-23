"""Test del reventón de burbuja (backend/analisis/burbuja.py) — sin DB, sin red.

Corre sobre los vectores dorados de scripts/casos_burbuja.json, los MISMOS que
verifica scripts/test-burbuja.ts: si un lado cambia una regla y el otro no,
uno de los dos tests se cae. Los números esperados están calculados a mano
sobre la historia sintética (20 partidos, fusión escrita siguiendo §3.3).

    python -m backend.test_burbuja
"""
import json
import os
import sys

from backend.analisis import burbuja as b

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def cargar():
    ruta = os.path.join(os.path.dirname(__file__), "..", "scripts", "casos_burbuja.json")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def analizar(filas, ctx, **cambios):
    c = {**ctx, **cambios}
    return b.analizar(filas, equipo_id=c["equipoId"], nivel=c["nivel"], bin_=c["bin"],
                      proximo=c["proximo"], plantilla=c["plantilla"], hoy=c["hoy"], nombre=c.get("nombre"))


def fila(i, cond, gf, ga, nivel, k, kl, kv):
    return {"fixtureId": 5000 + i, "fecha": f"2026-02-{i + 1:02d}T20:00:00Z", "condicion": cond,
            "rivalId": 900 + i, "rivalNombre": f"R{i}", "nivelRival": nivel, "golesFavor": gf,
            "golesContra": ga, "esInternacional": False, "fusion": {"k": k, "kLocal": kl, "kVisita": kv}}


def main():
    d = cargar()
    filas, ctx = d["filas"], d["ctx"]
    out = analizar(filas, ctx)

    print("— cabecera —")
    check("20 partidos procesados", out["partidos"] == 20, out["partidos"])
    check("manda la familia total (el backtest la puso por delante); la regla del nivel viaja como dato sin confirmar",
          out["mandan"]["tipo"] == "globales" and out["mandan"]["familias"] == ["total"]
          and out["mandan"]["reglaNivel"]["familias"] == ["visita"] and out["mandan"]["reglaNivel"]["confirmada"] is False, out["mandan"])
    check("el aviso dice que es guía, no probabilidad", "no probabilidad" in out["aviso"])

    print("\n— familia total —")
    t = out["familias"]["total"]
    check("20 partidos en condición", t["partidosEnCondicion"] == 20)
    check("5 reventones cerrados", len(t["reventones"]) == 5, len(t["reventones"]))
    r0 = t["reventones"][0]
    check("1er reventón: + de 2 partidos, K pico 7.5, lo reventó C (3.0) de local 0-1",
          (r0["signo"], r0["partidos"], r0["kPico"], r0["rival"], r0["nivelRival"], r0["condicion"], r0["resultado"])
          == ("+", 2, 7.5, "C", 3.0, "L", "0-1"), r0)
    r2 = t["reventones"][2]
    check("3er reventón: + de 3 partidos, K pico 13.3 (rombo internacional incluido), empate con H",
          (r2["signo"], r2["partidos"], r2["kPico"], r2["rival"], r2["resultado"]) == ("+", 3, 13.3, "H", "1-1"), r2)
    check("un cambio de signo en el mismo partido cierra la burbuja y abre la contraria (fila 3: +7.5 → −3)",
          t["reventones"][0]["fixtureId"] == 1002 and t["reventones"][1]["signo"] == "-")
    print("\n— por período —")
    per = t["historialPorPeriodo"]
    check("sin temporada en las filas: temporada (sin dato) · año 2026 · dt · últimos 20",
          [p["clave"] for p in per] == ["temporada", "anio:2026", "dt", "ultimos20"], [p["clave"] for p in per])
    check("el período sin dato viaja con sinDato, no con un corte inventado",
          per[0]["sinDato"] and per[0]["positivo"] is None, per[0])
    check("año 2026: desde el 1 de enero hasta el 1 de enero siguiente, vigente, los 5 reventones y los 20 partidos",
          per[1]["desde"] == "2026-01-01" and per[1]["hasta"] == "2027-01-01" and per[1]["vigente"]
          and per[1]["reventones"] == 5 and per[1]["partidos"] == 20
          and per[1]["positivo"] == t["historial"]["positivo"], per[1])
    check("con el DT actual (desde 2026-08-07): ningún reventón, referencia vacía con su n",
          per[2]["desde"] == "2026-08-07" and per[2]["reventones"] == 0 and per[2]["positivo"] is None, per[2])
    check("últimos 20 partidos = toda la muestra de 20", per[3]["partidos"] == 20 and per[3]["reventones"] == 5, per[3])
    con_temp = analizar([{**f, "temporada": 2025 if i < 8 else 2026} for i, f in enumerate(filas)], ctx)
    pts = con_temp["familias"]["total"]["historialPorPeriodo"]
    corte = filas[8]["fecha"][:10]
    check("con temporada en las filas hay UNA por temporada, en orden: 2025 (cerrada en el 1.º de 2026) y 2026 (vigente, abierta)",
          pts[0]["clave"] == "temporada:2025" and pts[0]["desde"] == filas[0]["fecha"][:10] and pts[0]["hasta"] == corte
          and not pts[0]["vigente"] and pts[1]["clave"] == "temporada:2026" and pts[1]["desde"] == corte
          and pts[1]["hasta"] == "" and pts[1]["vigente"], pts[:2])
    check("cada temporada cuenta solo lo que reventó dentro de sus fechas, y entre las dos suman la historia",
          pts[0]["partidos"] == 8 and pts[1]["partidos"] == 12 and pts[0]["reventones"] + pts[1]["reventones"] == 5
          and pts[1]["reventones"] == sum(1 for r in t["reventones"] if r["fecha"][:10] >= corte), pts[:2])
    check("los períodos viajan también en la cabecera", [p["clave"] for p in out["periodos"]] == [p["clave"] for p in per])

    hp = t["historial"]["positivo"]
    check("historial +: n=3", hp["n"] == 3, hp)
    check("K pico +: media 8.77 · mediana 7.5 · sin moda · min 5.5 · max 13.3",
          hp["kPico"] == {"media": 8.77, "mediana": 7.5, "moda": None, "min": 5.5, "max": 13.3}, hp["kPico"])
    check("partidos +: media 2.33 · mediana 2 · moda 2",
          (hp["partidos"]["media"], hp["partidos"]["mediana"], hp["partidos"]["moda"]) == (2.33, 2.0, 2.0), hp["partidos"])
    check("nivel del rival que revienta +: media 2.33 · mediana 2.0 · moda 2.0",
          (hp["nivelRival"]["media"], hp["nivelRival"]["mediana"], hp["nivelRival"]["moda"]) == (2.33, 2.0, 2.0), hp["nivelRival"])
    hn = t["historial"]["negativo"]
    check("historial −: n=2, K pico media 8 sin moda, nivel rival media 1.25",
          hn["n"] == 2 and hn["kPico"]["media"] == 8.0 and hn["kPico"]["moda"] is None and hn["nivelRival"]["media"] == 1.25, hn)
    a = t["actual"]
    check("burbuja abierta: + · K 22.1 · 6 partidos · aplica al próximo",
          (a["signo"], a["k"], a["partidos"], a["aplicaAlProximo"]) == ("+", 22.1, 6, True), a)
    check("posición: percentil 100 en K y en racha, K = 2.95× la mediana",
          t["posicion"] == {"percentilK": 100, "percentilRacha": 100, "kSobreMediana": 2.95}, t["posicion"])
    check("rival próximo (2.6) mucho más fuerte que la mediana de reventón (2.0, distancia +0.6) → tramo muy fuerte",
          t["rival"] == {"nivelProximo": 2.6, "medianaReventon": 2.0, "distancia": 0.6, "enZona": True, "tramo": "muy fuerte"}, t["rival"])
    rg = t["riesgo"]
    check("riesgo MUY ALTO con 8 puntos (racha ≥ mediana +1, rival muy fuerte +7; la K no puntúa) y 3 motivos",
          rg["nivel"] == "muy alto" and rg["puntos"] == 8 and len(rg["motivos"]) == 3, rg)
    check("la K se describe pero se declara informativa (no puntúa)",
          any("la K no puntúa" in m and "22.1" in m for m in rg["motivos"]), rg["motivos"])
    check("confianza BAJA: muestra corta (3) y estabilidad inestable la tumban",
          rg["confianza"] == "baja" and any("inestable" in m for m in rg["confianzaMotivos"]), rg["confianzaMotivos"])
    ex = t["extremo"]
    check("ALERTA DE EXTREMO activa: K 22.1 ≥ máximo previo 13.3 y racha 6 ≥ máximo previo 3, sobre 20 partidos",
          ex["activo"] and ex["kRecord"] and ex["rachaRecord"] and ex["partidosHistoria"] == 20
          and ex["maximoPrevio"] == {"kPico": 13.3, "partidos": 3}, ex)
    check("extremo: dos motivos con el N de partidos y un texto que pide no cargar la apuesta",
          len(ex["motivos"]) == 2 and all("20 partidos" in m for m in ex["motivos"])
          and "no cargar la apuesta" in ex["texto"], ex["motivos"])
    check("el extremo NO mueve el riesgo: sigue en 8 puntos (la K no puntúa)", rg["puntos"] == 8)

    print("\n— familia local (no se mueve en el próximo, que es de visita) —")
    lo = out["familias"]["local"]
    check("11 partidos de local", lo["partidosEnCondicion"] == 11)
    check("burbuja abierta + K 9.5, 3 partidos, NO aplica al próximo",
          (lo["actual"]["k"], lo["actual"]["partidos"], lo["actual"]["aplicaAlProximo"]) == (9.5, 3, False), lo["actual"])
    check("sin rival evaluado (otra condición) y motivo explícito",
          lo["rival"] is None and any("otra condición" in m for m in lo["riesgo"]["motivos"]), lo["riesgo"])
    check("riesgo BAJO con 1 punto (solo la racha ≥ mediana; sin rival que puntúe)",
          lo["riesgo"]["nivel"] == "bajo" and lo["riesgo"]["puntos"] == 1, lo["riesgo"])
    check("historial − local: K pico 3.0 repetida → moda 3.0", lo["historial"]["negativo"]["kPico"]["moda"] == 3.0)
    check("percentil K 50 (una de dos por debajo)", lo["posicion"]["percentilK"] == 50, lo["posicion"])
    check("local: K 9.5 < máximo previo 16 y racha 3 < 4 → extremo INACTIVO, sin motivos ni texto",
          lo["extremo"] == {"activo": False, "kRecord": False, "rachaRecord": False, "cerca": False, "partidosHistoria": 11,
                            "maximoPrevio": {"kPico": 16.0, "partidos": 4}, "motivos": [], "texto": ""}, lo["extremo"])

    # CERCA DEL EXTREMO (§10): el caso ADT, sintético y el mismo que en el TS.
    # Diez reventones negativos, récord K 19.54 y racha 4; la abierta en −17.93
    # tras 3 partidos supera (estricto) al 90 % en K y en racha sin ser récord.
    from backend.analisis.burbuja import _extremo
    de_c = [{"kPico": k, "partidos": p} for k, p in
            zip([2, 3, 4, 5, 6, 7, 8, 9, 10, 19.54], [1, 1, 1, 1, 1, 2, 2, 2, 1, 4])]
    base_c = {"kPico": {"max": 19.54}, "partidos": {"max": 4}}
    ce = _extremo(17.93, 3, base_c, 280, "-", de_c)
    check("CERCA: K −17.93 sobre récord −19.54 y racha 3 sobre 4 → cerca, NO activo (la alerta roja no cambia)",
          ce["cerca"] and not ce["activo"] and not ce["kRecord"] and not ce["rachaRecord"], ce)
    check("cerca: dos motivos con el signo de la K, el 90 % y el récord previo, y texto que pide no cargar fuerte",
          ce["motivos"] == ["K -17.93: más baja que el 90 % de las 10 burbujas - que reventaron (récord previo -19.54, a 1.61)",
                            "3 partidos seguidos: más que el 90 % de las 10 burbujas - que reventaron (máximo previo 4)"]
          and ce["texto"].startswith("CERCA DEL EXTREMO") and "no cargar fuerte" in ce["texto"], ce)
    rec = _extremo(26.04, 1, base_c, 280, "-", de_c)
    check("récord negativo: el motivo lleva el signo (K -26.04 … récord previo -19.54) y cerca queda en false",
          rec["activo"] and not rec["cerca"] and rec["motivos"][0].startswith("K -26.04: la más baja")
          and "récord previo -19.54" in rec["motivos"][0], rec)
    lejos = _extremo(9.5, 1, base_c, 280, "-", de_c)
    check("K −9.5 (80 %) y racha 1 → ni extremo ni cerca, sin motivos",
          not lejos["activo"] and not lejos["cerca"] and lejos["motivos"] == [] and lejos["texto"] == "", lejos)

    print("\n— familia visita —")
    vi = out["familias"]["visita"]
    check("9 partidos de visita", vi["partidosEnCondicion"] == 9)
    check("burbuja abierta + K 12.6 · 3 partidos", (vi["actual"]["k"], vi["actual"]["partidos"]) == (12.6, 3))
    check("riesgo MUY ALTO (8) y moda de partidos 1",
          vi["riesgo"]["nivel"] == "muy alto" and vi["historial"]["positivo"]["partidos"]["moda"] == 1.0, vi["riesgo"])

    print("\n— estabilidad —")
    e = out["estabilidad"]
    check("DT de 40 días + 7 movimientos → INESTABLE", e["grado"] == "inestable", e)
    check("dt.dias 40 · bajas 3 (las 3 de Missing Fixture con lectura ruido NO cuentan) · movimientos 4+3",
          e["dt"]["dias"] == 40 and e["bajas"] == 3 and e["movimientos"] == {"llegadas": 4, "salidas": 3, "ventanaDias": 120}, e)
    check("dueños/organización declarado SIN DATO, no rellenado", any("dueños" in s for s in e["sinDato"]))
    est = analizar(filas, ctx, plantilla={**ctx["plantilla"], "entrenador": {"nombre": "Viejo", "desde": "2024-01-01"},
                                          "revolucion": {"llegadas": 1, "salidas": 0, "ventanaDias": 120}})
    check("DT asentado + 1 movimiento → ESTABLE, y la confianza sube a MEDIA (n=3)",
          est["estabilidad"]["grado"] == "estable" and est["familias"]["total"]["riesgo"]["confianza"] == "media", est["estabilidad"])
    trans = analizar(filas, ctx, plantilla={**ctx["plantilla"], "entrenador": {"nombre": "Viejo", "desde": "2024-01-01"},
                                            "revolucion": {"llegadas": 2, "salidas": 1, "ventanaDias": 120}})
    check("3 movimientos → EN TRANSICIÓN", trans["estabilidad"]["grado"] == "en transición")
    vieja = analizar(filas, ctx, plantilla={**ctx["plantilla"], "actualizadoEn": "2026-07-01T00:00:00Z"})
    check("plantilla de hace 77 días: se avisa que el DT y las bajas pueden estar viejos",
          any("77 días" in m for m in vieja["estabilidad"]["motivos"]), vieja["estabilidad"]["motivos"])
    sd = analizar(filas, ctx, plantilla=None)
    check("sin plantilla → grado SIN DATO y la confianza no pasa de MEDIA",
          sd["estabilidad"]["grado"] == "sin dato" and sd["familias"]["total"]["riesgo"]["confianza"] == "media", sd["estabilidad"])

    print("\n— qué constante manda —")
    r8 = analizar(filas, ctx, bin=8)["mandan"]["reglaNivel"]
    check("regla del nivel, bin 8 → globales (como dato, no confirmada)",
          r8["tipo"] == "globales" and r8["familias"] == ["total"] and r8["confirmada"] is False, r8)
    check("regla del nivel, bin 1 → globales (nivel bajo)", analizar(filas, ctx, bin=1)["mandan"]["reglaNivel"]["tipo"] == "globales")
    sp = analizar(filas, ctx, proximo=None)
    check("sin próximo y nivel medio → la regla diría las dos específicas; manda igual la total",
          sp["mandan"]["reglaNivel"]["familias"] == ["local", "visita"] and sp["mandan"]["familias"] == ["total"])
    check("sin próximo: el rival no puntúa y se dice",
          sp["familias"]["total"]["rival"] is None and any("sin próximo" in m for m in sp["familias"]["total"]["riesgo"]["motivos"]))
    lejos = analizar(filas, ctx, proximo={**ctx["proximo"], "nivelRival": 1.5})
    check("rival 1.5 con mediana 2.0 → lejos (0 pts): solo queda la racha, riesgo BAJO (1)",
          lejos["familias"]["total"]["rival"]["tramo"] == "lejos" and lejos["familias"]["total"]["rival"]["enZona"] is False
          and lejos["familias"]["total"]["riesgo"]["nivel"] == "bajo" and lejos["familias"]["total"]["riesgo"]["puntos"] == 1,
          lejos["familias"]["total"]["riesgo"])
    borde = analizar(filas, ctx, proximo={**ctx["proximo"], "nivelRival": 1.85})
    check("tolerancia 0.15: rival 1.85 sigue en zona (+3 → 4, ALTO)",
          borde["familias"]["total"]["rival"]["tramo"] == "zona" and borde["familias"]["total"]["riesgo"]["puntos"] == 4
          and borde["familias"]["total"]["riesgo"]["nivel"] == "alto", borde["familias"]["total"]["riesgo"])
    fuerte = analizar(filas, ctx, proximo={**ctx["proximo"], "nivelRival": 2.3})
    check("rival 2.3 (distancia +0.3) → tramo fuerte (+5 → 6, MUY ALTO)",
          fuerte["familias"]["total"]["rival"]["tramo"] == "fuerte" and fuerte["familias"]["total"]["riesgo"]["puntos"] == 6,
          fuerte["familias"]["total"]["riesgo"])

    print("\n— bordes —")
    vacio = analizar([], ctx)
    check("sin historia: nada abierto, sin reventones, sin riesgo",
          vacio["familias"]["total"]["actual"] is None and vacio["familias"]["total"]["reventones"] == []
          and vacio["familias"]["total"]["riesgo"] is None)
    cero = analizar(filas + [fila(0, "Local", 1, 1, 2.0, 0.0, 0.0, 12.6)], ctx)
    check("último partido en 0 → sin burbuja abierta, y el reventón queda registrado (6)",
          cero["familias"]["total"]["actual"] is None and len(cero["familias"]["total"]["reventones"]) == 6)
    sinbase = analizar([fila(0, "Local", 2, 0, 2.0, 4.0, 4.0, 0.0), fila(1, "Visita", 1, 0, 2.0, 6.8, 4.0, 2.8)], ctx)
    check("burbuja abierta sin reventones previos → riesgo SIN BASE, nunca un número inventado",
          sinbase["familias"]["total"]["riesgo"]["nivel"] == "sin base" and sinbase["familias"]["total"]["posicion"] is None
          and sinbase["familias"]["total"]["extremo"] is None)
    neg = analizar([fila(0, "Local", 0, 1, 1.5, -1.5, -1.5, 0.0), fila(1, "Visita", 1, 1, 1.5, 0.0, -1.5, 0.0),
                    fila(2, "Local", 0, 2, 2.0, -4.0, -4.0, 0.0), fila(3, "Visita", 0, 1, 2.0, -6.0, -4.0, -2.0)],
                   ctx, proximo={**ctx["proximo"], "nivelRival": 1.2}, bin=8)
    tn = neg["familias"]["total"]
    check("burbuja NEGATIVA: signo −, K −6, 2 partidos", (tn["actual"]["signo"], tn["actual"]["k"], tn["actual"]["partidos"]) == ("-", -6.0, 2))
    check("racha de derrotas: se corta ante rivales de nivel ≤ mediana (1.5) → rival 1.2 en zona",
          tn["rival"]["enZona"] is True and any("cortarse" in m for m in tn["riesgo"]["motivos"]), tn)
    check("burbuja −: rival 1.2 con mediana 1.5 es 0.3 más flojo → tramo fuerte (+5) + racha (+1) = 6, MUY ALTO",
          tn["rival"]["tramo"] == "fuerte" and tn["riesgo"]["puntos"] == 6 and tn["riesgo"]["nivel"] == "muy alto", tn["riesgo"])

    print(f"\n{fallos} FALLAS" if fallos else "\nTODO OK")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
