# Calibración — cómo se ajusta el módulo con casos

> **Estado al 15.08.2026 — v0.1.11.** Registro: **27 filas**. Huecos de numeración declarados: **TDE-010, TDE-019, TDE-020, TDE-027 y TDE-028**. **Ningún peso tocado. Ninguna métrica de esta página se movió.**
>
> **Población nueva excluida: `post_resultado`.** TDE-031 y TDE-032 (Guaraní 2-3 Rubio Ñu, F5 Clausura Paraguay) entran al registro y **no entran a ninguna tabla de abajo**. El partido se eligió a ciegas, pero la búsqueda del XI confirmado devolvió el marcador antes de puntuar el primer indicador. No es `por_resultado` —no se eligió porque pasara algo— ni es `ciega` —se puntuó con el resultado adentro—. Ver disciplina 31.
>
> **El Brier sigue en ~0.235 sobre 10 ciegos cerrados y las echadas ciegas observadas siguen siendo una.** El umbral binding de N ≥ 5 no se movió. Las tres poblaciones del registro son ahora `por_resultado` (4 sembrados), `ciega` (la única que calibra) y `post_resultado` (2, excluidos).
>
> **Chequeo pendiente para la próxima pasada, declarado acá para que no se pierda:** contar la distribución completa de valores del ISE sobre todo el registro y reportar qué fracción supera 7. Van tres dieces (TDE-014, TDE-016, TDE-031) y la sospecha es que el índice satura, igual que `C1`. Es medición, no cambio: no tocar `SOB2` hasta tener el conteo.

> **Estado al 10.08.2026 — v0.1.7.** Registro: **19 filas**, 6 declaradas (2 cerradas y fallidas, 4 pendientes), 11 RETRO, 2 en modo `COND`. Huecos de numeración declarados: **TDE-010, TDE-019 y TDE-020**. **Ningún peso tocado.**
>
> **Los tres artefactos estaban desincronizados** y esta versión los alinea. `SKILL.md` había avanzado a v0.1.6 describiendo el cierre de TDE-019 y TDE-020, y esas dos filas nunca existieron en el CSV. Se declaran huecos en lugar de reconstruirse de memoria, y **las métricas de abajo no los incluyen**. Si aparecen, entran como filas nuevas sin renumerar nada.
>
> **Hallazgo estructural: hay dos poblaciones de RETRO.** Los cuatro sembrados fueron elegidos porque hubo echada; los reconstruidos por fecha completa son ciegos al resultado. Columna nueva `seleccion`. Mezclarlos infla la tasa de echada de 11% a 31%, y ese sesgo es el que sostenía la escala de `P(echada)`.
>
> **La banda 5-7 dejó de ser el problema: el problema es la escala entera.** Ver el chequeo completo abajo.

## Chequeo de calibración · 10.08.2026 (v0.1.7)

Calculado sobre los **9 casos ciegos y cerrados** del registro: TDE-005, 006, 007, 011, 012, 013, 014, 015, 016.

### Vía 1 — la frecuencia está inflada en toda la escala

| Métrica | Valor | Objetivo |
|---|---|---|
| IE medio de la muestra | 5.04 (la escala promete ~45%) | — |
| `P(echada)` declarada media | 44.1% | — |
| **Echadas observadas** | **1 / 9 = 11.1%** | — |
| **Brier de `P(echada)`** | **0.247** | < 0.20 |

Comparación de poblaciones, que es el punto:

| Muestra | n | Echadas | Tasa |
|---|---|---|---|
| Incluyendo los 4 sembrados | 13 | 4 | 31% |
| **Solo ciegos** | **9** | **1** | **11.1%** |

Y el detalle que descarta la hipótesis del tramo: **el único caso que se echó tenía IE 4.6 (TDE-005) y el IE más alto del registro, 7.6 (TDE-006), no se echó.** La escala no falla en la banda 5-7; no discrimina en ningún tramo.

### Vía 1 — la letalidad está subestimada

| Eslabón | Declarado | Observado |
|---|---|---|
| `P(echada)` | 44% medio | 11% (1/9) |
| `P(fractura \| echada)` | 22–55% | **75%** (3 de 4 echadas) |
| `P(gol \| fractura)` | 45–55% | **3 de 3** |

Las tres fracturas del registro (TDE-002, TDE-003, TDE-005) terminaron todas en gol. n mínimo, pero el signo es unánime y contrario a la rúbrica.

**Los dos errores van en direcciones opuestas y se cancelan parcialmente en el riesgo compuesto.** Es la primera evidencia medida a favor de una decisión de diseño que hasta ahora era intuición: la lectura que se comunica es el compuesto, nunca `P(echada)` sola.

### Vía 2 — separa mejor que la vía 1

| ISE | n | Se expuso |
|---|---|---|
| ≤ 4.4 | 3 | 0 / 3 |
| ≥ 6.7 | 3 | 3 / 3 |

Separación perfecta en 6 casos, mejor que cualquier tramo del IE. Con TDE-021 sumado, los expuestos que concedieron van **2 de 4**. Advertencia: los 6 son RETRO o `COND` y tres se construyeron conociendo el gol. **El umbral del ISE sigue siendo N = 4 declarados y hoy hay 2 (TDE-017, TDE-018), ninguno cerrado.**

### Consecuencias aplicadas en v0.1.7

1. Columna `seleccion`; toda tasa se calcula solo sobre ciegos.
2. Advertencia de sobreestimación extendida de la banda 5-7 a **todo** el rango de IE.
3. `P(gol | fractura)` arranca en la banda alta (50-65%) por defecto; bajarla exige justificación.
4. F2 pasa a ser dato obligatorio del motor (3 de 3 estimaciones propias corregidas).
5. Umbral de pesos medido en resultados positivos: **N ≥ 5 echadas observadas con selección ciega.**
6. Interacción entre vías reclasificada como varianza bidireccional; prohibición de coeficiente estructural.

### Candidatos declarados y NO aplicados

- **Recortar el mapeo IE → `P(echada)` a la mitad**: 0-3 → 5-12%, 3-5 → 12-22%, 5-7 → 22-35%, 7-8.5 → 35-50%. Es el cambio que los datos piden, y con 9 casos y **un** positivo aplicarlo sería reemplazar una escala inventada por otra inventada. Revisión al llegar a 5 echadas observadas ciegas.
- **Reescalado de `C1` con nivel intermedio 0.5**: sigue declarado pero **despriorizado**, porque el hallazgo de escala completa le saca la premisa. Cambio explícito respecto de v0.1.5, que lo tenía como hipótesis preferida.

> **Estado al 10.08.2026 — v0.1.5.** N = **6 casos declarados** (TDE-005, TDE-006, TDE-008, TDE-009, TDE-017, TDE-018), de los cuales 2 cerrados y ambos fallidos. Registro total: **17 filas**, 6 declaradas, 2 en modo `COND` y 9 `RETRO`. **Ningún peso tocado.** Faltan 2 declarados para el primer umbral de revisión de pesos.
>
> **La vía 2 tiene sus dos primeros casos declarados**: TDE-017 (ISE 8.3) y TDE-018 (ISE 6.7), los dos con el ISE escrito antes del partido. El primer umbral de revisión del ISE es N = 4 declarados. Y tiene su primer dato empírico: dos casos con ISE 10 y un gol (TDE-014 concedió, TDE-016 no).
>
> **Modo de evaluación nuevo** *(v0.1.5)*: la columna `modo_evaluacion` distingue `PRE` de `COND`. Un IE condicional de ventana no acredita validación predictiva. TDE-015 y TDE-016 son los dos primeros `COND` del registro y están marcados como tales.
>
> **Advertencia de comparabilidad, ampliada.** Además de `esquema_P`, las filas llevan ahora `IE_recomputado_esquema6` e `IE_recomputado_v015`. En TDE-015 las tres cifras difieren y ninguna es un error: 5.5 declarado con la cláusula de ventaja obtenida, 5.3 en la lectura estricta de v0.1.4 por μ, y 5.5 otra vez con el modo `COND` de v0.1.5. **El 5.3 es el síntoma numérico de un hueco de definición, no una corrección de estimación.**
>
> **Hueco de numeración declarado**: no existe TDE-010 y se deja como hueco (disciplina 12 del SKILL).
>
> **La banda IE 5–7 sigue declarada sobreestimada, con hipótesis nueva.** Cuatro casos con `P(echada)` ≥ 45% no se echaron: TDE-006, TDE-011, TDE-012 y TDE-015. **Los cuatro comparten `C1 = 1`.** La sospecha se mueve del peso del bloque C a la rúbrica de C1, que exige ocho partidos de rodaje de repliegue ensayado para puntuar 0 y por eso deja en 1 a casi cualquier equipo. Candidato de reescalado declarado en `INDICE_IE.md` y no aplicado.

> **Estado histórico al 09.08.2026 — v0.1.3.** N = 2 casos declarados y cerrados (TDE-005, TDE-006), ambos fallidos. Registro total: **13 casos**, 4 declarados (2 cerrados, 2 pendientes al 16.08) y 9 RETRO. **Ningún peso tocado en ninguna de las dos ramas de v0.1.2.** Los dos casos declarados para el 16.08.2026 llevarán N a 4.
>
> **Hueco de numeración declarado**: no existe TDE-010. Se deja como hueco y no se rellena con un caso reconstruido para que la serie quede prolija (disciplina 11 del SKILL).
>
> **Advertencia de estado del ISE.** La vía 2 nace con N = 0 casos declarados. Sus tres indicadores tienen peso idéntico porque ponderar sin datos sería inventar precisión. Primer umbral de revisión del ISE: N = 4 casos **con ISE escrito antes del partido**. TDE-013 y TDE-014 son RETRO y no cuentan.
>
> **Advertencia de comparabilidad** *(v0.1.3.1)*. Las filas del registro no comparten esquema de indicadores del bloque P: TDE-011 y TDE-012 se puntuaron sobre 4 indicadores, TDE-013 y TDE-014 sobre 6. Cada fila lo declara en `esquema_P` y lleva un `IE_recomputado_esquema6`. **El método manual de ajuste de pesos ordena casos por score de bloque, así que usar la columna declarada en lugar de la recomputada produciría un orden falso.** Recomputados: TDE-011 baja de 4.5 a 4.2 y TDE-012 sube de 6.2 a 6.5, sin cambiar de banda.
>
> **La banda IE 5–7 está declarada sobreestimada.** Tres casos con `P(echada)` ≥ 45% no se echaron: TDE-006, TDE-011 y TDE-012. Las compuertas recortan 0.3–0.4 de IE y no cierran la brecha; el driver probable es el peso relativo del bloque C. La corrección de pesos espera N = 8.

El TDE nace en v0.1 con pesos razonados, no ajustados. Los pesos `F×3 · C×2 · P×2 · S×1.5` son una hipótesis. Este documento define cómo se convierten en algo verificado.

## Regla de anti-hindsight

1. Un caso **solo cuenta como validación** si el IE, las tres probabilidades, el tipo modal y la ventana modal se escribieron en el registro **antes del inicio del partido**.
2. Los casos reconstruidos después se marcan `RETRO` en la columna `modo`. Sirven para fijar rúbrica y calibrar magnitudes, **no** para acreditar aciertos ni para calcular tasa de acierto.
3. Nunca reescribir una fila declarada. Si la estimación estaba mal, se registra el fallo y se anota la lección. La integridad del registro vale más que el ego del módulo.

## Cómo se cierra un caso

Completar las columnas de observación:

- `se_echo` — sí / no / parcial
- `se_expuso` — sí / no / parcial *(vía 2)*
- `minuto_real` — minuto donde la transición se volvió observable
- `tipo_real` — el mecanismo que efectivamente operó
- `se_partio` — sí / no (¿se abrió la franja entre líneas de forma sostenida?)
- `gol_en_echada` — sí / no (¿concedió gol durante el repliegue?)
- `gol_en_sobreexposicion` — sí / no (¿concedió gol con el equipo volcado y sin seguro tras la pérdida?)
- `compuertas_operadas` — qué compuertas se activaron, incluso si no cambiaron el número
- `minuto_gol`, `resultado`, `nivel_dato` (A/B/C), `notas`

## Métricas de evaluación

Con `N` casos declarados (no RETRO):

| Métrica | Cómo se calcula | Objetivo |
|---------|-----------------|----------|
| Acierto de banda | % de casos donde el resultado cayó dentro de la banda de IE declarada | > 65% con N ≥ 10 |
| Brier score de P(echada) | media de (p − resultado)², resultado = 1 si se echó | < 0.20 |
| Brier score de P(fractura) | igual, solo sobre casos donde se echó | < 0.25 |
| Error de ventana | \|ventana declarada − ventana real\| en número de ventanas | MAE < 1 ventana |
| Acierto de tipo | % de casos donde el tipo modal coincidió | > 55% |
| Brier score de P(sobreexposición) | media de (p − resultado)², resultado = 1 si se expuso | < 0.20, medible desde N = 4 declarados |
| Cobertura de vía | % de goles concedidos en los últimos 15' que alguna de las dos vías anticipó | > 60% con N ≥ 10 |

**La métrica de cobertura de vía es la que justifica el ISE.** Con solo la vía 1, TDE-014 concedió al 90' con un IE que había acertado en decir que no se echaría. El módulo tenía razón y no servía.

## Umbrales de revisión

> **Regla de resultados positivos** *(v0.1.7)*. Los umbrales de abajo cuentan casos declarados, pero el método manual de ajuste **separa el grupo que se echó del que no**. Si el grupo positivo tiene menos de 5 miembros con selección ciega, el paso 1 del método no tiene nada que ordenar y la revisión de pesos no se ejecuta, sin importar cuántas filas tenga el registro. **N de declarados es condición necesaria; N de resultados positivos es la condición binding.** Al 10.08.2026 hay **1** echada observada ciega.

- **N = 4** → primera lectura cualitativa. No tocar pesos. Solo revisar si la rúbrica de algún indicador está mal redactada.
- **N = 8** → primera revisión de pesos, **si además hay ≥ 5 echadas observadas ciegas**. Método manual descrito abajo.
- **N ≥ 10** → calcular Brier y error de ventana. Publicar v0.2 con los pesos ajustados y el registro adjunto.
- **N ≥ 25** → ajuste por regresión logística de `se_echo` sobre los cuatro scores de bloque. Recién ahí los pesos dejan de ser opinión.

## Método manual de ajuste (N = 8 a 24)

> **Antes de ordenar casos, verificar la columna `esquema_P`.** Si hay filas en esquemas distintos, usar `IE_recomputado_esquema6` y los scores de bloque recomputados. Ordenar por la columna declarada mezclando esquemas invalida el paso 1 del método.


Para cada bloque, calcular la correlación de signo simple: entre los casos donde el equipo **se echó** y los casos donde **no**, ¿qué bloque separa mejor los dos grupos?

1. Ordenar los casos por score del bloque.
2. Si el bloque separa bien (los que se echaron están arriba), su peso se mantiene o sube 0.5.
3. Si no separa (mezclados), su peso baja 0.5.
4. Si un bloque tiene el signo invertido de forma consistente, no se le baja el peso: se revisa la rúbrica, porque probablemente un indicador esté puntuando al revés.
5. Renormalizar el denominador (suma de pesos) y recalcular todos los IE del registro con los pesos nuevos para ver si el acierto de banda mejora. Si empeora, revertir.

**Nunca ajustar pesos con un solo caso llamativo.** Un 5-0 no es evidencia, es un caso.

## Cierres realizados — lo que enseñó cada uno

### TDE-005 · Melgar 2-4 FC Cajamarca (F4 Clausura, 09.08.2026)

Declarado IE 4.6 · P(echada) 38% · ventana 75-90 · `ECHADA-VOL`. Observado: se adelantó 1-0 al minuto 10 de córner y retrocedió en cuanto tuvo la ventaja; empate al 25' tras un penal atajado y una mala salida del propio arquero en la jugada siguiente; 1-2 al 55'. Desde ahí dejó de ser echada para ser partido roto (regla 3 de disciplina).

Falló la banda, falló el tipo (era `PSI`, no `VOL`) y la ventana falló por **4 ventanas**. **Es el cuadrante 3 de la lista de faltantes: el falso negativo que más enseña.** Cubierto.

### TDE-006 · FC Cajamarca gana 4-2 en Arequipa (F4 Clausura, 09.08.2026)

Declarado IE 7.6 · P(echada) 82% · ventana 60-75 · `ECHADA-FIS`. Observado: no se echó en ningún momento, fue 0-1 abajo de visitante y ganó 4-2. **Falso positivo severo.** El falsador sí se gatilló, lo que confirma que el registro está bien construido aunque el pronóstico haya sido malo.

Origen del error: P1 puntuado 1 por la cláusula del "equipo que espera recibir el primer gol", y F3 puntuado 1 por reputación de colista recién ascendido. Ambas rúbricas corregidas en `INDICE_IE.md`.

### TDE-011 · Cerro visitante a Danubio (F1 Clausura uruguayo, 09.08.2026) — RETRO

F 0.38 · C 0.33 · P 0.63 · S 0.50 · IE 4.5 · P(echada) 35%. **No se echó**: bloque bajo estructural sostenido los 90 minutos.

**Es el origen de las compuertas 2 y 3.** Los cambios defensivos estaban dentro de un plan ensayado, así que S2 no debía puntuar alto con C1 por debajo de 1. Y el ruido institucional del caso no llegaba al vestuario, lo que motivó el desdoble de P4. Aporta además la firma de bloque sostenido como proxy negativo: 67 minutos administrando un 1-0 sin conceder un solo remate desde el borde del área. Cubre parcialmente el cuadrante 4 (bloque estructural de 90'), aunque en un equipo chico.

### TDE-012 · Danubio local vs Cerro (F1 Clausura uruguayo, 09.08.2026) — RETRO

F 0.50 · C 1.00 · P 0.63 · S 0.33 · IE 6.2 · P(echada) 55%. **No se echó**: recibió al 23' y fue al frente los 67 minutos restantes, sin conceder el segundo gol.

**Segundo falso positivo de banda media** y el caso que puso la banda 5–7 bajo sospecha formal. P1a estaba mal puntuado por narrativa: el módulo daba al equipo como favorito (µ 1.55 vs 1.23, gap ajustado +0.35) y se le asignó 0 por el relato de crisis. Con P1a = 0.5 el IE sube a 6.5 y la compuerta 1 ni se activa — o sea que el error de procedimiento no era conservador, era ruido.

**Nota cruzada con el EFE**: `COLAPSO EN CASCADA` estaba activo y no se cumplió. **Tercera evidencia a favor de mantener la goleada calibrada en 8-15% y no en 30-40%.**

### TDE-013 · Wanderers gana 0-1 en el Franzini (F1 Clausura uruguayo, 09.08.2026) — RETRO

F 0.38 · C 0.17 · P 0.33 · S 0.25 · IE 3.0 · P(echada) 22% · P(fractura|echada) 18% · riesgo compuesto 1.6%. ISE 1.7. Bloque bajo estructural con ocho partidos de rodaje (siete fechas del Intermedio invicto, 4 goles en contra, más la final). No se echó, no se partió, aguantó los 90 y ganó de contragolpe al minuto 90 con tres suplentes en la jugada.

**Tercera confirmación de la lección de TDE-001 y TDE-011**: repliegue entrenado con C1 = 0 sostiene los 90 y `P(fractura)` va a la banda baja. Aportes de rúbrica: la regla `n/a` de S3 —se lo había puntuado 0.5 porque el rival sabía salir jugando, cuando este equipo no presiona alto y no tiene primera línea que pueda ser superada— y la separación de P1c, porque estaba 6° en la Tabla Anual y en zona de descenso por promedios al mismo tiempo. **Con las tres compuertas y la regla `n/a` apiladas, el IE baja de 3.4 a 3.0.**

### TDE-014 · Defensor Sporting pierde 0-1 en casa (F1 Clausura uruguayo, 09.08.2026) — RETRO

F 0.25 · C 0.67 · P 0.58 · S 0.33 · IE 4.4 · P(echada) 35%. **No se echó en ningún momento** y concedió al minuto 90 de contragolpe, con los dos laterales arriba y sin volante de contención tras un cambio de frente.

**Es el caso que obligó a abrir la vía 2.** El IE acertó —no hubo echada— y no vio el gol. Reconstruido con el ISE: SOB1 = 1 (local obligado, objetivo de copa a siete puntos, ocho partidos sin ganar recién cortados), SOB2 = 1 (rest defense inexistente, ya documentado en el Bloque H del EFE de la misma sesión), SOB3 = 1 (rival con contragolpe como plan A y banco de piernas frescas) → **ISE 10, P(sobreexposición) 80%, `P(gol|sobreexposición)` 55%.** El gol pasa de sorpresa a escenario modal.

**Segundo error de procedimiento de P1a, idéntico al de TDE-012.** Se había puntuado P1a = 0 por narrativa ("local obligado, va al frente los 90"). Con la salida de Regresión al Nivel: µ del partido 1.30 contra 1.46, diferencial −0.16, y corrigiendo la localía sudamericana (real ~+0.5–0.7 contra el +0.38 de µ) queda empate técnico → **P1a = 0.5, escenario abierto**. La compuerta 1 no se activa, igual que en TDE-012.

**Y el hallazgo que bloquea el candidato de P1a por µ**: el gap diferencial ajustado era **+0.72** y el diferencial de µ del partido **−0.16**. Apuntan en direcciones opuestas y darían P1a = 1 contra P1a = 0.5. El candidato no especifica qué número usa, así que no se puede ratificar hasta que se defina el input.

**Dos advertencias sobre este caso.** Es RETRO y el ISE se construyó conociendo el resultado: fija rúbrica y nada más. Y la salida de Regresión al Nivel usada era un snapshot **post-partido** (la forma de los últimos 5 incluía este partido), así que el gap está contaminado — el µ estructural sirve, la lectura de forma no.

### Reconciliación de TDE-011 y TDE-012 con Regresión al Nivel *(v0.1.3.1)*

Llegó la salida de Ley §5 del partido y permite verificar el parche y recomputar los dos casos.

**Los números del parche se confirman**: Danubio µ del partido 1.55, Cerro 1.23, gap diferencial ajustado +0.35. La objeción de procedimiento sobre P1a estaba bien fundada.

| | µ partido | gap | ajustado | forma últ. 5 | P declarado | P esquema 6 | IE decl. | IE esq. 6 |
|---|---|---|---|---|---|---|---|---|
| Danubio (L) | 1.55 | +0.47 | +0.28 | 0.80 pts | 0.63 | 0.75 | 6.2 | **6.5** |
| Cerro (V) | 1.23 | +0.10 | −0.07 | 1.20 pts | 0.63 | 0.50 | 4.5 | **4.2** |

Tres cosas salen de acá:

1. **El problema de comparabilidad del registro.** El 0.63 de TDE-012 solo cierra con cuatro indicadores (P1 = 0, P2 = 1, P3 = 1, P4 = 0.5). Motivó la columna `esquema_P` y la disciplina 12 del SKILL.
2. **La falta de definición de "favorito" en P1a**, con los dos valores defendibles dando 6.5 y 6.9. Ítem abierto en `INDICE_IE.md`.
3. **Primera activación de la compuerta 1 en el registro**, en TDE-011: P1a = 0 confirmado por el número (visitante con µ 1.23 contra 1.55, sin ventaja esperada que administrar). Se activó y **no cambió el número**, porque el promedio del bloque P ya daba 0.50. Es el primer caso de compuerta activa sin efecto y conviene tenerlo registrado: una compuerta que no muerde no es una compuerta que sobra.

**Y el aporte más grande, a la vía 2.** TDE-012 recibió al 23' y fue al frente 67 minutos con ISE 6.7 y `P(sobreexposición)` 55%, **sin conceder el segundo gol**. Es el **primer control negativo del ISE** y cubre parcialmente el cuadrante 9. Contrastado con TDE-014 —ISE 10, se expuso, concedió al 90'— da la primera señal de que el índice discrimina. Con N = 2 y los dos RETRO no concluye nada, pero es exactamente la señal que faltaba.

Nota cruzada adicional: `COLAPSO EN CASCADA` estaba activo en TDE-012 y el equipo no se desintegró tras recibir. **Cuarta evidencia a favor de mantener la goleada calibrada en 8-15%.**


### TDE-015 y TDE-016 · Nacional 1-2 Boston River (F1 Clausura uruguayo, 09.08.2026) — modo `COND`

Era el partido que faltaba de esa fecha: TDE-011 a TDE-014 cubrían los otros dos. Los dos casos se puntuaron sobre la **ventana 65-90**, con el 2-1 ya en el marcador, y por eso son los primeros `COND` del registro.

**TDE-015 · Boston River, IE 5.5 · ISE 3.3 · `ECHADA-VOL` · ventana 75-90.** Protegió un 2-1 de visitante durante 25 minutos con repliegue improvisado (`C1 = 1`), zaga rearmada por sanciones y sin banco profundo, y **no concedió**. Nacional no generó una sola ocasión clara; su única llegada fue al 90+7 de un centro largo con rebotes. Firma de bloque sostenido: 1 de 3 señales confirmada, 2 sin dato con Nivel B, así que **la firma no se declara completa**. Cuarto caso de la banda 5-7 sin echada.

**Es el caso que obligó a desdoblar P1a en dos modos.** Con `μ_partido` 0.84 contra 1.94, la escala de v0.1.4 le daba P1a = 0 y activaba la compuerta 1; la tabla de indicadores le daba 1 por ventaja obtenida. El escenario que describe la segunda cláusula —el chico aguantando de visitante— es la echada clásica, y el módulo le estaba asignando riesgo psicológico bajo. De acá salen el modo `COND` y la bandera `VENTAJA-INESPERADA`.

**TDE-016 · Nacional, IE 5.4 · ISE 10 · `SOB` · ventana 75-90 · riesgo de tramo final 44% por la vía 2.** Necesitaba el gol los últimos 25 minutos. `SOB1 = 1`, `SOB2 = 1` heredado directo del Bloque H del EFE y del M4 del DTP de la misma sesión, `SOB3 = 1`. **Se expuso exactamente como decía el falsador** —terminó con un volante de lateral improvisado, debut absoluto de un juvenil y sin contención— y **no concedió el tercero**.

**Y es el caso que abrió la regla de interacción entre vías.** La explicación de que no concediera no está en su propia estructura, que quedó partida, sino en la del rival: Boston River, ganando de visitante, eligió administrar en lugar de contragolpear con volumen. La echada voluntaria de uno canceló la sobreexposición del otro. Es el primer caso del registro donde el resultado de una vía depende de la decisión tomada en la otra.

**Nota de contaminación.** La salida de Regresión al Nivel llegó después de declarar y su forma de los últimos 5 **incluye este mismo partido** (trampa 1 de `INDICE_IE.md`): la L más reciente del local y la W más reciente del visitante son el 1-2 del 09.08. El μ estructural sirve y la dirección (+1.10) es demasiado amplia para invertirse al quitar un partido, pero la magnitud no es utilizable.

### TDE-017 y TDE-018 · declarados para la fecha 2 (15.08.2026)

Los dos con Nivel de dato C y con un aviso en la fila: **la fecha no tenía fijación oficial** al declarar, así que rival y sede se proyectaron por espejo del fixture del Apertura. La salida del motor los confirmó después (`RAC V · μ 1.00 · 6d` y `DAN L · μ 1.50 · 5d`). Si el rival cambiara, la fila se anula y se vuelve a declarar sin reescribirla.

**TDE-017 · Nacional visitante a Racing, IE 4.9 · ISE 8.3 · `SOB` · ventana 75-90.** Tercer registro consecutivo del mismo mecanismo en este equipo: `SOB2 = 1` no es un accidente, es su firma. La reconciliación con el motor **validó el criterio cualitativo de P1a** (μ 1.00 contra un rival etiquetado duro y local de nivel superior) y **corrigió F2 de 0.5 a 0**, con lo que el IE bajó de 5.4 a 4.9 y el caso salió de la banda 5-7. Es la primera vez que la regla de procedencia del dato de F2 mueve un IE de banda.

**TDE-018 · Boston River local vs Danubio, IE 5.9 · ISE 6.7 · `SOB` · ventana 75-90.** Dos aportes de rúbrica. Primero, `C3` bajó de 0.5 a 0 **con evidencia generada en la misma sesión** por TDE-015: sostuvo el 2-1 en el Gran Parque Central 25 minutos, y con el 0-1 en Progreso ya son dos ventajas de un gol sostenidas. Es la primera vez que el registro se retroalimenta dentro de una pasada. Segundo, la fila declarada anticipó su propia recomputación: dejó escrito que con P1a = 1 el bloque P subiría a 0.75 y el IE a 5.5, y el motor confirmó P1a = 1 (μ 1.50 con rival blando).

**Cuadrante nuevo declarado.** En un partido de seis puntos los dos equipos necesitan ganar, así que las dos `SOB1` valen 1 y **la regla de asimetría del módulo no se cumple**: ninguno de los dos es candidato a echada y las dos vías apuntan al mismo lado. No estaba en la lista de cuadrantes.

### Lección transversal de v0.1.5

Los dos ítems que se cerraron en dos versiones seguidas —qué cuenta como favorito en v0.1.4, y qué pasa cuando la ventaja ya está obtenida en v0.1.5— **no eran problemas de calibración sino de definición**, y los dos aparecieron en el mismo indicador. P1a concentra el trabajo conceptual del módulo porque es donde se cruza el estado del partido con la expectativa previa. La lección de procedimiento es que cuando un indicador admite dos lecturas defendibles, el defecto está en la rúbrica y no en el analista, y que el registro lo detecta solo si las dos lecturas quedan escritas en columnas distintas en lugar de resolverse por criterio.

### Lección transversal de v0.1.3

Los dos primeros fallos enseñaron que el módulo predecía territorio desde la identidad del equipo. TDE-011 a TDE-014 enseñan tres cosas más:

1. **La pregunta estaba incompleta.** Un módulo que solo pregunta "¿se va a echar?" acierta el 100% de las veces que el equipo no se echa, y en algunas de ellas el equipo concede igual, por la razón contraria. Acertar la respuesta a la pregunta equivocada es el fallo más difícil de detectar en un registro, porque no aparece como fallo.
2. **P1a por narrativa es un error reincidente**, no un descuido aislado: TDE-012 y TDE-014 lo cometieron igual, en partidos distintos y con equipos distintos. Es un problema de procedimiento, no de rúbrica, y por eso subió a la lista de disciplina del SKILL.
3. **La banda 5–7 tiene un problema de peso, no de indicadores.** Tres falsos positivos en esa franja con las compuertas ya aplicadas apuntan al bloque C. No se toca hasta N = 8, pero queda escrito de dónde va a venir la corrección.

### Lección transversal

Los dos fallos apuntan al mismo defecto de fondo: **el módulo estaba prediciendo territorio a partir de la identidad del equipo en lugar del mecanismo del partido.** Un equipo chico y cansado no se echa por ser chico y estar cansado; se echa cuando alguien lo empuja hacia atrás o cuando tiene algo que proteger. Cajamarca no tenía nada que proteger y Melgar sí.

## Casos sembrados en el registro (todos RETRO)

Los cuatro primeros del CSV son retrospectivos y están marcados como tales. Cubren a propósito los cuatro cuadrantes que el módulo necesita distinguir:

| Caso | Para qué sirve |
|------|----------------|
| Moquegua 0-0 Melgar (F3 Clausura 2026) | **Contradice** la vida útil del bloque bajo: IE alto sin fractura, porque el repliegue estaba entrenado. Calibra `P(fractura)` a la baja cuando C1 = bloque documentado |
| Cajamarca 0-2 Sport Huancayo (F3 Clausura 2026) | **Confirma** que posesión no es control: 53% de posesión y echado desde el 13' |
| Cajamarca 3-1 Melgar (F5 Apertura 2026) | Caso fundacional: `ECHADA-PSI` del favorito + `FRACTURA` en la ventana 75-90. Aviso: el ejecutor fue Barcos, hoy en otro club — la lección es del mecanismo, no del rival |
| Melgar 2-1 Sporting Cristal (F2 Clausura 2026) | **Contradice** el automatismo del favorito: se echó y no se partió, con un pivote acompañando el descenso de la línea |

## Cuadrantes que faltan cubrir

Para que el registro sea útil hacen falta casos de estos perfiles, que hoy no están representados:

1. `ECHADA-SUP` pura — equipo que deja de presionar antes del minuto 45 por plan superado, sin fatiga
2. `ECHADA-NUM` — repliegue tras roja temprana, con rearmado exitoso y con rearmado fallido
3. IE bajo que **sí** se echó — el falso negativo que más enseña
4. Bloque bajo estructural de 90 minutos en un equipo grande, no en un chico
5. Un caso de copa internacional, donde la relevancia asimétrica pesa distinto que en liga
6. Un caso de altura extrema (Andahuaylas, Cutervo, El Alto) para aislar F2 — parcialmente cubierto por TDE-007 (Cusco, 3.400 msnm) y reforzado por TDE-008 y TDE-009
7. **Falso positivo severo** — IE ≥ 7 sin echada. Cubierto por TDE-006, pero hace falta al menos uno más para saber si es un patrón de rúbrica o ruido
8. **Gol en el tramo final sin echada de ninguno de los dos** — el cuadrante que abrió la vía 2. **CUBIERTO en v0.1.5**: TDE-017 y TDE-018 están declarados antes del partido con el ISE escrito. Pendiente de cierre
9. **`SOB` con contramedida aplicada** — equipo con ISE ≥ 7 que mete el pivote fijo y no concede. **Parcialmente cubierto por TDE-012** (ISE 6.7, expuesto 67 minutos, sin conceder), pero falta uno con ISE ≥ 7 y con la contramedida identificada en cancha, no solo con el resultado a favor

**Prioridad de carga actualizada en v0.1.5: 9 primero** —falta un ISE ≥ 7 con la contramedida del pivote fijo identificada en cancha, no solo con el resultado a favor—, después 1, 2 y 5. El 8 quedó cubierto con TDE-017 y TDE-018.

**Cuadrante 10, nuevo** *(v0.1.5)*: **partido de seis puntos con las dos `SOB1` en 1.** Los dos equipos necesitan ganar, así que ninguno es candidato a echada y la regla de asimetría del módulo no aplica. Declarado en TDE-018 y pendiente de cierre.

**Cuadrante 11, nuevo** *(v0.1.5)*: **interacción entre vías** — equipo con ISE alto que no concede porque el rival, con ventaja, eligió administrar. Cubierto en modo `COND` por TDE-016; hace falta uno declarado. El cuadrante 4 (bloque estructural de 90') está cubierto tres veces en equipos chicos y sigue faltando **en un equipo grande** — ahí la presión de tribuna cambia el cálculo de P1b.

Cuando el usuario pida cargar ejemplos, priorizar estos seis perfiles antes de sumar más casos del mismo tipo.

---

## v0.1.9 · 13.08.2026 — TDE-025/026, primer caso de `rama_abandonada`

**Estado de las métricas: SIN CAMBIOS.** Las dos filas nuevas se excluyen de toda tasa.

| Métrica | Antes de v0.1.9 | Después | Motivo |
|---|---|---|---|
| Filas del registro | 21 | 23 | Altas TDE-025, TDE-026 |
| Casos ciegos y cerrados computables | 9 | 9 | Las dos altas son `rama_abandonada` |
| Echadas ciegas observadas | 1 | **1** | Botafogo se rompió, no se echó (disciplina 3) |
| Umbral binding N ≥ 5 | no alcanzado | **no alcanzado** | Sin movimiento |
| Brier sobre ciegos cerrados | 0.247 | 0.247 | Denominador intacto |
| MAE de ventana | ~2.4 | ~2.4 | Ventana no computada por rama abandonada |
| Correcciones de F2 por el motor | 3 de 3 | **5 de 5** | TDE-025 y TDE-026, de `sin dato` a 1 |

**Por qué el 6-1 no toca ningún peso.** El método manual ordena casos por score de bloque y compara el grupo que se echó contra el que no. Este partido no aporta un miembro a ninguno de los dos grupos: el que iba a echarse se rompió en el primer tiempo y el que iba a exponerse ganó por cinco. Un caso espectacular que no separa nada es, para efectos de calibración, un caso vacío — y tratarlo de otro modo por lo llamativo del marcador sería seleccionar sobre la variable dependiente con otro nombre.

**Lo que sí cambia.** Tres disciplinas nuevas (24, 25, 26), dos columnas nuevas en el registro (`IE_recomputado_motor`, `clase_caso`) y dos candidatos declarados y congelados: el modificador de goleada por asimetría fisiológica y el `D3-DEGRADADO` del EFE.

**Contra qué se falsa el candidato de goleada.** Se descongela cuando aparezca un segundo cruce con diferencial de altitud ≥2.500 m, `GK-DOWNGRADE` activo en el visitante y `MATCHUP FAVORABLE`. Si ese segundo caso termina con diferencia de dos goles o menos, el candidato se archiva.
