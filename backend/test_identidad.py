"""La identidad de un jugador o un DT, en un solo lugar (backend/identidad.py).

Cada caso es una incidencia real. Un caso nuevo de nombres se agrega ACÁ y
vale para el bloque F, la tabla F1, contraElOnce, el DT del parte y la ingesta
a la vez; antes cada módulo tenía su versión y el mismo error volvía por otro.

    python -m backend.test_identidad
"""
import sys

from backend import identidad as idn

fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


# ── normalización ─────────────────────────────────────────────────────────────
check("la ß se convierte, no se tira («Hoeneß» → hoeness)", idn.plano("Sebastian Hoeneß").split() == ["sebastian", "hoeness"])
check("la ø y la ł se convierten («Ødegaard», «Łukasz»)",
      idn.tokens("Martin Ødegaard") == ["martin", "odegaard"] and idn.tokens("Łukasz Fabiański") == ["lukasz", "fabianski"])
check("el apóstrofo une («N'Diaye» = «Ndiaye», 653)", idn.tokens("A. N'Diaye") == ["a", "ndiaye"])
check("las partículas no identifican («Alexis Mac Allister», «Van Dijk»)",
      idn.tokens("Virgil van Dijk") == ["virgil", "dijk"])
check("el mojibake de la API se limpia antes («R. ObriÄ\x87» = «R. Obrić»)",
      idn.tokens("R. ObriÄ\u0087") == idn.tokens("R. Obrić"), idn.tokens("R. ObriÄ\u0087"))
check("los dígitos se conservan (hojas de prueba «Jugador10»)", idn.tokens("A Jugador10") == ["a", "jugador10"])

# ── el apellido escrito distinto ─────────────────────────────────────────────
for a, b, caso in [("berrios", "berios", "856, Carabobo"), ("zampiero", "zampieri", "223, Torque"),
                   ("quiros", "quiroz", "seseo, Atlas"), ("bizans", "bisanz", "Huracán, letras cambiadas"),
                   ("balazar", "bazalar", "Los Chankas, DT"), ("hoeness", "hoeneb", "ß mal codificada, Stuttgart"),
                   ("emmanuel", "emanuel", "449, letra doble")]:
    check(f"apellido casi: «{a}» / «{b}» ({caso})", idn.apellido_casi(a, b))
for a, b, caso in [("martinez", "martino", "dos letras"), ("rojas", "rojo", "corto"), ("sosa", "sossa", "corto"),
                   ("berrios", "beros", "dos letras de menos")]:
    check(f"apellido distinto: «{a}» / «{b}» ({caso})", not idn.apellido_casi(a, b))

# ── el mismo jugador ──────────────────────────────────────────────────────────
for a, b, caso in [("S. Peña", "S. Pena", "Nacional Potosí"), ("E. Griffa", "Emiliano Griffa", "Leones del Norte"),
                   ("Y. Guzmán", "Y. Guzman", "839, América"), ("Luan Patrick", "Patrick Luan", "502, Estrela"),
                   ("J. Berríos", "J. Berios", "856")]:
    check(f"mismo jugador: «{a}» / «{b}» ({caso})", idn.mismo_jugador(a, b))
for a, b, caso in [("J. Bisanz", "F. Bisanz", "otra inicial: la decide f1_base con más datos"),
                   ("Juan Bisanz", "Pedro Bisanz", "dos pilas enteras: hermanos"),
                   ("Neymar", "Neymar da Silva Santos Júnior", "una sola palabra no alcanza")]:
    check(f"no se afirma: «{a}» / «{b}» ({caso})", not idn.mismo_jugador(a, b))

# ── la hoja contra la tabla ──────────────────────────────────────────────────
T = idn.tokens
check("«A. Campos» casa con «Ángelo Campos»", idn.casa(T("Ángelo Campos"), T("A. Campos")))
check("«Campos» solo casa con «Ángelo Campos»", idn.casa(T("Ángelo Campos"), T("Campos")))
check("«Saúl» (solo la pila) casa con «Saúl Ñíguez»", idn.casa(T("Saúl Ñíguez"), T("Saúl")))
check("«PH Ganso» casa con «Paulo Henrique Ganso» (la pila en iniciales)",
      idn.casa(T("Paulo Henrique Ganso"), T("PH Ganso")))
check("937: «Fran Lopez» casa con «Francisco López» (diminutivo de la lista)",
      idn.casa(T("Francisco López"), T("Fran Lopez")) and idn.mismo_jugador("Fran Lopez", "Francisco López"))
check("887/893: «Rafa Llorente» es «Rafael Llorente» y «R. Llorente»",
      idn.mismo_jugador("Rafa Llorente", "Rafael Llorente") and idn.mismo_jugador("Rafa Llorente", "R. Llorente"))
check("el diminutivo es una lista cerrada: «Joselu Mato» no es «José Mato», «Juanjo Pérez» no es «Juan Pérez»",
      not idn.mismo_jugador("Joselu Mato", "José Mato") and not idn.mismo_jugador("Juanjo Pérez", "Juan Pérez"))
check("«Fran» no es «Rafael» (diminutivo de otra pila)", not idn.mismo_jugador("Fran García", "Rafael García"))
check("«K. Álvarez» no casa con «Carlos Álvarez» (otra inicial, 390)", not idn.casa(T("Carlos Álvarez"), T("K. Álvarez")))
check("«Danilo» es solo la pila de «Danilo Santos» (855)", idn.solo_pila(T("Danilo Santos"), T("Danilo")))

# ── el mismo jugador con dos ids entre hojas (899) ──────────────────────────
_eq = idn.ids_equivalentes({1: "Lautaro Herrera", 2: "J. Pérez", 3: "Otro Uno"},
                           {9: "Lautaro Herrera", 2: "J. Pérez", 8: "Nuevo Dos"})
check("899: «Lautaro Herrera» con otro id en la hoja anterior es el mismo; el que se fue de verdad, no",
      _eq == {1: 9}, _eq)
check("899: con dos candidatos por nombre no se afirma nada",
      idn.ids_equivalentes({1: "J. Díaz"}, {5: "Juan Díaz", 6: "José Díaz"}) == {})

# ── el DT ────────────────────────────────────────────────────────────────────
check("DT: «M. Pellegrino» = «Mauricio Pellegrino»", idn.mismo_dt("M. Pellegrino", "Mauricio Pellegrino"))
check("DT: «S. Hoeneb» = «Sebastian Hoeneß» (ß corrupta)", idn.mismo_dt("S. Hoeneb", "Sebastian Hoeneß")
      and idn.mismo_nombre_dt("S. Hoeneb", "Sebastian Hoeneß"))
check("DT: «Manuel Luis Pellegrini Ripamonti» = «M. Pellegrini» (apellido materno al final)",
      idn.mismo_nombre_dt("Manuel Luis Pellegrini Ripamonti", "M. Pellegrini"))
check("DT: «J. Balazar» = «Juan Carlos Bazalar»", idn.mismo_nombre_dt("J. Balazar", "Juan Carlos Bazalar"))
check("DT: «Gustavo Alfaro» no es «Ricardo Gareca»", not idn.mismo_dt("Gustavo Alfaro", "Ricardo Gareca")
      and not idn.mismo_nombre_dt("Gustavo Alfaro", "Ricardo Gareca"))

# ── los módulos usan ESTA regla, no una copia ────────────────────────────────
from backend.analisis import bloque_f, dtp_cowork, f1_base, parte  # noqa: E402
from backend.ingesta import jugadores  # noqa: E402
check("bloque_f, f1_base, dtp_cowork, parte e ingesta/jugadores apuntan a identidad",
      bloque_f._casa is idn.casa and bloque_f._tokens is idn.tokens and f1_base.mismo_jugador is idn.mismo_jugador
      and f1_base._casi_igual is idn.apellido_casi and dtp_cowork._casi is idn.apellido_casi
      and dtp_cowork._plano is idn.plano and parte.mismo_dt is idn.mismo_dt
      and jugadores.mismo_nombre_dt is idn.mismo_nombre_dt and jugadores._casi_igual is idn.apellido_casi)

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
