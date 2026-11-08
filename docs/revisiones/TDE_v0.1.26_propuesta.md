# Propuesta de revisión · `teorema-del-echado` v0.1.25 → v0.1.26

**Estado:** PROPUESTA, pendiente de aprobación del usuario. No se tocó el
skill, ni el código, ni el estado de ninguna lección.

Se redactó el 08/11/2026 desde:

- el dossier (`GET /analisis/cowork/revision/teorema-del-echado`, generado el
  08/11 a las 02:31, versión vigente `v0.1.25`, cohorte `c3-2026-09-23`);
- el skill vigente (`docs/skills/teorema-del-echado/SKILL.md` y
  `references/`) y la propuesta anterior (`TDE_v0.1.25_propuesta.md`);
- lo que quedó pendiente de la app en `docs/revisiones/PENDIENTES.md`.

## De dónde sale

- **Ventana:** **638 lecciones** `pendiente`, de **169 partidos** del 01/11 al
  07/11/2026. Todas `ciega` + `PRE`. Son partes de la v0.1.25, salvo el tramo
  de las 04:47 del 01/11, que corrió con la v0.1.24 (ver «Sesgos»).
- **Población:** **610 acreditan**; **17 son de copa nacional** (Copa de la
  División Profesional de Bolivia: The Strongest–Always Ready, Nacional
  Potosí–Oriente, Aurora–Petrolero, Bolívar–Real Potosí) y **11 están en
  cuarentena que enseña** (Paranaense–Vasco y PAOK–Asteras, DT del parte
  distinto del que dirigió). Copa y cuarentena fijan rúbrica y no entran a
  ninguna cuenta.
- **Veredictos de las 638:** 320 aciertos, 144 parciales y 174 fallos.
- **Piden mover un número (Jev):** **ninguna**. `lectura` del dossier: «la
  revisión fija rúbrica; un cambio de peso no tiene quien lo sostenga».
- **Modo de fallo (Jev):** 598 sin etiqueta, 30 `lectura_efe`, 8 `tde`, 1
  `insumo`, 1 `imprevisto`. No ordena nada y no se usó para agrupar.
- **Lo que se leyó:** la lección entera de los 318 fallos y parciales, y todas
  las de expulsión, `siIguala`, configuración dual, ventana, añadido,
  relevancia, `S1` y las que no citan disciplina. De los aciertos, la regla que
  tocan y una muestra. Se agruparon por la causa, no por la etiqueta de
  `reglaTocada` (el dossier trae 351 etiquetas distintas para las mismas
  veinte reglas).
- **Lo que NO se midió esta vez:** no se bajaron los veredictos por partido.
  Los únicos números de abajo son los del dossier (`metricas.desenlaceTde`,
  `metricas.ventanaTde`) y los conteos de lecciones. Ninguno es una tasa de
  acierto.

**Sesgo de atribución, declarado antes de proponer:** buena parte de los 174
«fallos» dicen en la propia lección que la regla del TDE **se cumplió**
(«declarada y cumplida», «confirmación», «abierto no se cobra», «no cuenta
contra la rama»). Lo que falló ahí fue el 1X2 del lado, que no es del TDE. Los
cambios de abajo salen de lo que las lecciones dicen que **faltó escribir o se
escribió mal**, y de una regla de la v0.1.25 que los partidos contradicen.

## Respuesta corta

**Ningún número se mueve.** La v0.1.25 se sostiene: el desenlace `abierto` por
defecto, la vía del gol con fuente, la referencia del minuto leída completa y
la línea del empate en las dos ventajas aparecen confirmados decenas de veces.
Lo que se propone es rúbrica:

1. «Sostiene el punto» en `siIguala` se sigue escribiendo sin motivo: se dice
   qué NO es motivo.
2. En la rama de ventaja, el defecto «sigue atacando» es solo de tres; para los
   demás, la falta de antecedente no elige tipología.
3. El antecedente coincide también en el marcador que se cuidaba y en la
   cuenta de jugadores.
4. Con roja propia, el riesgo arranca con la roja, no en el 75-90 (corrige un
   texto de la v0.1.25).
5. El banco se nombra de la hoja: ocho partes nombraron como banco a
   titulares.
6. Cuando sale la pieza que sostiene el seguro de atrás, el cierre lo dice.
7. `S1` mira a los titulares que van al choque.

Y una contradicción para que **decida el usuario**: F2 subido a mano por viaje
y altitud (punto 8).

Casi todo lo nuevo se puede **avisar desde la app** en vez de pedírselo al
modelo, y lo pendiente de la v0.1.25 sigue sin hacerse (sección «Para la app»).

## Lo que no se toca

- La fórmula del IE, la del ISE y la del ISE de rama.
- Los pesos, las compuertas, las bandas, la ventana por defecto y el semáforo
  del IE (sigue bajo: las 98 «ventanas con gol» que el dossier cuenta en
  `liston.observadoAca` son de nuestra base y no son echadas expresadas en el
  esquema vigente de 6 indicadores, que es la condición (a) del listón; el
  registro sigue con 0 positivos que cuenten).
- La disciplina 65 tal como quedó: `abierto` por defecto con cualquier ISE de
  rama, `se_rompe` y `rescata` con un hecho de hoy.
- Las disciplinas 61 (la rama se cobra por su salida; sin fuente, el gol queda
  en la vía escrita), 66 (referencia completa, línea del empate en las dos
  ventajas, no copiar la referencia de un minuto que no pasó) y 43
  (configuración dual).
- El desdoble de la roja por marcador (disciplina 16) y la cifra de la v0.1.25
  (11 de 12 conceden con roja propia empatando antes del descanso).
- El peso de `S1`.
- El registro: sin altas. Los casos de la app no son filas del registro.
- Nada calculado por el backend: P1a, F2, F1, `μ_partido`,
  `ventajaPorMinuto` ni los tramos del veredicto.

---

## Los cambios propuestos

### 1. «Sostiene el punto» en `siIguala`: qué NO es motivo (disciplina 44 (f)) — RÚBRICA

**Qué dice hoy.** El que iguala «por defecto sigue empujando»; «sostiene el
punto» solo se escribe nombrando por qué, con un antecedente que se parezca,
que lo haya sostenido el bloque, que no haya terminado roto y con la pieza
disponible.

**Qué casos lo piden.** 17 lecciones de 17 partidos nombran «sostiene el
punto». En **13 se escribió sin un motivo válido y el equipo concedió o siguió
empujando**. Es la regla vigente incumplida una y otra vez, también con partes
del 03 al 07/11 (v0.1.25). Los motivos que se escribieron:

- **El empate que sirve o la visita:** Málaga–Racing (1570447:b, «el punto
  fuera le sirve»; marcó a los 10 minutos del empate), Guabirá–Bolívar
  (1645531:a, concedió en el 90+1), Groningen–Sparta (1552215:b) y PAOK–Asteras
  (1593351:b, cuarentena).
- **El calendario o la fatiga:** Getafe–Sevilla (1570438:a, «Brighton el
  jueves»; metió el 2-1 a los cinco minutos) y Groningen–Sparta («los 120
  minutos del miércoles»).
- **El DT nuevo:** Venezia–Udinese (1550196:b, «el debut del DT»; concedió a
  los 8) y Başakşehir–Samsunspor (1584449:b, «DT de dos partidos»; concedió a
  los 3).
- **La llave o la semifinal:** Aurora–Petrolero (1645454:b, copa: «no tiene
  obligación de ganar»; concedió a los 4) y Paranaense–Vasco (1492440:b,
  cuarentena: «la semifinal y la visita»; a los 2 minutos iba 1-2).
- **Un antecedente que no sostiene:** débil por la propia nota
  (Independiente–Riestra, 1493235:b, concedió al minuto), roto (St.
  Truiden–Leuven, 1558669:b; Frankfurt–Hamburgo, 1575205:b), o de otro
  marcador (Boston River–Torque, 1646901:a; Antwerp–Lommel, 1558671:b: punto 3).

**En contra o con matices.**

- Monterrey–Tijuana (1551025:b): con el motivo escrito no sostuvo el 2-2 y sí el
  3-3 durante 30 minutos.
- Porto–Napoli (1635656:b) y Atlético Grau–Universitario (1549541:a)
  sostuvieron la ventana del empate y se rompieron después: Porto al 71' con un
  bloque improvisado de vida útil 55-65 según el DTP; Grau a los 51 minutos,
  con los cambios.

**Qué se propone redactar** (44 (f), con la misma forma que la línea de
`VENTAJA-INESPERADA` en la 44 (b)):

- **No son motivo por sí solos para «sostiene el punto»:** que el empate le
  sirva, jugar de visita, el calendario o la fatiga, un DT nuevo o debutante,
  la cuenta de la llave. Dicen qué le conviene al equipo, no qué puede hacer su
  bloque.
- **Si el bloque es improvisado según el DTP**, la nota de «sostiene» dice
  cuándo vence su vida útil: es el minuto en que la rama deja de valer (Porto).
- El defecto y la regla del antecedente quedan como están.

**Qué NO se propone.** Ningún corte por minuto del empate (Getafe–Sevilla: «el
corte antes o después del 60' no sale de ninguna regla»).

**Calculable.** Ver «Para la app», punto 3: que la rama lleve el `fixtureId`
del antecedente y que el recibo avise un «sostiene» sin él.

### 2. Rama de ventaja: el defecto «sigue atacando» es de tres, y la falta de antecedente no elige (disciplina 44 (b)) — RÚBRICA

**Qué dice hoy.** «Administra» se escribe nombrando por qué. Para el favorito
por `μ_partido` con margen ≥ 0.30, el obligado de tabla y el que juega con
superioridad, el defecto es «sigue atacando». **No dice qué se escribe para los
demás.**

**Qué casos lo piden.** El hueco se llenó al revés: equipos que no eran ninguno
de los tres recibieron «sigue atacando» porque faltaba antecedente, y
administraron.

- Osasuna–Athletic (1570448:b): margen de μ 0,24, «sigue atacando por falta de
  antecedente»; Terzić cerró con tres cambios defensivos.
- La Louvière–Cercle (1558675:b): Cercle no favorito (0,98 contra 1,78) y «sigue
  presionando» por el anuncio de un DT debutante; con 1-0 al 6' cedió la pelota
  (38 %).
- U. Católica–U. de Chile (1505554:a): no favorito por μ; «local en el clásico,
  necesita el triunfo» no lo hace obligado de tabla, y administró.

Del otro lado, el que no es favorito y escribió «administra» **con motivo** lo
cumplió: Independiente Petrolero (1645534:b), Cagliari–Frosinone (1550188:a;
lo sostuvo el arquero), Levadiakos (1593348:a), PEC Zwolle (1552212:a) y
Mirassol (1492443:b). Y Excelsior–Go Ahead (1552218:b) escribió «en su plan,
sin echada declarada» y nombró el banco del rival: no prometió nada que no
tuviera.

Motivos que **sí** se nombraron para que un favorito administre, y valieron:
el objetivo ya cumplido (Gimnasia–Belgrano, 1493233:a: ya clasificado, `P1b` = 0),
el tercer partido en 8 días con `F2` = 1 del motor (Stuttgart–Werder,
1575214:a) y el plan del DT declarado en el DTP (Union–Köln, 1575207:a: la rama
decía «sigue atacando» con el repliegue en la p5 del DTP). Motivos que **no**
valieron: la posición en la tabla o el modelo del equipo, que es identidad
(Viseu–Rio Ave, 1575527:b; disciplina 6), y la frecuencia de visita con
`VENTAJA-INESPERADA` (América–Toluca, 1551026:b; ya prohibido).

**Qué se propone redactar** (44 (b)):

- **El defecto «sigue atacando» es solo de los tres** que nombra la regla.
  Para cualquier otro equipo, **la falta de antecedente no elige tipología**:
  la rama se escribe **«en su plan»** (la tipología de su base) y su riesgo es
  la línea del empate, que ya va escrita aparte (44 (a)).
- **Lista corta de motivos nombrables** para apartarse del defecto, con su
  fuente: el objetivo cumplido por la tabla (`P1b`), `F2` = 1 del motor y el
  plan del DT declarado en el DTP del mismo equipo. Son ejemplos de «nombrar por
  qué», no puntos ni pesos.
- **El anuncio de un DT, el clásico y la posición en la tabla no son motivo**
  para ninguna de las dos tipologías.

**Qué NO se propone.** Un defecto «administra» para el no favorito: cinco casos
a favor no son una medición, y la regla dice que administrar se nombra.

### 3. El antecedente coincide también en el marcador que se cuidaba y en la cuenta de jugadores (44 (b) y (f)) — RÚBRICA

**Qué dice hoy.** Tres coincidencias: condición, perfil del rival y piezas.
Desde la v0.1.25, que lo haya sostenido el bloque y que no haya terminado roto.

**Qué casos lo piden.** Siete partidos citaron un antecedente que coincidía en
las tres cosas pero cuidaba **otro marcador** u otra cuenta de jugadores:

- **Otro margen:** Fulham–Newcastle (1557461:b): una ventaja de un gol desde el
  80' apoyada en un 0-2. El banco del rival empató a los 3 minutos.
- **Sin ventaja que cuidar:** Viking–Sabah (1635745:b, el 4-4-1-1 ante Dortmund
  y el United) y Atlético Grau–Universitario (1549541:a, un 0-0 que además
  terminó roto). Las dos perdieron la ventaja en 16 y 11 minutos.
- **Una ventaja usada para sostener un empate, o al revés:** Boston
  River–Torque (1646901:a) y Antwerp–Lommel (1558671:b, «un empate al 90+6, que
  no es un empate sostenido»).
- **Otra cuenta de jugadores:** Estudiantes–Instituto (1493217:b, un 1-0 once
  contra once para un 3-0 con uno más) y Progreso–Defensor (1646900:b: una de
  las ventajas perdidas fue con uno menos desde el 61').

**Qué se propone redactar.** El antecedente coincide además en **el marcador
que se cuidaba** (ventaja de uno, ventaja de dos o empate) y en **la cuenta de
jugadores**. Vale para «administra», `ECHADA-PSI` y «sostiene el punto». Si
falla, la rama vuelve a su defecto, como hoy.

**Calculable.** El marcador y las rojas del antecedente están en la ficha
cuando el partido está en la base: el recibo puede mostrarlos al lado, con el
xG en contra y las atajadas que ya estaban aprobados (punto 3 de «Para la app»).

### 4. Con roja propia, el riesgo arranca con la roja (disciplina 16 y 44 (c) y (d)) — RÚBRICA, CORRIGE UN TEXTO DE LA v0.1.25

**Qué dice hoy.** La v0.1.25 escribió que con roja propia empatando antes del
descanso «el riesgo es la vía echada en el tramo final (ventana del reloj
75-90)». La 44 (c), en cambio, dice que **cada rama lleva su ventana relativa
al evento que la abre**: para `siExpulsion`, desde la roja.

**Qué casos lo piden.** 26 lecciones de 25 partidos tocan la roja. La cifra de
la v0.1.25 (concede casi siempre) se confirma; **el lugar donde la puso, no**:

- **Concedió a 15 minutos o menos de la roja:** Villarroel–Oruro (1645535:a, a
  los 5), Excelsior–Twente (1552213:a, roja al 5', gol al 12'), Hamburgo–Gladbach
  (1575218:b, a los 10 y 21, «en el 60-75, no en la ventana 75-90»), Nacional
  Potosí–Oriente (1645455:b, copa, a los 7), Aurora–Petrolero (1645454:b, copa,
  a los 6) y Kortrijk–Mechelen (1558657:a, roja ganando 1-0: a los 3 y 6).
- **Concedió más tarde pero antes del 75':** Parma–Bologna (1550194:a, roja al
  9', goles al 53' y 72') y Boca–River (1493214:b, roja al 10', gol a los 17).
- **Concedió en el 75-90 porque la roja llegó tarde:** Panetolikos–OFI
  (1593350:a, roja al 69', gol al 88') y Caracas–Puerto Cabello (1646933:a).
- **No concedió:** São Paulo–Corinthians (1492448:b, roja al 82'), Moquegua–Los
  Chankas (1549542:b, al 81'), Huachipato–La Serena (1505551:b, al 48', con el
  arquero) y Panathinaikos–AEK (1593349:a, ganando 2-0).

Y dos partes dejaron la ventana de la rama de expulsión **en la nota y no en su
campo**, así que el tramo no se pudo comprobar: Paderborn–Frankfurt
(1575220:a) y The Strongest–Always Ready (1645456:a, copa).

**Qué se propone redactar** (disciplina 16, línea de `siExpulsion.propia`):

- **La ventana de la rama de expulsión va desde la roja**: «desde la roja hasta
  +15», y el régimen de inferioridad hasta el final. Se quita la frase que
  ubica el riesgo en la ventana del reloj 75-90.
- La ventana del reloj se sigue declarando aparte y, con roja previa, sigue sin
  cobrarse (disciplinas 16 y 17).
- La línea sigue nombrando la vía propia (contra, pelota parada) y la vía del
  rival, que con uno más suele ser su banco (Atlante–Santos, 1551031:a;
  Cali–Chico, 1549846:a).

**Qué NO se propone.**

- Un número para el minuto de la concesión. Los minutos de arriba salen de la
  prosa de las lecciones; la medición es de la app (abajo).
- Condicionar el «ISE agravado» de la roja perdiendo a que el partido le
  importe al equipo (Unión–Vélez, 1493241:b: ya clasificado, no compró riesgo).
  Es un caso.

**Calculable.** Los tramos del veredicto ya traen `rojaPropia`, el estado y la
concesión. La app puede contar los minutos entre la roja y el primer gol
concedido, por marcador y por minuto de la roja, y sumarlo a la referencia de
concesión tras roja que la v0.1.25 dejó aprobada para `GET …/tde/{id}`.

### 5. El banco se nombra de la hoja (disciplinas 66, 65 y 44 (a)) — RÚBRICA + CALCULABLE

**Qué dice hoy.** La rama de ventaja nombra el banco ofensivo del rival que
persigue; el banco propio como hecho de `rescata` va condicionado a los
cambios y al reloj. No dice de dónde sale la lista.

**Qué casos lo piden.** La regla de la v0.1.25 funciona: muchas lecciones dicen
que la ventaja se cayó por el suplente que la rama nombraba (Torino–Lecce
1550195:a, Mushuc Runa–Manta 1639831:b, Paranaense–Vasco 1492440:a, AEK–Real
Madrid 1635606:a, Fenerbahçe–Liverpool 1635658:b). Lo que falla es **la lista**:

- **Nombró como banco a un titular** (ocho partidos, y uno al revés): Monagas–Táchira
  (1646932:a), Always Ready–ABB (1645536:a), Arsenal–Hull (1557457:a, **aun
  después de rehacer con el once oficial**), Venezia–Udinese (1550196:a),
  Táchira–Puerto Cabello (1646929:a), Manchester United–Roma (1635695:b),
  2 de Mayo–Trinidense (1632050:a) y The Strongest–Villarroel (1645530:a). Y al
  revés, Cobresal–Everton (1505547:a): un titular habitual rotado al banco que
  la lista no nombró.
- **No nombró el banco del rival y por ahí llegó el gol:** Union–Köln
  (1575207:a), Cercle–Antwerp (1558664:a), Viseu–Rio Ave (1575527:b),
  Kasımpaşa–Beşiktaş (1584453:b) y U. Católica–Aucas (1639802:a, 01/11).
- **Lo nombró en una rama y entró en otra:** Mushuc Runa–Manta (1639831:a).

**Qué se propone redactar.**

- **El banco se toma de la hoja.** Antes del once oficial, la lista es
  «probable» y se escribe así; con el once, **se reescribe en el modo
  `rehacer`** con los suplentes reales. Un nombre que sale titular deja de ser
  banco.
- **El banco del rival se nombra en todas las ramas donde puede entrar**, no
  solo en `siMarcaPrimero`.

**Calculable.** Ver «Para la app», punto 2: la lista del banco sale de
`substitutes` de la ficha, y el cruce con lo escrito usa `identidad.py`.

### 6. La pieza que sostiene el seguro de atrás: cuando sale, el cierre lo dice (disciplinas 63 y 61) — RÚBRICA

**Qué dice hoy.** `SOB2` es el seguro de atrás; en las ramas del que persigue
hereda el nivel «persiguiendo» del DTP (disciplina 63). No pide nombrar quién
lo sostiene ni dice qué pasa si esa pieza sale.

**Qué casos lo piden.** Diez partidos en los que la concesión o el cambio de
mecanismo vino **cuando salió la pieza del seguro**:

- Nacional–Sportivo San Lorenzo (1632053:a): al descanso salió Santacruz, «el
  único seguro que la propia rama nombraba», y la contra del 71' llegó con el
  seguro en cero.
- San Lorenzo–Platense (1493238:a): salió Río, la pieza del doble cinco, y a los
  7 minutos llegó el 0-2.
- ADO–Sparta (1552220:b): Sparta igualó al 50', sacó a su contenedor Mito al 56'
  y concedió al 57'.
- Westerlo–Charleroi (1558679:a): salió el contenedor Fofana por un delantero, y
  concedió tres veces.
- Lommel–Gent (1558667:b): los dos centrales cambiados por ofensivos al 85',
  gol a los cinco minutos.
- Boston River–Torque (1646901:a): salió Vázquez al 81' y concedió al 85'.
- Bodø/Glimt–Lille (1635640:b): con 0-0 al 70' salió el contenedor Kjærgaard
  por un 9, sin rama que cubriera esa exposición.
- 2 de Mayo–Trinidense (1632050:b): Gauto, el seguro fijo, salió al 75'.
- Lazio–Cagliari (1550183:b): la vía que reabría la rama dependía de dos piezas
  que salieron antes del descanso.
- Gaziantep–Kasımpaşa (1584462:a): el seguro nombraba a Gidado y arrancó en el
  banco (es el caso del punto 5: se revisa con el once).

**Qué se propone redactar** (disciplina 63):

- La rama que persigue —y la base `SOB`— **nombra la pieza que sostiene
  `sob2`**, como ya nombra las piezas de la vía.
- **El cierre anota el minuto en que esa pieza salió** y lee el tramo desde ahí
  con el seguro roto. Es lectura del mecanismo: **no recalcula el ISE de rama
  declarado ni cambia el cobro** de la salida (disciplina 61).

**Qué NO se propone.** Subir `sob2` en la rama por anticipado porque la pieza
«podría salir». Sería estimar un cambio que todavía no pasó.

**Calculable.** Con la pieza nombrada, los cambios están en los eventos de la
ficha: la app puede marcar en el tramo el minuto en que salió (punto 4 de «Para
la app»).

### 7. `S1` mira a los titulares que van al choque (bloque S) — RÚBRICA, SIN PESO

**Qué casos lo piden.** 5 lecciones.

- Huachipato–La Serena (1505551:b): `S1` = 0,5 se apoyó en las amarillas de
  suplentes, y la roja que reordenó el partido fue del punta titular.
- Boca–River (1493214:b): Martínez Quarta volvía de una suspensión por roja,
  `S1` quedó en 0,5 y la roja llegó al 10'.
- Hamburgo–Gladbach (1575218:b): `S1` sin dato, y la roja fue de un central con
  su tercera expulsión temprana en la Bundesliga según la prensa.
- Strasbourg–Auxerre (1552808:b): la roja fue de un suplente con 11 minutos en
  cancha. `S1` no tiene casillero para el que entra (hueco ya declarado).
- Metropolitanos–Carabobo (1646931:a): conducta violenta, otro caso para el
  candidato de la v0.1.12.

**Qué se propone redactar.** `S1` se puntúa sobre **los titulares del once que
van al choque** (zaga, pivote, el 9 que pelea), y cuenta a quien **vuelve de
una roja**. El suplente sigue siendo un hueco declarado.

**Qué NO se propone.** Tocar el peso de `S1` ni sumar la conducta violenta como
indicador: 5 lecciones, ninguna medición en positivos (disciplina 22).

### 8. F2 subido a mano por viaje y altitud: una contradicción para que decida el usuario (disciplina 21 y fila F2 de `INDICE_IE.md`) — A DECIDIR

**Qué hay.** La disciplina 21 dice «F2 es dato del motor o no es dato». La
tabla de `references/INDICE_IE.md` pone en F2 «viaje con cambio de altitud» y
«altura/calor extremo», que el motor no conoce. Y la app, en
`GET …/tde/{id}` (`f2.puedeSubir`), dice: viaje largo, altitud, calor o un
próximo de altísima exigencia que la base no reconoce «son parte de la rúbrica
F2: si los hay, súbelo a mano».

**Qué casos.** Dos partes lo subieron a mano y los dos cierres dicen que no
debía hacerse: Libertad–Emelec (1639859:b: F2 = 1 por ocho horas de viaje y
la altura de Loja, rama `ECHADA-FIS`; Emelec siguió atacando) y Pasto–Jaguares
(1549847:b: «la carga del viaje va en la nota, no en el indicador»). Son dos
partidos: no alcanza para una regla, pero el texto se contradice solo.

**Dos salidas (no mueven pesos; cambian de dónde sale F2 cuando hay viaje):**

- **(a) Manda el motor:** el IE se emite con el piso de F2 de la app y el viaje
  o la altitud van a la caja de sensibilidad como el otro extremo, con su
  fuente. Es la disciplina 21 al pie de la letra y la caja que ya existe. La
  app cambia el texto de `puedeSubir`.
- **(b) Manda la tabla:** se puede subir con fuente nombrada, y los dos cierres
  de arriba se archivan como desacuerdo.

La propuesta recomienda la (a), porque F2 es del bloque de peso ×3 y la
disciplina 21 nació de tres correcciones del motor sobre estimaciones a mano.
El candidato `F2 × F4` de la v0.1.15 sigue como está.

### 9. Confirmaciones que se cierran sin cambio

Se cierran con la v0.1.26 sin texto nuevo:

- **Desenlace `abierto` por defecto (disciplina 65).** Es el grupo más grande:
  unas 110 lecciones, casi todas dicen que `abierto` fue la lectura correcta y
  que el viejo `se_rompe` por ISE ≥ 7 habría fallado (Göztepe–Başakşehir
  1584463:b, Slavia–Arsenal 1635726:a, Manchester United–Roma 1635695:a,
  Kasımpaşa–Beşiktaş 1584453:a, Cobresal–Everton 1505547:b). Lo que el dossier
  mide en `desenlaceTde` va en «Lo medido que no entra».
- **El hecho de la v0.1.25.** El banco condicionado al reloj y a los cambios
  se cumplió en los dos sentidos (Fenerbahçe–Liverpool 1635658:b, Monagas–Caracas
  1646928:a, Cusco–Sport Boys 1549540:a, Torino–Lecce 1550195:b,
  Union–Köln 1575207:b). El perfil de temporada como hecho volvió a fallar
  (Always Ready–ABB 1645536:a y b, «concede 2+ por partido»), y el calendario
  como hecho también (Paranaense–Vasco, cuarentena). La regla ya los excluye.
- **Revisar la rama con el once oficial (modo `rehacer`).** Gaziantep–Kasımpaşa
  (1584462:a), 2 de Mayo–Trinidense (1632050:a), U. Católica–Aucas (1639802:a)
  y Leipzig–Augsburg (1575213:b): ya está en la 65.
- **Vía del gol con fuente (disciplina 61).** Unas 30 lecciones dicen «sin
  crónica, el gol queda en la vía escrita», y las que tenían fuente la usaron
  (Torino–Lecce 1550195:a, desvío; Metropolitanos–Carabobo 1646931:a, pelota
  parada; Danubio–Nacional 1646902:b y Famalicão–Arouca 1575539:b, error
  individual).
- **Referencia del minuto leída completa (disciplina 66).** Confirmada en las
  dos ventajas: «no pierde nueve de cada diez, pero no gana uno de cada cuatro»
  (St. Truiden–Leuven 1558669:a, Chicó–Inter 1549856:b, Osasuna–Athletic
  1570448:b, Fulham–Newcastle 1557461:b).
- **Configuración dual (disciplina 43):** 21 lecciones de 20 partidos,
  ninguna echada en un dual. Siguen siendo ausencias, no positivos.
- **Superioridad que no administra (disciplina 16):** confirmada en una
  veintena de partidos (Boca–River 1493214:a, Braga–Famalicão 1575530:a,
  Viking–Sabah 1635745:a, Hamburgo–Gladbach 1575218:a). Dos partes la
  escribieron al revés sin motivo (PAOK–Asteras, cuarentena; Cali–Chico
  1549846:b): la regla ya lo prohíbe.
- **Interacción entre vías (disciplina 14):** el ISE no se paga cuando el rival
  no ataca (Millonarios–América 1549851:a, Aldosivi–River 1493227:b,
  Internacional–Coritiba 1492446:a, Bolívar–Real Potosí 1645457:a, copa).
- **Casilla del añadido, los dos tiempos (disciplina 23):** 12 lecciones, todas
  confirmaciones.
- **Relevancia baja (disciplina 50):** 9 lecciones; dos partidos llegaron vivos
  al final (Lommel–Gent 1558667:a, Famalicão–Arouca 1575539:a). La regla ya
  dice que lo útil son las ramas, y eso se cumplió.

---

## Para la app, no para el skill

Va aparte del skill y se hace después de aprobar. Nada mueve un número
calibrado.

1. **Lo pendiente de la v0.1.25 sigue sin hacerse.** En el código no aparece
   `viaGol`, `porOtraVia`, quién persigue por `μ_partido` en los tramos, el
   banco del rival, la concesión tras roja, los insumos de `S1` en
   `GET …/tde/{id}`, `ARQUERO-NUEVO` ni `HERENCIA-DTP` en el `sob2` de rama
   (`PENDIENTES.md`). **El candidato del defecto por quién persigue no se puede
   medir** hasta que el veredicto guarde quién persigue: por eso no avanza en
   esta versión. Lo pide Viking–Sabah (1635745:b): «la app lo observa como
   se_rompe sin marcarlo porOtraVia».
2. **El banco desde la hoja (punto 5).** Con el once oficial, `GET …/tde/{id}`
   puede traer los `substitutes` de la ficha por lado, y el recibo puede avisar
   (tipo `dato`) cuando un nombre del banco escrito en una rama es titular,
   con el cruce de `backend/identidad.py`. Junto a eso, los cambios que le
   quedan a cada equipo al minuto de cada gol, desde los eventos, para el banco
   condicionado de la 65.
3. **El antecedente en la rama (puntos 1 y 3).** Que la rama acepte el
   `fixtureId` del antecedente (cambio de contrato: `docs/openapi.yaml`
   primero). Con él, el recibo muestra al lado el marcador que se cuidaba, la
   cuenta de jugadores, el xG en contra y las atajadas (esto último ya estaba
   aprobado), y avisa una `siIguala` o una rama de ventaja que se aparta del
   defecto sin antecedente.
4. **La pieza del seguro (punto 6).** Con la pieza nombrada en la rama, el
   veredicto marca en el tramo el minuto en que salió, desde los cambios de la
   ficha.
5. **Roja y concesión (punto 4).** Contar los minutos entre la roja propia y el
   primer gol concedido, por marcador y minuto de la roja, desde los tramos que
   ya existen; sumarlo a la referencia aprobada. Y avisar en el recibo una rama
   con tipología pero sin `ventana` (Paderborn, The Strongest).
6. **Coherencia con el DTP.** Union–Köln (1575207:a) escribió «sigue atacando»
   con el repliegue como plan del DT en la p5 de su propio DTP. Un caso:
   candidato a un aviso como `HERENCIA-DTP`, no regla.
7. **Textos viejos.** `backend/analisis/lecciones.py` (la nota de
   `desenlaceTde`) todavía dice «Lectura por defecto: ISE de rama ≥ 7 →
   se_rompe», y el rechazo de `desenlace` en `backend/analisis/parte.py` cita
   «TDE v0.1.24». El cobro ya usa `abierto`; solo la prosa quedó vieja.
8. **F2 (punto 8).** Si el usuario elige la salida (a), cambiar el texto de
   `f2.puedeSubir` en `backend/analisis/tde.py`.
9. **La versión del 01/11.** Anotar en `SUBIDA_VERSION` la hora en que la
   v0.1.25 llegó a la cuenta, para separar las lecciones del 01/11 escritas con
   la v0.1.24 (hoy el dossier no lo hace por lección).

## Lo medido que no entra

- **`rescata` con hecho.** `desenlaceTde` da `rescata` cumplido **15 de 22**
  (68 %, IC 47-84); en los 332 tramos `abierto` lo observado fue `rescata` 131
  (39 %, IC 34-45). Sugiere que el hecho de hoy elige bien, pero n = 22 está
  por debajo de los 30 por lectura que pide la 65, y quien escribe `rescata`
  suele ser el favorito (selección). No mueve nada.
- **`se_rompe`.** Cumplido **45 de 95** (47 %, IC 38-57), contra `se_rompe`
  observado en 144 de 332 tramos `abierto` (43 %, IC 38-49): sigue sin separar.
  Casi todos esos 95 son del defecto viejo de la v0.1.24; la serie es de toda la
  cohorte y no se puede partir por versión desde el dossier.
- **Ventanas.** `ventanaTde`: 93 ventanas con gol de 597 comprobadas (16 %); la
  ventana base del reloj, 80 de 359 (22 %). Es la serie del sesgo tardío y
  ninguna lección pide tocarla.

## Lo que NO se propone y por qué

- **Aplicar el defecto por quién persigue.** Esta semana hay lecciones en las
  dos direcciones: a favor Westerlo–Charleroi (1558679:a) y Paris FC–Monaco
  (1552807:b); en contra Nottingham Forest–City (1557465:b, el favorito por μ
  con margen 0,80 concedió persiguiendo), Progreso–Defensor (1646900:a) e
  Independiente Petrolero–Tomayapo (1645534:a). Sin la medición con
  `μ_partido` (punto 1 de la app), sigue candidato.
- **El «doble golpe» como salida.** Seis partidos más (Leipzig–Augsburg
  1575213:b, Villarreal–PSG 1635746:a, Galatasaray–Stuttgart 1635669:b,
  Pereira–Tolima 1549852:a, IDV–LDU 1639800:b, Paranaense–Vasco 1492440:a, este
  en cuarentena). Sigue sin medirse qué pasa después, y el corte en minutos
  sería inventado.
- **La ventaja de dos.** Cinco partidos perdieron o vieron descontar una ventaja
  de dos (Kasımpaşa–Beşiktaş 1584453:b, Cobresal–Everton 1505547:a,
  Sittard–Telstar 1552217:a, Universitario–Sport Boys 1549535:b,
  Gimnasia–Belgrano 1493233:a). Es el candidato «C3 desdoblado por magnitud» de
  la v0.1.15. `ventajaPorMinuto` no se parte por margen; primero tiene que
  hacerlo la app.
- **Un umbral de atajadas o de xG** para «lo sostuvo el arquero» (Cagliari,
  Galatasaray, Marseille, Universitario, Cusco): se dice con el dato a la vista.
- **Una tipología nueva** para la pérdida en salida bajo presión
  (Slavia–Arsenal, 1635726:a): es un caso.
- **El objetivo puntuado una vez para todas las ramas** (Danubio–Nacional,
  1646902:a: dos ramas del mismo equipo se contradijeron sobre si el empate le
  servía). Ya lo dice la disciplina 18.

## Cuándo se reabre

- **El defecto por quién persigue:** cuando el veredicto guarde quién persigue
  por `μ_partido` y haya n ≥ 30 tramos por lado (la regla de la v0.1.25).
- **El doble golpe y la ventaja de dos:** cuando la app los mida desde los
  tramos (minutos entre goles; `ventajaPorMinuto` por margen).
- **La roja propia:** cuando la app dé los minutos entre roja y concesión. Si
  separan por minuto de la roja, la referencia se cita con esa columna.
- **«Sostiene el punto» y la rama de ventaja (puntos 1 y 2):** si con la
  redacción y el aviso del recibo se siguen escribiendo sin motivo en la
  próxima cohorte, el problema es de lectura del skill y no de regla.
- **F2:** con la decisión del usuario sobre el punto 8.

## Sesgos y límites

- **Conteos, no tasas.** Quien cierra el caso nombra el skill sobre todo cuando
  algo falla (`sesgoDeAtribucion`). Los «13 de 17» del punto 1 y los «ocho
  partidos» del punto 5 son lecciones que lo dicen, no frecuencias.
- **La versión del 01/11.** 234 de las 638 lecciones son del 01/11 y parte de
  ese día corrió con la v0.1.24. Las causas de los puntos 1, 2, 3 y 5 aparecen
  también del 03 al 07/11; los incumplimientos de la v0.1.25 que solo aparecen
  el 01/11 (copiar la referencia del 31' con ventaja temprana: U. Católica–Aucas
  1639802:a, Estudiantes–Instituto 1493217:b) no se cuentan como causa nueva.
- **Sin veredictos bajados.** Esta revisión no midió tramos propios; los
  minutos del punto 4 y los cambios del punto 6 salen de la prosa de las
  lecciones.
- **Copa y cuarentena.** Las 17 de copa (Bolivia) y las 11 en cuarentena que
  enseña aparecen como casos de rúbrica y no sostienen nada.

## Resumen

| # | Punto | Disciplina | Tipo | Partidos que lo piden |
|---|---|---|---|---|
| 1 | «Sostiene el punto»: qué NO es motivo; la vida útil del bloque improvisado | 44 (f) | rúbrica + aviso calculable | 17 (13 sin motivo válido) |
| 2 | El defecto «sigue atacando» es de tres; los demás, «en su plan»; motivos nombrables | 44 (b) | rúbrica | ~12 |
| 3 | El antecedente coincide en el marcador que se cuidaba y en la cuenta de jugadores | 44 (b), (f) | rúbrica + calculable | 7 |
| 4 | Con roja propia la ventana va desde la roja, no del 75-90 | 16, 44 (c)-(d) | rúbrica, corrige v0.1.25 + calculable | 25 |
| 5 | El banco se toma de la hoja y se nombra en todas las ramas | 66, 65, 44 (a) | rúbrica + aviso calculable | 15 |
| 6 | La pieza del seguro se nombra y el cierre anota cuándo salió | 63, 61 | rúbrica + calculable | 10 |
| 7 | `S1` sobre los titulares que van al choque y quien vuelve de una roja | bloque S | rúbrica, sin peso | 5 |
| 8 | F2 a mano por viaje y altitud: decide el usuario | 21, `INDICE_IE.md` | a decidir | 2 |
| 9 | Confirmaciones sin cambio (65, 61, 66, 43, 16, 14, 23, 50) | varias | cierre sin texto | el resto |

**Ningún peso, umbral, compuerta, banda ni ventana por defecto se mueve.** La
única frase que se retira es de la v0.1.25 (la roja propia ubicada en el
75-90) y se reemplaza por lo que ya decía la 44 (c).
