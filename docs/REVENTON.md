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
  - `llegadas + salidas` de la ventana: ≥ 6 → `inestable`; ≥ 3 → `en transición`.
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
  **K-CERCA-EXTREMO** (tipo `dato`, calculada, no se deposita) en la tira.
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
