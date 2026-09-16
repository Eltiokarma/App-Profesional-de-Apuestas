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
    check("nivel medio (bin 5) → mandan las específicas de la condición del próximo (visita)",
          out["mandan"]["tipo"] == "especificas" and out["mandan"]["familias"] == ["visita"], out["mandan"])
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
    check("rival próximo (2.6) en zona de reventón (mediana 2.0, distancia +0.6)",
          t["rival"] == {"nivelProximo": 2.6, "medianaReventon": 2.0, "distancia": 0.6, "enZona": True}, t["rival"])
    rg = t["riesgo"]
    check("riesgo MUY ALTO con 7 puntos (K ≥ mediana +2, > máximo +1, racha ≥ mediana +1, > máxima +1, rival en zona +2)",
          rg["nivel"] == "muy alto" and rg["puntos"] == 7 and len(rg["motivos"]) == 5, rg)
    check("confianza BAJA: muestra corta (3) y estabilidad inestable la tumban",
          rg["confianza"] == "baja" and any("inestable" in m for m in rg["confianzaMotivos"]), rg["confianzaMotivos"])

    print("\n— familia local (no se mueve en el próximo, que es de visita) —")
    lo = out["familias"]["local"]
    check("11 partidos de local", lo["partidosEnCondicion"] == 11)
    check("burbuja abierta + K 9.5, 3 partidos, NO aplica al próximo",
          (lo["actual"]["k"], lo["actual"]["partidos"], lo["actual"]["aplicaAlProximo"]) == (9.5, 3, False), lo["actual"])
    check("sin rival evaluado (otra condición) y motivo explícito",
          lo["rival"] is None and any("otra condición" in m for m in lo["riesgo"]["motivos"]), lo["riesgo"])
    check("riesgo MEDIO con 2 puntos (K por encima del mínimo, racha ≥ mediana)",
          lo["riesgo"]["nivel"] == "medio" and lo["riesgo"]["puntos"] == 2, lo["riesgo"])
    check("historial − local: K pico 3.0 repetida → moda 3.0", lo["historial"]["negativo"]["kPico"]["moda"] == 3.0)
    check("percentil K 50 (una de dos por debajo)", lo["posicion"]["percentilK"] == 50, lo["posicion"])

    print("\n— familia visita —")
    vi = out["familias"]["visita"]
    check("9 partidos de visita", vi["partidosEnCondicion"] == 9)
    check("burbuja abierta + K 12.6 · 3 partidos", (vi["actual"]["k"], vi["actual"]["partidos"]) == (12.6, 3))
    check("riesgo MUY ALTO (7) y moda de partidos 1",
          vi["riesgo"]["nivel"] == "muy alto" and vi["historial"]["positivo"]["partidos"]["moda"] == 1.0, vi["riesgo"])

    print("\n— estabilidad —")
    e = out["estabilidad"]
    check("DT de 40 días + 7 movimientos → INESTABLE", e["grado"] == "inestable", e)
    check("dt.dias 40 · bajas 2 · movimientos 4+3", e["dt"]["dias"] == 40 and e["bajas"] == 2 and e["movimientos"] == {"llegadas": 4, "salidas": 3, "ventanaDias": 120}, e)
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
    check("bin 8 → globales", analizar(filas, ctx, bin=8)["mandan"] == {"tipo": "globales", "familias": ["total"],
          "motivo": "nivel alto (bin 8): pesan más las constantes globales"})
    check("bin 1 → globales (nivel bajo)", analizar(filas, ctx, bin=1)["mandan"]["tipo"] == "globales")
    sp = analizar(filas, ctx, proximo=None)
    check("sin próximo y nivel medio → las dos específicas", sp["mandan"]["familias"] == ["local", "visita"])
    check("sin próximo: el rival no puntúa y se dice",
          sp["familias"]["total"]["rival"] is None and any("sin próximo" in m for m in sp["familias"]["total"]["riesgo"]["motivos"]))
    lejos = analizar(filas, ctx, proximo={**ctx["proximo"], "nivelRival": 1.5})
    check("rival 1.5 con mediana 2.0 → fuera de zona, riesgo baja a ALTO (5)",
          lejos["familias"]["total"]["rival"]["enZona"] is False and lejos["familias"]["total"]["riesgo"]["nivel"] == "alto"
          and lejos["familias"]["total"]["riesgo"]["puntos"] == 5, lejos["familias"]["total"]["riesgo"])
    borde = analizar(filas, ctx, proximo={**ctx["proximo"], "nivelRival": 1.85})
    check("tolerancia 0.15: rival 1.85 sigue en zona", borde["familias"]["total"]["rival"]["enZona"] is True)

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
          sinbase["familias"]["total"]["riesgo"]["nivel"] == "sin base" and sinbase["familias"]["total"]["posicion"] is None)
    neg = analizar([fila(0, "Local", 0, 1, 1.5, -1.5, -1.5, 0.0), fila(1, "Visita", 1, 1, 1.5, 0.0, -1.5, 0.0),
                    fila(2, "Local", 0, 2, 2.0, -4.0, -4.0, 0.0), fila(3, "Visita", 0, 1, 2.0, -6.0, -4.0, -2.0)],
                   ctx, proximo={**ctx["proximo"], "nivelRival": 1.2}, bin=8)
    tn = neg["familias"]["total"]
    check("burbuja NEGATIVA: signo −, K −6, 2 partidos", (tn["actual"]["signo"], tn["actual"]["k"], tn["actual"]["partidos"]) == ("-", -6.0, 2))
    check("racha de derrotas: se corta ante rivales de nivel ≤ mediana (1.5) → rival 1.2 en zona",
          tn["rival"]["enZona"] is True and any("cortarse" in m for m in tn["riesgo"]["motivos"]), tn)
    check("K −6 supera la única K pico previa (1.5): puntúa como mediana y máximo",
          tn["riesgo"]["puntos"] == 7 and tn["riesgo"]["nivel"] == "muy alto", tn["riesgo"])

    print(f"\n{fallos} FALLAS" if fallos else "\nTODO OK")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
