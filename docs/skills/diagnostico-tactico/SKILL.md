---
name: diagnostico-tactico
description: "Analisis tactico-tecnico del juego de un partido de futbol, no estructural. Es la capa de juego del sistema SAD y complementa al EFE. Produce el Diagnostico Tactico de Partido: lectura de alineacion, clasificacion del bloque rival, mapa de duelos por carriles, plan por fases, autopsia de goles con responsables y deteccion de mecanismos abiertos. Funciona como cadena rodante: cada analisis es pre-partido y abre cerrando el anterior. Activar cuando el usuario quiera analizar tacticamente un partido o diga analicemos la formacion o la alineacion, como debe jugar tal equipo para ganar o empatar, por que no funciono el juego, analicemos los goles o la derrota o la victoria, analicemos el equipo que presentara el rival, dame un plan de partido o un mapa de duelos, sea pre o post. Activar tambien tras un EFE cuando se quiere bajar al futbol del partido. No usar para el clasificador EFE ni para constantes K o apuestas."
---

# Diagnóstico Táctico de Partido (DTP) — Capa de Juego del SAD

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

- **Dibujo y cambios respecto al partido anterior.**
- **Roles reasignados** — el dato más jugoso. Un jugador fuera de su puesto natural suele ser la grieta.
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
  - **Precisiones a las cuatro de la v1.4** *(v1.5)*: el **ejecutor de penales** se escribe **en las dos direcciones** y nunca «sin dato»: sin fuente del partido va el de la temporada, y solo queda vacío si el equipo no tiró ningún penal en el año, dicho así (Defensor–Racing, Rayo–Elche, Antwerp–Charleroi, Monagas). **La pelota parada se nombra por zona** e incluye al **lanzador de tiro libre directo** y la **segunda jugada tras el despeje**, no solo a los rematadores (Llaneros–Cali, Toluca–Tijuana, Juárez–Atlante). **El banco ofensivo es vía de los dos lados y por rol**: también del que gana o va igualado, y cuenta a todos los delanteros frescos, no solo al goleador conocido (Vasco–Boca, Central Español–Albion, 2 de Mayo–Recoleta, The Strongest). Todo entra a la lista de `viasGol`.
- **Dos capas cuando el once es nivel C** *(v1.4)*: M2 separa **lo estructural** —carril, zona, mecanismo, que sobrevive a un once rotado y vale con nivel C— de **los duelos con nombre propio**, que se marcan **condicionales al once**. Si DTP-REHACER suena y no se rehace antes del pitazo, el cierre lee la capa de nombres como **apertura caída**, no como fallo del mecanismo; la capa estructural se juzga igual. El XI de referencia va como **lista de nombres**: escrito como frase no se puede comprobar.
- **Las piezas del M2** *(v1.5)*: el M2 declara en `m2.piezas` los jugadores de los que depende la capa de nombres, propios y rivales —los duelos con nombre, el contenedor del seguro, el ejecutor de penales—, cada uno como `{nombre, lado: foco | rival, rol}`. **Si una pieza arranca en el banco, la capa de nombres cae**, aunque el corte de ausentes no se alcance (Solanke en Tottenham, incidencia 525). **Con M6 marcando rotación posible** —eliminación o copa a ≤6 días, gestión anunciada— la capa de nombres se escribe en dos versiones (con el núcleo y con la rotación) o no se escribe y queda solo la estructural: en La Louvière–Zulte M6 anunció la gestión, el DT rotó cuatro fijos y el arquero, y M1 y M2 se apoyaban en el núcleo que no jugó.
- **Rest defense / seguro tras la pérdida** de cada equipo. Este dato **viaja directo** al indicador de sobreexposición del módulo del tramo final; no se re-estima allá. *(v1.5)* Se declara también **persiguiendo** (`m2.restDefense.nivelFocoPersiguiendo` y `nivelRivalPersiguiendo`: fijo · depende · sin), con la pieza que lo sostiene: el seguro se mide con los centrales arriba, no con el dibujo de partida (Nacional–Trinidense, Valencia–Villarreal; Rayo–Elche, con Ciss único contenedor). Lo que hereda el TDE no cambia: ver Integración.
- **Veredicto:** MATCHUP FAVORABLE / NEUTRO / DESFAVORABLE, con la razón táctica. *(v1.5)* Dice **en qué rama del estado de marcador se apoya**. Si se apoya en que el rival «se abre» o «se vuelca», eso se escribe como condición, porque es lo que el cierre va a mirar (Chicó–Bucaramanga y Palmeiras: el obligado no se volcó; Torque: el que lideraba la llave cedió la pelota).

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
- **La pregunta 4 se responde con lo que el DT cambió de verdad** *(v1.4)*: los cambios de los últimos partidos y en qué líneas, no el conteo de lesionados. Alianza Valledupar se clasificó improvisado por las bajas y su DT hizo cinco cambios con recambio en todas las líneas.
- **La vida útil 55-65 del improvisado es techo, no piso** *(v1.4)*: si el rival ataca la debilidad desde el arranque, se rompe antes (Parma al 4', Angers al 37', Fiorentina al 32').
- **El cierre escribe el caso de la pregunta 6** *(v1.4)*: cuando el partido puso al bloque rival a sostener contra un obligado, el cierre lo anota con su resultado —sostuvo o no, con qué marcador y por cuántos minutos— y la apertura siguiente de ese bloque lo lee de la cadena. En la cohorte c3 el propio partido fue «el caso que le faltaba a la 6» en unos quince cierres.
- **El caso de la 6, completo** *(v1.5)*. Se escribe uno solo, en `cierre.casoBloque` (`sostuvo`, `caso`, `conUnoMenos`, `conUnoMas`, `tipo`, `sostuvoArquero`, `linea`), y se lee así:
  - (a) **La igualdad numérica es parte del caso.** Con uno menos cuenta; **con uno más (`conUnoMas`) no prueba** el bloque en igualdad (Arouca sostuvo un 1-0 del 25' al 90' con uno más desde el 6').
  - (b) **`tipo`: `ventaja` · `empate_que_sirve` · `cero_cero`.** Un 0-0 cuenta como caso solo si el empate le servía al que defendía —vuelta de llave, clasificación, título del rival— (`empate_que_sirve`, Palmeiras–Fluminense). Si solo le servía no perder, es `cero_cero`: caso **parcial**, se anota y no promueve solo a `estructural` (Juventud–Peñarol, IdV–Universidad Católica, Coventry–Fulham).
  - (c) **Sostuvo el bloque o el arquero** (`sostuvoArquero`), con el volumen concedido en el tramo (remates o xG). Con penal atajado o atajadas decisivas, se anota y no prueba el bloque (Nice ante Brest, Muslera ante Estudiantes; el contraste es Palmeiras, que sostuvo con el rival en xG 0.24).
  - (d) **El caso viaja con la línea que lo sostuvo** (`linea`: la pareja o la línea). Si el once de hoy cambia la pareja central o la mitad de esa línea, la 6 se responde «no» o «sin dato», con la misma regla que el MECANISMO-ABIERTO (Gimnasia de Mendoza–Platense).
  - (e) **Manda el caso comparable más reciente.** Si la cadena trae casos de los dos signos, el último en sede y competición comparables decide la 6 (Arsenal: el caso de liga ante Forest no se transfirió a la Champions y volvió a perder una ventaja).
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
- **65-80'+:** decisiones según marcador, piernas frescas, balón parado como palanca, riesgos de fatiga.
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

> **Caso de referencia.** Manchester United en el MKM Stadium, F1 2026-27: gol al 17' por rechace de córner no atacado, gol al 38' por marca perdida al segundo palo en tiro libre. Veintiún minutos entre los dos, sin ajuste visible del marcaje. La misma línea de fondo repetía intérpretes para la fecha siguiente.

### M5 — Diagnóstico de Fase de Juego *(post — vive en el CIERRE)*

- ¿Funcionó el plan (M3) pronosticado? **¿Hasta qué minuto?** Sé honesto.
- Separa **juego abierto vs balón parado vs transición**: ¿de dónde salió el peligro real?
- **Cronología del giro:** cuándo y por qué cambió el partido.
- **Contraste con el pronóstico previo:** qué acertó, qué no, y qué lección entra a M6/M3 del siguiente.
- **Chequeo de MECANISMO-ABIERTO** *(v1.1)*: ¿hubo dos goles del mismo mecanismo? Si sí, declararlo acá, con su `regimen` *(v1.5)*. Un mecanismo `persiguiendo` heredado que el partido no puso a prueba se anota como **no puesto a prueba**.
- **Chequeo de régimen** *(v1.5)*: ¿en qué rama del estado de marcador se jugó el partido, y era la rama en la que se apoyaba el veredicto del M2?
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
