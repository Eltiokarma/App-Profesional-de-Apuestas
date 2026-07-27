"""Test del chequeo previo del EFE (motor.preflight_efe) — sin red y sin IA.

Lo que blinda: que ANTES de pulsar el botón se pueda ver de dónde va a salir
cada dato y cuántas búsquedas web va a disparar. El candado de análisis frío
solo frena la catástrofe (>6 faltantes); el caso intermedio —4 faltantes son 11
búsquedas y ~medio dólar— se descubría con la factura.

La propiedad que más importa aquí no es el número: es que el preflight y la
corrida real resuelvan las fuentes con la MISMA función. Un preflight que
estimara por su cuenta mentiría en cuanto alguien cambiara el orden en
`_resolver_fuentes`, y una mentira barata en la pantalla del costo es peor que
no tener pantalla.

    python -m backend.test_preflight
"""
import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone

_TMP = tempfile.mkdtemp(prefix="sad-preflight-")
os.environ["SAD_DATA_DIR"] = _TMP
os.environ.pop("SAD_EFE_DEMO", None)
os.environ.pop("API_FOOTBALL_KEY", None)   # sin clave: xi/bajas no se prometen

from backend.analisis import db as efedb  # noqa: E402
from backend.analisis import motor  # noqa: E402

fallos = 0
LOCAL, VISITA, TERCERO = 1, 2, 3
LIGA, TEMP, FIXTURE = 281, 2026, 7001
N_LOCAL, N_VISITA = "Equipo Local", "Equipo Visita"


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def montar():
    con = sqlite3.connect(os.path.join(_TMP, "sad.db"))
    con.executescript("""
        CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE leagues (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date TEXT, status_short TEXT, status_long TEXT,
            league_id INTEGER, league_season INTEGER, league_round TEXT, venue_city TEXT,
            home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
            fulltime_home INTEGER, fulltime_away INTEGER);
    """)
    con.executemany("INSERT INTO teams (id, name) VALUES (?,?)",
                    [(LOCAL, N_LOCAL), (VISITA, N_VISITA), (TERCERO, "Tercero FC")])
    con.execute("INSERT INTO leagues (id, name) VALUES (?, 'Liga Test')", (LIGA,))
    fid = 6000
    for local, visita, gh, ga, f in [(LOCAL, TERCERO, 2, 0, "2026-07-01"),
                                     (TERCERO, LOCAL, 1, 1, "2026-07-08"),
                                     (VISITA, TERCERO, 0, 2, "2026-07-05")]:
        fid += 1
        con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                    "league_round, home_team_id, away_team_id, goals_home, goals_away, fulltime_home, fulltime_away) "
                    "VALUES (?,?, 'FT','Match Finished', ?,?, 'Regular Season - 3', ?,?,?,?,?,?)",
                    (fid, f + " 20:00:00", LIGA, TEMP, local, visita, gh, ga, gh, ga))
    con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                "home_team_id, away_team_id) VALUES (?, '2026-07-30 20:00:00', 'NS','Not Started', ?,?,?,?)",
                (FIXTURE, LIGA, TEMP, LOCAL, VISITA))
    con.commit()
    con.close()


def tipos_por_origen(pf, equipo):
    for e in pf["equipos"]:
        if e["equipo"] == equipo:
            out = {}
            for d in e["datos"]:
                out.setdefault(d["origen"], []).append(d["tipo"])
            return out
    return {}


def main():
    montar()

    # ── 1. sin nada en la despensa: lo local ya está, lo de la web falta ────
    pf = motor.preflight_efe(FIXTURE)
    check("no gasta: devuelve el chequeo sin llamar a ningún modelo", pf["fixtureId"] == FIXTURE)
    check("cubre a los dos equipos", [e["equipo"] for e in pf["equipos"]] == [N_LOCAL, N_VISITA],
          [e["equipo"] for e in pf["equipos"]])
    check("los siete tipos del protocolo, ninguno de menos",
          all(len(e["datos"]) == len(efedb.TIPOS) for e in pf["equipos"]),
          [len(e["datos"]) for e in pf["equipos"]])

    o = tipos_por_origen(pf, N_LOCAL)
    check("tabla/resultados/calendario salen de nuestra base, no de la web",
          set(o.get("local", [])) >= {"tabla", "resultados", "fixture"}, o)
    check("dt/plantel faltan (nadie los cargó): son los que se pagan",
          {"dt", "plantel"} <= set(o.get("falta", [])), o)
    check("sin API_FOOTBALL_KEY, xi/bajas también cuentan como falta (no se promete lo que no hay)",
          {"xi_reciente", "bajas"} <= set(o.get("falta", [])), o)
    check("marca que no hay NADA en la despensa de ese equipo",
          all(e["enDespensa"] is False for e in pf["equipos"]), pf["equipos"])

    frio = pf["faltantes"]
    check("cuenta los faltantes de los DOS equipos", frio == 8, frio)
    check("presupuesto de búsquedas = 3 + 2 × faltantes",
          pf["busquedasPrevistas"] == min(3 + 2 * frio, 18), pf["busquedasPrevistas"])
    check("con 8 faltantes (umbral 6) avisa de que el candado va a bloquear",
          pf["bloqueado"] is True and pf["nivel"] == "frio", (pf["bloqueado"], pf["nivel"]))
    check("y el costo estimado sube con las búsquedas, no es un número fijo",
          pf["costo"]["max"] > 0.4 and pf["costo"]["medido"] is False, pf["costo"])
    check("dice qué tipo falta y en qué equipo (no un 'faltan 8' a secas)",
          any("plantel" in r and N_LOCAL in r for r in pf["recomendaciones"]), pf["recomendaciones"])
    check("y propone la vía gratis de la capa de jugadores",
          any("ingesta.jugadores" in r for r in pf["recomendaciones"]), pf["recomendaciones"])

    # ── 2. con la despensa cargada: el semáforo tiene que moverse ───────────
    for equipo in (N_LOCAL, N_VISITA):
        for tipo in ("dt", "plantel", "xi_reciente", "bajas"):
            efedb.guardar_investigacion(equipo, tipo, f"{tipo} de {equipo}")
    pf2 = motor.preflight_efe(FIXTURE)
    check("con la despensa llena no queda nada que buscar",
          pf2["faltantes"] == 0 and pf2["busquedasPrevistas"] == 0, pf2["faltantes"])
    check("el nivel pasa a caliente y se levanta el bloqueo",
          pf2["nivel"] == "caliente" and pf2["bloqueado"] is False, pf2["nivel"])
    # OJO: sin búsquedas el costo BAJA, pero no cae a cero. La primera versión
    # de esto anunciaba ~$0.05 y una corrida real costó $0.60: el razonamiento
    # se cobra a precio de salida aunque no se busque nada en la web.
    check("sin búsquedas el costo baja respecto al caso con faltantes",
          pf2["costo"]["max"] < pf["costo"]["max"], (pf2["costo"], pf["costo"]))
    check("pero NO se anuncia como gratis: los tokens se pagan igual",
          pf2["costo"]["min"] >= 0.10, pf2["costo"])
    o2 = tipos_por_origen(pf2, N_LOCAL)
    check("lo depositado se declara como despensa, no como 'base'",
          {"dt", "plantel"} <= set(o2.get("despensa", [])), o2)
    check("la despensa NO pisa lo que ya calculábamos (el calendario sigue siendo nuestro)",
          "fixture" in o2.get("local", []), o2)

    # ── 3. un dato vencido pero servible se sirve DICIENDO su edad ──────────
    viejo = (datetime.now(timezone.utc) - timedelta(days=efedb.TTL_HORAS["plantel"] // 24 + 3))
    with efedb.conectar() as con:
        con.execute("UPDATE investigacion SET capturado_en=? WHERE equipo=? AND tipo='plantel'",
                    (viejo.strftime("%Y-%m-%d %H:%M:%S"), N_LOCAL))
        con.commit()
    pf3 = motor.preflight_efe(FIXTURE)
    o3 = tipos_por_origen(pf3, N_LOCAL)
    check("el plantel vencido dentro de la gracia sale como añejo, no como falta",
          "plantel" in o3.get("anejo", []), o3)
    anejo = next(d for d in pf3["equipos"][0]["datos"] if d["tipo"] == "plantel")
    check("y viaja con su edad en días (un dato viejo sin edad sería una mentira cómoda)",
          isinstance(anejo["edadDias"], int) and anejo["edadDias"] > 0, anejo)
    check("un añejo no dispara búsqueda: sigue sin costar", pf3["faltantes"] == 0, pf3["faltantes"])

    # ── 4. el costo pasa de estimado a MEDIDO cuando hay corridas reales ────
    check("sin historia, el costo se declara estimado", pf3["costo"]["medido"] is False, pf3["costo"])
    check("y el estimado SIN búsquedas no es ~0: el razonamiento se paga igual",
          pf3["costo"]["min"] >= 0.10 and pf3["costo"]["max"] >= 0.40, pf3["costo"])
    for costo in (0.06, 0.08, 0.07):
        efedb.registrar_corrida("efe", FIXTURE, 0, {"costo": costo, "busquedas": 0,
                                                    "modelo": "claude-sonnet-5", "input": 1000,
                                                    "output": 2000, "cache_write": 0, "cache_read": 5000,
                                                    "tokens_json": 1500, "tokens_pensamiento": 500})
    pf4 = motor.preflight_efe(FIXTURE)
    check("con tres corridas parecidas, el rango pasa a ser una MEDICIÓN",
          pf4["costo"]["medido"] is True and pf4["costo"]["muestra"] == 3, pf4["costo"])
    check("y es el rango real de lo que costaron",
          pf4["costo"]["min"] == 0.06 and pf4["costo"]["max"] == 0.08, pf4["costo"])
    lejos = efedb.costo_medido("efe", 8)
    check("las corridas de otro tamaño no contaminan la medición", lejos[2] == 0, lejos)

    # ── 4b. el gasto YA hecho: mirada hacia atrás, no estimación ────────────
    efedb.registrar_corrida("timeline", FIXTURE, 0, {"costo": 0.05, "busquedas": 0,
                                                     "modelo": "haiku", "input": 500, "output": 900,
                                                     "cache_write": 0, "cache_read": 0,
                                                     "tokens_json": 800, "tokens_pensamiento": 100})
    g = pf4 and motor.preflight_efe(FIXTURE)["gasto"]
    check("suma TODAS las corridas del partido, no solo la última",
          g["corridas"] == 4 and abs(g["total"] - 0.26) < 1e-6, g["total"])
    check("y las desglosa por tipo (un EFE regenerado tres veces se ve)",
          {t["tipo"]: t["corridas"] for t in g["porTipo"]} == {"efe": 3, "timeline": 1},
          g["porTipo"])
    check("cada corrida trae el reparto del output: JSON vs razonamiento",
          all("tokens_json" in c and "tokens_pensamiento" in c for c in g["ultimas"]),
          list(g["ultimas"][0]) if g["ultimas"] else None)
    check("el gasto ya hecho encabeza las recomendaciones (es lo primero que se mira)",
          motor.preflight_efe(FIXTURE)["recomendaciones"][0].startswith("Ya gastado en este partido"),
          motor.preflight_efe(FIXTURE)["recomendaciones"][0])
    check("un partido sin corridas no inventa un gasto",
          efedb.gasto_de_fixture(424242)["total"] == 0.0)

    # el reparto json/pensamiento se calcula de los chars REALES y suma justo
    # el output cobrado (si no sumara, el desglose mentiría sobre la factura)
    uso = {"output": 10_000, "chars_json": 2_000, "chars_pensamiento": 8_000}
    chars = uso["chars_json"] + uso["chars_pensamiento"]
    tj = round(uso["output"] * uso["chars_json"] / chars)
    check("el reparto reconstruye exactamente el output cobrado",
          tj + (uso["output"] - tj) == uso["output"] and tj == 2000, tj)

    # ── 5. no divergir de la corrida real ──────────────────────────────────
    # el preflight y generar_efe llaman a la MISMA función: se comprueba que lo
    # que el preflight declara faltante es exactamente lo que la corrida real
    # mandaría a buscar.
    fx = motor._fixture(FIXTURE)
    real = motor._resolver_fuentes(fx, con_api=False)
    faltan_real = len(real["equipo_a"]["faltan"]) + len(real["equipo_b"]["faltan"])
    check("los faltantes del preflight son los mismos que resolvería la corrida",
          faltan_real == pf4["faltantes"], (faltan_real, pf4["faltantes"]))

    # ── 6. un análisis ya emitido no se vuelve a pagar por mirarlo ──────────
    # con contenido real: un análisis en ceros se purga solo (es regenerable),
    # y entonces no habría nada de lo que avisar
    from backend.analisis import demo as efedemo
    efedb.guardar_analisis("efe", FIXTURE, N_LOCAL, N_VISITA, "2026-07-30", "preliminar",
                           efedemo.efe_demo(N_LOCAL, N_VISITA, "Liga Test", "2026-07-30"), "1.5")
    pf5 = motor.preflight_efe(FIXTURE)
    check("avisa de que ya hay EFE guardado (verlo cuesta 0)",
          pf5["yaExiste"] is True and any("cuesta 0" in r for r in pf5["recomendaciones"]),
          pf5["recomendaciones"])

    # ── 7. modo demo: no se estima un costo que no existe ──────────────────
    os.environ["SAD_EFE_DEMO"] = "1"
    try:
        pfd = motor.preflight_efe(FIXTURE)
        check("en demo el costo es 0 y se dice, en vez de simular un semáforo",
              pfd["demo"] is True and pfd["costo"]["max"] == 0.0, pfd["costo"])
    finally:
        os.environ.pop("SAD_EFE_DEMO", None)

    # ── 8. un fixture inexistente no inventa un chequeo ─────────────────────
    try:
        motor.preflight_efe(999999)
        check("un fixture que no existe levanta FixtureNoExiste", False)
    except motor.FixtureNoExiste:
        check("un fixture que no existe levanta FixtureNoExiste", True)

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
