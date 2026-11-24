# TDE v0.1.27 — lecciones pendientes, parte 2 (partidos del 21 al 23/11/2026)

Insumo: `teorema-del-echado.parte2.jsonl`, con 231 lecciones de 71 partidos: 54 lecciones del 21/11, 169 del 22/11 y 8 del 23/11. Todas son ciegas `PRE` y acreditan. **Copa nacional:** 29 lecciones de 10 partidos (Taça de Portugal), que cuentan para la rúbrica y no para las métricas.
Las clasifiqué leyendo la prosa entera, sin mirar el veredicto ni `modoFallo`. Clasificación por lección: `clasif_teorema-del-echado.parte2.json`. Las reglas van normalizadas como «disciplina N · subtema».

## Conteo

| clase | total | sin copa |
|---|---:|---:|
| regla_sostuvo | 174 (75 %) | 152 |
| mal_aplicada | 33 | 27 |
| no_dice (no testeado, rama sin tramo) | 13 | 13 |
| regla_fallo | 8 | 8 |
| imprevisto | 2 | 2 |
| insumo | 1 | 0 |
| otro_skill | 0 | 0 |

**Cruce con el veredicto del lado:**

| veredicto | lecciones | sostuvo | mal_aplicada | regla_fallo | no_dice | insumo | imprevisto |
|---|---:|---:|---:|---:|---:|---:|---:|
| acierto | 139 | 108 | 18 | 2 | 9 | – | 2 |
| fallo | 81 | 57 | 15 | 5 | 3 | 1 | – |
| parcial | 11 | 9 | – | 1 | 1 | – | – |

El veredicto no mide la regla. 57 de las `regla_sostuvo` son de lados que fallaron, y 18 de las `mal_aplicada`, de lados que acertaron.

## Por regla (agrupada)

| regla | n | partidos | copa | sostuvo | mal_apl. | fallo | otras |
|---|---:|---:|---:|---:|---:|---:|---|
| 44 (b) (tipología de la rama de ventaja, antecedente) | 38 | 38 | 4 | 28 | 8 | 2 | – |
| 61 (salidas, otra vía) | 38 | 33 | 6 | 37 | – | – | 1 no_dice |
| 16 (expulsión: superioridad, roja propia, plantilla) | 29 | 16 | 2 | 25 | 1 | 2 | 1 no_dice |
| 66 (ventaja, ventajaPorFuerza, banco, vía del empate) | 29 | 26 | 5 | 23 | 4 | 1 | 1 insumo |
| 63 (pieza del seguro) | 23 | 21 | 1 | 15 | 3 | – | 5 no_dice |
| 65 (desenlace, el hecho, candidato) | 22 | 21 | 6 | 16 | 6 | – | – |
| 18 · SOB1 (necesidad, no régimen) | 10 | 10 | 0 | 3 | 6 | – | 1 no_dice |
| 44 (f) (siIguala) | 9 | 9 | 1 | 7 | 1 | 1 | – |
| S1 (rojas) | 8 | 8 | 0 | 2 | 4 | – | 2 imprevisto |
| 17 (no testeado) | 4 | 4 | 0 | – | – | – | 4 no_dice |
| candidato doble golpe | 4 | 4 | 1 | 4 | – | – | – |
| 23, 3, 24, 43, 45, 44 (a), ventana, bloque F | 15 | 15 | 2 | 12 | – | 2 | 1 no_dice |

**Subtemas que conviene separar:**
- **66:**
  - ventaja y ventajaPorFuerza: 19, con 18 sostuvo y 1 mal aplicada;
  - banco: 9, con 5 sostuvo, 3 mal aplicadas y 1 insumo;
  - vía del empate por titulares: 1 fallo.
- **44 (b):**
  - defecto o «en su plan»: 31, con 26 sostuvo, 3 mal aplicadas y 2 fallo;
  - antecedente o C3: 7, con 5 mal aplicadas.
- **65:**
  - el hecho: 9, con 6 mal aplicadas;
  - `abierto` por defecto: 6 de 6;
  - candidato «defecto por quien persigue»: 7.
- **16:**
  - superioridad: 11 de 11;
  - roja propia ganando: 3;
  - roja propia perdiendo: 1 a 1;
  - plantilla: 1 mal aplicada.

**Lectura:**
- Las reglas reescritas hasta la v0.1.27 se sostienen. La 61 da 37 de 37 y la 66 de ventaja, con `ventajaPorFuerza`, da 18 de 19; el que falla citó la referencia del otro lado. La 65 da 6 de 6 con `abierto` y la superioridad «no administra», 11 de 11.
- El problema dominante sigue siendo de **cumplimiento**. Ya no es el banco. Ahora pesan cuatro reglas que ya están escritas: el SOB1 condicionado (18, nueva), la tipología de ventaja sin motivo o por C3 (44 (b)), `S1` sobre la línea y el hecho del desenlace (65).

## Patrones con ≥ 3 partidos distintos

### A. La 18 v0.1.27 no se cumple: la rama SOB del obligado no se condiciona al sistema ni a la pelota (6 `mal_aplicada`, 6 partidos, ninguno de copa)

| equipo | fixtureId | qué pasó |
|---|---|---|
| Paderborn | 1575222 | «persigue en 3-4-3» desde un 5-4-1 |
| América | 1551044 | falsador cumplido: sin segundo 9, cambió línea por línea |
| ADO | 1552225 | tipología SOB con `sob1` 0,5 y el 21 % de la pelota |
| OH Leuven | 1558680 | línea de cinco con el 31 % de la pelota |
| OFI | 1593363 | condicionó al minuto, no al hecho |
| Bulo Bulo | 1645547 | 5-4-1 del grid oficial con la nota «laterales arriba» |

- **Los que la cumplieron (3):** Eyüpspor 1584474 (la reserva escrita fue lo que pasó), Gladbach 1575226 (nota con gatillo) y Blooming 1645546.
- **Lo que confirma la regla:** en 8 de 9 casos la necesidad no produjo exposición con línea de cinco o con el rival dueño de la pelota.
- **Qué hacer: para la app.** La regla está escrita y tiene una semana. Repetirla no cambia la conducta. Propuesta:
  - un aviso en el recibo, `SOB-SIN-GATILLO`, cuando la rama SOB del obligado no tiene condición y el grid trae línea de cinco o el DTP prevé que cede la pelota;
  - o un campo `gatillo` estructurado en esa rama.
- **El peso del SOB1 (C1)** sigue siendo candidato a medir y no se toca.

### B. Tipología de la rama de ventaja sin motivo nombrable, o elegida por C3 o por un antecedente que no coincide (44 (b), 8 `mal_aplicada`, 8 partidos, 2 de copa)

**Sin motivo («administra» o ECHADA-VOL en un no favorito, o el defecto ignorado):**
- Trinidense 1632065;
- Libertad 1632067 (favorito, margen 0,52);
- Atlético CP 1647580 (copa);
- Sanjoanense 1647588 (copa), anotado en una lección de la 66.

**C3 («perdió ventajas») como motivo de ECHADA-PSI o VOL:**
- Nacional Potosí 1645542, que el analista marca «otra vez»;
- Mushuc Runa 1639837;
- La Guaira 1646938 (C3 y F2).

**Antecedente:**
- Levadiakos 1593361: «mismas piezas» con una pieza distinta, como ya decía el DTP rehecho.
- Marseille 1552822, al revés: el antecedente sí coincidía en condición y marcador, quedó el defecto «sigue atacando» y el equipo se echó.

**Qué hacer.** Se repite y sube respecto del 17/11, cuando hubo 4. La regla (44 (b) v0.1.26 y 65) ya dice que C3 topa el bloque y no elige la tipología.
- **Aclarar en el skill**, una línea en la 44 (b) y no en la rama: «C3 = 1 no es motivo de tipología».
- **Para la app:** un `motivoTipologia` de lista cerrada en `siMarcaPrimero`, con aviso si va vacío o dice solo C3.

### C. `S1` nombra candidatos y no la línea del choque (4 `mal_aplicada`, 4 partidos; la regla es de la v0.1.26)

| equipo | fixtureId | quién vio la roja |
|---|---|---|
| Real Tomayapo | 1645542 | Barbieri (el DTP sí lo tenía) |
| Manchester United | 1557473 | Yoro, el otro central |
| Atlético Nacional | 1650176 | Marín, del doble pivote |
| Instituto | 1649568 | el carrilero en capilla según la F1 |

- **Se cumplió** en ADO 1552225 y Osasuna 1570458.
- **Qué hacer: para la app** (ya aprobado en la v0.1.25: «insumos de `S1` en `GET …/tde/{id}`»). Que la app devuelva la línea del choque del once, con amarillas y regreso de roja, y la nota la copie. Volver a escribirlo en el texto no alcanzó.

### D. El hecho del desenlace (65): mal usado en los dos sentidos (6 `mal_aplicada`, 6 partidos, 3 de copa)

**Se apartó de `abierto` sin un hecho de hoy:**
- Rubio Ñu 1632067, por un antecedente;
- Sanjoanense 1647588 (copa), por la identidad;
- Casa Pia 1647580 (copa), por un banco probable que salió titular.

**El hecho estaba y no se usó:**
- Angers 1552825 (EJE-DEBUTANTE confirmada);
- Vila Nova 1650247 (banco con todos los cambios; el motivo «de llave» no vale);
- UD da Serra 1647591 (copa).

**Qué hacer.** Sin copa son 3 partidos. La regla es clara. Solo cuesta el primer grupo, porque `abierto` no se cobra. **Nada en el texto.** Si acaso, que el recibo rechace un `porqueDesenlace` que cite racha, identidad o antecedente: es la disciplina 6, aprobada.

### E. La pieza del seguro (63, v0.1.27): se sostiene y se cumple poco con el once

- **Se sostiene en la rama de ventaja** en unos 10 casos: Frankfurt 1575223, Dortmund 1575226, Freiburg 1575229, AEK 1593360, Paris FC 1552825, Osasuna 1570458 (con el relevo nombrado), Kasımpaşa 1584471 y Bolívar 1645545 (el cierre leyó el seguro roto).
- **Marseille 1552822:** el doble pivote amonestado salió junto y concedió dos. Es el 2.º caso del matiz C6 «doble pivote» (el 1.º fue Chapecoense).
- **Mal aplicada con el once (3 partidos):**
  - Hull 1557472: la pieza estaba en el banco de la hoja;
  - Estrela 1647582 (copa): la pieza no jugó;
  - Necaxa 1551046: `siIguala` empujando sin pieza nombrada, y concedió por ese carril.
- **La pieza salió al descanso, antes de abrirse la rama (3 partidos, `no_dice`):** Sporting 1647591 (copa), Juventus 1550201 y Monterrey 1551043. La 63 ya lo cubre: el cierre anota la salida y lee el reemplazo.
- **Qué hacer:**
  - **nada en el texto**;
  - **para la app**, el aviso aprobado y pendiente de la 65 («`porqueDesenlace` o la pieza nombrada fuera del once oficial»), extendido a la pieza del seguro de cada rama.

### F. Superioridad numérica: «no administra» 11 de 11 (16, C2)

- **Ganando, cargaron 5 y no administró ninguno:** Ajax 1552225, AZ 1552230, Liverpool 1557473, PAOK 1593365 y Nacional Potosí 1645542. Casi todos con dos goles o más de ventaja.
- **Empatando, cargaron:** Pumas 1551043, Hull 1557472, Gent 1558681, Union SG 1558685, Twente 1552232 (que concedió) y Once Caldas 1650176.
- **Perdiendo, persiguieron:** Delfín 1639836 y Huracán 1649568 (metió un defensor al 89').
- **Junto al 17/11:** ganando, 8 cargan contra 2 que administran (Cerro, Monterrey).
- **Qué hacer: candidato a medir** (C2: n ≥ 30 ganando y separar por margen). El texto actual se sostiene.

### G. Candidato «defecto por quien persigue» (65): 6 a favor, 1 en contra (7 partidos, 1 de copa)

- **El favorito persigue y rescata:** Barcelona 1570455 y Beşiktaş 1584473.
- **El no favorito persigue y se rompe:** Paderborn 1575222, Venezia 1550201, Huracán 1649568 y Torreense 1647592 (copa).
- **En contra:** Metropolitanos 1646938 (favorito, margen 0,65, se rompió).
- **Sube respecto del 17/11**, cuando hubo 1 explícito.
- **Qué hacer: candidato a medir.** Sigue la condición de la 65: `μ_partido` por tramo, n ≥ 30 por lado y los intervalos sin cruzarse. Las lecciones lo citan solo cuando encaja, así que esto no es medición.

### H. Candidato «doble golpe» (61): 4 partidos

UD da Serra 1647591 (copa), Barcelona 1570455, Real Sociedad 1570459 y Gimnasia M. 1649570. En todos el segundo gol llegó a 2 minutos del primero. El 17/11 hubo 1 (Danubio). **Candidato a medir**: los minutos ya están en los tramos. Sin medir lo que pasa después, no hay regla.

### I. La vía del empate en la rama de ventaja también son los **titulares** de la vía principal del rival (66, C6)

- **Querétaro 1551046** (`regla_fallo`): el empate llegó a los 2', por un extremo titular asistido por el pivote, no por el banco.
- **Racing 1570459:** la vía estaba bien en la categoría, pero el centro del lateral rival y el que saca los córners no estaban nombrados.
- **Benfica 1647592 (copa):** el `rescata` de `siLeEmpatan` lo hizo un titular antes de los cambios, no el banco del hecho.
- **Con Wanderers y Armenia–Cyprus del 17/11** se llega al 3.er caso ciego que pedía C6.
- **Qué hacer: aclarar en el skill (66), sin número:** la línea del empate nombra los titulares de la vía principal del rival, además del banco.

### J. El rehacer no revisa lo que la rama nombra del once (transversal, 4 partidos)

- Olimpia 1632065: el rehacer de las 20:45 no reescribió el banco de `porqueDesenlace` (un titular nombrado como banco).
- Hull 1557472: pieza en el banco.
- Levadiakos 1593361: antecedente de piezas, con el DTP rehecho diciendo lo contrario.
- Eyüpspor 1584474: rama escrita sobre el 4-1-4-1 de la hoja previa, que salió línea de cinco.

**Qué hacer: para la app** (aprobado en la 65 y pendiente): recalcular la rama y avisar cuando nombra a alguien fuera del once.

## Con 1-2 casos (no entran)

- **Roja propia ganando (C3):** sostuvieron Barcelona 1570455 e Instituto 1649568, concedió Manta 1639836. Junto al 17/11 queda 4 a 3: contradictorio, sigue a medir.
- **Roja propia empatando hasta el 45' (referencia 11 de 12):** se cumplió en Willem II, Man United, Estoril (copa) y, después del 45', en Brighton y Kortrijk. En contra, Atlético Nacional 1650176, que no concedió en 51'. Se sostiene.
- **ISE agravado con roja propia perdiendo:** ADO 1552225 a favor, Kifisia 1593365 en contra. El acumulado queda 3 a 3: nada.
- **Defecto «sigue atacando» que no se cumplió:** Genoa 1550206 (margen 0,35, administró por plan) y Atl. Goianiense 1650247 (0,54, administró y le empataron). Contra 26 sostenidos.
- **Defecto de `siIguala` que no se cumplió:** Atromitos 1593361 (visitante que iguala y vuelve al bloque). Académica 1647588 (copa) no tenía `siIguala` escrita.
- **Ventana desde el cambio ofensivo (C4):** 1 explícito, LDU 1639807 (gol al 84' tras tres cambios). Implícitos: Union Berlin 1575225 y Bulo Bulo 1645547. Sigue sin denominador.
- **F2 = 1 sin ECHADA-FIS:** Real Potosí 1645545 y La Guaira 1646938.
- **`siExpulsion`:**
  - plantilla sin la línea `rival`: Once Caldas 1650176;
  - la vía propia con diez debe nombrar el banco ya entrado: Monterrey 1551043;
  - el seguro de `rival` con su vuelta: Twente 1552232.
- **Huecos de `S1`:** roja del DT, Iraklis 1593362; roja de un interior sin amarillas, Kortrijk 1558685 (varianza). El suplente que entra y ve la roja no apareció.
- **ventajaPorFuerza citada del otro lado:** Augsburg 1575224. Lo arreglaría un recibo que compare la fuerza con el lado.
- **Banco con rotación anunciada en copa** (`insumo`): Mafra–Arouca 1647586.
- **Matices de la rama:**
  - Osasuna 1570458: si el M3 del DTP cierra con un pivote del banco, la rama dice desde qué tramo manda;
  - Racing 1570459: nombrar intérpretes y no solo la categoría.
- **El corte «antes del 75'» del banco como hecho:** Fenerbahçe 1584472 rescató con el banco desde el 76'.

## Comparación con el 17/11

| patrón del 17/11 | esta semana | juicio |
|---|---|---|
| 1. Banco desde la hoja (22: 16 mal aplicadas y 6 de insumo) | 3 mal aplicadas en 2 partidos (los dos del 22/11 en Paraguay) y 1 insumo de copa. 8 lecciones dicen que la lista entera cubrió a quien entró | **Bajó fuerte** |
| 2. `siExpulsion` incompleta (4) | 1 (sin la línea `rival`) | **Bajó** |
| 3. SOB1 sin régimen (5 `regla_fallo`) | Ahora es regla: 6 mal aplicadas y 3 cumplidas | **Se repite como incumplimiento** |
| 4. Tipología por identidad o antecedente (4) | 8, con C3 como motivo en 3 | **Se repite y sube** |
| 5. Pieza del seguro | Se sostiene, también en la rama de ventaja; 3 mal aplicadas con el once | Se sostiene |
| 6. Superioridad (contradictorio) | 11 de 11 no administra; ganando, 5-0 | Candidato a medir, ahora más inclinado |
| 7. Roja propia ganando (3 a 1 concede) | 2 sostienen y 1 concede | Contradictorio |
| 8. Ventana desde el cambio ofensivo | 1 explícito y 2 implícitos | Igual, sin denominador |
| 9. Huecos de `S1` | El suplente que ve la roja desapareció; roja del DT, 1 | **Bajó** |
| `S1` sobre la línea (17/11: 1 mal aplicada) | 4 mal aplicadas | **Sube** |
| C6, la vía del empate por titulares (2) | +1 ciego explícito (+2 afines) | **Llega al umbral** |
| Defecto por quien persigue (1) | 6 a favor y 1 en contra | Sube, a medir |
| Doble golpe (1) | 4 | Sube, a medir |

## Juicio sobre los arreglos de la app del 17/11

- **`bancoProbable`: funcionó.** Los errores de banco bajaron de 22 lecciones en 81 partidos a 4 en 71. No quedó ningún «titular nombrado como banco» de la lista de la rama.
- **Lo que queda del banco:**
  - un `porqueDesenlace` que el rehacer no reescribió (Olimpia 1632065);
  - el banco copiado en una sola rama (Rubio Ñu–Libertad 1632067, los dos lados).
  - Para la app: un aviso «banco ausente en rama donde entra».
- **`EFE-RECOMPUTO-PENDIENTE` y el rehacer:**
  - el TDE no habla de la F1;
  - lo que el once cambia en el TDE (la pieza del seguro, el banco de `porqueDesenlace`, el antecedente de piezas, el sistema de la rama SOB) sigue sin rehacerse en 4 partidos (patrón J).
- **`ventajaPorFuerza`:** se usa y se cumple en unas 14 lecciones. 1 la citó del lado equivocado.
- **Jev `lectura`:** no se puede juzgar con este archivo. Las 231 lecciones tienen `modoFallo: null`, también las de `orden` 1 con fallo.
- **El banco, la F1 y el arquero sin el homónimo (21/11 22:50):** ninguna lección del TDE habla de homónimos. No hay señal en ningún sentido.

## Datos raros

- No hay claves duplicadas. Todas las lecciones son ciegas `PRE`, acreditan y no tienen cuarentena.
- **Ninguna lección es del 17/11**, así que no hay ninguna escrita con la v0.1.26 en esta parte.
- `modoFallo` vale null en las 231, también en lados con `fallo` y `orden` 1. Hay que verificar si Jev corrió sobre esta cohorte.
- **Ninguna mal atribuida a otro skill.** Algunas citan al DTP como fuente buena: el DTP tenía al expulsado (Real Tomayapo) y el DTP rehecho tenía la línea (Levadiakos). Ahí la falla es del TDE al no tomar lo que el DTP traía.
- **Copa:** 29 lecciones de 10 partidos portugueses. Concentran 6 mal aplicadas y el único insumo.
