---
name: sad-analysis
description: "Skill de la SÍNTESIS del sistema SAD (v4.2): lee las constantes K de cada equipo (la espina y el reventón de la burbuja, 60 % de la lectura), la Regresión al Nivel (μ_partido, gap), la doble oportunidad trampa, goles por fecha y condición y rivales futuros, y arma el pronóstico con sus tres fuentes a la vista —el 1X2 del motor calculado, la matriz y el mercado—, el marcador declarado y el falsador. Activar en todo análisis pre-partido de fútbol o de apuestas, al escribir la lectura SAD o el pronóstico de un parte, al leer las K o las burbujas de un equipo, y al cerrar un veredicto. Lee los datos de la API de la app SAD, no CSV."
---

# SAD — Análisis Deportivo (v4.2)

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
| **Espina** | Tu lectura de adónde va la K total (o de la condición) después de ESTE partido: `positiva` (gana) · `cero` (empata) · `negativa` (pierde) · `neutra` |
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
| 7 | Goles × Fecha × Condición | 3.5 | Vigente · el marcador sale de aquí, no de un Poisson |
| 8 | Canales Opuestos | — | **SUSPENDIDA (v4.0)**: sin dato de audiencia; cero usos |
| 9 | Nivel sobre nombre | Transversal | Vigente |

| Suspendido | Por qué | Qué lo reemplaza |
|---|---|---|
| **Fe Perdida** (péndulo, flags) | Sin motor en la app; dos partes la invocaron sin dato | Nada: presión e hinchada se cuentan como contexto **con fuente** |
| **Modelo de goles Poisson v6** (`references/ley_marcador.md`) | Sin motor; se improvisó con μ en 78 partes (error de unidad) | El 1X2 del motor calculado (`unXDos`); el marcador, paso 3.5 |
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

## Paso 1.6 — Espina de la burbuja *(v4.0)*

Va en `lecturaSad.espina` por equipo: `{lectura, guia, porque}`.

- **`lectura`**: `positiva` (la K crece → gana) · `cero` (se reinicia → empata) · `negativa` (pierde) · `neutra` (la historia no dice nada para este partido).
- **`guia`**: `total` o `condicion` (la K local si juega de local, la de visita si es visitante). `condicion` cuando la diferencia se VE en la tarjeta, no por defecto.

**Guía calibrada** (`riesgo.movimiento` de cada burbuja, REVENTON §14):

| riesgo | sigue | a cero | al otro signo |
|---|---|---|---|
| bajo | 53 % | 25 % | 22 % |
| medio | 46 % | 27 % | 27 % |
| alto | 35 % | 27 % | 37 % |
| muy alto | 28 % | 27 % | 45 % |

**Procedimiento:**

1. **Empezar por la tarjeta** (`espinaTarjeta`). Leer antes `espina/calibracion`.
2. **Tarjeta fuerte:** la espina la sigue, salvo un **hecho de ESTE partido** que la contradiga (DT nuevo con el once de vuelta, once roto, rotación por copa, un rival que el TDE ve cerrando). Entonces el `porque` dice «contra la tarjeta porque <el hecho>».
3. **Tarjeta débil:** deciden los skills; decir cuál. **La tarjeta débil de la condición no se sigue por defecto** *(v4.2)*: acertó el 26 % de local (10 de 38) y el 34 % de visita (12 de 35), peor que el azar; con guía `condicion` y tarjeta débil, la espina sale de los skills y el `porque` no la cita como apoyo. La fuerte sí: acierta el 59 % (101 de 170).
4. Ir contra el riesgo calculado se dice: «contra el riesgo alto porque…».

**Reglas de la cohorte c3:**

- **(a) `cero` necesita un hecho de ESTE partido.** Leída como `cero`, la espina acertó 8 de 37 (22 %), lo mismo que la frecuencia del empate. La frecuencia con que el equipo corta sus burbujas empatando **no alcanza** (falló en Cagliari, IdV, ADT, Guabirá, Racing). Sí empujan al empate: los dos perfiles DC apuntando al empate, dos burbujas negativas enfrentadas, un rival que empata la mitad de sus partidos.
- **(b) El `porque` y la lectura van en la misma dirección.** Si el porqué dice que la racha se corta, la espina no lee que sigue (Puerto Cabello, Bucaramanga, Newcastle).
- **(c) Contra la tarjeta, con un hecho, no con un perfil.** Ganó un DT nuevo invicto con el once de vuelta (Nacional); perdieron la diferencia de EFE, la altura o el perfil de visita (Independiente Petrolero, Pasto, Chicó). Cuando el analista contradijo a la tarjeta con hechos, acertó 21 de 55 contra 10 (al 28/10: 63 de 134 contra 29 de la tarjeta). **No son un hecho** *(v4.2)*: la frecuencia propia del equipo (de local, de visita, de empates: Gremio «0 de 15 de visita», Portuguesa, Cerro Largo), un perfil DC de un solo lado, una rotación que no confirmó el club ni una fuente de nivel A (Tigre–Tucumán: una sola cadena de prensa), la brecha del EFE con T.54 / R-KT.2 / ESCALA-LIGAS (Palestino, City) y el H2H de la sede (Aucas: «nueve visitas sin ganar»).
- **(d) Burbuja de un partido:** «se da vuelta» no tiene más base que «se reinicia».
- **(e) Guía de la condición con T.54 o ESCALA-LIGAS:** si la K de la condición se armó con otro DT o en otra categoría, se lee la total o se declara la reserva (San Lorenzo, UCV Moquegua, Málaga). La serie del DT nuevo cuenta (EFE v1.6, T.54).
- **(f) `neutra` es honesta pero no puntúa** (0 de 18). Con riesgo alto o muy alto, una `neutra` que no nombra el riesgo deja sin lectura al lado que decide el partido.
- La espina puede ir **contra el 1X2**: se dice en la lectura del 1X2 y no se acomoda. Se mide sola.

---

## Paso 1.7 — Reventón de la burbuja *(v4.0)*

Una línea por equipo en `lecturaSad.reventon`, tras leer `/burbujas` de los dos. Los números no se copian: la app los recalcula.

- **(a) El riesgo frena la carga, no elige el lado del 1X2.** Con riesgo alto o muy alto, el 1X2 **no carga a favor de la racha** (Auxerre, América de Cali, City con 47 % a que siguiera: reventaron). Tampoco se da vuelta contra el favorito del mercado solo por el riesgo (Palmeiras, Chelsea, Feyenoord, Cúcuta: siguieron). Con riesgo muy alto la racha sigue el 28 % de las veces, no nunca.
- **(b) El tramo del rival se sobreestima cuando el rival rota** por otra competición (São Paulo–Vasco, Torque).
- **(c) Con ESCALA-LIGAS** el tramo del rival compara niveles de dos bases: el riesgo se lee con la confianza bajada (Bodø, Porto, Sporting Cristal, U. Católica, West Ham, Elversberg).
- **(d) FAMILIA-RECORD se sostiene:** una burbuja en su récord no se corta por estar en récord (Inter Bogotá, Ameliano, Brest, Central Córdoba, Tolima, Cajamarca). El corte necesita algo más que el récord.
- **(e) K-EXTREMO y K-CERCA-EXTREMO** son prudencia con la carga, obligatoria: la línea dice EXTREMO con el N de partidos y el pronóstico no recomienda cargar a que la racha siga. Un extremo `INFLADA` (hecho con amistosos) se nombra igual.
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

**El marcador** *(v4.0)*: la app **no tiene modelo de goles**. El marcador exacto es **lectura**, no número: sale de la Ley 7, de las stats (`/equipos/{id}/stats`: goles, xG) y del 1X2 del motor, y se declara como celda probable **sin porcentaje inventado**. **Nunca de un Poisson con μ** (μ son puntos, no goles).

- Un rótulo («los que menos marcan», «partido cerrado») no achica la banda de goles que dicen los promedios (Delfín–Manta: 6 goles).
- Una racha de goles en contra no convierte el gol del rival en certeza (Everton–Chelsea).
- Entre dos celdas casi empatadas, se nombran las dos.
- **El volumen de los dos lados** *(v4.2)*: el marcador lee lo que genera uno **contra lo que concede el otro** (`/equipos/{id}/stats`, xG a favor y en contra). El xG medio de un equipo no viaja solo (Central Córdoba–Vélez: el 0-1 salió de «Vélez genera poco», 0,9 de xG, contra un local que concede 1,81; fue 0-5). Un ataque que remata mucho y no convierte, contra un bloque que concede volumen, no sostiene un under (Jaguares–Tolima).

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
- **La razón que cae** *(v4.2)*. Una razón que una alerta del propio parte anula no sostiene el número: con `EFE-EMPATE-TECNICO`, ESCALA-LIGAS o T.54, el porcentaje del EFE no es razón para separarse del mercado ni del motor; si era la razón, el número vuelve al mercado (Cagliari–Bologna; Aston Villa–City, Leones–Libertad y Barcelona–Real Madrid se apoyaron en la brecha con T.54 del otro lado y fallaron).
- **DIV-MOTOR-MERCADO:** con ≥ 20 puntos entre el mercado y el motor sobre el favorito, se declara con las dos cifras. No ordena apostar: documenta. La serie se sigue contando (hoy acierta a veces uno y a veces el otro).

### 6-B — Las probabilidades

`pronostico.probabilidades` {local, empate, visita}: parte de las tres fuentes; la lectura de cada equipo (60 % K, 40 % lo demás) lo mueve con su porqué. FACTOR-X, EJE-DEBUTANTE o GOLEADOR-AL-BANCO **amplían el rango, no mueven el centro** (EFE). G-SORPRESA también amplía el rango (EFE v1.6).

- **El empate parte del mercado** *(v4.1)*. El empate de `pronostico.probabilidades` arranca en el empate sin margen del mercado (sin mercado, en el de `unXDos`) y se aparta **más de 2 puntos** solo con un **hecho de ESTE partido** que empuje al empate o lo saque, nombrado en la lectura del 1X2: una eliminatoria donde el empate de los 90 tiene premio (penales, la ida a favor), un rival que defiende en bloque probado sin su ataque (Ley 4, bajas por zona), los dos perfiles DC apuntando al empate, dos burbujas negativas enfrentadas. Un «partido parejo» o un margen de μ bajo 0,30 **no** son un hecho: el mercado ya los tiene. Medido en 231 partes ciegos (14/09-24/10/2026): decíamos el empate 2 puntos sobre el mercado (27 contra 25) y pasó el 20 %; igualarlo al mercado bajó el Brier de 0,585 a 0,580 sin ajustar nada. Ni nosotros ni el mercado distinguimos qué partido termina empatado: no se inventa un empate alto sin un hecho.
- **Los dos perfiles DC alineados son un hecho; uno solo no** *(v4.2)*. Cuando el perfil de doble oportunidad de la condición de **los dos** equipos apunta al mismo resultado —el local no pierde y el visitante no gana, **cada uno en dos de cada tres partidos o más**—, es un **hecho de ESTE partido**: el 1X2 puede apartarse del mercado hacia ese lado, nombrándolo («+N al empate y al local por los dos perfiles DC, 78 % / 79 %»). Acertó en Leones–Libertad (78/79, ganó el local 4-1 con el motor, el EFE y las dos tarjetas en contra), Fortaleza–Cali (76/77, empate; el parte subió el empate solo 2 puntos), Palestino–Colo Colo (70/57, empate) y Pumas–Tigres (empate). **Un perfil extremo de un solo lado es frecuencia, no un hecho**, y no mueve el 1X2 sobre el mercado (Coritiba: el rival no ganaba de visita 0 de 15 y ganó; Vélez: no gana el 70 % fuera y ganó 0-5). El umbral «dos de cada tres» es de lectura, sin peso en la app; la serie se mide en Aprendizaje antes de darle más.
- **El favorito no se recorta por costumbre** *(v4.1)*. Cuando el mercado da al favorito 50 % o más y nuestro pick va al mismo lado, el número no queda por debajo del mercado salvo con un **dato que el mercado no tenga**, escrito con su cifra en la lectura del 1X2: «−N puntos al favorito por <el dato>». Valen el once oficial o la rotación confirmada después de la última captura, una baja estructural que salió después de la cuota y la Ley 3 confirmada. No valen el riesgo del reventón (1.7 a: frena la carga, no elige el lado), la espina contra el favorito, la localía cualitativa ni un μ con ESCALA-LIGAS. Medido en 231 partes ciegos: 66 de 78 picks de 50 %+ quedaron 7,4 puntos bajo el mercado; en el tramo 60+ dijimos 67 y acertó el 90 % (26 de 29, IC 74-96). La Auditoría 1 y el mínimo del underdog siguen valiendo: si los gatillos K piden no-victoria, se publican los dos números (disciplina 33), no se recorta en silencio.
- **Calibración de la cohorte** *(v4.1)*. Las tablas de acierto por tramo del dossier son para leer de dónde sale el error, no para multiplicar el número. Estirar las probabilidades con un factor sacado de la cohorte (temperatura, «+N al favorito», «empate a la frecuencia») empeoró el Brier fuera de la muestra (validación por fecha, 25.10.2026). El 1X2 se corrige con las reglas del empate y del favorito, que no tienen ningún número ajustado.

### 6-C — El falsador *(v4.0)*

Una **condición observable pura**, escrita sobre el **mecanismo** (quién genera, por dónde, con qué). **No** sobre el estado del marcador («si el favorito marca primero» en Braga: marcó y perdió sin que sonara), **no** sobre un minuto (Fluminense–Palmeiras: el gol llegó al 45), y **cubre los dos lados** de la lectura (Juventus–Lazio, Real Oruro–Aurora).

**No sobre el volumen** *(v4.2)*. El xG, los remates o la posesión no separan el resultado: el falsador se escribe sobre la **conversión** o sobre la **vía de gol** que la lectura da por cerrada (Sporting–Viseu: el falsador medía xG y no sonó con el favorito perdiendo 1-2, porque Sporting superó en xG y Viseu convirtió su transición; Aurora–Real Tomayapo: «si genera peligro en juego abierto, la lectura está mal» se cumplió y el 1X2 se sostuvo).

### 6-D — La lectura integrada (`lecturaSad`)

1. **Módulo operativo:** qué parte del SAD es usable hoy y con qué confianza (K que habla o calla, μ con su fiabilidad, mercado con o sin delta).
2. **1X2:** las probabilidades con su porqué en una lectura.
3. **Contexto:** presión de tabla, hinchada, clima del club — **con fuente citada**.
4. **Dato estructural:** el dato más duro y confiable.
5. **Paradoja del partido**, si hay contradicción entre tabla y contexto.
6. **Espina** (paso 1.6) y **reventón** (paso 1.7) de cada equipo.

---

## Auditoría 2 (antes de la conclusión)

1. ¿Estoy concluyendo desde una posición cómoda o desde las leyes?
2. ¿Revisé **todas** las constantes?
3. ¿El marcador viene de la Ley 7 y del 1X2 del motor, o del conteo de goles recientes / de un Poisson con μ?
4. ¿Asigné 0 % a algún escenario con gatillos K que lo respalden? → asignar el mínimo.
5. *(v4.0)* ¿El falsador es observable, sobre el mecanismo y de los dos lados?
6. *(v4.1)* ¿El empate y el favorito están donde los pone el mercado? Si no, ¿qué dato de ESTE partido, que el mercado no tenga, los movió? Escribirlo con la cifra.

**Regla de inversión:** si la Auditoría 1 dijo «las K no respaldan victoria» y concluyo «gana» → justificar con una ley primaria o invertir.

---

## Prohibiciones permanentes

- Estadísticas descriptivas usadas como ley.
- **Un Poisson con `μ` como λ de goles** *(v4.0)*: μ son puntos. El 1X2 del motor es `unXDos`.
- **Invocar un motor suspendido** *(v4.0)*: Fe Perdida, Tensión del Favorito / culebra / ICF, canales opuestos, «modelo de goles». Sin motor no hay dato.
- Leer `k_positivo` / `k_negativo` sin fusionar.
- Revertir una K clara con leyes complementarias en la LECTURA (el número del 1X2 sigue a las tres fuentes).
- Confundir predicción de constante con predicción de resultado.
- Una lectura K-resultado sin el corte «antes del partido».
- Usar nivel, nombre o identidad del rival para desactivar un gatillo K propio.
- Resolver una contradicción en silencio (disciplina 33).

---

## Auditoría automática

`scripts/audit_protocol.py` queda **suspendido** (revisaba el formato viejo: CSV, Paso 3 de Tensión). La auditoría es el **recibo del parte**: `faltan` (lo que el contrato pide y no vino, como el «contra la tarjeta porque…»), `rechazos` (lo que no entró y por qué) y las alertas calculadas (ESPINA-VS-RIESGO, K-EXTREMO, ESCALA-LIGAS, FAMILIA-RECORD). Se leen en cada depósito y se corrige antes de cerrar.

---

## Cuándo consultar `references/`

Solo bajo demanda:

- `references/ley_regresion_nivel.md` → nivel, μ, gap clásico y ajustado, signo, camino de recuperación, veredicto empírico (**vigente**).
- `references/casos_referencia.md` → auditorías históricas (el caso de la convergencia crítica queda como historia de la Ley 5).
- `references/ley_marcador.md`, `references/ley_fe_perdida.md`, `references/motor_tension_favorito.md` → **suspendidas (v4.0)**, historia del sistema anterior.
