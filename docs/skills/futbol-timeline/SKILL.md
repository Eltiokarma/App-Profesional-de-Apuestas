---
name: futbol-timeline
description: >
  Genera timelines interactivos HTML comparativos de equipos de fútbol. Incluye resultados de partidos,
  eventos institucionales (crisis, sanciones, cambios de DT, fichajes, ascensos/descensos), y contexto
  narrativo. Siempre usa web search para obtener datos actualizados. Activar cuando el usuario pida:
  un timeline, cronología, calendario de sucesos, línea de tiempo, historial comparativo, o resumen
  cronológico de uno o más equipos de fútbol. También activar si pide "qué ha pasado con [equipo]
  en los últimos meses", "dame la historia reciente de [equipo]", "comparame la temporada de X vs Y",
  "cronología de la crisis de [equipo]", o cualquier variante que implique ordenar eventos futbolísticos
  en el tiempo. TAMBIÉN activar como complemento del skill efe-dashboard cuando el usuario, después
  de un análisis EFE, pide ver "qué viene pasando", el contexto histórico, o la cronología de los equipos.
  Funciona para cualquier liga, cualquier equipo, cualquier período.
---

# Futbol Timeline — Skill de Cronología Comparativa

## Qué hace

Genera un archivo HTML interactivo con un timeline visual que muestra eventos cronológicos de 1 o 2 equipos de fútbol. El output es siempre un `.html` autocontenido (sin dependencias externas más allá de Google Fonts) que se guarda en `/mnt/user-data/outputs/` y se presenta al usuario.

## Coordinación con `efe-dashboard`

Este skill suele ejecutarse **después** del skill `efe-dashboard` como complemento de contexto histórico. Si detectás que venís de un flujo EFE (porque hay un dashboard recién generado en la conversación o el usuario hace referencia a "los mismos equipos del EFE"), seguir este patrón:

1. **No re-buscar lo ya investigado.** Reutilizar:
   - Nombres exactos de los equipos (idéntica grafía a la del dashboard EFE)
   - Colores primarios asignados al equipo (mantener consistencia visual con el dashboard)
   - Hitos ya detectados en el análisis EFE (cambios de DT, fichajes/salidas, sanciones, lesiones de GK, fichajes recién llegados marcados en F5)
2. **Período por defecto si no se especifica:**
   - **Recién ascendido (R-KT.2):** 12 meses (incluir final de la temporada de ascenso)
   - **Crisis reciente / GK-DOWNGRADE / CRISIS-EX:** 3-4 meses (zoom a la fase aguda)
   - **DT nuevo (T.54 o T.54-B):** desde la fecha de asunción del DT
   - **Default:** últimos 6 meses
3. **Énfasis sugerido:** Marcar los eventos institucionales relacionados con las alertas activas del EFE (ej: si GK-DOWNGRADE estaba en el dashboard, destacar la transferencia del GK como evento de tipo `institucional`).

## Flujo de trabajo

### 1. Recoger parámetros

Antes de buscar, determinar:

- **Equipos**: 1 o 2 (máximo 2 para comparativo).
- **Período**: Si el usuario lo dice, usar eso. Si viene de un flujo EFE, usar las heurísticas de arriba. Si no, default 6 meses.
- **Tipos de evento**: Por defecto incluir TODO (partidos, institucional, técnico, sanciones, hitos).

Si el usuario ya dio toda la info, no preguntar — ir directo a buscar.

### 2. Investigar con web search

Mínimo 2-3 búsquedas por equipo. Queries en español funcionan mejor para ligas sudamericanas; italiano para Serie A:

```
"[Equipo] resultados [liga] [año]"
"[Equipo] noticias crisis fichajes [año]"
"[Equipo] cronología [período]"
"[Equipo] tabla posiciones [liga] [año]"
"[Equipo] cambio técnico DT [año]"
```

Buscar hasta tener cobertura suficiente de:
- Resultados de partidos (fecha, rival, marcador, contexto breve)
- Cambios de DT (quién salió, quién llegó, por qué)
- Eventos institucionales (sanciones, crisis financieras, compras/ventas, ascensos/descensos)
- Datos de tabla de posiciones

**No inventar datos.** Si un dato no se confirma con web search, no incluirlo.

### 3. Construir la estructura de datos

Eventos en orden cronológico estricto. Cada evento:

| Campo | Descripción |
|-------|-------------|
| `fecha` | YYYY-MM-DD o "~fecha" |
| `equipo` | Nombre del equipo (o "ambos" si aplica a los dos) |
| `tipo` | `resultado` / `derrota` / `empate` / `institucional` / `tecnico` / `sancion` / `hito` |
| `titulo` | Frase corta (~60 caracteres) |
| `detalle` | Contexto en 1-2 oraciones |
| `jornada` | Número de fecha/jornada si aplica |

### 4. Generar el HTML

Leer `references/TEMPLATE.md` para la estructura HTML completa. Adaptar colores según los equipos reales.

**Reglas de diseño inviolables:**

- **Fondo oscuro** (#0a0a0f o similar). Nunca fondo blanco.
- **Un equipo a la izquierda, otro a la derecha** del timeline central. Si es 1 solo, todo a la izquierda.
- **Eventos compartidos** (enfrentamiento directo) van centrados.
- **Línea vertical central** como eje temporal.
- **Separadores de mes** con etiqueta pill.
- **Dots de color** en la línea central según equipo.
- **Colores por equipo:** usar los reales del club. Si venís de EFE, mantener los colores que se usaron en el dashboard.
- **Badges de tipo de evento** con colores semánticos:
  - Victoria: verde
  - Derrota: rojo
  - Empate: amarillo
  - Institucional: púrpura
  - Técnico (DT): azul
  - Sanción: naranja
  - Hito: cyan/turquesa
- **Filtros interactivos** arriba: "Todo", un botón por equipo, "Institucional", "Partidos".
- **Barra de stats** con datos clave (posición, puntos, última victoria, etc.).
- **Leyenda de colores** debajo de los filtros.
- **Responsive:** cards al 44% en desktop, 85% en mobile.
- **Font:** Inter de Google Fonts.
- **Sin dependencias JS externas.** Vanilla JS para filtros.

### 5. Guardar y presentar

1. Guardar en `/mnt/user-data/outputs/timeline_[equipo1]_[equipo2].html`
2. `present_files` con el path
3. Resumen de 3-4 líneas

## Adaptaciones según contexto

### Un solo equipo
- Timeline unilateral (todo a la izquierda).
- Sin filtro de equipo en los botones.
- Línea central a ~20% del ancho.

### Equipos de la misma liga que se enfrentan
- Si hay enfrentamiento directo en el período, destacarlo como evento central compartido.
- Mencionar la posición relativa en la tabla.

### Crisis institucionales largas
- Agrupar sub-eventos bajo un arco narrativo claro.
- Diferenciar fases con `institucional`, `sancion`, `hito`.

### Período muy largo (>1 año)
- Agrupar por trimestre en lugar de mes.
- Priorizar eventos de alto impacto; no incluir cada partido.

## Ejemplos de trigger

**Input:** *"Haceme un timeline comparativo de River y Boca en la Libertadores 2025"*
1. Web search por cada equipo + superclásicos del año
2. River izquierda (rojo/blanco), Boca derecha (azul/dorado)
3. Guardar y presentar

**Input:** *"Dame la cronología de la crisis de Alianza Lima este año"*
1. Web search "Alianza Lima crisis 2026", DT, resultados
2. Timeline unilateral azul/blanco
3. Guardar y presentar

**Input (post-EFE):** *"Ahora pasame el timeline"*
1. Reutilizar nombres y colores del dashboard EFE
2. Período según las alertas activas (T.54 → desde DT actual; GK-DOWNGRADE → 4 meses; default 6)
3. Marcar como hitos los eventos relacionados con las alertas
4. Guardar y presentar

## Qué NO hacer

- No inventar resultados ni fechas. Si no se confirma, omitir.
- No usar frameworks JS externos. HTML autocontenido.
- No generar PDFs. Output siempre HTML interactivo.
- No preguntar si el usuario quiere web search — siempre buscar.
- No hacer timelines de más de 2 equipos simultáneos (ilegible).
- Si venís de un flujo EFE, **no repetir** búsquedas que ya se hicieron — reutilizar lo encontrado.
