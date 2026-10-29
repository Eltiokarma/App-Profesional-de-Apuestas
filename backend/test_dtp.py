"""Test del DTP (backend/analisis/motor.py, fase B) — sin red y sin API.

Blinda las dos reglas que le dan valor a la cadena y que son fáciles de romper
sin que salte ningún error:

1. **Anti-hindsight**: el cierre de N−1 solo contrasta contra un pronóstico
   escrito ANTES de que N−1 se jugara. Sin él, veredicto vacío.
2. **Sin búsqueda web**: el DTP razona sobre la ficha de partido; lo que falte
   se declara. Si un día alguien pone con_busqueda=True, esto lo caza.

    python -m backend.test_dtp
"""
import os
import sqlite3
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="sad-dtp-")
os.environ["SAD_DATA_DIR"] = _TMP

from backend.analisis import db as efedb  # noqa: E402
from backend.analisis import motor  # noqa: E402
from backend.analisis.esquemas import DTP, ajustar  # noqa: E402
from backend.ingesta.ficha_partido import guardar_alineaciones, guardar_eventos, preparar_tablas  # noqa: E402

fallos = 0
FOCO, RIVAL, OTRO = 100, 200, 300


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


LINEUPS = [
    {"team": {"id": FOCO}, "coach": {"name": "DT Foco"}, "formation": "4-3-3",
     "startXI": [{"player": {"id": 1 + i, "name": f"J{i}", "number": i + 1,
                             "pos": "G" if i == 0 else "D" if i < 5 else "M" if i < 8 else "F",
                             "grid": f"{1 if i == 0 else 2 if i < 5 else 3 if i < 8 else 4}:{(i % 4) + 1}"}}
                 for i in range(11)],
     "substitutes": []},
    {"team": {"id": RIVAL}, "coach": {"name": "DT Rival"}, "formation": "3-5-2",
     "startXI": [{"player": {"id": 51, "name": "R1", "number": 1, "pos": "G", "grid": "1:1"}}],
     "substitutes": []},
]
EVENTOS = [{"time": {"elapsed": 34, "extra": None}, "team": {"id": RIVAL},
            "player": {"id": 51, "name": "R1"}, "assist": {"id": None, "name": None},
            "type": "Goal", "detail": "Normal Goal"}]


def sad() -> sqlite3.Connection:
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.executescript("""
        CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS leagues (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT,
            status_long TEXT, league_id INTEGER, league_season INTEGER, home_team_id INTEGER,
            away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER);
    """)
    preparar_tablas(con)
    return con


def montar():
    con = sad()
    con.executemany("INSERT OR REPLACE INTO teams (id, name) VALUES (?,?)",
                    [(FOCO, "Equipo Foco"), (RIVAL, "Equipo Rival"), (OTRO, "Otro Equipo")])
    con.execute("INSERT OR REPLACE INTO leagues (id, name) VALUES (1,'Liga Test')")
    con.executemany(
        "INSERT OR REPLACE INTO fixtures (id, date, status_short, status_long, league_id, "
        "league_season, home_team_id, away_team_id, goals_home, goals_away) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [(10, "2026-07-05 20:00:00", "FT", "Match Finished", 1, 2026, FOCO, OTRO, 2, 0),
         (11, "2026-07-12 20:00:00", "FT", "Match Finished", 1, 2026, OTRO, FOCO, 1, 1),  # el N−1
         (12, "2026-07-19 20:00:00", "NS", "Not Started", 1, 2026, FOCO, RIVAL, None, None)],  # el N
    )
    guardar_alineaciones(con, 11, LINEUPS)
    guardar_eventos(con, {"fixture_id": 11, "eventos": EVENTOS})
    con.commit()
    con.close()


def main():
    montar()

    # ── cronología de la cadena ────────────────────────────────────────────
    check("N = posición cronológica del equipo en la temporada",
          motor._partido_n(FOCO, "2026-07-19 20:00:00") == 3, motor._partido_n(FOCO, "2026-07-19 20:00:00"))
    ant = motor._anterior_de(FOCO, "2026-07-19 20:00:00")
    check("N−1 = último TERMINADO antes de la fecha", ant and ant["id"] == 11, ant and ant["id"])

    # ── el payload: sin web, con la ficha, y avisando de lo que falta ──────
    capturado = {}

    def falso_analizar(payload, esquema, con_busqueda, **kw):
        capturado.update(payload=payload, con_busqueda=con_busqueda, salida=kw.get("salida"))
        return ajustar({"apertura": {"m1": {"sistema": "4-3-3"},
                                     "m2": {"choque_sistemas": "4-3-3 vs 3-5-2"}},
                        "cierre": {"m4_goles": [{"gol": "0-1", "minuto": 34}],
                                   "m5": {"peligro_real": "dos llegadas"},
                                   "registro": {"veredicto": "parcial", "leccion": "x"}}}, DTP), {}

    motor.cliente.analizar = falso_analizar
    motor.cliente.hay_clave = lambda: True

    dto = motor.generar_dtp(12, FOCO)
    check("nunca busca en la web", capturado["con_busqueda"] is False, capturado["con_busqueda"])
    p = capturado["payload"]
    check("sin apertura previa → modo dtp_apertura", p["modo"] == "dtp_apertura", p["modo"])
    check("avisa de que no puede haber veredicto (anti-hindsight)",
          "aviso_cadena" in p, sorted(p))
    check("declara lo que falta en vez de inventarlo",
          "apertura_previa" in p["campos_faltantes"] and "xi_oficial_n" in p["campos_faltantes"],
          p["campos_faltantes"])
    check("lleva la ficha del partido anterior (M4)",
          p["datos_cacheados"]["anterior"]["ficha"]["capturada"] is True,
          p["datos_cacheados"]["anterior"])
    check("y su marcador real", p["datos_cacheados"]["anterior"]["partido"]["marcador"] == "1-1",
          p["datos_cacheados"]["anterior"]["partido"])
    check("con grid, no avisa de carriles aproximados", "aviso_carriles" not in p, sorted(p))

    # ── qué quedó escrito en la cadena ─────────────────────────────────────
    check("el DTO trae la apertura del partido N", bool(dto["resultado"]["apertura"]), dto)
    esl_n = efedb.eslabon("Equipo Foco", 3)
    check("la apertura se escribe en el eslabón N", bool(esl_n and esl_n["apertura"]), esl_n)
    esl_ant = efedb.eslabon("Equipo Foco", 2)
    check("el CIERRE se escribe en el eslabón N−1, no en el de N",
          bool(esl_ant and esl_ant["cierre"]) and not (esl_n or {}).get("cierre"),
          {"n-1": bool(esl_ant and esl_ant["cierre"]), "n": bool((esl_n or {}).get("cierre"))})
    check("un eslabón con cierre pero sin apertura NO cuenta como DTP listo",
          motor._dto_dtp(esl_ant) is None, esl_ant)

    # ── anti-hindsight: una apertura escrita antes NO se pisa ──────────────
    efedb.guardar_cadena("Equipo Foco", 2, "Otro Equipo", "2026-07-12", 11,
                         {"m1": {"sistema": "PRONÓSTICO ORIGINAL"}})
    efedb.guardar_cadena("Equipo Foco", 2, "Otro Equipo", "2026-07-12", 11,
                         {"m1": {"sistema": "REESCRITO DESPUÉS DEL PARTIDO"}})
    esl = efedb.eslabon("Equipo Foco", 2)
    check("la apertura previa no se puede reescribir a posteriori",
          esl["apertura"]["m1"]["sistema"] == "PRONÓSTICO ORIGINAL", esl["apertura"])

    # ── con apertura previa, el modo cambia a completo ─────────────────────
    capturado.clear()
    motor.generar_dtp(12, FOCO)
    p = capturado["payload"]
    check("con apertura previa → modo dtp_completo", p["modo"] == "dtp_completo", p["modo"])
    check("y la lleva en datos_cacheados para M5",
          p["datos_cacheados"]["apertura_previa"]["m1"]["sistema"] == "PRONÓSTICO ORIGINAL",
          p["datos_cacheados"]["apertura_previa"])
    check("ya no avisa de la cadena rota", "aviso_cadena" not in p, sorted(p))

    # ── sin grid: M2 no puede hablar de carriles y se le dice ──────────────
    con = sad()
    con.execute("UPDATE alineaciones SET grid=NULL WHERE fixture_id=11")
    con.commit()
    con.close()
    capturado.clear()
    motor.generar_dtp(12, FOCO)
    check("sin grid, ordena no inventar duelos por carril",
          "aviso_carriles" in capturado["payload"], sorted(capturado["payload"]))

    # ── sin ficha ninguna: se niega en vez de pagar por inventar ───────────
    con = sad()
    con.execute("DELETE FROM alineaciones")
    con.execute("DELETE FROM fixture_eventos")
    con.commit()
    con.close()
    try:
        motor.generar_dtp(12, FOCO)
        check("sin ficha del anterior ni XI, se niega a abrir", False, "no lanzó excepción")
    except RuntimeError as e:
        check("sin ficha del anterior ni XI, se niega a abrir", "ficha_partido" in str(e), str(e))

    # ── el equipo tiene que jugar el partido ───────────────────────────────
    try:
        motor.generar_dtp(12, OTRO)
        check("un equipo que no juega el fixture → error", False, "no lanzó excepción")
    except motor.FixtureNoExiste:
        check("un equipo que no juega el fixture → error", True)

    # EJE-DEBUTANTE del EFE v1.7: la pareja con UNA titularidad junta también es nueva
    from backend.analisis.dtp_cowork import parejas_nuevas_de
    _xi = [{"jugadorId": 1, "nombre": "A", "posicion": "D"}, {"jugadorId": 2, "nombre": "B", "posicion": "D"},
           {"jugadorId": 3, "nombre": "C", "posicion": "D"}, {"jugadorId": 9, "nombre": "Z", "posicion": "F"}]
    _pn = parejas_nuevas_de(_xi, [{1, 2, 3}, {1, 2}, {2, 3}, {5, 6}])
    check("EJE-DEBUTANTE v1.7: ≤ 1 vez juntos es pareja nueva, 2+ no; otras líneas no cuentan",
          sorted((tuple(x["jugadores"]), x["vecesJuntos"]) for x in _pn) == [(("A", "C"), 1)], _pn)
    check("sin onces previos no se inventa una pareja nueva", parejas_nuevas_de(_xi, []) == [])
    # 623: el último once (el XI de referencia) cuenta como partido juntos
    import backend.analisis.dtp_cowork as _dc623
    _onces623 = {10: {1, 2, 3}, 11: {1, 3}, 12: {1, 3}}
    _ant623, _tit623 = _dc623._anteriores, _dc623._titulares
    _dc623._anteriores = lambda t, f, n: [{"id": i} for i in (10, 11, 12)][:n]
    _dc623._titulares = lambda fx, t: [{"player_id": p} for p in _onces623[fx]]
    try:
        _pn623 = {tuple(x["jugadores"]): x["vecesJuntos"] for x in _dc623._parejas_nuevas(1, "2026-10-25", _xi)}
    finally:
        _dc623._anteriores, _dc623._titulares = _ant623, _tit623
    check("623: la pareja que debutó en el último once tiene 1 partido juntos; la de 3 no es nueva",
          _pn623 == {("A", "B"): 1, ("B", "C"): 1}, _pn623)
    # 777 (Carabobo): de los últimos partidos solo uno tiene hoja → no se juzga;
    # los onces se buscan entre más partidos hasta juntar los que hacen falta
    _onces777 = {10: {1, 2, 3}, 11: set(), 12: set(), 13: set(), 14: set(), 15: {1, 2, 3}, 16: {1, 2, 3}}
    _dc623._anteriores = lambda t, f, n: [{"id": i} for i in range(10, 17)][:n]
    _dc623._titulares = lambda fx, t: [{"player_id": p} for p in _onces777[fx]]
    try:
        _dc623._anteriores = lambda t, f, n: [{"id": i} for i in range(10, 15)][:n]
        _pn777a = _dc623._parejas_nuevas(1, "2026-10-25", _xi)
        _dc623._anteriores = lambda t, f, n: [{"id": i} for i in range(10, 17)][:n]
        _pn777b = _dc623._parejas_nuevas(1, "2026-10-25", _xi)
    finally:
        _dc623._anteriores, _dc623._titulares = _ant623, _tit623
    check("777: con un solo once con hoja no se marca ninguna pareja nueva (Carabobo)", _pn777a == [], _pn777a)
    check("777: los onces sin hoja no cuentan; con 3 onces de 7 partidos, los fijos no son pareja nueva",
          _pn777b == [], _pn777b)
    # 540: un partido reprogramado no pierde su apertura en la cadena
    efedb.guardar_cadena("Reprogramado FC", 5, "Rival A", "2026-10-14", 9001, {"m1": {"sistema": "4-4-2"}})
    efedb.guardar_cadena("Reprogramado FC", 5, "Rival B", "2026-10-18", 9002, {"m1": {"sistema": "3-5-2"}})
    _e1, _e2 = efedb.eslabon_de_fixture("Reprogramado FC", 9001), efedb.eslabon_de_fixture("Reprogramado FC", 9002)
    check("540: el partido que toma el número de uno reprogramado no hereda ni borra su apertura",
          (_e1 or {}).get("apertura", {}).get("m1", {}).get("sistema") == "4-4-2"
          and (_e2 or {}).get("apertura", {}).get("m1", {}).get("sistema") == "3-5-2"
          and _e2["partidoN"] == 5, (_e1, _e2))
    efedb.guardar_cadena("Reprogramado FC", 7, "Rival A", "2026-10-21", 9001, {"m1": {"sistema": "5-4-1"}})
    _e1b = efedb.eslabon_de_fixture("Reprogramado FC", 9001)
    check("540: re-guardar el reprogramado con su número nuevo conserva la primera apertura y se mueve",
          _e1b["partidoN"] == 7 and _e1b["apertura"]["m1"]["sistema"] == "4-4-2"
          and [x["fixtureId"] for x in efedb.cadena_de("Reprogramado FC")] == [9001, 9002], _e1b)
    from backend.analisis.dtp_cowork import rehacer as _reh
    _b559 = {"equipo": "a", "apertura": {"m1": {"sistema": "4-2-3-1", "xiReferencia": ""}}}
    _r559 = _reh(_b559, {"a": {"formacion": "3-4-3", "formacionAlCerrar": "4-2-3-1", "titulares": [], "defensores": 3}})
    _r559b = _reh(_b559, {"a": {"formacion": "3-4-3", "titulares": [], "defensores": 3}})
    check("559: si la apertura cuadraba con la formación al cerrar y la API la corrigió después, no pide rehacer",
          not any(m.startswith("sistema") for m in _r559["motivos"]) and _r559.get("formacionCorregidaPorLaApi")
          and any(m.startswith("sistema") for m in _r559b["motivos"]), (_r559, _r559b))
    from backend.analisis.dtp_cowork import sin_referencia
    check("527: una nota entre paréntesis con «sin dato» no anula el XI de referencia",
          not sin_referencia("A, B, C, D, E, F, G, H, I, J (el undécimo titular no viene en la ficha: sin dato)")
          and sin_referencia("sin XI de referencia") and sin_referencia("(sin dato)"))

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
