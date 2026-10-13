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
| Cienciano 4-0 Lanús (29/07, Sudamericana) | Cienciano · racha − | el rival se echó (fatiga y altura) | altura, K-EXTREMO, bajas del rival, viaje |
| Alianza Lima 2-1 Huancayo (19/07) | Alianza Lima · racha − | racha de otra competición | cerca del extremo, racha de copa con alternativos y un amistoso |
| ADT 1-3 Huancayo (30/08) | Huancayo · racha − | rotación del rival (se sobreexpuso) | riesgo alto, cerca del extremo, DT nuevo del rival, rival en descenso |

## Lo que se repitió

1. **El riesgo calculado no ve lo que más pesó.** En 5 de 9 daba BAJO y la
   burbuja reventó. Lo que no ve: la **altura** (3 casos en Cusco), la
   **composición de la racha** (5 casos armados en la Copa de la Liga, con
   alternativos o con un amistoso, que revientan al volver la liga) y el
   **formato** (eliminación directa, ida y vuelta). No se mueven puntos: la
   composición pasa a ser SEÑAL CALCULADA (`racha_en_otra_competicion`,
   `condicion_a_contramano`) y la altura, mecanismo propio, para que el
   backtest pueda medirlas.
2. **El extremo sí avisó.** K-EXTREMO o K-CERCA-EXTREMO estaban encendidos en
   8 de 9: la regla de prudencia (§10) se confirma, también con riesgo bajo.
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
