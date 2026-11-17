# Historial · `efe-clasificador`

Se lee **solo al revisar el skill** (fase D, modo mantenimiento, una propuesta
nueva), nunca al analizar un partido. Toda regla vigente está en el cuerpo de
`SKILL.md` o de `references/rubrica-efe-v1.11.md`; acá quedan las notas de
cada versión, los casos de validación y las mediciones, movidos tal cual
(núcleo, `docs/revisiones/NUCLEO_SKILLS_propuesta.md`, aplicado con la v1.11).

---

## Changelog

> **Changelog v1.11** (17.11.2026) — Revisión desde las 189 lecciones pendientes (10-16/11, todas ciegas PRE; una semana con mayoría de selecciones —fecha FIFA— y unas 20 de copa nacional). Clasificación por la prosa: 123 la regla se sostuvo · 35 mal aplicada · 14 la regla falló · 9 insumo · 7 no dice · 1 de otro skill. Ninguna pide mover un número: pesos, máximos, cortes de la tabla de puntuación, cortes de zona, el ×1,5 de F2c y los umbrales de las alertas quedan como están. Aprobada por el usuario el 17/11 con todas las recomendaciones. Propuesta: `docs/revisiones/EFE_v1.11_propuesta.md`. Se aplica con el núcleo.
> 1. **Una fila por titular, sin umbral; el 3 es del recómputo** (F1, punto 6): con el once, cada titular sin fila se agrega aunque sea uno; el 3 es el corte desde el cual la app exige el recómputo de B y F (`EFE-RECOMPUTO-PENDIENTE`), no de la tabla. Decisión 1 (a): con el once B y F se recomputan **siempre** y la app lo exige desde 3; la nota B lleva la marca literal «recomputado con el once» y la prosa de bajas se reescribe entera. En `SKILL.md`, «con ≥ 3 titulares fijos rotados» pasa a «con el once oficial … (desde 3 titulares fijos o con el arquero, la app lo pide con `EFE-RECOMPUTO-PENDIENTE`)» en la regla de la rama y en el punto 6 de «Cuando no hay XI». Casos: 19 lecciones, 15 partidos (Kazajistán 1528968, Eslovaquia 1528967, Feroe 1528967, América 1648690, Alavés 1644336, Montenegro 1528979, Inter Bogotá 1549869…).
> 2. **El arco: B6 🔶, la zona GK en rojo y GK-DOWNGRADE miden continuidad o ausencia, no son vía de gol** sin GK-FALLA-ACTIVA o errores documentados; B6 se puntúa con los minutos de la hoja (9 + 2 casos: Chequia 1528985, Inglaterra 1528984, Turquía 1528982, Pasto 1549868, Celta 1644376; Moldavia 1528987). En `SKILL.md`, «Cuando no hay XI», punto 4: «el ×1,5 mide la ausencia, no es vía de gol del rival».
> 3. **Rama «once alternativo»: el clasificado o eliminado en la última fecha es un hecho** que la abre; un contraargumento no la cierra (6 casos: Bucaramanga 1549865, Sport Boys 1549557, Always Ready 1649146…). Cuando la rama se escribió acertó 10 de 14.
> 4. **B5 en copa, por rol y condicionado al once**; la lista es `bancoProbable` de `GET …/f1/{id}`; con el once, la hoja (4 casos: Boston River 1649058, UD Logroñés 1644335, Real Potosí 1649149, Garcilaso 1549559).
> 5. **Jerarquía de fuentes: ejemplos de redacción** que van a Duda y el convocado con sanción discutida (sin regla nueva; Always Ready 1649148, Bucaramanga 1549865, Islandia 1545617, Tolima 1549867).
> 6. **F3: la reducción usa el rol de hoy en la competición**, no el titular nominal (decisión 2 (a), entra como aclaración; Bélgica 1528958, Hungría 1528973, Atlético-MG 1492455).
> - **COLAPSO + AGRAVANTE** suma su cuarto caso (San Marino 1528981, 2-7, con μ 2,31 contra 0,49 de por medio) y **sigue candidato** hasta tener el denominador (decisión 3 (a), A7).
> - **Núcleo:** el changelog v1.10 … v1.4 y el apéndice de casos de validación salen de la rúbrica a este archivo; la rúbrica pasa a `references/rubrica-efe-v1.11.md`; la quinta lista del barrido fijo de F5 (el suplente con impacto documentado desde el banco, regla D1 de efe-dashboard v1.8) sube al cuerpo; «Disciplina 35» del `SKILL.md` se renombra «Bloque F sin XI confirmado», mismo texto (la disciplina 35 del TDE es otra cosa y quedó derogada por la 55).
> - **Candidatos a medir, NO aprobados:** bajar el ×1,5 de F2c o no activar GK-DOWNGRADE con un suplente con titularidades (9 en contra de la vía, 1 a favor: Mijas, arco alternado); el umbral del B5 🔶 por un partido de banco decisivo (Albion, 2 casos; A8); COLAPSO + AGRAVANTE como regla (A7); F3 leída con H contra un rival sin profundidad (Andorra 1545615, Eslovenia 1545654); EFE-EMPATE-TECNICO con y sin la alerta (A6).
>
> **Mediciones de la v1.11 (alertas, lecciones 10-16/11):** F3 30 lecciones (29 partidos), 22 se sostuvo, 4 la regla falló, 3 mal aplicada, 1 otro skill · EFE-EMPATE-TECNICO 27/27 «se cumple» (irrefutable así escrita; por la prosa ganó el de menor porcentaje en ~9 y hubo empate en ~11; la prueba es A6) · EJE-DEBUTANTE 14, 9 se sostuvo, 4 no dice, 1 mal aplicada (lo que falla es el insumo) · COLAPSO EN CASCADA 11, 10 se sostuvo, 1 no puesto a prueba · T.54 5/5 · FACTOR-X 3/3 · G-BLOQUE 1 de 3 (2 sin poner a prueba). Sueltos que no entran (1-2 casos): D3 ❌ de visita que pierde la ventaja cuando abre (Grau 1549560), D3 por racha en vez de respuesta (UTC 1549556), DT suspendido sin mirar (Maldonado 1649059), E alto hecho contra rivales muy inferiores (Gibraltar 1545615).
>
> **Changelog v1.10** (10.11.2026) — Revisión desde las lecciones pendientes de los partes escritos con la v1.9. De dónde sale: dossier del 10/11, 639 lecciones (568 del primer corte y 71 del segundo), partidos del 01 al 09/11, todas ciegas PRE. Ninguna pide mover un número: ningún peso, máximo ponderado, corte de la tabla de puntuación ni corte de zona tocado. Absorbe la propuesta del 08/11 (nunca aprobada). Decisiones del usuario del 10/11. Propuesta: `docs/revisiones/EFE_v1.10_propuesta.md`.
> 1. **Con el once oficial, el rehacer empieza por la tabla F1**, en orden fijo (F1 → bajas de la hoja → B6 → EJE-DEBUTANTE → B y F → D1 y H); la baja que está en la hoja deja de serlo; la F1 lleva a los candidatos al puesto, y la fila `delOnceOficial` que suma la app se usa, no se borra.
> 2. **Con D1 🔶 o T.54 de ≤ 2 partidos**, D1, H, la zona de cada baja y la F3 por zona van condicionados al once oficial o en dos variantes; el once de la API antes del pitazo es nivel B.
> 3. **EJE-DEBUTANTE con el once se chequea sobre la línea entera del grid**, no sobre la pareja de la apertura.
> 4. **El suplente sin rodaje en el arco es vía a vigilar**, no vía firme (que pide GK-FALLA-ACTIVA o errores documentados); B6 sin fuente es `sin dato` y la base cuenta como fuente.
> 5. **La roja calculada de la misma competición es ❌ Baja con la rama «si juega»** cuando ninguna fuente de nivel 1-3 la confirma; el ciclo de amarillas pasa a ⚠️ Duda con su rama.
> 6. **La rama «once alternativo» también se abre por un hecho** (rotación anunciada, costumbre del DT, equipo sin nada en juego), carga a los rotables de todas las líneas, el condicionado se levanta en las dos direcciones y la F3 de una rotación elegida es F4.
> 7. **La F3 por la zona DEF anuncia la vía del rival o el volumen concedido**, y el gol lo decide sobre todo el arquero (corrige el «no el volumen» de la v1.8).
> 8. **La F3 en ATK y MID se paga en volumen, en dónde se remata o en la conversión**; con un recambio con minutos en la casilla, «cubierta de oficio» y solo confianza en la K.
> 9. **La F1 admite `banco probable` y B5 nombra el banco por rol**; «banco corto» solo con la tabla mirada entera.
> 10. **Once tardío** (a menos de 20 minutos del pitazo): «F1 sin verificar» y «once tardío, sin verificar» en el eje.
> - **Notas sin cambio de regla:** la vía del rival en ámbar (2 casos, candidato), el D3 con pocos casos (espera A7), el sistema condicionado con toda serie corta (Genk), el eje que vuelve por un cambio y los candidatos del segundo corte. La nota de la brecha en la misma base no cambia hasta medir (A6). La regla 6.2 de la propuesta (condicionar según la costumbre del DT) no entra: se mantiene la v1.7.
>
> **Changelog v1.9** (01.11.2026) — Revisión desde las 296 lecciones pendientes de los partes escritos con la v1.8 (28/10 al 01/11, todas ciegas PRE; 43 de copa nacional, que fijan rúbrica y no entran a ninguna métrica). Ninguna pide mover un número: ningún peso, máximo ponderado, corte de la tabla de puntuación ni corte de zona tocado; el ×1,5 del arquero tampoco. Muchos «fallos» eran reglas ya escritas que no se aplicaron: esta versión las **cobra** antes que reescribirlas. Propuesta: `docs/revisiones/EFE_v1.9_propuesta.md`.
> 1. **La tabla F1 lleva al equipo que puede jugar**, no solo al último once: el recambio probable de cada baja o duda (el arquero suplente siempre), los rotables de la rama «once alternativo», todo jugador que la prosa del EFE nombra y, con el once oficial a la vista, los once titulares. El rol sale de la temporada, no de la última fecha. El tope de 14-16 no se sube como número.
> 2. **La rama «once alternativo»** se escribe para los dos equipos en una copa con liga a ≤ 5 días, dice quién rota, qué sistema y quién queda en el banco para volver; con T.54 de ≤ 2 partidos el XI de referencia es nivel C y B6 y F van condicionados al once oficial; el recomputo de B y F con ≥ 3 titulares fijos rotados ya era regla y ahora se cobra.
> 3. **El arquero:** el rodaje de la v1.8 cuenta la carrera en la categoría, no los minutos de la temporada; la zona GK se calcula sobre el arquero que ataja hoy; el suplente sin rodaje se declara como vía del rival al DTP.
> 4. **Las fuentes del F1 en las dos direcciones:** una vuelta al once que solo dice un agregador también es Duda y no activa FACTOR-X; el estado de lesión de la API es nivel 4; la sanción calculada de la base es nivel 1; una convocatoria que solo cita la prensa es nivel 2 o 3.
> 5. **La F3 por zona dice qué anuncia** (ATK: menos volumen propio · MID: esterilidad propia · DEF: la vía del rival) **y quién cubre la zona** («degradada, cubierta de oficio»); con el rival de otra base o SIN FORMACIÓN, la F3 es confianza en la K, no dirección del partido.
> 6. **D3 y E se leen en la condición del partido**; un partido con un jugador de más o de menos por más de 20 minutos no sostiene un D3; la nota del D3 dice cuántos casos y qué cara. COLAPSO: «no predice la ruptura»; el candidato COLAPSO + AGRAVANTE suma su tercer caso (Udinese) y **sigue candidato**.
> 7. **EJE-DEBUTANTE se verifica con el once oficial:** sin él va siempre condicional; con él se declara o se descarta con el grid.
> - **Notas sin cambio:** la brecha en la misma base ordena al ganador más probable, no el dominio ni descarta el empate; la brecha con F3 en el lado que la lidera queda candidato; los seis contraejemplos del empate técnico no mueven la regla.
>
> **Changelog v1.8** (28.10.2026) — Revisión desde las 179 lecciones pendientes de los partes escritos con la v1.7 (25 al 27/10, todas ciegas PRE; ninguna pide mover un número). Ningún peso, máximo ponderado ni corte de la tabla de puntuación tocado; el ×1,5 del arquero tampoco. Propuesta: `docs/revisiones/EFE_v1.8_propuesta.md`.
> - **T.54 se revisa en los dos lados, con la fecha del DT** (`dt.desde`): un DT de menos de 6 meses es T.54 o T.54-B, nunca en blanco; el oficializado en los 7 días previos se puntúa como banco que dirige. La app avisa `T.54-SIN-DECLARAR` y la cuenta en `EFE-EMPATE-TECNICO`.
> - **El arquero:** la F3 por zona GK no se activa sola si el suplente tiene ≥ 15 partidos en la categoría o titularidades en los últimos 12 meses (el umbral de B6 🔶); «arco sin dueño» abre los tres escenarios en la caja de sensibilidad.
> - **La zona del ausente sale de su rol en el sistema del once** (grid), y la F3 del medio dice si el eje está entero.
> - **Las fuentes del F1 tienen fecha:** dentro del mismo nivel manda la más reciente; una baja de más de 7 días que la previa de la víspera contradice es Duda; una salida que el club no confirmó no saca al jugador de la tabla.
> - **La caja de sensibilidad baja al partido:** el supuesto con declaración pública del DT pasa al matchup H como rama; la zona que se vuelve crítica baja la confianza un escalón antes del 1X2.
>
> **Changelog v1.7** (25.10.2026) — Revisión desde las 168 lecciones pendientes de la cohorte `c3-2026-09-23` (partidos del 21 al 24/10, todas ciegas PRE; ninguna pide mover un número). Ningún peso, máximo ponderado ni corte de la tabla de puntuación tocado. Propuesta: `docs/revisiones/EFE_v1.7_propuesta.md`.
> - **Reducción por zona leída por lo que genera y por quién entra:** F3 por zona (una zona 🔴 > 40 % activa F3 aunque el IP no pase de 7), recambio «de oficio» o «reconvertido» declarado, y el no convocado por descanso va a F4, no a F2.
> - **Jerarquía de fuentes del F1:** la previa de un agregador es ⚠️ Duda, nunca ❌ Baja; una hoja incompleta no cierra el bloque F; el TF que falta sin parte va a la caja de sensibilidad.
> - **D3 con su contexto** (condición, competición, escala): el candidato D3-DEGRADADO pasa a regla en esa forma; la semántica de los tres niveles queda escrita (✅ recupera · 🔶 reacciona sin sostener · ❌ no recupera). COLAPSO EN CASCADA: solo se evalúa si el D3 ❌ recibe primero, se desactiva si el que abre se queda con 10; candidato «COLAPSO + agravante → ruptura».
> - **Rotación por calendario:** con eliminatoria a ≤ 5 días o 3.er partido en 8 días, rama «once alternativo» y porcentaje condicionado al once oficial; con ≥ 3 TF rotados en el once oficial, B y F se recomputan antes de cargar; F4 mide dependencia con los rotados de inicio.
> - **El porcentaje no se compara entre bases distintas** (ESCALA-LIGAS, R-KT.2, T.54 en un lado = empate técnico de formación) y el bloque E se lee con su calendario.
> - **EJE-DEBUTANTE entra a la rúbrica** (alerta por fecha, declarativa): ≥ 2 titulares de la misma línea con **≤ 1 partido juntos** (antes 0 minutos, en `efe-dashboard`); las posiciones de la línea se leen del grid del once.
> - **T.54 con interino que repite ≥ 9 de 11:** C4/D3 heredados a la caja de sensibilidad; la serie del DT nuevo más corta que la ventana de validación (6-8) amplía el rango. C4 por condición y dos pérdidas de ventaja seguidas = patrón.
>
> **Changelog v1.6** (21.10.2026) — Revisión desde el dossier de la app SAD (35 casos PRE ciegos de la cohorte `c3-2026-09-23`, 341 lecciones acreditables, ninguna pide mover un número). Ningún peso, máximo ponderado ni corte de la tabla de puntuación tocado.
> - **COLAPSO EN CASCADA deja de predecir goleadas.** Su escenario completo —el equipo con D3 ❌ recibe primero ante un rival con D3 ✅/🔶— se dio en unos ocho casos (Mushuc Runa, Emelec, La Guaira, Necaxa, Tigre, Pereira, Racing de Santander, Estudiantes de Río Cuarto) y en ninguno hubo colapso; las dos goleadas de la cohorte fueron de equipos con D3 🔶 (Fenerbahçe 0-6, Cagliari 0-4). La alerta conserva el escenario y pierde la predicción y la instrucción de mercados: **D3 ❌ = riesgo de perder una ventaja, no de romperse**. El candidato D3-DEGRADADO suma dos casos y sigue candidato.
> - **F5 con barrido fijo** (cuatro listas) y FACTOR-X sin cambios en su regla: amplía el rango, no mueve el centro (confirmada en ~12 cierres).
> - **T.54 descuenta todo lo heredado** (D3, C4 y lecturas de colapso del DT anterior van `sin dato`), **respeta la serie del DT nuevo** (se corta en la fecha del cambio), se puntúa sobre **el banco que dirige** y descuenta la serie, no el partido.
> - **B5 por lo que entra:** sin evidencia de impacto, `sin dato`; y B5 ✅ no compensa un F3 rojo cuando la rotación toca una pareja de la misma línea.
> - **B6 se rehace con el once oficial**; el suplente que entra por lesión corta se declara; **alta de GK-FALLA-ACTIVA** (declarativa, sin peso).
> - **G-SORPRESA amplía el rango, no mueve el 1X2** (regresó en cinco casos y se sostuvo en cuatro).
>
> **Changelog v1.5** (25.03.2026) — Post-caso Junior 2-0 Bucaramanga:
> - **B6 (nuevo):** Indicador de continuidad de portería (efecto GK-downgrade)
> - **F2c (nuevo):** Multiplicador de posición crítica para GK en cálculo de IP
> - **F5 (nuevo):** Identificación de "jugador emergente / factor X" en plantilla
> - **GK-DOWNGRADE (nueva alerta):** Degradación de portería por transferencia del titular
> - **FACTOR-X (nueva alerta):** Jugador emergente no capturado por K históricas
> - Ajuste en máximos ponderados del Bloque B (de 5 a 6 indicadores)
> - Caso 2 de validación: Junior 2-0 Bucaramanga
>
> **Changelog v1.4** (24.03.2026) — Post-caso Estudiantes 5-0 Central Córdoba:
> - **B5 (nuevo):** Indicador de profundidad de banco (efecto supersub)
> - **T.54-B (nuevo):** Modificador "Herencia de ciclo" para atenuar T.54 cuando DT nuevo hereda plantel campeón
> - **Bloque H (nuevo):** Matchup táctico entre equipos (peso 0×, genera alertas)
> - **G-BLOQUE (nueva alerta):** Vida útil del bloque bajo del rival
> - **COLAPSO EN CASCADA (nueva alerta):** Predicción de goleadas vía D3
> - **F4 (nuevo):** Rotación voluntaria del DT como señal de profundidad
> - Ajuste en máximos ponderados del Bloque B (de 4 a 5 indicadores)

---

## APÉNDICE: REGISTRO DE CASOS DE VALIDACIÓN

*(Esta sección acumula los partidos donde el EFE fue aplicado pre-partido y luego contrastado con el resultado real, para calibración continua del modelo.)*

### Caso 1 — Estudiantes 5-0 Central Córdoba (F12 Apertura 2026, 23.03.2026)

| Dato | Estudiantes | Central Córdoba |
|------|-------------|-----------------|
| EFE pre-partido | 57% 🟢 FORMADO | 41% 🟡 EN FORMACIÓN |
| Resultado | ✅ Victoria 5-0 | ❌ Derrota 0-5 |
| Alineación | 4-1-4-1 (Iacovich; Meza, González Pírez, T. Palacios, Mancuso; Piovi; Cetré, Amondarain, Castro, T. Palacios; Carrillo) | 5-3-2 (Aguerre; Barrera, Mansilla, Maciel, Pignani, Moya; González, Cardozo, Vera; Santos, Naya) |
| Posesión | 60.8% | 39.2% |
| Remates | 18 (9 al arco) | 3 (1 al arco) |
| Goles | Castro 47', Amondarain 70', Gaich 80' 85' 88' | — |

**Qué acertó el EFE v1.3:**
- Clasificación general correcta (🟢 > 🟡)
- D3 ❌ de Central Córdoba anticipó el colapso tras recibir gol
- T.54-PARCIAL en Estudiantes fue prudente

**Qué no capturó el EFE v1.3 (→ corregido en v1.4):**
- Profundidad de banco de Estudiantes (Gaich 3 goles desde el banco) → **B5**
- Inercia del plantel campeón atenuando el cambio de DT → **T.54-B**
- Matchup táctico: 5-3-2 bloque bajo vs juego aéreo fuerte → **Bloque H**
- Vida útil del bloque bajo (~60 min) → **G-BLOQUE**
- Predicción de goleada por D3 ❌ → **COLAPSO EN CASCADA**
- Rotación de 3 titulares sin caída de rendimiento → **F4**

### Caso 2 — Junior 2-0 Bucaramanga (F13 Apertura 2026, 24.03.2026)

| Dato | Junior | Bucaramanga |
|------|--------|-------------|
| EFE pre-partido | 52% 🟡 EN FORMACIÓN | 87% 🟢 FORMADO |
| Resultado | ✅ Victoria 2-0 | ❌ Derrota 0-2 (primera del torneo) |
| Alineación | 4-3-3 (Silveira; Guerrero, Peña, Monzón, Suárez; H. Rivera, Ríos, Canchimbo; Barrios, Sarmiento, Teo) | 4-3-3 (Vásquez; A. Gutiérrez, Mena, García, De Las Salas; F. Charrupí, Flores, Londoño; Sambueza, Salazar, Pons) |
| Goles | Sarmiento 43' (tiro libre), Teo Gutiérrez 65' | — |
| Contexto | Ultimátum mediático a DT Arias. Bajas: Chará (DT), Celis (lesión), Paiva (lesión). | Invicto de 14 partidos roto. Baja: Batalla (lesión). Sin Quintana (transferido a IDV). |

**Qué acertó el EFE v1.4:**
- Variable decisiva correcta: "El primer gol es el partido" (Lago-Peñas). Sarmiento marcó al 43' y BUC nunca pudo remontar
- Mecanismo de gol: pelota parada (tiro libre) como vía más probable para Junior
- Factor localía + presión existencial como motor emocional (efecto Anticulebra)
- BUC sin capacidad de remontar: "Si Junior cierra centralmente, BUC no tiene plan B"
- H2H en Barranquilla desfavorable para BUC (4V 1E en últimos 5) — confirmado
- D3 ❌ de Junior no se puso a prueba (nunca fue abajo) — alerta correctamente emitida pero sin escenario de activación

**Qué no capturó el EFE v1.4 (→ corregido en v1.5):**
- Degradación de portería de Bucaramanga: Aldair Quintana (selección Perú, transferido a Independiente del Valle) fue reemplazado por Luis Vásquez, que mostró responsabilidad en ambos goles. Las K defensivas de BUC (6 GC en 11 PJ = menor goleado) estaban infladas por Quintana → **B6 + GK-DOWNGRADE**
- Jugadores decisivos fuera del perfil K: Sarmiento (fichaje reciente, 0 goles previos) y Kevin Pérez (regreso de lesión) no fueron identificados como posibles factores diferenciales → **F5 + FACTOR-X**
- Sobreestimación del EFE de BUC: 87% FORMADO pero con GK downgrade no capturado, lo que inflaba artificialmente la confianza en sus K defensivas. Con B6 y el nuevo cálculo, BUC habría sido ~78-80% (aún FORMADO pero con alerta de degradación en GK)
- El multiplicador de IP para GK habría elevado el impacto de la ausencia de Quintana en el Bloque F → **F2c**

