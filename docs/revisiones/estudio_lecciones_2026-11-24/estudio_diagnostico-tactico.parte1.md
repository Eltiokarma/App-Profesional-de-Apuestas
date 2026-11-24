# DTP v1.9 · lecciones pendientes del 17 al 21/11/2026 (parte 1 de 2)

**Insumo:** 270 lecciones de 65 partidos (17/11: 28, 18/11: 39, 19/11: 29, 20/11: 73, 21/11: 101). **20 son de copa nacional** (7 partidos: Copa del Rey 1644334, 1644346, 1644353, 1644369, 1644373, 1644384, y Copa de la División Profesional de Bolivia 1650230). Enseñan, pero no acreditan. Quedan 250 acreditables. Clasificación por lección: `clasif_diagnostico-tactico.parte1.json`.

## 1. Conteo

| Clase | Todas (270) | Sin copa (250) |
|---|---:|---:|
| regla_sostuvo | 146 | 137 |
| mal_aplicada | 70 | 63 |
| regla_fallo | 44 | 44 |
| insumo (once tardío, pieza fuera del once) | 8 | 5 |
| imprevisto | 1 | 1 |
| no_dice (copa sin stats) | 1 | 0 |
| otro_skill | 0 | 0 |

| Veredicto del lado | n | sostuvo | mal aplic. | falló | insumo | otros |
|---|---:|---:|---:|---:|---:|---:|
| acierto | 114 | 68 | 26 | 16 | 3 | 1 |
| fallo | 102 | 51 | 28 | 20 | 2 | 1 |
| parcial | 54 | 27 | 16 | 8 | 3 | 0 |

Como el 17/11, el veredicto del lado no dice si la regla funcionó: 51 lecciones de lados fallados dicen que la regla se sostuvo. Hay 1,6 lecciones mal aplicadas por cada regla que falló (70 contra 44). El 17/11 eran 2,4. La relación bajó porque **los fallos se concentran en el juicio de volumen del M5** (30 de los 44).

## 2. Tabla por regla (las más frecuentes)

| Regla | n | partidos | sostuvo | fallo | mal aplic. | insumo / otros |
|---|---:|---:|---:|---:|---:|---:|
| M5 · veredicto de la rama contra lo concedido | 59 | 44 | 28 | **30** | 1 | 0 |
| M2 · banco ofensivo (bancoProbable, todas las ramas) | 18 | 14 | 14 | 1 | 3 | 0 |
| Checklist del bloque · pregunta 6 / sostuvoArquero | 17 | 17 | 16 | 0 | 1 | 0 |
| MECANISMO-ABIERTO | 17 | 16 | 16 | 0 | 1 | 0 |
| M2 · ejecutor de penales | 13 | 13 | 10 | 0 | 3 | 0 |
| M2 · pelota parada: materia del cruce, por rama (v1.9) | 13 | 13 | 3 | 1 | **9** | 0 |
| M1 · vía de expulsión (dos lados, toda la línea) | 8 | 8 | 1 | 1 | **6** | 0 |
| M2 · veredicto con condición: línea menos favorable | 8 | 7 | 1 | **4** | 3 | 0 |
| M2 · posesión por rama (perfil en su condición de hoy) | 7 | 7 | 0 | 0 | **7** | 0 |
| M2 · viasGol: lado débil y segunda línea | 7 | 7 | 3 | 0 | 4 | 0 |
| M3 · costo de rearmar la línea | 7 | 7 | 5 | 0 | 2 | 0 |
| M2 · dos capas (once tardío / pieza fuera) | 7 | 7 | 5 | 0 | 0 | 2 insumo |
| Checklist · vida útil del improvisado | 7 | 7 | 5 | 2 | 0 | 0 |
| M3 · quién queda atrás (todas las ramas) | 5 | 5 | 1 | 0 | 4 | 0 |
| DTP-REHACER · momento tardío | 5 | 5 | 0 | 0 | 0 | 5 insumo |
| M2 · el reconvertido también ataca (v1.9) | 4 | 4 | 0 | 0 | 4 | 0 |

Además, con 3 lecciones o menos cada una:
- vía persiguiendo que sobrevive a los cambios: 4, de ellas 3 mal aplicadas;
- pregunta 5 del checklist: 3 mal aplicadas;
- referencia de volumen que no viaja: 3 mal aplicadas, en 2 partidos;
- grid del M1: 3 mal aplicadas;
- media distancia: 2 mal aplicadas;
- al rehacer: 2 mal aplicadas;
- mismatch en las dos direcciones: 3;
- candidato del rearme del medio: 3;
- «arriba» aparte (v1.9): 2 sostuvo y 1 falló;
- la presión alta con su vuelta (v1.9): 1 sostuvo.

**Lo que funciona:**
- MECANISMO-ABIERTO, 16 de 17;
- la pregunta 6 y `sostuvoArquero`, 16 de 17;
- el banco, 14 de 18;
- los penales, 10 de 13;
- las dos capas con el once tardío;
- «sin vía contra el bloque, DESFAVORABLE»;
- el costo de rearmar como vía.

## 3. Patrones con ≥ 3 partidos distintos

### A. M5: 30 veredictos de rama que el volumen contradijo (44 partidos con M5, ninguno de copa). Candidato a medir.

El cierre aplicó bien el juicio contra lo concedido. Lo que falla es la etiqueta de la apertura, de tres formas:
- **NEUTRO-refugio: 14.** El volumen lo resolvió hacia FAVORABLE en 9 casos: Suecia 1528998 (NEUTRO por «la rotación baja la contra»), Santos 1492451, Corinthians 1492450, Grêmio 1492454, Recoleta 1632066, Vélez 1649571, Everton 1505565, Aston Villa 1557467 y Alavés 1570453, este con 3,17 contra 0,24. Lo resolvió hacia DESFAVORABLE en 5: Georgia 1528994, Rumania 1528999, Macará 1639806, Sunderland 1557467 y Fulham 1557474.
- **FAVORABLE de más: 12.** Portugal 1528992, Dinamarca 1528993, Vasco 1492458, Torque 1650502, Guaraní 1632066, Racing M. 1650505, Como 1550200, Lazio 1550202, Atlas 1551040, Coventry 1557471, Arsenal 1557475 y Betis 1570462, este con 0,58 contra 2,25. En 5 de ellos el lado acertó el resultado por conversión (Portugal, Vasco, Como, Lazio y Coventry).
- **DESFAVORABLE de más: 4.** Internacional 1492458, Parma 1550205, Newcastle 1557475 y St. Truiden 1558683.

Comparado con el 17/11: el NEUTRO-refugio **se repite igual** (14, como entonces). El FAVORABLE de más **sube** de unos 6 a 12. Tres lecciones dicen lo mismo: un FAVORABLE o un NEUTRO que se apoya en el nivel o en la contra no escribió cuánto volumen le concede al débil mientras espera (Torque, Vasco y Macará). La regla v1.7 ya pide eso para el DESFAVORABLE; aplicarla también al FAVORABLE sería una aclaración sin número.

**Qué hacer:**
- **Candidato a medir:** la banda de «parejo», que ya figura en DTP_v1.9_propuesta §5. Hay que agregar la lectura (c): ¿el FAVORABLE de la apertura se concentra en un Δ positivo más que el NEUTRO?
- **Aclarar en el skill**, sin número: «FAVORABLE apoyado en el nivel o la transición escribe cuánto concede».

### B. Pelota parada: la materia sale del cruce y se lee por rama (v1.9). 9 mal aplicadas en 9 partidos. Se repite y sube.

La regla de la v1.9 se escribió el 17/11 y no se cumple. Se usa el **promedio propio** de córners:
- Grêmio 1492454;
- Le Havre 1552827 (0 córners);
- Cercle 1558682 (promedio medido con el DT anterior);
- Juárez 1551040 (sacó 9 y marcó dos de cabeza);
- Valencia 1570460;
- Audax 1505563 (sacó 9 persiguiendo);
- Torque 1650502 («con materia», sin los córners que concede el rival).

O no se relee por rama: Chapecoense 1492456 y Georgia 1528994 (este del 17/11).

Hay una regla_fallo: Cruzeiro 1492452. Sin un perfil de balón medido, la pelota parada del local no se rebaja a condicional: cedía según la apertura y tuvo el 62 % y los dos goles. Se sostuvo en 3 casos: Cerro Largo, Excelsior y Newcastle. En los dos últimos la condicional estaba bien declarada y fue gol.

Repetir el texto no cambió la conducta. **Para la app:** los córners que concede el rival por sede, con `n`, en los insumos de `dtp/{id}`. La v1.9 ya dice «sin los córners concedidos en los insumos, se cita la fuente con su n», y nadie lo hizo. Un aviso del recibo cuando la pelota parada se declara sin ese dato.

### C. Posesión: el perfil del rival en su condición de hoy. 7 de 7 mal aplicadas, en 7 partidos.

- Promedio de temporada sin sede, DT ni `n`: Guaraní 1632066, Bucaramanga 1650173, Everton 1505565 y Sevilla 1570462.
- El rival ganando tomado como su perfil en igualado: Polonia 1528998 y Ameliano 1632063 (un solo partido).
- La dirección sacada de la obligación de tabla: Tijuana 1551038.

La forma (a) del 17/11, escribir «igualado o arriba» juntos, **desapareció**: la v1.9 la resolvió. «Arriba, menos pelota» se cumplió en Ucrania 1528994 y Cobresal 1505563. Tiene un contraejemplo, Fluminense 1492457: arriba desde el 32', tuvo el 57 % con «olé», porque es un equipo de posesión que va arriba dentro de su plan. Es un solo caso y no entra.

La forma (b) **se repite**: el texto de la v1.9 («el perfil dice de dónde sale») no se cumple. **Para la app:** el perfil de posesión del rival por sede, con DT y `n`, calculado en los insumos y como campo propio de la rama, como ya proponía el 17/11.

### D. Vía de expulsión, de los dos lados y con toda la línea (renglón 11). 6 mal aplicadas en 6 partidos (1 de copa). Sube.

- Georgia 1528994: no tenía vía propia.
- Kosovo 1528997: nombró al pivote; la roja fue del central, por mano.
- Vitória 1492459: faltó el lateral del duelo.
- Audax 1505563: nombró solo al que estaba al borde del ciclo; el TDE del mismo parte listaba al central expulsado con 4 amarillas.
- Charleroi 1558683: faltó el contenedor del seguro.
- Deportiva Minera 1644353 (copa).

Hay una regla_fallo, Portugal 1528992: la roja fue de un extremo que defendía hacia atrás contra el velocista recién entrado. La regla cubre al reasignado, no al extremo. Es un solo caso.

**Para la app:** el aviso de que una pieza de la línea del duelo o del seguro con amarillas (las del TDE o de `sanciones`) no está en la vía. Audax muestra que el dato ya existía en el parte.

### E. «Si la condición no depende del foco, manda la línea menos favorable» (v1.8). 8 lecciones en 7 partidos, partidas. Aclarar en el skill.

- **Mal aplicada, 3:** Le Havre 1552827, Liverpool M. 1650504 y Charleroi 1558683. Publicaron FAVORABLE o NEUTRO con la condición del rival, y se jugó la línea menos favorable. La regla habría acertado.
- **Regla_fallo, 4:** Boston River 1650500, Köln 1575221, Wanderers 1650504 y Excelsior 1552226. La línea menos favorable no fue la que se jugó, porque la condición era casi segura:
  - lo que el rival hace siempre: Bayern no administra;
  - la obligación de tabla: Boston River;
  - el TDE del propio parte sostenía que el rival «sigue atacando»: Excelsior.
- **Sostuvo, 1:** Central Español 1650505.

**Aclarar:** el defecto «línea menos favorable» vale cuando la condición es incierta. Cuando el propio parte la sostiene con un hecho nombrado (TDE del rival, conducta repetida del DT), la etiqueta es la de la condición y la razón cita ese hecho. Son 4 casos contra 3 y no hay número que mover.

### F. M3: quién queda atrás y el costo del rearme en todas las ramas. 6 mal aplicadas en 6 partidos. Se repite.

- El M3 no escribió la rama igualado o la del que persigue: Coritiba 1492451, Cerro Largo 1650501 y Westerlo 1558682.
- Nombró como «los que quedan atrás» a piezas que el propio rearme sacaba: Central Español 1650505.
- Cambio forzado temprano sin escribir quién cubre: São Paulo 1492457 (al 25') y Santa Fe 1650175 (al 62').

Cambia respecto del 17/11: entonces el fallo era la rama de ventaja, y ahora son la de igualado y la del que persigue. La regla v1.8 ya dice «en todas las ramas»; se incumple. **Aclarar** que el cambio forzado entra (sin ventana, como ya dice la v1.7), o un **campo por rama en el parte** (para la app).

### G. Lista de `viasGol`, renglones 6 y 7. 6 mal aplicadas en 6 partidos.

- Lado débil y segunda línea: Israel 1528996, Polonia 1528998, Atlas 1551040 (el pivote al córner) y PSV 1552229 (el lateral que llega, como rematador).
- Media distancia con todos sus rematadores: Vélez 1649571 (el 9 que baja) y Aston Villa 1557467.
- A eso se suman Macará 1639806 (renglones 1 y 8) y Hungría 1528995 (renglón 5).

Como el 17/11, ningún renglón falla siempre. La lista de salida de la v1.9 todavía no cortó el patrón. Lo arregla **la app** con un recibo por renglón, no el texto.

### H. El reconvertido también ataca (regla nueva de la v1.9). 4 de 4 mal aplicadas.

Cercle 1558682 (Magnée asistió por segundo partido seguido), San Luis 1551039 (Duarte dio el centro del 1-1), Irlanda del Norte 1528995 (del 17/11, quizás con la v1.8) y Tenerife 1644346 (copa).

En los cuatro el reconvertido sí atacó: **la regla se confirma y no se cumple**. Hay 2 acreditables seguros con la v1.9. Es una regla recién escrita: **nada que tocar**, esperar otra semana.

### I. Checklist · pregunta 5 respondida sin el DT de hoy. 3 de 3 mal aplicadas, y el improvisado que sostiene.

- Con partidos del DT anterior: Vitória 1492459.
- «Reacción» cuando el DT cede la pelota de plan dos partidos seguidos: Cercle, en 1558682:b.
- Con la obligación de tabla y no con lo que hace el DT: Wanderers 1650504.

En los tres, el bloque llamado improvisado o ambiguo sostuvo la ventaja. Además, 2 regla_fallo: Progreso 1650502 y Köln 1575221. Dos improvisados que sostuvieron un empate de 28' y de 37' a 90', el de Köln sin atajadas de su arquero.

**Aclarar:** la 5 se responde con lo que hizo el DT de hoy, con `n`; la obligación de tabla no es evidencia. Que la vida útil de 55-65 se quede corta como techo es un **candidato a medir**: es un número calibrado.

### J. La vía depende de una pieza sin heredero. 3 mal aplicadas y 1 falló, en 4 partidos.

- Botafogo 1492450: la pieza amonestada salió al descanso.
- Maldonado 1650500: una pieza amonestada sostenía dos renglones.
- Sevilla 1570462: «la vía se apaga», con el banco heredero ya nombrado.
- Bayern 1575221: el FAVORABLE de igualado dependía de dos piezas que salieron. Esto extiende la regla del que persigue a todas las ramas.

**Aclarar:** «un renglón que depende de una pieza escribe su heredero, en todas las ramas».

### K. Candidatos del cuerpo

- **Rearme del medio** (M3). Suma 2 acreditables:
  - Liverpool M. 1650504: el pivote amonestado sale al 28' y el gol llega al 31';
  - Chelsea 1557470: Caicedo sale al 22' y el gol llega al 28'.

  Bahía 1492454 tuvo un cambio forzado y no concedió, así que no suma. Con Fiorentina e Instituto son **4 casos en 4 partidos: llega al umbral**.
- **El segundo de la lista de penales recibe la falta:** suma Noruega 1528993 (Ødegaard). Son **3 partidos: llega al umbral**, aunque dos de los tres son selecciones.
- **El seguro «sin» impide un FAVORABLE persiguiendo:** **contraejemplo** acreditable, Noruega 1528993. Persiguió 72 minutos con el seguro «sin» y generó 4,28 contra 1,7. Queda en 2 a favor y 1 en contra.

## 4. Con 1-2 casos (no entran)

- La vía del banco del que persigue dice qué pasa si el DT goleado cierra: Paderborn 1575222.
- La contra tras el córner propio va en las vías del rival: San Luis–Puebla 1551039, dos lecciones del mismo partido.
- El veredicto pesa la vuelta escrita del carril cargado: Feyenoord 1552226.
- La pieza que pierde en la salida se nombra por rol en toda la salida: Newcastle–Arsenal 1557475, dos lecciones.
- Con la pareja central cambiada en el once, la 6 dice «sin dato»: Tottenham 1557476.
- Un mecanismo de zona nacido con otro sistema no viaja: Alavés–Deportivo 1570453 (cumplimiento de la v1.4).
- La rotación sin nada en juego no baja el veredicto sin un hecho: Suecia 1528998.
- La referencia de volumen no viaja: Chelsea–Leeds 1557470 (dos lecciones) e IdV 1639806. Son 2 partidos.
- Penales: falta el 9 del banco «si entra» en Coquimbo 1505565 y en Sabadell 1644384, de copa; el lanzador de pelota parada en cancha en Remo 1492456; el ejecutor del año sin base va primero en Wanderers 1650504. El 9 titular de la v1.9 no falló ninguna vez.
- Banco: el defensor fresco en Niza 1552824 y el banco sin minuto fijo en PSG 1552824.
- Extremo expulsado que defendía hacia atrás: Portugal 1528992.
- La presión alta con su vuelta (v1.9) sostuvo en Arsenal 1557475.

## 5. Comparación con el 17/11 y juicio de los arreglos de la app

| Patrón del 17/11 | Esta semana | Juicio |
|---|---|---|
| Posesión por rama (12 mal) | (a) «igualado o arriba» junto: 0. (b) perfil fuera de su condición: 7 mal | (a) desapareció; (b) se repite |
| Banco ofensivo (16 mal en 15 partidos) | 3 mal (1 de copa), 14 sostuvo; 9 lecciones citan la hoja o `bancoProbable` | **bajó mucho** |
| M1 · grid (8 mal) | 3 mal (1 de copa) | bajó |
| Al rehacer (6 mal) | 2 mal (Lecce: el M3 y G-BLOQUE sin rehacer; Mallorca, de copa) | bajó |
| M3 · quién queda atrás (6 mal) | 6 mal, ahora en igualado y persiguiendo | se repite |
| Ceder y la condición con su contrario (5) | Ceder: 1 sostuvo. Línea menos favorable: 3 mal y 4 fallos | cambia de forma: pide aclaración |
| Lista de vías (8 mal, renglones sueltos) | 6 mal en renglones 6 y 7, más la vía de expulsión con 6 | se repite; la vía de expulsión sube |
| Pelota parada (4) | 9 mal con la regla v1.9 ya escrita | **sube** |
| Penales con la base corta (5 mal y 1 fallo) | 3 mal (1 de copa), ninguno del 9 titular | bajó |
| M5 NEUTRO-refugio (14 de 20) | 14 de 30, más 12 FAVORABLE de más | se repite; el FAVORABLE de más sube |
| MECANISMO, la 6 y la vida útil | 16/17 y 16/17 | se sostienen |
| Reconvertido y presión con su vuelta (subieron a regla) | 4 mal (la regla se confirma, no se aplica) y 1 sostuvo | recién escritas |

**Arreglos de la app del 17/11:**
- **`bancoProbable`: sí bajaron los errores.** El banco mal aplicado pasó de 16 a 3, y ninguno es el caso viejo (un titular nombrado como banco, o un banco incompleto). Lo que queda es de rol: el defensor fresco de Niza, aunque `bancoProbable` trae `lateral`; el minuto fijo, y una razón que no cita su renglón.
- **El rehacer por la hoja (FUERA-EN-LA-HOJA, ONCE-SIN-FILA-F1) y EFE-RECOMPUTO-PENDIENTE: bajaron** el grid (de 8 a 3) y el rehacer (de 6 a 2). Quedan dos huecos:
  - Sevilla 1570462: el once se capturó a las 17:03 y el último depósito fue a las 17:15, sin copiar el grid. Vale ver por qué no saltó el aviso.
  - El insumo dominante ya no es del rehacer. En **18 lecciones de 16 partidos** la API corrigió la formación o el grid **después del pitazo** (DTP-REHACER `tardio`). Ningún rehacer lo alcanza. Las lecciones lo cobran bien, como apertura caída y no como fallo. La capa estructural se sostuvo en casi todas: Bosnia, Cobresal, Bucaramanga, Leverkusen, Peñarol, Liverpool M.
- **`ventajaPorFuerza` y Jev `lectura`:** no tocan al DTP. Jev puso `lectura` en 10 de las 270 lecciones y ninguna es del EFE.
- **«El banco, la F1 y el arquero sin el partido del homónimo» (21/11 22:50):** sin evidencia. Ninguna lección habla de homónimos, y los partes del 21/11 son anteriores al arreglo.

**¿EFE heredado?** No hay ningún fallo del DTP atribuible al EFE (`otro_skill`: 0). Hay un caso al revés: Audax 1505563. El TDE del parte tenía las amarillas del central expulsado y el DTP no las tomó.

## 6. Rarezas del dato

- **Lecciones del 17/11 (28, de 10 partidos de selecciones, fixtures 15289xx):** pueden haber corrido con la v1.8, porque la v1.9 subió a las 13:20 UTC. Tres citan reglas de la v1.9:
  - 1528994:a:3, «arriba» aparte: sostuvo, y también valía en la v1.8;
  - 1528994:b:4, pelota parada por rama: mal aplicada;
  - 1528995:b, el reconvertido también ataca: mal aplicada. En la v1.8 era candidato y no regla, así que no debería contar como incumplimiento si el parte es anterior a la subida.
- No hay claves ni textos duplicados. No hay lecciones mal atribuidas a otro skill.
- Hay varios partidos con 2 a 4 lecciones de la misma regla de los dos lados (M5 en los dos lados de Vasco–Inter, Villa–Sunderland y Charleroi–STVV). Por eso la tabla separa lecciones y partidos.
- Copa: 20 lecciones; 9 sostuvo, 7 mal aplicadas, 3 insumo y 1 no dice. Ningún patrón de arriba depende de ellas.
