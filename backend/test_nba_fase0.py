"""NBA · fase 0: la descarga recorta bien, el motor no ve el partido que
predice, y el método detecta un efecto real sin inventar uno (docs/NBA_FASE0.md).

Sin red: todo con datos SINTÉTICOS donde se sabe la verdad.

    python -m backend.test_nba_fase0
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import tempfile

from backend.nba import burbujas, descarga, fase0, ligas, motor

fallas = 0


def check(nombre, ok, detalle=""):
    global fallas
    print(("OK  " if ok else "FALLA ") + nombre + ("" if ok else f" -> {detalle}"))
    fallas += 0 if ok else 1


def _evento(i, fecha, tipo, loc, vis, pl, pv, completo=True, neutral=False):
    return {"id": str(i), "date": fecha, "season": {"year": 2024, "type": tipo},
            "competitions": [{"neutralSite": neutral, "status": {"type": {"completed": completo}},
                              "competitors": [{"homeAway": "home", "team": {"id": str(loc), "abbreviation": "L"}, "score": str(pl)},
                                              {"homeAway": "away", "team": {"id": str(vis), "abbreviation": "V"}, "score": str(pv)}]}]}


def liga_sintetica(semilla: int = 3, temporadas=range(2016, 2021), equipos: int = 10) -> tuple[list[dict], dict]:
    """Equipos con fuerza fija; el resultado sale de la fuerza + localía, y la
    cuota es la probabilidad VERDADERA con 4 % de margen (un mercado perfecto)."""
    rnd = random.Random(semilla)
    fuerza = {t: rnd.gauss(0, 6) for t in range(1, equipos + 1)}
    partidos, cuotas, i = [], {}, 1000
    for temp in temporadas:
        dia = 0
        for vuelta in range(4):
            for a in range(1, equipos + 1):
                for b in range(a + 1, equipos + 1):
                    loc, vis = (a, b) if vuelta % 2 == 0 else (b, a)
                    esperado = fuerza[loc] - fuerza[vis] + 3
                    margen = round(rnd.gauss(esperado, 12)) or 1
                    pl = 105 + max(margen, 0)
                    pv = 105 + max(-margen, 0)
                    dia += 1
                    fecha = f"{temp}-{1 + (dia // 28) % 12:02d}-{1 + dia % 28:02d}T{dia % 24:02d}:00Z"
                    partidos.append({"id": i, "fecha": fecha, "temporada": temp, "tipo": "regular", "localId": loc,
                                     "local": str(loc), "visitaId": vis, "visita": str(vis),
                                     "ptsLocal": pl, "ptsVisita": pv, "neutral": False})
                    p = 1 / (1 + math.exp(-esperado / 7))
                    dl, dv = 1 / (p * 1.02), 1 / ((1 - p) * 1.02)
                    am = lambda d: round((d - 1) * 100) if d >= 2 else round(-100 / (d - 1))  # noqa: E731
                    cuotas[i] = [{"casa": "Sintética", "mlLocal": am(dl), "mlVisita": am(dv),
                                  "spreadLocal": -round(esperado * 2) / 2, "spreadCuotaLocal": -110,
                                  "spreadCuotaVisita": -110}]
                    i += 1
    partidos.sort(key=lambda p: (p["fecha"], p["id"]))
    return partidos, cuotas


def main() -> int:
    # ── descarga: qué entra ──────────────────────────────────────────────────
    crudo = {"events": [
        _evento(1, "2024-01-10T00:00Z", 2, 2, 13, 110, 100),
        _evento(2, "2024-01-10T00:00Z", 1, 2, 13, 110, 100),                 # pretemporada
        _evento(3, "2024-02-18T00:00Z", 2, 31, 32, 180, 175),                # All-Star
        _evento(4, "2024-01-10T00:00Z", 2, 5, 6, 0, 0, completo=False),      # sin jugar
        _evento(5, "2020-08-05T18:30Z", 2, 26, 29, 124, 115),                # burbuja 2020
        _evento(6, "2024-04-20T00:00Z", 3, 7, 8, 99, 101),                   # playoffs
    ]}
    rec = descarga.recortar_dia(crudo)
    check("descarga: solo terminados de temporada/playoffs entre franquicias", [p["id"] for p in rec] == [1, 5, 6], rec)
    check("descarga: la burbuja de Orlando 2020 es cancha neutral aunque ESPN no lo diga",
          next(p for p in rec if p["id"] == 5)["neutral"] and not next(p for p in rec if p["id"] == 1)["neutral"])
    check("descarga: el tipo viaja (playoffs)", next(p for p in rec if p["id"] == 6)["tipo"] == "playoffs")

    filas = descarga.recortar_cuotas({"items": [
        {"provider": {"name": "A"}, "spread": -6.5, "homeTeamOdds": {"moneyLine": -250, "spreadOdds": -110},
         "awayTeamOdds": {"moneyLine": 210, "spreadOdds": -110}},
        {"provider": {"name": "B"}, "spread": -7.0, "homeTeamOdds": {"moneyLine": -270}, "awayTeamOdds": {"moneyLine": 230}},
        {"provider": {"name": "C"}, "spread": -2.0, "homeTeamOdds": {"moneyLine": -130}, "awayTeamOdds": {"moneyLine": 110}},
        {"provider": {"name": "X - Live Odds"}, "spread": 15, "homeTeamOdds": {"moneyLine": 900}, "awayTeamOdds": {"moneyLine": -2000}},
        {"provider": {"name": "Opening"}, "spread": 3, "homeTeamOdds": {"moneyLine": 150}, "awayTeamOdds": {"moneyLine": -170}},
    ]})
    c = fase0.consenso(filas)
    check("cuotas: la mediana entre casas, sin líneas en vivo ni de apertura (−7, −6.5, −2 → −6.5)",
          c["spreadLocal"] == -6.5 and c["casas"] == 3, c)
    pa = (1 / fase0.decimal(-250)) / (1 / fase0.decimal(-250) + 1 / fase0.decimal(210))
    check("cuotas: probabilidad sin margen (1/cuota normalizado) y mediana entre casas",
          abs(c["pLocal"] - pa) < 1e-9, (c["pLocal"], pa))
    check("cuotas: americana → decimal (-110 → 1.909, +150 → 2.5)",
          abs(fase0.decimal(-110) - 1.9091) < 1e-3 and fase0.decimal(150) == 2.5)

    # ── motor: el nivel y la K ───────────────────────────────────────────────
    v = [(110, 100)] * 15 + [(90, 100)] * 5          # 15 victorias; últimos 5: 450-500
    esperado = 3 * 15 / 20 + 10 * (450 - 500) / 950 + 1
    check("motor: nivel = 3·victorias/20 + ESCALA_G·Σ(pf−pa)/Σ(pf+pa) de los últimos 5 + 1",
          abs(motor.nivel_de(v, 10.0) - esperado) < 1e-12, (motor.nivel_de(v, 10.0), esperado))

    partidos, cuotas = liga_sintetica()
    prev = motor.construir(partidos)
    j = 400
    alterados = [dict(p) for p in partidos]
    alterados[j]["ptsLocal"], alterados[j]["ptsVisita"] = alterados[j]["ptsVisita"], alterados[j]["ptsLocal"]
    prev2 = motor.construir(alterados)
    pid = partidos[j]["id"]
    check("motor SIN FUGA: cambiar el resultado de un partido no cambia lo que se sabía antes de jugarlo",
          prev[pid] == prev2[pid])
    sig = next(p for p in partidos[j + 1:] if p["localId"] == partidos[j]["localId"] or p["visitaId"] == partidos[j]["localId"])
    check("motor: y sí cambia lo que se sabe en el partido siguiente de ese equipo", prev[sig["id"]] != prev2[sig["id"]])

    mini = [{"id": n, "fecha": f"2024-01-{n + 1:02d}T00:00Z", "temporada": 2024, "tipo": "regular",
             "localId": 1, "visitaId": 2, "ptsLocal": pl, "ptsVisita": pv, "neutral": False}
            for n, (pl, pv) in enumerate([(110, 100), (105, 100), (120, 100), (90, 100), (100, 95)])]
    pm = motor.construir(mini)
    check("motor: sin empate, la K nunca vuelve a 0 (cada partido deja racha + o −)",
          all(pm[n]["local"]["signo"] != 0 for n in range(1, 5)))
    check("motor: la derrota corta la racha + de 3 y abre la − (reventón al otro signo)",
          pm[3]["local"]["racha"] == 3 and pm[3]["local"]["signo"] == 1
          and pm[4]["local"]["signo"] == -1 and pm[4]["local"]["racha"] == 1)
    q3 = (10 / 10) + (5 / 10) + (20 / 10)            # rival sin nivel → 1,0
    check("motor: k = Σ (margen/10)·nivel_rival mientras dura la racha (fallback 1,0)",
          abs(pm[3]["local"]["k"] - q3) < 1e-12, pm[3]["local"]["k"])
    check("motor: el visitante pesa ×1,4 en su K (como el fútbol, sin calibrar)",
          abs(pm[1]["visita"]["k"] - (-1.4)) < 1e-12, pm[1]["visita"]["k"])
    check("motor: descanso por horas (24 h = 1 día: back-to-back)", pm[1]["local"]["descanso"] == 1)

    # familias separadas (como la K de goles): sin empate, la de victorias es el
    # tramo + de la K fusionada y la de derrotas el tramo −, con las mismas bases
    distintos = 0
    for d in prev.values():
        for f in (d["local"], d["visita"]):
            for nombre, s_ in motor.FAMILIAS.items():
                v = f["familias"][nombre]
                if f["signo"] == s_:
                    distintos += not (v["signo"] == s_ and v["racha"] == f["racha"] and abs(v["k"] - abs(f["k"])) < 1e-9
                                      and v["reventonesSigno"] == f["reventonesSigno"]
                                      and v["medianaNivelRival"] == f["medianaNivelRival"])
                else:
                    distintos += not (v["signo"] == 0 and v["k"] == 0)
    check("familias: victorias = tramo + de la K fusionada, derrotas = tramo − (misma racha, K y base); la otra en cero",
          distintos == 0, distintos)
    check("familias: la de derrotas acumula POSITIVO (cuánto lleva perdiendo) y revienta a cero al ganar",
          pm[4]["local"]["familias"]["derrotas"]["k"] == 1.0 and pm[4]["local"]["familias"]["victorias"]["k"] == 0
          and pm[4]["local"]["familias"]["victorias"]["reventonesSigno"] == 1)

    # ── la K de PUNTOS (§10): anotar / recibir por encima de su media de 20 ─
    hist = [{"id": 5000 + n, "fecha": f"2024-0{1 + n // 28}-{1 + n % 28:02d}T00:00Z", "temporada": 2024, "tipo": "regular",
             "localId": 1, "visitaId": 2, "ptsLocal": pl, "ptsVisita": 100, "neutral": False}
            for n, pl in enumerate([110 if n % 2 else 90 for n in range(20)] + [115, 120, 95, 100])]
    pp = motor.construir(hist)
    v20, v21, v22, v23 = (pp[5020]["local"]["puntos"], pp[5021]["local"]["puntos"],
                          pp[5022]["local"]["puntos"], pp[5023]["local"]["puntos"])
    check("puntos: sin 20 partidos previos no hay media (ni burbuja)",
          pp[5019]["local"]["puntos"]["mediaAnota"] is None and v20["mediaAnota"] == 100)
    check("puntos: anotar 115 y 120 sobre su media abre y alarga la burbuja «anota»",
          v21["anota"]["abierta"] and v22["anota"]["racha"] == 2 and v22["anota"]["k"] > v21["anota"]["k"])
    check("puntos: anotar debajo de su media la revienta A CERO y queda en la base",
          not v23["anota"]["abierta"] and v23["anota"]["reventonesSigno"] == 1)
    pc = motor.construir(hist, linea_puntos={5020: (105.0, 100.0), 5021: (125.0, 95.0)})
    check("puntos (vara de la casa): anotar 115 con 105 esperados abre «anotaCasa»; 120 con 125 esperados la revienta",
          pc[5021]["local"]["puntos"]["anotaCasa"]["abierta"] and not pc[5022]["local"]["puntos"]["anotaCasa"]["abierta"]
          and pc[5022]["local"]["puntos"]["anotaCasa"]["reventonesSigno"] == 1)
    check("puntos (vara de la casa): la visita lee la línea del otro lado (recibe 115 con 105 esperados en contra)",
          pc[5021]["visita"]["puntos"]["recibeCasa"]["abierta"])
    check("puntos (vara de la casa): sin línea, la familia de la casa no se mueve",
          pc[5023]["local"]["puntos"]["anotaCasa"] == pc[5022]["local"]["puntos"]["anotaCasa"])
    rev = [{"partidos": 2, "kPico": 3.0, "nivelRival": 2.5, "fecha": "2020-01-01"} for _ in range(10)]
    check("puntos en su extremo: sin base (menos de 3 cortes) o cerrada no tiene estado",
          motor._estado_extremo({"k": 5.0, "racha": 4, "reventones": rev[:2]}) is None
          and motor._estado_extremo({"k": 0.0, "racha": 0, "reventones": rev}) is None)
    check("puntos en su extremo: K y racha sobre su récord con 3+ partidos → extremo (regla del fútbol)",
          motor._estado_extremo({"k": 5.0, "racha": 4, "reventones": rev}) == "extremo"
          and motor._record_reciente({"k": 5.0, "racha": 4, "reventones": rev}))
    check("puntos en su extremo: dentro de lo que ya aguantó → rango",
          motor._estado_extremo({"k": 1.0, "racha": 1, "reventones": rev}) == "rango")
    from backend.nba import puntos as _pts
    t = _pts.totales([{"casa": "A", "overUnder": 220.5, "overCuota": -110, "underCuota": -110},
                      {"casa": "B", "overUnder": 221.5, "overCuota": -105, "underCuota": -115},
                      {"casa": "X - Live Odds", "overUnder": 250, "overCuota": -110, "underCuota": -110}])
    check("puntos: la línea de más/menos es la mediana sin las de vivo", t["linea"] == 221.0, t)

    # ── la guía de burbujas: los puntos del fútbol, sin copiar números ───────
    base = {"signo": 1, "racha": 4, "k": 9.0, "kPico": 9.0, "nivel": 3.0, "nivelRival": 3.0,
            "reventonesSigno": 10, "medianaPartidos": 2, "medianaKPico": 5.0, "medianaNivelRival": 2.5,
            "contramano": True}
    rg = burbujas.riesgo(base)
    check("burbujas: racha ≥ mediana +1, rival muy fuerte +2, contramano +1 → muy alto (+4)",
          rg["puntos"] == 4 and rg["nivel"] == "muy alto" and rg["tramo"] == "muy fuerte", rg)
    check("burbujas: sin base propia (< 3 reventones del signo) no hay riesgo",
          burbujas.riesgo({**base, "reventonesSigno": 2}) is None)
    rg2 = burbujas.riesgo({**base, "signo": -1, "nivel": 2.0, "nivelRival": 3.5, "medianaNivelRival": 3.0,
                           "contramano": False})
    check("burbujas: con racha − el rival FLOJO empuja al corte; el rival muy fuerte resta (muy favorito)",
          rg2["tramo"] == "lejos" and rg2["favorito"] == "muy favorito" and rg2["puntos"] == 1 - 3, rg2)

    # ── la lectura de momentum: extremo del fútbol + récord del período ──────
    hist = [{"partidos": 2, "kPico": 5.0, "nivelRival": 2.5, "fecha": f"2020-01-{i + 1:02d}"} for i in range(30)]
    hist[0] = {**hist[0], "partidos": 12, "kPico": 60.0}           # récord viejo, de otro plantel
    fam = {"k": 30.0, "racha": 6, "kPico": 30.0, "conds": [], "reventones": hist}
    mo = burbujas.momentum(fam, "victorias", 500)
    check("momentum: sin superar el récord de toda la historia no es EXTREMO, pero pasa el 90 % → CERCA (regla del fútbol)",
          not mo["extremo"]["activo"] and mo["extremo"]["cerca"], mo["extremo"])
    check("momentum: sí pasa todo lo de los últimos 20 cortes → récord del período, dicho aparte",
          mo["recordPeriodo"]["activo"] and len(mo["recordPeriodo"]["motivos"]) == 2, mo["recordPeriodo"])
    check("momentum: la posición es contra los cortes de SU familia (K 30 sobre el 97 de cada 100)",
          mo["posicion"]["percentilK"] == 97 and mo["posicion"]["kSobreMediana"] == 6.0, mo["posicion"])
    mo2 = burbujas.momentum({**fam, "k": 70.0, "racha": 13}, "victorias", 500)
    check("momentum: sobre el récord de toda la historia (K 70 > 60, racha 13 > 12) → EXTREMO",
          mo2["extremo"]["activo"] and mo2["extremo"]["kRecord"] and mo2["extremo"]["rachaRecord"], mo2["extremo"])
    cero = burbujas.momentum({"k": 0.0, "racha": 0, "kPico": 0.0, "conds": [], "reventones": hist}, "derrotas", 500)
    check("momentum: la familia en cero dice cuándo y cómo terminó la última",
          not cero["abierta"] and cero["ultima"]["cortada"] == "2020-01-30" and "extremo" not in cero, cero)

    # ── el método: detecta un efecto real y no inventa uno ───────────────────
    rnd = random.Random(5)
    obs = []
    for i in range(3000):
        x, ruido = rnd.gauss(0, 1), rnd.gauss(0, 1)
        obs.append({"x": x, "ruido": ruido, "y": int(rnd.random() < 1 / (1 + math.exp(-0.8 * x)))})
    tr, te = obs[:2400], obs[2400:]
    m0, m1, m2 = fase0.modelo(tr, te, []), fase0.modelo(tr, te, ["x"]), fase0.modelo(tr, te, ["ruido"])
    check("método: una variable que mueve el resultado MEJORA (IC bajo 0)",
          fase0.ic_dif(m0["ll"], m1["ll"])["veredicto"] == "mejora", fase0.ic_dif(m0["ll"], m1["ll"]))
    check("método: una variable de ruido NO mejora",
          fase0.ic_dif(m0["ll"], m2["ll"])["veredicto"] != "mejora", fase0.ic_dif(m0["ll"], m2["ll"]))
    check("método: el coeficiente recupera el signo y el orden de magnitud (0,8)",
          0.5 < m1["coef"]["x"] < 1.1, m1["coef"])
    r = fase0.roi([(2.0, 1), (2.0, 0), (3.0, 1), (1.5, 0)])
    check("simulación plana: ROI = Σ ganancia / apuestas ((1 − 1 + 2 − 1)/4 = +25 %)", r["roi"] == 0.25, r)

    # ── la corrida entera sobre una liga sintética con mercado perfecto ──────
    base = tempfile.mkdtemp(prefix="sad_nba_")
    os.makedirs(os.path.join(base, "dias"))
    os.makedirs(os.path.join(base, "cuotas"))
    with open(os.path.join(base, "dias", "todo.json"), "w") as f:
        json.dump(partidos, f)
    for i, filas_c in cuotas.items():
        with open(os.path.join(base, "cuotas", f"{i}.json"), "w") as f:
            json.dump(filas_c, f)
    res = fase0.correr(base)
    g = res["ganador"]
    check("corrida: el nivel predice al ganador mejor que la moneda (log-loss < ln 2)",
          g["modelos"]["G0 · motor (nivel + localía)"]["logLoss"] < math.log(2), g["modelos"])
    mk = g["comparaciones"]["MK1 · mercado + la teoría vs MK0 · mercado solo"]
    check("corrida: con un mercado PERFECTO, la teoría no le agrega nada (no inventa ventaja)",
          mk["veredicto"] != "mejora", mk)
    check("corrida: prueba = el 20 % más reciente del entrenamiento en adelante",
          g["prueba"] == g["partidos"] - int(g["partidos"] * 0.8) and g["corte"] <= g["hasta"], g)
    check("corrida: hándicap y reventón salen con su prueba",
          res["handicap"]["prueba"] > 0 and res["reventon"]["prueba"] > 0, (res["handicap"].get("prueba"), res["reventon"].get("prueba")))
    check("corrida: el texto se arma", "REVENTÓN" in fase0.texto(res))

    # ── el estudio de ligas: rivales de otra división afuera, tramos medidos ─
    visita_rara = {"id": 1, "fecha": "2017-01-01T00:00Z", "temporada": 2017, "tipo": "regular", "localId": 1,
                   "visitaId": 999, "local": "1", "visita": "X", "ptsLocal": 120, "ptsVisita": 60, "neutral": False}
    filtrados = ligas._filtrar(partidos + [visita_rara])
    check("ligas: un rival que juega 1 partido en la temporada (otra división) queda afuera",
          all(999 not in (p["localId"], p["visitaId"]) for p in filtrados) and len(filtrados) == len(partidos))
    os.environ["SAD_NBA_DIR"] = base
    os.makedirs(os.path.join(descarga.carpeta("wnba"), "dias"))
    with open(os.path.join(descarga.carpeta("wnba"), "dias", "todo.json"), "w") as f:
        json.dump([{**p, "localConf": p["localId"] % 3, "visitaConf": p["visitaId"] % 3} for p in partidos], f)
    est = ligas.estudiar("wnba")
    check("ligas: la carpeta de cada liga es aparte de la NBA", descarga.carpeta("wnba").endswith(os.path.join("ligas", "wnba"))
          and descarga.carpeta("nba") == base)
    check("ligas: mide desde la 2.ª temporada (la 1.ª calienta el nivel)", min(est["temporadas"]) == "2017", est["temporadas"].keys())
    check("ligas: el nivel acierta más que la moneda en una liga con fuerza real", est["aciertoNivel"] > 0.5, est["aciertoNivel"])
    check("ligas: los cuatro tramos y la vista por conferencia salen", set(est["tramos"]) == set("ABCD")
          and "tramosPorConferencia" in est and "✓ = firme" in ligas.texto([est]))

    print("\nTODO OK" if not fallas else f"\n{fallas} FALLAS")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
