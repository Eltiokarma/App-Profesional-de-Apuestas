"""Tests del contrato del SAD API contra las DBs de demo.

    python3 -m backend.test_api
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


def main():
    tmp = tempfile.mkdtemp(prefix="sad_demo_")
    from backend.seed_demo import seed

    seed(tmp)
    os.environ["SAD_DATA_DIR"] = tmp

    import backend.db as dbmod

    dbmod.BASE_DIR = tmp  # el módulo pudo importarse antes de fijar el env

    from fastapi.testclient import TestClient
    import backend.app as appmod
    from backend.app import app

    # la suite lanza >120 requests seguidas: sin esto el limitador (120/min) la cortaría
    appmod.RATE_LIMIT = 0

    c = TestClient(app)
    A = "/api/v1"

    # /health
    h = c.get(A + "/health").json()
    check("/health ok + dbOk + lastPipelineRun", h["status"] == "ok" and h["dbOk"] and h["lastPipelineRun"], h)

    # /fixtures
    fx = c.get(A + "/fixtures?limit=200").json()
    check("/fixtures devuelve 122 (120 terminados + vivo + programado)", len(fx) == 122, len(fx))
    estados = {f["estado"] for f in fx}
    check("estados en_vivo/finalizado/programado presentes", estados == {"en_vivo", "finalizado", "programado"}, estados)
    vivo = next(f for f in fx if f["estado"] == "en_vivo")
    check("vivo: minuto 67 y marcador 1-0", vivo["minuto"] == 67 and vivo["golesLocal"] == 1 and vivo["golesVisitante"] == 0, vivo)
    check("fecha ISO con T", "T" in vivo["fecha"], vivo["fecha"])
    check("liga por nombre", vivo["liga"] == "LaLiga", vivo["liga"])
    check("fixture trae bandera y logo de la liga", vivo["ligaBandera"] and vivo["ligaLogo"], {k: vivo[k] for k in ("ligaBandera", "ligaLogo")})
    ucl = next(f for f in fx if f["ligaId"] == 2)
    check("copa internacional: ligaBandera null pero ligaLogo presente", ucl["ligaBandera"] is None and ucl["ligaLogo"], ucl["liga"])
    # filtro estado en SQL: se aplica antes del LIMIT (con limit=1 debe encontrar igual)
    fin1 = c.get(A + "/fixtures?estado=finalizado&limit=1").json()
    check("fixtures?estado=finalizado&limit=1 encuentra pese al LIMIT", len(fin1) == 1 and fin1[0]["estado"] == "finalizado", fin1)
    prog = c.get(A + "/fixtures?estado=programado&limit=200").json()
    check("fixtures?estado=programado: solo programados", bool(prog) and all(f["estado"] == "programado" for f in prog), len(prog))
    check("fixtures?estado=inválido → 422", c.get(A + "/fixtures?estado=jugando").status_code == 422)
    asc = c.get(A + "/fixtures?orden=asc&limit=200").json()
    check("fixtures?orden=asc: fechas ascendentes", len(asc) == 122 and all(asc[i]["fecha"] <= asc[i + 1]["fecha"] for i in range(len(asc) - 1)))
    hoy_demo = vivo["fecha"][:10]
    dd = c.get(A + f"/fixtures?desde={hoy_demo}&limit=200").json()
    check("fixtures?desde: solo fechas >= desde", bool(dd) and len(dd) < 122 and all(f["fecha"][:10] >= hoy_demo for f in dd), len(dd))
    check("fixtures?orden=inválido → 422", c.get(A + "/fixtures?orden=random").status_code == 422)
    uno = c.get(A + f"/fixtures/{vivo['id']}").json()
    check("/fixtures/{id} coincide", uno["id"] == vivo["id"] and uno["local"]["nombre"] == vivo["local"]["nombre"])
    check("equipos del fixture traen logo (nullable)", "logo" in uno["local"] and "logo" in uno["visitante"], uno["local"])
    check("/fixtures/999999 → 404", c.get(A + "/fixtures/999999").status_code == 404)

    betis = vivo["local"]["id"]

    # /niveles
    nv = c.get(A + f"/niveles/{betis}?limit=5").json()
    check("/niveles: 5 filas desc con bin/etiqueta", len(nv) == 5 and 0 <= nv[0]["bin"] <= 9 and nv[0]["binEtiqueta"], nv[:1])
    check("niveles orden desc por fecha", nv[0]["fecha"] >= nv[-1]["fecha"])

    # /constantes — invariantes del motor
    ct = c.get(A + f"/constantes/{betis}?limit=50").json()
    check("/constantes: 40 filas (historia completa)", len(ct) == 40, len(ct))
    c0 = ct[0]
    check("constantes: fusión = k⁺ + k⁻", abs(c0["fusion"]["k"] - (c0["k"]["positivo"] + c0["k"]["negativo"])) < 1e-9)
    inv = all(
        not (r["k"]["positivo"] != 0 and r["k"]["negativo"] != 0) and r["k"]["golesRecibido"] >= 0 for r in ct
    )
    check("invariantes: k⁺/k⁻ excluyentes y k_gR ≥ 0", inv)
    check("constantes traen rival y goles", c0["rivalNombre"] and c0["golesFavor"] is not None, c0)
    conds = {r["condicion"] for r in ct}
    check("condicion Local/Visita", conds == {"Local", "Visita"}, conds)

    # Doble Oportunidad (§3.6): familia k_dc servida por el contrato
    check("k_dc: fusion.kDc = k.dc (pasa tal cual, sin ±)", all(abs(r["fusion"]["kDc"] - r["k"]["dc"]) < 1e-9 for r in ct))
    check("k_dc: acumuladores no-negativos", all(r["k"]["dc"] >= 0 and r["k"]["dcLocal"] >= 0 and r["k"]["dcVisita"] >= 0 for r in ct))
    check("k_dc: hay racha activa en algún partido", any(r["k"]["dc"] > 0 for r in ct))
    check("k_dc: la derrota resetea a 0", all(r["k"]["dc"] == 0 for r in ct if r["golesFavor"] < r["golesContra"]))
    check("q_dc: no-negativo y 0 en toda derrota", all(r["q"]["dc"] >= 0 and (r["q"]["dc"] == 0 or r["golesFavor"] >= r["golesContra"]) for r in ct))

    # Márgenes (§3.7): familias por margen exacto de goles
    fam_m = [f"{s}{b}" for s in ("vic", "der") for b in (1, 2, 3)]
    check("márgenes: fusion.kXxx = k.xxx (pasa tal cual)", all(abs(r["fusion"]["k" + m[0].upper() + m[1:]] - r["k"][m]) < 1e-9 for r in ct for m in fam_m))
    check("márgenes: acumuladores no-negativos", all(r["k"][m] >= 0 for r in ct for m in fam_m))
    check("márgenes: máx un bucket del mismo signo activo", all(
        sum(r["k"][f"vic{b}"] > 0 for b in (1, 2, 3)) <= 1 and sum(r["k"][f"der{b}"] > 0 for b in (1, 2, 3)) <= 1 for r in ct))
    check("márgenes: victoria anula derrotas, derrota anula victorias, empate anula todo", all(
        (all(r["k"][f"der{b}"] == 0 for b in (1, 2, 3)) if r["golesFavor"] > r["golesContra"] else all(r["k"][f"vic{b}"] == 0 for b in (1, 2, 3)) if r["golesFavor"] < r["golesContra"] else all(r["k"][f"vic{b}"] == 0 and r["k"][f"der{b}"] == 0 for b in (1, 2, 3)))
        for r in ct))
    check("márgenes: hay racha activa en alguna familia", any(r["k"][m] > 0 for r in ct for m in fam_m))

    # /predicciones — §5
    p = c.get(A + f"/predicciones/{vivo['id']}").json()
    check(
        "prediccion: gap y señal para ambos",
        p["local"]["gap"] is not None and p["local"]["senal"] in ("fuerte", "leve", "equilibrio") and p["visitante"]["gap"] is not None,
        p,
    )
    check("gapDiff = local − visitante", abs(p["gapDiff"] - (p["local"]["gap"] - p["visitante"]["gap"])) < 1e-6)
    check("μ recortado a [0,3]", 0 <= p["local"]["ptsEsperados"] <= 3)

    # /analisis-prepartido
    an = c.get(A + f"/analisis-prepartido/{vivo['id']}").json()
    check(
        "analisis: niveles + constantes + prediccion + resumen",
        an["niveles"]["local"]["binEtiqueta"] and an["constantes"]["local"] and an["prediccion"]["fixtureId"] == vivo["id"] and "recibe a" in an["resumen"],
    )

    # /equipos/{id}/stats — calculadas de fixtures
    st = c.get(A + f"/equipos/{betis}/stats").json()
    check("stats: 40 PJ y forma de 5", st["partidosJugados"] == 40 and len(st["forma"]) == 5, st)
    check("stats: promedios plausibles", 0 < st["golesFavorProm"] < 4 and 0 < st["golesContraProm"] < 4, st)
    check("stats: puntos coherentes (0–120)", 0 <= st["puntos"] <= 3 * st["partidosJugados"])
    check("stats: xG/posesión null en v0", st["xgProm"] is None and st["posesionProm"] is None)
    check("/equipos/999999/stats → 404", c.get(A + "/equipos/999999/stats").status_code == 404)

    # /ligas/{id}
    lg = c.get(A + "/ligas/140").json()
    check("/ligas/140: nombre, país y bandera", lg["nombre"] == "LaLiga" and lg["pais"] == "Spain" and lg["bandera"], lg)
    check("/ligas/140: temporadas capturadas desc", lg["temporadas"] == [2025], lg.get("temporadas"))
    lg2 = c.get(A + "/ligas/2").json()
    check("/ligas/2 (copa): bandera null, logo presente", lg2["bandera"] is None and lg2["logo"], lg2)
    check("/ligas/999999 → 404", c.get(A + "/ligas/999999").status_code == 404)

    # /fixtures?temporada
    ft = c.get(A + "/fixtures?ligaId=140&temporada=2025&limit=200").json()
    check("fixtures?temporada: filtra por temporada de la liga", ft and all(f["temporada"] == 2025 for f in ft), len(ft))
    check("fixtures?temporada sin datos → lista vacía", c.get(A + "/fixtures?ligaId=140&temporada=1999").json() == [])

    # /ligas/{id}/standings
    tb = c.get(A + "/ligas/140/standings").json()
    check("standings: 6 equipos ordenados", len(tb) == 6 and tb[0]["posicion"] == 1 and tb[-1]["posicion"] == 6, [t["nombre"] for t in tb])
    check("standings: orden por puntos desc", all(tb[i]["puntos"] >= tb[i + 1]["puntos"] for i in range(5)))
    check("standings: Real Madrid arriba de Sevilla", next(t["posicion"] for t in tb if "Madrid" in t["nombre"]) < next(t["posicion"] for t in tb if "Sevilla" in t["nombre"]))
    suma_pj = sum(t["partidosJugados"] for t in tb)
    check("standings: 216 participaciones (108 de liga × 2; 12 son UCL)", suma_pj == 216, suma_pj)

    # /cuotas — mapeo API-Football → contrato y media entre bookmakers
    q = c.get(A + f"/cuotas/{vivo['id']}").json()
    mercados = {r["mercado"] for r in q}
    check("cuotas: 5 mercados mapeados", mercados == {"1x2", "dc", "ou", "ah", "btts"}, mercados)
    check("cuotas: 12 selecciones (3+3+2+2+2)", len(q) == 12, len(q))
    check("cuotas plausibles (1.0–20)", all(1.0 < r["cuota"] < 20 for r in q))
    sin = c.get(A + "/cuotas/900001").json()
    check("fixture sin odds → lista vacía", sin == [], sin)

    # /fixtures/{id}/live — en vivo real (fase 3): marcador, minuto y odds_live
    lv = c.get(A + f"/fixtures/{vivo['id']}/live").json()
    check("live: estado en_vivo + minuto 67", lv["estado"] == "en_vivo" and lv["minuto"] == 67, lv)
    check("live: marcador presente", lv["golesLocal"] is not None and lv["golesVisitante"] is not None, lv)
    check("live: cuotas de la última captura (1X2 + O/U del catálogo live)",
          len(lv["cuotas"]) == 5 and {(q2["mercado"], q2["seleccion"]) for q2 in lv["cuotas"]}
          == {("1x2", "1"), ("1x2", "X"), ("1x2", "2"), ("ou", "O"), ("ou", "U")}, lv["cuotas"])
    check("live: la suspendida viene marcada", any(q2["suspendida"] for q2 in lv["cuotas"]), lv["cuotas"])
    check("live: serie con minutos asc y sin suspendidas",
          len(lv["serie"]) > 6 and all(not any(p["minuto"] == 67 and p["seleccion"] == "2" for p in lv["serie"]) for _ in [0])
          and [p["minuto"] for p in lv["serie"]] == sorted(p["minuto"] for p in lv["serie"]), len(lv["serie"]))
    check("live: actualizadoEn presente", bool(lv["actualizadoEn"]), lv["actualizadoEn"])
    check("live: eventos mapeados (gol/amarilla/roja; subst y penal fallado fuera)",
          [(e["tipo"], e["minuto"]) for e in lv["eventos"]]
          == [("amarilla", 12), ("gol", 34), ("gol", 51), ("roja", 60)], lv["eventos"])
    check("live: eventos con jugador y equipo", all(e["jugador"] and e["equipoId"] for e in lv["eventos"]))
    fin = next(f for f in fx if f["estado"] == "finalizado")
    lv0 = c.get(A + f"/fixtures/{fin['id']}/live").json()
    check("live de fixture sin odds_live → cuotas y serie vacías",
          lv0["cuotas"] == [] and lv0["serie"] == [], lv0)
    check("live de fixture inexistente → 404", c.get(A + "/fixtures/999999/live").status_code == 404)

    # /cuotas/{id}/casas — comparador: cuota de cada casa, la mejor marcada
    cc = c.get(A + f"/cuotas/{vivo['id']}/casas").json()
    check("casas: 36 filas (12 selecciones × 3 casas)", len(cc) == 36, len(cc))
    check("casas: claves del contrato", cc and all(
        k in cc[0] for k in ("fixtureId", "mercado", "seleccion", "casaId", "casa", "cuota", "mejor")), cc[:1])
    unos = [r for r in cc if r["mercado"] == "1x2" and r["seleccion"] == "1"]
    check("casas: 3 casas por selección, orden cuota desc",
          len(unos) == 3 and unos[0]["cuota"] >= unos[1]["cuota"] >= unos[2]["cuota"], unos)
    check("casas: mejor = la cuota más alta", unos[0]["mejor"] and all(
        r["mejor"] == (r["cuota"] >= unos[0]["cuota"] - 1e-9) for r in unos), unos)
    check("casas de fixture sin odds → lista vacía", c.get(A + "/cuotas/900001/casas").json() == [])

    # /cuotas/{id}/historial — snapshots prepartido (fase 1 tiempo real)
    h = c.get(A + f"/cuotas/{vivo['id']}/historial").json()
    check("historial: 36 puntos (12 selecciones × 3 capturas)", len(h) == 36, len(h))
    check("historial: claves del contrato", h and all(
        k in h[0] for k in ("fixtureId", "mercado", "seleccion", "cuota", "casas", "capturadoEn")), h[:1])
    capturas = [r["capturadoEn"] for r in h]
    check("historial: asc por captura", capturas == sorted(capturas))
    serie_1 = [r["cuota"] for r in h if r["mercado"] == "1x2" and r["seleccion"] == "1"]
    q_1 = next(r["cuota"] for r in q if r["mercado"] == "1x2" and r["seleccion"] == "1")
    check("historial: 3 capturas por selección", len(serie_1) == 3, serie_1)
    check("historial: última captura ≈ cuota base de /cuotas", abs(serie_1[-1] - q_1) < 0.35, (serie_1[-1], q_1))
    hsin = c.get(A + "/cuotas/900001/historial").json()
    check("historial de fixture sin odds → lista vacía", hsin == [], hsin)

    # historial por casa de referencia
    fu = c.get(A + f"/cuotas/{vivo['id']}/historial/fuentes").json()
    check("fuentes del historial: las 3 casas del seed", fu == ["1xBet", "Bet365", "Pinnacle"], fu)
    hb = c.get(A + f"/cuotas/{vivo['id']}/historial?casa=bet365").json()
    check("historial?casa= (case-insensitive): 36 puntos propios", len(hb) == 36, len(hb))
    check("historial por casa distinto de la media",
          [r["cuota"] for r in hb] != [r["cuota"] for r in h])
    check("fuentes de fixture sin historial → []", c.get(A + "/cuotas/900001/historial/fuentes").json() == [])

    # mercados de 1er tiempo (trampas del seed, cuota 9.99): si cuota_key los
    # dejara pasar, la serie alternaría partido/medio tiempo (zigzag)
    check("1er tiempo fuera de /cuotas", all(r["cuota"] != 9.99 for r in q))
    check("1er tiempo fuera de /casas", all(r["cuota"] != 9.99 for r in cc))
    check("1er tiempo fuera del historial (media y por casa)",
          all(r["cuota"] != 9.99 for r in h + hb))
    check("1er tiempo fuera del live (cuotas y serie)",
          all(p["cuota"] != 9.99 for p in lv["cuotas"] + lv["serie"]))

    # cuotas prepartido guardadas en partidos PASADOS
    pasados = [f for f in fx if f["estado"] == "finalizado"]
    con_odds = [f for f in pasados if c.get(A + f"/cuotas/{f['id']}").json()]
    check("hay pasados con cuotas capturadas (≥8)", len(con_odds) >= 8, len(con_odds))

    # /equipos?buscar= — búsqueda inteligente
    b1 = c.get(A + "/equipos?buscar=bet").json()
    check("buscar 'bet' → Real Betis primero", b1 and "Betis" in b1[0]["nombre"], b1[:1])
    check("buscar: DTO incluye logo (nullable)", "logo" in b1[0], b1[:1])
    b2 = c.get(A + "/equipos?buscar=atletico").json()
    check("buscar sin tilde 'atletico' → Atlético", b2 and "Atlético" in b2[0]["nombre"], b2[:1])
    check("buscar corto (1 char) → 422", c.get(A + "/equipos?buscar=a").status_code == 422)
    check("buscar demasiado largo (>60) → 422", c.get(A + "/equipos?buscar=" + "a" * 61).status_code == 422)

    # /fixtures?equipoId=
    fxb = c.get(A + f"/fixtures?equipoId={betis}&limit=200").json()
    ok_eq = all(f["local"]["id"] == betis or f["visitante"]["id"] == betis for f in fxb)
    check("fixtures?equipoId: todos incluyen al equipo (41: 40+vivo)", ok_eq and len(fxb) == 41, len(fxb))

    # /fixtures?equipoId&rivalId — enfrentamientos directos (H2H)
    rival = next(f["visitante"]["id"] if f["local"]["id"] == betis else f["local"]["id"] for f in fxb if f["estado"] == "finalizado")
    h2h = c.get(A + f"/fixtures?equipoId={betis}&rivalId={rival}&limit=200").json()
    ok_h2h = h2h and all({f["local"]["id"], f["visitante"]["id"]} == {betis, rival} for f in h2h)
    check("fixtures?rivalId: todas las filas son entre ambos equipos", ok_h2h, len(h2h))
    h2h_inv = c.get(A + f"/fixtures?equipoId={rival}&rivalId={betis}&limit=200").json()
    check("fixtures?rivalId: simétrico al invertir equipoId↔rivalId", [f["id"] for f in h2h] == [f["id"] for f in h2h_inv])
    h2h_fin = c.get(A + f"/fixtures?equipoId={betis}&rivalId={rival}&estado=finalizado&limit=200").json()
    check("fixtures?rivalId+finalizado: solo finalizados", h2h_fin and all(f["estado"] == "finalizado" for f in h2h_fin), len(h2h_fin))
    check("fixtures?rivalId sin equipoId → 422", c.get(A + f"/fixtures?rivalId={rival}").status_code == 422)

    # constantes: flag de torneo internacional presente y con casos True
    intl = [r for r in ct if r.get("esInternacional")]
    check("constantes traen ligaId/esInternacional (hay UCL)", "ligaId" in c0 and len(intl) >= 3, len(intl))

    # auth bearer opcional (SAD_API_TOKEN)
    appmod.API_TOKEN = "token-de-prueba"
    check("auth: sin token → 401", c.get(A + "/fixtures?limit=1").status_code == 401)
    check("auth: token incorrecto → 401", c.get(A + "/fixtures?limit=1", headers={"Authorization": "Bearer malo"}).status_code == 401)
    ok_auth = c.get(A + "/fixtures?limit=1", headers={"Authorization": "Bearer token-de-prueba"})
    check("auth: token correcto → 200", ok_auth.status_code == 200 and ok_auth.json())
    check("auth: /health queda libre", c.get(A + "/health").status_code == 200)
    appmod.API_TOKEN = ""
    check("auth: sin SAD_API_TOKEN la API queda abierta", c.get(A + "/fixtures?limit=1").status_code == 200)

    # rate limit por IP (SAD_RATE_LIMIT)
    appmod.RATE_LIMIT = 3
    appmod._hits.clear()
    codes = [c.get(A + "/health").status_code for _ in range(4)]
    check("rate limit: 3 pasan y la 4ª → 429", codes == [200, 200, 200, 429], codes)
    r = c.get(A + "/health")
    check("rate limit: 429 con Retry-After: 60", r.status_code == 429 and r.headers.get("retry-after") == "60", dict(r.headers))
    appmod.RATE_LIMIT = 0
    appmod._hits.clear()
    check("rate limit: con 0 queda apagado", c.get(A + "/health").status_code == 200)

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
