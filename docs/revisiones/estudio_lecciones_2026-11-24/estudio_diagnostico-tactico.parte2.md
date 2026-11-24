# DTP v1.9 · lecciones pendientes del 21 al 23/11/2026 (parte 2 de 2)

**Insumo:** 267 lecciones de 72 partidos (63 del 21/11, 196 del 22/11, 8 del 23/11). Todas son `ciega` + `PRE`, sin cuarentena y posteriores a la v1.9: ninguna es del 17/11. **29 lecciones (12 partidos) son de copa**, de la Taça de Portugal del 21 y el 22/11. Quedan **238 acreditables de 60 partidos**. `modoFallo` viene vacío en las 267, así que Jev no aporta nada a esta parte. La clasificación por lección está en `clasif_diagnostico-tactico.parte2.json`, en el orden del archivo de entrada.

## 1. Conteo

| Clase | Todas (267) | Sin copa (238) |
|---|---|---|
| regla_sostuvo | 151 | 138 |
| mal_aplicada | 70 | 65 |
| regla_fallo | 29 | 26 |
| insumo | 8 | 4 |
| imprevisto | 1 | 1 |
| otro_skill | 0 | 0 |
| no_dice | 8 | 4 |

Por veredicto del lado:

- **acierto (159):** 102 sostuvo, 28 mal aplicada, 15 falló, 7 insumo, 6 no dice, 1 imprevisto.
- **parcial (14):** 6 sostuvo, 7 mal aplicada, 1 falló.
- **fallo (94):** 43 sostuvo, 35 mal aplicada, 13 falló, 2 no dice, 1 insumo.

Como en la v1.8, el veredicto del lado no dice si la regla funcionó: en los lados fallados hay 43 lecciones donde la regla se sostuvo. Por cada regla que falló hay **2,4 mal aplicadas** (70 contra 29), la misma proporción que el 17/11. El problema sigue siendo que no se cumple lo que ya está escrito.

## 2. Tabla por regla

| Regla | n | partidos | copa | sostuvo | mal aplic. | falló | insumo | imprev. | no dice |
|---|---|---|---|---|---|---|---|---|---|
| M5 · veredicto contra lo concedido | 61 | 41 | 0 | 39 | 0 | 21 | 0 | 1 | 0 |
| M2 · banco ofensivo (lista, todas las ramas, sin minuto, razón) | 29 | 28 | 6 | 15 | 11 | 0 | 1 | 0 | 2 |
| M2 · viasGol (otros renglones de la lista) | 23 | 20 | 0 | 15 | 8 | 0 | 0 | 0 | 0 |
| M2 · ejecutor de penales | 21 | 18 | 1 | 19 | 0 | 2 | 0 | 0 | 0 |
| Checklist del bloque (pregunta 6, vida útil) | 17 | 16 | 2 | 15 | 1 | 1 | 0 | 0 | 0 |
| M2 · veredicto de rama (ceder/tener, quién remata, sin vía, sobrevive) | 15 | 13 | 1 | 6 | 9 | 0 | 0 | 0 | 0 |
| MECANISMO-ABIERTO | 15 | 14 | 2 | 15 | 0 | 0 | 0 | 0 | 0 |
| M1 · grid, XI de referencia, rehacer, dos capas | 14 | 13 | 6 | 1 | 6 | 1 | 5 | 0 | 1 |
| M2 · vía de expulsión | 13 | 11 | 0 | 6 | 5 | 0 | 2 | 0 | 0 |
| M3 · quién queda atrás, rearme, fases | 11 | 10 | 3 | 6 | 4 | 1 | 0 | 0 | 0 |
| M5 · la referencia de volumen no viaja | 7 | 7 | 0 | 0 | **7** | 0 | 0 | 0 | 0 |
| Ramas por número (no puesta a prueba) | 7 | 5 | 0 | 7 | 0 | 0 | 0 | 0 | 0 |
| M2 · mismatch contra reconvertido o línea nueva | 6 | 6 | 1 | 2 | 4 | 0 | 0 | 0 | 0 |
| M2 · pelota parada (materia del cruce, tiro libre directo) | 6 | 6 | 2 | 1 | 5 | 0 | 0 | 0 | 0 |
| M2 · veredicto con condición escribe su contrario | 5 | 5 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| M2 · el reconvertido también ataca (v1.9) | 3 | 3 | 0 | 2 | 1 | 0 | 0 | 0 | 0 |
| M2 · posesión por rama | 3 | 2 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |

El resto suma 14 lecciones:

- otros (M4, M6, rest defense, cadena): 6;
- M5 sin stats: 3, todas `no_dice`, 2 de copa;
- nombre en el XI y en el banco: 2, las dos mal aplicadas.

**Lo que funciona:**

- **MECANISMO-ABIERTO:** 15 de 15.
- **Ramas por número:** 7 de 7.
- **Penales:** 19 de 21. La regla nueva de la v1.9, «con la base corta, el 9 titular entra en la lista», se cumplió en Frankfurt 1575223, Lommel 1558687, Kasımpaşa 1584471 y Racing 1570459, y no hay ninguna mal aplicada.
- **Pregunta 6 y vida útil:** 15 de 17.
- **El cierre del M5** aplica bien la vara: separa la conversión, pone el penal al lado del xG y no sube un veredicto por el marcador.

## 3. Patrones con ≥ 3 partidos distintos

### A. Hacer cumplir una regla que ya está escrita (no tocan números)

**A1. La referencia de volumen no viaja: 7 de 7 mal aplicadas, en 7 partidos.** La rama se apoya en un xG que no viene de la condición de hoy:

- de un solo partido de otra sede: Le Mans 1552822, Vila Nova 1650247 y Huracán 1649568;
- de la temporada o de los últimos 10 sin separar la sede: Schalke 1575228, América 1551044 y Levadiakos 1593361;
- de la temporada con un DT nuevo: Volos 1593364.

En los 7 casos el volumen del día desmintió la referencia. Es una regla de la v1.8 y el 17/11 tenía solo 3 casos: **sube**. **Para la app:**

- los insumos dan la referencia de volumen por sede y condición, con su `n`;
- el recibo avisa cuando la razón de una rama cita un xG de un solo partido o de la temporada.

Reescribir la regla no corta el patrón.

**A2. El veredicto con condición escribe su contrario: 4 mal aplicadas, en 4 partidos.**

- Gladbach 1575226, Cali 1650174 y OH Leuven 1558680 escribieron la línea contraria, pero publicaron la favorable.
- Metropolitanos 1646938 ni siquiera escribió la contraria.
- Se suma América 1551044, que va contado en A1.

La v1.8 manda que, si la condición no depende del foco, se publique la línea menos favorable. En los cuatro casos se jugó justo esa línea. El 17/11 había 1 caso: **sube**. **Para la app:** el parte ya tiene el campo de la línea contraria. Si existe y es menos favorable, el recibo exige que el veredicto de la rama sea el suyo. Es un chequeo mecánico.

**A3. Vía de expulsión con toda la línea del duelo: 5 mal aplicadas y 2 por insumo, en 7 partidos.**

- **Mal aplicadas:** Hoffenheim 1575223, Willem II 1552232, Villarreal 1570455, Kifisia 1593365 y Atlético Nacional 1650176. En los cinco se nombró al pivote o a un solo amonestado, y la roja fue de un central o lateral de la línea, a veces con sus amarillas ya en la F1.
- **Insumo:**
  - Pumas 1551043: el expulsado arrancó por el once tardío;
  - Getafe 1570456: Djené figuraba como «D. Dakonam» en la API y el parte lo dio fuera de la hoja.
- **Sostuvo en 6.**

El 17/11 había 4 lecciones: **sube**. **Para la app:**

- listar en los insumos del DTP, por cada duelo, las piezas de la línea con `amarillasEnLaCompeticion` y la roja reciente (la F1 ya lo trae);
- agregar el caso Djené/Dakonam a `backend/identidad.py`, con su test.

**A4. Banco ofensivo: 13 mal aplicadas, en 13 partidos.** Incluye las 2 de «nombre en el XI y en el banco», 3 de copa. Sostuvo en 15. Las formas del error cambiaron:

- **«desde el 60'» o con minuto fijo:** Samsunspor 1584469, Juventus 1550201, Paris FC 1552825 y Mushuc Runa 1639837. Es la forma nueva dominante.
- **Un nombrado como banco fue titular (FUERA-EN-LA-HOJA):** Mainz 1575224, Gimnasia M. 1649570, AZ 1552230 y La Guaira 1646938 (este con un nombre en el xiReferencia y en el banco a la vez). Los cuatro tuvieron el once tardío o sin capturar.
- **La razón de la rama recorta la lista:** Panetolikos 1593364 y Vila Nova 1650247.
- **Banco solo en «persiguiendo»:** The Strongest 1645546.
- **Lista incompleta:** el lateral fresco en AZ; de copa, Estoril 1647581 y Benfica 1647592 («los conocidos», con uno que no estaba en la hoja).

Juicio sobre `bancoProbable`:

- Ninguna lección dice que la lista de la app viniera mal.
- Donde se copió entera, el banco marcó: Hoffenheim, Nacional Potosí, Twente, Liverpool, Beşiktaş, Olympiakos, Always Ready y Atlético.
- Los errores que quedan son de dos tipos:
  - **del analista:** el minuto, el recorte y «solo persiguiendo»;
  - **de la apertura con el once probable,** que la hoja corrige tarde. Ahí `bancoProbable` sale del xiReferencia y hereda su error.

**Para la app:**

- un aviso en el recibo para un minuto en la línea del banco (por ejemplo «desde el NN'»);
- que la razón de cada rama copie la lista entera, o la cite por renglón.

Al rehacer, FUERA-EN-LA-HOJA ya está. **Se repite** (17/11: 16 en 15), con una mezcla de formas distinta.

**A5. Veredicto de rama: ceder o tener, quién remata, sin vía, sobrevive a los cambios. 9 mal aplicadas, en 8 partidos.**

- **Ceder o tener la pelota usado como señal:** Kocaelispor 1584472, Hull 1557472 y Atromitos 1593361.
- **FAVORABLE por zona sin quién remata, o con el rematador fuera:**
  - Fenerbahçe 1584472;
  - Gent 1558681;
  - LDU 1639807;
  - Bolívar 1645545, donde el H del mismo parte ya decía NEUTRO.
- **Banco solo como vía:** Kalamata 1593360, donde el ejemplo de Emelec ya está escrito.
- **Sin decir qué vía queda tras los cambios:** Lommel 1558687.

Todo eso está escrito en la v1.7 y la v1.8: **se repite** (17/11: ceder en 4 partidos). **Para la app:** el aviso «la razón cita sus vías por renglón», que sigue pendiente. Un FAVORABLE sin rematador nombrado en la razón se puede detectar.

**A6. viasGol, renglón 6: el que llega figura solo como centrador o asistidor. 4 mal aplicadas, en 4 partidos.**

- Juventus 1550201: el lateral Cabal hizo el 3-0.
- Chivas 1551045: llegó el extremo y no el carrilero nombrado.
- Aucas 1639807: el interior Guzmán.
- Necaxa 1551046: el extremo y el pivote reasignado.
- Se suma Frankfurt 1575223, la regla v1.9 del reconvertido que ataca: Knauff, nombrado solo por su espalda, asistió el gol.

Fuera del renglón 6, hay mal aplicadas sueltas, una por renglón:

- media distancia: Racing 1570459;
- pelota sucia con los centrales: Manta 1639836;
- quinta línea con sus dos condiciones: Atlético Goianiense 1650247;
- P2 del arquero: Trabzonspor 1584474. Se listó como vía a un arquero suplente sin sus ≥ 2 intervenciones fallidas, y atajó 8.

**Qué haría:**

- **aclarar en el skill, una línea de forma:** nombrar a un jugador en un renglón (centrador, asistidor, pieza) no lo saca del renglón 6. Cada titular de banda y de segunda línea va también como llegada, con su zona;
- **para la app:** cruzar los titulares de banda del grid contra los nombres del renglón 6.

**A7. Pelota parada: 5 mal aplicadas, en 5 partidos.**

- **Materia desde el promedio propio y no del cruce:** Lorient 1552821, Werder 1575227 y Gent 1558681 (condicional por «cede»). Es la regla 4 de la v1.9, recién escrita y ya incumplida 3 veces.
- **Falta el lanzador de tiro libre directo:** Tigres 1551044 (gol en el 90+1) y Mafra 1647586, de copa.

**Para la app:** traer en los insumos los córners que concede el rival por sede. Sin el número a la vista, el analista vuelve al promedio propio. **Se repite** (17/11: 4).

**A8. M3, quién queda atrás después de los cambios en todas las ramas: 4 mal aplicadas, en 4 partidos.**

- Rearme para cuidar una ventaja tardía: Kocaelispor 1584472 (concedió en el 90+3) y Querétaro 1551046 (penal 8 minutos después).
- Persiguiendo: Metropolitanos 1646938.
- Rearme por una roja temprana, que la v1.7 da como válido en cualquier tramo: Kifisia 1593365.

Sostuvo en 6, todos «vía, no certeza». **Se repite** (17/11: 6 en 6). Repetirlo en el texto no ha servido. **Para la app:** un campo `m3.quedaAtras` por rama que el recibo pida.

**A9. M1 y rehacer: el sistema se copia del grid. 6 mal aplicadas, en 5 partidos, y 5 insumo.**

- **Mal aplicadas:**
  - AEK 1593360: banda de Koita;
  - Standard 1558687: el rehacer siguió con el 4-2-3-1 del último once de liga;
  - LDU 1639807 y Aucas 1639807: la ficha de las 21:02 se capturó antes del pitazo, y el rehacer siguió con el sistema viejo y con el 9 y el extremo invertidos;
  - Hull 1557472: rehecho, la rama y el M3 citaron a Egan, que estaba en el banco;
  - Chaves 1647587, de copa: se depositó con el xiReferencia vacío, que la v1.5 manda rechazar.
- **`no_dice`:** Union SG 1558685. No consta si la API corrigió la formación después del rehacer.

**Bajó** (17/11: el grid 8 de 8 y el rehacer 6 de 6), pero sigue con el once a la vista antes del pitazo. **Para la app:**

- el aviso M1-VS-ONCE-OFICIAL, que sigue pendiente;
- la hora de llegada de la formación;
- rechazar en el recibo el depósito con `xiReferencia` vacío.

**A10. Mismatch contra un reconvertido o una línea nueva: 4 mal aplicadas, en 4 partidos (3 sin copa).**

- FAVORABLE sin la vía con su remate: Stuttgart 1575228 y Mainz 1575224.
- La inversa: Atlético 1570456. Su NEUTRO salió de la «frecuencia del local de Bordalás», con la zaga rival rearmada y la vía nombrada contra ella. Por la v1.8 la rama subía a FAVORABLE.
- De copa: Rio Ave 1647590, que no pesó la vuelta que su propia vulnerabilidad nombraba.

Es regla de la v1.8, **nada que reescribir**.

### B. Numérico: solo candidato a medir

**B1. NEUTRO-refugio.** De los 21 `regla_fallo` del M5, 12 son NEUTRO que el volumen resolvió con claridad, en 10 partidos:

- **hacia FAVORABLE:** Rizespor 1584466, Pumas 1551043, Tigres 1551044, Standard 1558687, Real Sociedad 1570459, Augsburg 1575224 y River 1649569;
- **hacia DESFAVORABLE:** Amed 1584466, Monterrey 1551043, Sparta 1552230, Racing 1570459 y Lanús 1649569.

Otros 8 son FAVORABLE o DESFAVORABLE que el volumen dejó parejos o dio vuelta: Freiburg 1575229, Real Tomayapo 1645542, GO Ahead 1552227, Marseille 1552822, Werder 1575227, Panetolikos 1593364, Olimpia 1632065 y LDU 1639807. Cuatro de ellos son aciertos del lado por conversión.

**Se repite** (17/11: 14 de 20). Sigue siendo la banda de «parejo» que la v1.9 dejó a medición (propuesta §5). Las lecciones no dan el número: **candidato a medir** sobre los veredictos cerrados.

### C. Candidatos del bloque «Candidatos abiertos» que llegan a 3 partidos

| Candidato | Casos anteriores | Caso nuevo (esta semana) | Total | Juicio |
|---|---|---|---|---|
| El segundo de la lista de penales recibe la falta | Panathinaikos 1593355, Dinamarca 1528974 | Barcelona 1570455 (Yamal, segundo de la lista, pateó con Raphinha en cancha). Apoyo: Racing 1570459 (la falta fue sobre Zabiri, de la lista; pateó el primero) | 3, o 4 con el apoyo | Llega al umbral, para la revisión. Barcelona dice «figura en el penal», sin más crónica: un caso con reserva. |
| El rearme del doble pivote cuenta como el de la línea (M3) | Fiorentina, Instituto (Gimnasia, con una roja) | Marseille 1552822 (doble cambio del pivote al 74', goles al 84' y al 90+5) | 3 | Llega al umbral. |
| El caso de la 6 viaja con el arquero | Villarroel, Liechtenstein | Genoa 1550206 (Bijlow, «como en Lecce») y Hull 1557472 (dos 0-0 seguidos, 9 y 7 atajadas de Tzolakis) | 4 | Llega. |

### D. Reglas nuevas de la v1.9 en su primera semana

- **El reconvertido también ataca:** 2 sostuvo (Singo en Galatasaray 1584469, Giménez en Querétaro 1551046) y 1 mal aplicada (Knauff, Frankfurt 1575223).
- **La presión alta con su vuelta:** 1 sostuvo (Sassuolo–Genoa 1550206).
- **La materia de la pelota parada sale del cruce:** 3 mal aplicadas (A7), ninguna sostenida explícita.
- **El 9 titular con la base corta:** solo se sostuvo, sin una mal aplicada.
- **Posesión con «arriba» aparte y el perfil con su fuente:** 3 mal aplicadas en 2 partidos (Elversberg–Freiburg 1575229, los dos lados; Tigres 1551044). El 17/11 eran 12 en 11: **bajó mucho**, aunque esta semana hubo pocas lecciones de posesión.

## 4. Casos de 1 o 2 partidos (no entran)

- **La línea contraria tiene que nombrar el seguro del rival**, no solo «si se vuelca»: Angers 1552825.
- **El tercer nombre de la lista de penales («si entra») es el 9 que reemplaza al ejecutor:** Anderlecht 1558680.
- **Con la base de penales vacía, pateó el carrilero que centra:** Alanyaspor 1584471. La lista sumaba al lanzador de pelota parada, pero no a él.
- **Un rest defense «fijo» de dos medios con pocas titularidades juntas no aguanta la transición:** Olympiakos 1593362.
- **La clase del bloque rival no fija dónde remata el que persigue:** Cruz Azul 1551045.
- **La línea «con uno menos» no contó que el rival seguiría cargando:** Monterrey 1551043, que ganó con diez.
- **La vía de expulsión cubre también la protesta:** Manta 1639836 (se sostuvo).
- **Con ventaja amplia, el DT reserva al goleador del banco:** Paris FC 1552825.
- **La vida útil del improvisado es techo:** mal aplicada en Blooming 1645546, regla de la v1.4. Angers 1552825 la cumplió.
- **De copa, contra un rival de dos a cinco categorías menos** (las tres en la Taça):
  - el refresco propio pesa más que la vida útil: Sporting 1647591;
  - la rotación anunciada no fija el margen: Gil Vicente 1647584;
  - «concede temprano de visita» no se activa solo: Lourosa 1647594.

  Son tres partidos, pero todos de copa: no acreditan.
- **Lesión de las dos piezas de la transición** (`imprevisto`): Instituto 1649568.
- **Sin `bancoProbable` en una copa sin base, el banco por rol sirvió:** Chaves 1647587.

## 5. Comparación con el 17/11

| Patrón del 17/11 | Esta semana | Tendencia |
|---|---|---|
| Posesión por rama (12 mal en 11) | 3 mal en 2 | **Bajó** (la v1.9 la reescribió) |
| Banco ofensivo (16 mal en 15) | 13 mal en 13; la forma dominante pasa a «desde el 60'» y titular nombrado con once tardío | **Se repite** |
| M1 · el grid se copia (8 en 8) | 4 lados en 3 partidos, más 2 de rehacer y 1 xiReferencia vacío de copa | **Bajó** |
| Al rehacer, todo lo que nombra piezas (6 en 5) | Hull, Standard, LDU–Aucas | **Bajó**, persiste |
| M3 · quién queda atrás (6 en 6) | 4 en 4 | **Se repite** |
| Ceder / contrario de la condición (5 partidos) | Ceder en 3, contrario en 4 | **Se repite**; sube el contrario |
| Lista de vías (8 en 8, cada una de un renglón) | 8 en 7; ahora concentradas en el renglón 6 (4) | **Se repite** |
| Pelota parada (4) | 5 (3 de materia del cruce, v1.9) | **Se repite** |
| Penales con la base corta (5 mal y 1 fallo) | 0 mal; la regla del 9 titular se sostuvo | **Desapareció** |
| Referencia de volumen (3) | 7 | **Sube** |
| Vía de expulsión (4 lecciones) | 13 lecciones, 5 mal | **Sube** |
| NEUTRO-refugio (14 de 20 fallos del M5) | 12 de 21 | **Se repite** (a medir) |
| MECANISMO-ABIERTO (15 de 15), pregunta 6 (16 de 18) | 15 de 15, 15 de 17 | Se sostiene |
| M5 sin stats (8 `no_dice`) | 3 (2 de copa) | Bajó |

**Arreglos de la app del 17/11:**

- **`bancoProbable`:** cuando se copió entero, sostuvo, y ninguna lección culpa a la lista. El error «banco con un titular» no desapareció: quedan 4 casos, todos con el once tardío o sin capturar. Ese error viene del once probable, no de la lista.

  Lo que la app no corrige es lo del analista: el minuto fijo, el recorte en la razón y «solo persiguiendo». El total de mal aplicadas casi no bajó (16 a 13).
- **`EFE-RECOMPUTO-PENDIENTE` y el rehacer con FUERA-EN-LA-HOJA:** ninguna lección del DTP lo nombra. El rehacer del propio DTP sigue fallando al copiar el grid y las piezas en 3 partidos con la ficha disponible antes del pitazo (Hull, Standard, LDU–Aucas). Bajó, pero sin aviso no se corta.
- **`ventajaPorFuerza` y Jev `lectura`:** no tocan al DTP. `modoFallo` viene vacío en las 267 lecciones.
- **El banco, la F1 y el arquero sin el homónimo (21/11, 22:50):** ninguna lección del 22 y el 23/11 muestra un error por homónimo. El único caso de identidad es otro: el alias de Djené, en Getafe 1570456, va a `identidad.py`. No se puede juzgar con este material.
- **El once tardío sigue siendo el insumo dominante:** unas 19 lecciones de 17 partidos citan un once capturado tarde o una formación que la API corrigió después del pitazo. La hora de llegada de la formación sigue pendiente de la app.

## 6. Rarezas del dato

- **Ninguna lección es del 17/11**, y por lo tanto ninguna es de la versión vieja. Varias citan reglas de la v1.9 por su número (el reconvertido, el 9 titular, la materia del cruce) y las aplican.
- **Dos lecciones atribuidas al DTP en partes sin DTP depositado:** Olimpia 1632065:a:5 y Libertad 1632067:b:3 («sin DTP depositado»). Son lecciones de rúbrica sin análisis que juzgar, clasificadas `no_dice`, y no deberían contar como del skill.
- **No hay lecciones duplicadas.** Las 267 claves son únicas.
- **No hay fallos heredados del EFE.** Hay 2 casos al revés: el EFE o el TDE tenían bien el dato y el DTP no lo tomó.
  - Benfica 1647592, de copa: Kamiński estaba convocado según el EFE y no figuraba en el banco del DTP.
  - Bolívar 1645545: el H del mismo parte decía NEUTRO y la rama salió FAVORABLE.
