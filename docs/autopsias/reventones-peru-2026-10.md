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
