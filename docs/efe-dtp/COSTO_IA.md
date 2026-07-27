# El costo de la IA — qué pagamos y qué dejamos de pagar

Los skills (EFE, timeline, DTP) son la única parte de la app que cuesta dinero
por uso. Este documento es la contabilidad: dónde se va el dinero, qué ya se
movió a código, y qué queda que valga la pena pagar.

La regla que ordena todo:

> **Si el dato es nuestro, se calcula. Si el dato es del mundo, se busca. Si es
> un juicio, se paga.**

Un modelo cobrando por deducir cuántas derrotas seguidas lleva un rival —cuando
ese número está en nuestra propia base— no es análisis: es una consulta SQL con
factura.

## De dónde sale el costo, en orden

1. **Búsquedas web.** Cada una arrastra el contenido de las páginas al contexto.
   Es, con diferencia, el rubro más caro de una corrida.
2. **Tokens de razonamiento.** Sonnet piensa por defecto con esfuerzo alto si no
   se le dice otra cosa, y ese pensamiento se paga a precio de salida.
3. **Tokens de salida.** Todo lo que el modelo escribe, incluido lo que solo
   copia de la entrada.
4. **Tokens de entrada.** Los más baratos, y encima cacheados (el protocolo va
   con `cache_control`).

## Lo que ya NO se paga

| Bloque | Antes | Ahora | Dónde |
|---|---|---|---|
| C · constantes K | investigado y puntuado | el analista lee las K en la app | `SAD_EFE_CON_K` (apagado) |
| G · calendario y mapa de rivales | buscado en la web y deducido | calculado de `sad.db` con el criterio numérico del protocolo | `backend/calendario.py` |
| tabla · resultados | buscados | de nuestra ingesta | `_datos_locales` |
| plantel · dt · bajas | buscados | de la capa de jugadores | `jugadores.resumen_para_skills` |
| xi_reciente | buscado | de API-Football (plan ya pagado) | `_xi_y_bajas` |
| despensa | re-emitida en cada análisis | solo si algo faltaba | `SALIDA_EFE_CALIENTE` |
| DTP completo | — | nunca busca en la web | `con_busqueda=False` |
| timeline · partidos y tabla | buscados y copiados uno por uno | calculados de `sad.db` e insertados por código | `backend/cronologia.py` |

Con la ingesta al día, **los siete tipos que consume el EFE tienen fuente local**.
El presupuesto de búsquedas es proporcional a lo que falta
(`3 + 2 × faltantes`), así que "no falta nada" significa literalmente cero
búsquedas y la corrida más barata posible.

### El bloque G, en detalle

Es el recorte más reciente y el más ilustrativo. El protocolo define siete
etiquetas de rival con criterio numérico explícito, y seis salen de datos que ya
tenemos:

| Etiqueta | Criterio | Fuente |
|---|---|---|
| RECIÉN ASCENDIDO | ascendió la última temporada | primera temporada del club en esa liga |
| EQUIPO SORPRESA | rinde sobre su expectativa | gap §5 del motor |
| LOCAL FUERTE | ≥70% de victorias en casa | conteo de sus partidos |
| VISITA DÉBIL | <25% de victorias fuera | conteo de sus partidos |
| EN CRISIS | 3+ derrotas seguidas o DT nuevo ≤4 semanas | resultados + `entrenadores` |
| BLOQUE BAJO | esquema con 5 defensores | formación dominante en `alineaciones` |
| CLÁSICO | rivalidad histórica | **PARCIAL**: solo derbi de ciudad |

Se ahorra tres veces: no se busca (entrada), no se deduce (razonamiento) y no se
copia a la salida — el `calendario` del EFE lo rellena el código después de la
llamada, con `items_para_efe()`.

`CLÁSICO` es el único que queda a medias, y va marcado `parcial: true`. Que no
aparezca no prueba que no haya rivalidad; solo que no era de ciudad. Preferimos
un hueco declarado a un dato cómodo.

### El timeline, en detalle

Mismo recorte, otro skill. Un timeline de seis meses son ~30-40 partidos **por
equipo**, y hasta aquí el modelo los pagaba tres veces: los buscaba en la web
(`"[Equipo] resultados [liga] [año]"`, `"[Equipo] tabla posiciones"`), deducía
de qué lado cayó cada uno, y después los escribía uno por uno en el JSON —
fecha, marcador, jornada, rival— para que el frontend los pintara.

Todo eso está en `fixtures` desde la ingesta. Ahora lo calcula
`backend/cronologia.py`:

| Pieza del esquema TIMELINE | Fuente |
|---|---|
| eventos `resultado` / `derrota` / `empate` | partidos terminados del período |
| `marcador` y `jornada` | `fulltime_*` (regla de 90') y `league_round` |
| enfrentamiento directo (`equipo: "ambos"`) | el fixture que enfrenta a los dos |
| `equipos[].stats` (posición, puntos, última victoria) | la tabla del año |

El modelo recibe la orden de devolver `eventos` **solo** con lo institucional
—crisis, sanciones, cambios de DT, hitos— y el código funde ambas listas en
orden cronológico. Si igual copia un partido, se descarta: nuestro marcador
viene de la ingesta, no de una página.

Con dos de los cuatro patrones de búsqueda del protocolo sin nada que traer, el
techo baja de 8 a 4 (`SAD_TL_BUSQUEDAS_CALC`) — bajar el techo *es* el ahorro:
el modelo administra lo que le den, y lo que le sobra lo gasta.

En vez de la lista de resultados, el prompt recibe una línea con el balance
(`"12G 4E 6D en el período"` + los últimos cinco), que es lo único que la
narrativa necesita. Y la despensa del timeline pasa a guardar **solo** eventos
institucionales: sellar los partidos sería congelar mañana lo que hoy se
recalcula gratis, y con el marcador al día si la ingesta corrige un resultado.

## Lo que SÍ vale la pena pagar

Lo que queda es lo que no se puede calcular:

- **Los bloques de juicio del EFE** (A/B/D/E, matchup H, lectura SAD): pesar
  señales que se contradicen y decir qué manda.
- **El DTP**: leer la mecánica de un gol, nombrar la grieta, escribir un
  pronóstico que después se pueda declarar fallado.
- **La cadena**: el veredicto contra lo que se dijo antes. Es el único juicio de
  la app que se puede auditar, y por eso se defiende con la regla
  anti-hindsight — sin pronóstico previo, `veredicto: ""`.

Prescindir de esto sería quedarnos con una calculadora. La reducción va contra
el trabajo mecánico, no contra la interpretación.

## Perillas (variables de entorno en Railway)

| Variable | Default | Para qué |
|---|---|---|
| `SAD_EFE_EFFORT` | `medium` | esfuerzo de razonamiento; `high` multiplica el gasto |
| `SAD_EFE_BUSQUEDAS` | `18` | techo duro de búsquedas por corrida |
| `SAD_EFE_MAX_FALTANTES` | `6` | candado del análisis frío (bloquea antes de gastar) |
| `SAD_DESPENSA_CADENCIA_DIAS` | `15` | cada cuánto se barre la despensa; el TTL se deriva de aquí |
| `SAD_EFE_MODELO` | `claude-sonnet-5` | el modelo del EFE/DTP |
| `SAD_TL_MODELO` | Haiku 4.5 | el timeline no necesita más |
| `SAD_TL_BUSQUEDAS` | `8` | techo del timeline cuando no hay partidos calculados |
| `SAD_TL_BUSQUEDAS_CALC` | `4` | techo del timeline con los partidos ya calculados |
| `SAD_EFE_CON_K` | apagado | reactiva el bloque C si alguna vez se quiere de vuelta |

### La ventana cara, cerrada en el código

Un TTL más corto que el barrido dejaba **un día de cada quince en que todo EFE
salía caro**: la despensa vencía justo antes del refresco y volvían las
búsquedas. Pedirle al operador que pusiera una variable no lo arreglaba — solo
movía el problema a que alguien se acordara.

Ahora hay dos capas, ambas en código:

1. **El TTL se deriva de la cadencia** (`SAD_DESPENSA_CADENCIA_DIAS` + 2 días de
   margen). No hay dos números que puedan desalinearse.
2. **Gracia de un ciclo para `dt` y `plantel`** — los únicos tipos que dependen
   de la despensa, ahora que el calendario y la tabla se calculan. Si un barrido
   se atrasa, el dato vencido se sirve igual **declarando su edad** en vez de
   disparar una búsqueda, y el prompt lo recibe en `datos_anejos` con la orden
   de no darlo por confirmado. Pasada la gracia vuelve a faltar.

Es el mismo criterio de siempre: preferimos un dato con su edad a la vista antes
que uno cómodo, y preferimos los dos antes que una factura.

## El chequeo previo: saberlo ANTES de pulsar

El candado de análisis frío evita la catástrofe, pero solo la catástrofe. Con
el umbral en 6, un partido al que le faltan **4** campos pasa el candado sin
decir nada y son 11 búsquedas: **medio dólar**, descubierto con la factura.

`GET /analisis/efe/preflight/{fixtureId}` responde eso antes de gastar. No
llama a ningún modelo y no consume cuota de API-Football: resuelve las fuentes
con la **misma función** que la corrida real (`_resolver_fuentes`) y devuelve,
por equipo y por tipo, de dónde va a salir el dato:

| Origen | Qué significa | Cuesta |
|---|---|---|
| `local` | sad.db o la capa de jugadores | nada |
| `despensa` | investigado antes y todavía fresco | nada |
| `anejo` | vencido pero servible, con su edad declarada | nada |
| `api` | API-Football al generar | cuota del plan, no dólares |
| `falta` | **no lo tenemos: búsqueda web** | esto es lo que se paga |

Que sea la misma función no es un detalle de implementación: un preflight que
estimara por su cuenta empezaría a mentir el día que alguien cambiara el orden
de resolución, y una pantalla de costo que miente es peor que no tenerla.

`bajas` es el único que se declara **dudoso**: depende de que API-Football
reporte lesionados de ese partido, y eso no se sabe sin gastar la request. Va
en el máximo del rango en vez de darse por resuelto.

### Estimado vs medido

Cada llamada ya calculaba su costo real para el log; ahora además se guarda
(tabla `corridas`). Con tres o más corridas de tamaño parecido, el preflight
deja de estimar y devuelve el **rango real de lo que costaron**, marcado
`MEDIDO ×n`. Mientras no las haya, usa la fórmula y lo marca `ESTIMADO`.

### El error que costó 60 centavos: creer que sin búsquedas no se paga

La primera versión de este documento —y del preflight— daba **~$0.05** para una
corrida sin faltantes. Un EFE real con el semáforo en verde, cero búsquedas y
todo cargado costó **$0.60**. La estimación no estaba imprecisa: estaba
conceptualmente mal.

Con 0 búsquedas se sigue pagando, y el reparto es este:

| Concepto | Tokens | Costo |
|---|---|---|
| system (protocolo EFE + API) | ~11k, cacheados | $0.03 la 1ª vez, $0.002 después |
| payload de entrada | 2-4k | ~$0.01 |
| JSON de salida | 2-5k | $0.02-0.05 |
| **razonamiento** | **decenas de miles** | **el sumando grande** |

El razonamiento se cobra **a precio de salida**, igual que el JSON, y con
`SAD_EFE_EFFORT=medium` sobre un protocolo de 9k tokens puede ser 10-40× el
tamaño de la respuesta. `SAD_EFE_MAX_TOKENS` está en 64000: el techo permite
esa factura sin avisar.

De ahí dos cambios:

1. El rango base pasó a **$0.10-$0.50** y es ancho **a propósito** — esa anchura
   dice "todavía no lo sabemos". Se estrecha con mediciones, no con optimismo.
2. `corridas` guarda ahora el **reparto del output**: cuánto fue JSON y cuánto
   razonamiento. Se cuentan los caracteres reales de cada bloque de la respuesta
   y se reparte el `output_tokens` cobrado en esa proporción, así que el
   desglose suma exactamente lo facturado.

El diagnóstico que habilita: si la barra del panel sale casi toda ámbar, el
dinero **no** está en lo que se escribe ni en lo que se busca — está en lo que
se piensa, y eso no se arregla con más despensa sino bajando `SAD_EFE_EFFORT`.

### Lo ya gastado, no lo que va a costar

Una estimación mira hacia adelante y puede equivocarse. El panel muestra además
**lo que ya se pagó en ese partido**, sumando todas las corridas: el EFE, sus
regeneraciones, el timeline y el DTP. Es la cifra que aparece en la factura y no
coincide con "lo que costó la última corrida" — tres regeneraciones de $0.20 son
$0.60, y hasta aquí eso no se veía en ninguna pantalla.

Se suman también los intentos fallidos: el cargo existió aunque el análisis se
descartara por venir vacío.

### Lo que el chequeo destapó

La despensa en bloque del repo tiene los nueve países de Sudamérica, pero
**solo `dt` está relleno**: `plantel` y `bajas` están vacíos en las nueve ligas
(salvo 8 equipos de Perú). Como la regla es que un campo sin fuente va vacío y
no rellenado a ojo, el archivo es honesto — pero el efecto práctico es que
cualquier EFE fuera de Perú arranca con 4 faltantes, pasa el candado y cuesta
~$0.50.

La salida barata no es subir el umbral: `plantel` y `bajas` los da gratis la
capa de jugadores desde API-Football. Con `python -m backend.ingesta.jugadores`
corrido sobre esos equipos, esos cuatro faltantes desaparecen y el mismo
análisis baja a ~$0.05. El preflight lo dice con esas palabras en sus
recomendaciones.

## Cómo saber si funciona

El log de cada corrida trae la cuenta, y es la medida real:

```
[efe] faltantes (0): ninguno        ← corrida más barata posible: sin búsquedas
[efe] despensa: 0 datos depositados ← nada nuevo que pagar
[dtp] fixture 123 · foco X (N=14) · modo dtp_completo · faltantes: ninguno
[timeline] 38 eventos de partido calculados · tope búsquedas: 4
[efe] claude-sonnet-5 · in=3120 out=48210 (json≈4100 pensamiento≈44110)
      cache_write=0 cache_read=11020 busqueda=no hechas=0 costo≈$0.49
```

Esa última línea es la que hay que leer cuando el número sorprenda. `hechas=0`
con `costo≈$0.49` significa que **no se buscó nada y aun así se pagó**: mira
`pensamiento≈`. Si es 10× el `json≈`, el gasto está en el esfuerzo de
razonamiento y la palanca es `SAD_EFE_EFFORT`, no la despensa.

En el timeline, esos 38 eventos son 38 que el modelo no buscó ni escribió. Si
el número sale en 0 con partidos que sí jugaron, el problema es de ingesta —el
período no está en `fixtures`—, y el modelo vuelve a pagar por buscarlos.

Con `faltantes: ninguno` no hay búsqueda web y la despensa no se re-emite. Si
aparecen faltantes de forma recurrente, el arreglo es de ingesta —correr
`backend.ingesta.jugadores` y `backend.ingesta.ficha_partido`, o cargar la
despensa en bloque—, no subir el presupuesto.
