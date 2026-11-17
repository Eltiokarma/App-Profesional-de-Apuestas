# Estudio · diagnostico-tactico (DTP) v1.8 · lecciones pendientes del 10 al 16/11/2026

**Insumo:** 347 lecciones `pendiente` de 81 partidos, todas posteriores a la subida de la v1.8 (población ciega PRE). La clasificación está en `clasif_diagnostico-tactico.json`, una línea por lección. **59 lecciones (15 partidos) son de copa**: Bolivia (1649146-49), Copa AUF (1649432-33), Copa Colombia (1648690-91) y Copa del Rey (1644xxx). Fijan rúbrica y no sostienen ningún cambio, y abajo se dice cuándo un patrón depende de ellas. El veredicto del lado (206 aciertos, 43 parciales y 98 fallos) **no** dice si la regla funcionó: 46 lecciones de lados fallados dicen que la regla se sostuvo.

## Resultado por clase

| Clase | Todas (347) | Sin copa (288) |
|---|---|---|
| regla_sostuvo | 187 | 161 |
| mal_aplicada | 93 | 78 |
| regla_fallo | 38 | 33 |
| insumo (once tardío o rotado, hoja incompleta) | 15 | 12 |
| imprevisto (rojas, lesión) | 5 | 3 |
| otro_skill | **0** | 0 |
| no_dice (casi siempre «sin stats en la ficha», 8 de 9 de copa) | 9 | 1 |

Hay 2,4 lecciones mal aplicadas por cada regla que falló (93 contra 38). Como en la v1.7 y la v1.8, el problema principal es que la rúbrica vigente no se cumple, no que falte rúbrica.

## Tabla por regla (las más frecuentes)

| Regla | n | sostuvo | fallo | mal aplic. | insumo | imprev. | no_dice |
|---|---|---|---|---|---|---|---|
| M5 · veredicto de la rama contra lo concedido | 92 | 67 | 20 | 4 | 1 | 0 | 0 |
| M2 · banco ofensivo | 35 | 16 | 0 | 16 | 3 | 0 | 0 |
| M2 · vías de gol (lista obligatoria) | 31 | 19 | 3 | 8 | 0 | 0 | 1 |
| M2 · ejecutor de penales | 25 | 18 | 2 | 5 | 0 | 0 | 0 |
| M2 · dos capas (once tardío, rotación M6) | 20 | 9 | 0 | 5 | 6 | 0 | 0 |
| Checklist del bloque (pregunta 6, vida útil) | 18 | 16 | 0 | 2 | 0 | 0 | 0 |
| MECANISMO-ABIERTO | 15 | 15 | 0 | 0 | 0 | 0 | 0 |
| M2 · posesión por rama | 14 | **0** | 2 | **12** | 0 | 0 | 0 |
| M1 · grid, variantes, xiReferencia | 13 | 0 | 0 | 8 | 5 | 0 | 0 |
| M2 · pelota parada con materia | 13 | 6 | 3 | 4 | 0 | 0 | 0 |
| M3 · quién queda atrás / costo de rearmar | 11 | 4 | 1 | 6 | 0 | 0 | 0 |
| M2 · veredicto con condición, ceder, vías por renglón | 10 | 1 | 2 | 7 | 0 | 0 | 0 |

Además: M4 categoría y fuentes 10 (9 sostuvo), M5 sin stats 8 (no_dice), media distancia 7 (4 mal aplicadas, 3 de ellas de copa), al rehacer 6 (6 mal aplicadas), vía de expulsión 4, rama con diferencia numérica 4 (imprevisto), referencia de volumen 3 (3 mal aplicadas), candidato del reconvertido 2.

**Lo que funciona:** MECANISMO-ABIERTO (15 de 15), la pregunta 6 y la vida útil (16 de 18), la M4 con «sin fuente» (9 de 10), los penales (18 de 25) y el juicio del M5 contra lo concedido como regla de cierre. En las 92 lecciones del M5, el cierre aplicó bien la regla: separó la conversión, puso los penales al lado del xG y no subió un veredicto por el marcador.

## Patrones que se repiten (≥ 3 partidos distintos)

### A. Aclarar una regla o hacer cumplir una que ya existe (no tocan números)

1. **Posesión por rama: 12 mal aplicadas, 0 sostenidas, en 11 partidos.** La regla que más se incumple. Falla de dos formas:
   - (a) Se escribe junta «igualado o arriba» con un foco que se pone arriba temprano: Bélgica–Italia 1528983, Chipre–Montenegro 1528979, Nacional–Albion 1649060, Suecia–Bosnia 1528978 y Türkiye–Bélgica 1528958. En los cinco, el que estaba arriba terminó con 42-48 %.
   - (b) El perfil del rival no se toma en su condición de hoy, que la v1.8 sí cubre:
     - de una tasa de resultados, UCV–Grau 1549560;
     - de su volumen de local, JPII–Garcilaso 1549559;
     - de la etiqueta «de visita cede», Belarus–Albania 1528980;
     - del promedio de temporada, Cali–Tolima 1549867;
     - de un solo partido, Moldavia–Kazajistán 1528968;
     - con un DT nuevo, Italia–Francia 1528960, los dos lados.

   **Pide:** no una regla nueva, sino que la posesión de «arriba» sea un campo propio y que el perfil cite de dónde sale (sede, DT, n). Que la app lo compruebe es lo que puede cortar el patrón.
2. **Banco ofensivo: 16 mal aplicadas en 15 partidos.** La regla de la hoja entera y por rol se incumple de tres formas:
   - Falta el volante que llega: Estonia 1528988, JPII 1549559, Montenegro 1528979, Vasco 1492312, Montenegro–Letonia 1545613 y Querétaro–Monterrey 1550951.
   - Falta el defensor o lateral fresco: UTC 1549556, Islandia 1528969 y España 1528961, gol del 0-2.
   - No se hereda el B5 del EFE: Los Chankas 1549556 y Dinamarca 1528974.

   La regla está bien: en las 16 sostenidas el banco nombrado marcó. **Pide:** la lista calculada del banco desde la hoja, que está «pendiente de la app».
3. **M1 · el grid se copia: 8 mal aplicadas en 8 partidos.**
   - Bandas invertidas con el grid a la vista: Croacia 1528985 y Georgia 1528973.
   - Rol o sistema leído del orden o de la etiqueta: Estonia 1545614, Islandia 1528969, Kazajistán 1528968 y Junior 1549868.
   - Dos variantes ausentes: Salamanca 1644376 (copa) y Liverpool M. 1649433 (copa).
   - Aparte, 5 lecciones son de insumo: la API corrigió la formación después del pitazo (Islandia–Bulgaria, Kosovo–Israel, Eslovenia–Suiza y otros).

   **Pide:** el aviso de coordenada inexistente y de etiqueta contra grid, que está pendiente de la app.
4. **Al rehacer, todo lo que nombra piezas: 6 de 6 mal aplicadas en 5 partidos.** Francia–Türkiye 1528982, Noruega–Gales 1528972, Mirassol 1492455, Chapecoense 1492312 y Países Bajos–Grecia 1528966. En este último, el seguro escrito dependía de Kourbelis, que no estaba en la hoja, y Grecia concedió tres goles en 12 minutos. Es una regla de la v1.8 que no se cumple.
5. **M3 · quién queda atrás en la rama de ventaja: 6 mal aplicadas en 6 partidos.** Juventud 1649063, Kazajistán 1528986, Rumania 1528977, Torque 1649057, Cerro Largo 1649056 y Nacional Potosí 1649147 (copa). En todos hubo un cambio conservador con ventaja y un gol en contra a ≤ 10 minutos. Peñarol 1649062 suma una aclaración, un caso: escribir qué queda atrás si el DT **no** hace el cambio defensivo anunciado.
6. **«Ceder no es señal» y «el contrario de la condición», mal aplicadas en 5 partidos.**
   - Ceder la pelota usado como señal: Letonia 1545616, Cerro 1649059, Irlanda del Norte 1528975 y Feroe 1528967.
   - Condición sin la línea contraria: Dinamarca 1528974.
   - La razón no cita sus vías por renglón: Inter Bogotá 1549869 y Racing 1649057.
7. **Lista obligatoria de vías: 8 mal aplicadas en 8 partidos**, cada una de un renglón distinto que ya está en la v1.4 a la v1.8:
   - vía aérea en juego abierto, Estonia;
   - transición del favorito, Chipre;
   - pelota sucia a favor, Albion;
   - origen además del rematador, Santa Fe e Irlanda del Norte;
   - lateral que llega, Suecia;
   - córner como origen, Escocia;
   - tiro libre directo, Valencia (copa).

   No hay un renglón que falle siempre: la lista es larga y se olvida por partes.
8. **Pelota parada: la materia sale del cruce y de la rama** (4 partidos: Letonia 1545616, Albion 1649060, Luxemburgo 1545614 y Llaneros 1549870). Las lecciones piden escribir los córners que concede el rival y la rama: persiguiendo, la materia sube. También piden que la condicional valga para el que tiene la pelota contra un bloque que cede. Es una aclaración del «el que cede no fabrica córners» de la v1.8, sin número.
9. **Penales con la base corta (0-1 penal): 5 mal aplicadas y 1 fallo** (Cali 1549867, Islandia 1528969, España 1528961, Italia 1528960, Levante 1644379 de copa y Torque 1649432 de copa). En cuatro pateó el 9 titular o el lanzador que la regla de la v1.7 ya mandaba nombrar. Se puede aclarar: «con base ≤ 1, el 9 titular entra en la lista siempre».

### B. Candidatos que juntaron casos (no aplicados en la v1.8)

- **El reconvertido también ataca: llega al umbral.** Suma Kosovo–Israel 1528971 (Kamberi al larguero) y Países Bajos–Grecia 1528966 (Timber, lateral reasignado, hizo dos goles). Con Leones del Norte y Telstar son **4 casos limpios en 4 partidos distintos** y cumple el criterio de reapertura («tres casos acreditables»).
- **La presión alta con su vuelta: llega a 3.** España–Inglaterra 1528984 se suma a Utrecht–NEC y Lille–Bodø: tres partidos distintos, uno nuevo. Entra al límite, y lo apoya Croacia 1528962, cuya presión inicial duró 15 minutos.
- **El seguro «sin» que impide un FAVORABLE persiguiendo:** suma Portugal–Dinamarca 1528974 (pedía DESFAVORABLE). Son 2 casos acreditables, más The Strongest de copa: sigue candidato.
- **Penales en serie:** suma Nacional Potosí 1649149, de copa y del mismo cruce. No suma.
- **El segundo de la lista que recibe la falta:** suma Dinamarca 1528974. Son 2 casos.
- **Caso de la 6 con el arquero:** suma Liechtenstein 1528970, dos partidos seguidos sostenidos por Büchel. Son 2 casos.
- **Vida útil del improvisado como techo, no como piso** (nuevo): San Marino–Belarus 1528964, mal aplicada, y Tavernes 1644380, de copa. Un caso acreditable.

### C. Números: solo candidatos a medir

- **NEUTRO como refugio.** De los 20 `regla_fallo` del M5 (17 partidos), 14 son NEUTRO que el volumen resolvió con claridad: 6 hacia FAVORABLE (Cajamarca, Feroe, Eslovaquia, Comerciantes, Albania y Países Bajos con 4,46 contra 0,46 de xG) y 8 hacia DESFAVORABLE (Kazajistán, Liverpool M., Sport Boys, Chipre, Águilas, Irlanda, Portugal y Georgia). Los otros 6 son FAVORABLE o DESFAVORABLE fuera de lugar. Esto pide la **banda de «parejo»** que la v1.8 dejó para un backtest. Las lecciones no dan el número: hay que medirlo sobre los veredictos cerrados (volumen a favor y en contra por rama).
- Ninguna lección pide mover un umbral (MECANISMO, vida útil o DTP-REHACER).

## Contradicciones

- **Pelota parada condicional.** Mirassol 1492455, Defensor 1649062 y Luxemburgo 1545614 dicen que sin materia no sostiene la rama. Letonia, Albion y Estonia 1528988 dicen que la condicional produjo córners o goles («condicional no es descartada»). No se anulan: las dos se resuelven si la materia se lee del cruce y por rama (patrón A8).
- **Dos capas.** Muchas lecciones cobran el once tardío como «apertura caída, no fallo». Armenia 1528959 (parte sin once consultado) y Francia–Türkiye y Georgia (once capturado antes del depósito) se cobran como mal aplicadas. La línea la pone el `momento` de DTP-REHACER. Hay dos lecciones sin `momento`, Bélgica 1528958 y Liverpool M. 1649433, que no se pueden atribuir.
- **Perfil de posesión contra marcador.** Bosnia 1528978 dice que con el favorito 3-0 arriba el que persigue domina la pelota sea cual sea su perfil de visita. La regla del perfil no cubre el marcador amplio: es un caso, para anotar.
- **Costo del rearme.** Vasco 1492312 y Belarus 1528980 rearmaron sin conceder. No contradice: la v1.8 ya dice «vía, no certeza».

## Cruce con la v1.8 y con `DTP_v1.8_propuesta.md`

- Las reglas nuevas de la v1.8 que más se incumplen son la posesión aparte y en la condición de hoy (cambios 3 y 11), al rehacer (T6b), el grid (6), el banco desde la hoja y el defensor fresco (5 y 12) y quién queda atrás en todas las ramas (8). **Las lecciones confirman que el texto es correcto**: cuando se aplica, sostiene, y cuando falla es por no aplicarlo. No piden reescribirlo. Piden lo de «Para la app»: banco calculado, aviso de grid, insumos del rehacer.
- El juicio contra lo concedido (cambio 1) se aplicó sin desvíos en el cierre. Lo que falla es la **apertura** que da NEUTRO.
- Candidatos de la propuesta: el **reconvertido que ataca (cambio 10)** y la **presión con su vuelta** llegan al umbral. El rearme del medio, los penales en serie, un cambio atrás por vez y la 5 con ventaja temprana no suman casos acreditables.

## ¿EFE heredado o regla propia del DTP?

- **Fallos del DTP:** 131 (38 `regla_fallo` y 93 `mal_aplicada`). **Por un EFE equivocado: 0.** Ninguna lección nombra un dato del EFE que estuviera mal.
- **El caso inverso: 4 lecciones** donde el EFE (o el TDE) tenía bien el dato y el DTP no lo heredó:
  - el B5 en Los Chankas 1549556;
  - el B5 en Dinamarca 1528974;
  - la línea de cinco en la sensibilidad, Salamanca 1644376 (copa);
  - la `siExpulsion` del TDE, Inter Bogotá 1648690 (copa).
- **Las 13 etiquetas `lectura_efe` de Jev:** ninguna es del EFE. 10 son rúbrica del DTP mal aplicada (posesión, ceder, pelota parada sin materia, referencia de racha) y 3 son reglas que se sostuvieron (Armenia 1545616:b, Eslovenia 1545654:a y Feroe 1528967:b).

## Conclusión

- **Tiene material para la v1.9:** el reconvertido también ataca (4 casos) y la presión con su vuelta (3), como reglas. Además dos aclaraciones sin número: la materia de la pelota parada sale del cruce y de la rama, y el 9 titular entra siempre en la lista de penales con la base ≤ 1.
- **No tiene material:** el resto del cambio de rúbrica. Las 93 lecciones mal aplicadas caen sobre reglas de la v1.6 a la v1.8 que ya dicen lo correcto (posesión, banco, grid, rehacer, M3). Reescribirlas no sirve. Lo que hace falta es lo pendiente de la app y, quizás, un checklist de salida.
- **El NEUTRO-refugio** (14 de 20 fallos de veredicto) es el único hallazgo numérico y va a backtest, no al skill.
- **Muestra:** una semana, 288 lecciones acreditables, la mayoría de una fecha FIFA (selecciones del 12 al 16/11).
