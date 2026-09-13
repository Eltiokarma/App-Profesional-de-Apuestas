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
    limpio = re.sub(r"[^a-z0-9ñ ]+", " ", normalizar(nombre))
    return [t for t in limpio.split() if t and t not in _PARTICULAS]


def _misma_pila(uno: str, otro: str) -> bool:
    """Nombre de pila igual, o uno es la inicial del otro ("a" ↔ "ángelo").

    Nada más: "jose" y "joselu" son personas distintas y un prefijo suelto los
    confundiría."""
    if uno == otro:
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
        return False
    pila_plantel = tokens_plantel[0] if len(tokens_plantel) > 1 else ""
    pila_hoja = [t for t in tokens_hoja if t not in apellidos]
    if not pila_hoja or not pila_plantel:
        return True
    return any(_misma_pila(t, pila_plantel) for t in pila_hoja)


def _buscar(plantel: list[dict], nombre_hoja: str) -> list[int]:
    th = _tokens(nombre_hoja)
    return [i for i, j in enumerate(plantel) if _casa(_tokens(j.get("nombre", "")), th)]


def resolver(plantel: list[dict], fuera: list[dict], once: list[str],
             banca: list[str] | None = None) -> dict:
    """Cruza la hoja del partido con la tabla de Cowork y cierra el bloque F.

    - en el once  → disponible (y titular)
    - en la banca → disponible; si es 🔴/🟠 cuenta como rotación voluntaria (F4)
    - en ninguna  → baja para esta fecha, con el motivo público si ya se sabía
    - nombre que casa con dos jugadores → NO se resuelve: va a `dudas`

    Devuelve el plantel con estados, el diagnóstico F2 y lo que no se pudo
    casar, para que la pantalla lo muestre en vez de esconderlo.
    """
    banca = banca or []
    conocidas = {normalizar(f.get("nombre", "")):
                 ((f.get("estado") or "baja").lower(), f.get("motivo", "")) for f in fuera}
    estados: dict[int, tuple[str, str]] = {}
    dudas: list[str] = []
    no_reconocidos: list[str] = []

    for lista, destino in ((once, "titular"), (banca, "banca")):
        for nombre in lista:
            idx = _buscar(plantel, nombre)
            if len(idx) == 1:
                estados[idx[0]] = ("disponible", destino)
            elif len(idx) > 1:
                dudas.append(f"«{nombre}» casa con {len(idx)} jugadores de la tabla: "
                             f"{', '.join(plantel[i].get('nombre', '?') for i in idx)}")
            else:
                no_reconocidos.append(nombre)

    resuelto: list[dict] = []
    for i, j in enumerate(plantel):
        clave = normalizar(j.get("nombre", ""))
        if i in estados:
            resuelto.append({**j, "estado": "disponible", "motivo": "",
                             "hoja": estados[i][1]})
        elif clave in conocidas:
            estado, motivo = conocidas[clave]
            resuelto.append({**j, "estado": estado, "motivo": motivo, "hoja": "fuera"})
        else:
            resuelto.append({**j, "estado": "baja",
                             "motivo": "no figura en la hoja del partido", "hoja": "fuera"})

    diag = evaluar(resuelto)
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
    # cuántos nombres del ONCE (no de la banca) se pudieron casar con la tabla.
    # Es el termómetro de si el cruce vale: un once que casa con 3 de 11 no es
    # un equipo diezmado, es una hoja que no corresponde a esta tabla.
    diag["casados"] = sum(1 for i, _ in enumerate(plantel)
                          if estados.get(i, ("", ""))[1] == "titular")
    diag["once"] = len(once)
    return diag


def alerta_f3(clasificacion: str, ip_nivel: str) -> dict | None:
    """F3 · formación fraccionada: EFE 🟢/🟡 pero impacto 🔴 para esta fecha."""
    if ip_nivel != "rojo" or clasificacion not in ("FORMADO", "EN_FORMACION"):
        return None
    return {
        "codigo": "F3",
        "tipo": "fecha",
        "detalle": f"El EFE es {clasificacion.replace('_', ' ')}, pero para esta fecha el equipo "
                   "opera degradado (impacto 🔴). Reducir confianza en las K históricas y bajar "
                   "un nivel la confianza efectiva.",
    }
