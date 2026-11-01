---
name: sad-analysis
description: "Skill de la SÍNTESIS del sistema SAD (v4.4): lee las constantes K de cada equipo (la espina y el reventón de la burbuja, 60 % de la lectura), la Regresión al Nivel (μ_partido, gap), la doble oportunidad trampa, goles por fecha y condición y rivales futuros, y arma el pronóstico con sus tres fuentes a la vista —el 1X2 del motor calculado, la matriz y el mercado—, el marcador declarado y el falsador. Activar en todo análisis pre-partido de fútbol o de apuestas, al escribir la lectura SAD o el pronóstico de un parte, al leer las K o las burbujas de un equipo, y al cerrar un veredicto. Lee los datos de la API de la app SAD, no CSV."
---

# SAD — Análisis Deportivo (v4.4)

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

## Qué hace este skill

Dos cosas, y nada que no tenga dato en la app:

1. **La lectura de las K** de cada equipo: adónde va su burbuja después de este partido (la **espina**) y cuán cerca está de reventar (el **reventón**). Es el 60 % de la lectura.
2. **El pronóstico**: las tres fuentes a la vista (motor, matriz, mercado), las probabilidades 1X2, el marcador declarado, el falsador y la lectura integrada.

Los otros skills aportan: `efe-clasificador` (formación), `teorema-del-echado` (tramo final), `diagnostico-tactico` (juego), `efe-dashboard` (matriz de escenarios). Este skill los junta y concluye.

---

## Glosario rápido

| Término | Significado operativo |
|---|---|
| **Constante K** | Indicador acumulado de presión/rendimiento del equipo, calculado por el motor de la app (`/constantes/{id}`). `k = k⁺ + k⁻` |
| **Burbuja** | La racha abierta de la K (signo, partidos, K pico). Revienta cuando la K vuelve a cero o pasa al otro signo |
| **Espina** | Tu lectura de adónde va la K total (o de la condición) después de ESTE partido: `positiva` (gana) · `cero` (empata) · `negativa` (pierde). *(v4.4)* `neutra` ya no existe: sin lectura propia, la guía `pronostico` sigue al 1X2 declarado |
| **Tarjeta** | `espinaTarjeta` de `/burbujas`: la espina que da la historia sola (movimiento más probable de la guía calibrada); `fuerte` con ≥ 50 % |
| **Riesgo del reventón** | Puntos calibrados (racha, rival frente a la mediana con que revienta, contramano, favorito): bajo · medio · alto · muy alto. Es una TASA, no un corte |
| **K-EXTREMO / K-CERCA-EXTREMO** | La burbuja en su récord o por encima del 90 % de sus reventones: prudencia con la carga, no anuncio de corte |
| **μ (mu)** | Puntos esperados (0 a 3): `1.241 + 0.334·nivel − 0.357·nivel_rival + 0.382·localía`. `μ_partido` usa rival y localía reales y dice quién es favorito. **Son puntos, no goles** |
| **1X2 del motor** | `unXDos` de `/predicciones/{id}`: μ de los dos lados convertido a local · empate · visita con una logística calibrada sobre 51.254 partidos |
| **Gap de regresión** | `μ − forma reciente`. `gap > 0` = sub-rinde, tiende a mejorar; `gap < 0` = sobre-rinde |
| **Tres fuentes** | motor (`unXDos`), matriz (`efe-dashboard`), mercado (cuotas sin margen). Se publican juntas (disciplina 33) |
| **Falsador** | La condición observable que, si aparece, da la lectura por fallada |
| **Doble oportunidad trampa** | 1X o X2 del favorito por encima de 1,05 |

---

## Insumos (la API de la app; no hay CSV ni screenshot)

| Qué | Ruta |
|---|---|
| K y su historia | `GET /constantes/{equipo}` (con `antesDe=<fixture>` para la vista al día del partido) |
| Burbujas, riesgo, tarjeta, extremo, otras familias | `GET /equipos/{equipo}/burbujas?proximo={fixture}` |
| μ, gap, fiabilidad de μ y **1X2 del motor** | `GET /predicciones/{fixture}` → `local`, `visitante`, `fiabilidadMu`, `unXDos` |
| Mercado | `GET /cuotas/{fixture}` (y `/historial` para el delta apertura → cierre) |
| Goles y stats | `GET /equipos/{equipo}/stats` (goles, xG, posesión, con su muestra) |
| **Goles acotados** *(v4.3)* | `golesAcotados` de `GET /equipos/{equipo}/burbujas?proximo={fixture}` (intervalo de cada lado y marcador acotado) |
| Once y bajas (Ley 4) | `GET /analisis/cowork/f1/{fixture}`, la ficha y la prensa |
| Calendario (Ley 3) | `GET /equipos/{equipo}/calendario` |
| Calibración de la espina | `GET /analisis/cowork/espina/calibracion` |

### Orden anti-anclaje

**Leer las K y las burbujas primero → formular la espina de cada equipo → después abrir las cuotas.** Si se vieron las cuotas antes, declararlo:
> ⚠️ Alerta de anclaje: vi las cuotas antes de leer las K.

---

## Jerarquía

```
PREFILTRO — Ley 4 (XI): ¿el once que armó las K es el que va a jugar?

LECTURA (por equipo):
  K = 60 %  → Ley 1 (gatillos), 3-B (trayectoria), espina y reventón
  resto 40 % → EFE, TDE, DTP, Regresión (Ley 2), Ley 3, Ley 6, Ley 7

PRONÓSTICO (el número):
  tres fuentes a la vista (motor · matriz · mercado) → probabilidades 1X2
  la lectura lo MUEVE solo con disciplina 33: el número se mueve con su
  porqué o se publican los dos

EXCEPCIONES:
  Si K calla → la Regresión hereda (gap ≥ 0.8 = peso de K techo).
  Si hay partido continental en 3-5 días → la Ley 3 pasa a ser el lente primario.
```

## Las leyes

| # | Ley | Paso | Estado v4.0 |
|---|---|---|---|
| 1 | Constantes K | 1 | **Primaria de la lectura (60 %)** |
| 2 | Regresión al Nivel | 5 | Vigente · hereda si K calla · da el 1X2 del motor |
| 3 | Rivales Futuros | 5 | Vigente · primaria con copa continental en 3-5 días |
| 3-B | Proyección de Trayectoria K | 1.5 | Vigente |
| 4 | Formación y DT | 0.5 | Vigente · prefiltro |
| 5 | Tensión del Favorito | 3 | **SUSPENDIDA (v4.0)**: sin motor en la app; el backtest no encontró culebra |
| 6 | Cuotas Invariables (doble oportunidad) | 2 | Vigente |
| 7 | Goles × Fecha × Condición | 3.5 | Vigente · el marcador sale de los goles acotados *(v4.3)*, nunca de un Poisson con μ |
| 8 | Canales Opuestos | — | **SUSPENDIDA (v4.0)**: sin dato de audiencia; cero usos |
| 9 | Nivel sobre nombre | Transversal | Vigente |

| Suspendido | Por qué | Qué lo reemplaza |
|---|---|---|
| **Fe Perdida** (péndulo, flags) | Sin motor en la app; dos partes la invocaron sin dato | Nada: presión e hinchada se cuentan como contexto **con fuente** |
| **Modelo de goles Poisson v6** (`references/ley_marcador.md`) | Sin motor; se improvisó con μ en 78 partes (error de unidad) | El 1X2 del motor calculado (`unXDos`); el marcador, los goles acotados de la app (paso 3.5, v4.3) |
| **Entradas por CSV y screenshot** | La corrida lee la API | Las rutas de «Insumos» |
| **`scripts/audit_protocol.py`** | Revisa los pasos del formato viejo (CSV, Tensión) | El recibo del parte (`faltan`, `rechazos`, alertas como ESPINA-VS-RIESGO) |

---

## Reglas transversales

### Fusión K (prerrequisito)

`k = k_positivo + k_negativo`. Igual para `k_local` y `k_visita`. Las `k_goles` **no se fusionan** (anotado y recibido son flujos independientes).

**Las 6 constantes operativas:** `k` · `k_local` o `k_visita` (según la condición) · `k_goles_anotado` · `k_goles_recibido` · `k_goles_contexto_anotado` · `k_goles_contexto_recibido`.

### Anti-tautología (obligatoria)

Las K de una fila son valores **post-partido**. Toda lectura «al día del partido» usa la historia **estrictamente anterior** (`antesDe=<fixture>` en `/constantes`, `/niveles` y `/burbujas`). Una correlación K → resultado sin ese corte es inválida.

### Ley 9 — Nivel sobre nombre

El **nivel** determina la dinámica del partido, no la reputación. El nivel del rival **nunca desactiva** un gatillo K activo del equipo propio. **Detector:** si la justificación para descartar un gatillo contiene nombre, nivel, posición o identidad del rival → violación → parar y reevaluar.

> **Matiz v4.0 (reventón).** El nivel del rival SÍ entra al **riesgo calibrado del reventón** (paso 1.7), que mide cuándo una burbuja suele cortarse frente a rivales de ese nivel. La Ley 9 prohíbe usar el nombre o la reputación para **apagar** un gatillo, no leer la tarjeta calibrada.

### Prohibición de estadísticas descriptivas

Un porcentaje que no viene de las leyes, del motor ni de una guía calibrada de la app ilustra; no genera hipótesis.

---

## Paso 0.5 — Ley 4: filtro XI

**Antes de leer las K.** Bajas y rotaciones con la tabla F1 de la base (`/analisis/cowork/f1/{id}`) y la prensa.

Pregunta clave: *¿el XI que generó esta K es el que va a jugar?*

| Escenario | Condición | Impacto sobre las K |
|---|---|---|
| 1 — Mismo XI | Titulares intactos | K normales |
| 2 — Bajas periféricas | No-ejes ausentes | K con descuento leve |
| 3 — Bajas estructurales | Eje ausente o múltiples titulares en una misma zona | K defensivas sin validez de estallido; K de rebote congelada; K ofensiva del rival potenciada; **K techo puede seguir creciendo** |

**Principio:** toda presión acumulada requiere el mismo XI que la generó. Sin ese XI, se congela.

**Rotación por otra competición** *(v4.0)*: un once rotado por una semifinal o una copa es Escenario 3 para el que rota, y además baja el tramo del rival en el riesgo del reventón del otro lado (paso 1.7).

**Bajas del rival, por zona** *(v4.1)*: una baja **ofensiva** del rival le quita goles al rival: sube el empate y las celdas bajas (0-0, 1-0), **no** le suma puntos de victoria al otro equipo, y menos si el rival es un bloque estructural probado (clase del DTP). Una baja **defensiva** (o del arquero, o una zona rota con IP alto) del propio equipo sí le resta, y suele pesar más de lo que se lee (Tigres–León, Pachuca–Cruz Azul). Köln–Schalke (24.10.2026): +8 al local por el ataque diezmado de Schalke, 0-0 con 14 remates de Köln contra un bloque probado. El mercado ya conoce las bajas publicadas (6-A): el ajuste propio por bajas se escribe con la zona y va al empate o al marcador, no al favorito.

```
LEY 4: [Equipo] → Escenario [1 / 2 / 3]
Bajas: [jugadores y zona]
Impacto K: [normales / descuento / invalidadas]
K rival beneficiadas: [cuáles]
```

---

## Paso 1 — Constantes K (60 % de la lectura, simetría obligatoria)

### 1-A — Extracción (solo cálculo)

Para cada constante operativa, de `/constantes` y `/burbujas`:

1. Valor actual + techo histórico + porcentaje del techo.
2. Picos anteriores (valores y fechas).
3. Si el valor es 0: partidos consecutivos en 0 + sequías anteriores + qué ocurrió después.
4. Resets en `k_goles`: ¿2+ en el ciclo activo? Patrones similares.
5. Deltas consecutivos: aceleraciones / desaceleraciones + episodios previos.
6. Distribución de goles a favor / en contra con la K contextual previa en el mismo rango.

Si `k_goles_general` y `k_goles_contextual` divergen → reportar la tensión (la contextual prioriza).

### 1-B — 6 gatillos (por equipo y constante, contra el historial propio)

| # | Gatillo | Cómo evaluarlo |
|---|---|---|
| 1 | ¿Techo histórico? | Valor actual vs. dispersión de picos propios. **Nota v4.0:** el techo es **prudencia** (no cargar a que siga), no anuncio de corte: estar sobre la K con que suele reventar no adelanta el reventón (REVENTON §13.2). Es la lectura de K-EXTREMO |
| 2 | ¿Presión en 0? | Sequía actual vs. previas que terminaron en brote |
| 3 | ¿Resets acumulados? | 2+ resets en el ciclo activo + historial de explosión post-reset |
| 4 | ¿Aceleración delta? | 2+ desaceleraciones consecutivas = marcador mínimo + señal de estallido |
| 5 | ¿Convergencia? | 2+ señales direccionales |
| 6 | ¿Combinación → marcador? | Cruzar gatillos para anticipar un marcador emergente |

**Patrón de N subidas → estallido:** si 2+ ciclos terminaron en estallido tras el mismo número de subidas (±1) y el ciclo actual lo iguala → gatillo activo.

### 1-C — Reglas especiales

- **Predicción de constante ≠ predicción de resultado.**
- **Interacción entre constantes:** K de goles y K de rendimiento no son independientes.
- **Historial directo como burbuja:** 2+ victorias seguidas contra el mismo rival pueden reventar; la deuda se cobra una sola vez.

### 1-F — ¿K habla o K calla?

**K calla solo si se cumplen todas:** cerca de 0 sin igualar sequías históricas · sin techo en `k_goles` contextual · sin resets con patrón · sin desaceleración con precedente · trayectoria sin ciclo identificable. **Un solo gatillo activo = K habla.**

### 1-G — Lectura K (antes «Veredicto K»)

```
LECTURA K: [Equipo] → dirección GANA / EMPATA / PIERDE (de la espina)
Gatillos activos: [por equipo, con evidencia]
Confianza K: ALTA / MEDIA / BAJA
```

Es la dirección de cada equipo según sus K. **No es el número del 1X2** (paso 6). Con confianza baja, las complementarias heredan.

### 1-H — Anti-anclaje post-lectura

¿La primera frase interpretativa ya tenía dirección? Si coincide con la lectura → sospechar → construir la hipótesis opuesta → si es más fuerte, invertir.

---

## Paso 1.5 — Ley 3-B: proyección de trayectoria K

| Fase | Implicación para hoy |
|---|---|
| **Alimentación** | Probablemente gana. Solo si `k` general **no tiene gatillo activo** |
| **Inflación** | Contra rival débil, las K siguen subiendo |
| **Cobro** | Las K convergen en estallido aquí: equipo vulnerable |

**Activación (todas):** trayectoria verificable · rival futuro de nivel suficiente (**del calendario de la base**, `/equipos/{id}/calendario`) · condición coincidente · 2+ constantes apuntando al mismo partido futuro. «Rival débil = inflación» es proyección futura, no escudo contra el estallido de hoy.

---

## Paso 1.6 — Espina de la burbuja *(v4.0; v4.4)*

Va en `lecturaSad.espina` por equipo: `{lectura, guia, porque}`.

- **`lectura`**: `positiva` (la K crece → gana) · `cero` (se reinicia → empata) · `negativa` (pierde). *(v4.4)* **`neutra` sale**: acertó 0 de 17 (IC 0-18) y no puede acertar nunca, porque la K siempre se mueve (crece, vuelve a cero o pasa al otro signo). Medida como lectura, era un fallo seguro.
- **`guia`**: `total` · `condicion` (la K local si juega de local, la de visita si es visitante) · `pronostico` *(v4.4)*. `condicion` cuando la diferencia se VE en la tarjeta, no por defecto. `pronostico` cuando no hay lectura propia (paso 4 del procedimiento).

**Guía calibrada** (`riesgo.movimiento` de cada burbuja, REVENTON §14):

| riesgo | sigue | a cero | al otro signo |
|---|---|---|---|
| bajo | 53 % | 25 % | 22 % |
| medio | 46 % | 27 % | 27 % |
| alto | 35 % | 27 % | 37 % |
| muy alto | 28 % | 27 % | 45 % |

**Lo medido en la cohorte c3** *(v4.4, 740 lados)*: `positiva` acierta el 57 % (337 lados) y `negativa` el 57 % (324), 17 puntos sobre la frecuencia de su movimiento (40 %): ahí está la información. `cero` acierta el 19 % (12 de 62), lo mismo que la frecuencia del empate (20 %): leer `cero` sin un hecho no agrega nada. La tarjeta fuerte acierta el 58 % (120/207) y la débil el 40 % (167/421). Contra la tarjeta, el analista acertó 84 y la tarjeta 33, sobre 164.

**Procedimiento, en cuatro pasos** *(v4.4)*. Empezar por la tarjeta (`espinaTarjeta`) y leer antes `espina/calibracion`.

1. **Tarjeta fuerte:** la espina la sigue, salvo un **hecho de ESTE partido** que la contradiga (DT nuevo con el once de vuelta, once roto, rotación por copa, un rival que el TDE ve cerrando).
2. **Hecho de ESTE partido:** lectura propia, y el `porque` dice «contra la tarjeta porque <el hecho>».
3. **Tarjeta débil:** deciden los skills; decir cuál. **La tarjeta débil de la condición no se sigue por defecto** *(v4.2)*: acertó el 26 % de local (10 de 38) y el 34 % de visita (12 de 35); con guía `condicion` y tarjeta débil, la espina sale de los skills y el `porque` no la cita como apoyo. Contradecir la tarjeta débil con los skills acertó en la mayoría de los casos de la tanda del 28-31/10 (Carabobo, Galatasaray, Pachuca, Atlético Nacional, Guaraní, Llaneros, Nice, Alianza Atlético, Monza; falló en Villarreal, Genk y Junior).
4. **Sin nada de eso** —ni tarjeta fuerte que seguir, ni hecho para contradecirla, ni lectura de los skills con la tarjeta débil—: **guía `pronostico`** *(v4.4)*. La espina sigue al 1X2 declarado: el elegido gana, así que `positiva` para él y `negativa` para el otro; si el elegido es el empate, `cero` en los dos. El `porque` dice «sin lectura propia: sigue al 1X2». Medido: el elegido del 1X2 acierta el 55 % (203/367), contra el 40 % de la tarjeta débil y el 0 % de `neutra`. Aprendizaje la mide aparte (`acreditables.espina.porGuia`), para que no se mezcle con la lectura propia.

Ir contra el riesgo calculado se dice: «contra el riesgo alto porque…».

**Reglas de la cohorte c3:**

- **(a) `cero` necesita un hecho de ESTE partido, de una lista cerrada** *(v4.4)*. La frecuencia con que el equipo corta sus burbujas empatando **no alcanza** (falló en Cagliari, IdV, ADT, Guabirá, Racing). Valen solo:
  - los dos perfiles DC apuntando al empate (la app los trae por condición en `/burbujas`);
  - una eliminatoria o un partido único donde el empate a los 90 tiene premio para uno de los dos: penales, prórroga, la ida a favor (sale de la ronda y de la ida);
  - los dos lados con el empate como marcador declarado **y** un hecho del partido escrito.

  **Salen de la lista** *(v4.4)* «dos burbujas negativas enfrentadas» —Remo–Botafogo (1492437): la espina `cero` por eso falló, y el empate subido 3 puntos por lo mismo dejó el 1X2 35/35 sin elegido con el motor dando al local arriba; el backtest de las lecciones (REVENTON §12) ya decía que las burbujas enfrentadas no puntúan— y «un rival que empata la mitad de sus partidos», que contradecía a la regla (c): la frecuencia propia de empates no es un hecho (Portuguesa). **La prudencia tampoco es un hecho para `cero`**: el extremo se trata en la regla (g). «Cero» como refugio de la duda (Parma 1550173, Comerciantes 1549530, Feyenoord 1552207, Portuguesa 1646923, Oriente 1645527, Chicó y Junior 1549726) acierta lo que la frecuencia; lo que esas lecciones pedían de verdad es la coherencia con el marcador de la regla (h).
- **(b) El `porque` y la lectura van en la misma dirección.** Si el porqué dice que la racha se corta, la espina no lee que sigue (Puerto Cabello, Bucaramanga, Newcastle).
- **(c) Contra la tarjeta, con un hecho, no con un perfil.** Ganó un DT nuevo invicto con el once de vuelta (Nacional); perdieron la diferencia de EFE, la altura o el perfil de visita (Independiente Petrolero, Pasto, Chicó). **No son un hecho** *(v4.2; v4.4)*: la frecuencia propia del equipo (de local, de visita, de empates: Gremio «0 de 15 de visita», Portuguesa, Cerro Largo), un perfil DC de un solo lado, una rotación que no confirmó el club ni una fuente de nivel A (Tigre–Tucumán: una sola cadena de prensa), la brecha del EFE con T.54 / R-KT.2 / ESCALA-LIGAS (Palestino, City), el H2H de la sede (Aucas: «nueve visitas sin ganar»), *(v4.4)* las burbujas negativas enfrentadas (Remo–Botafogo), un cambio de banco sin tarjeta, en ninguna dirección (Espanyol 1570442, con el interino como posible reacción), «el arranque de una burbuja» leído del motor y del once (Metropolitanos 1646923, Santos 1492438) y una sequía del débil leída como vía cerrada (3.5).
- **(d) Burbuja de un partido:** «se da vuelta» no tiene más base que «se reinicia».
- **(e) Guía de la condición con T.54 o ESCALA-LIGAS** *(endurecida en v4.4)*. Con T.54 del lado (DT de menos de seis meses, la misma fecha que usa `T.54-SIN-DECLARAR`) o con ESCALA-LIGAS / R-KT.2, si la K de la condición se armó con otro DT o en otra categoría: **la guía es `total`** y la tarjeta débil de esa K **no se cita como apoyo**. Ya no basta la reserva en el `porque`: FC Cajamarca (1549531) siguió la tarjeta fuerte de local armada con otro DT (T.54 de siete días), con la reserva escrita, y perdió. Con ESCALA o R-KT.2 la tarjeta débil no orienta: Elversberg (1575211) falló siguiéndola; Monza (1550172) la contradijo por la escala y acertó. La serie del DT nuevo cuenta (EFE v1.6, T.54).
- **(f) Dos tarjetas débiles que concuerdan no suman** *(v4.4; reemplaza a la vieja (f) sobre `neutra`)*. Cada una vale lo que vale, el 40 %: medido, las débiles que concuerdan aciertan el 39 % (30/77) contra el 44 % de una sola. Ni se refuerzan ni se contradicen sin un hecho, y contradecirlas pide el mismo hecho que contradecir una (Atlético-MG–Cruzeiro 1492430 y América–Tijuana 1550952: las dos iban al local y fallaron; Coventry–Sunderland 1557451: concordaban, acertaron, y contradecirlas con el descanso falló).
- **(g) La espina en el extremo** *(v4.4; es la regla de la alerta ESPINA-SIGUE-EN-EXTREMO de la app)*. Con K-EXTREMO o K-CERCA-EXTREMO (de la total o de la condición), la espina dice «sigue» **solo con un hecho de ESTE partido nombrado en el `porque`**. Valen la diferencia de nivel a favor de la racha que la app trae en el riesgo (`rival.aFavor` / `rival.favorito`) y una baja del rival confirmada en el once o por una fuente de nivel A. No valen el perfil del club, el objetivo en la tabla ni una baja sin confirmar. Acertó «sigue» con un hecho nombrado (Atlético Grau 1549529: el llano a 3.400 m y la zaga nueva; Sporting Cristal 1549534: Alianza sin Pavez ni Antoni; Casa Pia 1575531: un rival 1,43 de nivel arriba) y siguiendo la tarjeta fuerte con la diferencia de nivel a favor (PSG 1552801, Brugge 1558670, Heerenveen 1552208); sin hecho, o con un perfil, falló o se cortó en empate (UTC Cajamarca 1549531, «descendido sin objetivo» es perfil; Udinese 1550173, bajas sin comprobar en el once; Atalanta 1550169; Rizespor 1584454, 0-0).
  - **Sin ese hecho, en el extremo la espina no dice «sigue» y tampoco va a `cero` por prudencia.** Va con la tarjeta si la tarjeta lee el corte. Si la tarjeta también dice «sigue», va al corte más frecuente de la guía calibrada: **al otro signo** con riesgo alto o muy alto (37 % y 45 % contra 27 % a cero), salvo un hecho de la lista de `cero` de la regla (a). ⚠️ Son 6 cortes en la tanda y 3 salieron a cero: la serie se mide en Aprendizaje (espina en el extremo, por lectura) antes de afinar.
  - **Leer el corte en el extremo sin hecho tampoco funcionó**: Medellín (1549728, `cero`, y la racha siguió a cuatro) y Querétaro (1551021, siguió). El extremo no adelanta el corte (REVENTON §13.2: la K no puntúa).
- **(h) La espina y el marcador declarado del mismo parte no se contradicen en silencio** *(v4.4)*. Es la regla que ya rige para el 1X2: si un lado lee `positiva`, el marcador no lo da perdiendo, y al revés; si el marcador es un empate, la espina no lee `positiva` en un lado y `negativa` en el otro sin decirlo (Chicó y Junior, 1549726: 1-1 declarado con la espina positiva y negativa). Si van distinto, se dice en la lectura.
- La espina puede ir **contra el 1X2** en una lectura propia: se dice en la lectura del 1X2 y no se acomoda. Se mide sola. (Con guía `pronostico` sigue al 1X2 por definición.)

---

## Paso 1.7 — Reventón de la burbuja *(v4.0)*

Una línea por equipo en `lecturaSad.reventon`, tras leer `/burbujas` de los dos. Los números no se copian: la app los recalcula.

- **(a) El riesgo frena la carga, no elige el lado del 1X2.** Con riesgo alto o muy alto, el 1X2 **no carga a favor de la racha** (Auxerre, América de Cali, City con 47 % a que siguiera: reventaron). Tampoco se da vuelta contra el favorito del mercado solo por el riesgo (Palmeiras, Chelsea, Feyenoord, Cúcuta: siguieron). Con riesgo muy alto la racha sigue el 28 % de las veces, no nunca.
  - **Qué es «cargar»** *(v4.4)*: poner al lado de la racha **por encima del mercado**. Quedarse en el número del mercado no es cargar (6-B). Con riesgo alto o muy alto, el número del lado de la racha **no sube sobre el mercado** y el `porque` del 1X2 **nombra el riesgo**. Así seguir al mercado y frenar la carga dejan de chocar: Villarreal (1570442, 67 %) y Genk (1558666, 49 % del mercado) estaban en el mercado y ahí se quedan, con el riesgo escrito. Se siguió la racha con riesgo alto y reventó en Villarreal, Genk, Real Potosí (1645526, 63 % con la K de local en muy alto), Palmeiras (1492438) y en Coventry–Sunderland y Kocaelispor–Rizespor (1557451, 1584454: las dos burbujas en riesgo alto y el 1X2 a que seguían las dos); se respetó el riesgo y se cumplió en Santa Fe, Jaguares, Lecce y Alianza Lima. Medido con riesgo alto o muy alto (`respetoRiesgo`): el 1X2 que apostó a que la racha sigue acertó el 49 % (Brier 0,598, 169 lados) y el que apostó al corte el 53 % (0,591, 244): la diferencia existe y es chica, el riesgo vale como freno, no como lado (REVENTON §13.3).
  - «Riesgo alto en las dos burbujas → más empate» **no** es regla: sigue de candidato (Rizespor 0-0, Coventry 3-1, Remo–Botafogo sin empate).
- **(b) El tramo del rival se sobreestima cuando el rival rota** por otra competición (São Paulo–Vasco, Torque).
- **(c) Con ESCALA-LIGAS** el tramo del rival compara niveles de dos bases: el riesgo se lee con la confianza bajada (Bodø, Porto, Sporting Cristal, U. Católica, West Ham, Elversberg).
- **(d) FAMILIA-RECORD se sostiene:** una burbuja en su récord no se corta por estar en récord (Inter Bogotá, Ameliano, Brest, Central Córdoba, Tolima, Cajamarca). El corte necesita algo más que el récord.
- **(e) K-EXTREMO y K-CERCA-EXTREMO** son prudencia con la carga, obligatoria: la línea dice EXTREMO con el N de partidos y el pronóstico no recomienda cargar a que la racha siga. La espina en el extremo sigue la regla (g) de 1.6 *(v4.4)*: «sigue» solo con un hecho nombrado, y sin él no va a `cero` por prudencia. Un extremo `INFLADA` (hecho con amistosos) se nombra igual y **pesa poco la racha**, pero *(v4.4)* **no es razón para ir contra la tarjeta ni contra el riesgo** (Unionistas, 1644371, en la copa; Atlético Baleares, 1644343, no se siguió).
- La estabilidad (DT, ventana, bajas) mueve la **confianza**, nunca el riesgo.

---

## Auditoría 1 (entre el paso 1 y el 2)

Construir una **hipótesis de no-victoria del favorito** usando **solo** gatillos K propios (sin el rival para atenuar). Si las K callan: *«las K no respaldan victoria del favorito»*.

```
HIPÓTESIS DE NO-VICTORIA [Equipo]:
  Gatillos activos propios / señales de trayectoria / señales complementarias
  Severidad: ALTA si 3+ gatillos / MEDIA si 2 / BAJA si 1
  → ALTA: no-victoria ≥ 25 %  |  MEDIA: ≥ 15 %
```

---

## Paso 2 — Doble oportunidad trampa (Ley 6)

Si la doble oportunidad **1X o X2** del favorito está **por encima de 1,05** → alerta. Con K techo, amplifica la señal de que el favorito puede no ganar. Cuotas de `/cuotas/{id}`; una cuota inconsistente (1X por encima del 1) no se usa y se dice.

## Paso 3 — Ley 5: SUSPENDIDA *(v4.0)*

La Tensión del Favorito (ICF, Random Forest, tensión acumulada, «convergencia crítica») **no se aplica**. Motivo: no existe motor en la app; el estudio de febrero dejó `ml_break_score` roto (42,9 % en cero) y el ICF con r = 0,10; el backtest del 19.10.2026 (63.475 partidos del padrón) no encontró culebra: con la jornada intacta, el siguiente favorito gana igual o algo más de lo esperado. `references/motor_tension_favorito.md` queda como historia.

**Lo que queda en pie, como regla de mercado:** la combinada de favoritos tiene poca probabilidad (es el producto de las de cada uno) y **paga el margen de la casa k veces**. Nunca «el siguiente favorito va a caer».

## Paso 3.5 — Goles × Fecha × Condición (Ley 7) y el marcador

Mirar los **últimos 6 partidos del equipo en esa condición** y las K de goles. No promedios → ciclos. Un equipo rara vez repite el marcador exacto.

**El marcador** *(v4.3)*: sale de los **goles acotados** de la app (`golesAcotados` en `/burbujas?proximo=`), un modelo de goles calibrado con el padrón (REVENTON §17): para cada lado, un **intervalo de dos goles** («mete 1 o 2») con su probabilidad y uno de tres, y el **marcador acotado** (los cuatro marcadores que salen de cruzar los dos intervalos). Medido en el padrón con corte temporal: el intervalo acierta lo que promete (64 %) y el marcador acotado el 41 %: acota, no adivina el marcador exacto. Sus λ son **goles**, del cruce de lo que mete uno de local (o de visita) contra lo que concede el otro en su condición: no es el Poisson con μ, que sigue prohibido.

- **El marcador declarado va dentro del marcador acotado.** Se elige entre sus cuatro con la Ley 7 y la lectura (espina, TDE, DTP). Sacarlo de ahí pide **un hecho de ESTE partido** que el modelo no ve —una baja del arquero o del goleador confirmada, un once alternativo, la vía de gol que el DTP da por abierta—, escrito en la lectura con su fuente. Una sensación («partido cerrado», «viene goleando») no lo saca.
- **Los números no se copian**: el parte los recalcula al leer (`lecturaSad.golesAcotados`) y el veredicto mide intervalo y marcador (`objetivo.golesAcotados`).
- **No mueven el 1X2 ni son señal de apuesta.** Contra el mercado de más/menos 2,5 y de ambos marcan no hubo ventaja, y que los cuatro marcadores acotados den el mismo ganador todavía no está medido como señal: Aprendizaje lo mide primero (`acreditables.golesAcotados`). El 1X2 sigue a las tres fuentes (6-A, 6-B).
- **Sin modelo o sin historia** (`sinDato`), el marcador vuelve a ser lectura de la Ley 7 y del 1X2 del motor, declarado como celda probable **sin porcentaje inventado**.
- El marcador **no se repite** más de lo que da el azar (medido, REVENTON §17): que un equipo «empata 1-1 seguido» no es razón para el 1-1.

- Un rótulo («los que menos marcan», «partido cerrado») no achica la banda de goles que dicen los promedios (Delfín–Manta: 6 goles).
- Una racha de goles en contra no convierte el gol del rival en certeza (Everton–Chelsea).
- Entre dos celdas casi empatadas, se nombran las dos.
- **El volumen de los dos lados** *(v4.2)*: el marcador lee lo que genera uno **contra lo que concede el otro** (`/equipos/{id}/stats`, xG a favor y en contra). El xG medio de un equipo no viaja solo (Central Córdoba–Vélez: el 0-1 salió de «Vélez genera poco», 0,9 de xG, contra un local que concede 1,81; fue 0-5). Un ataque que remata mucho y no convierte, contra un bloque que concede volumen, no sostiene un under (Jaguares–Tolima).
- **La goleada como rama nombrada** *(v4.4)*. El acotado no cubre la cola de la goleada del favorito (PSG 1-5 en 1552801 con 26 % de 3+ en la distribución, Colo Colo 6-1 en 1505548, Macará 3-0 en 1639801, Anderlecht 4-0 en 1558662). Cuando **el propio parte la escribió en otro lado** —el TDE da `se_rompe` al que persigue, la matriz escribe la goleada tras el gol temprano, el rival concede el doble de la media—, la celda de goleada se **nombra como rama, sin sacar el marcador declarado del acotado**: «2-0, y 4-0 si abre antes del 20'», y el falsador cubre esa rama (6-C). Es nombrar la cola, no mover el marcador: el acotado sigue mandando. En Colo Colo la goleada estaba en el TDE y en la matriz; en Anderlecht, en el rival que concedía 2,3 por partido.
- **El gol del débil sale del volumen cruzado** *(v4.4)*: lo que genera contra lo que concede el otro. **No se da «de cortesía»** sin volumen que lo sostenga (Cienciano 1549529: Grau sin remates al arco; Atlético Nacional–Santa Fe 1549724: sin Bustos y 0,26 de xG; Cruzeiro 1492430: F3 ATK en rojo) **ni se niega por una sequía**: una sequía describe la forma, no la vía que el favorito le abre al exponerse (Zulte Waregem 1558670). La sequía del débil se suma a la lista de lo que no es un hecho (1.6 c).
- Los penales (Rennes 5-2 en 1552806 con tres, Junior 3-2 en 1549850 con dos) son varianza: van al falsador como vía (6-C), no al marcador.

---

## Paso 4 — Riesgo de no-victoria (ambos equipos)

*¿Qué condiciones harían que este equipo no gane, independientemente del rival?* K techo, K silente, K en 0 prolongada, gap, ciclo de goles apagándose, Ley 3, bajas, riesgo del reventón.

- Los factores de riesgo se reflejan **proporcionalmente** en los escenarios.
- Con factores para el favorito → **prohibido** que la no-victoria quede como escenario terciario.
- **Mínimo del underdog:** 2+ factores → ≥ 5 %; 3+ → ≥ 10 %; 4+ → ≥ 15 %. Solo 0 % si ningún gatillo está activo.
- **Simetría direccional:** si el favorito «puede no ganar» y el underdog «puede mejorar», las probabilidades se suman.

---

## Paso 5 — Leyes complementarias

### Ley 2 — Regresión al Nivel (y la fuente «motor»)

Detalle en `references/ley_regresion_nivel.md`.

- `|gap| ≥ 0.8` = señal estructural; **no predice goles ni marcador**. Signo: `gap > 0` sub-rinde → tiende a mejorar. Horizonte ~5 partidos, no este. El sobre-rendimiento fuerte **persiste**: prohibido «le toca caerse».
- Reportar los dos gaps (clásico y ajustado) con su signo.
- **Favoritismo con `μ_partido`, nunca con el gap.**
- **El 1X2 del motor es `unXDos`** de `/predicciones/{id}` *(v4.0)*: la conversión de los dos μ calibrada sobre 51.254 partidos (log-loss 1,051 contra 1,059 del Poisson sobre μ y 1,071 de la frecuencia). Se copia tal cual como fuente «motor». Si viene null, el motor no corrió y se dice.
- **Margen de `μ_partido` bajo 0,30** *(v4.0)*: el partido es parejo para el motor y el 1X2 queda cerca de `unXDos`. Se aparta solo con un **dato nuevo** que el motor no ve (once rotado, baja estructural, Ley 3 confirmada); una localía cualitativa, «DT nuevo + altura» o un perfil no alcanzan (Sport Boys, Chicó–Cúcuta, Pasto, Juventus–Lazio). Y al revés: un margen bajo el umbral no vuelve pick al empate cuando motor y mercado apuntan al mismo lado (Parma).
- **ESCALA-LIGAS / `fiabilidadMu` baja** *(v4.0)*: μ cruza niveles que no comparan. Se publica como sale, **ni gobierna el 1X2 ni se invierte en silencio**: se ensancha el rango y se publican los números (Porto, Fenerbahçe, LASK, Bodø).
- **Sudamérica:** la localía real va de +0.48 a +0.73 contra el +0.382 de μ: se **dice**, no se recalcula μ. **Argentina:** nivel comprimido; un diferencial chico es compresión, no paridad.
- **Ventana con amistosos:** un bajón armado sobre amistosos es ruido; un nivel inflado por amistosos se declara y el centro no se ancla en el motor (Gladbach).

### Ley 3 — Rivales Futuros

Con partido continental en 3-5 días, la Ley 3 pasa a ser primaria. Bidireccional: alimentación vs. vulnerabilidad; si la K tiene gatillo activo, domina la vulnerabilidad. **Con la Ley 3 activa y rotación confirmada, el 1X2 baja al favorito** *(v4.0)* (Estudiantes L.P. con once mixto quedó en 42 % y perdió en casa).

### Fe Perdida y Ley 8 — SUSPENDIDAS *(v4.0)*

Sin motor ni dato en la app. Presión de la hinchada o del entorno va como contexto **con fuente** en el paso 6, sin «módulo emocional» ni flag. `references/ley_fe_perdida.md` queda como historia.

---

## Paso 6 — La síntesis: pronóstico y lectura integrada *(v4.0)*

### 6-A — Las tres fuentes, a la vista (disciplina 33)

| Fuente | De dónde | Campo |
|---|---|---|
| Motor | `unXDos` de `/predicciones/{id}` | `pronostico.motor` |
| Matriz | la matriz de escenarios de `efe-dashboard` (probabilidad por escenario) | `pronostico.matriz` |
| Mercado | cuotas sin margen, promedio de casas | `pronostico.mercado` |

- **Cuando dos señales propias van contra el 1X2, el número se mueve o se publican los dos con su origen.** Escribir la contradicción en prosa y dejar el número anclado en un lado es resolverla en silencio (Alianza Atlético, Fluminense–Santos, Santos Laguna, Estudiantes de Mérida).
- **Un descuento propio contra el mercado pide un dato que el mercado no tenga.** El mercado ya descuenta las bajas conocidas (Nacional en Chicó); la rotación por copa la ve el mercado y el motor no (São Paulo–Vasco).
- **El mercado que se mueve** *(v4.2)*. El 1X2 no se aparta del mercado **en la dirección contraria al delta** apertura → cierre (`/cuotas/{id}/historial`) sin un dato propio que lo explique: un delta que se corre es información que el mercado ya tiene (Cúcuta–Águilas: local 3,6 puntos sobre el mercado con la cuota corriéndose a la visita y Berdugo en duda; ganó la visita 0-2).
- **El delta ya está en la última captura** *(v4.4)*. El mercado que se publica es el de cierre: sumarle el delta otra vez es contarlo dos veces. El delta sirve para lo de arriba (no ir en su contra) y **no para apartarse del mercado en su dirección**. Seguir el delta sin noticia falló: Los Chankas–Cusco (1549533: +4 al local en la mañana, sin causa publicada, más los perfiles DC, llevaron el 1X2 3,5 puntos sobre el mercado al local; ganó la visita 0-1), Parma–Udinese (1550173: separarse hacia el motor «por el delta de apertura» no tuvo sostén en cancha).
- **Un delta sin noticia identificada no da vuelta al elegido** *(v4.4)*. Cuando el delta cambia quién es el favorito del mercado y no hay una noticia que lo explique, el elegido no se decide por el delta: se publican el motor y el mercado con sus números (disciplina 33) y se dice «delta sin causa». Lille–Lens (1552802): la cuota se corrió a la visita sin una razón encontrada (2.32 → 2.73), el pick se dio vuelta contra el motor (local 41 %) y contra las dos espinas del propio parte, y ganó Lille; Coventry–Sunderland (1557451): el delta corrido a Sunderland, el motor con el local al 41 %, ganó el local 3-1. Seguir el delta salió bien con el motor de acuerdo (Carabobo 1646922) o con el mercado ya ≥ 50 % (Cienciano).
- **Partido parejo con motor y mercado en lados distintos** *(v4.4)*. Si el mercado da al favorito menos de 50 % y el motor elige el otro lado, se escriben **los dos elegidos** y el pick dice cuál sigue y por qué. Eso **no habilita a seguir al motor por defecto**: son 3-4 casos (Cambuur–Go Ahead 1552211, Sporting Cristal–Alianza 1549534, Lille, Coventry) y Parma va en contra; la serie se mide en Aprendizaje antes de la próxima revisión.
- **La razón que cae** *(v4.2)*. Una razón que una alerta del propio parte anula no sostiene el número: con `EFE-EMPATE-TECNICO`, ESCALA-LIGAS o T.54, el porcentaje del EFE no es razón para separarse del mercado ni del motor; si era la razón, el número vuelve al mercado (Cagliari–Bologna; Aston Villa–City, Leones–Libertad y Barcelona–Real Madrid se apoyaron en la brecha con T.54 del otro lado y fallaron).
- **DIV-MOTOR-MERCADO:** con ≥ 20 puntos entre el mercado y el motor sobre el favorito, se declara con las dos cifras. No ordena apostar: documenta. La serie se sigue contando (hoy acierta a veces uno y a veces el otro).

### 6-B — Las probabilidades

`pronostico.probabilidades` {local, empate, visita}: parte de las tres fuentes; la lectura de cada equipo (60 % K, 40 % lo demás) lo mueve con su porqué. FACTOR-X, EJE-DEBUTANTE o GOLEADOR-AL-BANCO **amplían el rango, no mueven el centro** (EFE). G-SORPRESA también amplía el rango (EFE v1.6).

- **El empate parte del mercado** *(v4.1)*. El empate de `pronostico.probabilidades` arranca en el empate sin margen del mercado (sin mercado, en el de `unXDos`) y se aparta **más de 2 puntos** solo con un **hecho de ESTE partido** que empuje al empate o lo saque, nombrado en la lectura del 1X2: una eliminatoria o un partido único donde el empate de los 90 tiene premio (penales, prórroga, la ida a favor), un rival que defiende en bloque probado sin su ataque (Ley 4, bajas por zona), los dos perfiles DC apuntando al empate. *(v4.4)* **Dos burbujas negativas enfrentadas y un rival que empata la mitad de sus partidos ya no son un hecho** (1.6 a; Remo–Botafogo). Un «partido parejo» o un margen de μ bajo 0,30 **no** son un hecho: el mercado ya los tiene. Medido en 231 partes ciegos (14/09-24/10/2026): decíamos el empate 2 puntos sobre el mercado (27 contra 25) y pasó el 20 %; igualarlo al mercado bajó el Brier de 0,585 a 0,580 sin ajustar nada. Ni nosotros ni el mercado distinguimos qué partido termina empatado: no se inventa un empate alto sin un hecho.
- **Los dos perfiles DC alineados son un hecho; uno solo no** *(v4.2)*. Cuando el perfil de doble oportunidad de la condición de **los dos** equipos apunta al mismo resultado —el local no pierde y el visitante no gana, **cada uno en dos de cada tres partidos o más**—, es un **hecho de ESTE partido**: el 1X2 puede apartarse del mercado hacia ese lado, nombrándolo («+N al empate y al local por los dos perfiles DC, 78 % / 79 %»). Acertó en Leones–Libertad (78/79, ganó el local 4-1 con el motor, el EFE y las dos tarjetas en contra), Fortaleza–Cali (76/77, empate; el parte subió el empate solo 2 puntos), Palestino–Colo Colo (70/57, empate) y Pumas–Tigres (empate). **Un perfil extremo de un solo lado es frecuencia, no un hecho**, y no mueve el 1X2 sobre el mercado (Coritiba: el rival no ganaba de visita 0 de 15 y ganó; Vélez: no gana el 70 % fuera y ganó 0-5). El umbral «dos de cada tres» es de lectura, sin peso en la app; la serie se mide en Aprendizaje antes de darle más.
  - **Lo que dicen juntos es «el visitante no gana», no «el local gana»** *(v4.4)*. Con los dos perfiles alineados el visitante no ganó en 11 de 13 partes de la tanda del 28-31/10 (Bragantino, Fluminense, Inter Bogotá, Grêmio, Pachuca, Atlético Nacional, Guaraní, Corinthians y Bournemouth ganaron; Metropolitanos–Portuguesa 1646923 y Real Oruro–Nacional Potosí 1645528 empataron). Los puntos se **restan a la visita** y se **reparten entre el local y el empate**, con el `porque` diciendo cuánto va a cada uno («−N a la visita por los dos perfiles DC, 78 % / 79 %: +a al local, +b al empate»). No van todos al local: Metropolitanos (+4,7 al local solo por los perfiles, 0-0) y Trinidense–Rubio Ñu (1632049: +5 al local, ganó la visita 2-4 con un ataque cambiado en el once); repartido acertó en Fluminense (1492435: +1 al local, −2 a la visita) e Inter Bogotá (1549728). En Real Oruro se siguió al mercado hacia la visita, el empate subió solo 1,6 y salió 1-1, lo que los dos perfiles decían juntos.
  - **Los dos perfiles no son dos fuentes independientes** de la espina y del 1X2 a la vez: se nombran **una vez**, como el hecho del partido, no como dos apoyos.
  - ⚠️ Sin número nuevo: el umbral «dos de cada tres» y la cuantía de N no se tocan hasta que Aprendizaje mida la tasa de «el visitante no gana» con los dos perfiles alineados.
- **El favorito no se recorta por costumbre** *(v4.1)*. Cuando el mercado da al favorito 50 % o más y nuestro pick va al mismo lado, el número no queda por debajo del mercado salvo con un **dato que el mercado no tenga**, escrito con su cifra en la lectura del 1X2: «−N puntos al favorito por <el dato>». Valen el once oficial o la rotación confirmada después de la última captura, una baja estructural que salió después de la cuota y la Ley 3 confirmada. No valen el riesgo del reventón (1.7 a: frena la carga, no elige el lado), la espina contra el favorito, la localía cualitativa ni un μ con ESCALA-LIGAS. Medido en 231 partes ciegos: 66 de 78 picks de 50 %+ quedaron 7,4 puntos bajo el mercado; en el tramo 60+ dijimos 67 y acertó el 90 % (26 de 29, IC 74-96). La Auditoría 1 y el mínimo del underdog siguen valiendo: si los gatillos K piden no-victoria, se publican los dos números (disciplina 33), no se recorta en silencio.
- **El número del favorito es el del mercado, hacia arriba y hacia abajo** *(v4.4)*, salvo un dato escrito con su cifra. **Lo que NO es un dato** para bajar al favorito del mercado (es la misma lista que en 6-A dice qué no saca el número del mercado):
  - **el motor más bajo**, con o sin DIV-MOTOR-MERCADO, ESCALA-LIGAS o una ventana con amistosos. En 12 partes el mercado daba al favorito 50 %+ y el motor menos; siguiendo al mercado ganaron 8 (Bragantino 1492432, Once Caldas 1549731, ADT 1549527, Napoli 1550172, Inter 1550176, Cienciano 1549529, Galatasaray 1584455, Sporting CP 1575531), con la altura, la localía sudamericana que μ no ve, la forma mezclada con la Champions y la ESCALA-LIGAS pesando en el motor. De los cuatro que no ganaron, solo en Genoa–Juventus (1550171) el motor estaba más cerca; América (1550952) y Bayern (1575203) empataron con 28 y 25 remates, por conversión, y Melgar (1549530) tuvo una roja al 4';
  - **una frecuencia de la condición con menos de 10 partidos** (Elversberg–Mainz 1575211: +7,5 al favorito sobre el motor por «3 de 3 de visita», y no ganó);
  - **la rotación o las bajas ya publicadas antes de la última captura**: están en la cuota (América 1550952, Alianza Atlético 1549528);
  - **el riesgo del reventón y la espina** (ya escritos en la v4.1).

  **Tampoco se sube sobre el mercado** por la tabla de la cohorte: la subconfianza del cuadro global es sobre todo de antes de la v4.1 (en la v4.0 decíamos 54 al 50-59 con el mercado en 60, y 66 al 60+ con el mercado en 74; desde la v4.1 la distancia es de medio punto: 54,7 contra 55,2, 68,9 contra 69,4); lo que queda lo comparte el mercado (en v4.1-v4.3 el elegido acertó 111 de 179, 62 %, cuando el mercado le daba ~52 %, en todos los tramos: una semana en la que el elegido ganó más de lo que pagaba cualquiera); la v4.3 sola está calibrada en el tramo alto (15 de 22 al 69 %), y el valor no la confirma (apostar siempre a nuestro elegido a la cuota media, `valorMercado.nuestroFavorito`, n 466: +4,2 % con el intervalo de −5,5 % a +14 %, cruza cero). **Ningún «+N» al favorito, ninguna temperatura ni factor.**

  **Cuándo se reabre:** si con la v4.3 o posterior un tramo llega a n ≥ 30 con el intervalo entero **por encima de lo que dijimos y de lo que daba el mercado**, y `valorMercado.nuestroFavorito` sale con el intervalo sobre cero (n ≥ 50), la revisión siguiente propone «el favorito sobre el mercado» con la validación por fecha de la v4.1. Antes, no.
- **Calibración de la cohorte** *(v4.1)*. Las tablas de acierto por tramo del dossier son para leer de dónde sale el error, no para multiplicar el número. Estirar las probabilidades con un factor sacado de la cohorte (temperatura, «+N al favorito», «empate a la frecuencia») empeoró el Brier fuera de la muestra (validación por fecha, 25.10.2026). El 1X2 se corrige con las reglas del empate y del favorito, que no tienen ningún número ajustado. *(v4.4)* Ni hacia abajo ni hacia arriba.

### 6-C — El falsador *(v4.0)*

Una **condición observable pura**, escrita sobre el **mecanismo** (quién genera, por dónde, con qué). **No** sobre el estado del marcador («si el favorito marca primero» en Braga: marcó y perdió sin que sonara), **no** sobre un minuto (Fluminense–Palmeiras: el gol llegó al 45), y **cubre los dos lados** de la lectura (Juventus–Lazio, Real Oruro–Aurora).

**El marcador fuera del acotado** *(v4.3)*. Si el marcador declarado sale del marcador acotado, el falsador nombra la **vía de gol** que lo saca de ahí (la que se abre o la que se cierra): si esa vía no aparece en el partido, la lectura del marcador está mal. Dentro del acotado no hace falta: el veredicto mide el intervalo solo.

**No sobre el volumen** *(v4.2)*. El xG, los remates o la posesión no separan el resultado: el falsador se escribe sobre la **conversión** o sobre la **vía de gol** que la lectura da por cerrada (Sporting–Viseu: el falsador medía xG y no sonó con el favorito perdiendo 1-2, porque Sporting superó en xG y Viseu convirtió su transición; Aurora–Real Tomayapo: «si genera peligro en juego abierto, la lectura está mal» se cumplió y el 1X2 se sostuvo).

**Comprobable, por cláusula y con todas las vías** *(v4.4)*:

1. **Sobre lo que la ficha registra**: el gol con su minuto, el autor, el asistente y el tipo (penal, autogol), las tarjetas y los cambios, y las stats de la ficha (remates al arco, xG si viene). **Una cláusula que la ficha no puede comprobar no cuenta** (Monza–Napoli 1550172: «remate de centro en el área» y «remate de cabeza», que la ficha no trae, dejaron el falsador sin evaluar).
2. **Una condición observable por cláusula.** Si son dos vías, son dos cláusulas que suenan cada una, **nunca «A y B»** (Xerez–Cádiz 1644386: falló la vía de Cádiz, el falsador atado con «y» no sonó y Xerez marcó por robo).
3. **Toma todas las vías del DTP, incluidos el penal y el banco**, más la **vulnerabilidad propia que el parte declaró** (Carabobo–La Guaira 1646922: tomó dos de las tres vías y el gol llegó por la tercera; Llaneros–Junior 1549850: dos penales; Kifisia–Olympiakos 1593347 y Anderlecht 1558662: el gol llegó del banco; Numancia–Oviedo 1644364: el error de salida del arquero suplente estaba en el parte y no en el falsador). Si la lectura nombra la goleada como rama (3.5), el falsador la cubre.
4. **Ningún corte de reloj antes de la palanca que el propio parte escribió** (el banco del favorito, el cambio de régimen del TDE): Poblense–Ceuta (1644368) cortaba en el 70' con el banco del favorito escrito desde el 60'.

Funcionó así en Fluminense, Genoa–Juventus, Metropolitanos, Los Chankas y Coquimbo.

### 6-D — La lectura integrada (`lecturaSad`)

1. **Módulo operativo:** qué parte del SAD es usable hoy y con qué confianza (K que habla o calla, μ con su fiabilidad, mercado con o sin delta).
2. **1X2:** las probabilidades con su porqué en una lectura.
3. **Contexto:** presión de tabla, hinchada, clima del club — **con fuente citada**.
4. **Dato estructural:** el dato más duro y confiable.
5. **Paradoja del partido**, si hay contradicción entre tabla y contexto.
6. **Espina** (paso 1.6) y **reventón** (paso 1.7) de cada equipo.

### 6-E — Copa nacional entre categorías *(v4.4)*

Rúbrica de las 24 lecciones de la Copa del Rey (29/10). Las copas nacionales tienen población `copa`: fijan rúbrica y no entran a ninguna métrica.

1. **El 1X2 de una copa nacional sale del mercado**; el motor se publica como referencia y no gobierna (localía negativa en copas; es lo que ya hace la app). Hortaleza–Sevilla (1645578): 93 % del mercado contra 49 % del motor; también Granada, Eldense, Valladolid y Huesca.
2. **Partido único con prórroga o penales:** el empate a los 90 es un hecho para `cero` (1.6 a) y para el empate del 1X2 (6-B). Es una salida del chico: Numancia–Oviedo (1644364), SS Reyes–Coria (1644377: el 1-1 declarado leía mejor que el 1X2).
3. **Contra un rival de otra categoría la K de la condición no se usa como guía** (1.6 e): la K armada en otra categoría no describe el partido (Racing 1644374: la K de visita en su récord, hecha en LaLiga; Osasuna 1644339, Getafe 1644358 y Sporting 1644356 contra rivales muy inferiores). El hecho que corta una burbuja es **la diferencia de categoría, nombrada** (ESCALA-LIGAS, fuera del padrón). Sin tarjeta, la espina por defecto contra el de más categoría no tiene base (Coria): va la guía `pronostico`.
4. **Rival sin datos:** la falta de datos **no es «pocos goles»**. La banda sale del volumen del grande, y la goleada escrita en la matriz se nombra como rama (3.5). Huesca 1-5 con 0-1 declarado (1644366); un gol de cortesía al de sexta (Osasuna); el más goleador de su grupo dejado en cero (Laredo 1644357); la goleada escrita en la matriz y no en el marcador (Athletic 1645579); un récord de goles recibidos no se proyecta contra otra escala (Depor 1644342).

---

## Auditoría 2 (antes de la conclusión)

1. ¿Estoy concluyendo desde una posición cómoda o desde las leyes?
2. ¿Revisé **todas** las constantes?
3. ¿El marcador está dentro del marcador acotado *(v4.3)*? Si no, ¿qué hecho de este partido lo saca, con su fuente, y lo dice el falsador? ¿O viene del conteo de goles recientes / de un Poisson con μ?
4. ¿Asigné 0 % a algún escenario con gatillos K que lo respalden? → asignar el mínimo.
5. *(v4.0)* ¿El falsador es observable, sobre el mecanismo y de los dos lados?
6. *(v4.1; v4.4)* ¿El empate y el favorito están donde los pone el mercado? Si no, ¿qué dato de ESTE partido, que el mercado no tenga, los movió? Escribirlo con la cifra. ¿Lo que lo movió está en la lista de lo que NO es un dato (6-B: el motor más bajo, una frecuencia de menos de 10 partidos, rotación o bajas ya publicadas, el riesgo o la espina) o es el delta sumado otra vez (6-A)?
7. *(v4.4)* ¿La espina de cada lado tiene lectura propia (tarjeta fuerte, un hecho, o los skills con la tarjeta débil)? Si no, ¿va con guía `pronostico`? ¿Un `cero` sale de la lista cerrada de 1.6 (a)? ¿La espina y el marcador declarado dicen lo mismo?
8. *(v4.4)* ¿Cada cláusula del falsador se puede comprobar en la ficha, es una sola condición, y entre todas cubren las vías del DTP, el penal, el banco y la vulnerabilidad propia, sin un corte de reloj antes de la palanca escrita?

**Regla de inversión:** si la Auditoría 1 dijo «las K no respaldan victoria» y concluyo «gana» → justificar con una ley primaria o invertir.

---

## Prohibiciones permanentes

- Estadísticas descriptivas usadas como ley.
- **Un Poisson con `μ` como λ de goles** *(v4.0)*: μ son puntos. El 1X2 del motor es `unXDos`.
- **Invocar un motor suspendido** *(v4.0)*: Fe Perdida, Tensión del Favorito / culebra / ICF, canales opuestos, el «modelo de goles» Poisson v6. Sin motor no hay dato. Los goles acotados de la app *(v4.3)* no son ese modelo: tienen motor y se leen en su ruta.
- **Mover el 1X2 o recomendar un mercado de goles por los goles acotados** *(v4.3)*.
- **La espina `neutra`** *(v4.4)*: sin lectura propia, guía `pronostico`.
- **«+N» al favorito, temperatura o factor de la cohorte** *(v4.4)*, hacia arriba o hacia abajo.
- Leer `k_positivo` / `k_negativo` sin fusionar.
- Revertir una K clara con leyes complementarias en la LECTURA (el número del 1X2 sigue a las tres fuentes).
- Confundir predicción de constante con predicción de resultado.
- Una lectura K-resultado sin el corte «antes del partido».
- Usar nivel, nombre o identidad del rival para desactivar un gatillo K propio.
- Resolver una contradicción en silencio (disciplina 33).

---

## Auditoría automática

`scripts/audit_protocol.py` queda **suspendido** (revisaba el formato viejo: CSV, Paso 3 de Tensión). La auditoría es el **recibo del parte**: `faltan` (lo que el contrato pide y no vino, como el «contra la tarjeta porque…»), `rechazos` (lo que no entró y por qué) y las alertas calculadas (ESPINA-VS-RIESGO, K-EXTREMO, ESCALA-LIGAS, FAMILIA-RECORD, ESPINA-SIGUE-EN-EXTREMO). Se leen en cada depósito y se corrige antes de cerrar.

---

## Cuándo consultar `references/`

Solo bajo demanda:

- `references/ley_regresion_nivel.md` → nivel, μ, gap clásico y ajustado, signo, camino de recuperación, veredicto empírico (**vigente**).
- `references/casos_referencia.md` → auditorías históricas (el caso de la convergencia crítica queda como historia de la Ley 5).
- `references/ley_marcador.md`, `references/ley_fe_perdida.md`, `references/motor_tension_favorito.md` → **suspendidas (v4.0)**, historia del sistema anterior.
