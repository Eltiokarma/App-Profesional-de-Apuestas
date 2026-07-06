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
    from backend.app import app

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
    # filtro estado en SQL: se aplica antes del LIMIT (con limit=1 debe encontrar igual)
    fin1 = c.get(A + "/fixtures?estado=finalizado&limit=1").json()
    check("fixtures?estado=finalizado&limit=1 encuentra pese al LIMIT", len(fin1) == 1 and fin1[0]["estado"] == "finalizado", fin1)
    prog = c.get(A + "/fixtures?estado=programado&limit=200").json()
    check("fixtures?estado=programado: solo programados", bool(prog) and all(f["estado"] == "programado" for f in prog), len(prog))
    check("fixtures?estado=inválido → 422", c.get(A + "/fixtures?estado=jugando").status_code == 422)
    uno = c.get(A + f"/fixtures/{vivo['id']}").json()
    check("/fixtures/{id} coincide", uno["id"] == vivo["id"] and uno["local"]["nombre"] == vivo["local"]["nombre"])
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

    # cuotas prepartido guardadas en partidos PASADOS
    pasados = [f for f in fx if f["estado"] == "finalizado"]
    con_odds = [f for f in pasados if c.get(A + f"/cuotas/{f['id']}").json()]
    check("hay pasados con cuotas capturadas (≥8)", len(con_odds) >= 8, len(con_odds))

    # /equipos?buscar= — búsqueda inteligente
    b1 = c.get(A + "/equipos?buscar=bet").json()
    check("buscar 'bet' → Real Betis primero", b1 and "Betis" in b1[0]["nombre"], b1[:1])
    b2 = c.get(A + "/equipos?buscar=atletico").json()
    check("buscar sin tilde 'atletico' → Atlético", b2 and "Atlético" in b2[0]["nombre"], b2[:1])
    check("buscar corto (1 char) → 422", c.get(A + "/equipos?buscar=a").status_code == 422)
    check("buscar demasiado largo (>60) → 422", c.get(A + "/equipos?buscar=" + "a" * 61).status_code == 422)

    # /fixtures?equipoId=
    fxb = c.get(A + f"/fixtures?equipoId={betis}&limit=200").json()
    ok_eq = all(f["local"]["id"] == betis or f["visitante"]["id"] == betis for f in fxb)
    check("fixtures?equipoId: todos incluyen al equipo (41: 40+vivo)", ok_eq and len(fxb) == 41, len(fxb))

    # constantes: flag de torneo internacional presente y con casos True
    intl = [r for r in ct if r.get("esInternacional")]
    check("constantes traen ligaId/esInternacional (hay UCL)", "ligaId" in c0 and len(intl) >= 3, len(intl))

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
