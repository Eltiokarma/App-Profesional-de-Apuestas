"""NBA · fase 0 · descarga de marcadores y cuotas de cierre (docs/NBA_FASE0.md).

Fuente: la API pública (no documentada) de ESPN, sin clave:
  - marcador por día:  site.api.espn.com/.../nba/scoreboard?dates=AAAAMMDD
  - cuotas por partido: sports.core.api.espn.com/.../events/{id}/competitions/{id}/odds
    (ganador y hándicap de cada casa; desde 2015-16).

Es SOLO para medir (fase 0): nada de esto entra a sad.db ni a la app. Guarda
en `$SAD_NBA_DIR` (por defecto ./nba_data, fuera de git):
  dias/AAAAMMDD.json    partidos del día ya recortados
  cuotas/{id}.json      una fila por casa
Se puede cortar y retomar: lo que ya está en disco no se vuelve a pedir
(salvo los últimos 3 días, que pueden no estar cerrados).

    python -m backend.nba.descarga                     # 2015-10-01 → hoy
    python -m backend.nba.descarga --desde 2024-10-01 --hilos 4
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone

URL_DIA = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={d}&limit=100"
URL_CUOTAS = ("https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/events/{i}"
              "/competitions/{i}/odds?limit=100")
FRANQUICIAS = set(range(1, 31))   # ids de ESPN de los 30 equipos (afuera: All-Star, giras)
TIPOS = {2: "regular", 3: "playoffs", 5: "play-in"}
# La burbuja de Orlando (30/07 → 11/10/2020): ESPN no la marca neutral, pero no hubo localía
BURBUJA_2020 = ("2020-07-30", "2020-10-12")
INICIO = "2015-10-01"


def carpeta() -> str:
    return os.environ.get("SAD_NBA_DIR", "nba_data")


def _get(url: str, intentos: int = 5) -> dict | None:
    for n in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "sad-fase0/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"  HTTP {e.code} en {url} (intento {n + 1})", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            print(f"  {type(e).__name__} en {url} (intento {n + 1})", file=sys.stderr)
        time.sleep(1.5 * 2 ** n + random.random())
    raise RuntimeError(f"sin respuesta tras {intentos} intentos: {url}")


def _int(x) -> int | None:
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def recortar_dia(crudo: dict) -> list[dict]:
    """Del scoreboard de ESPN a lo que usa la fase 0. Solo partidos TERMINADOS
    de temporada regular, play-in y playoffs entre dos franquicias."""
    out = []
    for e in crudo.get("events", []):
        temp = e.get("season") or {}
        if temp.get("type") not in TIPOS:
            continue
        c = (e.get("competitions") or [{}])[0]
        if not ((c.get("status") or {}).get("type") or {}).get("completed"):
            continue
        lados = {t.get("homeAway"): t for t in c.get("competitors", [])}
        if set(lados) != {"home", "away"}:
            continue
        loc, vis = lados["home"], lados["away"]
        li, vi = _int(loc["team"]["id"]), _int(vis["team"]["id"])
        pl, pv = _int(loc.get("score")), _int(vis.get("score"))
        if li not in FRANQUICIAS or vi not in FRANQUICIAS or pl is None or pv is None or pl == pv:
            continue
        fecha = e.get("date") or c.get("date")
        neutral = bool(c.get("neutralSite")) or BURBUJA_2020[0] <= fecha[:10] <= BURBUJA_2020[1]
        out.append({"id": int(e["id"]), "fecha": fecha, "temporada": temp.get("year"), "tipo": TIPOS[temp["type"]],
                    "localId": li, "local": loc["team"].get("abbreviation"),
                    "visitaId": vi, "visita": vis["team"].get("abbreviation"),
                    "ptsLocal": pl, "ptsVisita": pv, "neutral": neutral})
    return out


def _num(x) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v


def recortar_cuotas(crudo: dict) -> list[dict]:
    """Una fila por casa: ganador (americana) y hándicap DEL LOCAL (negativo =
    local favorito), con su cuota. Se queda con el valor de cierre/actual que
    ESPN deja arriba de todo (en los partidos terminados es el último)."""
    filas = []
    for it in crudo.get("items", []):
        casa = (it.get("provider") or {}).get("name") or "?"
        h, a = it.get("homeTeamOdds") or {}, it.get("awayTeamOdds") or {}
        filas.append({"casa": casa,
                      "mlLocal": _num(h.get("moneyLine")), "mlVisita": _num(a.get("moneyLine")),
                      "spreadLocal": _num(it.get("spread")),
                      "spreadCuotaLocal": _num(h.get("spreadOdds")), "spreadCuotaVisita": _num(a.get("spreadOdds")),
                      "favoritoLocal": h.get("favorite")})
    return filas


def dias(desde: str, hasta: str) -> list[str]:
    d, fin = date.fromisoformat(desde), date.fromisoformat(hasta)
    out = []
    while d <= fin:
        # julio-septiembre no hay NBA (salvo la burbuja de 2020)
        if not (date(d.year, 7, 15) <= d <= date(d.year, 9, 30)) or d.year == 2020:
            out.append(d.strftime("%Y%m%d"))
        d += timedelta(days=1)
    return out


def bajar(desde: str = INICIO, hasta: str | None = None, hilos: int = 4) -> dict:
    base = carpeta()
    os.makedirs(os.path.join(base, "dias"), exist_ok=True)
    os.makedirs(os.path.join(base, "cuotas"), exist_ok=True)
    hoy = datetime.now(timezone.utc).date()
    hasta = hasta or hoy.isoformat()
    recientes = {(hoy - timedelta(days=k)).strftime("%Y%m%d") for k in range(4)}
    lista = dias(desde, hasta)
    faltan = [d for d in lista if d in recientes or not os.path.exists(os.path.join(base, "dias", f"{d}.json"))]
    print(f"días: {len(lista)} en el rango, {len(faltan)} por pedir")

    def un_dia(d: str) -> int:
        partidos = recortar_dia(_get(URL_DIA.format(d=d)) or {})
        with open(os.path.join(base, "dias", f"{d}.json"), "w") as f:
            json.dump(partidos, f)
        return len(partidos)

    _en_paralelo(faltan, un_dia, hilos, "días")
    partidos = cargar_partidos(base)
    sin = [p["id"] for p in partidos if not os.path.exists(os.path.join(base, "cuotas", f"{p['id']}.json"))]
    print(f"partidos terminados: {len(partidos)}; cuotas por pedir: {len(sin)}")

    def una_cuota(i: int) -> int:
        filas = recortar_cuotas(_get(URL_CUOTAS.format(i=i)) or {})
        with open(os.path.join(base, "cuotas", f"{i}.json"), "w") as f:
            json.dump(filas, f)
        return len(filas)

    _en_paralelo(sin, una_cuota, hilos, "cuotas")
    return {"partidos": len(partidos), "dias": len(lista)}


def _en_paralelo(items: list, fn, hilos: int, rotulo: str):
    if not items:
        return
    hechos, t0 = 0, time.time()
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        futs = {ex.submit(fn, x): x for x in items}
        for fu in as_completed(futs):
            fu.result()
            hechos += 1
            if hechos % 250 == 0 or hechos == len(items):
                print(f"  {rotulo}: {hechos}/{len(items)} ({time.time() - t0:.0f} s)", flush=True)


def cargar_partidos(base: str | None = None) -> list[dict]:
    """Todos los partidos guardados, sin repetidos, ordenados por (fecha, id)."""
    base = base or carpeta()
    vistos: dict[int, dict] = {}
    d = os.path.join(base, "dias")
    for nombre in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        with open(os.path.join(d, nombre)) as f:
            for p in json.load(f):
                vistos[p["id"]] = p
    return sorted(vistos.values(), key=lambda p: (p["fecha"], p["id"]))


def cargar_cuotas(base: str | None = None) -> dict[int, list[dict]]:
    base = base or carpeta()
    d = os.path.join(base, "cuotas")
    out = {}
    for nombre in os.listdir(d) if os.path.isdir(d) else []:
        with open(os.path.join(d, nombre)) as f:
            out[int(nombre.split(".")[0])] = json.load(f)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde", default=INICIO)
    ap.add_argument("--hasta", default=None)
    ap.add_argument("--hilos", type=int, default=4)
    a = ap.parse_args()
    print(bajar(a.desde, a.hasta, a.hilos))


if __name__ == "__main__":
    main()
