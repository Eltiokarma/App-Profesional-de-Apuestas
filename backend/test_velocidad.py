"""Velocidad SIN cambiar un número: Aprendizaje (y Simulación) con caché.

    python -m backend.test_velocidad

10/11/2026, usuario: «la sección Aprendizaje carga mucho y es bien lenta,
igual Simulación». El inventario rehacía el objetivo de cada veredicto cada
10 minutos aunque nada hubiera cambiado. Ahora cada objetivo se guarda con la
huella de sus insumos (`lecciones._objetivo`). Lo que se verifica:

1. con caché y sin caché, el inventario y la calibración dan LO MISMO;
2. una segunda lectura no rehace ningún objetivo;
3. el pipeline que reescribe las derivadas sin tocar la historia no rehace
   nada; el que cambia la historia de un equipo rehace SOLO sus casos, y el
   resultado vuelve a ser idéntico al calculado desde cero;
4. un veredicto corregido o un marcador nuevo rehacen ese caso;
5. `historias_compartidas` devuelve la misma historia que la consulta suelta
   y una copia que se puede tocar sin ensuciar la siguiente.
"""
import json
import os
import random
import sqlite3
import tempfile

os.environ["SAD_SIN_HILOS"] = "1"

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'✓' if cond else '✗ FALLA'} {nombre}" + (f" — {detalle}" if detalle and not cond else ""))


def _armar(tmp: str) -> list[int]:
    """La demo con un parte y un veredicto en 30 partidos terminados."""
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
    fx = dbmod.query("sad", "SELECT f.id, f.date, ht.name a, at.name b FROM fixtures f "
                            "JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
                            "WHERE f.status_short='FT' ORDER BY f.date DESC LIMIT 30")
    rnd = random.Random(7)
    for f in fx:
        p = _parte(f["id"], f["a"], f["b"])
        p["fecha"] = f["date"][:10]
        p["pronostico"]["probabilidades"] = {"local": rnd.randint(30, 60), "empate": 25, "visita": 15}
        c.post("/api/v1/analisis/cowork", json=p)
        c.post(f"/api/v1/analisis/cowork/{f['id']}/veredicto", json={
            "seleccion": "ciega", "modoEvaluacion": "PRE", "falsadorCumplido": False,
            "porLado": {"a": {"veredicto": rnd.choice(["acierto", "fallo", "parcial"]), "queP": "x",
                              "leccion": "el bloque bajo sostiene", "skill": "teorema-del-echado"},
                        "b": {"veredicto": "fallo", "queP": "no llegó", "leccion": "la presión cae al 60",
                              "skill": "efe-clasificador"}}})
    return [f["id"] for f in fx]


def main():
    tmp = tempfile.mkdtemp(prefix="sad_velocidad_")
    ids = _armar(tmp)
    from backend.analisis import lecciones, veredicto as vered
    from backend.analisis import db as efedb

    calculos = []
    original = vered.objetivo

    def contado(fid, parte):
        calculos.append(fid)
        return original(fid, parte)
    vered.objetivo = contado

    def q(d):
        return json.dumps({k: v for k, v in d.items() if k != "generadoEn"}, sort_keys=True, default=str)

    def desde_cero():
        ttl = lecciones.OBJETIVO_TTL_S
        lecciones.OBJETIVO_TTL_S = 0
        lecciones._invalidar()
        try:
            return (q(lecciones.inventario(cohorte="vigente", resumen=True)),
                    q(lecciones.calibracion_espina()), q(lecciones.derrotas_favorito()))
        finally:
            lecciones.OBJETIVO_TTL_S = ttl

    def con_cache():
        lecciones._invalidar()
        return (q(lecciones.inventario(cohorte="vigente", resumen=True)),
                q(lecciones.calibracion_espina()), q(lecciones.derrotas_favorito()))

    lecciones.OBJETIVO_TTL_S = 86400
    lecciones._OBJ_CACHE.clear()
    base = desde_cero()
    calculos.clear()
    primera = con_cache()
    n_primera = len(calculos)
    check("con caché, el inventario, la calibración y las derrotas son idénticos a sin caché",
          primera == base)
    check("la primera lectura con caché calcula cada caso una vez (no una por pedido)",
          0 < n_primera <= len(ids), n_primera)

    calculos.clear()
    check("la segunda lectura da lo mismo", con_cache() == base)
    check("…y no rehace ningún objetivo", calculos == [], len(calculos))

    # el pipeline reescribe las derivadas (cambia la fecha del archivo) sin tocar la historia
    ruta = os.path.join(tmp, "constants.db")
    os.utime(ruta, None)
    st = os.stat(ruta)
    os.utime(ruta, ns=(st.st_atime_ns, st.st_mtime_ns + 10_000_000_000))
    calculos.clear()
    check("un pipeline que no cambia la historia no cambia nada", con_cache() == base)
    check("…y no rehace ningún objetivo (la firma estrecha lo confirma)", calculos == [], len(calculos))

    # el pipeline cambia la historia de UN equipo: solo sus casos se rehacen
    import backend.db as dbmod
    fx = {r["id"]: r for r in dbmod.query(
        "sad", f"SELECT id, home_team_id, away_team_id FROM fixtures WHERE id IN ({','.join('?' * len(ids))})",
        tuple(ids))}
    tid = fx[ids[0]]["home_team_id"]
    suyos = {i for i in ids if tid in (fx[i]["home_team_id"], fx[i]["away_team_id"])}
    sq = sqlite3.connect(ruta)
    sq.execute("UPDATE constants SET k_positivo = k_positivo + 1 WHERE team_id=?", (tid,))
    sq.commit()
    sq.close()
    calculos.clear()
    cambiado = con_cache()
    check("si la historia de un equipo cambia, se rehacen SOLO sus casos",
          set(calculos) <= suyos and calculos, (len(calculos), len(suyos)))
    check("…y el resultado es idéntico al calculado desde cero", cambiado == desde_cero())

    # un veredicto corregido: ese caso se rehace
    con = efedb.conectar()
    v = json.loads(con.execute("SELECT veredicto_json FROM parte_cowork WHERE fixture_id=?", (ids[1],)).fetchone()[0])
    v["porLado"]["a"]["veredicto"] = "acierto" if v["porLado"]["a"]["veredicto"] != "acierto" else "fallo"
    con.execute("UPDATE parte_cowork SET veredicto_json=?, actualizado_en=datetime('now','+1 minute') "
                "WHERE fixture_id=?", (json.dumps(v), ids[1]))
    con.commit()
    calculos.clear()
    corregido = con_cache()
    check("un veredicto corregido se ve enseguida (idéntico a desde cero)", corregido == desde_cero())

    # un marcador nuevo en sad.db (corrección de la API): ese caso se rehace
    sq = sqlite3.connect(os.path.join(tmp, "sad.db"))
    sq.execute("UPDATE fixtures SET goals_home = goals_home + 1, fulltime_home = COALESCE(fulltime_home, goals_home) + 1 "
               "WHERE id=?", (ids[2],))
    sq.commit()
    sq.close()
    calculos.clear()
    marcador = con_cache()
    check("un marcador corregido rehace ese caso", ids[2] in calculos, calculos[:5])
    check("…y da lo mismo que desde cero", marcador == desde_cero())

    # las historias compartidas: la misma historia, y una copia que se puede tocar
    from backend.app import constantes_de, historias_compartidas, niveles_de
    suelta = constantes_de(tid, 500, antes="2030-01-01")
    with historias_compartidas():
        a = constantes_de(tid, 500, antes="2030-01-01T00:00:00Z")
        a[0]["k"] = "ensuciado"
        b = constantes_de(tid, 500, antes="2030-01-01 00:00:00")
        nv = niveles_de(tid, 1, antes="2030-01-01")
    check("historias_compartidas: la misma historia que la consulta suelta", b == suelta)
    check("…y tocar lo que devolvió no ensucia la siguiente lectura", b[0].get("k") != "ensuciado")
    check("…también con los niveles", nv == niveles_de(tid, 1, antes="2030-01-01"))

    # una lectura ya calculada no espera detrás del cálculo de OTRA clave
    import threading
    import time as _t
    from backend.analisis.parte import COHORTE
    lecciones.INVENTARIO_TTL_S = 1800
    lecciones._INV_CACHE.clear()
    lecciones._nucleo(400, COHORTE)
    calc = lecciones._calcular_nucleo
    empezo = threading.Event()

    def lento(limite, clave):
        empezo.set()
        _t.sleep(3)
        return calc(limite, clave)
    lecciones._calcular_nucleo = lento
    hilo = threading.Thread(target=lecciones._nucleo, args=(2000, ""))
    hilo.start()
    empezo.wait(5)
    t0 = _t.monotonic()
    lecciones._nucleo(400, COHORTE)
    espera = _t.monotonic() - t0
    hilo.join()
    lecciones._calcular_nucleo = calc
    check("la cohorte ya calculada se lee mientras otra clave (el buscador) se calcula", espera < 1.0, round(espera, 2))
    check("el hilo deja calientes la vigente, todas y el buscador",
          set(lecciones.calentar()) == {f"{COHORTE}·400", "todas·400", "todas·2000"})

    vered.objetivo = original
    print(f"\n{'OK' if not fallos else f'{fallos} FALLAS'}")
    raise SystemExit(1 if fallos else 0)


if __name__ == "__main__":
    main()
