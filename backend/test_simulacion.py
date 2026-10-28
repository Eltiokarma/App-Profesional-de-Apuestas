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
larga = [ap(100 + i, f"2026-10-29 {i:02d}:00:00", (60, 25, 15), (1.5, 4, 6), "visita") for i in range(8)]
mg = est(sim.simular(larga), "martingala")
check("martingala quiebra con 7 derrotas (1+2+…+64 > 100)", mg["banca"] == 0 and mg["quebro"] == 106, mg)
check("caída máxima 100 %", mg["caidaMaxima"] == 1.0, mg)

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
check("simulacion() responde con las cinco estrategias", len(out["estrategias"]) == 5, out.keys())
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

print("\nTODO OK" if not fallas else f"\n{fallas} FALLA(S)")
sys.exit(1 if fallas else 0)
