"""Incidencias de las corridas: lo que vio roto el pipeline, para que alguien lo arregle.

Cada corrida (partes, veredictos, reventones) termina con un «Roto o a mirar»
que hasta el 18/10/2026 vivía solo en el chat de su sesión: el usuario lo
copiaba a mano a otra conversación y un humano decidía qué era bug, qué era
dato de la API y qué estaba bien así. Eso no escala y se pierde (pedido del
usuario, 18/10/2026: «estos parches automatizados como el parte y el
veredicto; la API siempre puede fallar y van a aparecer errores nuevos»).

Ahora la corrida deposita cada hallazgo acá, estructurado, y la rutina de
MANTENIMIENTO (`corrida-sad`, modo `mantenimiento`) los lee, los verifica
contra la base, arregla lo que es código con tests y marca cada uno con lo que
se hizo. Lo que no se arregla también queda dicho: `dato_api` (la API trajo
algo malo y no hay código que lo evite), `por_diseno` (funciona como se
decidió) o `usuario` (le toca a una persona: una variable de Railway, una
cuarentena con la llave maestra).

Una incidencia que se repite NO se duplica: mismo título normalizado (y mismo
partido, si lo trae) suma `veces` y actualiza `ultimaVez` mientras siga
abierta. Que algo se repita es la señal de que el parche no alcanzó.
"""
from __future__ import annotations

import re
import unicodedata

from backend.analisis import db as efedb

ORIGENES = ("partes", "veredictos", "reventones", "mantenimiento", "usuario")
AREAS = ("dt", "once", "ficha", "tde", "dtp", "f1", "timeline", "reventon", "burbujas", "agenda",
         "latido", "cuotas", "api", "contrato", "skill", "aprendizaje", "otro")
SEVERIDADES = ("bloquea", "error", "aviso")
ESTADOS = ("abierta", "en_curso", "resuelta", "dato_api", "por_diseno", "usuario", "descartada")
CERRADOS = ("resuelta", "dato_api", "por_diseno", "descartada")

DDL = """
CREATE TABLE IF NOT EXISTS incidencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL,
    origen TEXT NOT NULL,
    corrida TEXT,
    fixture_id INTEGER,
    area TEXT NOT NULL,
    severidad TEXT NOT NULL,
    titulo TEXT NOT NULL,
    detalle TEXT,
    estado TEXT NOT NULL DEFAULT 'abierta',
    resolucion TEXT,
    pr TEXT,
    veces INTEGER NOT NULL DEFAULT 1,
    creado_en TEXT NOT NULL,
    ultima_vez TEXT NOT NULL,
    cerrado_en TEXT
);
CREATE INDEX IF NOT EXISTS idx_incidencia_estado ON incidencia(estado);
CREATE INDEX IF NOT EXISTS idx_incidencia_clave ON incidencia(clave);
"""


class IncidenciaInvalida(ValueError):
    pass


def _con():
    con = efedb.conectar()
    con.executescript(DDL)
    return con


def _txt(x, tope: int = 4000) -> str:
    return str(x or "").strip()[:tope]


def clave_de(titulo: str, fixture_id: int | None) -> str:
    """El mismo hallazgo escrito dos veces con otras mayúsculas o tildes es uno."""
    t = unicodedata.normalize("NFKD", titulo or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return f"{fixture_id or 0}:{' '.join(t.split())[:160]}"


def depositar(payload: dict) -> dict:
    """`{origen, corrida?, items: [{titulo, area, severidad?, detalle?, fixtureId?}]}`.
    Devuelve qué entró nuevo, qué se sumó a una abierta y qué se rechazó."""
    origen = _txt(payload.get("origen")).lower()
    if origen not in ORIGENES:
        raise IncidenciaInvalida(f"origen {origen!r} desconocido: {' · '.join(ORIGENES)}")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise IncidenciaInvalida("`items` tiene que ser una lista con al menos una incidencia")
    corrida = _txt(payload.get("corrida"), 120)
    ahora = efedb.ahora()
    nuevas, repetidas, rechazos = [], [], []
    with _con() as con:
        for i, it in enumerate(items[:60]):
            if not isinstance(it, dict):
                rechazos.append({"donde": f"items[{i}]", "porque": "cada incidencia es un objeto"})
                continue
            titulo = _txt(it.get("titulo"), 300)
            area = _txt(it.get("area")).lower() or "otro"
            sev = _txt(it.get("severidad")).lower() or "error"
            if not titulo:
                rechazos.append({"donde": f"items[{i}].titulo", "porque": "sin título no hay incidencia"})
                continue
            if area not in AREAS:
                rechazos.append({"donde": f"items[{i}].area", "porque": f"{area!r} no está en la lista: queda «otro»",
                                 "esperado": " · ".join(AREAS)})
                area = "otro"
            if sev not in SEVERIDADES:
                rechazos.append({"donde": f"items[{i}].severidad", "porque": f"{sev!r} no está en la lista: queda «error»",
                                 "esperado": " · ".join(SEVERIDADES)})
                sev = "error"
            try:
                fid = int(it["fixtureId"]) if it.get("fixtureId") not in (None, "") else None
            except (TypeError, ValueError):
                fid = None
            clave = clave_de(titulo, fid)
            fila = con.execute(
                f"SELECT id FROM incidencia WHERE clave=? AND estado NOT IN ({','.join('?' * len(CERRADOS))})",
                (clave, *CERRADOS)).fetchone()
            if fila:
                con.execute("UPDATE incidencia SET veces=veces+1, ultima_vez=?, detalle=COALESCE(NULLIF(?, ''), detalle) "
                            "WHERE id=?", (ahora, _txt(it.get("detalle")), fila["id"]))
                repetidas.append(fila["id"])
                continue
            cur = con.execute(
                "INSERT INTO incidencia (clave, origen, corrida, fixture_id, area, severidad, titulo, detalle, "
                "creado_en, ultima_vez) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (clave, origen, corrida, fid, area, sev, titulo, _txt(it.get("detalle")), ahora, ahora))
            nuevas.append(cur.lastrowid)
    return {"nuevas": nuevas, "repetidas": repetidas, "rechazos": rechazos}


def _dto(r) -> dict:
    return {"id": r["id"], "origen": r["origen"], "corrida": r["corrida"] or "", "fixtureId": r["fixture_id"],
            "area": r["area"], "severidad": r["severidad"], "titulo": r["titulo"], "detalle": r["detalle"] or "",
            "estado": r["estado"], "resolucion": r["resolucion"] or "", "pr": r["pr"] or "",
            "veces": r["veces"], "creadoEn": r["creado_en"], "ultimaVez": r["ultima_vez"],
            "cerradoEn": r["cerrado_en"]}


def listar(estado: str | None = "abierta", limite: int = 200) -> dict:
    """Por defecto las abiertas (lo que el mantenimiento tiene que mirar),
    las más repetidas y graves primero. `estado=todas` trae todo."""
    with _con() as con:
        if estado and estado != "todas":
            filas = con.execute(
                "SELECT * FROM incidencia WHERE estado=? ORDER BY "
                "CASE severidad WHEN 'bloquea' THEN 0 WHEN 'error' THEN 1 ELSE 2 END, veces DESC, id "
                "LIMIT ?", (estado, limite)).fetchall()
        else:
            filas = con.execute("SELECT * FROM incidencia ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
        conteo = {r["estado"]: r["n"] for r in con.execute(
            "SELECT estado, COUNT(*) AS n FROM incidencia GROUP BY estado")}
    return {"incidencias": [_dto(r) for r in filas], "porEstado": conteo,
            "nota": ("abierta = sin mirar · en_curso = alguien la está arreglando · resuelta = con PR · "
                     "dato_api = la API trajo algo malo y no hay código que lo evite · por_diseno = "
                     "funciona como se decidió · usuario = le toca a una persona · descartada = no era")}


def cambiar_estado(inc_id: int, payload: dict) -> dict:
    estado = _txt(payload.get("estado")).lower()
    if estado not in ESTADOS:
        raise IncidenciaInvalida(f"estado {estado!r} desconocido: {' · '.join(ESTADOS)}")
    resolucion = _txt(payload.get("resolucion"))
    if estado != "en_curso" and estado != "abierta" and not resolucion:
        # cerrar sin decir qué se hizo es esconderla
        raise IncidenciaInvalida("para cerrar o derivar una incidencia hace falta `resolucion`: qué se hizo o por qué")
    ahora = efedb.ahora()
    with _con() as con:
        fila = con.execute("SELECT * FROM incidencia WHERE id=?", (inc_id,)).fetchone()
        if not fila:
            raise KeyError(inc_id)
        con.execute("UPDATE incidencia SET estado=?, resolucion=COALESCE(NULLIF(?, ''), resolucion), "
                    "pr=COALESCE(NULLIF(?, ''), pr), cerrado_en=? WHERE id=?",
                    (estado, resolucion, _txt(payload.get("pr"), 300),
                     ahora if estado in CERRADOS else None, inc_id))
        fila = con.execute("SELECT * FROM incidencia WHERE id=?", (inc_id,)).fetchone()
    return _dto(fila)


def resumen_latido() -> dict:
    """Para el latido: cuántas abiertas, cuántas bloquean y la más vieja."""
    with _con() as con:
        abiertas = con.execute("SELECT COUNT(*) AS n, SUM(severidad='bloquea') AS b, MIN(creado_en) AS v "
                               "FROM incidencia WHERE estado IN ('abierta', 'en_curso')").fetchone()
        usuario = con.execute("SELECT COUNT(*) AS n FROM incidencia WHERE estado='usuario'").fetchone()
    return {"abiertas": abiertas["n"] or 0, "bloquean": abiertas["b"] or 0,
            "masVieja": abiertas["v"], "esperanAlUsuario": usuario["n"] or 0}
