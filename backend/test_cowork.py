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
                  "fuera": [{"nombre": "A Jugador6", "estado": "baja", "motivo": "lesión"}]},
            "b": {"nombre": nombre_b, "bloques": {"A": 1, "B": 2, "D": 1, "E": 1},
                  "excluidos": {"C": "SIN DATOS K — recién ascendido (R-KT.2)"},
                  "dt": {"nombre": "DT B", "meses": 2},
                  "plantel": _plantel("B"), "fuera": []},
        },
        "alertas": [{"codigo": "T.54", "equipo": "b", "tipo": "estructural", "detalle": "DT interino"}],
        "matchup": {"diagnostico": "MATCHUP FAVORABLE", "favorece": "a", "razon": "asimetría en ATK"},
        "pronostico": {"motor": "gap §5 a favor de A", "matriz": "55/25/20", "mercado": "1.85 / 3.4 / 4.2",
                       "probabilidades": {"local": 52, "empate": 26, "visita": 22},
                       "marcador": "2-1", "falsador": "si B abre el marcador antes del 20'"},
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
