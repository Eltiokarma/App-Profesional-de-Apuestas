# El bucle de aprendizaje — diseño, todavía sin construir

> **Estado: fase B HECHA (13.09.2026).** El veredicto a las 12 h está
> construido y en la app. Las fases C, D y A siguen planificadas. Cada fase se
> marca aquí al construirse.

## Lo que se quiere, en una frase

Que Cowork **mire lo que ya dijo antes de analizar**, que **valide su propio
pronóstico 12 horas después del partido**, que **deje escrito qué aprendió
cuando falla**, y que cada tantos fallos **pida permiso** para convertir esas
lecciones en una versión nueva de un skill.

Cuatro piezas, en ese orden:

```
  A. ANTECEDENTES     Cowork lee lo que dijo de estos equipos → escribe menos      PENDIENTE
  B. VEREDICTO 12h    ¿acertó? lo objetivo lo calcula la app; el juicio lo escribe   HECHA
  C. LECCIONES        lo aprendido se acumula por skill, con su población declarada  PENDIENTE
  D. REVISIÓN         cada N fallos la app arma el dossier y el usuario autoriza     PENDIENTE
```

---

## La disciplina que el bucle NO puede romper

Esto va primero porque es lo que hace que el resto valga algo. Los skills ya
traen su propia regla, y coinciden:

> `teorema-del-echado` · CALIBRACION.md
> *"Hay dos poblaciones de RETRO. Los cuatro sembrados fueron elegidos porque
> hubo echada; los reconstruidos por fecha completa son ciegos al resultado.
> Mezclarlos infla la tasa de echada de 11% a 31%, y ese sesgo es el que
> sostenía la escala."*

> `diagnostico-tactico` · registro de la cadena
> *"Los casos contaminados fijan rúbrica pero **no acreditan**."*

De ahí salen cinco invariantes para cualquier cosa que construyamos:

1. **Toda fila lleva su `seleccion`**: `ciega` (el partido se eligió antes de
   saber nada), `por_resultado` (se eligió porque pasó algo) o
   `post_resultado` (se puntuó con el marcador ya a la vista). El parte de
   Cowork nace ciego —se elige de la agenda, la noche anterior— y eso es
   justamente lo que lo hace valioso: **es la primera vez que el sistema
   produce casos ciegos en volumen y sin esfuerzo**.
2. **Solo la población ciega calcula métricas.** Las otras dos se guardan, se
   muestran y se excluyen del acierto y del Brier. Un panel que mezcle las
   tres miente.
3. **`modo_evaluacion` PRE o COND.** Solo PRE acredita validación predictiva.
   Distingue **contra qué se puntuó**, no cuánto vio quien puntúa: `PRE` = el
   caso se cerró contra el **resultado final**; `COND` = se cerró contra un
   marcador **parcial**, con el partido todavía rodando, así que el acierto es
   condicional y podría darse vuelta. Todo veredicto se escribe después del
   partido —eso no lo vuelve COND—; lo que lo vuelve COND es puntuar sin que
   haya terminado. Es comprobable y **el backend lo comprueba**: declarar PRE
   sobre un fixture que no figura terminado se rechaza con 422.
4. **Sin pronóstico previo no hay veredicto.** Es la regla anti-hindsight que
   `cadena_dtp` ya implementa (`guardar_cadena` nunca pisa una apertura
   existente). El bucle la hereda entera.
5. **La app no mueve un peso jamás.** Acumula, cuenta y presenta. Que un peso
   del IE cambie es una decisión del usuario sobre el skill, con el listón de
   evidencia del propio skill (el TDE pide N ≥ 5 ciegos cerrados).

### El matiz sobre "cada 4 partidos fallados"

Cuatro fallos es un buen disparador para **abrir la revisión**: junta material
suficiente para que mirarlo valga la pena. No es un permiso para mover nada.
El TDE dice explícitamente "ningún peso tocado" mientras no haya N ≥ 5 casos
**ciegos y cerrados**, y cuatro fallos pueden ser cuatro casos contaminados.

Así que el dossier de la fase D muestra **dos cifras separadas**, nunca una:

- *"4 fallos acumulados"* → por eso te estoy escribiendo.
- *"de los cuales 2 son ciegos y cerrados; el skill pide 5"* → por eso todavía
  no se toca la escala.

Confundirlas es el error que este documento existe para evitar.

---

## Qué existe ya y qué falta

| Pieza | Estado hoy | Qué falta |
|---|---|---|
| Pronóstico declarado pre-partido | ✅ `parte_cowork` + `cadena_dtp.registro.pronostico_clave` | — |
| Marcador final del partido | ✅ `fixtures` (ingesta) | — |
| Cierre del eslabón (qué pasó, veredicto, lección) | ✅ `POST /analisis/cowork/{id}/veredicto` lo escribe (fase B) | — |
| Casos de validación del EFE | ⚠️ tabla `casos_validacion` en efe.db, **vacía** | poblarla |
| Registro del TDE | ❌ vive en el `.csv` del skill, fuera de la app | tabla propia |
| Casos del `sad-analysis` | ❌ `references/casos_referencia.md`, a mano | — |
| Métricas de acierto / Brier | ✅ `GET /analisis/cowork/lecciones`, solo sobre población ciega y con línea de base | — |
| Pantalla de aprendizaje | ✅ sección **Aprendizaje** (fase C) | — |

La buena noticia: **la mitad del andamiaje ya está puesto** y quedó puesto por
razones independientes. `cadena_dtp` tiene el campo `registro` con
`{pronostico_clave, que_paso, veredicto, leccion}` exactamente, y su regla
anti-hindsight ya funciona.

---

## A · Antecedentes: que Cowork no reescriba lo que ya sabe — **HECHA** (24/09/2026)

> **Cómo quedó**: `backend/analisis/antecedentes.py` →
> `GET /analisis/cowork/antecedentes/{fixtureId}?n=5` (abierto a Cowork, 0
> tokens). Por equipo: sus últimos N partes de partidos ANTERIORES (fecha
> estrictamente menor y otro fixture), cada uno con lo que se dijo
> (clasificación y % del EFE, pronóstico de la cadena, 1X2, marcador
> pronosticado, IE y ventana del TDE, la clase de su bloque que calculó el DTP
> del rival) y cómo salió (marcador, veredicto, `queP`, lección, población,
> cohorte y `cuarentena` si la hubo); `aciertoCiego` (solo ciega + PRE fuera
> de cuarentena, con la nota de muestra corta) y `leccionesVigentes` del
> equipo (pendientes o en revisión, de fechas anteriores). El prompt de
> Cowork lo lee ANTES de investigar (docs/COWORK.md, «ANTECEDENTES»). Lo
> diseñado abajo se respetó; la única diferencia es que el TDE viaja sin
> `acerto` (la ventana se comprueba en el veredicto de ese caso, no acá).

**Problema.** Cowork analiza Alianza vs Cristal hoy sin recordar que analizó a
Alianza hace dos fechas, que dijo "se echa entre el 75 y el 90" y que acertó.
Vuelve a investigar todo desde cero: tiempo y contexto tirados.

**Propuesta.** Un endpoint que devuelva, para los dos equipos del partido, lo
que el sistema ya dijo y cómo salió:

```
GET /analisis/cowork/antecedentes/{fixtureId}
```

```jsonc
{
  "a": {
    "equipo": "Alianza Lima",
    "partes": [                       // los últimos N, del más reciente atrás
      {"fixtureId": 123, "fecha": "2026-09-06", "rival": "Melgar",
       "clasificacion": "FORMADO", "porcentaje": 74,
       "pronostico": "domina por fuera y define antes del 70'",
       "veredicto": "fallo", "queP": "0-0, no generó por fuera",
       "leccion": "el bloque bajo de Melgar no es improvisado: vida útil 90'",
       "seleccion": "ciega", "tde": {"ie": 58, "acerto": false}}
    ],
    "aciertoCiego": {"n": 6, "acertados": 4, "brier": 0.19},
    "leccionesVigentes": ["…las lecciones sin aplicar que le tocan a este equipo…"]
  },
  "b": { … }
}
```

**Qué gana el prompt:** un paso nuevo antes del análisis —"lee tus
antecedentes"— y una orden explícita: *lo que ya dijiste y sigue siendo
cierto, no lo vuelvas a investigar; cítalo. Lo que fallaste, corrígelo y di
por qué.*

**Lo que NO debe pasar:** que los antecedentes contaminen la ceguera. Los
antecedentes son de **partidos anteriores ya cerrados**, nunca del partido que
se está analizando. Eso mantiene el caso nuevo en población `ciega`.

---

## B · El veredicto a las 12 horas

**Quién hace qué.** La misma regla de siempre (`docs/efe-dtp/COSTO_IA.md`): lo
que se puede calcular, se calcula.

| Lo calcula la app | Lo escribe Cowork |
|---|---|
| marcador final, ganador real | por qué falló |
| ¿acertó el 1X2 declarado? | qué mecanismo no vio |
| ¿acertó el marcador exacto? | la lección, en una frase accionable |
| error de la probabilidad (Brier por caso) | a qué skill le toca la lección |
| ¿el gol del tramo final cayó en la ventana del TDE? | si el caso es `ciego` o está contaminado |
| ¿reventó la burbuja de cada lado? (lo declarado antes y lo que pasó) | **si se cumplió el falsador** |
| los goles con su minuto y su lado (la evidencia) | |

**Corrección sobre la primera versión de este documento:** aquí decía que el
falsador lo verificaría el backend. Al construirlo quedó claro que no: el
falsador es prosa libre y un verificador que acierte el 80% de las veces es
peor que no tenerlo, porque nadie sabría de cuál 20% desconfiar. Lo que la app
hace es **servir la evidencia** con la que se comprueba —los goles con su
minuto y su lado— y dejar que Cowork declare `falsadorCumplido`.

**Qué pregunta ese booleano.** `falsadorCumplido` responde *¿ocurrió la
condición?*, no *¿acertó el falsador?*. Importa porque las dos lecturas dan
respuestas opuestas sobre el mismo partido, y solo una lleva información: si
`true` significara "el pronóstico se cayó", el campo repetiría
`unXDos.acerto`. Leído bien, la combinación **`true` + pronóstico acertado**
es el hallazgo más valioso del cierre: la condición que el analista eligió
como asesina del pronóstico ocurrió y el pronóstico sobrevivió, o sea que el
falsador estaba mal elegido. Es una lección sobre el falsador mismo, que es la
parte del método que menos se audita sola.

> **Precedente · Liga MX 1550964 (Santos–Juárez).** Falsador: «si Juárez marca
> primero, el pronóstico se cae por el D3 ❌ de Santos». Juárez marcó primero
> (penal al 54) y Santos remontó y ganó 2-1. Lo correcto es
> `falsadorCumplido: true` — la condición ocurrió — con el 1X2 acertado. En el
> primer cierre se declaró `false` leyendo el campo como "¿acertó el
> falsador?", que era la lectura que la doc de entonces permitía.

### El filtro de exclusión va ANTES de cualquier frecuencia

Una métrica de frecuencia que no filtra su población no es una métrica
optimista: es una métrica falsa. El TDE lo aprendió caro y quedó como regla del
proyecto.

La primera calibración del IE que escribí promedió los 21 casos ciegos y
cerrados del registro **sin excluir los `rama_abandonada`**, que las
disciplinas 24, 27 y 31 del skill sacan de toda métrica de frecuencia. Seis de
los 21 lo eran. Y uno de los dos «positivos» era TDE-030, cuya propia lección
en el CSV dice *«Excluida de toda metrica de frecuencia»* y cuyo `se_echo` es
*«repliegue voluntario sostenido desde el 25»* — que por la definición del
propio skill **no es una echada** sino un bloque bajo ejecutado.

Con el filtro puesto, el resultado no se suaviza, se endurece:

| | sin filtrar (mal) | filtrado (bien) |
|---|---|---|
| n | 23 | **8** |
| positivos | 2 | **1** |
| banda 3-5 | | 1 de 5 |
| banda 5-7 | | **0 de 1** |
| banda 7-8.5 | | **0 de 2** |

*(sobre el registro de 35 casos, TDE-001…048, canonizado por el autor del skill)*

La conclusión cambia de «casi plana» a **nula o invertida**: el único positivo
cae en la banda más baja. Y el remate: TDE-005 está medido con el esquema
viejo de 4 indicadores, así que **en el esquema vigente de 6 no hay ni un
positivo ciego**. Un semáforo sobre eso no congelaría ruido — congelaría una
escala calibrada con cero observaciones.

Por eso el número no se escribe a mano: `scripts/calibrar-tde.py` lo recalcula
desde el registro, aplica el filtro, avisa si una columna tiene varias
redacciones para el mismo valor, y **falla si el backend se desalinea**.

> **Regla.** Toda frecuencia que salga del registro filtra primero por
> `seleccion` y por `clase_caso`, y **declara el filtro que aplicó** junto al
> número. Un porcentaje sin su población al lado no se publica.

### Dos columnas de modo, y la que importa no era la que filtré

`modo_evaluacion` (PRE/COND/RETRO) dice **con qué escala** se puntuó. `modo`
(PRE/RETRO/DECLARADO/CERRADO) dice **cuándo se escribió el análisis**. Filtré
por la primera. De los 17 «computables», **nueve tenían `modo = RETRO`**: se
puntuaron con el partido ya jugado.

`seleccion = ciega` garantiza que el caso no se eligió *porque* pasara algo. No
garantiza que se puntuara a ciegas. Es la misma distinción que ya hacíamos para
`post_resultado` — **allí falla el partido, acá falla el analista** — y la
estábamos aplicando a una y no a la otra.

Con la exclusión puesta, n baja de 17 a 8 y la brecha pasa de **siete veces a
cuatro** (48.9% declarado contra 12.5% observado). Corrijo lo que publiqué: dije
que las siete veces «no dependían del único positivo», y sí dependían — de nueve
filas retrospectivas que inflaban el denominador de no-echadas.

**La prueba de que la exclusión no es prudencia genérica está en la vía 2**, que
sí tiene positivos de sobra:

| ISE | n | declara | observa | skill score |
|---|---|---|---|---|
| con RETRO | 14 | 47.4% | 64.3% | **+0.36** |
| sin RETRO | 6 | 50.0% | 83.3% | **−0.60** |

El ISE parece predecir **solo en las filas puntuadas después del partido**. Eso
no es señal: es la firma de la contaminación. Con los RETRO dentro, el módulo se
autoacredita una capacidad que no tiene.

> **Regla.** Una métrica de frecuencia filtra por las DOS columnas de modo. Una
> fila escrita después del partido no entra en ninguna medida de capacidad
> predictiva, aunque el caso se haya elegido a ciegas.

### Las tablas de probabilidad quedan suspendidas

No se recalibran: se **apagan**. Las dos vías fallan en **direcciones
opuestas** —la 1 sobreestima unas 4×, la 2 subestima— así que no existe un
factor de corrección global; arreglar una rompería la otra. Y con n=8 y un
positivo, cualquier tabla ajustada a esta muestra sería ruido con autoridad.

Se apaga también el **`riesgo_compuesto`**, porque es el producto literal de las
tres probabilidades (TDE-001: 0.55 × 0.20 × 0.30 = 3.3) y hereda la inflación
entera. Suspender las tablas y seguir publicando su producto habría sido no
suspender nada.

Lo que el módulo sigue publicando: el IE, el ISE, su **tramo ordinal**, el tipo
modal, la ventana, las compuertas operadas y los indicadores que sostienen la
lectura. Se reactivan con las tres condiciones del alta del semáforo.

### El dato canónico vive donde cambia, no donde se empaqueta

El registro del TDE se desincronizó **tres veces** con el paquete del skill, y
ninguna de las tres se habría detectado contando filas. La causa no es descuido:
el registro cambia **por partido** y el skill se reempaqueta **por versión**.
Empaquetar un dato de cadencia diaria dentro de un artefacto de cadencia semanal
es divergencia garantizada.

> **Regla.** El dato que cambia con los partidos vive en el repo; el artefacto
> que cambia por decisión (rúbrica, referencias) viaja con el skill. Y el estado
> vigente se identifica por **sha256**, no por conteo de filas ni por fecha —
> dos de las tres desincronizaciones no cambiaban el conteo.

`scripts/calibrar-tde.py` verifica el sha en cada corrida. El detalle —qué está
perdido, qué es hueco declarado, y las tres poblaciones mezcladas en la columna
de recomputo— está en `docs/skills/teorema-del-echado/REGISTRO.md`.

### Una condición que no se puede satisfacer es un candado

El alta del semáforo del TDE exigía que **todos** los positivos estuvieran
expresados en el esquema vigente. Suena impecable, y era inalcanzable: el único
positivo ciego del registro es de 2026 y sus bloques **no son promedios posibles
de una rúbrica de indicadores** con ningún denominador. Se puntuó con escala
continua. No hay nada que reexpresar, así que la condición daba falso para
siempre.

La regla que quedó distingue dos cosas que parecen iguales:

> **Una condición de calidad se bloquea por lo que se puede arreglar, no por lo
> que no.** Un caso al que le falta una decisión bloquea; uno estructuralmente
> inexpresable **sale del conteo**. Si no, la condición deja de medir calidad y
> pasa a ser un candado con buena redacción.

El caso inexpresable no se borra ni se disimula: se marca (`pre_rubrica`), se
explica por qué, y se declara que no cuenta. Lo que NO se hace es repuntuarlo
hoy con el resultado a la vista para que «entre»: eso produciría una fila
`post_resultado`, excluida de toda métrica el día que entrara.

### Un Brier sin línea de base no dice nada

Recalculado con los dos filtros puestos, el Brier del TDE da **0.3051** sobre
8 casos. Pero el número suelto engaña en las dos direcciones, y la comparación
que importa es otra: **predecir siempre la tasa base saca 0.1094**. Es decir que
hoy las probabilidades del módulo **restan en vez de sumar** (skill −1.79).

Dos honestidades sobre ese −3.14, porque el dato se puede sobreleer:

- **Lo robusto es la brecha, no el skill score.** La p media declarada es
  48.9% y lo observado 12.5%: unas **cuatro veces**.
- **El skill score con un positivo es ruidoso**, y la línea de base usa la tasa
  real, que es información que no se tenía al predecir. No sirve para condenar
  el método: sirve para decir que **el mapeo IE → probabilidad está roto**, que
  es justo lo que la disciplina 20 del skill ya declaraba.

Lo que esto NO dice: que el IE no ordene el riesgo. Eso sigue sin testearse,
porque para testear un ordenamiento hacen falta positivos arriba y hay cero.
Por eso el alta del semáforo pide las tres condiciones y no solo el N.

> **Regla.** Un Brier se publica siempre con el Brier de su línea de base al
> lado. Sin eso, un 0.23 puede leerse como bueno o como catastrófico según a
> quién le convenga.

Lo que sí se comprueba solo es **la ventana del TDE**, y por una razón
concreta: `"75-90'"` son dos números y un gol tiene un minuto. Se cuentan solo
los goles CONTRA el equipo evaluado —la echada se observa en lo que recibe— y
si la ficha de eventos no está capturada, `golEnVentana` vuelve `null` en vez
de `false`: no comprobable no es lo mismo que no ocurrido.

El índice es **por equipo**, así que la comprobación también: `objetivo.tde`
trae `bloques`, uno por lado declarado, cada uno con su ventana y su veredicto.
Mientras el parte guardó un solo TDE, el del otro equipo vivía en `notas` y
**no entraba en ninguna métrica** — ni siquiera se sabía que faltaba.

**Contrato propuesto:**

```
GET  /analisis/cowork/veredictos/pendientes
     → partidos con parte, terminados hace >12h y sin veredicto.
       Es lo que dispara la corrida de Cowork: no hace falta que nadie
       se acuerde.

POST /analisis/cowork/{fixtureId}/veredicto
{
  "seleccion": "ciega",
  "modoEvaluacion": "PRE",
  "porLado": {
    "a": {"veredicto": "fallo", "queP": "…", "leccion": "…",
          "skill": "teorema-del-echado"},
    "b": {"veredicto": "acierto", "queP": "…", "leccion": ""}
  },
  "notas": ""
}
→ devuelve el veredicto CON la parte calculada ya rellena, para que Cowork
  vea el marcador y el Brier que le salieron sin tener que pedirlos.
```

El veredicto entra en `cadena_dtp.registro` (el hueco que ya existe). La
lección viaja dentro del veredicto con su `skill`; la fase C la indexará desde
ahí en vez de pedir una tabla a medio construir hoy.

**Construido así** (`backend/analisis/veredicto.py` + `parte.py`):

- El objetivo se **recalcula en cada lectura**, nunca se sella. Si la ingesta
  corrige un marcador o llega la ficha de eventos que faltaba, la próxima
  lectura trae el cálculo bueno sin que nadie reescriba el juicio.
- El Brier es de **tres resultados** (Σ(pᵢ−oᵢ)², 0 perfecto, 2 máximo) y lo
  dice en su propio campo `escala`. El objetivo `< 0.20` del TDE es un Brier
  **binario**: no están en la misma escala y ponerlos en la misma tabla sería
  un error de lectura.
- Un reparto que no suma 100 se normaliza. Un 1X2 con dos selecciones
  empatadas en el máximo **no cuenta acierto**: se declara en `nota` en vez de
  desempatarse a ojo.
- Un marcador de un partido en curso se sirve igual (para eso existe `COND`)
  pero viene marcado `terminado: false`.

**Un bug que el diseño predijo y los tests destaparon:** re-depositar el parte
después de cerrar el caso borraba el veredicto de la cadena, porque la
apertura escribía un registro vacío encima. Ahora el re-depósito conserva el
veredicto **y** el pronóstico ya declarado, y delata en `cadenaIgnorada` que
llegó uno distinto. Es exactamente el hindsight que la fase B existe para
impedir, entrando por la puerta de atrás.

**Cuidado con el orden.** Si Cowork escribe el veredicto *antes* de consultar
el marcador, el caso es PRE. Si consulta el marcador y después puntúa, es
`post_resultado` y no acredita. El endpoint no puede saberlo solo: **lo
declara Cowork y el prompt tiene que decirlo con todas las letras.**

### El reventón de la burbuja: observación, no veredicto

El parte lleva, por lado, la burbuja abierta y su riesgo de reventón
(`lecturaSad.reventonCalculado`, `docs/REVENTON.md`), pero ese bloque se
recalcula al leer: después del partido ya no dice lo que decía antes. Por eso
`objetivo.reventon` reconstruye lo **declarado** con la vista «al día del
partido» (§9 del doc: historia estrictamente anterior al fixture y el fixture
como próximo, la misma construcción anti-hindsight del backtest; da los mismos
números que `GET /equipos/{id}/burbujas?antesDe=`) y pone al lado lo
**observado**: si la K fusionada de ese partido cerró la burbuja, con la
misma función que detecta los reventones en la historia.

Lo que NO hace es emitir acierto o fallo. Un riesgo alto que revienta no es un
acierto y uno bajo que revienta no es un fallo: el riesgo es una **tasa**, y
una tasa se juzga en conjunto. Eso vive en las lecciones:
`acreditables.reventon` trae, solo sobre los casos `ciega` + `PRE`, la tasa de
reventón observada por nivel de riesgo con el rango que el backtest dejó para
ese nivel (`docs/REVENTON.md` §8) y `dentroDelBacktest`, que solo se calcula
con `n ≥ 10` por nivel. Un nivel fuera del rango con n suficiente sale en
`fueraDelBacktest` y pone `revisionAbierta`: eso **abre** la revisión de los
puntos del riesgo, y nada más —los puntos se mueven con el backtest a la vista,
en los dos lados y en los vectores dorados, como dice `CLAUDE.md`—. Las
burbujas que tenían la alerta K-EXTREMO se cuentan aparte, porque la pregunta
ahí es otra: el backtest dice que la K no adelanta el reventón, y esto lo mira
en producción.

Sin burbuja abierta antes del partido no hay nada que observar
(`sinBurbuja`); si el pipeline aún no calculó la constante del partido, el
lado sale `comprobable: false` y no cuenta. Lo que sigue siendo de Cowork es
el juicio sobre su propia línea: si recomendó no seguir la racha y la racha
siguió, eso lo escribe quien cierra el caso.

### La salvedad: `mancha`

Los tres nombres de población describen **cuánto se sabía del resultado** al
escribir. Un parte retocado con el partido en el minuto 2 y 0-0 no es
`post_resultado`: no había resultado que mirar. Forzarlo a esa etiqueta no
sería prudencia, sería mentir en la otra dirección — el caso quedaría archivado
como «puntuado sabiendo el marcador», que es falso, y la etiqueta perdería
significado para todos los demás casos.

Para eso está `mancha`: una frase que viaja **con el caso que sí acredita**,
en campo propio y no en la prosa de `notas`. No cambia `seleccion` ni
`acredita`; deja constancia de lo que hubo, con nombre y apellido, para que una
auditoría dentro de seis meses la encuentre filtrando y no leyendo. La pantalla
la marca **CON SALVEDAD** al lado de la etiqueta de población.

Precedente, y la regla que deja:

> **Liga MX · 1550964 (Santos–Juárez, 2026-09-14).** El parte se reescribió
> entre el minuto 0 y el 4 con el partido rodando; el marcador estaba 0-0 y no
> se miró, y el `pronostico` quedó intacto en 62/24/14 todo el tiempo.
> Declarado **`ciega` + PRE** —decisión del dueño del proyecto— con la salvedad
> escrita. La regla de la duda («si dudás entre ciega y post_resultado, es
> post_resultado») **sigue en pie para los casos donde había resultado que
> mirar**; no se aplica cuando el partido no había producido ninguno.

Que la salvedad sea barata no la vuelve gratis: si un caso necesita `mancha`
para sostenerse, lo que hay que arreglar es el proceso que lo ensució, no la
etiqueta. Un `ciega` con salvedad cada dos casos es una métrica que ya no
significa nada.

---

## C · Las lecciones, acumuladas por skill — **HECHA**

`backend/analisis/lecciones.py` · `GET /analisis/cowork/lecciones` ·
`POST /analisis/cowork/lecciones/{clave}` · sección **Aprendizaje**.

### Se implementó con UNA diferencia deliberada respecto de este diseño

El diseño de abajo proponía una tabla con el TEXTO de la lección adentro. Eso
crea dos copias del mismo dato, y el día que alguien corrige un veredicto una de
las dos se queda vieja **sin que nadie se entere** — que es la forma más cara de
perder información y la que venimos arreglando en todo el resto del proyecto.

Lo implementado: el **contenido** de cada lección se DERIVA del veredicto al
leer (como el marcador y el timeline), y se guarda aparte **solo el estado**,
que es lo único que no se puede derivar de nada:

```sql
CREATE TABLE leccion_estado (
    clave TEXT PRIMARY KEY,          -- fixtureId:lado
    estado TEXT NOT NULL DEFAULT 'pendiente',
    aplicada_en TEXT,                -- versión del skill donde entró
    nota TEXT,
    actualizado_en TEXT NOT NULL
);
```

Tres reglas que quedaron en el código, no en la buena voluntad de quien lea:

- **`aplicada` exige `aplicadaEn`.** Una lección aplicada sin la versión donde
  entró no se puede auditar seis meses después, y este es el momento más barato
  para anotarlo.
- **`puedeMoverNumeros` viaja con cada lección.** Solo un caso `ciega`+`PRE`
  puede sostener un cambio de peso; el resto fija rúbrica. La distinción la
  lleva el dato y se pinta pegada a la lección, no en una nota al pie.
- **El sesgo de atribución se declara.** Quien cierra el caso nombra el skill
  sobre todo cuando algo falla: los conteos por skill NO son una tasa de
  acierto, y la pantalla lo dice antes de mostrarlos. La tasa que sí se publica
  sale de TODOS los lados de la población ciega, con su `n` al lado.
- **Cowork no puede mover estados.** `POST /analisis/cowork/lecciones/{clave}`
  no está en la lista de permitidos del token acotado: el agente lee sus
  lecciones, pero declarar aplicada la suya es del usuario.

### El diseño original, para referencia

Tabla propuesta en su momento (la capa de análisis sigue siendo la única que
escribe en `efe.db`):

```sql
CREATE TABLE lecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill TEXT NOT NULL,            -- teorema-del-echado, efe-clasificador, …
    fixture_id INTEGER,
    equipo TEXT,
    fecha TEXT,
    veredicto TEXT,                 -- acierto | parcial | fallo
    seleccion TEXT,                 -- ciega | por_resultado | post_resultado
    modo_evaluacion TEXT,           -- PRE | COND
    que_fallo TEXT,
    leccion TEXT NOT NULL,
    regla_tocada TEXT,              -- "escala de P(echada)", "bloque B6", …
    estado TEXT DEFAULT 'pendiente',-- pendiente | en_revision | aplicada | descartada
    aplicada_en TEXT,               -- versión del skill donde entró
    creado_en TEXT NOT NULL
);
```

`estado` es lo que evita el bucle infinito: una lección aplicada deja de
contar para el disparador y queda de historia.

```
GET  /analisis/cowork/lecciones?skill=&estado=
POST /analisis/cowork/lecciones/{id}   → cambiar estado (lo hace el usuario)
```

**En el frontend:** una sección **Aprendizaje** con, por skill:

- tasa de acierto **sobre la población ciega**, con el `n` a la vista y las
  otras poblaciones contadas aparte (nunca sumadas);
- el Brier cuando haya probabilidades declaradas, con su objetivo del skill;
- las lecciones pendientes, con el partido del que salieron;
- y un semáforo honesto: *"2 ciegos cerrados · el skill pide 5"*.

Y en la pantalla del partido, el eslabón cerrado: pronóstico → qué pasó →
veredicto → lección. Eso ya sabe pintarlo `DtpPizarra`.

---

## C-bis · Cuarentena y cohortes: qué casos cuentan — **HECHA**

Dos filtros que la población no cubre. Los tres nombres de población dicen
**cuánto se sabía del resultado** al escribir; no dicen si el insumo estaba
roto. Los partes de la primera semana se hicieron con el DT viejo en 17 de 22
equipos, el TDE sin nivel en diez partes y la agenda sin padrón: son `ciega`
por etiqueta y contaminados por proceso, y hasta el 19/09 pesaban igual que
uno de hoy.

**Cuarentena** (`POST/DELETE /analisis/cowork/{id}/cuarentena`, token
maestro; `parte_cowork.cuarentena_json`). Una marca por caso, con motivo
obligatorio. Un caso en cuarentena sale de todas las métricas, se cuenta en
su propia población y sus lecciones se listan aparte (`enCuarentena`) sin
poder mover números ni fijar rúbrica. La regla dura, y la razón de que exista
`veredictoAlPoner`:

> **Cuarentena POR CRITERIO, NUNCA POR RESULTADO.** Se pone por lo que le
> faltaba al parte antes del pitazo («DT viejo», «TDE sin nivel», «rodaje»),
> no porque el veredicto salió fallo. Si no, es la forma elegante de borrar
> los fallos y la métrica deja de significar. Por eso se guarda el veredicto
> que tenía el caso al ponerla: una auditoría ve de un vistazo si se puso
> después de saber cómo terminó.

**Cuarentena automática: sin DT no hay caso.** El bloque A, F3 y S1 se
apoyan en la continuidad del entrenador. Un parte con `dt` «sin establecer»
(o vacío, en los de rodaje) en un lado se hizo sin ese insumo: `lecciones.py`
lo pone en cuarentena solo, con motivo «automática: sin DT declarado (lado
a)», `cuarentenaAutomatica: true` y sin botón de quitar. Se levanta
re-depositando el parte con el DT (`parte.sin_dt`).

**Cuarentena automática: DT equivocado tampoco** (23/09/2026). El error de
la alineación rancia (Santa Fe–Cali, la Roma, arreglado el 22/09) no dejaba el
DT vacío: lo dejaba EQUIVOCADO, y esos partes contaban como buenos.
`parte.dt_equivocado` compara el DT que declaró el parte con el que se sentó en
el banco de ESE partido (la alineación que capturó la ficha); si no comparten
ni un apellido (`mismo_dt`: «R. Dudamel» y «Rafael Dudamel» casan, «Hernán
Torres Oliveros» y «H. Torres» también), el caso va a cuarentena automática
con los dos nombres en el motivo. Es criterio de INSUMO —qué traía el parte
antes del pitazo—, comprobado después solo porque el banco se conoce
entonces; no mira el resultado. Sin alineación capturada (Colombia, Uruguay,
ficha que aún no corrió) o sin apellido comparable («DT A») no se marca nada:
ahí la cuarentena es a mano. Se levanta re-depositando con el DT del banco.

**Cohortes** (`parte_cowork.cohorte`, `parte.COHORTE` / `COHORTES`). La
época del proceso se sella **al depositar** y un re-depósito no la cambia (un
parte viejo re-depositado hoy sigue siendo de su época; lo que ya existía sin
marca es `rodaje`). `GET /analisis/cowork/lecciones?cohorte=vigente|<clave>|`
calcula las métricas y los conteos por skill **solo sobre la cohorte elegida**;
`cohortes` viaja siempre entero para que se vea cuánto queda fuera. La pantalla
arranca en la vigente. Cuando cambie algo que invalide los casos anteriores
(otra regla de DT, otro contrato del TDE), se abre una cohorte nueva en
`COHORTES` con su descripción, y las anteriores quedan como referencia: enseñan,
no calibran.

Cohortes abiertas: `rodaje` (antes del 19/09) · `c2-2026-09-19` (con la
alineación rancia todavía ganándole a `/coachs`: referencia) ·
**`c3-2026-09-23`, la vigente**: DT de la alineación solo si es de los últimos 3
partidos, cuarentena automática por DT equivocado y aviso CERCA DEL EXTREMO.
Arranca vacía; se llena con lo que se deposite DESPUÉS del despliegue.

**El intervalo, no el punto.** La tabla de reventón por nivel decía FUERA
con 6 de 21 (29 %) contra un backtest de 42-47 %. El intervalo de Wilson al
95 % de esa observación es [14 %, 50 %]: es ruido. Ahora `porNivel` trae
`intervalo` y `lectura`, y FUERA es que el rango del backtest **no toca el
intervalo**, con n ≥ 10. Con 46 burbujas contra 171 mil del backtest, lo raro
sería que el punto cayera dentro.

## D · La revisión: del montón de lecciones al `.zip` — **HECHA** (24/09/2026)

> **Cómo quedó**: `lecciones.revision(skill)` → `GET /analisis/cowork/revision/{skill}`
> (abierto a Cowork en lectura: es lo que toma para redactar el diff) y el
> botón **Ver dossier** de cada skill en la sección Aprendizaje. Trae las
> lecciones abiertas agrupadas por la regla que tocan (`porRegla`), cuántas
> son acreditables y cuántas piden mover un número (y cuántas de esas pueden
> sostenerlo), las métricas ciegas SOLO de los casos del skill contra su
> listón, `pidenMoverSinPoder`, los casos en cuarentena, la **versión
> vigente** del snapshot en `docs/skills/` (la que va en `aplicadaEn`) y una
> `lectura` CALCULADA: sin acreditables, la revisión solo fija rúbrica; con
> acreditables que no piden mover nada, también; con el listón sin cumplir, el
> cambio de peso espera. «Abrir la revisión» (`POST …/abrir`, solo maestro)
> pasa las pendientes a `en_revision` y deja constancia; una revisión sigue
> abierta mientras tenga lecciones en revisión. Nada de esto mueve un peso ni
> marca `aplicada`.

> **Insumo nuevo para el dossier (22/09/2026, `backend/analisis/modo_fallo.py`,
> `docs/JEV.md`)**: al cerrar cada veredicto, Jev etiqueta el modo de fallo del
> lado fallado o parcial en una taxonomía cerrada —insumo · lectura_efe · tde ·
> reventon · mercado · imprevisto · varianza · no_lo_dice— y dice si la lección
> pide mover un número del skill. Viaja en cada lección (`modoFallo`,
> `proponeMoverNumero`) y agrupado en `porModoFallo` (global y por skill), con
> `pidenMoverSinPoder`: lecciones de casos contaminados o en cuarentena que
> proponen mover un peso. Es lo que permite que «4 fallos» se lean como «4
> imprevistos» o «4 lecturas del EFE», que no piden lo mismo. No toca la
> población, ninguna métrica ni el estado de la lección: agrupa, no autoriza.

**Disparador:** 4 partidos fallados con lección pendiente para un mismo skill.
La app lo detecta y lo marca; **no** escribe nada ni genera nada.

**Dossier** (`GET /analisis/cowork/revision/{skill}`): las lecciones
pendientes, los casos con su población, las métricas ciegas frente al listón
del propio skill, y qué regla concreta toca cada lección.

**Flujo, con el usuario en el medio:**

```
  app  → "4 fallos en teorema-del-echado (2 ciegos cerrados; el skill pide 5)"
  vos  → abrís el dossier y decidís
  vos  → "autorizado, armá la versión nueva"
  Cowork → toma el skill vigente + el dossier, redacta el diff, arma el .zip
  vos  → lo instalás en la cuenta
  app  → marca esas lecciones `aplicada` con la versión donde entraron
```

Tres cosas que **no** van a pasar, y conviene que estén escritas:

- La app no genera el `.zip` sola ni por un cron.
- Cowork no toca su propio skill: propone, y hasta la autorización el archivo
  no se mueve.
- Una lección de un caso contaminado puede **fijar rúbrica** (aclarar cómo se
  aplica una regla) pero **no mueve un número**. Esa distinción la lleva el
  dossier, no el criterio de quien lo lea ese día.

---

## Orden sugerido

| Fase | Qué desbloquea | Tamaño |
|---|---|---|
| **B** · veredicto + cálculo objetivo | es el que genera el dato; sin él las demás no tienen de qué vivir | mediano |
| **C** · lecciones + pantalla | hace visible lo acumulado y cierra la cadena en la pantalla de Equipo | mediano |
| **A** · antecedentes | ahorra tiempo de Cowork; necesita que B lleve un tiempo corriendo para tener qué mostrar | pequeño |
| **D** · dossier de revisión | lo último: sin lecciones acumuladas no hay nada que revisar | pequeño |

Empezar por B tiene una ventaja concreta: **desde el primer partido validado
el sistema empieza a acumular casos ciegos**, que es justo lo que a los skills
les falta. Aunque las fases C y D tarden, el dato no se pierde.

## Lo que queda por decidir

- **El timeline no tiene registro propio.** ¿Se le mide algo (si los eventos
  institucionales que trajo eran ciertos y relevantes) o se acepta que es un
  skill de contexto y no de pronóstico? Se inclina a lo segundo.
- **Qué es "acierto" para el EFE.** El EFE no pronostica un resultado:
  clasifica un estado. Su validación es la del skill (el caso numerado que
  ata una corrección a un partido), no un acierto/fallo de marcador. Meterlo
  en la misma tasa que el 1X2 sería comparar cosas distintas.
- **Las 12 horas.** Con partidos de noche, 12h cae a la mañana siguiente y
  está bien. Con un partido de mediodía cae de madrugada. ¿Se fija una hora
  del día en vez de un delta? La lista de pendientes lo resuelve igual: lo que
  no se validó hoy sigue ahí mañana.
