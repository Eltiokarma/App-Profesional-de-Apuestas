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

## Qué falta

- Volver a medirlo con un mes de datos y sin huecos (se perdieron los datos
  del domingo 01/11 desde las 17:00 hasta el lunes 02/11 a las 12:00).
- La investigación vive en una corrida suelta, no en un script del repo:
  bajar los partes de nuevo y correr el remuestreo cuando se quiera repetir.
- No es una recomendación de apuesta.
