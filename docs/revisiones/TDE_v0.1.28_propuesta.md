# Propuesta de revisión · `teorema-del-echado` v0.1.27 → v0.1.28

> **APROBADA por el usuario el 24/11/2026, con todas las recomendaciones.** D1 (a) la rama de ventaja copia todos los renglones de `viasGol` del rival, cada uno con su intérprete, empezando por la vía principal en juego abierto · D2 (a) la rama nombra el relevo del mismo rol (o «sin relevo de rol») y el cierre lee por rol · D3 (b) `C3` no se suma al texto de la 44 (b); lo hace A5 en la app. Aplicados los puntos 1, 2, 3 y 5 (v0.1.28, 24.11.2026); el 4 no entra al texto; C1-C9 siguen candidatos.

**Estado: PROPUESTA (24/11/2026), para aprobar punto por punto.** No se tocó
el skill, ni el código, ni otros docs. Lo que se apruebe se aplica después,
con su entrada en `references/HISTORIAL.md` y sus anclas en
`scripts/nucleo_reglas.json` (punto 5).

**Base:** el estudio del 24/11 (`estudio_lecciones_2026-11-24/`: `README.md`,
`estudio_teorema-del-echado.parte1.md` y `.parte2.md`,
`clasif_teorema-del-echado.json`); la prosa de las 468 lecciones `pendiente`
de 135 partidos del 17 al 23/11, ciegas `PRE` y escritas con la v0.1.27; el
skill vigente (`SKILL.md` v0.1.27, 463 líneas; `references/HISTORIAL.md`);
`PENDIENTES.md`; el código de hoy (`backend/analisis/parte.py`, `tde.py`,
`app.py`), revisado para separar lo que la app ya hace de lo que falta.

Las líneas citadas son las del `SKILL.md` vigente. Insertando de abajo hacia
arriba no se corren.

### Honestidad con la muestra

- **Una semana, 135 partidos.** 57 lecciones son de copa nacional (17
  partidos: Copa del Rey, Copa de la División Profesional y Taça de
  Portugal). Cuentan para la rúbrica y no para las métricas. Están marcadas
  «copa» en cada caso.
- **Son conteos de lecciones, no tasas.** Quien cierra un partido nombra la
  regla sobre todo cuando algo pasa por ella, y la clasificación sale de leer
  la prosa, no de una medición. Ningún punto de esta propuesta afirma una
  tasa.
- **El veredicto del lado no mide la regla:** 118 de las 349 lecciones
  `regla_sostuvo` son de lados que fallaron, y 26 `mal_aplicada` son de lados
  que acertaron.
- **Jev no sirve para cruzar esta cohorte:** 453 de 468 lecciones tienen
  `modoFallo: null` (Jev sin crédito desde el 22/11; ya lo arregla la app,
  abajo). La clasificación del estudio no se apoyó en él.
- **El punto 1 tiene un riesgo propio:** pedir que la rama copie todas las
  vías del rival puede volverla imposible de refutar («alguna vía nombrada
  iba a ser»). Por eso el punto 1 no agrega cobro ni métrica: nombra
  intérpretes para que el cierre pueda decir cuál fue, y el desenlace lo
  siguen poniendo las referencias de la 66.

## 0. Resumen

Las reglas reescritas hasta la v0.1.27 se sostienen: 349 de 468 lecciones
(75 %) dicen que se cumplió. La 61 se sostiene en 78 lecciones (y 1 sin tramo), el
`abierto` de la 65 se cumple siempre que se escribe, la superioridad «no
administra» 11 de 11 en la parte 2 y `ventajaPorFuerza` se cita y se cumple
en casi todas las lecciones que la nombran. **Lo que más se repite es no
cumplir una regla ya escrita**: el `SOB1` sin condicionar (10 partidos), `S1`
sin la línea del choque (7), el hecho del desenlace (8) y lo que el rehacer
no reescribe (banco, pieza, sistema). Eso va a la app, como el
`bancoProbable` del 17/11, que bajó los errores de banco de 22 a 10.

Al texto entran tres aclaraciones, sin ningún número: la vía del empate se
copia del DTP del rival (cierra el C6 de la v0.1.27), el relevo de la pieza
del seguro, y lo que RELEVANCIA BAJA dice y no dice.

### Lo que ya hizo la app (no se pide de nuevo)

- **Desde el 17/11:** `bancoProbable` en `tde/{id}`, `dtp/{id}` y `f1/{id}`
  (#561); `referencias.ventajaPorFuerza` en `tde/{id}` (#563); el rehacer por
  FUERA-EN-LA-HOJA, ONCE-SIN-FILA-F1 y EFE-RECOMPUTO-PENDIENTE (#560); Jev
  `lectura` (#562); FUERA-EN-LA-HOJA también lee las notas de las ramas del
  TDE y el detalle de sus vías (incidencia 1434, `parte.py` líneas
  2180-2192).
- **20 y 21/11:** con los dos ids, el id manda en FUERA-EN-LA-HOJA (1455); el
  banco, la F1 y el arquero sin el partido del homónimo (1473). Ninguna
  lección del TDE habla de homónimos: no hay señal para juzgarlo.
- **22/11:** el tramo de la prórroga no cobra el gol a su ventana (1486; toca
  la disciplina 23). `ventajaPorFuerza` viaja **tapada** al token de Cowork
  hasta que se sella el 1X2 ciego (`app.py` 3390-3399): la rama de ventaja se
  escribe después de sellar y de volver a pedir `tde/{id}`.
- **24/11:** Jev sin crédito lo grita el escaneo (`jev-caido`) y
  `POST /analisis/jev/reetiquetar` rehace el modo de fallo sellado en error
  (2cc1c67).
- **Ya estaba:** el aviso TDE-RELEVANCIA-SIN-DECLARAR (`parte.py` 2563-2588,
  incidencia 791).

### Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos (partidos) | Recomendación |
|---|---|---|---|---|
| 1 | 66: la vía del empate de la rama de ventaja se copia de las `viasGol` del rival por renglón, con los titulares de su vía principal, no «banco + pelota parada» | aclaración (cierra C6 de la v0.1.27) | 8 `regla_fallo` (7 partidos) + 2 dentro de lecciones `sostuvo` | aprobar · **D1** |
| 2 | 63: la pieza del seguro con sus amarillas y su relevo del mismo rol; el cierre lee «seguro roto» solo sin relevo de rol, también si la pieza salió antes de abrirse la rama | aclaración | 13 partidos (6 de relevo, 4 de doble pivote, 5 con la pieza ya fuera) | aprobar · **D2** |
| 3 | 50: RELEVANCIA BAJA dice «lean las ramas», no «el partido se resuelve antes»; la premisa pasa a candidato | aclaración (premisa a medir) | 3 `regla_fallo` + 2 `sostuvo` | aprobar |
| 4 | 44 (b): `C3` en la lista de «no son motivo» | incumplimiento de regla escrita → app (A5); texto opcional | 3 | **no entra** al texto · **D3** |
| 5 | Versión, historial y anclas del núcleo | trámite | — | aprobar |
| C1-C9 | Candidatos a medir | candidato | 2 a 15 | no entran |
| A1-A9 | Para la app | app | — | después de aprobar |

---

## 1. La vía del empate se copia del DTP del rival (disciplina 66) — ACLARACIÓN

**Qué dice hoy.**
- Líneas 439-445: la tipología de la rama de ventaja dice «**por dónde**
  llegaría el empate (el banco del rival, la contra, la pelota parada)».
- Línea 447: «La rama de ventaja nombra el banco ofensivo del rival que
  persigue».
- En ningún lado dice de dónde salen las vías del rival ni que los titulares
  también lo son. La v0.1.27 dejó el matiz como candidato C6 («la vía del
  empate también son los titulares del rival que domina»), con 2 casos y
  pidiendo el tercero ciego.

**Qué pasó.** En 7 partidos la nota de `siMarcaPrimero` nombró «banco +
pelota parada» y el empate llegó por un renglón que la lista de salida de
`viasGol` del DTP (v1.9) tiene y la nota no copió:

| equipo (lado que iba ganando) | fixtureId | por dónde llegó el empate | renglón del DTP |
|---|---|---|---|
| Gales | 1528992 | centro de Trincão a la espalda de C. Roberts, al segundo palo, a los 3' | 6, lado débil (el DTP rival lo tenía) |
| Portugal (mismo partido) | 1528992 | rebote del área: Costa tapa, Colwill la devuelve, Brooks define | 8, pelota sucia (el DTP la listaba) |
| Polonia | 1528998 | combinación en el área de los titulares suecos, a los 8' | 1-6, titulares |
| Athletico-PR | 1492453 | carril derecho de Flamengo contra Esquivel reconvertido, a los 6' | el DTP del parte lo listaba |
| Belgrano | 1649571 | remate de afuera del 9 titular de Vélez | 7, media distancia |
| Puebla | 1551039 | centro del carrilero Duarte y remate de Mora (48') | 1, juego abierto |
| Feyenoord | 1552226 | contra a la espalda de los laterales, a los 4' | 3, la vía `SOB` de su propia base |
| Querétaro | 1551046 | extremo titular M. Rodríguez, asistido por el pivote Ochoa, a los 2' | 6, titulares |

- **Dentro de lecciones `sostuvo`, lo mismo:** Vasco 1492458 (el empate fue
  de dos centrales de Inter, no del banco nombrado) y Racing 1570459 (la vía
  estaba en categoría, «la pelota parada», pero no el lateral que centra ni
  quién saca los córners).
- **Cuando la vía nombrada era la buena, se cumplió:** Palmeiras 1492452,
  Always Ready 1650230 (copa), Juárez 1551040 y Guaraní 1632066; y el banco de la
  hoja nombrado decidió en Gales 1528992 (Forbs) y Excelsior 1552226 (Borges).
- **Lectura:** el texto de la 66 siembra la falla. Su paréntesis enumera
  banco, contra y pelota parada, y la rama copia esa lista. El DTP ya tiene la
  lista completa por renglón (v1.9, `SKILL.md` del DTP, línea 122): falta
  que el TDE la tome. Con Wanderers y Armenia–Chipre del 17/11, el C6 pasa de
  2 casos a 9 partidos.

**T1 · dos cambios en la 66.**

Primero, en la línea 442, donde dice «(el banco del rival, la contra, la
pelota parada)», va:

> (los renglones de las `viasGol` del rival: sus titulares en juego abierto,
> la contra, la pelota parada y el banco)

Segundo, sub-ítem nuevo después de la línea 445 («…eligiendo con su motivo
(44 (b)).»):

> - **La vía del empate se copia del DTP del rival, renglón por renglón
>   *(v0.1.28)*.** La nota de `siMarcaPrimero` no resume las vías del rival en
>   «banco + pelota parada». Copia las `viasGol` del rival que trae el DTP del
>   mismo parte (su lista de salida), **cada renglón con su intérprete**, y
>   empieza por la vía principal en juego abierto con sus **titulares**: el
>   que centra, el extremo, la segunda línea, la media distancia del 9, la
>   pelota sucia. El banco de `bancoProbable` es un renglón más, no la vía
>   entera. Si el que va ganando «sigue atacando», la contra que su propia
>   base `SOB` ya nombra también va como vía del empate. Sin DTP del rival en
>   el parte, se dice, y se nombran los titulares de su vía principal desde
>   la investigación, con fuente.
>
>   No cambia el desenlace de la rama, que lo ponen las referencias, ni el
>   cobro: sirve para que el cierre diga por cuál renglón llegó el empate.

- **Historial:** los 7 partidos de la tabla, Vasco y Racing, y los 2 del
  17/11 (C6 de la v0.1.27).
- **Lo tumbaría:** que, con la nota copiada por renglón, el empate siga
  llegando por vías que no están en ninguno de los dos lados del DTP. Ahí la
  falla sería del DTP, no de la copia.

**Por qué no más.**
- No se pide que la rama acierte la vía. Una lista larga siempre contiene la
  vía que pasó, y por eso no se propone medir «vía nombrada = vía real» como
  acierto.
- «Nombrar intérpretes y no la categoría» (Racing) ya es regla del DTP (v1.8,
  «cada vía nombra zona o intérprete»). La copia la trae; no se repite.
- No se extiende a `siLeEmpatan` ni a `siIguala`: las lecciones que piden la
  vía por titulares son todas de la rama de ventaja.

## 2. El relevo de la pieza del seguro (disciplina 63) — ACLARACIÓN

**Qué dice hoy.**
- Línea 391: la pieza que sostiene el `sob2` se nombra, y «**el cierre anota
  el minuto en que esa pieza salio, por cambio o por roja**, y lee el tramo
  desde ahi con el seguro roto».
- Líneas 392-397 (v0.1.27): lo mismo en las ramas que no persiguen, y con el
  once oficial la pieza está en el once.
- No dice qué pasa si entra otro del mismo rol, ni qué pasa si la pieza ya no
  estaba cuando la rama se abrió.

**Qué pasó.**

**(a) La pieza salió y entró otro del mismo rol: el seguro no se rompió (6
partidos).**
- Sportivo Ameliano 1632063 (`regla_fallo`): W. Rodríguez salió al 29' y su
  reemplazo, J. Benítez, pivote de oficio amonestado al 38', sostuvo la
  ventaja del 62' al final sin conceder. La lección pide nombrar al heredero.
- Lazio 1550202: Belahyane salió al 83' por Rovella, pivote de oficio; no
  concedió.
- Como 1550200: Milla salió al 57' por Perrone, «el heredero que la rama
  escribía»; Cagliari, 1 remate al arco en el partido.
- Coventry 1557471: el doble pivote salió entero al 71' con 2-2 y con Onyeka
  y Hamer no concedió.
- Nottingham Forest 1557468: Yates salió al descanso por Schlager; con 2,92
  de xG rival no concedió más.
- Osasuna 1570458: la nota ya nombraba a Torró como relevo del doble pivote;
  el Málaga terminó con 0 remates al arco. En el mismo partido, el Málaga
  nombró a Pablo Martínez «salvo que entre Enríquez», y así fue.

**Donde salió sin relevo de rol, sí concedió:** Chelsea 1557470 (Caicedo
lesionado al 22', concedió cuatro), Coritiba 1492451 (las dos piezas fuera
al 70' y al 79', gol al 90+2) y Liverpool Montevideo 1650504 (Garayalde
salió al 28' por un suplente sin fila, concedió al 31').

**(b) Doble pivote y amarillas (4 partidos):** Bragantino 1492459 (Fabinho,
amonestado al 64', salió al 69'), Marseille 1552822 (los dos del doble
pivote amonestados, salieron juntos al 74' y concedió dos), Coventry 1557471
(Grimes amonestado) y Osasuna 1570458. Liverpool Montevideo 1650504 pide lo
mismo: la pieza, con sus amarillas.

**(c) La pieza ya estaba fuera cuando se abrió la rama (5 partidos):**
- Badajoz 1644346 (copa, `regla_fallo`): Agirre salió al descanso, la roja
  rival fue al 58' y concedió dos;
- Gales 1528992: Rodon fuera desde el 45' en `siExpulsion.rival`;
- Sporting 1647591 (copa): Altimira salió al 46', antes del gol;
- Juventus 1550201: Douglas Luiz salió al descanso, la rama abrió al 53' y
  «se jugó entera con el seguro en Sarr»;
- Monterrey 1551043: la lección pide leer el tramo «con el banco que la
  reemplazó, no con la nombrada».

**T2 · 63, dos cambios.**

Primero, en la línea 391, donde dice «y lee el tramo desde ahi con el seguro
roto.», va:

> y lee el tramo desde ahi con el seguro roto, salvo que entre otro del mismo
> rol (ver «El relevo de la pieza», abajo).

Segundo, sub-ítem nuevo después de la línea 397 («…se declara la rama sin
pieza.»):

> - **El relevo de la pieza *(v0.1.28)*.** La rama nombra la pieza **con sus
>   amarillas** y, desde `bancoProbable`, **quién la releva en el mismo rol**,
>   o escribe «sin relevo de rol». Si el seguro es un doble pivote, se nombran
>   las dos piezas. Por ejemplo: «seguro: el doble pivote X e Y (Y con
>   amarilla) · relevo del rol: Z, del banco de la hoja».
>   - El cierre lee «seguro roto» **solo si el que entra no es del rol**. Un
>     pivote que entra por el pivote mantiene el seguro; un delantero o un
>     lateral que entra por él lo rompe.
>   - Si la pieza ya salió cuando la rama se abre, el cierre lee la rama con
>     el seguro que hay en cancha en ese minuto, con la misma regla del rol.
>   - Es lectura del mecanismo, como arriba: no cambia el `sob2` declarado,
>     ni el ISE de rama, ni el cobro (61).

- **Historial:** los 13 partidos de (a), (b) y (c), y los 3 que concedieron
  sin relevo.
- **Lo tumbaría:** que con el relevo del mismo rol la rama conceda igual que
  sin él. Se mide con A4 (`piezaSeguro`, pendiente desde la v0.1.27).

**Por qué no más.**
- No se dice qué pasa cuando salen las dos piezas del doble pivote a la vez:
  Marseille concedió dos con el cambio doble y Coventry no concedió con el
  suyo. Va a C6.
- «Rol» se lee con la posición de la hoja y el `titularHabitual` de
  `bancoProbable`. No hay una tabla de roles equivalentes ni se propone.
- El central reconvertido de una línea de tres como pieza del seguro
  (Rumania 1528999) es un caso solo.

## 3. RELEVANCIA BAJA dice «lean las ramas» (disciplina 50) — ACLARACIÓN

**Qué dice hoy (línea 353).** «La derivacion asume que el partido llega vivo
al minuto 75, y cuando **ningun equipo tiene protector declarado** —los dos
con `SOB1 = 0.5` y `P1a = 0.5`— el partido se resuelve antes. El output
declara `RELEVANCIA BAJA` y comunica que la lectura util es la reasignacion
condicional, no la ventana.»

**Qué pasó.** En 3 partidos con RELEVANCIA BAJA declarada, el partido llegó
vivo y empatado al tramo final:
- Cercle Brugge–Westerlo 1558682: 0-0 al 71', y el gol cayó dentro de la
  ventana del reloj 60-75;
- Sportivo Ameliano–Sportivo Luqueño 1632063: 0-0 al 62' y abierto por un
  gol hasta el final;
- Aston Villa–Sunderland 1557467: 0-0 al 75'; la lectura útil fue la del que
  empuja.

En los tres, **la consecuencia se cumplió**: lo comprobable fueron las ramas
del primer gol, no la ventana. Lo que falló es la premisa. Se cumplieron las
dos: São Paulo 1492457 (decidido al 32') y Portugalete 1644369 (copa,
ninguna rama se abrió en 120').

**T3 · 50, línea 353.**

Donde dice «el partido se resuelve antes. El output declara», va:

> el reloj deja de ser la pregunta: sin nadie que proteja, el partido lo
> ordena el primer gol. El output declara

Y al final del párrafo («…delimita cuando preguntarla.»):

> **RELEVANCIA BAJA no anuncia que el partido se resuelva antes del 75
> *(v0.1.28)*.** Dice que se lea por ramas. Si el partido llega vivo y sin
> goles al tramo final, la lectura sigue siendo la rama que abra el primer
> gol, y la ventana se escribe y se puntúa igual (Cercle–Westerlo,
> Ameliano–Luqueño y Aston Villa–Sunderland llegaron 0-0 más allá del 60').

- **Historial:** los cinco partidos.
- **Lo tumbaría:** que los partidos sin protector lleguen vivos al 75' tanto
  como el resto **y** que la lectura por ramas tampoco sirva en ellos. La
  primera mitad se mide (C8).

**Por qué no más.** El criterio de entrada (`SOB1` y `P1a` en 0,5 en los dos
lados) es un umbral y no se toca. La ventana se sigue escribiendo, como ya
dice la regla, para no romper la serie. El aviso de la app
(TDE-RELEVANCIA-SIN-DECLARAR) dice hoy «el tramo final no decide el
partido»: cambiar ese texto es A7.

## 4. `C3` no elige la tipología de la rama (44 (b)) — NO ENTRA AL TEXTO

**Qué dice hoy.**
- Línea 338: «`C3 = 1` sigue siendo el tope del bloque C (disciplina 49), pero
  **no elige la tipologia de la rama**», dentro del sub-ítem de `ECHADA-PSI`.
- Línea 333: «**No son motivo** para ninguna de las dos tipologias el anuncio
  de un DT, el clasico, la posicion en la tabla ni la racha».

**Qué pasó (3 partidos, `mal_aplicada`).**
- Nacional Potosí 1645542: `ECHADA-PSI` por el 1-0 perdido en Oruro. Con el
  1-0 al 34' siguió llegando y amplió a 3-0. La lección lo marca «otra vez».
- Mushuc Runa 1639837: `ECHADA-PSI` por dos ventajas de uno perdidas,
  trasladada a una ventaja de dos.
- Deportivo La Guaira 1646938: `ECHADA-VOL` porque «con el interino no
  sostuvo cuatro ventajas» (`C3`) y por `F2` = 1; con ventaja desde el 42'
  hizo tres goles más.

**Juicio.** La regla está escrita en términos generales («no elige la
tipologia de la rama»), y los tres casos la incumplen. Con la regla del
encargo, no se reescribe. Va a la app: un `motivoTipologia` de lista cerrada
en la rama de ventaja, con aviso si va vacío o dice solo `C3` (A5). La
alternativa barata, si el usuario la quiere, es sumar `C3` a la lista de la
línea 333, que es la que el analista recorre para elegir el motivo (D3):

> **Texto, solo con D3 (a).** En la línea 333, donde dice «la posicion en la
> tabla ni la racha (Viseu–Rio Ave; Sunderland–Chelsea, «siete sin ganar»).»,
> va: «la posicion en la tabla, la racha (Viseu–Rio Ave; Sunderland–Chelsea,
> «siete sin ganar») ni las ventajas perdidas en la temporada (`C3` = 1, que
> topa el bloque C y no elige la tipologia: Nacional Potosí, Mushuc Runa, La
> Guaira) *(v0.1.28)*.»

**El resto de la 44 (b) de esta semana también es incumplimiento**, con la
regla escrita:
- «administra» sin motivo: Trinidense 1632065, Libertad 1632067, Atlético CP
  1647580 (copa);
- antecedente que no coincide: Palmeiras 1492452 (pieza ausente), Levadiakos
  1593361 (una pieza distinta, como decía el DTP rehecho) y Cartagena
  1644353 (copa, sostenido por el arquero).

Para esos va A5 junto con el `fixtureId` del antecedente, pendiente desde la
v0.1.25.

## 5. Versión, historial y anclas — TRÁMITE

- **`SKILL.md`, línea 8:** «Versión vigente: **v0.1.28 (<fecha de
  subida>)**».
- **`references/HISTORIAL.md`:**
  - la nota T0 (abajo) arriba de la de la v0.1.27;
  - una sección «v0.1.28 — casos que motivaron cada punto» con las tablas de
    los puntos 1 a 3, los candidatos C1-C9 y lo que no entra;
  - en «Textos reemplazados en la v0.1.28», las tres frases que se
    reemplazan: la línea 442 (paréntesis de la vía), la 391 («lee el tramo
    desde ahi con el seguro roto.») y la 353 («el partido se resuelve
    antes.»).
- **`scripts/nucleo_reglas.json`, anclas de `teorema-del-echado`**, tres
  nuevas:
  - «La vía del empate se copia del DTP del rival»;
  - «El relevo de la pieza»;
  - «RELEVANCIA BAJA no anuncia que el partido se resuelva antes».

  El núcleo pesa hoy 54.782 tokens (`python -m backend.test_nucleo_skills`)
  contra un tope de 60.278. Los textos nuevos suman ≈ 0,7 K, así que el tope
  no se mueve.
- **Fuera del skill, con la subida:**
  - `("teorema-del-echado", "v0.1.28")` en `SUBIDA_VERSION`
    (`backend/analisis/simulacion.py`, línea 131);
  - la versión en la lista de `backend/analisis/lecciones.py` (línea 1598);
  - la línea de versión de `docs/skills/README.md` (línea 14).

---

## Candidatos a medir (no entran)

Ningún número se mueve sin backtest.

| N.º | Qué | Esta semana | Qué haría falta |
|---|---|---|---|
| C1 | **Peso de `SOB1` de tabla sin un hecho de hoy** (de la v0.1.27) | 10 obligados escritos sin condicionar y en ninguno hubo exposición con línea de cinco o con el rival dueño de la pelota (Athletico-PR 1492453, São Paulo 1492457, Cerro 1650503, Wanderers 1650504, Paderborn 1575222, América 1551044, ADO 1552225, OH Leuven 1558680, OFI 1593363, Bulo Bulo 1645547). Más Tijuana 1551038, que administró en parte con 1-0 | lo de la v0.1.27: ramas `SOB` del obligado partidas por sistema del grid y posesión prevista, n ≥ 30 por lado. Lo destraba A1 |
| C2 | **Superioridad según el marcador** | ganando cargaron los 7 (Irlanda 1528997, Troyes 1552827, Ajax 1552225, AZ 1552230, Liverpool 1557473, PAOK 1593365, Nacional Potosí 1645542); empatando o perdiendo cargaron todos (Gales 1528992, Pumas 1551043, Hull 1557472, Gent 1558681, Twente 1552232, Once Caldas 1650176, Huracán 1649568 y otros) | tramos con uno más por marcador y minuto (A2 de la v0.1.27); n ≥ 30 ganando, separado por margen |
| C3 | **Roja propia ganando** | contradictorio: concedieron Melgar 1549554, Tenerife 1644346 (copa) y Manta 1639836; sostuvieron Portugal 1528992, Barcelona 1570455 e Instituto 1649568 | la tabla de concesión tras roja propia por marcador (A2 de la v0.1.27) |
| C4 | **Ventana desde el cambio ofensivo** | LDU 1639807 (gol al 84' tras tres cambios); implícitos Union Berlin 1575225 y Bulo Bulo 1645547. Sin denominador | A3 de la v0.1.27 |
| C5 | **Huecos de `S1`** | suplente que entra y ve la roja: Bucaramanga 1650173; roja del DT: Iraklis 1593362; roja de un interior sin amarillas: Kortrijk 1558685 | primero el insumo (A2 de esta propuesta) |
| C6 | **Matices de 1-2 casos** | las dos piezas del doble pivote fuera a la vez (Marseille 1552822 concedió, Coventry 1557471 no); la pieza de la VÍA en la rama que persigue (Bayern 1575221, Kane y Olise); el central reconvertido de la línea de tres como seguro (Rumania 1528999); el hecho de `SOB1` también en ramas con `sob1` 0,5 (Everton de Viña 1505565, ADO 1552225); el régimen condicionado a los cambios que queden (Central Español 1650505); nombrar intérpretes de la pelota parada (Racing 1570459, lo cubre el DTP) | el tercer caso ciego de cada uno |
| C7 | **El defecto por quien persigue** (65, de la v0.1.25) | 14 a favor y 1 en contra. El favorito que persigue rescata: Flamengo 1492453, Troyes 1552827, Bayern 1575221, Barcelona 1570455, Beşiktaş 1584473. El no favorito se rompe: Utebo 1644384 (copa), Lecce 1550202, Ipswich 1557476, La Louvière 1558684, Deportivo 1570453, Paderborn 1575222, Venezia 1550201, Huracán 1649568, Torreense 1647592 (copa). En contra: Metropolitanos 1646938. **Las lecciones lo citan cuando encaja: no es medición** | la condición de la 65: `μ_partido` por tramo (A6 de la v0.1.27), n ≥ 30 por lado, intervalos sin cruzarse |
| C8 | **La premisa de RELEVANCIA BAJA** (punto 3) | 3 llegaron vivos y 0-0 más allá del 60'; 2 no | con los tramos del veredicto: de los partidos con `SOB1` y `P1a` ≤ 0,5 en los dos lados, cuántos llegan al 75' empatados o a un gol, contra el resto, por liga |
| C9 | **«Doble golpe»** (61, de la v0.1.25) | 8 partidos con el segundo gol a ≤ 3' del primero: Norway 1528993, Badajoz 1644346 (copa), Cerro Largo 1650501, Nice 1552824, UD da Serra 1647591 (copa), Barcelona 1570455, Real Sociedad 1570459, Gimnasia M. 1649570 | los minutos ya están en los tramos: qué pasa después, con denominador, antes de redactar nada |

**Uno más, sin número para proponer:** el favorito con margen ≥ 0,30 que se
aparta del defecto «sigue atacando» con un motivo nombrable.
- Falló en 4: Tenerife 1644346 y Sabadell 1644384 (copa, `F2` = 1), Arsenal
  1557475 (antecedente de cinco coincidencias, margen 0,80) y Cartagena
  1644353 (copa).
- Se sostuvo en 3: Ucrania 1528994, Boston River 1650500 y Alavés 1570453.
- El defecto falló en 2: Genoa 1550206 (margen 0,35) y Atlético Goianiense
  1650247 (0,54).
- La 44 (b) ya dice que `F2` = 1 «no se aplica solo». Hace falta la tasa de
  «administra» cumplido por motivo, con n ≥ 30 por motivo.

## No entran (1-2 casos, o se sostienen sin cambio)

- **`P1a` bajado a mano por «necesita ganar»:** Grêmio 1492454 y Torque
  1650502. La 10 y la 47 ya lo prohíben.
- **`ECHADA-SUP` por identidad o «sin nada en juego»:** Progreso 1650502 y
  Atlante 1551038. Lo prohíbe la disciplina 6.
- **Rama y DTP del mismo equipo sin decir cuál manda:** América de Cali
  1650173 y Cerro 1650503. Está escrito en la v0.1.26.
- **Falsador:** Racing Montevideo 1650505 (atado al marcador, ya prohibido) y
  Köln 1575221 (escrito sobre remates de afuera).
- **Tipología del obligado:** Vitória 1492459, Wanderers 1650504, Tijuana
  1551038 y Betis 1570462, cada uno en una dirección distinta.
- **ISE agravado con roja propia perdiendo:** a favor Le Havre 1552827 y ADO
  1552225; en contra Kosovo 1528997 y Kifisia 1593365. Sigue contradictorio.
- **Roja propia empatando hasta el 45':** se cumplió varias veces. En contra,
  solo Atlético Nacional 1650176, que no concedió en 51'.
- **El que iguala:**
  - `siIguala` que no siguió empujando: Atromitos 1593361;
  - `siIguala` sin escribir: Académica 1647588 (copa);
  - en copa sin el 90-120: Alcoyano 1644334. Ya lo pide la 16.
- **`siExpulsion`:** Once Caldas 1650176 (sin la línea `rival`), Monterrey
  1551043 y Twente 1552232. La plantilla de la v0.1.27 se cumple en el resto.
- **`ventajaPorFuerza` citada del otro lado:** Augsburg 1575224 (A8).
- **El corte «antes del 75'» del banco como hecho:** Fenerbahçe 1584472
  rescató con el banco desde el 76'.
- **Insumo:**
  - banco vacío o con rotación en copa: Reddis–Barakaldo 1644373 y Mafra
    1647586;
  - once tardío: Crystal Palace 1557471 y Recoleta–Guaraní 1632066 (grid
    corregido).
- **Bloque de cinco de plan leído «improvisado» por el checklist:** Köln
  1575221. Es del DTP.
- **Se cierran sin texto:**
  - la 61, 78 lecciones sostenidas y 1 sin tramo;
  - el `abierto` de la 65;
  - la 66 con `ventajaPorMinuto` y `ventajaPorFuerza`, y la 44 (b) con su
    defecto (26 de 31 en la parte 2);
  - el `bancoProbable` copiado entero, que se sostiene en todas las lecciones
    que lo citan.

## Para la app (no entra al skill)

Verificado en `backend/` el 24/11. **Lo que movió la conducta el 17/11 fue el
dato, no el texto.** Estas son las reglas escritas que se incumplen, con el
dato o el aviso que las haría cumplir.

| N.º | Qué | Incumplimiento que ataca | Estado hoy |
|---|---|---|---|
| A1 | **`seExponeSi` en la base `SOB` y en la rama del obligado**, con aviso `SOB-SIN-GATILLO` si falta con `SOB1` = 1 y el grid trae línea de cinco o el DTP prevé que cede la pelota | 18 (v0.1.27): 10 partidos (C1) | no existe |
| A2 | **La línea del choque en `tde/{id}`:** zaga, pivote y 9 del once (o del probable) con sus amarillas, quien vuelve de roja y las rojas del equipo en la temporada; la nota de `S1` la copia como copia el banco | 16 (`S1` sobre la línea, v0.1.26): Melgar 1549554, Charleroi 1558683, Le Havre 1552827, Real Tomayapo 1645542, Manchester United 1557473, Atlético Nacional 1650176 e Instituto 1649568. En Real Tomayapo el DTP tenía al expulsado | `S1` sigue en `noCalculables` (`tde.py` línea 461); las amarillas están en `f1/{id}`. Es el A5 de la v0.1.27, sin hacer |
| A3 | **El rehacer revisa lo que la rama nombra del once.** (i) FUERA-EN-LA-HOJA lee también `porqueDesenlace`. (ii) Un aviso si la pieza del seguro nombrada no está en el once (Hull 1557472, Estrela 1647582, copa). (iii) Un aviso si el sistema de la rama `SOB` no es el del grid (Eyüpspor 1584474). (iv) Un aviso «banco ausente en rama donde entra» (Libertad–Rubio Ñu 1632067, los dos lados) | 66 y 65 (banco y rehacer): Olimpia 1632065, Remo–Chapecoense 1492456, IdV–Macará 1639806, Juárez 1551040, Nice 1552824 | (i) hoy el cruce lee `nota` y `vias.detalle`, no `porqueDesenlace` (`parte.py` 2186-2192). (ii) necesita A4 de la v0.1.27 (`piezaSeguro`). (iii) y (iv), nuevos. Recalcular el ISE de rama al rehacer sigue pendiente (65, línea 413) |
| A4 | **El hecho del desenlace:** con `bancoProbable` y los cambios disponibles, la app sugiere el condicional («si recibe antes del 75 con cambios por hacer») junto a `porqueDesenlace` | 65 (el hecho estaba y no se usó): Austria 1528996, Roma y Parma 1550205, Angers 1552825, Vila Nova 1650247, UD da Serra 1647591 (copa). Sin hecho de hoy: Rubio Ñu 1632067, Sanjoanense 1647588 y Casa Pia 1647580 (copa) | no existe. Un rechazo por «racha, identidad o antecedente» pediría leer prosa: no se pide |
| A5 | **`motivoTipologia`** de lista cerrada en `siMarcaPrimero` (y en «sostiene el punto» de `siIguala`): `P1b` · `F2` · plan del DT en el DTP · antecedente con su `fixtureId`. Aviso si va vacío, si es solo `C3` o si el favorito con margen ≥ 0,30 escribe «administra» sin él. Con el `fixtureId`, el recibo muestra el xG en contra y las atajadas de esa ficha (pendiente desde la v0.1.25) | 44 (b): punto 4 y los 6 casos de su párrafo final | no existe |
| A6 | **Aviso opcional:** la rama de ventaja no nombra a nadie del primer renglón de `viasGol` del DTP rival | punto 1 | opcional: el cruce por nombre ya existe para el banco (`identidad.menciona`) |
| A7 | **Texto del aviso TDE-RELEVANCIA-SIN-DECLARAR:** «(el tramo final no decide el partido)» pasa a «(sin protector: el partido se lee por ramas)» | punto 3 | `parte.py` líneas 2586-2587 |
| A8 | **`ventajaPorFuerza` del lado que marca:** el recibo avisa si la nota cita el tramo del otro lado | Augsburg 1575224 (1 caso, barato) | opcional |
| A9 | **Pendientes de la v0.1.27 que siguen:** A2 (concesión tras roja por marcador), A3 (minutos desde el cambio ofensivo), A4 (`piezaSeguro`), A6 (quién persigue por `μ_partido`) | C2-C4, C7 y punto 2 | sin hacer. A4 sirve a la vez al punto 2 y a A3 (ii) |

**Orden sugerido:** A1 y A2 primero (17 partidos entre los dos, y el mismo
camino que el `bancoProbable`), después A3 (i), que es de una línea.

## Coherencia entre skills

| Cambio | Depende de | Qué hacer |
|---|---|---|
| 1 (vía del empate) | **DTP v1.9**: lista de salida de `viasGol` (`SKILL.md` del DTP, línea 122) y «la razón de cada rama cita sus vías por renglón» (línea 144) | El TDE copia el `foco` del DTP del rival. Si la DTP v1.10 (en redacción) cambia el renglón 6 («el que llega no sale del renglón…»), la copia lo hereda sin tocar el TDE |
| 2 (relevo) | **DTP v1.9**, M3 («quién queda atrás» por rama); el README del 24/11 pide para la app un campo de quién queda atrás por rama (DTP M3, 10 partidos) | Si ese campo se hace, es la misma pieza que `piezaSeguro` (A4 de la v0.1.27): un solo campo para los dos skills |
| 3 (RELEVANCIA BAJA) | **sad-analysis** lee las ramas, no la alerta | Sin cambio |
| 4 (`C3`) | **EFE**: `C4` del EFE como antecedente (Marseille 1552822) | Sin cambio; A5 recibe el `fixtureId` del antecedente de cualquiera de los dos |
| 5 (núcleo) | Las anclas del TDE y la misma guardia | El tope no se mueve |

**Bloqueos para redactar:** ninguno. El punto 2 se puede aplicar antes de
A4: el cierre lo lee a mano, como hoy.

## Qué NO se propone

- **Ningún número:** ni el peso de `SOB1` (C1), ni un casillero de `S1` (C5),
  ni el desdoble de la superioridad o de la roja ganando (C2, C3), ni el
  umbral de RELEVANCIA BAJA, ni el corte de margen 0,30 de la 44 (b), ni el
  corte del 30' de la 66.
- **Ninguna regla repetida:** el `SOB1` condicionado, `S1` sobre la línea, el
  hecho del desenlace, el banco al rehacer y `C3` (D3 (b)) están escritos. Lo
  que los hace cumplir es A1-A5.
- **Ningún juicio contra el mercado:** la rama no se evalúa por si la casa ya
  cobraba el empate. Se evalúa por si describió el tramo.
- **Ni reetiquetar con Jev lo ya sellado:** eso lo hace la app con su propio
  endpoint.

## Decisiones del usuario

| | Pregunta | (a) | (b) | Recomiendo |
|---|---|---|---|---|
| **D1** | Cuánto copia la rama de ventaja (punto 1) | todos los renglones de `viasGol` del rival, cada uno con su intérprete, empezando por la vía principal en juego abierto | solo el renglón principal en juego abierto + el banco + la pelota parada | **(a)**: el empate llegó por los renglones 1, 3, 6, 7 y 8, no siempre por el principal (Belgrano, media distancia; Portugal, pelota sucia; Feyenoord, su propia contra) |
| **D2** | El relevo de la pieza (punto 2) | la rama nombra el relevo del mismo rol (o «sin relevo de rol») y el cierre lee por rol | solo el cierre lee por rol, sin pedir el relevo en la rama | **(a)**: en Como y Osasuna el relevo escrito dejó el cierre comprobable; en Ameliano, sin él, la regla de hoy leía «seguro roto» y no lo estaba |
| **D3** | `C3` en la lista de «no son motivo» (punto 4) | se suma a la lista de la línea 333 | no se toca el texto; lo hace A5 | **(b)**: la regla ya dice «no elige la tipologia de la rama», y en el 17/11 y el 24/11 lo que cambió la conducta fue el dato. Si A5 no se hace en esta tanda, **(a)** cuesta una línea |

## T0 · nota de versión (va directo a `references/HISTORIAL.md`)

> **v0.1.28 · <fecha de subida> — la vía del empate sale del DTP y el seguro
> tiene relevo.**
>
> Revisión desde el estudio del 24/11/2026: 468 lecciones `pendiente` de 135
> partidos del 17 al 23/11, ciegas `PRE` y escritas con la v0.1.27. Ningún
> número se mueve.
>
> - **66:** la vía del empate de la rama de ventaja se copia de las
>   `viasGol` del rival por renglón, con sus titulares en juego abierto; el
>   banco es un renglón más (cierra el C6 de la v0.1.27).
> - **63:** la pieza del seguro va con sus amarillas y su relevo del mismo
>   rol; el cierre lee «seguro roto» solo sin relevo de rol, también si la
>   pieza salió antes de abrirse la rama.
> - **50:** RELEVANCIA BAJA dice «lean las ramas», no que el partido se
>   resuelva antes; la premisa queda a medir.
> - **Para la app, no en el texto:** el `SOB1` sin gatillo, `S1` sin la línea
>   del choque, el hecho del desenlace, el rehacer de la rama y la tipología
>   sin motivo son reglas ya escritas que se incumplen.
> - **Candidatos, no aplicados:** el peso de `SOB1`, la superioridad y la
>   roja propia según el marcador, la ventana desde el cambio ofensivo, los
>   huecos de `S1`, el defecto por quien persigue, la premisa de RELEVANCIA
>   BAJA, el «doble golpe» y los matices de un caso.
