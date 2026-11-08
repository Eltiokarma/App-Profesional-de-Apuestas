# Estudio · la génesis del gol en el DTP (`diagnostico-tactico`)

**Estado:** ESTUDIO, no regla. Hecho el 08/11/2026 a pedido del usuario («al
DTP le falta la teoría de cómo llegó el gol»). No toca `docs/skills/`, ni el
código, ni ningún número del skill. La propuesta que sale de acá está al final
de `docs/revisiones/DTP_v1.8_propuesta.md` («Cambio adicional (08/11, pedido
del usuario): la génesis del gol»).

## Qué se preguntó

1. Cómo llegaron de verdad los goles, con crónicas de la web.
2. Si las `viasGol` que el DTP declaró ANTES del partido (M2, lista `foco` del
   equipo que anotó o lista `rival` del bloque contrario) cubrían esa forma de
   gol.
3. Qué fuentes sirven por liga para conseguir la crónica.
4. Si el M4 real de los cierres (`dtp.bloques[].cierre.m4Goles`) trae la
   autopsia o queda vacío / «sin mecánica».

## Muestra

15 partidos con parte y veredicto de la semana 01-07/11 (los `fixtureId` de las
lecciones del dossier), **45 goles** según la ficha (`/fixtures/{id}/ficha`,
`tactica.eventos`, tipo `Goal`; los «Missed Penalty» que la API manda como
`Goal` no se cuentan como goles).

| Liga | Partidos (fixtureId) | Goles |
|---|---|---|
| Premier League | Liverpool 0-1 Arsenal (1557453) | 1 |
| Serie A | Juventus 2-0 Napoli (1550182) | 2 |
| Champions | Barcelona 3-0 Aston Villa (1635627) · Atlético 0-2 Bayern (1635622) · Fenerbahçe 3-2 Liverpool (1635658) · RB Leipzig 2-3 Manchester City (1635710) | 15 |
| Argentina | Boca 1-0 River (1493214) | 1 |
| Brasil | Flamengo 3-1 Grêmio (1492445) | 4 |
| Perú | Universitario 2-2 Sport Boys (1549535) · Atlético Grau 1-3 Universitario (1549541) · Alianza Lima 1-0 Cienciano (1549537) | 9 |
| Liga MX | Monterrey 3-3 Tijuana (1551025) · América 2-2 Toluca (1551026) | 10 |
| Colombia | Deportivo Cali 2-0 Chicó (1549846) · Cúcuta 1-0 Santa Fe (1549845) | 3 |

**Probados y descartados:** Valencia–Real Madrid (1570451, 3 goles) y
Nottingham Forest–Manchester City (1557465, 4 goles), del 07-08/11. Ninguna
búsqueda (inglés, español, con goleadores y fecha) devolvió la crónica: la web
todavía no la tenía indexada a menos de 48 horas. **Ese es un hallazgo:** el
cierre que se corre al día siguiente puede no encontrar la crónica aunque
después aparezca (el skill ya prevé reclasificar «si la crónica aparece
después»).

## La taxonomía usada (cerrada)

Parte de la propuesta del pedido; los datos pidieron **una categoría nueva** y
**dos marcas** que no son categoría:

- **Pelota parada:** córner directo · segunda jugada de córner (incluye el
  córner en corto) · tiro libre directo · centro de tiro libre · lateral (largo
  o corto con envío al área).
- **Penal** (con su origen: falta, mano, VAR, y si fue convertido en el rebote).
- **Transición tras recuperación:** alta · media · baja (incluye la contra
  tras un córner rival).
- **Error en la salida bajo presión** (pase o despeje propio en campo propio
  que el rival roba).
- **Ataque elaborado:** centro lateral · pase interior entre líneas ·
  combinación por dentro · desborde individual.
- **Balón largo a la espalda** *(NUEVA)*: pelotazo o pase elevado que deja al
  delantero solo contra un central o el arquero, sin transición previa (Viñas
  en el América–Toluca, Nusa en el Leipzig–City). No cabía en ninguna: no es
  transición (no hay recuperación), ni ataque elaborado.
- **Tiro de media distancia.**
- **Rebote o segunda jugada en el área** (del arquero o de un despeje).
- **Error del arquero** (en la atajada; el error con el pie va a «error en la
  salida»).
- **Autogol.**
- **Sin fuente** (la fuente da autor y quizás asistente o la definición, pero
  no el disparador ni la secuencia).

Marcas aparte de la categoría: **desvío** (el remate cambia de dirección en un
rival: Raphinha, Nyoni, Greenwood) y **banco** (el autor o la pieza del gol
había entrado desde el banco o el parte lo listaba como suplente).

Comparación con `viasGol`: **Sí** = la categoría y la zona o el intérprete
estaban escritos para el equipo que anotó (en su lista `foco` o en la `rival`
del otro bloque). **Parcial** = estaba la categoría o el intérprete, no los
dos, o solo la definición. **No** = ni la categoría ni el intérprete.

## Gol por gol

| # | Partido | Min | Anota | Categoría | Disparador → secuencia → definición | ¿En `viasGol`? | Fuente |
|---|---|---|---|---|---|---|---|
| 1 | Liverpool–Arsenal | 16' | Havertz (ARS) | Error en la salida bajo presión | Pase de Alisson a Jacquet que pierde → Madueke y Rice combinan por la derecha → centro de Rice, Havertz empuja al segundo palo | **Sí** («error de Liverpool en la salida bajo presión tras pérdida» + «centro al segundo palo») | https://www.irishnews.com/sport/soccer/arsenal-win-at-liverpool-to-go-three-points-clear-at-premier-league-summit-4IAZINJN25K2LIKKYWYM5DAPHI/ |
| 2 | Juventus–Napoli | 70' | Alajbegovic (JUV) | Tiro de media distancia | La fuente no da el origen («out of nowhere») → asistencia de Zhegrova → zurdazo del borde del área al ángulo, por dentro del palo | **Parcial** (media distancia escrita para Douglas Luiz y McKennie; Zhegrova como banco) | https://www.livescore.com/en/news/football/serie-a/serie-a-juventus-2-0-napoli-alajbegovic-and-boga-magic-revives-juve-football-italia/ |
| 3 | Juventus–Napoli | 87' | Boga (JUV, banco) | Tiro de media distancia | Cambiaso la baja → Boga en el borde → rosca de derecha al palo largo, Napoli con diez | **Sí** (banco: Boga; media distancia) | misma |
| 4 | Barcelona–Aston Villa | 7' | Lamine Yamal (BAR) | Error en la salida bajo presión | Pase errado de João Gomes que corta Yamal → supera a Pau Torres → remate al palo largo | **Parcial** (escrito «Suzuki y los centrales»; perdió un medio) | https://www.flashscore.com/news/soccer-champions-league-barcelona-aston-villa-report-2026-11-03/tj6B04pp/ |
| 5 | Barcelona–Aston Villa | 52' | Raphinha (BAR) | Transición tras recuperación media · desvío | Recuperación en el medio tras una ocasión del Villa → Fermín conduce y la da → remate desviado en Lindelöf | **Parcial** (ninguna transición escrita para el Barça; sí «pase interior de Fermín») | misma |
| 6 | Barcelona–Aston Villa | 64' | Raphinha (BAR) | Ataque elaborado · pase interior | Cancelo conduce desde la izquierda → pase de exterior al área chica → Raphinha empuja | **Sí** («Cancelo al segundo palo para Fermín y Raphinha») | misma |
| 7 | Atlético–Bayern | 54' | Karl (BAY) | Error en la salida bajo presión | Despeje lento de Le Normand → Karl se la roba → vaselina sobre Oblak | **Sí** («error en la salida bajo presión del Atlético: Pubill y Le Normand recibiendo») | https://www.bundesliga.com/en/bundesliga/news/club-atletico-de-madrid-bayern-munich-match-report-highlights-matchday-4-39870 |
| 8 | Atlético–Bayern | 74' | Laimer (BAY) | Ataque elaborado · pase interior | Tras un remate de Upamecano al travesaño → Kane habilita a Laimer en el área → remate | **Sí** («Kane bajando al bolsillo para la llegada de…») | misma |
| 9 | Fenerbahçe–Liverpool | 25' | Nyoni (LIV) | Rebote o segunda jugada en el área · desvío | Envío profundo de Szoboszlai a Van Dijk, despejado → balón suelto en el área → remate de Nyoni, desviado | **Parcial** (segunda jugada escrita para Mac Allister) | https://www.liverpoolfc.com/news/liverpool-fenerbahce-champions-league-match-report |
| 10 | Fenerbahçe–Liverpool | 29' | Greenwood (FEN) | Tiro libre directo · desvío | Falta a unos 20 metros → remate flojo → se desvía en Jacquet, en la barrera | **Sí** («tiro libre directo de Greenwood») | misma y https://www.flashscore.com/news/soccer-champions-league-impressive-fenerbahce-stun-liverpool-in-five-goal-champions-league-thriller/GW2NbAcK/ |
| 11 | Fenerbahçe–Liverpool | 69' | Isak (LIV, banco) | Ataque elaborado · centro lateral | Gakpo (recién entrado) por la izquierda → centro → Isak de cabeza en el área chica, primer toque | **Sí** (banco: Isak y Gakpo; aérea por centro) | misma |
| 12 | Fenerbahçe–Liverpool | 73' | A. Brown (FEN) | Segunda jugada de córner | Córner en corto → centro de Kanté que Liverpool no despeja (peinada de Gakpo) → Brown solo al segundo palo | **Parcial** (córner al primer palo y segunda jugada de Yüksek; el lateral al segundo palo, no) | misma |
| 13 | Fenerbahçe–Liverpool | 79' | Muriqi (FEN, banco) | Lateral (corto y envío al área) | Saque de banda corto → balón largo al área → Muriqi le gana a Jacquet, cabezazo al rincón | **Parcial** («Muriqi del banco por alto» sí; el lateral, no) | misma |
| 14 | Leipzig–City | 37' | Lukeba, en contra (para el City) | Autogol | Pase atrás de O'Reilly desde la banda → Lukeba intenta despejar → a su arco | **Parcial** (escrito el centro atrás de Ndiaye, no el de O'Reilly) | https://www.101greatgoals.com/football/champions-league/rb-leipzig-man-city-haaland/ |
| 15 | Leipzig–City | 49' | Baku (RBL) | Error del arquero | Baku lanzado por la derecha → se cierra a un ángulo estrecho → Donnarumma la deja pasar por su palo | **No** (del arquero se escribió solo el pase) | misma |
| 16 | Leipzig–City | 58' | E. Fernández (MCI) | Ataque elaborado · centro lateral | Centro de Ndiaye desde la izquierda → Fernández llega → cabezazo | **Sí** («centros de Ndiaye…» y la segunda línea de Fernández) | misma |
| 17 | Leipzig–City | 61' | Nusa (RBL) | Balón largo a la espalda | Pase elevado de Nkunku (recién entrado) → Nusa solo contra Donnarumma → remate raso al rincón | **Parcial** (Nkunku en el banco; la espalda, no) | misma |
| 18 | Leipzig–City | 78' | Haaland (MCI) | Ataque elaborado · centro lateral | Anderson (banco) conduce por la derecha → centro → Haaland al segundo palo | **Sí** («Haaland en el área: centros…»; banco: Anderson) | misma |
| 19 | Boca–River | 27' | Di Lollo (BOC) | Córner directo | Córner de Villa desde la derecha → Di Lollo se suelta de la marca → cabezazo | **Sí** («pelota parada: Di Lollo y Herrera… córner de Villa») | https://www.contextotucuman.com/nota/427190/boca-le-gana-1-0-a-river-en-un-superclasico-caliente-expulsaron-a-martinez-quarta-y-montiel |
| 20 | Flamengo–Grêmio | 20' | Samuel Lino (FLA) | Rebote del arquero | Pase de Arrascaeta → remate de Lino, ataja Grando → Lino empuja el rebote | **Sí** («arquero suplente sin rodaje (Grando): remate y rechace») | https://www.jb.com.br/esportes/2026/11/1061459-flamengo-vence-gremio-por-3-a-1-e-amplia-lideranca-no-brasileirao.html |
| 21 | Flamengo–Grêmio | 28' | Pedro (FLA) | Ataque elaborado · desborde individual | Carrascal se va en una jugada individual → pase a Pedro → remate a la salida del arquero | **Parcial** (Carrascal escrito como llegada al segundo palo) | misma |
| 22 | Flamengo–Grêmio | 45' | Pedro (FLA) | Rebote del arquero | Centro de Varela → Grando ataja el remate de Lino → Pedro, atento al rebote | **Sí** (el rechace de Grando) | misma |
| 23 | Flamengo–Grêmio | 69' | Amuzu (GRE, banco) | Tiro libre directo | Falta → remate directo | **Parcial** (banco: Amuzu; no el tiro libre directo) | misma |
| 24 | Universitario–Sport Boys | 27' | Cueva, penal (SB) | Penal (origen sin fuente) | La fuente no dice la falta → Cueva convierte | **Sí** (ejecutor: Cueva) | https://caretas.pe/?p=842859 |
| 25 | Universitario–Sport Boys | 83' | Liza (SB, banco) | Transición | Contra del Sport Boys → Liza define | **Sí** (banco: Liza; transición) | https://www.americatv.com.pe/deportes/futbol-peruano/universitario-reacciono-y-empato-2-2-sport-boys-seguir-lucha-torneo-clausura-liga-1-alex-valera-cain-fara-christian-cueva-percy-liza-carlos-zambrano-n456989 |
| 26 | Universitario–Sport Boys | 88' | Valera (U) | Sin fuente | — | — | sin fuente |
| 27 | Universitario–Sport Boys | 91' | Fara (U) | Sin fuente (solo definición) | «Encontró el balón dentro del área» → taco | — | https://caretas.pe/?p=842859 |
| 28 | Atlético Grau–Universitario | 7' | A. Fernández (GRAU) | Sin fuente (solo definición) | Cabezazo, sin el centro | — | https://www.americatv.com.pe/deportes/futbol-peruano/universitario-remonto-3-1-atletico-grau-y-tomo-punta-torneo-clausura-liga-1-lapadula-polo-alzugaray-n456943 |
| 29 | Atlético Grau–Universitario | 18' | Polo (U) | Ataque elaborado · desborde individual | Jugada de Polo por la derecha → remate | **Parcial** (Polo escrito como centrador) | misma |
| 30 | Atlético Grau–Universitario | 69' | Lapadula (U) | Sin fuente | — | — | sin fuente |
| 31 | Atlético Grau–Universitario | 76' | Alzugaray (U, banco) | Sin fuente | — | — | sin fuente |
| 32 | Alianza Lima–Cienciano | 72' | E. Castillo (ALI) | Rebote o segunda jugada en el área | Quevedo llega por la derecha y remata en el área → rebote del despeje → Castillo de cabeza | **Parcial** (banco: Quevedo; el rebote no) | https://www.exitosanoticias.pe/deportes/alianza-lima-impone-minima-cienciano-gol-eryc-castillo-aun-suena-clausura-n187499 |
| 33 | Monterrey–Tijuana | 5' | Porozo (TIJ) | Córner directo | Córner desde la izquierda → Porozo libre → cabezazo | **Sí** («córners a Porozo y Bilbao») | https://www.foxsports.com.mx/2026/10/31/empate-dramatico-monterrey-y-tijuana-se-aferran-a-la-liguilla-en-partido-lleno-de-golazos-video/ |
| 34 | Monterrey–Tijuana | 19' | Cuypers, penal (MTY) | Penal (origen: VAR, falta sin nombrar) | Acción polémica en el área → VAR → Cuypers al centro | **No** (ejecutor escrito: Ocampos) | misma y https://planoinformativo.com/planodeportivo/345400/monterrey-y-tijuana-empatan-3-3 |
| 35 | Monterrey–Tijuana | 45' | Cuypers (MTY) | Sin fuente (solo definición) | «Gran jugada» → taco | — | misma |
| 36 | Monterrey–Tijuana | 45+4' | Preciado (TIJ) | Sin fuente (solo definición) | «Desatenciones defensivas» → cabezazo | — | misma |
| 37 | Monterrey–Tijuana | 57' | Ocampos (MTY) | Ataque elaborado · centro lateral | Balón elevado de Óliver Torres al área → chilena | **Parcial** (aérea por centro para Cuypers y los centrales; Ocampos por banda) | misma |
| 38 | Monterrey–Tijuana | 60' | Preciado (TIJ) | Transición | Contragolpe rápido → Preciado solo ante Andrada → define | **Sí** («transición: pase largo a Preciado a la espalda de Chávez») | misma |
| 39 | América–Toluca | 42' | Viñas (TOL) | Balón largo a la espalda | Pelotazo largo → le gana a Bueno → recorta y zurdazo | **No** (de Bueno se escribió la salida bajo presión) | https://www.foxsports.com.mx/2026/10/31/partidazo-america-rescato-empate-ante-el-toluca-con-agonico-gol-de-penal-y-se-mantiene-en-la-cima/ |
| 40 | América–Toluca | 62' | H. Martín (AME) | Rebote o segunda jugada en el área | Centro de Reyes → despeje fallido de García → remate de Perea que rebota → Martín | **Parcial** (centros al área de Martín; el rebote no) | misma |
| 41 | América–Toluca | 87' | Vega (TOL, banco) | Penal (rebote del penal atajado) | Jalón de Bueno a Paulinho (roja) → Malagón ataja a Vega → Vega de cabeza en el rebote | **Parcial** (Vega en el banco; ejecutores escritos: Helinho y Viñas) | misma y https://planoinformativo.com/planodeportivo/345401/america-y-toluca-protagonizan-un-vibrante-empate-2-2 |
| 42 | América–Toluca | 90+2' | H. Martín, penal (AME) | Penal (falta sobre Borja, del banco) | Falta sobre Borja → VAR → Martín convierte | **Sí** (ejecutor: Martín; banco: Borja) | misma |
| 43 | Cali–Chicó | 32' | Bacca (CAL) | Transición tras recuperación baja | Córner de Chicó → recuperación → contragolpe | **No** (ninguna transición escrita para el Cali; Bacca solo como banco) | https://www.noticiasrcn.com/deportes/deportivo-cali-se-impuso-ante-chico-pero-perdio-a-figura-para-el-clasico-vallecaucano-1077723 |
| 44 | Cali–Chicó | 79' | Dinenno (CAL) | Sin fuente | — | — | sin fuente |
| 45 | Cúcuta–Santa Fe | 62' | Berdugo (CUC) | Sin fuente | Solo «combinación entre Peralta y Berdugo» | — | https://www.winsports.co/?p=476150 |

## Tasas

**Con fuente que nombra la jugada: 36 de 45 goles** (80 %). Sin fuente: 9.
Sobre los 36:

- **Sí: 17 (47 %) · Parcial: 15 (42 %) · No: 4 (11 %).**

| Categoría | n | Sí | Parcial | No |
|---|---|---|---|---|
| Error en la salida bajo presión | 3 | 2 | 1 | 0 |
| Ataque elaborado · centro lateral | 4 | 3 | 1 | 0 |
| Ataque elaborado · pase interior | 2 | 2 | 0 | 0 |
| Ataque elaborado · desborde individual | 2 | 0 | 2 | 0 |
| Balón largo a la espalda *(nueva)* | 2 | 0 | 1 | 1 |
| Transición tras recuperación | 4 | 2 | 1 | 1 |
| Tiro de media distancia | 2 | 1 | 1 | 0 |
| Pelota parada · córner directo | 2 | 2 | 0 | 0 |
| Pelota parada · segunda jugada de córner | 1 | 0 | 1 | 0 |
| Pelota parada · tiro libre directo | 2 | 1 | 1 | 0 |
| Pelota parada · lateral | 1 | 0 | 1 | 0 |
| Penal | 4 | 2 | 1 | 1 |
| Rebote o segunda jugada en el área | 5 | 2 | 3 | 0 |
| Error del arquero | 1 | 0 | 0 | 1 |
| Autogol | 1 | 0 | 1 | 0 |
| **Total** | **36** | **17** | **15** | **4** |

Muestra chica: cada tasa por categoría es de 1 a 5 goles. Leerlo como
dirección, no como número.

### Qué se le escapa más al DTP

1. **La pelota sucia del área** —rebote del arquero o de un despeje, error del
   arquero, autogol, desvío—: **7 goles, 2 «Sí»** (los dos del Flamengo, donde
   el parte había escrito el arquero suplente). Más los 3 remates desviados
   (Raphinha, Nyoni, Greenwood). Es la clase que más pesa y la que el M2 casi
   nunca escribe: cuando la escribe (Grando), acierta.
2. **El balón largo a la espalda** (2 goles, 0 «Sí»): ninguna lista lo tenía.
   El DTP escribe la espalda del lateral «en transición», pero no el pelotazo
   del que defiende contra la línea alta (Viñas a Bueno, Nkunku a Nusa).
3. **La transición del dominante** (Barça al 52', Cali al 32'): las listas del
   favorito no traen su propia contra. La contra se escribe solo para el débil.
4. **El ejecutor del penal** (Monterrey: escrito Ocampos, pateó Cuypers;
   Toluca: escritos Helinho y Viñas, pateó Vega desde el banco). La v1.5 ya
   pide la lista de dos condicionada a quién esté en cancha: falló el «quién
   esté en cancha» y la jerarquía real del día.
5. **El origen de la pelota parada**: el córner directo se escribe bien (2 de
   2), pero el córner en corto, el lateral y el tiro libre directo del que no
   es el lanzador habitual (Amuzu) quedan a medias.

**Lo que acierta:** el error en la salida bajo presión cuando nombra la zona
(Karl–Le Normand, Havertz–Alisson), el córner directo con el rematador
nombrado, el centro lateral con el centrador nombrado, y el **banco**: en 11
goles el autor o la pieza venía del banco o el parte lo listaba como suplente
(Boga, Isak y Gakpo, Muriqi, Anderson, Nkunku, Liza, Amuzu, Alzugaray,
Quevedo, Vega, Borja), y casi siempre estaba escrito.

**Ojo con el «Sí»:** las listas de `viasGol` traen de 5 a 14 vías por lado y
casi todas repiten el mismo menú (pelota parada, centro, media distancia, error
en la salida, banco, penal). Con un menú tan ancho, cubrir la categoría es
fácil y dice poco. Lo que separa una vía útil de un menú es **la zona y el
intérprete**: los 17 «Sí» nombraban a la pieza o la zona exacta, y casi todos
los «Parcial» tenían la categoría con otro intérprete o en otra zona.

## El M4 real en los cierres

En los partidos siguientes de los mismos equipos (13 cierres que cubren 43
goles de esta muestra):

| Cierre (parte siguiente) | Goles del partido anterior | Con mecánica en el M4 | ¿Había crónica? |
|---|---|---|---|
| Liverpool en Fenerbahçe–Liverpool (1635658) | Havertz | 0 («sin crónica propia») | Sí (irishnews) |
| Arsenal en Slavia–Arsenal (1635726) | Havertz | 1, parcial (el centro de Rice, sin el error de Alisson) | Sí |
| Napoli en Porto–Napoli (1635656) | 2 | 0 («sin fuente de la jugada») | Sí, la definición |
| Bayern en Mainz–Bayern (1575217) | 2 | 0 («mecánica sin dato») | Sí (bundesliga.com), y era la vía que el propio parte había escrito |
| Leipzig en Leipzig–Augsburg (1575213) | 5 | 0 (autor y asistente) | Sí (101greatgoals) |
| City en Forest–City (1557465) | 5 | 0 | Sí |
| Fenerbahçe en Çorum–Fenerbahçe (1584459) | 5 | 0 | Sí (liverpoolfc.com) |
| Liverpool en Palace–Liverpool (1557459) | 5 | 0 | Sí |
| River en Aldosivi–River (1493227) | Di Lollo | 0 («sin fuente de la jugada») | Sí (córner de Villa) |
| Grau en Grau–Cusco (1549550) | 4 | 0 | 2 de 4, a medias |
| Universitario en U–Sport Boys (1549535) | 4 | 0 | 2 de 4, a medias |
| Tijuana en Necaxa–Tijuana (1551030) | 6 | 1 («penal») | 4 de 6 (foxsports.com.mx) |
| Chicó en Chicó–Inter de Bogotá (1549856) | 2 | 0 | 1 de 2 |

**1 de 43 goles con mecánica real en el cierre** (el de Arsenal, a medias), y
**36 de esos 43 tenían crónica en la web** al buscarla con el protocolo de
abajo. El Tijuana declaró `MECANISMO-ABIERTO · sin mecánica` sobre dos goles
cuya jugada estaba en Fox Sports México.

**En todo el archivo** (171 partes descargados, 330 bloques con partido
anterior): 973 goles en `m4Goles`; 565 sin disparador ni secuencia, 348 con
«sin fuente» o «sin crónica», y solo **~19 % con algo parecido a una mecánica**
(un disparador o una secuencia que no sea «asistencia de X»). `via`:
`juego_abierto` 636 · vacía 166 · `pelota_parada` 116 · `transicion` 52.
`juego_abierto` es el cajón por defecto: con la ficha sola no se puede saber
otra cosa.

**El problema no es que la crónica no exista: es que el cierre no la busca o
se queda con la ficha.** La ficha de la API trae autor, asistente y tipo
(`Normal Goal`, `Penalty`, `Own Goal`), nunca la jugada.

## Fuentes que sirvieron, por liga

Todas las búsquedas fueron con WebSearch (región EE. UU.) y la página se abrió
con WebFetch. **Lo que funcionó:** «[local] [marcador] [visitante] [goleadores]
[report / crónica / como foi]», y después abrir la crónica, nunca quedarse con
el resumen del buscador.

| Liga | Sirvió (con la jugada) | Solo la definición | Bloqueó (403) o no encontró |
|---|---|---|---|
| Premier / Champions (equipos ingleses) | sitio del club (liverpoolfc.com), flashscore.com/news, 101greatgoals.com, irishnews.com (PA Media) | allfootballapp | — |
| Bundesliga en Champions | bundesliga.com (match report) | — | fcbayern.com (403) |
| Serie A | livescore.com (republica Football Italia) | flashscore.es | — |
| LaLiga | (sin dato: el único partido de la muestra no estaba indexado) | — | — |
| Argentina | contextotucuman.com (córner, ejecutor, marca) | 442.perfil.com | elgrafico.com.ar y tudn.com (403) |
| Brasil | jb.com.br (los cuatro goles, en portugués: «como foi»), flashscore.com.br | oliberal | — |
| Liga MX | foxsports.com.mx (la mejor: origen y secuencia de casi todos), planoinformativo.com, record.com.mx | — | — |
| Perú | exitosanoticias.pe (la secuencia de Castillo), primicias.ec (prensa ecuatoriana para el jugador ecuatoriano) | caretas.pe, americatv.com.pe | infobae, libero, depor: no aparecieron para estos partidos |
| Colombia | noticiasrcn.com (contra tras córner) | winsports.co, occidente.co | — |

**Dificultad por liga** (goles con fuente que nombra la jugada): Europa 18 de 18
(más 7 sin indexar a menos de 48 h) · Argentina 1 de 1 · Brasil 4 de 4 · Liga
MX 6 de 10 completos y 4 con la definición sola · Perú 4 de 9 con algo, solo 2
completos · Colombia 1 de 3.

**El resumen del buscador inventa mecánica.** Dos veces el resumen dio una
jugada que ninguna página confirmó, y una vez citó mal la página: Berdugo «centro desde la derecha y
cabezazo de Peralta» (RCN, Occidente y Win Sports solo dicen «asistencia» o
«combinación»), el 2-0 de Pedro «de rebote» (el JB dice jugada individual de
Carrascal) y el córner de Villa atribuido a 442.perfil.com, que no lo dice
(era cierto: lo confirma contextotucuman.com). **La
fuente es la página abierta, citada, nunca el resumen.**

## Otros hallazgos de paso

- **Insumo equivocado:** el parte del Cúcuta–Santa Fe dice «Peralta, el otro
  [ejecutor], es baja», y Peralta jugó y dio el gol (amonestado al 60',
  asistencia al 61'). Va a la clase de quién juega y quién no
  (`docs/FALLAS.md`).
- **Penal en el rebote:** el Vega 87' figura en la ficha como un `Missed
  Penalty` y un `Normal Goal` en el mismo minuto. El cierre que cuente penales
  convertidos tiene que leer los dos.

## Límites

- **Muestra chica:** 45 goles, 36 clasificables, 15 partidos, una semana. Las
  tasas por categoría son de 1 a 5 casos.
- **Clasificó una sola persona**, sin video. Donde dos fuentes chocaban se
  siguió la página con más detalle y se dice cuál.
- **La comparación con `viasGol` es generosa**: se contó «Sí» si la vía estaba
  en cualquiera de las dos listas que miran al equipo que anotó (su `foco` o la
  `rival` del otro bloque). Con listas de hasta 14 vías, eso infla el «Sí».
- **Sesgo de liga:** Europa tiene crónica casi siempre; Perú y Colombia no. Las
  categorías de esas ligas quedan sub-representadas entre los clasificables.
- **No se midió si la vía estaba primera o última en la lista** (el orden no
  tiene significado en el parte hoy).
- **Ningún número del skill se movió.**
