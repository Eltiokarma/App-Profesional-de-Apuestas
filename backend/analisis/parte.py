"""El parte de Cowork — análisis escrito con la suscripción, no con la API.

Qué cambia respecto del camino viejo (`backend/analisis/motor.py`): ahí el
servidor le paga a la API de Claude un JSON de 92 campos por partido. Aquí el
análisis lo escribe Cowork de noche con la suscripción plana y lo DEPOSITA;
el backend solo lo guarda, calcula lo que es aritmética y lo sirve. La API de
Claude queda de emergencia.

Qué manda Cowork y qué NO (la regla de docs/efe-dtp/COSTO_IA.md aplicada al
texto: lo que se puede calcular no se le hace escribir):

  manda            los sub-scores crudos A-E, la tabla de plantel con zona y
                   rol, las bajas públicas, las alertas, el matchup, el
                   pronóstico con sus tres fuentes y los documentos en prosa
  NO manda         total, máximo alcanzable, porcentaje, clasificación, IP,
                   reducción por zona, ramas A/B, F3, F4 — todo eso sale de
                   este módulo con las fórmulas del protocolo
  NO manda tampoco los nombres del partido, la liga ni la fecha: son nuestros

El bloque F llega CONGELADO por diseño (ninguna fuente publica el once la
noche anterior). Cuando el once aparece —de la ficha que ya ingesta
API-Football, o de un pantallazo que el usuario le pasa a Cowork— entra por
`resolver_xi` y el bloque se cierra en local, gratis y al instante.

Excepción de solo-lectura: escribe efe.db (tabla `parte_cowork`), nunca las
DBs del SAD.
"""
import json
import sqlite3
from datetime import date as date_t, datetime, timedelta, timezone

from backend import db as saddb
from backend.analisis import bloque_f, db as efedb, veredicto as vered
from backend.nombres import canonizar, normalizar

VERSION = "cowork/1"

DDL = """
CREATE TABLE IF NOT EXISTS parte_cowork (
    fixture_id INTEGER PRIMARY KEY,
    fecha TEXT,
    equipo_a TEXT, equipo_b TEXT,
    estado TEXT NOT NULL DEFAULT 'pendiente_xi',
    version TEXT,
    parte_json TEXT NOT NULL,
    xi_json TEXT,
    creado_en TEXT NOT NULL,
    actualizado_en TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_parte_fecha ON parte_cowork(fecha);
CREATE INDEX IF NOT EXISTS idx_parte_estado ON parte_cowork(estado);
"""

# TABLA DE PUNTUACIÓN del protocolo: TOTAL = A + B×1.5 + C + D + E×2
# (máximo 27 con bloque C, 23 sin él). Los sub-scores crudos son lo único que
# Cowork escribe; el ponderado y el porcentaje salen de aquí.
PESO_BLOQUE = {"A": 1.0, "B": 1.5, "C": 1.0, "D": 1.0, "E": 2.0}
MAX_BLOQUE = {"A": 4.0, "B": 6.0, "C": 4.0, "D": 4.0, "E": 3.0}
LETRAS = ("A", "B", "C", "D", "E")
LADOS = ("a", "b")
# por debajo de esto, el cruce del once con la tabla no es creíble y el bloque F
# se queda congelado en vez de publicar un IP inventado (ver _disponibilidad)
MINIMO_CASADOS = 7
# tipos de evento institucional del protocolo TIMELINE (los de partido los pone
# cronologia.py: ver docs/efe-dtp/COSTO_IA.md)
TL_TIPOS = ("institucional", "tecnico", "sancion", "hito")
# documentos que la pantalla sabe titular sola; cualquier otro id se acepta
# igual y se muestra con el título que venga
DOCUMENTOS = {
    "dtp": "Diagnóstico táctico",
    "matriz": "Matriz de escenarios",
    "tde": "Teorema del Echado",
    "ensayo": "Cómo puede darse el partido",
    "timeline": "Timeline comparativo",
    "pendientes": "Qué falta cerrar",
}


class ParteInvalido(ValueError):
    """El depósito no se puede guardar tal cual llegó (y se dice por qué)."""


# el veredicto llegó después de la primera versión de la tabla: se añade en
# caliente para no perder los partes ya depositados (en SQLite un ALTER que ya
# existe es un error, no un problema)
_COLUMNAS_NUEVAS = (("veredicto_json", "TEXT"),)


def _conectar():
    con = efedb.conectar()
    con.executescript(DDL)
    for columna, tipo in _COLUMNAS_NUEVAS:
        try:
            con.execute(f"ALTER TABLE parte_cowork ADD COLUMN {columna} {tipo}")
        except sqlite3.OperationalError:
            pass  # ya existe: el caso normal a partir de la segunda conexión
    return con


def clasificacion_de(pct: float) -> str:
    """≥70% FORMADO · 40-69% EN FORMACIÓN · <40% SIN FORMACIÓN."""
    return "FORMADO" if pct >= 70 else ("EN_FORMACION" if pct >= 40 else "SIN_FORMACION")


# ── normalización del depósito ──────────────────────────────────────────────

def _num(v, tope: float) -> float:
    try:
        n = float(v)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(tope, round(n, 2)))


def _txt(v) -> str:
    return (v or "").strip() if isinstance(v, str) else ""


def _lista_txt(v) -> list[str]:
    if isinstance(v, str):
        v = [v]
    return [_txt(x) for x in (v or []) if _txt(x)]


def _jugador(j: dict) -> dict | None:
    nombre = _txt(j.get("nombre"))
    if not nombre:
        return None
    zona = _txt(j.get("zona")).upper()
    rol = _txt(j.get("rol")).upper()
    if zona not in bloque_f.ZONAS or rol not in bloque_f.ROLES:
        return None  # sin zona o sin rol no pesa en ninguna fórmula: sería relleno
    return {"nombre": nombre, "posicion": _txt(j.get("posicion")), "zona": zona,
            "rol": rol, "apps": _txt(j.get("apps"))}


def _fuera(f: dict) -> dict | None:
    nombre = _txt(f.get("nombre"))
    if not nombre:
        return None
    estado = _txt(f.get("estado")).lower()
    return {"nombre": nombre,
            "estado": estado if estado in ("baja", "duda") else "baja",
            "motivo": _txt(f.get("motivo"))}


def _equipo(bruto: dict, equipos_db: list[tuple[str, str]]) -> dict:
    bloques_in = bruto.get("bloques") or {}
    excluidos_in = bruto.get("excluidos") or {}
    notas_in = bruto.get("notas") or {}
    bloques = {}
    for letra in LETRAS:
        motivo = _txt(excluidos_in.get(letra))
        bloques[letra] = {
            "score": 0.0 if motivo else _num(bloques_in.get(letra), MAX_BLOQUE[letra]),
            "max": MAX_BLOQUE[letra],
            "peso": PESO_BLOQUE[letra],
            "excluido": bool(motivo),
            "motivoExclusion": motivo,
            "nota": _txt(notas_in.get(letra)),
        }
    plantel = [j for j in (_jugador(x) for x in (bruto.get("plantel") or [])) if j]
    fuera = [f for f in (_fuera(x) for x in (bruto.get("fuera") or [])) if f]
    dt = bruto.get("dt") or {}
    if isinstance(dt, str):
        dt = {"nombre": dt}
    perfil = bruto.get("perfil") or {}
    nombre = _txt(bruto.get("nombre"))
    return {
        "nombre": canonizar(nombre, equipos_db) if nombre else "",
        "bloques": bloques,
        "dt": {"nombre": _txt(dt.get("nombre")), "meses": _num(dt.get("meses"), 600)},
        "perfil": {k: _txt(perfil.get(k)) for k in ("sistema", "estilo", "fortaleza", "vulnerabilidad")},
        "plantel": plantel,
        "fuera": fuera,
        "factorX": [{"nombre": _txt(x.get("nombre")), "contexto": _txt(x.get("contexto"))}
                    for x in (bruto.get("factorX") or []) if _txt(x.get("nombre"))],
        "sensibilidad": [x for x in (_sensibilidad(y) for y in (bruto.get("sensibilidad") or [])) if x],
    }


def _sensibilidad(x: dict) -> dict | None:
    """Caja de sensibilidad: qué cambiaría si el dato que falta fuera otro.

    Es la contrapartida honesta de "sin dato es una respuesta válida": el hueco
    se declara Y se dice cuánto movería el análisis. Un hueco sin esto es una
    excusa; con esto es una incertidumbre acotada."""
    supuesto = _txt(x.get("supuesto"))
    if not supuesto:
        return None
    return {"supuesto": supuesto, "efecto": _txt(x.get("efecto"))}


_SEMAFORO = ("verde", "ambar", "rojo")


def _sem(v, con_na: bool = False) -> str:
    t = _txt(v).lower()
    if t in _SEMAFORO or (con_na and t == "na"):
        return t
    return "na" if con_na else ""


def _lectura_sad(x: dict) -> dict:
    """Lo que el protocolo llama la lectura SAD: el juicio que cierra el EFE.

    Es puro criterio —no hay forma de calcularlo— y es lo que el analista lee
    primero cuando ya vio los números. Sin sitio propio en el parte terminaba
    diluido dentro del ensayo."""
    uxd = x.get("unXDos") or x.get("un_x_dos") or {}
    if isinstance(uxd, str):
        uxd = {"texto": uxd}
    return {
        "moduloOperativo": _txt(x.get("moduloOperativo") or x.get("modulo_operativo")),
        "unXDos": {"texto": _txt(uxd.get("texto")),
                   "rangoAmpliado": bool(uxd.get("rangoAmpliado") or uxd.get("rango_ampliado"))},
        "contextoEmocional": _txt(x.get("contextoEmocional") or x.get("contexto_emocional")),
        "datoEstructural": _txt(x.get("datoEstructural") or x.get("dato_estructural")),
        "paradoja": _txt(x.get("paradoja")),
    }


def _via_tde(v: dict) -> dict | None:
    nombre = _txt(v.get("nombre"))
    if not nombre:
        return None
    return {"nombre": nombre, "indice": _num(v.get("indice"), 1000),
            "ventana": _txt(v.get("ventana")), "detalle": _txt(v.get("detalle"))}


def _tde(x: dict) -> dict:
    """Teorema del Echado: los dos índices y su ventana.

    Los NIVELES (verde/ámbar/rojo) llegan del skill, no los inventa el backend:
    la escala del IE es suya y ponerle umbrales aquí sería duplicar —y con el
    tiempo desalinear— una tabla que vive en otro lado. Sin nivel, la pantalla
    pinta el número en neutro."""
    if not isinstance(x, dict):
        return {}
    vias = [v for v in (_via_tde(y) for y in (x.get("vias") or [])) if v]
    tiene = any([_txt(x.get("tipologia")), vias, x.get("ie") is not None, x.get("ise") is not None])
    if not tiene:
        return {}
    equipo = _txt(x.get("equipo")).lower()
    return {
        "ie": _num(x.get("ie"), 1000), "ieNivel": _sem(x.get("ieNivel")),
        "ise": _num(x.get("ise"), 1000), "iseNivel": _sem(x.get("iseNivel")),
        "equipo": equipo if equipo in LADOS else "",
        "tipologia": _txt(x.get("tipologia")),
        "ventana": _txt(x.get("ventana")),
        "disciplina43": bool(x.get("disciplina43")),
        "vias": vias,
        "falsador": _txt(x.get("falsador")),
    }


def _evento_tl(e: dict) -> dict | None:
    """Un evento INSTITUCIONAL del timeline. Los partidos no entran por aquí:
    los calcula backend/cronologia.py de nuestra propia base."""
    from backend import cronologia as crono
    titulo = _txt(e.get("titulo"))
    fecha = _txt(e.get("fecha"))
    if not titulo or not fecha:
        return None
    tipo = _txt(e.get("tipo")).lower()
    if tipo in crono.TIPOS_PARTIDO or tipo not in TL_TIPOS:
        # un resultado copiado a mano se descarta: el marcador es de la ingesta
        return None
    return {
        "fecha": fecha, "aproximada": bool(e.get("aproximada")) or fecha.startswith("~"),
        "equipo": _txt(e.get("equipo")), "tipo": tipo, "titulo": titulo,
        "detalle": _txt(e.get("detalle")), "jornada": 0, "marcador": "",
        "destacado": bool(e.get("destacado")),
        "alerta_relacionada": _txt(e.get("alertaRelacionada") or e.get("alerta_relacionada")),
        "fuente": _txt(e.get("fuente")),
    }


def _alerta(a: dict) -> dict | None:
    codigo = _txt(a.get("codigo"))
    if not codigo:
        return None
    equipo = _txt(a.get("equipo")).lower()
    tipo = _txt(a.get("tipo")).lower()
    return {"codigo": codigo,
            "equipo": equipo if equipo in ("a", "b", "global") else "global",
            "tipo": tipo if tipo in ("estructural", "fecha") else "fecha",
            "detalle": _txt(a.get("detalle"))}


def _documento(d: dict) -> dict | None:
    cuerpo = _txt(d.get("cuerpo"))
    if not cuerpo:
        return None
    ident = _txt(d.get("id")) or "nota"
    formato = _txt(d.get("formato")).lower()
    return {"id": ident,
            "titulo": _txt(d.get("titulo")) or DOCUMENTOS.get(ident, ident),
            "formato": formato if formato in ("md", "html", "texto") else "md",
            "cuerpo": cuerpo}


def normalizar_parte(payload: dict) -> dict:
    """Deja el depósito en la forma exacta del contrato.

    Lo que no cumple no se corrige a ojo: un jugador sin zona o sin rol no
    entra (no pesaría en ninguna fórmula), un bloque fuera de rango se recorta
    a su máximo y un documento vacío se descarta. Lo descartado se cuenta y
    se devuelve en el recibo, para que Cowork lo vea en su propia corrida.
    """
    try:
        fixture_id = int(payload.get("fixtureId"))
    except (TypeError, ValueError):
        raise ParteInvalido("fixtureId ausente o no numérico: sácalo de /analisis/cowork/agenda")
    equipos_in = payload.get("equipos") or {}
    if not isinstance(equipos_in, dict) or not any(equipos_in.get(l) for l in LADOS):
        raise ParteInvalido("equipos.a / equipos.b vacíos: a = local, b = visitante")

    equipos_db = [(r["name"], normalizar(r["name"]))
                  for r in saddb.query("sad", "SELECT name FROM teams")]
    parte = {
        "fixtureId": fixture_id,
        "version": _txt(payload.get("version")) or VERSION,
        "generadoEn": _txt(payload.get("generadoEn")),
        "equipos": {l: _equipo(equipos_in.get(l) or {}, equipos_db) for l in LADOS},
        "alertas": [a for a in (_alerta(x) for x in (payload.get("alertas") or [])) if a],
        "matchup": {},
        "pronostico": {},
        "lecturaSad": _lectura_sad(payload.get("lecturaSad") or payload.get("lectura_sad") or {}),
        "tde": _tde(payload.get("tde") or {}),
        "timelineEventos": [e for e in (_evento_tl(x) for x in (payload.get("timelineEventos") or [])) if e],
        "timelineNarrativa": _txt(payload.get("timelineNarrativa")),
        "cadena": {l: _txt(((payload.get("cadena") or {}).get(l) or {}).get("pronostico")
                           if isinstance((payload.get("cadena") or {}).get(l), dict)
                           else (payload.get("cadena") or {}).get(l))
                   for l in LADOS},
        "documentos": [d for d in (_documento(x) for x in (payload.get("documentos") or [])) if d],
        "pendientes": _lista_txt(payload.get("pendientes")),
        "fuentes": _lista_txt(payload.get("fuentes")),
        "descartados": _lista_txt(payload.get("descartados")),
        "notas": _txt(payload.get("notas")),
    }
    m = payload.get("matchup") or {}
    diag = _txt(m.get("diagnostico")).upper().replace("MATCHUP ", "")
    parte["matchup"] = {
        "diagnostico": diag if diag in ("FAVORABLE", "NEUTRO", "DESFAVORABLE") else "NEUTRO",
        "favorece": _txt(m.get("favorece")).lower() if _txt(m.get("favorece")).lower() in LADOS else "",
        "razon": _txt(m.get("razon")),
        # H2a/H2b/H2c: los tres indicadores que SOSTIENEN el diagnóstico. Sin
        # ellos, "MATCHUP FAVORABLE" es una etiqueta sin nada detrás.
        "h2a": _sem(m.get("h2a"), con_na=True),
        "h2b": _sem(m.get("h2b"), con_na=True),
        "h2c": _sem(m.get("h2c"), con_na=True),
    }
    p = payload.get("pronostico") or {}
    prob = p.get("probabilidades") or {}
    parte["pronostico"] = {
        "motor": _txt(p.get("motor")),
        "matriz": _txt(p.get("matriz")),
        "mercado": _txt(p.get("mercado")),
        "probabilidades": {k: _num(prob.get(k), 100) for k in ("local", "empate", "visita")},
        "marcador": _txt(p.get("marcador")),
        "falsador": _txt(p.get("falsador")),
    }
    return parte


# ── guardado ────────────────────────────────────────────────────────────────

def _fixture(fixture_id: int):
    return saddb.query_one(
        "sad",
        "SELECT f.id, f.date, f.league_id, f.league_season, f.home_team_id, f.away_team_id, "
        "ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id "
        "JOIN teams at ON at.id=f.away_team_id WHERE f.id=?",
        (fixture_id,),
    )


def guardar(payload: dict) -> dict:
    """Deposita el parte (idempotente por fixture: el último manda).

    El partido —nombres, fecha, liga— NO se toma del depósito: se toma de
    nuestra base. Si Cowork mandó nombres y no coinciden con los nuestros, no
    se corrige en silencio: se guarda igual y la discrepancia va en el recibo
    y en la pantalla. Analizar el partido equivocado es el error que este
    chequeo tiene que hacer visible.
    """
    parte = normalizar_parte(payload)
    fx = _fixture(parte["fixtureId"])
    if not fx:
        raise ParteInvalido(f"el fixture {parte['fixtureId']} no está en nuestra base: "
                            "pide la lista con /analisis/cowork/agenda")
    discrepancias = []
    for lado, nuestro in (("a", fx["home_name"]), ("b", fx["away_name"])):
        suyo = parte["equipos"][lado]["nombre"]
        if suyo and normalizar(suyo) != normalizar(nuestro):
            discrepancias.append(f"lado {lado}: mandaste «{suyo}» y el fixture dice «{nuestro}»")
        parte["equipos"][lado]["nombre"] = nuestro

    ahora = efedb.ahora()
    with _conectar() as con:
        previo = con.execute("SELECT creado_en, xi_json FROM parte_cowork WHERE fixture_id=?",
                             (parte["fixtureId"],)).fetchone()
        con.execute(
            "INSERT INTO parte_cowork (fixture_id, fecha, equipo_a, equipo_b, estado, version, "
            "parte_json, xi_json, creado_en, actualizado_en) VALUES (?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(fixture_id) DO UPDATE SET fecha=excluded.fecha, equipo_a=excluded.equipo_a, "
            "equipo_b=excluded.equipo_b, version=excluded.version, parte_json=excluded.parte_json, "
            "actualizado_en=excluded.actualizado_en",
            (parte["fixtureId"], (fx["date"] or "")[:10], fx["home_name"], fx["away_name"],
             "pendiente_xi", parte["version"], json.dumps(parte, ensure_ascii=False),
             previo["xi_json"] if previo else None,
             previo["creado_en"] if previo else ahora, ahora),
        )
    # un parte nuevo sobre un fixture que ya tenía once resuelto se recalcula
    # solo al leerlo: el once vive aparte, justamente para sobrevivir al parte
    cadena, cadena_ignorada = _guardar_cadena(fx, parte.get("cadena") or {})
    resumen = {
        "fixtureId": parte["fixtureId"],
        "partido": f"{fx['home_name']} vs {fx['away_name']}",
        "fecha": (fx["date"] or "")[:10],
        "estado": "actualizado" if previo else "guardado",
        "jugadores": {l: len(parte["equipos"][l]["plantel"]) for l in LADOS},
        "documentos": [d["id"] for d in parte["documentos"]],
        "alertas": len(parte["alertas"]),
        "discrepancias": discrepancias,
        "xiResuelto": bool(previo and previo["xi_json"]),
        "eventosTimeline": len(parte.get("timelineEventos") or []),
        "cadena": cadena,
        "cadenaIgnorada": cadena_ignorada,
        "conLecturaSad": bool((parte.get("lecturaSad") or {}).get("moduloOperativo")),
        "conTde": bool(parte.get("tde")),
    }
    print(f"[cowork] parte {resumen['estado']}: {resumen['partido']} "
          f"({resumen['jugadores']['a']}+{resumen['jugadores']['b']} jugadores, "
          f"{len(parte['documentos'])} documentos, "
          f"{resumen['eventosTimeline']} eventos de timeline)"
          + (f" · cadena: {', '.join(cadena)}" if cadena else "")
          + (f" · PRONÓSTICO YA DECLARADO, se conserva el primero: {cadena_ignorada}"
             if cadena_ignorada else "")
          + (f" · DISCREPANCIAS: {discrepancias}" if discrepancias else ""), flush=True)
    return resumen


def borrar(fixture_id: int) -> bool:
    with _conectar() as con:
        cur = con.execute("DELETE FROM parte_cowork WHERE fixture_id=?", (fixture_id,))
    return cur.rowcount > 0


# ── lectura: el DTO que pinta la pantalla ───────────────────────────────────

def _totales(equipo: dict) -> dict:
    total = maximo = 0.0
    for letra in LETRAS:
        b = equipo["bloques"][letra]
        b["ponderado"] = round(b["score"] * b["peso"], 2)
        b["topePonderado"] = round(b["max"] * b["peso"], 2)
        if b["excluido"]:
            continue
        total += b["ponderado"]
        maximo += b["topePonderado"]
    pct = round((total / maximo) * 100, 1) if maximo else 0.0
    return {"total": round(total, 2), "maximoAlcanzable": round(maximo, 2),
            "porcentaje": pct, "clasificacion": clasificacion_de(pct)}


def _disponibilidad(equipo: dict, xi: dict | None) -> dict:
    """El bloque F: resuelto si ya hay once, en dos ramas si todavía no."""
    plantel, fuera = equipo["plantel"], equipo["fuera"]
    if not plantel:
        return {"resuelto": False, "sinTabla": True, "fuente": "",
                "nota": "el parte llegó sin tabla de plantel: no hay bloque F que calcular"}
    congelado = {
        "resuelto": False, "sinTabla": False, "fuente": "",
        "ramas": bloque_f.ramas(plantel, fuera),
        "jugadores": [{**j, "estado": "", "motivo": ""} for j in plantel],
        "nota": "bloque F congelado: sin once confirmado no se puntúa (Disciplina 35)",
    }
    if not (xi and xi.get("once")):
        return congelado
    d = bloque_f.resolver(plantel, fuera, xi.get("once") or [], xi.get("banca") or [])
    if d["casados"] < MINIMO_CASADOS:
        # un once que casa con 3 de 11 no describe a un equipo diezmado: describe
        # una hoja que no corresponde a esta tabla (otro partido, otro equipo, o
        # nombres que se escriben distinto). Antes que publicar un IP falso, el
        # bloque se queda congelado y se dice exactamente qué no casó.
        return {**congelado, "conflicto":
                f"el once recibido casa con {d['casados']} de {d['once']} nombres de la tabla: "
                "no se cierra el bloque F con eso. Revisa que sea el partido correcto o manda "
                "los nombres como aparecen en la tabla del parte.",
                "noReconocidos": d["noReconocidos"], "dudas": d["dudas"],
                "fuente": xi.get("fuente", "")}
    return {**d, "resuelto": True, "sinTabla": False,
            "fuente": xi.get("fuente", ""), "capturadoEn": xi.get("capturadoEn", ""),
            "formacion": xi.get("formacion", "")}


def timeline_del_parte(fx, eventos: list[dict], narrativa: str, fuentes: list[str]) -> dict | None:
    """Funde lo institucional de Cowork con los partidos CALCULADOS.

    Misma regla y mismo código que el timeline por API (docs/efe-dtp/COSTO_IA.md):
    los resultados, la jornada y el enfrentamiento directo salen de `fixtures`
    vía backend/cronologia.py, no de lo que escriba nadie. Cowork solo aporta
    lo que no se puede calcular —crisis, sanciones, cambios de DT, hitos— y
    esta función arma el TimelineData que pinta la pantalla de siempre.
    """
    from backend import cronologia as crono
    desde, hasta = crono.ventana()
    calculados = crono.eventos_del_partido(
        fx["home_team_id"], fx["home_name"], fx["away_team_id"], fx["away_name"], desde, hasta)
    if not calculados and not eventos:
        return None
    return {
        "titulo": f"{fx['home_name']} vs {fx['away_name']}",
        "periodo": {"desde": desde, "hasta": hasta},
        "equipos": [
            {"nombre": fx["home_name"], "lado": "izquierda",
             "color": "#5B8DEF", "color_secundario": "#C7D0EC",
             "stats": crono.stats_de(fx["home_team_id"], fx["league_id"],
                                     fx["league_season"], desde, hasta)},
            {"nombre": fx["away_name"], "lado": "derecha",
             "color": "#E5484D", "color_secundario": "#F2C1C3",
             "stats": crono.stats_de(fx["away_team_id"], fx["league_id"],
                                     fx["league_season"], desde, hasta)},
        ],
        "eventos": crono.ordenar(list(eventos) + calculados),
        "agrupacion": "mes",
        "narrativa": narrativa,
        "datos_faltantes": [],
        "fuentes": sorted({*(fuentes or []), crono.FUENTE}),
    }


def _guardar_cadena(fx, cadena: dict) -> tuple[list[str], list[str]]:
    """El pronóstico clave por equipo foco entra en la cadena del DTP.

    La película del equipo (página de Equipo) se alimenta de `cadena_dtp`, y
    hasta aquí solo escribía en ella el motor por API: con Cowork llevando el
    análisis, la cadena se habría quedado congelada. Se escribe SOLO la
    apertura —el pronóstico, antes del partido—; el veredicto lo emite después
    quien cierre el eslabón, que es lo que lo hace auditable.

    Dos cosas que este método NO hace, y que son la misma regla mirada desde
    sus dos lados:

    - **No pisa un pronóstico ya declarado.** Re-depositar el parte con otro
      pronóstico después del partido convertiría la cadena en hindsight. El
      primero manda y el segundo se delata en el recibo.
    - **No borra un veredicto ya escrito.** Un re-depósito posterior al cierre
      arrasaba con `que_paso`/`veredicto`/`leccion`: se fundían en el registro
      vacío de la apertura. Ahora se conservan.
    """
    from backend.analisis.motor import _partido_n  # misma numeración, no otra
    escritos, ignorados = [], []
    fecha = (fx["date"] or "")[:10] or None
    for lado, (foco, rival, tid) in (("a", (fx["home_name"], fx["away_name"], fx["home_team_id"])),
                                     ("b", (fx["away_name"], fx["home_name"], fx["away_team_id"]))):
        pronostico = (cadena.get(lado) or "").strip()
        if not pronostico:
            continue
        previo = ((efedb.eslabon_de_fixture(foco, fx["id"]) or {}).get("registro") or {})
        declarado = (previo.get("pronostico_clave") or "").strip()
        if declarado and declarado != pronostico:
            ignorados.append(foco)
        efedb.guardar_cadena(
            foco, _partido_n(tid, fx["date"] or ""), rival, fecha, fx["id"], None,
            registro={
                "pronostico_clave": declarado or pronostico,
                "que_paso": previo.get("que_paso", ""),
                "veredicto": previo.get("veredicto", ""),
                "leccion": previo.get("leccion", ""),
            },
        )
        escritos.append(foco)
    return escritos, ignorados


def dto(fixture_id: int) -> dict | None:
    """Todo lo que la pantalla necesita, con lo calculable ya calculado."""
    with _conectar() as con:
        fila = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b, estado, version, parte_json, "
            "xi_json, creado_en, actualizado_en FROM parte_cowork WHERE fixture_id=?",
            (fixture_id,),
        ).fetchone()
    if not fila:
        return None
    parte = json.loads(fila["parte_json"])
    xi = json.loads(fila["xi_json"]) if fila["xi_json"] else {}
    alertas = list(parte["alertas"])
    equipos = {}
    for lado in LADOS:
        eq = parte["equipos"][lado]
        tot = _totales(eq)
        disp = _disponibilidad(eq, xi.get(lado))
        f3 = bloque_f.alerta_f3(tot["clasificacion"], disp.get("ipNivel", "verde")) if disp.get("resuelto") else None
        if f3:
            alertas.append({**f3, "equipo": lado})
        equipos[lado] = {**eq, **tot, "disponibilidad": disp}
    fx = _fixture(fila["fixture_id"])
    # el timeline se funde AL LEER, no al depositar: si la ingesta corrige un
    # marcador, la próxima lectura ya lo trae — sellarlo sería congelar hoy lo
    # que mañana se recalcula gratis
    timeline = None
    if fx:
        timeline = timeline_del_parte(fx, parte.get("timelineEventos") or [],
                                      parte.get("timelineNarrativa") or "",
                                      parte.get("fuentes") or [])
    return {
        "fixtureId": fila["fixture_id"],
        "estado": fila["estado"],
        "version": fila["version"],
        "partido": {"equipoA": fila["equipo_a"], "equipoB": fila["equipo_b"],
                    "fecha": fila["fecha"],
                    "equipoAId": fx["home_team_id"] if fx else 0,
                    "equipoBId": fx["away_team_id"] if fx else 0},
        "equipos": equipos,
        "alertas": alertas,
        "matchup": parte["matchup"],
        "lecturaSad": parte.get("lecturaSad") or _lectura_sad({}),
        "tde": parte.get("tde") or {},
        "timeline": timeline,
        "pronostico": parte["pronostico"],
        "documentos": parte["documentos"],
        "pendientes": parte["pendientes"],
        "fuentes": parte["fuentes"],
        "notas": parte["notas"],
        "xi": {l: {k: v for k, v in (xi.get(l) or {}).items() if k != "banca"} for l in LADOS},
        "veredicto": veredicto_de(fila["fixture_id"]),
        "creadoEn": fila["creado_en"],
        "actualizadoEn": fila["actualizado_en"],
    }


# ── el once: de la ficha o a mano ───────────────────────────────────────────

def xi_de_ficha(fixture_id: int, team_id: int) -> dict | None:
    """El once que ya capturó la ingesta (API-Football). Costo cero.

    Si la ficha no tiene alineación —el caso que obliga al pantallazo— esto
    devuelve None y no inventa nada."""
    filas = saddb.query(
        "sad",
        "SELECT jugador, titular, formacion FROM alineaciones WHERE fixture_id=? AND team_id=? "
        "ORDER BY titular DESC",
        (fixture_id, team_id),
    )
    titulares = [f["jugador"] for f in filas if f["titular"] and f["jugador"]]
    if len(titulares) < 7:  # media alineación no es una alineación
        return None
    return {
        "once": titulares,
        "banca": [f["jugador"] for f in filas if not f["titular"] and f["jugador"]],
        "formacion": filas[0]["formacion"] or "",
        "fuente": "ficha de API-Football",
        "capturadoEn": efedb.ahora(),
    }


def resolver_xi(fixture_id: int, onces: dict) -> dict:
    """Guarda el once por lado y cierra el bloque F. Sin modelo, sin costo.

    `onces` = {"a": {"once": [...], "banca": [...], "fuente": "..."}, "b": {...}}
    Un lado ausente en `onces` conserva el que ya tuviera guardado: el once
    del local suele llegar antes que el del visitante.
    """
    with _conectar() as con:
        fila = con.execute("SELECT xi_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
        if not fila:
            raise ParteInvalido(f"no hay parte de Cowork para el fixture {fixture_id}")
        guardado = json.loads(fila["xi_json"]) if fila["xi_json"] else {}
        for lado in LADOS:
            nuevo = onces.get(lado)
            if not nuevo:
                continue
            once = _lista_txt(nuevo.get("once"))
            if not once:
                continue
            guardado[lado] = {
                "once": once,
                "banca": _lista_txt(nuevo.get("banca")),
                "formacion": _txt(nuevo.get("formacion")),
                "fuente": _txt(nuevo.get("fuente")) or "carga manual",
                "capturadoEn": efedb.ahora(),
            }
        con.execute("UPDATE parte_cowork SET xi_json=?, actualizado_en=? WHERE fixture_id=?",
                    (json.dumps(guardado, ensure_ascii=False), efedb.ahora(), fixture_id))
    listo = dto(fixture_id)
    # confirmado solo si los DOS bloques F quedaron cerrados de verdad
    estado = ("confirmado" if all(listo["equipos"][l]["disponibilidad"].get("resuelto")
                                  for l in LADOS) else "pendiente_xi")
    if estado != listo["estado"]:
        with _conectar() as con:
            con.execute("UPDATE parte_cowork SET estado=? WHERE fixture_id=?", (estado, fixture_id))
        listo["estado"] = estado
    for lado in LADOS:
        d = listo["equipos"][lado]["disponibilidad"]
        quien = listo["partido"]["equipoA" if lado == "a" else "equipoB"]
        if d.get("resuelto"):
            print(f"[cowork] XI {lado} · {quien}: IP {d['ip']} ({d['ipNivel']}) · "
                  f"{d['f4']['rotados']} rotados"
                  + (f" · dudas: {len(d['dudas'])}" if d.get("dudas") else ""), flush=True)
        elif d.get("conflicto"):
            print(f"[cowork] XI {lado} · {quien}: NO se cierra — {d['conflicto']}", flush=True)
    return listo


def resolver_desde_ficha(fixture_id: int) -> dict:
    """Intenta cerrar el bloque F con lo que ya tenemos ingestado."""
    fx = _fixture(fixture_id)
    if not fx:
        raise ParteInvalido(f"el fixture {fixture_id} no está en nuestra base")
    onces = {}
    for lado, team_id in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        xi = xi_de_ficha(fixture_id, team_id)
        if xi:
            onces[lado] = xi
    if not onces:
        raise ParteInvalido(
            "la ficha del partido todavía no trae alineaciones: corre "
            "`python -m backend.ingesta.ficha_partido` o manda el once a mano "
            "(POST /analisis/cowork/{id}/xi) desde el pantallazo")
    return resolver_xi(fixture_id, onces)


# ── el veredicto: 12 h después (fase B de docs/APRENDIZAJE.md) ─────────────

def _lado_veredicto(x) -> dict | None:
    if not isinstance(x, dict):
        return None
    v = _txt(x.get("veredicto")).lower()
    if v not in vered.VEREDICTOS:
        return None
    return {"veredicto": v, "queP": _txt(x.get("queP")), "leccion": _txt(x.get("leccion")),
            "skill": _txt(x.get("skill")), "reglaTocada": _txt(x.get("reglaTocada"))}


def guardar_veredicto(fixture_id: int, payload: dict) -> dict:
    """Cierra el caso: lo objetivo se calcula aquí, el juicio llega de Cowork.

    La población (`seleccion`) y el modo de evaluación los DECLARA quien
    escribe, porque el backend no puede saber si el veredicto se redactó antes
    o después de mirar el marcador. Se guardan con el caso para que ninguna
    tasa de acierto los pueda ignorar después.
    """
    with _conectar() as con:
        fila = con.execute("SELECT parte_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
    if not fila:
        raise ParteInvalido(f"no hay parte de Cowork para el fixture {fixture_id}")
    parte = json.loads(fila["parte_json"])

    seleccion = _txt(payload.get("seleccion")).lower()
    modo = _txt(payload.get("modoEvaluacion")).upper()
    if seleccion not in vered.SELECCIONES:
        raise ParteInvalido(
            "seleccion tiene que ser ciega, por_resultado o post_resultado: es lo que "
            "decide si el caso acredita o solo fija rúbrica, y no se puede deducir")
    if modo not in vered.MODOS:
        raise ParteInvalido("modoEvaluacion tiene que ser PRE o COND")

    por_lado = {}
    for l in LADOS:
        v = _lado_veredicto((payload.get("porLado") or {}).get(l))
        if v:
            por_lado[l] = v
    if not por_lado:
        raise ParteInvalido("porLado vacío: hace falta el veredicto de al menos un lado "
                            "(acierto, parcial o fallo)")

    cumplido = payload.get("falsadorCumplido")
    guardado = {
        "seleccion": seleccion,
        "modoEvaluacion": modo,
        "acredita": vered.acredita(seleccion, modo),
        "falsador": {"texto": (parte.get("pronostico") or {}).get("falsador", ""),
                     "cumplido": cumplido if isinstance(cumplido, bool) else None},
        "porLado": por_lado,
        "notas": _txt(payload.get("notas")),
        "cerradoEn": efedb.ahora(),
    }
    with _conectar() as con:
        con.execute("UPDATE parte_cowork SET veredicto_json=?, actualizado_en=? WHERE fixture_id=?",
                    (json.dumps(guardado, ensure_ascii=False), efedb.ahora(), fixture_id))

    sin_pronostico = _cerrar_cadena(fixture_id, por_lado)
    listo = veredicto_de(fixture_id)
    obj = listo.get("objetivo") or {}
    print(f"[cowork] veredicto {fixture_id}: {obj.get('marcador', {}).get('texto', '?')} · "
          f"1X2 {'✓' if obj.get('unXDos', {}).get('acerto') else '✗'} · "
          f"{seleccion}/{modo} ({'acredita' if guardado['acredita'] else 'no acredita'})"
          + (f" · sin pronóstico previo: {sin_pronostico}" if sin_pronostico else ""), flush=True)
    listo["sinPronosticoPrevio"] = sin_pronostico
    return listo


def _cerrar_cadena(fixture_id: int, por_lado: dict) -> list[str]:
    """Escribe el cierre en la cadena del DTP, respetando el anti-hindsight.

    Sin pronóstico previo NO se emite veredicto en la cadena: un juicio sobre
    algo que nunca se declaró no es auditable, es una opinión escrita después.
    El caso se guarda igual en el parte y el lado se devuelve para delatarlo.
    """
    fx = _fixture(fixture_id)
    if not fx:
        return []
    sin_pronostico = []
    for lado, (foco, tid) in (("a", (fx["home_name"], fx["home_team_id"])),
                              ("b", (fx["away_name"], fx["away_team_id"]))):
        v = por_lado.get(lado)
        if not v:
            continue
        eslabon = efedb.eslabon_de_fixture(foco, fixture_id)
        previo = ((eslabon or {}).get("registro") or {}).get("pronostico_clave", "")
        if not previo:
            sin_pronostico.append(foco)
            continue
        from backend.analisis.motor import _partido_n
        efedb.guardar_cadena(
            foco, _partido_n(tid, fx["date"] or ""), fx["away_name"] if lado == "a" else fx["home_name"],
            (fx["date"] or "")[:10] or None, fixture_id, None,
            registro={"pronostico_clave": previo, "que_paso": v["queP"],
                      "veredicto": v["veredicto"], "leccion": v["leccion"]},
        )
    return sin_pronostico


def veredicto_de(fixture_id: int) -> dict | None:
    """El veredicto guardado + la parte objetiva RECALCULADA al leer.

    Igual que el timeline: lo derivado no se sella. Si la ingesta corrige un
    marcador o llega la ficha de eventos que faltaba, la próxima lectura trae
    el cálculo bueno sin que nadie tenga que volver a escribir el juicio.
    """
    with _conectar() as con:
        fila = con.execute(
            "SELECT parte_json, veredicto_json FROM parte_cowork WHERE fixture_id=?",
            (fixture_id,)).fetchone()
    if not fila or not fila["veredicto_json"]:
        return None
    parte = json.loads(fila["parte_json"])
    guardado = json.loads(fila["veredicto_json"])
    return {**guardado, "fixtureId": fixture_id,
            "objetivo": vered.objetivo(fixture_id, parte)}


def pendientes_veredicto(horas: int = 12, limite: int = 50) -> list[dict]:
    """Partes de partidos terminados hace más de `horas` y todavía sin cerrar.

    Es lo que dispara la corrida de validación: nadie tiene que acordarse de
    nada, y lo que no se validó hoy sigue estando mañana."""
    with _conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b FROM parte_cowork "
            "WHERE veredicto_json IS NULL ORDER BY fecha DESC LIMIT 400").fetchall()
    if not filas:
        return []
    ids = [f["fixture_id"] for f in filas]
    marca = (datetime.now(timezone.utc) - timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
    marcadores = {
        r["id"]: r for r in saddb.query(
            "sad",
            f"SELECT f.id, f.date, COALESCE(f.fulltime_home, f.goals_home) AS gl, "
            f"COALESCE(f.fulltime_away, f.goals_away) AS gv FROM fixtures f "
            f"WHERE f.id IN ({','.join('?' * len(ids))}) AND f.date <= ?",
            (*ids, marca))
    }
    out = []
    for f in filas:
        m = marcadores.get(f["fixture_id"])
        if not m or m["gl"] is None or m["gv"] is None:
            continue  # aún no jugado, o sin marcador todavía en nuestra base
        out.append({
            "fixtureId": f["fixture_id"],
            "fecha": f["fecha"],
            "partido": f"{f['equipo_a']} vs {f['equipo_b']}",
            "marcador": f"{m['gl']}-{m['gv']}",
            "jugadoEn": m["date"],
        })
        if len(out) >= limite:
            break
    return out


def pendientes(limite: int = 50) -> list[dict]:
    """Partes esperando once — lo primero que mira el usuario al despertar."""
    with _conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b, estado, xi_json, actualizado_en "
            "FROM parte_cowork WHERE estado!='confirmado' ORDER BY fecha, fixture_id LIMIT ?",
            (limite,),
        ).fetchall()
    out = []
    for f in filas:
        xi = json.loads(f["xi_json"]) if f["xi_json"] else {}
        out.append({
            "fixtureId": f["fixture_id"],
            "fecha": f["fecha"],
            "partido": f"{f['equipo_a']} vs {f['equipo_b']}",
            "faltaXi": [l for l in LADOS if not (xi.get(l) or {}).get("once")],
            "actualizadoEn": f["actualizado_en"],
        })
    return out


# ── la agenda del día: qué merece análisis, calculado ───────────────────────

# Prioridad 1-5 del protocolo de batch. Lo que se puede decidir con datos se
# decide con datos; lo que no (una rivalidad sin vecindad geográfica), se
# declara parcial en vez de fingirse resuelto.
_COPAS = ("libertadores", "sudamericana", "copa america", "mundial", "champions")
_TOP_CONDICIONADAS = ("liga profesional", "liga mx", "primera division argentina")
_EUROPA = ("premier league", "la liga", "laliga", "bundesliga", "serie a", "ligue 1")


def _prioridad(liga: dict, etiquetas: set[str], pos_local: int, pos_visita: int) -> tuple[int, str]:
    nombre = normalizar(liga.get("nombre") or "")
    pais = normalizar(liga.get("pais") or "")
    if "peru" in pais and ("liga 1" in nombre or "primera" in nombre):
        return 1, "Liga 1 Perú"
    if "CLASICO" in etiquetas:
        return 2, "clásico / derbi detectado"
    if any(c in nombre for c in _COPAS):
        return 3, f"copa internacional ({liga.get('nombre')})"
    if any(c in nombre for c in _TOP_CONDICIONADAS):
        if "EN_CRISIS" in etiquetas or (0 < pos_local <= 8) or (0 < pos_visita <= 8):
            return 4, "liga grande con equipo arriba o en crisis"
        return 0, "liga grande sin equipo arriba ni cambio de DT"
    if any(c in nombre for c in _EUROPA):
        if (0 < pos_local <= 6) and (0 < pos_visita <= 6):
            return 5, "choque directo del top 6"
        if pos_local == 1 or pos_visita == 1:
            return 5, "partido con el líder"
        return 0, "europea sin top 6 ni líder"
    return 0, f"fuera del padrón de ligas cubiertas ({liga.get('nombre')})"


def agenda(fecha: date_t | None = None, limite: int = 4) -> dict:
    """Los partidos del día ordenados por prioridad — calculado, no preguntado.

    Es el paso 1 del batch: en vez de hacerle deducir a Cowork qué partido
    importa (y pagar esa deducción en tiempo y en búsquedas), la base lo
    resuelve con el criterio numérico del protocolo. Los descartados viajan
    CON su motivo: un descarte sin motivo no se puede auditar.
    """
    from backend import app as sadapp  # liga_meta y el mapa de posiciones

    dia = fecha or (datetime.now(timezone.utc) + timedelta(days=1)).date()
    filas = saddb.query(
        "sad",
        "SELECT f.id, f.date, f.league_id, f.league_season, f.home_team_id, f.away_team_id, "
        "ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        "WHERE f.date >= ? AND f.date < ? ORDER BY f.date",
        (dia.isoformat(), (dia + timedelta(days=1)).isoformat()),
    )
    with _conectar() as con:
        ya = {r["fixture_id"]: r["estado"] for r in
              con.execute("SELECT fixture_id, estado FROM parte_cowork").fetchall()}

    from backend import calendario as cal
    candidatos, descartados = [], []
    for f in filas:
        liga = sadapp.liga_meta(f["league_id"])
        try:
            posiciones = cal._posiciones(f["league_id"], f["league_season"], cal._hora()) if f["league_season"] else {}
        except Exception:
            posiciones = {}
        etiquetas = set()
        try:
            ciudad = cal._ciudad(f["home_team_id"])
            for e in cal.etiquetas_de_rival(f["away_team_id"], False, f["league_id"],
                                            f["league_season"], (f["date"] or "")[:10], ciudad):
                etiquetas.add(e["codigo"])
        except Exception:
            pass
        prio, motivo = _prioridad(liga, etiquetas,
                                  posiciones.get(f["home_team_id"], 0),
                                  posiciones.get(f["away_team_id"], 0))
        item = {
            "fixtureId": f["id"],
            "hora": (f["date"] or "")[11:16],
            "partido": f"{f['home_name']} vs {f['away_name']}",
            "equipoA": f["home_name"], "equipoB": f["away_name"],
            "liga": liga.get("nombre"), "pais": liga.get("pais"),
            "prioridad": prio, "motivo": motivo,
            "etiquetas": sorted(etiquetas),
            "parte": ya.get(f["id"], ""),
        }
        (candidatos if prio else descartados).append(item)
    candidatos.sort(key=lambda i: (i["prioridad"], i["hora"]))
    return {
        "fecha": dia.isoformat(),
        "analizar": candidatos[:limite],
        "enEspera": candidatos[limite:],
        "descartados": descartados,
        "nota": "CLÁSICO solo se detecta por derbi de ciudad: una rivalidad nacional sin "
                "vecindad geográfica no sale de nuestros datos y puede estar entre los descartados",
    }
