# Propuesta de revisión · `efe-clasificador` v1.11 → v1.12 (+ `efe-dashboard` v1.14 → v1.15)

> **APROBADA por el usuario el 24/11/2026, con todas las recomendaciones.** 1. (a) F3 de ATK o MID «cubierta» también por la segunda línea o por el banco de la casilla, solo confianza en la K, sin prometer volumen intacto ni extenderse a DEF · 2. (a) entra la frase «“otro” lleva nombre» y el pedido a la app de cargar los arqueros convocables · 3. (a) «campeón consagrado» queda fuera · 4. (a) el freno del recibo: FUERA-EN-LA-HOJA (`fuera` y `efeB5`) y EFE-RECOMPUTO-PENDIENTE pasan a rechazo del depósito rehecho, con la salida declarada «once tardío: EFE sin recomputar». Lo demás, como recomienda la propuesta (puntos 1, 2 y 4 aprobados; rúbrica a `rubrica-efe-v1.12.md`; con efe-dashboard v1.15).

**Estado:** PROPUESTA (24/11/2026), para aprobar punto por punto. No se tocó
ningún skill, ni código, ni lección.

**Base.** El skill vigente (`SKILL.md`, `references/rubrica-efe-v1.11.md`,
`references/HISTORIAL.md`; dashboard v1.14). Las líneas citadas son las de
hoy. El estudio del 24/11 (`estudio_lecciones_2026-11-24/README.md`,
`estudio_efe-clasificador.md` y `clasif_efe-clasificador.json`). Releí la
prosa de las **226 lecciones pendientes** (132 partidos, 17-23/11, todas
ciegas PRE) para cada punto. Cada fixtureId que se nombra acá está en esas
lecciones.

**Honestidad con la muestra.** Es **una semana**, la primera entera con la
v1.11, que subió el 17/11 a las 13:20. Las 15 lecciones del 17/11 son de
selecciones y pueden haber corrido con la v1.10. Hay 26 lecciones de copa
nacional (17 de la Taça, 8 de la Copa del Rey y 1 de la Copa de la División
Profesional): sirven para la rúbrica, no para métricas. Dos están en
cuarentena (Deportiva Minera–Cartagena 1644353, por el DT).
Clasificación por la prosa: 138 la regla se sostuvo · 43 mal aplicada ·
19 la regla falló · 18 no dice · 4 insumo · 3 de otro skill · 1 imprevisto.
**Ninguna lección pide mover un número** y esta propuesta no mueve ninguno.
Pesos, máximos, cortes de la tabla, cortes de zona, el ×1,5 de F2c, el umbral
de EJE-DEBUTANTE, el «dos pérdidas seguidas» de C4 y los umbrales de B5
quedan como están. Lo numérico va como «candidato a medir».

---

## 0. Resumen

Lo que más se repite **sigue sin ser una regla que falla: es una regla
escrita que no se cumple al rehacer con el once oficial**. Son 14 mal
aplicadas en 13 partidos: B y F sin recomputar, B5 con titulares de la hoja,
bajas que estaban en la hoja y rehaceres de un solo lado. Ya pasó dos veces
que repetir la regla en el texto no cambió la conducta y que darle el dato a
la corrida sí la cambió (`bancoProbable`: B5 por rol se sostuvo 10 de 11
antes del once). Por eso ese patrón va entero a «Para la app» (§7).

Al skill le quedan cuatro aclaraciones con 3+ partidos y una precisión de
lista. Dos sacan una contradicción del texto: EJE-DEBUTANTE «vía de gol» o
«no es vía de gol», y el ejemplo «si repiten X–Y» que enseña a condicionar
sobre una pareja.

### Lo que ya hizo la app (17-24/11; se referencia, no se pide)

- **21/11 · `EFE-RECOMPUTO-PENDIENTE` ya no se calla con la frase sola**
  (a250c90, incidencias 1467 y 1470). Al depositar se guarda una foto de los
  puntajes A-E de antes del once (`efe_antes_once_json`), y «recomputado con
  el once» calla la alerta solo si los puntajes se movieron contra esa foto.
  Si no se movieron, la alerta sigue con `fraseSinRecomputo`. En el modo
  `rehacer`, sin sub-scores, B se rejuzga a nivel de bloque con la hoja.
- **22/11 · La zona GK se calcula sobre el arquero que ataja hoy** (bc7849e,
  1488). `bloque_f._zona_gk_del_dia` lo hace desde el caso Rizespor 1584466.
  Es la regla v1.9 de la rúbrica (línea 292), ahora calculada, y cierra el
  caso que el estudio pedía «aclarar».
- **21/11 · El banco, la F1 y el arquero sin el partido del homónimo**
  (a350b4c, 1473). Ninguna lección lo muestra todavía, así que no se puede
  juzgar.
- **24/11 · Jev sin crédito**: el escaneo lo avisa y los veredictos sin
  etiqueta se reetiquetan (2cc1c67). La etiqueta del modo de fallo estaba
  caída desde el 21/11 (incidencia 3.1 del estudio); no cambia la
  clasificación, que se hizo por la prosa.

### Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos (partidos) | Recomendación |
|---|---|---|---|---|
| 1 | EJE-DEBUTANTE dice **una sola cosa**: amplía el rango y el volumen concedido. La vía de gol la fija el DTP. Si el rival no ataca la línea, la alerta «no se puso a prueba» | aclaración (saca una contradicción) | 31 lecciones: 19 sostuvo (volumen), 11 no dice, 1 de otro skill | **Aprobar** |
| 2 | Sin once, EJE-DEBUTANTE se condiciona **sobre la línea** («si la línea de fondo no repite 3 de 4»), no sobre una pareja. El ejemplo «si repiten X–Y» se cambia | aclaración del ejemplo | 3 (Progreso, Medellín, Tenerife) | **Aprobar** |
| 3 | F3 de ATK o MID: la cláusula «cubierta, solo confianza en la K» vale también cuando la vía del equipo es la **segunda línea** o el **banco por rol de esa casilla** es ✅ | aclaración de la v1.7/v1.10 | 5 la regla falló + River (6) | **Aprobar** (decisión 1, por Como) |
| 4 | **C4 se escribe con su condición**, como el D3: DT, tamaño de la ventaja, línea o sistema, competición y L/V. Fuera de esa condición amplía el rango y no fija la dirección | aclaración | 4 la regla falló + 3 a favor (7) | **Aprobar** |
| 5 | Arco sin dueño: el escenario «otro» **lleva nombre**, que son todos los arqueros convocables, cada uno con su fila F1 | precisión de una lista (v1.8) | 3 (AVS, Torreense, Marítimo; los tres de la Taça) | **Aprobar** la frase; el arreglo de fondo es de la app (decisión 2) |
| Dash | `efe-dashboard` v1.15: F6 condicional sobre la línea; EJE-DEBUTANTE no es gatillo de gol en «Para perder»; la fila F3 lleva la segunda línea; descripción | alineación | los de 1, 2 y 3 | **Aprobar** |
| N | Núcleo: la rúbrica pasa a `rubrica-efe-v1.12.md`, changelog al historial y tres anclas nuevas | forma, sin regla | — | **Aprobar** |

**Número:** v1.12 (aclaraciones, sin números ni bloques nuevos). El
dashboard pasa a v1.15 porque cambian F6, la matriz y la descripción (§10).

---

## 1. EJE-DEBUTANTE: amplía el rango y el volumen concedido; la vía la fija el DTP · [aclaración]

**Qué dice hoy.** La rúbrica dice las dos cosas en la misma alerta:
- Línea 559 (alta v1.7): «No modifica el IP ni el porcentaje: **amplía el
  rango** y baja al diagnóstico táctico como **vía de gol del rival**».
- Línea 561, al final del mismo bloque (v1.9/v1.10): «No tiene peso ni es
  vía de gol por sí sola: amplía el rango».
- `efe-dashboard`, línea 180: «si FACTOR-X, EJE-DEBUTANTE o
  GOLEADOR-AL-BANCO están activos → ampliar el rango, no mover el centro».
  La matriz «Para perder» (PASO 6) no dice nada de EJE-DEBUTANTE.

**Qué pasó (38 lecciones, 36 partidos; la regla más tocada de la semana).**
- **Volumen sí, la vía nombrada no** (en las que se sostuvo): Atlante 1551038
  (13 remates en el área y 2,43 de xG; la vía aérea bajada al DTP no dio el
  gol, que fue de penal), Racing Santander 1570459 (31 remates y 3,73 de xG;
  los dos goles llegaron por un centro y una segunda jugada, no por la espalda
  nombrada), Rumania 1528999 («confirmación de escenario, no de mecanismo»),
  Angers 1552825 (3,54 de xG, «confirma por volumen, no por jugada»),
  Coquimbo 1505565 y Frankfurt 1575223 (14 remates en el área y valla en
  cero por el arquero). Lorient 1552821: «una línea expuesta a la
  profundidad, no un colapso».
- **No dice: la alerta no se puso a prueba** (11): Ucrania 1528994 («baja la
  confianza en la K, no anuncia concesión»), Santos 1492451, Vélez 1649571
  (ningún gol por la pareja), Cerro 1650503 (uno de la pareja hizo el 1-0),
  Sunderland 1557467 (bloque bajo de plan), Anderlecht 1558680 y Trabzonspor
  1584474 (el rival no atacó la línea), Rosario Central 1649570 (el cero lo
  sostuvo el arquero), AZ 1552230, y Irlanda 1528997 y Manchester United
  1557473, con roja temprana.
- **De otro skill:** Millonarios 1650174. La alerta amplía el rango, pero el
  descarte y la cadena la escribieron como «la zaga rearmada concede», y la
  pareja sostuvo los 90' (0,45 de xG).

Con dos frases contrarias en la misma alerta, cada lección eligió una. La
semana sostiene la segunda. La alerta acierta **la línea** que concede: en
Gales 1528992 Trincão le ganó la espalda a Roberts, en Cagliari 1550200 los
dos goles nacieron por el lado de la línea rearmada, y en Mallorca 1644334 y
Konyaspor 1584473 la zaga nueva concedió. Pero no acierta **cómo**: cuando
bajó al DTP una vía concreta (la aérea en Atlante, la espalda en Racing),
esa vía no dio el gol. Y sin crónica, las lecciones no atribuyen el mecanismo
(Rumania, Angers, Coquimbo).

**Texto propuesto.**

*Rúbrica, línea 559*, cambiar «**amplía el rango** y baja al diagnóstico
táctico como **vía de gol del rival**.» por:

> **amplía el rango y el volumen concedido** y baja al diagnóstico táctico
> como **línea a vigilar**: la vía de gol la fija el DTP con un hecho del
> partido *(v1.12)*.

*Rúbrica, línea 561, al final del párrafo* («No tiene peso ni es vía de gol
por sí sola: amplía el rango.»), agregar:

> *(v1.12)* **Qué anuncia y qué no.** Anuncia **volumen concedido** (remates
> en el área, xG en contra), no el carril ni la jugada del gol: Atlante
> 1551038 (2,43 de xG; el gol, de penal), Racing Santander 1570459 (3,73 de
> xG; los goles, por un centro y una segunda jugada), Angers 1552825. Si el
> rival no ataca la línea (bloque bajo propio, rival que cede la pelota, roja
> temprana), la alerta **no se puso a prueba**: no se confirma ni se refuta
> con el marcador (Anderlecht 1558680, Trabzonspor 1584474, Sunderland
> 1557467). Que el descarte, la cadena o la matriz la escriban como «la zaga
> concede» es leerla como vía (Millonarios 1650174).

**Por qué no más.** El umbral (≤ 1 partido juntos) no se toca, y tampoco que
sea declarativa y sin peso. Hay un candidato de la v1.10 que esta tanda
apoya: Newcastle 1557475 (el DT la corrigió al descanso y pesó hasta el
primer cambio), con Austria 1528996 y Málaga 1570458 como casos parecidos
(rearme al descanso). Son 3 partidos, pero es una regla nueva sobre el tramo
de la alerta, no una aclaración: queda como candidato (§8).

**Lo tumbaría:** 3+ partidos en que la vía de gol salga de la alerta sola,
sin que el DTP la haya fijado con un hecho del once o del rival.

---

## 2. EJE-DEBUTANTE sin once: la condicional va sobre la línea, no sobre una pareja · [aclaración del ejemplo]

**Qué dice hoy.**
- `SKILL.md`, línea 31: «Sin once, EJE-DEBUTANTE va condicional («si
  repiten X–Y»); con el once, se declara o se descarta con el grid. *(v1.10)*
  Con el once, el chequeo va sobre **la línea entera** del grid».
- Rúbrica, línea 561: «**Sin once oficial, EJE-DEBUTANTE va siempre
  condicional** («si repiten X–Y»)».
- `efe-dashboard`, línea 68 (F6): «Sin once oficial va condicional («si
  repiten X–Y»)».

La v1.10 llevó el chequeo **con** el once a la línea entera, pero el ejemplo
de la condicional **sin** once sigue nombrando una pareja. Cuando arranca
otro nombre en la misma línea, la condicional cae aunque la línea sea igual
de nueva.

**Qué pasó (3 partidos).**
- Progreso 1650502 (la regla falló): la condicional era «Carroso–Oliva».
  Oliva fue al banco y la zaga fue G. Silva–Carroso, una pareja igual de
  nueva. La lección propone escribir «si la línea de fondo no repite tres de
  cuatro».
- Medellín 1650175 (insumo, once tardío): la condicional nombraba Didier
  Moreno–Diego Moreno y el grid puso a Perlaza con Didier Moreno.
- Tenerife 1644346 (copa, once tardío): la condicional era Viereck–León y la
  pareja fue León–Jorge Moreno.

Los otros cuatro casos con el once a la vista son **incumplimiento** de la
regla escrita y van a la app (§7.2): NEC 1552229 y Getafe 1570456 dejaron la
alerta condicional con el once publicado; Tottenham 1557476 y Sassuolo
1550206 la descartaron porque no salió la línea condicionada, sin revisar la
que salió, que también era nueva.

**Texto propuesto.**

*`SKILL.md`, línea 31*, cambiar «Sin once, EJE-DEBUTANTE va condicional
(«si repiten X–Y»)» por:

> Sin once, EJE-DEBUTANTE va condicional **sobre la línea**, no sobre una
> pareja («si la línea de fondo no repite 3 de 4», «si el doble pivote no es
> X–Y ni otro con partidos juntos») *(v1.12)*

*Rúbrica, línea 561*, cambiar «(«si repiten X–Y»)» por el mismo paréntesis y
agregar después de «se declara o se descarta con el dato.»:

> *(v1.12)* La condicional se escribe sobre la línea para que no caiga cuando
> cambia el nombre y no el problema (Progreso 1650502: la pareja nombrada no
> repitió y la zaga que salió era igual de nueva; Medellín 1650175; Tenerife
> 1644346). Con el once, la alerta **no se descarta por la línea que no
> salió**: se decide sobre la que salió (Tottenham 1557476, Sassuolo
> 1550206).

**Por qué no más.** Es el mismo chequeo de la v1.10 llevado a la condicional;
no hay umbral nuevo. Que la alerta quede condicional con el once a la vista
ya está prohibido dos veces (v1.9 y v1.10): eso lo arregla el dato
(`parejasNuevas` sobre el once oficial, §7.2), no otra frase.

---

## 3. F3 de ATK o MID cubierta por la segunda línea o por el banco de la casilla · [aclaración de la v1.7 y la v1.10]

**Qué dice hoy.**
- Rúbrica, línea 286 (v1.7): «F3 se lee por la zona que pierde y por la que
  genera […] Si el generador del equipo juega en otra zona, se dice».
- Rúbrica, línea 302 (v1.10): «**La F3 de ATK o de MID anuncia solo si la
  zona está en 🔴 y el recambio no tiene minutos en esa casilla esta
  temporada**. Con un recambio con rodaje, la nota dice «cubierta de oficio»
  y la F3 es solo confianza en la K».
- La tabla de la línea 298 dice qué anuncia ATK en rojo: «Menos peligro
  propio: se ve en el volumen, en dónde se remata o en la conversión».

La v1.10 da por cubierta la zona cuando hay **un** recambio con minutos en la
misma casilla. No dice nada del equipo cuya vía es la segunda línea (el gol
viene del medio) ni del banco por rol de esa casilla con B5 ✅. Ahí la nota
siguió anunciando «menos peligro» y el equipo produjo igual.

**Qué pasó (5 la regla falló, 5 partidos).**
- Corinthians 1492450: sin Garro ni Yuri Alberto, 16 remates, 1,57 de xG y
  4-0. La matriz del rival había escrito «genera poco sin Garro ni Yuri».
- Dortmund 1575226: sin Guirassy, 15 remates, 1,65 de xG y el gol de un
  mediocentro, en un equipo cuya vía declarada es la segunda línea.
- Galatasaray 1584469: sin Osimhen ni Leão, goles de Torreira y Akgün con
  asistencia de Sara.
- Olympiakos 1593362: sin Hezze ni El Kaabi y con B5 ✅, 2,6 de xG y seis
  goles.
- Tottenham 1557476 (MID): el doble pivote heredero, Gallagher–Mateus
  Fernandes, sostuvo el 62 % de la pelota.
- Va en la misma línea River 1649569 (se sostuvo): «los recambios de la hoja
  sostuvieron; F3 baja la confianza en la K, no anuncia que el equipo rinda
  menos».

**A favor de la tabla de hoy (ATK sin cobertura, la producción cayó):**
Bragantino 1492459 (el volumen no cayó y lo pagó la conversión, como dice la
v1.10), Sunderland 1557467, Técnico Universitario 1639838, Union Berlin
1575225, Botafogo 1492450 y Georgia 1528994. **El límite es Como 1550200**:
sin Kean generó 0,62 de xG con el 63 % de la pelota y los goles fueron de un
central y de Da Cunha. La segunda línea marcó, pero el volumen sí cayó. Por
eso la aclaración no anuncia «volumen intacto». Solo saca la dirección y deja
la F3 como confianza en la K, que es lo que dice hoy la cláusula «cubierta».
Bayern 1575221 marca la condición del banco: «el once tipo completo no dice
que la zona esté cubierta». El banco tiene que cubrir **la casilla, pieza por
pieza**.

**Texto propuesto.** *Rúbrica, línea 302, al final del párrafo «La F3 de ATK
o de MID anuncia solo si…»*, agregar:

> *(v1.12)* Vale igual **cuando la vía del equipo es la segunda línea** (el
> generador o el goleador juega en otra zona, v1.7) **o cuando el banco por
> rol de esa casilla es ✅** (B5 nombra quién entra por cada pieza de la vía,
> no «el once tipo»): la nota dice «cubierta por la segunda línea» o
> «cubierta por el banco» y la F3 es solo confianza en la K, sin anunciar
> menos volumen (Corinthians 1492450: 16 remates y 4-0; Dortmund 1575226,
> Galatasaray 1584469: goles del medio; Olympiakos 1593362, B5 ✅;
> Tottenham 1557476, MID con el pivote heredero). Sin anuncio no es «volumen
> intacto»: Como 1550200 cayó a 0,62 de xG con la segunda línea marcando. Y
> sin el banco pieza por pieza no hay cobertura (Bayern 1575221). No vale
> para DEF, cuya fila de la tabla sigue como está.

**Por qué no más.** El 40 % del corte de zona y el rojo no se mueven. La
extensión a DEF **no entra**: Chelsea 1557470 (1 caso) leyó «cubierta de
oficio» en DEF y concedió 2,37 de xG, y el estudio propone decir que la
cláusula no aplica a DEF. Pero la rúbrica la aplica a DEF a propósito desde
la v1.7 (línea 254, Deportivo Cali: DEF −37,5 % con recambio de oficio, 0,62
de xG en contra) y la v1.9 (línea 304, «Toda zona en rojo dice quién la
cubre»). Con un solo caso, que además tenía EJE-DEBUTANTE en esa misma línea
(Acheampong–Chavarría, poca muestra juntos), no se cambia una regla con
casos a favor. Queda anotado: con un eje nuevo en la línea, «cubierta» no
anula la alerta del eje (v1.6, línea 62, ya lo dice para B5).

**Lo tumbaría:** 3+ partidos con la nota «cubierta por la segunda línea o
por el banco» en que la producción caiga como si la zona no estuviera
cubierta. Entonces la cláusula buena es la de la tabla, no esta. Como ya es
un caso (decisión 1).

---

## 4. C4 se escribe con su condición · [aclaración]

**Qué dice hoy.** Rúbrica, línea 99 (v1.7): «Si la asimetría local/visita es
clara, C4 se declara por condición (Mainz). **Dos pérdidas de ventaja
seguidas** pasan C4 de «ocasionales» a patrón (Toluca)». La condición es
solo L/V. El D3, en cambio, se escribe con condición, competición, escala del
rival y cuántos casos lo sostienen (líneas 117-123, v1.7 y v1.9). Con T.54,
el C4 del DT anterior va `sin dato` (línea 514).

**Qué pasó (8 lecciones, 8 partidos).**
- **La regla falló (4):**
  - Mushuc Runa 1639837: C4 ❌ por dos ventajas perdidas de un gol, y sostuvo
    una de dos desde el 65'. «El patrón se midió en ventajas de uno».
  - Bulo Bulo 1645547: C4 ❌ por colapsos bajo Rojas con otra línea y otro
    sistema. Con el bloque de cinco sostuvo 71' tras el 0-1. «C4 no lo
    distingue».
  - Rennes 1552821: C4 ❌ por tres goleadas de visita, y de visita no
    colapsó (un gol de córner y un penal en 92').
  - Tomayapo 1645542: C4 🔶 dejaba las goleadas en la copa y la siguiente
    llegó en liga y de local (1-5, dos de los cinco con diez). **La
    competición no aisló el colapso.**
- **Se sostuvo con el DT de hoy (3):** Feyenoord 1552226 (tercera ventaja
  perdida con este DT, en las dos condiciones), Sparta 1552230 (tercera, con
  Meijer) y Marseille 1552822 (segundo colapso con ventaja amplia de local con
  Genesio, que lo nombra como patrón). Va en el mismo sentido AEK 1593360:
  las cuatro derrotas «explicadas por el rival» se leyeron así y ganó.

Lo que se repite: el patrón se sostiene **con el mismo DT** y no se repite
cuando cambian la línea o el sistema (Bulo Bulo) o el tamaño de la ventaja
(Mushuc). Rennes falló dentro de su condición, y Tomayapo muestra que la
competición no sirve para aislarlo. La aclaración no puede decir «fuera de la
condición no vale», porque Tomayapo la tumba. Lo que dice es que la nota
**escriba** la condición y que, fuera de ella, el C4 amplíe el rango en vez
de fijar la dirección, como el D3.

**Texto propuesto.** *Rúbrica, línea 99, al final del párrafo «C4 por
condición…»*, agregar:

> *(v1.12)* **La nota de C4 dice sobre cuántos casos se apoya y en qué
> condición**: el DT, el tamaño de la ventaja, la línea o el sistema, la
> competición y la condición (L/V), como el D3 (v1.9). Con el DT de hoy el
> patrón se sostuvo (Feyenoord 1552226, Sparta 1552230, Marseille 1552822).
> Si el partido de hoy cambia alguna de esas condiciones (otra línea u otro
> sistema: Bulo Bulo 1645547; una ventaja de otro tamaño: Mushuc Runa
> 1639837), el C4 **amplía el rango y no fija la dirección**. La competición
> sola no aísla el colapso (Tomayapo 1645542: copa en la serie, goleada en
> liga).

**Por qué no más.** No se toca cuántos colapsos hacen ❌. Marseille 1552822
pide «dos colapsos con ventaja de dos o más, de local y con el DT de hoy,
van ❌», y eso es un umbral: **candidato a medir** (§8). Rennes es un fallo
del C4 ❌ por condición, sin aclaración que lo explique: se anota.

**Lo tumbaría:** 3+ partidos en que el patrón se repita con otra línea u
otro sistema, o con una ventaja de otro tamaño. Eso diría que el C4 es del
plantel y no de la condición.

---

## 5. Arco sin dueño: el escenario «otro» lleva nombre · [precisión de una lista]

**Qué dice hoy.** Rúbrica, línea 72 (v1.8): «Con dos o más arqueros
alternándose sin motivo publicado, la caja abre **los tres escenarios**
(titular A, titular B, otro)». `SKILL.md`, línea 28 (v1.10): los candidatos
al puesto de cada baja o duda van a la F1, «el arquero suplente siempre».

**Qué pasó (3 partidos, los tres de la Taça).**
- AVS 1647579 (mal aplicada): la caja abrió Rebollo y Steffens, y atajó un
  tercero, Raul.
- Torreense 1647592 (mal aplicada): la caja abrió Adriel y Lucas Paes, y
  atajó Lisandru Olmeta, que no tenía fila en la tabla.
- Marítimo 1647587 (insumo, once a 6'): B6 leyó un arco entre Vieites y
  Pastor, y atajó un tercero, Tabuaço, que decidió la tanda con dos penales
  atajados.

En los tres, el «otro» de la v1.8 quedó sin nombre y sin fila. Es una
precisión del ítem de la lista, no una regla nueva. Lo que cambia la conducta
es que la F1 y `bancoProbable` traigan a todos los arqueros convocables
(§7.4), como pasó con el banco.

**Texto propuesto.** *Rúbrica, línea 72, después de «(titular A, titular B,
otro)»*, insertar:

> ; *(v1.12)* «otro» se escribe **con nombre**: todos los arqueros
> convocables del plantel, cada uno con su fila F1 (AVS 1647579, Torreense
> 1647592 y Marítimo 1647587, en copa: atajó un tercer arquero que la caja no
> nombraba)

**Por qué no más.**
- Rizespor 1584466 (dos arqueros que se alternan; la ausencia del que no
  ataja redujo la zona GK) **no es texto**: la regla está desde la v1.9
  (línea 292) y la app la calcula desde el 22/11 (bc7849e).
- Guaraní 1632066 (el arquero salió al descanso sin motivo publicado y la
  caja no abrió el arco) es un caso solo y otra situación: no entra.
- Bajar el ×1,5 de F2c o no activar GK-DOWNGRADE con un suplente con rodaje
  sigue como candidato (§8). Esta semana suma casos de «se mide, no anuncia»
  (Fortuna 1552227: 8 atajadas de Koopmans; Monterrey 1551043) y uno en
  contra con reserva (Sparta 1552230: cinco goles con la zona GK «cubierta»,
  sin crónica de error).

---

## 6. Las alertas, con sus conteos (lecciones 17-23/11)

| Alerta o regla | Lecciones (partidos) | Se sostuvo | En contra / otro | Qué hacer |
|---|---:|---:|---|---|
| EJE-DEBUTANTE | 38 (36) | 19 | 11 no dice, 4 mal aplicada, 2 insumo, 1 la regla falló, 1 otro skill | Puntos 1 y 2; el incumplimiento con el once, a la app (§7.2) |
| F3 (con el rol de hoy) | 34 (33) | 21 | 5 la regla falló, 4 mal aplicada, 2 no dice, 2 otro skill | Punto 3. Mal aplicadas: Chelsea 1557470 (DEF, no entra), Standard 1558687 y Barracas 1649566 (bajas de rotación: el punto 6 de la v1.11 ya lo cubre; se repite con menos casos), Independiente del Valle 1639806 (MID sin «eje entero», regla v1.8) |
| Jerarquía de fuentes | 21 (20) | 18 | 3 mal aplicada | Bajó de 4/14 a 3/21. Cada caso toca una regla escrita distinta: Bucaramanga 1650173 (previas copiadas, nivel C), Atlético Nacional 1650176 (baja contradicha va Duda), Vila Nova 1650247 (baja de la hoja sin motivo). **Nada** |
| B6, arquero y zona GK | 19 (18) | 12 | 4 mal aplicada, 1 insumo, 1 no dice, 1 imprevisto | Punto 5. «El ×1,5 mide la ausencia, no es vía» (v1.11) se sostiene: Polonia 1528998, Coritiba 1492451, Fortuna 1552227, Monterrey 1551043. Orense 1639837 (el titular fijo dejó vivo un rebote) es el primer caso hacia GK-FALLA-ACTIVA de un titular: se anota |
| Rama «once alternativo» | 17 (15) | 13 | 4 mal aplicada | Se sostiene cuando se escribe (Badajoz, Sabadell, Real Unión, Manchester City 1557474, Torreense 1647592…). Las 4 mal aplicadas no entran (§9) |
| Rehacer con el once | 15 (14) | — | 14 mal aplicada, 1 no dice | **Para la app** (§7.1) |
| B5 por rol, antes del once | 11 (11) | 10 | 1 la regla falló (Le Mans 1552822: A8) | `bancoProbable` funciona; nada |
| D3 | 9 (7) | 7 | 2 la regla falló | Barcelona 1570455 y Necaxa 1551046 no entran (§9) |
| C4 | 8 (8) | 4 | 4 la regla falló | Punto 4 |
| T.54 | 8 (8) | 5 | 2 mal aplicada, 1 no dice | Vitória 1492459 heredó C4 y D3 del DT anterior (regla escrita, línea 514); Rubio Ñu 1632067 dejó vacío el `dt.desde` de la base (regla escrita, `SKILL.md` línea 26). Nada |
| Bloque H | 6 (6) | 1 | 4 mal aplicada, 1 la regla falló | **Para la app** (§7.3) |
| COLAPSO EN CASCADA | 6 (6) | 4 | 2 la regla falló | Angers 1552825 es el **quinto caso** de COLAPSO + AGRAVANTE; AVS 1647579 (copa), goleada sin la alerta, suma para D3-DEGRADADO. Los dos siguen candidatos (§8) |
| Caja de sensibilidad | 6 (6) | 4 | 1 la regla falló, 1 insumo | Chivas 1551045 (el reconvertido que sostiene el dibujo) y ADO 1552225 (la pieza de la vía sin baja anunciada): uno cada uno, no entran |
| T.54 de ≤ 2 partidos (D1 y H condicionados) | 5 (5) | 5 | — | Se sostiene |
| EFE-EMPATE-TECNICO y brecha | 3 (3) | — | Leeds 1557470, contraejemplo | Casi desapareció como regla tocada (27 la semana pasada). La prueba sigue siendo A6 (§8) |

---

## 7. Para la app (no entra al skill)

Revisado con grep en `backend/` el 24/11. Va en orden de casos. El 1 es la
decisión 2 del estudio (README §5); acá se baja al EFE.

1. **Que el recibo del rehacer frene el depósito del EFE** (14 mal aplicadas,
   13 partidos). FUERA-EN-LA-HOJA y EFE-RECOMPUTO-PENDIENTE son `tipo: dato` y
   el depósito entró igual: Schalke 1575228 y Aucas 1639807 tenían
   FUERA-EN-LA-HOJA sonando. Los motivos que se repiten son «sin tiempo para
   re-juzgar» (Bosnia 1528999, Bolívar 1645545) y «solo se rehízo el DTP»
   (Schalke 1575228, Olimpia 1632065). Tres frenos:
   - **B5 nombra a un titular de la hoja.** Hoy `alertas_fuera_en_la_hoja`
     (`parte.py`, ~línea 2120) lee como `caso: dtpBanco` los `viasGol` y
     `veredictoRamas` del DTP y las notas del TDE, pero **no la nota B5 del
     EFE**. Falta un `caso: efeB5` con la misma rutina de identidad. Casos:
     Ameliano 1632063, Recoleta 1632066, Alavés 1570453 (Denis Suárez,
     titular, hizo el 3-1), Schalke 1575228 (cuatro titulares) y Hull 1557472.
   - **`fuera` lleva a alguien de la hoja** (`caso: fuera`, ya calculado):
     que pase de aviso a rechazo en el depósito rehecho. Casos: Aucas
     1639807 (dos del banco quedaron en `fuera` y B bajó por un TH que no
     faltaba) y Bolívar 1645545 (Matheus salió de `fuera`, pero B, D y la caja
     quedaron escritos con él afuera).
   - **EFE-RECOMPUTO-PENDIENTE sonando en algún lado**: desde el 21/11 la foto
     `efe_antes_once_json` ya distingue la frase sola del recómputo. Que el
     rehacer no se acepte con la alerta viva en un lado. Casos: Olimpia
     1632065 (solo se rehízo el rival), Suecia 1528998, Roma 1550205,
     Feyenoord 1552226 (once a 27'), Stuttgart 1575228 y Arouca 1647586
     (copa).

   **Lo tumbaría:** que con el freno puesto aparezca el patrón contrario
   (partes que no se depositan antes del pitazo). Entonces el freno va con
   una salida declarada («once tardío: EFE sin recomputar»), no con un
   depósito callado.
2. **`parejasNuevas` sobre el once oficial** (EJE-DEBUTANTE, 4 partidos con
   el once a la vista: NEC 1552229, Getafe 1570456, Tottenham 1557476,
   Sassuolo 1550206). Hoy `dtp_cowork.py` (línea 465) calcula
   `_parejas_nuevas` sobre el XI del partido anterior, no sobre la hoja de
   hoy. Es el `EJE-DEBUTANTE-SIN-DECLARAR` / `-SIN-OBJETO` aprobado el
   10/11, que sigue sin hacerse: que avise la línea nueva del grid que el
   parte no declaró, la alerta que quedó condicional con la hoja y la
   descartada por una línea que no salió.
3. **H contra el grid** (bloque H, 4 partidos: Nacional 1650503, Lecce
   1550202, Betis 1570462, Arouca 1647586). La regla está («manda el último
   grid», paso 6 del rehacer). Falta un aviso cuando el sistema que nombra el
   H no es el del grid capturado, o cuando hay D1 🔶 con variante nombrada y
   el H viene en una sola. Si no entra solo, va con el freno del 7.1.
4. **Los arqueros convocables en la F1 y en `bancoProbable`** cuando ningún
   arquero tiene la titularidad fija en la competición (punto 5: AVS 1647579,
   Torreense 1647592, Marítimo 1647587). Es la misma lección del banco: la
   lista la da la app.
5. **`onceTardio`** (aprobado el 10/11, sin hacer): Medellín 1650175,
   Marítimo 1647587, Querétaro 1551046, Progreso 1650502 y Tenerife 1644346
   siguen escribiéndolo a mano.
6. **A6, A7 y A8** siguen sin hacerse (§8).

---

## 8. Candidatos a medir (ninguno se aprueba con esta propuesta)

| Candidato | Casos | Qué haría falta |
|---|---|---|
| C4 ❌ con dos colapsos con ventaja de 2+ y el mismo DT | Marseille 1552822 (más Toluca, de la v1.7) | Sobre todos los partes con C4: cuántos colapsos y de qué tamaño de ventaja separan a los que vuelven a colapsar, por DT |
| COLAPSO + AGRAVANTE como regla | **5.º caso**: Angers 1552825 (D3 ❌ y bloque improvisado, se rompió tras el triple cambio) | El denominador: cuántos D3 ❌ con F3 DEF, R-KT.2 de visita o bloque improvisado **no** se rompieron (A7) |
| D3-DEGRADADO (D3 🔶 de < 8 partidos leído como ❌) | AVS 1647579 (copa), más los anteriores | A7 |
| Umbral del B5 🔶 por un partido de banco decisivo | 3.º caso: Le Mans 1552822 (más Albion, 2) | A8, sobre `bancoProbable` |
| EJE-DEBUTANTE pesa hasta el primer cambio del DT | Newcastle 1557475, Austria 1528996, Málaga 1570458 | La concesión por tramo antes y después del rearme, sobre los partes con la alerta |
| ×1,5 de F2c y GK-DOWNGRADE con suplente con rodaje | A favor de «se mide, no anuncia»: Fortuna 1552227, Monterrey 1551043; en contra, con reserva: Sparta 1552230 | Gol concedido por error del arquero, con y sin el ×1,5 |
| EFE-EMPATE-TECNICO: tasa del de mayor porcentaje con y sin la alerta | Leeds 1557470 (ganó el de mayor EFE con la alerta sonando) | A6 (`backend/medir_brecha_efe.py` existe desde el 17/11; falta correrlo y traer el resultado a la revisión) |

---

## 9. Lo que no entra (1 o 2 casos, o regla ya escrita)

- **«Campeón consagrado» como hecho que abre la rama**: Liverpool Montevideo
  1650504 (la rama quedó «sin hecho» y perdió con siete cambios). El otro
  caso de la semana va en contra de la dirección: Independiente del Valle
  1639806, campeón con la final de copa por delante, abrió la rama y nadie
  rotó. Son 2 partidos, y «sin nada en juego» (línea 336, v1.10/v1.11) ya
  cubre al campeón: es incumplimiento, no falta de texto. Decisión 3.
- **«Prevé» en una previa no es un hecho**: Real Potosí 1645545, 1 caso. La
  v1.10 ya dice «nunca por sospecha».
- **Rama corta o sin abrir en copa**: Tondela 1647579 (sin el arco ni los
  rotables de todas las líneas) y Casa Pia 1647580 (contra un Liga 3, sin
  rama). Reglas v1.9 y v1.10 escritas: incumplimiento.
- **«Cubierta de oficio» no aplica a DEF**: Chelsea 1557470, 1 caso,
  contradice las líneas 254 y 304 (punto 3).
- **D3 🔶 con un solo caso de la condición**: Barcelona 1570455 pide leerlo
  «sin dato con caja» y Cobresal 1505563 lo sostuvo con n = 1. Se
  contradicen y quedan en observación. Además, la v1.9 ya obliga a escribir
  «(1 caso)».
- **D3 ❌ con serie corta y T.54 como hecho que cierra el partido**: Necaxa
  1551046. La nota v1.10 ya lo dice y pasarlo a 🔶 espera A7.
- **G-BLOQUE confirmada solo con el once**: Köln 1575221, 1 caso.
- **H por calidad individual**: Recoleta 1632066, 1 caso.
- **DT interino de una sola fuente** (Beveren 1558681) y **A3 sin dato con
  el anuncio del DT disponible** (Fortuna 1552227): uno cada uno; los cubren
  las reglas de contradicciones y de fuentes.
- **T.54 «sin automatismos» escrito como vía del rival**: Chaves 1647587, 1
  caso de copa. Es la misma lectura que el punto 1 corrige para
  EJE-DEBUTANTE, pero sobre otra alerta.
- **F1 con 2 nombres de una previa sin plantilla en la base**: Barakaldo
  1644373, copa. El protocolo XI-REFERENCIA ya lo cubre.
- **La duda física que juega y sale temprano** (Hamburgo 1575227) y **la
  pieza de la vía que falta sin aviso** (ADO 1552225): uno cada uno.
- **De otro skill**: Maldonado 1650500 y Ameliano 1632063 (la espina y el
  pronóstico ignoraron la F3) van a sad-analysis, que queda fuera de esta
  ronda (README del estudio). Millonarios 1650174 (punto 1) también.

---

## 10. `efe-dashboard` v1.14 → v1.15: sí hace falta alinearlo

Como en la v1.14, el dashboard repite textos del clasificador que esta
versión cambia. Sin alinearlo, la matriz y la caja F6 contradicen la v1.12.

- **Dash-1. F6 condicional sobre la línea** (PASO 1, línea 68): «Sin once
  oficial va condicional («si repiten X–Y»)» pasa a «Sin once oficial va
  condicional sobre la línea («si la línea de fondo no repite 3 de 4»), no
  sobre una pareja *(v1.15; clasificador v1.12, punto 2)*».
- **Dash-2. EJE-DEBUTANTE no es gatillo de gol en «Para perder»** (PASO 6,
  después del párrafo del arco, línea 202):
  > *(v1.15)* **EJE-DEBUTANTE tampoco es gatillo de gol en «Para perder»**:
  > anuncia volumen concedido y va a la caja como rango; la vía la nombra la
  > matriz solo si el DTP la fijó con un hecho del partido (clasificador
  > v1.12, punto 1; Atlante 1551038, Racing Santander 1570459, Millonarios
  > 1650174).
- **Dash-3. La fila F3 de la tabla de alertas** (línea 163): después de
  «y quién la cubre *(v1.13)*», agregar «; en ATK o MID, «cubierta por la
  segunda línea» o «por el banco» la deja como confianza en la K *(v1.15)*».
- **Dash-4. Descripción y encabezado:** «EFE v1.12 (skill v1.15)» y
  «alineada con el clasificador EFE v1.12».

Son unos 150 tokens. El núcleo del dashboard pesa hoy unos 5.560 de un tope
de 6.119: entra.

---

## 11. Núcleo (se aplica con esta versión)

- **Rúbrica:** pasa a `references/rubrica-efe-v1.12.md`, con el `git mv`
  para que el historial siga al archivo. Hay que cambiar las menciones en
  `SKILL.md` (líneas 6, 8, 14 y 58), `references/HISTORIAL.md` (línea 5) y
  `docs/skills/README.md`.
- **`references/HISTORIAL.md`:** el changelog v1.12 arriba del de la v1.11,
  con las mediciones del §6 y los candidatos del §8, y la nota v1.15 en el
  historial del dashboard. Ninguna regla vive solo en el changelog: los
  puntos 1-5 van al cuerpo.
- **`scripts/nucleo_reglas.json`:** anclas nuevas para `efe-clasificador`:
  «la vía de gol la fija el DTP», «condicional **sobre la línea**» (o el
  literal elegido) y «La nota de C4 dice sobre cuántos casos se apoya». Para
  `efe-dashboard`: «EJE-DEBUTANTE tampoco es gatillo de gol». Las anclas de
  la v1.11 siguen.
- **Tope de tokens:** el núcleo del clasificador pesa hoy unos 23.380 de
  25.717. Los puntos 1-5 suman unos 900: entra sin tocar el tope.
- **`backend/test_nucleo_skills.py`** tiene que pasar con las anclas nuevas.

---

## 12. Coherencia con TDE v0.1.28 y DTP v1.10 (en paralelo)

- **EJE-DEBUTANTE y la vía (punto 1).** El EFE dice «línea a vigilar,
  volumen concedido» y el DTP fija la vía con un hecho del partido. Si la
  DTP v1.10 dice algo de la línea nueva como vía, que cite esta regla y pida
  el hecho (el carril atacado, el centro, el rival que la ataca).
- **F3 cubierta (punto 3) y el TDE.** El TDE hereda F4 y las alertas del
  EFE. Una F3 «cubierta por la segunda línea» no da una rama «genera poco»
  en el TDE ni en la matriz (Corinthians 1492450: la matriz del rival
  escribió «goleada baja: genera poco»).
- **El freno del recibo (§7.1)** es el mismo que el estudio pide para el
  veredicto con condición del DTP. Si se hace, que sea uno para los dos.

---

## 13. Decisiones del usuario

1. **Punto 3 con el límite de Como.** ¿Entra la extensión de «cubierta» a la
   segunda línea y al banco de la casilla, que solo saca la dirección y deja
   la F3 como confianza en la K, **(a)** recomendado? ¿O queda como candidato
   hasta otra tanda, **(b)**? Son 5 la regla falló y River a favor, Como en
   contra del «volumen intacto» que esta redacción no promete.
2. **Punto 5, el arco sin dueño.** ¿Entran la frase «“otro” lleva nombre» y
   el pedido a la app de cargar los arqueros convocables (§7.4), **(a)**
   recomendado? ¿O solo la app, **(b)**? Los tres casos son de la Taça; la
   regla v1.8 ya abre «otro».
3. **«Campeón consagrado».** ¿Queda fuera, porque «sin nada en juego» ya lo
   cubre y son 2 partidos (uno en contra de la dirección), **(a)**
   recomendado? ¿O entra como hecho de la lista con 2 casos, **(b)**? La (b)
   rompe la regla de los 3 partidos.
4. **El freno del recibo (§7.1).** ¿Pasan FUERA-EN-LA-HOJA (`fuera` y el
   nuevo `efeB5`) y EFE-RECOMPUTO-PENDIENTE de aviso a rechazo del depósito
   rehecho del EFE, con la salida declarada «once tardío: EFE sin
   recomputar», **(a)** recomendado? ¿O siguen como aviso una semana más,
   **(b)**? Es la decisión 2 del README del estudio.

Lo demás, como recomienda cada punto.

---

## 14. Cómo se aplica si se aprueba

1. Los puntos 1-5 sobre la rúbrica y el `SKILL.md`, ya renombrados a v1.12
   (§11). Después el changelog en el historial, el dashboard v1.15 (§10), las
   anclas y `test_nucleo_skills`.
2. `CORTE_VERSION` (`backend/analisis/lecciones.py`, línea 1596: agregar
   `("v1.12", fecha)`) y `SUBIDA_VERSION` (`backend/analisis/simulacion.py`,
   junto a la línea 133) con la hora de la subida. Las lecciones tocadas
   pasan a `aplicada` o `descartada`.
3. Lo de §7 por la cola del mantenimiento, cada uno con su test
   (`test_cowork`), fuera de la subida del skill.
4. **Se reabre** si en la próxima tanda pasa alguna de estas cosas:
   - siguen las notas B sin recomputar con el freno puesto, y entonces es la
     rutina y no el texto;
   - la vía de gol sale de EJE-DEBUTANTE sola en 3+ partidos (punto 1);
   - la F3 «cubierta» cae como si no lo estuviera en 3+ partidos (punto 3);
   - A6 o A7 dan resultados.
