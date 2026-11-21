# sad-analysis · Historial

Se lee **al revisar el skill** (propuesta nueva, fase D, modo mantenimiento), **nunca al analizar un partido**. Las reglas vigentes viven en `SKILL.md`, cada una en su paso; acá quedan las notas de cada versión, los casos que motivaron cada regla y las mediciones. Las notas de la v4.5 a la v4.0 se movieron tal cual del `SKILL.md` con la v4.6 (núcleo: `docs/revisiones/NUCLEO_SKILLS_propuesta.md`); ninguna regla vivía solo en ellas (NÚCLEO §2.5, verificado de nuevo para la v4.5).

---

## Notas de versión

> **v4.8 · 21.11.2026 — ¿Entrarías? El juicio del analista, y el cierre de las burbujas.** El usuario, tras ver que el rojo de Alavés–Deportivo (1570453) salía de una regla (racha de un partido con riesgo alto) y no de un juicio: «sería bueno que también el analista diga: en este partido creo que no entro… debería verse en los partidos»; y «tal vez debamos armar la 4.8 antes, este cambio me parece importante». Propuesta y aprobación: `docs/revisiones/SAD_v4.8_propuesta.md`. **1.** 6-F: `pronostico.entrar` (entraria · dudo · noEntraria) con motivo de una lista cerrada y el hecho del partido; no mueve el número; el recibo lo pide; la lista de Partidos lo pinta (✋). **2.** 1.7 (i): `separacionLiga`, que vivía solo en el prompt. **3.** 1.7 (j): de las otras familias pesa el perfil DC; el resto es narrativa. **4.** 1.7 (a): «más empate con las dos burbujas en riesgo» cerrado como no regla (REVENTON §19.1). **5.** 1.7 (k): cuándo revienta, medido (REVENTON §20): sin periodicidad, la racha de un partido es la frágil, el típico por período no es guía, ganar por la mínima es aviso débil. **6.** Auditoría 2, pregunta 10.
>
> **Medición:** el juicio se mide hacia adelante como quinto candidato del semáforo (`docs/METODO_APUESTA.md`): si los «no entraría» y «dudo» pierden más que los «entraría».

> **v4.7 · 21.11.2026 — Dónde se le escapa el partido al favorito: el perfil del rival, el margen y lo que no es motivo.** Revisión desde el caso Bayern 1-1 Köln (1575221, 20/11), debatido con el usuario el 20 y el 21/11 («la lección que casemos de ahí es fundamental»). Ocho hipótesis medidas en el padrón (hasta 43.167 favoritos, 2019-2026, niveles previos de los dos lados, sin copas nacionales) y contra la cuota desde agosto, con `backtest_dc_record`, `backtest_forma_cuota`, `backtest_rival_resiste` y `backtest_margen` (REVENTON §15.3-§15.4, `docs/METODO_APUESTA.md`). Propuesta aprobada el 21/11/2026 con todas las recomendaciones: `docs/revisiones/SAD_v4.7_propuesta.md`. **Ningún número de la app se mueve.** **1.** Riesgo bajo se escribe «la racha suele seguir», no «sin señal de reventón» (1.7 h). **2.** El motor no ve el perfil DC del rival (+7 a +10 puntos de «no gana» contra el nivel); con cuota, la casa ya lo cobra y no se resta otra vez (6-A). **3.** El margen apretado: sin goleada ni 2+ en el marcador con las dos señales (rival que pierde por 2+ el 15 % o menos en su condición y favorito con 2+ en 3 o menos de 10); con una, se nombra la celda de un gol; manda sobre la goleada del tramo 3+ (3.5). **4.** En Sudamérica, Libertadores, Sudamericana y Liga MX el grande gana apretado: marcador con un gol de diferencia salvo un hecho (3.5). **5.** Lo medido que no es motivo, lista cerrada de ocho (Prohibiciones). **6.** El perfil DC se cita con sus dos mitades (6-B).
>
> **Fuera del skill:** el punto 7 (alertas `dato` RIVAL-RESISTE y HANDICAP-APRETADO calculadas por la app) queda como desarrollo a pedir, contrato primero; mientras no exista, el analista lee el perfil y la forma de la tarjeta. El punto 8 (candidatos del semáforo, congelados el 22/11) vive en `docs/METODO_APUESTA.md` y no entra al parte. Las lecciones de TDE y DTP del caso viajan por Aprendizaje (veredicto 1575221).
>
> **Al texto aprobado, al redactar:** el punto 2 se escribió como viñeta de 6-A (la propuesta decía «a la fuente motor»); a la viñeta de la goleada del tramo 3+ (v4.5) se le sumó que manda el margen apretado; la tabla del punto 5 va en sub-viñetas, una por fila.

> **v4.6 · 17.11.2026 — En quién desconfiar, y el falsador dice qué hace imposible el pronóstico.** Revisión desde lo aprobado el 10 y el 11/11 (`DESCONFIAR_propuesta.md`) y las 70 lecciones pendientes del 10-16/11 (`estudio_lecciones_2026-11-17/`). Ninguna lección pide mover un número. Propuesta aprobada el 17/11/2026 con todas las recomendaciones: `docs/revisiones/SAD_v4.6_propuesta.md`. **1.** DESCONFIAR se lee y se nombra; no sube la carga ni se apaga retocando el número (1.7 g). **2.** Una racha de un partido no sostiene al elegido; el `porque` nombra las dos salidas del corte (1.6 i, d). **3.** El descarte: lo calcula la app, el parte lo sostiene con una frase (6-B). **4.** La cláusula «(1X2)» es lo que hace imposible el pronóstico (6-C 5). **5.** En el extremo, el hecho del once probable se rehace con la hoja (1.6 g). **6.** El falsador por nombres lleva la vía o el rol, con `bancoProbable` (6-C 7). **7.** El banco de la matriz sale de `bancoProbable` (6-A).
>
> **Núcleo** (aplicado con la v4.6): las notas de versión salen del `SKILL.md` a este archivo; arriba queda una línea que apunta acá. La regla de `efe-dashboard` v1.13, punto 2 («la palanca del reloj y el banco de la matriz salen del banco probable de la tabla F1»), pasa al paso 6-A, porque la corrida no carga `efe-dashboard`. La fecha de la subida del zip va a `SUBIDA_VERSION`; `CORTE_VERSION` suma la v4.6.
>
> **Decisiones del usuario (17/11):** 1 (a) la frase «con 3+ partidos la espina puede leer "sigue" con la tarjeta» **no entra** (afloja la (i) de la v4.5 contra el riesgo alto); 2 (a) un descarte distinto del menos probable del número es una contradicción y se resuelve en el número; 3 (a) el falsador por nombres lleva la vía o el rol; 4 (a) DESCONFIAR sellada en el primer depósito (eso es de la app; el skill solo la lee).
>
> **Al texto aprobado, al redactar:** en 6-C 7 el texto propuesto se aplicó tal cual reemplazando la frase «con los nombres: antes del once, los del banco probable de la F1 y del DTP; con el once oficial, los de la hoja». La pregunta 9 de la Auditoría 2 suma «o en el extremo» y deja la cita a la lista de 1.6 (i) (para el extremo rige la de (g)).

> **v4.5 · 10.11.2026 — Contra el riesgo alto, un hecho; el falsador dice qué refuta; el parte no busca valor contra la casa.** Revisión desde las 260 lecciones pendientes (01-09/11; 254 acreditables, 5 de copa nacional, 1 en cuarentena que enseña) y lo medido en conversación con el usuario entre el 03 y el 09/11. Ninguna lección pide mover un número (Jev): la revisión fija rúbrica. De dónde sale: dossier del 10/11, 260 lecciones, partidos del 01 al 09/11. Propuesta aprobada: `docs/revisiones/SAD_v4.5_propuesta.md`.
>
> - **1. El origen de la burbuja** (1.7 f): inflada por un batacazo o construida por una racha; mueve la confianza y la carga, nunca el 1X2.
> - **2. Contra el riesgo alto o muy alto, «sigue» pide un hecho de la lista** (1.6 i), y la guía `pronostico` no lleva a «sigue».
> - **3. La K de la condición en su extremo no es guía** (1.6 e).
> - **4. Los dos perfiles DC dicen «la visita no gana» y no le restan bajo el mercado** (6-B): el mercado ya lo cobra (n 195).
> - **5. Lo que está en juego en la tabla, por los dos y con a quién le sirve el empate**, como contexto (6-D).
> - **6. Cada cláusula del falsador dice qué refuta**, el volumen no va en el 1X2, no niega una vía del DTP, y el banco del rival que nombra va también en el 1X2 (6-C).
> - **7. El marcador no se elige por un récord ni contra el elegido en silencio**, y la cadena dice lo mismo que el parte (3.5, 1.6 h).
> - **8. Riesgo alto en las dos burbujas: el empate se nombra, no se carga a que siga una sola** (1.7 a).
> - **9. El parte no busca valor contra la casa** (6-B; usuario, 03/11): `valorMercado` es alarma.

> **v4.4 · 01.11.2026 — La espina sin `neutra`, el número del mercado sin vías para bajarlo y el falsador sobre la ficha.** Revisión desde las 139 lecciones pendientes (115 acreditables y 24 de copa nacional; 81 de partes escritos con la v4.2, que la v4.3 dejó para esta revisión) y lo medido en la cohorte `c3-2026-09-23` (370 partes ciegos, 740 lados). Propuesta aprobada entera: `docs/revisiones/SAD_v4.4_propuesta.md`. **Fija rúbrica y no mueve un número de la app**; no afloja ninguna regla de la v4.1, la v4.2 ni la v4.3.
>
> **1. El número del favorito es el del mercado**, hacia arriba y hacia abajo, salvo un dato escrito con su cifra; queda escrita la lista de lo que NO es un dato (6-B, Auditoría 2). **2. El delta ya está en el cierre**: no se suma otra vez al mercado y un delta sin noticia no da vuelta al elegido (6-A). **3. Sale la espina `neutra`**: tres lecturas, `cero` con una lista cerrada de hechos y, sin lectura propia, la guía `pronostico` (la espina sigue al 1X2 declarado); procedimiento en cuatro pasos (1.6). **4. La espina en el extremo dice «sigue» solo con un hecho**, y con T.54 o ESCALA-LIGAS la guía es la total (1.6, 1.7 e). **5. Los dos perfiles DC alineados le quitan a la visita**, no le suman todo al local (6-B). **6. Qué es «cargar»** con riesgo alto: poner el lado de la racha sobre el mercado (1.7 a). **7. La goleada como rama nombrada y el gol del débil desde el volumen cruzado** (3.5). **8. El falsador sobre lo que la ficha registra**, una condición por cláusula y todas las vías (6-C). **9. Copa nacional entre categorías** (6-E, rúbrica; población `copa`).

> **v4.3 · 30.10.2026 — El marcador sale de los goles acotados.** Revisión de UN solo punto: la app tiene desde hoy un modelo de goles calibrado (`golesAcotados`, REVENTON §17, 50.823 partidos del padrón) y la v4.2 decía «la app no tiene modelo de goles». Propuesta aprobada: `docs/revisiones/SAD_v4.3_propuesta.md`. **No integra las lecciones del 28-30/10** (esas van en la próxima revisión), no afloja ninguna regla de la v4.2 y no toca el 1X2.
>
> **1. El marcador declarado va dentro del marcador acotado** salvo un hecho de este partido que lo saque, dicho (3.5). **2. Los goles acotados no mueven el 1X2** ni son señal de apuesta: se miden en Aprendizaje antes de darles peso (3.5, 6-B). **3. El falsador dice qué vía de gol saca el marcador del acotado** cuando la lectura se aparta de él (6-C).

> **v4.2 · 28.10.2026 — Lo que la v4.1 dejó a la vista.** Revisión desde las 165 lecciones pendientes (130 de partes escritos con la v4.1, 25-27/10), la calibración del 1X2 por versión (la v4.1 acertó 44 de 67, 66 %, contra 46 % con la v4.0, pegada al mercado en cada tramo) y la calibración de la espina (582 lados ciegos con tarjeta). Propuesta aprobada: `docs/revisiones/SAD_v4.2_propuesta.md`. **No afloja ninguna regla de la v4.1** ni toca la Ley 1, el reventón o un número de la app.
>
> **1. El mercado que se mueve y la razón que cae** (6-A): no apartarse en contra del delta apertura → cierre sin dato propio; una razón que una alerta del propio parte anula no sostiene el número. **2. Los dos perfiles DC alineados son un hecho; uno solo no** (6-B). **3. La tarjeta débil de la condición no se sigue por defecto** y queda escrita la lista de lo que no es un hecho (1.6). **4. El falsador mide conversión o vía, y el marcador lee el volumen de los dos lados** (6-C, 3.5).

> **v4.1 · 25.10.2026 — Cómo sale el número del 1X2.** Revisión desde la calibración del 1X2 declarado: 260 partes ciegos con veredicto (14/09-24/10/2026), 231 con el mercado capturado antes del depósito, validación por fecha (ajustar en la primera mitad, medir en la segunda). Propuesta aprobada: `docs/revisiones/SAD_v4.1_propuesta.md`. Toca solo el paso 6 y la Ley 4; no toca la Ley 1, la espina, el reventón ni ningún número de la app.
>
> **1. El empate parte del mercado** (6-B) y se aparta solo con un hecho de ESTE partido. **2. El favorito de 50 %+ no se recorta por debajo del mercado** sin un dato que el mercado no tenga, escrito con su cifra (6-B y pregunta 6 de la Auditoría 2). **3. La calibración de la cohorte se lee, no se aplica como fórmula** (6-B). **4. Bajas del rival, por zona** (Ley 4): la ofensiva del rival le quita goles a él, no le suma puntos al otro (Köln–Schalke).

> **v4.0 · 21.10.2026 — El skill de la síntesis, sobre lo que la app tiene.** Revisión desde el dossier de la app (379 lecciones de la cohorte `c3-2026-09-23`, 253 acreditables, ninguna pide mover un número) y desde lo medido en 209 partes con veredicto. Propuesta aprobada: `docs/revisiones/SAD_v4.0_propuesta.md`.
>
> **1. El skill era del sistema anterior.** El predictor de goles Poisson v6, la Fe Perdida y el ICF con Random Forest de la Tensión del Favorito no existen en la app SAD, y el skill pedía dos CSV y un screenshot que la corrida no tiene. Lo que no tenía motor se improvisó: en 78 de 209 partes el 1X2 se armó con un Poisson que tomaba `μ_partido` (puntos) como λ de goles, y dos partes invocaron la Fe Perdida sin dato. **Se suspende todo lo que no tiene motor** (tabla en «Las leyes»), con su motivo; nada se borra ni se renumera.
>
> **2. Este skill es dueño de la síntesis**: la lectura de las K (espina y reventón) y el pronóstico (tres fuentes, probabilidades, marcador, falsador), más la lectura integrada que antes definía `efe-dashboard`. EFE, TDE y DTP describen; este skill concluye.
>
> **3. Las K pesan el 60 % de la LECTURA** (antes «70 % del peso»). Bajan diez puntos para darle más lugar a lo demás (EFE, TDE, DTP, regresión, mercado), y es el peso en la lectura de cada equipo, **no en el número del 1X2**: el backtest (REVENTON §13.3-13.4) mostró que las K no mejoran el 1X2 del motor, y desde el 14.10.2026 no entran a la fórmula. La Ley 1 conserva sus gatillos, la fusión y la anti-tautología.
>
> **4. Entran al skill las reglas que vivían solo en el prompt** —la espina, el riesgo del reventón, las tres fuentes, el umbral 0,30, el falsador— con las correcciones de la cohorte (pasos 1.6, 1.7, 5 y 6).
>
> **5. La Ley 5 (Tensión del Favorito) queda suspendida** (backtest del 19.10.2026: 63.475 partidos, sin culebra). Queda en pie una regla de mercado: la combinada de favoritos tiene poca probabilidad y paga el margen de la casa k veces.

---

## Mediciones y observaciones sin regla

Medidas en conversación con el usuario. **No son reglas y no van al cuerpo del skill**: una cifra como «≤ 2 pts gana el 66,7 %» en el núcleo invita a pegarse a la casa para quedar del lado bueno, y la señal deja de medir (anti-Goodhart). Lo que el skill tiene que decir ya está escrito: el número del favorito es el del mercado (6-B, v4.4) y el marcador acompaña al elegido o se dice (1.6 h, v4.5).

> **(h) Distancia a la casa** *(usuario, 11/11/2026; observación, no regla)*. 374 partes del 15/09 al 01/11, por la mayor distancia entre nuestro 1X2 y la casa sin margen: con ≤ 2 pts en los tres resultados el elegido ganó 66,7 % contra 53,7 % que pedía la casa (n 177); de 2 a 5 pts, 44,2 contra 46,7 (n 104); de 5 a 10, 46,0 contra 51,1 (n 63); de + 10, 50,0 contra 53,1 (n 30). Eligiendo distinto que la casa (33): 11 aciertos contra 10 del favorito de la casa. El valor no está en apartarse de la casa: está en marcar cuándo creerle.
>
> **(i) Marcador contra el elegido** *(usuario, 11/11/2026; observación, no regla)*. En 83 de los 374 partes el marcador declarado contradecía al elegido del 1X2: ahí el elegido acertó 39,8 %. Con el marcador acompañando, 60,1 % contra 55,6 % de la casa. Refuerza lo que ya pide 1.6 (h): el marcador lo gana el elegido o la lectura dice cuál de los dos manda y por qué.

Estudio del 17/11 sobre (h) e (i): sin material nuevo. Torque 1649057 (50 contra 50,2) y Portugal 1528974 (59 contra 59,6) estaban pegados a la casa y el elegido no ganó: anécdotas que la n 177 cubre mejor.

---

## Casos y mediciones de la v4.6

Fuente: `estudio_lecciones_2026-11-17/`, 70 lecciones de partidos del 10 al 16/11 (35 sostuvo, 20 regla falló, 14 mal aplicada, 1 imprevisto). Una semana, mayoría de fecha FIFA, y 7 de copa nacional (rúbrica, no métrica). Son lecciones escritas, no un muestreo.

**DESCONFIAR (1.7 g).** Cuatro partidos con la alerta:

| Partido | Elegido | ¿Ganó el elegido? | «Elegido o empate» |
|---|---|---|---|
| Suecia–Bosnia 1528978 | Suecia | sí | sí |
| Mirassol–Atlético-MG 1492455 | Mirassol | no (empate) | sí |
| Puerto Cabello–Monagas 1646937 | Puerto Cabello | no (perdió) | no |
| Italia–Francia 1528960 | Francia | no (ganó Italia) | no |

El elegido ganó 1 de 4: la dirección de la alerta se sostiene. La doble oportunidad acertó 2 de 4: no adelanta la opción (c) del método (queda para los 100+). `SOBRE-LA-CASA`: ninguna lección lo nombra (Armenia–Chipre 1528959 eligió la racha un punto sobre la casa, bajo el umbral). *Se sostiene si,* con 100+ partidos con alerta, el elegido acierta menos que sin ella; *lo tumba si* no hay diferencia. La medición es la tarjeta de la Simulación.

**Racha de un partido con riesgo alto o muy alto (1.6 i, d).** Se cortaron 8: cinco + (Racing 1649057, Chicó 1549870, Boston River 1649432, Mirassol 1492455 y Cali 1549867; el riesgo de Cali lo cuenta el estudio, no la lección) y tres − (Monterrey en Querétaro–Monterrey 1550951, Millonarios 1549871, Bélgica 1528958). Siguió 1: Dinamarca 1528974, ante un rival muy fuerte. Eslovaquia 1528967, de riesgo medio, también se cortó. Son lecciones, no denominador: la guía calibrada ya da 35 % y 28 % a que siga. **No entró** (decisión 1): «las burbujas de 3+ partidos son las que arrancan: ahí la espina puede leer "sigue" con la tarjeta»; contra el riesgo alto aflojaba la (i) de la v4.5.

**El descarte (6-B).** Hasta el 17/11 el descarte sale 17,0 % contra 21,8 % de la casa (264 partes), pero coincide con el de la casa en 251: todavía no descartamos distinto que ella. Lo aprobado decía «el menos probable, o el que la lectura excluye con un hecho»; con dos definiciones el número diría una cosa y la frase otra (decisión 2).

**El falsador «(1X2)» (6-C 5).** 6 de 6 mal aplicadas, todas con el 1X2 acertado: Lituania 1528989 («si Liechtenstein marca», 2-1 con 86 %), Finlandia 1528981 (7-2 con 92 %), Chipre–Montenegro 1528979 (el penal del 52'), Noruega 1528972 (el suplente marcó con 0-2), Inglaterra–Croacia 1528962 (un renglón de marcador mezclado en la condición del 1X2). Corrección al estudio: «el gol del rival con 0-0» tampoco es «(1X2)» (UCV Moquegua–Grau 1549560: «si Grau marca primero» sonó al 24' y el local ganó).

**K-CERCA-EXTREMO declarado y apostado igual (1.6 g).** 4 mal aplicadas de 8 (las otras 4 se sostuvieron: Santa Fe 1549869, Torque 1649057, Boston River 1649432, Anaitasuna 1644336). Tres eran cumplimiento de reglas escritas (Armenia–Chipre 1528959, Portugal–Dinamarca 1528974, Letonia–Armenia 1545616; la guardia es de la app, `1X2-CARGA-CONTRA-RIESGO`); la cuarta pidió la línea del once (Mirassol–Atlético-MG 1492455).

**El falsador por nombres (6-C 7).** 3 casos: falló en Comerciantes–Sport Boys 1549557 y en Inter Bogotá–América 1648690 (goleadores con una rotación probable de cinco); sirvió en Águilas–Medellín 1549863, que nombraba un rol (el banco). Kosovo–Israel 1528971 va en la misma dirección.

**A backtest, no al skill** (`SAD_v4.6_propuesta.md` §3): el corte a cero y no al otro signo, por largo de racha; la rama de goleada; el 1X2 o el empate (Luxemburgo, Always Ready, Italia–Francia, Llaneros). Lo que toca la guía calibrada, el 1X2 o el empate no se cambia por lecciones.
