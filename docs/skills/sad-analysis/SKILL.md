---
name: sad-analysis
description: "Análisis pre-partido de fútbol con sistema SAD: constantes K, Tensión del Favorito (antes 'Anticulebra'), Regresión al Nivel, modelo de goles Poisson, Fe Perdida. Activar con CSVs de equipos, screenshot del mercado, o análisis de apuestas."
---

# SAD — Análisis Deportivo (v3.2)

## Qué hace este skill

Ejecuta el protocolo SAD completo: análisis pre-partido de fútbol basado en 9 leyes con jerarquía estricta, **constantes K como señal primaria (70% del peso)**, y auditoría automática de completitud al final.

**Cambios v3.2 respecto a v3.1:** terminología refactorizada para reducir jerga.
- *Anticulebra* → **Tensión del Favorito**
- *Electrocardiograma (ECG)* → **trayectoria histórica**
- *DC trampa* → **doble oportunidad trampa**
- *ML* (ambiguo) → **modelo de mercado** o **modelo de ML** según contexto
- *GF / GC* → **goles a favor / goles en contra**
- *Nv* → **nivel del rival**
- *H2H* → **historial directo** (primera mención)
- *§AS-1 / §AS-2* → **Auditoría 1 / Auditoría 2**
- *Ley 9 "No Nombre"* → **Ley 9 — Nivel sobre nombre**
- *burst* → **estallido** (se mantiene "burst" como sinónimo técnico aceptado)

**No cambian:** nombres de columnas en CSV (`k`, `k_local`, `k_visita`, `k_goles_anotado`, `k_goles_recibido`, `k_goles_local_anotado`, `k_goles_visita_anotado`, `k_goles_local_recibido`, `k_goles_visita_recibido`) ni los códigos legales del EFE (T.54, T.54-B, R-KT.2, T.6 v4.2).

---

## Glosario rápido

| Término | Significado operativo |
|---|---|
| **Constante K** | Indicador acumulado de presión/rendimiento del equipo, calculado por el sistema y volcado al CSV post-partido |
| **Estallido (burst)** | Salto súbito de una constante después de acumular presión — típicamente coincide con un partido decisivo |
| **Trayectoria histórica** | Serie temporal completa de la constante a lo largo de 24-48 meses (antes "ECG") |
| **Tensión del Favorito** | Mecanismo que detecta cuándo un favorito está bajo presión acumulada de no cerrar partidos esperados (antes "Anticulebra") |
| **Índice de Favoritismo (ICF)** | Score compuesto que combina constantes locales/visitantes, goles y nivel para medir cuán favorito es un equipo |
| **Doble oportunidad trampa** | Cuota de doble oportunidad (1X o 2X del favorito) por encima de 1.05 — señal de que el mercado no confía plenamente en el favorito |
| **Gap de regresión** | `μ − forma reciente`, donde μ son los puntos esperados por la regresión calibrada. **`gap > 0` = sub-rendimiento, tiende a mejorar. `gap < 0` = sobre-rendimiento, tiende a empeorar.** No es `forma − nivel` |
| **μ (mu)** | Puntos esperados: `1.241 + 0.334·nivel − 0.357·nivel_rival + 0.382·localía`. `μ_partido` usa rival y localía reales y es **el número que dice quién es favorito** |
| **Fe Perdida** | Estado emocional acumulado de la hinchada modelado como péndulo |
| **Burbuja de historial directo** | 2+ victorias seguidas vs un mismo rival que pueden quebrarse |

---

## Cuándo consultar `references/`

Los archivos en `references/` contienen documentación técnica detallada de cada motor. Consultarlos **solo bajo demanda**, cuando haya duda específica sobre:

- `references/ley_marcador.md` → fórmulas Poisson, features del modelo de goles, umbrales de sugerencia
- `references/ley_fe_perdida.md` → cálculo del péndulo, faith por estatura, tabla empírica
- `references/motor_tension_favorito.md` → fórmula ICF, features del modelo ML, sistema de tensión acumulada
- `references/ley_regresion_nivel.md` → cálculo de nivel, μ, Gap clásico y ajustado, signo, camino de recuperación, veredicto empírico, bins
- `references/casos_referencia.md` → auditorías históricas y lecciones aprendidas

**No leer `references/` al inicio del análisis.** Solo cuando aparece una duda concreta.

## Auditoría automática (obligatoria al final)

Después de completar el análisis completo, antes de entregar al usuario:

1. Ejecutar `python scripts/audit_protocol.py` pasando el texto del análisis.
2. Si hay pasos faltantes → completarlos.
3. Si hay violaciones → corregirlas.
4. Entregar solo después de que la auditoría pase.

---

## Archivos obligatorios por análisis

1. CSV del equipo local
2. CSV del equipo visitante
3. Screenshot del mercado (con cuotas y predicción del modelo)

### Orden anti-anclaje

**Procesar CSVs primero → formular hipótesis K → después abrir el screenshot.**

Si por error se vieron las cuotas antes que las constantes K, declararlo explícitamente:
> ⚠️ Alerta de anclaje: vi las cuotas antes de leer las constantes K.

---

## Jerarquía no negociable

```
PREFILTRO — Ley 4 (XI): ¿el XI que generó las K es el que va a jugar?

NIVEL 1 — FILTROS OBLIGATORIOS (en orden):
  K techo → Doble oportunidad trampa → Tensión del Favorito → Goles × Fecha × Condición

NIVEL 2 — COMPLEMENTARIAS (no revierten una K clara):
  Regresión al Nivel, Fe Perdida, Rivales Futuros, Historial directo, Modelo de goles (Poisson)

EXCEPCIONES:
  Si K calla → Regresión hereda (Gap ≥ 0.8 = peso de K techo).
  Si hay partido continental en 3-5 días → Ley 3 pasa a ser el lente primario.
```

## Las 9 leyes

| # | Ley | Paso | Prioridad |
|---|---|---|---|
| 1 | Constantes K | 1 | **Primaria (70%)** |
| 2 | Regresión al Nivel | 5 | Hereda si K calla |
| 3 | Rivales Futuros | 5 | Primaria si hay copa continental en 3-5 días |
| 3-B | Proyección de Trayectoria K | 1.5 | Cadena alimentación → inflación → cobro |
| 4 | Formación y DT | 0.5 | Prefiltro de validez de las K |
| 5 | **Tensión del Favorito** | 3 | Filtro obligatorio |
| 6 | Cuotas Invariables (doble oportunidad) | 2 | Filtro obligatorio |
| 7 | Goles × Fecha × Condición | 3.5 | Filtro obligatorio |
| 8 | Canales Opuestos | 5 | Auxiliar |
| 9 | **Nivel sobre nombre** | Transversal | Nivel > reputación siempre |

> **Fe Perdida** no es una ley independiente. Opera dentro de la Ley 2. Su veredicto es un **flag**, no un péndulo.

---

## Reglas transversales

### Fusión K (prerrequisito, siempre antes de leer)

`k = k_positivo + k_negativo`. Igual para `k_local` y `k_visita`.

Las `k_goles` **no se fusionan** (anotado y recibido son flujos independientes).

**Las 6 constantes operativas son:**

1. `k` (fusionada general)
2. `k_local` o `k_visita` (según condición del partido)
3. `k_goles_anotado` (general)
4. `k_goles_recibido` (general)
5. `k_goles_contexto_anotado` (`k_goles_local_anotado` o `k_goles_visita_anotado`)
6. `k_goles_contexto_recibido` (`k_goles_local_recibido` o `k_goles_visita_recibido`)

### CSV

- Encoding: `utf-8-sig`.
- Contexto: columna `Es_Local == 1 / 0`.
- Liga: columna `Liga` para identificar competición.
- Estallido reciente: si la constante previa estaba >5 y la actual ≤0 → hubo burst.
- Aceleración: usar `numpy.diff()` por fecha para detectar cambios de pendiente.

### Ley 9 — Nivel sobre nombre

El **nivel** determina la dinámica del partido, no la reputación ni el nombre del equipo.

**Extensión v3.1:** el nivel del rival **nunca** desactiva un gatillo K activo del equipo propio. Una K revienta porque la presión propia alcanzó su límite, no porque el rival "sea bueno" o "sea malo".

**Prohibición:** frases como *"rival débil no provoca estallido"* o *"contra este nivel no revienta"* son violaciones de la Ley 9 cuando se usan para atenuar un gatillo activo.

**Detector:** si la justificación para descartar un gatillo contiene **nombre, nivel, posición o identidad del rival** → es violación → parar y reevaluar.

### Prohibición de estadísticas descriptivas

Solo las 9 leyes generan hipótesis. Si un argumento incluye un porcentaje que no proviene de las 9 leyes ni del modelo ML → es descriptivo → solo ilustra, nunca genera hipótesis.

### Regla anti-tautología (obligatoria)

Las K en el CSV son valores **post-partido**. Cualquier correlación K → resultado debe usar `shift(1)`:

```python
# CORRECTO
df['k_prev'] = df['k_col'].shift(1)
df[df['k_prev'] < umbral]['Resultado'].value_counts()

# INCORRECTO (tautológico)
df[df['k_col'] < umbral]['Resultado'].value_counts()
```

---

## Paso 0.5 — Ley 4: filtro XI

**Ejecutar antes de leer las K.** Buscar bajas y rotaciones con `web_search` **antes** de abrir los CSVs.

Pregunta clave: *¿el XI que generó esta K es el que va a jugar?*

| Escenario | Condición | Impacto sobre las K |
|---|---|---|
| 1 — Mismo XI | Titulares intactos | K normales |
| 2 — Bajas periféricas | No-ejes ausentes | K con descuento leve |
| 3 — Bajas estructurales | Eje ausente o múltiples titulares en una misma zona | K defensivas sin validez de estallido; K de rebote congelada; K ofensiva del rival potenciada; **K techo puede seguir creciendo** |

**Principio:** toda presión acumulada (estallido, rebote, reactivación) requiere el mismo XI que la generó. Sin ese XI, la presión ni revienta ni rebota — se congela.

**Diferenciar zona afectada:**

- Rotación defensiva, ofensiva intacta → `k_goles_anotado` no se deprecia.
- Rotación ofensiva, defensa intacta → `k_goles_anotado` se deprecia.
- Rotación mixta → la zona más afectada pierde validez.

**Formato del veredicto Ley 4:**

```
LEY 4: [Equipo] → Escenario [1 / 2 / 3]
Bajas: [jugadores y zona]
Impacto K: [normales / descuento / invalidadas]
K rival beneficiadas: [cuáles]
```

---

## Paso 1 — Constantes K (70% del peso, simetría obligatoria entre ambos equipos)

### 1-A — Extracción (solo cálculo, cero interpretación)

Para **cada constante operativa** extraer con código:

1. Valor actual + techo histórico + porcentaje del techo.
2. Todos los picos anteriores (valores y fechas).
3. Si el valor es 0: partidos consecutivos en 0 + todas las sequías anteriores + qué ocurrió después.
4. Resets en `k_goles`: ¿hubo 2+ resets en el ciclo activo? Historial de patrones similares.
5. Deltas consecutivos (`numpy.diff`): aceleraciones / desaceleraciones + episodios previos similares.
6. Predicción del modelo de ML del screenshot (incrementa / decrementa).
7. Distribución de **goles a favor / goles en contra** en estado K similar: filtrar partidos donde la K contextual *pre-match* estaba en el mismo rango → distribución completa de goles.

**Reconstruir la trayectoria histórica de 24-48 meses.**

Si `k_goles_general` y `k_goles_contextual` divergen → reportar la tensión (la contextual prioriza).

### 1-B — 6 gatillos (para cada equipo, cada constante)

**Sin umbrales universales** — comparar contra el historial propio del equipo.

| # | Gatillo | Cómo evaluarlo |
|---|---|---|
| 1 | ¿Techo histórico? | Valor actual vs. dispersión de picos propios |
| 2 | ¿Presión en 0? | Sequía actual vs. previas que terminaron en brote. **Excepción de alternancia rápida:** si la trayectoria muestra 0→gol→0→gol y el modelo ML indica incremento → rebote inmediato |
| 3 | ¿Resets acumulados? | 2+ resets en el ciclo activo + historial de explosión post-reset |
| 4 | ¿Aceleración delta? | Desaceleraciones vs. episodios previos. 2+ desaceleraciones consecutivas en delta general o contextual = marcador mínimo + señal de estallido inminente |
| 5 | ¿Convergencia? | **v3.1:** 2+ señales direccionales, ya sean de distintas constantes o de distintos gatillos de la misma constante |
| 6 | ¿Combinación → marcador? | Cruzar gatillos para anticipar un marcador emergente |

**Patrón de N subidas → estallido (v3.1):** si 2+ ciclos en los últimos 24-48 meses terminaron en estallido tras el mismo número de subidas (±1), y el ciclo actual iguala ese conteo → gatillo activo.

**Estallido posterior de `k_goles_recibido` (v3.1):** si `k_goles_contexto_recibido` reventó desde >30 a 0 en el partido anterior en esa condición → verificar historial: si los goles en contra fueron consistentemente >0 en los partidos siguientes → gatillo activo de goles en contra esperados.

### 1-C — Reglas especiales

- **Modelo ML vs. gatillo:** el gatillo prioriza.
- **Predicción de constante ≠ predicción de resultado:** un modelo que marca DECR no significa "no gana".
- **Combinación favorable a estallido:** K en 0 + modelo ML indicando INCR + sequía prolongada = convergen → equipo va a anotar / ganar.
- **Interacción entre constantes:** las K de goles y las K de rendimiento están relacionadas, no son independientes.

### 1-D — Historial directo como burbuja

- Historial directo con 2+ victorias seguidas = **burbuja** que puede reventar.
- Historial directo cruzado: la deuda se cobra una sola vez; si el objetivo ya se logró → equipo vulnerable.
- Historial directo + K techo = señales que **convergen**.

### 1-F — ¿K habla o K calla?

**K calla solo si se cumplen todas:**

1. Cerca de 0 pero sin igualar sequías históricas.
2. No hay techo en `k_goles` contextual.
3. No hay resets con patrón.
4. No hay desaceleración con precedente.
5. Modelo ML dividido.
6. Trayectoria sin ciclo identificable.

**Un solo gatillo activo = K habla.**

### 1-G — Veredicto K

Derivar el marcador K del **cruce de distribuciones de goles a favor / goles en contra** en el estado K actual (no Poisson, no promedios). Si la Ley 4 marcó Escenario 3 → desplazar la distribución de goles a favor del equipo afectado hacia abajo.

```
VEREDICTO K: [Equipo] GANA / EMPATE / [Equipo] PIERDE
Marcador K: [del cruce de distribuciones]
Gatillos activos: [por equipo, con evidencia del CSV]
Confianza K: ALTA / MEDIA / BAJA
```

- **Alta o Media** → veredicto cerrado (los pasos 2-5 solo ajustan tipo/marcador).
- **Baja** → las complementarias heredan.
- **Conflicto entre ambos equipos:** el que tenga más gatillos domina. Si están iguales → empate con goles.

### 1-H — Anti-anclaje post-veredicto

¿La primera frase interpretativa ya contenía dirección? Si el veredicto coincide → sospechar → construir la hipótesis opuesta → si es más fuerte → invertir.

Verificar anti-tautología: ¿alguna correlación K-resultado sin `shift(1)`? → inválido.

---

## Paso 1.5 — Ley 3-B: proyección de trayectoria K

Ejecutar **después** del Veredicto K, **antes** de la Auditoría 1.

### Cadena: alimentación → inflación → cobro

| Fase | Implicación para hoy |
|---|---|
| **Alimentación** | Equipo probablemente gana (la casa "infla" las K). **v3.1:** solo si `k` general **no tiene gatillo activo**. Si lo tiene → puede estallar hoy mismo. |
| **Inflación** | Contra rival débil, las K siguen subiendo. Victoria probable. |
| **Cobro** | Las K convergen en estallido aquí. Equipo vulnerable. |

### Condiciones de activación (todas deben cumplirse)

1. Trayectoria verificable: 1+ constante en zona de estallido contra distribución histórica.
2. Rival futuro de nivel suficiente (**solo del screenshot**, Ley 9).
3. Condición coincidente (`k_visita` solo cuenta vs. próximo partido de visita).
4. Convergencia: 2+ constantes apuntando a estallido en el **mismo** partido futuro.

### Prohibiciones de la Ley 3-B

- No usar nivel de rivales fuera del screenshot.
- No proyectar con una sola constante.
- No asumir "rival débil = estallido" (rival débil = **inflación** en la proyección).
- **Excepción v3.1:** "rival débil = inflación" es una heurística de **proyección futura**, no un escudo contra el estallido actual. Si la K propia tiene gatillo activo hoy, el nivel del rival es irrelevante.

```
VEREDICTO 3-B: [Equipo]
Cadena: [ALIMENTACIÓN / INFLACIÓN / COBRO] → [rival, fecha, condición]
Constantes en trayectoria: [valores proyectados]
Implicación para hoy: [resultado porque...]
```

---

## Auditoría 1 (obligatoria entre Paso 1 y Paso 2)

> Antes llamada *§Anti-Sesgo-1* o *§AS-1*.

Construir una **hipótesis de derrota del favorito** usando **solo** constantes K. Si las K están en silencio: declarar *"las K no respaldan victoria del favorito"*.

**Blindaje de Ley 9 (v3.1):** construir la hipótesis **exclusivamente** con gatillos K del equipo. Prohibido usar nivel, nombre o identidad del rival para atenuar.

```
HIPÓTESIS DE NO-VICTORIA [Equipo]:
  Gatillos activos propios: [sin referencia al rival]
  Señales de trayectoria propias: [patrón, conteo de subidas]
  Señales complementarias propias: [estallido posterior de k_goles_recibido,
                                     desaceleraciones, etc.]
  Severidad: [ALTA si 3+ gatillos / MEDIA si 2 / BAJA si 1]
  → ALTA: no-victoria ≥ 25%  |  MEDIA: ≥ 15%
```

---

## Paso 2 — Doble oportunidad trampa (Ley 6)

> Antes llamada *DC trampa*.

Si la doble oportunidad **1X o 2X** del favorito está **por encima de 1.05** → es una alerta.

**Doble oportunidad trampa + K techo = amplifica la señal de que el favorito puede no ganar.**

## Paso 3 — Tensión del Favorito (Ley 5)

> Antes llamada *Anticulebra*. Ver `references/motor_tension_favorito.md` para fórmula del Índice de Favoritismo (ICF), features del modelo ML y sistema de tensión acumulada.

Evaluar:

- **Índice de Favoritismo (ICF)** de cada equipo.
- **Ruptura del modelo de mercado**: ¿la probabilidad del modelo ML diverge de la cuota?
- **Tipo de tensión**: intra-día (acumulada en la jornada) y entre días.

**Convergencia crítica:** K techo + doble oportunidad trampa + Tensión del Favorito alta → **el favorito no gana.**

## Paso 3.5 — Goles × Fecha × Condición (Ley 7)

Mirar los **últimos 6 partidos del equipo en ese contexto** (local o visitante).

- **No usar promedios → buscar ciclos.**
- Poisson = promedio. K + trayectoria histórica = posición en el ciclo.
- Cada equipo tiene una dinámica distinta.
- Un equipo **rara vez repite el marcador exacto** del partido anterior.

---

## Paso 4 — Riesgo de no-victoria (ambos equipos)

Pregunta: *¿qué condiciones harían que este equipo no gane, independientemente del rival?*

Revisar: K techo, K silente, K en 0 prolongada, Gap de regresión, ciclo de goles apagándose, Ley 3, bajas.

### Cumplimiento obligatorio

- Los factores de riesgo deben reflejarse **proporcionalmente** en los escenarios.
- Si hay factores para el favorito → **prohibido** que la no-victoria quede como escenario terciario.
- **v3.1 — mínimo del underdog:**
  - 2+ factores de riesgo en el favorito → victoria del underdog ≥ 5%.
  - 3+ → ≥ 10%.
  - 4+ → ≥ 15%.
  - **Solo se asigna 0% si ningún gatillo está activo.**
- **v3.1 — simetría direccional:** si el favorito "puede no ganar" **y** el underdog "puede mejorar" → las probabilidades se **suman aritméticamente**.

---

## Paso 5 — Leyes complementarias (nunca revierten una K clara)

### Ley 2 — Regresión + Fe Perdida

- **Regresión:** `|gap| ≥ 0.8` = señal estructural. **No predice goles ni marcador.**
  - **Signo:** `gap > 0` = sub-rinde, tiende a mejorar · `gap < 0` = sobre-rinde, tiende a empeorar. Verificar contra la etiqueta textual del motor.
  - **Horizonte:** al partido siguiente el gap tiene ≤0.1 pts de residual. Es orientativo a **~5 partidos**, no promesa inmediata. No construir la lectura de este partido sobre la tendencia del gap.
  - **Único hallazgo replicado:** el sobre-rendimiento fuerte **persiste** (+0.11 ± 0.05). Es anti-reversión. Prohibido escribir que a un equipo caliente "le toca caerse".
  - **Reportar los dos gaps** (clásico y ajustado) con el signo explícito. Si discrepan, la diferencia es el calendario y ese es el hallazgo.
  - **Favoritismo se lee con `μ_partido`, nunca con el gap diferencial.** Son cantidades distintas y pueden apuntar en direcciones opuestas.
  - **Sudamérica:** la localía real va de +0.48 a +0.73 (Perú +0.73) contra el +0.382 de μ. Corregir al local hacia arriba en la lectura. **Argentina:** nivel y rival ponderados a la mitad (~±0.15), así que un diferencial de μ chico es compresión de liga, no paridad real.
  - **Ventana con amistosos:** los amistosos de clubes son el bucket más grande de la base y alimentan forma y nivel. Un bajón de 5 partidos construido sobre amistosos es ruido.
- **Fe Perdida:** veredicto = **flag**. `NONE` = sin señal. Prohibido construir narrativa emocional con flag `NONE`.

### Ley 3 — Rivales Futuros

¿Dónde gana más la casa de apuestas reventando la burbuja del historial directo? Si hay partido continental en 3-5 días → la Ley 3 pasa a ser primaria.

**v3.1 — bidireccional:** presentar **ambas lecturas** (alimentación vs. vulnerabilidad). Resolver con los gatillos K: si la K tiene gatillo activo → la vulnerabilidad domina.

### Ley 4 — ya ejecutada en el Paso 0.5

Reevaluar solo si surgieron bajas nuevas entre el inicio del análisis y este punto.

### Ley 8 — Canales opuestos

Audiencia alta → incentivo a estallido.

---

## Auditoría 2 (antes de la conclusión)

> Antes llamada *§Anti-Sesgo-2* o *§AS-2*.

Tres preguntas obligatorias:

1. ¿Estoy concluyendo desde una posición cómoda o desde las leyes?
2. ¿Revisé **todas** las constantes?
3. ¿El marcador final viene de conteo de goles a favor recientes o de las leyes? (Solo `k_goles` + Poisson + trayectoria histórica son válidos como fuente de marcador.)

**Regla de inversión:** si la Auditoría 1 dijo "las K no respaldan victoria" y concluyo "gana" → justificar con una ley primaria **o invertir**.

**Auto-destrucción de ambos equipos:** construir un contra-caso usando solo leyes (sin usar el rival para atenuar).

**v3.1 — 4ª pregunta:** *"¿Asigné 0% a algún escenario que tenga gatillos K que lo respalden?"* → si sí, asignar al menos el mínimo.

---

## Prohibiciones permanentes

- Estadísticas descriptivas usadas como ley.
- Marcador derivado del conteo de goles a favor recientes (solo `k_goles` + Poisson + trayectoria histórica).
- Leer `k_positivo` / `k_negativo` sin fusionar.
- Revertir una K clara con leyes complementarias.
- Narrativa emocional sobre Fe Perdida cuando el flag es `NONE`.
- Confundir predicción de constante con predicción de resultado.
- Correlación K-resultado sin `shift(1)`.
- Usar nivel, nombre o identidad del rival para desactivar un gatillo K propio (violación de Ley 9).

---

## Post-análisis: auditoría automática

Después de completar todo el análisis, ejecutar:

```bash
python /path/to/sad-analysis/scripts/audit_protocol.py
```

El script verifica que todos los pasos se ejecutaron con el formato correcto. Si hay faltantes → completarlos antes de entregar.

---

## Bandera `DIV-MOTOR-MERCADO` (22.08.2026)

Cuando la probabilidad implícita del mercado sobre el favorito difiere en **≥20 puntos** del 1X2 derivado del motor de
Regresión al Nivel, declararlo como bandera propia con las dos cifras y sus fuentes. No ordena apostar contra el mercado:
ordena **documentar la divergencia y su desenlace** para construir la serie. Caso semilla: Sport Huancayo vs CD Moquegua
(F6 Clausura Perú 2026) — mercado 72% al local (cuota 1,39), motor 49%; ganó el visitante 0-2. Décima corrección del motor
en la serie general y **primera contra el mercado**. La serie DIV se cuenta aparte de la serie de correcciones manuales.
Configuración de máximo interés: divergencia ≥20 pp **y** gap del no-favorito > +0.5 (sub-rendimiento fuerte) apuntando
en la misma dirección — "el value no cura el reset" no aplica cuando value y reset coinciden, y eso hay que medirlo.
