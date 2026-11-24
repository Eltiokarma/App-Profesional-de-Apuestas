# Historial · `diagnostico-tactico`

Notas de cada versión, con los casos que motivaron cada regla, sus candidatos, lo que quedó fuera y de dónde sale. **No hace falta leerlo para analizar un partido**: las reglas vigentes están todas en `SKILL.md` (los candidatos abiertos, en el bloque del M5). Se lee al revisar el skill (fase D, modo mantenimiento, una propuesta nueva). Lo que viene de la v1.8 hacia abajo se movió tal cual desde `SKILL.md` el 17/11/2026, al aplicar el núcleo (`docs/revisiones/NUCLEO_SKILLS_propuesta.md`).

> **v1.10 · 24.11.2026 — Revisión desde el dossier de la app SAD: las 537 lecciones pendientes de la v1.9 (137 partidos del 17 al 23/11, todas `ciega` + `PRE`). 49 (19 partidos) son de copa nacional (Copa del Rey, Copa de la División Profesional de Bolivia, Taça de Portugal) y enseñan sin acreditar; quedan 488 acreditables de 118 partidos: 275 sostuvo, 128 mal aplicada, 70 regla falló, 9 insumo, 4 no dice, 2 imprevisto, 0 de otro skill. Las 28 del 17/11 (selecciones) pueden haber corrido con la v1.8 y no se cuentan como incumplimiento de la v1.9; dos lecciones de partes sin DTP (Olimpia 1632065:a:5, Libertad 1632067:b:3) quedan fuera. La v1.9 se sostiene (1,8 mal aplicadas por cada regla que falló, 0 fallos heredados del EFE). Ningún número se mueve. Aprobada por el usuario el 24/11/2026 con todas las recomendaciones (`docs/revisiones/DTP_v1.10_propuesta.md`).**
>
> **1. El veredicto apoyado en el nivel, la contra o la transición dice cuánto concede mientras espera**, con cualquier etiqueta (la v1.7 lo pedía solo al DESFAVORABLE): Vasco–Internacional 1492458:a (FAVORABLE, 0,52 de xG contra 1,40, ganó por conversión), Progreso–Torque 1650502:b (FAVORABLE por nivel, Progreso salió y fue parejo), IdV–Macará 1639806:b (NEUTRO apoyado en la contra, 0,63 contra 2,28). Apoyo sin la frase: Dinamarca–Noruega 1528993:a:2 y Marseille–Le Mans 1552822:a:4; la vigente del DESFAVORABLE, incumplida en Lazio–Lecce 1550202:b:2. El M5 cambia «un DESFAVORABLE que se apoya en el nivel» por «un veredicto que se apoya en el nivel o en la contra, con cualquier etiqueta». Sin banda: cuánto es mucho conceder es la medición del punto 6.
>
> **2. Renglón 6 de `viasGol`: figurar en otro renglón no saca a nadie de este** (decisión del usuario: se agrega la frase además del cruce de la app). Juventus–Venezia 1550201:a:6 (Cabal, centrador, hizo el 3-0), NEC–PSV 1552229:b:4 (Kostić), Querétaro–Necaxa 1551046:b:3 (M. Rodríguez), LDU–Aucas 1639807:b:3 (Guzmán, asistidor), Israel–Austria 1528996:a (Dor Peretz) y Polonia–Suecia 1528998:a:2 (Larsson, media distancia). 6 partidos, sin copa.
>
> **3. La pregunta 5 se responde con el DT de hoy y con lo que hizo, con `n`; la obligación de tabla no es evidencia**: Vitória–Bragantino 1492459:b:6 (respondida con el DT anterior), Cercle–Westerlo 1558682:b:5 (segundo partido seguido de Caixinha cediendo la pelota, «reacción al 1-0»), Liverpool M.–Wanderers 1650504:b:3 («obligado a ir», plantó una línea de cinco y sostuvo 59 minutos). No toca el recuento ni la vida útil.
>
> **4. El rearme del doble pivote o del contenedor cuenta como el de la línea, de candidato a regla** (M3): Liverpool M.–Wanderers 1650504:a:6 (pivote amonestado sale al 28', gol al 31'), Chelsea–Leeds 1557470:a:4 (Caicedo sale al 22', empate al 28'), Marseille–Le Mans 1552822:a:6 (doble cambio al 74', goles al 84' y 90+5); antes, Fiorentina e Instituto. En contra, sin restar: Grêmio–Bahía 1492454:b:4 (cambio forzado del contenedor al 46' sin conceder). Gimnasia (con una roja) queda como apoyo y no se cuenta. Sin ventana de minutos. Sale del bloque de candidatos.
>
> **5. Bloque «Candidatos abiertos»**: el seguro «sin» persiguiendo suma su primer contraejemplo (Dinamarca–Noruega 1528993:b: Noruega persiguió 72 minutos con el seguro «sin» y generó 4,28 contra 1,7); el segundo de la lista de penales suma Dinamarca–Noruega 1528993:b:2 (Ødegaard; pateó Haaland) y Racing–Real Sociedad 1570459:a:6 (Zabiri; pateó Canales), con reserva Barcelona–Villarreal 1570455:a:5 (Yamal figura en el penal y lo pateó) y **sigue candidato** (decisión del usuario: la lista de dos nombres ya cubre la conducta); el caso de la 6 viaja con el arquero **no suma casos** (Sassuolo–Genoa 1550206:b:3 y Hull–Brighton 1557472:b:3 son `sostuvoArquero` con el mismo arquero: corrige al estudio, que lo daba por llegado); **candidato nuevo** (decisión del usuario: entra al bloque, no como excepción a la línea menos favorable): con la condición sostenida por el propio parte, manda la condición (Bayern–Köln 1575221:b:6; Feyenoord–Excelsior 1552226:b). La obligación de tabla va para los dos lados (Boston River–Maldonado 1650500:a:4 se volcó; Liverpool M.–Wanderers 1650504 no se abrió), y la línea menos favorable acertó donde se incumplió en 7 partidos.
>
> **Queda fuera:** la banda de «parejo» del M5 (50 `regla_fallo` de 119 lecciones: 26 NEUTRO que el volumen resolvió, 19 FAVORABLE de más, 5 DESFAVORABLE de más; el plan de medición, con las lecturas (c) y (d) nuevas, está en la propuesta §3) y la vida útil 55-65 del improvisado como techo (Progreso–Torque 1650502:a:4, Bayern–Köln 1575221:b:5 y los tres del punto 3): son números y van a medición. Los candidatos de uno o dos casos (heredero en todas las ramas, «arriba» con el equipo de posesión, extremo expulsado, la línea contraria nombra el seguro, el tercer nombre de los penales, rest defense fijo, rotación sin nada en juego, el banco del que persigue con el DT goleado, la contra tras el córner propio, la pieza que pierde en la salida), lo de copa contra rivales de categorías menores (tres partidos, todos de copa) y la lesión de las dos piezas de la transición (Instituto–Huracán 1649568, imprevisto). No se reescriben pelota parada, posesión, referencia de volumen, vía de expulsión, línea menos favorable, banco, M3, grid, rehacer ni el reconvertido: se incumplen con el texto bien escrito y van a la app (propuesta §5).
>
> **De dónde sale:** estudio del 24/11 (desde docs/revisiones/estudio_lecciones_2026-11-24/), 537 lecciones de 137 partidos del 17 al 23/11.

> **v1.9 · 17.11.2026 — Revisión desde el dossier de la app SAD: las 347 lecciones pendientes de la v1.8 (81 partidos del 10 al 16/11). 59 (15 partidos) son de copa nacional y enseñan sin acreditar; quedan 288 acreditables: 161 sostuvo, 78 mal aplicada, 33 regla falló, 12 insumo, 3 imprevisto, 1 no dice. La muestra es de una semana y la mayoría son selecciones (fecha FIFA del 12 al 16/11). La v1.8 se sostiene (2,4 mal aplicadas por cada regla que falló, 0 fallos heredados del EFE). Ninguna pide mover un número. Aprobada por el usuario el 17/11/2026 con todas las recomendaciones (`docs/revisiones/DTP_v1.9_propuesta.md`), y aplicada junto con el núcleo (`docs/revisiones/NUCLEO_SKILLS_propuesta.md`).**
>
> **1. Posesión: «arriba» siempre aparte** —se borra la condición «cuando el foco no es favorito, o puede ponerse arriba temprano» (decisión del usuario)—; sin referencia, «arriba» es menos pelota que en igualado, y **el perfil del rival dice de dónde sale** (sede, DT, `n`). 0 sostenidas y 12 mal aplicadas en 11 partidos (Bélgica–Italia 1528983, Chipre–Montenegro 1528979, Nacional–Albion 1649060, Suecia–Bosnia 1528978, Türkiye–Bélgica 1528958; UCV–Grau 1549560, JPII–Garcilaso 1549559, Belarus–Albania 1528980, Cali–Tolima 1549867, Moldavia–Kazajistán 1528968, Italia–Francia 1528960). En contra, anotado (un caso cada uno, no entran): Suecia–Bosnia 1528978:b (con el favorito 3-0 arriba, el que persigue domina la pelota, 58 %: el espejo persiguiendo, candidato) e Independiente Petrolero–Always Ready 1649146 (copa, ida de llave).
>
> **2. El reconvertido también ataca, de candidato a regla**: 4 limpios en 4 partidos (Leones del Norte, Telstar–Utrecht 1552214, Países Bajos–Grecia 1528966, Suecia–Bosnia 1528978:a:3); con reserva, Kosovo–Israel 1528971 y Cajamarca 1549549; de copa, Peña Sport. Corrección al estudio: contaba a Kosovo entre los cuatro; con Suecia el umbral se cumple sin la reserva.
>
> **3. La presión alta, con su vuelta, de candidato a regla** (decisión del usuario: entra justo en el umbral): Utrecht–NEC 1552223, Bodø–Lille 1635640 y España–Inglaterra 1528984:a:4; apoyo sin sumar, Inglaterra–Croacia 1528962. Chequia–España 1528961:b:7 queda fuera: lo cubre la transición del favorito.
>
> **4. Pelota parada: la materia sale del cruce y se lee por rama** (Letonia–Armenia 1545616, Luxemburgo–Estonia 1545614, Nacional–Albion 1649060:b:3, Llaneros–Chicó 1549870; confirman la vigente Mirassol 1492455 y Defensor 1649062). Resuelve «condicional no es descartada» contra «sin materia no sostiene».
>
> **5. Con la base corta (0 o 1 penal), el 9 titular entra en la lista** (Cali–Tolima 1549867, Bulgaria–Islandia 1528969, Italia–Francia 1528960; de copa, Boston River–Torque 1649432 y Tarancón–Levante 1644379). Suma un nombre, no reemplaza a nadie. Chequia–España 1528961 es cumplimiento.
>
> **6. Lista de salida de `viasGol`**: forma, sin regla nueva; junta lo obligatorio de la v1.4 a la v1.9 (8 mal aplicadas en 8 partidos, cada una con un renglón distinto: Estonia–Bulgaria 1528988, Chipre–Montenegro 1528979, Albion 1649060, Santa Fe 1549869, Irlanda del Norte 1528975, Suecia 1528978, Escocia 1545659, Tavernes–Valencia 1644380 de copa).
>
> **7. Banco, grid y rehacer: el texto nombra lo que la app ya da** (`bancoProbable`, FUERA-EN-LA-HOJA `dtpBanco`); el rehacer suma M6 y la referencia de posesión (Mirassol 1492455:b:3). Nota de un caso, que no entra: Moldavia–Kazajistán 1528968 (etiqueta 4-3-3 y cinco en la fila de defensa del grid) va como aviso de la app.
>
> **8. La banda de «parejo» del M5 queda a medición, no entra**: 14 de los 20 `regla_fallo` del M5 eran NEUTRO que el volumen decidió; el problema está en la apertura y las lecciones no dan el número. El plan de medición está en la propuesta (§5).
>
> **9. Núcleo**: las notas v1.1-v1.8 pasan a este archivo tal cual; suben al cuerpo **P1** (v1.3: el once probable es nivel C aunque converjan varias fuentes; ventana de confirmación pendiente) y **P2** (v1.3: la vía del arquero con ≥ 2 intervenciones fallidas con gol en el torneo en curso, que el cuerpo citaba sin definir); los candidatos van en un bloque «Candidatos abiertos (no regla)» al final del M5 (decisión del usuario), que absorbe las líneas de candidatos del checklist y del MECANISMO-ABIERTO.
>
> **Candidatos (en el bloque del cuerpo):** el seguro «sin» persiguiendo (Groningen; Portugal–Dinamarca 1528974; The Strongest de copa), el segundo de la lista de penales recibe la falta (Panathinaikos 1593355; Dinamarca 1528974), el caso de la 6 viaja con el arquero (Villarroel 1645530; Liechtenstein 1528970), los penales concedidos en serie (suma Nacional Potosí 1649149, de copa y del mismo cruce), el rearme del medio y el MECANISMO activo que baja el veredicto (sin casos nuevos).
>
> **Queda fuera:** ningún número se mueve (vida útil, umbrales del MECANISMO, corte de DTP-REHACER, banda de «parejo», xG por penal, magnitud de la posesión); no se reescriben banco, grid, rehacer, M3 ni ceder; candidatos de uno o dos casos (el espejo persiguiendo, la etiqueta contra el grid); nada de copa completa el umbral de ningún punto.
>
> **Choques resueltos al aplicar** (menor cambio, misma intención): (a) el reconvertido citaba «(M2, l. 209)»; con el historial fuera las líneas cambian, y se cita por su título («El mismatch contra un reconvertido»). (b) La sub-viñeta de los penales «debajo de la l. 217» va como renglón hermano de la lista del ejecutor, después de «Con un solo penal…», porque la l. 217 ya es un renglón de esa lista. (c) P2 reemplaza la frase dentro de la misma viñeta de las cuatro líneas obligatorias (la propuesta la daba como bloque aparte). (d) La línea de cabecera del núcleo (§3.2) cambia «el esquema del registro», que es del TDE, por «el texto que cada versión reemplazó», que es lo que este archivo guarda abajo. (e) El candidato del MECANISMO activo junta los dos de la l. 417 (la rama igualado sin corrección, Cúcuta, y el que baja el veredicto, Westerlo) porque la v1.8 los contó como un mismo candidato.
>
> **De dónde sale:** estudio del 17/11 (`estudio_lecciones_2026-11-17/`), 347 lecciones de 81 partidos del 10 al 16/11.

> **v1.8 · 10.11.2026 — Revision desde el dossier de la app SAD: las 1150 lecciones pendientes de la v1.7 (265 partidos del 01/11 al 09/11, en dos cortes del 10/11). Acreditan las `ciega` + `PRE` sin copa ni cuarentena; las 18 de la Copa de la División Profesional de Bolivia y las 15 de cuarentena que enseña fijan rubrica sin sostener cambios. Ninguna pide mover un numero. Decidida por el usuario el 10/11/2026.**
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
>
> **De donde sale:** dossier del 10/11, 1150 lecciones, partidos del 01 al 09/11.

> **v1.7 · 01.11.2026 — Revision desde el dossier de la app SAD: las 660 lecciones posteriores a la v1.6 (160 partidos del 26/10 al 01/11; 162 fallos, 125 parciales y 373 aciertos). 584 son `ciega` + `PRE` y acreditan; 76 son de la Copa del Rey del 29/10 y fijan rubrica sin sostener cambios. Ninguna pide mover un numero. Las 14 de DTP-REHACER `tardio` no eran del skill (la rutina de rehacer corre cada 20 minutos desde el 31/10) y confirman las dos capas. Diez altas de rubrica; ningun umbral tocado. Lo calculable que la app todavia no trae va escrito como «pendiente de la app»: hasta entonces se arma a mano con la ficha.**
>
> **1. El veredicto de cada rama nombra la via entera de esa rama** (Göztepe, Bologna, Fluminense, Dortmund, Estudiantes LP: la rama persiguiendo salio recortada a centros y pelota parada y el gol llego por el banco, la media distancia o la transicion que el propio M2 listaba). Sin via contra el bloque rival, la rama es DESFAVORABLE y no NEUTRO (GO Ahead, Emelec). Con una via de expulsion nombrada, la rama mas probable se escribe tambien con uno menos, y una rama jugada con diferencia numerica queda no puesta a prueba (Melgar, Bulo Bulo, Cuenca, Bucaramanga, Medellin). Al rehacer se reescriben las razones de las dos ramas (Llaneros, Rubio Ñu). Dos FAVORABLE en la misma rama del mismo partido se contradicen (Gladbach–Paderborn).
>
> **2. M5: el volumen se cuenta donde se remata** (Kocaelispor: 14 remates, 10 de afuera, 0,59 de xG), sin stats en la ficha el volumen no se juzga (Metropolitanos, Puerto Cabello) y un acierto por encima de lo generado no confirma el veredicto (Milan–Inter, Brentford, Brugge).
>
> **3. El banco ofensivo va en todas las ramas, de los dos lados, entero y por rol**, con el titular habitual rotado primero (Cambuur, Juarez, Talleres, Peñarol, Fenerbahçe, Casa Pia). Es la regla que mas se incumplio: 26 fallos y parciales.
>
> **4. El ejecutor de penales es una lista de dos, condicionada a quien este en cancha**; con un solo penal en la temporada la base no lo fija, y sin penales va el lanzador de pelota parada (Once Caldas, Aston Villa, Atletico-MG, Monagas, UTC, Cerro, San Lorenzo, Parma).
>
> **5. La pregunta 6: la linea del caso se comprueba contra el once** (Manchester City, Junior, Instituto, Wanderers, Portuguesa) **y la 6 mide sostener un resultado, no aguantar el arranque** (Cucuta, Trinidense, San Lorenzo, Riestra).
>
> **6. El costo de rearmar la linea vale en cualquier tramo**, con la pelota parada inmediata a un cambio atras (Emelec, Milan, UCV Moquegua, Instituto, Peñarol, Atletico-MG, Villarreal–Espanyol).
>
> **7. La posesion de cada rama sale de un rival del mismo perfil de balon y con la misma cuenta de jugadores**; sin esa referencia, solo la direccion (Oriente, Fiorentina, Lille, Juan Pablo II, Paderborn, Parma, Stuttgart).
>
> **8. M1: con el once oficial de este partido capturado antes del deposito, manda su grid** (Los Chankas, Tijuana, Medellin); el ultimo once de otra competicion, rotado, no fija la referencia (Mainz); y las amarillas de toda pieza del seguro, no solo del reasignado (Kocaelispor, Ourense).
>
> **9. La pelota parada como via necesita materia** —los corners del cruce; no se rebaja por la fama del arquero— (Oriente, Palmeiras, Cambuur) **y la media distancia va en las dos direcciones** (Fluminense, Talleres, Pachuca).
>
> **10. MECANISMO-ABIERTO: la frecuencia se cuenta** (pares de goles a ≤ 15 minutos, correccion entre ellos, asistidor repetido: Tigres, Estudiantes, Monterrey); la mecanica sigue siendo juicio.
>
> **Candidatos anotados, no regla (un caso cada uno):** un 1-0 once contra once no prueba administrar una ventaja amplia cediendo la pelota (Instituto); el reconvertido tambien ataca (Leones del Norte, Peña Sport); con MECANISMO-ABIERTO activo y la misma pieza sola, la rama igualado no sale FAVORABLE sin una correccion nombrada (Cucuta); los penales concedidos en serie son del equipo, no de la linea (La Guaira); con la 1 y la 2 del lado improvisado, 3 de 5 estructurales quizas no alcanzan para 80-90 (San Lorenzo); el mismatch contra un lateral suplente que nadie ataca (Lille–Lens) y el mismatch no condicional que inclina la rama (Cucuta–Aguilas).
>
> **Queda fuera:** ningun numero se mueve (vida util, ≥ 80 % de interpretes, ≥ 2 errores del arquero, ≥ 2 goles en ≤ 15 minutos, corte de ausentes de DTP-REHACER); ninguna ventana de minutos para el costo de rearmar; la magnitud de la posesion; la herencia del SOB2 desde la rama persiguiendo (decision del usuario); `rolesVsGrid` sigue en sombra (incidencia 646); el casillero del DTP en la taxonomia de Jev (decision del usuario); la rotacion en copa con la liga a ≤ 3 dias ya la cubre la v1.5.

> **v1.6 · 26.10.2026 — Revision desde el dossier de la app SAD: las 123 lecciones del 25/10 (30 partidos, 45 fallos y 32 parciales `ciega` + `PRE`), ninguna pide mover un numero. Doce «DTP-REHACER sono y no se rehizo» no eran del skill: la API corrigio el once despues del ultimo disparo de la rutina (resuelto en la app: `momento` de la alerta). Siete altas de rubrica; ningun umbral tocado.**
>
> **1. El veredicto del M2 en las dos ramas** (Sporting–Viseu, Rio Ave–Famalicao, Nacional–Braga, Toulouse–Troyes, Auxerre–Le Mans, Barcelona–Real Madrid): uno para igualado o arriba y otro para persiguiendo, con la via de cada rama. Que el rival ceda la pelota puede ser su plan, no una señal a favor.
>
> **2. El area desde el lado debil y desde la segunda linea** (Nacional–Liverpool, Sporting–Viseu, Real Sociedad–Levante, Lecce–Juventus, Pumas–Tigres): quien llega al segundo palo y quien lo defiende, la llegada del interior o el pivote, el centro por zona y altura.
>
> **3. M1 desde el ultimo once oficial y su grid** (Emelec, Aucas, Torque, Rennes), con dos excepciones: el sistema nacido de una expulsion temprana (Pumas) y las dos variantes cuando el EFE o la señal del once anuncian otra linea (Nacional–Braga, Angers).
>
> **4. El ejecutor de penales sale de la base** (seis partidos sin nombrarlo y con penal): la app lo da en los insumos; «por jerarquia» no es fuente.
>
> **5. La pregunta 6 con sede y competicion** (Libertad, Lecce: un caso de la otra sede), la 1 mide el modelo y no al DT (Famalicao) y un repliegue anunciado por el DT es plan (Nacional).
>
> **6. Tres candidatos que juntaron sus casos:** el costo de rearmar la linea (tercer caso, Nacional–Liverpool), el rol reasignado con carga de tarjetas (Grau, Aucas) y el remate de media distancia contra un bloque estructural (LDU–Macara, Once Caldas–Pereira).
>
> **7. M5 separa volumen de conversion** (Emelec, Sunderland, Sporting): el veredicto se juzga por lo que genero la rama jugada.
>
> **Queda fuera:** la magnitud de la posesion por rama (cuatro casos en direcciones distintas), la herencia del SOB2 desde la rama persiguiendo (decision del usuario) y la incidencia 634 del modo rehacer (pipeline).

> **v1.5 · 25.10.2026 — Revision desde el dossier de la app SAD: lo posterior a la v1.4 (21 al 24/10), 183 fallos y parciales `ciega` + `PRE` de 48 partidos, ninguno pide mover un numero. En 66 de los 183 la via, el carril o la capa estructural se cumplio y fallo el 1X2: confirman la v1.4. Seis altas de rubrica; ningun umbral tocado.**
>
> **1. Quinta linea obligatoria de vias de gol: el error en la salida bajo presion** (el hueco declarado de la v1.4, con siete casos ciegos: Real Potosi, Always Ready, Alverca, Levante, La Louviere, Brest, Valencia). Y tres precisiones a las cuatro de la v1.4: el ejecutor de penales en las dos direcciones y nunca «sin dato» (Defensor–Racing, Rayo–Elche, Antwerp, Monagas); la pelota parada por zona, con el lanzador de tiro libre directo y la segunda jugada (Llaneros–Cali, Toluca, Juarez); el banco ofensivo es via de los dos lados y por rol (Vasco–Boca, Central Español, 2 de Mayo, The Strongest).
>
> **2. El caso de la pregunta 6, uno solo y completo:** con uno mas no prueba (Arouca); un 0-0 es caso solo si el empate le servia (Palmeiras sí, Coventry no); dice si sostuvo el bloque o el arquero (Nice, Muslera); viaja con la linea que lo sostuvo (Gimnasia de Mendoza); manda el caso comparable mas reciente (Arsenal).
>
> **3. Regla del estado de marcador.** La posesion condicional (v1.2) se amplia: posesion, forma sin balon, seguro de atras y plan de transicion se declaran en dos ramas, igualado o arriba y persiguiendo (Real Potosi, Vasco, Manta, Audax, Valencia, Rayo, Chico–Bucaramanga, Torque).
>
> **4. MECANISMO-ABIERTO con mecanica es via declarada, y el de transicion viaja condicional al regimen** (Alaves–Malaga; Tigres–Leon no viajo; Sporting, Toluca, OH Leuven, La Louviere).
>
> **5. Los dos carriles de cada equipo, con ida y vuelta, tambien el «parejo»** (Sporting–LASK, Lille, Levante, Palmeiras: el gol llego por el carril que no se escribio).
>
> **6. Lo que el M2 nombra se compara con el once:** `xiReferencia` obligatorio en los dos bloques, el M2 declara sus piezas, y con rotacion posible en M6 la capa de nombres va en dos versiones o no va (Alaves–Malaga, Koln–Schalke, Valencia, La Louviere, incidencia 525).
>
> **Queda fuera:** la herencia del SOB2 del TDE desde la rama persiguiendo es una decision aparte del usuario; hasta entonces hereda el nivel de hoy. **Candidatos no aplicados:** el costo de rearmar la linea en un doble cambio (segundo caso, Manta–Cuenca), el remate de media distancia contra un bloque estructural (LDU–Macara), la cadena de tres arqueros (Chico), el rol reasignado con carga de tarjetas (Grau), y la eliminacion cercana sobre el once repetido en M6 (IdV).

> **v1.4 · 21.10.2026 — Revision desde el dossier de la app SAD: 57 casos PRE ciegos de la cohorte `c3-2026-09-23`, 503 lecciones acreditables, ninguna pide mover un numero. La capa acierta mas de lo que dicen sus fallos —en muchos «fallos» del lado la via escrita fue literalmente la del gol y lo que fallo fue el 1X2—, y sus huecos son de rubrica, no de calibracion. Seis altas; ningun umbral tocado.**
>
> **1. `MECANISMO-ABIERTO · sin mecanica`.** En unos diez cierres hubo dos o mas goles del mismo equipo en pocos minutos o sin correccion en vivo y ninguna fuente nombraba la jugada (Puerto Cabello, La Guaira, Alianza Atletico, Atletico Tucuman, Torque, Delfin, Betis–Barcelona, Monza–Cagliari): cada analista lo resolvio distinto. Ahora es una clase con nombre: entra al M2 del proximo rival como **via a verificar**, nivel de dato C, sin degradar K.
>
> **2. El mecanismo se nombra por la zona o el rol, no por el interprete.** Porto concedio por el carril de su lateral izquierdo con OTRO lateral; Wanderers volvio a perder la marca del segundo palo en juego abierto y no de corner; Leon hizo sus tres goles de corner con tres rematadores distintos. El umbral de ≥80% de interpretes queda para los mecanismos de PAREJA (dos centrales, doble pivote); el de carril o zona sigue abierto mientras el rol se repita. Contraste: con DT nuevo o media linea cambiada no viaja (Corinthians, Newcastle).
>
> **3. El duelo por carril se escribe en las dos direcciones.** Guarani, Lille–Brest, Fluminense–Palmeiras, Gladbach–Hoffenheim y Shakhtar–AEK: el carril que se cargaba para atacar fue por donde concedieron. Un mismatch «a favor» sin su cara de vuelta esta incompleto.
>
> **4. Cuatro lineas obligatorias de vias de gol.** Via aerea por centro Y por pelota parada (Torque, Guabira); el duelo aereo con todos los que atacan el area, centrales incluidos (Juventus–Lazio, Estudiantes–San Lorenzo); el banco del que persigue (Alaves, Villarreal, Central Cordoba); el ejecutor de penales del rival (Monagas, Barracas, Mushuc). El umbral de ≥2 errores para la via del arquero se mantiene (Atletico: un suplente no es via por serlo).
>
> **5. Checklist: la pregunta 6 y la 4, mas precisas.** El caso de la 6 es una ventaja o un empate sostenido contra un obligado en sede y competicion comparables (Villarreal: el caso de local no probo el bloque fuera; Manta: un 0-0 no prueba cerrar una ventaja), sostener con uno menos cuenta (Atletico, Getafe, America), y **el cierre escribe el caso de la 6** para la apertura siguiente, que hoy se descubria a mano en cada cierre (~15). La 4 se mide por lo que el DT cambio de verdad, no por el conteo de lesionados (Alianza Valledupar, Pereira). La vida util 55-65 del improvisado es techo, no piso (Parma, Angers, Fiorentina).
>
> **6. Con el once en nivel C, M2 en dos capas.** En ~15 cierres sono DTP-REHACER y el mapa describia otro equipo; lo que sobrevivio al once rotado fueron los carriles y los mecanismos (Rayo: «el mapa acerto el carril aun con el XI rotado en tres nombres»). Capa estructural (carril, zona, mecanismo) que vale con nivel C; capa de duelo con nombre propio, condicional al once, que sin rehacer se lee como apertura caida.
>
> **Hueco declarado, no aplicado:** la clase del bloque no cubre el error en la salida bajo presion (Cagliari concedio cuatro siendo estructural y probado): es via de gol de M2, no clase de bloque. **Candidatos no aplicados (un caso cada uno):** arquero sin dueño (≥3 arqueros en la temporada, Estudiantes de Rio Cuarto) y el costo de rearmar la linea en un doble cambio (Sarmiento).

> **v1.3 · 13.09.2026 — Post-caso Alianza Lima 1-2 Universitario (F9 Clausura Perú). La predicción más valiosa de toda la sesión salió de esta capa y no del clasificador ni del módulo del tramo final.** Dos altas.
>
> **1. La vía de gol por error del arquero se declara como vía, con su umbral, y no como color.** En la sesión del caso se escribió, dos veces y antes del pitazo: *error de salida del arquero local — mecanismo con dos antecedentes documentados este torneo, declararlo como vía y no como accidente*. El partido lo decidió una mala salida al 90+7. **Regla: cuando un arquero acumula ≥2 intervenciones fallidas con gol en el torneo en curso, entra en el listado de vías de gol del rival en M2, con el mismo estatus que un centro al segundo palo o una pelota parada.** No es una predicción de que va a fallar: es la constatación de que el mecanismo tiene frecuencia observada y merece casillero. Nace de un hueco entre `B6` del clasificador —que mide continuidad, no forma— y la bandera `ARQUERO-NUEVO` del tramo final —que se activa porque el arquero es otro, no porque esté fallando—. Candidato cruzado `GK-FALLA-ACTIVA` declarado en las dos capas vecinas.
>
> **2. El once probable es nivel de dato C aunque converjan cuatro fuentes, y el mapa de duelos hereda ese nivel.** Cuatro previas peruanas dieron la misma alineación del local y jugó un titular que ninguna había nombrado. **La convergencia entre redacciones es copia, no observación independiente.** M1 y M2 se apoyan íntegramente en el once: cuando el análisis se cierra antes de la publicación oficial —alrededor de sesenta minutos antes del inicio— el documento declara la **ventana de confirmación pendiente** y ofrece rehacer el mapa de duelos, en lugar de presentar el once probable como lista. Un mapa de duelos construido sobre dos nombres equivocados describe un partido que no se jugó.
>
> **Lo que esta capa acertó y conviene no borrar.** El checklist de seis preguntas clasificó el bloque visitante como **estructural y probado** con caso nombrado, se descartó explícitamente la lectura de que se caía pasada la hora, y el bloque sostuvo un 1-0 durante 61 minutos sin partirse. La regla de posesión condicional funcionó: se declaró que el perfil de balón dependía del marcador y no de los escudos, y así fue. El seguro tras la pérdida se declaró frágil en el local y sólido en el visitante, y por ahí llegó el gol del partido.

> **v1.2 · 30.08.2026 — Post-caso CD Moquegua 1-4 Alianza Atlético (F7 Clausura Perú).** Dos altas. La **sexta pregunta del checklist de clasificación del bloque** y con ella la clase **`no probado`**: un bloque puede dar estructural en las cinco preguntas de insumo y no haber sido puesto a prueba nunca, y en ese caso la alerta de degradación **no** se suprime. Y la **regla de posesión condicional**: el perfil de balón es una constante de la interacción, no del equipo, y se declara junto al estado de marcador que lo produjo. Caso de referencia del falso positivo: un bloque con cinco de cinco del lado estructural que concedió tres goles, y cuyo perfil de posesión importado —77% de balón cedido— se invirtió en el partido, terminando con más pases que el rival.

> **v1.1 · 22.08.2026 — Post-caso Hull City 2-0 Manchester United.** Tres altas: el **checklist de clasificación del bloque** (obligatorio en M2 antes de invocar cualquier número de minutos), el mecanismo **`MECANISMO-ABIERTO`** (trasladado desde el clasificador EFE, donde estaba mal alojado) y la **regla de minutos compartidos**, que baja del Bloque F del EFE y alimenta el seguro tras la pérdida.

## Texto de la v1.8 que la v1.9 reemplazó o movió

Literal, para comparar. Cada pieza tiene su reemplazo aprobado en el `SKILL.md` de la v1.9 (o, los candidatos, su línea en «Candidatos abiertos»).

- **M1, l. 196 de la v1.8 (candidato del reconvertido):**

  >   - *Candidato, no regla (v1.7):* **el reconvertido también ataca**. Leones del Norte: Luque, volante de lateral, se leyó solo como vulnerabilidad e hizo los dos goles; Peña Sport (copa): el lateral juvenil señalado como mismatch a favor hizo el 1-0. Su cara ofensiva iría a las vías; falta juntar casos. *(v1.8)* Suma Telstar–Utrecht (Martha, lateral de origen de mediapunta, asistió el 2-0 y marcó el 4-2) y, con reserva, Cajamarca–Alianza Atlético (la lección no dice si el lateral nuevo estaba reasignado): dos casos limpios; sigue candidato (decisión del usuario del 10/11).

- **M2, l. 211 de la v1.8 (frase del umbral del arquero):**

  > El umbral de ≥2 errores para la vía del arquero (v1.3) se mantiene.

- **M2, l. 229 de la v1.8:**

  > El rol de la hoja en la lista calculada del banco está **pendiente de la app**.

- **M2, l. 231 de la v1.8 (la frase final; lo que sigue es la viñeta de la l. 232, sin cambio):**

  > El aviso del recibo está **pendiente de la app**.
  >     - **El banco va sin minuto fijo**

- **M2, l. 233 de la v1.8:**

  > La lista calculada del banco en los insumos, el campo del banco en el parte y el aviso del recibo cuando falta un lado están **pendientes de la app**: hasta entonces se arma a mano, de los dos lados, y entra a `viasGol`.

- **M2, l. 254 de la v1.8 (la enumeración):**

  > M1, M2 (duelos, vías y las dos ramas), M3 (palancas) y `m2.piezas`

- **checklist, l. 290 de la v1.8 (candidatos; pasan a «Candidatos abiertos»):**

  >   - *Candidatos, no regla (v1.7):* un 1-0 once contra once **no prueba administrar una ventaja amplia cediendo la pelota** (Instituto no sostuvo un 3-0 con uno más, cediendo el 74 %); y con la 1 y la 2 del lado improvisado, 3 de 5 del lado estructural quizás no alcanzan para la vida útil de 80-90 (San Lorenzo). Un caso cada uno: el recuento del checklist no cambia.

- **MECANISMO-ABIERTO, l. 417 de la v1.8 (candidatos; pasan a «Candidatos abiertos»):**

  > - *Candidatos, no regla (v1.7, un caso cada uno):* con MECANISMO-ABIERTO activo y la misma pieza sola, la rama igualado no sale FAVORABLE sin una corrección nombrada (Cúcuta); los penales concedidos en serie son un mecanismo del equipo, no de la línea (La Guaira: tres en dos partidos con dos líneas distintas). *(v1.8)* Suman casos, sin llegar a regla: el MECANISMO activo que baja el veredicto (Westerlo, segundo caso) y los penales concedidos en serie (Portuguesa–La Guaira y Universitario–UCV Moquegua: tres casos, dos del mismo cruce; espera uno de otro equipo, decisión del usuario del 10/11).

- **posesión, l. 314 de la v1.8 (la condición, borrada por decisión del usuario):**

  > - Cuando el foco no es favorito, o puede ponerse arriba temprano, la posesión de la rama se escribe en dos: **igualado** y **arriba**.
