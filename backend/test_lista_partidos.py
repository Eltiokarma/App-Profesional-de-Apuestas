"""La lectura de la tarjeta en Partidos (13/11/2026): la alerta DESCONFIAR con
la MISMA regla que el parte y los tres marcadores más probables del modelo de
goles; solo para los partidos con parte, y cerrado al token de Cowork.

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
