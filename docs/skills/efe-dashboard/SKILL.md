---
name: efe-dashboard
description: "Genera dashboards visuales EFE v1.6 (Estabilidad de Formacion del Equipo) pre-partido de futbol. Produce React JSX interactivo con gauges, barras de bloques A-E, caja de sensibilidad, alertas estructurales y por fecha, impacto ponderado de disponibilidad, minutos compartidos y matchup tactico. Activar cuando el usuario pida un EFE de cualquier equipo o partido, dashboard visual de formacion o estabilidad, comparativa pre-partido, o variantes como haceme el EFE de X vs Y, dashboard EFE, EFE visual o plantilla EFE. Activar tambien si menciona bloques A-E, la clasificacion SIN FORMACION / EN FORMACION / FORMADO, o pide evaluar estabilidad institucional, tactica o de plantel. Activar tambien para analisis tactico, escenarios de resultado, recomendaciones pre-partido, que deben hacer para ganar o empatar o perder, y matriz de escenarios."
---

# EFE Dashboard — Skill de Visualización v1.7

> **v1.7 · 30.08.2026 — Post-caso CD Moquegua 1-4 Alianza Atlético (F7 Clausura Perú).** Dos alertas nuevas: **`COLAPSO POR VENTAJA PERDIDA`** (la secuencia inversa a la del colapso en cascada, que el sistema no contemplaba) y **`BLOQUE NO PROBADO`** (baja del checklist de `diagnostico-tactico` v1.2). Ninguna toca pesos ni indicadores del clasificador: son alertas de contexto. **El prompt del proyecto sigue siendo la fuente de verdad y hay que actualizarlo a mano** — ver la nota al pie de este archivo.

## Qué hace
Dashboard React (JSX) interactivo y comparativo pre-partido aplicando **EFE v1.6**. Opcionalmente genera **Matriz de Escenarios Tácticos v2.0** (Visualizer inline) cruzando EFE con recomendaciones tácticas calibradas con casos a favor/en contra y controles anti-sesgo.

## Fuente de verdad: el prompt del proyecto

> ⚠️ **REGLA CRÍTICA — siempre vigente:**
> El protocolo EFE completo (indicadores, pesos, máximos, alertas, fórmulas, protocolos de entrada, caja de sensibilidad y casos de validación) vive en **`/mnt/project/EFE_v1_6_prompt.md`** o el archivo equivalente del proyecto activo (`EFE_v1_X_prompt.md`).
>
> **ANTES de generar cualquier dashboard, hacer `view` sobre ese archivo.** Si una versión más alta está disponible (v1.7, v1.8, etc.), usar esa. Este SKILL.md es la guía de **renderizado y orquestación** — NO la fuente del protocolo. Si hay conflicto entre este SKILL.md y el prompt del proyecto, gana el prompt.

---

## Flujo de trabajo

### PASO 0 — Cargar fuente de verdad
1. `view /mnt/project/EFE_v1_X_prompt.md` (versión más alta disponible)
2. Verificar versión activa, leer changelog y reglas especiales
3. Anotar cualquier indicador nuevo o regla añadida desde la última ejecución

### PASO 0-bis — PROTOCOLOS DE ENTRADA *(NUEVO v1.6, obligatorio)*

**Antes de puntuar el primer indicador**, ejecutar los dos protocolos del prompt del proyecto y escribir sus resultados donde el usuario los vea:

**Disciplina de Categoría** — cuatro preguntas por equipo:
1. ¿Cambió de categoría en el último año? → `R-KT.2` + `E-CUARENTENA`
2. ¿Los últimos 5-6 partidos son amistosos? → `FECHA-1`
3. ¿Hay cambio de formato entre la ventana del dato y el partido? → declarar, bajar confianza un nivel
4. ¿Hay diferencial de altitud ≥2.000 m o viaje intercontinental? → declarar, extra-modelo

**Protocolo FECHA-1** — si el equipo no jugó ningún partido oficial del torneo analizado:
- E2, E3 con proxy declarado o `sin dato`; E4 en `n/a`
- F4 con nivel de dato C (la referencia son amistosos)
- **Caja de sensibilidad obligatoria**

> **Por qué está antes de la investigación y no después.** El caso Hull–United mostró que estos huecos no se detectan al puntuar: se detectan al ir a escribir el número, cuando ya se armó la narrativa alrededor. Hay que preguntarlos primero.

### PASO 1 — Recopilar datos (web search, NO inventar)

**Por equipo:**
1. **Bloque A** — DT actual: nombre, **fecha de asunción efectiva** (no la de confirmación si fue interino), cambios de DT en 12 meses, contrato, vínculo con el proyecto
2. **Bloque B** — Plantel:
   - B1: % titulares con ≥9 meses
   - B2: salidas de titulares en el último mercado
   - B3: bloque base (6-8 fijos) intacto
   - B4: fichaje que rompa jerarquía táctica
   - B5: profundidad de banco con **impacto documentado en la temporada en curso**
   - **B6: continuidad de portería + clasificación direccional** — si el titular salió, decidir si el reemplazo es `GK-DOWNGRADE` (nivel inferior) o `GK-SIN-CATEGORÍA` (nivel igual/superior sin minutos en la liga). Criterios objetivos: monto de transferencia comparado, nivel de la liga de origen, internacionalidades, vallas invictas previas, si el club rompió récord para traerlo
3. **Bloque C** — K Constants: válidas / invalidadas / cuarentena R-KT.2 / sin datos
4. **Bloque D** — Sistema base, meses con el mismo esquema, **D3 (respuesta a adversidad)**, rol en la liga
5. **Bloque E** — PPP temporada actual, últimos 6, comparación con la anterior. **Si `E-CUARENTENA` está activo, calcular las dos versiones**
6. **Bloque F** — Convocatoria de la fecha:
   - **11 confirmado o el más reciente** (NO plantilla teórica)
   - 14-16 jugadores clave: zona, rol **por participación real**, apariciones, estado, motivo
   - F2c: multiplicador GK ×1.5 si el titular fijo está ausente
   - F4: rotación voluntaria respecto del partido anterior
   - F5: jugador emergente / Factor X
   - **F6 (v1.6): minutos compartidos** — buscar minutos oficiales acumulados de la dupla de pivotes, de la dupla central y de la línea completa. Si hay ≥2 titulares de la misma línea con 0 minutos juntos → `EJE-DEBUTANTE`
   - **Máximo goleador disponible y fuera del XI** → `GOLEADOR-AL-BANCO`
7. **Bloque G** — Próximos 4 rivales con **columna FECHA obligatoria**, etiquetas (incluida 🪤 TRAMO TRAMPA), posición
8. **Bloque H** — Matchup: sistema rival, estilo, fortaleza, vulnerabilidad, H2a/H2b/H2c. **H2c exige clasificación previa del bloque rival: improvisado (55-65') o estructural (80-90')**

**Datos del partido:** fecha, torneo, fase, estadio, hora, condición L/V.

### PASO 2 — Calcular EFE

| Bloque | Peso | Máx ponderado | Notas |
|--------|------|---------------|-------|
| A | ×1.0 | 4 pts | Interino promovido no reinicia A1/A2 |
| B (B1-B6) | ×1.5 | 9 pts | 6 indicadores |
| C | ×1.0 | 4 pts | Excluir si SIN DATOS K o R-KT.2 |
| D | ×1.0 | 4 pts | Si D3=❌ → máx 2.5/4 |
| E | ×2.0 | 6 pts | Con `E-CUARENTENA`, publicar las dos versiones |
| F, G, H | ×0 | — | Solo alertas y modificadores de confianza |

```
TOTAL = A + (B × 1.5) + C* + D + (E × 2)
Máximo CON C:            27 pts
Máximo SIN C:            23 pts
Máximo SIN C NI E:       17 pts   ← versión E-cuarentena
% = (Total / Máximo alcanzable) × 100
```

| % | Clasificación | Símbolo |
|---|---------------|---------|
| ≥70% | FORMADO | 🟢 |
| 40–69% | EN FORMACIÓN | 🟡 |
| <40% | SIN FORMACIÓN | 🔴 |

> **Solo el porcentaje es comparable entre equipos con denominadores distintos.** Decirlo en el output.

### PASO 2-bis — CAJA DE SENSIBILIDAD *(NUEVO v1.6, obligatoria)*

Si algún indicador quedó `sin dato`, publicar el EFE en **los dos extremos**:

```
EFE_mínimo  = todos los sin dato en 0
EFE_máximo  = todos los sin dato en 1
```

- Los dos extremos en la **misma** clasificación → el hueco es cosmético, decirlo y seguir.
- Los extremos **cruzan** el 40% o el 70% → **la lectura depende de un dato que no se tiene**. Decirlo en el diagnóstico narrativo, no solo en la tabla.
- **Prohibido publicar el punto medio** como si fuera una estimación.

Con `E-CUARENTENA` activo, la caja se aplica también a la elección de denominador: publicar el % sobre 23 y sobre 17.

### PASO 3 — Generar el dashboard JSX

**No hay template en disco. Construir desde cero cada vez.**

#### 3.1 Estructura mínima
- **Header:** indicador SAD live, "EQUIPO A vs EQUIPO B", torneo · fase · estadio · fecha · hora
- **Banda de protocolos** *(v1.6)*: si `R-KT.2`, `E-CUARENTENA`, `FECHA-1` o cualquier `sin dato` están activos, una banda visible arriba del panel de scores que lo diga antes de que el lector vea los porcentajes
- **Panel central de scores:** dos `GaugeRing` SVG con %, clasificación y banderín. **Si hay caja de sensibilidad, el gauge muestra el rango**, no un punto
- **Tabs:**
  1. **Bloques EFE** — `BlockCard` por bloque expandible con ✅/🔶/❌, peso y barra. Bloques excluidos con patrón diagonal
  2. **Disponibilidad** — barras de reducción por zona con semáforo, badge de IP, leyenda de roles, lista de no disponibles, **y caja de F6 con los minutos compartidos por línea**
  3. **Matchup H** — perfil táctico de cada equipo, H2a/H2b/H2c con semáforo, **clasificación explícita del bloque rival (improvisado/estructural)**, diagnóstico
  4. **Lectura SAD** — 4 insight boxes + Paradoja del Partido + alertas activas con códigos
  5. **Calendario** — tabla por equipo con **columna FECHA**, etiquetas, posición, notas + diagnóstico calendárico
- **Caja de sensibilidad** como componente propio si aplica
- **Caja F4** y **caja DT** por equipo
- **Footer:** fecha de generación + versión EFE activa + modo (`PRE` / `RETRO`) y selección si corresponde

#### 3.2 Diseño
- **Tema claro**, fondo blanco. Texto `#1a1a2e` / `#37474F` / `#78909C`; cards `#F8F9FA`; barras `#ECEFF1`; bordes `#DEE2E6`
- **Color por equipo** según identidad real del club, con `colorLight` y `colorMid`. Si no hay color obvio, `#37474F`
- **Tipografía:** display/datos `JetBrains Mono`, body `DM Sans`, de Google Fonts
- **Bloques excluidos:** hatching diagonal + "N/A"
- **Interactividad:** expandir/colapsar por bloque, tabs, gauges animados

#### 3.3 Reglas técnicas
- Archivo único `.jsx` en `/mnt/user-data/outputs/efe_dashboard.jsx`
- `export default`, sin props requeridos
- Solo Tailwind core utility classes, o `<style>`/estilos inline
- Validar con `@babel/parser` (`sourceType:"module"`, `plugins:["jsx"]`) antes de presentar

### PASO 4 — Alertas SAD

| Código | Tipo | Condición |
|--------|------|-----------|
| T.54 | Estructural | DT <6 meses sin herencia |
| T.54-B | Estructural | DT <6 meses CON herencia de ciclo exitoso |
| **T.54-E** *(v1.6)* | Estructural | Interino promovido a permanente |
| T.6 v4.2 | Estructural | Fichaje con calidad muy superior |
| R-KT.2 | Estructural | Cambio de categoría → activa E-CUARENTENA |
| **E-CUARENTENA** *(v1.6)* | Estructural | R-KT.2 activo: publicar las dos versiones del % |
| K-INV | Estructural | K invalidadas por caos de DT |
| Formación fraccionada | Estructural | Score 🔴 con K individual aislada |
| GK-DOWNGRADE | Estructural | GK reemplazado por **nivel inferior** |
| **GK-SIN-CATEGORÍA** *(v1.6)* | Estructural | GK reemplazado por nivel igual/superior sin minutos en la liga |
| CRISIS-EX | Estructural | Crisis extra-cancha |
| F3 / F3-COND | Por fecha | IP > 7 o ≥2 titulares fijos ausentes |
| FACTOR-X | Por fecha | Jugador emergente fuera de las K |
| **EJE-DEBUTANTE** *(v1.6)* | Por fecha | ≥2 titulares de la misma línea con 0 minutos compartidos |
| **GOLEADOR-AL-BANCO** *(v1.6)* | Por fecha | Máximo goleador disponible y fuera del XI |
| G-CLÁSICO | Por fecha | Clásico/derby en próximas 4 fechas |
| G-ASCENDIDO | Por fecha | Rival recién ascendido |
| G-SORPRESA | Por fecha | Rival sobre expectativa |
| G-BLOQUE | Por fecha | Rival con bloque bajo **improvisado** vs equipo superior |
| **🪤 TRAMO TRAMPA** *(v1.6)* | Por fecha | Dos o más rivales seguidos de expectativa muy inferior |
| COLAPSO EN CASCADA | Por fecha | D3 ❌ vs rival con D3 ✅/🔶 |
| **💔 COLAPSO POR VENTAJA PERDIDA** *(v1.7)* | Por fecha | No sostuvo ventajas de un gol esta temporada + rival con banco de impacto documentado |
| **🧱 BLOQUE NO PROBADO** *(v1.7)* | Por fecha | Bloque estructural cuyas vallas invictas salieron todas de partidos sin presión real |

### PASO 5 — Lectura integrada
1. **Módulo Operativo:** ¿qué módulo SAD es usable y con qué confianza?
2. **1X2:** confianza y rango. Si FACTOR-X, EJE-DEBUTANTE o GOLEADOR-AL-BANCO están activos → **ampliar el rango, no mover el centro**
3. **Contexto Emocional:** presión, hinchada, Anticulebra, Fe Perdida
4. **Dato Estructural:** el dato más duro y confiable

Más la **Paradoja del Partido** si hay contradicción entre tabla y contexto.

### PASO 6 — Matriz de Escenarios Tácticos v2.0

Después del dashboard, **solo si el usuario lo pide**, generar con `visualize:show_widget`.

**Estructura: 3 escenarios × 2 equipos**

| Escenario | Filas obligatorias |
|-----------|-------------------|
| **Para ganar** | Táctica central, Pelota parada, Gestión del reloj, Base científica, Probabilidad estimada |
| **Para empatar** | Táctica central, Condiciones de campo, Dato estadístico, Probabilidad estimada |
| **Para perder** | Gatillo principal, Error sistémico, Factor psicológico, Riesgo de goleada, Probabilidad estimada |

**Principios v2.0 (anti-sesgo):**
1. Cruzar EFE (D3, B5, B6, F2, **F6**, Bloque H) con tácticas concretas
2. Consultar **Ficha de Mecanismo** completa (definición + cuándo funciona + **cuándo FALLA**) antes de aplicarlo
3. Citar evidencia real (Mohr 2003, Bradley 2009, Baumeister 1998, Lago-Peñas 2014, Seligman, Filho 2021)
4. Recorrer el **checklist de 9 puntos** pre-generación
5. En la síntesis, citar un caso que CONFIRMA y uno que CONTRADICE
6. Usar CSS variables del Visualizer, sin colores hardcoded

**Sesgos conocidos que la v2.0 corrige:**

| Sesgo | v1.0 hacía | v2.0 hace |
|-------|------------|-----------|
| Goleada | Calibrada con 7-1, 8-2, 5-0 | Probabilidad base 8-15% |
| Liga | Pensada para 38 partidos | En copa y en fecha 1, bajar confianza un nivel |
| Anti-defensa | Bloque bajo = frágil siempre | Distinguir improvisado (55-65') de estructural (80-90') |
| Pro-DT estable | Cambio de DT = negativo siempre | T.54 puede invertirse si el DT anterior subrendía |
| D3 estático | Etiqueta fija | Distribución probabilística que oscila |

**Disciplina 33 en la matriz** *(v1.6)*: publicar **simultáneamente** el mercado, la salida del motor de Regresión al Nivel y la matriz manual. Si el motor no está disponible, declararlo `sin dato` — **nunca estimarlo**. Las contradicciones se documentan, no se resuelven en silencio eligiendo un lado.

### PASO 7 — Output
1. `create_file` → `/mnt/user-data/outputs/efe_dashboard.jsx`
2. `present_files` con el path
3. Resumen breve (3-5 líneas): scores **con su rango si hay caja**, alertas activas, matchup
4. Si la matriz fue solicitada → `visualize:show_widget`
5. **Cerrar con la pregunta de coordinación:** *"¿Vamos con la Matriz de Escenarios o con el timeline (skill `futbol-timeline`)?"*

---

## Coordinación con `futbol-timeline`

Complementarios pero independientes.

### Cuándo aporta
- El usuario quiere la **historia reciente** antes o después del análisis estructural
- Hay alertas como **CRISIS-EX**, **GK-DOWNGRADE**, **GK-SIN-CATEGORÍA**, **T.54**, **T.54-E** o **COLAPSO EN CASCADA** donde la cronología contextualiza el "por qué"
- El usuario pregunta "qué viene pasando con [equipo]"

### Período por defecto
- **Recién ascendido (R-KT.2):** 12-14 meses, incluyendo el final de la temporada de ascenso
- **Crisis / GK-DOWNGRADE / CRISIS-EX:** 3-4 meses
- **DT nuevo (T.54 / T.54-B / T.54-E):** desde la **asunción efectiva**, no desde la confirmación
- **Default:** últimos 6 meses

### Datos que el flujo EFE pasa al timeline
Nombres exactos, colores primarios ya asignados, hitos detectados (cambios de DT, fichajes, salidas, sanciones, venta del portero titular) y el período sugerido. **No repetir búsquedas.**

---

## Notas finales

- El EFE es un **módulo auxiliar**: mide qué tan confiable es la señal K, **no predice resultado**
- 🔴 SIN FORMACIÓN ≠ va a perder. 🟢 FORMADO ≠ va a ganar
- En copa, un 🔴 puede llegar a semifinales — bajar confianza un nivel adicional
- La versión activa del prompt manda
- **Anti-hindsight:** todo análisis se hace pre-partido. Si el resultado ya se conoce, marcar el caso `RETRO` con su tipo de selección (`por_resultado` / `ciega` / `post_resultado`) y declarar que **no acredita**

## Errores comunes a evitar
- ❌ Usar plantilla teórica en lugar del 11 más reciente confirmado
- ❌ Puntuar el Rol de un jugador por monto de fichaje o reputación en vez de participación real
- ❌ Puntuar el Bloque E de un ascendido con datos de la categoría anterior sin declararlo
- ❌ Emitir un porcentaje único cuando hay indicadores `sin dato`
- ❌ Publicar el punto medio de la caja de sensibilidad como estimación
- ❌ Emitir GK-DOWNGRADE sin clasificar la **dirección** del cambio
- ❌ Emitir G-BLOQUE sin clasificar antes si el bloque es improvisado o estructural
- ❌ Olvidar F6 y dar el IP en verde con un eje que nunca jugó junto
- ❌ Tabla de calendario sin columna FECHA por rival
- ❌ Generar la matriz táctica sin que se haya pedido
- ❌ Asumir que este SKILL.md manda sobre el prompt del proyecto

### Alertas de v1.7 — detalle

> 💔 **COLAPSO POR VENTAJA PERDIDA.** La alerta de colapso en cascada describe la caída **después de recibir el primer gol**. Existe la secuencia contraria y es peor: el equipo **se pone en ventaja** y se desarma cuando se la empatan, porque al golpe táctico se le suma el emocional de haber tenido el partido en la mano. Se activa con dos condiciones simultáneas: el equipo no sostuvo ninguna ventaja de un gol en la temporada en curso, y el rival tiene **dos o más suplentes con impacto documentado** desde el banco. Predice diferencia amplia en contra a partir del momento en que la ventaja se pierde, no a partir del primer gol recibido.
>
> **Caso de referencia.** CD Moquegua, F7 Clausura Perú 2026: se puso 1-0 al minuto 20 y estaba 1-1 al 24. Terminó 1-4, con los goles tercero y cuarto marcados por dos suplentes que entraron al 59 y al 76. Su indicador de cierres previos estaba correctamente puntuado en el peor nivel y ninguna alerta del sistema lo recogía.

> 🧱 **BLOQUE NO PROBADO.** Baja del skill `diagnostico-tactico` v1.2, donde vive la sexta pregunta del checklist de clasificación. Si el bloque da estructural en las cinco preguntas de insumo pero **nunca sostuvo un resultado contra un rival obligado a atacar**, la vida útil de 80-90 minutos se mantiene y la alerta de degradación **no** se suprime. Un bloque que solo aguantó contra rivales sin urgencia no demostró que aguanta.

## Candidatos declarados y NO aplicados

> Se ejecutan igual en cada EFE y se reportan como **candidatos**, nunca como alertas oficiales.

- **`H2a DOMINANTE`:** que H2a 🟢 dispare MATCHUP FAVORABLE por sí solo cuando el mecanismo identificado es de balón parado. **No entra:** salió de un caso contaminado y está ajustado al resultado.
- **`D3-DEGRADADO`:** tratar como ❌ un D3 🔶 sostenido sobre menos de 8 partidos y medido en otro contexto. Viene del módulo del tramo final. Revisión con casos ciegos.
- **`ANTICULEBRA-INVERTIDA`:** el favorito que se relaja en un TRAMO TRAMPA. Hoy vive como contexto declarado en la etiqueta 🪤, sin coeficiente.
- **Asimetría de relevancia del partido:** un módulo propio que mida cuánto vale el partido para cada equipo por separado. Hoy está repartido entre P3, P1b y la etiqueta de calendario.

## Movido a otro skill en v1.6

- **`MECANISMO-ABIERTO`** (≥2 goles recibidos con mecanismo idéntico y línea que repite intérpretes) pasa al skill **`diagnostico-tactico`**, módulos M4 y M5. Es una observación de la capa de juego, no del clasificador estructural.

---

## Nota de actualización manual — el prompt del proyecto *(v1.7)*

Este skill **no manda** sobre `/mnt/project/EFE_v1_5_prompt.md`, que es la fuente de verdad y es de solo lectura desde el contenedor. Las dos alertas de v1.7 tienen que copiarse a mano a la tabla de alertas del prompt. El texto listo para pegar está en `assets/PARCHE_PROMPT_PROYECTO.md` de este mismo skill.
