"""Test del acumulador de k_cuota (backend/cuota_engine.step_cuota):
el 1X2 y la Doble Oportunidad (1X/12/X2), con sus huecos independientes.

    python -m backend.test_cuota
"""
import sys

from backend.cuota_engine import CUOTA0, CUOTA_K_COLS, cuotas_sinteticas, dc_desde_1x2, step_cuota

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def main():
    st = dict(CUOTA0)
    # M1 local, gana, cuota_v=2.0
    st = step_cuota(st, 1, True, 2.0, 3.3, 3.5)
    check("M1 kv=2 y kv_local=2", st["k_cuota_victoria"] == 2.0 and st["k_cuota_victoria_local"] == 2.0, st)
    check("M1 visita en 0", st["k_cuota_victoria_visita"] == 0.0)
    # M2 local, gana, cuota_v=1.8 -> encadena
    st = step_cuota(st, 1, True, 1.8, 3.3, 3.5)
    check("M2 kv encadena 2->3.8", abs(st["k_cuota_victoria"] - 3.8) < 1e-9)
    check("M2 kv_local encadena 3.8", abs(st["k_cuota_victoria_local"] - 3.8) < 1e-9)
    # M3 local, empata -> victoria revienta, empate arranca
    st = step_cuota(st, 0, True, 2.1, 3.0, 3.4)
    check("M3 kv RESET a 0", st["k_cuota_victoria"] == 0.0 and st["k_cuota_victoria_local"] == 0.0)
    check("M3 ke arranca 3.0", st["k_cuota_empate"] == 3.0 and st["k_cuota_empate_local"] == 3.0)
    # M4 VISITA, pierde -> derrota arranca; empate revienta; _local conservan
    st = step_cuota(st, -1, False, 2.6, 3.2, 4.0)
    check("M4 kd arranca 4.0 (total y visita)", st["k_cuota_derrota"] == 4.0 and st["k_cuota_derrota_visita"] == 4.0)
    check("M4 ke total RESET", st["k_cuota_empate"] == 0.0)
    check("M4 ke_local se CONSERVA en visita (=3.0)", st["k_cuota_empate_local"] == 3.0)
    # M5 SIN cuota -> se salta (todo igual que M4)
    antes = dict(st)
    st = step_cuota(st, 1, True, None, None, None)
    check("M5 sin cuota: estado inalterado", st == antes)
    # M6 VISITA, gana -> victoria arranca; derrota revienta (total y visita); _local conservan
    st = step_cuota(st, 1, False, 2.5, 3.1, 3.6)
    check("M6 kv=2.5 y kv_visita=2.5", st["k_cuota_victoria"] == 2.5 and st["k_cuota_victoria_visita"] == 2.5)
    check("M6 kd RESET (total y visita)", st["k_cuota_derrota"] == 0.0 and st["k_cuota_derrota_visita"] == 0.0)
    check("M6 ke_local sigue conservado (=3.0)", st["k_cuota_empate_local"] == 3.0)

    # --- Doble Oportunidad (1X/12/X2, perspectiva del equipo) ---------------
    check("18 acumuladores (9 del 1X2 + 9 de doble oportunidad)", len(CUOTA_K_COLS) == 18, len(CUOTA_K_COLS))
    d = dict(CUOTA0)
    # D1 local, EMPATA: 1X (no pierde) y X2 (no gana) viven; 12 (no empata) revienta
    d = step_cuota(d, 0, True, None, None, None, 1.3, 1.25, 1.55)
    check("D1 1x=1.3 (no pierde)", d["k_cuota_dc1x"] == 1.3 and d["k_cuota_dc1x_local"] == 1.3, d)
    check("D1 x2=1.55 (no gana)", d["k_cuota_dcx2"] == 1.55)
    check("D1 12 en 0 (empató)", d["k_cuota_dc12"] == 0.0)
    check("D1 el 1X2 no se movió (sin su cuota)", d["k_cuota_empate"] == 0.0)
    # D2 VISITA, gana: 1X y 12 encadenan; X2 revienta; _local se conservan
    d = step_cuota(d, 1, False, None, None, None, 1.4, 1.2, 1.6)
    check("D2 1x encadena 1.3->2.7", abs(d["k_cuota_dc1x"] - 2.7) < 1e-9, d["k_cuota_dc1x"])
    check("D2 1x_local se CONSERVA (=1.3)", d["k_cuota_dc1x_local"] == 1.3)
    check("D2 1x_visita arranca 1.4", d["k_cuota_dc1x_visita"] == 1.4)
    check("D2 12 arranca 1.2 (ganó)", d["k_cuota_dc12"] == 1.2)
    check("D2 x2 RESET (ganó)", d["k_cuota_dcx2"] == 0.0)
    # D3 VISITA, pierde: 1X revienta; 12 encadena; X2 arranca
    d = step_cuota(d, -1, False, None, None, None, 1.45, 1.22, 1.5)
    check("D3 1x RESET (perdió)", d["k_cuota_dc1x"] == 0.0 and d["k_cuota_dc1x_visita"] == 0.0)
    check("D3 12 encadena 1.2->2.42", abs(d["k_cuota_dc12"] - 2.42) < 1e-9, d["k_cuota_dc12"])
    check("D3 x2 arranca 1.5", d["k_cuota_dcx2"] == 1.5)
    check("D3 1x_local sigue conservado (=1.3)", d["k_cuota_dc1x_local"] == 1.3)
    # D4 sin cuota de doble oportunidad -> ese mercado se salta, el 1X2 sí avanza
    antes = dict(d)
    d = step_cuota(d, 1, True, 2.0, 3.3, 3.5)
    check("D4 sin DC: los 9 de doble oportunidad quedan igual",
          all(d[c] == antes[c] for c in CUOTA_K_COLS if "dc" in c))
    check("D4 sin DC: el 1X2 sí avanzó (kv=2.0)", d["k_cuota_victoria"] == 2.0)
    # D5 los dos mercados a la vez, y las rachas 1X ⊃ victoria
    d2 = step_cuota(dict(CUOTA0), 1, True, 2.0, 3.3, 3.5, 1.3, 1.25, 1.55)
    check("D5 mueve los dos mercados", d2["k_cuota_victoria"] == 2.0 and d2["k_cuota_dc1x"] == 1.3, d2)

    # cuotas sintéticas: local favorito -> su cuota < visita; suma de probs > 1 (margen)
    h, e, a = cuotas_sinteticas(3.0, 1.5)  # local mucho mejor
    check("sintéticas: local favorito (cuota_home < cuota_away)", h < a, (h, e, a))
    check("sintéticas: overround (1/h+1/e+1/a > 1)", (1 / h + 1 / e + 1 / a) > 1.0, (h, e, a))
    # doble oportunidad derivada: siempre más barata que cualquiera de sus patas
    c1x, c12, cx2 = dc_desde_1x2(h, e, a)
    check("DC derivada: 1X < min(cuota_home, cuota_draw)", c1x < min(h, e), (c1x, h, e))
    check("DC derivada: 12 < min(cuota_home, cuota_away)", c12 < min(h, a), (c12, h, a))
    check("DC derivada: X2 < min(cuota_draw, cuota_away)", cx2 < min(e, a), (cx2, e, a))
    check("DC derivada: 1/1X ≈ 1/h + 1/e", abs(1 / c1x - (1 / h + 1 / e)) < 0.01, (c1x, h, e))

    # favorito / tapado (ROADMAP_BURBUJAS §3), derivados al leer
    from backend.cuota_engine import favorito_tapado, rol_de_mercado
    check("rol: su cuota de victoria es la menor → favorito; la del rival menor → tapado; pareja → None",
          rol_de_mercado(1.5, 4.0, 6.0) is True and rol_de_mercado(5.0, 3.5, 1.7) is False
          and rol_de_mercado(2.8, 3.0, 2.8) is None and rol_de_mercado(None, 3, 2) is None)
    fs = [
        {"fixtureId": 1, "esLocal": True, "resultado": 1, "cuotaV": 1.5, "cuotaE": 4.0, "cuotaD": 6.0},   # fav, gana
        {"fixtureId": 2, "esLocal": False, "resultado": 1, "cuotaV": 5.0, "cuotaE": 3.5, "cuotaD": 1.7},  # tapado, gana
        {"fixtureId": 3, "esLocal": True, "resultado": 1, "cuotaV": 2.0, "cuotaE": 3.3, "cuotaD": 3.6},   # fav, gana
        {"fixtureId": 4, "esLocal": False, "resultado": 0, "cuotaV": 1.8, "cuotaE": 3.5, "cuotaD": 4.5},  # fav, empata
        {"fixtureId": 5, "esLocal": True, "resultado": 1, "cuotaV": None, "cuotaE": None, "cuotaD": None}, # sin cuota
    ]
    ft = favorito_tapado(fs, {1: 3.0, 2: 2.0, 3: 1.0, 4: 2.5, 5: 2.0})
    check("favorito: (1/1.5)·3 = 2 → sigue en 2 en el partido de tapado → +(1/2)·1 = 2.5 → revienta al empatar",
          [r["k"]["favorito"] for r in ft] == [2.0, 2.0, 2.5, 0.0, 0.0], [r["k"]["favorito"] for r in ft])
    check("tapado: 5·2 = 10 en la sorpresa y se conserva donde es favorito",
          [r["k"]["tapado"] for r in ft] == [0.0, 10.0, 10.0, 10.0, 10.0], [r["k"]["tapado"] for r in ft])
    check("local/visita: el favorito local no se toca con el empate de visita",
          ft[3]["k"]["favoritoLocal"] == 2.5 and ft[3]["k"]["favoritoVisita"] == 0.0, ft[3]["k"])
    check("sin cuota o sin nivel se salta (rol None, nada se mueve)",
          ft[4]["rol"] is None and ft[4]["k"] == ft[3]["k"]
          and favorito_tapado([fs[0]], {})[0]["k"]["favorito"] == 0.0)

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
