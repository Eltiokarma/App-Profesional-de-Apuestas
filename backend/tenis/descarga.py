"""Tenis · fase 0 · descarga de partidos (docs/TENIS_FASE0.md).

Fuente: la API pública de ESPN, sin clave (los datasets de Sackmann y
tennis-data.co.uk no se alcanzan desde el contenedor). Un pedido al
scoreboard trae los torneos en juego ese día con TODO su cuadro de singles
(principal y qualy), así que alcanza con pedir cada 3 días. Solo marcadores:
las burbujas no usan cuotas.

Guarda en `$SAD_TENIS_DIR` (por defecto ./tenis_data, fuera de git):
  dias/{circuito}-AAAAMMDD.json   partidos recortados de ese pedido
Retomable: lo que ya está en disco no se vuelve a pedir (salvo lo reciente).

    python -m backend.tenis.descarga                 # 2016 → hoy, ATP y WTA
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone

from backend.nba.descarga import _en_paralelo, _get

URL = "https://site.api.espn.com/apis/site/v2/sports/tennis/{circuito}/scoreboard?dates={d}"
CIRCUITOS = ("atp", "wta")
CUADROS = {"Men's Singles": "ATP", "Women's Singles": "WTA"}
INICIO = "2016-01-01"
PASO_DIAS = 3


def carpeta() -> str:
    return os.environ.get("SAD_TENIS_DIR", "tenis_data")


def _juegos(c: dict) -> list[int]:
    out = []
    for t in c.get("competitors", []):
        try:
            out.append(int(sum(float(x.get("value") or 0) for x in t.get("linescores", []))))
        except (TypeError, ValueError):
            out.append(0)
    return out


def recortar(crudo: dict) -> list[dict]:
    """Partidos de singles TERMINADOS en cancha. Afuera los walkover (no se
    jugó) y los retiros (el partido no terminó: no es momentum de nadie).
    `ganador`/`perdedor` con sus juegos; si el ganador hizo menos juegos que
    el perdedor (6-7 7-6 7-6 puede dar 20-19 o al revés), se le pone uno más:
    el motor necesita que el margen tenga el signo del resultado."""
    out = []
    for ev in crudo.get("events", []):
        for g in ev.get("groupings", []):
            tour = CUADROS.get((g.get("grouping") or {}).get("displayName"))
            if not tour:
                continue
            for c in g.get("competitions", []):
                st = (c.get("status") or {}).get("type") or {}
                if st.get("name") != "STATUS_FINAL" or not st.get("completed"):
                    continue
                comp = c.get("competitors", [])
                if len(comp) != 2:
                    continue
                ganador = [t for t in comp if t.get("winner")]
                if len(ganador) != 1:
                    continue
                juegos = dict(zip((t.get("id") for t in comp), _juegos(c)))
                w = ganador[0]
                l = comp[0] if comp[1] is w else comp[1]
                gw, gl = juegos.get(w.get("id"), 0), juegos.get(l.get("id"), 0)
                if gw + gl == 0:
                    continue
                if gw <= gl:
                    gw = gl + 1
                ronda = (c.get("round") or {}).get("displayName") or ""
                out.append({"id": int(c["id"]), "fecha": c.get("date") or c.get("startDate"),
                            "tour": tour, "torneo": ev.get("name"), "torneoId": ev.get("id"),
                            "grandSlam": bool(ev.get("major")), "ronda": ronda, "qualy": "qualif" in ronda.lower(),
                            "ganadorId": int(w["id"]), "ganador": (w.get("athlete") or {}).get("displayName"),
                            "perdedorId": int(l["id"]), "perdedor": (l.get("athlete") or {}).get("displayName"),
                            "juegosGanador": gw, "juegosPerdedor": gl,
                            "sets": len(w.get("linescores", []))})
    return out


def bajar(desde: str = INICIO, hasta: str | None = None, hilos: int = 6) -> int:
    base = os.path.join(carpeta(), "dias")
    os.makedirs(base, exist_ok=True)
    hoy = datetime.now(timezone.utc).date()
    fin = date.fromisoformat(hasta) if hasta else hoy
    d, pedidos = date.fromisoformat(desde), []
    while d <= fin:
        for c in CIRCUITOS:
            pedidos.append((c, d.strftime("%Y%m%d")))
        d += timedelta(days=PASO_DIAS)
    recientes = {(hoy - timedelta(days=k)).strftime("%Y%m%d") for k in range(10)}
    faltan = [(c, x) for c, x in pedidos if x in recientes or not os.path.exists(os.path.join(base, f"{c}-{x}.json"))]
    print(f"pedidos: {len(pedidos)}, por pedir {len(faltan)}", flush=True)

    def uno(par):
        c, x = par
        filas = recortar(_get(URL.format(circuito=c, d=x)) or {})
        with open(os.path.join(base, f"{c}-{x}.json"), "w") as f:
            json.dump(filas, f)
        return len(filas)

    _en_paralelo(faltan, uno, hilos, "pedidos")
    return len(cargar())


def cargar() -> list[dict]:
    """Todos los partidos, sin repetidos (el mismo torneo sale en varios
    pedidos), ordenados por (fecha, id)."""
    base = os.path.join(carpeta(), "dias")
    vistos = {}
    for n in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        with open(os.path.join(base, n)) as f:
            for p in json.load(f):
                vistos[p["id"]] = p
    return sorted((p for p in vistos.values() if p.get("fecha")), key=lambda p: (p["fecha"], p["id"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde", default=INICIO)
    ap.add_argument("--hasta", default=None)
    ap.add_argument("--hilos", type=int, default=6)
    a = ap.parse_args()
    print({"partidos": bajar(a.desde, a.hasta, a.hilos)})


if __name__ == "__main__":
    main()
