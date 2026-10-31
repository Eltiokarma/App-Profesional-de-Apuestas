"""LA IDENTIDAD DE UNA PERSONA, EN UN SOLO LUGAR (30/10/2026).

Quién es quién —un jugador de la hoja contra la tabla F1, dos ids de la API
que son la misma persona, el DT de la base contra el de la prensa— se decidía
en CINCO módulos (bloque_f, f1_base, dtp_cowork, parte, ingesta/jugadores) con
cuatro versiones de «una letra de diferencia», dos listas de partículas y dos
formas de quitar tildes (una tiraba la «ß» y la «ø»: «Hoeneß» quedaba «hoene»
y «Ødegaard» «degaard»). Cada parche arreglaba un módulo y el mismo error
volvía por otro: la identidad del jugador se parchó ocho veces en un mes
(381, 423, 449, 582, 673, 741, 839, 856) y la 724 se reportó 11 veces.

Acá vive la regla UNA vez; los módulos la importan (sus nombres viejos quedan
como alias). Un caso nuevo se arregla acá, con su test en
`backend/test_identidad.py`, y vale para todos. `backend/test_arquitectura.py`
falla si alguien vuelve a escribir una comparación de letras fuera de este
archivo.
"""
from __future__ import annotations

import difflib
import re
import unicodedata

from backend.nombres import limpiar_nombre

# partículas que no identifican a nadie: «Alexis Mac Allister», «Van Dijk»,
# «De Paul», «Le Normand», «Jr.» (unión de las dos listas que había)
PARTICULAS = {"de", "del", "la", "las", "lo", "los", "da", "das", "do", "dos", "van", "von", "di", "el", "al",
              "san", "santa", "mc", "jr", "le"}

# letras que NFKD no descompone y el «ascii ignore» tiraba
_LETRAS = str.maketrans({"ß": "ss", "ø": "o", "Ø": "o", "æ": "ae", "Æ": "ae", "œ": "oe", "Œ": "oe",
                         "đ": "d", "Đ": "d", "ł": "l", "Ł": "l", "ı": "i", "þ": "th", "Þ": "th", "ð": "d"})


def plano(texto: str) -> str:
    """minúsculas, sin tildes, con la ß/ø/ł convertidas, el apóstrofo que UNE
    («N'Diaye» = «Ndiaye», Le Havre, incidencia 653) y todo lo que no es letra
    ni dígito hecho espacio."""
    t = (texto or "").translate(_LETRAS)
    t = re.sub(r"['’`´]", "", t)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def tokens(nombre: str) -> list[str]:
    """Las palabras útiles del nombre, en orden: sin partículas y con las
    iniciales como una letra («A. Campos» → ['a', 'campos']). El nombre se
    limpia antes (entidades HTML y mojibake de la API)."""
    return [t for t in plano(limpiar_nombre(nombre or "") or "").split() if t and t not in PARTICULAS]


# EL DIMINUTIVO ES LA MISMA PILA (31/10/2026, incidencia 937: el once de Oriente
# Petrolero trae «Fran Lopez» y la tabla F1 «Francisco López»; sonó
# ONCE-SIN-FILA-F1 y no pesó en el IP; y 887/893, «Rafa Llorente»). Una lista
# CERRADA, no «el prefijo»: «jose» y «joselu», «juan» y «juanjo» pueden ser dos
# personas del mismo plantel.
HIPOCORISTICOS = {
    "fran": ("francisco", "franco", "francesc"), "paco": ("francisco",), "pancho": ("francisco",),
    "rafa": ("rafael",), "pepe": ("jose",), "nacho": ("ignacio",), "lucho": ("luis",),
    "toni": ("antonio",), "tony": ("antonio", "anthony"), "manu": ("manuel", "emmanuel"),
    "dani": ("daniel",), "santi": ("santiago",), "seba": ("sebastian",), "nico": ("nicolas",),
    "fede": ("federico",), "gonza": ("gonzalo",), "rodri": ("rodrigo",), "edu": ("eduardo",),
    "javi": ("javier",), "kike": ("enrique",), "quique": ("enrique",), "guille": ("guillermo",),
    "memo": ("guillermo",), "pipe": ("felipe",), "mati": ("matias",), "maxi": ("maximiliano",),
    "gabi": ("gabriel",), "tomi": ("tomas",), "agus": ("agustin",), "facu": ("facundo",),
    "nando": ("fernando",), "fer": ("fernando",), "migue": ("miguel",), "tincho": ("martin",),
    "joaco": ("joaquin",), "isma": ("ismael",), "moi": ("moises",), "pato": ("patricio",),
    "chucho": ("jesus",), "lalo": ("eduardo",), "alex": ("alejandro", "alexander", "alexis"),
}


def _hipocoristico(uno: str, otro: str) -> bool:
    return otro in HIPOCORISTICOS.get(uno, ()) or uno in HIPOCORISTICOS.get(otro, ())


def misma_pila(uno: str, otro: str) -> bool:
    """Nombre de pila igual, con una letra doble de más o de menos («Emmanuel» /
    «Emanuel», incidencia 449), uno es la inicial del otro («a» ↔ «ángelo») o el
    diminutivo de la lista cerrada («fran» ↔ «francisco», 937). Nada más:
    «jose» y «joselu» son personas distintas."""
    if uno == otro or _hipocoristico(uno, otro):
        return True
    if len(uno) > 3 and len(otro) > 3 and re.sub(r"(.)\1", r"\1", uno) == re.sub(r"(.)\1", r"\1", otro):
        return True
    if len(uno) == 1:
        return otro.startswith(uno)
    if len(otro) == 1:
        return uno.startswith(otro)
    return False


def apellido_casi(uno: str, otro: str, minimo: int = 5) -> bool:
    """EL MISMO APELLIDO ESCRITO DISTINTO por dos fuentes. Iguales tras el
    seseo («Quirós»/«Quiroz») o la ß mal codificada («Hoeneß»/«Hoeneb»); y,
    en apellidos de `minimo` letras o más: una letra cambiada («Zampiero»/
    «Zampieri»), una de más o de menos («Berríos»/«Berios», 856), una letra
    doble («Emmanuel»/«Emanuel») o las mismas letras en otro orden («Bizans»/
    «Bisanz», «Balazar»/«Bazalar»). En uno corto, una letra ya es otra persona
    (Martínez/Martino no: son dos letras)."""
    a, b = (uno or "").replace("z", "s"), (otro or "").replace("z", "s")
    if a == b:
        return bool(a)
    if a.replace("ss", "b") == b.replace("ss", "b"):
        return True
    if min(len(a), len(b)) < minimo:
        return False
    if sorted(a) == sorted(b):
        return True
    if re.sub(r"(.)\1", r"\1", a) == re.sub(r"(.)\1", r"\1", b):
        return True
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) <= 1
    if abs(len(a) - len(b)) == 1:
        largo, corto = (a, b) if len(a) > len(b) else (b, a)
        return any(largo[:k] + largo[k + 1:] == corto for k in range(len(largo)))
    return False


def mismo_jugador(uno: str, otro: str) -> bool:
    """¿Dos nombres de la API son la misma persona? El mismo apellido (o casi:
    `apellido_casi`) y la misma pila o su inicial: «S. Peña»/«S. Pena»,
    «E. Griffa»/«Emiliano Griffa», «Y. Guzmán»/«Y. Guzman». O el mismo nombre
    al revés con las palabras enteras («Luan Patrick»/«Patrick Luan», 502).
    Un nombre de una sola palabra no alcanza para afirmarlo."""
    a, b = tokens(uno), tokens(otro)
    if len(a) < 2 or len(b) < 2:
        return False
    if all(len(t) > 1 for t in a + b) and sorted(a) == sorted(b):
        return True
    if not misma_pila(a[0], b[0]):
        return False
    if a[-1] == b[-1] or apellido_casi(a[-1], b[-1]):
        return True
    # EL NOMBRE CORTO LLEVA EL PRIMER APELLIDO (31/10/2026, incidencia 893: «A.
    # Torrez» y «A. W. Torrez Suarez» de Oriente, el mismo arquero con dos ids):
    # una pila y UN apellido contra el nombre largo con dos o más, el apellido
    # corto casa con cualquiera de los del largo, no solo con el último.
    corto, largo = (a, b) if len(a) <= len(b) else (b, a)
    return (len(corto) == 2 and len(largo) >= 3
            and any(corto[-1] == x or apellido_casi(corto[-1], x) for x in largo[1:] if len(x) > 1))


def ids_equivalentes(antes: dict, ahora: dict) -> dict:
    """{id de `antes` → id de `ahora`} para el MISMO jugador con otro id entre
    dos hojas (incidencia 899: «Lautaro Herrera» en entraron y en salieron de
    `cambiosXi`, dos registros de la API). Solo ids que no están en la otra
    hoja y con UN candidato por nombre (`mismo_jugador`): dos posibles, nada."""
    sueltos = {i: n for i, n in ahora.items() if i not in antes}
    out = {}
    for i, n in antes.items():
        if i in ahora or not n:
            continue
        cand = [j for j, m in sueltos.items() if m and mismo_jugador(n, m)]
        if len(cand) == 1:
            out[i] = cand[0]
    return out


def casa(tokens_plantel: list[str], tokens_hoja: list[str]) -> bool:
    """¿La hoja nombra a este jugador de la tabla? API-Football escribe
    «A. Campos»; la prensa «Ángelo Campos»; un pantallazo solo «Campos». El
    apellido es obligatorio y la pila, si la hoja la trae, tiene que cuadrar.
    La hoja con SOLO la pila («Saúl», «Breno», Flamengo y Corinthians
    11/10/2026) casa con la pila del jugador; si dos la comparten, quien llama
    lo manda a dudas. «PH Ganso» = Paulo Henrique Ganso: la pila en iniciales."""
    if not tokens_plantel or not tokens_hoja:
        return False
    apellidos = set(tokens_plantel[1:]) or set(tokens_plantel)
    if not set(tokens_hoja) & apellidos:
        return len(tokens_hoja) == 1 and len(tokens_plantel) > 1 and tokens_hoja[0] == tokens_plantel[0]
    pila_plantel = tokens_plantel[0] if len(tokens_plantel) > 1 else ""
    pila_hoja = [t for t in tokens_hoja if t not in apellidos]
    if not pila_hoja or not pila_plantel:
        return True
    iniciales = "".join(t[0] for t in tokens_plantel[:-1])
    return any(misma_pila(t, pila_plantel) or (1 < len(t) <= 3 and t == iniciales[:len(t)])
               for t in pila_hoja)


def solo_pila(tokens_plantel: list[str], tokens_hoja: list[str]) -> bool:
    """¿La hoja casa con este jugador solo por el nombre de pila (sin apellido)?"""
    apellidos = set(tokens_plantel[1:]) or set(tokens_plantel)
    return not set(tokens_hoja) & apellidos


# ── el DT: laxo a propósito ──────────────────────────────────────────────────
# Una cuarentena falsa por «DT equivocado» saca un caso bueno de la métrica, y
# la base escribe al entrenador con letras rotas: acá basta un apellido en
# común (con tolerancia), no el nombre entero.

# EL APODO DEL DT ES SU NOMBRE (31/10/2026, incidencia 951: la base marcó un
# cambio de DT en el Granada de «Pacheta» a «José Rojo Martín», que es la misma
# persona). Lista CERRADA, con el caso que la pidió: apodo → nombre civil.
APODOS_DT = {"pacheta": "jose rojo martin"}


def tokens_dt(nombre: str) -> list[str]:
    """Las palabras de 3 letras o más del nombre de un DT (las iniciales no
    cuentan); un apodo conocido se lee como su nombre civil."""
    t = " ".join(plano(nombre).split())
    return [x for x in APODOS_DT.get(t, t).split() if len(x) >= 3]


def apellido_dt(x: str, y: str) -> bool:
    """El mismo apellido de DT: `apellido_casi`, o —la base trae letras
    corruptas («S. Hoeneb» por «S. Hoeneß», Stuttgart 23/09)— las mismas 5
    primeras letras o un parecido ≥ 80 % en apellidos de 4 letras o más."""
    if x == y or apellido_casi(x, y):
        return True
    if min(len(x), len(y)) >= 5 and x[:5] == y[:5]:
        return True
    return min(len(x), len(y)) >= 4 and difflib.SequenceMatcher(None, x, y).ratio() >= 0.8


def mismo_dt(a: str, b: str) -> bool:
    """¿Nombran al mismo entrenador? («M. Pellegrino» · «Mauricio Pellegrino» ·
    «Hernán Torres Oliveros» · «H. Torres» · «S. Hoeneß» / «S. Hoeneb»): basta
    un apellido en común con la tolerancia de `apellido_dt`."""
    ta, tb = tokens_dt(a), tokens_dt(b)
    return any(apellido_dt(x, y) for x in ta for y in tb)


def ultima_palabra_dt(nombre: str) -> str:
    """La última palabra de 2+ letras (el apellido como lo comparaba la ingesta)."""
    partes = [p for p in plano(nombre).split() if len(p) > 1]
    return partes[-1] if partes else plano(nombre).strip()


def mismo_nombre_dt(a: str, b: str) -> bool:
    """¿Nombran al mismo DT? Más estricta que `mismo_dt`: la ÚLTIMA palabra de
    uno está entre las del otro (en cualquier sentido) —en España la última es
    el apellido materno: «Manuel Luis Pellegrini Ripamonti» contra
    «Pellegrini» de la alineación (11/10/2026)—, o la última casa con una del
    otro salvo una letra (`apellido_casi`: «Hoeneß»/«Hoeneb», «Bazalar»/
    «Balazar»), o comparten dos palabras. Las iniciales no cuentan."""
    ta, tb = tokens_dt(a), tokens_dt(b)
    if not ta or not tb:
        return ultima_palabra_dt(a) == ultima_palabra_dt(b)
    if ta[-1] in tb or tb[-1] in ta:
        return True
    if any(apellido_casi(x[-1], y) for x, ys in ((ta, tb), (tb, ta)) for y in ys):
        return True
    return len(set(ta) & set(tb)) >= 2
