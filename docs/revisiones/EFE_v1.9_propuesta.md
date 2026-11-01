# Propuesta de revisión · `efe-clasificador` v1.8 → v1.9

**Estado:** PROPUESTA, sin aprobar. Escrita el 01/11/2026 desde las **296
lecciones pendientes** del dossier (294 de `efe-clasificador` y 2 de
`efe-dashboard`). Salen de los partes del 28/10 al 01/11, escritos con la v1.8.
La única excepción es una lección del dashboard del 24/10. La base es la v1.8
vigente (`docs/skills/efe-clasificador/`, `references/rubrica-efe-v1.8.md`) y
`efe-dashboard` v1.11.

## De dónde sale

- **296 lecciones:** 170 aciertos, 51 parciales y 75 fallos. Todas son
  `ciega` + `PRE`.
  - **43 son de copa nacional** (Copa del Rey del 29/10). Fijan rúbrica y no
    entran a ninguna métrica (población `copa`).
  - **9 están en cuarentena automática** por un DT distinto en el parte: Peña
    Sport, Numancia–Oviedo, Prat y Guijuelo.
  - **253 podrían sostener un cambio de peso** (`puedeMoverNumeros`).
- **Ninguna pide mover un número.** Jev no marcó ninguna con
  `proponeMoverNumero` (292 sin etiqueta, 4 en `false`). De los 23 fallos
  etiquetados, 16 son `lectura_efe` y 3 son `insumo`. Esta versión no toca
  pesos, máximos, cortes de la tabla de puntuación ni el ×1,5 del arquero. Los
  umbrales que se mencionan ya existen en la rúbrica.
- **Sesgo de atribución, más fuerte que en la v1.8.**
  - **Brecha:** 94 lecciones (casi un tercio) son de la regla de la brecha.
    Casi todas dicen «declarada y cumplida» aunque el lado salga como fallo
    (Parma–Udinese 0-0, Caracas–Monagas, Juárez–Querétaro). Ahí el fallo es
    del 1X2 o del empate, no del EFE.
  - **Incumplimientos:** muchos «fallos» del EFE son de reglas que ya están
    escritas y no se aplicaron: fuentes con fecha, recomputo con el once,
    arquero con rodaje. Eso pide **cobrarlas**, no reescribirlas. Donde se
    puede calcular, se propone que lo calcule la app.
- **Ya decidido el 31/10, no se re-propone:**
  - **Porcentaje (incidencia 799):** el porcentaje del EFE se calcula sobre los
    bloques declarados y con menos de 3 no hay porcentaje.
  - **Tabla F1 de la base (683, 1008, 1032):** un titular de los últimos 3
    onces entra aunque falte en la plantilla. La identidad funde los ids que se
    alternan y marca `posibleMismoQue`. Los que juegan en otro club salen
    (`jueganEnOtroEquipo`).
  - **Cómo se usa acá:** cerraron parte del problema de la tabla F1 (cambio 1)
    y de los huecos de copa (se citan en «Lo que la v1.8 acertó»).

## Lo que la v1.8 acertó y no hay que tocar

- **La brecha con T.54 / R-KT.2 / ESCALA-LIGAS es empate técnico.** Se
  confirmó en unas 60 lecciones, con 22 casos en que ganó el de menor
  porcentaje. Algunos:
  - Rayo–Celta: 26 puntos en contra, 3-0.
  - Bournemouth–Leeds, Anderlecht–Westerlo, Ajax–AZ.
  - Coritiba–Vitória: 28 puntos, 2-0 con 2,16 xG.
  - Pachuca–Tigres, San Lorenzo–Libertad: 49 puntos, ganó el de 14 %.
  - Villarreal–Espanyol, Cambuur–GAE, Juárez–Querétaro.

  `EFE-EMPATE-TECNICO` la calcula la app y se dejó de olvidar.
- **T.54 en los dos lados con la fecha del DT (cambio 1 de la v1.8).**
  - **Confirmaciones (13):** Olympiakos con Imanol, Willem II con interino de
    diez días (SIN FORMACIÓN y dos goleadas), Aldosivi (las dos fechas
    casaron con el banco), Cerro Largo, O'Higgins–Ñublense y Comerciantes.
  - **Lo que da T.54 pleno:** dice cuánto creerle a la K, no que el equipo se
    caiga ese día (Espanyol ganó con un interino de dos días, 1570442).
- **El arquero con rodaje (cambio 2 de la v1.8), donde se aplicó.**
  - **Suplente con rodaje que sostuvo:** Pirard (Standard, 4 atajadas), Vera
    (Independiente Petrolero, 7 atajadas a 3.900 m), Cleiton (Bragantino, 24
    titularidades) y Montoya (América de Cali, +0,62 goles evitados).
  - **GK-DOWNGRADE que se cumplió:** Bodart (Le Havre, 0 de 8 y cinco
    goles), Suzuki (Aston Villa, autogol) y Arzamendia (Riestra, un partido
    en el año y tres goles con 0,24 xG).
- **Las fuentes con fecha y la jerarquía (cambio 4 de la v1.8).** Catorce
  confirmaciones:
  - **Duda que jugó:** Romo (Chivas: más de 7 días, asistió el 1-0), Ndoye y
    Williams (Forest), Karetsas (Dortmund, asistió el 2-2), Wiechniak
    (Luqueño) y Alomía (Chico: sanción sin plazo publicado, marcó).
  - **Prensa del día que acertó el once:** la previa del día anterior le ganó
    al último once (Cádiz, 7 de 11) y la prensa local acertó 7 de 7 del once
    de copa (Zamora).
- **Sin dato es respuesta válida (y la 799).** Diez casos de copa con equipos
  que la base no sigue dejaron bloques vacíos y no ordenaron el partido con un
  número falso: Hortaleza, Calatayud (porcentaje nulo, no 0 %), Prat,
  Guijuelo, Covadonga, Laredo, Lebrijana, Peña Sport, Varea y Ribadesella. Un
  porcentaje de un equipo sin datos es hueco, no «sin formación».
- **COLAPSO EN CASCADA no predice goleada.**
  - **Sin goleada, como se escribió:** Santa Fe (1549724), Manchester United
    con diez (1557450), Central Español (recuperó con el banco en 13
    minutos), Crystal Palace e Inter (no activada, sin colapso).
  - **Contraejemplos:** se miran en el cambio 6.
- **La caja de sensibilidad bajada al partido (cambio 5 de la v1.8).**
  Describió el escenario en Atlante («Herrera rota tras tres fechas con el
  mismo once»: rotó tres y la línea se rompió), en Chivas («Romo vuelve») y en
  ABB. En ABB, lo heredado que T.54 deja sin dato siguió valiendo como
  sensibilidad del plantel.

## Los siete cambios propuestos

### 1. La tabla F1 lleva al equipo que puede jugar, no solo al último once

**Qué dice hoy.** F1 es «14-16 jugadores clave»: los titulares habituales y los
refuerzos. Desde el 31/10 la base suma a los titulares de los últimos 3 onces.
No dice nada de los **recambios** de una baja ni de los **rotables**.

**Lo medido (23 lecciones, 12 aciertos, 6 parciales y 5 fallos).**
`ONCE-SIN-FILA-F1` sonó en casi todas: un titular jugó sin fila y el IP leyó
otro equipo.
- **El reemplazo del sancionado o del lesionado:**
  - Galatasaray (1584455): Singo por Bardakcı.
  - Fenerbahçe (1584451): Peprah Oppong con Aké en duda.
  - Juárez (1551021): E. López de central.
  - Puebla (1551022): J. Pachuca con el pivote suspendido.
  - Delfín (1639830): Caicedo y Cisneros.
  - Táchira (1646924): V. Adamo hizo el único gol.
- **El rotable con la rama «once alternativo» abierta:**
  - Sporting (1575531): Pedro Lima hizo el 0-1.
  - Bologna–Monza (1550179): Colombo, Zeballos y Vitík. Colombo ya estaba
    nombrado en la caja.
  - Eldense (1644343): cinco titulares sin fila.
- **El titular nombrado en la prosa o en la nota del bloque B:**
  - 2 de Mayo (1632045): C. Saiz, usado como vulnerabilidad en EFE, DTP y
    matriz.
  - Rizespor (1584454): Görgen y Diakité.
- **El once oficial ya publicado antes del último depósito:**
  - Leeds (1557448): D. James.
  - Alavés (1570434): Benavídez, Guevara y Yusi.
  - Estrela (1575535).
- **Caras nuevas en el ataque:**
  - Rubio Ñu (1632049): Roldán y Acosta hicieron 3 goles y una asistencia sin
    fila.
  - Instituto (1493217): F. Suárez marcó al 3'.
- **El rol mal fijado:** Trinidense (1632049) puso a su goleador, F. Romero (7
  goles, 15 titularidades), como SUP con 0,5 porque arrancó en el banco la
  última fecha.

**Propuesta (sin tocar pesos ni el IP):**

1. **Por cada baja o duda, la tabla lleva a su recambio probable** en esa
   zona, aunque tenga pocos minutos o ninguno. El arquero suplente va siempre.
2. **Con la rama «once alternativo» abierta, la tabla lleva a los rotables**
   que la rama nombra.
3. **Todo jugador que el EFE nombra en la prosa** (bloque B, caja de
   sensibilidad, matchup) **tiene su fila**. Lo que no está en la tabla no
   pesa en el IP.
4. **Con el once oficial a la vista al depositar, los once titulares tienen
   fila.**
5. **El rol se fija por titularidades y participación de la temporada**, como
   ya dice la tabla de roles, **no por la última fecha**.

**Calculable (app, si se aprueba).**
- **Lo que ya existe:** `ONCE-SIN-FILA-F1` (743) avisa después del once.
- **Lo que se propone:**
  - Que el recibo del depósito avise si un nombre de la prosa del EFE (notas
    de bloque, caja) no casa con ninguna fila de la F1. Usa
    `backend/identidad.py`, como el cierre del bloque F.
  - Que `f1/{id}` sugiera un `recambio` por zona para cada baja o duda que
    sale de la base (`sanciones`, `Missing Fixture`): el que más minutos jugó
    en esa línea sin ser titular.

**Qué NO:** subir el tope de 14-16 filas como número. La tabla se agranda solo
con quien puede jugar hoy.

### 2. La rama «once alternativo» se escribe para los dos lados, con el banco, y el recomputo se cobra

**Qué dice hoy (v1.7).** Con una eliminatoria a ≤ 5 días o el tercer partido en
8 días, se abre la rama y el porcentaje queda «condicionado al once oficial».
Con ≥ 3 titulares fijos rotados, B y F se recomputan antes de cargar.

**Lo medido (28 lecciones, 20 aciertos, 3 parciales y 5 fallos).** La rama
acierta la dirección casi siempre (Burgos, Andorra, Osasuna, Antequera,
Hoffenheim, Palmeiras). Falla lo que queda alrededor:

- **El recomputo no se hizo:**
  - Libertad (1632047): cuatro rotados y el pivote al banco, y el 64 % quedó
    igual.
  - La Guaira (1646922): la rama escrita fue la que se jugó y no se
    recomputó.
  - Vasco (1492439): cinco del XI tipo al banco y la nota de B siguió con los
    laterales.
  - Atlético Baleares (1644343): ocho rotados, la F1 casó 6 de 11.
  - Burgos (1644357): 4 de 11 en la tabla.
- **El chico también rota en copa:**
  - Numancia (1644364): cinco titulares nuevos y un arquero debutante. La rama
    se aplicó solo al favorito.
  - Coruxo (1644350): seis fuera del XI de referencia.
- **El banco es parte de la rama:**
  - Inter (1550176): Chivu deshizo la rotación al descanso.
  - Sporting Gijón (1644356): los titulares que entraron dieron vuelta el
    partido.
  - Ceuta (1644368): Escobar entró al descanso y decidió.
  - Atlético de Madrid (1570439): con el Bayern a 3 días rotó en los cambios
    (67', 76'), no en el once.
- **El cambio de sistema:** Getafe (1644358) pasó de cinco a cuatro atrás, y el
  D1 🔶 ya lo anticipaba. Schalke (1575210) pasó de cinco a cuatro con Ayhan
  aunque la prensa de la víspera daba el sistema habitual.
- **Con T.54 de una o dos fechas, el XI de referencia no proyecta el once:**
  - Estoril (1575532): interino de dos partidos, cinco titulares cambiados,
    el arquero y el dibujo. El B6 se puntuó sobre Robles y atajó Turk.
  - FC Cajamarca (1549531): DT de siete días, tres cambios en la línea de
    fondo.
- **La previa de rotación es nivel C aunque acierte el sentido:**
  Atlético-MG (1492430) erró dos de cinco nombres.
- **El núcleo que vuelve:** Zulte Waregem (1558670) escribió como
  alternativa «vuelve el núcleo» y ese fue el once (Hedl, dos goles).
- **Sin la rama abierta:** Rennes (1552806), con 63 %, Europa League a 6 días
  y tres fijos en sus tres últimos onces, recibió cinco.

**Propuesta:**

1. **En una copa con liga a ≤ 5 días, la rama se escribe para los dos
   equipos**, no solo para el favorito.
2. **La rama dice tres cosas:** quién rota, **qué sistema** (si el DT ya usó
   otro en la temporada, D1 🔶) y **quién queda en el banco para volver**. Los
   titulares en el banco son la vuelta del once fijo si el marcador no se
   abre, no un dato aparte.
3. **Con T.54 de ≤ 2 partidos** (interino o DT de una semana), el XI de
   referencia es nivel C. B6 y el bloque F van **condicionados al once
   oficial** aunque no haya calendario exigente.
4. **El recomputo con ≥ 3 titulares fijos rotados ya es regla y se cobra.** Un
   parte re-depositado con el once oficial que no cambió B ni F con ≥ 3
   rotados es un incumplimiento, no una lectura.

**Calculable (app, si se aprueba).**
- **Alerta:** `EFE-RECOMPUTO-PENDIENTE`, tipo `dato`, al leer. Sale si el once
  oficial trae ≥ 3 titulares fijos de la F1 del parte fuera del once y el
  porcentaje o el bloque B del parte no cambiaron desde el depósito previo al
  once. Es la misma idea que `DTP-REHACER` y entraría a la rutina de rehacer.
- **Dato:** el número de partidos del DT para la regla 3 sale de `dt.desde`
  y de la base.

**Qué NO:** abrir la rama sin calendario exigente por defecto. «La rama se
escribe, no se presume» sigue. Palmeiras (1492438) repitió el once con la
semifinal a 4 días.

### 3. El arquero: el rodaje se mide en la categoría, y en el arco cuenta quién ataja

**Qué dice hoy.**
- **v1.8:** la F3 por zona GK no se activa sola si el suplente tiene ≥ 15
  partidos en la categoría o titularidades en los últimos 12 meses.
- **F2c:** «si el equipo tiene dos GK de nivel similar que rotan, no aplicar
  el multiplicador».

**Lo medido (16 lecciones, 7 aciertos, 4 parciales y 5 fallos).**
- **La regla de la v1.8 no se aplicó porque el rodaje se leyó en minutos de la
  temporada:**
  - Mönchengladbach (1575208): Batz tenía 90 minutos en la temporada y
    recorrido en la Bundesliga. La reducción GK quedó en 85,7 % y dejó el arco
    en cero con 4 atajadas.
  - Mechelen (1558666): De Wolf no tenía fila en la F1. La zona GK quedó al
    100 % y sostuvo el 1-0 con 5 atajadas.
- **Dos arqueros marcados como titular habitual:** en América (1550952)
  Malagón figuraba como TH y no estaba en la hoja. La zona GK salió en 🔴
  (50 %) y disparó F3, y jugó Cota, el titular habitual (15 de 16).
- **El suplente de emergencia sin antecedentes de error no es una vía de gol:**
  - Once Caldas (1549731): Beltrán, 7 PJ, hizo 7 atajadas.
  - Rizespor (1584454): Görgen, sin minutos, valla invicta.
  - Roma (1550186): Gollini, observación.
- **GK-FALLA-ACTIVA:**
  - Chelsea (1557450): con un error, Penders no se marcó y no falló. El
    umbral de ≥ 2 se sostuvo.
  - Nice (1552806): Diouf llegaba con dos errores e hizo 7 atajadas. Es un
    caso en contra; la alerta es declarativa y queda así.

**Propuesta (sin tocar el ×1,5 ni el IP):**

1. **El umbral de rodaje de la v1.8 cuenta la carrera en la categoría**, no los
   minutos de esta temporada. Un arquero con ≥ 15 partidos en la división
   tiene rodaje aunque este año haya sido suplente.
2. **La zona GK se calcula sobre el arquero que ataja hoy.** Con dos arqueros
   que se alternan, la ausencia del que no es titular del día no reduce la
   zona. Es la nota de F2c bajada a la zona, no un multiplicador nuevo.
3. **El arquero suplente sin rodaje** (< 15 partidos y sin titularidades
   recientes) **se declara como vía del rival al DTP**: media distancia,
   rechace o salida. Lo de suplente de emergencia sin antecedentes queda como
   rango, no como vía.

**Calculable, en parte.** Las titularidades de los últimos 12 meses y quién
atajó los últimos onces salen de la base (`f1/{id}`, alineaciones). Así se
puede marcar el arquero titular del día y los dos arqueros que se alternan. Los
partidos de carrera en la categoría no están en la base y quedan para la
investigación.

### 4. Las fuentes del F1: la jerarquía vale también para las buenas noticias y para la base de la API

**Qué dice hoy.**
- **v1.7:** una baja que solo sostiene el nivel 4 (agregador) es Duda.
- **v1.8:** dentro del mismo nivel manda la fuente más reciente, y una baja de
  más de 7 días que la víspera contradice es Duda.

**Lo medido (20 lecciones, 14 aciertos, 4 parciales y 2 fallos).** Las
confirmaciones están arriba. Lo que falló:
- **Bajas ❌ solo por agregador**, contra la v1.7 vigente: Fortuna Sittard
  (1552207, Jev `insumo`). Descotte y Zeefuik figuraban como «baja» por
  OneFootball y Goal y fueron titulares. El error contaminó el matchup, el DTP
  y la cadena.
- **Fuente vieja**, contra la v1.8 vigente:
  - PSV (1552209): Pepi era baja por una lesión del 20/09 «al menos un mes»;
    seis semanas después marcó desde el banco.
  - NEC (1552208): una fuente de 8 días quedó vieja en los dos sentidos.
- **La base de la API como única fuente:**
  - Monza (1550172): Zeballos era ❌ solo por el `Missing Fixture` y jugó
    desde el 69'.
  - Mainz (1575211): Zentner y Amiri, en duda o fuera según la base, fueron
    titulares, como decía la previa.
- **La convocatoria citada por la prensa:** Medellín (1549728). Mantilla era
  baja y el arquero Chaux titular, y fue al revés.
- **La buena noticia del agregador:** Tottenham (1557456). FACTOR-X se activó
  por la vuelta de Udogie según una previa de agregador, y arrancó en el
  banco.
- **Sanciones de la base:** Sarmiento (1493225). La sanción de Contrera
  calculada de la base (5.ª amarilla, `backend/sanciones.py`) le ganó a la
  previa que lo ponía titular.

**Propuesta:**

1. **La jerarquía vale en las dos direcciones.** Una **entrada o una vuelta al
   once** (FACTOR-X, regreso de lesión) que solo dice un agregador también es
   Duda, y no activa FACTOR-X como dato de la fecha.
2. **El estado de lesión de la API** (`Missing Fixture`, «Questionable») **es
   nivel 4**, igual que un agregador. Solo, da Duda.
3. **La sanción calculada de la base** (roja en la misma competición, ciclo de
   amarillas con regla conocida, `f1/{id}.sancionados`) **es nivel 1**: es una
   regla del reglamento, no una noticia. Le gana a una previa.
4. **Una convocatoria que solo cita la prensa**, sin la lista del club, es
   nivel 2 o 3. Un ausente de esa lista es Duda, no Baja.

**Calculable, en parte.** La 3 ya la calcula la app (`SANCION-SIN-DECLARAR`).
Lo demás depende de la fuente, que es texto: no se calcula.

**Qué NO:** endurecer la regla de la v1.8. Fortuna, PSV y NEC son
incumplimientos de reglas escritas. El cambio 1 de esta versión (la prosa que
casa con la tabla) y la caja «fuentes de más de 7 días» ya los hacen visibles.

### 5. La F3 por zona dice qué produce el equipo, y el que cubre la zona importa tanto como el que falta

**Qué dice hoy.**
- **F3:** baja un nivel la confianza efectiva con IP rojo o una zona > 40 %.
- **v1.7:** recambio de oficio o reconvertido.
- **v1.8:** zona por rol del grid. La reducción DEF se paga en la vía.

**Lo medido (34 lecciones de zona y F3 y 8 de banco, 42 en total).** El patrón
por zona es claro y repetido.

- **ATK en rojo, menos volumen propio:**
  - Nacional (1549724): 6 remates, 0,53 xG y un autogol.
  - Lens (1552802): 0,25 xG.
  - Junior (1549726): 0,33.
  - Moreirense (1575535): 0,52 y 8 remates de fuera.
  - Schalke (1575210): sexto partido sin gol en casa.
  - Deportivo La Coruña (1644342): contra un sexta, no cortó.
  - Betis (1570435): 23 remates sin Cucho, la degradación no cortó el
    volumen.
- **MID en rojo, esterilidad propia más que dominio del rival:**
  - Villarreal (1570442): 0,92 xG en 14 tiros.
  - São Paulo (1492431): 53 % de pelota con el medio en 🔴 y los dos goles
    de sus medios.
  - Atlas (1551020): 48,5 % de reducción, ganó sin conceder.
  - Chapecoense (1492432): el doble pivote suspendido decidió.
  - Lecce (1550170).
- **DEF en rojo, se paga en la vía y depende de quién la cubre:**
  - **Concedió:** Augsburg (1575206: dos goles con dos remates al arco),
    Luqueño (1632048: tres en 29'), Estudiantes de Río Cuarto (1493218),
    Udinese (1550186), Garcilaso (1549528), Hoffenheim (1575209: por el
    carril del debutante) y Nacional Potosí (1645528).
  - **No concedió en juego abierto:** Coventry (1557451: solo un penal),
    Wanderers (1646899: uno al 90' con 63,6 %), Portuguesa (1646923: un
    central, ámbar) y Monagas (1646925).
- **El recambio de oficio:**
  - Aurora (1645527): H. Vaca, delantero por delantero, marcó.
  - Flamengo (1492439): sin Carrascal, Plata abierto y Arrascaeta, cuatro
    goles.
- **El rol del día:** Stuttgart (1575204). Stiller, organizador de un equipo
  de posesión, pesó menos en un 3-4-1-2 de transición que cede la pelota.
  Stuttgart hizo cuatro.
- **La escala del rival:** contra un SIN FORMACIÓN o un rival de otra base, la
  F3 baja la confianza en la K y no el resultado. Ejemplos: PSG (1552801),
  Athletic (1645579), Granada (1644347) y Depor.
- **B5 con impacto documentado:** Freiburg (1575206: dos goles y una
  asistencia de suplentes), Kifisia (1593347), Lille (1552802: Giroud al 86'),
  Fluminense (1492435) y Bulo Bulo (1645529).
  - Al revés, un solo partido de banco decisivo no fija B5 alto: Beveren
    (1558663).
  - F4 fue profundidad, no dependencia, en Alianza Atlético (1549536) e
    Internacional de Bogotá (1549728).

**Propuesta (sin tocar el IP, los cortes de zona ni la F3):**

1. **La nota de la F3 escribe qué anuncia según la zona:**
   - **ATK:** menos volumen y xG propios.
   - **MID:** esterilidad propia, no que el rival domine la pelota.
   - **DEF:** la vía del rival (penal, pelota parada, el carril del
     reconvertido), no el volumen. Es el matiz de la v1.8, que pasa a la tabla
     de la F3.
2. **Toda zona en rojo dice quién la cubre:** de oficio, reconvertido o del
   filial. Con recambio de oficio con minutos en la temporada, la zona se
   escribe «degradada, cubierta de oficio» y amplía el rango sin bajar el
   centro, igual que el arco con rodaje (cambio 3).
3. **Con el rival de otra base o SIN FORMACIÓN, la F3 se escribe como
   confianza en la K, no como dirección del partido.**

**Calculable, en parte.** Si el recambio tiene oficio en la línea sale de la
base: titularidades en esa línea del grid. Que la nota diga la vía es juicio.

**Qué NO:** cortes de zona distintos por línea. Mover el 40 % o el rojo es
mover un número, y ninguna lección lo pide.

### 6. D3 y E se leen en la condición del partido, y COLAPSO suma su tercer caso de ruptura con agravante

**Qué dice hoy.**
- **v1.7:** D3 medido en una sola condición se lee una franja abajo en la otra.
  Un D3 medido en otra competición o escala va `sin dato`.
- **v1.8:** el E dice «3+ sin ganar» sin tocar el número.
- **COLAPSO:** riesgo de perder la ventaja, no de romperse. Queda el
  candidato «COLAPSO + agravante».

**Lo medido (19 lecciones de D, E y C4 y 8 de COLAPSO, 27 en total).**
- **D3 medido en la condición, confirmado:** Alianza Atlético de local
  (1549528), Cristal de local (1549534: dio vuelta un 1-2 en el añadido),
  Gimnasia de visita (1493218), Monza con el DT vigente (1550172), Cerro
  (1646898: reacciona y no sostiene, otra vez) y PSG (1552801).
- **D3 de la liga entera que no viajó a la condición:**
  - GAE (1552211): 🔶 de toda la liga con 0 victorias de visita en 5. De
    visita recibió al 7' y quedó 0-3 al 41'.
  - Genoa (1550171): el E en 0 mezcló tres victorias de local con todo
    perdido fuera.
- **D3 sostenido en un partido con un jugador de más o de menos:**
  - Barcelona SC (1639801): un 0-4 con uno más desde el 70'.
  - Coquimbo (1505549): un caso con bloque alto, y con diez cerró la ventaja.
- **D3 que solo midió una cara:** Estudiantes (1493217) se puntuó 🔶 por
  ventajas perdidas y el mismo equipo remontó un 0-3 con diez. Bahía
  (1492431) es el otro lado: su 🔶 de «pierde ventajas» se repitió.
- **C4 contra el perfil del rival:** en Talleres (1493216), dos ventajas
  perdidas no se repitieron ante un rival sin nada en juego que cedía la
  pelota. En Sarmiento (1493225) sí se repitieron.
- **COLAPSO, contraejemplos de «no romperse»:**
  - Udinese (1550186): D3 ❌ y línea de tres improvisada con un central
    reconvertido. Quedó 0-4 al 37'.
  - Zulte Waregem (1558670): el colapso vino después de la igualada, tres
    goles en 11'.
  - Vasco (1492439): D3 🔶 de un solo caso y el once rotado ante el líder,
    tres goles tras el empate.

**Propuesta:**

1. **El D3 y el E se puntúan con la serie de la condición del partido** (L/V)
   cuando hay al menos 3 partidos en esa condición. Si se mezclan, la nota
   escribe las dos caras («3 de 3 de local, 0 de 5 de visita»). Es la v1.7
   aplicada al origen de la serie, no un umbral nuevo de puntuación: el número
   del E no cambia, cambia qué partidos lo sostienen.
2. **Un partido con superioridad o inferioridad numérica de más de 20 minutos
   no sostiene un D3.** Ese caso va aparte en la nota.
3. **La nota del D3 dice sobre cuántos casos se apoya y en qué cara**
   (remontar estando abajo · sostener la ventaja). Un D3 de un solo caso se
   escribe «(1 caso)» y amplía el rango.
4. **COLAPSO: «no romperse» pasa a «no predice la ruptura».** La alerta sigue
   sin predecir goleada. El candidato **COLAPSO + agravante** suma su tercer
   caso, Udinese (zaga reconvertida, en la línea de Manchester United, v1.7).
   Zulte y Vasco suman la forma «el colapso llega tras la igualada», que es la
   semántica de 🔶 en el que lo sufre. **Sigue candidato:** con tres casos
   no hay base para volverlo regla, y se re-evalúa con la próxima tanda.

**Qué NO:**
- **E3 con «sin ganar».** Sigue candidato (v1.8): Genoa es de condición, no de
  empates.
- **Subir el D3 en la Liga MX.** Tijuana (1551025) es un caso y Jev no lo
  marca como mover un número.

### 7. EJE-DEBUTANTE se verifica con el once oficial, y la app lo calcula

**Qué dice hoy (v1.7).** ≥ 2 titulares de la misma línea con ≤ 1 partido juntos.
Es declarativa, amplía el rango y se lee del grid.

**Lo medido (18 lecciones, 7 aciertos, 4 parciales y 7 fallos).**
- **Se cumplió:**
  - Milan (1550167): cuatro goles en contra.
  - Alianza Lima (1549534): dos goles por el aire, bajados al DTP.
  - Vitória (1492434): 14 remates en el área.
  - Estudiantes (1493217): 0-3 en siete minutos.
  - Tigres (1551023), Pasto (1549725), Barcelona SC (1639801), Hull
    (1557452), Atalanta (1550169) y AZ (1552210).
- **Amplió sin materializarse (como dice la regla):** Udinese (1550173),
  Leones del Norte (1639856), Atlas (1551020), Jaguares (1549732: el gol
  entró por la banda) y Santos (1492438).
- **Lo que falló es el insumo, no la regla:**
  - Los Chankas (1549533): emitida sobre un carrilero del once probable que
    arrancó en el banco.
  - Wanderers (1646899): pareja Benítez–Zazpe en el parte, y la real fue
    Zazpe–Freitas.
  - Manchester City (1557454): la pareja Dias–Khusanov quedó en la prosa del
    DTP y no como alerta del EFE con el once rehecho.
  - Beveren (1558663): condicional, sin objeto.

**Propuesta:**

1. **Sin once oficial, EJE-DEBUTANTE va siempre condicional** («si repiten X–Y»).
2. **Con el once oficial, el chequeo del eje se rehace sobre el grid** y la
   alerta se declara o se descarta con el dato.

**Calculable (app, si se aprueba).**
- **El cálculo ya existe:** `dtp_cowork.parejas_nuevas_de` calcula las parejas
  de la misma línea con ≤ 1 titularidad juntas. Hoy se aplica al XI de
  referencia (`parejasNuevas` de los insumos del DTP).
- **Se propone:**
  - Correrlo sobre el once oficial capturado.
  - Que el parte avise `EJE-DEBUTANTE-SIN-DECLARAR` (tipo `dato`, calculada)
    si hay una pareja nueva y el parte no la tiene.
  - Que avise `EJE-DEBUTANTE-SIN-OBJETO` si el parte la declaró sobre una
    pareja que no arrancó.

**Qué NO:** darle peso o convertirla en vía de gol por sí sola. Los cinco
contraejemplos confirman que amplía el rango.

## Matices que no son cambio (se escriben como nota)

- **La brecha en la misma base ordena al ganador más probable, no el dominio
  ni descarta el empate.**
  - Confirmada en Konyaspor–Galatasaray, Levante–Atlético, Barcelona–Alavés,
    Udinese–Roma, Sarmiento–Central y Augsburg–Freiburg.
  - Con 0-0 en Metropolitanos–Portuguesa (31 puntos, 1646923) y
    Kocaelispor–Rizespor (1584454).
  - Con el volumen del menos formado en Heerenveen–NEC (1552208).
- **Brecha con F3 en el lado que la lidera.** En Recoleta–Ameliano (1632046) y
  Genoa–Juventus (1550171) no ordenó. PSG (1552801) es el contraejemplo.
  Queda **candidato** («la brecha se lee con la confianza efectiva»), con dos
  casos a favor y uno en contra. Si se aprueba más adelante, es calculable: la
  F3 la calcula `bloque_f.py` y `EFE-EMPATE-TECNICO` podría contarla.
- **Contraejemplos del empate técnico** (ganó el más formado con T.54 o R-KT.2
  en el otro lado): Lille–Lens (1552802), Macará–Barcelona SC (1639801),
  Carabobo–La Guaira (1646922), City–Brighton (1557454), Luqueño–Nacional
  (1632048) y Colo Colo–UdeC (1505548). Son 6 contra 22 en que ganó el de
  menor porcentaje. **No mueve la regla.** Es una medición pendiente y
  calculable: en Aprendizaje, la tasa del de mayor porcentaje con y sin
  `EFE-EMPATE-TECNICO`.
- **El matchup H ordena lo que la brecha no ordena** (Cienciano–Grau,
  1549529, en la altura).
- **Un paro salarial se paga en preparación, no en nivel** (Pereira, 1549732).

## `efe-dashboard` v1.11 → v1.12

**Lo medido (2 lecciones, las dos aciertos con matiz).**
- **Delfín (1639828):** la banda baja de goleada se apoyó en una racha récord
  de 13 visitas sin perder por 2+. FAMILIA-RECORD ya avisaba que, en su
  récord, la burbuja no da probabilidad de corte.
- **Konyaspor (1584455):** la banda base de goleada (8-15 %) se escribió y la
  goleada llegó por el gatillo declarado (gol temprano que obliga a abrirse),
  cumplido antes del 30'.

**Propuesta:**

1. **Un récord de racha** (`FAMILIA-RECORD`, `K-EXTREMO`) **no es argumento
   para bajar la banda de goleada.** Es prudencia con la carga, no
   probabilidad (REVENTON §10 y §15.2).
2. **En la fila «Para perder» de la matriz, la goleada se nombra como rama**
   cuando el gatillo es un gol temprano del rival y el inferior queda obligado
   a perseguir, no solo como banda base.
3. **Lo que baja de esta revisión al dashboard:** la zona «cubierta de oficio»
   (cambio 5), el arco del día (cambio 3) y la rama del once alternativo de los
   dos lados con el banco (cambio 2) se dibujan en la caja de sensibilidad. El
   EJE-DEBUTANTE calculado (cambio 7) se muestra en el F6 con su origen
   (`calculado` / `declarado`).

**Qué NO:** números en la banda de goleada. Se calibra con más casos.

## Lo que NO se propone

- **Ningún peso, máximo, corte de clasificación ni el ×1,5 del arquero.**
  Ninguna lección lo pide y Jev no marcó ninguna para mover un número.
- **Tocar el motor o lo que calcula el backend.** Lo que aquí dice
  «calculable» son alertas de tipo `dato` que leen lo que ya existe: once
  oficial, F1, grid, sanciones y `dt.desde`. No cambian ningún número.
- **Redefinir el porcentaje o el mínimo de bloques.** Ya decidido el 31/10
  (799).
- **E3 con empates, COLAPSO + agravante como regla, la brecha con F3, subir el
  D3 por liga.** Siguen candidatos o quedan como medición.

## Cómo se aplica si se aprueba

1. **Skill:** `references/rubrica-efe-v1.9.md` con el changelog (de 1 a 7). El
   `SKILL.md` pasa a v1.9 y suma tres líneas a «Reglas que no se negocian»:
   - la tabla F1 lleva el recambio de cada baja y todo nombre de la prosa;
   - la rama del once alternativo va a los dos lados en copa;
   - el eje se verifica con el once oficial.
2. **`efe-dashboard` v1.12:** los puntos de su sección.
3. **App (cada cambio por separado, con su test):**
   - `lecciones.CORTE_VERSION["efe-clasificador"]` suma `("v1.9", <fecha>)`,
     para que «Cerrar las anteriores» cierre estas 294 en la v1.9 (y las 2
     del dashboard en la v1.12).
   - Las alertas calculadas de los cambios 2 y 7: `EFE-RECOMPUTO-PENDIENTE`,
     `EJE-DEBUTANTE-SIN-DECLARAR` y `EJE-DEBUTANTE-SIN-OBJETO`. Van en
     `_ALERTAS_CALCULADAS`, en `docs/openapi.yaml` y en `test_cowork`.
     `test_arquitectura` exige que cada alerta calculada esté documentada.
   - El aviso del recibo por nombres de la prosa sin fila F1 (cambio 1) y el
     `recambio` sugerido en `f1/{id}`, con `backend/identidad.py`.
4. **`docs/COWORK.md`:** el prompt suma dos líneas: la tabla F1 con recambios y
   rotables, y el recomputo de B y F cuando el once oficial rota a 3 o más.
5. Zips para subir a la cuenta.

## Resumen: qué lecciones cierra cada punto

| Punto | Lecciones | Aciertos / parciales / fallos | Copa | Tipo |
|---|---:|---|---:|---|
| 1 · Tabla F1 con recambios, rotables y la prosa | 23 | 12 / 6 / 5 | 4 | regla + calculable (aviso del recibo, `recambio`) |
| 2 · Once alternativo en los dos lados, banco y recomputo | 28 | 20 / 3 / 5 | 9 | regla + calculable (`EFE-RECOMPUTO-PENDIENTE`) |
| 3 · Arquero: rodaje en la categoría, el arco del día | 16 | 7 / 4 / 5 | 1 | regla, calculable en parte |
| 4 · Fuentes: las dos direcciones, API nivel 4, sanción nivel 1 | 20 | 14 / 4 / 2 | 3 | regla (la sanción ya calculada) |
| 5 · F3 por zona: qué anuncia y quién la cubre (+ B5/F4) | 42 | 21 / 8 / 13 | 1 | regla, calculable en parte |
| 6 · D3 y E por condición · COLAPSO (3.er caso con agravante) | 27 | 17 / 2 / 8 | 1 | regla + candidato |
| 7 · EJE-DEBUTANTE con el once oficial | 18 | 7 / 4 / 7 | 0 | regla + calculable (`EJE-DEBUTANTE-SIN-DECLARAR/-SIN-OBJETO`) |
| Brecha / EFE-EMPATE-TECNICO: confirmación y matices | 97 | 53 / 17 / 27 | 13 | sin cambio (nota + candidato + medición calculable) |
| T.54 en los dos lados (v1.8): confirmación | 13 | 9 / 2 / 2 | 1 | sin cambio |
| Sin dato / HUECO-DOBLE (con la 799 ya decidida) | 10 | 8 / 1 / 1 | 10 | sin cambio |
| `efe-dashboard` · banda de goleada | 2 | 2 / 0 / 0 | 0 | regla del dashboard |
| **Total** | **296** | **170 / 51 / 75** | **43** | |

La asignación es por la regla que cita cada lección. Una lección que toca dos
reglas cuenta en la primera que nombra. Las cuentas por punto se hicieron sobre
el JSON de `/analisis/cowork/lecciones` del 01/11/2026 (05:08 UTC).
