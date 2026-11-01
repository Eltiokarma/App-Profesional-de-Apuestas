---
name: efe-dashboard
description: "Genera dashboards visuales EFE v1.9 (skill v1.12) (Estabilidad de Formacion del Equipo) pre-partido de futbol. Produce React JSX interactivo con gauges, barras de bloques A-E, caja de sensibilidad, alertas estructurales y por fecha, impacto ponderado de disponibilidad, minutos compartidos y matchup tactico. Activar cuando el usuario pida un EFE de cualquier equipo o partido, dashboard visual de formacion o estabilidad, comparativa pre-partido, o variantes como haceme el EFE de X vs Y, dashboard EFE, EFE visual o plantilla EFE. Activar tambien si menciona bloques A-E, la clasificacion SIN FORMACION / EN FORMACION / FORMADO, o pide evaluar estabilidad institucional, tactica o de plantel. Activar tambien para analisis tactico, escenarios de resultado, recomendaciones pre-partido, que deben hacer para ganar o empatar o perder, y matriz de escenarios."
---

# EFE Dashboard — Skill de Visualización v1.12

> **v1.12 · 01.11.2026 — Alineado con el clasificador EFE v1.9.** Ningún peso, indicador ni alerta del clasificador tocado; tampoco números en la banda de goleada (se calibra con más casos). Propuesta: `docs/revisiones/EFE_v1.9_propuesta.md`.
>
> **1. Un récord de racha no baja la banda de goleada.** `FAMILIA-RECORD` y `K-EXTREMO` son prudencia con la carga, no probabilidad (REVENTON §10 y §15.2): en su récord la burbuja no da probabilidad de corte (Delfín: la banda baja de goleada se apoyó en una racha récord de 13 visitas sin perder por 2+, y FAMILIA-RECORD ya lo avisaba).
>
> **2. La goleada se nombra como rama en «Para perder»** cuando el gatillo es un gol temprano del rival y el inferior queda obligado a perseguir, no solo como banda base (Konyaspor: la banda base de 8-15 % se escribió y la goleada llegó por el gatillo declarado, gol temprano que obliga a abrirse, cumplido antes del 30').
>
> **3. Lo que baja de la v1.9 al dibujo.** La caja de sensibilidad dibuja la zona **«degradada, cubierta de oficio»** (rango más ancho, mismo centro), **el arco del día** (la zona GK sobre el arquero que ataja hoy; con dos que se alternan, la ausencia del que no ataja no la reduce) y **la rama del once alternativo de los dos lados, con el sistema y el banco que vuelve**. El F6 muestra `EJE-DEBUTANTE` con su **origen** (`calculado` / `declarado`) y, sin once oficial, como condicional («si repiten X–Y»). Hoy la app calcula las parejas nuevas sobre el XI de referencia (`parejasNuevas` de los insumos del DTP); sobre el once oficial está **pendiente de la app**: hasta entonces, `calculado` vale solo para el XI de referencia y con el once oficial el eje es `declarado`.
>
> **v1.11 · 28.10.2026 — Alineado con el clasificador EFE v1.8.** La caja de sensibilidad baja al matchup: un supuesto con declaración pública del DT se dibuja como **rama** del H («si juega con línea de cinco…»), y una zona que la sensibilidad da como crítica (DEF o GK) baja la confianza un escalón antes de la matriz. T.54 se muestra en los dos lados con la fecha del DT; el arco «sin dueño» abre los tres escenarios en la caja. Lo demás de la v1.8 se puntúa en el clasificador.
>
> **v1.10 · 25.10.2026 — Alineado con el clasificador EFE v1.7.** `EJE-DEBUTANTE` pasa a la rúbrica del clasificador con el umbral **≤ 1 partido juntos como titulares** (antes 0 minutos) y las posiciones de la línea se leen del grid del once; el F6 de acá cita esa regla. Lo demás de la v1.7 (F3 por zona, recambio de oficio o reconvertido, jerarquía de fuentes, D3 con contexto, rama «once alternativo», brecha solo en la misma base) se puntúa en el clasificador y se dibuja como hasta ahora: la caja de sensibilidad lleva la rama alternativa y la alerta F3 nombra la zona.

> **v1.9 · 21.10.2026 — Limpieza de lo que no existe y reparto con `sad-analysis` v4.0.** Ningún peso, indicador ni alerta del clasificador tocado.
>
> **1. La lectura integrada (paso 5) pasa a `sad-analysis` v4.0**, que es el skill de la síntesis (pronóstico y lectura de las K). Este skill la muestra en el dashboard; la define y la escribe aquel.
>
> **2. Sale el «Contexto emocional: Anticulebra, Fe Perdida».** Los dos eran motores del sistema anterior que no existen en la app SAD: la Ley 5 (Tensión del Favorito) quedó suspendida por el backtest del 19.10.2026 (63.475 partidos, sin culebra) y la Fe Perdida no tiene péndulo que la calcule. En la cohorte c3 dos partes los invocaron sin dato (Boca–São Paulo, derbi de Montevideo). Queda un **contexto con fuente**: presión de tabla, hinchada, clima del club, citados.
>
> **3. `ANTICULEBRA-INVERTIDA` se renombra `FAVORITO-RELAJADO`.** El contexto del candidato se queda; el nombre de un motor suspendido, no.
>
> **4. Se quitan el «checklist de 9 puntos» y la «Ficha de Mecanismo»** del paso 6: no existen en disco y nadie podía recorrerlos. Quedan los principios que sí están escritos.
>
> **5. La matriz se compara con el 1X2 del motor calculado** (`unXDos` de `/predicciones`, logística calibrada sobre 51.254 partidos), nunca con un Poisson armado con μ: μ son puntos esperados, no goles.

> **v1.8 · 13.09.2026 — Post-caso Alianza Lima 1-2 Universitario (F9 Clausura Perú).** Tres altas y ninguna toca pesos ni indicadores del clasificador.
>
> **1. `F5` mira la nómina completa, no el once probable.** El texto del protocolo siempre dijo *revisar la convocatoria*, y la aplicación lo redujo al once. Resultado del caso: los dos `FACTOR-X` declarados **no fueron titulares** en ninguno de los dos equipos, y el jugador que decidió el partido estaba en la tabla de plantilla del propio dashboard marcado como rotación, sin casillero de factor. **Un suplente con impacto documentado desde el banco en la temporada en curso es factor X por derecho propio**, se proyecte titular o no. El mecanismo vive en el banco: en el fútbol de cinco cambios, el que entra al 70 contra defensas fatigadas es exactamente el perfil que las K no capturan. Es alinear la aplicación con lo que la regla ya pedía, no una regla nueva.
>
> **2. El once probable es nivel de dato C, no B, por muchas fuentes que converjan.** Cuatro medios peruanos publicaron la misma alineación del local y jugó un titular que ninguno había nombrado. **Cuatro fuentes que coinciden no son cuatro observaciones: son una previa copiada cuatro veces.** Consecuencia: cuando el dashboard se genera antes de la publicación del once oficial —alrededor de sesenta minutos antes del inicio—, la banda de protocolos declara la **ventana de confirmación pendiente** y ofrece el recomputo, en lugar de presentar el once probable como si fuera la lista. Los indicadores que se apoyan en el once (`B1`, `B5`, todo el Bloque F) heredan ese nivel.
>
> **3. Candidato declarado y NO aplicado — `GK-FALLA-ACTIVA`.** `B6` mide **continuidad de portería y recorrido en la categoría**, y en este caso puntuó ✅ con toda la razón: arquero titular indiscutido con ocho temporadas en la liga. Lo que `B6` no mira —ni tiene por qué mirar— es si ese arquero **está fallando ahora**. El del caso acumulaba dos errores con gol documentados en el torneo en curso, el mecanismo se declaró por escrito dos veces antes del partido, y el gol que lo decidió al 90+7 fue exactamente eso. **Propuesta: alerta paralela, no modificación de `B6`**, que se activa con ≥2 errores con gol documentados en el torneo en curso del arquero titular habitual, y que entra como agravante declarado y **sin coeficiente**. No entra con un caso, y tiene un riesgo de calibración propio: "error con gol" es una categoría que el periodismo asigna con generosidad, así que el indicador podría terminar midiendo cobertura en lugar de rendimiento. Revisión con ≥3 casos y la definición fijada antes de contarlos. La versión operativa vive en `teorema-del-echado/references/INDICE_IE.md`.
>
> **Lo que el clasificador acertó y conviene no borrar.** El diagnóstico de equivalencia estructural (68,5% contra 65,7%, los dos en formación) describió bien un partido que se decidió en el añadido. La caja de sensibilidad hizo su trabajo: se declaró que la clasificación del local dependía de `B1` y se publicaron los dos extremos en vez de un punto medio. `D3 = ✅` en los dos se confirmó —el local remontó por cuarta vez en la temporada— y `COLAPSO EN CASCADA` se descartó con razón. `B5 = ✅` del visitante se materializó en la jugada del gol decisivo, con el suplente fresco definiendo.

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
   - **F6 (v1.6, umbral v1.10): minutos compartidos** — buscar los partidos que arrancaron juntos la dupla de pivotes, la dupla central y la línea completa (posiciones del grid del once). Si hay ≥2 titulares de la misma línea con **≤ 1 partido juntos como titulares** → `EJE-DEBUTANTE` (regla del clasificador EFE v1.7). *(v1.12)* Sin once oficial va condicional («si repiten X–Y»); con el once se rehace sobre el grid y se marca su origen: `calculado` (de `parejasNuevas` de la app, hoy solo sobre el XI de referencia) o `declarado`
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
- **Caja de sensibilidad** como componente propio si aplica. *(v1.12)* Dibuja, cuando estén: la zona «degradada, cubierta de oficio» (rango, no centro), el arco del día y la rama del once alternativo de los dos lados con el sistema y el banco que vuelve
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
| **EJE-DEBUTANTE** *(v1.6, umbral v1.10)* | Por fecha | ≥2 titulares de la misma línea con ≤ 1 partido juntos como titulares |
| **GOLEADOR-AL-BANCO** *(v1.6)* | Por fecha | Máximo goleador disponible y fuera del XI |
| G-CLÁSICO | Por fecha | Clásico/derby en próximas 4 fechas |
| G-ASCENDIDO | Por fecha | Rival recién ascendido |
| G-SORPRESA | Por fecha | Rival sobre expectativa |
| G-BLOQUE | Por fecha | Rival con bloque bajo **improvisado** vs equipo superior |
| **🪤 TRAMO TRAMPA** *(v1.6)* | Por fecha | Dos o más rivales seguidos de expectativa muy inferior |
| COLAPSO EN CASCADA | Por fecha | D3 ❌ vs rival con D3 ✅/🔶 |
| **💔 COLAPSO POR VENTAJA PERDIDA** *(v1.7)* | Por fecha | No sostuvo ventajas de un gol esta temporada + rival con banco de impacto documentado |
| **🧱 BLOQUE NO PROBADO** *(v1.7)* | Por fecha | Bloque estructural cuyas vallas invictas salieron todas de partidos sin presión real |

### PASO 5 — Lectura integrada *(la define `sad-analysis` v4.0)*

Desde v1.9 la lectura integrada es del skill **`sad-analysis` v4.0** (paso 6, síntesis): módulo operativo, 1X2 con sus tres fuentes, contexto, dato estructural y paradoja. El dashboard la **muestra** con lo que aporta el EFE:

1. **1X2:** si FACTOR-X, EJE-DEBUTANTE o GOLEADOR-AL-BANCO están activos → **ampliar el rango, no mover el centro** (regla del EFE, sigue aquí).
2. **Contexto:** presión de tabla, hinchada, clima del club — **con fuente citada**. No hay «módulos emocionales»: la Fe Perdida y la Tensión del Favorito no existen en la app *(v1.9)*.
3. **Dato Estructural:** el dato más duro y confiable del EFE.

Más la **Paradoja del Partido** si hay contradicción entre tabla y contexto.

### PASO 6 — Matriz de Escenarios Tácticos v2.0

Después del dashboard, **solo si el usuario lo pide**, generar con `visualize:show_widget`.

**Estructura: 3 escenarios × 2 equipos**

| Escenario | Filas obligatorias |
|-----------|-------------------|
| **Para ganar** | Táctica central, Pelota parada, Gestión del reloj, Base científica, Probabilidad estimada |
| **Para empatar** | Táctica central, Condiciones de campo, Dato estadístico, Probabilidad estimada |
| **Para perder** | Gatillo principal, Error sistémico, Factor psicológico, Riesgo de goleada, Probabilidad estimada |

*(v1.12)* **Riesgo de goleada:** con un gol temprano del rival como gatillo y el inferior obligado a perseguir, la goleada se nombra como **rama** («si recibe antes del 30' y se abre…»), no solo como banda base. Un récord de racha (`FAMILIA-RECORD`, `K-EXTREMO`) **no es argumento para bajar la banda**: es prudencia con la carga, no probabilidad.

**Principios v2.0 (anti-sesgo):**
1. Cruzar EFE (D3, B5, B6, F2, **F6**, Bloque H) con tácticas concretas
2. Antes de aplicar un mecanismo, escribir cuándo funciona y **cuándo FALLA** *(v1.9: la «Ficha de Mecanismo» que se citaba aquí no existe; la regla queda escrita en su lugar)*
3. Citar evidencia real (Mohr 2003, Bradley 2009, Baumeister 1998, Lago-Peñas 2014, Seligman, Filho 2021)
4. En la síntesis, citar un caso que CONFIRMA y uno que CONTRADICE
5. Usar CSS variables del Visualizer, sin colores hardcoded

*(v1.9: se quitó el «checklist de 9 puntos», que no existe en disco.)*

**Sesgos conocidos que la v2.0 corrige:**

| Sesgo | v1.0 hacía | v2.0 hace |
|-------|------------|-----------|
| Goleada | Calibrada con 7-1, 8-2, 5-0 | Probabilidad base 8-15% |
| Liga | Pensada para 38 partidos | En copa y en fecha 1, bajar confianza un nivel |
| Anti-defensa | Bloque bajo = frágil siempre | Distinguir improvisado (55-65') de estructural (80-90') |
| Pro-DT estable | Cambio de DT = negativo siempre | T.54 puede invertirse si el DT anterior subrendía |
| D3 estático | Etiqueta fija | Distribución probabilística que oscila |

**Disciplina 33 en la matriz** *(v1.6)*: publicar **simultáneamente** el mercado, la salida del motor de Regresión al Nivel y la matriz manual. La salida del motor en 1X2 es `unXDos` de `/predicciones/{id}` *(v1.9)*, copiada tal cual; **nunca un Poisson con μ como λ** (μ son puntos, no goles). Si el motor no está disponible, declararlo `sin dato` — **nunca estimarlo**. Las contradicciones se documentan, no se resuelven en silencio eligiendo un lado.

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
- ❌ Bajar la banda de goleada porque el equipo está en su récord de racha *(v1.12)*
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
- **`FAVORITO-RELAJADO`** *(antes `ANTICULEBRA-INVERTIDA`, renombrado en v1.9)*: el favorito que se relaja en un TRAMO TRAMPA. Hoy vive como contexto declarado en la etiqueta 🪤, sin coeficiente.
- **Asimetría de relevancia del partido:** un módulo propio que mida cuánto vale el partido para cada equipo por separado. Hoy está repartido entre P3, P1b y la etiqueta de calendario.

## Movido a otro skill en v1.6

- **`MECANISMO-ABIERTO`** (≥2 goles recibidos con mecanismo idéntico y línea que repite intérpretes) pasa al skill **`diagnostico-tactico`**, módulos M4 y M5. Es una observación de la capa de juego, no del clasificador estructural.

---

## Nota de actualización manual — el prompt del proyecto *(v1.7)*

Este skill **no manda** sobre `/mnt/project/EFE_v1_5_prompt.md`, que es la fuente de verdad y es de solo lectura desde el contenedor. Las dos alertas de v1.7 tienen que copiarse a mano a la tabla de alertas del prompt. El texto listo para pegar está en `assets/PARCHE_PROMPT_PROYECTO.md` de este mismo skill.
