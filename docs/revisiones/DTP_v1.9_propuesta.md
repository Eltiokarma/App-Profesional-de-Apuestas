# Propuesta de revisión · `diagnostico-tactico` v1.8 → v1.9

> **APROBADA por el usuario el 17/11/2026, con todas las recomendaciones.** 1. la presión alta con su vuelta sube a regla · 2. se borra la condición de la l. 314: «arriba» siempre aparte · 3. bloque «Candidatos abiertos» en el cuerpo. Lo demás, como recomienda la propuesta (punto 8 a medición).

**Estado: PROPUESTA (17/11/2026), pendiente de aprobación punto por punto.**
No se tocó `docs/skills/diagnostico-tactico/SKILL.md` ni código. Se aplica
**junto con el núcleo** (`NUCLEO_SKILLS_propuesta.md`, aprobado con las cinco
recomendaciones de su resumen y todavía sin aplicar). Las líneas citadas son
de la **v1.8 de hoy (512 líneas), antes de mover el historial**.

**Base:** el estudio del 17/11 (`estudio_lecciones_2026-11-17/README.md`,
`estudio_diagnostico-tactico.md`, `clasif_diagnostico-tactico.json`) y la
prosa de las **347 lecciones pendientes** de 81 partidos del 10 al 16/11,
todas posteriores a la v1.8. **59 lecciones (15 partidos) son de copa
nacional** (Bolivia 1649146-49, Copa AUF 1649432-33, Copa Colombia
1648690-91, Copa del Rey 1644xxx): enseñan, pero no acreditan. Quedan **288
acreditables**: 161 sostuvo, 78 mal aplicada, 33 regla falló, 12 insumo, 3
imprevisto, 1 no dice. **La muestra es de una semana y la mayoría son
selecciones** (fecha FIFA del 12 al 16/11): donde un patrón sale solo de
selecciones, se dice.

## 0. Resumen

- La v1.8 **se sostiene**: 2,4 lecciones mal aplicadas por cada regla que
  falló, y **0 fallos heredados del EFE**. Lo que más se repite es no cumplir
  una regla que ya está escrita, casi siempre porque el once oficial no se
  propaga. La app ya hizo hoy lo principal (`bancoProbable` y el rehacer por
  la hoja).
- **Tienen material:** la posesión por rama (12 de 12 mal aplicadas), dos
  candidatos que llegan al umbral (el reconvertido también ataca y la presión
  alta con su vuelta), la materia de la pelota parada desde el cruce, el 9
  titular en la lista de penales con la base corta y una lista de salida de
  `viasGol`.
- **Ningún número se mueve.** La banda de «parejo» (14 de los 20 veredictos
  de rama que fallaron eran NEUTRO que el volumen decidió) va a medición.
- Con el núcleo, dos reglas que hoy solo viven en el historial suben al
  cuerpo: P1 (once probable = nivel C) y **P2 (el umbral del arquero, que la
  propuesta del núcleo no había listado)**.

## 1. Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos acreditables (copa aparte) | Recomendación |
|---|---|---|---|---|
| 1 | Posesión: «arriba» **siempre** aparte, y sin referencia, menos pelota que en igualado; el perfil del rival dice de dónde sale (sede, DT, n) | aclaración + app | 12 lecciones en 11 partidos (copa: 0 a favor, 1 en contra) | aprobar |
| 2 | El reconvertido también ataca | candidato que sube a regla | 4 limpios + 2 con reserva (copa: Peña Sport) | aprobar |
| 3 | La presión alta, con su vuelta | candidato que sube a regla | 3, uno nuevo + 1 de apoyo | aprobar (decide el usuario: entra justo en el umbral) |
| 4 | Pelota parada: la materia sale del cruce y se lee por rama | aclaración | 4 + 2 que confirman | aprobar |
| 5 | Con la base corta (0-1 penal), el 9 titular entra en la lista de penales | aclaración | 3 (copa: 2) | aprobar |
| 6 | Lista de salida de `viasGol` (junta lo obligatorio, sin regla nueva) | aclaración de forma | 7 partidos, cada uno con un renglón distinto (copa: 1) | aprobar |
| 7 | Banco, grid y rehacer: el texto nombra lo que la app ya da | app (cumplimiento) | 16 + 8 + 6 lecciones | aprobar los reemplazos |
| 8 | Banda de «parejo» del M5 | candidato a medir | 14 de 20 | medir; no entra |
| 9 | Núcleo: el historial sale; P1 y P2 suben; los candidatos, en un bloque | forma (núcleo) | — | aplicar con el núcleo |

## 2. Los puntos con material

### 1. Posesión: «arriba» siempre aparte, y el perfil dice de dónde sale

**Hoy** (l. 314 y 317): «igualado» y «arriba» van aparte *cuando el foco no
es favorito o puede ponerse arriba temprano*, y el perfil del rival es el de
su condición de hoy. **0 sostenidas y 12 mal aplicadas** (11 partidos; ningún
caso de copa entre las mal aplicadas).

- **(a) Se escribió «igualado o arriba» junto y el foco se puso arriba
  temprano.** En los cinco terminó con 42-48 % de la pelota: Bélgica–Italia
  1528983 (arriba desde el 22', 48 %), Chipre–Montenegro 1528979 (5', 43 %),
  Nacional–Albion 1649060 (16', 46 %), Suecia–Bosnia 1528978 (5', 42 %) y
  Türkiye–Bélgica 1528958 (30', 47 %). La condición «puede ponerse arriba temprano» es justo el juicio que se
  saltea. Los casos de la v1.8 van en la misma dirección (U. Católica: 30 %;
  Panathinaikos: 40 %).
- **(b) El perfil del rival no era el de su condición de hoy:** salió de una
  tasa de resultados (UCV–Grau 1549560: Grau tuvo el 53 %), del volumen de la
  otra sede (JPII–Garcilaso 1549559), de la etiqueta «de visita cede»
  (Belarus–Albania 1528980), del promedio de temporada (Cali–Tolima 1549867:
  57 % de media, 40 % de visita), de un partido de local (Moldavia–Kazajistán
  1528968) o de lo medido con el DT anterior (Italia–Francia 1528960, en los
  dos lados: 35 % y 65 %). La regla de la v1.8 ya lo prohíbe. Lo que falta es que la rama **diga de
  dónde sale** el perfil, para que la falta se vea al escribirlo y la app la
  pueda comprobar.

**Texto propuesto.** Va después de la l. 318 (última viñeta de la «Precisión
v1.8»):

> **Precisión v1.9: «arriba» siempre aparte, y el perfil dice de dónde sale.**
> - La posesión de **«arriba» se escribe siempre aparte** de la de
>   «igualado», sea o no favorito el foco. Decidir si «puede ponerse arriba
>   temprano» fue lo que se salteó. Sin una referencia de ese equipo ganando,
>   la dirección de «arriba» es **menos pelota que en igualado** (Bélgica–Italia:
>   arriba desde el 22', 48 %; Chipre–Montenegro, Nacional–Albion,
>   Suecia–Bosnia y Türkiye–Bélgica: arriba temprano y entre 42 y 47 %).
> - **El perfil de balón del rival dice de dónde sale:** la sede (su posesión
>   de local o de visita), el DT con el que se midió y cuántos partidos (`n`).
>   Si falta uno de los tres, la rama va solo con la dirección y su razón. No
>   son perfil: una tasa de resultados (UCV–Grau), el volumen de la otra sede
>   (JPII–Garcilaso), la etiqueta «de visita cede» (Belarus–Albania), el
>   promedio de temporada (Cali–Tolima), un solo partido (Moldavia–Kazajistán)
>   ni lo medido con el DT anterior (Italia–Francia).
> - Mientras el parte no tenga la rama «arriba» ni esos tres datos como
>   campos, van en la razón de la rama.

Además, en la l. 314 se borra la condición «Cuando el foco no es favorito, o
puede ponerse arriba temprano,». Queda: «La posesión de la rama se escribe en
dos: **igualado** y **arriba**.»

**Qué lo tumbaría:** focos que se pusieron arriba temprano y tuvieron **más**
pelota que en igualado sin una referencia que lo anunciara, o perfiles que
citan sede, DT y `n` y fallan igual. En ese caso es la regla y no su
cumplimiento.

**En contra, anotado (un caso cada uno, no entran):** Suecia–Bosnia
1528978:b (con el favorito 3-0 arriba, el que persigue domina la pelota, 58 %:
el espejo de (a) persiguiendo, candidato) e Independiente Petrolero–Always
Ready 1649146 (copa, ida de llave: el local con interino no tomó la pelota).

### 2. El reconvertido también ataca (de candidato a regla)

**Hoy** (l. 196): candidato desde la v1.7, con dos casos limpios (Leones del
Norte y Telstar–Utrecht 1552214) y Cajamarca 1549549 con reserva. El usuario
lo dejó en candidato el 10/11, a la espera de un tercer caso limpio.

**Casos nuevos, verificados en la prosa:** **Países Bajos–Grecia 1528966**
(Timber, leído como lateral izquierdo reasignado, 2:1, solo por su espalda,
hizo dos goles: 40' y 59'); **Suecia–Bosnia 1528978:a:3** (Svensson, volante
de oficio de lateral derecho, hizo el 1-0 llegando al área; el estudio lo
clasificó en «lateral que llega» y no lo contó acá, pero es la misma cara); y
con reserva **Kosovo–Israel 1528971** (Kamberi, la pieza nueva de la línea
leída como vulnerabilidad, cabezazo al larguero: ocasión y no gol, y la
lección dice «pieza nueva», no «reasignado»).

Son **4 limpios en 4 partidos distintos** (Leones del Norte, Telstar, Países
Bajos y Suecia), sin copa. Con reserva quedan Kosovo y Cajamarca. **Corrección
al estudio:** el estudio contó a Kosovo entre los cuatro; con Suecia en su
lugar el umbral se cumple sin la reserva.

**Texto propuesto.** Reemplaza la viñeta de la l. 196, que empieza con
«*Candidato, no regla (v1.7):* **el reconvertido también ataca**»:

> - **El reconvertido también ataca** *(v1.9; candidato desde la v1.7)*. El
>   rol reasignado se escribe con sus dos caras: la vulnerabilidad en el M1 y,
>   si su puesto de hoy lo lleva al área (lateral que pasa, volante de
>   lateral, central de lateral que sube), **su llegada en las `viasGol` del
>   foco**, con zona. Casos: Leones del Norte (Luque, volante de lateral: los
>   dos goles), Telstar–Utrecht (Martha, lateral de origen de mediapunta:
>   asistió el 2-0 e hizo el 4-2), Países Bajos–Grecia (Timber, leído solo por
>   su espalda: dos goles) y Suecia–Bosnia (Svensson, volante de oficio de
>   lateral: el 1-0 llegando al área). La otra cara no cambia: contra él, el
>   mismatch es vía a verificar (M2, l. 209).

**Qué lo tumbaría:** reasignados escritos con su llegada que no llegan,
mientras la vía de vulnerabilidad sí aparece. Eso diría que la cara ofensiva
es ruido.

### 3. La presión alta, con su vuelta (de candidato a regla, en el umbral)

**Hoy:** es candidato solo en el changelog de la v1.8 (l. 34), con dos casos
(Utrecht–NEC 1552223 y Bodø–Lille 1635640, donde el FAVORABLE apoyado en la
presión a una salida rehecha dio 4 remates y 0,53 de xG). El cuerpo tiene la
quinta línea (el error en la salida bajo presión, l. 212) y no tiene la
vuelta.

**Caso nuevo: España–Inglaterra 1528984:a:4.** El FAVORABLE de igualado
contaba con que Inglaterra presionara (renglón 4, el error en la salida
inglesa), y el contrario escrito era que se cerrara. Pasó una tercera cosa:
Inglaterra presionó y la salida que concedió fue la española (un error de
Zubimendi dejó a Kane al poste, más tres ocasiones en dos minutos;
menorca.info y SI, 15/11).

Apoyo, sin sumar: en Inglaterra–Croacia 1528962 la presión inicial croata
no pasó de 15 minutos (Sky, 12/11). Fuera de esta regla: en Chequia–España
1528961:b:7 el 0-2 nació de una recuperación alta no escrita en la rama con
ventaja; ya lo cubre la transición del favorito (l. 235, (3)). Son **3 partidos distintos y acreditables**, uno nuevo. Llega al umbral
justo, por eso decide el usuario (pregunta 1).

**Texto propuesto.** Va como sub-viñeta debajo de la l. 212 (quinta línea):

> - **La presión alta, con su vuelta** *(v1.9; candidato de la v1.8)*. Una
>   vía o un veredicto que se apoya en presionar alto (la recuperación sobre la
>   salida rival o su error en la salida) escribe también **su vuelta**: qué
>   pasa si la salida rival la supera, qué seguro queda detrás de la línea que
>   salta, y **la presión del rival sobre la salida propia**, que es la misma
>   vía en espejo (Utrecht–NEC; Bodø–Lille: 4 remates y 0,53 de xG; España–
>   Inglaterra: el FAVORABLE contaba con el error en la salida inglesa,
>   Inglaterra presionó y concedió la salida española). Es vía, no certeza.

**Qué lo tumbaría:** presiones altas escritas con su vuelta en las que la
vuelta no aparece y el veredicto se sostiene. En ese caso la vuelta sería un
renglón vacío.

### 4. Pelota parada: la materia sale del cruce y se lee por rama

**Hoy:** la l. 224 (v1.7) pide los córners esperados del cruce, los que saca
el foco y los que concede el rival. La l. 225 (v1.8) dice que el que cede va
condicional por defecto, «salvo que los córners que concede el rival digan
otra cosa». Se aplicó con el promedio propio y sin la rama.

**Casos (4 acreditables, 4 partidos):** Letonia–Armenia 1545616
(condicional por 4,5 córners de media del que cede; sacó 13 contra un rival
que ataca con centros); Luxemburgo–Estonia 1545614 (el que tenía la pelota,
contra un bloque que cerraba: 2 córners en 90 minutos); Nacional–Albion
1649060:b:3 (condicional, 3,0 de media; persiguiendo tuvo el 54 %, sacó 4 y
empató de córner); Llaneros–Chicó 1549870 (un «cede» importado del 42 % de
visita, contra su propia rama de posesión; de local, 63 % y 9 córners).

Confirman la regla vigente, sin materia la rama no se sostiene: Mirassol
1492455 y Defensor 1649062 (0 córners). La contradicción que vio el estudio
(«condicional no es descartada» contra «sin materia no sostiene») se resuelve
así: las dos valen si la materia se lee del cruce y por rama.

**Texto propuesto.** Va como sub-viñeta debajo de la l. 225:

> - **La materia sale del cruce y se lee por rama** *(v1.9, precisa las dos
>   anteriores)*. Mandan **los córners que concede el rival en su condición de
>   hoy**, no el promedio propio, en las dos direcciones (Letonia–Armenia:
>   condicional por 4,5 de media, y sacó 13 contra un rival que ataca con
>   centros). La condicional vale también para **el que tiene la pelota contra
>   un bloque que cierra** (Luxemburgo–Estonia: 2 córners). Se **relee en
>   cada rama**: el «cede» que la decide es el de la rama de posesión del
>   propio M2, y persiguiendo puede dejar de ceder (Nacional–Albion: 54 % y
>   empate de córner; Llaneros–Chicó: «cede» importado de otra sede, y de
>   local 63 % y 9 córners). Sin los córners concedidos en los insumos, se
>   cita la fuente con su `n`.

**Qué lo tumbaría:** cruces con muchos córners concedidos por el rival en los
que la pelota parada no tuvo materia, o al revés, en tres partidos o más.

### 5. Con la base corta, el 9 titular entra en la lista de penales

**Hoy** (l. 217-219): con un solo penal la base no fija al ejecutor, y se
nombran el de la base y el de jerarquía o el lanzador de pelota parada; sin
penales, el lanzador de pelota parada; el 9 del banco, como tercer nombre
«si entra». **El 9 titular no aparece.**

**Casos (3 acreditables, 3 partidos):** Cali–Tolima 1549867 (lista
Chaverra, 1 de 1, y S. Rodríguez, en el banco; pateó Dinenno, el 9 titular,
al 8'); Bulgaria–Islandia 1528969 (lista Óskarsson, 0 de 1, y Gylfi «si
entra»; pateó Guðjohnsen, el otro delantero titular); Italia–Francia 1528960
(sin base, lista Tonali, Barella y F. Esposito «si es el 9»; erró S. Esposito
y convirtió F. Esposito: la lección pide cubrir a los delanteros titulares).

De copa, en la misma dirección y sin acreditar: Boston River–Torque 1649432
(un delantero del banco con goles) y Tarancón–Levante 1644379 (con penales
sin fuente).

Con la base de 1 penal, el de la base pateó en Islandia–Luxemburgo,
Lituania, Bélgica–Italia, Escocia y Progreso. La regla **suma** un nombre,
no reemplaza a nadie.

Chequia–España 1528961 (pateó Baena, el lanzador de córners) es
cumplimiento de la l. 218, no un caso de este punto.

**Texto propuesto.** Va como sub-viñeta nueva debajo de la l. 217:

> - **Con la base corta (0 o 1 penal), el 9 titular entra en la lista
>   siempre** *(v1.9)*, y con dos delanteros, los dos. Se suma al de la base y
>   al lanzador de pelota parada, sin reemplazarlos, y el orden se declara no
>   fijado (Cali–Tolima: pateó Dinenno, el 9 titular, con el de la base 1 de 1
>   en cancha; Bulgaria–Islandia: Guðjohnsen, el otro delantero titular;
>   Italia–Francia: sin base, los dos Esposito).

**Qué lo tumbaría:** listas de cuatro o cinco nombres que siguen sin cubrir
a quien patea. Eso sería diluir la lista sin informar.

### 6. Una lista de salida para `viasGol` (forma, sin regla nueva)

**Hoy:** lo obligatorio en `viasGol` está repartido en seis lugares (l. 211,
212, 213, 224-225, 235 y el banco de la l. 226 en adelante). **8 lecciones
mal aplicadas en 8 partidos, cada una con un renglón distinto que ya estaba
escrito:** la vía aérea en juego abierto (Estonia–Bulgaria 1528988), la
transición del favorito (Chipre–Montenegro 1528979), la pelota sucia a favor
(Albion 1649060), el origen además del rematador (Santa Fe 1549869 e Irlanda
del Norte 1528975, el córner en corto), el lateral que llega (Suecia
1528978), el córner como origen (Escocia 1545659) y el tiro libre directo
(Tavernes–Valencia 1644380, copa).

Nada falla siempre: la lista es larga y se olvida por partes. Con el núcleo,
juntarla es el cambio de forma que corresponde.

**Texto propuesto.** Va debajo de la l. 235, que termina con «no cuenta como
vía en el cierre.»:

> - **Lista de salida de `viasGol`** *(v1.9; no agrega reglas, junta las de la
>   v1.4 a la v1.9)*. Antes de depositar, las vías de **cada lado** se
>   recorren con esta lista, y cada renglón nombra zona o intérprete, o dice
>   «no aplica» con la razón:
>   1. aérea por centro en juego abierto y por pelota parada, con todos los
>      que atacan el área;
>   2. pelota parada con la materia del cruce y su origen (córner en corto,
>      lateral al área, tiro libre directo);
>   3. transición de los dos, también la del favorito;
>   4. error en la salida bajo presión, con su vuelta;
>   5. balón largo a la espalda;
>   6. lado débil y segunda línea (el lateral que llega, el reconvertido y el
>      origen de la jugada, no solo el rematador);
>   7. media distancia con todos sus rematadores;
>   8. pelota sucia del área, a favor y en contra;
>   9. banco de `bancoProbable`, por rol y en todas las ramas;
>   10. lista de penales según la hoja;
>   11. vía de expulsión, de los dos lados.

**Qué lo tumbaría:** que los renglones se llenen con «no aplica» de forma
mecánica y las lecciones del mismo tipo sigan iguales. Ahí el problema no es
la forma.

## 3. Cumplimiento, no regla (punto 7)

Las reglas que más se incumplen ya dicen lo correcto. Cuando se aplicaron,
sostuvieron (en las 16 sostenidas del banco, el banco nombrado marcó). Repetir
el texto no cambió la conducta. Lo que lo cambia es la app, y una parte ya
está hecha hoy.

| Regla (v1.8) | Lecciones mal aplicadas | Qué hace ya la app (17/11) | ¿Línea en el skill? |
|---|---|---|---|
| Banco desde la hoja, por rol, sin titulares (l. 226-233) | 16 en 15 partidos: falta el volante que llega (Estonia, JPII, Montenegro, Vasco, Querétaro–Monterrey), el defensor fresco (UTC, Islandia, España) y el B5 sin heredar (Los Chankas, Dinamarca) | `bancoProbable` en `GET /analisis/cowork/dtp/{id}` (y en `tde` y `f1`). Con el once y la banca completa es la hoja; antes es probable. Trae `lateral` por el grid, goles y asistencias entrando, y el titular habitual primero. FUERA-EN-LA-HOJA (`dtpBanco`, `noConvocado`) avisa del titular o el no convocado nombrado como banco | **Sí:** tres reemplazos que nombran la lista (abajo) |
| M1 · el grid se copia (l. 191) | 8 en 8 partidos: bandas invertidas (Croacia 1528985, Georgia 1528973); rol leído del orden o la etiqueta (Estonia 1545614, Islandia 1528969, Kazajistán 1528968, Junior 1549868) | Nada nuevo. `rolesVsGrid` sigue en sombra (`ROLES_GRID_REHACE = False`) | No. Falta la app (ver «Para la app») |
| Al rehacer, todo lo que nombra piezas (l. 254) | 6 en 5 partidos: Francia–Türkiye 1528982, Noruega–Gales 1528972, Mirassol 1492455, Chapecoense 1492312, Países Bajos–Grecia 1528966 (Kourbelis fuera de la hoja como contenedor del seguro; tres goles en 12 minutos) | El rehacer entra también con FUERA-EN-LA-HOJA, ONCE-SIN-FILA-F1 y EFE-RECOMPUTO-PENDIENTE | Una precisión de un caso (Mirassol): la lista de la l. 254 suma M6 y la referencia de posesión |
| M3 · quién queda atrás en la rama de ventaja (l. 336) | 6 en 6 partidos (Juventud 1649063, Kazajistán 1528986, Rumania 1528977, Torque 1649057, Cerro Largo 1649056; Nacional Potosí 1649147 de copa) | — | No: la regla es de la v1.8 y está bien escrita |
| Ceder no es señal; la condición con su contrario (l. 241, 249) | 5 partidos (Letonia, Cerro, Irlanda del Norte, Feroe; Dinamarca) | — (el campo de la línea contraria sigue pendiente) | No |

**Reemplazos exactos (punto 7).** Cada texto viejo aparece una sola vez en la
v1.8, comprobado con `grep -F`:

- l. 229, viejo: «El rol de la hoja en la lista calculada del banco está
  **pendiente de la app**.» → nuevo: «La app lo marca en `bancoProbable`
  (`lateral`: el grid de su último partido lo puso en una punta de la línea).»
- l. 231, viejo: «El aviso del recibo está **pendiente de la app**.» → nuevo:
  «Si pasa, el recibo lo avisa con FUERA-EN-LA-HOJA (`dtpBanco`).»
- l. 233, viejo: «La lista calculada del banco en los insumos, el campo del
  banco en el parte y el aviso del recibo cuando falta un lado están
  **pendientes de la app**: hasta entonces se arma a mano, de los dos lados,
  y entra a `viasGol`.» → nuevo: «**La lista es `bancoProbable`** de los
  insumos (`GET …/dtp/{id}`), la misma que leen el EFE (F1 y B5) y el TDE: con
  el once y la banca completa es la hoja (`fuente: hoja`); antes es probable
  (`fuente: probable`) y se escribe así. Se toma por rol, de los dos lados y
  sin re-investigar, y entra a `viasGol`. El aviso cuando un lado no nombra a
  nadie de esa lista está **pendiente de la app**.»
- l. 254: después de «M3 (palancas)» se agrega «, M6 y la referencia de
  posesión». El caso es Mirassol 1492455:b:3 («once alternativo probable» en
  M6 y la posesión contra el «Atlético alternativo» después de rehacer). Es la
  misma regla; el caso es uno solo y la lista ya decía «todo lo que nombra
  piezas».

**Una nota de un solo caso, que no entra:** Moldavia–Kazajistán 1528968. La
etiqueta de la ficha decía 4-3-3 y el grid ponía cinco en la fila de
defensa. La l. 191 dice «el sistema es la formación de la ficha»: con una
etiqueta que no cuadra con sus filas, manda el grid. Va como aviso de la app
(«Para la app») antes que como texto.

## 4. Los candidatos de la v1.8: dónde quedan

| Candidato | Casos acreditables hoy | Queda |
|---|---|---|
| El reconvertido también ataca | 4 | **regla** (punto 2) |
| La presión alta con su vuelta | 3 | **regla** si el usuario aprueba el punto 3 |
| El seguro «sin» impide un FAVORABLE persiguiendo | 2 (Groningen; Portugal–Dinamarca 1528974); The Strongest, de copa | candidato |
| El segundo de la lista de penales es el que recibe la falta | 2 (Panathinaikos 1593355; Dinamarca 1528974) | candidato |
| El caso de la 6 viaja con el arquero | 2 (Villarroel 1645530; Liechtenstein 1528970) | candidato |
| Los penales concedidos en serie son del equipo | sin casos nuevos (suma Nacional Potosí 1649149, de copa y del mismo cruce) | candidato |
| El rearme del medio, el MECANISMO activo que baja el veredicto | sin casos nuevos | candidato |

La «vida útil del improvisado como techo» que el estudio anota como nueva ya
es regla (l. 278, v1.4). San Marino–Belarus 1528964 es cumplimiento.

## 5. Candidato a medir: la banda de «parejo» (punto 8)

**Hoy** (l. 432): «Sin umbral: cuánto es "parejo" lo lee el cierre con los
dos números a la vista». La v1.8 dejó la banda para un backtest.

**Lo que dicen las lecciones.** De los 20 `regla_fallo` del M5 (17
partidos), **14 son NEUTRO que el volumen decidió con claridad**:
6 eran FAVORABLE (UTC 1549556, Feroe 1528987, Eslovaquia 1528986:b,
Comerciantes 1549557, Albania 1528980 y Países Bajos 1528966, con 4,46
contra 0,46 de xG) y 8, DESFAVORABLE (Kazajistán 1528986:a, Liverpool M.
1649061:b, Sport Boys 1549557:b, Chipre 1528979, Águilas 1549863, Irlanda
1528976, Portugal 1528974 y Georgia 1528973).

Los otros 6 son FAVORABLE o DESFAVORABLE fuera de lugar. Entre ellos están
los que el cierre bajó a «parejo»: Llaneros 1549870, con 0,54 contra 0,55, y
Eslovaquia–Feroe 1528967, con 1,83 contra 2,09.

**El problema está en la apertura**: el cierre aplicó bien el juicio contra
lo concedido. NEUTRO funciona como refugio. Las lecciones no dan el número.

**Lo que haría falta medir** (fuera del skill, sobre los veredictos cerrados):
1. Población: lados con veredicto cerrado, `ramaJugada` calculada
   (`veredicto.py`, `porBloque`), stats en la ficha y la rama jugada en ≥ 70
   minutos. Las stats de la base son del partido entero y no por rama, y por
   eso la rama tiene que dominar los minutos. Se descuenta el xG de los
   penales, como manda la l. 434, sin copas nacionales.
2. Por cada lado: Δ = xG generado − xG concedido, sin penales y por 90
   minutos, y también el cociente. Donde no haya xG, los remates en el área.
3. Dos lecturas:
   - (a) qué banda de Δ separa lo que los cierres llamaron «parejo» del resto:
     el acuerdo entre cierres, no contra el resultado;
   - (b) cuánto se reparte el Δ cuando la apertura dijo NEUTRO, comparado con
     FAVORABLE y DESFAVORABLE. Si el NEUTRO de la apertura no se concentra
     cerca de 0 más que los otros, NEUTRO no informa.
4. Corte temporal y bootstrap, como en los backtests del motor. Selecciones y
   clubes por separado, porque esta semana fue de selecciones.

**Qué haría con el resultado:** solo con la banda medida se podría escribir
«NEUTRO pide un Δ esperado dentro de la banda». Hasta entonces, la l. 432 no
cambia y ninguna lección mueve el número.

## 6. Núcleo (punto 9)

Con el núcleo aprobado, para el `SKILL.md` de la v1.8 de hoy:

**Pasa a `references/HISTORIAL.md`, tal cual:** las l. 8-126, es decir, las
notas de la v1.8 a la v1.1 con sus «Candidatos anotados», «Queda fuera»,
«De dónde sale», el «Hueco declarado» de la v1.4 y «Lo que esta capa acertó»
de la v1.3. Son unos 5,1 K tokens (caracteres / 4) de los ~24,5 K del
archivo. La nota de la v1.9 que salga de esta propuesta **va directo al
historial**. Arriba queda la línea «Versión vigente: **v1.9 (fecha)**…» de la
propuesta del núcleo (§3.2).

**Lo que hoy vive solo en el historial y sube al cuerpo:**
- **P1** (v1.3, punto 2, l. 120), ya listada en el núcleo. Va como sub-viñeta
  debajo de la l. 201 («XI de referencia obligatorio»):
  > - **El once probable es nivel de dato C aunque converjan varias fuentes**
  >   *(v1.3)*: la convergencia entre redacciones es copia, no observación
  >   independiente. Si el análisis se cierra antes del once oficial, el
  >   documento declara la **ventana de confirmación pendiente** y ofrece
  >   rehacer el mapa de duelos.
- **P2** (v1.3, punto 1, l. 118), **que la propuesta del núcleo no listó**.
  El cuerpo (l. 211) solo dice «El umbral de ≥2 errores para la vía del
  arquero (v1.3) se mantiene», sin decir qué cuenta. Sin el historial, el
  umbral queda sin definición. Reemplaza esa frase de la l. 211:
  > **La vía del arquero** *(v1.3)*: cuando un arquero acumula **≥ 2
  > intervenciones fallidas con gol en el torneo en curso**, entra en las vías
  > de gol del rival con el mismo estatus que un centro al segundo palo. No
  > predice que va a fallar: dice que el mecanismo tiene frecuencia. Un
  > arquero suplente o nuevo no la activa por serlo (B6 y ARQUERO-NUEVO miden
  > otra cosa).

  La guardia del núcleo (`scripts/nucleo_reglas.json`) suma P2 con la frase
  ancla «intervenciones fallidas con gol».
- **Los candidatos que solo están en el changelog** (l. 34): el rearme del
  medio, el seguro «sin» persiguiendo y, si no sube, la presión alta. El
  cierre los necesita para sumar casos sin abrir el historial. Propuesta: un
  bloque **«Candidatos abiertos (no regla)»** al final del M5, de una línea
  por candidato con sus casos. Ese bloque junta los del §4 y absorbe las
  líneas de candidatos de las l. 290 y 417. Decide el usuario (pregunta 3).

Lo demás de las notas v1.1-v1.8 ya está en el cuerpo (los 12 cambios de la
v1.8 verificados uno por uno; la v1.1-v1.7, en la propuesta del núcleo).

## 7. Para la app (solo lo que falta)

Revisado contra `backend/` hoy (`dtp_cowork.py`, `banco.py`, `parte.py`,
`ficha_tactica.py`, `veredicto.py`):

| Qué | Por qué | Hoy |
|---|---|---|
| La rama **«arriba»** en `m2.posesion` y, por rama, `dt` y `n` del perfil del rival | Punto 1: que el recibo vea una rama sin «arriba» o un perfil sin sede, DT o `n` | `_rama_posesion` tiene `valor`, `contraQuien`, `marcador` y `sede`; las ramas son `igualadoOArriba` y `persiguiendo` |
| La **posesión y los córners del rival por condición** (local o visita, con `n`), y los **córners que concede** | Puntos 1 y 4 (la «referencia por condición» y los córners concedidos, pendientes desde la v1.7 y la v1.8) | `promedios_avanzados` da `posesion` y `corners` propios, sin sede ni concedidos (solo `xgContra`) |
| Aviso **«ningún nombre de `bancoProbable`»** en las `viasGol` de un lado | Punto 7 (l. 233): la única parte del banco que sigue pendiente | `bancoProbable` existe; FUERA-EN-LA-HOJA cubre el titular y el no convocado, no el lado vacío |
| Aviso del **grid**: coordenada citada que no existe, banda contraria a la casilla, y etiqueta de la ficha contra las filas del grid | Punto 7 (8 partidos; Kazajistán con la etiqueta) | Solo `M1-VS-ULTIMO-ONCE` y `rolesVsGrid` en sombra (`ROLES_GRID_REHACE = False`, a la espera de la medición cruzada de la v1.8) |
| Opcional: en `DTP-PENAL-SIN-EJECUTOR`, con base ≤ 1, avisar si la lista no nombra a ningún delantero titular de la hoja | Punto 5 | El aviso existe para la lista vacía |
| La medición de la banda de «parejo» | Punto 8 | No existe |

Ya hecho y referenciado, no se pide: `bancoProbable` (el `bancoOfensivo` de
la v1.8), el rehacer por FUERA-EN-LA-HOJA, ONCE-SIN-FILA-F1 y
EFE-RECOMPUTO-PENDIENTE, y la etiqueta de Jev `lectura_efe` → `lectura`.

## 8. Coherencia con TDE v0.1.27, EFE v1.11 y sad-analysis v4.6

Las tres se redactan en paralelo. Lo que esta propuesta pide o supone de cada
una:

| Dependencia | Qué tiene que decir el otro lado | Riesgo |
|---|---|---|
| **Banco ↔ EFE v1.11 (F1, B5) y TDE v0.1.27** | Las tres nombran **`bancoProbable`** como la única lista. El EFE puntúa B5 sobre ella y el DTP la hereda sin re-investigar (l. 506 sigue igual). La regla común: con el once y la banca completa es la hoja; antes, «probable» | Si una de las tres sigue diciendo «se arma a mano», se contradicen: es el arrastre del punto 7 |
| **Herencia SOB2 ↔ TDE v0.1.27** | Sin cambio en el DTP: el TDE hereda `nivelFoco`/`nivelRival` fuera de las ramas del que persigue y `nivelFocoPersiguiendo`/`nivelRivalPersiguiendo` dentro (l. 507; 1056). La «pieza del seguro en la rama de ventaja» del TDE se nombra desde `m2.piezas` y el M3 de quién queda atrás (l. 336). Si el TDE agrega «con doble pivote, las dos piezas», el DTP ya lo permite en `m2.piezas` | Ninguno, si el TDE no re-estima el seguro |
| **C1 ↔ TDE** | La clase del bloque y `c1Tde` las calcula el backend desde el checklist (`clasificar_bloque`); el TDE no la recalcula. Esta versión no toca el checklist | Ninguno |
| **Arquero ↔ EFE v1.11** | El estudio del EFE pide aclarar que B6 o la zona GK en rojo no son vía de gol sin un error documentado. El DTP dice lo mismo con P2 (≥ 2 intervenciones fallidas). La «pelota sucia del área» de la l. 235 (1) habla de quién llega al rebote, no de que el arquero falle: no choca | Que el EFE escriba «el DTP no hereda pelota sucia» y se lea como que se borra el renglón 8 de la lista del punto 6. Conviene que diga «la vía del arquero» |
| **Reconvertido y presión ↔ TDE (SOB) y sad-analysis v4.6 (falsador)** | El falsador toma todas las vías del DTP y nombra la vía o el rol además del nombre (aclaración del estudio del SAD). Las vías nuevas del reconvertido y de la vuelta de la presión entran con zona, así que no le agregan nombres sueltos | Ninguno |
| **Posesión ↔ TDE** | La rama «arriba» del DTP alimenta el régimen del que gana en el TDE. Si el TDE escribe su rama de ventaja «cediendo», cuadra con el «menos pelota que en igualado» por defecto | Ninguno |

## 9. Qué NO se propone

- **Ningún número** (vida útil, umbrales del MECANISMO, corte de DTP-REHACER,
  banda de «parejo», xG por penal, magnitud de la posesión).
- **Reescribir banco, grid, rehacer, M3 y ceder:** el texto está bien (§3).
- **Candidatos de uno o dos casos** (§4, el espejo persiguiendo, la etiqueta
  contra el grid), y **nada de copa** completa el umbral de ningún punto.

## 10. Decisiones del usuario

1. **Punto 3, la presión alta con su vuelta:** con 3 casos acreditables en 3
   partidos, uno de esta semana y de selecciones, ¿sube a regla o sigue
   candidato hasta un cuarto caso? *Recomendación: sube; cumple el umbral de
   la v1.8 y no toca números.*
2. **Punto 1, «arriba» siempre aparte:** ¿se borra la condición «cuando el
   foco no es favorito o puede ponerse arriba temprano» (l. 314), o se
   mantiene y solo se agrega la dirección por defecto? *Recomendación:
   borrarla. Es el juicio que se salteó en los cinco casos.*
3. **Núcleo, los candidatos:** ¿un bloque «Candidatos abiertos» en el cuerpo
   (una línea cada uno, al final del M5) o todos al historial? *Recomendación:
   el bloque. El cierre suma casos y no lee el historial.*

Lo demás, con la recomendación del §1 (regla conservadora de la v1.8).
