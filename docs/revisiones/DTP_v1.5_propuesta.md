# Propuesta de revisión · `diagnostico-tactico` v1.4 → v1.5

**Estado:** PROPUESTA, pendiente de aprobación del usuario. Redactada el
25/10/2026 desde el dossier (`GET /analisis/cowork/revision/diagnostico-tactico`,
cohorte `c3-2026-09-23`) y las lecciones del skill
(`GET /analisis/cowork/lecciones?skill=diagnostico-tactico`). Partimos de la
v1.4 vigente (21/10), en `docs/skills/diagnostico-tactico/SKILL.md`. No se
tocó el skill, ni el código, ni el estado de ninguna lección.

## De dónde sale

- **Ventana:** solo lo posterior a la v1.4, lecciones con fecha del 21 al
  24/10/2026. Son 314 lecciones de 74 partidos; 183 son fallos o parciales
  (112 fallos y 71 parciales) y salen de 48 partidos.
- **Población:** las 183 son `ciega` + `PRE` y acreditan. Tres lecciones de
  San Antonio Bulo Bulo–Real Potosí (24/10) están en cuarentena automática,
  porque el parte no tenía DT. No cuentan y no se usan acá.
- **Ninguna pide mover un número.** Jev no marcó ninguna con
  `proponeMoverNumero`: 167 sin etiqueta y 16 en «no». La revisión vuelve a
  fijar la rúbrica, como en la v1.4.
- **Lo que se leyó:** el texto entero (`queP` y `leccion`) de los 183 fallos y
  parciales, agrupados por la regla que tocan:
  - Vías de gol de M2: 49.
  - Checklist del bloque, pregunta 6: 38.
  - MECANISMO-ABIERTO: 24.
  - M2 en dos capas / DTP-REHACER: 20.
  - Duelo por carril y rest defense: 15.
  - Regla de posesión condicional: 9.
  - Otras: 28. Son sobre todo vida útil, M1, M4 y M6.

  Además se leyeron las incidencias 525 y 526 del modo `rehacer`.
- **Sesgo de atribución, más fuerte que en la v1.4:** en **66 de los 183**
  fallos y parciales, la lección dice que la vía, el carril o la capa
  estructural del DTP **se cumplió**. Suele decirlo en voz alta: «declarada y
  cumplida», «fue literalmente la jugada», «la capa estructural
  sobrevivió». Lo que falló fue el 1X2 del lado. Así pasa en casi todo el
  grupo de vías de gol y de dos capas, y en la mitad del de carriles. Esos
  casos **confirman** la v1.4 y no piden cambiarla.

  Algunos ejemplos:
  - Lille–Galatasaray: «el 1X2 falló, el mapa no».
  - Bayern–Arsenal, Alavés–Málaga, Brest–Nice, Westerlo–Beveren y
    Valencia–Villarreal: el banco del que persigue hizo los goles.
  - Grau–ADT: el ejecutor del penal.

  Los cambios de abajo salen del resto: las lecciones que dicen qué faltó
  escribir.

## Lo que esta capa acierta (no tocar)

- **Las cuatro líneas obligatorias de vías de gol (v1.4).** Cada línea
  acertó en sus casos:
  - Banco del que persigue: Torque–Atlético-MG, Vasco–Boca, Bayern–Arsenal,
    Palmeiras–Fluminense, Alavés–Málaga, Brest–Nice,
    Nacional–Trinidense, 2 de Mayo–Recoleta, Valencia–Villarreal y
    Westerlo–Beveren.
  - Duelo aéreo con los centrales: Torque, Grau–ADT, Augsburg–Union y
    Defensor–Racing.
  - Pelota parada: Brujas–Lens, OH Leuven–Lommel y Antwerp–Charleroi.
  - Ejecutor de penales: Grau, cuando el arquero era el ejecutor.
- **Las dos capas con el once en nivel C (v1.4, punto 6).** En 17 de los 20
  cierres con DTP-REHACER sin rehacer, cayó la capa de nombres y la capa
  estructural (carril, zona, mecanismo) dio el gol o el peligro. Pasó en
  Sporting–LASK, Lille–Galatasaray, Bayern–Arsenal, Levante–Athletic,
  Tigres–León, San Luis–Querétaro, Llaneros–Cali, Toluca–Tijuana,
  Puebla–Monterrey, Rayo–Elche, Westerlo–Beveren, Coventry–Fulham y otros.
  Los tres que no encajan son Chicó–Bucaramanga (la estructural tampoco se
  sostuvo) e IdV–Universidad Católica y Juventud–Peñarol, donde la capa
  estructural no dio gol de ningún lado.
- **La vida útil 55-65 como techo (v1.4).** Se confirmó cinco veces: Nacional
  Potosí (24' y 38'), UTC (7'), Always Ready (52'), Beveren (10') y Zulte
  (37'). En Brest (61') el improvisado cedió dentro del tramo.
- **El cierre escribe el caso de la pregunta 6 (v1.4).** Ahora se escribe en
  casi todos los cierres que lo permiten: 38 lecciones lo hacen. La regla
  pasó de «se descubre a mano» a «se escribe sola». Lo que falta es
  normalizar el caso (cambio 2).
- **La clase `estructural no probado` con la alerta encendida.** Atlético-MG
  sostuvo hasta el 89 y se rompió dos veces en cuatro minutos. Westerlo y
  Forest no sostuvieron. Arsenal volvió a perder una ventaja. En los cuatro,
  la alerta fue la lectura correcta.
- **El mecanismo por zona, no por intérprete (v1.4).** Se aplicó y acertó:
  - Alavés–Málaga: pase interior entre medios y centrales, con otro central.
  - Augsburg–Union: balón aéreo al área chica, con otra línea.
  - Mainz–Bremen: centro del carrilero, uno por cada lado.
  - San Luis–Querétaro: el de pareja no viajó con Reyes de vuelta, como manda
    la regla.

## Los cambios propuestos

### 1. Quinta línea obligatoria de vías de gol: el error en la salida bajo presión

En la v1.4 quedó como **hueco declarado**, con un caso (Cagliari): «es vía de
gol de M2, no clase de bloque». En cuatro días juntó **siete casos ciegos**
más:

- **Real Potosí 3-1 Bolívar** (21/10): una línea de fondo con parejas nuevas
  salía jugando contra un local que presionaba alto. Erró en la salida al 7'.
  En M1 estaba como vulnerabilidad y no como vía, y el 1-0 salió «exactamente
  de ahí».
- **Always Ready–The Strongest** (23/10): el gol concedido salió de un robo en
  la salida propia, una vía que el M2 no listaba.
- **Alverca–Arouca** (24/10): un central dio un mal pase en la salida de tres,
  el otro central entró sobre el 9 y vino la roja al 6'. La presión tras
  pérdida del rival estaba escrita como palanca, no como vía.
- **Levante–Athletic** (21/10): el 2-0 nació de una pérdida del mediocentro en
  la construcción. La lección lo llama «segundo caso del hueco».
- **La Louvière–Zulte** (24/10): un pase del lateral izquierdo a los pies del
  rival al 37'. El improvisado se rompió «por error en la salida, no por
  desgaste».
- **Brest–Nice** (23/10): el lateral izquierdo estuvo en el origen del gol en
  contra dos partidos seguidos, con mecánicas distintas.
- **Valencia–Villarreal** (24/10): el 1-2 vino de una pérdida de Arnau
  Martínez en la salida, recién entrado.

**Propuesta:** el error en la salida bajo presión pasa a ser la **quinta
línea obligatoria** de vías de gol. Se escribe **para el rival** cuando se
cumplen las dos condiciones:

- El equipo sale jugando desde atrás. Sobre todo con línea de tres, con una
  pareja nueva o con un pivote sin rodaje.
- El rival presiona alto o tras pérdida. Esto sale de su `formaSinBalon` o de
  sus palancas del 0-25.

En esos casos se nombra la pieza que recibe bajo presión: el rol, no
necesariamente el jugador. Puede ser vía de gol **o de expulsión**, como en
Alverca. No cambia la clase del bloque.

**Tres precisiones a las cuatro líneas de la v1.4**, todas con casos ciegos:

- **Ejecutor de penales.** No va «sin dato» y se escribe **en las dos
  direcciones**. Casos:
  - Defensor–Racing (24/10): dos penales decidieron medio partido y el
    ejecutor estaba «sin dato» en los dos lados.
  - Rayo–Elche (24/10): «ejecutor sin dato» y dos penales convertidos.
  - Antwerp–Charleroi (24/10): «sin dato» y lo tiró Porozo.
  - Monagas–Puerto Cabello (24/10): el M2 de Monagas no nombró al ejecutor
    rival y el partido se decidió de penal.

  Sin fuente del partido, se escribe el ejecutor de la temporada. Solo queda
  vacío si el equipo no tiró ningún penal en el año, y entonces se dice así.
- **La pelota parada se nombra por zona.** Incluye al **lanzador de tiro
  libre directo** y la **segunda jugada tras el despeje**, no solo a los
  rematadores. Casos:
  - Llaneros–Cali (21/10): el 0-2 fue un tiro libre directo de Benedetti y la
    vía estaba escrita como córner aéreo.
  - Toluca–Tijuana (22/10): un rechace no atacado en el área.
  - Juárez–Atlante (21/10): cabeceó un carrilero, no uno de los tres centrales
    nombrados.
- **El banco ofensivo es vía de los dos lados y por rol.** Lo es también para
  el que gana o va igualado, no solo para el que persigue. Casos:
  - Vasco–Boca (21/10): Paredes gol al 88' yendo arriba.
  - Central Español–Albion (24/10): un suplente centró el 3-0.
  - 2 de Mayo–Recoleta (24/10): el gol de Recoleta lo hizo un suplente
    entrado al descanso con el partido igualado.
  - The Strongest (23/10): marcó Cueto, que no estaba entre los dos nombres.

  La línea cuenta a todos los delanteros frescos, no solo al goleador
  conocido.

**Candidato, no se aplica (un caso):** contra un bloque estructural que no se
rompe por dentro, el remate de media distancia es vía del que domina
(LDU–Macará, 24/10). Vasco–Boca encaja como mecanismo del que concede (dos
goles de fuera del área), no como vía declarada del que ataca.

**En el parte:** nada nuevo. `viasGol.rival` ya es una lista y la quinta línea
entra ahí. Opcional para el backend: dar en los insumos del DTP los
ejecutores de penal de la temporada, sacados de los eventos `Goal` con
detalle `Penalty` o `Missed Penalty` de las fichas. Es un dato de la base
(«lo que está en nuestra base se calcula») y evita el «sin dato».

### 2. El caso de la pregunta 6: uno solo, completo y con la línea que lo sostuvo

El cierre ya escribe el caso; el cambio 5 de la v1.4 funcionó. Pero cada
analista lo escribe y lo pesa distinto, y en cinco puntos lo resuelven de
forma contradictoria:

- **Con uno MÁS no prueba.** Arouca (24/10) sostuvo un 1-0 de visita del 25'
  al 90', pero con uno más desde el 6'. El analista lo dejó como «no prueba
  el bloque en igualdad», aunque la v1.4 solo dice que con uno menos cuenta.
- **El 0-0 se lee distinto en cada cierre:**
  - Juventud–Peñarol (23/10): 0-0 los 90 ante un obligado a ganar. Se anotó
    como caso.
  - Palmeiras–Fluminense (22/10): 0-0 sostenido 81' en una vuelta. Se anotó
    como «probado, confirmado».
  - IdV–Universidad Católica (23/10): «empate sin ventaja que cuidar, cuenta
    como caso parcial y no promueve».
  - Coventry–Fulham (24/10): «no prueba el bloque».
  - Los cuatro eran 0-0 contra un obligado. La diferencia real es si **el
    empate le servía** al que defendía, como en la vuelta de llave de
    Palmeiras, o si solo le servía no perder.
- **Sostuvo el arquero, no el bloque.**
  - Brest–Nice (23/10): Nice sostuvo del 83' al 90+10 «con el arquero, no con
    el bloque», con un penal atajado.
  - Flamengo–Estudiantes (23/10): Muslera.
  - El contraejemplo es Palmeiras: sostuvo con el rival en xG 0.24 y cuatro
    remates.
- **El caso es de una línea concreta.** Gimnasia de Mendoza–Platense (23/10):
  el caso nombrado (1-0 a Newell's) lo sostuvo un bloque con Antonini y
  Muñoz. El once oficial cambió la pareja y la clase «probado» no tenía que
  viajar. Es la misma regla que el MECANISMO-ABIERTO ya aplica: con media
  línea cambiada, no viaja.
- **Un caso en contra más reciente pesa más que uno a favor anterior.**
  Bayern–Arsenal (21/10): el caso de liga (Forest 0-1) no se transfirió a la
  Champions, y Arsenal volvió a perder una ventaja dos veces. Hubo cierres
  en contra en Forest, Defensor, Westerlo, Lommel y Valencia, y la regla no
  dice qué pasa si la cadena tiene casos de los dos signos.

**Propuesta, redacción de la pregunta 6:**

- (a) **La igualdad numérica es parte del caso.** Sostener con uno menos
  cuenta. Sostener con uno más **no** prueba el bloque en igualdad.
- (b) **Un 0-0 cuenta como caso solo si el empate le servía** al que
  defendía: una vuelta de llave, la clasificación o el título del rival. Si
  no le servía, es caso **parcial**: se anota y no promueve solo a
  `estructural`.
- (c) **El caso dice si sostuvo el bloque o el arquero**, con el volumen
  concedido (remates o xG) en el tramo. Si sostuvo con el arquero (penal
  atajado, atajadas decisivas), se anota y no prueba el bloque.
- (d) **El caso viaja con la línea que lo sostuvo.** Si el once de hoy cambia
  la pareja central o la mitad de la línea del caso, la 6 se responde «no» o
  «sin dato».
- (e) **Manda el caso comparable más reciente.** Si la cadena trae casos de
  los dos signos, el último en sede y competición comparables decide la 6.

**En el parte:** `cierre.casoBloque` hoy es `{sostuvo, caso, conUnoMenos}` y
necesitaría cuatro campos más:

- `conUnoMas`.
- `tipo`: `ventaja` · `empate_que_sirve` · `cero_cero`.
- `sostuvoArquero`.
- `linea`: los nombres de la pareja o la línea.

`casos_bloque` (en `backend/analisis/dtp_cowork.py`) los entregaría tal cual
a la apertura siguiente. Lo que no puede hacer el backend es decidir por sí
solo: la 6 la responde el analista. A lo sumo, el recibo podría avisar
cuando `casoP6` cita un caso con `conUnoMas`, uno de `tipo: cero_cero`, o
una línea que no está en el `xiReferencia` de hoy.

### 3. Todo perfil de la interacción se declara por estado de marcador: posesión, seguro de atrás y plan de transición

La regla de posesión condicional (v1.2) **está** en el skill, pero se aplica
como advertencia y no como pronóstico. Se escribe un porcentaje con su
contexto y después el veredicto del M2 se apoya en ese número. Nueve
lecciones lo muestran:

- **Real Potosí–Bolívar** (21/10): se importó el bloque bajo del 1-0 en El
  Alto con uno más y de visita. En casa, ante el líder, el mismo equipo
  presionó alto y ganó 3-1. También la **forma sin balón** es condicional.
- **Vasco–Boca** (21/10): «se esperó que Vasco cediera la pelota por la sede;
  recibió al 4' y terminó con 59 %».
- **Manta–Cuenca** (24/10): pasó del 46 % al 58 % y 20 remates en cuanto quedó
  perdiendo.
- **Audax–Huachipato** (23/10): declarado 44 % «con ventaja mínima», sin ir
  nunca arriba terminó con 63 %.
- **Bayern–Arsenal** (21/10): «la posesión se declara condicionada a quién
  ocupa el pivote, no a la sede». Sin el organizador fue 42 %.
- **Palmeiras–Fluminense** (22/10): en una vuelta, la posesión depende de que
  el obligado ataque de verdad. No atacó.
- **UTC–Melgar** (23/10): el volumen concedido en Cusco era del marcador y de
  la altura, no del equipo.

Lo mismo pasa con dos piezas que la v1.2 no cubre:

- **El seguro de atrás (rest defense) se declara fijo y deja de serlo cuando
  el equipo persigue.**
  - Nacional–Trinidense (24/10): «el seguro tras la pérdida se mide con los
    centrales arriba, no con el dibujo de partida».
  - Valencia–Villarreal (24/10): «el seguro fijo del parte no se sostuvo con
    el equipo persiguiendo».
  - Rayo–Elche (24/10): Ciss era el único contenedor con los laterales
    arriba y fue responsable principal en dos de los tres goles.
- **El plan de transición necesita un rival que se abra.**
  - Chicó–Bucaramanga (23/10): el FAVORABLE se apoyó en que el obligado iba
    a abrirse. Tuvo la pelota al 50 % con dos volantes de seguro y la
    transición no apareció.
  - Torque–Atlético-MG (21/10): el DESFAVORABLE sobreponderó la transición de
    un rival que lideraba la llave y cedió la pelota (31 %).
  - Palmeiras–Fluminense (22/10): el obligado no se volcó.

**Propuesta:** la regla de posesión condicional se amplía a **regla del
estado de marcador**. Posesión, forma sin balón, seguro de atrás y plan de
transición se declaran en **dos ramas**:

- **Igualado o arriba.**
- **Persiguiendo.**

Cada rama lleva la pieza que la sostiene, por ejemplo el pivote organizador
o el contenedor. El veredicto del M2 dice **en qué rama se apoya**. Si se
apoya en que el rival «se abre» o «se vuelca», esa condición se escribe como
condición, porque es lo que el cierre va a mirar. Un porcentaje suelto
sigue prohibido. Ahora también lo está un porcentaje único con el contexto
al lado.

**En el parte:** dos cambios.

- `m2.posesion` pasa de `{valor, contraQuien, marcador, sede}` a dos ramas
  (`igualadoOArriba` y `persiguiendo`).
- `m2.restDefense` suma `nivelFocoPersiguiendo` y `nivelRivalPersiguiendo`,
  con los mismos valores fijo · depende · sin.

**Ojo con la herencia al TDE:** hoy el nivel del seguro da el SOB2 del TDE
directo. La sobreexposición del TDE es justamente la del que no repliega
buscando el gol, así que lo natural es que el SOB2 herede la **rama
persiguiendo**. Eso toca `herencia_tde` y un número calibrado del TDE (la
escala 0 · 0.5 · 1 no cambia, sí de qué rama sale). **Se deja como pregunta
para el usuario**, no como parte de esta propuesta. Sin esa decisión, el SOB2
sigue heredando el nivel de hoy.

### 4. MECANISMO-ABIERTO: con mecánica nombrada es vía principal, y el de transición viaja condicional al régimen

La v1.4 (zona o rol) funciona. Dos lecciones piden afinar **qué estatus** tiene
el mecanismo cuando viaja, y una tercera, **cuándo no viaja**:

- **Alavés–Málaga** (23/10): el mecanismo abierto por dentro del Alavés (pase
  interior entre medios y centrales, ya visto en Vigo) volvió a dar el gol con
  otro intérprete. La lección dice que «debe ir como vía principal del rival,
  no como vía a verificar». La v1.4 deja «vía a verificar» solo para el `sin
  mecánica`, pero no dice el estatus del que tiene mecánica. Del lado del
  Málaga, heredar el mecanismo como vía propia acertó el gol.
- **Tigres–León** (21/10): el mecanismo abierto ante América (transición a la
  espalda del pivote único) **no viajó**. Cambió el rol (doble pivote desde
  el 64') y León replegó en vez de perseguir. La lección dice: «un mecanismo
  de pivote único no se arrastra cuando el rival no obliga a perseguir».
- Los mecanismos de **transición con el equipo volcado** que se activaron en
  la ventana:
  - Sporting–LASK (21/10): 63' y 68'.
  - Toluca–Tijuana (22/10): segundo partido seguido.
  - OH Leuven–Lommel (24/10): 65' y 67'.
  - La Louvière–Zulte (24/10): pérdida con el bloque adelantado.

  Todos nacen de un estado de marcador, el de perseguir o volcarse.
- **Brest–Nice** (23/10): el rol (lateral izquierdo) repite en el origen del
  gol con mecánicas distintas. No activa MECANISMO-ABIERTO, pero el analista
  lo quería llevar al M2. Encaja en el cambio 1 si es de salida, o como vía
  de rol.

**Propuesta:**

- (a) **MECANISMO-ABIERTO con mecánica nombrada** (y zona o pareja que se
  repite) entra al M2 del próximo rival como **vía declarada**, en la lista
  principal. `sin mecánica` sigue como vía a verificar, nivel C.
- (b) **Un mecanismo de transición o de pérdida con el equipo volcado viaja
  condicional al régimen.** Se escribe en la rama «persiguiendo» del cambio 3
  y se juzga solo si el equipo tuvo que perseguir. Si el partido no lo puso a
  perseguir, el cierre lo anota como **no puesto a prueba**, ni confirmado ni
  cerrado (Juventud–Peñarol y Gladbach son los ejemplos de «a medias»).
- (c) Sin cambios en el umbral (≥ 2 goles, ≤ 15 minutos o sin corrección) ni
  en el de intérpretes de pareja (80 %).

**En el parte:** `cierre.mecanismoAbierto` suma `regimen`, con los valores
`cualquiera` · `persiguiendo`. El backend puede llevarlo a los insumos del
rival siguiente junto con el candidato que ya calcula.

### 5. Los dos carriles de cada lado en las dos direcciones, también el «parejo»

La regla de la v1.4 se aplicó al carril con mismatch y **acertó cuando se
escribió**. Casos:

- Brujas–Lens (21/10): «el mismatch escrito en las dos direcciones fue el
  partido».
- Stuttgart–Gladbach (23/10): «la cara de vuelta fue literalmente el
  partido».
- Ipswich–Forest (23/10), Audax–Huachipato (23/10), Manta–Cuenca (24/10) y
  Coventry–Fulham (24/10): la vuelta escrita fue la jugada del gol.

Los fallos son del carril que **no** se escribió:

- **Sporting–LASK** (21/10): el carril que el M2 dio por parejo (Araújo +
  Irankunda) fue el del 1-1. Se cargó la ida del carril derecho y no se
  escribió la vuelta del izquierdo.
- **Lille–Galatasaray** (21/10): la vuelta del **otro** carril, con un extremo
  de origen puesto de lateral, dio el centro del 2-2.
- **Levante–Athletic** (21/10): el carril que el visitante cargaba fue por
  donde concedió el 1-0. Un mismatch a favor sin su vuelta, como antes de la
  v1.4.
- **Palmeiras–Fluminense** (22/10): el carril izquierdo se escribió solo a
  favor y el gol llegó por ahí.

**Propuesta:** el mapa de duelos cubre **los dos carriles de cada equipo**,
cada uno con ida y vuelta, aunque no haya mismatch. Un carril «parejo»
también tiene espalda. Si un carril no tiene nada que decir, se escribe
«parejo» con su vuelta y el seguro que la cubre. Un carril omitido es un
carril que el cierre no puede juzgar. Peñarol (23/10) es el contraste: la
vuelta escrita nunca se atacó, y eso es dato, no fallo.

**En el parte:** nada nuevo en la forma (`duelosCarril[].vuelta` ya existe).
Hay dos avisos posibles en el recibo, sin rechazo:

- Uno, cuando hay menos de dos carriles de banda por bloque.
- Otro, cuando un duelo tiene `mismatch` y la `vuelta` vacía.

### 6. Lo que el M2 nombra se compara con el once: el XI de referencia como lista y las piezas del mapa

Las dos capas funcionan (ver «Lo que acierta»). Lo que falla es **cuándo se
avisa** que la capa de nombres cayó, y eso depende de lo que la apertura deja
escrito:

- **`xiReferencia` vacío o en prosa, por eso no hubo DTP-REHACER:**
  - Alavés–Málaga (23/10): «el XI probable en prosa y el xiReferencia vacío:
    el once oficial no se pudo comparar».
  - Köln–Schalke (24/10): «el duelo era contra Gantenbein y jugó Dina Ebimbe;
    con xiReferencia vacío no hubo DTP-REHACER que lo avisara».
  - Valencia–Villarreal (24/10): el Villarreal sin xiReferencia y con Cardona
    titular cuando no lo fue.

  La v1.4 ya dice «lista de nombres, nunca frase». Se incumple y el backend
  solo da un aviso de tipo `dato` (`DTP-SIN-REFERENCIA`).
- **La rotación anunciada no se trasladó al mapa.** La Louvière–Zulte
  (24/10): M6 escribió «Brujas en 6 días: posible gestión» y el DT rotó
  cuatro titulares fijos y el arquero. M1 y M2 se apoyaron en el núcleo que
  no jugó.
- **Incidencia 525** (modo rehacer, 24/10, cuatro partidos):
  - En Chapecoense–Fluminense se rehízo el bloque de Fluminense. El de
    Chapecoense quedó sin rehacer: su `xiReferencia` estaba vacío (solo dio
    `DTP-SIN-REFERENCIA`) y salió en 4-2-3-1 con Bolasie en vez del 4-3-3.
    Para el backend, ese cambio es la misma «forma», a propósito.
  - En Tottenham hubo dos ausentes de la referencia (el corte es 3) y Solanke,
    nombrado en el M2, arrancó en el banco.

**Propuesta:**

- (a) **El `xiReferencia` es obligatorio** en los dos bloques, como lista de
  11. Sin previa que lo dé, va **el último once oficial**, dicho así en
  `senalXi`. Es lo que en la práctica se usa como referencia, y deja
  comparar.
- (b) **El M2 declara sus piezas.** Son los jugadores, propios y rivales, de
  los que depende la capa de nombres: los duelos con nombre, el contenedor
  del seguro y el ejecutor de penales. Si una pieza arranca en el banco, la
  capa de nombres cae, aunque el corte de ausentes no se alcance.
- (c) **Con M6 marcando rotación posible** (un partido de eliminación o de copa
  a ≤ 6 días, la gestión anunciada), la capa de nombres se escribe en dos
  versiones (con el núcleo y con la rotación) o no se escribe y queda solo la
  estructural.

**En el parte y en el backend:** `m2.piezas` sería una lista de nombres,
cada uno con su lado. `rehacer()` la cruzaría con el once oficial de los
dos equipos, como hoy hace con `restDefense.foco`. Así se resuelve el caso
Solanke de la 525 sin bajar `REHACER_AUSENTES` de 3 a 2. Además, un
`xiReferencia` vacío pasaría a ser un **rechazo con motivo** al depositar la
apertura, no un aviso al leer.

## Las dos incidencias del modo rehacer: ¿skill o backend?

- **526: backend, y ya está resuelta** (PR #222, 25/10). `contraElOnce` leía
  «sin Lynen» en el seguro de Werder Bremen como «se apoya en Lynen» y daba
  DTP-REHACER falso. Le pasó cuatro veces, entre ellas a Mainz–Bremen. El
  arreglo es `dtp_cowork.sin_ausentes`, que quita del texto del seguro los
  nombres que van detrás de «sin», «ausente» y «baja de». El texto del
  analista era correcto. **No pide nada al skill.**
- **525: mitad y mitad.**
  - **La parte del skill** es el cambio 6. El bloque de Chapecoense no tenía
    `xiReferencia`, y ninguna regla del backend puede comparar un once contra
    nada. Con las piezas del M2 declaradas, el caso Solanke se marca solo.
  - **La parte del backend** sigue en `usuario` y es una decisión pendiente:
    bajar el corte de ausentes a 2, o marcar el bloque cuando una pieza
    nombrada en el M2 arranca en el banco. La propuesta recomienda lo
    segundo, que necesita `m2.piezas`.
  - **El modo `rehacer` de `corrida-sad`** (no este skill) podría además
    mirar el bloque del rival siempre que rehace uno. Si el once de un lado
    cambió lo bastante para rehacer, el M2 del otro lado nombra a esos
    mismos jugadores como rivales.

## Lo que NO se propone

- **Ningún número:** ni la vida útil (55-65 / 80-90), ni el ≥ 80 % de las
  parejas, ni el ≥ 2 del arquero, ni el umbral de ≥ 2 goles en ≤ 15 minutos.
  Estrela–Casa Pia (24/10) confirma el del arquero: un solo error de Léo Linck
  no abre la vía.
- **El costo de rearmar la línea en un doble cambio** junta su segundo caso:
  Manta–Cuenca, donde el 0-2 llegó dos minutos después del doble cambio y lo
  hizo en contra uno de los que entraron. El primero fue Sarmiento. Sigue
  como **candidato**: con dos casos no alcanza para una regla.
- **Candidatos de un caso, sin aplicar:**
  - El remate de media distancia contra un bloque estructural (LDU–Macará).
  - La cadena de tres arqueros (Chicó–Bucaramanga: entró el tercero y el gol
    llegó a los cinco minutos).
  - El rol reasignado con carga de tarjetas (Grau–ADT).
  - «Pocos minutos compartidos no es pérdida en el medio por defecto»
    (Antwerp–Charleroi). Es un contrapunto de M1, a mirar con más casos.
  - «Con tres sistemas en tres fechas, el dibujo en dos ramas»
    (2 de Mayo–Recoleta). El backend ya acepta varios sistemas en
    `m1.sistema`.
  - La cercanía de una eliminación pesa más que repetir el once en M6
    (IdV–Universidad Católica). Va en la línea del F2 del TDE.
- **La pregunta 4** se volvió a responder por las bajas en Köln–Schalke y en
  Mainz–Bremen, a pesar de la v1.4. Es incumplimiento, no hueco: el
  recordatorio va al prompt (`docs/COWORK.md`), no al skill.
- **Fulham, en Coventry–Fulham, y Juárez–Atlante:** un improvisado que no
  concede porque tiene la pelota, o que cae por pelota parada, **no puso a
  prueba** la vida útil. No es fallo de la clase. Se anota en el cierre como
  «no puesto a prueba», igual que el 4(b).

## Cómo se aplica si se aprueba

Igual que la v1.4:

1. El usuario aprueba o corrige, punto por punto. La herencia del SOB2 desde
   la rama «persiguiendo» (cambio 3) y la decisión de la 525 son preguntas
   aparte.
2. Se redacta la v1.5 en `docs/skills/diagnostico-tactico/SKILL.md`.
3. Se le da sitio en el parte a lo que lo necesita, con los tests y el
   prompt de `docs/COWORK.md`:
   - `casoBloque`: `conUnoMas`, `tipo`, `sostuvoArquero` y `linea`.
   - `posesion` y `restDefense` en dos ramas.
   - `mecanismoAbierto.regimen`.
   - `m2.piezas` y el rechazo del `xiReferencia` vacío.
   - Los avisos de carril sin vuelta.
4. Se entrega el `.zip` para subir a la cuenta.
5. Se marcan como aplicadas las lecciones correspondientes, con 🔑.
