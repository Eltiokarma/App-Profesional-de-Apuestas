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

Tres series en papel (`GET /analisis/simulacion`, tabla «Marcador más
probable · con el elegido»): **`metodoMarcador`** (el método, solo con el
marcador alineado), **`metodoVerdeMarcador`** (además con el semáforo en verde)
y **`martingalaMarcador`** (la martingala por líneas, solo con el marcador
alineado: pedido del usuario). La rutina de los lunes lo reporta en la sección
«Marcador» de `python -m backend.contacto`. Este marcador lo ve también el
analista (va en `golesAcotados` del parte): no es una señal que él pueda
pintar, porque sale de la base.

## Qué falta

- Volver a medirlo con un mes de datos y sin huecos (se perdieron los datos
  del domingo 01/11 desde las 17:00 hasta el lunes 02/11 a las 12:00).
- La investigación vive en una corrida suelta, no en un script del repo:
  bajar los partes de nuevo y correr el remuestreo cuando se quiera repetir.
- No es una recomendación de apuesta.
