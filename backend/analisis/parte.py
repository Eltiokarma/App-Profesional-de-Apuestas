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
import os
import re
import unicodedata
import sqlite3
from datetime import date as date_t, datetime, timedelta, timezone

from backend import identidad as _identidad
from backend import db as saddb
from backend.analisis import bloque_f, db as efedb, veredicto as vered
from backend.analisis import coherencia as _coherencia
from backend.analisis import modo_fallo as _modo_fallo
from backend.analisis import dtp_cowork as _dtp
from backend.analisis import f1_base as _f1_base
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
# con menos bloques declarados que esto, el EFE no tiene porcentaje (799)
MINIMO_BLOQUES_EFE = 3
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
                    ("coherencia_json", "TEXT"), ("modo_fallo_json", "TEXT"),
                    ("banco_desmentido_json", "TEXT"), ("dt_base_json", "TEXT"),
                    # el último depósito ANTES del pitazo (26/10/2026): lo que separa un
                    # DTP-REHACER ignorado de uno que llegó cuando ya no se podía rehacer
                    ("deposito_previo_en", "TEXT"),
                    # el DT con que se ESCRIBIÓ el parte, cuando se corrige después del
                    # pitazo (27/10/2026, incidencia 712): la corrección arregla el dato,
                    # no el análisis, y el caso sigue en cuarentena
                    ("dt_original_json", "TEXT"))
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
# CUÁNTOS PARTIDOS SE ESTUDIAN POR CORRIDA. Era 8, fijo en la llamada de la
# corrida y repetido en el latido; el 16/10/2026 quedaron 47 candidatos fuera
# solo por ese número (LaLiga, Serie A, Bundesliga, Ligue 1). Un solo sitio,
# para que la corrida y el latido que mide su cobertura no se separen.
AGENDA_LIMITE = max(1, min(30, int(os.environ.get("SAD_AGENDA_LIMITE", "16") or 16)))
# de TODOS los candidatos del padrón de un día, cuántos tienen que tener parte
COBERTURA_META = 0.80

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
    fuera = {"nombre": nombre, "posicion": _txt(j.get("posicion")), "zona": zona,
             "rol": rol, "apps": _txt(j.get("apps"))}
    # EL ID DE LA API CASA LO QUE EL NOMBRE NO PUEDE. La prensa escribe «Joshua
    # Cantt» y «Cristiano»; API-Football los llama «J. Cerro» y «Cris Silva».
    # Por nombre no hay regla que los una (UTC–Cristal, 11/10/2026: el bloque F
    # cerró con dos bajas falsas). Con el `jugadorId` de GET /equipos/{id}/plantilla
    # el cruce con la ficha es exacto.
    jid = j.get("jugadorId")
    if jid not in (None, ""):
        try:
            fuera["jugadorId"] = int(jid)
        except (TypeError, ValueError):
            rechazos.append({"donde": donde, "jugador": nombre,
                             "porque": f"jugadorId no es un número: {jid!r}",
                             "esperado": "el `id` del jugador en GET /equipos/{id}/plantilla"})
    # el mismo jugador con otro id en la API (la tabla F1 los funde, 381): la
    # hoja del partido puede traer cualquiera de los dos
    alt = [int(x) for x in (j.get("idsAlternos") or []) if isinstance(x, (int, str)) and str(x).lstrip("-").isdigit()]
    if alt:
        fuera["idsAlternos"] = alt
    return fuera


def _pron_cadena(v) -> str:
    """El pronóstico de un lado de la cadena, venga plano o como objeto."""
    if isinstance(v, dict):
        return _txt(v.get("pronostico"))
    return _txt(v)


def _sin_dato_bloque(v, letra: str, rechazos: list, donde: str) -> list[str]:
    """Los indicadores del bloque declarados sin dato (`{"score": 4, "sinDato":
    ["B5"]}`): del bloque, sin repetir y dejando al menos uno con dato."""
    if not isinstance(v, dict) or v.get("sinDato") in (None, [], ""):
        return []
    crudos = v["sinDato"] if isinstance(v["sinDato"], list) else [v["sinDato"]]
    out = []
    for x in crudos:
        cod = _txt(x).upper().replace(" ", "")
        if not re.fullmatch(rf"{letra}\d", cod):
            rechazos.append({"donde": f"{donde}.sinDato", "porque": f"{x!r} no es un indicador del bloque {letra}",
                             "esperado": f'["{letra}5"]: el código del indicador sin dato'})
            continue
        if cod not in out:
            out.append(cod)
    if len(out) >= MAX_BLOQUE[letra]:
        rechazos.append({"donde": f"{donde}.sinDato", "porque": "todos los indicadores sin dato: el bloque va en "
                                                               "`excluidos` con su motivo, no con sinDato",
                         "esperado": f'`excluidos.{letra}`: "motivo"'})
        return []
    return out


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


# `jugadorId` también: el prompt lo pide en la tabla y lo natural es repetirlo en
# la baja (Stuttgart–Atlético, 20/10/2026: 4 rechazos por eso, incidencia 310)
_CLAVES_FUERA = {"nombre", "estado", "motivo", "zona", "rol", "posicion", "apps", "jugadorId"}


_DESCANSO = re.compile(r"descans|rotaci|rotad|dosific|reservad", re.I)


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
    # EL NO CONVOCADO POR DESCANSO VA A F4, NO AL IP (rúbrica EFE v1.7, «Descanso
    # planificado»; incidencia 807: los cinco de Osasuna con estado «descanso» se
    # guardaban como «baja», sumaban al IP y encendían F3). Y un estado que no es
    # ninguno de los conocidos se dice, no se vuelve «baja» callado.
    if _DESCANSO.search(estado):
        estado = "descanso"
    elif estado and estado not in ("baja", "duda"):
        rechazos.append({"donde": f"{donde}.estado", "porque": f"estado {f.get('estado')!r} desconocido: se guardó «baja»",
                         "esperado": "baja · duda · descanso (el no convocado por descanso va a F4, no al IP)"})
    out = {"nombre": nombre,
           "estado": estado if estado in ("baja", "duda", "descanso") else "baja",
           "motivo": _txt(f.get("motivo")),
           "zona": _alias(f.get("zona"), _ZONA_ALIAS) or _alias(f.get("posicion"), _ZONA_ALIAS),
           "rol": _alias(f.get("rol"), _ROL_ALIAS)}
    try:
        if f.get("jugadorId") not in (None, ""):
            out["jugadorId"] = int(f["jugadorId"])
    except (TypeError, ValueError):
        rechazos.append({"donde": f"{donde}.jugadorId", "porque": f"no es un id: {f.get('jugadorId')!r}",
                         "esperado": "el `id` del jugador en GET /equipos/{id}/plantilla"})
    return out


_CLAVES_EQUIPO = {"nombre", "bloques", "excluidos", "notas", "dt", "perfil",
                  "plantel", "fuera", "factorX", "sensibilidad", "d3"}
_CLAVES_JUGADOR = {"nombre", "jugador", "jugadorId", "idsAlternos", "posicion", "zona", "rol", "apps", "estado", "motivo"}
_CLAVES_PARTE = {"fixtureId", "version", "generadoEn", "equipos", "alertas", "matchup",
                 "lecturaSad", "lectura_sad", "tde", "timelineEventos", "timelineNarrativa",
                 "cadena", "documentos", "pendientes", "fuentes", "descartados", "notas",
                 "pronostico", "dtp", "matriz"}

# EL VIAJE DE IDA Y VUELTA. Corregir un parte es leer → modificar →
# re-depositar, así que el POST tiene que aceptar TAL CUAL lo que devuelve el
# GET. Lo que el backend calcula vuelve en la lectura como eco: no es un error
# que aparezca en el cuerpo, es que el cuerpo salió de nuestra propia
# respuesta. Se ignora en silencio; delatarlo llenaría el recibo de rechazos
# falsos y escondería los de verdad.
_ECO_PARTE = {"partido", "estado", "creadoEn", "actualizadoEn", "xi", "veredicto",
              "timeline", "rechazos", "perdido", "aviso", "entrada", "cohorte", "cuarentena", "bancoDesmentido",
              "xiConservados", "coherencia", "vsMercado"}
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
    # LA FECHA DE /coachs NO ES DATO: es el mes de la carrera de la API (Carrick
    # «desde 2025-08» cuando llegó en enero) y la agenda ya la marca
    # `desdeConfirmar`. Rayo Zuliano y Metropolitanos (18/10/2026) dejaron `desde`
    # vacío y el parte salió con «2026-01-01 · 9.5 meses» de la base. Solo sirve
    # la llegada VISTA en el banco (fuente `alineacion`).
    if (meses is None and nombre and entrenador_base and entrenador_base.get("nombre")
            and (entrenador_base.get("fuente") or "coachs") == "alineacion"):
        # el mismo apellido que el DT de la base → su fecha de asunción sirve
        from backend.ingesta.jugadores import mismo_nombre_dt
        if mismo_nombre_dt(nombre, entrenador_base["nombre"]) and _fecha(entrenador_base.get("desde")) and partido:
            desde = desde or _txt(entrenador_base.get("desde"))[:10]
            meses = round(max(0, (partido - _fecha(entrenador_base["desde"])).days) / _DIAS_MES, 1)
            origen = "base"
    # «SIN FUENTE, EL `desde` VA VACÍO» es la regla del prompt (COWORK.md, DT): el
    # `desde` que llega vacío A PROPÓSITO es lo declarado, no un hueco (incidencia
    # 827, Prat: rechazo permanente en el recibo de los equipos chicos). El
    # rechazo queda para el `dt` que ni siquiera trae la clave.
    declarado_vacio = "desde" in crudo and not _txt(crudo.get("desde")) and crudo.get("meses") in (None, "")
    if nombre and meses is None and not declarado_vacio:
        # EL MOTIVO, EL DE VERDAD (incidencia 577: Le Havre, Toulouse y Troyes
        # mandaron el mismo nombre que la base y el rechazo decía «no casa»): con
        # el mismo DT, lo que falta es una fecha que sirva
        from backend.ingesta.jugadores import mismo_nombre_dt as _mnd
        base_nom = (entrenador_base or {}).get("nombre") or ""
        if base_nom and _mnd(nombre, base_nom):
            porque = (f"el DT «{nombre}» es el mismo de la base, pero llegó sin `desde` ni `meses` y la fecha "
                      "de la base viene de la carrera de /coachs (el mes de la temporada, no la llegada): "
                      "no sirve")
        else:
            porque = (f"el DT «{nombre}» llegó sin `desde` ni `meses` y no casa con el de la base"
                      + (f" ({base_nom})" if base_nom else ""))
        rechazos.append({
            "donde": f"equipos.{lado}.dt",
            "porque": porque + ": la antigüedad queda en null, no en cero",
            "esperado": '`desde`: "YYYY-MM-DD" (la fecha de asunción, del mes si no se sabe el día)'})
    out = {"nombre": nombre or DT_SIN_ESTABLECER, "meses": meses, "desde": desde, "origenMeses": origen}
    banco = _dt_banco(crudo.get("banco"), rechazos, lado)
    if banco:
        out["banco"] = banco
    return out


# EL DT NO SIEMPRE SE SIENTA EN EL BANCO, Y EL BANCO DE LA API NO SIEMPRE ES EL
# DT. Atlante (Herrera suspendido, dirigió Galindo) y Juárez (la API puso a «T.
# Campos» con Lema en el banco según la prensa), 20/10/2026: el parte tenía el DT
# correcto y la cuarentena automática lo apartaba igual. `dt.banco` declara,
# CON FUENTE, que el banco de ese partido no va a ser (o no fue) el DT: un
# suspendido o ausente con quien lo reemplaza, o una alineación de la API que la
# prensa desmiente. El lado deja de apartar el caso y viaja `disputado` con la
# explicación a la vista; quien la lea puede seguir poniéndolo en cuarentena a mano.
MOTIVOS_BANCO = {"suspendido", "ausente", "api_errada"}


def _dt_banco(crudo, rechazos: list, lado: str) -> dict | None:
    if crudo in (None, "", {}):
        return None
    esperado = ('{"motivo": "suspendido" | "ausente" | "api_errada", "nombre": "quién se sienta", '
                '"fuente": "link o nota de prensa"}')
    if not isinstance(crudo, dict):
        rechazos.append({"donde": f"equipos.{lado}.dt.banco", "porque": f"tiene que ser un objeto, llegó {crudo!r}",
                         "esperado": esperado})
        return None
    motivo = _txt(crudo.get("motivo")).lower()
    fuente = _txt(crudo.get("fuente"))
    nombre = _txt(crudo.get("nombre"))
    if motivo not in MOTIVOS_BANCO:
        rechazos.append({"donde": f"equipos.{lado}.dt.banco.motivo",
                         "porque": f"motivo fuera de la lista: {crudo.get('motivo')!r}", "esperado": esperado})
        return None
    if len(fuente) < DESMENTIDO_FUENTE_MIN:
        rechazos.append({"donde": f"equipos.{lado}.dt.banco.fuente",
                         "porque": "declarar quién se sienta en el banco lleva FUENTE (la nota de la sanción, "
                                   "la ausencia o la prensa del partido)", "esperado": esperado})
        return None
    if len(nombre) > DT_NOMBRE_MAX:
        nombre = ""
    return {"motivo": motivo, "nombre": nombre, "fuente": fuente}


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
        # INDICADORES SIN DATO DENTRO DE UN BLOQUE (incidencia 467, Köln: B5 sin
        # dato y el B se escalaba a mano sobre 5): la rúbrica los saca del
        # denominador; `sinDato: ["B5"]` baja el máximo del bloque uno por cada uno
        sin_dato = _sin_dato_bloque(bloques_in.get(letra), letra, rechazos, f"equipos.{lado}.bloques.{letra}")
        maximo = MAX_BLOQUE[letra] - len(sin_dato)
        score = 0.0 if motivo else _num(crudo, maximo)
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
                                     "esperado": f"0 a {maximo:g}"})
        bloques[letra] = {
            "score": score,
            "max": maximo,
            **({"sinDato": sin_dato} if sin_dato else {}),
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
    ids_tabla = {j.get("jugadorId") for j in plantel if j.get("jugadorId") is not None}
    for f in fuera:
        if normalizar(f["nombre"]) in en_tabla or (f.get("jugadorId") is not None and f["jugadorId"] in ids_tabla):
            continue
        if f["zona"] and f["rol"]:
            plantel.append({"nombre": f["nombre"], "posicion": "", "zona": f["zona"],
                            "rol": f["rol"], "apps": "", "soloBaja": True,
                            **({"jugadorId": f["jugadorId"]} if f.get("jugadorId") is not None else {})})
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
    d3 = None
    if bruto.get("d3") is not None:
        d3 = d3_valor(bruto.get("d3"))
        if d3 is None:
            rechazos.append({"donde": f"equipos.{lado}.d3", "porque": f"D3 no reconocido: {bruto.get('d3')!r}",
                             "esperado": "✅ · 🔶 · ❌ · «sin dato» (o 1 · 0.5 · 0)"})
    return {
        "nombre": canonizar(nombre, equipos_db) if nombre else "",
        "bloques": bloques,
        **({"d3": d3} if d3 else {}),
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
        "espina": _espina(x.get("espina"), rechazos),
    }


ESPINAS = ("positiva", "cero", "negativa", "neutra")
# las palabras del usuario también entran: «crece», «se reinicia», «se va a negativo»
_ESPINA_ALIAS = {"crece": "positiva", "sube": "positiva", "reinicia": "cero", "se reinicia": "cero",
                 "baja": "negativa", "negativo": "negativa", "positivo": "positiva"}
# qué K guió la lectura: la total o la de la condición en que juega HOY (la
# local si es local, la de visita si es visitante). Pedido del usuario
# (15/10/2026): hay equipos que en casa ganan siempre y afuera no, y otros al
# revés; para esos la burbuja que cuenta es la de la condición
GUIAS = ("total", "condicion")
_GUIA_ALIAS = {"condición": "condicion", "local": "condicion", "visita": "condicion",
               "visitante": "condicion", "k local": "condicion", "k visita": "condicion",
               "general": "total", "k total": "total"}


def _espina(x, rechazos: list) -> dict:
    """LA ESPINA DE LA BURBUJA (14/10/2026, pedido del usuario). Las K no
    mejoran el 1X2 del motor en ninguna fórmula (REVENTON §13.3-13.4), pero la
    gráfica —el tope del equipo, la forma de sus rachas, cómo se cortaron sus
    burbujas (a 0 o al otro signo), lo regular que es— le sirve al analista
    para LEER el partido. Esto le pide que diga, por equipo, adónde va su K
    total después de ESTE partido: `positiva` (crece, o arranca si estaba en 0:
    gana), `cero` (se reinicia: empata), `negativa` (pierde) o `neutra` (la
    historia no dice nada), con su porqué. El veredicto lo compara con lo que
    hizo la K (`objetivo.espina`) y las lecciones dicen si la lectura acierta
    más que la frecuencia de cada movimiento.

    `guia` dice qué K guió la lectura: `total` (por defecto) o `condicion` (la
    K local si el equipo juega de local, la de visita si es visitante: la
    burbuja que solo se mueve en esa condición, con su tope y sus reventones).
    El movimiento es el MISMO —ganar hace crecer las dos—; lo que cambia es la
    historia con que se lee, y las lecciones miden cada guía por separado."""
    if not x:
        return {}
    x = _dict(x, rechazos, "lecturaSad.espina",
              '{"a": {"lectura": "positiva|cero|negativa|neutra", "guia": "total|condicion", "porque": "…"}, "b": {…}}')
    out = {}
    for lado in ("a", "b"):
        v = x.get(lado)
        if v is None:
            continue
        if isinstance(v, str):
            v = {"lectura": v}
        if not isinstance(v, dict):
            rechazos.append({"donde": f"lecturaSad.espina.{lado}", "porque": "va un objeto",
                             "esperado": '{"lectura": "positiva|cero|negativa|neutra", "porque": "…"}'})
            continue
        lectura = _txt(v.get("lectura")).lower()
        lectura = _ESPINA_ALIAS.get(lectura, lectura)
        if lectura not in ESPINAS:
            rechazos.append({"donde": f"lecturaSad.espina.{lado}.lectura",
                             "porque": f"«{lectura}» no es una lectura",
                             "esperado": "positiva (crece) · cero (se reinicia) · negativa · neutra"})
            continue
        guia = _txt(v.get("guia")).lower() or "total"
        guia = _GUIA_ALIAS.get(guia, guia)
        if guia not in GUIAS:
            rechazos.append({"donde": f"lecturaSad.espina.{lado}.guia",
                             "porque": f"«{guia}» no es una guía: se tomó la total",
                             "esperado": "total · condicion (la K local si juega de local, la de visita si es visitante)"})
            guia = "total"
        out[lado] = {"lectura": lectura, "guia": guia, "porque": _txt(v.get("porque"))}
    return out


def _goles_acotados(fx) -> dict | None:
    """El intervalo de goles de cada lado y el marcador acotado (REVENTON §17),
    con la historia anterior al partido. Un fallo se declara, no tumba el parte."""
    if not fx:
        return None
    from backend.analisis import goles as _goles
    try:
        return _goles.acotar_fixture(fx)
    except Exception as e:  # noqa: BLE001
        return {"sinDato": f"no se pudo calcular: {e}"}


def _reventon_calculado(fx) -> dict | None:
    """El reventón de la burbuja de cada equipo con ESTE partido como próximo
    (docs/REVENTON.md), calculado AL LEER como el timeline y el bloque F: si la
    historia cambia, la próxima lectura ya lo trae. La familia total, que es
    la que manda (alertas de extremo incluidas), y al lado en `condicion` la K
    de la condición en que juega hoy (local o visita), que es la que la espina
    puede leer con `guia: condicion`. Un fallo se declara en `error`, no tumba
    el parte."""
    if not fx:
        return None
    from datetime import datetime, timezone
    from backend import jugadores as jug
    from backend.analisis import burbuja, familias as _familias
    from backend.app import constantes_de, iso, niveles_de
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # LA VISTA ES SIEMPRE «AL DÍA DEL PARTIDO» (docs/REVENTON.md §9): la historia
    # se corta ESTRICTAMENTE antes de este fixture. Sin el corte, un partido ya
    # jugado entraba en su propia burbuja y la tira del parte terminado gritaba
    # un K-EXTREMO que Cowork no vio antes del pitazo (Sport Boys–Alianza
    # Atlético, 11/10/2026: −18.97 en 2 al depositar, −25.73 en 3 al releer).
    # Para un partido que todavía no se jugó el corte no cambia nada.
    antes = iso(fx["date"])
    jugado = str(fx["date"])[:10] < hoy
    lados = (("a", fx["home_team_id"], fx["away_team_id"], fx["away_name"], "L"),
             ("b", fx["away_team_id"], fx["home_team_id"], fx["home_name"], "V"))
    out = {}
    for lado, tid, rid, rival, cond in lados:
        try:
            filas = list(reversed(constantes_de(tid, 500, antes=antes)))
            nv, nr = niveles_de(tid, 1, antes=antes), niveles_de(rid, 1, antes=antes)
            prox = {"fixtureId": fx["id"], "fecha": str(fx["date"])[:10], "rivalId": rid, "rival": rival,
                    "condicion": cond, "nivelRival": nr[0]["nivel"] if nr else 1.0}
            # la plantilla de hoy no es la de un partido ya jugado: sin dato,
            # como en /burbujas?antesDe (la confianza no pasa de media)
            r = burbuja.analizar(filas, equipo_id=tid, nivel=nv[0]["nivel"] if nv else 0.5,
                                 bin_=nv[0]["bin"] if nv else 0, proximo=prox,
                                 plantilla=None if jugado else jug.plantilla_de(tid), hoy=hoy)
            # la misma regla de escala que la tarjeta (incidencia 295)
            esc = {"comparable": True}
            try:
                from backend.analisis import escala as _escala
                esc = _escala.entre(tid, rid, prox["fecha"], fx["league_id"])
                _escala.bajar_confianza(r["familias"], esc)
                _escala.marcar(r["familias"], esc)
            except Exception:  # noqa: BLE001 — sin escala, como en /burbujas
                pass
            fam = r["familias"]["total"]
            # LA K DE LA CONDICIÓN DE HOY, al lado de la total (15/10/2026,
            # Boca–Vasco: la total estaba en 0 tras un 2-2 y el parte leyó, con
            # razón, la K local de Boca +18 y la de visita de Vasco +6, las dos
            # en riesgo muy alto; la pantalla mostraba todo en null y la línea
            # del analista quedaba sin un número que la sostuviera)
            fc = r["familias"]["local" if cond == "L" else "visita"]
            out[lado] = {"actual": fam["actual"], "riesgo": fam["riesgo"], "rival": fam["rival"],
                         "extremo": fam.get("extremo"),
                         "espinaTarjeta": burbuja.espina_tarjeta(
                             (fam.get("actual") or {}).get("signo"), (fam.get("riesgo") or {}).get("movimiento")),
                         "sinTarjeta": burbuja.sin_tarjeta(fam),   # el porqué del null (866)
                         "condicion": {"familia": "local" if cond == "L" else "visita",
                                       "actual": fc["actual"], "riesgo": fc["riesgo"], "rival": fc["rival"],
                                       "extremo": fc.get("extremo"),
                                       "espinaTarjeta": burbuja.espina_tarjeta(
                                           (fc.get("actual") or {}).get("signo"),
                                           (fc.get("riesgo") or {}).get("movimiento")),
                                       "sinTarjeta": burbuja.sin_tarjeta(fc)},
                         "estabilidad": r["estabilidad"]["grado"], "partidos": r["partidos"], "aviso": r["aviso"],
                         # las OTRAS burbujas contadas (REVENTON §15-15.1): para
                         # la narrativa del parte, con la misma historia cortada
                         "otrasFamilias": _familias.describir(
                             filas, cond, fx["home_name"] if lado == "a" else fx["away_name"])}
            # la tarjeta y el perfil DC con la MARCA de escala, como en /burbujas
            # (22/10/2026: se marca, no se mueve ningún número)
            if not esc.get("comparable", True):
                from backend.analisis import escala as _escala
                _escala.marcar_tarjeta(out[lado]["espinaTarjeta"], esc)
                _escala.marcar_tarjeta(out[lado]["condicion"]["espinaTarjeta"], esc)
                _escala.marcar_perfil(out[lado]["otrasFamilias"], esc)
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
                "inflada": ext.get("inflada"),
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
                       "declararlo en lecturaSad.reventon y en el pronóstico"
                       + (" · INFLADA: la mitad o más de la racha son amistosos —cuentan, pero el "
                          "récord se armó fuera de la competición—" if ext.get("inflada") else ""),
            "inflada": ext.get("inflada"),
        })
    # LA K DE LA CONDICIÓN EN SU EXTREMO TAMBIÉN SE DICE (Cagliari de visita
    # —récord de 3 victorias en 132 partidos afuera— con la total en 0, PSV de
    # visita, Sabah de local: veredictos del 18-19/10/2026, cuatro incidencias).
    # Tipo `dato`: manda la total en el riesgo y en la regla dura del prompt,
    # pero esta burbuja es la que se juega hoy y la tira no la mostraba.
    for lado in LADOS:
        r = (reventon or {}).get(lado) or {}
        if (r.get("extremo") or {}).get("activo"):
            continue  # ya grita la total
        c = r.get("condicion") or {}
        ext, act = c.get("extremo") or {}, c.get("actual") or {}
        k = act.get("k")
        if k is None or not (ext.get("activo") or ext.get("cerca")):
            continue
        donde = "de local" if c.get("familia") == "local" else "de visita"
        # con la total en la franja alta (K-CERCA-EXTREMO en la misma tira) no
        # se puede decir «no está en extremo» (Leones del Norte, incidencia 583)
        total = ("La total no está en su récord (sí en su franja alta, K-CERCA-EXTREMO)"
                 if (r.get("extremo") or {}).get("cerca") else "La total no está en extremo")
        out.append({
            # récord → K-EXTREMO-CONDICION; franja alta sin récord → su propio
            # código, como la total (incidencia 494: cuatro corridas lo pidieron)
            "codigo": "K-EXTREMO-CONDICION" if ext.get("activo") else "K-CERCA-EXTREMO-CONDICION",
            "equipo": lado, "tipo": "dato",
            "detalle": f"{nombres.get(lado, lado)}: burbuja {donde} K {k:+.2f} "
                       + ("en su máximo histórico" if ext.get("activo") else "en la franja más alta de su historia")
                       + f" ({' · '.join(ext.get('motivos') or [])}). {total} y es la que "
                         f"manda en el riesgo, pero hoy juega {donde}: no cargar fuerte a que esa racha siga",
            "inflada": ext.get("inflada"),
        })
    return out


def alertas_familias(reventon: dict | None, nombres: dict) -> list[dict]:
    """FAMILIA-RECORD: una por lado con alguna de las OTRAS burbujas (doble
    oportunidad, márgenes, goles) grande y en su récord (`familias.es_cuidado`).
    Pedido del usuario (17/10/2026, Everton 0-2 Chelsea con su doble
    oportunidad de local enorme): se lee como CUIDADO con la carga, igual que
    K-EXTREMO, pero de tipo `dato` porque el backtest no dice que se corte más
    (§15). No mueve el riesgo ni el 1X2; si se corta, el veredicto lo rastrea
    (`objetivo.otrasFamilias`)."""
    out = []
    for lado in LADOS:
        of = (((reventon or {}).get(lado) or {}).get("otrasFamilias") or {})
        grandes = [f for f in of.get("familias") or [] if f.get("cuidado")]
        if not grandes:
            continue
        # EL RÉCORD IGUALADO TIENE PRECEDENTE (incidencia 723, Huancayo: «récord
        # igualado» dentro de un «terreno sin precedente»): se dice aparte, como
        # el récord de racha igualado de la K (67), que queda en ámbar
        supera = any(f["record"] == "supera" for f in grandes)
        out.append({
            "codigo": "FAMILIA-RECORD", "equipo": lado, "tipo": "dato",
            "detalle": f"{nombres.get(lado, lado)}: " + " · ".join(
                f"{f['partidos']} {_AMBITO_TXT.get(f['ambito'], f['ambito'])} "
                f"{_estado_familia(f)} (récord{'' if f['record'] == 'supera' else ' igualado'})"
                for f in grandes)
                + (". Terreno sin precedente: cuidado con cargar a que siga" if supera else
                   ". Igualan su récord (ya lo vivió una vez): cuidado con cargar a que siga")
                + ". No es probabilidad de corte "
                  "(en su récord estas burbujas se sostienen, REVENTON §15); si se corta, hay una causa que "
                  "rastrear en el veredicto",
        })
    return out


def espina_vs_riesgo(reventon: dict | None, espina: dict | None) -> list[dict]:
    """La espina declarada contra el riesgo calculado, por lado.

    Albion–Torque (18/10/2026): la tarjeta decía «riesgo de reventón ALTO»
    para la racha negativa de Albion y el ensayo la leía «neutra» sin nombrar
    el riesgo; Albion ganó 2-1. Leer contra el riesgo está permitido —la
    espina mide la lectura del analista, no la del modelo—, pero tiene que
    decirse: si no, quien lee ve dos cosas que se contradicen y no sabe a cuál
    creerle. Con riesgo alto/muy alto, una espina que sigue la racha o neutra
    va contra él; con riesgo bajo, una que la corta."""
    out = []
    for lado in LADOS:
        e = (espina or {}).get(lado) or {}
        lect = e.get("lectura")
        r = (reventon or {}).get(lado) or {}
        if e.get("guia") == "condicion" and r.get("condicion"):
            r = r["condicion"]
        nivel = (r.get("riesgo") or {}).get("nivel")
        signo = (r.get("actual") or {}).get("signo")
        if not lect or not nivel or signo not in ("+", "-"):
            continue
        sigue = "positiva" if signo == "+" else "negativa"
        corta = {"cero", "negativa" if signo == "+" else "positiva"}
        if nivel in ("alto", "muy alto") and lect in (sigue, "neutra"):
            como = "la lee seguir" if lect == sigue else "la lee neutra"
        elif nivel == "bajo" and lect in corta:
            como = "la lee cortarse"
        else:
            continue
        out.append({"lado": lado, "nivel": nivel, "signo": signo, "lectura": lect, "como": como,
                    "guia": e.get("guia") or "total",
                    "dicho": "riesgo" in (e.get("porque") or "").lower()})
    return out


def espina_vs_tarjeta(reventon: dict | None, espina: dict | None) -> list[dict]:
    """La espina declarada contra la espina FUERTE de la tarjeta, por lado
    (19/10/2026, pedido del usuario: la tarjeta tiene base estadística y los
    skills la leen encima). Ir contra ella vale —eso es lo que se mide—, pero
    el `porque` dice «contra la tarjeta porque <lo que dicen los skills>». La
    tarjeta débil no se cobra: ahí deciden los skills. Usa la tarjeta de la
    guía que declaró el parte."""
    out = []
    for lado in LADOS:
        e = (espina or {}).get(lado) or {}
        lect = e.get("lectura")
        r = (reventon or {}).get(lado) or {}
        if e.get("guia") == "condicion" and r.get("condicion"):
            r = r["condicion"]
        t = r.get("espinaTarjeta")
        if not lect or lect == "neutra" or not t or t.get("fuerza") != "fuerte" or lect == t.get("lectura"):
            continue
        out.append({"lado": lado, "lectura": lect, "tarjeta": t, "guia": e.get("guia") or "total",
                    "dicho": "tarjeta" in (e.get("porque") or "").lower()})
    return out


def alertas_espina(reventon: dict | None, espina: dict | None, nombres: dict) -> list[dict]:
    """Solo la lectura contra el riesgo que el `porque` NO explica: la que ya lo
    nombra no se contradice con nada y a la tira solo la ensuciaba (Fenerbahçe y
    Slavia, 20/10/2026, incidencia 291). El detalle queda en el parte."""
    return [{
        "codigo": "ESPINA-VS-RIESGO", "equipo": x["lado"], "tipo": "dato",
        "detalle": (f"{nombres.get(x['lado'], x['lado'])}: el riesgo calculado de su racha {x['signo']} es "
                    f"{x['nivel'].upper()} y la espina {x['como']} ({x['lectura']}). Leer contra el riesgo vale, "
                    "pero se dice: " + ("el `porque` lo explica" if x["dicho"] else
                                        "el `porque` no nombra el riesgo —quien lee ve dos cosas que se contradicen—")),
    } for x in espina_vs_riesgo(reventon, espina) if not x["dicho"]]


# el `porque` que nombra el extremo —y con él el hecho que sostiene la racha—
_NOMBRA_EXTREMO = re.compile(r"extremo|r[eé]cord|techo|m[aá]ximo|franja alta", re.I)


def espina_sigue_en_extremo(reventon: dict | None, espina: dict | None) -> list[dict]:
    """La espina que dice que la racha SIGUE con esa burbuja en su récord o en
    la franja alta (K-EXTREMO · K-CERCA-EXTREMO, la total o la de la condición
    que guía la lectura). 25/10/2026: Leones–Libertad (K de Libertad en su
    récord de 175 partidos, espina «sigue», reventó con goleada) y Nacional–
    Braga (K −32.8 cerca del extremo, espina negativa siguiendo la tarjeta
    fuerte, reventó). El extremo no puntúa en el riesgo, pero es la regla
    dura del prompt: no se carga a que la racha siga."""
    out = []
    for lado in LADOS:
        e = (espina or {}).get(lado) or {}
        lect = e.get("lectura")
        r = (reventon or {}).get(lado) or {}
        if not lect or not r:
            continue
        candidatas = [("total", r)]
        if r.get("condicion"):
            candidatas.append(("de local" if (r["condicion"].get("familia") == "local") else "de visita",
                               r["condicion"]))
        for donde, b in candidatas:
            ext, act = b.get("extremo") or {}, b.get("actual") or {}
            signo = act.get("signo")
            if signo not in ("+", "-") or not (ext.get("activo") or ext.get("cerca")):
                continue
            if lect == ("positiva" if signo == "+" else "negativa"):
                out.append({"lado": lado, "donde": donde, "signo": signo, "k": act.get("k"),
                            "nivel": "récord" if ext.get("activo") else "franja alta",
                            "lectura": lect, "dicho": bool(_NOMBRA_EXTREMO.search(e.get("porque") or ""))})
                break
    return out


# UNA REGLA NO SE COBRA HACIA ATRÁS (27/10/2026): ESPINA-SIGUE-EN-EXTREMO y
# EFE-EMPATE-TECNICO nacieron el 26/10 (merge a las 05:02 UTC). En un parte
# creado antes siguen a la vista —el dato es el mismo— pero marcadas
# `posteriorAlParte`: el veredicto no las cuenta como regla incumplida.
REGLAS_CALCULADAS_DESDE = {"ESPINA-SIGUE-EN-EXTREMO": "2026-10-26 05:00:00",
                           "EFE-EMPATE-TECNICO": "2026-10-26 05:00:00"}


def marcar_posteriores(alertas: list[dict], creado_en: str | None) -> list[dict]:
    t = str(creado_en or "").replace("T", " ")[:19]
    if not t:
        return alertas
    for a in alertas:
        desde = REGLAS_CALCULADAS_DESDE.get(a.get("codigo"))
        if desde and t < desde:
            a["posteriorAlParte"] = True
            a["detalle"] = (a.get("detalle") or "") + (
                f" · REGLA POSTERIOR A ESTE PARTE (vigente desde el {desde[:10]}): se muestra, no se le cobra")
    return alertas


def alertas_espina_extremo(reventon: dict | None, espina: dict | None, nombres: dict) -> list[dict]:
    """Solo la que el `porque` NO explica, como ESPINA-VS-RIESGO: la que nombra
    el extremo ya cumple la regla —el recibo no la cobra— y a la tira solo la
    ensuciaba (incidencias 874 y 775: PSG, Brugge y Casa Pia pintadas como dato
    con el récord escrito en el `porque`)."""
    return [{
        "codigo": "ESPINA-SIGUE-EN-EXTREMO", "equipo": x["lado"], "tipo": "dato",
        "detalle": (f"{nombres.get(x['lado'], x['lado'])}: la espina dice que la racha {x['signo']} SIGUE "
                    f"({x['lectura']}) con la burbuja {x['donde']} en su {x['nivel']}"
                    + (f" (K {x['k']:+.2f})" if isinstance(x.get("k"), (int, float)) else "")
                    + ": con K-EXTREMO o K-CERCA-EXTREMO la espina no declara que la racha sigue —se dice "
                      "«cero» o «neutra», o se nombra el hecho del partido que la sostiene— y el 1X2 no se "
                      "carga a la continuidad (Leones–Libertad y Nacional–Braga, 25/10/2026)"),
    } for x in espina_sigue_en_extremo(reventon, espina) if not x["dicho"]]


# EFE v1.8 (28/10/2026): T.54 se revisa en LOS DOS lados con la fecha del DT.
# Angers–Lorient: los dos DT habían llegado en junio y T.54 se declaró solo en
# un lado; con T.54 en los dos, la brecha 44/68 era empate técnico (0-0). El
# umbral de 6 meses es el que ya define T.54; esto solo avisa que falta.
T54_MESES = 6


def alertas_t54_sin_declarar(parte: dict, alertas: list[dict], nombres: dict) -> list[dict]:
    out = []
    for lado in LADOS:
        dt = ((parte.get("equipos") or {}).get(lado) or {}).get("dt") or {}
        meses = dt.get("meses") if isinstance(dt, dict) else None
        if not isinstance(meses, (int, float)) or meses >= T54_MESES:
            continue
        if any(str(a.get("codigo") or "").startswith("T.54") and a.get("equipo") in (lado, "ambos")
               for a in alertas or []):
            continue
        out.append({
            "codigo": "T.54-SIN-DECLARAR", "equipo": lado, "tipo": "dato", "meses": round(float(meses), 1),
            "detalle": (f"{nombres.get(lado, lado)}: el DT ({dt.get('nombre') or 'sin nombre'}) lleva "
                        f"{meses:.1f} meses y el parte no declara T.54 ni T.54-B en ese lado. Con un DT de "
                        "menos de 6 meses, T.54 o T.54-B se declara siempre, en los dos lados (EFE v1.8); "
                        "para la brecha del EFE cuenta como T.54"),
        })
    return out


# EFE v1.7: el porcentaje dice cuánto creerle a la K de cada equipo, no quién
# gana, y la brecha entre los dos solo se lee en la misma base y sin R-KT.2 ni
# T.54 en un lado. El 25/10/2026 nueve partes usaron esa brecha para ordenar el
# partido o empujar el 1X2 con T.54 o ESCALA-LIGAS a la vista (Aucas, Barça–
# Madrid, Leones–Libertad, Nacional–Braga, Sporting–Viseu, Toulouse…): una
# regla que se incumple tanto se calcula, no se repite.
BRECHA_EMPATE_MIN = 5.0
_CORTAN_BRECHA = ("T.54", "R-KT.2")


def empate_tecnico(porcentajes: dict, alertas: list[dict]) -> dict | None:
    pa, pb = porcentajes.get("a"), porcentajes.get("b")
    if not isinstance(pa, (int, float)) or not isinstance(pb, (int, float)) or abs(pa - pb) < BRECHA_EMPATE_MIN:
        return None
    motivos = []
    for a in alertas or []:
        cod = str(a.get("codigo") or "")
        lado = a.get("equipo") or ""
        if cod == "ESCALA-LIGAS":
            motivos.append("ESCALA-LIGAS")
        elif any(cod.startswith(c) for c in _CORTAN_BRECHA) and lado in ("a", "b", "ambos"):
            motivos.append(f"{cod.split()[0]} en {'los dos' if lado == 'ambos' else lado}")
    motivos = list(dict.fromkeys(motivos))
    if not motivos:
        return None
    return {"a": pa, "b": pb, "brecha": round(abs(pa - pb), 1), "motivos": motivos}


def alerta_empate_tecnico(porcentajes: dict, alertas: list[dict], nombres: dict) -> list[dict]:
    e = empate_tecnico(porcentajes, alertas)
    if not e:
        return []
    return [{
        "codigo": "EFE-EMPATE-TECNICO", "equipo": "global", "tipo": "dato",
        "detalle": (f"EFE {nombres.get('a', 'a')} {e['a']:.1f} % contra {nombres.get('b', 'b')} {e['b']:.1f} % "
                    f"(brecha {e['brecha']:.1f}) con {', '.join(e['motivos'])}: es EMPATE TÉCNICO DE FORMACIÓN "
                    "(EFE v1.7). El porcentaje dice cuánto creerle a la K de cada equipo, no quién gana: la "
                    "brecha no ordena el partido, no hace favorito a nadie en el matchup ni empuja el 1X2"),
        "brecha": e["brecha"], "motivos": e["motivos"],
    }]


_AMBITO_TXT = {"local": "de local", "visita": "de visita", "total": "en total"}
def _estado_familia(f: dict) -> str:
    """El estado en que está la burbuja, con el par (sí, no) de la narrativa.
    Una burbuja en curso puede ser del «no»: Nice llevaba 5 de visita SIN
    anotar y la alerta decía «5 de visita anotando» (18/10/2026, inc. 158/30)."""
    from backend.analisis.familias import NARRADAS
    par = next(((si, no) for c, si, no in NARRADAS if c == f.get("familia")), None)
    if not par:
        return f.get("familia", "")
    return par[0] if f.get("valor", True) else par[1]


# ── la escala del nivel entre ligas ──────────────────────────────────────────

def _liga_domestica(team_id: int, fecha: str | None) -> dict | None:
    """La liga contra la que se calcula el nivel de un equipo: la MÁS FRECUENTE
    en sus partidos terminados del último año antes de `fecha`, fuera de los
    torneos internacionales de clubes, el Mundial, los amistosos y las COPAS
    nacionales (una copa no es una base: Bentín en la Copa Bicentenario, la FA
    Cup). Con solo copas, `categoria: "fuera del padrón"` (`escala.base_de`).
    None si no hay partidos (equipo nuevo en la base)."""
    from backend.analisis import escala
    return escala.base_de(team_id, fecha)


# UNA SEGUNDA QUE NO ESTÁ EN LAS LISTAS SE RECONOCE POR EL NOMBRE. Marítimo
# (Segunda Liga de Portugal, 95) salía «primera» y «misma base» frente a la
# Primeira Liga del Vitória (incidencia 407): las listas son del padrón y de la
# ingesta, y una liga que entra por un equipo de interés no está en ninguna.
# La «Challenger Pro League» de Bélgica (145) no casaba con «challenge league»
# y Lommel y Beveren salían «primera, misma base» frente a la Jupiler
# (incidencias 489 y 514).
_SEGUNDA_RE = re.compile(r"\b(segunda|serie b|ligue 2|2\. ?bundesliga|championship|league (?:one|two)|primera b|"
                         r"b nacional|primera nacional|nacional b|liga de expansi[oó]n|liga portugal 2|liga 2|"
                         r"divisi[oó]n intermedia|ascenso|eerste divisie|keuken kampioen divisie|1\. lig|"
                         r"challenger? (?:pro )?league|superettan|obos-ligaen|1\. division|prva liga 2|"
                         r"segunda liga|2\. liga)\b", re.I)


def _segunda(liga_id: int, nombre: str | None = None) -> bool:
    """Segunda división o torneo menor, con la lista de la ingesta si está a
    mano y, si no, por el nombre de la liga."""
    if liga_id in SEGUNDAS:
        return True
    try:
        from backend.ingesta.extractor import LIGAS_MENORES
        if liga_id in LIGAS_MENORES:
            return True
    except Exception:  # noqa: BLE001 — sin la ingesta importable (tests aislados) se decide por el nombre
        pass
    if nombre is None and liga_id is not None:
        try:
            from backend.app import liga_meta
            nombre = liga_meta(liga_id).get("nombre")
        except Exception:  # noqa: BLE001 — liga sin metadatos en la base: no se la marca segunda
            nombre = None
    return bool(nombre) and bool(_SEGUNDA_RE.search(nombre))


def misma_base(la: dict | None, lb: dict | None) -> bool:
    """¿Los dos niveles salen de la misma base de rivales? Misma liga, o el
    mismo país en la misma categoría (Uruguay y Paraguay parten la primera en
    Apertura/Clausura con dos ids: son la misma base)."""
    if not la or not lb:
        return True  # sin dato no se grita nada: la alerta es para lo que se sabe
    if la["id"] == lb["id"]:
        return True
    return bool(la.get("pais")) and la.get("pais") == lb.get("pais") and _segunda(la["id"]) == _segunda(lb["id"])


def _dt_con_expulsion(fixture_id: int, dts: dict) -> dict:
    """El DT de la agenda dice si viene de una roja (incidencia 920: Almirón,
    expulsado el 25/10, salía sin marca): `expulsado` con el detalle de
    `sanciones`, y el parte lo declara en `dt.banco`."""
    try:
        from backend import sanciones
        sanc = sanciones.de_fixture(fixture_id)
    except Exception:  # noqa: BLE001 — sin eventos no se infiere: el DT viaja como estaba
        return dts
    for lado, d in dts.items():
        ct = (sanc.get(lado) or {}).get("cuerpoTecnico") or []
        if d is not None and ct:
            dts[lado] = {**d, "expulsado": {"nombre": ct[0]["nombre"], "fecha": ct[0]["fecha"],
                                            "detalle": ct[0]["detalle"]}}
    return dts


DT_FIABLE_DIAS = 14   # un registro más viejo que esto se marca para confirmar en prensa
DT_ONCES_SOSTIENEN = 3   # las últimas hojas que pueden sostener al DT de /coachs


def _bancos_recientes(team_id: int) -> list[str]:
    """El DT de las últimas `DT_ONCES_SOSTIENEN` hojas del equipo, de la más
    nueva a la más vieja («» = la hoja vino sin entrenador)."""
    try:
        return [r["e"] or "" for r in saddb.query(
            "sad", "SELECT a.fixture_id, MAX(COALESCE(a.entrenador, '')) AS e, MAX(f.date) AS d "
                   "FROM alineaciones a JOIN fixtures f ON f.id = a.fixture_id WHERE a.team_id=? "
                   "GROUP BY a.fixture_id ORDER BY d DESC LIMIT ?", (team_id, DT_ONCES_SOSTIENEN))]
    except Exception:  # noqa: BLE001 — base sin la ficha de partido: no hay hojas que mirar
        return []


def _coachs_sin_sosten(nombre: str, bancos: list[str]) -> bool:
    """El DT de /coachs que ninguna hoja reciente sostiene, con la última hoja
    SIN entrenador (31/10/2026, incidencia 691, decisión del usuario: Pasto con
    «Jonathan Risueno» fiable por /coachs dirigiendo Diego Merino desde el
    12/10, y la alineación de la API sin DT; también Águilas y Tolima)."""
    return bool(bancos) and not bancos[0] and not any(b and mismo_dt(nombre, b) for b in bancos)


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
    sin_sosten = (e.get("fuente") != "alineacion" and fiable
                  and _coachs_sin_sosten(e.get("nombre") or "", _bancos_recientes(team_id)))
    if sin_sosten:
        fiable = False
    return {**e, "edadDias": edad, "fiable": fiable,
            "nota": ("visto en el banco en el último partido" if e.get("fuente") == "alineacion" else
                     f"carrera de la API, registro de hace {edad} días" if edad is not None else
                     "carrera de la API, sin fecha de registro")
                    + (" · la última hoja vino sin DT y ninguna de las últimas lo sostiene" if sin_sosten else "")
                    + ("" if fiable else " · CONFIRMAR EN PRENSA: si la red dice otro, manda la red"),
            # EL NOMBRE PUEDE SER FIABLE Y LA FECHA NO. /coachs trae la llegada
            # como «el mes de la temporada» (Carrick «desde 2025-08» cuando llegó
            # en enero) y 12 equipos del 18/10/2026 salieron con la fecha mal; el
            # parte anterior del Alavés puntuó el bloque A en 0 por eso. La
            # antigüedad se confirma en prensa y se declara en `dt.desde`.
            "desdeConfirmar": e.get("fuente") != "alineacion" or not e.get("desde"),
            "desdeNota": ("la fecha de llegada es el primer partido visto en el banco" if
                          e.get("fuente") == "alineacion" and e.get("desde") else
                          "la fecha de llegada de la base es aproximada (mes de la carrera de la API, o no se "
                          "vio la llegada): confirmala en prensa antes de puntuar el bloque A")}


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


# la identidad del DT vive en backend/identidad.py (30/10/2026)
def _tokens_dt(nombre: str) -> set[str]:
    return set(_identidad.tokens_dt(nombre))


_mismo_apellido = _identidad.apellido_dt
mismo_dt = _identidad.mismo_dt


def dt_equivocado(parte: dict, fixture_id: int, desmentidos: "dict | None" = None) -> list[dict]:
    """Los lados donde el DT que declaró el parte NO es el que se sentó en el
    banco de ESE partido (la alineación que capturó la ficha).

    Es un criterio de INSUMO, no de resultado: dice que el parte se escribió
    con el entrenador equivocado —el error de la alineación rancia del 22/09—,
    no cómo terminó el partido. Se mira después del pitazo solo porque el
    banco se conoce entonces. Sin alineación capturada (Colombia, Uruguay, o
    la ficha aún no corrió) no se puede comprobar y no se marca nada: ahí la
    cuarentena es a mano.

    `desmentidos` son los lados donde el usuario probó con una fuente que el
    BANCO de la API es el que está mal (Jaguares 11/10/2026: la alineación
    traía a Bodhert, que se había ido el 28/09). Esos lados no se comparan:
    el criterio sigue siendo de insumo, pero el insumo que falla es la API."""
    fx = _fixture(fixture_id)
    if not fx:
        return []
    out = []
    malos = set(sin_dt(parte)) | set(desmentidos or {})
    base_al_depositar = dt_base_al_depositar(fixture_id)
    originales = dt_original(fixture_id)
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        if lado in malos:
            continue
        dt = ((parte.get("equipos") or {}).get(lado) or {}).get("dt") or {}
        nombre = _txt(dt.get("nombre")) if isinstance(dt, dict) else ""
        # CORREGIDO DESPUÉS DEL PITAZO: manda el DT con que se escribió el
        # análisis (incidencia 712, Biaggio por Hernández): el EFE, el TDE y el
        # DTP se puntuaron sobre él, y corregir el nombre no los rehace
        orig = (originales.get(lado) or {}).get("nombre") if originales else ""
        if orig:
            nombre = orig
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
            # EL PARTE QUE CONTRADIJO A LA BASE NO COPIÓ UN DT RANCIO. El error
            # que esto atrapa es el del 22/09: el parte se escribió con el DT
            # viejo que tenía la base y en el banco se sentó otro. Si al
            # depositar la base decía OTRO nombre que el parte (saltó
            # DT-DISCREPANCIA), el parte fue a la prensa a propósito, y que el
            # banco de la API no le dé la razón es prensa contra API, no un
            # insumo roto: San José (Costa / banco «Baldivieso», el DT viejo) y
            # Real Potosí (tres nombres) caían en cuarentena falsa (17/10/2026).
            # Va como `disputado`: se ve, pero no aparta el caso.
            base = (base_al_depositar.get(lado) or "") if base_al_depositar else ""
            disputado = bool(_tokens_dt(base)) and not mismo_dt(nombre, base)
            # el parte declaró con fuente que el banco no iba a ser (o no fue)
            # el DT —suspendido, ausente, o la API equivocada— (_dt_banco)
            declarado = dt.get("banco") if isinstance(dt.get("banco"), dict) else None
            if declarado and declarado.get("motivo") in MOTIVOS_BANCO and declarado.get("fuente"):
                if declarado.get("nombre") and mismo_dt(declarado["nombre"], banco):
                    continue   # se sentó quien el parte dijo: no hay nada que comparar
                out.append({"lado": lado, "parte": nombre, "banco": banco, "disputado": True,
                            "bancoDeclarado": declarado})
                continue
            out.append({"lado": lado, "parte": nombre, "banco": banco,
                        **({"disputado": True, "baseAlDepositar": base} if disputado else {})})
    return out


def dt_base_al_depositar(fixture_id: int) -> dict:
    """{lado: nombre} del DT que tenía la base cuando se depositó el parte por
    primera vez. Vacío en los partes anteriores al 17/10/2026."""
    try:
        with _conectar() as con:
            fila = con.execute("SELECT dt_base_json FROM parte_cowork WHERE fixture_id=?",
                               (fixture_id,)).fetchone()
        return json.loads(fila["dt_base_json"]) if fila and fila["dt_base_json"] else {}
    except (sqlite3.Error, ValueError):
        return {}


def dt_original(fixture_id: int) -> dict:
    """{lado: {nombre, corregidoEn, por}} del DT con que se escribió el parte,
    sellado la PRIMERA vez que `corregir_dt` lo cambia después del pitazo."""
    try:
        with _conectar() as con:
            fila = con.execute("SELECT dt_original_json FROM parte_cowork WHERE fixture_id=?",
                               (fixture_id,)).fetchone()
        return json.loads(fila["dt_original_json"]) if fila and fila["dt_original_json"] else {}
    except (sqlite3.Error, ValueError):
        return {}


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
        # DESPUÉS DEL PITAZO la corrección arregla el dato, no el análisis
        # (incidencia 712): se sella el DT con que se escribió el parte, una sola
        # vez por lado, y `dt_equivocado` lo sigue mirando. Antes del pitazo no:
        # ahí el parte todavía se puede rehacer con el DT bueno.
        sellado = None
        cuando = efedb.ahora()
        if ahora and fx and not _antes_del_pitazo(cuando, fx["date"]):
            prev = con.execute("SELECT dt_original_json FROM parte_cowork WHERE fixture_id=?",
                               (fixture_id,)).fetchone()
            orig = json.loads(prev["dt_original_json"]) if prev and prev["dt_original_json"] else {}
            for lado in ahora:
                viejo = antes.get(lado) if isinstance(antes.get(lado), dict) else {}
                n_viejo = _txt((viejo or {}).get("nombre"))
                if lado not in orig and n_viejo and not mismo_dt(n_viejo, _txt(ahora[lado].get("nombre"))):
                    orig[lado] = {"nombre": n_viejo, "corregidoEn": cuando, "por": _txt(ahora[lado].get("nombre"))}
            sellado = orig or None
        if ahora:
            con.execute("UPDATE parte_cowork SET parte_json=?, actualizado_en=?"
                        + (", dt_original_json=?" if sellado else "") + " WHERE fixture_id=?",
                        (json.dumps(parte, ensure_ascii=False), cuando,
                         *((json.dumps(sellado, ensure_ascii=False),) if sellado else ()), fixture_id))
    return {
        "fixtureId": fixture_id,
        "antes": antes,
        "ahora": ahora,
        "rechazos": rechazos,
        # lo que ve el aprendizaje después del cambio: vacío = el DT del parte
        # ya casa con el que se sentó en el banco (o no hay alineación)
        "dtEquivocado": dt_equivocado(parte, fixture_id, bancos_desmentidos(fixture_id)),
        "sinDt": sin_dt(parte),
        # el DT con que se escribió el parte, si se corrigió después del pitazo:
        # el caso sigue en cuarentena (incidencia 712)
        "dtOriginal": dt_original(fixture_id),
    }


# EL BANCO DE LA API TAMBIÉN SE EQUIVOCA. La cuarentena automática por DT
# equivocado le cree a la alineación que trae API-Football, y esa alineación a
# veces arrastra a un DT que ya se fue (Jaguares–Tolima del 11/10/2026: «H.
# Bodhert», salido el 28/09; antes Cusco, Nacional, Libertad, Auxerre). Sin esto
# el único camino era cambiar el DT del parte por el de la API, o sea mentir.
# Lo pone el usuario con el token maestro, POR LADO y con la FUENTE que prueba
# que el banco está mal; no toca el parte, ni el veredicto, ni la cohorte.
DESMENTIDO_FUENTE_MIN = 8


def bancos_desmentidos(fixture_id: int) -> dict:
    with _conectar() as con:
        fila = con.execute("SELECT banco_desmentido_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
    if not fila or not fila["banco_desmentido_json"]:
        return {}
    try:
        return json.loads(fila["banco_desmentido_json"]) or {}
    except ValueError:
        return {}


def desmentir_banco(fixture_id: int, lado: str, fuente: str, nota: str = "") -> dict:
    """Marca que el DT del banco que trae la alineación de la API está mal en
    `lado`. Exige que hoy ESE lado figure como DT equivocado: no se desmiente
    lo que nadie afirmó."""
    lado = _txt(lado).lower()
    fuente = _txt(fuente)
    if lado not in LADOS:
        raise ParteInvalido("lado tiene que ser «a» (local) o «b» (visitante)")
    if len(fuente) < DESMENTIDO_FUENTE_MIN:
        raise ParteInvalido("desmentir el banco lleva FUENTE: el link o la nota de prensa que prueba "
                            "que ese DT no dirigió el partido (p. ej. su salida anunciada antes)")
    with _conectar() as con:
        fila = con.execute("SELECT parte_json, banco_desmentido_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
        if not fila:
            raise KeyError(fixture_id)
        parte = json.loads(fila["parte_json"])
        previos = json.loads(fila["banco_desmentido_json"]) if fila["banco_desmentido_json"] else {}
        malos = {m["lado"]: m for m in dt_equivocado(parte, fixture_id, previos)}
        if lado not in malos and lado not in previos:
            raise ParteInvalido(f"el lado {lado} no figura con DT equivocado: el DT del parte ya casa "
                                "con el banco (o no hay alineación con qué comparar)")
        previos[lado] = {
            "bancoDeLaApi": (malos.get(lado) or previos.get(lado) or {}).get("banco", ""),
            "dtDelParte": (malos.get(lado) or previos.get(lado) or {}).get("parte", "")
                          or (previos.get(lado) or {}).get("dtDelParte", ""),
            "fuente": fuente,
            "nota": _txt(nota),
            "puestoEn": efedb.ahora(),
        }
        con.execute("UPDATE parte_cowork SET banco_desmentido_json=? WHERE fixture_id=?",
                    (json.dumps(previos, ensure_ascii=False), fixture_id))
    return {"fixtureId": fixture_id, "bancoDesmentido": previos,
            "dtEquivocado": dt_equivocado(parte, fixture_id, previos)}


def quitar_desmentido(fixture_id: int, lado: str) -> dict:
    lado = _txt(lado).lower()
    with _conectar() as con:
        fila = con.execute("SELECT banco_desmentido_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
        if not fila:
            raise KeyError(fixture_id)
        previos = json.loads(fila["banco_desmentido_json"]) if fila["banco_desmentido_json"] else {}
        quitado = previos.pop(lado, None)
        con.execute("UPDATE parte_cowork SET banco_desmentido_json=? WHERE fixture_id=?",
                    (json.dumps(previos, ensure_ascii=False) if previos else None, fixture_id))
    return {"fixtureId": fixture_id, "bancoDesmentido": previos, "quitado": quitado}


# ── COLAPSO EN CASCADA, calculada (incidencia 162, decisión del usuario 22/10) ──
# EFE v1.6: D3 ❌ de un lado contra D3 ✅/🔶 del otro. Era la única alerta del
# EFE que dependía de que el agente se acordara de escribirla (United–Leeds:
# D3 ❌ contra 0.5 en las notas y la alerta no salió). D3 viaja en
# `equipos.{lado}.d3`; un parte que no lo trae se lee de la nota del bloque D,
# que es donde lo escribían. La alerta describe el ESCENARIO (perder la
# ventaja), no predice goleada: así la reescribió la v1.6.
_D3_ALIAS = {"✅": "si", "si": "si", "sí": "si", "documentada": "si", "1": "si", "1.0": "si",
             "🔶": "parcial", "parcial": "parcial", "0.5": "parcial", "0,5": "parcial",
             "❌": "no", "no": "no", "impredecible": "no", "0": "no", "0.0": "no",
             "sin dato": "sin dato", "sin_dato": "sin dato", "s/d": "sin dato"}
_D3_EN_NOTA = re.compile(r"D3\s*(?:[:=]|es|en|→)?\s*\(?\s*(✅|🔶|❌|0[.,]5\b|1(?:[.,]0)?\b|0(?:[.,]0)?\b|sin dato)",
                         re.IGNORECASE)


def d3_valor(v) -> str | None:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        v = {1: "1", 0.5: "0.5", 0: "0"}.get(float(v), "")
    return _D3_ALIAS.get(_txt(v).lower().replace("\ufe0f", ""))


def d3_de(equipo: dict) -> tuple[str | None, str]:
    """(valor, fuente): declarado en `d3` o leído de la nota del bloque D."""
    if (equipo or {}).get("d3"):
        return equipo["d3"], "declarado"
    nota = (((equipo or {}).get("bloques") or {}).get("D") or {}).get("nota") or ""
    m = _D3_EN_NOTA.search(nota.replace("\ufe0f", ""))
    return (d3_valor(m.group(1)), "nota del bloque D") if m else (None, "")


def alertas_colapso(parte: dict, nombres: dict) -> list[dict]:
    if any("CASCADA" in _txt(a.get("codigo")).upper() for a in parte.get("alertas") or []):
        return []           # ya la escribió el parte: no se duplica
    eq = parte.get("equipos") or {}
    d3 = {l: d3_de(eq.get(l) or {}) for l in LADOS}
    out = []
    for lado, rival in (("a", "b"), ("b", "a")):
        if d3[lado][0] == "no" and d3[rival][0] in ("si", "parcial"):
            sim = {"si": "✅", "parcial": "🔶"}[d3[rival][0]]
            out.append({
                "codigo": "COLAPSO-EN-CASCADA", "equipo": lado, "tipo": "dato",
                "detalle": (f"{nombres.get(lado, lado)} tiene D3 ❌ ({d3[lado][1]}) y {nombres.get(rival, rival)} "
                            f"D3 {sim} ({d3[rival][1]}): si el rival abre el marcador, tiene que abrir líneas y "
                            "el riesgo es perder una ventaja o no poder recuperarla, no romperse. Describe el "
                            "escenario; NO predice goleada ni orienta hándicap o más/menos goles (EFE v1.6)."),
            })
    return out


# ── UNA LLAVE AL REVÉS (incidencia 774, 29/10/2026) ──────────────────────────
# Palmeiras pasó a la final de la Libertadores por penales y el parte del
# Palmeiras–Bragantino lo dio por eliminado: D3, C4, la sensibilidad y el ensayo
# sobre una «resaca» que no existía. Quién pasó sale de `backend/eliminatoria.py`
# y una frase del parte que lo contradice se grita, al depositar y al leer.
_DICE_ELIMINADO = re.compile(r"elimin|qued[oó] (?:afuera|fuera|out)|se despidi[oó]|perdi[oó] la (?:llave|serie)|"
                             r"cay[oó] en (?:la )?(?:semi|cuartos|octavos|final|repechaje)", re.I)
_DICE_PASA = re.compile(r"clasific[oó]|pas[oó] a (?:la )?(?:final|semi|cuartos|octavos)|finalista|avanz[oó]|"
                        r"sigue (?:vivo|en carrera)", re.I)
_ACTIVA = re.compile(r"elimin(?:[oó]|ando|ar|aron)\s+a\b|dej[oó] (?:afuera|fuera) a\b", re.I)
# «evitó la eliminación», «estuvo a punto de quedar afuera»: no afirma la eliminación
_NIEGA = re.compile(r"evit|casi|a punto|cerca de|roz[oó]|salv[oó]|sin |no (?:fue|qued|cay)|lejos de|pese a", re.I)
_GENERICAS = {"conmebol", "uefa", "league", "copa", "primera", "division", "liga", "championship", "nacional",
              "national", "torneo", "trophy", "super", "cup"}


def _palabras(texto: str, minimo: int = 5) -> set[str]:
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    return {w for w in re.findall(r"[a-z]+", t) if len(w) >= minimo and w not in _GENERICAS}


def _frases(obj, lado: str | None = None):
    """(frase, lado del bloque donde está o None) de todo el texto del parte."""
    if isinstance(obj, str):
        for f in re.split(r"(?<=[.;!?])\s+|\n+", obj):
            if f.strip():
                yield f, lado
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _frases(v, lado)
    elif isinstance(obj, list):
        for v in obj:
            yield from _frases(v, lado)


def alertas_eliminatoria(parte: dict, fx, nombres: dict) -> list[dict]:
    from backend import eliminatoria
    if not fx:
        return []
    frases = list(_frases({k: v for k, v in parte.items() if k not in ("equipos", "alertas")}))
    for lado in LADOS:
        frases += list(_frases(((parte.get("equipos") or {}).get(lado) or {}), lado))
    out = []
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        try:
            llaves = eliminatoria.recientes(tid, str(fx["date"]))
        except Exception:  # noqa: BLE001 — base sin fixtures
            llaves = []
        equipo = _palabras(nombres.get(lado, ""), 4)
        for ll in llaves:
            anclas = _palabras(ll.get("competicion") or "") | ({"penal"} if ll.get("penales") else set())
            dice = _DICE_ELIMINADO if ll["pasa"] else _DICE_PASA
            rival = _palabras(ll.get("rival") or "", 4)
            for frase, donde in frases:
                plano = " ".join(_palabras(frase, 3))
                # «eliminó a Fluminense» es lo que HIZO, no lo que le pasó
                activa = _ACTIVA.sub(" ", frase)
                if not dice.search(activa) or _NIEGA.search(activa):
                    continue
                if not any(a in plano for a in anclas):
                    continue
                # fuera del bloque del equipo: la frase lo nombra a él y NO al de la
                # otra punta de la llave («Palmeiras clasificó eliminando a Fluminense»
                # habla de los dos y no se le carga a ninguno)
                if donde != lado and (not (equipo & _palabras(frase, 4)) or (rival & _palabras(frase, 4))):
                    continue
                out.append({
                    "codigo": "ELIMINATORIA-AL-REVES", "equipo": lado, "tipo": "dato",
                    "detalle": (f"{nombres.get(lado, lado)}: el parte dice «{frase.strip()[:160]}» y la base dice "
                                f"{ll['texto']} en {ll.get('competicion') or 'la copa'} (fixture {ll['fixtureId']}"
                                f"{', marcador a 90 ' + ll['marcador'] if ll.get('marcador') else ''}). Quién pasa "
                                "una llave sale de `eliminatoria` (ficha, timeline, veredicto), nunca del marcador "
                                "a 90' ni de contar los Shootout: corregir lo que se apoyó en eso (D3, C4, "
                                "sensibilidad, ensayo)"),
                })
                break
    return out


def alertas_dt(parte: dict, fx, nombres: dict) -> list[dict]:
    """DT-DISCREPANCIA cuando el parte (la prensa) y la base no dicen el mismo
    DT: manda el parte, y la base queda marcada para refrescarse. DT-SIN-DT
    cuando el bloque A no tiene entrenador: el caso no entra al aprendizaje.
    DT-VS-BANCO cuando el once oficial ya capturado trae en el banco a otro
    (incidencia 711, Comerciantes Unidos 25/10/2026: el once de las 15:33
    traía a Biaggio, oficializado el 21/10, y el parte y la base decían
    Hernández; nada sonó hasta el veredicto)."""
    from backend.ingesta.jugadores import mismo_nombre_dt
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
        if base and base.get("nombre") and not mismo_nombre_dt(nombre, base["nombre"]):
            out.append({"codigo": "DT-DISCREPANCIA", "equipo": lado, "tipo": "dato",
                        "detalle": f"{quien}: el parte dice «{nombre}» y la base tiene «{base['nombre']}» "
                                   f"({base['nota']}). Manda el parte —es lo verificado en prensa—; el registro "
                                   "de la base se refresca en la próxima corrida (DT de la agenda)",
                        "dtBase": base})
        banco = dt_del_banco(fx["id"], tid)
        if banco and _tokens_dt(nombre) and _tokens_dt(banco) and not mismo_dt(nombre, banco):
            declarado = dt.get("banco") if isinstance(dt.get("banco"), dict) else None
            if (declarado and declarado.get("motivo") in MOTIVOS_BANCO and declarado.get("fuente")
                    and (not declarado.get("nombre") or mismo_dt(declarado["nombre"], banco))):
                continue   # el parte ya dijo, con fuente, quién se sienta
            out.append({"codigo": "DT-VS-BANCO", "equipo": lado, "tipo": "dato", "banco": banco,
                        "detalle": f"{quien}: el once oficial de ESTE partido trae en el banco a «{banco}» y el "
                                   f"parte dice «{nombre}». Antes del pitazo: confirmalo en prensa y corregí con "
                                   "POST /analisis/cowork/{id}/dt (o declarás `dt.banco` si el titular no se "
                                   "sienta); después del pitazo el caso queda con el DT con que se escribió"})
    return out


def dt_del_banco(fixture_id, team_id) -> str:
    """El entrenador que trae la alineación capturada de ESE partido, o ""."""
    try:
        fila = saddb.query_one(
            "sad", "SELECT entrenador FROM alineaciones WHERE fixture_id=? AND team_id=? "
                   "AND entrenador IS NOT NULL AND entrenador <> '' LIMIT 1", (fixture_id, team_id))
    except Exception:  # noqa: BLE001 — sin tabla de alineaciones no hay con qué comparar
        return ""
    return (fila["entrenador"] if fila else "") or ""


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
        from backend.analisis import escala
        # sin partidos oficiales en la base: fuera del padrón (801, 798)
        la = _liga_domestica(fx["home_team_id"], fecha) or escala.SIN_BASE
        lb = _liga_domestica(fx["away_team_id"], fecha) or escala.SIN_BASE
        rel = escala.relacion(la, lb)
        if rel in ("misma", "sin dato"):
            return []
        from backend.app import niveles_de
        niv = {}
        for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
            nv = niveles_de(tid, 1, antes=str(fx["date"]))
            niv[lado] = nv[0]["nivel"] if nv else None
        fmt = lambda v: f"{v:.2f}" if v is not None else "sin nivel"  # noqa: E731
        def nom(x):
            if x.get("nombre"):
                return x["nombre"]
            return ("liga fuera del padrón: sin partidos oficiales en la base" if x.get("sinPartidos")
                    else "liga fuera del padrón: solo copas en la base")
        return [{
            "codigo": "ESCALA-LIGAS", "equipo": "global", "tipo": "dato",
            "detalle": (f"{nombres.get('a', 'A')} ({nom(la)}, {la['categoria']}) y {nombres.get('b', 'B')} "
                        f"({nom(lb)}, {lb['categoria']}) vienen de bases distintas ({rel}, mirado desde "
                        f"{nombres.get('a', 'A')}): el nivel SAD se calcula con los puntos y los goles contra "
                        f"los rivales de cada uno y NO compara entre bases (la cima de una segunda sale con "
                        f"más nivel que un equipo del medio de la primera). Leer {fmt(niv['a'])} y "
                        f"{fmt(niv['b'])} como la posición de cada uno dentro de su propia base; el gap §5, la "
                        f"μ del TDE y el RIESGO DEL REVENTÓN (que compara el nivel del rival con los rivales "
                        f"que reventaron las burbujas en su liga) cruzan esos niveles: van con esa reserva. "
                        f"`escala` en GET /equipos/{{id}}/burbujas trae cómo le fue a cada uno contra rivales "
                        f"de otra base"),
            "relacion": rel,
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


# TDE v0.1.21 (21/10/2026): además de las dos del primer gol, la línea del
# EMPATE POSTERIOR (la rama de ventaja caduca si la ventaja se pierde) y la de
# la EXPULSIÓN (disciplina 16 desdoblada). Opcionales: la 44 exige las dos primeras.
# TDE v0.1.23 (25/10/2026): `siIguala` (el que estaba abajo empata; 30 tramos
# del 22-24/10 sin poder declararla) y la roja del RIVAL con su línea
# (`siExpulsion: {"propia": …, "rival": …}` → se guarda como `siExpulsion` y
# `siExpulsionRival`; la forma plana vieja es la propia).
RAMAS_REASIGNACION = ("siMarcaPrimero", "siRecibePrimero", "siLeEmpatan", "siExpulsion", "siIguala",
                      "siExpulsionRival")
RAMAS_OBLIGATORIAS = RAMAS_REASIGNACION[:2]
_CLAVES_RAMA = {"sob1", "sob2", "sob3", "tipologia", "nota", "ventana", "desenlace", "porqueDesenlace"}
# las SOB que una rama puede declarar (TDE v0.1.22: cada rama con su número)
_SOB_RAMA = ("sob1", "sob2", "sob3")
# TDE v0.1.24 (disciplina 65): la rama del que persigue declara CÓMO TERMINA el
# régimen. En la cohorte c3 (253 casos) el que recibió primero con ISE de rama
# ≥ 7 lo dio vuelta 2 de 38 y con < 7, 7 de 33. Es lectura, no número.
RAMAS_DESENLACE = ("siRecibePrimero", "siLeEmpatan", "siIguala")


def rama_empuja(rama: str, r: dict | None) -> bool:
    """¿La rama es un régimen del que persigue? `siRecibePrimero` siempre;
    `siLeEmpatan` y `siIguala` solo «cuando vuelve a empujar / sigue
    empujando» (TDE disciplina 65): la que se cierra con el empate (una
    ECHADA) no tiene desenlace que declarar ni defecto que cobrar (incidencia
    908, U. de Concepción). La usan el recibo y el veredicto."""
    if rama not in RAMAS_DESENLACE:
        return False
    if rama == "siRecibePrimero":
        return True
    return not _txt((r or {}).get("tipologia")).upper().startswith("ECHADA")
DESENLACES = ("se_rompe", "rescata", "abierto")
ISE_RAMA_SE_ROMPE = 7.0   # con ISE de rama ≥ 7 la lectura por defecto es `se_rompe`


DUAL_TDE = 5.0  # disciplina 43 del TDE: IE ≥ 5 Y ISE ≥ 5


def tipologia_vs_indices(b: dict) -> dict | None:
    """TDE PASO 3: el tipo modal sale de cuál índice manda (ISE > IE → SOB;
    IE > ISE → ECHADA). Una tipología declarada del otro lado se avisa."""
    tip = (b.get("tipologia") or "").upper()
    try:
        ie, ise = float(b.get("ie")), float(b.get("ise"))
    except (TypeError, ValueError):
        return None
    if not tip:
        return None
    # CONFIGURACIÓN DUAL (disciplina 43 del TDE, incidencia 598): con IE ≥ 5 e
    # ISE ≥ 5 la vía echada no operó nunca en el registro (0 de 7) y el tramo
    # final se lee por SOB aunque el IE sea mayor (Inter de Bogotá 6,81 / 5).
    if ie >= DUAL_TDE and ise >= DUAL_TDE:
        if not tip.startswith("ECHADA"):
            return None
        manda, porque = "SOB", "la disciplina 43 del TDE (configuración dual, IE e ISE ≥ 5)"
    elif ie == ise:
        return None
    elif tip.startswith("ECHADA") and ise > ie:
        manda, porque = "SOB", "el PASO 3 del TDE"
    elif tip.startswith("SOB") and ie > ise:
        manda, porque = "ECHADA", "el PASO 3 del TDE"
    else:
        return None
    return {"codigo": "TIPOLOGIA-VS-INDICES", "tipo": "dato",
            "detalle": f"tipología modal {b.get('tipologia')} con IE {ie:g} e ISE {ise:g}: por {porque} "
                       f"el tipo modal es {manda}. O se corrige la tipología, o el índice que no cuadra"}


def _reasignacion(x, rechazos: list, donde: str) -> dict:
    """La disciplina 44 del TDE como CAMPO: qué le pasa a las vías de ESTE
    equipo si marca primero y si recibe primero.

    Se escribía en prosa y en la autopsia del 11/10/2026 faltó en unos once
    lados de 48; donde estaba escrita, funcionó (Inter, Guaraní, Racing). En
    prosa no se puede contar si está ni cobrar al cerrar cuál de las dos ramas
    jugó el partido: como campo, el veredicto dice qué rama se dio y si estaba
    declarada (`objetivo.tde.bloques[].reasignacion`)."""
    if x is None or x == {}:
        return {}
    if not isinstance(x, dict):
        rechazos.append({"donde": donde, "porque": f"`reasignacion` tiene que ser un objeto, llegó {type(x).__name__}",
                         "esperado": '{"siMarcaPrimero": {"sob1": 0, "tipologia": "…", "nota": "…"}, '
                                     '"siRecibePrimero": {"sob1": 1, …}}'})
        return {}
    fuera: dict = {}
    exp = x.get("siExpulsion")
    if isinstance(exp, dict) and ({"propia", "rival"} & set(exp)):
        x = {**x, "siExpulsion": exp.get("propia"), "siExpulsionRival": exp.get("rival")}
        x = {k: v for k, v in x.items() if v is not None}
    for clave in x:
        if clave not in RAMAS_REASIGNACION:
            rechazos.append({"donde": f"{donde}.{clave}", "porque": f"rama desconocida {clave!r}: no se guardó",
                             "esperado": " · ".join(RAMAS_REASIGNACION)})
    for rama in RAMAS_REASIGNACION:
        r = x.get(rama)
        if r is None:
            continue
        if isinstance(r, str):          # una línea suelta se acepta como nota
            r = {"nota": r}
        if not isinstance(r, dict):
            rechazos.append({"donde": f"{donde}.{rama}", "porque": f"tiene que ser un objeto, llegó {type(r).__name__}",
                             "esperado": '{"sob1": 0 | 0.5 | 1, "tipologia": "…", "nota": "…"}'})
            continue
        sobs = {}
        for k in _SOB_RAMA:
            v = r.get(k)
            if v is None:
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = None
            if v not in (0.0, 0.5, 1.0):
                rechazos.append({"donde": f"{donde}.{rama}.{k}", "porque": f"llegó {r.get(k)!r}: no se guardó",
                                 "esperado": f"0 · 0.5 · 1 (el valor que tomaría {k.upper()} en esa rama)"})
                continue
            sobs[k] = v
        rama_ok = {"sob1": sobs.get("sob1"), "tipologia": _txt(r.get("tipologia")), "nota": _txt(r.get("nota"))}
        rama_ok.update({k: v for k, v in sobs.items() if k != "sob1"})
        # la ventana de ESTA rama, si cambia: el veredicto mide la que jugó el
        # partido (Junior–Pereira y Roma–Madrid se medían contra la original)
        if _txt(r.get("ventana")):
            rama_ok["ventana"] = _txt(r.get("ventana"))
        # TDE v0.1.24 (disciplina 65): el desenlace del régimen del que persigue
        des = _txt(r.get("desenlace")).lower().replace("-", "_").replace(" ", "_")
        if des:
            if rama not in RAMAS_DESENLACE:
                rechazos.append({"donde": f"{donde}.{rama}.desenlace",
                                 "porque": f"`desenlace` es de las ramas del que persigue o vuelve a empujar "
                                           f"({', '.join(RAMAS_DESENLACE)}), no de {rama}: no se guardó",
                                 "esperado": "el desenlace en siRecibePrimero, siLeEmpatan o siIguala (TDE v0.1.24)"})
            elif des not in DESENLACES:
                rechazos.append({"donde": f"{donde}.{rama}.desenlace",
                                 "porque": f"llegó {r.get('desenlace')!r}: no se guardó",
                                 "esperado": " · ".join(DESENLACES) + " (TDE v0.1.24, disciplina 65)"})
            else:
                rama_ok["desenlace"] = des
                if _txt(r.get("porqueDesenlace")):
                    rama_ok["porqueDesenlace"] = _txt(r.get("porqueDesenlace"))
        if rama_ok["sob1"] is None and not rama_ok["tipologia"] and not rama_ok["nota"] \
                and not rama_ok.get("ventana"):
            continue
        fuera[rama] = rama_ok
    return fuera


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
        # EL SKILL NO PUBLICA COLOR (TDE v0.1.20+: «el IE no lleva semáforo; se
        # publica el valor y la banda ordinal»). Una banda («banda 5-7») no es un
        # error del analista: la banda ordinal la calcula el backend
        # (`calculado.bandaOrdinal`), así que se acepta sin guardar y sin
        # rechazo (incidencia 533: el rechazo era ruido en cada parte)
        if isinstance(crudo, str) and re.search(r"banda|\d\s*[-–]\s*\d", crudo, re.I):
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
        # UN ÍNDICE QUE NO LLEGÓ NO ES UN CERO. `_num(None)` daba 0.0, y con el
        # bloque S sin puntuar (el backend no puede calcular) el parte mostraba
        # «IE 0.0 · ISE 0.0»: el riesgo más bajo de la escala sobre algo que
        # nadie midió (Rennes–Auxerre y San Lorenzo–Riestra, 11/10/2026).
        "ie": None if ie in (None, "") else _num(ie, 1000), "ieNivel": niveles["ieNivel"],
        "ise": None if ise in (None, "") else _num(ise, 1000), "iseNivel": niveles["iseNivel"],
        "equipo": lado or equipo,
        "tipologia": _txt(x.get("tipologia")),
        "ventana": _txt(x.get("ventana")),
        "disciplina43": disciplina,
        "vias": vias,
        "falsador": _txt(x.get("falsador")),
        "reasignacion": ise_de_ramas(_reasignacion(x.get("reasignacion"), rechazos, f"{donde}.reasignacion"), ind),
        # LA PROSA DEL BLOQUE SE GUARDA (incidencia 863: `notas` llegaba, el recibo
        # no la rechazaba y el GET no la devolvía: se perdía callada)
        "notas": _txt(x.get("notas")),
        # LO QUE NO SE PUDO PUNTUAR, CON SU MOTIVO (incidencia 928: el prompt pide
        # excluir con motivo el indicador imposible —F4 pide PPDA— y desde la
        # 863 el bloque rechazaba `sinDato`). Lista o {indicador: motivo}.
        "sinDato": _sin_dato_tde(x.get("sinDato"), x.get("excluidos")),
    } | _claves_tde_ignoradas(x, rechazos, donde)


def _sin_dato_tde(*fuentes) -> dict:
    out = {}
    for f in fuentes:
        if isinstance(f, dict):
            out.update({str(k): _txt(v) for k, v in f.items() if k})
        elif isinstance(f, list):
            out.update({str(k): "" for k in f if isinstance(k, str) and k})
        elif isinstance(f, str) and f.strip():
            out[f.strip()] = ""
    return out


# Lo que el bloque del TDE guarda. Una clave fuera de esta lista NO se tira en
# silencio: vuelve en `rechazos` con su nombre (FALLAS.md §5, la falla callada).
CLAVES_BLOQUE_TDE = {"equipo", "indicadores", "ie", "ieNivel", "ise", "iseNivel", "tipologia", "ventana",
                     "disciplina43", "vias", "falsador", "reasignacion", "notas", "sinDato", "excluidos"}


def _claves_tde_ignoradas(x: dict, rechazos: list, donde: str) -> dict:
    fuera = sorted(k for k in x if k not in CLAVES_BLOQUE_TDE)
    if fuera:
        rechazos.append({"donde": donde,
                         "porque": f"el bloque del TDE no guarda {', '.join(f'`{k}`' for k in fuera)}: "
                                   "no se guardó; la prosa va en `notas`",
                         "esperado": ", ".join(sorted(CLAVES_BLOQUE_TDE))})
    return {}


HEREDA_SOB2 = ("siMarcaPrimero",)   # la rama donde el equipo va adelante, no persigue


def ise_de_ramas(reasig: dict, indicadores: dict) -> dict:
    """TDE v0.1.22 · CADA RAMA CON SU NÚMERO. Sporting 2-3 LASK (21/10/2026):
    la rama «si le empatan» decía «vuelve a empujar y reabre la SOB» y el ISE
    del bloque quedó en 1.67 —el del arranque—: la prosa vio el mecanismo y el
    número no. Con sob1 y sob2 declarados en la rama, la app calcula su ISE con
    la misma fórmula del skill ((SOB1+SOB2+SOB3)/3×10); SOB3 sale de la rama o,
    si no vino, del bloque (y se dice en `iseRamaHeredados`). SOB2 NO se
    hereda: el seguro de atrás del arranque no vale para el que persigue.
    …salvo en `siMarcaPrimero` (incidencia 483, Gil Vicente–Porto): el que va
    adelante no persigue y sigue con el seguro de su arranque; la rama traía
    sob1 sin sob2 y quedaba sin ISE para comparar en el veredicto."""
    for nombre, rama in reasig.items():
        s1, s2 = rama.get("sob1"), rama.get("sob2")
        heredados = []
        if s2 is None and nombre in HEREDA_SOB2 and s1 is not None:
            try:
                s2 = None if (indicadores or {}).get("SOB2") is None else float(indicadores["SOB2"])
            except (TypeError, ValueError):
                s2 = None
            if s2 is not None:
                heredados.append("SOB2")
        if s1 is None or s2 is None:
            continue
        s3 = rama.get("sob3")
        if s3 is None:
            base = (indicadores or {}).get("SOB3")
            try:
                s3 = None if base is None else float(base)
            except (TypeError, ValueError):
                s3 = None
            if s3 is not None:
                heredados.append("SOB3")
        if s3 is None:
            continue
        rama["iseRama"] = round((s1 + s2 + s3) / 3 * 10, 2)
        if heredados:
            rama["iseRamaHeredados"] = heredados
        # TDE v0.1.24 (disciplina 65): la lectura por defecto sale del número
        if rama_empuja(nombre, rama):
            rama["desenlaceDefecto"] = "se_rompe" if rama["iseRama"] >= ISE_RAMA_SE_ROMPE else "abierto"
    return reasig


def avisos_desenlace(bloques: list[dict]) -> list[str]:
    """TDE v0.1.24 (disciplina 65): ramas de sobreexposición sin `desenlace`, o
    con `rescata` contra un ISE de rama ≥ 7 sin el hecho que lo sostiene."""
    out = []
    for b in bloques:
        for rama, r in (b.get("reasignacion") or {}).items():
            if not rama_empuja(rama, r) or (r.get("sob1") or 0) < 0.5:
                continue
            donde = f"{b.get('equipo') or '?'}.{rama}"
            if not r.get("desenlace"):
                out.append(f"{donde} sin `desenlace`")
            elif r["desenlace"] == "rescata" and (r.get("iseRama") or 0) >= ISE_RAMA_SE_ROMPE \
                    and not r.get("porqueDesenlace"):
                out.append(f"{donde} dice «rescata» con ISE de rama {r['iseRama']:g} y sin `porqueDesenlace`")
    return out


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
_ALERTAS_CALCULADAS = {"K-EXTREMO", "K-CERCA-EXTREMO", "K-EXTREMO-CONDICION", "K-CERCA-EXTREMO-CONDICION", "FAMILIA-RECORD", "ESPINA-VS-RIESGO", "HERENCIA-DTP", "ESCALA-LIGAS", "HUECO-DOBLE", "F3", "DT-DISCREPANCIA", "DT-SIN-DT", "DT-VS-BANCO",
                        "COLAPSO-EN-CASCADA", "F1-DECISIVO-FUERA", "DTP-REHACER", "DTP-SIN-REFERENCIA",
                        "TIPOLOGIA-VS-INDICES", "ESPINA-SIGUE-EN-EXTREMO", "EFE-EMPATE-TECNICO",
                        "T.54-SIN-DECLARAR", "ELIMINATORIA-AL-REVES", "SANCION-SIN-DECLARAR",
                        "ONCE-SIN-FILA-F1"}
# LA TERCERA CLASE: las de coherencia las pone Jev AL DEPOSITAR y se guardan
# selladas (coherencia_json), porque no son deterministas y rehacerlas al leer
# las haría parpadear. Del depósito se descartan igual que las calculadas
# —Cowork no puede inyectarlas—, pero al leer NO se recalculan: se leen.
_ALERTAS_CAPTURADAS = {"COHERENCIA-BLOQUE", "COHERENCIA-1X2", "COHERENCIA-MATCHUP", "COHERENCIA-REVENTON"}
# el protocolo usa `ambos` para una alerta que toca a los dos equipos: estaba
# en el esquema del EFE viejo y se perdió al escribir este contrato
_EQUIPOS_ALERTA = ("a", "b", "ambos", "global")


# UN PARTE PARA OTRA FECHA NO ES EL PARTE DE ESTE PARTIDO (incidencia 371:
# Millonarios–Once Caldas, depositado el 13/10 para el 14/10, aplazado por el
# estado de la cancha y jugado el 20/10 —tres titulares nuevos, una burbuja
# distinta— y se juzgó como ciego). `fecha` del parte es la del partido en el
# ÚLTIMO depósito completo (solo el POST la escribe): si el partido se movió
# más de DIAS_PARTE_RANCIO desde entonces, el parte se escribió con otra
# semana de datos. La agenda lo vuelve a poner en `porHacer` y, si nadie lo
# rehízo, el caso va a cuarentena automática por criterio de insumo.
DIAS_PARTE_RANCIO = 1


def dias_movido(fecha_parte: str | None, fecha_fixture: str | None) -> int | None:
    """Días entre la fecha del partido con que se depositó el parte y la fecha
    real; None si no se movió más de DIAS_PARTE_RANCIO (o falta un dato)."""
    try:
        d = (date_t.fromisoformat(str(fecha_fixture)[:10]) - date_t.fromisoformat(str(fecha_parte)[:10])).days
    except (TypeError, ValueError):
        return None
    return d if abs(d) > DIAS_PARTE_RANCIO else None


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
    # `dato` es de las alertas que pone el backend; una declarada por el skill
    # es estructural o de fecha. Se guarda como `fecha`, pero se DICE: el
    # cambio callado se reportó como bug (incidencia 343, DIV-MOTOR-MERCADO
    # enviada «dato» y devuelta «fecha», 21/10/2026)
    if tipo and tipo not in ("estructural", "fecha"):
        rechazos.append({"donde": f"{donde}.tipo", "jugador": _txt(a.get("codigo")),
                         "porque": f"tipo {tipo!r} no es de una alerta declarada: se guardó como «fecha»",
                         "esperado": "estructural / fecha (`dato` lo pone solo el backend)"})
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
    ident = _txt(d.get("id"))
    if not ident:
        # 24/10/2026: los partes del 16/09 llegaron con 4-5 documentos sin id ni
        # título y se guardaron todos como «nota»: en la pantalla eran cinco
        # ensayos sin nombre. Sin id la pantalla no sabe dónde ponerlo; se dice.
        if rechazos is not None:
            rechazos.append({"donde": donde,
                             "porque": "documento sin `id`: la pantalla no sabe en qué pestaña va",
                             "esperado": "id = " + " · ".join(DOCUMENTOS) + " (u otro id propio, con su titulo)"})
        return None
    formato = _txt(d.get("formato")).lower()
    return {"id": ident,
            "titulo": _txt(d.get("titulo")) or DOCUMENTOS.get(ident, ident),
            "formato": formato if formato in ("md", "html", "texto") else "md",
            "cuerpo": cuerpo}


def _documentos(lista, rechazos: list) -> list[dict]:
    """Un documento por id: si llegan dos con el mismo, se queda el ÚLTIMO y
    el recibo lo dice (un ensayo rehecho que se agrega en vez de reemplazar
    no puede dejar dos versiones en la pantalla)."""
    docs = [d for d in (_documento(x, rechazos, f"documentos[{i}]")
                        for i, x in enumerate(_lista(lista, rechazos, "documentos"))) if d]
    ultimo = {d["id"]: i for i, d in enumerate(docs)}
    for i, d in enumerate(docs):
        if ultimo[d["id"]] != i:
            rechazos.append({"donde": f"documentos[{i}]",
                             "porque": f"documento `{d['id']}` repetido: se quedó el último que llegó",
                             "esperado": "un documento por id; para actualizar uno, reemplazalo entero"})
    return [d for i, d in enumerate(docs) if ultimo[d["id"]] == i]


# ── la matriz de escenarios: NARRATIVA, no estadística ─────────────────────
#
# (15/10/2026, decisión del usuario) La matriz se creó para contar CÓMO puede
# darse el partido —cómo gana, empata y pierde cada equipo, con sus palancas—,
# no para dar un número. En la corrida automática se había achatado a una
# tabla de tres filas con porcentajes, y ese porcentaje terminó haciendo de 1X2
# oficial. Ahora el número vive en `pronostico.probabilidades` y la matriz es
# estructurada, por equipo y por escenario, con las filas que pide el skill
# (efe-dashboard, PASO 6, v2.0), incluida su «Probabilidad estimada» por
# escenario (el usuario, 15/10: las analíticas con número se quedan). Esa
# probabilidad es analítica del skill, no el 1X2 oficial: si no cuadra con
# `pronostico.probabilidades` el recibo lo AVISA (`matrizVsPronostico`), no la
# rechaza.
ESCENARIOS_MATRIZ = {
    "ganar": ("tactica", "pelotaParada", "reloj", "base"),
    "empatar": ("tactica", "campo", "dato"),
    "perder": ("gatillo", "errorSistemico", "psicologico", "goleada"),
}
_FILA_ALIAS = {
    "tacticacentral": "tactica", "tactica_central": "tactica", "táctica": "tactica",
    "pelota_parada": "pelotaParada", "pelotaparada": "pelotaParada", "balonparado": "pelotaParada",
    "balon_parado": "pelotaParada", "abp": "pelotaParada",
    "gestionreloj": "reloj", "gestion_reloj": "reloj", "gestiondelreloj": "reloj",
    "basecientifica": "base", "base_cientifica": "base", "evidencia": "base",
    "condicionescampo": "campo", "condiciones": "campo", "condiciones_de_campo": "campo",
    "datoestadistico": "dato", "dato_estadistico": "dato",
    "gatilloprincipal": "gatillo", "gatillo_principal": "gatillo",
    "error": "errorSistemico", "error_sistemico": "errorSistemico", "errorsistemico": "errorSistemico",
    "factorpsicologico": "psicologico", "factor_psicologico": "psicologico", "psicológico": "psicologico",
    "riesgogoleada": "goleada", "riesgo_goleada": "goleada", "riesgodegoleada": "goleada",
}
_ESCENARIO_ALIAS = {"gana": "ganar", "victoria": "ganar", "empata": "empatar", "empate": "empatar",
                    "pierde": "perder", "derrota": "perder"}
_PRIMERA_FILA = {"ganar": "tactica", "empatar": "tactica", "perder": "gatillo"}


def _fila_matriz(k: str, escenario: str) -> str:
    if k in ESCENARIOS_MATRIZ[escenario]:
        return k
    return _FILA_ALIAS.get(k.lower().replace(" ", "").replace("-", "_"), _FILA_ALIAS.get(k.lower(), k))


def _matriz(x, rechazos: list) -> dict:
    """{a: {ganar: {...}, empatar: {...}, perder: {...}}, b: {...}, confirma, contradice}.

    Un escenario puede llegar como texto suelto (entra en su primera fila). Una
    fila desconocida o una probabilidad se rechazan con su motivo: el número va
    en `pronostico.probabilidades`, y una fila que nadie lee se pierde."""
    if not x:
        return {}
    x = _dict(x, rechazos, "matriz",
              '{"a": {"ganar": {"tactica": "…", "pelotaParada": "…", "reloj": "…", "base": "…"}, '
              '"empatar": {…}, "perder": {…}}, "b": {…}, "confirma": "…", "contradice": "…"}')
    out: dict = {}
    for lado in LADOS:
        v = x.get(lado)
        if v is None:
            continue
        if not isinstance(v, dict):
            rechazos.append({"donde": f"matriz.{lado}", "porque": "va un objeto por escenario",
                             "esperado": '{"ganar": {…}, "empatar": {…}, "perder": {…}}'})
            continue
        lado_out = {}
        for esc_in, filas in v.items():
            esc = _ESCENARIO_ALIAS.get(_txt(esc_in).lower(), _txt(esc_in).lower())
            if esc not in ESCENARIOS_MATRIZ:
                rechazos.append({"donde": f"matriz.{lado}.{esc_in}", "porque": "no es un escenario de la matriz",
                                 "esperado": "ganar · empatar · perder"})
                continue
            if isinstance(filas, str):
                filas = {_PRIMERA_FILA[esc]: filas}
            if not isinstance(filas, dict):
                rechazos.append({"donde": f"matriz.{lado}.{esc}", "porque": "va un objeto con sus filas",
                                 "esperado": ", ".join(ESCENARIOS_MATRIZ[esc])})
                continue
            fo = {}
            for k_in, t in filas.items():
                if _txt(k_in).lower().startswith("prob"):
                    pr = _prob_matriz(t)
                    if pr is None:
                        rechazos.append({"donde": f"matriz.{lado}.{esc}.{k_in}",
                                         "porque": f"«{t}» no es una probabilidad",
                                         "esperado": "un número de 0 a 100 (32, «32 %» o 0.32)"})
                    else:
                        fo["probabilidad"] = pr
                    continue
                k = _fila_matriz(_txt(k_in), esc)
                if k not in ESCENARIOS_MATRIZ[esc]:
                    rechazos.append({"donde": f"matriz.{lado}.{esc}.{k_in}",
                                     "porque": f"«{k_in}» no es una fila de «{esc}»",
                                     "esperado": ", ".join(ESCENARIOS_MATRIZ[esc])})
                    continue
                if _txt(t):
                    fo[k] = _txt(t)
            if fo:
                lado_out[esc] = fo
        if lado_out:
            out[lado] = lado_out
    for k in ("confirma", "contradice"):
        if _txt(x.get(k)):
            out[k] = _txt(x.get(k))
    return out


def _prob_matriz(v) -> float | None:
    """32 · «32 %» · 0.32 → 32.0; lo que no es número, None."""
    if isinstance(v, str):
        v = v.replace("%", "").replace(",", ".").strip()
    try:
        n = float(v)
    except (TypeError, ValueError):
        return None
    if 0 < n <= 1:
        n *= 100
    return round(n, 1) if 0 <= n <= 100 else None


_PALABRAS_ESPINA = ("espina", "burbuja", "reventón", "reventon")


def ensayo_cuenta_espina(parte: dict) -> bool:
    """True si no hay nada que contar (sin espina o sin ensayo) o si el ensayo
    nombra la espina o las burbujas. Es un chequeo de presencia, no de
    contenido: dice que el ensayo habla del tema, no que lo diga bien."""
    espina = (parte.get("lecturaSad") or {}).get("espina") or {}
    ensayo = next((d for d in parte.get("documentos") or [] if d.get("id") == "ensayo"), None)
    if not espina or not ensayo:
        return True
    texto = (ensayo.get("cuerpo") or "").lower()
    return any(p in texto for p in _PALABRAS_ESPINA)


def filas_matriz(m: dict) -> int:
    """Cuántas filas declaradas trae la matriz (para el recibo y `perdido`)."""
    return sum(sum(1 for k in f if k != "probabilidad")
               for l in LADOS for f in ((m or {}).get(l) or {}).values())


# a qué resultado del 1X2 corresponde cada escenario de cada lado
_ESCENARIO_A_1X2 = {("a", "ganar"): "local", ("a", "empatar"): "empate", ("a", "perder"): "visita",
                    ("b", "ganar"): "visita", ("b", "empatar"): "empate", ("b", "perder"): "local"}
MATRIZ_TOLERANCIA = 5.0


# EL 1X2 SUBIDO SOBRE EL MOTOR CUANDO EL MOTOR AVISA QUE COMPARA MAL.
# Sporting 2-3 LASK (21/10/2026): con ESCALA-LIGAS activa (μ entre Portugal y
# Austria, fiabilidad baja) el pronóstico puso 66 % al local, nueve puntos SOBRE
# el 1X2 del motor (57 %), y perdió. La lección: con la escala, el rango se abre
# hacia el motor, no se sube sobre él (sad-analysis v4.0, paso 5). Esto lo dice
# al depositar: aviso, no rechazo —quien escribe corrige o justifica en notas—.
PRONOSTICO_SOBRE_MOTOR_PTS = 8


_NOMBRA_MOTOR = re.compile(r"\bmotor\b", re.I)


def pronostico_vs_motor(pron: dict, pred: dict | None, notas: str = "") -> dict | None:
    """El 1X2 declarado contra `unXDos` de /predicciones. Con `fiabilidadMu`
    baja y el resultado favorito del pronóstico más de PRONOSTICO_SOBRE_MOTOR_PTS
    por encima del motor, `aviso` explica qué hacer; si no, solo informa."""
    probs = (pron or {}).get("probabilidades") or {}
    ux = (pred or {}).get("unXDos") or {}
    claves = ("local", "empate", "visita")
    if not ux or not all(isinstance(probs.get(k), (int, float)) for k in claves):
        return None
    top = max(claves, key=lambda k: probs[k])
    delta = round(float(probs[top]) - float(ux[top]), 1)
    fia = ((pred or {}).get("fiabilidadMu") or {}).get("nivel") or ""
    out = {"declarado": {k: probs[k] for k in claves}, "motor": {k: ux[k] for k in claves},
           "favorito": top, "sobreElMotor": delta, "fiabilidadMu": fia, "aviso": ""}
    # la razón escrita en `notas` (lo que el aviso pide) lo apaga (incidencia 752:
    # Venezia y Monza recién ascendidos, el dato que el motor no ve ya escrito y
    # el aviso volvía en cada depósito)
    if fia == "baja" and delta > PRONOSTICO_SOBRE_MOTOR_PTS and _NOMBRA_MOTOR.search(notas or ""):
        out["razonEscrita"] = True
    elif fia == "baja" and delta > PRONOSTICO_SOBRE_MOTOR_PTS:
        out["aviso"] = (f"el pronóstico pone «{top}» {delta:+.1f} puntos SOBRE el motor ({ux[top]} %) con la μ en "
                        "fiabilidad baja (ESCALA-LIGAS): con la escala el rango se abre hacia el motor, no se sube "
                        "sobre él (Sporting–LASK). Acercá el 1X2 al motor o decí en `notas` qué dato que el motor "
                        "no ve lo sostiene")
    return out


# LA VENTAJA SOBRE EL MERCADO (26/10/2026, pedido del usuario tras el PSG–Lyon:
# el parte dio 70 % al PSG, el mercado 71 %). Nuestro número igual al del
# mercado es el mejor pronóstico que tenemos, no una apuesta con valor: la
# cuota trae el margen de la casa. Se calcula al leer contra la última captura
# prepartido: `puntos` = nuestra − mercado sin margen; `valor` = lo que se
# espera ganar por unidad a la cuota media de las casas (con su margen).
VENTAJA_PTS = 3.0     # menos de esto contra el mercado es «sin ventaja»
VALOR_MIN = 0.03      # valor esperado desde el que una selección «tiene valor»


VALOR_N_MIN = 50      # selecciones con valor cerradas antes de confiar en el historial
_RECORTE_DECLARADO = re.compile(r"puntos al favorito", re.I)


def ventaja_mercado(pron: dict, mercado: dict | None, historial: dict | None = None,
                    texto_parte: str = "") -> dict | None:
    """La ventaja del 1X2 declarado sobre el mercado.

    26/10/2026 (usuario, Santa Clara–Benfica): un «valor» de 14 % contra 10 % a
    cuota 9 salía verde, y nacía de haberle quitado 5 puntos al favorito contra
    la regla 6-B. Sin historial que muestre que nuestras desviaciones ganan, un
    valor es `valor en el papel`; pasa a `con valor` solo con el historial
    confirmado (`historial_valor`: n ≥ VALOR_N_MIN y el intervalo de la
    ganancia por encima de cero). `naceDeRecorte`: el mercado da al favorito
    50 %+, lo elegimos igual, lo dejamos VENTAJA_PTS o más por debajo sin
    «−N puntos al favorito por <dato>» escrito, y el valor aparece en otro
    resultado."""
    probs = (pron or {}).get("probabilidades") or {}
    claves = ("local", "empate", "visita")
    if not mercado or not all(isinstance(probs.get(k), (int, float)) for k in claves):
        return None
    tot = sum(float(probs[k]) for k in claves)
    if tot <= 0:
        return None
    nuestra = {k: 100 * float(probs[k]) / tot for k in claves}
    sel = {}
    for k in claves:
        m, c = mercado["prob"][k], mercado["cuota"][k]
        sel[k] = {"nuestra": round(nuestra[k], 1), "mercado": round(m, 1), "puntos": round(nuestra[k] - m, 1),
                  "cuota": round(c, 2), "cuotaJusta": round(100 / nuestra[k], 2) if nuestra[k] > 0 else None,
                  "valor": round(nuestra[k] / 100 * c - 1, 3)}
    pick = max(claves, key=lambda k: nuestra[k])
    # una diferencia chica en un resultado de cuota alta da valor en el papel (13 % contra 12 % a cuota 8):
    # el valor cuenta solo con un desacuerdo real con el mercado, de VENTAJA_PTS o más
    con_valor = [k for k in claves if sel[k]["valor"] >= VALOR_MIN and sel[k]["puntos"] >= VENTAJA_PTS]
    mejor = max(con_valor, key=lambda k: sel[k]["valor"]) if con_valor else None
    fav_mercado = max(claves, key=lambda k: sel[k]["mercado"])
    recorte = bool(mejor and mejor != pick and pick == fav_mercado and sel[pick]["mercado"] >= 50
                   and sel[pick]["puntos"] <= -VENTAJA_PTS and not _RECORTE_DECLARADO.search(texto_parte or ""))
    confirmado = bool(historial and historial.get("confirmado"))
    pp = sel[pick]["puntos"]
    if mejor:
        estado = "con valor" if confirmado else "valor en el papel"
        texto = (f"{'valor' if confirmado else 'valor en el papel'} en {mejor}: {sel[mejor]['nuestra']:.0f} % nuestro "
                 f"contra {sel[mejor]['mercado']:.0f} % del mercado; a cuota {sel[mejor]['cuota']:.2f} saldría "
                 f"{sel[mejor]['valor'] * 100:+.1f} % por unidad SI nuestro número es el bueno")
        if recorte:
            texto += (f". Nace de recortar al favorito ({pick} {pp:+.1f} pts bajo el mercado) sin un dato escrito: "
                      "la regla 6-B del sad v4.1 lo prohíbe porque es un sesgo medido nuestro")
        if not confirmado:
            texto += ". Sin historial que muestre que estas desviaciones ganan"
    elif abs(pp) < VENTAJA_PTS:
        estado = "sin ventaja"
        texto = (f"sin ventaja sobre el mercado: {pick} {sel[pick]['nuestra']:.0f} % contra {sel[pick]['mercado']:.0f} % "
                 f"({pp:+.1f} pts); a cuota {sel[pick]['cuota']:.2f}, con el margen de la casa, se espera "
                 f"{sel[pick]['valor'] * 100:+.1f} % por unidad")
    else:
        estado = "sobre el mercado" if pp > 0 else "bajo el mercado"
        texto = (f"{pick} {pp:+.1f} pts {'sobre' if pp > 0 else 'bajo'} el mercado ({sel[pick]['nuestra']:.0f} % contra "
                 f"{sel[pick]['mercado']:.0f} %), y aun así sin valor a cuota {sel[pick]['cuota']:.2f} "
                 f"({sel[pick]['valor'] * 100:+.1f} % por unidad)")
    return {"estado": estado, "pick": pick, "puntosPick": pp, "mejorValor": mejor, "naceDeRecorte": recorte,
            "texto": texto, "seleccion": sel, "casas": mercado.get("casas"),
            "historial": ({k: historial.get(k) for k in ("n", "ganadas", "roi", "intervalo", "confirmado")}
                          if historial else None),
            "nota": "medido contra la última captura prepartido; no es una recomendación de apuesta: "
                    "valor = probabilidad nuestra × cuota media − 1 (la cuota trae el margen de la casa)"}


# EL HISTORIAL DEL VALOR: ¿las selecciones marcadas con valor ganaron plata a
# su cuota? Sobre los partes con veredicto que ACREDITAN (ciega + PRE) y sin
# cuarentena, la misma población que Aprendizaje. Se cachea en el proceso: lo
# pide cada GET de un parte y cambia solo cuando se cierra un veredicto.
HISTORIAL_TTL_S = int(os.environ.get("SAD_CACHE_VALOR_S", "1800"))
_HIST_CACHE: dict = {}


def _ganancia(filas: list[float]) -> dict:
    n = len(filas)
    if not n:
        return {"n": 0, "ganadas": 0, "roi": None, "intervalo": None}
    media = sum(filas) / n
    var = sum((x - media) ** 2 for x in filas) / (n - 1) if n > 1 else 0.0
    ee = (var / n) ** 0.5
    return {"n": n, "ganadas": sum(1 for x in filas if x > 0), "roi": round(media, 3),
            "intervalo": [round(media - 1.96 * ee, 3), round(media + 1.96 * ee, 3)] if n > 1 else None}


def historial_valor(cache: bool = True) -> dict:
    ahora_s = datetime.now(timezone.utc).timestamp()
    if cache and HISTORIAL_TTL_S > 0 and _HIST_CACHE.get("t", 0) + HISTORIAL_TTL_S > ahora_s:
        return _HIST_CACHE["v"]
    from backend.analisis import veredicto as _vered
    from backend.analisis.lecciones import cuotas_mercado
    with _conectar() as con:
        filas = con.execute("SELECT fixture_id, parte_json, veredicto_json FROM parte_cowork "
                            "WHERE veredicto_json IS NOT NULL AND cuarentena_json IS NULL").fetchall()
    casos = []
    for f in filas:
        try:
            v = json.loads(f["veredicto_json"])
            if not _vered.acredita(v.get("seleccion", ""), v.get("modoEvaluacion", "")):
                continue
            casos.append((f["fixture_id"], json.loads(f["parte_json"]), f["parte_json"]))
        except (ValueError, TypeError):
            continue
    # las copas nacionales no entran a las tablas (29/10/2026, usuario)
    from backend.analisis.escala import copas_nacionales
    copas = copas_nacionales([c[0] for c in casos])
    casos = [c for c in casos if c[0] not in copas]
    ids = [c[0] for c in casos]
    reales = _vered.resultados(ids)
    mercados = cuotas_mercado(ids)
    valor, recorte, sin_recorte, favorito = [], [], [], []
    for fid, parte, crudo in casos:
        real = reales.get(fid)
        vm = ventaja_mercado(parte.get("pronostico") or {}, mercados.get(fid), None, crudo)
        if not real or not vm:
            continue
        pk = vm["pick"]
        favorito.append(vm["seleccion"][pk]["cuota"] - 1 if real == pk else -1.0)
        if vm["mejorValor"]:
            s = vm["mejorValor"]
            g = vm["seleccion"][s]["cuota"] - 1 if real == s else -1.0
            valor.append(g)
            (recorte if vm["naceDeRecorte"] else sin_recorte).append(g)
    h = _ganancia(valor)
    h["confirmado"] = bool(h["n"] >= VALOR_N_MIN and h["intervalo"] and h["intervalo"][0] > 0)
    h["naceDeRecorte"] = _ganancia(recorte)
    h["sinRecorte"] = _ganancia(sin_recorte)
    h["nuestroFavorito"] = _ganancia(favorito)
    h["minimo"] = VALOR_N_MIN
    h["nota"] = ("apostar 1 unidad a cada selección marcada con valor, a la cuota media de la última captura "
                 "prepartido, en los partes cerrados que acreditan (ciega + PRE, sin cuarentena ni copas nacionales): roi = ganancia "
                 "media por unidad, intervalo al 95 %. `con valor` vuelve a la pantalla recién con n ≥ "
                 f"{VALOR_N_MIN} y el intervalo por encima de cero. `nuestroFavorito` = apostar siempre a nuestro "
                 "elegido, como referencia")
    _HIST_CACHE.update(t=ahora_s, v=h)
    return h


def _ventaja_o_nada(fixture_id: int, pron: dict, texto_parte: str = "") -> dict | None:
    try:
        from backend.analisis.lecciones import cuotas_mercado
        m = cuotas_mercado([fixture_id]).get(fixture_id)
        if not m:
            return None
        try:
            hist = historial_valor()
        except Exception:  # noqa: BLE001 — sin historial la marca dice «en el papel»
            hist = None
        return ventaja_mercado(pron, m, hist, texto_parte)
    except Exception:  # noqa: BLE001 — sin cuotas no hay marca, nunca un error
        return None


def _prediccion_o_nada(fixture_id: int) -> dict | None:
    try:
        from backend.app import prediccion
        return prediccion(fixture_id)
    except Exception:  # noqa: BLE001 — sin motor no hay aviso, el depósito sigue
        return None


def matriz_vs_pronostico(m: dict, pron: dict) -> list[dict]:
    """Las probabilidades de la matriz que no cuadran con el 1X2 del pronóstico
    (más de 5 puntos). Es un aviso: las dos son analítica del mismo parte y una
    diferencia puede ser a propósito, pero tiene que verse."""
    probs = (pron or {}).get("probabilidades") or {}
    if not sum(probs.values()):
        return []
    fuera = []
    for (lado, esc), res in _ESCENARIO_A_1X2.items():
        pm = (((m or {}).get(lado) or {}).get(esc) or {}).get("probabilidad")
        if pm is None:
            continue
        pp = float(probs.get(res) or 0)
        if abs(pm - pp) > MATRIZ_TOLERANCIA:
            fuera.append({"donde": f"matriz.{lado}.{esc}.probabilidad", "matriz": pm,
                          "pronostico": pp, "resultado": res,
                          "nota": f"la matriz dice {pm:g} % y el 1X2 del pronóstico {pp:g} %: "
                                  "si es a propósito, decí por qué en las notas"})
    return fuera


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
        "matriz": _matriz(payload.get("matriz"), rechazos),
        "lecturaSad": _lectura_sad(payload.get("lecturaSad") or payload.get("lectura_sad") or {},
                                   rechazos),
        "tde": _tde(payload.get("tde"), rechazos),
        # el DTP estructurado, uno por equipo foco (backend/analisis/dtp_cowork.py)
        "dtp": _dtp.normalizar_dtp(payload.get("dtp"), rechazos),
        "timelineEventos": [e for e in (_evento_tl(x, rechazos, f"timelineEventos[{i}]")
                                        for i, x in enumerate(_lista(payload.get("timelineEventos"),
                                                                     rechazos, "timelineEventos"))) if e],
        "timelineNarrativa": _txt(payload.get("timelineNarrativa")),
        "cadena": {l: _pron_cadena(cadena_in.get(l)) for l in LADOS},
        "documentos": _documentos(payload.get("documentos"), rechazos),
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
    # qué DT tenía la base al depositar: es lo que separa un parte que copió un
    # DT rancio de uno que lo contradijo con la prensa (dt_equivocado)
    dt_base = {}
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        try:
            b = dt_de_base(tid)
        except Exception:  # noqa: BLE001 — sin capa de jugadores no hay base que guardar
            b = None
        if b and b.get("nombre"):
            dt_base[lado] = b["nombre"]
    with _conectar() as con:
        previo = con.execute("SELECT creado_en, xi_json, parte_json FROM parte_cowork WHERE fixture_id=?",
                             (parte["fixtureId"],)).fetchone()
        con.execute(
            "INSERT INTO parte_cowork (fixture_id, fecha, equipo_a, equipo_b, estado, version, "
            "parte_json, xi_json, creado_en, actualizado_en, cohorte, dt_base_json, deposito_previo_en) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(fixture_id) DO UPDATE SET fecha=excluded.fecha, equipo_a=excluded.equipo_a, "
            "equipo_b=excluded.equipo_b, version=excluded.version, parte_json=excluded.parte_json, "
            "actualizado_en=excluded.actualizado_en, "
            # la cohorte es de la PRIMERA vez: un re-depósito no cambia de época, y un
            # parte que ya existía sin marca es de antes de la primera cohorte (rodaje)
            f"cohorte=COALESCE(parte_cowork.cohorte, '{COHORTE_RODAJE}'), "
            # la base de la PRIMERA vez, igual que la cohorte
            "dt_base_json=COALESCE(parte_cowork.dt_base_json, excluded.dt_base_json), "
            # un re-depósito DESPUÉS del pitazo no cuenta como rehacer
            "deposito_previo_en=COALESCE(excluded.deposito_previo_en, parte_cowork.deposito_previo_en)",
            (parte["fixtureId"], (fx["date"] or "")[:10], fx["home_name"], fx["away_name"],
             "pendiente_xi", parte["version"], json.dumps(parte, ensure_ascii=False),
             previo["xi_json"] if previo else None,
             previo["creado_en"] if previo else ahora, ahora, COHORTE,
             json.dumps(dt_base, ensure_ascii=False) if dt_base else None,
             ahora if _antes_del_pitazo(ahora, fx["date"]) else None),
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
                "bloquesDtp": len((p_.get("dtp") or {}).get("bloques") or []),
                # las vías (ECHADA / SOBREEXPOSICIÓN) se perdían en silencio en
                # un re-depósito que mandaba el TDE sin ellas (Cowork, 23/09)
                "viasTde": sum(len(b.get("vias") or []) for b in bloques_tde(p_.get("tde") or {})),
                "reasignacionesTde": sum(len(b.get("reasignacion") or {}) for b in bloques_tde(p_.get("tde") or {})),
                # `cadena[lado]` es el texto del pronóstico, pero también se
                # acepta `{"pronostico": "…"}`: las dos formas se cuentan igual
                "pronosticosDeCadena": sum(1 for l in LADOS if _pron_cadena((p_.get("cadena") or {}).get(l))),
                "repartoUnXDos": 1 if sum((pron.get("probabilidades") or {}).values()) else 0,
                "falsador": 1 if _txt(pron.get("falsador")) else 0,
                "lecturaSad": 1 if (p_.get("lecturaSad") or {}).get("moduloOperativo") else 0,
                "sensibilidad": sum(len((p_.get("equipos", {}).get(l) or {}).get("sensibilidad") or []) for l in LADOS),
                "filasMatriz": filas_matriz(p_.get("matriz") or {}),
            }
        t_antes, t_ahora = _tam(antes), _tam(parte)
        perdido = [f"{k}: {t_antes[k]} → {t_ahora[k]}" for k in t_antes if t_ahora[k] < t_antes[k]]

    cadena, cadena_ignorada = _guardar_cadena(fx, parte.get("cadena") or {})
    dtp_guardado, dtp_no_guardado = _guardar_apertura_dtp(fx, parte.get("dtp") or {})
    # LO QUE FALTA AHORA Y SE COBRA DENTRO DE 12 HORAS. Un bloque vacío no es
    # un error al depositar —se puede completar después, y a veces no hay dato—,
    # pero algunos se pagan al cerrar el caso, cuando ya NO se pueden llenar sin
    # hindsight. Decirlo acá, con el partido todavía por jugarse, es la única
    # ventana en la que arreglarlo es legítimo. Callarlo es descubrirlo medio
    # día tarde, que fue exactamente lo que pasó con `cadena` y con `tde`.
    faltan = []
    # DTP v1.5: los dos carriles de banda, con su vuelta (aviso, sin rechazo)
    faltan.extend(_dtp.avisos_carril(parte.get("dtp") or {}, {"a": fx["home_name"], "b": fx["away_name"]}))
    # DTP v1.6: el sistema contra el último once, el ejecutor de penales y la sede del caso de la 6
    try:
        faltan.extend(_dtp.avisos_v16(parte.get("dtp") or {}, fx, {"a": fx["home_name"], "b": fx["away_name"]}))
    except Exception:  # noqa: BLE001 — un aviso nunca tumba el depósito
        pass
    # una llave al revés (774): se corrige ANTES del partido, no en el veredicto
    try:
        for a in alertas_eliminatoria(parte, fx, {"a": fx["home_name"], "b": fx["away_name"]}):
            faltan.append({"bloque": f"equipos.{a['equipo']}", "codigo": a["codigo"], "costara": a["detalle"],
                           "comoSeArregla": "reescribir con la llave como la dice la base (GET /fixtures/{id}/ficha "
                                            "→ `eliminatoria`, o el título del evento en el timeline)"})
    except Exception:  # noqa: BLE001 — un aviso nunca tumba el depósito
        pass
    # un sancionado de la base que el parte tiene disponible: se corrige antes del partido
    try:
        for a in _f1_base.alertas_sancion(parte, fx, {"a": fx["home_name"], "b": fx["away_name"]}):
            faltan.append({"bloque": f"equipos.{a['equipo']}.fuera", "codigo": a["codigo"], "costara": a["detalle"],
                           "comoSeArregla": "declararlo en `fuera` con estado baja y motivo «sanción» (con zona y "
                                            "rol), o decir en la nota del equipo por qué juega, con la fuente"})
    except Exception:  # noqa: BLE001 — un aviso nunca tumba el depósito
        pass
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
    # LA REASIGNACIÓN POR PRIMER GOL (disciplina 44) es obligatoria en PRE y
    # se cobra al cerrar: el veredicto dice qué rama jugó el partido
    sin_reasig = [b.get("equipo") or "?" for b in tde_bloques
                  if not all(r in (b.get("reasignacion") or {}) for r in RAMAS_OBLIGATORIAS)]
    if tde_bloques and sin_reasig:
        faltan.append({
            "bloque": "tde.reasignacion",
            "costara": f"lado(s) {', '.join(sin_reasig)} sin las dos ramas: al cerrar, el veredicto "
                       "va a decir qué equipo marcó primero y no habrá nada declarado contra qué comprobarlo",
            "comoSeArregla": 'en cada bloque: "reasignacion": {"siMarcaPrimero": {"sob1": …, "tipologia": "…"}, '
                             '"siRecibePrimero": {…}} (disciplina 44)',
        })
    # TDE v0.1.23 (cambio 2): la línea del empate y la de la expulsión en SU
    # campo —65 notas de siMarcaPrimero hablaban del empate en prosa y no cuentan—
    sin_lineas = [f"{b.get('equipo') or '?'}: {', '.join(r for r in ('siLeEmpatan', 'siExpulsion') if r not in (b.get('reasignacion') or {}))}"
                  for b in tde_bloques if b.get("reasignacion")
                  and not all(r in b["reasignacion"] for r in ("siLeEmpatan", "siExpulsion"))]
    if sin_lineas:
        faltan.append({
            "bloque": "tde.reasignacion",
            "costara": f"sin la línea del empate o de la expulsión en su campo ({'; '.join(sin_lineas)}): "
                       "si el partido pasa por ahí, el tramo sale «no declarado» aunque la nota lo diga",
            "comoSeArregla": '"siLeEmpatan": {…} y "siExpulsion": {"propia": {…}, "rival": {…}} en cada bloque; '
                             '"siIguala" si el equipo puede ir abajo y empatar (TDE v0.1.23)',
        })
    # UNA RAMA QUE CAMBIA AL RÉGIMEN SOB SIN SU SEGURO DE ATRÁS (TDE v0.1.22):
    # el SOB2 del arranque no se hereda al que persigue (Sporting–LASK)
    sin_sob2 = [f"{b.get('equipo') or '?'}.{rama}" for b in tde_bloques
                for rama, r in (b.get("reasignacion") or {}).items()
                if rama in ("siRecibePrimero", "siLeEmpatan") and (r.get("sob1") or 0) >= 0.5 and r.get("sob2") is None]
    if sin_sob2:
        faltan.append({
            "bloque": "tde.reasignacion.sob2",
            "costara": f"rama(s) {', '.join(sin_sob2)} pasan a sobreexposición sin su SOB2: el ISE de la rama no "
                       "se calcula y queda el del arranque, como en Sporting–LASK (ISE 1.67 con la rama que decía «se expone»)",
            "comoSeArregla": 'en la rama: "sob2": 0 | 0.5 | 1 —el seguro de atrás CUANDO persigue, no el del arranque; '
                             'sin evidencia, 0.5— y, si cambia, "sob3" (TDE v0.1.22)',
        })
    # EL DESENLACE DEL QUE PERSIGUE (TDE v0.1.24, disciplina 65): con ISE de
    # rama ≥ 7 la cohorte c3 remontó 2 de 38; la lectura se declara y se mide
    sin_des = avisos_desenlace(tde_bloques)
    if sin_des:
        faltan.append({
            "bloque": "tde.reasignacion.desenlace",
            "costara": f"{'; '.join(sin_des)}: el veredicto no va a poder decir si el régimen del que "
                       "persigue terminó como se leyó",
            "comoSeArregla": '"desenlace": "se_rompe" | "rescata" | "abierto" en la rama —con ISE de rama ≥ 7 '
                             'el defecto es «se_rompe»; «rescata» ahí pide "porqueDesenlace" con el hecho '
                             '(rival que no administra, banco ofensivo documentado, roja rival)— (TDE v0.1.24)',
        })
    # UN IE QUE NO SE PUEDE CALCULAR SE DICE AL DEPOSITAR. Athletico-PR y
    # Gimnasia de Mendoza (17/10/2026) llegaron sin un solo indicador S: el IE
    # quedaba en null y el recibo callaba; los analistas lo vieron al releer.
    # ...con lo que HEREDA del DTP, como al leer: el C1 de la clase del bloque
    # cuenta para el bloque C (Tucumán, incidencia 434: c1Tde 0.5 y el recibo
    # decía «sin ningún indicador en el bloque C»; hubo que escribirlo a mano)
    from backend.analisis import tde as _tdemod
    _her = _dtp.herencia_tde(parte.get("dtp") or {})
    for b in tde_bloques:
        ind = (_heredar(b, _her.get(b.get("equipo") or "")).get("indicadores") or {}) if b.get("indicadores") else {}
        if not ind:
            continue
        calc = _tdemod.indice(dict(ind))
        # LO DECLARADO SIN DATO NO SE COBRA (incidencia 808, Lebrijana: la regla
        # es no rellenar, y el recibo pedía «puntuá al menos un indicador» de C
        # y S aunque el bloque los traía en `sinDato` con su motivo)
        sin_dato = {str(k)[:1].upper() for k in (b.get("sinDato") or {})}
        presentes = {str(k)[:1].upper() for k in ind if not str(k).upper().startswith("SOB")}
        if calc.get("sinDato") and ({"F", "C", "P"} - presentes) <= sin_dato:
            continue
        if calc.get("sinS") and "S" in sin_dato:
            continue
        if calc.get("sinDato"):
            faltan.append({
                "bloque": f"tde.ie (lado {b.get('equipo') or '?'})",
                "costara": f"el IE no se calcula —{calc.get('porque', 'faltan indicadores')}— y queda en null: "
                           "la ventana se comprueba igual, pero el índice no entra a ninguna métrica",
                "comoSeArregla": "puntuá al menos un indicador de cada bloque (F, C y P; 0 · 0.5 · 1) "
                                 "y re-depositá; sin dato de verdad, decilo en `notas`",
            })
        elif calc.get("sinS"):
            faltan.append({
                "bloque": f"tde.ie (lado {b.get('equipo') or '?'})",
                "costara": "sin ningún indicador S el IE sale PARCIAL (sobre F, C y P, marcado `sinS`): "
                           "se compara con reserva con uno completo",
                "comoSeArregla": "si hay dato, puntuá S1 (faltas y jugadores al límite) o S2 (cambios "
                                 "defensivos del DT); S3 pide PPDA y puede quedar fuera",
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
    elif empate_en_la_cima(pron.get("probabilidades") or {}):
        # 859 (Remo–Botafogo 35/30/35): sin elegido el veredicto no cuenta acierto,
        # y vsMercado y la simulación eligen uno por el orden de las claves
        faltan.append({
            "bloque": "pronostico.probabilidades",
            "costara": f"el 1X2 tiene a {' y '.join(empate_en_la_cima(pron.get('probabilidades') or {}))} "
                       "empatados arriba: no hay elegido, el veredicto no cuenta acierto y lo que elige "
                       "por el máximo toma el primero en el orden de las claves",
            "comoSeArregla": "decidí: un punto más al que elegís (y uno menos a otro) para que haya un "
                             "resultado elegido",
        })
    elif not _txt(pron.get("falsador")):
        faltan.append({
            "bloque": "pronostico.falsador",
            "costara": "sin falsador no hay nada que refutar: `falsadorCumplido` "
                       "queda en null y el caso pierde su prueba más dura",
            "comoSeArregla": "una condición OBSERVABLE que, si ocurre, declara fallado "
                             "el pronóstico",
        })
    # la matriz por equipo: un lado sin escenarios es una narrativa a medias
    m_ = parte.get("matriz") or {}
    lados_sin = [l for l in LADOS if not m_.get(l)]
    if lados_sin:
        faltan.append({
            "bloque": "matriz",
            "costara": ("sin matriz no hay narrativa de cómo puede darse el partido" if len(lados_sin) == 2 else
                        f"la matriz del lado {lados_sin[0]} está vacía: falta cómo gana, empata y pierde ese equipo"),
            "comoSeArregla": '"matriz": {"a": {"ganar": {"tactica": …, "pelotaParada": …, "reloj": …, "base": …}, '
                             '"empatar": {…}, "perder": {"gatillo": …, "errorSistemico": …, "psicologico": …, '
                             '"goleada": …}}, "b": {…}}',
        })
    # EL ENSAYO CUENTA LA ESPINA (pedido del usuario, 14/10: «el ensayo tiene
    # que decir si las burbujas le dan buena espina o no»). En Huracán–Gimnasia
    # (15/10) la espina estaba declarada y el ensayo no nombraba ni una burbuja:
    # quien lee el ensayo, que es lo primero que se lee, no se enteraba.
    if not ensayo_cuenta_espina(parte):
        faltan.append({
            "bloque": "ensayo.espina",
            "costara": "la espina está declarada pero el ensayo no la cuenta: quien lee el ensayo "
                       "no se entera de qué dicen las burbujas de cada equipo",
            "comoSeArregla": "un párrafo en el ensayo: la espina de cada equipo (crece, se reinicia, "
                             "negativa o neutra), con qué K se leyó (total, de local, de visita) y por qué",
        })
    # LA ESPINA CONTRA EL RIESGO, SIN DECIRLO (Albion–Torque, 18/10/2026)
    try:
        _rc = _reventon_calculado(fx)
        _esp = (parte.get("lecturaSad") or {}).get("espina")
        contra = [x for x in espina_vs_riesgo(_rc, _esp) if not x["dicho"]]
        contra_tarjeta = [x for x in espina_vs_tarjeta(_rc, _esp)
                          if not x["dicho"] and x["lado"] not in {c["lado"] for c in contra}]
    except Exception:  # noqa: BLE001 — el aviso no tumba el depósito
        contra, contra_tarjeta = [], []
    for x in contra_tarjeta:
        t = x["tarjeta"]
        faltan.append({
            "bloque": f"lecturaSad.espina.{x['lado']}",
            "costara": f"la tarjeta da espina {t['lectura']} FUERTE ({round(t['prob'] * 100)} %) y el parte "
                       f"dice {x['lectura']} sin decir por qué: no se puede medir si leer los skills encima "
                       "de la tarjeta suma o resta",
            "comoSeArregla": "o la espina sigue a la tarjeta, o el `porque` dice «contra la tarjeta porque "
                             "<lo que encontró el EFE/TDE/DTP>» (GET /analisis/cowork/espina/calibracion dice "
                             "quién viene ganando cuando se la contradice)",
        })
    # 25/10/2026: la espina que dice «sigue» con la burbuja en su extremo y la
    # brecha del EFE que es empate técnico, avisadas mientras se puede corregir
    try:
        _ext = espina_sigue_en_extremo(_rc, _esp)
    except Exception:  # noqa: BLE001
        _ext = []
    for x in _ext:
        # el `porque` que nombra el extremo y lo sostiene ya hizo lo que la regla
        # pide (incidencias 659 y 719: Guabirá y Lazio, cobrados con la razón escrita)
        if x.get("dicho"):
            continue
        faltan.append({
            "bloque": f"lecturaSad.espina.{x['lado']}", "codigo": "ESPINA-SIGUE-EN-EXTREMO",
            "costara": f"la espina dice que la racha {x['signo']} sigue con la burbuja {x['donde']} en su "
                       f"{x['nivel']}: el 25/10 reventaron así Libertad y Nacional",
            "comoSeArregla": "con K-EXTREMO o K-CERCA-EXTREMO la espina va «cero» o «neutra», o el `porque` "
                             "nombra el extremo (récord, franja alta) y el hecho del partido que la sostiene; el "
                             "1X2 no se carga a la continuidad",
        })
    try:
        _pct = {l: _totales(parte["equipos"][l]).get("porcentaje") for l in LADOS}
        _emp = empate_tecnico(_pct, list(parte.get("alertas") or [])
                              + alerta_escala(fx, {"a": fx["home_name"], "b": fx["away_name"]}))
    except Exception:  # noqa: BLE001
        _emp = None
    _dicho = re.search(r"empate t[eé]cnico", json.dumps(parte, ensure_ascii=False), re.I)
    if _emp and not _dicho:
        faltan.append({
            "bloque": "equipos.porcentaje", "codigo": "EFE-EMPATE-TECNICO",
            "costara": f"brecha de {_emp['brecha']:.1f} puntos con {', '.join(_emp['motivos'])}: es empate técnico "
                       "de formación (EFE v1.7); nueve partes del 25/10 la usaron para ordenar el partido",
            "comoSeArregla": "el ensayo, el matchup y el 1X2 no se apoyan en la brecha del EFE; decirlo con esas "
                             "palabras («empate técnico de formación») en la lectura o el ensayo, y el aviso se apaga",
        })
    for x in contra:
        faltan.append({
            "bloque": f"lecturaSad.espina.{x['lado']}",
            "costara": f"el riesgo calculado es {x['nivel'].upper()} (racha {x['signo']}) y la espina {x['como']}: "
                       "la pantalla muestra las dos cosas y quien lee no sabe a cuál creerle",
            "comoSeArregla": "o la espina sigue al riesgo, o el `porque` dice «contra el riesgo "
                             f"{x['nivel']} porque…» y el ensayo lo cuenta con esas palabras",
        })
    resumen = {
        "fixtureId": parte["fixtureId"],
        "partido": f"{fx['home_name']} vs {fx['away_name']}",
        "fecha": (fx["date"] or "")[:10],
        "estado": "actualizado" if previo else "guardado",
        "jugadores": {l: len(parte["equipos"][l]["plantel"]) for l in LADOS},
        "documentos": [d["id"] for d in parte["documentos"]],
        "filasMatriz": filas_matriz(parte.get("matriz") or {}),
        "matrizVsPronostico": matriz_vs_pronostico(parte.get("matriz") or {}, parte.get("pronostico") or {}),
        "pronosticoVsMotor": pronostico_vs_motor(parte.get("pronostico") or {}, _prediccion_o_nada(parte["fixtureId"]),
                                                 json.dumps(parte.get("notas") or "", ensure_ascii=False)),
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
        # el DTP estructurado: de qué equipos llegó, la clase del bloque rival
        # que calculó el backend y si la apertura entró a la cadena rodante
        "dtp": {"lados": [b["equipo"] for b in (parte.get("dtp") or {}).get("bloques") or []],
                "claseBloqueRival": {b["equipo"]: b["calculado"]["bloqueRival"]["clase"]
                                     for b in _dtp.leer_dtp(parte.get("dtp") or {})["bloques"]},
                "aperturaEnCadena": dtp_guardado, "aperturaNoGuardada": dtp_no_guardado},
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
    # LAS ALERTAS QUE SE CALCULAN AL LEER, YA EN EL RECIBO (incidencias 771 y
    # 806: HERENCIA-DTP y TIPOLOGIA-VS-INDICES aparecían recién en el GET —el
    # SOB2 heredado daba vuelta la tipología de Internacional y nadie lo veía
    # al depositar—, y el recibo solo traía cuántas alertas había). Con la lista
    # se corrige en el mismo depósito, sin otro GET.
    resumen["alertasAlLeer"] = _alertas_al_leer(parte["fixtureId"])
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


def _alertas_al_leer(fixture_id: int) -> list[dict]:
    """Las alertas calculadas que el GET le va a poner a este parte (código,
    lado y detalle); [] si el DTO no se puede armar todavía."""
    try:
        leido = dto(fixture_id) or {}
    except Exception:  # noqa: BLE001 — el depósito ya quedó guardado: sin la lista, el GET la trae
        return []
    return [{"codigo": a.get("codigo"), "equipo": a.get("equipo") or "", "tipo": a.get("tipo") or "",
             "detalle": a.get("detalle") or ""}
            for a in leido.get("alertas") or [] if a.get("codigo") in _ALERTAS_CALCULADAS]


def borrar(fixture_id: int) -> bool:
    with _conectar() as con:
        cur = con.execute("DELETE FROM parte_cowork WHERE fixture_id=?", (fixture_id,))
    return cur.rowcount > 0


# ── lectura: el DTO que pinta la pantalla ───────────────────────────────────

def empate_en_la_cima(probs: dict) -> list[str]:
    """Los resultados empatados en la probabilidad más alta del 1X2 (vacío si
    hay un elegido)."""
    vals = {k: probs.get(k) for k in ("local", "empate", "visita") if isinstance(probs.get(k), (int, float))}
    if len(vals) < 3:
        return []
    top = max(vals.values())
    cima = [k for k, v in vals.items() if abs(v - top) < 1e-9]
    return cima if len(cima) > 1 else []


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
    # EL PORCENTAJE SE CUENTA SOBRE LO DECLARADO (31/10/2026, incidencia 799,
    # decisión del usuario): con la Copa del Rey salieron Guijuelo 4,8 % (solo E)
    # y Prat 2,4 % «SIN FORMACIÓN» (solo A) porque los bloques sin puntuar
    # contaban como 0 en el máximo de 21 —el peor juicio de la rúbrica sobre lo
    # que nadie evaluó—. Un bloque sin declarar no entra ni al total ni al máximo.
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
            continue
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
    if len(declarados) < MINIMO_BLOQUES_EFE:
        return {"total": round(total, 2), "maximoAlcanzable": round(maximo, 2),
                "porcentaje": None, "clasificacion": "",
                "sinBloques": False, "pocosBloques": True, "bloquesSinDeclarar": sin_declarar,
                "notaTotales": (f"pocos bloques declarados ({', '.join(declarados)}): con menos de "
                                f"{MINIMO_BLOQUES_EFE} de A-E el EFE no tiene porcentaje ni clasificación"
                                + nota_legado)}
    pct = round((total / maximo) * 100, 1) if maximo else 0.0
    return {"total": round(total, 2), "maximoAlcanzable": round(maximo, 2),
            "porcentaje": pct, "clasificacion": clasificacion_de(pct),
            "sinBloques": False, "bloquesSinDeclarar": sin_declarar,
            # el hueco se DICE: el porcentaje es sobre lo declarado, no sobre la rúbrica entera
            "notaTotales": ((f"faltan los sub-scores {', '.join(sin_declarar)}: el porcentaje es sobre "
                             "los bloques declarados" if sin_declarar else "") + nota_legado).strip(". ")}


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
    from backend.analisis.f1_base import nunca_juntos
    d = bloque_f.resolver(plantel, fuera, xi.get("once") or [], xi.get("banca") or [],
                          ids=xi.get("ids") or None, nunca_juntos=nunca_juntos)
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
    # LA VISTA ES «AL DÍA DEL PARTIDO». Se recalcula al leer, y sin el corte un
    # parte de un partido ya jugado mostraba ese mismo resultado en el timeline
    # y en la tabla (City–PSG y LASK–Liverpool, 17/10/2026): hindsight en la
    # pantalla prepartido. Se corta el día anterior y la tabla, antes del pitazo.
    pitazo = str(fx["date"])
    dia_antes = (datetime.strptime(pitazo[:10], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    desde, hasta = crono.ventana(hasta=min(dia_antes, datetime.now(timezone.utc).strftime("%Y-%m-%d")))
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
                                     fx["league_season"], desde, hasta, antes=pitazo)},
            {"nombre": fx["away_name"], "lado": "derecha",
             "color": "#E5484D", "color_secundario": "#F2C1C3",
             "stats": crono.stats_de(fx["away_team_id"], fx["league_id"],
                                     fx["league_season"], desde, hasta, antes=pitazo)},
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


def _guardar_apertura_dtp(fx, dtp: dict) -> tuple[list[str], list[dict]]:
    """La APERTURA estructurada del DTP entra en `cadena_dtp` para que el
    próximo parte del equipo la cierre (M4/M5) contra lo que se dijo ANTES, y
    no contra la memoria. Dos candados: solo si el partido todavía no arrancó
    (una apertura escrita con el partido rodando es hindsight) y nunca pisa una
    apertura ya guardada (`guardar_cadena` conserva la primera)."""
    from backend.analisis.motor import _partido_n
    bloques = (dtp or {}).get("bloques") or []
    if not bloques:
        return [], []
    est = saddb.query_one("sad", "SELECT status_short FROM fixtures WHERE id=?", (fx["id"],))
    arranco = ((est["status_short"] if est else None) or "NS") not in ("NS", "TBD", "PST", "")
    guardados, no = [], []
    for b in bloques:
        lado = b["equipo"]
        foco, rival, tid = ((fx["home_name"], fx["away_name"], fx["home_team_id"]) if lado == "a"
                            else (fx["away_name"], fx["home_name"], fx["away_team_id"]))
        if arranco:
            no.append({"equipo": foco, "porque": "el partido ya arrancó: la apertura se guarda solo "
                                                 "antes del pitazo (anti-hindsight)"})
            continue
        previo = efedb.eslabon_de_fixture(foco, fx["id"]) or {}
        if previo.get("apertura"):
            # UNA VEZ, ANTES DEL PITAZO, Y SOLO SI LA PRIMERA NO TENÍA XI (581):
            # sin XI de referencia el DTP no puede avisar contra el once oficial
            nueva = _dtp.apertura_para_cadena(b)
            sin_xi_antes = not str(((previo["apertura"].get("m1") or {}).get("xiReferencia")) or "").strip()
            con_xi_ahora = bool(str(((nueva.get("m1") or {}).get("xiReferencia")) or "").strip())
            if sin_xi_antes and con_xi_ahora:
                nueva["reemplazaSinXi"] = {"en": efedb.ahora(),
                                           "porque": "la primera apertura entró sin XI de referencia (581)"}
                if efedb.reemplazar_apertura_sin_xi(foco, fx["id"], nueva):
                    guardados.append(foco)
                    continue
            no.append({"equipo": foco, "porque": "ya había una apertura guardada para este partido: "
                                                 "manda la primera"
                                                 + ("" if not sin_xi_antes else
                                                    " (estaba sin XI, pero esta tampoco trae xiReferencia)")})
            continue
        efedb.guardar_cadena(foco, _partido_n(tid, fx["date"] or ""), rival, (fx["date"] or "")[:10] or None,
                             fx["id"], _dtp.apertura_para_cadena(b))
        guardados.append(foco)
    return guardados, no


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


def _tde_calculado(tde: dict, herencia: dict | None = None) -> dict:
    """El TDE con su índice CALCULADO, un bloque por equipo.

    Igual que el bloque F y que los totales del EFE: si el dato de entrada está,
    el número lo pone la aritmética. Lo que llegó escrito se conserva al lado en
    `declarado`, y si no coincide se dice — un IE mal sumado que nadie compara
    es una banda de probabilidad equivocada durante meses.
    """
    bloques = bloques_tde(tde)
    if not bloques:
        return {}
    return {"bloques": [_bloque_calculado(_heredar(b, (herencia or {}).get(b.get("equipo") or ""))) for b in bloques]}


def _heredar(bloque: dict, her: dict | None) -> dict:
    """C1 y SOB2 vienen del DTP (skill teorema-del-echado: «no se re-estiman»).
    Solo sobre un bloque que ya trae indicadores —con dos sueltos no se arma un
    índice—; lo que Cowork había declarado queda al lado para auditar."""
    ind = bloque.get("indicadores") or {}
    if not her or not ind:
        return bloque
    nuevo, heredados = dict(ind), []
    for clave, h in her.items():
        declarado = ind.get(clave)
        if h["valor"] is None:   # el DTP no da valor (bloque ambiguo): queda lo declarado, y se dice
            heredados.append({"indicador": clave, "valor": declarado, "declarado": declarado, "de": h["de"],
                              "discrepa": False, "noHeredado": True})
            continue
        nuevo[clave] = h["valor"]
        heredados.append({"indicador": clave, "valor": h["valor"], "declarado": declarado, "de": h["de"],
                          "discrepa": declarado is not None and abs(float(declarado) - h["valor"]) > 1e-9})
    return {**bloque, "indicadores": nuevo, "heredadoDtp": heredados}


def _bloque_calculado(tde: dict) -> dict:
    ind = tde.get("indicadores") or {}
    if not ind:
        return tde
    from backend.analisis import tde as tdemod
    calc = tdemod.indice(ind)
    fuera = dict(tde)
    fuera["calculado"] = calc
    # UN 0.0 NO DECLARA NADA. Es el relleno de `_num(None)` de los partes
    # anteriores al 11/10/2026: un IE o ISE de 0 exacto con indicadores
    # puntuados no lo escribe nadie a mano. Se lee como «no declarado».
    declarado = {k: (None if tde.get(k) in (0, 0.0) else tde.get(k)) for k in ("ie", "ise")}
    fuera["declarado"] = declarado
    if calc.get("sinDato"):
        for clave in ("ie", "ise"):
            if fuera.get(clave) in (0, 0.0):
                fuera[clave] = None
        # el ISE no depende de los bloques del IE: si hay SOB, se publica igual
        if calc.get("ise") is not None:
            fuera["ise"] = calc["ise"]
    else:
        discrepa = []
        for clave in ("ie", "ise"):
            d, c = declarado.get(clave), calc.get(clave)
            if d and c is not None and abs(float(d) - float(c)) > 0.1:
                discrepa.append(f"{clave.upper()}: llegó {d} y la cuenta da {c}")
        fuera["discrepancia"] = discrepa
        # el número que manda es el calculado
        fuera["ie"], fuera["ise"] = calc["ie"], calc.get("ise")
        # la configuración dual la dice la cuenta, no la casilla: San Lorenzo
        # (IE 5.78 · ISE 6.67) llegó con `disciplina43: false`
        if (calc.get("riesgo") or {}).get("dual"):
            fuera["disciplina43"] = True
    # el índice de cada vía es el calculado de su vía: un 0.0 en `vias[].indice`
    # (San Lorenzo, Grêmio–Inter) no lo es, y una discrepancia se dice
    vias = []
    for v in fuera.get("vias") or []:
        v = dict(v)
        nombre = (v.get("nombre") or "").upper()
        calc_v = calc.get("ise") if nombre.startswith("SOB") else (calc.get("ie") if nombre.startswith("ECHADA") else None)
        if calc_v is not None:
            if v.get("indice") not in (None, "", 0, 0.0) and abs(float(v["indice"]) - float(calc_v)) > 0.1:
                fuera.setdefault("discrepancia", []).append(
                    f"vía {nombre}: llegó {v['indice']} y la cuenta da {calc_v}")
            v["indice"] = calc_v
        vias.append(v)
    if vias:
        fuera["vias"] = vias
    return fuera


def _formacion_al_dia(fixture_id: int, xi: dict) -> dict:
    """LA FORMACIÓN DEL ONCE ES LA DE LA FICHA DE HOY. El once se cierra con la
    alineación anunciada antes del pitazo y la API corrige el string de la
    formación después (Rayo 4-3-3 → 4-2-3-1, Tolima 5-3-2 → 4-4-2, Parma
    3-5-2 → 3-4-2-1: once incidencias del 18-19/10/2026): el parte mostraba una
    formación que ya no era la de la ficha que dice citar, mientras el DTP leía
    la nueva. Si el lado viene de la ficha y la formación cambió, manda la de
    la ficha y la que se guardó al cerrar viaja en `formacionAlCerrar`. Los
    nombres no se tocan: el bloque F se cerró con ellos."""
    if not any((xi.get(l) or {}).get("fuente") == FUENTE_FICHA for l in LADOS):
        return xi
    fx = _fixture(fixture_id)
    if not fx:
        return xi
    out = dict(xi)
    for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
        x = xi.get(lado) or {}
        if x.get("fuente") != FUENTE_FICHA:
            continue
        try:
            f = saddb.query_one("sad", "SELECT formacion FROM alineaciones WHERE fixture_id=? AND team_id=? "
                                       "AND formacion IS NOT NULL AND formacion <> '' LIMIT 1", (fixture_id, tid))
        except Exception:  # noqa: BLE001 — base sin alineaciones: queda la guardada
            f = None
        hoy = f["formacion"] if f else None
        if hoy and hoy != (x.get("formacion") or ""):
            out[lado] = {**x, "formacion": hoy, "formacionAlCerrar": x.get("formacion") or ""}
    return out


def _utc(t) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(t).strip().replace("Z", "+00:00").replace(" ", "T"))
    except (TypeError, ValueError):
        return None
    return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)


def _antes_del_pitazo(ahora: str, pitazo) -> bool:
    a, p = _utc(ahora), _utc(pitazo)
    return bool(a and p and a < p)


# La grilla de la rutina de rehacer (CLAUDE.md, deuda 11), de 05 a 23 de Lima
# (UTC−5, sin horario de verano). Hasta el 31/10/2026 eran dos disparos por
# hora (:07 y :37) con piso de 15 min; desde entonces (incidencia 636, decisión
# del usuario: el once llega ~25 min antes y caía entre dos disparos) son tres
# (:02, :22 y :42) con piso de 5. Un parte se juzga con la grilla de SU día:
# una regla no se cobra hacia atrás.
REHACER_GRILLAS = (("2026-10-31 01:21:00", (2, 22, 42), 5),)
REHACER_DISPAROS_MIN, REHACER_PISO_ANTES = (7, 37), 15
REHACER_HORAS_LIMA = (5, 23)


def grilla_rehacer(t: datetime | None) -> tuple[tuple[int, ...], int]:
    """(minutos de los disparos, piso en minutos antes del pitazo) vigentes en `t`."""
    out = (REHACER_DISPAROS_MIN, REHACER_PISO_ANTES)
    for desde, minutos, piso in REHACER_GRILLAS:
        if t is not None and t >= _utc(desde):
            out = (minutos, piso)
    return out


def disparo_entre(desde: datetime, hasta: datetime) -> bool:
    """¿Cae algún disparo de la rutina de rehacer en (desde, hasta]?"""
    if not desde or not hasta or hasta <= desde:
        return False
    lima = timezone(timedelta(hours=-5))
    t = desde.astimezone(lima).replace(second=0, microsecond=0)
    fin = hasta.astimezone(lima)
    while t <= fin:
        minutos, _ = grilla_rehacer(t.astimezone(timezone.utc))
        if (t.minute in minutos and REHACER_HORAS_LIMA[0] <= t.hour <= REHACER_HORAS_LIMA[1]
                and desde.astimezone(lima) < t):
            return True
        t += timedelta(minutes=1)
    return False


def momento_rehacer(alertas: list[dict], fx, deposito_previo: str | None) -> list[dict]:
    """CUÁNDO llegó el once que dispara DTP-REHACER, una vez jugado el partido
    (26/10/2026: 12 lecciones del DTP del 25/10 decían «sonó y no se rehízo» y
    la rutina había rehecho 18 partes; la API corrigió la formación en el
    refresco de los últimos 15 minutos, cuando ya no quedaba disparo). Con la
    hora de la versión final del once (`alineaciones_versiones`) y la del último
    depósito ANTES del pitazo, cada DTP-REHACER sale con `momento`:
      · `tardio` — el once final llegó a menos de REHACER_DESDE_MIN del pitazo:
        nadie podía rehacer; apertura caída por un once tardío, no un aviso ignorado.
        También si llegó antes de ese límite pero ningún disparo de la rutina
        (:07 y :37 de Lima) cayó entre su hora y el límite (incidencia 732).
      · `sinRehacer` — llegó a tiempo para un disparo y el parte no se volvió
        a depositar después: falla de la corrida de rehacer.
      · `conocido` — el once ya estaba cuando se depositó por última vez y la
        apertura igual lo contradice: lo rehecho no lo corrigió.
    Sin NINGUNA versión del once capturada hasta el pitazo (llegó después, o
    nunca) también es `tardio`: no había once con que rehacer (30/10/2026,
    incidencia 847: las copas nacionales capturaban el once con la ficha).
    Antes del pitazo, sin la tabla de versiones o sin depósito previo sellado
    (partes anteriores a esta regla), la alerta sale como estaba."""
    if not alertas or not fx:
        return alertas
    try:
        est = saddb.query_one("sad", "SELECT status_short FROM fixtures WHERE id=?", (fx["id"],))
        if (est and (est["status_short"] or "NS") in ("NS", "TBD", "PST")) or not deposito_previo:
            return alertas
        filas = saddb.query("sad", "SELECT team_id, formacion, capturada_en FROM alineaciones_versiones "
                                   "WHERE fixture_id=? ORDER BY capturada_en", (fx["id"],))
    except Exception:  # noqa: BLE001 — sin la tabla (base vieja) no hay momento que decir
        return alertas
    pitazo, dep = _utc(fx["date"]), _utc(deposito_previo)
    finales, despues = {}, {}
    for f in filas:
        # LA VERSIÓN DEL PITAZO, NO LA DEL FINAL: el refresco de la ficha en
        # juego o al terminar vuelve a sellar el once (Guabirá a las 23:54 con
        # pitazo 21:59, Riestra 116 min después: «-117 min antes del pitazo» y
        # todo `tardio`, incidencias 688 y 697). Lo capturado después del saque
        # no es el once con que se podía rehacer.
        t_f = _utc(f["capturada_en"])
        if pitazo and t_f and t_f > pitazo:
            despues[f["team_id"]] = f
            continue
        finales[f["team_id"]] = f   # ordenadas: queda la última de cada equipo
    if not pitazo or not dep:
        return alertas
    if not finales:
        texto = ("ninguna versión del once se capturó antes del pitazo: no había once con que rehacer; "
                 "apertura caída por un once que llegó tarde, no un aviso ignorado")
        return [{**a, "momento": "tardio", "onceFinalEn": None,
                 "ultimoDepositoPrevio": dep.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "detalle": f"{a['detalle']} [{texto}]"} if a.get("codigo") == "DTP-REHACER" else a
                for a in alertas]
    t = max(_utc(f["capturada_en"]) for f in finales.values())
    piso = grilla_rehacer(pitazo)[1]
    limite = pitazo - timedelta(minutes=piso)
    antes = int((pitazo - t).total_seconds() // 60)
    hora = t.strftime("%H:%M UTC")
    # 848: el once previo ya estaba en el depósito, pero la API corrigió la
    # formación DESPUÉS del pitazo y es esa corrección la que hace sonar la
    # alerta: nadie podía rehacer con ella
    corregida = [(finales[k]["formacion"], v["formacion"]) for k, v in despues.items()
                 if k in finales and v["formacion"] and v["formacion"] != finales[k]["formacion"]]
    if t <= dep and corregida:
        momento, texto = "tardio", ("la API corrigió la formación después del pitazo ("
                                    + ", ".join(f"{a} → {b}" for a, b in corregida)
                                    + "); el once previo ya estaba en el último depósito: nadie podía rehacer "
                                    "con la corrección")
    elif t <= dep:
        momento, texto = "conocido", (f"el once final ya estaba ({hora}) cuando se depositó por última vez "
                                      f"({dep.strftime('%H:%M UTC')}): lo rehecho no lo corrigió")
    elif t > limite:
        momento, texto = "tardio", (f"la versión final del once llegó a las {hora}, {antes} min antes del pitazo, "
                                    f"después del último rehacer posible (pitazo − {piso} min): "
                                    "apertura caída por un once tardío, no un aviso ignorado")
    elif not disparo_entre(t, limite):
        # incidencia 732: el once de las 19:17 con pitazo 19:45 llegó después del
        # disparo de las 19:07 y el de las 19:37 ya cae a 8 min; nadie podía rehacer
        momento, texto = "tardio", (f"la versión final del once llegó a las {hora}, {antes} min antes del pitazo, "
                                    "y ningún disparo de la rutina de rehacer cayó entre esa "
                                    f"hora y el pitazo − {piso} min: once tardío para la grilla, "
                                    "no un aviso ignorado")
    else:
        momento, texto = "sinRehacer", (f"el once final llegó a las {hora}, {antes} min antes del pitazo, y el "
                                        "parte no se volvió a depositar después: la corrida de rehacer no lo tomó")
    out = []
    for a in alertas:
        if a.get("codigo") == "DTP-REHACER":
            a = {**a, "momento": momento, "onceFinalEn": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "ultimoDepositoPrevio": dep.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "detalle": f"{a['detalle']} [{texto}]"}
        out.append(a)
    return out


def dto(fixture_id: int) -> dict | None:
    """Todo lo que la pantalla necesita, con lo calculable ya calculado."""
    with _conectar() as con:
        fila = con.execute(
            "SELECT fixture_id, fecha, equipo_a, equipo_b, estado, version, parte_json, "
            "xi_json, creado_en, actualizado_en, cohorte, cuarentena_json, coherencia_json, "
            "banco_desmentido_json, deposito_previo_en FROM parte_cowork WHERE fixture_id=?",
            (fixture_id,),
        ).fetchone()
    if not fila:
        return None
    parte = json.loads(fila["parte_json"])
    xi = json.loads(fila["xi_json"]) if fila["xi_json"] else {}
    xi = _formacion_al_dia(fixture_id, xi)
    alertas = list(parte["alertas"])
    equipos = {}
    for lado in LADOS:
        eq = parte["equipos"][lado]
        tot = _totales(eq)
        disp = _disponibilidad(eq, xi.get(lado))
        if disp.get("resuelto"):
            f3 = bloque_f.alerta_f3(tot["clasificacion"], disp.get("ipNivel", "verde"),
                                    bloque_f.titulares_fijos_fuera(disp.get("jugadores") or []),
                                    disp.get("zonasCriticas"))
        else:
            # ANTES DEL ONCE, con lo ya conocido (incidencia 383, Nacional: IP 15
            # rojo y FORMADO sin F3 hasta cerrar el once). Provisional y dicho.
            ra = (disp.get("ramas") or {}).get("a") or {}
            f3 = (bloque_f.alerta_f3(tot["clasificacion"], ra.get("ipNivel", "verde"),
                                     [x.get("nombre", "") for x in ra.get("fuera") or []
                                      if (x.get("rol") or "").upper() == "TF" and x.get("estado") == "baja"],
                                     ra.get("zonasCriticas"), provisional=True)
                  if ra else None)
        if f3:
            alertas.append({**f3, "equipo": lado})
        # TITULARES DEL ONCE OFICIAL SIN FILA EN LA TABLA F1 (incidencia 743, 7
        # veces: Lecce con 8 nombres de la hoja sin reconocer, Vasco con Jair,
        # Lucas Freitas y Gabriel Pereira). No pesan en el IP ni como factor X:
        # el bloque F se cerró sobre otro equipo y nadie lo decía.
        sin_fila = disp.get("noReconocidosOnce") or []
        if disp.get("resuelto") and sin_fila:
            alertas.append({
                "codigo": "ONCE-SIN-FILA-F1", "equipo": lado, "tipo": "dato",
                "detalle": f"{len(sin_fila)} titular(es) del once oficial sin fila en la tabla F1: "
                           f"{', '.join(sin_fila)}. No pesan en el IP ni en el FACTOR-X: si son caras "
                           "nuevas o rotados, el EFE y el bloque F leyeron otro equipo (con 3 o más, "
                           "rehacer la tabla F1 con GET /analisis/cowork/f1/{id} y re-depositar).",
                "titulares": sin_fila,
            })
        equipos[lado] = {**eq, **tot, "disponibilidad": disp}
    tde_calc = _tde_calculado(parte.get("tde") or {}, _dtp.herencia_tde(parte.get("dtp") or {}))
    # la herencia que contradice lo declarado se dice: el DTP manda, pero un
    # C1 o un SOB2 escritos distinto en el TDE son dos juicios del mismo hecho
    for b in tde_calc.get("bloques") or []:
        for h in b.get("heredadoDtp") or []:
            if h["discrepa"] and b.get("equipo") in LADOS:
                alertas.append({
                    "codigo": "HERENCIA-DTP", "equipo": b["equipo"], "tipo": "dato",
                    "detalle": f"{h['indicador']} del TDE: se declaró {h['declarado']} y el DTP dice "
                               f"{h['valor']} ({h['de']}). Manda el DTP —el skill prohíbe re-estimarlo—: "
                               "se corrige el indicador del TDE al del DTP (al rehacer con el once, el "
                               "DTP NO vuelve atrás para callar esta alerta, incidencia 634); si el DTP "
                               "está mal, se corrige el DTP",
                })
    # LA TIPOLOGÍA MODAL CONTRA LOS DOS ÍNDICES (TDE PASO 3, incidencia 538:
    # Porto con ECHADA-PSI e IE 2.94 < ISE 3.33). Si el ISE supera al IE el
    # tipo modal es SOB, y al revés: un aviso de tipo dato, no se corrige solo.
    for b in tde_calc.get("bloques") or []:
        alerta = tipologia_vs_indices(b)
        if alerta and b.get("equipo") in LADOS:
            alertas.append({**alerta, "equipo": b["equipo"]})
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
                           f"{cob.get('nominales')} indicadores. El EFE se calcula solo sobre los "
                           "bloques declarados y el IE sobre los indicadores que hay: los dos "
                           "números miran menos partido del que parece y salen del mismo vacío. "
                           "No es un equipo pésimo con riesgo altísimo, es un equipo con pocos "
                           "datos (incidencia 815: el texto decía que el hueco hundía el EFE, y el "
                           "denominador ya se ajusta)",
            })
    fx = _fixture(fila["fixture_id"])
    reventon = _reventon_calculado(fx)
    # la burbuja en su máximo histórico va a la tira de alertas, no solo a la
    # lectura: lo que decide cuánto se carga tiene que verse antes que nada
    alertas.extend(alertas_extremo(reventon, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    alertas.extend(alertas_familias(reventon, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    alertas.extend(alertas_espina(reventon, (parte.get("lecturaSad") or {}).get("espina"),
                                  {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    # dos equipos de ligas distintas: el nivel no compara entre bases, y el
    # parte lo dice antes de que alguien lea los dos números uno contra otro
    alertas.extend(alerta_escala(fx, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    # la espina que dice «sigue» con la burbuja en su extremo, y la brecha del
    # EFE que es empate técnico (25/10/2026): reglas que se incumplían, calculadas
    alertas.extend(alertas_t54_sin_declarar(parte, alertas, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    alertas.extend(marcar_posteriores(
        alertas_espina_extremo(reventon, (parte.get("lecturaSad") or {}).get("espina"),
                               {"a": fila["equipo_a"], "b": fila["equipo_b"]})
        + alerta_empate_tecnico({l: equipos[l].get("porcentaje") for l in LADOS}, alertas,
                                {"a": fila["equipo_a"], "b": fila["equipo_b"]}),
        fila["creado_en"]))
    alertas.extend(alertas_dt(parte, fx, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    alertas.extend(alertas_colapso(parte, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    alertas.extend(alertas_eliminatoria(parte, fx, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    # un decisivo de la base que no está en la tabla F1 no pesa en el IP
    alertas.extend(_f1_base.alertas(parte, fx, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    # un sancionado de la base (roja o amarillas) que el parte no declaró de baja
    alertas.extend(_f1_base.alertas_sancion(parte, fx, {"a": fila["equipo_a"], "b": fila["equipo_b"]}))
    # el once oficial contra la apertura del DTP: si no cuadra, el M2 se
    # escribió sobre otro equipo
    oficial = _dtp.oficial_de(fila["fixture_id"])
    # LA FORMACIÓN QUE LA API CORRIGIÓ DESPUÉS DEL CIERRE (incidencia 559, Orense–
    # Delfín): el parte se rehízo con la que había y la API la cambió después;
    # sin esto, DTP-REHACER pedía rehacer lo ya rehecho con el dato del momento
    for lado in LADOS:
        if (xi.get(lado) or {}).get("formacionAlCerrar") and lado in oficial:
            oficial[lado] = {**oficial[lado], "formacionAlCerrar": xi[lado]["formacionAlCerrar"]}
    dtp_leido = _dtp.leer_dtp(parte.get("dtp") or {}, oficial)
    alertas.extend(momento_rehacer(_dtp.alertas_rehacer(dtp_leido, {"a": fila["equipo_a"], "b": fila["equipo_b"]}),
                                   fx, fila["deposito_previo_en"]))
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
        "lecturaSad": {**(parte.get("lecturaSad") or _lectura_sad({})), "reventonCalculado": reventon,
                       # los goles acotados del partido (REVENTON §17), calculados al leer
                       "golesAcotados": _goles_acotados(fx)},
        "tde": tde_calc,
        "dtp": dtp_leido,
        "timeline": timeline,
        "pronostico": parte["pronostico"],
        # la ventaja sobre el mercado (26/10/2026): calculada al leer, nunca declarada
        "vsMercado": _ventaja_o_nada(fila["fixture_id"], parte["pronostico"], fila["parte_json"]),
        "matriz": parte.get("matriz") or {},
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
        "bancoDesmentido": (json.loads(fila["banco_desmentido_json"])
                            if fila["banco_desmentido_json"] else {}),
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


def poner_cuarentena(fixture_id: int, motivo: str, ensena: bool = False) -> dict:
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
        # LA CUARENTENA QUE ENSEÑA (usuario, 27/10/2026, Comerciantes–Cienciano:
        # el parte se escribió con el DT cesado). El caso sale de TODA métrica,
        # pero el sistema falló y de eso se aprende: sus lecciones siguen en la
        # lista del skill y en el dossier, fijando rúbrica sin mover un número.
        if ensena:
            marca["ensena"] = True
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
        "SELECT jugador, player_id, titular, formacion FROM alineaciones WHERE fixture_id=? AND team_id=? "
        "ORDER BY titular DESC",
        (fixture_id, team_id),
    )
    from backend.nombres import limpiar_nombre
    filas = [{**dict(f), "jugador": limpiar_nombre(f["jugador"])} for f in filas]
    titulares = [f["jugador"] for f in filas if f["titular"] and f["jugador"]]
    if len(titulares) < 7:  # media alineación no es una alineación
        return None
    return {
        "once": titulares,
        "banca": [f["jugador"] for f in filas if not f["titular"] and f["jugador"]],
        # nombre de la hoja → id de la API: el cruce exacto con la tabla F1
        "ids": _ids_por_nombre(filas),
        "formacion": filas[0]["formacion"] or "",
        "fuente": FUENTE_FICHA,
        "capturadoEn": efedb.ahora(),
    }


def _ids_por_nombre(filas) -> dict:
    """Nombre de la hoja → id; un nombre REPETIDO lleva la lista de sus ids en
    el orden de la hoja (incidencia 372: Shakhtar alineó a dos «Pedrinho»
    titulares, el dict guardaba uno y el otro salía de baja con IP 2.0)."""
    out: dict = {}
    for f in filas:
        if not (f["jugador"] and f["player_id"] and int(f["player_id"]) > 0):
            continue
        pid, previo = int(f["player_id"]), out.get(f["jugador"])
        out[f["jugador"]] = pid if previo is None else (previo if isinstance(previo, list) else [previo]) + [pid]
    return out


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
            ids = {}
            for k, v in (nuevo.get("ids") or {}).items() if isinstance(nuevo.get("ids"), dict) else []:
                try:
                    ids[_txt(k)] = [int(x) for x in v] if isinstance(v, list) else int(v)
                except (TypeError, ValueError):
                    pass
            guardado[lado] = {
                "once": once,
                "banca": _lista_txt(nuevo.get("banca")),
                **({"ids": ids} if ids else {}),
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

OTRAS_LECCIONES_MAX = 6


def _otras_lecciones(v, rechazos: list, donde: str) -> list[dict]:
    """Las lecciones de un lado después de la primera.

    UNA AUTOPSIA ENSEÑA MÁS DE UNA COSA. Cusco–Cristal (11/10/2026) tocó la
    disciplina 16 del TDE, el COLAPSO EN CASCADA del EFE y el mapa de duelos
    del DTP, y el veredicto tenía lugar para una: las otras dos quedaron en
    `notas`, que el inventario no lee. Cada una es un item con su skill y su
    regla, y se acumula como cualquier otra lección (clave `fixture:lado:n`)."""
    if v is None:
        return []
    if not isinstance(v, list):
        rechazos.append({"donde": donde, "porque": f"`otrasLecciones` tiene que ser una lista, llegó {type(v).__name__}",
                         "esperado": '[{"skill": "…", "reglaTocada": "…", "leccion": "…"}]'})
        return []
    fuera = []
    for i, x in enumerate(v):
        if not isinstance(x, dict) or not _txt(x.get("leccion")) or not _txt(x.get("skill")):
            rechazos.append({"donde": f"{donde}[{i}]", "porque": "una lección necesita `skill` y `leccion`: no se guardó",
                             "esperado": '{"skill": "efe-clasificador", "reglaTocada": "…", "leccion": "…"}'})
            continue
        fuera.append({"skill": _txt(x.get("skill")), "reglaTocada": _txt(x.get("reglaTocada")),
                      "leccion": _txt(x.get("leccion")), "queP": _txt(x.get("queP"))})
    if len(fuera) > OTRAS_LECCIONES_MAX:
        rechazos.append({"donde": donde, "porque": f"llegaron {len(fuera)}: se guardan las primeras "
                                                   f"{OTRAS_LECCIONES_MAX}",
                         "esperado": "las que tocan una regla; el resto va en `notas`"})
        fuera = fuera[:OTRAS_LECCIONES_MAX]
    return fuera


def _lado_veredicto(x, rechazos: list | None = None, donde: str = "porLado") -> dict | None:
    if not isinstance(x, dict):
        return None
    v = _txt(x.get("veredicto")).lower()
    if v not in vered.VEREDICTOS:
        return None
    out = {"veredicto": v, "queP": _txt(x.get("queP")), "leccion": _txt(x.get("leccion")),
           "skill": _txt(x.get("skill")), "reglaTocada": _txt(x.get("reglaTocada"))}
    otras = _otras_lecciones(x.get("otrasLecciones"), rechazos if rechazos is not None else [],
                             f"{donde}.otrasLecciones")
    if otras:
        out["otrasLecciones"] = otras
    # ¿LA NARRATIVA DE LA MATRIZ APARECIÓ? Cuál escenario se jugó lo dice el
    # marcador (lo calcula el backend en `objetivo.matriz`); si lo que se
    # escribió para ese escenario —la palanca, el gatillo— fue lo que pasó es
    # juicio, y va como observación: sin acierto ni tasa, para la autopsia.
    esc = x.get("escenario")
    if isinstance(esc, dict) and (esc.get("aparecio") or esc.get("que")):
        ap = _txt(esc.get("aparecio")).lower().replace("í", "i")
        if ap not in ("si", "parcial", "no", ""):
            if rechazos is not None:
                rechazos.append({"donde": f"{donde}.escenario.aparecio", "porque": f"«{ap}» no es una respuesta",
                                 "esperado": "si · parcial · no"})
            ap = ""
        out["escenario"] = {"aparecio": ap, "que": _txt(esc.get("que"))}
    # ¿POR QUÉ SE CORTÓ? Las otras burbujas que el partido cortó vienen en
    # `objetivo.otrasFamilias`; la causa es juicio y va con un mecanismo de la
    # lista cerrada del estudio de reventones, para que se pueda contar.
    cortes = _cortes_veredicto(x.get("cortes"), rechazos, f"{donde}.cortes")
    if cortes:
        out["cortes"] = cortes
    return out


def _cortes_veredicto(x, rechazos: list | None, donde: str) -> list[dict]:
    from backend.analisis.familias import NARRADAS
    from backend.analisis.reventones import MECANISMOS
    familias_ok = {c for c, _s, _n in NARRADAS}
    out = []
    for i, c in enumerate(x if isinstance(x, list) else []):
        if not isinstance(c, dict):
            continue
        fam, amb = _txt(c.get("familia")), _txt(c.get("ambito")).lower() or "total"
        mec, porque = _txt(c.get("mecanismo")).lower(), _txt(c.get("porque"))
        if fam not in familias_ok:
            if rechazos is not None:
                rechazos.append({"donde": f"{donde}[{i}].familia", "porque": f"«{fam}» no es una familia narrada",
                                 "esperado": " · ".join(sorted(familias_ok))})
            continue
        if amb not in ("local", "visita", "total"):
            amb = "total"
        if mec and mec not in MECANISMOS:
            if rechazos is not None:
                rechazos.append({"donde": f"{donde}[{i}].mecanismo", "porque": f"«{mec}» no está en la lista",
                                 "esperado": " · ".join(MECANISMOS)})
            mec = "otro"
        if not (mec or porque):
            continue
        out.append({"familia": fam, "ambito": amb, "mecanismo": mec, "porque": porque})
    return out


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
    rechazos: list[dict] = []
    for l in LADOS:
        v = _lado_veredicto((payload.get("porLado") or {}).get(l), rechazos, f"porLado.{l}")
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


def objetivo_de(fixture_id: int) -> dict | None:
    """La parte objetiva del caso, haya veredicto o no. None = sin parte."""
    with _conectar() as con:
        fila = con.execute("SELECT parte_json, veredicto_json FROM parte_cowork WHERE fixture_id=?",
                           (fixture_id,)).fetchone()
    if not fila:
        return None
    return {"fixtureId": fixture_id, "tieneVeredicto": bool(fila["veredicto_json"]),
            "objetivo": vered.objetivo(fixture_id, json.loads(fila["parte_json"]))}


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


def ficha_crecio(previo: dict, nuevo: dict) -> bool:
    """¿La ficha trae ahora más (u otro) once o más banca que lo que se cerró?"""
    po, pb = previo.get("once") or [], previo.get("banca") or []
    return (len(nuevo["once"]) > len(po) or len(nuevo["banca"]) > len(pb)
            or (len(nuevo["once"]) == len(po) and set(nuevo["once"]) != set(po)))


def cerrar_onces_pendientes(limite: int = 120) -> dict:
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
        # LOS CONFIRMADOS TAMBIÉN: un once de la ficha capturado antes del
        # pitazo puede venir incompleto (Nacional Potosí con 8 titulares y sin
        # banco 25' antes; Sportivo Ameliano con 10 suplentes) y el bloque F
        # quedaba cerrado con bajas que no existieron (18/10/2026).
        filas = [dict(r) for r in con.execute(
            "SELECT fixture_id, equipo_a, equipo_b, xi_json, estado FROM parte_cowork "
            "WHERE veredicto_json IS NULL ORDER BY fecha LIMIT ?", (limite,))]
    cerrados, sin_ficha, nunca, conflictos, reemplazados = [], [], [], [], []
    for f in filas:
        fid = f["fixture_id"]
        fx = _fixture(fid)
        if not fx:
            continue
        ya = json.loads(f["xi_json"]) if f["xi_json"] else {}
        onces = {}
        for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
            previo = ya.get(lado) or {}
            if previo.get("fuente") == FUENTE_FICHA:
                # ya viene de la ficha: solo se rehace si la ficha CRECIÓ
                de_ficha = xi_de_ficha(fid, tid)
                if de_ficha and ficha_crecio(previo, de_ficha):
                    reemplazados.append({"fixtureId": fid, "lado": lado, "fuenteAnterior": FUENTE_FICHA,
                                         "porque": "la ficha se completó después del cierre: "
                                                   f"{len(previo.get('once') or [])}+{len(previo.get('banca') or [])} → "
                                                   f"{len(de_ficha['once'])}+{len(de_ficha['banca'])}"})
                    onces[lado] = de_ficha
                continue
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
        if not onces and f.get("estado") == "confirmado":
            continue   # cerrado y la ficha no cambió: nada que hacer (sin recalcular el parte)
        ya_ficha = [l for l in LADOS if (ya.get(l) or {}).get("fuente") == FUENTE_FICHA]
        if not onces and ya_ficha:
            # LA FICHA YA LLEGÓ: lo que quede abierto no es «esta liga no da
            # onces». Un once de la ficha que no casa con la tabla F1 se
            # quedaba en `pendiente_xi` y la pasada siguiente lo mandaba a
            # `nuncaVaALlegar` (ADT–Cienciano y América–Águilas, 11/10/2026):
            # el conflicto se reporta en cada pasada hasta que se corrija.
            listo = dto(fid)
            malos = [l for l in LADOS if listo["equipos"][l]["disponibilidad"].get("conflicto")]
            if malos:
                conflictos.append({"fixtureId": fid, "partido": partido, "lados": malos,
                                   "porque": listo["equipos"][malos[0]]["disponibilidad"]["conflicto"],
                                   "onceDeLaFicha": True})
                continue
            if len(ya_ficha) == len(LADOS):
                continue  # los dos lados de la ficha y sin conflicto: nada que hacer
        if not onces:
            # «TODAVÍA» ES UNA PROMESA, Y HAY LIGAS DONDE NO SE CUMPLE NUNCA.
            # Un partido TERMINADO sin alineación ingestada no está esperando
            # nada: esa liga no trae onces, y el pantallazo a mano dejó de ser
            # la excepción para ser el procedimiento. Decirlo cambia qué hace
            # el usuario; llamarlo «todavía» lo deja esperando para siempre.
            fila_fx = saddb.query_one(
                "sad", "SELECT status_short, league_id, date FROM fixtures WHERE id=?", (fid,))
            estado_fx = dict(fila_fx) if fila_fx else {}
            faltan = [l for l in LADOS if l not in ya_ficha]
            try:
                meta = saddb.query_one("sad", "SELECT alineaciones FROM fichas_meta WHERE fixture_id=?", (fid,))
            except Exception:  # noqa: BLE001 — base sin la tabla de fichas
                meta = None
            terminado = (estado_fx.get("status_short") or "") in _TERMINADO
            # la ficha post-partido pide los jugados con parte de los últimos
            # días (ficha_partido.CON_PARTE_DIAS); pasado eso no va a llegar
            from backend.ingesta.ficha_partido import CON_PARTE_DIAS
            reciente = str(estado_fx.get("date") or "")[:19].replace("T", " ") >= (
                datetime.now(timezone.utc) - timedelta(days=CON_PARTE_DIAS)).strftime("%Y-%m-%d %H:%M:%S")
            if not reciente:
                meta = meta or {"alineaciones": 0}
            if terminado and ya_ficha and meta is None:
                # MEDIO ONCE NO ES «ESTA LIGA NO DA ONCES». Necaxa–Atlas, ABB–Real
                # Potosí y Atlante–Pumas (17/10/2026): la API trajo el once de un
                # lado y el otro no; la segunda pasada lo mandaba a `nuncaVaALlegar`
                # con «la liga no da onces», que es falso —el otro lado llegó— y
                # la ficha post-partido todavía no lo había vuelto a pedir.
                sin_ficha.append({"fixtureId": fid, "partido": partido, "lados": faltan,
                                  "porque": f"la API trajo solo el once del lado {', '.join(ya_ficha)}; "
                                            "el otro puede llegar con la ficha post-partido "
                                            "(próxima corrida diaria)"})
                continue
            if terminado and ya_ficha:
                nunca.append({
                    "fixtureId": fid, "partido": partido, "ligaId": estado_fx.get("league_id"),
                    "lados": faltan,
                    "porque": f"la API trajo el once del lado {', '.join(ya_ficha)} y el del lado "
                              f"{', '.join(faltan)} no llegó ni con la ficha post-partido: la liga SÍ da "
                              "onces, este partido vino incompleto",
                    "queHacer": f"pegá solo el lado {', '.join(faltan)} a mano (POST /analisis/cowork/{{id}}/xi); "
                                "el lado de la ficha no se toca sin `reemplazar: true`",
                })
                continue
            if terminado and meta is None:
                sin_ficha.append({"fixtureId": fid, "partido": partido,
                                  "porque": "el partido terminó y la ficha post-partido todavía no se pidió "
                                            "(próxima corrida diaria): recién después se sabe si la liga "
                                            "no da onces"})
                continue
            if terminado:
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
            f"""SELECT fixture_id, estado, xi_json, veredicto_json, actualizado_en,
                       json_extract(parte_json, '$.pronostico.probabilidades') AS reparto
                FROM parte_cowork WHERE fixture_id IN ({marcas_sql})""", ids).fetchall()
    # LA CONFIANZA DEL 1X2 EN LA LISTA (25/10/2026, pedido del usuario: ver de
    # un vistazo los partidos con más confianza). El tramo es el de la tabla de
    # Aprendizaje, donde se ve cuánto acierta cada uno.
    from backend.analisis import lecciones as _lec, veredicto as _ver
    salieron = _ver.resultados([f["fixture_id"] for f in filas])
    partes = {}
    for f in filas:
        try:
            reparto = json.loads(f["reparto"]) if f["reparto"] else None
        except (TypeError, ValueError):
            reparto = None
        decl, prob = _ver.declarado_1x2(reparto if isinstance(reparto, dict) else None)
        real = salieron.get(f["fixture_id"])
        partes[str(f["fixture_id"])] = {
            "estado": f["estado"],
            "onceCerrado": bool(f["xi_json"]) and f["estado"] == "confirmado",
            "conVeredicto": bool(f["veredicto_json"]),
            "actualizadoEn": f["actualizado_en"],
            "confianza": ({"declarado": decl, "probabilidad": round(prob, 1),
                           "tramo": _lec.tramo_confianza(prob),
                           "acerto": (real == decl) if real else None} if decl else None),
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
CHAMPIONS = 2
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
    except Exception:  # noqa: BLE001 — sin la ingesta importable (tests aislados): la lista mínima declarada
        return {lid for lid in INTERNACIONALES if lid != 1}


def _nombre_ingesta(liga_id: int) -> str:
    try:
        from backend.ingesta.extractor import LIGAS
        return LIGAS.get(liga_id, "")
    except Exception:  # noqa: BLE001 — sin la ingesta importable: liga sin nombre
        return ""


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
        # LA CHAMPIONS ENTRA SOLA, también en fase liga (pedido del usuario,
        # 14/10/2026: Roma–Real Madrid o Bayern–Arsenal no son relleno). El
        # relleno que motivó la exclusión era la Europa League y la Conference:
        # esas siguen fuera sin grupos=true.
        if liga_id == CHAMPIONS:
            return 4, f"{nombre_i} · {ronda or 'fase liga'} (la Champions entra también en fase liga)"
        if not grupos:
            return 0, (f"{nombre_i} · {ronda or 'fase de grupos'}: la fase de grupos / fase liga "
                       "queda fuera por defecto (de octavos en adelante entra sola); "
                       "pasá grupos=true para incluirla")
        return 5, f"{nombre_i} · {ronda or 'fase de grupos'}"
    # LAS COPAS NACIONALES MEDIDAS (29/10/2026, usuario; REVENTON §16.1): no son
    # del padrón (sin cuotas en vivo) pero entran a la agenda, al final, según
    # cuánto separa el riesgo del reventón en cada una
    from backend.analisis import separacion_liga as _sep
    copa = _sep.copa_en_agenda(liga_id, ronda, padron.get(liga_id) or _nombre_ingesta(liga_id)
                               or liga.get("nombre") or f"copa {liga_id}")
    if copa is not None:
        return copa
    if liga_id not in padron:
        # EL DESCARTE TIENE QUE SER EL MISMO SIEMPRE. Antes el clásico se
        # miraba ANTES del padrón, así que un torneo fuera de él entraba o no
        # según se activara el etiquetador de derbis: la Copa Uruguay entró
        # para un partido y se descartó para otros tres, el mismo día.
        return 0, (f"fuera del padrón: {liga.get('nombre') or 'liga'} (id {liga_id}). "
                   "El padrón son las ligas con cuotas en vivo (primeras divisiones y "
                   "los torneos internacionales; las segundas de Europa salieron el 29/10/2026); las copas "
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
        "matriz": {
            "forma": '{"a": {"ganar": {…}, "empatar": {…}, "perder": {…}}, "b": {…}, '
                     '"confirma": "…", "contradice": "…"}',
            "filas": {k: list(v) for k, v in ESCENARIOS_MATRIZ.items()},
            "nota": "cómo gana, empata y pierde CADA equipo, con sus palancas (Matriz de Escenarios "
                    "v2.0), y la `probabilidad` estimada de cada escenario (0-100) como pide el skill. "
                    "Tiene que cuadrar con `pronostico.probabilidades` (ganar de a = local, empatar = "
                    "empate, perder de a = visita…): si se aparta más de 5 puntos el recibo lo avisa en "
                    "`matrizVsPronostico`. `confirma`/`contradice`: un caso real de cada lado",
        },
        "lecturaSad": {
            "claves": ["moduloOperativo", "unXDos", "contextoEmocional", "datoEstructural", "paradoja", "reventon",
                       "espina"],
            "espina": '{"a": {"lectura": "positiva|cero|negativa|neutra", "guia": "total|condicion", '
                      '"porque": "…"}, "b": {…}}: por '
                      "equipo, adónde va su K después de ESTE partido según la historia de sus burbujas "
                      "(tope, forma de las rachas, cómo se cortaron: `historial.*.termina`): positiva = crece "
                      "o arranca (gana), cero = se reinicia (empata), negativa (pierde), neutra = no dice nada. "
                      "`guia`: qué burbuja leíste — `total`, o `condicion` (familias.local si juega de local, "
                      "familias.visita si es visitante) cuando el equipo es otro en casa que afuera. "
                      "El veredicto la compara con lo que hizo la K y Aprendizaje mide cada guía aparte",
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
            "ip, reducción por zona, ramas A/B, la alerta F3 y la F4 DEL EFE — salen de bloque_f.py "
            "(los indicadores F3 y F4 del TDE son OTROS y SÍ van en tde.bloques[].indicadores)",
            "los nombres del partido — salen de nuestra base",
            "COLAPSO EN CASCADA — la calcula la app desde `equipos.{lado}.d3` (✅ · 🔶 · ❌ · «sin dato»)",
            "ie / ise si mandás `indicadores` — se calculan y se delata la discrepancia",
        ],
        "laAgenda": {
            "conflicto": "cada candidato lo trae: vacío casi siempre. Si un equipo «también "
                         "figura en» otro partido a menos de 24 h, uno de los dos fixtures está "
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


# con menos NS por delante no hay base para gritar: un martes sin fútbol no es
# una ingesta caída
CUOTAS_MIN_PROXIMOS = 10
CUOTAS_HORAS = 48


def cuotas_prepartido(ahora: datetime | None = None, horas: int = CUOTAS_HORAS) -> dict:
    """¿Están entrando las cuotas prepartido? De los NS de las próximas `horas`,
    cuántos tienen alguna captura en `odds_history` y cuándo fue la última.

    LA FASE QUE NO GUARDA NADA TIENE QUE VERSE. Del 18/09 al 11/10/2026 el
    extractor se cayó en la fase de cuotas en cada corrida (deuda 8) y nadie
    lo vio en tres semanas: los fixtures y el en vivo seguían entrando. Se
    pregunta POR FIXTURE contra el índice (fixture_id, captured_at): un MAX
    sobre la tabla entera la recorrería, y eso es la factura de Railway."""
    ahora = ahora or datetime.now(timezone.utc)
    desde = ahora.strftime("%Y-%m-%d %H:%M:%S")
    hasta = (ahora + timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
    out = {"ventanaHoras": horas, "proximos": 0, "conCuota": 0, "ultimaCaptura": None, "alarma": ""}
    try:
        ids = [r["id"] for r in saddb.query(
            "sad", "SELECT id FROM fixtures WHERE status_short='NS' AND date BETWEEN ? AND ?",
            (desde, hasta))]
        ultimas = []
        for fid in ids:
            fila = saddb.query_one(
                "sad", "SELECT MAX(captured_at) AS m FROM odds_history WHERE fixture_id=?", (fid,))
            if fila and fila["m"]:
                ultimas.append(str(fila["m"]))
    except Exception:  # noqa: BLE001 — DB sin la tabla: no hay nada que vigilar
        return out
    out.update(proximos=len(ids), conCuota=len(ultimas),
               ultimaCaptura=(max(ultimas)[:19] if ultimas else None))
    if len(ids) >= CUOTAS_MIN_PROXIMOS and not ultimas:
        out["alarma"] = (f"ninguno de los {len(ids)} partidos de las próximas {horas} h tiene cuota "
                         "prepartido: la fase de cuotas de la ingesta no está guardando (mirá los "
                         "Deploy Logs de la corrida)")
    return out


# el plan diario de API-Football resetea a las 00:00 UTC: agotarlo antes de
# esta hora deja sin cuotas en juego ni alineaciones lo que queda del día
PRESUPUESTO_HORA_SANA = 22
CUOTA_ARCHIVO = ".extractor_cuota.json"


def _resumen_cuota(d: dict) -> dict:
    """Un día del marcador de la ingesta, en el formato del contrato."""
    por = d.get("usadas_por") if isinstance(d.get("usadas_por"), dict) else {}
    por_hora = d.get("usadas_por_hora") if isinstance(d.get("usadas_por_hora"), dict) else {}
    agotado = d.get("agotado_en") or None
    # un día que terminó lejos del tope no se agotó: la marca es la cola de la
    # ventana anterior, que la API todavía cuenta llena en el primer minuto del
    # día UTC (19/10/2026: «agotado a las 19:00» con 4.679 de 7.500)
    limite = d.get("limite_api")
    if agotado and isinstance(limite, int) and limite > 0 and int(d.get("usadas") or 0) < 0.9 * limite:
        agotado = None
    lima = None
    if agotado:
        try:
            t = datetime.strptime(str(agotado)[:19], "%Y-%m-%dT%H:%M:%S") - timedelta(hours=5)
            lima = t.strftime("%H:%M")
        except ValueError:
            pass
    return {
        "dia": d.get("dia"),
        "usadas": int(d.get("usadas") or 0),
        "limite": d.get("limite_api"),
        "porEndpoint": dict(sorted(((str(k), int(v)) for k, v in por.items()), key=lambda kv: -kv[1])),
        "porHora": {k: int(v) for k, v in sorted(por_hora.items())},
        "agotadoEn": agotado,
        "agotadoEnLima": lima,
    }


def presupuesto_api() -> dict:
    """¿Cuánto del plan de API-Football se gastó, en qué y a qué hora se acabó?

    Lo lee del marcador que comparten todas las corridas de la ingesta (0
    requests). El 11/10/2026 el plan se agotó a las 12:40 de Lima y la tarde
    sudamericana —Liga 1 incluida— se quedó sin cuotas en juego: nadie lo vio
    hasta revisar partido por partido. `alarma` sale cuando hoy o ayer el plan
    tocó el tope antes de las PRESUPUESTO_HORA_SANA UTC."""
    out = {"hoy": None, "ayer": None, "alarma": ""}
    try:
        with open(os.path.join(saddb.BASE_DIR, CUOTA_ARCHIVO), encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return out
    if not isinstance(d, dict):
        return out
    out["hoy"] = _resumen_cuota(d)
    if isinstance(d.get("anterior"), dict) and d["anterior"].get("dia"):
        out["ayer"] = _resumen_cuota(d["anterior"])
    for cual, r in (("hoy", out["hoy"]), ("ayer", out["ayer"])):
        if not r or not r["agotadoEn"]:
            continue
        try:
            hora = int(str(r["agotadoEn"])[11:13])
        except ValueError:
            continue
        if hora < PRESUPUESTO_HORA_SANA:
            top = ", ".join(f"{k} {v}" for k, v in list(r["porEndpoint"].items())[:3])
            out["alarma"] = (f"el plan de API-Football se agotó {cual} ({r['dia']}) a las "
                             f"{r['agotadoEnLima']} de Lima: desde ahí no entraron cuotas en juego "
                             f"ni alineaciones hasta el reset (19:00 Lima). Se lo comieron: {top}")
            break
    return out


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
    # COBERTURA: de TODOS los candidatos del padrón de ayer (no solo los que
    # entraban en el cupo de una corrida), ¿cuántos tienen parte? Es la señal
    # que delata que el batch no corrió o no alcanzó, y no se puede deducir
    # mirando solo los partes: hay que comparar contra lo que TOCABA. La meta es
    # COBERTURA_META (80 %, usuario 17/10/2026): un fin de semana trae 50-65
    # candidatos y el cupo de 8 dejaba fuera 47 sin que nada se pusiera ámbar.
    ayer = agenda(fecha=(ahora - timedelta(days=1)).date(), limite=500)
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

    cuotas = cuotas_prepartido(ahora)
    presupuesto = presupuesto_api()

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
    cobertura = round(len(con_parte) / len(tocaban), 3) if tocaban else None
    if cobertura is not None and cobertura < COBERTURA_META:
        motivos.append(f"cobertura de ayer {round(cobertura * 100)} % ({len(con_parte)} de {len(tocaban)} "
                       f"partidos del padrón), por debajo de la meta del {round(COBERTURA_META * 100)} %")
    if vencidos:
        motivos.append(f"{len(vencidos)} caso(s) llevan más de 12 h terminados y sin veredicto")
    if cuotas["alarma"]:
        motivos.append(cuotas["alarma"])
    if presupuesto["alarma"]:
        motivos.append(presupuesto["alarma"])
    # LO QUE LAS CORRIDAS VIERON ROTO Y NADIE ARREGLÓ (incidencias, 18/10/2026)
    try:
        from backend.analisis import incidencias as _inc
        inc = _inc.resumen_latido()
    except Exception:  # noqa: BLE001 — la vigilancia no tumba el latido
        inc = None
    if inc and inc["bloquean"]:
        motivos.append(f"{inc['bloquean']} incidencia(s) que bloquean sin resolver "
                       "(GET /analisis/cowork/incidencias)")
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
                            "porcentaje": cobertura, "meta": COBERTURA_META,
                            "faltaron": [{"fixtureId": x["fixtureId"], "partido": x.get("partido", ""),
                                          "porque": x.get("motivo", "")} for x in faltaron[:25]],
                            "faltaronTotal": len(faltaron)},
        "sinCerrar": sin_cerrar,
        "veredictosVencidos": [{"fixtureId": v["fixtureId"], "partido": v["partido"],
                                "marcador": v["marcador"]} for v in vencidos],
        "sinOnceCerrado": sin_xi,
        "cuotasPrepartido": cuotas,
        "presupuestoApi": presupuesto,
        "incidencias": inc,
        "nota": "esto solo mira; no dispara nada. El silencio cuenta como fallo: "
                "cero partes en la ventana es ROJO, no «sin novedad».",
    }


# un equipo no juega dos partidos oficiales con menos de esto de diferencia:
# si figura en dos, uno de los fixtures es un aplazado sin marcar o un duplicado
from backend.jugadores import HORAS_CHOQUE  # noqa: E402 — la misma regla del calendario y los próximos


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


def agenda(fecha: date_t | None = None, limite: int = AGENDA_LIMITE, liga_id: int | None = None,
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
    liga_pedida = (liga or "").strip()   # `liga` se reusa abajo como la liga de cada fila
    liga_txt = normalizar(liga or "").strip()
    ligas_que_casan: set[int] = set()
    if liga_txt:
        # el texto casa contra el nombre de la ingesta («España - La Liga») y el de
        # la tabla leagues con su país: «España», «LaLiga» y «Spain» encuentran lo mismo
        from backend.analisis.separacion_liga import COPAS_MEDIDAS
        for lid, nombre in {**_padron(), **{c: _nombre_ingesta(c) or "" for c in COPAS_MEDIDAS}}.items():
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
            # la tabla del torneo corto en curso si ya anda (incidencia 441), si no la del año
            posiciones = (cal.posiciones_y_tabla(f["league_id"], f["league_season"], cal._hora(), f["league_round"])[0]
                          if f["league_season"] else {})
        except Exception:  # noqa: BLE001 — una liga sin tabla de posiciones no corta la agenda: sin posiciones
            posiciones = {}
        etiquetas = set()
        try:
            ciudad = cal._ciudad(f["home_team_id"])
            for e in cal.etiquetas_de_rival(f["away_team_id"], False, f["league_id"],
                                            f["league_season"], (f["date"] or "")[:10], ciudad,
                                            equipo_id=f["home_team_id"]):
                etiquetas.add(e["codigo"])
        except Exception:  # noqa: BLE001 — un etiquetador que falla no corta la agenda: el partido va sin etiquetas
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
            "fecha": (f["date"] or "")[:10],
            "partido": f"{f['home_name']} vs {f['away_name']}",
            "equipoA": f["home_name"], "equipoB": f["away_name"],
            # EL DT DE LA BASE VIAJA CON SU EDAD Y SU PROCEDENCIA. Es una
            # alarma, no la verdad: si la prensa de la semana dice otro, manda
            # la prensa y este registro se refresca solo en la próxima corrida
            "dt": _dt_con_expulsion(f["id"], {"a": dt_de_base(f["home_team_id"]),
                                              "b": dt_de_base(f["away_team_id"])}),
            "liga": liga.get("nombre"), "pais": liga.get("pais"),
            "ronda": f["league_round"] or "",
            "prioridad": prio, "motivo": motivo,
            "etiquetas": sorted(etiquetas),
            # las etiquetas se calculan sobre el VISITANTE como rival del local:
            # EQUIPO_SORPRESA, EN_CRISIS… son de ese lado (incidencia 41)
            "etiquetasDe": "b",
            # …con el NOMBRE: «b» solo se leía al revés (incidencia 427, Atlante–
            # San Luis: el EQUIPO_SORPRESA es San Luis, no Atlante)
            "etiquetasEquipo": f["away_name"],
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
                f"SELECT fixture_id, fecha, estado, xi_json, veredicto_json FROM parte_cowork "
                f"WHERE fixture_id IN ({','.join('?' * len(todos_ids))})", tuple(todos_ids)):
                fecha_fx = next((x["fecha"] for x in candidatos + descartados if x["fixtureId"] == r["fixture_id"]), "")
                movido = None if r["veredicto_json"] else dias_movido(r["fecha"], fecha_fx)
                estados[r["fixture_id"]] = {
                    # un parte escrito para otra fecha vuelve a la lista de trabajo
                    "tieneParte": movido is None,
                    "rehacer": (f"el parte es del partido del {r['fecha']} y se juega el {fecha_fx} "
                                f"({movido:+d} días): rehacerlo entero") if movido is not None else "",
                    "onceCerrado": bool(r["xi_json"]) and r["estado"] == "confirmado",
                    "conVeredicto": bool(r["veredicto_json"]),
                }
    for x in candidatos + descartados:
        x.update(estados.get(x["fixtureId"],
                             {"tieneParte": False, "onceCerrado": False, "conVeredicto": False}))
    # EL CUPO ES DE TRABAJO, NO DE LISTA. El límite existe por los tokens, y un
    # partido que ya tiene parte no cuesta nada. Antes los `yaHechos` ocupaban
    # cupo: en el tramo de la tarde del 17/10/2026 Platense–Lanús y Botafogo–
    # Chapecoense entraron recién cuando otros arrancaron y se liberó lugar, a
    # menos de una hora del pitazo, y quedaron sin parte (y dos más ni entraron).
    # Ahora el límite cuenta solo los que faltan; los hechos van aparte.
    sin_parte = [x for x in candidatos if not x["tieneParte"]]
    faltan = sin_parte[:limite]
    entran = {x["fixtureId"] for x in faltan} | {x["fixtureId"] for x in candidatos if x["tieneParte"]}
    cola = [x for x in candidatos if x["fixtureId"] not in entran]
    candidatos = [x for x in candidatos if x["fixtureId"] in entran] + cola
    limite_pedido, limite = limite, len(candidatos) - len(cola)
    return {
        "porHacer": [x["fixtureId"] for x in faltan],
        "aRehacer": {x["fixtureId"]: x["rehacer"] for x in candidatos if x.get("rehacer")},
        "yaHechos": [x["fixtureId"] for x in candidatos[:limite] if x["tieneParte"]],
        "notaReanudacion": (
            f"{len(faltan)} de {len(candidatos[:limite])} sin parte. `porHacer` es la lista "
            "de trabajo: si la corrida se cortó, arrancá por ahí. Re-depositar un parte que "
            "ya estaba REEMPLAZA el anterior, así que no vuelvas sobre `yaHechos` salvo que "
            "quieras rehacerlos."),
        "fecha": dia.isoformat(),
        "ventana": ventana,
        "filtro": {"ligaId": liga_id, "liga": liga_pedida or None,
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
            "limite": limite_pedido,
            "cuenta": "solo los que no tienen parte: los ya hechos no ocupan cupo",
            "candidatos": len(candidatos),
            "seAnalizan": len(candidatos[:limite]),
            "quedanFuera": len(candidatos[limite:]),
            "porPrioridad": {str(pr): sum(1 for x in candidatos if x["prioridad"] == pr)
                             for pr in sorted({x["prioridad"] for x in candidatos})},
            "ligasQueQuedanFuera": sorted({x["liga"] for x in candidatos[limite:] if x.get("liga")}),
            "nota": ("todos los candidatos entran" if len(candidatos) <= limite else
                     f"{len(candidatos) - limite} candidatos quedan fuera SOLO por el "
                     f"límite de {limite_pedido} sin parte: subilo si querés cubrirlos"),
        },
        "descartados": descartados,
        "nota": "CLÁSICO solo se detecta por derbi de ciudad (y en una ciudad con 4 o más clubes "
                "de la liga, solo los clásicos documentados): una rivalidad nacional sin vecindad "
                "geográfica no sale de nuestros datos y puede estar entre los descartados",
        "notaSeleccion": (
            "Filtro manual puesto: elegir una liga o una ventana ANTES del pitazo es "
            "selección ex ante y el caso sigue siendo `ciega` al escribir el veredicto. "
            "Lo que contamina es elegir un partido PORQUE pasó algo en él."
            if manual else
            "Selección estándar por el padrón de prioridades: casos `ciega`."
        ),
    }


# ── la comprobación barata de la rutina de rehacer ───────────────────────────
# Pedido del usuario (22/10/2026): la rutina de rehacer dispara cada 30 minutos
# y casi siempre no hay nada; cada disparo vacío costaba ~0,25 USD porque el
# agente leía la agenda y después cada parte. Esto contesta en UNA llamada qué
# partes tienen DTP-REHACER y arrancan dentro de la ventana; vacío = terminar.
# Piso en 15 (24/10/2026, incidencias 444, 451 y 454): la API publica el once
# ~27 min antes y con piso en 30 esos partidos nunca entraban. Piso en 5 desde el
# 31/10/2026 (636, con disparos cada 20 min): el depósito se topa en el pitazo − 5
# (skill corrida-sad).
REHACER_DESDE_MIN, REHACER_HASTA_MIN = 5, 80


REHACER_DIAS_ATRAS = 30   # un parte reprogramado puede tener semanas


def rehacer_pendientes(desde_min: int = REHACER_DESDE_MIN, hasta_min: int = REHACER_HASTA_MIN,
                       ahora: datetime | None = None) -> dict:
    from backend.app import iso
    ahora = ahora or datetime.now(timezone.utc)
    lo, hi = ahora + timedelta(minutes=desde_min), ahora + timedelta(minutes=hasta_min)
    # POR LA FECHA DEL PARTIDO, NO LA DEL PARTE (incidencia 395, Santa Fe–
    # Jaguares: escrito el 14/10, jugado el 22/10 tras dos reprogramaciones, y
    # nunca entraba en la ventana porque se buscaba por la fecha del parte).
    # Se miran los partes sin veredicto de los últimos días; el pitazo decide.
    desde = (lo - timedelta(days=REHACER_DIAS_ATRAS)).strftime("%Y-%m-%d")
    with _conectar() as con:
        filas = [dict(r) for r in con.execute(
            "SELECT fixture_id, equipo_a, equipo_b, fecha FROM parte_cowork WHERE veredicto_json IS NULL "
            "AND fecha >= ? AND fecha <= ?", (desde, hi.strftime("%Y-%m-%d")))]
    en_ventana, pendientes = [], []
    for f in filas:
        fx = saddb.query_one("sad", "SELECT date, status_short FROM fixtures WHERE id=?", (f["fixture_id"],))
        if not fx or (fx["status_short"] or "NS") not in ("NS", "TBD"):
            continue
        try:
            pitazo = datetime.fromisoformat(iso(fx["date"]).replace("Z", "+00:00"))
        except ValueError:
            continue
        if not (lo <= pitazo <= hi):
            continue
        item = {"fixtureId": f["fixture_id"], "partido": f"{f['equipo_a']} vs {f['equipo_b']}",
                "pitazo": pitazo.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "minutosAlPitazo": int((pitazo - ahora).total_seconds() // 60)}
        en_ventana.append(item)
        d = dto(f["fixture_id"]) or {}
        # el DT del banco contra el del parte también se corrige antes del pitazo (711)
        rehacer = [a for a in d.get("alertas") or [] if a.get("codigo") in ("DTP-REHACER", "DT-VS-BANCO")]
        movido = dias_movido(f["fecha"], fx["date"])
        if movido:
            # se escribió con otra semana de datos: se rehace ENTERO, no solo el DTP
            rehacer.append({"codigo": "PARTE-OTRA-FECHA", "tipo": "dato",
                            "detalle": f"el parte es del partido del {str(f['fecha'])[:10]} y se juega el "
                                       f"{pitazo.strftime('%Y-%m-%d')} ({movido:+d} días): rehacer el parte entero "
                                       "con la semana nueva (si no, cae en cuarentena al cerrar el veredicto)"})
        if rehacer:
            pendientes.append({**item, "alertas": rehacer})
    return {"ahora": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "ventanaMin": [desde_min, hasta_min],
            "partesEnVentana": len(en_ventana), "enVentana": en_ventana, "pendientes": pendientes,
            "nota": "pendientes vacío = no hay nada que rehacer: la corrida termina en una línea y sin aviso"}
