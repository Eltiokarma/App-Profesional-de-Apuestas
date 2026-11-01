# Propuesta de revisión · `diagnostico-tactico` v1.6 → v1.7

**Estado:** PROPUESTA, pendiente de aprobación del usuario. Escrita el
01/11/2026 a partir del dossier
(`GET /analisis/cowork/revision/diagnostico-tactico`, cohorte `c3-2026-09-23`)
y de las lecciones abiertas del skill (`GET /analisis/cowork/lecciones`),
sobre la v1.6 vigente (26/10). Nada de esto está redactado en
`docs/skills/diagnostico-tactico/SKILL.md` todavía.

## De dónde sale

- **Ventana:** las **660 lecciones pendientes** del skill, todas posteriores al
  corte de la v1.6 (`lecciones.CORTE_VERSION`: 26/10). Vienen de **160
  partidos** jugados entre el 26/10 y el 01/11 y se reparten así:
  - 162 fallos;
  - 125 parciales;
  - 373 aciertos, que también son lecciones: confirman reglas.
- **Población:**
  - **584 son `ciega` + `PRE` y acreditan** (138 partidos).
  - **76 son de la Copa del Rey del 29/10** (22 partidos, población `copa`).
    Se analizan y enseñan, pero no entran a ninguna métrica: **fijan rúbrica y
    no sostienen ningún cambio**. Donde un punto se apoya en ellas, lo digo.
    Once de esas 76 tienen además cuarentena automática por DT equivocado (la
    que enseña).
  - En el dossier, el skill suma 92 casos ciegos (184 lados). El 1X2 acertó
    38 de 90 (42 %). El Brier es 0,645 y la línea de base, 0,657.
- **Ninguna lección pide mover un número.** Jev no marcó ninguna con
  `proponeMoverNumero`, y `pidenMoverSinPoder` está vacío. Igual que la v1.4,
  la v1.5 y la v1.6, esta revisión fija rúbrica. Lo que suma son **campos
  calculables**: lo que hoy se busca o se escribe a mano y ya está en la base.
- **El «lectura_efe» del modo de fallo.** `porModoFallo` del dossier etiqueta
  72 fallos, 34 como `lectura_efe` (22 de lecciones ya aplicadas y 12 de las
  pendientes). Leídas una por una, **las 12 pendientes no hablan del EFE**:
  - tres de la pregunta 6 (Tijuana 1551025, Brighton 1557454, Portuguesa
    1646923);
  - cuatro del veredicto por rama y del volumen (Kocaelispor 1584454, Göztepe
    1584451, Querétaro 1551021 y Unionistas 1644371, de copa);
  - dos de la posesión por rama (Parma 1550173, Paderborn 1575208);
  - el banco (Bologna 1550167), el MECANISMO-ABIERTO (Cúcuta 1549727) y el
    sistema del once (Estrela 1575535).

  La taxonomía cerrada de `modo_fallo.py` no tiene un casillero para la
  rúbrica del DTP, así que Jev pone ahí «una rúbrica que se aplicó mal». Las
  12 están repartidas en los puntos de abajo. Sumar el casillero es una
  decisión aparte (ver «Lo que NO se propone»).
- **Versión que leyó cada parte.** La hora de subida de la v1.6 a la cuenta no
  está en `simulacion.SUBIDA_VERSION`. Al menos un parte del 31/10 salió con
  veredicto único, sin ramas (Puerto Cabello–Táchira, 1646924, «anterior a la
  v1.6»). Lo demás se escribió con las ramas de la v1.6.
- **Fuente:** el texto entero de las 660, agrupado por la regla que tocan.
  Cada lección cuenta una sola vez, en la regla principal que cita:

  | Regla | Lecciones | Fallos | Parciales | Aciertos |
  |---|---|---|---|---|
  | Checklist del bloque (casi todo la pregunta 6) | 107 | 32 | 24 | 51 |
  | M2 · veredicto por rama | 104 | 21 | 20 | 63 |
  | Vías de gol (pelota parada, media distancia, área) | 84 | 18 | 18 | 48 |
  | M5 · volumen y conversión | 75 | 29 | 13 | 33 |
  | Banco ofensivo | 62 | 15 | 11 | 36 |
  | Ejecutor de penales | 45 | 11 | 7 | 27 |
  | M1 (sistema, xiReferencia, reasignados) | 42 | 8 | 8 | 26 |
  | MECANISMO-ABIERTO | 29 | 8 | 4 | 17 |
  | Posesión por rama | 24 | 4 | 5 | 15 |
  | M3 · costo de rearmar la línea | 14 | 4 | 1 | 9 |
  | Piezas, dos capas, rotación (M6) | 35 | 5 | 7 | 23 |
  | Duelos por carril en las dos direcciones | 23 | 6 | 1 | 16 |
  | DTP-REHACER `tardio` | 14 | 1 | 6 | 7 |
  | Otras | 2 | 0 | 0 | 2 |

### Primero, lo que ya está decidido y no se vuelve a proponer

- **Rehacer cada 20 minutos.** Desde el 31/10 la rutina de rehacer corre cada
  20 minutos (:02, :22 y :42). Al rehacer, el SOB2 y el C1 del TDE se
  reescriben con el DTP rehecho (incidencia 634). Las 14 lecciones de
  DTP-REHACER con `momento` `tardio` dicen «apertura caída por once tardío»:
  Estudiantes, Chicó, Genoa, Juventus, Atalanta, Mechelen, Standard, Milan y
  Cerro, entre otros. **No piden nada a esta capa.** Coinciden con lo de la
  v1.6: **la capa estructural sobrevivió y la de nombres cayó.** Cuentan como
  confirmación de las dos capas (v1.4).
- **`contraElOnce.rolesVsGrid` sigue en sombra** (incidencia 646). Tres
  lecciones de esta ventana leyeron mal un rol que el grid oficial daba bien:
  Tijuana 1550952, La Guaira 1646922 y Wanderers 1646899. Son casos para la
  medición de la semana, no para mover `ROLES_GRID_REHACE`. El punto 8 no lo
  toca.

## Lo que esta capa acierta (no tocar)

- **Los dos veredictos por rama (v1.6).** Hay 63 aciertos.
  - En varios partidos el veredicto de la rama jugada describió el partido y
    el único habría fallado: Medellín 1549728, Leverkusen 1575204, Genk
    1558666, San Lorenzo–Libertad 1632047, Querétaro 1551021 y Cerro 1646898.
  - La app calcula la rama jugada (`dtp.porBloque[].ramaJugada`) y la regla
    se aplicó.
- **Volumen y conversión por separado (v1.6).** Muchos «fallos» del lado son
  M2 acertados que perdió la definición o el arquero rival:
  - América 1550952: 28 remates y 7 atajadas.
  - Bayern 1575203: 3,95 de xG.
  - Inter 1550177, City 1557454, Tolima 1549837, Monterrey 1551025,
    Feyenoord 1552207, Once Caldas 1549731 y Peñarol 1646899.

  La regla evitó cargarle al mapa una varianza que no es suya.
- **El ejecutor de penales sale de la base (v1.6).** Hay 17 aciertos y varias
  confirmaciones dentro de fallos del lado:
  - Pinares (Audax, 1505537), Colman (Cusco, 1549533), Le Fée (Sunderland,
    1557451), Villarreal (Monagas, 1646925), Corulo (Real Oruro, 1645528) y
    Terrazas (Bulo Bulo, 1645529).
- **La quinta línea, el error en la salida bajo presión (v1.5):**
  - Milan–Bologna 1550167: Theate presionado.
  - Bayern–Dortmund 1575203: Nmecha.
  - Xerez 1644386 (copa): al 2'.
  - Numancia 1644364 (copa) y Tijuana–Santos 1551019: el robo de Preciado con
    otro intérprete.
- **La vuelta del carril escrita (v1.4/v1.5):**
  - Bayern 1575203: la pérdida de Kane dio el 1-1.
  - Caracas 1646925: el 1-1.
  - GO Ahead 1552211: la espalda de James.
  - Remo 1492437 y Brighton 1557454: el carril «parejo» con su vuelta.
- **«Estructural no probado» con la alerta de degradación emitida.** Fue la
  lectura correcta en Bucaramanga 1549822, Cagliari 1550168, Riestra 1493216,
  Celta 1570441, Hull 1557452, Bayern 1575203, Oriente 1645527, Tijuana
  1551025 y Bahia 1492431.
- **El techo del improvisado (v1.4):** Tigres 1551023 cayó al 42', y Vinto
  1645525 e Ipswich 1557452 cayeron dentro del 55-65.
- **La sede de la pregunta 6 (v1.6)** se cumplió como regla:
  - Libertad 1632047: el caso de local no respondía de visita, y de visita
    perdió la ventaja a los 27 minutos.
  - Nacional Potosí 1645528.
- **El área desde el lado débil y la segunda línea (v1.6):**
  - Fiorentina 1550169: el lateral contrario.
  - Sunderland 1557451: Rudoni de segunda línea.
  - Caracas 1646925: el pivote que llega.
  - Feyenoord 1552207: el lado débil.

## Los cambios propuestos

### 1. El veredicto de cada rama nombra la vía entera de esa rama, y también se escribe con diez

La v1.6 pidió dos veredictos, uno por rama, cada uno con «la vía que tendría
el foco en esa rama». Se escriben, pero la vía de la rama «persiguiendo» sale
**recortada**: centros y pelota parada, y se olvida de lo que el propio M2 ya
listaba. Pasó en 17 lecciones de fallo o parcial:

- **Göztepe 1584451:** «su vía sería la pelota parada» (DESFAVORABLE). Lo dio
  vuelta con dos delanteros del banco que el M2 tenía en la lista (76' y
  78').
- **Bologna 1550167:** DESFAVORABLE persiguiendo. Remontó con el banco que el
  propio M2 escribía como vía (Miranda, al 59').
- **Fluminense 1492435:** «su única vía son los centros y la pelota parada».
  Empató con un remate de media distancia del pivote.
- **Dortmund 1575203:** el veredicto persiguiendo dio como vía el centro al
  segundo palo. Marcó por transición tras robo: con un rival que sigue
  atacando, la transición sigue viva en esa rama.
- **Estudiantes LP 1493217:** DESFAVORABLE «solo con pelota parada y banco
  aéreo». Generó 2,03 de xG y metió tres con diez contra un bloque que
  administraba cediendo la pelota.
- **Caracas 1646925:** el FAVORABLE de igualado no contó el banco del rival,
  que no perseguía.
- **Oviedo 1644364 (copa):** NEUTRO persiguiendo con el banco de titulares
  declarado como vía. Hicieron tres en 26 minutos.

Y el reverso: cuando la rama **no tiene vía**, se escribió NEUTRO en lugar de
DESFAVORABLE:

- **GO Ahead 1552211:** 1 remate al arco en 83 minutos persiguiendo.
- **Emelec 1639856:** «el banco aéreo que entra al 68' no es vía por sí
  solo».
- **Troyes–Le Mans 1552809**, un acierto que lo dice igual.

**Regla propuesta (a).**
- El veredicto de cada rama nombra **todas** las vías que la rama tiene,
  tomadas de la lista del propio M2: el banco ofensivo, la media distancia, la
  transición si el rival sigue atacando y la pelota parada.
- Si después de eso la rama no tiene vía contra el bloque del rival, el
  veredicto es **DESFAVORABLE**, no NEUTRO.
- Un veredicto que se apoya en «la contra del rival» dice qué pasa si el que
  gana no quiere correr. Casos: San Luis 1551020 (Atlas no buscó la
  transición) y Ajax–AZ 1552210.

**Las ramas también por número (b).** Las ramas van por marcador. Una roja
temprana deja la rama jugada en otro partido, y en cinco casos el cierre no
supo qué juzgar:

- **Melgar 1549530:** roja antes del 15'. La rama igualado FAVORABLE se jugó
  90 minutos con diez y no se puso a prueba.
- **Bulo Bulo 1645529:** con diez desde el 12'. «Los dos veredictos no
  contemplan jugar con diez.»
- **Cuenca 1639830:** el FAVORABLE se apoyaba en la contra, que es la
  primera vía que se cae con diez.
- **Bucaramanga 1549822:** con diez y perdiendo, empató justo con la
  transición que el veredicto daba por perdida.
- **Medellín 1549728:** con superioridad numérica, el DESFAVORABLE
  persiguiendo se sostuvo.

Con la posesión pasa lo mismo: Gimnasia 1493218 (acierto) tuvo 47 % y no el
55-60 % de la rama arriba, porque jugó con diez desde el 57'.

- **Regla propuesta.** Cuando el M2 nombra una vía de expulsión (punto 8, o
  el reasignado con tarjetas de la v1.6), el veredicto de la rama más probable
  escribe también su línea **con uno menos**. Es el mismo arreglo que el TDE
  v0.1.23 hizo con `siExpulsion`.
- En el cierre, si la rama jugada pasó la mayor parte de sus minutos con
  diferencia numérica, su veredicto queda **no puesto a prueba**, como la
  disciplina 17 del TDE. No cuenta ni como acierto ni como fallo.
- **Calculable:** la app ya calcula la rama jugada desde los minutos de gol.
  Los minutos en inferioridad o superioridad de cada rama salen de las rojas
  de `fixture_eventos`.

**Al rehacer, también el veredicto (c).**
- **Llaneros 1549839:** rehecho con el once oficial, el veredicto por rama
  siguió nombrando la espalda de un jugador que arrancó en el banco.
- **Rubio NU 1632049:** el DESFAVORABLE se apoyaba en un bloque «rearmado»
  que el once rehecho ya había cambiado.

En el modo `rehacer`, la razón de las dos ramas se reescribe con el once, no
solo M1 y M2. Las piezas que nombran las ramas entran a `m2.piezas`.

**Un aviso barato (d), un caso.** En Gladbach–Paderborn 1575208 los dos
bloques dieron FAVORABLE a su foco en la rama «igualado o arriba». Se jugó
los 90 minutos con paridad (0,98 contra 1,04 de xG). Dos FAVORABLE en la
misma rama del mismo partido se contradicen. **Calculable:** el recibo lo
avisa (`M2-RAMAS-ESPEJO`) y no lo rechaza. Con un caso, se aprueba aparte.

### 2. M5: el volumen de la rama jugada lo trae la app, y sin stats no se juzga

La v1.6 separó el volumen de la conversión. Funcionó: 33 aciertos, y en la
mayoría de los 29 «fallos» el cierre dice «se sostiene por volumen». Quedan
tres huecos.

- **(a) El volumen se busca a mano en cada cierre**, con remates, al arco,
  xG, córners y atajadas del arquero rival, y cada subagente lo arma
  distinto. Está en `fixture_stats`.
  - **Calculable:** el objetivo del veredicto
    (`dtp.porBloque[].volumen`) trae, por bloque:
    - remates y al arco;
    - dentro y fuera del área (`Shots insidebox` y `Shots outsidebox`,
      cuando la API los da);
    - xG a favor y en contra;
    - córners;
    - atajadas del arquero rival.
  - Son números **del partido entero**: la API no los parte por tramo. Viajan
    con `cubreRama` (minutos de la rama jugada sobre 90) para que el cierre
    sepa cuánto de ese volumen es de la rama.
- **(b) Sin stats en la ficha, el volumen no se juzga.**
  - **Casos:** Metropolitanos 1646923, Puerto Cabello 1646924, Unionistas
    1644371 (copa) y Torrelavega–Ourense 1644381 (copa). En los cuatro se
    escribió «no se puede separar volumen de conversión» y el lado se cargó
    como fallo.
  - **Regla propuesta:** sin stats, el veredicto queda **no evaluable por
    volumen**, como hace la app con `sinEventos` en la rama.
  - **Calculable:** sale `sinStats` en el objetivo.
- **(c) El volumen se cuenta donde se remata, y la conversión a favor también
  va aparte.**
  - **Kocaelispor 1584454:** el FAVORABLE de la superioridad en el medio
    (3 contra 1) dio 14 remates, 10 desde fuera del área, y 0,59 de xG. Falló
    por volumen, no por conversión.
  - En la misma línea: San Luis 1551020 (11 de 22 de afuera), Ameliano
    1632046 (10 de 15) y Oriente 1645527 (11 de 16).
  - **Regla propuesta:** un veredicto FAVORABLE que se apoya en la superioridad
    en una zona dice **cómo termina en remate dentro del área**. El cierre
    mira el volumen dentro del área antes que el total.
  - Al revés, un acierto que sale por encima de lo generado **no confirma el
    veredicto**. Casos: Milan–Inter 1550177 (tres goles con 0,74 de xG),
    Brentford 1557449 (2-0 con 0,48 de xG) y Brugge 1558670.
  - Un DESFAVORABLE que se apoya en el nivel dice cuánto volumen le concede al
    débil. Caso: Kifisia 1593347, que generó 1,3 contra 0,92.

### 3. El banco ofensivo, de los dos lados, entero y por rol: la app lo lista

La regla tiene dos versiones encima: la v1.4 dijo «el banco del que persigue
es vía» y la v1.5, «de los dos lados y por rol». Aun así es la regla que más
se incumple de la ventana: **26 lecciones de fallo o parcial**.

- **Escrito solo «si persigue» y el gol llegó con el equipo ganando o
  igualado** (9 fallos):
  - Cambuur 1552211: el 4-0 con 3-0.
  - Juárez 1551021: el 3-0 con 2-0.
  - Talleres 1493216: el 2-0 con 1-0.
  - Leones del Norte 1639856: el 0-2 lo asistió un defensor que entró con
    ventaja.
  - Central Español 1646898: el gol con 1-1.
  - Instituto 1493217, UTC 1549531 y Monagas 1646925.
  - Frosinone–Lecce 1550170, un acierto: dos goles de un suplente con 3-0.
- **Nombrado por los conocidos y el gol lo hizo otro fresco** (7 fallos y 5
  parciales):
  - Peñarol 1646899: uno de los nombrados ni estaba en la hoja.
  - Fenerbahçe 1584451: nombró como banco a un titular.
  - Fortuna 1552207, Ipswich 1557452 (un pivote), Kifisia 1593347, Potosí
    1645526 (dos que entraron al 74' y al 86'), Junior 1549726 (un volante) y
    Estudiantes LP 1493217.
- **Un fijo rotado al banco es la primera pieza del banco del que gana**
  (Casa Pia–Sporting 1575531, acierto).

El incumplimiento se repite por la misma razón que el de los penales de la
v1.6: **hay que salir a armar la lista, y la lista está en la base.**

**Regla propuesta.**
- El banco ofensivo va en las vías **de todas las ramas**, no en
  «persiguiendo». Se escribe **por rol** y **con todos** los atacantes
  frescos: delanteros, extremos, mediapuntas y el volante que llega.
- Primero va el titular habitual rotado al banco.

**Calculable.**
- Los insumos del DTP traen `bancoOfensivo` por equipo: los atacantes de la
  plantilla que no están en el `xiReferencia`, con sus goles y asistencias de
  la temporada y sus minutos entrando de cambio.
- Con el once oficial, en el modo `rehacer`, son los suplentes reales de la
  hoja.
- En el parte va `m2.banco {foco, rival}`, una lista de `{nombre, rol}`. El
  recibo avisa si falta un lado (`DTP-BANCO-UN-LADO`).

### 4. El ejecutor de penales: dos nombres, cruzados con el once

La regla de la v1.6 (el ejecutor sale de la base) se confirmó sola. Lo que
falló es el caso en que **el nombrado no está en cancha cuando llega el
penal**, o en que **la base tiene un solo penal**. Son 18 lecciones de fallo
o parcial:

| Partido | Lo que se escribió | Quién pateó |
|---|---|---|
| Once Caldas 1549731 | Dayro Moreno (en el banco) | Barrios, titular |
| Aston Villa 1557447 | «quien designe Emery» (los dos de la base, en el banco) | McGinn, que lo erró al 16' |
| Rubio NU 1632049 | «sin ejecutor titular en la base» | Roldán, titular por primera vez |
| Atlético-MG 1492423 | Jorginho (salió al 75') | Carrascal |
| Monagas 1646925 | L. González (salió al 40') | Basante, que lo erró |
| Racing 1493224 (acierto) | A. Martínez (salió al 29') | I. Rodríguez |
| UTC 1549531 | Lliuya (1 de 1), en cancha | Arroyo, recién entrado |
| Cerro 1646898 | B. Morales (1 de 1), en cancha | Alemán, el 10 |
| San Lorenzo 1632047 | F. Aragón (1 de 1), en cancha | Salcedo, recién entrado |
| Parma 1550173 | 0 penales en la base | Bernabé, el lanzador de pelota parada |
| Coria 1644377 (copa) | el último que pateó, y lo había errado | Toper |

**Regla propuesta.**
- El ejecutor se escribe como **lista ordenada de dos**, condicionada a quién
  esté en cancha.
- Si el de la base no está en el once, o puede salir, va primero el titular
  que lo sigue.
- **Con un solo penal en la temporada, la base no fija al ejecutor.** Se
  nombran el de la base y el de jerarquía o el lanzador de pelota parada.
- **Sin penales en la base, va el lanzador de pelota parada**, declarado sin
  fuente.

**Calculable.**
- `penales` de los insumos ya trae a los ejecutores con convertidos y errados
  (`dtp_cowork.penales_temporada`). Le suma, por ejecutor:
  - `muestra`: cuántos tiró;
  - `ultimoErrado`;
  - con el once oficial, `enCancha` (titular o suplente).
- El recibo avisa si el primer nombre de la vía de penales está en el banco
  del once oficial (`DTP-PENAL-EJECUTOR-FUERA`). Es un aviso, no un rechazo.

### 5. La pregunta 6: el caso lo arma la app, la línea se comprueba y la 6 no mide el arranque

El checklist reúne 107 lecciones y casi todas son de la pregunta 6. **62 son
lo mismo: escribir el caso para la apertura siguiente** (v1.4: «el cierre
escribe el caso»). Se hace bien, pero cada cierre rearma a mano lo que ya
está en la ficha:
- la sede y la competición;
- si fue ventaja o empate;
- desde qué minuto y hasta cuál;
- si había uno más o uno menos;
- cuántas atajadas hizo el arquero;
- qué línea de fondo jugó.

Algunos ejemplos: Remo 1492437, Genoa 1550171, Cambuur 1552211, Aurora
1645527, Brighton 1557454, Stuttgart 1575204, Mechelen 1558666 y Leones del
Norte 1639856.

**(a) El caso se precalcula.**
- **Calculable:** los insumos del cierre traen `casoBloquePropuesto` por
  equipo, con:
  - cada tramo con ventaja o con empate, con su minuto de inicio y de fin, y
    si se sostuvo;
  - `sede` y `competicion` (la v1.6 ya las completa si faltan);
  - `conUnoMenos` y `conUnoMas`, sacados de las rojas del tramo;
  - las atajadas del arquero y el xG en contra del partido;
  - `linea`: los defensores del once oficial, por la fila del grid.
- Quedan como juicio:
  - **`tipo`**: si el empate le servía (`empate_que_sirve` o `cero_cero`)
    depende de la tabla y de la llave;
  - **`sostuvoArquero`**, que se escribe con los números a la vista.

**(b) La línea del caso se comprueba (regla (d) de la v1.5).** La regla
existe y se incumplió en seis casos:

- **Manchester City 1557454:** dado por estructural y probado con un caso de
  Dias–Guéhi. Jugó Dias–Khusanov y concedió al 11'.
- **Junior 1549726:** el caso era con Mena y J. Díaz, y ninguno de los dos
  estaba en el once.
- **Instituto 1493217:** el caso con la línea titular, y la línea de hoy
  estaba rearmada.
- **Wanderers 1646899:** la 3 y la 6 se respondieron sobre una pareja que no
  jugó.
- **Portuguesa 1646923:** la pareja sin minutos juntos.
- **Coventry 1557451:** el contraejemplo. Se respondió «con reserva» con otra
  pareja y el bloque sostuvo. No mueve la regla.

**Calculable:** el recibo compara `casoBloque.linea` con el `xiReferencia` o
con el once oficial, por `identidad.py`. Si cambió la pareja central o la
mitad de la línea y la 6 se respondió del lado estructural, avisa
`P6-OTRA-LINEA`, igual que `P6-OTRA-SEDE`.

**(c) La 6 mide sostener un resultado, no aguantar el arranque.** Hay nueve
lecciones:

- **Cúcuta 1549727:** el caso era un 1-0 protegido. Hoy había que sostener un
  0-0 ante un rival que no necesitaba la pelota, y concedió al 33'.
- **Trinidense 1632049:** estructural y probado con un 1-0 a Libertad.
  Concedió tres en 13 minutos desde el 0-0.
- **San Lorenzo 1493226:** dos goles entre el 22' y el 25'.
- **Riestra 1493216:** un gol al 25' de media distancia.

**Precisión propuesta.**
- La clase y su vida útil describen al bloque **protegiendo un resultado
  contra un obligado**.
- En la rama igualado, el riesgo del arranque se lee en las vías de gol: la
  quinta línea, el carril y la media distancia (punto 9). No se lee en la
  clase.
- Una concesión temprana con el marcador igualado no refuta la clase ni la
  confirma. El cierre la anota como **no puesta a prueba**.

**(d) Un candidato, un caso.** Instituto 1493217 no sostuvo un 3-0 con uno
más, cediendo el 74 % de la pelota. Un 1-0 once contra once no prueba
administrar una ventaja amplia cediendo la pelota. Queda como candidato.

### 6. El costo de rearmar la línea vale en cualquier tramo, y la app lo marca en el cierre

La v1.6 lo dejó en M3, tramo 65-80'+. En la ventana el rearme costó fuera de
ese tramo:

| Partido | Rearme | Gol en contra |
|---|---|---|
| Emelec 1639856 | lateral amonestado sale al 41' | 44' |
| Milan 1550167 | Tomori al descanso, el otro lateral al 58' | 60' y 62' |
| UCV Moquegua 1549527 | roja del central y triple cambio al descanso | 66', por el lateral que salió |
| Central Córdoba 1493201 (acierto) | central al 55' | 58' y 61' |
| Instituto 1493217 | triple cambio al 60', central fuera | 65' y 86' |
| Peñarol 1646899 | dos tiempos (descanso y 70') | 72' |
| Atlético-MG 1492423 | central por volante al 91' | penal al 99' |
| Villarreal–Espanyol 1570442 | doble cambio al 59' | 60', de tiro libre |

En el caso del Villarreal, la pelota parada llegó **un minuto después** del
doble cambio, con las marcas reasignadas.

Y dos en contra, que se quedan: Argentinos 1493198 (rearmó al 29' sin
conceder) y Sarmiento 1493225. Es vía, no certeza.

**Regla propuesta.**
- El costo de rearmar se escribe en el M3 como **línea transversal**, no del
  65-80'.
- Cuentan los cambios obligados y los planificados de la línea de fondo, y
  también la roja de un defensor.
- Entre las vías del rival entra **la pelota parada inmediata a un cambio
  atrás**.
- El plan del que persigue dice **quién queda atrás después de los cambios**
  (Estoril 1575532, acierto).

**Calculable (cierre).** Los insumos del cierre listan los cambios de la línea
de fondo (posición `D`/`G` del grid) y las rojas de defensores, con su minuto
y los goles en contra que siguieron, con los minutos transcurridos. **Sin
umbral:** la app no dice cuántos minutos «cuentan», lo lee el cierre. Fijar
una ventana sería un número nuevo y no hay con qué calibrarlo.

### 7. La posesión de cada rama se toma de un rival del mismo perfil

La regla de la v1.5 pide `{valor, contraQuien, marcador, sede}`. El
`contraQuien` se escribe, pero el valor se importa igual de un rival de otro
perfil. Esta vez falló **la dirección**, no solo la magnitud que la v1.6 dejó
fuera:

- **Oriente 1645527:** 35 % de igualado tomado contra The Strongest, que
  quería la pelota. Contra un visitante en cinco que cedía, tuvo 68 %. El
  FAVORABLE apoyado en «cede y sale por Flores» describió otro partido.
- **Fiorentina 1550169:** 37 % importado de San Siro contra el Inter. Contra
  una Atalanta rotada tuvo 60 % y 26 remates.
- **Lille 1552802:** 36 % de Mónaco, de visita y con diez. De local, once
  contra once, tuvo 62 %.
- **Juan Pablo II 1549536:** el 30 % ante el líder no viaja a una visita
  contra un par (53 %).
- **Paderborn 1575208:** con dos equipos que ceden, decide el perfil del
  rival, no la sede (57 %).
- **Parma–Udinese 1550173:** el visitante en 5-4-1 no cedió ante un local
  rotado en línea de cinco (58 % y 20 remates).
- **Stuttgart 1575204:** «sin el organizador la base no sale» pesa en la
  rama en que hay que salir jugando. Ganando desde el 14' cedió el 63 % y
  salió de contra.

**Regla propuesta.**
- La referencia de posesión de cada rama sale de un partido contra un rival
  del **mismo perfil de balón que el de hoy** (que quiere la pelota, que la
  cede o mixto), con la **misma cuenta de jugadores**.
- Sin esa referencia, la rama declara **solo la dirección** («más pelota que
  el rival» o «menos»), con su razón, y no un número prestado.
- La ausencia del organizador se escribe en la rama en que el equipo tiene que
  salir jugando.

**Calculable.**
- Los insumos traen `posesionReferencias` por equipo: los últimos partidos
  con posesión, la posesión media del rival en su temporada (su perfil), la
  sede y los minutos con diferencia numérica, todo desde `fixture_stats` y
  los eventos.
- En el parte, `m2.posesion.*.perfilRival` (`quiere` · `cede` · `mixto`).

### 8. M1: el once de hoy manda si ya está, y las tarjetas de toda pieza del seguro

- **(a) Con el once oficial capturado antes del depósito, el sistema sale de
  ESE grid.**
  - **Los Chankas 1549533:** el once final se capturó a las 17:32 UTC con
    cuatro defensores en la segunda fila del grid. La apertura, depositada a
    las 17:40, siguió leyendo línea de cinco con Takeuchi de carrilero.
  - **Tijuana 1550952:** el grid ponía cinco en la fila de defensa y la
    apertura escribió 4-1-4-1 por el rol habitual de un jugador.
  - **Medellín 1549728:** se apartó del último oficial por un probable de
    prensa, sin anuncio del DT, y salió el último oficial.
  - **Calculable:** `M1-VS-ULTIMO-ONCE` (v1.6) compara con el último once.
    Se suma `M1-VS-ONCE-OFICIAL`: si en `alineaciones_versiones` hay un once
    de ESTE partido con hora anterior al depósito y `m1.sistema` no coincide
    con su formación, el recibo avisa.
- **(b) El último once de otra competición, rotado, no fija la referencia de
  liga.**
  - **Mainz 1575211:** el `xiReferencia` tomó al arquero y a dos medios del
    once de copa, y la vía «error con arquero suplente» quedó sin objeto.
  - En copa: Eldense 1644343 (el sistema también va en dos variantes con
    rotación anunciada) y Peña Sport 1644366.
  - **Calculable:** los insumos traen, además del último once, el último de
    **la misma competición**, cuando el último es de otra.
- **(c) Las amarillas de toda pieza del seguro, no solo del reasignado
  (v1.6).**
  - **Kocaelispor 1584454:** el contenedor único, amonestado al 16', salió al
    63'. El lateral reconvertido, amonestado al 30'. El M1 nombró al
    reasignado sin sus amarillas.
  - **Ourense 1644381 (copa):** una pieza que venía de una roja vio la
    segunda amarilla al 88', y otra, al 47'.
  - Confirmación de la v1.6: Cuenca 1639830, el reconvertido expulsado al
    45+1.
  - **Calculable:** las amarillas en la competición ya viajan en
    `f1/{id}` (`amarillasEnLaCompeticion`, `backend/sanciones.py`). El
    DTP las toma de ahí para cada pieza de `m2.piezas`.
- **Candidato, no regla (dos casos):** el reconvertido también ataca.
  Leones del Norte 1639856: Luque, volante de lateral, se leyó solo como
  vulnerabilidad e hizo los dos goles. Peña Sport 1644366 (copa): el lateral
  juvenil señalado como mismatch a favor hizo el 1-0. Su cara ofensiva iría a
  las vías.

### 9. Vías de gol: la pelota parada con su volumen y la media distancia en las dos direcciones

- **(a) La pelota parada como vía necesita materia.**
  - **Oriente 1645527:** la vía principal (córner y tiro libre lateral contra
    una pareja nueva) tuvo 0 córners en 90 minutos.
  - **Palmeiras 1492438:** la pelota parada contra el arquero suplente, con
    3 córners en el partido.
  - **Cambuur 1552211:** el parte rebajó la vía de los centrales a «menor»
    por la fama de Cillessen por alto, sin dato. Dio dos goles.
  - **Regla propuesta:**
    - La vía de pelota parada lleva los córners esperados del cruce: los que
      saca el foco y los que concede el rival.
    - Si el cruce da pocos, la vía va como condicional.
    - Una vía declarada no se rebaja por la reputación del arquero rival.
  - **Calculable:** los córners promedio ya están en
    `ficha_tactica.promedios_avanzados` (`avanzadas.corners`, con su `n`).
    Entran a los insumos del DTP para los dos equipos.
- **(b) La media distancia va en las dos direcciones y en la rama
  persiguiendo.** La v1.6 la escribió solo para el rival de un bloque
  estructural.
  - **Fluminense 1492435:** el empate del foco fue del pivote, desde afuera.
  - **Talleres 1493216:** 7 de 8 remates de afuera contra un bloque de cinco
    que cedía. Es la vía principal del que tiene la pelota, no una
    secundaria.
  - **Pachuca 1551017:** dos goles desde la media luna.
  - Junior 1549726, Cádiz 1644386 (copa) y Getafe 1644358 (copa).
  - En aciertos: Barracas 1493200 y Técnico Universitario 1639829.
  - **Precisión propuesta:**
    - Contra un bloque bajo o de cinco que cede la pelota, la media distancia
      va **en las vías del foco** y en su rama persiguiendo, con su ejecutor.
    - Contra un bloque que presiona alto y deja el frontal, va en las del
      rival.
- **Confirma sin cambio:** el área desde el lado débil y la segunda línea
  (v1.6) en Cajamarca 1549531 (el 9 al segundo palo), Feyenoord 1552207,
  Fiorentina 1550169 y Caracas 1646925. Moreirense 1575535 (acierto) suma un
  caso: la llegada del pivote **propio** también va en las vías del foco. Ya
  lo dice la v1.6 («del interior o del pivote»).

### 10. MECANISMO-ABIERTO: la app cuenta la frecuencia, el analista nombra la jugada

La clase `sin mecánica` (v1.4) se aplicó bien en siete partidos: Cagliari
1550168, Trinidense 1632049, Fenerbahçe 1584451, Estudiantes e Instituto
1493217, Monterrey 1551025 y Tigres 1551023. Querétaro 1551021 heredó un
mecanismo que no se repitió y quedó «a verificar», que es lo correcto.

Lo que cada cierre hace a mano es **contar**: si hubo dos goles en contra a 15
minutos o menos, y si hubo una corrección entre ellos. Hoy los insumos traen
`mecanismoAbiertoCandidato` con un corte más grueso: dos o más goles
recibidos en el partido.

**Calculable.** El candidato se afina con:
- los pares de goles en contra a ≤ 15 minutos (el umbral es el del skill, no
  uno nuevo);
- los cambios de la línea de fondo o del medio entre esos goles (`correccion`:
  sí o no);
- quién asistió cada gol cuando la ficha lo trae. Un mismo asistidor en los
  dos goles ya es pista de zona: Idrissi en Tigres, Luna en Estudiantes,
  Preciado en Monterrey.

La mecánica sigue siendo juicio, y sin crónica no se fabrica.

**Dos candidatos, un caso cada uno:**
- Con MECANISMO-ABIERTO activo y la misma pieza sola, la rama igualado no sale
  FAVORABLE sin una corrección nombrada (Cúcuta 1549727).
- Los penales concedidos en serie son un mecanismo del equipo, no de la línea:
  tres en dos partidos, con dos líneas distintas (La Guaira 1646922).

## Lo que NO se propone

- **Ningún número:**
  - la vida útil (55-65 y 80-90);
  - el ≥ 80 % de intérpretes;
  - el ≥ 2 errores del arquero;
  - los ≥ 2 goles en ≤ 15 minutos;
  - el corte de ausentes de DTP-REHACER.

  San Lorenzo 1493226 sugiere que, con las preguntas 1 y 2 del lado
  improvisado, 3 de 5 del lado estructural no alcanzan para la vida útil de
  80-90. Es un caso y cambiaría el recuento del checklist: queda anotado.
- **Una ventana de minutos para el costo de rearmar** (punto 6). La app marca
  los minutos y el cierre los lee. Sin backtest no se fija.
- **La magnitud de la posesión**, como en la v1.6. El punto 7 corrige la
  referencia, no calibra el número.
- **DTP-REHACER `tardio`** (14 lecciones): ya resuelto (PR #244, rutina cada
  20 minutos desde el 31/10, incidencia 634). Dos casos son del backend y van
  como incidencia, no al skill:
  - **Fortuna Sittard 1552207:** DTP-REHACER no sonó con cuatro titulares de
    la referencia fuera.
  - **Estrela 1575535:** el cambio de 4-1-4-1 a 4-2-3-1 tumbó la capa
    estructural, porque la vulnerabilidad era el pivote único. El sistema ya
    está entre los motivos de rehacer (`sistema: la apertura dice…`). Hay que
    mirar por qué no saltó.
- **`rolesVsGrid` (646):** sigue en sombra. Tijuana, La Guaira y Wanderers
  son tres casos más para la medición de la semana.
- **La herencia del SOB2 desde la rama «persiguiendo»:** sigue siendo una
  decisión del usuario.
- **El casillero del DTP en la taxonomía de Jev.** Las 12 `lectura_efe`
  pendientes son rúbrica del DTP mal aplicada. Hay dos salidas:
  - sumar `lectura_dtp` (o, en general, `lectura_skill`) a la lista cerrada
    de `modo_fallo.py`;
  - redefinir `lectura_efe` como «rúbrica de un skill de juicio mal
    aplicada».

  Es código y toca cómo se agrupan los fallos en el dossier: lo decide el
  usuario. Esta revisión no lo necesita.
- **La rotación en copa con la liga a ≤ 3 días** (Baleares 1644343, Getafe
  1644358, SS Reyes y Coria 1644377). La regla de la v1.5 ya lo cubre: con
  rotación posible, la capa de nombres va en dos versiones. Además son copa:
  fijan rúbrica.
- **El mismatch contra un lateral suplente que nadie ataca** (Lille–Lens
  1552802) y **el mismatch no condicional que inclina la rama**
  (Cúcuta–Águilas 1549727). Un caso cada uno: quedan como candidatos.

## Lo que va al código si se aprueba

| Punto | Parte y backend | Tipo |
|---|---|---|
| 1 | `m2.veredictoRamas.conUnoMenos` (opcional); `dtp.porBloque[].minutosEnDiferencia` y «no puesto a prueba» en el objetivo; aviso `M2-RAMAS-ESPEJO` | campo nuevo + calculable + aviso |
| 2 | `dtp.porBloque[].volumen` (remates, al arco, dentro y fuera del área, xG, córners, atajadas rivales, `cubreRama`) y `sinStats` | calculable |
| 3 | `bancoOfensivo` en los insumos del DTP; `m2.banco {foco, rival}`; aviso `DTP-BANCO-UN-LADO` | insumo calculable + campo + aviso |
| 4 | `penales[].muestra`, `ultimoErrado` y `enCancha` (con el once); aviso `DTP-PENAL-EJECUTOR-FUERA` | calculable + aviso |
| 5 | `casoBloquePropuesto` en los insumos del cierre; aviso `P6-OTRA-LINEA` | calculable + aviso |
| 6 | `rearmes` en los insumos del cierre (cambios de la línea de fondo y rojas de defensores, con los goles que siguieron) | calculable |
| 7 | `posesionReferencias` en los insumos; `m2.posesion.*.perfilRival` | calculable + campo |
| 8 | aviso `M1-VS-ONCE-OFICIAL`; último once de la misma competición en los insumos; amarillas de cada pieza de `m2.piezas` desde `sanciones.py` | aviso + calculable |
| 9 | córners del cruce (`avanzadas.corners`) en los insumos del DTP | calculable |
| 10 | `mecanismoAbiertoCandidato` con pares a ≤ 15', `correccion` y asistidores | calculable |

Lo calculado se calcula al leer, como el resto de lo derivado. Ninguno de
estos campos toca el motor ni un número calibrado. El 1.(a), el 1.(c), el
5.(c) y el 9.(b) son rúbrica pura.

## Cómo se aplica si se aprueba

1. El usuario aprueba o corrige punto por punto. Se aprueban por separado:
   - 1.(d), el aviso de un solo caso;
   - 8.(b);
   - los candidatos de 5.(d), 8 y 10.
2. Se redacta la v1.7 en `docs/skills/diagnostico-tactico/SKILL.md`, con su
   entrada en el encabezado.
3. Se da sitio en el parte y en los insumos a lo de la tabla de arriba, con
   `docs/openapi.yaml`, los tipos, los tests y el prompt de `docs/COWORK.md`.
   Un aviso nuevo del recibo entra a la lista de alertas calculadas que
   `test_arquitectura` exige documentadas.
4. Se suma `("v1.7", fecha)` a `lecciones.CORTE_VERSION`. Cuando el usuario
   suba el zip, se anota la hora en `simulacion.SUBIDA_VERSION`, que hoy no
   tiene la de la v1.6.
5. Se entrega el `.zip` para subir a la cuenta.
6. Se cierran con 🔑 las anteriores a la v1.7. Ojo: las 14 de DTP-REHACER
   `tardio` no son lecciones del skill (ver «Primero»), y las 76 de copa
   cierran igual, porque fijaron rúbrica.

## Resumen: qué lecciones cierra cada punto

Cada lección cuenta una sola vez, en la regla principal que cita. «Acreditan»
son las `ciega` + `PRE` que no son de copa.

| Punto | Lecciones | Fallos | Parciales | Aciertos | Acreditan | Copa |
|---|---|---|---|---|---|---|
| 1 · Veredicto de cada rama: vía entera, con diez, al rehacer | 104 | 21 | 20 | 63 | 89 | 15 |
| 2 · M5: volumen calculado, sin stats no se juzga | 75 | 29 | 13 | 33 | 72 | 3 |
| 3 · Banco ofensivo entero, de los dos lados, listado por la app | 62 | 15 | 11 | 36 | 51 | 11 |
| 4 · Ejecutor de penales: dos nombres cruzados con el once | 45 | 11 | 7 | 27 | 42 | 3 |
| 5 · Pregunta 6: caso precalculado, línea comprobada, no mide el arranque | 107 | 32 | 24 | 51 | 101 | 6 |
| 6 · Costo de rearmar en cualquier tramo, marcado en el cierre | 14 | 4 | 1 | 9 | 14 | 0 |
| 7 · Posesión por rama desde un rival del mismo perfil | 24 | 4 | 5 | 15 | 24 | 0 |
| 8 · M1 desde el once de hoy; amarillas de toda pieza del seguro | 42 | 8 | 8 | 26 | 32 | 10 |
| 9 · Pelota parada con volumen; media distancia en las dos direcciones | 84 | 18 | 18 | 48 | 73 | 11 |
| 10 · MECANISMO-ABIERTO: frecuencia calculada | 29 | 8 | 4 | 17 | 26 | 3 |
| Confirman sin cambio (DTP-REHACER `tardio`, carriles, piezas y dos capas) | 74 | 12 | 14 | 48 | 60 | 14 |
| **Total** | **660** | **162** | **125** | **373** | **584** | **76** |

## Redactada (01/11/2026)

Aprobada entera por el usuario y redactada en
`docs/skills/diagnostico-tactico/SKILL.md` como **v1.7**: entrada en el
encabezado y los diez puntos en su módulo, con sus casos (M1: once oficial,
otra competición, amarillas de las piezas; M2: vía entera por rama, ramas por
número, rehacer y espejo, penales en lista de dos, media distancia, pelota
parada con córners, banco ofensivo; checklist: línea del caso, caso armado
con la ficha, la 6 no mide el arranque; posesión desde el mismo perfil; M3:
rearme en cualquier tramo; MECANISMO-ABIERTO: frecuencia contada; M5:
volumen dentro del área, sin stats no evaluable). Los candidatos (5.(d), el
reconvertido que ataca, los dos del punto 10, San Lorenzo, los dos mismatch)
quedan escritos como candidatos, no como regla. Ningún número se movió.

Lo que la app ya trae se cita por su nombre (`M1-VS-ULTIMO-ONCE`,
`ultimoOnceDeLiga`, `amarillasEnLaCompeticion`, `penales` con convertidos y
errados, `avanzadas.corners` en `/equipos/{id}/stats`,
`partidoAnterior.stats`, `partidoAnterior.mecanismoAbiertoCandidato`,
`dtp.porBloque[].ramaJugada`). Todo lo demás de la tabla «Lo que va al
código» va en el skill como **pendiente de la app**, sin nombre de campo ni
de alerta, hasta que exista: el skill no promete un campo que el recibo
todavía no conoce. Falta el paso 3 de «Cómo se aplica» (contrato, backend,
tipos, tests y prompt), `CORTE_VERSION` y el zip.
