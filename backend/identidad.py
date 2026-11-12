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
    # LA RAYA SEPARA (10/11/2026, incidencia 1347, Olympiakos–PAOK: «Puerta–Freuler»
    # quedaba «puertafreuler» porque el «encode ascii ignore» tiraba la «–» antes
    # de hacerla espacio, y el DTP no vio a Puerta en el banco). Todo signo que no
    # es letra ni dígito se hace espacio ANTES de quitar las tildes.
    t = re.sub(r"[^\w\s]", " ", t)
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
    "rafa": ("rafael",), "pepe": ("jose",), "pep": ("josep",), "nacho": ("ignacio",), "lucho": ("luis",),
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
    # LA I Y LA J INICIALES DE LA PILA VASCA (11/11/2026, incidencia 1385,
    # Amorebieta: «Ion Etxaniz» en la tabla F1 y «Jon Etxaniz» en la hoja; salía
    # de baja siendo titular). Solo esa letra y con el resto igual.
    if len(uno) >= 3 and len(uno) == len(otro) and uno[1:] == otro[1:] and {uno[0], otro[0]} == {"i", "j"}:
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
    doble («Emmanuel»/«Emanuel») o dos letras que cambiaron de lugar («Bizans»/
    «Bisanz», «Balazar»/«Bazalar»; un anagrama entero no: «mientras» no es
    «Martínez», 1256). En uno corto, una letra ya es otra persona
    (Martínez/Martino no: son dos letras)."""
    a, b = (uno or "").replace("z", "s"), (otro or "").replace("z", "s")
    if a == b:
        return bool(a)
    if a.replace("ss", "b") == b.replace("ss", "b"):
        return True
    if min(len(a), len(b)) < minimo:
        return False
    # LA «μπ» GRIEGA SE TRANSLITERA «mp» O «b» (07/11/2026, incidencia 1306,
    # Aris–Panetolikos: «Barbopoulos» en la hoja y «Barmpopoulos» en la
    # plantilla; el arquero suplente quedaba de baja y la zona GK subía 14,3 %).
    # Solo si uno trae «mp» donde el otro trae «b», y en apellidos largos.
    if "mp" in a + b and a.replace("mp", "b") == b.replace("mp", "b"):
        return True
    # LA GRAFÍA VASCA Y LA CASTELLANA DEL MISMO APELLIDO (11/11/2026, incidencia
    # 1385, Amorebieta: «Agirregomezkorta» en la tabla F1 y «Aguirregomezcorta»
    # en la hoja). k ↔ c ante a/o/u, «gui/gue» ↔ «gi/ge», «tx» ↔ «ch». En
    # apellidos de 6 letras o más.
    if min(len(a), len(b)) >= 6 and _castellano(a) == _castellano(b):
        return True
    # LAS MISMAS LETRAS EN OTRO ORDEN ES UN INTERCAMBIO, NO UN ANAGRAMA
    # (06/11/2026, incidencia 1256, Barracas–Racing: «mientras» de la prosa del
    # DTP es anagrama de «martines» y casaba con D. Martínez, y el DTP pedía
    # rehacer por un titular que no cambió). «Bizans»/«Bisanz» y «Balazar»/
    # «Bazalar» son dos letras que cambiaron de lugar: a lo sumo dos posiciones
    # distintas, como cualquier errata.
    if len(a) == len(b) and sorted(a) == sorted(b) and sum(x != y for x, y in zip(a, b)) <= 2:
        return True
    if re.sub(r"(.)\1", r"\1", a) == re.sub(r"(.)\1", r"\1", b):
        return True
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) <= 1
    if abs(len(a) - len(b)) == 1:
        largo, corto = (a, b) if len(a) > len(b) else (b, a)
        return any(largo[:k] + largo[k + 1:] == corto for k in range(len(largo)))
    return False


def _castellano(apellido: str) -> str:
    """El apellido con la grafía vasca llevada a la castellana (1385)."""
    t = apellido.replace("tx", "ch")
    t = re.sub(r"gu(?=[ie])", "g", t)
    return re.sub(r"k(?=[aou])", "c", t)


def apellido_truncado(corto: str, largo: str) -> bool:
    """LA API CORTA EL APELLIDO (11/11/2026, incidencia 1385: «Javi Entreca» por
    Javier Entrecanales en Amorebieta, «Manu Pedre» por Manuel Pedreño en el
    Logroñés). El corto es el comienzo del largo, con 5 letras o más y al menos
    dos menos que el largo. Solo sirve CON la pila entera y la misma: «Martín» y
    «Martínez» son dos apellidos, y por eso esto no va en `apellido_casi`."""
    # el patronímico no es un corte: Martín/Martínez, Gonzalo/González
    return (len(corto) >= 5 and len(largo) - len(corto) >= 2 and largo.startswith(corto)
            and largo[len(corto):] not in ("ez", "es", "is", "iz", "ss"))


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
        # LA PILA COMPUESTA (02/11/2026, incidencia 1077: «Nahuel Arias» de la
        # tabla y «Óscar Nahuel Arias» de la prensa, San Lorenzo): el nombre
        # corto usa la SEGUNDA pila del largo. Con la pila entera y el mismo
        # apellido.
        corto, largo = (a, b) if len(a) <= len(b) else (b, a)
        return (len(corto) == 2 and len(largo) >= 3 and len(corto[0]) > 1
                and any(misma_pila(corto[0], p) for p in largo[1:-1] if len(p) > 1)
                and (corto[-1] == largo[-1] or apellido_casi(corto[-1], largo[-1])))
    if a[-1] == b[-1] or apellido_casi(a[-1], b[-1]) or apellidos_juntos(a, b):
        return True
    # el apellido truncado por la API, con la pila ENTERA de los dos lados (1385)
    if len(a[0]) > 1 and len(b[0]) > 1 and (apellido_truncado(a[-1], b[-1]) or apellido_truncado(b[-1], a[-1])):
        return True
    # EL NOMBRE CORTO LLEVA EL PRIMER APELLIDO (31/10/2026, incidencia 893: «A.
    # Torrez» y «A. W. Torrez Suarez» de Oriente, el mismo arquero con dos ids):
    # una pila y UN apellido contra el nombre largo con dos o más, el apellido
    # corto casa con cualquiera de los del largo, no solo con el último.
    corto, largo = (a, b) if len(a) <= len(b) else (b, a)
    return (len(corto) == 2 and len(largo) >= 3
            and any(corto[-1] == x or apellido_casi(corto[-1], x) for x in largo[1:] if len(x) > 1))


def id_cruzado(nombre_hoja: str, pid: int, plantel: dict) -> int | None:
    """LA HOJA TRAE EL ID DE UNO CON EL NOMBRE DE OTRO (10/11/2026, incidencia
    1330, aprobada por el usuario): Pasto con 305596 —Paraszhidisz en la
    plantilla— escrito «P. Preciado», que es el 527180; St. Truiden con 406784
    —Zalán— escrito «I. Atrok». Si el nombre de la hoja NO es el del dueño del
    id (`plantel[pid]`) y casa con UN solo otro jugador de la plantilla
    (`plantel`: id → nombre), devuelve el id de ese otro: es a quien la hoja
    nombra. Con el dueño desconocido, dos candidatos o ninguno: None (el id
    manda, como siempre; 1307)."""
    dueno = plantel.get(pid)
    if not dueno or not nombre_hoja or len(tokens(nombre_hoja)) < 2:
        return None
    if mismo_jugador(nombre_hoja, dueno) or tokens(nombre_hoja) == tokens(dueno):
        return None
    otros = [q for q, n in plantel.items() if q != pid and n and mismo_jugador(nombre_hoja, n)]
    return otros[0] if len(otros) == 1 else None


def mismo_apellido(uno: str, otro: str) -> bool:
    """El mismo último apellido (o casi: `apellido_casi`), sin mirar la pila.
    Solo para MARCAR una posibilidad, nunca para fundir: «Jose Sagredo» /
    «Jesús Sagredo» (1330)."""
    a, b = tokens(uno), tokens(otro)
    return len(a) >= 2 and len(b) >= 2 and len(a[-1]) > 1 and (a[-1] == b[-1] or apellido_casi(a[-1], b[-1]))


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


def apellidos_juntos(uno: list[str], otro: list[str]) -> bool:
    """EL APELLIDO CON GUION ES EL MISMO PEGADO (08/11/2026, incidencia 1331,
    U. Católica–Deportes Limache: «Tomas Astaburuaga» de la ficha y «T.
    Asta-Buruaga» de la tabla F1; sonó ONCE-SIN-FILA-F1 y el titular quedaba en
    `fuera`). El guion se hace espacio en `plano`, así que «asta buruaga» no
    casaba con «astaburuaga». Los apellidos (todo después de la pila) pegados
    son iguales, con 6 letras o más, y con dos o más palabras en un lado: dos
    apellidos de una palabra distinta no entran por acá."""
    if len(uno) < 2 or len(otro) < 2 or max(len(uno), len(otro)) < 3:
        return False
    a, b = "".join(uno[1:]), "".join(otro[1:])
    return len(a) >= 6 and a == b


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
        if apellidos_juntos(tokens_plantel, tokens_hoja):  # «Asta-Buruaga» = «Astaburuaga» (1331)
            return misma_pila(tokens_plantel[0], tokens_hoja[0])
        return len(tokens_hoja) == 1 and len(tokens_plantel) > 1 and tokens_hoja[0] == tokens_plantel[0]
    pila_plantel = tokens_plantel[0] if len(tokens_plantel) > 1 else ""
    pila_hoja = [t for t in tokens_hoja if t not in apellidos]
    if not pila_hoja or not pila_plantel:
        return True
    iniciales = "".join(t[0] for t in tokens_plantel[:-1])
    return any(misma_pila(t, pila_plantel) or (1 < len(t) <= 3 and t == iniciales[:len(t)])
               for t in pila_hoja)


def pila_compuesta_posible(tokens_plantel: list[str], tokens_hoja: list[str]) -> bool:
    """¿La inicial de la hoja puede ser la de una PRIMERA pila que la tabla no
    escribe? «O. Arias» (Óscar Nahuel Arias) contra «Nahuel Arias» de la tabla
    (San Lorenzo, incidencia 1077): el mismo apellido, la hoja con una inicial
    y la tabla con una sola pila entera de otra letra. Es una POSIBILIDAD, no
    la misma persona («K. Álvarez» no es «Carlos Álvarez», 390): quien llama
    la usa solo como último recurso, con la fila sin `jugadorId` y el apellido
    único en la tabla y en la hoja."""
    return (len(tokens_plantel) == 2 and len(tokens_hoja) == 2
            and len(tokens_plantel[0]) > 1 and len(tokens_hoja[0]) == 1 and tokens_hoja[0].isalpha()
            and tokens_hoja[0] != tokens_plantel[0][0]
            and len(tokens_plantel[1]) > 1 and tokens_plantel[1] == tokens_hoja[1])


def pilas_enteras_distintas(nombres_uno, nombres_otro) -> bool:
    """¿Dos registros tienen, en alguno de sus nombres conocidos (la plantilla y
    las hojas), la pila ENTERA y distinta? Entonces son dos personas aunque la
    plantilla escriba a uno con inicial: «Ángel Gonzales» 101280 y «D.
    Gonzáles» 107017, que la hoja escribe «David Gonzales» (Los Chankas,
    incidencia 1107). Una pila del uno que está entre las del otro no es
    distinta (la pila compuesta: «Juan Bizans» / «Juan Francisco Bisanz»)."""
    def pilas(nombres):
        out = []
        for n in nombres or ():
            t = tokens(n)
            if len(t) >= 2 and len(t[0]) > 1:
                out.append(t[:-1])
        return out
    pu, po = pilas(nombres_uno), pilas(nombres_otro)
    if not pu or not po:
        return False
    return all(not any(misma_pila(x, y) for x in a for y in b if len(x) > 1 and len(y) > 1)
               for a in pu for b in po)


def menciona(nombre: str, frase: str, nombre_suelto: bool = False) -> bool:
    """¿La frase nombra a ESTE jugador? Una mención de su apellido (4 letras o
    más) que no vaya pegada a la inicial o la pila de OTRO: «N. da Silva» no
    es «K. Silva» (Boston River, incidencia 1111: el aviso de `equipos.fuera`
    tomaba al sancionado K. Silva por el N. da Silva del banco). Las
    partículas entre la pila y el apellido se saltan; una mención suelta
    («Silva») sí cuenta, porque no se sabe de quién es. Tampoco cuenta el
    apellido que es la pila de otro: «Felipe Anderson» no es «Matheus Felipe»
    (1236)."""
    t = tokens(nombre)
    apell = [x for x in t[1:] if len(x) >= 4] or [x for x in t if len(x) >= 4][-1:]
    if not apell:
        return False
    pila = t[0] if len(t) > 1 else ""
    limpio = limpiar_nombre(frase or "") or ""
    hallados = list(re.finditer(r"[^\W_][\w'’]*", limpio))
    crudo = [m.group(0) for m in hallados]
    palabras = [plano(w).replace(" ", "") for w in crudo]
    for k, w in enumerate(palabras):
        if w not in apell:
            continue
        j = k - 1
        while j >= 0 and (palabras[j] in PARTICULAS or palabras[j] in t[1:]):
            j -= 1
        # la palabra de antes es una pila si es una inicial o va con mayúscula
        # en medio de la frase («Entra Silva» al empezar no nombra a otro)
        # …salvo que la frase SEA un nombre suelto (un trozo de una lista de
        # banco: «Josep Díaz»): ahí la primera palabra con mayúscula es una pila
        # (11/11/2026, incidencia 1386, Amorebieta: FUERA-EN-LA-HOJA tomaba el
        # «Josep Díaz» del banco del DTP por el titular Ekain Díaz)
        otra_pila = j >= 0 and crudo[j][:1].isupper() and (len(palabras[j]) == 1 or j > 0 or nombre_suelto)
        propia = j >= 0 and bool(pila) and misma_pila(palabras[j], pila)
        # Y AL REVÉS: el «apellido» es la PILA de otro si lo sigue, pegado y con
        # mayúscula, un apellido que no es de este jugador (05/11/2026,
        # incidencia 1236, Palmeiras–Remo: «Flaco López y Felipe Anderson en el
        # banco» se leía como Matheus Felipe, baja de Remo, nombrado de
        # recambio). Solo con un espacio en medio: «Felipe, Anderson» o
        # «Felipe. Anderson» son dos menciones.
        n = k + 1
        otro_apellido = (n < len(crudo) and crudo[n][:1].isupper() and len(palabras[n]) >= 3
                         and palabras[n] not in t and palabras[n] not in PARTICULAS
                         and limpio[hallados[k].end():hallados[n].start()] == " ")
        if otro_apellido and not propia:
            continue
        if not pila or not otra_pila or propia:
            return True
    return False


def mencion_compartida(nombre: str, otros, frase: str, nombre_suelto: bool = False) -> bool:
    """¿La frase nombra a `nombre` pero también podría ser OTRO de `otros` con
    su mismo apellido? «Castillo» suelto con E. Castillo titular y J. Castillo
    en el banco no dice de cuál habla: no se afirma nada (10/11/2026,
    incidencia 1225, FUERA-EN-LA-HOJA: un titular nombrado de banco)."""
    t = tokens(nombre)
    if not t:
        return False
    for otro in otros or ():
        o = tokens(otro)
        if not o or o == t or not menciona(otro, frase, nombre_suelto):
            continue
        if o[-1] == t[-1] or apellido_casi(o[-1], t[-1]):
            return True
    return False


def solo_como_pila_de_otro(nombre: str, frase: str) -> bool:
    """¿Toda mención de las palabras de `nombre` en la frase es la PILA de otro
    jugador? Cada vez que aparece la sigue, con un solo espacio y mayúscula,
    un apellido que no es de `nombre`.

    Pieza «Gabriel Justino» contra «João Gabriel Castro Santos», del banco
    (05/11/2026, incidencia 1241, Botafogo–Atlético MG: saltó DTP-REHACER por
    «Gabriel»); la misma regla que `menciona` aplica desde la 1236. Sin
    ninguna mención exacta, False: no se tapa un cruce por tolerancia."""
    t = tokens(nombre)
    if not t:
        return False
    limpio = limpiar_nombre(frase or "") or ""
    hallados = list(re.finditer(r"[^\W_][\w'’]*", limpio))
    palabras = [plano(m.group(0)).replace(" ", "") for m in hallados]
    vistas = 0
    for k, w in enumerate(palabras):
        if w not in t or len(w) < 3:
            continue
        vistas += 1
        n = k + 1
        if not (n < len(hallados) and hallados[n].group(0)[:1].isupper() and len(palabras[n]) >= 3
                and palabras[n] not in t and palabras[n] not in PARTICULAS
                and limpio[hallados[k].end():hallados[n].start()] == " "):
            return False
    return vistas > 0


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


def pilas_distintas_dt(a: str, b: str) -> bool:
    """¿Los dos nombres traen la PILA ENTERA y no es la misma? Entonces son dos
    personas aunque compartan apellido (incidencia 1096, Defensor 02/11/2026:
    la base tenía a «Héctor Ignacio Rodríguez Peña» y dirigía el interino
    «Andrés Rodríguez»; como bastaba el apellido, DT-DISCREPANCIA no sonó y
    /burbujas lo dio por «asentado, 1826 días»). La pila de cada uno son las
    palabras ANTES de la primera que comparte con el otro; las iniciales no
    cuentan (`tokens_dt` las saca: «A. Rodríguez» sigue casando con «Andrés»),
    y una contenida en la otra es la misma («Pep» / «Josep»)."""
    ta, tb = tokens_dt(a), tokens_dt(b)

    def pila(t: list[str], otro: list[str]) -> list[str]:
        for i, x in enumerate(t):
            if any(apellido_dt(x, y) for y in otro):
                return t[:i]
        return []
    pa, pb = pila(ta, tb), pila(tb, ta)
    if not pa or not pb:
        return False
    return not any(misma_pila(x, y) or x in y or y in x for x in pa for y in pb)


def mismo_dt(a: str, b: str) -> bool:
    """¿Nombran al mismo entrenador? («M. Pellegrino» · «Mauricio Pellegrino» ·
    «Hernán Torres Oliveros» · «H. Torres» · «S. Hoeneß» / «S. Hoeneb»): basta
    un apellido en común con la tolerancia de `apellido_dt`, salvo que las dos
    pilas enteras sean distintas (`pilas_distintas_dt`, 1096)."""
    ta, tb = tokens_dt(a), tokens_dt(b)
    return any(apellido_dt(x, y) for x in ta for y in tb) and not pilas_distintas_dt(a, b)


def forma_dt(nombre: str) -> str:
    """Cómo escribe la fuente al DT: «inicial» («W. Ribonetto», «G. Huerta») o
    «completo» («Davis Gonzalez», «Gustavo Huerta»). Un cambio de forma en el
    banco de un equipo es un cambio de FUENTE de la API, no una llegada
    (incidencias 1100 y 1123: la liga chilena pasó el 10/10/2026 de «Gustavo
    Huerta» a «G. Huerta», y en Everton y La Serena el nombre de antes era
    otro: Ribonetto y Gutiérrez salían «DT nuevo desde 2026-10-11»)."""
    partes = plano(nombre).split()
    if not partes:
        return ""
    return "inicial" if len(partes) > 1 and len(partes[0]) == 1 else "completo"


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
    if pilas_distintas_dt(a, b):
        return False   # dos pilas enteras distintas son dos personas (1096)
    if ta[-1] in tb or tb[-1] in ta:
        return True
    if any(apellido_casi(x[-1], y) for x, ys in ((ta, tb), (tb, ta)) for y in ys):
        return True
    return len(set(ta) & set(tb)) >= 2
