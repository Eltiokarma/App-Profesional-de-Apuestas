"""Bloque F calculado AQUÍ — la aritmética del protocolo, sin modelo.

El protocolo EFE v1.5 define el bloque F con fórmulas cerradas: pesos por rol
(🔴×3 🟠×2 🟡×1 ⚪×0.5), factor por estado (baja 1.0 · duda 0.5), multiplicador
×1.5 del arquero titular fijo, reducción por zona y los umbrales de IP. Nada de
eso es un juicio: es una suma. Por eso lo hace este módulo y no un modelo.

Lo que Cowork manda es la parte que SÍ cuesta trabajo — quién es titular fijo,
en qué zona juega, cuántas titularidades lleva — y esa tabla se escribe UNA vez
la noche anterior. Cuando después aparece el once (de la ficha de API-Football
o de un pantallazo que el usuario le pasa a Cowork), este módulo lo cruza con
la tabla y cierra el bloque en milisegundos y a costo cero.

Regla de la casa: un nombre que no se puede resolver sin adivinar NO se
resuelve. Va a `dudas` y el jugador queda como estaba. Preferimos un hueco
declarado a un IP cómodo.
"""
import re

from backend.nombres import normalizar

# F1 · pesos por rol (tabla "Clasificación de Rol" del protocolo)
PESOS_ROL = {"TF": 3.0, "TH": 2.0, "ROT": 1.0, "SUP": 0.5}
# F2a · factor por estado
FACTOR_ESTADO = {"baja": 1.0, "duda": 0.5, "disponible": 0.0}
# F2c · monopolio del arquero: el titular fijo ausente pesa ×1.5
MULT_GK = 1.5
ZONAS = ("GK", "DEF", "MID", "ATK")
ROLES = tuple(PESOS_ROL)
ESTADOS = tuple(FACTOR_ESTADO)

# partículas que no distinguen a nadie: "de la Cruz" y "Cruz" son el mismo
_PARTICULAS = {"de", "del", "la", "las", "lo", "los", "da", "das", "do", "dos",
               "van", "von", "di", "el", "al", "san", "santa", "mc", "jr"}


def nivel_ip(ip: float) -> str:
    """F2a: 🟢 IP ≤ 3 · 🟡 3.5–7 · 🔴 > 7."""
    return "verde" if ip <= 3 else ("ambar" if ip <= 7 else "rojo")


def nivel_zona(pct: float) -> str:
    """F2b: 🟢 < 20% · 🟡 20–40% · 🔴 > 40%."""
    return "verde" if pct < 20 else ("ambar" if pct <= 40 else "rojo")


def _peso(j: dict) -> float:
    return PESOS_ROL.get((j.get("rol") or "").upper(), 0.0)


def _es_gk_titular(j: dict) -> bool:
    return (j.get("zona") or "").upper() == "GK" and (j.get("rol") or "").upper() == "TF"


def _impacto(j: dict) -> float:
    """Peso efectivo del jugador en el IP, con el multiplicador del arquero."""
    factor = FACTOR_ESTADO.get((j.get("estado") or "disponible").lower(), 0.0)
    if not factor:
        return 0.0
    base = _peso(j) * factor
    return base * MULT_GK if _es_gk_titular(j) else base


def evaluar(plantel: list[dict]) -> dict:
    """F2 completo sobre una tabla de plantel ya con `estado` en cada jugador.

    Devuelve el diagnóstico entero (IP, nivel, reducción por zona con su nivel,
    si se aplicó el ×1.5 del arquero y quién está fuera)."""
    ip = round(sum(_impacto(j) for j in plantel), 2)
    reduccion, niveles = {}, {}
    for z in ZONAS:
        de_la_zona = [j for j in plantel if (j.get("zona") or "").upper() == z]
        # el denominador es el poder de la zona SIN multiplicadores: el ×1.5 del
        # arquero corrige el IP global, no el tamaño de su propia línea (si no,
        # un GK de baja daría una reducción menor al 100% de una zona de uno)
        total = sum(_peso(j) for j in de_la_zona)
        perdido = sum(_peso(j) * FACTOR_ESTADO.get((j.get("estado") or "disponible").lower(), 0.0)
                      for j in de_la_zona)
        pct = round((perdido / total) * 100, 1) if total else 0.0
        reduccion[z] = pct
        niveles[z] = nivel_zona(pct)
    fuera = [{"nombre": j.get("nombre", ""), "zona": (j.get("zona") or "").upper(),
              "rol": (j.get("rol") or "").upper(), "estado": j.get("estado"),
              "motivo": j.get("motivo", ""), "impacto": round(_impacto(j), 2)}
             for j in plantel if _impacto(j) > 0]
    fuera.sort(key=lambda f: -f["impacto"])
    return {
        "ip": ip,
        "ipNivel": nivel_ip(ip),
        "reduccion": reduccion,
        "reduccionNivel": niveles,
        "multiplicadorGk": any(_es_gk_titular(j) and _impacto(j) > 0 for j in plantel),
        "fuera": fuera,
        # F2 nota cualitativa: el protocolo permite que la concentración anule
        # al criterio cuantitativo, así que la zona crítica se declara aparte
        "zonasCriticas": [z for z in ZONAS if niveles[z] == "rojo"],
    }


def _con_estados(plantel: list[dict], bajas: dict[str, tuple[str, str]]) -> list[dict]:
    """Copia del plantel con `estado`/`motivo` puestos por clave normalizada."""
    out = []
    for j in plantel:
        clave = normalizar(j.get("nombre", ""))
        estado, motivo = bajas.get(clave, ("disponible", ""))
        out.append({**j, "estado": estado, "motivo": motivo})
    return out


def ramas(plantel: list[dict], fuera: list[dict]) -> dict:
    """Las dos ramas pre-calculadas mientras el once no aparece.

    Rama A — juegan todos los disponibles conocidos: solo pesan las ausencias
    ya públicas (lesión larga, sanción, selección). Es el piso del IP.
    Rama B — además falta el 🔴 más pesado que hoy figura disponible. Es el
    techo razonable: el golpe de una ausencia de última hora.

    No es una predicción: son los dos bordes entre los que va a caer el número
    real, para que el partido se pueda leer esta noche sin el once.
    """
    bajas = {normalizar(f.get("nombre", "")):
             ((f.get("estado") or "baja").lower(), f.get("motivo", "")) for f in fuera}
    a = _con_estados(plantel, bajas)
    eval_a = evaluar(a)

    # el 🔴 más pesado que todavía cuenta como disponible (el arquero titular
    # pesa 4.5 por el ×1.5, así que suele ser él: es exactamente el punto)
    candidatos = [j for j in a if j["estado"] == "disponible" and (j.get("rol") or "").upper() == "TF"]
    peor = max(candidatos, key=lambda j: _peso(j) * (MULT_GK if _es_gk_titular(j) else 1),
               default=None)
    if peor is None:
        eval_b, nombre_b = eval_a, ""
    else:
        b = [{**j, "estado": "baja", "motivo": "rama B (hipótesis)"} if j is peor else j for j in a]
        eval_b, nombre_b = evaluar(b), peor.get("nombre", "")
    return {
        "a": {**eval_a, "supuesto": "juegan todos los disponibles conocidos"},
        "b": {**eval_b, "supuesto": f"además falta {nombre_b}" if nombre_b else
              "sin titular fijo disponible que quitar: igual que la rama A",
              "ausenteHipotetico": nombre_b},
    }


# ── cruce con el once ───────────────────────────────────────────────────────

def _tokens(nombre: str) -> list[str]:
    """Palabras útiles del nombre: sin tildes, sin puntos ("A." → "a") y sin
    partículas. El punto importa: la ficha de API-Football abrevia el nombre
    de pila y sin quitarlo "a." nunca casaría con "ángelo"."""
    # el apóstrofo une, no separa: «N'Diaye» y «Ndiaye» son la misma palabra
    # (Le Havre, incidencia 653: el suplente salía baja con id negativo)
    limpio = re.sub(r"[^a-z0-9ñ ]+", " ", re.sub(r"['’`´]", "", normalizar(nombre)))
    return [t for t in limpio.split() if t and t not in _PARTICULAS]


def _misma_pila(uno: str, otro: str) -> bool:
    """Nombre de pila igual, o uno es la inicial del otro ("a" ↔ "ángelo").

    Nada más: "jose" y "joselu" son personas distintas y un prefijo suelto los
    confundiría."""
    if uno == otro:
        return True
    # una letra doble de más o de menos es el mismo nombre: «Emmanuel» y
    # «Emanuel» Benítez (Nacional, incidencia 449: salía baja habiendo entrado)
    if len(uno) > 3 and len(otro) > 3 and re.sub(r"(.)\1", r"\1", uno) == re.sub(r"(.)\1", r"\1", otro):
        return True
    if len(uno) == 1:
        return otro.startswith(uno)
    if len(otro) == 1:
        return uno.startswith(otro)
    return False


def _casa(tokens_plantel: list[str], tokens_hoja: list[str]) -> bool:
    """¿La hoja nombra a este jugador?

    API-Football escribe "A. Campos"; Cowork escribe "Ángelo Campos"; un
    pantallazo puede traer solo "Campos". El apellido es obligatorio —por el
    nombre de pila solo no se identifica a nadie— y la pila, si la hoja la
    trae, tiene que cuadrar.
    """
    if not tokens_plantel or not tokens_hoja:
        return False
    apellidos = set(tokens_plantel[1:]) or set(tokens_plantel)
    if not set(tokens_hoja) & apellidos:
        # LA HOJA A VECES TRAE SOLO EL NOMBRE DE PILA: API-Football escribe
        # «Saúl», «Breno», «Andre» (Flamengo, Corinthians 11/10/2026) y la tabla
        # dice «Saúl Ñíguez», «Breno Bidon». Un solo token que es la pila del
        # jugador casa; si dos jugadores comparten esa pila, `resolver` lo manda
        # a dudas en vez de adivinar.
        return len(tokens_hoja) == 1 and len(tokens_plantel) > 1 and tokens_hoja[0] == tokens_plantel[0]
    pila_plantel = tokens_plantel[0] if len(tokens_plantel) > 1 else ""
    pila_hoja = [t for t in tokens_hoja if t not in apellidos]
    if not pila_hoja or not pila_plantel:
        return True
    # «PH Ganso» = Paulo Henrique Ganso: la pila en iniciales pegadas
    iniciales = "".join(t[0] for t in tokens_plantel[:-1])
    return any(_misma_pila(t, pila_plantel) or (1 < len(t) <= 3 and t == iniciales[:len(t)])
               for t in pila_hoja)


def _solo_pila(tokens_plantel: list[str], tokens_hoja: list[str]) -> bool:
    """¿La hoja casa con este jugador solo por el nombre de pila (sin apellido)?"""
    apellidos = set(tokens_plantel[1:]) or set(tokens_plantel)
    return not set(tokens_hoja) & apellidos


def _una_letra(t: str, apellidos: set) -> str | None:
    """El apellido de la tabla que difiere de `t` en UNA letra (5+ letras,
    mismo largo): «Zampiero» por «Zampieri» (Torque, 21/10/2026, incidencia
    223). Es la misma tolerancia de `dtp_cowork._casi`."""
    for a in apellidos:
        if len(a) >= 5 and len(a) == len(t) and sum(x != y for x, y in zip(a, t)) == 1:
            return a
    return None


def _buscar(plantel: list[dict], nombre_hoja: str) -> list[int]:
    th = _tokens(nombre_hoja)
    exactos = [i for i, j in enumerate(plantel) if _casa(_tokens(j.get("nombre", "")), th)]
    if exactos:
        return exactos
    # sin ninguno exacto, una letra cambiada en el apellido (la API y la base
    # escriben distinto al mismo jugador); con dos candidatos va a dudas
    out = []
    for i, j in enumerate(plantel):
        tp = _tokens(j.get("nombre", ""))
        apellidos = set(tp[1:]) or set(tp)
        th2 = [_una_letra(t, apellidos) or t for t in th]
        if th2 != th and _casa(tp, th2):
            out.append(i)
    return out


def resolver(plantel: list[dict], fuera: list[dict], once: list[str],
             banca: list[str] | None = None, ids: dict[str, int] | None = None) -> dict:
    """Cruza la hoja del partido con la tabla de Cowork y cierra el bloque F.

    - en el once  → disponible (y titular)
    - en la banca → disponible; si es 🔴/🟠 cuenta como rotación voluntaria (F4)
    - en ninguna  → baja para esta fecha, con el motivo público si ya se sabía
    - nombre que casa con dos jugadores → NO se resuelve: va a `dudas`

    `ids` (nombre de la hoja → id de API-Football) manda sobre el nombre cuando
    la tabla trae `jugadorId`: la API y la prensa escriben distinto al mismo
    jugador («J. Cerro» / «Joshua Cantt») y ninguna regla de nombres los une.

    Devuelve el plantel con estados, el diagnóstico F2 y lo que no se pudo
    casar, para que la pantalla lo muestre en vez de esconderlo.
    """
    banca = banca or []
    conocidas = {normalizar(f.get("nombre", "")):
                 ((f.get("estado") or "baja").lower(), f.get("motivo", "")) for f in fuera}
    estados: dict[int, tuple[str, str]] = {}
    dudas: list[str] = []
    no_reconocidos: list[str] = []
    no_reconocidos_once: list[str] = []

    por_id = {j["jugadorId"]: i for i, j in enumerate(plantel) if j.get("jugadorId") is not None}
    # el otro id de la misma persona (la tabla F1 funde los dos, incidencia 381)
    for i, j in enumerate(plantel):
        for alt in j.get("idsAlternos") or []:
            por_id.setdefault(alt, i)
    # EL MISMO JUGADOR DOS VECES EN LA TABLA. Cúcuta (20/10/2026, 335): la base lo
    # llama «D. Gelvez» (con id) y la hoja y la prensa «Dayan Pérez»; el parte lo
    # puso dos veces, la fila con id casó por id y la de prensa, sin id, salió
    # «baja» —un 82 % menos de ataque por el autor del gol—. Una fila SIN id que
    # casa por nombre con un jugador de la hoja que ya casó por id con OTRA fila
    # es esa misma persona: se marca duplicada y no pesa.
    duplicados: dict[int, int] = {}
    homonimos_once = 0
    ids = ids or {}
    # un nombre repetido trae la lista de sus ids: se toman en el orden de la
    # hoja (incidencia 372, los dos «Pedrinho» titulares del Shakhtar)
    pendientes = {k: (list(v) if isinstance(v, list) else [v]) for k, v in ids.items()}
    for lista, destino in ((once, "titular"), (banca, "banca")):
        for nombre in lista:
            cola = pendientes.get(nombre) or []
            jid = cola.pop(0) if cola else None
            idx = [por_id[jid]] if jid in por_id else _buscar(plantel, nombre)
            if jid is not None and jid not in por_id:
                # LA PILA SOLA NO PISA UN ID (30/10/2026, incidencia 855): la hoja
                # trae «Danilo» 553 del banco y la tabla «Danilo Santos» 275170, que
                # no viajó; casaba por la pila y salía de la banca en vez de baja.
                # Con los dos ids a la vista y distintos, una coincidencia de solo
                # el nombre de pila no es la misma persona.
                th = _tokens(nombre)
                idx = [i for i in idx if plantel[i].get("jugadorId") is None
                       or not _solo_pila(_tokens(plantel[i].get("nombre", "")), th)]
            if jid in por_id:
                for k in _buscar(plantel, nombre):
                    if k != por_id[jid] and plantel[k].get("jugadorId") is None:
                        duplicados[k] = por_id[jid]
            if destino == "banca":
                # un suplente que también casa con un titular ya resuelto no lo
                # pisa: «André Ramalho» (banca) casaba con «André» (titular)
                # y lo pasaba a rotado (Corinthians 11/10/2026)
                idx = [i for i in idx if estados.get(i, ("", ""))[1] != "titular"]
            if len(idx) == 1:
                estados[idx[0]] = ("disponible", destino)
            elif len(idx) > 1:
                dudas.append(f"«{nombre}» casa con {len(idx)} jugadores de la tabla: "
                             f"{', '.join(plantel[i].get('nombre', '?') for i in idx)} "
                             "(la tabla con `jugadorId` lo resuelve)")
                # UN HOMÓNIMO NO ES UNA BAJA. Shakhtar (17/10/2026): dos
                # «Pedrinho» en la tabla sin id, el que jugó y metió el penal
                # salía de baja y el IP quedaba inflado. Uno de los dos está en
                # la hoja seguro: quedan disponibles, marcados como homónimos.
                for i in idx:
                    estados.setdefault(i, ("disponible", f"{destino} (homónimo)"))
                if destino == "titular":
                    homonimos_once += 1
            else:
                no_reconocidos.append(nombre)
                if destino == "titular":
                    no_reconocidos_once.append(nombre)

    # LA FILA CUYO ID ES EL ALTERNO DE OTRA es esa otra persona: la tabla la
    # trajo dos veces (Pasto, «S. Cordoba» 538162 baja con «S. Córdoba» 64215
    # en la banca, incidencia 423)
    alternos = {alt: i for i, j in enumerate(plantel) for alt in j.get("idsAlternos") or []}
    for k, j in enumerate(plantel):
        dueno = alternos.get(j.get("jugadorId"))
        if dueno is not None and dueno != k and k not in estados:
            duplicados[k] = dueno

    resuelto: list[dict] = []
    for i, j in enumerate(plantel):
        clave = normalizar(j.get("nombre", ""))
        if i in duplicados and i not in estados:
            otro = plantel[duplicados[i]]
            resuelto.append({**j, "estado": "duplicado", "hoja": "duplicado",
                             "motivo": f"es «{otro.get('nombre', '?')}» (jugadorId {otro.get('jugadorId')}): la hoja "
                                       "lo nombra así y ya está contado en esa fila"})
        elif i in estados:
            resuelto.append({**j, "estado": "disponible", "motivo": "",
                             "hoja": estados[i][1]})
        elif clave in conocidas:
            estado, motivo = conocidas[clave]
            # CON LA HOJA A LA VISTA YA NO HAY DUDA: quien estaba en duda y no
            # figura en la hoja no jugó. Seguir contándolo como duda le pesaba la
            # mitad (Paradela, titular fijo de Cruz Azul, 11/10/2026: IP 3.0 en
            # vez de 4.5).
            if estado == "duda":
                estado, motivo = "baja", (f"{motivo} · " if motivo else "") + "no figura en la hoja del partido"
            resuelto.append({**j, "estado": estado, "motivo": motivo, "hoja": "fuera"})
        else:
            resuelto.append({**j, "estado": "baja",
                             "motivo": "no figura en la hoja del partido", "hoja": "fuera"})

    diag = evaluar([j for j in resuelto if j["estado"] != "duplicado"])
    # F4 · rotación voluntaria: titulares del XI tipo que hoy arrancan en banca
    rotados = [j["nombre"] for j in resuelto
               if j.get("hoja") == "banca" and (j.get("rol") or "").upper() in ("TF", "TH")]
    diag["f4"] = {
        "rotados": len(rotados),
        "nombres": rotados,
        "diagnostico": ("sin rotación respecto al XI tipo" if not rotados else
                        f"{len(rotados)} titular(es) del XI tipo en el banco: "
                        "verificar si es profundidad (refuerza B5) o dependencia"),
    }
    diag["jugadores"] = resuelto
    diag["dudas"] = dudas
    diag["noReconocidos"] = no_reconocidos
    # los TITULARES de la hoja sin fila en la tabla (incidencia 743): no pesan
    # en el IP ni como disponibles; el parte lo avisa (ONCE-SIN-FILA-F1)
    diag["noReconocidosOnce"] = no_reconocidos_once
    # cuántos nombres del ONCE (no de la banca) se pudieron casar con la tabla.
    # Es el termómetro de si el cruce vale: un once que casa con 3 de 11 no es
    # un equipo diezmado, es una hoja que no corresponde a esta tabla.
    diag["casados"] = sum(1 for i, _ in enumerate(plantel)
                          if estados.get(i, ("", ""))[1] == "titular") + homonimos_once
    diag["homonimos"] = sum(1 for v in estados.values() if v[1].endswith("(homónimo)"))
    diag["duplicados"] = [plantel[i].get("nombre", "") for i in duplicados if i not in estados]
    diag["once"] = len(once)
    return diag


def titulares_fijos_fuera(jugadores: list[dict]) -> list[str]:
    """Los 🔴 Titular fijo que no están disponibles para esta fecha."""
    return [j.get("nombre", "") for j in jugadores
            if (j.get("rol") or "").upper() == "TF" and (j.get("estado") or "") == "baja"]


def alerta_f3(clasificacion: str, ip_nivel: str, tf_fuera: list[str] | None = None,
              zonas_criticas: list[str] | None = None, provisional: bool = False) -> dict | None:
    """F3 · formación fraccionada: EFE 🟢/🟡 pero, para esta fecha, IP > 7 (🔴),
    ≥ 2 titulares fijos ausentes **o una zona en 🔴 (> 40 %)** —la F3 por zona
    de la EFE v1.7, que la nombra (Bayern MID 41,7 % con IP 5)—.
    Solo con la primera, la Juve del 11/10/2026 (Yildiz y Locatelli fuera, IP
    6.5) se quedaba sin alerta. `provisional`: antes del once, sobre las bajas
    ya conocidas (rama A del bloque congelado, incidencia 383)."""
    tf_fuera, zonas_criticas = tf_fuera or [], zonas_criticas or []
    if clasificacion not in ("FORMADO", "EN_FORMACION"):
        return None
    if ip_nivel != "rojo" and len(tf_fuera) < 2 and not zonas_criticas:
        return None
    motivo = ("impacto 🔴" if ip_nivel == "rojo" else
              f"{len(tf_fuera)} titulares fijos ausentes ({', '.join(tf_fuera)})" if len(tf_fuera) >= 2 else
              f"zona {'/'.join(zonas_criticas)} en 🔴 (> 40 %)")
    if zonas_criticas and ip_nivel == "rojo":
        motivo += f"; zona {'/'.join(zonas_criticas)} en 🔴"
    return {
        "codigo": "F3",
        "tipo": "fecha",
        **({"provisional": True} if provisional else {}),
        "detalle": f"El EFE es {clasificacion.replace('_', ' ')}, pero para esta fecha el equipo "
                   f"opera degradado ({motivo}). Reducir confianza en las K históricas y bajar "
                   "un nivel la confianza efectiva."
                   + (" PROVISIONAL: sin once confirmado, con las bajas ya conocidas (rama A); se "
                      "rehace al cerrar el once" if provisional else ""),
    }
