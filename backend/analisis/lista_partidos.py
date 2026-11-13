"""LA LECTURA EN LA LISTA DE PARTIDOS (13/11/2026, usuario: «tendría que estar
al costado del semáforo… se deberían de ver los dos marcadores más probables,
tres si nos da el tamaño»).

Dos cosas por partido con parte, calculadas, para la tarjeta de Partidos:

- **desconfiar**: la alerta de confianza del elegido, con la MISMA regla que
  la tira del parte y la Simulación (`simulacion.alerta_confianza`:
  SOBRE-LA-CASA y BURBUJA-DE-UN-PARTIDO) y la misma burbuja del elegido «al
  día del partido» (`simulacion._burbuja_elegido`). Lleva la lectura que
  restringe («X no gana: Y o empate») de `desconfianza.leer`. No mueve el 1X2.
- **marcadores**: los tres marcadores más probables del modelo de goles
  calibrado (`goles.acotar_fixture`, REVENTON §17), con su probabilidad. Es
  lectura del marcador, no una señal de apuesta; `porVentana` avisa cuando el
  nivel que entra a los goles sale de una ventana poco fiable.

Nada de esto es el semáforo: el semáforo sigue fuera de la vista del analista
(`semaforo.py`); la alerta ya va en su parte y los marcadores salen de la base.
Este endpoint igual nace denegado para el token de Cowork (no lo necesita).
"""
from __future__ import annotations

import json
import time

CLAVES = ("local", "empate", "visita")
N_MARCADORES = 3
# los goles acotados de un partido usan la historia ESTRICTAMENTE anterior: no
# cambian salvo que se rellene un partido viejo. Media hora de caché por proceso
# basta para que la lista no los rehaga en cada visita.
GOLES_TTL_S = 1800
_GOLES: dict[int, tuple[float, dict | None]] = {}


def _marcadores(fx) -> dict | None:
    """Los N más probables del modelo de goles, o None si no hay dato."""
    hit = _GOLES.get(fx["id"])
    if hit and time.monotonic() - hit[0] < GOLES_TTL_S:
        return hit[1]
    try:
        from backend.analisis import goles
        g = goles.acotar_fixture(dict(fx))
    except Exception:  # noqa: BLE001 — sin goles acotados la tarjeta no muestra marcadores; la lista sigue
        g = None
    out = None
    if g and not g.get("sinDato") and g.get("masProbables"):
        out = {"masProbables": g["masProbables"][:N_MARCADORES], "porVentana": bool(g.get("porVentana"))}
    _GOLES[fx["id"]] = (time.monotonic(), out)
    return out


def _desconfiar(fx, parte: dict, mercado: dict | None) -> dict | None:
    """La alerta del elegido con la regla del parte; None sin 1X2 completo."""
    from backend.analisis import desconfianza
    from backend.analisis.simulacion import _burbuja_elegido, _elegido, _normalizar
    pron = parte.get("pronostico") or {}
    p = _normalizar(pron.get("probabilidades") or {})
    if not p:
        return None
    e = _elegido(p)
    burb = _burbuja_elegido(fx, e)
    lado = {"local": "a", "visita": "b"}.get(e)
    reventon = ({lado: {"actual": {"signo": burb.get("signo"), "partidos": burb.get("partidos")},
                        "riesgo": {"nivel": burb.get("riesgo")}}} if burb and lado else None)
    nombres = {"a": fx["home_name"], "b": fx["away_name"]}
    bloque = desconfianza.leer(pron, mercado, reventon, nombres)
    if not bloque:
        return None
    do = bloque.get("dobleOportunidad") or {}
    return {"activa": bool(bloque["alerta"]["activa"]), "motivos": bloque["alerta"]["motivos"],
            "elegido": e, "lectura": do.get("texto") if bloque["alerta"]["activa"] else None}


def de_partidos(ids) -> dict[int, dict]:
    """{fixtureId: {desconfiar, marcadores}} de los partidos con parte."""
    from backend import db as saddb
    from backend.analisis.lecciones import cuotas_mercado
    from backend.analisis.parte import _conectar
    ids = sorted({int(i) for i in ids})[:300]
    if not ids:
        return {}
    marcas = ",".join("?" * len(ids))
    with _conectar() as con:
        filas = con.execute(f"SELECT fixture_id, parte_json FROM parte_cowork WHERE fixture_id IN ({marcas})",
                            tuple(ids)).fetchall()
    if not filas:
        return {}
    con_parte = [f["fixture_id"] for f in filas]
    fxs = {r["id"]: r for r in saddb.query(
        "sad",
        "SELECT f.id, f.date, f.home_team_id, f.away_team_id, f.league_id, "
        "ht.name AS home_name, at.name AS away_name FROM fixtures f "
        "JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        f"WHERE f.id IN ({','.join('?' * len(con_parte))})", tuple(con_parte))}
    mercados = cuotas_mercado(con_parte)
    out = {}
    for f in filas:
        fx = fxs.get(f["fixture_id"])
        if not fx:
            continue
        try:
            parte = json.loads(f["parte_json"])
        except (TypeError, ValueError):
            continue
        m = mercados.get(f["fixture_id"])
        mercado = {k: m["prob"][k] for k in CLAVES} if m else None
        try:
            desc = _desconfiar(fx, parte, mercado)
        except Exception:  # noqa: BLE001 — sin la alerta la tarjeta no la pinta; los marcadores siguen
            desc = None
        out[f["fixture_id"]] = {"desconfiar": desc, "marcadores": _marcadores(fx)}
    return out
