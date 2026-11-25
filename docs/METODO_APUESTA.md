# El método de apuesta (03/11/2026)

Pedido del usuario: «investiguemos el método definitivo, ese pondremos en la
simulación del sistema». Antes, ese mismo día, el usuario fijó el criterio:

> No le ganamos en probabilidades a la casa: la cuota la deciden ellos con
> miles de variables. No hay que romperse la cabeza esperando que Kelly sea
> positivo; con que no baje mucho alcanza. Lo nuestro es el **win rate** y
> **saber dónde poner la plata**, aunque la cuota sea 1.02.

Con eso, el método **apuesta siempre a nuestro elegido** (no busca valor
contra el mercado) y la única pregunta es **cuánto** y **en qué tramo**.

## El método: proporcional con freno por tramo

- **Monto**: el 1 % de la banca ya cobrada (`PROPORCION`) a nuestro elegido.
  Crece cuando la banca crece y se achica sola cuando cae; no quiebra.
- **Freno**: por tramo de confianza del elegido (`<40 · 40-49 · 50-59 · 60+`,
  los de `lecciones.TRAMOS_CONFIANZA`). Se miran los últimos
  `FRENO_VENTANA` = 50 partidos cerrados del tramo y se compara cuánto acertó
  con lo que pedía la cuota (media de 1/cuota). Con al menos
  `FRENO_MINIMO` = 15 partidos y más de `FRENO_Z` = 0,5 errores estándar por
  debajo, el tramo se **pausa**.
- En pausa el tramo **sigue anotando** (los partidos sin apuesta cuentan), así
  que vuelve solo cuando se recupera. La ventana móvil hace que una versión
  vieja mala del skill (v4.0) no castigue para siempre a la nueva.

Código: `backend/analisis/simulacion.py` (`proporcional`, `freno_tramo`),
serie `proporcional` de `GET /analisis/simulacion`, tarjeta «Proporcional con
freno · el método» en la sección Simulación con el estado de cada tramo.

## La investigación

Datos: 374 partes con 1X2, cuota prepartido y resultado, del 15/09 al
01/11/2026 (sin copas nacionales, sin cuarentena, depositados antes del
pitazo). Bajados por la API con el token de Cowork (el `/analisis/simulacion`
no está abierto a ese token) y pasados por la misma cuenta. Win rate 55,6 %
contra 54,8 % que pedían las cuotas; antes del 28/10, 51,2 % contra 54,3 %;
desde el 28/10, 61,3 % contra 55,6 %.

Cada método decide **solo con lo ya jugado**. Tres pruebas:

1. la secuencia real (todo, antes y desde el 28/10);
2. **remuestreo por días** (2.000 réplicas: se sortean días enteros con
   reemplazo, para que los días malos queden juntos);
3. **sin ventaja**: el mismo remuestreo, pero cada resultado se sortea con la
   probabilidad del mercado sin margen. Es lo que pasa si nuestro win rate
   vuelve a ser el de la casa: el método tiene que sobrevivir a eso.

| Método | Real (todo) | Remuestreo p05 · mediana · caída p95 | Sin ventaja: mediana · caída p95 · P(banca < 50) |
|---|---|---|---|
| Plana 1 u | 109,4 | 72 · 110 · 38 % | 75 · 63 % · 11,5 % |
| Proporcional 1 % | 107,9 | 74 · 109 · 35 % | 77 · 49 % · 2,0 % |
| **Proporcional 1 % + freno (ventana 50, z 0,5)** | **111,0** | **88 · 115 · 22 %** | **85 · 33 % · 0 %** |
| Kelly del tramo ½ | 134,2 | 53 · 137 · 62 % | 67 · 71 % · 21 % |
| Fibonacci | 148,5 | 97 · 151 · 43 % | 60 · 100 % · 48 % |
| D'Alembert | quiebra | 0 · 123 · 100 % | 0 · 100 % · 76 % |
| Martingala | 255,2 | 161 · 259 · 48 % | 0 · 100 % · 68 % |

Lectura:

- **Las progresiones (martingala, Fibonacci, D'Alembert) no agregan ventaja.**
  Lo que ganan lo pone el win rate. Ellas solo deciden cuánto se arriesga
  cuando viene una racha mala. En los datos reales no hubo la racha larga que
  las rompe; sin ventaja quiebran la mitad de las veces o más.
- **Kelly del tramo** (Kelly sobre el win rate real del tramo, no sobre la
  probabilidad del skill) gana más cuando la ventaja existe, pero con caídas
  del 60 % en el peor 5 % de los casos. Depende de que la ventaja se sostenga.
- **El freno** es lo que más protege y lo que menos cuesta: la peor caída
  baja de 35 % a 22 % y, sin ventaja, la banca no pasa de 50 en ninguna
  réplica. En el tramo bueno (desde el 28/10) casi no frena: 120 contra 122
  del proporcional sin freno.
- Las variantes del freno (ventana 30 o 50, z 0 · 0,5 · 1, tres tramos o
  cuatro, acelerador al doble con un tramo muy bueno, 1,5 %) dieron todas
  parecido, dentro del ruido. Se eligió la más simple con fundamento (ventana
  de 50, la mitad de la tolerancia, los tramos que ya usa Aprendizaje) y no
  la que mejor salió por casualidad.

Sobre la simulación del sistema (desde el 28/10, con el tiempo real de la
pantalla), el método queda en 125,59 con una caída máxima de 7,6 % y una sola
pausa en 165 partidos.

## El criterio de contacto (04/11/2026)

El usuario: «me sigue sorprendiendo cómo crece la martingala en la
simulación… las gráficas son muy reveladoras». Medido ese día:

- En nuestros 374 partes (15/09-01/11), después de varios fallos seguidos del
  elegido se acertó MÁS: tras 2 fallos 58,9 % (73 casos), tras 3 66,7 % (30) y
  tras 4 80,0 % (10), contra un promedio de 55,6 %. Eso es lo que la martingala
  cobra: ahí ganó +16,9 % por unidad apostada contra +2,5 % de la plana.
- En los 2.638 partidos de liga de la base, con el favorito de la casa en
  orden de fecha, NO aparece: tras 3 fallos 51,0 % (251 casos), tras 4 47,2 %
  (123); la racha más larga fue de 10 y la martingala pura quiebra.
- Los mismos 374 partes en otro orden (2.000 órdenes al azar): la martingala
  termina bajo 50 o quiebra el 41 % de las veces.
- 20 de 30 y 8 de 10, con un acierto de 55,6 %, salen por azar ~1 vez en 10.

No se descarta ni se cree: **se mide con una regla fijada antes de mirar los
datos nuevos**, que no se mueve para que se cumpla. **Contacto** = 100+ casos
tras 3 fallos seguidos, acierto de 65 %+ y el intervalo de confianza (Wilson
95 %) entero por encima del promedio. La cuenta es `simulacion.tras_fallos`
sobre las apuestas cerradas de la simulación (desde el 28/10, en orden de
pitazo), viaja en `trasFallos` de `GET /analisis/simulacion` y la sección
Simulación la muestra en la tabla «Criterio de contacto».

**Se mide cada fin de semana**: la rutina «SAD · criterio de contacto
(semanal, v2)» (`trig_01FPQZSDDb1GsMtYdbKAAFYu` desde el 09/11, en su propia
sesión; la v1 `trig_011ha3sLwm2qqjCpfpHLmFYx` quedó desactivada; lunes 07:43 de Lima, para que
entren los partidos del domingo por la noche) corre `python -m backend.contacto`,
que rearma las mismas apuestas desde la API con el token de Cowork (la
simulación no está abierta a ese token) y reporta la tabla y el estado. El
primer conteo, el 04/11: 9 casos tras 3 fallos desde el 28/10 (6 aciertos), a
~9 por semana: el criterio se puede decidir hacia febrero de 2027.

## El semáforo del elegido, por las espinas (13/11/2026; antes 11/11/2026)

El usuario: «me apoyaré de ese semáforo». No lee la prosa del parte: mira la
etiqueta del elegido, y esa etiqueta lleva un color CALCULADO
(`backend/analisis/semaforo.py`; el parte no declara nada de esto). Desde el
13/11/2026 el color dice **dónde NO meter plata**, no si hay value en la
cuota (usuario, tras Italia 3-1 Francia en verde: «no encontramos value a la
cuota; el semáforo dice: por más que la casa diga esto, estas otras cosas
hacen que mejor no apostemos»). Sale de las **espinas** del parte
(`lecturaSad.espina.{a,b}.lectura`, la lectura de las K que escribe el
analista):

- 🟢 **confirma**: la espina del elegido lo acompaña (positiva) y la del
  rival no dice que siga (negativa o neutra).
- 🟡 **duda**: la espina del elegido dice cero (empate), o la del rival dice
  positiva o cero; `motivos` dice cuál (`ESPINA-ELEGIDO-EMPATA` ·
  `ESPINA-RIVAL-SIGUE`).
- 🔴 **noApostar**: la espina del elegido dice negativa
  (`ESPINA-CONTRA-EL-ELEGIDO`): el analista leyó que su elegido pierde y lo
  eligió igual.
- ⚪ **sin dato**: sin el 1X2 o sin la espina del elegido (falta o es neutra).
- El elegido **empate**: verde con las dos espinas en cero; si no, amarillo.

La distancia a la casa y el signo del marcador viajan como información: no
deciden.

Medido el 13/11 sobre 721 partes acreditables (14/09-12/11, sin copas
nacionales), en la conversación que lo pidió:

- Con la espina del elegido positiva el elegido ganó **59 %** (n 601); con
  cero, **44 %** (34); con negativa, **26 %** (19). Con la espina a favor el
  elegido le sacaba ~7 pts al mercado; con la espina en contra quedaba ~5
  pts por debajo.
- Verde contra amarillo (la regla de arriba): **59 %** contra **43 %** (75
  amarillos), +16 pts en los partidos hasta el 01/11 (donde se eligió) y +17
  en los del 02/11 al 12/11 (donde se comprobó).
- Lo que NO separa, medido el mismo día: la burbuja del elegido (de un
  partido, riesgo alto o en récord: en récord gana MÁS) y la rotación del
  once (no revienta burbujas más que su riesgo).

La regla del 11/11 (≤ 2 pts de la casa en los tres resultados y el marcador
con el elegido) quedó atrás: medía cercanía a la cuota, no desconfianza, y
pintaba verde casi todo (verde 66 % contra amarillo 50 %, con el 57 % de los
partidos en amarillo).

Se encontró mirando esos mismos datos, así que **se mide hacia adelante con
una regla fija** (como el criterio de contacto, no se mueve): cuenta desde
los partidos del **13/11/2026** (00:00 de Lima, `semaforo.DESDE`).

### El criterio por escalones de no-verdes (13/11/2026)

Lo que se juzga es si la desconfianza acierta: el elegido en amarillo o rojo
tiene que ganar MENOS que en verde. Los no-verdes son los raros (~10 % de los
partes), así que los escalones se cuentan con ellos
(`simulacion.criterio_semaforo`). Con *n* amarillos + rojos nuevos cerrados e
IC = el intervalo de Wilson al 95 % de su acierto:

| escalón | estado |
|---|---|
| antes de 30 | `en_observacion` (con `faltan` hasta el 30), pase lo que pase |
| cualquiera | `no_se_sostiene` si los no-verdes aciertan lo mismo o más que los verdes |
| **30** | `prometedor` si el verde acierta **10+ pts** más; si no, `en_observacion` |
| **60** | `confirmado` con 10+ pts y el límite **superior** del IC de los no-verdes por debajo del acierto del verde; si no, `sin_contacto` |

Solo `confirmado` es tomarlo en serio. La cuota va al lado como información
(«pedía» y la plana a 1 u por color), nunca como criterio.

El estado viaja con `escalon` (0 · 30 · 60), `proximoEscalon`, `faltan`,
`verdes`, `noVerdes` (con su IC), `separacion` y un `texto` en español. La
cuenta es `simulacion.resumen_semaforo` (campo `semaforo` de
`GET /analisis/simulacion`, tabla «Semáforo del elegido · por las espinas»
en la pantalla, con verde, amarillo, rojo y sin dato), con la serie en papel
**`metodoVerde`**: el método (1 % de la banca y el mismo freno por tramo)
apostando SOLO en verde. La rutina de los lunes la reporta en la sección
«Semáforo» de `python -m backend.contacto`.

**REGLA ANTI-GOODHART**: el semáforo NO se le muestra a Cowork ni al
analista —ni en el recibo del depósito, ni en el prompt, ni en ningún
endpoint que lea su token—. Si lo viera, aprendería a «pintarse de verde»
escribiendo la espina a favor de su elegido y la señal moriría. Viaja solo en `/analisis/simulacion`
y en `/analisis/semaforo` (el chip de la web), que el token de Cowork no abre;
`backend/test_semaforo.py` lo verifica.

## El marcador más probable con el elegido (13/11/2026)

El usuario: «si el marcador más probable se alinea con lo que dice el parte…
lo más probable es que gane»; y después: «la filosofía no era medir contra la
cuota, era medir si nuestro win rate mejoraba». Es el marcador más probable
del **modelo de goles** (`goles.acotar_fixture`, `masProbables[0]`, el de la
lista de Partidos), no el que declara el analista (decisión del usuario el
13/11: «el calculado»). Sale de la historia ANTERIOR al partido, así que al
minuto 0 es el mismo que en cualquier lectura. **Alineado** = su signo es el
elegido (1-0 o 2-1 con el local elegido, 0-1 con la visita).

Medido el 13/11 sobre 748 partes con veredicto (14/09-13/11, sin copas
nacionales, elegido local o visita):

- win rate **66,7 %** con el marcador alineado (n 210) contra **52,3 %** con
  1-1/0-0 (n 533); 67 % contra 51 % hasta el 31/10 y 66 % contra 56 % desde
  el 01/11. Los tres más probables con el elegido: **83 %** (n 53).
- Dentro del verde del semáforo separa otros 10 pts: verde y alineado 66 %
  (n 187), verde con 1-1 56 % (n 392), no-verde con 1-1 38 % (n 65).
- Contra la cuota no separa (el alineado aparece con favoritos claros: la
  casa pedía 60 % contra 48 %), y apostar solo a los alineados dio ROI plano
  +3,8 % contra +5,2 % de todos. Se juzga el win rate; la banca de las series
  dice lo otro.

Se encontró en esos datos: **se mide hacia adelante** desde los partidos del
**14/11/2026** (00:00 de Lima, `simulacion.MARCADOR_DESDE`) con un criterio
fijo por escalones de **alineados** nuevos cerrados
(`simulacion.criterio_marcador`):

| escalón | estado |
|---|---|
| antes de 30 | `en_observacion` |
| cualquiera | `no_se_sostiene` si los alineados no ganan más que el resto |
| **30** | `prometedor` con **10+ pts** de win rate sobre el resto |
| **60** | `confirmado` con 10+ pts y el límite **inferior** del IC de los alineados por encima del resto; si no, `sin_contacto` |

Se mide en la tabla «Marcador más probable · con el elegido» de
`GET /analisis/simulacion`. Tuvo tres series en papel (`metodoMarcador`,
`metodoVerdeMarcador` y una martingala 🟢⚽) que el usuario quitó el mismo 13/11:
ver «Las puntas contra el medio». Queda **`martingala60Ajustada`**, la martingala
de 60 %+ AJUSTADA A LA CUOTA: tras perder apuesta
**1 + lo perdido en la línea / (cuota − 1)** (la clásica duplica y solo recupera
con cuota 2,00+). La rutina de los lunes lo reporta en la sección
«Marcador» de `python -m backend.contacto`. Este marcador lo ve también el
analista (va en `golesAcotados` del parte): no es una señal que él pueda
pintar, porque sale de la base.

## Las puntas contra el medio (13/11/2026)

El usuario: «siento que hay una forma correcta de apostar… por un lado un gran
win rate, por otro buena ganancia con un bajo win rate». Las dos cosas son la
misma: la plata sale de la **ventaja** (acierto − lo que pide la cuota), y la
ventaja está en las dos PUNTAS de lo que la casa (sin margen) le da al elegido.
Medido sobre 748 partes (14/09-13/11, elegido local o visita, 1 u plana):

| la casa le daba | n | acierta | pedía | ventaja | plana |
|---|---|---|---|---|---|
| < 40 % | 156 | 43 % | 35 % | +8,4 | +21,1 % |
| 40-50 % | 231 | 49 % | 45 % | +4,7 | +3,1 % |
| 50-60 % | 176 | 53 % | 55 % | −1,5 | −8,6 % |
| 60-70 % | 97 | 75 % | 64 % | +11,3 | +10,1 % |
| 70 %+ | 88 | 85 % | 76 % | +9,0 | +5,0 % |

Sin el medio (45-60 %): +11,5 % (n 465; +12,3 % hasta el 31/10 y +9,9 %
después) contra +5,2 % de todos y −5,0 % del medio solo (n 283; −4,8 % y
−5,4 %). El marcador alineado era la punta de los favoritos; por eso subía el
win rate y no la plata. Pistas más débiles, sin serie: con la visita elegida
+14,6 % (n 231) contra +1,0 % con el local.

Los cortes (45 y 60) salieron de esos datos: **se mide hacia adelante** desde
el 14/11/2026 (`simulacion.MEDIO_DESDE`) con la serie en papel
**`metodoFueraMedio`** (el método sin apostar en el medio) y un criterio fijo
por escalones de partidos nuevos del MEDIO (`simulacion.criterio_medio`). Acá
el criterio SÍ mira la cuota, porque el hallazgo es ese:

| escalón | estado |
|---|---|
| antes de 30 | `en_observacion` |
| cualquiera | `no_se_sostiene` si la ventaja del medio no es menor que la de las puntas |
| **30** | `prometedor` si las puntas le sacan **5+ pts** de ventaja al medio |
| **60** | `confirmado` con 5+ pts y la plana de las puntas en positivo y sobre la del medio; si no, `sin_contacto` |

Con las mismas puntas corrían dos martingalas AJUSTADAS A LA CUOTA (pedido del
usuario, 13/11): `martingalaFueraMedio`, que en cada apuesta buscaba TODA la
deuda de la línea, y la misma con un tope del 25 % de la banca.

### Cómo se pone la plata fuera del medio (14/11/2026)

El usuario: «viendo que el control seguía creciendo, es evidente que estamos
poniendo mal la plata». La ajustada cayó de 117,66 a 92,18 en UN partido
(2 de Mayo – Sportivo Trinidense, 03/11) con el control subiendo. No era un
error de cuenta: la línea 9 venía de cinco derrotas (Feyenoord a 1,15,
Peñarol, Caracas, Huachipato, Elche: deuda 1 → 29 u), repartidas entre ~70
partidos que las otras líneas ganaban; la sexta fue de 25,49 u (deuda 54 u) y
se rescató con 90 u a cuota 1,35 y 104 u a cuota 1,23. Una martingala no
sigue al control: en el mismo partido ganan o pierden juntas, pero ella pone
20-30 veces más cuando su línea arrastra deuda.

Backtest sobre los mismos 240 partidos fuera del medio de producción
(28/10-13/11, 100 u, cuota = media de las casas; la reconstrucción da las
bancas de producción al centavo). «Cae con el control subiendo» = la peor
caída entre dos momentos en que la plana fuera del medio no bajó:

| cómo se pone | banca | caída máx | apuesta máx | cae con el control subiendo |
|---|---|---|---|---|
| plana 1 u (control) | 126,1 | 6,7 % | 1,0 | — |
| ajustada, toda la deuda (la de antes) | 207,3 | 27,2 % | 104,0 | **27,2 %** |
| ajustada, deuda solo con las sorpresas (cuota ≥ 1,6) | 184,5 | 14,6 % | 10,1 | 7,9 % |
| ajustada, recupera ½ | 160,1 | 8,4 % | 28,1 | 4,3 % |
| **ajustada, recupera ⅓** | **150,0** | **7,9 %** | **16,3** | **2,2 %** |
| ajustada, recupera ¼ | 144,6 | 7,5 % | 11,8 | 1,8 % |
| proporcional 2 % | 161,5 | 16,7 % | 3,6 | 0,9 % |
| **proporcional 3 %** | **199,1** | **24,4 %** | **7,0** | **2,1 %** |

Lo de «solo con las sorpresas» es frágil: con el corte en 2,2 la caída sube a
49,9 %. **`martingalaFueraMedio`** pasa a buscar un TERCIO de la deuda por
apuesta (1 + (lo perdido en la línea / 3) / (cuota − 1); el acierto descuenta
lo que gana; `simulacion.RECUPERA_FUERA_MEDIO`). La del tope salió: recortaba
la apuesta y la línea seguía cargada.

### El orden de las apuestas: la mixta (14/11/2026)

El usuario: «el nuevo método tiene que ver con tener cuidado con el orden de
las apuestas». Con los mismos 240 partidos, barajando 1000 veces qué partido
cae en qué horario (aciertos y cuotas reales; solo cambia dónde caen las
rachas):

| cómo se pone | banca típica | 10 % peor | caída típica | caída 10 % peor | caída 1 % peor | termina bajo 100 u | quiebra |
|---|---|---|---|---|---|---|---|
| ajustada, toda la deuda (la de antes) | 201 | 5 | 24 % | 99 % | 100 % | 14 % | **10,7 %** |
| martingala ⅓, 1 u | 149 | 137 | 11,8 % | 23,4 % | 53,4 % | 0,9 % | 0,1 % |
| martingala ⅓, 2 u | 199 | 171 | 20,3 % | 40,4 % | 92,2 % | 1,5 % | 0,5 % |
| mixta 2 % | 150 | 148 | 13,5 % | 19,2 % | 25,6 % | 0 % | 0 % |
| **mixta 3 %** | **179** | **176** | **19,8 %** | **27,8 %** | **36,4 %** | **0 %** | **0 %** |
| mixta 4 % | 212 | 205 | 25,8 % | 35,8 % | 46,8 % | 0 % | 0 % |
| proporcional 3 % | 198 | 191 | 25,8 % | 34,7 % | 46,8 % | 0 % | 0 % |
| plana 1 u (control) | 126 | 126 | 8,1 % | 11,5 % | 16,6 % | 0 % | 0 % |

Las 207 u de la ajustada de antes fueron suerte del orden; toda martingala
tiene esa cola. La **MIXTA** pone en el favorito (cuota hasta 2) el X % de la
banca y en la sorpresa lo que GANA ese X %: X % / (cuota − 1). No mira lo que
pasó antes, así que no depende del orden y sigue al control; a igual
ganancia cae menos que la martingala ⅓ (2 %) y a igual caída gana más que la
proporcional (4 % contra 3 %). La ganancia y la caída suben juntas con el
porcentaje: elegirlo es elegir cuánto se aguanta. Decisión del usuario
(14/11): **`mixtaFueraMedio` al 3 %** (`simulacion.MIXTA_FUERA_MEDIO`; en el
orden real, 180,5 u con apuesta máxima de 5,9 u), al lado de la martingala ⅓
para ver en vivo cuál aguanta las rachas. Se miden hacia adelante: 240
partidos en 17 días es poco para dar el 3 % por bueno.

Tabla «Las puntas contra el medio» en la pantalla y sección «Fuera del medio»
del informe de los lunes. El mismo 13/11 el usuario quitó de la Simulación las
series del marcador (`metodoMarcador`, `metodoVerdeMarcador` y la martingala
🟢⚽ ajustada, que con 100 u quebró en una racha: con cuotas de 1,45 la apuesta
crece ×3,2 por derrota). La tabla de win rate del marcador y su criterio siguen.

## La martingala cuidada y «ganar fijo» (18/11/2026)

El usuario: «veo a martingala hasta el culo… es como que no supiera en qué
partido duplicar». Sobre los 447 partidos cerrados de producción (28/10-17/11;
la reconstrucción da las bancas de la pantalla al centavo), la clásica cayó de
211 u a 5,50 u: duplicaba a ciegas y sus apuestas de 64 u y 86 u fueron en el
medio, donde no hay ventaja.

**`martingalaCuidada`**: sin medio, la unidad de cada ciclo es el 1 % de la
banca cobrada y tras 3 derrotas seguidas la línea acepta la pérdida (1 · 2 · 4
y corta). Orden real 169,7 u (caída 14 %, apuesta máxima 6,7 u); barajada 1000
veces no quiebra; sin ventaja termina bajo 50 u el 13 % (la clásica quiebra el
60 %). Sin el corte («cuidada sin límite», pedida por el usuario para mirarla,
no se agregó): 134,3 u, caída 44 %, quiebra el 7 % de los órdenes y el 39 % sin
ventaja. Cortar a 4 quiebra el 10 % sin ventaja; a 2 es casi la plana.

**`ganarFijo`** salió de buscar algo mejor que la mixta 3 %. Lo que deja la
plana por unidad, según lo que la casa le da al elegido:

| franja | n | acierta | la cuota pide | plana |
|---|---|---|---|---|
| < 40 % | 81 | 44,4 % | 39,7 % | +12,0 % |
| 40-45 % | 72 | 50,0 % | 45,4 % | +10,0 % |
| medio 45-60 % | 177 | 54,8 % | 55,4 % | −0,3 % |
| 60-70 % | 60 | 75,0 % | 68,7 % | +10,0 % |
| 70 %+ | 57 | 93,0 % | 82,0 % | +13,6 % |

Con el mismo rendimiento en todas las puntas, conviene poner más donde menos
se falla. La regla (`simulacion.GANAR_FIJO`, `TOPE_GANAR_FIJO`):

- cada apuesta busca GANAR el 2,5 % de la banca cobrada: 2,5 % / (cuota − 1),
  sin pasar del doble (5 % de la banca; el tope pega con cuota bajo 1,50);
- no apuesta en el medio;
- no apuesta con el semáforo fuera de verde;
- no apuesta cuando le damos al elegido más de 2 puntos sobre la casa
  (`ALERTA_SOBRE_CASA`: 46 partidos a −14 % ± 17 por unidad contra +9 % de los
  otros 401);
- freno por franja con la regla del método (ventana 50, mínimo 15, z 0,5):
  sorpresas (casa bajo 45 %) y favoritos (60 %+) se pausan por separado.

| | orden real | caída real | barajado: típica · 10 % peor | caída 10 % peor | le gana a la mixta (remuestreo por días) | sin ventaja: bajo 50 u |
|---|---|---|---|---|---|---|
| mixta 3 % | 207,4 | 15,6 % | 205 · 201 | 27,8 % | — | 32,8 % |
| **ganar fijo 2,5 %** | 204,3 | 17,1 % | 253 · 229 | 24,2 % | 78,4 % | **4,6 %** |

Sin el freno y sin exigir verde gana más (a igual riesgo, 280 u en el orden real) pero sin
ventaja termina bajo 50 u el 46 % de las veces: mueve más plata. En el orden
real el freno pausó a destiempo en la primera mitad (126 · 162 por mitades
contra 151 · 138 de la mixta); la mejora está en los remuestreos y en la
protección. Es la misma muestra donde salieron el medio y la alerta: se mide
hacia adelante, al lado de la mixta 3 %.

Lo que se miró y NO separa (mismos 447): el marcador alineado (+5 % contra +7 %), cubrir el empate y apostar
contra el descarte (−2 %: se paga el margen dos veces) y local contra visitante
(+2 % contra +16 %, dentro del error).

**Cuándo no apostar** (usuario, 18/11: «lo que buscamos es aumentar el win
rate y saber cuándo no apostar»). Es lo propio del sistema que separa:

| | n | acierta | la cuota pide | plana |
|---|---|---|---|---|
| todos | 447 | 59,7 % | 56,1 % | +6,7 % |
| apostables (semáforo verde y sin pasarnos de la casa) | 365 | 64,7 % | 58,3 % | +12,0 % ± 4,7 |
| no apostar (no verde o nos pasamos) | 82 | 37,8 % | 46,6 % | −16,6 % ± 12,2 |

La diferencia es de 2,2 errores, algo inflada: las dos reglas se fijaron con
datos que se pisan con estos. El semáforo solo (37 no verdes, −15 % ± 19) casi
no mueve el total; junto con «nos pasamos» sí.

**El control del favorito (18/11).** El elegido coincide con el favorito de la
casa en 428 de 447 y rinde igual (+6,7 % contra +6,8 %). Apostando siempre al
favorito de la casa, por unidad: partidos con parte +6,6 % ± 4,4 (441); mismas
semanas, sin parte, en otras ligas −7,1 % ± 3,0 (862); nuestras 23 ligas antes
(01/08-27/10) −3,5 % ± 2,7 (1.271). No fue una racha general de favoritos ni
algo permanente de esas ligas, y no elegimos partidos dentro de la liga (449 de
497 con parte). La ventaja de base no se puede atribuir al elegido: lo que el
sistema aporta de forma medible es el «no apostar». Toda serie de la
Simulación reparte esa ventaja; si se corta, vuelven a perder el margen (7,6 %).

**La liga, como medición (decisión del usuario, 18/11).** Perú (281), Uruguay
(268), Venezuela (299), Bolivia (344) y Ecuador (242) sumaron 81 partidos a
−32 % ± 10 por unidad contra +15 % del resto, pero se agruparon DESPUÉS de ver
el resultado, y un freno por liga que aprende sobre la marcha no lo captura
(194-212 u contra 207; con las ligas repartidas al azar da lo mismo: cada liga
tiene 13-28 partidos). Los partes de antes cambiaron con las versiones y no
sirven para sostenerlo. Queda como hipótesis con el grupo FIJO (esas cinco
ligas) y cuenta desde los partidos del 18/11/2026: no cambia ninguna apuesta.
Todavía no tiene tabla en la pantalla.

## El equipo contra sí mismo, contra la cuota (21/11/2026)

El usuario, tras Bayern 1-1 Köln: «si sabés que Bayern pierde 1 de cada 8,
en esos 8 decime cuál es el más bajo: el equipo puede compararse contra sí»,
y «no se consideraba que fuese a responder el equipo rival». Bayern venía
ganando 6 de sus últimos 10 oficiales y la casa le daba 87 %; Köln venía
marcando en 8 de 10.

`backend/backtest_forma_cuota.py` (test: `backend/test_backtest_forma_cuota.py`)
lo mide contra la CUOTA, no contra el motor: para el favorito de la casa
(≥ 50 % sin margen), su forma de los últimos 10 oficiales y la del rival,
solo con partidos anteriores, y el residuo ganó − probabilidad de la casa, con
intervalo por bootstrap de equipos y la plana a la cuota media. Señales: la
forma del favorito 20+ pts debajo de lo que le da la casa (o arriba), el
favorito que viene recibiendo, el rival que no pierde o que marca seguido, y
las dos a la vez. Una señal cuenta como firme solo si separa en todo el
período y también en cada mitad, en el mismo sentido. Sin copas nacionales.

**Primera mirada (21/11, 385 partes acreditables, dos meses):** el favorito
con la forma 14+ pts debajo de la casa ganó el 69,5 % contra el 57,6 % que
decía la casa (n 128; la diferencia contra el grupo de forma arriba, IC −0,2
a +21). Al revés de la intuición: la casa mira la calidad, no solo los últimos
resultados (los empates de Bayern venían con xG de 2,5 a 5,1). El rival que no
pierde o que marca no separó (IC −12 a +7). Sin probar en ningún sentido.

**Corrida del padrón (21/11/2026, servidor):** 1.249 favoritos de la casa con
cuota, del 23/08 al 20/11/2026 (las cuotas guardadas no dan para más). Los
favoritos ganaron el 65,8 % contra el 62,6 % que decía la casa, y la plana
dio −2,4 % por el margen. **Ninguna señal separa y se repite.**

| Señal | n | Diferencia contra el resto | IC 95 % |
|---|---|---|---|
| favorito con la forma 20+ pts debajo de la casa (Bayern) | 411 | −1,9 pts | −7,5 a +3,6 |
| favorito con la forma arriba de la casa | 316 | +0,9 | −5,3 a +6,2 |
| favorito que recibió en 7+ de 10 | 697 | −2,6 | −7,9 a +2,3 |
| **rival que no perdió 6+ de 10** | 682 | **−5,2** | **−10,4 a +0,1** |
| rival que marcó en 8+ de 10 | 498 | −2,7 | −7,8 a +2,7 |
| las dos (favorito 20+ debajo y rival que no pierde) | 181 | −4,6 | −11,9 a +3,0 |

- **El favorito contra sí mismo no avisa nada.** Lo de los 385 partes (+12
  pts, «al revés») era ruido.
- **El rival que no pierde** es lo único que se acerca, en la dirección del
  usuario, pero no se repite: −1,8 pts antes del 18/10 (IC −9,7 a +5,4) y
  −8,4 desde el 18/10 (IC −15,1 a −1,1). Donde pesa es en el favorito MEDIO:
  con la casa entre 50 y 70 %, contra un rival que no pierde el favorito ganó
  lo que decía la casa (58,1 contra 58,0 %, n 539, plana −7,0 %); sin ese
  rival le sacó 6 pts a la casa (64,4 contra 58,4 %, n 421, plana +1,9 %).
  Con la casa en 70 %+ casi no cambia (+4,0 contra +6,5 pts). Es una de
  seis señales y el tramo se miró después: un candidato, no una regla.

**Candidato fijado hoy para medir hacia adelante** (como el semáforo: la
regla no se mueve): *favorito de la casa entre 50 y 70 % contra un rival que
no perdió 6+ de sus últimos 10 oficiales* → no apostar. Cuenta desde el
22/11/2026; se re-corre el script con `--json` al juntar unos 300 casos
nuevos de ese grupo y se decide con eso. Hasta entonces no entra al semáforo.

**Validación del candidato** (pedido del usuario, 21/11/2026: «¿no hay forma
de confirmar eso por liga? ¿validar con burbujas?»):
`backend/backtest_rival_resiste.py` (test: `backend/test_backtest_rival_resiste.py`)
no cambia la regla: la pone a prueba (1) contra el NIVEL en los años que la
regla no vio (2019 → agosto 2026, sin cuotas; favorito = 0,5+ de nivel previo,
lo esperado sale de los casos sin la señal del mismo tramo y condición), (2)
contra la casa con el tramo 50-70 % aparte, y (3) liga por liga, con la prueba
del signo. La resistencia del rival se mide de cuatro maneras: la regla
(no perdió 6+ de 10), su racha sin perder de la condición de 3+, esa racha en
su récord y su perfil de doble oportunidad (no pierde el 60 %+ en la
condición). Sobre 73 equipos bajados (sin cuotas), ninguna de las cuatro
separa contra el nivel (la regla: +0,1 pts, IC −4,4 a +5,5, n 1.089) y las
ligas no se inclinan.

**Corrida del padrón (21/11/2026, servidor):** 43.160 favoritos por nivel
(2019-01 a 2026-11, 8.954 partidos de copa nacional fuera) y 1.253 por casa.
Residuo > 0 = con ese rival el favorito no gana MÁS de lo esperado.

| Resistencia del rival | Contra el nivel (años sin cuota) | Épocas | Ligas en el sentido | Contra la casa |
|---|---|---|---|---|
| no perdió 6+ de 10 (la regla) | **+2,6 pts** (IC +1,4 a +3,8, n 18.317) | +1,9 y +3,2, las dos separan | **45 de 64** (p 0,002) | −1,0 (IC −4,2 a +2,7, n 681) |
| racha sin perder de la condición 3+ | +0,7 (IC −0,6 a +2,3) | no | 26 de 48 | −0,7 |
| esa racha en su récord | −1,5 (IC −4,3 a +1,2) | no | 9 de 19 | +3,7 (n 40) |
| no pierde el 60 %+ en la condición (perfil DC) | **+8,5 pts** (IC +7,3 a +9,7, n 21.687) | +9,2 y +7,6 | **64 de 73** | −2,2 (IC −5,7 a +1,3, n 633) |

Lectura:

- **El rival que resiste es real en el fútbol**: contra lo que dice el nivel,
  el favorito gana menos contra un rival que viene sin perder y, mucho más,
  contra uno que históricamente no pierde en esa condición. Siete años, dos
  épocas, la mayoría de las ligas. Es lo mismo que el §15.1 de REVENTON ya
  había medido sobre el motor (el perfil DC lo mejora).
- **La casa ya lo cobra.** Contra la cuota los dos dan cero (−1,0 y −2,2 pts):
  el favorito contra ese rival gana lo que la casa dice. No hay valor en
  dejar de apostarle ni en apostarle en contra; la plana pierde el margen
  igual que en cualquier favorito.
- **Las burbujas no lo ven**: la racha sin perder abierta (3+ o en récord) no
  separa ni contra el nivel. La resistencia está en el perfil largo y en la
  forma, no en la racha.
- **Reserva**: lo esperado se estandariza con dos tramos de ventaja (0,5-1,0 y
  1,0+). Dentro de cada tramo, un rival que no pierde puede estar algo más
  cerca en nivel, y eso infla el «contra el nivel». Contra la casa no hay ese
  problema.

**El candidato** (favorito de la casa 50-70 % contra un rival que no perdió
6+ de 10 → no apostar) **no tiene base contra la casa**: en ese tramo, −0,2
pts (IC −4,6 a +4,3, n 538). Sigue anotado con su fecha, pero sin esperar
que separe. Para el análisis, sirve como LECTURA: cuando el motor se aparta
de la casa (o no hay cuota), el perfil DC del rival es lo que el nivel no ve.

**Leído como lo usa el método (el usuario, 21/11/2026: «nos guiamos del win
rate y de en qué partido no se puede confiar; no buscamos ventaja sobre la
casa»).** La pregunta entonces no es si la casa lo cobra sino si el ACIERTO
baja con la señal. Baja en todos los cortes, siempre en el mismo sentido:

| Grupo | Rival que no perdió 6+ de 10 | Rival que viene perdiendo |
|---|---|---|
| nuestros elegidos, todos (385 partes) | 54,8 % (n 217) | 60,2 % (n 171) |
| semáforo verde | 57,1 % (n 189) | 62,0 % (n 158) |
| semáforo verde y le dimos 60 %+ | 76,6 % (n 47) | 92,6 % (n 54) |
| padrón, favorito de la casa 50-70 % | 58,1 % (n 539) | 64,4 % (n 421) |
| padrón, favorito de la casa 70 %+ | 81,1 % (n 143) | 83,6 % (n 146) |

Siete años contra el nivel dan lo mismo en chico (+2,6 pts de «no gana»). El
tamaño honesto es de 2 a 6 puntos de acierto; el salto del verde 60 %+ (16
pts) sale de 101 partes y casi seguro está inflado. Y la señal es común: más
de la mitad de los elegidos tienen un rival que resiste, así que como «rojo»
dejaría fuera la mitad de las apuestas.

**Candidato para el semáforo, a medir hacia adelante desde el 22/11/2026**
(regla congelada; no cambia el semáforo hasta medirlo): *verde con un rival
que no perdió 6+ de sus últimos 10 oficiales → amarillo*. Se compara el
acierto del verde puro contra el verde con rival que resiste en los partes
desde esa fecha; la forma del rival se calcula después con
`/constantes/{id}?antesDe=` (no tiene fuga), así que no hace falta tocar la
app para medirlo.

**Por segmento** (usuario, 21/11/2026: «segmentar para equipos fuertes como
Bayern o Arsenal, donde la cuota está desbalanceada, para ampliar lo que
cazamos»). `backtest_rival_resiste` mide ahora, dentro de cada segmento
(favorito, muy favorito, gigante —nivel 3,5+ y 1,0+ de ventaja—, gigante con
1,5+, gigante de local, casa 70 %+ y 80 %+), cuánto falla el favorito con la
señal y sin ella, qué parte de los tropiezos caza, y la diferencia contra los
sin señal del MISMO tramo de 0,1 de ventaja (para no confundir la señal con
un rival más cercano en nivel), por época. **Primera mirada, 73 equipos sin
cuota:** en el total de favoritos la señal no pesa (−1,7 pts); en los
gigantes falla 43 % con el rival que no perdió 6+ de 10 contra 30 % sin él,
caza 2 de cada 3 tropiezos, y contra el mismo tramo de ventaja queda en +8
a +12 pts, con intervalos todavía anchos.

**Corrida del padrón (21/11/2026, servidor, 43.167 favoritos por nivel
2019-2026; «diferencia» = contra el mismo tramo de 0,1 de ventaja):**

| Segmento | Rival que no perdió 6+ de 10 | Rival que no pierde el 60 %+ en la condición (perfil) |
|---|---|---|
| favorito (0,5+) | falla 51 / 46 % · +1,2 (no separa) | falla 55 / 41 % · **+7,4** · caza 60 % · se repite |
| muy favorito (1,0+) | +1,0 (no separa) | falla 51 / 35 % · **+9,4** · caza 57 % · se repite |
| gigante (nivel 3,5+, 1,0+) | +2,1 (justo en el borde) | falla 45 / 30 % · **+8,2** · caza 67 % |
| gigante con 1,5+ | +3,8 (separa, no se repite) | falla 40 / 26 % · **+9,6** · caza 62 % |
| gigante de local | +1,8 (no separa) | falla 35 / 28 % · +3,3 |
| casa 70 %+ (n 291) | falla 19 / 17 % | falla 19 / 17 % |
| casa 80 %+ (n 75) | falla 14 / 8 % | falla 13 / 9 % |

- **La señal que sirve no es la forma reciente sino el PERFIL**: el rival que
  históricamente no pierde en esa condición. Con el control fino de ventaja,
  la forma queda en 1-4 pts (lo de los 73 equipos se achicó); el perfil queda
  en 7-10 pts en todos los segmentos de favoritos, en las dos épocas. Lo que
  la burbuja abierta no ve (§15.1 de REVENTON lo había medido sobre el motor).
- **Es un punto ciego del NIVEL, no de la casa**: con la cuota de 70 %+ el
  favorito falla casi igual con y sin el perfil (19 contra 17 %, 291 casos,
  pocos para cerrar). Donde nuestro número sale del motor (o no hay cuota en
  la app), el perfil del rival es lo que falta.

**Segundo candidato del semáforo, congelado el 22/11/2026** (se mide hacia
adelante junto al primero, sin tocar la app): *verde cuyo rival no pierde el
60 %+ de su historia en la condición de hoy (perfil DC de la tarjeta) →
amarillo*. Si los dos se sostienen, manda el de mayor diferencia de acierto.

## Las burbujas: cuándo no apostar (21/11/2026)

El usuario, tras Sportivo Ameliano 1-0 Sportivo Luqueño (1632063): «las
burbujas no tienen que decir quién gana, solamente cuándo no apostar» y «no
nos importa si la casa ya cobra». `backend/backtest_semaforo_burbujas.py`
(REVENTON §19) pinta el semáforo con la **tarjeta** de cada lado (la espina
que da la historia sola, `espinaTarjeta`) en lugar de la espina del
analista, y mira cuánto más pierde o empata el elegido con cada señal.
Corrida del padrón (21/11/2026; 71.781 favoritos por nivel 2019-2026, 2.648
favoritos de la casa desde agosto). Falla = el elegido no gana:

| tramo de la casa | marca no verde | falla con / sin | caza |
|---|---|---|---|
| todos | 35,5 % | 50,0 / 42,4 | 39 % |
| 45-60 % | 32,7 % | 50,3 / 45,1 | 35 % |
| 60 %+ | 23,8 % | 29,6 / 21,5 | 30 % |
| 70 %+ | 18,9 % | 18,2 / 17,8 | — |

Por nivel, 2019-2026: no verde 60,7 contra 50,3 % (rojo 61,6 contra 51,0),
en las dos épocas y en 41 de 55 ligas. En 70 %+ el semáforo de las tarjetas
no avisa; ahí avisa otra cosa: **el favorito que viene de empatar** (su K
total en 0, sin burbuja abierta) no ganó el 35,4 % contra 14,4 % (n 48; en
60 %+, 32,2 contra 21,5). No avisan (el elegido falla igual o menos): su
racha + en el extremo, que venga de perder, el rival que viene ganando y el
cruce de las dos burbujas.

Son ~100 combinaciones de señal y tramo con 2.648 favoritos de la casa: se
congela y se mide hacia adelante, sin tocar la app ni el semáforo.

**Tercer candidato del semáforo, congelado el 22/11/2026**: *elegido de la
casa por debajo de 70 % con el semáforo de las tarjetas en amarillo o rojo →
no apostar*. Amarillo o rojo con la misma regla de `analisis/semaforo.py`,
pero con la tarjeta de cada lado (`reventonCalculado.*.espinaTarjeta` del
parte, de la K total): rojo = la tarjeta del elegido dice que pierde;
amarillo = dice empate, o la del rival dice que gana o empata.

**Cuarto candidato del semáforo, congelado el 22/11/2026**: *elegido de la
casa de 70 %+ que viene de empatar (K total en 0 antes del partido) → no
apostar*.

**Cómo se miden** (los cuatro candidatos, juntos): en los partes desde el
22/11/2026 (00:00 de Lima), sin copas nacionales, el acierto del elegido con
la señal contra sin ella en su tramo, con los escalones de no-verdes del
semáforo (30 para mirar, 60 para decidir). Se juzga por acierto: cuánto más
pierde el elegido con la señal y qué parte de los tropiezos caza; nunca
contra la casa. La tarjeta y la K salen del parte y de
`/constantes/{id}?antesDe=` (sin fuga): no hace falta tocar la app para
medirlos.

**Quinto candidato del semáforo: el juicio del analista** (21/11/2026,
sad-analysis v4.8, 6-F; usuario: «sería bueno que también el analista diga: en
este partido creo que no entro»). El analista escribe en el parte
`pronostico.entrar` (entraria · dudo · noEntraria, con motivo de una lista
cerrada). *Elegido con «dudo» o «noEntraria» → no apostar.* La lista de
Partidos lo pinta (✋), así que el usuario lo ve; el analista sigue sin ver el
semáforo. Se mide desde la hora de subida de la v4.8 (`SUBIDA_VERSION`) con
los mismos escalones, por acierto: cuánto más pierde el elegido con su «no
entraría» que con su «entraría».

**Primera mirada hacia atrás** (21/11/2026, a pedido del usuario; no decide
nada): los candidatos 3 y 4 salieron del padrón histórico, así que los partes
del 13 al 21/11 (99 sin copas nacionales) son datos que no vieron. Elegido de
la casa bajo 70 % (87): con las tarjetas en amarillo o rojo ganó **14 de 22
(64 %)**, en verde **18 de 39 (46 %)** y sin dato 11 de 26: **al revés** de lo
que dice el candidato 3, con un margen de error de ±20 pts. Elegido de 70 %+
que venía de empatar: 2 de 2 ganados (Lituania, Alemania en Serbia). Muestra
mínima: la regla queda congelada y se decide con los 60 marcados desde el
22/11; si en 30 sigue al revés, el escalón la da por `no_se_sostiene`.

## Verde sin alertas (24/11/2026)

El usuario: «agrega las dos series a la simulación; también Martingala Cuidada y
Ganar Fijo adaptadas al verde sin alertas fuera del medio». Cuatro series
nuevas en `simulacion.ESTRATEGIAS`, cada una con su gráfica:

| serie | la que adapta | además no apuesta si… |
|---|---|---|
| `metodoVerdeSinAlertas` | `metodoVerde` (1 % y freno por tramo) | DESCONFIAR sobre el elegido o su burbuja en riesgo **alto** |
| `metodoVerdeSinAlertasFueraMedio` | lo anterior | y la casa le da al elegido 45-60 % |
| `martingalaCuidadaSinAlertas` | `martingalaCuidada` (ya sin el medio) | fuera del verde, DESCONFIAR o riesgo alto |
| `ganarFijoSinAlertas` | `ganarFijo` (ya en verde y sin el medio) | DESCONFIAR o riesgo alto |

La regla (`simulacion.bloqueo_sin_alertas`) mira DESCONFIAR en toda la
historia (la sellada manda; si no, `alerta_confianza`), no desde el 10/11, y
el riesgo de la burbuja total del elegido. El «muy alto» no entra: su elegido
ganó 66 % (32) en las dos semanas, contra 41 % del alto (63).

**Lo medido el día en que se armó** (partes cerrados bajados con el token de
Cowork, 1 u plana, mismas apuestas): 28/10-09/11 (167), verde 59,1 % (+6,5 u),
sin alertas 62,5 % (+9,1 u), sin alertas y fuera del medio 70,7 % (+12,3 u, 58
apuestas); 10/11-24/11 (227), verde 56,2 % (−14,7 u), sin alertas 62,9 % (+3,4
u), sin alertas y fuera del medio 69,9 % (+9,1 u, 93 apuestas). Por separado,
el semáforo no verde y DESCONFIAR separan en los dos periodos (el elegido gana
31-44 % con ellos contra 55-60 % sin ellos); el riesgo alto solo en el segundo.

**Se armó mirando esos partidos**: vale lo que pase desde el **25/11/2026**
(`SIN_ALERTAS_DESDE`). La rutina de los lunes lo informa en la sección «Verde
sin alertas» de `python -m backend.contacto`, contando solo desde esa fecha.

## El 1X2 ciego: nuestra lectura sin la casa (22/11/2026)

El usuario, al ver la banca caer 15 días seguidos: «no tenemos porcentaje
propio anotado y calibrándose. El analista se manda sus páginas de análisis,
se mete sus horas de feedback, para seguir a la casa… Tenemos como prioridad
mejorar el acierto, NO SACARLE MARGEN A LOS NÚMEROS DE LA CASA».

**Lo medido ese día** (393 partes 28/10-22/11 bajados con el token de Cowork y
pasados por `simulacion.simular`; la pantalla tenía 539):

| | partidos | acierto | la cuota pedía | plana | siempre al favorito de la casa |
|---|---|---|---|---|---|
| 28/10-07/11 | 150 | 61,3 % | 51,5 % | +11,4 % | +16,0 % |
| 08/11-22/11 | 243 | 53,1 % | 53,6 % | −9,2 % | −7,2 % |

- El elegido fue el favorito de la casa en el **97,5 %** de los partidos y
  quedó en promedio a **1 punto** de su probabilidad. La curva de la banca fue
  la curva de los favoritos: subieron de más hasta el 07/11 (no ganaron 37 de
  cada 100) y después se cayeron (no ganaron 46 de cada 100).
- Las reglas de anclaje del sad-analysis (v4.1 «el empate parte del mercado»,
  «el favorito no se recorta»; v4.5 «no restan bajo el mercado») corrigen el
  número HACIA la casa después de leerla, y la lectura propia no quedaba
  guardada: **no se podía saber si leemos bien o mal**. Los 10 partidos en que
  el elegido no fue el favorito (acertó 2) son los pocos donde la lectura
  sobrevivió a esas reglas, no una medición de la lectura.
- Lo que sí separó en los 15 días malos: el semáforo en duda o no apostar (28
  partidos, 32 % contra 56 % en «confirma») y el tramo de 60 %+ de la casa
  (+7 % y +8,5 % por unidad, las dos mitades).

**El ciego** (`backend/analisis/ciego.py`): el 1X2 del analista ANTES de ver
la cuota, sellado con `POST /analisis/cowork/{id}/ciego` (`{local, empate,
visita, porque}`), una vez, antes del parte y del pitazo (un parte de otra
fecha, el aplazado de `aRehacer`, no cuenta: `parte.existe_vigente`, 1491). Con el token de
Cowork, las cuotas de un partido por jugarse dan 409 hasta el sello y la
`ventajaPorFuerza` del TDE viaja tapada (sale de la cuota). El maestro y la web
leen todo como siempre. La prensa puede traer cuotas: el prompt pide no
buscarlas, y eso no se puede verificar.

**Cómo se mide** (`ciego.resumen`, campo `ciego` de `GET /analisis/simulacion`,
tabla «Nuestro 1X2 ciego» arriba en Simulación, sección «1X2 ciego» de
`python -m backend.contacto` los lunes): desde los partidos del **23/11/2026**,
en las cerradas con ciego, el acierto del elegido del ciego, del publicado y
del favorito de la casa **en los mismos partidos**, con su IC; el desacuerdo
(el ciego no eligió al favorito: quién acertó); y la calibración del ciego por
tramo (lo que dijo contra lo que pasó). El Brier y la distancia a la casa van
como información. Con menos de 60 partidos es observación.

**Lo medido en los primeros 31** (todos del domingo 22/11, bajados el 24/11
con el token de Cowork; con el `DESDE` en el 23/11 la tabla de la app los
dejaba fuera y desde ese día cuenta desde el 22/11): ciego, publicado y
favorito de la casa acertaron los TRES 21 de 31; el Brier del ciego fue 0,519
contra 0,475 del publicado y 0,471 de la casa. El ciego le dio a su elegido 9
puntos menos que la casa en promedio y comprimió todo hacia el medio: dijo
45 % y ganó 36 % (14), dijo 53 % y ganó 100 % (10), dijo 63 % y ganó 80 %
(5); al empate le dio 26,5 % y hubo 3 empates (10 %). El publicado quedó a 1,1
puntos de la casa: las reglas de anclaje lo devuelven a la cuota (DEUDA 42).
Observación de un día, no conclusión.

**El espejo** (24/11/2026, usuario: «feedback inmediato y empezar a calibrar
esos porcentajes»): `GET /analisis/cowork/ciego/espejo` (`ciego.espejo`) es
esa misma calibración propia SIN la casa, para que el analista la lea ANTES
de sellar: por tramo, lo que le dio al elegido contra lo que ganó (`lectura`
corto / largo desde 5 partidos y 10 puntos de desvío) y el empate dicho contra
el que hubo. Se recalcula en cada llamada (cada veredicto cerrado ya entra:
ese es el feedback inmediato) y la corrida de partes lo pide una vez y lo pasa
a cada subagente. No corrige el número solo: el analista dice en el `porque`
si lo usó. La rutina de los lunes («contacto y semáforo») lo informa con la
sección «1X2 ciego». Recalibrar el 1X2 del motor con eso (de donde sale lo
plano) pide 60 cerrados y el backtest a la vista, en los dos lados.

**Las dos lecturas** (24/11/2026, usuario: «o gana el local o no gana, y el
que no gane involucra empate y derrota… cuando se cruzan con el otro, los dos
tienen un evento en común»; y «si suman más de 100, hacer que calce»): desde
ese día el ciego no reparte un 1X2 sino dos preguntas de sí o no, una por
equipo (`{ganaLocal, ganaVisita, porque}`). El empate es lo que comparten los
dos «no gana»: P(empate) = P(no gana local ∩ no gana visita) = 100 −
ganaLocal − ganaVisita. Si las dos suman más de 100 se cruzan: el empate lo
pone el motor (`unXDos`, del nivel, no de la cuota) y local y visita se
reparten el resto en su proporción (`ciego.calzar`, marcado `cruzadas`). Lo
escrito queda guardado tal cual y el espejo calibra cada lectura contra si
ese equipo ganó: dos datos por partido, la calibración más rápida. Un partido
con las lecturas cruzadas es un partido que no leímos claro: se cuenta aparte
(`cruzadas` del espejo) para ver si avisa cuándo no apostar.

**La calibración de las dos lecturas contra los resultados** (24/11/2026,
usuario: «se tiene que salir de lo que dice el analista y calibrar con los
resultados; incluso podemos tomar más resultados pasados»):
`backend/analisis/calibracion_lecturas.py`, una curva por lado,
logit(calibrada) = a + b·logit(dicha), con un previo en la identidad. Medido
ese día con `python -m backend.backtest_calibracion_lecturas` sobre 394 partes
cerrados desde el 28/10 (las lecturas son el 1X2 publicado, casi la casa) y
28 ciegos:

- **Lo dicho comprime hacia el medio**, en los dos lados y en la muestra
  entera: el local que dijimos 68 ganó 78 (69), el de 84 ganó 93 (15); la
  visita que dijimos 48 ganó 58 (66) y la de 67 ganó 78 (32). La curva sale
  con b ≈ 1,46 (local) y 1,35 (visita).
- **Fuera de la muestra no se sostiene.** Corte 80/20 (aprende de 315, mide
  en 79 desde el 21/11): logLoss local 0,5832 → 0,5814 y visita 0,5628 →
  0,5621, una mejora que no se distingue de cero, con cualquier previo (0,25
  a 2). **Semana a semana** —lo que haría la rutina de los lunes—, en 228
  partidos: local 0,5717 → 0,5718 y visita 0,5414 → **0,5509 (peor)**. La
  curva aprendió de las semanas en que los favoritos ganaron de más (b ≈ 1,6
  hasta el 08/11) y la aplicó a la semana en que se cayeron.
- Es la misma falla de la temperatura del 25/10 (sad-analysis v4.1, 6-B,
  «Calibración de la cohorte»): lo que aprende la curva es la racha de los
  favoritos de esas semanas, no un error estable del analista.
- **En el ciego** (28), la curva del publicado mejora un poco (local 0,6272
  → 0,6202; visita 0,5990 → 0,5979); la propia del ciego tiene 28 partidos.

**Con la ventana de dos semanas** (el mismo día, usuario: «solo usa los partes
más recientes, las dos últimas semanas es suficiente; las muy antiguas fueron
leídas con una versión muy antigua de skills»; `VENTANA_DIAS = 14`, la curva y
el backtest solo leen esos días): 227 partes desde el 09/11. Lo publicado
reciente está **casi calibrado** (local que dijimos 68 ganó 73, n 45; visita
de 48 ganó 53, n 34; b ≈ 1,24 y 1,11) y la curva **empeora fuera de la
muestra en los dos lados**: corte 80/20 local 0,6025 → 0,6237 y visita 0,5242
→ 0,5299; semana a semana local 0,5819 → 0,5907 y visita 0,5521 → 0,5562. La
compresión fuerte de arriba venía de las semanas viejas.

**Decisión de ese día**: la curva **no entra al número publicado**. Vive en
el espejo (`curvas`) como información para el analista, y se vuelve a medir
con el backtest semana a semana cuando el ciego llegue a 60 cerrados y con
más semanas: entra solo si la prueba semana a semana mejora en los dos lados.

**Lo que decide**: si el ciego acierta más que la casa en algún grupo de
partidos (sobre todo donde no coinciden), ahí se apuesta a nuestro lado
aunque la casa diga otra cosa. Si no, sabremos que leemos mal y qué arreglar
en la lectura. Y se revisan con eso las reglas de anclaje v4.1-v4.5 (DEUDA
42), que se justificaron por el error de los números, no por el acierto.

## El favorito que viene fallando (25/11/2026)

El caso: Manchester City ganó 1 de 7 (24/10 → 24/11) con la casa dándole
entre 55 y 75 % en cada uno, y el sistema no marcó nada. La alerta
DESCONFIAR no podía encenderse: SOBRE-LA-CASA pide nuestro número 2+ puntos
sobre la casa y 6-B lo pega a ella; BURBUJA-DE-UN-PARTIDO pide una racha +.
Lo demás empujaba al rebote: la regresión al nivel decía «gap fuerte ·
mejora» (+0,88 ante Fulham, +0,70 ante Napoli) y la burbuja «−» con riesgo
alto decía que la racha de no ganar se cortaba.

Lo que se descartó antes, sobre los 410 partes cerrados desde el 28/10 (160
favoritos de la casa con 50 %+, sin copas):

| Señal | n con | Gana con | Casa decía | Lectura |
|---|---|---|---|---|
| motor 15+ pts bajo la casa | 80 | 80,0 % | 69,6 % | al revés: gana MÁS |
| ciego 10+ pts bajo la casa | 17 | 82,4 % | 67,8 % | al revés |
| el analista «dudo» | 43 | 69,8 % | 65,0 % | no separa (−4,4, IC −20 a +10) |

**La señal, fijada antes de mirar**: el residuo de los últimos 5 partidos
oficiales del favorito (victorias − victorias esperadas) en −1,5 o menos.

- **Contra la cuota de cada previo** (1.890 favoritos con cuota, agosto →
  24/11): ganó el 51 % contra el 61 % que decía la casa, n 49, −14 pts con
  IC −28,6 a 0,0. En el City habría marcado Fulham y Napoli. Pista, no
  prueba: tres meses de cuotas, con el hueco del 18/09 al 11/10.
- **Contra el nivel, 5 años** (pedido del usuario;
  `backend/backtest_favorito_falla.py --desde-dir`, 1.595 equipos de las
  ligas con cuota bajados por la API, 38.054 favoritos por nivel del
  25/11/2021 al 24/11/2026, 10.850 partidos de copa nacional fuera): **no
  separa**.

| Variante (contra el nivel) | Marca | Falla con / sin | Diferencia (IC 95 %) |
|---|---|---|---|
| 5 en −1,5 (la fijada) | 2,9 % | 51,1 / 50,0 % | −1,3 (−4,5 a +1,6) |
| 3 en −1,0 | 8,0 % | 52,0 / 49,9 % | +0,3 (−1,5 a +1,8) |
| 5 en −1,0 | 8,1 % | 51,3 / 49,9 % | −0,8 (−2,4 a +1,1) |
| espejo: 5 en +1,5 | 16,2 % | 47,5 / 50,5 % | −0,1 (−1,8 a +1,6) |

Diferencia = cuánto más NO gana el favorito con la señal que los sin señal
de su mismo tramo fino de ventaja y condición. Ninguna variante separa ni
se repite por época; las ligas no se inclinan (la de 3: 20 en el sentido,
19 al revés). El test planta una crisis y la detecta, así que con este
tamaño un efecto de 5 puntos se habría visto. Lo único que asoma es el
gigante (nivel 3,5+ y 1,0+ de ventaja): +8,0 pts con la de 5 en −1,0 (IC
−0,8 a +17,3, unos 120 casos); se miró después y no es una regla.

**Solo grandes en temporada internacional** (pedido del usuario el mismo
día; `--grandes 3.0 --temporada-internacional`). Grande = liga principal en
la lista `LIGAS_GRANDES` (las cinco grandes de Europa, Portugal, Países
Bajos, Brasil y Argentina) **y** nivel mediano de los 5 años ≥ 3,0. Sin la
liga, el corte de nivel metía a La Fiorita, Kauno Žalgiris o Lincoln Red
Imps (el nivel es relativo a cada liga). Quedan 28 equipos: City, Bayern,
Real Madrid, Barcelona, PSG, Liverpool, Arsenal, Inter, Juventus, Napoli,
Atlético, Leverkusen, Dortmund, Leipzig, Benfica, Porto, Sporting, Braga,
Ajax, PSV, Feyenoord, AZ, Twente, Lens, Flamengo, Palmeiras, River y Boca.
Se evalúan sus partidos oficiales de cada temporada en que jugaron un torneo
internacional de clubes: 3.574 favoritos por nivel.

| Variante (contra el nivel) | Marca | Falla con / sin | Diferencia (IC 95 %) | Por época |
|---|---|---|---|---|
| 5 en −1,5 (la fijada) | 0,8 % (30) | 40,0 / 34,1 % | +2,3 (−14,9 a +17,3) | sin muestra |
| 3 en −1,0 | 3,5 % | 35,4 / 34,1 % | −1,9 (−9,5 a +5,2) | −11,3 y +8,7 (al revés) |
| 5 en −1,0 | 3,1 % | 38,4 / 34,0 % | +0,8 (−9,1 a +9,5) | −3,4 y +5,9 |

En un grande la mala racha contra su nivel casi no pasa (30 casos en cinco
años) y, cuando pasa, no separa. **El City no es un caso de esta señal**: su
nivel bajó de 4,08 (14/10) a 3,11 (04/11) y ante Fulham y Napoli ya no era
favorito por nivel (menos de 0,5 de ventaja). El nivel y el motor (49 %) lo
bajaron; la casa lo sostuvo en 69 y 75 %, y el número publicado siguió a la
casa (6-B).

**Lectura**: el que viene fallándole a su nivel gana lo que dice su nivel
(el nivel ya baja con la mala racha). Contra la casa queda la pista de tres
meses, sin muestra para decidir. No entra al semáforo ni a la alerta. Se
re-corre contra la casa (`--padron` en el servidor, que tiene todas las
cuotas) cuando haya seis meses de cuotas sin hueco.

## Las alertas del parte, calibradas (25/11/2026)

El usuario, tras el City: «veamos las señales que decían que no debíamos
apostar y calibremos». En los partes del City saltaron T.54-B sobre el City
(Maresca, que hereda el ciclo de Guardiola) en todos, EFE-EMPATE-TECNICO en
todos y DIV-MOTOR-MERCADO en cuatro; ninguna entra a DESCONFIAR. Sobre 370
partes cerrados desde el 28/10 con el elegido local o visita (sin copas;
el elegido no ganó el 44,6 %), cada alerta según caiga sobre el ELEGIDO,
el RIVAL o el partido. Diferencia = cuánto más no gana el elegido con la
alerta que sin ella, en el mismo tramo de 10 puntos de la casa; mitades
cortadas el 15/11. Con ~40 señales, 2 «separan» por azar.

| Señal | n | No gana con / sin | Diferencia (IC 95 %) | Mitades | Lectura |
|---|---|---|---|---|---|
| FUERA-EN-LA-HOJA sobre el elegido | 135 | 52,6 / 40,0 % | +9,3 (−1,6 a +19,2) | +13,7 y +7,6 | candidata |
| T.54-B sobre el elegido | 17 | 52,9 / 44,2 % | +17,4 (−7,4 a +40,0) | +16 y +15 | sin el City (3 casos): 6 de 14, la casa decía 40 % |
| FACTOR-X sobre el elegido | 20 | 55,0 / 44,0 % | +16,3 (−1,8 a +34,7) | +26 y +5 | poca muestra |
| EJE-DEBUTANTE sobre el elegido | 83 | 51,8 / 42,5 % | +6,5 (−4,4 a +17,6) | +8 y +5 | poca muestra |
| DESCONFIAR | 48 | 54,2 / 43,2 % | +3,9 (−10,3 a +17,2) | +2 y +9 | no separa |
| el analista «dudo» | 82 | 46,3 / 44,1 % | +2,1 | — | no separa |
| EFE-EMPATE-TECNICO | 247 | 42,1 / 49,6 % | −4,5 | −8 y −2 | no avisa |
| FAMILIA-RECORD sobre el elegido | 102 | 36,3 / 47,8 % | −13,2 (−23,9 a −2,4) | −9 y −16 | al revés: gana MÁS |
| DIV-MOTOR-MERCADO sobre el elegido | 36 | 11,1 / 48,2 % | −14,2 (−26,5 a −2,2) | −15 y −13 | al revés: gana MÁS |
| motor 15+ pts bajo la casa | 73 | 21,9 / 50,2 % | −4,8 | −14 y +7 | no avisa |

**Lectura**: ninguna alerta del parte marca con muestra dónde no apostar.
La que más se acerca es **FUERA-EN-LA-HOJA sobre el elegido**: el análisis
contaba de banco a alguien que salió titular, o sea que se leyó otro once.
Es una falla del proceso y suena con la hoja publicada, antes del pitazo.
FAMILIA-RECORD y DIV-MOTOR-MERCADO sobre el elegido van al revés: con ellas
el elegido gana más. Ninguna mueve el semáforo ni la alerta; FUERA-EN-LA-HOJA
queda como candidata para medir hacia adelante con 300 partes más. El
análisis se corrió suelto (scratchpad), no hay script en el repo.

## El semáforo calibrado por razones (25/11/2026)

El usuario, tras Manchester City (seis partidos seguidos en verde, uno
ganado): «el analista dice semáforo en amarillo por tal razón, en rojo por tal
razón, en verde por tal razón… viendo cuál razón se repite más y dándole más
peso, a eso me refiero con calibrar. Eso incluye hacer que el verde no diga
verde cuando perdimos». Y: «nada se mide hacia adelante esta vez, solo hacia
atrás». Después: «usa los otros dos semáforos, la razón de amarillo y las
razones de rojo que confirmen o no».

**Cómo se calibró** (`backend/backtest_semaforo_razones.py`, test
`backend/test_backtest_semaforo_razones.py`). Sobre 1.018 partes cerrados
(14/09 → 25/11/2026, sin copas nacionales, elegido local o visita) se juntaron
las RAZONES previas de cada parte (`semaforo.razones`): alertas por lado,
burbujas y tarjetas calculadas, EFE, TDE, DTP, motor, ciego, DESCONFIAR, el
empate y el marcador declarados, y lo que el analista escribió al justificar
cada espina. El `veredicto` no se lee. El peso de una razón es log(su
frecuencia en los verdes que perdimos / en los que ganamos); el puntaje de un
partido es la suma; el corte deja en amarillo el cuarto de los verdes con más
peso en contra.

**Las razones que más se repiten en los verdes perdidos**: le dimos al empate
27 % o más (60 % de los verdes perdidos contra 36 % de los ganados), el DTP no
ve ventaja (41 contra 25), DESCONFIAR (25 contra 15), 1X2-CARGA-CONTRA-RIESGO
(19 contra 12), el elegido viene de no ganar con riesgo alto (22 contra 14), la
espina del elegido se apoya en «una racha de un partido» (23 contra 15). A
favor: el motor 20+ puntos bajo lo publicado (los favoritos claros),
DIV-MOTOR-MERCADO y G-SORPRESA sobre el elegido.

**La regla** (`semaforo.calibrar`): verde con puntaje ≥ corte → amarillo;
amarillo con puntaje < corte → verde (las razones no lo confirman); rojo se
queda rojo y `confirmado` dice si las razones lo acompañan.

**Comprobación** (pesos y corte aprendidos con los verdes hasta el 04/11,
medido en los 425 partes posteriores, que no se usaron):

| Color | Hoy (espinas) | Calibrado |
|---|---|---|
| 🟢 verde | 218/377 = 57,8 % | 197/323 = **61,0 %** |
| 🟡 amarillo | 11/23 = 47,8 % · marca 5 % · 6 % de las derrotas | 32/77 = **41,6 %** · marca 18 % · **24 %** de las derrotas |
| 🔴 rojo | 9/25 = 36,0 % | 9/25 = 36,0 % |

Los amarillos de las espinas, que los pesos no vieron: con razones ganó el
40,6 % (13 de 32) y sin ellas el 55,0 % (22 de 40), y en los dos grupos
decíamos lo mismo (41-42 %). Los rojos no se confirman con las razones (40
contra 35 %, 33 partidos): el rojo se sostiene por su espina sola.

**Reserva**: descontado lo que decíamos, la ventaja del amarillo calibrado es
de unos 8 puntos y su intervalo cruza el cero en los verdes; la del amarillo
sobre los amarillos no vistos es la más firme. El City no se caza: sus verdes
perdidos suman entre −2,9 y +1,5 contra un corte de 2,26, y el calibrado
habría pasado a amarillo el 5-1 al AEK.

**Dónde vive**: `/analisis/semaforo` (el chip de la web) calibra con el parte
enriquecido (`parte.dto`) y trae `estadoBase` (el de las espinas) y
`calibrado` {puntaje, corte, cambio, confirmado, contra, aFavor}; el parte
muestra las razones escritas bajo el chip. La serie fija de la simulación
(`metodoVerde`, el criterio por escalones desde el 13/11) sigue con el color
de las espinas. Recalibrar = bajar los partes y correr
`python -m backend.backtest_semaforo_razones --desde-json … --tabla`, y pegar
la salida en `semaforo.py`. La regla anti-Goodhart no cambia: el analista no
ve ni el color ni las razones.

## Qué falta

- Volver a medirlo con un mes de datos y sin huecos (se perdieron los datos
  del domingo 01/11 desde las 17:00 hasta el lunes 02/11 a las 12:00).
- La investigación vive en una corrida suelta, no en un script del repo:
  bajar los partes de nuevo y correr el remuestreo cuando se quiera repetir.
- No es una recomendación de apuesta.
