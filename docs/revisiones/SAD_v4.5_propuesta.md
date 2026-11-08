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

**Nada de lo que sigue afloja esas reglas.**

---

## Los siete cambios

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
    Lazio (1550183).

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
  dos más; no alcanza.
- **La diferencia de nivel en el extremo:** acertó en Panetolikos, Real
  Madrid, Olimpia (1632057:b) y Trabzonspor. Falló en Libertad (1639859),
  Universitario (1549535:a:3), Cagliari (1550188) y Pereira–Tolima
  (1549852:b:6). Va 4 a 4 y sigue en la lista de (g).
- **El reventón en riesgo alto fuera del backtest** (19 de 21). Es la revisión
  de los puntos calibrados de la app (`--calibrar`, REVENTON §13.2): una zona
  sagrada. Va al usuario con el backtest a la vista, no al skill.
- **Lo que es de otros skills** (aquí solo se escribe cómo lo lee la síntesis):
  - el D3 del EFE de Başakşehir (1584463:b), de `efe-clasificador`;
  - el sistema que no salió en Defensor (1646900), de `diagnostico-tactico`;
  - el ISE de rama 8,33 de Charleroi (1558679), de `teorema-del-echado`.
- **Incumplimientos de una regla que ya existe** (no piden regla nueva):
  - Gaziantep–Kasımpaşa (1584462: el 1X2 contra la espina, el motor y el
    mercado; disciplina 33);
  - Cobresal (1505547:a: +3 sobre el mercado sin dato; 6-B).

## Cómo se aplica si se aprueba

1. **Skill:** `SKILL.md` a v4.5, con el changelog arriba. Cambian:
   - 1.6: el procedimiento (pasos 3 y 4), la regla (c) y la (g) extendida al
     riesgo alto (cambio 2), y la (e) con la condición en el extremo (cambio 3);
   - 1.7: la regla nueva (f) (cambio 1);
   - 3.5 y 1.6 (h): el marcador (cambio 7);
   - 6-B: los perfiles DC (cambio 4);
   - 6-C: el falsador (cambio 6);
   - 6-D (3): la tabla (cambio 5);
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
   6. el conteo de falsadores que sonaron con el 1X2 acertado (cambio 6).

   Cada alerta nueva va a `docs/openapi.yaml` y `REGLAS_CALCULADAS_DESDE` lleva
   la fecha de la v4.5 para no cobrar hacia atrás.
5. **Cierre:** con la v4.5 subida, el botón «Cerrar las anteriores a v4.5»
   pasa a `aplicada` las 179.

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
  con la validación por fecha de la v4.1, como dice 6-B.
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
