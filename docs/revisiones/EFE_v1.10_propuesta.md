# Propuesta de revisión · `efe-clasificador` v1.9 → v1.10

**Estado:** PROPUESTA, sin aprobar. Escrita el 08/11/2026 desde el dossier de
`GET /analisis/cowork/revision/efe-clasificador` (generado el 08/11 a las
02:31 UTC): **416 lecciones pendientes**, de los partidos del 01/11 al 07/11.
Casi todas se escribieron con la v1.9. Las del tramo de las 04:47 del 01/11 se
escribieron con la v1.8, porque la v1.9 se subió a la cuenta hacia las 08:00 de
Lima de ese día (DEUDA 19). La base es la v1.9 vigente
(`docs/skills/efe-clasificador/SKILL.md`, `references/rubrica-efe-v1.9.md`).
`efe-dashboard` v1.12 solo aparece donde una lección lo toca.

## De dónde sale

- **416 lecciones:** 202 aciertos, 95 parciales y 119 fallos, de 169 partidos.
  Todas son `ciega` + `PRE`.
  - **9 son de copa nacional** (Copa de la División Profesional de Bolivia).
    Fijan rúbrica y no entran a ninguna métrica.
  - **4 están en cuarentena automática** por un DT sin declarar (PAOK–Asteras
    1593351 y Athletico–Vasco 1492440). El dossier lista además 6 de
    Huracán–Tigre (1493219) y Bulo Bulo–Real Potosí (1645519). No cuentan en
    nada y no fijan rúbrica: acá se citan solo como contexto.
  - **403 son acreditables** y podrían sostener un cambio de peso
    (`puedeMoverNumeros`).
- **Ninguna pide mover un número.** Jev no marcó ninguna con
  `proponeMoverNumero`: 412 no tienen etiqueta y 4 la tienen en `false`. En
  `porModoFallo` hay 11 fallos: 5 `lectura_efe`, 3 `insumo` y 3 sin etiqueta.
  La `lectura` del dossier lo dice así: «la revisión fija rúbrica; un cambio de
  peso no tiene quien lo sostenga». **Esta versión no toca pesos, máximos,
  cortes de la tabla de puntuación, cortes de zona, el ×1,5 del arquero ni el
  tope del bloque D por D3 ❌.**
- **Métricas de la población que acredita** (`metricas`, 20 casos y 40
  lados): 22 aciertos, 8 parciales y 10 fallos por lado; el 1X2 acertó 12 de
  20. El Brier es 0,549, contra una línea de base de 0,515: no mejora la base.
  Son números del parte entero y de sad-analysis, no del EFE. Se citan para
  dar contexto y no se usan para mover nada.
- **El sesgo de atribución pesa todavía más que en la v1.9.**
  - **Brecha y empate técnico:** 100 lecciones, una de cada cuatro. Casi todas
    dicen «declarada y cumplida». De ellas, 37 figuran como fallo: el fallo es
    del 1X2 del lado, no de la regla. Ejemplos: Forest–City (1557465), Pachuca
    (1551032) y Nacional–San Lorenzo (1632053).
  - **Incumplimientos de la v1.9:** el grupo más grande de lo que sí falló son
    reglas que la v1.9 ya escribe y no se aplicaron. La principal: con el once
    oficial a la vista, los once titulares van en la tabla F1. Otra vez, esto
    pide **cobrarlas** y hacer que la app las calcule, no reescribirlas.
- **Pendientes de la app que dejó la v1.9** (`docs/revisiones/PENDIENTES.md`,
  sección EFE). Siguen sin hacer y casi todo lo que falló en esta tanda cae ahí:
  - `EFE-RECOMPUTO-PENDIENTE`;
  - `EJE-DEBUTANTE-SIN-DECLARAR` y `EJE-DEBUTANTE-SIN-OBJETO`;
  - el `recambio` en `f1/{id}`;
  - los nombres de la prosa sin fila F1;
  - el arquero del día.

  La sección «Para la app, no para el skill» los pone primero.

## Lo que la v1.9 acertó y no hay que tocar

- **El empate técnico de formación** (brecha con T.54, R-KT.2 o ESCALA-LIGAS).
  - **A favor:** unas 100 lecciones. En 29 ganó el de menor porcentaje. Algunos
    casos:
    - Nacional–San Lorenzo (1632053): 77,9 % contra 21,4 %, ganó el de 21 %.
    - Forest–City (1557465): 35,6 % contra 65,7 %.
    - Necaxa–Tijuana (1551030): 37,8 % contra 81,5 %.
    - Libertad–Emelec (1639859): 69,8 % contra 35,1 %.
    - Samsunspor–Konyaspor (1584465): 22 % contra 54 %.
    - Millonarios–América (1549851): el de 54,7 % dominó 26 a 4 en remates.
  - **Contraejemplos** (ganó el más formado con la alerta activa):
    Villarreal–PSG (1635746, 0-6), Feyenoord–Inter (1635662), Lens–Como
    (1635681), San Lorenzo–Platense (1493238) y Monagas–Táchira (1646932).
  - **Conclusión:** la proporción es la de la v1.9 (22 contra 6). No mueve la
    regla. `EFE-EMPATE-TECNICO` la calcula la app y no se olvidó en ningún parte.
- **T.54 con la fecha del DT y el banco que dirige (v1.8).**
  - **Volos (1593358):** DT de 12 días, tercera derrota en tres partidos.
  - **Sporting (1575543):** Fonseca, en su debut, se puntuó como banco que
    dirige.
  - **Samsunspor (1584449):** Bjelica, con dos semanas en el cargo.
  - **T.54-B atenuado:** se sostuvo en Arouca (1575528, 1575539).
  - **Contradicciones declaradas con `dt.banco` `api_errada`:** la ficha las
    confirmó en Coritiba (1492446) y Real Potosí (1645457), y en Juárez
    (1551029) el parte no cayó en cuarentena.
- **La jerarquía de fuentes** (v1.7 a v1.9): 13 confirmaciones.
  - **Dudas que jugaron:** Alianza Lima (1549537, cinco jugadores en Duda por
    prensa nacional contradictoria, los cinco titulares), Kortrijk (1558657),
    Sparta (1552220), Cerro (1632052), Arsenal (1557453), Famalicão (1575530),
    Hamburgo (1575205), Universidad Católica (1505554) y Genoa (1550184).
  - **Contradicción declarada y prensa que mandó:** Samsunspor (1584465), con
    Afonso Sousa.
- **«Sin dato es respuesta válida».**
  - **B6:** Seimen en Stuttgart (1575214).
  - **B5:** el banco de Cienciano (1549537).
  - **Bloque C:** PEC Zwolle (1552212), con HUECO-DOBLE.
  - **D3 de visita:** Racing de Santander (1570447). El D3 iba sin dato y el
    equipo remontó: sin dato dice que falta el caso, no que la reacción no
    exista.
- **COLAPSO EN CASCADA describe y no predice.**
  - **Recibió primero y no recuperó, sin goleada:** Mainz (1575217),
    Elversberg (1575212), Gaziantep (1584456 y 1584462), Chicó (1549846), Lecce
    (1550184) y Marítimo (1575534).
  - **Recibió primero y recuperó:** Başakşehir (1584463), Lecce (1550195) y ABB
    (1645536).
  - **No se puso a prueba:** Alavés (1570450), Strasbourg (1552808) y
    Excelsior (1552213, con una roja al 5').
- **La caja de sensibilidad bajada al partido (v1.8).** Escribió el once real
  en Standard (1558677), Panathinaikos (1593349), Kasımpaşa (1584453, «arranca
  Hajradinović»), Rio Ave (1575527), Cagliari (1550183) y Chivas–Atlante
  (1551024).
- **La F3 por zona dice qué anuncia (v1.9).** Se confirmó por zona:
  - **ATK, menos volumen propio:**
    - Aldosivi (1493227): ningún remate al arco.
    - Angers (1552804): 0,44 de xG.
    - Ameliano (1632051): 0,52.
    - Moreirense (1575543): 0,55.
    - Betis (1635651): 0,88.
    - Lecce (1550195): 0,31.
  - **MID, esterilidad propia:**
    - Hull (1557457): 0,36 de xG con 33 % de pelota.
    - Torino (1550181): 54 % de pelota y 0,68 de xG.
    - Inter de Bogotá (1549856).
    - Atlas (1551032).
  - **DEF, concede:**
    - Galatasaray (1584461): tres goles sin el central fijo.
    - Hamburgo (1575205).
    - Gimnasia (1493233): 20 remates en contra, lo sostuvo el arquero.
  - **«Baja la confianza en la K, no el resultado»:** Standard (1558677),
    Lille (1635640), Torque (1646901), Everton de Viña (1505547) y Barracas
    (1493230).
- **EJE-DEBUTANTE con el once oficial (v1.9), donde se aplicó.**
  - **Declarado con el grid y cumplido:**
    - Galatasaray (1584461) y Sassuolo (1550187): tres goles en contra cada uno.
    - Coventry (1557460): los dos goles por el aire que defendía la pareja.
    - Strasbourg (1552817).
    - Napoli (1635656).
    - Samsunspor (1584449).
    - La Louvière (1558665).
    - Estudiantes (1493217): 0-3 en siete minutos.
    - Lommel (1558671).
    - Nacional Asunción (1632058): autogol de uno de la pareja.
  - **Descartado con el grid:** Hamburgo (1575218), Alianza Lima (1549537),
    PSV (1635707), Cobresal (1505547) y Comerciantes (1549539).
  - **Amplió el rango sin materializarse, como dice la regla:** Libertad
    (1632058), Emelec (1639859), Espanyol (1570446), Necaxa (1551030) y Lyon
    (1552804).

## Los seis cambios propuestos

### 1. El rehacer con el once oficial empieza por la tabla F1, y una baja que está en la hoja deja de ser baja

**Qué dice hoy (v1.9).** «Con el once oficial a la vista, los once titulares
tienen fila.» La app avisa `ONCE-SIN-FILA-F1` al leer, con un texto que pide
rehacer la tabla «con 3 o más».

**Lo medido (80 lecciones de la tabla F1: 32 aciertos, 23 parciales y 25
fallos).**
- **El incumplimiento central:** desde el 03/11, cuando ya regía la v1.9, hay
  **37 lecciones de 34 partidos** en que el parte se rehízo o se re-depositó
  con el once capturado y dejó titulares sin fila. El DTP sí se rehizo con el
  once; la tabla F1, no. Algunos casos:
  - **Cagliari (1550188):** once a las 13:32 y depósito a las 13:46. Trepy,
    Grandu y Kofler quedaron sin fila, justo la línea de fondo del
    EJE-DEBUTANTE.
  - **Parma (1550194):** el central nuevo sin fila fue el expulsado al 9'.
  - **Recoleta (1632054):** Figueredo era la pieza nueva de la línea que
    concedió tres en 10 minutos.
  - **Luqueño (1632055):** tres sin fila, y uno de ellos hizo el 0-1.
  - **Mushuc Runa (1639831):** tres sin fila.
  - **Kifisia (1593358):** Apostolakis, en la banda que el rival atacó en el 1-0.
  - **Más casos:** Gremio (1492445), Barracas (1493230: Orsini, autor del
    1-0), Forest (1557465), Leeds (1557463), Real Madrid y AEK (1635606),
    Samsunspor y Konyaspor (1584465), Riestra (1493235: cinco titulares nuevos
    sin fila).
- **Con uno o dos sin fila también importa.** El texto del aviso dice «con 3 o
  más», y Samsunspor (1584465) y Recoleta (1632054) lo leyeron como un umbral.
  La regla de la v1.9 no tiene umbral: son los once.
- **La baja declarada que figura en la hoja:**
  - **Táchira (1646929):** Pollero y Alfonzo siguieron en `fuera` y en el DTP
    («sin un 9 de área») con la hoja ya capturada. Pollero estaba en el banco,
    entró al 46' e hizo un gol y una asistencia.
  - **Mismo patrón, aunque sin certeza de que el once estuviera al depositar:**
    Liverpool (1557453, Szoboszlai en el banco), Sporting (1635723, Zalazar) y
    Udinese (1550196, Bayo entró al 88').
- **Sin once oficial, la regla de la v1.9 tampoco se cumplió del todo.**
  - **Recambio de la duda:** Racing de Santander (1570440, Iker Luque), Lommel
    (1558667, Gooijer), Valencia (1570437), Guabirá (1645531, jugó un
    delantero de 241 minutos que no estaba).
  - **Rotables de la rama:** Braga (1575530, Fran Navarro y Travassos),
    Independiente del Valle (1639800, Góngora hizo el 1-0), Puerto Cabello
    (1646933, Ponce hizo el 1-1).
  - **Nombres de la prosa:** Athletic (1570433, Peio Canales), Pasto
    (1549847), Jaguares (1549847), Telstar (1552214).
  - **El refuerzo que ya debutó:** Cali (1549846, Bacca marcó).

  Son la regla 1 de la v1.9 sin aplicar. No hace falta otra regla: hace falta
  el cálculo de la app (A2).

**Propuesta (sin tocar pesos ni el IP):**

1. **El rehacer con el once oficial tiene un orden fijo**, y la tabla F1 va
   primero:
   1. Cruzar los once titulares de la hoja con la tabla y **sumar la fila de
      cada uno que falte**, con su `jugadorId` y el rol que da `f1/{id}`
      (`rolSugerido`).
   2. **Toda baja o duda de `fuera` que figura en la hoja**, titular o en el
      banco, pasa a disponible. La prosa que la usaba (DTP, matriz, matchup)
      se corrige en el mismo depósito.
   3. B6 sobre el arquero de la hoja (regla de la v1.6, cambio 4).
   4. EJE-DEBUTANTE sobre la línea entera del grid (cambio 3).
   5. B y F si hay ≥ 3 titulares fijos rotados (regla de la v1.7).
   6. D1 y H si el sistema cambió (cambio 2).

   Recién ahí se re-deposita. Un rehacer que rehízo el DTP y no la tabla es
   un incumplimiento, no una lectura.
2. **No hay umbral para la fila.** Con el once a la vista son los once, sean
   uno o cinco los que faltan.

**Calculable (app, ver A1).** Que el depósito devuelva en el recibo los
titulares sin fila y las bajas que están en la hoja, en el momento de
depositar y no solo al leer. Y que `f1/{id}`, con el once capturado, traiga la
fila lista de cada titular.

**Qué NO:** subir el tope de 14-16 filas como número. La tabla crece solo con
quien juega hoy.

### 2. El sistema se verifica con el once: D1 🔶, un DT que alterna o una T.54 corta dejan D1, H y la zona del ausente condicionados

**Qué dice hoy.**
- **D1:** puntúa el sistema base de más de 6 meses.
- **v1.9:** con T.54 de ≤ 2 partidos, B6 y F van condicionados al once
  oficial.
- **H:** nada dice que el matchup apoyado en un sistema se condiciona al once.

**Lo medido (3 lecciones por la regla y 6 citadas desde otros grupos; 2
aciertos, 2 parciales y 5 fallos).**
- **Alavés (1570450):** D1 decía «alterna 5-3-2 y 4-5-1» y el parte tomó «4-4-2
  hoy» del primer once de la API.
- **Panetolikos (1593350):** D1 ✅ por el 4-4-2 de los dos últimos grids, y el
  DT pasó a línea de tres en casa con dos titulares sin fila.
- **Defensor Sporting (1646900):** un interino que ya había cambiado de sistema
  entre sus dos primeros partidos. La sanción de Elizalde se leyó como «línea
  de tres rearmada» y volvió al 4-2-3-1.
- **São Paulo (1492448):** EJE-DEBUTANTE y F3 por la zona DEF se escribieron
  sobre una línea de tres con Newton de central. El grid trajo una línea de
  cuatro de oficio con Newton en el medio, y la valla quedó en cero.
- **Danubio (1646902):** H DESFAVORABLE por «rombo sin amplitud contra
  carrileros», y salió un 3-4-1-2 espejo (la API corrigió la formación 26
  minutos antes). El H acertó el resultado y no el mecanismo.
- **Atlas (1551032):** el EJE-DEBUTANTE se declaró sobre un grid que la API
  corrigió después. La línea real fue de tres.
- **A favor de escribir las dos variantes:** Standard (1558677: la caja traía
  las dos, dos puntas o tres medios, y cubrió el once real) y Cobresal
  (1505547: la caja traía la variante exacta).

**Propuesta:**

1. **Con D1 🔶 (el DT alterna sistemas), o con T.54 de ≤ 2 partidos**, el
   sistema del partido es un supuesto. D1, el matchup H, la zona que afecta
   cada baja y la F3 por zona **se escriben en las dos variantes**, o se
   declaran «condicionados al once oficial». Es la regla de la v1.9 para B6 y
   F, ampliada al sistema.
2. **Un once de la API publicado antes del pitazo es nivel B** hasta la hora
   de captura del once oficial. Si la API corrige el grid, manda el último.
3. **Con el once, D1 y H se verifican sobre el grid** (paso 6 del cambio 1). Un
   H que acertó el resultado con otro sistema se registra como «mecanismo no
   verificado».

**Calculable, en parte.** El sistema del once sale del grid capturado. La app
ya lee las líneas del grid (`f1_base._lineas_por_grid`, `rolesVsGrid` en
sombra). Lo que no se calcula es si el sistema cambió respecto del D1
declarado, porque D1 es texto.

**Qué NO:** bajar D1 por alternar. Un DT que alterna con un patrón es 🔶, como
dice la tabla, no ❌.

### 3. EJE-DEBUTANTE: con el once se lee la línea entera del grid, y «condicional» con el once a la vista no vale

**Qué dice hoy (v1.9).** Sin once, va condicional («si repiten X–Y»). Con el
once, se declara o se descarta con el grid.

**Lo medido (48 lecciones: 25 aciertos, 12 parciales y 11 fallos).** La regla
se sostiene: las confirmaciones y los descartes están arriba. Lo que falla:
- **Con el once a la vista, la alerta quedó condicional:** Manchester City
  (1635710, Bouaddi en el banco y el parte rehecho conservó el condicional),
  Barcelona (1635627), Santos Laguna (1551031), Augsburg (1575213), Rio Ave
  (1575527, el parte no se rehízo) y São Paulo (1492448, once tardío). Es la
  regla 2 de la v1.9 sin aplicar.
- **La pareja nombrada no era la línea que jugó:**
  - Feyenoord (1635662): el once trajo Kraaijeveld–Mármol, una pareja todavía
    más nueva que la declarada (Watanabe–Mármol).
  - Westerlo (1558679): además del lateral, entró un central sin fila (Balogh)
    con el titular fijo al banco. Esa línea recibió cuatro en 14 minutos.
  - Los Chankas (1549542): la pareja salió dentro de una línea de cinco con un
    tercero sin fila.
  - Atlas (1551032): el grid corregido.
- **Amplía el rango sin materializarse, como dice la regla:** se repite la
  lista de la v1.9 (Necaxa, Espanyol, Libertad, Emelec, Lyon, 2 de Mayo,
  Stuttgart–Werder).

**Propuesta:**

1. **Con el once, el chequeo se hace sobre la línea entera del grid** (línea
   de fondo y doble pivote), no sobre la pareja que el parte había nombrado.
   La alerta nombra la pareja o el trío que salió.
2. **Con el once a la vista, EJE-DEBUTANTE no queda condicional:** se declara
   o se descarta. Si el once llega a menos de 20 minutos y no se puede rehacer
   (Westerlo), se escribe «once tardío, sin verificar», no «condicional».

**Calculable (app, ver A2).** Ya está pedido en la v1.9: `parejasNuevas` sobre
el once oficial capturado y los dos avisos. Se suma un tercer caso: la alerta
condicional con el once ya capturado.

**Matices de un caso, como nota y sin regla:**
- **Cruzeiro (1492444):** con un banco sin central de recambio, la alerta
  descartada por el once queda abierta hasta la primera baja atrás.
- **Universidad Católica (1505554):** el riesgo del eje es del equipo
  expuesto, no del replegado.
- **Stuttgart–Galatasaray (1635669):** el eje nuevo concedió en el arranque y
  después se asentó.

**Qué NO:** darle peso ni hacerla vía de gol por sí sola.

### 4. B6 y el arquero: sin fuente es sin dato, la base cuenta como fuente, y el suplente sin rodaje es una vía a vigilar, no una vía firme

**Qué dice hoy.**
- **v1.6:** B6 se rehace con el once oficial.
- **v1.7:** «Sin impacto documentado no es 🔶», escrito para B5.
- **v1.9:** «el suplente sin rodaje se declara al DTP como vía del rival», y
  en el mismo párrafo «el suplente de emergencia sin antecedentes de error no
  es una vía de gol». Las dos frases chocan cuando el suplente no tiene rodaje
  ni errores.

**Lo medido (27 lecciones de B5, B6 y el arco: 14 aciertos, 6 parciales y 7
fallos).**
- **B6 🔶 por falta de dato:** La Serena (1505551). B6 quedó en 🔶 por
  «recorrido de Tapia sin fuente», y Tapia sostuvo el 0-0 con 5 atajadas.
  Castigó la falta de dato como si fuera una debilidad.
- **B6 vacío con la base a mano:** OH Leuven (1558669). B6 quedó sin dato con
  8 titularidades de Van den Heuvel en la base, y el arquero decidió el
  partido.
- **B6 sin rehacer con otro arquero en la hoja:**
  - The Strongest (1645530): atajó un arquero sin fila en vez de Banegas (25 de
    25 como titular), y concedió 2,89 de xG.
  - Gaziantep (1584456): el arquero de la hoja no tenía fila.
  - Osasuna (1570448): B6 quedó «viejo», sin efecto numérico.
  - Rio Ave (1575527).
  - Universidad Católica (1639802): ocho rotados, el arquero incluido.
- **El suplente sin rodaje casi nunca fue la vía:**
  - Santa Clara (1575534): Neneca, sin minutos en la liga, hizo 6 atajadas.
  - Tolima (1549852): un suplente de cuatro partidos; solo le marcaron un
    penal.
  - Başakşehir (1584463): la vía de media distancia contra Dilmen no dio.
  - OFI (1593350): Lilo atajó 3.
  - Aston Villa (1635627): con GK-DOWNGRADE, ningún error y 5 atajadas.
  - **No se puso a prueba:** Roma (1550187) e Internacional (1492446).
  - **El único a favor:** Gremio (1492445). El costo llegó por el rechace, no
    por el error: dos rechaces de Grando terminaron en goles.

**Propuesta:**

1. **B6 sin fuente es `sin dato`, no 🔶**, igual que B5 desde la v1.7. Pero
   **las titularidades del arquero en la base (`f1/{id}`) son fuente**: con
   ellas B6 se puntúa y no se deja vacío.
2. **Con el once, B6 y la zona GK se calculan sobre el arquero de la hoja**
   (paso 3 del cambio 1). Ya era regla en la v1.6, ahora se cobra.
3. **El suplente sin rodaje** (< 15 partidos en la categoría y sin
   titularidades recientes) **baja al DTP como vía a vigilar**, que amplía el
   rango. **Es vía firme solo con GK-FALLA-ACTIVA o con errores documentados
   en crónica.** Así se resuelve la contradicción de la v1.9 en favor de lo
   medido: 1 caso a favor (Gremio, por el rechace) y 5 en contra.

**Calculable (app, ver A2).** El arquero del día y los dos arqueros que se
alternan salen de las alineaciones. Ya está pendiente desde la v1.9.

**Qué NO:** tocar el ×1,5 de F2c, el umbral de 15 partidos ni el de ≥ 2
errores de GK-FALLA-ACTIVA.

### 5. La sanción calculada de la base: la roja es nivel 1, el ciclo de amarillas es probable

**Qué dice hoy (v1.9, cambio 4.3).** «La sanción calculada de la base es nivel
1: es una regla del reglamento, no una noticia. Le gana a una previa.»

**Lo medido (18 lecciones: 7 aciertos, 5 parciales y 6 fallos).** Contradice
la regla vigente en su parte de amarillas.
- **La roja de la misma competición acertó:**
  - Cusco (1549550): la roja directa de Lagos del 01/11; no estuvo en la hoja.
  - Antwerp (1558671): HLN, vía dos agregadores, daba a Benítez sancionado. La
    base no lo tenía, porque su roja era del 11/10, y jugó 72 minutos. La base
    mandó con razón.
- **El ciclo de amarillas calculado falló cinco veces:**
  - Fenerbahçe (1635658): Škriniar, por la 3.ª amarilla de UEFA, jugó los 90.
  - Sabah (1635745): Lepinjica figuraba con certeza «probable» y fue titular;
    el 1X2 se movió de 68/18/14 a 64/20/16 al rehacer.
  - Shakhtar (1635723): Marlon Gomes figuraba sancionado y fue titular.
  - Sevilla (1570438): la base daba la 5.ª amarilla de Isaac y la prensa,
    apercibido con 4. El parte siguió a la prensa y acertó.
  - Riestra (1493235): Céliz entró a `fuera` por el ciclo y fue titular.
- **La sanción de otra competición:** la roja de liga no suspende en la copa.
  - Nacional Potosí (1645455): Núñez entró y asistió.
  - Always Ready (1645456): el parte dio de baja a Rambal y jugó y marcó.

  La base ya lo calcula así (`sancion_de_otra_competicion`); el parte no lo
  siguió.
- **La base no agota las bajas:** Real Madrid (1570451). Vinícius cumplía el
  cuarto partido de una sanción larga que la base no traía; lo dijeron la
  prensa y la convocatoria.

**Propuesta:**

1. **La roja (directa o por doble amarilla) en el último partido de la misma
   competición es nivel 1.** Le gana a una previa que lo pone titular.
2. **El ciclo de amarillas calculado es `probable`.** Va a `fuera` como ⚠️
   Duda con su rama en la caja de sensibilidad («si juega X…»), no como ❌
   Baja.
   - **Pasa a Baja** si lo confirma el club o la prensa de nivel 1-2.
   - **Pasa a disponible** si la prensa del club o nacional da el conteo y lo
     contradice. Se declara la contradicción, como en Sevilla.
   - **En competiciones de UEFA, con su ciclo propio,** va siempre
     condicionado a la hoja.
3. **Una sanción de otra competición no saca al jugador**, salvo norma
   publicada que diga lo contrario.
4. **Una sanción de varios partidos** (suspensión por fechas, apelación) la
   trae la prensa o la convocatoria. Que la base no la tenga no la borra.
5. **Con la hoja, manda la hoja** (ya escrito).

**Calculable, en parte.** La 1 y la 3 ya las calcula la app. La 2 pide que la
app separe la certeza de la roja de la del ciclo y que la alerta lo diga (A3).
Lo demás es fuente.

**Qué NO:** sacar la sanción calculada del F1. La roja acertó y el ciclo sirve
como Duda.

### 6. La rama «once alternativo»: también la abre una rotación anunciada o de costumbre, y la F3 de una rotación elegida es F4

**Qué dice hoy.**
- **v1.7:** con una eliminatoria a ≤ 5 días o el 3.er partido en 8 días, la
  rama se abre y el porcentaje queda condicionado al once.
- **v1.9:** en copa, la rama va a los dos lados, con el banco que vuelve.
- **Sin calendario exigente:** «la rama se escribe, no se presume».
- **v1.7, F4:** el no convocado por descanso va a F4, no a F2.

**Lo medido (20 lecciones de la rama: 11 aciertos, 5 parciales y 4 fallos,
más cinco citadas desde la tabla F1).**
- **El recomputo no se hizo** (≥ 3 titulares fijos rotados, ya es regla):
  - Carabobo (1646931): con ocho rotaciones, el bloque B siguió «sin cambio» y
    el once alternativo hizo los dos goles.
  - Universidad Católica (1639802): ocho rotados y el porcentaje publicado fue
    el del equipo que no jugó.
  - Atlético-MG (1492441): seis fuera de la hoja y el 66,7 % sin recomputar.
  - Guaraní (1632051).

  Es la alerta pendiente `EFE-RECOMPUTO-PENDIENTE` (A2).
- **Rotación sin calendario exigente:**
  - **De costumbre:** Monagas (1646932), con un DT que rota 6 por fecha y sin
    nada en juego.
  - **Del eliminado:** Puerto Cabello (1646933, «el eliminado podía rotar
    otra vez»).
  - **Anunciada por una fuente:** Frosinone (1550181, «Alvini potrebbe
    cambiare la difesa») y Juventus (1550182, la fuente daba otra línea).
  - **En los cinco casos, los rotables no tenían fila.**
- **La F3 contra el XI de referencia cuando la rotación fue elegida:** Puerto
  Cabello (1646933). Con IP 9 en rojo y GK y MID en rojo por la rotación, ganó
  de visita. La degradación se midió contra un equipo que el DT eligió no
  poner.
- **El descarte sin hecho:** Real Potosí (1645457). Se descartó la rotación
  porque «viajó el plantel completo», y rotó en los cambios. Always Ready
  (1645456): «repite once por tercera vez», y no repitió.
- **La rama cubre la dosificación en vivo:** Mechelen (1558674: repitió el once
  y rotó con cambios tempranos) y Olimpia (1632054: rotó en el entretiempo con
  la ventaja hecha). Es la línea del banco de la v1.9 (Atlético de Madrid).
- **En contra de abrir de más:** Arsenal (1557457), Excelsior (1552213) y
  Libertad (1632052) repitieron el once con el calendario exigente. La rama
  declarada no costó nada.

**Propuesta:**

1. **La rama también se abre**, aunque no haya calendario exigente, con:
   - una **rotación anunciada** por el DT o por prensa de nivel 1-3;
   - un **DT que rota de costumbre**, según el F4 de sus últimos onces;
   - un **equipo sin nada en juego o ya eliminado**.

   En estos tres casos va **en la caja de sensibilidad y en la tabla F1** (los
   rotables con fila). El porcentaje queda «condicionado al once» solo con
   calendario exigente o con un anuncio de nivel 1-2. «Se escribe, no se
   presume» sigue: lo que abre la rama es un hecho, no la sospecha.
2. **«Viajó el plantel completo» o «repite el once» no descartan la rama**
   sin el once oficial ni una crónica: son nivel C.
3. **La ausencia por rotación elegida va a F4 y no infla F2 ni la F3** (regla
   de la v1.7 aplicada a la rama). La F3 se mide contra el once alternativo
   escrito, no contra el XI de referencia.
4. **La rama nombra también la dosificación en vivo** (cambios tempranos,
   entretiempo con la ventaja hecha) cuando el calendario la pide.

**Calculable, en parte.** `EFE-RECOMPUTO-PENDIENTE` y el F4 de los últimos
onces salen de las alineaciones. La rotación anunciada es texto.

**Qué NO:** abrir la rama por defecto en cada partido, ni condicionar el
porcentaje por una sospecha.

## Matices que no son cambio (se escriben como nota)

- **B5 con dos partidos de banco decisivo.** La v1.9 dice que un solo partido
  no fija B5 alto. Dos partidos seguidos bajo el mismo DT con goles o
  asistencias de suplentes ya son impacto documentado:
  - Famalicão (1575539): el interino.
  - San Lorenzo de Paraguay (1632053): Salcedo y Amarilla.

  Confirmado además en Sport Boys (1549540: Alarcón, otra vez desde el banco),
  Dortmund (1635651: la misma dupla), Lazio (1550183), Fenerbahçe (1635658:
  Muriqi), Palmeiras (1492447), Táchira (1646929) y Fluminense (1492449).
  **Aucas (1639802):** B5 se mide por quién puede entrar contra el rival de
  hoy. Es una aclaración de evidencia, como «un solo partido no es evidencia»
  en GK-DOWNGRADE, **no un umbral de puntuación nuevo**: si el usuario lo
  quiere como regla, se escribe con estos dos casos.
- **La zona cubierta reconvertida se escribe aunque el porcentaje quede en
  ámbar.**
  - **Lens (1635681):** la reducción DEF dio 28,6 % porque la línea se cubrió
    con nombres (Aguilar reconvertido), y concedió nueve. Es el «quién la
    cubre» de la v1.9 aplicado también fuera del rojo.
  - **Como (1635681):** el parte no nombró la zona, y el que generaba jugaba
    en el medio entero. Incumplimiento de la regla de la v1.7.
- **El recambio de oficio sostuvo la zona** en PSG (1635746), Inter (1635662),
  Paris FC (1552807), Bayern (1635622, Jev `lectura_efe`), Real Madrid
  (1570440), Lyon (1552804, Nuamah reconvertido de 9) y Telstar (1552214).
  Confirma «degradada, cubierta de oficio» de la v1.9. Dortmund (1575212): sin
  Guirassy, la segunda línea cubrió el área.
- **La F3 en ATK se paga en la conversión más que en el volumen** en San
  Lorenzo (1493238) y Mirassol (1492443). La F3 por GK que el rival no ataca
  ni confirma ni refuta (Roma 1550187, Internacional 1492446): eso lo dice el
  veredicto, no la rúbrica.
- **La brecha en la misma base:** dos contraejemplos.
  - Göztepe (1584463): 73,4 contra 59,6, sin T.54, y perdió con un xG parejo.
  - Getafe–Sevilla (1570438): ganó el de 32,4 %. El E en 0 se leyó como estado
    del local con dos derrotas fuera, y la v1.9 ya pide leer el E en la
    condición.
  - **Cubiertos por «no descarta el empate»:** Sevilla–Alavés (1570450, 0-0)
    y Trinidense (1632050, parejo, con viaje y 3 días de descanso).

  **No mueve la regla.** Sigue la medición pendiente (A6).
- **Candidato «la brecha se lee con la confianza efectiva»** (v1.9, dos a
  favor y uno en contra). Suma América–Toluca (1551026): FORMADO 72 % con la
  zona MID en rojo, contra 69 % con IP 0,5, y el porcentaje no ordenó. Quedan
  tres a favor y uno en contra. **Sigue candidato.**
- **COLAPSO + AGRAVANTE** (v1.9: tres casos, sigue candidato).
  - **A favor:**
    - La Louvière (1558665): D3 ❌ de visita, con T.54 y EJE-DEBUTANTE en el
      mismo lado, 0-4 al 49'.
    - Remo (1492447): D3 ❌ de visita, recibió al 4', 0-4 al 36'. Si el parte
      tenía R-KT.2 en Remo, es la forma de Marítimo; hay que verificarlo en el
      parte.
  - **En contra:** Elversberg (1575212). Con D3 ❌ de visita y recién
    ascendido (R-KT.2, el agravante de Marítimo), perdió 2-1 sin romperse.
  - **Sigue candidato.** Un agravante nuevo (T.54 + eje nuevo) con un solo
    caso no se suma a la regla.
- **Candidato D3-DEGRADADO** (v1.6, dos casos). Suma Villarreal (1635746: D3
  🔶 y cuatro goles en ocho minutos ante el PSG) y Pereira (1549852: D3 🔶
  medido solo de visita, y de local concedió dos más en cinco minutos). Quedan
  cuatro casos.
  - **En la misma línea, ya escritos en la regla de contexto de la v1.7:**
    Manchester United (1635695: el D3 ❌ de dos visitas de Premier no viajó a
    un local de Champions, y remontó), Atlético de Madrid (1635622: el ✅ de
    LaLiga no viajó contra el Bayern) y Slovan (1635677: leído en la
    competición, se cumplió).
  - **Sigue candidato.** Ver «Cuándo se reabre».
- **El DT se verifica en cada parte, no se arrastra de un parte viejo**:
  Kasımpaşa (1584462, Jev `insumo`). El bloque A se puntuó con Belözoğlu, que
  se había ido el 03/11; Schreuder se oficializó el 04/11. Es la regla de la
  v1.8 («oficializado en los 7 días previos = banco que dirige»). Es un insumo
  y va a la app (A5).
- **D4 dice qué se juega junto con el rol:** Sport Boys (1549535). «Media
  tabla» no decía que peleaba un cupo a la Sudamericana. Un caso: es la línea
  del E de la v1.8 («dice qué se juega»).
- **La K por condición contra rivales de su liga no representa el cruce con
  otra escala:** Leipzig–City (1635710). Es ESCALA-LIGAS aplicada al bloque C.
- **Bloque H:** Leeds–Tottenham (1557463). La superioridad por banda sin
  remate dentro del área no hace desfavorable el matchup del que cede la
  pelota. Un caso.
- **FACTOR-X amplía el rango, no mueve el centro.** Confirmado en Beveren
  (1558677), Sparta (1552215) y La Serena (1505551, por el lado contrario:
  expulsado al 48'). Bien no activado en Arsenal (1557457: Saliba no estaba en
  la hoja).

## `efe-dashboard` v1.12: sin cambio

La rama de goleada en «Para perder» (v1.12) quedó mezclada.
- **Se cumplió por el gatillo del gol temprano:** Panetolikos (1593353, abrió
  el rival al 11'), Remo (1492447, al 4'), La Louvière (1558665, al 6') y
  Villarreal (1635746).
- **No se cumplió:** Mainz (1575217: recibió al 14' y perdió por dos) y
  Gaziantep (1584462: recibió al 3' y perdió 0-2).

No hay números para la banda: se sigue calibrando con más casos. Lo que baja
al dashboard de esta revisión es el dibujo de las dos variantes del sistema
(cambio 2) y la rama abierta por anuncio (cambio 6) en la caja de
sensibilidad.

## Para la app, no para el skill

Ordenado por cuántas lecciones cierra. Ninguno cambia un número del motor ni
un peso: son avisos de tipo `dato` y campos que leen lo que ya está en la base.

**A1. La tabla F1 contra el once, al depositar** (cambio 1; 37 lecciones de 34
partidos desde el 03/11).
- **Hoy:** `ONCE-SIN-FILA-F1` sale al leer (`parte.py`) y su texto dice «con 3
  o más, rehacer».
- **Se propone:**
  1. **En el recibo del depósito**, si el once está capturado, en `faltan`:
     los titulares sin fila y las bajas o dudas de `fuera` que figuran en la
     hoja (Táchira 1646929). El segundo es un aviso nuevo, propuesto como
     `BAJA-EN-LA-HOJA`, tipo `dato`, calculado.
  2. **El texto de `ONCE-SIN-FILA-F1`** dice «con el once a la vista, los once
     titulares llevan fila», sin el umbral de 3.
  3. **`GET /analisis/cowork/f1/{id}` con el once capturado** trae
     `onceOficial`: cada titular con `jugadorId`, la zona del grid y
     `rolSugerido`, listo para copiar.
- **Para decidir (usuario):** que el cierre del bloque F sume solo la fila del
  titular que falta, con el rol sugerido y marcada como agregada por la app, en
  vez de pedírsela a Cowork. Es coherente con «lo calculado no se le hace
  copiar», pero cambia el IP que la app calcula, porque entra un jugador que
  antes no pesaba. Por eso no se propone sin decisión.
- **La rutina de rehacer** (`corrida-sad`, modo `rehacer`, y `docs/COWORK.md`)
  suma el orden del cambio 1, con la tabla F1 primero.
- **Test:** en `test_cowork`. La alerta nueva va en `_ALERTAS_CALCULADAS` y en
  `docs/openapi.yaml`, porque `test_arquitectura` lo exige.

**A2. Lo pendiente de la v1.9, que esta tanda vuelve a pedir** (ya está en
`PENDIENTES.md`):
- **`EFE-RECOMPUTO-PENDIENTE`:** Carabobo 1646931, Universidad Católica
  1639802, Atlético-MG 1492441 y Guaraní 1632051.
- **`EJE-DEBUTANTE-SIN-DECLARAR` y `-SIN-OBJETO`, sobre el once oficial:** se
  suma el caso de la alerta que sigue condicional con el once capturado (City
  1635710, Barcelona 1635627, Santos 1551031 y Augsburg 1575213). Se propone
  como un tercer aviso, `EJE-DEBUTANTE-CONDICIONAL-CON-ONCE`, o como variante
  de `-SIN-OBJETO`.
- **El `recambio` por zona en `f1/{id}` y los nombres de la prosa sin fila F1:**
  Guabirá, Racing de Santander, Lommel, Braga, Independiente del Valle,
  Athletic, Pasto y Telstar, en el cambio 1.
- **El arquero del día y los que se alternan:** The Strongest 1645530,
  Gaziantep 1584456, Osasuna 1570448 y PAOK 1593351 (en cuarentena). Con el
  once, un aviso si el arquero de la hoja no es el de B6.

**A3. Sanciones** (cambio 5).
- **`backend/sanciones.py` y `f1/{id}.sancionados`:** que la certeza separe la
  roja (`segura`) del ciclo de amarillas (`probable`). La alerta
  `SANCION-SIN-DECLARAR`, para el ciclo, dice «baja o duda con su rama», no
  «van de baja».
- **Para verificar como incidencias** (pueden ser errores del conteo, no de la
  regla):
  - **El ciclo de UEFA** (`UMBRALES` 2, 3 y 848) dio tres sancionados que
    jugaron: Škriniar (1635658), Lepinjica (1635745) y Marlon Gomes (1635723).
    Hay que mirar qué partidos entran al conteo.
  - **Isaac (Sevilla, 1570438):** la base contó 5 amarillas y la prensa, 4.
    Puede ser una tarjeta mal atribuida (identidad).
  - **Afonso Sousa (Samsunspor, 1584465):** la API seguía con la roja y la
    prensa del club la daba cumplida.

**A4. Identidad y filas de la tabla** (`backend/identidad.py`, con su test en
`test_identidad`).
- **Vitória (1492449):** «Mateus Silva», una fila sin `jugadorId`, era el
  «Mateusinho» de la plantilla (308148). Dos filas para una persona sumaron al
  IP una baja que jugó. Hay que cubrir el apodo y el diminutivo.
- **Botafogo (1492441):** la tabla traía `jugadorId` cruzados con otro nombre
  (Alex Telles con el id de Marçal, entre otros). Se propone que el recibo
  avise si el `jugadorId` de una fila no casa con el nombre de esa fila en la
  plantilla.
- **Unión (1493241):** el parte descartó a Pittón por «juega en otro club»
  usando el nombre. La regla de la base (`jueganEnOtroEquipo`) es por id; el
  recibo podría avisar del descarte sin id.
- **Leones del Norte (1639858):** el arquero quedó sin fila por la duda de
  identidad.

**A5. El DT del parte contra el de la base** (Kasımpaşa 1584462). Hay que
verificar por qué no sonó ningún aviso si Schreuder se oficializó el 04/11 y el
parte del 06/11 puntuó a Belözoğlu. Pueden ser tres cosas: el DT de la base
viejo (`jugadores --dt-agenda`), un `dt.desde` arrastrado de un parte anterior
o `T.54-SIN-DECLARAR` sin dato. Va como incidencia.

**A6. La medición del empate técnico, y menos lecciones de confirmación.**
- **Lo pendiente desde la v1.9:** la tasa del de mayor porcentaje con y sin
  `EFE-EMPATE-TECNICO`, en Aprendizaje.
- **Lo nuevo:** con esa medición hecha, el veredicto (`corrida-sad`, modo
  `veredictos`) deja de escribir una lección por cada «empate técnico
  declarado y cumplido». Son 100 de 416 lecciones en esta tanda; las cuenta la
  métrica y la lección sobra. Es un cambio del skill de corrida y del prompt,
  no del EFE, y lo decide el usuario.

## Lo que no cambia

- **Los pesos y la tabla de puntuación:** A 1×, B 1,5×, C 1×, D 1× y E 2×; el
  máximo de 27 y 23; los cortes 70/40; la regla especial D3; la regla especial
  B.
- **La F3** (IP > 7, ≥ 2 titulares fijos o una zona > 40 %) y los cortes de
  zona.
- **El ×1,5 del arquero en F2c**, el umbral de 15 partidos de B6 y
  GK-DOWNGRADE, y el de ≥ 2 errores de GK-FALLA-ACTIVA.
- **La regla del empate técnico de formación** (v1.7) y su cálculo
  (`EFE-EMPATE-TECNICO`).
- **T.54 / T.54-B** y sus criterios, con la fecha del DT (v1.8).
- **COLAPSO EN CASCADA:** describe el escenario, no predice ni la goleada ni
  la ruptura (v1.6 y v1.9).
- **EJE-DEBUTANTE y FACTOR-X:** declarativas, sin peso, amplían el rango.
- **Lo que el parte no trae porque lo calcula la app:** total, porcentaje,
  clasificación, IP, reducción por zona, F3, F4, el bloque F por el once y el
  bloque G desde `backend/calendario.py`. Un bloque sin puntuar no es cero.
  Los sancionados salen de la base.

## Lo que NO se propone y por qué

- **Ningún peso, máximo, corte ni multiplicador.** Ninguna lección lo pide y
  Jev no marcó ninguna para mover un número. La `lectura` del dossier lo dice.
- **Endurecer la regla de la tabla F1 con un número de filas.** El problema no
  es la regla, es que no se cobra: el cambio 1 fija el orden y la app (A1)
  avisa al depositar.
- **Volver regla a COLAPSO + AGRAVANTE, D3-DEGRADADO o «la brecha con la
  confianza efectiva».** Siguen candidatos: tienen casos a favor, pero también
  contraejemplos (Elversberg) o muy pocos casos.
- **E3 con «sin ganar».** Sigue candidato desde la v1.8. Esta tanda no trae
  casos nuevos.
- **Subir el D3 de la Liga MX** (Tijuana, 1551025, otra vez). Es un caso, y Jev
  no lo marca para mover un número.
- **B5 «con dos partidos» como umbral de puntuación.** Va como aclaración de
  evidencia, salvo que el usuario lo pida como regla.
- **Números en la banda de goleada del dashboard.** El gatillo del gol
  temprano salió mezclado.
- **Que la app sume sola las filas del once (A1, para decidir).** Cambia el IP
  calculado. No se hace sin la decisión del usuario.

## Cuándo se reabre

- **El cambio 1 y A1:** si con el aviso en el recibo los titulares sin fila
  siguen apareciendo en más de 5 partidos por semana, la app los suma sola
  (opción para decidir de A1).
- **COLAPSO + AGRAVANTE:** con 5 casos de un mismo agravante y su cuenta de
  contraejemplos (hoy, R-KT.2 de visita: Marítimo, quizás Remo, y Elversberg
  en contra).
- **D3-DEGRADADO:** con la próxima tanda que traiga un 🔶 medido en otra
  condición o competición que recibe primero, contando también los que no
  colapsaron.
- **«La brecha con la confianza efectiva»:** con 5 casos a favor y la cuenta
  de los que van en contra. Es calculable: la F3 la calcula `bloque_f.py` y
  `EFE-EMPATE-TECNICO` podría contarla.
- **El empate técnico:** cuando Aprendizaje tenga la tasa del de mayor
  porcentaje con y sin la alerta (A6). Si el de mayor porcentaje gana con la
  alerta tanto como sin ella, la regla se revisa con ese número, no con
  lecciones.
- **El suplente sin rodaje (cambio 4):** si en una tanda la vía firme por
  error del arquero aparece en 3 o más partidos sin GK-FALLA-ACTIVA previa.
- **La sanción por ciclo (cambio 5):** cuando A3 diga si los tres casos de
  UEFA fueron error del conteo. Si el conteo estaba bien y la regla de UEFA
  es otra, se corrige `UMBRALES` y el ciclo de UEFA puede volver a nivel 1.

## Cómo se aplica si se aprueba

1. **Skill:**
   - **La rúbrica** pasa a `references/rubrica-efe-v1.10.md` (con `git mv`
     desde la v1.9), con el changelog de los cambios 1 a 6 y las notas. Cada
     cambio va en su bloque:
     - el orden del rehacer y la baja que está en la hoja (F1 y el protocolo);
     - el sistema condicionado (D1, H y F2b);
     - la línea entera del grid (EJE-DEBUTANTE, en alertas y en la tabla
       resumen);
     - B6 sin dato o con la base, y el suplente como vía a vigilar (B6);
     - la roja y el ciclo (la jerarquía de fuentes del F1);
     - la rama por anuncio o costumbre y la F3 de la rotación elegida (F4 y el
       protocolo sin XI).
   - **De paso,** se corrige el «Eres un analista… aplicar el EFE v1.7» de la
     cabecera (DEUDA 21).
   - **`SKILL.md` en v1.10** cambia dos líneas de «Reglas que no se negocian»:
     - la de la jerarquía en las dos direcciones: la sanción de la base es
       nivel 1 solo por roja;
     - la del eje: la línea entera, sin condicional con el once.

     Y suma dos:
     - el rehacer empieza por la tabla F1;
     - el sistema se verifica con el once con D1 🔶 o T.54 corta.
2. **`efe-dashboard` v1.13** (opcional): las dos variantes del sistema y la
   rama por anuncio en la caja de sensibilidad. Sin números.
3. **App (cada punto por separado, con su test):**
   - `lecciones.CORTE_VERSION["efe-clasificador"]` suma `("v1.10", <fecha>)`,
     para que «Cerrar las anteriores» cierre estas 416.
   - A1 a A6, en ese orden. Las alertas nuevas (`BAJA-EN-LA-HOJA` y la
     variante de EJE-DEBUTANTE) van en `_ALERTAS_CALCULADAS`, en
     `docs/openapi.yaml` y en `test_cowork`.
   - Lo que no se haga queda en `PENDIENTES.md`.
4. **`docs/COWORK.md` y `corrida-sad` (modo `rehacer`):** el orden del cambio
   1.
5. **Zips para subir a la cuenta,** y anotar la hora en `SUBIDA_VERSION`.

## Resumen: qué lecciones cierra cada punto

| Punto | Lecciones | Partidos | Aciertos / parciales / fallos | Copa | Tipo |
|---|---:|---:|---|---:|---|
| 1 · El rehacer empieza por la tabla F1; la baja en la hoja | 80 | 74 | 32 / 23 / 25 | 1 | regla (cobrar la v1.9) + calculable (A1) |
| 2 · El sistema con el once (D1, H) | 3 | 3 | 1 / 0 / 2 | 0 | regla, calculable en parte (+6 casos citados de otros grupos) |
| 3 · EJE-DEBUTANTE: la línea del grid, sin condicional | 48 | 44 | 25 / 12 / 11 | 0 | regla + calculable (A2) |
| 4 · B5, B6 y el arco | 27 | 27 | 14 / 6 / 7 | 0 | regla + nota de B5 + calculable (A2) |
| 5 · Sanción: roja nivel 1, ciclo probable | 18 | 18 | 7 / 5 / 6 | 2 | regla (corrige la v1.9) + calculable (A3) |
| 6 · Rama por anuncio o costumbre; F3 de la rotación elegida | 20 | 19 | 11 / 5 / 4 | 3 | regla + calculable (A2) |
| Jerarquía de fuentes (v1.7-v1.9): confirmación | 18 | 16 | 13 / 2 / 3 | 0 | sin cambio |
| F3 por zona: confirmación y matices | 43 | 40 | 27 / 5 / 11 | 0 | sin cambio (notas) |
| Brecha / EFE-EMPATE-TECNICO | 100 | 100 | 46 / 17 / 37 | 2 | sin cambio (medición A6) |
| T.54 / T.54-B y contradicciones de DT | 13 | 13 | 8 / 3 / 2 | 1 | sin cambio (+ A5) |
| COLAPSO EN CASCADA | 21 | 21 | 10 / 8 / 3 | 0 | sin cambio (candidatos) |
| D3, D4, C y sin dato | 22 | 19 | 7 / 7 / 8 | 0 | sin cambio (candidatos y notas) |
| FACTOR-X | 3 | 3 | 1 / 2 / 0 | 0 | sin cambio |
| **Total** | **416** | | **202 / 95 / 119** | **9** | |

La asignación es por la regla que cita cada lección y por su texto. Cada
lección cuenta en el primer grupo que la toma, en el orden de la tabla, salvo
la tabla F1, que va primero. Los partidos se cuentan por grupo y se repiten
entre grupos. Las cuentas se hicieron sobre el JSON del dossier del
08/11/2026 (02:31 UTC). Los conteos no son una tasa de acierto del skill
(`sesgoDeAtribucion`).
