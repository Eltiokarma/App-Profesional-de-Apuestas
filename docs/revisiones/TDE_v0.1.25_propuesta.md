# Propuesta de revisión · `teorema-del-echado` v0.1.24 → v0.1.25

**Estado:** PROPUESTA, pendiente de aprobación del usuario. No se tocó el
skill, ni el código, ni el estado de ninguna lección.

Se redactó el 01/11/2026 desde:

- el dossier (`GET /analisis/cowork/revision/teorema-del-echado`, generado el
  01/11 a las 05:08, versión vigente `v0.1.24`, cohorte `c3-2026-09-23`);
- las lecciones del skill (`GET /analisis/cowork/lecciones`, filtradas a
  `teorema-del-echado` + `pendiente`);
- el veredicto de cada partido de la cohorte
  (`GET /analisis/cowork/{id}/veredicto`, 399 con veredicto);
- el pendiente ya aprobado en `docs/revisiones/PENDIENTES.md` (incidencia 744).

## De dónde sale

- **Ventana:** las lecciones `pendiente` del TDE son **654**, todas de partidos
  del 26/10 al 01/11/2026, es decir, partes escritos con la v0.1.24 (disciplinas
  65 y 66). El encargo hablaba de unas 375, pero la cola creció: solo el 31/10
  dejó 264.
- **Población:** las 654 son `ciega` + `PRE`. Quedan **568 que acreditan** y
  pueden sostener un número. Las otras **86 son de copa nacional** (14 de ellas
  también en cuarentena) y solo fijan rúbrica: no entran a ninguna cuenta de
  abajo.
- **Veredictos de las 654:** 378 aciertos, 126 parciales y 150 fallos.
- **Piden mover un número:** 3, las tres sobre el corte en 7 de la disciplina 65
  (Recoleta–Ameliano 1632046:b, Milan–Inter 1550177:b, Riestra–Talleres
  1493216:a). Las tres son acreditables.
- **Modo de fallo (Jev):** 622 sin etiqueta, 25 `lectura_efe`, 5 `tde`. No
  ordena nada y no se usa para agrupar.
- **Lo que se leyó:** la lección entera de los 276 fallos y parciales. De los
  355 aciertos, la regla que tocan y una muestra. Se agruparon por la regla que
  citan y, dentro de cada regla, por la causa.
- **Lo que se midió:** los tramos que el veredicto calcula
  (`objetivo.tde.bloques[].tramos`, con `desenlace` e `iseRama`) y la
  `reasignacion` de cada bloque. Todo sobre los casos `ciega` + `PRE` sin copa
  ni cuarentena:
  - **Desenlace:** 220 tramos de 111 partidos (26/10 al 01/11).
  - **Ventaja y expulsiones:** 373 partidos de la cohorte (15/09 al 01/11).
  - Los intervalos son de Wilson al 95 %.

**Sesgo de atribución, declarado antes de proponer:** muchos fallos y
parciales dicen que la rama **se cumplió**. Algunos ejemplos: «declarada y
cumplida», «salida "marcó él": no cuenta contra la rama», «abierto no se
cobra», «acierto no testeado». Esos casos confirman la v0.1.24. Ahí lo que
falló fue el 1X2 del lado, que no es del TDE. Los cambios de abajo salen de lo
que **se midió** y de las lecciones que dicen **qué faltó escribir** o qué se
escribió mal.

## Respuesta corta

**Un número se mueve y es para quitarlo.** El defecto `se_rompe` con ISE de
rama ≥ 7 no separa nada: con ≥ 7 o con < 7 el que persigue concede igual. Se
propone retirarlo y dejar `abierto` como lectura por defecto. Lo demás es
rúbrica:

- qué cuenta como hecho para escribir `se_rompe` o `rescata`;
- la vía del gol, con la pelota parada ya aprobada;
- qué dice la referencia del minuto y qué no;
- el antecedente sostenido por el arquero;
- la roja propia temprana empatando;
- el añadido del primer tiempo y la prórroga.

Cuatro piezas se pueden **calcular** en la app en vez de pedírselas al modelo.

## Lo que no se toca

- La fórmula del IE, la del ISE y la del ISE de rama: `(SOB1 + SOB2 + SOB3) / 3 × 10`.
- Los pesos, las compuertas, las bandas, la ventana por defecto y el semáforo
  del IE (sigue bajo).
- Las disciplinas 61, 62, 63 y 64. La rama sigue cerrándose por su régimen y
  sus salidas, y el desenlace se mide aparte.
- El peso de `S1` dentro del bloque S. Hay 7 lecciones y ninguna medición.
- El registro: sin altas. Los casos de la app no son filas del registro.
- Nada calculado por el backend: el 1X2 del motor, `μ_partido`, la referencia
  `ventajaPorMinuto` ni los tramos del veredicto.

---

## Los cambios propuestos

### 1. El corte en 7 del desenlace no separa: se retira el defecto `se_rompe` (disciplina 65) — MUEVE UN NÚMERO

**Qué dice hoy el skill.** Con ISE de rama ≥ 7 la lectura por defecto es
`se_rompe`; con < 7, `abierto`. Escribir `rescata` contra el defecto exige un
hecho del partido. El corte se revisa con n ≥ 30 tramos jugados por lectura.

**Qué se midió.** Ya hay n de sobra: 95 tramos con `se_rompe`, 104 con
`abierto` y 19 con `rescata`. El desenlace observado es el evento que cierra el
tramo.

| ISE de rama | n | le meten otro (`se_rompe`) | iguala o pasa adelante (`rescata`) | sin más goles |
|---|---|---|---|---|
| ≥ 7 | 109 | 43 · 39 % (IC 31-49) | 44 · 40 % (IC 32-50) | 22 |
| < 7 | 111 | 45 · 41 % (IC 32-50) | 45 · 41 % (IC 32-50) | 21 |
| = 10 | 29 | 15 · 52 % (IC 34-69) | 10 · 34 % (IC 20-53) | 4 |
| 8,33 | 80 | 28 · 35 % (IC 25-46) | 34 · 42 % (IC 32-53) | 18 |
| 6,67 y 5 | 108 | 45 · 42 % (IC 33-51) | 44 · 41 % (IC 32-50) | 19 |

Sin los «sin más goles», el que persigue con ≥ 7 concedió antes de igualar el
49 % (43 de 87) y con < 7 el 50 % (45 de 90). **El corte no separa.**

La lectura `se_rompe` se cumplió **44 de 95 (46 %, IC 37-56)**, que es lo que
dice `acreditables.desenlaceTde` del 01/11. Es la misma cifra que la medición
anterior del encargo (23 de 48, 48 %, IC 35-62) con el doble de n. Y casi no
se aparta de lo que pasó con `abierto`, que no se cobra: 40 % de `se_rompe`
(42 de 104).

El ISE de rama se agrupa en tres valores (6,67 · 8,33 · 10), así que no hay
un corte fino que buscar. El único escalón que asoma es el 10: 52 % contra
38 % del resto, con los intervalos cruzados (34-69 contra 32-45) y n = 29. No
alcanza para un corte nuevo.

**Lo que sí separa son dos cosas que el corte no mira.**

- **Quién persigue.** El 1X2 declarado es un proxy del favorito: lo elige
  sad-analysis, no el TDE.

  | El que persigue | ISE de rama | n | `se_rompe` | `rescata` |
  |---|---|---|---|---|
  | el elegido por el 1X2 | ≥ 7 | 35 | 14 % (IC 6-29) | 60 % (IC 44-74) |
  | el elegido por el 1X2 | < 7 | 56 | 23 % (IC 14-36) | 61 % (IC 48-72) |
  | el otro | ≥ 7 | 74 | 51 % (IC 40-62) | 31 % (IC 22-42) |
  | el otro | < 7 | 55 | 58 % (IC 45-70) | 20 % (IC 12-32) |

- **Qué escribió el rival en su rama de ventaja.** El rival declaró en su
  `siMarcaPrimero`:
  - **«sigue atacando» (SOB):** el que persigue se rompió el 57 % (34 de 60,
    IC 44-68).
  - **`ECHADA-*` (administra):** se rompió el 35 % (17 de 48, IC 23-50) y
    rescató el 52 %.

  Es lo contrario de lo que leyeron dos autopsias (Bayern–Dortmund 1575203:b,
  Flamengo–Galo 1492423:b). Ellas tomaron «el rival sigue atacando» como hecho
  para escribir `rescata`. En la cohorte, el rival que sigue atacando es el que
  mete el segundo. Las dos señales están cruzadas: el que sigue atacando suele
  ser el favorito.

**Casos que lo piden.** 26 lecciones: 22 acreditables y 4 de copa. Ejemplos:

- Las tres que piden mover el número.
- Peñarol–Wanderers (1646899:a) y América–Tijuana (1550952:a): «caso a favor
  del corte».
- Pachuca–Tigres (1551023:b) y Prat–Athletic (1645579:a, copa): ISE ≥ 7 se
  rompió.
- Monza–Napoli (1550172:a), Sassuolo–Lazio (1550174:a) y Sporting
  Cristal–Alianza (1549534:a): ISE ≥ 7 rescató.
- Coritiba–Vitória (1492434:b) y Grêmio–Athletico (1492436:b): ISE < 7 se
  rompió.
- Bucaramanga–Pasto (1549725:a) y Barracas–Estudiantes (1493200:a): ISE < 7
  rescató.

Se leen en las dos direcciones, que es lo que dice la tabla.

**Qué se propone redactar.**

- **Se retira el defecto por ISE de rama.** Con cualquier ISE de rama, la
  lectura por defecto es **`abierto`**.
- `se_rompe` y `rescata` **se escriben solo con un hecho del partido** en
  `porqueDesenlace` (punto 2). Hoy el hecho se pide solo para ir contra
  `se_rompe`. Lo pidieron Sportivo San Lorenzo–Libertad (1632047:a) y Atlético
  Baleares–Eldense (1644343:a, copa).
- **El ISE de rama sigue siendo el número de la rama** (disciplina 62). Dice
  cuánto se expone el equipo, no cómo termina. La disciplina 65 deja de citar
  «2 de 38 contra 7 de 33»: esa medición (v0.1.24) contaba «lo da vuelta» y la
  de ahora cuenta el evento que cierra el tramo.
- **Candidato declarado, NO aplicado:** el defecto por **quién persigue**.
  - El favorito por `μ_partido` con margen ≥ 0.30, el mismo de la disciplina 44
    (b), persigue con defecto `rescata`.
  - El otro, con defecto `se_rompe`.

  Se mide con `μ_partido` y no con el 1X2 (el TDE no lee el 1X2) y entra en la
  v0.1.26 si con n ≥ 30 por lado los intervalos no se cruzan. Lo del rival que
  sigue atacando entra en la medición como segunda variable, no como regla.

**Qué NO se propone y por qué.**

- **Mover el corte a 10 u otro valor.** El escalón del 10 tiene n = 29 y el
  intervalo cruzado. Sería la disciplina 33 por la otra puerta.
- **Aplicar ya el defecto por favorito.** La medición usa el 1X2 de
  sad-analysis como proxy, y la disciplina 14 prohíbe que la lectura de un
  equipo se construya con el pronóstico de otro skill. Primero hay que medirlo
  con `μ_partido`.

**Calculable.** Con `μ_partido` de los dos lados (está en `/predicciones`), el
veredicto puede guardar en cada tramo con desenlace quién persigue: favorito
por μ con margen ≥ 0.30, o no. También puede guardar la tipología de la rama
de ventaja del rival. Aprendizaje lo cuenta en `acreditables.desenlaceTde`
como un corte más. El modelo no tiene que escribir nada nuevo.

### 2. Qué cuenta como hecho para escribir `se_rompe` o `rescata` (disciplina 65) — RÚBRICA

**Qué dice hoy.** «Escribir `rescata` exige un hecho del partido: un rival que
no sabe administrar, un banco ofensivo documentado o una roja rival.» No dice
qué NO es un hecho, ni que el hecho depende del once y del reloj.

**Qué casos lo piden.** 146 lecciones: 127 acreditables y 19 de copa. Las
causas:

- **El hecho escrito no era del partido de hoy.** El `rescata` no se cumplió
  en estos casos:
  - una racha o identidad del rival: Cajamarca–UTC (1549531:a), «0 victorias
    en el Clausura»;
  - el perfil de temporada: Fenerbahçe–Göztepe (1584451:a);
  - un antecedente de otra sede: Emelec–Leones (1639856:a), «perdió dos
    ventajas de local»;
  - un antecedente con otra línea del rival: City–Brighton (1557454:a);
  - un antecedente único: Villarreal–Espanyol (1570442:a) y Aston Villa–Fulham
    (1557447:a).

  Es la disciplina 6 (no predecir desde la identidad) y la regla del
  antecedente parecido de la 44 (b), sin escribir en la 65.
- **El hecho estaba y no se usó.** Hull–Ipswich (1557452:b) tenía el banco
  documentado y lo usó en `siIguala` pero no en `siRecibePrimero`. Otros casos
  con banco ofensivo documentado: Chicó–Junior (1549726:b), Aurora
  (1645527:b), Cerro (1646898:b), Fluminense–Inter (1492435:a) y Roma–Cagliari
  (1550168:b).
- **Otros hechos que no figuran en la lista de hoy:**
  - el bloque rival improvisado con su vida útil vencida: Standard–Kortrijk
    (1558668:a);
  - la zaga del rival rearmada o rotada: Fiorentina–Atalanta (1550169:a);
  - el volumen a favor desde antes del gol: Oruro–Potosí (1645528:a).
- **El hecho depende de cosas que cambian:**
  - **Del once.** Carabobo–La Guaira (1646922:b) se apartó del defecto por una
    línea de cinco que no salió. En Moreirense–Estrela (1575535:b) el once
    cambió el SOB2 y con él el ISE de rama.
  - **De los cambios que quedan.** Lille–Lens (1552802:b): el banco ofensivo
    ya había entrado y recibió al 86' sin cambios.
  - **Del reloj.** Feyenoord–Sittard (1552207:a): un `rescata` con el empate
    después del 85' no tiene tramo para probarse.
- **Cumplido por otra vía.** Monterrey–Tijuana (1551025:a): el `rescata` se
  cumplió con un penal, no con el banco escrito.

**Qué se propone redactar** (disciplina 65, punto nuevo «El hecho»):

- **Un hecho es del partido de hoy.** Vale:
  - un dato del once o del banco confirmado;
  - el estado del bloque rival según el DTP: improvisado, vida útil, zaga
    rearmada;
  - el volumen previsto por el motor o el DTP;
  - una roja rival.

  No valen la racha, la identidad ni el perfil de temporada (disciplina 6), ni
  un antecedente que no cumpla las tres coincidencias de la 44 (b): condición,
  perfil del rival y piezas.
- **Un antecedente solo, aunque se parezca, no alcanza** para apartarse de
  `abierto`.
- **El banco ofensivo como hecho se escribe condicionado** a los cambios que le
  queden al minuto del gol y al tiempo que quede: «si recibe antes del 75 con
  cambios por hacer». Si el empate o el gol en contra llega en los últimos
  minutos, la lectura es `abierto`.
- **Si el hecho se apoya en el once** (sistema, una pieza, el seguro de atrás),
  la rama se revisa cuando sale el once oficial, igual que el DTP. Es el modo
  `rehacer`.

**Qué NO se propone.** No se propone una lista cerrada de hechos con puntos: un
hecho no lleva peso (disciplina 14). Tampoco se cuenta el «rival que sigue
atacando» como hecho para `rescata`, porque lo medido en el punto 1 dice lo
contrario.

**Calculable.**

- En el **modo `rehacer`** la app ya reescribe el SOB2 y el C1 con el DTP
  rehecho. Puede recalcular también el ISE de rama de la rama afectada y
  avisar si el `porqueDesenlace` nombra una pieza que no está en el once
  oficial, con el mismo cruce de nombres de `identidad.py`.
- En el **veredicto**, el desenlace que cierra un penal o un autogol puede
  marcarse `porOtraVia`, como la salida del punto 3. Se muestra y no se cobra
  ni a favor ni en contra del hecho escrito.

### 3. La vía del gol: pelota parada en `otra_via`, y lo mismo para la ventana del reloj (disciplina 61) — RÚBRICA, YA APROBADA EN PARTE

**Qué dice hoy.** La disciplina 61 ya nombra la pelota parada entre las
causas de `otra_via`: «Penal, pelota parada o error individual sin la
exposición escrita». Pero la app calcula la salida solo con penal y autogol,
porque la API no marca la pelota parada. Un gol de córner o de tiro libre queda
`concedio` y se cobra contra la rama. La incidencia 744 lo aprobó el 31/10.

**Qué casos lo piden.** 73 lecciones: 63 acreditables y 10 de copa. En las
lecciones pendientes, 10 cierres nombran un gol de pelota parada que no era la
vía escrita; 6 son del 28/10 en adelante (encargo de PENDIENTES, sobre 544
lecciones del TDE de esas fechas):

- **En la salida de una rama:**
  - Troyes–Le Mans (1552809:b): córner, volea y rebote.
  - Cieza–Granada (1644347:a, copa): segunda jugada de un córner.
  - Remo–Botafogo (1492437:a): córner cabeceado con 2-0 defendiendo el área.
  - Lebrijana–Getafe (1644358:b, copa): falta lateral.
- **En la ventana del reloj o la base:**
  - Villarreal–Espanyol (1570442:a): centro de tiro libre en la 60-75.
  - Milan–Bologna (1550167:a): tiro libre desviado en la 60-75.
- **Antes del 28/10:** Tijuana–Santos (1551019:b, dos de tres goles), Coritiba–Grêmio
  (1492421:a) y Cúcuta–Águilas (1549727:a, probable).

El mismo problema aparece **con la ventana del reloj**, que hoy es `cobrable`
aunque el gol sea un penal. Lo marcan:

- Bayern–Dortmund (1575203:a): robo en el área propia.
- Vélez–San Lorenzo (1493226:a): el falsador de la echada no se gatilló.
- Lille–Lens (1552802:b): desgaste bajo dominio, no echada.

Y un patrón chico, sin regla todavía: **el segundo gol a 2-3 minutos del
primero**, antes de que el equipo se desarme persiguiendo
(Trinidense–Rubio Ñu, 1632049:a). Fueron 8 de los 61 tramos `siRecibePrimero`
que cerró un gol rival, a ≤ 3 minutos.

**Qué se propone redactar.**

- **La vía del gol se declara en el cierre** para cada gol concedido dentro de
  una rama o de la ventana del reloj: `exposicion` · `pelota_parada` (córner,
  tiro libre, saque lateral al área) · `error_individual` · `penal` ·
  `autogol`. Lleva fuente: crónica o video. **Sin fuente, el gol queda en la
  vía escrita** y se cobra como hoy. Riestra–Talleres (1493216:a, media
  distancia sin crónica) y Milan–Inter (1550177:b) se quedan como `concedio`.
- `pelota_parada` y `error_individual` llevan la salida a `otra_via`, igual que
  el penal: **ni a favor ni en contra de la rama**.
- **La ventana del reloj sigue la misma regla.** Un gol de `otra_via` dentro de
  la ventana no se cobra como acierto ni como error del tipo declarado. Es la
  disciplina 24 escrita para la ventana base.
- **La excepción: la pelota parada que ES la vía escrita.** Si el tipo o la
  rama nombraban la pelota parada como el riesgo (Coritiba–Grêmio, banco aéreo
  fresco del rival), el gol cuenta a favor. No es otra vía.

**Qué NO se propone.**

- Un tipo de echada o de SOB nuevo para la pelota parada.
- El «doble golpe» como salida. Son 8 casos, sin medición de qué pasa después,
  y el corte en minutos sería inventado. Se anota como candidato.

**Calculable.**

- **Penal y autogol ya lo son.** La app puede extenderlos a la ventana del
  reloj (`ventana_reloj` y la ventana de la rama hoy no los miran: el
  `cobrable` solo mira la roja previa y la clase roto o resuelto).
- **La pelota parada NO es calculable:** el evento de gol de la API trae
  `Normal Goal` · `Penalty` · `Own Goal` y nada de la jugada. Queda como juicio
  del cierre, con fuente. La app la toma del cierre y recalcula la salida al
  leer.
- **El doble golpe sí se puede medir:** los minutos entre el gol que abre el
  tramo y el que lo cierra ya están en los tramos. La app puede contar, para
  los que reciben a ≤ 3 minutos, qué pasa en el resto del partido, antes de
  que nadie lo redacte.

### 4. Qué dice la referencia del minuto y qué no (disciplina 66, con la 44 (a)) — RÚBRICA

**Qué dice hoy.** Con ventaja temprana (gol hasta el 30') se escribe primero
`siLeEmpatan`. Con ventaja tardía, una echada lleva la referencia «la ventaja
desde el 31 se sostuvo nueve de cada diez veces». La referencia la calcula la
app y no se copia.

**Qué se midió.** Equipos que marcaron primero, por su minuto. El
resultado es el final.

| Primer gol | n | no gana (empata o pierde) | pierde |
|---|---|---|---|
| hasta el 30' | 190 | 32 % (IC 26-39) | 16 % (IC 11-22) |
| desde el 31' | 167 | 27 % (IC 21-34) | 10 % (IC 6-15) |

El «nueve de cada diez» es **no pierde**. Pero desde el 31' al que marcó
primero se lo empatan o se lo dan vuelta **uno de cada cuatro**. Hasta el 30',
uno de cada tres. **La línea del empate se juega en las dos.** Lo que el minuto
separa es la derrota, no el empate.

**Qué casos lo piden.** 138 lecciones: 122 acreditables y 16 de copa. Las
causas:

- **La referencia se leyó como «ventaja segura».** Ventajas tardías perdidas,
  casi todas empatadas, con la referencia como única lectura de la rama:
  - Monterrey–Tijuana (1551025:a): dos veces en ≤ 4 minutos.
  - Caracas–Monagas (1646925:a).
  - Peñarol–Wanderers (1646899:b): empate al 90'.
  - Oriente–Aurora (1645527:a).
  - Fenerbahçe–Göztepe (1584451:a).
  - Bayern–Dortmund (1575203:a).
  - Hull–Ipswich (1557452:a).
  - Feyenoord–Sittard (1552207:a).
  - Unión–Estudiantes (1493211:b).

  Cuatro (Caracas, Fenerbahçe, Hull y Feyenoord) nombran **el banco ofensivo
  fresco del rival** como lo que faltó escribir; en copa, también Numancia–Oviedo
  (1644364:a).
- **Se citó la referencia del minuto que no era.** Estudiantes–Instituto
  (1493217:b) y Bucaramanga–Pasto (1549725:b) llevaban en la nota la
  referencia del 31', y el gol fue al 3' y al 23'. Antes del pitazo no se sabe
  el minuto: copiar una de las dos es elegir el escenario.
- **Confirmaciones.** Con ventaja temprana se jugó la línea del empate, escrita
  primero: Cerro (1646898:b), Sportivo San Lorenzo (1632047:b), Vélez
  (1493226:a), Xerez y Lebrijana (copa). Con ventaja tardía se sostuvo:
  Cúcuta–Águilas (1549727:b), Once Caldas (1549731:a), Tolima (1549837:b).

**Qué se propone redactar.**

- **La referencia se lee completa:** no pierde y gana. «Desde el 31' no
  pierde nueve de cada diez, pero no gana uno de cada cuatro.» La app ya
  devuelve las dos columnas en `referencias.ventajaPorMinuto`. La nota no copia
  números: cita la referencia.
- **`siLeEmpatan` se escribe con su número en las dos ventajas**, temprana y
  tardía. Con la temprana, primero. Con la tardía, sin sacarla de la nota por
  la referencia.
- **La rama de ventaja nombra el banco ofensivo del rival que persigue**: qué
  delanteros frescos tiene y si suele meterlos. Es la vía por la que se cae
  una ventaja tardía en esta cohorte.
- **No se copia en la nota la referencia de un minuto que todavía no pasó.**
  Se escribe «ver `ventajaPorMinuto`» y el veredicto pone la del minuto real.

**Qué NO se propone.**

- **Condicionar la referencia a la tipología declarada.** En la cohorte, quien
  escribió «sigue atacando» con ventaja no la perdió más: no ganó el 16-17 %,
  contra el 33-39 % de quien escribió `ECHADA-*`. Pero ese cruce es de
  selección, porque el favorito escribe SOB. No es una regla del tramo, y la
  disciplina 66 ya dice que el IE no anuncia el empate.
- **Mover el corte del 30'.** Nadie lo pidió y la tabla lo sostiene.

**Calculable.**

- **La referencia ya lo es.** El veredicto puede marcar `referenciaCitada` y
  avisar si la nota de la rama cita una cifra de la referencia del otro tramo
  de minutos.
- **El banco ofensivo del rival es calculable en parte:**
  - goles y asistencias de suplentes en la temporada, desde `fixture_eventos`
    y las alineaciones;
  - los delanteros del banco del último once.

  Puede viajar en `GET /analisis/cowork/tde/{id}` como insumo, igual que P1a y
  F2.

### 5. El antecedente que sostuvo el arquero no es antecedente (disciplina 44 (b) y (f)) — RÚBRICA

**Qué dice hoy.** Un antecedente sostiene «administra» o «sostiene el punto»
solo si coincide en condición, perfil del rival y piezas.

**Qué casos lo piden.** 129 lecciones: 110 acreditables y 19 de copa. La
mayoría son **confirmaciones** de la regla de la v0.1.23:

- Mechelen–Genk (1558666:a), Coventry–Sunderland (1557451:a), Juárez–Querétaro
  (1551021:a) y Genoa–Juve (1550171:a): antecedente parecido y rama cumplida.
- Bayern–Dortmund (1575203:b), Fenerbahçe (1584451:b), Xerez y Poblense
  (copa): antecedente no parecido y rama caída.

Lo nuevo:

- **Antecedentes sostenidos por el arquero, no por el bloque.**
  - Monterrey–Tijuana (1551025:b): el Azteca, «un empate sostenido por el
    arquero».
  - Bucaramanga–Pasto (1549725:b): el antecedente de Ibagué lo sostuvo
    Banguera, y hoy concedió dos con 3,14 de xG en contra.
  - América–Pachuca (1551017:b): «lo sostuvo el arquero, no la estructura».
- **Un antecedente que ya se había roto.** Flamengo–Galo (1492423:b): el
  antecedente de Montevideo se había roto en el 89' y el 90+3.
- **La regla del parecido también para `ECHADA-PSI`.** Riestra–Talleres
  (1493216:b) escribió ECHADA-PSI por «dos ventajas perdidas» (una en la
  Bombonera ante un rival superior) y hoy el rival cedía la pelota.
  Emelec–Leones (1639856:b) escribió lo mismo por dos ventajas perdidas de
  local, y sostuvo y amplió. Leverkusen–Stuttgart (1575204:b) se apoyó en C3 y
  en la menor μ, y el equipo no se echó.
- **Una pieza clave ausente.** Roma–Cagliari (1550168:b): faltaba Winks, pieza
  del antecedente. La regla ya lo dice, pero se escribió «administra» igual,
  con la reserva en la nota.

**Qué se propone redactar** (44 (b), con efecto en (f)):

- **Un antecedente vale si lo sostuvo el bloque.** Si el resultado lo sostuvo
  el arquero (muchas atajadas, xG en contra alto) o el rival falló solo, no es
  antecedente de administrar. Se dice cuál de las dos cosas fue.
- **Un antecedente que terminó roto** (concedió al final aunque no perdiera)
  no sostiene «administra» ni «sostiene el punto».
- **Para `ECHADA-PSI` vale la misma regla.** «Perdió ventajas» tiene que
  coincidir en condición, perfil del rival y piezas. C3 = 1 sigue siendo el
  tope del bloque C (disciplina 49), pero no elige la tipología de la rama.
- **Con la pieza del antecedente ausente, la rama vuelve al defecto.** No
  basta con dejar la reserva escrita en la nota.

**Qué NO se propone.** No se propone un umbral de atajadas ni de xG para decir
«lo sostuvo el arquero». No hay medición y sería inventarlo. Se dice con el
dato a la vista.

**Calculable.** La app tiene las stats de la ficha del antecedente (xG en
contra, atajadas) cuando el partido está en la base. Con el `fixtureId` del
antecedente en la rama, el recibo puede mostrarlas al lado. El juicio sigue
siendo del analista.

### 6. La roja propia temprana empatando: `ECHADA-NUM` no es resistir (disciplina 16) — RÚBRICA

**Qué dice hoy.** Con roja propia yendo empatado o ganando, el tipo migra a
`ECHADA-NUM` y el ISE se lee anulado: «puede elegir resistir». No dice qué
suele pasar con esa echada.

**Qué se midió.** Concesión después de la primera roja propia, por el
marcador en ese momento:

| Marcador al ver la roja | hasta el 45' | desde el 46' |
|---|---|---|
| empatado | **11 de 12 conceden** (92 %, IC 65-99) | 8 de 19 (42 %, IC 23-64) |
| ganando | 2 de 3 | 7 de 16 (44 %, IC 23-67) |
| perdiendo | 5 de 8 (62 %) | 13 de 32 (41 %, IC 26-58) |

**Qué casos lo piden.** 55 lecciones: 49 acreditables y 6 de copa.

- **Echada larga que se agota.** Melgar–Comerciantes (1549530:a): roja al 4'
  con 0-0 y concesión al 86'. Delfín–Cuenca (1639830:b): roja al 45+1 y se
  partió al 80'. Barracas–Estudiantes (1493200:b): «la echada numérica no
  aseguró el punto».
- **`ECHADA-NUM` no apaga el gol propio.** ABB–Bulo Bulo (1645529:b) marcó dos
  en seis minutos con diez. Nacional Potosí (1645528:b) siguió yendo y marcó
  un gol que anuló el VAR.
- **El agravado perdiendo, al revés.** ADT–Moquegua (1549527:b) metió
  defensores con diez y perdiendo. Es un solo caso.
- **Superioridad que no administra.** Confirmada en 9 lecciones: ABB
  (1645529:a), Comerciantes (1549530:b), Inter de Bogotá (1549728:b),
  Cajamarca (1549531:b), Tottenham (1557456:a) y los de copa.
- **Prórroga en copa** (solo rúbrica): SS Reyes–Coria (1644377:a) y
  Gimnástica–Ourense (1644381:a). La rama de expulsión de un partido único
  necesita su ventana hasta el 120.

**Qué se propone redactar** (disciplina 16):

- **Con roja propia empatando antes del descanso, `ECHADA-NUM` es una echada
  larga, no un punto asegurado.** La línea de `siExpulsion.propia` dice que el
  riesgo es la vía echada en el tramo final (ventana del reloj 75-90) y que el
  ISE anulado no la apaga. En la cohorte concedieron 11 de 12. Es referencia,
  no peso: el IE no se toca.
- **El ISE anulado no anula la vía de gol propia.** La línea dice también por
  dónde puede marcar el que se echa (contra, pelota parada), porque eso
  reordena el 1X2 de sad-analysis.
- **En un partido único con prórroga**, las ramas de expulsión y de empate
  llevan su ventana hasta el 120.

**Qué NO se propone.**

- Un número para la roja temprana: n = 12 y el intervalo es ancho.
- Tocar el desdoble por marcador: lo perdiendo y lo ganando no separan.
- Contar la expulsión del DT (Santa Fe–Bucaramanga, 1549822:b): es un solo
  caso.

**Calculable.** La tabla de arriba sale de los tramos del veredicto (`rojaPropia`,
`estado`, `concedio`). Puede viajar como referencia en `GET …/tde/{id}`, igual
que `ventajaPorMinuto`, para que la nota la cite y no la copie.

### 7. La casilla del añadido mira los dos tiempos, y la prórroga se declara (disciplina 23) — REDACCIÓN

**Qué dice hoy.** «El cierre cuenta aparte el gol concedido en el añadido del
segundo tiempo.»

**Qué casos lo piden.** 14 lecciones: 11 acreditables y 3 de copa.

- **El añadido del primer tiempo también reordena las ramas.**
  Monterrey–Tijuana (1551025:b) recibió el 2-2 en el 45+4 y Vélez–San Lorenzo
  (1493226:a) el 2-1 en el 45+1.
- **Goles y rojas del añadido final.** Los Chankas–Cusco (1549533:a),
  Moreirense–Estrela (1575535:b) y Unión–Estudiantes (1493211:b).
- **La prórroga, en copa** (solo rúbrica): Real Ávila–Unionistas (1644371:a) y
  SS Reyes–Coria (1644377:a).

**Qué se propone redactar.**

- La casilla `anadido` cuenta **los dos añadidos**. La app ya lo hace:
  `anadido_del_cierre` toma todo gol con `enAnadido`, y el del 45+4 de
  Monterrey figura. El texto del skill se alinea con eso.
- Si el partido va a prórroga, el output dice que la prórroga no está cubierta
  por las seis ventanas, igual que el añadido. El gol de la prórroga se cuenta
  aparte y no se cobra a ninguna ventana.

**Qué NO se propone.** Una ventana `90+` ni una séptima ventana: la serie del
75-90 estricto no se toca.

### 8. `S1` y el arquero: insumos que la base ya tiene (bloque S, ARQUERO-NUEVO) — CALCULABLE, SIN PESO

**Qué casos lo piden.** 7 lecciones: 6 acreditables y 1 de copa.

- **La roja que `S1` anticipó y luego ordenó el partido.** ABB–Bulo Bulo
  (1645529:b) tenía rojas en sus dos últimos partidos. Santa Fe–Bucaramanga
  (1549822:b) tenía tres rojas de local.
- **Datos de `S1` que no se miraron.** En Los Chankas–Cusco (1549533:a), el
  pivote único llegaba con 7 amarillas y una roja en el año y vio la segunda
  amarilla al 90+2. En Gimnástica–Ourense (1644381:b, copa), Ferreiro llegaba
  con una roja de liga y `S1` quedó sin dato.
- **El arquero nuevo no declarado.** Cambuur–Go Ahead (1552211:b): Cillessen,
  con 0 partidos de liga, atajó por Haug y no se declaró ARQUERO-NUEVO.

**Qué se propone redactar.**

- `S1` se puntúa con los insumos de la base cuando la app los dé. No se
  estiman.
- Si el arquero del once oficial no es el habitual, se declara ARQUERO-NUEVO
  al rehacer.

**Qué NO se propone.** No se toca el peso de `S1`. La disciplina 16 ya dice que
`S1` no es un indicador más, y cambiar su peso pide medición en positivos
(disciplina 22), que no hay.

**Calculable.**

- **Insumos de `S1`.**
  - Las rojas del equipo en la temporada.
  - Los jugadores del once probable con amarillas al borde del ciclo
    (`backend/sanciones.py` ya da `amarillasEnLaCompeticion` y la regla por
    competición).
  - Las rojas de los últimos partidos.

  Pueden viajar en `GET …/tde/{id}` junto a P1a, F1 y F2.
- **ARQUERO-NUEVO** sale del once oficial contra los minutos del arquero en la
  tabla F1. La app puede avisarlo como alerta calculada, igual que
  `ONCE-SIN-FILA-F1`.

### 9. Confirmaciones que se cierran sin cambio

**66 lecciones**: 58 acreditables y 8 de copa. Dicen que la regla vigente se
cumplió o que el escenario no existió. Se cierran con la v0.1.25 sin texto
nuevo:

- **Configuración dual (disciplina 43):** 13 lecciones, ninguna echada en un
  dual. Ejemplos: Gladbach (1575208:a), Leverkusen (1575204:b), Milan–Inter
  (1550177:a), Parma–Udinese (1550173:a), Once Caldas (1549731:a) y Coritiba
  (1492421:b). Roma–Cagliari (1550168:b) podría ser la primera echada en un
  dual, pero sin dato de altura de línea no se computa. Queda a la vista: la
  regla cae con un caso.
- **Acierto no testeado, rama abandonada y relevancia (17, 3, 24, 29 y 50).**
  Kocaelispor (1584454:a), Metropolitanos (1646923:a), Coventry (1557451:a) y
  San Luis–Atlas (1551020:a).
- **Banda 5-7 sin echada (disciplina 20).** Parma–Udinese (1550173:b) y
  Milan–Bologna (1550167:b).
- **Dos incumplimientos que ya tienen alerta.**
  - Kocaelispor (1584454:a) declaró ECHADA-VOL con ISE > IE e ignoró
    `TIPOLOGIA-VS-INDICES`.
  - Rayo–Celta (1570441:b) y Xerez–Cádiz (1644386:a, copa) escribieron el SOB2
    de la rama contra el nivel «persiguiendo» del DTP. **Calculable:**
    `HERENCIA-DTP` puede comparar también el `sob2` de la rama que persigue con
    el nivel del DTP persiguiendo, no solo el de la base.
- **SOB1 = 1 sin volcarse.** En Gladbach–Paderborn (1575208:a), el colista con
  DT de transición cedió la pelota. Es un solo caso y no se toca.

---

## Lo que tendría que hacer la app si se aprueba

Va aparte del skill y se hace después de aprobar. Todo es al leer o en el
recibo; nada mueve un número calibrado.

1. **Desenlace:**
   - el defecto por ISE pasa a `abierto` para los partes desde la v0.1.25. Lo
     anterior se cobra con su regla (`regla_desenlace_vigente`, con su fecha);
   - el recibo pide `porqueDesenlace` para `se_rompe` y para `rescata`;
   - el veredicto guarda en cada tramo quién persigue por `μ_partido` y la
     tipología de la rama de ventaja del rival;
   - Aprendizaje lo cuenta (punto 1).
2. **Vía del gol:**
   - el cierre acepta `viaGol` por gol concedido, con fuente;
   - la salida y la ventana del reloj pasan a `otra_via` con penal, autogol o
     la vía declarada;
   - el desenlace cerrado por otra vía lleva `porOtraVia`;
   - el doble golpe se mide antes de redactarlo (punto 3).
3. **Referencias en `GET …/tde/{id}`:** el banco ofensivo del rival (punto 4),
   la concesión tras roja propia por marcador y minuto (punto 6) y los
   insumos de `S1` (punto 8).
4. **Alertas calculadas:**
   - `ARQUERO-NUEVO` desde el once oficial;
   - `HERENCIA-DTP` también en el `sob2` de la rama que persigue;
   - el aviso de la nota de ventaja que cita la referencia del otro tramo de
     minutos.
5. **Modo `rehacer`:** recalcula el ISE de rama y avisa si el `porqueDesenlace`
   nombra una pieza fuera del once (punto 2).
6. **`lecciones.CORTE_VERSION` y `SUBIDA_VERSION`** con la fecha de la
   v0.1.25, cuando se suba.

## Lo medido que NO entra

- **El corte del ISE de rama en 10:** 52 % contra 38 %, con el intervalo
  cruzado y n = 29.
- **La tipología de la rama de ventaja contra perder la ventaja:** SOB no
  gana el 16-17 % y ECHADA el 33-39 %. Es selección (el favorito escribe SOB),
  no una regla del tramo.
- **Los «sin más goles» por minuto en que se abre el tramo.** Los tramos que
  abren desde el 76' terminan sin más goles 17 de 26 veces. Eso explica parte
  de los `se_rompe` incumplidos, pero no pide otra lectura: con `abierto` por
  defecto ya no se cobra.

## Sesgos y límites

- **Proxy del favorito.** La separación por quién persigue se midió con el 1X2
  declarado (sad-analysis), no con `μ_partido`. Por eso entra como candidato.
- **Lo observado no es lo de la v0.1.24.** La v0.1.24 midió «lo da vuelta» y
  «le meten otro en algún momento»; el veredicto mide el evento que cierra el
  tramo. Las dos cifras no se comparan entre sí.
- **El defecto nunca se aplicó solo.** De los 109 tramos con ISE ≥ 7, 88
  escribieron `se_rompe` a mano. La medición es de lecturas declaradas que
  siguieron el defecto, no del defecto aplicado en silencio.
- **Una semana de partes.** Los 220 tramos del desenlace son del 26/10 al
  01/11. La de ventaja y rojas usa toda la cohorte c3.
- **La pelota parada se contó en la prosa**, no en el evento: la API no la
  marca.
- **La versión en la cuenta.** El dossier da v0.1.24 como vigente. Si el zip
  no se subió antes del 26/10, parte de esos partes corrió con el prompt
  nuevo y el skill viejo, como pasó con la v0.1.22.

## Cómo se midió

Los scripts están en el scratchpad de la sesión del 01/11:

- `des25.py`: desenlace por ISE de rama y por lectura.
- `med25.py`: quién persigue y doble golpe.
- `med25b.py`: ventaja por minuto y tipología.
- `med25c.py`: concesión tras roja propia.
- `med25d.py`: desenlace según la rama de ventaja del rival.
- `grp25.py` y `pts25.py`: agrupación de las lecciones.

Leen los veredictos de `GET /analisis/cowork/{id}/veredicto` y las lecciones
de `GET /analisis/cowork/lecciones`. Se excluyen las copas nacionales y la
cuarentena.

## Resumen

| # | Punto | Disciplina | Tipo | Lecciones | Acreditables | Fallos · parciales · aciertos |
|---|---|---|---|---|---|---|
| 1 | Se retira el defecto `se_rompe` por ISE ≥ 7; queda `abierto`; candidato por favorito | 65 | **mueve un número** (quita el corte) | 26 | 22 | 6 · 4 · 16 |
| 2 | Qué es un hecho para `se_rompe` o `rescata` (del partido, condicionado al once, a los cambios y al reloj) | 65 | rúbrica + calculable (rehacer, `porOtraVia`) | 146 | 127 | 32 · 29 · 85 |
| 3 | Vía del gol: pelota parada y error en `otra_via`, también en la ventana del reloj | 61, 24 | rúbrica (744 aprobada) + calculable (penal y autogol en el reloj) | 73 | 63 | 26 · 10 · 37 |
| 4 | La referencia del minuto: no pierde y gana, línea del empate en las dos, banco del rival | 66, 44 (a) | rúbrica + calculable (banco del rival) | 138 | 122 | 31 · 24 · 83 |
| 5 | El antecedente que sostuvo el arquero, el que terminó roto y ECHADA-PSI | 44 (b), (f) | rúbrica | 129 | 110 | 22 · 27 · 80 |
| 6 | Roja propia temprana empatando: echada larga; prórroga hasta el 120 | 16 | rúbrica + referencia calculable | 55 | 49 | 10 · 14 · 31 |
| 7 | La casilla del añadido mira los dos tiempos; la prórroga se declara | 23 | redacción | 14 | 11 | 4 · 3 · 7 |
| 8 | Insumos de `S1` y ARQUERO-NUEVO desde la base | bloque S | calculable, sin peso | 7 | 6 | 3 · 2 · 2 |
| 9 | Confirmaciones sin cambio (dual, no testeado, relevancia, banda 5-7) | 43, 17, 20, 50… | cierre sin texto (+ `HERENCIA-DTP` en el sob2 de rama, calculable) | 66 | 58 | 16 · 13 · 37 |
| | **Total** | | | **654** | **568** | **150 · 126 · 378** |

Las 86 lecciones de copa nacional están repartidas en sus puntos y fijan
rúbrica: no sostienen ningún número. La única que mueve uno, el punto 1, se
sostiene en los 220 tramos acreditables de la medición, no en las lecciones
sueltas.
