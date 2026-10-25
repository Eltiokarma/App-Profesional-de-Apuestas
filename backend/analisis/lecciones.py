"""Fase C del bucle de aprendizaje: las lecciones, acumuladas por skill.

Ver `docs/APRENDIZAJE.md`. El veredicto (fase B) ya deja una lección por lado
dentro del parte; acá se indexan, se cuentan y se les pone un estado.

DOS DECISIONES QUE EXPLICAN TODO EL MÓDULO:

1. **El contenido de la lección NO se copia a ninguna tabla.** Se deriva del
   veredicto al leer, igual que el marcador y el timeline. El diseño original
   proponía una tabla `lecciones` con el texto adentro; eso crea dos copias del
   mismo dato y una se queda vieja el día que alguien corrige un veredicto —sin
   que nadie se entere, que es la peor forma—. Acá lo único que se guarda es lo
   que NO se puede derivar: el estado.

2. **Las métricas salen solo de la población acreditable** (`ciega` + `PRE`).
   Las otras se cuentan aparte y no se suman nunca. Y cada lección viaja con
   `puedeMoverNumeros`: una lección de un caso contaminado puede FIJAR RÚBRICA
   —aclarar cómo se aplica una regla— pero no mueve un peso. Esa distinción la
   lleva el dato, no el criterio de quien lea el dossier ese día.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import threading
import time

from backend.analisis import db as efedb, veredicto as vered

ESTADOS = ("pendiente", "en_revision", "aplicada", "descartada")
# fase D: cuántos fallos con lección pendiente del MISMO skill abren la revisión.
# Abrir la revisión no autoriza nada: solo la abre (docs/APRENDIZAJE.md § D).
DISPARADOR_REVISION = 4

DDL = """
CREATE TABLE IF NOT EXISTS leccion_estado (
    clave TEXT PRIMARY KEY,          -- fixtureId:lado
    estado TEXT NOT NULL DEFAULT 'pendiente',
    aplicada_en TEXT,                -- versión del skill donde entró
    nota TEXT,
    actualizado_en TEXT NOT NULL
);
"""


def _conectar():
    con = efedb.conectar()
    con.executescript(DDL)
    return con


def _estados() -> dict[str, dict]:
    with _conectar() as con:
        filas = con.execute("SELECT * FROM leccion_estado").fetchall()
    return {f["clave"]: dict(f) for f in filas}


def _casos(limite: int = 400, ids=None) -> list[dict]:
    """Los partes con veredicto, con su parte y su juicio ya cargados.

    `ids` acota a esos fixtures: los antecedentes de un partido miran los
    partes de DOS equipos y armaban el inventario entero (cada caso con su
    chequeo de DT contra las alineaciones) para quedarse con cinco; con doce
    agentes a la vez el GET tardaba de 30 s a más de 2 min (11/10/2026)."""
    from backend.analisis.parte import _conectar as conectar_parte

    from backend.analisis.parte import cohorte_de, dias_movido, dt_equivocado, sin_dt

    if ids is not None and not ids:
        return []
    filtro, params = "", ()
    if ids is not None:
        ids = sorted({int(i) for i in ids})
        filtro = f" AND fixture_id IN ({','.join('?' * len(ids))})"
        params = tuple(ids)
    with conectar_parte() as con:
        filas = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b, parte_json, veredicto_json, "
            "cohorte, cuarentena_json, modo_fallo_json, banco_desmentido_json FROM parte_cowork "
            "WHERE veredicto_json IS NOT NULL"
            + filtro + " ORDER BY fecha DESC LIMIT ?", (*params, limite)).fetchall()
    # la fecha REAL de cada partido, para el parte escrito para otra fecha
    fecha_real: dict[int, str] = {}
    if filas:
        try:
            from backend import db as saddb
            ids_f = [f["fixture_id"] for f in filas]
            for r in saddb.query("sad", f"SELECT id, date FROM fixtures WHERE id IN ({','.join('?' * len(ids_f))})",
                                 tuple(ids_f)):
                fecha_real[r["id"]] = str(r["date"] or "")
        except Exception:  # noqa: BLE001 — sin la base de partidos no se juzga
            fecha_real = {}
    fuera = []
    for f in filas:
        parte = json.loads(f["parte_json"])
        cuarentena = json.loads(f["cuarentena_json"]) if f["cuarentena_json"] else None
        # UN PARTE PARA OTRA FECHA TAMPOCO (incidencia 371, Millonarios–Once
        # Caldas: depositado para el 14/10, jugado el 20/10 sin rehacerse). Se
        # escribió con otra semana de datos: no calibra nada.
        movido = dias_movido(f["fecha"], fecha_real.get(f["fixture_id"]))
        if movido is not None and not cuarentena:
            cuarentena = {"motivo": f"automática: el parte es del partido del {f['fecha']} y se jugó el "
                                    f"{fecha_real[f['fixture_id']][:10]} ({movido:+d} días) sin rehacerse",
                          "automatica": True, "puestaEn": "", "veredictoAlPoner": None, "parteDeOtraFecha": movido}
        # SIN DT NO HAY CASO. El bloque A, F3 y S1 se apoyan en la continuidad
        # del entrenador; un parte con «sin establecer» en un lado se hizo sin
        # ese insumo y no calibra nada. Cuarentena automática, por criterio.
        lados_sin = sin_dt(parte)
        if lados_sin and not cuarentena:
            cuarentena = {"motivo": "automática: sin DT declarado (lado " + ", ".join(lados_sin) + ")",
                          "automatica": True, "puestaEn": "", "veredictoAlPoner": None}
        # DT EQUIVOCADO TAMPOCO. El parte nombró a un DT y en el banco se sentó
        # otro (la alineación rancia del 22/09: Santa Fe–Cali, la Roma). Es el
        # mismo criterio de insumo —qué traía el parte antes del pitazo—,
        # comprobado contra la alineación de ese partido cuando la hay.
        # …salvo los lados donde el usuario probó que el banco de la API es el
        # que está mal (parte.desmentir_banco): esos ya no se comparan
        desmentidos = json.loads(f["banco_desmentido_json"]) if f["banco_desmentido_json"] else {}
        disputados = []
        if not cuarentena:
            todos = dt_equivocado(parte, f["fixture_id"], desmentidos)
            # los `disputados` (el parte contradijo a la base con la prensa) se
            # ven en el item pero no apartan el caso
            disputados = [m for m in todos if m.get("disputado")]
            malos = [m for m in todos if not m.get("disputado")]
            if malos:
                cuarentena = {"motivo": "automática: DT del parte distinto del que dirigió el partido ("
                                        + " · ".join(f"lado {m['lado']}: parte «{m['parte']}», banco «{m['banco']}»"
                                                     for m in malos) + ")",
                              "automatica": True, "puestaEn": "", "veredictoAlPoner": None,
                              "dtEquivocado": malos}
        fuera.append({
            "fixtureId": f["fixture_id"], "fecha": (f["fecha"] or "")[:10],
            "equipoA": f["equipo_a"], "equipoB": f["equipo_b"],
            "parte": parte,
            "veredicto": json.loads(f["veredicto_json"]),
            "cohorte": cohorte_de(f["cohorte"])["clave"],
            "cuarentena": cuarentena,
            "modoFallo": json.loads(f["modo_fallo_json"]) if f["modo_fallo_json"] else None,
            "dtDisputado": disputados,
        })
    return fuera


def _items_de(caso: dict, estados: dict) -> list[dict]:
    v = caso["veredicto"]
    seleccion = v.get("seleccion", "")
    modo = v.get("modoEvaluacion", "")
    acredita = bool(v.get("acredita", vered.acredita(seleccion, modo)))
    fuera = []
    for lado in ("a", "b"):
        lv = (v.get("porLado") or {}).get(lado)
        if not lv:
            continue
        propio = caso["equipoA"] if lado == "a" else caso["equipoB"]
        rival = caso["equipoB"] if lado == "a" else caso["equipoA"]
        mf_lado = ((caso.get("modoFallo") or {}).get("lados") or {}).get(lado) or {}
        # la primera lección conserva su clave de siempre (`fixture:lado`, con
        # su estado guardado); las siguientes son `fixture:lado:2`, `:3`…
        # La etiqueta de Jev se selló sobre la PRIMERA: las otras van sin ella.
        candidatas = [(f"{caso['fixtureId']}:{lado}", lv, mf_lado, 1)]
        candidatas += [(f"{caso['fixtureId']}:{lado}:{i}", {**o, "veredicto": lv.get("veredicto", "")}, {}, i)
                       for i, o in enumerate(lv.get("otrasLecciones") or [], start=2)]
        for clave, lx, mf, orden in candidatas:
            item = _item(caso, lado, clave, lx, mf, orden, propio, rival, estados,
                         seleccion, modo, acredita, v)
            if item:
                fuera.append(item)
    return fuera


def _item(caso, lado, clave, lv, mf, orden, propio, rival, estados, seleccion, modo, acredita, v) -> dict | None:
    leccion = (lv.get("leccion") or "").strip()
    if not leccion:
        return None   # sin lección no hay nada que acumular: el veredicto ya está en el parte
    st = estados.get(clave) or {}
    return {
        "clave": clave,
        "orden": orden,
        "fixtureId": caso["fixtureId"], "lado": lado,
        # LA ETIQUETA DE JEV (backend/analisis/modo_fallo.py): de qué
        # naturaleza fue el fallo y si la lección pide mover un número.
        # Sellada al cerrar el caso; None = sin clave, sin confianza o
        # cerrado antes de que existiera. No entra en ninguna métrica.
        "modoFallo": mf.get("modo"),
        "modoFalloConfianza": mf.get("modoConfianza"),
        "proponeMoverNumero": mf.get("proponeMoverNumero"),
        "equipo": propio, "rival": rival,
        "partido": f"{caso['equipoA']} vs {caso['equipoB']}",
        "fecha": caso["fecha"],
        "skill": (lv.get("skill") or "").strip(),
        "veredicto": lv.get("veredicto", ""),
        "queP": lv.get("queP", ""),
        "leccion": leccion,
        "reglaTocada": (lv.get("reglaTocada") or "").strip(),
        "seleccion": seleccion, "modoEvaluacion": modo, "acredita": acredita,
        "mancha": v.get("mancha", ""),
        "cohorte": caso.get("cohorte", ""),
        "cuarentena": (caso.get("cuarentena") or {}).get("motivo", "") if caso.get("cuarentena") else "",
        "cuarentenaAutomatica": bool((caso.get("cuarentena") or {}).get("automatica")),
        # por qué lado y con qué nombres saltó la automática por DT: es lo que
        # el usuario desmiente cuando el banco de la API es el equivocado
        "dtEquivocado": (caso.get("cuarentena") or {}).get("dtEquivocado") or [],
        # el parte contradijo a la base con la prensa y el banco de la API no le
        # da la razón: no aparta el caso, pero queda a la vista para revisarlo
        "dtDisputado": caso.get("dtDisputado") or [],
        # LA DISTINCIÓN QUE EL DOSSIER NO PUEDE DEJAR AL CRITERIO DEL DÍA:
        # un caso contaminado enseña, pero no mueve un número. Uno en
        # cuarentena ni siquiera enseña: su insumo estaba roto.
        "puedeMoverNumeros": acredita and not caso.get("cuarentena"),
        "queAutoriza": ("en cuarentena: no cuenta ni fija rúbrica" if caso.get("cuarentena") else
                        "puede sostener un cambio de peso" if acredita else
                        "solo fija rúbrica: aclara cómo se aplica una regla, "
                        "no mueve ningún número"),
        "estado": st.get("estado") or "pendiente",
        "aplicadaEn": st.get("aplicada_en") or "",
        "nota": st.get("nota") or "",
        "actualizadoEn": st.get("actualizado_en") or "",
    }


def _sumar_tarjeta(tar: dict, lado: str, e: dict) -> None:
    """Un lado del veredicto a la calibración de la tarjeta: por fuerza, por
    tipo (general · local · visita), por nivel, y el analista contra ella."""
    t = e.get("tarjeta")
    if not t:
        return
    tipo = "general" if t.get("guia") != "condicion" else ("local" if lado == "a" else "visita")
    for acc in (tar["porFuerza"][t["fuerza"]], tar["porTipo"][tipo][t["fuerza"]],
                tar["porNivel"].setdefault(t.get("nivel") or "?", {"lados": 0, "aciertos": 0})):
        acc["lados"] += 1
        acc["aciertos"] += 1 if t.get("cumplida") else 0
    if e.get("vsTarjeta") == "sigue":
        tar["sigue"]["lados"] += 1
        tar["sigue"]["aciertos"] += 1 if e.get("cumplida") else 0
    elif e.get("vsTarjeta") == "contra":
        tar["contra"]["lados"] += 1
        tar["contra"]["aciertaAnalista"] += 1 if e.get("cumplida") else 0
        tar["contra"]["aciertaTarjeta"] += 1 if t.get("cumplida") else 0


# EL OBJETIVO DE CADA VEREDICTO, POR UNOS MINUTOS. Se recalcula al leer (no hay
# copia que se quede vieja), pero Aprendizaje lo pide para ~250 casos a la vez
# y la pantalla lanza dos pedidos juntos: 21 s cada uno y la web cortaba
# («signal is aborted without reason», 20/10/2026). La clave lleva el parte
# entero (con su veredicto): corregir un caso cambia la clave y se rehace; lo
# que cambia por fuera (la constante del partido, la ficha) entra en ≤ TTL.
# El candado hace que el segundo pedido espere al primero y lea lo guardado.
OBJETIVO_TTL_S = float(os.environ.get("SAD_CACHE_OBJETIVO_S", "600") or "0")
_OBJ_CACHE: dict[tuple, tuple[float, dict]] = {}
_OBJ_LOCK = threading.Lock()


def _objetivo(fixture_id: int, parte: dict) -> dict:
    if OBJETIVO_TTL_S <= 0:
        return vered.objetivo(fixture_id, parte)
    clave = (fixture_id, hashlib.sha1(json.dumps(parte, sort_keys=True, default=str).encode()).hexdigest())
    with _OBJ_LOCK:
        hit = _OBJ_CACHE.get(clave)
        if hit and time.monotonic() - hit[0] < OBJETIVO_TTL_S:
            return hit[1]
        obj = vered.objetivo(fixture_id, parte)
        if len(_OBJ_CACHE) > 3000:
            _OBJ_CACHE.clear()
        _OBJ_CACHE[clave] = (time.monotonic(), obj)
        return obj


def _metricas(casos: list[dict]) -> tuple[dict, dict]:
    """Población por separado, y las métricas SOLO de lo acreditable.

    Un caso en cuarentena se cuenta en su propia población y NO entra en
    ninguna métrica: la etiqueta ciega describe cuánto se sabía del
    resultado, la cuarentena describe que el insumo estaba roto."""
    poblacion = {s: {"casos": 0, "lados": 0} for s in vered.SELECCIONES}
    poblacion["cuarentena"] = {"casos": 0, "lados": 0}
    acred = {"acierto": 0, "parcial": 0, "fallo": 0}
    casos_acred, briers, reales, con_reparto = 0, [], [], 0
    unxdos_ok, unxdos_de = 0, 0
    tde_obs, tde_positivos, tde_sin_ficha, tde_contaminadas = 0, 0, 0, 0
    reloj_obs, reloj_positivos = 0, 0
    rev = _reventon_vacio()
    espina = {e: {"lados": 0, "aciertos": 0} for e in ("positiva", "cero", "negativa", "neutra")}
    movimientos = {m: 0 for m in ("positiva", "cero", "negativa")}
    # la misma cuenta por guía (K total o K de la condición): la que lee mejor
    # se ve aparte, cada una contra la frecuencia de SUS lados
    por_guia = {g: ({e: {"lados": 0, "aciertos": 0} for e in espina}, {m: 0 for m in movimientos})
                for g in ("total", "condicion")}
    # la espina de la TARJETA y el analista contra ella (19/10/2026)
    tar = {"porFuerza": {f: {"lados": 0, "aciertos": 0} for f in ("fuerte", "debil")},
           # la tarjeta GENERAL (K total) o la de la condición que leyó el parte:
           # local para el lado a, visita para el b (19/10/2026, pedido del usuario)
           "porTipo": {t: {f: {"lados": 0, "aciertos": 0} for f in ("fuerte", "debil")}
                       for t in ("general", "local", "visita")},
           "porNivel": {}, "sigue": {"lados": 0, "aciertos": 0},
           "contra": {"lados": 0, "aciertaAnalista": 0, "aciertaTarjeta": 0},
           # las dos tarjetas del partido, como un 1X2 (Monza 4-0 Cagliari)
           "partido": {"concuerdan": {"lados": 0, "aciertos": 0},
                       "concuerdanDebiles": {"lados": 0, "aciertos": 0},
                       "discrepan": {"lados": 0, "aciertaA": 0, "aciertaB": 0},
                       "unaSola": {"lados": 0, "aciertos": 0}}}

    for caso in casos:
        v = caso["veredicto"]
        sel = v.get("seleccion", "")
        lados = [l for l in ("a", "b") if (v.get("porLado") or {}).get(l)]
        if caso.get("cuarentena"):
            poblacion["cuarentena"]["casos"] += 1
            poblacion["cuarentena"]["lados"] += len(lados)
            continue
        if sel in poblacion:
            poblacion[sel]["casos"] += 1
            poblacion[sel]["lados"] += len(lados)
        if not v.get("acredita"):
            continue
        casos_acred += 1
        for l in lados:
            ver = ((v.get("porLado") or {})[l]).get("veredicto", "")
            if ver in acred:
                acred[ver] += 1
        obj = _objetivo(caso["fixtureId"], caso["parte"])
        if not obj.get("jugado"):
            continue
        ux = obj.get("unXDos") or {}
        if ux.get("declarado"):
            unxdos_de += 1
            unxdos_ok += 1 if ux.get("acerto") else 0
        br = (obj.get("brier") or {}).get("valor")
        if br is not None and ux.get("real"):
            briers.append(br)
            reales.append(ux["real"])
            con_reparto += 1
        # la ventana del TDE: lo único del skill que se comprueba solo
        for b in (obj.get("tde") or {}).get("bloques") or []:
            # la serie del RELOJ (sesgo tardío, TDE 44c/45): la base sola, también
            # cuando se cobró la de la rama (incidencia 367)
            r = b.get("reloj") if b.get("ventanaDeRama") else b
            if r and r.get("golEnVentana") is not None and r.get("cobrable") is not False:
                reloj_obs += 1
                reloj_positivos += 1 if r["golEnVentana"] else 0
            if b.get("golEnVentana") is None:
                tde_sin_ficha += 1
                continue
            # una ventana con roja antes del gol no puso a prueba el mecanismo
            # declarado (disciplina 24): no cuenta ni a favor ni en contra
            if b.get("cobrable") is False:
                tde_contaminadas += 1
                continue
            tde_obs += 1
            tde_positivos += 1 if b["golEnVentana"] else 0
        _acumular_reventon(rev, obj.get("reventon") or {}, ux, br)
        tp = obj.get("tarjetas") or {}
        if tp.get("estado") == "concuerdan":
            for k in ("concuerdan",) + (("concuerdanDebiles",) if tp.get("ambasDebiles") else ()):
                tar["partido"][k]["lados"] += 1
                tar["partido"][k]["aciertos"] += 1 if tp.get("cumplida") else 0
        elif tp.get("estado") == "discrepan":
            d = tar["partido"]["discrepan"]
            d["lados"] += 1
            d["aciertaA"] += 1 if tp.get("aciertaA") else 0
            d["aciertaB"] += 1 if tp.get("aciertaB") else 0
        elif tp.get("estado") == "una sola":
            tar["partido"]["unaSola"]["lados"] += 1
            tar["partido"]["unaSola"]["aciertos"] += 1 if tp.get("cumplida") else 0
        for lado in ("a", "b"):
            e = (obj.get("espina") or {}).get(lado) or {}
            _sumar_tarjeta(tar, lado, e)
            if e.get("lectura") in espina:
                g_acc, g_mov = por_guia.get(e.get("guia") or "total", por_guia["total"])
                for acc, mov in ((espina, movimientos), (g_acc, g_mov)):
                    c = acc[e["lectura"]]
                    c["lados"] += 1
                    c["aciertos"] += 1 if e.get("cumplida") else 0
                    if e.get("movimiento") in mov:
                        mov[e["movimiento"]] += 1

    total_lados = sum(acred.values())
    decididos = acred["acierto"] + acred["fallo"] + acred["parcial"]
    metricas = {
        "criterio": "ciega + PRE: la única combinación que acredita validación predictiva",
        "casos": casos_acred,
        "lados": total_lados,
        "veredictos": acred,
        "tasaAcierto": round(acred["acierto"] / decididos, 3) if decididos else None,
        "tasaNota": ("" if decididos else
                     "sin lados acreditables cerrados no hay tasa: no es 0%, es que no hay n"),
        "unXDos": {"aciertos": unxdos_ok, "de": unxdos_de,
                   "tasa": round(unxdos_ok / unxdos_de, 3) if unxdos_de else None},
        "brier": _brier_con_linea_base(briers, reales),
        "ventanaTde": {
            "observadas": tde_obs, "conGol": tde_positivos,
            "sinFicha": tde_sin_ficha, "conRojaAntes": tde_contaminadas,
            "reloj": {"observadas": reloj_obs, "conGol": reloj_positivos,
                      "nota": "la ventana BASE del reloj, también cuando se cobró la de la rama: "
                              "la serie del sesgo tardío (TDE 44c y 45)"},
            "nota": "ventanas del TDE comprobadas contra los goles recibidos, en población "
                    "ciega. `sinFicha` no cuenta como no ocurrido: no se pudo comprobar",
        },
        "reventon": _cerrar_reventon(rev),
        "espina": {**_cerrar_espina(espina, movimientos),
                   "porGuia": {g: _cerrar_espina(*por_guia[g]) for g in por_guia},
                   "tarjeta": _cerrar_tarjeta(tar)},
    }
    return poblacion, metricas


def _tasa(c: dict, clave: str = "aciertos") -> dict:
    n = c["lados"]
    ic = intervalo_wilson(c[clave], n)
    return {"lados": n, "aciertos": c[clave], "tasa": round(c[clave] / n, 3) if n else None,
            "intervalo": list(ic) if ic else None}


def _cerrar_tarjeta(tar: dict) -> dict:
    """La espina de la tarjeta sola, por fuerza y por nivel de riesgo, y el
    analista contra ella: cuando la contradice, ¿quién acierta? Es la
    calibración que el analista lee antes de escribir su espina."""
    c = tar["contra"]
    cero = {"lados": 0, "aciertos": 0}
    pt = tar.get("partido") or {"concuerdan": cero, "concuerdanDebiles": cero, "unaSola": cero,
                                "discrepan": {"lados": 0, "aciertaA": 0, "aciertaB": 0}}
    return {
        "porFuerza": {f: _tasa(v) for f, v in tar["porFuerza"].items()},
        "porNivel": {n: _tasa(v) for n, v in tar["porNivel"].items()},
        # general (K total) · local · visita (la K de la condición que leyó el
        # parte), cada una entera y por fuerza: ¿la específica acierta más?
        "porTipo": {tipo: {"todas": _tasa({"lados": sum(c["lados"] for c in fz.values()),
                                           "aciertos": sum(c["aciertos"] for c in fz.values())}),
                           **{f: _tasa(c) for f, c in fz.items()}}
                    for tipo, fz in (tar.get("porTipo") or {}).items()},
        "analistaLaSigue": _tasa(tar["sigue"]),
        # por PARTIDO (los «lados» son partidos): las dos tarjetas como un 1X2.
        # Lo que se compara es «concuerdan» contra cada tarjeta sola (porFuerza)
        "partido": {"concuerdan": _tasa(pt["concuerdan"]),
                    "concuerdanDebiles": _tasa(pt["concuerdanDebiles"]),
                    "unaSola": _tasa(pt["unaSola"]),
                    "discrepan": pt["discrepan"],
                    "nota": ("partidos: el resultado que da cada tarjeta (a: positiva→local, cero→empate, "
                             "negativa→visita; b al revés). «concuerdan» = las dos dicen lo mismo; si acierta "
                             "más que una tarjeta sola, la segunda confirma a la primera (Monza 4-0 Cagliari)")},
        "analistaVaContra": {"lados": c["lados"], "aciertaAnalista": c["aciertaAnalista"],
                             "aciertaTarjeta": c["aciertaTarjeta"],
                             "lectura": ("sin n" if c["lados"] < REVENTON_N_MINIMO else
                                         "el analista le gana a la tarjeta cuando la contradice"
                                         if c["aciertaAnalista"] > c["aciertaTarjeta"] else
                                         "la tarjeta le gana al analista cuando él la contradice"
                                         if c["aciertaTarjeta"] > c["aciertaAnalista"] else "empate")},
        "nota": ("espina de la TARJETA = el movimiento más probable de la guía calibrada (fuerte con ≥ 50 %); "
                 "el analista la sigue o va contra ella leyendo los skills. Esto dice cuál de las dos acierta "
                 "más, en población ciega"),
    }


def _cerrar_espina(acc: dict, movimientos: dict) -> dict:
    """¿La lectura de la K acierta más que la frecuencia de cada movimiento?
    Decir «positiva» en todos los partidos acierta lo que ganan los equipos (~37 %
    por lado): la lectura vale si su tasa, con intervalo de Wilson, queda por
    ENCIMA de esa frecuencia. Con pocos lados se dice."""
    total = sum(movimientos.values())
    out = {}
    for lectura, c in acc.items():
        n = c["lados"]
        base = round(movimientos[lectura] / total, 3) if total and lectura in movimientos else None
        ic = intervalo_wilson(c["aciertos"], n)
        out[lectura] = {"lados": n, "aciertos": c["aciertos"],
                        "tasa": round(c["aciertos"] / n, 3) if n else None,
                        "intervalo": list(ic) if ic else None,
                        "frecuenciaDelMovimiento": base,
                        "sobreLaFrecuencia": (None if n < REVENTON_N_MINIMO or base is None or not ic
                                              else ic[0] > base)}
    juzgadas = [l for l in ("positiva", "cero", "negativa") if out[l]["lados"] >= REVENTON_N_MINIMO]
    lectura = ("sin n" if not juzgadas else
               "acierta más que la frecuencia" if any(out[l]["sobreLaFrecuencia"] for l in juzgadas) else
               "no supera la frecuencia todavía")
    return {**out, "lectura": lectura, "nMinimo": REVENTON_N_MINIMO, "lados": total,
            "nota": "lados ciegos con espina: adónde dijo el analista que iba la K total y adónde fue. "
                    "Vale si la tasa de una lectura, con intervalo, queda por encima de la frecuencia de "
                    "ese movimiento entre todos los lados con espina"}


# ── el reventón en producción, contra el backtest ───────────────────────────
#
# El backtest (docs/REVENTON.md §8) calibró los puntos del riesgo sobre 171k
# burbujas históricas y dejó una tasa de reventón por nivel. Eso responde «¿los
# pesos son razonables en general?». Esto responde lo otro: en los partidos que
# SÍ se analizaron y se cerraron a ciegas, ¿las burbujas de riesgo alto
# reventaron más que las de riesgo bajo, y en la proporción que el backtest
# decía? Un nivel cuya tasa en producción se sale del rango del backtest con n
# suficiente es lo único que autoriza a abrir la revisión de los puntos —y
# abrirla, no moverlos: la app nunca mueve un peso por su cuenta—.

NIVELES_RIESGO = ("bajo", "medio", "alto", "muy alto", "sin base")
REVENTON_N_MINIMO = 10   # por nivel, para que la comparación con el backtest diga algo


GRUPOS_RESPETO = ("aFavor", "enContra", "neutro")


def _reventon_vacio() -> dict:
    return {"porNivel": {n: {"observadas": 0, "reventadas": 0} for n in NIVELES_RIESGO},
            "extremo": {"observadas": 0, "reventadas": 0},
            "sinBurbuja": 0, "noComprobables": 0,
            # SOLO con riesgo alto o muy alto: ¿el 1X2 siguió la racha o no, y
            # cómo le fue? Es la pregunta que decide si el riesgo vale algo
            # para el pronóstico o solo lo decora (docs/REVENTON.md §11)
            "respeto": {g: {"lados": 0, "reventadas": 0, "aciertos1x2": 0, "briers": []}
                        for g in GRUPOS_RESPETO}}


def _acumular_reventon(acc: dict, reventon: dict, unxdos: dict | None = None,
                       brier: float | None = None) -> None:
    for lado in ("a", "b"):
        r = reventon.get(lado) or {}
        if not r:
            continue
        if r.get("sinBurbuja"):
            acc["sinBurbuja"] += 1
            continue
        if not r.get("comprobable") or not r.get("observado"):
            acc["noComprobables"] += 1
            continue
        nivel = ((r.get("declarado") or {}).get("riesgo") or {}).get("nivel") or "sin base"
        celda = acc["porNivel"].setdefault(nivel, {"observadas": 0, "reventadas": 0})
        celda["observadas"] += 1
        celda["reventadas"] += 1 if r["observado"].get("revento") else 0
        if (r.get("declarado") or {}).get("extremo"):
            acc["extremo"]["observadas"] += 1
            acc["extremo"]["reventadas"] += 1 if r["observado"].get("revento") else 0
        # el respeto se juzga solo con riesgo alto/muy alto (None = no aplica)
        grupo = r.get("pronosticoVsRacha")
        if r.get("respetoRiesgo") is not None and grupo in acc["respeto"]:
            cel = acc["respeto"][grupo]
            cel["lados"] += 1
            cel["reventadas"] += 1 if r["observado"].get("revento") else 0
            if unxdos and unxdos.get("declarado"):
                cel["aciertos1x2"] += 1 if unxdos.get("acerto") else 0
            if brier is not None:
                cel["briers"].append(float(brier))


def intervalo_wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalo de Wilson al 95 % para una proporción k/n. Con n chico el
    punto engaña: 6 de 21 (29 %) contra un backtest de 42-47 % parece FUERA, y
    el intervalo [14 %, 50 %] dice que es ruido. Se compara el RANGO del
    backtest con el intervalo, no con el punto."""
    if n <= 0:
        return None
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    medio = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(max(0.0, centro - medio), 3), round(min(1.0, centro + medio), 3))


def _cerrar_reventon(acc: dict) -> dict:
    from backend.analisis.burbuja import TASA_BACKTEST, TASA_BASE_BACKTEST
    por_nivel = {}
    for nivel, c in acc["porNivel"].items():
        n, k = c["observadas"], c["reventadas"]
        tasa = round(k / n, 3) if n else None
        esperado = TASA_BACKTEST.get(nivel)
        intervalo = intervalo_wilson(k, n)
        dentro = None
        lectura = "sin n" if n < REVENTON_N_MINIMO else ("sin base en el backtest" if not esperado else "")
        if tasa is not None and esperado and n >= REVENTON_N_MINIMO and intervalo:
            # FUERA solo si el rango del backtest y el intervalo no se tocan
            dentro = not (intervalo[1] < esperado[0] or intervalo[0] > esperado[1])
            lectura = "compatible" if dentro else "fuera"
        por_nivel[nivel] = {
            "observadas": n, "reventadas": k, "tasa": tasa,
            "intervalo": list(intervalo) if intervalo else None,
            "esperadoBacktest": list(esperado) if esperado else None,
            "dentroDelBacktest": dentro,
            "lectura": lectura,
            "nMinimo": REVENTON_N_MINIMO,
        }
    obs = sum(c["observadas"] for c in acc["porNivel"].values())
    revs = sum(c["reventadas"] for c in acc["porNivel"].values())
    fuera = [n for n, c in por_nivel.items() if c["dentroDelBacktest"] is False]
    respeto = {}
    for g, c in (acc.get("respeto") or {}).items():
        n = c["lados"]
        respeto[g] = {
            "lados": n,
            "reventadas": c["reventadas"],
            "tasaReventon": round(c["reventadas"] / n, 3) if n else None,
            "aciertos1x2": c["aciertos1x2"],
            "tasa1x2": round(c["aciertos1x2"] / n, 3) if n else None,
            "brierMedio": round(sum(c["briers"]) / len(c["briers"]), 3) if c["briers"] else None,
        }
    return {
        "observadas": obs, "reventadas": revs,
        "respetoRiesgo": {
            **respeto,
            "nota": "solo lados con riesgo alto o muy alto antes del partido: si el 1X2 declarado "
                    "apostó a que la racha sigue (aFavor), se corta (enContra) o al empate (neutro), "
                    "y cómo le fue a cada grupo. Un Brier peor en aFavor que en enContra es la "
                    "evidencia de que el riesgo vale para el pronóstico; igual, de que solo lo decora",
        },
        "tasa": round(revs / obs, 3) if obs else None,
        "tasaBaseBacktest": TASA_BASE_BACKTEST,
        "porNivel": por_nivel,
        "extremo": {**acc["extremo"],
                    "nota": "burbujas con alerta K-EXTREMO declarada antes del partido: el backtest "
                            "dice que la K no adelanta el reventón; esto lo mira en producción"},
        "sinBurbuja": acc["sinBurbuja"],
        "noComprobables": acc["noComprobables"],
        "fueraDelBacktest": fuera,
        "revisionAbierta": bool(fuera),
        "nota": ("por lado, en población ciega: la burbuja total tal como estaba antes del partido "
                 "y si ese partido la reventó. La tasa por nivel se compara con la del backtest "
                 f"(docs/REVENTON.md §8) solo con n ≥ {REVENTON_N_MINIMO}, y por INTERVALO (Wilson 95 %), "
                 "no por el punto: FUERA es que el rango del backtest no toca el intervalo. Un nivel "
                 "fuera ABRE la revisión de los puntos, no los mueve. `sinBurbuja` y `noComprobables` no "
                 "cuentan: no había nada que reventar o el pipeline no calculó el partido"),
    }


def _brier_con_linea_base(briers: list[float], reales: list[str]) -> dict:
    """UN BRIER SIN LÍNEA DE BASE NO DICE NADA (docs/APRENDIZAJE.md).

    La línea de base es el predictor constante que reparte según la frecuencia
    OBSERVADA en esta misma muestra: es lo que habría sacado alguien que no mira
    el partido. Un Brier mejor que eso es información; peor, es ruido caro.
    """
    n = len(briers)
    if not n:
        return {"media": None, "n": 0, "lineaBase": None,
                "nota": "sin casos ciegos con reparto 1X2 declarado no hay Brier que publicar",
                "escala": "0 perfecto · 2 máximo · TRES resultados (no comparable con un Brier binario)"}
    frec = {k: reales.count(k) / n for k in ("local", "empate", "visita")}
    base = sum(sum((frec[k] - (1.0 if k == r else 0.0)) ** 2
                   for k in ("local", "empate", "visita")) for r in reales) / n
    media = sum(briers) / n
    return {
        "media": round(media, 4), "n": n,
        "lineaBase": round(base, 4),
        "mejorQueLaBase": bool(media < base),
        "nota": "la línea de base es el reparto constante con la frecuencia observada de "
                "esta misma muestra: lo que sacaría quien no mira el partido",
        "escala": "0 perfecto · 2 máximo · TRES resultados (no comparable con un Brier binario)",
    }


def _liston(skill: str, metricas: dict) -> dict | None:
    """Lo que el propio skill pide antes de que sus números se puedan tocar."""
    if skill != "teorema-del-echado":
        return None
    from backend.analisis import tde as tdemod
    obs = metricas["ventanaTde"]
    return {
        "de": "el skill teorema-del-echado (ALTA_DEL_SEMAFORO)",
        "condiciones": tdemod.ALTA_DEL_SEMAFORO,
        "observadoAca": f"{obs['conGol']} ventanas con gol de {obs['observadas']} comprobadas "
                        f"en población ciega",
        "semaforo": f"{obs['conGol']} echada(s) observada(s) en ciego · el skill pide 5",
        "cumple": obs["conGol"] >= 5,
        "nota": "este conteo es de NUESTRA base y es independiente del registro del skill "
                "(n=8, 1 positivo): no se suman, se comparan",
    }


def _por_modo_fallo(items: list[dict]) -> dict:
    """Los fallos y parciales agrupados por la etiqueta de Jev, más la alarma
    del dossier: lecciones que piden mover un número y no pueden sostenerlo."""
    from backend.analisis.modo_fallo import MODOS
    # un lado fallado es UN fallo aunque deje varias lecciones: se cuenta la primera
    con_fallo = [i for i in items if i["veredicto"] in ("fallo", "parcial") and i.get("orden", 1) == 1]
    conteo = {m: 0 for m in MODOS}
    sin_etiqueta = 0
    for i in con_fallo:
        if i.get("modoFallo") in conteo:
            conteo[i["modoFallo"]] += 1
        else:
            sin_etiqueta += 1
    piden = [i for i in items if i.get("proponeMoverNumero") is True]
    return {
        "fallos": len(con_fallo),
        "porModo": {m: n for m, n in conteo.items() if n},
        "sinEtiqueta": sin_etiqueta,
        "pidenMoverNumero": len(piden),
        "pidenMoverSinPoder": [i["clave"] for i in piden if not i["puedeMoverNumeros"]],
        "nota": "etiquetas de Jev sobre la prosa del veredicto (backend/analisis/modo_fallo.py): "
                "agrupan, no puntúan. `pidenMoverSinPoder` son lecciones de casos contaminados o en "
                "cuarentena que proponen mover un peso: el dossier las muestra, no las aplica",
    }


COHORTE_VIGENTE = "vigente"


def inventario(skill: str = "", estado: str = "", limite: int = 400, cohorte: str = "") -> dict:
    """Todo lo aprendido, por skill, con las métricas de la población ciega.

    `cohorte`: "" = todas; "vigente" = la del proceso actual; o una clave
    concreta. Las métricas y los conteos por skill se calculan SOBRE LA
    COHORTE ELEGIDA; el resumen de cohortes viaja siempre entero para que se
    vea cuánto queda fuera. Lo que está en cuarentena se lista aparte y no
    entra en ningún conteo."""
    from backend.analisis.parte import COHORTE, COHORTES, cohorte_de
    estados = _estados()
    todos_los_casos = _casos(limite)
    clave_cohorte = COHORTE if cohorte == COHORTE_VIGENTE else cohorte
    cohortes = []
    for clave in sorted({c["cohorte"] for c in todos_los_casos} | {COHORTE}):
        de = [c for c in todos_los_casos if c["cohorte"] == clave]
        cohortes.append({**cohorte_de(clave), "casos": len(de),
                         "enCuarentena": sum(1 for c in de if c.get("cuarentena"))})
    casos = [c for c in todos_los_casos if not clave_cohorte or c["cohorte"] == clave_cohorte]
    todos = [i for caso in casos for i in _items_de(caso, estados)]
    poblacion, metricas = _metricas(casos)
    en_cuarentena = [i for i in todos if i["cuarentena"]]
    todos = [i for i in todos if not i["cuarentena"]]
    # los estudios de reventones hacia atrás (backend/analisis/reventones.py):
    # mismas lecciones por skill, población post_resultado (fijan rúbrica)
    if clave_cohorte in ("", COHORTE):
        from backend.analisis import reventones as _rev
        todos += _rev.items_leccion(estados, COHORTE)

    filtrados = [i for i in todos
                 if (not skill or i["skill"] == skill)
                 and (not estado or i["estado"] == estado)]

    por_skill = []
    for nombre in sorted({i["skill"] for i in todos if i["skill"]}):
        suyas = [i for i in todos if i["skill"] == nombre]
        cuenta = {e: sum(1 for i in suyas if i["estado"] == e) for e in ESTADOS}
        atribuidos = {v: sum(1 for i in suyas if i["veredicto"] == v)
                      for v in vered.VEREDICTOS}
        fallos_pendientes = sum(1 for i in suyas
                                if i["veredicto"] == "fallo" and i["estado"] == "pendiente")
        por_skill.append({
            "skill": nombre,
            "lecciones": cuenta,
            "atribuidos": atribuidos,
            # EL SESGO SE DECLARA, NO SE DISIMULA. El skill se nombra sobre todo
            # cuando algo falla: publicar esto como "tasa de acierto del skill"
            # sería inventar un denominador que nadie midió.
            "sesgoDeAtribucion": "quien cierra el caso nombra el skill sobre todo cuando algo "
                                 "falla: estos conteos NO son una tasa de acierto del skill",
            "acreditables": sum(1 for i in suyas if i["puedeMoverNumeros"]),
            "soloRubrica": sum(1 for i in suyas if not i["puedeMoverNumeros"]),
            "revisionAbierta": fallos_pendientes >= DISPARADOR_REVISION,
            "fallosPendientes": fallos_pendientes,
            "faltanParaDisparar": max(0, DISPARADOR_REVISION - fallos_pendientes),
            "disparador": f"{DISPARADOR_REVISION} fallos con lección pendiente del mismo skill "
                          "ABREN la revisión; no autorizan ningún cambio",
            "liston": _liston(nombre, metricas),
            "porModoFallo": _por_modo_fallo(suyas),
            "items": [i for i in filtrados if i["skill"] == nombre],
        })

    huerfanas = [i for i in todos if not i["skill"]]
    return {
        "generadoEn": efedb.ahora(),
        # PARA EL DOSSIER (fase D): los fallos agrupados por causa, y la alarma
        # que importa: lecciones que PIDEN mover un número sin poder sostenerlo
        "porModoFallo": _por_modo_fallo(todos),
        "filtro": {"skill": skill, "estado": estado, "cohorte": clave_cohorte},
        "cohortes": cohortes,
        "cohorteVigente": COHORTE,
        "notaCohortes": ("la cohorte se sella al depositar y no cambia con un re-depósito; "
                         "las métricas de arriba son SOLO de la cohorte elegida (vacío = todas). "
                         + COHORTES.get(COHORTE, "")),
        "enCuarentena": {
            "cuantas": len(en_cuarentena),
            "automaticas": sum(1 for i in en_cuarentena if i["cuarentenaAutomatica"]),
            "porque": "casos apartados por criterio (qué le faltaba al parte antes del pitazo), "
                      "nunca por resultado: no cuentan ni fijan rúbrica. Las automáticas son "
                      "partes sin DT declarado en un lado; se levantan re-depositando el parte con el DT",
            "items": en_cuarentena,
        },
        "poblacion": {
            **poblacion,
            "nota": "las poblaciones no se suman entre sí: solo `ciega` + `PRE` acredita, "
                    "las demás fijan rúbrica; `cuarentena` no cuenta en nada",
        },
        "acreditables": metricas,
        "porSkill": por_skill,
        "sinSkill": {
            "cuantas": len(huerfanas),
            "porque": "la lección no declaró de qué skill es: no se reparte a ojo",
            "items": [i for i in filtrados if not i["skill"]],
        },
        "estados": list(ESTADOS),
        "items": filtrados,
    }


# ── fase D: el dossier de revisión de un skill ──────────────────────────────
#
# El disparador (4 fallos con lección pendiente del mismo skill) ABRE la
# revisión; esto es lo que se abre: todo lo que hace falta para decidir,
# ordenado para que la decisión no dependa del criterio del día. Qué NO hace:
# no genera el .zip, no mueve un peso y no marca nada `aplicada`. El flujo es
# el de docs/APRENDIZAJE.md § D: la app detecta, el usuario decide, Cowork
# redacta el diff con autorización, el usuario lo instala y marca `aplicada`
# con la versión donde entró.

_RAIZ = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(
    __import__("os").path.abspath(__file__))))


def calibracion_espina(limite: int = 400) -> dict:
    """Lo que el analista lee ANTES de escribir su espina: cuánto acierta la
    espina de la tarjeta por nivel de riesgo y fuerza, cuánto acierta él
    cuando la sigue y quién gana cuando la contradice. Sale de nuestros propios
    veredictos ciegos, así que se recalibra solo con cada caso cerrado."""
    _pob, metricas = _metricas(_casos(limite))
    esp = metricas.get("espina") or {}
    return {
        "generadoEn": efedb.ahora(),
        "tarjeta": esp.get("tarjeta"),
        "analistaPorLectura": {k: esp.get(k) for k in ("positiva", "cero", "negativa", "neutra")},
        "comoLeerlo": ("empieza por la espina de la tarjeta (`familias.*.espinaTarjeta` en /burbujas). Si es "
                       "FUERTE y su nivel acierta en esta tabla, síguela salvo que un skill diga otra cosa con "
                       "un hecho concreto; si es DÉBIL (riesgo alto: revienta, pero no se sabe cómo), los skills "
                       "deciden cómo se corta. Ir contra la tarjeta se dice en `porque`, y esta tabla mide si "
                       "valió la pena"),
    }


LADO_DE = {"local": "a", "visita": "b"}


def derrotas_favorito(cohorte: str = COHORTE_VIGENTE, limite: int = 400) -> dict:
    """Las derrotas del equipo que el 1X2 declarado daba como ganador, cada una
    con lo que el TDE y el DTP habían ESCRITO ANTES del pitazo (pedido del
    usuario, 21/10/2026: «las derrotas no esperadas las podremos justificar con
    eso»). La disciplina 9 del TDE manda la lectura: solo cuenta lo declarado
    antes —una rama escrita que describe cómo se perdió es evidencia; explicar
    la derrota después de verla, no—. Por eso cada caso dice si la rama que
    jugó el favorito estaba escrita y qué decía, sin juzgar si «la explicó».

    `explicacion`: `rama_escrita` (la rama que jugó el partido estaba
    declarada) · `rama_sin_escribir` · `sin_goles` (perdió… sin goles no hay
    rama: no pasa) · `sin_ficha` (no se sabe quién marcó primero)."""
    from backend.analisis.parte import COHORTE
    clave = COHORTE if cohorte == COHORTE_VIGENTE else cohorte
    casos = [c for c in _casos(limite) if not clave or c["cohorte"] == clave]
    out, resumen = [], {"rama_escrita": 0, "rama_sin_escribir": 0, "sin_ficha": 0, "sin_goles": 0}
    for c in casos:
        obj = _objetivo(c["fixtureId"], c["parte"])
        u = obj.get("unXDos") or {}
        fav = LADO_DE.get(u.get("declarado") or "")
        real = u.get("real") or ""
        if not fav or not real or real == "empate" or LADO_DE.get(real) == fav:
            continue
        riv = "b" if fav == "a" else "a"
        bloques = {b.get("equipo"): b for b in (obj.get("tde") or {}).get("bloques") or []}
        tde_fav = bloques.get(fav) or {}
        reas = tde_fav.get("reasignacion") or {}
        if reas.get("rama") == "sinGoles":
            expl = "sin_goles"
        elif not reas.get("rama"):
            expl = "sin_ficha"
        else:
            expl = "rama_escrita" if reas.get("declarada") else "rama_sin_escribir"
        resumen[expl] += 1
        parte = c["parte"]
        dtp_fav = next((b for b in (parte.get("dtp") or {}).get("bloques") or [] if b.get("equipo") == fav), {})
        decl_tde = next((b for b in (parte.get("tde") or {}).get("bloques") or [] if b.get("equipo") == fav), {})
        lado_v = ((c["veredicto"].get("porLado") or {}).get(fav) or {})
        out.append({
            "fixtureId": c["fixtureId"], "fecha": c["fecha"],
            "partido": f"{c['equipoA']} vs {c['equipoB']}",
            "favorito": {"lado": fav, "equipo": c["equipoA"] if fav == "a" else c["equipoB"],
                         "probabilidad": u.get("probabilidadDeclarada")},
            "marcador": (obj.get("marcador") or {}).get("texto", ""),
            "goles": (obj.get("evidencia") or {}).get("goles") or [],
            "seleccion": c["veredicto"].get("seleccion", ""),
            "cuarentena": bool(c.get("cuarentena")),
            "explicacion": expl,
            "tde": {"ramaJugada": reas.get("rama"), "minuto": reas.get("minuto"),
                    "loDeclarado": reas.get("loDeclarado"), "segundoGiro": reas.get("segundoGiro"),
                    "salida": reas.get("salida"),
                    "tipologia": decl_tde.get("tipologia", ""), "ventana": tde_fav.get("ventana", ""),
                    "golEnVentana": tde_fav.get("golEnVentana")},
            "tdeRival": {"ramaJugada": ((bloques.get(riv) or {}).get("reasignacion") or {}).get("rama"),
                         "loDeclarado": ((bloques.get(riv) or {}).get("reasignacion") or {}).get("loDeclarado")},
            # lo que el DTP del favorito había escrito sobre cómo le marca el rival
            "dtpViasRival": ((dtp_fav.get("apertura") or {}).get("m2") or {}).get("viasGol", {}).get("rival") or [],
            "leccion": lado_v.get("leccion", ""),
        })
    out.sort(key=lambda x: x["fecha"], reverse=True)
    return {
        "generadoEn": efedb.ahora(), "cohorte": clave, "derrotas": out, "resumen": resumen,
        "nota": ("derrotas del equipo que el 1X2 declarado daba como ganador, con lo que el TDE y el DTP habían "
                 "escrito ANTES del pitazo. Solo cuenta lo declarado (disciplina 9 del TDE): `rama_escrita` dice "
                 "que el escenario que se jugó estaba descrito, no que se haya acertado; el juicio es de la "
                 "autopsia (`leccion`)."),
    }


def version_skill(skill: str) -> str:
    """La versión vigente del snapshot del skill (docs/skills/<skill>/SKILL.md):
    la que va en `aplicadaEn` cuando una lección entra. '' si no hay snapshot."""
    import os
    import re
    ruta = os.path.join(_RAIZ, "docs", "skills", skill, "SKILL.md")
    try:
        with open(ruta, encoding="utf-8") as f:
            m = re.search(r"\*\*v(\d+(?:\.\d+)+)", f.read(20000))
    except OSError:
        return ""
    return f"v{m.group(1)}" if m else ""


FLUJO_REVISION = [
    "la app detecta y abre la revisión (esto): no escribe nada ni genera nada",
    "el usuario lee el dossier y decide si se arma una versión nueva",
    "con la autorización, Cowork toma el skill vigente + este dossier y redacta el diff",
    "el usuario instala el skill nuevo en la cuenta",
    "el usuario marca `aplicada` cada lección, con la versión donde entró",
]


def revision(skill: str, cohorte: str = COHORTE_VIGENTE, limite: int = 400) -> dict:
    """El dossier del skill: lecciones pendientes agrupadas por la regla que
    tocan, con su población y lo que autoriza cada una; métricas ciegas SOLO
    de los casos de este skill contra su listón; y una lectura calculada de lo
    que la revisión puede y no puede concluir."""
    from backend.analisis.parte import COHORTE
    inv = inventario(skill=skill, cohorte=cohorte, limite=limite)
    sk = next((x for x in inv["porSkill"] if x["skill"] == skill), None)
    clave_cohorte = COHORTE if cohorte == COHORTE_VIGENTE else cohorte
    base = {"skill": skill, "versionVigente": version_skill(skill), "cohorte": clave_cohorte,
            "generadoEn": efedb.ahora(), "flujo": FLUJO_REVISION}
    if not sk:
        return {**base, "existe": False, "abierta": False, "fallosPendientes": 0,
                "faltanParaDisparar": DISPARADOR_REVISION, "lecciones": [], "porRegla": [],
                "metricas": None, "poblacion": None, "liston": None, "porModoFallo": None,
                "enCuarentena": [], "lectura": "sin lecciones de este skill en la cohorte elegida"}
    abiertas = [i for i in sk["items"] if i["estado"] in ("pendiente", "en_revision")]
    # una revisión ya abierta sigue abierta mientras tenga lecciones en ella: el
    # disparador del inventario cuenta solo `pendiente`, y abrirla las mueve
    fallos_abiertos = sum(1 for i in abiertas if i["veredicto"] == "fallo")
    abierta = fallos_abiertos >= DISPARADOR_REVISION or any(i["estado"] == "en_revision" for i in abiertas)
    faltan = max(0, DISPARADOR_REVISION - fallos_abiertos)
    # métricas ciegas SOLO de los casos donde algún lado nombró este skill
    estados = _estados()
    casos = [c for c in _casos(limite)
             if (not clave_cohorte or c["cohorte"] == clave_cohorte)
             and any(((c["veredicto"].get("porLado") or {}).get(l) or {}).get("skill", "").strip() == skill
                     for l in ("a", "b"))]
    poblacion, metricas = _metricas(casos)
    del estados
    grupos: dict[str, list[dict]] = {}
    for i in abiertas:
        grupos.setdefault(i["reglaTocada"] or "(sin regla declarada)", []).append(i)
    por_regla = []
    for regla, its in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
        modos: dict[str, int] = {}
        for i in its:
            if i.get("modoFallo"):
                modos[i["modoFallo"]] = modos.get(i["modoFallo"], 0) + 1
        por_regla.append({
            "regla": regla, "lecciones": len(its), "claves": [i["clave"] for i in its],
            "fallos": sum(1 for i in its if i["veredicto"] == "fallo"),
            "parciales": sum(1 for i in its if i["veredicto"] == "parcial"),
            "acreditables": sum(1 for i in its if i["puedeMoverNumeros"]),
            "pidenMoverNumero": sum(1 for i in its if i.get("proponeMoverNumero") is True),
            "pidenMoverYPueden": sum(1 for i in its
                                     if i.get("proponeMoverNumero") is True and i["puedeMoverNumeros"]),
            "porModoFallo": modos,
        })
    acred_piden = sum(r["pidenMoverYPueden"] for r in por_regla)
    acred = sum(r["acreditables"] for r in por_regla)
    liston = sk.get("liston")
    if not abierta:
        lectura = (f"revisión NO disparada: {fallos_abiertos} fallo(s) con lección pendiente, "
                   f"faltan {faltan}. El dossier se puede leer, pero no hay nada que decidir")
    elif not acred:
        lectura = ("ninguna lección abierta viene de un caso ciega + PRE: esta revisión solo puede FIJAR "
                   "RÚBRICA (aclarar cómo se aplica una regla), no mover ningún número del skill")
    elif not acred_piden:
        lectura = (f"{acred} lección(es) acreditable(s), pero ninguna pide mover un número (según Jev): la "
                   "revisión fija rúbrica; un cambio de peso no tiene quien lo sostenga")
    elif liston and not liston.get("cumple"):
        lectura = (f"{acred_piden} lección(es) acreditable(s) piden mover un número, pero el listón del "
                   f"propio skill no se cumple ({liston.get('semaforo')}): el cambio de peso espera; la "
                   "rúbrica se puede fijar ya")
    else:
        lectura = (f"{acred_piden} lección(es) acreditable(s) piden mover un número y nada del listón lo "
                   "impide: la decisión es del usuario, con el dossier a la vista")
    return {
        **base, "existe": True,
        "abierta": abierta, "fallosPendientes": fallos_abiertos,
        "faltanParaDisparar": faltan, "disparador": sk["disparador"],
        "sesgoDeAtribucion": sk["sesgoDeAtribucion"],
        "enRevision": sum(1 for i in abiertas if i["estado"] == "en_revision"),
        "lecciones": abiertas, "porRegla": por_regla,
        "poblacion": {**poblacion, "nota": inv["poblacion"]["nota"]},
        "metricas": metricas, "liston": liston,
        "porModoFallo": sk.get("porModoFallo"),
        "pidenMoverSinPoder": [i for i in abiertas
                               if i.get("proponeMoverNumero") is True and not i["puedeMoverNumeros"]],
        "enCuarentena": [i for i in inv["enCuarentena"]["items"] if i["skill"] == skill],
        "lectura": lectura,
    }


def abrir_revision(skill: str, cohorte: str = COHORTE_VIGENTE) -> dict:
    """Pasa a `en_revision` las lecciones PENDIENTES del dossier (solo si la
    revisión está disparada). Deja constancia de qué entró en la revisión;
    no autoriza ni aplica nada. Lo hace el usuario, no el agente."""
    d = revision(skill, cohorte)
    if not d.get("abierta"):
        raise LeccionInvalida(f"la revisión de {skill} no está disparada: {d.get('lectura', '')}")
    movidas = []
    for i in d["lecciones"]:
        if i["estado"] != "pendiente":
            continue
        with _conectar() as con:
            con.execute(
                "INSERT INTO leccion_estado (clave, estado, aplicada_en, nota, actualizado_en) "
                "VALUES (?,?,?,?,?) ON CONFLICT(clave) DO UPDATE SET "
                "estado=excluded.estado, actualizado_en=excluded.actualizado_en",
                (i["clave"], "en_revision", "", f"revisión de {skill} abierta", efedb.ahora()))
        movidas.append(i["clave"])
    print(f"[cowork] revisión de {skill} abierta: {len(movidas)} lección(es) a en_revision", flush=True)
    return {"skill": skill, "movidas": movidas, "versionVigente": d["versionVigente"]}


class LeccionInvalida(ValueError):
    """El cambio de estado no se puede aplicar tal cual llegó."""


# Hasta qué fecha de partido miró cada versión vigente su dossier (la fecha
# en que se redactó la propuesta en docs/revisiones/). Una lección de un caso
# ANTERIOR ya entró en esa revisión: queda `aplicada` en esa versión. Se
# actualiza con cada versión nueva (25/10/2026: 2.632 lecciones, ninguna
# cerrada, aunque cuatro versiones ya habían salido de esos dossiers).
# Historial por skill, de la más vieja a la vigente: cada lección se cierra
# en la PRIMERA versión cuyo corte es posterior a su partido (la que la leyó).
CORTE_VERSION = {
    "diagnostico-tactico": [("v1.4", "2026-10-21"), ("v1.5", "2026-10-25")],
    "efe-clasificador": [("v1.6", "2026-10-21")],
    "sad-analysis": [("v4.0", "2026-10-21"), ("v4.1", "2026-10-25")],
    "teorema-del-echado": [("v0.1.22", "2026-10-22"), ("v0.1.23", "2026-10-25")],
}


def cerrar_anteriores(skill: str) -> dict:
    """Pasa a `aplicada` (con la versión) las lecciones PENDIENTES del skill
    cuyos partidos son anteriores al corte de su versión vigente: esa revisión
    ya las leyó. Las posteriores quedan pendientes: son el dossier que viene.
    Lo hace el usuario, no el agente."""
    if skill not in CORTE_VERSION:
        raise LeccionInvalida(f"{skill} no tiene versión con corte en CORTE_VERSION")
    historial = sorted(CORTE_VERSION[skill], key=lambda vc: vc[1])
    version, corte = historial[-1]
    inv = inventario(skill=skill, limite=100000)
    filas, porVersion = [], {}
    for i in inv["items"]:
        if i["estado"] != "pendiente":
            continue
        f = (i.get("fecha") or "")[:10]
        v = next(((vv, cc) for vv, cc in historial if f < cc), None)
        if not v:
            continue
        filas.append((i["clave"], v[0], f"cerrada en bloque: el dossier de {v[0]} (redactado el {v[1]}) "
                                        "ya leyó este caso"))
        porVersion[v[0]] = porVersion.get(v[0], 0) + 1
    ahora = efedb.ahora()
    with _conectar() as con:
        con.executemany(
            "INSERT INTO leccion_estado (clave, estado, aplicada_en, nota, actualizado_en) "
            "VALUES (?,'aplicada',?,?,?) ON CONFLICT(clave) DO UPDATE SET "
            "estado=excluded.estado, aplicada_en=excluded.aplicada_en, nota=excluded.nota, "
            "actualizado_en=excluded.actualizado_en",
            [(k, v, n, ahora) for k, v, n in filas])
    quedan = sum(1 for i in inv["items"] if i["estado"] == "pendiente") - len(filas)
    print(f"[cowork] {skill}: {len(filas)} lecciones anteriores al {corte} → aplicada ({porVersion})", flush=True)
    return {"skill": skill, "version": version, "corte": corte, "cerradas": len(filas),
            "porVersion": porVersion, "quedanPendientes": quedan,
            "nota": "cada lección queda aplicada en la primera versión cuyo dossier la leyó"}


def descartar_cohorte(cohorte: str, nota: str = "") -> dict:
    """Pasa a `descartada` TODAS las lecciones pendientes de una cohorte que no
    es la vigente. Las de rodaje y c2 no calibran nada (su insumo era el viejo:
    DT rancio, TDE sin nivel) y llenaban la pantalla de Aprendizaje con 113
    pendientes que nadie iba a revisar. Lo hace el usuario, no el agente; la
    vigente no se descarta en bloque: sus lecciones se miran una por una."""
    from backend.analisis.parte import COHORTE
    cohorte = (cohorte or "").strip()
    if not cohorte or cohorte in (COHORTE, COHORTE_VIGENTE):
        raise LeccionInvalida("la cohorte vigente no se descarta en bloque: sus lecciones son las que "
                              "calibran y se revisan una por una")
    nota = (nota or "").strip() or f"descarte en bloque de la cohorte {cohorte}: no calibra"
    estados = _estados()
    casos = [c for c in _casos(100000) if c["cohorte"] == cohorte]
    if not casos:
        raise KeyError(cohorte)
    claves = [i["clave"] for c in casos for i in _items_de(c, estados) if i["estado"] == "pendiente"]
    ahora = efedb.ahora()
    with _conectar() as con:
        con.executemany(
            "INSERT INTO leccion_estado (clave, estado, aplicada_en, nota, actualizado_en) "
            "VALUES (?,'descartada','',?,?) ON CONFLICT(clave) DO UPDATE SET "
            "estado=excluded.estado, nota=excluded.nota, actualizado_en=excluded.actualizado_en",
            [(k, nota, ahora) for k in claves])
    print(f"[cowork] cohorte {cohorte}: {len(claves)} lecciones pendientes → descartada", flush=True)
    return {"cohorte": cohorte, "descartadas": len(claves), "claves": claves, "nota": nota}


def mover(clave: str, estado: str, aplicada_en: str = "", nota: str = "") -> dict:
    """Cambia el estado de una lección. Lo hace el usuario, no el agente."""
    estado = (estado or "").strip().lower()
    if estado not in ESTADOS:
        raise LeccionInvalida(f"estado tiene que ser uno de {', '.join(ESTADOS)}")
    aplicada_en = (aplicada_en or "").strip()
    # UNA LECCIÓN APLICADA SIN VERSIÓN NO SE PUEDE AUDITAR. Y el momento más
    # barato para anotar dónde entró es justo este; después nadie se acuerda.
    if estado == "aplicada" and not aplicada_en:
        raise LeccionInvalida(
            "marcar `aplicada` exige `aplicadaEn` con la versión del skill donde entró: "
            "sin eso, dentro de seis meses no hay forma de saber si el cambio se hizo")

    inv = inventario()
    item = next((i for i in inv["items"] if i["clave"] == clave), None)
    if not item:
        raise KeyError(clave)
    with _conectar() as con:
        con.execute(
            "INSERT INTO leccion_estado (clave, estado, aplicada_en, nota, actualizado_en) "
            "VALUES (?,?,?,?,?) ON CONFLICT(clave) DO UPDATE SET "
            "estado=excluded.estado, aplicada_en=excluded.aplicada_en, "
            "nota=excluded.nota, actualizado_en=excluded.actualizado_en",
            (clave, estado, aplicada_en, (nota or "").strip(), efedb.ahora()))
    print(f"[cowork] lección {clave} → {estado}"
          + (f" (en {aplicada_en})" if aplicada_en else ""), flush=True)
    return {**item, "estado": estado, "aplicadaEn": aplicada_en,
            "nota": (nota or "").strip(), "actualizadoEn": efedb.ahora()}
