# Propuesta de revisión · `sad-analysis` v4.5 → v4.6

**Estado: PROPUESTA (17/11/2026), para aprobar punto por punto.** No toca
`docs/skills/sad-analysis/SKILL.md` hasta que se redacte. Se aplica **con el
núcleo** (`NUCLEO_SKILLS_propuesta.md`, aprobado con las cinco
recomendaciones de `RESUMEN_GENERACION_2026-11.md`, todavía sin aplicar). Al
redactarse: el SKILL, `references/HISTORIAL.md`, `CORTE_VERSION` con la v4.6
y, cuando el usuario suba el zip, su hora en `SUBIDA_VERSION`.

De dónde sale: lo aprobado (`PENDIENTES.md`, 10 y 11/11;
`DESCONFIAR_propuesta.md`) y el estudio del 17/11
(`estudio_lecciones_2026-11-17/`): 70 lecciones de partidos del 10 al 16/11
(35 sostuvo, 20 regla falló, 14 mal aplicada, 1 imprevisto). **Una semana,
mayoría de fecha FIFA**, y 7 de copa nacional (rúbrica, no métrica). Cada
patrón se releyó contra la prosa: dos números del estudio se corrigen (puntos
1 y 5). **Ninguna lección pide mover un número.**

## 0. Resumen

Tres puntos aprobados se redactan (1-3), (h)/(i) van al historial (4), tres
aclaraciones con 3+ partidos (5-7) y el núcleo (8). Nada afloja una regla
vigente ni mueve un número de la app; tres temas quedan para backtest (9-11).

### Puntos para aprobar

| n.º | Qué cambia | Tipo | Casos | Recomendación |
|---|---|---|---|---|
| 1 | DESCONFIAR se lee en el `porque` del 1X2 y en la espina; no sube la carga y no se retoca el número para apagarla (1.7 g, nueva) | aprobado antes | 4 con alerta: Suecia, Mirassol, Puerto Cabello, Italia–Francia | aprobar |
| 2 | Una racha de un partido no sostiene al elegido; con racha de uno, (d) pide nombrar las dos salidas del corte (1.6 i, d) | aprobado antes + aclaración | 9 rachas de un partido con riesgo alto: 8 se cortaron | aprobar **sin** la frase «3+ sigue con la tarjeta» (decisión 1) |
| 3 | El descarte: lo calcula la app; el parte escribe la frase que lo sostiene (6-B) | aprobado antes | sin casos nuevos | aprobar (decisión 2) |
| 4 | (h) distancia a la casa e (i) marcador contra el elegido: medición en el historial, sin regla y sin semáforo | aprobado antes | sin material nuevo | aprobar |
| 5 | El falsador «(1X2)» nombra lo que hace imposible el pronóstico, no un gol suelto del débil (6-C 5) | aclaración | 6 de 6 mal aplicadas | aprobar |
| 6 | En el extremo, el hecho que depende del once probable se rehace con la hoja, como en (i) (1.6 g) | aclaración (una línea) | 4 de 8 mal aplicadas (3 seguras) | aprobar |
| 7 | El falsador por nombres lleva también la vía o el rol, y los nombres salen de `bancoProbable` (6-C 7) | aclaración | 3 (2 fallaron, 1 sirvió) | aprobar (decisión 3) |
| 8 | Núcleo: el changelog va a `references/HISTORIAL.md`; el banco de la matriz sale de `bancoProbable` (6-A) | núcleo (aprobado el 10/11) | — | aplicar con la v4.6 |
| 9 | El corte a cero y no al otro signo | a backtest | 5 + 4 partidos | no al skill: medir por largo de racha |
| 10 | La rama de goleada como marcador | a backtest | 7 (3 sí, 4 no) | no al skill |
| 11 | El 1X2 o el empate (Luxemburgo, Always Ready, Italia–Francia, Llaneros) | a backtest | 1 cada uno | no al skill |
| 12 | Lo que falta en la app: la alerta en el recibo, sellada en el primer depósito; `pronostico.descarte`; `1X2-CARGA-CONTRA-RIESGO`; una línea en `rehacer` | app | — | pedir como incidencias |

---

## 1. Lo aprobado

Las líneas son de `docs/skills/sad-analysis/SKILL.md` v4.5 (546 líneas, hoy).
Si cambia antes de redactar, cada texto se ubica por la sección y la regla.

### Punto 1 · La alerta DESCONFIAR (paso 1.7, regla nueva (g))

**Qué hace hoy la app** (`backend/analisis/desconfianza.py`, PR #469): al
leer el parte calcula la alerta `dato` **DESCONFIAR** con dos motivos.
`SOBRE-LA-CASA` es nuestra probabilidad del elegido 2+ puntos sobre la casa
sin margen (`simulacion.ALERTA_SOBRE_CASA`). `BURBUJA-DE-UN-PARTIDO` es la
racha + del elegido de un solo partido con riesgo alto o muy alto. La pone en
la tira y arma el bloque `desconfianza`: el descarte (el menos probable de
nuestro 1X2, con lo que le da la casa), la doble oportunidad «el otro no
gana» y `ventajaPorFuerza` por lado. No mueve ningún número. **El skill no la
calcula ni la copia**: la lee y la nombra.

**Texto** (entre la (f), l. 324, y «La estabilidad…», l. 325):

> - **(g) DESCONFIAR, la alerta de la app** *(v4.6; usuario, 10/11)*. La tira del parte trae la alerta `dato` DESCONFIAR sobre el elegido del 1X2, con sus motivos: `SOBRE-LA-CASA` (le damos 2+ puntos sobre la casa sin margen) o `BURBUJA-DE-UN-PARTIDO` (su racha + es de un solo partido con riesgo alto o muy alto). La calcula la app; no se calcula a mano ni se copia. Si aparece: se **nombra** en el `porque` del 1X2 y en la espina del elegido; el elegido **no sube** sobre el mercado (1.7 a); y la lectura del 1X2 se escribe con el descarte (6-B). **No mueve el 1X2 y no se retoca el número para apagarla**: es confianza, no número (usuario, 03/11). Si el número está 2+ sobre la casa, lo que lo sostiene es el dato con su cifra de 6-B, escrito antes; la alerta no lo agrega ni lo quita. Qué se juega con ella lo decide el método con 100+ partidos (`docs/METODO_APUESTA.md`), no el parte.

En «Auditoría automática» (l. 535), sumar DESCONFIAR a la lista de alertas
calculadas.

**Lo que el estudio le suma.** El estudio dice «3 de 3». Releída la prosa,
hay **4 partidos con la alerta** y el resultado es más fino:

| Partido | Elegido | ¿Ganó el elegido? | «Elegido o empate» |
|---|---|---|---|
| Suecia–Bosnia 1528978 | Suecia | sí | sí |
| Mirassol–Atlético-MG 1492455 | Mirassol | no (empate) | sí |
| Puerto Cabello–Monagas 1646937 | Puerto Cabello | no (perdió) | no |
| Italia–Francia 1528960 | Francia | no (ganó Italia) | no |

El elegido ganó 1 de 4: la dirección de la alerta se sostiene. La doble
oportunidad acertó 2 de 4: **no adelanta** la opción (c) del método
(Mirassol la pide; queda para los 100+). Son lecciones escritas, no un
muestreo: la medición es la tarjeta de la Simulación. `SOBRE-LA-CASA`: ninguna
lección lo nombra (Armenia–Chipre 1528959 eligió la racha un punto sobre la
casa, bajo el umbral). Sin material a favor ni en contra.

*Se sostiene si,* con 100+ partidos con alerta, el elegido acierta menos que
sin ella. *Lo tumba si* no hay diferencia.

### Punto 2 · Una racha de un partido no sostiene al elegido (1.6 (i) y (d))

**Lo aprobado** (`DESCONFIAR_propuesta.md`, punta 2) dice «con racha de 1
partido y riesgo alto o muy alto, la espina no dice "sigue" sin un hecho de
la lista». **La (i) de la v4.5 ya lo pide** para toda racha con ese riesgo.
Lo que agrega es nombrar el caso de un partido, donde se cayó la semana:
«viene de ganar» y la tarjeta fuerte no alcanzan. Con racha de un partido,
además, la (d) vigente («"se da vuelta" no tiene más base que "se
reinicia"») choca con mandar el corte «al otro signo» (g, i) sin nombrar el
empate. Se aclara sin tocar la guía.

**Texto**, subviñeta nueva al final de la (i) (después de la l. 308):

> - **Una racha de un partido no sostiene al elegido** *(v4.6)*. Con racha de un solo partido y riesgo alto o muy alto, «viene de ganar» (o de perder) no es razón del 1X2 ni de la espina, y la tarjeta fuerte tampoco es un hecho (Cali–Tolima 1549867: «sigue» con la tarjeta fuerte y se cortó empatando). Si el 1X2 elige igual al lado de esa racha, la tira trae `BURBUJA-DE-UN-PARTIDO` (1.7 g). Y rige (d): el `porque` de la espina nombra **las dos salidas del corte**, a cero y al otro signo. La lectura sigue siendo la de (g) e (i); lo que cambia es que el empate no queda fuera de la prosa (Torque–Racing 1649057, Llaneros–Chicó 1549870: se cortaron a cero con la lectura al otro signo).

En (d) (l. 299), al final: «*(v4.6)* Con riesgo alto o muy alto, ver la
última subviñeta de (i).»

**Lo que el estudio le suma** (la prosa lo confirma). Rachas de un partido
con riesgo alto o muy alto en las lecciones:

- **se cortaron 8**: cinco +, Racing 1649057, Chicó 1549870, Boston River
  1649432, Mirassol 1492455 y Cali 1549867 (el riesgo de Cali no está en la lección: lo cuenta el estudio); tres −, Monterrey (en Querétaro–Monterrey 1550951),
  Millonarios 1549871 y Bélgica 1528958;
- **siguió 1**: Dinamarca 1528974, ante un rival muy fuerte.

Eslovaquia 1528967, de riesgo medio, también se cortó. Son lecciones, no
denominador: la guía calibrada ya da 35 % y 28 % a que siga.

**Lo que no entra** (decisión 1): la frase aprobada «las burbujas de 3+
partidos son las que arrancan: ahí la espina puede leer "sigue" con la
tarjeta». Contra el riesgo alto **afloja la (i) de la v4.5**, que pide un
hecho de la lista para «sigue» con cualquier largo. Se escribió el mismo
10/11, antes de la (i). La regla conservadora del 10/11 resuelve a favor de
la vigente.

### Punto 3 · El descarte (paso 6-B)

**Qué hace hoy la app.** El resultado descartado ya está calculado
(`desconfianza.descarte`: el menos probable de **nuestro** 1X2, con la casa).
La Simulación lo mide (`alertaConfianza.descarte`). Lo que no existe es el
lugar para la frase: `PronosticoParte` no tiene `descarte`, y un campo que no
está en el contrato se pierde sin aviso.

**Texto**, viñeta nueva en 6-B, después de «El banco del rival…» (l. 457):

> - **El descarte** *(v4.6; usuario, 10/11: «una de las formas de acertar es escoger qué alternativa no hay que escoger»)*. El descarte es el resultado **menos probable de nuestro 1X2**: lo calcula la app (`desconfianza.descarte`, con lo que le da la casa) y no se copia. El parte escribe **la frase que lo sostiene**, con un hecho de ESTE partido o la lectura que lo excluye, en `pronostico.descarte`. Hasta que la app tenga el campo, va al final de `lecturaSad.unXDos.texto`, empezando por «Descarte:». Si la lectura excluye otro resultado que el menos probable del número, es una contradicción: se mueve el número con su porqué o se publican los dos (disciplina 33, 6-A). **Con DESCONFIAR, la lectura del 1X2 se escribe como «el otro lado no gana» antes que como «gana el elegido».** Es narrativa, no apuesta: no mueve el número y qué se juega lo decide el método. El veredicto lo mide aparte del 1X2.

**La diferencia con lo aprobado** (decisión 2). Lo aprobado decía «el menos
probable, **o el que la lectura excluye con un hecho**». Con dos definiciones,
el número diría una cosa y la frase otra: el resultado tiene que ser
calculable y único (CLAUDE.md: «el parte NO trae nada calculable»). La
lectura que excluye otro resultado se resuelve en el número, como cualquier
contradicción.

**Historial**: hoy el descarte sale 17,0 % contra 21,8 % de la casa (264
partes), pero coincide con el de la casa en 251. Todavía no descartamos
distinto que ella.

### Punto 4 · Medido en conversación: (h) e (i), observación sin regla

Van a `references/HISTORIAL.md` (núcleo, punto 8) y **no al cuerpo del
SKILL**. El texto, para el historial:

> **(h) Distancia a la casa** *(usuario, 11/11/2026; observación, no regla)*. 374 partes del 15/09 al 01/11, por la mayor distancia entre nuestro 1X2 y la casa sin margen: con ≤ 2 pts en los tres resultados el elegido ganó 66,7 % contra 53,7 % que pedía la casa (n 177); de 2 a 5 pts, 44,2 contra 46,7 (n 104); de 5 a 10, 46,0 contra 51,1 (n 63); de + 10, 50,0 contra 53,1 (n 30). Eligiendo distinto que la casa (33): 11 aciertos contra 10 del favorito de la casa. El valor no está en apartarse de la casa: está en marcar cuándo creerle.
>
> **(i) Marcador contra el elegido** *(usuario, 11/11/2026; observación, no regla)*. En 83 de los 374 partes el marcador declarado contradecía al elegido del 1X2: ahí el elegido acertó 39,8 %. Con el marcador acompañando, 60,1 % contra 55,6 % de la casa. Refuerza lo que ya pide 1.6 (h): el marcador lo gana el elegido o la lectura dice cuál de los dos manda y por qué.

**Por qué no va al núcleo.** La app calcula con estas dos señales un
semáforo con regla fija desde el 11/11. Una línea en el cuerpo del skill con
«≤ 2 pts gana el 66,7 %» invita a pegarse a la casa para quedar del lado bueno,
y la señal deja de medir (anti-Goodhart). Lo que el skill tiene que decir ya
está escrito: el número del favorito es el del mercado (6-B, v4.4) y el
marcador acompaña al elegido o se dice (1.6 h, v4.5). **El skill no nombra el
semáforo** en ningún texto de esta propuesta.

**El estudio**: sin material nuevo. Torque 1649057 (50 contra 50,2) y
Portugal 1528974 (59 contra 59,6) estaban pegados a la casa y el elegido no
ganó: anécdotas que la n 177 cubre mejor. Luxemburgo 1545614 pide apartarse:
punto 11.

---

## 2. Puntos nuevos con material (3+ partidos)

### Punto 5 · El falsador «(1X2)» es lo que hace imposible el pronóstico (6-C, punto 5)

**El patrón** (6 de 6 mal aplicadas, todas con el 1X2 acertado). El
falsador del 1X2 sonó con un gol del débil que no tumbaba nada: Lituania
1528989 («si Liechtenstein marca», 2-1 con 86 %), Finlandia 1528981 (7-2 con
92 %), Chipre–Montenegro 1528979 (el penal del 52'), Noruega 1528972 (el
suplente marcó con 0-2). En Inglaterra–Croacia 1528962 un renglón de marcador
quedó mezclado en la condición del 1X2.

**Corrección al estudio.** El borrador del estudio aceptaba como «(1X2)» «el
gol del rival con 0-0». UCV Moquegua–Grau (1549560) lo desmiente:
«(1X2) si Grau marca primero» sonó al 24' y el local ganó. Según la ventaja
por minuto, el que abre a esa altura no gana uno de cada tres. Abrir el
marcador no es sacar el resultado. La aclaración, entonces, no es sobre qué
gol sino sobre **qué resultado**.

**Texto**, al final del punto 5 de 6-C (l. 474):

> *(v4.6)* **Una cláusula «(1X2)» nombra lo que hace imposible el pronóstico: la vía por la que el rival se queda con el resultado** —empata o gana—, no un gol suyo: «(1X2) si Liechtenstein empata o gana con un gol de pelota parada». Un gol del débil que deja al elegido ganando, o que todavía se puede dar vuelta, va como «(marcador)»; tampoco «marca primero» es «(1X2)» (UCV–Grau 1549560: Grau abrió al 24' y el local ganó; Lituania–Liechtenstein 1528989, Noruega–Gales 1528972: el gol del débil sonó con el favorito ganando). Un renglón «(marcador)» no tumba el 1X2 aunque suene (Inglaterra–Croacia 1528962).

Es coherente con el primer párrafo de 6-C («sobre el mecanismo, no sobre el
estado del marcador»): la cláusula dice la vía y el resultado que esa vía le
da al rival.

En la Auditoría 2, pregunta 8 (l. 509), al final: «*(v4.6)* ¿Alguna cláusula
"(1X2)" es un gol suelto del débil?»

*No mueve números ni el veredicto*: el falsador sigue siendo prosa que el
veredicto juzga (`docs/COWORK.md`).

### Punto 6 · K-CERCA-EXTREMO declarado y apostado igual (1.6 (g))

**El patrón** (4 mal aplicadas de 8; las otras 4 respetaron la alerta y se
sostuvieron: Santa Fe 1549869, Torque 1649057, Boston River 1649432 y
Anaitasuna 1644336). Releídos:

| Partido | Qué pasó | ¿Hace falta texto? |
|---|---|---|
| Armenia–Chipre 1528959 | la racha elegida un punto sobre la casa (36 contra 35,4): es cargar (1.7 a, v4.4) | no: cumplimiento |
| Portugal–Dinamarca 1528974 | «sigue» por la tarjeta fuerte, sin hecho de la lista | no: (g) ya lo pide |
| Mirassol–Atlético-MG 1492455 | la espina se sostenía en un once alternativo; la hoja trajo al titular y la lectura no se movió | **sí**: la (g) no dice lo que la (i) dice del once |
| Letonia–Armenia 1545616 | el 1X2 eligió la racha (40 %) en riesgo alto y cerca del extremo | dudoso: la lección no da el mercado; si estaba en el número de la casa, la v4.4 no lo llama cargar |

Tres son cumplimiento de reglas escritas: repetirlas no cambia la conducta
(estudio §2), y la guardia es de la app (`1X2-CARGA-CONTRA-RIESGO`, punto
12). El cuarto sí pide **una línea**: la subviñeta del once vive solo en la
(i), y el extremo sin riesgo alto no la hereda.

**Texto**, en (g), después de la segunda subviñeta (l. 304):

> - *(v4.6)* **El hecho que depende del once probable se rehace con el once oficial**, como en (i): si la hoja lo desmiente, el hecho cae, la espina vuelve a la tarjeta o al corte, y se dice (Mirassol–Atlético-MG 1492455: la racha de visita se leía «sigue» por un once alternativo que no salió).

En la Auditoría 2, pregunta 9 (l. 510), «contra riesgo alto o muy alto»
pasa a «contra riesgo alto o muy alto, o en el extremo».

### Punto 7 · El falsador por nombres lleva la vía o el rol (6-C, punto 7)

**El patrón** (3 partidos). Falló en Comerciantes–Sport Boys 1549557 (los
nombres del banco de la apertura arrancaron de titulares) y en Inter
Bogotá–América 1648690 (goleadores con una rotación probable de cinco);
sirvió en Águilas–Medellín 1549863 (el banco rival, gol del 83'). El que sirvió nombraba un rol (el banco), no solo personas. Kosovo–Israel
1528971 va en la misma dirección: el mecanismo, la roja, como alarma.
Desde el 17/11 la app trae **una sola lista**, `bancoProbable` (en `f1/{id}`,
`dtp/{id}` y `tde/{id}`): `fuente: probable` antes del once y `fuente: hoja`
con la banca publicada.

**Texto**, en el punto 7 de 6-C (l. 476): «con los nombres: antes del once,
los del banco probable de la F1 y del DTP; con el once oficial, los de la
hoja» pasa a:

> …con los nombres de `bancoProbable` (`fuente: probable` antes del once, `fuente: hoja` con la banca publicada), **y con la vía o el rol** (el banco, la segunda línea, la pelota parada): un nombre del once probable puede arrancar de titular o rotar, y la cláusula se queda sin sonar (Comerciantes–Sport Boys 1549557; Águilas–Medellín 1549863 nombró el banco y sonó).

---

## 3. A backtest, no al skill

Lo que toca la guía calibrada, el 1X2 o el empate **no se cambia por
lecciones** (REVENTON; CLAUDE.md: «solo con el backtest a la vista, en los
dos lados y en los vectores dorados»).

### Punto 9 · La burbuja que revienta a cero y no al otro signo

- **Casos.** La espina leía «al otro signo» y se cortó a cero en Defensor
  1649062, Tolima 1549867, Racing 1649057, Chicó 1549870 y Eslovaquia
  1528967. También cortaron a cero Letonia 1545616, Torque 1649057, Mirassol
  1492455 y Atlético-MG 1492455, aunque esas lecciones tocan otra regla.
  Varias son rachas de uno o dos partidos con la tarjeta débil.
- **Qué está medido.** `backtest_burbuja --calibrar` parte el movimiento por
  signo y riesgo (87.379 burbujas, REVENTON §14): a cero da 25-28 % en todos
  los niveles y al otro signo 37 % y 45 % con riesgo alto y muy alto. Eso es
  `MOVIMIENTO_BACKTEST` (`burbuja.py` y `src/lib/burbuja.ts`), lo que leen la
  (g) y la (i).
- **Qué falta medir.** El mismo bloque **partido por largo de la racha (1 ·
  2 · 3+)** y por `rival.aFavor`: las observaciones ya traen `partidos`, son
  unas líneas en `_movimiento`, sin tocar puntos. Si con racha de un partido
  y riesgo alto «a cero» iguala o pasa a «al otro signo», con intervalos que
  no se tocan, cambia la guía de las rachas cortas (Python, TS y
  `scripts/casos_burbuja.json`). Si no, la semana fue ruido (la v4.5 ya
  anotó «3 de 6 a cero, se mide antes de afinar»). En Aprendizaje sigue
  faltando la espina en el extremo partida por movimiento (v4.5, app 3).
  Mientras tanto, solo el punto 2: nombrar las dos salidas.

### Punto 10 · La rama de goleada

- **Casos.** El gatillo por minuto no separa. No llegó con el gatillo dado:
  Petrolero 1649148 (5'), Croacia 1528985 (2', Kinský), Inglaterra 1528962
  (24'). Llegó: Valencia 1644380, Eibar 1644365, Finlandia 1528981, y
  Alavés 1644336 sin gatillo; casi siempre contra 3-5 categorías abajo o
  San Marino.
- **Qué falta medir.** (1) Con ventaja de uno o dos al descanso, cuánto
  termina 3+ arriba por tramo de probabilidad previa (con un tramo 90 %+):
  extender `docs/revisiones/datos/tabla_ventaja_por_fuerza.py` (53.108
  partidos; trae el descanso, no el minuto). (2) Si con el favorito de λ
  alta el tramo 3+ acierta más que el marcador acotado: `backtest_goles
  --padron` (REVENTON §17) partido por λ del favorito.
- **Las copas** (los casos de categoría) quedan fuera de toda métrica
  (`escala.copas_nacionales`): rige 6-E (4). El candidato «con 90 %+ la rama
  es el marcador» choca con la v4.4 («el acotado manda»): se mide antes. La
  aclaración del estudio («nombrar lo que la contiene: el arquero, el
  rearme») tiene 3 a favor y 4 mixtos: candidato.

### Punto 11 · El 1X2 o el empate

| Caso | Pide | Medición que haría falta | Script |
|---|---|---|---|
| Luxemburgo–Estonia 1545614 | seguir a las tres fuentes contra un mercado casi parejo | nuestros partes con el mercado bajo 50 % y motor y espina fuerte del otro lado: acierto de cada elegido (la serie de 6-A, v4.4: «partido parejo con motor y mercado en lados distintos») | no hay en `backend/`: va a Aprendizaje (punto 12) |
| Always Ready 1649146 | más empate en la ida de una llave | el empate de las idas contra la cuota de cierre | `backend/eliminatoria.py` marca ida y vuelta; el script es nuevo |
| Italia–Francia 1528960 | seguir al motor con DESCONFIAR | la tarjeta de la Simulación, con 100+ alertas | `simulacion.resumen_alerta` (ya corre) |
| Llaneros–Chicó 1549870 | el contexto «sin nada en juego» mueve el empate | el empate entre dos eliminados contra la cuota | ninguno; la v4.5 lo dejó como contexto, no hecho (6-D) |

En sentido contrario, Andorra 1545615 y Azerbaiyán 1528970 siguieron al
mercado contra un motor con μ de amistosos y acertaron. Coincide con
`backtest_nivel_ventana` (30/10: el nivel sin amistosos no mejora el 1X2) y
con la lista de la v4.4. Nada que cambiar.

---

## 4. Núcleo (punto 8)

Para el `SKILL.md` v4.5 de hoy (73,4 K caracteres, ≈ 18,4 K tokens; era
15,0 K el 03/11):

| Qué | Dónde queda | Tokens |
|---|---|---:|
| l. 8-46: changelogs v4.5 … v4.0 | `references/HISTORIAL.md`, tal cual | −2,0 K |
| changelog v4.6 (abajo) | `references/HISTORIAL.md` | 0 en el núcleo |
| (h), (i) y las mediciones de los puntos 1 a 3 | `references/HISTORIAL.md` | 0 |
| textos de los puntos 1-3 y 5-7 | cuerpo del SKILL | +1,3 K |
| l. 1-7, 50-fin | cuerpo, sin cambios salvo los puntos | — |

**Resultado: ≈ 17,7 K**, más o menos lo de hoy pese a la versión nueva.
Fase 2 (sacar los casos de 1.6 y 6-B, ≈ 5,5 K mixtos) **no se propone**: es
reescribir reglas, con su propia propuesta (NÚCLEO §3.4).

**Debajo del título** (reemplaza las l. 8-46):

> Versión vigente: **v4.6 (<fecha de la subida>)**. Las notas de cada versión, los casos que motivaron cada regla y las mediciones están en `references/HISTORIAL.md`: **no hace falta leerlo para analizar un partido**; se lee al revisar el skill.

En la l. 3 y la l. 6, «v4.5» pasa a «v4.6». **Reglas que viven solo en el
changelog: ninguna** (NÚCLEO §2.5; se verificó de nuevo para la v4.5: los
nueve puntos están en sus pasos).

**La recomendación 5 del núcleo** (la corrida no carga `efe-dashboard` en
`partes`). La regla del dashboard v1.13, punto 2, pasa a sad-analysis: «la
palanca del reloj y el banco de la matriz salen del banco probable de la
tabla F1». Si no, queda en un skill que no se carga. **Texto**, debajo de la
tabla de 6-A (l. 423):

> *(v4.6)* La matriz la escribe el parte (`efe-dashboard` no se carga en la corrida): **su banco y la palanca del reloj salen de `bancoProbable`** de `GET /analisis/cowork/f1/{fixture}`, no de los nombres más conocidos.

**Changelog v4.6**, para el historial:

> **v4.6 · <fecha> — En quién desconfiar, y el falsador dice qué hace imposible el pronóstico.** Revisión desde lo aprobado el 10 y el 11/11 (`DESCONFIAR_propuesta.md`) y las 70 lecciones pendientes del 10-16/11 (`estudio_lecciones_2026-11-17/`). Ninguna lección pide mover un número. **1.** DESCONFIAR se lee y se nombra; no sube la carga ni se apaga retocando el número (1.7 g). **2.** Una racha de un partido no sostiene al elegido; el `porque` nombra las dos salidas del corte (1.6 i, d). **3.** El descarte: lo calcula la app, el parte lo sostiene con una frase (6-B). **4.** La cláusula «(1X2)» es lo que hace imposible el pronóstico (6-C 5). **5.** En el extremo, el hecho del once probable se rehace con la hoja (1.6 g). **6.** El falsador por nombres lleva la vía o el rol, con `bancoProbable` (6-C 7). **7.** El banco de la matriz sale de `bancoProbable` (6-A).

**Guardia** (NÚCLEO §5, `test_nucleo_skills`): anclas de sad-analysis para
`scripts/nucleo_reglas.json`: «DESCONFIAR, la alerta de la app», «Una racha
de un partido no sostiene al elegido», «El descarte», «lo que hace imposible
el pronóstico», «se rehace con el once oficial» (en g y en i) y «salen de
`bancoProbable`».

---

## 5. Para la app

Solo lo que falta (revisado en `backend/` el 17/11). Cada uno es una
incidencia con su test, si el usuario la pide.

1. **DESCONFIAR en el recibo, sellada en el primer depósito.** Hoy se
   calcula solo al leer (`parte.dto`); el recibo del POST no la trae y
   `modos/partes.md` relee el parte solo si el recibo marca algo: el analista
   puede no verla nunca. Mostrarla antes del cierre invita a bajar el número
   para apagarla, y la Simulación compararía partes retocados: se sella la
   del **primer** depósito, como la `cadena` (decisión 4).
2. **`pronostico.descarte`** (texto) en `docs/openapi.yaml`, `parte.py`,
   `src/api/types.ts` y los dos datasources. El resultado lo pone la app
   (`desconfianza.descarte`) y el veredicto lo muestra aparte del 1X2.
3. **`1X2-CARGA-CONTRA-RIESGO`** (`dato`, pendiente desde la v4.4): el
   elegido es el lado de una racha con riesgo alto o muy alto, o en
   K-EXTREMO / K-CERCA-EXTREMO, y su número está sobre el mercado. Casos:
   Armenia–Chipre 1528959, Once Caldas 1648691 y Llaneros 1549870
   (`respetoRiesgo: false`). Es la guardia del punto 6: el cumplimiento se
   frena en el recibo, no repitiendo la regla.
4. **Una línea en `.claude/skills/corrida-sad/modos/rehacer.md`.** Hay que
   revisar, con la hoja, el hecho de la espina que dependía del once
   probable, en la (i) y en la (g). Lo pidió la v4.5 («Para la app» 13) y
   sigue sin estar.
5. **La serie «motor y mercado en lados distintos»** (6-A, v4.4) en
   Aprendizaje: acierto de cada elegido, para el punto 11.
6. **`_movimiento` por largo de racha** en `backtest_burbuja` (punto 9). Es
   medición, no un número: los puntos no se tocan.
7. **Sellos:** `CORTE_VERSION["sad-analysis"]` suma `("v4.6", <fecha>)`, la
   hora de la subida va a `SUBIDA_VERSION` y `REGLAS_CALCULADAS_DESDE` lleva
   la fecha de cada alerta nueva.

**No hace falta**: `ventajaPorFuerza` (ya en `desconfianza` del parte; en
`GET …/tde/{id}` es del TDE) y `bancoProbable` (hecho el 17/11).

---

## 6. Coherencia con las versiones en paralelo

| Dependencia | Qué necesita la v4.6 | ¿Lo tiene la otra? |
|---|---|---|
| **TDE v0.1.27 · `ventajaPorFuerza`** | El punto 5 se apoya en que abrir el marcador no es ganar. La rama `siMarcaPrimero` del TDE cita la misma tabla: «no gana» por tramo de fuerza | **Sí, por la misma propuesta** (DESCONFIAR, puntas 4 y 5). La tabla vive en `desconfianza.TABLA_VENTAJA`: el SAD y el TDE citan la misma. La de `GET …/tde/{id}` es pendiente del TDE, no del SAD. Si el TDE da «no gana el 31 %» al que abre, el falsador «(1X2)» no puede ser «si abre»: dicen lo mismo |
| **TDE v0.1.27 · el desenlace lo pone la fuerza** | Nada: el SAD no lee la tipología para el 1X2 | — |
| **DTP v1.9 · posesión por rama, rama «arriba» separada** | Las vías que toma el falsador (6-C 3) | **Sí.** Portugal–Dinamarca 1528974 apoyó la espina en la rama persiguiendo del DTP y se jugó la otra: un caso, sin texto en el SAD; lo resuelve la rama separada del DTP |
| **DTP v1.9 · el 9 titular en la lista de penales** | El falsador por penal (6-C 3) nombra al ejecutor del DTP | **Sí**: el SAD no cambia, toma la lista |
| **EFE v1.11 · rama «once alternativo» y F1 con el once oficial** | El punto 6: el hecho del once probable se rehace con la hoja | **Sí**: el rehacer ya entra con EFE-RECOMPUTO-PENDIENTE (PR #560). La línea del punto 6 es la del SAD |
| **EFE v1.11 · el arquero suplente no fue la vía** (9 partidos) | Hoy 3.5 cuenta «una baja del arquero confirmada» como hecho para sacar el marcador del acotado | **Coherente**: el EFE lo deja como aclaración y bajar el ×1,5 es candidato. Si el EFE lo mide y lo baja, se revisa 3.5 |
| **`bancoProbable`, una lista** | Puntos 7 y 8 | **Sí**, hecho el 17/11 (`backend/analisis/banco.py`) |
| **efe-dashboard v1.13, punto 2** | El banco de la matriz | Pasa al SAD (punto 8): el dashboard no se carga |

---

## 7. Qué NO se propone y por qué

- **«Un récord no se apuesta a favor aunque haya un hecho»** (Rumania
  1528977). K-EXTREMO con un hecho se sostuvo 7 veces: Chequia, Türkiye,
  Macedonia, Serbia, Croacia, Noruega y Garcilaso. Falló 2: Rumania y Central
  Español. La (g) se queda.
- **La frase de las rachas de 3+** del punto 2: afloja la (i) (decisión 1).
- **Una línea en el skill sobre la distancia a la casa o el semáforo** (punto
  4): anti-Goodhart.
- **El marcador no contradice el tramo más probable** (Finlandia 1528981, un
  caso). Choca con «el acotado manda». La v4.5 ya pide nombrar la rama.
- **La tarjeta fuerte en una racha de un partido pesa menos que cómo se
  cortan** (Cali 1549867, Suiza 1545654; 2 casos). Queda en observación; el
  punto 2 cubre lo que se puede decir.
- **Ir contra el riesgo con ESCALA-LIGAS** (Amorebieta–Logroñés 1644335):
  un caso y de copa.
- **Adelantar «elegido o empate»** (Mirassol): 2 de 4 en la semana. Lo
  decide el método con 100+.
- **Mover la guía del corte, la rama de goleada, el 1X2 o el empate**:
  puntos 9 a 11.

---

## 8. Decisiones del usuario

1. **Punto 2.** La frase aprobada «con 3+ partidos la espina puede leer
   "sigue" con la tarjeta», ¿entra? (a) **No**: contra el riesgo alto rige
   la (i) de la v4.5 *(recomendado)*; (b) sí, como excepción a la (i).
2. **Punto 3.** Si la lectura descarta otro resultado que el menos probable
   del número: (a) es una contradicción y se resuelve en el número
   (disciplina 33) *(recomendado)*; (b) el parte declara su propio descarte y
   la app guarda los dos.
3. **Punto 7.** El falsador por nombres con la vía o el rol (3 casos: 2 en
   contra, 1 a favor): (a) entra como aclaración *(recomendado: no afloja
   nada y usa la lista única nueva)*; (b) candidato hasta más casos.
4. **«Para la app» 1.** La alerta en el recibo: (a) sellada en el primer
   depósito, y la Simulación mide esa *(recomendado)*; (b) recalculada con
   cada depósito, como hoy; (c) fuera del recibo, y el encargo relee siempre.

Lo demás (puntos 1, 4, 5, 6 y 8) se recomienda tal cual. Los puntos 9 a 11
no piden decisión: quedan medidos o por medir.
