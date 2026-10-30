# Reventón de la burbuja · cuándo la K vuelve a cero

> Guía calculada, **no probabilidad**. Nadie puede decir con certeza cuándo una
> K deja de acumular; sí se puede mirar cuánto aguantó este equipo cada vez
> antes de reventar y comparar la burbuja de hoy con eso. Sirve sobre todo
> para saber **cuándo no apostar**.

Dueño de la matemática: `backend/analisis/burbuja.py` (función pura, sin DB).
Espejo TS para el mock y los tests: `src/lib/burbuja.ts`. Los dos se verifican
contra los **mismos vectores dorados** (`scripts/casos_burbuja.json`):

```bash
python -m backend.test_burbuja     # backend
npm run test:burbuja               # espejo TS
```

Contrato: `GET /equipos/{id}/burbujas` (`BurbujasEquipo` en `docs/openapi.yaml`).
Abierto al token de Cowork como todo `GET /equipos/*`: cero requests a
API-Football y cero tokens. Pantalla: tarjeta **Reventón · guía** en Burbujas
(bajo cada gráfica de K) y en la página de Equipo; sobre la gráfica de K va
la línea punteada de la mediana con la que revienta.

## 1. Qué es una burbuja y qué es un reventón

Sobre la **K de resultado fusionada** (`k = k⁺ + k⁻`, §3.3/§4.2 del motor),
por familia `total · local · visita`:

- Una **burbuja** es una racha de la K con el mismo signo.
- **Revienta** cuando la K vuelve a 0 (empate, o el resultado contrario sin
  acumular) o cuando **cambia de signo en el mismo partido** (una derrota que
  arranca la racha negativa cierra la positiva y abre la contraria).
- El partido que la revienta viaja con su rival, el **nivel del rival**, la
  condición y el marcador. De cada burbuja cerrada se guardan: signo,
  **partidos** que duró y **K pico** (la |K| máxima que alcanzó).
- `local`/`visita` solo miran los partidos de su condición: los de la otra
  conservan el valor y **no cuentan** como partidos de la racha.

Las K de goles (`k_goles_*`) quedan **fuera a propósito** por ahora: sí forman
burbujas y sí se podría decir cuándo un equipo deja de anotar o vuelve a
hacerlo, pero eso se agrega cuando toque, sin saturar a Cowork.

## 2. Lo que se calcula por signo

Para las burbujas cerradas de cada signo (`historial.positivo` /
`historial.negativo`): **media, mediana y moda** de la K pico, de los partidos
y del nivel del rival que la reventó, más mín y máx.

- La moda se busca sobre valores redondeados (K a entero, partidos exacto,
  nivel a un decimal). Si nada se repite, **no hay moda** (`null`), no se
  inventa una. En empate se toma la **menor**: avisar antes es más barato que
  avisar tarde.
- Un equipo con dos victorias y K 10 y otro con seis partidos y la misma K
  son dos historias distintas: por eso viajan las tres cosas, no solo la K.

## 3. La burbuja abierta hoy

`actual`: signo, K con signo, partidos, K pico, desde cuándo, y si el próximo
partido **mueve** esta familia (`aplicaAlProximo`: total siempre; local solo si
el próximo es de local; visita ídem).

`posicion`: percentil de la K actual y de la racha actual entre los reventones
de su signo, y `kSobreMediana` (K actual / mediana de K pico).

`rival`: el nivel del próximo rival frente a la mediana del nivel con el que
suele reventar. **En zona** = burbuja positiva: `nivel ≥ mediana − 0.15`;
burbuja negativa (racha de derrotas): `nivel ≤ mediana + 0.15` (la racha
de derrotas se corta ante rivales flojos, así que la lectura es espejo).
Sin próximo, o si la familia no se mueve en él, `rival` es `null` y el motivo
lo dice.

## 4. Qué constante manda

**La total, siempre.** La hipótesis original era que a nivel alto o bajo
(bin ≥ 7 o ≤ 2) mandan las globales y a nivel medio las específicas de la
condición del próximo. El backtest real (§8) no la confirmó: la familia total
separa más que local/visita en nivel medio (0.25 vs 0.24) y en extremos
(0.30 vs 0.26), y agrupar por «manda / no manda» según la regla da lo mismo
(0.266 vs 0.266). La lectura más simple es que local y visita tienen la mitad
de partidos y sus medianas son más ruidosas.

La regla viaja igual en `mandan.reglaNivel` (con `confirmada: false`) para
verla, no para decidir. La pantalla marca con ★ la total; local y visita se
ven como detalle.

## 5. Riesgo de reventón (puntos con motivo, calibrados)

Solo con burbuja abierta y reventones previos del mismo signo. Cada punto
viaja con su frase en `riesgo.motivos`. Los puntos salen de la regresión
logística del backtest real (§8): un punto por cada 0.25 de log-odds.

| condición | coef. | pts |
|---|---|---|
| K actual frente a la mediana / máximo de K pico | −0.15 / −0.15 | **0** (se describe, no puntúa) |
| racha ≥ mediana de partidos | +0.32 | +1 |
| próximo rival **en zona** (±0.15 de la mediana con la que revienta) | +0.82 | +3 |
| próximo rival **fuerte** (≥ 0.15 por encima, en la dirección del riesgo) | +1.18 | +5 |
| próximo rival **muy fuerte** (≥ 0.45) | +1.86 | +7 |

La «dirección del riesgo» es: para la burbuja positiva, rival más fuerte que
la mediana; para la negativa (racha de derrotas), rival más flojo. El tramo
viaja en `rival.tramo` (`lejos · zona · fuerte · muy fuerte`).

`nivel`: 0–1 **bajo** · 2–3 **medio** · 4–5 **alto** · ≥ 6 **muy alto**. Con
los datos reales eso da, aproximadamente: bajo 42–47 % de reventón, medio
≈ 61 %, alto 67–69 %, muy alto 75–85 % (tasa base 60 %). Sin reventones
previos del signo: **sin base** (se dice; no se inventa un número).

## 6. Confianza (aparte del riesgo)

La **estabilidad** no mueve el riesgo: mueve cuánto vale la guía. Si el DT es
nuevo o el plantel cambió, la historia de K es de *otro* equipo.

- Muestra: `< 3` reventones del signo → **baja** · `< 6` → **media** · si no
  **alta**.
- Estabilidad (de la plantilla del contrato, `docs/JUGADORES.md`):
  - DT con menos de **90 días** → `inestable`.
  - `llegadas + salidas` CON MINUTOS de la ventana (120 días): ≥ 20 →
    `inestable`; ≥ 10 → `en transición` (23/10/2026, incidencias 43: se
    cuentan solo los que jugaron en el primer equipo —la llegada, después de
    llegar— y el total en papeles viaja en `enPapeles`; los cortes eran 6 y 3
    sobre el conteo en papeles y dejaban 0 estables de 82 equipos de la
    agenda. Primer corte, sin backtest).
  - ≥ 5 bajas → `en transición`. Cuentan solo las de **señal**: una baja del
    flag «Missing Fixture» leída como ruido (media plantilla marcada,
    `docs/JUGADORES.md`) no es una baja, en los dos lados (Python y TS).
  - Plantilla sin capturar → `sin dato`.
  - Plantilla con **≥ 30 días** de edad: se avisa que el DT y las bajas pueden
    estar viejos (deuda 2 de `CLAUDE.md`).
- Tope por estabilidad: `inestable` → baja · `en transición` / `sin dato` →
  media. Nunca sube por encima de lo que da la muestra.
- **Dueños / organización que maneja el club** no está en la base: viaja en
  `estabilidad.sinDato`, declarado, jamás rellenado a ojo.

## 7. Cómo leerlo (y cómo no)

- **Riesgo alto + confianza alta**: terreno conocido, la burbuja está donde
  suele reventar. Es el caso claro de no apostar a que sigue.
- **Riesgo alto + confianza baja**: la burbuja es grande pero el equipo
  cambió; la historia no sirve de regla. Cuidado en los dos sentidos.
- **Riesgo bajo**: la K está por debajo de lo que este equipo suele aguantar.
  No es «va a seguir»: es «no hay señal de reventón en su historia».
- Un reventón que ocurre con riesgo bajo no es un fallo del cálculo: es lo que
  la guía no puede ver (lesión, expulsión, un rival que jugó mejor de su nivel).
- **Riesgo bajo + EXTREMO** (§10): la K está en su récord y el modelo no lo
  cuenta porque la K no adelanta el reventón. Igual no se carga la apuesta a
  que siga: si revienta, revienta desde lo más alto.

## 8. Backtest hacia atrás (calibrar y confirmar)

`backend/backtest_burbuja.py` recorre la historia de cada equipo y, en cada
partido donde había una burbuja abierta, reconstruye la guía **solo con las
filas anteriores** (el rival real de ese partido hace de «próximo», el bin
sale del último nivel previo, la estabilidad va sin dato) y la compara con lo
que pasó: reventó en ese partido, o dentro de `--horizonte` partidos de la
condición.

```bash
python -m backend.backtest_burbuja --padron           # las ligas importantes (padrón único: extractor.ligas_vivo())
python -m backend.backtest_burbuja                    # todos los equipos con ≥ 12 filas
python -m backend.backtest_burbuja --horizonte 2 --liga 281 --json salida.json
python -m backend.test_backtest_burbuja               # anti-fuga y conteos, sobre la demo
```

Corre **donde viven las `.db`**: en tu PC junto a las cuatro bases (o con
`SAD_DATA_DIR`), o en el servidor por `GET /analisis/burbujas/backtest`
(`padron`, `horizonte`, `muestra`, `liga`, `minFilas`) con el **token
maestro**. No está abierto a Cowork a propósito: es calibración de la guía,
no un dato del parte, y Cowork no tiene que gastar una sesión en algo que
se calcula solo. Lo que Cowork SÍ lee es la guía de cada equipo
(`GET /equipos/{id}/burbujas`) al escribir el parte.

Con `--padron` la historia previa de cada equipo (su K y sus reventones) usa
**todos** sus partidos, como en la app; solo se **evalúan** los partidos de las
ligas del padrón. La salida trae `ligasEvaluadas` y el desglose por liga para
que se vea qué se calibró y dónde la separación es ruido por n chico.

El endpoint corre el backtest en un **subproceso** (`backend.backtest_burbuja
--json`), no en el proceso web: cargar 171k burbujas dentro de la API dejó
al backend en 7 GB de RAM permanentes (Railway los cobra cada hora,
`docs/DESPLIEGUE.md`). El subproceso y el CLI van con `SAD_SIN_HILOS=1` para
que importar `backend.app` no arranque ingestas ni backfills.

### `--calibrar` (o `calibrar=true` en el endpoint)

Ajusta una **regresión logística** sobre las señales de la guía, con el rival
graduado por distancia a la mediana de reventón (lejos = referencia · en zona
· fuerte ≥ 0.15 · muy fuerte ≥ 0.45). Como las señales son binarias, se agrupa
por patrón (≤ 64 celdas) y Newton converge sin numpy. Devuelve:

- `coeficientes` por señal y `aporta` (coef > 0.1);
- `puntosPropuestos`: un punto por cada 0.25 de log-odds, nunca negativo;
- `porPuntosPropuestos`: tasa por puntos con el nivel que le tocaría
  (bajo < base − 10 · medio < base · alto < base + 10 · muy alto) y
  `cortesPropuestos`;
- `aucLogit`, `aucPuntosPropuestos`, `separacionPropuesta`.

Es **ajuste en muestra**: dice qué señal pesa y propone enteros; no promete
una tasa. Cambiar los puntos de §5 se hace a mano con eso a la vista, en los
dos lados (Python y TS) y con los vectores dorados.

### Resultado de la primera corrida real (16/09/2026, padrón, horizonte 1)

172.524 observaciones, 1.038 equipos, 35 ligas. Tasa base 60 %: seis de cada
diez burbujas abiertas revientan en el partido siguiente.

| riesgo | tasa | n |
|---|---|---|
| bajo | 43.8 % | 14.490 |
| medio | 51.5 % | 71.899 |
| alto | 70.0 % | 71.960 |
| muy alto | 73.1 % | 12.902 |

**Ojo con esa corrida**: el pipeline guarda en `processed_matches.nivel_rival`
el **bin 0–9**, no el nivel continuo, y `/constantes` lo servía tal cual. La
calibración salió con el tramo «rival fuerte» (0.15–0.45) vacío porque las
distancias eran enteras: «en zona» era «mismo bin» y «muy fuerte» «un bin o
más arriba». Y en la app, el próximo rival (continuo, de `levels.db`) se
comparaba contra medianas en bins: la señal estaba rota en producción.
Arreglado en la lectura (`_nivel_rival_exacto` en `backend/app.py`): el
nivel se recupera de las q de la fila, como hace `backfill_kdc`. Las
conclusiones de signo (qué señal aporta) se mantienen; los cortes por
distancia hay que recalibrarlos con la base ya corregida.

Monótona, AUC 0.61. Pero el lift por señal dice **quién trabaja**: rival en
zona +0.29; racha ≥ mediana +0.06; K ≥ mediana **−0.02** y K ≥ máximo **−0.03**.
La K actual contra la K de reventón no adelanta el reventón (una K alta es un
equipo fuerte, no una burbuja a punto). La regla del nivel no se confirmó: la
familia total separa más que las específicas en nivel medio (0.25 vs 0.24) y
en extremos (0.30 vs 0.26), y «manda / no manda» da lo mismo. Por liga todas
separan en positivo; las copas europeas son las más flojas (Europa League
0.14, Conference 0.19).

### Segunda corrida (niveles continuos, `calibrar=true`, horizonte 1) — APLICADA

Mismas 171.260 observaciones, ahora con 36 celdas (el tramo «fuerte» ya se
llena). Coeficientes de la logística: K ≥ mediana −0.15 · K ≥ máximo −0.15 ·
racha ≥ mediana +0.32 · racha ≥ máximo +0.04 · rival en zona +0.82 · fuerte
+1.18 · muy fuerte +1.86. AUC del logit 0.68 (la tabla vieja daba 0.61).
Puntos propuestos y **aplicados** en §5: racha 1 · zona 3 · fuerte 5 · muy
fuerte 7; la K, 0. Tasa por puntos propuestos:

| pts | tasa | n |
|---|---|---|
| 0 | 42.1 % | 13.959 |
| 1 | 47.3 % | 76.343 |
| 3 | 60.8 % | 3.933 |
| 4 | 67.2 % | 23.089 |
| 5 | 69.2 % | 3.074 |
| 6 | 74.7 % | 19.445 |
| 7 | 80.8 % | 4.771 |
| 8 | 85.4 % | 26.646 |

A horizonte 2 la K tampoco aparece (−0.19 / −0.20), así que no es cuestión
de plazo. Lo que queda por probar cuando haya más historia: graduar también
la racha, y si las copas internacionales merecen su propia mediana.

### Probado: ¿la K pesa distinto por signo? No.

Caso real (16/09/2026): Valencia llegaba a Mendizorroza con K −32 tras 4
derrotas, la peor burbuja negativa de su historia (máximo previo 24), y la
guía dijo **bajo** porque Alavés (3.08) quedaba lejos del nivel con el que
Valencia suele cortar sus rachas (mediana 2.15). Valencia ganó 0-1.

La sospecha era que la logística conjunta escondiera un efecto opuesto por
signo (en la − una K muy negativa empujaría a cortarse por regresión a la
media). Se corrió `calibracionPorSigno` sobre los mismos 171.260 casos:

| señal | burbuja + (n 88.158) | burbuja − (n 83.102) |
|---|---|---|
| K ≥ mediana de reventón | −0.18 | −0.11 |
| K ≥ máximo histórico | −0.13 | **−0.18** |
| racha ≥ mediana | +0.36 | +0.24 |
| rival en zona · fuerte · muy fuerte | +0.77 · +1.13 · +1.84 | +0.87 · +1.24 · +1.88 |

Los dos signos dicen lo mismo, y en la negativa «K ≥ máximo» sale incluso
más negativa: un equipo en su peor racha tiene un poco MENOS chance de
cortarla en el siguiente partido. No hay regresión a la media a un partido
vista; hay un equipo que está mal. La tabla conjunta de §5 queda, y el caso
Valencia es lo que «bajo» significa: 46.5 % de reventón en esta base, no
«no va a reventar». Con los puntos calibrados ya en producción la escala
mide bajo 46.5 % · medio 60.8 % · alto 67.5 % · muy alto 80.9 %, y las tres
familias separan igual (≈ 0.30), así que la total sigue mandando por simple.

## 9. Vista «al día del partido» (releer el pasado sin el resultado)

Un partido ya jugado se puede releer como se veía esa mañana:
`antesDe=<fixtureId>` en `/constantes`, `/niveles` y `/equipos/{id}/burbujas`.

- La historia se corta **estrictamente antes** de ese partido (`date <
  fecha`): el propio partido, que en `constants` lleva la misma fecha que el
  fixture, queda fuera, y todo lo posterior también.
- En `/burbujas`, ese partido hace de **próximo**: rival real, condición y el
  nivel del rival a esa fecha. Es exactamente la construcción del backtest.
- La plantilla de hoy **no** se usa (la de entonces no está guardada): la
  estabilidad va `sin dato` y la confianza no pasa de media. Fingir
  estabilidad con datos de hoy sería hindsight.
- La sección Burbujas lo hace sola para todo partido finalizado y lo anuncia
  con una banda «VISTA AL DÍA DEL PARTIDO». Retrocediendo en el calendario se
  ve, día por día, qué habría dicho la guía.

Qué mirar en la salida:

| tabla | qué confirma |
|---|---|
| tasa por nivel de riesgo | debe **crecer** de bajo a muy alto; si no, los puntos no están calibrados |
| AUC de los puntos | 0.5 = no ordena nada; cuanto más cerca de 1, mejor ordena |
| lift de cada señal | encendida debe reventar más que apagada; lift ≤ 0 → bajarle el peso |
| separación por familia y «manda / noManda» | si la familia que manda separa más, la regla del nivel se confirma |
| nivel medio vs extremo | en medio las específicas deberían separar más que la total; en extremos, al revés |
| por tamaño de muestra | si con < 3 reventones la tasa se desordena, el umbral de confianza está bien puesto |

Sobre la demo (datos sintéticos, solo sirve de humo) la tasa ya sale monótona
y el rival en zona es la señal con más lift. La calibración real se corre
sobre las `.db` del usuario; los umbrales que se ajustan con ella son los
puntos de §5, la tolerancia de zona (0.15) y los cortes de muestra de §6.

## 10. Alerta de extremo (prudencia, no probabilidad)

El backtest de §8 dejó claro que una K récord no revienta más que otra: por
eso la K no puntúa. Pero Alavés–Valencia (septiembre 2026) enseñó lo que
falta: la K de Valencia estaba en **−32 sobre un máximo previo de 24**, el
riesgo decía **bajo** (correcto dentro de su tasa: 46 % de reventón) y el
partido terminó 0-1. La K local del Alavés también reventó. Quien hubiera
cargado con confianza sobre el pronóstico perdía, y la intuición de «acá
mejor no» no tenía dónde apoyarse en la pantalla.

Eso no es un fallo de calibración y no se arregla moviendo puntos: se arregla
con una **bandera aparte** que dice cuánto se carga, no cuánto pasa.

- **Qué es**: por familia, `extremo` con `activo`, `kRecord` (|K| ≥ la K pico
  más alta con la que reventó ese signo), `rachaRecord` (racha ≥ la más larga
  que reventó), `partidosHistoria` (el N de «la más alta en N partidos»),
  `maximoPrevio`, `motivos` y `texto`. `null` sin base del signo.
- **Qué NO es**: no mueve `riesgo.puntos` ni `riesgo.nivel`. Puede convivir
  con «riesgo bajo», y ahí es justo donde más sirve.
- **Dónde se ve**: en rojo, antes del riesgo, en la tarjeta de Burbujas y
  Equipo; en la caja «Reventón de la burbuja» del parte; y como alerta
  **K-EXTREMO** (tipo estructural) que el backend agrega a la tira de alertas
  del parte al leer (`alertas_extremo` en `backend/analisis/parte.py`), para
  que se vea antes que cualquier otra cosa.
- **Qué le exige a Cowork** (prompt v2.5): escribir EXTREMO con el N de
  partidos en `lecturaSad.reventon`, no recomendar carga fuerte a que esa
  racha siga, bajar la confianza del pronóstico y decirlo en el falsador. No
  se convierte en «va a reventar»: es «acá no se pone plata grande».
- **Espejo**: `_extremo` en Python y `extremoDe` en TS, sobre los mismos
  vectores dorados (el caso Foco tiene K 22.1 sobre máximo 13.3 y racha 6
  sobre 3: activo en total y visita, inactivo en local).

### 10.1 Cerca del extremo (el escalón ámbar)

ADT–Cienciano (septiembre 2026) enseñó el hueco de la bandera: la K total de
ADT estaba en **−17.9 con un récord previo de −19.5**, por encima del 95 % de
sus 39 reventones negativos, y como no era récord no se encendía nada. La
tarjeta decía «riesgo bajo · 1 pt» a secas, que se lee como luz verde.

- **Qué es**: `extremo.cerca` = sin récord, la K o la racha ya superan
  (ESTRICTO: «más alta que») al `CERCA_PCT` = **90 %** de los reventones de
  ese signo. Los motivos dicen el porcentaje, el n, el récord previo y a
  cuánto queda («K -17.93: más baja que el 95 % de las 39 burbujas - que
  reventaron (récord previo -19.54, a 1.61)»).
- **Qué NO es**: no mueve el riesgo ni cambia `activo`, que sigue siendo
  SOLO el récord (la alerta K-EXTREMO, el veredicto y las lecciones leen
  `activo` y no cambian de significado).
- **Dónde se ve**: caja ámbar «CERCA DEL EXTREMO» antes del riesgo en la
  tarjeta, una línea ámbar en la caja del reventón del parte, y la alerta
  **K-CERCA-EXTREMO** (tipo `dato`, calculada, no se deposita) en la tira. Y si
  la que está en su extremo (récord o cerca) es la K de la CONDICIÓN de hoy y no
  la total, la tira trae **K-EXTREMO-CONDICION** (tipo `dato`, 20/10/2026: el
  Cagliari de visita con la total en 0): manda la total en el riesgo, pero esa
  es la burbuja que se juega. Desde el 25/10/2026 (incidencia 494) la franja alta
  sin récord de la condición tiene su propio código, **K-CERCA-EXTREMO-CONDICION**,
  como la total: K-EXTREMO-CONDICION queda solo para el récord.
- **Qué le pide a Cowork**: nombrarla en `lecturaSad.reventon` y no
  recomendar carga fuerte a que la racha siga. No es regla dura como el
  récord: es prudencia en la carga.
- Con muestra corta (menos de 10 reventones del signo) el 90 % estricto solo
  se alcanza siendo récord, así que la bandera ámbar no aparece sola: no
  hay franja alta que medir.
- **Espejo**: `CERCA_PCT` y `_extremo` en Python, `extremoDe` (exportada) en
  TS, con el mismo caso sintético en los dos tests.
- **Calibración** (`franjaAlta` del backtest, `--padron`; en el servidor
  `GET /analisis/burbujas/backtest`): como la K no adelanta el reventón, el
  umbral NO se elige por tasa sino por **ruido**. Para cada candidato (75 ·
  80 · 85 · 90 · 95) el backtest dice en qué fracción de las burbujas
  abiertas saltaría el aviso (solo K, solo racha, K o racha; sin contar las
  que ya son récord) y cuánto revientan ahí. `propuesto` = el más bajo que
  salta en ≤ 10 % (`TECHO_AVISO`). El 90 vigente es un primer corte hasta
  correrlo con la base real; moverlo es cambiar `CERCA_PCT` en los dos lados.
- **Resultado con la base real (23/09, muestra de 100 equipos, 16.639
  burbujas abiertas):** el aviso con 90 salta en el **5,2 %** (tasa de
  reventón 58,8 %); con 85, en el 9,3 %; con 75, en el 18,2 %. La tasa casi no
  cambia entre umbrales ni contra el resto (61,5 %) ni contra el récord
  (60,3 %): confirma §8, la K alta no adelanta el reventón, y el umbral es
  solo cuestión de ruido. **Se queda en 90**: el backtest propone 85 (el más
  bajo bajo el techo del 10 %), pero el récord rojo ya salta en el **18,5 %**
  de las burbujas, y sumarle un 9 % de ámbar deja más de una de cada cuatro
  burbujas con algún aviso. Hallazgo aparte, sin tocar: que el EXTREMO salte
  en casi una de cada cinco burbujas sugiere que en historias cortas el
  récord es fácil de batir; revisar si pide un mínimo de reventones del signo.

De paso, los motivos del récord llevan el signo de la K («K -26.04 … récord
previo -19.54»): antes decían «K 26.04 … máximo previo 19.54» bajo un título
«K -26.0: la más baja», que se leía como contradicción.

### 10.2 Extremo inflado por amistosos (14/10/2026)

Los amistosos **cuentan** en la burbuja: el espectáculo se arma para el hincha
también en pretemporada, y una racha se construye o se rompe ahí con causas
que interesan para leer al equipo. Pero en los estudios fuera de Perú dos
alertas de extremo salieron de rachas hechas en buena parte en pretemporada
(Lazio, racha récord de 9 con 5 amistosos; Real Madrid, K-CERCA con 3 de 6).
Por eso `extremo.inflada` = `{amistosos, partidos, texto}` cuando la alerta
(récord o cerca) está encendida y **la mitad o más** de la racha abierta son
amistosos (liga 667, `AMISTOSOS`); si no, `null`. `actual.amistosos` trae el
conteo siempre. La marca **no apaga la alerta ni mueve el riesgo**: dice de
qué está hecho el récord. Espejo en `src/lib/burbuja.ts` y check en los dos
tests sobre el mismo vector (los 3 últimos partidos como amistosos → inflada;
los 2 últimos → no). La tarjeta pinta el chip «INFLADA · n/N amistosos» y
las alertas K-EXTREMO / K-CERCA-EXTREMO del parte lo dicen.

### 10.3 Récord de racha: superar y con 3 o más (23/10/2026, incidencia 67)

Decisión del usuario sobre el «hallazgo aparte» de §10.1 (el EXTREMO salía en
el 18,5 % de las burbujas). En la agenda del 23/10, 3 de las 15 alertas rojas
eran rachas de **2** que solo **igualaban** un máximo de 2 (Cusco y Medellín
de local, Juan Pablo II), y Leones del Norte gritaba «la racha más larga en 55
partidos» con 2 derrotas de local sobre un máximo de 1, una historia hecha
casi toda en la Serie B (subió en 2026: en primera llevaba 16 de local). El
Leipzig con 11 de local sobre 9 es el récord que la alerta quiere decir.

- `rachaRecord` = la racha **supera** el máximo previo **y** tiene
  `RACHA_RECORD_MIN` = **3** partidos o más. Igualar el máximo ya no es rojo:
  con 3+ puede quedar en ámbar (`cerca`, si pasa el 90 % de sus reventones).
  Una racha de 1-2 no es récord ni «cerca» por largo. La K récord no cambia.
- La INFLADA por «solo es récord contando los amistosos» sigue la misma
  regla: sin ellos, igualar el máximo o quedar debajo de 3 ya no sería récord.
- **INFLADA en cualquier racha abierta** (incidencia 311): Stuttgart perdió
  0-1 en casa con el Dortmund y dos amistosos de septiembre (3-0 Heidenheim,
  5-0 Fürth) le dieron «+18 de local, 2 seguidas»; el 1-1 con el Atlético la
  reventó. `extremo.inflada` sale con la mitad o más de amistosos aunque no
  haya récord ni cerca (sin sumar motivos a la alerta), y la tarjeta pinta el
  chip junto a la burbuja abierta.
- **La historia de otra categoría** (pedido del usuario: el ascendido juega
  distinto, y en las copas contra los de arriba también «despierta»): lo dice
  `escala` (cambio de categoría, `rival de categoría inferior/superior`) y el
  analista lo considera; el cálculo no se corta por categoría.
- Espejo en `src/lib/burbuja.ts`, mismos casos en los dos tests.

## 10-bis. La misma referencia, por período

El Universitario de hoy no es el de Fossati ni el de la gestión de Ferrari, y
el City del primer Guardiola no es el de ahora: un cambio institucional grande
cambia con qué K y ante qué rival revienta un equipo. La referencia global
(toda la historia del equipo) **sigue mandando en el riesgo**, porque es la
que está calibrada con el backtest de §8 y no hay backtest por período. Pero
al lado viajan las mismas medidas —n, K pico, racha y nivel del rival con el
que reventó, media · mediana · moda— acotadas en el tiempo, en
`familias.*.historialPorPeriodo[]` (y los cortes en `periodos[]`):

| clave | corte | de dónde sale |
|---|---|---|
| `temporada:<t>` | UNA por cada temporada de la historia: del primer partido de esa temporada al primero de la siguiente | `ConstantesDTO.temporada` (league_season) |
| `anio:<a>` | UNA por cada año: del 1 de enero al 1 de enero siguiente | la fecha |
| `dt` | la asunción del DT vigente | `plantilla.entrenador.desde` |
| `ultimos20` | los últimos 20 partidos | las filas |

Cada período lleva `desde` (inclusivo), `hasta` (exclusivo, vacío = abierto) y
`vigente` (la temporada y el año del último partido, el DT y los últimos N).
La tarjeta muestra los vigentes; en la gráfica se elige cualquiera: los chips
de temporada y año abren una segunda fila con todos los que hay en la historia,
y la gráfica marca el principio y el fin del elegido.

Reglas: se filtra por **la fecha en la que reventó** cada burbuja sobre los
mismos reventones de `episodios()` —los episodios no se recortan, así uno
nunca cambia de forma según la ventana—; un período que no se puede cortar
(sin temporada en las filas, sin DT con fecha) viaja con `sinDato` y sin
número; y con n chico la pantalla dice «muestra corta». En la vista «al día
del partido» (§9) la plantilla no se usa, así que el período del DT queda sin
dato. Espejo TS en `src/lib/burbuja.ts` (`periodosDe`) y vectores dorados en
los dos tests. La sección Burbujas muestra temporada y DT; la página de
Equipo, los cuatro.

**En la gráfica de K** (`KLineChart`, botonera `PeriodoReventon`, estado
`kPeriodo` del store compartido por Burbujas y Equipo): las dos líneas
punteadas «revienta ~ / se corta ~» toman la mediana del período elegido
(`src/lib/reventonRef.ts`) y llevan su etiqueta; una línea vertical marca el
partido donde arranca el período (la asunción del DT, el primero de la
temporada) o «←» en el borde si quedó antes de la ventana visible. Por defecto
la referencia es toda la historia; un período sin base se puede elegir y la
gráfica dice por qué no dibuja línea, en vez de volver a la global en silencio.

## 11. El reventón en el bucle de aprendizaje (producción contra backtest)

El backtest de §8 responde «¿los pesos son razonables en general?» sobre 171k
burbujas históricas. Lo que no responde es lo que pasa con los partidos que SÍ
se analizaron: si las burbujas de riesgo alto reventaron más que las de riesgo
bajo, y en la proporción que el backtest decía. Eso lo hace el bucle de
aprendizaje (`docs/APRENDIZAJE.md`), en dos piezas:

- **En el veredicto** (`objetivo.reventon`, `backend/analisis/veredicto.py`):
  por lado, `declarado` = la burbuja total tal como estaba antes del partido
  (signo, K, racha, nivel y puntos de riesgo, tramo del rival, si tenía la
  alerta K-EXTREMO), reconstruida con la vista «al día del partido» de §9 —los
  mismos números de `/burbujas?antesDe=`—, y `observado` = si la K fusionada
  de ese partido cerró la burbuja, con `episodios()`, la misma función que
  detecta los reventones de la historia. Es observación, no veredicto: no hay
  `acerto`.
- **En las lecciones** (`acreditables.reventon`, `backend/analisis/lecciones.py`):
  solo casos `ciega` + `PRE`, de la cohorte elegida y sin los de cuarentena.
  Tasa observada por nivel de riesgo contra `TASA_BACKTEST` (la tabla de §8,
  segunda corrida, como rango por nivel), comparada solo con `n ≥ 10` por
  nivel **y por intervalo, no por el punto**: `porNivel[nivel].intervalo` es
  el de Wilson al 95 % de la tasa observada, y `lectura` es `compatible`
  cuando el rango del backtest lo toca y `fuera` cuando no. Con 6 de 21
  (29 %) contra 42-47 % el punto está afuera y el intervalo [14 %, 50 %] dice
  que es ruido; eso salía en rojo el 19/09. Las burbujas con K-EXTREMO aparte.
  `fueraDelBacktest` / `revisionAbierta` **abren** la revisión de los puntos
  de §5: no los mueven. `TASA_BACKTEST` no es un peso y no entra en ningún
  cálculo de riesgo; por eso no tiene espejo TS ni vector dorado.

Se ve en la banda del veredicto del parte (`↯ reventó` / `→ siguió`, con el
riesgo que se había declarado) y en la sección Aprendizaje (reventadas sobre
observadas y la tabla por nivel contra el backtest).

## 12. Las lecciones de los estudios, contra el denominador (14/10/2026)

Los 52 estudios hacia atrás (`docs/autopsias/reventones-*.md`) explican POR
QUÉ revientan las burbujas, pero solo miraron burbujas que reventaron. El
backtest con `--lecciones` (`backend/backtest_lecciones.py`) pone cada lección
contra TODAS las burbujas abiertas de la familia total: tasa encendida y
apagada, lift, intervalo de Wilson, cobertura (las que dependen de las
alineaciones solo cuentan donde la base las tiene) y, sobre todo, el **lift
sobre el riesgo**: el mismo lift DENTRO de cada nivel de riesgo, que es lo que
la señal suma a lo calibrado. Una lección sin lift sobre el riesgo no entra a
los puntos aunque los estudios la hayan visto en muchos reventones.

El arquero del no favorito va aparte: la marca (favorito con racha + o débil
con racha −) se mide como las demás, y con las estadísticas DEL partido se
mira, como autopsia, cuánto revienta según las atajadas del débil y los tiros
al arco del fuerte; el único insumo previo, el perfil del arquero (goles
evitados contra xG, n ≥ 5), se mide por terciles: si no separan, la forma del
arquero no sirve para pronosticar.

Correrlo: `python -m backend.backtest_burbuja --padron --lecciones` (en
Railway, en subproceso) o `GET /analisis/burbujas/backtest?padron=true&lecciones=true`
(maestro). El resultado queda en `$SAD_DATA_DIR/.backtest_lecciones.json` y se
lee con `GET /analisis/cowork/reventones/backtest`.


### 12.1 Primera corrida real (14/10/2026, padrón, 1.078 equipos, 87.361 burbujas abiertas, familia total)

Tasa base 61,7 %. El riesgo calibrado separa: bajo 46,5 % · medio 60,7 % ·
alto 67,3 % · muy alto 80,8 %.

| Lección | Encendida | Apagada | Lift | Sobre el riesgo | Lectura |
|---|---|---|---|---|---|
| **condición a contramano** | 64,0 % (52.726) | 58,3 % | +5,7 | **+5,8** | real, en los dos signos |
| **favorito por nivel** (la marca ARQUERO-NO-FAVORITO) | 44,0 % (36.493) | 74,4 % | −30,4 | **−20,6** | PROTEGE: la burbuja del favorito (o la − del débil) revienta MENOS, y el riesgo no lo ve |
| cambio de categoría, racha + | 68,7 % (2.635) | 61,7 % | +7,0 | — | el ascendido/descendido en racha positiva revienta más |
| cambio de categoría, racha − | 56,9 % (3.257) | 62,6 % | −5,7 | — | …y en racha negativa, menos |
| resaca internacional, racha − | 65,7 % (3.518) | 61,4 % | +4,3 | — | la − se corta más tras perder afuera |
| racha de otra competición, + / − | 57,5 % / 64,6 % | 63,1 % / 61,1 % | −5,6 / +3,5 | — | va al revés en cada signo |
| récord (K-EXTREMO) | 61,0 % (11.466) | 61,8 % | −0,8 | −1,7 | NO adelanta el reventón (confirma §8) |
| cerca del récord | 59,4 % | 61,9 % | −2,5 | −2,8 | ídem |
| inflada | 59,8 % (405) | 61,7 % | −1,9 | −1,4 | sin efecto |
| rival con su burbuja · parón · concediendo · rival de otra base | | | ±0,7 | ±1,7 | sin efecto |
| DT / once / arquero suplente | n ≈ 3.000 (cobertura 4 %) | | | | sin evidencia (IC anchos) |
| Perú contra el resto | 62,4 % | 61,7 % | +0,7 | 0,0 | Perú NO es distinto |

**El arquero.** Con las stats del partido (n = 1.413, autopsia): cuantos MÁS
tiros al arco tiene el fuerte, MENOS revienta (59 % → 45 % → 21 % por
terciles), y las atajadas del débil casi no separan (45 · 45 · 37 %). El
reventón típico del favorito no es «dominó y el arquero lo paró»: es que el
favorito NO generó. El perfil previo del arquero (goles evitados contra xG,
n ≥ 5) no ordena la tasa (56 · 34 · 50 %, IC superpuestos): no sirve para
pronosticar. La marca ARQUERO-NO-FAVORITO como riesgo extra queda REFUTADA.

**El sesgo de los estudios.** Los 52 estudios vieron el récord en casi todos
los reventones porque la lista de candidatos se ordenaba por racha y K pico
(`reventones.candidatos`): estudiamos las burbujas más grandes. Contra el
denominador el récord no revienta más. Sigue como PRUDENCIA (no cargar la
apuesta a que la racha siga, porque si revienta revienta desde lo más alto),
nunca como probabilidad.

**Lo que pide recalibrar** (con el backtest a la vista, en los dos lados y en
los vectores dorados; sin aplicar): sumar a la logística la condición a
contramano y la diferencia de nivel equipo − rival (hoy el riesgo solo mira la
distancia del rival a la mediana de SUS reventones), y por signo el cambio de
categoría y la resaca internacional.

### 12.2 Recalibración (14/10/2026, `--calibrar`, 173.615 observaciones de las tres familias)

> **En duda desde el 14/10/2026 (§13.1):** esta corrida y la §12.1 usaron el nivel
> del rival de DESPUÉS del partido. Los puntos siguen vigentes en la app hasta
> que la corrida limpia diga otra cosa.

| Señal | Coeficiente (log-odds) | + | − | Puntos |
|---|---|---|---|---|
| K ≥ mediana / K récord | −0.006 / −0.090 | | | 0 (no puntúa) |
| racha ≥ mediana / récord | 0.227 / 0.081 | 0.273 | 0.162 | 1 / 0 |
| rival en zona · fuerte · muy fuerte | 0.473 · 0.743 · 1.340 | | | 2 · 3 · 5 (antes 3 · 5 · 7) |
| **contramano** | 0.207 | 0.226 | 0.187 | **+1** |
| **favorito** (≥ 0.5 a favor) | −0.528 | −0.540 | −0.512 | **−2** |
| **muy favorito** (≥ 1.0 a favor) | −1.057 | −1.053 | −1.058 | **−4** |

Un punto cada 0.25 de log-odds, como en §8. AUC del logit 0.716 y de los
puntos 0.715. Por puntos la tasa sube sin retroceder: −4 → 29 % · −3 → 33 % ·
−2 → 38 % · −1 → 47 % · 0 → 53 % · 1 → 59 % · 2 → 64 % · 3 → 69 % · 4 → 75 %
· 5 → 80 % · 6 → 85 % · 7 → 88 %. Cortes sobre la isotónica (base 60 %):
**bajo < 0 · medio 0-1 · alto 2-3 · muy alto ≥ 4**, separación bajo/muy alto
37,8 puntos. `TASA_BACKTEST` (el listón del bucle de aprendizaje) va con los
rangos nuevos. Las dos señales nuevas son iguales en los dos signos: una sola
tabla. Aplicado en `burbuja.py` y su espejo `src/lib/burbuja.ts`, con vectores
nuevos en los dos tests (contramano, favorito, muy favorito).

## 13. ¿La burbuja mejora el 1X2? (`backend/backtest_burbuja_1x2.py`, 14/10/2026)

El riesgo está calibrado para decir si una RACHA se corta, no quién gana: una
racha de victorias se corta también con un empate. Hoy entra al pronóstico
solo como FRENO de la carga (reglas del prompt en `docs/COWORK.md`), nunca en
una fórmula. Antes de meterlo en una, se mide con la historia y sin cuotas:

| modelo | variables (por partido, todo «a favor del local») |
|---|---|
| M0 · motor | d = μ_partido local − μ_partido visita, y d² (el empate vive cerca de d = 0) |
| M1 · + racha | más la racha abierta de cada lado: signo × log(1 + partidos) |
| M2 · + riesgo | más los puntos del riesgo de cada lado, con el signo de su racha |
| M3 · + extremo | más el récord (2) y el «cerca» (1), con signo |

Logística multinomial (local · empate · visita), ajustada con el 80 % más
VIEJO de los partidos y evaluada en el 20 % más NUEVO; log-loss y Brier en la
prueba y la diferencia contra el modelo anterior con IC 95 % por bootstrap
emparejado por partido, también en los partidos con algún lado en riesgo alto
y con extremo. Sin fuga: burbuja, riesgo y nivel salen solo de lo anterior al
partido; un partido entra solo si los DOS equipos tienen historia (un lado sin
datos no es un lado sin burbuja).

Regla de decisión (la `lectura` del resultado la calcula el script): si el IC
de **M2 − M1** queda entero por debajo de cero, el riesgo AGREGA al 1X2 más
allá de la racha y tiene sentido llevarlo a la fórmula con esos coeficientes
(en los dos lados y con su propio test); si cruza cero, la burbuja se queda
como freno de la carga. M1 − M0 dice si la racha sola ya aporta (la «forma»
que el nivel ventana-20 no termina de ver). El método se prueba con datos
sintéticos de verdad conocida en `backend/test_backtest_1x2.py`.

Se corre en Railway (las `.db` viven ahí), como el resto de los backtests:
`nohup python -m backend.backtest_burbuja_1x2 --padron > /data/b1x2.log 2>&1 &`
y el resumen queda en `/data/.backtest_1x2.json`.

### 13.1 Primera corrida: CONTAMINADA (14/10/2026)

58.588 partidos, 47 % → 54 % de acierto con el riesgo y el coeficiente del
motor AL REVÉS (más ventaja de nivel del local, menos chance de que gane).
Demasiado bueno para ser cierto, y no lo era: el «próximo rival» se armaba
con `fila["nivelRival"]`, el nivel con el que el motor ponderó la fila, que
se escribe DESPUÉS del partido y ya trae el resultado (en la demo, el rival
de una victoria quedó 0.075 más abajo en promedio; el de una derrota, 0.084
más arriba). El riesgo lo usa dos veces (tramo del rival y favorito), así que
leía el marcador. Arreglado con `backtest_burbuja.nivel_rival_previo` (el
nivel ANTES del partido, el mismo que la app usa para un próximo con
`niveles_de(antes=)`), con su test en `test_backtest_burbuja`.

**La misma fuga estaba en la calibración de §12.1 y §12.2**: el lift del
«favorito por nivel», los puntos del tramo del rival y la tasa por nivel se
midieron con ella. La app en producción NO tiene la fuga (arma el próximo
con el nivel previo), pero los PUNTOS que usa salieron de un backtest que sí.
Hay que volver a correr `--lecciones`, `--calibrar` y este backtest; hasta
entonces los puntos de §12.2 están en duda, sobre todo el −2/−4 del favorito.

Queda aparte, y NO es fuga: el historial de reventones (`burbuja.py`, «el
nivel del rival que reventó cada burbuja») también guarda el nivel de
después. Es pasado, no filtra el partido que se predice, pero compara la
mediana de esos niveles (post) con un próximo medido antes: un sesgo de
escala chico, a revisar con el backtest limpio a la vista.

### 13.2 La corrida limpia y los puntos vigentes (14/10/2026, tarde)

Mismas 173.615 observaciones (1.078 equipos, padrón, horizonte 1), con el rival
medido antes del partido:

| | con la fuga (§12.2) | limpia |
|---|---|---|
| AUC de la logística | 0.715 | **0.615** |
| coef. racha ≥ mediana | 0.32 | 0.247 |
| coef. rival zona · fuerte · muy fuerte | 0.47 · 0.74 · 1.34 | **0.10 · 0.19 · 0.38** |
| coef. contramano | 0.207 | 0.207 |
| coef. favorito · muy favorito | −0.53 · −1.06 | **−0.37 · −0.71** |
| lift sobre el riesgo: contramano · favorito | +5,8 · −20,6 | **+2,2 · −14,8** |

Casi toda la «fuerza» del rival era la fuga: el nivel de después dice quién
ganó. Contramano no cambia (no usa el nivel del rival) y el favorito sigue
siendo la señal más fuerte, más chica. Ninguna otra lección gana lift.

Puntos vigentes (paso 0.25 de log-odds, los que propone `--calibrar`): racha
≥ mediana +1 · rival zona 0 · fuerte +1 · muy fuerte +2 · contramano +1 ·
favorito −1 · muy favorito −3. Cortes: **bajo < 0 · medio 0 · alto 1-2 · muy
alto ≥ 3**. Tasa por puntaje (isotónica, monótona): −3 39.7 % · −2 44.7 % ·
−1 50.0 % · 0 55.2 % · 1 62.0 % · 2 67.1 % · 3 71.0 % · 4 75.0 % — de ahí
`TASA_BACKTEST`. Con los puntos de la mañana y datos limpios la tasa por nivel
daba 48 · 60 · 64 · 70 %: el orden se sostenía, lo que estaba mal eran los
rangos esperados (bajo 29-47 %, muy alto 75-88 %), que habrían hecho saltar
la revisión del aprendizaje por un error nuestro.

Lectura honesta: la guía ordena el riesgo (de ~45 % a ~72 %) pero separa poco.
Sirve para frenar la carga, no para prometer un reventón.

### 13.3 El 1X2, limpio: la burbuja NO agrega al resultado (14/10/2026)

58.588 partidos, entrenamiento 2019-04 → 2025-08 (46.870), prueba 2025-08 →
2026-10 (11.718; local 45 % · empate 26 % · visita 29 %):

| modelo | log-loss | Brier | acierto |
|---|---|---|---|
| M0 · motor | 1.0428 | 0.6273 | 47.4 % |
| M1 · + racha | 1.0428 | 0.6273 | 47.6 % |
| M2 · + riesgo | 1.0428 | 0.6273 | 47.5 % |
| M3 · + extremo | 1.0429 | 0.6274 | 47.6 % |

Todas las diferencias con el IC cruzando cero, también en los partidos con
riesgo alto (n = 7.319) y con extremo (n = 2.537). El coeficiente del motor
vuelve al sentido correcto (+0.24 local), y los de racha y riesgo quedan en
casi cero. **Decisión: la burbuja no entra a la fórmula del 1X2.** Se queda
como lo que el backtest sí sostiene: guía de si la RACHA se corta y freno de
cuánto se carga. Es coherente: lo que más pesa en el riesgo (el favorito por
nivel, el rival frente a su mediana) es diferencia de nivel, y esa ya la
tiene el motor en μ_partido.

Dato al margen que queda anotado: el motor solo acierta 47.4 % con log-loss
1.043, contra 45 % y ~1.068 de las frecuencias a secas. Mejorar el 1X2 pasa
por el motor (o por el EFE/TDE del analista), no por la burbuja.

### 13.4 Las constantes mismas, cruzadas (M4-M6, 14/10/2026)

§13.3 solo midió la burbuja TOTAL de resultado (signo y largo de la racha, y
los puntos del riesgo): nunca entró el VALOR de las K ni las familias por
condición ni las de goles. M4-M6 las agregan, tomadas de la fila ANTERIOR al
partido (la del partido ya trae su resultado) y comprimidas con
sign·log(1+|x|):

| modelo | variables además del motor (d, d²) |
|---|---|
| M4 · + K resultado | k total de los dos, k local del local y k visita del visitante |
| M5 · + K goles | goles anotado/recibido total de los dos, y por condición: los del local DE LOCAL, los del visitante DE VISITA |
| M6 · + todas las K | M4 + M5 |

El cruce local × visita lo hace la logística: cada equipo con su variable y su
coeficiente por resultado. Se compara cada una contra M0 y M6 contra M3. El
test (`test_backtest_1x2`) siembra un cruce real (anota de local × recibe de
visita) y comprueba que M5/M6 lo detectan y que los coeficientes que pesan
son esos; con K de ruido, no inventa nada.

**Primera corrida (14/10/2026): INVÁLIDA.** La K de goles anotados se guardó
con la clave `ga`, la misma de «goles en contra» del lado, y pisó el marcador:
el resultado salió de comparar goles con constantes (7 % de empates en la
prueba, contra 26 % real) y `gaL` «predijo» con coeficiente +10 lo que él
mismo había armado. Arreglado con claves propias (`kRes`, `kGa`, …), una
guardia que corta si algo pisa el marcador, un test que compara el resultado
con el real y un control de cordura que aborta si los empates salen fuera de
15-35 %.

**Corrida limpia (14/10/2026, 58.590 partidos; prueba 11.718 con local 45 %
· empate 26 % · visita 29 %): NINGUNA constante agrega al 1X2.**

| contra el motor (M0, log-loss 1.0428, acierto 47.4 %) | Δ log-loss | IC 95 % |
|---|---|---|
| M4 · K de resultado (total y por condición) | +0.00011 | [−0.00034, +0.00059] |
| M5 · K de goles (total y por condición) | −0.00018 | [−0.00116, +0.00079] |
| M6 · todas las K | −0.00023 | [−0.00121, +0.00073] |

Igual en riesgo alto y con extremo. Los coeficientes de las K quedan todos
cerca de cero (|β| < 0.1 por desvío) y solo pesa la diferencia de nivel. Es
coherente: el nivel ventana-20 ya resume puntos y goles ponderados por rival,
y las K son otra lectura de esa misma historia. Límite declarado: es una
logística lineal; un cruce no lineal de K extremas no queda descartado del
todo, pero con estos pesos no hay ahí nada grande. **Decisión: las K no entran
a la fórmula del 1X2.** Mejorar el 1X2 pasa por el motor (47 % contra 45 % de
«siempre local») o por lo que el nivel no ve —bajas, DT, contexto: el EFE/TDE
del analista, medido con los veredictos—.

### 13.5 El mercado sobre los mismos partidos (sin rentabilidad)

Para saber dónde estamos parados, el mismo backtest compara al motor con el
MERCADO en los partidos de la prueba que tienen cuota 1X2 capturada en
`sad.db` (`odds`): probabilidad = 1/cuota sin margen, promediada entre casas;
las cuotas SINTÉTICAS de `backfill_cuota` (`bookmaker_name='SYNTHETIC'`) no
entran. Sale en el log como «el MERCADO sobre los mismos partidos» con su
cobertura, casas promedio, margen y la diferencia de log-loss con IC. No es
rentabilidad: es cuánto mejor (o peor) acierta el mercado que el motor.

**Primera corrida (14/10/2026):** 2.379 partidos de la prueba con cuota 1X2
(20 %, del 16/07 al 14/10/2026: antes no se capturaban cuotas, y del 18/09 al
11/10 hubo el hueco del extractor), 12,2 casas en promedio, margen 7,7 %.

| mismos partidos | log-loss | Brier | acierto |
|---|---|---|---|
| mercado | 0.9908 | 0.5912 | 51.2 % |
| motor (M0) | 1.0405 | 0.6257 | 46.9 % |

Mercado − motor: −0.0497 [−0.0624, −0.0378]. Contra la línea de base de las
frecuencias (~1.068), el mercado mejora ~0.08 y el motor ~0.03: el motor capta
alrededor de un tercio de lo que sabe el mercado. Siguiente pregunta (sin
rentabilidad): ¿el motor agrega algo SOBRE el mercado? Si no, toda su
información ya está en la cuota y el valor del SAD tiene que salir del análisis
del partido; si sí, hay información propia mal expresada.

## 14. Cómo se corta: a cero o al otro signo (14/10/2026)

La K total de un equipo, después de un partido, queda positiva si ganó, en 0
si empató y negativa si perdió (MOTOR_SAD_EXTRACCION §3.3). El riesgo de
reventón dice si la burbuja se corta; esto dice CÓMO:

- **Por equipo** (`historial.positivo|negativo.termina` y `termina` en cada
  reventón de `/equipos/{id}/burbujas`): cuántas de sus burbujas se cortaron
  a 0 —primero empata— y cuántas pasaron directo al otro signo —se cae de
  golpe—. Espejo TS y vector dorado (`scripts/casos_burbuja.json`: las
  derrotas 0-1 y 0-3 cambian de signo, los empates 1-1 y 2-2 van a 0).
- **Calibrado** (`backtest_burbuja --calibrar`, bloque «cómo se mueve la K
  total en el partido siguiente», `movimiento` en `.backtest_calibracion.json`):
  por signo y nivel de riesgo, qué parte sigue, va a cero o cambia de signo.
  Corrida limpia del 14/10/2026 (87.379 burbujas de la familia total):

  | burbuja | riesgo | n | sigue | a cero | al otro signo |
  |---|---|---|---|---|---|
  | + | bajo | 9.927 | 53.9 % | 24.7 % | 21.3 % |
  | + | medio | 4.074 | 45.9 % | 26.4 % | 27.6 % |
  | + | alto | 19.873 | 35.2 % | 27.7 % | 37.1 % |
  | + | muy alto | 11.108 | 27.2 % | 26.9 % | 45.9 % |
  | − | bajo | 8.881 | 52.3 % | 25.0 % | 22.7 % |
  | − | medio | 3.744 | 46.2 % | 27.2 % | 26.6 % |
  | − | alto | 20.199 | 35.4 % | 26.9 % | 37.8 % |
  | − | muy alto | 9.573 | 28.0 % | 27.3 % | 44.6 % |

  El «a cero» casi no se mueve (25-28 %: es la tasa de empates); el riesgo
  separa SEGUIR de DARSE VUELTA, y los dos signos se comportan igual. Viaja
  en `riesgo.movimiento` (`MOVIMIENTO_BACKTEST`, espejo TS y vector dorado),
  solo en la familia total.
- **En el parte**: la espina (`lecturaSad.espina`) es la lectura del analista
  de adónde va la K de cada equipo (positiva · cero · negativa · neutra); el
  veredicto la compara con lo que hizo la K y Aprendizaje mide cada lectura
  contra la frecuencia de ese movimiento. No es un número del 1X2: es la
  lectura por equipo, y se mide como tal.
### 14.1 Las K de la condición (15/10/2026, `--calibrar`, padrón)

La misma guía para la K local (en el próximo partido de local) y la de visita
(en el próximo de visita). Viaja en `riesgo.movimiento` de `familias.local` /
`familias.visita` cuando esa familia se mueve en el próximo partido (si no, `null`),
y es la que acompaña a una espina con `guia: condicion`.

| familia · signo | bajo | medio | alto | muy alto |
|---|---|---|---|---|
| local + (n 26.698) | 63 · 22 · 15 | 50 · 26 · 24 | 43 · 28 · 30 | 35 · 29 · 37 |
| local − (n 16.506) | 45 · 27 · 28 | 35 · 29 · 36 | 27 · 27 · 46 | 21 · 26 · 53 |
| visita + (n 17.993) | 47 · 26 · 27 | 33 · 29 · 38 | 27 · 27 · 46 | 20 · 26 · 55 |
| visita − (n 25.080) | 61 · 23 · 17 | 51 · 26 · 23 | 42 · 29 · 30 | 36 · 28 · 37 |

(sigue · a cero · al otro signo, en %). La asimetría local/visita que se ve en la
cancha está en los números: con el mismo riesgo, la racha ganadora DE LOCAL
aguanta bastante más que la total (63 % contra 54 % con riesgo bajo) y la DE
VISITA bastante menos (47 %); la racha perdedora de visita es la que más se
sostiene y la de local la que más se corta. «A cero» sigue en 22-29 %: el
empate no depende de la burbuja. Ojo con leerla como ventaja sobre el 1X2: el
motor ya trae la localía en el nivel (§13.4); esto es la guía para LEER a un
equipo por condición, y Aprendizaje (`acreditables.espina.porGuia`) dirá si la
lectura con la K de la condición acierta más que con la total.

### 14.2 La espina de la tarjeta y el analista (19/10/2026)

Pedido del usuario: «la espina viene de las tarjetas; tiene una base más sólida
y estadística… hay que juntarlo con el análisis de los skills». La tarjeta ya
dice adónde suele ir la K (§14, §14.1); ahora lo dice también como espina:
`espinaTarjeta` = el movimiento más probable de `riesgo.movimiento`, traducido
a resultado del equipo (sigue → `positiva` con racha + y `negativa` con racha
−; cero → `cero`; cambio → el signo contrario), `fuerte` si llega al 50 %
(`burbuja.ESPINA_FUERTE`, espejo `src/lib/burbuja.ts`, vectores
`scripts/casos_espina_tarjeta.json`). Viaja en cada familia de `/burbujas` y en
`reventonCalculado` del parte (total y condición), y la tarjeta la pinta.

Es el PUNTO DE PARTIDA del parte, no su reemplazo: el analista lee los skills
(EFE, TDE, DTP, matriz) encima y, si va contra una tarjeta fuerte, lo dice en
`porque` («contra la tarjeta porque…»; si no, el recibo lo cobra en `faltan`).
Con la tarjeta débil (riesgo alto: va a reventar, no se sabe cómo) deciden los
skills. El veredicto guarda las dos espinas (`objetivo.espina.*.tarjeta` y
`vsTarjeta`) y `GET /analisis/cowork/espina/calibracion` (en Aprendizaje,
`acreditables.espina.tarjeta`) dice, en población ciega, cuánto acierta la
tarjeta por fuerza y nivel, cuánto el analista cuando la sigue y **quién gana
cuando la contradice**: si con casos el analista no le gana a la tarjeta al
contradecirla, la regla del prompt se endurece; si le gana, los skills están
sumando.

**Las dos tarjetas del partido** (19/10/2026, Monza 4-0 Cagliari): las dos eran
débiles (38 %), pero una decía «el local gana» y la otra «el visitante pierde» —el
mismo resultado desde los dos lados— y acertaron. El veredicto las lee como un
1X2 (`objetivo.tarjetas`: a positiva→local, cero→empate, negativa→visita; b al
revés) y dice si concuerdan, discrepan o hay una sola; Aprendizaje acumula en
`acreditables.espina.tarjeta.partido` cuánto aciertan cuando concuerdan (y
cuando concuerdan siendo las dos débiles) contra una tarjeta sola. Si
«concuerdan» acierta claramente más, la segunda tarjeta confirma a la primera y
eso puede entrar al prompt como regla; hasta entonces es medición.

**General, local o visita** (19/10/2026, pedido del usuario: a veces el parte
se guía de las constantes específicas): la calibración separa la tarjeta GENERAL
(K total) de la de LOCAL y la de VISITA —la de la condición que leyó el parte—
en `tarjeta.porTipo`, cada una entera y por fuerza. Hasta el 19/10 el veredicto
medía siempre la general, así que local y visita arrancan en cero.

Medición de arranque (veredictos del 17-18/10, a mano): la espina de la tarjeta
sola acertó 56 de 102 lados, la del analista 52 de 97 y el 1X2 59 de 102; con
riesgo bajo, la tarjeta 17 de 20. Es n chico: lo que decide es la tabla.

## 15. Las otras familias: doble oportunidad, márgenes y goles (17/10/2026)

Pedido del usuario: la burbuja de doble oportunidad de local de Everton estaba
en su récord (4 partidos en casa sin perder; nunca había llegado a 4) y Everton
perdió 0-2 con Chelsea. ¿Las burbujas de las otras familias avisan algo que la
K de resultado no? `backend/backtest_familias.py` (test:
`backend/test_backtest_familias.py`, detecta un reventón plantado y no inventa
uno con resultados independientes).

**Qué mide.** Cada familia es un sí/no por partido —no pierde · no gana · gana
por 1+…4+ · pierde por 1+…4+ · anota · anota 2+ · recibe · recibe 2+ · ambos
marcan · más de 2,5— en total, de local y de visita. En cada partido, solo con
lo anterior: la frecuencia propia del equipo, el largo de la burbuja abierta
(racha o sequía) y si está en su récord (lo iguala · lo supera · lejos, con ≥ 3
burbujas previas del valor). Se compara la predicción del partido siguiente con
la frecuencia sola (A) contra frecuencia + largo + récord (B), corte temporal
80/20 y bootstrap por equipo. No usa el nivel del rival (no hereda §13.1).

**Datos.** 518 equipos de las 30 ligas del padrón (historias de `/constantes`,
hasta 500 partidos), 119.584 partidos, 3,58 M observaciones.

**Resultado: la burbuja no aporta en ninguna familia.** De 48 combinaciones
(16 familias × 3 ámbitos; `noGana` y `pierde1+` son el complemento de `gana1+`
y `noPierde` y dan lo mismo), UNA queda con el intervalo bajo cero —pierde 3+
en total, Δ log-loss −0.0009—, que es lo que se espera por azar con 48 pruebas
al 95 %. Cuatro EMPEORAN fuera de muestra (ambos marcan, más de 2,5, recibe y
recibe 2+, de local): el largo y el récord sobreajustan.

**El récord no revienta: se sostiene un poco más.** Sobre todas las familias,
la racha que supera su récord sigue el 59,9 % de las veces contra 58,0 % que
esperaba la frecuencia (+1,9 pts); la que lo iguala, +1,2; la sequía en récord,
+1,9 a +2,4. En «no pierde de local» —el caso de Everton—: igualando el récord
sigue 76 % contra 68 % esperado (n = 1.049), superándolo 77 % contra 73 %
(n = 3.538). Es INERCIA, no reventón, y casi seguro es forma reciente (la
frecuencia de toda la historia va atrasada respecto de un equipo que mejoró).
Es la misma conclusión que §12 para la K: el récord no adelanta el corte.

**Qué se hace con esto.** Las otras familias entran al análisis como
DESCRIPCIÓN —cuánto lleva la burbuja, su récord, cuánto suele durar y la
frecuencia propia— sin riesgo ni puntos, y con la lectura correcta del récord
(«en su récord estas burbujas se sostienen algo más de lo que dice la
frecuencia, no menos»). Everton–Chelsea no lo habría corregido: la guía
histórica decía que esa racha tendía a seguir. Re-correr con
`python -m backend.backtest_familias --padron` (servidor) o `--desde-json`
(historias bajadas) cuando haya más temporada.

### 15.1 El PERFIL de doble oportunidad sí agrega al 1X2 (17/10/2026)

El §15 midió la burbuja (largo y récord) contra la frecuencia del equipo, no
la frecuencia misma contra el motor. El usuario: «hay equipos que, como no
tienen tan buen rendimiento, pueden empatar como locales o jugarse un empate
como visitas». `backtest_burbuja_1x2` suma dos modelos sobre el motor (M0):

- **M7 + perfil DC**: la frecuencia (Laplace, solo partidos ANTERIORES) con que
  el local no pierde y no gana DE LOCAL, y el visitante DE VISITA
  (`backtest_familias.perfil_dc`).
- **M8 + perfil y burbuja DC**: más la burbuja abierta de «no pierde» en la
  condición y su récord.

Corrido sobre las historias y niveles reales bajados de `/constantes` y
`/niveles` (518 equipos del padrón, corte temporal 80/20, sin cuotas):

| modelo | log-loss | Brier | acierto |
|---|---|---|---|
| M0 motor | 1.0430 | 0.6275 | 47.3 % |
| M7 + perfil DC | **1.0316** | **0.6193** | **47.9 %** |
| M8 + perfil y burbuja DC | 1.0313 | 0.6192 | 47.8 % |

M7 − M0: **−0.0114 [−0.0142, −0.0084]**: el perfil MEJORA al motor. M8 − M7:
−0.0003 [−0.0006, +0.0001]: la burbuja no agrega sobre el perfil (lo mismo
que el §15). M1-M6 dan lo del §13 (la racha, el riesgo y las K no agregan),
así que la corrida reproduce lo conocido. Para dimensionarlo: el mercado le
saca 0,050 al motor (§13.5); el perfil recupera ~0,011, casi un cuarto.

Coeficientes (por desvío, contra el empate): que el local NO GANE de local
baja su victoria (−0.14) y que el visitante NO GANE de visita baja la suya
(−0.13); que el visitante NO PIERDA de visita sube su victoria (+0.07). Lectura
probable: el motor usa una localía igual para todos y el perfil trae la de
CADA equipo (el que en casa empata mucho, el que afuera se planta).

**Qué queda por medir antes de tocar la fórmula** (la matemática del motor
es sagrada, `MOTOR_SAD_EXTRACCION.md`): (1) contra el MERCADO sobre los mismos
partidos —en el servidor, con `--padron`, que trae las cuotas—: si la cuota ya
lo tiene, el valor es de lectura, no de apuesta; (2) qué ventana del perfil
sirve más (toda la historia, la temporada, los últimos 20 de la condición).
Mientras tanto entra al análisis como DATO con su frecuencia por condición.

**Primera mirada al mercado (17/10/2026, con las cuotas de `/cuotas/{id}/casas`,
sin sintéticas):** solo 940 de los 7.490 partidos de la prueba tienen cuota por
esa vía (se capturan desde julio), y no alcanza para concluir. En esos 940:
mercado 1.0276 · motor 1.0412 · motor + perfil 1.0345 (perfil − motor −0.0067
[−0.0132, +0.0010]). Sobre el mercado, ajustando en la mitad vieja y probando
en la nueva (470/470): mercado + perfil − mercado +0.0031 [−0.0108, +0.0163],
mercado + motor − mercado −0.0073 [−0.0164, +0.0029]. Sin evidencia de que el
perfil agregue SOBRE la cuota; la respuesta firme saldría de `--padron` en el
servidor, con todas las cuotas guardadas. **Decisión del usuario (17/10/2026):
no hace falta correrlo; lo que importa es que esté como narrativa.** El perfil
se queda como DATO del análisis, y la fórmula del motor no se toca.

### 15.2 Narrativa: cuidado antes, causa después (17/10/2026)

Everton 0-2 Chelsea: el Everton llegaba con su doble oportunidad de local
enorme y anotando de local, y perdió sin marcar. El backtest dice que un récord
así no se corta más que lo normal, y por eso mismo un corte así tiene una causa
que rastrear. Dos piezas, sin puntos ni riesgo:

- **Antes**: una burbuja de otra familia en su récord y de 5+ partidos
  (`cuidado`, `familias.es_cuidado`) se lee como CUIDADO con la carga. Va en
  ámbar en la tarjeta y como alerta `FAMILIA-RECORD` (tipo `dato`) en la tira
  del parte. Es prudencia, como `K-EXTREMO`, no una probabilidad de corte.
- **Después**: `objetivo.otrasFamilias` del veredicto reconstruye las burbujas
  destacadas «al día del partido» y lista las que el marcador cortó. Las
  grandes o en su récord quedan `porExplicar`, y quien cierra el caso escribe
  la causa en `porLado.*.cortes` con un mecanismo de la lista cerrada del
  estudio de reventones (`reventones.MECANISMOS`). Juntas, esas causas son la
  materia para que lo «entendible y rastreable» se pueda contar.

**Rara para el equipo (24/10/2026, incidencias 420 y 450).** «58 de local sin
ganar por 3+» es récord, pero a quien gana por 3+ una vez cada 40 una racha
así le sale sola: gritaba CUIDADO y pedía causa al cortarse sin que hubiera
nada raro. Ahora cada burbuja lleva `probRacha` = la frecuencia propia del
estado de hoy elevada al largo (la chance de encadenar tantos seguidos) e
`improbable` (< 5 %, `familias.IMPROBABLE_BAJO`). `cuidado` exige récord, 5+
e improbable; `porExplicar`, además de grande o en su récord, improbable. Un
récord grande pero habitual lo dice en su línea («una racha así es
esperable»). Es regla de narrativa, no un número calibrado: no mueve ningún
riesgo. Espejo TS y vectores dorados («Sequía habitual»).

## 16. Cuánto separa el riesgo en cada liga (29/10/2026)

La fase 0 de ligas nuevas (`python -m backend.fase0_ligas` y
`backtest_burbuja --liga` liga por liga, horizonte 1, sin fuga) midió el AUC
de los puntos del riesgo en 23 ligas, con 2.000-10.000 observaciones cada una.

| AUC | Ligas |
|---|---|
| ≥ 0,64 (alta) | Eredivisie 0,679 · Serie A 0,676 · Grecia 0,669 · Bolivia 0,656 · Perú Liga 2 0,649 · Premier 0,648 · LaLiga 0,648 · Bundesliga 0,644 · Ligue 1 0,641 |
| 0,60-0,64 (media) | Süper Lig 0,632 · Liga MX 0,627 · Perú Liga 1 0,626 · Ecuador 0,622 · Conference 0,609 |
| < 0,60 (baja) | Europa League 0,593 · Serie B 0,593 · Brasil 0,590 · 2. Bundesliga 0,590 · Colombia 0,581 · Championship 0,578 · Argentina 0,577 · Ligue 2 0,575 · Segunda 0,572 |

**La regla**: el AUC sube con el peso del nivel en la μ de esa liga
(`backtest_gap --por-liga`): r = 0,89 sobre 22 ligas. Donde hay jerarquía una
burbuja «fuera de lugar» (el grande con racha negativa, el chico con racha
positiva) dice algo; en las ligas de paridad las rachas se cortan casi al azar
y el riesgo «bajo» ya revienta la mitad de las veces (49-54 % contra 34-41 %).
La Liga 2 de Perú separa como una primera: lo que fallaba ahí no era la
burbuja, eran las cuotas (38 % de partidos con 1X2 capturado).

**Lo que se hizo**: los puntos y los cortes NO cambian (son los calibrados con
el padrón). `/burbujas` trae `separacionLiga` (`backend/analisis/separacion_liga.py`:
AUC, n y nivel de la liga doméstica del equipo, con su nota) y la tarjeta lo
pinta; el prompt pide pesar menos la guía en una liga de nivel `baja`. Con el
mismo dato entraron al padrón Eredivisie, Grecia y Süper Lig, y las segundas
de Europa y la Liga de Expansión MX pasaron a menores (sin cuotas en vivo ni
agenda; su historia sigue entera). La tabla es una medición fechada: con cada
backtest nuevo se rehace.

### 16.1 Las copas nacionales (29/10/2026)

Misma medición, sobre las copas que ya estaban en la base:

| Copa | Riesgo bajo → muy alto | AUC | n |
|---|---|---|---|
| Taça de Portugal | 32 % → 84 % | 0,746 | 1.203 |
| Coupe de France | 34 % → 84 % | 0,736 | 1.184 |
| Copa del Rey | 33 % → 83 % | 0,727 | 1.215 |
| DFB Pokal | 37 % → 76 % | 0,652 | 1.042 |
| FA Cup | 46 % → 72 % | 0,611 | 3.776 |
| Coppa Italia | 44 % → 69 % | 0,601 | 744 |
| EFL Cup | 51 % → 64 % | 0,555 | 1.310 |

Donde un grande cruza con uno de tercera o cuarta (Taça, Coupe, Copa del Rey)
el riesgo separa MÁS que en cualquier liga: la diferencia de nivel es enorme y
se lee fácil —que se lea fácil no quiere decir que pague: la casa también la
ve—. La EFL Cup es la más floja de todo lo medido: los grandes la juegan con
suplentes y la burbuja no es la del once que sale. Y el MOTOR se equivoca en
las copas más que en cualquier liga (`backtest_gap --por-liga`: localía −0,22
en la Copa del Rey y −0,19 en la Coupe —el chico juega en casa—; calibrar por
torneo mejora el error ~0,04 contra ≤ 0,01 en las ligas).

**Lo que se hizo** (decisión del usuario): las copas medidas entran a la
agenda AL FINAL (prioridad 8, `separacion_liga.copa_en_agenda`): las de
separación alta en cualquier ronda (Taça, Coupe, Copa del Rey, Pokal), las de
media solo desde cuartos (FA Cup, Coppa Italia), la EFL Cup nunca. Siguen sin
cuotas en vivo. `separacionLiga` de `/burbujas` trae la de la copa cuando el
próximo partido es de copa (`competicion: copa`), y el prompt pide sacar el
1X2 de un partido de copa del mercado y de los skills, no del motor.


## 17. ¿Las constantes de goles ACOTAN los goles? (`backend/backtest_goles.py`, 30/10/2026)

Pedido del usuario: «las constantes de goles no predicen el resultado, acotan
los goles. Goles anotados, goles en contra. Esto va con un marcador. Puede
definir al ganador, pero no necesariamente acierta. Y teníamos dos, local y
visita: era brutal». Su método era mirar la serie de goles de cada equipo
(Alianza mete 1, 2, 2, 2, 1, 2, 2, 1, 2, 3, 4, 1…), quedarse con un INTERVALO
(«1 o 2») sin decimales y cruzarlo con lo que recibe el rival.

Lo que ya se midió NO es esa pregunta: §13.4 probó las K de goles contra el
1X2 (no agregan) y §15, la burbuja de goles contra la frecuencia propia en el
partido siguiente. Este backtest mide si acotan LOS GOLES de cada equipo:

| modelo | qué usa (todo anterior al partido) |
|---|---|
| G0 · a mano | la ventana de dos goles más repetida en los últimos 10 del equipo en su condición |
| G1 · frecuencia | la media de esos 10 (encogida hacia 1,45 de local · 1,15 de visita con 3 partidos de peso) |
| G2 · cruce | Poisson con lo que mete el que ataca EN SU CONDICIÓN, lo que recibe el otro EN LA SUYA, la localía y la μ del motor |
| G3 · + K | G2 más la K de goles anotados del que ataca y recibidos del que defiende (de la condición y totales) y la racha abierta de marcar / de recibir |

Ajuste con el 80 % de partidos más viejos, prueba en el 20 % más nuevo. Se
comparan el log-loss de los goles de cada equipo (por partido, bootstrap
emparejado), el **intervalo de dos goles** (cuánto acierta contra lo que
prometía), el **marcador acotado** (los cuatro marcadores de los dos
intervalos) y el exacto; y, en los mismos partidos con cuota, el MERCADO de
más/menos 2,5 y ambos marcan (log-loss y un valor de 1 unidad donde el modelo
ve 5+ puntos sobre el mercado). La guardia de cordura corta si la prueba sale
fuera de 0,8-2,2 goles por equipo.

Y **¿el marcador se repite?** (el usuario: «el marcador no se repite tanto;
cierto equipo que empata mucho empata con marcador diferente»): por equipo,
cuántas veces un partido repite el marcador del anterior —y un empate, el del
empate anterior— contra 200 permutaciones del orden de LOS MISMOS marcadores
del equipo. Razón < 1 con `pMenos` ≤ 0,025 es «se repite menos que el azar».

`test_backtest_goles` siembra un efecto real de la constante (G3 lo detecta y
pesan los coeficientes sembrados), uno de ruido (no inventa nada), una serie
que nunca repite (sale bajo el azar) y una al azar (queda en el azar).

Pendiente: correrlo en el servidor con `--padron` y anotar acá el resultado.
