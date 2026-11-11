"""El semáforo del elegido (11/11/2026): la regla, la serie en papel, el criterio
fijo y la REGLA ANTI-GOODHART (el analista no lo ve).

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

    # ── la regla ────────────────────────────────────────────────────────────
    check("el marcador manda el primero y da el signo",
          sem.signo_marcador("2-1") == "local" and sem.signo_marcador("1-1 (o 2-2)") == "empate"
          and sem.signo_marcador("0 – 2") == "visita" and sem.signo_marcador("sin marcador") is None)
    casa = {"local": 50.0, "empate": 27.0, "visita": 23.0}
    v = sem.semaforo({"local": 51, "empate": 26, "visita": 23}, casa, "2-1")
    check("verde: a ≤ 2 pts de la casa en los tres y el marcador con el elegido",
          v["estado"] == "confirma" and v["motivos"] == [] and v["elegido"] == "local" and v["distancia"] == 1.0, v)
    v = sem.semaforo({"local": 52, "empate": 25, "visita": 23}, casa, "1-0")
    check("el borde: exactamente 2 pts sigue siendo verde", v["estado"] == "confirma", v)
    v = sem.semaforo({"local": 55, "empate": 24, "visita": 21}, casa, "2-1")
    check("amarillo por la casa: un resultado a más de 2 pts (dice cuál)",
          v["estado"] == "duda" and [m["codigo"] for m in v["motivos"]] == ["LEJOS-DE-LA-CASA"]
          and "local" in v["motivos"][0]["detalle"], v)
    v = sem.semaforo({"local": 51, "empate": 26, "visita": 23}, casa, "1-1")
    check("amarillo por el marcador: dice empate y el elegido es el local",
          v["estado"] == "duda" and [m["codigo"] for m in v["motivos"]] == ["MARCADOR-CONTRADICE"], v)
    v = sem.semaforo({"local": 0.40, "empate": 0.40, "visita": 0.20}, casa, "0-1")
    check("las dos fallas a la vez, y un 1X2 en fracción se normaliza",
          v["estado"] == "duda" and {m["codigo"] for m in v["motivos"]} == {"LEJOS-DE-LA-CASA", "MARCADOR-CONTRADICE"}, v)
    check("sin cuotas, sin marcador o sin 1X2: sin dato (no se adivina)",
          sem.semaforo({"local": 51, "empate": 26, "visita": 23}, None, "2-1")["estado"] == "sinDato"
          and sem.semaforo({"local": 51, "empate": 26, "visita": 23}, casa, "")["estado"] == "sinDato"
          and sem.semaforo({"local": 51}, casa, "2-1")["estado"] == "sinDato")

    # ── la serie en papel: el método solo en verde ──────────────────────────
    def ap(fid, pit, probs, cuotas, res, marcador, mercado=None):
        p = dict(zip(sim.CLAVES, probs))
        m = mercado or {k: round(100 / c / sum(1 / x for x in cuotas), 1) for k, c in zip(sim.CLAVES, cuotas)}
        return {"fixtureId": fid, "pitazo": pit, "partido": {"local": "A", "visita": "B", "liga": "L"},
                "depositadoEn": pit, "versiones": {}, "versionPrompt": "", "probabilidades": p,
                "cuotas": dict(zip(sim.CLAVES, cuotas)), "mercado": m, "resultado": res,
                "semaforo": sem.semaforo(p, m, marcador)}
    cuotas = (2.0, 3.4, 3.9)
    m = {k: round(100 / c / sum(1 / x for x in cuotas), 1) for k, c in zip(sim.CLAVES, cuotas)}
    pegado = (m["local"], m["empate"], m["visita"])
    out = sim.simular([ap(1, "2026-11-11 15:00:00", pegado, cuotas, "local", "2-1"),
                       ap(2, "2026-11-11 18:00:00", pegado, cuotas, "local", "1-1"),
                       ap(3, "2026-11-11 21:00:00", (70, 20, 10), cuotas, "visita", "2-0")])
    mv = next(e for e in out["estrategias"] if e["clave"] == "metodoVerde")
    pr = next(e for e in out["estrategias"] if e["clave"] == "proporcional")
    check("metodoVerde apuesta SOLO en verde (1 de 3) y el método en los tres",
          mv["apuestas"] == 1 and pr["apuestas"] == 3, (mv["apuestas"], pr["apuestas"]))
    check("con el mismo 1 % de la banca: +1 u × (2.0 − 1)", mv["banca"] == 101.0, mv["banca"])
    filas = {a["fixtureId"]: a for a in out["apuestas"]}
    check("cada apuesta trae su semáforo y el motivo de no apostar",
          filas[1]["semaforo"]["estado"] == "confirma"
          and filas[2]["porEstrategia"]["metodoVerde"]["motivo"] == "semáforo en amarillo", filas[2]["porEstrategia"]["metodoVerde"])
    check("y el freno por tramo, como el método", mv["tramos"] is not None and len(mv["tramos"]) == 4)
    sin = sim.simular([{k: v for k, v in ap(4, "2026-11-11 15:00:00", pegado, cuotas, "local", "2-1").items()
                        if k != "semaforo"}])
    check("una apuesta sin semáforo armado queda «sin dato» y metodoVerde no apuesta",
          sin["apuestas"][0]["semaforo"]["estado"] == "sinDato"
          and next(e for e in sin["estrategias"] if e["clave"] == "metodoVerde")["apuestas"] == 0)

    # ── el criterio fijo: solo lo nuevo, 150+ verdes, +5 pts con el IC encima ──
    def lote(n, aciertan, desde_h=0, dia="2026-11-12", verde=True):
        out = []
        for i in range(n):
            hora = f"{dia} {(desde_h + i // 60) % 24:02d}:{i % 60:02d}:00"
            out.append(ap(1000 + i + desde_h * 1000, hora, pegado if verde else (70, 20, 10), cuotas,
                          "local" if i < aciertan else "visita", "2-1"))
        return out
    r = sim.simular(lote(40, 30, dia="2026-11-05"))["semaforo"]
    check("lo anterior al 11/11 entra en «todo» pero NO cuenta para el criterio",
          r["todo"]["verde"]["n"] == 40 and r["nuevo"]["verde"]["n"] == 0
          and r["criterio"]["estado"] == "en_observacion", r["criterio"])
    r = sim.simular(lote(149, 120))["semaforo"]
    check("con 149 verdes nuevos sigue en observación aunque acierten mucho",
          r["criterio"]["estado"] == "en_observacion" and r["criterio"]["faltan"] == 1, r["criterio"])
    r = sim.simular(lote(160, 110) + lote(40, 10, desde_h=10, verde=False))["semaforo"]
    check("150+ verdes nuevos, +5 pts con el intervalo encima y los amarillos abajo: SEÑAL",
          r["criterio"]["estado"] == "senal" and r["criterio"]["cumple"]
          and r["nuevo"]["verde"]["ventaja"] >= 0.05 and r["nuevo"]["amarillo"]["n"] == 40, r["criterio"])
    r = sim.simular(lote(160, 85))["semaforo"]
    check("150+ verdes que no le ganan a la cuota por 5: sin señal",
          r["criterio"]["estado"] == "sin_senal" and not r["criterio"]["cumple"], r["criterio"])
    r = sim.simular(lote(160, 110) + lote(40, 38, desde_h=10, verde=False))["semaforo"]
    check("si los amarillos aciertan más que los verdes, tampoco",
          r["criterio"]["estado"] == "sin_senal" and r["criterio"]["amarillosDebajo"] is False, r["criterio"])

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
    recibo = c.post(f"{A}/analisis/cowork", json=p).json()
    check("el recibo del depósito NO trae el semáforo", not _tiene_clave(recibo, "semaforo"))
    gp = c.get(f"{A}/analisis/cowork/{fid}").json()
    check("el GET del parte NO trae el semáforo", not _tiene_clave(gp, "semaforo"))
    r = c.get(f"{A}/analisis/semaforo", params={"ids": f"{fid},1"}).json()
    s1 = r["partes"].get(str(fid))
    check("GET /analisis/semaforo calcula el del parte (y omite lo que no tiene parte)",
          s1 and s1["estado"] in sem.ESTADOS and s1["marcadorSigno"] == "local" and "1" not in r["partes"], r)
    from backend.analisis.lecciones import cuotas_mercado
    mk = (cuotas_mercado([fid]).get(fid) or {}).get("prob")
    check("…con la MISMA cuota que la simulación (lecciones.cuotas_mercado)",
          s1 == sem.semaforo(p["pronostico"]["probabilidades"], mk, "2-1"), (s1, mk))

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

    # el informe de los lunes (backend.contacto) trae su sección
    from backend import contacto
    datos = {"7": {"parte": {"creadoEn": "2026-11-11 12:00:00", "version": "x",
                             "pronostico": {"probabilidades": {"local": 50, "empate": 27, "visita": 23}, "marcador": "2-1"}},
                   "fx": {"fecha": "2026-11-11T20:00:00Z", "estado": "finalizado", "ligaId": 135, "liga": "Serie A",
                          "local": {"nombre": "A"}, "visitante": {"nombre": "B"}, "golesLocal": 2, "golesVisitante": 1},
                   "cuotas": [{"mercado": "1x2", "seleccion": s, "cuota": q} for s, q in zip("1X2", (2.0, 3.6, 4.3))]}}
    aps, _ = contacto.armar(datos)
    out = sim.simular(aps)
    texto = contacto.informe(out)
    check("contacto.armar arma el semáforo con el 1X2 sin margen de /cuotas",
          aps and aps[0]["semaforo"]["estado"] in sem.ESTADOS and aps[0]["semaforo"]["marcadorSigno"] == "local", aps[:1])
    check("y el informe de los lunes trae la sección «Semáforo» con el criterio",
          "Semáforo" in texto and "verdes:" in texto and out["semaforo"]["criterio"]["texto"] in texto, texto[-400:])

    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
    raise SystemExit(1 if fallos else 0)


if __name__ == "__main__":
    main()
