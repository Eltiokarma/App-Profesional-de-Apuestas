# Las cuotas y los goles (25/11/2026)

## La pregunta

Una persona que apuesta con las cuotas de la casa le contó al usuario su
hipótesis: según el rango de la cuota del local y la del visitante, cada
partido tiene una forma (A, B, C, D o E), y esa forma dice cuántos goles va a
haber. El usuario quiso ponerla a prueba y sumarle dos cosas que la app ya
tiene: las constantes de goles, con su reventón, y las cuotas que la propia
casa da a los goles (más o menos de 2,5 goles y ambos marcan).

Todo se midió hacia atrás, con un corte temporal: lo que se aprende con los
partidos más viejos se comprueba con los más nuevos, que no se usaron para
aprender. Así un patrón que apareció por azar no pasa como si fuera real.

## Los datos

- **Partidos con cuota 1X2 y resultado**: 4.400, del 27/08 al 24/11/2026, sin
  amistosos. La «casa» es el promedio de todas las casas que captura la
  ingesta (`lecciones.cuotas_mercado`): se promedian las cuotas de cada
  resultado, se pasan a probabilidad y se les quita el margen.
- **Partidos que además tienen la cuota de goles**: 4.343, con más o menos de
  2,5 goles y ambos marcan, que la ingesta guarda desde agosto.
- **Partes con las constantes de goles de la app**: 987, del 14/09 al 24/11,
  con el modelo de goles (`golesAcotados`) y las rachas de goles de cada
  equipo, pedidas con `antesDe` para que solo lean lo anterior al partido.
- **Historias de 1.595 equipos**, para calcular sus rachas de goles en los
  4.236 partidos con cuota de goles donde están los dos equipos.

Las cuotas son la última captura antes del pitazo, y como no hay cuotas
guardadas de antes de agosto, la muestra cubre tres meses.

## 1. La forma de la cuota 1X2 sí dice cuántos goles hay

La hipótesis tiene base, y para probarla se fijaron dos formas antes de mirar
los resultados: la que propone esa persona (quién es favorito y cuánto) y la
probabilidad de empate que da la casa.

| Forma | Partidos | Goles promedio | Más de 2,5 | Ambos marcan | 0 o 1 gol |
|---|---|---|---|---|---|
| A · local muy favorito (65 %+) | 557 | 3,56 | 69 % | 51 % | 14 % |
| B · local favorito (50-65 %) | 953 | 2,92 | 56 % | 57 % | 22 % |
| C · parejo (nadie llega a 50 %) | 2.260 | 2,65 | 49 % | 54 % | 26 % |
| D · visitante favorito (50-65 %) | 397 | 3,09 | 61 % | 56 % | 19 % |
| E · visitante muy favorito (65 %+) | 233 | 3,27 | 61 % | 45 % | 19 % |
| Todos | 4.400 | 2,89 | 55 % | 54 % | 23 % |

La probabilidad de empate de la casa ordena los goles todavía mejor, porque
la casa sube el empate cuando espera un partido cerrado:

| Empate según la casa | Partidos | Goles promedio | Más de 2,5 | 0-0 |
|---|---|---|---|---|
| menos de 22 % | 1.020 | 3,45 | 66 % | 3 % |
| 22-25 % | 786 | 3,10 | 60 % | 5 % |
| 25-28 % | 1.367 | 2,80 | 52 % | 5 % |
| 28-31 % | 990 | 2,48 | 46 % | 8 % |
| 31 % o más | 237 | 2,12 | 36 % | 13 % |

En los partidos nuevos (1.790 desde el 27/10), las dos formas predicen «más
de 2,5» mejor que el promedio general y que el de cada liga. La pérdida
logarítmica, que es más baja cuanto mejor se predice, fue de 0,6908 con el
promedio general, 0,6864 con el de la liga, 0,6796 con la forma A-E y 0,6768
con el empate de la casa. Para «ambos marcan» la forma casi no ayuda (0,6944
contra 0,6928): un favorito muy fuerte hace goles, pero suele dejar al rival
en cero.

## 2. La cuota de goles de la casa lo dice mejor

La forma de la cuota 1X2 es una manera indirecta de leer lo que la casa ya
dice directamente en su mercado de goles. Su empate y su probabilidad de
más de 2,5 están muy ligados (correlación de −0,83), y en los partidos nuevos
la cuota de goles predice mejor que cualquier forma:

| Cómo se predice (1.789 partidos desde el 27/10) | Más de 2,5 | Ambos marcan |
|---|---|---|
| Promedio general | 0,6907 | 0,6942 |
| **La cuota de goles de la casa, tal cual** | **0,6654** | **0,6875** |
| La forma 1X2 sola (empate y A-E) | 0,6755 | 0,6932 |
| La cuota de goles más la forma 1X2 | 0,6688 | 0,6896 |

Sumarle la forma a la cuota de goles no mejora nada: lo empeora un poco,
porque agrega lo mismo dos veces. La cuota de goles, además, está bien
calibrada: cuando dice entre 60 y 70 % de más de 2,5 (promedio 64 %), pasó en
el 66 % de los partidos; cuando dice 70 % o más, en el 75 %.

## 3. Las constantes de goles no agregan a la cuota de goles

En los 987 partes, el modelo de goles de la app predice peor que la casa, y
sumarlo a la cuota tampoco ayuda (403 partidos desde el 05/11):

| Cómo se predice | Más de 2,5 | Ambos marcan |
|---|---|---|
| La cuota de goles de la casa | **0,6655** | **0,6874** |
| El modelo de goles de la app | 0,6797 | 0,6878 |
| La casa más el modelo de la app | 0,6715 | 0,6886 |
| La casa más las rachas de goles de los dos equipos | 0,6722 | 0,6888 |

Cuando la app y la casa eligen distinto (si habrá más de 2,5 goles), acertó la
casa en 135 partidos y la app en 112; en ambos marcan, 122 contra 110. Es lo
mismo que ya había medido REVENTON §17: el modelo de goles acota el marcador,
pero no le gana a la cuota de goles.

## 4. Las rachas de goles no revientan más de lo que la casa espera

En los partes apareció una pista que parecía firme: cuando alguno de los dos
equipos venía con 4 partidos o más seguidos con «ambos marcan», en el
siguiente pasó 7,1 puntos menos de lo que decía la casa (IC de −13,0 a −1,3,
270 partidos), y en las dos mitades del período fue negativo.

Con la muestra grande, calculando esas rachas desde las historias en 4.236
partidos, la pista se cae:

| Racha de alguno de los dos equipos | Partidos | Pasó | La casa decía | Diferencia (IC 95 %) | Mitades |
|---|---|---|---|---|---|
| ambos marcan, 4+ | 690 | 55,5 % | 55,7 % | −0,2 (−3,9 a +3,6) | +3,7 y −4,4 |
| ambos marcan, 6+ | 209 | 53,6 % | 57,1 % | −3,5 (−10,0 a +3,2) | −1,5 y −5,8 |
| más de 2,5, 4+ | 747 | 57,8 % | 58,6 % | −0,7 (−4,2 a +2,7) | −1,1 y −0,4 |
| más de 2,5, 6+ | 287 | 64,5 % | 62,1 % | +2,4 (−2,8 a +8,0) | −1,0 y +5,5 |

Una racha de goles, aunque sea larga, sigue más o menos lo que la casa ya
espera. Queda una sola pista, que se encontró después de mirar y no se toma
como regla: cuando los dos equipos vienen con 3 o más partidos de «ambos
marcan», pasó en el 49,5 % de los partidos contra el 56,1 % de la casa, pero
son solo 111 partidos.

## Qué significa para apostar

La hipótesis de esa persona es correcta en lo que afirma: la forma de la
cuota 1X2 dice cuántos goles habrá. Pero la casa lo dice mejor en su propio
mercado de goles, así que el camino corto es mirar la cuota de más o menos de
2,5 y de ambos marcan, en vez de inferirla de la cuota 1X2. Es la misma
conclusión a la que llegamos con el 1X2: lo que mejor predice el resultado es
el número de la casa, y lo que agregan los análisis propios (las razones del
parte para el 1X2, las constantes y las rachas para los goles) no mejora ese
número.

Lo único que la app agrega de verdad, por ahora, está en el 1X2: las dos
alertas de las burbujas (DESCONFIAR y el riesgo alto del elegido), que suben
el acierto del elegido de 74,9 % a 79,2 % en los partidos de 55 % o más
(«El número, no el color», en
`docs/METODO_APUESTA.md`); para los goles, en cambio, no apareció ninguna
señal equivalente.

## Reservas

- Son tres meses de cuotas. Una señal más débil que unos 3 puntos no se
  podría ver con esta muestra.
- La «forma» que usa esa persona puede no ser exactamente la que se probó
  acá. Se fijaron dos formas razonables antes de mirar, y la del empate fue
  la mejor; con sus rangos exactos se puede repetir en minutos.
- Esta medición juzga cuánto se acerca la predicción a lo que pasó. No midió
  si alguna regla de apuesta en goles deja ganancia, porque el criterio del
  proyecto es el acierto, y un mercado de goles bien calibrado no deja dónde
  acertar más que la casa.
- Los cálculos se corrieron con scripts sueltos en la sesión, no con un
  backtest del repo. Si el estudio se va a repetir, conviene pasarlos a
  `backend/` con su test, como los demás backtests.
