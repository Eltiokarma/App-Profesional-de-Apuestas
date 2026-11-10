# Propuesta de revisión · `diagnostico-tactico` v1.7 → v1.8

**Estado:** PROPUESTA, pendiente de aprobación del usuario. Escrita el
08/11/2026 a partir del dossier
(`GET /analisis/cowork/revision/diagnostico-tactico`, cohorte `c3-2026-09-23`,
generado el 08/11 a las 02:31) sobre la v1.7 vigente (01/11). Nada de esto
está redactado en `docs/skills/diagnostico-tactico/SKILL.md` todavía.

**Actualizada el 10/11/2026** con el dossier generado el 10/11 a las 02:13 UTC
(misma cohorte, misma v1.7): **1032 lecciones pendientes** de **236 partidos**
del 01/11 al 09/11, de las que **268 (67 partidos, 08-09/11) son nuevas**.
Sigue sin aprobar. Lo escrito el 08/11 queda como estaba, con su numeración;
lo nuevo va así:

- en los cambios 1 a 10 y en la génesis del gol, un párrafo **«Refuerzo
  10/11»** o **«En contra 10/11»** cuando las lecciones nuevas los tocan;
- los cambios **11 a 14**, nuevos, a continuación del 10;
- las secciones nuevas: «El modo de fallo `lectura_efe`, uno por uno»,
  «`rolesVsGrid`: lo que dicen las lecciones», «Comprobación con los
  veredictos del 08-09/11» y «Núcleo e historial»;
- en «Para la app», lo pendiente verificado contra el código del 10/11.

Unos 50 veredictos del 08-09/11 se estaban cerrando cuando se cortó el
dossier: cada cambio lleva su línea «Se sostiene si… / Lo tumba si…» para
mirarlos.

**Segundo corte, 10/11 a las 04:29 UTC:** se cerraron los veredictos que
faltaban. Traen **118 lecciones nuevas de 29 partidos** (73 del 07/11 y 45 del
08/11) que no estaban en el dossier de las 02:13. Lo que se agregó con ellas:

- debajo de cada «Se sostiene si…», una **«Comprobación 10/11»** con lo que
  dicen las lecciones nuevas (sostiene, matiza, tumba o sin casos);
- el **cambio 15**, que sale de las lecciones nuevas (tres casos);
- el **cambio 16**, la incidencia 1056, **APROBADO por el usuario el 10/11**
  (el texto viejo y el nuevo del skill, exactos);
- al final, la sección «Tabla de cambios».

Salvo el 16, todo sigue sin aprobar. Nada de esto está redactado en el
`SKILL.md`.

**Decidida por el usuario el 10/11/2026** (en conversación): el 16 (1056,
opción a) y «lo demás como recomiendas». Cada punto abierto quedó resuelto con
la recomendación de esta propuesta y, donde no recomendaba nada, con la regla
conservadora (no aflojar lo vigente, no mover números, 1-2 casos —o 3 con dos
del mismo cruce o uno contaminado— quedan como candidato). La tabla va abajo;
lo que entra al `SKILL.md`, con su texto exacto, en «Lista para redactar», al
final. Sigue sin redactarse en el `SKILL.md`.

## Decisiones del 10/11

| Punto | Decisión | Efecto en el texto |
|---|---|---|
| 1 · NEC–Utrecht 1552223: ¿manda la diferencia de volumen o la lista de vías cumplida? | **Manda la diferencia de volumen** (el 1.(a)); la lista cumplida se anota y no sube el veredicto | 1.(a) entra con esa frase; el caso NEC queda como ejemplo de NEUTRO |
| 1.(a) · juzgar contra lo concedido | Entra (recomendación de la propuesta; 6+ casos en cada sentido) | regla del M5 |
| 8 · el rearme del medio | **Candidato** (2 casos limpios: Gimnasia mezcla el rearme con una roja) | sale de la regla del 8; al changelog como candidato |
| 10 · el reconvertido también ataca | **Sigue candidato** (2 casos limpios: Leones del Norte y Telstar; Peña Sport es de copa y Cajamarca no dice si el lateral estaba reasignado) | no pasa a regla; la línea de candidato del M1 suma los casos |
| 11 · «Contradicción a la vista» del ejemplo de Paderborn | **Se reescribe el ejemplo** con la lectura que no choca: decide el perfil del rival, leído en su sede de hoy, no la sede del foco | reemplazo exacto en la Precisión v1.7 de la posesión |
| 13 · penales concedidos en serie | **Candidato** (3 casos, dos del mismo cruce venezolano y ninguno con crónica) | no entra; la línea de candidatos del MECANISMO suma los casos |
| 14 · redacción | **«Con la vía nombrada, la rama sube por él»** (recomendación de la propuesta) | entra con esa frase |
| 16 · 1056 | **Aprobado (a)** heredar y avisar (ya escrito) | Integración, texto exacto |
| 16.(b) · el arrastre de la línea 196 del M2 | **Entra** (regla conservadora: sin él, el M2 dice «no cambia» y la Integración dice que cambia) | reemplazo exacto en el M2 |
| Génesis del gol | Entra (pedido del usuario del 08/11), con las dos correcciones de la tabla de fuentes (El Gráfico respondió; Chile con Redgol) | M4 y M2; la tabla, fechada, dentro del M4 mientras no se aplique el núcleo |
| Candidato del 2 (seguro «sin» persiguiendo) y los de «Lo que NO se propone» | Siguen candidatos (no traen casos nuevos) | changelog |
| `ROLES_GRID_REHACE` (1232) | **Sigue en `False`** (conservadora: la propuesta no recomienda; primero la medición cruzada de 0 tokens de «`rolesVsGrid`») | nada al skill; «Para la app» |
| Casillero de Jev (`lectura_dtp` o redefinir `lectura_efe`) | **No se cambia en esta revisión** (conservadora: es código, toca cómo se agrupan los fallos, y la propuesta no recomienda) | nada al skill; es la A0 del EFE |
| Precisiones de un caso (4: con materia la vía tampoco está dada, Limache; 11: las bajas del rival en su condición, Los Chankas; 7: el recambio cargado de tarjetas, Gimnasia; 9: el asistidor repetido bajo el umbral, Argentinos; 5: el segundo de la lista que recibe la falta, Panathinaikos) | **Notas**, no regla | quedan en esta propuesta, fuera del `SKILL.md` |

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
  carril, el rearme y el banco. Es el mismo hallazgo de la v1.7. **Decidido
  por el usuario el 10/11/2026** (regla conservadora): el casillero de Jev no se
  cambia en esta revisión (ver «Lo que NO se propone»). **10/11:** ahora son
  46 (26 fallos y 20 parciales); la clasificación de las 46, una por una, está
  en «El modo de fallo `lectura_efe`, uno por uno».
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

### Actualización 10/11: lo que suma el dossier nuevo

- **Ventana entera:** 1032 lecciones pendientes, 236 partidos, 01/11 a 09/11:
  291 fallos, 201 parciales y 540 aciertos. **1004 acreditan**; las 18 de
  copa y las 10 de cuarentena que enseña son las mismas del 08/11.
- **Lo nuevo:** **268 lecciones de 67 partidos** (250 del 08/11 y 18 del
  09/11): 84 fallos, 37 parciales y 147 aciertos. **Las 268 acreditan**
  (`ciega` + `PRE`): ninguna es de copa ni está en cuarentena. Todas leyeron la
  v1.7. Ninguno de los cuatro partidos que todavía deben su cuarentena (LDU
  1631509, Palmeiras 1492426, Manta 1639824 y 1639827) aparece en este skill.
  El dossier lista en `enCuarentena` a Huracán–Tigre 1493219 (automática, sin
  DT declarado, no enseña): fuera.
- **Cohorte del dossier:** 126 casos ciegos (252 lados: 105 aciertos, 55
  parciales y 92 fallos del lado). El 1X2 acertó 67 de 126 (53 %); Brier
  0,583 contra una línea de base de 0,648. Siguen sin ser una tasa de acierto
  del skill (`sesgoDeAtribucion`).
- **Ningún número:** Jev marcó 80 lecciones con `proponeMoverNumero: false`
  (15 de las nuevas) y ninguna con `true`; `pidenMoverSinPoder` sigue vacío.
- **Las 268 nuevas, por la regla que citan primero** (la misma agrupación,
  hecha con el texto de `reglaTocada`; cada lección cuenta una vez):

  | Regla que cita | Lecciones | Fallos | Parciales | Aciertos | Partidos |
  |---|---|---|---|---|---|
  | M5 · volumen y conversión | 58 | 24 | 10 | 24 | 46 |
  | M2 · veredicto por rama | 42 | 10 | 9 | 23 | 38 |
  | Vías (segunda línea, quinta línea, lado débil, banco en vías) | 31 | 6 | 3 | 22 | 26 |
  | Checklist del bloque (casi todo la 6) y dos capas | 26 | 6 | 3 | 17 | 24 |
  | Banco ofensivo | 25 | 8 | 2 | 15 | 23 |
  | Ejecutor de penales | 20 | 5 | 3 | 12 | 17 |
  | M3 · costo de rearmar | 15 | 5 | 4 | 6 | 14 |
  | M1 (grid, variantes, amarillas) | 14 | 4 | 1 | 9 | 13 |
  | Posesión por rama | 13 | 6 | 2 | 5 | 11 |
  | MECANISMO-ABIERTO | 7 | 4 | 0 | 3 | 7 |
  | Duelos por carril | 5 | 1 | 0 | 4 | 5 |
  | Otras | 4 | 1 | 0 | 3 | 4 |
  | DTP-REHACER | 3 | 1 | 0 | 2 | 3 |
  | Pelota parada | 3 | 1 | 0 | 2 | 3 |
  | Piezas y rotación (M6) | 2 | 2 | 0 | 0 | 2 |

  OJO con la columna «Fallos»: es el veredicto del LADO, no de la lección.
  Muchas lecciones de lados fallados dicen «confirmación» (Marseille 1552818,
  Olympiakos 1593357, Sunderland 1557466 y otras).
- **Lo que cambia respecto del 08/11:** nada de lo escrito se cae. Las
  lecciones nuevas **refuerzan** los cambios 1, 2, 5, 6, 7 y 8; dan **un
  caso en contra** al 5.(c) y al 3; y hacen subir a regla tres candidatos que
  ya estaban anotados (cambios 12, 13 y 14). Aparece una precisión nueva de
  la posesión (cambio 11).

### Segundo corte 10/11 (04:29 UTC): los veredictos que faltaban

- **Lo nuevo:** **118 lecciones de 29 partidos** (73 del 07/11 y 45 del
  08/11). Por veredicto del lado: 43 fallos, 18 parciales y 57 aciertos. Con
  las del primer corte, la ventana suma **1150 lecciones pendientes**.
- **Población:** **113 acreditan** (`ciega` + `PRE`, sin copa ni cuarentena).
  **5 están en cuarentena que enseña**: Once Caldas–Águilas Doradas 1549861,
  los dos lados (el parte dice Hernán Darío Herrera, el banco dice Carlos
  Valencia). No cuentan y fijan rúbrica. Ninguna es de copa. Ninguno de los
  cuatro partidos que todavía deben su cuarentena (LDU 1631509, Palmeiras
  1492426, Manta 1639824 y 1639827) aparece en este skill. Todas leyeron la
  v1.7.
- **Ningún número:** 13 lecciones nuevas con `proponeMoverNumero: false` y
  ninguna con `true`.
- **Modo de fallo:** 7 `lectura_efe` nuevas. Ninguna nombra al EFE: son
  rúbrica del DTP, como las 46 anteriores (53 en total). Se reparten así:
  - Audax 1505555: posesión;
  - O'Higgins 1505561 y Viseu 1575540: volumen (Viseu también ceder);
  - Sport Huancayo 1549546: la vía entera;
  - Comerciantes 1549547: la 6 sostenida por el arquero;
  - Alianza Atlético 1549549: la vía que no sobrevive a los cambios (cambio 15);
  - Nacional 1575540: el banco.

  Una más es `varianza` (Banfield 1493229).
- **Las 118, por la regla que citan primero** (la misma agrupación de
  siempre; cada lección cuenta una vez):

  | Regla que cita | Lecciones | Fallos | Parciales | Aciertos | Partidos |
  |---|---|---|---|---|---|
  | M5 · volumen y conversión | 25 | 9 | 5 | 11 | 22 |
  | M2 · veredicto por rama | 20 | 6 | 3 | 11 | 18 |
  | Banco ofensivo | 14 | 6 | 3 | 5 | 12 |
  | Checklist del bloque (casi todo la 6) y dos capas | 11 | 4 | 1 | 6 | 11 |
  | Vías (pelota parada por zona, centrales, segunda línea) | 9 | 2 | 2 | 5 | 8 |
  | M3 · costo de rearmar | 8 | 4 | 0 | 4 | 8 |
  | Ejecutor de penales | 7 | 1 | 1 | 5 | 7 |
  | Posesión por rama | 5 | 3 | 1 | 1 | 4 |
  | DTP-REHACER (momento tardío) | 4 | 1 | 0 | 3 | 4 |
  | M1 · el grid manda | 4 | 3 | 1 | 0 | 3 |
  | Pelota parada con materia | 4 | 1 | 0 | 3 | 4 |
  | MECANISMO-ABIERTO | 3 | 2 | 1 | 0 | 3 |
  | Duelos por carril | 3 | 1 | 0 | 2 | 3 |
  | Piezas (M6) | 1 | 0 | 0 | 1 | 1 |

  Las 5 de cuarentena están dentro de la tabla: una en M5, una en veredicto,
  una en la 6, una en penales y una en pelota parada. Igual que en el primer
  corte, la columna «Fallos» es el veredicto del LADO, no de la lección.
- **Lo que cambia:**
  - **ningún cambio se cae**;
  - **sostienen** el 1, 2, 5, 7, 8, 9, 11, 12 y la génesis;
  - **matizan** el 4, el 6 y el 14;
  - no traen casos para el 3 ni para el 13;
  - el 10 suma un caso.

  **Sube un candidato a tres casos:** el rearme del medio, en el cambio 8.
  **Entra una regla nueva**, la vía persiguiendo que sobrevive a los cambios
  (cambio 15). **El hallazgo nuevo de la tanda no es del skill:** en seis
  partidos la API corrigió la formación después del pitazo (ver el cambio 6).

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

**Refuerzo 10/11.** Las 147 lecciones de acierto del 08-09/11 confirman lo
mismo:
- **El banco nombrado, en cualquier rama** (también ganando o igualado), fue
  el gol o la asistencia en St. Truiden 1558678 (Matsuzawa, al minuto de entrar),
  Beşiktaş 1584458 (Poku con 2-0), Fenerbahçe 1584459, Olympiakos 1593357
  (González, a los dos minutos), Marseille 1552818 (Abdallah), Cerro
  1632056, Villarreal 1570452 (Pépé y Ayoze), Köln 1575219, Cambuur 1552219,
  Genoa 1550190, Oriente Petrolero 1645540, Le Mans 1552814 (Colas al 90') y
  los dos lados de Portuguesa–Metropolitanos 1646934.
- **El ejecutor de la base, primero y en cancha:** Bolívar 1645539, Rio Ave y
  Braga 1575541 (Horta), St. Truiden 1558678, Brighton 1557458, Cruz Azul
  1551033, Sunderland 1557466 (Le Fée), América 1551035 (H. Martín),
  Universitario 1549553 (Lapadula), Twente 1552222 (Weghorst) y Pumas
  1551035 (Morales, el segundo, con el primero ya fuera).
- **`sin mecánica` bien declarado, con la frecuencia contada:** Çorum
  1584459 (tres pares a ≤ 15'), Zulte Waregem 1558678, Genoa 1550190,
  Feyenoord 1552221 y Macará 1639805 (mismo asistidor y mismo definidor).
- **Volumen y conversión por separado, en los dos sentidos:** varianza bien
  separada en Celta 1570444 (3,12 de xG), Brugge 1558672, OFI 1593356, Cerro
  1632056, Querétaro 1551036 y Monza 1550192; acierto por encima de lo
  generado sin acreditarlo en Milan 1550190, Independiente del Valle 1639803,
  Benfica 1575538, Lille 1552816 y Cuenca 1639833.
- **La vuelta del carril escrita** dio los goles en Querétaro–Puebla 1551036
  (las dos vueltas), Cambuur 1552219, Levadiakos 1593352 e Iraklis 1593355.
- **Las dos capas con once tardío:** Real Sociedad 1570449, The Strongest
  1645539, Toluca 1551034, Anderlecht 1558672, Orense 1639833 y Santa Fe
  1549862: cayó la capa de nombres y sostuvo la estructural.

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

**Refuerzo 10/11.** Es el grupo más grande de las nuevas (58 lecciones, 46
partidos), y el error va **en los dos sentidos**, que es lo que pide juzgar
contra lo concedido y no con un número propio:
- **FAVORABLE que no generó** (apertura sin «quién remata en el área»):
  América de Cali–Deportivo Cali 1549854 (pelota parada con 7 córners, 4
  remates en el área y 0,40), Macará–U. Católica 1639805 (7 de 14 de afuera),
  Santa Clara–Gil Vicente 1575542 (0 al arco; el gol fue un autogol),
  Feyenoord–Heerenveen 1552221 (1,22 contra 1,97) y América–Pumas
  1551035.
- **NEUTRO o DESFAVORABLE que generó mucho más de lo que concedió:**
  Sunderland–Chelsea 1557466 (2,58 contra 0,55 cediendo el 69 %), Brest–Lyon
  1552812 (1,92 contra 0,70), Napoli–Lazio 1550193 (2,44 contra 0,92),
  Twente–Ajax 1552222 (2,56 contra 0,72), LDU–Barcelona SC 1639804 (1,1
  contra 0,16) y Çorum 1584459 (2,00 contra 1,30, perdiendo 0-5).
- **FAVORABLE que generó y concedió igual** (el (a) tal cual): Groningen–AZ
  1552224 (2,18 contra 3,96), Marseille–Lens 1552818 («más cerca de NEUTRO
  que de dominio»: 2,22 contra 2,0), Hoffenheim 1575215 (1,94 contra 2,61) y
  Universitario–Moquegua 1549553 («un FAVORABLE de volumen no dice nada del
  seguro detrás»). Y Querétaro–Puebla 1551036: el FAVORABLE de igualado duró
  9 minutos contra un rival armado para correr por las vueltas.
- **El punto que sostuvo el arquero propio** tampoco confirma la rama: Elche
  1570445 (7 atajadas), Levante 1570444 (9 de Ryan con 3,12 en contra) y
  Atalanta 1550192. Es el mismo (a) leído desde lo concedido.
- **(b), el volumen que no viaja:** Atromitos 1593356 (NEUTRO por el 1,62 de
  temporada; de visita, 0 al arco), Le Mans 1552814 (DESFAVORABLE por «en
  Troyes así no generó»: 1,53 y 12 remates en el área), Schalke 1575215
  (DESFAVORABLE por «4 sin marcar», una racha: 2,61), PAOK 1593357 («un
  DESFAVORABLE que se apoya en el nivel dice cuánto volumen le deja») y
  Moquegua 1549553 («0,6 goles esperados» y generó 1,2). Precisión que piden:
  **la referencia tampoco sale de un solo partido ni de una racha.**
- **(c), los penales en el xG:** América 1551035 (casi la mitad de 1,85),
  Kortrijk 1558673 (~0,5 en juego abierto), Orense 1639833 (casi todo el 0,97
  era el penal errado) e Ipswich 1557462. Cuatro más.

**En contra 10/11 (un caso):** NEC–Utrecht 1552223. El cierre pide
FAVORABLE porque las tres vías de los goles estaban en la lista y el seguro
rival era «depende»; con el (a), 2,31 contra 2,1 es parejo y la rama queda
NEUTRO, que es lo que se escribió. Las dos lecturas no caben juntas.
**Decidido por el usuario el 10/11/2026:** manda la diferencia de volumen (es
lo que ya dice la v1.6 —se juzga lo que generó la rama— leído contra lo
concedido; que los goles salieran por vías de la lista se anota y no sube el
veredicto). NEC queda como ejemplo de NEUTRO. Los cierres que juzgaron solo por lo generado (AZ 1552224, Sport
Boys 1549552, OFI 1593356) no van en contra: generaron mucho más de lo que
concedieron y dan lo mismo con el (a). Man United–Aston Villa 1557464 (3,63
contra 2,94, persiguiendo DESFAVORABLE) también encaja: parejo, NEUTRO, no
DESFAVORABLE.

**Comprobación (veredictos del 08-09/11 que faltan).** Se sostiene si los
FAVORABLE que se cobran como fallo son, otra vez, los que concedieron tanto
como generaron o remataron de afuera. Lo tumba si aparecen FAVORABLE con lo
generado muy por encima de lo concedido, rematado en el área, cobrados como
fallo de mapa (entonces el problema no es la vara sino la conversión, y el
(a) no agrega nada).

**Comprobación 10/11 (118 lecciones nuevas; 25 citan M5):** **SOSTIENE.**

- **FAVORABLE que no remató en el área o concedió lo mismo**, otra vez:
  - Sporting Cristal–ADT 1549545: 3 remates en el área, 0,39 de xG;
  - Alianza Lima–Los Chankas 1549551: 0,92 contra 1,67, apoyado en tener la
    pelota;
  - O'Higgins–U. de Concepción 1505561: 20 remates, 12 de afuera, 1,32 de xG
    «a la par del local». El cierre pide NEUTRO: es el (a) tal cual;
  - Viseu–Nacional 1575540: 0,65 de xG;
  - Coquimbo 1505555 (parcial): 36 % de pelota y 3 al arco;
  - Tigre 1493240: 9 de 13 remates de afuera; lo sostuvo solo la diferencia
    numérica.
- **NEUTRO o DESFAVORABLE que generó mucho más de lo que concedió:**
  - La Serena–Palestino 1505557: 1,61 contra 0,95;
  - Unión La Calera–Huachipato 1505562: 1,44, con 13 de 16 remates en el área;
  - Cajamarca–Alianza Atlético 1549549: 3,13 con el 41 % de pelota;
  - Los Chankas 1549551: 1,67 contra 0,92;
  - Nacional–Viseu 1575540: DESFAVORABLE con 1,17 contra 0,65;
  - Audax–Coquimbo 1505555: persiguiendo DESFAVORABLE con 1,55 de xG y 12
    remates en el área.
- **Lo que podía tumbarlo, mirado:** cuatro lados fallados tienen un FAVORABLE
  con mucho más generado que concedido y rematado en el área:
  - Lanús 1493232: 1,88 contra 0,47;
  - Talleres 1493239: 1,14 contra 0,31;
  - Cienciano 1549546: 2,1 contra 1,52;
  - Garcilaso 1549547: 1,52 de xG, 10 remates en el área.

  **Ninguno se cobró como fallo de mapa.** Los cuatro cierres lo leyeron como
  conversión y arquero, que es lo que ordena el (a). No tumban.
- **(b):** Nacional 1575540 sacó el DESFAVORABLE de «0,34 de xG en Arouca»,
  un solo partido. Es la precisión del primer corte.
- **(c):** sin casos explícitos. Cienciano 1549546 trae un penal en cada xG y
  el cierre no los separó.
- **El punto que sostuvo el arquero propio:** Comerciantes 1549547 (5
  atajadas) y Coquimbo 1505555 (8).
- **Para la app, no para el skill:** sin stats por tramo, la rama no se
  separa del total (Millonarios 1549857, Audax 1505555). Es el `cubreRama`
  pendiente.

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

**Refuerzo 10/11.**
- **(a) La vía entera, en los dos sentidos.** Rama recortada que igual dio
  gol por lo que la lista tenía: Man United–Aston Villa 1557464 (DESFAVORABLE
  persiguiendo y «las cuatro vías escritas dieron gol»), Le Mans 1552814,
  Gil Vicente 1575542 (dejó afuera la transición de Murilo, la primera vía
  del propio M2), Iraklis 1593355 (la vía listada tercera), Betis 1570445 y
  PSV 1552219 (las secundarias). Y el reverso, NEUTRO para una rama sin vía:
  Barcelona SC 1639804, Levante 1570444, Chelsea 1557466, Monterrey 1551034 y
  Lyon 1552812 (con el 9 titular fuera y cinco piezas rotadas). Son cinco de
  las ocho `lectura_efe` nuevas.
- **(b) La condición y su contrario:** Carabobo–La Guaira 1646935 (la
  transición dependía de que el obligado se volcara; sin stats, no se sabe si
  lo hizo). Y la confirmación de escribirlo: Deportivo Cali 1549854 («si
  América no se abre, poco volumen propio», y así fue).
- **(c) Ceder no es señal en contra:** Sunderland 1557466 (31 % y 2,58),
  Brest 1552812 (cedió el 69 % y generó 1,92) y UTC 1549552 (la razón «cede y
  vive de la transición» fue falsa: tuvo el 52 %).
- **La rama jugada con diferencia numérica (v1.7) se cumplió bien** en
  Beşiktaş 1584458, Brighton y Brentford 1557458, Oriente Petrolero 1645540 y
  Jaguares 1549859 («no puesta a prueba»). Chivas 1551037 la juzgó igual con
  37 de sus 90 minutos con uno más. Es el `minutosEnDiferencia` pendiente.
- **Dos FAVORABLE en la misma rama** (v1.7): Atlético–Barcelona 1570443 (1,71
  contra 1,62). Es el primer caso del aviso `M2-RAMAS-ESPEJO`, que no existe.

**En contra 10/11:** ninguna.

**Comprobación.** Se sostiene si los veredictos que faltan siguen trayendo
ramas con gol por un renglón de la lista que la razón no citó, o ramas sin vía
dadas NEUTRO. Lo tumba si las ramas que citan su lista entera fallan igual
que las recortadas (la lista entera no separaría nada).

**Comprobación 10/11 (20 lecciones citan el veredicto por rama):**
**SOSTIENE.**

- **(a) Ramas con gol por un renglón de la lista que la razón no citó:**
  - Sport Huancayo–Cienciano 1549546: el empate fue el penal sobre Falconí,
    el lateral que llega. El M2 lo listaba en el carril y la rama persiguiendo
    no lo citó;
  - Independiente Medellín–Fortaleza 1549858: la pelota parada de Simarra y
    Escorcia estaba en las vías y no en la razón. El 1-0 fue un córner.
- **(a) Ramas sin vía dadas NEUTRO:**
  - Huachipato 1505562;
  - Nublense 1505558: 0,47 de xG, 5 de 7 remates de afuera;
  - Alianza Atlético 1549549: persiguiendo, un remate al arco.

  Águilas 1549861 lo repite, pero está en cuarentena.
- **(b) La condición y su contrario:** Viseu 1575540 apoyó el FAVORABLE en que
  el improvisado de Nacional «se vencía al 55-65», y no se venció. Es el caso
  de Rubio Ñu.
- **(c) Ceder no es señal:** Cajamarca 1549549 cedió (41 %) y generó 3,13. Y
  del lado de la v1.6, tener la pelota tampoco: O'Higgins 1505561, Alianza
  Lima 1549551 y Coquimbo 1505555 apoyaron el FAVORABLE en eso y no
  generaron.
- **La rama con diferencia numérica (v1.7), bien juzgada como «no puesta a
  prueba»:**
  - Argentinos–Huracán 1493228, los dos lados: 65 minutos con diez;
  - Independiente Rivadavia–Gimnasia 1493234, los dos lados.

  Sarmiento 1493240 tenía la roja a la vista y no escribió la línea con uno
  menos (va en el cambio 7).
- **Lo que podía tumbarlo:** ninguna rama que citara su lista entera falló
  igual que las recortadas. No apareció.
- **Nuevo en esta tanda:** la vía que no sobrevive a los cambios del DT. Ver
  el cambio 15.

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

**Refuerzo 10/11.** Un caso nuevo de «igualado» y «arriba» mezclados:
Trinidense–Ameliano 1632061 («la ficha no parte la posesión por tramo»,
45-55 con 46 minutos ganando). Y uno más para la precisión del DT nuevo: Rio
Ave–Braga 1575541 (la referencia era de otro DT y otro modelo: con Franclim
en 3-4-3, 53 %): es el mismo Rio Ave de 1575527, ya citado arriba, en otro
partido. Lo demás de la posesión que traen las
nuevas es otra cosa y va en el cambio 11.

**En contra 10/11 (un caso):** Heerenveen–Feyenoord 1552221. La referencia
era del mismo perfil (NEC, que quería la pelota: 38 %) y la dirección igual
se invirtió (54 %). El cierre lo anota «contraejemplo de un caso, sin mover
magnitud». No tumba la regla —sin referencia del mismo perfil sería peor—,
pero dice que la dirección tampoco es segura con ella.

**Comprobación.** Se sostiene si en los veredictos que faltan la posesión de
«igualado o arriba» vuelve a fallar en partidos con gol temprano del foco.
Lo tumba si fallan igual las ramas que no tuvieron gol temprano: entonces el
problema no es mezclar los dos estados.

**Comprobación 10/11 (5 lecciones de posesión):** **SIN CASOS** para lo que el
cambio propone. Ninguna rama mezcló «igualado» y «arriba» con un gol temprano
del foco: los goles tempranos de la tanda (U. de Chile 1505560 al 14',
Juan Pablo II 1549548 al 9') no traen lección de posesión.

- **La precisión del DT nuevo suma un caso:** Nacional–Viseu 1575540 («con un
  DT de dos partidos… la dirección no se sostiene en el anuncio del rival»).
- **Las otras inversiones de posesión son de otros puntos:** del cambio 11, o
  de la cuenta de jugadores (Gimnasia 1493234: 59 % con 11 contra 10, que ya
  es v1.7).

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

**Refuerzo 10/11 (a).** Santa Clara–Gil Vicente 1575542: la pelota parada de
Pacheco y Fernandes tuvo 1 córner en 90 minutos contra un rival que se quedó
la pelota, y el cierre pide lo mismo que el (a). Ameliano 1632061: la pelota
parada de Falabella y Paredes, con 1 córner. Y el cruce decide, no el
promedio: Trinidense 1632061 (6,6 de promedio, 4 en el cruce, ningún gol de
pelota parada), Juventus–Fiorentina 1550189 (12 córners y el 2-2 de Bremer) y
Monza 1550192 (7 contra 2, vía bien nombrada que cerró el arquero).

**Refuerzo 10/11 (b).** Genoa–Milan 1550190: 10 de 17 remates de afuera
persiguiendo, la media distancia que el M2 listaba fue la vía principal.
Ningún caso nuevo de la media distancia del que cede.

**En contra 10/11:** ninguna.

**Comprobación.** Se sostiene si en lo que falta la pelota parada del que cede
vuelve a quedarse sin córners. Lo tumba si los equipos que ceden y tienen la
pelota parada como vía principal la convierten con pocos córners en varios
partidos (como Chapecoense 1492443): entonces la materia no es el córner del
cruce.

**Comprobación 10/11 (4 lecciones de pelota parada y 2 de vías):**
**SOSTIENE el (a) y lo MATIZA.**

- **Sostiene, el que cede sin córners:**
  - U. de Concepción–O'Higgins 1505561: el que cedía (O'Higgins tuvo el 62 %)
    llevaba el córner a los centrales como vía principal y tuvo 2 córners. El
    cierre pide lo mismo que el (a): «debió ir condicional»;
  - Nublense–Colo Colo 1505558: la pelota parada de Bosso y Céspedes, con 1
    córner en 90'.

  Ninguno de los que ceden convirtió de pelota parada con pocos córners. Lo
  que podía tumbarlo no apareció.
- **Matiza, desde la otra punta: con materia, la vía tampoco está dada.**
  Limache–U. Católica 1505559 tuvo 10 córners contra 4 y la vía aérea no dio
  xG («los córners solos no hacen la vía cuando el rival defiende el área
  con…»). Va como precisión: la materia es necesaria, no suficiente; la vía
  depende también de quién defiende el área.
- **Con materia y gol:** Rosario Central 1493237 (12 córners contra 2) y La
  Serena 1505557 (11).
- **(b), la media distancia del que cede:** sin casos.

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
Bolívar 1645531: Rivero, defensor que entró al 65'). **10/11: sube a regla,
ver el cambio 12.**

**Refuerzo 10/11 (la lista).** El titular habitual rotado primero, que **ya
es regla de la v1.7**, se incumplió en tres partidos y en los tres decidió:
Heerenveen–Feyenoord 1552221 (Meerveld, en el XI de referencia, salió
suplente, entró al descanso e hizo tres goles; el parte escribió «banco
corto»), Asteras–Kalamata 1593354 (Carreazo asistió) y Kortrijk 1558673
(Dejaegere, 9 de 10 titularidades, recibió el penal del 83'; además el banco
escrito, Roche y Podgoreanu, no estaba en la hoja). Le faltó quien decidió:
Rayo 1570449 (Nteka), PSV 1552219 (A. Santos con 3-1), Porto 1575544 (Martim
Fernandes) y las vías de Le Havre contra Lorient 1552813 (Kone, al 66'). Y
**(a)** Cruz Azul 1551033: Ibáñez, nombrado en el banco, fue titular y marcó.
Todo esto es la lista calculada que falta (`bancoOfensivo`).

**Refuerzo 10/11 (c), el más claro de la tanda.** El que patea entró del
banco o es el 9 que entra por el ejecutor, en seis partidos:
- Crystal Palace 1557459: Nketiah, que entró por Strand Larsen;
- Bucaramanga 1549859: B. Caicedo, el 9 que entraba por Pons (suspendido);
- UCV Moquegua 1549553: Angulo, el único de la base, en el banco: entró al
  73' y pateó al 78';
- Freiburg 1575216: Grifo, entrado al 68', con Ginter en cancha;
- Ipswich 1557462: Clarke, entrado al 53', con los dos nombrados en cancha;
- Trinidense 1632061: O. Giménez, del banco ofensivo, con los dos nombrados ya
  fuera.

Y la muestra mínima no fija el orden: Llaneros 1549853 (pateó Vásquez con
Ospina en cancha), Santa Fe 1549862 (Fagúndez 1 de 1; pateó Rodallega) y
Orense 1639833 (Herrera 1 de 1; pateó Mena). Panathinaikos 1593355 suma un
caso nuevo y suelto: el segundo de la lista fue el que recibió la falta
(candidato, un caso).

**En contra 10/11 (un caso), del «después de un errado»:** AZ 1552224.
Meerdink erró el penal del 59' y pateó y convirtió el del 90+1. La regla del
(c) dice que la lista dice quién patea después de un errado; tiene que poder
decir **«el mismo»**: no es que patee otro, es que se escribe.

**Comprobación.** Se sostiene si en los veredictos que faltan vuelve a patear
un suplente o el 9 que entra por el ejecutor nombrado. Lo tumba si los
penales que faltan los patea siempre el primero de la base estando en
cancha: entonces el tercer nombre es ruido.

**Comprobación 10/11 (14 lecciones de banco y 7 de penales):** **SOSTIENE.**

- **(c) Penales:**
  - **el «si entra» se cumplió:** Pereira–Nacional 1549855. M. Pérez,
    nombrado y rotado al banco, entró al 61' y convirtió al 63';
  - **la muestra mínima no fija el orden:** en U. de Chile–Cobresal 1505560
    pateó el tercero nombrado (Vargas) con Rivero en cancha. En Cienciano
    1549546, con Garcés 0 de 1 en la base, pateó Succar, que no estaba
    nombrado;
  - **«nunca vacía»:** Tolima–Millonarios 1549857. El parte dejó «sin fuente
    entre los titulares» y pateó E. Valencia, titular.
- **Lo que podía tumbarlo:** el primero de la base, estando en cancha, pateó
  en tres partidos: Sarmiento 1493240 (le atajaron el penal), U. Católica
  1505559 (Zampedri) y Guabirá 1645537 (Garzón). No tumba: en los otros
  cuatro no fue él.
- **La lista del banco:**
  - **le faltó el que decidió:** Gimnasia–Independiente Rivadavia 1493234
    (Sequeira y Díaz), Talleres 1493239 (Chiavassa, que entró al descanso),
    Colo Colo 1505558 (Bolados), Cobresal 1505560 (un volante y un defensor)
    y Pereira 1549855 (E. Moreno);
  - **el titular habitual rotado primero (v1.7)** se incumplió en Newell's
    1493236 (Mazzantti, en duda, hizo el 2-1 desde el banco) y se cumplió en
    Nacional 1549855.
- **(b) El banco sin minuto fijo:** dos goles de suplentes entrados al
  descanso (Talleres 1493239, Cobresal 1505560).
- **(a):** sin casos.

Once Caldas 1549861 dice que el segundo nombre tiene que ser un titular
probable, pero está en cuarentena: no cuenta.

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

**Refuerzo 10/11.**
- **(a) El grid ya capturado, leído a ojo, en cuatro partidos nuevos:**
  Beşiktaş 1584458 (once con grid a las 17:37, rehacer a las 17:46: Trossard y
  Fakılı en la banda contraria, y los duelos de carril del M2 al revés), Le
  Havre 1552813 (Mizuta y Samatta, cada uno en la casilla del otro), Rayo
  1570449 (4-3-3 escrito, 4-2-3-1 en el grid con Pedro Díaz de mediapunta) y
  América de Cali–Deportivo Cali 1549854 (Bertel lateral en 2:1 y Tovar
  central en 2:3: la vía rival «Martínez a la espalda de Tovar» se escribió
  sobre una casilla que no existía, el mismo hueco que Espanyol). Brentford
  1557458 es parecido, pero el once llegó después del depósito: no cuenta.
- **(b) Al rehacer, las piezas del seguro:** Kalamata–Asteras 1593354 (el
  doble pivote del seguro rival «fijo» con Piñeiro, que no estaba en la hoja;
  el corte de ausentes no pidió rehacer). Y Alianza Valledupar 1549853 da el
  costado opuesto: la apertura (3-4-3) era la buena y el rehacer la pasó a
  4-2-3-1 por un dato de la API que se corrigió después del pitazo. Es
  `dato_api`, no del skill.
- **(c) La señal anunciaba otra línea:** UCV Moquegua 1549553 (la caja de
  sensibilidad del EFE decía «Soto mete línea de cinco para el punto», la
  apertura escribió solo el 4-2-3-1 y jugó 5-4-1). Tercer caso con el EFE como
  fuente de la señal (Levadiakos 1593348 y Táchira 1646932 eran del 01-07/11).
  Y Brugge–Anderlecht 1558672: el rol reasignado sin el pivote fijo no estaba
  entre las alternativas del M1 (un caso).

**En contra 10/11:** ninguna de los cambios (a)-(c). Sobre la excepción del
M1 que ya existe (apartarse del último once con fuente), dos a favor y uno en
contra: Carabobo 1646935 y Bournemouth 1557462 se apartaron y acertaron 11 de
11; Blooming 1645540 se apartó por una previa de prensa y salió el último
once oficial. No pide cambio: la excepción ya exige la fuente.

**Comprobación.** Se sostiene si en los rehacer que faltan el M1 vuelve a
apartarse del grid ya capturado. Lo tumba si los M1 que faltan copian el grid
y el mapa de carriles falla igual: entonces el grid de la API no describe la
banda real.

**Comprobación 10/11 (4 lecciones de M1 y 4 de DTP-REHACER):** **SOSTIENE el
(a) y lo MATIZA.**

- **Sostiene.** El grid ya estaba capturado y el rehacer lo leyó a ojo en tres
  partidos:
  - Sporting Cristal 1549545: L. Díaz y J. González, cada uno en la banda del
    otro;
  - Comerciantes 1549547: Salinas y Parodi al revés (uno en el medio y el otro
    en la línea);
  - Alianza Atlético 1549549: 4-1-4-1 con pivote único, donde el grid ponía
    doble pivote.
- **Matiza: en seis partidos la API corrigió la formación después del
  pitazo.** Fueron Argentinos 1493228, Estudiantes de Río Cuarto 1493237,
  Juan Pablo II 1549548, Millonarios 1549857, Fortaleza 1549858 y
  Guabirá–Bulo Bulo 1645537. Ahí, copiar el grid de antes del pitazo es copiar
  el dato equivocado.
  - Los seis cierres lo trataron bien, con la regla de dos capas de la v1.4:
    «apertura caída por once tardío, no fallo del skill». La capa de nombres
    quedó sin juzgar. La capa estructural se juzgó y casi siempre se cumplió.
  - **No tumba.** Lo que tumbaba era copiar el grid y fallar el carril igual,
    y en estos la capa estructural se sostuvo.
  - Lo que pide es de la app: guardar la hora de la formación y marcar la que
    cambió después del pitazo (`dato_api`), para que el cierre no tenga que
    deducirla.
- **(b):** el banco escrito de Fortaleza 1549858 no estaba en la hoja, pero
  es del once tardío, no del rehacer.
- **(c):** sin casos.

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

**Refuerzo 10/11.** Tres más, y uno pide precisar:
- **Monterrey–Toluca 1551034:** el M1 nombró a Chávez (4 amarillas, la del
  límite) y la roja fue del central Salcedo al 61', tras cinco amarillas de
  Monterrey entre el 48' y el 71'. Precisión: **la vía de expulsión va con
  todas las piezas de la línea que defiende el duelo**, no solo con la que
  está al borde del ciclo.
- **Barcelona 1570443:** Marc Bernal, contenedor único sin Rodri, vio amarilla
  al 74' y salió en el acto; el M1 lo nombró como rol reasignado sin sus
  amarillas, que la tabla F1 ya traía.
- **Gençlerbirliği–Beşiktaş 1584458:** el M1 nombró la zaga nueva como
  vulnerabilidad sin las amarillas de sus centrales; Baltacı se fue a los 22' y
  la rama persiguiendo se jugó 68 minutos con diez.

**En contra 10/11:** ninguna.

**Comprobación.** Se sostiene si en lo que falta hay rojas de piezas del
seguro o de la línea que el M1 no cargó. Lo tumba si las rojas que faltan son
de piezas sin amarillas previas ni papel en el duelo: entonces la vía de
expulsión no se puede leer antes.

**Comprobación 10/11 (dentro del veredicto por rama, M3 y M1):**
**SOSTIENE.**

- **Rojas de piezas del seguro o de la línea que el M1 no cargó:**
  - Independiente Rivadavia–Gimnasia 1493234: Florentín, del doble pivote
    del seguro, expulsado al 17'. La vía no estaba nombrada;
  - Sarmiento–Tigre 1493240: el TDE del mismo parte decía que venía de dos
    rojas y el M2 no escribió la línea con uno menos. Jugó 40' con nueve.
- **La regla, cumplida:** Argentinos–Huracán 1493228 nombró a Paredes, con 4
  amarillas, en el carril de Kalinger, y la rama persiguiendo «con uno menos
  pasa a DESFAVORABLE». Se cumplió.
- **Candidato (un caso):** el recambio que entra al seguro con carga de
  tarjetas también es vía de expulsión. Gimnasia 1493234: Cingolani, con 5
  amarillas en la competición, entró al descanso por el doble pivote y vio
  dos.
- **Rojas que ninguna lección dice si se podían leer:** Rosario Central
  1493237 (Ávila), Cienciano 1549546 (Amondarain) y Comerciantes 1549547
  (Salinas, al 89'). No tumban: ninguna lección dice que fueran piezas sin
  carga.

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

**Refuerzo 10/11.** Quince lecciones nuevas, y casi todas lo dicen igual:
- **Con ventaja o igualado:** Aston Villa–Man United 1557464 (cinco cambios
  del 71' al 86' con 4-2: dos goles en el añadido), Porto 1575544 (central
  cambiado al 66' con ventaja mínima, gol al 77'), Cerro–Recoleta 1632056
  (cuádruple cambio con 0-0 y dos defensores fuera: gol en el minuto
  siguiente) y Fiorentina–Juventus 1550189 (el cambio para sostener la
  ventaja, en el doble pivote, un minuto antes del 2-2).
- **Persiguiendo, sin el «quién queda atrás»:** Feyenoord–Heerenveen 1552221
  (sale Watanabe al 65': goles al 84' y al 90+3), Man United 1557464 (Maguire
  al descanso: penal al 48' y gol al 53'), Tigres 1551033 (dos rearmes, dos
  concesiones), León y Chivas 1551037 (los dos lados, uno de ellos con uno
  más), Orense 1639833 y Lazio 1550193.
- **El costo de un carril:** Milan–Genoa 1550190 (Musah, carrilero derecho,
  sale al 87' y al 88' marca el carrilero rival que atacaba ese lado, con el
  duelo escrito en el M2).
- Con la roja: Jaguares 1549859 y Gençlerbirliği 1584458 (la línea rehecha
  en minutos).

**En contra 10/11 (contraejemplos, como los de la v1.7):** Barcelona SC
1639804 y Barcelona 1570443 rearmaron y no concedieron. Sostienen que es vía y
no certeza; no van contra el cambio.

**Candidato que suma un caso:** el rearme del doble pivote cuenta como el de
la línea de fondo (Fiorentina 1550189, sin crónica del gol). Uno.

**Comprobación.** Se sostiene si en los veredictos que faltan vuelve a llegar
un gol en contra a pocos minutos de un cambio atrás con el foco ganando o
igualado. Lo tumba si los goles tras un rearme salen siempre de otra zona que
la rearmada: entonces el «quién queda atrás» no es la vía.

**Comprobación 10/11 (8 lecciones de rearme):** **SOSTIENE.**

- **Gol en contra a pocos minutos de un cambio atrás, con el foco ganando o
  igualado:**
  - Sporting Cristal–ADT 1549545: sale un central al 88' con 1-0 y llega el
    empate de pelota parada al 90+4;
  - Defensa y Justicia–Boca 1493231: doble cambio defensivo al 90+1 para
    cerrar el 0-0 y gol al 90+6 por el carril derecho propio. **El rearme para
    administrar también cuesta**;
  - Alianza Lima–Los Chankas 1549551: con ventaja, sale el lateral amonestado
    al 54' y llega el empate al 59'.
- **Observado sin crónica:** Cienciano 1549546 (un central sale al descanso,
  gol al 58').
- **Contraejemplos que confirman «vía, no certeza»:** Rosario Central 1493237
  (roja del central, pero el rival ya no tenía la vía) y La Serena 1505557 (la
  vía del rearme existió y se anuló por un fuera de juego).
- **Lo que podía tumbarlo:** en estas lecciones, ningún gol tras un rearme
  salió de otra zona.

**El candidato del medio sube a tres casos:**
- Fiorentina 1550189 (primer corte);
- Instituto–Newell's 1493236: doble cambio en el medio al 62' y gol al 66';
- Gimnasia–Independiente Rivadavia 1493234: salen los dos del doble pivote al
  descanso y llega el gol 11 minutos después de la expulsión del recambio.

Por la letra de «Cuándo se reabre» (tres casos acreditables en partidos
distintos) entraría. ~~**Propuesta:** sumar al cambio 8 «el rearme del doble
pivote o del medio de contención se escribe como el de la línea de fondo, con
quién queda delante de los centrales».~~ **Decidido por el usuario el
10/11/2026:** candidato, no regla (Gimnasia mezcla el rearme con una roja; sin
ella quedan dos casos limpios, Fiorentina e Instituto). Va a los candidatos del
changelog de la v1.8 y espera un tercer caso limpio.

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

**Refuerzo 10/11.** El conteo a mano sigue saliendo bien (Çorum 1584459,
Zulte Waregem 1558678, Genoa 1550190, Feyenoord 1552221 con dos pares,
Macará 1639805 con el mismo asistidor y definidor) y ninguno fabricó la
jugada. Del (c): Metropolitanos 1646934, el mecanismo de no sostener una
ventaja de un gol fuera, **cuarta vez en el cuadrangular**, aun con siete
cambios en el once. Del candidato de los penales en serie, un tercer caso:
ver el cambio 13.

**En contra 10/11:** ninguna. Nada nuevo para (a) ni (b).

**Comprobación.** Se sostiene si los pares de MECANISMO que traen los
veredictos que faltan vuelven a necesitar la reserva (con diez, autogol,
partido resuelto) para leerse. Lo tumba si ningún par nuevo la necesita: la
reserva sería letra muerta.

**Comprobación 10/11 (3 lecciones de MECANISMO):** **SOSTIENE, con poco.**

- **El conteo a mano salió bien y nadie fabricó la jugada:**
  - Banfield 1493229: dos goles en 3', con el mismo centrador y el central
    rival, sin corrección. Es un MECANISMO de zona;
  - Pereira 1549855: dos goles en 7', con el mismo asistidor; su primer cambio
    fue al 60'.
- **(c):** Pereira es el segundo partido seguido (ante Tolima fueron tres en
  cinco minutos) y va a la rama del próximo rival.
- **(b), la reserva:** aparece una vez y fuera del umbral. Argentinos 1493228:
  dos goles a 23', con la roja en medio, que el cierre anota como vía a
  verificar con su reserva.
- **(a):** sin casos de un cambio de otra zona entre los goles.
- **Candidato (un caso):** el asistidor repetido por la misma banda, por
  debajo del umbral de 15', como vía a verificar (Argentinos 1493228,
  Kalinger). Pereira 1549855 y Macará 1639805 lo tienen dentro del umbral: no
  cuentan.

**Mueve un número:** no.

### 10. El reconvertido también ataca: pasa de candidato a regla — decidido 10/11: sigue candidato

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

**Decidido por el usuario el 10/11/2026:** sigue candidato, no regla (regla
conservadora, la misma vara del rearme del medio del cambio 8: dos casos
limpios —Leones del Norte y Telstar—; Peña Sport es de copa y Cajamarca
1549549 no dice si el lateral nuevo estaba reasignado). La línea de candidato
del M1 suma los casos; pasa a regla con un tercer caso limpio. ~~**Regla
propuesta:** el rol reasignado se escribe con sus dos caras~~ (queda como
texto del candidato).

**10/11:** ningún caso nuevo de un reconvertido que ataque. Lo que traen las
lecciones nuevas del reconvertido es la otra cara (que el mismatch contra él
no está dado): va en el cambio 14.

**Comprobación.** Se sostiene si aparece en lo que falta otro reasignado con
gol o asistencia desde el puesto de hoy. Lo tumba si los reasignados de los
veredictos que faltan solo aparecen como vulnerabilidad.

**Comprobación 10/11:** **SOSTIENE, un caso.** Cajamarca–Alianza Atlético
1549549: el lateral nuevo se leyó solo como vulnerabilidad («la espalda de
Timaná») e hizo el 1-0 llegando al área. El cierre lo anota como caso del
candidato.

Con una reserva: la lección dice «lateral nuevo», no si estaba reasignado.

La otra cara, el reconvertido como vulnerabilidad, se pagó en Talleres
1493239 (ver el cambio 14).

## Cambios nuevos (10/11)

Salen de las 268 lecciones del 08-09/11, que acreditan todas, sumadas a las
del 01-07/11 cuando el candidato ya estaba anotado. Ninguno mueve un número.

### 11. Posesión: el perfil de balón del rival se mide en su condición de hoy

La v1.7 pide la referencia de un rival «del mismo perfil». En siete partidos
nuevos el perfil se tomó bien por su tipo y mal por su **condición**: del
promedio de temporada, de un partido en la otra sede o de la etiqueta del
sistema, y la **dirección** se invirtió.

| Partido | De dónde salió el perfil | Lo que pasó |
|---|---|---|
| OFI–Atromitos 1593356 (los dos lados) | el 54 % de temporada de Atromitos | de visita cedió: 37 %; OFI, escrito «menos pelota», tuvo el 63 % |
| Genk–Union 1558676 (los dos lados) | el 58 % de Genk en Mechelen | en el campo del 3.º, que no cede de local, 46 %; Union 54 % |
| Olympiakos–PAOK 1593357 | la media de PAOK contra otros rivales | de local, ante un 4-4-2 que cedió, 64 % |
| Le Mans–Monaco 1552814 | Troyes, un rival que cedía (61 %) | contra Monaco, que la quiere, 48 % |
| Hoffenheim–Schalke 1575215 | el 40 % de Schalke ante Leipzig | contra un local que cede y sale, 51 % |
| Sport Boys–UTC 1549552 | «el descendido cede» | sin objetivo, no cedió: 48 % |
| Nacional Potosí–Real Potosí 1645538 | «el 5-4-1 cede» (la etiqueta del sistema) | un bloque de cinco que sale de contra no cedió: 47 % |

**Regla propuesta (rúbrica).**
- El perfil de balón del rival es **el de su condición de hoy**: su posesión
  de local o de visita en la competición, y con el objetivo de hoy. Ni su
  promedio de temporada, ni un partido en la otra sede, ni la etiqueta del
  sistema («un bloque de cinco cede»).
- Sin partidos en esa condición, va la dirección con su razón, como ya dice la
  v1.7.

**Contradicción a la vista.** La v1.7 cita a
Paderborn: «con dos equipos que ceden, decide el perfil del rival, no la
sede». Leído como «la sede del foco no decide», no choca: lo que se propone
es que **el perfil del rival se lea en su sede**. Leído como «la sede no
importa», sí choca.

**Decidido por el usuario el 10/11/2026:** se reescribe el ejemplo de
Paderborn con la lectura que no choca (no afloja la v1.7: el perfil del rival
sigue mandando; solo dice en qué sede se lee). Texto viejo y nuevo, exactos, en
«Lista para redactar».

**En contra:** Heerenveen–Feyenoord 1552221 (la referencia era del mismo
perfil y la dirección igual se invirtió; ver el cambio 3).

**Calculable:** la posesión media del rival **por condición** (local y
visita) y con el DT de cada partido, en los insumos del DTP. Es la misma
`posesionReferencias` pendiente desde la v1.7, con la sede adentro.

**Se sostiene si** en los veredictos que faltan la posesión vuelve a
invertirse en partidos donde el rival tiene perfiles distintos de local y de
visita. **Lo tumba si** las inversiones que faltan son de rivales con el mismo
perfil en las dos sedes: entonces la condición no es la causa.

**Comprobación 10/11 (5 lecciones de posesión):** **SOSTIENE.** La dirección
se invirtió cuando el perfil salió de otra condición o de otro objetivo:

- **Audax–Coquimbo 1505555:** la dirección «no salía de un partido de Coquimbo
  de visita ante un local que cede». Audax tuvo el 64 %.
- **Garcilaso–Comerciantes 1549547, los dos lados:** «más pelota» salió del
  4-1 a Los Chankas, un visitante que cedía. El visitante, sin nada en juego,
  no cedió: 49 % y 51 %. El cierre: «la dirección no sale de la sede ni de la
  tabla».

Los dos piden lo que dice el cambio: la condición de hoy, **con el objetivo
de hoy**.

- **Matiza:** Los Chankas–Alianza Lima 1549551. El rival llegó sin Vélez ni
  R. Garcés y no se impuso (51 % contra 49 %): la condición de hoy incluye
  también las bajas del rival.
- **Lo que podía tumbarlo:** ninguna inversión de un rival con el mismo
  perfil en las dos sedes. No apareció.

**Mueve un número:** no. La magnitud sigue sin calibrarse.

### 12. El lateral o el defensor fresco que llega es banco ofensivo (de candidato a regla)

El 08/11 quedó como candidato con dos casos (Başakşehir 1584463: Bulut asistió
el gol decisivo; Bolívar 1645531: Rivero, defensor que entró al 65'). Las
lecciones nuevas suman cuatro partidos, todos acreditables:
- **Man United–Aston Villa 1557464:** Dorgu, que entró al 66' como lateral,
  asistió el 3-4 e hizo el 4-4; no estaba en la lista del banco.
- **Bucaramanga 1549859:** la asistencia del 0-3 la dio Hinestroza, lateral
  entrado al 63'.
- **Porto–Vitória 1575544:** el gol del triunfo, de Martim Fernandes, lateral
  que entró al 58' por un extremo y no estaba en el banco nombrado.
- **Chivas–León 1551037:** el empate de León llegó de un defensor entrado
  (Bellón), asistido por un central, cuando la rama nombraba solo atacantes.

**Regla propuesta (rúbrica):** el banco ofensivo por rol incluye al **lateral
o carrilero fresco que llega** y, en la rama persiguiendo, al **defensor que
entra a cargar el área**. No es todo el banco: es el que por su rol de hoy
llega al área rival.

**Calculable:** en `bancoOfensivo` (pendiente), con el rol de la hoja; el
lateral entra si su último partido lo tuvo de lateral o carrilero.

**Se sostiene si** en los veredictos que faltan vuelve a marcar o asistir un
lateral o defensor entrado. **Lo tumba si** no aparece ninguno y las listas
crecen sin acertar más (la lista se vuelve el banco entero).

**Comprobación 10/11:** **SOSTIENE, dos casos.**

- **Cobresal–U. de Chile 1505560:** Sandoval, defensor que entró al descanso,
  asistió el descuento al 90+2.
- **Pereira–Nacional 1549855:** E. Moreno, defensa que entró al 86', asistió
  el 3-2. No estaba en el banco nombrado.

Los dos son del que persigue o va igualado, como dice la regla.

**Mueve un número:** no.

### 13. Los penales concedidos en serie son del equipo, no de una línea — decidido 10/11: candidato

Candidato desde la v1.7 (La Guaira 1646922), con un segundo caso el 08/11
(Portuguesa–La Guaira 1646930: «tercer penal concedido en dos partidos ante
el mismo rival», con otra línea). Tercer caso, de otro equipo:
**Universitario–UCV Moquegua 1549553** (segundo partido seguido en que la U
concede un penal en el Monumental, el 05/11 y hoy al 78', con líneas
parecidas).

**Regla propuesta (rúbrica):** un equipo que concedió penales en dos partidos
seguidos lleva **«penal en contra»** en las vías del rival como vía **del
equipo**, sin atarla a una línea ni nombrar al infractor sin crónica. Sigue
siendo vía a verificar: no degrada K ni baja un veredicto.

Llega a tres casos, pero dos son del mismo cruce del cuadrangular venezolano y
los tres están sin crónica. Por la letra de «Cuándo se reabre» (tres casos
acreditables en partidos distintos) entra; por el espíritu (tres equipos
distintos) no. **Decidido por el usuario el 10/11/2026:** candidato, no regla
(dos de los tres son del mismo cruce); espera un caso de otro equipo. ~~**Regla
propuesta (rúbrica)**~~: queda como texto del candidato, en la línea de
candidatos del MECANISMO-ABIERTO.

**Calculable:** los penales concedidos por el equipo en sus últimos
partidos, de los eventos (`Penalty` del rival), en los insumos del DTP.

**Se sostiene si** en lo que falta un equipo con dos partidos seguidos
concediendo penal vuelve a conceder. **Lo tumba si** los que vienen de dos
seguidos no conceden en el tercero, en varios equipos.

**Comprobación 10/11:** **SIN CASOS.** Ninguna lección habla de un equipo con
penales concedidos en serie. (Decidido el 10/11: candidato, ver arriba.)

**Mueve un número:** no.

### 14. Un reconvertido o una línea nueva es vía a verificar, no un mismatch dado (de candidato a regla)

Candidato del 08/11 con Getafe 1570438 y Lille y Bodø 1635640 (dos de los tres
eran del mismo partido). Suma un tercer partido, de los dos lados:
**Napoli–Lazio 1550193**. La Lazio apoyó el FAVORABLE de igualado en el 2
contra 1 sobre el carrilero reconvertido del Napoli y generó 0,92 contra
2,44; el cierre del Napoli lo dice desde el otro lado: «un bloque improvisado
de local con De Bruyne y McTominay no pierde el volumen por la reconversión
de un carril». Con el candidato de la v1.7 (el mismatch contra un lateral
suplente que nadie ataca, Lille–Lens), es la misma idea.

**Regla propuesta (rúbrica):** un mismatch contra un reconvertido, un lateral
suplente o una línea nueva **sostiene un FAVORABLE solo si la vía que lo ataca
está nombrada** (quién, por dónde y qué remate sale de ahí). Sin eso, va como
vía a verificar y la rama no sube por él. Es la misma vara del cambio 1: la
superioridad en una zona dice cómo termina en remate.

**Encaja con el cambio 10**, no lo contradice: el reconvertido tiene dos caras
y ninguna está dada.

**Se sostiene si** en lo que falta otro FAVORABLE apoyado en un reconvertido
rival no genera. **Lo tumba si** los FAVORABLE apoyados en un reconvertido
generan más que los demás en los veredictos que faltan.

**Comprobación 10/11:** **MATIZA.**

- **Unión La Calera–Huachipato 1505562:** la línea de tres del rival, con dos
  reconvertidos (P. Vargas, Toro), le dio a La Calera 1,44 de xG, con 13 de 16
  remates en el área. El cierre dice que la rama, dada NEUTRO «por nivel», era
  FAVORABLE por el área. El mismatch contra la línea nueva **sí pagó**.
- **Talleres–Estudiantes 1493239:** la vuelta escrita contra Schott, central
  reconvertido a lateral, fue la jugada del 0-1.

Ninguno es un FAVORABLE apoyado en un reconvertido que no generó, ni uno que
generó más que los demás. No apareció lo que lo sostenía ni lo que lo
tumbaba.

Lo que agregan es la mitad de la regla que el cambio deja entre líneas:
**con la vía que lo ataca nombrada, el mismatch sí sube la rama**. Talleres la
tenía nombrada y pagó; La Calera no la escribió y la rama quedó corta.

**Propuesta de redacción:** «…sostiene un FAVORABLE solo si la vía que lo
ataca está nombrada; con la vía nombrada, la rama sube por él».
**Decidido por el usuario el 10/11/2026:** con esa redacción (la vía nombrada
hace subir la rama; sin ella, vía a verificar).

Sport Huancayo–Cienciano 1549546 (el caso de la 6 era con otra línea) es la
misma idea del lado del bloque, y eso ya es v1.7 (g).

**Mueve un número:** no.

## Cambios nuevos del segundo corte (10/11, 04:29 UTC)

### 15. La vía de la rama persiguiendo tiene que sobrevivir a los cambios del DT

Sale de las 118 lecciones del segundo corte. Son tres partidos, los tres
acreditables:

- **Huachipato–Unión La Calera 1505562:** la rama persiguiendo salió NEUTRO
  con sus vías (el centro de Briceño, la media distancia de Altez, la pelota
  parada y el banco). Altez salió al 45' y Briceño al 59'. En 67 minutos
  persiguiendo hubo un remate al arco y 0,35 de xG. El cierre: «una rama cuyas
  vías dependen de piezas que el DT suele cambiar pronto, contra un local que
  no cedió la pelota, es DESFAVORABLE».
- **Alianza Atlético–Cajamarca 1549549:** la vía escrita (segunda línea,
  centros de Gordillo, media distancia de Lupú) salió del campo al descanso
  con los tres. En todo el partido hubo un remate al arco. El cierre: «sin vía
  nombrada que sobreviva a los cambios, la rama persiguiendo es
  DESFAVORABLE».
- **Palestino–La Serena 1505557:** la vía principal (Montes entre líneas)
  se apagó cuando salió al 63'. La rama quedó con Gallegos y el banco, y
  generó un remate al arco. Es un acierto: el veredicto estaba bien, y la
  lección es la misma.

La v1.7 ya dice que una rama sin vía contra el bloque rival es DESFAVORABLE.
Lo que no dice es **dónde mirar**: las vías se escriben con el once de
arranque, y el que persigue suele cambiar primero, justamente, a las piezas
que las sostienen.

**Regla propuesta (rúbrica).**
- En la rama persiguiendo, el M2 cruza sus vías con el M3. Si las piezas que
  las sostienen son las que el DT de hoy suele cambiar primero, o están
  amonestadas, la razón dice **qué vía queda después de los cambios**, con el
  nombre del suplente que la hereda.
- Si no queda ninguna, la rama es DESFAVORABLE, que es lo que ya dice la v1.7.
- Sin minuto fijo y sin umbral, como el banco del cambio 5.(b).

**Encaja con** el cambio 2.(a) (la razón cita la vía por su renglón), con el
cambio 8 (quién queda atrás después de los cambios; este es el espejo, quién
queda adelante) y con el 12 (el banco que hereda la vía).

**Calculable (pendiente de la app):** el minuto habitual de salida de cada
titular con el DT de hoy, de los eventos `subst` de sus últimos partidos, en
los insumos del DTP. Va al lado de `bancoOfensivo`.

**Se sostiene si** en los próximos cierres vuelve a apagarse la rama
persiguiendo cuando salen las piezas de sus vías. **Lo tumba si** las ramas
persiguiendo cuyas piezas salen temprano generan lo mismo que las demás: en
ese caso, el banco que entra hereda la vía y el cruce no agrega nada.

**Mueve un número:** no.

### 16. APROBADO (10/11, incidencia 1056): el TDE hereda el seguro persiguiendo del DTP

**Estado: APROBADO por el usuario el 10/11/2026.** Es la contraparte del
cambio 14 del TDE v0.1.26 (`docs/revisiones/TDE_v0.1.26_propuesta.md`). La
disciplina 63 del TDE (v0.1.23) ya manda que el `sob2` de las ramas del que
persigue salga del `nivelFocoPersiguiendo` del DTP. Pero el DTP vigente decía
que eso no se hereda hasta que el usuario decida. Los dos skills se
contradecían, y la app hacía lo que decía el DTP.

**Los casos** están en la propuesta del TDE: Westerlo–Charleroi 1558679,
Konyaspor–Galatasaray 1584465 y Como–Inter 1550191. Los tres partes lo
hicieron bien a mano.

**(a) Integración, el texto que se reemplaza.**

El texto viejo (`docs/skills/diagnostico-tactico/SKILL.md`, Integración,
«Hacia el módulo del tramo final», exacto):

> *(v1.5)* El SOB2 **sigue heredando el nivel de hoy** del seguro (`nivelFoco`/`nivelRival`); la rama persiguiendo (`nivelFocoPersiguiendo`/`nivelRivalPersiguiendo`) se declara pero no se hereda hasta que el usuario decida si el SOB2 sale de ella.

El texto nuevo:

> *(v1.5)* El SOB2 **sigue heredando el nivel de hoy** del seguro (`nivelFoco`/`nivelRival`) fuera de las ramas del que persigue. *(v1.8)* El TDE hereda `nivelFocoPersiguiendo` en las ramas del que persigue; HERENCIA-DTP avisa si difiere — aprobado 10/11, incidencia 1056. Si el que persigue es el rival, la fuente es `nivelRivalPersiguiendo`, como dice la disciplina 63 del TDE.

**(b) El arrastre en M2.** La línea del rest defense del M2 termina con «Lo
que hereda el TDE no cambia», y con el (a) eso deja de ser cierto. Si no se
cambia, el skill se contradice solo.

El texto viejo (M2, línea del rest defense, final, exacto):

> Lo que hereda el TDE no cambia: ver Integración.

El texto nuevo:

> Desde la v1.8 el TDE también hereda la rama persiguiendo: ver Integración.

**Decidido por el usuario el 10/11/2026:** el arrastre entra con el (a) (regla
conservadora: sin él el skill se contradice).

**Para la app:** que `HERENCIA-DTP` compare también el `sob2` de la rama. En
el TDE figura como «aprobado y pendiente de la app» desde la v0.1.25. El
alcance (si se recalculan o no los partes viejos) es el que fija el cambio 14
del TDE, no este.

**Mueve un número:** no. El nivel del seguro ya se declaraba; lo que cambia
es de dónde lo lee el TDE.

## El modo de fallo `lectura_efe`, uno por uno

Jev puso `lectura_efe` en **46 lecciones pendientes del DTP** (26 de lados
fallados y 20 parciales): 38 del 01-07/11 y **8 nuevas** del 08/11. (El
`porModoFallo` del dossier dice 58, pero cuenta otra cosa: los lados fallados
de la cohorte, no las lecciones.)

**Las 46 son del DTP. Ninguna es del EFE.** Ninguna nombra un bloque, un
sub-score, la F1 ni la clasificación del EFE; la única que menciona algo
parecido (Tijuana 1551030: «DTP-REHACER tardío, la API corrigió la
formación») habla del once, no del EFE. Por la regla que citan:

| Regla del DTP que citan | Lecciones | Las 8 nuevas | Cambio de esta propuesta |
|---|---|---|---|
| M2 · veredicto por rama (vía entera, sin vía → DESFAVORABLE, condición) | 21 | Barcelona SC 1639804, Levante 1570444, Chelsea 1557466, Man United 1557464, Monterrey 1551034 | 1.(a) y 2 |
| M5 · volumen y conversión | 11 | — | 1 |
| Posesión por rama | 5 | OFI 1593356 | 3 y 11 |
| Checklist del bloque · la 6 | 3 | Aston Villa 1557464 (la línea del caso cambió en dos de cuatro) | ya es v1.7 (5.(g)) |
| Banco ofensivo | 2 | Heerenveen 1552221 (el titular rotado) | 5 y 12 |
| Vías (quinta línea) | 2 | — | candidato «presión con su vuelta» |
| Duelos por carril | 1 | — | ya es v1.5 |
| M3 · rearme | 1 | — | 8 |

**Para el EFE (no son regla del DTP).** Fuera de la etiqueta, tres lecciones
del DTP leen al EFE como fuente: UCV Moquegua 1549553, Levadiakos 1593348 y
Táchira 1646932. En las tres la caja de sensibilidad del EFE anunciaba otra
línea u otro once, y **el que falló fue el DTP** (la regla de las dos
variantes es de la v1.6: cambio 6.(c)). Lo único que le tocaría al EFE es de
forma: que la caja de sensibilidad escriba la línea alternativa con su sistema
y la pieza que entra, de modo que la app pueda compararla con el M1. Se anota
para la revisión del EFE, no acá. Y Rennes–Lille 1552816: la alerta
EJE-DEBUTANTE del EFE (Oliveira por Rouault) era la señal de que la línea del
caso de la 6 había cambiado; cruzarlas es de la app.

**Era del usuario** (ya estaba en «Lo que NO se propone»): un
casillero propio del DTP en la taxonomía de Jev (`lectura_dtp`) o redefinir
`lectura_efe` como «lectura del skill». Con 46 de 46 mal etiquetadas, el
`porModoFallo` del DTP no dice nada útil hoy. **Decidido por el usuario el
10/11/2026:** no se cambia en esta revisión (regla conservadora: es código de
`modo_fallo.py`, la taxonomía es cerrada y lo sellado no se re-etiqueta; la
propuesta no recomendaba). Es la A0 del EFE v1.10; si allá se decide, vale
para los tres skills.

## `rolesVsGrid`: lo que dicen las lecciones

`ROLES_GRID_REHACE` sigue en `False` (`backend/analisis/dtp_cowork.py`), y la
medición del 05/11 dio 9 reales y 0 falsos (incidencia 1232,
`docs/DEUDA.md` punto 20).

**Las lecciones no alcanzan para contar sus hallazgos.** Solo una de las 1032
nombra `rolesVsGrid`: Belgrano–Gimnasia 1493233 (05/11), **real** (marcó a
Benítez y la pareja Ricca–López, el rehacer no tocó a Belgrano y el descuento
fue de Benítez por la banda que el mapa tenía al revés). City 1635710 lo trae
como `contraElOnce`, también real.

**Lo que sí traen:** cuatro rehacer nuevos con el grid ya capturado y el rol
leído al revés, que el cierre comprobó contra la ficha y son reales por
definición: Beşiktaş 1584458, Le Havre 1552813, Rayo 1570449 y América de
Cali 1549854 (cambio 6.(a)). Ninguna lección cita un hallazgo de
`rolesVsGrid` que haya resultado falso.

**Medición para decidir (calculable, 0 tokens):** cruzar
`contraElOnce.rolesVsGrid` de esos cuatro partidos y de Belgrano y City.
- Si los marcó, son hallazgos reales que la corrida no rehízo: suman a los 9
  del 05/11.
- Si no los marcó (Rayo es de sistema, no de rol, y le tocaría a
  `M1-VS-ONCE-OFICIAL`), es su techo de cobertura.

En cualquiera de los dos casos, **nada de las lecciones va en contra de
promoverlo**. **Decidido por el usuario el 10/11/2026** (regla conservadora,
la propuesta no recomendaba): `ROLES_GRID_REHACE` sigue en `False` hasta que
se haga esa medición cruzada; con ella a la vista se vuelve a proponer. No toca
el `SKILL.md`.

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

**Actualización 10/11: verificado en el código.** Con `grep` sobre `backend/`,
`src/` y `docs/openapi.yaml` (rama del 10/11, desde `origin/main` 60ba263),
**lo pendiente del DTP en `docs/revisiones/PENDIENTES.md` sigue sin hacerse**:
no existe ninguno de `P6-OTRA-LINEA`, `M1-VS-ONCE-OFICIAL`, `bancoOfensivo`,
`DTP-BANCO-UN-LADO`, `DTP-PENAL-EJECUTOR-FUERA`, `M2-RAMAS-ESPEJO`,
`casoBloquePropuesto`, `posesionReferencias`, `minutosEnDiferencia`,
`cubreRama`, `rearmes` ni los córners concedidos; tampoco el volumen dentro del
área en ningún módulo, ni los pares de MECANISMO (el backend solo marca
`mecanismoAbiertoCandidato` con ≥ 2 goles recibidos). `rolesVsGrid` existe, en
sombra (`ROLES_GRID_REHACE = False`). Lo que las 268 nuevas le suman a cada
uno:

| Pendiente (de PENDIENTES.md o del 08/11) | Casos nuevos del 08-09/11 |
|---|---|
| `bancoOfensivo` y `DTP-BANCO-UN-LADO` | Heerenveen 1552221, Asteras 1593354, Kortrijk 1558673 (fuera de la hoja), Rayo 1570449, PSV 1552219, Porto 1575544, Le Havre 1552813, Cruz Azul 1551033 y los cuatro del cambio 12 |
| `penales[]` con quién entra y `DTP-PENAL-EJECUTOR-FUERA` | los seis del cambio 5.(c) y los tres de muestra mínima |
| `M1-VS-ONCE-OFICIAL` | Beşiktaş 1584458, Le Havre 1552813, Rayo 1570449, América de Cali 1549854 |
| `P6-OTRA-LINEA` y `casoBloquePropuesto` | Aston Villa 1557464 (la línea del caso cambió en dos de cuatro), Rennes 1552816 (un central cambiado), Gent–Kortrijk 1558673 (el checklist respondió por una zaga que no jugó); y al menos 15 cierres que escribieron a mano el caso de la 6 para la apertura siguiente (Inter 1550191, Puebla 1551036, Brest 1552812, Sunderland 1557466, UTC 1549552, Toluca 1551034, Bournemouth 1557462, entre otros) |
| M5 con volumen dentro del área (`dtp.porBloque[].volumen`, `cubreRama`) | las 58 del cambio 1; y Trinidense 1632061 («la ficha no parte la posesión por tramo») |
| Pares de MECANISMO a ≤ 15' | Çorum 1584459, Zulte Waregem 1558678, Genoa 1550190, Feyenoord 1552221, Macará 1639805 |
| `minutosEnDiferencia` | Beşiktaş 1584458, Brighton y Brentford 1557458, Oriente Petrolero 1645540, Jaguares 1549859, Chivas 1551037, Nacional Potosí 1645538 |
| `M2-RAMAS-ESPEJO` | Atlético–Barcelona 1570443 (el primero) |
| `rearmes` | los quince del cambio 8 |
| `posesionReferencias` | los siete del cambio 11, ahora **por condición** |

**Nuevo del 10/11, para la app:**
- **`posesionReferencias` por condición** (local y visita) y con el DT de
  cada partido (cambio 11).
- **El rol de la hoja en `bancoOfensivo`**, para que entren el lateral y el
  carrilero frescos (cambio 12).
- **Los penales concedidos por el equipo en sus últimos partidos**, de los
  eventos (cambio 13).
- **EJE-DEBUTANTE del EFE contra `casoBloque.linea`**: si el EFE del mismo
  parte marca un debutante en la línea del caso, aviso de que la 6 se mira de
  nuevo (Rennes 1552816).
- **El cruce de `rolesVsGrid` con los cuatro partidos del cambio 6.(a)**: es la
  medición para decidir `ROLES_GRID_REHACE` (ver su sección).

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
  `ROLES_GRID_REHACE`: decidido el 10/11, sigue en `False` hasta la medición
  cruzada (ver «`rolesVsGrid`»). En la ventana lo marcó en Belgrano 1493233 y
  City 1635710.
- **El rest defense cambia con los cambios** (Monagas–Caracas 1646928: el doble
  pivote del seguro estaba fuera al 68'). Si se mide, es del TDE (SOB2 del tramo
  final), no del DTP. Un caso.
- **10/11, once tardío y su reverso.** Siguen los onces corregidos por la API
  después del pitazo (Real Sociedad 1570449, Orense 1639833, Tigres 1551033,
  Cerro 1632056, Toluca 1551034, Santa Fe 1549862, The Strongest 1645539,
  Anderlecht 1558672: 7 minutos antes del pitazo). Y uno al revés: Alianza
  Valledupar 1549853, donde **el rehacer empeoró** una apertura buena por un
  dato de la API que se corrigió después. Es `dato_api`; si se repite, es una
  incidencia para la rutina de rehacer, no para el skill.
- **10/11, sin stats:** Carabobo–La Guaira 1646935 (Venezuela otra vez); la
  regla «no evaluable por volumen» se aplicó bien.

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
- ~~**La herencia del SOB2 desde la rama persiguiendo:** sigue siendo una
  decisión del usuario.~~ **Decidido el 10/11:** aprobada, es el cambio 16.
- **`ROLES_GRID_REHACE`:** la medición está hecha (incidencia 1232).
  **Decidido el 10/11:** sigue en `False` hasta la medición cruzada de
  «`rolesVsGrid`» (regla conservadora).
- **El casillero del DTP en la taxonomía de Jev** (`lectura_dtp` o
  redefinir `lectura_efe`): ninguna de las 38 etiquetas `lectura_efe` habla
  del EFE. Es código y toca cómo se agrupan los fallos. **Decidido el 10/11:**
  no se cambia en esta revisión (regla conservadora; es la A0 del EFE).
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
- **10/11, lo que cambió en esta lista:**
  - suben a regla el lateral o defensor fresco como banco ofensivo (cambio
    12) y la línea nueva o el reconvertido como vía a verificar (cambio 14);
    los penales concedidos en serie (cambio 13) **siguen candidato** por
    decisión del usuario del 10/11 (dos de los tres casos son del mismo cruce);
  - **decidido el 10/11, siguen candidatos:** el rearme del doble pivote o del
    medio (cambio 8: dos casos limpios, Fiorentina 1550189 e Instituto
    1493236; Gimnasia 1493234 mezcla una roja) y el reconvertido que ataca
    (cambio 10: Leones del Norte y Telstar 1552214; Cajamarca 1549549 con
    reserva);
  - candidatos nuevos, sin regla: una presión alta como vía a favor se
    escribe con su vuelta, qué pasa si la salida la supera y qué seguro queda
    (Utrecht–NEC 1552223 y Lille–Bodø 1635640: dos); el rearme del doble
    pivote cuenta como el de la línea (Fiorentina 1550189: uno, sin crónica);
    el segundo de la lista de penales que es el que recibe la falta
    (Panathinaikos 1593355: uno); y el FAVORABLE de igualado que dura minutos
    contra un rival armado para correr por la vuelta nombra qué seguro la
    cubre (Querétaro 1551036, con el Juárez de la v1.7: dos, y queda dentro
    del cambio 1.(a));
  - siguen igual el MECANISMO activo que baja el veredicto, el rest defense
    «sin» que impide un FAVORABLE persiguiendo, el caso de la 6 con el arquero
    que lo sostuvo, «lo sostuvo el rival fallando», el seguro en la pelota
    parada propia, un cambio atrás por vez, la pregunta 5 con ventaja
    temprana, guardar los cambios en el tercer partido en ocho días y el 1-0
    once contra once: ninguna lección nueva les suma.
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
- **Cuando el usuario decida** el SOB2 desde la rama persiguiendo
  (**decidido el 10/11: cambio 16, aprobado**),
  `ROLES_GRID_REHACE` (1232; **10/11: sigue en `False` hasta la medición
  cruzada**) o el casillero de Jev (**10/11: sin cambio; A0 del EFE**).
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
| 11 | `posesionReferencias` por condición (local y visita) y con el DT de cada partido | calculable |
| 12 | el rol de la hoja en `bancoOfensivo` (laterales y carrileros frescos) | calculable |
| 13 | penales concedidos por el equipo en sus últimos partidos, de los eventos (ayuda para juntar casos del candidato; decidido 10/11: no es regla) | calculable |
| 14 | — | rúbrica pura |

Lo calculado se calcula al leer, como el resto de lo derivado. Ninguno de
estos campos toca el motor ni un número calibrado. Los puntos 2.(b), 2.(c),
3, 4.(b), 5.(b), 5.(c), 6.(b), 7, 8, 9.(c) y 10 son rúbrica pura; del 10/11,
el 14 y la regla de los cambios 11 a 13 (lo calculable de esos tres es la
ayuda, no la regla).

## Cómo se aplica si se aprueba

1. ~~El usuario aprueba o corrige punto por punto.~~ **Hecho el 10/11/2026**
   (ver «Decisiones del 10/11»):
   - el 1.(a): entra, y con el caso NEC 1552223 manda la diferencia de volumen;
   - el 10: sigue candidato;
   - el 11: entra, con el ejemplo de Paderborn reescrito;
   - el 13: candidato;
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
6. Se cierran con 🔑 las anteriores a la v1.8 (al 10/11, las 1032 pendientes
   más las que dejen los veredictos del 08-09/11 que se estaban cerrando).
   Las 18 de copa y las 10 de cuarentena cierran igual, porque fijaron
   rúbrica. Sigue pendiente cerrar
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

**Las 268 nuevas (08-09/11), con la tabla de «Actualización 10/11».** Todas
acreditan; ninguna es de copa ni de cuarentena.

| Punto | Grupos de lecciones | Lecciones | Fallos | Parciales | Aciertos |
|---|---|---|---|---|---|
| 1 (y 14) · Volumen de los dos lados | M5 | 58 | 24 | 10 | 24 |
| 2 · Rama con su contrario; ceder no es señal | veredicto por rama | 42 | 10 | 9 | 23 |
| 3 y 11 · Posesión | posesión | 13 | 6 | 2 | 5 |
| 4 · Pelota parada; media distancia | pelota parada | 3 | 1 | 0 | 2 |
| 5 y 12 · Banco y penales | banco, penales | 45 | 13 | 5 | 27 |
| 6 · Grid; rehacer | M1, DTP-REHACER | 17 | 5 | 1 | 11 |
| 7 · Expulsión | (dentro de M1) | — | — | — | — |
| 8 · Quién queda atrás | rearme | 15 | 5 | 4 | 6 |
| 9 y 13 · MECANISMO | MECANISMO-ABIERTO | 7 | 4 | 0 | 3 |
| Confirman sin cambio (checklist, vías, carril, M6, otras) | | 68 | 16 | 6 | 46 |
| **Total** | | **268** | **84** | **37** | **147** |

## Cambio adicional (08/11, pedido del usuario): la génesis del gol

**Pedido:** «al DTP le falta la teoría de cómo llegó el gol». **Base:**
`docs/revisiones/DTP_autopsia_gol_estudio.md` (15 partidos de la semana,
45 goles, 36 con crónica que nombra la jugada). Se aprueba aparte de los
puntos 1 a 10. **Decidido por el usuario el 10/11/2026:** entra entera (la
recomendación de la propuesta), con las dos correcciones de la tabla (b) del
«Refuerzo 10/11». Mientras no se aplique el núcleo, la tabla de fuentes va
dentro del M4 del `SKILL.md`, fechada. **Ningún número del skill se mueve**: no hay umbral, peso ni
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

### Refuerzo 10/11 de la génesis del gol

- **«Sin crónica» sigue siendo lo normal, y sin buscarla.** 24 lecciones
  nuevas de 22 partidos dicen «sin crónica de la jugada» (Cerro 1632056,
  Nacional y Real Potosí 1645538, Inter 1550191, Lorient 1552813, AZ 1552224,
  Atlético 1570443, PAOK 1593357, Tigres 1551033, León y Chivas 1551037,
  Orense 1639833, Universitario 1549553, entre otros) y **ninguna cita una
  página abierta**. La disciplina de no fabricar la jugada se cumplió en todas;
  el protocolo (b) no existe todavía en el skill y no se aplicó. Varias son de
  ligas de la tabla (b) con más de 48 horas (Serie A, Bundesliga, Liga MX):
  es el caso del aviso (d).4.
- **Lo que la ficha ya pre-etiqueta, (d).3:** autogoles que decidieron la
  lectura del volumen (Santa Clara 1575542, Lazio 1550193 con el que entró,
  Jaguares 1549859, Barcelona SC 1639804) y goles de suplentes entrados
  (los del cambio 12 y la lista de «Lo que acierta»). Saldrían sin juicio.
- **(c).4, el ejecutor del día:** los seis partidos del cambio 5.(c) son el
  mismo hueco que Monterrey y Toluca en el estudio.

**En contra 10/11:** ninguna.

**Comprobación.** Se sostiene si los veredictos que faltan siguen trayendo
el M4 sin jugada en ligas con fuente de la tabla (b) y más de 48 horas. Lo
tumba si, buscando con la tabla, los cierres no encuentran crónica fuera de los
15 partidos del estudio: el protocolo no rendiría y quedaría solo la
categoría «sin fuente».

**Comprobación 10/11:** **SOSTIENE y MATIZA la tabla (b).**

- **Donde se buscó en la lista, apareció la crónica:**
  - Banfield–Tucumán 1493229: Contexto Tucumán. Trae el tiro libre directo de
    L. Gómez, que no estaba en la vía: es el (c).5;
  - Boca–Defensa 1493231: El Gráfico. Trae el gol de Valencia en el rebote;
  - La Serena–Palestino 1505557: la encontró en Redgol.

  Lo que tumbaba (buscar con la tabla y no encontrar) no apareció.
- **Dos correcciones a la tabla (b), con un caso cada una:**
  - **El Gráfico respondió**, y la tabla dice que da 403;
  - **falta Chile**, y Redgol sirvió.

  **Decidido el 10/11:** entran las dos, en una tabla que es fechada (no es una
  regla: dice dónde buscar primero). El Gráfico pasa a «Si no sale» como
  probado una vez; Chile entra con Redgol y «sin medir más». La tabla nueva,
  exacta, en «Lista para redactar».
- **«Sin crónica» sigue** en Argentinos 1493228, La Calera 1505562,
  Melgar–Juan Pablo II 1549548, Pereira 1549855 y Cienciano 1549546. Ninguno
  fabricó la jugada. Ninguno cita una página abierta.

## Comprobación con los veredictos del 08-09/11

El dossier se cortó a las 02:13 UTC del 10/11 con unos 50 veredictos del
08-09/11 todavía cerrándose. Cada cambio lleva su línea «Se sostiene si… / Lo
tumba si…» dentro de su punto; en corto:

| Cambio | Se sostiene si… | Lo tumba si… |
|---|---|---|
| 1 | los FAVORABLE fallados son los que concedieron tanto como generaron o remataron de afuera | hay FAVORABLE con mucho más generado que concedido, en el área, cobrados como fallo de mapa |
| 2 | siguen las ramas con gol por un renglón de la lista no citado, o sin vía dadas NEUTRO | las ramas con la lista entera fallan igual que las recortadas |
| 3 | la posesión de «igualado o arriba» vuelve a fallar con gol temprano del foco | falla igual sin gol temprano |
| 4 | la pelota parada del que cede vuelve a quedarse sin córners | los que ceden convierten de pelota parada con pocos córners en varios partidos |
| 5 | vuelve a patear un suplente o el 9 que entra por el ejecutor | los penales los patea siempre el primero de la base en cancha |
| 6 | los rehacer vuelven a apartarse del grid ya capturado | los M1 copian el grid y los carriles fallan igual |
| 7 | hay rojas de piezas del seguro o de la línea sin cargar en el M1 | las rojas son de piezas sin amarillas ni papel en el duelo |
| 8 | llega un gol a pocos minutos de un cambio atrás con el foco ganando o igualado | los goles tras un rearme salen siempre de otra zona |
| 9 | los pares nuevos necesitan la reserva para leerse | ninguno la necesita |
| 10 | otro reasignado marca o asiste desde el puesto de hoy | los reasignados solo aparecen como vulnerabilidad |
| 11 | la posesión se invierte con rivales de perfiles distintos por sede | las inversiones son de rivales con el mismo perfil en las dos sedes |
| 12 | marca o asiste otro lateral o defensor entrado | ninguno, y las listas crecen sin acertar más |
| 13 | un equipo con dos seguidos concediendo penal concede en el tercero | los que vienen de dos seguidos no conceden, en varios equipos |
| 14 | otro FAVORABLE apoyado en un reconvertido rival no genera | esos FAVORABLE generan más que los demás |
| Génesis | sigue el M4 sin jugada en ligas con fuente y más de 48 h | buscando con la tabla, no aparece crónica fuera del estudio |

Lo que se mira es el texto de las lecciones nuevas, no una tasa: por el
sesgo de atribución, un conteo de «se sostiene» no es un acierto del skill.

**Hecho el 10/11 con el corte de las 04:29 UTC** (118 lecciones, 113
acreditables): el resultado va en la «Comprobación 10/11» de cada cambio y en
la «Tabla de cambios» del final.

## Núcleo e historial

`docs/revisiones/NUCLEO_SKILLS_propuesta.md` (03/11) **no se aplica acá**.
Para cuando se aplique, esto es lo que cada cambio deja en el núcleo (arriba
del `SKILL.md`, lo que la corrida necesita para analizar) y lo que va al
historial (`references/HISTORIAL.md`: casos, de dónde salió, conteos):

| Cambio | NÚCLEO (va al módulo, en una o dos frases) | HISTORIAL |
|---|---|---|
| 1 | M5: el veredicto de la rama jugada se juzga por lo generado **contra** lo concedido, en el área primero; la referencia de volumen, de la misma sede y perfil, nunca de un partido ni de una racha; los penales al lado del xG. M2: el FAVORABLE apoyado en una zona escribe quién remata en el área | las tablas de casos (13 del 08/11 y los del 10/11), el caso NEC |
| 2 | M2: la razón de cada rama cita los renglones de `viasGol`; el veredicto con condición lleva su contrario (`siNo`); ceder no es señal en ninguna dirección | los once casos de vía recortada, los ocho de condición, los cuatro de ceder |
| 3 | M2 posesión: «igualado» y «arriba» aparte cuando el foco puede ponerse arriba temprano; DT nuevo y copa de otra categoría no son referencia | la tabla de ocho partidos |
| 4 | M2 vías: la pelota parada del que cede va condicional; la media distancia en los dos lados con todos sus rematadores | la tabla de córners |
| 5 | M2: ningún nombre en el XI y en el banco; el banco sin minuto fijo; la lista de penales con tercer nombre «si entra» y quién patea después de un errado (puede ser el mismo) | los 22 partidos de la lista, los seis de penales del 10/11 |
| 6 | M1: el sistema es la formación de la ficha y el rol sale de la fila del grid; una coordenada citada existe. Modo `rehacer`: se reescribe todo lo que nombra piezas | los catorce del 08/11 y los cuatro del 10/11 |
| 7 | M1/M2: la vía de expulsión de los dos lados, con todas las piezas de la línea del duelo y la vuelta de suspensión | Málaga, Frankfurt, River y los tres del 10/11 |
| 8 | M3: quién queda atrás después de los cambios en todas las ramas; lateral y extremo de la misma banda = costo del carril | los quince del 10/11 |
| 9 | M4/MECANISMO: qué es una corrección, la reserva del par, `sin mecánica` repetido a la rama donde se dio | los casos por reserva |
| 10 | — (decidido 10/11: candidato; va al changelog, no al módulo) | Leones del Norte, Peña Sport, Telstar, Cajamarca |
| 11 | M2 posesión: el perfil del rival en su condición de hoy, no el promedio ni la etiqueta del sistema | la tabla de siete partidos, la pregunta de Paderborn |
| 12 | M2 banco: el lateral o carrilero fresco y, persiguiendo, el defensor que entra a cargar | los seis partidos |
| 13 | — (decidido 10/11: candidato) | La Guaira, Portuguesa, Universitario |
| 14 | M2: un mismatch contra reconvertido, suplente o línea nueva sostiene un FAVORABLE solo con la vía que lo ataca nombrada | Getafe, Lille–Bodø, Napoli–Lazio |
| 15 | M2: en la rama persiguiendo, la razón dice qué vía queda después de los cambios habituales del DT y quién la hereda; si no queda ninguna, DESFAVORABLE | Huachipato, Alianza Atlético, Palestino |
| 16 | Integración: el TDE hereda `nivelFocoPersiguiendo` en las ramas del que persigue; HERENCIA-DTP avisa si difiere | la incidencia 1056 y los tres casos del TDE |
| Génesis | M4: la lista cerrada de categorías y las dos marcas; «sin fuente» es categoría; M2: las cinco vías obligatorias y «cada vía nombra zona o intérprete». El protocolo de fuentes por liga, en una referencia aparte que el cierre abre al buscar | el estudio (`DTP_autopsia_gol_estudio.md`) y sus mediciones |

Dos cosas para quien aplique el núcleo:
- La nota de versión de la v1.8 que se escriba en el encabezado va **entera al
  historial**; arriba queda la línea «Versión vigente» de la propuesta del
  núcleo.
- La tabla de fuentes por liga de la génesis (b) es fechada y se rehace con
  cada revisión: conviene que viva en `references/` y no en el núcleo, para que
  la corrida de partes no la cargue (solo la usa el cierre).


## Tabla de cambios

Una fila por cambio. En la comprobación, «sostiene» quiere decir que lo
sostiene el texto de las 113 lecciones acreditables del segundo corte. No es
una tasa: rige el sesgo de atribución.

| # | Cambio (una línea) | Tipo | Comprobación 10/11 | Núcleo o historial |
|---|---|---|---|---|
| 1 | M5: la rama se juzga por lo generado contra lo concedido, en el área primero; la referencia no viaja; los penales al lado del xG | rúbrica | sostiene | núcleo (regla) · historial (casos) |
| 2 | M2: la razón de la rama cita sus vías por renglón; la condición lleva su contrario; ceder no es señal | rúbrica + app (aviso) | sostiene | núcleo · historial |
| 3 | Posesión: «igualado» y «arriba» aparte cuando el foco puede ponerse arriba temprano | rúbrica | sin casos | núcleo · historial |
| 4 | Vías: la pelota parada del que cede va condicional; la media distancia en los dos lados | rúbrica | matiza (con materia la vía tampoco está dada) | núcleo · historial |
| 5 | Banco y penales desde la hoja: sin titulares, sin minuto fijo, tercer nombre «si entra», quién patea tras un errado | rúbrica + app (`bancoOfensivo`) | sostiene | núcleo · historial |
| 6 | M1: el grid se copia y la coordenada existe; `rehacer` reescribe todo lo que nombra piezas | rúbrica + app (lectura del grid, hora de la formación) | sostiene y matiza (formación corregida tras el pitazo) | núcleo · historial |
| 7 | La vía de expulsión de los dos lados, con toda la línea del duelo y la vuelta de suspensión | rúbrica | sostiene | núcleo · historial |
| 8 | M3: quién queda atrás en todas las ramas; lateral y extremo de la misma banda = costo del carril (el rearme del medio: **candidato**, decidido 10/11) | rúbrica | sostiene | núcleo · historial |
| 9 | MECANISMO: qué es una corrección, la reserva del par, `sin mecánica` repetido a su rama | rúbrica | sostiene | núcleo · historial |
| 10 | El reconvertido también ataca (sus dos caras) | **candidato** (decidido 10/11) | sostiene (un caso, con reserva) | historial |
| 11 | Posesión: el perfil del rival en su condición y con su objetivo de hoy; el ejemplo de Paderborn se reescribe (decidido 10/11) | rúbrica + app (`posesionReferencias`) | sostiene | núcleo · historial |
| 12 | Banco: el lateral o defensor fresco que llega es banco ofensivo | rúbrica + app | sostiene | núcleo · historial |
| 13 | Penales concedidos en serie: vía del equipo | **candidato** (decidido 10/11) | sin casos | historial |
| 14 | El mismatch contra un reconvertido o una línea nueva sube la rama solo con la vía nombrada; con ella, sube (decidido 10/11) | rúbrica | matiza (con la vía nombrada, sí sube) | núcleo · historial |
| 15 | La vía persiguiendo tiene que sobrevivir a los cambios del DT | rúbrica + app (minuto de salida habitual) | nuevo (tres casos del segundo corte) | núcleo · historial |
| 16 | El TDE hereda `nivelFocoPersiguiendo` en las ramas del que persigue; HERENCIA-DTP avisa si difiere; con el arrastre del M2 (línea 196) | aprobado (usuario, 10/11) + app | no aplica (decisión del usuario) | núcleo |
| G | Génesis del gol: categoría cerrada, protocolo de fuentes, vías obligatorias | rúbrica + app + medir | sostiene y matiza la tabla de fuentes (El Gráfico, Chile) | núcleo (M4/M2) · referencia aparte (tabla de fuentes) · historial (estudio) |

## Lista para redactar

Verificado el 10/11/2026 contra `docs/skills/diagnostico-tactico/SKILL.md`
**v1.7, 414 líneas** (rama `claude/skills-decisiones-2026-11`). Las líneas
citadas son de ese archivo y se abrieron una por una; los reemplazos marcados
«exacto» se comprobaron con `grep -F` (aparecen una sola vez). Las inserciones
van como sub-viñeta debajo de la línea citada, con la marca *(v1.8)*. Lo que la
app todavía no trae va como «pendiente de la app», sin nombre de campo nuevo
(paso 3 de «Cómo se aplica»).

| # | Entra | Dónde va en el SKILL.md (v1.7) | Texto nuevo listo | Caso nombrado | ¿Afloja algo vigente? | ¿Toca otro skill? |
|---|---|---|---|---|---|---|
| 0 | sí | encabezado, nueva entrada `v1.8` arriba de la `v1.7` (línea 8) | sí (T0) | — | no | no |
| 1 | sí | M5, debajo de «La conversión a favor también va aparte» (l. 336), y M2, debajo de «El veredicto de cada rama nombra la vía entera» (l. 199-201) | sí (T1a, T1b, T1c, T1d) | Groningen, Sunderland–Chelsea, NEC–Utrecht, Paderborn–Frankfurt, Sevilla–Alavés | no (precisa la v1.6: lo generado se lee contra lo concedido) | no |
| 2 | sí | M2, veredicto: debajo de l. 198 (ceder), l. 201 (vía por renglón) y l. 202 (condición) | sí (T2a, T2b, T2c) | Slavia, Sport Huancayo, Libertad–Guayaquil City, Rubio Ñu, Viseu, Emelec–Libertad, Cajamarca | no | SAD 6-C toma las vías del DTP (sin conflicto) |
| 3 | sí | Regla de posesión, después de la última viñeta de la Precisión v1.7 (l. 262) | sí (T3) | U. Católica–U. de Chile, Panathinaikos–AEK, São Paulo–Corinthians, PEC Zwolle | no | no |
| 4 | sí (la precisión de Limache, como nota) | M2 vías: debajo de l. 186 (media distancia) y de l. 187 (pelota parada) | sí (T4a, T4b) | AEK–Real Madrid, Auxerre, Torino–Lecce, Genoa–Milan | no (Chapecoense: condicional no es descartada) | no |
| 5 | sí (el segundo que recibe la falta, como nota) | M2 vías: penales, debajo de l. 183; banco, debajo de l. 191; reemplazo en l. 192 | sí (T5a, T5b, T5c) | Crystal Palace, UCV Moquegua, AZ, Utrecht, Cruz Azul | no | **EFE 10** (banco probable): arrastre T5c |
| 6 | sí ((c) sin cambio de regla) | M1, debajo de l. 158 (once oficial manda); M2, debajo de l. 206 (al rehacer) | sí (T6a, T6b) | Espanyol, Beşiktaş, Rayo, Millonarios, Kalamata | no | EFE 2/D1 (caja de sensibilidad con las dos variantes: lo compara la app) |
| 7 | sí (el recambio cargado de tarjetas, como nota) | M1, debajo de l. 161 (amarillas de toda pieza del seguro) | sí (T7) | Málaga, Frankfurt–Paderborn, Monterrey, River–Boca | no | no |
| 8 | sí (el rearme del medio: **candidato**) | M3, debajo de l. 280 | sí (T8) | Roma–Man United, Defensa y Justicia, Liverpool–Fenerbahçe, Milan–Genoa | no | TDE 13 (la rama del TDE contra el M3; del lado del TDE) |
| 9 | sí (el asistidor repetido bajo el umbral, como nota) | MECANISMO-ABIERTO, debajo de l. 321; candidatos de l. 322 | sí (T9) | Villarroel, Charleroi, Westerlo, Pereira | no (el umbral ≥ 2 en ≤ 15' no cambia; `sin mecánica` sigue sin degradar K, l. 317) | no |
| 10 | como candidato | M1, línea del candidato (l. 162), al final | sí (T10) | Telstar, Cajamarca | no | no |
| 11 | sí (las bajas del rival, como nota) | Regla de posesión: reemplazo exacto en l. 259 (Paderborn) y viñeta nueva al final de la Precisión v1.7 (dentro de T3) | sí (T3, T11) | OFI–Atromitos, Genk–Union, Sport Boys–UTC, Garcilaso–Comerciantes, Paderborn | no (el perfil del rival sigue mandando) | no |
| 12 | sí | M2 vías, banco: debajo de l. 190 | sí (T12) | Man United–Aston Villa, Porto–Vitória, Pereira | no | EFE 10 (B5 por rol) |
| 13 | como candidato | MECANISMO-ABIERTO, candidatos (l. 322) | sí (dentro de T9) | La Guaira, Portuguesa–La Guaira, Universitario | no | no |
| 14 | sí | M2, debajo de l. 174 (duelos por carril) | sí (T14) | Napoli–Lazio, Talleres, La Calera, Getafe | no | no |
| 15 | sí | M2, veredicto: debajo de l. 201 (sin vía → DESFAVORABLE) | sí (T15) | Huachipato, Alianza Atlético, Palestino | no | no |
| 16 | sí | Integración, l. 409 (exacto) y M2, l. 196 (exacto) | sí (cambio 16, (a) y (b)) | Westerlo–Charleroi, Konyaspor, Como–Inter (en el TDE) | no | **TDE 14** (lo tiene, aprobado) |
| G | sí | M4: reemplazo exacto de l. 295 y subsecciones nuevas después de l. 300; M2 vías: debajo de l. 193 | sí (TGa, TGb, TGc) | Havertz, Karl, Monterrey, Toluca, Boca–Defensa, La Serena–Palestino | no | no |

**Lo que NO entra al `SKILL.md`:** el candidato del 2 (seguro «sin»
persiguiendo), el rearme del medio (8), el reconvertido que ataca (10, sigue
candidato), los penales en serie (13), las precisiones de un caso de la tabla
de decisiones, `ROLES_GRID_REHACE` y el casillero de Jev. Los candidatos van en
la línea «Candidatos anotados» del changelog v1.8 (T0).

### Textos exactos

**T0 · encabezado (nueva entrada, arriba de la de la v1.7).**

> **v1.8 · <fecha de redacción> — Revision desde el dossier de la app SAD: las 1150 lecciones pendientes de la v1.7 (265 partidos del 01/11 al 09/11, en dos cortes del 10/11). Acreditan las `ciega` + `PRE` sin copa ni cuarentena; las 18 de la Copa de la División Profesional de Bolivia y las 15 de cuarentena que enseña fijan rubrica sin sostener cambios. Ninguna pide mover un numero. Decidida por el usuario el 10/11/2026.**
>
> **1. M5: el veredicto se juzga contra lo concedido** —manda la diferencia de volumen, no la lista de vias cumplida (NEC–Utrecht)—, la referencia de volumen no viaja y los penales van al lado del xG (Groningen, Sunderland–Chelsea, Paderborn–Frankfurt, Sevilla–Alaves).
>
> **2. M2: la razon de cada rama cita sus vias por renglon, el veredicto con condicion escribe su contrario, y ceder la pelota no es señal en ninguna direccion** (Slavia, Libertad–Guayaquil City, Rubio Ñu, Emelec–Libertad).
>
> **3. Posesion: «igualado» y «arriba» aparte cuando el foco puede ponerse arriba temprano, y el perfil del rival en su condicion de hoy** (U. Catolica–U. de Chile, OFI–Atromitos, Genk–Union); el ejemplo de Paderborn se precisa: el perfil del rival se lee en su sede.
>
> **4. Vias: la pelota parada del que cede va condicional; la media distancia en los dos lados con todos sus rematadores** (AEK–Real Madrid, Torino–Lecce).
>
> **5. Banco y penales desde la hoja:** ningun nombre en el XI y en el banco, el banco sin minuto fijo, el lateral o defensor fresco que llega es banco ofensivo, y la lista de penales con un tercer nombre «si entra» y quien patea tras un errado (Crystal Palace, UCV Moquegua, Man United–Aston Villa, AZ).
>
> **6. M1: con el once oficial, el sistema y los roles se copian del grid; al rehacer se reescribe todo lo que nombra piezas** (Espanyol, Beşiktaş, Rayo, Millonarios).
>
> **7. La via de expulsion de los dos lados, con toda la linea del duelo y la vuelta de suspension** (Malaga, Frankfurt–Paderborn, Monterrey, River–Boca).
>
> **8. M3: quien queda atras despues de los cambios en todas las ramas, y el costo del carril** (Roma–Man United, Defensa y Justicia, Liverpool–Fenerbahce).
>
> **9. MECANISMO-ABIERTO: que es una correccion, la reserva del par y el `sin mecanica` repetido a su rama** (Villarroel, Charleroi, Westerlo).
>
> **10. El mismatch contra un reconvertido o una linea nueva sube la rama solo con la via que lo ataca nombrada** (Napoli–Lazio, Talleres), **y la via persiguiendo tiene que sobrevivir a los cambios del DT** (Huachipato, Alianza Atletico).
>
> **11. M4: la categoria del gol de una lista cerrada, el protocolo de fuentes por liga y lo que figura si o si en `viasGol`** (pedido del usuario del 08/11).
>
> **12. El TDE hereda el seguro persiguiendo del DTP** (incidencia 1056, aprobado por el usuario el 10/11).
>
> **Candidatos anotados, no regla:** el reconvertido tambien ataca (Leones del Norte, Telstar; Cajamarca con reserva), el rearme del doble pivote o del medio cuenta como el de la linea (Fiorentina, Instituto; Gimnasia con una roja), los penales concedidos en serie son del equipo (La Guaira, Portuguesa–La Guaira, Universitario: dos del mismo cruce), MECANISMO-ABIERTO activo que baja el veredicto (Cucuta, Westerlo), el seguro «sin» que impide un FAVORABLE persiguiendo (Groningen; The Strongest en copa), la presion alta con su vuelta (Utrecht–NEC, Lille–Bodø).
>
> **Queda fuera:** ningun numero se mueve (vida util, ≥ 80 % de interpretes, ≥ 2 errores del arquero, ≥ 2 goles en ≤ 15 minutos, corte de DTP-REHACER); ni banda de «parejo» para el volumen, ni valor de xG por penal, ni ventana de minutos para el rearme, ni magnitud de la posesion.

(La fecha y los conteos finales se completan al redactar; la entrada sigue el
formato de la v1.7, sin tildes como las anteriores.)

**T1a · M5, sub-viñeta debajo de la línea 336.**

> - **El veredicto se juzga contra lo concedido** *(v1.8)*. El volumen de la rama jugada se lee **contra el que concedió el foco en esa rama**, dentro del área primero: generó más de lo que concedió → FAVORABLE; parejo → NEUTRO; menos → DESFAVORABLE. Un FAVORABLE que generó mucho y concedió lo mismo es NEUTRO por volumen (Groningen: 2,18 de xG contra 2,48; HSV–Gladbach; Sporting–Shakhtar; Marseille–Lens), y un NEUTRO o DESFAVORABLE que generó mucho más de lo que concedió subestimó la rama (Sunderland–Chelsea: 2,58 contra 0,55 cediendo el 69 %; Napoli–Lazio; Twente–Ajax; Brest–Lyon). **Manda la diferencia de volumen, no la lista de vías cumplida**: que los goles salieran por vías de la lista se anota y no sube el veredicto (NEC–Utrecht: 2,31 contra 2,1, NEUTRO). El punto que sostuvo el arquero propio tampoco confirma la rama (Elche: 7 atajadas; Levante; Atalanta). **Sin umbral**: cuánto es «parejo» lo lee el cierre con los dos números a la vista; una banda sería un número nuevo sin con qué calibrarlo.

**T1b · M5, sub-viñeta debajo de T1a.**

> - **La referencia de volumen no viaja** *(v1.8)*: como la posesión, sale de partidos en la misma sede y contra un rival del mismo perfil de balón, **nunca de un solo partido ni de una racha**. Sin esa referencia, la rama dice la dirección y no un número (Paderborn–Frankfurt: NEUTRO porque «genera poco», 1,03 de temporada, y generó 2,42; Espanyol–Deportivo; Atromitos, NEUTRO por el 1,62 de temporada y de visita 0 al arco; Schalke: DESFAVORABLE por «4 sin marcar», y 2,61; Nacional: «0,34 de xG en Arouca»).

**T1c · M5, sub-viñeta debajo de T1b.**

> - **Los penales, al lado del xG** *(v1.8)*: el xG de la API incluye los penales. El cierre dice cuántos hubo y lee el volumen en juego abierto aparte, **sin restar ningún valor fijo por penal** (Sevilla–Alavés: cerca de 0,8 de 1,61 era el penal; Mirassol; The Strongest: tres penales; América; Orense: casi todo el 0,97 era el penal errado). Los penales del partido en el volumen de los insumos están **pendientes de la app**: hasta entonces salen de los eventos de la ficha.

**T1d · M2, sub-viñeta debajo de la línea 201** (va antes de T15).

> - **El FAVORABLE apoyado en una zona escribe quién remata** *(v1.8)*: la apertura dice **quién remata dentro del área y desde dónde le llega la pelota**; sin eso, la rama es NEUTRO (Libertad–Emelec: 9 de 14 remates de afuera; Tottenham–Leeds; U. de Chile–U. Católica: 7 de 11 de afuera y 0 al arco; Macará; Sporting Cristal–ADT). Es la regla del M5 («el volumen se cuenta donde se remata») escrita en la apertura.

**T2a · M2, sub-viñeta debajo de la línea 198.**

> - **Que el foco ceda tampoco es señal en contra** *(v1.8, espejo de la v1.6)*: quién tiene la pelota no decide el veredicto **en ninguna dirección**; la rama se juzga por las vías contra el bloque y el seguro (Emelec–Libertad: DESFAVORABLE «contra un bloque de cinco que cede» y 2,27 de xG; Leeds–Tottenham: 11 remates en el área contra 3; Tomayapo; Telstar: cedió el 65 % y generó 2,49; Sunderland, Brest, Cajamarca: 41 % y 3,13 de xG). Y tenerla tampoco sostiene un FAVORABLE (O'Higgins, Alianza Lima, Coquimbo).

**T2b · M2, sub-viñeta debajo de la línea 201** (después de T1d).

> - **La razón de cada rama cita sus vías por renglón** *(v1.8)*: nombra los renglones de `viasGol` que usa, en vez de resumirlos. Una rama que no cita ninguno, o que solo cita la pelota parada y los centros cuando la lista tiene banco, segunda línea o media distancia, se revisa antes de depositar (Telstar, Riestra, Kasımpaşa, Getafe; Slavia: 16 remates y 2,17 de xG «sin vía»; Gil Vicente; Sport Huancayo: el empate fue del lateral que la lista tenía en el carril). El aviso del recibo está **pendiente de la app** (aviso, no rechazo).

**T2c · M2, sub-viñeta debajo de la línea 202.**

> - **El veredicto con condición escribe su contrario** *(v1.8, amplía las de la v1.6 y la v1.7)*: una rama que se apoya en algo que tiene que hacer el rival —abrirse, volcarse, salir, caerse— lleva **dos líneas, la de la condición y la de su contrario**, cada una con su veredicto. Si la condición no depende del foco, el veredicto de la rama es el de la línea menos favorable hasta que el cierre diga cuál se jugó (Libertad–Guayaquil City: «cerrar y correr», cerró y no corrió; Rubio Ñu y Viseu: «el improvisado se cae al 55-65», y no se cayó; Valencia–Elche; PEC Zwolle–Willem II; Deportivo Cali, acierto que lo escribió). El campo de la línea contraria en el parte está **pendiente de la app**: hasta entonces va en la razón de la rama.

**T3 · Regla de posesión, después de la línea 262** (bloque nuevo, al mismo nivel que la Precisión v1.7).

> **Precisión v1.8: «igualado» y «arriba» aparte, y el perfil del rival en su condición de hoy.**
> - Cuando el foco no es favorito, o puede ponerse arriba temprano, la posesión de la rama se escribe en dos: **igualado** y **arriba**. La forma sin balón, el seguro y la transición siguen juntas (U. Católica–U. de Chile: 55-60 % escrito, arriba desde el 4', 30 %; Stuttgart–Bremen, Olimpia–Recoleta, Necaxa–Tijuana, Athletic–Real Sociedad, Cercle, ADO; Panathinaikos–AEK: arriba al 1', 40 %; Trinidense–Ameliano). El campo de «arriba» en el parte está **pendiente de la app**: hasta entonces va en la rama.
> - **Con DT nuevo en el rival, su perfil de balón con el DT anterior no vale**: sin partidos con el DT de hoy, solo la dirección (São Paulo–Corinthians, Rio Ave, Cercle, Nacional–Viseu).
> - **Un partido de copa contra un rival de otra categoría no es referencia** (Telstar y Utrecht; PEC Zwolle: 72 % ante el FC Oss, 34 % hoy).
> - **El perfil de balón del rival es el de su condición de hoy**: su posesión de local o de visita en la competición, y con el objetivo de hoy; ni su promedio de temporada, ni un partido en la otra sede, ni la etiqueta del sistema («un bloque de cinco cede»). OFI–Atromitos: el 54 % de temporada de Atromitos, que de visita cedió (37 %); Genk–Union: el 58 % de Genk en Mechelen, 46 % en el campo del 3.º; Olympiakos–PAOK; Le Mans–Monaco; Hoffenheim–Schalke; Sport Boys–UTC: «el descendido cede», y sin objetivo no cedió; Nacional Potosí–Real Potosí; Audax–Coquimbo; Garcilaso–Comerciantes. La referencia por condición en los insumos está **pendiente de la app**.
> - Sin referencia, la rama declara la dirección con su razón, **nunca vacía** (Telstar y Utrecht dejaron una rama «sin dato»).

**T11 · Regla de posesión, línea 259, reemplazo exacto** (el ejemplo de Paderborn, decidido el 10/11).

Texto viejo:

> Paderborn: con dos equipos que ceden, decide el perfil del rival, no la sede (57 %).

Texto nuevo:

> Paderborn: con dos equipos que ceden, decide el perfil del rival —leído en su sede de hoy (v1.8)—, no la sede del foco (57 %).

(La entrada 7 del changelog de la v1.7, línea 22, no se toca: es historia.)

**T4a · M2 vías, sub-viñeta debajo de la línea 186.**

> - **La media distancia en los dos lados, con todos sus rematadores** *(v1.8, amplía la de la v1.7)*: cuando uno de los dos ataca un bloque replegado, la línea de media distancia va **en las vías de los dos lados**, con **todos** los rematadores de afuera del once, no uno (Torino–Lecce: el que cedía remató 5 de 6 de afuera y empató así; Bremen–Stuttgart: 12 de 23; Kasımpaşa: el 1-0 de un titular que la línea no nombraba; Tolima; Genoa–Milan: 10 de 17 persiguiendo).

**T4b · M2 vías, sub-viñeta debajo de la línea 187.**

> - **El que cede no fabrica córners** *(v1.8)*: en la rama en que el foco va a ceder la pelota, su pelota parada va **condicional por defecto** y no como vía principal, salvo que los córners que concede el rival digan otra cosa. La materia la decide el cruce, no el promedio propio (AEK–Real Madrid y Olimpia–Cerro: 30 % y 0 córners; Auxerre–Strasbourg: 5,3 de temporada y 0; Jaguares, Barracas, Casa Pia, Santa Clara, U. de Concepción, Nublense; y al revés, Bodø: 5,8 de promedio y 3 en el cruce; Excelsior: 1,2 y 7). Condicional no es descartada: se declara igual (Chapecoense: dio con 2 córners).

**T5a · M2 vías, penales: sub-viñeta debajo de la línea 183.**

> - **Tercer nombre «si entra» y el orden tras un errado** *(v1.8)*. La lista de dos suma **el 9 o el lanzador del banco ofensivo como tercer nombre condicional** («si entra») y dice **quién patea después de un errado**, que puede ser el mismo, y se escribe así (AZ: Meerdink erró al 59' y convirtió al 90+1). Pateó un suplente, o el 9 que entró por el ejecutor, en Paderborn, Charleroi, Bologna, Porto, The Strongest, Crystal Palace (Nketiah), Bucaramanga, UCV Moquegua (Angulo entró al 73' y pateó al 78'), Freiburg, Ipswich y Trinidense; el segundo penal tras un errado lo pateó otro en St. Truiden, La Louvière y The Strongest. Con dos ejecutores de muestra mínima, el orden no está fijado y se dice así (ADT–Comerciantes, River, Llaneros, Santa Fe, Orense). Y **nunca vacía** (Levadiakos, Strasbourg–Auxerre, Parma; Tolima–Millonarios: «sin fuente entre los titulares», y pateó un titular).

**T5b · M2 vías, banco: dos sub-viñetas debajo de la línea 191.**

> - **Ningún nombre va a la vez en el XI de referencia y en el banco** *(v1.8)*; con el once oficial, el banco es **la hoja** (Gaziantep, Mónaco, ADO, Man United; Ameliano: Torales en el XI y en el banco; Cruz Azul: Ibáñez, nombrado banco, fue titular y marcó). El aviso del recibo está **pendiente de la app**.
> - **El banco va sin minuto fijo** *(v1.8)*: el M3 dice cuándo es probable que entre, y las vías no lo condicionan a ese minuto (Utrecht: Alarcón, escrito «para la última media hora», entró al 37'; Getafe y Bologna: al descanso; Talleres y Cobresal).

**T5c · M2 vías, banco, línea 192: reemplazo exacto** (arrastre de coherencia con el cambio 10 del EFE v1.10).

Texto viejo:

> El banco se arma con la plantilla y el `xiReferencia`;

Texto nuevo:

> El banco se arma con la plantilla y el `xiReferencia` —y *(v1.8)* con el banco probable de la tabla F1 y el B5 por rol del EFE del mismo parte, que se heredan sin re-investigar (ver Integración)—;

(Solo si el EFE v1.10 se redacta con su cambio 10 en la misma tanda; si no,
esta línea queda como está.)

**T6a · M1, sub-viñeta debajo de la línea 158.**

> - **Con el once oficial a la vista, el sistema se copia de la ficha** *(v1.8, precisa la de la v1.7)*: el sistema es **la formación de la ficha** y el rol de cada titular sale de **su fila del grid** —dos jugadores en la fila del pivote son doble pivote aunque su rol habitual diga otra cosa— y la banda, de su casilla. **Una coordenada que se cita tiene que existir en la ficha.** Sin grid, el rol contado por puestos va en las dos variantes hasta que el grid llegue (Guayaquil City). Con el grid ya capturado se leyó a ojo: pivote único por doble en Excelsior, Viking, PSV, Grau, Gaziantep, City y Alianza Atlético; bandas invertidas en Moreirense, Grêmio, Beşiktaş, Le Havre, Sporting Cristal y Comerciantes; otro sistema en Espanyol (coordenadas 2:5 y 3:4 que no existen), Tottenham, Rayo y América de Cali. Si la API corrige la formación después del pitazo, es el once tardío de las dos capas, no un fallo del M1. La lectura del grid en los insumos del rehacer y el aviso de coordenada inexistente están **pendientes de la app**.

**T6b · M2, sub-viñeta debajo de la línea 206.**

> - **Al rehacer, todo lo que nombra piezas** *(v1.8, amplía la anterior)*: en el modo `rehacer` se reescriben M1, M2 (duelos, vías y las dos ramas), M3 (palancas) y `m2.piezas`. Una pieza que no está en la hoja se saca, y la vía que dependía de ella se reescribe con quien la hereda (Millonarios: la presión de Castro y Estupiñán en el 0-25'; Slovan; Botafogo: duelos y palancas con cuatro suplentes; Atlético-MG; América; Kalamata: el doble pivote del seguro «fijo» con un jugador fuera de la hoja).

**T7 · M1, sub-viñeta debajo de la línea 161.**

> - **La vía de expulsión, de los dos lados y con toda la línea del duelo** *(v1.8)*. Se escribe también para la pieza **propia** reasignada que corre hacia atrás contra el velocista rival (Málaga: Aznou, amarilla al 38' y roja al 64'; Frankfurt–Paderborn: se nombró a Onyedika y el expulsado fue Baum, lateral reasignado), con **todas las piezas de la línea que defiende el duelo** y no solo la que está al borde del ciclo (Monterrey: se nombró a Chávez y la roja fue del central Salcedo; Gençlerbirliği: la zaga nueva sin las amarillas de sus centrales; Barcelona: Marc Bernal, contenedor único, sin sus amarillas; Independiente Rivadavia: Florentín, del doble pivote del seguro). Una pieza que **vuelve de una suspensión** o tiene una roja reciente se nombra con eso (River–Boca: Martínez Quarta, expulsado al 10'; Sarmiento: venía de dos rojas). Con cualquiera de ellas en el once, la rama más probable escribe su línea con uno menos (v1.7). Que las amarillas, la roja reciente y la vuelta de suspensión de cada pieza entren a los insumos del DTP está **pendiente de la app** (hoy viajan en la tabla F1).

**T8 · M3, sub-viñeta debajo de la línea 280.**

> - **Quién queda atrás, en todas las ramas, y el costo del carril** *(v1.8, amplía la anterior)*. El M3 escribe **quién queda atrás después de los cambios en todas las ramas**, no solo en la del que persigue: el rearme para cuidar o administrar una ventaja también cuesta (Roma–Man United: los dos centrales al 75'-76', goles al 83' y 86'; Sport Boys con 2-0; Strasbourg con 3-0; Aston Villa con 4-2, dos goles en el añadido; Porto; Cerro; Sporting Cristal; Defensa y Justicia: doble cambio al 90+1 para cerrar el 0-0 y gol al 90+6). Un cambio que toca **el lateral y el de delante de la misma banda** se escribe como **costo de ese carril**, con la vía del rival por ahí (Liverpool–Fenerbahçe: Gomez y Muñoz al 66'; Nacional–Libertad; AEK–Panathinaikos; Santa Fe–Cúcuta; Milan–Genoa: sale el carrilero al 87' y marca al 88' el carrilero rival de ese lado). Sin ventana de minutos, como en la v1.7, y es vía, no certeza (Rubio Ñu, Marseille, Barcelona SC y Barcelona rearmaron sin conceder).

**T9 · MECANISMO-ABIERTO: sub-viñeta debajo de la línea 321, y la línea 322 de candidatos, ampliada.**

> - **Qué es una corrección, la reserva del par y el `sin mecánica` repetido** *(v1.8)*. (a) Cuenta como corrección el cambio de un jugador de **la línea o la banda donde nacieron los goles**, o un cambio de sistema; un cambio de otra zona se anota y no corta la frecuencia (Villarroel: los cambios del 55-56 fueron ofensivos; Cusco; Liverpool). (b) El mecanismo declarado lleva su **reserva** escrita —`con diez`, `autogol/penal`, `resuelto`— y entra al M2 del próximo rival como vía a verificar **con esa reserva**, sin descartarlo ni sumarle peso (Atlante; Excelsior, con diez desde el 5'; Sabah; Kortrijk; Chapecoense; Charleroi: dos goles en dos minutos con 4-0). El umbral no cambia (≥ 2 goles en ≤ 15 minutos). (c) Un `sin mecánica` visto en **dos partidos seguidos** entra a las vías del rival **en la rama en que se dio** —casi siempre persiguiendo, como el régimen de la v1.5—, como vía a verificar y sin degradar K (Westerlo: tres en seis minutos y cuatro en 14; Sassuolo, Belgrano, Monagas, Vitória, Metropolitanos, Pereira).

Línea 322, al final, se agrega:

> *(v1.8)* Suman casos, sin llegar a regla: el MECANISMO activo que baja el veredicto (Westerlo, segundo caso) y los penales concedidos en serie (Portuguesa–La Guaira y Universitario–UCV Moquegua: tres casos, dos del mismo cruce; espera uno de otro equipo, decisión del usuario del 10/11).

**T10 · M1, línea 162 (candidato), al final, se agrega:**

> *(v1.8)* Suma Telstar–Utrecht (Martha, lateral de origen de mediapunta, asistió el 2-0 y marcó el 4-2) y, con reserva, Cajamarca–Alianza Atlético (la lección no dice si el lateral nuevo estaba reasignado): dos casos limpios; sigue candidato (decisión del usuario del 10/11).

**T12 · M2 vías, banco: sub-viñeta debajo de la línea 190.**

> - **El lateral o el defensor fresco que llega es banco ofensivo** *(v1.8)*: por su rol de hoy, el banco ofensivo incluye al **lateral o carrilero fresco que llega** y, en la rama persiguiendo, al **defensor que entra a cargar el área**; no es todo el banco (Başakşehir: Bulut asistió el gol decisivo; Bolívar; Man United: Dorgu entró al 66', asistió el 3-4 e hizo el 4-4; Bucaramanga; Porto: Martim Fernandes, el gol del triunfo; Chivas–León; Cobresal; Pereira). El rol de la hoja en la lista calculada del banco está **pendiente de la app**.

**T14 · M2, sub-viñeta debajo de la línea 174.**

> - **El mismatch contra un reconvertido, un lateral suplente o una línea nueva es vía a verificar, no un mismatch dado** *(v1.8)*: sostiene un FAVORABLE **solo si la vía que lo ataca está nombrada** —quién, por dónde y qué remate sale de ahí—; **con la vía nombrada, la rama sube por él**. Sin eso, va como vía a verificar y la rama no sube (Getafe; Lille–Bodø; Napoli–Lazio: la Lazio apoyó el FAVORABLE en el 2 contra 1 sobre el carrilero reconvertido y generó 0,92 contra 2,44; Talleres: la vuelta escrita contra el central reconvertido a lateral fue el 0-1; La Calera no la escribió y la rama quedó corta). Es la misma vara del FAVORABLE apoyado en una zona.

**T15 · M2, sub-viñeta debajo de la línea 201** (después de T2b).

> - **La vía persiguiendo tiene que sobrevivir a los cambios** *(v1.8)*. En la rama persiguiendo, el M2 cruza sus vías con el M3: si las piezas que las sostienen son las que el DT de hoy suele cambiar primero, o están amonestadas, la razón dice **qué vía queda después de los cambios**, con el suplente que la hereda; si no queda ninguna, la rama es DESFAVORABLE (lo de arriba). Sin minuto fijo y sin umbral (Huachipato: Altez salió al 45' y Briceño al 59', y en 67 minutos persiguiendo hubo un remate al arco; Alianza Atlético: la vía escrita salió al descanso con los tres; Palestino, acierto que lo dice igual: la vía principal se apagó al 63'). El minuto habitual de salida de cada titular con el DT de hoy está **pendiente de la app**.

**Cambio 16:** los dos reemplazos exactos ya están en el punto 16 ((a)
Integración, línea 409; (b) M2, línea 196). Comprobados con `grep -F`: cada
texto viejo aparece una vez.

**TGa · M4, línea 295, reemplazo exacto, y subsección nueva después de la línea 300.**

Texto viejo:

> Vía: pelota parada / transición / juego abierto.

Texto nuevo:

> Categoría (de la lista cerrada, abajo). Vía: pelota parada / transición / juego abierto, derivada de la categoría (vacía si es «sin fuente»).

Subsección nueva, después de la línea 300:

> **La categoría del gol, de una lista cerrada** *(v1.8)*. Cada gol lleva **una categoría principal** de esta lista, y nada fuera de ella:
>
> | Familia | Categoría |
> |---|---|
> | Pelota parada | córner directo · segunda jugada de córner (incluye el córner en corto) · tiro libre directo · centro de tiro libre · lateral |
> | Penal | penal (con su origen: falta, mano o VAR; y «en el rebote» si se atajó y se convirtió después) |
> | Transición | transición tras recuperación alta · media · baja (la contra tras un córner rival es baja) |
> | Salida | error en la salida bajo presión (pase o despeje propio en campo propio) |
> | Ataque elaborado | centro lateral · pase interior entre líneas · combinación por dentro · desborde individual |
> | Directo | balón largo a la espalda (pelotazo o pase elevado sin recuperación previa) |
> | Remate | tiro de media distancia |
> | Pelota sucia | rebote o segunda jugada en el área · error del arquero (en la atajada) · autogol |
> | — | sin fuente |
>
> Dos **marcas** que no son categoría: **desvío** (el remate cambió de dirección en un rival) y **banco** (el autor o la pieza del gol había entrado).
> 1. **Sin fuente es una categoría, no un hueco.** Si ninguna página abierta nombra el disparador o la secuencia, la categoría es «sin fuente», con lo que sí se sepa (autor, asistente, «de cabeza»). Nunca se deduce la jugada de la asistencia, del tipo de la ficha ni del puesto del autor (un central que marca no es «pelota parada» sin fuente).
> 2. **La categoría la decide el disparador**, no la definición: el gol de Havertz es «error en la salida» aunque terminó en un centro; el de Karl también, aunque fue una vaselina.
> 3. La **vía** se deriva de la familia; guardar la categoría en el parte (y derivar la vía sola) está **pendiente de la app**. Hasta entonces, «sin fuente» va con la vía vacía, no con «juego abierto».
> 4. **MECANISMO-ABIERTO** se sigue nombrando con precisión (zona o rol); la categoría es el piso, no el reemplazo («segunda jugada de córner» no alcanza: «córner en corto, centro al segundo palo sin marca del lateral»).
> 5. Si la crónica aparece después del cierre, **se reclasifica** (como `sin mecánica`, v1.4).

**TGb · M4, subsección nueva después de TGa** (la tabla, fechada; con las
correcciones del 10/11).

> **Protocolo de fuentes para la crónica, por liga** *(v1.8; tabla fechada el 10/11/2026, se rehace con cada revisión)*. Antes de escribir «sin fuente», el cierre **abre** al menos dos páginas de la lista de su liga. **El resumen del buscador no es fuente** (en el estudio inventó la jugada dos veces y le atribuyó a una página un dato que no traía). Se cita la URL de la página abierta en la nota del gol.
>
> | Liga | Buscar en | Probar primero | Si no sale |
> |---|---|---|---|
> | Premier y equipos ingleses en Europa | inglés | sitio del club (match report), flashscore.com/news, PA Media (irishnews.com y otros) | 101greatgoals.com |
> | Bundesliga y alemanes en Europa | inglés | bundesliga.com (match report) | flashscore.com/news (fcbayern.com da 403) |
> | Serie A | inglés o italiano | livescore.com (Football Italia) | flashscore |
> | LaLiga | español | (sin medir) | flashscore.es, sitio del club |
> | Argentina | español | contextotucuman.com | elgrafico.com.ar (respondió el 10/11: Boca–Defensa), 442.perfil.com (solo definición); tudn da 403 |
> | Brasil | portugués, con «como foi» | jb.com.br, flashscore.com.br | — |
> | Liga MX | español | foxsports.com.mx | planoinformativo.com, record.com.mx |
> | Perú | español | exitosanoticias.pe, caretas.pe | prensa del país del jugador extranjero (primicias.ec para un ecuatoriano); americatv.com.pe da poco |
> | Colombia | español | noticiasrcn.com | winsports.co, occidente.co |
> | Chile | español | redgol.cl (La Serena–Palestino, 10/11; sin medir más) | — |
>
> Consulta que funcionó: «[local] [marcador] [visitante] [goleadores] [report / crónica / como foi]». **Partidos de menos de 48 horas**: la crónica puede no estar indexada; se escribe «sin fuente · a reintentar» y el cierre siguiente del mismo equipo la vuelve a buscar.

**TGc · M2 vías, sub-viñeta debajo de la línea 193.**

> - **Lo que figura sí o sí en `viasGol`, de los dos lados** *(v1.8)*, además de lo de la v1.5: (1) **la pelota sucia del área** —quién llega al rebote y contra qué arquero—, obligatoria cuando el arquero rival es suplente o viene de un error; (2) **el balón largo a la espalda**, del que defiende, contra la línea alta del rival, con el central que queda mano a mano; (3) **la transición también del favorito**: el que domina recupera alto y medio, y su contra se escribe aunque sea el que ataca; (4) **el ejecutor del penal según la hoja del día** (ver el ejecutor, arriba); (5) **el origen de la pelota parada además del rematador**: córner en corto, lateral al área y el tiro libre directo de quien no es el lanzador habitual (Banfield–Tucumán: el tiro libre directo de L. Gómez). Y una regla de forma: **cada vía nombra zona o intérprete**; una vía que solo dice la categoría («pelota parada», «media distancia») no cuenta como vía en el cierre.

### Para la app (no va al `SKILL.md`)

Todo lo de «Para la app, no para el skill» y «Lo que va al código si se
aprueba» sigue igual. Con las decisiones del 10/11 se suma o se precisa:

- **16 · `HERENCIA-DTP` compara también el `sob2` de la rama** (`parte.py`,
  `dtp_cowork.herencia_tde`), con el alcance del TDE 14: no se recalculan los
  partes viejos. Lo implementa el mantenimiento.
- **`ROLES_GRID_REHACE` sigue en `False`:** primero la medición cruzada de
  «`rolesVsGrid`» (seis partidos, 0 tokens).
- **El casillero de Jev:** sin cambio en esta revisión (A0 del EFE).
- **13 · los penales concedidos por el equipo en sus últimos partidos:** la
  ayuda calculable sirve para juntar los casos del candidato, no para una regla.
- **1068 (EFE↔corrida-sad):** la fila del titular que falta en la F1
  (`delOnceOficial`, ROT) y el rehacer con EFE son de la app y de la rutina; el
  DTP no cambia texto (su modo `rehacer` ya reescribe todo lo que nombra
  piezas, T6b, y hereda del EFE lo que el EFE traiga).

### Coherencia entre skills

| Dependencia | Qué pide del otro lado | ¿La otra propuesta lo tiene? |
|---|---|---|
| **16 ↔ TDE v0.1.26, cambio 14 (1056)** | el TDE hereda `nivelFocoPersiguiendo` (o `nivelRivalPersiguiendo`) en las ramas del que persigue; los dos skills salen juntos | **Sí**, aprobado (opción a), «coordinada con `DTP_v1.8_propuesta.md`». Su punto (2) resume la línea del DTP con otras palabras («viaja al `sob2`…»); manda el texto exacto del cambio 16 de acá. Sin bloqueo |
| **5 / 12 ↔ EFE v1.10, cambio 10 (banco probable, B5 por rol)** | el EFE dice que el DTP toma esa lista y no la arma de nuevo | **Sí** en el EFE (rúbrica, sin «decide»); del lado del DTP faltaba: va el arrastre T5c, condicionado a que el EFE 10 se redacte en la misma tanda |
| **6.(c) ↔ EFE v1.10, cambio 2 y D1 del dashboard** | la caja de sensibilidad dibuja las dos variantes del sistema para que la app la compare con el M1 | **Sí** (D1, «las dos variantes del sistema»). El DTP no cambia la regla (v1.6) |
| **Casillero de Jev ↔ EFE v1.10, A0** | una sola taxonomía para los tres skills | El EFE la tiene como **[DECIDE USUARIO]** abierta al leerla el 10/11; acá se resolvió conservador (sin cambio). Si el EFE la decide distinto, vale para el DTP sin tocar su `SKILL.md` |
| **1068 ↔ EFE v1.10 (cambio 1) y `corrida-sad`** | la F1 con la fila del que falta y el rehacer con EFE con 3+ titulares fijos cambiados o arquero distinto | En el EFE (cambio 1, A1, pregunta 2). El DTP no depende de texto nuevo |
| **8 ↔ TDE v0.1.26, cambio 13** | la rama del TDE se compara con el M3 del DTP | Del lado del TDE; el DTP no cambia nada para eso |
| **2 / G ↔ SAD v4.5, cambio 6 (falsador)** | el falsador toma todas las vías del DTP y no niega una que el DTP escribió | **Sí** en el SAD (6-C, punto 3). La lista de vías más larga del DTP (T2b, TGc) no choca |

**Bloqueos para redactar:** ninguno. Todas las líneas citadas existen en la
v1.7 y los reemplazos exactos aparecen una vez. Dos cosas a tener en cuenta:
T5c depende de que el EFE 10 entre en la misma tanda, y el texto del cambio 16
es el que manda sobre el resumen del punto (2) del TDE 14.
