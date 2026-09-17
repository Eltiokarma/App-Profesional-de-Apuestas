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

import json

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


def _casos(limite: int = 400) -> list[dict]:
    """Los partes con veredicto, con su parte y su juicio ya cargados."""
    from backend.analisis.parte import _conectar as conectar_parte

    with conectar_parte() as con:
        filas = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b, parte_json, veredicto_json "
            "FROM parte_cowork WHERE veredicto_json IS NOT NULL "
            "ORDER BY fecha DESC LIMIT ?", (limite,)).fetchall()
    fuera = []
    for f in filas:
        fuera.append({
            "fixtureId": f["fixture_id"], "fecha": (f["fecha"] or "")[:10],
            "equipoA": f["equipo_a"], "equipoB": f["equipo_b"],
            "parte": json.loads(f["parte_json"]),
            "veredicto": json.loads(f["veredicto_json"]),
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
        leccion = (lv.get("leccion") or "").strip()
        if not leccion:
            continue   # sin lección no hay nada que acumular: el veredicto ya está en el parte
        clave = f"{caso['fixtureId']}:{lado}"
        st = estados.get(clave) or {}
        propio = caso["equipoA"] if lado == "a" else caso["equipoB"]
        rival = caso["equipoB"] if lado == "a" else caso["equipoA"]
        fuera.append({
            "clave": clave,
            "fixtureId": caso["fixtureId"], "lado": lado,
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
            # LA DISTINCIÓN QUE EL DOSSIER NO PUEDE DEJAR AL CRITERIO DEL DÍA:
            # un caso contaminado enseña, pero no mueve un número.
            "puedeMoverNumeros": acredita,
            "queAutoriza": ("puede sostener un cambio de peso" if acredita else
                            "solo fija rúbrica: aclara cómo se aplica una regla, "
                            "no mueve ningún número"),
            "estado": st.get("estado") or "pendiente",
            "aplicadaEn": st.get("aplicada_en") or "",
            "nota": st.get("nota") or "",
            "actualizadoEn": st.get("actualizado_en") or "",
        })
    return fuera


def _metricas(casos: list[dict]) -> tuple[dict, dict]:
    """Población por separado, y las métricas SOLO de lo acreditable."""
    poblacion = {s: {"casos": 0, "lados": 0} for s in vered.SELECCIONES}
    acred = {"acierto": 0, "parcial": 0, "fallo": 0}
    casos_acred, briers, reales, con_reparto = 0, [], [], 0
    unxdos_ok, unxdos_de = 0, 0
    tde_obs, tde_positivos, tde_sin_ficha = 0, 0, 0
    rev = _reventon_vacio()

    for caso in casos:
        v = caso["veredicto"]
        sel = v.get("seleccion", "")
        lados = [l for l in ("a", "b") if (v.get("porLado") or {}).get(l)]
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
        obj = vered.objetivo(caso["fixtureId"], caso["parte"])
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
            if b.get("golEnVentana") is None:
                tde_sin_ficha += 1
                continue
            tde_obs += 1
            tde_positivos += 1 if b["golEnVentana"] else 0
        _acumular_reventon(rev, obj.get("reventon") or {})

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
            "sinFicha": tde_sin_ficha,
            "nota": "ventanas del TDE comprobadas contra los goles recibidos, en población "
                    "ciega. `sinFicha` no cuenta como no ocurrido: no se pudo comprobar",
        },
        "reventon": _cerrar_reventon(rev),
    }
    return poblacion, metricas


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


def _reventon_vacio() -> dict:
    return {"porNivel": {n: {"observadas": 0, "reventadas": 0} for n in NIVELES_RIESGO},
            "extremo": {"observadas": 0, "reventadas": 0},
            "sinBurbuja": 0, "noComprobables": 0}


def _acumular_reventon(acc: dict, reventon: dict) -> None:
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


def _cerrar_reventon(acc: dict) -> dict:
    from backend.analisis.burbuja import TASA_BACKTEST, TASA_BASE_BACKTEST
    por_nivel = {}
    for nivel, c in acc["porNivel"].items():
        n, k = c["observadas"], c["reventadas"]
        tasa = round(k / n, 3) if n else None
        esperado = TASA_BACKTEST.get(nivel)
        dentro = None
        if tasa is not None and esperado and n >= REVENTON_N_MINIMO:
            dentro = esperado[0] <= tasa <= esperado[1]
        por_nivel[nivel] = {
            "observadas": n, "reventadas": k, "tasa": tasa,
            "esperadoBacktest": list(esperado) if esperado else None,
            "dentroDelBacktest": dentro,
            "nMinimo": REVENTON_N_MINIMO,
        }
    obs = sum(c["observadas"] for c in acc["porNivel"].values())
    revs = sum(c["reventadas"] for c in acc["porNivel"].values())
    fuera = [n for n, c in por_nivel.items() if c["dentroDelBacktest"] is False]
    return {
        "observadas": obs, "reventadas": revs,
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
                 f"(docs/REVENTON.md §8) solo con n ≥ {REVENTON_N_MINIMO}; un nivel fuera del rango "
                 "ABRE la revisión de los puntos, no los mueve. `sinBurbuja` y `noComprobables` no "
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


def inventario(skill: str = "", estado: str = "", limite: int = 400) -> dict:
    """Todo lo aprendido, por skill, con las métricas de la población ciega."""
    estados = _estados()
    casos = _casos(limite)
    todos = [i for caso in casos for i in _items_de(caso, estados)]
    poblacion, metricas = _metricas(casos)

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
            "items": [i for i in filtrados if i["skill"] == nombre],
        })

    huerfanas = [i for i in todos if not i["skill"]]
    return {
        "generadoEn": efedb.ahora(),
        "filtro": {"skill": skill, "estado": estado},
        "poblacion": {
            **poblacion,
            "nota": "las poblaciones no se suman entre sí: solo `ciega` + `PRE` acredita, "
                    "las demás fijan rúbrica",
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


class LeccionInvalida(ValueError):
    """El cambio de estado no se puede aplicar tal cual llegó."""


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
