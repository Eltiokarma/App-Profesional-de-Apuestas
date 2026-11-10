# Propuesta de revisión · `efe-clasificador` v1.9 → v1.10 (+ `efe-dashboard` v1.12 → v1.13)

**Estado:** PROPUESTA, sin aprobar. Escrita el 10/11/2026 desde el dossier de
`GET /analisis/cowork/revision/efe-clasificador` (**dossier generado el 10/11 a
las 02:13 UTC**): **568 lecciones pendientes** de los partidos del 01/11 al
09/11, 152 de ellas de partidos del 08/11 o después. **Comprobada el mismo día
con un segundo corte (10/11 a las 04:29 UTC): 71 lecciones nuevas** de 29
partidos del 07 y 08/11 que no estaban en el primero (ver «De dónde sale»).
Cada cambio lleva su «**Comprobación 10/11**» debajo de la línea «Se sostiene
si…», y al final hay una «Tabla de cambios». **Absorbe la propuesta v1.10 del
08/11** (que estaba en este mismo archivo; su texto queda en la historia de
git): era la de las 416 lecciones del 01 al 07/11, nunca aprobada, y sus seis
cambios están acá con la marca «era el 08/11-N», con lo que las lecciones
nuevas dicen de cada uno. Las verificaciones del 08/11 que cerraban aquella
propuesta (Remo recién ascendido y la regla de amarillas de la UEFA 2026/27, ya
corregida en `backend/sanciones.py`) valen igual acá.

La base es la v1.9 vigente (`docs/skills/efe-clasificador/SKILL.md`,
`references/rubrica-efe-v1.9.md`) y `efe-dashboard` v1.12. Ningún skill, código
ni lección se tocó para escribir esto.

**Comprobación hecha.** El dossier se cortó a las 02:13 UTC del 10/11, con unos
50 veredictos del 07 al 09/11 todavía cerrándose. Ya se cerraron: las 71
lecciones del EFE que trajeron se leyeron todas, una por una, contra la línea
«Se sostiene si… / Lo tumba si…» de cada cambio.

## El número: decidido, v1.10 (usuario, 10/11)

**Lo que las lecciones justifican es una 1.10, no una 2.0.** Ninguna lección
pide mover un peso, un máximo, un corte de la tabla de puntuación ni un corte de
zona, y Jev no marcó ninguna con `proponeMoverNumero` (563 sin etiqueta y 5 en
`false` en el primer corte; en el segundo, 69 sin etiqueta y 2 en `false`). Los
cambios son de protocolo y de redacción: el orden del rehacer, qué
anuncia cada zona de la F3, cuándo el sistema es un supuesto, la certeza de la
sanción, la rama de rotación y el banco probable. Los bloques A-H, los pesos y
la tabla de puntuación quedan como están.

**El modo de fallo `lectura_efe` tampoco la justifica** (sección siguiente):
de los 130 fallos con esa etiqueta en todo el sistema, 125 están en los dossiers
de otros skills, y en las lecciones pendientes casi todos corrigen una regla del
TDE o del DTP, no del EFE. Solo en unas 14 de las 85 de otros skills hay un
insumo del EFE (más las 3 del propio EFE, y 1 más en el segundo corte:
Newell's 1493236b, el banco de una duda, cambio 10).

**La estructura de los archivos tampoco cambia el número.** Si esta revisión se
aplica junto con el NÚCLEO (`NUCLEO_SKILLS_propuesta.md`: el changelog y los
casos pasan a `references/HISTORIAL.md`), el skill cambia de forma aunque no de
reglas, y el changelog de la v1.10 lo dice así. **Decidido: v1.10** (usuario,
10/11), con núcleo o sin él.

## De dónde sale

- **568 lecciones:** 278 aciertos, 126 parciales y 164 fallos, de 236
  partidos. Todas son `ciega` + `PRE`.
  - **Del 01 al 07/11:** 416 lecciones, la base de la propuesta del 08/11 (202 / 95 / 119).
  - **Del 08 y 09/11:** 152 lecciones (76 aciertos, 31 parciales y 45
    fallos), de 67 partidos. Ninguna es de copa ni está en cuarentena.
  - **9 son de copa nacional** (Copa de la División Profesional de Bolivia,
    03 al 05/11). Fijan rúbrica y no entran a ninguna métrica.
  - **4 están en cuarentena que enseña**, por DT distinto en el parte
    (Athletico–Vasco 1492440 y PAOK–Asteras 1593351). Fijan rúbrica y no
    mueven números. El dossier lista además 6 en cuarentena que no enseña
    (Huracán–Tigre 1493219). Quedan fuera.
  - **555 son acreditables** (`puedeMoverNumeros`).
- **Segundo corte (10/11, 04:29 UTC): 71 lecciones nuevas** (33 aciertos, 13
  parciales y 25 fallos) de **29 partidos** del 07/11 (40 lecciones) y del
  08/11 (31). Ninguno de esos partidos estaba en el primer corte. Son de
  Argentina, Chile, Perú, Colombia y Bolivia, más uno de Portugal
  (Nacional–Académico Viseu). Todas son `ciega` y ninguna es de copa.
  - **3 en cuarentena que enseña:** Once Caldas–Águilas Doradas (1549861). El
    parte puso a Herrera y dirigió el interino Carlos Valencia. Fijan rúbrica y
    no mueven números.
  - **68 son acreditables.** Una sola tiene `lectura_efe` (Newell's 1493236b).
    Jev marcó `proponeMoverNumero: false` en 2 y dejó las otras 69 sin
    etiqueta.
  - **Por grupo** (el mismo criterio): tabla F1, 21 (8 / 4 / 9) de 18
    partidos; brecha y empate técnico, 18 (10 / 3 / 5); B5, B6 y el arco, 8
    (5 / 1 / 2); F3, 8 (2 / 1 / 5); EJE-DEBUTANTE, 7 (3 / 1 / 3); rama once
    alternativo, 4 (2 / 2 / 0); T.54, 2; FACTOR-X y G-BLOQUE, 2; jerarquía de
    fuentes, 1. No hay ninguna de sanción ni del sistema (D1/H).
  - **Con los dos cortes: 639 lecciones** (311 / 139 / 189) de 265 partidos,
    623 acreditables.
- **Los cuatro casos que todavía no tienen la cuarentena que les corresponde**
  (LDU 1631509, Palmeiras 1492426, Manta 1639824 y 1639827) **no aparecen** en
  las lecciones del EFE, ni en el primer corte ni en el segundo. Ninguna regla de acá se apoya en ellos. (LDU–Barcelona
  SC 1639804 es otro partido y está limpio.)
- **Métricas de la población que acredita** (`metricas`, 22 casos y 44 lados):
  29 aciertos, 7 parciales y 8 fallos por lado. El 1X2 acertó 17 de 22, con un
  Brier de 0,452 contra 0,492 de la línea de base. Son números del parte
  entero y de sad-analysis, no del EFE. Se citan para dar contexto y no mueven
  nada.
- **El sesgo de atribución sigue mandando** (`sesgoDeAtribucion`). Las
  lecciones del empate técnico son 138 de 568, una de cada cuatro. En las
  nuevas son 40 de 152, casi todas «declarada y cumplida»: un fallo ahí es del
  1X2, no de la regla. Los conteos de este documento **no son una tasa de
  acierto del skill**.
- **Cómo se contó.** Cada lección va al grupo de su `reglaTocada`, en el orden
  de la tabla final. No se usa el texto, como hizo la propuesta del 08/11, así que los
  números de cada grupo no son los de la propuesta del 08/11.

## El modo de fallo `lectura_efe`: cuánto es del EFE

**Lo que dicen los dossiers.** En `porModoFallo` hay 130 fallos etiquetados
`lectura_efe` en todo el sistema:
- 65 en el TDE;
- 58 en el DTP;
- 5 en el EFE;
- 2 en sad-analysis.

Entre las lecciones pendientes hay 88: 39 del TDE, 46 del DTP y 3 del EFE.

**Lo que dicen las lecciones.** La definición de Jev
(`backend/analisis/modo_fallo.py`) es «la rúbrica del EFE se aplicó mal: un
bloque puntuó lo que el propio texto no sostenía…». Pero la taxonomía no tiene
otra casilla para «la lectura del skill fue mala», así que Jev pone ahí los
errores de lectura del DTP y del TDE.
- **TDE (39):** las 39 citan una disciplina del propio TDE en `reglaTocada`.
  Son la 44 (b) (19: el antecedente de «administra» no se parecía al partido),
  la 66 y la 65 (8 cada una) y la 61 (3).
- **DTP (46):** las 46 citan el DTP. Son M2 (25: el veredicto de la rama no
  nombró la vía entera), M5 (11: el volumen se cuenta donde se remata), el
  checklist del bloque y la posesión por rama.

Esto ya se había visto como incidencia (1062 y 794: «la etiqueta `lectura_efe`
es insumo de la fase D, no juez»).

**Lo que sí es del EFE** (leído caso por caso). En unas 14 de las 85 lecciones
de otros skills,
el error del otro skill empieza en un insumo que el EFE escribe y que el otro
skill toma tal cual:

| Insumo del EFE | Lección del otro skill | Va al cambio |
|---|---|---|
| **El banco probable** (quién arranca en el banco y puede cambiar el partido) | DTP: Heerenveen 1552221a (Meerveld, del XI de referencia, arrancó suplente e hizo tres; el parte escribió «banco corto»), Riestra 1493235b («banco corto», empató con dos suplentes), Utrecht 1552214b, Manchester United 1557464a. TDE: Köln 1575207b, Le Mans 1552814a (Colas, en duda por un agregador, salió del banco y empató), Always Ready 1645536a (un titular nombrado como banco), Torino 1550195a (el banco del rival) | 10 |
| **La línea nueva** (EJE-DEBUTANTE) | DTP: Aston Villa 1557464b (la línea cambió en dos de cuatro, con Harwood-Bellis sin fila en la F1), Lille 1635640b (línea de cuatro sin minutos juntos: vía, no certeza), Atlético de Madrid 1635622a (pareja con un lateral reconvertido) | 3 y 9 |
| **El sistema y el DT nuevo** | TDE: Cercle 1558675b (debut de Caixinha con un 3-4-2-1 que la apertura no tenía) | 2 |
| **La rotación y el calendario** | TDE: Universidad Católica 1639802a (ocho rotados por la Copa), Stuttgart 1575214a (tercer partido en 8 días: cedió la pelota con ventaja). Athletico–Vasco 1492440b, en cuarentena, solo como contexto | 6 |

Y las 3 lecciones `lectura_efe` del propio EFE:
- **Lyon (1552812b):** el recomputo no se hizo con cinco rotados (cambio 6).
- **Estrela (1575538a):** D3 ❌ firme con tres casos del DT nuevo (cambio 11).
- **Bayern (1635622b):** la F3 roja en ATK, leída como ataque roto, con un
  recambio que tenía rodaje (cambio 8).

**Conclusión.** El modo de fallo más grande del sistema no es, en su mayor
parte, un error del EFE: es una casilla de la taxonomía que junta la lectura de
tres skills. Lo que sí es del EFE se reparte entre la tabla F1, el banco
probable y la línea nueva, y entra a los cambios 1, 3, 6 y 10. Separar la
etiqueta es de la app y lo decide el usuario (A0).

## Lo que la v1.9 acertó y no hay que tocar (con los casos del 08-09/11)

- **El empate técnico de formación** (brecha con T.54, R-KT.2 o
  ESCALA-LIGAS). Se declaró sin empujar el 1X2 en casi todos los partes.
  - **Ganó el de menor porcentaje o empató:**
    - St. Truiden–Zulte Waregem (1558678): un 31,4 % con DT de dos días ganó
      4-1.
    - Toluca–Monterrey (1551034): el 74 % perdió 4-0.
    - Querétaro–Puebla (1551036).
    - Sunderland–Chelsea (1557466).
    - Napoli–Lazio (1550193): el de menor porcentaje generó 2,44 de xG
      contra 0,92.
    - Carabobo–La Guaira (1646935), Barcelona SC–LDU (1639804), Cerro–Recoleta
      (1632056) y Universitario–Moquegua (1549553).
  - **Contraejemplos** (ganó el de mayor porcentaje con la alerta activa):
    Cruz Azul–Tigres (1551033), Marseille–Lens (1552818), Cambuur–PSV
    (1552219), Lorient–Le Havre (1552813) y Beşiktaş–Gençlerbirliği (1584458).
  - **No mueve la regla.** Sigue la medición pendiente (A6).
  - **Segundo corte:** 18 lecciones de la brecha y el empate técnico (10 / 3 /
    5), y en 17 la brecha se declaró y no empujó el 1X2. Ganó el de menor
    porcentaje o empató en Tigre–Sarmiento (1493240), Unión La Calera–Huachipato
    (1505562), Universidad de Concepción–O'Higgins (1505561, ganó el de 33 %),
    Concepción–Everton (1505556), Cajamarca–Alianza Atlético (1549549),
    Tolima–Millonarios (1549857), Nacional–Académico Viseu (1575540, ganó el de
    17 %), Chankas–Alianza Lima (1549551), ADT–Cristal (1549545),
    Garcilaso–Comerciantes (1549547), Gimnasia–Independiente Rivadavia
    (1493234), Central Córdoba–Lanús (1493232) y Talleres–Estudiantes
    (1493239). Ganó el de mayor porcentaje en Melgar–Juan Pablo II (1549548),
    Colo Colo–Ñublense (1505558) y Boca–Defensa (1493231).
- **T.54 baja la confianza en la serie, no anuncia el resultado:** Leverkusen
  (1575219, tres derrotas seguidas y ganó de visita), Braga (1575541, DT de 19
  días), Puebla (1551036, una burbuja hecha con otros DT que se cortó) y
  Bournemouth (1557462, T.54-B por herencia de ciclo).
- **La jerarquía de fuentes:**
  - Feyenoord (1552221): Targhalline, «no juega» según el agregador, fue
    titular.
  - Cali (1549854): la contradicción entre Semana e Infobae quedó declarada.
  - Santa Fe (1549862): la baja del arquero titular salió de la prensa
    nacional, a tres días y sin parte del club. Era Duda, y jugó.
  - Le Mans (1552814): Colas, Duda por un agregador, fue al banco y decidió.
- **COLAPSO EN CASCADA describe y no predice.** Napoli (1550193), Tigres
  (1551033), Le Havre (1552813), Estrela (1575538) y Recoleta (1632056)
  recibieron primero con D3 ❌ y ninguno se rompió.
- **EJE-DEBUTANTE amplía el rango, no es vía de gol por sí sola.**
  - **Confirmada con el once:** Gençlerbirliği (1584458, 4,09 de xG en
    contra), Hoffenheim (1575215), Union Berlin (1575216, 2,62), AZ (1552224) y
    Barcelona SC (1639804).
  - **Sin efecto o la sostuvo otro:** Rennes (1552816), Milan (1550190, 5
    atajadas de Maignan), Liverpool (1557459, la pareja nueva armó el 0-1),
    La Guaira (1646935), Iraklis (1593355) y Ameliano (1632061).
- **C4 que pasa a patrón:** Universidad Católica (1639805) perdió una ventaja
  por tercera vez seguida (2-0 → 2-2 en 4 minutos).
- **El E se lee en la condición:** Brentford (1557458).
- **FACTOR-X amplía el rango, no mueve el centro:** Bolívar (1645539).

## Los cambios propuestos

Doce cambios al clasificador, todos independientes: se aprueban o se rechazan
uno por uno. Los seis primeros eran los de la propuesta del 08/11.

Marcas: **[rúbrica]**, cambia el texto de la regla · **[CALCULABLE→app]**, lo
calcula la app y no la corrida · **[MEDIR PRIMERO]**, no entra sin medir ·
**[DECIDE USUARIO]**, hay una contradicción o una regla que se afloja.

---

### 1. El rehacer con el once oficial empieza por la tabla F1, y una baja que está en la hoja deja de ser baja — era el 08/11-1 · [rúbrica] [CALCULABLE→app] [DECIDE USUARIO]

**Qué dice hoy (v1.9).** «Con el once oficial a la vista, los once titulares
tienen fila.» La app avisa `ONCE-SIN-FILA-F1` al leer, con el texto «con 3 o
más, rehacer la tabla F1» (`parte.py`, verificado hoy).

**Lo que dijo la propuesta del 08/11.** Desde el 03/11 hubo 37 lecciones de 34 partidos
rehechos con el once a la vista y con titulares sin fila. Propuso:
- un orden fijo del rehacer: F1 → bajas de la hoja → B6 → EJE → B y F → D1 y H;
- la fila para los once, sin umbral;
- que la baja que está en la hoja (Táchira 1646929, Pollero) pase a
  disponible.

**Lo que traen las lecciones nuevas: lo refuerzan.** En el grupo de la tabla F1
hay 113 lecciones (53 aciertos, 26 parciales y 34 fallos). Del 08/11 en
adelante son 28 lecciones de 26 partidos, y en 11 (10 partidos) el once ya
estaba a la vista o el parte se rehízo:
- **Real Sociedad (1570449):** el once se capturó a las 14:47 UTC y el último
  depósito fue a las 15:04. Aihen Muñoz, el lateral que el propio DTP marcaba
  como la espalda a atacar, quedó sin fila.
- **LDU (1639804b):** tres rotados sin fila, y uno de ellos fue el goleador. Se
  rehízo el DTP y no la F1.
- **NEC (1552223b):** M. Bakker, sin fila, asistió el 0-1.
- **Aston Villa (1557464b):** Goretzka y Harwood-Bellis, sin fila. Goretzka
  hizo el 2-4 y Harwood-Bellis jugó en la pareja central rearmada.
- **Sunderland (1557466a):** Talbi y Meunier, sin fila. Talbi estaba en la vía
  principal del DTP.
- **Aucas (1639803a):** el lateral nuevo del carril más atacado.
- **Otros sin fila:** Orense (1639833b), Barcelona SC (1639804a, Intriago),
  Alanyaspor (1584457a), Rio Ave (1575541a) y Lorient (1552813b).

**Lo nuevo: la causa está en la rutina, no en el skill.** El modo `rehacer` de
`corrida-sad` (`.claude/skills/corrida-sad/SKILL.md`, paso 2):
- carga solo `diagnostico-tactico` y `sad-analysis`, no el EFE;
- en el paso 4 dice: «Lo demás no se toca: una baja decisiva que no juega, un
  arquero distinto (EFE v1.6, B6)…».

El mantenimiento ya lo vio y lo dejó esperando una decisión (1257, 1265 y 1339,
que remiten a la **1068**). Mientras la rutina no cargue el EFE, la regla de la
v1.9 no se puede cumplir al rehacer, por bien que esté escrita. Es una
**contradicción entre el skill y la rutina**, y la decide el usuario:
- **(a)** el rehacer carga el EFE y hace el orden del cambio 1;
- **(b)** la app suma la fila del titular que falta, con su `rolSugerido` y la
  marca «agregada por la app» (opción de A1);
- **(c)** las dos cosas.

La propuesta del 08/11 no lo había visto.

**Matices nuevos, sin regla nueva** (son la regla 1 de la v1.9 sin aplicar):
- **El recambio de la baja: todos los candidatos al puesto, no solo el que
  nombra la previa.** Brujas (1558672a): el recambio de Potts fue Tsawa, sin
  fila, y el EJE-DEBUTANTE quedó escrito sobre la pareja equivocada. También
  Toluca (1551034a: Luan y B. García sin fila, B. García asistió), Asteras
  (1593354a), Kalamata (1593354b), Alianza Valledupar (1549853a) y Crystal
  Palace (1557459a: J. Lerma, que el propio DTP nombraba).
- **Los rotables de la línea, no solo los de arriba:** Recoleta (1632056b,
  cuatro sin fila y Masi asistió), The Strongest (1645539b), Union St. Gilloise
  (1558676a: Sykes, sin fila, hizo el gol). Son del cambio 6.
- **Antes de dar un titular por «sin fila» o por baja, se cruza la
  identidad:**
  - Levadiakos (1593352b): el «Μόουζες» de la previa griega era Moses David
    Cobnan, con fila.
  - Real Potosí (1645538b): «H. Rojas» se dio de baja por no estar en la hoja y
    entró con el id 546779, que la hoja llama «J. Rojas».

  Va a la app (A4).

**Propuesta.** La de la propuesta del 08/11 sin cambios (el orden fijo y sin umbral), más una
línea: **«el recambio probable» de la v1.9 pasa a ser «los candidatos al
puesto»**. Por cada baja o duda de un titular fijo, los que pueden ocupar su
casilla según el rol de la temporada, no solo el que nombra la previa. El tope
de 14-16 no se sube como número: la tabla crece solo con quien puede jugar hoy.

**Calculable (A1, A2).** El recibo del depósito avisa de los titulares sin
fila y de las bajas que están en la hoja. `f1/{id}` trae `onceOficial` con la
fila lista y, por cada baja, los candidatos por rol (`rolSugerido` y
titularidades en esa casilla del grid).

**Qué NO:** subir el tope de filas, ni escribir otra regla para algo que la
v1.9 ya escribe.

**Núcleo / historial.** Núcleo: el orden del rehacer (cinco renglones) en «Reglas
que no se negocian» del `SKILL.md` y en el bloque F1 de la rúbrica. Historial:
los casos.

**Se sostiene si** los ~50 veredictos pendientes del 08-09/11 traen más
`ONCE-SIN-FILA-F1` con el parte rehecho. **Lo tumba si** no traen ninguno con
el once a la vista: entonces lo de la propuesta del 08/11 era un pico y alcanza con A1.

**Comprobación 10/11 (71 lecciones nuevas):** **SOSTIENE, y es el grupo más grande del segundo
corte.** 21 lecciones de 18 partidos en la tabla F1 (8 / 4 / 9). En 20 lados
(17 partidos) el parte se rehízo o se depositó con el once a la vista y quedaron
titulares sin fila (`ONCE-SIN-FILA-F1`). Con el primer corte son **31 lados de
27 partidos desde el 07/11**: no era un pico.
- **El que quedó sin fila decidió el partido en 8 de los 20:** Huracán
  (1493228b, Barticciotto hizo el 0-2), Lanús (1493232b, Moreno asistió el
  empate), Universidad de Concepción (1505561a, I. González asistió el 2-0),
  O'Higgins (1505561b, Moreira hizo el 1-2), Cajamarca (1549549a, Timaná hizo
  el 1-0), Tolima (1549857a, Flórez hizo el 2-1), Fortaleza (1549858a,
  Ramírez, el lateral que entró por Medina Obando, hizo el autogol del 0-2) y
  Newell's (1493236b, W. Núñez empató).
- **Sin umbral:** en 18 de los 20 lados faltaban 1 o 2 filas, debajo del «con 3
  o más» del aviso. Los de una sola fila: Ñublense (1505558a), Cobresal
  (1505560b), Audax Italiano (1505555a), Coquimbo (1505555b), Unión La Calera
  (1505562a), Sporting Cristal (1549545b), Sarmiento (1493240b), Los Chankas
  (1549551a), Tolima, Fortaleza y Newell's. Solo Estudiantes de Río Cuarto
  (1493237b, cuatro) e Instituto (1493236a, tres) pasaban el corte.
- **Lo que la prosa nombra, sin fila** (el pendiente de A2): Coquimbo (Dixon
  Pereira, el rematador de la matriz), Cobresal (Astudillo, nombrado en el
  DTP), Sarmiento (G. Díaz, nombrado en el DTP) y Sport Huancayo (1549546b:
  Murillo, la alternativa de la señal del once, y Labrador, el de la rama de
  expulsión).
- **Los candidatos al puesto** (la línea nueva del cambio): Newell's (la duda
  «Mazzantti o Núñez»: el que arrancó no tenía fila y el otro dio vuelta el
  partido desde el banco), Universidad de Concepción («el recambio probable
  del 4-1-4-1 tenía que estar en la tabla») y Once Caldas (1549861a, en
  cuarentena que enseña: el recambio de cada titular fijo de banda).
- **El B6 en el rehacer:** Estudiantes de Río Cuarto, con el arquero Gualtieri
  entre los cuatro sin fila y B6 sin re-puntuar (cambio 4).
- **El tiempo:** Los Chankas re-depositó 5 minutos después de capturado el once
  (17:41 → 17:46), Audax 13 minutos después (15:02 → 15:15) y Fortaleza tenía
  el once a 6 minutos del pitazo. Con esos márgenes la F1 a mano no llega: va
  al cambio 13 y es el argumento de la recomendación de la **1068** (pregunta 2
  de «Preguntas para el usuario»: la (c), con la (b) primero).

---

### 2. El sistema se verifica con el once: con D1 🔶 o un DT que todavía prueba, D1, H y la zona del ausente van condicionados — era el 08/11-2 · [rúbrica] [DECIDE USUARIO en el alcance]

**Qué dice hoy.** D1 puntúa el sistema base de más de 6 meses. Con T.54 de ≤ 2
partidos, B6 y F van condicionados al once (v1.9). Nada condiciona el sistema ni
el H.

**Lo que dijo la propuesta del 08/11.** Con D1 🔶 o T.54 de ≤ 2 partidos, D1, H, la zona de
cada baja y la F3 por zona se escriben en las dos variantes, o «condicionados al
once». El once de la API antes del pitazo es nivel B y manda el último grid. Un
H que acertó el resultado con otro sistema queda «mecanismo no verificado».
Casos: Alavés 1570450, Panetolikos 1593350, Defensor 1646900, São Paulo 1492448,
Danubio 1646902 y Atlas 1551032.

**Lo que traen las lecciones nuevas: lo refuerzan y lo estiran.**
- **Genk (1558676b):** Thorup lleva cuatro meses (T.54, pero no «de ≤ 2
  partidos»). Pasó a línea de tres con un central recién llegado sin minutos.
  B y F se puntuaron sobre otro equipo, y Genk no remató al arco.
- **Cercle (TDE 1558675b, `lectura_efe`):** en el debut de Caixinha salió un
  3-4-2-1 que la apertura no tenía.
- **Lyon (1552812b):** el interino, en su último partido, repitió el 4-3-3 y
  rotó cinco piezas.

**Propuesta.** La de la propuesta del 08/11, con una decisión de alcance:
- **(a)** como la propuesta del 08/11: D1 🔶 o T.54 de ≤ 2 partidos;
- **(b)** estirarla a **T.54 con la serie del DT más corta que la ventana de
  validación (6-8 partidos)**, que es el corte que la v1.7 ya usa para ampliar
  el rango.

La (b) cubre a Genk. Usa un corte que ya existe, así que no es un número nuevo,
pero condiciona más partes.

**Calculable, en parte.** El sistema del once sale del grid
(`f1_base._lineas_por_grid`). El largo de la serie del DT sale de `dt.desde` y
de los partidos de la base. Lo que no se calcula es si el sistema cambió
respecto del D1 declarado, porque D1 es texto.

**Qué NO:** bajar D1 por alternar. 🔶 es 🔶.

**Núcleo / historial.** Núcleo: una línea en «Cuando no hay XI confirmado»,
punto 6. Historial: los casos.

**Se sostiene si** aparecen otros cambios de sistema con un DT de menos de 6-8
partidos. **Lo tumba si** los DT con T.54 repiten el sistema del D1 en casi
todos los partidos nuevos: entonces queda la (a).

**Comprobación 10/11 (71 lecciones nuevas):** **SIN CASOS.** Ninguna de las 71 trae un sistema
distinto del D1 declarado ni un H acertado con otro sistema. Lo más cerca no es
del sistema: Universidad de Chile (1505560a, Gago suspendido y Coloccini en el
banco, con el modelo intacto: no movió la clasificación) y Ñublense (1505558a,
el interino en su tercer partido, con T.54 leída como confianza en la K). La
elección entre (a) y (b) queda con los casos del primer corte (Genk).

---

### 3. EJE-DEBUTANTE: con el once se lee la línea entera del grid, y «condicional» con el once a la vista no vale — era el 08/11-3 · [rúbrica] [CALCULABLE→app] [DECIDE USUARIO tras la comprobación]

**Qué dice hoy (v1.9).** Sin once, va condicional. Con el once, se declara o se
descarta con el grid.

**Lo que dijo la propuesta del 08/11.** Con el once, el chequeo va sobre la línea entera
(línea de fondo y doble pivote), no sobre la pareja nombrada. Con el once a la
vista, la alerta no queda condicional. Con el once a menos de 20 minutos, se
escribe «once tardío, sin verificar».

**Lo que traen las lecciones nuevas: lo refuerzan.** El grupo tiene 71
lecciones (38 aciertos, 17 parciales y 16 fallos). Del 08/11 en adelante son 18
(11 / 3 / 4).
- **Condicional con el once a la vista** (otra vez la regla 2 de la v1.9 sin
  aplicar):
  - Barcelona (1570443b): rehecho a las 19:45 con el grid, siguió condicional
    sobre Eric García, que arrancó en el banco.
  - Atromitos (1593356b): Ofori, Zuber y Serginho salieron juntos.
  - Rio Ave (1575541a).
  - Chivas (1551037b): el condicional de Romo se cumplió y no se declaró.
- **La pareja nombrada no era la que jugó:** Brujas (1558672a), con Tsawa y no
  Lemaréchal.
- **Lo que no tiene regla todavía:** el eje descartado al pitazo puede volver
  por un cambio.
  - León (1551037a): Mora, descartado con el grid, entró al 67 y la línea
    rearmada concedió a los dos minutos.
  - Chivas (1551037b): el 1-1 llegó después de rearmar la línea con Rey.
  - Anderlecht (1558672b): el eje nuevo duró 45 minutos.

  Son dos partidos: va como nota y candidato, no como regla.

**Propuesta.** La de la propuesta del 08/11 sin cambios. Se suma una nota de candidato: «con
un banco que trae al titular descartado, la caja dice que el eje puede volver
por un cambio» (León–Chivas).

**Calculable (A2).** `parejasNuevas` sobre el once oficial (hoy solo sobre el XI
de referencia, `dtp_cowork.py`) y los avisos `EJE-DEBUTANTE-SIN-DECLARAR`,
`-SIN-OBJETO` y la alerta condicional con el once capturado.

**Qué NO:** darle peso ni hacerla vía de gol.

**Núcleo / historial.** Núcleo: la regla del eje en «Reglas que no se negocian»
(una línea cambia). Historial: casos y candidato.

**Se sostiene si** siguen apareciendo condicionales con el once capturado.
**Lo tumba si** no aparece ninguno en los veredictos pendientes, que fueron con
la v1.9.

**Comprobación 10/11 (71 lecciones nuevas):** **MATIZA: la mitad del cambio se queda sin casos.**
Hay 7 lecciones de EJE-DEBUTANTE (3 / 1 / 3), y en todas la alerta se verificó
con el grid, como manda la v1.9:
- **Declarada con el once y cumplida:** Argentinos (1493228a, la pareja
  Mendoza–Godoy confirmada en el grid, con la DEF en rojo: perdió 0-2), Talleres
  (1493239a, S. Fernández–Riquelme: concedió el único gol en un cierre al
  segundo palo), Huachipato (1505562b, la línea de tres sin partidos juntos: 16
  remates y 1,44 de xG en contra) y Alianza Lima (1549551b, 19 remates y 1,67
  de xG, pero el gol no fue por la vía aérea escrita).
- **Amplió el rango y no se pagó:** Palestino (1505557b) y Guabirá (1645537a).
- **Condicional verificado con el grid:** Atlético Tucumán (1493229b).

**Ningún condicional con el once a la vista**, que es lo que el «Se sostiene»
pedía. Por su propia línea, la frase «condicional con el once a la vista no
vale» queda apoyada solo en los 4 casos del primer corte (Barcelona, Atromitos,
Rio Ave y Chivas). No es que la regla falle: es la regla 2 de la v1.9, y en
este corte se cumplió. **Cómo queda el cambio:**
- se queda la línea entera del grid (línea de fondo y doble pivote);
- se queda «once tardío, sin verificar» con el once a menos de 20 minutos, que
  el cambio 13 extiende a la F1;
- la frase del condicional **no se reescribe**: la v1.9 ya la dice, y el
  refuerzo pasa al aviso de la app (A2, la alerta condicional con el once
  capturado). [DECIDE USUARIO: sacar la frase o dejarla como refuerzo.]

**Candidato nuevo (1 caso):** Atlético Tucumán. El debutante decidió en el área
rival («la alerta mide el riesgo defensivo, no su cara ofensiva»).

---

### 4. B6 y el arquero: sin fuente es sin dato, la base cuenta como fuente, y el suplente sin rodaje es una vía a vigilar — era el 08/11-4 · [rúbrica] [CALCULABLE→app]

**Qué dice hoy.** La v1.9 escribe dos frases que chocan: «el suplente sin
rodaje se declara al DTP como vía del rival» y «el suplente de emergencia sin
antecedentes de error no es una vía de gol».

**Lo que dijo la propuesta del 08/11.**
- B6 sin fuente es `sin dato`, y las titularidades de la base son fuente.
- Con el once, B6 se calcula sobre el arquero de la hoja.
- El suplente sin rodaje es «vía a vigilar»: es vía firme solo con
  GK-FALLA-ACTIVA o con errores documentados.

En la cuenta de la propuesta del 08/11 había 1 caso a favor de la vía (Gremio, por el
rechace) y 5 en contra.

**Lo que traen las lecciones nuevas: lo sostienen, con un caso a favor de la
vía.**
- **A favor de la vía:** Aucas (1639803a). GK-DOWNGRADE se declaró al rehacer
  con Chaves, de un partido en el año, por el titular al banco. Independiente
  del Valle convirtió 4 de 4 remates al arco, sin una atajada. Quedan **2 a
  favor** (Gremio y Aucas).
- **En contra o sin probar:**
  - Chelsea (1557466b): el único gol fue un penal.
  - PAOK (1593357b): el arco sin dueño, con 4 atajadas.
  - OFI (1593356a): el rival no remató al arco.
  - Jaguares (1549859a): el riesgo vino de una roja al 9', no del nivel.
  - Como (1550191b): GK-DOWNGRADE sin probar.
- **B6 ✅ sostuvo:** Levante (1570444b): Ryan hizo 9 paradas.

**Propuesta.** La de la propuesta del 08/11 sin cambios. Con Aucas, la frase dice: «vía a
vigilar: amplía el rango, y con GK-DOWNGRADE declarado la caja nombra la pelota
parada y el remate al arco como lo que se le cae».

**Calculable (A2).** Quién ataja hoy ya lo calcula `backend/analisis/arquero.py`
(`arquero_suplente`, usado por los reventones). El rehacer del DTP ya avisa
«arquero: X ataja hoy y no estaba en el XI de referencia (revisar el B6 del
EFE)». Falta el aviso al EFE: el arquero de la hoja no es el del B6.

**Qué NO:** tocar el ×1,5 de F2c, el umbral de 15 partidos ni el de ≥ 2 errores.

**Núcleo / historial.** Núcleo: el párrafo del suplente sin rodaje, que reemplaza
a los dos de la v1.9 que chocan. Historial: la cuenta de casos.

**Se sostiene si** la vía firme por error del arquero aparece en menos de 3
partidos sin GK-FALLA-ACTIVA. **Lo tumba si** aparece en 3 o más (lo que la propuesta del 08/11
ya ponía en «Cuándo se reabre»).

**Comprobación 10/11 (71 lecciones nuevas):** **SOSTIENE.** No hay ninguna vía firme por error del
arquero sin GK-FALLA-ACTIVA (lo tumbaba con 3 o más). En 6 lecciones del arco:
- **El suplente sin errores documentados no fue vía de gol:**
  - Universidad Católica (1505559a): Melo, con B6 🔶 y sin GK-DOWNGRADE por su
    recorrido, dejó la valla invicta con 3 atajadas.
  - Tolima (1549857a): Ortega, suplente con 5 titularidades, hizo 3 atajadas y
    recibió uno contra 0,66 de xG. La lección escribe la frase del cambio: «se
    declara como duda de confianza, no como vía de gol del rival».
  - Comerciantes Unidos (1549547b): el arco alternado de B6 🔶 no anticipó
    nada. Córdova hizo 5 atajadas decisivas: «la alternancia mide continuidad,
    no rendimiento».
- **Sin fuente es sin dato:** Deportes Limache (1505559b). Dutra, con B6 sin
  dato, recibió tres con 4 atajadas y no fue el mecanismo. El sin dato no hacía
  falta convertirlo en alerta.
- **La vía firme con errores documentados se cumplió:** Independiente
  Rivadavia (1493234b). Con GK-FALLA-ACTIVA, a Bolcato se le escurrió el 1-0:
  tercer error con gol en seis partidos.
- **El arquero de la hoja:** Estudiantes de Río Cuarto (1493237b). Gualtieri,
  sin fila, y B6 sin re-puntuar con el once (cambio 1).

Cuenta: siguen **2 a favor** de la vía sin GK-FALLA-ACTIVA (Gremio y Aucas).
En contra o sin probar se suman 3 (Melo, Ortega y Córdova).

---

### 5. La sanción calculada de la base: la roja es Baja con su rama, el ciclo de amarillas es probable — era el 08/11-5, con una corrección · [rúbrica] [DECIDE USUARIO] [CALCULABLE→app]

**Qué dice hoy (v1.9).** «La sanción calculada de la base es nivel 1… le gana a
una previa.»

**Lo que dijo la propuesta del 08/11.**
- La roja de la misma competición es nivel 1.
- El ciclo de amarillas es `probable` y va como Duda, con su rama.
- La sanción de otra competición no saca al jugador.
- La sanción de varios partidos la trae la prensa.

Los tres falsos sancionados de UEFA eran la regla vieja, y ya se corrigió en
`backend/sanciones.py` el 08/11.

**Lo que traen las lecciones nuevas: desmienten en parte la roja como nivel
1.**
- **Kortrijk (1558673b):** Ndjeungoue, dado de baja por la roja del 04/11
  calculada por la base y sin ninguna prensa que la confirmara, **fue
  titular**. La cadena, el DTP y la matriz se apoyaban en «la zaga sin
  Ndjeungoue». La lección pide cargarla como Duda con rama.
- **En la propuesta del 08/11:** la roja acertó en Cusco (1549550) y Antwerp (1558671).
- **Quedan 2 a favor y 1 en contra.** Puede ser un dato mal leído: una roja de
  copa (la regla general dice que no suspende en la liga), una sanción anulada
  o una tarjeta mal atribuida. Hay que verificarlo antes de mover la regla (A3).

**La contradicción, para el usuario:**
- La v1.9 dice que la sanción de la base es nivel 1 y le gana a la previa.
- La propuesta del 08/11 dejaba en nivel 1 solo la roja.
- Kortrijk pide bajar también la roja cuando nadie la confirma.

**Propuesta (elegir una):**
- **(a)** la roja sigue en nivel 1 y va como ❌ Baja, **con la rama «si juega»
  en la caja de sensibilidad cuando ninguna fuente de nivel 1-3 la confirma**.
  La prosa (DTP, matriz) no se apoya en la baja sin decir la rama. Es lo menos
  que se afloja.
- **(b)** la roja sin confirmación de prensa va como ⚠️ Duda, como el ciclo.
  Es lo que pide la lección, y se apoya en un solo caso.

Esta propuesta recomienda la (a) hasta que A3 diga qué pasó en Kortrijk. El
resto de la propuesta del 08/11 sigue igual: el ciclo como Duda, la sanción de otra
competición no saca al jugador y la de varias fechas la trae la prensa.

**Calculable (A3).** Hoy **todo** sale con `certeza: probable` en
`backend/sanciones.py` (la roja, la doble amarilla y el ciclo). Que la roja de
la misma competición salga `segura` y el ciclo `probable`. Que la alerta
`SANCION-SIN-DECLARAR` diga «baja con rama» o «duda con rama» según cada caso.

**Qué NO:** sacar la sanción calculada del F1.

**Núcleo / historial.** Núcleo: la línea de la jerarquía en las dos direcciones
del `SKILL.md`. Historial: los casos de UEFA y de Kortrijk.

**Se sostiene si** A3 encuentra que la roja de Kortrijk era de otra competición
o se anuló, o si en los veredictos pendientes otra roja calculada se cumple.
**Lo tumba si** aparece otra roja de la misma competición, bien leída, cuyo
jugador juega: entonces la (b).

**Comprobación 10/11 (71 lecciones nuevas):** **SIN CASOS.** Melgar (1549548a, Tandazo suspendido)
y Juan Pablo II (1549548b, Flores sancionado) nombran sanciones que se
cumplieron, pero no dicen si salieron de la base o de la prensa, y no hay
ninguna roja calculada cuyo jugador haya jugado. Kortrijk sigue siendo el único
caso en contra. La recomendación (a) y A3 quedan como están.

---

### 6. La rama «once alternativo»: se abre por un hecho (calendario, anuncio o costumbre del DT) y carga a los rotables de todas las líneas; la F3 de una rotación elegida es F4 — era el 08/11-6, con un agregado · [rúbrica] [CALCULABLE→app] [DECIDE USUARIO]

**Qué dice hoy.** Con una eliminatoria a ≤ 5 días o el 3.er partido en 8 días,
la rama se abre y el porcentaje queda «condicionado al once» (v1.7).

**Lo que dijo la propuesta del 08/11.** La rama también la abren:
- una rotación anunciada;
- un DT que rota de costumbre;
- un equipo sin nada en juego.

Además:
- «viajó el plantel completo» es nivel C;
- la rotación elegida va a F4 y no infla la F3;
- la rama nombra la dosificación en vivo.

**Lo que traen las lecciones nuevas: refuerzan el recomputo y relativizan el
calendario solo.**
- **El recomputo no se hizo:** Lyon (1552812b, `lectura_efe`). Se declaró
  «condicionado al once», salió con cinco cambios y al rehacer solo se reescribió
  el DTP: B y F quedaron con el 55,8 % del once tipo. Es
  `EFE-RECOMPUTO-PENDIENTE` (A2), que sigue sin existir.
- **Los rotables sin fila:** Recoleta (1632056b), The Strongest (1645539b,
  Terrazas, un lateral juvenil: «la rama debía nombrar a los rotables de la
  línea de fondo, no solo a los de arriba») y Union St. Gilloise (1558676a,
  Sykes).
- **El calendario exigente sin rotación:**
  - OFI (1593356a): tercer partido en 8 días con el once habitual.
  - Brighton (1557458a): repitió el once del Etihad.
  - Juventus (1550189b): no rotó y no bajó el volumen.
  - Freiburg (1575216a): salió el once de liga.

  Con los de la propuesta del 08/11 (Arsenal, Excelsior y Libertad) son **7 partidos con
  calendario exigente y sin rotación**. Del otro lado, la rotación se dio en
  Celta (1570444a), Hoffenheim (1575215a), Union St. Gilloise y Lyon, y en la
  propuesta del 08/11 en Carabobo, Universidad Católica, Atlético-MG y Guaraní. En el TDE,
  Stuttgart (1575214a) no rotó y cedió la pelota con la ventaja.

**Propuesta.** La de la propuesta del 08/11, más dos líneas:
1. **La rama carga a los rotables de todas las líneas** que el calendario toca,
   no solo a los de arriba (The Strongest).
2. **El porcentaje «condicionado al once» por calendario se apoya en la
   costumbre del DT** con ese calendario: lo que rotó en sus últimas ventanas
   cortas. Si el DT repite el once con calendario exigente (OFI, Brighton), la
   rama va en la caja sin condicionar el porcentaje.

   **Esto afloja la regla de la v1.7**, que condiciona siempre con el
   calendario, y por eso lo decide el usuario. Va con ⚠️ medir primero: cuántas
   veces rota el DT en ventanas cortas lo calcula la app (A8). Sin esa medición
   se queda como en la v1.7.

**Calculable (A2, A8).** `EFE-RECOMPUTO-PENDIENTE` y la costumbre de rotación
por DT: cambios en el once en partidos con ≤ 3 días de descanso, sacados de las
alineaciones.

**Qué NO:** abrir la rama por defecto, ni condicionar por una sospecha.

**Núcleo / historial.** Núcleo: el punto 6 de «Cuando no hay XI confirmado».
Historial: los casos.

**Se sostiene si** en los veredictos pendientes los DT con costumbre de repetir
el once vuelven a repetirlo con el calendario exigente. **Lo tumba si** la mitad
o más de esos DT rotan: entonces el calendario solo sigue bastando para
condicionar.

**Comprobación 10/11 (71 lecciones nuevas):** **SOSTIENE 6.1 y el recomputo; TUMBA 6.2 tal como
está escrito.** 4 lecciones en el grupo de la rama y 4 más que la citan desde
la tabla F1.
- **Los rotables, con fila (6.1):**
  - Instituto (1493236a): un líder ya clasificado, al que el empate le daba el
    primer puesto, rotó de verdad. La rama de la caja ya lo nombraba («Flores
    rota más titulares pensando en octavos»). Acevedo, Bravo y Meli salieron
    titulares sin fila y tres titulares fijos fueron al banco. Es el «equipo
    sin nada en juego» de la propuesta del 08/11.
  - O'Higgins (1505561b): la caja anticipó la rotación por la final, y Moreira
    y Movillo quedaron sin fila. Moreira hizo el 1-2.
  - Once Caldas (1549861a, cuarentena que enseña): semifinal de Copa a 3 días;
    faltó el recambio de cada titular fijo de banda.
- **El recomputo (`EFE-RECOMPUTO-PENDIENTE`, A2), en las dos direcciones:**
  - Atlético Tucumán (1493229b): cuatro titulares fijos al banco y B quedó en
    4,5 sin cambio.
  - Atlético Nacional (1549855a): la caja anticipó el once rotado exacto por la
    semifinal de Copa a 3 días; «con ≥ 3 rotados, B y F se recomputan».
  - **La rama que NO se cumple también recompone:** Estudiantes de La Plata
    (1493239b). El porcentaje y la F3 se condicionaron a la rotación, el once
    trajo a los titulares (Castro, Piovi, Burgos y T. Palacios) y B, F y la F3
    quedaron colgando. **Línea nueva dentro del cambio** (sin regla aparte):
    «con el once oficial, el condicionado se levanta en las dos direcciones: B
    y F se recomputan con el once que salió, haya rotado o no».
- **La rotación elegida no es debilidad** (la F3 elegida va a F4): Atlético
  Tucumán. «El once rotado se puso 2-0 con goles del debutante.»
- **6.2, en contra de aflojar.** Con calendario exigente rotaron 4 de 5:
  Universidad de Chile (1505560a, 3.er partido en 8 días, la rama se cumplió con
  la hoja), Atlético Nacional, O'Higgins y Once Caldas. No rotó Estudiantes de
  La Plata. Ninguna lección dice la costumbre previa del DT, así que la línea
  del «Se sostiene» no se puede leer al pie de la letra. Pero en este corte el
  calendario solo sí anunció la rotación. Con los dos cortes y la propuesta del
  08/11 son **12 partidos con rotación y 8 sin rotación**: la mitad o más
  rotó, que es lo que la tumba.
- **Cómo queda:** 6.2 sale del cambio. Se queda la v1.7 (el calendario
  condiciona siempre), y A8 (la costumbre de rotación por DT) sigue como
  medición, sin regla atada. Se reabre si A8 muestra DT que repiten el once en
  la mayoría de sus ventanas cortas. [DECIDE USUARIO]

---

### 7. La F3 por la zona DEF se lee en lo concedido, y el marcador lo decide el arquero — nuevo · [rúbrica]

**Qué dice hoy (v1.9, la tabla de la F3 por zona).** DEF en 🔴 anuncia «**la
vía del rival** (penal, pelota parada, el carril del reconvertido), **no el
volumen**».

**Lo medido.** El grupo F3 tiene 65 lecciones (39 aciertos, 12 parciales y 14
fallos). Del 08/11 en adelante son 22 (13 / 6 / 3). En las nuevas, la zona DEF
degradada **se vio en el volumen concedido**, y el marcador lo sostuvo el
arquero:
- Atalanta (1550192b), sin Kristensen, Hien ni Kossounou: 22 remates y 1,42
  de xG concedidos. El arco quedó en cero con B6 ✅.
- Fenerbahçe (1584459b): 22 remates y 2,00 de xG. Ederson sostuvo.
- Gent (1558673a), con Volckaert reconvertido de central: 7 remates al arco y
  un penal. La valla la sostuvo el arquero.
- Real Sociedad (1570449a): la pareja rearmada, con 1,39 de xG en contra y
  Remiro atajando los tres remates al arco.
- Hoffenheim (1575215a), con la zaga rearmada (DEF en ámbar al 21 % e IP
  rojo): 23 remates en contra, 18 dentro del área, y ganó.
- Milan (1550190b): 1,22 de xG en contra y 5 atajadas de Maignan.
- **Donde sí concedió:** Manchester United (1557464a, cuatro, dos en los
  primeros cuatro minutos) y Alianza Valledupar (1549853a, dos y un penal).
- **La vía del rival de la v1.9 sigue valiendo:** AEK (1593352a), con el 0-1
  por la espalda del lateral de recambio.

**Propuesta.** La fila DEF de la tabla pasa a decir: «**la vía del rival y el
volumen concedido**; si el gol llega o no lo decide sobre todo el arquero. Con
B6 ✅ la nota nombra al arquero como el sostén y el riesgo como volumen
concedido, no como goles». **Esto corrige el «no el volumen» de la v1.9**,
que sale de casos que no concedieron en juego abierto (Coventry, Portuguesa,
Monagas): no concedieron goles, que no es lo mismo que no conceder volumen.

**Calculable, en parte.** El xG y los remates en contra los tiene la ficha. El
cierre del veredicto puede medir la F3 DEF por el volumen concedido sin
pedírselo al modelo.

**Qué NO:** mover el 40 % ni el rojo de zona.

**Núcleo / historial.** Núcleo: la fila DEF de la tabla de la F3. Historial: los
casos.

**Se sostiene si** en los veredictos pendientes las zonas DEF en rojo conceden
volumen (remates, xG) por encima de lo habitual del rival, sea cual sea el
marcador. **Lo tumba si** las zonas DEF en rojo no conceden más volumen que las
verdes.

**Comprobación 10/11 (71 lecciones nuevas):** **MATIZA: la DEF en rojo se pagó en el volumen o en la
vía, no en los dos a la vez.**
- **En el volumen:** Alianza Lima (1549551b), sin R. Garcés ni Huamán y con la
  pareja Advíncula–Antoni sin partidos juntos. Concedió 19 remates y 1,67 de
  xG, el peor volumen en contra de la mejor defensa del año, y el gol no fue
  por la vía aérea escrita.
- **En la vía, sin volumen:** Sporting Cristal (1549545b), sin Araujo, Cris
  Silva ni Lutiger. ADT generó 0,55 de xG y el gol fue la vía de la v1.9:
  pelota parada aérea a un central contra la pareja rearmada.
- **Sin dato de volumen:** Argentinos (1493228a, DEF al 42,9 %, perdió 0-2).
- **En la línea, fuera del grupo F3:** Huachipato (1505562b, EJE en una línea de
  tres) concedió 16 remates y 1,44 de xG.

**Cómo queda la fila:** «**la vía del rival o el volumen concedido** (uno, el
otro o los dos); si el gol llega o no lo decide sobre todo el arquero». Es
«o», no «y». Corrige igual el «no el volumen» de la v1.9 (Alianza Lima), sin
borrar la vía (Cristal). Ningún caso nuevo de B6 ✅ sosteniendo una DEF en
rojo: la parte del arquero sigue con los casos del primer corte.

---

### 8. La F3 en ATK y MID: el ataque degradado se paga en volumen, en dónde se remata o en la conversión, y con un recambio que ya juega no anuncia nada — nuevo (sube una nota de la propuesta del 08/11) · [rúbrica]

**Qué dice hoy (v1.9).** ATK en 🔴 anuncia «menos volumen y xG propios». MID en
🔴 anuncia «esterilidad propia». Con un recambio de oficio con minutos, la zona
queda «degradada, cubierta de oficio».

**Lo medido.**
- **Se pagó en dónde se remata o en la conversión, no en el volumen:**
  - Ameliano (1632061b): 55 % de pelota y 15 remates, pero 10 de afuera y 0,93
    de xG.
  - Celta (1570444a), sin Borja Iglesias: 23 remates, 8 al arco y ningún gol.
  - En la propuesta del 08/11 (nota): San Lorenzo (1493238) y Mirassol (1492443).
- **Se pagó en el volumen, como dice la v1.9:** Angers (1552810a, 0,70 de xG
  en 88 minutos persiguiendo), The Strongest (1645539b, 0,39 de xG) y Union
  Berlin (1575216b, ningún remate al arco).
- **Con un recambio que ya juega, la zona no se degradó:**
  - Bayern (1635622b, `lectura_efe`): Karl, Olise y Davies de extremo, con
    minutos en la temporada. 19 remates y 1,79 de xG.
  - Inter (1550191a): Esposito por Lautaro marcó al 12'.
  - Gil Vicente (1575542b): Walace de 9 y Murilo, la pieza de transición ya
    titular, hicieron los dos goles.
  - Llaneros (1549853b): los recambios, sin fila, sostuvieron el ataque.

  Es el «cubierta de oficio» de la v1.9, que no se aplicó.
- **El MID reducido leído como estéril sin estar en rojo:** Universidad Católica
  (1639805b), con la zona MID en verde al 17,6 %. El parte la leyó estéril y el
  doble pivote asistió los dos goles. Es «MID reducido, eje entero» (v1.8), sin
  aplicar.

**Propuesta.**
1. La fila ATK pasa a decir: «**menos peligro propio**, que se ve en el volumen,
   **en dónde se remata** (de afuera) **o en la conversión**».
2. **La F3 de ATK o de MID solo anuncia** si la zona está en 🔴 **y** el
   recambio no tiene minutos en la temporada en esa casilla. Con un recambio con
   rodaje, la nota dice «cubierta de oficio» y la F3 es solo confianza en la K.
   No es una regla nueva: es la de la v1.9 puesta en la misma fila, para que no
   se lea por separado.

**Calculable, en parte.** Las titularidades del recambio en esa línea del grid
ya salen de `f1/{id}`. La proporción de remates de afuera la tiene la ficha.

**Qué NO:** tocar los cortes de zona.

**Núcleo / historial.** Núcleo: las filas ATK y MID de la tabla. Historial: los
casos.

**Se sostiene si** las zonas ATK en rojo con recambio sin rodaje generan menos
peligro, por cualquiera de las tres vías, que las cubiertas de oficio. **Lo
tumba si** no hay diferencia entre una y otra.

**Comprobación 10/11 (71 lecciones nuevas):** **SOSTIENE las tres vías, con un matiz; la parte del
recambio con rodaje queda sin probar.**
- **ATK en rojo:**
  - Everton de Viña (1505556a), sin Montiel: 18 remates, 10 de afuera, 0,88 de
    xG y ningún gol. Es dónde se remata, como Ameliano.
  - Fortaleza (1549858a): 2 remates al arco y 0,40 de xG. Es el volumen, como
    en la v1.9.
  - Huracán (1493228b) tuvo la ATK en rojo y aun así generó 1,78 de xG con dos
    goles. Con la roja rival al 25', no se puso a prueba en igualdad: no
    cuenta.
- **MID en rojo:** Cienciano (1549546a), sin Souza ni Hohberg (MID al 46 %). El
  volumen no cayó (2,1 de xG). Faltó la pelota parada de Souza: 8 córners sin
  gol. Es la conversión, y dice algo más: **lo que se pierde es lo que hacía el
  ausente** (1 caso: candidato, no regla).
- **Cubierta de oficio, sin anuncio:** Melgar (1549548a, Zegarra cubrió la
  mediapunta y la F3 bajó la confianza sin cambiar el lado) y La Serena
  (1505557a, sin Mac Allister ni Figueroa, generó más que Palestino).
- **La F3 como confianza:** Lanús (1493232b, con el medio titular lesionado no
  le ganó al colista).

Las lecciones no dicen si el recambio tenía minutos en esa casilla, así que la
comparación que pide el «Se sostiene» (rojo sin rodaje contra cubierta de
oficio) sigue sin medir. Va a la parte calculable del cambio.

---

### 9. La baja de un titular fijo con recambio sin minutos se nombra como vía del rival aunque la zona quede en ámbar — nuevo (sube una nota de la propuesta del 08/11) · [rúbrica] [DECIDE USUARIO: regla o nota]

**Qué dice hoy.** «Toda zona **en rojo** dice quién la cubre» (v1.9). La propuesta del 08/11 lo
dejó como nota para el ámbar, con Lens (1635681): la reducción DEF dio 28,6 %
con Aguilar reconvertido, y concedió nueve.

**Lo medido.**
- **AEK (1593352a):** reducción DEF del 26,9 %, en ámbar, por la sanción de Rota,
  un titular fijo. El 0-1 llegó por la espalda del lateral de recambio, que
  salió al descanso.
- **Como (1635681):** la zona no se nombró y el generador jugaba en otra línea.
- **En la otra dirección:** Lille (DTP 1635640b) muestra que la línea rehecha
  puede salir limpia. La vía es eso, una vía: amplía el rango.

**Propuesta.** «La baja de un titular fijo cuyo recambio no tiene minutos en esa
casilla se nombra **como vía del rival** (al DTP), aunque la zona quede en
ámbar.» Son dos casos (Lens y AEK). Si el usuario prefiere esperar a un tercero,
queda como nota.

**Calculable.** El recambio sin minutos en la casilla sale de `f1/{id}`.

**Qué NO:** cambiar el corte del ámbar.

**Núcleo / historial.** Núcleo: una línea bajo «Toda zona en rojo dice quién la
cubre». Historial: Lens y AEK.

**Se sostiene si** aparece un tercer caso de ámbar con un recambio sin minutos
por el que llegó el gol. **Lo tumba si** los ámbar con recambio sin minutos no
conceden por esa casilla.

**Comprobación 10/11 (71 lecciones nuevas):** **SIN CASOS.** Ninguna lección nombra una zona en
ámbar. Fortaleza (1549858a) se parece: el lateral que entró por Medina Obando,
sin fila, hizo el autogol. Pero la lección no da la zona, y el problema que
nombra es la fila (cambio 1). Siguen siendo dos casos (Lens y AEK).
**Recomendación:** nota hasta el tercero.

---

### 10. La tabla F1 dice quién arranca en el banco, y B5 nombra el banco por rol: el titular habitual en el banco, la duda que va al banco y el que vuelve — nuevo · [rúbrica] [CALCULABLE→app]

**Qué dice hoy.** B5 puntúa «≥ 2 suplentes capaces de cambiar el partido», con
impacto documentado (v1.6 a v1.9). Un titular que el DT nuevo manda al banco es
profundidad (v1.8). La tabla F1 no dice quién arranca en el banco.

**Lo medido** (es el insumo del EFE que más aparece en las lecciones
`lectura_efe` del DTP y del TDE):
- **«Banco corto» con el banco lleno:**
  - Heerenveen (DTP 1552221a): el parte escribió «banco corto» y nombró a Oyen y
    Farji. Meerveld, del XI de referencia, arrancó suplente, entró al 46' e hizo
    tres.
  - Riestra (DTP 1493235b): empató con Díaz y T. González, del banco.
  - Independiente (efe-dashboard 1493235a): la palanca del reloj llevaba dos
    nombres y el que decidió, Tempone, no estaba.
- **La Duda que va al banco es banco ofensivo, no ausencia:** Le Mans (EFE
  1552814a, y TDE 1552814a): Colas, en duda por un agregador, fue al banco y
  empató al 90'.
- **El banco en todas las ramas:** Utrecht (DTP 1552214b: Alarcón, escrito
  «para la última media hora», entró al 37'), Köln (TDE 1575207b), Always Ready
  (TDE 1645536a: un titular nombrado como banco) y Manchester United (DTP
  1557464a: Zirkzee y Dorgu empataron).
- **B5 con impacto, confirmado:** Betis (1570445b: los dos goles con firma de
  suplentes), Olympiakos (1593357a: el que entró al 56' marcó al 58') y UCV
  Moquegua (1549553b: Dávila y Angulo entraron al 73' y Angulo convirtió el 2-2).
  Se suman a la nota de la propuesta del 08/11 sobre B5 con dos partidos (Famalicão, San
  Lorenzo de Paraguay y siete más).

**Propuesta.**
1. **En la tabla F1, la columna Estado admite `banco probable`**: el titular
   habitual que rota, la Duda que puede ir al banco y el que vuelve de lesión.
   No es una columna nueva ni un número.
2. **B5 nombra el banco por rol** (quién entra para qué), no solo por nombre.
   Esa lista es la que toman el DTP (banco ofensivo), el TDE (ramas) y la matriz
   (palanca del reloj). Ninguno de esos skills la arma de nuevo con dos nombres.
3. **«Banco corto» solo con la tabla mirada entera:** no hay ningún titular
   habitual, ninguna Duda y ningún suplente con impacto documentado que pueda
   entrar.

**Calculable (A8).** Con el once oficial, los titulares habituales que están en
el banco de la hoja (titularidades contra el banco de hoy) salen de la base.
Antes del once, los suplentes con goles o asistencias desde el banco en la
temporada salen de los eventos.

**Qué NO:** subir B5 a ✅ con un solo partido de banco decisivo (v1.9), ni
convertir «dos partidos» en umbral de puntuación sin la decisión del usuario
(nota de la propuesta del 08/11).

**Núcleo / historial.** Núcleo: los tres renglones bajo B5 y la mención en el
bloque F1. Historial: los casos de los otros skills.

**Se sostiene si** en los veredictos pendientes el banco que decide estaba en la
tabla F1 como titular habitual, Duda o suplente con impacto. **Lo tumba si** el
banco que decide es casi siempre un suplente sin historia, que ninguna tabla
habría nombrado.

**Comprobación 10/11 (71 lecciones nuevas):** **SOSTIENE.** En todos los casos nuevos, el banco que
decidió se podía nombrar desde la F1:
- **El titular habitual en el banco:**
  - Banfield (1493229a): Machado, del XI tipo, estaba en el banco con la duda
    «profundidad o dependencia». Entró al descanso e hizo el 1-2, y el B5 🔶
    «sin impacto decisivo nombrado» suma un caso.
  - Instituto (1493236a): Tissera, titular rotado al banco, empató en el 90+3.
  - Atlético Nacional (1549855a): James fue al banco, y lo rescató Tesillo,
    suplente, al 89'. De Tesillo la lección no dice la historia.
- **La Duda que va al banco:**
  - Concepción (1505556b): J. Henríquez, en duda sin motivo y fuera del once
    anterior, fue al banco y marcó a los 12 minutos de entrar. «Un titular del
    F1 rotado al banco es profundidad de B5, no baja.»
  - Newell's (1493236b, `lectura_efe`): Mazzantti, la duda de la señal del
    once, entró al 78' e hizo el 2-1.
- **El suplente con impacto documentado:**
  - Boca (1493231a): B5 ✅ por Villa y Paredes, y el gol lo hizo un suplente.
  - Deportivo Pereira (1549855b): dos de sus tres goles salieron de suplentes.
  - Independiente Medellín (1549858b): Jackson Martínez, FACTOR-X, asistió
    desde el banco.

Ningún caso de un suplente sin historia que ninguna tabla habría nombrado.

---

### 11. D3 con T.54 y una serie corta: la nota dice cuántos casos tiene, y con pocos el ❌ o el ✅ firme va con caja — nuevo · [MEDIR PRIMERO] [DECIDE USUARIO]

**Qué dice hoy.**
- **v1.6:** T.54 descuenta lo heredado y respeta la serie del DT nuevo.
- **v1.7:** la serie más corta que la ventana de validación (6-8) amplía el
  rango.
- **v1.9:** «la nota del D3 dice cuántos casos y qué cara».

**Lo medido.**
- **Estrela (1575538a, `lectura_efe`):** D3 ❌ apoyado en tres casos de local de
  la serie del DT nuevo. Igualó dos veces desde abajo ante el líder.
- **Macará (1639805a):** el D3 ✅ de local se apoyaba solo en casos de sostener,
  y remontó de 0-2 a 2-2 en cuatro minutos. Es la otra cara de la escala.
- En el grupo D3/D4/C/E hay 28 lecciones (9 / 10 / 9).

**Propuesta.** Con T.54 y menos casos de la cara que se evalúa que la ventana de
validación, D3 se puntúa como dice la tabla y **lleva la caja de sensibilidad
con la otra cara**. Pasarlo a 🔶 cambiaría un sub-score, que es un número, y
eso **no entra sin medir**: hay que saber cuánto acierta un D3 apoyado en 1-3
casos contra uno apoyado en 6 o más.

**Calculable (A7) y cómo se mide.** «Recibió primero y recuperó puntos», por
condición y desde `dt.desde`, sale de `fixture_eventos` (minuto de cada gol).
La app puede dar la base del D3 (casos y cara) y medir su acierto por tamaño de
muestra contra el partido siguiente. Recién con eso se decide.

**Qué NO:** mover D3 sin la medición.

**Núcleo / historial.** Núcleo: una línea en el bloque D. Historial: Estrela y
Macará.

**Se sostiene si** la medición de A7 muestra que el D3 de 1-3 casos acierta
claramente menos que el de 6 o más. **Lo tumba si** acierta lo mismo.

**Comprobación 10/11 (71 lecciones nuevas):** **SIN CASOS para la serie corta.** Deportivo Pereira
(1549855b): el D3 de visita, «reacciona sin remontar», quedó corto, porque
reaccionó del 1-2 al 3-2. Pero la lección no dice si había T.54 ni cuántos casos
tenía el D3. Entra a la medición A7 como un dato más y no mueve el cambio.

---

### 12. La brecha en la misma base: ¿ordena al ganador más probable? — nuevo · [MEDIR PRIMERO]

**Qué dice hoy (v1.9, nota).** «La brecha en la misma base ordena al ganador
más probable, no el dominio, ni descarta el empate.»

**Lo medido.**
- **En contra:**
  - En la propuesta del 08/11: Göztepe (1584463) y Getafe–Sevilla (1570438).
  - Groningen–AZ (1552224b): 75,5 contra 60,4, sin T.54 y en la misma base.
    Ordenó al revés.
  - Atlético–Barcelona (1570443a): el 91,7 % de local perdió contra el 78,7 %.
  - Brentford–Brighton (1557458b): el 85 % no se tradujo en puntos.
- **A favor:** Trinidense–Ameliano (1632061a: 73,1 contra 47,0, 3-0).

Son 5 en contra y 1 a favor, contados en las lecciones, que son las que se
escriben cuando algo llama la atención.

**Propuesta.** **No se cambia el texto hasta medirlo** (A6). Si la tasa del de
mayor porcentaje en la misma base no supera a la del favorito del mercado, la
nota pasa a «mide cuánto creerle a la señal de cada uno, no ordena al ganador»,
que es lo que dicen las lecciones de Atlético y de Groningen. **Sería aflojar
una nota vigente**, y se dice así.

**Calculable (A6).** La app tiene los dos porcentajes, la alerta y el resultado.

**Núcleo / historial.** Núcleo: la nota de la brecha. Historial: los casos.

**Se sostiene si** A6 muestra que el de mayor porcentaje en la misma base gana
más de lo que da su cuota. **Lo tumba si** no.

**Comprobación 10/11 (71 lecciones nuevas):** **MATIZA a favor, con un caso.** Universidad Católica–
Deportes Limache (1505559a): 79,8 contra 68,4, en la misma liga y sin T.54 ni
R-KT.2. La brecha ordenó al ganador, como se declaró, sin leerse como dominio.
Quedan **5 en contra y 2 a favor** (Trinidense y Universidad Católica). La
Serena–Palestino (1505557a, 57,7 contra 70,3) no cuenta: la brecha se apoyaba
en indicadores sin dato. Sigue en [MEDIR PRIMERO] (A6).

---

### 13. Once tardío: con el once a menos de 20 minutos del pitazo, la F1 no se da por rehecha — nuevo (segundo corte) · [rúbrica] [CALCULABLE→app]

**Qué dice hoy.** La v1.9 no dice nada del tiempo. El cambio 3 escribe «once
tardío, sin verificar» solo para EJE-DEBUTANTE, con el once a menos de 20
minutos.

**Lo medido (segundo corte).** Dos partidos en los que la lección dice que el
once llegó tarde, y la F1 quedó con titulares sin fila:
- **Fortaleza–Independiente Medellín (1549858a):** el once estaba a 6 minutos
  del pitazo, «no hubo tiempo de rehacer la tabla». Ramírez, el lateral sin
  fila que entró por Medina Obando, hizo el autogol del 0-2.
- **Instituto–Newell's (1493236a y b):** «DTP-REHACER tardío: el once llegó
  tarde, apertura caída». Quedaron tres titulares sin fila en Instituto y W.
  Núñez sin fila en Newell's, y Núñez empató.
- **Cerca, sin la palabra «tardío»:** Los Chankas (1549551a) re-depositó 5
  minutos después de capturado el once, y Audax Italiano (1505555a) 13
  minutos después. En los dos quedó una fila sin hacer.

**Propuesta.** «Con el once a menos de 20 minutos del pitazo, el parte rehecho
no da la tabla F1 por cerrada. Escribe **"once tardío: F1 sin verificar"**, y el
IP y la F que salen de la tabla vieja se leen como de otro equipo. No se
inventa la fila a mano con apuro: la pone la app (A1, opción (b) de la 1068).»
Es el «once tardío» del cambio 3, llevado a la F1. El corte de 20 minutos ya
está en ese cambio, así que no es un número nuevo.

**Calculable (A1).** La app sabe a qué hora se capturó el once y a qué hora
llegó el depósito. Puede marcar `onceTardio` en el recibo y sumar la fila del
titular que falta.

**Qué NO:** demorar el depósito, ni dar el EFE por rehecho cuando solo se
rehízo el DTP.

**Núcleo / historial.** Núcleo: una línea junto al orden del rehacer
(cambio 1). Historial: Fortaleza e Instituto–Newell's.

**Se sostiene si**, con el aviso de A1 al depositar, los partes con once tardío
siguen dejando titulares sin fila. **Lo tumba si** el aviso alcanza para cerrar
la F1 aun con el once a pocos minutos: entonces sobra la marca y alcanza con
A1.

**Comprobación 10/11 (71 lecciones nuevas):** sale de este corte (Fortaleza
1549858 e Instituto–Newell's 1493236). Ninguno de los dos está entre los cuatro
casos sin la cuarentena que les toca.

## Matices que no son cambio (se escriben como nota)

- **El cansancio del calendario pesa al final y contra los cambios, no desde el
  pitazo:** Getafe (1570452b, dos días después de la Conference). El bloque
  aguantó hasta el 80 y cedió con el banco fresco del rival. Es un caso, y es
  más del TDE (F2) que del EFE.
- **G-BLOQUE acertó el desgaste tardío, no su ventana:** Iraklis (1593355b).
  Es un caso.
- **La regla especial B describió al equipo que jugó:** Pasto (1549862b, con el
  plantel profesional en paro).
- **La caja nombró la pieza que decidió:** Groningen (1552224b). La caja decía
  «Vaessen vuelve a fallar en la salida» y el arquero terminó expulsado con el
  penal decisivo. No se afirma el mecanismo sin crónica.
- **COLAPSO + AGRAVANTE, D3-DEGRADADO y «la brecha con la confianza efectiva»
  siguen candidatos.**
  - Para la confianza efectiva, Santa Clara (1575542a) suma a favor: F3 en MID
    y GK a la vez, y concedió 20 remates. Independiente del Valle (1639803b)
    suma en contra: F3 en MID y la brecha de 89 contra 49 ordenó igual. Quedan
    4 a favor y 2 en contra.
  - Los otros dos no traen casos nuevos.
- **Candidatos del segundo corte (1 caso cada uno, no son regla):**
  - **EJE-DEBUTANTE mide el riesgo defensivo, no la cara ofensiva:** Atlético
    Tucumán (1493229b), donde el debutante decidió en el área rival.
  - **La F3 del ausente es lo que él hacía:** Cienciano (1549546a). Sin Souza,
    el volumen no cayó, pero se perdió la pelota parada: 8 córners sin gol.
  - **Un DT suspendido, con el modelo intacto, no mueve la clasificación:**
    Universidad de Chile (1505560a, Gago suspendido y Coloccini en el banco).
    Va con `dt.banco`.
  - **La fecha del DT con la hoja sin DT y `/coachs` rancio sale de la prensa
    del cambio:** Once Caldas (1549861a, en cuarentena que enseña). Herrera se
    fue el 26/09 y dirigía el interino Valencia. Va con A5.
  - **G-BLOQUE describe la vida útil del bloque rival, no garantiza que el
    banco del favorito genere:** Académico Viseu (1575540b).
  - **El arco alternado es continuidad, no rendimiento:** Comerciantes Unidos
    (1549547b, cambio 4).
- **Lo que quedó de la propuesta del 08/11 como nota, sin cambios:** B5 con dos partidos, el
  recambio de oficio que sostuvo la zona, el DT que se verifica en cada parte
  (Kasımpaşa, A5), D4 con lo que se juega, la K por condición contra otra
  escala, el bloque H de Leeds–Tottenham y FACTOR-X.

## `efe-dashboard` v1.12 → v1.13

**Dossier:** 2 lecciones pendientes, las dos acertadas y ninguna fallada (la
revisión del dashboard no se abrió sola).
- **Konyaspor (1584455, 30/10):** la goleada como rama de «Para perder». **Ya
  está en la v1.12** (punto 2). La lección quedó pendiente porque no se
  pulsaron los botones de «Cerrar las anteriores». Se marca aplicada.
- **Independiente (1493235, 06/11):** la palanca del reloj lleva el banco
  entero de la tabla F1. Es nueva y va con el cambio 10.

**Cambios (sin números, sin tocar la banda de goleada):**
- **D1. Lo que dibuja la caja de sensibilidad.** Era lo opcional de la propuesta del 08/11:
  las dos variantes del sistema (cambio 2) y la rama abierta por anuncio o
  costumbre (cambio 6), con los rotables de todas las líneas.
- **D2. La palanca del reloj y el banco de la matriz salen del banco probable
  de la tabla F1** (cambio 10), no de los dos nombres más conocidos
  (Independiente: Tempone).
- **D3. La nota F3 del dashboard copia las filas nuevas de la tabla:** DEF,
  volumen concedido y el arquero (cambio 7); ATK, dónde se remata (cambio 8).
- **D4. La descripción** pasa a «EFE v1.10 (skill v1.13)» (número decidido por el usuario el 10/11).
- **Banda de goleada:** sigue sin números. Ninguna lección nueva la toca.

**Núcleo / historial del dashboard.** Las notas v1.7 a v1.12 pasan a
`references/HISTORIAL.md`. Las dos reglas que hoy viven solo en las notas
(`NUCLEO_SKILLS_propuesta.md` §2.4) se copian al núcleo antes de mover:
- **D1:** el suplente con impacto desde el banco es factor X. Encaja con el
  cambio 10.
- **D2:** el once probable es nivel C.

## Núcleo e historial

No se aplica acá (`NUCLEO_SKILLS_propuesta.md` espera la decisión del usuario).
Si se aplica junto con esta revisión:

| Va al NÚCLEO (`SKILL.md` o el cuerpo de la rúbrica) | Va al HISTORIAL (`references/HISTORIAL.md`) |
|---|---|
| El orden del rehacer con el once, con la F1 primero, y la baja que está en la hoja (1) | Los partidos de cada cambio, con sus conteos |
| Los candidatos al puesto en la F1 (1) | El changelog v1.4 a v1.9 de la rúbrica (líneas 5-57) |
| El sistema condicionado con D1 🔶 o T.54 corta (2) | El apéndice de casos de validación (Estudiantes y Junior) |
| La línea entera del grid y la alerta sin condicional con el once (3) | La cuenta «a favor / en contra» del suplente sin rodaje (4), de la roja (5) y de la rotación (6) |
| El suplente sin rodaje como vía a vigilar (4) | Los candidatos: COLAPSO + AGRAVANTE, D3-DEGRADADO, la confianza efectiva y el eje que vuelve por un cambio |
| La roja con rama y el ciclo como Duda (5) | La lectura de `lectura_efe` en los otros skills (esta propuesta) |
| La rama por hecho, con los rotables de todas las líneas, y la F3 elegida como F4 (6) | |
| Las filas DEF, ATK y MID de la tabla de la F3 (7, 8) | |
| La vía del rival en ámbar (9), si se aprueba como regla | |
| `banco probable` en la F1 y B5 por rol (10) | |
| La caja del D3 con pocos casos (11) | |
| El once tardío: la F1 sin verificar (13) | |

La cabecera de la rúbrica todavía dice «aplicar el **EFE v1.7**» (DEUDA 21). Se
corrige al aplicar.

## Para la app, no para el skill

Ordenado por cuántas lecciones cierra. Ninguno toca el motor ni un peso. El
estado de cada uno se verificó con grep en `backend/` el 10/11, sobre
`60ba263`.

**A0. La etiqueta `lectura_efe` de Jev** · [DECIDE USUARIO]
- **Qué pasa hoy:** junta la lectura de tres skills (ver la sección de arriba).
- **Opciones:**
  - **(a)** renombrarla a `lectura` («la rúbrica del skill se aplicó mal»),
    porque el dossier ya es por skill;
  - **(b)** sumar `lectura_dtp` y `lectura_tde`.
- **El costo:** la taxonomía es CERRADA (`modo_fallo.py`) y lo que Jev ya
  respondió está sellado: lo viejo no se re-etiqueta. Mientras tanto, el dossier
  del EFE podría contar aparte las `lectura_efe` de otros skills cuya
  `reglaTocada` nombra un insumo del EFE (F1, B5, EJE, rotación), que es la
  cuenta que hizo esta propuesta a mano.

**A1. La tabla F1 contra el once, al depositar** (cambio 1) · **sin hacer**
- **El aviso al leer:** `ONCE-SIN-FILA-F1` sale solo al leer, y su texto todavía
  dice «con 3 o más» (`parte.py`, línea ~4544).
- **El recibo:** no hay `BAJA-EN-LA-HOJA` ni `onceOficial` en `f1/{id}`.
- **Lo que hay:** `faltan` avisa de un jugador de `fuera` nombrado como banco
  (`fuera_en_el_banco`, 1051). Es la dirección contraria y sirve de molde.
- **Para decidir:** que la app sume la fila del titular que falta. Es la
  incidencia **1068**, junto con el modo `rehacer` que no carga el EFE (cambio
  1).

**A2. Lo pendiente de la v1.9** (`PENDIENTES.md`):

| Pendiente | Estado | Casos de esta tanda |
|---|---|---|
| `EFE-RECOMPUTO-PENDIENTE` | sin hacer (sin rastro en `backend/`) | Lyon 1552812, LDU 1639804 |
| `EJE-DEBUTANTE-SIN-DECLARAR` y `-SIN-OBJETO` | sin hacer: `parejasNuevas` solo va sobre el XI de referencia (`dtp_cowork.py`) | Barcelona 1570443, Atromitos 1593356, Rio Ave 1575541 y Chivas 1551037, con el condicional y el once capturado |
| El `recambio` en `f1/{id}` | sin hacer (no hay campo). Lo que hay: dos arqueros siempre (`arqueroDeReserva`, 986) y `rolSugerido` | se pide como «candidatos al puesto» (cambio 1) |
| Los nombres de la prosa sin fila F1 | sin hacer | Crystal Palace 1557459 (Lerma, en el DTP) y UCV Moquegua 1549553 (D. Ramírez) |
| El arquero del día | en parte. `arquero.py` sabe quién ataja hoy (`arquero_suplente`, para los reventones) y el rehacer del DTP avisa «arquero: X ataja hoy…». Falta el aviso al EFE: el arquero de la hoja no es el del B6 | Oriente Petrolero 1645540 (atajó Torrez y no Bernal) y Aucas 1639803 |

**A3. Sanciones** (cambio 5) · **sin hacer**
- **Hoy:** todo sale con `certeza: probable` (`sanciones.py`).
- **Se propone:** la roja de la misma competición `segura`; el ciclo
  `probable`; y que `SANCION-SIN-DECLARAR` diga «baja con rama» o «duda con
  rama».
- **Incidencia a verificar:** Kortrijk–Gent (1558673). ¿La roja de Ndjeungoue
  del 04/11 era de liga o de copa? ¿Se anuló? ¿Era otro jugador?

**A4. Identidad** (`backend/identidad.py` + `test_identidad`)
- **Pendientes de la propuesta del 08/11, a verificar:** Mateusinho (Vitória 1492449), los ids
  cruzados de Botafogo (1492441), Pittón (Unión 1493241) y Leones del Norte
  (1639858).
- **Nuevos:**
  - Levadiakos (1593352): el nombre de la previa en griego («Μόουζες») no se
    cruzó con Moses David Cobnan. Hay que transliterar antes de cruzar.
  - Real Potosí (1645538): «H. Rojas» de la tabla contra el id 546779 de la hoja
    («J. Rojas», «Hugo Rojas» en el evento). Hay que cruzar el banco por id
    antes de dar de baja a un titular fijo.

**A5. El DT del parte contra el de la base** (Kasımpaşa 1584462, propuesta del 08/11). Ya hay
algo: el recibo avisa del DT sin antigüedad (1326) y el `desde` sin la llegada
vista no completa la antigüedad (1338). Falta verificar si eso habría hecho
sonar el caso.

**A6. Las mediciones de la brecha y menos lecciones de confirmación** (cambio 12).
- **Qué medir:** la tasa del de mayor porcentaje con y sin
  `EFE-EMPATE-TECNICO`, y en la misma base contra la cuota.
- **Después de medir:** el modo `veredictos` deja de escribir una lección por
  cada «empate técnico declarado y cumplido» (138 de 568). Es un cambio de la
  corrida y lo decide el usuario.

**A7. La base del D3, calculada** (cambio 11) · **nuevo**. Los casos de
«recibió primero» por condición dentro de la serie del DT, y la cara de cada
uno (recuperó, sostuvo o no recuperó), desde `fixture_eventos` y `dt.desde`.
Con eso se mide el acierto del D3 por tamaño de muestra.

**A8. La costumbre de rotación y el banco probable** (cambios 6 y 10) · **nuevo**
- Por DT, los cambios en el once en sus partidos con ≤ 3 días de descanso.
- Con el once oficial, los titulares habituales que arrancan en el banco.
- Antes del once, los suplentes con goles o asistencias desde el banco en la
  temporada.

Las alertas nuevas que salgan de A1 a A8 van en `_ALERTAS_CALCULADAS`, en
`docs/openapi.yaml` (`test_arquitectura` lo exige) y en `test_cowork`. Lo que no
se haga queda en `PENDIENTES.md`.

## Lo que no cambia

- **Los pesos y la tabla de puntuación:** A 1×, B 1,5×, C 1×, D 1× y E 2×; el
  máximo de 27 y 23; los cortes 70/40; las reglas especiales B y D3.
- **La F3** (IP > 7, ≥ 2 titulares fijos o una zona > 40 %), los cortes de zona,
  el ×1,5 de F2c, los 15 partidos de B6 y de GK-DOWNGRADE, y los ≥ 2 errores de
  GK-FALLA-ACTIVA.
- **Las reglas vigentes:** el empate técnico de formación (v1.7) y su cálculo;
  T.54 y T.54-B con la fecha del DT (v1.8); COLAPSO EN CASCADA describe y no
  predice; EJE-DEBUTANTE y FACTOR-X sin peso.
- **Lo que calcula la app:** total, porcentaje, clasificación, IP, reducción por
  zona, F3, F4, el bloque F por el once y el bloque G. Un bloque sin puntuar no
  es cero.

## Lo que NO se propone y por qué

- **Ningún peso, máximo, corte ni multiplicador.** Ninguna lección lo pide y
  Jev no marcó ninguna (`lectura` del dossier: «la revisión fija rúbrica; un
  cambio de peso no tiene quien lo sostenga»).
- **Mover D3 a 🔶 con pocos casos** (cambio 11), **aflojar la nota de la
  brecha en la misma base** (12) **ni condicionar el porcentaje por la costumbre
  del DT** (6.2) sin medir.
- **Volver regla un candidato:** COLAPSO + AGRAVANTE, D3-DEGRADADO, la confianza
  efectiva o el eje que vuelve por un cambio.
- **Bajar la roja calculada a Duda** solo por Kortrijk (cambio 5, opción b) sin
  verificar el caso.
- **Leer `lectura_efe` como el error más grande del EFE.** No lo es: ver la
  sección de arriba.
- **Números en la banda de goleada del dashboard.**

## Cuándo se reabre

- **La tabla F1 (1):** si con el aviso al depositar (A1) los titulares sin fila
  siguen apareciendo en más de 5 partidos por semana, la app suma la fila sola
  (1068).
- **La roja (5):** cuando A3 diga qué pasó en Kortrijk.
- **La rotación por costumbre (6.2):** con A8 medido, en 30 o más partidos de
  calendario exigente.
- **El D3 con pocos casos (11):** con A7.
- **La brecha en la misma base (12) y el empate técnico:** con A6.
- **El suplente sin rodaje (4):** con 3 o más partidos en una tanda con la vía
  por error del arquero y sin GK-FALLA-ACTIVA previa.
- **Los candidatos:** con 5 casos de un mismo agravante y su cuenta de
  contraejemplos.

## Cómo se aplica si se aprueba

1. **Skill:**
   - **La rúbrica** pasa a `references/rubrica-efe-v1.10.md`, con
     `git mv` desde la v1.9, y con el changelog de los cambios aprobados.
   - **La cabecera** se corrige (v1.7, DEUDA 21).
   - **`SKILL.md`** cambia la línea del eje (3) y la de la jerarquía (5), y suma
     el orden del rehacer (1), el sistema condicionado (2) y el banco probable
     (10).
   - **Si se aplica el núcleo:** el historial se mueve como dice la tabla de
     arriba.
2. **`efe-dashboard` v1.13:** D1 a D4.
3. **`corrida-sad`:** el modo `rehacer` carga `efe-clasificador` y sigue el orden
   del cambio 1, o se elige la opción (b) de la 1068. Es la decisión que más
   lecciones cierra.
4. **App:** `lecciones.CORTE_VERSION["efe-clasificador"]` suma la versión con su
   fecha, para que «Cerrar las anteriores» cierre estas 568. Después, A0 a A8,
   cada uno con su test.
5. **Zips para subir a la cuenta**, y anotar la hora en `SUBIDA_VERSION`.

## Resumen: qué lecciones toca cada punto

Cada lección cuenta en el grupo de su `reglaTocada`, en el orden de la tabla.
Los partidos se repiten entre grupos. Las cuentas se hicieron sobre el JSON del
dossier del 10/11 (02:13 UTC) y no son una tasa de acierto
(`sesgoDeAtribucion`).

| Grupo · cambio | Lecciones (todas) | A / P / F | Del 08/11 en adelante | A / P / F | Tipo |
|---|---:|---|---:|---|---|
| Tabla F1 y once · 1 (era 08/11-1) | 113 | 53 / 26 / 34 | 28 | 14 / 4 / 10 | rúbrica + app + decide usuario (1068) |
| Sistema D1/H · 2 (era 08/11-2) | 4 | 1 / 1 / 2 | 0 | — | rúbrica, más casos citados de otros grupos y del TDE |
| EJE-DEBUTANTE · 3 (era 08/11-3) | 71 | 38 / 17 / 16 | 18 | 11 / 3 / 4 | rúbrica + app |
| B5, B6 y el arco · 4 (era 08/11-4) y 10 | 42 | 20 / 8 / 14 | 14 | 4 / 2 / 8 | rúbrica + app |
| Sanción · 5 (era 08/11-5) | 8 | 2 / 3 / 3 | 1 | 1 / 0 / 0 | decide usuario + app |
| Rama once alternativo · 6 (era 08/11-6) | 21 | 11 / 3 / 7 | 6 | 3 / 0 / 3 | rúbrica + medir + app |
| F3 por zona · 7, 8 y 9 | 65 | 39 / 12 / 14 | 22 | 13 / 6 / 3 | rúbrica |
| Brecha y empate técnico · 12 | 138 | 67 / 23 / 48 | 40 | 21 / 7 / 12 | medir (A6) |
| T.54 / T.54-B | 24 | 13 / 4 / 7 | 7 | 4 / 0 / 3 | sin cambio (alimenta el 2) |
| COLAPSO EN CASCADA | 27 | 12 / 12 / 3 | 5 | 1 / 4 / 0 | sin cambio |
| D3, D4, C y E · 11 | 28 | 9 / 10 / 9 | 6 | 2 / 3 / 1 | medir (A7) |
| Jerarquía de fuentes | 15 | 8 / 2 / 5 | 3 | 1 / 1 / 1 | sin cambio |
| FACTOR-X y G-BLOQUE | 5 | 2 / 3 / 0 | 2 | 1 / 1 / 0 | sin cambio |
| Otros | 7 | 3 / 2 / 2 | 0 | — | notas |
| **Total** | **568** | **278 / 126 / 164** | **152** | **76 / 31 / 45** | |

Fuera de esta tabla, 88 lecciones pendientes de otros skills con `lectura_efe`
(39 del TDE, 46 del DTP y 3 del EFE, que están arriba) se leyeron para el
cambio 10 y para A0. Además, 2 lecciones de `efe-dashboard`.

## Preguntas para el usuario

1. **El número:** decidido: v1.10 (usuario, 10/11).
2. **La 1068 (sin decidir): ¿cómo se cierra la tabla F1 cuando sale el once?**
   - **(a)** El modo `rehacer` de `corrida-sad` carga `efe-clasificador` y hace
     el orden del cambio 1: F1, bajas de la hoja, B6, EJE, B y F, D1 y H.
   - **(b)** La app suma la fila del titular que falta, con su `rolSugerido`, y
     la marca «agregada por la app» (A1). La corrida no carga nada nuevo.
   - **(c)** Las dos cosas.

   **Recomendación: la (c), en dos pasos y con la (b) primero.**
   - **Por qué la (b) primero:**
     - En los dos cortes hay 31 lados (27 partidos) con el once a la vista y
       titulares sin fila desde el 07/11.
     - En el segundo corte, 18 de los 20 lados tenían 1 o 2 filas de menos.
       Eso es cruzar dos listas y poner el rol, lo mismo que hace `xi/auto`
       con el bloque F, y la regla del proyecto dice que lo calculable lo hace
       la app.
     - No es cosmético: en 8 de esos 20 lados, el que no tenía fila hizo o
       asistió un gol.
     - El tiempo juega en contra de la (a): re-depósitos a 5 y a 13 minutos de
       capturado el once (Los Chankas y Audax), y onces a 6 minutos del pitazo
       (Fortaleza). Un rehacer que además carga el EFE cuesta más tokens y
       llega igual de tarde.
   - **Por qué la (a) también, pero acotada:** la (b) no re-puntúa B ni B6,
     que son juicio. Eso pasó en Estudiantes de Río Cuarto (el arquero sin fila
     y B6 sin re-puntuar), Instituto (tres sin fila y tres titulares fijos al
     banco), Atlético Tucumán (cuatro titulares fijos al banco y B quieto en
     4,5) y Atlético Nacional, más Lyon en el primer corte. Son 5 de unos 30
     partidos. La (a) se dispara solo cuando la app marca 3 o más titulares
     fijos distintos del XI de referencia, o un arquero distinto. Es el corte
     que la v1.9 ya usa para recomputar, así que no hay número nuevo.
3. **El cambio 3:** ¿se saca la frase del condicional (sin casos nuevos, queda
   en A2) o se deja como refuerzo?
3-bis. **El cambio 2:** ¿el sistema condicionado solo con T.54 de ≤ 2 partidos, o
   con toda serie más corta que la ventana de validación?
4. **El cambio 5:** ¿la roja sin confirmación va como Baja con rama (a) o como
   Duda (b)?
5. **El cambio 6.2:** la comprobación lo tumba (12 partidos con rotación contra
   8 sin rotación con calendario exigente). ¿Se saca, y queda la v1.7 con A8
   solo como medición?
6. **El cambio 9:** ¿regla con dos casos o nota hasta el tercero? El segundo
   corte no trajo ninguno: la recomendación es la nota.
7. **A0:** ¿se separa la etiqueta `lectura_efe` de Jev?
