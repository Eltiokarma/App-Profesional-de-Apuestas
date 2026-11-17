# Estudio de lecciones pendientes · sad-analysis v4.5

70 lecciones, partidos del 10 al 16/11/2026 (población ciega PRE). Veredicto del lado: 37 aciertos, 20 fallos, 13 parciales.
Clasificación por la prosa (`clasif_sad-analysis.json`): **35 regla_sostuvo · 20 regla_fallo · 14 mal_aplicada · 1 imprevisto**.
Entran 7 lecciones de copa nacional (Copa del Rey: Pamplona, Eibar, Anaitasuna, Alavés, Valencia, Logroñés; Copa Uruguay: Boston River–Torque). Sirven para la rúbrica, no para las métricas.
Un dato que se cruza con el veredicto: 6 de las 20 lecciones de un lado que falló dicen que la regla se sostuvo. Casi todas son alertas de prudencia que se cumplieron (K-CERCA-EXTREMO, FAMILIA-RECORD).

## Tabla por regla (las más frecuentes)

| regla / alerta | n | partidos | sostuvo | fallo | mal_aplicada | otra |
|---|---|---|---|---|---|---|
| K-EXTREMO (incluye la de condición; «sigue» con un hecho) | 9 | 9 | 7 | 2 | – | – |
| K-CERCA-EXTREMO (incluye la de condición) | 8 | 7 | 4 | – | 4 | – |
| Rama de goleada / marcador por rama | 7 | 7 | 3 | 4 | – | – |
| Falsador del 1X2 que nombra un gol suelto del débil | 6 | 6 | – | – | 6 | – |
| Riesgo alto o muy alto respetado en el 1X2 | 6 | 6 | 5 | – | 1 | – |
| Espina: el corte va a cero y no al otro signo | 5 | 5 | – | 5 | – | – |
| Falsador por nombres propios | 3 | 3 | 1 | 2 | – | – |
| DESCONFIAR · BURBUJA-DE-UN-PARTIDO | 3 | 3 | 3 | – | – | – |

Resto, 1-2 casos cada uno: tarjeta fuerte en una racha de un partido (2 fallo), DIV-MOTOR-MERCADO con amistosos (2 sostuvo), FAMILIA-RECORD (2 sostuvo), marcador acotado (2 sostuvo), y riesgo en las dos burbujas, ESCALA o mercado (1 cada uno).

## Patrones que se repiten (≥ 3 partidos)

**1. El falsador del 1X2 nombra un gol del débil que no tumba el pronóstico (6 de 6 mal_aplicada).** Es el patrón más claro.
Casos: Grau 1549560 (primer gol temprano del no favorito), Lituania 1528989, Finlandia 1528981, Chipre 1528979 (gol de penal), Noruega 1528972 (suplente que marca con 0-2) e Inglaterra 1528962 (cláusulas de marcador y de 1X2 mezcladas).
La v4.5 ya pide «cada cláusula dice qué refuta». En 5 de 6 el favorito pasaba el 80 %.
- *Aclarar* (no es un número): una cláusula «(1X2)» es un evento con su marcador que haga imposible el pronóstico: el empate, o el gol del rival con 0-0 o con un gol abajo. Un gol suelto del débil va como «(marcador)».

**2. La burbuja revienta a cero (empate) y no al otro signo que leía la espina (5 regla_fallo, 5 partidos).**
Casos: Defensor 1649062, Tolima 1549867, Racing 1649057, Chicó 1549870 y Eslovaquia 1528967 (riesgo medio).
También revientan a cero Letonia 1545616, Torque 1649057, Mirassol 1492455 y Atlético-MG 1492455, aunque esas lecciones tocan otra regla.
La regla (g) manda «al otro signo» con riesgo alto o muy alto porque la guía calibrada da 37 % y 45 % contra 27 % a cero. La propia v4.5 dejó escrito «⚠️ 3 de 6 a cero: se mide antes de afinar».
- *Candidato a medir, no regla:* la frecuencia del corte a cero frente al otro signo sale de la guía calibrada del reventón. Cambiarla es tocar la calibración, **solo con backtest** (`backtest_burbuja`, por signo del corte), en Python y TS y en los vectores dorados.
- *Mientras tanto se puede aclarar:* con la tarjeta débil y una racha de un partido, la espina nombra el empate como la salida del corte.

**3. K-CERCA-EXTREMO declarada y después apostada igual (4 mal_aplicada sobre 8).**
- Letonia 1545616: el 1X2 a favor de la racha.
- Portugal 1528974: «sigue» por la tarjeta fuerte, sin hecho.
- Chipre 1528959: un punto sobre el mercado.
- Atlético-MG 1492455: la espina sostenida en un once alternativo que no salió.
Las 4 que respetaron la alerta se sostuvieron: Santa Fe, Torque ×2 y Anaitasuna.
La regla de la v4.5 alcanza; es un problema de cumplimiento. *Aclarar* que con el once oficial el hecho que sostenía el «sigue» se revisa.

**4. Rama de goleada: el gatillo por minuto no separa (7 lecciones, resultado mixto).**
- La rama no llegó aunque el gatillo se dio: Petrolero 1649148 (gol al 5'), Croacia 1528985 (2', Kinský) e Inglaterra 1528962 (24').
- La rama llegó: Valencia 1644380, Eibar 1644365 y Finlandia 1528981. En Alavés 1644336 llegó sin el gatillo (primer gol al 28').
- Llegó contra rivales de 3 a 5 categorías abajo o contra San Marino, y no llegó entre selecciones parejas o contra un arquero en racha. La lectura de Santa Fe 1549869 apunta a la misma división.
- *Aclarar:* la rama se nombra con lo que la puede contener (el arquero rival, el rearme del rival).
- *Candidato a medir:* que con el favorito de 90 %+ o con distancia de categoría la rama sea el marcador. Choca con la regla v4.4 «el acotado manda»: se mide antes.

**5. K-EXTREMO «sigue con un hecho del partido»: 7 sostuvo, 2 fallo.**
- Sostuvo: Chequia 1528985, Türkiye 1528982, Macedonia 1545659, Serbia 1528965, Croacia 1528962, Noruega 1528972 y Garcilaso 1549559.
- Falló: Rumania 1528977 (con el hecho de las bajas propias del medio) y Central Español 1649058 (con el nivel del rival).
La regla (g) se sostiene. La propuesta de Rumania («un récord no se apuesta a favor aunque haya un hecho») contradice 7 casos y no se toma.

**6. Falsador por nombres propios (3 partidos, resultado mixto).**
Sport Boys 1549557 y América 1648690 fallaron (los nombres heredaron el once de referencia o había rotación). Medellín 1549863 funcionó (banco rival nombrado).
- *Aclarar:* el falsador nombra la vía o el rol además de los nombres.
- Kosovo 1528971 (la roja por mecanismo) va a favor de escribir el mecanismo.

**7. La tarjeta fuerte en una racha de un partido no pesa más que cómo se cortan (2 partidos).**
Casos: Cali 1549867 (de local se cortan empatando 30 de 41) y Suiza 1545654. Portugal (patrón 3) es parecido.
Son 2 o 3 casos: queda en observación.

Todo lo que toca el 1X2 o el número contra el mercado se cambia **solo con backtest**, nunca por lecciones:
- Luxemburgo 1545614: tres fuentes contra un mercado casi parejo.
- Always Ready 1649146: el empate en una ida con el once desconocido.
- Francia 1528960: siguió al mercado contra su propia lectura. La propia lección dice «un caso, no mueve la regla».
- Llaneros 1549870: contexto «sin nada en juego».
La dirección contraria también sale: Andorra 1545615 y Azerbaiyán 1528970 siguieron al mercado contra el motor con μ hecho de amistosos, y acertaron (2 sostuvo).

## Contradicciones entre lecciones

- Falsador por nombres: sirve en Medellín y no sirve en Sport Boys ni en América.
- K-EXTREMO con un hecho: Rumania pide no apostar nunca a favor del récord; 7 casos dicen que el hecho alcanza.
- Rama de goleada: el minuto «sí separa» (Valencia, Eibar, Finlandia) y «no separa» (Alavés, Petrolero, Inglaterra, Croacia).
- El signo del corte: la regla (g) y Eslovaquia («13 de 19 al otro signo») contra los 5 cortes a cero de la semana.

## Cruce con lo aprobado para la v4.6 (PENDIENTES.md)

- **DESCONFIAR · BURBUJA-DE-UN-PARTIDO: lo apoya, con muestra chica.**
  - La alerta acertó la desconfianza en sus 3 casos: Bosnia 1528978, Mirassol 1492455 y Puerto Cabello 1646937. En Puerto Cabello la restricción «Monagas no gana» también cayó.
  - En Francia 1528960, con DESCONFIAR sobre el elegido, el elegido perdió.
  - «Una racha de un partido no sostiene al elegido»: rachas + de un partido con riesgo alto o muy alto reventaron en Racing 1649057, Chicó 1549870, Boston River 1649432, Mirassol, Cali 1549867 y Eslovaquia 1528967 (riesgo medio). Siguió solo Dinamarca 1528974 (la burbuja de un partido ante un rival muy fuerte).
  - Mirassol pide además «la lectura útil fue la doble oportunidad», que es la opción elegido-o-empate que el método deja para cuando haya 100+ partidos. No adelanta esa decisión.
- **SOBRE-LA-CASA:** ninguna lección lo nombra. Chipre 1528959 eligió la racha un punto sobre la casa (bajo el umbral de 2) y se cortó. No hay material ni a favor ni en contra.
- **(h) Distancia a la casa ≤ 2 pts:** Torque 1649057 (50 contra 50,2) y Portugal 1528974 (59 contra 59,6) estaban pegados a la casa y el elegido no ganó. Luxemburgo pide apartarse. Son anécdotas que la observación (n 177) ya cubre mejor. No mueven nada y el skill no debe mencionar el semáforo.
- **(i) Marcador contra el elegido:** sin lecciones directas. Finlandia 1528981 (marcador contra el tramo más probable de su propia matriz) es la regla (h) de la v4.4 mal aplicada, en la misma dirección.

## Conclusión

Hay material para aclarar en la v4.6, sin números:
1. El falsador «(1X2)» es lo que hace imposible el pronóstico (6 de 6, el patrón más fuerte).
2. Cumplir K-CERCA-EXTREMO y rehacer la espina con el once oficial (4 casos).
3. La rama de goleada se nombra con lo que la contiene.
4. El falsador por vía o rol, no solo por nombres.

Candidatos a medir con backtest, sin aprobar: el signo del corte (cero o el otro signo), que es la guía calibrada del reventón; la rama de goleada como marcador con un favorito de 90 %+; y todo lo del 1X2 o el empate (Luxemburgo, Always Ready).
Lo aprobado de DESCONFIAR sale reforzado por 3 de 3 y por unas 6 rachas de un partido que reventaron. SOBRE-LA-CASA y (h)/(i) no reciben material nuevo.
