---
name: efe-clasificador
description: Rubrica completa del clasificador EFE v1.5 del sistema SAD, Estado de Formacion de Equipo, con los ocho bloques A-H, los pesos ponderados, la tabla de puntuacion, las alertas automaticas estructurales y por fecha, y el registro de casos de validacion. Activar siempre que el usuario pida un EFE de un equipo o un partido, hablar de estado de formacion, bloques A-E, sub-scores, impacto ponderado de ausencias, reduccion por zona, clasificacion FORMADO o EN FORMACION o SIN FORMACION, o cualquier alerta del sistema como T.54, T.54-B, R-KT.2, GK-DOWNGRADE, FACTOR-X, F3, G-BLOQUE o COLAPSO EN CASCADA. Activar tambien antes de correr el skill efe-dashboard, porque este skill aporta la rubrica y el otro aporta la visualizacion. Activar tambien en corridas batch del pipeline SAD donde haya que puntuar equipos pre-partido.
---

# Clasificador EFE v1.5

Este skill guarda la rúbrica operativa del EFE (Estado de Formación de Equipo), el módulo estructural del sistema SAD.

## Cómo usarlo

1. **Leé `references/rubrica-efe-v1.5.md` completo antes de puntuar nada.** Contiene los ocho bloques con sus tablas de indicadores, los fundamentos de cada regla y los casos de validación. No puntúes de memoria.
2. Investigá en la web lo que pide la sección "Instrucciones de ejecución" de la rúbrica: cuerpo técnico, historial de cambios de DT, plantel, mercado, tabla, resultados, ausencias de la fecha, fixture y sistema táctico del rival.
3. Completá los bloques en orden, justificando cada indicador con el dato encontrado y citando la fuente.
4. Aplicá los pesos, calculá el porcentaje y emití el diagnóstico con las implicaciones para el SAD.
5. Verificá **todas** las alertas automáticas, no solo las que parecen obvias.

## Reglas que no se negocian

- **Modo PRE / selección ciega.** Todo se declara antes del pitazo. Nada de puntuar con el resultado a la vista. Lo que se escriba después del partido va marcado `RETRO` y no cuenta para calibración.
- **Disciplina 35 — el Bloque F no se puntúa sin XI confirmado.** No lo rellenes con el plantel ni lo estimes. Si no hay XI confirmado, ver más abajo.
- **Sin dato es respuesta válida.** Si un indicador no tiene información, se escribe `sin dato`, se excluye del denominador cuando la rúbrica lo permite y se abre caja de sensibilidad. No se estima para rellenar.
- **Contradicciones se declaran, no se resuelven en silencio.** Si dos fuentes dicen cosas distintas (típico: quién dirige al equipo según el acta oficial vs la prensa), van las dos y se marca la contradicción.
- **No sobreescribas filas ya declaradas** en ningún registro. Los datos de reconciliación van en columnas nuevas.

## Cuando no hay XI confirmado

Pasa casi siempre en Liga 1 Perú, donde ningún medio publica el once la noche anterior. Protocolo:

1. Buscá el **XI real más reciente** de cada equipo, el de la última fecha jugada, no la plantilla. Cargalo etiquetado como `XI-REFERENCIA (fecha X)`.
2. Armá la tabla F1 de 14 a 16 jugadores con posición, zona, rol (🔴🟠🟡⚪) y apariciones. Dejá **vacías** las columnas Estado y Motivo.
3. Cargá lo que sí es público sin depender del XI: lesiones de largo plazo, suspensiones por tarjetas, convocatorias a selección.
4. Precalculá el Impacto Ponderado y la reducción por zona en dos ramas — rama A con todos los disponibles conocidos, rama B con el 🔴 más pesado de cada equipo ausente — aplicando el multiplicador ×1.5 de F2c si el ausente es el arquero titular fijo.
5. Marcá arriba del entregable: `⚠️ XI NO CONFIRMADO — Bloque F congelado`.

## Relación con los otros módulos

- `efe-dashboard` toma el resultado de este skill y lo renderiza como JSX comparativo. Este skill puntúa, el otro dibuja.
- El diagnóstico EFE es insumo del `diagnostico-tactico` y del `teorema-del-echado`. Las alertas emitidas acá se arrastran hacia adelante en el pipeline.
- El Bloque H (matchup táctico) es la bisagra: lo que sale ahí condiciona la lectura táctica del partido.

## Archivo de referencia

| Archivo | Qué contiene | Cuándo leerlo |
|---|---|---|
| `references/rubrica-efe-v1.5.md` | Rúbrica completa — bloques A a H, tablas de indicadores, reglas especiales, tabla de puntuación, alertas automáticas, casos de validación | Siempre, antes de puntuar |
