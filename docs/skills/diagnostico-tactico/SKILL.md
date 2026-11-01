---
name: diagnostico-tactico
description: "Analisis tactico-tecnico del juego de un partido de futbol, no estructural. Es la capa de juego del sistema SAD y complementa al EFE. Produce el Diagnostico Tactico de Partido: lectura de alineacion, clasificacion del bloque rival, mapa de duelos por carriles, plan por fases, autopsia de goles con responsables y deteccion de mecanismos abiertos. Funciona como cadena rodante: cada analisis es pre-partido y abre cerrando el anterior. Activar cuando el usuario quiera analizar tacticamente un partido o diga analicemos la formacion o la alineacion, como debe jugar tal equipo para ganar o empatar, por que no funciono el juego, analicemos los goles o la derrota o la victoria, analicemos el equipo que presentara el rival, dame un plan de partido o un mapa de duelos, sea pre o post. Activar tambien tras un EFE cuando se quiere bajar al futbol del partido. No usar para el clasificador EFE ni para constantes K o apuestas."
---

# Diagnóstico Táctico de Partido (DTP) — Capa de Juego del SAD

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

## Qué es y qué NO es

El SAD tiene tres capas. No las mezcles:

| Capa | Pregunta que responde | Skill |
|------|----------------------|-------|
| **EFE** | ¿Puedo confiar en la señal histórica (K) de este equipo? | `efe-dashboard` |
| **DTP** *(este skill)* | ¿Cómo se juega y se decide ESTE partido? | `diagnostico-tactico` |
| **K / mercado** | ¿Qué dicen las constantes y el mercado de apuestas? | `sad-analysis` |

El DTP **no usa constantes K ni clasifica estabilidad**. Trabaja con lo que se ve en cancha: sistemas, perfiles individuales, duelos, fases del juego y el contexto del partido. El EFE te dice *cuánto creerle a los datos*; el DTP te dice *el fútbol*.

> **Origen:** el DTP es el "Bloque H" del EFE crecido. El Bloque H del EFE queda como un "DTP-lite" que dispara este análisis completo.

---

## EL PRINCIPIO ORGANIZADOR: LA CADENA RODANTE

**Todo DTP es un documento pre-partido que ABRE cerrando el partido anterior.**

```
DTP(N)  =  [ CIERRE de N-1 ]  +  [ APERTURA de N ]
              M4 + M5              M1 + M2 + M3 + M6
           (post, validación)      (pre, proyección)
```

```
DTP(1):           [APERTURA 1]
DTP(2): [CIERRE 1][APERTURA 2]
DTP(3): [CIERRE 2][APERTURA 3]
```

**Por qué importa:** el pre-partido es lo accionable, pero al obligar a cada pre-partido a empezar cerrando el anterior, el modelo se autovalida continuamente.

**Reglas de la cadena:**
- Si **no hay partido anterior** en la serie → omitir el CIERRE, anotar "Sin partido anterior en la cadena".
- Si **sí hay** un DTP previo → recuperar M2 y M3 del documento anterior y **validarlos honestamente**. No reescribir el pasado.
- "Partido anterior" = el último partido del MISMO equipo foco, sin importar competición.
- **Si el partido anterior es un amistoso** *(v1.1)*, el CIERRE se hace igual pero se declara nivel de dato C: los estímulos son asimétricos y las conclusiones no se transfieren.

---

## FLUJO DE EJECUCIÓN

1. **Investiga en la web (obligatorio).** Para ambos equipos: XI confirmado o el más reciente/probable, sistema, bajas/dudas, **minutos compartidos de las líneas clave**, y el contexto: amistoso o competitivo, rotación, días de descanso, estímulo.
2. **CIERRE del partido anterior** (si aplica): M4 + M5, contrastando con lo pronosticado.
3. **APERTURA:** M1 → M2 → M3.
4. **M6** cruza y matiza todo.
5. **Método de Responsables** en cada evento decisivo.
6. **Entrega** en el formato pedido.

> **Investigación web:** consultas en español con año y nombres entre comillas; consultas secuenciales y específicas por tipo de dato (XI, sistema, bajas, resultado) en vez de una sola amplia. `fetch_sports_data` sirve para EPL/LaLiga/Serie A; NO para Liga 1 Perú ni Liga MX.

---

## MÓDULOS

### M1 — Lectura de Alineación *(pre)*

Lee el XI como una declaración de intenciones. No describas: interpreta.

- **Dibujo y cambios respecto al partido anterior.** *(v1.6)* **El sistema y los carriles salen del último once oficial con su grid** —los insumos de la app lo dan (`partidoAnterior.xi`: formación y carril de cada titular)—, no de la previa ni del dibujo habitual de liga. Apartarse de él es una decisión que se escribe con su fuente («el DT anunció…», «la previa del club…»). Casos: Emelec–Guayaquil City (se leyó línea de tres sobre un grid con cuatro atrás), Aucas–Barcelona SC (dos extremos en el mismo carril que jugaban en bandas opuestas), Torque–Cerro (el lateral derecho en el carril izquierdo), Rennes–Strasbourg (el DT pasó a línea de tres tras una goleada y la sostuvo; la apertura tomó el 4-3-3 habitual). **Dos excepciones:** (a) **un sistema nacido de una expulsión temprana no fija el del partido siguiente**: manda el anterior a la roja y se declaran las dos variantes (Pumas–Tigres: el 5-4-1 de jugar con diez desde el 2'); (b) **cuando el EFE trae otra línea en su caja de sensibilidad, o la señal del once anuncia regresos en una línea**, la forma sin balón se escribe en las dos variantes (Nacional–Braga: la línea de cinco del interino; Angers–Lorient: volvían tres titulares de la zaga).
  - **El once oficial de ESTE partido manda si ya está** *(v1.7)*. Si el once oficial se capturó antes del depósito, el sistema y los carriles salen **de ese grid**, no del último once ni del rol habitual de un jugador. Los Chankas–Cusco: el once final se capturó a las 17:32 UTC con cuatro defensores en la segunda fila del grid y la apertura, depositada a las 17:40, siguió leyendo línea de cinco con Takeuchi de carrilero; Tijuana: el grid ponía cinco en la fila de defensa y se escribió 4-1-4-1 por el rol habitual de un jugador; Medellín: se apartó del último oficial por un probable de prensa, sin anuncio del DT, y salió el último oficial. La app avisa hoy el desvío contra el último once (`M1-VS-ULTIMO-ONCE`); el aviso contra el once oficial de este partido está **pendiente de la app**: hasta entonces, se mira el once antes de depositar.
  - **El último once de otra competición, rotado, no fija la referencia** *(v1.7)*. Mainz: el `xiReferencia` tomó al arquero y a dos medios del once de copa y la vía «error con arquero suplente» quedó sin objeto (en copa, también Eldense y Peña Sport). Cuando el último partido fue de copa, la app ya trae el último once de liga (`ultimoOnceDeLiga` en los insumos del DTP) y el M1 se apoya en ese; el último de **la misma competición** en los demás casos (por ejemplo, una copa internacional entre dos de liga) está **pendiente de la app**. Con rotación anunciada, el sistema también va en dos variantes (v1.5).
- **Roles reasignados** — el dato más jugoso. Un jugador fuera de su puesto natural suele ser la grieta. *(v1.6)* **Un reasignado que persigue al velocista rival es vía de expulsión**: se nombra con sus amarillas recientes (Grau–ADT; Aucas–Barcelona SC: el central adelantado a interior, amonestado al 40', vio la segunda al 70' por una falta sobre la pieza de transición que nombraba el M2).
  - **Las amarillas de toda pieza del seguro, no solo del reasignado** *(v1.7)*. Cada pieza de `m2.piezas` que sostiene el seguro o la línea —el contenedor único, el lateral reconvertido, el central— se nombra con sus amarillas en la competición. La app las trae en la tabla F1 (`GET /analisis/cowork/f1/{id}`, `amarillasEnLaCompeticion`, desde `backend/sanciones.py`): se toman de ahí. Kocaelispor: el contenedor único, amonestado al 16', salió al 63', y el lateral reconvertido vio amarilla al 30', y el M1 nombró solo al reasignado; Ourense (copa): una pieza que venía de una roja vio la segunda amarilla al 88'. Confirma la v1.6: Cuenca, el reconvertido expulsado al 45+1.
  - *Candidato, no regla (v1.7):* **el reconvertido también ataca**. Leones del Norte: Luque, volante de lateral, se leyó solo como vulnerabilidad e hizo los dos goles; Peña Sport (copa): el lateral juvenil señalado como mismatch a favor hizo el 1-0. Su cara ofensiva iría a las vías; falta juntar casos.
- **Qué señala el XI:** ¿plan conservador u ofensivo? ¿busca tener la pelota o cederla?
- **Vulnerabilidad que el propio XI introduce.** Todo plan abre un flanco. Nómbralo.
- **Forma sin balón:** cómo se reordena el dibujo al defender. *(v1.5)* También es condicional: se declara por estado de marcador, como la posesión (ver la regla del estado de marcador). Real Potosí replegó con el 1-0 en El Alto y presionó alto en casa ante el líder.
- **Minutos compartidos** *(v1.1)*: ¿hay dos titulares de la misma línea que nunca jugaron juntos? Si el EFE ya activó `EJE-DEBUTANTE`, heredarlo sin re-investigar.
- **XI de referencia obligatorio** *(v1.5)*: cada bloque —el del foco y el del rival— lleva su `xiReferencia` como **lista de 11 nombres**. Sin previa que lo dé, va **el último once oficial**, y se dice así en `senalXi`. Un `xiReferencia` vacío se rechaza al depositar: sin lista no hay contra qué comparar el once oficial ni DTP-REHACER que avise (Alavés–Málaga, Köln–Schalke, Valencia–Villarreal, Chapecoense en la incidencia 525).

### M2 — Mapa de Enfrentamiento *(pre)*

Cruza los dos perfiles. El fútbol es interacción, no equipos aislados.

- **Sistema vs sistema:** qué produce el choque de esquemas.
- **Duelos por carril** e identificación de **mismatches** concretos. **Cada mismatch se escribe en las dos direcciones** *(v1.4)*: lo que gana el que ataca por ese carril y lo que expone si pierde la pelota —la espalda del lateral que sube—, resuelto por el rest defense de ese lado. Un mismatch «a favor» sin su cara de vuelta está incompleto: en Guaraní, Lille, Fluminense, Gladbach y Shakhtar el carril que se cargaba para atacar fue por donde concedieron. **Los dos carriles de cada equipo, aunque no haya mismatch** *(v1.5)*: cada uno con ida y vuelta (`duelosCarril[].vuelta`). Un carril «parejo» también tiene espalda: se escribe «parejo» con su vuelta y el seguro que la cubre. Un carril omitido es un carril que el cierre no puede juzgar: en Sporting–LASK, Lille–Galatasaray, Levante–Athletic y Palmeiras–Fluminense el gol llegó por el carril que no se escribió. Una vuelta escrita que nunca se atacó (Peñarol) es dato, no fallo.
- **Vida útil del planteo rival** → ver el checklist obligatorio abajo.
- **Vías de gol probables de CADA lado** (no solo del equipo foco): pelota parada, transición, desborde, llegada de segunda línea, cutback. **Cuatro líneas obligatorias** *(v1.4)*: (1) la vía aérea se declara **por centro en juego abierto Y por pelota parada**, no solo la segunda; (2) el duelo aéreo cuenta a **todos los que atacan el área, centrales incluidos**, no solo a la referencia; (3) **el banco del que persigue es vía**: centradores y velocistas frescos que entran a buscar el gol; (4) **el ejecutor de penales del rival se nombra**. El umbral de ≥2 errores para la vía del arquero (v1.3) se mantiene.
  - **Quinta línea: el error en la salida bajo presión** *(v1.5)*. Se escribe **para el rival** cuando se cumplen las dos condiciones: el equipo sale jugando desde atrás —sobre todo con línea de tres, una pareja nueva o un pivote sin rodaje— y el rival presiona alto o tras pérdida (su forma sin balón o sus palancas del 0-25). Se nombra la pieza que recibe bajo presión: el rol, no necesariamente el jugador. Puede ser vía de gol **o de expulsión** (Alverca: mal pase en la salida de tres y roja al 6'). No cambia la clase del bloque. Casos: Real Potosí–Bolívar (estaba en M1 como vulnerabilidad y no como vía, y el 1-0 salió de ahí), Always Ready, Levante–Athletic, La Louvière–Zulte, Brest–Nice, Valencia–Villarreal.
  - **El área desde el lado débil y desde la segunda línea** *(v1.6, amplía la línea 2)*. El gol lo hizo el que llega y no la referencia nombrada en cinco partidos: (1) se escribe **quién llega al segundo palo desde el lado débil** —carrilero, extremo o lateral contrario— **y quién lo defiende** (Nacional–Liverpool: en un espejo 3-4-1-2 el segundo palo lo cubre el carrilero del lado débil, y ahí cabeceó Martirena; Sporting–Viseu: dos goles del extremo del lado débil cerrando al segundo palo; Real Sociedad–Levante: el lateral contrario); (2) se escribe **la llegada de segunda línea del interior o del pivote** cuando el rival deja espacio entre medios y centrales, **también en pelota parada** (Real Sociedad–Levante: Turrientes; Lecce–Juventus: en el tiro libre ensayado atacó el área el interior que llega, no los centrales nombrados); (3) **el centro se nombra por su zona de origen y su altura, raso o aéreo** (Pumas–Tigres: la vía de los centros se cumplió, pero raso desde la izquierda).
  - **El ejecutor de penales sale de la base** *(v1.6)*. Los insumos de la app traen `penales` por equipo: quién tiró en la temporada, con convertidos y errados. Se nombra a ese, en las dos direcciones; **«por jerarquía» no es fuente** (Always Ready–Real Oruro: se escribió «Bravo por jerarquía» y lo tiró el central). Si el arquero rival atajó penales en la temporada, se anota al lado (Monterrey–Chivas: Rangel atajó el de Ocampos). Seis partidos del 25/10 lo dejaron sin nombre o «sin fuente» y en los seis hubo penal.
  - **El ejecutor, una lista de dos condicionada a quién esté en cancha** *(v1.7)*. La regla de la v1.6 se confirmó (Pinares, Colman, Le Fée, Villarreal de Monagas, Corulo, Terrazas); lo que falló fue el nombrado que no estaba en cancha cuando llegó el penal y la base con un solo penal. Se escribe así:
    - **Dos nombres en orden.** Si el de la base no está en el once, o puede salir antes (cambio habitual, amonestado), va primero el titular que lo sigue. Once Caldas: Dayro Moreno en el banco y pateó Barrios, titular; Aston Villa: «quien designe Emery», con los dos de la base en el banco, y lo pateó (y erró) McGinn; Atlético-MG: Jorginho salió al 75' y pateó Carrascal; Monagas: L. González salió al 40' y pateó Basante; Racing (acierto): A. Martínez salió al 29' y pateó I. Rodríguez.
    - **Con un solo penal en la temporada, la base no fija al ejecutor.** Se nombran el de la base y el de jerarquía o el lanzador de pelota parada (UTC: Lliuya, 1 de 1, en cancha, y pateó Arroyo recién entrado; Cerro: B. Morales, 1 de 1, y pateó Alemán, el 10; San Lorenzo: F. Aragón, 1 de 1, y pateó Salcedo, recién entrado).
    - **Sin penales en la base, va el lanzador de pelota parada**, declarado sin fuente (Parma: 0 en la base, pateó Bernabé, el lanzador de pelota parada). Un solo nombre falla igual con la base corta: Coria (copa) nombró al último que pateó, que lo había errado, y pateó Toper.
    - La app trae en `penales` a cada ejecutor con sus convertidos y errados (la muestra es la suma) y si sigue en la plantilla. El último errado de cada uno, si está en el once oficial y el aviso del recibo cuando el primer nombre arranca en el banco están **pendientes de la app**: hasta entonces, se cruza a mano con el once.
  - **El remate de media distancia contra un bloque estructural** *(v1.6)*: cuando el bloque del foco es estructural y no concede transiciones, entre las vías del rival va el remate de media distancia, con su ejecutor (LDU–Macará; Once Caldas–Pereira: un suplente desde más de 30 metros).
  - **La media distancia en las dos direcciones y en la rama persiguiendo** *(v1.7, amplía la de la v1.6)*. Contra un bloque bajo o de cinco que cede la pelota, la media distancia va **en las vías del foco** y en su rama persiguiendo, con su ejecutor: es la vía principal del que tiene la pelota, no una secundaria. Contra un bloque que presiona alto y deja el frontal, va en las del rival. Fluminense: el empate del foco fue del pivote desde afuera; Talleres: 7 de 8 remates de afuera contra un bloque de cinco que cedía; Pachuca: dos goles desde la media luna (también Junior, y Cádiz y Getafe en copa; en aciertos, Barracas y Técnico Universitario). La llegada del pivote **propio** también va en las vías del foco (Moreirense; ya lo decía la v1.6).
  - **La pelota parada como vía necesita materia** *(v1.7)*. La vía de pelota parada lleva **los córners esperados del cruce**: los que saca el foco y los que concede el rival. Si el cruce da pocos, la vía va como **condicional**. Y una vía declarada **no se rebaja por la reputación del arquero rival** sin dato. Oriente: la vía principal (córner y tiro libre lateral contra una pareja nueva) tuvo 0 córners en 90 minutos; Palmeiras: la pelota parada contra el arquero suplente, con 3 córners en el partido; Cambuur: se rebajó la vía de los centrales a «menor» por la fama de Cillessen por alto, sin dato, y dio dos goles. Los córners que saca cada equipo ya los trae la app en `GET /equipos/{id}/stats` (`avanzadas.corners`, con su muestra en `avanzadas.n`); que entren a los insumos del DTP, y los que concede cada equipo, está **pendiente de la app**.
  - **El banco ofensivo, de los dos lados, entero y por rol, en todas las ramas** *(v1.7)*. La v1.4 dijo «el banco del que persigue es vía» y la v1.5, «de los dos lados y por rol»; aun así fue la regla que más se incumplió en la ventana (26 fallos y parciales). Ahora:
    - El banco ofensivo va en las vías **de todas las ramas**, no solo en «persiguiendo». Escrito solo «si persigue», el gol llegó con el equipo ganando o igualado: Cambuur (el 4-0 con 3-0), Juárez (el 3-0 con 2-0), Talleres (el 2-0 con 1-0), Leones del Norte (un defensor que entró con ventaja asistió el 0-2), Central Español (con 1-1), Instituto, UTC, Monagas; Frosinone–Lecce, en acierto: dos goles de un suplente con 3-0.
    - Se escribe **por rol y con todos** los atacantes frescos: delanteros, extremos, mediapuntas y el volante que llega, no solo los conocidos. Peñarol: uno de los nombrados ni estaba en la hoja; Fenerbahçe: se nombró como banco a un titular; Potosí: dos que entraron al 74' y al 86' no estaban; también Fortuna, Ipswich (un pivote), Kifisia, Junior (un volante) y Estudiantes LP.
    - **Primero va el titular habitual rotado al banco**: es la primera pieza del banco del que gana (Casa Pia–Sporting, acierto).
    - El banco se arma con la plantilla y el `xiReferencia`; con el once oficial (modo `rehacer`), son los suplentes reales de la hoja. La lista calculada del banco en los insumos, el campo del banco en el parte y el aviso del recibo cuando falta un lado están **pendientes de la app**: hasta entonces se arma a mano, de los dos lados, y entra a `viasGol`.
  - **Precisiones a las cuatro de la v1.4** *(v1.5)*: el **ejecutor de penales** se escribe **en las dos direcciones** y nunca «sin dato»: sin fuente del partido va el de la temporada, y solo queda vacío si el equipo no tiró ningún penal en el año, dicho así (Defensor–Racing, Rayo–Elche, Antwerp–Charleroi, Monagas). **La pelota parada se nombra por zona** e incluye al **lanzador de tiro libre directo** y la **segunda jugada tras el despeje**, no solo a los rematadores (Llaneros–Cali, Toluca–Tijuana, Juárez–Atlante). **El banco ofensivo es vía de los dos lados y por rol**: también del que gana o va igualado, y cuenta a todos los delanteros frescos, no solo al goleador conocido (Vasco–Boca, Central Español–Albion, 2 de Mayo–Recoleta, The Strongest). Todo entra a la lista de `viasGol`.
- **Dos capas cuando el once es nivel C** *(v1.4)*: M2 separa **lo estructural** —carril, zona, mecanismo, que sobrevive a un once rotado y vale con nivel C— de **los duelos con nombre propio**, que se marcan **condicionales al once**. Si DTP-REHACER suena y no se rehace antes del pitazo, el cierre lee la capa de nombres como **apertura caída**, no como fallo del mecanismo; la capa estructural se juzga igual. El XI de referencia va como **lista de nombres**: escrito como frase no se puede comprobar.
- **Las piezas del M2** *(v1.5)*: el M2 declara en `m2.piezas` los jugadores de los que depende la capa de nombres, propios y rivales —los duelos con nombre, el contenedor del seguro, el ejecutor de penales—, cada uno como `{nombre, lado: foco | rival, rol}`. **Si una pieza arranca en el banco, la capa de nombres cae**, aunque el corte de ausentes no se alcance (Solanke en Tottenham, incidencia 525). **Con M6 marcando rotación posible** —eliminación o copa a ≤6 días, gestión anunciada— la capa de nombres se escribe en dos versiones (con el núcleo y con la rotación) o no se escribe y queda solo la estructural: en La Louvière–Zulte M6 anunció la gestión, el DT rotó cuatro fijos y el arquero, y M1 y M2 se apoyaban en el núcleo que no jugó.
- **Rest defense / seguro tras la pérdida** de cada equipo. Este dato **viaja directo** al indicador de sobreexposición del módulo del tramo final; no se re-estima allá. *(v1.5)* Se declara también **persiguiendo** (`m2.restDefense.nivelFocoPersiguiendo` y `nivelRivalPersiguiendo`: fijo · depende · sin), con la pieza que lo sostiene: el seguro se mide con los centrales arriba, no con el dibujo de partida (Nacional–Trinidense, Valencia–Villarreal; Rayo–Elche, con Ciss único contenedor). Lo que hereda el TDE no cambia: ver Integración.
- **Veredicto:** MATCHUP FAVORABLE / NEUTRO / DESFAVORABLE, con la razón táctica. *(v1.5)* Dice **en qué rama del estado de marcador se apoya**. Si se apoya en que el rival «se abre» o «se vuelca», eso se escribe como condición, porque es lo que el cierre va a mirar (Chicó–Bucaramanga y Palmeiras: el obligado no se volcó; Torque: el que lideraba la llave cedió la pelota).
  - **Dos veredictos, uno por rama** *(v1.6)*. Se escribía uno solo, el de «igualado o arriba», y el partido se jugó en la otra rama en seis casos del 25/10 (Sporting–Viseu, Rio Ave–Famalicão, Nacional–Braga, Toulouse–Troyes, Auxerre–Le Mans, Barcelona–Real Madrid). Ahora el M2 escribe **un veredicto para igualado o arriba y otro para persiguiendo**, cada uno con su razón y **la vía que tendría el foco en esa rama** (`m2.veredictoRamas`). El `veredicto` de siempre queda como el de la rama más probable, y el cierre juzga **el de la rama que se jugó** (la app la calcula de los minutos de gol). **Que el rival ceda la pelota no es una señal a favor del foco: puede ser su plan** (Toulouse, Auxerre y Barça lo leyeron a favor y fue lo contrario); si el rival puede administrar con un bloque bajo, el veredicto «persiguiendo» dice con qué vía se ataca ese bloque, o que no la hay. Un veredicto con condición («si Troyes sale») escribe también qué pasa si no se cumple. Es el mismo arreglo que el TDE v0.1.24 hizo con el `desenlace` de las ramas del que persigue.
  - **El veredicto de cada rama nombra la vía entera de esa rama** *(v1.7)*. Se escribían los dos veredictos, pero la vía de «persiguiendo» salía **recortada** a centros y pelota parada, olvidando lo que el propio M2 ya listaba (17 fallos y parciales). Göztepe: «su vía sería la pelota parada» (DESFAVORABLE) y lo dio vuelta con dos delanteros del banco que el M2 tenía en la lista; Bologna: DESFAVORABLE persiguiendo y remontó con el banco que el M2 escribía (Miranda, 59'); Fluminense: «su única vía son los centros y la pelota parada» y empató con un remate de media distancia del pivote; Dortmund: marcó por transición tras robo, que sigue viva con un rival que sigue atacando; Estudiantes LP: «solo con pelota parada y banco aéreo», 2,03 de xG y tres goles con diez contra un bloque que administraba cediendo; Caracas: el FAVORABLE de igualado no contó el banco del rival, que no perseguía; Oviedo (copa): NEUTRO con el banco de titulares como vía, tres goles en 26 minutos. Por eso:
    - El veredicto de cada rama nombra **todas** las vías que la rama tiene, tomadas de la lista del propio M2: el banco ofensivo, la media distancia, la transición si el rival sigue atacando y la pelota parada.
    - Si después de eso la rama **no tiene vía** contra el bloque del rival, el veredicto es **DESFAVORABLE, no NEUTRO** (GO Ahead: 1 remate al arco en 83 minutos persiguiendo; Emelec: «el banco aéreo que entra al 68' no es vía por sí solo»; Troyes–Le Mans, acierto que lo dice igual).
    - Un veredicto que se apoya en **«la contra del rival»** dice qué pasa si el que gana no quiere correr (San Luis: Atlas no buscó la transición; Ajax–AZ).
  - **Las ramas también por número** *(v1.7)*. Las ramas van por marcador, pero una roja temprana deja la rama jugada en otro partido: Melgar (roja antes del 15': el FAVORABLE de igualado se jugó 90 minutos con diez), Bulo Bulo (con diez desde el 12'), Cuenca (el FAVORABLE se apoyaba en la contra, la primera vía que se cae con diez), Bucaramanga (con diez y perdiendo empató con la transición que se daba por perdida), Medellín (con uno más, el DESFAVORABLE persiguiendo se sostuvo). Con la posesión pasa igual (Gimnasia: 47 % y no el 55-60 % de la rama arriba, con diez desde el 57').
    - Cuando el M2 nombra una **vía de expulsión** (el reasignado con tarjetas de la v1.6, las piezas del seguro amonestadas de la v1.7), el veredicto de la rama más probable escribe también su línea **con uno menos**. Es el mismo arreglo que el TDE v0.1.23 hizo con `siExpulsion`.
    - En el cierre, si la rama jugada pasó **la mayor parte de sus minutos con diferencia numérica**, su veredicto queda **no puesto a prueba**, como la disciplina 17 del TDE: ni acierto ni fallo. La app calcula la rama jugada (`dtp.porBloque[].ramaJugada`); los minutos con diferencia numérica de cada rama están **pendientes de la app**: hasta entonces salen de las rojas de la ficha.
  - **Al rehacer, también el veredicto** *(v1.7)*. En el modo `rehacer`, la razón de las dos ramas se reescribe con el once oficial, no solo M1 y M2, y las piezas que nombran las ramas entran a `m2.piezas` (Llaneros: rehecho, el veredicto siguió nombrando la espalda de un jugador que arrancó en el banco; Rubio Ñu: el DESFAVORABLE se apoyaba en un bloque «rearmado» que el once rehecho ya había cambiado).
  - **Dos FAVORABLE en espejo se contradicen** *(v1.7)*. Si los dos bloques del mismo partido dan FAVORABLE a su foco en la misma rama, se contradicen: Gladbach–Paderborn, 90 minutos de paridad (0,98 contra 1,04 de xG). Se revisa antes de depositar; el aviso del recibo está **pendiente de la app** (un caso: aviso, no rechazo).

#### CHECKLIST DE CLASIFICACIÓN DEL BLOQUE *(NUEVO v1.1, obligatorio)*

> **Antes de invocar cualquier número de minutos de vida útil**, clasificar. La diferencia entre un bloque improvisado y uno estructural no es de grado, es de clase, y confundirlas es un error documentado del sistema.

| # | Pregunta | Improvisado | Estructural |
|---|----------|-------------|-------------|
| 1 | ¿Cuántos meses lleva el equipo jugando con ese modelo defensivo? | <3 | ≥6 |
| 2 | ¿Cuántos minutos competitivos acumula **esa línea de fondo concreta**? | <300 | ≥800 |
| 3 | ¿Los centrales son de oficio o improvisados? | Improvisados / laterales reconvertidos | De oficio |
| 4 | ¿Hay capacidad de refresco? (banco con carrileros y centrales de recambio) | No | Sí |
| 5 | ¿El repliegue está documentado como plan o es una reacción al marcador? | Reacción | Plan |
| **6** *(v1.2, precisada en v1.4 y v1.5)* | **¿Este bloque sostuvo alguna vez una ventaja o un empate contra un rival obligado a atacar, en sede y competición comparables?** | **No: todas las vallas invictas salieron de partidos sin presión real, o el único caso es de otra sede o competición, o con uno más, o lo sostuvo el arquero, o la línea del caso no es la de hoy** | **Sí, con caso concreto nombrado y completo (sostener con uno menos cuenta)** |

**Lectura:**
- **3 o más respuestas en la columna izquierda (preguntas 1-5) → bloque improvisado. Vida útil 55-65 minutos.**
- **3 o más en la derecha (preguntas 1-5) → bloque estructural. Vida útil 80-90 minutos.**
- **La pregunta 6 no cuenta para el recuento: es una llave aparte.** Un bloque estructural con la 6 en la columna izquierda se clasifica **`estructural no probado`**: conserva la vida útil de 80-90 minutos —los insumos son reales— pero **la alerta de degradación SÍ se emite**, y en el módulo del tramo final `C1` puntúa **0.5** en lugar de 0.
- **Empate en las cinco primeras → declarar la ambigüedad y publicar las dos lecturas.** No elegir la que conviene a la narrativa.
- **La pregunta 1 mide el modelo, no al DT** *(v1.6)*: un interino que no toca el modelo no reinicia la 1 (Rio Ave–Famalicão: el 4-2-3-1 venía heredado, el D1 del EFE en ✅, y el bloque sostuvo 42 minutos). Es la trampa frecuente de abajo aplicada al banco.
- **La pregunta 5: un repliegue anunciado por el DT es plan** *(v1.6)*, sea interino o no (Nacional–Braga: «vamos ter de sofrer», y sostuvo 71 minutos sin depender del arquero).
- **La pregunta 4 se responde con lo que el DT cambió de verdad** *(v1.4)*: los cambios de los últimos partidos y en qué líneas, no el conteo de lesionados. Alianza Valledupar se clasificó improvisado por las bajas y su DT hizo cinco cambios con recambio en todas las líneas.
- **La vida útil 55-65 del improvisado es techo, no piso** *(v1.4)*: si el rival ataca la debilidad desde el arranque, se rompe antes (Parma al 4', Angers al 37', Fiorentina al 32').
- **El cierre escribe el caso de la pregunta 6** *(v1.4)*: cuando el partido puso al bloque rival a sostener contra un obligado, el cierre lo anota con su resultado —sostuvo o no, con qué marcador y por cuántos minutos— y la apertura siguiente de ese bloque lo lee de la cadena. En la cohorte c3 el propio partido fue «el caso que le faltaba a la 6» en unos quince cierres.
- **El caso de la 6, completo** *(v1.5)*. Se escribe uno solo, en `cierre.casoBloque` (`sostuvo`, `caso`, `conUnoMenos`, `conUnoMas`, `tipo`, `sostuvoArquero`, `linea`; *v1.6* `sede`, `competicion`), y se lee así:
  - (a) **La igualdad numérica es parte del caso.** Con uno menos cuenta; **con uno más (`conUnoMas`) no prueba** el bloque en igualdad (Arouca sostuvo un 1-0 del 25' al 90' con uno más desde el 6').
  - (b) **`tipo`: `ventaja` · `empate_que_sirve` · `cero_cero`.** Un 0-0 cuenta como caso solo si el empate le servía al que defendía —vuelta de llave, clasificación, título del rival— (`empate_que_sirve`, Palmeiras–Fluminense). Si solo le servía no perder, es `cero_cero`: caso **parcial**, se anota y no promueve solo a `estructural` (Juventud–Peñarol, IdV–Universidad Católica, Coventry–Fulham).
  - (c) **Sostuvo el bloque o el arquero** (`sostuvoArquero`), con el volumen concedido en el tramo (remates o xG). Con penal atajado o atajadas decisivas, se anota y no prueba el bloque (Nice ante Brest, Muslera ante Estudiantes; el contraste es Palmeiras, que sostuvo con el rival en xG 0.24).
  - (d) **El caso viaja con la línea que lo sostuvo** (`linea`: la pareja o la línea). Si el once de hoy cambia la pareja central o la mitad de esa línea, la 6 se responde «no» o «sin dato», con la misma regla que el MECANISMO-ABIERTO (Gimnasia de Mendoza–Platense).
  - (e) **Manda el caso comparable más reciente.** Si la cadena trae casos de los dos signos, el último en sede y competición comparables decide la 6 (Arsenal: el caso de liga ante Forest no se transfirió a la Champions y volvió a perder una ventaja).
  - (f) **La sede y la competición viajan con el caso** *(v1.6)*: `casoBloque.sede` (`local` · `visita` · `neutral`) y `casoBloque.competicion`; si no se escriben, la app las toma del partido que se cierra. Un caso de la otra sede no responde la 6 (Leones del Norte–Libertad: el bloque de cinco se dio por probado con un 4-0 de local y de visita concedió tres; Lecce–Juventus: un caso de visita para un partido de local). Si la 6 se responde del lado estructural con un caso de otra sede, el recibo lo avisa.
  - (g) **La línea del caso se comprueba contra el once** *(v1.7, la (d) que se incumplía)*. Antes de responder la 6 del lado estructural, se compara `casoBloque.linea` con el `xiReferencia` o con el once oficial: si cambió la pareja central o la mitad de la línea, la 6 es «no» o «sin dato». Manchester City: probado con un caso de Dias–Guéhi, jugó Dias–Khusanov y concedió al 11'; Junior: el caso era con Mena y J. Díaz y ninguno estaba en el once; Instituto: el caso con la línea titular y la de hoy rearmada; Wanderers: la 3 y la 6 sobre una pareja que no jugó; Portuguesa: la pareja sin minutos juntos. El contraejemplo (Coventry: «con reserva» con otra pareja, y el bloque sostuvo) no mueve la regla. El aviso del recibo, como el de la sede, está **pendiente de la app**.
  - (h) **El caso lo arma el cierre con la ficha a la vista** *(v1.7)*. 62 cierres rearmaron a mano lo que ya está en la ficha: la sede y la competición, si fue ventaja o empate, desde qué minuto y hasta cuál, si había uno más o uno menos, las atajadas del arquero y el xG en contra, y qué línea de fondo jugó (Remo, Genoa, Cambuur, Aurora, Brighton, Stuttgart, Mechelen, Leones del Norte). El caso precalculado en los insumos del cierre está **pendiente de la app** (hoy solo completa `sede` y `competicion`). Aun precalculado, quedan como juicio **`tipo`** —si el empate le servía depende de la tabla y de la llave— y **`sostuvoArquero`**, que se escribe con los números a la vista.
- **La 6 mide sostener un resultado, no aguantar el arranque** *(v1.7)*. La clase y su vida útil describen al bloque **protegiendo un resultado contra un obligado**. En la rama igualado, el riesgo del arranque se lee en las vías de gol —la quinta línea, el carril, la media distancia—, no en la clase. Una concesión temprana con el marcador igualado **no refuta la clase ni la confirma**: el cierre la anota como **no puesta a prueba**. Cúcuta: el caso era un 1-0 protegido y hoy había que sostener un 0-0 ante un rival que no necesitaba la pelota, y concedió al 33'; Trinidense: estructural y probado con un 1-0 a Libertad, concedió tres en 13 minutos desde el 0-0; San Lorenzo: dos goles entre el 22' y el 25'; Riestra: un gol de media distancia al 25'.
  - *Candidatos, no regla (v1.7):* un 1-0 once contra once **no prueba administrar una ventaja amplia cediendo la pelota** (Instituto no sostuvo un 3-0 con uno más, cediendo el 74 %); y con la 1 y la 2 del lado improvisado, 3 de 5 del lado estructural quizás no alcanzan para la vida útil de 80-90 (San Lorenzo). Un caso cada uno: el recuento del checklist no cambia.
- **Un improvisado que no fue atacado no puso a prueba la vida útil** *(v1.5)*: si no concede porque tiene la pelota o cae por pelota parada, el cierre lo anota como **no puesto a prueba**, no como fallo de la clase (Fulham en Coventry, Juárez–Atlante).

> **De dónde sale la pregunta 6 — falso positivo con cinco de cinco.** CD Moquegua, F7 del Clausura peruano 2026: tres temporadas con el mismo cuerpo técnico, misma línea de fondo desde febrero, centrales de oficio, recambios en el banco, repliegue como plan declarado. Cinco de cinco del lado estructural, alerta de degradación suprimida, y el equipo concedió tres goles. **Sus porterías a cero venían de tres empates y un 0-0: partidos donde el rival nunca tuvo que ir a buscar de verdad.** Las cinco preguntas originales miden lo que el equipo *tiene*; ninguna mide si eso fue puesto a prueba. Un bloque que solo aguantó contra rivales sin urgencia no demostró que aguanta, demostró que no lo atacaron.
>
> **Corolario sobre precedentes.** Un caso anterior del mismo equipo en la misma cancha no vale como precedente si tampoco hubo presión. Y vale al revés: si el bloque sostuvo un resultado contra un rival que necesitaba el gol, nombrar ese partido en el output es lo que convierte la clasificación en evidencia.

> **Trampa frecuente:** el dibujo cambió pero el modelo no. Un equipo que pasó de línea de cuatro a línea de tres sigue teniendo su repliegue entrenado si el modelo de bloque medio-bajo lleva una temporada. La pregunta 1 es sobre el **modelo**, la pregunta 2 sobre la **línea concreta**. Son distintas y las dos cuentan.
>
> **Caso de referencia — falso positivo.** Hull City, F1 Premier League 2026-27: dibujo nuevo (3-4-2-1 en lugar del 4-2-3-1 del ascenso) pero modelo de una temporada entera, centrales de oficio, carrileros con fondo y banco recién comprado. Cuatro de cinco preguntas del lado estructural. El bloque aguantó los 90 con 11 despejes y dos atajadas del arquero.

#### REGLA DE POSESIÓN CONDICIONAL → REGLA DEL ESTADO DE MARCADOR *(NUEVO v1.2, ampliada en v1.5, obligatoria)*

> **El perfil de balón es una constante de la interacción, no del equipo.** Nunca importar un porcentaje de posesión de un partido anterior sin declarar **contra quién** y **con qué marcador** se produjo.

**Ampliación v1.5.** La regla se aplicaba como advertencia y no como pronóstico: se escribía un porcentaje con su contexto al lado y el veredicto se apoyaba en ese número (Vasco recibió al 4' y terminó con 59 %; Manta pasó del 46 % al 58 % en cuanto quedó perdiendo; Audax, declarado 44 % «con ventaja mínima», terminó con 63 % sin ir nunca arriba). Ahora **posesión, forma sin balón, seguro de atrás y plan de transición se declaran en dos ramas: igualado o arriba, y persiguiendo**, cada una con la pieza que la sostiene (el pivote organizador, el contenedor: Bayern–Arsenal fue 42 % sin el organizador). En el parte, `m2.posesion` lleva las dos ramas, `igualadoOArriba` y `persiguiendo`, cada una con `{valor, contraQuien, marcador, sede}`. **Un porcentaje suelto sigue prohibido, y ahora también uno único con el contexto al lado.**

**Precisión v1.7: la referencia sale de un rival del mismo perfil.** El `contraQuien` se escribía, pero el valor se importaba igual de un rival de otro perfil, y esta vez falló **la dirección**, no solo la magnitud. Oriente: 35 % de igualado tomado contra The Strongest, que quería la pelota; contra un visitante en cinco que cedía tuvo 68 %, y el FAVORABLE apoyado en «cede y sale por Flores» describió otro partido. Fiorentina: 37 % importado de San Siro contra el Inter; contra una Atalanta rotada, 60 % y 26 remates. Lille: 36 % de Mónaco, de visita y con diez; de local, once contra once, 62 %. Juan Pablo II: el 30 % ante el líder no viaja a una visita contra un par (53 %). Paderborn: con dos equipos que ceden, decide el perfil del rival, no la sede (57 %). Parma–Udinese: el visitante en 5-4-1 no cedió ante un local rotado en línea de cinco (58 % y 20 remates). Por eso:
- La referencia de posesión de cada rama sale de un partido contra un rival del **mismo perfil de balón que el de hoy** —que quiere la pelota, que la cede o mixto— y con **la misma cuenta de jugadores**.
- **Sin esa referencia, la rama declara solo la dirección** («más pelota que el rival» o «menos»), con su razón, y no un número prestado.
- **La ausencia del organizador se escribe en la rama en que el equipo tiene que salir jugando** (Stuttgart: «sin el organizador la base no sale» pesaba en la rama de salir jugando; ganando desde el 14' cedió el 63 % y salió de contra).
- La magnitud no se calibra: esto corrige la referencia, no el número. Las referencias de posesión calculadas en los insumos (últimos partidos con posesión, el perfil del rival por su posesión media de la temporada, la sede y los minutos con diferencia numérica) y el campo del perfil del rival en `m2.posesion` están **pendientes de la app**: hasta entonces el perfil se escribe en `contraQuien`.

| Lo que se declara | Ejemplo correcto | Ejemplo incorrecto |
|-------------------|------------------|--------------------|
| Rival y su intención con el balón | "Cedió el 77% ante un rival que también quería la pelota" | "Cede el 77%" |
| Estado de marcador dominante | "Cedió el 77% yendo empatado o arriba" | "Es un equipo que cede la pelota" |
| Altitud, sede y competición | "En altura, a 3.050 m, partido de copa" | *(omitido)* |

**Caso de referencia.** En el F7 del Clausura peruano 2026 se modeló al local como bloque medio-bajo cediendo el balón, usando el 77% cedido de su partido anterior en altura. Le empataron al minuto 24 y terminó con **más pases que el visitante**, 351 contra 300, y 19 remates en contra. El mismo equipo, tres días después, con el perfil de posesión invertido, porque el marcador lo obligó a perseguir. **Con el partido a favor un equipo cede; con el partido en contra el mismo equipo acumula pases.**

### M3 — Plan por Fases *(pre)* — es la Matriz de Escenarios

Plan accionable dividido en tramos.

- **0-25':** cómo arrancar (aguantar el ímpetu / golpear si el rival arranca frío).
- **25-65':** gestión del bloque, tempo, alturas de laterales, rol del 9, rest defense.
- **65-80'+:** decisiones según marcador, piernas frescas, balón parado como palanca, riesgos de fatiga. *(v1.6)* **El costo de rearmar la línea**: un cambio obligado que rearma la defensa —lesión de un central, doble cambio atrás— abre un tramo en el que la línea concede; el plan dice quién entra y cómo se reordena, y el cierre lo anota como vía del rival en ese tramo (Sarmiento; Manta–Cuenca; Nacional–Liverpool: la línea de tres rearmada con el cambio demorado concedió por el segundo palo).
- **El costo de rearmar la línea, en cualquier tramo** *(v1.7)*. Ya no es solo del 65-80': se escribe en el M3 como **línea transversal**. Cuentan los cambios obligados y los planificados de la línea de fondo, y también **la roja de un defensor**. Entre las vías del rival entra **la pelota parada inmediata a un cambio atrás**, con las marcas reasignadas (Villarreal–Espanyol: doble cambio al 59' y gol de tiro libre al 60'). El plan del que persigue dice **quién queda atrás después de los cambios** (Estoril, acierto). Casos: Emelec (lateral amonestado sale al 41', gol al 44'), Milan (Tomori al descanso y el otro lateral al 58', goles al 60' y 62'), UCV Moquegua (roja del central y triple cambio al descanso, gol al 66' por el lateral que salió), Central Córdoba (central al 55', goles al 58' y 61'), Instituto (triple cambio al 60' con el central fuera, goles al 65' y 86'), Peñarol (descanso y 70', gol al 72'), Atlético-MG (central por volante al 91', penal al 99'). Es vía, no certeza: Argentinos rearmó al 29' sin conceder, y Sarmiento tampoco. **Sin umbral de minutos**: cuántos minutos «cuentan» lo lee el cierre; fijarlo sería un número nuevo sin con qué calibrarlo. La lista de los rearmes en los insumos del cierre (cambios de la línea de fondo y rojas de defensores, con su minuto y los goles en contra que siguieron) está **pendiente de la app**: hasta entonces sale de los eventos de la ficha.
- Para cada fase, **palancas concretas** — no "jugar mejor", sino "circular vertical en 2-3 toques", "cargar el área con dos centrales altos en córner", "un hombre fijo al rechace del primer palo".
- Si el usuario lo pide, expandir a la **Matriz clásica** (ganar / empatar / no perder).

### M4 — Autopsia de Gol *(post — vive en el CIERRE)*

Por **cada** gol del partido anterior:

```
DISPARADOR  →  SECUENCIA  →  DEFINICIÓN
```

Y aplicar el **Método de Responsables**. Distinguir siempre **mérito** de **error**.

**Formato:**
Gol — Jugador X (min'), marcador. Vía: pelota parada / transición / juego abierto.
- *Disparador:* qué lo originó.
- *Secuencia:* cómo se construyó.
- *Definición:* cómo terminó en gol.
- *Responsables (mérito):* quién asistió, quién definió, qué hicieron bien.
- *Responsables (en contra):* con jerarquía — principal, secundario, estructural.

#### MECANISMO-ABIERTO *(NUEVO v1.1 — trasladado desde el clasificador EFE)*

> **Por qué vive acá y no en el EFE.** Es una observación de la capa de juego: describe cómo se concede, no cuánta confianza merece la serie histórica. En el clasificador estaba declarado como candidato y no tenía dónde aterrizar.

**Activación:** ≥2 goles recibidos que comparten mecanismo identificable —centro y cabezazo, rechace de córner no atacado, pase interior entre líneas, transición por el mismo carril— **en el mismo partido o en partidos consecutivos**.

**Procedimiento:**
1. Nombrar el mecanismo con precisión. No "pelota parada": *"envío al segundo palo con marca zonal y sin hombre asignado al rechace"*.
2. Verificar si **la línea implicada repite ≥80% de sus intérpretes** para la fecha siguiente.
3. Verificar si **hubo corrección en vivo** entre el primer gol y el segundo. Dos concesiones del mismo tipo separadas por más de 15 minutos sin ajuste es un fallo de lectura del banco, no de calidad de los jugadores.

**Efecto:** degradar las K defensivas del equipo **para el partido siguiente** y anotar el mecanismo como vía de gol probable del próximo rival en M2. **No es coeficiente**: es una vía declarada.

**El mecanismo se nombra por la zona o el rol, no por el intérprete** *(v1.4)*. El paso 2 (la línea repite ≥80% de sus intérpretes) vale para los mecanismos de **pareja** —los dos centrales, el doble pivote—. Un mecanismo de **carril o zona** —la espalda del lateral izquierdo, el segundo palo, la salida bajo presión— sigue abierto aunque cambie el intérprete, mientras el rol se repita: Porto concedió por el mismo carril con otro lateral. Con DT nuevo o la mitad de la línea cambiada, no viaja.

**`MECANISMO-ABIERTO · sin mecánica`** *(v1.4)*. Cuando se cumple la frecuencia —≥2 goles del mismo equipo en ≤15 minutos, o sin corrección en vivo entre ellos— y **ninguna fuente nombra la jugada**, no se fabrica la mecánica (la disciplina de no inventar manda) y tampoco se descarta: se declara con esta clase, entra al M2 del próximo rival como **vía a verificar** con nivel de dato C y **no degrada K**. Si la crónica aparece después, se reclasifica.

**Estatus y régimen del mecanismo que viaja** *(v1.5)*. (a) **Con mecánica nombrada** —y la zona o la pareja que se repite— entra al M2 del próximo rival como **vía declarada**, en la lista principal, no como vía a verificar (Alavés–Málaga: el pase interior entre medios y centrales volvió a dar el gol con otro intérprete). `sin mecánica` sigue como vía a verificar, nivel C. (b) **Un mecanismo de transición o de pérdida con el equipo volcado viaja condicional al régimen**: se escribe en la rama «persiguiendo» del M2 y se juzga solo si el equipo tuvo que perseguir (Sporting–LASK, Toluca–Tijuana, OH Leuven–Lommel, La Louvière–Zulte). Si el partido no lo puso a perseguir, el cierre lo anota como **no puesto a prueba**, ni confirmado ni cerrado (Tigres–León: el de pivote único no se arrastró porque León replegó). En el parte, `cierre.mecanismoAbierto.regimen`: `cualquiera` · `persiguiendo`. (c) Los umbrales no cambian: ≥2 goles en ≤15 minutos o sin corrección, y ≥80 % de intérpretes para los de pareja.

**La frecuencia se cuenta; la jugada la nombra el analista** *(v1.7)*. La clase `sin mecánica` se aplicó bien en siete partidos (Cagliari, Trinidense, Fenerbahçe, Estudiantes, Instituto, Monterrey, Tigres; Querétaro heredó un mecanismo que no se repitió y quedó «a verificar», que es lo correcto). Lo que cada cierre hace a mano es **contar**: (1) los pares de goles en contra a ≤ 15 minutos (el umbral del skill, no uno nuevo); (2) si hubo **corrección** entre ellos: un cambio de la línea de fondo o del medio; (3) **quién asistió cada gol** cuando la ficha lo trae: un mismo asistidor en los dos goles ya es pista de zona (Idrissi en Tigres, Luna en Estudiantes, Preciado en Monterrey). Los insumos del cierre traen hoy `partidoAnterior.mecanismoAbiertoCandidato` con un corte más grueso —dos o más goles recibidos, con minuto y autor—; los pares a ≤ 15', la corrección y los asistidores calculados están **pendientes de la app**: hasta entonces se cuentan con los eventos de la ficha. **La mecánica sigue siendo juicio, y sin crónica no se fabrica.**
- *Candidatos, no regla (v1.7, un caso cada uno):* con MECANISMO-ABIERTO activo y la misma pieza sola, la rama igualado no sale FAVORABLE sin una corrección nombrada (Cúcuta); los penales concedidos en serie son un mecanismo del equipo, no de la línea (La Guaira: tres en dos partidos con dos líneas distintas).

> **Caso de referencia.** Manchester United en el MKM Stadium, F1 2026-27: gol al 17' por rechace de córner no atacado, gol al 38' por marca perdida al segundo palo en tiro libre. Veintiún minutos entre los dos, sin ajuste visible del marcaje. La misma línea de fondo repetía intérpretes para la fecha siguiente.

### M5 — Diagnóstico de Fase de Juego *(post — vive en el CIERRE)*

- ¿Funcionó el plan (M3) pronosticado? **¿Hasta qué minuto?** Sé honesto.
- Separa **juego abierto vs balón parado vs transición**: ¿de dónde salió el peligro real?
- **Cronología del giro:** cuándo y por qué cambió el partido.
- **Contraste con el pronóstico previo:** qué acertó, qué no, y qué lección entra a M6/M3 del siguiente.
- **Chequeo de MECANISMO-ABIERTO** *(v1.1)*: ¿hubo dos goles del mismo mecanismo? Si sí, declararlo acá, con su `regimen` *(v1.5)*. Un mecanismo `persiguiendo` heredado que el partido no puso a prueba se anota como **no puesto a prueba**.
- **Chequeo de régimen** *(v1.5)*: ¿en qué rama del estado de marcador se jugó el partido, y era la rama en la que se apoyaba el veredicto del M2? *(v1.6)* Con los dos veredictos, se juzga **el de la rama jugada** (la app la trae en el objetivo del veredicto, `dtp.porBloque[].ramaJugada`).
- **Volumen y conversión, por separado** *(v1.6)*: el veredicto del M2 se juzga por **lo que generó la rama jugada** —remates, xG, ocasiones claras—; la conversión y el arquero rival se anotan aparte como varianza, con el mismo criterio que `sostuvoArquero` pero del otro lado. Un M2 que acertó el partido no se carga como fallo por la definición (Emelec–Guayaquil City: 30 remates y 2,35 de xG contra 9 atajadas; Sunderland–Leeds: dos mano a mano cerrados por el arquero; Sporting–Viseu: 28 remates).
  - **El volumen se cuenta donde se remata** *(v1.7)*. Un FAVORABLE que se apoya en la superioridad en una zona dice **cómo termina en remate dentro del área**, y el cierre mira el volumen **dentro del área antes que el total** (Kocaelispor: la superioridad en el medio, 3 contra 1, dio 14 remates, 10 desde fuera del área, y 0,59 de xG: falló por volumen, no por conversión; igual San Luis, 11 de 22 de afuera, Ameliano, 10 de 15, y Oriente, 11 de 16).
  - **La conversión a favor también va aparte** *(v1.7)*: un acierto que sale por encima de lo generado **no confirma el veredicto** (Milan–Inter: tres goles con 0,74 de xG; Brentford: 2-0 con 0,48; Brugge). Y un DESFAVORABLE que se apoya en el nivel dice **cuánto volumen le concede al débil** (Kifisia generó 1,3 de xG contra 0,92).
  - **Sin stats en la ficha, el volumen no se juzga** *(v1.7)*: el veredicto queda **no evaluable por volumen**, como la rama sin eventos, y el lado no se carga como fallo (Metropolitanos, Puerto Cabello; Unionistas y Torrelavega–Ourense en copa).
  - **De dónde sale el volumen.** Los insumos del cierre traen hoy `partidoAnterior.stats` (remates, al arco y xG de los dos lados). Son números **del partido entero**: la API no los parte por tramo, así que el cierre dice cuánto del partido duró la rama jugada. El volumen completo por bloque en el objetivo del veredicto (dentro y fuera del área, córners, atajadas del arquero rival, la parte de la rama) y la marca de «sin stats» están **pendientes de la app**.
- **El costo de rearmar en el cierre** *(v1.7)*: los cambios de la línea de fondo y las rojas de defensores se anotan con su minuto y los goles en contra que siguieron (ver M3); la ventana la lee el cierre.
- **DTP-REHACER en el cierre** *(v1.6)*: la alerta trae `momento`. `tardio` = el once final llegó a menos de 15 minutos del pitazo, cuando ya nadie podía rehacer: es apertura caída por un once tardío, no un aviso ignorado ni un fallo de esta capa.
- **Chequeo del checklist de bloque** *(v1.1)*: si se clasificó el bloque rival y el partido lo contradijo, anotar **qué pregunta del checklist se respondió mal**, no solo que la alerta falló. El aprendizaje está en la pregunta, no en el número.

### M6 — Moduladores de Contexto *(transversal)*

- **Amistoso vs competitivo:** bajar la confianza; estímulos asimétricos.
- **Rotación / protección de figuras:** un XI muy rotado arranca descoordinado los primeros 20-30'. *(v1.5)* Si M6 marca rotación posible, la capa de nombres del M2 va en dos versiones o no va (ver M2, piezas).
- **Fatiga:** segundo partido en pocos días, viaje, falta de fondo de banco.
- **Ausencias estrella:** quitar a un desequilibrante de 1v1 cambia las vías de gol del rival.
- **Equipo en reconstrucción / XI nuevo:** sin automatismos ensayados, el ataque posicional contra defensas ordenadas suele fallar.
- **Primera fecha del torneo** *(v1.1)*: la ventana de referencia son amistosos, los dos equipos llegan sin automatismos competitivos y **el peso relativo de la pelota parada sube**, porque es la vía que menos depende de coordinación acumulada en juego abierto. Declararlo en M2.

---

## EL MÉTODO DE RESPONSABLES — el sello del DTP

Por cada evento decisivo (gol, ocasión clara, error grave):

1. **Mérito** — quién lo construyó, acción por acción.
2. **Error** — quién lo concedió.
3. **Jerarquía** — reparte: **principal** (el gatillo), **secundario** (mala cobertura), **estructural** (línea alta sin seguro). No descargues todo en una persona si la estructura también falló; tampoco diluyas un error individual claro en "fue colectivo".
4. **Absolución cuando toca** — si la definición fue de mérito en un mano a mano inevitable, el arquero no es responsable. Dilo.

---

## DISCIPLINA — lo que lo salva de ser puro relato

1. **Hecho observable vs interpretación.** Etiqueta la interpretación como tal y dale un nivel de confianza.
2. **Respeto a la varianza.** Un 2-1 tiene poquísimos eventos decisivos. El DTP **describe mecanismos, no decreta causas**.
3. **Anti-hindsight estricto en el CIERRE.** Reconstruye solo con lo reportado. Si el DTP previo falló, regístralo como fallo.
4. **No fabricar mecánica de gol.** Si las fuentes solo dicen "asistencia de X a Y", di lo que hay y marca lo que falta.
5. **Clasificar antes de alarmar** *(v1.1)*. Ninguna alerta de vida útil, degradación o colapso se emite sin haber corrido antes el checklist que le corresponde. Cuando una alerta falla, revisar primero si el paso de clasificación existía.
6. **Declarar la contaminación en el momento en que ocurre** *(v1.1)*. Si el resultado aparece durante la investigación —típicamente al buscar el XI confirmado— decirlo antes de escribir el primer módulo, no al cerrar. Un analista que conoce el desenlace siempre encuentra buenos motivos para haber estado donde el desenlace lo deja parado.

---

## SALIDAS / FORMATOS DE ENTREGA

### A) Dashboard JSX interactivo
React de un solo archivo en `/mnt/user-data/outputs/dtp_[equipos].jsx`:
- **Pizarra de goles:** croquis SVG de cada gol con disparador → secuencia → definición y responsables.
- **Mapa de duelos:** carriles con los mismatches marcados (M2).
- **Checklist de clasificación del bloque** como tabla visible, con su veredicto.
- **Plan por fases:** las tres franjas (M3) con sus palancas.
- **Cierre vs Apertura:** dos secciones claras.
- Tema claro, colores reales de cada club, tipografía legible.

**Validación JSX:** `@babel/parser` con plugin JSX. Copiar a `/mnt/user-data/outputs/` y usar `present_files`.

### B) Reporte escrito estructurado
Orden CIERRE → APERTURA con los módulos como secciones. Prosa directa.

> **Si se usa el visualizer:** caracteres ASCII-safe y JavaScript ES5 (sin arrow functions, sin template literals).

---

## REGISTRO DE LA CADENA — validación acumulada

| Partido | Pronóstico clave del DTP | Qué pasó | Acierto / Fallo | Lección → siguiente |
|---------|--------------------------|----------|-----------------|---------------------|
| N-1 vs … | (vía de gol / matchup / plan) | (resultado real) | ✅ / 🔶 / ❌ | (ajuste que entra a M6/M3) |

Añadir la entrada al cerrar cada partido (M5). Marcar `RETRO` y el tipo de selección cuando corresponda: los casos contaminados fijan rúbrica pero **no acreditan**.

---

## INTEGRACIÓN CON EL ECOSISTEMA SAD

- **Tras un EFE** (`efe-dashboard`): el EFE aporta el contexto de confianza; el DTP, el juego. **Heredar sin re-investigar** B5, D3, F4, F6/`EJE-DEBUTANTE`, el matchup H y las alertas activas.
- **Hacia el módulo del tramo final** (`teorema-del-echado`): el **rest defense de M2 viaja directo** al indicador de seguro tras la pérdida. La **clasificación del bloque de M2** viaja directo al indicador de repliegue entrenado. No se re-estiman. *(v1.5)* El SOB2 **sigue heredando el nivel de hoy** del seguro (`nivelFoco`/`nivelRival`); la rama persiguiendo (`nivelFocoPersiguiendo`/`nivelRivalPersiguiendo`) se declara pero no se hereda hasta que el usuario decida si el SOB2 sale de ella.
- **Matriz de Escenarios:** es la salida M3 en modo prospectivo.
- **Timeline** (`futbol-timeline`): aporta el "qué viene pasando" institucional.
- **Idioma:** español para fútbol latinoamericano y español; inglés para Premier League. **Si el usuario escribe en español, el idioma del usuario manda** sobre esta regla.

> **Cierre de cada entrega:** ofrecer el siguiente paso — la pizarra si entregaste texto, la Matriz ampliada, el timeline de contexto, o el módulo del tramo final.
