# Propuesta de revisión · `diagnostico-tactico` v1.7 → v1.8

**Estado:** PROPUESTA, pendiente de aprobación del usuario. Escrita el
08/11/2026 a partir del dossier
(`GET /analisis/cowork/revision/diagnostico-tactico`, cohorte `c3-2026-09-23`,
generado el 08/11 a las 02:31) sobre la v1.7 vigente (01/11). Nada de esto
está redactado en `docs/skills/diagnostico-tactico/SKILL.md` todavía.

## De dónde sale

- **Ventana:** las **764 lecciones pendientes** del skill, de **169 partidos**
  jugados entre el 01/11 y el 07/11. Se reparten así:
  - 207 fallos;
  - 164 parciales;
  - 393 aciertos, que también son lecciones: confirman reglas.
- **Población:**
  - **736 acreditan** (`ciega` + `PRE`, sin copa ni cuarentena; 163 partidos).
  - **18 son de copa** (Copa de la División Profesional de Bolivia: Aurora
    1645454, Nacional Potosí 1645455, The Strongest–Always Ready 1645456,
    Bolívar–Real Potosí 1645457). Fijan rúbrica y **no sostienen ningún
    cambio**. Donde un punto se apoya en ellas, lo digo.
  - **10 están en cuarentena que enseña** (DT del parte distinto del que
    dirigió): Athletico-PR–Vasco 1492440 y PAOK–Asteras 1593351. No cuentan;
    fijan rúbrica.
  - En el dossier, la cohorte suma 117 casos ciegos (234 lados: 91 aciertos,
    60 parciales y 83 fallos del lado). El 1X2 acertó 61 de 117 (52 %). El
    Brier es 0,5865 y la línea de base, 0,6472. Son números de la cohorte
    entera, no de la v1.7, y **no son una tasa de acierto del skill**
    (`sesgoDeAtribucion`: quien cierra nombra el skill sobre todo cuando algo
    falla).
- **Ninguna lección pide mover un número.** Jev marcó 65 con
  `proponeMoverNumero: false` y ninguna con `true`; `pidenMoverSinPoder` está
  vacío. Como la v1.4 a la v1.7, esta revisión fija rúbrica.
- **El «lectura_efe» del modo de fallo, otra vez.** Jev etiqueta 38 de las
  pendientes como `lectura_efe` (20 fallos y 18 parciales). Ninguna nombra al
  EFE: las 38 son rúbrica del DTP mal aplicada, 16 de volumen, 11 del
  veredicto por rama, 4 de posesión y el resto del checklist, las vías, el
  carril, el rearme y el banco. Es el mismo hallazgo de la v1.7 y sigue siendo
  una decisión del usuario (ver «Lo que NO se propone»).
- **Versión que leyó cada parte.** La v1.7 entró a la cuenta el 01/11 a las
  13:00 UTC (`simulacion.SUBIDA_VERSION`). El tramo de las 04:47 de ese día
  corrió con la v1.6. Tres lecciones lo dicen solas y no se cobran como
  incumplimiento de la v1.7: Toluca 1551026, Twente 1552213 y Los Chankas
  1549542. Dos partidos del 01/11 (Estudiantes–Instituto 1493217 y
  Monterrey–Tijuana 1551025) **ya los citó la v1.7**: no cuentan como casos
  nuevos para ningún candidato.
- **Fuente:** el texto entero de las 764, agrupado por la regla que cita cada
  una (la primera que nombra en `reglaTocada`). Cada lección cuenta una sola
  vez:

  | Regla que cita | Lecciones | Fallos | Parciales | Aciertos | Partidos |
  |---|---|---|---|---|---|
  | M5 · volumen y conversión | 153 | 50 | 30 | 73 | 130 |
  | M2 · veredicto por rama (vía entera, condición, por número) | 105 | 30 | 17 | 58 | 88 |
  | Banco ofensivo | 89 | 24 | 17 | 48 | 81 |
  | Checklist del bloque (casi todo la 6) y dos capas | 87 | 24 | 18 | 45 | 79 |
  | Ejecutor de penales | 48 | 15 | 12 | 21 | 42 |
  | MECANISMO-ABIERTO | 47 | 13 | 11 | 23 | 44 |
  | M3 · costo de rearmar la línea | 45 | 14 | 8 | 23 | 43 |
  | M1 (grid, variantes, amarillas, reconvertido) | 38 | 6 | 7 | 25 | 35 |
  | Vías (segunda línea, quinta línea, lado débil) | 36 | 5 | 14 | 17 | 35 |
  | Posesión por rama | 31 | 8 | 13 | 10 | 25 |
  | Pelota parada con materia | 27 | 3 | 6 | 18 | 26 |
  | Duelos por carril | 22 | 4 | 5 | 13 | 22 |
  | DTP-REHACER y modo `rehacer` | 21 | 6 | 4 | 11 | 19 |
  | Media distancia | 6 | 1 | 2 | 3 | 6 |
  | Piezas y rotación (M6) | 5 | 2 | 0 | 3 | 5 |
  | Otras (no fabricar mecánica, señal del XI, plan 65-80) | 4 | 2 | 0 | 2 | 4 |

### Primero, el hallazgo que ordena todo lo demás

**La mayor parte de lo que se incumplió en esta ventana ya es regla de la v1.7,
y lo que la v1.7 dejó «pendiente de la app» no se construyó.** En el código de
hoy no existen `bancoOfensivo`, `casoBloquePropuesto`, `posesionReferencias`,
los minutos con diferencia numérica de cada rama, el volumen por bloque del
objetivo (`cubreRama`), los `rearmes`, los pares de MECANISMO a ≤ 15', los
córners concedidos, ni los avisos `M1-VS-ONCE-OFICIAL`, `P6-OTRA-LINEA`,
`DTP-PENAL-EJECUTOR-FUERA`, `DTP-BANCO-UN-LADO` y `M2-RAMAS-ESPEJO`. Están
anotados en `docs/revisiones/PENDIENTES.md` desde el 01/11.

Las lecciones repiten las mismas reglas de la v1.7 con otros nombres: el banco
armado de memoria, el grid leído a ojo, el caso de la 6 rearmado a mano, la
frecuencia del mecanismo contada a mano, la pelota parada sin los córners del
cruce, la posesión sin referencia del mismo perfil. Es la misma razón que la
v1.7 dio para el banco: **hay que salir a armar la lista, y la lista está en la
base.** Una regla más escrita en el skill no arregla eso. Por eso esta
propuesta tiene dos partes:

1. pocos cambios de rúbrica, los que las lecciones piden y la v1.7 no dice;
2. una sección larga «Para la app, no para el skill», que va primero en el
   orden de trabajo.

## Lo que esta capa acierta (no tocar)

- **El banco ofensivo en todas las ramas (v1.7).** Es la regla más confirmada
  de la ventana. El banco escrito para la rama del que gana o va igualado fue
  la vía del gol en Paderborn 1575220, Pachuca 1551032, Fluminense 1492449,
  Tomayapo 1645534, Liverpool–Fenerbahçe 1635658 (tres de cinco goles),
  Leipzig 1575213, Arsenal 1557457, Mainz 1575217, Dortmund–Betis 1635651,
  Porto 1635656, Cusco–Sport Boys 1549540 y Universitario–Grau 1549541, entre
  otros.
- **El ejecutor de penales en lista de dos (v1.7).** Se cumplió en Caracas
  1646933, Táchira 1646932, Standard 1558677, Universitario 1549535, Grau
  1549550, Pachuca 1551032, San Luis 1551029, Kasımpaşa 1584462 e Internacional
  1492446. La base vacía con el lanzador de pelota parada funcionó en Fortuna
  1552217.
- **Volumen y conversión por separado (v1.6/v1.7).** El cierre dejó de cargarle
  al mapa la definición y el arquero rival: Leones del Norte 1639858, PSV
  1635707, Libertad–Cerro 1632052, São Paulo 1492448, Mushuc Runa 1639831, St.
  Truiden 1558669, Cusco 1549540 y Moquegua 1549542. Y un acierto por encima de
  lo generado no se acreditó: Panathinaikos 1593349, Galatasaray 1635669,
  Marseille 1552805 y Leipzig–City 1635710.
- **El costo de rearmar en cualquier tramo (v1.7).** Con la roja de un defensor
  incluida: Kortrijk 1558657, Napoli 1550182 y Atlas 1551032. Fuera del 65-80':
  Cruzeiro 1492444 (al 5'), Santa Fe 1549845 (al 43'), Táchira 1646929 (al
  descanso) y Beveren 1558677. Los contraejemplos (Rubio Ñu 1632055, Marseille
  1552805, Alianza Lima 1549537 y Telstar 1552214) sostienen que es vía y no
  certeza.
- **`sin mecánica` y la frecuencia.** Se declaró bien, sin fabricar la jugada,
  en más de veinte cierres: Galatasaray 1584461, Aris 1593353, Augsburg 1575213,
  Sassuolo 1550187, Coventry 1557460 (con mecánica nombrada), Lens 1635681 y
  Villarreal 1635746, entre otros.
- **La 6 mide sostener un resultado (v1.7).** Pereira 1549852, San Lorenzo
  1493238, Willem II 1552216 y Bayern–Atlético 1635622: la concesión con el
  marcador igualado quedó no puesta a prueba. Y el «estructural no probado» con
  la alerta emitida leyó bien en Málaga 1570447, Sparta 1552215, Cobresal
  1505547, AEK 1635606, Roma 1635695 y Sabah 1635745.
- **Las dos capas con once tardío (v1.4).** En trece partidos la API corrigió
  la formación después del pitazo (Panetolikos 1593353, Paris FC 1552811,
  Slavia 1635726, Cerro 1632052, Kortrijk 1558657, Slovan 1635677, Huachipato
  1505551, Union 1575207, Alavés 1570450, entre otros). La capa de nombres
  cayó y la estructural sostuvo. No es del skill.
- **La quinta línea (v1.5)**, con el rol y no el intérprete: Slavia 1635726,
  Villarreal–PSG 1635746, Barcelona 1635627, Bahia 1492444 y Danubio 1646902.
- **La vuelta del carril escrita (v1.4/v1.5):** Volos 1593358, Coventry
  1557460, Vélez 1493241, Carabobo 1646931, AEK 1635606 y Cerro–Olimpia
  1632044.

## Los cambios propuestos

### 1. M5: el volumen se lee de los dos lados, y la apertura escribe dónde se remata

La v1.7 pidió que el FAVORABLE apoyado en una superioridad zonal diga «cómo
termina en remate dentro del área». **El cierre lo aplica; la apertura no.**
En trece partidos, un FAVORABLE de esa clase falló por volumen, no por
conversión:

| Partido | Lo que sostenía el FAVORABLE | Lo que dio la rama |
|---|---|---|
| Libertad–Emelec 1639859 | la transición de Branda | 9 de 14 remates de afuera, 0,64 de xG |
| Tottenham–Leeds 1557463 | la superioridad por banda | 3 remates en el área, 0,36 de xG |
| Fulham–Newcastle 1557461 | el medio contra un doble pivote rearmado | 0,70 de xG, 4 de 11 de afuera |
| Ind. Petrolero–Tomayapo 1645534 | carril y mediapuntas | 7 de 10 de afuera, 0,74 de xG |
| Inter de Bogotá–Chicó 1549856 | Sanguinetti entre líneas | 0,76 de xG y un autogol |
| Bodø–Lille 1635640 | la presión a una salida rehecha | 4 remates, 0,53 de xG |
| Trinidense–2 de Mayo 1632050 | el medio y la pelota parada | 5 de 12 en el área, 0,67 de xG |
| U. Católica–Aucas 1639802 | la superioridad con la pelota | 7 de 12 de afuera, 0,48 de xG |
| Sevilla–Getafe 1570438 | la contra de Correia y Ejuke | 0,74 de xG |
| U. de Chile–U. Católica 1505554 | que la UC se abriera | 7 de 11 de afuera, 0 al arco |
| Atlético–Bayern 1635622 | que Bayern se expusiera | 9 remates, 0,76 de xG |
| Ameliano–Guaraní 1632051 | el medio (segundo partido seguido de afuera) | 4 de 6 de afuera, 0,52 de xG |
| Guayaquil City–Libertad 1639857 | entre líneas contra un 5-4-1 | 8 en el área pero 0,65 de xG |

Y aparecen dos huecos que la v1.7 no cubre.

**(a) El veredicto se juzga por lo que la rama genera Y por lo que concede.**
Cada cierre decide a ojo si un volumen «sostiene» el veredicto, y el mismo
número se lee distinto según quién cierre. Lo que separa los casos es la
comparación con el rival, no el número propio:

- **FAVORABLE que generó y concedió igual:** Groningen 1552215 (2,18 de xG a
  favor y 2,48 en contra, «la vuelta del mismo carril se pagó»), Dortmund–
  Elversberg 1575212 (el débil sacó 1,21 y 7 al arco), HSV–Gladbach 1575218
  (2,36 contra 2,47), Göztepe 1584463 (0,90 contra 0,99), Sporting–Shakhtar
  1635723 (1,24 contra 1,97) y Genoa–Lecce 1550184.
- **DESFAVORABLE que no lo fue:** Fenerbahçe–Liverpool 1635658 (1,74 contra
  1,55).
- **NEUTRO que subestimó o sobrestimó la rama:** Pasto–Jaguares 1549847 (1,27
  contra 0,16), Millonarios 1549851 (26 remates, 1,45 contra 0,66) y Arouca–
  Famalicão 1575539 (1 remate en el área contra 5).

**Regla propuesta.**
- El cierre juzga el veredicto de la rama jugada por **la diferencia entre lo
  que el foco generó y lo que concedió**, dentro del área primero: FAVORABLE
  si generó más de lo que concedió, NEUTRO si fue parejo y DESFAVORABLE si
  generó menos. Un FAVORABLE que generó mucho y concedió lo mismo es NEUTRO
  por volumen.
- **Sin umbral:** cuánto es «parejo» lo lee el cierre con los dos números a la
  vista. Fijar una banda sería un número nuevo y no hay con qué calibrarlo.
- La apertura de un FAVORABLE apoyado en una zona escribe **quién remata
  dentro del área y desde dónde le llega la pelota**. Sin eso, la rama es
  NEUTRO.

**(b) El volumen de temporada no viaja, igual que la posesión.** Tres casos lo
importaron de otra sede o de otro perfil:
- **Paderborn–Frankfurt 1575220:** NEUTRO porque Paderborn «genera poco»
  (1,03 de xG de temporada) y generó 2,42 contra un rival que concede 1,96.
- **Espanyol–Deportivo 1570446:** DESFAVORABLE por 0,80 contra 1,72 de
  temporada, y en la rama jugada fue 0,72 contra 0,32.
- **Deportivo–Espanyol 1570446:** el 2,39 de Riazor no viajó a Cornellà
  contra una línea de tres (0,32).

**Regla propuesta:** la referencia de volumen de una rama sale de partidos en
la misma sede y contra un rival del mismo perfil de balón, como la posesión de
la v1.7. Sin esa referencia, la rama dice la dirección y no un número.

**(c) Los penales del partido se anotan al lado del xG.** El xG de la API
incluye los penales y en cinco cierres eso cambió la lectura del volumen en
juego abierto: Sevilla–Alavés 1570450 (~0,8 de 1,61 era el penal), Mirassol
1492443 (cerca de 1,5 de 2,16 eran dos penales), Manta 1639831 (1,97 con dos
penales), La Louvière 1558675 y The Strongest 1645530 (tres penales).

**Regla propuesta:** el cierre dice cuántos penales hubo y lee el volumen en
juego abierto aparte. **No se resta ningún valor fijo por penal:** sería un
número nuevo.

**Mueve un número:** no.

### 2. M2: el veredicto con condición escribe su contrario, y ceder la pelota no es señal en ninguna dirección

**(a) La vía entera de cada rama (v1.7) se sigue recortando.** Once casos con
la regla ya vigente: Telstar 1552217 (el mediapunta de la lista empató),
Riestra 1493235 (el banco de las propias vías), Belgrano 1493233 (20 remates
persiguiendo), Aucas 1639802 (el banco), Kasımpaşa 1584453 (el lateral que
llega), Köln 1575207 (el banco), Getafe 1570438 (la pareja de puntas y
Mangala), Slavia 1635726 (16 remates y 2,17 de xG «sin vía»), Shakhtar
1635723 y Stuttgart–Galatasaray 1635669. (Vasco 1492440, en cuarentena, lo
repite.) El reverso también se repite: NEUTRO para una rama sin vía en
Westerlo 1558679 (segunda apertura seguida), Aris–Levadiakos 1593348, Mónaco
1552807 y U. de Chile 1505554.

No hace falta otra regla: hace falta que se pueda comprobar. **Regla
propuesta:** la razón de cada rama **cita las vías por su renglón de
`viasGol`** (la misma lista del M2), en vez de resumirlas. Una rama que no cita
ninguna, o que solo cita la pelota parada y los centros cuando la lista tiene
banco, segunda línea o media distancia, se revisa antes de depositar. El aviso
del recibo va en «Para la app».

**(b) El veredicto con condición escribe qué pasa si no se cumple.** La v1.6 lo
pidió («si Troyes sale») y la v1.7 lo repitió para «la contra del rival». Se
incumplió en ocho partidos:

- **Libertad–Guayaquil City 1639857:** «cerrar y correr»; cerró, pero no corrió
  (0,49 de xG).
- **América–Millonarios 1549851:** el obligado se abrió (26 remates) y América
  sacó 4 remates en 90 minutos: el bloque propio quedó hundido.
- **PEC Zwolle–Willem II 1552216:** el local no salió y la rama fue NEUTRO, que
  era la condición escrita y no la elegida.
- **Rubio Ñu–Luqueño 1632055:** «un bloque improvisado que se cae», y no se
  cayó.
- **Valencia–Elche 1570437:** «si Elche no se abre, el 0-0 es su techo»; Elche
  se abrió al 68' y el gol salió de ahí.
- **U. de Chile–U. Católica 1505554** y **Atlético–Bayern 1635622:** no
  escribieron qué pasaba si el rival marcaba primero o controlaba sin abrirse.
- **Libertad–Cerro 1632052:** la vía persiguiendo dependía de que el bloque
  rival «se cae entre el 55 y el 65» (además, sobre un sistema que no jugó).

**Regla propuesta:** un veredicto de rama que se apoya en algo que tiene que
hacer el rival (abrirse, volcarse, salir, caerse) lleva **dos líneas: la de la
condición y la de su contrario**, cada una con su veredicto. Si la condición
no depende del foco, el veredicto de la rama es el de la línea menos favorable
hasta que el cierre diga cuál se jugó. En el parte, `m2.veredictoRamas.*.siNo`
(opcional).

**(c) Que el foco ceda la pelota tampoco es señal en contra.** La v1.6 dijo que
la cesión del rival no es señal a favor. Tres casos piden el espejo:
- **Emelec–Libertad 1639859:** DESFAVORABLE «contra un bloque de cinco que cede,
  poca cosa», y sacó 11 remates en el área y 2,27 de xG.
- **Leeds–Tottenham 1557463:** el 5-3-2 que cedía sacó 11 remates en el área
  contra 3.
- **Tomayapo–Petrolero 1645534:** DESFAVORABLE porque cedía, y generó más
  (1,28 contra 0,74).

Con Telstar–Utrecht 1552214 (cedió el 65 % y generó 2,49), son cuatro.

**Regla propuesta:** quién tiene la pelota no decide el veredicto en ninguna
dirección. La rama se juzga por **las vías contra el bloque y el seguro**, no
por la posesión.

**Candidato, no regla (un caso acreditable y uno de copa):** con el seguro
«sin» en la rama persiguiendo, esa rama no sale FAVORABLE sin pesar la vuelta
(The Strongest 1645456, de copa; Groningen 1552215).

**Mueve un número:** no.

### 3. Posesión: «igualado» y «arriba» se escriben aparte cuando la ventaja puede llegar temprano

La v1.5 juntó en una rama «igualado o arriba». En ocho partidos esa rama mezcló
dos estados con la posesión en sentidos opuestos: el foco marcó temprano y
cedió la pelota que la rama le daba.

| Partido | La rama decía | Arriba desde | Posesión |
|---|---|---|---|
| U. Católica–U. de Chile 1505554 | 55-60 % | 4' | 30 % |
| Stuttgart–Bremen 1575214 | más pelota | 7' | 43 % |
| Olimpia–Recoleta 1632054 | más pelota | 5' | 46 % |
| Necaxa–Tijuana 1551030 | más pelota | 12' | 42 % |
| Athletic–Real Sociedad 1570433 | más pelota | 14' | 38 % |
| Cercle–La Louvière 1558675 | más pelota | 6' | 38 % |
| ADO–Sparta 1552220 | más pelota | 22' | 43 % |
| Panathinaikos–AEK 1593349 | más pelota | 1' | 40 % |

El cierre de Olimpia ya lo había anotado en el partido anterior («30 %
ganando en La Nueva Olla»).

**Regla propuesta.**
- Cuando el foco no es favorito, o puede ponerse arriba temprano, la posesión
  de la rama se escribe en dos: **igualado** y **arriba**. Las demás piezas de
  la rama (forma sin balón, seguro, transición) siguen juntas.
- En el parte, `m2.posesion.arriba` (opcional, mismo formato).

**Dos precisiones a la regla del mismo perfil (v1.7), con sus casos:**
- **Con DT nuevo en el rival, su perfil de balón del DT anterior no vale.**
  São Paulo–Corinthians 1492448 (Seedorf, dos partidos: el rival que «tenía
  53,5 %» cedió), Rio Ave 1575527 (DT de cuatro semanas) y Cercle 1558675. Sin
  partidos con el DT de hoy, solo la dirección.
- **Un partido de copa contra un rival de otra categoría no es referencia.**
  Telstar y Utrecht 1552214 (Almere y Kozakken Boys) y PEC Zwolle 1552212
  (72 % ante el FC Oss, 34 % hoy).

Y cuando la rama queda sin referencia, va **la dirección**, nunca vacía
(Telstar y Utrecht 1552214 dejaron una rama «sin dato»).

**Mueve un número:** no. La magnitud sigue sin calibrarse.

### 4. Vías: la pelota parada del que cede va condicional, y la media distancia la escriben todos

**(a) Un equipo que cede la pelota no fabrica córners.** La regla de la v1.7
(la pelota parada necesita los córners del cruce) se confirmó y se incumplió
en la misma dirección: la vía principal fue la pelota parada de un equipo que
iba a tener poco la pelota, y no hubo materia.

| Partido | Posesión | Córners del foco |
|---|---|---|
| AEK–Real Madrid 1635606 | 30 % | 0 |
| Olimpia–Cerro 1632044 | 30 % | 0 |
| Auxerre–Strasbourg 1552808 | 36 % (5,3 de temporada) | 0 |
| Jaguares–Pasto 1549847 | cede | 0 (9 del rival) |
| Barracas–Racing 1493230 | 44 % | 1 |
| Casa Pia–Alverca 1575536 | cede | 2 |
| Arouca–Famalicão 1575539 | — | 2 (9 del rival) |
| Sporting–Shakhtar 1635723 | — | 2 (7 del rival) |

Y en sentido contrario, la materia la decide el cruce y no el promedio propio:
Bodø–Lille 1635640 (5,8 de promedio, 3 en el cruce) y Excelsior–GO Ahead
1552218 (1,2 de promedio, 7 en el cruce contra un rival que quería la pelota).
Arsenal–Slavia 1635726 y Dortmund–Betis 1635651 (2 córners cada uno) dicen lo
mismo.

**Regla propuesta:** en la rama en que el foco va a ceder la pelota, la
pelota parada va **condicional** por defecto y no como vía principal, salvo
que los córners que concede el rival digan otra cosa. El contraejemplo
(Chapecoense 1492443: dio con 2 córners) no la tumba: la vía se declara igual,
condicional.

**(b) La media distancia la escriben los dos lados, con todos sus
rematadores.** La v1.7 la puso en las vías del que tiene la pelota contra un
bloque que cede. Faltó el otro lado y faltaron nombres:
- **Torino–Lecce 1550195:** el que cedía (Lecce) remató 5 de 6 veces de afuera
  y empató así; no estaba en las vías del rival.
- **Bremen–Stuttgart 1575214:** 12 de 23 remates de afuera; estaba solo en las
  vías del rival del otro bloque.
- **Kasımpaşa–Gaziantep 1584462:** el 1-0 lo hizo de afuera un titular que la
  matriz tenía como banco; la línea nombraba a otro.
- **Tolima–Pereira 1549852:** la vía se cumplió con un mediapunta que no estaba
  en el XI de referencia.

**Regla propuesta:** la línea de media distancia va **en las vías de los dos
lados** cuando uno de los dos ataca un bloque replegado, con **todos** los
rematadores de afuera del once, no uno.

**Mueve un número:** no.

### 5. Banco ofensivo y penales: la lista sale de la hoja, sin titulares y sin minuto fijo

La regla del banco en todas las ramas funcionó (ver «Lo que acierta»). Lo que
falla ahora es **la lista**: en al menos 22 partidos el banco escrito tenía un titular,
alguien que no estaba en la hoja o le faltaba quien hizo el gol. Algunos
casos:

- **Con un titular en la lista:** Gaziantep 1584462 (Stewart y Camara),
  Mónaco 1552807 (Diop y Abline), ADO 1552212 (N. Thomas), Man United 1635695
  (Diallo), Ameliano 1632051 (Torales a la vez en el XI y en el banco), City
  1635710 y Betis 1635651 (al rehacer).
- **Con alguien fuera de la hoja:** Chicó 1549856, ADT 1549539, Boston River
  1646901, Defensor 1646900 y Pasto 1549847.
- **Le faltó el que decidió:** Köln–Union 1575207 (El Mala y Castro-Montes, los
  dos lados), Sparta 1552215 (Kostić), Lommel 1558667 (el titular del último
  once que quedó afuera), Luqueño 1632055, Samsunspor 1584449, Augsburg
  1575213, Como 1635681, Viseu 1575527, Táchira 1646929 y Always Ready 1645536.

Eso es de la app (la lista calculada de la v1.7 no existe). Lo que sí es
rúbrica:

**(a) Ningún nombre va a la vez en el XI de referencia y en el banco.** Siete
casos arriba. Con el once oficial, el banco es **la hoja**.

**(b) El banco va sin minuto fijo.** Escrito «para la última media hora» o
«65-80», entró antes y marcó: Utrecht 1552214 (Alarcón entró al 37'), Getafe
1570438 (Mangala, al descanso) y Bologna 1550194 (Orsolini, al descanso). El
M3 dice cuándo es probable, y las vías no lo condicionan a ese minuto.

**(c) Penales: la lista de dos se rehace con quién entra y con un primer
errado.** La lista de la v1.7 acertó al ejecutor en la mayoría. Fallaron dos
cosas que la regla no dice:
- **El que patea entró del banco.** Paderborn 1575220 (Pieringer al 65'),
  Charleroi 1558679 (Bojang), Bologna 1550194 (Orsolini), Porto 1635656
  (Samu, con los dos nombrados ya fuera), Manta 1639831, The Strongest 1645530
  (Lom, dos penales con el primer nombre en cancha) y Toluca 1551026 (Vega,
  con la v1.6).
- **El segundo penal del mismo partido lo patea otro tras un errado:** St.
  Truiden 1558669, La Louvière 1558675 y The Strongest 1645530.

**Regla propuesta:** la lista de dos suma **el 9 o el lanzador del banco
ofensivo** como tercer nombre condicional («si entra»), y dice quién patea
**después de un errado**. Y se cumple lo que ya dice la v1.7: **nunca vacía**.
Levadiakos 1593348 («no se afirma»), Strasbourg–Auxerre 1552808 y Parma
1550194 la dejaron sin nombre. Con dos ejecutores de muestra mínima, el orden
no está fijado y se dice así (ADT–Comerciantes 1549539, River 1493227).

**Candidato, no regla (dos casos):** el lateral o defensor fresco que llega es
banco ofensivo por rol (Başakşehir 1584463: Bulut asistió el gol decisivo;
Bolívar 1645531: Rivero, defensor que entró al 65').

**Mueve un número:** no.

### 6. M1 y `rehacer`: el grid se copia, y al rehacer también el plan

**(a) Con el once oficial a la vista, el sistema se copia de la formación de
la ficha, no se interpreta.** La regla de la v1.7 («manda su grid») se
incumplió en catorce partidos **con el grid ya capturado**. Casi siempre falló
lo mismo: pivote único contra doble pivote, o la banda de un jugador
invertida.

- **Pivote único leído donde el grid ponía dos (o al revés):** Excelsior
  1552218, Viking 1635745, PSV 1635707, Grau 1549550, Gaziantep 1584456 y
  City 1635710. (En Marseille 1552805 pasó lo mismo, pero el grid llegó
  después del depósito.)
- **Bandas invertidas:** Moreirense 1575543 (los dos bloques) y Grêmio 1492445.
- **Otro sistema entero:** Espanyol 1570446 (5-4-1 por un 3-4-1-2, con
  coordenadas de grid que no existen, 2:5 y 3:4), Tottenham 1557463, Sporting
  1635723, Belgrano 1493233, Cercle 1558664 y Guayaquil City 1639857.

**Regla propuesta.**
- El sistema es **la formación de la ficha**. El rol de cada titular sale de su
  fila del grid: dos jugadores en la fila del pivote son doble pivote, aunque
  su rol habitual diga otra cosa.
- Una coordenada que se cita tiene que existir en la ficha.
- Sin grid en la ficha, el rol del jugador contado por puestos va en las dos
  variantes hasta que el grid llegue (Guayaquil City 1639858).

La lectura del grid es calculable y va en «Para la app».

**(b) Al rehacer, también el M3 y los duelos.** La v1.7 pidió reescribir las
razones de las dos ramas. En tres partidos el plan por fases siguió con piezas
que arrancaron en el banco: Millonarios 1549851 (la presión de Castro y
Estupiñán en el 0-25'), Slovan 1635677 (Takáč al pelotazo) y Botafogo 1492441
(los duelos de carril y las palancas con Montoro, Telles, Ziyech y Martins).
Y una pieza fuera de la hoja quedó en el M2 en Atlético-MG 1492441 (Minda) y
América 1551026.

**Regla propuesta:** en el modo `rehacer` se reescribe **todo lo que nombra
piezas**: M1, M2 (duelos, vías y las dos ramas), M3 (palancas) y `m2.piezas`.
Una pieza que no está en la hoja se saca, y la vía que dependía de ella se
reescribe con quien la hereda.

**(c) Las dos variantes cuando la señal anuncia otra línea (v1.6), incumplida
en cuatro partidos.** Levadiakos 1593348 (el EFE del mismo parte anotaba «la
prensa sugiere línea de cinco» y el M1 escribió solo el 4-2-3-1: jugó 5-3-2),
Juventus 1550182 (dos previas de tres y una de cuatro: jugó la de cuatro),
São Paulo 1492448 (central suspendido) y Táchira 1646932 (la sensibilidad
anunciaba la vuelta de Pollero, que hizo un gol). **No cambia la regla:** el
recibo puede comparar la caja de sensibilidad del EFE con las variantes del M1
(ver «Para la app»).

**Mueve un número:** no.

### 7. La vía de expulsión, de los dos lados y con el historial

La v1.7 pidió las amarillas de toda pieza del seguro. Se incumplió, y en dos
casos la pieza era **propia**:
- **Málaga–Racing 1570447:** se escribió la vía de expulsión del reconvertido
  rival y no la del carrilero propio reasignado (Aznou, lateral de origen) que
  defendía a Iker Luque. Amarilla al 38', roja al 64'.
- **Frankfurt–Paderborn 1575220:** se nombró a Onyedika (4 amarillas) y el
  expulsado fue Baum, lateral derecho reasignado a la izquierda (3 en la
  temporada).

Y tres más con la pieza del seguro sin su carga:
- **River–Boca 1493214:** Martínez Quarta volvía de una suspensión. Expulsado
  al 10'; las dos ramas se jugaron con diez.
- **Gladbach–HSV 1575218:** Itakura, central del duelo central escrito. La
  segunda amarilla fue por una falta sobre ese rival.
- **Los Chankas–Moquegua 1549542:** el volante central amonestado al 34' fue
  expulsado al 81'.
- Indep. Petrolero–Aurora 1645454 (copa): la pieza del medio, expulsada
  persiguiendo a un local volcado.

**Regla propuesta.**
- La vía de expulsión se escribe **de los dos lados**. También va la pieza
  propia reasignada que corre hacia atrás contra el velocista rival.
- Una pieza que **vuelve de una suspensión** o tiene una roja reciente se nombra
  con eso.
- La rama más probable escribe su línea con uno menos (v1.7) cuando cualquiera
  de esas piezas está en el once.

**Mueve un número:** no. Las amarillas ya salen de la base
(`amarillasEnLaCompeticion` en `f1/{id}`).

### 8. M3: quién queda atrás después de los cambios, en todas las ramas, y por qué carril

La v1.7 pidió que **el plan del que persigue** diga quién queda atrás después
de los cambios. En la ventana el rearme costó también **al que ganaba o iba
igualado**, y el plan no lo decía:

- **Roma–Man United 1635695:** «cuidar piernas con ventaja», cambió a los dos
  centrales al 75'-76' y concedió al 83' y al 86'.
- **Sport Boys–Universitario 1549535:** rearmado yendo 2-0, concedió al 88' y
  al 90+1.
- **Strasbourg–Auxerre 1552808:** doble cambio al 66' con 3-0, gol al 68'.
- **Göztepe 1584463:** el plan escribía el rearme «si va arriba»; con 1-1 salió
  un carrilero al 82' y llegó el gol al 83'.
- **Sparta–ADO 1552220:** «rearmar con cuidado», sin nombres; gol al minuto
  siguiente de sacar al contenedor y gol al minuto siguiente de cambiar al
  arquero.
- Persiguiendo, sin el «quién queda atrás»: Volos 1593358, Tottenham 1557463,
  Monagas 1646928, Boston River 1646901, Progreso 1646900, Beşiktaş 1584453 y
  Atlético–Bayern 1635622.

Y en cuatro el rearme abrió **un carril entero**, porque salieron a la vez el
lateral y el de delante en la misma banda, y por ahí llegaron los goles:
Liverpool–Fenerbahçe 1635658 (Gomez y Muñoz al 66'), Nacional–Libertad
1632058 (un central y el volante del carril izquierdo al descanso), AEK–
Panathinaikos 1593349 y Santa Fe–Cúcuta 1549845.

**Regla propuesta.**
- El M3 escribe **quién queda atrás después de los cambios en todas las ramas**,
  no solo en la del que persigue.
- Un cambio que toca **el lateral y el de delante de la misma banda** se
  escribe como **costo de ese carril**, con la vía del rival por ahí.
- Sin ventana de minutos, como en la v1.7. Contraejemplos: Rubio Ñu 1632055,
  Marseille 1552805, Alianza Lima 1549537 y Telstar 1552214.

**Candidato, no regla (un caso):** «con ventaja, un cambio atrás por vez»
funcionó como palanca en Roma–Sassuolo 1550187, contra un rival de 0,3 de xG.

**Mueve un número:** no.

### 9. MECANISMO-ABIERTO: qué es una corrección y con qué reserva viaja el par

El conteo de la v1.7 se hizo a mano en las 47 lecciones del grupo y casi siempre bien. Las
lecciones piden precisar dos cosas que cada cierre resolvió distinto.

**(a) La corrección es un cambio en la zona del mecanismo.** Un cambio ofensivo
entre los dos goles no corta la frecuencia: Villarroel 1645535 («los cambios
del 55-56 fueron ofensivos»), Cusco 1549550 (lateral por delantero) y
Liverpool 1635658 (la corrección fue del otro lado). Famalicão–Braga 1575530
lo contó como corrección y Kortrijk 1558657 metió al que después hizo el
autogol.

**Regla propuesta:** cuenta como corrección el cambio de un jugador de **la
línea o la banda donde nacieron los goles**, o un cambio de sistema. Uno de
otra zona se anota y no corta.

**(b) El par viaja con su reserva.** Hay pares que se armaron en otro
partido:
- **con diferencia numérica:** Atlante 1551031, Excelsior 1552213 (con diez
  desde el 5'), Estudiantes 1493217 y Sabah 1635745;
- **con autogol o penal adentro:** Kortrijk 1558657, Chapecoense 1492443 y La
  Louvière 1558665;
- **con el partido resuelto:** Charleroi 1558665 (dos goles en dos minutos con
  4-0).

**Regla propuesta:** el mecanismo declarado lleva su reserva escrita (`con
diez`, `autogol/penal`, `resuelto`) y entra al M2 del próximo rival como vía a
verificar **con esa reserva**. No se descarta ni se le suma peso. No cambia el
umbral (≥ 2 goles en ≤ 15 minutos).

**(c) El `sin mecánica` que se repite va a la rama del rival donde se dio.**
Westerlo 1558679: la ráfaga sin corrección se repitió (tres en seis minutos en
Anderlecht, cuatro en 14 hoy) y quedó «en la matriz como gatillo
psicológico». También se repitieron Sassuolo 1550187 (tercer partido
seguido), Belgrano 1493233 (cuatro goles en dos partidos con la misma línea),
Monagas 1646932 y Vitória 1492449.

**Regla propuesta:** un `sin mecánica` visto en dos partidos seguidos entra a
las vías del rival **en la rama en que se dio** (casi siempre persiguiendo,
como el régimen de la v1.5). Sigue siendo vía a verificar y no degrada K.

**Candidato que sigue, ahora con dos casos:** que un MECANISMO-ABIERTO activo
**baje el veredicto** de esa rama (Cúcuta, de la v1.7, y Westerlo 1558679).
Con dos casos no se aprueba.

**Mueve un número:** no.

### 10. El reconvertido también ataca: pasa de candidato a regla

La v1.7 lo dejó como candidato con dos casos: Leones del Norte (Luque, volante
de lateral, hizo los dos goles) y Peña Sport (de copa). Suma el tercero:
**Telstar–Utrecht 1552214**, donde Martha, lateral de origen jugando de
mediapunta derecha, se leyó solo como centrador y vulnerabilidad, y asistió el
2-0 y marcó el 4-2.

**Regla propuesta:** el rol reasignado se escribe con **sus dos caras**: la
vulnerabilidad en M1 y, si su puesto de hoy lo pone a atacar, su llegada en las
vías del foco.

**Honestidad:** de los tres casos, dos acreditan y uno es de copa. Es rúbrica,
no un número; se aprueba aparte.

## Para la app, no para el skill

**Primero va lo pendiente de la v1.7.** Ninguno de estos campos existe. Si se
construyen, la mitad de las lecciones de esta ventana no habría hecho falta:

| Pendiente de la v1.7 | Lecciones de esta ventana que lo piden (casos) |
|---|---|
| `bancoOfensivo` en los insumos del DTP (la hoja con el once oficial) y aviso `DTP-BANCO-UN-LADO` | punto 5: al menos 22 partidos |
| `penales[].muestra`, `ultimoErrado`, `enCancha` y aviso `DTP-PENAL-EJECUTOR-FUERA` | punto 5.(c): Charleroi 1558679, Cobresal 1505547, Los Chankas 1549542 (nombrados fuera de la hoja) |
| Aviso `M1-VS-ONCE-OFICIAL` | punto 6.(a): 14 partidos |
| `casoBloquePropuesto` en los insumos del cierre y aviso `P6-OTRA-LINEA` | 35 cierres que escribieron a mano el caso de la 6 para la apertura siguiente |
| `dtp.porBloque[].volumen` (dentro y fuera del área, xG, córners, atajadas, `cubreRama`) | punto 1 |
| Minutos con diferencia numérica de cada rama (`minutosEnDiferencia`) | Atlante 1551031, La Serena 1505551, Real Oruro 1645535, Bologna 1550194, Metropolitanos 1646931 |
| `posesionReferencias` y `m2.posesion.*.perfilRival` | punto 3 |
| `rearmes` en los insumos del cierre | punto 8 |
| Pares de MECANISMO a ≤ 15', `correccion` y asistidores | punto 9 |
| Córners concedidos por cada equipo en los insumos | punto 4.(a) |
| Aviso `M2-RAMAS-ESPEJO` | — (no hubo casos nuevos) |

**Nuevo, que esta ventana pide:**

- **La lectura del grid del once oficial**, en los insumos del rehacer: la
  formación y, por titular, su fila y su banda (pivote único o doble, carriles),
  con la misma regla que ya usa `partidoAnterior.xi`. Y un aviso cuando una
  coordenada citada en `senalXi` o en el M1 no existe en la ficha (Espanyol
  1570446). Es lo que hace cumplible el punto 6.(a).
- **`veredicto` igual a la rama más probable.** En Casa Pia 1575536, Juárez
  1551029 y Cagliari 1550188 el `veredicto` de siempre no coincidía con el de
  ninguna rama, o era el de la rama menos probable. El recibo lo puede avisar.
- **Un nombre en el XI de referencia y en el banco a la vez**, aviso del recibo
  (punto 5.(a)).
- **Las vías de cada rama contra `viasGol`** (punto 2.(a)): si la razón de la
  rama no cita ningún renglón de la lista, el recibo avisa. Es un aviso, no un
  rechazo.
- **Los penales del partido al lado del xG** en el volumen del objetivo
  (punto 1.(c)), sacados de los eventos. Sin restar nada.
- **Las amarillas, la roja reciente y la vuelta de suspensión de cada pieza de
  `m2.piezas`**, en los insumos del DTP, desde `backend/sanciones.py` (punto 7).
  Hoy viajan en `f1/{id}` y el DTP no las lee.
- **La caja de sensibilidad del EFE contra las variantes del M1** (punto
  6.(c)): si el EFE del mismo parte anota otra línea y el M1 escribe una sola,
  aviso.

**Datos y pipeline (no son del skill ni de la app de juicio):**

- **La API corrige la formación después del pitazo.** Trece partidos de la
  ventana (Panetolikos 1593353, Paris FC 1552811, Slavia 1635726, Cerro 1632052,
  Kortrijk 1558657, Slovan 1635677, Huachipato 1505551, Union 1575207, Alavés
  1570450, Tomayapo 1645534, Emelec 1639859, Trinidense 1632050 y Unión–Vélez
  1493241). Ya lo cubre `momento: tardio`. Es `dato_api`.
- **Sin stats en la ficha:** la liga de Venezuela (Monagas–Caracas 1646928,
  Caracas–Puerto Cabello 1646933, Metropolitanos–Carabobo 1646931,
  Portuguesa–La Guaira 1646930) y la copa boliviana (Bolívar 1645457). La regla
  «no evaluable por volumen» se aplicó bien. Es `dato_api`.
- **Las stats son del partido entero.** Frosinone 1550188, Libertad–Cerro
  1632052 y Sevilla 1570438 lo dicen: con una rama de 52 minutos, el cierre no
  puede separar el tramo. Es la razón de `cubreRama`.
- **El xG de la API no coincide con el de la liga** (HSV–Gladbach 1575218:
  2,36 contra 2,47 en la API, 1,90 contra 1,86 en bundesliga.com). Una sola
  fuente por cierre; se anota cuál.
- **`rolesVsGrid` sigue en sombra.** La medición del 05/11 dio 9 reales y 0
  falsos (incidencia 1232, `docs/DEUDA.md` punto 20). Promover
  `ROLES_GRID_REHACE` es una decisión del usuario y no de esta revisión. En
  la ventana lo marcó en Belgrano 1493233 y City 1635710.
- **El rest defense cambia con los cambios** (Monagas–Caracas 1646928: el doble
  pivote del seguro estaba fuera al 68'). Si se mide, es del TDE (SOB2 del tramo
  final), no del DTP. Un caso.

## Lo que no cambia

- La cadena rodante, los seis módulos y el Método de Responsables.
- El checklist del bloque: las seis preguntas, el recuento de las cinco
  primeras, la 6 como llave aparte y la clase `estructural no probado`. Las
  lecciones del checklist de esta ventana son, casi todas, casos de la 6
  escritos para la apertura siguiente: confirman la v1.4-v1.7.
- La vida útil (55-65 y 80-90), el ≥ 80 % de intérpretes, el ≥ 2 errores del
  arquero, el ≥ 2 goles en ≤ 15 minutos y el corte de ausentes de DTP-REHACER.
- Los dos veredictos por rama, el banco en todas las ramas, la lista de dos del
  penal, el volumen y la conversión por separado, el rearme en cualquier tramo y
  la posesión desde el mismo perfil: se precisan, no se reemplazan.
- Las vías que ya están y se siguieron olvidando: la llegada del pivote propio
  (ABB 1645536, Casa Pia 1575536, Defensor 1646900, Rio Ave 1575527, Twente
  1552213), los centrales que atacan el área (Guayaquil City 1639858, Everton
  de Viña 1505547) y quién llega al segundo palo desde el lado débil (Santa Fe
  1549845). No piden regla nueva: son de la v1.4 y la v1.6.
- Las piezas y la rotación de la v1.5: Venezia 1550196 (Busio, tres roles y
  fuera de `m2.piezas`) y U. Católica–Aucas 1639802 (rotación marcada en M6 y
  el M2 solo con el núcleo) son incumplimientos de una regla que ya existe.
- La herencia al TDE (rest defense y clase del bloque) y el SOB2 desde el nivel
  de hoy.

## Lo que NO se propone y por qué

- **Ningún número.** Ni la vida útil, ni los umbrales del MECANISMO, ni el
  corte de DTP-REHACER. Tampoco una banda de «parejo» para el volumen (punto
  1.(a)), un valor de xG por penal (1.(c)), una ventana de minutos para el
  rearme (8) ni la magnitud de la posesión (3). Ninguna lección lo pide, y no
  hay backtest con qué fijarlos.
- **La herencia del SOB2 desde la rama persiguiendo:** sigue siendo una
  decisión del usuario.
- **`ROLES_GRID_REHACE`:** la medición está hecha (incidencia 1232); lo decide
  el usuario.
- **El casillero del DTP en la taxonomía de Jev** (`lectura_dtp` o
  redefinir `lectura_efe`): ninguna de las 38 etiquetas `lectura_efe` habla
  del EFE. Es código y toca cómo se agrupan los fallos; lo decide el usuario.
- **Candidatos con uno o dos casos**, que quedan anotados y no entran:
  - el lateral o defensor fresco como banco ofensivo (Başakşehir 1584463,
    Bolívar 1645531);
  - el MECANISMO-ABIERTO activo que baja el veredicto de la rama (Cúcuta y
    Westerlo 1558679);
  - el rest defense «sin» que impide un FAVORABLE persiguiendo (The Strongest
    1645456, de copa, y Groningen 1552215);
  - los penales concedidos en serie son del equipo y no de la línea (La Guaira:
    1646922 en la v1.7 y Portuguesa–La Guaira 1646930);
  - el caso de la 6 viaja también con el arquero que lo sostuvo (Villarroel
    1645530: hoy atajó el suplente y el bloque concedió 2,89 de xG);
  - «lo sostuvo el rival fallando» como otra forma de `sostuvoArquero` (Cercle
    1558675: 2,18 de xG en contra, casi todo de dos penales errados);
  - el seguro en la pelota parada propia (Danubio 1646902: el 0-1 fue una
    transición tras un córner propio);
  - con ventaja, un cambio atrás por vez (Roma–Sassuolo 1550187);
  - la pregunta 5 con ventaja temprana: el repliegue fue plan (U. Católica
    1505554);
  - una línea nueva o un reconvertido es vía a verificar, no un mismatch dado
    (Getafe 1570438, Lille 1635640 y Bodø 1635640: dos de los tres son del mismo
    partido);
  - guardar los cambios en el tercer partido en ocho días (Caracas 1646928);
  - un 1-0 once contra once no prueba administrar una ventaja amplia
    (Instituto 1493217, el mismo caso de la v1.7: no suma).
- **La rotación en copa** (Palmeiras 1492447, el triple cambio del 46' con la
  vuelta a tres días): la cubre la v1.5.

## Cuándo se reabre

- **Cuando la app construya lo pendiente** (la tabla de «Para la app»). Las
  reglas del banco, el grid, el caso de la 6, el MECANISMO y la pelota parada se
  vuelven a medir con los insumos calculados a la vista. Si después siguen
  fallando igual, es rúbrica y entra a la v1.9. Si dejan de fallar, era la
  lista que faltaba.
- **Cuando un candidato junte tres casos acreditables** (sin copa ni
  cuarentena) en partidos distintos.
- **Cuando el usuario decida** el SOB2 desde la rama persiguiendo,
  `ROLES_GRID_REHACE` (1232) o el casillero de Jev.
- **Una banda de «parejo» para el volumen o un valor por penal** solo con un
  backtest sobre los veredictos cerrados (volumen a favor y en contra por rama
  contra el resultado), nunca desde las lecciones.
- Y como siempre: con 4 fallos con lección pendiente se abre la revisión
  (`disparador`), lo que no autoriza ningún cambio por sí solo.

## Lo que va al código si se aprueba

| Punto | Parte y backend | Tipo |
|---|---|---|
| 1 | volumen a favor **y en contra** por bloque en el objetivo, con los penales del partido al lado (sobre el `volumen` pendiente de la v1.7) | calculable |
| 2 | `m2.veredictoRamas.*.siNo` (opcional); aviso de rama sin vías de `viasGol`; aviso `veredicto` distinto de la rama más probable | campo + aviso |
| 3 | `m2.posesion.arriba` (opcional); `posesionReferencias` con el DT de cada partido | campo + calculable |
| 4 | córners concedidos en los insumos (pendiente de la v1.7) | calculable |
| 5 | `bancoOfensivo` (pendiente de la v1.7); aviso de un nombre en el XI de referencia y en el banco | calculable + aviso |
| 6 | lectura del grid del once oficial en los insumos del rehacer; aviso de coordenada inexistente; aviso de sensibilidad del EFE sin variante en el M1; `M1-VS-ONCE-OFICIAL` (pendiente de la v1.7) | calculable + aviso |
| 7 | amarillas, roja reciente y vuelta de suspensión de cada pieza de `m2.piezas` desde `sanciones.py` | calculable |
| 8 | `rearmes` (pendiente de la v1.7), con la banda de cada cambio | calculable |
| 9 | pares de MECANISMO (pendiente de la v1.7) con la zona de cada cambio y la reserva (`con diez`, `autogol/penal`) | calculable |
| 10 | — | rúbrica pura |

Lo calculado se calcula al leer, como el resto de lo derivado. Ninguno de
estos campos toca el motor ni un número calibrado. Los puntos 2.(b), 2.(c),
3, 4.(b), 5.(b), 5.(c), 6.(b), 7, 8, 9.(c) y 10 son rúbrica pura.

## Cómo se aplica si se aprueba

1. El usuario aprueba o corrige punto por punto. Se aprueban por separado:
   - el 1.(a), porque cambia cómo se juzga el veredicto en el cierre;
   - el 10, que se apoya en un caso de copa;
   - los candidatos, que no entran.
2. **Antes de redactar, la app** (si el usuario lo pide al mantenimiento): lo
   pendiente de la v1.7 y lo nuevo de la tabla de arriba, con
   `docs/openapi.yaml`, los tipos, los tests y el prompt de `docs/COWORK.md`.
   Un aviso nuevo del recibo entra a la lista de alertas calculadas que
   `test_arquitectura` exige documentadas.
3. Se redacta la v1.8 en `docs/skills/diagnostico-tactico/SKILL.md`, con su
   entrada en el encabezado. Lo que la app todavía no traiga va como
   «pendiente de la app», sin nombre de campo, como en la v1.7.
4. Se suma `("v1.8", fecha)` a `lecciones.CORTE_VERSION`, y la hora de subida
   del zip a `simulacion.SUBIDA_VERSION`.
5. Se entrega el `.zip` para subir a la cuenta.
6. Se cierran con 🔑 las anteriores a la v1.8. Las 18 de copa y las 10 de
   cuarentena cierran igual, porque fijaron rúbrica. Sigue pendiente cerrar
   las anteriores a la v1.7 (`docs/DEUDA.md` punto 20).

## Resumen: qué lecciones toca cada punto

Por la regla que cita cada lección (la tabla de «De dónde sale»). Un grupo
puede alimentar más de un punto; cada lección cuenta una vez.

| Punto | Grupos de lecciones | Lecciones | Fallos | Parciales | Aciertos | Acreditan | Copa | Cuarentena |
|---|---|---|---|---|---|---|---|---|
| 1 · Volumen de los dos lados | M5 | 153 | 50 | 30 | 73 | 149 | 2 | 2 |
| 2 · Rama con su contrario; ceder no es señal | veredicto por rama | 105 | 30 | 17 | 58 | 100 | 3 | 2 |
| 3 · Posesión igualado y arriba aparte | posesión | 31 | 8 | 13 | 10 | 31 | 0 | 0 |
| 4 · Pelota parada del que cede; media distancia | pelota parada, media distancia | 33 | 4 | 8 | 21 | 32 | 1 | 0 |
| 5 · Banco y penales desde la hoja | banco, penales | 137 | 39 | 29 | 69 | 134 | 2 | 1 |
| 6 · Grid copiado; rehacer también el plan | M1, DTP-REHACER | 59 | 12 | 11 | 36 | 57 | 2 | 0 |
| 7 · Expulsión de los dos lados | (dentro de M1 y veredicto por rama) | — | — | — | — | — | — | — |
| 8 · Quién queda atrás, por carril | rearme | 45 | 14 | 8 | 23 | 45 | 0 | 0 |
| 9 · Corrección y reserva del MECANISMO | MECANISMO-ABIERTO | 47 | 13 | 11 | 23 | 43 | 2 | 2 |
| 10 · El reconvertido ataca | (dentro de M1) | — | — | — | — | — | — | — |
| Confirman sin cambio (checklist y dos capas, vías, carril, piezas, otras) | | 154 | 37 | 37 | 80 | 145 | 6 | 3 |
| **Total** | | **764** | **207** | **164** | **393** | **736** | **18** | **10** |

## Cambio adicional (08/11, pedido del usuario): la génesis del gol

**Pedido:** «al DTP le falta la teoría de cómo llegó el gol». **Base:**
`docs/revisiones/DTP_autopsia_gol_estudio.md` (15 partidos de la semana,
45 goles, 36 con crónica que nombra la jugada). Se aprueba aparte de los
puntos 1 a 10. **Ningún número del skill se mueve**: no hay umbral, peso ni
minuto nuevo; son una lista cerrada, un procedimiento y dos obligaciones de
escritura.

**Lo medido, en corto:**

- El M4 de los cierres casi nunca trae la jugada: **1 de 43** goles de la
  muestra con mecánica real en el cierre siguiente, y **36 de esos 43 tenían
  crónica en la web**. En todo el archivo, ~19 % de los 973 goles del M4 traen
  algo parecido a una mecánica; el resto es autor y asistente de la ficha.
- `via` hoy es `juego_abierto` en 636 de 973: es el cajón por defecto, no una
  clase.
- Las `viasGol` del M2 cubrieron la forma del gol en 17 de 36 (**Sí**), a
  medias en 15 y no en 4. Las listas son un menú de 5 a 14 vías que casi
  siempre repite lo mismo; lo que separa el acierto es **la zona y el
  intérprete**.
- Lo que más se escapa: **la pelota sucia del área** (rebote, error del
  arquero, autogol, desvío: 2 «Sí» de 7, más 3 desvíos), **el balón largo a la
  espalda** (0 de 2), **la transición del dominante** (Barça, Cali) y **el
  ejecutor real del penal** (Monterrey, Toluca).

### (a) M4: la categoría del gol, de una lista cerrada

Cada gol del M4 lleva **una categoría principal** de esta lista, y nada fuera
de ella:

| Familia | Categoría |
|---|---|
| Pelota parada | córner directo · segunda jugada de córner (incluye el córner en corto) · tiro libre directo · centro de tiro libre · lateral |
| Penal | penal (con su origen: falta, mano o VAR; y «en el rebote» si se atajó y se convirtió después) |
| Transición | transición tras recuperación alta · media · baja (la contra tras un córner rival es baja) |
| Salida | error en la salida bajo presión (pase o despeje propio en campo propio) |
| Ataque elaborado | centro lateral · pase interior entre líneas · combinación por dentro · desborde individual |
| Directo | balón largo a la espalda (pelotazo o pase elevado sin recuperación previa) |
| Remate | tiro de media distancia |
| Pelota sucia | rebote o segunda jugada en el área · error del arquero (en la atajada) · autogol |
| — | sin fuente |

Y dos **marcas** que no son categoría: **desvío** (el remate cambió de
dirección en un rival) y **banco** (el autor o la pieza del gol había entrado).

Reglas de uso:

1. **Sin fuente es una categoría, no un hueco.** Si ninguna página abierta
   nombra el disparador o la secuencia, la categoría es «sin fuente», con lo
   que sí se sepa (autor, asistente, «de cabeza»). Nunca se deduce la jugada de
   la asistencia, del tipo de la ficha ni del puesto del autor (un central que
   marca no es «pelota parada» sin fuente). La disciplina de no inventar no
   cambia.
2. **La categoría la decide el disparador**, no la definición: el gol de
   Havertz es «error en la salida» aunque terminó en un centro; el de Karl
   también, aunque fue una vaselina.
3. **`via`** (`pelota_parada` · `transicion` · `juego_abierto`) se deriva de la
   familia y deja de escribirse a mano cuando la app guarde la categoría (ver
   (d)). Hasta entonces, «sin fuente» va con `via` vacía, no con
   `juego_abierto`.
4. **MECANISMO-ABIERTO** se sigue nombrando con precisión (zona o rol); la
   categoría es el piso, no el reemplazo («segunda jugada de córner» no alcanza:
   «córner en corto, centro al segundo palo sin marca del lateral»).
5. Si la crónica aparece después del cierre, **se reclasifica** (ya lo dice la
   v1.4 para `sin mecánica`); con la app, el cambio queda fechado.

### (b) Protocolo de fuentes para la crónica, por liga

Antes de escribir «sin fuente», el cierre **abre** al menos dos páginas de la
lista de su liga. El resumen del buscador **no es fuente**: en el estudio
inventó la jugada dos veces (Berdugo, Pedro) y le atribuyó a una página un
dato que no traía (Di Lollo). Se cita la URL de la
página abierta en `absolucion` o en la nota del gol.

| Liga | Buscar en | Probar primero | Si no sale |
|---|---|---|---|
| Premier y equipos ingleses en Europa | inglés | sitio del club (match report), flashscore.com/news, PA Media (irishnews.com y otros) | 101greatgoals.com |
| Bundesliga y alemanes en Europa | inglés | bundesliga.com (match report) | flashscore.com/news (fcbayern.com da 403) |
| Serie A | inglés o italiano | livescore.com (Football Italia) | flashscore |
| LaLiga | español | (sin medir: el único partido no estaba indexado) | flashscore.es, sitio del club |
| Argentina | español | contextotucuman.com | 442.perfil.com (solo definición; elgrafico y tudn dan 403) |
| Brasil | portugués, con «como foi» | jb.com.br, flashscore.com.br | — |
| Liga MX | español | foxsports.com.mx | planoinformativo.com, record.com.mx |
| Perú | español | exitosanoticias.pe, caretas.pe | prensa del país del jugador extranjero (primicias.ec para un ecuatoriano); americatv.com.pe da poco |
| Colombia | español | noticiasrcn.com | winsports.co, occidente.co |

Consulta que funcionó: «[local] [marcador] [visitante] [goleadores]
[report / crónica / como foi]». **Partidos de menos de 48 horas**: la crónica
puede no estar indexada (Valencia–Real Madrid y Forest–City no salieron); se
escribe «sin fuente · a reintentar» y el cierre siguiente del mismo equipo la
vuelve a buscar. La tabla es fechada: se rehace con cada revisión del skill.

### (c) M2: lo que tiene que figurar sí o sí en `viasGol`

Con lo medido, **de los dos lados**, además de lo que ya pide la v1.5:

1. **La pelota sucia del área**: quién llega al rebote y contra qué arquero.
   Obligatoria cuando el arquero rival es suplente o viene de un error (fue el
   único caso donde se escribió, Grando, y acertó dos de dos).
2. **El balón largo a la espalda**: del que defiende, contra la línea alta del
   rival, con el central que queda mano a mano (Viñas contra Bueno, Nusa con
   Nkunku). Hoy solo se escribe la espalda del lateral «en transición».
3. **La transición también del favorito**: el que domina la pelota recupera
   alto y medio; su contra se escribe aunque sea el que ataca (Barça al 52',
   Cali al 32').
4. **El ejecutor del penal según la hoja del día**, no el de la temporada:
   quién patea si el habitual no está en cancha **y** quién del banco puede
   tomarlo (Monterrey: escrito Ocampos, pateó Cuypers; Toluca: escritos
   Helinho y Viñas, pateó Vega al entrar). Precisa la v1.5, no la cambia.
5. **El origen de la pelota parada además del rematador**: córner en corto,
   lateral al área y el tiro libre directo de quien no es el lanzador
   habitual (Amuzu).

Y una regla de forma: **cada vía nombra zona o intérprete**. Una vía que solo
dice la categoría («pelota parada», «media distancia») no cuenta como vía en
el cierre: con listas de 14 entradas, cubrir la categoría es casi seguro y no
dice nada.

### (d) Para la app (no para el skill; se escribe «pendiente de la app»)

1. **Guardar la categoría de cada gol** en el M4 del parte (la lista cerrada
   de (a), validada al depositar; fuera de lista → aviso en el recibo, no
   rechazo), con `desvio` y `banco` como marcas, la `fuente` (URL) y
   `reclasificadoEn` si cambia después.
2. **Medir**: por categoría, cuántos goles estaban en las `viasGol` del
   equipo que anotó, separando «categoría» de «zona o intérprete». Es el
   número que hoy este estudio hizo a mano sobre 36 goles; con la app sale de
   cientos. Va a las métricas del DTP como **observación sin tasa** hasta que
   el usuario decida otra cosa.
3. **Marcar en los insumos del cierre** (`GET /analisis/cowork/dtp/{id}`) los
   goles que la ficha ya permite pre-etiquetar sin juicio: `Penalty` (penal),
   `Own Goal` (autogol), el `Missed Penalty` seguido de un gol del mismo
   jugador en el mismo minuto (penal en el rebote) y el autor que entró desde
   el banco (marca `banco`). Lo demás sigue siendo de la crónica.
4. **Aviso del recibo** cuando un cierre trae todos sus goles «sin fuente» en
   un partido de una liga con fuente de la tabla de (b) y de más de 48 horas:
   no rechaza, avisa que la crónica probablemente existe. Si entra, va a la
   lista de alertas calculadas que `test_arquitectura` exige documentadas.

### Qué NO se propone

- Ningún umbral nuevo para MECANISMO-ABIERTO ni para el M2; ninguna «tasa de
  vía» que mueva un veredicto. La muestra es de 36 goles.
- No se le pide a Jev ni a la ficha que deduzcan la jugada: la categoría la
  pone quien leyó la crónica, o es «sin fuente».
- No se ordena la lista de `viasGol` por probabilidad: no hay con qué
  calibrarla todavía (lo da el punto (d).2 cuando junte casos).
