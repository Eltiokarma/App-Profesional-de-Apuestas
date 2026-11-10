# Propuesta de revisión · `teorema-del-echado` v0.1.25 → v0.1.26

**Estado:** PROPUESTA **DECIDIDA por el usuario el 10/11/2026** (ver
«Decisiones del 10/11» y «Lista para redactar»), todavía sin redactar en el
skill. No se tocó el skill, ni el código, ni el estado de ninguna lección.
**Actualizada el
10/11/2026** con el dossier generado el 10/11 a las 02:13 UTC (865 lecciones
pendientes, 227 de ellas de partidos del 08 y 09/11): los puntos 1 a 9 se
conservan con su número y llevan sus «Refuerzo 10/11» / «En contra 10/11»; lo
nuevo va del punto 10 al 14. El 14 es la incidencia 1056 y la **decidió el
usuario** (opción a). Cada punto lleva su línea de comprobación («Se sostiene si… / Lo
tumba si…») para los ~50 veredictos del 08-09/11 que todavía se estaban
cerrando cuando se cortó el dossier, y su marca de núcleo o historial.

**Comprobada el 10/11/2026** con el segundo corte (04:29 UTC): las **103
lecciones** que no estaban en el dossier de las 02:13. Cada punto lleva su
«Comprobación 10/11». Ninguna tumba nada; el 1, el 2, el 5 y el 6 traen un
matiz, el 10 sigue a medir y el 11 y el 13 quedan sin casos. **El punto 14 lo APROBÓ el usuario el
10/11/2026 con la opción (a)** («heredar y avisar», sin recalcular partes
viejos): falta la app (la implementa el mantenimiento), la línea del skill DTP
y `DEUDA.md`. Se agrega el **punto 15** («sigue atacando» se lee por la
amenaza, no por la pelota; tres casos) y los candidatos de un caso van a «Lo
que NO se propone». Al final, la «Tabla de cambios».

Se redactó el 08/11/2026 desde:

- el dossier (`GET /analisis/cowork/revision/teorema-del-echado`, generado el
  08/11 a las 02:31, versión vigente `v0.1.25`, cohorte `c3-2026-09-23`);
- el skill vigente (`docs/skills/teorema-del-echado/SKILL.md` y
  `references/`) y la propuesta anterior (`TDE_v0.1.25_propuesta.md`);
- lo que quedó pendiente de la app en `docs/revisiones/PENDIENTES.md`.

## Decisiones del 10/11

El usuario decidió el 10/11/2026, en conversación: la 1056 con la (a) y «lo
demás como recomiendas». Cada punto abierto se resolvió con la recomendación
que la propia propuesta escribía; donde no recomendaba nada, con lo
conservador (no aflojar una regla vigente, no mover números, lo que tiene 1-2
casos queda como candidato).

| Punto | Decisión | Efecto en el texto |
|---|---|---|
| 1-7, 15 (rúbrica) | Aprobados como los recomienda la propuesta | Entran al `SKILL.md` con el texto de «Lista para redactar» |
| 1, matiz `siLeEmpatan` | Candidato (un caso: Millonarios–Tolima) | Queda en «Candidatos de la comprobación» |
| 5, matices «banco entero» y «además de los titulares» | Candidatos (un caso cada uno: U. de Chile–Cobresal, U. Católica–Macará) | No entran a la línea del punto 5; van a candidatos |
| 6, extensión a la rama de ventaja | Candidato (dos casos: Barcelona–Atlético, Alianza Lima–Los Chankas) | La línea nombra la pieza en la rama que persigue y en la base `SOB`, no en la de ventaja |
| 8 · F2 a mano por viaje y altitud | **(a) manda el motor** (lo que la propuesta recomendaba) | Una línea en la disciplina 21, la fila F2 de `INDICE_IE.md` marcada y el texto de `f2.puedeSubir` (app); la (b) queda tachada como historia |
| 9 · confirmaciones | Se cierran sin texto | Nada |
| 10 · ventana desde el cambio | Medir primero (lo que recomendaba) | Candidato; la medición, a «Para la app» (10) |
| 11 · SOB de la hora con 0-0 y el empate útil | **Se espera: candidato** (la propuesta no recomendaba; dos casos, sin casos nuevos y con una tensión con el punto 1) | No entra; la línea de la 18 queda escrita como candidato |
| 12 · `S1` desde la base | App + una línea en el `S1` de la disciplina 16 (lo recomendado) | La línea entra junto a la del punto 7 |
| 13 · rama TDE contra plan DTP | Entra la línea de rúbrica (recomendada); **sin vigilancia por Jev por ahora** (no había recomendación: lo conservador es no abrir otra pregunta del guardrail con dos casos) | Una línea en la 44 (b); el aviso de Jev queda candidato |
| 14 · incidencia 1056 | **(a) heredar y avisar**, sin recalcular partes viejos (decisión expresa) | Línea de la 63 con la decisión; la app la implementa el mantenimiento; coordinada con el cambio 16 del DTP v1.8 |

## Lista para redactar

Verificado el 10/11/2026 contra el skill vigente
(`docs/skills/teorema-del-echado/SKILL.md`, v0.1.25, 768 líneas, y
`references/INDICE_IE.md`, 493 líneas). Cada ancla de abajo se buscó en el
archivo y aparece **una sola vez**. Las líneas son las del archivo vigente;
al insertar de arriba hacia abajo, se corren. Las disciplinas 44, 63 y 66 del
archivo están escritas sin tildes: el texto nuevo para ellas va igual.

| # | Entra | Dónde va (archivo vigente) | Texto nuevo listo | Caso nombrado | ¿Afloja algo vigente? | ¿Toca otro skill? |
|---|---|---|---|---|---|---|
| 1 | sí | `SKILL.md` 44 (f), línea 575, después de «que la pieza este disponible—.» | sí (T1) | Málaga–Racing, Getafe–Sevilla, Venezia–Udinese, Başakşehir–Samsunspor, Porto–Napoli | no: agrega lo que no es motivo; el defecto y el antecedente quedan | no (lee la vida útil del bloque del DTP, que ya existe) |
| 2 | sí | `SKILL.md` 44 (b), línea 567, sub-ítem nuevo antes de «El antecedente tiene que parecerse…» (línea 568) | sí (T2) | Osasuna–Athletic, La Louvière–Cercle, U. Católica–U. de Chile, Sunderland–Chelsea, Gent–Kortrijk | no: el defecto de los tres queda; llena el hueco de los demás | no |
| 3 | sí | `SKILL.md` 44 (b), línea 568 (reemplazo) + línea 570 (`ECHADA-PSI`) + línea 635 (65, «las tres coincidencias») | sí (T3) | Fulham–Newcastle, Viking–Sabah, Lille–Rennes, Estudiantes–Instituto, Estudiantes LP–Talleres | no: exige dos coincidencias más (endurece) | no |
| 4 | sí | `SKILL.md` 16, línea 510 (reemplazo de una frase) | sí (T4) | Villarroel–Oruro, Excelsior–Twente, Hamburgo–Gladbach, Kortrijk–Mechelen, Jaguares–Bucaramanga, Santa Clara–Gil Vicente | **corrige** un texto de la v0.1.25 (el 75-90): lo desmienten 8+ casos; la cifra 11 de 12 y el ISE anulado quedan | `sad-analysis` lee la vía de gol propia de la misma línea, que no cambia |
| 5 | sí | `SKILL.md` 66, línea 654, al final de «La rama de ventaja nombra el banco ofensivo…» | sí (T5) | Arsenal–Hull, Always Ready–ABB, Monagas–Táchira (y cinco más), Lens–Marseille | no | **sí:** EFE v1.10 cambio 10 (B5 por rol, `banco probable`) y `corrida-sad` modo `rehacer` (ver «Coherencia») |
| 6 | sí (sin la rama de ventaja) | `SKILL.md` 63, después de la línea 622 y antes de «La evidencia puede venir…» (línea 623) | sí (T6) | Nacional–Sportivo San Lorenzo, San Lorenzo–Platense, ADO–Sparta, Westerlo–Charleroi, León–Chivas | no: no recalcula ni cambia el cobro (61) | complementa el cambio 8 del DTP v1.8 (M3: quién queda atrás); no depende de él |
| 7 | sí | `SKILL.md` 16, párrafo de `S1` (línea 517), después de la primera oración | sí (T7) | Boca–River, Santa Clara–Gil Vicente, Huachipato–La Serena | no: el peso de `S1` no se toca | lee `f1/{id}` (EFE/app); ver 1068 en «Coherencia» |
| 8 | sí | `SKILL.md` 21, línea 525, al final; `references/INDICE_IE.md` línea 119 (fila F2) | sí (T8) | Libertad–Emelec, Pasto–Jaguares | no: endurece la 21 (no se sube a mano) | no; la app cambia `f2.puedeSubir` («Para la app» 8) |
| 9 | no (cierre sin texto) | — | — | — | — | — |
| 10 | no (medir primero; candidato) | — | — | Asteras–Kalamata, Elche–Betis | — | — |
| 11 | no (candidato, decidido el 10/11) | — | — | Atromitos–OFI, Levante–Celta | — | — |
| 12 | sí | `SKILL.md` 16, párrafo de `S1` (línea 517), reemplaza «Mientras falte, esa parte…» | sí (T12) | Gençlerbirliği–Beşiktaş | no | lee `f1/{id}`; la parte de la app va a «Para la app» 11 |
| 13 | sí | `SKILL.md` 44 (b), sub-ítem nuevo después de T15 (antes de «El antecedente tiene que parecerse…») | sí (T13) | Chivas–León, Union–Köln | no | lee el M3 y el veredicto por rama del DTP; el DTP no necesita cambio |
| 14 | sí | `SKILL.md` 63, línea 623 (reemplazo de una frase) | sí (T14) | Westerlo–Charleroi, Konyaspor–Galatasaray, Como–Inter | no: la regla es la de la v0.1.23; cambia solo «pendiente» por la decisión | **sí:** DTP v1.8 cambio 16 (lo tiene) y `DEUDA.md` (no lo tiene todavía) |
| 15 | sí | `SKILL.md` 44 (b), sub-ítem nuevo después de T2 | sí (T15) | Coquimbo–Audax, Independiente Medellín–Fortaleza, Tolima–Millonarios | no: aclara con qué se comprueba la tipología | no |
| — | sí (changelog) | `SKILL.md` línea 16, bloque nuevo `v0.1.26` arriba del de la v0.1.25 | sí (T0) | — | — | — |

**Entran al skill 12 cambios** (1-8 y 12-15), más el bloque del changelog. **Quedan fuera 3**: el 9
(cierre sin texto), el 10 (medir primero) y el 11 (candidato). Candidatos
nuevos del 10/11: cuatro de un caso y tres de dos (ver «Candidatos de la
comprobación»). A la app: 13 ítems (sección «Para la app»), de los que el 9 ya
está hecho.

### Los textos

**T0 · changelog (línea 16, arriba del bloque de la v0.1.25):**

> **v0.1.26 · <fecha de subida> — la rama nombra por que, con que y con quien. Revision desde los dossiers del 08 y del 10/11/2026 (865 lecciones `pendiente`, 236 partidos del 01 al 09/11, mas 103 del segundo corte), todas ciegas `PRE`. Ningun numero se mueve: ni pesos, ni la formula del IE, del ISE ni del ISE de rama, ni compuertas, ni bandas, ni la ventana por defecto. El semaforo del IE sigue bajo. Una frase de la v0.1.25 se corrige (la roja propia en el 75-90).**
>
> **Registro al cierre de esta version: 35 filas, 51 columnas, sin altas.** IDs: los mismos de la v0.1.20.
>
> - **44 (f):** lo que no es motivo para «sostiene el punto» y la vida util del bloque improvisado. **44 (b):** el defecto «sigue atacando» es solo de los tres; los demas, «en su plan»; motivos nombrables y los que no lo son; «sigue atacando» se lee por la amenaza; la rama y el DTP del mismo equipo dicen lo mismo o se nombra cual manda. **44 (b) y (f):** el antecedente coincide tambien en el marcador que se cuidaba y en la cuenta de jugadores.
> - **16:** la ventana de `siExpulsion.propia` va desde la roja y el regimen hasta el final (sale el 75-90); `S1` sobre los titulares que van al choque y con lo que la app ya trae. **21:** F2 no se sube a mano por viaje, altitud ni calor (decision del usuario del 10/11). **63:** se nombra la pieza del seguro; `HERENCIA-DTP` en el `sob2` de rama, decidido el 10/11 (incidencia 1056). **66:** el banco sale de la hoja y se nombra en todas las ramas.
> - **Candidatos, no aplicados:** la ventana desde el cambio ofensivo (medir primero), la SOB de la hora con 0-0 y el empate util, la pieza del seguro en la rama de ventaja, la lista del 44 (f) en `siLeEmpatan`. Propuesta aprobada: `docs/revisiones/TDE_v0.1.26_propuesta.md`.

**T1 · 44 (f), después de «que la pieza este disponible—.» (línea 575):**

> **No son motivo por si solos para «sostiene el punto» *(v0.1.26)*:** que el empate le sirva, jugar de visita, el calendario o la fatiga, un DT nuevo o debutante, ni la cuenta de la llave. Dicen que le conviene al equipo, no que puede hacer su bloque (Malaga–Racing, «el punto fuera le sirve»; Getafe–Sevilla, el calendario; Venezia–Udinese y Basaksehir–Samsunspor, el DT nuevo; Estrela–Benfica y Vitoria–Porto, «la tabla no lo obliga a ganar», que es el empate que sirve). **Si el DTP declara el bloque improvisado**, la nota de «sostiene» dice cuando vence su vida util: desde ahi la rama deja de valer (Porto–Napoli, roto al 71' con vida util 55-65). Sin corte por minuto del empate.

**T2 · 44 (b), sub-ítem nuevo antes de «El antecedente tiene que parecerse…» (línea 568):**

> - **El defecto «sigue atacando» es solo de esos tres *(v0.1.26)*.** Para cualquier otro equipo **la falta de antecedente no elige tipologia**: la rama se escribe **«en su plan»** —la tipologia de su base— y su riesgo es la linea del empate, en su campo (a) (Osasuna–Athletic, margen de μ 0,24, y La Louviere–Cercle, «sigue atacando» por falta de antecedente, administraron; U. Catolica–U. de Chile: el clasico no hace obligado). **Motivos nombrables** para apartarse del defecto, con su fuente: el objetivo cumplido por la tabla (`P1b`), `F2` = 1 del motor y el plan del DT declarado en el DTP del mismo equipo (Gimnasia–Belgrano, Stuttgart–Werder, Gent–Kortrijk, Union–Koln). Son ejemplos de nombrar por que, no puntos ni pesos, y `F2` = 1 es nombrable, no un defecto que se aplica solo (Freiburg–Union siguio atacando con `F2` = 1). **No son motivo** para ninguna de las dos tipologias el anuncio de un DT, el clasico, la posicion en la tabla ni la racha (Viseu–Rio Ave; Sunderland–Chelsea, «siete sin ganar»).

**T15 · 44 (b), sub-ítem nuevo después de T2:**

> - **«Sigue atacando» describe la amenaza, no la pelota *(v0.1.26)*.** Se comprueba por remates y llegadas al area. La posesion de temporada y el modelo del equipo no son motivo para escribirlo (disciplina 6). El que cede la pelota y sigue llegando cumple la rama; el que cede y deja de llegar administro, y el cierre lo dice (Coquimbo–Audax: «sigue atacando con la pelota» por la posesion de temporada, se quedo con el 36 % y cerro con un defensor; Independiente Medellin–Fortaleza: con el 38 % siguio llegando, 12 remates, y amplio; Tolima–Millonarios). Sin umbral de posesion ni de remates: no hay datos por tramo.

**T13 · 44 (b), sub-ítem nuevo después de T15:**

> - **La rama y el DTP del mismo equipo dicen lo mismo *(v0.1.26)*.** Si el M3 o el veredicto por rama del DTP del mismo equipo dicen otra cosa que la tipologia de la rama, la nota nombra cual manda y por que; sin motivo, manda el plan del DT del DTP, que es el que tiene la fuente (Chivas–Leon: la rama decia «no administra», el M3 pedia doble pivote fijo si iba arriba, entro un defensor al 84' y concedio a los 3 minutos; Union–Koln: «sigue atacando» con el repliegue en la p5 del DTP). Es la herencia de `C1` y `SOB2` llevada a la tipologia, sin numero y sin alerta calculada.

**T3 · 44 (b), línea 568, reemplazo.** Donde dice «Un antecedente sostiene «administra» solo si coincide en tres cosas: **la misma condicion** (local o visita), **un rival del mismo perfil** (que tambien queria la pelota, obligado o superior) y **las mismas piezas** (las que lo sostuvieron estan disponibles hoy).», va:

> Un antecedente sostiene «administra» solo si coincide en cinco cosas: **la misma condicion** (local o visita), **un rival del mismo perfil** (que tambien queria la pelota, obligado o superior), **las mismas piezas** (las que lo sostuvieron estan disponibles hoy) y, desde la v0.1.26, **el mismo marcador que se cuidaba** (ventaja de uno, ventaja de dos o empate) y **la misma cuenta de jugadores** (Fulham–Newcastle: un 0-2 para cuidar un gol desde el 80'; Viking–Sabah, Atletico Grau–Universitario y Lille–Rennes: un 0-0 para cuidar una ventaja; Estudiantes–Instituto: un 1-0 once contra once para un 3-0 con uno mas; Estudiantes LP–Talleres: un 0-0 con uno menos). Vale igual para `ECHADA-PSI` y para «sostiene el punto» de (f).

Y en la línea 570, «coinciden en condicion, perfil del rival y piezas» pasa a «coinciden en las cinco cosas de arriba»; en la línea 635 (65), «ni un antecedente que no cumpla las tres coincidencias de la 44 (b)» pasa a «ni un antecedente que no cumpla las coincidencias de la 44 (b)».

**T4 · 16, línea 510, reemplazo.** Donde dice «La línea de `siExpulsion.propia` dice que el riesgo es **la vía echada en el tramo final** (ventana del reloj 75-90) y que el ISE anulado no la apaga», va:

> La línea de `siExpulsion.propia` lleva su ventana **desde la roja hasta +15** y el régimen de inferioridad **hasta el final**, y dice que el ISE anulado no apaga la vía echada *(v0.1.26: la v0.1.25 la ubicaba en la ventana del reloj 75-90, que es la 44 (c) incumplida; en la cohorte de noviembre concedieron a 15 minutos o menos de la roja Villarroel–Oruro, Excelsior–Twente, Hamburgo–Gladbach, Kortrijk–Mechelen y Jaguares–Bucaramanga, y dentro del régimen pero fuera del +15 Santa Clara–Gil Vicente e Independiente Rivadavia–Gimnasia: por eso el régimen no se corta en +15)*. La ventana del reloj se sigue declarando aparte y, con roja previa, no se cobra (disciplinas 16 y 17)

(los casos de la v0.1.25 entre paréntesis que siguen, Melgar–Comerciantes, Delfín–Cuenca y Barracas–Estudiantes, se conservan). Y en la 44 (d) no cambia nada: ya remite a la 16.

**T5 · 66, línea 654, al final del ítem «La rama de ventaja nombra el banco ofensivo…» (después de «hasta entonces sale de la investigacion, con fuente.»):**

> **La lista sale de la hoja *(v0.1.26)*.** Antes del once oficial es «probable» y se escribe asi (si el EFE trae el banco por rol en B5, es esa lista); con el once, se reescribe en el modo `rehacer` con los suplentes reales, y **un nombre que sale titular deja de ser banco** (ocho partes nombraron como banco a un titular: Monagas–Tachira, Always Ready–ABB, Arsenal–Hull aun despues de rehacer, Venezia–Udinese, Tachira–Puerto Cabello, Manchester United–Roma, 2 de Mayo–Trinidense, The Strongest–Villarroel). **Se nombra en todas las ramas donde puede entrar**, no solo en `siMarcaPrimero` (Lens–Marseille: el banco de la rama de ventaja rompio el empate en `siIguala`; Mushuc Runa–Manta; y el que no lo nombro lo pago: Union–Koln, Cercle–Antwerp, Estudiantes LP–Talleres).

**T6 · 63, sub-ítem nuevo entre la línea 622 y «La evidencia puede venir…» (línea 623):**

> - **La pieza que sostiene el seguro se nombra *(v0.1.26)*.** La rama que persigue —y la base `SOB`— nombra quien sostiene su `sob2`, como ya nombra las piezas de la via. **El cierre anota el minuto en que esa pieza salio, por cambio o por roja**, y lee el tramo desde ahi con el seguro roto. Es lectura del mecanismo: no recalcula el ISE de rama declarado ni cambia el cobro de la salida (disciplina 61), y el `sob2` no se sube por anticipado porque la pieza «podria salir». Casos: Nacional–Sportivo San Lorenzo (Santacruz, «el unico seguro que la rama nombraba», salio al descanso), San Lorenzo–Platense, ADO–Sparta (Mito al 56', gol al 57'), Westerlo–Charleroi (Fofana por un delantero), Boston River–Torque, Lommel–Gent, Leon–Chivas (la roja de J. Rodriguez, pieza del doble pivote).

**T14 · 63, línea 623, reemplazo.** Donde dice «que `HERENCIA-DTP` compare tambien el `sob2` de la rama que persigue, no solo el de la base, esta aprobado y pendiente de la app.», va:

> que `HERENCIA-DTP` compare tambien el `sob2` de las tres ramas que persiguen, no solo el de la base, lo decidio el usuario el 10/11/2026 (incidencia 1056, «heredar y avisar»): la app toma el nivel persiguiendo del DTP para `siRecibePrimero`, `siIguala` y `siLeEmpatan` cuando vuelve a empujar (`sob1` ≥ 0.5) y avisa si el declarado difiere; los partes depositados antes se leen como se declararon. Mientras la app no lo haga, lo copia el analista *(cuando el mantenimiento lo implemente, esta ultima oracion se borra)*. Casos que lo hicieron bien a mano: Westerlo–Charleroi, Konyaspor–Galatasaray, Como–Inter.

**T7 · 16, párrafo de `S1` (línea 517), después de la primera oración («…no se estiman *(v0.1.25)*.**»):**

> *(v0.1.26)* **`S1` se puntua sobre los titulares del once que van al choque** —zaga, pivote, el 9 que pelea— y cuenta a quien **vuelve de una roja**; nombra a toda la linea, no a un candidato (Boca–River: Martinez Quarta volvia de una suspension por roja y la vio al 10'; Santa Clara–Gil Vicente: el riesgo se nombro en uno y la vio otro; Huachipato–La Serena: las amarillas eran de suplentes y la roja fue del punta titular). El suplente que entra sigue siendo un hueco declarado (Strasbourg–Auxerre, Orense–Cuenca).

**T12 · 16, párrafo de `S1` (línea 517), reemplazo.** Donde dice «Mientras falte, esa parte de `S1` se declara `sin dato` y entra en la caja de sensibilidad; no se rellena a ojo.», va:

> Mientras falte, esa parte de `S1` se declara `sin dato` y entra en la caja de sensibilidad; no se rellena a ojo. **Lo que la app ya trae no se deja vacio *(v0.1.26)*:** con `amarillasEnLaCompeticion` y `sancionados` de `f1/{id}` a la vista, `S1` se puntua con ellos o se declara `sin dato` con el motivo que da la app (`conteoParcial`, jugador sin fila o sin datos de la temporada); no se puntua de memoria (Gençlerbirliği–Beşiktaş: `S1` sin dato y un central de la zaga nueva vio dos amarillas en cinco minutos, con el dato en `f1/{id}`; Nacional Potosí–Real Potosí: `S1` = 1 por las rojas de la base, y acertó).

**T8 · 21, línea 525, al final; y fila F2 de `INDICE_IE.md`, línea 119.** En la 21, después de «porque el número finge precisión.»:

> **El viaje, la altitud y el calor no suben F2 a mano *(v0.1.26, decisión del usuario del 10/11/2026)*.** El IE se emite con el `F2` de la app (`GET …/tde/{id}` → `f2`) y, si hay un viaje largo, un cambio de altitud o calor extremo que el motor no ve, va a la **caja de sensibilidad** como el otro extremo, con su fuente (disciplina 32). Libertad–Emelec subió F2 a 1 por ocho horas de viaje y la altura de Loja, escribió `ECHADA-FIS` y Emelec siguió atacando; Pasto–Jaguares: «la carga del viaje va en la nota, no en el indicador».

En `INDICE_IE.md`, la fila F2 queda (las tres celdas de puntaje, sin mover ningún número):

> `| F2 | Descanso, viaje y calendario | 6+ días, sin viaje exigente, próximo partido accesible | 4–5 días *(viaje con cambio de altitud: caja de sensibilidad, disciplina 21)* | ≤3 días, o próximo partido de altísima exigencia *(altura o calor extremo: caja de sensibilidad, disciplina 21)* |`

## Coherencia entre skills

| Cambio | Depende de | ¿Lo tiene la otra parte? | Qué hacer al redactar |
|---|---|---|---|
| 14 (1056, herencia del `sob2` de rama) | DTP `diagnostico-tactico` (M2 e Integración: «no se hereda hasta que el usuario decida») | **Sí:** `DTP_v1.8_propuesta.md`, cambio 16, con el texto nuevo de Integración («El TDE hereda `nivelFocoPersiguiendo` en las ramas del que persigue; HERENCIA-DTP avisa si difiere — aprobado 10/11, incidencia 1056») | Subir TDE v0.1.26 y DTP v1.8 juntos |
| 14 | `docs/DEUDA.md` (entrada DTP v1.6 / TDE v0.1.23, «pendiente del usuario») | **No todavía** | Cerrar esa línea con la decisión del 10/11 al redactar (no es un skill: no bloquea) |
| 14 | La app (`parte.py` `HEREDA_SOB2`, `_heredar`, `HERENCIA-DTP`; `dtp_cowork.herencia_tde`) | No: `HEREDA_SOB2 = ("siMarcaPrimero",)` sigue en `parte.py` línea 2475 | La redacción T14 deja «lo copia el analista» hasta que el mantenimiento lo implemente |
| 5 (banco de la hoja) | EFE v1.10 cambio 10 (la F1 admite `banco probable` y B5 nombra el banco por rol: «esa lista es la que toman el DTP, el TDE y la matriz») | **Sí**, en la misma dirección | T5 cita la lista del B5 condicionada («si el EFE trae el banco por rol»): no se rompe si el cambio 10 del EFE no entrara |
| 5 | `corrida-sad`, modo `rehacer`, paso 4 (reescribe todo lo que nombra al once viejo, `tde.bloques[]` con sus ramas incluido) | Sí en parte: saca de las ramas al titular nombrado como banco; no dice que se escriban los suplentes reales de la hoja. Y el `rehacer` corre solo con `DTP-REHACER` | No bloquea. Nota para el mantenimiento: el aviso del recibo («Para la app» 2) cubre los partes sin `rehacer` |
| 7 y 12 (`S1` desde `f1/{id}`) | 1068 (c): la app suma a la F1 la fila del titular que falta (`delOnceOficial`, rol ROT, **sin stats de temporada**) | La decisión está; el código no | Esa fila no trae amarillas de la competición: para `S1` es «sin datos de la temporada» (ya en T12), nunca 0. Sin conflicto con el rehacer con EFE (3+ titulares fijos o arquero distinto): el banco del TDE se reescribe en todo `rehacer` |
| 13 (rama contra M3) | DTP: el M3 y el veredicto por rama | Existen en el DTP vigente; el DTP v1.8 cambio 8 (M3: quién queda atrás en todas las ramas) los hace más explícitos | Nada: la regla es del lado del TDE |
| 6 (pieza del seguro) | DTP v1.8 cambio 8 | Complementa; no depende | Nada |
| 4 (roja) | `sad-analysis` lee la vía de gol propia de `siExpulsion.propia` | Esa parte no cambia | Nada |
| 11 (candidato) contra 1 | — | La tensión quedó resuelta: el 11 no entra | Nada |

**Bloqueos para redactar: ninguno.** Las secciones y líneas citadas existen;
no queda una contradicción abierta (la del 1 contra el 11 se resolvió dejando
el 11 como candidato); la única dependencia en otro skill (DTP, 1056) la tiene
su propuesta. Lo que falta fuera de los skills: `DEUDA.md` (14) y la app (14,
8, 12), que no impiden subir el texto.

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

**Actualización del 10/11/2026** (dossier generado el 10/11 a las 02:13 UTC,
versión vigente `v0.1.25`, cohorte `c3-2026-09-23`):

- **Ventana:** **865 lecciones** `pendiente`, de **236 partidos** del 01/11 al
  09/11 (432 aciertos, 191 parciales, 242 fallos). Las 638 de arriba siguen
  pendientes; las **nuevas son 227, de 67 partidos**: 213 del 08/11 y 14 del
  09/11 (Universitario–Moquegua, Alianza Valledupar–Llaneros, Querétaro–Puebla,
  León–Chivas). Todas de la v0.1.25, `ciega` + `PRE`, acreditan.
- **Veredictos de las 227:** 112 aciertos, 47 parciales y 68 fallos.
- **Población de las 227:** ninguna de copa nacional ni en cuarentena. En el
  total siguen las 17 de copa y las 11 de cuarentena que enseña del 08/11. Los
  cuatro casos que todavía no tienen la cuarentena que les corresponde (LDU
  1631509, Palmeiras 1492426, Manta 1639824 y 1639827) **no aparecen** en las
  lecciones del TDE: ningún punto se apoya en ellos.
- **Piden mover un número (Jev):** ninguna de las 865 trae
  `proponeMoverNumero: true` (141 `false`, 724 sin etiqueta). El dossier cuenta
  3 en `porModoFallo.pidenMoverNumero`, que no salen en la lista de pendientes
  (ver «Sesgos»). `lectura`: «837 lección(es) acreditable(s), pero ninguna pide
  mover un número».
- **Modo de fallo (Jev) de las 227:** 214 sin etiqueta, 9 `lectura_efe`, 4
  `tde`. En todo el dossier: 65 `lectura_efe`, 17 `tde`, 1 de cada uno de
  `insumo`, `reventon`, `imprevisto` y `varianza`, 159 sin etiqueta. Las 13
  etiquetadas de esta tanda no forman un grupo propio: caen en los puntos 2, 3,
  10 y 11.
- **Lo que se leyó:** la lección entera de los 115 fallos y parciales nuevos, y
  de los aciertos la regla que tocan y la lección de las que tocan las
  disciplinas 44 (b), 44 (f), 16, 18, 63, `S1` y las ventanas. Por regla (las
  etiquetas agrupadas por número de disciplina): 66 → 45 lecciones (21
  aciertos, 9 parciales, 15 fallos); 65 → 41 (23/7/11); 61 → 34 (20/7/7);
  44 (b) → 32 (20/5/7); 16 → 19 (10/4/5); 43 → 8; 44 (f) → 8; `S1` → 5 (y 2
  de la 16 que también lo nombran); 23 →
  5; 24 y 17 → 4 cada una; 50 → 3; 18 → 2; el resto, una.
- **Westerlo (incidencia 1056):** el caso está en las lecciones del 07/11
  (Westerlo–Charleroi, 1558679:a), no entre las nuevas. La incidencia en sí no
  está en el dossier y no se bajó (el encargo prohíbe llamar a la API): el
  punto 14 sale de la lección y del código.

**Segundo corte, comprobación del 10/11/2026** (04:29 UTC; solo las lecciones
pendientes que no estaban en el dossier de las 02:13):

- **103 lecciones de 29 partidos**, 64 con fecha del 07/11 y 39 del 08/11
  (Argentina, Chile, Perú, Colombia, Portugal y Bolivia): 51 aciertos, 20
  parciales y 32 fallos. Se leyeron todas, enteras.
- **Población:** ninguna de copa nacional. **3 en cuarentena que enseña** (Once
  Caldas–Águilas Doradas, 1549861: DT del parte distinto del que dirigió):
  fijan rúbrica y no sostienen nada. Los cuatro casos todavía sin la cuarentena
  que les toca (LDU 1631509, Palmeiras 1492426, Manta 1639824 y 1639827) no
  aparecen.
- **Piden mover un número (Jev):** ninguna (15 `false`, 88 sin etiqueta).
  **Modo de fallo:** 5 `lectura_efe` (Estudiantes LP, Coquimbo, U. de
  Concepción, Alianza Lima, Fortaleza), 98 sin etiqueta. Caen en los puntos 3,
  5, 9 y 15.
- Igual que antes: muchas «fallo» son el 1X2 y dicen «declarado y cumplido» o
  «confirmación». Los casos de cada comprobación son lecciones que lo dicen, no
  tasas.

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

Y una contradicción que **el usuario decidió el 10/11 con la (a)**: F2
subido a mano por viaje y altitud (punto 8) no se sube; manda el motor.

Casi todo lo nuevo se puede **avisar desde la app** en vez de pedírselo al
modelo, y lo pendiente de la v0.1.25 sigue sin hacerse (sección «Para la app»).

**Con el dossier del 10/11** los puntos 1, 2, 4, 6 y 7 suman casos a favor;
el 1 y el 3 tienen además uno en contra cada uno, a la vista en su punto.
Ninguno se cae. Se agregan:

10. La ventana de la vía del banco rival cuenta desde que el banco entra
    (medir primero).
11. Con 0-0 y el empate en la mano, la SOB de «si a la hora no gana, empuja»
    pide un hecho de hoy. Tiene una tensión con el punto 1. **Decidido el
    10/11: se espera (candidato).**
12. `S1` desde la base: las amarillas y las rojas que la app ya calcula (va a
    la app).
13. La rama del TDE y el plan del DTP del mismo equipo dicen lo mismo antes de
    depositar.
14. **Incidencia 1056 (APROBADO por el usuario el 10/11, opción a):** el
    `sob2` de las ramas del que persigue se hereda del `nivelFocoPersiguiendo` del DTP y `HERENCIA-DTP` lo
    compara. El skill ya lo dice desde la v0.1.23; lo que falta es que lo haga
    la app y que el DTP deje de decir «no se hereda hasta que el usuario
    decida».
15. «Sigue atacando» se lee por la amenaza, no por la pelota (nuevo en la
    comprobación del 10/11).

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

**Refuerzo 10/11.** Dos partes más, del 08/11, escribieron «sostiene el punto»
con la tabla como único motivo y concedieron: Estrela–Benfica (1575538:a, «la
tabla no lo obliga a ganar»; las dos veces que igualó concedió en el tramo
siguiente, a los 20 y a los 18 minutos, con el banco fresco del favorito) y
Vitória–Porto (1575544:a, «por la tabla y sin antecedente comparable», lo dice
la propia nota; concedió a los 9 minutos del empate, por el banco que la rama
nombraba). El defecto «sigue empujando» se cumplió en Rennes–Lille (1552816:a),
Juventus–Fiorentina (1550189:b), Tigres–Cruz Azul (1551033:a) y
Panathinaikos–Iraklis (1593355:b); Kalamata–Asteras (1593354:b) escribió
`abierto` sin antecedente y estuvo bien.

**En contra 10/11.** PAOK–Olympiakos (1593357:b): «el empate de visita le
sirve: puede sostenerlo», con su motivo de tabla, y se cumplió (del 71' al
final sin más goles). Un caso: no alcanza para aflojar la lista de lo que no
es motivo, pero se cuenta.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* las
`siIguala` con «sostiene el punto» sin antecedente siguen concediendo o
empujando. *Lo tumba si* aparecen varias más como PAOK: «sostiene» con el
empate o la visita como motivo y sin conceder, con el bloque de pie. Habría
que contarlas aparte de las que sostuvo el arquero.

**Comprobación 10/11 (4 lecciones nuevas): SOSTIENE, con un matiz.** Dos
«sostiene el punto» más con motivos de la lista de lo que no es motivo:
Banfield–Atl. Tucumán (1493229:a, «promedios, semifinal de Copa a 8 días»: tras
el 2-2 no hubo más goles, pero la crónica dice que Banfield buscó la victoria
al final, así que la conducta escrita no se dio) y Ñublense–Colo Colo
(1505558:a, un motivo de tabla y sin antecedente: sostuvo 61 minutos y concedió
en el 90+2 con el banco fresco del favorito). El defecto «sigue empujando» se
cumplió en Los Chankas–Alianza Lima (1549551:a). No aparece ningún caso como
PAOK («sostiene» por el empate o la visita, sin conceder y con el bloque de
pie): la lista no se afloja.

**Matiz:** el mismo motivo falló en `siLeEmpatan`, que este punto no cubre:
Millonarios–Tolima (1549857:b, «el empate le sirve, vuelve a la pelota sin
volcarse»; concedió a los 11 minutos del empate, dentro de su ventana). Es un
caso: va a candidatos (extender la lista a `siLeEmpatan`), no al punto.

**Núcleo / historial.** Núcleo: la lista de lo que no es motivo y la vida útil
del bloque improvisado (dos líneas en la 44 (f)). Historial: los casos.

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

**Refuerzo 10/11.** El defecto de los tres se cumplió en unas 18 lecciones
nuevas: el favorito por μ con margen ≥ 0,30 o el obligado que marca siguió
atacando y amplió (Bolívar–The Strongest 1645539:a, IDV–Aucas 1639803:b,
Trinidense–Ameliano 1632061:a, Trabzonspor–Alanyaspor 1584457:b,
Freiburg–Union 1575216:a, Villarreal–Getafe 1570452:a, St. Truiden–Zulte
1558678:a, Bournemouth–Ipswich 1557462:b, Liverpool–Palace 1557459:b,
Nice–Angers 1552810:b, PSV–Cambuur 1552219:b, Toluca–Monterrey 1551034:a,
Inter–Como 1550191:a, Santa Fe–Pasto 1549862:a, Leverkusen–Köln 1575219:b,
Brest–Lyon 1552812:a, Brujas–Anderlecht 1558672:a, Fenerbahçe–Çorum
1584459:b). Y lo que no es motivo volvió a no serlo: Sunderland–Chelsea
(1557466:a) escribió ECHADA-PSI por la menor μ, «la racha de siete sin ganar» y
la falta de confianza, y el bloque cedió la pelota sin partirse. La racha se
suma a la lista de lo que no es motivo, junto al anuncio del DT, el clásico y
la tabla. Un motivo nombrable que valió: Gent–Kortrijk (1558673:a), favorito
con `F2` = 1 tras un viaje europeo, administró con dos defensores al 65'.
Carabobo–La Guaira (1646935:b) administró con el motivo del partido escrito
(«el empate da la final», que es `P1b`).

**En contra 10/11 (matiz, no tumba).** Union SG–Genk (1558676:a) y
Atalanta–Monza (1550192:b): el favorito o el obligado con «sigue atacando»
cerró antes del final (un defensor a los 4 minutos del gol; un volante por el
9 al 83'), sin conceder. Y Freiburg–Union (1575216:a) tenía `F2` = 1 y siguió
atacando. Lo que dicen: el defecto describe el arranque de la ventaja y no
garantiza el cierre, y `F2` = 1 es un motivo **nombrable**, no un defecto que
se aplica solo. La redacción propuesta ya lo deja así.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* el
favorito de los tres sigue atacando casi siempre y las ramas «en su plan» del
no favorito no fallan más que las otras. *Lo tumba si* varios no favoritos
escritos «sigue atacando» por falta de antecedente vuelven a administrar
(Osasuna, La Louvière). O si varios favoritos cierran con cambios defensivos
**y conceden**: eso pediría que la rama nombre el cierre.

**Comprobación 10/11 (15 lecciones nuevas): SOSTIENE el defecto de los tres;
MATIZA la lectura de «sigue atacando».** El favorito por μ con margen ≥ 0,30 o
el obligado de tabla siguió atacando en once: Rosario Central (1493237:a,
margen 1,77; amplió con diez), Huracán (1493228:b), U. Católica–Limache
(1505559:a), U. de Chile–Cobresal (1505560:a, margen 1,72), La
Calera–Huachipato (1505562:a), Melgar (1549548:a), Cajamarca (1549549:a), Colo
Colo (1505558:b, margen 0,49), Atl. Nacional (1549855:a: siguió atacando y
perdió la ventaja, que es la línea del empate y no la tipología), Sport
Huancayo (1549546:b) y La Serena (1505557:a, con antecedente). Guabirá
(1645537:a) escribió «sigue atacando» «sin antecedente de administrar» y goleó;
la lección no dice si era de los tres, así que no cuenta ni a favor ni en
contra de «en su plan». Ningún no favorito escrito «sigue atacando» por falta
de antecedente administró, y ningún favorito cerró con cambios defensivos y
concedió: lo que tumbaría el punto no apareció.

**Matiz:** tres equipos con ventaja cedieron la pelota. Tolima (1549857:a,
obligado) cedió y cortó con faltas sin partirse; Independiente Medellín
(1549858:b, obligado) cedió (38 %) y siguió amenazando; Coquimbo (1505555:b)
escribió «sigue atacando con la pelota» por la posesión de temporada y
administró. No tumba el defecto (ninguno concedió por cerrar): pide leer la
tipología por la amenaza y no por la pelota. Va como punto 15.

**Núcleo / historial.** Núcleo: el defecto de los tres, «en su plan» para los
demás y la lista corta de motivos y de lo que no es motivo. Historial: los
casos y los conteos.

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

**Refuerzo 10/11.** Lille–Rennes (1552816:b) escribió «administra» apoyado en
el 0-0 de Bodø («un 0-0 no es antecedente de cerrar una ventaja») y perdió la
ventaja del 24' a los 7 minutos. Puebla–Querétaro (1551036:b) escribió
ECHADA-PSI con un solo antecedente de otra cuenta (el 2-1 perdido ante Atlas en
un 4-3) y con el gol al 9' no se echó: amplió y administró. Los dos son el «sin
ventaja que cuidar / otro margen» de este punto. Aston Villa–United
(1557464:b, la línea del antecedente no era la de hoy) y Cuenca–Orense
(1639833:a, antecedente de visita) son la regla vigente incumplida.

**En contra 10/11.** Recoleta–Cerro Porteño (1632056:b): el antecedente
coincidía en condición y perfil del rival, faltaban dos piezas (lo decía la
reserva escrita) y se repitió igual: administró desde el 58' y perdió la
ventaja al 81', como en Pedro Juan Caballero. Va contra la exigencia de piezas
de la v0.1.25, no contra este punto. Es un caso: no se afloja.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* los
antecedentes con otro marcador o con otra cuenta siguen sin anticipar el
partido. *Lo tumba si* aparecen ramas con un antecedente de otro marcador que
igual se cumplen. Para que cuente, tiene que verse en «administra» y no solo
en «sostiene».

**Comprobación 10/11 (5 lecciones nuevas): SOSTIENE.** Estudiantes LP–Talleres
(1493239:b): ECHADA-VOL apoyada en el 0-0 del Maracaná, de Libertadores, **con
uno menos** y con una pieza ausente hoy; le empataron a los 14 minutos. Es
«otra cuenta de jugadores». Atl. Tucumán–Banfield (1493229:b): el antecedente
lo habían sostenido una pieza ausente hoy y el arquero; administró y perdió un
2-0 del 18'. Es además el caso que equilibra a Recoleta («En contra 10/11»):
ahí la pieza ausente sí importó. Del otro lado, los antecedentes que coincidían
en todo se cumplieron: Concepción–Everton (1505556:b, el 1-0 de visita en
Ñublense: no se partió y amplió) y Nacional–Viseu (1575540:a, «misma condición,
perfil y línea», con pocos minutos de prueba). Ninguna rama con un antecedente
de otro marcador se cumplió.

**Núcleo / historial.** Núcleo: «el antecedente coincide en condición, perfil
del rival, piezas, marcador que se cuidaba y cuenta de jugadores» (una
línea). Historial: los siete partidos y los de esta tanda.

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

**Refuerzo 10/11.** Jaguares–Bucaramanga (1549859:a): roja al 9' con 0-0, y
concedió a los 3 y a los 6 minutos. León–Chivas (1551037:a): roja al 53' con
0-0, y concedió a los 16. Gençlerbirliği–Beşiktaş (1584458:b): roja perdiendo
al 22', y concedió al 45' y al 85'. Groningen–AZ (1552224:b): roja del arquero
al 88' con 3-3, y penal en el 90+1. No concedieron Nacional Potosí–Real Potosí
(1645538:a, roja al 61', 33 minutos sin conceder, con nueve en el añadido),
Barcelona SC–LDU (1639804:a, roja al 61' y paridad restablecida al 76') y
AEK–Levadiakos (1593352:a, roja al 80' ganando, penal anulado por VAR).

**En contra 10/11 (de la frase, no del riesgo).** Santa Clara–Gil Vicente
(1575542:a) escribió la frase de la v0.1.25 («roja empatando → el riesgo es la
echada en el tramo final 75-90'») y se cumplió al pie de la letra: roja al 62'
con 1-1, gol al 81'. Fue a los 19 minutos de la roja: fuera del «+15» y dentro
del régimen de inferioridad, que es lo que este punto propone cobrar. Con la
redacción nueva el caso sigue siendo un acierto del régimen. Lo que no se puede
decir es que «el riesgo arranca con la roja» por esa sola vía. Por eso la
propuesta mantiene el régimen hasta el final y no corta en +15.

**Y en el «Qué NO se propone»:** Brentford–Brighton (1557458:b) es el segundo
caso de roja perdiendo que no compró riesgo (con 0-2 metió un central y un
pivote al 45' y no concedió más), tras Unión–Vélez. Son dos casos: sigue sin
condicionarse el «ISE agravado».

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* las
concesiones tras roja propia temprana siguen cayendo en los primeros minutos
tras la roja o dentro del régimen, y no se juntan en el 75-90 cuando la roja
fue antes. *Lo tumba si* varias rojas tempranas conceden recién en el 75-90:
ahí la ventana del reloj describiría mejor que la de la roja.

**Comprobación 10/11 (9 lecciones nuevas): SOSTIENE.** Las rojas propias antes
del 75' que terminaron en gol concedieron cerca de la roja o dentro del
régimen, ninguna recién en el 75-90: Argentinos–Huracán (1493228:a, roja al 25'
perdiendo, 0-2 al 31': a los 6 minutos), Sarmiento–Tigre (1493240:b, rojas al
50' y al 55' con 0-0, gol al 70': a los 15 de la segunda) e Independiente
Rivadavia–Gimnasia (1493234:b, roja al 17' con 0-0, gol al 45: a los 28, de
pelota parada con error del arquero). Independiente Rivadavia es el segundo
caso, tras Santa Clara, que cae fuera del «+15» y dentro del régimen: confirma
que el régimen siga hasta el final y no se corte en +15. Las rojas tardías
concedieron tarde o no concedieron: Gimnasia (1493234:a, roja al 84' ganando,
gol en el 90+5), Cienciano (1549546:a, 74' perdiendo, sin más goles),
Comerciantes Unidos (1549547:b, 89') y Juan Pablo II (1549548:b, 82', de un
suplente). Rosario Central (1493237:a, roja al 72' ganando 1-0) no se echó y
amplió con diez: otro «no concedió» con ventaja.

**Núcleo / historial.** Núcleo: «la ventana de `siExpulsion.propia` va desde
la roja; el régimen de inferioridad, hasta el final». Historial: las cifras
(11 de 12, 8 de 19) y los partidos.

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

**Refuerzo 10/11.** Con el banco bien nombrado, la vía se cumplió en diez
partidos: Universitario–Moquegua (1549553:a, Angulo), NEC–Utrecht (1552223:b,
Amrabat entró al 59' y asistió al 64'), Asteras–Kalamata (1593354:a, Bolívar),
Kalamata–Asteras (1593354:b), Portuguesa–Metropolitanos (1646934:a),
Tigres–Cruz Azul (1551033:a), Lens–Marseille (1552818:a, Abdallah entró al
78' y marcó al 82'), Groningen–AZ (1552224:b), Real Potosí–Nacional Potosí
(1645538:b) y Twente–Ajax (1552222:a). Lens confirma la segunda línea de la
propuesta: el banco que rompió el empate era el que nombraba **la rama de
ventaja** y entró en `siIguala`. En los fallos y parciales nuevos no aparece
otro titular nombrado como banco.

**Matiz 10/11.** U. Católica–Macará (1639805:b): el banco de Macará estaba
nombrado, pero los dos goles del empate fueron de titulares antes del primer
cambio. «El banco no es la única vía por la que se cae una ventaja.» La rama
nombra el banco **además** de la vía de los titulares, no en su lugar.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* los
cierres siguen encontrando la vía en el banco nombrado y aparecen más
«nombró a un titular» en los partes sin rehacer. *Lo tumba si* el banco
nombrado casi nunca es la vía, porque entonces la lista no aporta y solo
alarga la rama. Contra eso, esta tanda trae diez a favor.

**Comprobación 10/11 (10 lecciones nuevas): SOSTIENE, con dos matices.** El
banco nombrado fue la vía en cuatro partidos: Atl. Tucumán–Banfield (1493229:b,
Machado, entrado al 46', hizo el 2-1), Newell's–Instituto (1493236:b, Tissera,
2-2 en el 90+3), U. de Concepción–O'Higgins (1505561:a, Toloza entró al 68' y
asistió el 2-2 al 71') y Alianza Lima–Los Chankas (1549551:b, y 1549551:a desde
el otro lado: K. Sánchez entró al 56' y empató al 59'). Y el que no lo nombró
lo pagó: Estudiantes LP–Talleres (1493239:b, empate del suplente entrado al
descanso). Huachipato (1505562:b): el banco nombrado entró y no cambió el
volumen, que es lo normal en una rama y no tumba. En esta tanda no hay ningún
titular nombrado como banco.

**Matices.** (1) U. de Chile–Cobresal (1505560:a): la rama nombró a tres
delanteros y el gol fue de dos cambios del descanso, un volante y un defensor:
«el banco del rival se escribe entero y contando los cambios de medio tiempo,
no solo los delanteros». Cabe en «se toma de la hoja»; agrega «entero», con un
caso. (2) Palestino–La Serena (1505557:b): la rama escribió como hecho un banco
que ya había entrado al 63', antes del gol del 65'. Es la regla vigente de la
65 (el banco condicionado a los cambios que quedan al minuto del gol) y el
punto 2 de «Para la app».

**Núcleo / historial.** Núcleo: «el banco sale de la hoja, se reescribe en
`rehacer` y se nombra en todas las ramas donde puede entrar». Historial: los
partidos.

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

**Refuerzo 10/11.** León–Chivas (1551037:a): la roja directa al 53' fue de J.
Rodríguez, la pieza del doble pivote del seguro (Echeverría–J. Rodríguez), y
concedió a los 16 minutos, dos después de rearmar la línea. La pieza también
sale por roja, no solo por cambio. Barcelona–Atlético (1570443:b): al 74'
salió el mediocentro amonestado por un central. La lección pide que la rama
nombre también el cambio defensivo que fuerza la amarilla del contenedor (une
este punto con el 7). Como–Inter (1550191:b) escribió el `sob2` de la rama
heredado del «sin» persiguiendo del DTP y concedió a los 7 minutos: es del
punto 14.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si*, donde la
rama nombró la pieza, la salida de esa pieza (por cambio o por roja) sigue
apareciendo antes de la concesión. *Lo tumba si* las concesiones llegan con
la pieza en cancha tanto como sin ella. Eso no se puede contar hasta que la
app marque el minuto de salida.

**Comprobación 10/11 (2 lecciones nuevas): SOSTIENE, con un caso.**
Everton–Concepción (1505556:a): con `nivelFocoPersiguiendo` «sin», sacó al
contenedor Moya y al lateral Ramos al 77' por dos delanteros y concedió al 84'.
**Matiz:** Alianza Lima–Los Chankas (1549551:b) concedió el empate a los 5
minutos de cambiar a su lateral derecho amonestado, pero en la rama de ventaja,
que este punto no cubre. Con Barcelona–Atlético (1570443:b, del «Refuerzo
10/11») son dos casos del mismo mecanismo (amarilla de la pieza → cambio →
concesión). **Decidido el 10/11/2026:** con dos casos, la extensión a la rama
de ventaja queda **candidato** (regla conservadora); la línea nombra la pieza
en la rama que persigue y en la base `SOB`. Si la salida de la pieza adelanta la concesión
sigue sin poder contarse hasta que la app marque el minuto.

**Núcleo / historial.** Núcleo: «nombrar la pieza que sostiene `sob2`; el
cierre anota cuándo salió (cambio o roja) y no recobra la rama». Historial:
los diez partidos.

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

**Refuerzo 10/11.** Siete lecciones nuevas, todas en la misma dirección.

- Santa Clara–Gil Vicente (1575542:a): el riesgo de roja se nombró en un solo
  candidato (Emanuel Fernandes, 4 amarillas) y la vio Pacheco. «`S1` debe
  nombrar a toda la línea.»
- Gençlerbirliği–Beşiktaş (1584458:b): `S1` sin dato, y un central de la zaga
  nueva vio dos amarillas en cinco minutos. «Se puntúa con las amarillas de la
  tabla F1 (`amarillasEnLaCompeticion`) de las piezas de la zaga, no se deja
  vacío.» El dato existe y no se usó: ver el punto 12.
- León–Chivas (1551037:a) y Brentford–Brighton (1557458:b): `S1` sin dato, y
  la roja directa fue de una pieza del seguro y del 9, respectivamente.
- Nacional Potosí–Real Potosí (1645538:a): `S1` = 1 por las dos rojas
  directas del último partido, y hubo dos rojas más. Confirmación.
- Orense–Cuenca (1639833:b): la roja fue de un suplente que entró a perseguir
  («el banco que persigue también es vía de expulsión»). Es el hueco del
  suplente ya declarado.
- UTC–Sport Boys (1549552:b): expulsaron al DT al 87'. No hay casillero y no
  cambió nada.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* las rojas
que ordenan el partido siguen siendo de titulares de la zaga, el pivote o el
9. *Lo tumba si* son sobre todo de suplentes que entran (Strasbourg, Orense):
entonces lo que falta es el casillero del banco, no el foco en los titulares.

**Comprobación 10/11 (3 lecciones nuevas): SOSTIENE.** (Tres tocan `S1`; se
miraron también las rojas de otras cinco.) Las rojas que ordenaron el partido
fueron tempranas y, por lo que dicen las lecciones, de jugadores que estaban
desde el inicio: Paredes en Argentinos (1493228:a, 25'), Florentín en
Independiente Rivadavia (1493234:b, 17', conducta violenta: otro caso para el
candidato de la v0.1.12) y G. González y L. Suárez en Sarmiento (1493240:b, 50'
y 55'). Las de suplentes llegaron tarde y no ordenaron nada: Durán en Juan
Pablo II (1549548:b, 82') y Aguayo en Tolima (1549857:a, 90+5). Sarmiento
agrega que «llegaba de dos rojas en su último partido» con `S1` = 0,5: el
historial disciplinario también es del equipo (punto 12).

**Núcleo / historial.** Núcleo: «`S1` sobre los titulares que van al choque,
con quien vuelve de una roja, y con el dato de la base cuando está» (una
línea). Historial: los casos.

### 8. F2 subido a mano por viaje y altitud: una contradicción que decidió el usuario (disciplina 21 y fila F2 de `INDICE_IE.md`) — DECIDIDO (a) el 10/11/2026

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
- ~~**(b) Manda la tabla:** se puede subir con fuente nombrada, y los dos
  cierres de arriba se archivan como desacuerdo.~~ *(Descartada el 10/11.)*

**Decidido por el usuario el 10/11/2026:** (a) manda el motor (es lo que la
propuesta recomendaba: F2 es del bloque de peso ×3 y la disciplina 21 nació de
tres correcciones del motor sobre estimaciones a mano). El viaje, la altitud y
el calor van a la caja de sensibilidad con su fuente; el texto exacto está en
«Lista para redactar». El candidato `F2 × F4` de la v0.1.15 sigue como está.

**10/11.** Ninguna lección nueva sube F2 a mano. Las que tocan `F2` = 1 del
motor van en las dos direcciones. Gent–Kortrijk (1558673:a) administró con la
carga del viaje europeo. Freiburg–Union (1575216:a) y Celta–Levante
(1570444:a, 2 días de descanso y 6 rotados, 3,12 de xG) no mostraron la echada
física. Mónaco–Le Mans (1552814:b, 2 días) perdió la ventaja al 90'. No mueve
la decisión: es la fila de F2 del motor, que nadie discute.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene la (a) si*
los F2 subidos a mano vuelven a dar cierres que dicen «iba en la nota». *La
tumba si* aparecen viajes o altitudes que el motor no ve y que explican la
echada: eso daría razón a la (b).

**Comprobación 10/11 (2 lecciones nuevas): SOSTIENE la (a), débil.** Ninguna
lección sube F2 a mano. Dos ramas pusieron la vía en la echada física por la
altura y no se pagó: Juan Pablo II–Melgar (1549548:b: la rama del empate la
ponía desde el 60' en altura y el gol cayó al 48') y Comerciantes
Unidos–Garcilaso (1549547:b: «la vía secundaria de echada en la altura (60-75)
tampoco se pagó»). No apareció ningún viaje ni altitud que el motor no vea y
que explique una echada, que es lo que daría razón a la (b).

**Núcleo / historial.** Núcleo: la (a) (una línea en la 21 y la fila de
`INDICE_IE.md` marcada). Historial: los dos cierres.

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

**Refuerzo 10/11.** Las mismas confirmaciones, con los partidos del 08-09/11:

- **65** (41 lecciones): `abierto` fue la lectura honesta también cuando el
  tramo tuvo las dos caras: Manchester United–Villa (1557464:a, se rompió dos
  veces y rescató en el añadido), Juventus–Fiorentina (1550189:b),
  Macará–U. Católica (1639805:a) y Utrecht–NEC (1552223:a, se rompió con ISE
  de rama 6,67: «el corte no separa»). Le Mans–Mónaco (1552814:a) escribió
  `se_rompe` con un solo antecedente de otra sede y rescató al 90': es la regla
  de la v0.1.25 incumplida, no una causa nueva.
- **66** (45): «no pierde nueve de cada diez, pero no gana uno de cada
  cuatro», jugado por el lado de «no gana» en Universitario–Moquegua
  (1549553:a, dos veces), Chivas–León (1551037:b), Mónaco–Le Mans (1552814:b),
  Brujas–Anderlecht (1558672:a), Olympiakos–PAOK (1593357:a), Asteras–Kalamata
  (1593354:a), Groningen–AZ (1552224:b, con ventaja de dos), Real
  Potosí–Nacional Potosí (1645538:b) y Fiorentina–Juventus (1550189:a). La
  línea del empate escrita en su campo se jugó en Feyenoord–Heerenveen
  (1552221:b), América–Pumas (1551035:b) y Llaneros–Alianza (1549853:b).
- **61** (34): `otra_via` por penal o autogol en Pumas–América (1551035:a),
  Lyon–Brest (1552812:b), Barcelona SC–LDU (1639804:a), Twente–Ajax
  (1552222:a), Estrela–Benfica (1575538:a) y Alianza–Llaneros (1549853:a).
- **43** (8): «0 de 8 en dual» (Pumas–América 1551035:a), y también en Brest,
  Cerro Porteño, Napoli, Fenerbahçe y América de Cali.
- **14** (interacción entre vías): La Guaira–Carabobo (1646935:a). El ISE rojo
  del obligado no se pagó en 90 minutos frente a un rival al que el empate le
  daba la final: «la vía SOB se declara con la salida "el rival administra"».
- **23** (añadido): Aston Villa–United (1557464:b, dos goles en el 90+2 y el
  90+6), Groningen–AZ (1552224:b), Iraklis–Panathinaikos (1593355:a) y
  Portuguesa–Metropolitanos (1646934:a).
- **17** (acierto no testeado): Sport Boys–UTC (1549552:a y b), OFI–Atromitos
  (1593356:a) y América de Cali–Cali (1549854:a), sin goles o sin el
  escenario.
- **24** (la ventana del reloj no se cobra al tipo declarado si la premisa no
  estaba): Rennes–Lille (1552816:a), con la ECHADA-FIS escrita «si va arriba»
  y el gol con 1-1.

**Comprobación con los veredictos del 08-09/11.** *Se sostienen si* los
cierres siguen diciendo «declarado y cumplido» en estas disciplinas. *Las
tumba* una que empiece a acumular fallos en los que la regla se cumplió y el
tramo salió al revés. La que habría que mirar primero es `abierto`: si
aparecen `se_rompe` con un hecho de hoy nombrado y que no se rompen.

**Comprobación 10/11 (unas 60 lecciones nuevas): SOSTIENEN.**

- **65:** `abierto` fue la lectura correcta en unas veinte (Argentinos
  1493228:a, Lanús 1493232:b, Independiente Rivadavia 1493234:b, Audax Italiano
  1505555:a, Everton 1505556:a, Limache 1505559:b, U. de Concepción 1505561:a,
  O'Higgins 1505561:b, Huachipato 1505562:b, ADT 1549545:a, Los Chankas
  1549551:a, Alianza Atlético 1549549:b, Fortaleza 1549858:a, Viseu 1575540:b,
  Bulo Bulo 1645537:b). No hay ningún `se_rompe` con un hecho de hoy que no se
  rompiera. Los dos «hechos» apoyados en el once se cayeron con el once
  oficial: Bulo Bulo (un grid que la API corrigió después del pitazo) y Águilas
  Doradas (1549861:b, cuarentena que enseña: «la espalda a Barrios», que no
  estuvo en la hoja). Es la revisión con el once oficial que ya está en la 65.
- **61** (la salida «marcó él» no cuenta contra la rama; sin crónica, la vía
  escrita): Lanús, Newell's 1493236:b, Talleres 1493239:a, Ñublense 1505558:a,
  Melgar 1549548:a, Sport Huancayo 1549546:b, Cobresal 1505560:b (la vía pagada
  a los 75 minutos del gol: la rama se cobra por su salida).
- **66** (las dos ventajas y la línea del empate): Central Córdoba 1493232:a,
  Instituto 1493236:a, Gimnasia 1493234:a, Colo Colo 1505558:b, Sporting
  Cristal 1549545:b, Cienciano 1549546:a, Atl. Nacional 1549855:a, Juan Pablo
  II 1549548:b, Cajamarca 1549549:a.
- **23** (añadido): Boca–Defensa (1493231:a y b), Gimnasia, Newell's, Guabirá
  1645537:a. **14:** Boca (1493231:a) y Millonarios (1549857:b), con el rival
  que no quiere correr. **16** (superioridad no administra): Tigre 1493240:a,
  Huracán 1493228:b, Melgar, Sport Huancayo.
- **17, 24, 43 y 50:** Huracán 1493228:b (no testeado); Viseu 1575540:b y Atl.
  Tucumán 1493229:b (la ventana coincide pero la vía es otra); Cajamarca
  1549549:a (dual, otra vez sin echada); Audax 1505555:a y Fortaleza 1549858:a.

Ningún grupo junta fallos con la regla cumplida y el tramo al revés.

**Núcleo / historial.** No agrega texto: las reglas ya están en el núcleo y
los casos van al historial.

### 10. La ventana de la vía del banco rival cuenta desde que el banco entra (disciplina 44 (c) y 56) — MEDIR PRIMERO + CALCULABLE

**Qué dice hoy.** La 44 (c) da a cada rama su ventana relativa al evento que
la abre (el gol, la roja). La 56 dice que el inicio del régimen sale del
indicador que lo declara, no del reloj. Ninguna de las dos dice qué pasa
cuando lo que abre la vía es **un cambio** del rival o del propio equipo.

**Qué casos lo piden** (dos, del 08/11):

- Asteras–Kalamata (1593354:a): ventaja desde el 45+1. La ventana +15 de
  `siMarcaPrimero` (45-60) quedó limpia, y el gol llegó a los 21 minutos del
  gol, **ocho después** de que entraran Bolívar y Carreazo, el banco que la
  rama nombraba. «La +15 dice si se paga rápido; la vía del banco rival se
  cobra desde que el banco entra.»
- Elche–Betis (1570445:a): 0-0 a la hora, triple cambio ofensivo del local al
  69' y concesión al 81', fuera de la base 60-75. «Anclar la ventana SOB al
  minuto del cambio ofensivo (+15) cuando el 0-0 llega a la hora.»

Van en la misma dirección los cierres del punto 5 donde el gol llegó poco
después de que entrara el banco nombrado (NEC: entró al 59', gol al 64'; Lens:
entró al 78', gol al 82'; Kalamata: entró al 59', gol al 67').

**Qué se propone.** **⚠️ Medir primero; no se redacta todavía.** Mover el
inicio de una ventana es mover una cantidad del skill, y dos casos no la
sostienen. Cómo se mediría: en los tramos del veredicto, para cada gol
concedido con la vía del banco o de la SOB, los minutos desde el último
cambio ofensivo (del rival que persigue o del propio que empuja) contra los
minutos desde el gol que abrió la rama y desde el inicio de la ventana del
reloj. La pregunta es cuál de los tres relojes junta más goles en sus 15
minutos. Con n ≥ 30 goles por reloj, la regla de la v0.1.25.

**Calculable.** Todo: los cambios con su minuto y el perfil del que entra
están en los eventos de la ficha (la misma materia que `S2` en
`noCalculables`). Ver «Para la app», punto 10.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* aparecen
más goles de la vía del banco o de la SOB dentro de los 15 minutos de un
cambio ofensivo y fuera de la +15 del gol. *Lo tumba si* esos goles caen
igual de seguido lejos de los cambios.

**Comprobación 10/11 (6 lecciones nuevas): MATIZA; sigue en medir primero.** A
favor: U. de Concepción–O'Higgins (1505561:a: ventaja desde el 41', la +15
limpia, y el 2-2 al 71', a los 3 minutos de que entrara Toloza); Alianza Lima
(1549551:b: K. Sánchez entró al 56' y empató al 59', aunque dentro de la +15
del gol) y Everton (1505556:a: el 0-2 al 84', a los 7 minutos del cambio
ofensivo propio del 77' y a los 12 de la entrada de Henríquez). En contra,
goles del banco lejos de su entrada: U. de Chile–Cobresal (1505560:a, cambios
del descanso, gol en el 90+2), Ñublense–Colo Colo (1505558:a, Bolados entró al
68' y marcó en el 90+2) y Viseu (1575540:b, tres cambios ofensivos al 70', gol
al 86'). Los tres relojes no se separan a ojo: decide la medición de «Para la
app», punto 10.

**Núcleo / historial.** Si se aprueba tras la medición, una línea en la
44 (c). Hoy es historial (candidato).

### 11. Con 0-0 y el empate en la mano, la SOB de «si a la hora no gana, empuja» pide un hecho de hoy (disciplinas 18 y 56) — CANDIDATO (decidido el 10/11/2026: se espera)

**Qué dice hoy.** La 18 manda puntuar `SOB1`, `P1b` y `P1c` con la tabla. La 56
dice que con `SOB1` = 1 el régimen empieza en el 0. No dice qué se escribe para
quien la tabla pone a pelear abajo pero al que **el empate de visita le
sirve**.

**Qué casos lo piden** (dos, del 08/11, los dos visitantes con 0-0):

- Atromitos–OFI (1593356:b, Jev: `tde`): «el penúltimo de visita al que el
  empate le sirve no se expone a la hora con 0-0». La SOB 60-75 de «si a la
  hora no gana, empuja» no tenía un hecho del partido, y el régimen no ocurrió
  (37 % de pelota, 0 remates al arco).
- Levante–Celta (1570444:b): el colista de visita, con 0-0 ante un local
  dominante, cambió delantero por defensor al 56' y administró el punto. «P1b /
  P1c = 1 por descenso no llevó a SOB con el empate en la mano.»

A favor del mismo lado, La Guaira–Carabobo (1646935:a, punto 9): la SOB del
obligado no se paga si el rival administra.

**Lo que se proponía redactar (queda como candidato, no entra a la v0.1.26)**
(18, una línea): **`SOB1` = 1 por la tabla abre la
SOB desde el pitazo (56). Una SOB que se escribe para la hora («si a la hora no
gana, empuja») con 0-0 de visita necesita un hecho de hoy** (el DT que lo
anunció, el banco ofensivo en la hoja, un rival que no administra). Si no lo
hay, la base queda en su plan y la SOB va a la rama `siRecibePrimero`. No se
toca la puntuación de `SOB1`.

**La tensión (resuelta el 10/11: se espera).** El punto 1 dice que «el empate le sirve» y
«juega de visita» **no** son motivo para «sostiene el punto» en `siIguala`
(13 de 17 casos concedieron). Este punto dice que, con 0-0 de visita, ese
mismo hecho **sí** frena la SOB de la hora. Las dos cosas pueden ser ciertas,
porque son regímenes distintos: el que igualó viene empujando con el banco
adentro, y el del 0-0 nunca persiguió. Pero es la misma frase leída en dos
direcciones, y PAOK (1593357:b, «En contra» del punto 1) cae justo en el medio.
**Decidido por el usuario el 10/11/2026:** se espera; queda como candidato
(la propuesta no recomendaba ninguna de las dos; con la regla conservadora,
dos casos de un mismo día y ninguno en la comprobación no hacen una regla, y
entrar ahora dejaría la misma frase leída en dos direcciones contra el punto
1). Se reabre con el tercer caso, en «Cuándo se reabre».

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* los
visitantes con 0-0 y el empate útil no empujan a la hora cuando la SOB no
traía un hecho. *Lo tumba si* empujan y conceden: entonces la tabla sola sí
abría la SOB.

**Comprobación 10/11 (0 lecciones nuevas): SIN CASOS.** Ningún visitante con
0-0, la tabla abajo y el empate útil. Lo más cercano, Defensa y Justicia en la
Bombonera (1493231:b), es un visitante ya clasificado que cerró con cambios
defensivos en el 90+1 y concedió en el 90+6: no es el régimen de este punto.
Decidido el 10/11: candidato.

**Núcleo / historial.** Hoy, historial (candidato: Atromitos, Levante). Si
entra con el tercer caso, la línea de la 18 y la frase que separa los dos
regímenes en la 44 (f).

### 12. `S1` desde la base: las amarillas y las rojas que la app ya calcula (bloque S, disciplina 21 aplicada a `S1`) — CALCULABLE → APP, SIN PESO

**Qué hay.** `GET …/tde/{id}` lista `S1` en `noCalculables` («faltas por
partido y jugadores al límite SÍ están en bruto, pero nadie los agrega
todavía», `backend/analisis/tde.py`). Pero desde el 30/10 `f1/{id}` trae
`amarillasEnLaCompeticion` por fila y `sancionados` con la roja del último
partido (`backend/sanciones.py`). El insumo existe y el TDE no lo recibe. La
v0.1.25 ya había aprobado «los insumos de `S1` en `GET …/tde/{id}`»
(`PENDIENTES.md`), y sigue sin hacerse.

**Qué casos lo piden.** Las siete del «Refuerzo 10/11» del punto 7. Sobre
todo Gençlerbirliği (1584458:b, dos amarillas de un central de la zaga
nueva), León (1551037:a), Brentford (1557458:b), con `S1` sin dato y la roja
ordenando el partido, y Nacional Potosí (1645538:a), donde `S1` = 1 por las
rojas de la base acertó.

**Qué se propone.**

- **En la app:** `GET …/tde/{id}` trae, por lado, los titulares probables (o
  los del once) de zaga, pivote y 9 con sus amarillas en la competición, quién
  está a una del ciclo (cuando `UMBRALES` conoce la regla) y quién vuelve de
  una roja. Con `conteoParcial`, lo dice. Es dato, no un `S1` puntuado.
- **En el skill (una línea en el bloque S):** con ese dato a la vista, `S1` se
  puntúa, o se declara sin dato con el motivo de la app. **No se puntúa de
  memoria ni se deja vacío si la app lo trae.**
- **No se toca el peso de `S1`** ni su escala.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* siguen
apareciendo rojas de piezas con amarillas acumuladas o que volvían de una
roja, con `S1` sin dato. *Lo tumba si* las rojas que ordenan el partido no
tienen nada que ver con el historial disciplinario. Entonces el dato no
aportaría y bastaría con declararlo sin dato.

**Comprobación 10/11 (1 lecciones nuevas): SOSTIENE, con un caso.**
Sarmiento–Tigre (1493240:b): «llegaba de dos rojas en su último partido», `S1`
= 0,5, y volvió a quedarse con nueve. La roja del último partido es justo lo
que `sanciones.py` ya tiene. El caso agrega que el dato sirva también como
cuenta del equipo, no solo por jugador; con un caso va a candidatos.
Independiente Rivadavia (1493234:b): conducta violenta con `S1` sin dato; la
lección no dice si había historial, así que no tumba.

**Núcleo / historial.** Núcleo: la línea del bloque S. Historial: los casos.

### 13. La rama del TDE y el plan del DTP del mismo equipo dicen lo mismo antes de depositar (disciplinas 63 y 44 (b)) — RÚBRICA

**Qué dice hoy.** El TDE hereda del DTP `C1` y `SOB2` (con alerta
`HERENCIA-DTP` si difieren). La tipología de cada rama (administra, sigue
atacando, empuja) no se compara con el plan por fases del DTP (M3) ni con su
veredicto por rama.

**Qué casos lo piden** (dos):

- Chivas–León (1551037:b, 09/11): con uno más y 1-0, `siExpulsionRival` decía
  «no administra», y el M3 del DTP propio pedía «doble pivote fijo y
  carrileros abajo» si iba arriba. Al 84' entró un defensor y concedió a los 3
  minutos. «La rama del TDE y el M3 se contradecían y el equipo jugó el M3:
  revisar que las dos capas digan lo mismo antes de depositar.»
- Union–Köln (1575207:a, 07/11, ya en «Para la app», punto 6): «sigue
  atacando» con el repliegue como plan del DT en la p5 de su propio DTP.

**Qué se propone redactar** (una línea en la 44 (b), junto a «nombrar por
qué»): **si el DTP del mismo equipo (M3 o el veredicto por rama) dice otra
cosa que la rama, se nombra cuál manda y por qué.** Si no hay motivo, manda el
plan del DT del DTP, que es el que tiene la fuente. Es lo mismo que la
herencia de `C1` y `SOB2`, llevado a la tipología, sin número.

**Qué NO se propone.** Una alerta calculada: comparar prosa no es aritmética.
**Decidido por el usuario el 10/11/2026:** por ahora no se vigila (la
propuesta no recomendaba; lo conservador con dos casos es no abrir otra
pregunta del guardrail de coherencia de Jev). Queda candidato a ese
guardrail, nunca a `HERENCIA-DTP`.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* aparecen
más casos en los que el equipo jugó el plan del DTP contra la rama del TDE.
*Lo tumba si* cuando las dos capas difieren el equipo juega la rama del TDE
tanto como el DTP: entonces nombrar cuál manda no aporta.

**Comprobación 10/11 (0 lecciones nuevas): SIN CASOS.** Ninguna lección nueva
compara la rama del TDE con el M3 o con el veredicto por rama del DTP.

**Núcleo / historial.** Núcleo: una línea en la 44 (b). Historial: los dos
casos.

### 14. Incidencia 1056: el `sob2` de las ramas del que persigue se hereda del DTP y `HERENCIA-DTP` lo compara (disciplina 63) — APROBADO por el usuario el 10/11/2026 (opción a)

**APROBADO por el usuario el 10/11/2026 (opción a, «heredar y avisar»).** Las
ramas del que persigue (`siRecibePrimero`, `siLeEmpatan` cuando vuelve a
empujar y `siIguala`) heredan el `sob2` de `nivelFocoPersiguiendo` del DTP (o
de `nivelRivalPersiguiendo` del DTP del rival) y `HERENCIA-DTP` compara también
la rama. **No se recalculan los partes viejos:** el ISE de rama de lo
depositado antes se lee como se declaró. Lo que hace falta (nada se tocó en
esta revisión):

- **(1) La app** — la implementa el mantenimiento: `parte.py` (`HEREDA_SOB2` en
  `ise_de_ramas`, `_heredar` y la alerta `HERENCIA-DTP`) y `dtp_cowork.py`
  (`herencia_tde`), con el contrato primero y los tests, en el orden de «Qué
  tendría que cambiar en la app» de abajo.
- **(2) El skill DTP:** la línea de `diagnostico-tactico` (M2 e Integración)
  que dice que la rama persiguiendo «no se hereda hasta que el usuario decida»
  cambia por «viaja al `sob2` de las ramas del que persigue del TDE»,
  coordinada con `DTP_v1.8_propuesta.md` para que las dos versiones salgan
  juntas.
- **(3) `DEUDA.md`:** cerrar el «pendiente del usuario» de la entrada DTP v1.6
  / TDE v0.1.23 con esta decisión.

En el TDE, la línea de la 63 pierde «pendiente de la app» cuando la app lo
haga. Lo de abajo («Las dos salidas», «Recomendación») queda como la historia
de la decisión.

**El caso.** Westerlo–Charleroi (1558679:a, 07/11; la incidencia 1056 no está
en el dossier y no se bajó, el caso sale de la lección). La rama
`siRecibePrimero` tomó el `sob2` del nivel «persiguiendo» del DTP («sin» →
`sob2` 1, ISE de rama 8,33), y la vía se pagó enseguida: concedió al 60', 65'
y 72' persiguiendo, y al 67' sacó al contenedor Fofana por un delantero. El
DTP del mismo partido dice lo mismo desde su lado: «con el seguro
persiguiendo declarado "sin"… la rama persiguiendo es DESFAVORABLE y no
NEUTRO». Van en la misma dirección Konyaspor–Galatasaray (1584465:b, 07/11:
`sob2` 1 del «sin» persiguiendo, y no del «depende» del arranque; la
exposición existió) y Como–Inter (1550191:b, 08/11: `sob2` 1 heredado del
«sin» persiguiendo, ISE de rama 10, concedió a los 7 minutos). **Los tres lo
hicieron bien a mano.** Lo que la 1056 pide es que no dependa de la mano.

**Qué dice hoy el skill.** Desde la v0.1.23, la disciplina 63 manda que el
`sob2` de `siRecibePrimero`, de `siLeEmpatan` cuando vuelve a empujar y de
`siIguala` salga del `nivelFocoPersiguiendo` del DTP (o del
`nivelRivalPersiguiendo` del DTP del rival), en lugar del 0.5. La v0.1.25
agregó que «`HERENCIA-DTP` compare también el `sob2` de la rama» está
«aprobado y pendiente de la app», con dos partes que lo escribieron en contra
(Rayo–Celta, Xerez–Cádiz). **En el TDE no hay regla nueva que escribir.**

**Qué dice el otro skill.** `diagnostico-tactico` (v1.5 en adelante, líneas de
M2 e Integración) todavía dice que la rama persiguiendo «se declara pero no se
hereda hasta que el usuario decida si el SOB2 sale de ella». Y `DEUDA.md` (la
entrada de la DTP v1.6 / TDE v0.1.23) anota «el SOB2 del TDE sigue heredando
el nivel de hoy, no la rama persiguiendo (pendiente del usuario)». **Los dos
skills se contradicen**, y la app hace lo que dice el DTP.

**Qué hace hoy la app** (leído, sin tocar):

- `backend/analisis/dtp_cowork.py`, `herencia_tde` (línea 1159): hereda `C1`
  y **solo el `SOB2` de la base**, del `nivelFoco` del DTP propio o del
  `nivelRival` del DTP del rival. `nivelFocoPersiguiendo` y
  `nivelRivalPersiguiendo` se guardan (línea 1104), con el comentario «el SOB2
  del TDE sigue heredando nivelFoco/nivelRival hasta que el usuario decida»,
  y no se usan.
- `backend/analisis/parte.py`, `_heredar` (línea 4192): pisa los
  `indicadores` del bloque con lo heredado y lo lista en `heredadoDtp`. La
  alerta `HERENCIA-DTP` (línea 4553) recorre `heredadoDtp`: **compara solo la
  base**.
- `parte.ise_de_ramas` (línea 2461) con `HEREDA_SOB2 = ("siMarcaPrimero",)`
  (línea 2458): las ramas del que persigue no heredan nada. Si traen `sob1` ≥
  0.5 sin `sob2`, el recibo lo pide en `faltan` (línea 3521: «sin evidencia,
  0.5»), sin mirar el DTP.
- `PENDIENTES.md` **ya lo anota**: «`HERENCIA-DTP` en el `sob2` de rama; el
  rehacer recalcula el ISE de rama» (pendientes del TDE, redactado el 01/11).

**Las dos salidas.**

- **(a) Hereda y avisa, como con la base.** Para `siRecibePrimero`,
  `siIguala` y `siLeEmpatan` con `sob1` ≥ 0.5 (el filtro que ya usa el recibo
  para «vuelve a empujar»), el `sob2` de la rama se toma de
  `nivelFocoPersiguiendo` (si falta, de `nivelRivalPersiguiendo` del DTP del
  rival). El declarado queda al lado, el ISE de rama se recalcula, y
  `HERENCIA-DTP` sale con la rama nombrada si difieren. Sin nivel
  persiguiendo en el DTP, queda lo declarado (o el 0.5), y se dice.
- **(b) Solo avisa.** La rama conserva el `sob2` declarado, y `HERENCIA-DTP`
  suena (tipo `dato`) cuando difiere del nivel persiguiendo del DTP. Cowork
  corrige o sostiene en `notas`.

**Recomendación: (a).** Es lo que el TDE ya manda y lo que la base hace hace un
mes («manda el DTP, el skill prohíbe re-estimarlo»). Los tres casos de arriba
muestran que la corrida lo hace bien cuando lo hace, y la (b) deja el número
a merced de que lo haga. Pero la (a) cambia el ISE de rama de partes que lo
declararon distinto. Por eso:

- **⚠️ medir antes de cobrar con él.** La v0.1.25 contó, con n chico, que el
  `sob2` subido concedió en 11 de 36 ramas y el igual al de la base en 6 de
  16. La regla de revisión es n ≥ 10 ramas jugadas por valor de herencia
  (fijo · depende · sin). No se mueve la escala (0 · 0.5 · 1) ni la fórmula:
  cambia de qué fuente sale el número de la rama.
- **No se recalcula hacia atrás.** El ISE de rama de los partes depositados
  antes de la versión que lo apruebe se lee como se declaró (como la
  v0.1.24/v0.1.25 con el desenlace: `regimen_desenlace` por versión).

**Qué tendría que cambiar en la app** (después de aprobar, en este orden):

1. `docs/openapi.yaml`: cada entrada de `heredadoDtp` lleva `rama` (null para
   la base), y la rama heredada lleva `sob2Declarado` / `iseRamaHeredados`
   con `SOB2`.
2. `dtp_cowork.herencia_tde`: devolver además, por lado, `SOB2_PERSIGUIENDO`
   desde `nivelFocoPersiguiendo` (propio) o `nivelRivalPersiguiendo` (rival),
   con su `de`. Quitar el comentario «hasta que el usuario decida».
3. `parte._heredar` y `parte.ise_de_ramas`: aplicarlo a las tres ramas (con el
   filtro `sob1` ≥ 0.5 para `siLeEmpatan`) y que `HERENCIA-DTP` recorra
   también la herencia de rama. El aviso de `faltan` de la línea 3521 deja de
   decir «sin evidencia, 0.5» cuando el DTP trae el nivel.
4. El **rehacer**: con el DTP rehecho, el `sob2` de rama y su ISE se
   recalculan. El DTP no vuelve atrás para callar la alerta (incidencia 634,
   como la base).
5. Tests: `backend/test_api.py` (un parte con nivel persiguiendo distinto del
   declarado → alerta con la rama; sin nivel → queda lo declarado) y
   `test_dtp`.

**Qué tendría que cambiar en los skills.**

- **TDE (disciplina 63):** quitar «pendiente de la app» y decir qué ramas
  heredan (las tres, `siLeEmpatan` solo cuando vuelve a empujar). Una línea.
- **DTP** (`diagnostico-tactico`, M2 e Integración): cambiar «se declara pero
  no se hereda hasta que el usuario decida» por «viaja directo al `sob2` de las
  ramas del que persigue del TDE». Es del encargo del DTP: se coordina con su
  propuesta para que las dos versiones salgan juntas.
- **DEUDA.md:** cerrar la línea «pendiente del usuario» de la entrada de la
  v0.1.23 con la decisión.

**Comprobación con los veredictos del 08-09/11.** *Se sostiene si* las ramas
del que persigue con nivel «sin» en el DTP conceden más que las «fijo», y las
partes que declararon otro `sob2` que el DTP fallan la vía más que las que
copiaron el DTP. *Lo tumba si* el `sob2` del DTP persiguiendo no separa
(«sin» y «fijo» conceden igual). En ese caso, mejor la (b) hasta medir.

**Comprobación 10/11 (2 lecciones nuevas): SOSTIENE, sin separar.** Dos partes
más lo hicieron a mano y la vía se pagó: Everton–Concepción (1505556:a:
`nivelFocoPersiguiendo` «sin», ISE de rama 8,33, concedió al 84' tras sacar al
contenedor) y Limache–U. Católica (1505559:b: `sob2` del «depende»
persiguiendo, ISE de rama 5, concedió a los 8 minutos). No hay ramas con «fijo»
en esta tanda: «sin» contra «fijo» sigue sin poder separarse y queda la
revisión con n ≥ 10 por valor.

**Núcleo / historial.** Núcleo: la línea de la 63 sin «pendiente». Historial:
Westerlo, Konyaspor, Como, Rayo–Celta y Xerez–Cádiz, y la cifra 11 de 36 /
6 de 16.

### 15. «Sigue atacando» se lee por la amenaza, no por la pelota (disciplina 44 (b)) — RÚBRICA (nuevo en la comprobación del 10/11)

**Qué dice hoy.** La 44 (b) da el defecto «sigue atacando» a los tres y pide
nombrar por qué para «administra». No dice con qué se comprueba la tipología ni
con qué hecho se escribe.

**Qué casos lo piden** (tres, del 07-08/11, de la comprobación):

- Coquimbo–Audax Italiano (1505555:b, Jev: `lectura_efe`): la rama se escribió
  «sigue atacando con la pelota (tiene posesión con su doble pivote)» y con 0-1
  de visita desde el 50' cedió la pelota (36 %) y cerró con un defensor por un
  delantero. «La posesión de temporada no es hecho del partido de hoy para
  descartar que administre.»
- Independiente Medellín–Fortaleza (1549858:b): el obligado con ventaja
  temprana cedió la pelota (38 %), siguió amenazando (12 remates, 7 en el área)
  y amplió. «"Sigue atacando" se lee por la amenaza y no por la posesión.»
- Tolima–Millonarios (1549857:a): el obligado con ventaja desde el 36' cedió la
  pelota (46 % contra su 57,8 de media), cortó con faltas y no se partió (0,66
  de xG del rival). Pide «la variante de administrar cediendo cuando el rival
  persigue sin profundidad».

Van en la misma dirección los matices del punto 2 (Union SG–Genk y
Atalanta–Monza cerraron sin conceder).

**Qué se propone redactar** (44 (b), una línea junto al defecto): **«sigue
atacando» describe la amenaza (remates, llegadas al área), no la pelota.** La
posesión de temporada y el modelo del equipo no son motivo para escribirlo (es
identidad, disciplina 6, ya en la lista del punto 2). El que cede la pelota y
sigue llegando cumple la rama; el que cede y deja de llegar administró, y el
cierre lo dice.

**Qué NO se propone.** Una tipología nueva «administra cediendo» (Tolima es un
caso y las tipologías no se tocan). Un umbral de posesión o de remates: no hay
datos por tramo (La Serena, 1505557:a: «sin datos por tramo, el volumen tras el
gol no se mide»).

**Calculable.** Los remates y el xG del que va arriba **desde el gol** saldrían
de la ficha si trajera estadísticas por tramo; hoy solo hay totales. Candidato
para la app, junto al punto 10.

**Comprobación.** *Se sostiene si* las ramas «sigue atacando» que ceden la
pelota y siguen llegando no conceden más que las que la conservan. *Lo tumba
si* ceder la pelota con «sigue atacando» escrito precede a la concesión:
entonces la pelota sí importaba.

**Núcleo / historial.** Núcleo: una línea en la 44 (b). Historial: Coquimbo,
Medellín y Tolima.

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
   candidato a un aviso como `HERENCIA-DTP`, no regla. *Refuerzo 10/11:*
   Chivas–León (1551037:b) es el segundo caso (la rama decía «no administra», el
   M3 del DTP pedía cerrar y el equipo jugó el M3). Pasa a rúbrica en el punto
   13. **Decidido el 10/11: no se vigila por ahora**; la pregunta del
   guardrail de coherencia de Jev queda candidata, no se hace.
7. **Textos viejos.** `backend/analisis/lecciones.py` (la nota de
   `desenlaceTde`) todavía dice «Lectura por defecto: ISE de rama ≥ 7 →
   se_rompe», y el rechazo de `desenlace` en `backend/analisis/parte.py` cita
   «TDE v0.1.24». El cobro ya usa `abierto`; solo la prosa quedó vieja. *Sigue igual
   el 10/11:* la nota del dossier de las 02:13 repite «Lectura por defecto: ISE de
   rama ≥ 7 → se_rompe» (`backend/analisis/lecciones.py`, línea 889).
8. **F2 (punto 8), DECIDIDO (a) el 10/11.** Cambiar el texto de
   `f2.puedeSubir` en `backend/analisis/tde.py` (línea 321) de «súbelo a mano»
   a: «viaje largo, cambio de altitud o calor extremo no los ve el motor y no
   suben F2: van a la caja de sensibilidad como el otro extremo, con su fuente
   (TDE v0.1.26, disciplina 21)». Contrato primero si el campo cambia de
   significado (`docs/openapi.yaml`), y su test.
9. **La versión del 01/11.** Anotar en `SUBIDA_VERSION` la hora en que la
   v0.1.25 llegó a la cuenta, para separar las lecciones del 01/11 escritas con
   la v0.1.24 (hoy el dossier no lo hace por lección). *Verificado el 10/11:*
   ya está (`backend/analisis/simulacion.py`, `SUBIDA_VERSION`:
   `("teorema-del-echado", "v0.1.25"): "2026-11-01 13:00:00"`); lo que falta
   es que el dossier lo use por lección. Al subir la v0.1.26, anotar su hora
   ahí.
10. **Los cambios con su minuto, por tramo (punto 10).** Para cada gol
    concedido, los minutos desde el último cambio ofensivo del rival y del
    propio equipo, con el perfil del que entra (la materia de `S2` en
    `noCalculables`), al lado de los minutos desde el gol que abrió la rama y
    desde el inicio de la ventana del reloj. Es la medición que pide el punto
    10, y sirve también para el banco condicionado de la 65 (punto 2 de arriba).
11. **Los insumos de `S1` (punto 12).** `GET …/tde/{id}` trae, por lado, las
    amarillas en la competición de zaga, pivote y 9, quién está a una del
    ciclo y quién vuelve de una roja, desde `backend/sanciones.py` (lo mismo
    que ya viaja en `f1/{id}`), y saca `S1` de `noCalculables` cuando hay
    dato. Era pendiente de la v0.1.25.
12. **La herencia del `sob2` de rama (punto 14), APROBADA el 10/11 con la
    (a): la implementa el mantenimiento.** Contrato primero (`heredadoDtp` con `rama`), después
    `dtp_cowork.herencia_tde`, `parte._heredar` / `parte.ise_de_ramas` y la
    alerta `HERENCIA-DTP`, el rehacer y los tests. El detalle está en el punto
    14. Ya figura en `PENDIENTES.md`.
13. **Quién persigue por `μ_partido` en los tramos.** Sigue siendo el
    requisito del candidato del defecto por quién persigue. Esta tanda suma
    casos en las dos direcciones (ver «Lo que NO se propone»).

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
- **Actualizado con el dossier del 10/11** (las series son de toda la cohorte,
  no de las 227 nuevas): `rescata` con hecho, **17 de 24** (71 %, IC 51-85);
  `se_rompe`, **46 de 97** (47 %, IC 38-57); en los **444** tramos `abierto`
  lo observado fue `se_rompe` 185 (42 %), `rescata` 171 (39 %) y sin más
  goles 88. Ventanas: **103 con gol de 591** comprobadas (17 %), y la base del
  reloj **81 de 361** (22 %). Nada cambia de lectura: `rescata` sigue por
  debajo de n = 30 y `se_rompe` sigue sin separarse de lo que pasa en
  `abierto`.

## Lo que NO se propone y por qué

- **Aplicar el defecto por quién persigue.** Esta semana hay lecciones en las
  dos direcciones: a favor Westerlo–Charleroi (1558679:a) y Paris FC–Monaco
  (1552807:b); en contra Nottingham Forest–City (1557465:b, el favorito por μ
  con margen 0,80 concedió persiguiendo), Progreso–Defensor (1646900:a) e
  Independiente Petrolero–Tomayapo (1645534:a). Sin la medición con
  `μ_partido` (punto 1 de la app), sigue candidato. *10/11, en las dos
  direcciones otra vez:* se rompió persiguiendo el no favorito Como–Inter
  (1550191:b) y el favorito obligado Querétaro–Puebla (1551036:a, a los 27
  minutos y por la misma vía); rescataron Estrela–Benfica (1575538:a, dos
  veces), Kalamata–Asteras (1593354:b) y Nacional Potosí–Real Potosí
  (1645538:a); las dos caras en el mismo partido, Manchester United–Villa
  (1557464:a), Juventus–Fiorentina (1550189:b) y Macará–U. Católica
  (1639805:a). Sigue sin poder leerse sin `μ_partido` en el tramo.
- **El «doble golpe» como salida.** Seis partidos más (Leipzig–Augsburg
  1575213:b, Villarreal–PSG 1635746:a, Galatasaray–Stuttgart 1635669:b,
  Pereira–Tolima 1549852:a, IDV–LDU 1639800:b, Paranaense–Vasco 1492440:a, este
  en cuarentena). Sigue sin medirse qué pasa después, y el corte en minutos
  sería inventado. *10/11:* dos más del lado del que va arriba,
  Feyenoord–Heerenveen (1552221:b, 45+3 y 47) y U. Católica–Macará
  (1639805:b, 56' y 58', los dos de titulares). La lección de UC lo pide «con
  sus minutos», no como regla. *Comprobación 10/11:* dos más del lado del que
  persigue, Banfield (1493229:a, a los 3 minutos) y O'Higgins (1505561:b, a los
  2), antes de desarmarse persiguiendo.
- **La ventaja de dos.** Cinco partidos perdieron o vieron descontar una ventaja
  de dos (Kasımpaşa–Beşiktaş 1584453:b, Cobresal–Everton 1505547:a,
  Sittard–Telstar 1552217:a, Universitario–Sport Boys 1549535:b,
  Gimnasia–Belgrano 1493233:a). Es el candidato «C3 desdoblado por magnitud» de
  la v0.1.15. `ventajaPorMinuto` no se parte por margen; primero tiene que
  hacerlo la app. *10/11:* tres más, Feyenoord–Heerenveen (1552221:b, 0-2 al
  31'), Groningen–AZ (1552224:b, 1-3 al 54', perdió 4-3) y U. Católica–Macará
  (1639805:b, 2-0 empatado en 4 minutos), y Aston Villa–United (1557464:b,
  4-2 desde el 53', dos en el añadido). Ya son nueve partidos: es lo primero
  que habría que medir cuando la app parta `ventajaPorMinuto` por margen.
  *Comprobación 10/11:* diez, con Atl. Tucumán–Banfield (1493229:b, 2-0 al 18'
  que terminó 2-2).
- **Un umbral de atajadas o de xG** para «lo sostuvo el arquero» (Cagliari,
  Galatasaray, Marseille, Universitario, Cusco): se dice con el dato a la vista.
- **Una tipología nueva** para la pérdida en salida bajo presión
  (Slavia–Arsenal, 1635726:a): es un caso.
- **El objetivo puntuado una vez para todas las ramas** (Danubio–Nacional,
  1646902:a: dos ramas del mismo equipo se contradijeron sobre si el empate le
  servía). Ya lo dice la disciplina 18.
- **Casos sueltos del 08-09/11, que quedan anotados.** La rama de ventaja con
  `sob1` 0 y el ISE del arranque cuando la rama dice «sigue atacando»
  (Olympiakos–PAOK, 1593357:a, disciplina 62: «sus SOB describen ese
  régimen»). `siLeEmpatan` con «vuelve al bloque, el empate le basta» como
  ECHADA-VOL con su ventana hasta el final (Iraklis–Panathinaikos,
  1593355:a). La rotación de 6 que no costó volumen (Celta–Levante, 1570444:a,
  disciplina 36). El DT expulsado sin casillero (UTC, 1549552:b). Cada uno es
  un caso.

- **Candidatos de la comprobación del 10/11 (un caso cada uno; no son regla).**

  - Extender a `siLeEmpatan` la lista del punto 1 («el empate le sirve» no pone
    a salvo al que vuelve a la pelota sin volcarse): Millonarios–Tolima
    (1549857:b).
  - El banco del rival se nombra entero, con los cambios del descanso y no solo
    los delanteros: U. de Chile–Cobresal (1505560:a). Cabe en el punto 5.
  - La rama nombra el banco **además** de la vía de los titulares, no en su
    lugar: U. Católica–Macará (1639805:b). Cabe en el punto 5.
  - *(dos casos, decidido el 10/11)* La pieza del seguro que sale por la
    amarilla también en la **rama de ventaja**: Barcelona–Atlético
    (1570443:b) y Alianza Lima–Los Chankas (1549551:b). Cabe en el punto 6.
  - *(dos casos, decidido el 10/11)* El punto 11 entero: Atromitos–OFI
    (1593356:b) y Levante–Celta (1570444:b).
  - *(decidido el 10/11)* Vigilar con el guardrail de Jev la rama del TDE
    contra el M3 del DTP (punto 13): Chivas–León, Union–Köln.
  - El historial disciplinario del equipo (rojas del último partido) como dato de
    `S1`, además del del jugador: Sarmiento–Tigre (1493240:b).
  - El segundo gol rápido tras el empate como hecho repetido de un equipo:
    Pereira (1549855:b), «candidato a medir y no a regla».
  - Un «hecho» de `se_rompe` sacado de un grid que la API corrige después del
    pitazo no es hecho: Bulo Bulo (1645537:b); Águilas Doradas (1549861:b) va
    igual, pero está en cuarentena y no cuenta.

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
- **F2:** decidido el 10/11 (a). Se reabre si aparecen viajes o altitudes
  que el motor no ve y que explican una echada (lo que daría razón a la (b)).
- **La ventana desde el cambio (punto 10):** cuando la app dé los minutos
  desde el cambio ofensivo por gol concedido, con n ≥ 30 por reloj.
- **La herencia del `sob2` de rama (punto 14):** aprobada el 10/11 (a); cuando
  la app la aplique, revisar con n ≥ 10 ramas jugadas por valor (fijo · depende ·
  sin) si el heredado separa mejor que el 0.5.
- **La SOB de la hora con el empate en la mano (punto 11), candidato desde
  el 10/11:** entra con el tercer caso de un visitante con 0-0, la tabla abajo
  y el empate útil que no empujó sin un hecho escrito (de otro cruce que
  Atromitos–OFI y Levante–Celta); se cae si aparecen visitantes así que
  empujaron y concedieron sin hecho escrito.

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
- **El dossier del 10/11 está cortado.** Se generó a las 02:13 UTC, con unos
  50 veredictos del 08-09/11 todavía cerrándose. Las 227 nuevas son casi todas
  del 08/11 (solo 14 del 09/11): los partidos del domingo están poco
  representados. Por eso cada punto lleva su «Se sostiene si… / Lo tumba si…».
- **Los tres «piden mover un número».** `porModoFallo.pidenMoverNumero` dice
  3, pero ninguna de las 865 pendientes trae `proponeMoverNumero: true`.
  Probablemente son lecciones ya cerradas que el contador sigue sumando; no se
  pudo verificar sin la API. No cambia nada: ninguna propuesta mueve un número.
- **Muchas etiquetas «fallo» son el 1X2.** En las 68 de esta tanda pasa lo
  mismo que en la anterior: la mayoría dicen «declarado y cumplido» o
  «confirmación». Los conteos de cada punto son lecciones que lo dicen, no
  tasas.

## Núcleo e historial

La propuesta del núcleo (`NUCLEO_SKILLS_propuesta.md`, 03/11) **no se aplica
acá**. Si se aplica, esto es lo que va arriba del `SKILL.md` (lo que la corrida
necesita para escribir el parte) y lo que va a `references/HISTORIAL.md`:

| # | Núcleo (regla, una o dos líneas en su disciplina) | Historial |
|---|---|---|
| 1 | 44 (f): lo que no es motivo para «sostiene el punto»; la vida útil del bloque improvisado | los 17 + 2 partidos, PAOK en contra |
| 2 | 44 (b): el defecto de los tres; «en su plan» para los demás; los motivos nombrables y los que no lo son (DT, clásico, tabla, racha) | los ~30 partidos y los matices (Union SG, Atalanta, Freiburg) |
| 3 | 44 (b) y (f): el antecedente coincide también en el marcador y en la cuenta de jugadores | los 7 + 2 partidos, Recoleta en contra |
| 4 | 16: la ventana de `siExpulsion.propia` desde la roja, el régimen hasta el final (sale la frase del 75-90) | las cifras 11 de 12 y 8 de 19, los partidos, Santa Clara |
| 5 | 66, 65, 44 (a): el banco de la hoja, reescrito en `rehacer`, en todas las ramas | los partidos |
| 6 | 63: nombrar la pieza del `sob2`; el cierre anota su salida (cambio o roja) | los 10 + 2 partidos |
| 7 | bloque S: `S1` sobre los titulares que van al choque y quien vuelve de una roja | los casos |
| 8 | 21 y fila F2 de `INDICE_IE.md`: la (a), manda el motor (decidido el 10/11) | los dos cierres |
| 9 | nada nuevo | las confirmaciones |
| 10 | (solo si se aprueba tras medir) una línea en la 44 (c) | hoy, candidato: Asteras, Elche |
| 11 | (candidato desde el 10/11; nada hasta el tercer caso) | Atromitos, Levante |
| 12 | bloque S: con el dato de la app, `S1` se puntúa o se declara sin dato con su motivo | los casos |
| 13 | 44 (b): si el DTP del mismo equipo dice otra cosa, se nombra cuál manda | Chivas, Union–Köln |
| 14 | 63 sin «pendiente de la app», con las tres ramas (aprobado el 10/11) | Westerlo, Konyaspor, Como, Everton, Limache, Rayo–Celta, Xerez–Cádiz, 11 de 36 / 6 de 16 |
| 15 | 44 (b): «sigue atacando» describe la amenaza, no la pelota; la posesión de temporada no es motivo | Coquimbo, Medellín, Tolima |

Ninguno de los cambios agrega una regla que viva solo en el historial. Los
casos y los conteos de esta propuesta son todos historial.

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
| 8 | F2 a mano por viaje y altitud: manda el motor | 21, `INDICE_IE.md` | **decidido (a) el 10/11** | 2 |
| 9 | Confirmaciones sin cambio (65, 61, 66, 43, 16, 14, 23, 50) | varias | cierre sin texto | el resto |
| 10 | La ventana de la vía del banco desde que el banco entra | 44 (c), 56 | medir primero + calculable | 2 (+3 del punto 5) |
| 11 | Con 0-0 de visita y el empate útil, la SOB de la hora pide un hecho (tensión con el 1) | 18, 56 | **candidato (decidido el 10/11)** | 2 |
| 12 | `S1` desde la base (amarillas y rojas de `sanciones.py`) | bloque S | calculable → app, sin peso | 7 |
| 13 | La rama del TDE y el plan del DTP del mismo equipo dicen lo mismo | 44 (b), 63 | rúbrica | 2 |
| 14 | 1056: el `sob2` de rama se hereda del DTP persiguiendo y `HERENCIA-DTP` lo compara | 63 | **APROBADO (a) el 10/11** → app (mantenimiento) + DTP + DEUDA | 5 (Westerlo, Konyaspor, Como, Everton, Limache) |
| 15 | «Sigue atacando» se lee por la amenaza, no por la pelota | 44 (b) | rúbrica | 3 (Coquimbo, Medellín, Tolima) |

**Ningún peso, umbral, compuerta, banda ni ventana por defecto se mueve.** La
única frase que se retira es de la v0.1.25 (la roja propia ubicada en el
75-90) y se reemplaza por lo que ya decía la 44 (c). Con la actualización del
10/11 sigue igual: el punto 10 movería el inicio de una ventana y por eso va a
medir primero, y el 14 no cambia la escala ni la fórmula, sino de qué fuente
sale el `sob2` de la rama.


## Tabla de cambios

| # | Cambio (una línea) | Tipo | Comprobación 10/11 | Núcleo o historial |
|---|---|---|---|---|
| 1 | «Sostiene el punto» en `siIguala`: qué NO es motivo; vida útil del bloque improvisado | rúbrica | sostiene (matiz: el mismo motivo falla en `siLeEmpatan`, a candidatos) | núcleo |
| 2 | Rama de ventaja: «sigue atacando» por defecto solo para los tres; los demás «en su plan» | rúbrica | sostiene (matiz: ceder la pelota → punto 15) | núcleo |
| 3 | El antecedente coincide también en el marcador que se cuidaba y en la cuenta de jugadores | rúbrica | sostiene | núcleo |
| 4 | Con roja propia, la ventana va desde la roja y el régimen hasta el final (sale el 75-90) | rúbrica | sostiene | núcleo |
| 5 | El banco se toma de la hoja, se reescribe en `rehacer` y se nombra en todas las ramas | rúbrica | sostiene (matiz: banco entero con los cambios del descanso) | núcleo |
| 6 | Se nombra la pieza que sostiene `sob2`; el cierre anota cuándo salió | rúbrica | sostiene (matiz: también en la rama de ventaja) | núcleo |
| 7 | `S1` sobre los titulares que van al choque y quien vuelve de una roja | rúbrica | sostiene | núcleo |
| 8 | F2 subido a mano por viaje y altitud: manda el motor (a) | decidido (a) el 10/11 | sostiene la (a), débil | núcleo |
| 9 | Confirmaciones sin cambio (65, 61, 66, 43, 16, 14, 23, 50, 17, 24) | rúbrica | sostiene | historial |
| 10 | La ventana de la vía del banco rival cuenta desde que el banco entra | medir | matiza (casos en los dos sentidos) | historial (candidato) |
| 11 | Con 0-0 de visita y el empate útil, la SOB de la hora pide un hecho de hoy | candidato (decidido el 10/11) | sin casos | historial (candidato) |
| 12 | `S1` desde la base: amarillas y rojas de `sanciones.py` en `GET …/tde/{id}` | app | sostiene (un caso) | núcleo |
| 13 | La rama del TDE y el plan del DTP del mismo equipo dicen lo mismo, o se nombra cuál manda | rúbrica | sin casos | núcleo |
| 14 | 1056: el `sob2` de las ramas del que persigue se hereda del DTP y `HERENCIA-DTP` lo compara — APROBADO (a) el 10/11 | app | sostiene (sin «fijo» para separar) | núcleo |
| 15 | «Sigue atacando» se lee por la amenaza, no por la pelota; la posesión de temporada no es motivo | rúbrica | nuevo (3 casos) | núcleo |
