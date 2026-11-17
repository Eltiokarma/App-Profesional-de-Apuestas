"""Test de la medición A6 (backend/medir_brecha_efe.py) — sin red.

Arma partes sintéticos y comprueba que la medición separa los tres grupos, cuenta
bien quién gana y no inventa casos con datos faltantes.

    python -m backend.test_medir_brecha_efe
"""
import sys

from backend import medir_brecha_efe as m

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def parte(fid, pa, pb, real, merc, alerta=False):
    return {"fixtureId": fid, "equipos": {"a": {"porcentaje": pa}, "b": {"porcentaje": pb}},
            "alertas": [{"codigo": "EFE-EMPATE-TECNICO"}] if alerta else [{"codigo": "T.54"}],
            "veredicto": {"objetivo": {"unXDos": {"real": real}}},
            "vsMercado": {"seleccion": {k: {"mercado": v} for k, v in zip(("local", "empate", "visita"), merc)}}}


def main():
    partes = [
        parte(1, 70, 50, "local", (55, 25, 20)),               # sin alerta, gana el mayor y el favorito
        parte(2, 70, 50, "visita", (55, 25, 20)),              # sin alerta, pierde el mayor
        parte(3, 72, 55, "visita", (30, 25, 45), alerta=True),  # con alerta: el mayor (local) no gana, la casa sí
        parte(4, 60, 58, "empate", (40, 30, 30)),              # brecha chica
        {"fixtureId": 5, "equipos": {"a": {"porcentaje": 60}, "b": {}}},  # sin porcentaje: fuera
    ]
    casos = [c for c in (m.caso_de_parte(p) for p in partes) if c]
    check("un parte sin porcentaje o sin resultado no entra", len(casos) == 4, len(casos))
    r = m.medir(casos)
    check("tres grupos: con la alerta, brecha ≥ 5 sin ella, y brecha chica",
          (r["conEmpateTecnico"]["partidos"], r["sinAlerta"]["partidos"], r["brechaChica"]["partidos"]) == (1, 2, 1), r)
    check("sin alerta, el mayor EFE ganó 1 de 2", r["sinAlerta"]["ganaElMayorEfe"]["aciertos"] == 1)
    check("con la alerta, el mayor EFE no ganó y el favorito de la casa sí",
          r["conEmpateTecnico"]["ganaElMayorEfe"]["aciertos"] == 0
          and r["conEmpateTecnico"]["ganaElFavoritoDeLaCasa"]["aciertos"] == 1)
    check("el empate no lo gana nadie", r["brechaChica"]["ganaElMayorEfe"]["aciertos"] == 0
          and r["brechaChica"]["ganaElFavoritoDeLaCasa"]["aciertos"] == 0)
    check("cuenta cuántas veces el mayor EFE es el favorito de la casa", r["sinAlerta"]["mayorEfeEsElFavorito"] == 2)
    check("con n el intervalo viene; sin n, None", r["sinAlerta"]["ganaElMayorEfe"]["intervalo"] is not None
          and m.medir([])["sinAlerta"]["ganaElMayorEfe"]["tasa"] is None)
    print("\nTODO OK" if not fallos else f"\n{fallos} FALLAS")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
