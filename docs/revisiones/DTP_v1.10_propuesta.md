# Propuesta de revisión · `diagnostico-tactico` v1.9 → v1.10

> **APROBADA por el usuario el 24/11/2026, con todas las recomendaciones.** 1. el segundo de la lista de penales sigue candidato, con los casos nuevos · 2. el candidato nuevo «con la condición sostenida por el propio parte, manda la condición» entra al bloque de candidatos (no como excepción a la línea menos favorable) · 3. la frase del renglón 6 se agrega. Lo demás, como recomienda la propuesta (puntos 1 a 4 entran; 6 y 7 a medición; 8 a la app). Aplicada en la v1.10.

**Estado: PROPUESTA (24/11/2026), pendiente de aprobación punto por punto.**
No se tocó `docs/skills/diagnostico-tactico/SKILL.md`, su `references/` ni
código. Las líneas citadas son de la **v1.9 de hoy (425 líneas, ya con el
historial fuera)**, comprobadas con `sed -n` y `grep -F` el 24/11.

**Base:** el estudio del 24/11 (`estudio_lecciones_2026-11-24/README.md`,
`estudio_diagnostico-tactico.parte1.md` y `.parte2.md`,
`clasif_diagnostico-tactico.json`) y la prosa de las **537 lecciones
pendientes** de 137 partidos del 17 al 23/11, todas `ciega` + `PRE`.
**49 lecciones (19 partidos) son de copa nacional** (Copa del Rey 1644xxx,
Copa de la División Profesional de Bolivia 1650230 y la Taça de Portugal
1647xxx): enseñan, pero no acreditan. Quedan **488 acreditables de 118
partidos**: 275 sostuvo, 128 mal aplicada, 70 regla falló, 9 insumo, 4 no
dice, 2 imprevisto, 0 de otro skill.

**Honestidad con la muestra.**
- Las 28 lecciones del 17/11 (10 partidos de selecciones, 15289xx) pueden
  haber corrido con la v1.8: la v1.9 subió ese día a las 13:20 UTC. Las dos
  que cobran una regla nueva de la v1.9 (Irlanda del Norte 1528995:b, el
  reconvertido; Ucrania–Georgia 1528994:b:4, la pelota parada por rama) **no
  se cuentan como incumplimiento** de la v1.9 en ningún punto de texto.
- Dos lecciones son de partes **sin DTP depositado** (Olimpia 1632065:a:5 y
  Libertad 1632067:b:3): no juzgan nada del skill y quedan fuera.
- `modoFallo` viene vacío en casi todas (Jev dejó de etiquetar desde el
  21/11, README §3.1): Jev no aporta a esta revisión.
- El veredicto del lado no dice si la regla funcionó: en los lados fallados
  hay 94 lecciones donde la regla se sostuvo. Por eso se cuentan **lecciones
  y partidos distintos**, no aciertos.
- **Tres correcciones al estudio**, hechas releyendo la prosa: (1) la
  excepción a la «línea menos favorable» tiene **2 casos limpios, no 4**
  (punto 5, candidato nuevo); (2) los casos nuevos del «caso de la 6 viaja con el
  arquero» no cambian de arquero y **no prueban el candidato** (punto 5); (3) el
  parte **no tiene** hoy el campo de la línea contraria: `_veredicto_ramas`
  de `backend/analisis/dtp_cowork.py` guarda solo `veredicto` y `razon` por
  rama (§5).

## 0. Resumen

- La v1.9 **se sostiene**: 1,8 lecciones mal aplicadas por cada regla que
  falló (128 contra 70) y **0 fallos heredados del EFE**. MECANISMO-ABIERTO
  (31 de 32), la pregunta 6 con `sostuvoArquero` (30 de 31), los penales con
  la base corta (el 9 titular: ninguna mal aplicada) y las ramas por número
  se sostienen enteras.
- **El único fallo de volumen es el M5**: 50 `regla_fallo` de 119 lecciones.
  26 son NEUTRO que el volumen resolvió y 19 FAVORABLE de más (10 de ellos
  acertaron el lado por conversión). La banda de «parejo» es un número y va a
  medición (punto 6). Lo que sí entra sin número es que el veredicto apoyado
  en el nivel o la contra **diga cuánto concede mientras espera** (punto 1).
- Lo demás que se repite **es incumplir reglas ya escritas** (pelota parada
  desde el cruce, perfil de posesión, referencia de volumen, vía de
  expulsión, línea menos favorable, banco con minuto, M3 por rama, grid). No
  se reescriben: van a «Para la app» (§5), porque lo que cambió la conducta
  el 17/11 fue el dato (`bancoProbable`), no repetir el texto.
- **Ningún número se mueve.**

**Lo que ya hizo la app** (desde el 17/11, y cómo se ve en las lecciones):
- `bancoProbable` (#561): el banco mal aplicado bajó de 16 a 3 en la parte 1
  y a 13 en la parte 2. Ninguna lección culpa a la lista; donde se copió
  entera, el banco marcó. Lo que queda es del analista (el minuto fijo, el
  recorte en la razón, «solo persiguiendo») o del once probable que la hoja
  corrige tarde.
- El rehacer por la hoja (FUERA-EN-LA-HOJA, ONCE-SIN-FILA-F1,
  EFE-RECOMPUTO-PENDIENTE, #560): el grid sin copiar bajó de 8 a 3 (parte 1)
  y el rehacer mal hecho de 6 a 2. Persiste con la ficha a la vista antes del
  pitazo (Hull 1557472, Standard 1558687, LDU–Aucas 1639807, Sevilla
  1570462).
- Jev `lectura` (#562) y `ventajaPorFuerza` (#563): no tocan al DTP.
- El banco, la F1 y el arquero sin el homónimo (21/11, 22:50): ninguna
  lección muestra ese error; no se puede juzgar todavía.
- **El insumo dominante ya no es el rehacer**: en 18 lecciones de 16 partidos
  (parte 1) y unas 19 de 17 (parte 2) la API corrigió la formación o el grid
  **después del pitazo**. Las lecciones lo cobran bien, como apertura caída.

## 1. Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos (partidos acreditables; copa aparte) | Recomendación |
|---|---|---|---|---|
| 1 | El veredicto apoyado en el nivel, la contra o la transición dice **cuánto concede mientras espera**, con cualquier etiqueta (hoy solo el DESFAVORABLE) | aclaración | 3 + 2 de apoyo; 1 de la regla vigente incumplida (Lecce) | aprobar |
| 2 | Renglón 6 de `viasGol`: **figurar en otro renglón no saca a nadie de este** (el centrador, el asistidor o el de media distancia también llega) | aclaración de forma + app | 6 partidos | aprobar |
| 3 | Pregunta 5 del checklist: **con el DT de hoy y lo que hizo**; la obligación de tabla no es evidencia | aclaración | 3 partidos | aprobar |
| 4 | **El rearme del doble pivote o del contenedor cuenta como el de la línea** (M3) | candidato que sube a regla | 3 nuevos + 2 anteriores; 1 que no concedió | aprobar |
| 5 | Bloque «Candidatos abiertos»: casos nuevos, un contraejemplo y un candidato nuevo | lista | — | aprobar (decide el usuario el de penales y el nuevo) |
| 6 | Banda de «parejo» del M5 | candidato a medir | 50 `regla_fallo` de 119 | medir; no entra |
| 7 | Vida útil 55-65 del improvisado | candidato a medir | 5 partidos (3 del punto 3 + Progreso y Köln) | medir; no entra |
| 8 | Lo que se incumple con la regla escrita | app (no entra al skill) | ver §5 | pedir a la app |
| 9 | Núcleo: anclas nuevas y la nota v1.10 al historial | forma (núcleo) | — | aplicar con la versión |

## 2. Los puntos con material

### 1. El veredicto apoyado en el nivel o en la contra dice cuánto concede mientras espera

**Qué dice hoy.** El M5 (l. 332, *v1.7*), al final: «Y un DESFAVORABLE que se
apoya en el nivel dice **cuánto volumen le concede al débil** (Kifisia generó
1,3 de xG contra 0,92).» El M2 (l. 146): «Un veredicto que se apoya en **«la
contra del rival»** dice qué pasa si el que gana no quiere correr». Nada pide
al FAVORABLE ni al NEUTRO que se apoyan en el nivel o en la contra que digan
cuánto le dejan al otro.

**Qué pasó.** De los 19 FAVORABLE de más del M5, tres lecciones dicen esto
mismo y con la misma palabra, en tres partidos distintos:
- **Vasco–Internacional 1492458:a**: FAVORABLE de igualado o arriba apoyado en
  la transición y la segunda línea contra un bloque improvisado; 90 minutos,
  0,52 de xG contra 1,40. Ganó por conversión (2 goles con 0,52). «No escribió
  cuánto le concedía a la contra y al área rival».
- **Progreso–Torque 1650502:b**: FAVORABLE de igualado por la superioridad del
  medio, con «si Progreso sale, se suma la transición». Progreso salió y fue
  parejo (15 remates contra 12, 7 al arco contra 6; sin xG en la ficha, con
  reserva). «La línea "si el rival sale" escribe cuánto volumen le concede
  al débil».
- **IdV–Macará 1639806:b**: NEUTRO apoyado en la contra; Macará ganó con 0,63
  de xG contra 2,28 (21 remates en el área en contra), con un autogol y 9
  atajadas. «Un NEUTRO apoyado en la contra tiene que decir cuánto volumen
  concede el bloque mientras espera».

Apoyo, en la misma dirección y sin la frase: Dinamarca–Noruega 1528993:a:2
(FAVORABLE que vivía de que Noruega se abriera: se abrió, y 1,7 contra 4,28) y
Marseille–Le Mans 1552822:a:4 (FAVORABLE con la transición rival ya abierta en
el primer tiempo: 1,49 contra 4,07). La regla vigente del DESFAVORABLE tuvo
una mal aplicada: Lazio–Lecce 1550202:b:2 (DESFAVORABLE persiguiendo «se le
parte el medio», 0,97 contra 1,2: casi parejo).

**Texto propuesto.**

(a) Sub-viñeta nueva **debajo de la l. 146**:

> - **El veredicto que se apoya en el nivel, la contra o la transición dice
>   cuánto concede mientras espera** *(v1.10; la v1.7 lo pedía solo al
>   DESFAVORABLE)*. Con cualquier etiqueta, la razón escribe **cuánto volumen
>   le deja al otro** —al débil que sale, al que tiene la pelota, a la contra
>   rival— mientras llega la vía que la sostiene, con su zona, y no solo la vía
>   que gana. Va como dirección con su razón, no como número prestado (la
>   referencia de volumen no viaja, M5). Vasco–Internacional: FAVORABLE por la
>   transición y la segunda línea, 0,52 de xG contra 1,40; Progreso–Torque:
>   FAVORABLE por nivel con «si Progreso sale, se suma la transición», salió y
>   fue parejo; IdV–Macará: NEUTRO apoyado en la contra, 0,63 contra 2,28.

(b) En la **l. 332**, reemplazo (el texto viejo aparece una sola vez):
- viejo: «Y un DESFAVORABLE que se apoya en el nivel dice **cuánto volumen le
  concede al débil** (Kifisia generó 1,3 de xG contra 0,92).»
- nuevo: «Y un veredicto que se apoya en el nivel o en la contra, con
  cualquier etiqueta, dice **cuánto volumen le concede al otro** (Kifisia
  generó 1,3 de xG contra 0,92; Lazio–Lecce; ver M2, «dice cuánto concede
  mientras espera»).»

**Por qué no más.** No fija cuánto es «mucho» conceder: eso es la banda de
«parejo» (punto 6). Tampoco baja el FAVORABLE por defecto: 10 de los 19
FAVORABLE de más acertaron el lado, y el problema es que la razón no deja ver
lo que el cierre va a medir. **Qué lo tumbaría:** FAVORABLE o NEUTRO que
escriben cuánto conceden y fallan por volumen igual, en tres partidos o más.

### 2. Renglón 6: figurar en otro renglón no saca a nadie de este

**Qué dice hoy.** La lista de salida (l. 128): «6. lado débil y segunda línea
(el lateral que llega, el reconvertido y el origen de la jugada, no solo el
rematador);» y la l. 97 (*v1.6*) pide quién llega al segundo palo y la
llegada del interior o del pivote. La regla dice «no solo el rematador»: pide
el origen además del que remata. **No dice lo inverso**: que el nombrado como
origen también va como llegada.

**Qué pasó.** El que marcó estaba en la lista, pero **en otro papel**:
- Juventus–Venezia 1550201:a:6: Cabal, lateral izquierdo, nombrado solo como
  centrador de la vía aérea, hizo el 3-0.
- NEC–PSV 1552229:b:4: Kostić, lateral, nombrado como centrador y lanzador,
  hizo el 1-0.
- Querétaro–Necaxa 1551046:b:3: M. Rodríguez, extremo, nombrado solo como
  centrador, hizo el 1-1 (asistido por el pivote reasignado).
- LDU–Aucas 1639807:b:3: Guzmán, interior, nombrado solo como asistidor en
  `piezas`, entró al área y marcó.
- Israel–Austria 1528996:a y Polonia–Suecia 1528998:a:2: el interior nombrado
  solo de media distancia (Dor Peretz; Larsson, en las vías del rival) llegó al
  área y marcó.

Son 6 partidos, sin copa. Fuera del renglón 6 hubo una mal aplicada por
renglón (media distancia, pelota sucia, quinta línea, P2 del arquero), sin
patrón.

**Texto propuesto.** Reemplaza el renglón 6 de la l. 128:

> 6. lado débil y segunda línea (el lateral que llega, el reconvertido y el
>    origen de la jugada, no solo el rematador). **Figurar en otro renglón no
>    saca a nadie de este**: el lateral o el extremo nombrado como centrador,
>    y el interior nombrado como asistidor o de media distancia, van también
>    acá como llegada, con su zona (Juventus: Cabal, centrador, hizo el 3-0;
>    PSV: Kostić; Necaxa: M. Rodríguez; Aucas: Guzmán, asistidor, entró y
>    marcó);

**Por qué no más.** Es el renglón que más se incumple desde el 17/11 y
repetir la lista no lo cortó: la frase solo cierra una lectura (la del nombre
que «ya está» en otro renglón). Lo que lo corta es la app (§5): cruzar los
titulares de banda y de segunda línea del grid contra los nombres del renglón
6. **Qué lo tumbaría:** listas donde cada titular de banda figura como
llegada y los goles siguen saliendo de un nombre fuera de la lista.

### 3. La pregunta 5 se responde con el DT de hoy

**Qué dice hoy.** La tabla del checklist (l. 165): «¿El repliegue está
documentado como plan o es una reacción al marcador?». La l. 174 (*v1.6*):
«un repliegue anunciado por el DT es plan». La l. 173: «La pregunta 1 mide el
modelo, no al DT». Nada dice con los partidos de **qué DT** se responde la 5,
ni que un repliegue repetido sin anunciar también es plan.

**Qué pasó.** Tres mal aplicadas en tres partidos, y en las tres el bloque
llamado improvisado o ambiguo sostuvo el resultado:
- **Vitória–Bragantino 1492459:b:6**: la 5 («el repliegue es reacción») se
  respondió con partidos del DT anterior; Vitória sostuvo una ventaja del 4'
  al final de local, con reserva por el arquero (6 atajadas).
- **Cercle–Westerlo 1558682:b:5**: «reacción al 1-0», pero Cercle cedió el
  43 % de local con 0-0 hasta el 71', el segundo partido seguido de Caixinha
  cediendo la pelota (38 % y 43 %); sostuvo los 90 minutos con 0,96 de xG en
  contra.
- **Liverpool M.–Wanderers 1650504:b:3**: «reacción, hoy además obligado a
  ir»; Wanderers plantó una línea de cinco de plan y sostuvo 0-1 y 0-2
  durante 59 minutos de visita, con 3 remates al arco en contra.

**Texto propuesto.** Sub-viñeta nueva **debajo de la l. 174**:

> - **La 5 se responde con el DT de hoy y con lo que hizo, con `n`**
>   *(v1.10)*. Plan o reacción sale de los partidos del DT que dirige hoy, no
>   de los del anterior (Vitória). Un repliegue que el DT de hoy ya eligió con
>   el marcador igualado es plan aunque no lo anuncie (Cercle: «reacción al
>   1-0», y era el segundo partido seguido de Caixinha cediendo la pelota). La
>   obligación de tabla dice lo que el equipo necesita, no cómo defiende: no
>   es evidencia para la 5 (Wanderers: «obligado a ir», plantó una línea de
>   cinco y sostuvo 59 minutos de visita). La 1 mide el modelo; la 5, lo que
>   hace el DT de hoy.

**Por qué no más.** No fija cuántos partidos hacen «plan»: se escribe con su
`n` y lo lee el cierre. No toca el recuento (3 de 5) ni la vida útil (punto
7). **Qué lo tumbaría:** bloques con la 5 respondida «plan» por el DT de hoy
que se caen dentro de la vida útil del improvisado, en tres partidos o más.

### 4. El rearme del doble pivote o del contenedor cuenta como el de la línea (de candidato a regla)

**Qué dice hoy.** El bloque de candidatos (l. 349): «**El rearme del doble
pivote o del medio cuenta como el de la línea** (M3): Fiorentina, Instituto;
Gimnasia, con una roja.» El cuerpo (l. 237-238) pide el costo del rearme y
quién queda atrás para **la línea de fondo**, no para el medio.

**Casos nuevos, verificados en la prosa:**
- **Liverpool M.–Wanderers 1650504:a:6**: el pivote del seguro (Garayalde),
  amonestado al 21', sale al 28'; el 0-1 llega al 31'. `m2.piezas` lo nombraba
  sin sus amarillas ni su relevo.
- **Chelsea–Leeds 1557470:a:4**: Caicedo, contenedor del seguro, sale
  obligado al 22'; el empate llega al 28', por el centro.
- **Marseille–Le Mans 1552822:a:6**: doble cambio del doble pivote al 74'
  (Kondogbia y Nnadi, amonestados); el 2-2 al 84' por un pase interior y el
  2-3 al 90+5. «El M3 escribió el costo de un cambio atrás, no el del medio».

Con los dos anteriores (Fiorentina, Instituto) son **5 partidos**; sin
ellos, los 3 nuevos llegan solos al umbral. En contra, sin restar: Grêmio–
Bahía 1492454:b:4, cambio forzado del contenedor al 46' sin conceder (es vía,
no certeza, como el rearme de la línea).

**Texto propuesto.** Sub-viñeta nueva **debajo de la l. 238** («Quién queda
atrás, en todas las ramas…»), y la l. 349 sale del bloque de candidatos:

> - **El rearme del doble pivote o del contenedor cuenta como el de la
>   línea** *(v1.10; candidato desde la v1.8)*. El cambio, forzado o
>   planificado, del contenedor del seguro o de los dos del doble pivote se
>   escribe en el M3 con **quién queda de seguro** y entra como vía del rival
>   en ese tramo, igual que un cambio atrás (Liverpool M.–Wanderers: el pivote
>   amonestado sale al 28' y el gol llega al 31'; Chelsea–Leeds: Caicedo sale
>   al 22', empate al 28'; Marseille–Le Mans: doble cambio al 74', goles al 84'
>   y al 90+5; antes, Fiorentina e Instituto). Vía, no certeza, y sin ventana
>   de minutos (Bahía: cambio forzado al 46' sin conceder).

**Por qué no más.** Gimnasia (con una roja) sigue como apoyo y no se cuenta.
No se agrega ventana: la v1.7 y la v1.8 dejaron los minutos al cierre, y acá
igual. **Qué lo tumbaría:** rearmes del medio escritos con su seguro en los
que el rival no ataca ese tramo y los goles llegan por otra vía.

### 5. El bloque «Candidatos abiertos»: casos nuevos

**Qué dice hoy:** l. 342-352. Cada candidato, con sus casos.

| Candidato (línea) | Casos nuevos de esta ventana | Queda |
|---|---|---|
| El seguro «sin» impide un FAVORABLE persiguiendo (l. 345) | **En contra**: Dinamarca–Noruega 1528993:b. Noruega persiguió 72 minutos con el seguro «sin» y generó 4,28 contra 1,7 | candidato, con el contraejemplo escrito: 2 a favor, 1 en contra |
| El segundo de la lista de penales recibe la falta (l. 346) | Dinamarca–Noruega 1528993:b:2 (Ødegaard, segundo, recibió la falta; pateó Haaland, primero) y Racing–Real Sociedad 1570459:a:6 (Zabiri, segundo, recibió la falta; pateó Canales, primero). Con reserva: Barcelona–Villarreal 1570455:a:5 (Yamal, segundo, «figura en el penal» y lo pateó con Raphinha en cancha) | **decide el usuario** (pregunta 1): llega a 4, pero no dice qué escribir distinto |
| El caso de la 6 viaja con el arquero (l. 347) | Sassuolo–Genoa 1550206:b:3 (Bijlow) y Hull–Brighton 1557472:b:3 (Tzolakis): los dos son `sostuvoArquero` repetido **con el mismo arquero**. El candidato nació de Villarroel, donde atajó el suplente y el bloque concedió 2,89. Estos casos cumplen la (c) vigente y **no prueban** que el caso no viaje cuando cambia el arquero | candidato, sin casos nuevos (corrige al estudio, que lo daba por llegado) |
| El rearme del medio (l. 349) | ver punto 4 | **regla** |
| **Nuevo:** con la condición sostenida por el propio parte, manda la condición | Bayern–Köln 1575221:b:6 (el propio DTP decía que Bayern no administra; se volcó desde el 12') y Feyenoord–Excelsior 1552226:b (el TDE del rival en SOB, «sigue atacando»; 71 % de Feyenoord) | **candidato nuevo** (pregunta 2): son 2 |

Sobre el candidato nuevo: el estudio lo contó con 4 `regla_fallo` contra 3
mal aplicadas y propuso aclararlo. Releída la prosa, la obligación de tabla
**va para los dos lados**: en Boston River–Maldonado 1650500:a:4 el obligado
se volcó, y en Liverpool M.–Wanderers 1650504 (los dos lados) el obligado no
se abrió. Limpios, con un hecho del propio parte, quedan **2**: no llega al
umbral. Y la regla vigente acertó donde se incumplió, en 7 partidos (§5).

**Texto propuesto** (reemplazos en el bloque; cada texto viejo aparece una
sola vez):
- l. 345, al final, después de «De copa: The Strongest.»: se agrega «En
  contra: Dinamarca–Noruega (Noruega persiguió 72 minutos con el seguro «sin»
  y generó 4,28 contra 1,7).»
- l. 346, si sigue candidato: «Panathinaikos; Dinamarca.» → «Panathinaikos;
  Dinamarca; Dinamarca–Noruega (Ødegaard; pateó Haaland); Racing–Real
  Sociedad (Zabiri; pateó Canales). Con reserva: Barcelona–Villarreal (Yamal
  figura en el penal y lo pateó).»
- l. 349: sale (punto 4).
- Línea nueva al final del bloque, si el usuario la aprueba:

> - **Con la condición sostenida por el propio parte, manda la condición y no
>   la línea menos favorable**: Köln–Bayern (el DTP decía que Bayern no
>   administra); Excelsior–Feyenoord (el TDE del rival, «sigue atacando»). La
>   obligación de tabla sola no la sostiene: Boston River (el obligado se
>   volcó) contra Liverpool M.–Wanderers (no se abrió).

**Por qué no más.** El de penales llega a 4 casos, pero la regla no cambiaría
qué escribe la lista: ya son dos nombres en orden condicionados a quién está
en cancha (l. 99-104), y Barcelona va en contra de la lectura obvia (el que
figura en el penal lo pateó). Subirlo sería una frase descriptiva sin
conducta.

## 3. Candidatos a medir (números: sin backtest no entran)

### 6. La banda de «parejo» del M5

**Qué dice hoy** (l. 333): «**Sin umbral**: cuánto es «parejo» lo lee el
cierre con los dos números a la vista; una banda sería un número nuevo sin
con qué calibrarlo.» La v1.9 la dejó a medición (DTP_v1.9_propuesta §5).

**Qué pasó.** 50 `regla_fallo` de 119 lecciones del M5, ninguna de copa:
- **NEUTRO que el volumen resolvió: 26** (9 aciertos del lado, 13 fallos, 4
  parciales). Hacia FAVORABLE, por ejemplo Alavés–Deportivo 1570453 (3,17
  contra 0,24) y Augsburg–Mainz 1575224 (3,59 contra 1,22); hacia
  DESFAVORABLE, Fulham 1557474 y Lanús 1649569.
- **FAVORABLE de más: 19** (10 aciertos del lado por conversión, 9 fallos).
  Real Betis 1570462 (0,58 contra 2,25), Atlas 1551040 (1,19 contra 3,82),
  Marseille 1552822 (1,49 contra 4,07).
- **DESFAVORABLE de más: 5** (Internacional 1492458, Parma 1550205, Newcastle
  1557475, St. Truiden 1558683, Real Tomayapo 1645542).

Comparado con el 17/11 (14 NEUTRO de 20), el NEUTRO-refugio **se repite** y
el FAVORABLE de más **sube** (de unos 6 a 19, con 537 lecciones contra 347). El
cierre aplica bien la vara: separa la conversión, pone el penal al lado del
xG y no sube un veredicto por el marcador. El problema está en la apertura.

**Lo que haría falta medir** (fuera del skill, sobre los veredictos cerrados;
amplía el plan de DTP_v1.9_propuesta §5, que sigue sin correrse):
1. Población: lados con veredicto cerrado, `ramaJugada` calculada
   (`dtp.porBloque[].ramaJugada`), stats en la ficha y la rama jugada en ≥ 70
   minutos (las stats son del partido entero). xG sin penales, sin copas
   nacionales. Selecciones y clubes por separado.
2. Por lado: Δ = xG generado − xG concedido por 90 minutos, y el cociente;
   sin xG, los remates en el área.
3. Lecturas:
   - (a) qué banda de Δ separa lo que los cierres llamaron «parejo» del resto
     (acuerdo entre cierres, no contra el resultado);
   - (b) si el Δ del NEUTRO de la apertura se concentra cerca de 0 más que el
     de las otras etiquetas;
   - **(c) nueva:** si el Δ del FAVORABLE de la apertura se concentra en
     positivo más que el del NEUTRO. Si no, FAVORABLE tampoco informa;
   - **(d) nueva:** el mismo reparto separando los FAVORABLE y NEUTRO cuya
     razón se apoya en el nivel o en la contra (punto 1) del resto, para ver si
     la aclaración del punto 1 apunta donde está el error.
4. Corte temporal y bootstrap, como en los backtests del motor.

**Qué haría con el resultado:** solo con la banda medida se podría escribir
«NEUTRO pide un Δ esperado dentro de la banda». Hasta entonces la l. 333 no
cambia.

### 7. La vida útil 55-65 del improvisado como techo

**Qué dice hoy** (l. 169 y 176): improvisado, vida útil 55-65 minutos, «techo,
no piso». **Qué pasó:** dos `regla_fallo` (Progreso–Torque 1650502:a:4:
sostuvo el 1-1 del 28' al final, con reserva por el arquero; Bayern–Köln
1575221:b:5: sostuvo el 1-1 desde el 37' en Múnich **con 0 atajadas** de su
arquero) y los tres del punto 3, donde el improvisado sostuvo más allá del
techo. **Es un número calibrado:** no se toca. Medición: sobre los casos de la
6 cerrados (`cierre.casoBloque`) de bloques clasificados improvisados, cuántos
minutos sostuvieron contra un obligado, separando `sostuvoArquero` y la 5
respondida con el DT de hoy (si el punto 3 se aprueba, la clase de algunos
cambia y la medición tiene que esperar a esa población).

## 4. Lo que no entra (1-2 casos)

- **Un renglón que depende de una pieza escribe su heredero en todas las
  ramas**: solo Bayern–Köln 1575221:a:5 fuera de la rama persiguiendo. Los
  otros tres (Corinthians–Botafogo 1492450:b, Boston River–Maldonado
  1650500:b:5 y Sevilla–Betis 1570462:a:3) son la rama persiguiendo, que ya lo
  pide (l. 145): incumplimiento, a la app (§5). Volos 1593364:b:2 lo cumplió y
  la vía siguió viva con el heredero.
- **«Arriba, menos pelota» con el equipo de posesión que va arriba dentro de
  su plan**: São Paulo–Fluminense 1492457 (57 % arriba desde el 32'). Un caso.
- **Extremo expulsado que defendía hacia atrás contra el velocista recién
  entrado**: Wales–Portugal 1528992. Un caso.
- **La línea contraria nombra el seguro del rival, no solo «si se vuelca»**:
  Paris FC–Angers 1552825:b:7.
- **El tercer nombre de los penales («si entra») es el 9 que reemplaza al
  ejecutor**: Anderlecht–OH Leuven 1558680. Un caso; el 9 titular de la v1.9
  no falló ninguna vez.
- **Rest defense «fijo» de dos medios con pocas titularidades juntas**:
  Olympiakos–Iraklis 1593362. Un caso.
- **La rotación sin nada en juego no baja el veredicto sin un hecho**:
  Polonia–Suecia 1528998:b:2. Un caso.
- **La vía del banco del que persigue dice qué pasa si el DT goleado cierra**:
  Leverkusen–Paderborn 1575222. Un caso.
- **La contra tras el córner propio va en las vías del rival**: Puebla–San
  Luis 1551039 (dos lecciones del mismo partido).
- **La pieza que pierde en la salida se nombra por rol en toda la salida**:
  Newcastle–Arsenal 1557475 (dos lecciones del mismo partido).
- **De copa, contra un rival de dos a cinco categorías menos**: Sporting–UD da
  Serra 1647591, Gil Vicente–Olhanense 1647584, Sernache–Lourosa 1647594.
  Tres partidos, todos de copa: no acreditan.
- **Lesión de las dos piezas de la transición**: Instituto–Huracán 1649568
  (`imprevisto`).

## 5. Para la app (no entra al skill)

Las reglas que más se incumplen ya dicen lo correcto, y donde se aplicaron
sostuvieron. Repetir el texto no cambió la conducta. Revisado contra
`backend/` hoy (`dtp_cowork.py`, `parte.py`, `identidad.py`):

| Qué | Regla que se incumple (línea de hoy) y casos | Hoy |
|---|---|---|
| **Córners que concede el rival por sede, con `n`**, en los insumos de `dtp/{id}`; aviso del recibo cuando la pelota parada se declara sin ese dato | Materia del cruce (l. 109-111, v1.7-v1.9): 12 partidos. Grêmio 1492454, Troyes–Le Havre 1552827, Cercle 1558682, Juárez–Atlas 1551040, Rayo–Valencia 1570460, Audax 1505563, Torque 1650502, Remo–Chapecoense 1492456, Ucrania–Georgia 1528994 (quizás con la v1.8); Lorient 1552821, Werder 1575227, Gent 1558681 | Ningún campo de córners concedidos en `dtp_cowork.py`; la l. 109 ya lo da por pendiente |
| **Perfil de posesión del rival por sede, con DT y `n`**, y la rama «arriba» como campo de `m2.posesion` | Perfil en su condición de hoy (l. 214, 219): 9 partidos. Guaraní 1632066, Bucaramanga 1650173, Everton 1505565, Sevilla 1570462, Polonia 1528998, Ameliano 1632063, Tijuana 1551038; Elversberg–Freiburg 1575229 (los dos lados), Tigres 1551044 | `_rama_posesion` guarda `valor`, `contraQuien`, `marcador`, `sede`; ramas `igualadoOArriba` y `persiguiendo`, sin «arriba» ni DT ni `n` |
| **Referencia de volumen por sede y condición, con `n`**; aviso cuando la razón de una rama cita un xG de un solo partido o de la temporada | La referencia de volumen no viaja (l. 334, v1.8): 10 lecciones en 9 partidos, todas mal aplicadas. Le Mans 1552822, Vila Nova 1650247, Huracán 1649568, Schalke 1575228, América 1551044, Levadiakos 1593361, Volos 1593364, Chelsea–Leeds 1557470, IdV 1639806 | No existe |
| **Las piezas de la línea de cada duelo con `amarillasEnLaCompeticion`, la roja reciente y la vuelta de suspensión**, en los insumos del DTP; aviso cuando una pieza del duelo o del seguro con amarillas no figura en el renglón 11 | Vía de expulsión con toda la línea (l. 76-77, v1.7-v1.8): 10 mal aplicadas en 10 partidos (y 1 de copa). Ucrania–Georgia 1528994, Irlanda–Kosovo 1528997, Vitória 1492459, Audax 1505563 (el TDE del mismo parte tenía las 4 amarillas del central), Charleroi 1558683, Hoffenheim 1575223, Willem II 1552232, Villarreal 1570455, Kifisia 1593365, Atlético Nacional 1650176 | Viajan en la tabla F1; la l. 77 lo da por pendiente |
| **Identidad: Djené / «D. Dakonam»** a `backend/identidad.py` con su test | Getafe–Atlético 1570456: el parte lo dio fuera de la hoja (insumo) | `grep` no encuentra el alias en `backend/` |
| **Campo de la línea contraria** por rama (`{condicion, veredicto}`) y aviso del recibo cuando la condición es del rival, la contraria es menos favorable y el veredicto publicado no es el suyo | El veredicto con condición (l. 147, v1.8): 7 mal aplicadas en 7 partidos, y en las 7 se jugó la línea menos favorable. Troyes–Le Havre 1552827, Liverpool M. 1650504, Charleroi 1558683, Gladbach 1575226, Cali 1650174, OH Leuven 1558680, Metropolitanos 1646938 (ni la escribió) | `_veredicto_ramas` guarda `veredicto` y `razon`; **no** hay campo de la línea contraria (el estudio de la parte 2 lo daba por existente) |
| **Aviso de minuto fijo en el banco** («desde el NN'») | El banco va sin minuto fijo (l. 118, v1.8): Samsunspor 1584469, Juventus 1550201, Paris FC 1552825, Mushuc Runa 1639837 | No existe. Sigue pendiente también el aviso de un lado sin ningún nombre de `bancoProbable` (l. 119) |
| **`m3.quedaAtras` por rama**, que el recibo pida | Quién queda atrás en todas las ramas (l. 237-238, v1.7-v1.8): 10 partidos. Coritiba–Santos 1492451, Peñarol–Cerro Largo 1650501, Westerlo 1558682, Central Español 1650505, São Paulo 1492457, Santa Fe 1650175, Kocaelispor 1584472, Querétaro 1551046, Metropolitanos 1646938, Kifisia 1593365 | No existe |
| **Minuto habitual de salida de cada titular con el DT de hoy** | La vía persiguiendo sobrevive a los cambios (l. 145): Botafogo 1492450, Maldonado 1650500, Sevilla 1570462, Lommel–Standard 1558687 | La l. 145 lo da por pendiente |
| **M1-VS-ONCE-OFICIAL**, la hora de llegada de la formación y rechazar el depósito con `xiReferencia` vacío | El sistema se copia de la ficha (l. 73, v1.8) y al rehacer: Hull 1557472, Standard 1558687, LDU–Aucas 1639807 (los dos lados), Kalamata–AEK 1593360, Sevilla 1570462 (once a las 17:03, depósito a las 17:15); de copa, Marítimo–Chaves 1647587 con el `xiReferencia` vacío | Solo `M1-VS-ULTIMO-ONCE`; pendientes desde el 10/11 (PENDIENTES.md) |
| **Aviso «la razón cita sus vías por renglón»** y FAVORABLE por zona sin rematador nombrado | l. 143-144 (v1.8): Fenerbahçe 1584472, Gent 1558681, LDU 1639807, Bolívar 1645545 (el H del mismo parte decía NEUTRO) | La l. 144 lo da por pendiente |
| **Cruce de los titulares de banda y de segunda línea del grid contra el renglón 6**, y del rol reasignado sin renglón en `viasGol` | Punto 2, y el reconvertido también ataca (l. 78, v1.9): Frankfurt 1575223 (Knauff), Cercle 1558682 (Magnée), Puebla–San Luis 1551039 (Duarte). La regla se confirma: en los tres atacó | No existe |
| **Que no se generen lecciones del DTP en partes sin DTP** | Olimpia 1632065:a:5 y Libertad 1632067:b:3 | — |
| Las mediciones de los puntos 6 y 7 | — | No existen |

## 6. Núcleo e historial (punto 9)

- **Versión** (l. 8): «v1.9 (17.11.2026)» → «v1.10 (fecha de aplicación)».
- **Historial:** la nota de la v1.10 va **directo** a
  `references/HISTORIAL.md`, arriba de la v1.9, con el formato de las
  anteriores: los puntos aprobados con sus casos y fixtureIds, los candidatos
  (con el contraejemplo del seguro «sin» y la corrección del caso de la 6),
  lo que queda fuera (puntos 6 y 7, §4) y «De dónde sale» (estudio del 24/11,
  537 lecciones de 137 partidos del 17 al 23/11).
- **Anclas nuevas** en `scripts/nucleo_reglas.json`, `diagnostico-tactico`
  (las frases son literales del texto propuesto):
  - punto 1: «dice cuánto concede mientras espera»;
  - punto 2: «Figurar en otro renglón no saca a nadie de este»;
  - punto 3: «La 5 se responde con el DT de hoy»;
  - punto 4: «El rearme del doble pivote o del contenedor cuenta como el de la
    línea».

  Ninguna ancla vigente se toca («Candidatos abiertos (no regla)» sigue).
- **Tope de tokens:** el núcleo mide hoy unos 20,8 K (caracteres / 4) contra
  un tope de 22.859. El texto de los puntos 1 a 5 suma unos 1,0 K y la l. 349
  resta unos 30: queda por debajo del tope sin moverlo.

## 7. Coherencia con TDE v0.1.28 y EFE v1.12 (en redacción paralela)

| Dependencia | Qué tiene que decir el otro lado | Riesgo |
|---|---|---|
| **Rearme del medio ↔ TDE (disciplina 63, la pieza del seguro relevada por otra del mismo rol)** | El TDE nombra al heredero del seguro desde `m2.piezas` y el M3 de quién queda (de seguro, con el punto 4); no lo re-estima | Ninguno, si el TDE toma el «quién queda de seguro» del M3 |
| **Renglón 6 ↔ TDE (la vía del empate en la rama de ventaja copia las vías del DTP rival por renglón)** | El TDE copia el renglón 6 entero; con el punto 2, el lateral o el extremo centrador también figura como llegada | Ninguno: le da más nombres por rol, no sueltos |
| **Pregunta 5 ↔ EFE (D1, el DT)** | El EFE no clasifica el bloque: la clase y `c1Tde` las calcula el backend desde el checklist (`clasificar_bloque`). Si el punto 3 cambia respuestas de la 5, cambia la clase que hereda el TDE | Bajo: el recuento y la vida útil no cambian |
| **Punto 1 ↔ EFE (EJE-DEBUTANTE anuncia volumen concedido)** | Las dos hablan de volumen concedido como dirección, sin número | Ninguno |

## 8. Qué NO se propone

- **Ningún número** (banda de «parejo», vida útil, umbrales del MECANISMO,
  corte de DTP-REHACER, xG por penal, magnitud de la posesión).
- **Reescribir** pelota parada, posesión, referencia de volumen, vía de
  expulsión, línea menos favorable, banco, M3, grid ni rehacer: el texto está
  bien y lo que falta es el dato o el aviso (§5).
- **Tocar el reconvertido** (v1.9): 4 mal aplicadas y 2 sostenidas en su
  primera semana; en las cuatro el reconvertido atacó. Se confirma y no se
  cumple: es §5, no texto.
- **Candidatos de uno o dos casos** (§4), y **nada de copa** completa el
  umbral de ningún punto.

## 9. Decisiones del usuario

1. **El segundo de la lista de penales recibe la falta:** llega a 4 casos
   (Panathinaikos, Dinamarca, Dinamarca–Noruega, Racing–Real Sociedad; con
   reserva Barcelona), dos de selecciones. ¿Sube a regla o sigue candidato?
   *Recomendación: sigue candidato con los casos nuevos. La lista de dos ya
   cubre la conducta y una regla no cambiaría qué se escribe; Barcelona va en
   contra de la lectura obvia.*
2. **El candidato nuevo de la condición sostenida por el propio parte**
   (Köln, Excelsior): ¿entra al bloque de candidatos o queda solo en el
   historial? *Recomendación: entra al bloque, para que el cierre sume casos.
   No se escribe como excepción a la l. 147: con 2 casos limpios contra 7
   partidos donde la línea menos favorable acertó, una excepción ahora
   debilitaría la regla que sí funciona.*
3. **Punto 2, una línea más en la lista de salida:** el texto del renglón 6 ya
   se incumple desde el 17/11. ¿Se agrega la frase o se espera solo al cruce
   de la app (§5)? *Recomendación: agregarla. Cierra una lectura nueva (el
   nombre que «ya está» en otro renglón) y no repite lo escrito; la app hace
   el resto.*

Lo demás, con la recomendación de la tabla del §1 (regla conservadora: solo
aclaraciones con 3 partidos distintos o más; ningún número).
