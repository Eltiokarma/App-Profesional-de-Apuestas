# efe-clasificador v1.11: lecciones pendientes del 17 al 23/11/2026

Son 226 lecciones de 132 partidos, todas ciegas PRE. Hay 26 de copa nacional: 17 de la Taça de Portugal, 8 de la Copa del Rey y 1 de la Copa de la División Profesional. Dos están en cuarentena por un DT distinto en el parte (Deportiva Minera–Cartagena 1644353, de copa).
Por fecha: 17/11 15 · 18/11 16 · 19/11 14 · 20/11 28 · 21/11 71 · 22/11 79 · 23/11 3.
Clasificación: `clasif_efe-clasificador.json`, en el mismo orden que la entrada. Clasifiqué por la prosa, no por el veredicto ni por `modoFallo`.

## Conteo

| clase | total | sin copa | copa |
|---|---|---|---|
| regla_sostuvo | 138 | 122 | 16 |
| mal_aplicada | 43 | 35 | 8 |
| regla_fallo | 19 | 18 | 1 |
| no_dice | 18 | 18 | 0 |
| insumo | 4 | 3 | 1 |
| otro_skill | 3 | 3 | 0 |
| imprevisto | 1 | 1 | 0 |

Veredicto del lado: 122 acierto, 80 fallo y 24 parcial.
De los 80 fallos, 41 son regla_sostuvo: el lado falló y la regla se cumplió.
De las 43 mal_aplicada, 14 vinieron en lados con acierto.
Criterio para EJE-DEBUTANTE: cuando la alerta «no se materializó» o no se puso a prueba (roja temprana, rival que no ataca), la cuento `no_dice`, igual que el 17/11. Son 11.

## Tabla por regla

| regla (normalizada) | n | partidos | sostuvo | mal_apl. | fallo | no_dice | insumo | otro/impr. |
|---|---|---|---|---|---|---|---|---|
| EJE-DEBUTANTE | 38 | 36 | 19 | 4 | 1 | 11 | 2 | 1 otro |
| F3 (incluye rol de hoy y F3 contra F4) | 34 | 33 | 21 | 4 | 5 | 2 | – | 2 otro |
| Jerarquía de fuentes de bajas y contradicciones | 21 | 20 | 18 | 3 | – | – | – | – |
| B6 / arquero / zona GK | 19 | 18 | 12 | 4 | – | 1 | 1 | 1 impr. |
| Rama «once alternativo» | 17 | 15 | 13 | 4 | – | – | – | – |
| **Rehacer con el once** (B/F sin recomputar, B5 con titulares, bajas de la hoja o un solo lado) | 15 | 14 | – | 14 | – | 1 | – | – |
| B5 (banco por rol, antes del once) | 11 | 11 | 10 | – | 1 | – | – | – |
| D3 | 9 | 7 | 7 | – | 2 | – | – | – |
| C4 | 8 | 8 | 4 | – | 4 | – | – | – |
| T.54 (heredado, fecha del DT, tribuna) | 8 | 8 | 5 | 2 | – | 1 | – | – |
| Bloque H (último grid, dos variantes, rehacer) | 6 | 6 | 1 | 4 | 1 | – | – | – |
| COLAPSO EN CASCADA | 6 | 6 | 4 | – | 2 | – | – | – |
| Caja de sensibilidad (reemplazo, duda física, pieza de la vía, D1) | 6 | 6 | 4 | – | 1 | – | 1 | – |
| T.54 de ≤ 2 partidos (D1/H condicionados) | 5 | 5 | 5 | – | – | – | – | – |

## Patrones con 3 o más partidos distintos

**1. El rehacer con el once queda a medias: B, F, B5 y las bajas siguen escritos sobre el once viejo.**
Son 14 mal_aplicada en 13 partidos. Es incumplimiento: la regla de v1.10/v1.11 lo manda en orden fijo.
- *B y F sin recomputar o condicionado no levantado:* Suecia 1528998, Bosnia 1528999 (rehizo B y no F, D1 ni H), Roma 1550205, Feyenoord 1552226 (once a 27', nota B sin «recomputado»), Stuttgart 1575228 y Arouca 1647586 (copa).
- *B5 con titulares de la hoja:* Ameliano 1632063, Recoleta 1632066, Alavés 1570453 (Denis Suárez, titular, hizo el 3-1), Schalke 1575228 (cuatro titulares en el banco; FUERA-EN-LA-HOJA sonaba) y Hull 1557472.
- *Bajas de la hoja y rehacer de un solo lado:* Olimpia 1632065 (solo se rehízo el rival), Aucas 1639807 (dos del banco quedaron en `fuera`; B bajó por un TH fuera que no lo era) y Bolívar 1645545 (Matheus sale de «fuera», pero B, D y la caja siguen con él afuera).
- *Motivo que se repite:* «sin tiempo para re-juzgar» (Bosnia, Bolívar, Ajax) o «solo se rehízo el DTP» (Schalke, Olimpia).
- **Para la app**, no para el texto (la regla ya está escrita dos veces). FUERA-EN-LA-HOJA y EFE-RECOMPUTO-PENDIENTE son avisos `tipo: dato` y el depósito entró igual. Que el recibo rechace el rehacer del EFE en tres casos:
  - B5 nombra a un titular de la hoja;
  - `fuera` lleva a alguien que está en la hoja;
  - con la alerta sonando, la nota B no dice «recomputado con el once» o falta un lado.

**2. EJE-DEBUTANTE con el once: se deja condicional o se descarta por la línea que no salió (4 mal_aplicada, 4 partidos).**
Casos: NEC 1552229 y Getafe 1570456 (once a la vista y alerta condicional; la línea concedió 4 y 4,16 de xG), Tottenham 1557476 y Sassuolo 1550206 (descartada porque no salió la línea condicionada; la que salió también era nueva, y en Sassuolo el 0-2 nació de un pase errado de Fali Candé).
- Es el «pendiente de la app» que la rúbrica ya nombra: correr `parejasNuevas` sobre el once oficial y avisar. **Para la app.**
- Va junto a la condicional escrita sobre una pareja y no sobre la línea: Progreso 1650502 (regla_fallo), Medellín 1650175 y Querétaro 1551046 (once tardío). **Aclarar en el skill**: sin once, la condicional se escribe sobre la línea («si la línea de fondo no repite 3 de 4»).

**3. EJE-DEBUTANTE: volumen sí, la vía nombrada no (patrón de lectura, no de falla).**
- *Volumen sin la vía escrita* (19 sostuvo): Atlante 1551038, Racing Santander 1570459, AZ 1552230, Rumania 1528999, Angers 1552825 y Coquimbo 1505565. La zaga nueva concede volumen, pero el gol llega por otra vía (centro, segunda jugada, penal).
- *No materializada*: 11 `no_dice`, entre ellas Ucrania 1528994, Santos 1492451, Vélez 1649571, Cerro 1650503 (uno de la pareja hizo el gol), Sunderland 1557467, Anderlecht 1558680 y Trabzonspor 1584474. En casi todas, el rival no atacó la línea.
- **Aclarar en el skill**: la rúbrica se contradice en el mismo párrafo. Dice «baja al diagnóstico táctico como vía de gol del rival» y, más abajo, «no es vía de gol por sí sola: amplía el rango». Hay que dejar una sola frase: «amplía el rango y el volumen concedido; la vía la fija el DTP».
- Millonarios 1650174 es otro_skill: el descarte y la cadena la escribieron como «la zaga rearmada concede».

**4. F3 por ataque (o medio) en rojo con la segunda línea o el banco enteros: la producción no cayó (5 regla_fallo, 5 partidos).**
Casos: Corinthians 1492450 (sin Garro ni Yuri Alberto, 16 remates y 4-0), Dortmund 1575226 (sin Guirassy, 1,65 de xG y gol de un mediocentro), Galatasaray 1584469 (sin Osimhen ni Leão, goles de Torreira y Akgün), Olympiakos 1593362 (2,6 de xG con B5 ✅) y Tottenham 1557476 (MID: el pivote heredero sostuvo).
- A favor de la regla v1.10 (ATK se paga en volumen o conversión): Bragantino 1492459, Como 1550200, Sunderland 1557467, Técnico Universitario 1639838, Union 1575225, Botafogo 1492450 y Georgia 1528994.
- **Aclarar en el skill**: la cláusula «cubierta de oficio, solo confianza en la K» vale también cuando la vía del equipo es la segunda línea o el banco por rol es ✅, no solo con un recambio en la misma casilla.
- No va número.

**5. F3 mal leída (4 mal_aplicada, 4 partidos).**
- Chelsea 1557470 usó «cubierta de oficio» en DEF. Esa cláusula es de ATK/MID; la línea concedió 2,37 de xG.
- Standard 1558687 contó bajas de rotación.
- Barracas 1649566 tomó como F3 la rotación de un plantel profundo, que va a F4.
- Independiente del Valle 1639806 dejó el MID en rojo sin decir «eje entero».
- La v1.11 (punto 6, rol de hoy) ya cubre Standard y Barracas: **se repite**, pero con menos casos.
- Para Chelsea, **aclarar en el skill**: «cubierta de oficio» no aplica a DEF.
- Aparte, dos otro_skill: la espina o el pronóstico ignoraron la F3 (Maldonado 1650500, Ameliano 1632063). Van a sad-analysis.

**6. C4 ❌ / 🔶 por colapsos o ventajas perdidas: no se repite cuando cambia la condición (4 regla_fallo, 4 partidos).**
- Casos: Tomayapo 1645542 (la goleada llegó en liga, no en copa), Rennes 1552821 (C4 ❌ de visita y no colapsó), Mushuc Runa 1639837 (patrón con ventajas de 1; sostuvo una de 2) y Bulo Bulo 1645547 (los colapsos fueron con otra línea y otro sistema).
- A favor: Feyenoord 1552226, Sparta 1552230 y Marseille 1552822 (segundo colapso con el mismo DT: pasa a ❌), y AEK 1593360.
- **Aclarar en el skill**: la nota de C4 dice en qué condición se dio el patrón (tamaño de la ventaja, sistema, competición, condición) y no se lee fuera de ella. Es la misma lógica del D3 por condición.
- Si se quisiera fijar «cuántos colapsos hacen ❌», es **candidato a medir**.

**7. Bloque H no releído con el grid o en una sola variante (4 mal_aplicada, 4 partidos).**
Casos: Nacional 1650503 (D1 🔶 del rival con la variante 4-4-2 nombrada y el H en una sola), Lecce 1550202 (H sobre una línea de cinco y salió de cuatro), Betis 1570462 (H sobre el 4-3-3 anunciado; el último grid era 4-2-3-1) y Arouca 1647586 (copa: H FAVORABLE sobre el once que la caja daba por rotable).
- La regla está (paso 6 del rehacer, «manda el último grid»): es incumplimiento.
- **Para la app**: el recibo del rehacer lista D1 y H como pasos y avisa si el sistema que nombra H no es el del grid. Si no, va al patrón 1.

**8. Arco alternado o sin dueño: la caja no nombra a todos los arqueros (4 mal_aplicada y 1 insumo, 5 partidos; 3 de copa).**
- Casos: AVS 1647579 y Torreense 1647592 (atajó un tercer arquero sin fila), Rizespor 1584466 (dos arqueros que se alternan: la ausencia del que no ataja no reduce la zona GK) y Guaraní 1632066 (B6 sin dato y la caja no abrió el arco). Marítimo 1647587 es once tardío.
- La regla del arco sin dueño ya está (v1.8: «abre sus escenarios»; F1: «el arquero suplente siempre»).
- **Para la app**: `bancoProbable` y la F1 llevan a todos los arqueros convocables cuando ninguno tiene la titularidad fija.
- **Aclarar en el skill** la zona GK con arqueros que se alternan (Rizespor).

**9. Rama «once alternativo»: se sostiene cuando se escribe (13 de 17) y falla al abrirla (4 mal_aplicada, 4 partidos).**
- Casos: Liverpool Montevideo 1650504 (campeón consagrado y la rama quedó «sin hecho»; perdió 0-2 con 7 cambios), Casa Pia 1647580 (copa contra un Liga 3 sin rama), Tondela 1647579 (sin el arco ni los rotables de todas las líneas) y Real Potosí 1645545 (al revés: se abrió por una previa que decía «prevé», contra otra que decía «duda», y jugó el once de la final).
- Se sostuvo en Badajoz, Tenerife, Sabadell, Real Unión, Progreso, IDV (nadie rotó y el condicionado se levantó), América, Boston River, Anderlecht, Torreense y City.
- **Aclarar en el skill**: «campeón consagrado» entra en la lista de hechos junto a clasificado o eliminado. Una previa con «prevé» no es un hecho.

**10. Jerarquía de fuentes: se sostiene (18 de 21).**
Hay 3 mal_aplicada:
- Bucaramanga 1650173: dos previas que convergen eran copia y siguen siendo nivel C.
- Atlético Nacional 1650176: baja sin motivo, contradicha por otra fuente, cargada ❌.
- Vila Nova 1650247: baja de la hoja sin buscar el motivo en la prensa local.

**Nada: se sostiene.** Bajó frente al 17/11 (4 de 14).

**11. Lo que se sostiene sin discusión.**
- B6 sobre el arquero de la hoja y «el ×1,5 mide la ausencia, no es vía»: 12 sostuvo, entre ellos Polonia 1528998, Coritiba 1492451, Gladbach 1575226, Kortrijk 1558685, Fortuna 1552227, Bulo Bulo 1645547 y Monterrey 1551043.
- B5 por rol antes del once: 10 de 11.
- T.54 de ≤ 2 partidos con D1 y H en dos variantes: 5 de 5.
- Jerarquía de fuentes, D3 por condición (7 de 9) y COLAPSO como «no recupera» (4 de 6).
- **Nada.**

## Casos con 1 o 2 partidos (no entran)

- D3 🔶 con un solo caso de la condición: Barcelona 1570455 pide leerlo «sin dato con caja» y Cobresal 1505563 lo sostuvo con n = 1. Se contradicen; queda en observación.
- D3 ❌ con serie corta y T.54 tomado como hecho que cierra el partido: Necaxa 1551046.
- T.54 que hereda C4 y D3 del DT anterior (Vitória 1492459); `dt.desde` de la base dejado en blanco (Rubio Ñu 1632067).
- DT interino tomado de una sola fuente (Beveren 1558681); A3 sin dato con el anuncio del DT disponible (Fortuna 1552227).
- G-BLOQUE confirmada solo con el once (Köln 1575221).
- H por calidad individual que no anticipó el volumen del local (Recoleta 1632066).
- COLAPSO que se rompió: Angers 1552825 (D3 ❌ con bloque improvisado). Es el **quinto caso del candidato COLAPSO + AGRAVANTE: candidato a medir (A7)**. AVS 1647579, de copa, tuvo una goleada sin la alerta: es un caso para D3-DEGRADADO.
- B5 🔶 con un solo suplente de impacto y banco decisivo: Le Mans 1552822. Con Albion son 3 casos: **candidato a medir (A8)**.
- Error del arquero titular fijo (Orense 1639837): imprevisto. Es el primer caso hacia GK-FALLA-ACTIVA.
- Una pieza de la vía que falta sin aviso (ADO 1552225, Hawkins): insumo.
- La duda física que juega y sale temprano (Hamburgo 1575227).
- La baja del reconvertido que sostiene el dibujo (Chivas 1551045).
- T.54 «sin automatismos» escrito como vía del rival (Chaves 1647587, copa).
- F1 armada con 2 nombres de una previa sin plantilla en la base (Barakaldo 1644373, copa). El protocolo XI-REFERENCIA ya lo cubre.
- EFE-EMPATE-TECNICO: Leeds 1557470 ganó por lo que decía la brecha. Es un contraejemplo y va a A6.

## Comparación con el 17/11

| patrón del 17/11 | esta semana |
|---|---|
| 1. F1 sin fila con el once (19 lecciones, 15 partidos) | **Bajó**: titulares sin fila solo en Barakaldo (copa), Ameliano (suplentes) e IDV (B5). El incumplimiento **se movió** al resto del rehacer (patrón 1: 14 en 13 partidos). |
| 2. El arquero suplente no fue vía | **Se repite y ahora se sostiene**: la v1.11 lo escribió y 12 lecciones lo confirman. Contrapeso: Orense (error del titular) y Levadiakos 1593361 (error de Eliasi, con la vía bien en el DTP). |
| 3. Rama «once alternativo» falta o es corta | **Bajó**: de 6 a 4. Aparece el error inverso, abrirla por una previa (Real Potosí). |
| 4. F3 contraejemplos de magnitud | **Se repite** (5 regla_fallo), ahora concentrado en ATK con la segunda línea entera. Leer F3 junto con H (Andorra, Eslovenia) no reapareció. |
| 5. B5 en copa | **Desapareció**: Estoril y Sporting en la Taça se sostuvieron. |
| 6. Jerarquía de fuentes | **Bajó**: de 4/14 a 3/21. |
| 7. Once tardío | **Se repite, menos**: 3 insumo (Medellín, Marítimo, Querétaro) y menciones en Tenerife, Progreso, Cercle y Ajax. |
| EFE-EMPATE-TECNICO (27 lecciones) | **Casi desapareció** como regla tocada: 2 lecciones más 1 de brecha en la misma base. La medición A6 sigue siendo la prueba. |
| EJE-DEBUTANTE | Se repite: es la regla más tocada (38). Lo nuevo es el incumplimiento con el once (patrón 2) y la contradicción del texto (patrón 3). |

## Juicio sobre los arreglos de la app del 17/11 y del 21/11

- **`bancoProbable`:** antes del once funciona. B5 por rol tiene 10 de 11 sostuvo, con el «banco probable» acertado en Sevilla 1570462, PSG 1552824, Juventus 1550201 y Panathinaikos 1593363. El error **no bajó: cambió de lugar**. Ahora está en el B5 *rehecho con el once* (5 casos del 20 al 22/11), que no toma la lista de la hoja.
- **EFE-RECOMPUTO-PENDIENTE y el rehacer por FUERA-EN-LA-HOJA y ONCE-SIN-FILA-F1:** la F1 sin fila bajó mucho. El recómputo de B y F y las bajas de la hoja siguen fallando: 9 casos, del 17 al 22/11, incluidos días posteriores a los arreglos. Schalke y Aucas tenían FUERA-EN-LA-HOJA sonando y el depósito entró igual. **Que el aviso pase a bloqueo del recibo.**
- **`ventajaPorFuerza`, y Jev con `lectura`:** no tocan al EFE. Solo 3 lecciones traen `modoFallo: lectura` (Suecia, Real Unión, Liverpool Montevideo) y por la prosa las tres son del EFE (recómputo o rama). Ninguna es de otro skill.
- **«El banco, la F1 y el arquero sin el partido del homónimo» (21/11 22:50):** ninguna lección habla de homónimos. Después del arreglo hay 82 lecciones del 22 y 23/11, y los B5 con titulares de ese tramo (Hull) no son de homónimo. No se puede juzgar; no aparece.

## Rarezas del dato

- **Dos lecciones del mismo lado se pisan:** Stuttgart y Schalke 1575228 (las dos del rehacer) y Ameliano 1632063 (B5 y F3). No están duplicadas.
- **Cuarentena:** 2 lecciones (Deportiva Minera–Cartagena 1644353, copa), por la discrepancia de DT. Las clasifiqué igual.
- **Atribuidas al EFE y que son de otro skill:** Maldonado 1650500 y Ameliano 1632063 (pronóstico y espina, sad-analysis) y Millonarios 1650174 (descarte y cadena). Además, Bulo Bulo 1645547 nombra un error de la matriz.
- **Lecciones del 17/11 (15, selecciones):** Suecia 1528998 y Bosnia 1528999 (B y F sin recomputar) pudieron correr con la v1.10. Aun así, la v1.10 ya mandaba recomputar con 3 o más rotados. Lo único que agregó la v1.11 es la marca «recomputado con el once». Ninguna lección del 17/11 cita una regla que la v1.11 haya cambiado.
- **Lecciones con `queP` largo:** 12 traen el resultado en `queP` («perdió 0-2…»). No cambian la clase.
