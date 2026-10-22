"""Tests del parte de Cowork: lo que se deposita, lo que se calcula y el once.

    python3 -m backend.test_cowork

Lo que se verifica es justo la frontera: que Cowork solo tenga que escribir lo
que es trabajo (sub-scores, tabla de plantel, prosa) y que TODO lo derivable
—totales, clasificación, IP, reducción por zona, ramas, F3, F4— lo ponga el
backend. Si un día alguien le pide a Cowork que mande un total, estos tests
siguen pasando pero el parte se vuelve más lento y más fácil de equivocar: por
eso el contrato ignora los campos calculados en vez de creerles.
"""
import os as _os_cache; _os_cache.environ.setdefault("SAD_CACHE_OBJETIVO_S", "0")  # los tests cambian fichas y veredictos y releen
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
        "matriz": {
            "a": {"ganar": {"tactica": "presión alta los primeros 25'", "pelota_parada": "córner al primer palo",
                            "gestionReloj": "doble pivote desde el 70'", "base": "Lago-Peñas 2014"},
                  "empatar": "bloque medio sin hundirse antes del 80'",
                  "perder": {"gatillo": "gol temprano de B", "errorSistemico": "lateral derecho a la espalda",
                             "psicologico": "ansiedad local", "goleada": "banda base"}},
            "b": {"gana": {"tactica": "transición por el carril de A"},
                  "perder": {"gatillo": "roja temprana"}},
            "confirma": "el 2-0 de la fecha 5", "contradice": "el 1-1 en su cancha",
        },
        "lecturaSad": {
            "moduloOperativo": "Regresión al Nivel con gap a favor de A",
            "unXDos": {"texto": "A con ventaja estructural", "rangoAmpliado": True},
            "contextoEmocional": "B llega de dos derrotas",
            "datoEstructural": "Núcleo de A intacto",
            "paradoja": "El mejor EFE es el más dependiente de un hombre",
            "reventon": "A: muy alto, rival mucho más fuerte que su zona → no seguir la racha; B: bajo",
            "espina": {"a": {"lectura": "positiva", "porque": "rachas parejas de temporada en temporada, lejos de su tope"},
                       "b": {"lectura": "se reinicia", "guia": "visita",
                             "porque": "de visita sus burbujas se cortan en empate"}},
        },
        # el índice es POR EQUIPO: el parte modelo declara los dos
        "tde": {"bloques": [
            {"ie": 58, "ieNivel": "ambar", "ise": 31, "equipo": "b",
             "tipologia": "repliegue por agotamiento", "ventana": "75-90'",
             "vias": [{"nombre": "echada", "indice": 58, "ventana": "75-90'", "detalle": "baja el bloque"}],
             "falsador": "si sostiene la línea tras el 75'",
             "reasignacion": {"siMarcaPrimero": {"sob1": 0, "tipologia": "ECHADA-VOL", "nota": "administra"},
                              "siRecibePrimero": {"sob1": 1, "sob2": 0.5, "nota": "persigue y se expone"}}},
            {"ie": 24, "ieNivel": "verde", "ise": 47, "iseNivel": "ambar", "equipo": "a",
             "tipologia": "sobreexposición por urgencia", "ventana": "60-75'",
             "vias": [{"nombre": "sobreexposicion", "indice": 47, "ventana": "60-75'",
                       "detalle": "adelanta los laterales"}],
             "falsador": "si conserva los laterales por detrás del balón",
             "reasignacion": {"siMarcaPrimero": {"sob1": 0}, "siRecibePrimero": "sigue igual"}},
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
        "documentos": [{"id": "ensayo", "cuerpo": "# Cómo puede darse\n\nTexto largo. Las burbujas le dan buena espina al local."},
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
          and "NO compara entre bases" in esc[0]["detalle"] and "REVENTÓN" in esc[0]["detalle"],
          esc and esc[0]["detalle"])
    # ── LA COPA NO ES UNA BASE (Cristal–Bentín, tercera tanda de Perú) ──────
    from backend.analisis import escala as _esc
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("INSERT OR REPLACE INTO teams (id, name, country) VALUES (990102, 'Bentín Tacna', 'Peru')")
        _con.execute("INSERT OR REPLACE INTO teams (id, name, country) VALUES (990103, 'Millwall', 'England')")
        _con.execute("INSERT OR REPLACE INTO leagues (id, name, country, season) VALUES (502, 'Copa Bicentenario', 'Peru', 2026)")
        _con.execute("INSERT OR REPLACE INTO leagues (id, name, country, season) VALUES (40, 'Championship', 'England', 2026)")
        for i in range(2):  # Bentín: en la base solo hay partidos de copa
            _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                         "home_team_id, away_team_id, goals_home, goals_away) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (990130 + i, (t0 - _dt.timedelta(days=9 * (i + 1))).strftime("%Y-%m-%d %H:%M:%S"),
                          "FT", "Match Finished", 502, 2026, 990102, 990101, 1, 0))
        for i in range(3):  # Millwall: su Championship
            _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                         "home_team_id, away_team_id, goals_home, goals_away) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (990140 + i, (t0 - _dt.timedelta(days=7 * (i + 1))).strftime("%Y-%m-%d %H:%M:%S"),
                          "FT", "Match Finished", 40, 2026, 990103, 990101, 1, 1))
        _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                     "home_team_id, away_team_id) VALUES (?,?,?,?,?,?,?,?)",
                     (990150, (t0 + _dt.timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), "NS",
                      "Not Started", 502, 2026, fxr["home_team_id"], 990102))
    check("una copa se reconoce por la lista o por el nombre (FA Cup, Copa del Rey, Coppa, Pokal)",
          _esc.es_copa(502) and _esc.es_copa(999, "FA Cup") and _esc.es_copa(999, "Coppa Italia")
          and _esc.es_copa(999, "DFB Pokal") and not _esc.es_copa(999, "Premier League"))
    _bb = _esc.base_de(990102, None)
    check("un equipo con solo partidos de copa no es «primera»: su liga está fuera del padrón",
          _bb and _bb["categoria"] == "fuera del padrón" and _bb["id"] is None, _bb)
    check("la segunda inglesa es segunda; la relación se lee desde el equipo",
          _esc.base_de(990103, None)["categoria"] == "segunda"
          and _esc.relacion({"id": 39, "pais": "England", "categoria": "primera"},
                            _esc.base_de(990103, None)) == "rival de categoría inferior"
          and _esc.relacion(_esc.base_de(990103, None),
                            {"id": 39, "pais": "England", "categoria": "primera"}) == "rival de categoría superior"
          and _esc.relacion({"id": 268, "pais": "Uruguay", "categoria": "primera"},
                            {"id": 270, "pais": "Uruguay", "categoria": "primera"}) == "misma")
    check("cambio de categoría: el de la Championship jugando Premier es ascendido; al revés, descendido; "
          "una copa no es cambio",
          _esc.cambio_de_categoria(_esc.base_de(990103, None), 39) == "ascendido"
          and _esc.cambio_de_categoria({"id": 39, "categoria": "primera"}, 40) == "descendido"
          and _esc.cambio_de_categoria({"id": 39, "categoria": "primera"}, 45) == ""
          and _esc.cambio_de_categoria({"id": 39, "categoria": "primera"}, 39) == "")
    # pretemporada: Millwall (base Championship) con su próximo partido de liga en la Premier
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("INSERT OR REPLACE INTO leagues (id, name, country, season) VALUES (39, 'Premier League', 'England', 2026)")
        _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                     "home_team_id, away_team_id) VALUES (?,?,?,?,?,?,?,?)",
                     (990160, (t0 + _dt.timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S"), "NS",
                      "Not Started", 39, 2027, 990103, 990101))
    _pre = _esc.entre(fxr["home_team_id"], 990103, t0.strftime("%Y-%m-%d"), 667)
    check("amistoso de pretemporada con un rival que ya ascendió: la escala lo dice (Mallorca–Elversberg)",
          _pre["comparable"] is False and _pre.get("cambioDeCategoriaRival") == "ascendido"
          and "receso" in _pre["nota"], _pre)
    _wh = _esc.entre(fxr["home_team_id"], 990103, None, 40)   # uno de LaLiga jugando la liga de Millwall
    check("con el rival de su liga nueva, lo que no compara es la HISTORIA del equipo (West Ham en The Den)",
          _wh["relacion"] == "equipo descendido" and _wh["comparable"] is False
          and "categoría vieja" in _wh["nota"] and "lejos" in _wh["nota"], _wh)
    r = c.post(f"{A}/analisis/cowork", json=_parte(990150))
    esc2 = [a for a in c.get(f"{A}/analisis/cowork/990150").json()["alertas"] if a["codigo"] == "ESCALA-LIGAS"]
    check("cruce de copa con un rival fuera del padrón → ESCALA-LIGAS (antes la copa contaba como su liga)",
          len(esc2) == 1 and esc2[0]["relacion"] == "rival fuera del padrón", esc2)
    j_esc = c.get(f"{A}/equipos/{fxr['home_team_id']}/burbujas", params={"proximo": 990150}).json()
    check("la burbuja trae la escala del próximo rival: no comparable, con su nota y el historial en copas",
          j_esc.get("escala", {}).get("comparable") is False and "reserva" in j_esc["escala"]["nota"]
          and "porRelacion" in j_esc["escala"]["historial"], j_esc.get("escala"))
    check("con escala distinta la confianza del riesgo baja a «baja» y lo dice; los puntos no se tocan",
          all(f["riesgo"]["confianza"] == "baja" and any("escala distinta" in m for m in f["riesgo"]["confianzaMotivos"])
              for f in j_esc["familias"].values() if f.get("riesgo") and f["riesgo"]["nivel"] != "sin base"),
          [f.get("riesgo") for f in j_esc["familias"].values()])
    # incidencia 295: el reventón del parte aplica la MISMA regla que la tarjeta
    _rc = (c.get(f"{A}/analisis/cowork/990150").json().get("lecturaSad") or {}).get("reventonCalculado") or {}
    _rga = ((_rc.get("a") or {}).get("riesgo")) or {}
    check("295: el reventonCalculado del parte trae «escala distinta» en la confianza, como /burbujas",
          _rga.get("nivel") == "sin base" or (_rga.get("confianza") == "baja"
          and any("escala distinta" in m for m in _rga.get("confianzaMotivos") or [])), _rga)
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM fixtures WHERE id BETWEEN 990100 AND 990199")
    from backend.analisis.parte import borrar as _borrar_parte
    _borrar_parte(990120)
    _borrar_parte(990150)

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
    # UN ÍNDICE QUE NO SE PUEDE CALCULAR NO ES UN CERO (11/10/2026: Rennes–
    # Auxerre y San Lorenzo–Riestra salían «IE 0.0 · ISE 0.0» con el bloque S
    # sin puntuar: el riesgo más bajo de la escala sobre algo que nadie midió)
    sin_s = {k: v for k, v in ind.items() if not k.startswith("S")}
    r = c.post(f"{A}/analisis/cowork", json={**pel, "tde": {"bloques": [
        {"equipo": "a", "ventana": "60-75'", "indicadores": sin_s, "ieNivel": "ambar"},
        {"equipo": "b", "ventana": "75-90'", "indicadores": ind}]}})
    bl = {b["equipo"]: b for b in c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["tde"]["bloques"]}
    # (21/10/2026, decisión del usuario) sin S el IE sale PARCIAL sobre F, C y P, marcado
    check("sin bloque S el IE sale parcial (sinS, divisor 7.0), nunca 0.0 por defecto",
          bl["a"]["calculado"].get("sinS") and isinstance(bl["a"].get("ie"), float)
          and "7.0" in bl["a"]["calculado"]["formula"],
          (bl["a"].get("ie"), bl["a"].get("calculado", {}).get("formula")))
    check("…y el nivel declarado se conserva, y el otro equipo sí trae su número",
          bl["a"].get("ieNivel") == "ambar" and isinstance(bl["b"].get("ie"), float), (bl["a"], bl["b"].get("ie")))
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
    # LA FORMACIÓN ES LA DE LA FICHA DE HOY: la API corrige el string después del
    # cierre del once (Rayo 4-3-3 → 4-2-3-1, 18-19/10/2026)
    import sqlite3 as _sq3fo
    _g0 = c.get(f"{A}/analisis/cowork/{con_ficha}").json()["xi"]["a"]
    with _sq3fo.connect(os.path.join(tmp, "sad.db")) as _cfo:
        _hfo = _cfo.execute("SELECT home_team_id FROM fixtures WHERE id=?", (con_ficha,)).fetchone()[0]
        _cfo.execute("UPDATE alineaciones SET formacion='3-4-2-1' WHERE fixture_id=? AND team_id=?", (con_ficha, _hfo))
    _g1 = c.get(f"{A}/analisis/cowork/{con_ficha}").json()["xi"]["a"]
    check("el once de la ficha muestra la formación de la ficha de hoy y la que tenía al cerrar viaja aparte",
          _g1.get("formacion") == "3-4-2-1" and _g1.get("formacionAlCerrar") == (_g0.get("formacion") or "")
          and _g1.get("once") == _g0.get("once"), (_g0.get("formacion"), _g1.get("formacion"), _g1.get("formacionAlCerrar")))
    # un titular SIN posición en la fila 2 del grid es defensor (Central Español, 18/10/2026)
    from backend.analisis.dtp_cowork import oficial_de as _ofd
    _d0 = (_ofd(con_ficha).get("a") or {}).get("defensores")
    with _sq3fo.connect(os.path.join(tmp, "sad.db")) as _cfo:
        _pid = _cfo.execute("SELECT player_id FROM alineaciones WHERE fixture_id=? AND team_id=? AND titular=1 "
                            "AND posicion='D' LIMIT 1", (con_ficha, _hfo)).fetchone()
        if _pid:
            _cfo.execute("UPDATE alineaciones SET posicion=NULL, grid='2:1' WHERE fixture_id=? AND team_id=? AND player_id=?",
                         (con_ficha, _hfo, _pid[0]))
    _d1 = (_ofd(con_ficha).get("a") or {}).get("defensores")
    check("un defensor que la ficha trae sin posición pero en la fila 2 del grid se sigue contando",
          _pid is None or _d1 == _d0, (_d0, _d1, _pid))
    # UN ONCE DE LA FICHA QUE NO CASA NO ES «ESTA LIGA NO DA ONCES» (11/10/2026:
    # ADT–Cienciano y América–Águilas salieron en conflicto y, en la pasada
    # siguiente, en `nuncaVaALlegar`, porque sus lados ya venían de la ficha)
    malo = _parte(con_ficha)
    for lado in ("a", "b"):
        for j in malo["equipos"][lado]["plantel"]:
            j["nombre"] = "Zz" + j["nombre"].replace(" ", "")
        malo["equipos"][lado]["fuera"] = []
    c.delete(f"{A}/analisis/cowork/{con_ficha}")
    c.post(f"{A}/analisis/cowork", json=malo)
    primera = c.post(f"{A}/analisis/cowork/xi/auto").json()
    segunda = c.post(f"{A}/analisis/cowork/xi/auto").json()
    check("un once de la ficha que no casa con la tabla F1 sale en `conConflicto`",
          any(x["fixtureId"] == con_ficha for x in primera["conConflicto"]), primera.get("conConflicto"))
    check("…y en la pasada siguiente SIGUE en conflicto, no en `nuncaVaALlegar`",
          any(x["fixtureId"] == con_ficha and x.get("onceDeLaFicha") for x in segunda["conConflicto"])
          and all(x["fixtureId"] != con_ficha for x in segunda["nuncaVaALlegar"] + segunda["sinFichaTodavia"]),
          (segunda.get("conConflicto"), segunda.get("nuncaVaALlegar")))
    c.delete(f"{A}/analisis/cowork/{con_ficha}")
    c.post(f"{A}/analisis/cowork", json=_parte(con_ficha))
    c.post(f"{A}/analisis/cowork/xi/auto")

    # MEDIO ONCE NO ES «ESTA LIGA NO DA ONCES» (Necaxa–Atlas, ABB–Real Potosí,
    # Atlante–Pumas, 17/10/2026): la API trajo el once de un lado solo
    import sqlite3 as _sq3m
    from datetime import datetime as _dtm, timedelta as _tdm, timezone as _tzm
    _sadm = os.path.join(tmp, "sad.db")
    with _sq3m.connect(_sadm) as _con:
        _fxm = _con.execute("SELECT home_team_id, away_team_id, date, status_short FROM fixtures WHERE id=?",
                            (con_ficha,)).fetchone()
        _ali_b = _con.execute("SELECT * FROM alineaciones WHERE fixture_id=? AND team_id=?",
                              (con_ficha, _fxm[1])).fetchall()
        _cols = [d[0] for d in _con.execute("SELECT * FROM alineaciones LIMIT 1").description]
        _con.execute("DELETE FROM alineaciones WHERE fixture_id=? AND team_id=?", (con_ficha, _fxm[1]))
        _con.execute("UPDATE fixtures SET status_short='FT', date=? WHERE id=?",
                     ((_dtm.now(_tzm.utc) - _tdm(hours=8)).strftime("%Y-%m-%d %H:%M:%S"), con_ficha))
        _con.execute("CREATE TABLE IF NOT EXISTS fichas_meta (fixture_id INTEGER PRIMARY KEY, capturado_en TEXT, "
                     "alineaciones INTEGER, eventos INTEGER, stats INTEGER)")
        _con.execute("DELETE FROM fichas_meta WHERE fixture_id=?", (con_ficha,))
        _tit_a = [r[0] for r in _con.execute("SELECT jugador FROM alineaciones WHERE fixture_id=? AND team_id=? "
                                             "AND titular=1", (con_ficha, _fxm[0]))]
    _pm = _parte(con_ficha)
    for _j, _nom in zip(_pm["equipos"]["a"]["plantel"], _tit_a):
        _j["nombre"] = _nom    # el lado que SÍ llegó casa con su tabla: sin conflicto
    c.delete(f"{A}/analisis/cowork/{con_ficha}")
    c.post(f"{A}/analisis/cowork", json=_pm)
    c.post(f"{A}/analisis/cowork/xi/auto")
    medio = c.post(f"{A}/analisis/cowork/xi/auto").json()
    check("con el once de un solo lado y la ficha post-partido sin pedir, espera (no es «la liga no da onces»)",
          any(x["fixtureId"] == con_ficha and x.get("lados") == ["b"] for x in medio["sinFichaTodavia"])
          and all(x["fixtureId"] != con_ficha for x in medio["nuncaVaALlegar"]),
          (medio.get("sinFichaTodavia"), medio.get("nuncaVaALlegar")))
    with _sq3m.connect(_sadm) as _con:
        _con.execute("INSERT INTO fichas_meta VALUES (?, '2026-10-17 00:00:00', 11, 10, 0)", (con_ficha,))
    sellado = c.post(f"{A}/analisis/cowork/xi/auto").json()
    _n = [x for x in sellado["nuncaVaALlegar"] if x["fixtureId"] == con_ficha]
    check("con la ficha post-partido ya pedida, va a `nuncaVaALlegar` pidiendo SOLO el lado que falta",
          _n and _n[0]["lados"] == ["b"] and "SÍ da onces" in _n[0]["porque"], _n)
    with _sq3m.connect(_sadm) as _con:
        _con.execute("DELETE FROM fichas_meta WHERE fixture_id=?", (con_ficha,))
        _con.execute("UPDATE fixtures SET status_short=?, date=? WHERE id=?", (_fxm[3], _fxm[2], con_ficha))
        _con.executemany(f"INSERT INTO alineaciones ({','.join(_cols)}) VALUES ({','.join('?' * len(_cols))})",
                         _ali_b)
    c.delete(f"{A}/analisis/cowork/{con_ficha}")
    c.post(f"{A}/analisis/cowork", json=_parte(con_ficha))
    c.post(f"{A}/analisis/cowork/xi/auto")

    # LA FICHA QUE SE COMPLETA DESPUÉS DEL CIERRE (Nacional Potosí, 18/10/2026:
    # 8 titulares y sin banco 25' antes; la ficha final traía 11 + 12)
    with _sq3m.connect(_sadm) as _con:
        _todas_a = _con.execute("SELECT * FROM alineaciones WHERE fixture_id=? AND team_id=?",
                                (con_ficha, _fxm[0])).fetchall()
        _tit_rows = [r for r in _todas_a if r[_cols.index("titular")]]
        _con.execute("DELETE FROM alineaciones WHERE fixture_id=? AND team_id=?", (con_ficha, _fxm[0]))
        _con.executemany(f"INSERT INTO alineaciones ({','.join(_cols)}) VALUES ({','.join('?' * len(_cols))})",
                         _tit_rows[:8])
    c.delete(f"{A}/analisis/cowork/{con_ficha}")
    c.post(f"{A}/analisis/cowork", json=_parte(con_ficha))
    c.post(f"{A}/analisis/cowork/xi/auto")
    _x8 = c.get(f"{A}/analisis/cowork/{con_ficha}").json()["xi"]["a"]
    with _sq3m.connect(_sadm) as _con:
        _con.execute("DELETE FROM alineaciones WHERE fixture_id=? AND team_id=?", (con_ficha, _fxm[0]))
        _con.executemany(f"INSERT INTO alineaciones ({','.join(_cols)}) VALUES ({','.join('?' * len(_cols))})",
                         _todas_a)
    _re = c.post(f"{A}/analisis/cowork/xi/auto").json()
    _x11 = c.get(f"{A}/analisis/cowork/{con_ficha}").json()["xi"]["a"]
    check("un lado cerrado con la ficha incompleta se vuelve a cruzar cuando la ficha se completa",
          len(_x8["once"]) == 8 and len(_x11["once"]) == len(_tit_rows)
          and any(x["fixtureId"] == con_ficha and x["lado"] == "a" and "se completó" in x.get("porque", "")
                  for x in _re["reemplazados"]), (len(_x8["once"]), len(_x11["once"]), _re["reemplazados"]))
    _re2 = c.post(f"{A}/analisis/cowork/xi/auto").json()
    check("y una vez completo no se vuelve a tocar (idempotente)",
          all(x["fixtureId"] != con_ficha for x in _re2["reemplazados"] + _re2["cerrados"]), _re2["reemplazados"])

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
    r_id = c.post(f"{A}/analisis/cowork", json={
        "fixtureId": sin_ficha, "equipos": {"a": {"bloques": {"A": 3},
            "plantel": [{"nombre": "Ito Hiroki", "zona": "DEF", "rol": "TF", "jugadorId": 9001}],
            "fuera": [{"nombre": "H. Ito", "jugadorId": 9001, "zona": "DEF", "rol": "TF", "motivo": "lesión"}]}}}).json()
    _pl_id = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]["plantel"]
    check("una baja con jugadorId entra sin rechazo y no duplica la fila de la tabla con ese id (310)",
          not any("jugadorId" in x["donde"] for x in r_id["rechazos"] if x["donde"].startswith("equipos.a.fuera"))
          and len(_pl_id) == 1, (r_id["rechazos"], _pl_id))
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
    check("la Champions entra sola también en fase liga (14/10/2026), con prioridad de top 6; Europa y Conference no",
          prio_de(2, "League Stage - 3")[0] == 4 and prio_de(3, "League Stage - 3")[0] == 0
          and prio_de(848, "League Stage - 3")[0] == 0, (prio_de(2, "League Stage - 3"), prio_de(848, "League Stage - 3")))
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
    _ag41 = (ag.get("analizar") or []) + (ag.get("enEspera") or [])
    check("41: cada partido de la agenda dice de qué lado son sus etiquetas (el visitante)",
          bool(_ag41) and all(x.get("etiquetasDe") == "b" for x in _ag41), [x.get("etiquetasDe") for x in _ag41][:5])
    check("y cada candidato viene marcado con lo que ya hay en la base",
          all("tieneParte" in x and "onceCerrado" in x
              for x in (ag["analizar"] + ag["descartados"])),
          (ag["analizar"] or [{}])[0])
    check("los que ya tienen parte NO aparecen en porHacer",
          all(x not in ag["porHacer"] for x in ag["yaHechos"]),
          (ag["porHacer"], ag["yaHechos"]))
    check("y se explica que re-depositar REEMPLAZA, para no rehacer de más",
          "REEMPLAZA" in ag["notaReanudacion"], ag.get("notaReanudacion"))
    # EL CUPO ES DE TRABAJO (tramo de la tarde del 17/10/2026): los que ya
    # tienen parte no ocupan lugar; el límite cuenta solo los que faltan
    ag1 = c.get(f"{A}/analisis/cowork/agenda",
                params={"fecha": fecha, "limite": 1, "incluirDescartados": True}).json()
    check("con limite=1, entra a lo sumo UNO sin parte y además todos los que ya tienen parte",
          len(ag1["porHacer"]) <= 1
          and len(ag1["analizar"]) == len(ag1["porHacer"]) + len(ag1["yaHechos"]),
          (ag1["porHacer"], ag1["yaHechos"], ag1["corte"]))
    check("los ya hechos no quedan en espera por el límite",
          not any(x["tieneParte"] for x in ag1["enEspera"]) and ag1["corte"]["limite"] == 1,
          [x["fixtureId"] for x in ag1["enEspera"] if x["tieneParte"]])

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
    check("y la mide contra la meta del 80 % de TODO el padrón, no contra el cupo",
          lat["coberturaDeAyer"].get("meta") == 0.8 and "porcentaje" in lat["coberturaDeAyer"]
          and "faltaronTotal" in lat["coberturaDeAyer"], lat.get("coberturaDeAyer"))
    check("lista los veredictos vencidos y los onces sin cerrar",
          isinstance(lat["veredictosVencidos"], list) and isinstance(lat["sinOnceCerrado"], list),
          sorted(lat))
    cp = lat.get("cuotasPrepartido") or {}
    check("vigila las cuotas prepartido de los próximos NS (deuda 8)",
          {"proximos", "conCuota", "ultimaCaptura", "alarma"} <= set(cp), cp)
    from backend.analisis import parte as _parte_mod
    _min = _parte_mod.CUOTAS_MIN_PROXIMOS
    try:
        _parte_mod.CUOTAS_MIN_PROXIMOS = 0
        sin = _parte_mod.cuotas_prepartido(horas=24 * 365 * 5)
        check("la alarma suena SOLO cuando ningún NS próximo tiene cuota",
              sin["proximos"] > 0 and bool(sin["alarma"]) == (sin["conCuota"] == 0), sin)
    finally:
        _parte_mod.CUOTAS_MIN_PROXIMOS = _min
    check("y declara que el silencio cuenta como fallo",
          "ROJO" in lat["nota"] and "silencio" in lat["nota"].lower(), lat.get("nota"))
    # EL PLAN DE API-FOOTBALL: cuánto, en qué y a qué hora se acabó (11/10/2026:
    # agotado a las 12:40 de Lima y la tarde sudamericana sin cuotas en juego)
    check("sin marcador de la ingesta, el presupuesto no afirma nada",
          lat.get("presupuestoApi") == {"hoy": None, "ayer": None, "alarma": ""}, lat.get("presupuestoApi"))
    from datetime import datetime as _dtp, timezone as _tzp
    _hoy = _dtp.now(_tzp.utc).strftime("%Y-%m-%d")
    with open(os.path.join(tmp, ".extractor_cuota.json"), "w", encoding="utf-8") as _f:
        json.dump({"dia": _hoy, "usadas": 1200, "limite_api": 7500,
                   "usadas_por": {"odds/live": 900, "fixtures": 300},
                   "usadas_por_hora": {"12": 700, "13": 500}, "agotado_en": None,
                   "anterior": {"dia": "2026-10-11", "usadas": 7495, "limite_api": 7500,
                                "usadas_por": {"odds/live": 5100, "odds": 1500, "fixtures": 895},
                                "usadas_por_hora": {"12": 1300, "17": 1100},
                                "agotado_en": "2026-10-11T17:40:12Z"}}, _f)
    pa = c.get(f"{A}/analisis/cowork/latido").json()
    pr = pa.get("presupuestoApi") or {}
    check("el latido trae el consumo de hoy por endpoint y por hora",
          (pr.get("hoy") or {}).get("usadas") == 1200
          and list((pr.get("hoy") or {}).get("porEndpoint", {}))[0] == "odds/live"
          and (pr.get("hoy") or {}).get("porHora") == {"12": 700, "13": 500}, pr.get("hoy"))
    check("y el de ayer, con la hora de Lima en que se agotó",
          (pr.get("ayer") or {}).get("agotadoEnLima") == "12:40", pr.get("ayer"))
    check("un plan agotado antes de la noche es alarma y pasa al motivo del latido",
          "12:40" in pr.get("alarma", "") and "odds/live 5100" in pr["alarma"]
          and pr["alarma"] in pa["porque"] and pa["estado"] in ("ambar", "rojo"), pr.get("alarma"))
    with open(os.path.join(tmp, ".extractor_cuota.json"), "w", encoding="utf-8") as _f:
        json.dump({"dia": _hoy, "usadas": 7495, "limite_api": 7500, "usadas_por": {},
                   "agotado_en": f"{_hoy}T23:30:00Z"}, _f)
    check("agotarse a las 23:30 UTC (media hora del reset) no es alarma",
          _parte_mod.presupuesto_api()["alarma"] == "", _parte_mod.presupuesto_api())
    # la marca del primer minuto del día con el día lejos del tope es la cola de la
    # ventana anterior, no un agotamiento (19/10/2026: «19:00» con 4.679 de 7.500)
    with open(os.path.join(tmp, ".extractor_cuota.json"), "w", encoding="utf-8") as _f:
        json.dump({"dia": _hoy, "usadas": 1000, "limite_api": 7500, "usadas_por": {},
                   "anterior": {"dia": "2026-10-19", "usadas": 4679, "limite_api": 7500, "usadas_por": {},
                                "agotado_en": "2026-10-19T00:00:55Z"}}, _f)
    _pq = _parte_mod.presupuesto_api()
    check("un día que terminó en 4.679 de 7.500 no se agotó aunque traiga la marca de las 00:00 UTC: no hay alarma",
          _pq["alarma"] == "" and _pq["ayer"]["agotadoEn"] is None, _pq)
    os.remove(os.path.join(tmp, ".extractor_cuota.json"))
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
    check("y al lado la K de la condición de hoy (local para a, visita para b) con su riesgo",
          rc["a"].get("condicion", {}).get("familia") == "local" and rc["b"].get("condicion", {}).get("familia") == "visita"
          and all({"actual", "riesgo", "rival", "extremo"} <= set(rc[l]["condicion"]) for l in ("a", "b")), rc)
    check("y las otras burbujas contadas por lado, en la condición de hoy (local para a, visita para b)",
          rc["a"]["otrasFamilias"]["condicion"] == "local" and rc["b"]["otrasFamilias"]["condicion"] == "visita"
          and all(isinstance(rc[l]["otrasFamilias"]["lineas"], list) for l in ("a", "b")),
          {l: (rc[l].get("otrasFamilias") or {}).get("condicion") for l in ("a", "b")})
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
    # Cagliari 19/10/2026: total en 0, K de VISITA en su récord → la tira lo dice (tipo dato)
    _cg = {"b": {"actual": None, "extremo": None,
                 "condicion": {"familia": "visita", "actual": {"k": 8.97}, "extremo": {"activo": True, "motivos": ["racha récord: 3 en 132"]}}},
           "a": {"actual": {"k": 5.0}, "extremo": {"activo": True, "motivos": ["K récord"]},
                 "condicion": {"familia": "local", "actual": {"k": 9.0}, "extremo": {"activo": True}}}}
    _alc = alertas_extremo(_cg, {"a": "Monza", "b": "Cagliari"})
    check("la K de la condición en su extremo sale en la tira (K-EXTREMO-CONDICION, dato); si ya grita la total, no se duplica",
          [(x["codigo"], x["equipo"]) for x in _alc] == [("K-EXTREMO", "a"), ("K-EXTREMO-CONDICION", "b")]
          and _alc[1]["tipo"] == "dato" and "de visita" in _alc[1]["detalle"], _alc)
    sint_c = {"a": {"actual": {"k": -17.93}, "riesgo": {"nivel": "bajo"},
                    "extremo": {"activo": False, "cerca": True, "motivos": ["K -17.93: más baja que el 95 % de las 39 burbujas - que reventaron (récord previo -19.54, a 1.61)"]}},
              "b": {"actual": {"k": 3.0}, "extremo": {"activo": False, "cerca": False, "motivos": []}}}
    alc = alertas_extremo(sint_c, {"a": "ADT", "b": "Cienciano"})
    check("K −17.9 a 1.6 del récord con riesgo BAJO → UNA alerta K-CERCA-EXTREMO (tipo dato) para el lado a, sin K-EXTREMO",
          len(alc) == 1 and alc[0]["codigo"] == "K-CERCA-EXTREMO" and alc[0]["equipo"] == "a"
          and alc[0]["tipo"] == "dato" and "ADT" in alc[0]["detalle"] and "95 %" in alc[0]["detalle"], alc)


    # FAMILIA-RECORD: la burbuja de otra familia grande y en su récord es CUIDADO (tipo dato)
    from backend.analisis.parte import alertas_familias, _cortes_veredicto
    _sf = {"a": {"otrasFamilias": {"familias": [
        {"familia": "noPierde", "ambito": "local", "partidos": 9, "record": "supera", "cuidado": True},
        {"familia": "anota", "ambito": "local", "partidos": 4, "record": "supera", "cuidado": False}]}},
        "b": {"otrasFamilias": {"familias": []}}}
    _af = alertas_familias(_sf, {"a": "Everton", "b": "Chelsea"})
    check("DC de local en su récord de 9 → UNA alerta FAMILIA-RECORD (dato) para Everton, sin la de 4",
          len(_af) == 1 and _af[0]["codigo"] == "FAMILIA-RECORD" and _af[0]["tipo"] == "dato"
          and "9 de local sin perder" in _af[0]["detalle"] and "anotando" not in _af[0]["detalle"]
          and "cuidado" in _af[0]["detalle"], _af)
    # una burbuja del «no» se dice con el texto del «no» (Nice, 18/10/2026: «anotando» por «sin anotar»)
    _sqf = {"b": {"otrasFamilias": {"familias": [
        {"familia": "anota", "ambito": "visita", "partidos": 5, "record": "supera", "cuidado": True, "valor": False},
        {"familia": "gana3+", "ambito": "local", "partidos": 8, "record": "iguala", "cuidado": True, "valor": False}]}}}
    _aq = alertas_familias(_sqf, {"b": "Nice"})
    check("FAMILIA-RECORD de una sequía dice el estado real: «sin anotar», «sin ganar por 3 o más»",
          _aq and "5 de visita sin anotar" in _aq[0]["detalle"] and "8 de local sin ganar por 3 o más" in _aq[0]["detalle"]
          and " anotando" not in _aq[0]["detalle"], _aq)
    check("sin reventón calculado, FAMILIA-RECORD no rompe", alertas_familias(None, {}) == [])
    # ESPINA CONTRA EL RIESGO (Albion–Torque, 18/10/2026): riesgo ALTO de la
    # racha − y espina «neutra» sin nombrar el riesgo
    from backend.analisis.parte import alertas_espina, espina_vs_riesgo
    _rv = {"a": {"actual": {"signo": "-"}, "riesgo": {"nivel": "alto"}},
           "b": {"actual": {"signo": "-"}, "riesgo": {"nivel": "muy alto"}}}
    _es = {"a": {"lectura": "neutra", "guia": "total", "porque": "dupla de 18 días, plantel en obra"},
           "b": {"lectura": "positiva", "guia": "total", "porque": "rival más flojo"}}
    _ae = alertas_espina(_rv, _es, {"a": "Albion", "b": "Torque"})
    check("riesgo ALTO de una racha − con espina neutra → ESPINA-VS-RIESGO para Albion; Torque (corta) no",
          len(_ae) == 1 and _ae[0]["equipo"] == "a" and "ALTO" in _ae[0]["detalle"]
          and "no nombra el riesgo" in _ae[0]["detalle"], _ae)
    _es2 = {"a": {"lectura": "neutra", "porque": "contra el riesgo alto porque la historia es de otro plantel"}}
    check("si el porque nombra el riesgo, queda dicho (la alerta lo reconoce y el recibo no lo cobra)",
          espina_vs_riesgo(_rv, _es2)[0]["dicho"] is True)
    check("…y la que ya lo dice no sale a la tira (Fenerbahçe y Slavia, 291)",
          alertas_espina(_rv, _es2, {"a": "Albion"}) == [], alertas_espina(_rv, _es2, {"a": "Albion"}))
    check("con riesgo BAJO, una espina que corta la racha también va contra",
          espina_vs_riesgo({"a": {"actual": {"signo": "+"}, "riesgo": {"nivel": "bajo"}}},
                           {"a": {"lectura": "cero"}})[0]["como"] == "la lee cortarse")
    _rech = []
    _ct = _cortes_veredicto([{"familia": "noPierde", "ambito": "local", "mecanismo": "bloque_bajo_del_rival", "porque": "p"},
                             {"familia": "noPierde", "ambito": "local", "mecanismo": "mala suerte", "porque": "q"},
                             {"familia": "inventada", "mecanismo": "roja"}], _rech, "porLado.a.cortes")
    check("los cortes: el mecanismo fuera de la lista queda «otro» con rechazo; la familia inventada se rechaza",
          [x["mecanismo"] for x in _ct] == ["bloque_bajo_del_rival", "otro"] and len(_rech) == 2, (_ct, _rech))

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
    # la fecha de /coachs (fuente por defecto) es el mes de la carrera: NO se toma (Rayo Zuliano, 18/10)
    check("con la base de /coachs, el parte sin `desde` queda sin antigüedad (no se rellena con la carrera)",
          da["meses"] is None and da["origenMeses"] != "base" and not da["desde"], (da, dict(dt_base)))
    import sqlite3 as _sq3dt
    with _sq3dt.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("UPDATE entrenadores SET fuente='alineacion' WHERE nombre=?", (dt_base["nombre"],))
    d_dt = c.post(f"{A}/analisis/cowork", json=p_dt).json()
    da = c.get(f"{A}/analisis/cowork/{sin_ficha}").json()["equipos"]["a"]["dt"]
    check("con la llegada VISTA en el banco (fuente alineacion), toma la fecha de asunción de la base",
          da["meses"] is not None and da["origenMeses"] == "base" and da["desde"] == dt_base["desde"],
          (da, dict(dt_base)))
    with _sq3dt.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("UPDATE entrenadores SET fuente='coachs' WHERE nombre=?", (dt_base["nombre"],))
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

    # LO OBJETIVO ANTES DEL VEREDICTO: el GET del veredicto da 404 hasta el
    # primer POST y quien lo escribe necesita saber qué escenario se jugó
    ob = c.get(f"{A}/analisis/cowork/{pasado['id']}/objetivo")
    check("lo objetivo se lee antes de escribir el veredicto (marcador y matriz)",
          ob.status_code == 200 and ob.json()["tieneVeredicto"] is False
          and "matriz" in ob.json()["objetivo"], ob.text[:300])
    check("sin parte depositado, 404", c.get(f"{A}/analisis/cowork/1/objetivo").status_code == 404)

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
        "porLado": {"a": {"veredicto": "acierto", "queP": "ganó como se dijo", "leccion": "",
                          "escenario": {"aparecio": "sí", "que": "la presión de los primeros 25'"}},
                    "b": {"veredicto": "fallo", "queP": "no llegó por fuera",
                          "leccion": "el bloque bajo entrenado sostiene los 90",
                          "skill": "teorema-del-echado"}},
    })
    check("el veredicto se acepta", r.status_code == 200, r.text[:300])
    v = r.json()
    check("sin salvedad, el campo viene vacío y no ausente", v["mancha"] == "", v.get("mancha"))
    check("la autopsia dice si lo escrito para el escenario jugado apareció (observación, se guarda tal cual)",
          v["porLado"]["a"].get("escenario") == {"aparecio": "si", "que": "la presión de los primeros 25'"}
          and "escenario" not in v["porLado"]["b"], v["porLado"])
    _pg = c.get(f"{A}/analisis/cowork/{pasado['id']}").json()
    check("el parte devuelve la matriz estructurada por equipo",
          (_pg.get("matriz") or {}).get("a", {}).get("ganar", {}).get("pelotaParada") == "córner al primer palo"
          and _pg["matriz"]["b"]["ganar"] == {"tactica": "transición por el carril de A"}, _pg.get("matriz"))
    check("y el objetivo trae, por lado, el escenario que dio el marcador",
          set((v.get("objetivo") or {}).get("matriz", {})) >= {"a", "b", "nota"}
          and v["objetivo"]["matriz"]["a"]["escenario"] in ("ganar", "empatar", "perder"),
          (v.get("objetivo") or {}).get("matriz"))
    # ── LAS OTRAS BURBUJAS QUE EL PARTIDO CORTÓ (usuario, 17/10/2026) ─────────
    _of = (v.get("objetivo") or {}).get("otrasFamilias") or {}
    check("el objetivo trae las otras burbujas por lado, con su nota de observación",
          set(_of) >= {"a", "b", "nota"} and "sin tasa" in _of["nota"], list(_of))
    check("porExplicar = grande (5+) o en su récord; el resto de lo cortado se cuenta sin pedir causa",
          all(_c["porExplicar"] == (_c["cuidado"] or _c["partidos"] >= 5)
              for l in ("a", "b") for _c in _of[l]["cortadas"]), _of)
    _hay = [(l, _c) for l in ("a", "b") for _c in _of[l]["cortadas"] if _c["porExplicar"]]
    if _hay:
        _l, _c = _hay[0]
        _rv = c.post(f"{A}/analisis/cowork/{pasado['id']}/veredicto", json={
            **v, "porLado": {**v["porLado"], _l: {**(v["porLado"].get(_l) or {"veredicto": "parcial", "queP": "x",
                                                                              "leccion": "x", "skill": "sad-analysis"}),
                                                    "cortes": [{"familia": _c["familia"], "ambito": _c["ambito"],
                                                                "mecanismo": "bloque_bajo_del_rival",
                                                                "porque": "el rival se cerró desde el arranque"}]}}}).json()
        check("la causa del corte se guarda con su mecanismo de la lista",
              (_rv["porLado"][_l].get("cortes") or [{}])[0].get("mecanismo") == "bloque_bajo_del_rival", _rv["porLado"][_l])
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
    # la tarjeta de la condición sale del MISMO cálculo del reventón (no se rehace: 20/10/2026)
    for lado, tid, fam in (("a", fx_p["home_team_id"], "local"), ("b", fx_p["away_team_id"], "visita")):
        _bc = c.get(f"{A}/equipos/{tid}/burbujas", params={"antesDe": pasado["id"]}).json()["familias"][fam]
        check(f"lado {lado}: el reventón del veredicto trae la K de la condición de ese día y su tarjeta",
              "condicion" in rv[lado] and (rv[lado]["condicion"] or {}).get("espinaTarjeta") == _bc.get("espinaTarjeta"),
              (rv[lado].get("condicion"), _bc.get("espinaTarjeta")))
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
    # EL AUTOGOL VA CON EL EQUIPO DEL EVENTO Y EL PENAL ERRADO NO ES GOL. La API
    # pone en el autogol al equipo beneficiado (Libertad–Guaraní 2-2 sumaba 3-1)
    # y un `Missed Penalty` viaja como `Goal` (Palmeiras–Corinthians).
    with _sq2.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.executemany("INSERT INTO fixture_eventos (fixture_id, minuto, extra, tipo, detalle, equipo_id, jugador) "
                         "VALUES (?,?,?,?,?,?,?)",
                         [(con_ficha, 60, 0, "Goal", "Own Goal", hid, "Autogol rival"),
                          (con_ficha, 70, 0, "Goal", "Missed Penalty", hid, "Penal errado")])
    ev = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]["evidencia"]["goles"]
    og = [g for g in ev if g["minuto"] == 60]
    check("el autogol cuenta para el equipo que figura en el evento (el beneficiado)",
          len(og) == 1 and og[0]["lado"] == "a" and og[0]["autogol"] is True, og)
    check("el penal errado no entra como gol", all(g["minuto"] != 70 for g in ev), ev)
    with _sq2.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM fixture_eventos WHERE fixture_id=? AND minuto IN (60, 70) "
                     "AND jugador IN ('Autogol rival', 'Penal errado')", (con_ficha,))

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

    # LA REASIGNACIÓN ES UN CAMPO Y EL VEREDICTO DICE QUÉ RAMA JUGÓ EL PARTIDO
    # (disciplina 44; faltó en ~11 lados del 11/10/2026). El 34' es de 'a'.
    p_tde["tde"] = {"bloques": [
        {"ie": 60, "equipo": "a", "ventana": "45-60'", "tipologia": "prueba",
         "reasignacion": {"siMarcaPrimero": {"sob1": 0, "tipologia": "ECHADA-VOL"}}},
        {"ie": 40, "equipo": "b", "ventana": "20-40'", "tipologia": "prueba",
         "reasignacion": {"siMarcaPrimero": {"sob1": 0}, "siRecibePrimero": {"sob1": 2},
                          "siEmpata": {"sob1": 1}}}]}
    rec_r = c.post(f"{A}/analisis/cowork", json=p_tde).json()
    check("una rama desconocida y un SOB1 fuera de 0/0.5/1 se rechazan con motivo",
          any(x["donde"].endswith("reasignacion.siEmpata") for x in rec_r["rechazos"])
          and any(x["donde"].endswith("siRecibePrimero.sob1") for x in rec_r["rechazos"]), rec_r["rechazos"])
    check("y una reasignación a medias se avisa en `faltan` (se cobra al cerrar)",
          any(x["bloque"] == "tde.reasignacion" for x in rec_r["faltan"]), rec_r["faltan"])
    # TDE v0.1.22: la rama que pasa a sobreexposición sin su SOB2 se avisa al depositar
    p_s2 = json.loads(json.dumps(p_tde))
    p_s2["tde"]["bloques"][1]["reasignacion"] = {"siMarcaPrimero": {"sob1": 0}, "siRecibePrimero": {"sob1": 1}}
    rec_s2 = c.post(f"{A}/analisis/cowork", json=p_s2).json()
    check("rama siRecibePrimero en SOB sin sob2: `faltan` lo pide (el seguro del arranque no se hereda)",
          any(x["bloque"] == "tde.reasignacion.sob2" for x in rec_s2["faltan"]), rec_s2["faltan"])
    check("el recibo trae pronosticoVsMotor (o null sin pronóstico): la clave existe",
          "pronosticoVsMotor" in rec_s2, list(rec_s2)[:30])
    # LA VENTANA RELATIVA AL GOL Y LA VENTANA DE LA RAMA (veredictos del 17/10/2026)
    from backend.analisis.veredicto import _ventana as _vv, ventana_relativa as _vr
    check("«15-30' desde la ventaja» es relativa: no se lee como minutos 15-30",
          _vr("15-30' desde la ventaja") and _vv("15-30' desde la ventaja") is None and _vv("75-90'") == (75, 90))
    from backend.analisis.veredicto import clase_ventana as _cv
    _g = lambda m, l: {"minuto": m, "lado": l}
    check("recibió 3 antes de la ventana → roto (disciplina 3); 3 arriba → rama abandonada (24); si no, se juega",
          _cv([_g(10, "b"), _g(20, "b"), _g(30, "b")], 75, "b")[0] == "roto"
          and _cv([_g(10, "a"), _g(20, "a"), _g(30, "a")], 75, "b")[0] == "rama_abandonada"
          and _cv([_g(10, "a"), _g(20, "b")], 75, "a")[0] == ""
          and _cv([_g(80, "b"), _g(81, "b"), _g(82, "b")], 75, "b")[0] == "")
    p_rr = json.loads(json.dumps(p_tde))
    p_rr["tde"]["bloques"][0]["ventana"] = "15-30' desde la ventaja"
    p_rr["tde"]["bloques"][1]["reasignacion"]["siRecibePrimero"]["ventana"] = "30-40'"
    c.post(f"{A}/analisis/cowork", json=p_rr)
    od_rr = {b["equipo"]: b for b in c.get(f"{A}/analisis/cowork/{con_ficha}/objetivo").json()["objetivo"]["tde"]["bloques"]}
    check("una ventana relativa no se cobra y lo dice", od_rr["a"]["comprobable"] is False
          and "relativa" in od_rr["a"]["nota"], od_rr["a"])
    # el 34' es el gol que ABRE la rama «si recibe primero»: no se cobra en ella
    # (1493189, 19/10/2026) y la etiqueta es la de la rama, no la base
    check("con la rama jugada declarando su ventana, se mide ESA (30-40') sin cobrar el gol que la abre (34')",
          od_rr["b"]["ventanaDeRama"] is True and od_rr["b"]["desde"] == 30 and od_rr["b"]["golEnVentana"] is False
          and od_rr["b"]["ventana"] == "30-40'", od_rr["b"])
    c.post(f"{A}/analisis/cowork", json=p_tde)
    # EL TIMELINE ES «AL DÍA DEL PARTIDO» (City–PSG, 17/10/2026): ni el
    # resultado de ese partido ni la tabla con él
    from backend.analisis.parte import _fixture as _fxp, timeline_del_parte as _tlp
    _fxr = _fxp(con_ficha)
    _tlv = _tlp(_fxr, [{"fecha": "2020-01-01", "tipo": "hito", "titulo": "x"}], "", [])
    check("el timeline de un partido jugado corta ANTES de ese partido (sin su propio resultado)",
          _tlv and _tlv["periodo"]["hasta"] < str(_fxr["date"])[:10]
          and all(e["fecha"] < str(_fxr["date"])[:10] for e in _tlv["eventos"]), (_tlv or {}).get("periodo"))
    # UN IE QUE NO SE PUEDE CALCULAR SE AVISA (Athletico-PR, 17/10/2026: sin un S)
    p_ie = json.loads(json.dumps(p_tde))
    p_ie["tde"]["bloques"][0]["indicadores"] = {"F1": 1, "F2": 0.5, "C1": 0.5, "P1a": 1}
    rec_ie = c.post(f"{A}/analisis/cowork", json=p_ie).json()
    check("un bloque del TDE sin indicadores S → el recibo avisa que el IE sale PARCIAL",
          any(x["bloque"] == "tde.ie (lado a)" and "PARCIAL" in x["costara"] for x in rec_ie["faltan"]),
          [x for x in rec_ie["faltan"] if x["bloque"].startswith("tde")])
    c.post(f"{A}/analisis/cowork", json=p_tde)
    od_ra = {b["equipo"]: b for b in c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]["tde"]["bloques"]}
    check("el que marcó primero juega la rama siMarcaPrimero, declarada",
          od_ra["a"]["reasignacion"]["rama"] == "siMarcaPrimero" and od_ra["a"]["reasignacion"]["declarada"] is True
          and od_ra["a"]["reasignacion"]["loDeclarado"]["tipologia"] == "ECHADA-VOL", od_ra["a"]["reasignacion"])
    check("el otro juega siRecibePrimero y, sin declararla, lo dice",
          od_ra["b"]["reasignacion"]["rama"] == "siRecibePrimero" and od_ra["b"]["reasignacion"]["declarada"] is False
          and "disciplina 44" in od_ra["b"]["reasignacion"]["nota"], od_ra["b"]["reasignacion"])
    # TDE v0.1.21: el empate posterior y la expulsión tienen rama, y el veredicto
    # dice el segundo giro y cómo terminó la rama del que persigue (disciplina 61)
    from backend.analisis.veredicto import rama_jugada as _rj
    _g = lambda *xs: [{"minuto": m, "lado": l} for m, l in xs]  # noqa: E731
    _tdea = {"equipo": "a", "reasignacion": {"siMarcaPrimero": {"sob1": 0}, "siRecibePrimero": {"sob1": 1},
                                              "siLeEmpatan": {"sob1": 0.5, "nota": "reabre la SOB"}}}
    _r1 = _rj(_tdea, _g((28, "a"), (34, "b"), (80, "b")), 3, True)
    check("el que marcó primero y recibió el empate: segundoGiro siLeEmpatan, con su línea declarada (AEK, 44a)",
          _r1["rama"] == "siMarcaPrimero" and _r1["segundoGiro"]["minuto"] == 34
          and _r1["segundoGiro"]["declarada"] is True, _r1)
    _r2 = _rj({"equipo": "b", "reasignacion": {}}, _g((57, "a"), (62, "b"), (64, "b")), 3, True)
    check("el que recibió primero y marcó él: salida «marco», no cuenta contra la rama (Emelec, disciplina 61)",
          _r2["rama"] == "siRecibePrimero" and _r2["salida"] == "marco", _r2)
    _r3 = _rj({"equipo": "b", "reasignacion": {}}, _g((35, "a"), (65, "a")), 2, True)
    _r4 = _rj({"equipo": "b", "reasignacion": {}}, _g((59, "a"),), 1, True)
    check("…concedió de nuevo → «concedio»; sin más goles → «sinMasGoles»",
          _r3["salida"] == "concedio" and _r4["salida"] == "sinMasGoles" and "segundoGiro" not in _r4, (_r3, _r4))
    p_tde["tde"]["bloques"][0]["reasignacion"] = {"siMarcaPrimero": {"sob1": 0}, "siRecibePrimero": {"sob1": 1},
                                                  "siLeEmpatan": {"sob1": 1}, "siExpulsion": "roja ganando → ECHADA-NUM"}
    rec_n = c.post(f"{A}/analisis/cowork", json=p_tde).json()
    check("el parte acepta siLeEmpatan y siExpulsion sin rechazo",
          not any(x["donde"].startswith("tde.bloques[0].reasignacion") for x in rec_n["rechazos"]), rec_n["rechazos"])
    p_tde["tde"] = {"bloques": [{"ie": 60, "equipo": "a", "ventana": "45-60'", "tipologia": "prueba"},
                                {"ie": 40, "equipo": "b", "ventana": "20-40'", "tipologia": "prueba"}]}
    c.post(f"{A}/analisis/cowork", json=p_tde)

    # VARIAS LECCIONES POR LADO: una autopsia toca más de un skill (Cusco–Cristal)
    rv = c.post(f"{A}/analisis/cowork/{con_ficha}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "COND",
        "porLado": {"a": {"veredicto": "fallo", "skill": "teorema-del-echado", "reglaTocada": "disciplina 16",
                          "leccion": "con diez y perdiendo, atacó más",
                          "otrasLecciones": [
                              {"skill": "efe-clasificador", "reglaTocada": "COLAPSO EN CASCADA",
                               "leccion": "el favorito administró y no hubo colapso"},
                              {"skill": "diagnostico-tactico", "leccion": "el M2 se escribió sobre otro once"},
                              {"leccion": "sin skill no entra"}]}}}).json()
    check("una lección extra sin skill se rechaza con motivo",
          any("otrasLecciones[2]" in x["donde"] for x in rv["rechazos"]), rv["rechazos"])
    check("el GET devuelve las otras lecciones (y el eco las acepta)",
          len(rv["porLado"]["a"].get("otrasLecciones") or []) == 2, rv["porLado"]["a"])
    rv2 = c.post(f"{A}/analisis/cowork/{con_ficha}/veredicto",
                 json={k: v for k, v in rv.items() if k != "rechazos"}).json()
    check("re-depositar el eco conserva las otras lecciones",
          len(rv2["porLado"]["a"].get("otrasLecciones") or []) == 2 and not rv2["rechazos"], rv2.get("rechazos"))
    inv_l = c.get(f"{A}/analisis/cowork/lecciones", params={"cohorte": ""}).json()
    mias = sorted(i["clave"] for i in inv_l["items"] if i["fixtureId"] == con_ficha)
    check("cada lección es un item con su clave (fixture:lado, :2, :3)",
          mias == sorted([f"{con_ficha}:a", f"{con_ficha}:a:2", f"{con_ficha}:a:3"]), mias)
    extra = next(i for i in inv_l["items"] if i["clave"] == f"{con_ficha}:a:2")
    check("la extra hereda el veredicto del lado y va a su skill",
          extra["veredicto"] == "fallo" and extra["skill"] == "efe-clasificador"
          and extra["reglaTocada"] == "COLAPSO EN CASCADA", extra)
    check("un lado fallado sigue siendo UN fallo para el modo de fallo",
          inv_l["porModoFallo"]["fallos"] == sum(1 for i in inv_l["items"]
                                                 if i["veredicto"] in ("fallo", "parcial") and i["orden"] == 1),
          inv_l["porModoFallo"])
    # LAS DERROTAS DEL FAVORITO, con lo que el TDE y el DTP escribieron antes (21/10/2026)
    _u = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]["unXDos"]
    _df = c.get(f"{A}/analisis/cowork/derrotas-favorito", params={"cohorte": ""})
    _dj = _df.json() if _df.status_code == 200 else {}
    _fav = {"local": "a", "visita": "b"}.get(_u.get("declarado") or "")
    _perdio = bool(_fav) and _u.get("real") not in ("empate", _u.get("declarado"), None, "")
    _mio = [d for d in _dj.get("derrotas", []) if d["fixtureId"] == con_ficha]
    check("derrotas-favorito: el caso entra SOLO si el favorito declarado perdió, con su rama y su explicación",
          _df.status_code == 200 and set(_dj["resumen"]) == {"rama_escrita", "rama_sin_escribir", "sin_ficha", "sin_goles"}
          and (len(_mio) == 1 and _mio[0]["favorito"]["lado"] == _fav
               and _mio[0]["explicacion"] in _dj["resumen"] if _perdio else not _mio),
          (_u, _mio, _dj.get("resumen")))
    from backend.analisis import lecciones as _lec_df
    _orig_c, _orig_o = _lec_df._casos, _lec_df._objetivo
    def _caso(fid, decl, real, rama, declarada):
        return {"fixtureId": fid, "fecha": "2026-10-20", "equipoA": "Fav", "equipoB": "Riv", "cohorte": "x",
                "parte": {"dtp": {"bloques": [{"equipo": "a", "apertura": {"m2": {"viasGol": {"rival": ["contra por izquierda"]}}}}]},
                          "tde": {"bloques": [{"equipo": "a", "tipologia": "SOB"}]}},
                "veredicto": {"seleccion": "ciega", "porLado": {"a": {"leccion": "le empataron y se partió"}}},
                "_obj": {"unXDos": {"declarado": decl, "real": real, "probabilidadDeclarada": 55},
                         "marcador": {"texto": "1-2"}, "evidencia": {"goles": []},
                         "tde": {"bloques": [{"equipo": "a", "ventana": "75-90'", "golEnVentana": True,
                                              "reasignacion": {"rama": rama, "declarada": declarada}}]}}}
    _fab = [_caso(1, "local", "visita", "siMarcaPrimero", True), _caso(2, "local", "visita", "siRecibePrimero", False),
            _caso(3, "local", "visita", None, False), _caso(4, "local", "local", "siMarcaPrimero", True),
            _caso(5, "local", "empate", "siMarcaPrimero", True), _caso(6, "empate", "visita", "siMarcaPrimero", True)]
    _lec_df._casos = lambda limite=400, ids=None: _fab
    _lec_df._objetivo = lambda fid, parte: next(x["_obj"] for x in _fab if x["fixtureId"] == fid)
    try:
        _dfab = _lec_df.derrotas_favorito("", 400)
    finally:
        _lec_df._casos, _lec_df._objetivo = _orig_c, _orig_o
    check("derrotas del favorito: entran solo las derrotas del declarado (ni victoria, ni empate, ni favorito «empate»); "
          "rama escrita · sin escribir · sin ficha",
          [d["fixtureId"] for d in _dfab["derrotas"]] == [1, 2, 3]
          and [d["explicacion"] for d in _dfab["derrotas"]] == ["rama_escrita", "rama_sin_escribir", "sin_ficha"]
          and _dfab["derrotas"][0]["dtpViasRival"] == ["contra por izquierda"] and _dfab["derrotas"][0]["leccion"],
          _dfab)
    from backend import app as _app_df
    check("…y la web (token de lectura) la puede leer", _app_df._web_puede("GET", f"{A}/analisis/cowork/derrotas-favorito"))
    c.post(f"{A}/analisis/cowork/{con_ficha}/veredicto", json={
        "seleccion": "ciega", "modoEvaluacion": "COND", "porLado": {"a": {"veredicto": "fallo"}}})

    # UNA ROJA ANTES DEL GOL DE LA VENTANA: hay gol, pero no se cobra (disc. 16/24)
    _hid_r = dbmod.query_one("sad", "SELECT home_team_id FROM fixtures WHERE id=?", (con_ficha,))["home_team_id"]
    with _sq2.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, extra, tipo, detalle, equipo_id, jugador, jugador_id) "
                     "VALUES (?,?,?,?,?,?,?,?)", (con_ficha, 47, 0, "Card", "Red Card", _hid_r, "Expulsado", 777))
        _con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, extra, tipo, detalle, equipo_id, jugador) "
                     "VALUES (?,?,?,?,?,?,?)", (con_ficha, 46, 0, "Card", "Red Card", _hid_r, "DT expulsado"))
        _con.execute("INSERT INTO fixture_eventos (fixture_id, minuto, extra, tipo, detalle, equipo_id, jugador) "
                     "VALUES (?,?,?,?,?,?,?)", (con_ficha, 47, 2, "Goal", "Normal Goal", _hid_r, "Añadido 1T"))
    od_r = {b["equipo"]: b for b in c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]["tde"]["bloques"]}
    check("una roja de jugador antes del gol de la ventana: hay gol pero NO se cobra, y la roja del DT no cuenta",
          od_r["a"]["golEnVentana"] is True and od_r["a"]["cobrable"] is False
          and [r["jugador"] for r in od_r["a"]["rojasAntes"]] == ["Expulsado"], od_r["a"])
    check("la ventana sin roja previa se cobra normal", od_r["b"]["cobrable"] is True, od_r["b"])
    check("un gol del añadido del primer tiempo (45+2 guardado como 47) no cae en la 45-60",
          all(g["jugador"] != "Añadido 1T" for g in od_r["a"]["goles"]), od_r["a"]["goles"])
    # (17/10/2026) sin gol en la ventana, una roja ANTES de que termine tampoco
    # deja cobrar el «no hubo gol», y el añadido se anota solo en la ventana
    # que cierra su tiempo
    from backend.analisis import veredicto as _vd
    _g = [{"minuto": 49, "lado": "a", "jugador": "x", "autogol": False, "enAnadido": True, "baseAnadido": 45},
          {"minuto": 46, "lado": "b", "jugador": "y", "autogol": False, "enAnadido": True, "baseAnadido": 45}]
    _orig_g, _orig_r = _vd._goles, _vd._rojas
    _vd._goles = lambda fid, hid: _g
    _vd._rojas = lambda fid, hid: [{"minuto": 14, "lado": "b", "jugador": "Rojo"}]
    try:
        _p = {"tde": {"bloques": [{"equipo": "a", "ventana": "75-90'"}, {"equipo": "b", "ventana": "30-45'"}]}}
        _ob = {b["equipo"]: b for b in _vd.objetivo(con_ficha, _p)["tde"]["bloques"]}
    finally:
        _vd._goles, _vd._rojas = _orig_g, _orig_r
    check("sin gol en la ventana pero con una roja antes de que termine: no se cobra",
          _ob["a"]["golEnVentana"] is False and _ob["a"]["cobrable"] is False and _ob["a"]["rojasAntes"], _ob["a"])
    check("un gol del 45+4 se anota en la ventana que cierra el primer tiempo y no en la 75-90",
          _ob["b"]["golesEnAnadido"] and not _ob["a"]["golesEnAnadido"], (_ob["a"], _ob["b"]))
    with _sq2.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM fixture_eventos WHERE fixture_id=? AND jugador IN "
                     "('Expulsado', 'DT expulsado', 'Añadido 1T')", (con_ficha,))

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
    from backend.analisis.parte import dt_base_al_depositar as _dtb
    check("al depositar se guarda qué DT tenía la base", bool(_dtb(pasado["id"]).get("a")), _dtb(pasado["id"]))
    def _base_fue(nombre):  # qué decía la base al depositar (sellado en la primera vez)
        with _sq3.connect(os.path.join(tmp, "efe.db")) as _e:
            _e.execute("UPDATE parte_cowork SET dt_base_json=? WHERE fixture_id=?",
                       (json.dumps({"a": nombre}), pasado["id"]))
    # (17/10/2026) un parte que CONTRADIJO a la base con la prensa no copió un
    # DT rancio: si el banco de la API no le da la razón es «disputado», no cuarentena
    p_eq = _copy.deepcopy(p_lec)
    p_eq["equipos"]["a"]["dt"] = {"nombre": "Pablo Repetto", "desde": "2026-01-01"}
    c.post(f"{A}/analisis/cowork", json=p_eq)
    _base_fue("Mariano Messera")
    inv_d = c.get(f"{A}/analisis/cowork/lecciones").json()
    _todos_d = [i for s in inv_d["porSkill"] for i in s["items"]]
    check("el parte que contradijo a la base y no casa con el banco NO va a cuarentena: va como disputado",
          not [i for i in inv_d["enCuarentena"]["items"] if i["clave"].startswith(f"{pasado['id']}:")]
          and any(i["fixtureId"] == pasado["id"] and i["dtDisputado"] for i in _todos_d),
          [i.get("dtDisputado") for i in _todos_d if i["fixtureId"] == pasado["id"]])
    # el caso que la cuarentena SÍ atrapa (22/09): el parte copió el DT de la
    # base (Repetto) y en el banco se sentó otro (Dudamel)
    _base_fue("Pablo Repetto")
    inv_eq = c.get(f"{A}/analisis/cowork/lecciones").json()
    item_eq = [i for i in inv_eq["enCuarentena"]["items"] if i["clave"].startswith(f"{pasado['id']}:")]
    check("DT del parte (Repetto, copiado de la base) distinto del que se sentó en el banco (Dudamel) → cuarentena AUTOMÁTICA con los dos nombres",
          item_eq and all(i["cuarentenaAutomatica"] for i in item_eq)
          and "Repetto" in item_eq[0]["cuarentena"] and "Dudamel" in item_eq[0]["cuarentena"],
          [i.get("cuarentena") for i in item_eq] or inv_eq["enCuarentena"])
    # (20/10/2026, Atlante y Juárez) el parte declara CON FUENTE quién se sienta
    # en el banco: un DT suspendido no es un DT equivocado
    def _con_banco(banco):
        p_b = _copy.deepcopy(p_eq)
        p_b["equipos"]["a"]["dt"]["banco"] = banco
        r_b = c.post(f"{A}/analisis/cowork", json=p_b).json()
        _base_fue("Pablo Repetto")
        inv_b = c.get(f"{A}/analisis/cowork/lecciones").json()
        return (r_b, [i for i in inv_b["enCuarentena"]["items"] if i["clave"].startswith(f"{pasado['id']}:")],
                [d for s in inv_b["porSkill"] for i in s["items"] if i["fixtureId"] == pasado["id"]
                 for d in (i.get("dtDisputado") or [])])
    _r, _cu, _di = _con_banco({"motivo": "suspendido", "nombre": "Rafael Dudamel", "fuente": "prensa: sanción de 2 fechas"})
    check("DT suspendido declarado con fuente y en el banco el reemplazo que el parte nombró → ni cuarentena ni disputa",
          not _cu and not _di and c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["equipos"]["a"]["dt"]["banco"]["motivo"] == "suspendido",
          (_cu, _di))
    _r, _cu, _di = _con_banco({"motivo": "api_errada", "fuente": "ClaroSports 18/10: Lema en el banco"})
    check("la alineación de la API desmentida por la prensa → el caso no se aparta y viaja disputado con lo declarado",
          not _cu and any(d.get("bancoDeclarado", {}).get("motivo") == "api_errada" for d in _di), (_cu, _di))
    _r, _cu, _di = _con_banco({"motivo": "suspendido", "fuente": "x"})
    check("sin fuente, `dt.banco` se rechaza con motivo y la cuarentena sigue",
          any(x["donde"].endswith("dt.banco.fuente") for x in _r["rechazos"]) and _cu, (_r["rechazos"], _cu))
    _r, _cu, _di = _con_banco({"motivo": "lesion", "fuente": "prensa del partido"})
    check("un motivo fuera de la lista se rechaza", any(x["donde"].endswith("dt.banco.motivo") for x in _r["rechazos"]) and _cu,
          _r["rechazos"])
    # ── EL REVENTÓN DE UN PARTIDO YA JUGADO SE LEE «AL DÍA DEL PARTIDO» ──
    # (Sport Boys–Alianza Atlético 11/10: el GET del parte terminado metía ese
    # mismo partido en su burbuja y gritaba un K-EXTREMO que Cowork no vio)
    _rc_p = c.get(f"{A}/analisis/cowork/{pasado['id']}").json()["lecturaSad"]["reventonCalculado"]
    _fxp = dbmod.query_one("sad", "SELECT home_team_id FROM fixtures WHERE id=?", (pasado["id"],))
    _bur = c.get(f"{A}/equipos/{_fxp['home_team_id']}/burbujas?antesDe={pasado['id']}").json()
    check("el reventón del parte de un partido jugado es el mismo que /burbujas?antesDe (sin ese partido)",
          (_rc_p.get("a") or {}).get("actual") == _bur["familias"]["total"]["actual"],
          ((_rc_p.get("a") or {}).get("actual"), _bur["familias"]["total"]["actual"]))
    # ── EL BANCO DE LA API TAMBIÉN SE EQUIVOCA (Jaguares 11/10: «H. Bodhert», ido el 28/09) ──
    _pid = pasado["id"]
    check("la lección en cuarentena dice qué lado y qué nombres chocaron",
          item_eq and item_eq[0]["dtEquivocado"] and item_eq[0]["dtEquivocado"][0]["lado"] == "a",
          item_eq[0].get("dtEquivocado") if item_eq else None)
    r_sin = c.post(f"{A}/analisis/cowork/{_pid}/banco-desmentido", json={"lado": "a", "fuente": "x"})
    r_otro = c.post(f"{A}/analisis/cowork/{_pid}/banco-desmentido",
                    json={"lado": "b", "fuente": "https://prensa.example/salida-del-dt"})
    check("desmentir el banco exige fuente, y solo en un lado que figure con DT equivocado (422)",
          r_sin.status_code == 422 and r_otro.status_code == 422, (r_sin.text[:120], r_otro.text[:120]))
    r_des = c.post(f"{A}/analisis/cowork/{_pid}/banco-desmentido",
                   json={"lado": "a", "fuente": "https://prensa.example/dudamel-se-fue", "nota": "salió dos semanas antes"})
    inv_des = c.get(f"{A}/analisis/cowork/lecciones").json()
    check("con el banco desmentido el caso sale de la cuarentena automática, sin tocar el DT del parte",
          r_des.status_code == 200 and r_des.json()["dtEquivocado"] == []
          and not any(i["clave"].startswith(f"{_pid}:") for i in inv_des["enCuarentena"]["items"])
          and c.get(f"{A}/analisis/cowork/{_pid}").json()["equipos"]["a"]["dt"]["nombre"] == "Pablo Repetto",
          r_des.text[:300])
    check("el GET del parte trae el desmentido con la fuente y el banco que traía la API",
          c.get(f"{A}/analisis/cowork/{_pid}").json()["bancoDesmentido"]["a"]["bancoDeLaApi"] == "R. Dudamel",
          c.get(f"{A}/analisis/cowork/{_pid}").json().get("bancoDesmentido"))
    c.delete(f"{A}/analisis/cowork/{_pid}/banco-desmentido/a")
    check("quitar el desmentido devuelve el caso a la cuarentena",
          any(i["clave"].startswith(f"{_pid}:") for i in
              c.get(f"{A}/analisis/cowork/lecciones").json()["enCuarentena"]["items"]))
    from backend import app as _app_mod
    check("desmentir el banco y descartar una cohorte NO están abiertos a Cowork",
          not _app_mod._cowork_puede("POST", f"{A}/analisis/cowork/{_pid}/banco-desmentido")
          and not _app_mod._cowork_puede("POST", f"{A}/analisis/cowork/cohortes/rodaje/descartar"))
    # ── DESCARTE EN BLOQUE de una cohorte vieja (113 pendientes de rodaje/c2 al 12/10) ──
    from backend.analisis import parte as _pm_desc, lecciones as _lec_desc
    check("la cohorte vigente no se descarta en bloque (422) y una sin casos da 404",
          c.post(f"{A}/analisis/cowork/cohortes/vigente/descartar", json={}).status_code == 422
          and c.post(f"{A}/analisis/cowork/cohortes/{_pm_desc.COHORTE}/descartar", json={}).status_code == 422
          and c.post(f"{A}/analisis/cowork/cohortes/c9-no-existe/descartar", json={}).status_code == 404)
    with _pm_desc._conectar() as _cn:
        _cn.execute("UPDATE parte_cowork SET cohorte='c2-2026-09-19' WHERE fixture_id=?", (_pid,))
    r_desc = c.post(f"{A}/analisis/cowork/cohortes/c2-2026-09-19/descartar", json={"nota": "no calibra"})
    _vieja = c.get(f"{A}/analisis/cowork/lecciones?cohorte=c2-2026-09-19").json()
    _todas_c2 = [i for i in _vieja["items"] + _vieja["enCuarentena"]["items"] if i["cohorte"] == "c2-2026-09-19"]
    check("descartar la cohorte vieja pasa TODAS sus pendientes a descartada, cuarentena incluida",
          r_desc.status_code == 200 and r_desc.json()["descartadas"] >= 1
          and _todas_c2 and all(i["estado"] == "descartada" for i in _todas_c2),
          (r_desc.text[:200], [(i["clave"], i["estado"]) for i in _todas_c2]))
    with _pm_desc._conectar() as _cn:
        _cn.execute("UPDATE parte_cowork SET cohorte=? WHERE fixture_id=?", (_pm_desc.COHORTE, _pid))
    with _lec_desc._conectar() as _cn:
        _cn.executemany("DELETE FROM leccion_estado WHERE clave=?", [(k,) for k in r_desc.json().get("claves", [])])
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
    # ── fase A: antecedentes (solo partidos ANTERIORES) ──
    fx_pas = dbmod.query_one("sad", "SELECT id, date, home_team_id FROM fixtures WHERE id=?", (pasado["id"],))
    posterior = dbmod.query_one(
        "sad", "SELECT id FROM fixtures WHERE (home_team_id=? OR away_team_id=?) AND date > ? "
               "ORDER BY date LIMIT 1", (fx_pas["home_team_id"], fx_pas["home_team_id"], fx_pas["date"]))
    if posterior:
        an = c.get(f"{A}/analisis/cowork/antecedentes/{posterior['id']}").json()
        lado_eq = "a" if an["a"]["equipoId"] == fx_pas["home_team_id"] else "b"
        prev = [p_ for p_ in an[lado_eq]["partes"] if p_["fixtureId"] == pasado["id"]]
        check("antecedentes: el partido posterior del equipo trae el parte anterior con su marcador, "
              "veredicto y lección",
              prev and prev[0]["marcador"] and "veredicto" in prev[0] and "leccion" in prev[0]
              and {"aciertoCiego", "leccionesVigentes"} <= set(an[lado_eq]), an[lado_eq])
    an_propio = c.get(f"{A}/analisis/cowork/antecedentes/{pasado['id']}").json()
    check("antecedentes: NUNCA el partido que se analiza ni uno posterior (anti-hindsight)",
          all(p_["fixtureId"] != pasado["id"] and p_["fecha"] <= str(fx_pas["date"])[:10]
              for l in ("a", "b") for p_ in an_propio[l]["partes"]), an_propio)
    # LA MISMA RESPUESTA, LEYENDO SOLO DOS EQUIPOS (11/10/2026: de 30 s a más de
    # 2 min por armar el inventario entero). Referencia: la cuarentena y las
    # lecciones vigentes como las ve el inventario completo.
    from backend.analisis import antecedentes as _ant, lecciones as _lec_a
    _cuar_ref = {c_["fixtureId"]: (c_.get("cuarentena") or {}).get("motivo", "")
                 for c_ in _lec_a._casos() if c_.get("cuarentena")}
    _inv_ref = _lec_a.inventario()
    # UN PARTE DEPOSITADO PARA OTRA FECHA VA A CUARENTENA AUTOMÁTICA (incidencia 371)
    from backend.analisis.parte import _conectar as _con_p
    _c0 = next((c_ for c_ in _lec_a._casos() if not c_.get("cuarentena")), None)
    if _c0:
        with _con_p() as _cp:
            _f0 = _cp.execute("SELECT fecha FROM parte_cowork WHERE fixture_id=?", (_c0["fixtureId"],)).fetchone()["fecha"]
            _cp.execute("UPDATE parte_cowork SET fecha=date(?, '-7 day') WHERE fixture_id=?", (_f0, _c0["fixtureId"]))
        try:
            _c1 = next(c_ for c_ in _lec_a._casos() if c_["fixtureId"] == _c0["fixtureId"])
            check("parte de un partido que se movió 7 días: cuarentena automática con el motivo y los días",
                  (_c1.get("cuarentena") or {}).get("automatica") and (_c1["cuarentena"].get("parteDeOtraFecha") or 0) >= 6
                  and "sin rehacerse" in _c1["cuarentena"]["motivo"], _c1.get("cuarentena"))
        finally:
            with _con_p() as _cp:
                _cp.execute("UPDATE parte_cowork SET fecha=? WHERE fixture_id=?", (_f0, _c0["fixtureId"]))
    _iguales = True
    for _fid in {pasado["id"], *( [posterior["id"]] if posterior else [] )}:
        _an = _ant.antecedentes(_fid)
        for _l in ("a", "b"):
            for _p in _an[_l]["partes"]:
                _iguales &= _p["cuarentena"] == (_cuar_ref.get(_p["fixtureId"]) or "")
            _ref = sorted(i["clave"] for i in _inv_ref["items"]
                          if i["equipo"] == _an[_l]["equipo"] and i["estado"] in ("pendiente", "en_revision")
                          and str(i["fecha"]) < _an["partido"]["fecha"])
            _iguales &= sorted(v["clave"] for v in _an[_l]["leccionesVigentes"]) == _ref
    check("antecedentes acotado a los dos equipos da la misma cuarentena y las mismas lecciones "
          "que el inventario completo", _iguales)
    check("antecedentes abiertos a Cowork (GET) y 404 si el fixture no existe",
          appmod._cowork_puede("GET", A + f"/analisis/cowork/antecedentes/{pasado['id']}")
          and c.get(f"{A}/analisis/cowork/antecedentes/999999999").status_code == 404)

    # ── fase D: el dossier de revisión de un skill ──
    from backend.analisis import lecciones as _lec
    from backend.analisis.parte import COHORTE as _COH
    d_vacio = c.get(f"{A}/analisis/cowork/revision/skill-que-no-existe").json()
    check("dossier de un skill sin lecciones: existe false, no abierta, con el flujo declarado",
          d_vacio["existe"] is False and d_vacio["abierta"] is False and len(d_vacio["flujo"]) == 5, d_vacio)
    check("el dossier trae la versión vigente del snapshot del skill (la que va en aplicadaEn)",
          c.get(f"{A}/analisis/cowork/revision/teorema-del-echado").json()["versionVigente"].startswith("v0."))
    def _caso_d(k, regla, modo="tde"):
        return {"fixtureId": 870000 + k, "fecha": "2026-09-20", "equipoA": f"A{k}", "equipoB": f"B{k}",
                "parte": {}, "cohorte": _COH, "cuarentena": None,
                "veredicto": {"seleccion": "por_resultado", "modoEvaluacion": "PRE", "acredita": False,
                              "porLado": {"a": {"veredicto": "fallo", "skill": "teorema-del-echado",
                                                "leccion": f"lección {k}", "reglaTocada": regla, "queP": "x"}}},
                "modoFallo": {"lados": {"a": {"modo": modo, "proponeMoverNumero": True}}}}
    _casos_orig = _lec._casos
    _lec._casos = lambda limite=400: [_caso_d(1, "C1"), _caso_d(2, "C1"), _caso_d(3, "SOB2"),
                                      _caso_d(4, "C1", "varianza")]
    try:
        dd = c.get(f"{A}/analisis/cowork/revision/teorema-del-echado").json()
        check("4 fallos con lección pendiente del mismo skill → revisión ABIERTA",
              dd["abierta"] is True and dd["fallosPendientes"] == 4 and len(dd["lecciones"]) == 4, dd.get("lectura"))
        check("agrupado por la regla que tocan, la más cargada primero, con su modo de fallo",
              [(r["regla"], r["lecciones"]) for r in dd["porRegla"]] == [("C1", 3), ("SOB2", 1)]
              and dd["porRegla"][0]["porModoFallo"] == {"tde": 2, "varianza": 1}, dd["porRegla"])
        check("todos contaminados (por_resultado) → la lectura dice que SOLO puede fijar rúbrica",
              "solo puede FIJAR RÚBRICA" in dd["lectura"] and dd["porRegla"][0]["acreditables"] == 0, dd["lectura"])
        check("los 4 piden mover un número sin poder sostenerlo: la alarma del dossier los lista",
              len(dd["pidenMoverSinPoder"]) == 4, len(dd["pidenMoverSinPoder"]))
        check("abrir la revisión NO está abierto a Cowork ni a la web; leer el dossier sí (Cowork)",
              not appmod._cowork_puede("POST", A + "/analisis/cowork/revision/teorema-del-echado/abrir")
              and appmod._cowork_puede("GET", A + "/analisis/cowork/revision/teorema-del-echado"))
        ab = c.post(f"{A}/analisis/cowork/revision/teorema-del-echado/abrir").json()
        dd2 = c.get(f"{A}/analisis/cowork/revision/teorema-del-echado").json()
        check("abrir pasa las 4 a en_revision; siguen en el dossier y un segundo abrir no mueve nada",
              len(ab["movidas"]) == 4 and dd2["enRevision"] == 4 and len(dd2["lecciones"]) == 4
              and c.post(f"{A}/analisis/cowork/revision/teorema-del-echado/abrir").json()["movidas"] == [], ab)
    finally:
        _lec._casos = _casos_orig
    check("abrir una revisión no disparada → 422 con el motivo",
          c.post(f"{A}/analisis/cowork/revision/skill-que-no-existe/abrir").status_code == 422)

    # ── DTP estructurado (skill diagnostico-tactico) ──
    from backend.analisis import dtp_cowork as dtpc
    check("checklist: 3+ a la izquierda → improvisado, 55-65', C1 del TDE = 1",
          dtpc.clasificar_bloque({"p1": "improvisado", "p2": "improvisado", "p3": "improvisado",
                                  "p4": "estructural", "p5": "estructural"})["clase"] == "improvisado"
          and dtpc.clasificar_bloque({"p1": "izq", "p2": "izq", "p3": "izq"})["c1Tde"] == 1.0)
    moq = dtpc.clasificar_bloque({"p1": "estructural", "p2": "estructural", "p3": "estructural",
                                  "p4": "estructural", "p5": "estructural", "p6": "no"})
    check("Moquegua: 5 de 5 estructural con la p6 en no → estructural NO PROBADO, 80-90, alerta SÍ, C1 0.5",
          moq["clase"] == "estructural no probado" and moq["vidaUtilMin"] == "80-90"
          and moq["alertaDegradacion"] is True and moq["c1Tde"] == 0.5, moq)
    sin_caso = dtpc.clasificar_bloque({"p1": "der", "p2": "der", "p3": "der", "p6": "si"})
    check("p6 en sí pero sin caso concreto nombrado → sigue no probado (sin prueba no se suprime la alerta)",
          sin_caso["clase"] == "estructural no probado", sin_caso)
    hull = dtpc.clasificar_bloque({"p1": "der", "p2": "der", "p3": "der", "p4": "der", "p5": "izq",
                                   "p6": "si", "casoP6": "1-0 ante el Leeds con 20 min en desventaja"})
    check("estructural y probado con caso nombrado → estructural, alerta suprimida, C1 0",
          hull["clase"] == "estructural" and hull["alertaDegradacion"] is False and hull["c1Tde"] == 0.0, hull)
    amb = dtpc.clasificar_bloque({"p1": "izq", "p2": "izq", "p3": "der", "p4": "der"})
    check("2-2 con una sin dato → ambiguo: las dos lecturas, sin C1",
          amb["clase"] == "ambiguo" and amb["c1Tde"] is None and "dos" in amb["motivo"], amb)
    check("checklist vacío → sin clase ni minutos (el skill prohíbe dar vida útil sin clasificar)",
          dtpc.clasificar_bloque({})["clase"] == "" and dtpc.clasificar_bloque({})["vidaUtilMin"] == "")

    # insumos calculados, sobre un partido cuyo equipo tiene ficha del anterior
    fx_dtp = dbmod.query_one(
        "sad", "SELECT f.id FROM fixtures f WHERE f.status_short='NS' AND EXISTS ("
               "SELECT 1 FROM alineaciones a JOIN fixtures g ON g.id=a.fixture_id "
               "WHERE a.team_id IN (f.home_team_id, f.away_team_id) AND g.date < f.date) "
               "ORDER BY f.date DESC LIMIT 1")
    fx_dtp = fx_dtp["id"] if fx_dtp else sin_ficha
    ins = c.get(f"{A}/analisis/cowork/dtp/{fx_dtp}")
    check("GET /analisis/cowork/dtp/{id}: insumos por lado, noCalculables y nota", ins.status_code == 200
          and {"a", "b", "noCalculables", "nota"} <= set(ins.json()), ins.text[:300])
    ia = ins.json()["a"]
    pa = ia.get("partidoAnterior")
    check("el partido anterior trae marcador, goles con minuto y la posesión atada al rival y al marcador",
          pa is None or ({"marcador", "goles", "posesion", "xi"} <= set(pa)
                         and pa["posesion"]["rival"] == pa["rival"] and "marcadorFinal" in pa["posesion"]),
          pa and {k: pa[k] for k in ("marcador", "posesion")})
    check("el DTP del partido abierto a Cowork (GET) y 404 si el fixture no existe",
          appmod._cowork_puede("GET", A + f"/analisis/cowork/dtp/{fx_dtp}")
          and c.get(f"{A}/analisis/cowork/dtp/999999999").status_code == 404)
    check("estado por tiempo desde los minutos de gol (0-1 al 30, 1-1 al 60)",
          dtpc._estado_por_tiempo([{"minuto": 30, "extra": 0, "aFavor": False},
                                   {"minuto": 60, "extra": 0, "aFavor": True}])
          == {"ganando": 0, "empatando": 60, "perdiendo": 30, "dominante": "empatando"})

    # el DTP en el parte: normaliza, calcula la clase al leer, entra a la cadena
    ns_dtp = next((f["id"] for f in dbmod.query("sad", "SELECT id FROM fixtures WHERE status_short='NS' "
                                                        "ORDER BY date DESC LIMIT 40")
                   if c.get(f"{A}/analisis/cowork/{f['id']}").status_code == 404), sin_ficha)
    p_dtp = _parte(ns_dtp)
    p_dtp["dtp"] = {"bloques": [
        {"equipo": "a",
         "apertura": {"m1": {"sistema": "4-3-3", "senalXi": "plan ofensivo"},
                      "m2": {"choqueSistemas": "4-3-3 vs 5-3-2",
                             "duelosCarril": [{"carril": "derecha", "duelo": "extremo vs carrilero", "mismatch": "velocidad"}],
                             "checklistBloqueRival": {"p1": "estructural", "p2": "estructural", "p3": "estructural",
                                                      "p4": "estructural", "p5": "estructural", "p6": "no"},
                             "restDefense": {"foco": "dos centrales y pivote", "rival": "sin seguro"},
                             "posesion": {"valor": "60%", "contraQuien": "rival que cede", "marcador": "empatado"},
                             "veredicto": "matchup favorable"},
                      "m3Fases": [{"tramo": "0-25", "plan": "aguantar", "palancas": ["pelota parada"]},
                                  {"tramo": "90+", "plan": "tramo inventado"}]},
         "cierre": {"m4Goles": [{"gol": "1-0", "minuto": 17, "via": "pelota parada",
                                 "responsablesError": [{"jugador": "X", "nivel": "principal"}]}],
                    "mecanismoAbierto": {"activo": True, "mecanismo": "rechace de córner no atacado"}}},
        {"equipo": "c", "apertura": {}},
    ]}
    r_dtp = c.post(f"{A}/analisis/cowork", json=p_dtp).json()
    check("el recibo trae el DTP: lado, clase del bloque rival calculada y apertura en la cadena",
          r_dtp.get("dtp", {}).get("lados") == ["a"]
          and r_dtp["dtp"]["claseBloqueRival"] == {"a": "estructural no probado"}
          and r_dtp["dtp"]["aperturaEnCadena"], r_dtp.get("dtp"))
    check("un bloque con equipo inválido se rechaza con motivo",
          any(x["donde"].startswith("dtp.bloques[1]") for x in r_dtp["rechazos"]), r_dtp["rechazos"])
    from backend.analisis.dtp_cowork import normalizar_dtp as _ndtp
    _rch: list = []
    _ndtp({"bloques": [{"equipo": "a", "apertura": {"m2": {"checklistBloqueRival": {
        "p1": "der", "p2": "improvisado", "p3": "bloque bajo", "p4": "sin dato", "p6": "tal vez"}}}}]}, _rch)
    check("checklist: izq/der e improvisado/estructural entran; un valor fuera de la lista se rechaza con motivo (321)",
          sorted(x["donde"].rsplit(".", 1)[1] for x in _rch) == ["p3", "p6"], _rch)
    g_dtp = c.get(f"{A}/analisis/cowork/{ns_dtp}").json()["dtp"]["bloques"][0]
    check("GET: el bloque vuelve normalizado (tramo inválido fuera, vía canónica, veredicto sin «MATCHUP»)",
          [f["tramo"] for f in g_dtp["apertura"]["m3Fases"]] == ["0-25"]
          and g_dtp["cierre"]["m4Goles"][0]["via"] == "pelota_parada"
          and g_dtp["apertura"]["m2"]["veredicto"] == "FAVORABLE", g_dtp["apertura"]["m3Fases"])
    check("GET: la clase del bloque rival se CALCULA al leer, del lado del rival, con su C1 para el TDE",
          g_dtp["calculado"]["bloqueRival"]["clase"] == "estructural no probado"
          and g_dtp["calculado"]["bloqueRival"]["equipoDelBloque"] == "b"
          and g_dtp["calculado"]["bloqueRival"]["c1Tde"] == 0.5, g_dtp["calculado"])
    # DTP v1.4: el carril en las dos direcciones, el duelo condicional al once,
    # el mecanismo sin mecánica y el caso de la pregunta 6 del bloque propio
    from backend.analisis.dtp_cowork import normalizar_dtp as _ndtp4, casos_bloque as _casos_b
    _b4 = _ndtp4({"bloques": [{"equipo": "a", "apertura": {"m2": {"duelosCarril": [
        {"carril": "izquierda", "duelo": "Pilios vs Alisson", "mismatch": "Pilios sube",
         "vuelta": "su espalda queda para Alisson", "condicional": True}]}},
        "cierre": {"mecanismoAbierto": {"activo": True, "sinMecanica": True},
                   "casoBloque": {"sostuvo": True, "caso": "1-0 sostenido 50' ante un obligado", "conUnoMenos": True}}}]},
        [])["bloques"][0]
    _d4 = _b4["apertura"]["m2"]["duelosCarril"][0]
    check("DTP v1.4: el duelo guarda su vuelta y si es condicional; el mecanismo, sinMecanica; el cierre, su caso del bloque",
          _d4["vuelta"] and _d4["condicional"] is True and _b4["cierre"]["mecanismoAbierto"]["sinMecanica"] is True
          and _b4["cierre"]["casoBloque"]["sostuvo"] is True and _b4["cierre"]["casoBloque"]["conUnoMenos"] is True, _b4)
    p_cb = _copy.deepcopy(p_dtp)
    p_cb["dtp"]["bloques"][0]["cierre"]["casoBloque"] = {"sostuvo": False, "caso": "perdió el 1-0 en 4' ante un obligado"}
    c.post(f"{A}/analisis/cowork", json=p_cb)
    _fx_cb = dbmod.query_one("sad", "SELECT home_team_id, away_team_id, date FROM fixtures WHERE id=?", (ns_dtp,))
    _cb_a = _casos_b(_fx_cb["home_team_id"], "2100-01-01", dias=100000)
    _cb_b = _casos_b(_fx_cb["away_team_id"], "2100-01-01", dias=100000)
    check("casosBloque devuelve el caso al MISMO equipo foco (no al rival) y nunca uno posterior al partido",
          any(x["deParte"] == ns_dtp and x["sostuvo"] is False for x in _cb_a)
          and not any(x["deParte"] == ns_dtp for x in _cb_b)
          and not any(x["deParte"] == ns_dtp for x in _casos_b(_fx_cb["home_team_id"], "2000-01-01")),
          (_cb_a, _cb_b))
    c.post(f"{A}/analisis/cowork", json=p_dtp)
    from backend.analisis import db as _efedb_dtp
    fxn = dbmod.query_one("sad", "SELECT ht.name AS a FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
                                 "WHERE f.id=?", (ns_dtp,))
    esl = _efedb_dtp.eslabon_de_fixture(fxn["a"], ns_dtp) or {}
    check("la apertura estructurada entra en cadena_dtp (el próximo parte la cierra contra esto)",
          (esl.get("apertura") or {}).get("fuente") == "cowork"
          and esl["apertura"]["bloqueRival"]["clase"] == "estructural no probado", esl.get("apertura"))
    p_dtp2 = _copy.deepcopy(p_dtp)
    p_dtp2["dtp"]["bloques"][0]["apertura"]["m1"]["sistema"] = "5-4-1"
    r_dtp2 = c.post(f"{A}/analisis/cowork", json=p_dtp2).json()
    check("re-depositar NO pisa la apertura de la cadena: manda la primera, y el recibo lo dice",
          (_efedb_dtp.eslabon_de_fixture(fxn["a"], ns_dtp) or {})["apertura"]["m1"]["sistema"] == "4-3-3"
          and r_dtp2["dtp"]["aperturaNoGuardada"], r_dtp2.get("dtp"))
    # ── herencia DTP → TDE: C1 del bloque rival y SOB2 del rest defense ──
    p_her = _copy.deepcopy(p_dtp)
    p_her["dtp"]["bloques"][0]["apertura"]["m2"]["restDefense"].update({"nivelFoco": "pivote fijo",
                                                                         "nivelRival": "sin seguro"})
    ind_h = {"F1": 1, "F2": 0.5, "F3": 1, "F4": 0, "C1": 0, "C2": 0.5, "C3": 0,
             "P1a": 1, "P1b": 0.5, "P2": 0, "S1": 1, "S2": 0.5, "SOB1": 0.5, "SOB2": 0, "SOB3": 0.5}
    p_her["tde"] = {"bloques": [{"equipo": "a", "indicadores": dict(ind_h)},
                                {"equipo": "b", "indicadores": dict(ind_h)}]}
    c.post(f"{A}/analisis/cowork", json=p_her)
    lect_h = c.get(f"{A}/analisis/cowork/{ns_dtp}").json()
    tb = {b["equipo"]: b for b in lect_h["tde"]["bloques"]}
    her_b = {h["indicador"]: h for h in tb["b"].get("heredadoDtp") or []}
    check("C1 del TDE de b = 0.5: lo hereda de la clase «no probado» que calculó el DTP de a (Cowork había puesto 0)",
          tb["b"]["indicadores"]["C1"] == 0.5 and her_b["C1"]["declarado"] == 0 and her_b["C1"]["discrepa"], her_b)
    check("SOB2 de b = 1 (sin seguro, leído desde el DTP de a) y SOB2 de a = 0 (pivote fijo, de su propio DTP)",
          tb["b"]["indicadores"]["SOB2"] == 1.0 and tb["a"]["indicadores"]["SOB2"] == 0.0
          and not any(h["indicador"] == "C1" for h in tb["a"].get("heredadoDtp") or []), tb["a"].get("heredadoDtp"))
    check("la discrepancia heredada sale como alerta HERENCIA-DTP del lado b, y la de SOB2 de a no (coincidía)",
          any(x["codigo"] == "HERENCIA-DTP" and x["equipo"] == "b" and "C1" in x["detalle"] for x in lect_h["alertas"])
          and not any(x["codigo"] == "HERENCIA-DTP" and x["equipo"] == "a" for x in lect_h["alertas"]),
          [x for x in lect_h["alertas"] if x["codigo"] == "HERENCIA-DTP"])
    check("el índice del TDE de b se calcula YA con lo heredado (el ISE sube con SOB2 = 1)",
          tb["b"]["ise"] is not None and tb["a"]["ise"] is not None and tb["b"]["ise"] > tb["a"]["ise"],
          (tb["a"].get("ise"), tb["b"].get("ise")))
    # bloque AMBIGUO: C1 no se hereda, y heredadoDtp lo dice (Slovan, 302)
    from backend.analisis.dtp_cowork import herencia_tde as _her_tde
    from backend.analisis.parte import _heredar as _heredar_p
    _amb = _her_tde({"bloques": [{"equipo": "a", "apertura": {"m2": {"checklistBloqueRival": {
        "p1": "izq", "p2": "izq", "p3": "der", "p4": "der", "p5": "sin dato"}, "restDefense": {}}}}]})
    _hb = _heredar_p({"equipo": "b", "indicadores": {"C1": 0.5, "C2": 0}}, _amb["b"])
    check("con el bloque ambiguo C1 queda el declarado y heredadoDtp lo dice (noHeredado, sin discrepancia)",
          _hb["indicadores"]["C1"] == 0.5 and _hb["heredadoDtp"][0]["noHeredado"]
          and not _hb["heredadoDtp"][0]["discrepa"] and "ambiguo" in _hb["heredadoDtp"][0]["de"], _hb)
    r_eco_h = c.post(f"{A}/analisis/cowork", json={**lect_h, "fixtureId": ns_dtp}).json()
    check("el eco del GET no arrastra HERENCIA-DTP como alerta declarada",
          not any("alertas[" in x["donde"] for x in r_eco_h["rechazos"]), r_eco_h["rechazos"])
    p_dtp3 = _copy.deepcopy(p_dtp)
    del p_dtp3["dtp"]
    r_dtp3 = c.post(f"{A}/analisis/cowork", json=p_dtp3).json()
    check("un re-depósito sin el DTP lo delata en `perdido`",
          any(x.startswith("bloquesDtp") for x in r_dtp3["perdido"]), r_dtp3["perdido"])

    # EL DTP A REHACER: el once oficial contradice la apertura (9 de 24 el 11/10)
    _hid_d = dbmod.query_one("sad", "SELECT home_team_id FROM fixtures WHERE id=?", (con_ficha,))["home_team_id"]
    _form = dbmod.query_one("sad", "SELECT formacion FROM alineaciones WHERE fixture_id=? AND team_id=? LIMIT 1",
                            (con_ficha, _hid_d))["formacion"]
    _xi = [r["jugador"] for r in dbmod.query("sad", "SELECT jugador FROM alineaciones WHERE fixture_id=? "
                                                     "AND team_id=? AND titular=1", (con_ficha, _hid_d))]
    p_reh = _parte(con_ficha)
    p_reh["dtp"] = {"bloques": [{"equipo": "a", "apertura": {"m1": {
        "sistema": "3-5-2 con carrileros",
        "xiReferencia": "Arquero; Uno, Dos, Tres; Cuatro, Cinco, Seis, Siete, Ocho; Nueve, Diez"}}}]}
    c.post(f"{A}/analisis/cowork", json=p_reh)
    g_reh = c.get(f"{A}/analisis/cowork/{con_ficha}").json()
    from backend.analisis.dtp_cowork import rehacer as _rehacer
    _alt = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-2-3-1 / 4-3-3"}}},
                    {"a": {"formacion": "4-3-3", "titulares": []}})
    _no = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-2-3-1 / 4-3-3"}}},
                   {"a": {"formacion": "3-5-2", "titulares": []}})
    check("una apertura con dos sistemas («4-2-3-1 / 4-3-3») no pide rehacer si salió con cualquiera; "
          "con otro, sí", _alt["rehacer"] is False and _no["rehacer"] is True, (_alt, _no))
    # Huracán–Gimnasia y Estudiantes–Flamengo (16/10/2026): dos avisos falsos
    _fam = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-2-2-2"}}},
                    {"a": {"formacion": "4-4-2", "titulares": []}})
    _fam_no = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3"}}},
                       {"a": {"formacion": "4-4-2", "titulares": []}})
    check("«4-2-2-2» y «4-4-2» son el mismo sistema (misma línea de atrás y de arriba); «4-3-3» y «4-4-2» no",
          _fam["rehacer"] is False and _fam_no["rehacer"] is True, (_fam, _fam_no))
    # Atlético-MG (17/10/2026): «3-4-3 / 5-4-1» y salió 3-4-2-1; «4-3-3» y salió 4-2-3-1
    check("«3-4-3» y «3-4-2-1», «4-3-3» y «4-2-3-1» son la misma forma (línea de atrás y puntas)",
          _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "3-4-3 / 5-4-1"}}},
                   {"a": {"formacion": "3-4-2-1", "titulares": []}})["rehacer"] is False
          and _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3"}}},
                       {"a": {"formacion": "4-2-3-1", "titulares": []}})["rehacer"] is False)
    _ref = "Muslera; Mancuso, Núñez, Rojo, Benedetti; Piovi, Castro, B. Gallego; Palacios, Carrillo, Burgos"
    # SIN XI DE REFERENCIA (Rayo Zuliano, Puerto Cabello, 18/10/2026): no hay ausentes que contar
    _onze = ["A. Uno", "B. Dos", "C. Tres", "D. Cuatro", "E. Cinco", "F. Seis", "G. Siete", "H. Ocho",
             "I. Nueve", "J. Diez", "K. Once"]
    _sr = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-4-2",
                    "xiReferencia": "sin dato: no hay XI capturado en la base para esta liga, se espera la ficha"}}},
                   {"a": {"formacion": "4-4-2", "titulares": _onze}})
    check("con «sin XI de referencia» no se cuentan ausentes ni se pide rehacer por el once",
          _sr["ausentesDeLaReferencia"] == [] and _sr["rehacer"] is False and _sr["sinReferencia"] is True, _sr)
    # Villa (17/10/2026): lo que `senalXi` ya anunciaba no es sorpresa
    _an = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3", "xiReferencia": _ref,
                                                       "senalXi": "entran Onana, Bogarde y Maatsen por rotación"}}},
                   {"a": {"formacion": "4-3-3", "titulares": ["A. Onana", "L. Bogarde", "I. Maatsen", "F. Muslera"]}})
    check("los cambios que la apertura anunció en senalXi no cuentan como ausentes de la referencia",
          _an["ausentesDeLaReferencia"] == [] and _an["rehacer"] is False, _an)
    # Liverpool (20/10/2026, 334): una alternativa entre paréntesis no es el once anunciado
    _par = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3", "xiReferencia": _ref,
                     "senalXi": "Rojo (o Tsimikas), Burgos (o Gakpo/Ngumoha); entra Onana"}}},
                    {"a": {"formacion": "4-3-3", "titulares": ["K. Tsimikas", "C. Gakpo", "R. Ngumoha", "A. Onana",
                                                               "F. Muslera"]}})
    check("las alternativas entre paréntesis de senalXi no cuentan como anunciadas (sí lo que se anuncia fuera)",
          sorted(_par["ausentesDeLaReferencia"]) == ["C. Gakpo", "K. Tsimikas", "R. Ngumoha"]
          and _par["rehacer"] is True, _par)
    _al = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3", "xiReferencia": _ref + ", Abde"}}},
                   {"a": {"formacion": "4-3-3", "titulares": ["A. Ezzalzouli"], "alias": {"A. Ezzalzouli": ["Abde Ezzalzouli"]}}})
    check("el nombre de la plantilla (con el apodo) también casa con la referencia", _al["ausentesDeLaReferencia"] == [], _al)
    _dos = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3", "xiReferencia": _ref}}},
                    {"a": {"formacion": "4-3-3", "titulares": ["Baltasar Gallego Rodríguez", "Fernando Muslera"]}})
    check("un titular con dos apellidos casa con la referencia por cualquiera de ellos",
          _dos["ausentesDeLaReferencia"] == [], _dos)
    # la primera palabra también nombra (contraElOnce, 18-19/10/2026)
    _pi = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3",
                    "xiReferencia": _ref + ", C. Nunes, Gabriel, Otávio"}}},
                   {"a": {"formacion": "4-3-3", "titulares": ["Nunes Cesar", "Gabriel Magalhães",
                                                              "Otávio Eleodoro Rezende Costa", "Juan Desconocido"]}})
    check("«Nunes Cesar», «Gabriel Magalhães» y «Otávio Eleodoro…» casan por la primera palabra; un «Juan» no",
          _pi["ausentesDeLaReferencia"] == ["Juan Desconocido"], _pi)
    # (17/10/2026) Quirós/Quiroz y la ficha sin formación (Atlas con línea de 4)
    _sz = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-4-2", "xiReferencia": _ref.replace("Rojo", "Quiroz")}}},
                   {"a": {"formacion": "4-4-2", "titulares": ["C. Quirós"]}})
    check("«Quirós» en la ficha casa con «Quiroz» en la referencia", _sz["ausentesDeLaReferencia"] == [], _sz)
    # GRUPO 2 DE INCIDENCIAS (22/10/2026)
    # 260: «entraron Bambú y Meraz por Mora y Galindo» no anuncia a Mora; «B. Duarte o Villanueva» no anuncia a Villanueva
    _sal = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3", "xiReferencia": _ref,
                     "senalXi": "entraron Bambú y Meraz por Mora y Galindo; B. Duarte o Villanueva"}}},
                    {"a": {"formacion": "4-3-3", "titulares": ["F. Mora", "Bambú", "J. Villanueva", "F. Muslera"]}})
    check("260: el que sale («por Mora») y la alternativa sin paréntesis («o Villanueva») no cuentan como anunciados",
          sorted(_sal["ausentesDeLaReferencia"]) == ["F. Mora", "J. Villanueva"], _sal)
    # 152: el seguro de atrás en el banco
    _seg = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "3-4-2-1", "xiReferencia": _ref},
                                                 "m2": {"restDefense": {"foco": "fijo en Lobotka por delante de la línea de tres"}}}},
                    {"a": {"formacion": "3-4-2-1", "titulares": ["F. Muslera"], "banca": ["S. Lobotka", "Otro Suplente"]}})
    check("152: si el rest defense se apoyaba en un jugador que arrancó en el banco, el bloque se rehace",
          _seg["rehacer"] is True and any("Lobotka" in m for m in _seg["motivos"]), _seg)
    _seg_ok = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "3-4-2-1", "xiReferencia": _ref},
                                                    "m2": {"restDefense": {"foco": "fijo en Lobotka"}}}},
                       {"a": {"formacion": "3-4-2-1", "titulares": ["S. Lobotka", "F. Muslera"], "banca": ["Otro Suplente"]}})
    check("y si el del seguro es titular, no", _seg_ok["rehacer"] is False, _seg_ok)
    # 163: la referencia con varias proyecciones se avisa
    _mez = _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3",
                     "xiReferencia": _ref + "; SI proyecta a E. Gómez; Milenio, a Herrera y Simeone"}}},
                    {"a": {"formacion": "4-3-3", "titulares": ["F. Muslera"]}})
    check("163: una referencia que cita proyecciones de varias fuentes se marca mezclada",
          _mez["referenciaMezclada"] is True and _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": "4-3-3",
          "xiReferencia": _ref}}}, {"a": {"formacion": "4-3-3", "titulares": []}})["referenciaMezclada"] is False, _mez)
    # 137: con el grid completo, la línea de atrás es la fila 2 aunque la API etiquete «M» a dos de ella
    import backend.analisis.dtp_cowork as _dcm
    _orig = (_dcm._fixture, _dcm._titulares, _dcm._banca)
    _xi137 = ([{"player_id": 1, "jugador": "Arquero", "posicion": "G", "grid": "1:1"}]
              + [{"player_id": 10 + k, "jugador": f"Def {k}", "posicion": "D" if k < 2 else "M", "grid": f"2:{k + 1}"} for k in range(4)]
              + [{"player_id": 20 + k, "jugador": f"Med {k}", "posicion": "M", "grid": f"3:{k + 1}"} for k in range(4)]
              + [{"player_id": 30 + k, "jugador": f"Del {k}", "posicion": "F", "grid": f"4:{k + 1}"} for k in range(2)])
    try:
        _dcm._fixture = lambda fx: {"home_team_id": 1, "away_team_id": 2}
        _dcm._titulares = lambda fx, tid: _xi137 if tid == 1 else []
        _dcm._banca = lambda fx, tid: []
        _of137 = _dcm.oficial_de(1638786)
    finally:
        _dcm._fixture, _dcm._titulares, _dcm._banca = _orig
    check("137: con grid, los defensores son la fila 2 (4), no los etiquetados «D» (2)",
          _of137["a"]["defensores"] == 4, _of137.get("a"))
    from backend.analisis.dtp_cowork import alertas_rehacer as _alr
    _als = _alr({"bloques": [{"equipo": "a", "calculado": {"contraElOnce": {"rehacer": False, "sinReferencia": True}}},
                             {"equipo": "b", "calculado": {"contraElOnce": {"rehacer": False, "sinReferencia": False}}}]},
                {"a": "Aston Villa", "b": "Viking"})
    check("365: sin XI de referencia y con once oficial, DTP-SIN-REFERENCIA (tipo dato) para ese lado y solo ese",
          [(a["codigo"], a["equipo"], a["tipo"]) for a in _als] == [("DTP-SIN-REFERENCIA", "a", "dato")], _als)
    _sin = lambda sis, d: _rehacer({"equipo": "a", "apertura": {"m1": {"sistema": sis}}},
                                   {"a": {"formacion": "", "titulares": [], "defensores": d}})["rehacer"]
    check("sin formación en la ficha, una línea de 4 contra una apertura de 5 pide rehacer; 3 contra 5 no",
          _sin("5-3-2", 4) is True and _sin("5-3-2", 3) is False and _sin("4-4-2", 4) is False)
    check("y el campo de ausentes explica qué lista", "OFICIAL" in _sz.get("nota", ""), _sz)
    ce = g_reh["dtp"]["bloques"][0]["calculado"]["contraElOnce"]
    check("con el once oficial distinto, el bloque del DTP queda a rehacer (sistema y once)",
          ce["rehacer"] is True and ce["sistemaOficial"] == _form and len(ce["motivos"]) == 2
          and len(ce["ausentesDeLaReferencia"]) >= 3, ce)
    check("y la alerta DTP-REHACER va a la tira",
          any(a["codigo"] == "DTP-REHACER" and a["equipo"] == "a" for a in g_reh["alertas"]), g_reh["alertas"])
    p_reh["dtp"]["bloques"][0]["apertura"]["m1"] = {"sistema": _form, "xiReferencia": ", ".join(_xi)}
    c.post(f"{A}/analisis/cowork", json=p_reh)
    g_ok = c.get(f"{A}/analisis/cowork/{con_ficha}").json()
    check("con el sistema y el once de la ficha, no hay nada que rehacer",
          g_ok["dtp"]["bloques"][0]["calculado"]["contraElOnce"]["rehacer"] is False
          and not any(a["codigo"] == "DTP-REHACER" for a in g_ok["alertas"]),
          g_ok["dtp"]["bloques"][0]["calculado"])
    c.post(f"{A}/analisis/cowork", json=p_dtp)
    sin_once = c.get(f"{A}/analisis/cowork/{ns_dtp}").json()["dtp"]["bloques"][0]["calculado"]
    check("sin once oficial no se dice nada (no es «cuadra»)", "contraElOnce" not in sin_once, sin_once)
    r_eco_reh = c.post(f"{A}/analisis/cowork", json={**g_reh, "fixtureId": con_ficha}).json()
    check("el eco del GET no arrastra DTP-REHACER ni F1-DECISIVO-FUERA como declaradas",
          not any("alertas[" in x["donde"] for x in r_eco_reh["rechazos"]), r_eco_reh["rechazos"])
    c.post(f"{A}/analisis/cowork", json=_parte(con_ficha))

    # LA TABLA F1 DESDE LA BASE: 14+ decisivos faltaron el 11/10
    f1 = c.get(f"{A}/analisis/cowork/f1/{con_ficha}").json()
    cand = f1["a"]["candidatos"]
    check("la tabla F1 de la base trae candidatos con jugadorId, zona y rol sugerido",
          cand and all(x["jugadorId"] and x["rolSugerido"] in ("TF", "TH", "ROT", "SUP") for x in cand)
          and cand[0]["rolSugerido"] == "TF", cand[:2])
    dec = [x for x in cand if x["decisivo"]]
    check("y marca los decisivos con su porqué", dec and all(x["decisivo"] for x in dec), dec[:2])
    check("un fixture que no existe da 404", c.get(f"{A}/analisis/cowork/f1/1").status_code == 404)
    g_f1 = c.get(f"{A}/analisis/cowork/{con_ficha}").json()
    al_f1 = [a for a in g_f1["alertas"] if a["codigo"] == "F1-DECISIVO-FUERA" and a["equipo"] == "a"]
    check("un decisivo fuera de la tabla F1 depositada dispara F1-DECISIVO-FUERA",
          al_f1 and dec[0]["nombre"] in al_f1[0]["detalle"], al_f1)
    # UNO QUE YA SE FUE DEL CLUB NO ES UN DECISIVO DE HOY (Medellín, 17/10/2026)
    import sqlite3 as _sq3f
    _tid_f1 = dbmod.query_one("sad", "SELECT home_team_id, date FROM fixtures WHERE id=?", (con_ficha,))
    with _sq3f.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("CREATE TABLE IF NOT EXISTS traspasos (player_id INTEGER NOT NULL, fecha TEXT NOT NULL, tipo TEXT, "
                     "team_in INTEGER, team_in_nombre TEXT, team_out INTEGER, team_out_nombre TEXT, PRIMARY KEY (player_id, fecha))")
        _con.execute("INSERT OR REPLACE INTO traspasos VALUES (?, '2000-01-01', 'Transfer', 999999, 'Otro club', ?, 'este')",
                     (dec[0]["jugadorId"], _tid_f1["home_team_id"]))
    al_f1s = [a for a in c.get(f"{A}/analisis/cowork/{con_ficha}").json()["alertas"]
              if a["codigo"] == "F1-DECISIVO-FUERA" and a["equipo"] == "a"]
    check("un decisivo con salida registrada del club ya no dispara F1-DECISIVO-FUERA",
          not any(dec[0]["nombre"] in a["detalle"] for a in al_f1s), al_f1s)
    with _sq3f.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM traspasos WHERE fecha='2000-01-01'")
    p_f1 = _parte(con_ficha)
    p_f1["equipos"]["a"]["plantel"] += [{"nombre": "Otro Nombre", "jugadorId": x["jugadorId"], "zona": x["zona"] or "MID",
                                         "rol": x["rolSugerido"], "apps": x["apps"]} for x in dec]
    c.post(f"{A}/analisis/cowork", json=p_f1)
    g_f1b = c.get(f"{A}/analisis/cowork/{con_ficha}").json()
    # MINUTOS QUE NO CABEN EN LOS PARTIDOS (J. García, Tigres, 20/10/2026: 1 partido y 1.708 min)
    from backend import jugadores as _jugm
    _hid = _tid_f1["home_team_id"]
    _pl = _jugm.plantilla_de(_hid)
    _vic = _pl["jugadores"][-1]
    with _sq3f.connect(os.path.join(tmp, "sad.db")) as _con:
        _bk = _con.execute("SELECT rowid, partidos, titularidades, minutos FROM jugador_stats WHERE player_id=? AND team_id=?",
                           (_vic["id"], _hid)).fetchall()
        _con.execute("UPDATE jugador_stats SET partidos=0, titularidades=0, minutos=0 WHERE player_id=? AND team_id=?",
                     (_vic["id"], _hid))
        _con.execute("UPDATE jugador_stats SET partidos=1, titularidades=1, minutos=99999 WHERE rowid=?", (_bk[0][0],))
    _pl2 = {j["id"]: j for j in _jugm.plantilla_de(_hid)["jugadores"]}
    _f1g = [x for x in c.get(f"{A}/analisis/cowork/f1/{con_ficha}").json()["a"]["candidatos"] if x["jugadorId"] == _vic["id"]]
    check("1 partido con 99.999 minutos: el dato crudo viaja marcado y el % se cuenta con lo que cabe (no es decisivo)",
          _pl2[_vic["id"]].get("minutosIncoherentes") and _pl2[_vic["id"]]["pctMinutos"] < 0.2
          and max(j["pctMinutos"] for j in _pl2.values()) == 1.0
          and not any(x["decisivo"].startswith("titular habitual") for x in _f1g), (_pl2[_vic["id"]], _f1g))
    with _sq3f.connect(os.path.join(tmp, "sad.db")) as _con:
        for _r in _bk:
            _con.execute("UPDATE jugador_stats SET partidos=?, titularidades=?, minutos=? WHERE rowid=?", (_r[1], _r[2], _r[3], _r[0]))
    # EL ÚLTIMO ONCE ENTRA ENTERO a la tabla F1 (Boca, Cúcuta, Fortaleza: 20/10/2026)
    from backend.analisis.f1_base import onces_recientes as _orec, tabla_equipo as _tabla_eq
    # un once nuevo con los de MENOS minutos de la temporada (los que el corte de 16 dejaba fuera)
    _cola = _jugm.plantilla_de(_hid)["jugadores"][-11:]
    with _sq3f.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("INSERT INTO fixtures (id, date, home_team_id, away_team_id, status_short, status_long) "
                     "VALUES (990777, '2099-12-31T20:00:00+00:00', ?, ?, 'FT', 'Match Finished')", (_hid, _hid + 1))
        for _j in _cola:
            _con.execute("INSERT INTO alineaciones (fixture_id, team_id, player_id, jugador, titular) VALUES (990777, ?, ?, ?, 1)",
                         (_hid, _j["id"], _j["nombre"]))
    _rec = _orec(_hid, "2100-01-01")
    _ult = {pid for pid, r in _rec["jugadores"].items() if r["enUltimo"] and pid > 0}
    import backend.analisis.f1_base as _f1m
    _cand_antes, _f1m.CANDIDATOS = _f1m.CANDIDATOS, 3   # que el corte deje fuera a los del once
    try:
        _ids_f1 = {x["jugadorId"] for x in _tabla_eq(_hid, "local", "2100-01-01")["candidatos"]
                   if x.get("titularEnElUltimo")}
    finally:
        _f1m.CANDIDATOS = _cand_antes
    _f1n = {x["jugadorId"]: x for x in _tabla_eq(_hid, "local", "2100-01-01")["candidatos"]}
    check("con el nombre de la base en la alineación, la tabla F1 no trae nombreEnLaHoja",
          not any(x.get("nombreEnLaHoja") for x in _f1n.values()), [x for x in _f1n.values() if x.get("nombreEnLaHoja")])
    with _sq3f.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("UPDATE alineaciones SET jugador='Dayan Pérez' WHERE fixture_id=990777 AND player_id=?", (_cola[0]["id"],))
    _f1n = {x["jugadorId"]: x for x in _tabla_eq(_hid, "local", "2100-01-01")["candidatos"]}
    check("si la alineación lo llama distinto que la base, la fila trae nombreEnLaHoja (335)",
          _f1n[_cola[0]["id"]].get("nombreEnLaHoja") == "Dayan Pérez", _f1n.get(_cola[0]["id"]))
    check("los titulares del último once están todos en la tabla F1, marcados",
          _rec["onces"] > 0 and _ult and _ult <= _ids_f1, (_rec["onces"], _ult, _ids_f1))
    with _sq3f.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM alineaciones WHERE fixture_id=990777")
        _con.execute("DELETE FROM fixtures WHERE id=990777")
    # DECISIVO DE LA TEMPORADA CON 0 DE 10 EN LOS ÚLTIMOS ONCES (Ameliano/Cerro, incidencia 45)
    _dec_all = _f1m.decisivos(_jugm.plantilla_de(_hid))
    _orig_rec = _f1m.onces_recientes
    _vic_d = _dec_all[0]["id"]
    _otros = [j["id"] for j in _jugm.plantilla_de(_hid)["jugadores"] if j["id"] != _vic_d][:11]
    _f1m.onces_recientes = lambda t, a: {"onces": 10, "ultimo": 1, "jugadores": {
        **{p: {"nombre": "x", "posicion": "M", "titular": 10, "convocado": 10, "enUltimo": True} for p in _otros},
        _vic_d: {"nombre": "x", "posicion": "M", "titular": 0, "convocado": 10, "enUltimo": False}}}
    try:
        _t45 = {x["jugadorId"]: x for x in _tabla_eq(_hid, "local", "2100-01-01")["candidatos"]}
        _fal45 = _f1m.faltantes(_hid, [{"nombre": "Nadie", "jugadorId": 1}], "2100-01-01")
    finally:
        _f1m.onces_recientes = _orig_rec
    check("con 10 onces y 0 titularidades, el decisivo de la temporada pierde «decisivo», viaja en decisivoTemporada "
          "y no dispara F1-DECISIVO-FUERA",
          (_vic_d not in _t45 or (not _t45[_vic_d]["decisivo"] and "0 de 10" in _t45[_vic_d].get("decisivoTemporada", "")))
          and not any(f["jugadorId"] == _vic_d for f in _fal45), (_t45.get(_vic_d), _fal45))
    # GRUPO 4 DE INCIDENCIAS (22/10/2026): fuera del corte con stats (360) y la zona del último once (171, 323, 66, 359)
    _pl4 = _jugm.plantilla_de(_hid)["jugadores"]
    _fuera = next(j for j in reversed(_pl4) if j["posicion"] != "Defensa")
    _top = [j for j in _pl4 if j["id"] != _fuera["id"]][:3]
    _f1m.onces_recientes = lambda t, a: {"onces": 10, "ultimo": 1, "jugadores": {
        **{j["id"]: {"nombre": j["nombre"], "posicion": "M", "titular": 10, "convocado": 10, "enUltimo": False} for j in _top},
        _fuera["id"]: {"nombre": _fuera["nombre"], "posicion": "D", "posicionReciente": "D", "titular": 3,
                       "convocado": 10, "enUltimo": False}}}
    _c4, _f1m.CANDIDATOS = _f1m.CANDIDATOS, 3
    try:
        _t4 = {x["jugadorId"]: x for x in _tabla_eq(_hid, "local", "2100-01-01")["candidatos"]}
    finally:
        _f1m.onces_recientes, _f1m.CANDIDATOS = _orig_rec, _c4
    check("360: el que quedó fuera del corte pero está en la plantilla entra CON sus stats, no «sin stats de temporada»",
          _fuera["id"] in _t4 and not _t4[_fuera["id"]].get("sinStatsDeTemporada")
          and _t4[_fuera["id"]]["apps"] == _fuera["partidos"], _t4.get(_fuera["id"]))
    check("171/323: la zona es la del último once en que fue titular (D → DEF) y la de la temporada queda aparte",
          _t4[_fuera["id"]]["zona"] == "DEF" and _t4[_fuera["id"]].get("zonaTemporada"), _t4.get(_fuera["id"]))
    check("359: la posición en inglés tiene zona", _f1m._ZONA.get("Forward") == "ATK" and _f1m._ZONA.get("Goalkeeper") == "GK")
    # UN JUGADOR CON DOS IDS ES UNO (Leones del Norte, Nacional Potosí: 17-19/10/2026)
    from backend.analisis.f1_base import deduplicar as _dedup, mismo_jugador as _mj
    _js = [{"id": 362224, "nombre": "Emiliano Griffa", "minutos": 900, "partidos": 10},
           {"id": 566349, "nombre": "E. Griffa", "minutos": 0, "partidos": 0},
           {"id": 476417, "nombre": "S. Peña", "minutos": 300, "partidos": 5},
           {"id": 549618, "nombre": "S. Pena", "minutos": 0, "partidos": 0},
           {"id": 1, "nombre": "T. Palacios", "minutos": 500, "partidos": 6},
           {"id": 2, "nombre": "T. Palacios", "minutos": 200, "partidos": 3},
           {"id": 3, "nombre": "M. Quiñonez", "minutos": 0, "partidos": 0}]
    _q2, _ = _dedup([{"id": 538162, "nombre": "S. Córdoba", "minutos": 1200, "partidos": 15},
                     {"id": 64215, "nombre": "S. Cordoba", "minutos": 1200, "partidos": 15}], {})
    check("dos registros con el mismo nombre y las MISMAS stats son uno (Pasto, 194)", len(_q2) == 1, _q2)
    _q, _t = _dedup(_js, {566349: 2, 362224: 3, 3: 1})
    check("la copia sin minutos de un jugador se funde con su gemela y le suma las titularidades; "
          "dos con minutos y el mismo nombre quedan (pueden ser dos personas), y otra inicial no es la misma",
          {j["id"] for j in _q} == {362224, 476417, 1, 2, 3} and _t.get(362224) == 5 and 566349 not in _t
          and _mj("Y. Guzmán", "Y. Guzman") and not _mj("S. Quinonez", "M. Quiñonez"), (_q, _t))
    from backend.analisis.f1_base import _en_tabla as _f1_en_tabla
    check("el mismo jugador con dos ids y el apellido mal escrito («Juan Bizans» / «Juan Bisanz») está en la tabla",
          _f1_en_tabla({"id": 406291, "nombre": "Juan Bizans"}, [{"nombre": "Juan Bisanz", "jugadorId": 304371}]))
    check("pero otra pila con un apellido parecido es otra persona",
          not _f1_en_tabla({"id": 1, "nombre": "Juan Gomez"}, [{"nombre": "Pedro Gomes", "jugadorId": 2}]))
    check("con los decisivos en la tabla (por jugadorId), la alerta se va",
          not any(a["codigo"] == "F1-DECISIVO-FUERA" and a["equipo"] == "a" for a in g_f1b["alertas"]),
          [a for a in g_f1b["alertas"] if a["codigo"] == "F1-DECISIVO-FUERA"])
    c.post(f"{A}/analisis/cowork", json=_parte(con_ficha))

    # EL ROL SALE DE LOS ÚLTIMOS ONCES, NO DEL AÑO (Millonarios 13/10: el
    # Clausura mezclado con el Apertura) y un titular reciente sin stats entra
    import sqlite3 as _sq3
    _tid = dbmod.query_one("sad", "SELECT home_team_id FROM fixtures WHERE id=?", (con_ficha,))["home_team_id"]
    _fecha = dbmod.query_one("sad", "SELECT date FROM fixtures WHERE id=?", (con_ficha,))["date"]
    _prev = [r["id"] for r in dbmod.query(
        "sad", "SELECT id FROM fixtures WHERE (home_team_id=? OR away_team_id=?) AND date < ? "
               "AND status_short='FT' ORDER BY date DESC LIMIT 6", (_tid, _tid, _fecha))]
    _pl = [x["jugadorId"] for x in cand]
    _ultimo = _pl[-1]   # el de menos minutos: en los onces recientes es titular siempre
    with _sq3.connect(os.path.join(tmp, "sad.db")) as _con:
        for _f in _prev:
            for _pid in [_ultimo] + _pl[:9]:
                _con.execute("INSERT OR REPLACE INTO alineaciones (fixture_id, team_id, player_id, jugador, posicion, titular) "
                             "VALUES (?,?,?,?,?,1)", (_f, _tid, _pid, f"J{_pid}", "M"))
            _con.execute("INSERT OR REPLACE INTO alineaciones (fixture_id, team_id, player_id, jugador, posicion, titular) "
                         "VALUES (?,?,?,?,?,1)", (_f, _tid, 990001, "Fichaje Nuevo", "D"))
    f1r = c.get(f"{A}/analisis/cowork/f1/{con_ficha}").json()["a"]
    _por = {x["jugadorId"]: x for x in f1r["candidatos"]}
    check("con ≥ 5 onces recientes el rol sale de ahí (no de los minutos del año)",
          f1r["rolPor"].startswith("titularidades en los últimos 6")
          and _por[_ultimo]["rolSugerido"] == "TF" and _por[_ultimo]["titularEnUltimos"] == "6/6"
          and f1r["candidatos"][0]["titularEnUltimos"] == "6/6", f1r["candidatos"][:3])
    check("y un titular reciente sin stats de temporada entra a la tabla",
          _por.get(990001, {}).get("sinStatsDeTemporada") is True and _por[990001]["zona"] == "DEF",
          _por.get(990001))
    # el titular fijo de los onces que la temporada no trae también es decisivo (Robert Sánchez, Como)
    from backend.analisis.f1_base import faltantes as _falt
    _fl = _falt(_tid, [{"nombre": "Otro", "jugadorId": 1}], _fecha)
    check("un titular fijo de los últimos onces sin stats de temporada, fuera de la tabla, es decisivo que falta",
          any(f["jugadorId"] == 990001 and "6 de los últimos 6" in f["porQue"] for f in _fl), _fl)
    with _sq3.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute(f"DELETE FROM alineaciones WHERE fixture_id IN ({','.join('?' * len(_prev))})", _prev)

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
    # ── la matriz de escenarios: narrativa por equipo, sin números ──────────
    from backend.analisis.parte import _matriz, filas_matriz
    from backend.analisis.veredicto import matriz_objetivo
    _rz = []
    _m = _matriz({"a": {"gana": {"tactica central": "x", "pelota_parada": "y", "probabilidad": "40 %"},
                        "no perder": "z", "perder": {"error": "w", "inventada": "q", "prob": "mucha"}},
                  "b": "texto suelto", "confirma": "caso"}, _rz)
    check("la matriz entra por equipo y escenario con las palabras del skill y su probabilidad estimada; "
          "un escenario, una fila y una probabilidad que no es número se rechazan con motivo",
          _m == {"a": {"ganar": {"tactica": "x", "pelotaParada": "y", "probabilidad": 40.0},
                       "perder": {"errorSistemico": "w"}}, "confirma": "caso"}
          and {r["donde"] for r in _rz} >= {"matriz.a.no perder", "matriz.a.perder.inventada",
                                            "matriz.a.perder.prob", "matriz.b"}, (_m, _rz))
    from backend.analisis.parte import matriz_vs_pronostico
    _vs = matriz_vs_pronostico({"a": {"ganar": {"probabilidad": 52.0}, "perder": {"probabilidad": 30}},
                                "b": {"empatar": {"probabilidad": 27}}},
                               {"probabilidades": {"local": 52, "empate": 27, "visita": 21}})
    check("la probabilidad de la matriz se compara con el 1X2 del pronóstico: solo AVISA lo que se aparta "
          "más de 5 puntos (perder de a = visita)",
          [x["donde"] for x in _vs] == ["matriz.a.perder.probabilidad"] and _vs[0]["pronostico"] == 21.0, _vs)
    check("las filas de la matriz se cuentan (recibo y `perdido`)", filas_matriz(_m) == 3, filas_matriz(_m))
    _mo = matriz_objetivo({"a": {"perder": {"gatillo": "g"}}, "b": {"ganar": {"tactica": "t"}}}, "visita")
    check("el veredicto dice qué escenario jugó cada equipo y qué se había escrito para él, sin acierto",
          _mo["a"] == {"escenario": "perder", "escrito": {"gatillo": "g"}, "declarado": True}
          and _mo["b"]["escenario"] == "ganar" and "acerto" not in _mo["a"], _mo)
    _me = matriz_objetivo({"a": {"ganar": {"tactica": "t"}}}, "empate")
    check("un escenario sin escribir viaja como no declarado", _me["a"]["escenario"] == "empatar"
          and _me["a"]["declarado"] is False and _me["b"]["declarado"] is False, _me)

    from backend.analisis.parte import ensayo_cuenta_espina
    _esp = {"lecturaSad": {"espina": {"a": {"lectura": "positiva"}}}}
    check("el ensayo tiene que contar la espina: sin nombrarla ni a las burbujas, el recibo lo avisa",
          ensayo_cuenta_espina({**_esp, "documentos": [{"id": "ensayo", "cuerpo": "Huracán gana de local."}]}) is False
          and ensayo_cuenta_espina({**_esp, "documentos": [{"id": "ensayo", "cuerpo": "La burbuja de local crece."}]})
          and ensayo_cuenta_espina({"lecturaSad": {}, "documentos": [{"id": "ensayo", "cuerpo": "x"}]})
          and ensayo_cuenta_espina({**_esp, "documentos": []}))

    # ── la buena espina de la burbuja: la lectura del analista, medida ──────
    from backend.analisis.parte import _espina
    from backend.analisis.veredicto import espina_objetivo
    _rz = []
    check("la espina entra por lado (objeto o palabra, con las palabras del usuario) y una inventada se rechaza",
          _espina({"a": {"lectura": "Crece", "porque": "x"}, "b": "buena"}, _rz)
          == {"a": {"lectura": "positiva", "guia": "total", "porque": "x"}}
          and any(r["donde"] == "lecturaSad.espina.b.lectura" for r in _rz), (_rz,))
    _rz = []
    _eg = _espina({"a": {"lectura": "positiva", "guia": "K local"}, "b": {"lectura": "cero", "guia": "la tabla"}}, _rz)
    check("la guía de la espina: la K de la condición entra con las palabras del usuario, una inventada vuelve "
          "a la total con su motivo",
          _eg["a"]["guia"] == "condicion" and _eg["b"]["guia"] == "total"
          and any(r["donde"] == "lecturaSad.espina.b.guia" for r in _rz), (_eg, _rz))
    _eq = espina_objetivo({"b": {"lectura": "positiva", "guia": "condicion"}}, "visita")
    check("la espina guiada por la K de la condición se juzga con el mismo marcador y la guía viaja",
          _eq["b"]["cumplida"] is True and _eq["b"]["guia"] == "condicion", _eq)
    _eo = espina_objetivo({"a": {"lectura": "cero"}, "b": {"lectura": "positiva"}}, "empate")
    check("un empate deja la K en 0: acierta «cero» y no «positiva»",
          _eo["a"]["cumplida"] is True and _eo["b"]["cumplida"] is False and _eo["b"]["movimiento"] == "cero", _eo)
    _ev = espina_objetivo({"a": {"lectura": "negativa"}, "b": {"lectura": "positiva"}}, "visita")
    check("gana la visita: la K del local va a negativa y la del visitante crece",
          _ev["a"]["cumplida"] is True and _ev["b"]["cumplida"] is True and _ev["a"]["movimiento"] == "negativa", _ev)
    _en = espina_objetivo({"a": {"lectura": "neutra"}}, "visita")
    check("neutra no se juzga, y un lado sin espina tampoco",
          _en["a"]["cumplida"] is None and _en["a"]["resultado"] == "pierde" and _en["b"]["lectura"] is None, _en)
    # ── la espina de la TARJETA al lado del analista (19/10/2026) ──────────
    from backend.analisis import burbuja as _bb
    _rv = {"a": {"declarado": {"signo": "+", "riesgo": {"nivel": "bajo"}}},
           "b": {"declarado": {"signo": "-", "riesgo": {"nivel": "muy alto"}}}}
    _ta = _bb.espina_tarjeta("+", _bb._movimiento_esperado("total", "+", "bajo"))
    _tb = _bb.espina_tarjeta("-", _bb._movimiento_esperado("total", "-", "muy alto"))
    _et = espina_objetivo({"a": {"lectura": _ta["lectura"]},
                           "b": {"lectura": "cero" if _tb["lectura"] != "cero" else "positiva"}}, "local", _rv)
    check("el veredicto pone la espina de la tarjeta al lado del analista: la sigue o va contra ella, "
          "y cada una se cumple contra el mismo marcador",
          _et["a"]["tarjeta"]["lectura"] == _ta["lectura"] and _et["a"]["vsTarjeta"] == "sigue"
          and _et["b"]["vsTarjeta"] == "contra" and _et["a"]["tarjeta"]["nivel"] == "bajo"
          and _et["a"]["tarjeta"]["cumplida"] == (_ta["lectura"] == "positiva")
          and _et["b"]["tarjeta"]["cumplida"] == (_tb["lectura"] == "negativa"), _et)
    # Monza 4-0 Cagliari (19/10/2026): K total del Cagliari en 0, el parte leyó su K de VISITA
    _cg = {"b": {"condicion": {"actual": {"signo": "+"}, "riesgo": {"nivel": "medio"},
                               "espinaTarjeta": {"lectura": "negativa", "movimiento": "cambio", "prob": 0.379, "fuerza": "debil"}}}}
    _ec = espina_objetivo({"b": {"lectura": "cero", "guia": "condicion"}}, "local", {"b": {"declarado": None}}, _cg)
    check("con guía de la condición, la tarjeta del veredicto es la de la condición (Cagliari: «pierde», cumplida) y el parte fue contra ella",
          (_ec["b"]["tarjeta"] or {}).get("lectura") == "negativa" and _ec["b"]["tarjeta"]["cumplida"] is True
          and _ec["b"]["tarjeta"].get("guia") == "condicion" and _ec["b"]["vsTarjeta"] == "contra", _ec)
    # LA VENTANA QUE SE COBRA CON RAMA (veredictos del 19/10/2026)
    from backend.analisis.veredicto import ventana_a_cobrar, clase_ventana as _cv
    _r = {"rama": "siRecibePrimero", "minuto": 89, "loDeclarado": {"ventana": "60-75'"}}
    _t, _dr, _venc = ventana_a_cobrar({"ventana": "75-90'"}, _r)
    check("una rama que se abre al 89' con ventana 60-75' no tuvo tramo: se dice y no se cobra",
          _t == "60-75'" and _dr and "no se cobra" in _venc)
    _t2, _dr2, _v2 = ventana_a_cobrar({"ventana": "75-90'"}, {**_r, "minuto": 50})
    check("con la rama viva, la etiqueta es la de la rama", _t2 == "60-75'" and _dr2 and _v2 == "")
    # UN NOMBRE ROTO EN LA F1 SE LIMPIA, Y SI NO TIENE ARREGLO MANDA LA HOJA (incidencia 352)
    from backend.analisis.f1_base import nombre_sano
    check("F1: «A. MaksimoviÄ» (mojibake a medias) toma el nombre de la hoja; uno completo se repara; uno sano no cambia",
          nombre_sano("A. MaksimoviÄ", "A. Maksimović") == "A. Maksimović"
          and nombre_sano("R. ObriÄ\x87") == "R. Obrić" and nombre_sano("Alemão", "J. Tornich") == "Alemão")
    # UNA ALERTA DECLARADA CON TIPO «dato» SE GUARDA COMO «fecha», PERO SE DICE (incidencia 343)
    from backend.analisis.parte import _alerta
    _rz = []
    _al = _alerta({"codigo": "DIV-MOTOR-MERCADO", "equipo": "global", "tipo": "dato", "detalle": "72 contra 49"}, _rz, "alertas[0]")
    check("alerta declarada con tipo «dato»: queda «fecha» y el recibo lo dice",
          _al["tipo"] == "fecha" and any(r["donde"] == "alertas[0].tipo" for r in _rz), _rz)
    _rz2 = []
    _alerta({"codigo": "T.54", "equipo": "a", "tipo": "estructural", "detalle": "DT nuevo"}, _rz2, "alertas[1]")
    check("con un tipo válido no hay aviso", not _rz2, _rz2)
    # TDE v0.1.22 · CADA RAMA CON SU NÚMERO (Sporting 2-3 LASK: la rama decía «se expone» y el ISE quedó en 1.67)
    from backend.analisis.parte import _reasignacion as _rsg, ise_de_ramas as _idr, pronostico_vs_motor as _pvm
    _rz = []
    _ra = _idr(_rsg({"siLeEmpatan": {"sob1": 1, "sob2": 1, "nota": "vuelve a empujar"},
                     "siRecibePrimero": {"sob1": 1, "sob2": 0.5, "sob3": 1}, "siMarcaPrimero": {"sob1": 0}}, _rz, "t"),
               {"SOB1": 0, "SOB2": 0, "SOB3": 0.5})
    check("la rama con sob1 y sob2 trae su ISE (SOB3 del bloque, dicho); con las tres, sin heredados; sin sob2, sin ISE",
          _ra["siLeEmpatan"]["iseRama"] == 8.33 and _ra["siLeEmpatan"]["iseRamaHeredados"] == ["SOB3"]
          and _ra["siRecibePrimero"]["iseRama"] == 8.33 and "iseRamaHeredados" not in _ra["siRecibePrimero"]
          and "iseRama" not in _ra["siMarcaPrimero"] and not _rz, (_ra, _rz))
    _rz2 = []
    _rsg({"siLeEmpatan": {"sob1": 1, "sob2": 2}}, _rz2, "t")
    check("un sob2 fuera de 0/0.5/1 se rechaza con motivo", any(r["donde"] == "t.siLeEmpatan.sob2" for r in _rz2), _rz2)
    # EL AVISO DEL 1X2 SOBRE EL MOTOR CON LA ESCALA ENTRE LIGAS (Sporting–LASK: 66 contra 57)
    _pr = {"probabilidades": {"local": 66, "empate": 20, "visita": 14}}
    _ux = {"unXDos": {"local": 57.0, "empate": 24.0, "visita": 19.0}}
    _av = _pvm(_pr, {**_ux, "fiabilidadMu": {"nivel": "baja"}})
    check("con fiabilidad baja y el favorito 9 puntos SOBRE el motor, el recibo avisa; con fiabilidad alta solo informa",
          _av["sobreElMotor"] == 9.0 and "Sporting" in _av["aviso"]
          and _pvm(_pr, {**_ux, "fiabilidadMu": {"nivel": "alta"}})["aviso"] == ""
          and _pvm({"probabilidades": {"local": 60, "empate": 22, "visita": 18}}, {**_ux, "fiabilidadMu": {"nivel": "baja"}})["aviso"] == ""
          and _pvm(_pr, None) is None, _av)
    # EL REVENTÓN SE OBSERVA CON EL MARCADOR SI EL PIPELINE NO CORRIÓ (incidencias 100 y 373)
    from backend.analisis.veredicto import observado_por_marcador as _opm
    _dec = {"signo": "+", "k": 12.5, "partidos": 3}
    check("reventón por marcador: burbuja + que empata revienta (a cero), que gana sigue, que pierde revienta al otro signo",
          _opm(_dec, 2, 2)["revento"] and _opm(_dec, 2, 2)["signoDespues"] == "0"
          and not _opm(_dec, 1, 0)["revento"] and _opm(_dec, 1, 0)["partidos"] == 4
          and _opm(_dec, 0, 1)["revento"] and _opm(_dec, 0, 1)["kPico"] == 12.5)
    check("reventón por marcador: burbuja − sigue solo si pierde; sin marcador no se observa",
          not _opm({"signo": "-", "k": -4, "partidos": 2}, 0, 2)["revento"]
          and _opm({"signo": "-", "k": -4, "partidos": 2}, 1, 1)["revento"] and _opm(_dec, None, 1) is None)
    # UN PARTE DE OTRA FECHA DEL PARTIDO (incidencia 371)
    from backend.analisis.parte import dias_movido
    check("parte para el 14/10 de un partido jugado el 20/10: movido +6; el mismo día o al siguiente no cuenta",
          dias_movido("2026-10-14", "2026-10-20T01:30:00") == 6 and dias_movido("2026-10-14", "2026-10-15") is None
          and dias_movido("2026-10-14", "2026-10-14 20:00") is None and dias_movido(None, "2026-10-20") is None)
    # LA VENTANA DE LA RAMA RELATIVA AL GOL SE COBRA (incidencia 345, TDE v0.1.21)
    from backend.analisis.veredicto import rango_relativo
    check("«desde el gol +15» con el gol al 50' es el tramo 50-65; sin minuto o sin «+N» no hay tramo",
          rango_relativo("desde el gol +15", 50) == (50, 65) and rango_relativo("desde el gol +15", None) is None
          and rango_relativo("tras la ventaja", 50) is None and rango_relativo("75-90'", 50) is None)
    # GRUPO 1 DE INCIDENCIAS (22/10/2026): la ventana en palabras, la del reloj aparte y el tramo por tramo
    from backend.analisis.veredicto import rango_sin_gol, ancla_casa, ventana_reloj, tramos_por_marcador
    _v114 = "'los 15' posteriores al gol propio; sin gol, 75-90''"
    check("114: «los 15 posteriores al gol propio» con el gol propio al 68' es 68-83; sin goles vale el 75-90 del «sin gol»",
          rango_relativo(_v114, 68) == (68, 83) and rango_sin_gol(_v114) == (75, 90)
          and ancla_casa(_v114, "siMarcaPrimero") and not ancla_casa(_v114, "siRecibePrimero"))
    _g367 = [{"minuto": 77, "lado": "a"}]
    _r367 = ventana_reloj("75-90'", _g367, [], "a", True)
    check("367: la ventana del reloj se puntúa aparte con el gol que abrió la rama (77' en la 75-90)",
          _r367["golEnVentana"] is True and _r367["cobrable"] is True)
    # Real Sociedad–Málaga (incidencia 147): Real 1-0 al 59', 2-2... el partido en tramos con su rama
    _tde = {"ventana": "75-90'", "reasignacion": {"siMarcaPrimero": {"ventana": "60-75'"},
                                                 "siLeEmpatan": {"ventana": "desde el gol +15"}}}
    _gt = [{"minuto": 10, "lado": "a"}, {"minuto": 59, "lado": "b"}, {"minuto": 66, "lado": "a"}, {"minuto": 80, "lado": "a"}]
    _tr = tramos_por_marcador(_tde, _gt, "b")
    check("tramo por tramo: perdiendo → siRecibePrimero, empatado tras ir perdiendo → siIguala, perdiendo de nuevo, y empatado tras ganar → siLeEmpatan",
          [t["rama"] for t in _tr] == ["base", "siRecibePrimero", "siIguala", "siRecibePrimero", "siRecibePrimero"]
          and [t["marcador"] for t in _tr] == ["0-0", "0-1", "1-1", "1-2", "1-3"], [(t["rama"], t["marcador"]) for t in _tr])
    _gt2 = [{"minuto": 59, "lado": "b"}, {"minuto": 66, "lado": "a"}, {"minuto": 70, "lado": "a"}]
    _tr2 = tramos_por_marcador(_tde, _gt2, "b")
    check("ganando con su ventana 60-75 concede al 66 (golEnVentana) y el empate abre siLeEmpatan desde el 66 (+15)",
          [t["rama"] for t in _tr2] == ["base", "siMarcaPrimero", "siLeEmpatan", "siRecibePrimero"]
          and _tr2[1]["golEnVentana"] is True and _tr2[2]["rango"] == [66, 81] and _tr2[2]["golEnVentana"] is True,
          _tr2)
    _gs = [{"minuto": 20, "lado": "a"}, {"minuto": 60, "lado": "a"}, {"minuto": 81, "lado": "a"}, {"minuto": 86, "lado": "b"}]
    check("un 3 arriba alcanzado DENTRO de la ventana, antes del gol que se cobra, abandona la rama (Nacional 3-0 al 81', 3-1 al 86')",
          _cv(_gs, 86, "b")[0] == "rama_abandonada" and _cv(_gs, 75, "b")[0] == "")
    from backend.analisis.veredicto import tarjetas_partido
    _tm = {"a": {"tarjeta": {"lectura": "positiva", "fuerza": "debil"}}, "b": {"tarjeta": {"lectura": "negativa", "fuerza": "debil"}}}
    _tp = tarjetas_partido(_tm, "local")
    check("las dos tarjetas como 1X2: «el local gana» y «el visitante pierde» concuerdan en local, débiles las dos, y aciertan con el 4-0",
          _tp["estado"] == "concuerdan" and _tp["dicen"] == "local" and _tp["ambasDebiles"] and _tp["cumplida"] is True, _tp)
    _td = tarjetas_partido({"a": {"tarjeta": {"lectura": "positiva", "fuerza": "fuerte"}},
                            "b": {"tarjeta": {"lectura": "positiva", "fuerza": "debil"}}}, "visita")
    check("si discrepan no hay resultado de las tarjetas, y se dice cuál acertó; con una sola, manda esa",
          _td["estado"] == "discrepan" and _td["dicen"] is None and _td["aciertaA"] is False and _td["aciertaB"] is True
          and tarjetas_partido({"a": {}, "b": {"tarjeta": {"lectura": "cero", "fuerza": "debil"}}}, "empate")["cumplida"] is True
          and tarjetas_partido({}, "empate")["estado"] == "sin tarjetas", _td)
    _es = espina_objetivo({}, "empate", _rv)
    check("sin lectura del analista la tarjeta se mide igual (es su propia calibración) y no hay «vs»",
          _es["a"]["lectura"] is None and _es["a"]["tarjeta"] is not None and _es["a"]["vsTarjeta"] is None
          and espina_objetivo({"a": {"lectura": "neutra"}}, "local", _rv)["a"]["vsTarjeta"] is None, _es)
    check("sin burbuja declarada no hay tarjeta",
          espina_objetivo({"a": {"lectura": "positiva"}}, "local", {"a": {"declarado": None}})["a"]["tarjeta"] is None)
    from backend.analisis.parte import espina_vs_tarjeta
    _rt = {"a": {"espinaTarjeta": {"lectura": "positiva", "movimiento": "sigue", "prob": 0.6, "fuerza": "fuerte"},
                 "condicion": {"espinaTarjeta": {"lectura": "cero", "movimiento": "cero", "prob": 0.3, "fuerza": "debil"}}},
           "b": {"espinaTarjeta": {"lectura": "negativa", "movimiento": "cambio", "prob": 0.4, "fuerza": "debil"}}}
    _vt = espina_vs_tarjeta(_rt, {"a": {"lectura": "cero", "porque": "el TDE ve un partido cerrado"},
                                  "b": {"lectura": "positiva"}})
    check("ir contra la tarjeta FUERTE sin decirlo se cobra; contra la débil no (ahí deciden los skills)",
          [x["lado"] for x in _vt] == ["a"] and _vt[0]["dicho"] is False, _vt)
    check("dicho «contra la tarjeta porque…» ya no se cobra, y con guía condición manda la tarjeta de la condición",
          espina_vs_tarjeta(_rt, {"a": {"lectura": "cero", "porque": "contra la tarjeta porque el DTP…"}})[0]["dicho"]
          and espina_vs_tarjeta(_rt, {"a": {"lectura": "positiva", "guia": "condicion"}}) == [], _vt)
    from backend.analisis.lecciones import _cerrar_tarjeta, calibracion_espina
    _ct = _cerrar_tarjeta({"porFuerza": {"fuerte": {"lados": 4, "aciertos": 3}, "debil": {"lados": 0, "aciertos": 0}},
                           "porNivel": {"bajo": {"lados": 4, "aciertos": 3}},
                           "sigue": {"lados": 3, "aciertos": 2},
                           "contra": {"lados": 12, "aciertaAnalista": 4, "aciertaTarjeta": 7}})
    check("la calibración dice quién gana cuando el analista contradice a la tarjeta, con su n",
          _ct["porFuerza"]["fuerte"]["tasa"] == 0.75 and _ct["porFuerza"]["debil"]["tasa"] is None
          and _ct["analistaVaContra"]["lectura"].startswith("la tarjeta le gana"), _ct)
    from backend.analisis.lecciones import _sumar_tarjeta, _cerrar_tarjeta as _ct2
    _tz = {"porFuerza": {f: {"lados": 0, "aciertos": 0} for f in ("fuerte", "debil")}, "porNivel": {},
           "porTipo": {t: {f: {"lados": 0, "aciertos": 0} for f in ("fuerte", "debil")} for t in ("general", "local", "visita")},
           "sigue": {"lados": 0, "aciertos": 0}, "contra": {"lados": 0, "aciertaAnalista": 0, "aciertaTarjeta": 0}}
    _sumar_tarjeta(_tz, "b", {"tarjeta": {"lectura": "negativa", "fuerza": "debil", "cumplida": True, "guia": "condicion"}})
    _sumar_tarjeta(_tz, "a", {"tarjeta": {"lectura": "positiva", "fuerza": "fuerte", "cumplida": False}})
    _pt = _ct2(_tz)["porTipo"]
    check("la calibración separa la tarjeta general de la de local y la de visita",
          _pt is not None and set(_pt) == {"general", "local", "visita"}
          and _pt["visita"]["todas"]["lados"] == 1 and _pt["visita"]["todas"]["aciertos"] == 1
          and _pt["general"]["fuerte"]["lados"] == 1 and _pt["local"]["todas"]["lados"] == 0, _pt)
    # el objetivo de cada veredicto se guarda unos minutos (Aprendizaje tardaba 21 s, 20/10/2026)
    from backend.analisis import lecciones as _lmod
    _ttl, _orig = _lmod.OBJETIVO_TTL_S, _lmod.vered.objetivo
    _n = {"c": 0}
    def _cuenta(fid, parte):
        _n["c"] += 1
        return {"jugado": False}
    try:
        _lmod.OBJETIVO_TTL_S, _lmod.vered.objetivo = 600, _cuenta
        _lmod._OBJ_CACHE.clear()
        _lmod._objetivo(1, {"x": 1}); _lmod._objetivo(1, {"x": 1}); _lmod._objetivo(1, {"x": 2})
    finally:
        _lmod.OBJETIVO_TTL_S, _lmod.vered.objetivo = _ttl, _orig
        _lmod._OBJ_CACHE.clear()
    check("el objetivo se recalcula una vez por versión del parte: la segunda lectura sale guardada, "
          "un parte corregido se rehace", _n["c"] == 2, _n)
    _cal = calibracion_espina()
    check("GET de calibración: la tabla de la tarjeta, la del analista por lectura y cómo leerla",
          set(_cal) >= {"tarjeta", "analistaPorLectura", "comoLeerlo"}
          and set((_cal["tarjeta"] or {})) >= {"porFuerza", "porNivel", "analistaLaSigue", "analistaVaContra", "partido"}, _cal)
    esm = inv["acreditables"]["espina"]
    check("las lecciones miden la espina contra la frecuencia de cada movimiento y con pocos lados lo dicen",
          set(esm) >= {"positiva", "cero", "negativa", "neutra", "lectura"} and esm["lectura"] == "sin n"
          and "frecuenciaDelMovimiento" in esm["positiva"], esm)
    _pg = esm.get("porGuia") or {}
    check("y aparte por guía (K total · K de la condición), cada una con sus lados, que suman el total",
          set(_pg) == {"total", "condicion"} and _pg["condicion"]["lados"] > 0
          and _pg["total"]["lados"] + _pg["condicion"]["lados"] == esm["lados"], _pg)

    rvm = inv["acreditables"]["reventon"]
    check("las métricas traen la tasa de reventón por nivel de riesgo con el rango del backtest al lado",
          set(rvm["porNivel"]) >= {"bajo", "medio", "alto", "muy alto", "sin base"}
          and rvm["porNivel"]["muy alto"]["esperadoBacktest"] == [0.71, 0.75]
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
    check("la serie del reloj (sesgo tardío) viaja aparte y nunca cuenta más que lo observado",
          "reloj" in acr["ventanaTde"] and acr["ventanaTde"]["reloj"]["conGol"] <= acr["ventanaTde"]["reloj"]["observadas"],
          acr["ventanaTde"])

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
    from backend.analisis import tde as _tdem
    _sin_s = _tdem.indice({"F1": 1, "F2": 0.5, "C1": 1, "P1a": 1, "P2": 0.5,
                           "SOB1": 1, "SOB2": 0.5, "SOB3": 1})
    check("sin bloque S el IE sale parcial y el ISE igual (Rennes–Auxerre)",
          _sin_s.get("sinS") and _sin_s.get("ie") is not None and _sin_s.get("ise") == 8.33, _sin_s)
    _sin_c = _tdem.indice({"F1": 1, "F2": 0.5, "P1a": 1, "S1": 1, "SOB1": 1})
    check("sin bloque C (u otro que no sea S) el IE sigue sin calcularse; el ISE sale",
          _sin_c.get("sinDato") and _sin_c.get("ise") == 10.0, _sin_c)
    _bc = _parte_mod._bloque_calculado({"ie": 0.0, "ise": 0.0, "equipo": "a",
                                        "indicadores": {"F1": 1, "F2": 0.5, "C1": 1, "P1a": 1, "S1": 1, "SOB1": 1},
                                        "vias": [{"nombre": "ECHADA", "indice": 0.0},
                                                 {"nombre": "SOBREEXPOSICION", "indice": 3.0}]})
    check("un 0.0 declarado se lee como no declarado y las vías toman el índice calculado (la de 3.0 discrepa)",
          _bc["declarado"] == {"ie": None, "ise": None}
          and _bc["vias"][0]["indice"] == _bc["calculado"]["ie"]
          and _bc["vias"][1]["indice"] == _bc["calculado"]["ise"]
          and any("SOBREEXPOSICION" in x for x in _bc.get("discrepancia", [])), _bc)

    # EL ID CASA LO QUE EL NOMBRE NO (UTC–Cristal 11/10/2026): la API llama
    # «J. Cerro» a Joshua Cantt y «Cris Silva» a Cristiano
    t_id = [{"nombre": "Joshua Cantt", "zona": "MID", "rol": "ROT", "jugadorId": 354001},
            {"nombre": "Cristiano", "zona": "DEF", "rol": "TF", "jugadorId": 105501},
            {"nombre": "Luis Iberico", "zona": "ATK", "rol": "TF"}]
    # incidencia 223 (Torque, 21/10/2026): «S. Zampiero» en la hoja es «Santiago Zampieri» de la tabla
    _pz = [{"nombre": "Santiago Zampieri", "zona": "MID"}, {"nombre": "Juan Pérez", "zona": "DEF"}]
    check("bloque F: una letra cambiada en el apellido casa («S. Zampiero» = Santiago Zampieri) y otro apellido no",
          bf._buscar(_pz, "S. Zampiero") == [0] and bf._buscar(_pz, "S. Zampa") == []
          and bf._buscar(_pz, "J. Gomez") == [] and bf._buscar(_pz, "J. Peres") == [1], (bf._buscar(_pz, "S. Zampiero"), bf._buscar(_pz, "S. Zampa")))
    d_sin = bf.resolver(t_id, [], ["J. Cerro", "Cris Silva", "L. Iberico"])
    d_con = bf.resolver(t_id, [], ["J. Cerro", "Cris Silva", "L. Iberico"],
                        ids={"J. Cerro": 354001, "Cris Silva": 105501, "L. Iberico": 39646})
    check("por nombre «J. Cerro» y «Cris Silva» no casan con la tabla de la prensa",
          d_sin["casados"] == 1 and set(d_sin["noReconocidos"]) == {"J. Cerro", "Cris Silva"}, d_sin["noReconocidos"])
    check("con el jugadorId de la tabla y los ids de la ficha casan los tres (el sin id, por nombre)",
          d_con["casados"] == 3 and not d_con["noReconocidos"], (d_con["casados"], d_con["noReconocidos"]))
    # EL MISMO JUGADOR DOS VECES (Cúcuta 20/10/2026, 335): «D. Gelvez» con id y «Dayan Pérez» de prensa
    t_dup = [{"nombre": "D. Gelvez", "zona": "ATK", "rol": "ROT", "jugadorId": 555163},
             {"nombre": "Dayan Pérez", "zona": "ATK", "rol": "TH"},
             {"nombre": "Otro Delantero", "zona": "ATK", "rol": "TF"}]
    d_dup = bf.resolver(t_dup, [], ["Dayan Pérez", "Otro Delantero"], ids={"Dayan Pérez": 555163})
    _dp = next(j for j in d_dup["jugadores"] if j["nombre"] == "Dayan Pérez")
    check("la fila sin id que es el mismo jugador que una con id sale «duplicado» y no pesa (ATK sin reducción)",
          _dp["estado"] == "duplicado" and "D. Gelvez" in _dp["motivo"] and d_dup["reduccion"]["ATK"] == 0.0
          and d_dup["duplicados"] == ["Dayan Pérez"] and d_dup["ip"] == 0, (_dp, d_dup["reduccion"], d_dup["ip"]))
    d_nodup = bf.resolver(t_dup, [], ["Otro Delantero"], ids={})
    check("sin el jugador en la hoja, las dos filas siguen siendo bajas (no se inventa un duplicado)",
          [j["estado"] for j in d_nodup["jugadores"]][:2] == ["baja", "baja"] and not d_nodup["duplicados"], d_nodup["jugadores"])
    # DOS HOMÓNIMOS TITULARES (incidencia 372, Shakhtar: Pedrinho 10244 MID y 299925 DEF)
    from backend.analisis.parte import _ids_por_nombre
    _hoja = [{"jugador": "Pedrinho", "player_id": 10244}, {"jugador": "Pedrinho", "player_id": 299925},
             {"jugador": "Otro", "player_id": 5}]
    _idp = _ids_por_nombre(_hoja)
    check("la hoja con dos «Pedrinho» guarda los dos ids en orden", _idp == {"Pedrinho": [10244, 299925], "Otro": 5}, _idp)
    t_ped = [{"nombre": "Pedrinho", "zona": "MID", "rol": "TF", "jugadorId": 10244},
             {"nombre": "Pedrinho", "zona": "DEF", "rol": "TF", "jugadorId": 299925},
             {"nombre": "Otro", "zona": "ATK", "rol": "TF", "jugadorId": 5}]
    d_ped = bf.resolver(t_ped, [], ["Pedrinho", "Pedrinho", "Otro"], ids=_idp)
    check("los dos Pedrinho titulares quedan disponibles: sin baja fantasma ni IP",
          all(j["estado"] == "disponible" for j in d_ped["jugadores"]) and d_ped["ip"] == 0,
          ([(j["nombre"], j["estado"]) for j in d_ped["jugadores"]], d_ped["ip"]))
    d_duda = bf.resolver(t_id, [{"nombre": "Luis Iberico", "estado": "duda", "motivo": "molestia"}],
                         ["J. Cerro", "Cris Silva"], ids={"J. Cerro": 354001, "Cris Silva": 105501})
    _ib = next(j for j in d_duda["jugadores"] if j["nombre"] == "Luis Iberico")
    check("con el once resuelto, una duda que no figura en la hoja pasa a baja (con su motivo)",
          _ib["estado"] == "baja" and "molestia" in _ib["motivo"], _ib)
    t_br = [{"nombre": "Saúl Ñíguez", "zona": "MID", "rol": "TF"},
            {"nombre": "Paulo Henrique Ganso", "zona": "MID", "rol": "ROT"},
            {"nombre": "Breno Bidon", "zona": "MID", "rol": "TF"},
            {"nombre": "André", "zona": "MID", "rol": "TF"},
            {"nombre": "Saúl Pérez", "zona": "DEF", "rol": "SUP"}]
    d_br = bf.resolver(t_br[:4], [], ["Saúl", "Breno", "Andre"], ["PH Ganso", "André Ramalho"])
    _est = {j["nombre"]: j.get("hoja") for j in d_br["jugadores"]}
    check("la hoja con solo la pila casa («Saúl», «Breno»); las iniciales también («PH Ganso»)",
          _est["Saúl Ñíguez"] == "titular" and _est["Breno Bidon"] == "titular"
          and _est["Paulo Henrique Ganso"] == "banca", _est)
    check("un suplente que casa con un titular ya resuelto no lo pisa (André / André Ramalho)",
          _est["André"] == "titular" and d_br["f4"]["rotados"] == 0, (_est, d_br["f4"]))
    d_amb = bf.resolver(t_br, [], ["Saúl"])
    check("si dos jugadores comparten la pila, la hoja con solo la pila va a dudas",
          any("Saúl" in x for x in d_amb["dudas"]), d_amb["dudas"])
    _rech: list = []
    check("el parte acepta jugadorId en la tabla y rechaza uno que no es número",
          _parte_mod._jugador({"nombre": "Joshua Cantt", "zona": "MID", "rol": "ROT", "jugadorId": "354001"}, _rech, "t")["jugadorId"] == 354001
          and "jugadorId" not in _parte_mod._jugador({"nombre": "X Y", "zona": "MID", "rol": "ROT", "jugadorId": "abc"}, _rech, "t")
          and any("jugadorId" in r["porque"] for r in _rech), _rech)

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
    _camp = [j for j in d["jugadores"] if "Campos" in j["nombre"]]
    check("y ninguno de los dos homónimos queda de baja: uno jugó seguro (Pedrinho del Shakhtar, 17/10)",
          len(_camp) == 2 and all(j["estado"] == "disponible" for j in _camp) and d["homonimos"] == 2, _camp)

    # una duda pública pesa la mitad MIENTRAS no hay hoja (ramas)…
    r_duda = bf.ramas(tabla, [{"nombre": "Paolo Guerrero", "estado": "duda", "motivo": "molestia"}])
    check("sin hoja, la duda pesa la mitad que la baja", r_duda["a"]["ip"] == 1.5, r_duda["a"]["ip"])
    # …y con la hoja a la vista, si no figura, es baja con su motivo público
    d = bf.resolver(tabla, [{"nombre": "Paolo Guerrero", "estado": "duda", "motivo": "molestia"}],
                    ["A. Campos", "Zambrano", "Trauco", "Concha", "Ceppelini", "Barcos"], ["Valera"])
    check("con la hoja, la duda que no figura pesa como baja", d["ip"] == 3.0, d["ip"])
    check("y conserva su motivo público",
          any("molestia" in f["motivo"] for f in d["fuera"]), d["fuera"])

    check("F3 salta con EFE formado e impacto rojo",
          (bf.alerta_f3("FORMADO", "rojo") or {}).get("codigo") == "F3")
    check("F3 no salta si el impacto no es rojo", bf.alerta_f3("FORMADO", "ambar") is None)
    check("F3 salta con ≥ 2 titulares fijos ausentes aunque el IP no sea rojo (Juve 11/10)",
          "Yildiz" in ((bf.alerta_f3("FORMADO", "ambar", ["Yildiz", "Locatelli"]) or {}).get("detalle") or "")
          and bf.alerta_f3("FORMADO", "ambar", ["Yildiz"]) is None
          and bf.titulares_fijos_fuera([{"nombre": "A", "rol": "TF", "estado": "baja"},
                                        {"nombre": "B", "rol": "TH", "estado": "baja"},
                                        {"nombre": "C", "rol": "TF", "estado": "disponible"}]) == ["A"])

    # ── EL ESTUDIO DE LOS REVENTONES HACIA ATRÁS (13/10/2026) ────────────────
    from backend.analisis import reventones as rv
    check("una burbuja de 1 partido es ruido; de 3, candidata; de 2, solo sobre la mediana",
          not rv.significativo({"partidos": 1, "kPico": 99, "signo": "+"}, {"+": 2})
          and rv.significativo({"partidos": 3, "kPico": 0.1, "signo": "+"}, {"+": 2})
          and rv.significativo({"partidos": 2, "kPico": 3, "signo": "-"}, {"-": 2})
          and not rv.significativo({"partidos": 2, "kPico": 1, "signo": "-"}, {"-": 2}))
    # LA COMPOSICIÓN DE LA RACHA LA SABE LA BASE (primera tanda de Perú, 13/10):
    # rachas de la Copa de la Liga o de amistosos que revientan al volver la liga
    _fila = {"ligaId": 281, "condicion": "Visita"}
    _racha = [{"fixtureId": 1, "fecha": "2026-06-01", "ligaId": 1232, "condicion": "Local", "golesFavor": 2, "golesContra": 0},
              {"fixtureId": 2, "fecha": "2026-06-08", "ligaId": 667, "condicion": "Local", "golesFavor": 1, "golesContra": 0},
              {"fixtureId": 3, "fecha": "2026-06-15", "ligaId": 281, "condicion": "Visita", "golesFavor": 1, "golesContra": 0}]
    _comp = rv.composicion(_racha, _fila)
    check("racha de copa y amistoso que revienta en liga: racha_en_otra_competicion; 2 de 3 de local: a contramano",
          _comp["senalesCalculadas"] == ["racha_en_otra_competicion", "condicion_a_contramano"]
          and _comp["enOtraCompeticion"] == 2 and _comp["partidos"][1]["amistoso"] is True, _comp)
    check("en su propio estadio la visita es nominal: no hay condicion_a_contramano (clásico de estadio compartido)",
          "condicion_a_contramano" not in rv.composicion(_racha, _fila, en_su_estadio=True)["senalesCalculadas"])
    _vis = [{**f, "condicion": "Visita"} for f in _racha]
    check("de LOCAL en su estadio, una racha hecha de visita sí es a contramano (Cristal 2-0 JP2)",
          "condicion_a_contramano" in rv.composicion(_vis, {"ligaId": 281, "condicion": "Local"},
                                                     en_su_estadio=True)["senalesCalculadas"])
    _fila_f = {"ligaId": 281, "condicion": "Local", "fecha": "2026-09-23T20:00:00Z"}
    _conc = [{"fixtureId": 7, "fecha": "2026-08-30", "ligaId": 281, "condicion": "Local", "golesFavor": 3, "golesContra": 2},
             {"fixtureId": 8, "fecha": "2026-09-01", "ligaId": 281, "condicion": "Local", "golesFavor": 4, "golesContra": 2}]
    _prev = [{"fixtureId": 9, "fecha": "2026-09-17T23:00:00Z", "esInternacional": True, "golesFavor": 0, "golesContra": 3}]
    _c2 = rv.composicion(_conc, _fila_f, _prev)["senalesCalculadas"]
    check("racha de victorias concediendo en todos y derrota internacional 6 días antes: las dos señales salen solas",
          "racha_concediendo" in _c2 and "derrota_internacional_reciente" in _c2, _c2)
    check("21 días sin partido antes del reventón → paron_largo (Union SG); 4 días, no",
          "paron_largo" in rv.composicion(_racha[2:], {**_fila, "fecha": "2026-07-06T20:00:00Z"},
                                           [{"fecha": "2026-06-15T20:00:00Z", "ligaId": 281}])["senalesCalculadas"]
          and "paron_largo" not in rv.composicion(_racha[2:], {**_fila, "fecha": "2026-06-19T20:00:00Z"},
                                                  [{"fecha": "2026-06-15T20:00:00Z", "ligaId": 281}])["senalesCalculadas"])
    check("una derrota internacional de hace 20 días ya no es resaca",
          "derrota_internacional_reciente" not in rv.composicion(
              _conc, _fila_f, [{**_prev[0], "fecha": "2026-09-01T23:00:00Z"}])["senalesCalculadas"])
    check("una racha de la misma liga y condición no levanta ninguna señal",
          rv.composicion(_racha[2:], _fila)["senalesCalculadas"] == [])
    _eq = dbmod.query_one("sad", "SELECT team_id, fixture_id FROM alineaciones WHERE titular=1 "
                                 "GROUP BY team_id, fixture_id HAVING COUNT(*)>=11 LIMIT 1")
    if _eq:
        check("el mismo once contra sí mismo no cambia a nadie; sin el otro once, None (sin dato no es cero)",
              rv.cambios_en_el_once(_eq["fixture_id"], _eq["team_id"], _eq["fixture_id"]) == 0
              and rv.cambios_en_el_once(_eq["fixture_id"], _eq["team_id"], -1) is None)
    check("once_distinto es calculada: un estudio no la declara ni la borra",
          "once_distinto" in rv.SENALES_CALCULADAS and "bloque_bajo_del_rival" in rv.MECANISMOS
          and "arquero_rival" in rv.MECANISMOS and "clasico" in rv.SENALES)
    # EL ARQUERO ANTES DEL PITAZO (14/10/2026): dato calculado, no regla
    from backend.analisis import arquero as _arq
    # caso propio: el arquero 1 atajó los dos primeros, el 2 el tercero (suplente)
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        for i, (gk, ga, xg) in enumerate([(1, 0, 1.5), (1, 1, 2.0), (2, 2, 0.5)]):
            fid = 990301 + i
            _con.execute("INSERT INTO fixtures (id, date, status_short, status_long, league_id, league_season, "
                         "home_team_id, away_team_id, goals_home, goals_away) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (fid, f"2026-03-0{i + 1} 20:00:00", "FT", "Match Finished", 140, 2026, 990300, 990101, 1, ga))
            _con.execute("INSERT INTO alineaciones (fixture_id, team_id, player_id, jugador, posicion, titular) "
                         "VALUES (?,?,?,?,?,1)", (fid, 990300, 9903000 + gk, f"Arquero {gk}", "G"))
            _con.execute("INSERT INTO fixture_stats (fixture_id, team_id, clave, valor) VALUES (?,?,?,?)",
                         (fid, 990101, "expected_goals", str(xg)))
    _p = _arq.perfil(990300, "2026-03-10", 990303)
    check("el perfil del arquero: habitual (2 de 3), el de hoy es otro → suplente; goles vs xG con su n",
          _p["habitual"]["nombre"] == "Arquero 1" and _p["habitual"]["titularEn"] == 2
          and _p["hoy"]["nombre"] == "Arquero 2" and _p["suplente"] is True
          and {k: _p["golesVsXg"][k] for k in ("recibidos", "xgContra", "evitados", "n")}
          == {"recibidos": 3, "xgContra": 4.0, "evitados": 1.0, "n": 3}
          and _p["golesVsXg"]["muestraCorta"] is True and len(_p["golesVsXg"]["porPartido"]) == 3
          and _p["hoyPerfil"] == {"titularEn": 1, "evitados": -1.5, "nXg": 1}, _p)
    check("sin partidos antes de la fecha: sinDato, no un perfil inventado",
          "sinDato" in _arq.perfil(990300, "1900-01-01"))
    with _sq.connect(os.path.join(tmp, "sad.db")) as _con:
        _con.execute("DELETE FROM fixtures WHERE id BETWEEN 990301 AND 990303")
        _con.execute("DELETE FROM alineaciones WHERE fixture_id BETWEEN 990301 AND 990303")
        _con.execute("DELETE FROM fixture_stats WHERE fixture_id BETWEEN 990301 AND 990303")
    check("arquero_suplente es calculada y el estudio tiene campo para el arquero",
          "arquero_suplente" in rv.SENALES_CALCULADAS and "arquero_suplente_rival" in rv.SENALES_CALCULADAS)
    check("«reventon» no es un skill: sus lecciones van a sad-analysis",
          rv.skill_canonico("reventon") == "sad-analysis" and rv.skill_canonico("teorema-del-echado") == "teorema-del-echado")
    _liga = dbmod.query_one("sad", "SELECT league_id, COUNT(*) AS n FROM fixtures GROUP BY league_id "
                                   "ORDER BY n DESC LIMIT 1")["league_id"]
    r_rv = c.get(f"{A}/analisis/cowork/reventones", params={"liga": _liga, "meses": 36})
    j_rv = r_rv.json()
    check("la lista de reventones sale de la base, con los dos tipos y la ficha disponible",
          r_rv.status_code == 200 and j_rv["total"] > 0 and set(j_rv["porTipo"]) == set(rv.TIPOS.values())
          and all("conFicha" in x and x["partidos"] >= 2 for x in j_rv["candidatos"]), j_rv.get("porTipo"))
    check("los candidatos salen al azar y estable (no por tamaño): el orden no sigue a la racha ni a la K",
          rv.orden_azar(1, 2) == rv.orden_azar(1, 2) and rv.orden_azar(1, 2) != rv.orden_azar(2, 1)
          and "AL AZAR" in j_rv["criterio"])
    _x = j_rv["candidatos"][0]
    _ruta = f"{A}/analisis/cowork/reventones/{_x['fixtureId']}/{_x['equipoId']}"
    f_rv = c.get(_ruta).json()
    check("la ficha del reventón trae la burbuja de los dos AL DÍA del partido y la táctica",
          f_rv["esCandidato"] and f_rv["reventon"]["tipo"] == _x["tipo"]
          and "riesgo" in f_rv["alDia"]["equipo"] and "riesgo" in f_rv["alDia"]["rival"]
          and "tactica" in f_rv and f_rv["estudio"] is None, list(f_rv))
    check("un mecanismo fuera de la lista no se guarda (422)",
          c.post(_ruta + "/estudio", json={"mecanismo": "mala suerte"}).status_code == 422)
    p_rv = c.post(_ruta + "/estudio", json={
        "mecanismo": "echada_del_que_ganaba", "senales": ["riesgo_alto", "inventada"],
        "tde": {"equipo": {"ie": 6.1}, "rival": {"ise": 3}},
        "arquero": {"rival": {"forma": "en racha", "decisivo": True}},
        "lecciones": [{"skill": "teorema-del-echado", "reglaTocada": "disciplina 16", "leccion": "se echó"},
                      {"leccion": "sin skill"}]}).json()
    check("el estudio se guarda; una señal inventada y una lección sin skill se rechazan con motivo",
          p_rv["estado"] == "guardado" and p_rv["estudio"]["senales"][0] == "riesgo_alto"
          and set(p_rv["estudio"]["senales"][1:]) == set(p_rv["estudio"]["senalesCalculadas"])
          and len(p_rv["rechazos"]) == 2 and p_rv["estudio"]["seleccion"] == "post_resultado"
          and p_rv["estudio"]["arquero"]["rival"]["decisivo"] is True, p_rv)
    check("la población no se declara: es post_resultado aunque llegue otra",
          c.post(_ruta + "/estudio", json={"mecanismo": "roja", "seleccion": "ciega"}).json()["estudio"]["seleccion"]
          == "post_resultado")
    c.post(_ruta + "/estudio", json=p_rv["estudio"])
    _otro = next((x for x in j_rv["candidatos"] if x["equipoId"] != _x["equipoId"]), None)
    _fx_no = dbmod.query_one("sad", "SELECT id FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
                                    "AND status_short='NS' LIMIT 1", (_x["equipoId"], _x["equipoId"]))
    if _fx_no:
        check("un partido que no cerró una burbuja de ese equipo no se estudia (422)",
              c.post(f"{A}/analisis/cowork/reventones/{_fx_no['id']}/{_x['equipoId']}/estudio",
                     json={"mecanismo": "roja"}).status_code == 422)
    j_rv2 = c.get(f"{A}/analisis/cowork/reventones", params={"liga": _liga, "meses": 36}).json()
    check("el estudiado sale marcado y al final de la lista",
          j_rv2["estudiados"] == 1 and not j_rv2["candidatos"][0]["estudiado"]
          and any(x["estudiado"] for x in j_rv2["candidatos"]), j_rv2["estudiados"])
    res_rv = c.get(f"{A}/analisis/cowork/reventones/resumen").json()
    check("el resumen cuenta por mecanismo y señal, y dice que no es probabilidad",
          res_rv[_x["tipo"]]["porMecanismo"] == {"echada_del_que_ganaba": 1}
          and "no probabilidad" in res_rv[_x["tipo"]]["nota"], res_rv)
    inv_rv = c.get(f"{A}/analisis/cowork/lecciones").json()
    it_rv = [i for i in inv_rv["items"] if i.get("origen") == "reventon"]
    check("sus lecciones entran a Aprendizaje como rúbrica: post_resultado, no mueven números",
          len(it_rv) == 1 and it_rv[0]["clave"] == f"rev:{_x['fixtureId']}:{_x['equipoId']}:1"
          and it_rv[0]["puedeMoverNumeros"] is False and it_rv[0]["skill"] == "teorema-del-echado", it_rv)
    import backend.app as _appmod
    check("el backtest de las lecciones se LEE con el token de Cowork; correrlo sigue siendo maestro",
          _appmod._cowork_puede("GET", f"{A}/analisis/cowork/reventones/backtest")
          and not _appmod._cowork_puede("GET", f"{A}/analisis/burbujas/backtest"))
    _rb = c.get(f"{A}/analisis/cowork/reventones/backtest")
    check("sin correrlo todavía responde 404 con cómo correrlo (o 200 si ya hay uno guardado)",
          _rb.status_code == 200 or (_rb.status_code == 404 and "--lecciones" in _rb.text), _rb.text[:200])
    check("el token de Cowork puede escribir el estudio y nada más nuevo",
          _appmod._cowork_puede("POST", f"{A}/analisis/cowork/reventones/1/2/estudio")
          and not _appmod._cowork_puede("POST", f"{A}/analisis/cowork/reventones/1/2"))

    # ── INCIDENCIAS: lo roto que ven las corridas, para el mantenimiento (18/10/2026) ──
    check("el token de Cowork deposita incidencias y marca su estado, sin borrar",
          _appmod._cowork_puede("POST", f"{A}/analisis/cowork/incidencias")
          and _appmod._cowork_puede("POST", f"{A}/analisis/cowork/incidencias/3/estado")
          and not _appmod._cowork_puede("DELETE", f"{A}/analisis/cowork/incidencias/3"))
    _ri = c.post(f"{A}/analisis/cowork/incidencias", json={"origen": "veredictos", "corrida": "18/10 20:12", "items": [
        {"titulo": "DT de Bournemouth: la base dice Tindall", "area": "dt", "fixtureId": 1557427,
         "detalle": "tres onces de Rose"},
        {"titulo": "Ventana relativa cobrada en minutos", "area": "ventanas", "severidad": "grave"},
        {"area": "tde"}]})
    _ji = _ri.json()
    check("depositar: dos nuevas, un área y una severidad fuera de lista se rechazan con motivo y se corrigen, "
          "sin título no entra",
          _ri.status_code == 200 and len(_ji["nuevas"]) == 2 and len(_ji["rechazos"]) == 3, _ji)
    _ri2 = c.post(f"{A}/analisis/cowork/incidencias", json={"origen": "partes", "items": [
        {"titulo": "dt de bournemouth: la base dice TINDALL", "area": "dt", "fixtureId": 1557427}]}).json()
    check("la misma incidencia abierta no se duplica: suma `veces`",
          _ri2["nuevas"] == [] and _ri2["repetidas"] == [_ji["nuevas"][0]], _ri2)
    _li = c.get(f"{A}/analisis/cowork/incidencias").json()
    _bour = next(x for x in _li["incidencias"] if x["id"] == _ji["nuevas"][0])
    check("el listado trae las abiertas con sus veces", _bour["veces"] == 2 and _bour["area"] == "dt"
          and _li["porEstado"].get("abierta", 0) >= 2, _bour)
    check("cerrar sin `resolucion` se rechaza (cerrar callado es esconderla)",
          c.post(f"{A}/analisis/cowork/incidencias/{_bour['id']}/estado", json={"estado": "resuelta"}).status_code == 422)
    _ce = c.post(f"{A}/analisis/cowork/incidencias/{_bour['id']}/estado",
                 json={"estado": "resuelta", "resolucion": "once de 4 días gana a /coachs", "pr": "#149"}).json()
    check("con resolución se cierra, con PR y fecha de cierre", _ce["estado"] == "resuelta" and _ce["pr"] == "#149"
          and _ce["cerradoEn"], _ce)
    _ri3 = c.post(f"{A}/analisis/cowork/incidencias", json={"origen": "partes", "items": [
        {"titulo": "DT de Bournemouth: la base dice Tindall", "area": "dt", "fixtureId": 1557427}]}).json()
    check("si vuelve a aparecer después de resuelta, entra NUEVA (el parche no alcanzó)", len(_ri3["nuevas"]) == 1, _ri3)
    # LA MISMA CAUSA EN OTRO PARTIDO NO ES OTRA INCIDENCIA (20/10/2026: 254 abiertas)
    _g1 = c.post(f"{A}/analisis/cowork/incidencias", json={"origen": "veredictos", "items": [
        {"titulo": "Titular de la ficha sin jugadorId (Rayo)", "area": "once", "fixtureId": 111},
        {"titulo": "titular de la ficha sin jugadorId", "area": "once", "fixtureId": 222},
        {"titulo": "Titular de la ficha sin jugadorId: Águilas", "area": "once", "fixtureId": 111}]}).json()
    _gl = next(x for x in c.get(f"{A}/analisis/cowork/incidencias").json()["incidencias"] if x["id"] == _g1["nuevas"][0])
    check("la misma causa en otros partidos suma veces y junta los partidos, no abre otra",
          len(_g1["nuevas"]) == 1 and len(_g1["repetidas"]) == 2 and _gl["veces"] == 3 and _gl["fixtures"] == [111, 222], (_g1, _gl))
    # EL ÁREA NO SEPARA UNA CAUSA (AEK, 298 «ficha» y 333 «agenda», 21/10/2026)
    _ga = c.post(f"{A}/analisis/cowork/incidencias", json={"origen": "veredictos", "items": [
        {"titulo": "Faltan partidos domésticos recientes (AEK)", "area": "ficha", "fixtureId": 555},
        {"titulo": "Faltan partidos domésticos recientes", "area": "agenda", "fixtureId": 556}]}).json()
    check("el mismo título con otra área es la misma incidencia", len(_ga["nuevas"]) == 1 and len(_ga["repetidas"]) == 1, _ga)
    from backend.analisis import incidencias as _incm
    with _incm._con() as _ci:
        for f, ar in ((777, "ficha"), (778, "agenda")):
            _ci.execute("INSERT INTO incidencia (clave, origen, area, severidad, titulo, creado_en, ultima_vez, fixture_id) "
                        "VALUES (?,?,?,?,?,?,?,?)", (f"{ar}:sede erronea", "partes", ar, "aviso", "Sede errónea", "2026-10-20", "2026-10-20", f))
    with _incm._con() as _ci:   # al abrir, las claves viejas «area:titulo» se reagrupan solas
        _rows = _ci.execute("SELECT estado, clave FROM incidencia WHERE titulo='Sede errónea' ORDER BY id").fetchall()
    check("las abiertas con la clave vieja (con área) se reagrupan solas al abrir la tabla",
          [r["estado"] for r in _rows] == ["abierta", "descartada"] and _rows[0]["clave"] == "sede erronea", [dict(r) for r in _rows])
    with _incm._con() as _ci:
        for f in (333, 444):
            _ci.execute("INSERT INTO incidencia (clave, origen, area, severidad, titulo, creado_en, ultima_vez, fixture_id) "
                        "VALUES (?,?,?,?,?,?,?,?)", (f"{f}:vieja", "partes", "ficha", "aviso", "Ficha sin stats (x)", "2026-10-18", "2026-10-18", f))
        _nf = _incm.reagrupar(_ci)
        _rows = _ci.execute("SELECT estado, fixtures, veces FROM incidencia WHERE titulo='Ficha sin stats (x)' ORDER BY id").fetchall()
    check("reagrupar funde las viejas de la misma causa: una queda con los dos partidos, la otra «descartada» (no se borra)",
          _nf >= 1 and [r["estado"] for r in _rows] == ["abierta", "descartada"] and json.loads(_rows[0]["fixtures"]) == [333, 444]
          and _rows[0]["veces"] == 2, [dict(r) for r in _rows])
    check("un origen desconocido es 422", c.post(f"{A}/analisis/cowork/incidencias",
                                                  json={"origen": "x", "items": [{"titulo": "t"}]}).status_code == 422)
    check("y el latido cuenta las incidencias", "incidencias" in c.get(f"{A}/analisis/cowork/latido").json())

    print()
    print(f"{'TODO OK' if not fallos else f'{fallos} FALLAS'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
