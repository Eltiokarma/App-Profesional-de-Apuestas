"""La lectura de la tarjeta en Partidos (13/11/2026): la alerta DESCONFIAR con
la MISMA regla que el parte, los tres marcadores más probables del modelo de
goles y (21/11/2026, v4.8) el juicio propio del analista, «¿entraría?»; solo
para los partidos con parte, y cerrado al token de Cowork.

    python -m backend.test_lista_partidos
"""
import os
import tempfile

os.environ["SAD_SIN_HILOS"] = "1"

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'✓' if cond else '✗ FALLA'} {nombre}" + (f" — {detalle}" if detalle and not cond else ""))


def main():
    tmp = tempfile.mkdtemp(prefix="sad_lista_")
    from backend.seed_demo import seed
    seed(tmp)
    os.environ["SAD_DATA_DIR"] = tmp
    import backend.db as dbmod
    dbmod.BASE_DIR = tmp
    from backend.analisis import db as efedb
    efedb.saddb.BASE_DIR = tmp
    from fastapi.testclient import TestClient
    import backend.app as appmod
    from backend.analisis import lista_partidos as lp
    from backend.analisis.lecciones import cuotas_mercado
    from backend.analisis.simulacion import alerta_confianza
    from backend.test_cowork import _parte
    appmod.RATE_LIMIT = 0
    c = TestClient(appmod.app)
    A = "/api/v1"

    fid = dbmod.query_one("sad", "SELECT DISTINCT fixture_id FROM odds ORDER BY fixture_id LIMIT 1")["fixture_id"]
    mk = cuotas_mercado([fid])[fid]["prob"]
    elegido = max(("local", "visita"), key=lambda k: mk[k])
    # le damos al elegido 8 pts más que la casa: SOBRE-LA-CASA seguro
    probs = {k: float(mk[k]) for k in ("local", "empate", "visita")}
    otro = "visita" if elegido == "local" else "local"
    probs[elegido] += 8
    probs[otro] -= 8
    p = _parte(fid)
    p["pronostico"]["probabilidades"] = {k: round(v, 1) for k, v in probs.items()}
    assert c.post(f"{A}/analisis/cowork", json=p).status_code in (200, 201)

    r = c.get(f"{A}/analisis/lista-partidos", params={"ids": f"{fid},1"})
    check("GET /analisis/lista-partidos responde 200", r.status_code == 200, r.text[:300])
    partes = r.json()["partes"]
    check("solo vienen los partidos con parte", str(fid) in partes and "1" not in partes, partes.keys())
    x = partes[str(fid)]
    d = x["desconfiar"]
    check("DESCONFIAR se enciende por SOBRE-LA-CASA, del lado del elegido",
          d and d["activa"] and d["elegido"] == elegido
          and any(m["codigo"] == "SOBRE-LA-CASA" for m in d["motivos"]), d)
    check("…con la lectura que restringe («X no gana: Y o empate»)",
          d and d["lectura"] and "no gana" in d["lectura"], d)
    gp = c.get(f"{A}/analisis/cowork/{fid}").json()
    tira = [a for a in gp.get("alertas") or [] if a.get("codigo") == "DESCONFIAR"]
    check("la MISMA alerta que la tira del parte (mismos motivos)",
          tira and sorted(tira[0]["motivos"]) == sorted(m["codigo"] for m in d["motivos"]), (tira, d))
    pura = alerta_confianza(p["pronostico"]["probabilidades"], mk, None)
    check("y la misma regla que la Simulación (alerta_confianza)",
          {m["codigo"] for m in pura["motivos"]} <= {m["codigo"] for m in d["motivos"]}, (pura, d))

    mar = x["marcadores"]
    if mar is None:
        check("sin goles acotados en la demo, marcadores es null (no se inventa)", x["marcadores"] is None)
    else:
        mp = mar["masProbables"]
        check("hasta tres marcadores, ordenados de más a menos probable",
              1 <= len(mp) <= lp.N_MARCADORES and all(mp[i]["prob"] >= mp[i + 1]["prob"] for i in range(len(mp) - 1))
              and all("-" in m["marcador"] for m in mp), mp)
        ga = (gp.get("lecturaSad") or {}).get("golesAcotados") or {}
        check("…los mismos que los goles acotados del parte",
              mp == (ga.get("masProbables") or [])[:lp.N_MARCADORES], (mp, ga))

    # sin desventaja: el 1X2 igual a la casa no enciende SOBRE-LA-CASA
    p["pronostico"]["probabilidades"] = {k: round(float(mk[k]), 1) for k in ("local", "empate", "visita")}
    c.post(f"{A}/analisis/cowork", json=p)
    d2 = c.get(f"{A}/analisis/lista-partidos", params={"ids": str(fid)}).json()["partes"][str(fid)]["desconfiar"]
    check("con el 1X2 pegado a la casa no hay SOBRE-LA-CASA",
          d2 is not None and not any(m["codigo"] == "SOBRE-LA-CASA" for m in d2["motivos"]), d2)
    check("sin ids válidos, vacío y sin error",
          c.get(f"{A}/analisis/lista-partidos", params={"ids": "a,b"}).json() == {"partes": {}})

    # ── ¿ENTRARÍA? el juicio propio del analista (21/11/2026, sad-analysis v4.8) ──
    p["pronostico"].pop("entrar", None)
    c.post(f"{A}/analisis/cowork", json=p)
    check("sin `pronostico.entrar`, la lista lo trae en null",
          c.get(f"{A}/analisis/lista-partidos", params={"ids": str(fid)}).json()["partes"][str(fid)]["entrar"] is None)
    rec = c.post(f"{A}/analisis/cowork", json=p).json()
    check("…y el recibo lo pide en `faltan` (con 1X2 declarado)",
          any(f.get("bloque") == "pronostico.entrar" for f in rec.get("faltan") or []), rec.get("faltan"))
    p["pronostico"]["entrar"] = {"decision": "noEntraria", "motivos": ["ONCE-INCIERTO", "once-incierto", "INVENTADO"],
                                 "porque": "el once depende de tres dudas que no se confirmaron"}
    rec = c.post(f"{A}/analisis/cowork", json=p).json()
    check("un motivo fuera de la lista cerrada se rechaza con motivo",
          any(r.get("donde") == "pronostico.entrar.motivos" and "INVENTADO" in r.get("porque", "")
              for r in rec.get("rechazos") or []), rec.get("rechazos"))
    check("con decisión, motivo y porqué ya no falta",
          not any(f.get("bloque") == "pronostico.entrar" for f in rec.get("faltan") or []), rec.get("faltan"))
    gp = c.get(f"{A}/analisis/cowork/{fid}").json()
    check("el parte lo guarda tal cual (motivos sin repetir, en mayúsculas)",
          gp["pronostico"]["entrar"] == {"decision": "noEntraria", "motivos": ["ONCE-INCIERTO"],
                                         "porque": "el once depende de tres dudas que no se confirmaron"},
          gp["pronostico"].get("entrar"))
    e = c.get(f"{A}/analisis/lista-partidos", params={"ids": str(fid)}).json()["partes"][str(fid)]["entrar"]
    check("la lista de Partidos lo trae para pintarlo", e and e["decision"] == "noEntraria" and e["motivos"] == ["ONCE-INCIERTO"], e)
    p["pronostico"]["entrar"] = {"decision": "dudo"}
    rec = c.post(f"{A}/analisis/cowork", json=p).json()
    check("«dudo» sin motivo ni porqué: entra, pero el recibo lo pide",
          any(f.get("bloque") == "pronostico.entrar" for f in rec.get("faltan") or []), rec.get("faltan"))
    p["pronostico"]["entrar"] = {"decision": "quizas"}
    rec = c.post(f"{A}/analisis/cowork", json=p).json()
    check("una decisión que no existe se rechaza y no se guarda",
          any(r.get("donde") == "pronostico.entrar.decision" for r in rec.get("rechazos") or [])
          and c.get(f"{A}/analisis/cowork/{fid}").json()["pronostico"].get("entrar") is None, rec.get("rechazos"))
    p["pronostico"]["entrar"] = {"decision": "entraria"}
    rec = c.post(f"{A}/analisis/cowork", json=p).json()
    check("«entraria» no pide motivo",
          not any(f.get("bloque") == "pronostico.entrar" for f in rec.get("faltan") or []), rec.get("faltan"))

    # ── las ligas que analizamos: las que tuvieron parte en los últimos días ──
    liga = dbmod.query_one("sad", "SELECT league_id FROM fixtures WHERE id=?", (fid,))["league_id"]
    from backend.analisis.parte import _conectar
    with _conectar() as con:   # el parte de la demo, con fecha de hoy (cuenta en la ventana)
        con.execute("UPDATE parte_cowork SET fecha=date('now') WHERE fixture_id=?", (fid,))
    lp._ANALIZADAS.clear()
    la = c.get(f"{A}/analisis/ligas-analizadas").json()
    fila = next((x for x in la["ligas"] if x["ligaId"] == liga), None)
    check("GET /analisis/ligas-analizadas trae la liga del parte, con cuántos y el último",
          la["dias"] == lp.DIAS_ANALIZADAS and fila and fila["partes"] >= 1 and fila["ultima"], la)
    otras = {r["league_id"] for r in dbmod.query("sad", "SELECT DISTINCT league_id FROM fixtures")} - {liga}
    check("…y no trae ligas sin parte", not ({x["ligaId"] for x in la["ligas"]} & otras), la)
    with _conectar() as con:   # un parte viejo no cuenta como «normalmente»
        con.execute("UPDATE parte_cowork SET fecha='2020-01-01' WHERE fixture_id=?", (fid,))
    lp._ANALIZADAS.clear()
    check("un parte de hace más de 30 días ya no cuenta",
          not any(x["ligaId"] == liga for x in c.get(f"{A}/analisis/ligas-analizadas").json()["ligas"]))

    appmod.API_TOKEN, appmod.TOKEN_COWORK, appmod.TOKEN_WEB = "maestra-prueba", "cowork-prueba", "web-prueba"
    try:
        check("el token de Cowork no lo abre (nace denegado)",
              c.get(f"{A}/analisis/lista-partidos", params={"ids": str(fid)},
                    headers={"Authorization": "Bearer cowork-prueba"}).status_code == 403)
        check("la web (solo lectura) sí",
              c.get(f"{A}/analisis/lista-partidos", params={"ids": str(fid)},
                    headers={"Authorization": "Bearer web-prueba"}).status_code == 200)
    finally:
        appmod.API_TOKEN = appmod.TOKEN_COWORK = appmod.TOKEN_WEB = ""

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
    raise SystemExit(1 if fallos else 0)


if __name__ == "__main__":
    main()
