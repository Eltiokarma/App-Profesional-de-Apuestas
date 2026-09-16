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

Por el nivel del equipo (bin 0–9 del motor):

| bin | mandan | familia |
|---|---|---|
| ≥ 7 (alto) o ≤ 2 (bajo) | **globales** | `total` |
| 3–6 (medio) | **específicas** | la de la condición del próximo (`local` o `visita`); sin próximo, las dos |

La pantalla marca con ★ la familia que manda; las demás se ven, pero el
selector recuerda que no son las que pesan.

## 5. Riesgo de reventón (puntos con motivo)

Solo con burbuja abierta y reventones previos del mismo signo. Cada punto
viaja con su frase en `riesgo.motivos`:

| condición | pts |
|---|---|
| K actual ≥ mediana de K pico | +2 |
| (si no) K actual ≥ mínimo de K pico | +1 |
| K actual ≥ máximo de K pico («nunca aguantó tanta K») | +1 |
| racha ≥ mediana de partidos | +1 |
| racha ≥ máximo de partidos | +1 |
| próximo rival en zona (si la familia aplica) | +2 |

`nivel`: 0–1 **bajo** · 2–3 **medio** · 4–5 **alto** · ≥ 6 **muy alto**.
Sin reventones previos del signo: **sin base** (se dice; no se inventa un
número).

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
