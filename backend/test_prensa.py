"""Qué veredictos llevan la crónica de la prensa (backend/analisis/prensa.py, 13/11/2026).

    python -m backend.test_prensa
"""
import sys

from backend.analisis import prensa

fallos = 0
SEL = {1, 4, 5, 10, 32, 960}


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def imp(liga, ronda, copa=False):
    return prensa.importancia(liga, ronda, selecciones=SEL, copa_nacional=copa)


# ── importancia ──────────────────────────────────────────────────────────────
check("selecciones: la Nations League entra", imp(5, "League A - 5"))
check("selecciones: las eliminatorias UEFA al Mundial entran", imp(32, "Group E - 7"))
check("selecciones: los amistosos no", not imp(10, "Friendlies 1"))
check("Champions: la fase de liga no", not imp(2, "League Stage - 5"))
check("Champions: la ÚLTIMA fecha de la fase de liga sí", imp(2, "League Stage - 8"))
check("Champions: el playoff de eliminación sí", imp(2, "Knockout Round Play-offs"))
check("Champions: los octavos sí", imp(2, "Round of 16"))
check("Champions: las previas no", not imp(2, "3rd Qualifying Round"))
check("Champions: el playoff de la previa no", not imp(2, "Play-offs Qualifying"))
check("Conference: los cuartos sí", imp(848, "Quarter-finals"))
check("Conference: la fase de liga no", not imp(848, "League Stage - 6"))
check("Europa League: la última fecha de liga no (solo la de la Champions)", not imp(3, "League Stage - 8"))
check("Libertadores: la final sí", imp(13, "Final"))
check("Libertadores: la fase de grupos no", not imp(13, "Group Stage - 6"))
check("liga: la fecha regular no", not imp(239, "Clausura - 19"))
check("liga: la Regular Season no", not imp(39, "Regular Season - 12"))
check("liga: la liguilla sí", imp(262, "Apertura - Quarter-finals"))
check("liga: los cuadrangulares sí", imp(239, "Clausura - Quadrangulars - 3"))
check("liga: la ronda por el título sí", imp(144, "Championship Round - 3"))
check("liga: la ronda del descenso sí", imp(144, "Relegation Round - 2"))
check("copa nacional: la final sí", imp(143, "Final", copa=True))
check("copa nacional: la semifinal no", not imp(143, "Semi-finals", copa=True))
check("copa nacional: la ronda de 32 no", not imp(143, "Round of 32", copa=True))


# ── el 50 % del día ──────────────────────────────────────────────────────────
def pend(fid, fecha, acerto, prob, importante=""):
    return {"fixtureId": fid, "fecha": fecha, "importante": importante,
            "unXDos": {"acerto": acerto, "probabilidad": prob}}


dia = [pend(1, "d", True, 70), pend(2, "d", False, 45), pend(3, "d", False, 62),
       pend(4, "d", True, 40), pend(5, "d", None, 0), pend(6, "d", True, 55)]
prensa.marcar(dia)
con = sorted(p["fixtureId"] for p in dia if p["prensa"])
check("6 partidos: entran 3 (el 50 %)", len(con) == 3, con)
check("primero los perdidos", {2, 3} <= set(con), con)
check("completa el acertado con MENOS confianza", 4 in con, con)
check("cada uno dice por qué", all(p.get("prensaMotivo") for p in dia))

dia = [pend(1, "d", False, 50), pend(2, "d", False, 70), pend(3, "d", False, 60),
       pend(4, "d", True, 40), pend(5, "d", True, 30)]
prensa.marcar(dia)
con = sorted(p["fixtureId"] for p in dia if p["prensa"])
check("5 partidos: entran 3 (se redondea para arriba)", len(con) == 3, con)
check("con más perdidos que cupo, los más confiados", con == [1, 2, 3], con)

dia = [pend(1, "d", True, 60, "selecciones: torneo oficial"), pend(2, "d", True, 60, "selecciones: torneo oficial"),
       pend(3, "d", True, 60, "selecciones: torneo oficial"), pend(4, "d", False, 50)]
prensa.marcar(dia)
con = sorted(p["fixtureId"] for p in dia if p["prensa"])
check("los importantes entran aunque pasen el 50 %", {1, 2, 3} <= set(con), con)
check("y llenando el cupo, el perdido normal ya no entra", 4 not in con, con)

dia = [pend(1, "a", False, 50), pend(2, "a", True, 50), pend(3, "b", True, 70), pend(4, "b", True, 40)]
prensa.marcar(dia)
con = sorted(p["fixtureId"] for p in dia if p["prensa"])
check("el cupo se cuenta por día, no por corrida", con == [1, 4], con)

print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
sys.exit(1 if fallos else 0)
