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

Una incidencia que se repite NO se duplica: la MISMA CAUSA —misma área y mismo
título normalizado, sin lo que va entre paréntesis ni lo que sigue a «:»—
suma `veces`, actualiza `ultimaVez` y agrega el partido a `fixtures` mientras
siga abierta. Hasta el 20/10/2026 la clave llevaba el partido: «titular de la
ficha sin jugadorId» en diez partidos eran diez incidencias, la cola llegó a
254 y no se veía cuántas causas había detrás. Que algo se repita es la señal
de que el parche no alcanzó.
"""
from __future__ import annotations

import json
import re
import unicodedata

from backend.analisis import db as efedb

ORIGENES = ("partes", "veredictos", "reventones", "mantenimiento", "usuario")
AREAS = ("dt", "once", "ficha", "tde", "dtp", "f1", "timeline", "reventon", "burbujas", "agenda",
         "latido", "cuotas", "api", "contrato", "skill", "aprendizaje", "otro")
SEVERIDADES = ("bloquea", "error", "aviso")
# `aprobada`: el usuario aprobó la propuesta de una `usuario` y el mantenimiento
# la implementa (solo se llega con `decidir`, nunca con el token de Cowork);
# `por_desplegar`: el PR está mergeado pero producción todavía no corre ese
# commit (27/10/2026: el 21-22/10 Railway estuvo caído y un push se perdió).
ESTADOS = ("abierta", "en_curso", "resuelta", "dato_api", "por_diseno", "usuario", "descartada",
           "aprobada", "por_desplegar")
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
    cerrado_en TEXT,
    fixtures TEXT
);
CREATE INDEX IF NOT EXISTS idx_incidencia_estado ON incidencia(estado);
CREATE INDEX IF NOT EXISTS idx_incidencia_clave ON incidencia(clave);
"""


class IncidenciaInvalida(ValueError):
    pass


def _con():
    con = efedb.conectar()
    con.executescript(DDL)
    cols = {r[1] for r in con.execute("PRAGMA table_info(incidencia)")}
    if "fixtures" not in cols:   # tabla de antes del 20/10/2026: se agrupa una vez por causa
        con.execute("ALTER TABLE incidencia ADD COLUMN fixtures TEXT")
        reagrupar(con)
    # claves de antes del 21/10/2026 («area:titulo»): las abiertas se reagrupan
    # una vez con la clave sin área (la nueva nunca lleva «:»)
    elif con.execute(f"SELECT 1 FROM incidencia WHERE clave LIKE '%:%' AND estado NOT IN "
                     f"({','.join('?' * len(CERRADOS))}) LIMIT 1", CERRADOS).fetchone():
        reagrupar(con)
    return con


def reagrupar(con) -> int:
    """Funde las abiertas que son la misma causa (clave nueva): la más vieja
    queda con la suma de `veces` y los partidos de todas; las otras pasan a
    `descartada` con «agrupada en #N» —no se borra nada—. Devuelve cuántas
    se fundieron."""
    marcas = ",".join("?" * len(CERRADOS))
    filas = con.execute(f"SELECT * FROM incidencia WHERE estado NOT IN ({marcas}) ORDER BY id",
                        CERRADOS).fetchall()
    grupos: dict[str, list] = {}
    for r in filas:
        grupos.setdefault(clave_de(r["titulo"]), []).append(r)
    fundidas, ahora = 0, efedb.ahora()
    for clave, rs in grupos.items():
        base, resto = rs[0], rs[1:]
        fx = _fixtures(base)
        for r in resto:
            fx += [f for f in _fixtures(r) if f not in fx]
        con.execute("UPDATE incidencia SET clave=?, veces=?, ultima_vez=?, fixtures=? WHERE id=?",
                    (clave, sum(r["veces"] for r in rs), max(r["ultima_vez"] for r in rs),
                     json.dumps(fx[-50:]), base["id"]))
        for r in resto:
            con.execute("UPDATE incidencia SET estado='descartada', resolucion=?, cerrado_en=? WHERE id=?",
                        (f"agrupada en #{base['id']} (misma causa)", ahora, r["id"]))
            fundidas += 1
    con.commit()
    return fundidas


def _fixtures(r) -> list[int]:
    try:
        lst = json.loads(r["fixtures"]) if r["fixtures"] else []
    except (ValueError, TypeError):
        lst = []
    if r["fixture_id"] and r["fixture_id"] not in lst:
        lst.insert(0, r["fixture_id"])
    return lst


def _txt(x, tope: int = 4000) -> str:
    return str(x or "").strip()[:tope]


def clave_de(titulo: str, area: str = "") -> str:
    """La causa, no el caso: el mismo hallazgo con otras mayúsculas, tildes, otro
    partido entre paréntesis o otro detalle después de «:» es uno.

    EL ÁREA NO ENTRA EN LA CLAVE (21/10/2026). La elige quien deposita y dos
    subagentes ponen otra al mismo hallazgo: «Faltan partidos domésticos…» del
    AEK entró como `ficha` (298) y como `agenda` (333), dos abiertas para una
    causa. El área queda como dato de la incidencia; `area` se acepta y se
    ignora para no romper a quien llama."""
    t = re.sub(r"\([^)]*\)", " ", titulo or "").split(":")[0]
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return " ".join(t.split())[:160]


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
            clave = clave_de(titulo, area)
            fila = con.execute(
                f"SELECT * FROM incidencia WHERE clave=? AND estado NOT IN ({','.join('?' * len(CERRADOS))})",
                (clave, *CERRADOS)).fetchone()
            if fila:
                fx = _fixtures(fila)
                if fid and fid not in fx:
                    fx.append(fid)
                con.execute("UPDATE incidencia SET veces=veces+1, ultima_vez=?, detalle=COALESCE(NULLIF(?, ''), detalle), "
                            "fixtures=? WHERE id=?",
                            (ahora, _txt(it.get("detalle")), json.dumps(fx[-50:]), fila["id"]))
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
            "cerradoEn": r["cerrado_en"], "fixtures": _fixtures(r)}


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
        todas = con.execute("SELECT * FROM incidencia").fetchall() if any(
            r["estado"] not in CERRADOS for r in filas) else []
    # LA PISTA DE LA CAUSA CONOCIDA: a cada una sin cerrar, la última cerrada de
    # su familia (27/10/2026: se re-investigaba lo ya clasificado)
    conocida: dict[int, dict] = {}
    for fam in _familias(todas):
        cerradas = [r for r in fam if r["estado"] in CERRADOS]
        if not cerradas:
            continue
        ult = _conocida(max(cerradas, key=lambda r: (r["cerrado_en"] or "", r["id"])))
        for r in fam:
            if r["estado"] not in CERRADOS:
                conocida[r["id"]] = ult
    return {"incidencias": [{**_dto(r), "conocida": conocida.get(r["id"])} for r in filas], "porEstado": conteo,
            "nota": ("abierta = sin mirar · en_curso = alguien la está arreglando · resuelta = con PR · "
                     "dato_api = la API trajo algo malo y no hay código que lo evite · por_diseno = "
                     "funciona como se decidió · usuario = le toca a una persona · descartada = no era · "
                     "aprobada = el usuario aprobó la propuesta: la implementa el mantenimiento · "
                     "por_desplegar = PR mergeado que producción todavía no corre")}


def cambiar_estado(inc_id: int, payload: dict) -> dict:
    estado = _txt(payload.get("estado")).lower()
    if estado not in ESTADOS:
        raise IncidenciaInvalida(f"estado {estado!r} desconocido: {' · '.join(ESTADOS)}")
    if estado == "aprobada":
        # aprobar es del usuario, con la llave maestra: POST …/decision
        raise IncidenciaInvalida("`aprobada` la pone el usuario con POST …/incidencias/{id}/decision")
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
        n = {r["estado"]: r["n"] for r in con.execute(
            "SELECT estado, COUNT(*) AS n FROM incidencia WHERE estado IN ('usuario', 'aprobada', 'por_desplegar') "
            "GROUP BY estado")}
    return {"abiertas": abiertas["n"] or 0, "bloquean": abiertas["b"] or 0,
            "masVieja": abiertas["v"], "esperanAlUsuario": n.get("usuario", 0),
            "aprobadas": n.get("aprobada", 0), "porDesplegar": n.get("por_desplegar", 0)}


# ── LA MISMA CAUSA CON OTRAS PALABRAS (27/10/2026, pedido del usuario) ──────
# La clave exacta junta lo que se escribe igual; las corridas escriben la misma
# causa de muchas formas («Fecha de llegada del DT mal en la base…», «…no casa
# con la prensa»): 19 incidencias de 18 partidos, cada una verificada desde
# cero y cerrada como dato_api. La familia las junta por las palabras que
# comparten (raíz de 6 letras, sin vacías): una pista para no investigar dos
# veces y la cuenta que hace visible lo que se repite. NO cierra nada sola.
_VACIAS = set("de del la las el los un una unos unas y o en con sin por para que se su sus al lo a no es "
              "mas como cuando desde ya le les otro otra".split())
SIMILITUD = 0.6        # palabras compartidas sobre las del título más corto
COMPARTIDAS_MIN = 3    # y al menos tres: dos títulos cortos no se juntan por «DT» y «base»
RECURRENTE_FIXTURES = 3


def _toks(titulo: str) -> frozenset:
    t = re.sub(r"\([^)]*\)", " ", titulo or "")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return frozenset(w[:6] for w in re.sub(r"[^a-z0-9 ]+", " ", t).split() if len(w) >= 3 and w not in _VACIAS)


def parecidos(a: frozenset, b: frozenset) -> bool:
    comunes = len(a & b)
    corto = min(len(a), len(b))
    return corto >= COMPARTIDAS_MIN and comunes >= COMPARTIDAS_MIN and comunes / corto >= SIMILITUD


def _agrupada(r) -> bool:
    return r["estado"] == "descartada" and "agrupada en #" in (r["resolucion"] or "")


def _familias(filas) -> list[list]:
    """Por orden de id: cada incidencia entra en la primera familia cuya raíz
    (o una de sus primeras cinco) se le parece. Las «agrupada en #N» no cuentan."""
    fams: list[tuple[list, list]] = []
    for r in sorted(filas, key=lambda r: r["id"]):
        if _agrupada(r):
            continue
        t = _toks(r["titulo"])
        destino = next((f for f in fams if parecidos(t, f[1][0]) or any(parecidos(t, x) for x in f[1][1:5])), None)
        if destino:
            destino[0].append(r)
            destino[1].append(t)
        else:
            fams.append(([r], [t]))
    return [f[0] for f in fams]


def _conocida(r) -> dict:
    return {"id": r["id"], "estado": r["estado"], "titulo": r["titulo"], "resolucion": r["resolucion"] or "",
            "pr": r["pr"] or "", "cerradoEn": r["cerrado_en"]}


def causas(solo_recurrentes: bool = False) -> dict:
    """Las familias de causa, con lo que hace falta para decidir:

    - `conocida`: la última cerrada de la familia (dato_api · por_diseno ·
      descartada · resuelta), con su resolución: una nueva parecida se cierra
      remitiendo a ella sin volver a investigar, salvo que traiga algo nuevo;
    - `recurrente`: un dato de la API que ya pasó en 3+ partidos distintos y
      nadie decidió nada: va al usuario con una regla de código propuesta
      (como 381 y 673, que se convirtieron en código a pedido suyo);
    - `reaparece`: hubo un PR (`resuelta`) y la causa volvió a reportarse
      después: el parche no alcanzó."""
    with _con() as con:
        filas = con.execute("SELECT * FROM incidencia").fetchall()
    out = []
    for fam in _familias(filas):
        fx: list[int] = []
        for r in fam:
            fx += [f for f in _fixtures(r) if f not in fx]
        estados: dict[str, int] = {}
        for r in fam:
            estados[r["estado"]] = estados.get(r["estado"], 0) + 1
        cerradas = [r for r in fam if r["estado"] in CERRADOS]
        ultima = max(cerradas, key=lambda r: (r["cerrado_en"] or "", r["id"])) if cerradas else None
        fx_dato = []
        for r in fam:
            if r["estado"] == "dato_api":
                fx_dato += [f for f in _fixtures(r) if f not in fx_dato]
        decidida = any(r["estado"] in ("usuario", "aprobada") for r in fam)
        resueltas = [r for r in fam if r["estado"] in ("resuelta", "por_desplegar")]
        cierre_pr = max((r["cerrado_en"] or r["ultima_vez"] for r in resueltas), default=None)
        reaparece = bool(cierre_pr) and any(r["creado_en"] > cierre_pr for r in fam if r["estado"] not in CERRADOS)
        item = {
            "raiz": fam[0]["id"], "titulo": fam[0]["titulo"], "area": fam[0]["area"],
            "ids": [r["id"] for r in fam], "incidencias": len(fam), "veces": sum(r["veces"] for r in fam),
            "fixtures": len(fx), "porEstado": estados,
            "abiertas": [r["id"] for r in fam if r["estado"] in ("abierta", "en_curso")],
            "ultimaVez": max(r["ultima_vez"] for r in fam),
            "conocida": _conocida(ultima) if ultima else None,
            "recurrente": len(fx_dato) >= RECURRENTE_FIXTURES and not decidida,
            "fixturesDatoApi": len(fx_dato),
            "reaparece": reaparece,
        }
        if not solo_recurrentes or item["recurrente"] or item["reaparece"]:
            out.append(item)
    out.sort(key=lambda f: (not f["recurrente"], not f["reaparece"], -f["fixtures"], -f["veces"]))
    return {"causas": out, "total": len(out),
            "regla": (f"misma causa = {COMPARTIDAS_MIN}+ palabras compartidas y {int(SIMILITUD * 100)} % de las del "
                      f"título más corto · recurrente = dato_api en {RECURRENTE_FIXTURES}+ partidos sin decisión · "
                      "reaparece = reportada de nuevo después de un PR")}


def decidir(inc_id: int, aprobar: bool, nota: str = "") -> dict:
    """La decisión del usuario sobre una `usuario` (con la llave maestra, desde
    la app). Aprobada: el mantenimiento la implementa en su próxima pasada,
    antes que las abiertas. Rechazada: queda `por_diseno` con la decisión."""
    nota = _txt(nota, 1000)
    ahora = efedb.ahora()
    with _con() as con:
        fila = con.execute("SELECT * FROM incidencia WHERE id=?", (inc_id,)).fetchone()
        if not fila:
            raise KeyError(inc_id)
        if fila["estado"] != "usuario":
            raise IncidenciaInvalida(f"solo se decide una incidencia en `usuario` (esta está en `{fila['estado']}`)")
        previa = fila["resolucion"] or ""
        if aprobar:
            estado, res = "aprobada", f"{previa}\nAPROBADA por el usuario el {ahora[:10]}" + (f": {nota}" if nota else "")
        else:
            estado, res = "por_diseno", f"Decisión del usuario el {ahora[:10]}: NO" + (f" ({nota})" if nota else "") \
                + (f"\nPropuesta: {previa}" if previa else "")
        con.execute("UPDATE incidencia SET estado=?, resolucion=?, cerrado_en=? WHERE id=?",
                    (estado, res.strip(), ahora if estado in CERRADOS else None, inc_id))
        fila = con.execute("SELECT * FROM incidencia WHERE id=?", (inc_id,)).fetchone()
    return _dto(fila)
