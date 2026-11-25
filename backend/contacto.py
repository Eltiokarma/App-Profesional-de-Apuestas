"""CRITERIO DE CONTACTO desde la API (04/11/2026, usuario: «hay que medirlo cada
fin de semana»).

¿Después de 3 fallos seguidos del elegido acertamos más que el promedio? La
pantalla de Simulación lo muestra en vivo (`simulacion.tras_fallos`, campo
`trasFallos`), pero `GET /analisis/simulacion` NO está abierto al token de
Cowork, a propósito (CLAUDE.md). La medición del fin de semana corre en una
sesión con ese token, así que acá se rearman las MISMAS apuestas desde lo que
el token sí lee (los partes, el fixture y sus cuotas) y se pasa por la MISMA
cuenta (`simulacion.simular`). Solo cambia la fuente, no la regla.

Diferencias con la pantalla, declaradas: la hora del depósito es la del primer
depósito del parte (`creadoEn`), no `deposito_previo_en`, que el GET no trae; y
la cuota es la que sirve `/cuotas`, no la media de las casas. La secuencia de
aciertos del criterio depende solo del elegido y del resultado, así que esas
dos no la mueven; pueden mover la banca un poco.

    python -m backend.contacto            # tabla y estado del criterio
    python -m backend.contacto --json     # todo, para guardarlo

Lee `SAD_API_BASE` y `SAD_TOKEN_COWORK` del entorno. 0 tokens de IA, 0 cuota de
API-Football.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend.analisis import semaforo  # noqa: E402
from backend.analisis import simulacion as sim  # noqa: E402
from backend.analisis.escala import es_copa_nacional  # noqa: E402

try:
    from backend.ingesta.extractor import LIGAS_INTERNACIONALES
    _INTERNACIONALES = set(LIGAS_INTERNACIONALES)
except Exception:  # noqa: BLE001 — sin el extractor queda el filtro por nombre de es_copa_nacional
    _INTERNACIONALES = set()

_SEL = {"1": "local", "X": "empate", "2": "visita"}


def armar(datos: dict) -> tuple[list[dict], list[dict]]:
    """{fixtureId: {parte, fx, cuotas}} → (apuestas, excluidos), con los filtros
    de `simulacion.simulacion()`. Sin red: es lo que prueban los tests."""
    desde = sim._utc(sim.DESDE)
    apuestas, excluidos = [], []
    for fid, d in datos.items():
        parte, fx, cuotas = d.get("parte") or {}, d.get("fx") or {}, d.get("cuotas")
        pitazo = sim._utc(fx.get("fecha"))
        if not pitazo or pitazo < desde or not parte or "_error" in parte:
            continue
        partido = {"local": (fx.get("local") or {}).get("nombre", ""),
                   "visita": (fx.get("visitante") or {}).get("nombre", ""), "liga": fx.get("liga") or ""}

        def fuera(motivo: str):
            excluidos.append({"fixtureId": int(fid), "pitazo": pitazo.strftime("%Y-%m-%d %H:%M:%S"),
                              "partido": partido, "motivo": motivo})

        depositado = sim._utc(parte.get("creadoEn"))
        if not depositado or depositado >= pitazo:
            fuera("el parte no se depositó antes del pitazo")
            continue
        if parte.get("cuarentena"):
            fuera("en cuarentena: fuera de toda métrica")
            continue
        if es_copa_nacional(fx.get("ligaId"), fx.get("liga") or "", _INTERNACIONALES):
            fuera(f"copa nacional ({fx.get('liga')}): se analiza, pero no entra a las tablas")
            continue
        probs = (parte.get("pronostico") or {}).get("probabilidades") or {}
        if not sim._normalizar(probs):
            fuera("el pronóstico no trae el 1X2 completo")
            continue
        c = {_SEL[x["seleccion"]]: float(x["cuota"]) for x in (cuotas if isinstance(cuotas, list) else [])
             if x.get("mercado") == "1x2" and x.get("seleccion") in _SEL}
        if len(c) < 3:
            fuera("sin las tres cuotas del 1X2 capturadas")
            continue
        resultado = None
        real = (((parte.get("veredicto") or {}).get("objetivo") or {}).get("unXDos") or {}).get("real")
        if real in sim.CLAVES:
            resultado = real
        elif fx.get("estado") == "finalizado" and fx.get("golesLocal") is not None:
            gl, gv = fx["golesLocal"], fx["golesVisitante"]
            resultado = "local" if gl > gv else "visita" if gv > gl else "empate"
        inv = {k: 1 / v for k, v in c.items()}
        tot = sum(inv.values())
        momento = parte.get("creadoEn")
        apuestas.append({
            "fixtureId": int(fid), "pitazo": pitazo.strftime("%Y-%m-%d %H:%M:%S"), "partido": partido,
            "depositadoEn": momento, "versiones": {s: sim.version_al(s, momento) for s in sim.SKILLS},
            "versionPrompt": parte.get("version") or "", "probabilidades": probs,
            "cuotas": {k: round(c[k], 3) for k in sim.CLAVES},
            "mercado": {k: round(100 * inv[k] / tot, 1) for k in sim.CLAVES}, "resultado": resultado,
            # el semáforo del elegido (11/11/2026) con el 1X2 sin margen de /cuotas
            "semaforo": semaforo.del_parte(parte, {k: 100 * inv[k] / tot for k in sim.CLAVES}),
            # el marcador más probable (13/11/2026): el que el GET del parte calcula con la historia anterior
            "marcador": _marcador(parte, probs),
            # el 1X2 ciego (22/11/2026): el GET del parte lo trae sellado
            "ciego": parte.get("ciego"),
            # el verde sin alertas (24/11/2026): DESCONFIAR (la sellada manda) y el riesgo de la burbuja del elegido
            "desconfiar": bool(((parte.get("desconfianzaSellada") or {}).get("alerta")
                                or (parte.get("desconfianza") or {}).get("alerta") or {}).get("activa")),
            "riesgoElegido": ((parte.get("desconfianza") or {}).get("burbujaElegido") or {}).get("riesgo"),
            # la serie de goles (25/11/2026): /cuotas trae el más/menos 2,5; el nivel de 3 años
            # no viene por la API, así que esa serie no apuesta acá (el contacto mira el 1X2)
            "goles": sim.datos_goles(_goles_casa(cuotas), _total(fx), None),
        })
    return apuestas, excluidos


def _goles_casa(cuotas) -> dict | None:
    ou = {x["seleccion"]: float(x["cuota"]) for x in (cuotas if isinstance(cuotas, list) else [])
          if x.get("mercado") == "ou" and x.get("seleccion") in ("O", "U") and float(x.get("cuota") or 0) > 1}
    if len(ou) < 2:
        return None
    return {"probMas": 100 * (1 / ou["O"]) / (1 / ou["O"] + 1 / ou["U"]), "cuotaMas": ou["O"]}


def _total(fx: dict) -> int | None:
    if fx.get("estado") != "finalizado" or fx.get("golesLocal") is None or fx.get("golesVisitante") is None:
        return None
    return int(fx["golesLocal"]) + int(fx["golesVisitante"])


def _marcador(parte: dict, probs: dict) -> dict | None:
    """El marcador más probable de `lecturaSad.golesAcotados` contra el elegido,
    como lo arma `simulacion.marcador_de`."""
    ga = (parte.get("lecturaSad") or {}).get("golesAcotados") or {}
    mp = (ga.get("masProbables") or [None])[0] if not ga.get("sinDato") else None
    p = sim._normalizar(probs)
    if not mp or not p:
        return None
    signo = semaforo.signo_marcador(mp["marcador"])
    return {"masProbable": mp["marcador"], "prob": mp["prob"], "signo": signo, "alineado": signo == sim._elegido(p)}


def _get(base: str, token: str, ruta: str):
    error = ""
    for _ in range(3):
        try:
            req = urllib.request.Request(base + ruta, headers={"Authorization": "Bearer " + token})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 — se reintenta y, si no, viaja como error del partido
            error = str(e)
    return {"_error": error}


def bajar(base: str, token: str) -> dict:
    """Los partes desde `DESDE`: los que tienen lección (veredicto cerrado) más
    los de las últimas dos semanas (`revisor`), con su fixture y sus cuotas."""
    ids: set[int] = set()
    lec = _get(base, token, "/analisis/cowork/lecciones")
    for it in (lec.get("items") or []) if isinstance(lec, dict) else []:
        if (it.get("fecha") or "") >= sim.DESDE[:10] and it.get("fixtureId"):
            ids.add(int(it["fixtureId"]))
    rev = _get(base, token, "/analisis/cowork/revisor?horas=336")
    for p in (rev.get("partes") or []) if isinstance(rev, dict) else []:
        if (p.get("fecha") or "") >= sim.DESDE[:10] and p.get("fixtureId"):
            ids.add(int(p["fixtureId"]))

    def uno(fid: int):
        return fid, {"parte": _get(base, token, f"/analisis/cowork/{fid}"),
                     "fx": _get(base, token, f"/fixtures/{fid}"), "cuotas": _get(base, token, f"/cuotas/{fid}")}

    with ThreadPoolExecutor(8) as ex:
        return dict(ex.map(uno, sorted(ids)))


def informe(out: dict) -> str:
    tf = out["trasFallos"]
    b, c = tf["base"], tf["contacto"]
    pct = lambda x: "—" if x is None else f"{100 * x:.1f} %"  # noqa: E731
    ic = lambda i: "—" if not i else f"{100 * i[0]:.0f}-{100 * i[1]:.0f} %"  # noqa: E731
    lineas = [f"Criterio de contacto · {out['cerradas']} apuestas cerradas desde {sim.DESDE[:10]}",
              f"  promedio del elegido: {b['aciertos']} de {b['n']} ({pct(b['tasa'])}, IC {ic(b['intervalo'])})"]
    for f in tf["porK"]:
        lineas.append(f"  tras {f['k']} fallo{'s' if f['k'] > 1 else ''} seguido{'s' if f['k'] > 1 else ''}: "
                      f"{f['aciertos']} de {f['n']} ({pct(f['tasa'])}, IC {ic(f['intervalo'])})")
    lineas.append(f"  → {c['texto']}")
    m = next((e for e in out["estrategias"] if e["clave"] == "martingala"), None)
    if m:
        lineas.append(f"  martingala: banca {m['banca']:.2f}, caída máx. {100 * m['caidaMaxima']:.1f} %, "
                      f"apuesta máx. {m['montoMaximo']:.0f} u")
    lineas += ["", informe_ciego(out), "", informe_semaforo(out), "", informe_marcador(out), "", informe_medio(out),
               "", informe_sin_alertas(out)]
    return "\n".join(lineas)


SIN_ALERTAS_SERIES = ("metodoVerde", "metodoVerdeSinAlertas", "metodoVerdeSinAlertasFueraMedio",
                      "martingalaCuidada", "martingalaCuidadaSinAlertas", "ganarFijo", "ganarFijoSinAlertas")


def informe_sin_alertas(out: dict) -> str:
    """La sección «Verde sin alertas» del informe de los lunes (24/11/2026): las
    cuatro series nuevas al lado de las que adaptan, contando SOLO desde
    `SIN_ALERTAS_DESDE` (la regla se armó con los partidos de antes)."""
    desde = sim.SIN_ALERTAS_DESDE
    nombres = {e["clave"]: e["nombre"] for e in out.get("estrategias") or []}
    lineas = [f"Verde sin alertas · cuenta desde {desde[:10]} (antes es la muestra con que se armó la regla)"]
    for clave in SIN_ALERTAS_SERIES:
        if clave not in nombres:
            continue
        n = k = 0
        apostado = ganancia = 0.0
        for a in out.get("apuestas") or []:
            r = (a.get("porEstrategia") or {}).get(clave) or {}
            if a.get("estado") != "cerrada" or str(a.get("pitazo") or "") < desde or not r.get("monto"):
                continue
            n += 1
            k += 1 if a.get("resultado") == r.get("seleccion") else 0
            apostado += r["monto"]
            ganancia += r.get("ganancia") or 0.0
        if n:
            lineas.append(f"  {nombres[clave]}: {k} de {n} ({100 * k / n:.1f} %), apostado {apostado:.2f} u, "
                          f"ganancia {ganancia:+.2f} u ({100 * ganancia / apostado:+.1f} % por unidad)")
        else:
            lineas.append(f"  {nombres[clave]}: sin apuestas cerradas todavía")
    return "\n".join(lineas)


def informe_ciego(out: dict) -> str:
    """La sección «1X2 ciego» del informe de los lunes (22/11/2026): la lectura
    sellada antes de ver la cuota contra la casa, en los mismos partidos."""
    s = out.get("ciego")
    if not s:
        return "1X2 ciego · sin datos"
    pct = lambda x: "—" if x is None else f"{100 * x:.1f} %"  # noqa: E731
    ic = lambda i: "—" if not i else f"{100 * i[0]:.0f}-{100 * i[1]:.0f} %"  # noqa: E731
    lineas = [f"1X2 ciego · cuenta desde {s['desde'][:10]} (sellado antes de ver la cuota; se juzga el acierto)"]
    for nom, k in (("ciego", "ciego"), ("publicado", "publicado"), ("favorito de la casa", "casa")):
        g = s[k]
        lineas.append(f"  {nom}: {g['aciertos']} de {g['n']} ({pct(g['tasa'])}, IC {ic(g['intervalo'])})")
    d = s["desacuerdo"]
    lineas.append(f"  donde el ciego no eligió al favorito de la casa: {d['n']} · ciego {d['ciego']} · "
                  f"casa {d['casa']} · ninguno {d['ninguno']}")
    lineas.append(f"  partidos cerrados sin ciego en el período: {s['sinCiego']}")
    lineas.append(f"  → {s['texto']}")
    # la calibración propia, la misma que lee el analista antes de sellar (24/11/2026)
    from backend.analisis import ciego as _ciego
    e = _ciego.espejo([{"fixtureId": a.get("fixtureId"), "pitazo": a.get("pitazo"), "ciego": a.get("ciego"),
                        "resultado": a.get("resultado")}
                       for a in out.get("apuestas") or [] if a.get("estado") == "cerrada"])
    if e["n"]:
        for titulo, clave in (("lo que el ciego le dio a su elegido → lo que ganó", "calibracion"),
                              ("la lectura del LOCAL (¿gana?) → lo que ganó", "ganaLocal"),
                              ("la lectura del VISITANTE (¿gana?) → lo que ganó", "ganaVisita")):
            lineas.append(f"  calibración propia · {titulo}:")
            for t in e[clave]:
                if t["n"]:
                    lineas.append(f"    {t['tramo']}: {t['n']} partidos · dijo {t['dijo']:g} % → ganó {t['paso']:g} %"
                                  f" (IC {ic(t['intervalo'])})" + (f" · {t['lectura']}" if t["lectura"] else ""))
        if e["cruzadas"]["n"]:
            lineas.append(f"    lecturas cruzadas (sumaron más de 100): {e['cruzadas']['n']} · el elegido ganó "
                          f"{e['cruzadas']['elegidoGano']}")
        em = e["empate"]
        lineas.append(f"    empate: dijo {em['dijo']:g} % → hubo {em['paso']:g} % ({em['empates']} de {em['n']})")
        for a in e["avisos"]:
            lineas.append(f"    ! {a}")
    return "\n".join(lineas)


def informe_semaforo(out: dict) -> str:
    """La sección «Semáforo» del informe de los lunes (11/11/2026)."""
    s = out.get("semaforo")
    if not s:
        return "Semáforo · sin datos"
    pct = lambda x: "—" if x is None else f"{100 * x:.1f} %"  # noqa: E731
    pts = lambda x: "—" if x is None else f"{100 * x:+.1f} pts"  # noqa: E731
    ic = lambda i: "—" if not i else f"{100 * i[0]:.0f}-{100 * i[1]:.0f} %"  # noqa: E731
    lineas = [f"Semáforo · cuenta desde {s['desde'][:10]} (por las espinas: verde = la del elegido lo acompaña; "
              "amarillo = dice empate o la del rival dice que sigue; rojo = la del elegido dice que pierde)"]
    for etiqueta, clave in (("nuevos", "nuevo"), ("todo lo simulado", "todo")):
        g = s[clave]
        lineas.append(f"  {etiqueta}:")
        for nombre, k in (("verdes", "verde"), ("amarillos", "amarillo"), ("rojos", "rojo"), ("sin dato", "sinDato")):
            x = g.get(k)
            if not x:
                continue
            lineas.append(f"    {nombre}: {x['aciertos']} de {x['n']} ({pct(x['tasa'])}, IC {ic(x['intervalo'])}) · "
                          f"la cuota pedía {pct(x['pide'])} · {pts(x['ventaja'])} · ROI plano {pct(x['roiPlano'])}")
    lineas.append(f"  → {s['criterio']['texto']}")
    mv = next((e for e in out.get("estrategias") or [] if e["clave"] == "metodoVerde"), None)
    if mv:
        lineas.append(f"  método solo en verde: banca {mv['banca']:.2f} en {mv['apuestas']} apuestas, "
                      f"caída máx. {100 * mv['caidaMaxima']:.1f} %")
    return "\n".join(lineas)


def informe_marcador(out: dict) -> str:
    """La sección «Marcador» del informe de los lunes (13/11/2026)."""
    s = out.get("marcador")
    if not s:
        return "Marcador · sin datos"
    pct = lambda x: "—" if x is None else f"{100 * x:.1f} %"  # noqa: E731
    lineas = [f"Marcador · cuenta desde {s['desde'][:10]} (el más probable del modelo de goles con el elegido, "
              "contra 1-1, 0-0 o contrario; se juzga el win rate)"]
    for etiqueta, clave in (("nuevos", "nuevo"), ("todo lo simulado", "todo")):
        g = s[clave]
        lineas.append(f"  {etiqueta}: " + " · ".join(
            f"{nom} {g[k]['aciertos']} de {g[k]['n']} ({pct(g[k]['tasa'])})"
            for nom, k in (("alineado", "alineado"), ("resto", "resto"), ("verde y alineado", "verdeAlineado"))))
    lineas.append(f"  → {s['criterio']['texto']}")
    return "\n".join(lineas)


def informe_medio(out: dict) -> str:
    """La sección «Fuera del medio» del informe de los lunes (13/11/2026)."""
    s = out.get("medio")
    if not s:
        return "Fuera del medio · sin datos"
    pct = lambda x: "—" if x is None else f"{100 * x:.1f} %"  # noqa: E731
    pts = lambda x: "—" if x is None else f"{100 * x:+.1f} pts"  # noqa: E731
    lineas = [f"Fuera del medio · cuenta desde {s['desde'][:10]} (medio = la casa le da al elegido "
              f"{s['medio'][0]:g}-{s['medio'][1]:g} %)"]
    for etiqueta, clave in (("nuevos", "nuevo"), ("todo lo simulado", "todo")):
        g = s[clave]
        lineas.append(f"  {etiqueta}:")
        for nom, k in (("punta baja", "puntaBaja"), ("medio", "medio"), ("punta alta", "puntaAlta"), ("puntas", "puntas")):
            x = g[k]
            lineas.append(f"    {nom}: {x['aciertos']} de {x['n']} ({pct(x['tasa'])}) · pedía {pct(x['pide'])} · "
                          f"{pts(x['ventaja'])} · plana {pct(x['roiPlano'])}")
    lineas.append(f"  → {s['criterio']['texto']}")
    e = next((x for x in out.get("estrategias") or [] if x["clave"] == "metodoFueraMedio"), None)
    if e:
        lineas.append(f"  método fuera del medio: banca {e['banca']:.2f} en {e['apuestas']} apuestas "
                      f"({e['ganadas']} ganadas), caída máx. {100 * e['caidaMaxima']:.1f} %")
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--json", action="store_true", help="imprime todo en JSON")
    a = ap.parse_args(argv)
    base = os.environ.get("SAD_API_BASE", "").rstrip("/")
    token = os.environ.get("SAD_TOKEN_COWORK") or os.environ.get("SAD_API_TOKEN") or ""
    if not base:
        print("falta SAD_API_BASE", file=sys.stderr)
        return 2
    apuestas, excluidos = armar(bajar(base, token))
    out = sim.simular(apuestas)
    out["excluidos"] = excluidos
    if a.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(informe(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
