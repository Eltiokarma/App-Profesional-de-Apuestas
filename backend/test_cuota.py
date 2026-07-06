"""Test del acumulador de k_cuota (backend/cuota_engine.step_cuota).

    python -m backend.test_cuota
"""
import sys

from backend.cuota_engine import CUOTA0, cuotas_sinteticas, step_cuota

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

    # cuotas sintéticas: local favorito -> su cuota < visita; suma de probs > 1 (margen)
    h, e, a = cuotas_sinteticas(3.0, 1.5)  # local mucho mejor
    check("sintéticas: local favorito (cuota_home < cuota_away)", h < a, (h, e, a))
    check("sintéticas: overround (1/h+1/e+1/a > 1)", (1 / h + 1 / e + 1 / a) > 1.0, (h, e, a))

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
