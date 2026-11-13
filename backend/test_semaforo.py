"""El semáforo del elegido POR LAS ESPINAS (13/11/2026; antes 11/11): la regla,
la serie en papel, el criterio por escalones (30 · 60 no-verdes: el amarillo y
el rojo tienen que acertar menos que el verde) y la REGLA ANTI-GOODHART (el
analista no lo ve).

    python -m backend.test_semaforo
"""
import json
import os
import tempfile

os.environ["SAD_SIN_HILOS"] = "1"
os.environ.setdefault("SAD_CACHE_SIMULACION_S", "0")

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'✓' if cond else '✗ FALLA'} {nombre}" + (f" — {detalle}" if detalle and not cond else ""))


def _tiene_clave(x, clave: str) -> bool:
    if isinstance(x, dict):
        return clave in x or any(_tiene_clave(v, clave) for v in x.values())
    if isinstance(x, list):
        return any(_tiene_clave(v, clave) for v in x)
    return False


def main():
    from backend.analisis import semaforo as sem
    from backend.analisis import simulacion as sim

    # ── la regla: sale de las espinas, NO de la cuota ───────────────────────
    check("el marcador manda el primero y da el signo (solo información)",
          sem.signo_marcador("2-1") == "local" and sem.signo_marcador("1-1 (o 2-2)") == "empate"
          and sem.signo_marcador("0 – 2") == "visita" and sem.signo_marcador("sin marcador") is None)
    casa = {"local": 50.0, "empate": 27.0, "visita": 23.0}
    L = {"local": 51, "empate": 26, "visita": 23}
    V = {"local": 26, "empate": 26, "visita": 48}

    def esp(a, b):
        return {"a": {"lectura": a, "porque": "x"}, "b": {"lectura": b, "porque": "y"}}
    v = sem.semaforo(L, esp("positiva", "negativa"), casa, "2-1")
    check("verde: la espina del elegido (local) positiva y la del rival negativa",
          v["estado"] == "confirma" and v["motivos"] == [] and v["elegido"] == "local"
          and v["espinaElegido"] == "positiva" and v["espinaRival"] == "negativa" and v["distancia"] == 1.0, v)
    v = sem.semaforo(L, esp("positiva", "neutra"), casa, "2-1")
    check("verde: la espina neutra del rival no se juzga (no enciende nada)", v["estado"] == "confirma", v)
    lejos = {"local": 70, "empate": 20, "visita": 10}
    v = sem.semaforo(lejos, esp("positiva", "negativa"), casa, "1-1")
    check("la cuota NO decide: 20 pts lejos de la casa y el marcador en contra siguen en verde",
          v["estado"] == "confirma" and v["distancia"] == 20.0 and v["marcadorSigno"] == "empate", v)
    v = sem.semaforo(L, esp("cero", "negativa"), casa, "1-0")
    check("amarillo: la espina del elegido dice empate",
          v["estado"] == "duda" and [m["codigo"] for m in v["motivos"]] == ["ESPINA-ELEGIDO-EMPATA"], v)
    v = sem.semaforo(L, esp("positiva", "positiva"), casa, "2-1")
    check("amarillo: la espina del rival dice que gana",
          v["estado"] == "duda" and [m["codigo"] for m in v["motivos"]] == ["ESPINA-RIVAL-SIGUE"], v)
    v = sem.semaforo(L, esp("positiva", "cero"), casa, "2-1")
    check("amarillo: la espina del rival dice que no pierde (cero)",
          v["estado"] == "duda" and "no pierde" in v["motivos"][0]["detalle"], v)
    v = sem.semaforo(V, esp("negativa", "negativa"), casa, "1-2")
    check("ROJO: el elegido (visita) con su espina negativa — el caso Italia 3-1 Francia",
          v["estado"] == "noApostar" and v["elegido"] == "visita" and v["espinaElegido"] == "negativa"
          and [m["codigo"] for m in v["motivos"]] == ["ESPINA-CONTRA-EL-ELEGIDO"], v)
    v = sem.semaforo(V, esp("positiva", "negativa"), casa, "1-2")
    check("rojo aunque además la del rival diga que gana: los dos motivos a la vista",
          v["estado"] == "noApostar" and {m["codigo"] for m in v["motivos"]}
          == {"ESPINA-CONTRA-EL-ELEGIDO", "ESPINA-RIVAL-SIGUE"}, v)
    v = sem.semaforo({"local": 0.20, "empate": 0.30, "visita": 0.50}, {"a": "negativa", "b": "positiva"})
    check("la visita lee la espina b, el rival la a; un 1X2 en fracción y la lectura sola valen",
          v["estado"] == "confirma" and v["espinaElegido"] == "positiva" and v["espinaRival"] == "negativa", v)
    E = {"local": 30, "empate": 40, "visita": 30}
    check("el elegido EMPATE: verde con las dos espinas en cero, amarillo si una no",
          sem.semaforo(E, esp("cero", "cero"))["estado"] == "confirma"
          and sem.semaforo(E, esp("cero", "positiva"))["estado"] == "duda"
          and sem.semaforo(E, esp("cero", "positiva"))["motivos"][0]["codigo"] == "ESPINA-NO-EMPATA")
    check("sin 1X2 o sin la espina del elegido (o neutra): sin dato (no se adivina)",
          sem.semaforo({"local": 51}, esp("positiva", "negativa"))["estado"] == "sinDato"
          and sem.semaforo(L, {})["estado"] == "sinDato"
          and sem.semaforo(L, esp("neutra", "negativa"))["estado"] == "sinDato"
          and sem.semaforo(L, None)["motivos"][0]["codigo"] == "SIN-ESPINA"
          and sem.semaforo(E, esp("cero", "neutra"))["estado"] == "sinDato")
    parte = {"pronostico": {"probabilidades": V, "marcador": "1-2"}, "lecturaSad": {"espina": esp("negativa", "negativa")}}
    check("del_parte lee pronostico y lecturaSad.espina", sem.del_parte(parte)["estado"] == "noApostar")
    check("los estados son cuatro y la regla se llama", sem.ESTADOS == ("confirma", "duda", "noApostar", "sinDato")
          and sem.REGLA == "espinas" and sem.DESDE == "2026-11-13 05:00:00")

    # ── la serie en papel: el método solo en verde ──────────────────────────
    def ap(fid, pit, probs, cuotas, res, espinas):
        p = dict(zip(sim.CLAVES, probs))
        m = {k: round(100 / c / sum(1 / x for x in cuotas), 1) for k, c in zip(sim.CLAVES, cuotas)}
        return {"fixtureId": fid, "pitazo": pit, "partido": {"local": "A", "visita": "B", "liga": "L"},
                "depositadoEn": pit, "versiones": {}, "versionPrompt": "", "probabilidades": p,
                "cuotas": dict(zip(sim.CLAVES, cuotas)), "mercado": m, "resultado": res,
                "semaforo": sem.semaforo(p, espinas, m, "2-1")}
    cuotas = (2.0, 3.4, 3.9)
    pl = (51, 26, 23)
    VERDE, AMARILLO, ROJO = esp("positiva", "negativa"), esp("positiva", "positiva"), esp("negativa", "positiva")
    out = sim.simular([ap(1, "2026-11-13 15:00:00", pl, cuotas, "local", VERDE),
                       ap(2, "2026-11-13 18:00:00", pl, cuotas, "local", AMARILLO),
                       ap(3, "2026-11-13 21:00:00", pl, cuotas, "visita", ROJO)])
    mv = next(e for e in out["estrategias"] if e["clave"] == "metodoVerde")
    pr = next(e for e in out["estrategias"] if e["clave"] == "proporcional")
    check("metodoVerde apuesta SOLO en verde (1 de 3) y el método en los tres",
          mv["apuestas"] == 1 and pr["apuestas"] == 3, (mv["apuestas"], pr["apuestas"]))
    check("con el mismo 1 % de la banca: +1 u × (2.0 − 1)", mv["banca"] == 101.0, mv["banca"])
    filas = {a["fixtureId"]: a for a in out["apuestas"]}
    check("cada apuesta trae su semáforo y el motivo de no apostar (amarillo y rojo)",
          filas[1]["semaforo"]["estado"] == "confirma"
          and filas[2]["porEstrategia"]["metodoVerde"]["motivo"] == "semáforo en amarillo"
          and filas[3]["porEstrategia"]["metodoVerde"]["motivo"] == "semáforo en rojo: no apostar",
          [filas[k]["porEstrategia"]["metodoVerde"] for k in (2, 3)])
    check("y el freno por tramo, como el método", mv["tramos"] is not None and len(mv["tramos"]) == 4)
    g = out["semaforo"]["nuevo"]
    check("el resumen separa verde, amarillo, rojo y sin dato",
          (g["verde"]["n"], g["amarillo"]["n"], g["rojo"]["n"], g["sinDato"]["n"]) == (1, 1, 1, 0), g)
    sin = sim.simular([{k: v for k, v in ap(4, "2026-11-13 15:00:00", pl, cuotas, "local", VERDE).items()
                        if k != "semaforo"}])
    check("una apuesta sin semáforo armado queda «sin dato» y metodoVerde no apuesta",
          sin["apuestas"][0]["semaforo"]["estado"] == "sinDato"
          and next(e for e in sin["estrategias"] if e["clave"] == "metodoVerde")["apuestas"] == 0)

    # ── el criterio por escalones (30 · 60 no-verdes), solo lo nuevo ───────
    def lote(n, aciertan, espinas, base=0, dia="2026-11-14"):
        out = []
        for i in range(n):
            hora = f"{dia} {(base + i // 60) % 24:02d}:{i % 60:02d}:00"
            out.append(ap(10000 + base * 1000 + i, hora, pl, cuotas, "local" if i < aciertan else "visita", espinas))
        return out

    def crit(verdes, v_ac, amarillos, am_ac, rojos=0, r_ac=0):
        lotes = lote(verdes, v_ac, VERDE) + lote(amarillos, am_ac, AMARILLO, base=8)
        if rojos:
            lotes += lote(rojos, r_ac, ROJO, base=16)
        return sim.simular(lotes)["semaforo"]["criterio"]
    r = sim.simular(lote(40, 30, AMARILLO, dia="2026-11-12"))["semaforo"]
    check("lo anterior al 13/11 entra en «todo» pero NO cuenta para el criterio",
          r["todo"]["amarillo"]["n"] == 40 and r["nuevo"]["amarillo"]["n"] == 0
          and r["criterio"]["estado"] == "en_observacion" and r["criterio"]["escalon"] == 0
          and r["criterio"]["faltan"] == 30 and r["criterio"]["separacion"] is None, r["criterio"])
    c = crit(200, 120, 29, 5)
    check("antes de 30 no-verdes: en observación aunque separen mucho, con lo que falta",
          c["estado"] == "en_observacion" and c["escalon"] == 0 and c["proximoEscalon"] == 30
          and c["faltan"] == 1 and c["n"] == 29, c)
    c = crit(200, 120, 20, 5, rojos=10, r_ac=2)
    check("escalón 30: amarillos + rojos cuentan juntos; 10+ pts debajo del verde → PROMETEDOR",
          c["estado"] == "prometedor" and c["escalon"] == 30 and c["n"] == 30 and c["proximoEscalon"] == 60
          and c["faltan"] == 30 and c["verdes"]["tasa"] == 0.6 and c["noVerdes"]["tasa"] == round(7 / 30, 4)
          and not c["cumple"], c)
    c = crit(200, 120, 30, 16)
    check("escalón 30: separa pero menos de 10 pts → en observación",
          c["estado"] == "en_observacion" and c["escalon"] == 30 and 0 < c["separacion"] < 0.10, c)
    c = crit(200, 120, 30, 19)
    check("escalón 30: los no-verdes aciertan más que el verde → NO SE SOSTIENE",
          c["estado"] == "no_se_sostiene" and c["separacion"] < 0, c)
    c = crit(200, 120, 60, 18)
    check("escalón 60: 10+ pts y el IC de los no-verdes entero debajo del verde → CONFIRMADO",
          c["estado"] == "confirmado" and c["cumple"] and c["escalon"] == 60 and c["proximoEscalon"] is None
          and c["faltan"] == 0 and c["noVerdesDebajo"] and c["noVerdes"]["intervalo"][1] < 0.6, c)
    c = crit(200, 120, 60, 30)
    check("escalón 60: 10+ pts pero el IC de los no-verdes toca el verde → sin contacto",
          c["estado"] == "sin_contacto" and not c["noVerdesDebajo"] and c["separacion"] >= 0.10, c)
    c = crit(200, 120, 60, 36)
    check("escalón 60: igual que el verde → NO SE SOSTIENE (sigue valiendo)",
          c["estado"] == "no_se_sostiene" and c["escalon"] == 60, c)
    c = crit(0, 0, 30, 10)
    check("sin verdes con que comparar → no se sostiene, con su texto", c["estado"] == "no_se_sostiene"
          and "sin verdes" in c["texto"], c)
    c = crit(200, 120, 60, 18)
    check("cada estado trae su texto en español con el escalón",
          all(k in c for k in ("escalon", "proximoEscalon", "faltan", "verdes", "noVerdes", "separacion", "n",
                               "texto")) and "escalón 60" in c["texto"], c)
    check("los escalones están fijados (30 · 60, 10 pts de separación)",
          sim.SEMAFORO_ESCALONES == (30, 60) and sim.SEMAFORO_SEPARACION == 0.10)

    # ── de punta a punta, y LA REGLA ANTI-GOODHART ──────────────────────────
    tmp = tempfile.mkdtemp(prefix="sad_semaforo_")
    from backend.seed_demo import seed
    seed(tmp)
    os.environ["SAD_DATA_DIR"] = tmp
    import backend.db as dbmod
    dbmod.BASE_DIR = tmp
    from backend.analisis import db as efedb
    efedb.saddb.BASE_DIR = tmp
    from fastapi.testclient import TestClient
    import backend.app as appmod
    from backend.test_cowork import _parte
    appmod.RATE_LIMIT = 0
    c = TestClient(appmod.app)
    A = "/api/v1"
    fid = dbmod.query_one("sad", "SELECT DISTINCT fixture_id FROM odds ORDER BY fixture_id LIMIT 1")["fixture_id"]
    p = _parte(fid)
    p["pronostico"]["probabilidades"] = {"local": 50, "empate": 27, "visita": 23}
    p["pronostico"]["marcador"] = "2-1"
    p.setdefault("lecturaSad", {})["espina"] = {"a": {"lectura": "positiva", "guia": "total", "porque": "x"},
                                                 "b": {"lectura": "negativa", "guia": "total", "porque": "y"}}
    recibo = c.post(f"{A}/analisis/cowork", json=p).json()
    check("el recibo del depósito NO trae el semáforo", not _tiene_clave(recibo, "semaforo"))
    gp = c.get(f"{A}/analisis/cowork/{fid}").json()
    check("el GET del parte NO trae el semáforo", not _tiene_clave(gp, "semaforo"))
    r = c.get(f"{A}/analisis/semaforo", params={"ids": f"{fid},1"}).json()
    s1 = r["partes"].get(str(fid))
    check("GET /analisis/semaforo calcula el del parte (y omite lo que no tiene parte)",
          s1 and s1["estado"] in sem.ESTADOS and s1["marcadorSigno"] == "local" and "1" not in r["partes"], r)
    gpe = (gp.get("lecturaSad") or {}).get("espina") or {}
    check("…con las espinas que guardó el parte (local positiva, visita negativa → verde)",
          s1["estado"] == "confirma" and s1["espinas"] == {k: (gpe.get(k) or {}).get("lectura") if (gpe.get(k) or {}).get("lectura") in sem.LECTURAS
                            else None for k in ("a", "b")}, (s1, gpe))
    from backend.analisis.lecciones import cuotas_mercado
    mk = (cuotas_mercado([fid]).get(fid) or {}).get("prob")
    check("…con la MISMA cuota que la simulación (lecciones.cuotas_mercado)",
          s1 == sem.semaforo(p["pronostico"]["probabilidades"], gpe, mk, "2-1"), (s1, mk))

    appmod.API_TOKEN, appmod.TOKEN_COWORK, appmod.TOKEN_WEB = "maestra-prueba", "cowork-prueba", "web-prueba"
    try:
        cw = {"Authorization": "Bearer cowork-prueba"}
        wb = {"Authorization": "Bearer web-prueba"}
        check("ANTI-GOODHART: el token de Cowork NO lee el semáforo",
              c.get(f"{A}/analisis/semaforo", params={"ids": str(fid)}, headers=cw).status_code == 403
              and not appmod._cowork_puede("GET", f"{A}/analisis/semaforo"))
        check("…ni la simulación (donde viaja por apuesta)",
              c.get(f"{A}/analisis/simulacion", headers=cw).status_code == 403)
        check("…y lo que sí lee no lo trae (el parte, las lecciones)",
              not _tiene_clave(c.get(f"{A}/analisis/cowork/{fid}", headers=cw).json(), "semaforo")
              and not _tiene_clave(c.get(f"{A}/analisis/cowork/lecciones?resumen=true", headers=cw).json(), "semaforo"))
        check("la web (solo lectura) sí lo lee",
              c.get(f"{A}/analisis/semaforo", params={"ids": str(fid)}, headers=wb).status_code == 200)
    finally:
        appmod.API_TOKEN = appmod.TOKEN_COWORK = appmod.TOKEN_WEB = ""

    # el caché de la simulación ve un marcador nuevo (la huella lo incluye)
    from backend.analisis.parte import _conectar
    with _conectar() as con:   # la huella mira los partes desde el 28/10: se lo pone ahí
        con.execute("UPDATE parte_cowork SET fecha='2026-11-11' WHERE fixture_id=?", (fid,))
    h1 = sim.huella_simulacion()
    with _conectar() as con:
        pj = json.loads(con.execute("SELECT parte_json FROM parte_cowork WHERE fixture_id=?", (fid,)).fetchone()[0])
        pj["pronostico"]["marcador"] = "0-1"
        con.execute("UPDATE parte_cowork SET parte_json=? WHERE fixture_id=?", (json.dumps(pj), fid))
    check("un marcador re-declarado cambia la huella de la simulación", sim.huella_simulacion() != h1)
    h2 = sim.huella_simulacion()
    with _conectar() as con:
        pj = json.loads(con.execute("SELECT parte_json FROM parte_cowork WHERE fixture_id=?", (fid,)).fetchone()[0])
        pj.setdefault("lecturaSad", {})["espina"] = {"a": {"lectura": "negativa"}, "b": {"lectura": "positiva"}}
        con.execute("UPDATE parte_cowork SET parte_json=? WHERE fixture_id=?", (json.dumps(pj), fid))
    check("una espina re-declarada también (el color sale de ahí)", sim.huella_simulacion() != h2)

    # el informe de los lunes (backend.contacto) trae su sección
    from backend import contacto
    datos = {"7": {"parte": {"creadoEn": "2026-11-11 12:00:00", "version": "x",
                             "pronostico": {"probabilidades": {"local": 50, "empate": 27, "visita": 23}, "marcador": "2-1"},
                             "lecturaSad": {"espina": {"a": {"lectura": "positiva"}, "b": {"lectura": "negativa"}}}},
                   "fx": {"fecha": "2026-11-11T20:00:00Z", "estado": "finalizado", "ligaId": 135, "liga": "Serie A",
                          "local": {"nombre": "A"}, "visitante": {"nombre": "B"}, "golesLocal": 2, "golesVisitante": 1},
                   "cuotas": [{"mercado": "1x2", "seleccion": s, "cuota": q} for s, q in zip("1X2", (2.0, 3.6, 4.3))]}}
    aps, _ = contacto.armar(datos)
    out = sim.simular(aps)
    texto = contacto.informe(out)
    check("contacto.armar arma el semáforo con el 1X2 sin margen de /cuotas",
          aps and aps[0]["semaforo"]["estado"] == "confirma" and aps[0]["semaforo"]["marcadorSigno"] == "local", aps[:1])
    check("y el informe de los lunes trae la sección «Semáforo» con el criterio",
          "Semáforo" in texto and "verdes:" in texto and "rojos:" in texto and out["semaforo"]["criterio"]["texto"] in texto, texto[-400:])

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
    raise SystemExit(1 if fallos else 0)


if __name__ == "__main__":
    main()
