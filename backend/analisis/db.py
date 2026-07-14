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
    return [_fila_a_dto(f) for f in filas]


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
    # Autocuración: un EFE guardado sin contenido (ambos equipos en 0 — bug de
    # versiones anteriores) se borra para que el usuario pueda regenerarlo.
    if tipo == "efe":
        from backend.analisis.esquemas import analisis_vacio
        if analisis_vacio(dto["resultado"]):
            with conectar() as con:
                con.execute("DELETE FROM analisis WHERE tipo=? AND fixture_id=? AND estado=?",
                            (tipo, fixture_id, estado))
                con.commit()
            print(f"[efe] fixture {fixture_id}: análisis vacío purgado (regenerable)", flush=True)
            return None
    return dto


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

TTL_HORAS = {
    "dt": 14 * 24,
    "plantel": 14 * 24,
    "tabla": 24,
    "resultados": 24,
    "fixture": 7 * 24,
    "xi_reciente": 48,
    "bajas": 48,
}
TIPOS = tuple(TTL_HORAS)


def investigacion_de(equipo: str) -> tuple[dict, list[str]]:
    """Devuelve ({tipo: contenido} fresco, [tipos vencidos o ausentes])."""
    with conectar() as con:
        filas = con.execute(
            "SELECT tipo, contenido, capturado_en FROM investigacion WHERE equipo=?",
            (equipo,),
        ).fetchall()
    ahora_dt = datetime.now(timezone.utc)
    frescos: dict = {}
    for f in filas:
        capturado = datetime.strptime(f["capturado_en"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        edad_h = (ahora_dt - capturado).total_seconds() / 3600
        if edad_h <= TTL_HORAS.get(f["tipo"], 24):
            frescos[f["tipo"]] = json.loads(f["contenido"])
    faltantes = [t for t in TIPOS if t not in frescos]
    return frescos, faltantes


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
