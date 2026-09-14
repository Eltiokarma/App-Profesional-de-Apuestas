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


def _jugador(j: dict, rechazos: list, donde: str) -> dict | None:
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


def _bloque_crudo(v):
    """El sub-score puede venir plano (`"A": 3`) o como objeto
    (`"A": {"score": 3, "nota": "…"}`). Las dos formas son razonables si vienes
    de leer la rúbrica; antes la segunda se convertía en 0 sin avisar."""
    if isinstance(v, dict):
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
              "timeline", "rechazos", "perdido", "aviso", "entrada"}
_ECO_EQUIPO = {"total", "maximoAlcanzable", "porcentaje", "clasificacion", "disponibilidad"}
_ECO_JUGADOR = {"soloBaja"}
_CLAVES_VEREDICTO = {"seleccion", "modoEvaluacion", "mancha", "falsadorCumplido",
                     "porLado", "notas", "fixtureId"}


def _equipo(bruto: dict, equipos_db: list[tuple[str, str]],
            rechazos: list, lado: str) -> dict:
    _claves_raras(bruto, _CLAVES_EQUIPO | _ECO_EQUIPO, rechazos, f"equipos.{lado}")
    bloques_in = bruto.get("bloques") or {}
    excluidos_in = bruto.get("excluidos") or {}
    notas_in = bruto.get("notas") or {}
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
            "nota": _txt(notas_in.get(letra)) or nota_obj,
        }
    plantel = [j for j in (_jugador(x, rechazos, f"equipos.{lado}.plantel[{i}]")
                           for i, x in enumerate(bruto.get("plantel") or [])) if j]
    fuera = [f for f in (_fuera(x, rechazos, f"equipos.{lado}.fuera[{i}]")
                         for i, x in enumerate(bruto.get("fuera") or [])) if f]
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
    ind = x.get("indicadores") if isinstance(x.get("indicadores"), dict) else {}
    tiene = any([_txt(x.get("tipologia")), vias, ind,
                 x.get("ie") is not None, x.get("ise") is not None])
    if not tiene:
        return {}
    equipo = _txt(x.get("equipo")).lower()
    return {
        # LOS INDICADORES MANDAN SOBRE EL ÍNDICE. Si llegan los 0/0.5/1, el IE y
        # el ISE los calcula el backend con sus compuertas: la cuenta se puede
        # equivocar y las compuertas se pueden olvidar, y las dos cosas pasaron
        # en el registro. El `ie` suelto se conserva solo como lo que llegó.
        "indicadores": {k: _num(v, 1) for k, v in ind.items() if v is not None},
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


_CLAVES_ALERTA = {"codigo", "equipo", "tipo", "detalle", "texto"}
# el protocolo usa `ambos` para una alerta que toca a los dos equipos: estaba
# en el esquema del EFE viejo y se perdió al escribir este contrato
_EQUIPOS_ALERTA = ("a", "b", "ambos", "global")


def _alerta(a: dict, rechazos: list, donde: str) -> dict | None:
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
    parte = {
        "fixtureId": fixture_id,
        "version": _txt(payload.get("version")) or VERSION,
        "generadoEn": _txt(payload.get("generadoEn")),
        "equipos": {l: _equipo(equipos_in.get(l) or {}, equipos_db, rechazos, l) for l in LADOS},
        "alertas": [a for a in (_alerta(x, rechazos, f"alertas[{i}]")
                                for i, x in enumerate(payload.get("alertas") or [])) if a],
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
        "rechazos": rechazos,
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
        previo = con.execute("SELECT creado_en, xi_json, parte_json FROM parte_cowork WHERE fixture_id=?",
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
            return {
                "alertas": len(p_.get("alertas") or []),
                "documentos": len(p_.get("documentos") or []),
                "fuentes": len(p_.get("fuentes") or []),
                "jugadores": sum(len((p_.get("equipos", {}).get(l) or {}).get("plantel") or []) for l in LADOS),
                "bajas": sum(len((p_.get("equipos", {}).get(l) or {}).get("fuera") or []) for l in LADOS),
                "eventosTimeline": len(p_.get("timelineEventos") or []),
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
    if not parte.get("tde"):
        faltan.append({
            "bloque": "tde",
            "costara": "el veredicto no va a poder comprobar la ventana del TDE "
                       "(`objetivo.tde` viene vacío)",
            "comoSeArregla": "mandá el bloque `tde` con su ventana de 15 minutos",
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
        "conTde": bool(parte.get("tde")),
        # lo que falta y se va a cobrar al cerrar el caso, mientras todavía se
        # puede llenar sin mirar el resultado
        "faltan": faltan,
        # lo que NO entró, con el motivo y dónde estaba
        "rechazos": parte.get("rechazos") or [],
        # lo que este depósito BORRÓ de lo que ya había guardado
        "perdido": perdido,
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


def _tde_calculado(tde: dict) -> dict:
    """El TDE con su índice CALCULADO cuando llegaron los indicadores.

    Igual que el bloque F y que los totales del EFE: si el dato de entrada está,
    el número lo pone la aritmética. Lo que llegó escrito se conserva al lado en
    `declarado`, y si no coincide se dice — un IE mal sumado que nadie compara
    es una banda de probabilidad equivocada durante meses.
    """
    if not tde:
        return {}
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
        "tde": _tde_calculado(parte.get("tde") or {}),
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

    cumplido = payload.get("falsadorCumplido")
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
    _claves_raras(payload, _CLAVES_VEREDICTO, rechazos, "(veredicto)")
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
            "SELECT parte_json, veredicto_json FROM parte_cowork WHERE fixture_id=?",
            (fixture_id,)).fetchone()
    if not fila or not fila["veredicto_json"]:
        return None
    parte = json.loads(fila["parte_json"])
    guardado = json.loads(fila["veredicto_json"])
    return {**guardado, "fixtureId": fixture_id,
            # los veredictos cerrados antes de que existiera el campo no tienen
            # salvedad: vacía, no ausente, para que la pantalla no adivine
            "mancha": guardado.get("mancha", ""),
            "rechazos": guardado.get("rechazos", []),
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
        "criterio": f"partes sin veredicto cuyo partido arrancó hace más de {horas} h "
                    f"y ya tiene marcador en nuestra base (subir `horas` estrecha)",
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
        if m["date"] > marca:
            fuera(f"arrancó hace menos de {horas} h: todavía no entra en la ventana",
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
    cerrados, sin_ficha, conflictos = [], [], []
    for f in filas:
        fid = f["fixture_id"]
        fx = _fixture(fid)
        if not fx:
            continue
        ya = json.loads(f["xi_json"]) if f["xi_json"] else {}
        onces = {}
        for lado, tid in (("a", fx["home_team_id"]), ("b", fx["away_team_id"])):
            if ya.get(lado):
                continue  # ese lado ya estaba cerrado: no se pisa
            de_ficha = xi_de_ficha(fid, tid)
            if de_ficha:
                onces[lado] = de_ficha
        partido = f"{f['equipo_a']} vs {f['equipo_b']}"
        if not onces:
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
        "conConflicto": conflictos,
        "sinFichaTodavia": sin_ficha,
        "nota": "esto no gasta tokens ni llama a ningún modelo: cruza el once ingestado "
                "con la tabla F1 y aplica los pesos de rol. Los que salen en "
                "`sinFichaTodavia` son los que necesitan el pantallazo a mano.",
    }


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


def agenda(fecha: date_t | None = None, limite: int = 4, liga_id: int | None = None,
           desde_ahora: bool = False, horas: int = 12,
           incluir_descartados: bool = False) -> dict:
    """Los partidos del día ordenados por prioridad — calculado, no preguntado.

    Es el paso 1 del batch: en vez de hacerle deducir a Cowork qué partido
    importa (y pagar esa deducción en tiempo y en búsquedas), la base lo
    resuelve con el criterio numérico del protocolo. Los descartados viajan
    CON su motivo: un descarte sin motivo no se puede auditar.

    Los tres mandos manuales son para apuntar el batch a mano —probar una liga
    concreta, o cubrir lo que queda de esta noche— sin tener que tocar el
    padrón de prioridades:

      liga_id             solo esa liga
      desde_ahora + horas ventana rodante desde AHORA (no el día natural: a las
                          20:00 de Lima el día UTC ya cambió, y un filtro por
                          fecha se comería justo los partidos de la noche)
      incluir_descartados los de prioridad 0 entran al final, con su motivo

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
    else:
        dia = fecha or (datetime.now(timezone.utc) + timedelta(days=1)).date()
        desde, hasta = dia.isoformat(), (dia + timedelta(days=1)).isoformat()
        ventana = f"día completo {dia.isoformat()} (UTC)"
    cond, params = ["f.date >= ?", "f.date < ?"], [desde, hasta]
    if liga_id is not None:
        cond.append("f.league_id = ?")
        params.append(liga_id)
    filas = saddb.query(
        "sad",
        "SELECT f.id, f.date, f.league_id, f.league_season, f.home_team_id, f.away_team_id, "
        "ht.name AS home_name, at.name AS away_name "
        "FROM fixtures f JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id "
        "WHERE " + " AND ".join(cond) + " ORDER BY f.date",
        tuple(params),
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
    # con el mando manual puesto, los de prioridad 0 entran al final y CON su
    # motivo: se ve que no habrían entrado por sí solos
    if incluir_descartados:
        candidatos += sorted(descartados, key=lambda i: i["hora"])
        descartados = []
    manual = bool(liga_id is not None or desde_ahora or incluir_descartados)
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
        "filtro": {"ligaId": liga_id, "desdeAhora": desde_ahora,
                   "horas": horas if desde_ahora else None,
                   "incluirDescartados": incluir_descartados, "manual": manual},
        "analizar": candidatos[:limite],
        "enEspera": candidatos[limite:],
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
