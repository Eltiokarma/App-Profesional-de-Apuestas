"""Diagnóstico de integridad de sad.db: ¿dónde hay huecos de ingesta?

Detecta la firma de un hueco sin gastar requests: partidos que siguen NS/TBD
con la fecha ya vencida (nadie volvió a pedir ese día — típico del desfase de
temporadas cruzadas: en mayo de 2026 la Premier va por la temporada API 2025 y
la ventana vieja, que pedía por liga con SEASON=2026, no la veía). Con --api
además contrasta un día contra el feed real de API-Football (1 request) y
lista los partidos que faltan por completo en la DB.

Uso (junto a sad.db, o --db ruta):
  python -m backend.ingesta.diagnostico                     # resumen general
  python -m backend.ingesta.diagnostico --dia 2026-05-31    # radiografía de un día
  python -m backend.ingesta.diagnostico --dia 2026-05-31 --api  # + contraste con la API

Para RELLENAR un día detectado (cualquier temporada):
  python -m backend.ingesta.extractor --desde 2026-05-31 --hasta 2026-05-31 --solo fixtures
(la autocuración `sanar fechas` del extractor hace esto sola en cada corrida)
"""
import argparse
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone

from .extractor import LIGAS, Cliente, fechas_zombi, leer_clave

JUGADO = ("FT", "AET", "PEN")
ZOMBI = ("NS", "TBD")


def resumen(con: sqlite3.Connection) -> int:
    """Visión general: fechas pasadas con zombis y torneos aún abiertos."""
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fechas = fechas_zombi(con, hoy, horizonte_dias=3650)
    total_zombis = sum(c for _, c in fechas)
    print(f"Fechas pasadas con partidos NS/TBD (zombis): {len(fechas)} días · {total_zombis} partidos")
    for fecha, c in fechas[:30]:
        ligas = [
            f"{LIGAS.get(lid, lid)} ({n})"
            for lid, n in con.execute(
                """SELECT league_id, COUNT(*) FROM fixtures
                   WHERE status_short IN ('NS','TBD') AND substr(date,1,10)=?
                   GROUP BY league_id ORDER BY COUNT(*) DESC""",
                (fecha,),
            )
        ]
        print(f"  {fecha}: {c} zombis → {', '.join(ligas[:6])}{' …' if len(ligas) > 6 else ''}")
    if len(fechas) > 30:
        print(f"  … y {len(fechas) - 30} días más (usa --dia para inspeccionar uno)")

    abiertos = con.execute(
        """SELECT league_id, league_season, COUNT(*), MIN(substr(date,1,10)), MAX(substr(date,1,10))
           FROM fixtures
           WHERE status_short IN ('NS','TBD') AND substr(date,1,10) < ?
             AND league_id IS NOT NULL AND league_season IS NOT NULL
           GROUP BY league_id, league_season ORDER BY COUNT(*) DESC""",
        (hoy,),
    ).fetchall()
    if abiertos:
        print(f"\nTorneos con tramo congelado (candidatos a re-barrido del backfill): {len(abiertos)}")
        for lid, temp, c, desde, hasta in abiertos:
            print(f"  {LIGAS.get(lid, f'liga {lid}')} · temporada {temp}: {c} zombis entre {desde} y {hasta}")
    else:
        print("\nSin torneos congelados: no hay NS/TBD con fecha vencida.")
    return 0 if not fechas else 1


def dia(con: sqlite3.Connection, fecha: str) -> int:
    """Radiografía de un día: qué tiene la DB por liga y qué huele a hueco."""
    filas = con.execute(
        """SELECT f.league_id, f.league_season, f.status_short,
                  th.name, ta.name, f.goals_home, f.goals_away
           FROM fixtures f
           LEFT JOIN teams th ON th.id = f.home_team_id
           LEFT JOIN teams ta ON ta.id = f.away_team_id
           WHERE substr(f.date,1,10) = ? ORDER BY f.league_id, f.date""",
        (fecha,),
    ).fetchall()
    por_liga: dict[int, list] = defaultdict(list)
    for fila in filas:
        por_liga[fila[0]].append(fila)
    print(f"{fecha}: {len(filas)} partidos en la DB · {len(por_liga)} ligas")
    zombis = 0
    for lid in sorted(por_liga, key=lambda x: (x not in LIGAS, x)):
        partidos = por_liga[lid]
        estados = defaultdict(int)
        for p in partidos:
            estados[p[2]] += 1
        marca = "" if lid in LIGAS else " (fuera de la lista)"
        print(f"\n  {LIGAS.get(lid, f'liga {lid}')}{marca} · temporada {partidos[0][1]} · "
              + " ".join(f"{k}={v}" for k, v in sorted(estados.items())))
        for _, _, st, home, away, gh, ga in partidos:
            res = f"{gh}-{ga}" if gh is not None else "—"
            aviso = "  ⚠ sin resultado (zombi)" if st in ZOMBI else ""
            zombis += 1 if st in ZOMBI else 0
            print(f"    [{st}] {home} vs {away}  {res}{aviso}")
    ausentes = sorted(set(LIGAS) - set(por_liga))
    if ausentes:
        print(f"\nLigas de la lista SIN ningún partido ese día ({len(ausentes)}): "
              + ", ".join(LIGAS[l] for l in ausentes))
        print("(puede ser legítimo — no toda liga juega cada día; --api lo confirma contra el feed real)")
    if zombis:
        print(f"\n⚠ {zombis} partidos sin resultado con fecha vencida. Para rellenar:")
        print(f"  python -m backend.ingesta.extractor --desde {fecha} --hasta {fecha} --solo fixtures")
    return 0 if not zombis else 1


def dia_api(con: sqlite3.Connection, fecha: str) -> int:
    """Contraste del día contra API-Football: lo que el feed real tiene de
    nuestras ligas vs lo que hay en la DB (1 request, más si pagina)."""
    try:
        cliente = Cliente(leer_clave())
    except SystemExit as e:
        print(f"--api no disponible: {e}", file=sys.stderr)
        return 2
    filas = cliente.paginado("fixtures", {"date": fecha})
    nuestras = [it for it in filas if (it.get("league") or {}).get("id") in LIGAS]
    en_db = {
        fid: (st, gh, ga)
        for fid, st, gh, ga in con.execute(
            "SELECT id, status_short, goals_home, goals_away FROM fixtures "
            "WHERE substr(date,1,10) = ?", (fecha,),
        )
    }
    faltan, desactualizados = [], []
    for it in nuestras:
        f = it.get("fixture", {})
        fid = f.get("id")
        st_api = (f.get("status") or {}).get("short")
        goles = it.get("goals", {})
        etiqueta = (f"{LIGAS.get(it['league']['id'])}: "
                    f"{(it.get('teams', {}).get('home') or {}).get('name')} vs "
                    f"{(it.get('teams', {}).get('away') or {}).get('name')} "
                    f"[{st_api}] {goles.get('home')}-{goles.get('away')}")
        if fid not in en_db:
            faltan.append(etiqueta)
        elif en_db[fid][0] != st_api or en_db[fid][1] != goles.get("home"):
            desactualizados.append(f"{etiqueta}  (DB: [{en_db[fid][0]}] {en_db[fid][1]}-{en_db[fid][2]})")
    print(f"\nContraste con la API ({fecha}): feed del día {len(filas)} partidos, "
          f"{len(nuestras)} de nuestras ligas · en DB {len(en_db)}")
    if faltan:
        print(f"\n✗ FALTAN en la DB ({len(faltan)}):")
        for linea in faltan:
            print(f"  {linea}")
    if desactualizados:
        print(f"\n✗ DESACTUALIZADOS en la DB ({len(desactualizados)}):")
        for linea in desactualizados:
            print(f"  {linea}")
    if not faltan and not desactualizados:
        print("✓ la DB coincide con el feed del día para nuestras ligas")
    else:
        print(f"\nPara rellenar: python -m backend.ingesta.extractor "
              f"--desde {fecha} --hasta {fecha} --solo fixtures")
    return 1 if (faltan or desactualizados) else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Diagnóstico de huecos de ingesta en sad.db")
    ap.add_argument("--db", default="sad.db", help="ruta a sad.db")
    ap.add_argument("--dia", metavar="YYYY-MM-DD", help="radiografía de un día concreto")
    ap.add_argument("--api", action="store_true",
                    help="con --dia: contrastar el día contra API-Football (gasta 1 request)")
    args = ap.parse_args()
    if not os.path.exists(args.db):
        print(f"No existe {args.db}", file=sys.stderr)
        return 2
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA busy_timeout=15000")
    try:
        if args.dia:
            codigo = dia(con, args.dia)
            if args.api:
                codigo = max(codigo, dia_api(con, args.dia))
            return codigo
        return resumen(con)
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
