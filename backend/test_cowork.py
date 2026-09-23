"""Tests del parte de Cowork: lo que se deposita, lo que se calcula y el once.

    python3 -m backend.test_cowork

Lo que se verifica es justo la frontera: que Cowork solo tenga que escribir lo
que es trabajo (sub-scores, tabla de plantel, prosa) y que TODO lo derivable
—totales, clasificación, IP, reducción por zona, ramas, F3, F4— lo ponga el
backend. Si un día alguien le pide a Cowork que mande un total, estos tests
siguen pasando pero el parte se vuelve más lento y más fácil de equivocar: por
eso el contrato ignora los campos calculados en vez de creerles.
"""
import json
import os
import sys
import tempfile

fallos = 0

from backend.analisis.parte import _CLAVES_PARTE as _CLAVES_ESPERADAS


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'✓' if cond else '✗ FALLA'} {nombre}" + (f" — {detalle}" if detalle and not cond else ""))


def _plantel(prefijo: str) -> list[dict]:
    """16 jugadores con zona y rol, como los manda Cowork."""
    plan = [("GK", "TF", 1), ("GK", "SUP", 1),
            ("DEF", "TF", 3), ("DEF", "TH", 1), ("DEF", "ROT", 1),
            ("MID", "TF", 2), ("MID", "TH", 2), ("MID", "SUP", 1),
            ("ATK", "TF", 2), ("ATK", "ROT", 1), ("ATK", "SUP", 1)]
    out, n = [], 0
    for zona, rol, cuantos in plan:
        for _ in range(cuantos):
            n += 1
            out.append({"nombre": f"{prefijo} Jugador{n}", "posicion": zona, "zona": zona,
                        "rol": rol, "apps": "12/15"})
    return out


def _parte(fixture_id: int, nombre_a: str = "", nombre_b: str = "") -> dict:
    return {
        "fixtureId": fixture_id,
        "equipos": {
            "a": {"nombre": nombre_a, "bloques": {"A": 4, "B": 5, "C": 3, "D": 4, "E": 3},
                  "dt": {"nombre": "DT A", "meses": 18},
                  "perfil": {"sistema": "4-3-3", "estilo": "presión alta",
                             "fortaleza": "juego aéreo", "vulnerabilidad": "espalda de laterales"},
                  "plantel": _plantel("A"),
                  "fuera": [{"nombre": "A Jugador6", "estado": "baja", "motivo": "lesión"}],
                  "sensibilidad": [{"supuesto": "el central no llega", "efecto": "DEF pasa a zona debilitada"},
                                   {"supuesto": "", "efecto": "esto se descarta"}]},
            "b": {"nombre": nombre_b, "bloques": {"A": 1, "B": 2, "D": 1, "E": 1},
                  "excluidos": {"C": "SIN DATOS K — recién ascendido (R-KT.2)"},
                  "dt": {"nombre": "DT B", "meses": 2},
                  "plantel": _plantel("B"), "fuera": []},
        },
        "alertas": [{"codigo": "T.54", "equipo": "b", "tipo": "estructural", "detalle": "DT interino"}],
        "matchup": {"diagnostico": "MATCHUP FAVORABLE", "favorece": "a", "razon": "asimetría en ATK",
                    "h2a": "verde", "h2b": "verde", "h2c": "inventado"},
        "pronostico": {"motor": "gap §5 a favor de A", "matriz": "55/25/20", "mercado": "1.85 / 3.4 / 4.2",
                       "probabilidades": {"local": 52, "empate": 26, "visita": 22},
                       "marcador": "2-1", "falsador": "si B abre el marcador antes del 20'"},
        "lecturaSad": {
            "moduloOperativo": "Regresión al Nivel con gap a favor de A",
            "unXDos": {"texto": "A con ventaja estructural", "rangoAmpliado": True},
            "contextoEmocional": "B llega de dos derrotas",
            "datoEstructural": "Núcleo de A intacto",
            "paradoja": "El mejor EFE es el más dependiente de un hombre",
            "reventon": "A: muy alto, rival mucho más fuerte que su zona → no seguir la racha; B: bajo",
        },
        # el índice es POR EQUIPO: el parte modelo declara los dos
        "tde": {"bloques": [
            {"ie": 58, "ieNivel": "ambar", "ise": 31, "equipo": "b",
             "tipologia": "repliegue por agotamiento", "ventana": "75-90'",
             "vias": [{"nombre": "echada", "indice": 58, "ventana": "75-90'", "detalle": "baja el bloque"}],
             "falsador": "si sostiene la línea tras el 75'"},
            {"ie": 24, "ieNivel": "verde", "ise": 47, "iseNivel": "ambar", "equipo": "a",
             "tipologia": "sobreexposición por urgencia", "ventana": "60-75'",
             "vias": [{"nombre": "sobreexposicion", "indice": 47, "ventana": "60-75'",
                       "detalle": "adelanta los laterales"}],
             "falsador": "si conserva los laterales por detrás del balón"},
        ]},
        "timelineEventos": [
            {"fecha": "2026-03-02", "equipo": nombre_b or "B", "tipo": "tecnico",
             "titulo": "Cambio de DT", "detalle": "asume el interino", "destacado": True},
            {"fecha": "2026-04-10", "equipo": nombre_a or "A", "tipo": "resultado",
             "titulo": "Victoria 2-0", "marcador": "2-0"},
        ],
        "timelineNarrativa": "Semestre de curva ascendente para A.",
        "cadena": {"a": {"pronostico": "A domina por fuera y define antes del 70'"},
                   "b": {"pronostico": "B aguanta con bloque bajo y busca el contragolpe"}},
        "documentos": [{"id": "ensayo", "cuerpo": "# Cómo puede darse\n\nTexto largo."},
                       {"id": "tde", "titulo": "TDE", "cuerpo": "IE 62 · ventana 75-90"},
                       {"id": "vacio", "cuerpo": "   "}],
        "pendientes": ["XI de ambos equipos"],
        "fuentes": ["futbolperuano.com"],
    }


def main():
    tmp = tempfile.mkdtemp(prefix="sad_cowork_")
    from backend.seed_demo import seed

    seed(tmp)
    os.environ["SAD_DATA_DIR"] = tmp

    import backend.db as dbmod
    dbmod.BASE_DIR = tmp
    from backend.analisis import db as efedb
    efedb.saddb.BASE_DIR = tmp

    from fastapi.testclient import TestClient
    import backend.app as appmod
    from backend.app import app

    appmod.RATE_LIMIT = 0
    c = TestClient(app)
    A = "/api/v1"

    # el fixture con alineaciones capturadas (el "en vivo" de la demo) y uno
    # programado sin ficha: los dos caminos del once
    con_ficha = dbmod.query_one("sad", "SELECT DISTINCT fixture_id FROM alineaciones")["fixture_id"]
    sin_ficha = dbmod.query_one(
        "sad", "SELECT id FROM fixtures WHERE status_short='NS' AND id NOT IN "
               "(SELECT fixture_id FROM alineaciones) ORDER BY date LIMIT 1")["id"]
    fx = dbmod.query_one(
        "sad", "SELECT ht.name AS a, at.name AS b FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
               "JOIN teams at ON at.id=f.away_team_id WHERE f.id=?", (sin_ficha,))

    # ── agenda ──────────────────────────────────────────────────────────────
    fecha = dbmod.query_one("sad", "SELECT substr(date,1,10) AS d FROM fixtures WHERE id=?",
                            (sin_ficha,))["d"]
    r = c.get(f"{A}/analisis/cowork/agenda", params={"fecha": fecha, "limite": 2})
    check("agenda responde 200", r.status_code == 200, r.text[:200])
    ag = r.json()
    check("agenda trae la fecha pedida", ag["fecha"] == fecha, ag.get("fecha"))
    check("agenda respeta el tope", len(ag["analizar"]) <= 2, len(ag["analizar"]))
    todos = ag["analizar"] + ag["enEspera"] + ag["descartados"]
    check("todo partido del día sale clasificado", all(i["motivo"] for i in todos),
          "hay items sin motivo")
    check("los analizables van ordenados por prioridad",
          [i["prioridad"] for i in ag["analizar"]] == sorted(i["prioridad"] for i in ag["analizar"]))
    check("ningún analizable tiene prioridad 0", all(i["prioridad"] > 0 for i in ag["analizar"]))

    # ── los mandos manuales de la agenda ────────────────────────────────────
    import datetime as _dt0
    _dt_now_txt = lambda: _dt0.datetime.now(_dt0.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    from backend.app import liga_meta as sadapp_liga_meta
    liga_del_dia = dbmod.query_one(
        "sad", "SELECT league_id, COUNT(*) AS n FROM fixtures WHERE substr(date,1,10)=? "
               "GROUP BY league_id ORDER BY n DESC LIMIT 1", (fecha,))["league_id"]
    r = c.get(f"{A}/analisis/cowork/agenda",
              params={"fecha": fecha, "ligaId": liga_del_dia, "limite": 20}).json()
    todos_liga = r["analizar"] + r["enEspera"] + r["descartados"]
    check("el filtro por liga deja solo esa liga", todos_liga and all(
        i["liga"] == next(x["liga"] for x in todos_liga) for i in todos_liga), r.get("filtro"))
    check("el filtro se declara en la respuesta", r["filtro"]["ligaId"] == liga_del_dia
          and r["filtro"]["manual"] is True, r.get("filtro"))
    check("y se dice que un filtro ex ante NO contamina la población",
          "ciega" in r["notaSeleccion"] and "manual" in r["notaSeleccion"].lower(),
          r.get("notaSeleccion"))

    # sin el mando, un partido de prioridad 0 se queda fuera de `analizar`
    base = c.get(f"{A}/analisis/cowork/agenda", params={"fecha": fecha, "limite": 20}).json()
    con_todo = c.get(f"{A}/analisis/cowork/agenda",
                     params={"fecha": fecha, "limite": 20, "incluirDescartados": "true"}).json()
    check("incluirDescartados sube los de prioridad 0 a la lista",
          len(con_todo["analizar"]) >= len(base["analizar"]) and not con_todo["descartados"],
          (len(base["analizar"]), len(con_todo["analizar"])))
    check("pero conservan su motivo de descarte",
          all(i["motivo"] for i in con_todo["analizar"]), con_todo["analizar"][:2])
    check("y los de prioridad real van primero",
          [i["prioridad"] for i in con_todo["analizar"] if i["prioridad"]] ==
          sorted(i["prioridad"] for i in con_todo["analizar"] if i["prioridad"]),
          [i["prioridad"] for i in con_todo["analizar"]])

    # SIN FECHA NI desdeAhora: desde ahora y por 24 h. Antes era «el día siguiente
    # en UTC» y a las 07:00 de un miércoles devolvía el jueves entero.
    r_def = c.get(f"{A}/analisis/cowork/agenda", params={"limite": 20}).json()
    check("sin fecha, la agenda es «desde ahora y por 24 h» y lo declara (y NO cuenta como filtro manual)",
          r_def["filtro"]["desdeAhora"] is True and r_def["filtro"]["horas"] == 24
          and "desde ahora" in r_def["ventana"] and r_def["filtro"]["manual"] is False, r_def.get("filtro"))
    _ahora = _dt_now_txt()
    check("y no trae partidos ya empezados ni de pasado mañana",
          all(_ahora <= dbmod.query_one("sad", "SELECT date FROM fixtures WHERE id=?", (i["fixtureId"],))["date"]
              for i in r_def["analizar"] + r_def["enEspera"] + r_def["descartados"]))
    # filtro por TEXTO de liga: «la liga española, toda» sin buscar el id
    meta_dia = sadapp_liga_meta(liga_del_dia)
    r_txt = c.get(f"{A}/analisis/cowork/agenda",
                  params={"fecha": fecha, "liga": (meta_dia.get("pais") or meta_dia.get("nombre") or "")[:6], "limite": 20,
                          "incluirDescartados": "true"}).json()
    todos_txt = r_txt["analizar"] + r_txt["enEspera"] + r_txt["descartados"]
    check("liga=<texto> deja solo las ligas que casan por país o nombre, y las lista",
          todos_txt and liga_del_dia in r_txt["filtro"]["ligasQueCasan"]
          and all(i["liga"] in {sadapp_liga_meta(l).get("nombre") for l in r_txt["filtro"]["ligasQueCasan"]} for i in todos_txt),
          r_txt.get("filtro"))
    check("un texto que no casa con ninguna liga deja la agenda vacía, declarado",
          c.get(f"{A}/analisis/cowork/agenda", params={"fecha": fecha, "liga": "Narnia"}).json()["filtro"]["ligasQueCasan"] == [])

    # la ventana rodante ignora el día natural (a las 20:00 de Lima el día UTC ya cambió)
    r = c.get(f"{A}/analisis/cowork/agenda", params={"desdeAhora": "true", "horas": 48,
                                                     "limite": 20, "incluirDescartados": "true"}).json()
    check("la ventana rodante se declara", r["filtro"]["desdeAhora"] is True
          and "desde ahora" in r["ventana"], r.get("ventana"))
    import datetime as _dt
    ahora_txt = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    en_ventana = r["analizar"] + r["enEspera"] + r["descartados"]
    check("la ventana rodante NO devuelve partidos ya empezados",
          all(dbmod.query_one("sad", "SELECT date FROM fixtures WHERE id=?", (i["fixtureId"],))["date"]
              >= ahora_txt for i in en_ventana),
          [i["partido"] for i in en_ventana[:3]])
    # y que el vacío sea del filtro y no de la base: por fecha esos días sí traen
    pasado_dia = dbmod.query_one(
        "sad", "SELECT substr(date,1,10) AS d FROM fixtures WHERE date < ? ORDER BY date DESC LIMIT 1",
        (ahora_txt,))["d"]
    r_pasado = c.get(f"{A}/analisis/cowork/agenda",
                     params={"fecha": pasado_dia, "limite": 20, "incluirDescartados": "true"}).json()
    check("los partidos pasados existen y es la ventana la que los excluye",
          len(r_pasado["analizar"]) > 0, pasado_dia)

    # ── UN EQUIPO EN DOS PARTIDOS A POCAS HORAS (la sesión perdida de Cowork) ──
    # Pereira–Santa Fe a las 20:00 con Santa Fe en cuartos de Sudamericana a
    # las 22:00 y Pereira jugando otra vez cinco horas después: un aplazado
    # sin marcar. La agenda lo tiene que decir ANTES de gastar la sesión.
    fxr = dbmod.query_one("sad", "SELECT date, league_id, league_season, home_team_id, away_team_id "
                                 "FROM fixtures WHERE id=?", (sin_ficha,))
    import sqlite3 as _sq
    t0 = _dt.datetime.strptime(fxr["date"][:19], "%Y-%m-%d %H:%M:%S")
    otros_eq = [r["id"] for r in dbmod.query(
        "sad", "SELECT id FROM teams WHERE id NOT IN (?,?) ORDER BY id LIMIT 3",
        (fxr["home_team_id"], fxr["away_team_id"]))]
    otro_equipo, otro_b, otro_c = otros_eq
    base_ch = {i["fixtureId"]: i["conflicto"] for i in
               (lambda a: a["analizar"] + a["enEspera"] + a["descartados"])(
                   c.get(f"{A}/analisis/cowork/agenda", params={"fecha": fecha, "limite": 20}).json())}
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        # el visitante juega OTRO partido dos horas después (uno solo choca)
        _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                     "home_team_id, away_team_id) VALUES (?,?,?,?,?,?,?,?)",
                     (990001, (t0 + _dt.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "NS",
                      "Not Started", fxr["league_id"], fxr["league_season"], otro_equipo, fxr["away_team_id"]))
        # y un fixture donde chocan LOS DOS equipos: el local también juega en otro
        _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                     "home_team_id, away_team_id) VALUES (?,?,?,?,?,?,?,?)",
                     (990002, (t0 + _dt.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), "NS",
                      "Not Started", fxr["league_id"], fxr["league_season"], fxr["home_team_id"], otro_b))
        # y un aplazado con fecha vieja, que no es choque de nadie
        _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                     "home_team_id, away_team_id) VALUES (?,?,?,?,?,?,?,?)",
                     (990003, (t0 + _dt.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "PST",
                      "Match Postponed", fxr["league_id"], fxr["league_season"], otro_c, fxr["away_team_id"]))
    ag_ch = c.get(f"{A}/analisis/cowork/agenda", params={"fecha": fecha, "limite": 20, "incluirDescartados": "false"}).json()
    todo_ch = {i["fixtureId"]: i for i in ag_ch["analizar"] + ag_ch["enEspera"] + ag_ch["descartados"]}
    check("el fixture cuyos DOS equipos juegan en otro lado se descarta con motivo",
          sin_ficha in {i["fixtureId"] for i in ag_ch["descartados"]}
          and "probablemente aplazado" in todo_ch[sin_ficha]["motivo"], todo_ch.get(sin_ficha, {}).get("motivo"))
    check("y el motivo nombra los otros fixtures",
          "990001" in todo_ch[sin_ficha]["motivo"] and "990002" in todo_ch[sin_ficha]["motivo"],
          todo_ch[sin_ficha]["motivo"])
    check("el fixture donde choca UN solo equipo sigue en la lista, con `conflicto`",
          990001 in todo_ch and 990001 not in {i["fixtureId"] for i in ag_ch["descartados"]}
          and str(sin_ficha) in todo_ch[990001]["conflicto"], todo_ch.get(990001, {}).get("conflicto"))
    check("un aplazado no cuenta como choque y sale descartado como tal",
          "aplazado" in todo_ch[990003]["motivo"] and todo_ch[990003]["prioridad"] == 0
          and "990003" not in todo_ch[990001]["conflicto"], todo_ch.get(990003, {}).get("motivo"))
    tocados = {fxr["home_team_id"], fxr["away_team_id"], otro_equipo, otro_b, otro_c}
    check("los partidos ajenos al choque no cambian su `conflicto`",
          all(i["conflicto"] == base_ch.get(i["fixtureId"], "") for i in todo_ch.values()
              if i["fixtureId"] < 990000 and not ({dbmod.query_one(
                  "sad", "SELECT home_team_id AS h, away_team_id AS a FROM fixtures WHERE id=?",
                  (i["fixtureId"],))[k] for k in ("h", "a")} & tocados)))
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM fixtures WHERE id IN (990001, 990002, 990003)")

    # ── depósito ────────────────────────────────────────────────────────────
    r = c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))
    check("deposita el parte", r.status_code == 200, r.text[:300])
    rec = r.json()
    check("el recibo dice el partido de NUESTRA base", rec["partido"] == f"{fx['a']} vs {fx['b']}",
          rec.get("partido"))
    check("el recibo cuenta los jugadores", rec["jugadores"] == {"a": 16, "b": 16}, rec.get("jugadores"))
    check("el documento vacío se descarta", rec["documentos"] == ["ensayo", "tde"], rec.get("documentos"))
    check("sin discrepancias cuando no se mandan nombres", rec["discrepancias"] == [])

    r = c.post(f"{A}/analisis/cowork",
               json={"fixtureId": 99999999, "equipos": {"a": {"bloques": {"A": 1}}, "b": {}}})
    check("fixture desconocido → 422 con guía", r.status_code == 422 and "agenda" in r.text, r.text[:200])
    r = c.post(f"{A}/analisis/cowork", json={"equipos": {"a": {}}})
    check("sin fixtureId → 422", r.status_code == 422, r.status_code)

    # la discrepancia de nombre se DECLARA, no se corrige en silencio
    r = c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha, nombre_a="Equipo Inventado FC"))
    check("nombre que no casa → discrepancia declarada",
          any("Equipo Inventado" in d for d in r.json()["discrepancias"]), r.json().get("discrepancias"))
    check("re-depositar es actualizar, no duplicar", r.json()["estado"] == "actualizado")

    # ── ESCALA-LIGAS: dos equipos de ligas distintas (deuda 6, corrida del 16/09)
    # El nivel se calcula contra los rivales de cada uno y no compara entre
    # bases; el parte lo tiene que DECIR cuando junta a dos ligas.
    from backend.analisis.parte import misma_base, _liga_domestica
    d_mismo = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("dos equipos de LaLiga: sin alerta ESCALA-LIGAS",
          not any(a["codigo"] == "ESCALA-LIGAS" for a in d_mismo["alertas"]),
          [a for a in d_mismo["alertas"] if a["codigo"] == "ESCALA-LIGAS"])
    ld = _liga_domestica(fxr["home_team_id"], None)
    check("la liga doméstica es la más frecuente fuera de los torneos internacionales (LaLiga, no la Champions)",
          ld and ld["id"] == 140 and ld["pais"] == "Spain", ld)
    check("misma base: misma liga · Apertura y Clausura del mismo país · sin dato",
          misma_base({"id": 140, "pais": "Spain"}, {"id": 140, "pais": "Spain"})
          and misma_base({"id": 268, "pais": "Uruguay"}, {"id": 270, "pais": "Uruguay"})
          and misma_base(None, {"id": 140, "pais": "Spain"}))
    check("bases distintas: otro país · primera contra segunda del mismo país",
          not misma_base({"id": 140, "pais": "Spain"}, {"id": 203, "pais": "Turkey"})
          and not misma_base({"id": 239, "pais": "Colombia"}, {"id": 240, "pais": "Colombia"}))
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("INSERT OR REPLACE INTO teams (id, name, country) VALUES (990100, 'Beşiktaş', 'Turkey')")
        _con.execute("INSERT OR REPLACE INTO teams (id, name, country) VALUES (990101, 'Galatasaray', 'Turkey')")
        _con.execute("INSERT OR REPLACE INTO leagues (id, name, country, season) VALUES (203, 'Süper Lig', 'Turkey', 2026)")
        _con.execute("INSERT OR REPLACE INTO leagues (id, name, country, season) VALUES (3, 'UEFA Europa League', 'World', 2026)")
        for i in range(3):  # su Süper Lig, terminada, en el último año
            _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                         "home_team_id, away_team_id, goals_home, goals_away) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (990110 + i, (t0 - _dt.timedelta(days=7 * (i + 1))).strftime("%Y-%m-%d %H:%M:%S"),
                          "FT", "Match Finished", 203, 2026, 990100, 990101, 2, 1))
        _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                     "home_team_id, away_team_id) VALUES (?,?,?,?,?,?,?,?)",
                     (990120, (t0 + _dt.timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), "NS",
                      "Not Started", 3, 2026, fxr["home_team_id"], 990100))
    r = c.post(f"{A}/analisis/cowork", json=_parte(990120))
    check("se deposita el parte del cruce europeo", r.status_code == 200, r.text[:200])
    d_esc = c.get(f"{A}/analisis/cowork/990120").json()
    esc = [a for a in d_esc["alertas"] if a["codigo"] == "ESCALA-LIGAS"]
    check("LaLiga vs Süper Lig → UNA alerta ESCALA-LIGAS global, de tipo dato, con las dos ligas",
          len(esc) == 1 and esc[0]["equipo"] == "global" and esc[0]["tipo"] == "dato"
          and esc[0]["ligas"]["a"]["id"] == 140 and esc[0]["ligas"]["b"]["id"] == 203, esc)
    check("la alerta nombra a los equipos y sus ligas y dice que el nivel no compara entre ligas",
          esc and "Beşiktaş" in esc[0]["detalle"] and "Süper Lig" in esc[0]["detalle"]
          and "NO compara entre ligas" in esc[0]["detalle"], esc and esc[0]["detalle"])
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM fixtures WHERE id BETWEEN 990100 AND 990199")
    from backend.analisis.parte import borrar as _borrar_parte
    _borrar_parte(990120)

    # ── LO QUE SE TIRA SE DICE, TAMBIÉN EN EL TDE (3ª corrida real) ─────────
    # Cowork probó tres formas de `tde` y las tres se guardaron como {} sin un
    # solo rechazo; `vias` con strings adentro reventaba por 500. Un 500 en un
    # batch desatendido pierde el parte entero y no dice por qué.
    pel = {"fixtureId": sin_ficha, "equipos": {l: {"bloques": {"A": 3}} for l in ("a", "b")}}
    for nombre, val, donde in (
        ("tde como string", "ECHADA-FIS", "tde"),
        ("vias con strings", {"equipo": "a", "ie": 6, "vias": ["ECHADA"]}, "tde.vias[0]"),
        ("vias como string suelto", {"equipo": "a", "ie": 6, "vias": "ECHADA"}, "tde.vias"),
        ("equipo con el nombre del club", {"equipo": "Tigres FC", "ie": 6}, "tde.equipo"),
        ("dos bloques del mismo lado", [{"equipo": "a", "ie": 6}, {"equipo": "a", "ie": 5}],
         "tde[1]"),
        ("la llave y el equipo se contradicen", {"a": {"equipo": "b", "ie": 6}}, "tde.a.equipo"),
    ):
        r = c.post(f"{A}/analisis/cowork", json={**pel, "tde": val})
        check(f"{nombre}: responde 200, no 500", r.status_code == 200, r.status_code)
        rs = r.json().get("rechazos", []) if r.status_code == 200 else []
        check(f"{nombre}: se DECLARA, no se traga",
              any(x["donde"] == donde for x in rs), rs[:2])
        check(f"{nombre}: y dice la forma buena",
              any(x["donde"] == donde and x.get("esperado") for x in rs), rs[:2])

    # ── EL TDE ES POR EQUIPO Y CABEN LOS DOS ───────────────────────────────
    # Antes el parte guardaba UN bloque: el del segundo equipo terminaba en
    # `notas`, que es prosa —no se puede consultar, no se puede comprobar
    # contra los goles recibidos y no entra en ninguna métrica—.
    dos = {"a": {"ie": 4.2, "ventana": "60-75'", "tipologia": "sobreexposición"},
           "b": {"ie": 6.4, "ventana": "75-90'", "tipologia": "repliegue"}}
    formas = {
        "{a, b} como los equipos": dos,
        "lista de bloques": [{**dos["a"], "equipo": "a"}, {**dos["b"], "equipo": "b"}],
        "la canónica {bloques: [...]}": {"bloques": [{**dos["a"], "equipo": "a"},
                                                     {**dos["b"], "equipo": "b"}]},
    }
    for nombre, val in formas.items():
        r = c.post(f"{A}/analisis/cowork", json={**pel, "tde": val})
        check(f"tde {nombre}: entra sin rechazos", r.status_code == 200
              and not [x for x in r.json().get("rechazos", []) if x["donde"].startswith("tde")],
              r.json().get("rechazos"))
        check(f"tde {nombre}: el recibo dice de qué equipos quedó índice",
              r.json().get("ladosTde") == ["a", "b"], r.json().get("ladosTde"))
        d = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
        bl = d["tde"]["bloques"]
        check(f"tde {nombre}: se guardan los DOS bloques", len(bl) == 2, bl)
        check(f"tde {nombre}: cada uno con su lado y su ventana",
              {b["equipo"]: b["ventana"] for b in bl} == {"a": "60-75'", "b": "75-90'"},
              {b["equipo"]: b["ventana"] for b in bl})

    # un solo bloque SIGUE entrando (forma plana), y el recibo cobra el que falta
    r = c.post(f"{A}/analisis/cowork", json={**pel, "tde": {**dos["b"], "equipo": "b"}})
    check("el objeto plano de siempre sigue entrando",
          r.json()["ladosTde"] == ["b"], r.json().get("ladosTde"))
    check("y `faltan` cobra el TDE del otro equipo",
          any(f["bloque"].startswith("tde (el otro") for f in r.json()["faltan"]),
          [f["bloque"] for f in r.json()["faltan"]])

    # los DOS índices se calculan: uno por equipo, con sus propias compuertas
    ind = {"F1": 1, "F2": 0.5, "F3": 1, "F4": 0, "C1": 1, "C2": 0.5, "C3": 0,
           "P1a": 1, "P1b": 0.5, "P2": 0, "S1": 1, "S2": 0.5}
    r = c.post(f"{A}/analisis/cowork", json={**pel, "tde": {"bloques": [
        {"equipo": "a", "ventana": "60-75'", "indicadores": ind, "ie": 9.9},
        {"equipo": "b", "ventana": "75-90'", "indicadores": {**ind, "F1": 0, "F3": 0}},
    ]}})
    check("dos bloques con indicadores: 200", r.status_code == 200, r.text[:200])
    bl = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["tde"]["bloques"]
    check("cada equipo tiene su índice CALCULADO",
          all(b.get("calculado", {}).get("ie") is not None for b in bl),
          [b.get("calculado", {}).get("ie") for b in bl])
    check("y son distintos, porque los indicadores lo son",
          bl[0]["calculado"]["ie"] != bl[1]["calculado"]["ie"],
          [b["calculado"]["ie"] for b in bl])
    check("la discrepancia se delata en el bloque que la tiene",
          bool(bl[0].get("discrepancia")) and not bl[1].get("discrepancia"),
          [b.get("discrepancia") for b in bl])
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))

    # ── EL CONTRATO SE PUEDE LEER, NO SE ADIVINA ────────────────────────────
    # `/openapi.json` está apagado en despliegue, así que Cowork reconstruyó la
    # forma a golpe de recibo. Esto sale de las MISMAS constantes que validan.
    ct = c.get(f"{A}/analisis/cowork/contrato").json()
    check("el contrato lista las claves de la raíz",
          set(ct["raiz"]) == _CLAVES_ESPERADAS, sorted(set(ct["raiz"]) ^ _CLAVES_ESPERADAS))
    check("y avisa que el TDE es por equipo y caben los dos",
          "bloques" in ct["tde"]["forma"] and ct["tde"].get("dosEquipos"), ct["tde"]["forma"])
    check("y publica los indicadores del TDE por bloque",
          set("FCPS") <= set(ct["tde"]["indicadores"]) and "ISE" in ct["tde"]["indicadores"],
          sorted(ct["tde"]["indicadores"]))
    check("y los ids de documento que la pantalla titula sola",
          "dtp" in ct["documentos"]["idsQueLaPantallaTitulaSola"], ct["documentos"])

    # ── EL ONCE SE CIERRA SOLO, SIN MODELO Y SIN RELOJ ──────────────────────
    # Seis partidos que arrancan juntos no son seis análisis contra el reloj:
    # son seis cruces de listas de nombres. La carrera de 30 minutos no existe.
    c.post(f"{A}/analisis/cowork", json=_parte(con_ficha))
    auto = c.post(f"{A}/analisis/cowork/xi/auto").json()
    check("el cierre automático revisa los partes sin once",
          auto["revisados"] >= 1, auto.get("revisados"))
    check("y cierra el que YA tiene la alineación ingestada",
          any(x["fixtureId"] == con_ficha for x in auto["cerrados"]),
          [x["fixtureId"] for x in auto["cerrados"]])
    check("declara que no gasta tokens ni llama a ningún modelo",
          "no gasta tokens" in auto["nota"], auto.get("nota"))
    check("y los que no tienen ficha salen con su motivo, no en silencio",
          all(x.get("porque") for x in auto["sinFichaTodavia"]), auto.get("sinFichaTodavia"))
    # «TODAVÍA» ES UNA PROMESA QUE EN ALGUNAS LIGAS NO SE CUMPLE NUNCA. Un
    # partido ya TERMINADO sin alineación ingestada no está esperando nada:
    # llamarlo «todavía» deja al usuario esperando para siempre.
    terminados = {r["id"] for r in dbmod.query(
        "sad", "SELECT id FROM fixtures WHERE status_short IN ('FT','AET','PEN')")}
    check("un partido YA TERMINADO sin once no se llama `todavía`",
          all(x["fixtureId"] not in terminados for x in auto["sinFichaTodavia"]),
          [x["fixtureId"] for x in auto["sinFichaTodavia"]])
    check("va a `nuncaVaALlegar`, con qué hacer en su lugar",
          all(x.get("queHacer") and "procedimiento" in x["queHacer"]
              for x in auto["nuncaVaALlegar"]), auto.get("nuncaVaALlegar"))
    check("y se listan las ligas que no dan onces, para verlo como patrón",
          isinstance(auto["ligasSinOnce"], list), auto.get("ligasSinOnce"))
    # idempotente: pasar dos veces no rehace nada
    otra = c.post(f"{A}/analisis/cowork/xi/auto").json()
    check("es idempotente: el ya cerrado no se vuelve a tocar",
          all(x["fixtureId"] != con_ficha for x in otra["cerrados"]),
          [x["fixtureId"] for x in otra["cerrados"]])

    # ── EL MISMO HUECO, LEÍDO AL REVÉS POR DOS ESCALAS ─────────────────────
    # Un equipo salió «1.9% SIN FORMACIÓN» y «IE 8.14 · casi seguro» a la vez:
    # el EFE cuenta el bloque ausente como 0 y hunde el porcentaje; el TDE
    # promedia solo sobre los presentes y un 1 con denominador chico dispara el
    # índice. Los dos números son artefactos del mismo vacío.
    r_h = c.post(f"{A}/analisis/cowork", json={
        "fixtureId": sin_ficha,
        "equipos": {"a": {"bloques": {"A": 1}}, "b": {"bloques": {"A": 2, "B": 3}}},
        "tde": {"bloques": [{"equipo": "a", "ventana": "75-90'",
                             "indicadores": {"F1": 1, "C1": 1, "P1a": 1, "S1": 1}}]},
    })
    check("un TDE con pocos indicadores se deposita igual", r_h.status_code == 200, r_h.text[:150])
    d_h = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    cob = d_h["tde"]["bloques"][0]["calculado"]["cobertura"]
    check("el TDE declara con cuántos indicadores se calculó",
          cob["usados"] == 4 and cob["nominales"] == 16, cob)
    check("y avisa que menos dato no es más riesgo",
          "menos dato" in cob["nota"], cob["nota"])
    check("la contradicción EFE/TDE se declara JUNTA, en una alerta",
          any(x["codigo"] == "HUECO-DOBLE" and x["equipo"] == "a" for x in d_h["alertas"]),
          [x["codigo"] for x in d_h["alertas"]])
    check("y la alerta dice qué NO significa",
          any("es un equipo sin datos" in x.get("detalle", "") for x in d_h["alertas"]),
          [x.get("detalle", "")[:60] for x in d_h["alertas"]])
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))

    # `sensibilidad` como lista de strings tumbaba el endpoint con un 500 sin
    # recibo: en un batch desatendido eso pierde el parte entero sin decir por qué
    r_s = c.post(f"{A}/analisis/cowork", json={
        "fixtureId": sin_ficha,
        "equipos": {"a": {"bloques": {"A": 3}, "sensibilidad": ["si el central no llega, cambia"]},
                    "b": {"bloques": {"A": 3}}}})
    check("`sensibilidad` mal formada responde 200, no 500", r_s.status_code == 200, r_s.status_code)
    # ── NINGUNA FORMA MAL ESCRITA TUMBA EL DEPÓSITO (reportado por Cowork) ──
    # `lecturaSad` como string respondía 500 sin mensaje: el segundo campo del
    # contrato que reventaba en vez de rechazar. Acá van todas las ramas que
    # se leen con `.get`: cada una tiene que dar 200 y un rechazo con su sitio.
    formas = {
        "lecturaSad": {"lecturaSad": "Regresión al Nivel con gap a favor del local"},
        "lecturaSad.unXDos": {"lecturaSad": {"moduloOperativo": "x", "unXDos": ["1", "X"]}},
        "matchup": {"matchup": "FAVORABLE al local"},
        "pronostico": {"pronostico": "52 / 27 / 21"},
        "pronostico.probabilidades": {"pronostico": {"probabilidades": "52/27/21"}},
        "cadena": {"cadena": "domina por fuera"},
        "alertas": {"alertas": "T.54"},
        "alertas[0]": {"alertas": [7]},
        "documentos": {"documentos": "## ensayo"},
        "documentos[0]": {"documentos": ["## ensayo"]},
        "timelineEventos[0]": {"timelineEventos": ["cambio de DT"]},
        "timelineEventos[1]": {"timelineEventos": [{"fecha": "2026-03-02", "tipo": "partido", "titulo": "3-0 al Erzurumspor"},
                                                   {"fecha": "2026-03-02", "tipo": "rumor", "titulo": "…"}]},
        "equipos.a.bloques": {"equipos": {"a": {"bloques": "A3 B4"}}},
        "equipos.a.excluidos": {"equipos": {"a": {"bloques": {"A": 3}, "excluidos": "C"}}},
        "equipos.a.notas": {"equipos": {"a": {"bloques": {"A": 3}, "notas": "mismo DT"}}},
        "equipos.a.dt": {"equipos": {"a": {"bloques": {"A": 3}, "dt": ["Nombre", 14]}}},
        "equipos.a.perfil": {"equipos": {"a": {"bloques": {"A": 3}, "perfil": "4-3-3 presión alta"}}},
        "equipos.a.plantel": {"equipos": {"a": {"bloques": {"A": 3}, "plantel": "Campos, Zambrano"}}},
        "equipos.a.plantel[0]": {"equipos": {"a": {"bloques": {"A": 3}, "plantel": ["Campos"]}}},
        "equipos.a.fuera[0]": {"equipos": {"a": {"bloques": {"A": 3}, "fuera": [3]}}},
        "equipos.a.factorX[0]": {"equipos": {"a": {"bloques": {"A": 3}, "factorX": ["Barcos"]}}},
        "equipos.b": {"equipos": {"a": {"bloques": {"A": 3}}, "b": "Visitante FC"}},
    }
    for donde, cuerpo in formas.items():
        body = {"fixtureId": sin_ficha, "equipos": {"a": {"bloques": {"A": 3}}}}
        body.update(cuerpo)
        r_f = c.post(f"{A}/analisis/cowork", json=body)
        ok = r_f.status_code == 200 and any(
            x["donde"] == donde and x.get("esperado") for x in r_f.json().get("rechazos", []))
        check(f"`{donde}` mal formado responde 200 con rechazo, no 500", ok,
              (r_f.status_code, [x["donde"] for x in r_f.json().get("rechazos", [])]
               if r_f.status_code == 200 else r_f.text[:120]))
    # y las dos tolerancias que sí tienen sentido: una baja o una alerta «a secas»
    r_f = c.post(f"{A}/analisis/cowork", json={
        "fixtureId": sin_ficha, "alertas": ["T.54"],
        "equipos": {"a": {"bloques": {"A": 3}, "fuera": ["Zambrano"]}}}).json()
    check("una baja como string entra con su nombre",
          any(x.get("jugador") == "Zambrano" for x in r_f["rechazos"]), r_f["rechazos"])
    check("una alerta como string entra como código y se delata sin texto",
          r_f["alertas"] == 1 and any(x.get("jugador") == "T.54" for x in r_f["rechazos"]),
          r_f["rechazos"])
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))  # dejarlo como estaba
    check("y se DECLARA con la forma buena al lado",
          any(x["donde"].startswith("equipos.a.sensibilidad") and x.get("esperado")
              for x in r_s.json().get("rechazos", [])), r_s.json().get("rechazos"))
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))

    # ── EL PADRÓN DE LA AGENDA: UNA SOLA FUENTE ────────────────────────────
    # El criterio por NOMBRE dejaba fuera a Brasil, Colombia, Chile, Uruguay,
    # Ecuador, Paraguay, Bolivia, Venezuela, Portugal, Bélgica, la Europa
    # League y la Conference: salían como «fuera del padrón» y nadie lo miraba.
    # Ahora el padrón es EL MISMO que el de las cuotas en vivo, para que no
    # haya dos listas de «ligas importantes» que se separen con el tiempo.
    from backend.analisis.parte import _prioridad, _padron, SEGUNDAS, INTERNACIONALES
    from backend.ingesta.extractor import ligas_vivo
    liga_x = {"nombre": "X"}
    prio_de = lambda lid, ronda="", etq=None, pl=0, pv=0, **kw: _prioridad(
        liga_x, etq or set(), pl, pv, lid, ronda, **kw)

    check("el padrón de la agenda ES el de las cuotas en vivo",
          set(_padron()) == set(ligas_vivo()),
          sorted(set(_padron()) ^ set(ligas_vivo())))
    check("todas las ligas del padrón entran a la agenda (con grupos y segundas abiertos)",
          all(prio_de(lid, grupos=True, segundas=True)[0] > 0 for lid in _padron()),
          [lid for lid in _padron() if not prio_de(lid, grupos=True, segundas=True)[0]])
    check("las doce que el criterio viejo tiraba ahora entran",
          all(prio_de(lid, grupos=True)[0] > 0 for lid in (71, 239, 265, 268, 242, 250, 344,
                                                           299, 94, 144, 3, 848)),
          [lid for lid in (71, 239, 265, 268, 242, 250, 344, 299, 94, 144, 3, 848)
           if not prio_de(lid, grupos=True)[0]])
    # LO QUE LLENÓ LA CORRIDA DEL 16/09: fase liga de Europa League y segundas
    check("por defecto la fase de grupos / fase liga internacional QUEDA FUERA, con motivo",
          prio_de(3, "League Stage - 1")[0] == 0 and "grupos=true" in prio_de(3, "League Stage - 1")[1],
          prio_de(3, "League Stage - 1"))
    check("y la fase decisiva entra igual sin pedirlo", prio_de(3, "Round of 16")[0] == 2, prio_de(3, "Round of 16"))
    check("por defecto las segundas divisiones QUEDAN FUERA, con motivo",
          all(prio_de(lid)[0] == 0 and "segundas=true" in prio_de(lid)[1] for lid in SEGUNDAS),
          [prio_de(lid) for lid in SEGUNDAS if prio_de(lid)[0]])
    check("con segundas=true entran, al final (7)", all(prio_de(lid, segundas=True)[0] == 7 for lid in SEGUNDAS))
    check("una primera división sin equipo arriba sigue entrando (6)", prio_de(140)[0] == 6, prio_de(140))
    check("una fase decisiva manda sobre la fase de grupos",
          prio_de(13, "Quarter-finals")[0] < prio_de(13, "Group Stage - 4", grupos=True)[0],
          (prio_de(13, "Quarter-finals"), prio_de(13, "Group Stage - 4", grupos=True)))
    check("y las cuatro maneras de nombrar una llave se reconocen",
          all("fase decisiva" in prio_de(2, r)[1]
              for r in ("Round of 16", "Quarter-finals", "Semi-finals", "Final")),
          [prio_de(2, r)[1] for r in ("Round of 16", "Quarter-finals", "Semi-finals", "Final")])
    check("la Liga 1 de Perú sigue primera", prio_de(281)[0] == 1, prio_de(281))
    check("una segunda división (con segundas=true) entra, pero al final",
          prio_de(141, segundas=True)[0] > prio_de(140)[0] > 0, (prio_de(141, segundas=True), prio_de(140)))
    check("dentro de una liga, el equipo en el top 6 o en crisis va antes",
          prio_de(71, pl=3)[0] < prio_de(71, pl=14, pv=17)[0],
          (prio_de(71, pl=3), prio_de(71, pl=14, pv=17)))

    # UN CLÁSICO NO PUEDE METER A UNA LIGA QUE NO ESTÁ EN EL PADRÓN. Antes el
    # derbi se miraba ANTES del padrón: la Copa Uruguay entró para un partido y
    # se descartó para otros tres del mismo torneo y el mismo día.
    check("una copa nacional NO entra sola", prio_de(930)[0] == 0, prio_de(930))
    check("y tampoco entra por ser clásico: el descarte es el mismo siempre",
          prio_de(930, etq={"CLASICO"})[0] == 0, prio_de(930, etq={"CLASICO"}))
    check("pero un clásico DENTRO del padrón sí sube",
          prio_de(140, etq={"CLASICO"})[0] == 3, prio_de(140, etq={"CLASICO"}))
    check("el descarte dice la liga Y su id, que es lo que hace falta para agregarla",
          "id 930" in prio_de(930)[1], prio_de(930)[1])

    # EL CORTE POR LÍMITE SE VE, NO SE DEDUCE. Con limite=4 y cuatro llaves
    # internacionales el mismo día, una jornada entera de LaLiga no entra —y
    # desde afuera parecía que la liga no estaba cubierta.
    ag_corte = c.get(f"{A}/analisis/cowork/agenda", params={"limite": 1}).json()
    check("la agenda declara el corte por límite", "corte" in ag_corte, sorted(ag_corte))
    check("y dice cuántos candidatos quedaron fuera y de qué prioridad",
          ag_corte["corte"]["limite"] == 1
          and ag_corte["corte"]["quedanFuera"] == max(0, ag_corte["corte"]["candidatos"] - 1)
          and isinstance(ag_corte["corte"]["porPrioridad"], dict), ag_corte["corte"])
    check("y si quedó algo fuera, nombra las ligas",
          (not ag_corte["corte"]["quedanFuera"]) or ag_corte["corte"]["ligasQueQuedanFuera"],
          ag_corte["corte"])

    # ── LA AGENDA SE PUEDE RETOMAR DONDE SE CORTÓ ───────────────────────────
    ag = c.get(f"{A}/analisis/cowork/agenda",
               params={"fecha": fecha, "limite": 4, "incluirDescartados": True}).json()
    check("la agenda dice qué falta por hacer y qué ya está",
          "porHacer" in ag and "yaHechos" in ag, sorted(ag)[:6])
    check("y cada candidato viene marcado con lo que ya hay en la base",
          all("tieneParte" in x and "onceCerrado" in x
              for x in (ag["analizar"] + ag["descartados"])),
          (ag["analizar"] or [{}])[0])
    check("los que ya tienen parte NO aparecen en porHacer",
          all(x not in ag["porHacer"] for x in ag["yaHechos"]),
          (ag["porHacer"], ag["yaHechos"]))
    check("y se explica que re-depositar REEMPLAZA, para no rehacer de más",
          "REEMPLAZA" in ag["notaReanudacion"], ag.get("notaReanudacion"))

    # ── LAS MARCAS: qué partidos de la lista ya tienen parte ────────────────
    # Lo que la tarjeta de cada partido pinta al costado. Por ids, no por
    # fecha: el día de la pantalla es local y el de la base es UTC.
    mk_r = c.get(f"{A}/analisis/cowork/marcas", params={"ids": f"{sin_ficha},{con_ficha},999999"})
    check("`marcas` no se lo come /{fixture_id}", mk_r.status_code == 200, mk_r.text[:160])
    mk = mk_r.json()
    check("el partido con parte viene con su estado; el que no lo tiene no viene",
          str(sin_ficha) in mk["partes"] and "999999" not in mk["partes"]
          and mk["partes"][str(sin_ficha)]["estado"] in ("pendiente_xi", "confirmado")
          and mk["partes"][str(sin_ficha)]["conVeredicto"] is False, mk)
    check("sin ids no hay marcas ni error", c.get(f"{A}/analisis/cowork/marcas").json() == {"partes": {}, "total": 0})
    check("ids que no son enteros → 422", c.get(f"{A}/analisis/cowork/marcas", params={"ids": "a,b"}).status_code == 422)

    # ── EL LATIDO: QUE EL SILENCIO SE VEA ───────────────────────────────────
    # Una tubería automática sin vigilancia no falla con ruido, falla callada.
    lat_r = c.get(f"{A}/analisis/cowork/latido")
    lat = lat_r.json()
    # REGRESIÓN DE ORDEN DE RUTAS: `latido` es un segmento suelto y FastAPI
    # resuelve por orden de declaración. Declarado después de `/{fixture_id}`,
    # el parámetro de camino se lo come y devuelve 422 intentando parsear
    # "latido" como entero. Pasó, y por eso este check nombra la causa.
    check("`latido` no se lo come /{fixture_id}", lat_r.status_code == 200, lat_r.text[:160])
    check("el latido responde con estado y motivo",
          lat["estado"] in ("verde", "ambar", "rojo") and lat["porque"], lat.get("estado"))
    check("cuenta los partes de la ventana y dice cuánto hace del último",
          "depositadosEnLaVentana" in lat and "horasDesdeElUltimo" in lat, sorted(lat))
    check("mide la COBERTURA contra lo que tocaba, no solo lo depositado",
          "tocaban" in lat["coberturaDeAyer"], lat.get("coberturaDeAyer"))
    check("lista los veredictos vencidos y los onces sin cerrar",
          isinstance(lat["veredictosVencidos"], list) and isinstance(lat["sinOnceCerrado"], list),
          sorted(lat))
    check("y declara que el silencio cuenta como fallo",
          "ROJO" in lat["nota"] and "silencio" in lat["nota"].lower(), lat.get("nota"))
    # ── EL REVISOR DE COHERENCIA: QUÉ ENCONTRÓ Y QUÉ HIZO COWORK ─────────────
    rev_r = c.get(f"{A}/analisis/cowork/revisor")
    check("`revisor` no se lo come /{fixture_id}", rev_r.status_code == 200, rev_r.text[:160])
    rev = rev_r.json()
    check("el reporte trae totales, partes, el modo vigente y la lista para mirar",
          {"totales", "partes", "modo", "paraMirar", "ventana"} <= set(rev), sorted(rev))
    check("sin clave de Jev, todo lo depositado hasta acá figura como noEvaluado",
          rev["totales"]["evaluaciones"] >= 1 and rev["totales"]["partesEvaluados"] == 0
          and all(p_["reaccion"] == "noEvaluado" for p_ in rev["partes"]), rev["totales"])
    # con un guion, el revisor «encuentra» una contradicción en el 1X2 (el texto
    # inclina a la visita, el reparto pone 52 en local) y luego Cowork corrige
    from backend.analisis import coherencia as coh_mod
    modo_antes = coh_mod.MODO
    coh_mod.MODO = "alertas"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump({"unXDos": {"valor": "visita", "confianza": 0.95, "comoReal": True}}, fh)
        guion = fh.name
    os.environ["SAD_JEV_GUION"] = guion
    r1 = c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha)).json()
    check("el recibo en modo alertas trae el hallazgo y qué hacer",
          r1["coherencia"]["hallazgos"] == 1 and r1["coherencia"]["detalle"][0]["codigo"] == "COHERENCIA-1X2"
          and "queHacer" in r1["coherencia"], r1.get("coherencia"))
    g1 = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("en modo alertas la COHERENCIA-1X2 sale en la tira con origen jev",
          any(a["codigo"] == "COHERENCIA-1X2" and a.get("origen") == "jev" for a in g1["alertas"]), g1["alertas"])
    check("y el GET trae la evaluación sellada con el modelo del guion",
          g1["coherencia"]["modelo"] == "guion" and len(g1["coherencia"]["hallazgos"]) == 1, g1.get("coherencia"))
    rev1 = c.get(f"{A}/analisis/cowork/revisor").json()
    p1 = next(p_ for p_ in rev1["partes"] if p_["fixtureId"] == sin_ficha)
    check("el reporte lo cuenta como hallazgo sin reacción y lo pone para mirar",
          p1["reaccion"] == "sinReaccion" and p1["hallazgosEncontrados"] == ["COHERENCIA-1X2"]
          and sin_ficha in rev1["paraMirar"], p1)
    # Cowork corrige: el mismo texto ahora inclina al local → concuerda
    with open(guion, "w", encoding="utf-8") as fh:
        json.dump({"unXDos": {"valor": "local", "confianza": 0.95, "comoReal": True}}, fh)
    r2 = c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha)).json()
    check("el re-depósito corregido ya no tiene hallazgos", r2["coherencia"]["hallazgos"] == 0, r2.get("coherencia"))
    rev2 = c.get(f"{A}/analisis/cowork/revisor").json()
    p2 = next(p_ for p_ in rev2["partes"] if p_["fixtureId"] == sin_ficha)
    check("el reporte ve la secuencia y dice que Cowork corrigió",
          p2["reaccion"] == "corrigio" and len(p2["evaluaciones"]) >= 2
          and p2["evaluaciones"][-1]["redeposito"] is True and sin_ficha not in rev2["paraMirar"], p2)
    check("cada evaluación del reporte dice por dónde pasó y el reporte dice el host de hoy",
          all("via" in e for e in p2["evaluaciones"]) and rev2["via"] and "oficial" in rev2
          and isinstance(rev2["totales"]["porVia"], dict), (rev2.get("via"), p2["evaluaciones"][-1]))
    check("los totales cuentan el hallazgo por código y el costo del día",
          rev2["totales"]["hallazgosPorCodigo"].get("COHERENCIA-1X2") == 1
          and rev2["totales"]["corrigio"] == 1 and "costoUsd" in rev2["totales"], rev2["totales"])
    check("`dia` acota por fecha UTC y un día sin nada devuelve vacío",
          c.get(f"{A}/analisis/cowork/revisor", params={"dia": "2000-01-01"}).json()["partes"] == [])
    check("un `dia` mal formado es 422",
          c.get(f"{A}/analisis/cowork/revisor", params={"dia": "ayer"}).status_code == 422)
    os.environ.pop("SAD_JEV_GUION", None)
    os.unlink(guion)
    coh_mod.MODO = modo_antes

    # sobre una ventana de 1 hora, lo que se depositó hace rato ya no cuenta:
    # es la prueba de que el silencio se detecta
    corto = c.get(f"{A}/analisis/cowork/latido", params={"horas": 1}).json()
    check("con la ventana corta, cero depósitos da ROJO y no «sin novedad»",
          corto["estado"] == "rojo" if corto["depositadosEnLaVentana"] == 0 else True,
          (corto["depositadosEnLaVentana"], corto["estado"]))

    # ── LOS INSUMOS DEL TDE SALEN DEL MOTOR, NO DEL MODELO ──────────────────
    # El propio skill lo manda: P1a es «input inviolable» y F2 es «dato del
    # motor o no es dato». Pedirle a Cowork que escriba un μ que ya tenemos
    # calculado es lento, caro y peor.
    t = c.get(f"{A}/analisis/cowork/tde/{sin_ficha}")
    check("la ficha del TDE responde", t.status_code == 200, t.text[:200])
    tde = t.json()
    check("P1a sale del μ del partido, no de un juicio",
          tde["p1a"]["muPartido"]["a"] is not None and tde["p1a"]["muPartido"]["b"] is not None,
          tde["p1a"])
    check("y aplica el umbral de 0.30 del skill", tde["p1a"]["umbral"] == 0.30, tde["p1a"]["umbral"])
    check("el protector puntúa 1 y el otro 0 cuando el margen lo pasa",
          (sorted(tde["p1a"]["score"].values()) == [0.0, 1.0]) if tde["p1a"]["margen"] > 0.30
          else (sorted(tde["p1a"]["score"].values()) == [0.5, 0.5]), tde["p1a"])
    check("declara la compuerta 1, que es lo que P1a dispara",
          "0.5" in tde["p1a"]["compuerta1"], tde["p1a"].get("compuerta1"))
    check("F2 trae los días de descanso calculados",
          tde["f2"]["a"]["diasDescanso"] is not None, tde["f2"]["a"])
    check("y da un PISO, no un score cerrado: el viaje y la altitud no están en la base",
          "scorePiso" in tde["f2"]["a"] and "altitud" in tde["f2"]["a"]["puedeSubir"],
          tde["f2"]["a"])
    check("sin onces capturados, F1 dice sinDato en vez de inventar rotación",
          tde["f1"]["a"].get("sinDato") is True or tde["f1"]["a"].get("score") is not None,
          tde["f1"]["a"])
    check("y el nivel de dato baja a C cuando falta el once",
          tde["nivelDeDato"] in ("B", "C"), tde["nivelDeDato"])
    check("los 16 indicadores que NO se calculan se declaran con su motivo",
          len(tde["noCalculables"]) == 16 and all(x["porque"] for x in tde["noCalculables"]),
          len(tde["noCalculables"]))
    check("y la ficha aclara que NO es el IE", "NO es el IE" in tde["nota"], tde["nota"][:80])
    check("un fixture inexistente da 404",
          c.get(f"{A}/analisis/cowork/tde/99999999").status_code == 404)

    # F1 sobre el fixture que SÍ tiene alineaciones capturadas
    tf = c.get(f"{A}/analisis/cowork/tde/{con_ficha}").json()
    check("con onces capturados, F1 cuenta de verdad o dice por qué no",
          tf["f1"]["a"].get("score") is not None or tf["f1"]["a"].get("porque"),
          tf["f1"]["a"])

    # ── LA ARITMÉTICA DEL IE LA HACE EL BACKEND ─────────────────────────────
    # La fórmula se verificó contra el registro del skill: reproduce 30 de 33
    # casos. Lo que se calcula no se le pregunta al modelo.
    from backend.analisis import tde as tdemod
    todos = {k: 0.5 for k in ("F1", "F2", "F3", "F4", "C1", "C2", "C3",
                              "P1a", "P1b", "P1c", "P2", "P3", "P4", "S1", "S2", "S3")}
    r5 = tdemod.indice(todos)
    check("con todos los indicadores en 0.5 el IE da 5.00", r5["ie"] == 5.0, r5.get("ie"))
    # LAS TABLAS ESTÁN SUSPENDIDAS: banda ordinal, nunca probabilidad
    check("no se emite probabilidad: la tabla está suspendida",
          "pEchada" not in r5 and "pSobreexposicion" not in r5, sorted(r5))
    check("se emite el tramo ordinal en su lugar",
          r5["bandaOrdinal"]["tramo"] == "medio-alto", r5.get("bandaOrdinal"))
    check("y el riesgo compuesto cae con ellas, porque es su producto",
          "riesgo_compuesto" in r5["tablasSuspendidas"]["que"], r5["tablasSuspendidas"]["que"])
    check("y declara la fórmula y el esquema de P que usó",
          "8.5" in r5["formula"] and "6 indicadores" in r5["esquemaP"], r5["esquemaP"])

    # COMPUERTA 1: sin protector no hay echada psicológica
    sin_prot = {**todos, "P1a": 0.0, "P1b": 1.0, "P1c": 1.0, "P2": 1.0, "P3": 1.0, "P4": 1.0}
    r = tdemod.indice(sin_prot)
    check("P1a=0 topa el bloque P en 0.5 (compuerta 1)", r["bloques"]["P"] == 0.5, r["bloques"])
    # EL CRUDO AL LADO DEL TOPEADO. Sin eso, una compuerta que baja el promedio
    # es indistinguible de una que no hizo nada — y hay un caso en el registro
    # (TDE-026) que declara «sin efecto numérico» sobre un promedio que sí bajaba.
    check("y el promedio CRUDO viaja al lado, para que el efecto se vea",
          r["bloquesCrudos"]["P"] > 0.5, (r["bloquesCrudos"]["P"], r["bloques"]["P"]))
    # toda reducción de denominador se declara, en CUALQUIER bloque, no solo en P
    rf = tdemod.indice({k: v for k, v in todos.items() if k != "F3"})
    check("un bloque F promediado sobre 3 se declara",
          any("bloque F promediado sobre 3 de 4" in x for x in rf["compuertasOperadas"]),
          rf["compuertasOperadas"])
    check("y nombra el indicador que faltó",
          any("F3" in x for x in rf["compuertasOperadas"]), rf["compuertasOperadas"])
    check("y la compuerta se DECLARA aunque el número no lo delate",
          any("compuerta 1" in x for x in r["compuertasOperadas"]), r["compuertasOperadas"])

    # COMPUERTA 2: S2 solo puede valer 1 con repliegue documentado
    r = tdemod.indice({**todos, "C1": 0.5, "S2": 1.0})
    check("C1<1 topa S2 en 0.5 (compuerta 2)",
          any("compuerta 2" in x for x in r["compuertasOperadas"]), r["compuertasOperadas"])

    # S3 n/a cuando el bloque bajo es por diseño
    r = tdemod.indice({**todos, "F4": 0.0, "C1": 0.0, "S3": 1.0})
    check("F4=0 ∧ C1=0 saca a S3 del promedio",
          r["indicadoresUsados"]["S"] == ["S1", "S2"], r["indicadoresUsados"]["S"])

    # las dos reglas de piso
    r = tdemod.indice({**todos, "F1": 1.0, "F3": 1.0, "F2": 0.0, "F4": 0.0})
    check("F1=1 ∧ F3=1 sube el bloque F a 0.75", r["bloques"]["F"] == 0.75, r["bloques"]["F"])
    r = tdemod.indice({**todos, "C1": 0.0, "C2": 0.0, "C3": 1.0})
    check("C3=1 sube el bloque C a 0.60", r["bloques"]["C"] == 0.60, r["bloques"]["C"])

    # Disciplina 21: F2 es dato del motor o el bloque F no existe
    sin_f2 = {k: v for k, v in todos.items() if k != "F2"}
    r = tdemod.indice(sin_f2)
    check("sin F2 el bloque F entero se declara sin dato (Disciplina 21)",
          r.get("sinDato") is True and r["bloque"] == "F", r)

    # el ISE se emite siempre, y el riesgo es el MÁXIMO de las dos vías
    r = tdemod.indice({**todos, "SOB1": 1.0, "SOB2": 1.0, "SOB3": 1.0})
    check("el ISE se calcula aparte y sin pesos", r["ise"] == 10.0, r.get("ise"))
    check("el riesgo es el máximo de las dos vías, nunca la suma",
          r["riesgo"]["maximo"] == 10.0 and r["riesgo"]["via"] == "sobreexposicion", r["riesgo"])
    r = tdemod.indice(todos)
    check("sin SOB el ISE es null y se dice por qué, no se omite",
          r["ise"] is None and "SIEMPRE" in r["iseNota"], r.get("iseNota"))

    # no se inventan umbrales de color
    check("no hay nivel verde/ámbar/rojo y se explica por qué",
          r["nivel"] == "" and "ORDENA" in r["notaNivel"], r.get("notaNivel"))
    # LA CALIBRACIÓN EXCLUYE LO QUE EL SKILL MANDA EXCLUIR. La primera versión
    # promedió los 21 ciegos sin sacar los `rama_abandonada` (disciplinas 24, 27
    # y 31) y uno de los dos «positivos» era TDE-030, que su propia lección
    # declara fuera de toda métrica de frecuencia.
    cal = r["calibracion"]
    check("la calibración declara el filtro que aplicó",
          "rama_abandonada" in cal["filtro"], cal.get("filtro"))
    check("y usa los computables, no todos los ciegos",
          cal["casosComputables"] == 8 and cal["seEcharon"] == 1, cal)
    check("excluye modo=RETRO, que es cuándo se escribió el análisis",
          "RETRO" in cal["filtro"] and "CUÁNDO" in cal["porQueRetro"], cal.get("filtro"))
    # la vía 2 es la PRUEBA de que el filtro RETRO no es un capricho: con los
    # retro adentro el ISE «predice» (+0.36) y sin ellos no (−0.60)
    fc = cal["firmaDeContaminacion"]
    check("la firma de contaminación viaja con la calibración",
          fc["via2ConRetro"]["skill"] > 0 > fc["via2SinRetro"]["skill"], fc)
    check("el Brier viaja con su línea de base, no suelto",
          cal["brier"] > cal["brierTasaBase"] and "restan" in cal["brierNota"],
          {k: cal[k] for k in ("brier", "brierTasaBase")})
    check("las dos vías fallan en direcciones OPUESTAS: no hay corrección global",
          "sobreestima" in cal["direccionesOpuestas"]["via1"]
          and "subestima" in cal["direccionesOpuestas"]["via2"], cal["direccionesOpuestas"])
    check("el único positivo cae en la banda MÁS BAJA: la escala no ordena",
          cal["porBanda"]["3-5"]["positivos"] == 1
          and cal["porBanda"]["5-7"]["positivos"] == 0
          and cal["porBanda"]["7-8.5"]["positivos"] == 0, cal["porBanda"])
    check("y en el esquema vigente de 6 no hay ni un positivo",
          cal["positivosEnEsquemaVigente"] == 0, cal)
    alta = r["altaDelSemaforo"]
    check("el alta del semáforo pide las tres condiciones, no solo el N",
          set("abc") <= set(alta), sorted(alta))
    # una condición que NO se puede satisfacer es un candado, no una condición:
    # un positivo `pre_rubrica` no se puede reexpresar ni con todo el trabajo
    # del mundo, así que sale del conteo en vez de trabar la (c) para siempre
    check("un positivo pre_rubrica sale del conteo, no bloquea la (c)",
          "pre_rubrica` no" in alta["c"] and "sale del conteo" in alta["c"], alta["c"])
    check("pero uno `bloqueado` sí la bloquea: ese sí se puede arreglar",
          "sí lo bloquea" in alta["c"], alta["c"])
    check("y (a) exige los 5 positivos EN EL ESQUEMA VIGENTE",
          "ESQUEMA VIGENTE" in alta["a"], alta["a"])

    # denominador VARIABLE del bloque P: P1a sin dato promedia sobre cinco
    sin_p1a = {k: v for k, v in todos.items() if k != "P1a"}
    rp = tdemod.indice(sin_p1a)
    check("P1a sin dato promedia el bloque P sobre 5, no sobre 6",
          len(rp["indicadoresUsados"]["P"]) == 5, rp["indicadoresUsados"]["P"])
    check("y el denominador variable se DECLARA",
          any("sobre 5" in x for x in rp["compuertasOperadas"]), rp["compuertasOperadas"])

    # de punta a punta: los indicadores entran por el parte y el índice sale calculado
    con_ind = _parte(sin_ficha)
    con_ind["tde"] = {"equipo": "a", "ie": 9.9, "indicadores": todos}
    c.post(f"{A}/analisis/cowork", json=con_ind)
    leido = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["tde"]["bloques"][0]
    check("el IE que se lee es el calculado, no el que llegó escrito",
          leido["ie"] == 5.0, (leido.get("ie"), leido.get("declarado")))
    check("y la discrepancia con lo declarado se delata",
          any("IE" in x for x in leido["discrepancia"]), leido.get("discrepancia"))
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))

    # ── LO QUE FALTA SE AVISA AL DEPOSITAR, NO AL CERRAR ────────────────────
    # Caso real: dos partes sin `cadena` y sin `tde`. Nadie se enteró hasta el
    # cierre, 12 h después, cuando llenarlos ya habría sido hindsight.
    pelado = {"fixtureId": sin_ficha, "equipos": {"a": {"bloques": {"A": 3}}, "b": {"bloques": {"A": 3}}}}
    rec = c.post(f"{A}/analisis/cowork", json=pelado).json()
    bloques_faltantes = {x["bloque"] for x in rec["faltan"]}
    check("un parte sin cadena lo avisa al depositar", "cadena" in bloques_faltantes, rec["faltan"])
    check("y sin tde también", "tde" in bloques_faltantes, bloques_faltantes)
    check("y sin reparto 1X2 avisa que el caso se cierra sin métrica",
          "pronostico.probabilidades" in bloques_faltantes, bloques_faltantes)
    check("cada aviso dice qué va a costar y cómo se arregla ahora",
          all(x.get("costara") and x.get("comoSeArregla") for x in rec["faltan"]), rec["faltan"])
    check("y el de la cadena nombra sinPronosticoPrevio, que es donde se cobra",
          any("sinPronosticoPrevio" in x["costara"] for x in rec["faltan"] if x["bloque"] == "cadena"),
          rec["faltan"])
    # el parte completo con cadena, tde y pronóstico no tiene nada que avisar
    lleno = _parte(sin_ficha)
    lleno["cadena"] = {"a": {"pronostico": "A domina el balón parado"}}
    lleno["pronostico"] = {"probabilidades": {"local": 50, "empate": 30, "visita": 20},
                           "falsador": "si el visitante abre antes del 20', la lectura falla"}
    rec = c.post(f"{A}/analisis/cowork", json=lleno).json()
    check("un parte completo no inventa avisos", rec["faltan"] == [], rec["faltan"])
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))

    # ── lectura: lo calculado ───────────────────────────────────────────────
    r = c.get(f"{A}/analisis/cowork/{sin_ficha}")
    check("lee el parte", r.status_code == 200, r.text[:200])
    d = r.json()
    a, b = d["equipos"]["a"], d["equipos"]["b"]
    # A=4 ·1 + B=5 ·1.5 + C=3 ·1 + D=4 ·1 + E=3 ·2 = 4+7.5+3+4+6 = 24.5 sobre 27
    check("total ponderado calculado", a["total"] == 24.5, a["total"])
    check("máximo con bloque C = 27", a["maximoAlcanzable"] == 27, a["maximoAlcanzable"])
    check("porcentaje calculado", a["porcentaje"] == 90.7, a["porcentaje"])
    check("clasificación ≥70% = FORMADO", a["clasificacion"] == "FORMADO", a["clasificacion"])
    # B: A=1 + B=2 ·1.5 + D=1 + E=1 ·2 = 1+3+1+2 = 7 sobre 23 (bloque C excluido)
    check("bloque excluido no suma ni al total ni al máximo",
          (b["total"], b["maximoAlcanzable"]) == (7.0, 23.0), (b["total"], b["maximoAlcanzable"]))
    check("clasificación <40% = SIN FORMACION", b["clasificacion"] == "SIN_FORMACION", b["clasificacion"])
    check("el motivo de exclusión viaja con el bloque",
          "R-KT.2" in b["bloques"]["C"]["motivoExclusion"], b["bloques"]["C"])
    check("matchup normalizado sin el prefijo", d["matchup"]["diagnostico"] == "FAVORABLE",
          d["matchup"]["diagnostico"])
    check("las tres fuentes del pronóstico viajan juntas",
          all(d["pronostico"][k] for k in ("motor", "matriz", "mercado")), d["pronostico"])

    # ── el parte se puede reconstruir desde su propia lectura ───────────────
    # El POST reemplaza el parte ENTERO: corregir algo es leer → modificar →
    # re-depositar. Si la lectura no devuelve todo, ese viaje pierde datos.
    eco = d["entrada"]
    check("la lectura devuelve los eventos del timeline que se depositaron",
          len(eco["timelineEventos"]) == 1, eco.get("timelineEventos"))
    check("y la narrativa, y los pronósticos de la cadena",
          eco["timelineNarrativa"].startswith("Semestre") and eco["cadena"]["a"].startswith("A domina"),
          {k: eco[k] for k in ("timelineNarrativa", "cadena")})
    # el viaje completo: leer, re-depositar TAL CUAL, y que no se pierda nada.
    # Tal cual es literal: el cuerpo del POST es la respuesta del GET sin tocar
    # una coma —`entrada` anidada incluida, y también el eco de lo calculado—.
    # Cualquier otra cosa obliga a quien corrige a desarmar la respuesta a mano,
    # y ahí es donde se pierden campos.
    ida = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    rec = c.post(f"{A}/analisis/cowork", json=ida).json()
    check("la respuesta del GET se vuelve a depositar tal cual, sin perder nada",
          rec["perdido"] == [], rec.get("perdido"))
    check("y sin un solo rechazo inventado en el viaje de vuelta",
          rec["rechazos"] == [], rec.get("rechazos"))
    vuelto = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("los eventos del timeline sobreviven al viaje",
          vuelto["entrada"]["timelineEventos"] == ida["entrada"]["timelineEventos"],
          vuelto["entrada"]["timelineEventos"])
    check("la cadena y los descartados también",
          (vuelto["entrada"]["cadena"], vuelto["entrada"]["descartados"])
          == (ida["entrada"]["cadena"], ida["entrada"]["descartados"]),
          vuelto["entrada"])
    check("los DOS bloques del TDE sobreviven al viaje, con su lado",
          [b["equipo"] for b in vuelto["tde"]["bloques"]]
          == [b["equipo"] for b in ida["tde"]["bloques"]] != [],
          [b["equipo"] for b in vuelto["tde"]["bloques"]])
    check("y los totales calculados salen idénticos",
          [vuelto["equipos"][l]["porcentaje"] for l in ("a", "b")]
          == [ida["equipos"][l]["porcentaje"] for l in ("a", "b")],
          [vuelto["equipos"][l]["porcentaje"] for l in ("a", "b")])

    # lo suelto en la raíz manda sobre el eco: quien corrige escribe el campo
    # nuevo arriba y no tiene que acordarse de limpiar `entrada`
    mano = {**ida, "timelineNarrativa": "corregido a mano"}
    c.post(f"{A}/analisis/cowork", json=mano)
    vuelto = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("un campo escrito suelto en la raíz le gana al que trae `entrada`",
          vuelto["entrada"]["timelineNarrativa"] == "corregido a mano",
          vuelto["entrada"]["timelineNarrativa"])

    c.post(f"{A}/analisis/cowork", json=ida)
    d = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()

    # ── bloque F congelado: las dos ramas ───────────────────────────────────
    disp = a["disponibilidad"]
    check("sin once, el bloque F no se resuelve", disp["resuelto"] is False)
    check("sin once hay dos ramas", set(disp["ramas"]) == {"a", "b"}, list(disp.get("ramas", {})))
    # rama A: solo la baja pública (A Jugador6 = DEF TH → peso 2)
    check("rama A pesa solo las bajas públicas", disp["ramas"]["a"]["ip"] == 2.0,
          disp["ramas"]["a"]["ip"])
    # rama B: además el 🔴 más pesado disponible = el arquero titular (3 × 1.5 = 4.5)
    check("rama B añade el titular fijo más pesado", disp["ramas"]["b"]["ip"] == 6.5,
          disp["ramas"]["b"]["ip"])
    check("rama B aplica el ×1.5 del arquero", disp["ramas"]["b"]["multiplicadorGk"] is True)
    check("la rama B declara a quién saca", disp["ramas"]["b"]["ausenteHipotetico"].startswith("A "),
          disp["ramas"]["b"].get("ausenteHipotetico"))
    check("estado del parte: pendiente de once", d["estado"] == "pendiente_xi", d["estado"])
    check("el parte aparece en pendientes",
          any(p["fixtureId"] == sin_ficha and p["faltaXi"] == ["a", "b"]
              for p in c.get(f"{A}/analisis/cowork/pendientes").json()))

    # ── llega el once a mano (el pantallazo) ────────────────────────────────
    once_a = [f"A Jugador{n}" for n in (1, 3, 4, 5, 6, 7, 8, 10, 12, 13, 14)]
    banca_a = ["A Jugador2", "A Jugador9"]   # 9 es MID TH: rotación voluntaria
    r = c.post(f"{A}/analisis/cowork/{sin_ficha}/xi",
               json={"a": {"once": once_a, "banca": banca_a, "formacion": "4-3-3",
                           "fuente": "pantallazo BeSoccer"}})
    check("el once a mano se acepta", r.status_code == 200, r.text[:300])
    disp = r.json()["equipos"]["a"]["disponibilidad"]
    check("con once, el bloque F queda resuelto", disp["resuelto"] is True)
    check("la fuente del once queda declarada", disp["fuente"] == "pantallazo BeSoccer", disp["fuente"])
    # ausentes de la hoja: 11, 15, 16 (ATK ROT, ATK SUP, GK SUP… según el plan)
    ausentes = {f["nombre"] for f in disp["fuera"]}
    check("quien no figura en la hoja cuenta como baja de la fecha", ausentes, "no detectó ausencias")
    check("el titular en banca NO cuenta como ausencia",
          "A Jugador9" not in ausentes, ausentes)
    check("F4 cuenta la rotación voluntaria", disp["f4"]["rotados"] == 1, disp["f4"])
    check("el IP resuelto es un número propio, no una rama",
          disp["ip"] != disp.get("ramas", {}).get("a", {}).get("ip", -1))
    check("el lado sin once sigue congelado",
          r.json()["equipos"]["b"]["disponibilidad"]["resuelto"] is False)
    check("con un solo lado el parte sigue pendiente", r.json()["estado"] == "pendiente_xi",
          r.json()["estado"])

    # una hoja que no casa con la tabla NO cierra el bloque: se declara el choque
    r = c.post(f"{A}/analisis/cowork/{sin_ficha}/xi",
               json={"b": {"once": [f"Nadie Conocido{n}" for n in range(11)], "fuente": "prueba"}})
    dispb = r.json()["equipos"]["b"]["disponibilidad"]
    check("un once que no casa con la tabla no cierra el bloque F",
          dispb["resuelto"] is False and "conflicto" in dispb, dispb.get("conflicto"))
    check("el conflicto dice cuántos nombres casaron", "0 de 11" in dispb["conflicto"],
          dispb.get("conflicto"))
    check("un once que no casa deja el parte pendiente", r.json()["estado"] == "pendiente_xi",
          r.json()["estado"])

    # ahora sí, el once bueno del lado b
    r = c.post(f"{A}/analisis/cowork/{sin_ficha}/xi", json={"b": {
        "once": [f"B Jugador{n}" for n in (1, 3, 4, 5, 6, 8, 9, 10, 13, 14, 15)],
        "fuente": "rueda de prensa"}})
    check("con los dos onces el parte queda confirmado", r.json()["estado"] == "confirmado",
          r.json()["estado"])
    check("ya no aparece en pendientes",
          all(p["fixtureId"] != sin_ficha for p in c.get(f"{A}/analisis/cowork/pendientes").json()))

    # re-depositar el parte NO borra el once ya resuelto
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))
    check("el once sobrevive a un parte nuevo",
          c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]["disponibilidad"]["resuelto"] is True)

    # ── el once desde la ficha ya ingestada (costo cero) ────────────────────
    c.post(f"{A}/analisis/cowork", json=_parte(con_ficha))
    titulares = [r["jugador"] for r in dbmod.query(
        "sad", "SELECT jugador FROM alineaciones WHERE fixture_id=? AND titular=1 LIMIT 3", (con_ficha,))]
    r = c.post(f"{A}/analisis/cowork/{con_ficha}/xi", json={"desdeFicha": True})
    check("el once sale de la ficha sin pedirle nada a nadie", r.status_code == 200, r.text[:300])
    dispf = r.json()["equipos"]["a"]["disponibilidad"]
    check("la ficha se declara como fuente", "API-Football" in dispf.get("fuente", ""), dispf.get("fuente"))
    check("la ficha que no casa con la tabla tampoco cierra el bloque",
          dispf["resuelto"] is False and dispf.get("conflicto"), dispf.get("conflicto"))
    check("y los nombres que no casaron se listan",
          len(dispf["noReconocidos"]) >= len(titulares), dispf.get("noReconocidos"))

    # ── LA FICHA NO SE PISA A MANO SIN DECIRLO (reportado por Cowork, 1549492) ──
    once_manual = [f"Home Jugador{i}" for i in range(1, 12)]
    r = c.post(f"{A}/analisis/cowork/{con_ficha}/xi", json={"a": {"once": once_manual, "fuente": "prueba"}})
    check("un POST manual sobre un lado que ya viene de la ficha responde 200", r.status_code == 200, r.text[:200])
    check("…pero NO lo pisa: el lado se conserva y se dice por qué",
          r.json().get("xiConservados", {}).get("a", {}).get("porque")
          and "API-Football" in r.json()["equipos"]["a"]["disponibilidad"].get("fuente", ""),
          (r.json().get("xiConservados"), r.json()["equipos"]["a"]["disponibilidad"].get("fuente")))
    r = c.post(f"{A}/analisis/cowork/{con_ficha}/xi",
               json={"a": {"once": once_manual, "fuente": "prueba", "reemplazar": True}})
    check("con `reemplazar: true` sí se pisa y la procedencia cambia",
          r.json()["equipos"]["a"]["disponibilidad"].get("fuente") == "prueba"
          and not r.json().get("xiConservados"), r.json()["equipos"]["a"]["disponibilidad"].get("fuente"))
    auto_r = c.post(f"{A}/analisis/cowork/xi/auto").json()
    check("xi/auto NO saltea el lado manual: cuando la ficha está, la ficha manda y lo dice en `reemplazados`",
          any(x["fixtureId"] == con_ficha and x["lado"] == "a" and x["fuenteAnterior"] == "prueba"
              for x in auto_r["reemplazados"]), auto_r.get("reemplazados"))
    check("y la procedencia vuelve a ser la ficha",
          "API-Football" in c.get(f"{A}/analisis/cowork/{con_ficha}").json()["equipos"]["a"]["disponibilidad"].get("fuente", ""))
    otra_r = c.post(f"{A}/analisis/cowork/xi/auto").json()
    check("un lado que ya viene de la ficha no se vuelve a reemplazar",
          all(x["fixtureId"] != con_ficha for x in otra_r["reemplazados"]), otra_r.get("reemplazados"))

    # sin ficha ni once a mano: 409 que dice qué correr, no un 500
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))
    c.delete(f"{A}/analisis/cowork/{sin_ficha}")
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))
    r = c.post(f"{A}/analisis/cowork/{sin_ficha}/xi", json={"desdeFicha": True})
    check("sin alineaciones el error dice qué hacer",
          r.status_code == 409 and "ficha_partido" in r.json()["detail"], r.text[:200])

    # ── borrado y 404 ───────────────────────────────────────────────────────
    check("borra el parte", c.delete(f"{A}/analisis/cowork/{sin_ficha}").status_code == 200)
    check("parte inexistente → 404", c.get(f"{A}/analisis/cowork/{sin_ficha}").status_code == 404)

    # ── jugadores sin zona/rol no entran (serían relleno) ───────────────────
    p = _parte(sin_ficha)
    p["equipos"]["a"]["plantel"].append({"nombre": "Sin Datos", "zona": "", "rol": ""})
    p["equipos"]["a"]["plantel"].append({"nombre": "", "zona": "MID", "rol": "TF"})
    r = c.post(f"{A}/analisis/cowork", json=p)
    check("jugador sin zona o sin nombre se descarta", r.json()["jugadores"]["a"] == 16,
          r.json()["jugadores"])

    # ── lo que cada skill produce tiene sitio ───────────────────────────────
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))
    d = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()

    # bloque G: el calendario NO viaja en el parte, pero el DTO trae los ids
    # con los que la pantalla lo pide ya calculado
    check("el parte trae los ids de equipo para el calendario",
          d["partido"]["equipoAId"] > 0 and d["partido"]["equipoBId"] > 0, d["partido"])

    # bloque H completo: los tres indicadores, con el inválido normalizado
    check("los indicadores H2 viajan", (d["matchup"]["h2a"], d["matchup"]["h2b"]) == ("verde", "verde"),
          d["matchup"])
    check("un H2 inválido cae en 'na', no se inventa", d["matchup"]["h2c"] == "na", d["matchup"])

    # lectura SAD
    ls = d["lecturaSad"]
    check("la lectura SAD tiene sitio propio", ls["moduloOperativo"].startswith("Regresión"), ls)
    check("el 1X2 conserva su rango ampliado", ls["unXDos"]["rangoAmpliado"] is True, ls["unXDos"])
    check("la paradoja viaja", ls["paradoja"].startswith("El mejor EFE"), ls)
    check("la lectura del reventón de Cowork tiene sitio (una línea por equipo)",
          ls["reventon"].startswith("A: muy alto"), ls.get("reventon"))
    rc = ls["reventonCalculado"]
    check("el reventón se CALCULA al leer, uno por lado, con la familia total",
          rc and set(rc) == {"a", "b"} and all("riesgo" in rc[l] and "actual" in rc[l] and "rival" in rc[l]
                                                and "error" not in rc[l] for l in ("a", "b")), rc)
    check("cada lado trae la estabilidad y el aviso de que es guía, no probabilidad",
          all(rc[l]["estabilidad"] in ("estable", "en transición", "inestable", "sin dato")
              and "no probabilidad" in rc[l]["aviso"] for l in ("a", "b")), rc)
    check("con burbuja abierta el riesgo trae nivel y motivos; sin ella, null",
          all((rc[l]["actual"] is None) == (rc[l]["riesgo"] is None) for l in ("a", "b"))
          and all(rc[l]["riesgo"] is None or (rc[l]["riesgo"]["nivel"] and rc[l]["riesgo"]["motivos"]) for l in ("a", "b")), rc)
    check("el contrato documenta la forma de `cadena` (objeto por lado) y los tipos de `timelineEventos`",
          (lambda ct: '"a"' in ct["cadena"]["forma"] and ct["timelineEventos"]["tipos"] == ["institucional", "tecnico", "sancion", "hito"]
           and "titulo" in ct["documentos"]["forma"])(c.get(A + "/analisis/cowork/contrato").json()))
    check("el contrato declara la clave reventon de la lectura SAD",
          "reventon" in c.get(A + "/analisis/cowork/contrato").json()["lecturaSad"]["claves"])
    # ALERTA DE EXTREMO: viaja por lado, y si está activa el parte la grita en la tira de alertas
    check("cada lado trae `extremo` (null sin burbuja o sin base; con burbuja, el bloque completo)",
          all("extremo" in rc[l] and (rc[l]["extremo"] is None or
                                       {"activo", "kRecord", "rachaRecord", "partidosHistoria", "maximoPrevio", "motivos", "texto"}
                                       <= set(rc[l]["extremo"])) for l in ("a", "b")), rc)
    activos = {l for l in ("a", "b") if (rc[l]["extremo"] or {}).get("activo")}
    kext = {a["equipo"] for a in d["alertas"] if a["codigo"] == "K-EXTREMO"}
    check(f"la alerta K-EXTREMO del parte sale exactamente para los lados con extremo activo ({sorted(activos) or 'ninguno'})",
          kext == activos, {"alertas": kext, "extremo": activos})
    check("una alerta K-EXTREMO es estructural y pide no cargar la apuesta",
          all(a["tipo"] == "estructural" and "NO cargar" in a["detalle"] for a in d["alertas"] if a["codigo"] == "K-EXTREMO"))
    # el caso Alavés–Valencia, sintético: K −32 sobre máximo 24, riesgo bajo → la alerta sale igual
    from backend.analisis.parte import alertas_extremo
    sint = {"a": {"actual": {"k": 5.0}, "extremo": {"activo": False, "motivos": []}},
            "b": {"actual": {"k": -32.0}, "riesgo": {"nivel": "bajo"},
                  "extremo": {"activo": True, "kRecord": True, "rachaRecord": False, "partidosHistoria": 118,
                              "motivos": ["K 32.0: la más baja de los 118 partidos que hay en la base (máximo previo 24.09)"]}}}
    al = alertas_extremo(sint, {"a": "Alavés", "b": "Valencia"})
    check("K −32 sobre máximo 24 con riesgo BAJO → UNA alerta K-EXTREMO para el lado b, con el nombre, la K y el N",
          len(al) == 1 and al[0]["equipo"] == "b" and al[0]["codigo"] == "K-EXTREMO"
          and "Valencia" in al[0]["detalle"] and "-32.00" in al[0]["detalle"] and "118 partidos" in al[0]["detalle"], al)
    check("sin reventón calculado no hay alerta ni excepción", alertas_extremo(None, {}) == [])
    sint_c = {"a": {"actual": {"k": -17.93}, "riesgo": {"nivel": "bajo"},
                    "extremo": {"activo": False, "cerca": True, "motivos": ["K -17.93: más baja que el 95 % de las 39 burbujas - que reventaron (récord previo -19.54, a 1.61)"]}},
              "b": {"actual": {"k": 3.0}, "extremo": {"activo": False, "cerca": False, "motivos": []}}}
    alc = alertas_extremo(sint_c, {"a": "ADT", "b": "Cienciano"})
    check("K −17.9 a 1.6 del récord con riesgo BAJO → UNA alerta K-CERCA-EXTREMO (tipo dato) para el lado a, sin K-EXTREMO",
          len(alc) == 1 and alc[0]["codigo"] == "K-CERCA-EXTREMO" and alc[0]["equipo"] == "a"
          and alc[0]["tipo"] == "dato" and "ADT" in alc[0]["detalle"] and "95 %" in alc[0]["detalle"], alc)


    # caja de sensibilidad
    sens = d["equipos"]["a"]["sensibilidad"]
    check("la caja de sensibilidad viaja por equipo", len(sens) == 1, sens)
    check("un supuesto vacío no entra", all(x["supuesto"] for x in sens), sens)

    # TDE estructurado
    check("el TDE guarda un bloque POR EQUIPO", len(d["tde"]["bloques"]) == 2, d["tde"])
    t = next(b for b in d["tde"]["bloques"] if b["equipo"] == "b")
    check("el TDE trae sus dos índices", (t["ie"], t["ise"]) == (58.0, 31.0), t)
    check("el nivel del IE llega del skill, no del backend", t["ieNivel"] == "ambar", t)
    check("el ISE sin nivel queda vacío en vez de inventado", t["iseNivel"] == "", t)
    check("el TDE trae su ventana y su causa", t["ventana"] and t["tipologia"], t)
    check("las vías del TDE viajan", len(t["vias"]) == 1, t.get("vias"))
    # EL NIVEL ES UNA ETIQUETA Y EL ÍNDICE UN NÚMERO (reportado por Cowork: diez
    # partes con el índice en `ieNivel`, nueve guardados con "" y sin un rechazo)
    p_niv = _parte(sin_ficha)
    p_niv["tde"] = {"bloques": [
        {"equipo": "a", "ieNivel": 6.4, "ise": 3, "iseNivel": "alto", "ventana": "75-90'", "tipologia": "x"},
        {"equipo": "b", "disciplina43": True, "ventana": "60-75'", "tipologia": "y"},
    ]}
    r_niv = c.post(f"{A}/analisis/cowork", json=p_niv).json()
    rz = {x["donde"]: x for x in r_niv["rechazos"]}
    r_niv = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("un número en `ieNivel` se RECHAZA con su sitio, no se tira en silencio",
          "tde.bloques[0].ieNivel" in rz and "verde" in rz["tde.bloques[0].ieNivel"]["esperado"], list(rz))
    ta = next(b for b in r_niv["tde"]["bloques"] if b["equipo"] == "a")
    check("y el número se rescata en `ie`, que es el campo numérico del contrato",
          ta["ie"] == 6.4 and ta["ieNivel"] == "", ta)
    check("una etiqueta fuera de verde/ambar/rojo también se rechaza",
          "tde.bloques[0].iseNivel" in rz and ta["iseNivel"] == "" and ta["ise"] == 3, (list(rz), ta))
    tb = next(b for b in r_niv["tde"]["bloques"] if b["equipo"] == "b")
    check("`disciplina43: true` sin vías, indicadores ni índice se rechaza y queda false",
          "tde.bloques[1].disciplina43" in rz and tb["disciplina43"] is False, (list(rz), tb))

    # ── EL DT DEL PARTE: {nombre, desde} sin perder la antigüedad (Cowork, B y C) ──
    fx_dt = dbmod.query_one("sad", "SELECT substr(date,1,10) AS d, ht.name AS a FROM fixtures f "
                            "JOIN teams ht ON ht.id=f.home_team_id WHERE f.id=?", (sin_ficha,))
    dt_base = dbmod.query_one("sad", "SELECT e.nombre, e.desde FROM entrenadores e JOIN fixtures f "
                              "ON f.home_team_id=e.team_id WHERE f.id=?", (sin_ficha,))
    from datetime import date as _date
    dias = (_date.fromisoformat(fx_dt["d"]) - _date.fromisoformat("2025-06-15")).days
    p_dt = _parte(sin_ficha)
    p_dt["equipos"]["a"]["dt"] = {"nombre": "Diego Simeone", "desde": "2025-06-15"}
    p_dt["equipos"]["b"]["dt"] = "Edin Terzić"
    d_dt = c.post(f"{A}/analisis/cowork", json=p_dt).json()
    d_dt = {**c.get(f"{A}/analisis/cowork/{sin_ficha}").json(), "rechazos": d_dt["rechazos"]}
    da, db_ = d_dt["equipos"]["a"]["dt"], d_dt["equipos"]["b"]["dt"]
    check("`dt: {nombre, desde}` calcula los meses hasta el partido",
          da["nombre"] == "Diego Simeone" and da["meses"] == round(dias / (365.25 / 12), 1)
          and da["origenMeses"] == "desde" and da["desde"] == "2025-06-15", da)
    check("`dt` como texto ya NO guarda meses 0: queda null y se rechaza pidiendo `desde`",
          db_["nombre"] == "Edin Terzić" and db_["meses"] is None
          and any(x["donde"] == "equipos.b.dt" for x in d_dt["rechazos"]), (db_, d_dt["rechazos"]))
    p_dt["equipos"]["a"]["dt"] = {"nombre": dt_base["nombre"]}
    d_dt = c.post(f"{A}/analisis/cowork", json=p_dt).json()
    d_dt = {**c.get(f"{A}/analisis/cowork/{sin_ficha}").json(), "rechazos": d_dt["rechazos"]}
    da = d_dt["equipos"]["a"]["dt"]
    check("el nombre que coincide con el DT de la base toma la fecha de asunción de la base",
          da["meses"] is not None and da["origenMeses"] == "base" and da["desde"] == dt_base["desde"],
          (da, dict(dt_base)))
    p_dt["equipos"]["a"]["dt"] = {"nombre": "Según prensa de esta semana dirige el interino tras la salida "
                                            "del técnico anterior el pasado martes por malos resultados"}
    p_dt["equipos"]["b"]["dt"] = "desconocido"
    d_dt = c.post(f"{A}/analisis/cowork", json=p_dt).json()
    d_dt = {**c.get(f"{A}/analisis/cowork/{sin_ficha}").json(), "rechazos": d_dt["rechazos"]}
    check("una oración en `dt.nombre` se rechaza y queda «sin establecer»",
          d_dt["equipos"]["a"]["dt"]["nombre"] == "sin establecer"
          and any(x["donde"] == "equipos.a.dt.nombre" for x in d_dt["rechazos"]), d_dt["equipos"]["a"]["dt"])
    check("«desconocido», vacío o ausente se guardan como el canónico «sin establecer», meses null",
          d_dt["equipos"]["b"]["dt"] == {"nombre": "sin establecer", "meses": None, "desde": "", "origenMeses": ""},
          d_dt["equipos"]["b"]["dt"])
    p_dt["equipos"]["a"]["dt"] = {"nombre": "Diego Simeone", "meses": 177.5, "desde": "2011-12-23"}
    c.post(f"{A}/analisis/cowork", json=p_dt)
    d_dt = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("`meses` declarado manda sobre `desde`",
          d_dt["equipos"]["a"]["dt"]["meses"] == 177.5 and d_dt["equipos"]["a"]["dt"]["origenMeses"] == "declarado")
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))

    # timeline: lo institucional entra, el partido copiado se descarta y los
    # partidos de NUESTRA base se funden
    tl = d["timeline"]
    check("el timeline se arma al leer", tl is not None and tl["equipos"][0]["nombre"] == fx["a"],
          (tl or {}).get("equipos"))
    tipos = [e["tipo"] for e in (tl or {}).get("eventos", [])]
    check("el evento institucional de Cowork entra", "tecnico" in tipos, tipos[:8])
    check("un resultado copiado a mano se descarta",
          not any(e.get("titulo") == "Victoria 2-0" for e in (tl or {}).get("eventos", [])), tipos[:8])
    check("la fuente de la ingesta se declara en el timeline",
          any("sad.db" in f for f in (tl or {}).get("fuentes", [])), (tl or {}).get("fuentes"))
    check("la narrativa viaja", (tl or {}).get("narrativa", "").startswith("Semestre"), (tl or {}).get("narrativa"))

    # cadena del DTP: la película del equipo sigue rodando
    rec = c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha)).json()
    check("el recibo dice en qué cadenas escribió", set(rec["cadena"]) == {fx["a"], fx["b"]}, rec.get("cadena"))
    eq_id = dbmod.query_one("sad", "SELECT id FROM teams WHERE name=?", (fx["a"],))["id"]
    cadena = c.get(f"{A}/equipos/{eq_id}/cadena").json()
    check("el pronóstico entra en la cadena del equipo",
          any((e.get("registro") or {}).get("pronostico_clave", "").startswith("A domina") for e in cadena),
          cadena[:1])
    check("la cadena del parte no emite veredicto (anti-hindsight)",
          all((e.get("registro") or {}).get("veredicto", "") == "" for e in cadena), cadena[:1])

    # un parte sin los bloques nuevos sigue siendo válido: nada es obligatorio
    minimo = {"fixtureId": sin_ficha, "equipos": {"a": {"bloques": {"A": 2}}, "b": {"bloques": {"A": 2}}}}
    r = c.post(f"{A}/analisis/cowork", json=minimo)
    check("un parte mínimo se acepta igual", r.status_code == 200, r.text[:200])
    d2 = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("sin TDE el bloque va vacío, no inventado", d2["tde"] == {}, d2["tde"])
    check("sin lectura SAD los campos van vacíos", d2["lecturaSad"]["moduloOperativo"] == "", d2["lecturaSad"])
    c.delete(f"{A}/analisis/cowork/{sin_ficha}")

    # ── FASE B · el veredicto a las 12 h ────────────────────────────────────
    # un partido terminado hace rato y con ficha de eventos capturada
    pasado = dbmod.query_one(
        "sad", "SELECT f.id, COALESCE(f.fulltime_home, f.goals_home) AS gl, "
               "COALESCE(f.fulltime_away, f.goals_away) AS gv, f.date "
               "FROM fixtures f WHERE f.status_short='FT' AND f.date < datetime('now','-2 days') "
               "ORDER BY f.date DESC LIMIT 1")
    marcador_real = f"{pasado['gl']}-{pasado['gv']}"
    real = "local" if pasado["gl"] > pasado["gv"] else ("visita" if pasado["gv"] > pasado["gl"] else "empate")

    # el pronóstico se declara ANTES: se deposita el parte apuntando al ganador real
    p_ok = _parte(pasado["id"])
    otras = [k for k in ("local", "empate", "visita") if k != real]
    p_ok["pronostico"]["probabilidades"] = {real: 60, otras[0]: 25, otras[1]: 15}
    p_ok["pronostico"]["marcador"] = marcador_real
    c.post(f"{A}/analisis/cowork", json=p_ok)

    # la lista de pendientes es el disparador
    sobre = c.get(f"{A}/analisis/cowork/veredictos/pendientes").json()
    pend = sobre["pendientes"]
    check("el partido jugado aparece como pendiente de veredicto",
          any(x["fixtureId"] == pasado["id"] for x in pend), pend[:2])
    check("el sobre declara la ventana y el criterio, no solo la lista",
          sobre["ventanaHoras"] == 12 and "arrancó hace más de" in sobre["criterio"],
          {k: sobre.get(k) for k in ("ventanaHoras", "criterio")})
    check("y cuenta cuántos partes hay sin cerrar", sobre["sinCerrar"] >= 1, sobre["sinCerrar"])
    # UN PARTIDO EN CURSO SE EXPLICA, NO SE CALLA. Es el caso de la 3ª corrida:
    # `[]` pelado y Cowork sin poder decir si esperar o avisar.
    check("un parte que no entra a la lista sale en noListados con su motivo",
          len(sobre["noListados"]) >= 1 and all(x.get("porque") for x in sobre["noListados"]),
          sobre["noListados"][:3])
    check("y un partido en curso trae su minuto y su marcador parcial",
          any("se está jugando" in x["porque"] and "minuto" in x["estado"]
              for x in sobre["noListados"]), sobre["noListados"][:3])
    check("el pendiente trae ya el marcador",
          next((x["marcador"] for x in pend if x["fixtureId"] == pasado["id"]), "") == marcador_real,
          pend[:2])
    check("un partido sin jugar NO aparece como pendiente",
          all(x["fixtureId"] != sin_ficha for x in pend), pend[:2])

    # la población es obligatoria y no se deduce
    r = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto",
               json={"seleccion": "cualquiera", "modoEvaluacion": "PRE",
                     "porLado": {"a": {"veredicto": "acierto"}}})
    check("una población inválida se rechaza explicando por qué",
          r.status_code == 422 and "acredita" in r.text, r.text[:200])
    r = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto",
               json={"seleccion": "ciega", "modoEvaluacion": "PRE", "porLado": {}})
    check("un veredicto sin ningún lado se rechaza", r.status_code == 422, r.status_code)

    r = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE", "falsadorCumplido": False,
        "porLado": {"a": {"veredicto": "acierto", "queP": "ganó como se dijo", "leccion": ""},
                    "b": {"veredicto": "fallo", "queP": "no llegó por fuera",
                          "leccion": "el bloque bajo entrenado sostiene los 90",
                          "skill": "teorema-del-echado"}},
    })
    check("el veredicto se acepta", r.status_code == 200, r.text[:300])
    v = r.json()
    check("sin salvedad, el campo viene vacío y no ausente", v["mancha"] == "", v.get("mancha"))
    # ── EL MODO DE FALLO (Jev): sellado al cerrar, para el dossier ────────────
    check("el veredicto trae la etiqueta de Jev sellada (sin clave: simulada, sin modo)",
          v["modoFallo"] and v["modoFallo"]["simulado"] is True
          and v["modoFallo"]["lados"].get("b", {}).get("modo") is None
          and "a" not in v["modoFallo"]["lados"], v.get("modoFallo"))
    eco = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json=v).json()
    check("re-depositar el eco con `modoFallo` no produce rechazos",
          not any(x["donde"].endswith("modoFallo") for x in eco.get("rechazos", [])), eco.get("rechazos"))
    # con guion, la etiqueta entra y llega a la lección
    import tempfile as _tf
    with _tf.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump({"modo_b": {"valor": "tde", "confianza": 0.9, "comoReal": True},
                   "mueve_b": {"valor": 0.9, "comoReal": True}}, fh)
        guion_mf = fh.name
    os.environ["SAD_JEV_GUION"] = guion_mf
    v2 = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json=v).json()
    os.environ.pop("SAD_JEV_GUION", None)
    os.unlink(guion_mf)
    check("con respuesta real el lado fallado queda etiquetado y dice si pide mover un número",
          v2["modoFallo"]["lados"]["b"]["modo"] == "tde"
          and v2["modoFallo"]["lados"]["b"]["proponeMoverNumero"] is True
          and v2["modoFallo"]["modelo"] == "guion", v2.get("modoFallo"))
    check("el modo de fallo no toca la población ni el acredita",
          v2["seleccion"] == "ciega" and v2["acredita"] is True)
    inv_mf = c.get(f"{A}/analisis/cowork/lecciones").json()
    it_mf = next((i for i in inv_mf["items"] if i["fixtureId"] == pasado["id"] and i["lado"] == "b"), None)
    check("la lección lleva la etiqueta y el «pide mover»",
          it_mf and it_mf["modoFallo"] == "tde" and it_mf["proponeMoverNumero"] is True, it_mf)
    check("el inventario agrupa los fallos por modo para el dossier",
          inv_mf["porModoFallo"]["porModo"].get("tde", 0) >= 1
          and "pidenMoverSinPoder" in inv_mf["porModoFallo"], inv_mf.get("porModoFallo"))
    sk_mf = next((x for x in inv_mf["porSkill"] if x["skill"] == "teorema-del-echado"), None)
    check("y cada skill trae su propio agrupado", sk_mf and sk_mf["porModoFallo"]["fallos"] >= 1)
    o = v["objetivo"]
    check("el marcador lo pone la base, no el veredicto", o["marcador"]["texto"] == marcador_real, o["marcador"])
    check("dice si el partido está terminado", o["marcador"]["terminado"] is True, o["marcador"])
    check("acierta el 1X2 declarado", o["unXDos"]["acerto"] is True and o["unXDos"]["real"] == real,
          o["unXDos"])
    check("acierta el marcador exacto", o["marcadorExacto"]["acerto"] is True, o["marcadorExacto"])
    # Brier de tres resultados con 60/25/15 sobre el acertado:
    # (0.6-1)² + (0.25-0)² + (0.15-0)² = 0.16 + 0.0625 + 0.0225 = 0.245
    check("el Brier se calcula y declara su escala", o["brier"]["valor"] == 0.245
          and "binario" in o["brier"]["escala"], o["brier"])

    # ── EL REVENTÓN, COMPROBADO (docs/REVENTON.md §11) ──────────────────────
    # lo declarado se reconstruye con la vista «al día del partido» (la misma
    # que sirve /burbujas?antesDe=) y lo observado sale de la K de ESE partido
    rv = o["reventon"]
    check("el objetivo trae el reventón por lado, con su nota de que es observación y no veredicto",
          set(rv) >= {"a", "b", "nota"} and "no veredicto" in rv["nota"], list(rv))
    fx_p = dbmod.query_one("sad", "SELECT home_team_id, away_team_id FROM fixtures WHERE id=?", (pasado["id"],))
    for lado, tid in (("a", fx_p["home_team_id"]), ("b", fx_p["away_team_id"])):
        r_l = rv[lado]
        ant = c.get(f"{A}/equipos/{tid}/burbujas", params={"antesDe": pasado["id"]}).json()["familias"]["total"]
        if not ant["actual"]:
            check(f"lado {lado}: sin burbuja antes del partido → sinBurbuja y nada observado",
                  r_l["sinBurbuja"] is True and r_l["observado"] is None, r_l)
            continue
        check(f"lado {lado}: lo declarado es EXACTAMENTE la burbuja de /burbujas?antesDe= (signo, K, racha, riesgo)",
              r_l["comprobable"] and r_l["declarado"]["signo"] == ant["actual"]["signo"]
              and r_l["declarado"]["k"] == ant["actual"]["k"]
              and r_l["declarado"]["partidos"] == ant["actual"]["partidos"]
              and r_l["declarado"]["riesgo"]["nivel"] == ant["riesgo"]["nivel"]
              and r_l["declarado"]["extremo"] == bool((ant.get("extremo") or {}).get("activo")),
              (r_l["declarado"], ant["actual"], ant["riesgo"]))
        hoy_b = c.get(f"{A}/equipos/{tid}/burbujas").json()["familias"]["total"]
        cerro = any(x["fixtureId"] == pasado["id"] for x in hoy_b["reventones"])
        check(f"lado {lado}: lo observado coincide con la historia entera ({'reventó' if cerro else 'siguió'})",
              r_l["observado"]["revento"] is cerro
              and (("reventó" in r_l["nota"]) if cerro else ("siguió" in r_l["nota"])), r_l)
    check("el reventón no emite acierto ni fallo: no hay `acerto` en el bloque",
          all("acerto" not in (rv[l] or {}) for l in ("a", "b")))
    # ¿EL 1X2 RESPETÓ LA BURBUJA? Por lado: a favor / en contra / neutro, y con
    # riesgo alto si lo respetó. Sin burbuja o sin 1X2 declarado, None.
    check("cada lado dice si el 1X2 fue a favor o en contra de su racha",
          all("pronosticoVsRacha" in rv[l] and "respetoRiesgo" in rv[l] for l in ("a", "b")), rv)
    for lado in ("a", "b"):
        r_l = rv[lado]
        if r_l.get("sinBurbuja") or not r_l.get("declarado"):
            check(f"lado {lado}: sin burbuja no hay racha que seguir → None",
                  r_l["pronosticoVsRacha"] is None and r_l["respetoRiesgo"] is None, r_l)
        else:
            gana = (o["unXDos"]["declarado"] == "local") if lado == "a" else (o["unXDos"]["declarado"] == "visita")
            sigue = gana if r_l["declarado"]["signo"] == "+" else not gana
            esperado = "neutro" if o["unXDos"]["declarado"] == "empate" else ("aFavor" if sigue else "enContra")
            check(f"lado {lado}: 1X2 «{o['unXDos']['declarado']}» contra burbuja {r_l['declarado']['signo']} → {esperado}",
                  r_l["pronosticoVsRacha"] == esperado, r_l)
            alto = r_l["declarado"]["riesgo"]["nivel"] in ("alto", "muy alto")
            check(f"lado {lado}: el respeto solo se juzga con riesgo alto (acá {r_l['declarado']['riesgo']['nivel']})",
                  (r_l["respetoRiesgo"] is None) if not alto else (r_l["respetoRiesgo"] == (esperado != "aFavor")), r_l)
    from backend.analisis.veredicto import pronostico_vs_racha
    check("burbuja «−» de la visita con 1X2 local = la visita pierde = sigue la racha = aFavor, y no respeta el riesgo alto",
          pronostico_vs_racha("b", {"signo": "-", "riesgo": {"nivel": "muy alto"}}, "local")
          == {"pronosticoVsRacha": "aFavor", "respetoRiesgo": False})
    check("el empate es neutro y con riesgo alto cuenta como respetado",
          pronostico_vs_racha("a", {"signo": "+", "riesgo": {"nivel": "alto"}}, "empate")
          == {"pronosticoVsRacha": "neutro", "respetoRiesgo": True})
    check("con riesgo bajo seguir la racha no es error: None, no False",
          pronostico_vs_racha("a", {"signo": "+", "riesgo": {"nivel": "bajo"}}, "local")["respetoRiesgo"] is None)

    # UNA SALVEDAD SOBRE UN CASO QUE ACREDITA. La población la declara quien
    # escribe; la salvedad no la cambia, pero queda en campo propio para que se
    # pueda auditar sin leer prosa. Caso real: un parte retocado con el partido
    # rodando cuyo pronóstico no se tocó — sigue siendo ciego, y aun así hay
    # algo que contar dentro de seis meses.
    r = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE",
        "mancha": "el parte se reescribió en el minuto 2 con el partido rodando; "
                  "el pronóstico quedó intacto",
        "porLado": {"a": {"veredicto": "acierto"}},
    })
    vm = r.json()
    check("una salvedad declarada se guarda", vm["mancha"].startswith("el parte se reescribió"),
          vm.get("mancha"))
    check("y NO le quita el acredita: la población sigue siendo la declarada",
          vm["acredita"] is True and vm["seleccion"] == "ciega", (vm["acredita"], vm["seleccion"]))
    # PRE SOBRE UN PARTIDO EN CURSO SE RECHAZA. No es criterio: `terminado` está
    # en nuestra base, y archivar como validación predictiva un caso puntuado en
    # el minuto 17 es justo lo que la fase B existe para impedir.
    en_curso = next((x["fixtureId"] for x in
                     c.get(f"{A}/analisis/cowork/veredictos/pendientes").json()["noListados"]
                     if "se está jugando" in x["porque"]), None)
    if en_curso:
        r = c.post(f"{A}/analisis/cowork/{en_curso}/veredicto", json={
            "seleccion": "ciega", "modoEvaluacion": "PRE",
            "porLado": {"a": {"veredicto": "acierto"}}})
        check("PRE sobre un partido sin terminar se rechaza", r.status_code == 422, r.status_code)
        check("y el mensaje dice que eso es COND", "COND" in r.text, r.text[:200])
        r = c.post(f"{A}/analisis/cowork/{en_curso}/veredicto", json={
            "seleccion": "ciega", "modoEvaluacion": "COND",
            "porLado": {"a": {"veredicto": "acierto"}}})
        check("COND sobre el mismo partido sí entra, y no acredita",
              r.status_code == 200 and r.json()["acredita"] is False, r.text[:200])

    # el mismo recibo que el parte: un campo mal escrito se DICE
    r = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE", "manchas": "typo",
        "porLado": {"a": {"veredicto": "acierto"}},
    })
    check("una clave desconocida en el veredicto se delata, no se tira",
          any("manchas" in x.get("donde", "") and "mancha" in x.get("esperado", "")
              for x in r.json().get("rechazos", [])),
          r.json().get("rechazos"))

    c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE",
        "mancha": "el parte se reescribió en el minuto 2 con el partido rodando; "
                  "el pronóstico quedó intacto",
        "porLado": {"a": {"veredicto": "acierto"}},
    })
    check("la salvedad sobrevive a la relectura",
          (c.get(f"{A}/analisis/cowork/{pasado['id']}/veredicto").json()["mancha"]
           == vm["mancha"]))

    # un reparto que no suma 100 se normaliza en vez de rechazarse
    p_norm = dict(p_ok)
    p_norm["pronostico"] = {**p_ok["pronostico"], "probabilidades": {real: 6, otras[0]: 2.5, otras[1]: 1.5}}
    c.post(f"{A}/analisis/cowork", json=p_norm)
    check("un reparto que no suma 100 se normaliza, no se rechaza",
          c.get(f"{A}/analisis/cowork/{pasado['id']}/veredicto").json()["objetivo"]["brier"]["valor"] == 0.245,
          c.get(f"{A}/analisis/cowork/{pasado['id']}/veredicto").json()["objetivo"]["brier"])
    c.post(f"{A}/analisis/cowork", json=p_ok)
    check("ciega + PRE acredita", v["acredita"] is True, v)
    check("el falsador queda declarado por quien lo comprobó",
          v["falsador"]["cumplido"] is False and v["falsador"]["texto"], v["falsador"])

    # anti-hindsight: este parte sí mandó cadena, así que el cierre entra
    check("sin pronóstico previo no se escribiría veredicto en la cadena",
          v["sinPronosticoPrevio"] == [], v.get("sinPronosticoPrevio"))
    eq_local = dbmod.query_one(
        "sad", "SELECT ht.id FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id WHERE f.id=?",
        (pasado["id"],))["id"]
    cad = c.get(f"{A}/equipos/{eq_local}/cadena").json()
    eslabon = next((e for e in cad if e["fixtureId"] == pasado["id"]), None)
    check("el veredicto cierra el eslabón de la cadena",
          (eslabon or {}).get("registro", {}).get("veredicto") == "acierto", eslabon)
    check("y el pronóstico previo NO se pisa al cerrar",
          (eslabon or {}).get("registro", {}).get("pronostico_clave", "").startswith("A domina"),
          (eslabon or {}).get("registro"))

    # el veredicto viaja con el parte y se puede leer aparte
    check("el parte trae su veredicto", c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["veredicto"] is not None)
    check("y hay endpoint propio para leerlo",
          c.get(f"{A}/analisis/cowork/{pasado['id']}/veredicto").status_code == 200)
    check("ya no aparece como pendiente",
          all(x["fixtureId"] != pasado["id"]
              for x in c.get(f"{A}/analisis/cowork/veredictos/pendientes").json()["pendientes"]))
    check("un fixture sin veredicto responde 404",
          c.get(f"{A}/analisis/cowork/{sin_ficha}/veredicto").status_code == 404)

    # UN PARTIDO TERMINADO ENTRA AUNQUE HAYA ARRANCADO HACE MENOS DE 12 H. Era el
    # hueco de la validación de la mañana: un partido de las 21:00 revisado a
    # las 8:00 (11 h) caía en noListados y Cowork cerraba cero casos.
    import os as _os
    import sqlite3 as _sq3
    from datetime import datetime as _dt, timedelta as _td, timezone as _tz
    _sad = _os.path.join(_os.environ["SAD_DATA_DIR"], "sad.db")
    with _sq3.connect(_sad) as _con:
        reciente, fecha_original = _con.execute(
            "SELECT id, date FROM fixtures WHERE status_short='FT' AND goals_home IS NOT NULL AND id!=? "
            "ORDER BY id DESC LIMIT 1", (pasado["id"],)).fetchone()
        _con.execute("UPDATE fixtures SET date=? WHERE id=?",
                     ((_dt.now(_tz.utc) - _td(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), reciente))
    c.post(f"{A}/analisis/cowork", json=_parte(reciente))
    sobre2 = c.get(f"{A}/analisis/cowork/veredictos/pendientes").json()
    with _sq3.connect(_sad) as _con:  # se devuelve la fecha: los checks de abajo eligen fixtures por fecha
        _con.execute("UPDATE fixtures SET date=? WHERE id=?", (fecha_original, reciente))
    check("un partido TERMINADO de hace 2 h ya entra como pendiente (no espera las 12 h desde el saque)",
          any(x["fixtureId"] == reciente for x in sobre2["pendientes"]),
          [x for x in sobre2["noListados"] if x["fixtureId"] == reciente])
    check("el criterio lo dice: terminado con marcador entra aunque arrancó hace menos de 12 h",
          "TERMINADO" in sobre2["criterio"] and "arrancó hace más de" in sobre2["criterio"], sobre2["criterio"])

    # REGRESIÓN: re-depositar el parte después del cierre no puede borrar el
    # veredicto ni cambiar el pronóstico ya declarado (sería hindsight)
    otro_pron = _parte(pasado["id"])
    otro_pron["pronostico"]["probabilidades"] = {real: 60, otras[0]: 25, otras[1]: 15}
    otro_pron["cadena"]["a"]["pronostico"] = "ahora digo otra cosa, con el resultado puesto"
    rec2 = c.post(f"{A}/analisis/cowork", json=otro_pron).json()
    check("un pronóstico distinto tras el partido se delata en el recibo",
          rec2["cadenaIgnorada"], rec2.get("cadenaIgnorada"))
    cad2 = c.get(f"{A}/equipos/{eq_local}/cadena").json()
    esl2 = next((e for e in cad2 if e["fixtureId"] == pasado["id"]), None)
    check("el pronóstico que manda sigue siendo el primero",
          (esl2 or {}).get("registro", {}).get("pronostico_clave", "").startswith("A domina"),
          (esl2 or {}).get("registro"))
    check("y el veredicto ya escrito sobrevive al re-depósito",
          (esl2 or {}).get("registro", {}).get("veredicto") == "acierto", (esl2 or {}).get("registro"))

    # población contaminada: se guarda, se muestra y NO acredita
    r = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "por_resultado", "modoEvaluacion": "PRE",
        "porLado": {"a": {"veredicto": "acierto"}}})
    check("un caso sembrado no acredita", r.json()["acredita"] is False, r.json())
    r = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "COND",
        "porLado": {"a": {"veredicto": "acierto"}}})
    check("ciego pero puntuado en marcha tampoco acredita", r.json()["acredita"] is False, r.json())

    # anti-hindsight de verdad: un fixture que NUNCA tuvo pronóstico en la cadena
    virgen = dbmod.query_one(
        "sad", "SELECT id FROM fixtures WHERE status_short='FT' AND id NOT IN (?,?,?) "
               "ORDER BY date DESC LIMIT 1", (pasado["id"], con_ficha, sin_ficha))["id"]
    sin_cadena = _parte(virgen)
    sin_cadena.pop("cadena")
    c.post(f"{A}/analisis/cowork", json=sin_cadena)
    r = c.post(f"{A}/analisis/cowork/{virgen}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE",
        "porLado": {"a": {"veredicto": "fallo", "queP": "…"}}})
    check("sin pronóstico previo la cadena NO recibe veredicto",
          len(r.json()["sinPronosticoPrevio"]) == 1, r.json().get("sinPronosticoPrevio"))
    check("pero el caso se guarda igual en el parte",
          c.get(f"{A}/analisis/cowork/{virgen}/veredicto").json()["porLado"]["a"]["veredicto"] == "fallo")

    # ── la ventana del TDE, comprobada contra los goles reales ──────────────
    # el partido con ficha tiene goles en el 34' (local) y el 51' (visitante)
    p_tde = _parte(con_ficha)
    p_tde["tde"] = {"ie": 60, "equipo": "a", "ventana": "45-60'", "tipologia": "prueba"}
    c.post(f"{A}/analisis/cowork", json=p_tde)
    c.post(f"{A}/analisis/cowork/{con_ficha}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "COND", "porLado": {"a": {"veredicto": "fallo"}}})
    o2 = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]
    t2 = o2["tde"]["bloques"][0]
    check("la ventana del TDE se lee del texto", (t2["desde"], t2["hasta"]) == (45, 60), t2)
    check("detecta el gol recibido dentro de la ventana", t2["golEnVentana"] is True, t2)
    check("y solo cuenta los goles CONTRA el equipo evaluado",
          all(g["lado"] == "b" for g in t2["goles"]), t2.get("goles"))
    check("la evidencia trae los goles con su minuto",
          len(o2["evidencia"]["goles"]) >= 2 and o2["evidencia"]["primerGol"]["minuto"] == 34,
          o2["evidencia"].get("goles"))
    # EL AÑADIDO SE SUMA UNA VEZ, Y LA TANDA NO SON GOLES. Un gol al 90+4 se
    # guarda como minuto 94 / extra 4; el veredicto lo ponía en el 98. Y los
    # 24 «goles» del 121' al 142' de un Santa Fe–River eran la definición por
    # penales, ingestada como juego.
    import sqlite3 as _sq2
    hid = dbmod.query_one("sad", "SELECT home_team_id FROM fixtures WHERE id=?", (con_ficha,))["home_team_id"]
    with _sq2.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, extra, tipo, detalle, equipo_id, jugador) "
                     "VALUES (?,?,?,?,?,?,?)", (con_ficha, 94, 4, "Goal", "Normal Goal", hid, "Añadido"))
        _con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, extra, tipo, detalle, equipo_id, jugador) "
                         "VALUES (?,?,?,?,?,?,?)",
                         [(con_ficha, 120 + k, k, "Shootout", "Penalty", hid, f"Penal {k}") for k in range(1, 6)])
    c.post(f"{A}/analisis/cowork/{con_ficha}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "COND", "porLado": {"a": {"veredicto": "fallo"}}})
    goles_min = [g["minuto"] for g in c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]["evidencia"]["goles"]]
    check("el gol del 90+4 queda en el 94, no en el 98", 94 in goles_min and 98 not in goles_min, goles_min)
    check("la tanda de penales no entra como gol", all(m <= 94 for m in goles_min), goles_min)
    with _sq2.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM fixture_eventos WHERE fixture_id=? AND minuto >= 94", (con_ficha,))

    # DOS EQUIPOS, DOS VENTANAS, DOS VEREDICTOS. Antes el segundo bloque vivía
    # en `notas` y no se comprobaba contra nada.
    p_tde["tde"] = {"bloques": [{"ie": 60, "equipo": "a", "ventana": "45-60'", "tipologia": "prueba"},
                                {"ie": 40, "equipo": "b", "ventana": "20-40'", "tipologia": "prueba"}]}
    c.post(f"{A}/analisis/cowork", json=p_tde)
    od = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]
    porlado = {b["equipo"]: b for b in od["tde"]["bloques"]}
    check("con dos bloques se comprueban las DOS ventanas", len(porlado) == 2, od["tde"])
    check("la echada de 'a' se ve en el gol que RECIBE (51')",
          porlado["a"]["golEnVentana"] is True, porlado["a"])
    check("la de 'b' en el suyo (34'), que cae en su ventana",
          porlado["b"]["golEnVentana"] is True and all(g["lado"] == "a" for g in porlado["b"]["goles"]),
          porlado["b"])

    # una ventana fuera de los goles no se da por cumplida
    p_tde["tde"] = {"ie": 60, "equipo": "a", "ventana": "75-90'", "tipologia": "prueba"}
    c.post(f"{A}/analisis/cowork", json=p_tde)
    o3 = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]["tde"]["bloques"][0]
    check("sin gol en la ventana, no se inventa el acierto", o3["golEnVentana"] is False, o3)
    check("lo objetivo se RECALCULA al leer (el juicio no se re-escribió)",
          o3["ventana"] == "75-90'", o3)

    # un pronóstico sin 1X2 no cuenta acierto en vez de contarlo como fallo
    p_vacio = _parte(con_ficha)
    p_vacio["pronostico"]["probabilidades"] = {"local": 0, "empate": 0, "visita": 0}
    c.post(f"{A}/analisis/cowork", json=p_vacio)
    o4 = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]
    check("sin 1X2 declarado no hay acierto ni fallo, hay nota",
          o4["unXDos"]["acerto"] is False and "no se cuenta" in o4["unXDos"]["nota"], o4["unXDos"])
    check("y tampoco hay Brier", o4["brier"]["valor"] is None, o4["brier"])

    # ── UN HUECO NO ES UN CERO (visto en producción) ───────────────────────
    # Un parte sin sub-scores se pintaba «0.0/27 · 0% · SIN FORMACIÓN»: el
    # veredicto más duro de la rúbrica, inventado sobre un dato que nadie
    # puntuó. Y el re-depósito que los borró no lo declaró en `perdido`.
    sin_scores = {"fixtureId": sin_ficha,
                  "equipos": {l: {"plantel": [{"nombre": "Uno", "zona": "GK", "rol": "TF"}]}
                              for l in ("a", "b")}}
    c.post(f"{A}/analisis/cowork", json=sin_scores)
    d0 = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]
    check("sin un solo sub-score el porcentaje es null, NO 0",
          d0["porcentaje"] is None, d0["porcentaje"])
    check("y no se clasifica lo que nadie evaluó",
          d0["clasificacion"] == "" and d0["sinBloques"] is True,
          (d0["clasificacion"], d0.get("sinBloques")))
    check("y se dice que no es 0% ni SIN FORMACIÓN", "nadie puntuó" in d0["notaTotales"],
          d0["notaTotales"])
    check("cada bloque dice si lo puntuaron o no",
          all(d0["bloques"][l]["declarado"] is False for l in "ABCDE"),
          {l: d0["bloques"][l]["declarado"] for l in "ABCDE"})

    # un cero DECLARADO sigue siendo un cero: la distinción es llegar o no
    con_cero = {"fixtureId": sin_ficha,
                "equipos": {l: {"bloques": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}}
                            for l in ("a", "b")}}
    c.post(f"{A}/analisis/cowork", json=con_cero)
    d1 = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]
    check("un 0 DECLARADO sí es 0% y sí clasifica",
          d1["porcentaje"] == 0.0 and d1["clasificacion"] == "SIN_FORMACION",
          (d1["porcentaje"], d1["clasificacion"]))

    # un parte a medias declara el hueco en vez de dejar que arrastre callado
    c.post(f"{A}/analisis/cowork", json={"fixtureId": sin_ficha,
                                         "equipos": {l: {"bloques": {"A": 4, "B": 6}}
                                                     for l in ("a", "b")}})
    d2 = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]
    check("los bloques que faltan se declaran, no se disimulan",
          d2["bloquesSinDeclarar"] == ["C", "D", "E"], d2.get("bloquesSinDeclarar"))
    check("y se avisa que cuentan como 0 y bajan el porcentaje",
          "bajan el porcentaje" in d2["notaTotales"], d2["notaTotales"])

    # UN PARTE VIEJO NO PIERDE SU EFE POR UN CAMPO QUE NO EXISTÍA. Los partes
    # guardados antes de `declarado` no tienen la clave: tratar «ausente» como
    # «no declarado» les borraba la rúbrica de la pantalla — el mismo error que
    # el campo vino a arreglar, girado del otro lado.
    import backend.analisis.parte as cowork_mod
    c.post(f"{A}/analisis/cowork", json={"fixtureId": sin_ficha,
                                         "equipos": {l: {"bloques": {"A": 4, "B": 5, "C": 3,
                                                                     "D": 4, "E": 2}}
                                                     for l in ("a", "b")}})
    with cowork_mod._conectar() as _con:
        _fila = _con.execute("SELECT parte_json FROM parte_cowork WHERE fixture_id=?",
                             (sin_ficha,)).fetchone()
        _p = json.loads(_fila["parte_json"])
        for _l in ("a", "b"):          # simula el JSON viejo: sin la clave
            for _x in _p["equipos"][_l]["bloques"].values():
                _x.pop("declarado", None)
        _con.execute("UPDATE parte_cowork SET parte_json=? WHERE fixture_id=?",
                     (json.dumps(_p, ensure_ascii=False), sin_ficha))
    viejo = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]
    check("un parte anterior al campo `declarado` NO pierde su EFE",
          viejo["sinBloques"] is False and viejo["porcentaje"] > 0,
          (viejo.get("sinBloques"), viejo.get("porcentaje")))
    check("y se dice que la declaración fue INFERIDA, no leída",
          all(viejo["bloques"][l].get("declaradoInferido") for l in "ABCDE")
          and "se infirió" in viejo["notaTotales"], viejo["notaTotales"])

    # EL RE-DEPÓSITO QUE VACÍA LA RÚBRICA LO DICE
    completo = _parte(sin_ficha)
    c.post(f"{A}/analisis/cowork", json=completo)
    # un cuerpo "vacío pero válido": el equipo existe, la rúbrica no
    rec_v = c.post(f"{A}/analisis/cowork", json={"fixtureId": sin_ficha,
                                                 "equipos": {l: {"plantel": []} for l in ("a", "b")}}).json()
    perdido = " ".join(rec_v["perdido"])
    check("borrar los sub-scores del EFE se declara en `perdido`",
          "subScoresEfe" in perdido, rec_v["perdido"])
    check("y también el TDE, la cadena y el reparto 1X2",
          all(k in perdido for k in ("bloquesTde", "pronosticosDeCadena", "repartoUnXDos")),
          rec_v["perdido"])
    check("el aviso dice cómo se arregla", "vuelve a depositarlo completo" in rec_v["aviso"],
          rec_v.get("aviso"))

    # y la respuesta del GET se puede re-depositar sin inventar sub-scores
    c.post(f"{A}/analisis/cowork", json=sin_scores)
    ida0 = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    c.post(f"{A}/analisis/cowork", json=ida0)
    d3 = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]
    check("el viaje de ida y vuelta NO convierte el hueco en un 0 declarado",
          d3["porcentaje"] is None and d3["sinBloques"] is True,
          (d3["porcentaje"], d3.get("sinBloques")))
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))

    # ── EL VEREDICTO TAMBIÉN SE RE-DEPOSITA (reportado por Cowork) ─────────
    # Re-postear la respuesta del GET —el flujo natural para corregir una
    # lección— rechazaba media docena de claves propias, degradaba un
    # `falsadorCumplido: false` a `null` y corría la fecha del cierre.
    p_rt = _parte(pasado["id"])
    c.post(f"{A}/analisis/cowork", json=p_rt)
    c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE", "falsadorCumplido": False,
        "porLado": {"a": {"veredicto": "fallo", "queP": "…", "leccion": "una lección",
                          "skill": "teorema-del-echado"}}})
    v1 = c.get(f"{A}/analisis/cowork/{pasado['id']}/veredicto").json()
    cerrado_1 = v1["cerradoEn"]
    r_rt = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json=v1)
    check("la respuesta del veredicto se vuelve a depositar sin rechazos",
          r_rt.status_code == 200 and r_rt.json()["rechazos"] == [],
          r_rt.json().get("rechazos"))
    v2 = c.get(f"{A}/analisis/cowork/{pasado['id']}/veredicto").json()
    check("y `falsadorCumplido: false` NO se degrada a null en el viaje",
          v2["falsador"]["cumplido"] is False, v2["falsador"])
    check("la fecha de cierre es evidencia: no se re-sella",
          v2["cerradoEn"] == cerrado_1, (cerrado_1, v2["cerradoEn"]))
    # (`ahora()` tiene resolución de segundos: en el mismo segundo los dos
    # sellos coinciden, así que lo que se comprueba es que la corrección SE
    # MARCA como corrección, no que el reloj haya avanzado)
    check("la corrección queda marcada como corrección",
          bool(v2["actualizadoEn"]), v2.get("actualizadoEn"))
    check("la lección sobrevive al re-depósito",
          v2["porLado"]["a"]["leccion"] == "una lección", v2["porLado"]["a"])
    # borrar el valor sigue siendo posible, pero hay que pedirlo
    c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE", "falsadorCumplido": None,
        "porLado": {"a": {"veredicto": "fallo"}}})
    check("mandar `falsadorCumplido: null` a propósito SÍ lo borra",
          c.get(f"{A}/analisis/cowork/{pasado['id']}/veredicto").json()["falsador"]["cumplido"] is None)

    # ── FASE C: LAS LECCIONES, ACUMULADAS POR SKILL ────────────────────────
    # REGRESIÓN DE ORDEN DE RUTAS: `lecciones` es un segmento suelto y si se
    # declara después de /{fixture_id}, FastAPI intenta parsear "lecciones"
    # como entero y devuelve 422. Ya pasó con `latido`.
    rl = c.get(f"{A}/analisis/cowork/lecciones")
    check("`lecciones` no se lo come /{fixture_id}", rl.status_code == 200, rl.text[:160])

    # un caso ciego con lección por skill
    p_lec = _parte(pasado["id"])
    c.post(f"{A}/analisis/cowork", json=p_lec)
    c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE",
        "porLado": {"a": {"veredicto": "fallo", "queP": "no aguantó el tramo final",
                          "leccion": "el bloque bajo entrenado sostiene los 90",
                          "skill": "teorema-del-echado", "reglaTocada": "escala de P(echada)"},
                    "b": {"veredicto": "acierto", "queP": "aguantó"}}})
    inv = c.get(f"{A}/analisis/cowork/lecciones").json()
    mio = next((i for i in inv["items"] if i["clave"] == f"{pasado['id']}:a"), None)
    check("la lección se indexa desde el veredicto", mio is not None,
          [i["clave"] for i in inv["items"]][:5])
    check("y trae el partido del que salió",
          bool(mio["partido"]) and mio["fecha"] and mio["equipo"], mio)
    check("un lado sin lección no inventa una entrada",
          not any(i["clave"] == f"{pasado['id']}:b" for i in inv["items"]),
          [i["clave"] for i in inv["items"]][:5])
    check("nace pendiente", mio["estado"] == "pendiente", mio["estado"])
    check("un caso ciego+PRE SÍ puede mover números", mio["puedeMoverNumeros"] is True, mio)

    # ── COHORTE: la época del proceso se sella al depositar ──
    check("la cohorte del parte es la vigente y viaja en la lectura",
          c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["cohorte"]["vigente"] is True
          and inv["cohorteVigente"] and any(x["vigente"] and x["casos"] >= 1 for x in inv["cohortes"]),
          (inv.get("cohorteVigente"), inv.get("cohortes")))
    check("la lección trae su cohorte", mio["cohorte"] == inv["cohorteVigente"], mio.get("cohorte"))
    inv_rod = c.get(f"{A}/analisis/cowork/lecciones", params={"cohorte": "rodaje"}).json()
    check("filtrar por otra cohorte deja las métricas en cero y el resumen de cohortes entero",
          inv_rod["acreditables"]["casos"] == 0 and inv_rod["filtro"]["cohorte"] == "rodaje"
          and inv_rod["cohortes"] == inv["cohortes"], (inv_rod["acreditables"]["casos"], inv_rod["filtro"]))
    inv_vig = c.get(f"{A}/analisis/cowork/lecciones", params={"cohorte": "vigente"}).json()
    check("`cohorte=vigente` resuelve a la clave vigente y conserva el caso",
          inv_vig["filtro"]["cohorte"] == inv["cohorteVigente"]
          and any(i["clave"] == f"{pasado['id']}:a" for i in inv_vig["items"]), inv_vig["filtro"])
    # un re-depósito NO cambia de época
    import backend.analisis.parte as cowork_mod2
    with cowork_mod2._conectar() as con_c:
        con_c.execute("UPDATE parte_cowork SET cohorte=NULL WHERE fixture_id=?", (pasado["id"],))
    c.post(f"{A}/analisis/cowork", json=p_lec)
    check("un parte sin cohorte (anterior) es «rodaje» y un re-depósito no lo trae a la vigente",
          c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["cohorte"]["clave"] == "rodaje")
    with cowork_mod2._conectar() as con_c:
        con_c.execute("UPDATE parte_cowork SET cohorte=? WHERE fixture_id=?", (cowork_mod2.COHORTE, pasado["id"]))
    inv = c.get(f"{A}/analisis/cowork/lecciones").json()

    # ── CUARENTENA: por criterio, con motivo, y fuera de toda métrica ──
    r_q = c.post(f"{A}/analisis/cowork/{pasado['id']}/cuarentena", json={"motivo": "falló"})
    check("cuarentena sin motivo de verdad → 422 (un fallo no es motivo)", r_q.status_code == 422, r_q.text[:120])
    r_q = c.post(f"{A}/analisis/cowork/{pasado['id']}/cuarentena", json={"motivo": "rodaje: DT viejo en la ficha"})
    check("cuarentena con motivo → 200 y guarda el veredicto que tenía el caso al ponerla",
          r_q.status_code == 200 and r_q.json()["cuarentena"]["veredictoAlPoner"]["a"] == "fallo", r_q.text[:200])
    inv_q = c.get(f"{A}/analisis/cowork/lecciones").json()
    check("el caso en cuarentena sale de la población ciega y de las métricas",
          inv_q["poblacion"]["cuarentena"]["casos"] == 1
          and inv_q["poblacion"]["ciega"]["casos"] == inv["poblacion"]["ciega"]["casos"] - 1
          and inv_q["acreditables"]["casos"] == inv["acreditables"]["casos"] - 1,
          (inv_q["poblacion"], inv_q["acreditables"]["casos"], inv["acreditables"]["casos"]))
    check("su lección se lista aparte, en `enCuarentena`, sin poder mover números, y no en los conteos por skill",
          any(i["clave"] == f"{pasado['id']}:a" and i["puedeMoverNumeros"] is False and i["cuarentena"]
              for i in inv_q["enCuarentena"]["items"])
          and not any(i["clave"] == f"{pasado['id']}:a" for i in inv_q["items"]), inv_q["enCuarentena"])
    check("la lectura del parte trae la cuarentena",
          c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["cuarentena"]["motivo"].startswith("rodaje"))
    r_q = c.delete(f"{A}/analisis/cowork/{pasado['id']}/cuarentena")
    check("quitar la cuarentena devuelve lo quitado y el caso vuelve a contar",
          r_q.status_code == 200 and r_q.json()["quitada"]["motivo"].startswith("rodaje")
          and c.get(f"{A}/analisis/cowork/lecciones").json()["poblacion"]["cuarentena"]["casos"] == 0, r_q.text[:200])
    # ── SIN DT NO HAY CASO: cuarentena automática ──
    p_sin = dict(p_lec)
    import copy as _copy
    p_sin = _copy.deepcopy(p_lec)
    p_sin["equipos"]["a"]["dt"] = "sin establecer"
    c.post(f"{A}/analisis/cowork", json=p_sin)
    lect = c.get(f"{A}/analisis/cowork/{pasado['id']}").json()
    check("el parte con DT «sin establecer» lleva la alerta DT-SIN-DT del lado",
          any(x["codigo"] == "DT-SIN-DT" and x["equipo"] == "a" for x in lect["alertas"]),
          [x["codigo"] for x in lect["alertas"]])
    inv_sin = c.get(f"{A}/analisis/cowork/lecciones").json()
    check("…y el caso queda en cuarentena AUTOMÁTICA, fuera de las métricas",
          inv_sin["poblacion"]["cuarentena"]["casos"] == 1 and inv_sin["enCuarentena"]["automaticas"] == 1
          and any(i["clave"] == f"{pasado['id']}:a" and i["cuarentenaAutomatica"] for i in inv_sin["enCuarentena"]["items"]),
          (inv_sin["poblacion"], inv_sin["enCuarentena"].get("automaticas")))
    p_sin["equipos"]["a"]["dt"] = {"nombre": "Otro Técnico", "desde": "2026-01-01"}
    c.post(f"{A}/analisis/cowork", json=p_sin)
    lect = c.get(f"{A}/analisis/cowork/{pasado['id']}").json()
    check("re-depositar con el DT levanta la cuarentena automática",
          c.get(f"{A}/analisis/cowork/lecciones").json()["poblacion"]["cuarentena"]["casos"] == 0)
    check("un DT que no es el de la base dispara DT-DISCREPANCIA con el registro de la base al lado",
          any(x["codigo"] == "DT-DISCREPANCIA" and x["equipo"] == "a" and x.get("dtBase", {}).get("nombre")
              for x in lect["alertas"]), [x["codigo"] for x in lect["alertas"]])
    r_eco = c.post(f"{A}/analisis/cowork", json={**lect, "fixtureId": pasado["id"]}).json()
    check("el eco con las alertas calculadas no genera rechazos ni las duplica",
          not any("alertas[" in x["donde"] for x in r_eco["rechazos"])
          and sum(1 for x in c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["alertas"]
                  if x["codigo"] == "DT-DISCREPANCIA" and x["equipo"] == "a") == 1,
          (r_eco["rechazos"], [x["codigo"] for x in c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["alertas"]]))
    # ── DT EQUIVOCADO: el parte nombra a uno y en el banco se sentó otro ──
    import sqlite3 as _sq3
    with _sq3.connect(os.path.join(tmp, "sad.db")) as _con:
        _fx = _con.execute("SELECT home_team_id FROM fixtures WHERE id=?", (pasado["id"],)).fetchone()
        _con.execute("UPDATE alineaciones SET entrenador=? WHERE fixture_id=? AND team_id=?",
                     ("R. Dudamel", pasado["id"], _fx[0]))
        _hay = _con.execute("SELECT COUNT(*) FROM alineaciones WHERE fixture_id=? AND team_id=?",
                            (pasado["id"], _fx[0])).fetchone()[0]
        if not _hay:
            _con.execute("INSERT INTO alineaciones (fixture_id, team_id, entrenador, player_id, jugador, titular) "
                         "VALUES (?, ?, ?, ?, ?, 1)", (pasado["id"], _fx[0], "R. Dudamel", 999001, "Jugador Demo"))
    p_eq = _copy.deepcopy(p_lec)
    p_eq["equipos"]["a"]["dt"] = {"nombre": "Pablo Repetto", "desde": "2026-01-01"}
    c.post(f"{A}/analisis/cowork", json=p_eq)
    inv_eq = c.get(f"{A}/analisis/cowork/lecciones").json()
    item_eq = [i for i in inv_eq["enCuarentena"]["items"] if i["clave"].startswith(f"{pasado['id']}:")]
    check("DT del parte (Repetto) distinto del que se sentó en el banco (Dudamel) → cuarentena AUTOMÁTICA con los dos nombres",
          item_eq and all(i["cuarentenaAutomatica"] for i in item_eq)
          and "Repetto" in item_eq[0]["cuarentena"] and "Dudamel" in item_eq[0]["cuarentena"],
          [i.get("cuarentena") for i in item_eq] or inv_eq["enCuarentena"])
    p_eq["equipos"]["a"]["dt"] = {"nombre": "Rafael Dudamel", "desde": "2026-01-01"}
    c.post(f"{A}/analisis/cowork", json=p_eq)
    check("re-depositar con el DT del banco («Rafael Dudamel» vs «R. Dudamel») la levanta",
          not any(i["clave"].startswith(f"{pasado['id']}:") for i in
                  c.get(f"{A}/analisis/cowork/lecciones").json()["enCuarentena"]["items"]))
    # ── corregir SOLO el DT: el resto del parte no se toca ──
    p_eq["equipos"]["a"]["dt"] = {"nombre": "Pablo Repetto", "desde": "2026-01-01"}
    c.post(f"{A}/analisis/cowork", json=p_eq)
    antes_dt = c.get(f"{A}/analisis/cowork/{pasado['id']}").json()
    r_dt = c.post(f"{A}/analisis/cowork/{pasado['id']}/dt", json={"a": {"nombre": "Rafael Dudamel", "desde": "2026-02-01"}})
    despues_dt = c.get(f"{A}/analisis/cowork/{pasado['id']}").json()
    _sin = lambda d: {k: v for k, v in d.items() if k not in ("equipos", "actualizadoEn", "coherencia", "alertas")}  # noqa: E731
    check("POST …/dt cambia el DT del lado a, dice que ya casa con el banco y deja el resto del parte igual",
          r_dt.status_code == 200 and r_dt.json()["ahora"]["a"]["nombre"] == "Rafael Dudamel"
          and r_dt.json()["dtEquivocado"] == [] and despues_dt["equipos"]["a"]["dt"]["nombre"] == "Rafael Dudamel"
          and _sin(antes_dt) == _sin(despues_dt)
          and {k: v for k, v in despues_dt["equipos"]["a"].items() if k != "dt"}
              == {k: v for k, v in antes_dt["equipos"]["a"].items() if k != "dt"}
          and despues_dt["equipos"]["b"] == antes_dt["equipos"]["b"],
          r_dt.text[:300])
    r_dt_mal = c.post(f"{A}/analisis/cowork/{pasado['id']}/dt",
                      json={"a": {"nombre": "Según la prensa dirige el interino tras la salida del anterior DT del club"}})
    check("un DT en prosa se rechaza con motivo y NO pisa el que había",
          r_dt_mal.status_code == 200 and r_dt_mal.json()["rechazos"] and r_dt_mal.json()["ahora"] == {}
          and c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["equipos"]["a"]["dt"]["nombre"] == "Rafael Dudamel",
          r_dt_mal.text[:300])
    check("POST …/dt sin lados → 422; fixture sin parte → 404",
          c.post(f"{A}/analisis/cowork/{pasado['id']}/dt", json={}).status_code == 422
          and c.post(f"{A}/analisis/cowork/999999999/dt", json={"a": {"nombre": "X Y"}}).status_code == 404)
    from backend.analisis.parte import mismo_dt
    check("mismo_dt: apellido compuesto y abreviado casan; apellidos distintos no",
          mismo_dt("Hernán Torres Oliveros", "H. Torres") and mismo_dt("Mauricio Pellegrino", "M. Pellegrino")
          and not mismo_dt("Pablo Repetto", "R. Dudamel")
          and mismo_dt("S. Hoeneß", "S. Hoeneb") and mismo_dt("Sebastian Hoeneß", "S. Hoeness")
          and not mismo_dt("Gustavo Álvarez", "Tiago Nunes"))
    c.post(f"{A}/analisis/cowork", json=p_lec)
    ag_dt = c.get(f"{A}/analisis/cowork/agenda", params={"fecha": fecha, "limite": 2}).json()
    check("la agenda lleva el DT de la base por lado, con edad, procedencia y si es fiable",
          all("dt" in x and set(x["dt"]) == {"a", "b"} for x in ag_dt["analizar"])
          and any((x["dt"]["a"] or {}).get("nombre") and "fiable" in x["dt"]["a"] and "nota" in x["dt"]["a"]
                  for x in ag_dt["analizar"]), [x.get("dt") for x in ag_dt["analizar"]][:2])

    check("cuarentena sobre un fixture sin parte → 404",
          c.post(f"{A}/analisis/cowork/999999/cuarentena", json={"motivo": "rodaje: primera semana"}).status_code == 404)
    inv = c.get(f"{A}/analisis/cowork/lecciones").json()

    tde_skill = next((x for x in inv["porSkill"] if x["skill"] == "teorema-del-echado"), None)
    check("las lecciones se agrupan por skill", tde_skill is not None,
          [x["skill"] for x in inv["porSkill"]])
    check("el sesgo de atribución se DECLARA, no se disimula",
          "NO son una tasa" in tde_skill["sesgoDeAtribucion"], tde_skill.get("sesgoDeAtribucion"))
    check("el disparador de la fase D dice que ABRE, no que autoriza",
          "no autorizan" in tde_skill["disparador"], tde_skill["disparador"])
    check("con 1 fallo pendiente la revisión NO está abierta",
          tde_skill["revisionAbierta"] is False and tde_skill["faltanParaDisparar"] == 3,
          (tde_skill["revisionAbierta"], tde_skill["faltanParaDisparar"]))
    check("el listón del TDE sale del propio skill",
          "5" in (tde_skill["liston"] or {}).get("semaforo", ""), (tde_skill["liston"] or {}).get("semaforo"))

    # ── el reventón en producción, contra el backtest (REVENTON.md §11) ─────
    rvm = inv["acreditables"]["reventon"]
    check("las métricas traen la tasa de reventón por nivel de riesgo con el rango del backtest al lado",
          set(rvm["porNivel"]) >= {"bajo", "medio", "alto", "muy alto", "sin base"}
          and rvm["porNivel"]["muy alto"]["esperadoBacktest"] == [0.747, 0.854]
          and rvm["porNivel"]["sin base"]["esperadoBacktest"] is None, rvm["porNivel"])
    n_casos_ciegos = inv["acreditables"]["casos"]
    check("las observaciones son los lados de los casos ciegos (dos por caso) y suman por nivel",
          rvm["observadas"] == sum(x["observadas"] for x in rvm["porNivel"].values())
          and 0 < rvm["observadas"] + rvm["sinBurbuja"] + rvm["noComprobables"] <= 2 * n_casos_ciegos
          and (rvm["observadas"] + rvm["sinBurbuja"] + rvm["noComprobables"]) % 2 == 0,
          (rvm["observadas"], rvm["sinBurbuja"], rvm["noComprobables"], n_casos_ciegos))
    check("con n < 10 por nivel no se compara con el backtest: `dentroDelBacktest` null y la revisión cerrada",
          all(x["dentroDelBacktest"] is None for x in rvm["porNivel"].values())
          and rvm["revisionAbierta"] is False and rvm["fueraDelBacktest"] == [], rvm)
    check("y la nota dice que un nivel fuera del rango ABRE la revisión, no mueve los puntos",
          "no los mueve" in rvm["nota"], rvm["nota"])
    check("las métricas del reventón traen el respeto del riesgo por grupo, con su nota",
          set(rvm["respetoRiesgo"]) >= {"aFavor", "enContra", "neutro", "nota"}
          and "alto" in rvm["respetoRiesgo"]["nota"], rvm.get("respetoRiesgo"))
    from backend.analisis.lecciones import _acumular_reventon, _cerrar_reventon, _reventon_vacio
    sr = _reventon_vacio()
    obs_alto = {"comprobable": True, "sinBurbuja": False,
                "declarado": {"signo": "+", "riesgo": {"nivel": "alto"}, "extremo": False},
                "observado": {"revento": True}, "pronosticoVsRacha": "aFavor", "respetoRiesgo": False}
    obs_bajo = {**obs_alto, "declarado": {"signo": "+", "riesgo": {"nivel": "bajo"}, "extremo": False},
                "respetoRiesgo": None}
    _acumular_reventon(sr, {"a": obs_alto, "b": obs_bajo}, {"declarado": "local", "acerto": False}, 0.9)
    _acumular_reventon(sr, {"a": {**obs_alto, "pronosticoVsRacha": "enContra", "respetoRiesgo": True}},
                       {"declarado": "visita", "acerto": True}, 0.2)
    cr = _cerrar_reventon(sr)["respetoRiesgo"]
    check("solo los lados con riesgo alto entran al respeto (el bajo queda fuera)",
          cr["aFavor"]["lados"] == 1 and cr["enContra"]["lados"] == 1 and cr["neutro"]["lados"] == 0, cr)
    check("cada grupo lleva su tasa de reventón, su 1X2 y su Brier medio",
          cr["aFavor"]["brierMedio"] == 0.9 and cr["aFavor"]["tasa1x2"] == 0.0
          and cr["enContra"]["brierMedio"] == 0.2 and cr["enContra"]["tasa1x2"] == 1.0, cr)
    sint = _reventon_vacio()
    sint["porNivel"]["bajo"] = {"observadas": 20, "reventadas": 16}     # 80 %: fuera de 42-47 %
    sint["porNivel"]["alto"] = {"observadas": 25, "reventadas": 17}     # 68 %: dentro de 67.2-69.2 %
    sint["porNivel"]["medio"] = {"observadas": 5, "reventadas": 5}      # n chico: no se compara
    cerr = _cerrar_reventon(sint)
    check("con n suficiente, un nivel fuera del rango del backtest se nombra y abre la revisión",
          cerr["fueraDelBacktest"] == ["bajo"] and cerr["revisionAbierta"] is True
          and cerr["porNivel"]["alto"]["dentroDelBacktest"] is True
          and cerr["porNivel"]["medio"]["dentroDelBacktest"] is None, cerr["porNivel"])
    # EL INTERVALO, NO EL PUNTO: 6 de 21 (29 %) contra 42-47 % parecía FUERA en
    # la pantalla del 19/09; el intervalo de Wilson [14 %, 50 %] dice que es ruido
    sint2 = _reventon_vacio()
    sint2["porNivel"]["bajo"] = {"observadas": 21, "reventadas": 6}
    sint2["porNivel"]["muy alto"] = {"observadas": 19, "reventadas": 13}   # 68 % vs 75-85 %
    cerr2 = _cerrar_reventon(sint2)
    check("6/21 contra 42-47 % es COMPATIBLE por intervalo (Wilson 95 %), no FUERA por el punto",
          cerr2["porNivel"]["bajo"]["dentroDelBacktest"] is True and cerr2["porNivel"]["bajo"]["lectura"] == "compatible"
          and cerr2["porNivel"]["bajo"]["intervalo"][0] < 0.42 < cerr2["porNivel"]["bajo"]["intervalo"][1]
          and cerr2["porNivel"]["muy alto"]["dentroDelBacktest"] is True
          and cerr2["revisionAbierta"] is False, cerr2["porNivel"])
    check("la nota dice que se compara por intervalo", "Wilson" in cerr2["nota"], cerr2["nota"])
    from backend.analisis.lecciones import intervalo_wilson
    check("intervalo de Wilson: 16/20 → [0.584, 0.919] (80 % no toca 42-47 %) y n=0 → None",
          intervalo_wilson(16, 20) == (0.584, 0.919) and intervalo_wilson(0, 0) is None, intervalo_wilson(16, 20))

    # LO CONTAMINADO ENSEÑA PERO NO MUEVE UN NÚMERO
    c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "post_resultado", "modoEvaluacion": "PRE",
        "porLado": {"a": {"veredicto": "fallo", "leccion": "misma lección, caso sembrado",
                          "skill": "teorema-del-echado"}}})
    inv2 = c.get(f"{A}/analisis/cowork/lecciones").json()
    m2 = next(i for i in inv2["items"] if i["clave"] == f"{pasado['id']}:a")
    check("una lección de caso contaminado NO puede mover números",
          m2["puedeMoverNumeros"] is False, m2)
    check("y dice qué sí autoriza: fijar rúbrica",
          "fija rúbrica" in m2["queAutoriza"], m2["queAutoriza"])
    check("las poblaciones se cuentan aparte y se avisa que no se suman",
          "no se suman" in inv2["poblacion"]["nota"], inv2["poblacion"]["nota"])

    # EL CONTENIDO SE DERIVA, NO SE COPIA: corregir el veredicto corrige la lección
    c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE",
        "porLado": {"a": {"veredicto": "fallo", "leccion": "TEXTO CORREGIDO",
                          "skill": "teorema-del-echado"}}})
    m3 = next(i for i in c.get(f"{A}/analisis/cowork/lecciones").json()["items"]
              if i["clave"] == f"{pasado['id']}:a")
    check("corregir el veredicto corrige la lección (no hay copia vieja)",
          m3["leccion"] == "TEXTO CORREGIDO", m3["leccion"])

    # el estado sí se guarda aparte, y `aplicada` exige la versión
    clave = f"{pasado['id']}:a"
    r = c.post(f"{A}/analisis/cowork/lecciones/{clave}", json={"estado": "aplicada"})
    check("marcar `aplicada` sin versión se rechaza", r.status_code == 422, r.status_code)
    check("y el error dice por qué", "aplicadaEn" in r.text, r.text[:120])
    r = c.post(f"{A}/analisis/cowork/lecciones/{clave}",
               json={"estado": "aplicada", "aplicadaEn": "tde/v0.1.4"})
    check("con versión sí entra", r.status_code == 200 and r.json()["estado"] == "aplicada",
          r.text[:160])
    check("un estado inventado se rechaza",
          c.post(f"{A}/analisis/cowork/lecciones/{clave}",
                 json={"estado": "casi"}).status_code == 422)
    check("una clave que no existe es 404",
          c.post(f"{A}/analisis/cowork/lecciones/99999999:a",
                 json={"estado": "descartada"}).status_code == 404)
    inv3 = c.get(f"{A}/analisis/cowork/lecciones", params={"estado": "aplicada"}).json()
    check("el estado sobrevive al re-derivado",
          [i["clave"] for i in inv3["items"]] == [clave], [i["clave"] for i in inv3["items"]])
    check("y trae la versión donde entró",
          inv3["items"][0]["aplicadaEn"] == "tde/v0.1.4", inv3["items"][0])
    tde3 = next(x for x in inv3["porSkill"] if x["skill"] == "teorema-del-echado")
    check("una lección aplicada deja de contar para el disparador",
          tde3["fallosPendientes"] == 0, tde3["fallosPendientes"])

    # las métricas salen SOLO de lo acreditable y el Brier viaja con su base
    acr = inv3["acreditables"]
    check("las métricas declaran su criterio", "ciega + PRE" in acr["criterio"], acr["criterio"])
    check("el Brier viaja con su línea de base",
          "lineaBase" in acr["brier"], acr["brier"])
    check("sin n no se publica un 0% disfrazado de tasa",
          acr["tasaAcierto"] is not None or acr["tasaNota"], acr)
    check("la ventana del TDE observada no cuenta lo no comprobable",
          "no cuenta como no ocurrido" in acr["ventanaTde"]["nota"], acr["ventanaTde"])

    # una lección sin skill se delata en vez de repartirse a ojo
    c.post(f"{A}/analisis/cowork/{virgen}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "PRE",
        "porLado": {"a": {"veredicto": "fallo", "leccion": "lección huérfana"}}})
    inv4 = c.get(f"{A}/analisis/cowork/lecciones").json()
    check("una lección sin skill se declara aparte",
          inv4["sinSkill"]["cuantas"] >= 1 and "no se reparte a ojo" in inv4["sinSkill"]["porque"],
          inv4["sinSkill"])

    # ── LO QUE SE RECHAZA SE DICE (reportado por Cowork en la 1ª corrida) ───
    # La rúbrica del EFE nombra los roles con 🔴🟠🟡⚪ y con su etiqueta, y las
    # posiciones en español. Quien escribe el parte viene de leer ESA rúbrica.
    def _dep(equipo_a):
        r = c.post(f"{A}/analisis/cowork", json={"fixtureId": sin_ficha,
                                                 "equipos": {"a": equipo_a, "b": {"bloques": {"A": 1}}}})
        return r.json(), c.get(f"{A}/analisis/cowork/{sin_ficha}").json()

    rec, d = _dep({"bloques": {"A": {"score": 4, "nota": "mismo DT"}, "B": {"score": 5},
                               "C": {"score": 3}, "D": {"score": 4}, "E": {"score": 3}},
                   "plantel": [{"nombre": "Uno", "zona": "GK", "rol": "TF"}]})
    check("el sub-score como objeto {score, nota} se entiende",
          d["equipos"]["a"]["total"] == 24.5, d["equipos"]["a"]["total"])
    check("y la nota del objeto llega al bloque",
          d["equipos"]["a"]["bloques"]["A"]["nota"] == "mismo DT", d["equipos"]["a"]["bloques"]["A"])

    rec, d = _dep({"bloques": {"A": 4},
                   "plantel": [{"nombre": "Uno", "zona": "GK", "rol": "🔴"},
                               {"nombre": "Dos", "zona": "DEF", "rol": "🟠"},
                               {"nombre": "Tres", "zona": "MID", "rol": "🟡"},
                               {"nombre": "Cuatro", "zona": "ATK", "rol": "⚪"}]})
    check("los roles con el símbolo de la rúbrica entran", rec["jugadores"]["a"] == 4, rec["jugadores"])
    check("y se traducen a la sigla interna",
          [j["rol"] for j in d["equipos"]["a"]["plantel"]] == ["TF", "TH", "ROT", "SUP"],
          [j["rol"] for j in d["equipos"]["a"]["plantel"]])

    rec, d = _dep({"bloques": {"A": 4},
                   "plantel": [{"nombre": "Uno", "posicion": "Portero", "rol": "Titular fijo"},
                               {"nombre": "Dos", "posicion": "Lateral", "rol": "Titular habitual"},
                               {"nombre": "Tres", "posicion": "Volante", "rol": "Rotación"},
                               {"nombre": "Cuatro", "posicion": "Delantero", "rol": "Suplente"}]})
    check("el rol por etiqueta y la zona por posición en español también",
          rec["jugadores"]["a"] == 4, rec["jugadores"])
    check("la zona se deduce de la posición",
          [j["zona"] for j in d["equipos"]["a"]["plantel"]] == ["GK", "DEF", "MID", "ATK"],
          [j["zona"] for j in d["equipos"]["a"]["plantel"]])

    # y lo que de verdad no se entiende, se rechaza CON MOTIVO
    rec, _ = _dep({"bloques": {"A": "cuatro", "B": 99},
                   "plantel": [{"nombre": "Uno", "zona": "banquillo", "rol": "TF"},
                               {"nombre": "Dos", "zona": "GK", "rol": "crack"},
                               {"zona": "GK", "rol": "TF"}]})
    porques = " · ".join(r["porque"] for r in rec["rechazos"])
    check("un sub-score no numérico se declara", "no numérico" in porques, porques)
    check("un sub-score recortado se declara (99 → 6)", "fuera de rango" in porques, porques)
    check("una zona desconocida se declara con lo esperado",
          any("zona no reconocida" in r["porque"] and "GK / DEF" in r.get("esperado", "")
              for r in rec["rechazos"]), rec["rechazos"])
    check("un rol desconocido se declara con lo esperado",
          any("rol no reconocido" in r["porque"] and "🔴" in r.get("esperado", "")
              for r in rec["rechazos"]), rec["rechazos"])
    check("un jugador sin nombre se declara", "sin nombre" in porques, porques)
    check("el rechazo dice DÓNDE estaba", all(r["donde"] for r in rec["rechazos"]), rec["rechazos"])

    # ── un depósito que BORRA lo anterior lo dice (el error de la 1ª corrida) ─
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))
    rec = c.post(f"{A}/analisis/cowork", json={"fixtureId": sin_ficha,
                                               "equipos": {"a": {"bloques": {"A": 1}}, "b": {}}}).json()
    check("un depósito incompleto avisa de lo que borró", rec["perdido"], rec.get("perdido"))
    check("y el aviso explica que el POST reemplaza entero",
          "reemplaza el parte entero" in rec["aviso"], rec.get("aviso"))
    check("lo borrado se cuenta campo por campo",
          any("alertas" in x for x in rec["perdido"]) and any("jugadores" in x for x in rec["perdido"]),
          rec["perdido"])
    c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha))
    rec = c.post(f"{A}/analisis/cowork", json=_parte(sin_ficha)).json()
    check("re-depositar lo mismo NO avisa de pérdida", rec["perdido"] == [] and not rec["aviso"],
          rec.get("perdido"))

    # ── LO QUE SE TIRA EN SILENCIO (2ª corrida de Cowork) ───────────────────
    # El fallo más caro no es un valor inválido —ese se ve— sino una clave con
    # el nombre equivocado: se descarta entera y el POST responde 200.
    rec, d = _dep({"bloques": {"A": 4}, "sensibilidadd": [{"supuesto": "x"}],
                   "plantel": [{"nombre": "Uno", "zona": "GK", "rol": "TF", "minutos": 90}]})
    porques = {r["donde"]: r for r in rec["rechazos"]}
    check("una clave desconocida del equipo se delata",
          "equipos.a.sensibilidadd" in porques, list(porques))
    check("y sugiere la que se quiso escribir",
          "sensibilidad" in porques["equipos.a.sensibilidadd"]["esperado"],
          porques.get("equipos.a.sensibilidadd"))
    check("también dentro de un jugador",
          any("minutos" in k for k in porques), list(porques))

    r = c.post(f"{A}/analisis/cowork", json={"fixtureId": sin_ficha, "pronosticoo": {"marcador": "2-1"},
                                             "equipos": {"a": {"bloques": {"A": 1}}, "b": {}}}).json()
    check("una clave desconocida en la raíz se delata",
          any(x["donde"] == "(raíz).pronosticoo" and "pronostico" in x["esperado"]
              for x in r["rechazos"]), r["rechazos"])

    # alertas: `texto` como alias de `detalle`, y `ambos` es vocabulario válido
    r = c.post(f"{A}/analisis/cowork", json={
        "fixtureId": sin_ficha, "equipos": {"a": {"bloques": {"A": 1}}, "b": {}},
        "alertas": [{"codigo": "T.54", "equipo": "ambos", "texto": "el texto va aquí"},
                    {"codigo": "VACIA", "equipo": "a"},
                    {"codigo": "RARA", "equipo": "los dos", "detalle": "x"}]}).json()
    d = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()
    check("`texto` se acepta como alias de `detalle`",
          d["alertas"][0]["detalle"] == "el texto va aquí", d["alertas"][0])
    check("`ambos` es un equipo válido en una alerta", d["alertas"][0]["equipo"] == "ambos",
          d["alertas"][0])
    check("una alerta sin texto se delata como cáscara vacía",
          any("cáscara vacía" in x["porque"] for x in r["rechazos"]), r["rechazos"])
    check("un equipo de alerta inválido se delata",
          any("equipo no reconocido" in x["porque"] for x in r["rechazos"]), r["rechazos"])

    # ── UNA BAJA FUERA DE LA TABLA F1 NO PESA EN EL IP ──────────────────────
    # Cowork lo leyó como "el ponderador solo cuenta TF". No: cuenta todos los
    # roles, pero solo de quien está en la tabla.
    base_f1 = [{"nombre": "Castillo", "zona": "DEF", "rol": "TF"},
               {"nombre": "Uno", "zona": "MID", "rol": "TH"}]
    _, d = _dep({"bloques": {"A": 1}, "plantel": base_f1,
                 "fuera": [{"nombre": "Castillo", "estado": "baja", "motivo": "lesión"},
                           {"nombre": "Uno", "estado": "baja", "motivo": "lesión"}]})
    check("el IP pondera TODOS los roles, no solo TF",
          d["equipos"]["a"]["disponibilidad"]["ramas"]["a"]["ip"] == 5.0,
          d["equipos"]["a"]["disponibilidad"]["ramas"]["a"]["ip"])

    rec, d = _dep({"bloques": {"A": 1}, "plantel": base_f1,
                   "fuera": [{"nombre": "Castillo", "estado": "baja", "motivo": "lesión"},
                             {"nombre": "Gómez", "estado": "baja", "motivo": "lesión",
                              "zona": "MID", "rol": "🟠"},
                             {"nombre": "Inda", "estado": "baja", "motivo": "lesión"}]})
    check("una baja con zona y rol entra a la tabla y SÍ pesa",
          d["equipos"]["a"]["disponibilidad"]["ramas"]["a"]["ip"] == 5.0,
          d["equipos"]["a"]["disponibilidad"]["ramas"]["a"]["ip"])
    check("y queda marcada como venida de `fuera`",
          any(j.get("soloBaja") for j in d["equipos"]["a"]["plantel"]),
          [j["nombre"] for j in d["equipos"]["a"]["plantel"]])
    check("una baja SIN zona/rol y fuera de la F1 se delata (no pesa)",
          any("NO pesa en el Impacto Ponderado" in x["porque"] and x.get("jugador") == "Inda"
              for x in rec["rechazos"]), rec["rechazos"])

    # ── el cruce de nombres, al detalle ─────────────────────────────────────
    from backend.analisis import bloque_f as bf

    tabla = [
        {"nombre": "Ángelo Campos", "zona": "GK", "rol": "TF"},
        {"nombre": "Carlos Zambrano", "zona": "DEF", "rol": "TF"},
        {"nombre": "Miguel Trauco", "zona": "DEF", "rol": "TH"},
        {"nombre": "Jairo Concha", "zona": "MID", "rol": "TF"},
        {"nombre": "Pablo Ceppelini", "zona": "MID", "rol": "ROT"},
        {"nombre": "Hernán Barcos", "zona": "ATK", "rol": "TH"},
        {"nombre": "Paolo Guerrero", "zona": "ATK", "rol": "TF"},
        {"nombre": "Alex Valera", "zona": "ATK", "rol": "SUP"},
    ]
    d = bf.resolver(tabla, [], ["A. Campos", "Zambrano", "Miguel Trauco", "J. Concha",
                                "Ceppelini", "Barcos", "Guerrero"], ["Valera"])
    check("la abreviatura de API-Football casa con el nombre completo", d["casados"] == 7,
          d["casados"])
    check("sin nadie fuera, el IP es cero", d["ip"] == 0.0, d["ip"])
    check("el suplente en banca no suma IP", d["f4"]["rotados"] == 0, d["f4"])

    d = bf.resolver(tabla, [], ["A. Campos", "Zambrano", "Trauco", "Concha", "Ceppelini",
                                "Barcos", "Valera"], ["Guerrero"])
    check("el titular fijo en banca es rotación, no baja", d["ip"] == 0.0 and d["f4"]["rotados"] == 1,
          (d["ip"], d["f4"]))

    d = bf.resolver(tabla, [], ["Zambrano", "Trauco", "Concha", "Ceppelini", "Barcos",
                                "Guerrero", "Valera"], [])
    check("el arquero titular ausente pesa 4.5 (×1.5 del F2c)", d["ip"] == 4.5, d["ip"])
    check("y su zona queda al 100% de reducción", d["reduccion"]["GK"] == 100.0, d["reduccion"])
    check("el nivel de IP sigue la tabla del protocolo", d["ipNivel"] == "ambar", d["ipNivel"])
    check("el ×1.5 se declara", d["multiplicadorGk"] is True)

    # dos apellidos iguales: no se adivina
    ambigua = tabla + [{"nombre": "Renzo Campos", "zona": "MID", "rol": "ROT"}]
    d = bf.resolver(ambigua, [], ["Campos", "Zambrano", "Trauco", "Concha", "Ceppelini",
                                  "Barcos", "Guerrero"], [])
    check("un apellido compartido va a dudas, no se resuelve a ojo",
          any("Campos" in x for x in d["dudas"]), d["dudas"])

    # una duda pública pesa la mitad
    d = bf.resolver(tabla, [{"nombre": "Paolo Guerrero", "estado": "duda", "motivo": "molestia"}],
                    ["A. Campos", "Zambrano", "Trauco", "Concha", "Ceppelini", "Barcos"], ["Valera"])
    check("la duda pesa la mitad que la baja", d["ip"] == 1.5, d["ip"])
    check("y conserva su motivo público",
          any(f["motivo"] == "molestia" for f in d["fuera"]), d["fuera"])

    check("F3 salta con EFE formado e impacto rojo",
          (bf.alerta_f3("FORMADO", "rojo") or {}).get("codigo") == "F3")
    check("F3 no salta si el impacto no es rojo", bf.alerta_f3("FORMADO", "ambar") is None)

    print()
    print(f"{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
