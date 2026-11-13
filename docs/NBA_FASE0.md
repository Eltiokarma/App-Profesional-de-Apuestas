# NBA · fase 0 · ¿la teoría SAD ve algo que la cuota no?

> Pedido del usuario (12/11/2026): extender la teoría a otros deportes,
> empezando por el básquet, **solo NBA**, mercados **ganador y hándicap**.
> La fase 0 **solo mide**: no hay ingesta diaria, ni pantalla, ni skill.
>
> **CORRECCIÓN DEL USUARIO (12/11/2026): la vara de esta fase estaba mal.**
> El sistema no busca ganarle a la cuota ni sacarle valor (`docs/METODO_APUESTA.md`:
> «no le ganamos en probabilidades a la casa; lo nuestro es el win rate y
> saber dónde poner la plata, aunque la cuota sea 1.02»). Decidimos ANTES
> dónde explota, se acaba o vuelve el momentum, y apostamos a nuestro
> elegido; que la cuota coincida es una CONFIRMACIÓN, no un fracaso. Las
> secciones 4.1 a 4.4 miden «¿le gana a la cuota?» y deben leerse como
> contexto, no como veredicto. El veredicto con la vara correcta está en §6.

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

## 6. Con la vara del sistema: win rate y dónde poner la plata (12/11/2026)

La pregunta no es si la burbuja le gana a la cuota, sino si dice **dónde** el
momentum sigue o se corta con un win rate alto. Se cuentan las burbujas
abiertas de los 20 de mayor nivel al arrancar cada temporada, sin sesgo de
selección (`--inicio`, §5.1).

| tramo | lectura | 24-25 | 25-26 | 26-27 (hasta hoy) |
|---|---|---|---|---|
| victorias, riesgo **bajo** | la racha SIGUE: apostar a que gana | 75 % (284) | 77 % (276) | 82 % (38) |
| victorias, riesgo **muy alto** | la racha se corta: no apostar a que siga | se cortó 59 % (189) | 53 % (201) | 57 % (14) |
| derrotas, riesgo **muy alto** | la mala racha SE CORTA: apostar a que gana | 68 % (171) | 64 % (210) | 56 % (34) |
| derrotas, riesgo **bajo** | la mala racha sigue: apostar al rival | 69 % (152) | 74 % (141) | 56 % (9) |

(% de veces que se cumplió la lectura; n entre paréntesis)

- **Victorias de riesgo bajo:** 3 de cada 4 veces la racha siguió, en las dos
  temporadas completas y en esta.
- **Derrotas de riesgo muy alto:** 2 de cada 3 veces la mala racha se cortó
  en las temporadas completas. En esta temporada la muestra todavía es chica.
- **El riesgo muy alto en victorias** sirve como FRENO: la racha se corta más
  o menos la mitad de las veces, así que ahí no se carga.

Que la cuota diga más o menos lo mismo (§4.3) es la confirmación. Lo que
falta, si se sigue, es lo que pide el método: los tramos con el freno de
`METODO_APUESTA.md` y la simulación proporcional sobre estas lecturas.

### 6.1 Los otros 10 equipos de la liga (12/11/2026)

`python -m backend.nba.burbujas --desde 21 --top 30`: los puestos 21 a 30 por
nivel. Para medir sin sesgo, con `--inicio`: los 10 de menor nivel al
ARRANCAR cada temporada.

| tramo (los 10 de abajo) | lectura | 24-25 | 25-26 | 26-27 |
|---|---|---|---|---|
| derrotas, riesgo **bajo** | la mala racha SIGUE: apostar al rival | 79 % (204) | 82 % (208) | 93 % (28) |
| victorias, riesgo **muy alto** | su racha buena se corta: apostar al rival | 75 % (72) | 66 % (71) | 67 % (9) |
| victorias, riesgo **bajo** | su racha buena sigue | 70 % (54) | 78 % (32) | — |
| derrotas, riesgo **muy alto** | la mala racha se corta | 50 % (86) | 52 % (115) | 56 % (16) |

(% de veces que se cumplió la lectura; n entre paréntesis)

- **El tramo más firme de toda la liga es el de los de abajo con la mala
  racha de riesgo bajo:** 4 de cada 5 veces siguen perdiendo, en las dos
  temporadas completas.
- **Para los de abajo, la «mala racha que se corta» es una moneda** (50 %),
  así que no es lugar para la plata. Para los de arriba sí lo era (64–68 %,
  §6): la misma señal pesa distinto según quién sea el equipo.

**Hoy** (al 12/11):
- **MIL está en 🔴 EXTREMO:** 8 derrotas seguidas, la peor racha de K y de
  largo de toda su historia en la base.
- **En 🟠 cerca del extremo,** con derrotas: CHI (8), UTAH (10), WSH (5) y NO
  (4).
- **Con derrotas de riesgo bajo:** UTAH contra HOU, CHI contra ATL, WSH contra
  DET, SAC contra POR y LAC contra OKC.
- **IND:** victorias de riesgo muy alto contra NY.

## 7. ¿Hasta qué escalón baja la teoría? (12/11/2026)

`python -m backend.nba.descarga --liga <slug>` (solo marcadores, ESPN gratis,
un pedido por día) y `python -m backend.nba.ligas` (→ `nba_data/ligas.txt`).
Pedido del usuario: un estudio proporcional al de las ligas de fútbol, sin
gastar, con los años necesarios. La primera temporada de cada liga solo
calienta el nivel. La Euroliga no está en ESPN.

Los cuatro tramos de la NBA (§6 y §6.1), con «arriba» y «abajo» como tercios
de nivel al ARRANCAR la temporada. El porcentaje es la parte de los casos en
que se cumplió la lectura:

| liga | equipos | temporadas medidas | A arriba, victorias, riesgo bajo: sigue | B arriba, derrotas, muy alto: se corta | C abajo, derrotas, riesgo bajo: sigue | D abajo, victorias, muy alto: se corta |
|---|---|---|---|---|---|---|
| NBA (ref.) | 30 | 2022-23 → hoy | 76 % ✓ | 67 % | 79 % ✓ | 68 % |
| **NCAA D1** | 366 | 2022-23 → 2025-26 | **81 % ✓** | **74 % ✓** | **81 % ✓** | **73 % ✓** |
| WNBA | 15 | 2022 → 2026 | 74 % ✓ | 69 % | 78 % ✓ | 68 % |
| NBL Australia | 10 | 2023-24 → hoy | 70 % | 60 % | 71 % | 82 % (27) |
| **G League (liga B)** | 31 | 2022-23 → 2025-26 | 64 % | 56 % | 67 % | 57 % |

✓ = firme: en TODAS sus temporadas con 30 o más casos acertó 65 % o más.

**NCAA por la fuerza de la CONFERENCIA** (el escalón subregional, tercios de
las ~32 conferencias por el nivel medio de sus equipos): A 82 % ✓ · B 70 % ✓ ·
C 83 % ✓ · D 68 % ✓. **Se sostiene también en las conferencias chicas.**

### Lectura

- **El límite no es la profundidad geográfica.** La teoría baja hasta las
  conferencias más chicas de la NCAA, con 366 equipos y los 4 tramos firmes en
  las 4 temporadas.
- **El límite es la ESTABILIDAD del plantel.** La G League es la liga B de la
  NBA: los jugadores suben y bajan de la NBA durante la temporada. Ahí ningún
  tramo es firme, y dos temporadas caen al 49 % (B) o al 53-56 % (D). Es lo
  mismo que ya hacemos en el fútbol: la liga B no.
- **NBL Australia:** con 10 equipos casi ninguna temporada junta 30 casos.
  Apunta en la misma dirección, pero falta muestra para afirmarlo.
- **La WNBA** aguanta como la NBA.
- **Ojo con la NCAA:** sus porcentajes altos vienen en buena parte de las
  diferencias enormes de nivel (un grande contra uno de conferencia chica).
  La lectura es correcta, pero las cuotas de esos partidos son muy bajas.
  Para el sistema (`docs/METODO_APUESTA.md`: «aunque la cuota sea 1.02») eso
  no es un problema.

## 8. Las fases que siguen (propuesta, 12/11/2026; no decidida)

Valen para el básquet y para el tenis. La fase 0 (medir) está cerrada.

1. **Fase 1 · datos diarios.** La ingesta automática de ESPN: los resultados
   de ayer y la agenda de los próximos días, en sus propias bases y nunca en
   `sad.db`, para no subir la factura de Railway. Corre una vez al día, igual
   que la corrida del fútbol.
2. **Fase 2 · la lectura en la app.** Contrato primero (`docs/openapi.yaml`):
   los endpoints de momentum por equipo o jugador y la pantalla de Burbujas
   con selector de deporte. Es la misma lectura de `burbujas.py`, pero
   visible.
3. **Fase 3 · el elegido y su aprendizaje.** Una regla escrita de dónde va la
   plata, partido por partido (los tramos A-D con su nivel de riesgo), el
   veredicto después del partido y su win rate por tramo. Es el bucle de
   Aprendizaje del fútbol, pero calculado y sin IA.
4. **Fase 4 · la simulación del método.** El proporcional con freno por tramo
   (`docs/METODO_APUESTA.md`) sobre los elegidos de la fase 3, contando desde
   que empiezan a registrarse.
5. **Fase 5 · la capa de juego (si hace falta).** El equivalente del EFE: las
   bajas, el descanso y los viajes en el básquet; la superficie y la fatiga de
   las rondas en el tenis. Solo si la fase 3 muestra fallos que el momentum no
   ve.

## 9. Servilleta: ¿más rentable que el fútbol? (12/11/2026)

Pedido del usuario: antes de pagar una API para otro deporte, saber cuál es
más rentable. Rentable = el win rate de nuestro elegido contra lo que pide la
cuota (1/cuota): si se acierta más de lo que la cuota pide, se gana. Es la
misma cuenta que hace el freno de `docs/METODO_APUESTA.md`.

**NBA,** los cuatro tramos apostados planos a la cuota de cierre de ESPN
(2023-24 → hoy, 1.680 apuestas):

| tramo | acierto | la cuota pedía | cuota media | ROI |
|---|---|---|---|---|
| A · arriba sigue ganando | 77 % | 80 % | 1,25 | −5,3 % |
| B · arriba corta la mala | 67 % | 73 % | 1,36 | −10,9 % |
| C · abajo sigue perdiendo (al rival) | 82 % | 82 % | 1,22 | −0,2 % |
| D · abajo se le corta (al rival) | 68 % | 73 % | 1,37 | −8,3 % |
| **todo** | **76 %** | **79 %** | | **−4,6 %** |

**Fútbol** (`docs/METODO_APUESTA.md`): con los skills, el win rate del
elegido fue de 55,6 % contra el 54,8 % que pedía la cuota en total, y de
61,3 % contra 55,6 % desde el 28/10. La simulación del método va de 100 a
125,59.

**Tenis:** no hay cuotas que se puedan bajar desde el contenedor, así que no
se puede hacer la cuenta.

**Lectura:** en la NBA el momentum solo acierta mucho, pero la cuota de la
NBA ya lo pide (aciertos de 77-82 % a cuotas de 1,2-1,4). Con el método
proporcional, el freno pausaría A, B y D, y C quedaría en empate. **Para
empezar, el fútbol es lo rentable;** la NBA con solo momentum no lo es. El
tenis queda sin medir hasta tener cuotas.

### 9.1 Con el método real: seguir a la casa, salvo que la burbuja diga «desconfiá» (12/11/2026)

El usuario corrigió la servilleta: el método no apuesta a las lecturas de
momentum. **Sigue al favorito de la casa** y la burbuja es la que dice «aquí
no». Es la alerta `BURBUJA-DE-UN-PARTIDO` de `simulacion.alerta_confianza`
(10/11/2026): la racha + del elegido es de UN solo partido y tiene riesgo
alto o muy alto. La otra pieza, `SOBRE-LA-CASA`, necesita el 1X2 de los
skills; sin análisis nuestra probabilidad es la de la casa y no se enciende.

En la NBA: el elegido es el favorito de cierre de ESPN, apostado plano a su
cuota mediana.

| | 2016-17 → 2022-23 | 2023-24 → hoy |
|---|---|---|
| todos los favoritos | 67,2 % vs pide 70,2 % · ROI −4,1 % (8.820) | 69,1 % vs 71,6 % · **−3,6 %** (4.102) |
| con DESCONFIAR (no se apuesta) | 62,8 % vs 65,4 % · −3,9 % (964) | 58,7 % vs 65,8 % · **−10,7 %** (429) |
| **sin alerta (el método)** | 67,8 % vs 70,8 % · −4,1 % (7.856) | 70,4 % vs 72,3 % · **−2,8 %** (3.673) |

- **La alerta hace su trabajo.** Los favoritos marcados rinden por debajo de
  su cuota: 2,6 puntos en el período viejo y 7,1 en el reciente. Sacarlos
  achica la pérdida, de −3,6 % a −2,8 %.
- **No alcanza para dar vuelta el margen de la casa.** Seguir al favorito de
  la NBA a la cuota de cierre cuesta alrededor del 3-4 %, y la burbuja sola
  recupera menos de un punto.
- **En el fútbol el resultado positivo no lo pone la burbuja sola,** sino los
  skills y el análisis (el semáforo: 66,7 % contra 53,7 % que pedía la cuota).

**Tenis:** sin cuotas no se puede hacer esta cuenta. Si se paga una API para
el tenis, que traiga cuotas HISTÓRICAS, para hacer esta misma cuenta antes de
apostar.

### 9.2 ¿Mejor que el apostador de internet? Plana y martingala (12/11/2026)

El apostador de internet apuesta SIEMPRE al favorito. «El nuestro» es el
favorito sin la alerta DESCONFIAR. Cada uno con plana (1 u) y con la
martingala del repo, por líneas (`simulacion.py`: cada línea arranca en 1, se
duplica tras perder y vuelve a 1 al ganar; los partidos del mismo día toman
líneas distintas; quiebra = la apuesta del día no cabe en la banca). La banca
arranca en 100. Se mide la secuencia real y 2.000 remuestreos por días.

| 2023-24 → hoy | acierto | plana: banca final | martingala: P(quiebra) |
|---|---|---|---|
| favorito siempre | 69,1 % | −47,9 (−3,6 % por apuesta) | **99 %** |
| **nuestro** | **70,4 %** | **−2,0** (−2,8 %) | **93 %** |

En 2016-17 → 2022-23 la diferencia es más chica: con plana, −261 contra
−223. Con la martingala, quiebra en el 100 % de los remuestreos para los dos.

- **El nuestro es mejor que el de internet:** acierta más y pierde menos, en
  los dos períodos. Pero en la NBA ninguno de los dos gana.
- **La martingala con favoritos está rota por la cuota, no por el
  análisis.** A cuota 1,35, ganar la apuesta duplicada devuelve solo el 35 %
  de lo que se juega: perder 1 y después ganar 2 deja −0,3. La martingala
  necesita cuotas cerca de 2 para recuperar con una sola victoria. Con
  favoritos de 1,2-1,4 cada derrota se arrastra, y con varias líneas por noche
  la banca no aguanta.
- **En el fútbol la martingala salió 255 en la secuencia real**
  (`docs/METODO_APUESTA.md`) porque el elegido paga más (cerca de 1,8) y el
  win rate supera a la cuota. Pero sin esa ventaja quiebra en el 68 % de los
  remuestreos. Es lo mismo que se ve acá.

## 10. La K de PUNTOS, con dos varas (12/11/2026)

Pedido del usuario: medir la K de goles (en el básquet, de puntos) y
combinarla con la dirección. En el básquet todos anotan siempre, así que el
usuario pidió que la K se REINICIE contra una vara, y eligió dos (la 1 y la 3
de la discusión):

- **«propia»** (`anota` / `recibe`): anotar o recibir por encima de su media
  de los 20 partidos anteriores.
- **«casa»** (`anotaCasa` / `recibeCasa`): anotar o recibir por encima de lo
  que la casa esperaba de ese equipo en ese partido. Local = (total −
  hándicap del local)/2.

La K acumula el exceso (÷ 10) por el nivel del rival y revienta a 0 la
primera vez que queda por debajo. Está en `motor.FAMILIAS_PUNTOS` /
`FAMILIAS_CASA` y en `backend/nba/puntos.py`. Revienta bien: unos 6.800
reventones por familia, la mitad dura un partido, racha mediana 2, máximo
18. La línea de más/menos se agregó a la descarga, que se rehízo para las
14.336 cuotas.

Dos períodos que tienen que coincidir (2016-17 → 2022-23 y 2023-24 → hoy):

1. **¿La burbuja de puntos sigue?** Apenas. Con la vara propia, el siguiente
   partido queda arriba de su media entre 50 y 55 % de las veces, contra 49-50
   % de todos. Con la vara de la casa, nada (46-54 %, sin dirección): la casa
   ya corrige su línea.
2. **Hándicap del elegido** (favorito sin DESCONFIAR) según el cruce de
   burbujas de puntos: **nada estable.** Cubre 50-51 % contra 52,4 % que pide
   −110, y los cortes se contradicen entre períodos. Por ejemplo, «propia +2»
   da 54,4 % en el viejo y 45,4 % en el nuevo.
3. **Más/menos según la presión** (cuántas de las 4 burbujas de puntos están
   abiertas, de los dos equipos): **la única señal que se repite.**

| presión 4 · MÁS | 2016-17 → 2022-23 | 2023-24 → hoy |
|---|---|---|
| vara de la casa | 54,6 % vs pide 52,4 % · ROI +4,3 % (838) | 54,5 % vs 52,3 % · ROI +4,2 % (391) |
| vara propia | 53,7 % · +2,5 % (780) | 52,8 % · +0,8 % (326) |

La señal: cuando los dos equipos vienen anotando Y recibiendo por encima de lo
que la casa esperaba, el partido tiende a pasarse del total.

**Cautela:** salió de mirar unos 40 cortes a la vez. Juntando los dos
períodos (1.229 partidos, 54,6 % contra 52,4 %) el intervalo todavía roza lo
que pide la cuota (z ≈ 1,5). Lo que corresponde, como con el semáforo
(`docs/METODO_APUESTA.md`), es **fijar la regla hoy y medirla hacia
adelante** con escalones. Queda propuesto, sin decidir.

### 10.1 ¿Elegir nosotros el margen? El hándicap con las burbujas combinadas (13/11/2026)

Pregunta del usuario: combinando la K de puntos con las burbujas de victorias
y derrotas, ¿se puede decidir un margen de puntos y apostar a ese hándicap?
Se mide x = margen del elegido (favorito sin DESCONFIAR) + su línea, es decir,
cuánto le sobró o le faltó para cubrir. Se compara P(x > t) con lo que da una
normal(0, 14) centrada en la línea, que es como se precian las líneas
alternativas (ESPN no las trae).

- **En todos los grupos la media de x queda cerca de 0** (−1,3 a +1,3) y
  **cambia de signo entre períodos**: victorias o derrotas por cada riesgo, el
  balance de puntos de la casa −2 a +2, y las combinaciones. La línea de la
  casa ya es el centro: con las burbujas no aparece un margen que la casa no
  haya puesto.
- **Un margen más «seguro»** (que el favorito no pierda por más de 6) se
  cumple en el 67-72 % de los casos, que es justo lo que pide su precio.
  Sube el win rate, no la plata.
- **Lo único que se repite es un FRENO:** con la burbuja de victorias en riesgo
  **muy alto**, el favorito cubre el 47 % en los dos períodos (media −1,3
  puntos; n 294 y 154). Es la misma idea de la alerta DESCONFIAR, pero para
  el hándicap.

**Lectura:** el hándicap no es donde la burbuja paga. Combinando todo, el
camino queda así:
- **ganador:** el favorito sin DESCONFIAR (§9.1);
- **hándicap:** solo frena, no con victorias en riesgo muy alto;
- **puntos:** MÁS con presión 4 en la vara de la casa (§10), a medir hacia
  adelante.

Para medir de verdad líneas alternativas harían falta sus cuotas reales (una
API paga).
