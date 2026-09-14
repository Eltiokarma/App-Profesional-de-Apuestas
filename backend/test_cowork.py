"""Tests del parte de Cowork: lo que se deposita, lo que se calcula y el once.

    python3 -m backend.test_cowork

Lo que se verifica es justo la frontera: que Cowork solo tenga que escribir lo
que es trabajo (sub-scores, tabla de plantel, prosa) y que TODO lo derivable
—totales, clasificación, IP, reducción por zona, ramas, F3, F4— lo ponga el
backend. Si un día alguien le pide a Cowork que mande un total, estos tests
siguen pasando pero el parte se vuelve más lento y más fácil de equivocar: por
eso el contrato ignora los campos calculados en vez de creerles.
"""
import os
import sys
import tempfile

fallos = 0


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
        },
        "tde": {"ie": 58, "ieNivel": "ambar", "ise": 31, "equipo": "b",
                "tipologia": "repliegue por agotamiento", "ventana": "75-90'",
                "vias": [{"nombre": "echada", "indice": 58, "ventana": "75-90'", "detalle": "baja el bloque"}],
                "falsador": "si sostiene la línea tras el 75'"},
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

    # caja de sensibilidad
    sens = d["equipos"]["a"]["sensibilidad"]
    check("la caja de sensibilidad viaja por equipo", len(sens) == 1, sens)
    check("un supuesto vacío no entra", all(x["supuesto"] for x in sens), sens)

    # TDE estructurado
    t = d["tde"]
    check("el TDE trae sus dos índices", (t["ie"], t["ise"]) == (58.0, 31.0), t)
    check("el nivel del IE llega del skill, no del backend", t["ieNivel"] == "ambar", t)
    check("el ISE sin nivel queda vacío en vez de inventado", t["iseNivel"] == "", t)
    check("el TDE trae su ventana y su causa", t["ventana"] and t["tipologia"], t)
    check("las vías del TDE viajan", len(t["vias"]) == 1, t.get("vias"))

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
    pend = c.get(f"{A}/analisis/cowork/veredictos/pendientes").json()
    check("el partido jugado aparece como pendiente de veredicto",
          any(x["fixtureId"] == pasado["id"] for x in pend), pend[:2])
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
              for x in c.get(f"{A}/analisis/cowork/veredictos/pendientes").json()))
    check("un fixture sin veredicto responde 404",
          c.get(f"{A}/analisis/cowork/{sin_ficha}/veredicto").status_code == 404)

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
    check("la ventana del TDE se lee del texto", (o2["tde"]["desde"], o2["tde"]["hasta"]) == (45, 60),
          o2.get("tde"))
    check("detecta el gol recibido dentro de la ventana", o2["tde"]["golEnVentana"] is True,
          o2.get("tde"))
    check("y solo cuenta los goles CONTRA el equipo evaluado",
          all(g["lado"] == "b" for g in o2["tde"]["goles"]), o2["tde"].get("goles"))
    check("la evidencia trae los goles con su minuto",
          len(o2["evidencia"]["goles"]) >= 2 and o2["evidencia"]["primerGol"]["minuto"] == 34,
          o2["evidencia"].get("goles"))

    # una ventana fuera de los goles no se da por cumplida
    p_tde["tde"]["ventana"] = "75-90'"
    c.post(f"{A}/analisis/cowork", json=p_tde)
    o3 = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]
    check("sin gol en la ventana, no se inventa el acierto", o3["tde"]["golEnVentana"] is False,
          o3.get("tde"))
    check("lo objetivo se RECALCULA al leer (el juicio no se re-escribió)",
          o3["tde"]["ventana"] == "75-90'", o3.get("tde"))

    # un pronóstico sin 1X2 no cuenta acierto en vez de contarlo como fallo
    p_vacio = _parte(con_ficha)
    p_vacio["pronostico"]["probabilidades"] = {"local": 0, "empate": 0, "visita": 0}
    c.post(f"{A}/analisis/cowork", json=p_vacio)
    o4 = c.get(f"{A}/analisis/cowork/{con_ficha}/veredicto").json()["objetivo"]
    check("sin 1X2 declarado no hay acierto ni fallo, hay nota",
          o4["unXDos"]["acerto"] is False and "no se cuenta" in o4["unXDos"]["nota"], o4["unXDos"])
    check("y tampoco hay Brier", o4["brier"]["valor"] is None, o4["brier"])

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
