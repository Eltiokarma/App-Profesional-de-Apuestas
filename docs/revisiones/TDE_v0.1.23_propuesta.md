# Propuesta de revisión · `teorema-del-echado` v0.1.22 → v0.1.23

**Estado:** APROBADA por el usuario (25/10/2026, entera). Redactada en docs/skills/teorema-del-echado/ (v0.1.23). Falta que el usuario la suba a su cuenta.

Redactada el 25/10/2026 desde el dossier (`GET /analisis/cowork/revision/teorema-del-echado`,
cohorte `c3-2026-09-23`), las lecciones del skill
(`GET /analisis/cowork/lecciones?skill=teorema-del-echado`), los partes de esos
partidos con su veredicto (`GET /analisis/cowork/{id}`) y las incidencias 554,
560, 563, 568 y 572. Partimos de la v0.1.22 redactada el 22/10 en
`docs/skills/teorema-del-echado/SKILL.md`, que **todavía no está subida a la
cuenta**. No se tocó el skill, ni el código, ni el estado de ninguna lección.

## De dónde sale

- **Ventana:** solo lo posterior a la v0.1.22, lecciones con fecha del 22 al
  24/10/2026. Son 211 lecciones de 56 partidos: 83 aciertos, 84 fallos y 44
  parciales. Los 128 fallos y parciales salen de 36 partidos.
- **Población:** las 211 son `ciega` + `PRE` y acreditan. Ninguna está en
  cuarentena.
- **Qué versión se aplicó en esos partes.** La cuenta tenía la v0.1.21, pero
  el parte y el prompt ya pedían las SOB por rama desde el 22/10. En los hechos
  la v0.1.22 corrió a medias: 98 de las 112 ramas `siRecibePrimero` traen su
  `sob2`, y 14 llegaron sin él.
- **Lo que se leyó:** el texto entero (`queP` y `leccion`) de los 128 fallos y
  parciales, agrupados por la regla que tocan:
  - Disciplina 61, salidas de `siRecibePrimero`: 28.
  - Disciplina 44 (b), rama de ventaja: 25.
  - Disciplina 44 (a), línea del empate: 16.
  - Disciplina 16, roja según marcador: 11.
  - Disciplina 44 sin letra: 8.
  - Disciplina 23, ventana 90+: 7.
  - Disciplina 44 (d), línea de expulsión: 5.
  - Disciplina 44 (c), ventana de la rama: 3.
  - Otras, de una o dos lecciones cada una: 25.
- **Lo que se midió en los 56 partes**, con los tramos del veredicto ya
  recalculados con el PR #221:
  - Las ramas declaradas.
  - Los tramos que jugó cada rama y si concedió en ellos.
  - El SOB2 de la base y de cada rama.
- **Sesgo de atribución, igual de fuerte que en el DTP:** en **unos 75 de los
  128** fallos y parciales, la lección dice que la rama **se cumplió** o que
  **no se puso a prueba**. Lo dice así: «declarada y cumplida», «salida
  "marcó él": no cuenta contra la rama», «acierto no testeado», «la ventana
  relativa contuvo el gol». Lo que falló fue el 1X2 del lado. Esos casos
  **confirman** la v0.1.22 y no piden cambiarla. Dos ejemplos:
  - Mainz–Bremen: «la reasignación declarada antes del pitazo describió el
    partido».
  - Rayo–Elche: el `siRecibePrimero` en SOB «se pagó» y el `siMarcaPrimero`
    de Elche «se cumplió».

  Los cambios de abajo salen del resto: las lecciones que dicen **qué faltó
  escribir** o qué **escribió mal** la rúbrica.

## Respuesta corta: ¿hay algo que modificar?

**Sí, pero ningún número.** La fórmula, los pesos, las compuertas, las bandas y
las disciplinas 62-64 se sostienen. Lo que aparece son huecos de **cobertura de
las ramas**, y se pueden contar:

- **El que iguala no tiene rama.** Hubo 30 tramos de `siIguala` en 56 partidos.
  Nadie pudo declararlos, porque el parte rechaza esa clave. En 8 de esos
  tramos el equipo concedió, y en 5 lo hizo a 15 minutos o menos del empate.
- **La línea del empate se escribe en la prosa, no en su campo.**
  `siLeEmpatan` está declarada en 62 de 112 bloques, y 65 notas de
  `siMarcaPrimero` hablan del empate. Se jugaron 29 tramos de `siLeEmpatan`:
  14 sin rama escrita, y en 5 de esos el equipo concedió.
- **Una roja que iguala el número no es inferioridad.** La regla no lo decía.
  Pasó en Augsburg–Union y en Valencia–Villarreal.
- **El motivo de «administra» no se comprueba.** La 44 (b) se escribe
  nombrando un antecedente que no se parece al partido de hoy: otra sede, otro
  rival o sin las piezas que lo sostuvieron.
- **La ventana +15 del que persigue cobra la rapidez, no el régimen.** En 20
  ramas `siRecibePrimero` el equipo volvió a conceder. Solo 8 de esas primeras
  concesiones cayeron dentro de los 15 minutos; las otras 12 llegaron después,
  hasta 61 minutos más tarde.
- **El añadido decide partidos fuera de las seis ventanas.** De 151 goles
  concedidos, 14 cayeron en el añadido del segundo tiempo, en 12 de los 56
  partidos. En el 75-90 cayeron 27.

## Lo que esta capa acierta (no tocar)

- **La fórmula del ISE** (`(SOB1 + SOB2 + SOB3) / 3 × 10`), los pesos del IE,
  las compuertas y las bandas.
- **Las disciplinas 62 y 63 (cada rama con su número).**
  - Se cumplen en 98 de 112 ramas.
  - En LDU–Macará, Leuven–Lommel y La Louvière–Zulte, el ISE de la rama
    (6,67 a 8,33) describió el régimen que se pagó o el que rindió.
- **La disciplina 61 (tres salidas):**
  - Las salidas se repartieron 23 «marcó», 18 «concedió» y 11 «sin más
    goles».
  - De haberse contado como fallos, los 23 «marcó» habrían hundido la 44 sin
    motivo.
- **La disciplina 64:** el veredicto ya juzga tramo por tramo con la rama del
  marcador.
- **El desdoble de la 16 por marcador**, que entró en la v0.1.21, se cumplió
  en varios partidos:
  - Union Berlin, Estudiantes y The Strongest: roja yendo empatado,
    `ECHADA-NUM`, y sostuvieron.
  - Atlético Grau, Defensor Sporting y Westerlo: roja yendo ganando,
    `ECHADA-NUM`, y concedieron por centro o por rebote. Eso es la vía de
    echada operando, no un fallo.
- **«Administra» con un motivo que se parece al partido de hoy:**
  - Se cumplió en Cuenca, Macará, Casa Pia, Elche, Puerto Cabello, Recoleta y
    Tijuana.
  - La 44 (b) funciona cuando el antecedente viaja (cambio 4).

## Los cambios propuestos

### 1. Se aplica la rama del que iguala (`siIguala`)

La v0.1.22 la dejó como **candidato**, con dos casos (Paris FC–Rennes y
Albion–Torque), hasta llegar al tercero ciego. Ya llegó, y con margen. Las
lecciones ciegas del 22 al 24/10 que la piden son estas:

- **LDU–Macará** (24/10): con 1-1 al 74 y obligado a ganar, LDU siguió
  cargando y concedió al minuto.
- **Monagas–Puerto Cabello** (24/10): concedió un penal a los 6 minutos de
  igualar.
- **Torino–Monza** (23/10): el 2-1 llegó a los 14 minutos del empate.
- **Villarroel–Blooming** (24/10): Blooming quiso sostener el empate y
  concedió a los 14 minutos.
- **Caracas–Táchira** (24/10): Caracas igualó al 25 y perdió en el 90+2,
  «acorralado por el banco rival».
- **Stuttgart–Gladbach** (23/10): con 1-1, el que había igualado se puso
  arriba al 51.
- **Maldonado–Danubio** (24/10): con la línea escrita en la nota, siguió
  cargando y ganó en el 90+4.

En los 56 partes hubo **30 tramos `siIguala`**:

- Ninguno pudo declararse: `parte.RAMAS_REASIGNACION` rechaza la clave.
- En 8 el equipo concedió, y en 5 de ellos a 15 minutos o menos del empate
  (Monza, Blooming, Monagas, LDU y Beveren).

**Propuesta:** `siIguala` entra como **quinta rama** de la disciplina 44. Dice
qué hace el equipo que **empata un partido que iba perdiendo**:

- **Sigue empujando:** es la rama por defecto del obligado, del local que
  necesita ganar y del que ya metió el banco ofensivo. Va en SOB, con sus tres
  SOB y una ventana **desde el empate +15**.
- **Sostiene el punto:** solo **nombrando por qué**, con la misma regla de la
  44 (b).

No es un peso nuevo. Es la disciplina 64 con su casilla escrita.

### 2. La línea del empate y la de la expulsión van en su campo, sin tope de minuto

La 44 (a) dice «si recibe el empate **antes del 75**», y la (d) pide una línea
por expulsión. En la práctica pasan dos cosas:

- **Se escriben dentro de la nota de `siMarcaPrimero`** («caduca si le
  empatan y reabre la SOB»). Así nadie las puede cobrar.
  - Tijuana–Toluca, Forest, Puerto Cabello, Lommel y Racing Montevideo, para
    el empate.
  - Defensor Sporting, para la expulsión.
  - Stuttgart: la ventana de la rama quedó solo en la prosa.
- **El tope del 75 deja sin rama al empate tardío.**
  - Gimnasia–Platense: empate al 79 y derrota en el 90+3.
  - 2 de Mayo–Recoleta: empate en el 90+3.
  - La disciplina 64 ya dice que en cada tramo manda la rama del marcador, así
    que el tope contradice a la 64.

**Propuesta:**

- **(a) Sin tope.** La línea del empate vale para el empate en cualquier
  minuto. Si llega tarde, la ventana de la rama se corta en el final.
- **En su campo.** `siLeEmpatan`, `siIguala` y `siExpulsion` se escriben en su
  campo, con su ventana. **Una línea dentro de la nota de otra rama no cuenta
  como declarada**, porque el cierre no la puede comprobar.
- **La 44 (d) también cubre la roja que llega perdiendo.** Pasó en
  Manta–Cuenca: roja al 89 con 0-2.

### 3. Disciplina 16: primero manda la cuenta de jugadores, después el marcador

La 16 habla de «un hombre menos» y «uno más», pero no de la segunda roja. Tres
lecciones ciegas de dos partidos del 24/10 muestran el hueco:

- **Augsburg–Union:** la roja de Bah (63) dejó 10 contra 10. Augsburg no pasó
  a `ECHADA-NUM`, siguió atacando y marcó al 71.
- **Valencia–Villarreal:**
  - El Villarreal sostuvo 11 minutos con diez y, cuando el Valencia también
    quedó con diez, «dejó de resistir y ganó de contragolpe».
  - El Valencia, ya 10 contra 10, siguió en `siLeEmpatan`, se expuso y
    concedió en el 90+6.

A eso se suman dos huecos de la línea y uno de orden:

- **El rival con uno menos.** Albion (roja rival al 31 yendo 1-0) y Arouca
  (roja rival al 6). El `siExpulsion` solo cubría la roja propia, y
  «administra» quedó sin línea mientras los dos siguieron cargando. La regla
  ya existe («el que queda con uno más no administra»); lo que faltaba era
  escribirla.
- **El orden entre ramas.** Atlético Grau, con diez desde el 27, no reabrió la
  SOB tras el empate: la expulsión mandó sobre `siLeEmpatan`.

**Propuesta:**

- **La cuenta de jugadores manda primero.**
  - **Inferioridad:** rige `siExpulsion` con el desdoble por marcador de
    siempre, y manda sobre la línea del empate.
  - **Paridad restablecida**, es decir, una roja propia que iguala el número:
    `ECHADA-NUM` **caduca** y vuelve la rama del marcador.
  - **Superioridad:** «no administra», como hoy.
- **`siExpulsion` declara los dos lados:** `propia` y `rival`.

El veredicto ya marca `numerico` (inferioridad, paridad o superioridad) en
cada tramo desde el PR #221. Esto le da a la regla el mismo criterio.

### 4. 44 (b): el motivo de «administra» tiene que parecerse al partido de hoy

La 44 (b) exige **nombrar** por qué un equipo administraría. Se nombra, pero
con antecedentes que no se parecen al partido de hoy. Hubo seis ramas
«administra» que no operaron, más una que concedió sin las piezas que la
sostenían:

- **Brest–Nice:** se apoyó en un partido **de visita** contra un rival que
  quería la pelota. De local y con la orden de «oser», Brest siguió atacando.
- **La Louvière–Zulte:** el bloque bajo **ante Brujas**, un rival superior.
  Hoy enfrente había un obligado sin gol.
- **Leuven–Lommel:** el bloque probado de visita ante Cercle. Lommel se quedó
  la pelota (57 %) y concedió dos transiciones en dos minutos.
- **Gimnasia–Platense:** el antecedente se sostuvo con Antonini y Muñoz. Hoy
  los dos estaban fuera (IP rojo), y Gimnasia concedió en el 79 y en el
  añadido.
- **Puebla–Monterrey:** el motivo fue la rotación y la fecha doble. Siguió
  atacando: 3-0 al 34 y 4-0 al 61.
- **Stuttgart–Gladbach y Antwerp–Charleroi:** la `VENTAJA-INESPERADA` se
  tomó como motivo. El de menor `μ` siguió atacando. En el Antwerp, además,
  era el obligado (SOB1 = 1), que la 44 (b) ya manda a «sigue atacando»: ahí
  fue incumplimiento.

Del otro lado, en Cuenca, Macará, Casa Pia, Elche, Puerto Cabello, Recoleta y
Tijuana el motivo era de la **misma condición y del mismo tipo de rival**, y se
cumplió.

**Propuesta:** un antecedente sostiene «administra» solo si se parece al
partido de hoy en tres cosas:

- **La misma condición:** local o visita.
- **Un rival del mismo perfil:** que también quería la pelota, obligado o
  superior.
- **Las mismas piezas:** las que lo sostuvieron están disponibles hoy.

Si falla alguna de las tres, el antecedente no vale y la rama vuelve al
defecto de la 44 (b). Además, **`VENTAJA-INESPERADA` y la menor `μ` no son
motivo por sí solas**: dicen que el equipo no esperaba ir ganando, no qué va a
hacer con la ventaja.

Es la disciplina 48 («un precedente sin presión no es precedente») aplicada a
la rama de ventaja. Va en la línea del cambio 2 del DTP v1.5 (el caso del
bloque, completo).

### 5. Disciplina 61: cuarta salida, y la rama del que persigue se cobra por el régimen

**La cuarta salida: «concedió por otra vía».** Cinco lecciones muestran que la
salida «concedió» no distingue la vía que se pagó de un gol que no tiene nada
que ver con exponerse:

- **Antwerp–Charleroi:** un penal nacido en el medio y un córner.
- **Rayo–Elche:** la ventana 23-38 contuvo un penal. El contragolpe llegó
  recién al 68.
- **Defensor–Racing:** un penal de mano.
- **Stuttgart–Gladbach:** un 1 contra 1 perdido en la banda.
- **Always Ready–The Strongest:** una pérdida en la salida y un remate de
  media distancia.

**Propuesta:** se agrega la salida **«concedió por otra vía»**: penal, pelota
parada o error individual sin la exposición escrita. No cuenta ni a favor ni
en contra de la rama, igual que la disciplina 24 hace con la ventana.

**La aclaración del régimen.** La 44 (c) ya permite el régimen de la
disciplina 45 en una rama SOB. Pero 110 de las 112 ramas `siRecibePrimero` se
escribieron «desde el gol +15», y los cierres de varios partidos juzgan esa
ventana como si fuera la rama:

- **Manta–Cuenca:** concedió a los 33 minutos del gol.
- **UTC–Melgar:** el 0-2 llegó al 68, con la rama abierta desde el 7.
- **Estrela–Casa Pia:** el gol llegó en el 90+2.
- **LDU–Macará:** el equipo se expuso hasta empatar.

**Propuesta:** la rama SOB del que persigue se cobra **por su salida**, que
es el régimen desde el gol hasta el empate o el final. El veredicto ya la
calcula (`reasignacion.salida`). La ventana +15 queda como lo que es: si la
vía se paga **rápido**. Es una aclaración, no un número.

### 6. El añadido como casilla de cierre, no como ventana modal

La disciplina 23 manda escribir que la ventana no incluye el añadido y anotar
en el cierre si el gol cayó fuera, pero no hay casilla donde contarlo. El
candidato `90+` con duración que sale de los eventos del partido lleva
pendiente desde la v0.1.8, con un caso.

Hoy los datos son estos:

- **En los 56 partes,** 14 de los 151 goles concedidos (9 %) cayeron en el
  añadido del segundo tiempo, en 12 partidos. En el 75-90 cayeron 27: **uno
  de cada tres goles del tramo final queda fuera de las seis ventanas**.
- **En la cohorte,** 33 lecciones de 33 partidos citan la disciplina 23 o el
  90+.
- **En esta ventana de tres días:**
  - Recoleta en el 90+3, Estrela en el 90+2 y Leuven en el 90+6.
  - Westerlo en el 90+7 y el 90+12.
  - Nacional Asunción en el 90+2 y Gimnasia en el 90+3.

**Propuesta, a medias:**

- **Se crea la casilla «añadido»:** el cierre cuenta aparte el gol concedido
  en el añadido del segundo tiempo, con la vía que estaba activa.
- **El 75-90 estricto no se toca.** La serie del sesgo tardío no se rompe
  (disciplina 45), y las seis ventanas modales siguen como están.
- **La duración que sale de los eventos y el «amplificador de la vía activa»
  siguen como candidatos.** Con la casilla en marcha se van a poder contar.

## Las cuatro lecciones que Jev marcó como «pide mover un número»

Las cuatro son anteriores a la v0.1.22 y acreditan. Lo que piden de verdad:

| Lección | Qué pide | Lectura |
|---|---|---|
| Cusco–Alianza (11/10, disciplina 16) | Desdoblar la roja por marcador | **Ya aplicada en la v0.1.21.** Se marca `aplicada` con 🔑 |
| Chicó–Cúcuta (11/10, F2) | Declarar viaje y altura | **No mueve nada del skill.** F2 es dato del motor (disciplina 21) y lo subido a mano se declara. Falso positivo |
| Vasco–Boca (21/10, 44 a) | Línea para el **segundo gol en contra** en una serie de ida y vuelta (SOB1 de 0,5 a 1) | **Candidato, un caso.** La disciplina 64 ya pone la rama del marcador en cada tramo; falta saber si «perdiendo por dos» merece su propia línea |
| Grêmio–Inter (11/10, ventana) | Con `C1 = 1`, la ventana de la echada sigue la vida útil del bloque (55-65) y no el 75-90 | **Es la única que pide de verdad mover un número**: la ventana por defecto de la echada. Un caso a favor (Los Chankas–ADT no llegó a la vida útil y en Leeds fue pelota parada). **Candidato**, no se aplica |

## La pregunta abierta del DTP v1.5: ¿el SOB2 hereda la rama «persiguiendo»?

**Cómo hereda hoy.** `dtp_cowork.herencia_tde` toma el SOB2 del TDE del
`restDefense.nivelFoco` del DTP del mismo equipo; si falta, del `nivelRival`
del DTP del rival. La escala es fijo 0 · depende 0,5 · sin 1. Ese SOB2 alimenta
**la base**. Desde la v0.1.22 (disciplina 63), el SOB2 de cada rama del que
persigue se vuelve a puntuar aparte, y sin evidencia vale 0,5.

**Qué dicen los 56 partes:**

- **Ningún parte trae `nivelFocoPersiguiendo`:** el DTP v1.5 todavía no
  rige. No hay forma directa de medir qué habría cambiado.
- **La disciplina 63 ya hace el trabajo en las ramas.** En 68 de 112 ramas
  `siRecibePrimero`, el `sob2` de la rama es mayor que el de la base. En 30 es
  igual (casi siempre «depende» 0,5 = sin dato 0,5) y en 14 falta.
- **El SOB2 de la rama no separa, por ahora:**
  - Con el `sob2` subido, el equipo concedió en 11 de 36 ramas jugadas (31 %).
  - Con el `sob2` igual al de la base, concedió en 6 de 16 (38 %).
  - Con n tan chico no hay base para mover nada.
- **Heredar la rama «persiguiendo» en la base sería un error.** El tramo base
  es el 0-0, donde el equipo no persigue. Subirle el SOB2 al arranque inflaría
  el ISE de todos los tramos base. En 119 tramos base, el equipo concedió en
  50, y no hay nada que diga que el seguro del arranque era peor.

**Recomendación:**

- **La base no cambia:** sigue heredando el `nivelFoco` del arranque.
- **Si el usuario aprueba el cambio 3 del DTP v1.5,** el
  `nivelFocoPersiguiendo` pasa a ser **la evidencia que pide la disciplina
  63** para el `sob2` de las ramas del que persigue (`siRecibePrimero`,
  `siLeEmpatan` cuando vuelve a empujar y `siIguala`, del cambio 1). Ocupa el
  lugar del 0,5 por defecto.
- **Si el TDE declara otro valor,** sale `HERENCIA-DTP`, como con C1. Si falta
  el del propio equipo, se lee el `nivelRivalPersiguiendo` del DTP del rival.
- **La escala 0 · 0,5 · 1 no cambia.** Lo que cambia es de qué fuente sale el
  número de la rama, no un número calibrado.
- **Revisar con n ≥ 10 ramas jugadas por valor de herencia** si el `sob2`
  heredado separa mejor que el 0,5.

## Las cinco incidencias: ¿skill o backend?

Las cinco son **del backend** (`backend/analisis/veredicto.py`,
`tramos_por_marcador` y la ventana de la rama), y las cinco quedaron
**resueltas en el PR #221** (25/10):

- **554 (añadido del primer tiempo):** el 45+6 y el 51 del segundo tiempo
  compartían minuto. Ahora el bloque y los tramos usan la misma regla del
  añadido. **No pide nada al skill.**
- **572 (Westerlo 4-4 Beveren):** había tramos desordenados con goles y rojas
  en el añadido. Ahora los eventos van en orden (reloj, añadido) y la roja
  trae su añadido. **No pide nada al skill.**
- **560, 563 y 568 (la roja del rival y la que iguala el número):** el arreglo
  del backend es el campo `numerico` y `rojaRival` por tramo: `siExpulsion`
  solo con el equipo en inferioridad, y con paridad vuelve la rama del
  marcador. **Pero destaparon un hueco del skill:** la disciplina 16 no decía
  qué pasa con la paridad ni con la roja del rival. Es el **cambio 3**, que
  pone la regla a la altura de lo que el backend ya calcula.

Queda del lado del backend, **si se aprueba**:

- Aceptar `siIguala` en el parte.
- Exigir en el recibo `siLeEmpatan` y `siExpulsion`, y avisar si una nota de
  `siMarcaPrimero` habla del empate sin la rama en su campo.
- `siExpulsion` con `propia` y `rival`.
- La salida «concedió por otra vía» y la casilla «añadido» en el veredicto.

## Lo que NO se propone

- **Ningún número:** ni pesos, ni la fórmula del ISE, ni las bandas, ni la
  ventana por defecto de la echada (Grêmio–Inter sigue como candidato).
- **Candidatos de un caso, sin aplicar:**
  - **La ventaja que se achica a un gol** (Westerlo–Beveren): con 3-2 el DT
    hizo cuatro cambios a la vez para cerrar y concedió dos.
  - **La rama de ventaja que manda la llave a penales** (Palmeiras–Fluminense):
    se administra hacia la tanda.
  - **El segundo gol en contra en una serie** (Vasco–Boca).
  - **Un rol reasignado con amarilla temprana** como S1 alto desde ese minuto
    (Atlético Grau: segunda amarilla al 27).
  - **El SOB3 que se puntúa por el perfil del rival** sin mirar si ese rival
    genera cuando no tiene ventaja que defender (Chicó–Bucaramanga).
  - **El obligado que se expone a 0-0 sin haber recibido**
    (Nacional–Trinidense). Lo cubren el `SOB1` de la base y la disciplina 18:
    es cumplimiento.
- **El descendido sin nada en juego que recibe primero y no colapsa** suma su
  segundo caso (UTC, después de Estudiantes de Río Cuarto). Sigue como
  candidato hasta el tercero ciego.
- **La roja yendo perdiendo agrava el ISE:** Alverca no lo mostró (con diez,
  corrigió en el descanso y se adelantó sin pagar). Es un caso en contra
  frente a TDE-034 y Cusco. No se toca.
- **La rotación de 3 o más titulares contra F1 y F2** (Independiente del
  Valle, Tijuana) ya está en las disciplinas 35 y 36: es cumplimiento.

## Cómo se aplica si se aprueba

1. El usuario aprueba o corrige, punto por punto. La herencia del SOB2 desde la
   rama «persiguiendo» va **junto con el cambio 3 del DTP v1.5**: sin ese
   cambio no hay campo que heredar.
2. Se redacta la v0.1.23 en `docs/skills/teorema-del-echado/` sobre la v0.1.22:
   - El changelog.
   - En la disciplina 44: `siIguala`, y (a) y (d) en su campo y sin tope.
   - La disciplina 16 con la cuenta de jugadores.
   - En la 44 (b), las tres condiciones del antecedente.
   - La cuarta salida de la 61.
   - La casilla «añadido» en la 23.
3. Se le da sitio en el parte y en el veredicto, con sus tests y el prompt de
   `docs/COWORK.md`:
   - `siIguala` en `RAMAS_REASIGNACION`.
   - Los avisos del recibo.
   - `siExpulsion.propia/rival`.
   - La salida `concedioOtraVia`.
   - El conteo del añadido.
4. Se entrega **un solo `.zip` con la v0.1.23**, que incluye la v0.1.22
   todavía sin subir, para subirlo a la cuenta.
5. Se marcan como aplicadas, con 🔑:
   - Las lecciones de `siIguala`, la línea del empate, las rojas y la 44 (b)
     de esta revisión.
   - La de Cusco–Alianza, en la v0.1.21.
