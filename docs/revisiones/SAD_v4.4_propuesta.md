# Propuesta de revisión · `sad-analysis` v4.3 → v4.4

**Estado:** PROPUESTA, pendiente de aprobación del usuario. No se tocó el
skill (`docs/skills/sad-analysis/SKILL.md` sigue en v4.3) ni la app.
Escrita el 01/11/2026 desde las **139 lecciones pendientes** del skill
(`GET /analisis/cowork/lecciones` y el dossier
`GET /analisis/cowork/revision/sad-analysis`, leídos el 01/11 a las 05:08
UTC) y desde lo medido en `acreditables` (cohorte `c3-2026-09-23`, **370
partes ciegos**, 740 lados).

## De dónde sale

- **139 lecciones pendientes**, todas `ciega` + `PRE`:
  - **115 acreditables** (partidos de liga y torneos internacionales).
  - **24 de copa nacional** (Copa del Rey, 29/10): población `copa`, fijan
    rúbrica y no entran a ninguna métrica. 8 de ellas están además en
    cuarentena automática por DT equivocado, de la que **enseña**.
  - **81 son de partes anteriores al corte de la v4.3** (28-29/10, escritos
    con la v4.2). La v4.3 fue de un solo punto y las dejó para esta revisión.
    Las otras 58 son de partes escritos con la v4.3 (30-31/10).
  - Fuera de esta cuenta: las del Huracán–Tigre y el San Antonio–Real Potosí,
    en cuarentena que **no** enseña (parte sin DT): no cuentan ni fijan
    rúbrica.
- **Veredicto por lado:** 76 aciertos, 23 parciales y 40 fallos.
- **Jev no marcó ninguna** como «pide mover un número» (`pidenMoverSinPoder`
  vacío). Los modos de fallo etiquetados: reventón 7, lectura del EFE 4,
  mercado 3, sin etiqueta 11. **Esta revisión fija rúbrica y no mueve un
  número de la app.** Las lecciones son ciegas y PRE, así que podrían
  sostener un cambio de peso, pero ninguna lo pide con n suficiente. Donde una
  regla nueva de lectura necesitaría un umbral, se marca con ⚠️ y se pide
  medirla primero.
- **Lo calculable se marca «calculable»**: la app lo puede calcular o avisar
  con un dato que ya tiene. La v4.4 no le hace calcular eso a la corrida.

### Lo medido que manda esta revisión

**1X2 por tramo de confianza** (elegido del parte; «dijimos» y «mercado» son
lo que cada uno le daba al elegido):

| Tramo | n | Acierto (IC 95 %) | Dijimos | Mercado |
|---|---|---|---|---|
| < 40 | 73 | 45 % | 37,4 | 37,7 |
| 40-49 | 132 | 45 % | 44,1 | 45,2 |
| 50-59 | 99 | **62 %** (52-71) | 54,4 | 57,4 |
| 60+ | 63 | **78 %** (66-86) | 68,1 | 70,8 |

**El mismo cuadro, separado por versión del skill:**

| Tramo | v4.0 y anterior: acierto · dijimos · mercado | v4.1 a v4.3: acierto · dijimos · mercado |
|---|---|---|
| < 40 | 42 % (19/45) · 37,5 · 39,6 | 50 % (14/28) · 37,2 · 34,7 |
| 40-49 | 39 % (31/80) · 44,0 · 46,0 | 56 % (29/52) · 44,2 · 44,0 |
| 50-59 | 58 % (26/45) · 54,1 · **60,0** | 65 % (35/54) · 54,7 · 55,2 |
| 60+ | 89 % (16/18) · 66,0 · **74,4** | 73 % (33/45) · 68,9 · 69,4 |

**Por versión:**

| Versión | Acierto del 1X2 |
|---|---|
| v4.1 | 44/68 (65 %) |
| v4.2 | 18/29 (62 %) |
| v4.3 | 49/82 (60 %) |

Con la v4.3 sola, el tramo 60+ acierta 15 de 22 (68 %) cuando dijimos 69,2, y
el 50-59 acierta 11 de 20 (55 %) cuando dijimos 54,5.

**Espina** (`acreditables.espina`):

| Lectura | Lados | Acierto (IC 95 %) | Frecuencia del movimiento |
|---|---|---|---|
| `positiva` | 337 | 57 % (52-62) | 40 % |
| `negativa` | 324 | 57 % (52-63) | 40 % |
| `cero` | 62 | **19 %** (11-31) | 20 % |
| `neutra` | 17 | **0 %** (0-18) | — |

- **Tarjeta:** fuerte 58 % (120/207), débil 40 % (167/421).
- **Dos tarjetas débiles que concuerdan:** 39 % (30/77), contra 44 % de una
  tarjeta sola.
- **Contra la tarjeta:** el analista acierta 84 y la tarjeta 33, sobre 164.

**Goles acotados** (`acreditables.golesAcotados`):

| Medida | Acierto | IC 95 % | Lo que promete el backtest |
|---|---|---|---|
| Intervalo de dos goles | 457/740 (61,8 %) | 58-65 | 64 % |
| Marcador acotado | 134/370 (36,2 %) | 31,5-41,2 | 40,3 % |

Los dos están dentro de lo que promete el modelo.

## Lo que la v4.3 y la v4.2 acertaron y no hay que tocar

- **El favorito no se recorta sin dato (6-B, v4.1).** Napoli, Inter,
  Galatasaray, Cienciano, Sporting CP, Bragantino y Once Caldas siguieron al
  mercado contra un motor 20-30 puntos más abajo, y acertaron.
- **La tarjeta débil de la condición no se sigue por defecto (1.6, v4.2).**
  Moreirense–Estrela (1575535) la confirma.
- **FAMILIA-RECORD se sostiene (1.7 d).** Inter llegó a 30 partidos anotando,
  Colo Colo a 13 de local, Brugge a 37. También se sostuvieron el Monza con más
  de 2,5 y el Alianza Atlético.
- **El marcador dentro del acotado (3.5, v4.3).** Exacto en Bournemouth–Leeds
  2-0, Casa Pia–Sporting 0-2 y Guaraní–2 de Mayo 1-0.
- **El falsador sobre la vía (6-C, v4.2)** sonó en el lado correcto en
  Genoa–Juventus, Metropolitanos y Los Chankas, y separó el acierto del número
  del acierto de la lectura en Fluminense–Internacional.

**Nada de lo que sigue afloja esas reglas.**

---

## Los nueve puntos

### 1. La calibración del favorito: el número es el del mercado, y se cierran las vías por las que todavía baja

**Qué dice hoy (6-B, v4.1):**

- El favorito de 50 %+ no se recorta bajo el mercado sin un dato que el
  mercado no tenga, escrito con su cifra.
- La tabla de la cohorte se lee, no se aplica como fórmula.

**Lo medido:**

- **La subconfianza que se ve en el cuadro global es sobre todo de antes de
  la v4.1.** En la v4.0 y antes decíamos 54 al 50-59 con el mercado en 60, y 66
  al 60+ con el mercado en 74: recortábamos. Desde la v4.1 la distancia con el
  mercado es de medio punto (54,7 contra 55,2; 68,9 contra 69,4).
- **Lo que queda la comparte el mercado.** En v4.1-v4.3 el elegido acertó
  **111 de 179 (62 %, IC 55-69)** cuando el mercado le daba en promedio
  **~52 %**, y pasa en TODOS los tramos, también debajo del 50 (< 40: 50 %
  contra 37). No es un sesgo nuestro con el favorito: es una semana (25-31/10)
  en la que el elegido ganó más de lo que pagaba cualquiera.
- **La v4.3 sola está calibrada** en el tramo alto: 15 de 22 al 69 % (68 %).
  La lectura previa de «41 de 50 al 82 %» juntaba la v4.0 a la v4.3 cuando la
  v4.3 tenía menos casos.
- **No hay valor que cobrar:** apostar siempre a nuestro elegido a la cuota
  media (`valorMercado.nuestroFavorito`, n 466) da +4,2 % con el intervalo de
  −5,5 % a +14 %: cruza cero. Si el mercado infravalorara de verdad al
  favorito, ese intervalo estaría arriba.
- **Inflar con un factor ya se probó:** «+N al favorito» o la temperatura
  empeoraron el Brier fuera de la muestra (validación por fecha, v4.1).

**Las lecciones (13):** cuándo el favorito sigue bajando todavía.

- **El motor por debajo del mercado no es un dato.** En 12 partes el mercado
  daba al favorito 50 % o más y el motor menos. Siguiendo al mercado, **ganaron
  8**:
  - Bragantino (1492432), Once Caldas (1549731), ADT (1549527), Napoli
    (1550172), Inter (1550176), Cienciano (1549529), Galatasaray (1584455) y
    Sporting CP (1575531).
  - En el motor pesaban la altura y la localía sudamericana (que μ no ve), la
    forma mezclada con la Champions y la ESCALA-LIGAS.
  - De los cuatro que no ganaron, **solo en Genoa–Juventus (1550171) el motor
    estaba más cerca**. América (1550952) y Bayern (1575203) empataron con
    28 y 25 remates, por conversión. Melgar (1549530) tuvo una roja al 4'.
- **Una muestra chica de la condición tampoco es un dato.** Elversberg–Mainz
  (1575211:b:6): +7,5 al favorito sobre el motor por «3 de 3 de visita», y no
  ganó.
- **La rotación ya publicada está en la cuota.** América (1550952) y Alianza
  Atlético (1549528) la confirman.

**Propuesta (6-B y Auditoría 2, pregunta 6):**

1. **La lista de lo que NO es un dato para bajar al favorito del mercado** se
   escribe entera:
   - el motor más bajo, con o sin DIV-MOTOR-MERCADO, ESCALA-LIGAS o una
     ventana con amistosos;
   - una frecuencia de la condición con menos de 10 partidos;
   - la rotación o las bajas ya publicadas antes de la última captura;
   - el riesgo del reventón y la espina (ya escritos en la v4.1).

   Esta lista es la misma que en 6-A dice qué no saca el número del mercado.
2. **Tampoco se sube sobre el mercado** por la tabla de la cohorte. La
   subconfianza que queda la comparte el mercado y el valor no la confirma. La
   regla escrita es «el número del favorito es el del mercado salvo un dato
   escrito con su cifra», hacia arriba y hacia abajo.
3. **Cuándo se reabre (calculable):** si con la v4.3 o posterior un tramo
   llega a n ≥ 30 con el intervalo entero **por encima de lo que dijimos y de
   lo que daba el mercado**, y `valorMercado.nuestroFavorito` sale con el
   intervalo sobre cero (n ≥ 50), la revisión siguiente propone «el favorito
   sobre el mercado» con la validación por fecha de la v4.1. Antes, no.

**Qué NO:** ningún «+N» al favorito, ninguna temperatura ni factor. No se
toca el motor ni `unXDos`.

### 2. El delta sin noticia no da vuelta al elegido ni se suma al mercado

**Qué dice hoy (6-A, v4.2):** el 1X2 no se aparta del mercado **en contra**
del delta (apertura → cierre) sin un dato propio.

**Lo medido (9 lecciones).** La regla de la v4.2 se aplicó al revés: se
siguió el delta **más allá** del mercado, o se lo usó para dar vuelta al
elegido.

- **Seguir el delta sin noticia falló:**
  - **Los Chankas–Cusco (1549533):** +4 al local en la mañana, sin causa
    publicada, más los perfiles DC, llevaron el 1X2 3,5 puntos sobre el
    mercado al local. Ganó la visita 0-1.
  - **Lille–Lens (1552802):** la cuota se corrió a la visita sin una razón
    encontrada (2.32 → 2.73). El pick se dio vuelta contra el motor (local
    41 %) y contra las dos espinas del propio parte, que iban al local. Ganó
    Lille.
  - **Coventry–Sunderland (1557451):** el delta corrido a Sunderland, con el
    motor dando al local 41 %. Ganó el local 3-1.
  - **Parma–Udinese (1550173):** separarse hacia el motor «por el delta de
    apertura» no tuvo sostén en cancha.
- **El motor, más cerca cuando el partido era parejo** (el mercado daba al
  favorito menos de 50 %):
  - Sporting Cristal–Alianza (1549534): el delta de la víspera, sin noticia;
    el motor dio 50 %.
  - Cambuur–Go Ahead (1552211): el motor dio 46 % contra 34 % del mercado, y
    ganó el local 4-0.
  - Los mismos Lille y Coventry.
- **Seguir el delta salió bien en tres casos:** Carabobo (1646922, el delta
  con el motor de acuerdo), Cienciano (con el mercado ya ≥ 50 %) y Moreirense
  (1575535, un caso).

**Propuesta (6-A):**

1. **El delta ya está en la última captura.** El mercado que se publica es el
   de cierre: sumarle el delta otra vez es contarlo dos veces. El delta sirve
   para lo que dice la v4.2 (no ir en su contra) y **no para apartarse del
   mercado en su dirección**.
2. **Un delta sin noticia identificada no da vuelta al elegido.** Cuando el
   delta cambia quién es el favorito del mercado y no hay una noticia que lo
   explique, el elegido no se decide por el delta: se publican el motor y el
   mercado con sus números (disciplina 33) y se dice «delta sin causa».
3. **Partido parejo con motor y mercado en lados distintos:** si el mercado da
   al favorito menos de 50 % y el motor elige el otro lado, se escriben los dos
   elegidos y el pick dice cuál sigue y por qué. Eso no habilita a seguir al
   motor por defecto: son 3-4 casos.
4. **Calculable:** la app ya trae `pronosticoVsMotor` y el historial de
   cuotas. Puede marcar «el elegido del motor y el del mercado difieren» y
   medir en Aprendizaje cuál acierta cuando difieren. Esa serie decide el
   punto 3 en la próxima revisión.

### 3. La espina: sale `neutra`, `cero` pide un hecho de la lista y sin lectura propia se sigue al 1X2

**Qué dice hoy (1.6):**

- Hay cuatro lecturas.
- `cero` necesita un hecho de ESTE partido. La lista admite «dos burbujas
  negativas enfrentadas» y «un rival que empata la mitad de sus partidos».
- `neutra` es honesta pero no puntúa.

**Lo medido:**

- **`neutra` acertó 0 de 17** (IC 0-18). No puede acertar nunca: la K
  siempre se mueve (crece, vuelve a cero o pasa al otro signo). Medida como
  lectura, es un fallo seguro.
- **`cero` acierta el 19 %** (12/62), lo mismo que la frecuencia del empate
  (20 %). Leer `cero` no agrega nada sobre tirar la frecuencia.
- **`positiva` y `negativa` aciertan el 57 %**, 17 puntos sobre su frecuencia.
  Es donde está la información.

**Las lecciones (31), por causa:**

- **«Cero o neutra» como refugio de la duda** (10). Varias lecciones lo piden
  después del resultado: Parma 1550173:a:6, Comerciantes 1549530:b:6,
  Feyenoord 1552207, Portuguesa 1646923:b:5, Oriente 1645527, Metropolitanos
  1646923:a:3, Chicó y Junior 1549726.

  Pero leer `cero` acierta lo que la frecuencia. Lo que esas lecciones piden
  de verdad es no cargar la lectura **contra** el empate, y eso es coherencia
  con el marcador: Chicó y Junior declararon 1-1 como marcador y leyeron la
  espina positiva y negativa.
- **Las burbujas negativas enfrentadas no son un hecho** (2). Remo–Botafogo
  (1492437):
  - la espina `cero` por «dos burbujas negativas enfrentadas» falló;
  - el empate subido 3 puntos por lo mismo dejó al 1X2 35/35, sin elegido, y
    el motor tenía al local arriba.

  El backtest de las lecciones (REVENTON §12) ya decía que las burbujas
  enfrentadas no puntúan.
- **Contradicción interna del skill.** La regla (a) cuenta «un rival que
  empata la mitad de sus partidos» como hecho para `cero`. La (c) de la v4.2
  dice que la frecuencia propia de empates **no** es un hecho (Portuguesa).
- **Dos tarjetas débiles que concuerdan no suman** (3):
  - Atlético-MG–Cruzeiro (1492430) y América–Tijuana (1550952:b:5): las dos
    tarjetas iban al local y las dos fallaron.
  - Coventry–Sunderland (1557451:b): concordaban y acertaron, y contradecirlas
    con el descanso falló.

  Medido: 39 % las débiles que concuerdan, contra 44 % de una sola. Ni
  refuerzan ni se contradicen sin un hecho.
- **Sin tarjeta, un cambio de banco no es un hecho en ninguna dirección**
  (Espanyol 1570442:b:4, con el interino como posible reacción). Tampoco lo es
  «el arranque de una burbuja» leído del motor y del once (Metropolitanos,
  Santos 1492438:a:6).
- **Contradecir la tarjeta débil con los skills acertó en la mayoría de los
  casos de esta tanda:** Carabobo, Galatasaray, Pachuca, Atlético Nacional,
  Guaraní, Llaneros, Nice, Alianza Atlético y Monza. Falló en Villarreal, Genk
  y Junior. Confirma el paso 3 del procedimiento (con tarjeta débil deciden
  los skills) y la medición global: el analista acierta 84 contra 33 de la
  tarjeta.

**Propuesta (1.6, glosario y 6-D):**

1. **Sale `neutra`.** Quedan tres lecturas: `positiva`, `cero` y `negativa`.
   La regla (f) se reemplaza.
2. **Sin lectura propia, la espina sigue al 1X2 declarado**, con una guía
   nueva: `guia: "pronostico"`. El elegido gana: `positiva` para él y
   `negativa` para el otro. Si el elegido es el empate, `cero` en los dos.
   - Es la lectura por defecto cuando no hay tarjeta fuerte que seguir, ni
     hecho para contradecirla, ni lectura de los skills con la tarjeta débil.
   - Medido: el elegido del 1X2 acierta el 55 % (203/367), contra el 40 % de
     la tarjeta débil y el 0 % de `neutra`.
   - **Calculable:** Aprendizaje la mide aparte en `porGuia`, para que no se
     mezcle con la lectura propia.
3. **El orden del procedimiento queda en cuatro pasos:**
   1. Tarjeta fuerte: se sigue, salvo un hecho.
   2. Hecho de ESTE partido: lectura propia, «contra la tarjeta porque…».
   3. Tarjeta débil: deciden los skills, que lo digan.
   4. Sin nada de eso: guía `pronostico`.
4. **`cero` se queda, con una lista cerrada de hechos:**
   - los dos perfiles DC apuntando al empate (calculable);
   - una eliminatoria o un partido único donde el empate a los 90 tiene premio
     para uno de los dos: penales, prórroga, la ida a favor (calculable con la
     ronda y la ida);
   - los dos lados con el empate como marcador declarado **y** un hecho del
     partido escrito.

   **Se sacan de la lista** «dos burbujas negativas enfrentadas» y «un rival
   que empata la mitad de sus partidos», en 1.6 (a) y en 6-B (empate).
   **La prudencia no es un hecho para `cero`:** el extremo se trata en el
   punto 4.
5. **La espina y el marcador declarado del mismo parte no se contradicen en
   silencio.** Es la regla que ya rige para el 1X2. **Calculable:** la app
   puede avisar «ESPINA-VS-MARCADOR» cuando un lado lee `positiva` y el
   marcador lo da perdiendo, o al revés.
6. **Dos tarjetas débiles que concuerdan** se escriben en 1.6 como lo que son:
   cada una al 40 %, sin sumar. Contradecirlas pide el mismo hecho que
   contradecir una.

### 4. La espina en el extremo y con la K de otra escala o de otro DT

**Qué dice hoy:**

- **1.7 (e):** K-EXTREMO y K-CERCA-EXTREMO son prudencia con la carga.
- **1.6 (e):** con T.54 o ESCALA-LIGAS «se lee la total **o se declara la
  reserva**».
- La alerta de la app ESPINA-SIGUE-EN-EXTREMO (desde el 26/10) **no está
  escrita en el skill**.

**Lo medido (16 lecciones):**

- **Decir «sigue» en el extremo acertó 6 veces, siempre con algo más que la
  racha:**
  - **Con un hecho nombrado (3):**
    - Atlético Grau (1549529:b:4): el llano a 3.400 m y la zaga nueva.
    - Sporting Cristal (1549534:a:7): Alianza sin Pavez ni Antoni.
    - Casa Pia (1575531:a:7): un rival 1,43 de nivel arriba.
  - **Siguiendo la tarjeta fuerte (3):**
    - PSG (1552801): un rival sin victorias y con el arquero de recambio.
    - Brugge (1558670:b:6).
    - Heerenveen (1552208).

    PSG y Brugge eran favoritos claros: **la diferencia de nivel a favor de la
    racha**, que la app calcula.
  - **Sin hecho, o con un perfil, falló o se cortó en empate:** UTC
    Cajamarca (1549531:b, «descendido sin objetivo» es perfil), Udinese
    (1550173:b, bajas sin comprobar en el once), Atalanta (1550169:b:7) y
    Rizespor (1584454:b:4, se cortó en 0-0).
- **Leer el corte en el extremo tampoco funcionó:** Medellín (1549728:b:6,
  `cero` y la racha siguió a cuatro) y Querétaro (1551021:b:4, siguió). El
  extremo no adelanta el corte (REVENTON §13.2: la K no puntúa).
- **La reserva escrita no reemplaza cambiar la guía.** FC Cajamarca
  (1549531:a:5) siguió la tarjeta fuerte de local armada con otro DT (T.54 de
  siete días), con la reserva en el `porque`, y perdió.
- **Con ESCALA o R-KT.2 la tarjeta débil no orienta:** Elversberg (1575211:a:6)
  falló siguiéndola; Monza (1550172:a:6) la contradijo por la escala y
  acertó.
- **Con la tarjeta fuerte de la condición y un hecho en la misma dirección se
  sigue** (Frosinone 1550170:a:7).

**Propuesta (1.6 y 1.7 e):**

1. **Se escribe la regla de ESPINA-SIGUE-EN-EXTREMO.** Con K-EXTREMO o
   K-CERCA-EXTREMO (de la total o de la condición), la espina dice «sigue»
   solo con un hecho de ESTE partido nombrado en el `porque`. Valen:
   - la diferencia de nivel a favor de la racha, que la app trae en el riesgo
     (`rival.aFavor` / `rival.favorito`; **calculable**);
   - una baja del rival confirmada en el once o por una fuente de nivel A.

   No valen el perfil del club, el objetivo en la tabla ni una baja sin
   confirmar.
2. **Sin ese hecho, en el extremo la espina no dice «sigue» y tampoco va a
   `cero` por prudencia.** Va con la tarjeta si la tarjeta lee el corte. Si la
   tarjeta también dice «sigue», va al corte más frecuente de la guía
   calibrada: al otro signo con riesgo alto o muy alto (37 % y 45 % contra 27 %
   a cero), salvo un hecho de la lista de `cero` del punto 3. ⚠️ Son 6 cortes
   en esta tanda y 3 salieron a cero: la serie se mide en Aprendizaje
   (**calculable**: espina en el extremo, por lectura) antes de afinar.
3. **1.6 (e) se endurece.** Con T.54 del lado (DT de menos de seis meses, la
   misma fecha que usa `T.54-SIN-DECLARAR`) o con ESCALA-LIGAS / R-KT.2, si la
   K de la condición se armó con otro DT o en otra categoría:
   - la guía es `total`;
   - la tarjeta débil de esa K no se cita como apoyo.

   Ya no basta la reserva en el `porque`. **Calculable:** la app conoce
   `dt.desde` y la escala, y puede avisar «GUIA-CONDICION-CON-T54/ESCALA».
4. **INFLADA** (extremo hecho con amistosos) pesa poco la racha, pero **no**
   es razón para ir contra la tarjeta ni contra el riesgo (Unionistas,
   1644371, en la copa). Se escribe en 1.7 (e).

### 5. Los dos perfiles DC alineados le quitan a la visita; no le suman todo al local

**Qué dice hoy (6-B, v4.2):**

- Los dos perfiles DC apuntando al mismo resultado (el local no pierde y el
  visitante no gana, cada uno en dos de cada tres partidos o más) son un
  hecho.
- «+N al empate y al local», nombrándolo.

**Lo medido.** Con los dos perfiles alineados, **el visitante no ganó en 11
de 13 partes** de esta tanda:

- Bragantino, Fluminense, Inter Bogotá, Grêmio, Pachuca, Atlético Nacional,
  Guaraní, Corinthians y Bournemouth ganaron.
- Metropolitanos–Portuguesa (1646923) y Real Oruro–Nacional Potosí (1645528)
  empataron.
- Perdieron el local Trinidense–Rubio Ñu (1632049, 2-4) y Los Chankas–Cusco
  (1549533, 0-1).

Pero las lecciones (6) muestran cómo se aplicó:

- **Todo al local:**
  - Metropolitanos: +4,7 al local solo por los perfiles, y empate 0-0.
  - Trinidense: +5 al local, y ganó la visita con un ataque cambiado en el
    once.
- **Repartido:**
  - Fluminense (1492435): +1 al local y −2 a la visita, y ganó.
  - Inter Bogotá (1549728:a:6): +4 al local, y ganó.
- **Real Oruro (1645528):** se siguió al mercado hacia la visita y el empate
  subió solo 1,6. Salió 1-1, lo que los dos perfiles decían juntos.

**Propuesta (6-B):**

1. **Lo que dicen los dos perfiles juntos es «el visitante no gana»**, no «el
   local gana». Los puntos se **restan a la visita** y se reparten entre el
   local y el empate, con el `porque` diciendo cuánto va a cada uno. No van
   todos al local.
2. **Los dos perfiles no son dos fuentes independientes** de la espina y del
   1X2 a la vez. Se nombran una vez, como el hecho del partido, no como dos
   apoyos.
3. ⚠️ **Sin número nuevo**: el umbral «dos de cada tres» y la cuantía de N no
   se tocan.
4. **Calculable:** la app tiene los perfiles DC por condición en `/burbujas`.
   Puede marcar «DC-ALINEADOS» con los dos porcentajes y medir en Aprendizaje
   la tasa de «el visitante no gana» cuando se dan. Esa medición es la que
   faltaba desde la v4.2.

### 6. El riesgo alto frena la carga: qué es «cargar»

**Qué dice hoy (1.7 a):**

- Con riesgo alto o muy alto, el 1X2 no carga a favor de la racha.
- Tampoco se da vuelta contra el favorito del mercado solo por el riesgo.

**Lo medido:**

- **`respetoRiesgo`, con riesgo alto o muy alto:**

  | El 1X2 apostó… | Lados | Acierto del 1X2 | Brier |
  |---|---|---|---|
  | a que la racha sigue | 169 | 49 % | 0,598 |
  | a que se corta | 244 | 53 % | 0,591 |

  La diferencia existe y es chica: el riesgo vale como freno, no como lado
  (REVENTON §13.3).
- **El reventón por nivel está dentro del backtest** en los cuatro niveles
  (alto 63 %, muy alto 68 %). No se abre la revisión de los puntos.

**Las lecciones (11):**

- **Se siguió la racha con riesgo alto y reventó** (6):
  - Villarreal (1570442:a:7) con el 67 %.
  - Genk (1558666:b:4), al 49 % del mercado.
  - Real Potosí (1645526:a:4) con el 63 % y la K de local en muy alto.
  - Palmeiras (1492438:b), con la espina contra la tarjeta.
  - Coventry–Sunderland y Kocaelispor–Rizespor (1557451:b:2, 1584454:b:5): las
    dos burbujas en riesgo alto y el 1X2 a que seguían las dos.
- **Se respetó el riesgo y se cumplió** (4): Santa Fe, Jaguares, Lecce y
  Alianza Lima.
- **Con ESCALA-LIGAS el riesgo no anticipó el corte** (1): Mainz (1575211:b:5)
  siguió. Confirma 1.7 (c).

**Propuesta (1.7 a):**

1. **«Cargar» se define:** es poner al lado de la racha **por encima del
   mercado**. Quedarse en el número del mercado no es cargar, por el punto 1
   y la v4.1. Con riesgo alto o muy alto:
   - el número del lado de la racha no sube sobre el mercado;
   - el `porque` del 1X2 nombra el riesgo.

   Así las dos reglas (seguir al mercado y frenar la carga) dejan de chocar:
   Villarreal y Genk estaban en el mercado y ahí se quedan, con el riesgo
   escrito.
2. **Calculable:** `pronosticoVsRacha` se calcula hoy en el veredicto. Al
   depositar, la app puede avisar «1X2-CARGA-CONTRA-RIESGO» cuando el elegido
   es el lado de la racha con riesgo alto o muy alto **y** queda sobre el
   mercado. Es un cálculo de la app, no un número del skill.

**Qué NO:** «riesgo alto en las dos burbujas → más empate» sigue de
candidato. Rizespor salió 0-0, Coventry 3-1, y en Remo–Botafogo no hubo
empate: n chico y dividido.

### 7. El marcador: la goleada como rama nombrada, el gol del débil desde el volumen

**Qué dice hoy (3.5, v4.2-v4.3):**

- El marcador declarado va dentro del acotado, y sale de ahí solo con un
  hecho.
- El marcador lee el volumen de los dos lados.

**Lo medido:**

- El intervalo y el marcador acotado están dentro de lo prometido (61,8 % y
  36,2 %).
- **El acotado no cubre la cola de la goleada del favorito:**
  - PSG 1-5 (1552801:b:6), con 26 % de 3+ en la distribución.
  - Colo Colo 6-1 (1505548).
  - Macará 3-0 (1639801).
  - Anderlecht 4-0 (1558662).
  - Rennes 5-2 (1552806:b:7, con tres penales: varianza).
  - Junior 3-2 (1549850:b:5, con dos penales).

**Las lecciones (20):**

- **La goleada estaba escrita en otro lado del parte**: el TDE con el que
  persigue en `se_rompe` (ISE de rama ≥ 7) en Colo Colo, la matriz con la
  goleada tras el gol temprano en Colo Colo, y el rival que concede 2,3 por
  partido en Anderlecht.
- **El gol del débil, de cortesía o negado sin volumen:**
  - **De cortesía, sin volumen que lo sostenga:** Cienciano (1549529:a:5,
    Grau sin remates al arco), Atlético Nacional–Santa Fe (1549724:a:6, sin
    Bustos y 0,26 de xG) y Cruzeiro (1492430:b:4, F3 ATK en rojo).
  - **Negado a un débil que sí tenía volumen:** Zulte Waregem (1558670:a:5,
    la sequía no cierra su gol contra un favorito que se expone).
- **FAMILIA-RECORD de goles, sostenida:** Inter, Monza, Colo Colo,
  Estudiantes de Río Cuarto (1493218, 1-2 exacto) y Rayo Vallecano
  (1570441). Atlético Paranaense (1492436:b:4) solo la había igualado, y se
  cortó, como avisa el ámbar.
- **Exactos dentro del acotado:** Bournemouth, Casa Pia–Sporting y Guaraní.

**Propuesta (3.5 y 6-C):**

1. **La celda de goleada se nombra como rama, sin sacar el marcador
   declarado del acotado**, cuando el propio parte la escribió en otro lado:
   - el TDE da `se_rompe` al que persigue;
   - la matriz escribe la goleada tras el gol temprano;
   - el rival concede el doble de la media.

   La lectura dice «2-0, y 4-0 si abre antes del 20'», y el falsador cubre esa
   rama. Es nombrar la cola, no mover el marcador: el acotado sigue mandando.
2. **El gol del débil sale del volumen cruzado** (lo que genera contra lo que
   concede el otro, v4.2). No se da «de cortesía» ni se niega por una sequía:
   una sequía describe la forma, no la vía que el favorito le abre al
   exponerse. Se agrega a la lista de lo que no es un hecho (1.6 c y 3.5).
3. **Calculable:** el veredicto ya mide el intervalo y el marcador acotado.
   Puede medir aparte el **marcador declarado** (exacto, dentro o fuera del
   acotado) para ver si elegir entre los cuatro con la Ley 7 le gana al modal
   del modelo. Hoy esa serie no existe.

**Qué NO:** ningún cambio a `golesAcotados` (es de la app y está calibrado).

### 8. El falsador: lo que la ficha registra, una condición por cláusula, todas las vías

**Qué dice hoy (6-C):**

- El falsador es observable, va sobre el mecanismo y cubre los dos lados.
- Va sobre la conversión o la vía, no sobre el volumen.
- Si el marcador sale del acotado, el falsador nombra la vía que lo saca.

**Lo medido (9 lecciones):**

- **Sin evaluar porque la ficha no lo registra:** Monza–Napoli
  (1550172:a:7) usó «remate de centro en el área» y «remate de cabeza», que la
  ficha no trae.
- **Dos condiciones atadas con «y»:** Xerez–Cádiz (1644386, copa). Falló la
  vía de Cádiz, el falsador no sonó y Xerez marcó por robo.
- **Las vías del rival a medias:** Carabobo–La Guaira (1646922:b:7) tomó dos
  de las tres vías del DTP y el gol llegó por la tercera.
- **Quedaron fuera el penal y el banco:**
  - Llaneros–Junior (1549850): dos penales.
  - Kifisia–Olympiakos (1593347): el banco del débil.
  - Anderlecht (1558662): el gol llegó del banco.
- **Un corte de reloj antes del banco del favorito:** Poblense–Ceuta
  (1644368, copa). El falsador cortaba en el 70' y el parte había escrito que
  el banco entraba desde el 60'.
- **La vulnerabilidad propia declarada, fuera del falsador:** Numancia–Oviedo
  (1644364:b:6, copa). El error de salida del arquero suplente estaba en el
  parte y no en el falsador.
- **Funcionó:** Fluminense, Genoa–Juventus, Metropolitanos, Los Chankas,
  Coquimbo.

**Propuesta (6-C):**

1. **El falsador se escribe sobre lo que la ficha registra:** el gol con su
   minuto, el autor, el asistente y el tipo (penal, autogol), las tarjetas y
   los cambios, y las stats de la ficha (remates al arco, xG si viene). Una
   cláusula que la ficha no puede comprobar no cuenta.
2. **Una condición observable por cláusula.** Si son dos vías, son dos
   cláusulas que suenan cada una, nunca «A y B».
3. **Toma todas las vías del DTP**, incluidos el penal y el banco, más la
   vulnerabilidad propia que el parte declaró.
4. **Ningún corte de reloj antes de la palanca que el propio parte escribió**
   (el banco del favorito, el cambio de régimen del TDE).
5. **Calculable:** el veredicto ya marca un falsador «sin evaluar». Puede
   contarlo por skill y avisar al depositar si una cláusula no nombra ningún
   evento de la ficha. (Esta parte es de Jev o del recibo; se propone, no se
   asume.)

### 9. Copa nacional entre categorías (rúbrica; población `copa`, sin métrica)

**Qué dice hoy:** nada específico. La app ya decide que el 1X2 de las copas
medidas sale del mercado (`separacion_liga.copa_en_agenda`: localía negativa
en copas).

**Lo medido (24 lecciones de la Copa del Rey, 29/10).** No entran a ninguna
métrica (CLAUDE.md: las copas no entran a las tablas). Fijan rúbrica:

- **1X2 del mercado y no del motor:**
  - Hortaleza–Sevilla (1645578): 93 % del mercado contra 49 % del motor.
  - También Granada, Eldense, Valladolid y Huesca.
- **El empate a los 90 con prórroga es una salida del chico:**
  - Numancia–Oviedo (1644364:a:6).
  - SS Reyes–Coria (1644377): el 1-1 declarado leía mejor que el 1X2.
  - Coria (1644377:b:5): sin tarjeta, la espina por defecto contra el de más
    categoría no tuvo base.
- **La K armada en otra categoría no describe el partido:**
  - Racing (1644374): la K de visita en su récord, hecha en LaLiga.
  - Osasuna (1644339:b:7), Getafe (1644358) y Sporting (1644356): rivales
    muy inferiores.
- **INFLADA:** Atlético Baleares (1644343:a:7, no se siguió) y Unionistas
  (1644371, no es razón para ir contra el riesgo).
- **Marcador contra el chico sin datos:**
  - Huesca 1-5 con 0-1 declarado (1644366:b:3): la falta de datos no achica
    la banda.
  - Osasuna (1644339:b:5): un gol de cortesía al de sexta.
  - Laredo (1644357): el más goleador de su grupo, dejado en cero.
  - Athletic (1645579): la goleada escrita en la matriz y no en el marcador.
  - Depor (1644342): un récord de goles recibidos no se proyecta contra otra
    escala.

**Propuesta (sección nueva «Copa nacional», corta, en el paso 6):**

1. **El 1X2 de una copa nacional sale del mercado**; el motor se publica como
   referencia y no gobierna. Es lo que ya hace la app.
2. **Partido único con prórroga o penales:** el empate a los 90 es un hecho
   para `cero` y para el empate del 1X2 (ya está en la lista del punto 3).
3. **Contra un rival de otra categoría** la K de la condición no se usa como
   guía (punto 4.3). El hecho que corta una burbuja es la diferencia de
   categoría, nombrada (ESCALA-LIGAS, fuera del padrón).
4. **Rival sin datos:** la falta de datos no es «pocos goles». La banda sale
   del volumen del grande, y la goleada escrita en la matriz se nombra como
   rama (punto 7.1).

---

## Lo que NO se propone

- **La tarjeta fuerte «en el borde» (50-52 %).** En esta tanda la tarjeta
  falló en los 5 casos:
  - Portuguesa al 52 % (1646923:b:5);
  - Feyenoord al 50 % (1552207);
  - Oriente, con 50 % y 51 % (1645527);
  - Chicó al 50 % (1549726:a:6);
  - Mirassol al 52 % (1492433, el analista la contradijo y ganó).

  Juventus, al 54 %, también falló. Sumado a Fortaleza y Mirassol de la v4.2,
  el patrón es fuerte, pero **mover el corte de «fuerte» es tocar un número
  calibrado de la app** (`burbuja.espina_tarjeta`, ≥ 50 %). Se pide medirlo
  primero (**calculable**: la tasa de la tarjeta fuerte por tramo de su
  probabilidad, 50-52 · 53-59 · 60+, en `espina/calibracion`). Con n ≥ 30 en
  el borde se propone en la revisión siguiente, en los dos lados (Python y TS)
  y con los vectores dorados.
- **Seguir al motor en el partido parejo** (Lille, Coventry, Cambuur, Sporting
  Cristal–Alianza): son 3-4 casos y Parma va en contra. Se mide (punto 2.4).
- **Riesgo alto en las dos burbujas → más empate:** dividido (punto 6).
- **Los dos perfiles DC alineados con más peso:** el umbral y la cuantía
  esperan a la medición calculable del punto 5.4.
- **Recalibrar la tabla de movimiento (1.6) o los puntos del riesgo:** el
  reventón por nivel está dentro del backtest en los cuatro niveles.
- **Lo que es de otros skills:**
  - el D3 del EFE de local como hecho (Alianza Atlético) y la zona ATK en rojo
    (Cruzeiro) son de `efe-clasificador`;
  - las tres vías del DTP enteras son también de `diagnostico-tactico`;
  - la rama `se_rompe` es de `teorema-del-echado`.

  Aquí se escribe solo cómo los lee la síntesis.

## Cómo se aplica si se aprueba

1. **Skill:** `SKILL.md` a v4.4, con el changelog arriba. Cambian:
   - el glosario (espina con tres lecturas);
   - 1.6: procedimiento en cuatro pasos, `guia: pronostico`, lista cerrada de
     `cero`, (e) endurecida, el extremo y las tarjetas que concuerdan;
   - 1.7 (a) y (e): qué es cargar, INFLADA;
   - 3.5: la goleada como rama y el gol del débil;
   - 6-A: el delta ya está en el cierre y el delta sin noticia;
   - 6-B: la lista de lo que no es dato, el favorito sin «+N», los perfiles DC
     que restan a la visita y el empate sin burbujas enfrentadas;
   - 6-C: el falsador sobre la ficha, una condición por cláusula, las vías
     enteras y sin corte antes de la palanca;
   - la sección de copa nacional;
   - la Auditoría 2: una pregunta sobre la espina sin lectura y otra sobre el
     falsador comprobable.
2. **App (código, con su test; no es del skill):**
   - `parte.ESPINAS` deja de aceptar `neutra` en depósitos nuevos. Se rechaza
     con motivo y se sugiere `guia: "pronostico"`; los partes viejos se leen
     igual.
   - `guia: "pronostico"` entra al contrato (`docs/openapi.yaml`, `types.ts`,
     `test_api`) y a `acreditables.espina.porGuia`.
   - El texto de ESPINA-SIGUE-EN-EXTREMO deja de sugerir «cero o neutra».
   - `REGLAS_CALCULADAS_DESDE` lleva la fecha de la v4.4 para no cobrar hacia
     atrás.
   - **Opcional, ya marcado «calculable» arriba**, en este orden de valor:
     1. motor contra mercado cuando eligen distinto (2.4);
     2. «DC-ALINEADOS» y su tasa (5.4);
     3. la tarjeta fuerte por tramo (NO se propone);
     4. «1X2-CARGA-CONTRA-RIESGO» (6.2);
     5. «ESPINA-VS-MARCADOR» (3.5);
     6. «GUIA-CONDICION-CON-T54/ESCALA» (4.3);
     7. el marcador declarado medido aparte (7.3).

     Cada uno es una incidencia para el mantenimiento si el usuario lo pide.
3. **`lecciones.CORTE_VERSION["sad-analysis"]`** suma `("v4.4", <fecha>)` y
   **`SUBIDA_VERSION`** la hora de la subida.
4. **`docs/COWORK.md`:** el prompt cambia la espina (sin `neutra`, guía
   `pronostico`) y suma una línea sobre el delta.
5. **Cierre:** con la v4.4 subida, el botón «Cerrar las anteriores a v4.4»
   pasa a `aplicada` las 139. Esta vez sí entran las 81 de los partes
   anteriores a la v4.3.

## Resumen: cuántas lecciones cierra cada punto

| Punto | Paso del skill | Lecciones | Antes del corte de la v4.3 | Mueve un número |
|---|---|---|---|---|
| 1. Calibración del favorito: el número del mercado y la lista de lo que no es dato | 6-B, Auditoría 2 | 13 | 9 | No |
| 2. El delta sin noticia no da vuelta al elegido ni se suma | 6-A | 9 | 4 | No |
| 3. Espina: sale `neutra`, `cero` con lista cerrada, guía `pronostico` | 1.6, 6-B | 31 | 16 | No (cambia el contrato) |
| 4. Espina en el extremo, con T.54 o con otra escala | 1.6, 1.7 e | 16 | 9 | No |
| 5. Los perfiles DC le quitan a la visita | 6-B | 6 | 3 | No |
| 6. Qué es «cargar» con riesgo alto | 1.7 a | 11 | 3 | No |
| 7. Marcador: la goleada como rama y el gol del débil | 3.5 | 20 | 7 | No |
| 8. Falsador comprobable, por cláusula, con todas las vías | 6-C | 9 | 6 | No |
| 9. Copa nacional entre categorías (población `copa`) | 6, nueva | 24 | 24 | No |
| **Total** | | **139** | **81** | **ninguno** |

De las 139, 115 son acreditables y 24 de copa fijan solo rúbrica. Las dos de
cuarentena que no enseña (Huracán–Tigre, San Antonio–Real Potosí) quedan fuera
de la cuenta.

## Redactada (01/11/2026)

Aprobada entera por el usuario y redactada en `docs/skills/sad-analysis/SKILL.md`
(v4.4 en el frontmatter, el título y el changelog de arriba). Los nueve puntos
quedan así:

- **1 y 2** en 6-B (la lista de lo que no es dato, sin «+N» hacia arriba ni
  hacia abajo, cuándo se reabre) y 6-A (el delta ya está en el cierre, el delta
  sin noticia, los dos elegidos en el partido parejo); pregunta 6 de la
  Auditoría 2 ampliada.
- **3 y 4** en el glosario y 1.6: sale `neutra`, guía `pronostico` (nombre
  exacto del contrato: `guia: total | condicion | pronostico`), procedimiento
  en cuatro pasos, lista cerrada de `cero` (a), lo que no es hecho (c), (e)
  endurecida, (f) nueva sobre las tarjetas débiles que concuerdan, (g) el
  extremo (la regla de ESPINA-SIGUE-EN-EXTREMO) y (h) espina contra marcador;
  1.7 (e) con INFLADA.
- **5** en 6-B (los perfiles DC restan a la visita, una sola fuente). **6** en
  1.7 (a) (qué es cargar). **7** en 3.5 (la goleada como rama, el gol del débil
  desde el volumen cruzado). **8** en 6-C (comprobable, por cláusula, todas las
  vías, sin corte antes de la palanca). **9** en la sección nueva 6-E (copa
  nacional).
- Auditoría 2 suma las preguntas 7 (espina sin lectura) y 8 (falsador
  comprobable); Prohibiciones suma `neutra` y el «+N».
- No se tocó nada de la app ni `docs/COWORK.md` (punto 2 y 4 de «Cómo se
  aplica»): van por su lado. Pendiente del usuario: subir el zip, sumar
  `("v4.4", <fecha>)` a `CORTE_VERSION` y la hora a `SUBIDA_VERSION`, y cerrar
  con 🔑 las anteriores a v4.4.
