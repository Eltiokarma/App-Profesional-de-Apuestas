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
    check("fixtures acepta limit=500 (días con amistosos globales)",
          c.get(A + "/fixtures?limit=500").status_code == 200)
    fx = c.get(A + "/fixtures?limit=200").json()
    check("/fixtures devuelve 125 (120 terminados + vivo + 4 programados)", len(fx) == 125, len(fx))
    estados = {f["estado"] for f in fx}
    check("estados en_vivo/finalizado/programado presentes", estados == {"en_vivo", "finalizado", "programado"}, estados)
    vivo = next(f for f in fx if f["estado"] == "en_vivo")
    check("vivo: minuto 67 y marcador 1-0", vivo["minuto"] == 67 and vivo["golesLocal"] == 1 and vivo["golesVisitante"] == 0, vivo)
    check("fecha ISO con T", "T" in vivo["fecha"], vivo["fecha"])
    check("liga por nombre", vivo["liga"] == "LaLiga", vivo["liga"])
    check("fixture trae bandera y logo de la liga", vivo["ligaBandera"] and vivo["ligaLogo"], {k: vivo[k] for k in ("ligaBandera", "ligaLogo")})
    check("fixture trae ligaPais (desambigua torneos homónimos)", vivo["ligaPais"] == "Spain", vivo.get("ligaPais"))
    ucl = next(f for f in fx if f["ligaId"] == 2)
    check("copa internacional: ligaBandera null pero ligaLogo presente", ucl["ligaBandera"] is None and ucl["ligaLogo"], ucl["liga"])
    # filtro estado en SQL: se aplica antes del LIMIT (con limit=1 debe encontrar igual)
    fin1 = c.get(A + "/fixtures?estado=finalizado&limit=1").json()
    check("fixtures?estado=finalizado&limit=1 encuentra pese al LIMIT", len(fin1) == 1 and fin1[0]["estado"] == "finalizado", fin1)
    prog = c.get(A + "/fixtures?estado=programado&limit=200").json()
    check("fixtures?estado=programado: solo programados", bool(prog) and all(f["estado"] == "programado" for f in prog), len(prog))
    check("fixtures?estado=inválido → 422", c.get(A + "/fixtures?estado=jugando").status_code == 422)
    asc = c.get(A + "/fixtures?orden=asc&limit=200").json()
    check("fixtures?orden=asc: fechas ascendentes", len(asc) == 125 and all(asc[i]["fecha"] <= asc[i + 1]["fecha"] for i in range(len(asc) - 1)))
    hoy_demo = vivo["fecha"][:10]
    dd = c.get(A + f"/fixtures?desde={hoy_demo}&limit=200").json()
    check("fixtures?desde: solo fechas >= desde", bool(dd) and len(dd) < 125 and all(f["fecha"][:10] >= hoy_demo for f in dd), len(dd))
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
    check(
        "gap ajustado por calendario para ambos, señal válida",
        p["local"]["gapAjustado"] is not None and p["visitante"]["gapAjustado"] is not None
        and p["local"]["senalAjustada"] in ("fuerte", "leve", "equilibrio"),
        p,
    )
    check(
        "gapAjustado = esperadosAjustados − recientes",
        abs(p["local"]["gapAjustado"] - (p["local"]["ptsEsperadosAjustados"] - p["local"]["ptsRecientes"])) < 1e-3,
        p["local"],
    )
    check("μ ajustado recortado a [0,3]", 0 <= p["local"]["ptsEsperadosAjustados"] <= 3)
    check(
        "gapDiffAjustado = local − visitante",
        abs(p["gapDiffAjustado"] - (p["local"]["gapAjustado"] - p["visitante"]["gapAjustado"])) < 1e-3,
    )
    # camino de recuperación (§5 v2): el vivo es Betis-Sevilla; el seed pone a
    # Betis 2 futuros (Barça en Champions +2d, Villarreal +5d) y a Sevilla 1
    pl, pv = p["local"], p["visitante"]
    check("camino: Betis con 2 próximos, Sevilla con 1", len(pl["proximos"]) == 2 and len(pv["proximos"]) == 1,
          (len(pl["proximos"]), len(pv["proximos"])))
    check("camino: primer próximo de Betis es internacional (+2d de descanso)",
          pl["proximos"][0]["esInternacional"] and pl["proximos"][0]["diasDescanso"] == 2, pl["proximos"])
    check("camino: segundo próximo de Betis descansa 3 días tras el primero",
          not pl["proximos"][1]["esInternacional"] and pl["proximos"][1]["diasDescanso"] == 3, pl["proximos"])
    check("camino: rival con nombre y μ esperada en [0,3]",
          all(x["rival"]["nombre"] and 0 <= x["muEsperado"] <= 3 for x in pl["proximos"] + pv["proximos"]))
    check("camino: recuperabilidad = media de μ esperadas",
          abs(pl["recuperabilidad"] - sum(x["muEsperado"] for x in pl["proximos"]) / 2) < 1e-3, pl)
    check("camino: señal de calendario válida",
          pl["senalCalendario"] in ("blando", "neutro", "duro") and pv["senalCalendario"] in ("blando", "neutro", "duro"))
    check("camino: μ del partido en [0,3] y trampa booleana",
          0 <= pl["muPartido"] <= 3 and isinstance(pl["partidoTrampa"], bool) and isinstance(pv["partidoTrampa"], bool))
    # el programado (Madrid-Barça) va DESPUÉS del vivo: Barça tiene próximo (Betis
    # en Champions al día siguiente) y Madrid ninguno → recuperabilidad null
    prog_fx = min((f for f in fx if f["estado"] == "programado"), key=lambda f: f["fecha"])  # Madrid-Barça (+1d)
    pp = c.get(A + f"/predicciones/{prog_fx['id']}").json()
    check("camino: sin próximos → proximos [], recuperabilidad y señal null",
          pp["local"]["proximos"] == [] and pp["local"]["recuperabilidad"] is None and pp["local"]["senalCalendario"] is None,
          pp["local"])
    check("camino: Barça tiene un próximo internacional al día siguiente",
          len(pp["visitante"]["proximos"]) == 1 and pp["visitante"]["proximos"][0]["esInternacional"]
          and pp["visitante"]["proximos"][0]["diasDescanso"] == 1, pp["visitante"])

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

    # CASAS DUPLICADAS (el zigzag real del 14/07): el upsert viejo acumulaba
    # filas de la misma casa (ids nulos / variantes '1X' vs 'Home/Draw')
    import sqlite3 as _sql
    with _sql.connect(os.path.join(tmp, "sad.db")) as _sd:
        # fila fantasma: 1xBet duplicada con otra cuota para la misma selección
        _sd.execute(
            "INSERT INTO odds (fixture_id, league_id, bookmaker_id, bookmaker_name, "
            "bet_id, bet_name, value, odd) VALUES (?, 140, 8, '1xBet', NULL, 'Match Winner', '1', 9.5)",
            (vivo["id"],))
        _sd.commit()
    cc_dup = c.get(A + f"/cuotas/{vivo['id']}/casas").json()
    unos_dup = [r for r in cc_dup if r["mercado"] == "1x2" and r["seleccion"] == "1"]
    check("casas: la casa duplicada sale UNA sola vez (última fila gana)",
          len(unos_dup) == 3 and sum(1 for r in unos_dup if r["casa"].lower() == "1xbet") == 1
          and next(r["cuota"] for r in unos_dup if r["casa"].lower() == "1xbet") == 9.5,
          unos_dup)
    # limpiar_odds_duplicadas purga la fila vieja del volumen (queda la nueva)
    from backend.ingesta.extractor import guardar_odds, limpiar_odds_duplicadas
    with _sql.connect(os.path.join(tmp, "sad.db")) as _sd:
        antes = _sd.execute("SELECT COUNT(*) FROM odds WHERE fixture_id=?", (vivo["id"],)).fetchone()[0]
        borradas = limpiar_odds_duplicadas(_sd)
        despues = _sd.execute("SELECT COUNT(*) FROM odds WHERE fixture_id=?", (vivo["id"],)).fetchone()[0]
    check("limpiar_odds_duplicadas: purga la gemela y conserva la reciente",
          borradas >= 1 and despues == antes - 1, (antes, borradas, despues))
    # guardar_odds ya no acumula: ids nulos + variante del valor → misma fila
    with _sql.connect(os.path.join(tmp, "sad.db")) as _sd:
        item_a = {"league": {"id": 140}, "bookmakers": [{"id": None, "name": "1xBet", "bets": [
            {"id": None, "name": "Double Chance", "values": [{"value": "Home/Draw", "odd": "1.40"}]}]}]}
        item_b = {"league": {"id": 140}, "bookmakers": [{"id": None, "name": "1xBet", "bets": [
            {"id": None, "name": "Double Chance", "values": [{"value": "1X", "odd": "1.55"}]}]}]}
        guardar_odds(_sd, 900777, [item_a])
        guardar_odds(_sd, 900777, [item_b])
        filas_dc = _sd.execute(
            "SELECT value, odd FROM odds WHERE fixture_id=900777").fetchall()
        _sd.execute("DELETE FROM odds WHERE fixture_id=900777")
        _sd.execute("DELETE FROM odds_history WHERE fixture_id=900777")
        _sd.commit()
    check("guardar_odds: ids nulos + variante '1X' NO acumulan filas (1 fila, cuota nueva)",
          len(filas_dc) == 1 and filas_dc[0][0] == "Home/Draw" and filas_dc[0][1] == 1.55,
          filas_dc)

    # análisis EFE (capa backend/analisis/, modo demo: sin API ni créditos)
    os.environ["SAD_EFE_DEMO"] = "1"
    from backend.analisis import db as efedb
    if os.path.exists(efedb.ruta()):
        os.remove(efedb.ruta())  # corrida limpia: sin restos de tests previos
    gen = c.post(A + "/analisis/efe", json={"fixtureId": vivo["id"]}).json()
    check("efe: POST responde estado listo (demo síncrono)", gen["estado"] == "listo", gen.get("estado"))
    ae = gen["registro"]
    check("efe: registro con claves del contrato",
          all(k in ae for k in ("tipo", "fixtureId", "estado", "versionEfe", "creadoEn", "resultado")), ae.keys())
    check("efe: tipo/estado/versión", ae["tipo"] == "efe" and ae["estado"] == "preliminar"
          and ae["versionEfe"] == "1.5", ae)
    r_efe = ae["resultado"]
    check("efe: comparativo con ambos equipos y clasificación",
          r_efe["equipos"]["a"]["clasificacion"] in ("FORMADO", "EN_FORMACION", "SIN_FORMACION")
          and r_efe["equipos"]["b"]["porcentaje"] > 0, r_efe["equipos"]["b"]["clasificacion"])
    check("efe: matchup y alertas presentes",
          r_efe["matchup_h"]["diagnostico"] in ("FAVORABLE", "NEUTRO", "DESFAVORABLE")
          and isinstance(r_efe["alertas"], list))
    ae2 = c.post(A + "/analisis/efe", json={"fixtureId": vivo["id"]}).json()
    check("efe repetido → el mismo (caché, 0 créditos)",
          ae2["estado"] == "listo" and ae2["registro"]["creadoEn"] == ae["creadoEn"])
    est = c.get(A + f"/analisis/efe/estado/{vivo['id']}").json()
    check("efe/estado con análisis → listo con registro",
          est["estado"] == "listo" and est["registro"]["creadoEn"] == ae["creadoEn"], est.get("estado"))
    check("efe/estado sin trabajo ni análisis → nada",
          c.get(A + "/analisis/efe/estado/900001").json()["estado"] == "nada")
    ap = c.get(A + f"/analisis/partido/{vivo['id']}").json()
    check("analisis/partido lista el efe", len(ap) == 1 and ap[0]["tipo"] == "efe", len(ap))
    check("analisis/partido sin análisis → []",
          c.get(A + "/analisis/partido/900001").json() == [])
    # normalizador: el JSON del modelo (por instrucción) se ajusta al contrato
    from backend.analisis.cliente import _extraer_json
    from backend.analisis.esquemas import EFE_COMPARATIVO, ajustar
    aj = ajustar({"partido": {"equipo_a": "X", "torneo": None},
                  "alertas": [{"codigo": "T.54", "equipo": None}]}, EFE_COMPARATIVO)
    check("ajustar: rellena huecos y corrige nulls al contrato",
          aj["partido"]["equipo_a"] == "X" and aj["partido"]["torneo"] == ""
          and aj["equipos"]["a"]["bloques"]["A"]["score"] == 0.0
          and aj["alertas"][0]["tipo"] == "estructural" and aj["lectura_sad"]["paradoja"] == "")
    check("extraer JSON tolera envoltorios markdown",
          _extraer_json('```json\n{"a": 1}\n```') == {"a": 1})
    # el modelo a veces emite cifras como texto: "3.5"/"75%" NO deben volverse 0
    aj2 = ajustar({"equipos": {"a": {"total": "21,25", "porcentaje": "79%",
                                     "bloques": {"A": {"score": "3.5"}}}}}, EFE_COMPARATIVO)
    check("ajustar: strings numéricos se convierten, no se anulan",
          aj2["equipos"]["a"]["total"] == 21.25 and aj2["equipos"]["a"]["porcentaje"] == 79.0
          and aj2["equipos"]["a"]["bloques"]["A"]["score"] == 3.5,
          aj2["equipos"]["a"]["total"])
    # análisis vacíos (ambos equipos en 0) se detectan y no valen como caché
    from backend.analisis.esquemas import analisis_vacio
    vacio = ajustar({}, EFE_COMPARATIVO)
    check("analisis_vacio detecta el comparativo en ceros",
          analisis_vacio(vacio) and not analisis_vacio(ae["resultado"]))
    # autocuración: un vacío guardado (bug antiguo) se purga y deja regenerar
    efedb.guardar_analisis("efe", 900002, "X", "Y", "2026-01-01", "preliminar", vacio, "1.5")
    check("análisis vacío guardado → purgado al leer (regenerable)",
          efedb.analisis_existente("efe", 900002, "preliminar") is None)
    # ...también por la ruta del dashboard (/analisis/partido), que es otra función
    efedb.guardar_analisis("efe", 900003, "X", "Y", "2026-01-01", "preliminar", vacio, "1.5")
    check("análisis vacío → /analisis/partido lo purga y devuelve []",
          c.get(A + "/analisis/partido/900003").json() == [])
    # REGLA DE 90': la matemática usa fulltime_* (un AET con 2-2 en los 90 y
    # 3-2 tras prórroga cuenta como EMPATE), y el filtro incluye AET/PEN
    import sqlite3 as _sql
    import tempfile as _tmp
    from backend.ingesta import pipeline as _pipe
    _f90 = os.path.join(_tmp.mkdtemp(), "sad90.db")
    with _sql.connect(_f90) as _c90:
        _c90.execute("""CREATE TABLE fixtures (id INTEGER PRIMARY KEY, date DATETIME,
            home_team_id INTEGER, away_team_id INTEGER, goals_home INTEGER, goals_away INTEGER,
            fulltime_home INTEGER, fulltime_away INTEGER, status_short TEXT, status_long TEXT,
            league_id INTEGER, league_season INTEGER)""")
        _c90.executemany(
            "INSERT INTO fixtures VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            [(1, "2026-07-01", 10, 20, 3, 2, 2, 2, "AET", "Match Finished After Extra Time", 1, 2026),
             (2, "2026-07-02", 10, 20, 1, 0, 1, 0, "FT", "Match Finished", 1, 2026)])
        _c90.commit()
    _fx90 = _pipe.leer_fixtures(_f90)
    check("K de 90': el AET entra al motor con su marcador de los 90 (2-2)",
          len(_fx90) == 2 and (_fx90[0][4], _fx90[0][5]) == (2, 2)
          and (_fx90[1][4], _fx90[1][5]) == (1, 0),
          [(f[4], f[5]) for f in _fx90])
    # datos locales: tabla/resultados/próximos salen de sad.db (costo cero,
    # sin búsqueda web) y entran al análisis como datos_cacheados
    from backend.analisis import motor as efemotor
    loc = efemotor._datos_locales(efemotor._fixture(vivo["id"]))
    check("datos locales desde sad.db: resultados y tabla sin búsqueda web",
          loc["equipo_a"]["resultados"] != "" and loc["equipo_a"]["tabla"] != ""
          and loc["equipo_b"]["resultados"] != "",
          {k: v[:40] for k, v in loc["equipo_a"].items()})
    # la despensa: el esquema del EFE exige el bloque investigacion (mismos
    # tipos que la tabla con TTL) y lo depositado vuelve como dato fresco
    from backend.analisis.esquemas import DESPENSA_EQUIPO
    check("despensa: esquema en sintonía con TIPOS de la db",
          tuple(DESPENSA_EQUIPO["properties"]) == efedb.TIPOS
          and "investigacion" in EFE_COMPARATIVO["properties"])
    efedb.guardar_investigacion("Equipo Despensa", "dt", "DT X, asumió 2024-05, 18 partidos")
    frescos_t, faltan_t = efedb.investigacion_de("Equipo Despensa")
    check("despensa: lo depositado vuelve fresco y ya no se re-busca",
          frescos_t.get("dt") == "DT X, asumió 2024-05, 18 partidos"
          and "dt" not in faltan_t and "tabla" in faltan_t)
    # regenerar (botón): forzar descarta el guardado y emite uno nuevo
    gen3 = c.post(A + "/analisis/efe", json={"fixtureId": vivo["id"], "forzar": True}).json()
    check("efe con forzar → regenera y responde listo",
          gen3["estado"] == "listo" and gen3["registro"]["fixtureId"] == vivo["id"],
          gen3.get("estado"))
    check("tras forzar sigue habiendo UN solo análisis del fixture",
          len(c.get(A + f"/analisis/partido/{vivo['id']}").json()) == 1)
    # timeline comparativo (modo futbol-timeline): mismo patrón asíncrono
    gtl = c.post(A + "/analisis/timeline", json={"fixtureId": vivo["id"]}).json()
    check("timeline: POST responde listo (demo) con tipo timeline",
          gtl["estado"] == "listo" and gtl["registro"]["tipo"] == "timeline",
          gtl.get("estado"))
    rtl = gtl["registro"]["resultado"]
    check("timeline: contrato (2 equipos, eventos en orden, agrupación)",
          len(rtl["equipos"]) == 2 and len(rtl["eventos"]) >= 3
          and rtl["agrupacion"] in ("mes", "trimestre")
          and [e["fecha"] for e in rtl["eventos"]] == sorted(e["fecha"] for e in rtl["eventos"]))
    check("timeline/estado → listo con registro",
          c.get(A + f"/analisis/timeline/estado/{vivo['id']}").json()["estado"] == "listo")
    check("analisis/partido lista efe + timeline",
          sorted(x["tipo"] for x in c.get(A + f"/analisis/partido/{vivo['id']}").json())
          == ["efe", "timeline"])
    check("timeline con forzar → regenera y responde listo",
          c.post(A + "/analisis/timeline", json={"fixtureId": vivo["id"], "forzar": True}).json()["estado"] == "listo")
    from backend.analisis.esquemas import TIMELINE, timeline_vacio
    check("timeline_vacio detecta un timeline sin eventos",
          timeline_vacio(ajustar({}, TIMELINE)) and not timeline_vacio(rtl))
    check("efe de fixture inexistente → 404",
          c.post(A + "/analisis/efe", json={"fixtureId": 999999}).status_code == 404)
    del os.environ["SAD_EFE_DEMO"]
    if not os.environ.get("ANTHROPIC_API_KEY"):
        # sin demo y sin clave: 503 honesto (fixture distinto para no chocar con la caché)
        fin_efe = next(f for f in fx if f["estado"] == "finalizado")
        check("efe sin ANTHROPIC_API_KEY → 503",
              c.post(A + "/analisis/efe", json={"fixtureId": fin_efe["id"]}).status_code == 503)
    # preflight CORS del POST: con solo GET el navegador bloqueaba /analisis/efe
    pre = c.options(A + "/analisis/efe", headers={
        "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST",
    })
    check("CORS: preflight de POST /analisis/efe permitido",
          pre.status_code == 200 and "POST" in pre.headers.get("access-control-allow-methods", ""),
          (pre.status_code, pre.headers.get("access-control-allow-methods")))

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
    check("fixtures?equipoId: todos incluyen al equipo (43: 40+vivo+2 futuros)", ok_eq and len(fxb) == 43, len(fxb))

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
