"""Tests del modo de fallo del veredicto (Jev) — sin red y sin clave.

    python3 -m backend.test_modo_fallo

La frontera: solo se etiquetan lados con fallo o parcial Y con prosa; sin
clave no sale ninguna etiqueta; la taxonomía es cerrada y tiene salida; el
«pide mover un número» se decide por probabilidad con zona gris; y el
agrupado del dossier cuenta sin puntuar.
"""
import os as _os_cache; _os_cache.environ.setdefault("SAD_CACHE_OBJETIVO_S", "0")  # los tests cambian fichas y veredictos y releen
_os_cache.environ.setdefault("SAD_CACHE_INVENTARIO_S", "0")  # ídem el inventario de lecciones
import json
import os
import sys
import tempfile

fallos = 0
os.environ.pop("TYPESAFE_API_KEY", None)
os.environ.pop("SAD_JEV_GUION", None)

from backend.analisis import modo_fallo as mf  # noqa: E402


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
        print(f"  FALLA  {nombre}" + (f" — {detalle}" if detalle else ""))
    else:
        print(f"  ok     {nombre}")


NOMBRES = {"a": "Alianza Lima", "b": "Sporting Cristal"}
POR_LADO = {
    "a": {"veredicto": "acierto", "queP": "ganó como se dijo", "leccion": "", "skill": ""},
    "b": {"veredicto": "fallo", "queP": "expulsión al 30' y penal en el descuento",
          "leccion": "el índice de echada tiene que subir dos puntos cuando el rival juega con diez",
          "skill": "teorema-del-echado", "reglaTocada": "escala de P(echada)"},
}

print("\n== qué se pregunta ==")
preg = mf.preguntas_de(POR_LADO, NOMBRES)
check("un acierto no se etiqueta", "modo_a" not in preg and "mueve_a" not in preg)
check("un fallo con prosa se etiqueta (modo + mueve)", {"modo_b", "mueve_b"} <= set(preg))
check("la taxonomía tiene salida «no lo dice»", "no_lo_dice" in preg["modo_b"]["criteria"])
check("las opciones son exactamente la taxonomía", set(preg["modo_b"]["criteria"]) == set(mf.MODOS))
sin_prosa = {"b": {"veredicto": "fallo", "queP": "", "leccion": ""}}
check("un fallo sin prosa no se pregunta", mf.preguntas_de(sin_prosa, NOMBRES) == {})
parcial = {"b": {**POR_LADO["b"], "veredicto": "parcial", "leccion": ""}}
p2 = mf.preguntas_de(parcial, NOMBRES)
check("un parcial con queP pero sin lección pregunta el modo y no el «mueve»",
      "modo_b" in p2 and "mueve_b" not in p2)
estado = mf._estado(POR_LADO, NOMBRES)
check("la prosa va en el estado y no en las instrucciones",
      POR_LADO["b"]["leccion"] in json.dumps(estado, ensure_ascii=False)
      and all(POR_LADO["b"]["leccion"] not in q["instructions"] for q in preg.values()))

print("\n== A0 (17/11/2026): `lectura_efe` pasa a `lectura`; lo sellado se lee con el nombre nuevo ==")
check("la taxonomía trae `lectura` y no `lectura_efe`", "lectura" in mf.MODOS and "lectura_efe" not in mf.MODOS)
check("lo sellado como `lectura_efe` se lee como `lectura`; lo demás no cambia",
      mf.canonico("lectura_efe") == "lectura" and mf.canonico("tde") == "tde" and mf.canonico(None) is None)
from backend.analisis import lecciones as _lec
_base = {"veredicto": "fallo", "orden": 1, "modoFallo": "lectura"}
_items = [
    {**_base, "clave": "1:a:1", "skill": "diagnostico-tactico", "reglaTocada": "M2 · tabla F1 sin rehacer con el once"},
    {**_base, "clave": "2:a:1", "skill": "teorema-del-echado", "reglaTocada": "disciplina 44 (b)"},
    {**_base, "clave": "3:a:1", "skill": "efe-clasificador", "reglaTocada": "F1"},
    {**_base, "clave": "4:a:1", "skill": "teorema-del-echado", "reglaTocada": "rama once alternativo, rotación",
     "veredicto": "acierto"},
]
_x = _lec.lectura_con_insumo_efe(_items)
check("la cuenta cruzada del EFE: solo fallos de OTROS skills cuya regla nombra un insumo del EFE",
      _x["claves"] == ["1:a:1"] and _x["porSkill"] == {"diagnostico-tactico": 1}, _x)

print("\n== sin clave: nada se etiqueta ==")
ev = mf.evaluar(POR_LADO, NOMBRES)
check("se evaluó y se marcó simulado", ev["simulado"] is True and ev["preguntas"] == 2)
check("el lado con fallo queda sin modo y sin decisión sobre mover",
      ev["lados"]["b"]["modo"] is None and ev["lados"]["b"]["proponeMoverNumero"] is None, ev["lados"])
check("el lado con acierto no aparece", "a" not in ev["lados"])
check("la taxonomía viaja para que la pantalla no la adivine", ev["taxonomia"] == list(mf.MODOS))

print("\n== con guion: la etiqueta y la zona gris del «mueve» ==")
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
    json.dump({"modo_b": {"valor": "tde", "confianza": 0.9, "comoReal": True},
               "mueve_b": {"valor": 0.92, "comoReal": True}}, fh)
    ruta = fh.name
os.environ["SAD_JEV_GUION"] = ruta
ev = mf.evaluar(POR_LADO, NOMBRES)
check("con confianza el modo se etiqueta", ev["lados"]["b"]["modo"] == "tde", ev["lados"])
check("p=0.92 → pide mover un número", ev["lados"]["b"]["proponeMoverNumero"] is True)
check("el modelo sellado es el del guion", ev["modelo"] == "guion" and ev["simulado"] is False)
for p, esperado in ((0.5, None), (0.2, False), (0.7, True)):
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump({"modo_b": {"valor": "tde", "confianza": 0.9, "comoReal": True},
                   "mueve_b": {"valor": p, "comoReal": True}}, fh)
    check(f"p={p} → proponeMoverNumero={esperado}",
          mf.evaluar(POR_LADO, NOMBRES)["lados"]["b"]["proponeMoverNumero"] is esperado)
with open(ruta, "w", encoding="utf-8") as fh:
    json.dump({"modo_b": {"valor": "imprevisto", "confianza": 0.4, "comoReal": True}}, fh)
ev = mf.evaluar(POR_LADO, NOMBRES)
check("un modo con confianza baja se deja en None (no se adivina)",
      ev["lados"]["b"]["modo"] is None and ev["lados"]["b"]["modoConfianza"] == 0.4)
os.environ.pop("SAD_JEV_GUION", None)
os.unlink(ruta)

print("\n== el agrupado del dossier cuenta, no puntúa ==")
from backend.analisis.lecciones import _por_modo_fallo  # noqa: E402
items = [
    {"veredicto": "fallo", "modoFallo": "tde", "proponeMoverNumero": True, "puedeMoverNumeros": False, "clave": "1:b"},
    {"veredicto": "fallo", "modoFallo": "tde", "proponeMoverNumero": False, "puedeMoverNumeros": True, "clave": "2:b"},
    {"veredicto": "parcial", "modoFallo": None, "proponeMoverNumero": None, "puedeMoverNumeros": True, "clave": "3:a"},
    {"veredicto": "acierto", "modoFallo": None, "proponeMoverNumero": True, "puedeMoverNumeros": True, "clave": "4:a"},
]
g = _por_modo_fallo(items)
check("cuenta fallos y parciales, no aciertos", g["fallos"] == 3)
check("agrupa por modo y cuenta los sin etiqueta", g["porModo"] == {"tde": 2} and g["sinEtiqueta"] == 1, g)
check("la alarma: piden mover un número sin poder sostenerlo",
      g["pidenMoverNumero"] == 2 and g["pidenMoverSinPoder"] == ["1:b"], g)
check("y lo dice: agrupan, no puntúan", "no puntúan" in g["nota"])

print("\n== la etiqueta que no llegó (24/11/2026: Jev 402 sin crédito desde el 22/11) ==")
from backend.analisis import escaneo as _esc  # noqa: E402
_err402 = 'Jev respondió 402: {"error":"Insufficient credits"}'
_filas = [
    {"fixture_id": 1, "fecha": "2026-11-22", "coherencia_json": None,
     "modo_fallo_json": json.dumps({"error": _err402, "lados": {}}, ensure_ascii=False)},
    {"fixture_id": 2, "fecha": "2026-11-22", "coherencia_json": json.dumps({"error": _err402, "hallazgos": []}),
     "modo_fallo_json": None},
    {"fixture_id": 3, "fecha": "2026-11-20", "coherencia_json": json.dumps({"error": None}),
     "modo_fallo_json": json.dumps({"error": None, "lados": {"a": {"modo": "tde"}}})},
]
_h = _esc._jev_errores(_filas)
check("el escaneo grita el sello con error, del veredicto y del parte, y calla lo sano",
      [x["fixtureId"] for x in _h] == [1, 2] and all(x["chequeo"] == "jev-caido" for x in _h)
      and "402" in _h[0]["detalle"] and "coherencia" in _h[1]["detalle"], _h)
check("el chequeo se DEPOSITA (no es informativo) y su área existe",
      not _esc.CHEQUEOS["jev-caido"].get("informativo") and _esc.CHEQUEOS["jev-caido"]["area"] == "api")
check("solo el sello con error y sin lados se re-etiqueta; lo etiquetado y lo viejo (null) no",
      mf._sin_etiqueta_por_error({"error": _err402, "lados": {}})
      and not mf._sin_etiqueta_por_error({"error": None, "lados": {"a": {}}})
      and not mf._sin_etiqueta_por_error(None))

# sobre una base de partes de verdad (temporal)
_tmp = tempfile.mkdtemp(prefix="sad_mf_")
from backend.seed_demo import seed as _seed  # noqa: E402
_seed(_tmp)   # el nombre de los equipos sale de sad.db (parte._fixture)
os.environ["SAD_DATA_DIR"] = _tmp
import backend.db as _dbmod  # noqa: E402
_dbmod.BASE_DIR = _tmp
from backend.analisis import parte as _parte  # noqa: E402
_v = {"porLado": POR_LADO}
_sano = {"error": None, "lados": {"b": {"modo": "imprevisto"}}, "evaluadoEn": "2026-11-20T00:00:00+00:00"}
with _parte._conectar() as con:
    _cols = {r[1] for r in con.execute("PRAGMA table_info(parte_cowork)")}
    for fid, mfj in ((10, {"error": _err402, "lados": {}, "evaluadoEn": "2026-11-22T01:31:00+00:00"}),
                     (11, _sano), (12, None)):
        fila = {"fixture_id": fid, "fecha": "2026-11-22", "parte_json": "{}", "creado_en": "2026-11-21 00:00:00",
                "actualizado_en": "2026-11-21 00:00:00",
                "veredicto_json": json.dumps(_v, ensure_ascii=False),
                "modo_fallo_json": json.dumps(mfj, ensure_ascii=False) if mfj else None}
        fila = {k: v for k, v in fila.items() if k in _cols}
        con.execute(f"INSERT INTO parte_cowork ({','.join(fila)}) VALUES ({','.join('?' * len(fila))})",
                    tuple(fila.values()))
r = mf.reetiquetar()
check("sin aplicar solo cuenta: 1 pendiente (el 402), ni el sano ni el viejo",
      r["pendientes"] == 1 and r["reetiquetados"] == [] and list(r["erroresSellados"].values()) == [1], r)
r = mf.reetiquetar(aplicar=True)
check("sin clave no re-etiqueta con respuestas simuladas", r["reetiquetados"] == [] and r["cortadoPor"], r)
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
    json.dump({"modo_b": {"valor": "imprevisto", "confianza": 0.9, "comoReal": True}}, fh)
    ruta = fh.name
os.environ["SAD_JEV_GUION"] = ruta
_disp, _preg = mf.jev.disponible, mf.jev.preguntar
mf.jev.disponible = lambda: True   # con clave …


def _sigue_sin_credito(estado, preguntas, modelo=""):
    raise mf.jev.JevError(_err402)


mf.jev.preguntar = _sigue_sin_credito
try:
    r_corta = mf.reetiquetar(aplicar=True)
    mf.jev.preguntar = mf.jev._simular   # … y el guion responde en lugar de la red
    r = mf.reetiquetar(aplicar=True)
finally:
    mf.jev.disponible, mf.jev.preguntar = _disp, _preg
    os.environ.pop("SAD_JEV_GUION", None)
    os.unlink(ruta)
with _parte._conectar() as con:
    _n = {f["fixture_id"]: json.loads(f["modo_fallo_json"]) if f["modo_fallo_json"] else None
          for f in con.execute("SELECT fixture_id, modo_fallo_json FROM parte_cowork")}
check("si Jev sigue sin crédito corta en el primero y no pisa nada",
      r_corta["reetiquetados"] == [] and "402" in (r_corta["cortadoPor"] or ""), r_corta)
check("con clave: el 402 se re-etiqueta y deja dicho de qué error venía",
      r["reetiquetados"] == [10] and _n[10]["lados"]["b"]["modo"] == "imprevisto"
      and "402" in _n[10]["reetiquetado"]["errorAnterior"], (r, _n[10]))
check("lo ya etiquetado y lo de antes de Jev no se tocan", _n[11] == _sano and _n[12] is None, _n)
check("una segunda pasada no encuentra nada", mf.reetiquetar()["pendientes"] == 0)

print(f"\n{'TODO OK' if not fallos else str(fallos) + ' FALLAS'}")
sys.exit(1 if fallos else 0)
