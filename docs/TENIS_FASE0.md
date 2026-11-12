# Tenis · fase 0 · ¿el momentum aguanta en el tenis?

> Pedido del usuario (12/11/2026): después de la NBA, el tenis. Con la vara
> del sistema (`docs/METODO_APUESTA.md`): **win rate y dónde poner la plata,
> SIN cuotas**. Solo mide; no hay ingesta diaria, ni pantalla, ni skill.

## 1. Qué se corre

```bash
python -m backend.tenis.descarga     # ESPN, sin clave → ./tenis_data (fuera de git)
python -m backend.tenis.fase0        # → tenis_data/fase0.txt y .json
python -m backend.test_tenis_fase0   # sin red, en CI
```

- **Fuente.** ESPN (`sports/tennis/{atp,wta}/scoreboard`). Un pedido trae el
  torneo en juego con TODO su cuadro de singles, principal y qualy, así que
  basta con un pedido cada 3 días: 2.646 pedidos para 2016 a hoy.
- **Lo que no se alcanza desde el contenedor:** los datasets de Sackmann y
  tennis-data.co.uk. ESPN no trae Challengers ni ITF.
- **Lo que queda afuera:** los walkover (no se jugó) y los retiros (el partido
  no terminó). Si el ganador hizo menos juegos que el perdedor, se le pone uno
  más, para que el margen tenga el signo del resultado.
- **Volumen:** 76.067 partidos de singles, ATP y WTA. Desde 2022 ESPN trae
  casi el doble por año, porque suma torneos chicos.

## 2. La teoría en el tenis (`backend/tenis/fase0.py`, sobre `backend/nba/motor.py`)

- **El motor es por jugador.** Nivel = 3·victorias/20 + G + 1, con
  G = ESCALA_G × Σ(juegos ganados − perdidos)/Σ juegos de los últimos 5.
  q = (margen de juegos ÷ 5) × nivel del rival. ESCALA_G = **2**, elegida con
  el acierto del nivel de 2017 a 2020 (62,2 %, contra 61,9 % con 5 y 61,0 %
  con 10). Se mide desde 2021.
- **Sin localía:** todo partido es neutral, así que no hay factor de visita,
  ni familias de condición, ni contramano. El lado «local» se sortea por el id.
- **La K va separada como la de goles:** burbuja de victorias y de derrotas,
  con el riesgo, el extremo y el cerca-del-extremo del fútbol
  (`backend/nba/burbujas.py`).
- **Las rachas cruzan torneos.** Casi todos pierden una vez por semana, pero
  la K no se reinicia al cambiar de torneo.

## 3. Resultados (12/11/2026)

Los cuatro tramos del básquet (`docs/NBA_FASE0.md` §7), con «arriba» y
«abajo» como tercio de nivel del circuito al ARRANCAR cada año (jugadores con
10 o más partidos en el año). El porcentaje es la parte de los casos en que se
cumplió la lectura, de 2021 a hoy:

| escalón | A arriba, victorias, riesgo bajo: sigue | B arriba, derrotas, muy alto: se corta | C abajo, derrotas, riesgo bajo: sigue | D abajo, victorias, muy alto: se corta |
|---|---|---|---|---|
| **ATP total** | 77 % (1.709) ✓ | 71 % (618) ✓ | 70 % (857) | 77 % (573) ✓ |
| ATP Grand Slam | **87 %** (471) ✓ | 84 % (122) | **88 %** (188) ✓ | 84 % (121) |
| ATP cuadro principal | 75 % ✓ | 69 % | 68 % | 76 % ✓ |
| ATP qualy | 60 % | 66 % | 58 % | 69 % |
| **WTA total** | 73 % (2.062) ✓ | 74 % (878) ✓ | 71 % (1.098) ✓ | 70 % (827) ✓ |
| WTA Grand Slam | **82 %** ✓ | 77 % | **82 %** ✓ | 78 % ✓ |
| WTA cuadro principal | 71 % | 72 % | 70 % | 69 % |
| WTA qualy | 69 % ✓ | 76 % ✓ | 68 % | 69 % |

✓ = firme: en TODOS sus años con 30 o más casos acertó 65 % o más.

**El de más nivel gana:** ATP 61 % (Grand Slam 68 %, qualy 57 %) y WTA 60 %
(Grand Slam 64 %).

### Lectura

- **El momentum aguanta en el tenis, y mejor que en la NBA.** Los cuatro
  tramos quedan entre 70 y 77 % en los dos circuitos, año tras año.
- **El Grand Slam es donde más se cumple** (82-88 %). Es el escalón más alto y
  el más estable: al mejor de 5 sets en el ATP, y con los mejores siempre
  presentes.
- **La qualy del ATP es el límite** (58-69 %, ningún tramo firme). Es lo mismo
  que la G League en el básquet y la liga B en el fútbol: jugadores que suben y
  bajan de nivel. La qualy de la WTA aguanta mejor.

### Lo que todavía no está bien: la foto de «hoy»

- **El nivel del motor mide FORMA, no la calidad del rival,** y en el tenis
  todos van al mismo pozo. Quien gana mucho en torneos chicos sube igual.
  Desde 2022 ESPN mete en el «cuadro principal» torneos chicos (los WTA 125,
  por ejemplo) y no dice la categoría.
- **El top 20 por nivel no es la élite.** Ya se filtra a los activos en 60 días
  con 10 o más partidos de cuadro en el año, y aun así salen Clara Burel,
  Polona Hercog o Francesca Jones entre las primeras de la WTA.
- **Los tramos del §3 siguen valiendo,** porque miden cuántas veces se cumple
  la lectura en cada tercio. La lista de «los mejores de hoy» no vale, hasta
  que el nivel distinga la categoría del torneo o pese al rival en la P. Eso
  es una decisión de teoría, así que queda para el usuario.

## 4. ¿Con qué nivel? Las variantes, lado a lado (12/11/2026)

`python -m backend.tenis.nivel` (→ `tenis_data/nivel.txt`). Las variantes
están en el motor, apagadas por defecto: `nivel_por_rival` y `cuenta_nivel`
de `motor.construir`. La NBA no cambia. ESCALA_G = 2 en todas, para comparar
solo la P.

| variante | el de más nivel gana: 2017-20 | ATP 21+ | WTA 21+ | tramos ATP A·B·C·D | tramos WTA A·B·C·D |
|---|---|---|---|---|---|
| actual | 62,2 % | 61,1 % | 60,1 % | 77✓ 71✓ 70 77✓ | 73✓ 74✓ 71✓ 70✓ |
| rival (P pesada por el rival) | 62,2 % | 61,1 % | 60,3 % | 78✓ 72 71 74✓ | 74✓ 75✓ 71✓ 71✓ |
| **pozos** (nivel solo con cuadro principal) | 62,2 % | **62,7 %** | 60,3 % | **78✓ 73✓ 74✓ 80✓** | 75✓ 70 70✓ 72✓ |
| rival + pozos | 62,2 % | 62,4 % | 60,6 % | 80✓ 71 74✓ 78✓ | 75✓ 71 70 72✓ |
| **Elo (vara de afuera)** | **63,8 %** | **64,2 %** | **64,4 %** | — | — |

**Top 10 de hoy:**
- **Elo:** Alcaraz, Zverev, Djokovic, Fils, Shelton, Fritz, Medvedev… y en la
  WTA Rybakina, Sabalenka, Gauff, Pegula, Swiatek, Andreeva…
- **Las cuatro variantes SAD** siguen con Burel, Andreescu, F. Jones o C. Liu
  arriba en la WTA, y sin Sabalenka ni Gauff.

### Lectura

- **«Rival» casi no cambia nada.** Pesar la victoria por el nivel del rival no
  alcanza, porque el nivel del rival también es de forma. Un pozo de
  jugadoras que se ganan entre sí en torneos chicos se infla igual. Es la
  circularidad que se esperaba.
- **«Pozos» es la mejor para el MOMENTUM:** los 4 tramos firmes en el ATP
  (74-80 %) y +1,6 puntos de acierto en el ATP. Pero no arregla la foto,
  porque los WTA 125 están dentro del «cuadro principal» de ESPN.
- **El Elo es el mejor para saber QUIÉN ES MEJOR:** 2 a 4 puntos más de
  acierto y un top 10 que tiene sentido. Pero no es la teoría.

### Lo que sigue (decisión del usuario)

Un **doble nivel** (la alternativa 6 de la discusión):
- **El Elo dice quién es mejor:** arriba y abajo, la foto de hoy, el favorito.
- **El SAD con pozos dice el momentum:** las K, las burbujas, el riesgo y el
  extremo.

La prueba pendiente es ver si los tramos siguen firmes cuando «arriba y
abajo» salen del Elo.

## 5. El Elo COMO el nivel del SAD (12/11/2026, corrección del usuario)

El usuario corrigió la propuesta de la doble capa del §4: el Elo no va
«al lado» del SAD, **va como el nivel del SAD**. Es el número que entra en
la q (el peso del rival en la K), en el riesgo (rival en zona o fuerte,
favorito) y en los tercios. Las burbujas, el extremo y el récord del período
quedan iguales, montados sobre un nivel que sabe quién es mejor.

- **Escala:** el Elo se pasa a la escala del nivel SAD con la misma media y el
  mismo desvío, medidos SOLO en 2017-2020, para que los umbrales del fútbol
  (zona ±0,15, fuerte 0,45, favorito 0,5 / 1,0) signifiquen lo mismo. Queda
  nivel = 2,62 + (Elo − 1.678) / 240: **1 punto de nivel = 240 de Elo**.
- **El Elo** es el de FiveThirtyEight para tenis: k = 250/(n+5)^0,4, sobre
  todos los partidos, con nivel recién a partir de 20 partidos, como el SAD.
- **En el motor:** `motor.construir(nivel_externo=…, nivel_final=…)`;
  `backend/tenis/nivel.py` (`elo_como_nivel`).

| | el de más nivel gana: ATP 21+ | WTA 21+ | tramos ATP A·B·C·D | tramos WTA A·B·C·D |
|---|---|---|---|---|
| SAD con su nivel (actual) | 61,1 % | 60,1 % | 77✓ 71✓ 70 77✓ | 73✓ 74✓ 71✓ 70✓ |
| **SAD sobre Elo** | **64,2 %** | **64,4 %** | **81✓ 79✓ 74 73✓** | **79✓ 81✓ 74✓ 77✓** |

**Por escalón, con el SAD sobre Elo:**
- **Grand Slam:** 83-87 %.
- **Cuadro principal:** ATP 71-79 %; WTA 73-81 %, los 4 firmes.
- **Qualy WTA:** 73-80 %, firme. Antes era el límite.
- **Qualy ATP:** 62-74 %, sigue siendo el límite.

**La foto de hoy por fin es la élite:**
- **ATP:** Alcaraz (9 victorias seguidas), Zverev, Djokovic, Fils, Shelton,
  Fritz…
- **WTA:** Rybakina, Sabalenka, Gauff, Pegula, Swiatek…
- **Alertas que aparecen:** Muchova y Bencic en 🟠🟡 con derrotas (cerca de
  su peor racha y récord del período), Kostyuk 🟠 con 5 derrotas y
  Chwalinska 🟠 con 6 victorias.

**Lectura:** el problema nunca fue la burbuja, era el nivel. Con un nivel que
mide la calidad del rival, el mismo momentum del SAD acierta más en los dos
circuitos y en casi todos los escalones. **Para el tenis, el nivel recomendado
es el SAD sobre Elo.** Falta que la fase 0 lo use por defecto, y eso queda a
decisión del usuario.
