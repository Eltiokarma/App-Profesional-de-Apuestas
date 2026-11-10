# Propuesta de revisión · `sad-analysis` v4.4 → v4.5

**Estado:** PROPUESTA, falta que el usuario la apruebe (08/11/2026, usuario:
«ese aprendizaje está al nivel de un skill… vamos corrigiendo la brújula»).
No toca `docs/skills/sad-analysis/SKILL.md` hasta la aprobación. Al aprobarse:
se redacta en el SKILL, `CORTE_VERSION` con la v4.5 y, cuando el usuario suba
el zip, su hora en `SUBIDA_VERSION`.

Nació con un solo cambio (el 1, el origen de la burbuja, medido contra la
casa) y se amplió el mismo 08/11 con las **179 lecciones pendientes** del
skill (dossier `GET /analisis/cowork/revision/sad-analysis`, generado el
08/11 a las 02:32 UTC). Se puede aprobar entera o por cambio: son
independientes.

**Actualizada el 10/11/2026** con el dossier generado el 10/11 a las 02:13
UTC: **237 lecciones pendientes**, las 179 de arriba más **58 nuevas** de
partidos del 08/11 y el 09/11. Lo escrito el 08/11 queda entero y con su
numeración. Lo nuevo va así:

- los cambios **8 y 9**, nuevos;
- «Refuerzo 10/11» y «En contra 10/11» dentro de los cambios 1 a 7;
- la sección **«Medido en conversación (03-09/11)»**, puntos **10 a 19**: lo
  que se midió conversando con el usuario y no está en ninguna lección;
- en cada cambio, una línea **«Se sostiene si… / Lo tumba si…»** para los
  ~50 veredictos del 08-09/11 que todavía se están cerrando, y la marca
  **núcleo / historial** (sección «Núcleo e historial»).

**Jev no marcó ninguna lección que pida mover un número**, tampoco en esta
tanda: la revisión sigue fijando rúbrica.

## De dónde sale

- **179 lecciones pendientes**, todas `ciega` + `PRE`, de partidos del 01/11 al
  07/11 (21 del 01/11, 32 del 03/11, 19 del 04/11, 24 del 05/11, 19 del 06/11 y
  64 del 07/11), en **112 partidos**.
  - **173 acreditables.**
  - **5 de copa nacional** (Copa de la División Profesional de Bolivia: The
    Strongest–Always Ready 1645456, Bolívar–Real Potosí 1645457 y Nacional
    Potosí–Oriente 1645455): población `copa`, fijan rúbrica y no entran a
    ninguna métrica.
  - **1 en cuarentena que enseña** (Atlético Paranaense–Vasco 1492440, DT del
    parte distinto del que dirigió): no cuenta, fija rúbrica.
  - Las dos de cuarentena que **no** enseña (Huracán–Tigre 1493219, San
    Antonio–Real Potosí 1645519) quedan fuera, como en la v4.4.
- **Versión:** casi todas son de partes escritos con la v4.4. Las del tramo de
  las 04:47 del 01/11 se escribieron con la v4.3 (la subida fue a las 08:00 de
  Lima, DEUDA 19); el dossier no dice cuáles de las 21 del 01/11 son de ese
  tramo. Para fijar rúbrica da igual: ninguna de esas 21 sostiene sola un
  cambio.
- **Veredicto por lado:** 76 aciertos, 44 parciales y 59 fallos. **El conteo
  no es una tasa de acierto**: quien cierra el caso nombra el skill sobre todo
  cuando algo falla (`sesgoDeAtribucion`).
- **Jev:** 3 lecciones etiquetadas, las tres `reventon` (Manta 1639831, 2 de
  Mayo 1632050, Jaguares 1549847); 5 con «no pide mover un número» y ninguna
  con «sí». `pidenMoverSinPoder` vacío. Lectura del dossier: «173
  acreditables, pero ninguna pide mover un número: la revisión fija rúbrica».
  **Esta revisión no mueve ningún número de la app.**
- **Lo calculable se marca «calculable»**: la app lo puede calcular o avisar
  con un dato que ya tiene. La v4.5 no se lo hace calcular a la corrida.

**Lo que sumó el dossier del 10/11 (generado a las 02:13 UTC):**

- **237 lecciones pendientes en 152 partidos**: las 179 de arriba (las mismas,
  sin cambios) y **58 nuevas en 40 partidos**, 53 del 08/11 (37 partidos) y 5
  del 09/11 (3 partidos: Alianza Valledupar–Llaneros 1549853, Querétaro–Puebla
  1551036 y Chivas–León 1551037). Todas `ciega` + `PRE`.
  - Las 58 nuevas son **todas acreditables**: ninguna de copa nacional y
    ninguna en cuarentena. El dossier cuenta 231 acreditables (237 menos 5 de
    copa y 1 de cuarentena que enseña).
  - Las dos de cuarentena que no enseña siguen fuera (Huracán–Tigre 1493219,
    San Antonio–Real Potosí 1645519).
  - Ninguna de las 237 es de los cuatro partidos que todavía esperan la
    cuarentena que les corresponde (LDU 1631509, Palmeiras 1492426, Manta
    1639824 y 1639827). LDU–Barcelona SC del 08/11 (1639804) es otro partido.
- **Veredicto por lado de las 58:** 29 aciertos, 8 parciales y 21 fallos. De
  las 237: 105, 52 y 80. **Sigue sin ser una tasa de acierto**
  (`sesgoDeAtribucion`).
- **Versión:** las 58 son de partes escritos con la v4.4.
- **Jev:** 1 lección nueva etiquetada, `reventon` (LDU 1639804:b, confianza
  0,97), y 2 con «no pide mover un número» (esa y Carabobo–La Guaira
  1646935:b). Ninguna con «sí». `pidenMoverSinPoder` sigue vacío.
- **Faltan ~50 veredictos del 08-09/11** que se estaban cerrando cuando se cortó
  el dossier. Por eso cada cambio lleva su «Se sostiene si / Lo tumba si».

## Lo medido

### Lo que mide el dossier (24 casos, 48 lados)

La población medida del dossier es chica y no sirve para juzgar a la v4.4:

| Versión | Casos | Aciertos del 1X2 |
|---|---|---|
| v4.0 | 3 | 0 |
| v4.1 | 5 | 1 |
| v4.2 | 7 | 2 |
| v4.3 | 3 | 1 |
| **v4.4** | **6** | **2** |

- **v4.4 por tramo:** 40-49 acierta 1 de 3 (dijimos 43,7, mercado 43,4);
  50-59, 1 de 1 (58 contra 56,9); 60+, 0 de 2 (61,5 contra 61,7). Con n = 6
  manda el intervalo, y el intervalo cubre casi todo. **No se puede decir si la
  v4.4 mejoró o empeoró nada.** Lo que sí se ve: en todos los tramos «dijimos»
  y «mercado» van a medio punto o menos. La regla «el número del favorito es el
  del mercado» (6-B, v4.4) se está cumpliendo.
- **1X2:** 6 de 24 (25 %), Brier 0,709 contra 0,642 de la línea de base. Es
  peor que la base, pero son 24 casos que no salen al azar: no se lee como la
  tasa del skill.
- **Valor:** apostar siempre a nuestro elegido (`nuestroFavorito`, n 628) da
  **+6,4 %, con el intervalo de −1,8 % a +14,5 %**. Cruza cero, por menos que
  en la v4.4 (+4,2 %, −5,5 a +14). Lo marcado «con valor» (n 206) da −0,7 %
  (−25,7 a +24,2).
- **Espina:** `positiva` 7 de 24 (29 %) y `negativa` 6 de 22 (27 %), contra
  una frecuencia del movimiento de 27 % en los dos casos: «no supera la
  frecuencia todavía». En la cohorte c3 (740 lados) la v4.4 había medido 57 %
  contra 40 %.
- **Reventón:** 30 de 40 burbujas reventaron. En riesgo **alto** reventaron
  19 de 21 (90 %, IC 71-97) cuando el backtest promete 62-67 %. La app lo
  marca `fueraDelBacktest: ["alto"]`: eso **abre la revisión de los puntos,
  no los mueve**, y es un número calibrado de la app, no del skill (va en «Lo
  que NO se propone»). En muy alto, 7 de 12 (58 %), compatible.
- **Respeto del riesgo** (solo lados en alto o muy alto):

  | El 1X2 apostó a que la racha… | Lados | Acierto del 1X2 | Brier |
  |---|---|---|---|
  | sigue (`aFavor`) | 17 | 3 | 0,736 |
  | se corta (`enContra`) | 16 | 3 | 0,788 |

  Ninguno de los dos lados gana: apostar al corte no salió mejor.
- **Goles acotados:** el intervalo acertó 34 de 48 (70,8 %; el backtest promete
  64 %) y el marcador acotado 11 de 24 (45,8 %; promete 40,3 %). Los dos
  están dentro de lo prometido o por encima.

### Lo que mide el dossier del 10/11 (21 casos, 42 lados)

El dossier rehace la población medida en cada corrida: hoy son 21 casos, no
24, porque dos pasaron a cuarentena. No se compara punto a punto con el del
08/11.

- **v4.4 por tramo (n = 8, 2 aciertos):** <40 acierta 0 de 2 (dijimos 37,5,
  mercado 38,0); 40-49, 1 de 3 (43,7 contra 43,4); 50-59, 1 de 1 (58 contra
  56,9); 60+, 0 de 2 (61,5 contra 61,7). **Sigue sin poder decir nada de la
  v4.4.** «Dijimos» y «mercado» siguen a medio punto: 6-B se cumple.
- **1X2:** 6 de 21 (28,6 %), Brier 0,696 contra 0,649 de la base.
- **Valor:** `nuestroFavorito` (n 684) da **+5,3 %, con el intervalo de −2,4 %
  a +13,0 %**: sigue cruzando cero. «Con valor» (n 209), +0,6 % (−24,5 a
  +25,6). Ver el punto 19: el usuario decidió el 03/11 que esto es una alarma,
  no una meta.
- **Espina:** `positiva` 7 de 22 (31,8 %) y `negativa` 6 de 20 (30 %), contra
  28,6 % de frecuencia: «no supera la frecuencia todavía».
- **Reventón:** 25 de 35. En alto, 15 de 17 (88 %, IC 66-97) contra 62-67 % del
  backtest: **ahora sale «compatible»** y `fueraDelBacktest` vacío, así que
  la alarma del 08/11 se apagó con la muestra rehecha. En muy alto, 7 de 12
  (58 %).
- **Respeto del riesgo:** a favor de la racha, 14 lados, 3 aciertos del 1X2
  (Brier 0,708); en contra, 15 lados, 3 aciertos (0,783). Igual que el 08/11:
  apostar al corte no sale mejor.
- **Goles acotados:** el intervalo, 29 de 42 (69 %); el marcador acotado, 9 de 21
  (42,9 % contra 40,4 % prometido).
- **Modo de fallo (Jev, en la población medida):** 18 fallos, 9 `reventon`,
  2 `lectura_efe`, 7 sin etiqueta. Ninguno pide mover un número.

### Lo que dicen nuestras apuestas (DEUDA 26, 08/11)

En las 269 apuestas cerradas desde el 28/10, el elegido rinde **+8,9 ± 5,8
puntos sobre lo que pide la cuota**. El elegido invicto de 5+ partidos rinde
+21,0 ± 13,7 (n = 46). Es la población grande y sostiene que la síntesis, tal
como está, no rompe nada que haya que salir a arreglar con números. Lo que
sigue es rúbrica.

## Lo que la v4.4 acertó y no hay que tocar

De las 179 lecciones, 86 son confirmaciones como estas o caen en «Lo que NO
se propone» (ruido de tasa, casos contradictorios): no piden regla nueva.

- **El número del favorito es el del mercado (6-B).** Se siguió al mercado
  contra el motor, con DIV-MOTOR-MERCADO, ESCALA-LIGAS o la ventana con
  amistosos, y acertó en:
  - Sporting–Moreirense (1575543): 82 % contra el 57 % del motor, Brier 0,05;
  - LASK–Slovan (1635677): Brier 0,145;
  - Mainz–Bayern (1575217): 73 % contra 39,5 %;
  - Flamengo–Grêmio (1492445): 83 % contra 58,6 %, con suspensiones que el
    motor no ve;
  - Viking–Sabah (1635745), Manchester United–Roma (1635695), Shakhtar–Sporting
    (1635723), Pereira–Tolima (1549852), Necaxa–Tijuana (1551030) y
    Libertad–Nacional (1632058).

  El único que va en contra es Lommel–Gent (1558667), y la propia lección lo
  llama varianza del favorito.
- **K-EXTREMO y K-CERCA-EXTREMO son prudencia de carga, no anuncio de corte
  (1.7 e).** El 1X2 se quedó en el mercado sin cargar y la racha siguió en
  Como (1635681), Sassuolo (1550187), PSG (1552815), Real Madrid (1570451),
  Brugge (1635707), Táchira (1646932) y Coritiba (1492446). Reventó en Real
  Sociedad (1570433), Hamburgo (1575218), Leipzig (1635710), Göztepe (1584463)
  y Leones (1639858). En los dos casos la alerta no costó nada.
- **El riesgo muy alto contra un rival muy fuerte se respetó y la burbuja
  reventó:** Remo (1492447), Elversberg (1575212), Troyes (1552815), ADO
  (1552220), Werder (1575214), Moreirense (1575543), Recoleta (1632054),
  Internacional (1492446), Coventry (1557460), Botafogo (1492441), Guaraní
  (1632057) y Slavia (1635726).
- **FAMILIA-RECORD se sostiene (1.7 d):** Beveren (1558677), Volos (1593358),
  Osasuna (1570448), Dortmund (1575212) y Olimpia (1632057). Coincide con
  REVENTON §15. Oriente (1645455) se cortó con una causa que se puede nombrar
  (la roja del 41'), no por estar en récord.
- **La guía `pronostico` (v4.4)** acertó en Toulouse (1552805) y en
  Shakhtar–Sporting (1635723). Atlético–Bayern (1635622) la pedía: la espina
  en `cero` sin un hecho contradijo al 1X2.
- **La estabilidad mueve la confianza, nunca el riesgo:** Beveren (1558677).

**Refuerzo 10/11.** De las 58 lecciones nuevas, 24 son confirmaciones como
estas y 4 caen en «Lo que NO se propone». Algún caso de abajo también se cita
en un cambio: cada lección se cuenta una sola vez, en la tabla del final.

- **6-B con el motor de fiabilidad media.** Se siguió al mercado contra el
  motor (con DIV-MOTOR-MERCADO, `fiabilidadMu` media por amistosos en la
  ventana, R-KT.2 o una noticia) y acertó en:
  - Santa Fe–Pasto (1549862): 86 % contra 49,5 %, por el paro de Pasto;
  - Toluca–Monterrey (1551034): 3 amistosos de 20 en cada ventana; Brier 0,29;
  - PSV en Cambuur (1552219:b:5): 68 contra 29; Brier 0,154;
  - Liverpool en Crystal Palace (1557459:b:6): 61 contra 35,4;
  - Fenerbahçe en Çorum (1584459:a:5): el recién ascendido con el nivel hecho
    en la 1. Lig.

  Falló en Heerenveen–Feyenoord (1552221:a:4, el motor daba al local y ganó el
  local), Brest–Lyon (1552812:a:5, igual, con 7 amistosos en la ventana) y
  Asteras–Kalamata (1593354:a:7, empate). Van 5 a 3, y las dos primeras suman
  a «seguir al motor en el partido parejo» («Lo que NO se propone»).
- **K-EXTREMO y K-CERCA-EXTREMO como prudencia (1.7 e).** No se cargó y
  la racha siguió en Brighton (1557458:a:6), Benfica (1575538:b:6, en el 90+4) y
  Bournemouth (1557462:b:4). En Macará (1639805:a:5, récord igualado de 6
  victorias) el 1X2 se quedó en el mercado (40 %) y la racha se cortó a cero;
  ahí falló la tarjeta fuerte, no la alerta. Reventó en Como (1550191:b:6), Cambuur
  (1552219:a:6), Genoa (1550190:a:5), AEK (1593352:a:5) y Fenerbahçe
  (1584459:b:6).
- **Riesgo alto o muy alto respetado, y la burbuja reventó:** Fiorentina
  (1550189:a:5), Brentford (1557458:b:6), Liverpool (1557459:b:5), Betis
  (1570445:b:4), Villarreal (1570452:a:6) y Deportivo Cali (1549854:b:3).
- **El riesgo es una tasa:** con riesgo muy alto la racha siguió en Alianza
  Valledupar (1549853:a:7) y Querétaro (1551036:a:6, a 1,1 del récord). Es lo
  que dice 1.7 (a): sigue el 28 % de las veces.
- **FAMILIA-RECORD se sostiene (1.7 d):** América (1551035:b:2, «recibe gol»
  llegó a 11). Levadiakos (1593352:b:5) cortó dos récords por una causa
  que se puede nombrar (el lateral de recambio del rival), no por estar en
  récord.

**Nada de lo que sigue afloja esas reglas.**

---

## Los cambios (1-7 del 08/11; 8-9 del 10/11)

### 1. El origen de la burbuja: inflada o construida (paso 1.7, regla nueva (f))

*(El cambio con el que nació esta propuesta; va entero.)*

#### Por qué

La teoría de las burbujas dice cuánto puede rendir un equipo hasta reventar.
Hasta hoy el skill leía el TAMAÑO de la burbuja (K, racha, récord, riesgo) y
no su ORIGEN. La medición del 08/11 (DEUDA 26) dice que el origen importa, y
que importa **contra la casa**, no solo contra el azar:

- **Burbuja INFLADA por un golpe.** Un equipo que acaba de ganar teniendo
  25 % o menos (un batacazo: la K sube mucho porque le ganó a uno más fuerte)
  rinde bajo su cuota en el partido siguiente (−1,4 ± 1,2 puntos) y en el
  subsiguiente (−2,1 ± 1,2), y −2,6 ± 1,6 si ese subsiguiente es contra un
  rival fuerte. La casa le cree el golpe.
- **Burbuja CONSTRUIDA por una racha.** Un equipo con 10+ partidos sin perder
  gana +1,8 ± 1,3 sobre su cuota, y con 15+, +2,6 ± 2,1. La casa no le termina
  de creer.

Fuente: 62.320 partidos con la cuota de CIERRE (football-data.co.uk,
2012-2026; las diez ligas europeas del padrón, Argentina, Brasil y México).
Cada señal se partió en 2012-18 y 2019-26 y sale igual en las dos mitades.
Casi todo el efecto es de Europa: en las tres ligas americanas hay pocos casos
y no se ve. Ninguna señal sola le gana al margen de las casas.

**En nuestras apuestas** (269 cerradas desde el 28/10): con elegido invicto de
5+ acertamos 78 % cuando la cuota pedía 57 % (+21,0 ± 13,7; n = 46). Con
elegido tras batacazo, 14 casos: todavía no dice nada.

#### Lo que cambia (paso 1.7, una regla nueva)

**(f) El origen de la burbuja: inflada o construida** *(v4.5)*. La línea de
`lecturaSad.reventon` dice de dónde viene la burbuja de cada equipo, con el
dato que lo prueba:

- **Inflada**: ganó como gran no-favorito (≤ 25 % sin margen) en uno de sus
  dos partidos anteriores. Con el elegido inflado, el 1X2 **no sube sobre el
  mercado** a ese lado, y el `porque` lo nombra («viene de ganar con 18 % al
  Bayern: burbuja inflada»). Es la misma lógica de «cargar» de 1.7 (a): frena
  la carga, no elige el lado.
- **Construida**: 10+ partidos sin perder. Con el elegido construido, el
  riesgo de reventón **no es razón para bajarlo del mercado** (ya lo dice
  6-B), y el `porque` lo nombra. **No suma puntos sobre el mercado**: la
  regla del favorito de la v4.4 sigue entera.

Lo que **no** cambia: ningún número de la app, ningún «+N» ni «−N», el 1X2 del
motor, los puntos del riesgo y la regla del favorito de 6-B. La señal mueve la
CONFIANZA y la carga, como la estabilidad en 1.7.

#### Lo que pide a la app (después de aprobar)

Que el dato lo calcule la app, no Cowork (CLAUDE.md: «lo que está en nuestra
base se calcula»): en `/burbujas`, por equipo, `origen` con `inflada` (el
partido del golpe, su probabilidad sin margen) y `construida` (partidos sin
perder), y dos alertas de tipo `dato`, **BURBUJA-INFLADA** y
**BURBUJA-CONSTRUIDA**, documentadas en `docs/openapi.yaml`. La probabilidad
del golpe sale de `/cuotas` del partido previo; sin cuota capturada no hay
alerta (no se adivina desde el Elo).

#### Cuándo se reabre

Con 100+ apuestas por grupo en la simulación (elegido inflado, elegido
construido). Si sobre NUESTRO acierto la inflada resta y la construida suma,
con los intervalos fuera de cero, la revisión siguiente propone mover el
número, con la validación por fecha de la v4.1. Si no, la regla (f) se queda
como lectura o se saca.

**Mueve un número:** no.

**A la vista 10/11 (choca con la decisión del usuario del 03/11, punto 19).**
La regla (f) no aparta al 1X2 del mercado: la inflada frena la subida y la
construida no es razón para bajar. Eso va **hacia** el mercado y no choca. Lo
que choca son dos frases:

- el «Por qué» se apoya en el rinde **contra la casa** («la casa le cree el
  golpe», «no le termina de creer»);
- «Cuándo se reabre» dice que, si se confirma, la revisión siguiente
  «propone mover el número».

Si ese número es subir al construido sobre el mercado, eso es apartarse de la
casa para buscar valor, y el usuario lo descartó el 03/11
(`docs/METODO_APUESTA.md`). DEUDA 26 lo dice así: «avisos que muevan la
confianza, no el 1X2».

**Pregunta para el usuario:** ¿«Cuándo se reabre» pasa a decir «si sobre
NUESTRO win rate la inflada resta y la construida suma (100+ por grupo,
intervalo fuera de cero), el aviso mueve la confianza del elegido (el tramo y
el freno del método), nunca el 1X2 sobre el mercado»? La propuesta queda
escrita así hasta que el usuario decida. **Ninguna lección del 08-09/11 trae
un caso de inflada o construida nombrado.**

**Se sostiene si** los veredictos del 08-09/11 con un elegido que viene de un
batacazo (≤ 25 %) aciertan menos que su cuota y los de 10+ sin perder, más.
**Lo tumba si** aparecen al revés con varios casos. Con estos n, ningún
resultado de una semana decide: manda la regla de 100+ por grupo.

**Núcleo:** la regla (f) en 1.7, con sus dos definiciones y lo que hace cada
una. **Historial:** la fuente (62.320 partidos, mitades 2012-18 / 2019-26) y
las 269 apuestas.

---

### 2. Contra el riesgo alto, la espina que dice «sigue» necesita un hecho de la lista (paso 1.6: procedimiento 3 y 4, reglas (c) y (g))

**Qué dice hoy:**

- Paso 3 del procedimiento: con la tarjeta débil, «deciden los skills».
- Paso 4: sin lectura propia, guía `pronostico`, y la espina sigue al 1X2.
- «Ir contra el riesgo calculado se dice.»
- La lista cerrada de hechos que valen para decir «sigue» existe solo **en el
  extremo** (g).

**Lo que dicen las lecciones (36 lecciones en 34 partidos: 18 fallos, 7
parciales y 11 aciertos).** El patrón más repetido de la tanda: con riesgo
alto o muy alto, y casi siempre con la tarjeta (débil) leyendo el corte, la
espina dijo que la racha **seguía**, apoyada en algo que no es un hecho de ESTE
partido, y la burbuja reventó como decían el riesgo y la tarjeta.

- **Falló con estos apoyos:**
  - **obligación de tabla o rival eliminado:** Caracas–Puerto Cabello
    (1646933, los dos lados);
  - **perfiles DC:** Cusco–Sport Boys (1549540:a, «no pierde de local 82 %» y
    la altura), Rubio Ñu–Luqueño (1632055:a, 0-5), The Strongest (1645456:a,
    copa) y Platense (1493238);
  - **promedios de temporada o volumen del DTP:** Espanyol–Depor (1570446:b) y
    Atlas–Pachuca (1551032:a, «la transición de los skills»);
  - **DT nuevo:** La Guaira (1646930, DT de 18 días; ya está en 1.6 c);
  - **calendario de otra competición sin rotación confirmada:** Vasco
    (1492440, semifinal a 4 días; cuarentena que enseña);
  - **bajas propias del medio o un carril rearmado:** Newcastle (1557461) y
    Racing (1570447:b);
  - **un hecho que la hoja del partido desmintió:**
    - Leeds–Tottenham (1557463): «Okafor fuera», y estaba en el banco y fue el
      autor del gol;
    - Progreso–Defensor (1646900): la línea de tres sin Elizalde no salió;
    - Pereira–Tolima (1549852:b:4): el «plan B juvenil» que la hoja desmintió;
  - **la guía `pronostico` llevando a «sigue» contra el riesgo:**
    Monagas–Caracas (1646928:a: las dos tarjetas débiles concordaban en el
    corte y acertaron), Libertad–Cerro (1632052), Cobresal–Everton de Viña
    (1505547:b), Osasuna–Athletic (1570448:a) y 2 de Mayo–Trinidense (1632050,
    los dos lados, cortado por el empate).
- **Acertó con un hecho de este partido:**
  - una **baja del rival confirmada:** Galatasaray–Stuttgart (1635669, sin
    Stiller) y Frankfurt–HSV (1575205, bajas del HSV);
  - una **rotación o un descanso confirmados:** Atlético-MG (1492441, el club
    no relacionó titulares), Santa Fe (1549845, Fagúndez fuera y dos días de
    descanso tras la Copa) y OH Leuven (1558674, el descanso del rival y el P1a
    del motor);
  - la **diferencia de nivel a favor:** Olimpia–Recoleta (1632054, 0,84);
  - **una vía del DTP contra una pareja central nueva** (un hecho del once):
    Everton–Coventry (1557460);
  - **la separación del riesgo baja en la liga** (`separacionLiga`, que la
    tarjeta ya pinta): Chapecoense (1492443).
- **Van en contra de la regla:**
  - Venezia–Udinese (1550196:b): los dos perfiles DC, y acertó;
  - Aldosivi–River (1493227) y Boston River–Torque (1646901): la obligación de
    tabla, y acertaron;
  - Shakhtar–Sporting (1635723:b:7) y Libertad–Nacional (1632058:b): la guía
    `pronostico` contra la tarjeta, y acertaron.

**Propuesta (1.6):**

1. **La lista de (g) vale también contra el riesgo alto o muy alto**, no solo
   en el extremo. Con riesgo alto o muy alto, la espina dice «sigue» solo con un
   hecho de ESTE partido nombrado en el `porque`, de esta lista:
   - la diferencia de nivel a favor de la racha que trae el riesgo
     (`rival.aFavor` / `rival.favorito`);
   - una baja del rival confirmada en el once o por una fuente de nivel A;
   - una rotación o un descanso corto confirmados por el club o en el once.
2. **No son un hecho para ir contra el riesgo:**
   - los perfiles DC, de un lado o de los dos (1 acierto y 4 fallos; para `cero`
     siguen valiendo, regla a);
   - el objetivo de tabla o un rival eliminado (2 aciertos y 2 fallos: es
     contexto, cambio 5);
   - el calendario de otra competición sin rotación confirmada;
   - un promedio de temporada o el volumen del DTP;
   - las bajas propias sin rotación;
   - y lo que ya lista (c): DT nuevo, altura, frecuencia propia.
3. **Un hecho que depende del once probable se rehace con el once oficial**:
   si la hoja lo desmiente, el hecho cae y la espina vuelve a la tarjeta (Leeds,
   Progreso, Pereira). Es lo que ya hace el modo `rehacer` con el DTP. Para la
   espina, se nombra.
4. **La guía `pronostico` no lleva a «sigue» contra el riesgo alto o muy
   alto.** Si el 1X2 elige al lado de la racha y el riesgo es alto o muy alto,
   la espina de ese lado va como en (g) sin hecho: con la tarjeta si la tarjeta
   lee el corte, y si no, al corte más frecuente de la guía calibrada. El
   `porque` dice «sin hecho contra el riesgo alto: no sigue al 1X2».

**Qué NO cambia:** el 1X2. El riesgo sigue frenando la carga y no elige el
lado (1.7 a): la espina puede ir contra el elegido del 1X2 y se dice (1.6,
última viñeta). No se mueve ningún punto del riesgo ni el corte de la tarjeta.

**Calculable (opcional, para la app):** una alerta de tipo `dato`,
`ESPINA-CONTRA-RIESGO`, para la espina que dice «sigue» con riesgo alto o muy
alto y la tarjeta en el corte. Es hermana de ESPINA-SIGUE-EN-EXTREMO: el
recibo pide el hecho en el `porque`; la app no lo juzga.

**Mueve un número:** no.

**Refuerzo 10/11 (8 lecciones en 8 partidos: 4 fallos, 1 parcial y 3
aciertos).**

- **Falló con un apoyo que no es de la lista:**
  - Puebla en Querétaro (1551036:b:3): «eliminado» y C3 = 1. La burbuja
    negativa reventó con un 0-2. Es el punto 2 tal cual: el objetivo de tabla
    no es un hecho;
  - OFI–Atromitos (1593356:a:6): la espina positiva contra el riesgo muy alto,
    «sostenida por el juego» de los skills. Las dos burbujas se cortaron con
    el empate. Es el paso 3 del procedimiento («deciden los skills») chocando
    con el riesgo: el punto 1 lo resuelve;
  - América de Cali–Deportivo Cali (1549854:a:4): la espina positiva contra el
    riesgo muy alto de la K de local, porque la total estaba en 0. Se cortó
    con el empate;
  - Levante–Celta (1570444:b:5): la espina negativa siguió al 1X2 contra el
    riesgo alto, con el Celta en su zona de corte. Empate. Es el punto 4: la
    guía `pronostico` no lleva a «sigue».
- **Acertó con un hecho de la lista (el nivel a favor de la racha):** Zulte
  Waregem–St. Truiden (1558678:b:5, el rival lejos del nivel con que suele
  reventar) y Angers–Nice (1552810:a:4, 0,92 de nivel en contra; además sin
  su goleador).

**En contra 10/11:**

- Porto en Vitória SC (1575544:b:6): riesgo alto, la espina dijo «sigue» sin
  hecho del partido y la burbuja siguió (60 contra 60 del mercado, sin
  cargar). La lección no dice si la app traía `rival.aFavor`. Si lo traía, es
  un acierto con hecho de la lista; si no, es un caso en contra.
- Elche–Betis (1570445:a:5, parcial): contra la tarjeta débil, con hechos del
  EFE y del DTP, y la negativa siguió. La lección no dice el riesgo. Si era
  alto, los hechos «del EFE y del DTP» no están en la lista y acertaron.

Con esto la serie de la regla queda en 22 fallos, 8 parciales y 14 aciertos
sobre 44 lecciones. Las que van en contra suben de 5 a 7.

**Se sostiene si**, en los veredictos del 08-09/11 que faltan, la espina
«sigue» contra riesgo alto o muy alto sin hecho de la lista vuelve a cortarse
más que la frecuencia de «sigue» de la guía calibrada (35 % y 28 %).
**Lo tumba si** esas espinas siguen en la mitad de los casos o más (como
Porto), o si las apoyadas en los skills «por juego» aciertan tanto como las
apoyadas en un hecho de la lista.

**Núcleo:** los puntos 1 a 4 en 1.6 (procedimiento y reglas c y g) y la
pregunta nueva de la Auditoría 2. **Historial:** las listas de casos.

### 3. La K de la condición en su extremo no es guía (paso 1.6, reglas (e) y (g))

**Qué dice hoy:** (g) trata igual el extremo de la total y el de la condición:
«sigue» con un hecho nombrado. (e) ya saca la guía `condicion` cuando la K de
la condición se armó con otro DT o en otra categoría.

**Lo que dicen las lecciones (11 en 11 partidos: 4 fallos, 2 parciales y 5
aciertos que confirman no cargar).** Con K-EXTREMO-CONDICION o
K-CERCA-EXTREMO-CONDICION, la espina leída **con la guía de la condición**
falló en las dos direcciones:

- **Leyó «sigue» y se cortó:**
  - Libertad–Emelec (1639859): a 0,27 del récord, con diferencia de nivel y
    bajas del rival, que son hechos de la lista;
  - La Louvière–Cercle (1558675): a 0,15, con los perfiles DC;
  - Independiente Petrolero–Tomayapo (1645534): la total en muy alto
    apuntaba al corte;
  - Mushuc Runa–Manta (1639831): la altura, sin G. Mina y T.54 contra la
    tarjeta.
- **Leyó el corte y siguió:**
  - Excelsior–Go Ahead (1552218): la K de local en su récord;
  - Pasto–Jaguares (1549847): la K de visita cerca del extremo, contra el
    propio 1X2.

Cuando no se cargó el 1X2 (Coritiba 1492446, Casa Pia 1575536:b:6, Corinthians
1492448:b:3, Kifisia 1593358, Leipzig 1635710), la alerta funcionó como
prudencia: eso se queda.

**Propuesta (1.6 e):** con K-EXTREMO-CONDICION o K-CERCA-EXTREMO-CONDICION,
**la guía no es `condicion`**: la espina se lee con la `total` y, si la total
no da lectura, con `pronostico`. Es la misma lógica de (e): una K de la
condición en su franja más alta no orienta en ninguna dirección. La alerta
sigue frenando la carga del 1X2 (1.7 e). Si la total también está en el
extremo, rige (g) entera.

**Calculable (opcional):** `GUIA-CONDICION-EN-EXTREMO` (tipo `dato`) cuando
el parte declara `guia: condicion` con esa alerta activa del mismo lado.

**Mueve un número:** no.

**Refuerzo 10/11 (3 lecciones en 3 partidos: 1 fallo, 1 parcial y 1
acierto), en la mitad de la prudencia, no en la de la guía.** Con la K de la
condición en la franja alta:

- **se cargó y falló:** América–Pumas (1551035:b:3). La visita al 42 % con
  su K de visita en +17,66; volvió a cero con el empate;
- **no se cargó y se cumplió la prudencia:** Brighton–Brentford (1557458:a:6:
  a 0,07 del récord, 50 % igual al mercado; siguió y lo superó) y
  Fenerbahçe en Çorum (1584459:b:6: K de visita −30,21; se cortó ganando).

En dos lecciones citadas en otros cambios, la condición en el extremo también
empujó una carga: Llaneros (1549853:b:6, cambio 9) y Carabobo (1646935:b,
cambio 5). Ninguna lección nueva dice que la espina se leyó con `guia:
condicion` en el extremo. La mitad «la guía no es `condicion`» no gana ni
pierde casos esta semana.

**Se sostiene si** en los veredictos pendientes las espinas con K de la
condición en el extremo, leídas con la condición, siguen fallando en las dos
direcciones. **Lo tumba si** las leídas con la condición aciertan más que las
leídas con la total en esos mismos lados (n ≥ 15, como dice «Cuándo se
reabre»).

**Núcleo:** la oración nueva en (e) y (g). **Historial:** los casos.

### 4. Los perfiles DC: dicen «la visita no gana», no restan contra el riesgo y se leen con su burbuja (paso 6-B y 1.6 (c); regla del usuario del 05/11)

**Qué dice hoy (6-B, v4.2 y v4.4):** los dos perfiles DC alineados son un
hecho. Los puntos se restan a la visita y se reparten entre el local y el
empate, diciendo cuánto va a cada uno. Un perfil de un solo lado es
frecuencia.

**Lo que dicen las lecciones (14 en 12 partidos: 10 fallos, 1 parcial y 3
aciertos; 3 son de la copa boliviana).**

- **Los dos perfiles se cumplieron… en el empate**, y el 1X2 los había leído
  como ventaja del local:
  - Guayaquil City–Libertad (1639857): local 50 %, empate 29 %; salió empate;
  - Millonarios–América (1549851): +0,5 al local, con «con Gamero empata más
    de lo que gana» en el mismo parte; salió empate;
  - São Paulo–Corinthians (1492448:b:4): 38/32/30; salió 0-0;
  - Universitario–Sport Boys (1549535): +3 al empate, 63/26/11; salió 2-2.
- **Restar a la visita contra el riesgo de su burbuja negativa** es cargar a
  que esa racha siga, y reventó:
  - Rubio Ñu–Luqueño (1632055:b): de 28,5 a 27 con K-CERCA-EXTREMO y riesgo
    muy alto; 0-5;
  - Monagas–Caracas (1646928:b): de 31,3 a 29 con riesgo alto en las dos
    burbujas; ganó la visita;
  - Always Ready (1645456:b, copa): «no gana de visita el 68 %»; ganó por tres;
  - Metropolitanos–Carabobo (1646931): −7 a una visita que el mercado tenía
    primera (36 %), con el local en FAMILIA-RECORD; ganó la visita. Es el
    segundo caso tras 1646923.
  - Lo mismo hacia arriba: La Louvière (1558675) eligió al local por los
    perfiles a 37 contra 35,5 del mercado, con K-CERCA-EXTREMO-CONDICION.
- **Un perfil del ciclo de otro DT:** Vitória (1492449). El 70 % de local que
  no pierde era del ciclo de Jair, con T.54 de cuatro días.
- **Regla del usuario (05/11/2026, incidencia 1227)**, que hoy no está en el
  skill: antes del 1X2 se lee **la burbuja de doble oportunidad** de cada
  equipo en su condición, con su largo, su máximo y la regularidad con que
  revienta, no solo el perfil. La U llegaba con 10 sin perder de local (máximo
  previo 19, 20 burbujas previas) y Sport Boys no gana de visita el 80 %:
  juntas decían «a lo más un empate» para la visita.
- **Van en contra:** Venezia–Udinese (1550196:b), Bolívar (1645457, copa) y
  Trabzonspor–Gaziantep (1584456:b) acertaron apoyados en los perfiles, y en
  Chicó (1549856:a) el perfil de local leyó mejor que la tarjeta fuerte.

**Propuesta (6-B):**

1. **Lo que dicen juntos se escribe como «la visita no gana»**, también en el
   `porque` del 1X2 y en el marcador declarado. La celda del empate del
   acotado se nombra como salida cuando el elegido es el local. No cambia la
   cuantía ni el umbral: el reparto sigue diciendo cuánto va a cada lado.
2. **Los perfiles no restan a la visita bajo el mercado si su burbuja negativa
   está en riesgo alto o muy alto, o en K-CERCA-EXTREMO.** Restarle sería
   cargar a que la racha negativa siga (1.7 a, «qué es cargar», al revés).
   Tampoco sacan del primer lugar a un favorito del mercado ni suben al local
   sobre el mercado con su K de la condición en el extremo.
3. **Un perfil armado con otro DT no es hecho** (la misma regla que (e) para
   la K): con T.54 del lado, el perfil de la condición se nombra y no mueve
   el 1X2.
4. **La burbuja DC se lee con su largo, su máximo y su regularidad** (regla
   del usuario). Viene en `otrasFamilias` de `/burbujas` (REVENTON §15:
   descripción, sin puntos): no se calcula a mano y no suma puntos por sí sola.

**Mueve un número:** no. El umbral «dos de cada tres» y la cuantía siguen
esperando la medición de 6-B.

**Refuerzo 10/11:**

- **Una lección:** América de Cali–Deportivo Cali (1549854:a:4). «De local
  no pierde el 80 %» fue lo que se sostuvo: salió empate. Es el punto 1: el
  perfil dice «no pierde», no «gana».
- **La medición que pedía 6-B ya está hecha, en conversación** (punto 11):
  con los dos perfiles alineados (n 195), la visita no ganó el 80 %, y la cuota
  de 1X pedía 81,7 %. Confirma el punto 1 («la visita no gana») y deja a la
  vista una pregunta sobre la cuantía, en el punto 11.

**Se sostiene si**, en los veredictos pendientes, la visita no gana con los dos
perfiles alineados en una proporción cercana a la del mercado (~80 %), y los
partes que restaron a la visita bajo el mercado con su burbuja negativa en
riesgo alto vuelven a fallar. **Lo tumba si** la visita gana más de una de
cada cuatro con los dos perfiles alineados (el perfil no diría ni eso), o si
restarle con el riesgo alto acierta.

**Núcleo:** los puntos 1 a 4 en 6-B y en (c) de 1.6. **Historial:** los casos
y la regla del usuario del 05/11 con la incidencia 1227 (queda la regla y se
va el caso).

### 5. Lo que está en juego en la tabla se lee en la síntesis (paso 6-D, regla del usuario del 05/11)

**Qué dice hoy:** 6-D (3) pide «presión de tabla… con fuente citada». La tabla
entra sobre todo como D4 del EFE.

**La lección (Universitario–Sport Boys, 1549535:a:2; regla del usuario,
incidencia 1227):** la tabla con lo que está en juego (título, cupos
internacionales, descenso) se lee **en la síntesis y para los dos**. La U,
segunda del acumulado (60 contra 68) y a un punto de la punta del Clausura,
estaba obligada. Sport Boys, 11.º a 4 puntos del 8.º en la pelea por la
Sudamericana, no era «un visitante sin objetivo». El parte solo la tuvo como
D4.

**Propuesta (6-D, punto 3):**

- **Lo que está en juego, por los dos lados**, con los puntos y la distancia
  al objetivo que da la tabla de la app (`TablaPosiciones`, la fase que
  corresponda), no como adjetivo.
- **Es contexto, no un hecho para ir contra el riesgo** (cambio 2): «obligado
  contra eliminado» falló en Caracas–Puerto Cabello (1646933) y acertó en
  Aldosivi–River (1493227) y Boston River–Torque (1646901).

**Calculable (opcional):** la distancia de cada equipo a su objetivo
(punta, cupos, descenso) en el insumo del parte, para no contarla a mano.

**Mueve un número:** no.

**Refuerzo 10/11 (1 lección en 1 partido, un fallo; y una cita del cambio
2):**

- **Carabobo–La Guaira (1646935:b).** El 1X2 y el marcador 1-2 cargaron a que
  siguieran la burbuja de visita en la franja alta y la racha anotando en
  récord de La Guaira. Terminó 0-0, y **el empate le daba la final**. Lección:
  «el visitante al que el empate le sirve no está obligado a seguir la racha,
  y eso pesa más que la racha». Lo que está en juego incluye **a quién le
  sirve el empate**. **Casi seguro, ya es un hecho de la v4.4**: 6-B y la (a)
  de 1.6 listan «una eliminatoria o un partido único donde el empate de los 90
  tiene premio». Si «tiene premio» incluye «clasifica a la final» en la última
  fecha de una fase, el parte incumplió una regla vigente. Si el usuario la
  lee solo para llaves, el texto propuesto la extiende, y eso se dice.
  **Texto propuesto (6-D, punto 3):** «… y a quién le sirve el empate (la
  final, la clasificación, la ida a favor): si le sirve a uno, es el hecho de
  6-B y de (a) de 1.6, y se nombra».
- **Puebla (1551036:b:3, cambio 2):** «eliminado» no fue un hecho contra el
  riesgo alto. Confirma el segundo punto de este cambio: la tabla es contexto.

**Se sostiene si**, en los veredictos pendientes, los partes que nombraron lo
que está en juego para los dos no fallan por eso, y los que dieron a un equipo
«sin objetivo» se equivocan como Sport Boys. **Lo tumba si** la obligación de
tabla vuelve a decidir partidos contra el riesgo alto. En ese caso se vuelve
a la lista de hechos del cambio 2, con la pregunta al usuario.

**Núcleo:** el punto 3 de 6-D con la frase del empate que sirve.
**Historial:** Universitario–Sport Boys y Carabobo.

### 6. El falsador: cada cláusula dice qué refuta, el volumen no refuta el 1X2 y no contradice al DTP (paso 6-C)

**Qué dice hoy (6-C, v4.2-v4.4):**

- Comprobable en la ficha (incluye «remates al arco» entre lo que la ficha
  trae).
- No sobre el volumen.
- Una condición por cláusula.
- Todas las vías del DTP.
- Si la lectura nombra la goleada como rama, el falsador la cubre.

**Lo que dicen las lecciones (15 en 15 partidos: 10 aciertos, 3 parciales y
2 fallos).** El falsador **sonó con el pronóstico acertado** y no separó nada:

- **Una rama del marcador mezclada con las cláusulas del 1X2:**
  - Aris–Panetolikos (1593353): «abre al 11'» era una rama del 2-0 → 3-0;
  - Charleroi–La Louvière (1558665): «cualquier gol de La Louvière» refutaba
    el 1-0, no el 1X2;
  - Villarreal–PSG (1635746) y Porto–Napoli (1635656): la cláusula de la
    goleada sonó con el 1X2 acertado;
  - Westerlo–Charleroi (1558679): «gana por tres o más»;
  - Cruzeiro–Bahia (1492444): «concede como mucho uno».
- **Remates al arco como cláusula del 1X2:**
  - Venezia–Udinese (1550196:a): 5 contra 4, y el local ganó con más xG;
  - Marseille–Toulouse (1552805:a): 3 remates y el pronóstico acertó;
  - Panetolikos–OFI (1593350): «más de dos remates al arco» y OFI hizo
    exactamente 2;
  - Shakhtar–Sporting (1635723:b:5): «menos remates al arco que el rival».

  La ficha los trae, pero son volumen. **Comprobable no quiere decir válido.**
- **El falsador contradijo las vías del DTP del mismo parte:**
  - Mainz–Bayern (1575217:a): «si marca un suplente, la vía fue otra», con el
    banco nombrado en el DTP;
  - Atlético Grau (1549541): «su única vía es la pelota parada», y el DTP
    listaba la transición;
  - Chapecoense–Mirassol (1492443:b): la pelota parada llamada «vía menor»,
    cuando el DTP la tenía como vía 1.
- **No comprobable:** la ficha no dice si un gol fue de pelota parada
  (Mirassol; el TDE v0.1.25 ya la pasó a `otra_via`, 744) ni si fue de
  transición (OFI).
- **Confirman que bien escrito funciona:** Nacional–San Lorenzo (1632053:a:
  las tres vías nombradas se cumplieron) y Paderborn–Frankfurt (1575220:b).

**Propuesta (6-C):**

1. **Cada cláusula dice qué refuta:** «(1X2)» si cae el pronóstico, «(marcador)»
   si cae el marcador declarado o una rama suya. La rama de goleada y el gol
   del rival que solo rompe el marcador van como «(marcador)». Así se cumple
   la regla de la v4.4 (el falsador cubre la rama) sin gatillar el falsador
   del 1X2.
2. **Los remates al arco, el xG y la posesión no van en una cláusula del
   1X2.** Es la regla de la v4.2 («no sobre el volumen»), que el punto 1 de la
   v4.4 dejaba ambigua al listar los remates como comprobables. Se corrige el
   ejemplo.
3. **El falsador no declara falsa una vía que el DTP del mismo parte escribió**
   (banco, transición, pelota parada). Si el DTP la tiene, el falsador la toma
   (ya lo pide la regla 3); nunca la niega.
4. **La pelota parada y la transición no son comprobables en la ficha**: se
   escriben por el autor, el minuto o el tipo que la ficha sí trae, o no van.

**Calculable (opcional, de Jev o del recibo):** contar por skill los falsadores
que sonaron con el 1X2 acertado. Eso es lo que mide si la etiqueta
«(1X2)/(marcador)» sirvió.

**Mueve un número:** no.

**Refuerzo 10/11 (5 lecciones en 5 partidos: 4 aciertos y 1 parcial; las
cuatro son «el falsador sonó y el 1X2 acertó»):**

- **Volumen como cláusula del 1X2 (punto 2):** Genoa–Milan (1550190:b:6):
  «el Milan termina con menos de 3 remates al arco» se dio (2) y el Milan
  ganó.
- **Una cláusula que solo rompía el marcador (punto 1):**
  - Brighton–Brentford (1557458:a:5): «Brentford no marca» falsaba el 2-1
    declarado, no la lectura;
  - Crystal Palace–Liverpool (1557459:a:6): cuatro de seis cláusulas eran
    vías del rival (penal, suplente, central, transición). Dos se cumplieron
    en el 90+5 con 0-3. Con la etiqueta del punto 1, esas vías van como
    «(marcador)», y así se concilia con la regla 3 de la v4.4 («todas las
    vías del DTP»);
  - PSV en Cambuur (1552219:b:6): la rama de goleada estaba escrita en la
    cláusula 5 y se cumplió. Bien escrita; con la etiqueta, va como
    «(marcador)».
- **Celta–Levante (1570444:a:6, parcial):** «el Celta no marca» se cumplió con
  3,12 de xG. Es una cláusula del 1X2 bien hecha; lo que faltaba era el
  marcador (cambio 7).

**En contra 10/11, en parte (Vitória SC–Porto, 1575544:a:5).** «Más remates
al arco del local» sonó 6 contra 4 con el 1X2 acertado. Refuerza el punto 2,
pero la lección propone escribir el falsador del dominio **«con xG o remates
dentro del área»**, y el punto 2 saca también el xG. **Pregunta para el
usuario:** ¿el xG queda fuera de la cláusula del 1X2 (como dice el punto 2,
porque es volumen) o vale como cláusula del DOMINIO, etiquetada «(lectura)»
y no «(1X2)»? Mientras no se decida, el punto 2 queda como está. El DTP ya
pide «M5 con volumen dentro del área» (`PENDIENTES.md`): si la app lo trae,
la pregunta se responde con el dato.

**Se sostiene si**, en los veredictos pendientes, los falsadores que sonaron
con el 1X2 acertado son cláusulas de volumen, de marcador o de una vía del
rival, como estas cuatro. **Lo tumba si** aparecen falsadores «(1X2)» bien
escritos que suenan con el pronóstico acertado. Ahí la etiqueta no separa, y
el problema es otro.

**Núcleo:** los puntos 1 a 4 en 6-C y la pregunta 8 de la Auditoría 2.
**Historial:** los ejemplos.

### 7. El marcador declarado: ni apoyado en un récord de familia ni contra el elegido en silencio (paso 3.5 y regla (h) de 1.6)

**Qué dice hoy:**

- El marcador va dentro del acotado.
- La goleada se nombra como rama (v4.4).
- El gol del débil sale del volumen cruzado.
- FAMILIA-RECORD pide cuidado con la carga (1.7 d).
- (h): la espina y el marcador no se contradicen en silencio.

**Lo que dicen las lecciones (16 en 15 partidos: 9 aciertos, 5 parciales y 2
fallos).**

- **El marcador cargado a que siga un récord de familia, y el récord se
  cortó:**
  - São Paulo–Corinthians (1492448:a): 18 de local anotando, hechos en el
    Morumbi, en un partido mudado a la Vila Belmiro;
  - Unión–Vélez (1493241): 2-1 sobre una racha de recibir gol en récord;
  - Forest–City (1557465:a:5): el 0-1 sobre una sequía récord, cortada al 6';
  - Auxerre–Paris FC (1552811:a): el gol del local sobre 20 partidos
    marcando;
  - PSG–Troyes (1552815:a:5): el 2-0 sobre «gana por dos o más» en récord;
    salió 1-0;
  - Marseille–Toulouse (1552805:b): el gol de visita sobre una racha en
    récord.

  El récord se SOSTIENE más de lo normal (1.7 d, cinco casos arriba), pero el
  marcador exacto no se puede apoyar en eso: un récord es terreno sin
  precedente, no un piso.
- **El marcador contra el elegido del 1X2:**
  - Pereira–Tolima (1549852:b:5): 1-0 local con 57 % a la visita;
  - Willem II–PEC (1552216:b): 1-1 acotado con el 1X2 en la visita, y ganó el
    acotado;
  - Atlético–Bayern (1635622:b:6): +2 al empate y 1-1 contra el propio
    elegido.

  Dos lecturas sin elegir.
- **La goleada se quedó afuera otra vez:**
  - Barcelona–Aston Villa (1635627): con 2,42 goles esperados, el tramo 3+
    (44 %) era el más probable por sí solo;
  - Palmeiras–Remo (1492447:a): la matriz daba goleada al 32 %;
  - Viking–Sabah (1635745): 4 goles;
  - Porto–Napoli (1635656:a:6).

  Es la regla de la v4.4: se refuerza, no se cambia.
- **El volumen de otro partido:** Paris FC (1552811:b), con 2,19 de xG ante
  Monaco, no sostenía el segundo gol. Feyenoord–Inter (1635662:a): la celda del
  local en 0 merecía estar. En contra: Stuttgart (1635669:b) no marcó con 1,85
  de xG (varianza). Lazio–Cagliari (1550183) fue exacto con todo alineado.

**Propuesta (3.5 y 1.6 h):**

1. **Con FAMILIA-RECORD, el marcador declarado no se elige por el récord**
   (ni a que siga ni a que se corte). Se elige entre las celdas del acotado con
   el volumen cruzado, y si la celda elegida depende del récord, se dice y se
   nombra la otra. Una racha de condición hecha en el estadio propio no viaja a
   una sede prestada (São Paulo, un caso: va de ejemplo, no de regla aparte).
2. **(h) se extiende al 1X2:** el marcador declarado lo gana el elegido del
   1X2. Si no, se dice en la lectura cuál de los dos manda y por qué (a veces
   el acotado lee mejor: Willem II–PEC).
3. **La goleada como rama** (v4.4) se nombra siempre que el tramo 3+ del
   favorito sea, por sí solo, el más probable de su distribución, aunque el
   resto del parte no la escriba (Barcelona).
4. **El volumen cruzado es el de la condición en la temporada**, no el de un
   partido.

**Mueve un número:** no. El acotado sigue mandando.

**Refuerzo 10/11 (7 lecciones en 7 partidos: 5 aciertos, 1 parcial y 1
fallo):**

- **Punto 1, el récord no elige el marcador (ni a que siga ni a que se
  corte):**
  - Rayo–Real Sociedad (1570449:b:5): el 2-1 se apoyó «explícitamente» en que
    siguiera el récord de goles de visita del Rayo. Salió 1-0;
  - Deportivo Cuenca–Orense (1639833:a:5, parcial): el récord de 19 de local
    sin ganar por 2+ **bajó** el marcador a 1-0. El corte lo dio el estado del
    partido (el rival que persigue y se rearma al descanso), no la racha;
  - **a favor:** Bournemouth–Ipswich (1557462:b:4). El 1-2 no cargó la
    goleada sobre la burbuja de «gana por 2+» en récord, y acertó.
- **Punto 2, el marcador contra el elegido:** Lazio–Napoli (1550193:b:4). El
  1-2 y el 1X2 al local se contradecían, y salió la celda vecina, 1-1.
- **Punto 3, la goleada como rama:**
  - Aucas–Independiente del Valle (1639803:a:6): el 0-1 declarado no tomó la
    goleada que la matriz escribía como rama («recibe antes del 20'»);
  - **a favor:** PSV en Cambuur (1552219:b:6), con la rama escrita y el
    gatillo al 1'.
- **El acotado cuando el once se degrada:**
  - Portuguesa–Metropolitanos (1646934:a:5): con F3 en los dos lados y dos
    arqueros suplentes, las dos salidas escritas del acotado de un gol
    (penal y gol desde el banco) aparecieron;
  - Union SG–Genk (1558676:a:6): el 2-0 sobreestimó un partido convertido poco
    (1,40 de xG en 23 remates). Es varianza;
  - Celta (1570444:a:6, del cambio 6): un 2-1 sin el goleador del Celta pedía
    el 0-0 por conversión a la vista. Es Ley 4 por zona aplicada al equipo
    propio: la baja del goleador le quita goles a él.
- **Observación sin regla (un caso), Santa Fe–Pasto (1549862:a:5):** con el
  salto de cuota explicado por una noticia (el paro de Pasto), el acotado del
  motor también medía al Pasto profesional y se quedó corto (5-0 contra el 3-0
  declarado). Si el mercado se movió por una noticia, el acotado es de antes
  de la noticia: se nombra la rama larga. Un caso: no va al skill.

**Se sostiene si**, en los veredictos pendientes, los marcadores apoyados en
un récord de familia vuelven a fallar más que los elegidos con el volumen
cruzado, y los marcadores contra el elegido salen en la celda vecina.
**Lo tumba si** los marcadores apoyados en el récord aciertan tanto o más que
el marcador acotado (40 % prometido). Eso diría que el récord sí sirve para el
marcador.

**Núcleo:** los puntos 1 a 4 en 3.5 y en (h). **Historial:** los casos.

### 8. Riesgo alto o muy alto en las DOS burbujas: el empate se nombra, no se carga a que siga una sola (1.7 a)

**Qué dice hoy (1.7 a, v4.4):**

- Con riesgo alto o muy alto, el 1X2 no carga a favor de la racha.
- Ya cita dos casos de «las dos burbujas en riesgo alto y el 1X2 a que
  seguían las dos» (Coventry–Sunderland y Kocaelispor–Rizespor).
- «Riesgo alto en las dos burbujas → más empate» **no** es regla: sigue de
  candidato.

**Lo que dicen las lecciones (4 lecciones en 3 partidos: 3 fallos y 1
acierto; más OFI, contada en el cambio 2).** Con riesgo alto o muy alto (o
K-CERCA-EXTREMO) en los dos lados, el 1X2 eligió el lado que hacía seguir la
racha de uno, y el partido cortó las dos con el empate:

- Chivas–León (1551037:b:7): riesgo alto en las dos totales; el 1X2 cargó a
  que siguiera la de Chivas (`pronosticoVsRacha: aFavor`). Empate. Lección:
  «con riesgo alto en los dos lados, el empate es la salida que corta las
  dos»;
- Barcelona SC–LDU (1639804:a:6 y :b, Jev `reventon`, confianza 0,97, no pide
  mover un número): el 1X2 eligió al local, que hacía seguir la racha negativa
  de LDU. Empate, con LDU superior en volumen. Lección: «con riesgo alto en
  los dos lados y sin ventaja contra el mercado, el elegido no apuesta a que
  siga la racha de un solo lado»;
- **a favor:** Lazio–Napoli (1550193:b:4), K-CERCA-EXTREMO en los dos lados
  y EFE-EMPATE-TECNICO: las dos espinas «sigue» se cortaron con el empate.
  América de Cali–Deportivo Cali (1549854, empate) no entra: la total del
  local estaba en 0 y el riesgo era el de su K de local;
- OFI–Atromitos (1593356, cambio 2): dos burbujas + cortas en muy alto, las
  dos a cero con el empate.

Con lo de la tanda anterior (2 de Mayo–Trinidense, empate; Monagas–Caracas,
ganó la visita), más Rizespor 0-0, Coventry 3-1 y Remo–Botafogo (de la
v4.4), van **6 empates en 9 partidos nombrados**. **Son lecciones elegidas**:
quien cierra nombra el caso cuando falla. No es una tasa.

**Por qué no sube el empate.** El usuario midió el 03-09/11 (punto 10) que la
casa calibra el empate tramo por tramo, y que los equipos que empatan mucho
no empatan más. «Las dos en riesgo» podría estar ya en la cuota. No se toca
el número del empate.

**Propuesta (1.7 a, rúbrica):**

1. **Con riesgo alto o muy alto (o K-EXTREMO / K-CERCA-EXTREMO) en las DOS
   burbujas totales**, el `porque` del 1X2 **nombra el empate como la salida
   que corta las dos**. Es descripción, no un hecho de la lista de 6-B: el
   empate sigue partiendo del mercado.
2. **El elegido no sube sobre el mercado si su victoria hace seguir la racha
   en riesgo del otro lado** (la misma carga de 1.7 a, vista desde el rival).
   Quedarse en el mercado sigue sin ser cargar.
3. **La espina de los dos lados no dice «sigue» en los dos a la vez** sin un
   hecho de la lista del cambio 2.

**⚠️ Medir primero (calculable), antes de cualquier número:** la frecuencia
de empate de los partidos con las dos totales en riesgo alto o muy alto,
contra el empate sin margen del mercado en esos mismos partidos. Hay que
mirarlo en la base (backtest del reventón, con cuota) y en nuestros partes.
Si el empate sale por encima del mercado con el intervalo fuera de cero
(n ≥ 100), la revisión siguiente lo propone como hecho de 6-B. Si no, queda
como descripción. Es la misma medición que pide «Lo que NO se propone» al
partir las reventadas por movimiento.

**Calculable (opcional):** una alerta de tipo `dato`, `RIESGO-EN-LOS-DOS`,
cuando las dos totales están en alto o muy alto. Va con la frecuencia de
empate medida en esos partidos (cuando exista) al lado del empate del
mercado.

**Se sostiene si**, en los veredictos pendientes, los partidos con las dos
burbujas en riesgo alto vuelven a cortar las dos (empate o al otro signo de
la que traía el elegido) más de lo que da la guía calibrada.
**Lo tumba si** en esos partidos el elegido del mercado gana como siempre. Ahí
el punto 2 sobra y el 1 queda como descripción.

**Mueve un número:** no.

**Núcleo:** los tres puntos en 1.7 (a), reemplazando la línea «"más empate"
no es regla». Esa línea pasa a decir: «candidato, con su medición
calculable». **Historial:** los casos.

### 9. La cadena y el pronóstico por equipo dicen lo mismo que el parte (1.6 h extendida; 1.7 d)

**Qué dice hoy:** (h) prohíbe que la espina y el marcador se contradigan en
silencio. El pronóstico por equipo foco entra en `cadena_dtp` como apertura
(CLAUDE.md), pero el skill no dice que tenga que coincidir con el parte.

**Lo que dicen las lecciones (2 lecciones en 2 partidos: 2 fallos).**

- Sport Boys–UTC Cajamarca (1549552:a:5): la cadena cargó a que siguiera la
  racha récord de 12 de local anotando («anota por 13.º partido»), contra
  FAMILIA-RECORD. Se cortó. Lección: «el récord no se escribe como apuesta a
  que sigue».
- Alianza Valledupar–Llaneros (1549853:b:6): **el parte respetó la alerta**
  (24 % a la visita, con la racha de derrotas de visita en su récord), pero
  **la cadena la dio por sexta derrota**. Se cortó.
- Lo mismo en el 1X2 y el marcador de Carabobo (1646935:b, cambio 5).

**Propuesta (1.6 h):** la apertura de la cadena (el pronóstico por equipo
foco) **dice lo mismo que el 1X2 y la espina del parte**. Si el parte frena la
carga por una alerta (FAMILIA-RECORD, K-EXTREMO, K-CERCA-EXTREMO, riesgo alto),
la cadena no la carga. Un récord no se escribe en la cadena como «por N+1.º
partido» (la regla 1 del cambio 7, aplicada a la cadena).

**Calculable (opcional):** `CADENA-VS-PARTE` (tipo `dato`) cuando el
pronóstico de la apertura de un equipo contradice el 1X2 del mismo parte
(gana contra pierde).

**Se sostiene si** en los veredictos pendientes aparecen otras cadenas que
cargaron lo que el parte frenaba y fallaron. **Lo tumba si** la cadena
contradice al parte y acierta en la misma medida: eso diría que la cadena lee
algo que el parte no ve, y se pregunta al usuario cuál manda.

**Mueve un número:** no.

**Núcleo:** una oración en (h). **Historial:** los dos casos.

---

## Medido en conversación (03-09/11)

Lo que se aprendió conversando con el usuario entre el 03 y el 09/11. No está
en ninguna lección. La numeración sigue a la de los cambios para que cada
punto tenga un número propio, pero **no todos son cambios**. Cada punto dice
qué hace en el skill:

- «refuerza la regla X (texto propuesto)»;
- «observación sin regla»: una pista que se vigila y no entra al skill como
  regla;
- «nada que cambiar».

Las cifras son de las mediciones de la conversación (la base y nuestros partes
bajados por la API). Los scripts no quedaron en el repo: el método es el texto.

### 10. El empate: la casa lo calibra, y empatar mucho no es un hecho

- **Medido:** 2.638 partidos de liga con cuota prepartido (01/09-03/11/2026).
  La casa calibra el empate tramo por tramo: con el empate del mercado bajo
  17 %, salió 11,6 % contra 13,6 %; entre 23 y 26 %, 25,2 % contra 24,6 %.
  - **Refuerza 6-B, «el empate parte del mercado» (v4.1).** Texto propuesto,
    al final de esa viñeta: «*(v4.5)* Medido en 2.638 partidos de liga con
    cuota (01/09-03/11/2026): la casa calibra el empate tramo por tramo (bajo
    17 %: 11,6 contra 13,6; 23-26 %: 25,2 contra 24,6). No hay de dónde
    sacarle puntos sin un hecho.»
- **Medido:** con los dos equipos empatando 25 %+ en su condición, el empate
  salió 17,7 % contra 28,7 % que pedía la cuota (n 175). Los que empatan mucho
  NO empatan más.
  - **Refuerza 1.6 (c) y 6-B, «la frecuencia propia de empates no es un
    hecho» (v4.4).** Texto propuesto, en (c), después de «de empates»:
    «(medido: con los dos al 25 %+ en su condición, el empate salió 17,7 %
    contra 28,7 % de la cuota, n 175)».
- **Medido:** la doble oportunidad «12» pierde en todas las ligas, de −3 a
  −10 %.
  - **Nada que cambiar:** el skill no elige mercados de doble oportunidad y la
    Ley 6 lee el 1X/X2 del favorito como alerta, no como apuesta. Si un parte
    propone «12» como salida, esto es lo que se le responde.
- **Medido, en COPAS nacionales:** el empate salió por debajo de la casa, 18,4 %
  contra 22,2 % (n 196). Con el empate del mercado bajo 26 %, 9,7 % contra ~19 %
  (n 124).
  - **Observación sin regla (pista para leer copas).** En 6-E basta con que el
    empate no suba sobre el mercado (ya es la regla). Bajarlo bajo la casa
    sería apartarse del mercado (punto 19). Además las copas no entran a
    ninguna métrica y n 124 es una sola mirada. Se vigila con la regla fija
    de medir las copas aparte.

### 11. Los dos perfiles DC alineados: dicen «la visita no gana», y el mercado ya lo cobra

- **Medido:** con los dos perfiles alineados (local no pierde ≥ 2/3 y visita
  no gana ≥ 2/3, n 195), la visita no ganó el 80 %, y la cuota de 1X pedía
  81,7 %.
- **Refuerza 6-B, «lo que dicen juntos es "el visitante no gana"» (v4.4), y el
  punto 1 del cambio 4.** Es la medición que la v4.4 dejó marcada con ⚠️
  («la cuantía de N no se toca hasta que Aprendizaje mida…»): la cuantía que
  la medición sostiene es **cero**. Es narrativa, no ventaja.
- **[DECIDE USUARIO] Texto propuesto (6-B), que endurece la v4.2/v4.4, no la
  afloja:** «Los dos perfiles alineados se escriben como "la visita no gana" y
  **no restan a la visita bajo el mercado**: el mercado ya lo cobra (n 195: la
  visita no ganó el 80 %, la cuota de 1X pedía 81,7 %). Siguen siendo un
  hecho para la espina `cero` (1.6 a) y se nombran una vez». Si se aprueba,
  el punto 2 del cambio 4 (no restar con la burbuja negativa en riesgo) queda
  contenido en esta regla, más amplia. **Pregunta:** ¿se saca también el
  «+N al empate» por los perfiles? La medición es de «la visita no gana» (1X),
  no del empate solo. Hasta medir el empate de esos 195, el empate sigue
  pudiendo apartarse más de 2 puntos con ese hecho, como dice la v4.1.

### 12. Cómo fallamos: como el favorito de la casa

- **Medido:** 166 fallos en 374 partes (15/09-01/11). El 45 % fue empate y el
  55 % ganó el otro lado: el mismo reparto que los fallos del favorito de la
  casa. El otro lado ganó lo esperado (24,3 % contra 23,9 %) y el empate salió
  menos (20,1 % contra el 25,7 % que le dábamos).
- **Refuerza 6-B, «el empate parte del mercado» (v4.1).** Casi todo el período
  es anterior a la v4.1, cuando decíamos el empate 2 puntos sobre el mercado.
  Esto confirma por qué se igualó.
- **Nada que cambiar:** no hay un modo de fallar propio que pida regla. Por eso
  ninguno de los cambios 1 a 9 sube el empate: el 8 lo nombra y no lo carga.

### 13. Elegir la visita no cuesta; apartarse del mercado, sí

- **Medido (100 partes con la visita elegida):** acierta el 55 % contra el
  48,9 % de la casa (ROI +3,4 %), como cuando se elige el local.
  - **A la par del mercado** (±2 puntos): la visita ganó el 64,5 % (n 62, ROI
    +22 %);
  - **con 2+ puntos menos que la casa:** ROI −20 % (n 31);
  - **con 2+ puntos más:** 1 de 7.
- **Refuerza 6-B, «el número del favorito es el del mercado, hacia arriba y
  hacia abajo» (v4.4).** Texto propuesto, al final de esa viñeta: «*(v4.5)*
  Medido con la visita elegida (100 partes): a la par del mercado ganó el
  64,5 % (n 62); 2+ puntos bajo la casa, ROI −20 % (n 31); 2+ puntos sobre la
  casa, 1 de 7. Lo que cuesta no es el lado: es apartarse del número.» Es
  también el argumento de los cambios 4 y 8 (quedarse en el mercado).
- **Observación sin regla (pista abierta):** con la visita elegida al 40-49 %, el
  local ganó 17 de 38 (44,7 % contra 27,2 % de la casa). Con el local elegido
  en ese tramo no pasa, y en la base tampoco. Se vigila; no es regla.
  **Calculable:** que Aprendizaje parta el tramo 40-49 por el lado del elegido
  (local / visita) y muestre cuánto gana el otro lado contra la casa.

### 14. Win rate por tramo desde el 28/10 (163 partes)

- **Medido:**

  | Tramo | Acierto | Pedía la cuota |
  |---|---|---|
  | < 40 % | 62,5 % | 38,9 % |
  | 40-49 % | 50,0 % | 46,4 % |
  | 50-59 % | 58,7 % | 57,6 % |
  | 60+ % | 76,7 % | 73,4 % |

  El tramo 60+ es el más parejo en los dos períodos (77-78 %).
- **Nada que cambiar:** la calibración se lee, no se aplica (6-B, v4.1). El
  tramo < 40 % rinde muy sobre la cuota, pero no autoriza a subir a nadie
  sobre el mercado (puntos 13 y 19). Es el insumo del freno del método
  (`docs/METODO_APUESTA.md`), no del skill.

### 15. Las rachas entre partidos distintos: sin dependencia

- **Medido:**
  - en la base (2.638 partidos), tras 3 fallos del favorito ganó el 51 %;
  - en nuestros partes del 28/10 al 09/11, tras 3 fallos se acertó 12 de 28.

  Un fallo no hace más probable el acierto siguiente, ni al revés.
- **Refuerza la suspensión de la Ley 5 (nota 5 del SKILL y Paso 3).** Texto
  propuesto, en el Paso 3: «*(v4.5)* Tampoco hay dependencia entre partidos
  distintos en nuestros aciertos: tras 3 fallos seguidos, la base da 51 % al
  favorito y nuestros partes del 28/10 al 09/11, 12 de 28. El resultado de
  otro partido no es un hecho de ESTE.»
- **Nada que cambiar fuera de eso:** el criterio de contacto de la martingala
  (DEUDA 23) se sigue midiendo los lunes con su regla fija (100+ casos tras 3
  fallos, 65 %+). Los 12 de 28 de ahora van en contra del 20 de 30 que lo
  abrió. Es de la simulación, no del skill.

### 16. La anticulebra por liga-día (DEUDA 24): sin culebra

- **Estado de la medición:**
  - medido el 07/11 sobre 34.970 partidos de las ligas nacionales del padrón
    (2022-2026) y 1.221 con cuota en 324 liga-días: tras locales ganadores, el
    empate del siguiente no sube (+0,7 · −1,1 · −1,9 puntos con 1 · 2 · 3+
    previos), y los días van en racha (405 contra 376, z +1,9);
  - el 08/11, con los 62.320 de football-data (DEUDA 26), quedó **muerta**:
    las mitades no coinciden.
- **Pistas abiertas, con pocos casos:**
  - el empate tras 2+ locales ganadores (ROI +5,9 %, n 50; probablemente
    suerte);
  - el favorito VISITANTE tras un día en que ganaron todos los favoritos
    (39,7 % contra 46,6 % de la cuota, n 68). Es lo único con forma de
    culebra;
  - la combinada de los favoritos más fuertes (DEUDA 16).

  Falta medirla con NUESTROS elegidos, en `simulacion.py`.
- **Observación sin regla.** El skill sigue prohibiendo invocar la culebra
  (Prohibiciones permanentes). Si la pista del favorito visitante llega a
  100+ casos con el intervalo bajo cero, la revisión siguiente la mira como
  aviso de **confianza**, no de 1X2.

### 17. La resaca del clásico (DEUDA 25): PISTA con su regla fija

- **Estado de la medición** (07/11, 35 mil partidos, 2023-2026, 417 clásicos
  en 69 rivalidades): **en todas las ligas no hay resaca**. El siguiente
  partido sale +3,3 ± 4,5 sobre lo esperado y el subsiguiente +1,0 ± 4,7.
- **La pista:** en el SUBSIGUIENTE de las grandes ligas europeas (Inglaterra,
  Turquía, España, Portugal, Italia), unos −9 ± 9. Se encontró MIRANDO la
  tabla (~70 comparaciones).
- **Regla fija desde el 08/11/2026:** los clásicos ganados en Inglaterra,
  España, Italia, Portugal y Turquía; el subsiguiente partido de liga del
  ganador contra lo esperado por Elo (o por la cuota sin margen). Se toma en
  serio con **60+ casos nuevos y el intervalo entero bajo cero**.
- **Aparte:** tras cualquier victoria en Perú (−2,7 ± 3,0) y en Bolivia
  (−2,3 ± 3,4) se rinde menos. Es la altura, y el mercado ya la paga.
- **Observación sin regla.** No es un hecho para la espina ni para el 1X2. Si
  un parte la nombra, va como contexto, sin cifra.

### 18. Burbuja inflada y burbuja construida contra la casa (DEUDA 26): es el cambio 1

- **Estado de la medición:**
  - 62.320 partidos con cuota de cierre (2012-2026), con las dos señales en
    las dos mitades;
  - la inflada (ganó con ≤ 25 %): −1,4 ± 1,2 en el siguiente y −2,1 ± 1,2 en
    el subsiguiente;
  - la construida (10+ sin perder): +1,8 ± 1,3; con 15+, +2,6 ± 2,1;
  - ninguna gana sola al margen.
- **En nuestras 269 apuestas:** elegido tras batacazo, n 14; invicto 5+,
  +21,0 ± 13,7 (n 46); 10+, n 13; 15+, n 3. **Pendiente: 100+ apuestas por
  grupo.**
- **Lo que hace en el skill:** el cambio 1, como aviso que mueve la
  **confianza** y la carga, no el 1X2 (con la pregunta del punto 19). Se
  propuso como aviso, pendiente de los 100+ casos.

### 19. La decisión del usuario del 03/11: se mejora el win rate; no se busca valor contra la casa

- **La decisión:** lo que se mejora es el acierto del elegido. No se busca valor
  contra la casa, y Kelly es una alarma, no una meta (`docs/METODO_APUESTA.md`,
  DEUDA 22). El skill no tiene que empujar a apartarse del mercado para
  «encontrar valor».
- **Refuerza 6-B.** Texto propuesto, un párrafo nuevo al empezar 6-B:
  «**El parte no busca valor contra la casa** *(v4.5; usuario, 03/11)*. Lo que
  se mejora es el acierto del elegido. Ninguna regla aparta al 1X2 del
  mercado para "encontrar valor": `valorMercado` y Kelly son alarmas de la
  app, no metas del parte.»
- **Revisión de lo ya escrito, contra esta decisión:**
  - **Cambio 1:** choca en el «Por qué» y en «Cuándo se reabre». Está anotado
    en el cambio, con la pregunta.
  - **«Cuándo se reabre» de esta propuesta («El valor») y el de 6-B en la v4.4:**
    reabren «el favorito sobre el mercado» si `valorMercado.nuestroFavorito`
    sale con el intervalo sobre cero. **Eso usa el valor como disparador para
    apartarse del mercado: choca.** Además el punto 13 mide que apartarse
    cuesta. **Pregunta para el usuario:** ¿el disparador pasa a ser el win
    rate del tramo contra lo que pide la cuota (el mismo del freno), y aun
    así sin subir sobre el mercado, solo como lectura de confianza? Mientras
    no decida, se deja escrito: «`valorMercado` es alarma: si baja mucho, se
    revisa el skill; si sube, no autoriza a subir al favorito sobre el
    mercado».
  - **«Lo que dicen nuestras apuestas» (+8,9 sobre la cuota)** es win rate
    contra lo que pide la cuota: es la medida del método y no choca.
  - **Cambios 2 a 9:** ninguno aparta del mercado. El 4, el 8 y el punto 11
    empujan **hacia** el número del mercado.

---

## Lo que no cambia

- Ningún número de la app: los puntos y los cortes del riesgo, el corte de la
  tarjeta fuerte (≥ 50 %), la guía calibrada (`riesgo.movimiento`), los goles
  acotados, el 1X2 del motor (`unXDos`) y la μ.
- **Las K pesan el 60 % de la LECTURA y no entran al 1X2** (CLAUDE.md). Los
  cambios 2, 3 y 4 tocan la espina y la carga, no el número del 1X2.
- **El número del favorito es el del mercado, hacia arriba y hacia abajo**,
  salvo un dato con su cifra (6-B, v4.4), y la lista de lo que no es un dato.
- **Qué es cargar** (1.7 a, v4.4): por encima del mercado. Quedarse en el
  mercado no es cargar.
- El empate parte del mercado (6-B, v4.1); los dos perfiles DC alineados
  siguen siendo un hecho para el empate y para `cero`.
- Sin `neutra`; la guía `pronostico` se queda (el cambio 2 solo la frena
  contra el riesgo alto).
- Nada calculable lo inventa Cowork: el origen de la burbuja, la burbuja DC y
  la distancia en la tabla salen de la app.
- *(10/11)* El número del empate: el cambio 8 y los puntos 10 a 12 lo
  nombran o lo miden, no lo suben. Ninguna regla de esta propuesta aparta al
  1X2 del mercado para buscar valor (punto 19).

## Lo que NO se propone y por qué

- **Bajar al favorito del mercado por el riesgo alto o muy alto.**
  - Seis lecciones lo piden: Kasımpaşa–Beşiktaş (1584453, 58 % con riesgo
    muy alto, empate), Osasuna–Athletic (1570448:b), Willem II–PEC
    (1552216), Torino–Lecce (1550195), Alverca–Casa Pia (1575536:b:5) y
    Leones–Guayaquil (1639858, 56 contra 56).
  - Pero apostar al corte no salió mejor: `respetoRiesgo` da 3 de 17
    (Brier 0,736) a favor de la racha contra 3 de 16 (0,788) en contra.
    En la cohorte c3, 49 % contra 53 %.
  - Chapecoense (1492443), Libertad–Nacional (1632058:b) y Bolívar
    (1645457) siguieron la racha y acertaron.
  - Contradice 6-B y 1.7 (a). Queda como está.
  - **En contra 10/11, dos lecciones que lo piden con el extremo:**
    - Twente–Ajax (1552222:a:5, parcial): la burbuja en su récord (K +50,82
      en 285 partidos) reventó con el empate; «con K-EXTREMO el pronóstico no
      debería apostar a que la racha siga aunque el mercado lo haga»;
    - Panathinaikos en Iraklis (1593355:b:5, parcial): se puso al favorito
      bajo el mercado (69 contra 73) por K-CERCA-EXTREMO, la racha siguió en
      el 90+4 de penal, y la lección lo llama justificado.

    Las dos chocan con «qué es cargar» (1.7 a, v4.4: quedarse en el mercado
    no es cargar) y con 6-B. El punto 13 mide que bajar al elegido 2+ puntos
    bajo la casa costó un ROI de −20 % (n 31). **Queda como está**, a la
    vista: **¿el usuario quiere que K-EXTREMO sea la única excepción a «el
    número del favorito es el del mercado»?** Hoy no hay medición que la
    sostenga (1.7 e: la alerta no adelanta el corte).
- **Cambiar el corte por defecto de (g), «al otro signo»** (marcado ⚠️ en la
  v4.4).
  - Muchas burbujas en riesgo alto se cortaron por el **empate**: 2 de Mayo,
    Osasuna–Athletic, Everton de Viña, Alverca–Casa Pia, Newcastle, Lecce,
    Willem II–PEC, Lille, Bodø, Leones, Beşiktaş y Telstar.
  - Muchas otras, al otro signo.
  - Las lecciones que nombran el empate están elegidas, y la guía calibrada
    es un número de la app.
  - **Calculable:** que `metricas.reventon` parta las reventadas por
    movimiento (a cero / al otro signo) y por nivel, contra el 27 / 37-45 % de
    la tabla. Con n ≥ 30 por nivel se vuelve a mirar.
  - **10/11, cómo se cortaron las burbujas en el extremo o cerca** (lo que
    dicen las lecciones nuevas):
    - **a cero:** Twente (1552222), Macará (1639805), Lazio–Napoli (1550193),
      América (1551035:b:3) y La Guaira (1646935);
    - **al otro signo:** Cambuur (1552219), Fenerbahçe (1584459), AEK
      (1593352), Genoa (1550190) y Llaneros (1549853);
    - **siguieron:** Heerenveen (1552221), Brighton (1557458), Bournemouth
      (1557462), Benfica (1575538), Panathinaikos (1593355) y Querétaro
      (1551036).

    Va mitad y mitad entre los dos cortes. El ⚠️ de (g) sigue en pie.
  - **En contra 10/11 del corte por defecto:** Heerenveen–Feyenoord
    (1552221:a:5). La espina negativa con la K en su récord (+24,04) falló: la
    burbuja siguió a +29,29. Lección: «el extremo pide no cargar a que la racha
    siga, no habilita a pronosticar el corte sin un hecho del partido». Va en la
    línea de lo que (g) ya dice («Leer el corte en el extremo sin hecho tampoco
    funcionó»: Medellín, Querétaro). Junto con Twente, dice que en el extremo
    la espina **no orienta en ninguna dirección**, la misma lógica del cambio 3
    para la condición. **Pregunta para el usuario:** sin hecho, ¿la espina en el
    extremo sigue yendo «al corte más frecuente de la guía calibrada», o pasa a
    `pronostico` (sigue al 1X2, que no carga)? No se cambia sin la medición
    calculable de arriba.
- **La tarjeta fuerte en el borde.**
  - Esta tanda suma cuatro fallos: Chicó (1549856:a, 52 %), Groningen
    (1552215, 53 %), Bodø (1635640:a, 54 %, con ESCALA-LIGAS) y Sport Boys
    (1549535:b, 55 %, salió cero).
  - Más la tarjeta de la condición corta de Pereira (1549852:a: dos partidos
    contra un mercado de 18 %).
  - Mover el corte (≥ 50 %) es tocar un número calibrado, en los dos lados y
    con los vectores dorados. Sigue pendiente la medición calculable de la
    v4.4 (la tasa por tramo de la tarjeta, 50-52 · 53-59 · 60+); con n ≥ 30 en
    el borde se propone.
- **Dos tarjetas que concuerdan, con más peso.** Lo pide Monagas–Caracas
  (1646928:a), pero los casos van y vienen:
  - las débiles concordantes fallaron en Libertad–Nacional (1632058:a) y en
    Forest–City (1557465:a:6);
  - acertaron en Leeds–Tottenham (1557463);
  - las fuertes concordantes acertaron en Atlante (1551031, con roja al 15') y
    Lazio (1550183);
  - *(10/11)* las fuertes concordantes **fallaron** juntas en Santa
    Clara–Gil Vicente (1575542:a:4, con `fiabilidadMu` media por 5 amistosos y
    F3 en el local): «la concordancia no compensa el degradado del once».

  (f) se queda.
- **La burbuja de un partido leída por el riesgo solo.** El corte leído solo
  por el riesgo falló en San Luis–Juárez (1551029, los dos lados), San
  Lorenzo (1632053:b, con T.54 y R-KT.2), Sport Boys (1549540:b) y Málaga
  (1570447:a). Las propias lecciones dicen «un caso más para la tasa». (d)
  sigue como está.
- **El delta del mercado:** uno y uno. Gualberto Villarroel (1645535) va a
  favor de leerlo, con una roja al 38'. Chicó–Inter (1549856:b) va en contra.
  6-A se queda.
- **Seguir al motor en el partido parejo:** Gimnasia–Belgrano (1493233:b, ganó
  el favorito del motor) y Lommel–Gent (1558667) suman a la serie de 6-A. Son
  dos más; no alcanza. *(10/11)* Suman Heerenveen–Feyenoord (1552221:a:4) y
  Brest–Lyon (1552812:a:5): las dos con fiabilidad media y el motor más cerca.
  En contra, cinco aciertos del mercado en la misma situación («Lo que la v4.4
  acertó», 10/11). Y el punto 13 mide que apartarse cuesta.
- **La diferencia de nivel en el extremo:** acertó en Panetolikos, Real
  Madrid, Olimpia (1632057:b) y Trabzonspor. Falló en Libertad (1639859),
  Universitario (1549535:a:3), Cagliari (1550188) y Pereira–Tolima
  (1549852:b:6). Va 4 a 4 y sigue en la lista de (g).
- **El reventón en riesgo alto fuera del backtest** (19 de 21). Es la revisión
  de los puntos calibrados de la app (`--calibrar`, REVENTON §13.2): una zona
  sagrada. Va al usuario con el backtest a la vista, no al skill. *(10/11)*
  Con la muestra rehecha (15 de 17), el dossier ya lo da «compatible» y
  `fueraDelBacktest` sale vacío. Se mira de nuevo con n ≥ 30.
- **Lo que es de otros skills** (aquí solo se escribe cómo lo lee la síntesis):
  - el D3 del EFE de Başakşehir (1584463:b), de `efe-clasificador`;
  - el sistema que no salió en Defensor (1646900), de `diagnostico-tactico`;
  - el ISE de rama 8,33 de Charleroi (1558679), de `teorema-del-echado`.
- **Incumplimientos de una regla que ya existe** (no piden regla nueva):
  - Gaziantep–Kasımpaşa (1584462: el 1X2 contra la espina, el motor y el
    mercado; disciplina 33);
  - Cobresal (1505547:a: +3 sobre el mercado sin dato; 6-B);
  - *(10/11)* Chivas–León (1551037:b:7): el 1X2 cargó a que la racha siguiera
    con riesgo alto (1.7 a). Va al cambio 8 por el patrón de las dos burbujas;
  - *(10/11)* Carabobo–La Guaira (1646935:b): probablemente el empate con
    premio de 6-B y de (a) de 1.6, sin aplicar (cambio 5).

## Cómo se aplica si se aprueba

1. **Skill:** `SKILL.md` a v4.5, con el changelog arriba. Cambian:
   - 1.6: el procedimiento (pasos 3 y 4), la regla (c) y la (g) extendida al
     riesgo alto (cambio 2), y la (e) con la condición en el extremo (cambio 3);
   - 1.7: la regla nueva (f) (cambio 1);
   - 3.5 y 1.6 (h): el marcador (cambio 7);
   - 6-B: los perfiles DC (cambio 4);
   - 6-C: el falsador (cambio 6);
   - 6-D (3): la tabla (cambio 5), con la frase del empate que sirve
     (10/11);
   - *(10/11)* 1.7 (a): las dos burbujas en riesgo (cambio 8), reemplazando la
     línea «"más empate" no es regla»;
   - *(10/11)* 1.6 (h): la cadena (cambio 9);
   - *(10/11)* 6-B: los textos de los puntos 10, 13 y 19, y el del 11 si el
     usuario lo aprueba; 1.6 (c): el número del punto 10; Paso 3: el texto
     del punto 15;
   - Auditoría 2: una pregunta nueva, «¿alguna espina dice "sigue" contra
     riesgo alto o muy alto? ¿con qué hecho de la lista?», y la 8 suma
     «¿cada cláusula dice si refuta el 1X2 o el marcador?».
2. **`lecciones.CORTE_VERSION["sad-analysis"]`** suma `("v4.5", <fecha>)` y
   **`SUBIDA_VERSION`** la hora de la subida.
3. **`docs/COWORK.md`:** el prompt suma la burbuja DC antes del 1X2 (ya pide el
   perfil DC) y la etiqueta «(1X2)/(marcador)» del falsador.
4. **App (código, con su test; no es del skill, cada uno es una incidencia si
   el usuario lo pide), en este orden de valor:**
   1. `origen` en `/burbujas` con BURBUJA-INFLADA / BURBUJA-CONSTRUIDA
      (cambio 1);
   2. ESPINA-CONTRA-RIESGO (cambio 2);
   3. el reparto de las reventadas por movimiento en `metricas.reventon`
      («Lo que NO se propone»);
   4. GUIA-CONDICION-EN-EXTREMO (cambio 3);
   5. la distancia al objetivo en la tabla (cambio 5);
   6. el conteo de falsadores que sonaron con el 1X2 acertado (cambio 6);
   7. *(10/11)* la frecuencia de empate con las dos totales en riesgo alto o
      muy alto contra el empate del mercado, en la base y en nuestros partes,
      y la alerta `RIESGO-EN-LOS-DOS` (cambio 8);
   8. *(10/11)* `CADENA-VS-PARTE` (cambio 9);
   9. *(10/11)* el tramo 40-49 partido por el lado del elegido en
      Aprendizaje (punto 13).

   Cada alerta nueva va a `docs/openapi.yaml` y `REGLAS_CALCULADAS_DESDE` lleva
   la fecha de la v4.5 para no cobrar hacia atrás.
5. **Cierre:** con la v4.5 subida, el botón «Cerrar las anteriores a v4.5»
   pasa a `aplicada` las 179 del 08/11 y las 58 del 10/11 (las 237). Las que
   lleguen de los veredictos del 08-09/11 después de las 02:13 UTC del 10/11
   no están leídas acá: no se cierran con el botón sin mirarlas.

## Cuándo se reabre

- **Cambio 1:** con 100+ apuestas por grupo (arriba).
- **Cambio 2:** con la alerta ESPINA-CONTRA-RIESGO (o contando a mano en
  Aprendizaje) y n ≥ 30. Si la espina «sigue» con un hecho de la lista no
  acierta más que la frecuencia de «sigue» en ese nivel (35 % alto, 28 % muy
  alto), la lista se achica. Si acierta, se mantiene.
- **Cambio 3:** si la espina leída con la total en esos lados (n ≥ 15) no
  acierta más que la leída con la condición en la cohorte vieja, se vuelve
  atrás.
- **Cambio 4:** cuando Aprendizaje mida «la visita no gana» con los dos
  perfiles alineados (pendiente de la v4.4). Con n ≥ 30, la siguiente revisión
  propone, o no, cuánto va al empate.
- **Cambio 6:** si tras dos semanas los falsadores «(1X2)» siguen sonando con
  el pronóstico acertado en más de uno de cada cuatro partes, la regla no
  alcanzó.
- **El valor:** si `valorMercado.nuestroFavorito` sale con el intervalo entero
  sobre cero (hoy −1,8 % a +14,5 %), se reabre «el favorito sobre el mercado»
  con la validación por fecha de la v4.1, como dice 6-B. *(10/11: hoy −2,4 % a
  +13,0 %. **Choca con la decisión del usuario del 03/11**: está a la vista,
  con la pregunta, en el punto 19.)*
- *(10/11)* **Cambio 8:** con la medición calculable (n ≥ 100 partidos con las
  dos en riesgo, con cuota).
- *(10/11)* **Cambio 9:** si `CADENA-VS-PARTE` (o la cuenta a mano) muestra
  que la cadena que contradice al parte acierta tanto como él, se pregunta al
  usuario cuál manda.
- *(10/11)* **Punto 11:** con el empate de los 195 partidos con los dos
  perfiles alineados medido contra el del mercado.
- *(10/11)* **Puntos 13, 16 y 17:** la pista de la visita al 40-49 se mira con
  el tramo partido. La anticulebra se mira con nuestros elegidos en
  `simulacion.py`. La resaca del clásico, con su regla fija (60+ casos).
- **La v4.4 en sí:** con n ≥ 30 partes ciegos de la v4.4 en la tabla por
  tramo (hoy 6), la revisión siguiente dice si mejoró o empeoró. Esta no lo
  puede decir.

## Resumen: cuántas lecciones toca cada cambio

| Cambio | Paso del skill | Lecciones | Fallos / parciales / aciertos | Partidos | Mueve un número |
|---|---|---|---|---|---|
| 1. Origen de la burbuja (inflada / construida) | 1.7 (f) | 0 (sale de DEUDA 26) | — | — | No |
| 2. Contra el riesgo alto, un hecho de la lista | 1.6 proc. 3-4, (c), (g) | 36 | 18 / 7 / 11 | 34 | No |
| 3. La condición en el extremo no es guía | 1.6 (e), (g) | 11 | 4 / 2 / 5 | 11 | No |
| 4. Perfiles DC: «la visita no gana», sin restar contra el riesgo, con su burbuja | 6-B, 1.6 (c) | 14 | 10 / 1 / 3 | 12 | No |
| 5. La tabla en juego, en la síntesis | 6-D (3) | 1 | 1 / 0 / 0 | 1 | No |
| 6. El falsador: qué refuta, sin volumen, sin contradecir al DTP | 6-C | 15 | 2 / 3 / 10 | 15 | No |
| 7. El marcador: ni del récord ni contra el elegido | 3.5, 1.6 (h) | 16 | 2 / 5 / 9 | 15 | No |
| Confirmaciones y «no se propone» | — | 86 | 22 / 26 / 38 | — | No |
| **Total** | | **179** | **59 / 44 / 76** | **112** | **ninguno** |

De las 179, 173 son acreditables, 5 de copa (fijan solo rúbrica) y 1 de
cuarentena que enseña. Las dos de cuarentena que no enseña quedan fuera.

### Las 58 del 10/11 (partidos del 08-09/11, todas acreditables)

Cada lección se cuenta una vez, donde más pesa. Las citas cruzadas entre
cambios no se suman dos veces.

| Destino | Lecciones | Fallos / parciales / aciertos | Partidos |
|---|---|---|---|
| 2. Contra el riesgo alto, un hecho de la lista (refuerzo y en contra) | 8 | 4 / 1 / 3 | 8 |
| 3. La condición en el extremo (refuerzo de la prudencia) | 3 | 1 / 1 / 1 | 3 |
| 5. La tabla en juego: a quién le sirve el empate | 1 | 1 / 0 / 0 | 1 |
| 6. El falsador | 5 | 0 / 1 / 4 | 5 |
| 7. El marcador | 7 | 1 / 1 / 5 | 7 |
| **8. Las dos burbujas en riesgo (nuevo)** | 4 | 3 / 0 / 1 | 3 |
| **9. La cadena dice lo que el parte (nuevo)** | 2 | 2 / 0 / 0 | 2 |
| Confirmaciones de 6-B con el motor de fiabilidad media | 8 | 3 / 0 / 5 | 8 |
| Confirmaciones del riesgo, el extremo y FAMILIA-RECORD | 16 | 4 / 2 / 10 | 15 |
| «Lo que NO se propone» (en contra, a la vista) | 4 | 2 / 2 / 0 | 4 |
| **Total** | **58** | **21 / 8 / 29** | **40** |

Los cambios 1 y 4 no tienen lecciones propias en esta tanda. El 1 lleva la
pregunta del punto 19; el 4, la medición del punto 11 y una cita del cambio 2.
**Ninguno de los cambios mueve un número.** Los puntos 10 a 19 son de la
conversación: no son lecciones y no entran a la tabla.

## Núcleo e historial

Para cuando se aplique `NUCLEO_SKILLS_propuesta.md` (03/11, no se aplica
acá): el **núcleo** es lo que la corrida necesita, arriba del `SKILL.md`; el
**historial** son los casos y de dónde salió cada regla, que van a
`references/HISTORIAL.md`. Aquel documento dice que en 1.6 y 6-B la regla y su
caso van mezclados. Esta propuesta ya los escribe separables:

| Cambio / punto | Núcleo (SKILL.md) | Historial (`references/HISTORIAL.md`) |
|---|---|---|
| 1. Origen de la burbuja | regla (f) de 1.7: las dos definiciones y lo que frena | la fuente de 62.320 partidos, las mitades y las 269 apuestas |
| 2. Un hecho contra el riesgo alto | puntos 1-4 en 1.6 y la pregunta de la Auditoría 2 | las listas de casos del 08/11 y del 10/11 |
| 3. Condición en el extremo | la oración de (e) y (g) | los casos |
| 4. Perfiles DC | puntos 1-4 en 6-B y (c) | los casos y la incidencia 1227 |
| 5. La tabla en juego | el punto 3 de 6-D con «a quién le sirve el empate» | Universitario–Sport Boys y Carabobo |
| 6. El falsador | puntos 1-4 de 6-C y la pregunta 8 de la Auditoría 2 | los ejemplos |
| 7. El marcador | puntos 1-4 de 3.5 y (h) | los casos |
| 8. Las dos burbujas en riesgo | los tres puntos de 1.7 (a) | los casos y el conteo de 6 empates en 9 |
| 9. La cadena | una oración en (h) | los dos casos |
| 10, 13, 15, 19 | la frase de cada texto propuesto, en su paso | las cifras completas de la medición |
| 11 | el texto de 6-B, si se aprueba | la medición de los 195 |
| 12, 14, 16, 17, 18 | nada (observación o nada que cambiar) | todo: el estado de la medición de cada uno |

**Lo que la corrida no necesita leer:** los conteos por cambio, las tablas
de este documento y «Lo que NO se propone». Todo eso es historial.
