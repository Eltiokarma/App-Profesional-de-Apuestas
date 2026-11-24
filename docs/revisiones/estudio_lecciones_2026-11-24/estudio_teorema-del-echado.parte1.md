# TDE v0.1.27: lecciones pendientes, parte 1 (partidos del 17 al 21/11/2026)

Hay 237 lecciones de 64 partidos, todas ciegas PRE y acreditables. 28 son de copa nacional (23 de la Copa del Rey y 5 de la Copa de la División Profesional, todas del 18/11): cuentan para la rúbrica pero no para las métricas.
La clasificación por lección, en el mismo orden que la entrada, está en `clasif_teorema-del-echado.parte1.json`. Clasifiqué por la prosa, no por el veredicto ni por `modoFallo`.

## Conteo

| clase | total | sin copa | copa |
|---|---:|---:|---:|
| regla_sostuvo | 175 (74 %) | 155 | 20 |
| mal_aplicada | 24 | 23 | 1 |
| regla_fallo | 24 | 20 | 4 |
| no_dice (no testeado) | 7 | 6 | 1 |
| insumo | 4 | 2 | 2 |
| imprevisto | 2 | 2 | 0 |
| otro_skill | 1 | 1 | 0 |

Por veredicto del lado: acierto 103, parcial 50 y fallo 84. De las 84 de lados con fallo, 61 son `regla_sostuvo`: el veredicto del lado no mide la regla.
- Acierto: 82 sostuvo · 11 fallo · 8 mal aplicada · 1 no dice · 1 insumo.
- Parcial: 32 sostuvo · 6 fallo · 5 mal aplicada · 5 no dice · 1 insumo · 1 otro skill.
- Fallo: 61 sostuvo · 11 mal aplicada · 7 fallo · 2 insumo · 2 imprevisto · 1 no dice.

## Por regla (familias más frecuentes)

| regla | n | partidos | sostuvo | mal aplicada | fallo | otras |
|---|---:|---:|---:|---:|---:|---|
| disc 44 (b/f/a), tipología de rama | 47 | 41 | 34 | 6 | 7 | – |
| disc 66 (banco, referencias, vía del empate) | 43 | 34 | 31 | 4 | 7 | 1 insumo |
| disc 61 (salidas, otra_via) | 40 | 34 | 40 | – | – | – |
| disc 65 (desenlace, hecho, candidato) | 24 | 23 | 19 | 3 | 1 | 1 insumo |
| disc 63 (pieza del seguro) | 23 | 23 | 18 | – | 3 | 1 insumo, 1 imprevisto |
| disc 16 (expulsiones y S1) | 17 | 9 | 14 | 2 | 1 | – |
| disc 18 (SOB1 = necesidad, v0.1.27) | 10 | 10 | 4 | 4 | 1 | 1 insumo |
| disc 50 (RELEVANCIA BAJA) | 5 | 5 | 2 | – | 3 | – |
| disc 23 (añadido, prórroga) | 4 | 4 | 3 | – | – | 1 no dice |
| disc 17 / 24 (no testeado) | 6 | 6 | – | – | – | 6 no dice |
| disc 10/47 (P1a a mano) | 2 | 2 | – | 2 | – | – |
| disc 6 (tipología por identidad) | 2 | 2 | – | 2 | – | – |
| PASO 4 (falsador) | 2 | 2 | – | 1 | 1 | – |

Dentro de la 66 las subreglas se comportan así:
- `bancoProbable` copiado: 10 de 10 se sostienen. Hay otras 8 lecciones de otras reglas que confirman que el banco nombrado fue la vía.
- `ventajaPorFuerza` y `ventajaPorMinuto`: 21 de 21.
- La vía del empate en la rama de ventaja: 7 `regla_fallo`.
- Titular nombrado como banco o lista incompleta: 4 `mal_aplicada`.

## Patrones con ≥ 3 partidos distintos

1. **La vía del empate de la rama de ventaja no nombró la vía real (disc 66, C6). `regla_fallo`, 7 lecciones en 6 partidos.**
   - Los casos: Wales–Portugal 1528992 (Gales y Portugal), Poland 1528998, Athletico-PR 1492453, Belgrano 1649571, Puebla 1551039 y Feyenoord 1552226. Vasco 1492458 suma uno dentro de una lección `sostuvo`.
   - En los seis, la nota nombraba «banco + pelota parada» y el empate llegó por titulares en juego abierto, por la pelota sucia, por la media distancia del 9 o por la contra que la base propia ya nombraba. En 4 de ellos el DTP del parte tenía el renglón.
   - Cuando la vía nombrada era la buena, se cumplió: Palmeiras 1492452, Always Ready 1650230, Juárez 1551040 y Guaraní 1632066.
   - **Aclarar en el skill:** la nota de `siMarcaPrimero` copia las vías del rival del DTP por renglón, con la vía principal en juego abierto y no solo el banco. Con esto se cierra el C6 de la v0.1.27, «la vía también son los titulares», que pedía un tercer caso. Ahora tiene seis.
   - **Para la app, opcional:** que el recibo avise si la rama de ventaja no nombra el renglón 1 del DTP rival.

2. **SOB1 dice la necesidad, no el régimen: regla nueva de la v0.1.27 (disc 18). Se cumplió en 4 lecciones y se incumplió en 4.**
   - Sin el condicional escrito (`mal_aplicada`): Athletico-PR 1492453, São Paulo 1492457, Cerro 1650503 y Wanderers 1650504. En los cuatro, el obligado no se expuso: no tuvo la pelota o salió con línea de cinco.
   - Escrita y cumplida: Grêmio 1492454, Central Español 1650505 y Cagliari 1550200. Se suma Polonia 1528998, condicionada al resultado simultáneo.
   - Once tardío con DT de debut: Crystal Palace 1557471 (`insumo`).
   - Pide extender el condicional a ramas con `sob1` 0,5: Everton de Viña 1505565 (`regla_fallo`).
   - **Juicio:** es la primera semana de la regla y está escrita. No hace falta repetirla.
   - **Para la app:** un campo `seExponeSi` en la base SOB y en la rama del obligado, y que el recibo avise si falta con `SOB1` = 1. Es el mismo arreglo que funcionó con el banco.
   - **Candidato a medir (C1):** suma 5 obligados de tabla que no se expusieron (los 4 de arriba y Tijuana 1551038). El peso no se toca sin backtest.

3. **El banco de la hoja (disc 66): bajó mucho, pero queda una cola en el rehacer. `mal_aplicada`, 4 lecciones en 4 partidos.**
   - Titular nombrado como banco: Remo–Chapecoense 1492456, IdV–Macará 1639806 (rehecho con la hoja, pero las ramas que nombran el banco **rival** no se reescribieron) y Juárez–Atlas 1551040 (ya rehecha, con dos titulares en la lista y sin Montiel, que marcó el 2-3).
   - Lista incompleta: Nice–PSG 1552824 (faltó A. Abdi, autor del 2-3).
   - `bancoProbable` vacío en copa (`insumo`): Reddis–Barakaldo 1644373, en dos lecciones.
   - **Para la app:** al rehacer, reescribir también la línea de banco del rival en las ramas, o que el recibo frene un nombre de la línea de banco que está en el once oficial. El texto ya lo dice; repetirlo no cambia nada.

4. **El favorito se apartó del defecto «sigue atacando» y falló (44 (b)). `regla_fallo`, 4 partidos.**
   - Los casos:
     - Tenerife 1644346 (copa): `F2` = 1 y rotación.
     - Sabadell 1644384 (copa): `F2` = 1 y el Granada a 3 días.
     - Arsenal 1557475: antecedente de cinco coincidencias, margen 0,80.
     - Cartagena 1644353 (copa): antecedente sostenido por el arquero.
   - A eso se suma Palmeiras 1492452, `mal_aplicada` porque el antecedente tenía la pieza ausente.
   - Con motivo, sostuvieron Ucrania 1528994, Boston River 1650500 y Alavés 1570453.
   - Tres de los cinco son de copa contra un rival muy inferior.
   - **Candidato a medir, sin número:** la tasa de «administra» cumplido por motivo (`F2`, antecedente, plan del DT) en el favorito con margen ≥ 0,30. No hay material para cambiar texto: la 44 (b) ya dice que `F2` = 1 «no se aplica solo» (Freiburg–Union).

5. **RELEVANCIA BAJA: la premisa «sin protector se resuelve antes» falló (disc 50). `regla_fallo`, 3 partidos.**
   - Los casos: Cercle–Westerlo 1558682 (0-0 al 71'), Ameliano–Luqueño 1632063 (0-0 al 62') y Aston Villa–Sunderland 1557467 (0-0 al 90').
   - Sostuvieron São Paulo 1492457 y Portugalete 1644369 (copa).
   - La consecuencia (leer por ramas) se cumplió en los cinco. Lo que falló es la premisa.
   - **Candidato a medir:** cuánto llegan vivos al 75 los partidos sin protector frente al resto. Mientras tanto, aclarar que RELEVANCIA BAJA dice «lean las ramas», no «el partido se resuelve antes».

6. **Pieza del seguro relevada por una del mismo rol (disc 63). 5 partidos: 1 `regla_fallo` y 4 `sostuvo` con el mismo matiz.**
   - El seguro no se rompió al salir la pieza porque entró otra del mismo rol: Ameliano 1632063, Lazio 1550202, Como 1550200 (el heredero estaba escrito), Coventry 1557471 y Forest 1557468.
   - Donde salió sin reemplazo de rol, sí concedió: Chelsea 1557470, Coritiba 1492451 y Liverpool M. 1650504.
   - Se pidió nombrar la pieza con sus amarillas en Bragantino 1492459 y Liverpool M. 1650504.
   - **Aclarar en el skill:** la rama nombra quién hereda el seguro desde `bancoProbable` y la pieza con sus amarillas. El cierre lee «seguro roto» solo si el que entra no es del rol. Es texto, sin número.

7. **El hecho de la 65 estaba y no se usó (incumplimiento de texto escrito). 3 partidos.**
   - Los casos:
     - Austria 1528996: banco condicionado «antes del 75 con cambios».
     - Roma 1550205: lo mismo.
     - Parma 1550205: el hecho de `siRecibePrimero` no pasó a `siIguala`.
     - Barakaldo 1644373 (copa): `insumo`, quedó `abierto` porque `bancoProbable` venía vacío.
   - **Juicio:** el texto ya lo dice («se usa en todas las ramas donde aplica»).
   - **Para la app:** con `bancoProbable` y los cambios disponibles, la app puede sugerir el condicional («si recibe antes del 75 con cambios por hacer») en `porqueDesenlace`.

8. **S1 nombró candidatos y no la línea (disc 16, v0.1.26). 3 partidos.**
   - `mal_aplicada`: Melgar 1549554 (la vio Quagliata, volante titular) y Charleroi 1558683 (la vio el pivote Khalifi).
   - En Le Havre 1552827 el expulsado era un carrilero titular que S1 no nombraba y el DTP sí.
   - **Para la app:** que la lista «titulares que van al choque» (zaga, pivote, 9) con sus amarillas salga de `f1/{id}` y el skill la copie, como el banco.

9. **Candidato «doble golpe» (61): 4 casos más.** Norway 1528993, Badajoz 1644346 (copa), Cerro Largo 1650501 (a 4') y Nice 1552824. Sigue siendo candidato a medir, sin denominador.

10. **Candidato de la 65, defecto por quien persigue: 8 casos, todos en su dirección.**
    - El favorito que persigue rescata: Flamengo 1492453, Troyes 1552827 y Bayern 1575221.
    - El no favorito se rompe: Utebo 1644384 (copa), Lecce 1550202, Ipswich 1557476, La Louvière 1558684 y Deportivo 1570453.
    - **Candidato a medir:** con `μ_partido`, n ≥ 30 por lado, en la app.

## Quedaron con 1-2 casos (no entran)

- **Pieza del seguro ya fuera al abrirse la rama:** Badajoz 1644346 (copa) y Gales 1528992 (Rodon). Se leería «sin seguro».
- **Central reconvertido de la línea de tres como pieza del seguro:** Rumania 1528999.
- **Pieza de la VÍA en la rama que persigue (Kane y Olise lesionados):** Bayern 1575221, `imprevisto` con candidato.
- **P1a bajado a mano por «necesita ganar» (disc 10/47):** Grêmio 1492454 y Torque 1650502.
- **ECHADA-SUP por identidad o «sin nada en juego» (disc 6):** Progreso 1650502 y Atlante 1551038.
- **Rama y DTP del mismo equipo sin decir cuál manda (44 (b), v0.1.26):** América 1650173 y Cerro 1650503.
- **Falsador:**
  - Atado al marcador, `mal_aplicada`: Racing 1650505.
  - Escrito sobre remates de afuera, que son la firma de la echada ordenada: Köln 1575221, `regla_fallo`.
- **Tipología del obligado:**
  - Escrito «en su plan» cuando el defecto era «sigue atacando»: Vitória 1492459, `mal_aplicada`.
  - En la dirección contraria: Wanderers 1650504 (línea de cinco, «en su plan» describió).
  - «Le basta ganar por uno» administra en parte: Tijuana 1551038.
  - «En su plan» que administró: Betis 1570462.
- **ISE agravado con roja propia perdiendo:** Kosovo 1528997 concedió por otra vía (contraejemplo parcial) y Le Havre 1552827 lo cumplió. La contradicción sigue abierta.
- **Régimen condicionado a los cambios que queden:** Central Español 1650505.
- **siIguala en copa sin el 90-120:** Alcoyano 1644334 (copa; la regla de la 16 ya lo pide).
- **Bloque de cinco de plan leído como improvisado por el checklist del DTP (C1 heredado):** Köln 1575221, `otro_skill`.
- **C5, suplente que entra y ve la roja:** Bucaramanga 1650173. Con Serbia y Juventud del 17/11 ya son 3, pero sigue siendo un casillero nuevo: primero el insumo.
- **C2, superioridad ganando:** Irlanda 1528997 y Troyes 1552827 cargaron.
  - Perdiendo o empatado cargaron los cuatro: Gales 1528992, Alianza Atl. 1549554, Badajoz 1644346 y Cartagena 1644353.
  - La superioridad no administró en 6 de 6.
- **C3, roja propia ganando:** concedió Melgar 1549554 (roja al 10' con 1-0, empate al 90). Tenerife 1644346 concedió uno con 3-1. Portugal 1528992 no concedió.

## Comparación con el 17/11

| patrón del 17/11 | esta semana |
|---|---|
| Banco desde la hoja (16 mal aplicadas + 6 insumo) | **Bajó mucho:** 4 mal aplicadas y 2 insumo, frente a 18 lecciones que lo citan cumplido. La cola es el rehacer del banco **rival** |
| `siExpulsion` incompleta (4) | **Desapareció:** ninguna lección pide líneas que faltan. La plantilla v0.1.27 se ve cumplida (Portugal, Irlanda, Cartagena, Troyes) |
| SOB1 = 1 sin régimen (5, `regla_fallo`) | **Se repite, ahora como `mal_aplicada`** (4) de una regla nueva, más 4 cumplidas. Suma a C1 |
| Tipología apoyada en antecedente o identidad (4) | **Se repite** (Palmeiras, Cartagena, Arsenal, Progreso, Atlante): 2 mal aplicadas y 3 fallos de regla con el motivo |
| Pieza del seguro (12 de 15) | Se sostiene (18 de 23) y suma el matiz del relevo del mismo rol |
| Superioridad por marcador (C2) | Sin contraejemplo esta semana: 6 de 6 cargan |
| Roja propia ganando (C3) | +1 que concede, +1 que sostiene |
| Huecos de S1 (C5) | +1 suplente. Además, 2 S1 que no nombraron la línea (regla escrita) |
| 61, 65 `abierto`, referencia de la 66 | **Se sostienen:** 40 de 40, 11 de 11 y 21 de 21 |
| Vía del empate por titulares (C6, 2 casos) | **Llega a 6 partidos** y pasa a patrón |

**Arreglos de la app:**
- **`bancoProbable` funcionó.** El error pasó de 22 a 6. La falla que queda es del rehacer: la línea de banco del rival en las ramas no se reescribe con el once.
- **`ventajaPorFuerza` se cita y se cumple en todas las lecciones que la nombran (unas 20).** Igual que EFE-EMPATE-TECNICO, una referencia de dos columnas no se refuta con casos: la prueba es la medición en la app.
- **Rehacer con la hoja.** Siguen 3 once tardíos en el TDE: Recoleta–Guaraní 1632066 (grid corregido), Palace 1557471 y Liverpool–Wanderers 1650504. En el 17/11 fueron 6. Desde el TDE no se puede juzgar el recómputo del EFE.
- **Jev `lectura`:** etiquetó 14 lecciones, todas de orden 1. De esas, 5 son `regla_sostuvo`: sigue siendo poco fiable para el TDE.
- **Fix del homónimo (21/11 22:50):** ninguna lección de esta parte lo menciona. No se puede juzgar.

## Rarezas del dato

- **Las 23 lecciones del 17/11 ya están escritas con la v0.1.27:** citan `bancoProbable`, `ventajaPorFuerza` y la plantilla de `siExpulsion`. Ninguna cita una regla que la v0.1.27 haya cambiado.
- **Cuarentena:** las 4 lecciones de Deportiva Minera–Cartagena 1644353 (copa) están marcadas «DT del parte distinto del que dirigió». Las clasifiqué igual: ninguna depende del DT.
- **Duplicados:** no hay lecciones duplicadas (237 textos distintos).
- **Atribución:** una lección es más del DTP que del TDE, la de Köln 1575221:b (el checklist del DTP leyó «improvisado» un bloque de plan).
