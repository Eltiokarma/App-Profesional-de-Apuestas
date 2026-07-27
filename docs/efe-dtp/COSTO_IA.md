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

## Cómo saber si funciona

El log de cada corrida trae la cuenta, y es la medida real:

```
[efe] faltantes (0): ninguno        ← corrida más barata posible: sin búsquedas
[efe] despensa: 0 datos depositados ← nada nuevo que pagar
[dtp] fixture 123 · foco X (N=14) · modo dtp_completo · faltantes: ninguno
[timeline] 38 eventos de partido calculados · tope búsquedas: 4
```

En el timeline, esos 38 eventos son 38 que el modelo no buscó ni escribió. Si
el número sale en 0 con partidos que sí jugaron, el problema es de ingesta —el
período no está en `fixtures`—, y el modelo vuelve a pagar por buscarlos.

Con `faltantes: ninguno` no hay búsqueda web y la despensa no se re-emite. Si
aparecen faltantes de forma recurrente, el arreglo es de ingesta —correr
`backend.ingesta.jugadores` y `backend.ingesta.ficha_partido`, o cargar la
despensa en bloque—, no subir el presupuesto.
