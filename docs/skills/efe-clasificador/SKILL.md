---
name: efe-clasificador
description: Rubrica completa del clasificador EFE v1.9 del sistema SAD, Estado de Formacion de Equipo, con los ocho bloques A-H, los pesos ponderados, la tabla de puntuacion, las alertas automaticas estructurales y por fecha, y el registro de casos de validacion. Activar siempre que el usuario pida un EFE de un equipo o un partido, hablar de estado de formacion, bloques A-E, sub-scores, impacto ponderado de ausencias, reduccion por zona, clasificacion FORMADO o EN FORMACION o SIN FORMACION, o cualquier alerta del sistema como T.54, T.54-B, R-KT.2, GK-DOWNGRADE, GK-FALLA-ACTIVA, EJE-DEBUTANTE, FACTOR-X, F3, G-BLOQUE o COLAPSO EN CASCADA. Activar tambien antes de correr el skill efe-dashboard, porque este skill aporta la rubrica y el otro aporta la visualizacion. Activar tambien en corridas batch del pipeline SAD donde haya que puntuar equipos pre-partido.
---

# Clasificador EFE v1.9

Este skill guarda la rúbrica operativa del EFE (Estado de Formación de Equipo), el módulo estructural del sistema SAD.

## Cómo usarlo

1. **Leé `references/rubrica-efe-v1.9.md` completo antes de puntuar nada.** Contiene los ocho bloques con sus tablas de indicadores, los fundamentos de cada regla y los casos de validación. No puntúes de memoria.
2. Investigá en la web lo que pide la sección "Instrucciones de ejecución" de la rúbrica: cuerpo técnico, historial de cambios de DT, plantel, mercado, tabla, resultados, ausencias de la fecha, fixture y sistema táctico del rival.
3. Completá los bloques en orden, justificando cada indicador con el dato encontrado y citando la fuente.
4. Aplicá los pesos, calculá el porcentaje y emití el diagnóstico con las implicaciones para el SAD.
5. Verificá **todas** las alertas automáticas, no solo las que parecen obvias.

## Reglas que no se negocian

- **Modo PRE / selección ciega.** Todo se declara antes del pitazo. Nada de puntuar con el resultado a la vista. Lo que se escriba después del partido va marcado `RETRO` y no cuenta para calibración.
- **Disciplina 35 — el Bloque F no se puntúa sin XI confirmado.** No lo rellenes con el plantel ni lo estimes. Si no hay XI confirmado, ver más abajo.
- **Sin dato es respuesta válida.** Si un indicador no tiene información, se escribe `sin dato`, se excluye del denominador cuando la rúbrica lo permite y se abre caja de sensibilidad. No se estima para rellenar.
- **Las fuentes de bajas tienen jerarquía (v1.7).** Club > prensa local > prensa nacional > previa de agregador. Una baja que solo dice un agregador va ⚠️ Duda, nunca ❌ Baja.
- **T.54 en los dos lados, con la fecha del DT (v1.8).** Un DT de menos de 6 meses es T.54 o T.54-B, nunca en blanco; el oficializado en los 7 días previos se puntúa como banco que dirige. La app avisa `T.54-SIN-DECLARAR`.
- **Las fuentes del F1 tienen fecha (v1.8).** Dentro del mismo nivel manda la más reciente; una baja de más de 7 días que la previa de la víspera contradice es Duda, y una salida que el club no confirmó no saca al jugador de la tabla.
- **La tabla F1 lleva al equipo que puede jugar (v1.9).** El recambio probable de cada baja o duda (el arquero suplente siempre), los rotables de la rama «once alternativo», todo jugador que la prosa del EFE nombra y, con el once oficial a la vista, los once titulares. El rol sale de la temporada, no de la última fecha. Lo que no tiene fila no pesa en el IP: la app avisa `F1-DECISIVO-FUERA` y `ONCE-SIN-FILA-F1`.
- **La rama «once alternativo» va a los dos lados en copa (v1.9).** Con liga a ≤ 5 días, la escriben los dos equipos y dice quién rota, qué sistema y quién queda en el banco para volver; con ≥ 3 titulares fijos rotados en el once oficial, B y F se recomputan: no hacerlo es un incumplimiento.
- **El eje se verifica con el once oficial (v1.9).** Sin once, EJE-DEBUTANTE va condicional («si repiten X–Y»); con el once, se declara o se descarta con el grid.
- **La jerarquía de fuentes vale en las dos direcciones (v1.9).** Una vuelta al once que solo dice un agregador es Duda y no activa FACTOR-X; el estado de lesión de la API (`Missing Fixture`) es nivel 4; la sanción calculada de la base (`f1/{id}.sancionados`) es nivel 1.
- **El porcentaje no se compara entre bases distintas (v1.7).** Con otra liga u otra categoría, o con R-KT.2 / T.54 en un lado, la brecha es «empate técnico de formación».
- **Contradicciones se declaran, no se resuelven en silencio.** Si dos fuentes dicen cosas distintas (típico: quién dirige al equipo según el acta oficial vs la prensa), van las dos y se marca la contradicción.
- **No sobreescribas filas ya declaradas** en ningún registro. Los datos de reconciliación van en columnas nuevas.

## Cuando no hay XI confirmado

Pasa casi siempre en Liga 1 Perú, donde ningún medio publica el once la noche anterior. Protocolo:

1. Buscá el **XI real más reciente** de cada equipo, el de la última fecha jugada, no la plantilla. Cargalo etiquetado como `XI-REFERENCIA (fecha X)`.
2. Armá la tabla F1 de 14 a 16 jugadores con posición, zona, rol (🔴🟠🟡⚪) y apariciones. Dejá **vacías** las columnas Estado y Motivo.
3. Cargá lo que sí es público sin depender del XI: lesiones de largo plazo, suspensiones por tarjetas, convocatorias a selección.
4. Precalculá el Impacto Ponderado y la reducción por zona en dos ramas — rama A con todos los disponibles conocidos, rama B con el 🔴 más pesado de cada equipo ausente — aplicando el multiplicador ×1.5 de F2c si el ausente es el arquero titular fijo.
5. Marcá arriba del entregable: `⚠️ XI NO CONFIRMADO — Bloque F congelado`.
6. **Con eliminatoria a ≤ 5 días o 3.er partido en 8 días (v1.7)**, abrí además la rama «once alternativo» en la caja de sensibilidad y declará el porcentaje «condicionado al once oficial». Con el once oficial y ≥ 3 titulares fijos rotados, recomputá B y F antes de cargar. *(v1.9)* En una copa con liga a ≤ 5 días la rama va para **los dos equipos**, con el sistema y el banco que vuelve; con T.54 de ≤ 2 partidos el XI de referencia es nivel C y B6 y F van condicionados al once oficial aunque no haya calendario exigente.

## Relación con los otros módulos

- `efe-dashboard` toma el resultado de este skill y lo renderiza como JSX comparativo. Este skill puntúa, el otro dibuja.
- El diagnóstico EFE es insumo del `diagnostico-tactico` y del `teorema-del-echado`. Las alertas emitidas acá se arrastran hacia adelante en el pipeline.
- El Bloque H (matchup táctico) es la bisagra: lo que sale ahí condiciona la lectura táctica del partido.

## Archivo de referencia

| Archivo | Qué contiene | Cuándo leerlo |
|---|---|---|
| `references/rubrica-efe-v1.9.md` | Rúbrica completa — bloques A a H, tablas de indicadores, reglas especiales, tabla de puntuación, alertas automáticas, casos de validación | Siempre, antes de puntuar |
