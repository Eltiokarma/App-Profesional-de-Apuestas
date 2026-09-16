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
