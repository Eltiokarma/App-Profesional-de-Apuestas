# Reventones de la Liga 1 — primera tanda (13/10/2026)

Nueve estudios hacia atrás (`/analisis/cowork/reventones`, modo `reventones` de
`corrida-sad`), Liga 1 Perú y sus equipos en copa e internacional, julio a
septiembre de 2026. Población `post_resultado`: lo que sigue FIJA RÚBRICA y abre
candidatos; no mueve ningún número.

| Partido | Equipo · tipo | Mecanismo (secundario) | Señales previas |
|---|---|---|---|
| Sport Boys 1-0 Garcilaso (13/09) | Garcilaso · racha + | penal | riesgo alto, cerca del extremo, DT interino |
| Cienciano 2-0 Universitario (02/08) | Universitario · racha + | superioridad del rival (balón parado) | altura, DT nuevo, 4 bajas · riesgo BAJO |
| Cienciano 2-3 ADT (10/07, Copa de la Liga) | Cienciano · racha + | sobreexposición del que ganaba | K-EXTREMO, eliminación directa · riesgo BAJO |
| Cusco 4-1 Alianza Atlético (18/07) | Alianza Atlético · racha + | altura (sobreexposición) | altura, cerca del extremo, racha hecha en copa · riesgo BAJO |
| Alianza Lima 2-1 Huancayo (19/07) | Huancayo · racha + | superioridad del rival | riesgo alto, racha hecha en copa y de local |
| Cienciano 1-1 Los Chankas (30/09) | Los Chankas · racha − | varianza (el rival no administró) | K-EXTREMO, DT recién vuelto · riesgo BAJO |
| Cienciano 4-0 Lanús (29/07, Sudamericana) | Cienciano · racha − | el rival se echó (fatiga y altura) | altura, K-EXTREMO, bajas del rival, viaje · riesgo BAJO |
| Alianza Lima 2-1 Huancayo (19/07) | Alianza Lima · racha − | racha de otra competición | cerca del extremo, racha de copa con alternativos y un amistoso · riesgo BAJO |
| ADT 1-3 Huancayo (30/08) | Huancayo · racha − | rotación del rival (se sobreexpuso) | riesgo alto, cerca del extremo, DT nuevo del rival, rival en descenso |

## Lo que se repitió

1. **El riesgo calculado no ve lo que más pesó.** En 6 de 9 daba BAJO y la
   burbuja reventó. Lo que no ve: la **altura** (3 casos en Cusco), la
   **composición de la racha** (4 casos armados en la Copa de la Liga, con
   alternativos o con un amistoso, que revientan al volver la liga) y el
   **formato** (eliminación directa, ida y vuelta). No se mueven puntos: la
   composición pasa a ser SEÑAL CALCULADA (`racha_en_otra_competicion`,
   `condicion_a_contramano`) y la altura, mecanismo propio, para que el
   backtest pueda medirlas.
2. **El extremo sí avisó.** K-EXTREMO o K-CERCA-EXTREMO estaban encendidos en
   7 de 9: la regla de prudencia (§10) se confirma, también con riesgo bajo.
3. **TDE.** La reasignación por primer gol (disciplina 44) se confirma en casi
   todos; la administración del que gana cancela la sobreexposición del rival
   (14/42) suma casos; RELEVANCIA BAJA (50) va 2 a favor y 1 en contra.
   Candidatos: F2 en altura para el local que juega en su altura; un bloque
   bajo de PLAN no es echada.
4. **EFE.** Faltan casilleros: altura, desinterés por un torneo menor,
   rotación de crisis después de una goleada (no es profundidad), cambio de
   arquero por decisión técnica.
5. **DTP.** El córner corto con el 9 libre y el gol de media distancia siguen
   sin vía propia en el M2; MECANISMO-ABIERTO por sistema (no por intérpretes).

## Datos de la base a corregir

- `/coachs` atrasado: Pellejero (Huancayo) desde marzo, la base dice julio;
  Orfila figuraba en el banco de Cusco cuando ya dirigía Rabanal.

## Segunda tanda (8 estudios más, 17 en total)

| Partido | Equipo · tipo | Mecanismo (secundario) | Señales previas |
|---|---|---|---|
| Cienciano 1-1 Los Chankas (30/09) | Cienciano · racha − | racha de otra competición (varianza) | rival inferior, riesgo muy alto, DT nuevo del rival |
| FC Cajamarca 2-5 Cienciano (04/09) | Cienciano · racha − | superioridad del rival (el rival se sobreexpuso) | riesgo alto, cerca del extremo, rival en descenso, rotación |
| Universitario 2-2 Comerciantes (05/09) | Universitario · racha + | balón parado (penal) | rival inferior · riesgo BAJO · la racha concedía 2 por partido |
| UTC 1-1 ADT (08/08) | ADT · racha − | otro → regresión al nivel (varianza: penal al 90+15) | riesgo muy alto, cerca del extremo, DT nuevos, rival necesitado |
| Cienciano 0-0 Garcilaso (16/08, clásico) | Garcilaso · racha + | penal fallado (superioridad del rival en el juego) | riesgo muy alto, cerca del extremo, DT interino, rival necesitado |
| Torque 3-0 Cienciano (17/09, Sudamericana) | Cienciano · racha + | superioridad del rival (altura) | rival superior, riesgo muy alto, cerca del extremo, bajas |
| ADT 2-1 Cienciano (23/09) | ADT · racha − | rotación/fatiga del rival (balón parado) | riesgo alto, cerca del extremo, DT nuevo, fatiga del rival |
| Grau 3-1 UTC (18/07) | UTC · racha + | racha de otra competición | cerca del extremo, DT nuevo, rival necesitado · riesgo BAJO |

### Lo nuevo de esta tanda

1. **6 de 8 llegaban con riesgo alto o muy alto** (en la primera tanda, 6 de 9
   llegaban con riesgo BAJO). Los dos de esta tanda con riesgo bajo
   (Universitario, UTC) tienen justo lo que el riesgo no mira: racha
   concediendo y racha de otra competición. Ojo: entre reventones estudiados
   no hay denominador; si el riesgo «acierta» lo dice el backtest, no esto.
2. **Dos burbujas enfrentadas** (3 casos: Chankas–Cienciano, UTC–ADT,
   Cienciano–Garcilaso): el empate corta las dos. Pasa a señal CALCULADA
   (`rival_tambien_en_burbuja`).
3. **La resaca de una eliminación continental** (Cienciano tras Torque: perdió
   con ADT y empató con Chankas en 13 días). Pasa a señal CALCULADA
   (`derrota_internacional_reciente`, 10 días); candidato EFE «OBJETIVO-PERDIDO».
4. **Racha de victorias que concede en todos los partidos** (Universitario):
   frágil aunque el rival sea inferior. Señal CALCULADA (`racha_concediendo`).
5. **Patrón de equipo**: Cienciano concede poco después de ponerse arriba o
   igualar (Copa de la Liga con ADT, Sudamericana, Chankas) — candidato DTP de
   MECANISMO-ABIERTO entre partidos, a confirmar con video.
6. **«Condición a contramano» es nominal en un clásico de estadio compartido**:
   ya no salta si el partido es en su propio estadio.
7. **Mecanismo nuevo `regresion_al_nivel`** (pedido por dos estudios): la racha
   corta se corta ante un rival de su nivel sin un hecho que lo explique.

## Tercera tanda (8 estudios más, 25 en total)

| Partido | Equipo · tipo | Mecanismo (secundario) | Señales previas |
|---|---|---|---|
| Sporting Cristal 1-1 Bentín Tacna (11/07, Copa) | Cristal · racha + | regresión al nivel (error del arquero) | riesgo alto, DT nuevo, rival necesitado |
| UCV Moquegua 0-0 Melgar (02/08) | Melgar · racha + | bloque bajo del rival (regresión al nivel) | rival inferior · la racha concedía |
| Sporting Cristal 2-0 Juan Pablo II (02/08) | Cristal · racha − | regresión al nivel (el rival se sobreexpuso) | riesgo alto, DT nuevo, fatiga · racha de otra competición, resaca internacional, de visita |
| Alianza Atlético 1-0 Cienciano (06/08) | Cienciano · racha + | rotación/fatiga (racha de otra competición) | cerca del extremo, rotación (6 cambios en el once) · riesgo BAJO |
| Alianza Lima 1-1 Sporting Cristal (09/05, clásico) | Alianza · racha + | varianza (el empate al 90+2) | K récord, DT nuevo del rival, Advíncula suspendido · riesgo BAJO |
| ADT 0-0 FC Cajamarca (10/10) | ADT · racha − | racha de otra competición (roja; lo sostuvo el arquero) | riesgo muy alto, cerca del extremo, DT nuevo, rival directo |
| Cusco 1-0 FC Cajamarca (22/04) | Cusco · racha − | regresión al nivel (penal) | K récord (un 0-8 y dos de Libertadores), riesgo muy alto, DT nuevos, resaca internacional |
| ADT 4-0 Los Chankas (27/04) | Chankas · racha + | cambio de DT del rival: estreno del interino (sobreexposición) | K récord (8 partidos, máx. previo 3), rival inferior, fatiga · riesgo BAJO |

### Lo nuevo de esta tanda

1. **El extremo vuelve a ser la única alarma con riesgo bajo.** Los tres
   reventones positivos con riesgo BAJO (Cienciano, Alianza, Chankas) tenían
   K-EXTREMO o K-CERCA encendido. En la suma de las tres tandas, el extremo
   está en casi todos los estudiados; sin el denominador no es probabilidad,
   pero la prudencia de §10 se sostiene.
2. **`regresion_al_nivel` es el mecanismo más frecuente de la tanda** (3 + 1
   secundario). Las rachas negativas de Cusco y Cristal se armaron con rivales
   de otra escala (Flamengo, Estudiantes, el líder con un 0-8) y se cortaron
   al volver a su nivel: la K récord era de la escala del rival, no del equipo.
   Candidato a backtest: rachas negativas armadas por una goleada aislada.
3. **El once que jugó no era el que armó la racha** (Cienciano en Sullana: 6
   cambios, con la Sudamericana a 7 días). Pasa a señal CALCULADA
   `once_distinto` (≥ 5 titulares distintos respecto del último partido de la
   racha), solo con los dos onces en la base: se ve ~60 min antes del pitazo.
4. **Mecanismos nuevos**: `bloque_bajo_del_rival` (Melgar ante UCV: un
   repliegue POR PLAN desde el arranque no es una echada) y `arquero_rival`
   (Medina, de Cajamarca, sostuvo el 0-0 ante ADT: el espejo de
   GK-FALLA-ACTIVA, que el bloque C no mira).
5. **Señales nuevas a declarar**: `clasico` (6 empates en los últimos 10
   Alianza–Cristal: la paridad del cruce no la ve la regla del nivel) y
   `rival_directo` (ADT–Cajamarca, 15.º contra 16.º).
6. **Bug arreglado**: `condicion_a_contramano` se apagaba con el equipo de
   LOCAL en su estadio (Cristal–JP2: la racha negativa era toda de visita).
   Ahora solo se apaga si figura de visita en su propio estadio.
7. **Estreno de DT interino del rival** (ADT con Ripacolli: cambio de planteo
   en el descanso y el banco decidió): segundo caso de efecto estreno
   inmediato, candidato a vigilar, no regla.
8. **La escala de la liga dentro del riesgo**: el nivel de Bentín (Copa,
   recién ascendido) venía de la base de Liga 2; el riesgo lo comparó como si
   fuera de la misma escala. Es el mismo problema que `ESCALA-LIGAS` en el
   parte, sin alerta en la burbuja: pendiente.
