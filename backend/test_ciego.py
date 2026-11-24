"""EL 1X2 CIEGO (22/11/2026): la lectura propia del analista, sellada ANTES de
ver la cuota, y medida contra la casa por acierto.

- se sella antes del pitazo y antes del parte; el primero manda;
- con el token de Cowork las cuotas de un partido por jugarse dan 409 hasta
  que el ciego esté sellado, y la `ventajaPorFuerza` del TDE viaja tapada;
- el maestro y la web leen las cuotas como siempre;
- el parte lo muestra y el recibo avisa si falta;
- `ciego.resumen` mide ciego, publicado y casa en los mismos partidos.

    python -m backend.test_ciego
"""
import os
import tempfile
from datetime import datetime, timedelta, timezone

os.environ["SAD_SIN_HILOS"] = "1"
os.environ.setdefault("SAD_CACHE_SIMULACION_S", "0")

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'✓' if cond else '✗ FALLA'} {nombre}" + (f" — {detalle}" if detalle and not cond else ""))


def resumen_puro():
    from backend.analisis import ciego

    # la validación
    for malo, por in (({"local": 50, "empate": 30}, "faltan claves"),
                      ({"local": 50, "empate": 30, "visita": 40, "porque": "x" * 30}, "suma 120"),
                      ({"local": 40, "empate": 20, "visita": 40, "porque": "x" * 30}, "empate arriba"),
                      ({"local": 50, "empate": 30, "visita": 20}, "sin porqué")):
        try:
            ciego.normalizar(malo)
            check(f"normalizar rechaza: {por}", False)
        except ciego.CiegoInvalido:
            check(f"normalizar rechaza: {por}", True)
    n = ciego.normalizar({"local": 50, "empate": 30, "visita": 19, "porque": "la K del local viene creciendo"})
    check("normalizar lleva a 100 lo que suma 99", abs(n["local"] + n["empate"] + n["visita"] - 100) < 0.2, n)
    n = ciego.normalizar({"probabilidades": {"local": 20, "empate": 30, "visita": 50},
                          "porque": "el rival viene de tres victorias"})
    check("normalizar acepta el 1X2 dentro de `probabilidades`", n["visita"] == 50.0, n)

    # la medición: mismos partidos para los tres
    casa = {"local": 60.0, "empate": 25.0, "visita": 15.0}
    pub = {"local": 59, "empate": 26, "visita": 15}

    def fila(i, c, real, desde="2026-11-24 20:00:00"):
        return {"fixtureId": i, "pitazo": desde, "ciego": c, "probabilidades": pub, "mercado": casa,
                "resultado": real}
    ciego_local = {"local": 55, "empate": 25, "visita": 20}
    ciego_visita = {"local": 30, "empate": 25, "visita": 45}
    filas = ([fila(1, ciego_local, "local"), fila(2, ciego_local, "empate"),
              fila(3, ciego_visita, "visita"), fila(4, ciego_visita, "local"),
              fila(5, None, "local"),                                       # sin ciego: no entra
              fila(6, ciego_local, None),                                   # pendiente: no entra
              fila(7, ciego_local, "local", desde="2026-11-20 20:00:00")])  # antes de DESDE: no entra
    r = ciego.resumen(filas)
    check("resumen: solo cerradas con ciego desde DESDE", r["n"] == 4 and r["sinCiego"] == 1, r)
    check("resumen: aciertos del ciego (local, visita)", r["ciego"]["aciertos"] == 2, r["ciego"])
    check("resumen: aciertos del publicado y de la casa (siempre local)",
          r["publicado"]["aciertos"] == 2 and r["casa"]["aciertos"] == 2, (r["publicado"], r["casa"]))
    check("resumen: desacuerdo con la casa (2: ciego 1, casa 1)",
          r["desacuerdo"] == {"n": 2, "ciego": 1, "casa": 1, "ninguno": 0}, r["desacuerdo"])
    check("resumen: la calibración por tramo cuenta las cuatro",
          sum(t["n"] for t in r["calibracion"]) == 4, r["calibracion"])
    check("resumen: con pocos partidos dice que es observación", "observación" in r["texto"], r["texto"])
    vacio = ciego.resumen([])
    check("resumen vacío: sin tasas y con texto", vacio["n"] == 0 and vacio["ciego"]["tasa"] is None
          and vacio["texto"], vacio)


def http():
    tmp = tempfile.mkdtemp(prefix="sad_ciego_")
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
    appmod.API_TOKEN = "maestra"
    appmod.TOKEN_COWORK = "token-cowork"
    appmod.TOKEN_WEB = "token-web"
    c = TestClient(app)
    A = "/api/v1"
    cw = {"Authorization": "Bearer token-cowork"}
    ma = {"Authorization": "Bearer maestra"}
    web = {"Authorization": "Bearer token-web"}

    # dos partidos por jugarse: uno se sella, el otro no; y uno ya jugado
    import sqlite3
    sad = sqlite3.connect(os.path.join(tmp, "sad.db"))
    ids = [r[0] for r in sad.execute("SELECT id FROM fixtures ORDER BY date DESC LIMIT 4")]
    futuro = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    pasado = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    fx, otro, jugado, cruce = ids
    sad.execute("UPDATE fixtures SET date=?, status_short='NS' WHERE id IN (?,?,?)", (futuro, fx, otro, cruce))
    sad.execute("UPDATE fixtures SET date=? WHERE id=?", (pasado, jugado))
    sad.commit()
    sad.close()

    r = c.get(f"{A}/cuotas/{fx}", headers=cw)
    check("cowork: las cuotas de un partido por jugarse sin ciego dan 409",
          r.status_code == 409 and r.json().get("pendienteCiego") is True, (r.status_code, r.text[:200]))
    check("cowork: también el historial de cuotas", c.get(f"{A}/cuotas/{fx}/historial", headers=cw).status_code == 409)
    check("cowork: las cuotas de un partido ya jugado se leen",
          c.get(f"{A}/cuotas/{jugado}", headers=cw).status_code == 200)
    check("maestro: lee las cuotas sin ciego", c.get(f"{A}/cuotas/{fx}", headers=ma).status_code == 200)
    check("web: lee las cuotas sin ciego", c.get(f"{A}/cuotas/{fx}", headers=web).status_code == 200)
    t = c.get(f"{A}/analisis/cowork/tde/{fx}", headers=cw)
    vpf = ((t.json().get("referencias") or {}).get("ventajaPorFuerza") or {}) if t.status_code == 200 else {}
    check("cowork: el TDE trae la ventaja por fuerza TAPADA antes del ciego",
          t.status_code == 200 and vpf.get("pendienteCiego") is True and vpf.get("a") is None,
          (t.status_code, vpf))
    t = c.get(f"{A}/analisis/cowork/tde/{fx}", headers=ma)
    check("maestro: el TDE trae la ventaja por fuerza sin tapar",
          t.status_code == 200 and not (t.json()["referencias"]["ventajaPorFuerza"] or {}).get("pendienteCiego"))

    body = {"local": 47, "empate": 28, "visita": 25, "porque": "la K del local crece y el rival llega sin su nueve"}
    r = c.post(f"{A}/analisis/cowork/{fx}/ciego", json={"local": 60, "empate": 60, "visita": 0}, headers=cw)
    check("cowork: un ciego que no suma 100 → 422", r.status_code == 422, r.text[:200])
    r = c.post(f"{A}/analisis/cowork/{fx}/ciego", json=body, headers=cw)
    check("cowork: sella el ciego (200, el token acotado puede)", r.status_code == 200, r.text[:300])
    s = r.json().get("ciego") or {}
    check("el sellado trae elegido y la hora", s.get("elegido") == "local" and s.get("selladoEn"), s)
    r = c.post(f"{A}/analisis/cowork/{fx}/ciego", json={**body, "local": 30, "visita": 42}, headers=cw)
    check("el primero manda: un segundo ciego → 409 con el sellado",
          r.status_code == 409 and (r.json()["detail"].get("ciego") or {}).get("local") == 47.0, r.text[:300])
    check("cowork: con el ciego sellado las cuotas se abren", c.get(f"{A}/cuotas/{fx}", headers=cw).status_code == 200)
    t = c.get(f"{A}/analisis/cowork/tde/{fx}", headers=cw).json()
    check("cowork: con el ciego sellado el TDE trae la ventaja por fuerza",
          not (t["referencias"]["ventajaPorFuerza"] or {}).get("pendienteCiego"))
    check("cowork: el otro partido sigue tapado", c.get(f"{A}/cuotas/{otro}", headers=cw).status_code == 409)
    check("GET del ciego", c.get(f"{A}/analisis/cowork/{fx}/ciego", headers=cw).json()["ciego"]["local"] == 47.0)
    check("GET del ciego que no existe → 404", c.get(f"{A}/analisis/cowork/{otro}/ciego", headers=cw).status_code == 404)
    r = c.post(f"{A}/analisis/cowork/{jugado}/ciego", json=body, headers=cw)
    check("después del pitazo no se sella (422)", r.status_code == 422 and "pitazo" in r.text, r.text[:200])

    # el parte lo muestra; el recibo avisa cuando falta, y después del parte ya no se sella
    from backend.test_cowork import _parte
    from backend.analisis import parte as cowork
    for fid in (fx, otro):
        p = _parte(fid)
        rr = c.post(f"{A}/analisis/cowork", json=p, headers=cw)
        check(f"deposita el parte de {fid}", rr.status_code == 200, rr.text[:300])
        faltan = [f["bloque"] for f in rr.json().get("faltan") or []]
        check(f"recibo de {fid}: avisa «ciego» solo si falta", ("ciego" in faltan) == (fid == otro), faltan)
    d = cowork.dto(fx)
    check("el parte trae el ciego sellado", (d.get("ciego") or {}).get("local") == 47.0, d.get("ciego"))
    check("un parte sin ciego trae ciego null", cowork.dto(otro).get("ciego") is None)
    check("cowork: con el parte ya depositado (sin ciego) las cuotas se abren: `rehacer` las necesita",
          c.get(f"{A}/cuotas/{otro}", headers=cw).status_code == 200)
    r = c.post(f"{A}/analisis/cowork/{otro}/ciego", json=body, headers=cw)
    check("con el parte ya depositado el ciego no se sella (422)", r.status_code == 422 and "parte" in r.text,
          r.text[:200])
    # 1491 (22/11/2026): Huancayo–Universitario y Cristal–Cienciano tenían parte
    # del 14/11 y se jugaban el 22/11 (aRehacer); el parte viejo bloqueaba el
    # ciego y dejaba la casa a la vista. Un parte de OTRA fecha no cuenta.
    movido = (datetime.now(timezone.utc) + timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    sad = sqlite3.connect(os.path.join(tmp, "sad.db"))
    sad.execute("UPDATE fixtures SET date=? WHERE id=?", (movido, otro))
    sad.commit()
    sad.close()
    check("aplazado (parte de otra fecha): la agenda lo manda a rehacer y la casa se tapa otra vez",
          c.get(f"{A}/cuotas/{otro}", headers=cw).status_code == 409)
    r = c.post(f"{A}/analisis/cowork/{otro}/ciego", json=body, headers=cw)
    check("aplazado: el ciego se sella antes del parte nuevo (200)", r.status_code == 200, r.text[:300])
    check("aplazado: con el ciego sellado la casa se abre", c.get(f"{A}/cuotas/{otro}", headers=cw).status_code == 200)
    check("la simulación trae el bloque del ciego",
          "ciego" in c.get(f"{A}/analisis/simulacion", headers=ma).json())
    # LAS DOS LECTURAS (24/11/2026): una por equipo; si se cruzan, el empate del motor las calza
    lect = {"ganaLocal": 70, "ganaVisita": 45, "porque": "el local llega entero y el visitante gana fuera"}
    r = c.post(f"{A}/analisis/cowork/{cruce}/ciego", json=lect, headers=cw)
    motor = (c.get(f"{A}/predicciones/{cruce}", headers=ma).json().get("unXDos") or {}).get("empate")
    if motor is None:
        check("dos lecturas cruzadas sin motor → 422 (no se inventa el empate)", r.status_code == 422, r.text[:300])
    else:
        cg = r.json().get("ciego") or {}
        check("dos lecturas cruzadas: se sellan (200) marcadas `cruzadas`", r.status_code == 200
              and cg.get("cruzadas") is True and cg.get("formato") == "lecturas", r.text[:300])
        check("dos lecturas cruzadas: el empate es el del motor y el 1X2 suma 100",
              abs(cg["empate"] - round(motor, 1)) < 0.11
              and abs(cg["local"] + cg["empate"] + cg["visita"] - 100) < 0.2, (cg, motor))
        check("dos lecturas cruzadas: lo escrito queda tal cual (70 y 45)",
              cg["ganaLocal"] == 70.0 and cg["ganaVisita"] == 45.0, cg)
        check("el GET del parte de cuotas se abre tras el sello de dos lecturas",
              c.get(f"{A}/cuotas/{cruce}", headers=cw).status_code == 200)
        # el PARTE también en dos lecturas (24/11/2026): el backend arma el 1X2
        from backend.test_cowork import _parte as _p
        pp = _p(cruce)
        pp["pronostico"] = {**(pp.get("pronostico") or {}), "lecturas": {"ganaLocal": 70, "ganaVisita": 45}}
        pp["pronostico"].pop("probabilidades", None)
        rr = c.post(f"{A}/analisis/cowork", json=pp, headers=cw)
        from backend.analisis import parte as _cw
        pr = (_cw.dto(cruce).get("pronostico") or {})
        check("parte en dos lecturas cruzadas: se deposita y el 1X2 lo arma el backend con el empate del motor",
              rr.status_code == 200 and abs(pr["probabilidades"]["empate"] - round(motor, 1)) < 0.11
              and abs(sum(pr["probabilidades"].values()) - 100) < 0.2
              and pr["lecturas"]["cruzadas"] is True and pr["lecturas"]["ganaLocal"] == 70.0, (rr.text[:200], pr))
    r = c.get(f"{A}/analisis/cowork/ciego/espejo", headers=cw)
    check("espejo: el token de Cowork lo lee (200) y no choca con /analisis/cowork/{id}",
          r.status_code == 200 and "calibracion" in r.json(), (r.status_code, r.text[:200]))
    crudo = r.text.lower()
    check("espejo: no trae nada de la casa (ni mercado, ni cuotas, ni plata)",
          not any(x in crudo for x in ('"mercado"', '"cuotas"', '"casa"', '"banca"', '"monto"')), crudo[:300])


def lecturas_puro():
    """Las dos lecturas (24/11/2026): ¿gana el local?, ¿gana el visitante?; el
    empate es la intersección de los dos «no gana»."""
    from backend.analisis import ciego

    p = ciego.calzar(55, 20)
    check("calzar: 55 y 20 → empate 25 (100 − las dos), sin cruce",
          p == {"local": 55.0, "empate": 25.0, "visita": 20.0, "cruzadas": False, "empateMotor": None}, p)
    p = ciego.calzar(70, 60, empate_motor=24.0)
    check("calzar: 70 y 60 se cruzan → empate del motor (24) y el resto 76 en proporción 70:60",
          p["cruzadas"] and p["empate"] == 24.0 and p["local"] == round(70 * 76 / 130, 1)
          and abs(p["local"] + p["empate"] + p["visita"] - 100) < 0.11, p)
    check("calzar: el motor puede llegar como función (se llama solo si hace falta)",
          ciego.calzar(70, 60, empate_motor=lambda: 30.0)["empate"] == 30.0)
    llamado = []
    ciego.calzar(40, 30, empate_motor=lambda: llamado.append(1))
    check("calzar: sin cruce no se llama al motor", not llamado)
    try:
        ciego.calzar(70, 60, empate_motor=None)
        check("calzar: cruzadas sin motor → CiegoInvalido", False)
    except ciego.CiegoInvalido:
        check("calzar: cruzadas sin motor → CiegoInvalido", True)
    n = ciego.normalizar({"ganaLocal": 48, "ganaVisita": 25, "porque": "el local viene entero y el rival sin su nueve"})
    check("normalizar: las dos lecturas dan el 1X2 y quedan tal cual",
          n["local"] == 48.0 and n["empate"] == 27.0 and n["visita"] == 25.0
          and n["ganaLocal"] == 48.0 and n["ganaVisita"] == 25.0 and n["cruzadas"] is False, n)
    for malo, por in (({"ganaLocal": 48, "porque": "x" * 30}, "falta una lectura"),
                      ({"ganaLocal": 120, "ganaVisita": 10, "porque": "x" * 30}, "una lectura sobre 100"),
                      ({"ganaLocal": 48, "ganaVisita": 25}, "sin porqué"),
                      ({"ganaLocal": 35, "ganaVisita": 35, "porque": "x" * 30}, "local y visita empatados arriba")):
        try:
            ciego.normalizar(malo, empate_motor=20.0)
            check(f"normalizar rechaza las lecturas: {por}", False)
        except ciego.CiegoInvalido:
            check(f"normalizar rechaza las lecturas: {por}", True)
    n = ciego.normalizar({"local": 50, "empate": 30, "visita": 20, "porque": "el formato de antes sigue valiendo"})
    check("normalizar: el 1X2 de antes sigue valiendo y sus lecturas son local y visita",
          n["ganaLocal"] == 50.0 and n["ganaVisita"] == 20.0 and n["cruzadas"] is False, n)


def parte_lecturas_puro():
    """El pronóstico del parte en dos lecturas (24/11/2026)."""
    from backend.analisis import parte as cowork

    rech = []
    x = cowork._lecturas_pronostico({"lecturas": {"ganaLocal": 52, "ganaVisita": 21}}, {}, rech)
    check("parte: lecturas 52 y 21 → 1X2 52/27/21 sin cruce",
          x and (x["local"], x["empate"], x["visita"]) == (52.0, 27.0, 21.0) and not x["cruzadas"] and not rech, x)
    x = cowork._lecturas_pronostico({}, {"ganaLocal": 52, "ganaVisita": 21}, rech)
    check("parte: las lecturas también se leen dentro de `probabilidades`", x and x["empate"] == 27.0, x)
    check("parte: el 1X2 de antes no tiene lecturas", cowork._lecturas_pronostico({}, {"local": 50}, rech) is None)
    cowork._lecturas_pronostico({"lecturas": {"ganaLocal": 150, "ganaVisita": 10}}, {}, rech)
    check("parte: una lectura fuera de 0-100 se rechaza con motivo",
          bool(rech) and rech[-1]["donde"] == "pronostico.lecturas")
    parte = {"pronostico": {"probabilidades": {"local": 0, "empate": 0, "visita": 0},
                            "lecturas": {"ganaLocal": 70, "ganaVisita": 60, "cruzadas": True, "empateMotor": None}}}
    cowork.calzar_lecturas(parte, lambda: 24.0)
    pr = parte["pronostico"]
    check("parte: las cruzadas se calzan al guardar con el empate del motor",
          pr["probabilidades"]["empate"] == 24.0 and pr["lecturas"]["empateMotor"] == 24.0, pr)
    sin = {"pronostico": {"probabilidades": {"local": 0, "empate": 0, "visita": 0},
                          "lecturas": {"ganaLocal": 70, "ganaVisita": 60, "cruzadas": True, "empateMotor": None}}}
    cowork.calzar_lecturas(sin, lambda: None)
    check("parte: cruzadas sin motor → 1X2 vacío y el rechazo lo dice (no se inventa el empate)",
          sum(sin["pronostico"]["probabilidades"].values()) == 0 and bool(sin.get("rechazos")), sin)


def espejo_puro():
    """El espejo (24/11/2026): la calibración propia sin la casa, con sus avisos."""
    from backend.analisis import ciego

    check("DESDE cuenta desde el domingo 22/11 (00:00 de Lima)", ciego.DESDE == "2026-11-22 05:00:00")

    def f(i, c, real, pitazo="2026-11-23 20:00:00"):
        return {"fixtureId": i, "pitazo": pitazo, "ciego": c, "resultado": real, "local": "A", "visita": "B"}
    corto = {"local": 53, "empate": 27, "visita": 20}      # tramo 50-59, gana siempre
    largo = {"local": 45, "empate": 30, "visita": 25}      # tramo 40-49, gana poco
    filas = ([f(i, corto, "local") for i in range(6)]
             + [f(10 + i, largo, "local" if i < 1 else "visita") for i in range(6)]
             + [f(20, corto, None),                                   # pendiente: no entra
                f(21, None, "local"),                                 # sin ciego: no entra
                f(22, corto, "visita", pitazo="2026-11-21 20:00:00")])  # antes de DESDE
    e = ciego.espejo(filas)
    check("espejo: solo cerradas con ciego desde DESDE", e["n"] == 12, e["n"])
    t = {x["tramo"]: x for x in e["calibracion"]}
    check("espejo: el 50-59 que gana siempre se lee CORTO", t["50-59"]["lectura"] == "corto"
          and t["50-59"]["paso"] == 100.0 and t["50-59"]["dijo"] == 53.0, t["50-59"])
    check("espejo: el 40-49 que gana 1 de 6 se lee LARGO", t["40-49"]["lectura"] == "largo", t["40-49"])
    check("espejo: un tramo sin 5 partidos no se lee", t["60-69"]["lectura"] is None, t["60-69"])
    check("espejo: el empate dicho contra el que hubo (0 de 12) avisa que le da de más",
          e["empate"]["empates"] == 0 and any("empate" in a.lower() and "de más" in a for a in e["avisos"]),
          (e["empate"], e["avisos"]))
    check("espejo: un aviso por tramo del elegido leído fuera de lo dicho, más el del empate",
          sum("tu elegido" in a for a in e["avisos"]) == 2 and any("empate" in a.lower() for a in e["avisos"]),
          e["avisos"])
    check("espejo: los últimos casos, el más nuevo arriba y con el elegido",
          e["ultimos"] and e["ultimos"][0]["elegido"] in ("local", "visita") and len(e["ultimos"]) <= ciego.ESPEJO_ULTIMOS,
          e["ultimos"][:1])
    check("espejo: con menos de 60 dice que es guía", "guía" in e["texto"], e["texto"])
    check("espejo: ninguna clave de la casa", not any(k in e for k in ("casa", "mercado", "publicado", "brier")))
    gl = {x["tramo"]: x for x in e["ganaLocal"]}
    check("espejo: la lectura del local se calibra sola (53 → 40-59, ganó 6 de 6 + 1 de 6)",
          gl["40-59"]["n"] == 12 and gl["40-59"]["paso"] == round(100 * 7 / 12, 1), gl["40-59"])
    gv = {x["tramo"]: x for x in e["ganaVisita"]}
    check("espejo: la lectura del visitante se calibra sola (20 y 25 → 20-39, ganó 5 de 12: corto)",
          gv["20-39"]["n"] == 12 and gv["20-39"]["paso"] == round(100 * 5 / 12, 1)
          and gv["20-39"]["lectura"] == "corto", gv["20-39"])
    cr = ciego.espejo([f(30 + i, {"local": 45, "empate": 20, "visita": 35, "ganaLocal": 70, "ganaVisita": 55,
                                  "cruzadas": True}, "local") for i in range(3)])
    check("espejo: los partidos con lecturas cruzadas se cuentan aparte y la lectura escrita es la que se calibra",
          cr["cruzadas"] == {"n": 3, "elegidoGano": 3}
          and {x["tramo"]: x for x in cr["ganaLocal"]}["60-79"]["n"] == 3, (cr["cruzadas"], cr["ganaLocal"]))
    v = ciego.espejo([])
    check("espejo vacío: n 0, sin avisos y con texto", v["n"] == 0 and not v["avisos"] and v["texto"], v)


def main():
    resumen_puro()
    lecturas_puro()
    parte_lecturas_puro()
    espejo_puro()
    http()
    print(f"\n{'TODO OK' if not fallos else f'{fallos} FALLA(S)'}")
    raise SystemExit(1 if fallos else 0)


if __name__ == "__main__":
    main()
