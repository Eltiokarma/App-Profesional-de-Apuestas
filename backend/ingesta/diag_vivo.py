"""Por qué un partido NO tiene cuotas en juego — diagnóstico puerta por puerta.

El ciclo en vivo tiene varias puertas y todas tienen que abrirse: liga seguida,
partido dentro de la ventana, presupuesto disponible, el partido en el feed
live, la API con cobertura de odds live de esa liga, y los nombres de mercado
mapeados por cuota_key. Cuando la ficha dice "sin cobertura de cuotas en vivo
en esta liga", esto dice CUÁL de las puertas se quedó cerrada.

Sin red por defecto (solo lee sad.db). Con --api gasta 3-4 requests para
distinguir lo único que no se puede saber desde la DB: si la API ofrece o no
cuotas en juego de esa liga.

    python -m backend.ingesta.diag_vivo --fixture 1234567
    python -m backend.ingesta.diag_vivo --hoy
    python -m backend.ingesta.diag_vivo --fixture 1234567 --api
"""
import argparse
import contextlib
import io
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

from backend.ingesta.en_vivo import (
    EN_JUEGO,
    PREVIOS,
    TOPE_LIGAS_LIVE,
    VENTANA_JUEGO_MIN,
    VENTANA_PREVIA_MIN,
)
from backend.ingesta.extractor import (
    CUOTA_PATH,
    LIGAS,
    LIGAS_MENORES,
    Cliente,
    leer_clave,
    ligas_vivo,
)

OK, NO, DUDA = "OK  ", "FALLA", "?   "


def fecha(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def tabla_existe(con: sqlite3.Connection, nombre: str) -> bool:
    return bool(con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (nombre,)).fetchone())


def cuota_diaria() -> str:
    """El marcador de presupuesto que comparten todas las corridas: si estaba
    agotado a la hora del partido, el ciclo en vivo no hizo ni una request."""
    try:
        with open(CUOTA_PATH, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return f"sin {CUOTA_PATH} (o no se corre desde la raíz de datos)"
    linea = (f"día {d.get('dia')} · usadas {d.get('usadas')} de "
             f"{d.get('limite_api') or '?'} del plan")
    por = d.get("usadas_por")
    if isinstance(por, dict) and por:
        # el desglose acumulado del día: QUIÉN se está comiendo el plan
        top = sorted(por.items(), key=lambda kv: -kv[1])[:8]
        linea += "\n      consumo del día: " + " · ".join(f"{k}={v}" for k, v in top)
    return linea


def diagnosticar(con: sqlite3.Connection, fid: int, cliente=None) -> None:
    f = con.execute(
        """SELECT f.id, f.date, f.status_short, f.status_long, f.elapsed, f.league_id,
                  f.goals_home, f.goals_away, l.name, h.name, a.name
           FROM fixtures f
           LEFT JOIN leagues l ON l.id = f.league_id
           LEFT JOIN teams h ON h.id = f.home_team_id
           LEFT JOIN teams a ON a.id = f.away_team_id
           WHERE f.id = ?""", (fid,)).fetchone()
    if not f:
        print(f"{NO} el fixture {fid} no está en sad.db (la ingesta nunca lo bajó)")
        return
    _, date, ss, sl, elapsed, lid, gh, ga, liga, local, visita = f
    ahora = datetime.now(timezone.utc)
    dt = fecha(date)
    hace = (ahora - dt).total_seconds() / 60 if dt else None
    print(f"\n=== {local} vs {visita} · {liga or lid} · fixture {fid} ===")
    print(f"    {date} UTC" + (f" (hace {hace:.0f} min)" if hace is not None else "")
          + f" · estado {ss}/{sl} · marcador {gh}-{ga}" + (f" · minuto {elapsed}" if elapsed else ""))

    # 1. la liga: ¿seguida? ¿importante o menor?
    if lid not in LIGAS:
        print(f"{NO} liga {lid} FUERA de la lista LIGAS: no se ingesta nada de ella")
        return
    if lid in LIGAS_MENORES:
        print(f"{NO} liga {lid} marcada como MENOR: por diseño no recibe ciclo en vivo "
              f"(quítala de SAD_LIGAS_MENORES si quieres sus cuotas en juego)")
        return
    print(f"{OK} liga {lid} ({LIGAS[lid]}) está en el ciclo en vivo")
    if len(ligas_vivo()) > TOPE_LIGAS_LIVE:
        print(f"{OK} {len(ligas_vivo())} ligas en vivo > {TOPE_LIGAS_LIVE}: el ciclo pide "
              f"live=all y filtra local (ninguna liga puede caerse del filtro)")

    # 2. la ventana: ¿este partido llegó a ser candidato del ciclo?
    if ss in EN_JUEGO:
        print(f"{OK} estado {ss}: candidato mientras siga así")
    elif ss in PREVIOS:
        print(f"{OK} estado {ss}: candidato entre {VENTANA_PREVIA_MIN} min antes y "
              f"{VENTANA_JUEGO_MIN} min después del saque")
    elif hace is not None and -VENTANA_PREVIA_MIN <= hace <= VENTANA_JUEGO_MIN:
        print(f"{DUDA} estado {ss}: ahora mismo NO es candidato, pero su hora sí está en ventana")
    else:
        print(f"{OK} estado {ss}: partido cerrado, su ventana en vivo ya pasó")

    # 3. ¿el ciclo llegó a PREGUNTAR por esta liga? (la rotación con tope de
    #    ligas por ciclo va por esta marca; sin ella, "sin cobertura" puede
    #    significar simplemente "nunca le tocó turno")
    if tabla_existe(con, "odds_live_consultas"):
        cols = {f[1] for f in con.execute("PRAGMA table_info(odds_live_consultas)")}
        extra = ", estado, items, nuestros, ajenos" if "estado" in cols else ""
        fila = con.execute(
            f"SELECT consultada_en, con_datos{extra} FROM odds_live_consultas WHERE league_id=?",
            (lid,)).fetchone()
        if fila and extra:
            estado, items, nuestros, ajenos = fila[2], fila[3], fila[4], fila[5]
            print(f"{OK if estado == 'ok' else DUDA} última consulta /odds/live?league={lid}: "
                  f"{fila[0]} UTC · estado {estado} "
                  f"({items} items, {nuestros} nuestros, {ajenos} de otra liga)")
            print("    " + {
                "ok": "la liga sí devuelve cuotas en juego",
                "vacia": "el feed vino VACÍO. Es lo más parecido a falta de cobertura, "
                         "pero un feed vacío puntual no lo prueba: míralo varias rondas",
                "ajena": f"el feed trajo partidos pero NINGUNO nuestro. Si `ajenos` > 0, el "
                         f"filtro ?league={lid} no está filtrando y estamos leyendo el feed "
                         f"global paginado — NO es falta de cobertura",
                "fallo": "la consulta se CAYÓ (red, HTTP, errors de la API o presupuesto). "
                         "No dice nada sobre la cobertura de la liga",
            }.get(estado, "estado desconocido"))
        elif fila:
            print(f"{OK if fila[1] else DUDA} última consulta /odds/live?league={lid}: "
                  f"{fila[0]} UTC · {'trajo datos' if fila[1] else 'sin datos'} "
                  f"(DB vieja: sin columna `estado`, no se puede saber por qué)")
        else:
            print(f"{DUDA} el ciclo nunca ha consultado /odds/live de esta liga "
                  f"(no le ha tocado turno con partido vivo, o el ciclo no corre)")

    # 4. lo que quedó guardado
    if not tabla_existe(con, "odds_live"):
        print(f"{NO} no existe la tabla odds_live: el ciclo en vivo nunca corrió en esta DB")
    else:
        filas = con.execute(
            "SELECT COUNT(*), MIN(captured_at), MAX(captured_at), MIN(minuto), MAX(minuto), "
            "COUNT(DISTINCT captured_at), SUM(suspendida) FROM odds_live WHERE fixture_id=?",
            (fid,)).fetchone()
        n, primera, ultima, min0, min1, capturas, susp = filas
        if n:
            print(f"{OK} odds_live: {n} valores en {capturas} capturas "
                  f"({primera} → {ultima}), minutos {min0}-{min1}, {susp or 0} suspendidas")
            mapeadas = mercados_mapeados(con, fid)
            if mapeadas:
                print(f"{OK} cuota_key mapea {mapeadas} de esas filas a mercados del contrato")
            else:
                print(f"{NO} NINGUNA fila mapea a un mercado del contrato: hay datos pero la "
                      f"ficha se ve vacía. Faltan aliases en cuota_key (backend/app.py)")
                nombres = con.execute(
                    "SELECT DISTINCT bet_name FROM odds_live WHERE fixture_id=? LIMIT 8", (fid,)
                ).fetchall()
                print(f"      nombres que llegaron: {[x[0] for x in nombres]}")
        else:
            print(f"{NO} odds_live: 0 filas para este partido")
            hubo = con.execute(
                "SELECT COUNT(*), MIN(captured_at), MAX(captured_at) FROM odds_live "
                "WHERE captured_at >= ? AND captured_at <= ?",
                ((dt - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S") if dt else "",
                 (dt + timedelta(minutes=VENTANA_JUEGO_MIN)).strftime("%Y-%m-%d %H:%M:%S") if dt else "")
            ).fetchone() if dt else (0, None, None)
            if hubo and hubo[0]:
                print(f"      pero el ciclo SÍ capturó {hubo[0]} valores de OTROS partidos "
                      f"mientras este se jugaba ({hubo[1]} → {hubo[2]}): el ciclo corría; "
                      f"lo que falló es la cobertura de ESTA liga")
            else:
                print(f"      y tampoco capturó nada de ningún partido en esa franja: el ciclo "
                      f"no corrió (SAD_LIVE_SEGUNDOS apagado, deploy viejo o presupuesto agotado)")

    # 5. prepartido, para separar "no hay cuotas de nada" de "solo faltan las live"
    for tabla in ("odds", "odds_history"):
        if tabla_existe(con, tabla):
            n = con.execute(f"SELECT COUNT(*) FROM {tabla} WHERE fixture_id=?", (fid,)).fetchone()[0]
            print(f"{OK if n else NO} {tabla} (prepartido): {n} filas")

    print(f"    presupuesto: {cuota_diaria()}")

    # 6. lo único que no se puede saber desde la DB: si la API ofrece odds live
    #    de esta liga, por liga Y por fixture. 3-4 requests, solo con --api.
    if cliente is not None:
        data = cliente.get("fixtures", {"live": "all"})
        vivos = {(it.get("fixture") or {}).get("id") for it in (data or {}).get("response", [])}
        print(f"{OK if fid in vivos else DUDA} /fixtures?live=all: {len(vivos)} partidos en juego "
              f"en el mundo; este {'SÍ' if fid in vivos else 'NO'} aparece")
        filas = cliente.paginado("odds/live", {"league": lid}, tope_paginas=3)
        ids = {(it.get("fixture") or {}).get("id") for it in filas}
        ligas_resp = sorted({(it.get("league") or {}).get("id") for it in filas} - {None})
        if not filas:
            print(f"{NO} /odds/live?league={lid}: la API no devuelve NADA para esta liga ahora "
                  f"mismo. Si se repite ronda tras ronda con partidos en juego, ahí sí es "
                  f"falta de cobertura (bájala a SAD_LIGAS_MENORES y ahorra requests)")
        else:
            print(f"{OK} /odds/live?league={lid}: {len(filas)} items, fixtures {sorted(x for x in ids if x)}")
            print(f"    este partido {'SÍ' if fid in ids else 'NO'} está en ese feed")
            print(f"    ligas EN LA RESPUESTA: {ligas_resp}")
            if ligas_resp and lid not in ligas_resp:
                print(f"{NO} el filtro ?league={lid} NO está filtrando: la API devolvió otras "
                      f"ligas. Eso explica el 'sin cobertura' sin que falte cobertura — y es "
                      f"justo lo que cubre el rescate por fixture (SAD_LIVE_ODDS_FIXTURES)")
        # la prueba decisiva: preguntar por el partido, sin depender del filtro
        directo = cliente.paginado("odds/live", {"fixture": fid}, tope_paginas=1)
        n_val = sum(len(b.get("values") or []) for it in directo for b in (it.get("odds") or []))
        if directo:
            print(f"{OK} /odds/live?fixture={fid}: {len(directo)} items y {n_val} cuotas. "
                  f"HAY cobertura para este partido — si por liga no llegaba, el problema "
                  f"es el feed por liga, no la API")
        else:
            print(f"{NO} /odds/live?fixture={fid}: tampoco por fixture hay cuotas. Aquí sí "
                  f"apunta a cobertura real (o a mercado cerrado en este momento)")
        print(f"    requests gastadas: {cliente.usadas}")


def mercados_mapeados(con: sqlite3.Connection, fid: int) -> int:
    """Cuántas filas de odds_live entiende el backend (cuota_key). Con 0, la
    ficha se ve igual de vacía que sin datos."""
    try:
        # importar backend.app imprime su banner de programación: fuera del informe
        with contextlib.redirect_stdout(io.StringIO()):
            from backend.app import cuota_key
    except Exception:
        return -1
    n = 0
    for bet, valor in con.execute(
            "SELECT bet_name, value FROM odds_live WHERE fixture_id=?", (fid,)):
        if cuota_key(bet, valor):
            n += 1
    return n


def de_hoy(con: sqlite3.Connection) -> list[int]:
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    marcas = ",".join("?" * len(ligas_vivo()))
    return [r[0] for r in con.execute(
        f"SELECT id FROM fixtures WHERE substr(date,1,10)=? AND league_id IN ({marcas}) "
        f"ORDER BY date", (hoy, *sorted(ligas_vivo())))]


def main() -> int:
    ap = argparse.ArgumentParser(description="Por qué un partido no tiene cuotas en juego")
    ap.add_argument("--db", default="sad.db")
    ap.add_argument("--fixture", type=int, action="append", default=[],
                    help="id del fixture (repetible)")
    ap.add_argument("--hoy", action="store_true", help="todos los de hoy de las ligas en vivo")
    ap.add_argument("--api", action="store_true",
                    help="3-4 requests: ¿está en el feed live? ¿la API da odds live por liga? ¿y por fixture?")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"No existe {args.db}", file=sys.stderr)
        return 1
    con = sqlite3.connect(args.db)
    ids = list(args.fixture)
    if args.hoy:
        ids += de_hoy(con)
    if not ids:
        print("hoy no hay partidos de las ligas del ciclo en vivo en sad.db"
              if args.hoy else "Nada que diagnosticar: pasa --fixture ID o --hoy",
              file=sys.stderr)
        return 1

    cliente = Cliente(leer_clave()) if args.api else None
    for fid in dict.fromkeys(ids):
        diagnosticar(con, fid, cliente)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
