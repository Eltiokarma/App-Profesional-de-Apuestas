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
                   ("emmanuel", "emanuel", "449, letra doble"),
                   ("barbopoulos", "barmpopoulos", "1306, μπ griega: mp ↔ b")]:
    check(f"apellido casi: «{a}» / «{b}» ({caso})", idn.apellido_casi(a, b))
for a, b, caso in [("martinez", "martino", "dos letras"), ("rojas", "rojo", "corto"), ("sosa", "sossa", "corto"),
                   ("berrios", "beros", "dos letras de menos"),
                   ("mientras", "martinez", "1256: un anagrama entero de una palabra de la prosa")]:
    check(f"apellido distinto: «{a}» / «{b}» ({caso})", not idn.apellido_casi(a, b))

# ── el mismo jugador ──────────────────────────────────────────────────────────
for a, b, caso in [("S. Peña", "S. Pena", "Nacional Potosí"), ("E. Griffa", "Emiliano Griffa", "Leones del Norte"),
                   ("Y. Guzmán", "Y. Guzman", "839, América"), ("Luan Patrick", "Patrick Luan", "502, Estrela"),
                   ("J. Berríos", "J. Berios", "856"),
                   ("Apostolos Barbopoulos", "Apostolos Barmpopoulos", "1306, Aris")]:
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
check("893: «A. Torrez» es «A. W. Torrez Suarez» (el corto lleva el primer apellido)",
      idn.mismo_jugador("A. Torrez", "A. W. Torrez Suarez") and idn.mismo_jugador("A. W. Torrez Suarez", "A. Torrez"))
check("893: el apellido del corto tiene que estar en el largo y la pila cuadrar",
      not idn.mismo_jugador("A. Romero", "A. W. Torrez Suarez") and not idn.mismo_jugador("B. Torrez", "A. W. Torrez Suarez"))
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
check("951: «Pacheta» es «José Rojo Martín» (apodo conocido del DT)",
      idn.mismo_dt("Pacheta", "José Rojo Martín") and idn.mismo_nombre_dt("Pacheta", "José Rojo Martín"))
check("811: la «ð» es «d» en la normalización que usan todos (Guðmundsson = Gudmundsson)",
      idn.plano("A. Guðmundsson") == idn.plano("A. Gudmundsson"))
from backend.analisis import dtp_cowork as _dtp811  # noqa: E402
check("811: el ejecutor «A. Gudmundsson» se reconoce en una línea que dice «Guðmundsson»",
      _dtp811._nombra_ejecutor("penal: Guðmundsson (3 de 3)", ["A. Gudmundsson"]))
check("DT: «Gustavo Alfaro» no es «Ricardo Gareca»", not idn.mismo_dt("Gustavo Alfaro", "Ricardo Gareca")
      and not idn.mismo_nombre_dt("Gustavo Alfaro", "Ricardo Gareca"))
check("1096: «Héctor Ignacio Rodríguez Peña» no es «Andrés Rodríguez» (dos pilas enteras distintas)",
      not idn.mismo_dt("Héctor Ignacio Rodríguez Peña", "Andrés Rodríguez")
      and not idn.mismo_nombre_dt("Héctor Ignacio Rodríguez Peña", "Andrés Rodríguez"))
check("1096: con la inicial o la pila dentro de la otra sigue casando (A. Rodríguez, Pep/Josep, Ricardo Silva)",
      idn.mismo_dt("A. Rodríguez", "Andrés Rodríguez") and idn.mismo_nombre_dt("Pep Guardiola", "Josep Guardiola Sala")
      and idn.mismo_nombre_dt("Ricardo Silva", "Ricardo Jorge Ferreira Pinto da Silva")
      and idn.mismo_nombre_dt("Luis Enrique", "Enrique Luis")
      and idn.mismo_nombre_dt("Victor Manuel Vucetich", "Manuel Vucetich Rojas Victor"))
check("1100/1123: la forma del nombre del DT (inicial o completo)",
      idn.forma_dt("W. Ribonetto") == "inicial" and idn.forma_dt("Davis Gonzalez") == "completo"
      and idn.forma_dt("Ribonetto") == "completo")

# ── los módulos usan ESTA regla, no una copia ────────────────────────────────
from backend.analisis import bloque_f, dtp_cowork, f1_base, parte  # noqa: E402
from backend.ingesta import jugadores  # noqa: E402
check("bloque_f, f1_base, dtp_cowork, parte e ingesta/jugadores apuntan a identidad",
      bloque_f._casa is idn.casa and bloque_f._tokens is idn.tokens and f1_base.mismo_jugador is idn.mismo_jugador
      and f1_base._casi_igual is idn.apellido_casi and dtp_cowork._casi is idn.apellido_casi
      and dtp_cowork._plano is idn.plano and parte.mismo_dt is idn.mismo_dt
      and jugadores.mismo_nombre_dt is idn.mismo_nombre_dt and jugadores._casi_igual is idn.apellido_casi)

# ── mantenimiento del 02/11/2026 (grupo identidad-jugador) ───────────────────
# 1077 (San Lorenzo): la pila compuesta, en la regla y en el bloque F
check("1077: «Nahuel Arias» es «Óscar Nahuel Arias» (la segunda pila del largo)",
      idn.mismo_jugador("Nahuel Arias", "Óscar Nahuel Arias") and idn.mismo_jugador("Óscar Nahuel Arias", "Nahuel Arias")
      and not idn.mismo_jugador("Pedro Arias", "Óscar Nahuel Arias"))
check("1077: «O. Arias» PUEDE ser «Nahuel Arias» (inicial de una primera pila que la tabla no escribe); "
      "«N. Arias» no entra por acá (ya casa) y otro apellido tampoco",
      idn.pila_compuesta_posible(T("Nahuel Arias"), T("O. Arias"))
      and not idn.pila_compuesta_posible(T("Nahuel Arias"), T("N. Arias"))
      and not idn.pila_compuesta_posible(T("Nahuel Arias"), T("O. Arce")))
_pl1077 = [{"nombre": "J. Devecchi", "jugadorId": 6595, "zona": "GK", "rol": "TF"},
           {"nombre": "Nahuel Arias", "zona": "MID", "rol": "TH"},
           {"nombre": "G. Alassia", "jugadorId": 296488, "zona": "MID", "rol": "TH"}]
_r1077 = bloque_f.resolver(_pl1077, [], ["J. Devecchi", "O. Arias"], [], {"J. Devecchi": 6595, "O. Arias": 414527})
_e1077 = {x["nombre"]: (x["estado"], x.get("hoja"), x.get("porPilaCompuesta")) for x in _r1077["jugadores"]}
check("1077: el bloque F casa «O. Arias» con «Nahuel Arias» (sin id, apellido único) y no suena ONCE-SIN-FILA-F1",
      _e1077["Nahuel Arias"] == ("disponible", "titular", "O. Arias") and not _r1077["noReconocidosOnce"], _r1077)
_r1077b = bloque_f.resolver([*_pl1077, {"nombre": "Martín Arias", "zona": "DEF", "rol": "ROT"}], [],
                            ["J. Devecchi", "O. Arias"], [], {"J. Devecchi": 6595})
check("1077: con dos Arias en la tabla no se adivina (390: «K. Álvarez» no es «Carlos Álvarez»)",
      _r1077b["noReconocidosOnce"] == ["O. Arias"], _r1077b["noReconocidosOnce"])
_r1077c = bloque_f.resolver([{**_pl1077[1], "jugadorId": 999}], [], ["O. Arias"], [], {"O. Arias": 414527})
check("1077: una fila CON otro id no casa por la pila compuesta", _r1077c["noReconocidosOnce"] == ["O. Arias"], _r1077c)
_r1077d = bloque_f.resolver(_pl1077, [], ["J. Devecchi", "O. Arias"], ["N. Arias"], {"J. Devecchi": 6595})
check("1077: si la hoja trae también a «N. Arias», «Nahuel Arias» es ese y «O. Arias» queda sin fila",
      {x["nombre"]: x.get("hoja") for x in _r1077d["jugadores"]}["Nahuel Arias"] == "banca"
      and _r1077d["noReconocidosOnce"] == ["O. Arias"], _r1077d)

# 1107 (Los Chankas): dos pilas enteras distintas no se funden por la inicial
check("1107: «Ángel Gonzales» y «D. Gonzáles» (hoja «David Gonzales») tienen pilas enteras distintas",
      idn.pilas_enteras_distintas(["Ángel Gonzales"], ["D. Gonzáles", "David Gonzales"])
      and not idn.pilas_enteras_distintas(["Ángel Gonzales"], ["D. Gonzáles"])
      and not idn.pilas_enteras_distintas(["Juan Bizans"], ["F. Bisanz", "Juan Francisco Bisanz"]))
_gz = [{"id": 101280, "nombre": "Ángel Gonzales", "minutos": 1800, "partidos": 22, "goles": 1, "asistencias": 0},
       {"id": 107017, "nombre": "D. Gonzáles", "minutos": 213, "partidos": 4, "goles": 1, "asistencias": 0}]
_g1, _ = f1_base.deduplicar(_gz, {}, lambda a, b: False, lambda a, b: True)
_g2, _ = f1_base.deduplicar(_gz, {}, lambda a, b: False, lambda a, b: True,
                            nombres={107017: ["David Gonzales"], 101280: ["Ángel Gonzales"]})
check("1107: sin el nombre de la hoja la inicial funde (673); con «David Gonzales» en la hoja quedan dos filas",
      len(_g1) == 1 and len(_g2) == 2 and not any(r.get("fundidoPorInicial") for r in _g2), (_g1, _g2))

# 1111 (Boston River) y 1094 (Cercle, Twente): el aviso de `equipos.fuera`
check("1241: «Gabriel Justino» nombra a «João Gabriel Castro Santos» solo como pila de otro; «Gabriel» suelto o «Castro Santos», no",
      idn.solo_como_pila_de_otro("João Gabriel Castro Santos", "Gabriel Justino")
      and not idn.solo_como_pila_de_otro("João Gabriel Castro Santos", "entra Gabriel por la izquierda")
      and not idn.solo_como_pila_de_otro("João Gabriel Castro Santos", "João Gabriel Castro Santos de central")
      and not idn.solo_como_pila_de_otro("João Gabriel Castro Santos", "Gabriel, Justino y Scarpa")
      and not idn.solo_como_pila_de_otro("João Gabriel Castro Santos", "Scarpa en el balón parado"))
check("1236: «Felipe Anderson» no menciona a «Matheus Felipe»; «Felipe» suelto, «Matheus Felipe» y «Felipe, Anderson» sí",
      not idn.menciona("Matheus Felipe", "Flaco López y Felipe Anderson en el banco")
      and not idn.menciona("Matheus Felipe", "Felipe Anderson entra por la izquierda")
      and idn.menciona("Matheus Felipe", "entra Felipe por la derecha")
      and idn.menciona("Matheus Felipe", "Matheus Felipe desde el banco")
      and idn.menciona("Matheus Felipe", "en el banco Felipe, Anderson y Gómez")
      and idn.menciona("Matheus Felipe", "recambio: Felipe."))
check("1111: «N. da Silva» no menciona a «K. Silva»; «K. Silva», «Kevin Silva» y «Silva» suelto sí",
      not idn.menciona("K. Silva", "N. da Silva desde el banco")
      and idn.menciona("K. Silva", "K. Silva desde el banco") and idn.menciona("K. Silva", "entra Kevin Silva")
      and idn.menciona("K. Silva", "entra Silva por la derecha") and idn.menciona("K. Silva", "Silva entra"))
_p1111 = {"equipos": {"a": {"fuera": [{"nombre": "K. Silva", "estado": "baja"}]}},
          "dtp": {"bloques": [{"equipo": "a", "apertura": {"m6": {"recambio": "N. da Silva en el banco"}}}]}}
check("1111: el sancionado «K. Silva» no se avisa por el «N. da Silva» del banco", parte.fuera_en_el_banco(_p1111) == [])
_p1094 = {"equipos": {"a": {"fuera": [{"nombre": "A. Vanzeir", "estado": "baja"}]}},
          "dtp": {"bloques": [{"equipo": "a", "apertura": {"m1": {
              "senalXi": "entra Mondele por Vanzeir (roja directa ante el Genk)"}}}]}}
_p1094b = {"equipos": {"a": {"fuera": [{"nombre": "A. Vanzeir", "estado": "baja"}]}},
           "dtp": {"bloques": [{"equipo": "a", "apertura": {"m1": {"senalXi": "entra Vanzeir desde el banco"}}}]}}
check("1094: «entra Mondele por Vanzeir» no cuenta con Vanzeir (el que sale); «entra Vanzeir» sí se avisa",
      parte.fuera_en_el_banco(_p1094) == [] and len(parte.fuera_en_el_banco(_p1094b)) == 1,
      (parte.fuera_en_el_banco(_p1094), parte.fuera_en_el_banco(_p1094b)))

# 1076 (Monagas): dos «A. Romero» en la misma hoja son dos personas
_r1076 = bloque_f.resolver([{"nombre": "A. Romero", "jugadorId": 159161, "zona": "MID", "rol": "TH"}], [],
                           ["A. Romero"], ["A. Romero"], {"A. Romero": [159161, 53129]})
check("1076: el titular casa por su id (159161) y el suplente homónimo (53129) no se suma a su fila",
      [(x["estado"], x.get("hoja")) for x in _r1076["jugadores"]] == [("disponible", "titular")]
      and _r1076["noReconocidos"] == ["A. Romero"], _r1076)
_rm, _ = f1_base.deduplicar([{"id": 159161, "nombre": "A. Romero", "minutos": 900, "partidos": 10},
                             {"id": 53129, "nombre": "A. Romero", "minutos": 0, "partidos": 0}], {},
                            lambda a, b: True)
check("1076: la copia sin minutos que COMPARTIÓ hoja con el otro id no se funde (1039)", len(_rm) == 2, _rm)

# 1331 (08/11/2026, U. Católica–Deportes Limache): el apellido con guion es el mismo pegado
check("1331: «T. Asta-Buruaga» de la tabla casa con «Tomas Astaburuaga» de la ficha, en los dos sentidos",
      idn.casa(idn.tokens("T. Asta-Buruaga"), idn.tokens("Tomas Astaburuaga"))
      and idn.casa(idn.tokens("Tomas Astaburuaga"), idn.tokens("T. Asta-Buruaga"))
      and idn.mismo_jugador("T. Asta-Buruaga", "Tomas Astaburuaga"))
check("1331: con otra pila no casa, y dos apellidos sueltos distintos tampoco",
      not idn.casa(idn.tokens("T. Asta-Buruaga"), idn.tokens("Mario Astaburuaga"))
      and not idn.mismo_jugador("Juan Perez", "Juan Lopez"))
_r1331 = bloque_f.resolver([{"nombre": "T. Asta-Buruaga", "zona": "DEF", "rol": "TH"}], [],
                           ["Tomas Astaburuaga"], ["Tomas Astaburuaga"], {})
check("1331: el bloque F lo cuenta titular, no «no figura en la hoja»",
      [(x["estado"], x.get("hoja")) for x in _r1331["jugadores"]] == [("disponible", "titular")], _r1331)

# 1337 (08/11/2026, La Guaira–Carabobo): «Loureins Martínez» del rival no es el sancionado «L. Martinez»
_p1337 = {"equipos": {"a": {"fuera": [{"nombre": "L. Martinez", "estado": "baja"}]},
                      "b": {"plantel": [{"nombre": "Loureins Martínez", "zona": "ATK"}]}},
          "dtp": {"bloques": [{"equipo": "a", "apertura": {"m2": {"duelos": "entra Loureins Martínez desde el banco"}}}]}}
_p1337b = {"equipos": {"a": {"fuera": [{"nombre": "L. Martinez", "estado": "baja"}]}, "b": {"plantel": []}},
           "dtp": {"bloques": [{"equipo": "a", "apertura": {"m2": {"duelos": "entra L. Martinez desde el banco"}}}]}}
check("1337: la mención que también nombra a un jugador del rival no se avisa; sin ese rival, sí",
      parte.fuera_en_el_banco(_p1337) == [] and len(parte.fuera_en_el_banco(_p1337b)) == 1,
      (parte.fuera_en_el_banco(_p1337), parte.fuera_en_el_banco(_p1337b)))

# 1347 (10/11/2026, Olympiakos–PAOK): la raya «–» entre dos nombres los separa
check("1347: «Puerta–Freuler» son dos palabras y menciona a Puerta",
      idn.plano("Puerta–Freuler").split() == ["puerta", "freuler"]
      and idn.menciona("D. Puerta", "doble pivote Puerta–Freuler fijo")
      and idn.plano("Asta-Buruaga").split() == ["asta", "buruaga"] and idn.plano("Hoeneß") == "hoeness")

# 1225 (10/11/2026, FUERA-EN-LA-HOJA): «Castillo» suelto con E. Castillo titular y
# J. Castillo en el banco no tiene dueño; «J. Castillo» o «Adamo» sí
check("1225: la mención de un apellido que también es de otro de la hoja queda sin dueño",
      idn.mencion_compartida("E. Castillo", ["J. Castillo"], "Castillo")
      and not idn.mencion_compartida("E. Castillo", ["J. Castillo"], "E. Castillo")
      and not idn.mencion_compartida("V. Adamo", ["J. Castillo"], "Adamo"))
# 1330 (10/11/2026, aprobada): la hoja trae el id de uno con el nombre de OTRO de la plantilla
_pl1330 = {305596: "Krisztian Paraszhidisz", 527180: "P. Preciado", 64215: "S. Córdoba"}
check("1330: «P. Preciado» con el id 305596 (Paraszhidisz) es el 527180",
      idn.id_cruzado("P. Preciado", 305596, _pl1330) == 527180)
check("1330: el nombre del dueño, otro nombre que nadie lleva, un dueño desconocido o una sola palabra: el id manda",
      idn.id_cruzado("K. Paraszhidisz", 305596, _pl1330) is None
      and idn.id_cruzado("Dayan Pérez", 305596, _pl1330) is None
      and idn.id_cruzado("P. Preciado", 999, _pl1330) is None
      and idn.id_cruzado("Preciado", 305596, _pl1330) is None)
check("1330: dos candidatos por nombre no se afirman",
      idn.id_cruzado("P. Preciado", 305596, {**_pl1330, 1: "Pablo Preciado"}) is None)
check("1330: mismo apellido sin mirar la pila («Jose» / «Jesús Sagredo»); otro apellido, no",
      idn.mismo_apellido("Jose Sagredo", "Jesús Sagredo") and not idn.mismo_apellido("Jose Sagredo", "Jose Sagasti"))

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
