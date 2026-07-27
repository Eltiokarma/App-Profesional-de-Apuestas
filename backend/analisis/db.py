"""efe.db — almacenamiento de la capa de análisis EFE+DTP.

Tres niveles (ver docs/efe-dtp/PLAN_ADAPTADO.md):
  investigacion  hechos por equipo con TTL por tipo (la despensa)
  analisis       veredictos por partido, inmutables, con versión EFE
  cadena_dtp     la película por equipo foco (apertura → cierre → lección)
  casos_validacion  casos numerados que calibran versiones del protocolo

Vive junto a las demás DBs (SAD_DATA_DIR / volumen de Railway). WAL para
convivir con las lecturas del backend.
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

from backend import db as saddb

DDL = """
CREATE TABLE IF NOT EXISTS investigacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo TEXT NOT NULL,
    tipo TEXT NOT NULL,
    contenido TEXT NOT NULL,
    fuentes TEXT,
    capturado_en TEXT NOT NULL,
    UNIQUE (equipo, tipo)
);
CREATE TABLE IF NOT EXISTS analisis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    fixture_id INTEGER,
    equipo_a TEXT, equipo_b TEXT, fecha_partido TEXT,
    estado TEXT NOT NULL DEFAULT 'preliminar',
    resultado_json TEXT NOT NULL,
    version_efe TEXT DEFAULT '1.5',
    creado_en TEXT NOT NULL,
    UNIQUE (tipo, fixture_id, estado)
);
CREATE INDEX IF NOT EXISTS idx_analisis_fixture ON analisis(fixture_id);
CREATE TABLE IF NOT EXISTS cadena_dtp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_foco TEXT NOT NULL,
    partido_n INTEGER NOT NULL,
    rival TEXT, fecha TEXT, fixture_id INTEGER,
    apertura_json TEXT, cierre_json TEXT, registro TEXT,
    UNIQUE (equipo_foco, partido_n)
);
CREATE TABLE IF NOT EXISTS casos_validacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caso_num INTEGER, partido TEXT, fecha TEXT,
    que_acerto TEXT, que_fallo TEXT, correccion_derivada TEXT
);
"""


def ruta() -> str:
    return os.path.join(saddb.BASE_DIR, "efe.db")


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(ruta())
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=15000")
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(DDL)
    return con


def ahora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ── analisis ────────────────────────────────────────────────────────────────

def analisis_de_fixture(fixture_id: int) -> list[dict]:
    with conectar() as con:
        filas = con.execute(
            "SELECT tipo, fixture_id, estado, resultado_json, version_efe, creado_en "
            "FROM analisis WHERE fixture_id=? ORDER BY creado_en",
            (fixture_id,),
        ).fetchall()
    # ESTA es la ruta que alimenta el dashboard (/analisis/partido/{id}): la
    # autocuración de análisis vacíos tiene que correr también aquí, no solo
    # en analisis_existente — si no, el dashboard sigue pintando el vacío.
    buenos: list[dict] = []
    for f in filas:
        dto = _fila_a_dto(f)
        if _es_vacio(dto):
            _purgar(dto["tipo"], fixture_id, dto["estado"])
        else:
            buenos.append(dto)
    return buenos


def borrar_analisis(tipo: str, fixture_id: int) -> None:
    """Descarta TODOS los análisis del fixture (preliminar y confirmado) —
    la base del botón «Regenerar»."""
    with conectar() as con:
        con.execute("DELETE FROM analisis WHERE tipo=? AND fixture_id=?", (tipo, fixture_id))
        con.commit()


def analisis_existente(tipo: str, fixture_id: int, estado: str) -> dict | None:
    with conectar() as con:
        f = con.execute(
            "SELECT tipo, fixture_id, estado, resultado_json, version_efe, creado_en "
            "FROM analisis WHERE tipo=? AND fixture_id=? AND estado=?",
            (tipo, fixture_id, estado),
        ).fetchone()
    if not f:
        return None
    dto = _fila_a_dto(f)
    if _es_vacio(dto):
        _purgar(tipo, fixture_id, estado)
        return None
    return dto


def _es_vacio(dto: dict) -> bool:
    """Autocuración: un análisis guardado sin contenido (EFE en ceros o
    timeline sin eventos) no vale como caché — se detecta para purgarlo y
    que el usuario pueda regenerar."""
    from backend.analisis.esquemas import analisis_vacio, timeline_vacio
    if dto["tipo"] == "efe":
        return analisis_vacio(dto["resultado"])
    if dto["tipo"] == "timeline":
        return timeline_vacio(dto["resultado"])
    return False


def _purgar(tipo: str, fixture_id: int, estado: str) -> None:
    with conectar() as con:
        con.execute("DELETE FROM analisis WHERE tipo=? AND fixture_id=? AND estado=?",
                    (tipo, fixture_id, estado))
        con.commit()
    print(f"[{tipo}] fixture {fixture_id}: análisis vacío purgado (regenerable)", flush=True)


def guardar_analisis(tipo: str, fixture_id: int, equipo_a: str, equipo_b: str,
                     fecha_partido: str, estado: str, resultado: dict,
                     version_efe: str) -> dict:
    with conectar() as con:
        con.execute(
            "INSERT OR REPLACE INTO analisis (tipo, fixture_id, equipo_a, equipo_b, "
            "fecha_partido, estado, resultado_json, version_efe, creado_en) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (tipo, fixture_id, equipo_a, equipo_b, fecha_partido, estado,
             json.dumps(resultado, ensure_ascii=False), version_efe, ahora()),
        )
        con.commit()
    return analisis_existente(tipo, fixture_id, estado)  # type: ignore[return-value]


def _fila_a_dto(f: sqlite3.Row) -> dict:
    return {
        "tipo": f["tipo"],
        "fixtureId": f["fixture_id"],
        "estado": f["estado"],
        "versionEfe": f["version_efe"],
        "creadoEn": f["creado_en"].replace(" ", "T") + "Z",
        "resultado": json.loads(f["resultado_json"]),
    }


# ── investigacion (despensa con TTL por tipo, en horas) ─────────────────────

# La despensa se rellena en BARRIDOS periódicos (docs/DESPENSA_DESKTOP.md), así
# que el TTL se DERIVA de esa cadencia en vez de fijarse a ojo: un TTL más corto
# que el barrido abre una ventana en la que la despensa ya venció y el barrido
# todavía no llegó — y ese día TODO EFE sale caro. El margen absorbe además que
# un barrido se atrase un día o dos, que es lo normal cuando lo dispara una
# persona.
_CADENCIA_DIAS = max(1, int(os.environ.get("SAD_DESPENSA_CADENCIA_DIAS", "15")))
_MARGEN_DIAS = 2
# SAD_DESPENSA_TTL_DIAS sigue mandando si alguien lo fija explícitamente.
_TTL_DIAS = max(1, int(os.environ.get("SAD_DESPENSA_TTL_DIAS", "0") or 0)
                or _CADENCIA_DIAS + _MARGEN_DIAS)

TTL_HORAS = {
    "dt": _TTL_DIAS * 24,
    "plantel": _TTL_DIAS * 24,
    "tabla": 24,
    "resultados": 24,
    "fixture": 7 * 24,
    "xi_reciente": 48,
    "bajas": 48,
    # cronología del modo timeline (cargable desde el escritorio): los eventos
    # institucionales/técnicos no caducan rápido
    "timeline_eventos": 72,
}

# GRACIA: aun con el TTL alineado, un barrido que no se corre deja la despensa
# vencida y el EFE volvería a pagar búsquedas. Para los tipos que SOLO da la web
# (dt, plantel), un dato vencido pero reciente se sigue sirviendo —declarando su
# edad— durante un ciclo más de barrido: un plantel de hace tres semanas es peor
# que uno de ayer, pero es MUCHO mejor que gastar en buscarlo, y decir su edad
# deja que el análisis lo descuente. Pasada la gracia vuelve a contar como
# faltante: servir un dato viejo sin límite sí sería mentir.
#
# El resto no lleva gracia y no la necesita: tabla/resultados/fixture salen de
# sad.db y xi_reciente/bajas de API-Football, así que nunca dependen de esto.
GRACIA_HORAS = {"dt": _CADENCIA_DIAS * 24, "plantel": _CADENCIA_DIAS * 24}

# TIPOS del protocolo EFE: lo que el EFE investiga/consume. timeline_eventos
# es del modo timeline — NO debe entrar aquí o el EFE lo contaría faltante.
TIPOS = tuple(t for t in TTL_HORAS if t != "timeline_eventos")


def _nota_edad(contenido, dias: int):
    """Marca un dato añejo con su edad. Solo tiene sentido en texto (que es lo
    que guarda el EFE); cualquier otra forma se devuelve intacta antes que
    corromperla por adornarla."""
    if not isinstance(contenido, str) or not contenido.strip():
        return contenido
    return (f"[dato de hace {dias} días, sin refrescar desde el último barrido: "
            f"tómalo con reserva y NO lo des por confirmado] {contenido}")


def investigacion_de(equipo: str) -> tuple[dict, list[str]]:
    """({tipo: contenido} utilizable, [tipos ausentes o demasiado viejos]).

    Lo añejo-pero-servible entra en el primero (con su edad declarada) y NO en
    el segundo: los faltantes son los que disparan búsqueda web, y por tanto el
    gasto."""
    frescos, faltantes, _ = investigacion_detallada(equipo)
    return frescos, faltantes


def investigacion_detallada(equipo: str) -> tuple[dict, list[str], dict[str, int]]:
    """Igual que `investigacion_de` + {tipo: días de antigüedad} de lo que se
    sirvió pasado su TTL, para poder decirlo en el prompt y en el log."""
    with conectar() as con:
        filas = con.execute(
            "SELECT tipo, contenido, capturado_en FROM investigacion WHERE equipo=?",
            (equipo,),
        ).fetchall()
    ahora_dt = datetime.now(timezone.utc)
    frescos: dict = {}
    anejos: dict[str, int] = {}
    for f in filas:
        tipo = f["tipo"]
        capturado = datetime.strptime(f["capturado_en"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        edad_h = (ahora_dt - capturado).total_seconds() / 3600
        ttl = TTL_HORAS.get(tipo, 24)
        if edad_h <= ttl:
            frescos[tipo] = json.loads(f["contenido"])
        elif edad_h <= ttl + GRACIA_HORAS.get(tipo, 0):
            dias = int(edad_h // 24)
            frescos[tipo] = _nota_edad(json.loads(f["contenido"]), dias)
            anejos[tipo] = dias
    faltantes = [t for t in TIPOS if t not in frescos]
    return frescos, faltantes, anejos


def guardar_investigacion(equipo: str, tipo: str, contenido: dict | list,
                          fuentes: list[str] | None = None) -> None:
    with conectar() as con:
        con.execute(
            "INSERT OR REPLACE INTO investigacion (equipo, tipo, contenido, fuentes, capturado_en) "
            "VALUES (?, ?, ?, ?, ?)",
            (equipo, tipo, json.dumps(contenido, ensure_ascii=False),
             json.dumps(fuentes or [], ensure_ascii=False), ahora()),
        )
        con.commit()


# ── cadena_dtp (la película por equipo foco) ────────────────────────────────

def guardar_cadena(equipo_foco: str, partido_n: int, rival: str, fecha: str | None,
                   fixture_id: int, apertura: dict | None,
                   cierre: dict | None = None, registro: dict | None = None) -> None:
    """Una fila por (equipo_foco, N). La apertura se escribe ANTES del partido;
    el cierre, después. Nunca se pisa una apertura ya escrita con otra
    posterior al partido: eso convertiría el pronóstico en hindsight."""
    with conectar() as con:
        previa = con.execute(
            "SELECT apertura_json, cierre_json, registro FROM cadena_dtp "
            "WHERE equipo_foco=? AND partido_n=?",
            (equipo_foco, partido_n),
        ).fetchone()
        apertura_txt = None
        if previa and previa["apertura_json"]:
            apertura_txt = previa["apertura_json"]   # la de antes manda
        elif apertura is not None:
            apertura_txt = json.dumps(apertura, ensure_ascii=False)
        con.execute(
            "INSERT OR REPLACE INTO cadena_dtp (equipo_foco, partido_n, rival, fecha, "
            "fixture_id, apertura_json, cierre_json, registro) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (equipo_foco, partido_n, rival, fecha, fixture_id, apertura_txt,
             json.dumps(cierre, ensure_ascii=False) if cierre is not None else
             (previa["cierre_json"] if previa else None),
             json.dumps(registro, ensure_ascii=False) if registro is not None else
             (previa["registro"] if previa else None)),
        )
        con.commit()


def _fila_cadena(f) -> dict:
    return {
        "equipoFoco": f["equipo_foco"],
        "partidoN": f["partido_n"],
        "rival": f["rival"],
        "fecha": f["fecha"],
        "fixtureId": f["fixture_id"],
        "apertura": json.loads(f["apertura_json"]) if f["apertura_json"] else None,
        "cierre": json.loads(f["cierre_json"]) if f["cierre_json"] else None,
        "registro": json.loads(f["registro"]) if f["registro"] else None,
    }


def cadena_de(equipo_foco: str, limite: int = 20) -> list[dict]:
    """La película del equipo, del partido más reciente hacia atrás."""
    with conectar() as con:
        filas = con.execute(
            "SELECT * FROM cadena_dtp WHERE equipo_foco=? ORDER BY partido_n DESC LIMIT ?",
            (equipo_foco, limite),
        ).fetchall()
    return [_fila_cadena(f) for f in filas]


def eslabon(equipo_foco: str, partido_n: int) -> dict | None:
    with conectar() as con:
        f = con.execute(
            "SELECT * FROM cadena_dtp WHERE equipo_foco=? AND partido_n=?",
            (equipo_foco, partido_n),
        ).fetchone()
    return _fila_cadena(f) if f else None


def eslabon_de_fixture(equipo_foco: str, fixture_id: int) -> dict | None:
    with conectar() as con:
        f = con.execute(
            "SELECT * FROM cadena_dtp WHERE equipo_foco=? AND fixture_id=?",
            (equipo_foco, fixture_id),
        ).fetchone()
    return _fila_cadena(f) if f else None
