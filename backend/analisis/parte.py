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
import difflib
import json
import re
import unicodedata
import sqlite3
from datetime import date as date_t, datetime, timedelta, timezone

from backend import db as saddb
from backend.analisis import bloque_f, db as efedb, veredicto as vered
from backend.analisis import coherencia as _coherencia
from backend.analisis import modo_fallo as _modo_fallo
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
CREATE TABLE IF NOT EXISTS coherencia_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL,
    evaluado_en TEXT NOT NULL,
    modo TEXT, modelo TEXT,
    preguntas INTEGER, hallazgos INTEGER, sin_confianza INTEGER,
    simulado INTEGER, error TEXT, tokens INTEGER,
    redeposito INTEGER,
    hallazgos_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_coherencia_log_fecha ON coherencia_log(evaluado_en);
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
_COLUMNAS_NUEVAS = (("veredicto_json", "TEXT"), ("cohorte", "TEXT"), ("cuarentena_json", "TEXT"),
                    ("coherencia_json", "TEXT"), ("modo_fallo_json", "TEXT"))
# el registro del revisor nació sin `via`; se añade en caliente igual
_COLUMNAS_LOG = (("via", "TEXT"),)

# ── COHORTES: de qué época del proceso es cada caso ─────────────────────────
#
# Un caso «ciego» de la primera semana se hizo con el DT viejo en 17 de 22
# equipos, el TDE sin nivel en diez partes y la agenda sin padrón: la etiqueta
# de población dice que es limpio y el insumo estaba roto. La cohorte se sella
# AL DEPOSITAR con la versión vigente del proceso y no cambia con un
# re-depósito (un parte viejo re-depositado hoy sigue siendo de su época). Lo
# anterior a la primera cohorte sellada es «rodaje». Las métricas se leen por
# cohorte; la vigente es la única que vale para calibrar.
COHORTE_RODAJE = "rodaje"
COHORTE = "c3-2026-09-23"
COHORTES = {
    COHORTE_RODAJE: "partes anteriores al 19/09/2026: DT viejo en 17 de 22 equipos, TDE sin nivel "
                    "en diez partes, agenda sin padrón. Enseñan, no calibran",
    "c2-2026-09-19": "desde el 19/09/2026: dt {nombre, desde}, niveles del TDE rechazados si "
                     "llegan mal, DT de la ingesta desde la alineación, once de la ficha con procedencia. "
                     "Todavía con la alineación RANCIA ganándole a /coachs (Santa Fe–Cali, la Roma): "
                     "referencia, no calibra",
    "c3-2026-09-23": "desde el 23/09/2026: la alineación manda en el DT solo si es de los últimos 3 "
                     "partidos (arreglo del 22/09), cuarentena automática si el DT del parte no es el "
                     "que se sentó en el banco, aviso CERCA DEL EXTREMO en el reventón",
}


def _conectar():
    con = efedb.conectar()
    con.executescript(DDL)
    for columna, tipo in _COLUMNAS_NUEVAS:
        try:
            con.execute(f"ALTER TABLE parte_cowork ADD COLUMN {columna} {tipo}")
        except sqlite3.OperationalError:
            pass  # ya existe: el caso normal a partir de la segunda conexión
    for columna, tipo in _COLUMNAS_LOG:
        try:
            con.execute(f"ALTER TABLE coherencia_log ADD COLUMN {columna} {tipo}")
        except sqlite3.OperationalError:
            pass
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


# La rúbrica del EFE nombra los roles con símbolos (🔴 🟠 🟡 ⚪) y con su
# etiqueta ("Titular fijo"), y las posiciones en español. Quien escribe el
# parte viene de leer ESA rúbrica, así que exigirle las siglas internas es
# pedirle que traduzca — y cuando se equivoca, el jugador desaparecía sin
# decir nada. Se aceptan las tres formas y se traduce aquí.
_ROL_ALIAS = {
    "TF": "TF", "🔴": "TF", "TITULAR FIJO": "TF", "FIJO": "TF",
    "TH": "TH", "🟠": "TH", "TITULAR HABITUAL": "TH", "HABITUAL": "TH",
    "ROT": "ROT", "🟡": "ROT", "ROTACION": "ROT", "ROTADOR": "ROT",
    "SUP": "SUP", "⚪": "SUP", "SUPLENTE": "SUP", "MARGINAL": "SUP",
    "SUPLENTE / MARGINAL": "SUP", "SUPLENTE/MARGINAL": "SUP",
}
_ZONA_ALIAS = {
    "GK": "GK", "POR": "GK", "PORTERO": "GK", "ARQUERO": "GK", "G": "GK", "POR.": "GK",
    "DEF": "DEF", "DEFENSA": "DEF", "D": "DEF", "ZAGUERO": "DEF", "LATERAL": "DEF",
    "CENTRAL": "DEF", "DFC": "DEF",
    "MID": "MID", "MED": "MID", "M": "MID", "MEDIO": "MID", "VOLANTE": "MID",
    "MEDIOCAMPISTA": "MID", "CENTROCAMPISTA": "MID", "MC": "MID", "PIVOTE": "MID",
    "ATK": "ATK", "DEL": "ATK", "F": "ATK", "ATA": "ATK", "ATAQUE": "ATK",
    "DELANTERO": "ATK", "EXTREMO": "ATK", "ATACANTE": "ATK", "DC": "ATK",
}


def _alias(valor, tabla: dict) -> str:
    """Traduce lo que llegó a la sigla interna. '' si no se reconoce."""
    crudo = _txt(valor)
    if not crudo:
        return ""
    for candidato in (crudo, crudo.upper(), normalizar(crudo).upper(),
                      normalizar(crudo).upper().split()[0] if normalizar(crudo).split() else ""):
        if candidato in tabla:
            return tabla[candidato]
    return ""


def _jugador(j, rechazos: list, donde: str) -> dict | None:
    if not isinstance(j, dict):
        rechazos.append({"donde": donde, "porque": f"cada jugador es un objeto, llegó {type(j).__name__}",
                         "esperado": '{"nombre": "…", "zona": "DEF", "rol": "TF", "apps": "18/20"}'})
        return None
    _claves_raras(j, _CLAVES_JUGADOR | _ECO_JUGADOR, rechazos, donde)
    nombre = _txt(j.get("nombre")) or _txt(j.get("jugador"))
    if not nombre:
        rechazos.append({"donde": donde, "porque": "sin nombre"})
        return None
    # la zona puede venir en `zona` o deducirse de `posicion`
    zona = _alias(j.get("zona"), _ZONA_ALIAS) or _alias(j.get("posicion"), _ZONA_ALIAS)
    rol = _alias(j.get("rol"), _ROL_ALIAS)
    if not zona:
        rechazos.append({"donde": donde, "jugador": nombre,
                         "porque": f"zona no reconocida: {j.get('zona')!r}",
                         "esperado": "GK / DEF / MID / ATK (o la posición en español)"})
        return None
    if not rol:
        rechazos.append({"donde": donde, "jugador": nombre,
                         "porque": f"rol no reconocido: {j.get('rol')!r}",
                         "esperado": "TF / TH / ROT / SUP (o 🔴 🟠 🟡 ⚪, o «Titular fijo»)"})
        return None
    return {"nombre": nombre, "posicion": _txt(j.get("posicion")), "zona": zona,
            "rol": rol, "apps": _txt(j.get("apps"))}


def _pron_cadena(v) -> str:
    """El pronóstico de un lado de la cadena, venga plano o como objeto."""
    if isinstance(v, dict):
        return _txt(v.get("pronostico"))
    return _txt(v)


def _bloque_crudo(v):
    """El sub-score puede venir plano (`"A": 3`) o como objeto
    (`"A": {"score": 3, "nota": "…"}`). Las dos formas son razonables si vienes
    de leer la rúbrica; antes la segunda se convertía en 0 sin avisar."""
    if isinstance(v, dict):
        # EL ECO DEL GET TRAE `declarado: false` EN LOS BLOQUES QUE NADIE
        # PUNTUÓ. Sin mirarlo, re-depositar la respuesta convertía esos huecos
        # en ceros declarados: el viaje de ida y vuelta inventaba una nota.
        if v.get("declarado") is False:
            return None, _txt(v.get("nota")), _txt(v.get("motivoExclusion") or v.get("motivo"))
        for clave in ("score", "valor", "puntaje", "subscore", "sub_score"):
            if clave in v:
                return v[clave], _txt(v.get("nota")), _txt(v.get("motivoExclusion") or v.get("motivo"))
        return None, _txt(v.get("nota")), _txt(v.get("motivoExclusion") or v.get("motivo"))
    return v, "", ""


_CLAVES_FUERA = {"nombre", "estado", "motivo", "zona", "rol", "posicion", "apps"}


def _fuera(f: dict, rechazos: list, donde: str) -> dict | None:
    """Una baja pública. Puede traer zona y rol, y conviene que los traiga.

    CORRECCIÓN de la primera versión: aquí se descartaban zona y rol "porque
    ya están en el plantel". Falso cuando el jugador NO está en la tabla F1:
    entonces la baja no pesa en el IP y desaparece del cálculo. Ahora, si trae
    zona y rol, se incorpora a la tabla para el bloque F; y si no los trae y
    tampoco está en la F1, se avisa de que no va a pesar.
    """
    if isinstance(f, str):
        f = {"nombre": f}   # una baja como «Apellido» a secas: entra, sin motivo
    if not isinstance(f, dict):
        rechazos.append({"donde": donde, "porque": f"cada baja es un objeto, llegó {type(f).__name__}",
                         "esperado": '{"nombre": "…", "estado": "baja", "motivo": "…"}'})
        return None
    _claves_raras(f, _CLAVES_FUERA, rechazos, donde)
    nombre = _txt(f.get("nombre"))
    if not nombre:
        rechazos.append({"donde": donde, "porque": "baja sin nombre"})
        return None
    estado = _txt(f.get("estado")).lower()
    return {"nombre": nombre,
            "estado": estado if estado in ("baja", "duda") else "baja",
            "motivo": _txt(f.get("motivo")),
            "zona": _alias(f.get("zona"), _ZONA_ALIAS) or _alias(f.get("posicion"), _ZONA_ALIAS),
            "rol": _alias(f.get("rol"), _ROL_ALIAS)}


_CLAVES_EQUIPO = {"nombre", "bloques", "excluidos", "notas", "dt", "perfil",
                  "plantel", "fuera", "factorX", "sensibilidad"}
_CLAVES_JUGADOR = {"nombre", "jugador", "posicion", "zona", "rol", "apps", "estado", "motivo"}
_CLAVES_PARTE = {"fixtureId", "version", "generadoEn", "equipos", "alertas", "matchup",
                 "lecturaSad", "lectura_sad", "tde", "timelineEventos", "timelineNarrativa",
                 "cadena", "documentos", "pendientes", "fuentes", "descartados", "notas",
                 "pronostico"}

# EL VIAJE DE IDA Y VUELTA. Corregir un parte es leer → modificar →
# re-depositar, así que el POST tiene que aceptar TAL CUAL lo que devuelve el
# GET. Lo que el backend calcula vuelve en la lectura como eco: no es un error
# que aparezca en el cuerpo, es que el cuerpo salió de nuestra propia
# respuesta. Se ignora en silencio; delatarlo llenaría el recibo de rechazos
# falsos y escondería los de verdad.
_ECO_PARTE = {"partido", "estado", "creadoEn", "actualizadoEn", "xi", "veredicto",
              "timeline", "rechazos", "perdido", "aviso", "entrada", "cohorte", "cuarentena",
              "xiConservados", "coherencia"}
_ECO_EQUIPO = {"total", "maximoAlcanzable", "porcentaje", "clasificacion", "disponibilidad",
               "sinBloques", "bloquesSinDeclarar", "notaTotales"}
_ECO_JUGADOR = {"soloBaja"}
# los indicadores del TDE, por bloque — para poder publicarlos en el contrato
from backend.analisis.tde import INDICADORES as _IND_TDE, INDICADORES_ISE as _IND_ISE
INDICADORES_TDE = {**_IND_TDE, "ISE": _IND_ISE}

_CLAVES_VEREDICTO = {"seleccion", "modoEvaluacion", "mancha", "falsadorCumplido",
                     "porLado", "notas", "fixtureId"}
# EL VEREDICTO TAMBIÉN TIENE QUE PODER RE-DEPOSITARSE. Su GET devuelve lo
# calculado al lado del juicio; re-postear esa respuesta —el flujo natural para
# corregir una lección— rechazaba media docena de claves propias, y una de
# ellas (`falsador`) además degradaba un `cumplido: false` guardado a `null`.
_ECO_VEREDICTO = {"acredita", "falsador", "rechazos", "cerradoEn", "objetivo",
                  "actualizadoEn", "sinPronosticoPrevio", "modoFallo"}


FUENTE_FICHA = "ficha de API-Football"   # procedencia del once que trae la ingesta
FUENTE_MANUAL = "carga manual"           # el pantallazo pegado a mano
DT_SIN_ESTABLECER = "sin establecer"   # el valor canónico de «no sé quién dirige»
_DT_DESCONOCIDO = {"", "sin establecer", "desconocido", "no establecido", "sin dato", "sin datos",
                   "n/a", "na", "?", "-", "—", "null", "none", "por confirmar", "sin confirmar"}
DT_NOMBRE_MAX = 60   # más que esto no es un nombre, es una oración
_DIAS_MES = 365.25 / 12


def _fecha(v) -> date_t | None:
    t = _txt(v)[:10]
    try:
        return datetime.strptime(t, "%Y-%m-%d").date()
    except ValueError:
        return None


def _dt_equipo(crudo, rechazos: list, lado: str, fecha_partido: str,
               entrenador_base: dict | None) -> dict:
    """El DT del bloque A: `{nombre, desde}` o `{nombre, meses}`, nunca prosa.

    Tres cosas que pasaron en el registro y que esto corta: (1) `dt` como texto
    se guardaba con `meses: 0`, y ese cero —que es «acaba de llegar»— entraba
    en A, F3 y S1 como si fuera un dato; (2) en el parte 1549491 entró una
    oración de cien caracteres como nombre; (3) un DT desconocido se escribía
    de siete formas. Ahora: `meses` manda si viene; si no, se calcula de
    `desde` a la fecha del partido; si tampoco, se toma del DT de NUESTRA base
    cuando el nombre es el mismo (así el nombre verificado en prensa no pierde
    la continuidad); y si nada de eso, `meses: null` —que no es cero—. Un
    nombre vacío o desconocido se guarda como «sin establecer», y uno más largo
    que DT_NOMBRE_MAX se rechaza: la fuente va en `notas.A`, no en el nombre.
    """
    if crudo is None:
        crudo = {}
    if isinstance(crudo, str):
        crudo = {"nombre": crudo}
    crudo = _dict(crudo, rechazos, f"equipos.{lado}.dt", '{"nombre": "…", "desde": "2025-06-15"}')
    nombre = _txt(crudo.get("nombre"))
    if len(nombre) > DT_NOMBRE_MAX or nombre.count(" ") >= 6:
        rechazos.append({
            "donde": f"equipos.{lado}.dt.nombre",
            "porque": f"eso no es un nombre, es una oración ({len(nombre)} caracteres): se guardó "
                      f"«{DT_SIN_ESTABLECER}»",
            "esperado": '`nombre` con el DT a secas ("Diego Simeone"); la fuente y el contexto '
                        'van en `notas.A`'})
        nombre = ""
    if nombre.lower() in _DT_DESCONOCIDO:
        nombre = ""
    origen = ""
    meses = None
    if crudo.get("meses") not in (None, ""):
        try:
            meses = max(0.0, min(600.0, round(float(crudo["meses"]), 1)))
            origen = "declarado"
        except (TypeError, ValueError):
            rechazos.append({"donde": f"equipos.{lado}.dt.meses",
                             "porque": f"`meses` tiene que ser un número, llegó {crudo['meses']!r}",
                             "esperado": '`meses`: 14 — o mejor `desde`: "2025-06-15" y se calcula'})
    desde = _txt(crudo.get("desde"))[:10]
    if desde and _fecha(desde) is None:
        rechazos.append({"donde": f"equipos.{lado}.dt.desde",
                         "porque": f"`desde` no es una fecha, llegó {crudo.get('desde')!r}",
                         "esperado": '"YYYY-MM-DD" (el día 01 si solo se sabe el mes)'})
        desde = ""
    partido = _fecha(fecha_partido)
    if meses is None and desde and partido:
        meses = round(max(0, (partido - _fecha(desde)).days) / _DIAS_MES, 1)
        origen = "desde"
    if meses is None and nombre and entrenador_base and entrenador_base.get("nombre"):
        # el mismo apellido que el DT de la base → su fecha de asunción sirve
        from backend.ingesta.jugadores import _norm_dt
        if _norm_dt(nombre) == _norm_dt(entrenador_base["nombre"]) and _fecha(entrenador_base.get("desde")) and partido:
            desde = desde or _txt(entrenador_base.get("desde"))[:10]
            meses = round(max(0, (partido - _fecha(entrenador_base["desde"])).days) / _DIAS_MES, 1)
            origen = "base"
    if nombre and meses is None:
        rechazos.append({
            "donde": f"equipos.{lado}.dt",
            "porque": f"el DT «{nombre}» llegó sin `desde` ni `meses` y no casa con el de la base"
                      + (f" ({entrenador_base['nombre']})" if entrenador_base and entrenador_base.get("nombre") else "")
                      + ": la antigüedad queda en null, no en cero",
            "esperado": '`desde`: "YYYY-MM-DD" (la fecha de asunción, del mes si no se sabe el día)'})
    return {"nombre": nombre or DT_SIN_ESTABLECER, "meses": meses, "desde": desde, "origenMeses": origen}


def _equipo(bruto: dict, equipos_db: list[tuple[str, str]],
            rechazos: list, lado: str, fecha_partido: str = "",
            entrenador_base: dict | None = None) -> dict:
    bruto = _dict(bruto, rechazos, f"equipos.{lado}", '{"bloques": {…}, "plantel": [...], …}')
    _claves_raras(bruto, _CLAVES_EQUIPO | _ECO_EQUIPO, rechazos, f"equipos.{lado}")
    bloques_in = _dict(bruto.get("bloques"), rechazos, f"equipos.{lado}.bloques",
                       '{"A": 3, "B": 4.5, "C": 2, "D": 3, "E": 2}')
    excluidos_in = _dict(bruto.get("excluidos"), rechazos, f"equipos.{lado}.excluidos",
                         '{"C": "motivo de la exclusión"}')
    notas_in = _dict(bruto.get("notas"), rechazos, f"equipos.{lado}.notas", '{"A": "…"}')
    bloques = {}
    for letra in LETRAS:
        crudo, nota_obj, motivo_obj = _bloque_crudo(bloques_in.get(letra))
        motivo = _txt(excluidos_in.get(letra)) or motivo_obj
        score = 0.0 if motivo else _num(crudo, MAX_BLOQUE[letra])
        # cualquier desvío entre lo que llegó y lo que se guarda se declara:
        # un 99 donde el máximo es 6 se recortaba en silencio, y un sub-score
        # recortado cambia la clasificación del equipo sin que nadie lo vea
        if not motivo and crudo is not None:
            try:
                pedido = float(crudo)
            except (TypeError, ValueError):
                rechazos.append({"donde": f"equipos.{lado}.bloques.{letra}",
                                 "porque": f"sub-score no numérico: {crudo!r}",
                                 "esperado": f"un número de 0 a {MAX_BLOQUE[letra]:g}"})
            else:
                if round(pedido, 2) != score:
                    rechazos.append({"donde": f"equipos.{lado}.bloques.{letra}",
                                     "porque": f"sub-score fuera de rango: {pedido:g} "
                                               f"(se guardó {score:g})",
                                     "esperado": f"0 a {MAX_BLOQUE[letra]:g}"})
        bloques[letra] = {
            "score": score,
            "max": MAX_BLOQUE[letra],
            "peso": PESO_BLOQUE[letra],
            "excluido": bool(motivo),
            "motivoExclusion": motivo,
            # UN BLOQUE QUE NADIE PUNTUÓ NO ES UN CERO. Sin esto, un parte al
            # que le falta la mitad de la rúbrica se pintaba «0% · SIN
            # FORMACIÓN», que es un veredicto durísimo inventado sobre un dato
            # ausente — y el equipo salía en pantalla como el peor posible.
            "declarado": crudo is not None or bool(motivo),
            "nota": _txt(notas_in.get(letra)) or nota_obj,
        }
    plantel = [j for j in (_jugador(x, rechazos, f"equipos.{lado}.plantel[{i}]")
                           for i, x in enumerate(_lista(bruto.get("plantel"), rechazos,
                                                        f"equipos.{lado}.plantel"))) if j]
    fuera = [f for f in (_fuera(x, rechazos, f"equipos.{lado}.fuera[{i}]")
                         for i, x in enumerate(_lista(bruto.get("fuera"), rechazos,
                                                      f"equipos.{lado}.fuera"))) if f]
    # UNA BAJA QUE NO ESTÁ EN LA F1 NO PESA EN EL IP. El protocolo pide que la
    # tabla F1 liste a todos los relevantes, disponibles y no disponibles; si
    # una baja quedó fuera, o se incorpora con su rol o el IP la ignora — y
    # ese IP mudo es el que después parece "el ponderador está roto".
    en_tabla = {normalizar(j["nombre"]) for j in plantel}
    for f in fuera:
        if normalizar(f["nombre"]) in en_tabla:
            continue
        if f["zona"] and f["rol"]:
            plantel.append({"nombre": f["nombre"], "posicion": "", "zona": f["zona"],
                            "rol": f["rol"], "apps": "", "soloBaja": True})
            en_tabla.add(normalizar(f["nombre"]))
        else:
            rechazos.append({
                "donde": f"equipos.{lado}.fuera", "jugador": f["nombre"],
                "porque": "esta baja no está en la tabla F1 y no trae zona/rol: "
                          "NO pesa en el Impacto Ponderado",
                "esperado": "inclúyela en `plantel`, o dale `zona` y `rol` aquí mismo",
            })
    dt = _dt_equipo(bruto.get("dt"), rechazos, lado, fecha_partido, entrenador_base)
    perfil = _dict(bruto.get("perfil"), rechazos, f"equipos.{lado}.perfil",
                   '{"sistema": "4-3-3", "estilo": "…", "fortaleza": "…", "vulnerabilidad": "…"}')
    nombre = _txt(bruto.get("nombre"))
    return {
        "nombre": canonizar(nombre, equipos_db) if nombre else "",
        "bloques": bloques,
        "dt": dt,
        "perfil": {k: _txt(perfil.get(k)) for k in ("sistema", "estilo", "fortaleza", "vulnerabilidad")},
        "plantel": plantel,
        "fuera": fuera,
        "factorX": [{"nombre": _txt(x.get("nombre")), "contexto": _txt(x.get("contexto"))}
                    for x in (_dict(y, rechazos, f"equipos.{lado}.factorX[{i}]",
                                    '{"nombre": "…", "contexto": "…"}')
                              for i, y in enumerate(_lista(bruto.get("factorX"), rechazos,
                                                           f"equipos.{lado}.factorX")))
                    if _txt(x.get("nombre"))],
        "sensibilidad": [x for x in (
            _sensibilidad(y, rechazos, f"equipos.{lado}.sensibilidad[{i}]")
            for i, y in enumerate(_lista(bruto.get("sensibilidad"), rechazos,
                                         f"equipos.{lado}.sensibilidad"))) if x],
    }


def _lista(v, rechazos: list, donde: str) -> list:
    """Lo que tiene que ser una lista y no lo es se DICE, no revienta."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    rechazos.append({"donde": donde,
                     "porque": f"tiene que ser una lista, llegó {type(v).__name__}",
                     "esperado": "[…]"})
    return []


def _dict(v, rechazos: list, donde: str, esperado: str = "{…}") -> dict:
    """Lo que tiene que ser un objeto y no lo es se DICE, no revienta.

    `lecturaSad` como string tumbaba el depósito con un 500 sin mensaje: era
    el segundo campo del contrato (después de `sensibilidad`) que en vez de
    rechazar con motivo reventaba el endpoint. En un batch desatendido un 500
    pierde el parte entero y nadie sabe por qué. Cualquier rama del cuerpo
    que se lea con `.get` pasa por aquí."""
    if v is None:
        return {}
    if isinstance(v, dict):
        return v
    rechazos.append({"donde": donde,
                     "porque": f"tiene que ser un objeto, llegó {type(v).__name__}",
                     "esperado": esperado})
    return {}


def _sensibilidad(x, rechazos: list, donde: str) -> dict | None:
    """Caja de sensibilidad: qué cambiaría si el dato que falta fuera otro.

    Es la contrapartida honesta de "sin dato es una respuesta válida": el hueco
    se declara Y se dice cuánto movería el análisis. Un hueco sin esto es una
    excusa; con esto es una incertidumbre acotada.

    UN STRING ACÁ TUMBABA EL DEPÓSITO CON UN 500. `["si el central no llega,
    …"]` es lo primero que se le ocurre a cualquiera, y era el ÚNICO campo del
    contrato que en vez de rechazar con motivo reventaba el endpoint: en un
    batch desatendido eso pierde el parte entero sin decir por qué."""
    if not isinstance(x, dict):
        rechazos.append({
            "donde": donde,
            "porque": f"cada supuesto tiene que ser un objeto, llegó {type(x).__name__}",
            "esperado": '{"supuesto": "el central 2 no llega", '
                        '"efecto": "DEF pasa a zona debilitada"}'})
        return None
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


def _lectura_sad(x, rechazos: list | None = None) -> dict:
    """Lo que el protocolo llama la lectura SAD: el juicio que cierra el EFE.

    Es puro criterio —no hay forma de calcularlo— y es lo que el analista lee
    primero cuando ya vio los números. Sin sitio propio en el parte terminaba
    diluido dentro del ensayo."""
    rechazos = rechazos if rechazos is not None else []
    x = _dict(x, rechazos, "lecturaSad",
              '{"moduloOperativo": "…", "unXDos": {"texto": "…", "rangoAmpliado": false}, '
              '"contextoEmocional": "…", "datoEstructural": "…", "paradoja": "…", "reventon": "…"}')
    uxd = x.get("unXDos") or x.get("un_x_dos") or {}
    if isinstance(uxd, str):
        uxd = {"texto": uxd}
    uxd = _dict(uxd, rechazos, "lecturaSad.unXDos", '{"texto": "…", "rangoAmpliado": false}')
    return {
        "moduloOperativo": _txt(x.get("moduloOperativo") or x.get("modulo_operativo")),
        "unXDos": {"texto": _txt(uxd.get("texto")),
                   "rangoAmpliado": bool(uxd.get("rangoAmpliado") or uxd.get("rango_ampliado"))},
        "contextoEmocional": _txt(x.get("contextoEmocional") or x.get("contexto_emocional")),
        "datoEstructural": _txt(x.get("datoEstructural") or x.get("dato_estructural")),
        "paradoja": _txt(x.get("paradoja")),
        # el reventón de la burbuja (docs/REVENTON.md): Cowork escribe su LECTURA
        # (una línea por equipo: qué racha no se recomienda seguir y por qué);
        # los números NO se copian: el backend los recalcula al leer y viajan
        # al lado en `reventonCalculado`
        "reventon": _txt(x.get("reventon")),
    }


def _reventon_calculado(fx) -> dict | None:
    """El reventón de la burbuja de cada equipo con ESTE partido como próximo
    (docs/REVENTON.md), calculado AL LEER como el timeline y el bloque F: si la
    historia cambia, la próxima lectura ya lo trae. Solo la familia total, que
    es la que manda. Un fallo se declara en `error`, no tumba el parte."""
    if not fx:
        return None
    from datetime import datetime, timezone
    from backend import jugadores as jug
    from backend.analisis import burbuja
    from backend.app import constantes_de, niveles_de
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lados = (("a", fx["home_team_id"], fx["away_team_id"], fx["away_name"], "L"),
             ("b", fx["away_team_id"], fx["home_team_id"], fx["home_name"], "V"))
    out = {}
    for lado, tid, rid, rival, cond in lados:
        try:
            filas = list(reversed(constantes_de(tid, 500)))
            nv, nr = niveles_de(tid, 1), niveles_de(rid, 1)
            prox = {"fixtureId": fx["id"], "fecha": str(fx["date"])[:10], "rivalId": rid, "rival": rival,
                    "condicion": cond, "nivelRival": nr[0]["nivel"] if nr else 1.0}
            r = burbuja.analizar(filas, equipo_id=tid, nivel=nv[0]["nivel"] if nv else 0.5,
                                 bin_=nv[0]["bin"] if nv else 0, proximo=prox,
                                 plantilla=jug.plantilla_de(tid), hoy=hoy)
            fam = r["familias"]["total"]
            out[lado] = {"actual": fam["actual"], "riesgo": fam["riesgo"], "rival": fam["rival"],
                         "extremo": fam.get("extremo"),
                         "estabilidad": r["estabilidad"]["grado"], "partidos": r["partidos"], "aviso": r["aviso"]}
        except Exception as e:  # noqa: BLE001 — se declara, no se inventa ni se rompe la lectura
            out[lado] = {"actual": None, "riesgo": None, "rival": None, "extremo": None, "estabilidad": "sin dato",
                         "partidos": 0, "aviso": "", "error": f"no se pudo calcular: {e}"}
    return out


def alertas_extremo(reventon: dict | None, nombres: dict) -> list[dict]:
    """La alerta K-EXTREMO del parte, una por lado con la burbuja total en su
    máximo histórico (y K-CERCA-EXTREMO, ámbar, si está en la franja alta sin
    llegar al récord). Va en la TIRA de alertas, arriba del todo, porque una
    línea dentro de la lectura SAD se lee tarde o no se lee: en Alavés–Valencia
    el riesgo decía «bajo» con la K de Valencia en su récord y nadie lo vio
    hasta el 0-1. No cambia el riesgo (la K no puntúa); cambia cuánto se carga."""
    out = []
    for lado in LADOS:
        ext = ((reventon or {}).get(lado) or {}).get("extremo") or {}
        act = ((reventon or {}).get(lado) or {}).get("actual") or {}
        k = act.get("k")
        if ext.get("cerca") and not ext.get("activo") and k is not None:
            out.append({
                "codigo": "K-CERCA-EXTREMO", "equipo": lado, "tipo": "dato",
                "detalle": f"{nombres.get(lado, lado)}: burbuja K {k:+.2f} en la franja más alta de su "
                           f"historia ({' · '.join(ext.get('motivos') or [])}). No es récord y el modelo "
                           "no lo puntúa como riesgo, pero queda poco margen: no cargar fuerte a que la "
                           "racha siga",
            })
            continue
        if not ext.get("activo"):
            continue
        out.append({
            "codigo": "K-EXTREMO", "equipo": lado, "tipo": "estructural",
            "detalle": f"{nombres.get(lado, lado)}: burbuja K {k:+.2f} en su máximo histórico "
                       f"({' · '.join(ext.get('motivos') or [])}). El modelo no lo puntúa como "
                       "riesgo (la tasa de reventón no sube con la K), pero es terreno sin "
                       "precedente: NO cargar la apuesta a que la racha siga. Cowork tiene que "
                       "declararlo en lecturaSad.reventon y en el pronóstico",
        })
    return out


# ── la escala del nivel entre ligas ──────────────────────────────────────────

def _liga_domestica(team_id: int, fecha: str | None) -> dict | None:
    """La liga contra la que se calcula el nivel de un equipo: la MÁS FRECUENTE
    en sus partidos terminados del último año antes de `fecha`, fuera de los
    torneos internacionales de clubes, el Mundial y los amistosos. None si no
    hay partidos (equipo nuevo en la base)."""
    from backend.app import liga_meta
    fuera = _internacionales_de_clubes() | {1, 667}
    hasta = (fecha or datetime.now(timezone.utc).strftime("%Y-%m-%d")).replace("T", " ").rstrip("Z")
    try:
        desde = (datetime.strptime(hasta[:10], "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
    except ValueError:
        return None
    filas = saddb.query(
        "sad",
        f"""SELECT league_id, COUNT(*) AS n FROM fixtures
            WHERE (home_team_id=? OR away_team_id=?) AND date < ? AND date >= ?
              AND (status_short IN ('FT','AET','PEN') OR status_long='Match Finished')
              AND league_id IS NOT NULL AND league_id NOT IN ({",".join("?" * len(fuera))})
            GROUP BY league_id ORDER BY n DESC, league_id LIMIT 1""",
        (team_id, team_id, hasta, desde, *sorted(fuera)),
    )
    if not filas:
        return None
    meta = liga_meta(filas[0]["league_id"])
    return {"id": filas[0]["league_id"], "nombre": meta.get("nombre"), "pais": meta.get("pais"),
            "partidos": filas[0]["n"]}


def _segunda(liga_id: int) -> bool:
    """Segunda división o torneo menor, con la lista de la ingesta si está a mano."""
    if liga_id in SEGUNDAS:
        return True
    try:
        from backend.ingesta.extractor import LIGAS_MENORES
        return liga_id in LIGAS_MENORES
    except Exception:
        return False


def misma_base(la: dict | None, lb: dict | None) -> bool:
    """¿Los dos niveles salen de la misma base de rivales? Misma liga, o el
    mismo país en la misma categoría (Uruguay y Paraguay parten la primera en
    Apertura/Clausura con dos ids: son la misma base)."""
    if not la or not lb:
        return True  # sin dato no se grita nada: la alerta es para lo que se sabe
    if la["id"] == lb["id"]:
        return True
    return bool(la.get("pais")) and la.get("pais") == lb.get("pais") and _segunda(la["id"]) == _segunda(lb["id"])


DT_FIABLE_DIAS = 14   # un registro más viejo que esto se marca para confirmar en prensa


def dt_de_base(team_id: int) -> dict | None:
    """El DT que tiene la base para un equipo, con su edad en días y si se
    puede tomar sin confirmar: `fiable` = viene de la alineación del último
    partido (el que se sentó en el banco) o tiene menos de DT_FIABLE_DIAS."""
    from backend import jugadores as jug
    try:
        filas = jug._entrenador_filas(team_id)
    except sqlite3.Error:
        return None
    if not filas:
        return None
    e = jug._entrenador_dto(filas[0])
    edad = None
    if e.get("actualizadoEn"):
        try:
            act = datetime.strptime(str(e["actualizadoEn"])[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
            edad = max(0, (datetime.now(timezone.utc).replace(tzinfo=None) - act).days)
        except ValueError:
            edad = None
    fiable = e.get("fuente") == "alineacion" or (edad is not None and edad <= DT_FIABLE_DIAS)
    return {**e, "edadDias": edad, "fiable": fiable,
            "nota": ("visto en el banco en el último partido" if e.get("fuente") == "alineacion" else
                     f"carrera de la API, registro de hace {edad} días" if edad is not None else
                     "carrera de la API, sin fecha de registro")
                    + ("" if fiable else " · CONFIRMAR EN PRENSA: si la red dice otro, manda la red")}


def sin_dt(parte: dict) -> list[str]:
    """Los lados cuyo bloque A no tiene DT: «sin establecer» o vacío. Un caso
    así no entra al aprendizaje (cuarentena automática en lecciones.py)."""
    fuera = []
    for lado in LADOS:
        nombre = _txt(((parte.get("equipos") or {}).get(lado) or {}).get("dt", {}).get("nombre")
                      if isinstance(((parte.get("equipos") or {}).get(lado) or {}).get("dt"), dict) else "")
        if not nombre or nombre.lower() in _DT_DESCONOCIDO:
            fuera.append(lado)
    return fuera


def _tokens_dt(nombre: str) -> set[str]:
    n = (nombre or "").lower().replace("ß", "ss")
    n = unicodedata.normalize("NFD", n)
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    return {t for t in re.split(r"[^a-z]+", n) if len(t) >= 3}


def _mismo_apellido(x: str, y: str) -> bool:
    if x == y:
        return True
    # la base trae letras corruptas («S. Hoeneb» por «S. Hoeneß», Stuttgart
    # 23/09): un apellido largo que coincide en las primeras 5 letras, o que
    # se parece en ≥ 80 %, es el mismo apellido mal escrito
    if min(len(x), len(y)) >= 5 and x[:5] == y[:5]:
        return True
    return min(len(x), len(y)) >= 4 and difflib.SequenceMatcher(None, x, y).ratio() >= 0.8


def mismo_dt(a: str, b: str) -> bool:
    """¿Nombran al mismo entrenador? La API y la prensa los escriben distinto
    («M. Pellegrino» · «Mauricio Pellegrino» · «Hernán Torres Oliveros» ·
    «H. Torres» · «S. Hoeneß» y la base con «S. Hoeneb»): basta un apellido en
    común, tolerando una letra mal codificada. Laxo a propósito: una
    cuarentena falsa saca un caso bueno, y eso también ensucia la métrica."""
    ta, tb = _tokens_dt(a), _tokens_dt(b)
    return any(_mismo_apellido(x, y) for x in ta for y in tb)


def dt_equivocado(parte: dict, fixture_id: int) -> list[dict]:
    """Los lados donde el DT que declaró el parte NO es el que se sentó en el
    banco de ESE partido (la alineación que capturó la ficha).

    Es un criterio de INSUMO, no de resultado: dice que el parte se escribió
    con el entrenador equivocado —el error de la alineación rancia del 22/09—,
    no cómo terminó el partido. Se mira después del pitazo solo porque el
    banco se conoce entonces. Sin alineación capturada (Colombia, Uruguay, o
    la ficha aún no corrió) no se puede comprobar y no se marca nada: ahí la
    cuarentena es a mano."""
    fx = _fixture(fixture_id)
    if not fx:
        return []
    out = []
    malos = set(sin_dt(parte))
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        if lado in malos:
            continue
        dt = ((parte.get("equipos") or {}).get(lado) or {}).get("dt") or {}
        nombre = _txt(dt.get("nombre")) if isinstance(dt, dict) else ""
        try:
            fila = saddb.query_one(
                "sad", "SELECT entrenador FROM alineaciones WHERE fixture_id=? AND team_id=? "
                       "AND entrenador IS NOT NULL AND entrenador <> '' LIMIT 1", (fixture_id, tid))
        except Exception:  # noqa: BLE001 — sin tabla de alineaciones no hay con qué comparar
            fila = None
        banco = (fila["entrenador"] if fila else "") or ""
        # sin un apellido comparable de algún lado («DT A») no se puede decir
        # que sean distintos: no se marca
        if banco and _tokens_dt(nombre) and _tokens_dt(banco) and not mismo_dt(nombre, banco):
            out.append({"lado": lado, "parte": nombre, "banco": banco})
    return out


def corregir_dt(fixture_id: int, cambios: dict) -> dict:
    """Cambia SOLO el `dt` de uno o los dos lados de un parte ya depositado.

    El POST del parte reemplaza el parte entero (a propósito: es la única forma
    de quitar una alerta que ya no aplica). Para corregir un DT eso obligaba a
    rearmar el parte completo desde el GET, y el 23/09 un intento con cuerpo
    parcial vació Everton–Ipswich (documentos, plantel, marcador, TDE) hasta
    que Cowork lo reconstruyó a mano. Esto toca un campo y nada más: no re-sella
    la cohorte, no rehace la coherencia, no mueve el pronóstico ni el veredicto.
    El DT pasa por la MISMA normalización que en el depósito (`_dt_equipo`); un
    lado rechazado no se aplica y vuelve con su motivo."""
    cambios = {l: v for l, v in (cambios or {}).items() if l in LADOS and v is not None}
    if not cambios:
        raise ParteInvalido("manda al menos un lado: {\"a\": {\"nombre\": \"…\", \"desde\": \"AAAA-MM-DD\"}}")
    fx = _fixture(fixture_id)
    with _conectar() as con:
        fila = con.execute("SELECT parte_json FROM parte_cowork WHERE fixture_id=?", (fixture_id,)).fetchone()
        if not fila:
            raise KeyError(fixture_id)
        parte = json.loads(fila["parte_json"])
        fecha_partido = _txt(fx["date"])[:10] if fx else ""
        antes, ahora, rechazos = {}, {}, []
        for lado, crudo in cambios.items():
            base = None
            if fx:
                from backend import jugadores as jug
                try:
                    base = jug.plantilla_de(fx["home_team_id"] if lado == "a" else fx["away_team_id"]).get("entrenador")
                except sqlite3.Error:
                    base = None
            r_lado: list = []
            nuevo = _dt_equipo(crudo, r_lado, lado, fecha_partido, base)
            equipo = (parte.setdefault("equipos", {}).setdefault(lado, {}))
            if r_lado:
                rechazos.extend(r_lado)
                continue
            antes[lado] = equipo.get("dt")
            equipo["dt"] = nuevo
            ahora[lado] = nuevo
        if ahora:
            con.execute("UPDATE parte_cowork SET parte_json=?, actualizado_en=? WHERE fixture_id=?",
                        (json.dumps(parte, ensure_ascii=False), efedb.ahora(), fixture_id))
    return {
        "fixtureId": fixture_id,
        "antes": antes,
        "ahora": ahora,
        "rechazos": rechazos,
        # lo que ve el aprendizaje después del cambio: vacío = el DT del parte
        # ya casa con el que se sentó en el banco (o no hay alineación)
        "dtEquivocado": dt_equivocado(parte, fixture_id),
        "sinDt": sin_dt(parte),
    }


def alertas_dt(parte: dict, fx, nombres: dict) -> list[dict]:
    """DT-DISCREPANCIA cuando el parte (la prensa) y la base no dicen el mismo
    DT: manda el parte, y la base queda marcada para refrescarse. DT-SIN-DT
    cuando el bloque A no tiene entrenador: el caso no entra al aprendizaje."""
    from backend.ingesta.jugadores import _norm_dt
    out = []
    if not fx:
        return out
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        dt = ((parte.get("equipos") or {}).get(lado) or {}).get("dt") or {}
        nombre = _txt(dt.get("nombre")) if isinstance(dt, dict) else ""
        quien = nombres.get(lado, lado)
        if lado in sin_dt(parte):
            out.append({"codigo": "DT-SIN-DT", "equipo": lado, "tipo": "dato",
                        "detalle": f"{quien}: el bloque A no tiene DT («sin establecer»). Sin entrenador "
                                   "confirmado no hay continuidad que puntuar: este caso queda FUERA del "
                                   "aprendizaje (cuarentena automática) hasta que se re-deposite con el DT"})
            continue
        base = dt_de_base(tid)
        if base and base.get("nombre") and _norm_dt(nombre) != _norm_dt(base["nombre"]):
            out.append({"codigo": "DT-DISCREPANCIA", "equipo": lado, "tipo": "dato",
                        "detalle": f"{quien}: el parte dice «{nombre}» y la base tiene «{base['nombre']}» "
                                   f"({base['nota']}). Manda el parte —es lo verificado en prensa—; el registro "
                                   "de la base se refresca en la próxima corrida (DT de la agenda)",
                        "dtBase": base})
    return out


def alerta_escala(fx, nombres: dict) -> list[dict]:
    """La alerta ESCALA-LIGAS del parte: los dos equipos vienen de bases
    distintas y el nivel NO compara entre ligas. Es de diseño —el nivel es
    puntos y goles contra los rivales de cada uno—, pero el parte tiene que
    decirlo cuando junta a un 12.º de LaLiga con un 15.º de la Premier: sin
    la advertencia, el número invita a leerlo como si midiera lo mismo."""
    if not fx:
        return []
    try:
        fecha = str(fx["date"])[:10]
        la = _liga_domestica(fx["home_team_id"], fecha)
        lb = _liga_domestica(fx["away_team_id"], fecha)
        if misma_base(la, lb):
            return []
        from backend.app import niveles_de
        niv = {}
        for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
            nv = niveles_de(tid, 1, antes=str(fx["date"]))
            niv[lado] = nv[0]["nivel"] if nv else None
        fmt = lambda v: f"{v:.2f}" if v is not None else "sin nivel"  # noqa: E731
        return [{
            "codigo": "ESCALA-LIGAS", "equipo": "global", "tipo": "dato",
            "detalle": (f"{nombres.get('a', 'A')} ({la['nombre']}) y {nombres.get('b', 'B')} ({lb['nombre']}) "
                        f"vienen de bases distintas: el nivel SAD se calcula con los puntos y los goles "
                        f"contra los rivales de cada uno y NO compara entre ligas (un 12.º de LaLiga puede "
                        f"salir con menos nivel que un 15.º de la Premier). Leer {fmt(niv['a'])} y "
                        f"{fmt(niv['b'])} como la posición de cada uno dentro de su propia liga; el gap §5 "
                        f"y la μ del TDE cruzan esos dos niveles, así que van con esa reserva. El reventón "
                        f"no la necesita: compara al rival con la propia historia del equipo"),
            "ligas": {"a": la, "b": lb},
        }]
    except Exception as e:  # noqa: BLE001 — se declara, no tumba el parte
        return [{"codigo": "ESCALA-LIGAS", "equipo": "global", "tipo": "dato",
                 "detalle": f"no se pudo comparar las ligas de los dos equipos: {e}"}]


def _via_tde(v, rechazos: list, donde: str) -> dict | None:
    """Una vía del TDE. Tolera que no sea un objeto y lo DICE.

    Antes esto hacía `v.get(...)` a ciegas: una vía mandada como string
    —`["ECHADA", "SOB"]`, que es lo primero que a cualquiera se le ocurre—
    reventaba con AttributeError y salía por 500. Un 500 en un batch
    desatendido pierde el parte entero y no dice por qué.
    """
    if not isinstance(v, dict):
        rechazos.append({"donde": donde, "porque": f"una vía tiene que ser un objeto, llegó {type(v).__name__}",
                         "esperado": '{"nombre": "ECHADA", "indice": 6.4, "ventana": "60-75", "detalle": "…"}'})
        return None
    nombre = _txt(v.get("nombre"))
    if not nombre:
        rechazos.append({"donde": donde, "porque": "vía sin `nombre`",
                         "esperado": "ECHADA / SOBREEXPOSICIÓN"})
        return None
    return {"nombre": nombre, "indice": _num(v.get("indice"), 1000),
            "ventana": _txt(v.get("ventana")), "detalle": _txt(v.get("detalle"))}


def _bloque_tde(x, rechazos: list, donde: str, lado: str = "") -> dict:
    """El TDE de UN equipo: los dos índices, su ventana y su causa.

    Los NIVELES (verde/ámbar/rojo) llegan del skill, no los inventa el backend:
    la escala del IE es suya y ponerle umbrales aquí sería duplicar —y con el
    tiempo desalinear— una tabla que vive en otro lado. Sin nivel, la pantalla
    pinta el número en neutro."""
    if not isinstance(x, dict):
        rechazos.append({
            "donde": donde,
            "porque": f"un bloque del TDE tiene que ser un objeto, llegó {type(x).__name__}",
            "esperado": '{"equipo": "a", "indicadores": {...}, "tipologia": "…", "ventana": "…"}'})
        return {}
    vias_raw = x.get("vias")
    if vias_raw is not None and not isinstance(vias_raw, list):
        rechazos.append({"donde": f"{donde}.vias", "porque": f"`vias` tiene que ser una lista, "
                                                             f"llegó {type(vias_raw).__name__}",
                         "esperado": '[{"nombre": "ECHADA", "indice": 6.4, …}]'})
        vias_raw = []
    vias = [v for v in (_via_tde(y, rechazos, f"{donde}.vias[{i}]")
                        for i, y in enumerate(vias_raw or [])) if v]
    ind = x.get("indicadores") if isinstance(x.get("indicadores"), dict) else {}
    tiene = any([_txt(x.get("tipologia")), vias, ind,
                 x.get("ie") is not None, x.get("ise") is not None])
    if not tiene:
        return {}
    # `equipo` es el LADO, no el nombre del club. Mandarlo como «Tigres FC» se
    # guardaba vacío sin avisar, y con él se perdía de qué equipo era el índice
    # —que es la mitad del sentido del TDE—.
    equipo = _txt(x.get("equipo")).lower()
    if equipo and equipo not in LADOS:
        rechazos.append({"donde": f"{donde}.equipo",
                         "porque": f"`equipo` es el lado, no el nombre del club: llegó {x.get('equipo')!r}",
                         "esperado": '"a" (local) o "b" (visitante)'})
        equipo = ""
    # cuando el lado viene de la LLAVE ({"a": {...}}) manda la llave, pero una
    # contradicción no se elige en silencio: se dice cuál se guardó
    if lado and equipo and equipo != lado:
        rechazos.append({"donde": f"{donde}.equipo",
                         "porque": f"el bloque está bajo {lado!r} pero adentro dice {equipo!r}: "
                                   f"se guarda como {lado!r}",
                         "esperado": "que la llave y el `equipo` de adentro digan lo mismo"})
    # EL NIVEL ES UNA ETIQUETA Y EL ÍNDICE ES UN NÚMERO, en dos campos. El
    # pipeline mandó el índice numérico en `ieNivel` durante diez partes y el
    # backend lo tiraba guardando "" sin un rechazo: nueve partes sin nivel y
    # sin nadie que lo viera. Un número ahí se delata y, si `ie` venía vacío,
    # se guarda en `ie` —que es el campo numérico del contrato— para no perderlo.
    ie, ise = x.get("ie"), x.get("ise")
    niveles = {}
    for clave_nivel, clave_num, valor_num in (("ieNivel", "ie", ie), ("iseNivel", "ise", ise)):
        crudo = x.get(clave_nivel)
        niveles[clave_nivel] = _sem(crudo)
        if crudo in (None, "") or niveles[clave_nivel]:
            continue
        numero = None
        try:
            numero = float(crudo)
        except (TypeError, ValueError):
            pass
        if numero is not None and valor_num in (None, ""):
            if clave_num == "ie":
                ie = numero
            else:
                ise = numero
            rechazos.append({
                "donde": f"{donde}.{clave_nivel}",
                "porque": f"`{clave_nivel}` es la etiqueta de color y llegó el número {crudo!r}: "
                          f"se guardó en `{clave_num}` y el nivel quedó vacío",
                "esperado": f'`{clave_nivel}`: "verde" | "ambar" | "rojo" · `{clave_num}`: el índice numérico'})
        else:
            rechazos.append({
                "donde": f"{donde}.{clave_nivel}",
                "porque": f"`{clave_nivel}` es la etiqueta de color y llegó {crudo!r}: no se guardó",
                "esperado": f'`{clave_nivel}`: "verde" | "ambar" | "rojo" · `{clave_num}`: el índice numérico'})
    disciplina = bool(x.get("disciplina43"))
    if disciplina and not vias and not ind and ie in (None, "") and ise in (None, ""):
        rechazos.append({
            "donde": f"{donde}.disciplina43",
            "porque": "`disciplina43: true` declara las dos vías por separado, pero no llegó ni "
                      "una vía, ni indicadores, ni `ie`/`ise`: no hay índice que lo sostenga, "
                      "se guardó false",
            "esperado": '`vias`: [{"nombre": "ECHADA", "indice": …}, {"nombre": "SOBREEXPOSICION", …}] '
                        'o `indicadores` con los 0/0.5/1'})
        disciplina = False
    return {
        # LOS INDICADORES MANDAN SOBRE EL ÍNDICE. Si llegan los 0/0.5/1, el IE y
        # el ISE los calcula el backend con sus compuertas: la cuenta se puede
        # equivocar y las compuertas se pueden olvidar, y las dos cosas pasaron
        # en el registro. El `ie` suelto se conserva solo como lo que llegó.
        "indicadores": {k: _num(v, 1) for k, v in ind.items() if v is not None},
        "ie": _num(ie, 1000), "ieNivel": niveles["ieNivel"],
        "ise": _num(ise, 1000), "iseNivel": niveles["iseNivel"],
        "equipo": lado or equipo,
        "tipologia": _txt(x.get("tipologia")),
        "ventana": _txt(x.get("ventana")),
        "disciplina43": disciplina,
        "vias": vias,
        "falsador": _txt(x.get("falsador")),
    }


def _tde(x, rechazos: list) -> dict:
    """Teorema del Echado del partido: hasta UN bloque por equipo.

    EL ÍNDICE ES POR EQUIPO Y EL PARTE GUARDABA UNO SOLO. El segundo terminaba
    en `notas`, que es prosa: no se puede consultar, no se puede comprobar
    contra los goles recibidos y no entra en ninguna métrica. Ahora los dos son
    dato de primera clase y se guardan siempre en `bloques`.

    Se aceptan las cuatro formas que aparecen solas —la canónica que devuelve el
    GET, el objeto plano, el `{a, b}` como los equipos y la lista— porque la
    alternativa ya se probó: la forma no prevista se guardaba como `{}` sin un
    solo rechazo y el recibo decía que todo estaba bien.
    """
    if x is None:
        return {}
    crudos: list[tuple[str, str, object]] = []   # (donde, lado, bloque)
    if isinstance(x, list):
        crudos = [(f"tde[{i}]", "", y) for i, y in enumerate(x)]
    elif isinstance(x, dict) and isinstance(x.get("bloques"), list):
        crudos = [(f"tde.bloques[{i}]", "", y) for i, y in enumerate(x["bloques"])]
    elif isinstance(x, dict) and set(x) & set(LADOS) and not (set(x) - set(LADOS)):
        crudos = [(f"tde.{l}", l, x[l]) for l in LADOS if x.get(l) is not None]
    elif isinstance(x, dict):
        crudos = [("tde", "", x)]
    else:
        rechazos.append({
            "donde": "tde",
            "porque": f"`tde` tiene que ser un objeto o una lista de bloques, llegó {type(x).__name__}",
            "esperado": '{"bloques": [{"equipo": "a", "indicadores": {…}, "ventana": "…"}]}'})
        return {}

    bloques: list[dict] = []
    for donde, lado, crudo in crudos:
        b = _bloque_tde(crudo, rechazos, donde, lado)
        if not b:
            continue
        # DOS BLOQUES PARA EL MISMO LADO NO SE RESUELVEN A DEDO. Guardar el
        # primero (o el último) es tirar un análisis entero sin decirlo.
        gemelo = next((o for o in bloques if o["equipo"] and o["equipo"] == b["equipo"]), None)
        if gemelo:
            rechazos.append({
                "donde": donde,
                "porque": f"ya venía otro bloque del TDE para el equipo {b['equipo']!r}: "
                          f"el segundo NO se guardó",
                "esperado": "un bloque por lado; si son dos lecturas del mismo equipo, "
                            "mandá una sola con las dos vías (`disciplina43`)"})
            continue
        bloques.append(b)
    if len(bloques) > len(LADOS):
        sobra = bloques[len(LADOS):]
        rechazos.append({"donde": "tde", "porque": f"llegaron {len(bloques)} bloques y el partido "
                                                   f"tiene dos equipos: {len(sobra)} no se guardaron",
                         "esperado": "hasta un bloque por lado"})
        bloques = bloques[:len(LADOS)]
    return {"bloques": bloques} if bloques else {}


def _evento_tl(e, rechazos: list | None = None, donde: str = "timelineEventos") -> dict | None:
    """Un evento INSTITUCIONAL del timeline. Los partidos no entran por aquí:
    los calcula backend/cronologia.py de nuestra propia base."""
    from backend import cronologia as crono
    if not isinstance(e, dict):
        if rechazos is not None:
            rechazos.append({"donde": donde,
                             "porque": f"cada evento es un objeto, llegó {type(e).__name__}",
                             "esperado": '{"fecha": "2026-03-02", "tipo": "tecnico", "titulo": "…"}'})
        return None
    titulo = _txt(e.get("titulo"))
    fecha = _txt(e.get("fecha"))
    if not titulo or not fecha:
        if rechazos is not None:
            rechazos.append({"donde": donde, "porque": "evento sin `titulo` o sin `fecha`: no se guarda",
                             "esperado": '{"fecha": "2026-03-02", "tipo": "tecnico", "titulo": "…"}'})
        return None
    tipo = _txt(e.get("tipo")).lower()
    if tipo in crono.TIPOS_PARTIDO or tipo not in TL_TIPOS:
        # un resultado copiado a mano se descarta: el marcador es de la ingesta.
        # ANTES SE DESCARTABA EN SILENCIO: Cowork mandaba eventos y el recibo
        # devolvía «eventosTimeline: 0» sin decir por qué.
        if rechazos is not None:
            rechazos.append({"donde": donde,
                             "porque": (f"tipo {tipo!r} no es institucional: los partidos los calcula la base"
                                        if tipo in crono.TIPOS_PARTIDO else
                                        f"tipo {tipo!r} desconocido: solo {', '.join(TL_TIPOS)}"),
                             "esperado": f"tipo ∈ {list(TL_TIPOS)}"})
        return None
    return {
        "fecha": fecha, "aproximada": bool(e.get("aproximada")) or fecha.startswith("~"),
        "equipo": _txt(e.get("equipo")), "tipo": tipo, "titulo": titulo,
        "detalle": _txt(e.get("detalle")), "jornada": 0, "marcador": "",
        "destacado": bool(e.get("destacado")),
        "alerta_relacionada": _txt(e.get("alertaRelacionada") or e.get("alerta_relacionada")),
        "fuente": _txt(e.get("fuente")),
    }


def _claves_raras(bruto: dict, conocidas: set, rechazos: list, donde: str) -> None:
    """Delata las claves que nadie va a leer.

    El modo de fallo más caro no es un valor inválido —ese se ve— sino una
    clave con el nombre equivocado: se descarta enterita y el depósito
    responde 200 como si todo hubiera ido bien. Se sugiere la más parecida
    porque casi siempre es un `texto` donde iba `detalle`."""
    if not isinstance(bruto, dict):
        return
    for clave in bruto:
        if clave in conocidas:
            continue
        cerca = difflib.get_close_matches(clave, sorted(conocidas), n=1, cutoff=0.6)
        rechazos.append({
            "donde": f"{donde}.{clave}",
            "porque": "campo desconocido: no se guarda nada de lo que venga aquí",
            "esperado": (f"¿querías decir «{cerca[0]}»?" if cerca
                         else "mira el contrato en docs/openapi.yaml"),
        })


_CLAVES_ALERTA = {"codigo", "equipo", "tipo", "detalle", "texto", "ligas", "dtBase"}
# LAS ALERTAS CALCULADAS NO SE DEPOSITAN. K-EXTREMO, ESCALA-LIGAS, HUECO-DOBLE,
# F3 y las de DT las pone la lectura a partir de la base y del propio parte;
# si el eco del GET vuelve con ellas, se descartan sin rechazo (se van a
# recalcular igual) en vez de guardarse por duplicado.
_ALERTAS_CALCULADAS = {"K-EXTREMO", "K-CERCA-EXTREMO", "ESCALA-LIGAS", "HUECO-DOBLE", "F3", "DT-DISCREPANCIA", "DT-SIN-DT"}
# LA TERCERA CLASE: las de coherencia las pone Jev AL DEPOSITAR y se guardan
# selladas (coherencia_json), porque no son deterministas y rehacerlas al leer
# las haría parpadear. Del depósito se descartan igual que las calculadas
# —Cowork no puede inyectarlas—, pero al leer NO se recalculan: se leen.
_ALERTAS_CAPTURADAS = {"COHERENCIA-BLOQUE", "COHERENCIA-1X2", "COHERENCIA-MATCHUP", "COHERENCIA-REVENTON"}
# el protocolo usa `ambos` para una alerta que toca a los dos equipos: estaba
# en el esquema del EFE viejo y se perdió al escribir este contrato
_EQUIPOS_ALERTA = ("a", "b", "ambos", "global")


def _alerta(a, rechazos: list, donde: str) -> dict | None:
    if isinstance(a, str):
        a = {"codigo": a}   # «T.54» a secas: entra, y se delata que va sin texto
    if isinstance(a, dict) and _txt(a.get("codigo")) in (_ALERTAS_CALCULADAS | _ALERTAS_CAPTURADAS):
        return None
    if not isinstance(a, dict):
        rechazos.append({"donde": donde, "porque": f"cada alerta es un objeto, llegó {type(a).__name__}",
                         "esperado": '{"codigo": "T.54", "equipo": "b", "tipo": "estructural", "detalle": "…"}'})
        return None
    _claves_raras(a, _CLAVES_ALERTA, rechazos, donde)
    codigo = _txt(a.get("codigo"))
    if not codigo:
        rechazos.append({"donde": donde, "porque": "alerta sin código"})
        return None
    equipo = _txt(a.get("equipo")).lower()
    if equipo and equipo not in _EQUIPOS_ALERTA:
        rechazos.append({"donde": f"{donde}.equipo", "porque": f"equipo no reconocido: {equipo!r}",
                         "esperado": "a / b / ambos / global"})
    tipo = _txt(a.get("tipo")).lower()
    # `texto` es el nombre que sale natural; se acepta como alias de `detalle`
    detalle = _txt(a.get("detalle")) or _txt(a.get("texto"))
    if not detalle:
        rechazos.append({"donde": f"{donde}.detalle", "jugador": codigo,
                         "porque": "la alerta llegó sin texto: se guarda como cáscara vacía",
                         "esperado": "detalle: «qué dice la alerta»"})
    return {"codigo": codigo,
            "equipo": equipo if equipo in _EQUIPOS_ALERTA else "global",
            "tipo": tipo if tipo in ("estructural", "fecha") else "fecha",
            "detalle": detalle}


def _documento(d, rechazos: list | None = None, donde: str = "documentos") -> dict | None:
    if not isinstance(d, dict):
        if rechazos is not None:
            rechazos.append({"donde": donde,
                             "porque": f"cada documento es un objeto, llegó {type(d).__name__}",
                             "esperado": '{"id": "ensayo", "cuerpo": "markdown"}'})
        return None
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
    # lo que se descarta se DECLARA. Antes se caía en silencio y quien depositaba
    # veía un 0 sin forma de saber por qué: cuarenta minutos de adivinar la forma
    # del campo en vez de cinco segundos de leer el motivo.
    rechazos: list[dict] = []
    # `entrada` es el bloque que la lectura devuelve para poder re-depositar sin
    # pérdidas: aquí se desempaqueta. Lo que venga suelto en la raíz manda sobre
    # lo que traiga el eco, porque lo suelto es lo que alguien acaba de escribir.
    eco = payload.get("entrada")
    if isinstance(eco, dict):
        payload = {**{k: v for k, v in eco.items() if k in _CLAVES_PARTE}, **payload}
    _claves_raras(payload, _CLAVES_PARTE | _ECO_PARTE, rechazos, "(raíz)")
    cadena_in = _dict(payload.get("cadena"), rechazos, "cadena",
                      '{"a": {"pronostico": "…"}, "b": {"pronostico": "…"}}')
    # la fecha del partido y el DT de nuestra base, para calcular la antigüedad
    # del DT del parte (`desde` → meses) sin pedírsela al modelo
    fx_dt = _fixture(fixture_id)
    fecha_partido = _txt(fx_dt["date"])[:10] if fx_dt else ""
    entrenadores_base: dict[str, dict | None] = {"a": None, "b": None}
    if fx_dt:
        from backend import jugadores as jug
        for l, tid in (("a", fx_dt["home_team_id"]), ("b", fx_dt["away_team_id"])):
            try:
                entrenadores_base[l] = jug.plantilla_de(tid).get("entrenador")
            except sqlite3.Error:
                entrenadores_base[l] = None
    parte = {
        "fixtureId": fixture_id,
        "version": _txt(payload.get("version")) or VERSION,
        "generadoEn": _txt(payload.get("generadoEn")),
        "equipos": {l: _equipo(equipos_in.get(l) or {}, equipos_db, rechazos, l,
                               fecha_partido, entrenadores_base[l]) for l in LADOS},
        "alertas": [a for a in (_alerta(x, rechazos, f"alertas[{i}]")
                                for i, x in enumerate(_lista(payload.get("alertas"), rechazos,
                                                             "alertas"))) if a],
        "matchup": {},
        "pronostico": {},
        "lecturaSad": _lectura_sad(payload.get("lecturaSad") or payload.get("lectura_sad") or {},
                                   rechazos),
        "tde": _tde(payload.get("tde"), rechazos),
        "timelineEventos": [e for e in (_evento_tl(x, rechazos, f"timelineEventos[{i}]")
                                        for i, x in enumerate(_lista(payload.get("timelineEventos"),
                                                                     rechazos, "timelineEventos"))) if e],
        "timelineNarrativa": _txt(payload.get("timelineNarrativa")),
        "cadena": {l: _pron_cadena(cadena_in.get(l)) for l in LADOS},
        "documentos": [d for d in (_documento(x, rechazos, f"documentos[{i}]")
                                   for i, x in enumerate(_lista(payload.get("documentos"), rechazos,
                                                                "documentos"))) if d],
        "pendientes": _lista_txt(payload.get("pendientes")),
        "fuentes": _lista_txt(payload.get("fuentes")),
        "descartados": _lista_txt(payload.get("descartados")),
        "notas": _txt(payload.get("notas")),
        "rechazos": rechazos,
    }
    m = _dict(payload.get("matchup"), rechazos, "matchup",
              '{"diagnostico": "FAVORABLE", "favorece": "a", "razon": "…", "h2a": "verde", …}')
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
    p = _dict(payload.get("pronostico"), rechazos, "pronostico",
              '{"motor": "…", "matriz": "…", "mercado": "…", '
              '"probabilidades": {"local": 52, "empate": 27, "visita": 21}, "marcador": "2-1", "falsador": "…"}')
    prob = _dict(p.get("probabilidades"), rechazos, "pronostico.probabilidades",
                 '{"local": 52, "empate": 27, "visita": 21}')
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
        previo = con.execute("SELECT creado_en, xi_json, parte_json FROM parte_cowork WHERE fixture_id=?",
                             (parte["fixtureId"],)).fetchone()
        con.execute(
            "INSERT INTO parte_cowork (fixture_id, fecha, equipo_a, equipo_b, estado, version, "
            "parte_json, xi_json, creado_en, actualizado_en, cohorte) VALUES (?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(fixture_id) DO UPDATE SET fecha=excluded.fecha, equipo_a=excluded.equipo_a, "
            "equipo_b=excluded.equipo_b, version=excluded.version, parte_json=excluded.parte_json, "
            "actualizado_en=excluded.actualizado_en, "
            # la cohorte es de la PRIMERA vez: un re-depósito no cambia de época, y un
            # parte que ya existía sin marca es de antes de la primera cohorte (rodaje)
            f"cohorte=COALESCE(parte_cowork.cohorte, '{COHORTE_RODAJE}')",
            (parte["fixtureId"], (fx["date"] or "")[:10], fx["home_name"], fx["away_name"],
             "pendiente_xi", parte["version"], json.dumps(parte, ensure_ascii=False),
             previo["xi_json"] if previo else None,
             previo["creado_en"] if previo else ahora, ahora, COHORTE),
        )
    # COHERENCIA (Jev): se evalúa AQUÍ y se guarda sellada, no al leer —Jev no
    # es determinista y dos lecturas darían hallazgos distintos—. Nunca tumba
    # el depósito: un fallo se declara dentro del propio JSON.
    nombres = {"a": fx["home_name"], "b": fx["away_name"]}
    try:
        # el reventón calculado solo hace falta si de verdad se va a preguntar:
        # sin clave el adaptador responde simulado y no hay hallazgo posible
        rev = (_reventon_calculado(fx)
               if _coherencia.modo() != "off" and _coherencia.jev.disponible() else None)
        coh = _coherencia.evaluar(parte, nombres, rev)
    except Exception as e:  # noqa: BLE001 — se declara, no se rompe el POST
        coh = {"modo": _coherencia.modo(), "error": f"no se pudo evaluar: {e}", "hallazgos": []}
    with _conectar() as con:
        con.execute("UPDATE parte_cowork SET coherencia_json=? WHERE fixture_id=?",
                    (json.dumps(coh, ensure_ascii=False), parte["fixtureId"]))
        # EL REGISTRO. coherencia_json guarda la ÚLTIMA evaluación; para saber
        # cómo reaccionó Cowork (¿re-depositó corregido? ¿sostuvo?) hace falta
        # la secuencia: es lo que lee el reporte del revisor (revisor()).
        con.execute(
            "INSERT INTO coherencia_log (fixture_id, evaluado_en, modo, modelo, preguntas, hallazgos, "
            "sin_confianza, simulado, error, tokens, redeposito, hallazgos_json, via) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (parte["fixtureId"], coh.get("evaluadoEn") or ahora, coh.get("modo"), coh.get("modelo"),
             coh.get("preguntas", 0), len(coh.get("hallazgos") or []),
             len(coh.get("sinConfianza") or []), 1 if coh.get("simulado") else 0,
             coh.get("error"), coh.get("tokensEntrada", 0), 1 if previo else 0,
             json.dumps([{"codigo": h["codigo"], "equipo": h["equipo"]} for h in coh.get("hallazgos") or []],
                        ensure_ascii=False),
             coh.get("via") or ("simulado" if coh.get("simulado") else None)))
    # un parte nuevo sobre un fixture que ya tenía once resuelto se recalcula
    # solo al leerlo: el once vive aparte, justamente para sobrevivir al parte
    # AVISO DE DEPÓSITO DESTRUCTIVO: el POST reemplaza el parte entero (es
    # idempotente a propósito — con merge no habría forma de QUITAR una alerta
    # que ya no aplica). Pero un cuerpo incompleto borraba lo anterior sin que
    # nadie se enterara hasta abrir la pantalla. Ahora se cuenta y se dice.
    perdido = []
    if previo:
        try:
            antes = json.loads(previo["parte_json"])
        except (ValueError, TypeError):
            antes = {}
        def _tam(p_: dict) -> dict:
            # LO QUE ESTE CONTEO NO MIRE SE PUEDE BORRAR EN SILENCIO. La
            # primera versión contaba listas —documentos, plantel, bajas— y
            # dejaba fuera justo lo que hace al EFE: los sub-scores. Un
            # re-depósito recortado vaciaba la rúbrica entera y el recibo decía
            # `perdido: []`.
            def _subscores(lado):
                bl = ((p_.get("equipos", {}).get(lado) or {}).get("bloques") or {})
                return sum(1 for l in LETRAS
                           if isinstance(bl.get(l), dict) and bl[l].get("declarado"))
            pron = p_.get("pronostico") or {}
            return {
                "alertas": len(p_.get("alertas") or []),
                "documentos": len(p_.get("documentos") or []),
                "fuentes": len(p_.get("fuentes") or []),
                "jugadores": sum(len((p_.get("equipos", {}).get(l) or {}).get("plantel") or []) for l in LADOS),
                "bajas": sum(len((p_.get("equipos", {}).get(l) or {}).get("fuera") or []) for l in LADOS),
                "eventosTimeline": len(p_.get("timelineEventos") or []),
                "subScoresEfe": sum(_subscores(l) for l in LADOS),
                "bloquesTde": len(bloques_tde(p_.get("tde") or {})),
                # las vías (ECHADA / SOBREEXPOSICIÓN) se perdían en silencio en
                # un re-depósito que mandaba el TDE sin ellas (Cowork, 23/09)
                "viasTde": sum(len(b.get("vias") or []) for b in bloques_tde(p_.get("tde") or {})),
                # `cadena[lado]` es el texto del pronóstico, pero también se
                # acepta `{"pronostico": "…"}`: las dos formas se cuentan igual
                "pronosticosDeCadena": sum(1 for l in LADOS if _pron_cadena((p_.get("cadena") or {}).get(l))),
                "repartoUnXDos": 1 if sum((pron.get("probabilidades") or {}).values()) else 0,
                "falsador": 1 if _txt(pron.get("falsador")) else 0,
                "lecturaSad": 1 if (p_.get("lecturaSad") or {}).get("moduloOperativo") else 0,
                "sensibilidad": sum(len((p_.get("equipos", {}).get(l) or {}).get("sensibilidad") or []) for l in LADOS),
            }
        t_antes, t_ahora = _tam(antes), _tam(parte)
        perdido = [f"{k}: {t_antes[k]} → {t_ahora[k]}" for k in t_antes if t_ahora[k] < t_antes[k]]

    cadena, cadena_ignorada = _guardar_cadena(fx, parte.get("cadena") or {})
    # LO QUE FALTA AHORA Y SE COBRA DENTRO DE 12 HORAS. Un bloque vacío no es
    # un error al depositar —se puede completar después, y a veces no hay dato—,
    # pero algunos se pagan al cerrar el caso, cuando ya NO se pueden llenar sin
    # hindsight. Decirlo acá, con el partido todavía por jugarse, es la única
    # ventana en la que arreglarlo es legítimo. Callarlo es descubrirlo medio
    # día tarde, que fue exactamente lo que pasó con `cadena` y con `tde`.
    faltan = []
    if not any((parte.get("cadena") or {}).get(l) for l in LADOS):
        faltan.append({
            "bloque": "cadena",
            "costara": "ningún equipo recibirá veredicto en su cadena: al cerrar, "
                       "`sinPronosticoPrevio` va a devolver los dos lados",
            "comoSeArregla": "declará `cadena.a.pronostico` y `cadena.b.pronostico` AHORA, "
                             "antes del saque; después del partido ya sería escribirlo con "
                             "el resultado puesto",
        })
    tde_bloques = bloques_tde(parte.get("tde") or {})
    if not tde_bloques:
        faltan.append({
            "bloque": "tde",
            "costara": "el veredicto no va a poder comprobar la ventana del TDE "
                       "(`objetivo.tde` viene sin bloques)",
            "comoSeArregla": "mandá `tde` con su ventana de 15 minutos; el índice es POR "
                             "equipo, así que caben los dos lados",
        })
    elif len(tde_bloques) == 1 and tde_bloques[0].get("equipo"):
        faltan.append({
            "bloque": "tde (el otro equipo)",
            "costara": f"solo se comprueba la ventana del lado {tde_bloques[0]['equipo']!r}: "
                       "del otro no queda nada medible",
            "comoSeArregla": 'mandá los dos: {"bloques": [{"equipo": "a", …}, {"equipo": "b", …}]}',
        })
    pron = parte.get("pronostico") or {}
    # el normalizador siempre deja las tres claves, así que "vacío" es que
    # sumen cero — no que el diccionario no esté
    if not sum((pron.get("probabilidades") or {}).values()):
        faltan.append({
            "bloque": "pronostico.probabilidades",
            "costara": "sin reparto 1X2 no hay acierto que medir ni Brier que calcular: "
                       "el caso se cierra sin métrica",
            "comoSeArregla": "mandá `pronostico.probabilidades` con local/empate/visita",
        })
    elif not _txt(pron.get("falsador")):
        faltan.append({
            "bloque": "pronostico.falsador",
            "costara": "sin falsador no hay nada que refutar: `falsadorCumplido` "
                       "queda en null y el caso pierde su prueba más dura",
            "comoSeArregla": "una condición OBSERVABLE que, si ocurre, declara fallado "
                             "el pronóstico",
        })
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
        "conTde": bool(tde_bloques),
        # de QUÉ equipos quedó índice: el TDE es por equipo y caben los dos
        "ladosTde": [b.get("equipo") or "" for b in tde_bloques],
        # lo que falta y se va a cobrar al cerrar el caso, mientras todavía se
        # puede llenar sin mirar el resultado
        "faltan": faltan,
        # lo que NO entró, con el motivo y dónde estaba
        "rechazos": parte.get("rechazos") or [],
        # lo que este depósito BORRÓ de lo que ya había guardado
        "perdido": perdido,
        # el guardrail semántico (Jev): qué se preguntó y qué no cuadró. En modo
        # sombra se ve acá y en el GET, no en la tira de alertas
        "coherencia": _coherencia.resumen_recibo(coh),
        "aviso": ("Este depósito dejó el parte con MENOS contenido del que tenía "
                  f"({'; '.join(perdido)}). El POST reemplaza el parte entero: si fue sin "
                  "querer, vuelve a depositarlo completo." if perdido else ""),
    }
    print(f"[cowork] parte {resumen['estado']}: {resumen['partido']} "
          f"({resumen['jugadores']['a']}+{resumen['jugadores']['b']} jugadores, "
          f"{len(parte['documentos'])} documentos, "
          f"{resumen['eventosTimeline']} eventos de timeline)"
          + (f" · RECHAZOS: {len(parte.get('rechazos') or [])}"
             if parte.get("rechazos") else "")
          + (f" · BORRÓ: {'; '.join(perdido)}" if perdido else "")
          + (f" · cadena: {', '.join(cadena)}" if cadena else "")
          + (f" · PRONÓSTICO YA DECLARADO, se conserva el primero: {cadena_ignorada}"
             if cadena_ignorada else "")
          + (f" · FALTAN (se cobra al cerrar): {', '.join(x['bloque'] for x in faltan)}"
             if faltan else "")
          + (f" · DISCREPANCIAS: {discrepancias}" if discrepancias else ""), flush=True)
    return resumen


def borrar(fixture_id: int) -> bool:
    with _conectar() as con:
        cur = con.execute("DELETE FROM parte_cowork WHERE fixture_id=?", (fixture_id,))
    return cur.rowcount > 0


# ── lectura: el DTO que pinta la pantalla ───────────────────────────────────

def _totales(equipo: dict) -> dict:
    """El total ponderado, y —lo que faltaba— si hay algo que totalizar.

    Un parte sin sub-scores daba 0/27 y clasificación SIN FORMACIÓN: el mismo
    resultado que un equipo evaluado y reprobado. La ausencia se pintaba como
    el peor juicio posible, que es la forma más cara de este error.
    """
    # PARTES DEPOSITADOS ANTES DE QUE `declarado` EXISTIERA. Su JSON guardado no
    # tiene la clave, y tratar «ausente» como «no declarado» le borraba el EFE
    # de la pantalla a todo lo depositado hasta ayer — el mismo error que este
    # campo vino a arreglar, girado del otro lado. Para esos se INFIERE (un
    # sub-score > 0 lo puso alguien) y se dice que es una inferencia.
    legado = not any("declarado" in equipo["bloques"][l] for l in LETRAS)
    if legado:
        for letra in LETRAS:
            b = equipo["bloques"][letra]
            b["declarado"] = bool(b["score"]) or b["excluido"]
            b["declaradoInferido"] = True
    total = maximo = 0.0
    sin_declarar = []
    for letra in LETRAS:
        b = equipo["bloques"][letra]
        b["ponderado"] = round(b["score"] * b["peso"], 2)
        b["topePonderado"] = round(b["max"] * b["peso"], 2)
        if b["excluido"]:
            continue
        if not b.get("declarado"):
            sin_declarar.append(letra)
        total += b["ponderado"]
        maximo += b["topePonderado"]
    declarados = [l for l in LETRAS
                  if equipo["bloques"][l].get("declarado") and not equipo["bloques"][l]["excluido"]]
    nota_legado = (". Parte anterior al campo `declarado`: se infirió de los sub-scores, "
                   "así que un 0 declarado de verdad puede figurar como hueco" if legado else "")
    if not declarados:
        return {"total": 0.0, "maximoAlcanzable": round(maximo, 2),
                "porcentaje": None, "clasificacion": "",
                "sinBloques": True, "bloquesSinDeclarar": list(sin_declarar),
                "notaTotales": "el parte no trae ni un sub-score: no hay EFE que calcular. "
                               "Esto NO es 0% ni SIN FORMACIÓN, es que nadie puntuó" + nota_legado}
    pct = round((total / maximo) * 100, 1) if maximo else 0.0
    return {"total": round(total, 2), "maximoAlcanzable": round(maximo, 2),
            "porcentaje": pct, "clasificacion": clasificacion_de(pct),
            "sinBloques": False, "bloquesSinDeclarar": sin_declarar,
            # un bloque ausente arrastra el porcentaje hacia abajo como si
            # fuera un cero: la cuenta se mantiene (la rúbrica los pide todos)
            # pero el hueco se DICE, para que nadie lea el número como completo
            "notaTotales": ((f"faltan los sub-scores {', '.join(sin_declarar)}: cuentan como 0 "
                             "y bajan el porcentaje" if sin_declarar else "") + nota_legado).strip(". ")}


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


def bloques_tde(tde) -> list[dict]:
    """Los bloques del TDE, entienda o no la forma vieja.

    En la base hay partes depositados cuando `tde` era UN objeto plano. Leerlos
    con la forma nueva devolvería vacío y el TDE de esos partidos desaparecería
    de la pantalla sin que nadie tocara nada: eso es perder dato en silencio,
    que es justo lo que venimos arreglando.
    """
    if not isinstance(tde, dict) or not tde:
        return []
    if isinstance(tde.get("bloques"), list):
        return [b for b in tde["bloques"] if isinstance(b, dict) and b]
    return [tde]   # forma vieja: un bloque plano


def _tde_calculado(tde: dict) -> dict:
    """El TDE con su índice CALCULADO, un bloque por equipo.

    Igual que el bloque F y que los totales del EFE: si el dato de entrada está,
    el número lo pone la aritmética. Lo que llegó escrito se conserva al lado en
    `declarado`, y si no coincide se dice — un IE mal sumado que nadie compara
    es una banda de probabilidad equivocada durante meses.
    """
    bloques = bloques_tde(tde)
    if not bloques:
        return {}
    return {"bloques": [_bloque_calculado(b) for b in bloques]}


def _bloque_calculado(tde: dict) -> dict:
    ind = tde.get("indicadores") or {}
    if not ind:
        return tde
    from backend.analisis import tde as tdemod
    calc = tdemod.indice(ind)
    fuera = dict(tde)
    fuera["calculado"] = calc
    declarado = {"ie": tde.get("ie"), "ise": tde.get("ise")}
    fuera["declarado"] = declarado
    if not calc.get("sinDato"):
        discrepa = []
        for clave in ("ie", "ise"):
            d, c = declarado.get(clave), calc.get(clave)
            if d and c is not None and abs(float(d) - float(c)) > 0.1:
                discrepa.append(f"{clave.upper()}: llegó {d} y la cuenta da {c}")
        fuera["discrepancia"] = discrepa
        # el número que manda es el calculado
        fuera["ie"], fuera["ise"] = calc["ie"], calc.get("ise")
    return fuera


def dto(fixture_id: int) -> dict | None:
    """Todo lo que la pantalla necesita, con lo calculable ya calculado."""
    with _conectar() as con:
        fila = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b, estado, version, parte_json, "
            "xi_json, creado_en, actualizado_en, cohorte, cuarentena_json, coherencia_json "
            "FROM parte_cowork WHERE fixture_id=?",
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
    tde_calc = _tde_calculado(parte.get("tde") or {})
    # EL MISMO HUECO, LEÍDO AL REVÉS POR DOS ESCALAS. El EFE cuenta el bloque
    # ausente como 0 y hunde el porcentaje; el TDE promedia solo sobre los
    # indicadores presentes, así que uno alto con denominador chico dispara el
    # índice. Un equipo salía «1.9% SIN FORMACIÓN» y «IE 8.14, casi seguro» a
    # la vez: los dos números son artefactos del mismo vacío y apuntan en
    # direcciones contrarias. Quien mira la pantalla lee «equipo pésimo con
    # riesgo altísimo» cuando lo que hay es «no hay datos».
    for b in tde_calc.get("bloques") or []:
        lado = b.get("equipo")
        cob = (b.get("calculado") or {}).get("cobertura") or {}
        if lado not in LADOS or not cob:
            continue
        pocos = cob.get("usados", 0) < cob.get("nominales", 16) * 0.75
        huecos = equipos[lado].get("bloquesSinDeclarar") or equipos[lado].get("sinBloques")
        if pocos and huecos:
            alertas.append({
                "codigo": "HUECO-DOBLE", "equipo": lado, "tipo": "dato",
                "detalle": f"al mismo equipo le faltan sub-scores del EFE "
                           f"({', '.join(equipos[lado].get('bloquesSinDeclarar') or []) or 'todos'}) "
                           f"y el TDE se calculó con {cob.get('usados')} de "
                           f"{cob.get('nominales')} indicadores. El hueco tira el EFE hacia "
                           "abajo y empuja el IE hacia arriba: los dos números salen del "
                           "mismo vacío y apuntan al revés. No es un equipo pésimo con "
                           "riesgo altísimo, es un equipo sin datos",
            })
    fx = _fixture(fila["fixture_id"])
    reventon = _reventon_calculado(fx)
    # la burbuja en su máximo histórico va a la tira de alertas, no solo a la
    # lectura: lo que decide cuánto se carga tiene que verse antes que nada
    alertas.extend(alertas_extremo(reventon, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    # dos equipos de ligas distintas: el nivel no compara entre bases, y el
    # parte lo dice antes de que alguien lea los dos números uno contra otro
    alertas.extend(alerta_escala(fx, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    alertas.extend(alertas_dt(parte, fx, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    # las de coherencia se LEEN, no se rehacen (ver _ALERTAS_CAPTURADAS)
    coherencia = json.loads(fila["coherencia_json"]) if fila["coherencia_json"] else None
    alertas.extend(_coherencia.alertas_de(coherencia))
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
        # la lectura de Cowork + el reventón CALCULADO al leer, uno por lado
        "lecturaSad": {**(parte.get("lecturaSad") or _lectura_sad({})), "reventonCalculado": reventon},
        "tde": tde_calc,
        "timeline": timeline,
        "pronostico": parte["pronostico"],
        "documentos": parte["documentos"],
        "pendientes": parte["pendientes"],
        "fuentes": parte["fuentes"],
        "notas": parte["notas"],
        "xi": {l: {k: v for k, v in (xi.get(l) or {}).items() if k != "banca"} for l in LADOS},
        # ECO DE LA ENTRADA: lo que se depositó y no se puede reconstruir desde
        # el resto de la respuesta. El POST reemplaza el parte ENTERO, así que
        # el flujo normal para corregir algo es leer → modificar → re-depositar;
        # sin esto, ese viaje de ida y vuelta perdía los eventos del timeline,
        # los pronósticos de la cadena y la lista de descartados, en silencio.
        "entrada": {
            "timelineEventos": parte.get("timelineEventos") or [],
            "timelineNarrativa": parte.get("timelineNarrativa", ""),
            "cadena": parte.get("cadena") or {},
            "descartados": parte.get("descartados") or [],
        },
        "veredicto": veredicto_de(fila["fixture_id"]),
        # la evaluación de coherencia sellada al depositar; en sombra es lo
        # único que la muestra (para medirla contra el criterio humano)
        "coherencia": coherencia,
        "cohorte": cohorte_de(fila["cohorte"]),
        "cuarentena": json.loads(fila["cuarentena_json"]) if fila["cuarentena_json"] else None,
        "creadoEn": fila["creado_en"],
        "actualizadoEn": fila["actualizado_en"],
    }


def revisor(horas: int = 24, dia: str | None = None) -> dict:
    """El reporte del día: cómo le fue a Cowork con el revisor de coherencia.

    Para quien no mira los partes uno por uno y quiere saber, al final del
    día, tres cosas: qué encontró el revisor, qué hizo Cowork con eso, y
    cuánto costó. Por fixture se lee la SECUENCIA de evaluaciones (un
    re-depósito vuelve a evaluar) y de ahí sale la reacción:

      limpio       nunca hubo hallazgos
      corrigio     hubo hallazgos y el último depósito ya no los tiene
      corrigioParte  el último depósito tiene menos, no cero
      sostuvo      re-depositó y los hallazgos siguen iguales (o más)
      sinReaccion  hubo hallazgos y no volvió a depositar (todavía)
      noEvaluado   todas las evaluaciones fueron simuladas (sin clave) o con error

    `dia` (YYYY-MM-DD, UTC) acota a ese día; sin `dia`, las últimas `horas`
    —«desde ahora hacia atrás», que es lo que uno quiere a las 22:00 de Lima—.
    """
    from datetime import datetime, timedelta, timezone
    from backend.analisis import coherencia as coh_mod
    with _conectar() as con:
        if dia:
            filas = con.execute(
                "SELECT * FROM coherencia_log WHERE substr(evaluado_en,1,10)=? "
                "ORDER BY fixture_id, evaluado_en, id", (dia,)).fetchall()
        else:
            desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat(timespec="seconds")
            filas = con.execute(
                "SELECT * FROM coherencia_log WHERE evaluado_en >= ? "
                "ORDER BY fixture_id, evaluado_en, id", (desde,)).fetchall()
    por_fixture: dict[int, list] = {}
    for f in filas:
        por_fixture.setdefault(f["fixture_id"], []).append(dict(f))

    partes, totales = [], {
        "partesEvaluados": 0, "conHallazgos": 0, "limpios": 0, "corrigio": 0, "corrigioParte": 0,
        "sostuvo": 0, "sinReaccion": 0, "noEvaluados": 0, "evaluaciones": len(filas),
        "hallazgosPorCodigo": {}, "sinConfianza": 0, "tokensEntrada": 0, "errores": 0,
        # POR DÓNDE PASARON las evaluaciones reales: el oficial o un intermediario
        "porVia": {},
    }
    for fid, evs in por_fixture.items():
        fx = _fixture(fid)
        reales = [e for e in evs if not e["simulado"] and not e["error"]]
        totales["tokensEntrada"] += sum(int(e["tokens"] or 0) for e in evs)
        totales["errores"] += sum(1 for e in evs if e["error"])
        secuencia = [{"evaluadoEn": e["evaluado_en"], "modo": e["modo"], "preguntas": e["preguntas"],
                      "hallazgos": [h["codigo"] for h in json.loads(e["hallazgos_json"] or "[]")],
                      "sinConfianza": e["sin_confianza"], "simulado": bool(e["simulado"]),
                      "error": e["error"], "redeposito": bool(e["redeposito"]),
                      "via": e.get("via")} for e in evs]
        for e in evs:
            if not e["simulado"] and not e["error"]:
                v = e.get("via") or "?"
                totales["porVia"][v] = totales["porVia"].get(v, 0) + 1
        if not reales:
            reaccion = "noEvaluado"
            totales["noEvaluados"] += 1
        else:
            totales["partesEvaluados"] += 1
            totales["sinConfianza"] += int(reales[-1]["sin_confianza"] or 0)
            primera = next((e for e in reales if e["hallazgos"]), None)
            if not primera:
                reaccion = "limpio"
                totales["limpios"] += 1
            else:
                totales["conHallazgos"] += 1
                for h in json.loads(primera["hallazgos_json"] or "[]"):
                    totales["hallazgosPorCodigo"][h["codigo"]] = totales["hallazgosPorCodigo"].get(h["codigo"], 0) + 1
                despues = [e for e in reales if e["id"] > primera["id"]]
                if not despues:
                    reaccion = "sinReaccion"
                elif despues[-1]["hallazgos"] == 0:
                    reaccion = "corrigio"
                elif despues[-1]["hallazgos"] < primera["hallazgos"]:
                    reaccion = "corrigioParte"
                else:
                    reaccion = "sostuvo"
                totales[reaccion] += 1
        partes.append({
            "fixtureId": fid,
            "partido": f"{fx['home_name']} vs {fx['away_name']}" if fx else f"fixture {fid}",
            "fecha": (fx["date"] or "")[:10] if fx else "",
            "reaccion": reaccion,
            "hallazgosEncontrados": next((s_["hallazgos"] for s_ in secuencia if s_["hallazgos"]), []),
            "hallazgosAhora": secuencia[-1]["hallazgos"],
            "evaluaciones": secuencia,
        })
    orden = {"sinReaccion": 0, "sostuvo": 1, "corrigioParte": 2, "corrigio": 3, "limpio": 4, "noEvaluado": 5}
    partes.sort(key=lambda p_: (orden.get(p_["reaccion"], 9), p_["fecha"], p_["fixtureId"]))
    return {
        "modo": coh_mod.modo(),
        "via": coh_mod.jev.via(),
        "oficial": coh_mod.jev.oficial(),
        "ventana": {"dia": dia, "horas": None if dia else horas},
        "totales": {**totales, "costoUsd": round(coh_mod.jev.costo(totales["tokensEntrada"]), 5)},
        "partes": partes,
        "paraMirar": [p_["fixtureId"] for p_ in partes if p_["reaccion"] in ("sinReaccion", "sostuvo")],
        "nota": ("lo que Jev marcó y qué hizo Cowork con eso. `paraMirar` son los partes con hallazgos "
                 "que Cowork no corrigió: o el revisor se equivocó, o Cowork sostuvo con razón en "
                 "`notas`, o no volvió a pasar por ahí. Las tres cosas se ven abriendo el parte"),
    }


def cohorte_de(valor: str | None) -> dict:
    clave = valor or COHORTE_RODAJE
    return {"clave": clave, "vigente": clave == COHORTE,
            "descripcion": COHORTES.get(clave, "cohorte sin descripción registrada")}


# ── cuarentena: un caso que no cuenta, con su motivo ────────────────────────
#
# Cuarentena POR CRITERIO, NUNCA POR RESULTADO. Se pone por lo que le faltaba
# al parte antes del pitazo (DT viejo, TDE sin nivel, agenda equivocada), no
# porque el veredicto salió fallo: si no, es la forma elegante de borrar los
# fallos y la métrica deja de significar. Por eso el motivo es obligatorio,
# se guarda el veredicto que tenía el caso en ese momento (para que una
# auditoría vea si se puso después de saber cómo terminó) y la pone el
# usuario con el token maestro: no está abierta a Cowork.
CUARENTENA_MOTIVO_MIN = 12


def poner_cuarentena(fixture_id: int, motivo: str) -> dict:
    motivo = _txt(motivo)
    if len(motivo) < CUARENTENA_MOTIVO_MIN:
        raise ParteInvalido("la cuarentena lleva motivo: qué le faltaba a ESTE parte antes del pitazo "
                            "(«DT viejo», «TDE sin nivel», «rodaje: primera semana»). Un fallo no es motivo")
    with _conectar() as con:
        fila = con.execute("SELECT veredicto_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
        if not fila:
            raise KeyError(fixture_id)
        ver = json.loads(fila["veredicto_json"]) if fila["veredicto_json"] else {}
        marca = {
            "motivo": motivo,
            "puestaEn": efedb.ahora(),
            # evidencia para la auditoría: qué se sabía del caso al ponerla
            "veredictoAlPoner": {l: ((ver.get("porLado") or {}).get(l) or {}).get("veredicto", "")
                                 for l in LADOS} if ver else None,
        }
        con.execute("UPDATE parte_cowork SET cuarentena_json=? WHERE fixture_id=?",
                    (json.dumps(marca, ensure_ascii=False), fixture_id))
    return {"fixtureId": fixture_id, "cuarentena": marca}


def quitar_cuarentena(fixture_id: int) -> dict:
    with _conectar() as con:
        fila = con.execute("SELECT cuarentena_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
        if not fila:
            raise KeyError(fixture_id)
        con.execute("UPDATE parte_cowork SET cuarentena_json=NULL WHERE fixture_id=?", (fixture_id,))
    return {"fixtureId": fixture_id, "cuarentena": None,
            "quitada": json.loads(fila["cuarentena_json"]) if fila["cuarentena_json"] else None}


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
        "fuente": FUENTE_FICHA,
        "capturadoEn": efedb.ahora(),
    }


def resolver_xi(fixture_id: int, onces: dict) -> dict:
    """Guarda el once por lado y cierra el bloque F. Sin modelo, sin costo.

    `onces` = {"a": {"once": [...], "banca": [...], "fuente": "..."}, "b": {...}}
    Un lado ausente en `onces` conserva el que ya tuviera guardado: el once
    del local suele llegar antes que el del visitante.

    LA FICHA NO SE PISA A MANO SIN DECIRLO. Un POST de prueba dejó el once
    del 1549492 idéntico pero etiquetado «carga manual» en vez de «ficha de
    API-Football»: la procedencia es dato. Un lado que ya viene de la ficha
    se conserva salvo `reemplazar: true`, y lo conservado se devuelve en
    `xiConservados` con su motivo.
    """
    conservados: dict[str, dict] = {}
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
            fuente = _txt(nuevo.get("fuente")) or FUENTE_MANUAL
            previo = guardado.get(lado) or {}
            if (previo.get("fuente") == FUENTE_FICHA and fuente != FUENTE_FICHA
                    and not nuevo.get("reemplazar")):
                conservados[lado] = {
                    "fuente": FUENTE_FICHA, "capturadoEn": previo.get("capturadoEn", ""),
                    "porque": "este lado ya tiene el once de la ficha de API-Football: no se pisa "
                              "con una carga manual. Si la ficha está mal, mandá `reemplazar: true`",
                }
                continue
            guardado[lado] = {
                "once": once,
                "banca": _lista_txt(nuevo.get("banca")),
                "formacion": _txt(nuevo.get("formacion")),
                "fuente": fuente,
                "capturadoEn": efedb.ahora(),
            }
        con.execute("UPDATE parte_cowork SET xi_json=?, actualizado_en=? WHERE fixture_id=?",
                    (json.dumps(guardado, ensure_ascii=False), efedb.ahora(), fixture_id))
    listo = dto(fixture_id)
    if conservados:
        listo["xiConservados"] = conservados
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

    # PRE ES COMPROBABLE Y SE COMPRUEBA. `terminado` sale de nuestra base, así
    # que declarar PRE sobre un partido que sigue rodando no es un criterio a
    # discutir: es una contradicción con un dato que ya tenemos. La regla del
    # proyecto vale también acá —lo que está en la base se calcula, no se le
    # pregunta al modelo—, y de paso ahorra la peor versión del error: puntuar
    # un partido en el minuto 17 y que el sistema lo archive como validación
    # predictiva.
    obj_previo = vered.objetivo(fixture_id, parte)
    if modo == "PRE" and obj_previo.get("jugado") and not obj_previo["marcador"]["terminado"]:
        raise ParteInvalido(
            "el partido todavía no terminó: un veredicto cerrado contra un marcador "
            "parcial es COND, no PRE (y no acredita). Si querés esperar al final, "
            "volvé cuando el fixture figure terminado en nuestra base")

    por_lado = {}
    for l in LADOS:
        v = _lado_veredicto((payload.get("porLado") or {}).get(l))
        if v:
            por_lado[l] = v
    if not por_lado:
        raise ParteInvalido("porLado vacío: hace falta el veredicto de al menos un lado "
                            "(acierto, parcial o fallo)")

    # el veredicto anterior, si lo hay: hace falta para dos cosas que no se
    # pueden reconstruir —cuándo se cerró y qué se había declarado—
    with _conectar() as con:
        fila_v = con.execute("SELECT veredicto_json FROM parte_cowork WHERE fixture_id=?",
                             (fixture_id,)).fetchone()
    previo_v = json.loads(fila_v["veredicto_json"]) if fila_v and fila_v["veredicto_json"] else {}

    # AUSENTE NO ES `null`. Re-postear el eco del GET —que trae `falsador` como
    # objeto y no `falsadorCumplido`— degradaba un `cumplido: false` guardado a
    # `null`: el caso perdía su prueba más dura sin que nadie lo pidiera. Ahora
    # la clave ausente CONSERVA lo anterior, y para borrarlo hay que mandar
    # `falsadorCumplido: null` a propósito.
    if "falsadorCumplido" in payload:
        cumplido = payload["falsadorCumplido"]
    elif isinstance(payload.get("falsador"), dict) and "cumplido" in payload["falsador"]:
        cumplido = payload["falsador"]["cumplido"]      # el eco del propio GET
    else:
        cumplido = (previo_v.get("falsador") or {}).get("cumplido")
    # UNA EXCEPCIÓN DECLARADA. A veces el caso es `ciega` de verdad y aun así
    # hay algo que contar: el parte se tocó con el partido rodando aunque el
    # pronóstico no se movió, la alineación llegó por un pantallazo sin sellar,
    # el reloj del que escribe no coincidía con el del partido. Eso no cambia
    # la población —esa la declara quien escribe y decide si acredita—, pero
    # tiene que quedar en un CAMPO, no en la prosa de `notas`: una salvedad que
    # solo se puede encontrar leyendo no se encuentra nunca, y la duda vuelve
    # entera dentro de seis meses cuando nadie se acuerde del caso.
    mancha = _txt(payload.get("mancha"))
    rechazos: list[dict] = []
    _claves_raras(payload, _CLAVES_VEREDICTO | _ECO_VEREDICTO, rechazos, "(veredicto)")
    guardado = {
        "seleccion": seleccion,
        "modoEvaluacion": modo,
        "acredita": vered.acredita(seleccion, modo),
        "mancha": mancha,
        "falsador": {"texto": (parte.get("pronostico") or {}).get("falsador", ""),
                     "cumplido": cumplido if isinstance(cumplido, bool) else None},
        "porLado": por_lado,
        "notas": _txt(payload.get("notas")),
        "rechazos": rechazos,
        # CUÁNDO SE CERRÓ EL CASO ES EVIDENCIA, NO UN `updated_at`. Re-sellarlo
        # en cada depósito corría la fecha del cierre —justo el dato con el que
        # se comprueba que el juicio se escribió antes de mirar otra cosa—. El
        # primer cierre manda; las correcciones posteriores van aparte.
        "cerradoEn": previo_v.get("cerradoEn") or efedb.ahora(),
        "actualizadoEn": efedb.ahora() if previo_v else "",
    }
    # EL MODO DE FALLO (Jev, docs/JEV.md): se etiqueta AL CERRAR y se sella
    # aparte —no es determinista— para que el dossier de la fase D agrupe los
    # fallos por causa. No toca la población, ni una métrica, ni el estado de
    # la lección. Un fallo de Jev se declara y el veredicto se guarda igual.
    fx_v = _fixture(fixture_id)
    nombres_v = {"a": fx_v["home_name"], "b": fx_v["away_name"]} if fx_v else {}
    try:
        modo_fallo = _modo_fallo.evaluar(por_lado, nombres_v)
    except Exception as e:  # noqa: BLE001
        modo_fallo = {"error": f"no se pudo etiquetar: {e}", "lados": {}, "preguntas": 0}
    with _conectar() as con:
        con.execute("UPDATE parte_cowork SET veredicto_json=?, modo_fallo_json=?, actualizado_en=? "
                    "WHERE fixture_id=?",
                    (json.dumps(guardado, ensure_ascii=False),
                     json.dumps(modo_fallo, ensure_ascii=False), efedb.ahora(), fixture_id))

    sin_pronostico = _cerrar_cadena(fixture_id, por_lado)
    listo = veredicto_de(fixture_id)
    obj = listo.get("objetivo") or {}
    print(f"[cowork] veredicto {fixture_id}: {obj.get('marcador', {}).get('texto', '?')} · "
          f"1X2 {'✓' if obj.get('unXDos', {}).get('acerto') else '✗'} · "
          f"{seleccion}/{modo} ({'acredita' if guardado['acredita'] else 'no acredita'})"
          + (f" · CON SALVEDAD: {mancha}" if mancha else "")
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
            "SELECT parte_json, veredicto_json, modo_fallo_json FROM parte_cowork WHERE fixture_id=?",
            (fixture_id,)).fetchone()
    if not fila or not fila["veredicto_json"]:
        return None
    parte = json.loads(fila["parte_json"])
    guardado = json.loads(fila["veredicto_json"])
    return {**guardado, "fixtureId": fixture_id,
            # la etiqueta de Jev se LEE sellada, no se rehace (null en casos
            # cerrados antes de que existiera)
            "modoFallo": json.loads(fila["modo_fallo_json"]) if fila["modo_fallo_json"] else None,
            # los veredictos cerrados antes de que existiera el campo no tienen
            # salvedad: vacía, no ausente, para que la pantalla no adivine
            "mancha": guardado.get("mancha", ""),
            "rechazos": guardado.get("rechazos", []),
            "actualizadoEn": guardado.get("actualizadoEn", ""),
            "objetivo": vered.objetivo(fixture_id, parte)}


# cómo se lee `status_short` de API-Football cuando hay que explicar una ausencia
_EN_CURSO = {"1H": "1er tiempo", "HT": "entretiempo", "2H": "2do tiempo",
             "ET": "alargue", "BT": "descanso del alargue", "P": "penales",
             "LIVE": "en curso", "INT": "interrumpido"}
_TERMINADO = {"FT", "AET", "PEN"}
_NO_SE_JUGO = {"PST": "aplazado", "CANC": "cancelado", "ABD": "abandonado",
               "AWD": "ganado en mesa", "WO": "walkover", "SUSP": "suspendido"}


def pendientes_veredicto(horas: int = 12, limite: int = 50) -> dict:
    """Partes sin cerrar cuyo partido ya arrancó hace más de `horas`.

    Devuelve un SOBRE, no una lista pelada. Una lista vacía no distingue entre
    "no hay nada que cerrar", "los partidos siguen jugándose" y "la ingesta no
    trajo el marcador": las tres se ven igual desde afuera, y quien corre la
    validación se queda sin saber si esperar, avisar o seguir. Por eso cada
    parte sin veredicto que NO entra a la lista sale en `noListados` con el
    motivo y, si se está jugando, con su minuto y su marcador parcial.
    """
    with _conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b FROM parte_cowork "
            "WHERE veredicto_json IS NULL ORDER BY fecha DESC LIMIT 400").fetchall()
    ahora = datetime.now(timezone.utc)
    marca = (ahora - timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
    sobre = {
        "ventanaHoras": horas,
        "ahora": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"),
        # el criterio, con todas las letras: `horas` se cuenta desde el SAQUE,
        # no desde el pitazo final (no guardamos la hora de término). Subirlo
        # ESTRECHA la búsqueda; bajarlo la abre. Cowork probó con 24 creyendo
        # lo contrario y no tenía cómo saberlo.
        "criterio": f"partes sin veredicto cuyo partido figura TERMINADO con marcador en nuestra base "
                    f"(entra aunque haya arrancado hace menos de {horas} h), o que sin figurar terminado "
                    f"arrancó hace más de {horas} h y ya tiene marcador (subir `horas` estrecha solo a esos)",
        "sinCerrar": len(filas),
        "pendientes": [],
        "noListados": [],
    }
    if not filas:
        sobre["nota"] = "no hay ningún parte sin veredicto: todo lo depositado ya está cerrado"
        return sobre

    ids = [f["fixture_id"] for f in filas]
    marcadores = {
        r["id"]: r for r in saddb.query(
            "sad",
            f"SELECT f.id, f.date, f.status_short AS estado, f.elapsed, "
            f"COALESCE(f.fulltime_home, f.goals_home) AS gl, "
            f"COALESCE(f.fulltime_away, f.goals_away) AS gv FROM fixtures f "
            f"WHERE f.id IN ({','.join('?' * len(ids))})",
            tuple(ids))
    }
    for f in filas:
        fid = f["fixture_id"]
        partido = f"{f['equipo_a']} vs {f['equipo_b']}"
        m = marcadores.get(fid)

        def fuera(porque: str, estado: str = ""):
            if len(sobre["noListados"]) < 20:
                sobre["noListados"].append({
                    "fixtureId": fid, "partido": partido, "fecha": f["fecha"],
                    "estado": estado, "porque": porque})

        if not m:
            fuera("el partido no está en nuestra base de fixtures")
            continue
        est = (m["estado"] or "").upper()
        parcial = ("" if m["gl"] is None or m["gv"] is None else f"{m['gl']}-{m['gv']}")
        if est in _EN_CURSO:
            minuto = f", minuto {m['elapsed']}" if m["elapsed"] is not None else ""
            fuera("el partido se está jugando: no hay resultado final que puntuar",
                  f"{_EN_CURSO[est]}{minuto}" + (f", {parcial}" if parcial else ""))
            continue
        if est in _NO_SE_JUGO:
            fuera(f"el partido está {_NO_SE_JUGO[est]}: no hay nada que puntuar", est)
            continue
        if m["gl"] is None or m["gv"] is None:
            fuera("todavía no tenemos el marcador en nuestra base"
                  + ("" if est in _TERMINADO else "; el partido tampoco figura terminado"), est)
            continue
        # TERMINADO en nuestra base = listo para cerrar, sin esperar las `horas`
        # desde el saque. Antes un partido de las 21:00 revisado a las 8:00 (11 h)
        # caía en noListados y la validación de la mañana cerraba cero casos
        # creyendo que no había nada: la ventana existía porque no guardamos la
        # hora de término, pero el status FT + marcador final YA es esa hora.
        if est not in _TERMINADO and m["date"] > marca:
            fuera(f"no figura terminado y arrancó hace menos de {horas} h: todavía no entra en la ventana",
                  f"{est or 'sin estado'}, {parcial}")
            continue
        if len(sobre["pendientes"]) >= limite:
            fuera(f"la lista se cortó en el límite de {limite}", est)
            continue
        sobre["pendientes"].append({
            "fixtureId": fid, "fecha": f["fecha"], "partido": partido,
            "marcador": parcial, "jugadoEn": m["date"],
        })

    if not sobre["pendientes"]:
        sobre["nota"] = (f"ningún caso listo para cerrar: hay {len(filas)} parte(s) sin "
                         f"veredicto y ninguno pasa el filtro. Mirá `noListados`.")
    return sobre


def cerrar_onces_pendientes(limite: int = 50) -> dict:
    """Cierra el bloque F de todos los partes cuya alineación YA está ingestada.

    EL ONCE NO NECESITA AL MODELO. Cerrar el bloque F es cruzar dos listas de
    nombres y multiplicar por los pesos de rol: aritmética que ya vive en
    `bloque_f.py`. Pedirle eso a un agente por token es lento, caro y peor —y
    además mete una carrera contra el reloj que no existe: seis partidos que
    arrancan juntos son seis cierres de milisegundos, no seis análisis.

    Idempotente: un parte ya cerrado no se vuelve a tocar. Lo que no se pudo
    cerrar sale con el motivo, que casi siempre es «la ficha todavía no trae
    la alineación» —el caso que obliga al pantallazo manual—.
    """
    with _conectar() as con:
        filas = [dict(r) for r in con.execute(
            "SELECT fixture_id, equipo_a, equipo_b, xi_json FROM parte_cowork "
            "WHERE veredicto_json IS NULL AND estado != 'confirmado' "
            "ORDER BY fecha LIMIT ?", (limite,))]
    cerrados, sin_ficha, nunca, conflictos, reemplazados = [], [], [], [], []
    for f in filas:
        fid = f["fixture_id"]
        fx = _fixture(fid)
        if not fx:
            continue
        ya = json.loads(f["xi_json"]) if f["xi_json"] else {}
        onces = {}
        for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
            if (ya.get(lado) or {}).get("fuente") == FUENTE_FICHA:
                continue  # ese lado ya viene de la ficha: no hay nada mejor
            de_ficha = xi_de_ficha(fid, tid)
            if de_ficha:
                # LA FICHA MANDA SOBRE LA CARGA MANUAL. El pantallazo existe
                # porque la ficha no había llegado; cuando llega, es la fuente.
                # Antes un lado manual se salteaba para siempre y la procedencia
                # quedaba mal etiquetada (1549492).
                if ya.get(lado):
                    reemplazados.append({"fixtureId": fid, "lado": lado,
                                         "fuenteAnterior": ya[lado].get("fuente", "")})
                onces[lado] = de_ficha
        partido = f"{f['equipo_a']} vs {f['equipo_b']}"
        if not onces:
            # «TODAVÍA» ES UNA PROMESA, Y HAY LIGAS DONDE NO SE CUMPLE NUNCA.
            # Un partido TERMINADO sin alineación ingestada no está esperando
            # nada: esa liga no trae onces, y el pantallazo a mano dejó de ser
            # la excepción para ser el procedimiento. Decirlo cambia qué hace
            # el usuario; llamarlo «todavía» lo deja esperando para siempre.
            fila_fx = saddb.query_one(
                "sad", "SELECT status_short, league_id FROM fixtures WHERE id=?", (fid,))
            estado_fx = dict(fila_fx) if fila_fx else {}
            if (estado_fx.get("status_short") or "") in _TERMINADO:
                nunca.append({
                    "fixtureId": fid, "partido": partido, "ligaId": estado_fx.get("league_id"),
                    "porque": "el partido ya terminó y la ingesta nunca trajo la alineación: "
                              "esta liga no da onces por API-Football",
                    "queHacer": "pegá el once a mano (POST /analisis/cowork/{id}/xi). Para esta "
                                "liga eso no es la excepción, es el procedimiento",
                })
            else:
                sin_ficha.append({"fixtureId": fid, "partido": partido,
                                  "porque": "la ficha todavía no trae la alineación"})
            continue
        listo = resolver_xi(fid, onces)
        # UN ONCE QUE NO CASA CON LA TABLA F1 NO CIERRA NADA. El conflicto se
        # reporta, no se fuerza: un IP inventado es peor que un bloque abierto.
        malos = [l for l in LADOS if listo["equipos"][l]["disponibilidad"].get("conflicto")]
        if malos:
            conflictos.append({"fixtureId": fid, "partido": partido,
                               "lados": malos,
                               "porque": listo["equipos"][malos[0]]["disponibilidad"]["conflicto"]})
        cerrados.append({"fixtureId": fid, "partido": partido,
                         "lados": sorted(onces), "estado": listo["estado"]})
    if cerrados:
        print(f"[cowork] onces cerrados solos: {len(cerrados)} "
              f"({', '.join(x['partido'] for x in cerrados[:4])})"
              + (f" · CONFLICTOS: {len(conflictos)}" if conflictos else ""), flush=True)
    return {
        "revisados": len(filas),
        "cerrados": cerrados,
        # lados que estaban a mano y ahora tienen la ficha: la ficha manda
        "reemplazados": reemplazados,
        "conConflicto": conflictos,
        "sinFichaTodavia": sin_ficha,
        # separado a propósito de `sinFichaTodavia`: acá no hay nada que esperar
        "nuncaVaALlegar": nunca,
        "ligasSinOnce": sorted({x["ligaId"] for x in nunca if x.get("ligaId")}),
        "nota": "esto no gasta tokens ni llama a ningún modelo: cruza el once ingestado "
                "con la tabla F1 y aplica los pesos de rol. `sinFichaTodavia` son los que "
                "todavía pueden cerrar solos; `nuncaVaALlegar` son partidos YA TERMINADOS "
                "cuya liga no da alineaciones: esos necesitan el pantallazo a mano y "
                "reintentarlos no sirve de nada.",
    }


def marcas(fixture_ids: list[int]) -> dict:
    """Qué partidos de una lista YA tienen parte de Cowork, y en qué punto está
    cada uno (once cerrado, veredicto). Es lo que la lista de partidos pinta
    al costado de cada tarjeta: sin abrir el partido se ve si el análisis
    pasó. Se pide por ids, no por fecha, porque el día de la pantalla es
    local y el de la base es UTC: cerca de medianoche no coinciden. Los ids
    sin parte simplemente no vienen."""
    ids = sorted({int(x) for x in fixture_ids if x is not None})[:300]
    if not ids:
        return {"partes": {}, "total": 0}
    marcas_sql = ",".join("?" * len(ids))
    with _conectar() as con:
        filas = con.execute(
            f"""SELECT fixture_id, estado, xi_json, veredicto_json, actualizado_en
                FROM parte_cowork WHERE fixture_id IN ({marcas_sql})""", ids).fetchall()
    partes = {}
    for f in filas:
        partes[str(f["fixture_id"])] = {
            "estado": f["estado"],
            "onceCerrado": bool(f["xi_json"]) and f["estado"] == "confirmado",
            "conVeredicto": bool(f["veredicto_json"]),
            "actualizadoEn": f["actualizado_en"],
        }
    return {"partes": partes, "total": len(partes)}


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
# ── EL PADRÓN DE LA AGENDA ──────────────────────────────────────────────────
# UNA SOLA FUENTE: las mismas ligas a las que se les siguen las cuotas EN VIVO
# (`extractor.ligas_vivo()` = LIGAS − LIGAS_MENORES). Tener dos listas de
# "ligas importantes" en dos archivos garantiza que se separen, y ya se
# separaron una vez: la agenda decidía por NOMBRE y descartaba enteras a
# Brasil, Colombia, Chile, Uruguay, Ecuador, Paraguay, Bolivia, Venezuela,
# Portugal, Bélgica, la Europa League y la Conference, en silencio.
#
# Dentro del padrón hay un orden, y las segundas divisiones van últimas: están
# cubiertas, pero no le sacan el turno a una primera división.
SEGUNDAS = {40: "Inglaterra · Championship", 62: "Francia · Ligue 2",
            72: "Brasil · Serie B", 79: "Alemania · 2. Bundesliga",
            136: "Italia · Serie B", 141: "España · Segunda División",
            263: "México · Liga de Expansión"}
INTERNACIONALES = {
    1: "Copa del Mundo",
    13: "CONMEBOL Libertadores", 11: "CONMEBOL Sudamericana",
    2: "UEFA Champions League", 3: "UEFA Europa League", 848: "UEFA Conference League",
}


def _internacionales_de_clubes() -> set[int]:
    """Los torneos internacionales DE CLUBES, de la ingesta (una sola lista:
    `extractor.LIGAS_INTERNACIONALES`); sin la ingesta a mano, los de acá."""
    try:
        from backend.ingesta.extractor import LIGAS_INTERNACIONALES
        return set(LIGAS_INTERNACIONALES)
    except Exception:
        return {lid for lid in INTERNACIONALES if lid != 1}


def _padron() -> dict[int, str]:
    """Las ligas cubiertas, con su nombre. Sale de la ingesta, no de una copia."""
    try:
        from backend.ingesta.extractor import LIGAS, ligas_vivo
        return {lid: LIGAS.get(lid, f"liga {lid}") for lid in ligas_vivo()}
    except Exception:
        # sin la ingesta a mano (tests aislados), el padrón mínimo declarado
        return {**SEGUNDAS, **INTERNACIONALES, 281: "Perú · Liga 1"}


# fases que el usuario llama «importantes»: de octavos en adelante. «final»
# cubre también «Quarter-finals», «Semi-finals» y «8th Finals», que es como las
# nombra API-Football; la fase de grupos entra igual, pero más abajo.
_FASE_DECISIVA = ("final", "octavos", "cuartos", "semi", "round of 16",
                  "knockout", "playoff", "play-off", "repechaje")


def _prioridad(liga: dict, etiquetas: set[str], pos_local: int, pos_visita: int,
               liga_id: int = 0, ronda: str = "", grupos: bool = False,
               segundas: bool = False) -> tuple[int, str]:
    """Qué merece análisis, en orden. 0 = no entra, y siempre con su motivo.

    El padrón es el de las cuotas en vivo; lo que ordena adentro es: la casa,
    los torneos internacionales cuando se juegan de verdad, los clásicos, y
    después la primera división de cualquier país —con los partidos que mueven
    la tabla adelante—.

    Por defecto QUEDAN FUERA la fase de grupos / fase liga de los torneos
    internacionales y las segundas divisiones: un jueves de Europa League son
    dieciocho partidos de fase liga, y con prioridad 5 le sacaban el turno a
    una primera división entera —la corrida del 16/09 gastó ocho partes en
    Levski–Salzburg, OFI–Hoffenheim y compañía—. Entran solo con `grupos=true`
    / `segundas=true`, y mientras tanto van a `descartados` con este motivo.
    """
    padron = _padron()
    ronda_n = normalizar(ronda or "")
    if liga_id in INTERNACIONALES:
        nombre_i = INTERNACIONALES[liga_id]
        if any(f in ronda_n for f in _FASE_DECISIVA):
            return 2, f"{nombre_i} · fase decisiva ({ronda or 'sin ronda declarada'})"
        if not grupos:
            return 0, (f"{nombre_i} · {ronda or 'fase de grupos'}: la fase de grupos / fase liga "
                       "queda fuera por defecto (de octavos en adelante entra sola); "
                       "pasá grupos=true para incluirla")
        return 5, f"{nombre_i} · {ronda or 'fase de grupos'}"
    if liga_id not in padron:
        # EL DESCARTE TIENE QUE SER EL MISMO SIEMPRE. Antes el clásico se
        # miraba ANTES del padrón, así que un torneo fuera de él entraba o no
        # según se activara el etiquetador de derbis: la Copa Uruguay entró
        # para un partido y se descartó para otros tres, el mismo día.
        return 0, (f"fuera del padrón: {liga.get('nombre') or 'liga'} (id {liga_id}). "
                   "El padrón son las ligas con cuotas en vivo (primeras divisiones, "
                   "segundas de Europa y los torneos internacionales); las copas "
                   "nacionales y los amistosos quedan fuera a propósito")
    if liga_id == 281:
        return 1, "Liga 1 Perú (la casa)"
    if "CLASICO" in etiquetas:
        return 3, f"clásico / derbi · {padron[liga_id]}"
    if liga_id in SEGUNDAS:
        if not segundas:
            return 0, (f"{SEGUNDAS[liga_id]}: las segundas divisiones quedan fuera por "
                       "defecto; pasá segundas=true para incluirlas")
        return 7, f"{SEGUNDAS[liga_id]} (segunda división: entra, pero al final)"
    if "EN_CRISIS" in etiquetas:
        return 4, f"{padron[liga_id]} · equipo en crisis"
    if (0 < pos_local <= 6) or (0 < pos_visita <= 6):
        return 4, f"{padron[liga_id]} · equipo en el top 6"
    return 6, padron[liga_id]


def contrato() -> dict:
    """La forma del cuerpo del POST, derivada de las MISMAS constantes que validan.

    Cowork tuvo que reconstruir esta forma a golpe de recibo porque
    `/openapi.json` está apagado en despliegue —y con razón: expone también lo
    que gasta dinero—. Pero dejar al que deposita adivinando la forma es
    garantizar depósitos a medias.

    Sale de `_CLAVES_*`, no de un texto aparte: un campo nuevo aparece acá solo
    con agregarlo al validador, así que esto NO se puede desincronizar del
    código. Un contrato escrito a mano al lado del código siempre termina
    mintiendo.
    """
    return {
        "endpoint": "POST /api/v1/analisis/cowork",
        "raiz": sorted(_CLAVES_PARTE),
        "tambienSeAceptan": {
            "porque": "son el eco de lo que devuelve el GET, para poder leer → modificar "
                      "→ re-depositar sin desarmar nada. Se ignoran en silencio.",
            "claves": sorted(_ECO_PARTE),
        },
        "equipos": {
            "forma": '{"a": {...}, "b": {...}} — a = local, b = visitante',
            "claves": sorted(_CLAVES_EQUIPO),
            "jugador": sorted(_CLAVES_JUGADOR),
            "fuera": sorted(_CLAVES_FUERA),
            "bloques": {"letras": list(LETRAS), "maximos": MAX_BLOQUE, "pesos": PESO_BLOQUE,
                        "nota": "el sub-score puede ir plano (3) o como objeto "
                                '({"score": 3, "nota": "…"})'},
        },
        "tde": {
            "forma": '{"bloques": [{...}, {...}]} — el índice es POR EQUIPO y caben los dos. '
                     "También se aceptan, y se guardan igual, un objeto plano con `equipo` "
                     "adentro, un {a, b} como los equipos y una lista de bloques",
            "equipo": 'el LADO ("a" o "b"), nunca el nombre del club',
            "dosEquipos": "mandá los dos bloques: el del otro equipo en `notas` es prosa, no "
                          "se puede comprobar contra los goles recibidos ni entra en ninguna "
                          "métrica",
            "indicadores": {k: list(v) for k, v in INDICADORES_TDE.items()},
            "nota": "mandá `indicadores` en 0/0.5/1 y el backend calcula el IE, el ISE y las "
                    "compuertas. NO mandes P(echada) ni riesgo_compuesto: están suspendidas",
            "vias": '[{"nombre": "ECHADA", "indice": 6.4, "ventana": "60-75", "detalle": "…"}]',
        },
        "alertas": {"claves": sorted(_CLAVES_ALERTA),
                    "equipo": list(_EQUIPOS_ALERTA)},
        "lecturaSad": {
            "claves": ["moduloOperativo", "unXDos", "contextoEmocional", "datoEstructural", "paradoja", "reventon"],
            "reventon": "UNA línea por equipo con tu lectura del reventón de la burbuja "
                        "(GET /equipos/{id}/burbujas, docs/REVENTON.md): qué racha NO se recomienda "
                        "seguir y por qué. No copies los números: el backend los recalcula al leer "
                        "y los devuelve en `reventonCalculado`",
        },
        "documentos": {"forma": '[{"id": "…", "titulo": "…", "cuerpo": "markdown", "formato": "md|html|texto"}]',
                       "idsQueLaPantallaTitulaSola": DOCUMENTOS,
                       "nota": "`cuerpo` es obligatorio; sin `id` se guarda como `nota`; el título "
                               "sale del id si no viene"},
        "cadena": {"forma": '{"a": {"pronostico": "…"}, "b": {"pronostico": "…"}}',
                   "nota": "un OBJETO por lado (a = local, b = visitante), no una lista de pasos. "
                           "El pronóstico por equipo foco entra en la cadena del DTP como "
                           "apertura; el veredicto lo emite quien cierre el eslabón"},
        "timelineEventos": {"forma": '[{"fecha": "2026-03-02", "equipo": "…", "tipo": "tecnico", "titulo": "…", "detalle": "…", "fuente": "…"}]',
                            "tipos": list(TL_TIPOS),
                            "nota": "solo eventos INSTITUCIONALES; los partidos los calcula la base "
                                    "(backend/cronologia.py) y un resultado copiado a mano se rechaza "
                                    "con motivo"},
        "loQueNoSeManda": [
            "total, porcentaje, clasificación — los calcula la app",
            "ip, reducción por zona, ramas A/B, F3, F4 — salen de bloque_f.py",
            "los nombres del partido — salen de nuestra base",
            "ie / ise si mandás `indicadores` — se calculan y se delata la discrepancia",
        ],
        "laAgenda": {
            "conflicto": "cada candidato lo trae: vacío casi siempre. Si un equipo «también "
                         "figura en» otro partido a menos de 20 h, uno de los dos fixtures está "
                         "mal (aplazado sin marcar o duplicado). Con los DOS equipos chocando el "
                         "fixture va a `descartados` con ese motivo",
            "porHacer": "los de `analizar` que todavía no tienen parte: la lista de trabajo",
        },
        "elRecibo": {
            "rechazos": "lo que NO se guardó, con el motivo y la forma esperada",
            "faltan": "bloques ausentes y qué van a costar al cerrar el caso",
            "perdido": "lo que este depósito borró de lo que ya había",
        },
        "nota": "esto sale de las mismas constantes que validan el depósito, así que no "
                "puede desincronizarse del código.",
    }


def latido(horas: int = 36) -> dict:
    """¿Está corriendo esto, o lleva dos días muerto y nadie se enteró?

    Una tubería automática sin vigilancia no falla con ruido: falla en silencio,
    y se descubre semanas después cuando alguien va a mirar una métrica y no hay
    casos. Esto contesta de una sola llamada las cuatro preguntas que delatan
    que el batch se cayó, y —lo importante— **el silencio también es un
    estado**: cero partes depositados en 36 horas es rojo, no «sin novedad».

    No decide nada ni arregla nada. Solo mira y dice.
    """
    ahora = datetime.now(timezone.utc)
    corte = (ahora - timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
    with _conectar() as con:
        depositados = con.execute(
            "SELECT COUNT(*) n FROM parte_cowork WHERE actualizado_en >= ?", (corte,)).fetchone()["n"]
        ultimo = con.execute(
            "SELECT fixture_id, equipo_a, equipo_b, actualizado_en FROM parte_cowork "
            "ORDER BY actualizado_en DESC LIMIT 1").fetchone()
        sin_cerrar = con.execute(
            "SELECT COUNT(*) n FROM parte_cowork WHERE veredicto_json IS NULL").fetchone()["n"]
        sin_xi = [dict(r) for r in con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b FROM parte_cowork "
            "WHERE xi_json IS NULL AND veredicto_json IS NULL ORDER BY fecha LIMIT 20")]
    # COBERTURA: de los partidos que la agenda habría elegido ayer, ¿cuántos
    # tienen parte? Es la señal que delata que el batch no corrió, y no se puede
    # deducir mirando solo los partes: hay que comparar contra lo que TOCABA.
    ayer = agenda(fecha=(ahora - timedelta(days=1)).date(), limite=8)
    tocaban = [x["fixtureId"] for x in (ayer.get("analizar") or [])]
    con_parte = set()
    if tocaban:
        with _conectar() as con:
            con_parte = {r["fixture_id"] for r in con.execute(
                f"SELECT fixture_id FROM parte_cowork WHERE fixture_id IN "
                f"({','.join('?' * len(tocaban))})", tuple(tocaban))}
    faltaron = [x for x in (ayer.get("analizar") or []) if x["fixtureId"] not in con_parte]

    # los veredictos que ya deberían estar cerrados y no lo están
    pend = pendientes_veredicto(horas=12, limite=50)
    vencidos = pend.get("pendientes") or []

    horas_sin_nada = None
    if ultimo:
        try:
            t = datetime.strptime(str(ultimo["actualizado_en"])[:19], "%Y-%m-%d %H:%M:%S")
            horas_sin_nada = round((ahora.replace(tzinfo=None) - t).total_seconds() / 3600, 1)
        except ValueError:
            pass

    motivos = []
    if depositados == 0:
        motivos.append(f"no se depositó ningún parte en {horas} h")
    if tocaban and faltaron:
        motivos.append(f"{len(faltaron)} de {len(tocaban)} partidos de la agenda de ayer "
                       "se quedaron sin parte")
    if vencidos:
        motivos.append(f"{len(vencidos)} caso(s) llevan más de 12 h terminados y sin veredicto")
    estado = "rojo" if depositados == 0 else ("ambar" if motivos else "verde")
    return {
        "estado": estado,
        "porque": motivos or ["todo al día"],
        "ahora": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ventanaHoras": horas,
        "depositadosEnLaVentana": depositados,
        "horasDesdeElUltimo": horas_sin_nada,
        "ultimoParte": ({"fixtureId": ultimo["fixture_id"],
                         "partido": f"{ultimo['equipo_a']} vs {ultimo['equipo_b']}",
                         "cuando": ultimo["actualizado_en"]} if ultimo else None),
        "coberturaDeAyer": {"tocaban": len(tocaban), "conParte": len(con_parte),
                            "faltaron": [{"fixtureId": x["fixtureId"], "partido": x.get("partido", ""),
                                          "porque": x.get("motivo", "")} for x in faltaron]},
        "sinCerrar": sin_cerrar,
        "veredictosVencidos": [{"fixtureId": v["fixtureId"], "partido": v["partido"],
                                "marcador": v["marcador"]} for v in vencidos],
        "sinOnceCerrado": sin_xi,
        "nota": "esto solo mira; no dispara nada. El silencio cuenta como fallo: "
                "cero partes en la ventana es ROJO, no «sin novedad».",
    }


# un equipo no juega dos partidos oficiales con menos de esto de diferencia:
# si figura en dos, uno de los fixtures es un aplazado sin marcar o un duplicado
HORAS_CHOQUE = 20


def _choques(filas) -> dict[int, dict[int, str]]:
    """fixture_id → {team_id: «también figura en …»} para los equipos de `filas`
    que aparecen en OTRO fixture a menos de HORAS_CHOQUE. Los aplazados y
    cancelados no cuentan como choque: ya están marcados como que no se juegan."""
    if not filas:
        return {}
    equipos = sorted({f["home_team_id"] for f in filas} | {f["away_team_id"] for f in filas})
    fechas = [f["date"] for f in filas if f["date"]]
    if not equipos or not fechas:
        return {}
    margen = timedelta(hours=HORAS_CHOQUE)
    desde = (datetime.strptime(min(fechas)[:19], "%Y-%m-%d %H:%M:%S") - margen).strftime("%Y-%m-%d %H:%M:%S")
    hasta = (datetime.strptime(max(fechas)[:19], "%Y-%m-%d %H:%M:%S") + margen).strftime("%Y-%m-%d %H:%M:%S")
    marcas = ",".join("?" * len(equipos))
    otros = saddb.query(
        "sad",
        "SELECT f.id, f.date, f.status_short, f.home_team_id, f.away_team_id, "
        "ht.name AS home_name, at.name AS away_name FROM fixtures f "
        "JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        f"WHERE f.date >= ? AND f.date <= ? AND (f.home_team_id IN ({marcas}) OR f.away_team_id IN ({marcas}))",
        (desde, hasta, *equipos, *equipos),
    )
    por_equipo: dict[int, list] = {}
    for o in otros:
        if (o["status_short"] or "").upper() in _NO_SE_JUGO:
            continue
        for tid in (o["home_team_id"], o["away_team_id"]):
            por_equipo.setdefault(tid, []).append(o)
    out: dict[int, dict[int, str]] = {}
    for f in filas:
        if (f["status_short"] or "").upper() in _NO_SE_JUGO:
            continue   # un aplazado ya se descarta por lo que es; no hace falta el choque
        try:
            t0 = datetime.strptime((f["date"] or "")[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        for tid, nombre in ((f["home_team_id"], f["home_name"]), (f["away_team_id"], f["away_name"])):
            for o in por_equipo.get(tid, []):
                if o["id"] == f["id"]:
                    continue
                try:
                    t1 = datetime.strptime((o["date"] or "")[:19], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if abs((t1 - t0).total_seconds()) < margen.total_seconds():
                    out.setdefault(f["id"], {})[tid] = (
                        f"{nombre} también figura en {o['id']} ({o['home_name']} vs {o['away_name']}, "
                        f"{(o['date'] or '')[:16]} UTC)")
                    break
    return out


def agenda(fecha: date_t | None = None, limite: int = 8, liga_id: int | None = None,
           desde_ahora: bool = False, horas: int = 12,
           incluir_descartados: bool = False, liga: str | None = None,
           grupos: bool = False, segundas: bool = False) -> dict:
    """Los partidos del día ordenados por prioridad — calculado, no preguntado.

    Es el paso 1 del batch: en vez de hacerle deducir a Cowork qué partido
    importa (y pagar esa deducción en tiempo y en búsquedas), la base lo
    resuelve con el criterio numérico del protocolo. Los descartados viajan
    CON su motivo: un descarte sin motivo no se puede auditar.

    Los tres mandos manuales son para apuntar el batch a mano —probar una liga
    concreta, o cubrir lo que queda de esta noche— sin tener que tocar el
    padrón de prioridades:

      liga_id             solo esa liga
      liga                solo las ligas cuyo país o nombre contiene ese texto
                          («España», «LaLiga», «Perú»): lo que uno escribe
                          cuando dice «la liga española, toda»
      desde_ahora + horas ventana rodante desde AHORA (no el día natural: a las
                          20:00 de Lima el día UTC ya cambió, y un filtro por
                          fecha se comería justo los partidos de la noche)
      incluir_descartados los de prioridad 0 entran al final, con su motivo
      grupos / segundas   meten la fase de grupos internacional y las segundas
                          divisiones, que por defecto quedan fuera

    SIN `fecha` NI `desde_ahora` la ventana es «desde ahora y por 24 h». Antes
    era «el día siguiente en UTC», pensado para el batch de las 23:00 de Lima:
    corrido a las 07:00 del miércoles devolvía el JUEVES entero, y Cowork se
    puso a analizar los del jueves. Un prompt que se manda a otra hora tiene
    que entenderse igual: lo que viene, desde este momento.

    **Esto NO contamina la población del caso.** Elegir "Liga MX de esta noche"
    antes del pitazo es una selección ex ante: el caso sigue siendo `ciega`.
    Lo que la contaminaría es elegir un partido PORQUE pasó algo en él. La
    respuesta lo dice con esas palabras para que nadie tenga que deducirlo al
    escribir el veredicto (docs/APRENDIZAJE.md).
    """
    from backend import app as sadapp  # liga_meta y el mapa de posiciones

    if desde_ahora:
        ahora = datetime.now(timezone.utc)
        desde = ahora.strftime("%Y-%m-%d %H:%M:%S")
        hasta = (ahora + timedelta(hours=max(1, horas))).strftime("%Y-%m-%d %H:%M:%S")
        dia = ahora.date()
        ventana = f"desde ahora y por {horas} h"
    elif fecha:
        dia = fecha
        desde, hasta = dia.isoformat(), (dia + timedelta(days=1)).isoformat()
        ventana = f"día completo {dia.isoformat()} (UTC)"
    else:
        ahora = datetime.now(timezone.utc)
        desde = ahora.strftime("%Y-%m-%d %H:%M:%S")
        hasta = (ahora + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        dia = ahora.date()
        desde_ahora, horas = True, 24
        ventana = ("sin fecha: desde ahora y por 24 h (lo que viene, a la hora que se corra; "
                   "para un día concreto pasá fecha=YYYY-MM-DD)")
    cond, params = ["f.date >= ?", "f.date < ?"], [desde, hasta]
    if liga_id is not None:
        cond.append("f.league_id = ?")
        params.append(liga_id)
    liga_txt = normalizar(liga or "").strip()
    ligas_que_casan: set[int] = set()
    if liga_txt:
        # el texto casa contra el nombre de la ingesta («España - La Liga») y el de
        # la tabla leagues con su país: «España», «LaLiga» y «Spain» encuentran lo mismo
        for lid, nombre in _padron().items():
            meta = sadapp.liga_meta(lid)
            texto = normalizar(f"{nombre} {meta.get('nombre') or ''} {meta.get('pais') or ''}")
            if liga_txt in texto:
                ligas_que_casan.add(lid)
        cond.append(f"f.league_id IN ({','.join('?' * len(ligas_que_casan)) or 'NULL'})")
        params.extend(sorted(ligas_que_casan))
    filas = saddb.query(
        "sad",
        "SELECT f.id, f.date, f.league_id, f.league_season, f.league_round, f.status_short, "
        "f.home_team_id, f.away_team_id, ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        "WHERE " + " AND ".join(cond) + " ORDER BY f.date",
        tuple(params),
    )
    choques = _choques(filas)
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
                                  posiciones.get(f["away_team_id"], 0),
                                  f["league_id"], f["league_round"] or "",
                                  grupos=grupos, segundas=segundas)
        estado_fx = (f["status_short"] or "").upper()
        if estado_fx in _NO_SE_JUGO:
            # un aplazado sigue en `fixtures` con su fecha vieja: sin esto
            # entraba a la agenda como si fuera a jugarse
            prio, motivo = 0, f"el partido está {_NO_SE_JUGO[estado_fx]} ({estado_fx}): no se analiza"
        choque = choques.get(f["id"]) or {}
        if len(choque) == len(LADOS):
            # LOS DOS equipos figuran en OTRO partido a pocas horas: este fixture
            # es casi seguro un aplazado que la ingesta todavía no marcó. Cowork
            # gastó una sesión entera en un Pereira–Santa Fe con Santa Fe jugando
            # cuartos de Sudamericana dos horas después y Pereira otro partido
            # cinco horas más tarde.
            prio, motivo = 0, ("probablemente aplazado o duplicado: los dos equipos figuran "
                               "en otro partido a menos de "
                               f"{HORAS_CHOQUE} h ({'; '.join(choque.values())}). Confirmalo "
                               "con `ingesta.diagnostico --dia … --api` antes de analizarlo")
        item = {
            "fixtureId": f["id"],
            "hora": (f["date"] or "")[11:16],
            "partido": f"{f['home_name']} vs {f['away_name']}",
            "equipoA": f["home_name"], "equipoB": f["away_name"],
            # EL DT DE LA BASE VIAJA CON SU EDAD Y SU PROCEDENCIA. Es una
            # alarma, no la verdad: si la prensa de la semana dice otro, manda
            # la prensa y este registro se refresca solo en la próxima corrida
            "dt": {"a": dt_de_base(f["home_team_id"]), "b": dt_de_base(f["away_team_id"])},
            "liga": liga.get("nombre"), "pais": liga.get("pais"),
            "ronda": f["league_round"] or "",
            "prioridad": prio, "motivo": motivo,
            "etiquetas": sorted(etiquetas),
            "parte": ya.get(f["id"], ""),
            # un equipo que también figura en otro partido a pocas horas: uno de
            # los dos fixtures está mal, y el analista tiene que saberlo ANTES
            # de gastar la sesión. Vacío cuando no hay choque.
            "conflicto": "; ".join(choque.values()) if choque else "",
        }
        (candidatos if prio else descartados).append(item)
    candidatos.sort(key=lambda i: (i["prioridad"], i["hora"]))
    # con el mando manual puesto, los de prioridad 0 entran al final y CON su
    # motivo: se ve que no habrían entrado por sí solos
    if incluir_descartados:
        candidatos += sorted(descartados, key=lambda i: i["hora"])
        descartados = []
    manual = bool(liga_id is not None or liga_txt or (desde_ahora and horas != 24) or incluir_descartados
                  or grupos or segundas)
    # PARA PODER RETOMAR DONDE SE CORTÓ. Un batch que se queda sin tokens a
    # mitad de camino tiene que poder volver mañana y seguir, no empezar de
    # cero ni —peor— re-depositar encima de lo que ya estaba bien. Marcar cada
    # candidato con lo que ya hay en la base convierte la agenda en la lista de
    # trabajo pendiente, sin que nadie tenga que llevar la cuenta aparte.
    todos_ids = [x["fixtureId"] for x in candidatos + descartados]
    estados: dict[int, dict] = {}
    if todos_ids:
        with _conectar() as con:
            for r in con.execute(
                f"SELECT fixture_id, estado, xi_json, veredicto_json FROM parte_cowork "
                f"WHERE fixture_id IN ({','.join('?' * len(todos_ids))})", tuple(todos_ids)):
                estados[r["fixture_id"]] = {
                    "tieneParte": True,
                    "onceCerrado": bool(r["xi_json"]) and r["estado"] == "confirmado",
                    "conVeredicto": bool(r["veredicto_json"]),
                }
    for x in candidatos + descartados:
        x.update(estados.get(x["fixtureId"],
                             {"tieneParte": False, "onceCerrado": False, "conVeredicto": False}))
    faltan = [x for x in candidatos[:limite] if not x["tieneParte"]]
    return {
        "porHacer": [x["fixtureId"] for x in faltan],
        "yaHechos": [x["fixtureId"] for x in candidatos[:limite] if x["tieneParte"]],
        "notaReanudacion": (
            f"{len(faltan)} de {len(candidatos[:limite])} sin parte. `porHacer` es la lista "
            "de trabajo: si la corrida se cortó, arrancá por ahí. Re-depositar un parte que "
            "ya estaba REEMPLAZA el anterior, así que no vuelvas sobre `yaHechos` salvo que "
            "quieras rehacerlos."),
        "fecha": dia.isoformat(),
        "ventana": ventana,
        "filtro": {"ligaId": liga_id, "liga": liga or None,
                   "ligasQueCasan": sorted(ligas_que_casan) if liga_txt else None,
                   "desdeAhora": desde_ahora,
                   "horas": horas if desde_ahora else None,
                   "incluirDescartados": incluir_descartados,
                   "grupos": grupos, "segundas": segundas, "manual": manual},
        "analizar": candidatos[:limite],
        "enEspera": candidatos[limite:],
        # QUÉ SE QUEDÓ AFUERA POR EL LÍMITE, Y DE QUÉ TIPO. Con `limite=4` y
        # cuatro llaves internacionales el mismo día, una jornada entera de
        # LaLiga no entra — y desde afuera parecía que la liga no estaba
        # cubierta. El corte se ve, no se deduce.
        "corte": {
            "limite": limite,
            "candidatos": len(candidatos),
            "seAnalizan": len(candidatos[:limite]),
            "quedanFuera": len(candidatos[limite:]),
            "porPrioridad": {str(pr): sum(1 for x in candidatos if x["prioridad"] == pr)
                             for pr in sorted({x["prioridad"] for x in candidatos})},
            "ligasQueQuedanFuera": sorted({x["liga"] for x in candidatos[limite:] if x.get("liga")}),
            "nota": ("todos los candidatos entran" if len(candidatos) <= limite else
                     f"{len(candidatos) - limite} candidatos quedan fuera SOLO por el "
                     f"límite de {limite}: subilo si querés cubrirlos"),
        },
        "descartados": descartados,
        "nota": "CLÁSICO solo se detecta por derbi de ciudad: una rivalidad nacional sin "
                "vecindad geográfica no sale de nuestros datos y puede estar entre los descartados",
        "notaSeleccion": (
            "Filtro manual puesto: elegir una liga o una ventana ANTES del pitazo es "
            "selección ex ante y el caso sigue siendo `ciega` al escribir el veredicto. "
            "Lo que contamina es elegir un partido PORQUE pasó algo en él."
            if manual else
            "Selección estándar por el padrón de prioridades: casos `ciega`."
        ),
    }
