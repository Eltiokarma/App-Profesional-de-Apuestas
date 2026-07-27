"""Despensa EN BLOQUE — investigación versionada en el repo → efe.db.

Por qué existe: el costo del EFE lo domina la búsqueda web de los campos que
las webs de datos NO listan (`dt` y `plantel`). Investigados a mano en el
escritorio y depositados uno a uno, el flujo depende de que alguien se acuerde
(docs/DESPENSA_DESKTOP.md). Aquí esa investigación vive como ARCHIVO en el
repo: se revisa en un PR, viaja con el deploy y se carga sola al arrancar, sin
tokens, sin red y sin clave de API. El ciclo es quincenal porque el TTL de
`dt`/`plantel` son 14 días (DESPENSA_TTL_DIAS).

Formato — backend/analisis/despensa/<liga>.json:

    {
      "liga": "Perú - Primera División",
      "investigado_en": "2026-07-27",          # fecha REAL de la investigación
      "fuentes": ["https://…", "https://…"],
      "equipos": [
        {"equipo": "Sporting Cristal",
         "datos": {"dt": "…", "plantel": "…", "bajas": "…"}}
      ]
    }

Dos reglas que hacen que esto no mienta:

1. `capturado_en` es `investigado_en`, NO el momento de la carga. Un bloque de
   hace un mes entra vencido y el EFE lo cuenta como faltante (y su candado de
   frío salta). Sellarlo con la hora del deploy sería fabricar frescura: el
   análisis creería tener datos de hoy sobre un plantel de hace un mes.
2. Nunca pisa un dato MÁS NUEVO. La carga manual de la víspera (bajas frescas)
   sobrevive a un redeploy que reinyecta el bloque quincenal.

Uso:
    python -m backend.analisis.despensa_bulk            # carga todos los archivos
    python -m backend.analisis.despensa_bulk --listar   # qué hay, sin escribir
    python -m backend.analisis.despensa_bulk --liga peru-primera --forzar
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

from backend.analisis import db as efedb
from backend.nombres import canonizar, normalizar

DIR_DESPENSA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "despensa")

# tipos aceptados en un bloque: los del EFE + la cronología del timeline
TIPOS_VALIDOS = set(efedb.TIPOS) | {"timeline_eventos"}


def _equipos_de_la_app() -> list[tuple[str, str]]:
    """[(teams.name, normalizado)] de sad.db. Vacío si la DB no está montada
    (entorno sin datos): entonces no se canoniza y el nombre viaja tal cual."""
    try:
        from backend import db as saddb
        return [(r["name"], normalizar(r["name"])) for r in saddb.query("sad", "SELECT name FROM teams")]
    except Exception as e:
        print(f"[despensa-bulk] sin sad.db para canonizar ({e}): los nombres van tal cual")
        return []


def archivos(liga: str | None = None, directorio: str | None = None) -> list[str]:
    patron = os.path.join(directorio or DIR_DESPENSA, f"{liga or '*'}.json")
    return sorted(glob.glob(patron))


def _fecha_valida(txt: str) -> str | None:
    """'YYYY-MM-DD' → 'YYYY-MM-DD 00:00:00' (formato de capturado_en)."""
    try:
        d = datetime.strptime((txt or "").strip()[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    if d > datetime.now(timezone.utc):
        return None  # investigación fechada en el futuro: no sella frescura falsa
    return d.strftime("%Y-%m-%d %H:%M:%S")


def _capturado_de(con, equipo: str, tipo: str) -> str | None:
    fila = con.execute(
        "SELECT capturado_en FROM investigacion WHERE equipo=? AND tipo=?", (equipo, tipo)
    ).fetchone()
    return fila["capturado_en"] if fila else None


def cargar_archivo(ruta: str, forzar: bool = False) -> dict:
    """Deposita un bloque. Devuelve el resumen de lo que hizo y lo que no."""
    res = {"archivo": os.path.basename(ruta), "depositados": 0, "conservados": 0,
           "vacios": 0, "ignorados": [], "canonizados": {}, "equipos": 0,
           "sin_equipo": [], "error": None}
    try:
        with open(ruta, encoding="utf-8") as f:
            bloque = json.load(f)
    except (OSError, ValueError) as e:
        res["error"] = f"ilegible: {e}"  # un archivo roto no tumba a los demás
        return res

    capturado = _fecha_valida(bloque.get("investigado_en", ""))
    if not capturado:
        res["error"] = f"investigado_en inválido o futuro: {bloque.get('investigado_en')!r}"
        return res
    fuentes = bloque.get("fuentes") or []
    equipos_app = _equipos_de_la_app()

    with efedb.conectar() as con:
        for e in bloque.get("equipos") or []:
            nombre = (e.get("equipo") or "").strip()
            if not nombre:
                continue
            res["equipos"] += 1
            # el nombre de los medios y el de la app (API-Football) no siempre
            # coinciden ("Deportivo Moquegua" vs "UCV Moquegua"): el bloque
            # puede traer `alias` y se prueba en orden hasta dar con uno que
            # exista en la app. Sin alias que case, manda el nombre principal.
            candidatos = [nombre] + [a for a in (e.get("alias") or []) if isinstance(a, str)]
            canon = nombre
            if equipos_app:
                nombres_app = {n for n, _ in equipos_app}
                # el primero que EXISTA en la app manda; si ninguno casa, se
                # cae al nombre principal — quedarse con el último alias
                # probado depositaría el dato bajo un nombre arbitrario
                canon = canonizar(nombre, equipos_app)
                for cand in candidatos:
                    c = canonizar(cand, equipos_app)
                    if c in nombres_app:
                        canon = c
                        break
            if canon != nombre:
                res["canonizados"][nombre] = canon
            # el nombre no existe en la app: el dato se guardaría bajo una clave
            # que el EFE nunca consulta — trabajo perdido en silencio. Se
            # deposita igual (por si el equipo entra luego) pero se canta.
            if equipos_app and canon not in {n for n, _ in equipos_app}:
                res["sin_equipo"].append(nombre)
            for tipo, contenido in (e.get("datos") or {}).items():
                if tipo not in TIPOS_VALIDOS:
                    res["ignorados"].append(tipo)
                    continue
                if tipo == "timeline_eventos":
                    if not isinstance(contenido, list) or not contenido:
                        res["vacios"] += 1
                        continue
                else:
                    contenido = contenido.strip() if isinstance(contenido, str) else ""
                    if not contenido:
                        # campo que la web no dio: se deja vacío a propósito,
                        # el EFE lo buscará. Guardar "" sería peor: pasaría por
                        # dato fresco y el análisis no buscaría nada.
                        res["vacios"] += 1
                        continue
                previo = _capturado_de(con, canon, tipo)
                if previo and previo > capturado and not forzar:
                    res["conservados"] += 1  # lo de la DB es más nuevo: no se pisa
                    continue
                con.execute(
                    "INSERT OR REPLACE INTO investigacion (equipo, tipo, contenido, fuentes, capturado_en) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (canon, tipo, json.dumps(contenido, ensure_ascii=False),
                     json.dumps(fuentes, ensure_ascii=False), capturado),
                )
                res["depositados"] += 1
        con.commit()
    res["ignorados"] = sorted(set(res["ignorados"]))
    return res


def cargar_todo(liga: str | None = None, directorio: str | None = None,
                forzar: bool = False) -> list[dict]:
    rutas = archivos(liga, directorio)
    if not rutas:
        print(f"[despensa-bulk] sin archivos en {directorio or DIR_DESPENSA}")
        return []
    salida = []
    for ruta in rutas:
        r = cargar_archivo(ruta, forzar)
        salida.append(r)
        if r["error"]:
            print(f"[despensa-bulk] {r['archivo']}: ERROR {r['error']}", flush=True)
        else:
            print(f"[despensa-bulk] {r['archivo']}: {r['depositados']} datos de "
                  f"{r['equipos']} equipos · {r['conservados']} conservados (más nuevos) · "
                  f"{r['vacios']} campos vacíos"
                  + (f" · canonizados: {r['canonizados']}" if r["canonizados"] else "")
                  + (f" · tipos ignorados: {r['ignorados']}" if r["ignorados"] else ""), flush=True)
            if r["sin_equipo"]:
                print(f"[despensa-bulk] ⚠ NO existen en la app (nadie leerá su despensa; "
                      f"corrige el nombre en el archivo): {sorted(set(r['sin_equipo']))}", flush=True)
    return salida


def _listar(liga: str | None, directorio: str | None) -> None:
    """Qué hay en los archivos y qué edad tendrá cada bloque, sin escribir."""
    hoy = datetime.now(timezone.utc)
    for ruta in archivos(liga, directorio):
        try:
            with open(ruta, encoding="utf-8") as f:
                b = json.load(f)
        except (OSError, ValueError) as e:
            print(f"{os.path.basename(ruta)}: ilegible ({e})")
            continue
        cap = _fecha_valida(b.get("investigado_en", ""))
        edad = (hoy - datetime.strptime(cap, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)).days if cap else None
        equipos = b.get("equipos") or []
        llenos = sum(1 for e in equipos for v in (e.get("datos") or {}).values() if v)
        ttl = efedb.TTL_HORAS.get("dt", 336) / 24
        gracia = efedb.GRACIA_HORAS.get("dt", 0) / 24
        if edad is None:
            estado = "sin fecha válida"
        elif edad < ttl:
            estado = f"{edad} días · VENCE en {int(ttl - edad)} días"
        elif edad < ttl + gracia:
            # dentro de gracia el EFE lo sigue usando: no cuesta, pero avisa
            estado = (f"{edad} días · VENCIDO, aún servido con su edad declarada "
                      f"({int(ttl + gracia - edad)} días antes de volver a costar)")
        else:
            estado = f"{edad} días · VENCIDO y fuera de gracia: cada EFE vuelve a buscar en la web"
        print(f"{os.path.basename(ruta)}: {b.get('liga', '?')} · {len(equipos)} equipos · "
              f"{llenos} campos con dato · investigado {b.get('investigado_en')} ({estado})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Carga la despensa en bloque del repo → efe.db")
    ap.add_argument("--liga", help="nombre del archivo sin .json (default: todos)")
    ap.add_argument("--dir", dest="directorio", help="carpeta de bloques (default: la del repo)")
    ap.add_argument("--forzar", action="store_true", help="pisa también lo que en la DB sea más nuevo")
    ap.add_argument("--listar", action="store_true", help="solo informa: qué hay y qué edad tiene")
    args = ap.parse_args()
    if args.listar:
        _listar(args.liga, args.directorio)
        return 0
    res = cargar_todo(args.liga, args.directorio, args.forzar)
    return 1 if any(r["error"] for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())
