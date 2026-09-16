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
  - ≥ 5 bajas → `en transición`.
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
