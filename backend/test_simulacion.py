"""Simulación de apuesta: las tres estrategias hacen lo que dicen.

Sobre apuestas SINTÉTICAS donde la cuenta se hace a mano: la plana pone 1
unidad al elegido, Kelly no apuesta sin ventaja y apuesta f*·banca con ella,
la martingala duplica tras perder y vuelve a 1 al ganar, y la versión del
skill sale de la hora de subida. Y que el endpoint responda sobre la demo.

    python -m backend.test_simulacion
"""
from __future__ import annotations

import os
import sys
import tempfile

os.environ.setdefault("SAD_SIN_HILOS", "1")
_tmp = tempfile.mkdtemp(prefix="sad_sim_")
from backend.seed_demo import seed  # noqa: E402
seed(_tmp)
os.environ["SAD_DATA_DIR"] = _tmp
import backend.db as _dbmod  # noqa: E402
_dbmod.BASE_DIR = _tmp

from backend.analisis import simulacion as sim  # noqa: E402

fallas = 0


def check(nombre, ok, detalle=""):
    global fallas
    print(("OK  " if ok else "FALLA ") + nombre + ("" if ok else f" -> {detalle}"))
    fallas += 0 if ok else 1


def ap(fid, pitazo, probs, cuotas, resultado, version="v4.2"):
    return {"fixtureId": fid, "pitazo": pitazo, "partido": {"local": "A", "visita": "B", "liga": ""},
            "probabilidades": dict(zip(("local", "empate", "visita"), probs)),
            "cuotas": dict(zip(("local", "empate", "visita"), cuotas)),
            "mercado": {}, "resultado": resultado, "versiones": {"sad-analysis": version}}


def est(out, clave):
    return next(e for e in out["estrategias"] if e["clave"] == clave)


# Kelly a mano: p = 0.5, c = 2.5 → f* = (1.25 − 1)/1.5 = 1/6
check("kelly(0.5, 2.5) = 1/6", abs(sim.kelly(0.5, 2.5) - 1 / 6) < 1e-9, sim.kelly(0.5, 2.5))
check("kelly sin ventaja es negativa", sim.kelly(0.5, 1.9) < 0)

# 1) un partido con ventaja en el local (50 % a cuota 2.5), gana el local
out = sim.simular([ap(1, "2026-10-28 20:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local")])
pl, k, kc, mg = est(out, "plana"), est(out, "kelly"), est(out, "kellyCuarto"), est(out, "martingala")
check("plana: +1.5 con 1 unidad a cuota 2.5", pl["banca"] == 101.5, pl)
check("kelly: apuesta 100/6 y gana ×1.5", abs(k["banca"] - (100 + 100 / 6 * 1.5)) < 0.01, k)
check("kelly ¼: un cuarto de lo de Kelly", abs(kc["banca"] - (100 + 100 / 24 * 1.5)) < 0.01, kc)
check("martingala: 1 unidad la primera vez", mg["banca"] == 101.5, mg)

# 2) sin ventaja en ninguna selección (probabilidades = mercado con margen) → Kelly no apuesta
out = sim.simular([ap(2, "2026-10-28 20:00:00", (50, 28, 22), (1.9, 3.3, 4.2), "visita")])
k = est(out, "kelly")
check("kelly sin ventaja no apuesta", k["apuestas"] == 0 and k["banca"] == 100, k)
check("la fila dice que Kelly no apostó", out["apuestas"][0]["porEstrategia"]["kelly"]["seleccion"] is None)
check("plana pierde 1 igual", est(out, "plana")["banca"] == 99)

# 3) martingala: pierde, pierde, gana → apuesta 1, 2, 4; vuelve a 1
serie = [ap(10, "2026-10-28 15:00:00", (60, 25, 15), (1.5, 4, 6), "empate"),
         ap(11, "2026-10-28 17:00:00", (60, 25, 15), (1.5, 4, 6), "visita"),
         ap(12, "2026-10-28 19:00:00", (60, 25, 15), (1.5, 4, 6), "local"),
         ap(13, "2026-10-28 21:00:00", (60, 25, 15), (1.5, 4, 6), "local")]
out = sim.simular(list(reversed(serie)))  # el orden de entrada no importa: manda el pitazo
montos = [f["porEstrategia"]["martingala"]["monto"] for f in reversed(out["apuestas"])]
check("martingala: 1 · 2 · 4 · 1", montos == [1, 2, 4, 1], montos)
mg = est(out, "martingala")
check("martingala: −1 −2 +2 +0.5 = 99.5", mg["banca"] == 99.5, mg)
check("la serie arranca en la banca inicial y suma un punto por cerrada",
      len(mg["serie"]) == 5 and mg["serie"][0]["banca"] == 100, mg["serie"])

# 4) martingala sin banca: apuesta lo que queda y quiebra
larga = [ap(100 + i, f"2026-10-29 {2 * i:02d}:00:00", (60, 25, 15), (1.5, 4, 6), "visita") for i in range(8)]
mg = est(sim.simular(larga), "martingala")
check("martingala quiebra con 7 derrotas (1+2+…+64 > 100)", mg["banca"] == 0 and mg["quebro"] == 106, mg)
check("caída máxima 100 %", mg["caidaMaxima"] == 1.0, mg)

# 4-bis) LÍNEAS EN PARALELO (29/10/2026, usuario): tres perdidas a las 15:00 → las tres
# siguientes van por 2; una cuarta a la misma hora abre una línea nueva en 1
par = [ap(40 + i, "2026-10-28 15:00:00", (60, 25, 15), (1.5, 4, 6), "visita") for i in range(3)]
par += [ap(50 + i, "2026-10-28 18:00:00", (60, 25, 15), (1.5, 4, 6), "local") for i in range(4)]
out = sim.simular(par)
por_fx = {a["fixtureId"]: a["porEstrategia"]["martingala"] for a in out["apuestas"]}
check("15:00 · tres líneas en 1", [por_fx[40 + i]["monto"] for i in range(3)] == [1, 1, 1]
      and sorted(por_fx[40 + i]["linea"] for i in range(3)) == [1, 2, 3], por_fx)
check("18:00 · las tres que perdieron van por 2",
      [por_fx[50 + i]["monto"] for i in range(3)] == [2, 2, 2], por_fx)
check("18:00 · la cuarta abre la línea 4 en 1", por_fx[53]["monto"] == 1 and por_fx[53]["linea"] == 4, por_fx)
mg = est(out, "martingala")
check("martingala: 4 líneas, ninguna perdiendo al final, máximo en juego 7",
      mg["lineas"] == {"abiertas": 4, "perdiendo": 0, "proximoMayor": 1} and mg["exposicionMaxima"] == 7, mg)
check("una línea ocupada no se usa: el partido de las 16:00 abre otra",
      [a["porEstrategia"]["martingala"]["linea"] for a in reversed(sim.simular(
          [ap(60, "2026-10-28 15:00:00", (60, 25, 15), (1.5, 4, 6), "visita"),
           ap(61, "2026-10-28 16:00:00", (60, 25, 15), (1.5, 4, 6), "visita"),
           ap(62, "2026-10-28 17:00:00", (60, 25, 15), (1.5, 4, 6), "visita")])["apuestas"])] == [1, 2, 1])
fifo = sim.simular([ap(70, "2026-10-28 12:00:00", (60, 25, 15), (1.5, 4, 6), "visita"),
                    ap(71, "2026-10-28 13:00:00", (60, 25, 15), (1.5, 4, 6), "local"),
                    ap(72, "2026-10-28 18:00:00", (60, 25, 15), (1.5, 4, 6), "local")])
f72 = next(a for a in fifo["apuestas"] if a["fixtureId"] == 72)["porEstrategia"]["martingala"]
check("con dos libres toma la que más tiempo lleva libre (la 1, que perdió: va por 2)",
      f72["linea"] == 1 and f72["monto"] == 2, f72)

# 4-ter) KELLY SIN MIRAR EL FUTURO: los simultáneos con la banca de antes, y sin pasarse de la plata libre
out = sim.simular([ap(80, "2026-10-28 15:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local"),
                   ap(81, "2026-10-28 15:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local"),
                   ap(82, "2026-10-28 16:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local")])
mk = {a["fixtureId"]: a["porEstrategia"]["kelly"]["monto"] for a in out["apuestas"]}
check("kelly: los dos de las 15:00 y el de las 16:00 apuestan sobre la banca de 100 (nada se cobró)",
      all(abs(mk[f] - 100 / 6) < 0.01 for f in (80, 81, 82)), mk)
out = sim.simular([ap(90 + i, "2026-10-28 15:00:00", (80, 10, 10), (2.0, 8, 8), "local") for i in range(3)])
mk = [a["porEstrategia"]["kelly"]["monto"] for a in reversed(out["apuestas"])]
check("kelly entero con f* = 0.6 en tres simultáneos: 60 · 40 · nada (no pasa de la plata libre)",
      mk == [60, 40, 0], mk)
check("el tercero dice que no hubo plata libre", out["apuestas"][0]["porEstrategia"]["kelly"]["motivo"]
      == "sin plata libre", out["apuestas"][0]["porEstrategia"]["kelly"])

# 4-quater) CONTROL DE CONFIANZA: plana solo con nuestro elegido a 60 %+ (29/10/2026, usuario)
out = sim.simular([ap(110, "2026-10-28 15:00:00", (65, 20, 15), (1.5, 4.2, 6.0), "local"),
                   ap(111, "2026-10-28 18:00:00", (55, 25, 20), (1.8, 3.6, 4.5), "visita"),
                   ap(112, "2026-10-28 21:00:00", (30, 10, 60), (4.0, 6.0, 1.6), "empate")])
p60 = {a["fixtureId"]: a["porEstrategia"]["plana60"] for a in out["apuestas"]}
check("plana 60 %+: apuesta al local de 65 % y a la visita de 60 %", p60[110]["monto"] == 1
      and p60[112]["monto"] == 1 and p60[112]["seleccion"] == "visita", p60)
check("plana 60 %+: no apuesta al de 55 % y dice por qué",
      p60[111]["seleccion"] is None and p60[111]["motivo"] == "bajo 60 %", p60[111])
e60 = est(out, "plana60")
check("plana 60 %+: +0.5 −1 = 99.5 en 2 apuestas", e60["banca"] == 99.5 and e60["apuestas"] == 2, e60)
check("la plana de control apostó en las tres", est(out, "plana")["apuestas"] == 3)

# 4-quinquies) MARTINGALA 60 %+ (29/10/2026, usuario): las mismas líneas, solo con el elegido a 60 %+
out = sim.simular([ap(120, "2026-10-28 12:00:00", (65, 20, 15), (1.5, 4.2, 6.0), "visita"),   # pierde 1
                   ap(121, "2026-10-28 15:00:00", (55, 25, 20), (1.8, 3.6, 4.5), "visita"),   # bajo 60: no toca
                   ap(122, "2026-10-28 18:00:00", (70, 18, 12), (1.4, 4.5, 7.0), "local")])   # va por 2, gana
m60 = {a["fixtureId"]: a["porEstrategia"]["martingala60"] for a in out["apuestas"]}
check("martingala 60 %+: 1 · (no apuesta bajo 60 %) · 2 en la misma línea",
      m60[120]["monto"] == 1 and m60[121]["seleccion"] is None and m60[121]["motivo"] == "bajo 60 %"
      and m60[122]["monto"] == 2 and m60[122]["linea"] == 1, m60)
e = est(out, "martingala60")
check("martingala 60 %+: −1 +0.8 = 99.8 y una sola línea, que vuelve a 1",
      abs(e["banca"] - 99.8) < 1e-9 and e["lineas"]["abiertas"] == 1 and e["lineas"]["perdiendo"] == 0, e)
check("la martingala de siempre apostó en las tres", est(out, "martingala")["apuestas"] == 3)

# 5) pendiente: no mueve la banca pero dice qué se apostaría
out = sim.simular([ap(20, "2026-10-28 20:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local"),
                   ap(21, "2026-10-28 23:00:00", (50, 30, 20), (2.5, 3.2, 4.0), None)])
pend = out["apuestas"][0]
check("la pendiente va arriba y sin banca", pend["estado"] == "pendiente" and
      pend["porEstrategia"]["plana"]["banca"] is None, pend)
check("la pendiente trae el monto de Kelly con la banca de hoy",
      abs(pend["porEstrategia"]["kelly"]["monto"] - est(out, "kelly")["banca"] / 6) < 0.01, pend)
check("cerradas 1 · pendientes 1", out["cerradas"] == 1 and out["pendientes"] == 1)

# 6) por versión: cada versión con lo suyo
out = sim.simular([ap(30, "2026-10-28 10:00:00", (60, 25, 15), (1.5, 4, 6), "local", "v4.1"),
                   ap(31, "2026-10-28 20:00:00", (60, 25, 15), (1.5, 4, 6), "empate", "v4.2")])
pv = {v["version"]: v for v in out["porVersion"]}
check("por versión: v4.1 ganó 0.5 en la plana", pv["v4.1"]["estrategias"]["plana"]["ganancia"] == 0.5, pv)
check("por versión: v4.2 perdió 1 en la plana", pv["v4.2"]["estrategias"]["plana"]["ganancia"] == -1, pv)

# 7) la versión por hora de subida: el tramo de la madrugada del 28/10 fue con v4.1
check("sad 28/10 09:50 UTC → v4.1", sim.version_al("sad-analysis", "2026-10-28 09:50:00") == "v4.1")
check("sad 28/10 12:00 UTC → v4.2", sim.version_al("sad-analysis", "2026-10-28 12:00:00") == "v4.2")
check("efe 28/10 09:50 UTC → v1.7", sim.version_al("efe-clasificador", "2026-10-28 09:50:00") == "v1.7")
check("TDE sin hora de subida: rige desde el día del corte",
      sim.version_al("teorema-del-echado", "2026-10-28 09:50:00") == "v0.1.24")
# 1143: los zips del 01/11 subieron a las 08:00 de Lima (13:00 UTC)
for _sk, _antes, _despues in (("sad-analysis", "v4.3", "v4.4"), ("teorema-del-echado", "v0.1.24", "v0.1.25"),
                              ("diagnostico-tactico", "v1.6", "v1.7"), ("efe-clasificador", "v1.8", "v1.9")):
    check(f"{_sk} 01/11 10:00 UTC → {_antes}", sim.version_al(_sk, "2026-11-01 10:00:00") == _antes,
          sim.version_al(_sk, "2026-11-01 10:00:00"))
    check(f"{_sk} 01/11 13:30 UTC → {_despues}", sim.version_al(_sk, "2026-11-01 13:30:00") == _despues)
# los zips del 10/11 subieron hacia las 07:15 de Lima (12:15 UTC)
for _sk, _antes, _despues in (("sad-analysis", "v4.4", "v4.5"), ("teorema-del-echado", "v0.1.25", "v0.1.26"),
                              ("diagnostico-tactico", "v1.7", "v1.8"), ("efe-clasificador", "v1.9", "v1.10")):
    check(f"{_sk} 10/11 10:00 UTC → {_antes}", sim.version_al(_sk, "2026-11-10 10:00:00") == _antes,
          sim.version_al(_sk, "2026-11-10 10:00:00"))
    check(f"{_sk} 10/11 12:30 UTC → {_despues}", sim.version_al(_sk, "2026-11-10 12:30:00") == _despues)

# 8) el armado desde la base corre sobre la demo (sin partes desde el 28/10: vacío, no un error)
out = sim.simulacion()
check("simulacion() responde con las trece estrategias (con el método, en verde, con el marcador y las martingalas ajustadas)", len(out["estrategias"]) == 13, out.keys())
check("simulacion() trae desde y nota", out["desde"] == sim.DESDE and out["nota"])

# 9) de punta a punta: un parte de verdad en la base, depositado antes del pitazo
import json as _json  # noqa: E402
import sqlite3 as _sql  # noqa: E402
from backend.analisis.parte import _conectar  # noqa: E402
_sad = _sql.connect(os.path.join(_tmp, "sad.db"))
fids = [r[0] for r in _sad.execute("SELECT DISTINCT fixture_id FROM odds ORDER BY fixture_id LIMIT 4")]
cols = {r[1] for r in _sad.execute("PRAGMA table_info(fixtures)")}
gol_l = "fulltime_home" if "fulltime_home" in cols else "goals_home"
gol_v = "fulltime_away" if "fulltime_away" in cols else "goals_away"
pitazos = ["2026-10-28T20:00:00+00:00", "2026-10-28T22:00:00+00:00", "2026-10-29T20:00:00+00:00",
           "2026-10-27T20:00:00+00:00"]
for fid, pit in zip(fids, pitazos):
    _sad.execute(f"UPDATE fixtures SET date=?, status_short='FT', {gol_l}=2, {gol_v}=1, "
                 "goals_home=2, goals_away=1 WHERE id=?", (pit, fid))
_sad.commit()
_sad.close()
parte = {"fixtureId": 0, "version": "v2.5", "pronostico": {"probabilidades": {"local": 50, "empate": 27, "visita": 23}}}
with _conectar() as con:
    for i, (fid, pit) in enumerate(zip(fids, pitazos)):
        dep = None if i == 1 else ("2026-10-28 10:00:00" if i == 0 else "2026-10-29 12:00:00")
        if i == 3:
            dep = "2026-10-27 12:00:00"  # partido del 27/10: fuera de la simulación
        con.execute("INSERT OR REPLACE INTO parte_cowork (fixture_id, fecha, equipo_a, equipo_b, estado, version, "
                    "parte_json, creado_en, actualizado_en, deposito_previo_en) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (fid, pit[:10], "A", "B", "pendiente_xi", "v2.5", _json.dumps({**parte, "fixtureId": fid}),
                     dep or "2026-10-28 23:00:00", dep or "2026-10-28 23:00:00", dep))
out = sim.simulacion()
ids = [a["fixtureId"] for a in out["apuestas"]]
check("entra el parte depositado antes del pitazo", fids[0] in ids and fids[2] in ids, ids)
check("el parte sin depósito previo al pitazo queda excluido con su motivo",
      any(x["fixtureId"] == fids[1] and "antes del pitazo" in x["motivo"] for x in out["excluidos"]), out["excluidos"])
check("un partido anterior al 28/10 no aparece ni como excluido",
      fids[3] not in ids and all(x["fixtureId"] != fids[3] for x in out["excluidos"]))
a0 = next(a for a in out["apuestas"] if a["fixtureId"] == fids[0])
check("la apuesta trae la versión de la hora del depósito (madrugada del 28/10 → sad v4.1)",
      a0["versiones"]["sad-analysis"] == "v4.1" and a0["versiones"]["efe-clasificador"] == "v1.7", a0["versiones"])
check("la del 29/10 → sad v4.2", next(a for a in out["apuestas"] if a["fixtureId"] == fids[2])
      ["versiones"]["sad-analysis"] == "v4.2")
check("cerrada con el resultado de la base (local 2-1)", a0["estado"] == "cerrada" and a0["resultado"] == "local", a0)
check("la plana apostó en las dos", est(out, "plana")["apuestas"] == 2, est(out, "plana"))

# 11) EL MÉTODO (03/11/2026, usuario; docs/METODO_APUESTA.md): 1 % de la banca al
# elegido, con freno por tramo de confianza
out = sim.simular([ap(200, "2026-10-28 20:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local")])
pr = est(out, "proporcional")
check("proporcional: 1 % de 100 al elegido a cuota 2.5 → +1.5", pr["banca"] == 101.5
      and out["apuestas"][0]["porEstrategia"]["proporcional"]["seleccion"] == "local", pr)
out = sim.simular([ap(201, "2026-10-28 12:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local"),
                   ap(202, "2026-10-28 18:00:00", (50, 30, 20), (2.5, 3.2, 4.0), "local")])
m202 = next(a for a in out["apuestas"] if a["fixtureId"] == 202)["porEstrategia"]["proporcional"]["monto"]
check("proporcional: la segunda va por el 1 % de la banca nueva (101.5 → 1.015)", abs(m202 - 1.015) < 1e-9, m202)

check("freno: con menos de FRENO_MINIMO partidos no se juzga",
      not sim.freno_tramo([(False, 0.7)] * (sim.FRENO_MINIMO - 1))["pausado"])
check("freno: 15 de 15 perdidos a cuota 1.3 → pausa",
      sim.freno_tramo([(False, 1 / 1.3)] * sim.FRENO_MINIMO)["pausado"])
f = sim.freno_tramo([(True, 0.5)] * 9 + [(False, 0.5)] * 11)
check("freno: 9 de 20 donde se pedía 50 % (z −0.45) está dentro de la tolerancia", not f["pausado"]
      and f["tasa"] == 0.45 and f["pide"] == 0.5, f)

# el tramo 60+ pierde 15 seguidos y se pausa; el 40-49 sigue apostando; en pausa sigue
# anotando y vuelve cuando las derrotas salen de la ventana
seq = [ap(300 + i, f"2026-11-0{1 + i // 8} {(3 * (i % 8)):02d}:00:00", (65, 20, 15), (1.3, 5, 9), "visita")
       for i in range(sim.FRENO_MINIMO)]
seq.append(ap(400, "2026-11-03 00:00:00", (65, 20, 15), (1.3, 5, 9), "local"))      # 60+: en pausa
seq.append(ap(401, "2026-11-03 00:00:00", (45, 30, 25), (2.1, 3.3, 3.6), "local"))  # 40-49: apuesta
out = sim.simular(seq)
pf = {a["fixtureId"]: a["porEstrategia"]["proporcional"] for a in out["apuestas"]}
check("freno: tras 15 derrotas el 60+ no apuesta y dice por qué",
      pf[400]["monto"] == 0 and "tramo 60+ en pausa" in pf[400]["motivo"], pf[400])
check("freno: el tramo 40-49 no se contagia", pf[401]["monto"] > 0, pf[401])
t60 = next(t for t in est(out, "proporcional")["tramos"] if t["tramo"] == "60+")
check("freno: el partido en pausa también se anota (16 en el tramo, 1 acierto)",
      t60["n"] == sim.FRENO_MINIMO + 1 and t60["aciertos"] == 1 and t60["pausado"], t60)
check("solo el método trae el estado de los tramos", est(out, "plana")["tramos"] is None
      and [t["tramo"] for t in est(out, "proporcional")["tramos"]] == ["<40", "40-49", "50-59", "60+"])
vuelta = seq[:sim.FRENO_MINIMO] + [
    ap(500 + i, f"2026-11-{4 + i // 8:02d} {(3 * (i % 8)):02d}:00:00", (65, 20, 15), (1.3, 5, 9), "local")
    for i in range(sim.FRENO_VENTANA)]
out = sim.simular(vuelta)
ult = min(out["apuestas"], key=lambda a: -a["fixtureId"])["porEstrategia"]["proporcional"]
check("freno: con las derrotas fuera de la ventana el tramo vuelve a apostar", ult["monto"] > 0, ult)

# 12) CRITERIO DE CONTACTO (04/11/2026, usuario): acierto tras k fallos seguidos
tf = sim.tras_fallos([True, False, True, False, False, True, False, False, False, True, False, False, False, False])
pk = {f["k"]: f for f in tf["porK"]}
check("tras 1 fallo: 3 de 9", pk[1]["n"] == 9 and pk[1]["aciertos"] == 3, pk[1])
check("tras 2 fallos: 2 de 5", pk[2]["n"] == 5 and pk[2]["aciertos"] == 2, pk[2])
check("tras 3 fallos: 1 de 2 (el 4.º fallo de la última racha también cuenta)", pk[3]["n"] == 2 and pk[3]["aciertos"] == 1, pk[3])
check("tras 4 fallos: ninguno todavía", pk[4]["n"] == 0 and pk[4]["tasa"] is None and pk[4]["intervalo"] is None, pk[4])
check("promedio: 4 de 14", tf["base"]["n"] == 14 and tf["base"]["aciertos"] == 4)
check("con pocos casos queda en observación y dice cuántos faltan",
      tf["contacto"]["estado"] == "en_observacion" and tf["contacto"]["faltan"] == sim.CONTACTO_N - 2, tf["contacto"])
# 100 casos tras 3 fallos, todos aciertos, con un promedio de 25 %: contacto
tf = sim.tras_fallos(([False] * 3 + [True]) * sim.CONTACTO_N)
c3 = next(f for f in tf["porK"] if f["k"] == 3)
check("contacto: 100+ casos, tasa ≥ 65 % y el intervalo entero sobre el promedio",
      c3["n"] >= sim.CONTACTO_N and tf["contacto"]["cumple"] and tf["contacto"]["estado"] == "contacto", tf["contacto"])
tf = sim.tras_fallos(([False] * 3 + [True, False]) * 120)
check("100+ casos sin la tasa: sin contacto", tf["contacto"]["estado"] == "sin_contacto" and not tf["contacto"]["cumple"],
      tf["contacto"])
out = sim.simular([ap(600 + i, f"2026-10-30 {i:02d}:00:00", (60, 25, 15), (1.5, 4, 6),
                      "local" if i % 4 == 3 else "visita") for i in range(12)])
check("simular trae trasFallos sobre las cerradas (12 partidos, 9 casos tras 1 fallo)",
      out["trasFallos"]["base"]["n"] == 12 and out["trasFallos"]["porK"][0]["n"] == 9, out["trasFallos"]["porK"][0])

# la medición del fin de semana (backend.contacto) arma las apuestas con los MISMOS filtros, sin red
from backend import contacto  # noqa: E402
def _dato(fid, fecha, creado, liga_id=135, liga="Serie A", probs=(50, 27, 23), cu=(2.0, 3.4, 3.9),
          goles=(2, 1), cuarentena=None, real=None):
    return {"parte": {"creadoEn": creado, "cuarentena": cuarentena, "version": "cowork/1",
                      "pronostico": {"probabilidades": dict(zip(("local", "empate", "visita"), probs))},
                      "veredicto": {"objetivo": {"unXDos": {"real": real}}} if real else None},
            "fx": {"fecha": fecha, "estado": "finalizado", "ligaId": liga_id, "liga": liga,
                   "local": {"nombre": "A"}, "visitante": {"nombre": "B"}, "golesLocal": goles[0], "golesVisitante": goles[1]},
            "cuotas": [{"mercado": "1x2", "seleccion": s, "cuota": c} for s, c in zip("1X2", cu)]}
datos = {
    "1": _dato(1, "2026-10-29T20:00:00Z", "2026-10-29 12:00:00"),
    "2": _dato(2, "2026-10-29T20:00:00Z", "2026-10-29 21:00:00"),                       # depositado después
    "3": _dato(3, "2026-10-29T20:00:00Z", "2026-10-29 12:00:00", liga_id=143, liga="Copa del Rey"),
    "4": _dato(4, "2026-10-29T20:00:00Z", "2026-10-29 12:00:00", cuarentena={"motivo": "DT"}),
    "5": _dato(5, "2026-10-27T20:00:00Z", "2026-10-27 12:00:00"),                       # antes de DESDE
    "6": _dato(6, "2026-10-30T20:00:00Z", "2026-10-30 12:00:00", liga_id=2, liga="UEFA Champions League", goles=(0, 0)),
    "7": _dato(7, "2026-10-30T20:00:00Z", "2026-10-30 12:00:00", goles=(1, 0), real="visita"),
}
ap_, ex_ = contacto.armar(datos)
ids = sorted(a["fixtureId"] for a in ap_)
check("contacto.armar: entran 1, 6 y 7; la Champions no es copa nacional", ids == [1, 6, 7], ids)
motivos = {x["fixtureId"]: x["motivo"] for x in ex_}
check("contacto.armar: fuera el depositado tarde, la copa y la cuarentena, con su motivo",
      "antes del pitazo" in motivos.get(2, "") and "copa nacional" in motivos.get(3, "")
      and "cuarentena" in motivos.get(4, "") and 5 not in motivos, motivos)
res = {a["fixtureId"]: a["resultado"] for a in ap_}
check("contacto.armar: el resultado del veredicto manda sobre el marcador; sin veredicto, el marcador",
      res == {1: "local", 6: "empate", 7: "visita"}, res)

# 10) COPA NACIONAL FUERA (29/10/2026, usuario: «no hay que contaminar las tablas»)
_sad = _sql.connect(os.path.join(_tmp, "sad.db"))
_sad.execute("INSERT OR REPLACE INTO leagues (id, name, country) VALUES (143, 'Copa del Rey', 'Spain')")
_liga_antes = _sad.execute("SELECT league_id FROM fixtures WHERE id=?", (fids[0],)).fetchone()[0]
_sad.execute("UPDATE fixtures SET league_id=143 WHERE id=?", (fids[0],))
_sad.commit()
out = sim.simulacion()
check("un partido de la Copa del Rey no entra a la simulación y dice por qué",
      fids[0] not in [a["fixtureId"] for a in out["apuestas"]]
      and any(x["fixtureId"] == fids[0] and "copa nacional" in x["motivo"] for x in out["excluidos"]),
      out["excluidos"])
from backend.analisis.escala import copas_nacionales  # noqa: E402
_sad.execute("INSERT OR REPLACE INTO leagues (id, name, country) VALUES (16, 'CONCACAF Champions Cup', 'World')")
_sad.execute("UPDATE fixtures SET league_id=16 WHERE id=?", (fids[2],))
_sad.commit()
check("la Champions Cup de la Concacaf es internacional, no copa nacional",
      copas_nacionales([fids[0], fids[2]]) == {fids[0]: "Copa del Rey"}, copas_nacionales([fids[0], fids[2]]))
_sad.execute("UPDATE fixtures SET league_id=? WHERE id IN (?, ?)", (_liga_antes, fids[0], fids[2]))
_sad.commit()
_sad.close()

# 12) VELOCIDAD SIN CAMBIAR UN NÚMERO (10/11/2026, usuario: «Simulación es bien lenta»)
def _sin_cache():
    return _orig_sim()


_orig_sim = sim._simulacion


_q = lambda d: _json.dumps(d, sort_keys=True, default=str)  # noqa: E731
_a = sim.simulacion()
check("con caché, la simulación es idéntica a la calculada sin caché", _q(_a) == _q(_sin_cache()))
_llamadas = []
sim._simulacion = lambda: (_llamadas.append(1), _orig_sim())[1]
sim.simulacion()
check("una segunda lectura sin cambios no rehace la simulación", _llamadas == [], len(_llamadas))
_sad = _sql.connect(os.path.join(_tmp, "sad.db"))
_sad.execute(f"UPDATE fixtures SET {gol_l}=0, {gol_v}=3, goals_home=0, goals_away=3 WHERE id=?", (fids[2],))
_sad.commit()
_b = sim.simulacion()
check("un resultado nuevo en la base se ve enseguida (idéntico a sin caché)",
      _llamadas == [1] and _q(_b) == _q(_sin_cache()) and _q(_b) != _q(_a))
_sad.execute("UPDATE odds SET odd = odd + 0.5 WHERE fixture_id=?", (fids[0],))
_sad.commit()
_sad.close()
check("una cuota nueva también", _q(sim.simulacion()) == _q(_sin_cache()) and len(_llamadas) == 2, len(_llamadas))
with _conectar() as con:
    _pj = _json.loads(con.execute("SELECT parte_json FROM parte_cowork WHERE fixture_id=?", (fids[0],)).fetchone()[0])
    _pj["pronostico"]["probabilidades"] = {"local": 20, "empate": 30, "visita": 50}
    con.execute("UPDATE parte_cowork SET parte_json=? WHERE fixture_id=?", (_json.dumps(_pj), fids[0]))
check("y un 1X2 re-depositado (aunque no cambie la fecha de actualización)",
      _q(sim.simulacion()) == _q(_sin_cache()) and len(_llamadas) == 3, len(_llamadas))
sim._simulacion = _orig_sim

# el prefiltro de mercados en SQL no cambia ninguna cuota: lo mismo que filtrar todo en Python
from backend.analisis import lecciones as _lec  # noqa: E402
from backend import db as _saddb  # noqa: E402
_orig_q = _saddb.query
_saddb.query = lambda db, sql, p=(): _orig_q(db, sql.split(" AND (bet_name LIKE")[0], p)
_todas = _lec.cuotas_mercado(fids)
_saddb.query = _orig_q
check("cuotas_mercado con el prefiltro SQL = sin él", _q(_lec.cuotas_mercado(fids)) == _q(_todas) and _todas,
      (_lec.cuotas_mercado(fids), _todas))

# EN QUIÉN DESCONFIAR (10/11/2026): la alerta de confianza no toca el elegido ni las estrategias
_a = sim.alerta_confianza({"local": 55, "empate": 25, "visita": 20}, {"local": 50.0, "empate": 27.0, "visita": 23.0}, None)
check("alerta: 5 pts sobre la casa → SOBRE-LA-CASA", _a["activa"] and _a["motivos"][0]["codigo"] == "SOBRE-LA-CASA", _a)
_a = sim.alerta_confianza({"local": 51, "empate": 27, "visita": 22}, {"local": 50.0, "empate": 27.0, "visita": 23.0}, None)
check("alerta: 1 pt sobre la casa no alcanza", not _a["activa"], _a)
_a = sim.alerta_confianza({"local": 50, "empate": 27, "visita": 23}, {"local": 50.0, "empate": 27.0, "visita": 23.0},
                          {"signo": "+", "partidos": 1, "riesgo": "alto"})
check("alerta: racha + de UN partido con riesgo alto → BURBUJA-DE-UN-PARTIDO",
      [m["codigo"] for m in _a["motivos"]] == ["BURBUJA-DE-UN-PARTIDO"], _a)
for _b in ({"signo": "+", "partidos": 3, "riesgo": "alto"}, {"signo": "-", "partidos": 1, "riesgo": "alto"},
           {"signo": "+", "partidos": 1, "riesgo": "bajo"}):
    check(f"alerta: {_b} no es burbuja de un partido",
          not sim.alerta_confianza({"local": 50, "empate": 27, "visita": 23},
                                   {"local": 50.0, "empate": 27.0, "visita": 23.0}, _b)["activa"])
_fs = [
    {"elegido": "local", "resultado": "local", "cuotas": {"local": 2.0, "empate": 3.4, "visita": 4.0},
     "mercado": {"local": 48.0, "empate": 28.0, "visita": 24.0}, "probabilidades": {"local": 52.0, "empate": 27.0, "visita": 21.0},
     "alerta": {"activa": True, "motivos": [{"codigo": "SOBRE-LA-CASA"}]}},
    {"elegido": "local", "resultado": "empate", "cuotas": {"local": 1.8, "empate": 3.6, "visita": 4.5},
     "mercado": {"local": 53.0, "empate": 26.0, "visita": 21.0}, "probabilidades": {"local": 53.0, "empate": 26.0, "visita": 21.0},
     "alerta": {"activa": False, "motivos": []}},
    {"elegido": "visita", "resultado": "local", "cuotas": {"local": 3.5, "empate": 3.4, "visita": 2.1},
     "mercado": {"local": 27.0, "empate": 28.0, "visita": 45.0}, "probabilidades": {"local": 26.0, "empate": 28.0, "visita": 46.0},
     "alerta": {"activa": False, "motivos": []}},
    {"elegido": "local", "resultado": "local", "cuotas": {"local": 1.5, "empate": 4.0, "visita": 6.0},
     "mercado": {"local": 63.0, "empate": 23.0, "visita": 14.0}, "probabilidades": {"local": 63.0, "empate": 23.0, "visita": 14.0},
     "alerta": None},   # anterior al 10/11: no registra
]
_r = sim.resumen_alerta(_fs)
check("resumen: con alerta 1 de 1, sin alerta 0 de 2, lo anterior al 10/11 no cuenta",
      _r["conAlerta"]["n"] == 1 and _r["conAlerta"]["aciertos"] == 1 and _r["sinAlerta"]["n"] == 2
      and _r["sinAlerta"]["aciertos"] == 0 and _r["porMotivo"] == {"SOBRE-LA-CASA": 1}, _r)
check("resumen: la doble oportunidad elegido-o-empate (sin alerta: 1 de 2) y la plana (con alerta: +1 u en 1)",
      _r["sinAlerta"]["dobleOportunidad"]["aciertos"] == 1 and _r["conAlerta"]["roiPlano"] == 1.0, _r)
check("resumen: el descarte (lo menos probable) salió 1 de 3 — el local que le dimos 26 %",
      _r["descarte"]["n"] == 3 and _r["descarte"]["salio"] == 1, _r["descarte"])
check("simular trae alertaConfianza", "alertaConfianza" in sim.simular([]), list(sim.simular([]).keys()))

# EN QUIÉN DESCONFIAR, en el parte (backend/analisis/desconfianza.py)
from backend.analisis import desconfianza as _dsc  # noqa: E402
_nom = {"a": "Local FC", "b": "Visita FC"}
_rev = {"a": {"actual": {"signo": "+", "partidos": 1}, "riesgo": {"nivel": "alto"}}, "b": {}}
_d = _dsc.leer({"probabilidades": {"local": 52, "empate": 27, "visita": 21}},
               {"local": 47.0, "empate": 28.0, "visita": 25.0}, _rev, _nom)
check("parte: alerta con los dos motivos (5 pts sobre la casa y racha de un partido)",
      [m["codigo"] for m in _d["alerta"]["motivos"]] == ["SOBRE-LA-CASA", "BURBUJA-DE-UN-PARTIDO"], _d["alerta"])
check("parte: el descarte resaltado dice que el otro lado no gana",
      _d["dobleOportunidad"]["texto"] == "Visita FC no gana: Local FC o empate" and _d["dobleOportunidad"]["resaltar"]
      and _d["dobleOportunidad"]["nuestra"] == 79.0 and _d["dobleOportunidad"]["casa"] == 75.0, _d["dobleOportunidad"])
check("parte: ventaja por fuerza del local (47 %) en el tramo 35-48 % y de la visita (25 %) en < 35 %",
      _d["ventajaPorFuerza"]["a"]["tramo"] == "35-48 %" and _d["ventajaPorFuerza"]["a"]["noGanaCon1"] == 0.310
      and _d["ventajaPorFuerza"]["b"]["tramo"] == "< 35 %", _d["ventajaPorFuerza"])
_t = _dsc.alerta_tira(_d, _nom)
check("parte: DESCONFIAR a la tira, tipo dato, del lado del elegido",
      len(_t) == 1 and _t[0]["codigo"] == "DESCONFIAR" and _t[0]["tipo"] == "dato" and _t[0]["equipo"] == "a", _t)
_d2 = _dsc.leer({"probabilidades": {"local": 47, "empate": 28, "visita": 25}},
                {"local": 47.0, "empate": 28.0, "visita": 25.0}, {"a": {"actual": {"signo": "+", "partidos": 4},
                                                                         "riesgo": {"nivel": "alto"}}}, _nom)
check("parte: a la par de la casa y con racha larga, sin alerta ni tira", not _d2["alerta"]["activa"]
      and not _dsc.alerta_tira(_d2, _nom) and not _d2["dobleOportunidad"]["resaltar"], _d2["alerta"])
check("parte: sin 1X2 no hay bloque", _dsc.leer({}, None, None, _nom) is None)
check("parte: sin cuotas, la casa queda en null pero el bloque sale",
      _dsc.leer({"probabilidades": {"local": 50, "empate": 27, "visita": 23}}, None, None, _nom)["descarte"]["casa"] is None)
from backend.analisis import parte as _pt  # noqa: E402
check("DESCONFIAR es calculada (se descarta del depósito) y `desconfianza` es eco",
      "DESCONFIAR" in _pt._ALERTAS_CALCULADAS and "desconfianza" in _pt._ECO_PARTE)

# ── EL MÉTODO CON EL MARCADOR (13/11/2026, usuario: «si el marcador más
# probable se alinea con el elegido… lo más probable es que gane»; y «también
# voy a querer un martingala a este método») ─────────────────────────────────
def _apm(fid, pit, res, mp, verde=True):
    p = {"local": 55, "empate": 25, "visita": 20}
    sg = {"1-0": "local", "2-1": "local", "1-1": "empate", "0-1": "visita"}.get(mp)
    return {"fixtureId": fid, "pitazo": pit, "partido": {"local": "A", "visita": "B", "liga": "L"},
            "depositadoEn": pit, "versiones": {}, "versionPrompt": "", "probabilidades": p,
            "cuotas": {"local": 1.8, "empate": 3.6, "visita": 4.5}, "mercado": {"local": 54, "empate": 26, "visita": 20},
            "resultado": res,
            "semaforo": {"estado": "confirma" if verde else "duda", "motivos": []},
            "marcador": ({"masProbable": mp, "prob": 0.12, "signo": sg, "alineado": sg == "local"} if mp else None)}
_om = sim.simular([_apm(1, "2026-11-14 15:00:00", "visita", "1-0"),
                   _apm(2, "2026-11-14 20:00:00", "local", "1-0"),
                   _apm(3, "2026-11-15 15:00:00", "local", "1-1"),
                   _apm(4, "2026-11-15 20:00:00", "local", "2-1", verde=False),
                   _apm(5, "2026-11-16 15:00:00", "local", None)])
_em = {e["clave"]: e for e in _om["estrategias"]}
_fm = {a["fixtureId"]: a for a in _om["apuestas"]}
check("marcador: las tres series nuevas existen (método, verde + marcador, martingala)",
      all(c in _em for c in sim._CON_MARCADOR))
check("metodoMarcador apuesta SOLO con el marcador alineado (1, 2 y 4), no con 1-1 ni sin marcador",
      _em["metodoMarcador"]["apuestas"] == 3
      and _fm[3]["porEstrategia"]["metodoMarcador"]["motivo"] == "el marcador más probable (1-1) no va con el elegido"
      and _fm[5]["porEstrategia"]["metodoMarcador"]["motivo"] == "sin marcador del modelo de goles",
      [_fm[k]["porEstrategia"]["metodoMarcador"] for k in (3, 5)])
check("metodoVerdeMarcador pide además el verde (1 y 2, no el 4 en amarillo)",
      _em["metodoVerdeMarcador"]["apuestas"] == 2
      and _fm[4]["porEstrategia"]["metodoVerdeMarcador"]["motivo"] == "semáforo no está en verde")
# LA MARTINGALA AJUSTADA A LA CUOTA (13/11/2026, usuario): tras perder apuesta
# 1 + lo perdido / (cuota − 1). Cuota 1,80: pierde 1 en el 1 → en el 2 apuesta
# 1 + 1/0,8 = 2,25, gana 1,80 y la línea queda +0,80 (lo de 1 u), sin pérdida
_m1, _m2 = (_fm[1]["porEstrategia"]["martingalaAjustadaVerdeMarcador"],
            _fm[2]["porEstrategia"]["martingalaAjustadaVerdeMarcador"])
_ea = _em["martingalaAjustadaVerdeMarcador"]
check("martingala 🟢⚽ ajustada: pierde 1 u y después apuesta 2,25 (recupera y gana lo de 1 u), misma línea",
      _m1["monto"] == 1.0 and _m1["ganancia"] == -1.0 and _m2["monto"] == 2.25 and _m2["ganancia"] == 1.8
      and _m2["linea"] == _m1["linea"] and _ea["banca"] == 100.8
      and _ea["lineas"]["perdiendo"] == 0 and _ea["lineas"]["perdidaMayor"] == 0, (_m1, _m2, _ea["lineas"]))
check("…pide el verde y el marcador: no apuesta el 3 (1-1), el 4 (amarillo) ni el 5 (sin marcador)",
      _ea["apuestas"] == 2 and _fm[4]["porEstrategia"]["martingalaAjustadaVerdeMarcador"]["motivo"] == "semáforo no está en verde"
      and _fm[3]["porEstrategia"]["martingalaAjustadaVerdeMarcador"]["monto"] == 0
      and _fm[5]["porEstrategia"]["martingalaAjustadaVerdeMarcador"]["monto"] == 0)
check("la 🟢⚽ clásica (sin ajuste) ya no existe, por decisión del usuario",
      "martingalaVerdeMarcador" not in _em and "martingalaMarcador" not in _em)
# la 60 %+ ajustada: dos derrotas seguidas con cuota 1,50 y después un acierto
def _ap60(fid, pit, res):
    a = _apm(fid, pit, res, None)
    a["probabilidades"] = {"local": 65, "empate": 20, "visita": 15}
    a["cuotas"] = {"local": 1.5, "empate": 4.0, "visita": 6.0}
    return a
_o60 = sim.simular([_ap60(21, "2026-11-14 15:00:00", "visita"), _ap60(22, "2026-11-14 20:00:00", "empate"),
                    _ap60(23, "2026-11-15 15:00:00", "local")])
_f60 = {a["fixtureId"]: a["porEstrategia"]["martingala60Ajustada"] for a in _o60["apuestas"]}
_e60 = {e["clave"]: e for e in _o60["estrategias"]}
check("martingala 60 %+ ajustada: 1 → 1 + 1/0,5 = 3 → 1 + 4/0,5 = 9, y el acierto deja la línea en +0,5",
      [_f60[k]["monto"] for k in (21, 22, 23)] == [1.0, 3.0, 9.0] and _f60[23]["ganancia"] == 4.5
      and _e60["martingala60Ajustada"]["banca"] == 100.5, _f60)
check("…mientras la clásica de 60 %+ (1, 2, 4) cierra en −1 con la misma secuencia",
      [a["porEstrategia"]["martingala60"]["monto"] for a in sorted(_o60["apuestas"], key=lambda x: x["fixtureId"])]
      == [1.0, 2.0, 4.0] and _e60["martingala60"]["banca"] == 99.0)
check("el método con el marcador lleva el freno por tramo, como el método",
      _em["metodoMarcador"]["tramos"] is not None and _em["metodoVerdeMarcador"]["tramos"] is not None)
_rm = _om["marcador"]
check("el resumen separa alineados, resto y sin marcador, en todo y en lo nuevo",
      (_rm["nuevo"]["alineado"]["n"], _rm["nuevo"]["resto"]["n"], _rm["nuevo"]["sinMarcador"]["n"]) == (3, 1, 1)
      and _rm["nuevo"]["verdeAlineado"]["n"] == 2 and _rm["desde"] == sim.MARCADOR_DESDE == "2026-11-14 05:00:00", _rm)
_viejo = sim.simular([_apm(9, "2026-11-12 15:00:00", "local", "1-0")])["marcador"]
check("lo anterior al 14/11 entra en «todo» pero NO en el criterio",
      _viejo["todo"]["alineado"]["n"] == 1 and _viejo["nuevo"]["alineado"]["n"] == 0
      and _viejo["criterio"]["estado"] == "en_observacion" and _viejo["criterio"]["faltan"] == 30)


def _crit_m(al, al_ac, resto, resto_ac):
    g = lambda n, k: sim._grupo_semaforo([{"resultado": "local" if i < k else "visita", "elegido": "local",  # noqa: E731
                                           "cuotas": {"local": 1.8}} for i in range(n)])
    return sim.criterio_marcador(g(al, al_ac), g(resto, resto_ac))
_c = _crit_m(29, 25, 100, 50)
check("criterio marcador: con 29 alineados, en observación aunque separe", _c["estado"] == "en_observacion"
      and _c["faltan"] == 1, _c)
_c = _crit_m(30, 20, 100, 50)
check("escalón 30: 66,7 % contra 50 % (+16,7) → PROMETEDOR", _c["estado"] == "prometedor" and _c["escalon"] == 30, _c)
_c = _crit_m(30, 16, 100, 50)
check("escalón 30: +3,3 pts → en observación", _c["estado"] == "en_observacion", _c)
_c = _crit_m(30, 14, 100, 50)
check("escalón 30: los alineados ganan menos → NO SE SOSTIENE", _c["estado"] == "no_se_sostiene", _c)
_c = _crit_m(60, 45, 200, 100)
check("escalón 60: 75 % contra 50 % con el IC entero encima → CONFIRMADO", _c["estado"] == "confirmado"
      and _c["cumple"] and _c["alineadosEncima"], _c)
_c = _crit_m(60, 37, 200, 100)
check("escalón 60: +11,7 pts pero el IC toca el 50 % → sin contacto", _c["estado"] == "sin_contacto", _c)
check("el criterio está fijado (30 · 60, 10 pts)", sim.MARCADOR_ESCALONES == (30, 60) and sim.MARCADOR_SEPARACION == 0.10)

# LA PÁGINA (13/11/2026, usuario: «esa página demora mucho en cargarse»): la
# misma cuenta, solo se manda menos; `linea` va en el orden de `serie`
_pg = sim.paginar(_om, 2, 2)
check("paginar: 5 apuestas de 2 en 2 → 3 páginas, la 2.ª trae 2, y la salida en caché no se toca",
      _pg["paginacion"] == {"pagina": 2, "porPagina": 2, "total": 5, "paginas": 3} and len(_pg["apuestas"]) == 2
      and _pg["apuestas"] == _om["apuestas"][2:4] and len(_om["apuestas"]) == 5 and "linea" not in _om, _pg["paginacion"])
check("…fuera de rango da la última, y `linea` = las cerradas en el orden de estrategias[].serie",
      sim.paginar(_om, 99, 2)["paginacion"]["pagina"] == 3
      and [x["fixtureId"] for x in _pg["linea"]] == [p["fixtureId"] for p in _em["proporcional"]["serie"][1:]]
      and all(set(x) == {"fixtureId", "pitazo", "local", "visita", "resultado", "sad"} for x in _pg["linea"]), _pg["linea"])

# el marcador sale del modelo de goles, con la historia anterior (cacheado por partido)
import backend.analisis.goles as _gm  # noqa: E402
_ac, sim._MARCADOR = _gm._acotar_fixture, {}
_gm._acotar_fixture = lambda fx: {"masProbables": [{"marcador": "0-1", "prob": 0.11}]}  # noqa: E731
try:
    _mk = sim.marcador_de({"id": 77}, "visita")
    _mk2 = sim.marcador_de({"id": 77}, "local")
finally:
    _gm._acotar_fixture = _ac
check("marcador_de: el más probable del modelo de goles, alineado con la visita y no con el local",
      _mk == {"masProbable": "0-1", "prob": 0.11, "signo": "visita", "alineado": True} and _mk2["alineado"] is False, _mk)
sim._MARCADOR = {77: None}
check("…y sin modelo o sin historia, None (no se inventa)", sim.marcador_de({"id": 77}, "local") is None)

# el informe de los lunes (contacto) trae la sección «Marcador» con el del GET del parte
from backend import contacto as _ct  # noqa: E402
_pm = {"lecturaSad": {"golesAcotados": {"masProbables": [{"marcador": "2-1", "prob": 0.1}]}}}
check("contacto._marcador lee lecturaSad.golesAcotados del GET del parte",
      _ct._marcador(_pm, {"local": 50, "empate": 27, "visita": 23})["alineado"] is True
      and _ct._marcador({}, {"local": 50, "empate": 27, "visita": 23}) is None)
check("y el informe lo dice", "Marcador · cuenta desde 2026-11-14" in _ct.informe_marcador(_om)
      and _om["marcador"]["criterio"]["texto"] in _ct.informe_marcador(_om))

print("\nTODO OK" if not fallas else f"\n{fallas} FALLA(S)")
sys.exit(1 if fallas else 0)
