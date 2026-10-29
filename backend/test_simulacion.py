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

# 8) el armado desde la base corre sobre la demo (sin partes desde el 28/10: vacío, no un error)
out = sim.simulacion()
check("simulacion() responde con las siete estrategias", len(out["estrategias"]) == 7, out.keys())
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

print("\nTODO OK" if not fallas else f"\n{fallas} FALLA(S)")
sys.exit(1 if fallas else 0)
