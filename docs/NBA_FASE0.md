# NBA · fase 0 · ¿la teoría SAD ve algo que la cuota no?

> Pedido del usuario (12/11/2026): extender la teoría a otros deportes,
> empezando por el básquet, **solo NBA**, mercados **ganador y hándicap**.
> La fase 0 **solo mide**: no hay ingesta diaria, ni pantalla, ni skill. Si la
> teoría no separa nada que la cuota no tenga ya, no se construye nada más.

## 1. Qué se corre

```bash
python -m backend.nba.descarga     # ESPN, sin clave → ./nba_data (fuera de git)
python -m backend.nba.fase0        # → nba_data/fase0.json y fase0.txt
python -m backend.test_nba_fase0   # sin red, en CI
```

- **Fuente.** La API pública de ESPN, que no está documentada y no pide clave:
  el marcador por día y, por partido, las cuotas de cada casa (ganador y
  hándicap del local, con su cuota). Hay cuotas desde 2015-16.
  - API-Basketball (de API-Sports) pediría su propia suscripción.
  - stats.nba.com no responde desde el contenedor.
  - Como la API de ESPN no está documentada, puede cambiar sin aviso. Para
    medir alcanza; para producción habría que ver una fuente con contrato.
- **Qué entra.** Temporada regular, play-in y playoffs entre las 30
  franquicias. Quedan afuera la pretemporada, el All-Star y los partidos de
  gira.
- **Cancha neutral.** La burbuja de Orlando (30/07 al 11/10/2020) es neutral
  aunque ESPN no la marque así; también los partidos en México y París.
- **La cuota.** Es la mediana entre casas, sin las líneas en vivo ni la de
  apertura. La probabilidad es 1/cuota normalizada, o sea sin el margen de la
  casa. Es la línea que ESPN deja como «actual», que en un partido terminado
  es la de cierre (aproximada: no hay hora de captura).
- **Nada entra a `sad.db`** ni a la app.

## 2. El motor llevado al básquet (`backend/nba/motor.py`)

Es la misma teoría de `docs/MOTOR_SAD_EXTRACCION.md`. Lo que cambia es lo que
el básquet obliga a cambiar, y cada cambio queda como parámetro a la vista. El
motor del fútbol no se toca.

| pieza | fútbol | NBA (fase 0) | por qué |
|---|---|---|---|
| P del nivel | puntos 3/1/0 ÷ 20 | 3 × victorias ÷ 20 | no hay empate; se mantiene la escala 0–3 |
| G del nivel | Σ(gf−ga)/Σ(gf+ga), últimos 5 | lo mismo × **ESCALA_G** | en básquet ese cociente ronda ±0,05 y sin escalar no pesa; la escala se elige **en el entrenamiento** |
| q | \|dif\| × res × nivel rival | (\|dif\| ÷ **10**) × res × nivel rival | ganar por 10 ≈ ganar por 1 gol |
| visita | × 1,4 | × 1,4 (**sin calibrar**) | se dejó el del fútbol |
| reventón | a 0 (empate) o al otro signo | **siempre al otro signo** | no hay empate: cada derrota corta la + y abre la − |
| nivel en el backtest | el guardado con fecha anterior | el previo al partido; **sin** regla retroactiva | con menos de 20 partidos previos no hay nivel y el partido no entra |
| cancha neutral | — | sin factor de visita, no mueve local/visita | burbuja 2020, partidos internacionales |
| descanso | `jugadores.dias_descanso` | el mismo (por horas; ≤ 1 día = back-to-back) | la guardia de arquitectura |

## 3. Qué se mide (`backend/nba/fase0.py`)

Es el método del backtest del 1X2 del fútbol (`docs/REVENTON.md` §13):
logística ajustada con el 80 % más viejo y evaluada en el 20 % más nuevo,
log-loss por partido y la diferencia con un IC bootstrap emparejado (500
remuestreos). «Mejora» quiere decir que el IC queda entero bajo 0.

- **Ganador.** Hay cuatro modelos que van sumando piezas:
  - G0: el nivel con la localía.
  - G1: más el descanso.
  - G2: más la racha y las K.
  - G3: más el reventón (racha sobre su mediana, K sobre la mediana de su
    pico, rival en la dirección del riesgo). Es la teoría entera.

  Después vienen **MK0**, que es la cuota sola, y **MK1**, la cuota más la
  teoría. Lo que importa para apostar es MK1 contra MK0. Se agrega una
  simulación plana a la cuota mediana cuando MK1 ve 3 puntos o más de
  ventaja; es indicativa y no es la rentabilidad.
- **Hándicap.** La pregunta es si el local cubre la línea (los push quedan
  afuera). El motor predice el margen con una regresión, y la ventaja es el
  margen predicho más la línea. La vara es ln 2 (una moneda al aire) y el
  52,4 % que hace falta para ganarle a −110. También se compara el error del
  margen del motor con el de la línea misma.
- **Reventón.** Se toma cada lado con una racha abierta y base propia (3 o
  más reventones de ese signo). Se compara qué tan seguido se corta la racha
  con lo que decía la cuota, por largo de racha. Después, la logística de la
  cuota sola contra la cuota más la burbuja.

## 4. Resultados (12/11/2026, primera corrida)

Datos: 14.336 partidos de 2015-16 a hoy (2026-27 va por 170), todos con
cuota. La temporada 2015-16 es solo arranque. Entrenamiento: hasta noviembre
de 2024. Prueba: 2.604 partidos desde el 19/11/2024.

**Localía.** El local gana entre 54 y 59 % según la temporada, con +1,2 a +3,1
puntos de margen. Bajó desde 2021 (55 %, contra 59 % antes de la pandemia).
La burbuja de 2020 sale con 175 partidos neutrales.

**ESCALA_G = 5**, elegida en el entrenamiento: log-loss de validación 0,6329,
contra 0,6342 sin la G y 0,6456 con escala 40. La G de puntos ayuda poco y
solo con poco peso.

### 4.1 Ganador

| modelo | log-loss | acierto |
|---|---|---|
| G0 · nivel + localía | 0,6217 | 65,7 % |
| G1 · + descanso | 0,6199 | 66,0 % |
| G2 · + racha y K | 0,6204 | 65,7 % |
| G3 · + reventón (la teoría entera) | 0,6207 | 66,0 % |
| **MK0 · la cuota sola** | **0,5776** | **69,2 %** |
| MK1 · cuota + la teoría | 0,5796 | 68,5 % |
| MK2 · cuota + descanso | 0,5771 | 69,2 % |

- El **descanso** mejora al nivel: −0,0019, IC [−0,0035, −0,0003]. La
  racha, las K y el reventón no agregan nada encima.
- La **cuota le gana al motor** por 0,044 de log-loss, IC [+0,034, +0,055]:
  es lejos, la mejor fuente.
- **La teoría sobre la cuota no agrega nada.** MK1 contra MK0 da +0,0020,
  IC [−0,0001, +0,0041]; si algo, empeora un poco. El descanso sobre la cuota
  da −0,0005, IC [−0,0010, +0,0001]: la cuota ya lo tiene.
- **Simulación plana.** Apostando cuando MK1 ve 3 puntos o más: 655 apuestas,
  ROI −5,2 %, IC [−13,8 %, +4,4 %]. No hay ventaja; es lo que cuesta el
  margen de la casa.

### 4.2 Hándicap

- **Error del margen (RMSE).** La línea se equivoca en 14,1 puntos; el motor,
  en 15,1 (y 15,0 con la teoría entera).
- **Cubrir la línea.** Ningún modelo se separa de la moneda al aire: H1 da
  −0,0002, IC [−0,0005, +0,0001], y la teoría entera da +0,0001.
- **Simulación.** Con un valor esperado de 3 % o más, el modelo casi nunca
  apuesta (una sola vez): no ve ventaja.

### 4.3 Reventón

26.040 lados con racha abierta y base propia (3 o más reventones del signo).
**Las rachas se cortan como dice la cuota.** La diferencia queda entre −3 y
+3 puntos en cada tramo de largo, sin patrón (la tabla está en `fase0.txt`).
Con las rachas de 9 o más el margen es de +2,8 en las positivas y +0,8 en
las negativas, con n de 252 y 365.

- **Cuota más burbuja contra cuota sola:** +0,0002, IC [−0,0002, +0,0006].
  No agrega.
- **La burbuja sola, sin la cuota,** sí predice el corte (log-loss 0,646). Los
  coeficientes van en el sentido de la teoría: el rival en zona de riesgo
  empuja al corte (+0,44) y la racha larga lo frena (−0,22). Pero la cuota
  sola es mucho mejor (−0,068) y ya contiene todo eso.

### 4.4 Lectura

Es lo mismo que en el fútbol (REVENTON §13.3), y más marcado. La teoría
**describe** bien (el nivel predice, la burbuja ve el corte con el sentido
correcto), pero **no ve nada que la cuota de cierre de la NBA no tenga ya**,
ni en ganador ni en hándicap. Según la regla de la fase 0, no se construye
ingesta, pantalla ni skill de NBA con esta teoría.

**Lo que queda abierto, si el usuario quiere seguir:**

1. **Contra la cuota de APERTURA** en vez de la de cierre. La de cierre es
   la más eficiente que existe. ESPN trae la apertura y el cierre separados
   desde ~2022-23; habría que medir si la teoría anticipa el movimiento de la
   línea.
2. **Las bajas de jugadores** (el EFE del básquet). Es lo que más mueve una
   línea de la NBA, y la teoría de rachas no lo ve.
3. **Otras ligas de básquet**, menos eficientes. La Euroliga quedó afuera a
   pedido del usuario.

## 5. Las burbujas de esta temporada, los 20 de mayor nivel (12/11/2026)

`python -m backend.nba.burbujas` (→ `nba_data/burbujas.txt`). A pedido del
usuario, no es otro backtest de miles de partidos. Es la pantalla de Burbujas
del fútbol llevada a la NBA, solo sobre la temporada 2026-27 (170 partidos al
12/11) y solo sobre los **20 equipos de mayor nivel del motor hoy**.

- **El riesgo es el del fútbol.** Se usan las mismas reglas y puntos de
  `backend/analisis/burbuja.py`, importados y no copiados: racha ≥ mediana +1,
  rival fuerte o muy fuerte en la dirección del riesgo +1 o +2, favorito −1 o
  muy favorito −3, contramano +1.
- **El motor recorre la historia entera** porque la necesita. El nivel pide 20
  partidos, y en noviembre nadie llegó a 20 en la temporada. La base de cada
  equipo son sus reventones previos, igual que en el fútbol. Lo que se mide es
  solo la temporada.

**La guía en la temporada** (228 lados de los 20 con burbuja y base):

| riesgo | n | se cortó | la cuota decía | fútbol (backtest) |
|---|---|---|---|---|
| bajo | 45 | 27 % | 27 % | 40–50 % |
| medio | 39 | 36 % | 38 % | 55 % |
| alto | 96 | 45 % | 50 % | 62–67 % |
| muy alto | 48 | 62 % | 64 % | 71–75 % |

- **La guía ordena bien:** a más riesgo, más corte, igual que en el fútbol.
  Las tasas son más bajas porque en la NBA no hay empate que corte la racha.
- **La cuota dice lo mismo, tramo por tramo.** Es lo mismo que en el §4.3: la
  guía describe, pero no le gana a la cuota.
- **La mediana de racha de casi todos es 1 o 2.** Sin empate las rachas son
  cortas, así que «racha ≥ mediana» suma casi siempre. En el básquet esa
  regla discrimina poco.
- **La base sale de toda la historia desde 2015** (200 o más reventones por
  equipo, con planteles que ya no existen). Si la guía se usara en serio,
  habría que acotarla, por ejemplo a las últimas 2 temporadas.
- **n chico:** es una foto de un mes, no una medición.

### 5.1 La K separada: burbuja de victorias y burbuja de derrotas (12/11/2026)

Pedido del usuario: como no hay empate, tratar la K como la de goles («anotás
o no anotás»). Quedan dos familias, cada una con su propia base:

- **Victorias:** crece con cada victoria (|q|) y revienta **a cero** con la
  primera derrota.
- **Derrotas:** crece con cada derrota (en positivo: cuánto lleva perdiendo) y
  revienta a cero con la primera victoria.

Está en `motor.FAMILIAS` y `_vista_familia`, y `burbujas.py` las muestra por
separado.

**Matemáticamente son los mismos episodios que el tramo + y el tramo − de la
K fusionada.** Comparadas en los 28.672 partidos-equipo, desde 2015, no hay
ni una diferencia: misma racha, misma K (en valor absoluto) y misma base de
reventones. El test lo controla. En el fútbol la separación sí cambia algo,
porque el empate deja la K en 0 sin abrir la contraria. En el básquet siempre
hay exactamente una familia abierta. Lo que cambia es la LECTURA: cada familia
con su base y su guía.

**La guía, por familia, en la temporada** (los 20; n chico):

| riesgo | victorias: n · se cortó · cuota | derrotas: n · se cortó · cuota |
|---|---|---|
| bajo | 38 · 18 % · 26 % | 7 · 71 % · 32 % |
| medio | 26 · 27 % · 35 % | 13 · 54 % · 43 % |
| alto | 52 · 38 % · 48 % | 44 · 52 % · 52 % |
| muy alto | 18 · 56 % · 57 % | 30 · 67 % · 67 % |

En las dos familias la guía ordena. Las rachas de victorias de estos 20 se
cortaron MENOS de lo que decía la cuota (unos 8 a 10 puntos), y las de derrotas
se cortaron más en los tramos bajos. **Pero eso es casi seguro un sesgo de
selección:** los 20 se eligieron por el nivel de HOY, o sea por cómo les fue en
este arranque, así que la muestra junta a los que ganaron más de lo esperado.
Para saber si hay algo, la medición limpia elegiría a los 20 por el nivel de
ANTES de la temporada. La medición contra el mercado del §4.3 (26.040 rachas,
sin selección) no encontró nada.

**El control del sesgo** (`python -m backend.nba.burbujas --inicio`: los 20
elegidos por el nivel de ANTES de la temporada):

| riesgo | victorias 26-27 | victorias 25-26 | victorias 24-25 | derrotas 26-27 | derrotas 25-26 | derrotas 24-25 |
|---|---|---|---|---|---|---|
| bajo | 18 % vs 26 % (38) | 23 vs 24 (276) | 25 vs 24 (284) | 44 vs 30 (9) | 26 vs 28 (141) | 32 vs 31 (152) |
| medio | 29 vs 36 (21) | 37 vs 40 (147) | 31 vs 36 (129) | 44 vs 38 (16) | 45 vs 45 (112) | 42 vs 45 (105) |
| alto | 46 vs 49 (46) | 50 vs 48 (383) | 52 vs 47 (389) | 47 vs 50 (49) | 59 vs 54 (333) | 56 vs 53 (383) |
| muy alto | 57 vs 56 (14) | 53 vs 57 (201) | 59 vs 59 (189) | 56 vs 65 (34) | 64 vs 69 (210) | 68 vs 68 (171) |

(se cortó vs la cuota decía, con el n entre paréntesis)

- **Sin el sesgo,** la ventaja de este arranque se achica (18 contra 26 % en
  victorias de riesgo bajo, con n 38).
- **En las dos temporadas completas anteriores** (unas 1.800 rachas por
  temporada) la cuota y lo que pasó quedan a ±5 puntos, sin una dirección que
  se repita, salvo un detalle chico: las rachas de victorias de riesgo
  **medio** se cortaron 3 a 5 puntos menos que lo que decía la cuota en las
  dos temporadas. Con n de alrededor de 140 por temporada, eso no alcanza para
  afirmar nada.
- **Conclusión:** la misma de la fase 0. La guía ordena, pero la cuota ya lo
  sabe.

### 5.2 La lectura de momentum completa, SIN cuotas (12/11/2026)

Pedido del usuario: «las burbujas no son cuota, son un análisis del
momentum». Las comparaciones con la cuota de §5 y §5.1 eran para evaluar si
la guía sirve para apostar, que no es su trabajo (REVENTON: «guía, no
probabilidad»). `python -m backend.nba.burbujas` queda como lectura de
momentum pura, sin ninguna cuota:

- **Por familia** (victorias y derrotas), la burbuja abierta: racha y K.
- **Su POSICIÓN frente a los cortes de esa familia:** en toda la historia y en
  los últimos 20 cortes (el «período» del fútbol), el percentil de la K y de
  la racha, la K sobre la mediana y los récords.
- **EXTREMO 🔴 y CERCA DEL EXTREMO 🟠,** con la regla del fútbol importada
  (`burbuja._extremo`: récord superado con 3+ partidos, o la franja del 90 %).
- **RÉCORD DEL PERÍODO 🟡,** que es nuevo y va aparte: la burbuja ya pasó todo
  lo de sus últimos 20 cortes. La historia arranca en 2015, y sus récords son
  de planteles que ya no existen. El extremo sigue siendo contra toda la
  historia, como en el fútbol.
- **El riesgo de reventón** con los puntos y motivos del fútbol, ante el
  próximo rival y por el NIVEL del motor.
- **La familia en cero:** cuándo y cómo terminó su última burbuja.
- **Cómo ordenó la guía en la temporada:** cuántas burbujas se cortaron en
  cada nivel de riesgo (frecuencia de lo que pasó), con la referencia del
  fútbol al lado.

Al 12/11, entre los 20 no hay ningún extremo 🔴. Hay tres en 🟠:
- **SA:** victorias, 10 partidos, K 36,3, que es 7,1 veces su mediana; está
  por encima del 98 % de sus cortes en K y del 99 % en racha.
- **LAL:** victorias, 7 partidos, K 18,0, 4,3 veces su mediana.
- **BOS:** victorias, 5 partidos, K 25,7. Además está en 🟡: supera el récord
  de K de sus últimos 20 cortes (21,6) e iguala su racha más larga (5).
