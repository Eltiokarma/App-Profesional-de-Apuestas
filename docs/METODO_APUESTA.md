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

## El semáforo del elegido (11/11/2026)

El usuario: «me apoyaré de ese semáforo». No lee la prosa del parte: mira la
etiqueta del elegido, y ahora esa etiqueta lleva un color CALCULADO
(`backend/analisis/semaforo.py`; el parte no declara nada de esto):

- 🟢 **confirma**: nuestro 1X2 (`pronostico.probabilidades`, normalizado)
  queda a **≤ 2,0 puntos** de la casa sin margen (la última captura
  prepartido, la misma de `lecciones.cuotas_mercado`) en **los tres**
  resultados, **y** el marcador declarado (`pronostico.marcador`, el primer
  N-N) tiene el mismo signo que el elegido.
- 🟡 **duda**: falla una (o las dos); `motivos` dice cuál
  (`LEJOS-DE-LA-CASA` · `MARCADOR-CONTRADICE`).
- ⚪ **sin dato**: sin las tres cuotas, sin el 1X2 o sin un marcador legible.

Medido el 11/11 sobre los mismos 374 partes (15/09-01/11):

- Cuando nuestro 1X2 queda a ≤ 2 pts de la casa en los tres, el elegido ganó
  **66,7 %** contra **53,7 %** que daba la cuota (n 177); cuando se aparta
  más, rinde por debajo de su cuota (−2,5 a −5 pts).
- Cuando el marcador declarado **contradice** al elegido (83 de 374), el
  elegido acierta **39,8 %**. Apostando solo cuando el marcador lo acompaña:
  **60,1 %** contra **55,6 %** (291 de 374), ROI **+4,3 %** contra +2,5 %;
  desde el 28/10, 64,7 % contra 61,3 %.

Se encontró mirando esos mismos datos, así que **se mide hacia adelante con
una regla fija** (como el criterio de contacto, no se mueve): cuenta desde
los partidos del **11/11/2026** (00:00 de Lima, `semaforo.DESDE`), y se toma
en serio si con **150+ verdes NUEVOS** el elegido le gana a lo que pedía su
cuota (media de 1/cuota) por **5+ puntos**, con el intervalo de Wilson al
95 % **entero por encima** de lo que pedía, y los amarillos quedan **por
debajo** de los verdes. La cuenta es `simulacion.resumen_semaforo` (campo
`semaforo` de `GET /analisis/simulacion`, tabla «Semáforo del elegido» en la
pantalla), con una serie en papel nueva, **`metodoVerde`**: el método (1 % de
la banca y el mismo freno por tramo) apostando SOLO en verde. La rutina de
los lunes la reporta en la sección «Semáforo» de `python -m backend.contacto`.

**REGLA ANTI-GOODHART**: el semáforo NO se le muestra a Cowork ni al
analista —ni en el recibo del depósito, ni en el prompt, ni en ningún
endpoint que lea su token—. Si lo viera, aprendería a «pintarse de verde»
pegándose a la casa y la señal moriría. Viaja solo en `/analisis/simulacion`
y en `/analisis/semaforo` (el chip de la web), que el token de Cowork no abre;
`backend/test_semaforo.py` lo verifica.

## Qué falta

- Volver a medirlo con un mes de datos y sin huecos (se perdieron los datos
  del domingo 01/11 desde las 17:00 hasta el lunes 02/11 a las 12:00).
- La investigación vive en una corrida suelta, no en un script del repo:
  bajar los partes de nuevo y correr el remuestreo cuando se quiera repetir.
- No es una recomendación de apuesta.
