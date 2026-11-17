# Estudio de lecciones pendientes — teorema-del-echado (TDE) v0.1.26

Insumo: 276 lecciones `pendiente`, 81 fixtures, partidos del 10 al 16/11/2026, todas ciegas PRE y escritas con la v0.1.26.
Clasificación por lección: `clasif_teorema-del-echado.json` (misma carpeta). La clasificé leyendo la prosa; no usé `modoFallo`.
Aclaración: el veredicto del lado no mide la regla. De las 198 `regla_sostuvo`, 54 son de lados con veredicto `fallo`.

## Totales por clase

| clase | n |
|---|---|
| regla_sostuvo | 198 (72 %) |
| mal_aplicada | 31 |
| regla_fallo | 19 |
| no_dice (no testeado / rama sin tramo) | 15 |
| imprevisto | 7 |
| insumo (once tardío) | 6 |
| otro_skill | 0 |

## Tabla por regla (las más frecuentes)

| regla | n | sostuvo | mal_aplicada | fallo | insumo | imprevisto | no_dice |
|---|---|---|---|---|---|---|---|
| disc 61 (salidas y vía del gol en el cierre) | 50 | 47 | – | 3* | – | – | – |
| disc 44 (b) (sigue atacando / en su plan) | 46 | 39 | 3 | 2 | – | – | 2 |
| disc 66 (ventaja por minuto y línea del empate) | 33 | 30 | – | 2 | – | – | 1 |
| disc 65 (desenlace `abierto` por defecto) | 31 | 29 | 1 | – | – | 1 | – |
| disc 16 (expulsiones, propia y rival) | 27 | 14 | 5 | 5 | – | 1 | 2 |
| disc 66 (banco desde la hoja) | 22 | 0 | 16 | – | 6 | – | – |
| disc 63 (pieza del seguro) | 15 | 12 | – | 2 | – | – | 1 |
| S1 / ARQUERO-NUEVO | 8 | 1 | 1 | – | – | 5 | 1 |
| disc 44 (f) (siIguala / sostiene el punto) | 7 | 5 | 1 | 1 | – | – | – |
| otras (23, 50, 3/24, 43, 20, tipologías, ventana) | 37 | 21 | 4 | 4 | – | – | 8 |

\* Las 3 «fallo» de la 61 son en realidad del SOB1 de base (patrón 3), no de la regla de salidas.

**Lectura:** las reglas que la v0.1.25 y la v0.1.26 reescribieron se sostienen casi sin excepción. La 61 da 47 de 47 como regla. La 65 da 29 de 29 con `abierto` sin cobro: con `abierto` declarado, lo observado fue sobre todo `se_rompe` (unos 18-20), menos `rescata` (unos 5-9) y unos 4 «sin más goles». Es un conteo aproximado, hecho sobre la prosa. En la 66, la referencia completa («no pierde 9 de 10, no gana 1 de 4») se cita en 15 lecciones y en ninguna falla. La 44 (b) da 39 de 41 con amenaza leída. El problema dominante no es de regla: es de **ejecución del banco** (16 mal aplicadas y 6 de insumo).

## Patrones que se repiten (≥ 3 partidos distintos)

### Piden aclarar o hacer cumplir una regla (no mueven números)

1. **El banco sale de la hoja: incumplimiento sistemático de la 66 (v0.1.26).** Son 16 `mal_aplicada` en 16 partidos y 6 de once tardío.
   - **(a) Titular nombrado como banco con el once oficial ya capturado (10 partidos):** Lithuania–Liechtenstein 1528989, Estonia–Bulgaria 1528988, Faroe–Moldova 1528987, Kazakhstan–Slovakia 1528986 (Kenzhebek, «banco», asistió los dos goles), France–Türkiye 1528982, N. Ireland–Ukraine 1528975, Norway–Wales 1528972, Mirassol–Atlético-MG 1492455, Chapecoense–Vasco 1492312 y Albania–Finland 1528963.
   - **(b) Lista parcial o ausente en alguna rama (6 partidos):** JPII–Garcilaso 1549559, Croatia–Czech 1528985 (Majer, que no estaba en la rama, hizo el 2-1), Belarus–Albania 1528980 (1 nombre contra 12 suplentes), Nacional–Albion 1649060 (el lanzador del córner del 1-1 no estaba nombrado), Montenegro–Latvia 1545613 (faltaba en la rama de sostener) e Italy–France 1528960 (faltaba en siLeEmpatan).
   - **(c) Once tardío (6 partidos):** Wanderers 1649063, Millonarios 1549871, Llaneros 1549870, Cerro Largo 1649056, Tarancón 1644379 y Amorebieta 1644335. Piden marcar «probable» antes del once.
   - **Cambio:** que la app entregue la lista de suplentes de la hoja por rol, la misma para todas las ramas (ya está en PENDIENTES, «Banco probable: una sola lista en la app»). El skill la copia entera, en cada rama, y la marca «probable» sin once. Es regla ya escrita: lo que falta es la herramienta.
2. **`siExpulsion` incompleta, aunque la regla ya lo pide (4 partidos):**
   - England 1528984: no tenía la línea de «ganando», que fue la que se dio.
   - Montenegro–Latvia 1545613: sin la vía de gol propia del que necesita ganar con diez.
   - Pereira–América 1549872: sin ventana desde la roja.
   - Danubio–Liverpool 1649061: la ventana de la rama rival quedó en la nota.
   - **Cambio:** plantilla fija de `siExpulsion` con las tres cuentas del marcador, ventana en su campo y régimen hasta el final, también para `rival`. La v0.1.26 solo lo dice para `propia`.
3. **El SOB1 = 1 por la tabla no trae el régimen de exposición (5 partidos, `regla_fallo`).**
   - Los casos: Luxembourg 1545617 (0 remates en el área persiguiendo), Czech 1528985 (40 % de pelota y 8 remates con 0-1 desde el 2'), Belarus 1528980, Central Español 1649058 (salió 5-4-1) y Serbia 1528965 (20 % de pelota).
   - Se suman Boston River 1649058 y Croatia 1528962, donde el rival le quitó el régimen.
   - **Aclarar:** la base y la rama SOB del obligado se escriben condicionadas al sistema y al once («necesita el gol» no equivale a «se vuelca»). El cierre ya lo separa por la 61.
   - **Candidato a medir (numérico):** si el SOB1 de tabla debe pesar menos sin un hecho de hoy.
4. **La tipología se apoyó en la identidad o en un antecedente que no coincide (4 partidos, `mal_aplicada`).**
   - ECHADA-PSI por descenso y C3 en UTC 1549556.
   - Antecedente de visita para un partido de local en Faroe 1528987.
   - Antecedente de otra sede en Central Español 1649058.
   - Repliegue de plan leído como PSI en Slovenia 1545654.
   - Chico 1549870 y Andorra 1545615 confirman el contrario: el repliegue de plan no es echada.
   - **Cambio:** ninguno. Es la 44 (b) y la 65 de la v0.1.25. Como mucho, un recordatorio en la base, no solo en la rama.
5. **Pieza del seguro (63): se sostiene (12 de 15)** y suma el candidato de la rama de ventaja (ver los cruces). Hay dos aclaraciones de un caso cada una, que no forman patrón:
   - Con doble pivote se nombran las dos piezas (Chapecoense 1492312).
   - Con `sob2` = 1 heredado, el seguro está roto desde el gol aunque la pieza siga en cancha (Portugal 1528974).

### Piden mover o crear un NÚMERO o un casillero (todo candidato a medir, nada aprobado)

6. **Superioridad numérica con ventaja: ¿administra? (contradictorio).**
   - «No administra» se cumplió en 6: ADT 1549558, Spain–England 1528984, América 1549872, Cali 1549867, Czech–Spain 1528961 y América 1648690.
   - Falló en 3: Cerro 1649059 y Monterrey 1550951, que con 1-0 y uno más cambiaron delanteros por medios, e Israel 1528971, que hizo cambios ofensivos sin amenaza.
   - Germany 1528965 rotó con 3-1, pero ese tramo no se cobra.
   - Partido por el marcador: perdiendo o empatado con uno más, carga 4 de 4. Ganando, 2 cargan y 2 administran. Hay que **desdoblar `siExpulsion.rival` por marcador**, como se hizo con la propia en la v0.1.21. Con n = 4 del lado «ganando» se marca como candidato a medir.
7. **Roja propia ganando: tampoco es punto asegurado (3 a 1).**
   - Concedieron Cusco 1549558 (2-1 con diez, empate al 87'), Juventud 1649433 (3' después de la roja del 78') e Inter Bogotá 1648690 (roja al 11' con 1-0, dio vuelta).
   - Sostuvo Junior 1549868, contra un rival sin banco.
   - La referencia de la v0.1.25 (11 de 12) se midió **empatando**. Candidato: medir la tasa ganando y escribirla al lado.
8. **Ventana desde el cambio ofensivo (candidato de la v0.1.26):** ver los cruces.
9. **Huecos de S1 (5 imprevistos, ya declarados desde la v0.1.12):**
   - Suplente que entra y ve la roja: Pereira 1549872, Serbia 1528965 y Juventud 1649433. Son 3 y forman patrón.
   - Roja del DT: Pereira.
   - Conducta violenta sin pelota: Maldonado 1649059.
   - Roja al arquero titular: Querétaro 1550951.
   - Un casillero nuevo es número: candidato a medir. El patrón pide al menos declarar el hueco del suplente en la rama.

## Contradicciones sobre la misma regla

- **Disciplina 16, roja propia perdiendo (ISE agravado): empate 2 a 2.**
  - A favor: Liverpool 1649061 y Pereira 1549872. Salamanca 1644376 confirma, pero estaba roto y no acredita.
  - En contra: Comerciantes 1549557 y Finland 1528963. Querétaro 1550951 terminó sin más goles, pero porque el rival administró.
  - No hay material para tocar nada.
- **Disciplina 16, superioridad: ver el patrón 6.** Las lecciones se contradicen entre sí, y la contradicción se ordena por el marcador.
- **Vía del empate en la rama de ventaja (66).** Unas 9 lecciones confirman que el empate llegó por el banco nombrado: Kazakhstan, Defensor–Peñarol, Nacional–Albion, Real Potosí, Sweden, Norway, Cerro Largo, Tarancón y Austria. En 2 llegó por **titulares** del rival que dominaba: Wanderers 1649063 y Armenia–Cyprus 1528959. Más que contradecir, complementan la regla («la vía también son los titulares»). Con n = 2 no alcanza.
- **ARQUERO-NUEVO:** Juventud 1649433 (el suplente atajó tres penales) es un dato contra leer al suplente como agravante. Moldova 1528987 no decidió. Es un caso de cada lado: nada.

## Cruces con lo ya aprobado y con los candidatos

- **Aprobado para la v0.1.27 (`ventajaPorFuerza`, el desenlace de la ventaja lo pone la fuerza):** las lecciones lo **apoyan en lo cualitativo y no lo miden.**
  - 15 lecciones citan `ventajaPorMinuto` y se cumplen, todas en la columna «no gana».
  - La tipología no separa dentro de la muestra. Con ECHADA-VOL / «en su plan», sostuvieron Real Potosí 1649149, N. Ireland 1528975, Amorebieta 1644335, Juventud 1649433, Albania 1528980 y Medellín 1549863. Con la misma tipología perdió la ventaja Cyprus 1528959. Con «sigue atacando» perdieron Torque 1649057 (2-0 a 2-2) y France 1528960 (1-0 a 1-3).
  - Eso concuerda con la fila E del estudio (la tipología describe la vía, no el desenlace). Ninguna lección lo contradice.
  - La división por probabilidad previa no se puede hacer con la prosa: hace falta la app.
  - Además, las 39 de 41 de la 44 (b) «sigue atacando» cumplidas son casi todas de favoritos claros (margen de μ entre 0,66 y 1,82). Es el sesgo de selección que ya declaró la v0.1.25.
- **Candidatos de la v0.1.26, línea 22:**
  - **Ventana desde el cambio ofensivo: lo apoyan 4 explícitos y unos 5 implícitos.**
    - Explícitos: Cali 1549867 (el empate llegó 1' después del doble cambio del descanso, 24' fuera del +15), Cúcuta–Jaguares 1549866 (13' después del triple cambio), Lithuania 1528989 (3' después del doble cambio rival) y England 1528962 (5 llegadas croatas después de los cambios ingleses del 77', sin gol).
    - Implícitos, gol a 2-8' de un cambio: Georgia 1528973, Cerro Largo 1649056, Millonarios 1549871, Norway 1528972 y Mijas 1644362.
    - **Sesgo:** solo se anotan los cambios seguidos de gol; no hay denominador. Sigue en «medir primero», con más motivo.
  - **Pieza del seguro en la rama de ventaja: apoyo con 3 partidos firmes.**
    - Danubio 1649061: ventaja y uno más; sale la pieza al 68' y concede dos en 82'-84'.
    - Cali 1549867: superioridad sin seguro nombrado; concede a los 4'.
    - Italy 1528983: siLeEmpatan con `sob2` = 1, «pesa aunque no persiga».
    - Lithuania 1528989 suma un cuarto caso, sin fuente.
    - Es el candidato mejor respaldado para pasar a regla de texto: nombrar, no puntuar.
  - **SOB de la hora con 0-0 y el empate útil: 1 caso** (Maldonado 1649059, que concedió por la vía escrita al 68', 7' antes de la ventana). No alcanza.
  - **Lista de la 44 (f) en siLeEmpatan: 1 caso** (Tarancón 1644379, «el empate de copa le sirve, vuelve al bloque» y se vino arriba en la prórroga). No alcanza, aunque apunta en la dirección del candidato.
- **Candidato de la v0.1.25 (defecto por quien persigue):** hay un caso explícito, Anaitasuna 1644336. Muchas ramas `abierto` terminaron en `se_rompe` del lado débil, pero la prosa no trae el `μ_partido` de cada tramo. La medición sigue siendo la que fija la 65 (n ≥ 30 por lado, con `μ_partido`).
- **App (ya en PENDIENTES):** `viaGol` (Scotland 1545659 y Sweden 1528978, donde la app cobra como concedió un gol de pelota parada) y la lista única del banco (patrón 1).

## Conclusión

- **Tiene material para la v0.1.27, como texto:**
  - El desdoble de `siExpulsion.rival` por marcador (patrón 6), sin número.
  - La pieza del seguro también en la rama de ventaja y de superioridad (3 casos, cierra un candidato).
  - La plantilla completa de `siExpulsion` (patrón 2).
  - La SOB del obligado condicional al once y al sistema (patrón 3, 5 partidos).
  - Y sobre todo, para la app, la lista del banco desde la hoja (22 lecciones). Es la falla más repetida y no es de regla.
- **No tiene material:** mover el peso del SOB1, la ventana desde el cambio (sin denominador), la SOB de la hora con 0-0, la lista de la 44 (f) en siLeEmpatan, el ISE agravado con roja perdiendo (2 a 2) ni el defecto por quien persigue. La tasa de la roja propia ganando es candidata a medir (3 a 1).
- **Lo aprobado (`ventajaPorFuerza`)** no encuentra contraejemplos, pero estas lecciones no lo prueban.
- **Las disciplinas 61, 65 y 66 (referencia) y la 44 (b)** se confirman y no piden cambios.
