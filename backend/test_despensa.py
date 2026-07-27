"""Test de la despensa EN BLOQUE (backend/analisis/despensa_bulk.py) — sin red.

Lo que blinda: que un barrido quincenal depositado en el repo llegue a la clave
que el EFE consulta, con la EDAD REAL de la investigación y sin pisar lo que se
cargó a mano después. Si algo de esto se rompe, el síntoma no es un error: es
que cada análisis vuelve a buscar en la web y a costar de más.

    python -m backend.test_despensa
"""
import json
import os
import sys
import tempfile

# la despensa vive junto a las DBs: se apunta a un temporal ANTES de importar
_TMP = tempfile.mkdtemp(prefix="sad-despensa-")
os.environ["SAD_DATA_DIR"] = _TMP

from backend.analisis import db as efedb  # noqa: E402
from backend.analisis import despensa_bulk  # noqa: E402
from backend.nombres import canonizar, normalizar  # noqa: E402

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def escribir(dir_, nombre, bloque) -> str:
    ruta = os.path.join(dir_, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(bloque, f, ensure_ascii=False)
    return ruta


def bloque(fecha="2026-07-20", dt="Contexto del DT", equipo="Sporting Cristal"):
    return {"liga": "L", "investigado_en": fecha, "fuentes": ["https://x"],
            "equipos": [{"equipo": equipo, "datos": {"dt": dt, "plantel": "", "bajas": ""}}]}


def limpiar():
    with efedb.conectar() as con:
        con.execute("DELETE FROM investigacion")
        con.commit()


def capturado(equipo, tipo):
    with efedb.conectar() as con:
        f = con.execute("SELECT contenido, capturado_en FROM investigacion WHERE equipo=? AND tipo=?",
                        (equipo, tipo)).fetchone()
    return (json.loads(f["contenido"]), f["capturado_en"]) if f else (None, None)


def main():
    tmp = tempfile.mkdtemp(prefix="bloques-")

    # ── la fecha del archivo es la que manda (TTL honesto) ──────────────────
    limpiar()
    escribir(tmp, "liga.json", bloque(fecha="2026-07-20"))
    despensa_bulk.cargar_todo(directorio=tmp)
    cont, cap = capturado("Sporting Cristal", "dt")
    check("deposita el dato bajo el equipo", cont == "Contexto del DT", cont)
    check("capturado_en = fecha de investigación, no la de carga",
          cap == "2026-07-20 00:00:00", cap)

    # ── no pisa lo más nuevo (la carga manual de la víspera sobrevive) ──────
    efedb.guardar_investigacion("Sporting Cristal", "dt", "DATO NUEVO A MANO")
    despensa_bulk.cargar_todo(directorio=tmp)
    cont, _ = capturado("Sporting Cristal", "dt")
    check("un redeploy NO pisa el dato más nuevo", cont == "DATO NUEVO A MANO", cont)
    despensa_bulk.cargar_todo(directorio=tmp, forzar=True)
    cont, _ = capturado("Sporting Cristal", "dt")
    check("--forzar sí lo pisa", cont == "Contexto del DT", cont)

    # ── campos vacíos NO se guardan ────────────────────────────────────────
    _, cap_p = capturado("Sporting Cristal", "plantel")
    check("un campo vacío no se deposita (el EFE debe buscarlo)", cap_p is None, cap_p)

    # ── el bloque más nuevo del repo sí actualiza ──────────────────────────
    escribir(tmp, "liga.json", bloque(fecha="2026-07-26", dt="DT actualizado"))
    despensa_bulk.cargar_todo(directorio=tmp)
    cont, cap = capturado("Sporting Cristal", "dt")
    check("un bloque más reciente actualiza", cont == "DT actualizado" and cap == "2026-07-26 00:00:00", (cont, cap))

    # ── archivos rotos: no tumban la carga ni mienten ──────────────────────
    roto = os.path.join(tmp, "roto.json")
    with open(roto, "w", encoding="utf-8") as f:
        f.write("{ esto no es json")
    escribir(tmp, "futuro.json", bloque(fecha="2099-01-01"))
    res = {r["archivo"]: r for r in despensa_bulk.cargar_todo(directorio=tmp)}
    check("archivo ilegible → error propio, los demás siguen", bool(res["roto.json"]["error"]), res["roto.json"])
    check("fecha futura → rechazada (no sella frescura falsa)",
          bool(res["futuro.json"]["error"]), res["futuro.json"])
    check("el archivo bueno se cargó igual", res["liga.json"]["error"] is None, res["liga.json"])
    os.remove(roto)
    os.remove(os.path.join(tmp, "futuro.json"))

    # ── TTL: lo que el EFE ve como fresco ──────────────────────────────────
    limpiar()
    escribir(tmp, "liga.json", bloque(fecha="2026-07-26"))
    despensa_bulk.cargar_todo(directorio=tmp)
    frescos, faltantes = efedb.investigacion_de("Sporting Cristal")
    check("el EFE lo ve fresco y deja de contarlo faltante",
          "dt" in frescos and "dt" not in faltantes, (list(frescos), faltantes))
    check("lo no investigado sigue en faltantes", "plantel" in faltantes, faltantes)

    # ── canonización: los nombres del barrido contra los nombres de la app ──
    # (API-Football nombra distinto que los medios; sin este puente el dato se
    #  guarda bajo una clave que nadie consulta)
    print("\n— canonización de los nombres investigados —")
    app = ["Universitario", "Alianza Lima", "Sporting Cristal", "Deportivo Garcilaso",
           "FBC Melgar", "Cusco FC", "Cienciano", "Alianza Atletico", "Atletico Grau",
           "Sport Huancayo", "Sport Boys", "ADT", "Los Chankas", "UTC Cajamarca",
           "Comerciantes Unidos", "Juan Pablo II", "FC Cajamarca", "UCV Moquegua"]
    equipos = [(n, normalizar(n)) for n in app]
    ruta_real = os.path.join(despensa_bulk.DIR_DESPENSA, "peru-primera.json")
    with open(ruta_real, encoding="utf-8") as f:
        real = json.load(f)
    nombres_app = set(app)
    sin_match = []
    for e in real["equipos"]:
        # mismo orden que el cargador: nombre principal y luego los alias
        if not any(canonizar(c, equipos) in nombres_app
                   for c in [e["equipo"]] + (e.get("alias") or [])):
            sin_match.append(e["equipo"])
    check(f"los {len(real['equipos'])} equipos del barrido casan con nombres de la app",
          not sin_match, f"sin match: {sin_match}")
    check("acentos y orden de palabras no importan",
          canonizar("Atlético Grau", equipos) == "Atletico Grau"
          and canonizar("Cajamarca FC", equipos) == "FC Cajamarca", "")
    # "Alianza" casa con Alianza Lima Y con Alianza Atletico: ambiguo, no se
    # elige uno al azar (meter el dato en el club equivocado es peor que no meterlo)
    check("un nombre ambiguo se queda como está (no inventa equipo)",
          canonizar("Alianza", equipos) == "Alianza", canonizar("Alianza", equipos))

    print("\n" + ("TODO OK" if fallos == 0 else f"{fallos} FALLAS"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
