# Estudio de lecciones pendientes · efe-clasificador v1.10

189 lecciones, partidos del 10 al 16/11/2026 (población ciega PRE). Veredicto del lado: 109 aciertos, 57 fallos, 23 parciales (no dice si la regla funcionó).
Clasificación por la prosa (`clasif_efe-clasificador.json`): **123 regla_sostuvo · 35 mal_aplicada · 14 regla_fallo · 9 insumo · 7 no_dice · 1 otro_skill**.
Entran unas 20 lecciones de copa nacional (Copa del Rey, Copa Uruguay, Copa Bolivia, Copa Colombia). Sirven para la rúbrica, no para las métricas.
Ojo: «declarada y cumplida» es la frase de cierre de casi todas las lecciones. Para EFE-EMPATE-TECNICO y F3 cuesta escribir un caso que la contradiga (ver más abajo).

## Tabla por regla (las más frecuentes)

| regla / alerta | n | partidos | sostuvo | fallo | mal_aplicada | insumo | no_dice | otro |
|---|---|---|---|---|---|---|---|---|
| F3 | 30 | 29 | 22 | 4 | 3 | – | – | 1 |
| EFE-EMPATE-TECNICO (incluye «no se compara entre bases») | 27 | 27 | 27 | – | – | – | – | – |
| Tabla F1 (ONCE-SIN-FILA-F1, candidatos al puesto) + rehacer de la prosa | 21 | 17 | 1 | – | 19 | 1 | – | – |
| Rama «once alternativo» | 14 | 11 | 10 | – | 4 | – | – | – |
| Jerarquía de fuentes de bajas | 14 | 13 | 10 | – | 4 | – | – | – |
| EJE-DEBUTANTE | 14 | 14 | 9 | – | 1 | – | 4 | – |
| COLAPSO EN CASCADA | 11 | 11 | 10 | – | – | – | 1 | – |
| B5 (banco por rol) | 10 | 10 | 5 | 3 | 2 | – | – | – |
| B6 / arquero (incluye GK-DOWNGRADE y la zona GK) | 10 | 10 | 5 | 4 | 1 | – | – | – |
| Once tardío (< 20') | 7 | 6 | – | – | – | 7 | – | – |
| D3 | 7 | 7 | 5 | 1 | 1 | – | – | – |

## Patrones que se repiten (≥ 3 partidos)

**1. La tabla F1 no se rehace con el once oficial: ONCE-SIN-FILA-F1 (19 lecciones, 15 partidos). Es incumplimiento, no regla.**
Casos: Escocia y Macedonia 1545659, Eslovenia 1545654, Kazajistán 1528968, Eslovaquia y Feroe 1528967, Grecia 1528966, Serbia 1528965, Montenegro 1545613, San Marino 1528964, Albania y Finlandia 1528963, Chequia 1528961, Inter Bogotá y América 1648690, Valencia 1644380, Alavés 1644336 y Atlético-MG 1492455 (roles del alternativo).
En varios de esos casos el titular sin fila decidió: Chesnokov hizo el gol, Prekop el 1-0, Davidsen el penal, Tortolero el 1-2 y M. Rodríguez el 1-3.
La v1.10 ya lo manda («los once titulares con fila, sin umbral»; «candidatos al puesto»).
- *Aclarar:* las lecciones citan un «corte de 3» de la alarma (1528967 «por encima del corte de 3»; 1528961 «con 3 o más»). La rúbrica dice «sin umbral» y otras lecciones dicen «aunque sean menos de 3» (1528968, 1528966). Hay que alinear el texto de la alarma de la app con la rúbrica.
- *Para la app, no para el skill:* que el recibo bloquee el depósito rehecho con titulares sin fila. Repetir la regla en el skill no cambió la conducta.
- Va junto con el rehacer que deja la prosa vieja: Montenegro 1528979 («faltan cinco») e Inter Bogotá 1549869 (B y F sin recomputar).

**2. El arquero suplente, nuevo o «sin rodaje» no fue la vía de gol (9 lecciones, 9 partidos).**
Casos: Chequia 1528985 (Kinský, 6 atajadas), Inglaterra 1528984 (Trafford), Turquía 1528982 (×1.5 de F2c), Jaguares 1549866, Dinamarca 1528974, Gales 1528972, Pasto 1549868 (GK-DOWNGRADE), Albania 1528963 y Celta 1644376 (FACTOR-X por un arquero que debutaba).
Ninguno concedió por error del arquero. Las cajas con los dos arqueros, que no movían la franja, se sostuvieron.
- *Aclarar:* B6 🔶 o la zona GK en rojo describen ausencia o continuidad, no una vía de gol del rival; el DTP no hereda «pelota sucia contra el arquero» sin un error documentado.
- *Candidato a medir:* bajar el peso del ×1.5 de F2c y de GK-DOWNGRADE cuando el suplente tiene titularidades. Es un número, no se aprueba sin medición.
- Hay un caso con la otra cara: Mijas 1644362, donde el 0-1 llegó en la salida del arquero alternativo.

**3. La rama «once alternativo» falta o es corta (6 lecciones, 6 partidos).**
- Sin rama pese a un hecho: Sport Boys 1549557 (sin nada en juego, 7 titulares fuera) y Bucaramanga 1549865 (clasificado en la última fecha).
- Sin los rotables de todas las líneas: Atlético Nacional 1549864 (James, Morelos y Sarmiento) y la F1 de América 1648690, Valencia 1644380 y Alavés 1644336.
- Rama escrita y descartada por un contraargumento: Always Ready 1649146.
- *Aclarar* que «clasificado sin nada en juego» es un hecho de la lista de la v1.10. Lo demás ya está escrito. Cuando la rama se escribió, acertó en 10 de 14 (Juventud, Eibar, Puerto Cabello, Monagas y otros).

**4. F3: contraejemplos de magnitud (4 regla_fallo y 2 mal_aplicada sobre 30).**
Casos: Hungría 1528973 y Bélgica 1528958 (la reducción contó bajas de rotación o a Courtois), Bielorrusia 1528964, Racing 1649057, Eslovenia 1545654 y Andorra 1545615.
La lectura vigente se sostiene: «F3 baja la confianza en la K, no ordena el partido». Lo hacen explícito Austria, Vasco, España, Monterrey y Liechtenstein.
- *Aclarar:* la reducción por zona se calcula con el rol en la competición del partido, no con el titular nominal.
- *Candidato:* leer F3 junto con H, porque contra un rival sin profundidad la F3 no se paga (Andorra, Eslovenia). Es un solo eje, con 2 casos claros: queda en observación.

**5. B5 en copa o con rotación: el banco nombrado no fue el banco (4 lecciones, 4 partidos).**
Casos: Boston River 1649058 y UD Logroñés 1644335 (copa con liga cerca), Real Potosí 1649149 (el gol vino de un suplente no nombrado) y Garcilaso 1549559 (el rehacer lo dio fuera de la hoja).
- *Aclarar:* en copa con liga a ≤ 5 días, B5 se escribe por rol y condicionado al once, igual que el porcentaje.
- *Candidato a medir:* Albion 1649060 tiene un B5 🔶 con dos casos de banco decisivo. Es un umbral.

**6. Jerarquía de fuentes por lenguaje y por fecha (4 mal_aplicada sobre 14).**
Casos: Always Ready 1649148 («se recupera de una lesión» se cargó como ❌), Bucaramanga 1549865 (parte de 7 días, el jugador fue titular), Islandia 1545617 (ciclo de amarillas dado por disponible) y Tolima 1549867 (convocado con sanción discutida).
La regla v1.7/v1.8 se sostuvo en las otras 10 (Estonia, Central Español, Türkiye, Valencia, San Marino…). *Aclarar* con ejemplos de redacción que van a Duda.

**7. Once tardío (< 20' del pitazo): 7 lecciones, 6 partidos, todas insumo.**
Casos: Pereira 1549872, Millonarios–Alianza Valledupar 1549871, Águilas 1549863, Irlanda del Norte 1528975, Chicó 1549870 y Progreso 1649056.
La regla «once tardío: F1 sin verificar» existe. No hay nada que cambiar en el skill; es un límite del insumo.

Casos sueltos (1-2), que no son patrón:
- DT suspendido sin mirar: Maldonado 1649059.
- D3 medido por racha en vez de por respuesta: UTC 1549556.
- E alto hecho contra rivales muy inferiores: Gibraltar 1545615.
- Medio sin creadores contra un bloque bajo: Suiza 1545654.
- Una F1 hecha con un solo agregador: Tavernes 1644380.

## Las alertas: cuáles se cumplen y cuáles no

- **EFE-EMPATE-TECNICO: 27 de 27 «cumplidas».** Por la prosa, ganó el de menor porcentaje en unas 9 (Grau, Los Chankas, Cerro, Central Español, Monagas, Francia–Italia, Países Bajos–Grecia, Bélgica–Italia, Dinamarca). Hubo empate en unas 11 (Cusco, Kazajistán–Eslovaquia, Defensor, Garcilaso, Tolima, Llaneros, Potosí, Cerro Largo, Once Caldas, Letonia, Armenia). El resto ganó el de mayor porcentaje o la prosa no lo dice.
  Como está escrita («la brecha no ordena»), la alerta no se puede refutar: si gana el de mayor porcentaje también «se cumple» (Millonarios, Moldavia, España). Su prueba real es la medición pendiente de la app: la tasa del de mayor porcentaje con y sin la alerta.
- **F3: 22 sostuvo, 4 fallo, 3 mal_aplicada y 1 otro_skill (Polonia 1528977: la confianza bajada no llegó al número del 1X2).** Se cumple como «baja la confianza». Como señal de volumen o de resultado tiene unos 6 contraejemplos.
- **EJE-DEBUTANTE: 14 lecciones, 9 materializadas (gol o grieta por la línea).** Casos: Bulgaria ×2, Comerciantes, Chipre, Polonia, Inglaterra, Liechtenstein, Macedonia (volumen, no la vía escrita) e Israel (vía sí, gol no).
  En 4 no se pagó (Peñarol, Croacia, Albania y Estonia; no_dice). En 1 la condición no se dio (Cerro). En 1 se escribió sobre la línea equivocada (Bulgaria 1528988: línea de 4 con un grid de 3).
  Aparte, 3 lecciones de EJE con once tardío o pareja equivocada están en «once tardío». La alerta funciona como amplía-rango; el fallo recurrente es el insumo (la pareja o la línea), no la regla.
- **COLAPSO EN CASCADA: 10 de 11 se cumplen en la forma v1.6/v1.9** (recibe primero, no recupera y no se rompe). Casos: Liechtenstein, Chequia, Querétaro, Jaguares, Gales, Chapecoense, Serbia, Pasto, Croacia y Santa Fe (no puesto a prueba).
  Una ruptura, San Marino 1528981 (2-7 con zaga de urgencia), suma un caso al candidato COLAPSO + AGRAVANTE (serían 4). La propia lección lo reserva: μ 2,31 contra 0,49 también lo explica. Sigue candidato.
- **T.54 (5) y FACTOR-X (3): todas sostuvo. G-BLOQUE: 2 sin poner a prueba (gol antes de la vida útil) y 1 sostuvo.**

## Contradicciones entre lecciones

- Umbral de ONCE-SIN-FILA-F1: «por encima del corte de 3» (1528967, 1528961) contra «aunque sean menos de 3» (1528968, 1528966). La rúbrica dice «sin umbral».
- F3 como volumen: Georgia 1528973 y Luxemburgo 1545614/1545617 (sin el núcleo no generó) contra Hungría, Bielorrusia, Monterrey y España (generó igual). Lo concilia la lectura vigente: F3 es confianza, no magnitud.
- Arquero: Mijas 1644362 (la rama del alternativo «no es cosmética») contra los 9 casos del patrón 2.
- D3 ❌ de visita en Grau 1549560: la nota del EFE («no recupera») leyó peor que la del TDE («pierde la ventaja»). Es 1 caso.

## Conclusión

Hay material para la v1.11 en aclaraciones, no en números:
1. La F1 con el once oficial: alinear el umbral con «sin umbral» y pedir a la app que bloquee el depósito.
2. B6 y la zona GK no son vía de gol por sí solas (9 casos).
3. La rama «once alternativo» la abre también un clasificado sin nada en juego, con los rotables de todas las líneas.
4. B5 en copa va condicionado al once.
5. Ejemplos de redacción para la jerarquía de fuentes.

Candidatos a medir, sin aprobar: el peso del ×1.5 de F2c y GK-DOWNGRADE con un suplente con titularidades, el umbral del B5 🔶 y COLAPSO + AGRAVANTE.
No hay material para tocar EFE-EMPATE-TECNICO ni COLAPSO: se sostienen, pero el primero no se puede refutar con lecciones y espera la medición de la app.
