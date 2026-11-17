# Propuesta de revisión · `efe-clasificador` v1.10 → v1.11 (+ `efe-dashboard` v1.13 → v1.14)

> **APROBADA por el usuario el 17/11/2026, con todas las recomendaciones.** 1. (a) B y F se recomputan siempre con el once; la app lo exige desde 3 · 2. (a) el punto 6 entra como aclaración · 3. (a) COLAPSO + AGRAVANTE sigue candidato. Lo demás, como recomienda la propuesta (con efe-dashboard v1.14).

**Estado:** PROPUESTA (17/11/2026), para aprobar punto por punto. No se tocó
ningún skill, ni código, ni lección. Se aplica **junto con el núcleo**
(`NUCLEO_SKILLS_propuesta.md`, aprobado el 10/11 con las cinco
recomendaciones de `RESUMEN_GENERACION_2026-11.md` y todavía sin aplicar).

**Base.** El skill vigente (`SKILL.md`, `rubrica-efe-v1.10.md`, dashboard
v1.13; las líneas citadas son las de hoy) y el estudio del 17/11
(`estudio_lecciones_2026-11-17/`). La prosa de las **189 lecciones
pendientes** (10-16/11, ciegas PRE) se releyó para cada punto.

**Honestidad con la muestra.** Es **una semana**, con mayoría de partidos de
selecciones (fecha FIFA: Nations League y amistosos) y unas 20 lecciones de
copa nacional (sirven para la rúbrica, no para métricas). Clasificación por
la prosa: 123 la regla se sostuvo · 35 mal aplicada · 14 la regla falló ·
9 insumo · 7 no dice · 1 de otro skill. **Ninguna lección pide mover un
número** y esta propuesta no mueve ninguno: pesos, máximos, cortes de la
tabla de puntuación, cortes de zona, el ×1,5 de F2c y los umbrales de las
alertas quedan como están. Lo numérico va como «candidato a medir».

---

## 0. Resumen

Lo que más se repite **no es una regla que falle, es una regla escrita que no
se cumple al rehacer con el once oficial**. La app ya hizo hoy lo que le
tocaba; al skill le queda alinear el texto con eso y aclarar el resto.

### Lo que ya hizo la app hoy (17/11; se referencia, no se pide)

- **`EFE-RECOMPUTO-PENDIENTE`** (1068 paso 2, `parte.alerta_recomputo_efe`):
  con el once, 3+ titulares fijos que no arrancan y el parte no declaró,
  declarados fuera que la hoja pone en el once, o el arquero TF que no
  arranca; **se calla con «recomputado con el once» en la nota del bloque
  B**. El modo `rehacer` carga `efe-clasificador` con ella, y entra también
  con `ONCE-SIN-FILA-F1` y `FUERA-EN-LA-HOJA` (`parte.REHACER_POR`).
- **`bancoProbable`** en `GET /analisis/cowork/f1/{id}` (y `dtp`, `tde`): UNA
  lista para B5 y «banco probable»; con el once y la banca completa, la hoja.
- **Jev A0:** `lectura_efe` pasa a `lectura`; el dossier del EFE cuenta aparte
  `lecturaDeOtrosConInsumoEfe`.
- Desde el 14/11 (1400) la app suma al leer las filas `delOnceOficial` de
  hasta 4 titulares sin fila (`parte.con_filas_del_once`).

### Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos (partidos) | Recomendación |
|---|---|---|---|---|
| 1 | La F1 con el once: una fila por titular **sin umbral**; el **3** es el corte del recómputo de B y F (`EFE-RECOMPUTO-PENDIENTE`), no de la tabla; la nota B lleva la marca «recomputado con el once» y la prosa de bajas se reescribe entera | aclaración + marca | 19 lecciones / 15 partidos | **Aprobar** |
| 2 | El arco: B6 🔶, la zona GK en rojo (×1,5 de F2c) y GK-DOWNGRADE miden continuidad o ausencia, **no son vía de gol** sin GK-FALLA-ACTIVA o errores documentados; B6 sale de la hoja | aclaración | 9 + 2 | **Aprobar**; el ×1,5 solo como candidato |
| 3 | Rama «once alternativo»: el clasificado o eliminado en la última fecha es un **hecho** que la abre; un contraargumento no la cierra | aclaración | 6 | **Aprobar** |
| 4 | B5 en copa con liga a ≤ 5 días, **por rol y condicionado al once**; con el once, el banco es `bancoProbable` (hoja) | aclaración | 4 (2 directos) | **Aprobar** (muestra justa) |
| 5 | Jerarquía de fuentes: **ejemplos de redacción** que van a Duda y el convocado con sanción discutida | ejemplos, sin regla nueva | 4 | **Aprobar** |
| 6 | F3: la reducción por zona usa el **rol de hoy en la competición**, no el titular nominal | aclaración de la v1.9 | 3 | Aprobar o dejar como nota (decisión 2) |
| Dash | `efe-dashboard` v1.14: la matriz no usa el arco como gatillo de gol sin GK-FALLA-ACTIVA; la palanca del reloj lee `bancoProbable`; descripción | alineación | los de 2 y 4 | **Aprobar** |
| N | Núcleo: changelog y apéndice a `references/HISTORIAL.md`, quinta lista del barrido F5, «Disciplina 35» renombrada | forma, sin regla | — | **Aprobar** (ya decidido el 10/11) |

**Número:** v1.11 (aclaraciones, sin números ni bloques nuevos), con núcleo.
El dashboard pasa a v1.14 porque la matriz y la descripción cambian.

---

## 1. La F1 con el once oficial: una fila por titular, sin umbral; el 3 es del recómputo · [aclaración] [marca]

**Qué dice hoy.**
- Rúbrica, línea 271 (F1, punto 6) y `SKILL.md` línea 27: «(1) la F1, con
  los once titulares con fila, **sin umbral**».
- Rúbrica, líneas 394-395 y `SKILL.md` líneas 28 y 44: «con ≥ 3 titulares
  fijos rotados, B y F se recomputan» (v1.7/v1.9) y «el condicionado se
  levanta en las dos direcciones: B y F se recomputan con el once que salió,
  **haya rotado o no**» (v1.10).
- **La app**, en el detalle de `ONCE-SIN-FILA-F1` (`parte.py`, ~línea 5219):
  «(**con 3 o más**, rehacer la tabla F1 con GET …/f1/{id} y re-depositar)».

**De dónde sale la contradicción.** Las lecciones citan dos cosas distintas
como si fueran una: el «corte de 3» lo leyeron en el texto de la alarma de la
app (Eslovaquia 1528967a: «por encima del corte de 3»; Chequia 1528961a: «con
3 o más»), y otras lo niegan con la rúbrica (Kazajistán 1528968b y Grecia
1528966b: «aunque sean menos de 3»; Feroe 1528967b: «con 2, bajo el corte»).
La rúbrica no tiene corte para la tabla; el 3 es del **recómputo de B y F**,
que desde hoy exige `EFE-RECOMPUTO-PENDIENTE`.

**Casos (19 lecciones, 15 partidos; 18 mal aplicadas, 1 insumo).** Sin
fila y decisivos: Kazajistán 1528968 (Chesnokov, el gol), Eslovaquia 1528967
(Prekop, el 1-0), Feroe 1528967 (Davidsen, el penal), América 1648690
(Tortolero, el 1-2), Alavés 1644336 (M. Rodríguez, el 1-3). Otros: Escocia
1545659, Eslovenia 1545654, Grecia 1528966, Serbia 1528965, Montenegro
1545613, San Marino 1528964, Albania y Finlandia 1528963, Chequia 1528961,
Inter Bogotá 1648690, Valencia 1644380. Prosa sin rehacer: Montenegro
1528979b (la F1 sacó a Lončar de las bajas y la nota B y el ensayo siguieron
con «faltan cinco»: **un solo** declarado fuera que jugó, debajo del corte) e
Inter Bogotá 1549869a (no recomputó B y F). Roles del alternativo:
Atlético-MG 1492455b (punto 6). Insumo: Tavernes 1644380a (un agregador).

**Lo que sigue.** 13 de los 15 partidos son del 10 al 13/11, **antes** de
que la app sumara las filas sola (1400, 14/11). Después queda la **prosa** y
el **recómputo** (Montenegro 1528979, Inter Bogotá 1549869): lo que
`EFE-RECOMPUTO-PENDIENTE` cubre desde 3 y el skill por debajo de 3.

**Propuesta.** Una sola redacción, coherente con la alerta:

*Rúbrica, línea 271, después de «(1) la F1, con los once titulares con fila,
sin umbral;»*, insertar:

> **Una fila por titular, sin umbral; el 3 es del recómputo *(v1.11)*.**
> Con el once oficial, cada titular sin fila se agrega antes de depositar,
> aunque sea uno (Kazajistán 1528968: Chesnokov, sin fila, hizo el gol;
> Feroe 1528967: Davidsen convirtió el penal); las filas `delOnceOficial` se
> copian de `GET …/f1/{id}`. El **3** no es de la tabla: es el corte desde el
> cual la app **exige** el recómputo de B y F (`EFE-RECOMPUTO-PENDIENTE`: 3 o
> más titulares fijos que no arrancan y el parte no declaró, declarados fuera
> que la hoja pone en el once, o el arquero titular que no arranca). Por
> debajo de ese corte el recómputo **sigue siendo la regla** (el condicionado
> se levanta en las dos direcciones, v1.10): con la hoja se reescribe **toda
> la prosa de bajas**, no solo la tabla (nota B, dato estructural, F3,
> caja y ensayo; Montenegro 1528979: un sancionado que jugó y la nota siguió
> con «faltan cinco»). Hecho el recómputo, la nota del bloque B lo dice con la
> marca literal **«recomputado con el once»**; sin recomputar no se escribe.

*`SKILL.md`, línea 27*, cambiar «(1) la F1, con los once titulares con fila,
sin umbral;» por:

> (1) la F1, con los once titulares con fila, sin umbral (el 3 de
> `EFE-RECOMPUTO-PENDIENTE` es el corte del recómputo de B y F, no de la
> tabla);

y al final del mismo punto agregar: «Recomputado, la nota del bloque B dice
«recomputado con el once» y la prosa de bajas se reescribe entera *(v1.11)*.»

*`SKILL.md`, línea 28*, cambiar «con ≥ 3 titulares fijos rotados en el once
oficial, B y F se recomputan: no hacerlo es un incumplimiento» por «con el
once oficial, B y F se recomputan (desde 3 titulares fijos o con el arquero,
la app lo pide con `EFE-RECOMPUTO-PENDIENTE`): no hacerlo es un
incumplimiento».

**Lo tumbaría:** que en la próxima tanda (partes desde el 17/11) sigan
apareciendo titulares sin fila o notas B sin recomputar **con la alerta
sonando y el rehacer cargando el EFE**: entonces no es texto, es la rutina.

---

## 2. El arco: B6 🔶, la zona GK en rojo y GK-DOWNGRADE no son vía de gol por sí solos · [aclaración] [candidato a medir]

**Qué dice hoy.** La v1.10 (rúbrica, línea 143) ya dice que el suplente sin
rodaje es «**vía a vigilar**, no vía firme», que pide GK-FALLA-ACTIVA o
errores documentados. No lo dice de **B6 🔶 por un arquero elegido por
decisión**, de la **zona GK en rojo** que arma el ×1,5 de F2c ni de
**GK-DOWNGRADE por un debut**, y por ahí la vía «pelota sucia contra el
arquero» siguió llegando al DTP y a la matriz.

**Casos (9 lecciones, 9 partidos; ninguno concedió por error del arquero).**
Chequia 1528985b (Kinský, sin rodaje en la competición, seis atajadas: «la
vía pelota sucia no rindió»), Inglaterra 1528984b (Trafford, elegido por
decisión, seis atajadas), Turquía 1528982b (zona GK en rojo, Özer: siete
atajadas contra 3,43 de xG; «el ×1,5 mide ausencia, no forma»), Pasto
1549868a (GK-DOWNGRADE por debut, uno sobre 1,09 de xG), Celta 1644376b
(debutante, valla en cero), y las cajas con dos arqueros que no movían la
franja: Jaguares 1549866b, Dinamarca 1528974b, Gales 1528972b, Albania
1528963a («la vía del error en la salida, gatillo de la matriz, no
apareció»). Mal aplicadas del mismo grupo: Moldavia 1528987b (B6 ✅ por
nombre; la hoja de la base decía Celeadnic 4 de 4) y Bélgica 1528958b.

**La otra cara (1 caso):** Mijas 1644362a, arco alternado, el 0-1 llegó ante
la salida del alternativo. Es arco **sin dueño** (v1.8), que la caja ya abre:
no contradice la aclaración, que habla de la vía, no de la caja.

**Propuesta.** *Rúbrica, línea 143, al final del párrafo «El suplente sin
rodaje es una vía a vigilar»*, agregar:

> **Lo mismo para B6 🔶, la zona GK en rojo y GK-DOWNGRADE *(v1.11)*.** Los
> tres miden **continuidad o ausencia**, no una vía de gol del rival: un
> arquero elegido por decisión con poco rodaje, la reducción GK que arma el
> ×1,5 de F2c y el debut con GK-DOWNGRADE amplían el rango y abren la caja,
> pero la vía «pelota sucia contra el arquero» baja al DTP y a la matriz solo
> con GK-FALLA-ACTIVA o errores documentados (Chequia 1528985: Kinský, seis
> atajadas; Inglaterra 1528984: Trafford; Turquía 1528982: Özer, siete
> atajadas contra 3,43 de xG; Pasto 1549868; Celta 1644376). **B6 se puntúa
> con los minutos de la hoja** del arquero del once en la competición, no con
> el nombre (Moldavia 1528987: Celeadnic 4 de 4 en la base, el parte decía
> Kozhukhar). El arco sin dueño sigue abriendo sus escenarios en la caja
> (Mijas 1644362: el 0-1 llegó ante la salida del alternativo).

*`SKILL.md`, «Cuando no hay XI», punto 4* (el ×1,5 en la rama B): agregar
«; el ×1,5 mide la ausencia, no es vía de gol del rival (v1.11)».

**Candidato a medir, NO se aprueba:** bajar el ×1,5 de F2c, o no activar
GK-DOWNGRADE, cuando el suplente tiene titularidades recientes. Es un número:
pide el gol concedido por error del arquero con y sin el ×1,5 sobre todos los
partes, no 9 lecciones de una semana de selecciones.

**Lo tumbaría:** 3+ partidos en que el suplente sin GK-FALLA-ACTIVA conceda
por error propio documentado (hoy: 0 en esta tanda; 2 a favor de la vía en la
v1.10, Gremio y Aucas).

---

## 3. Rama «once alternativo»: el clasificado o eliminado de la última fecha es un hecho · [aclaración]

**Qué dice hoy.** Rúbrica línea 395 y `SKILL.md` línea 44 (v1.10): la rama se
abre por un hecho, «una rotación anunciada, un DT que rota de costumbre o un
equipo sin nada en juego», con los rotables de todas las líneas.

**Casos (6 lecciones, 6 partidos, todos mal aplicados).** Sin rama pese al
hecho: Sport Boys 1549557b (última fecha, sin nada en juego: 7 titulares
fuera, arquero incluido) y Bucaramanga 1549865a (clasificado en la última
fecha; la caja solo movía al 9 y faltaron cuatro fijos). Rama corta: Atlético
Nacional 1549864a (rotó arco y zaga y dejó a James, Morelos y Sarmiento, que
arrancaron en el banco) y, en la F1, América, Valencia y Alavés (punto 1).
Rama descartada por un contraargumento: Always Ready 1649146b (la gala de una
vuelta eliminatoria contra una ida con la vuelta en casa a 4 días; rotó).

**Cuando la rama se escribió acertó 10 de 14** (Juventud 1649063, Eibar
1644365, Puerto Cabello y Monagas 1646937, Fortaleza 1549865b, Independiente
Petrolero 1649146a, Amorebieta 1644335, Pereira 1549872b…). La regla está;
falta que el hecho se reconozca.

**Propuesta.** *Rúbrica, línea 395, después de «un equipo sin nada en juego,
nunca por sospecha.»*, insertar:

> *(v1.11)* «Sin nada en juego» incluye al **clasificado o eliminado en la
> última fecha**, con fase final o copa por delante (Bucaramanga 1549865:
> clasificado, salió sin cuatro fijos; Sport Boys 1549557: siete fuera, el
> arquero incluido; Puerto Cabello y Monagas 1646937, eliminados: la rama
> acertó). **Un contraargumento no cierra la rama**: va como su peso en la
> caja (Always Ready 1649146: la gala de otra eliminatoria no era
> antecedente de una ida con la vuelta en casa a 4 días; rotó).

**Lo tumbaría:** clasificados o eliminados de última fecha que repitan el
once en 3+ partidos con la rama escrita (la rama se declara y no se presume:
eso ya lo dice la línea 399, «Qué no cambia»).

---

## 4. B5 en copa: por rol y condicionado al once; con el once, el banco es la hoja · [aclaración]

**Qué dice hoy.** Rúbrica línea 125 (v1.10): B5 nombra el banco por rol;
«con el once oficial, el banco es la hoja». No dice qué pasa con B5 cuando el
porcentaje ya va «condicionado al once» por calendario.

**Casos (4 lecciones, 4 partidos; 2 directos de copa).** Boston River
1649058b (el 9 de impacto nombrado no estuvo en la hoja; entraron Avenatti,
Aristegui y L. Suárez, que B5 no nombraba) y UD Logroñés 1644335b (el banco
que había decidido en Ferrol fue titular o no estuvo); Real Potosí 1649149b
(el 0-2 de Igor Soares, 1 titularidad, fuera de la lista); Garcilaso
1549559b (el banco de impacto, fuera de la hoja al rehacer). A favor del B5
por rol nombrado entero: UCV 1549560a, Los Chankas 1549556b, Liverpool
1649061b, Cali 1549867a, Medellín 1549863b.

**Propuesta.** *Rúbrica, línea 125, al final del párrafo «B5 nombra el banco
por rol»*, agregar:

> *(v1.11)* **Con el porcentaje «condicionado al once»** (copa con liga a
> ≤ 5 días, rama «once alternativo» abierta), **B5 va condicionado igual**:
> el banco de impacto de la temporada puede ser titular o no viajar (Boston
> River 1649058, UD Logroñés 1644335). La lista por rol es la de
> `bancoProbable` de `GET …/f1/{id}` (antes del once, `fuente: probable`;
> con el once y la banca completa, `fuente: hoja`, sin ningún titular), más
> los rotables de la rama. Con el once, B5 se relee sobre la hoja (Garcilaso
> 1549559) y nombra a todos los que pueden entrar, no solo a los goleadores
> conocidos (Real Potosí 1649149).

**Candidato a medir, NO se aprueba:** el umbral del B5 🔶 por «un solo
partido de banco decisivo» (v1.9, Beveren): Albion 1649060b suma su segundo
caso con la misma dupla. Es un umbral; queda en observación.

**Lo tumbaría:** que con `bancoProbable` en uso el B5 nombrado siga sin
contener a quien entra y decide en 3+ partidos de copa: entonces el problema
es la lista de la app (entradas en los últimos 10), no la regla.

---

## 5. Jerarquía de fuentes: ejemplos de redacción · [ejemplos, sin regla nueva]

**Qué dice hoy.** Rúbrica líneas 249-257 (v1.7-v1.10): agregador = Duda;
fuentes con fecha (> 7 días contradicha = Duda); ciclo de amarillas = Duda con
rama; las dos direcciones.

**Casos (4 mal aplicadas de 14; las otras 10 se sostuvieron: Estonia
1528988a, Central Español 1649058a, Türkiye 1528958a, Valencia 1644380b…).**
Always Ready 1649148a («**se recupera de una lesión**», día del partido,
cargado ❌: Maraude titular y gol al 5'); Bucaramanga 1549865a (parte de 7
días; Novoa titular; regla v1.8); Islandia 1545617a (ciclo con conteo
parcial usado como reemplazo; estaba suspendido; regla v1.10); Tolima
1549867b (Sandoval «duda» por la 5.ª amarilla con la **convocatoria
publicada** que lo incluía; jugó y marcó dos).

Tres de cuatro son reglas escritas que no se cumplieron; lo nuevo es el
**lenguaje** (Always Ready) y el **convocado con sanción discutida** (Tolima,
1 caso: va como ejemplo de «las dos direcciones», no como regla).

**Propuesta.** *Rúbrica, después de la línea 257 (punto 4 de la v1.9)*:

> 5. *(v1.11, ejemplos, sin regla nueva)* **Van ⚠️ Duda con su rama «si
> juega»**: «se recupera de», «en recuperación», «no está descartado», «llega
> justo», una baja de un parte de más de 7 días sin la víspera
> (Always Ready 1649148: «se recupera de una lesión» el día del partido,
> titular y gol; Bucaramanga 1549865). **Va ❌ Baja** solo con «descartado»,
> «no viaja», «fuera de la convocatoria» de nivel 1-3. Un ciclo de amarillas
> con conteo parcial nunca es reemplazo disponible en la caja (Islandia
> 1545617). Y al revés: **un convocado en la lista publicada** con una
> sanción que discute la prensa va ✅ con la rama «no habilitado» (Tolima
> 1549867: Sandoval, dos goles).

**Lo tumbaría:** nada que medir; si los ejemplos no cambian la conducta en la
próxima tanda, el arreglo es `SANCION-SIN-DECLARAR`/certeza (A3), no texto.

---

## 6. F3: la reducción usa el rol de hoy en la competición · [aclaración de la v1.9]

**Qué dice hoy.** Rúbrica (F1, v1.9, punto 5): «el rol se fija por
titularidades y participación de la temporada, no por la última fecha». No
dice qué pasa con el titular nominal que ya no lo es en esta competición.

**Casos (3 partidos).** Bélgica 1528958b (zona GK 66,7 % por Courtois; Lammens
atajaba la Nations League desde el 02/10 e hizo 6 atajadas), Hungría 1528973b
(ATK en rojo, 66,7 %, contando como hueco bajas de una rotación previa;
entraron Varga y Sallai, de nivel titular, y Varga marcó) y Atlético-MG 1492455b (la F1 con
los roles del alternativo dio IP 20 y «opera degradado»; el once titular
dominó: 56 % de pelota, 1,14 de xG, valla en cero).

**Propuesta.** *Rúbrica, línea 363 («Toda zona en rojo dice quién la
cubre»), al final:*

> *(v1.11)* El peso del ausente es **su rol de hoy en la competición del
> partido**, no el nominal: un titular que ya no ataja o no arranca en este
> torneo no deja hueco (Bélgica 1528958: Courtois; Hungría 1528973), y con
> el once oficial los roles se releen antes de disparar F3 (Atlético-MG
> 1492455: roles del alternativo, F3 falsa).

**Lo tumbaría:** 3+ partidos en que la ausencia de un titular nominal que ya
no arrancaba en la competición sí se pague como hueco. Muestra justa (uno de
selección, uno de una regla ya escrita): decisión 2.

---

## 7. Las alertas, con sus conteos

| Alerta | Lecciones | Se sostuvo | En contra / otro | Qué hacer |
|---|---:|---:|---|---|
| F3 | 30 (29 partidos) | 22 | 4 la regla falló, 3 mal aplicada, 1 otro skill | Se cumple como **«baja la confianza en la K, no ordena el partido»** (Austria, Vasco, España, Monterrey, Liechtenstein). Como señal de volumen tiene ~6 contraejemplos: Hungría y Bielorrusia 1528964b (generaron igual), Racing 1649057b, Eslovenia, Andorra. La lectura vigente los concilia; punto 6 para el rol |
| EFE-EMPATE-TECNICO | 27 (27) | 27 | — | **Así escrita no se puede refutar**: si gana el de mayor porcentaje también «se cumple» (Millonarios, Moldavia, España). Por la prosa ganó el de menor porcentaje en ~9 y hubo empate en ~11. Sin cambio de texto: **la prueba es A6** (sigue sin hacer, ver «Para la app») |
| EJE-DEBUTANTE | 14 (14) | 9 | 4 no dice, 1 mal aplicada | Amplía el rango y se materializó en 9 (Bulgaria 1528969 y 1528988, Comerciantes 1549557, Chipre 1528979, Polonia 1528977, Inglaterra 1528962, Liechtenstein 1528970, Macedonia 1545659, Israel 1528971 la vía sin gol). No se pagó en Peñarol, Croacia, Albania, Estonia. **Lo que falla es el insumo** (Bulgaria 1528988b: línea de cuatro con un grid de tres; Millonarios 1549871, Pereira 1549872, Chicó 1549870 con once tardío). Sin cambio |
| COLAPSO EN CASCADA | 11 (11) | 10 | 1 no puesto a prueba (Santa Fe 1549869b) | La forma v1.6/v1.9 se cumple: recibe primero, no recupera, no se rompe (Liechtenstein, Chequia, Querétaro, Jaguares, Gales, Chapecoense, Serbia, Pasto, Croacia). **San Marino 1528981b** (2-7, zaga de urgencia) es el **4.º caso de COLAPSO + AGRAVANTE** (Marítimo, Manchester United, Udinese), con la reserva de la propia lección: μ 2,31 contra 0,49 también lo explica. Decisión 3 |
| T.54 · FACTOR-X · G-BLOQUE | 5 · 3 · 3 | 5 · 3 · 1 | G-BLOQUE: 2 sin poner a prueba (gol antes de la vida útil) | Sin cambio |

Sueltos que **no entran** (1-2 casos): D3 ❌ de visita que pierde la ventaja
cuando abre (Grau 1549560b; la nota del TDE leyó mejor), D3 por racha en vez
de respuesta (UTC 1549556a, ya regla), DT suspendido sin mirar (Maldonado
1649059), E alto hecho contra rivales muy inferiores (Gibraltar 1545615).

---

## 8. Candidatos a medir (ninguno se aprueba con esta propuesta)

| Candidato | Casos | Qué haría falta |
|---|---|---|
| Bajar el ×1,5 de F2c / no activar GK-DOWNGRADE con un suplente con titularidades | 9 en contra de la vía, 1 a favor (Mijas, arco alternado) | Gol por error del arquero, con y sin el ×1,5, sobre todos los partes (no una semana de selecciones) |
| Umbral del B5 🔶 por un partido de banco decisivo | 2 (Albion) | Banco decisivo por partido sobre `bancoProbable` (A8) |
| COLAPSO + AGRAVANTE como regla | 4 (uno con μ de por medio) | El denominador: cuántos D3 ❌ + F3 DEF o R-KT.2 de visita **no** se rompieron (sale de A7, la base del D3 calculada) |
| F3 leída con H: contra un rival sin profundidad no se paga | 2 (Andorra 1545615a, Eslovenia 1545654a) | Más casos; sin medición propia |
| EFE-EMPATE-TECNICO: tasa del de mayor porcentaje con y sin la alerta | 27 lecciones irrefutables | A6 |

---

## 9. Para la app (solo lo que falta; revisado con grep en `backend/` el 17/11)

1. **El texto de `ONCE-SIN-FILA-F1`** (`backend/analisis/parte.py`, detalle
   de la alerta, ~línea 5219) dice «con 3 o más, rehacer la tabla F1»: es la
   fuente del «corte de 3» que citan las lecciones (punto 1). Que diga
   «rehacer la tabla F1 con las filas `delOnceOficial` de GET …/f1/{id} y
   re-depositar, **aunque sea uno**; el recómputo de B y F lo pide
   `EFE-RECOMPUTO-PENDIENTE`», con su check en `test_cowork`. **No** se pide
   que el recibo frene el depósito: desde el 14/11 la app suma sola hasta 4
   filas y el rehacer entra con la alerta; primero se mira la próxima tanda.
2. **A6** (aprobada el 10/11, sin rastro en `backend/`): la tasa del de mayor
   porcentaje con y sin `EFE-EMPATE-TECNICO`, y contra la cuota en la misma
   base. Sin ella, 27 de 189 lecciones son «declarada y cumplida» sin
   contenido.
3. **Aprobados el 10/11 y sin hacer**, con casos nuevos (se priorizan, no se
   piden de nuevo): `EJE-DEBUTANTE-SIN-DECLARAR/-SIN-OBJETO` sobre el once
   (Bulgaria 1528988, Millonarios 1549871) y `onceTardio` (Pereira 1549872,
   Millonarios 1549871, Águilas 1549863, Irlanda del Norte 1528975, Chicó
   1549870, Progreso 1649056).

---

## 10. Coherencia con TDE v0.1.27, DTP v1.9 y sad-analysis v4.6 (en paralelo)

- **Banco.** Las tres propuestas nombran **la misma lista**, `bancoProbable`
  (EFE B5 y «banco probable», DTP `bancoOfensivo`, TDE ramas y su bloque F,
  que hereda B5: `INDICE_IE.md` línea 120). Con la rama abierta, el TDE y el
  DTP heredan un B5 **condicionado** (punto 4), no uno firme.
- **Recómputo y herencia al TDE.** En `rehacer` va primero el EFE, en el orden
  de la v1.10 (F1 → bajas de la hoja → B6 → EJE → B y F → D1 y H), y después
  el DTP y el TDE: lo que el TDE hereda (B5, D3, F4; disciplina «heredar B5,
  D3, F4, H y alertas») sale del EFE recomputado, y la marca «recomputado con
  el once» en la nota B dice que ya está. Sin la marca, el TDE y el DTP leen la
  hoja, no la nota B vieja.
- **El arco.** El punto 2 coincide con el DTP vigente (≥ 2 errores del arquero
  para la vía) y con la v1.10: el DTP no hereda «pelota sucia contra el
  arquero» de B6 🔶, la zona GK en rojo ni GK-DOWNGRADE. Si el DTP v1.9 dice
  algo del arquero, que cite esta regla.
- **Matriz.** El encargo de `partes` no carga el dashboard (recomendación 5 del
  núcleo): el punto Dash-1 (el arco no es gatillo) y Dash-2 (`bancoProbable`)
  tienen que estar también en sad-analysis v4.6 o en el prompt, donde se
  escribe la matriz.
- **F3 y el 1X2.** Polonia 1528977b (otro skill): la confianza bajada por F3
  no llegó al 1X2. El EFE dice cuánto creerle a la K; el ancho del rango lo
  decide sad-analysis v4.6. Nada que cambiar acá.

---

## 11. Núcleo (se aplica con esta versión)

**`efe-clasificador/SKILL.md`** (todo núcleo, 1,7 K):
- Debajo del título, la línea común del núcleo («Versión vigente: v1.11 … las
  notas de versión y los casos están en `references/HISTORIAL.md`: no hace
  falta leerlo para analizar un partido»).
- **«Disciplina 35» (línea 21) pasa a «Bloque F sin XI confirmado»**, mismo
  texto: la disciplina 35 del TDE va al historial como derogada por la 55
  (recomendación 1, aprobada) y el EFE no puede citar un número que en el otro
  skill significa otra cosa.

**Rúbrica** (pasa a `references/rubrica-efe-v1.11.md`):
- **A `references/HISTORIAL.md`, tal cual:** líneas 7-70 (changelog v1.10 a
  v1.4, con el de la v1.11 encima) y 700-754 (apéndice: Estudiantes y Junior),
  que deja una línea: «Casos de validación 1 y 2: `references/HISTORIAL.md`».
- **Sube al cuerpo** (recomendación 4, aprobada): la **quinta lista del
  barrido fijo de F5** (línea 423): «5. **El suplente con impacto documentado
  desde el banco** en la temporada en curso es factor X por derecho propio, se
  proyecte titular o no (dashboard v1.8)». Encaja con `bancoProbable`.
- Ninguna regla vive solo en el changelog (núcleo §2.3, verificado de nuevo
  para la v1.10). Los blockquotes con su caso no se separan (fase 2).

**`efe-dashboard/SKILL.md`:** notas v1.13 a v1.7 (líneas 8-52) y «Movido a
otro skill» + «Nota de actualización manual» (333-fin) al historial; antes de
mover, al núcleo (§2.4, aprobado): el suplente de impacto es factor X (PASO 1,
F5) y el once probable es nivel C con la ventana de confirmación (PASO 0-bis).

---

## 12. `efe-dashboard` v1.13 → v1.14

- **Dash-1. La matriz no usa el arco como gatillo de gol** («Para perder»,
  PASO 6) sin GK-FALLA-ACTIVA o errores documentados: B6 🔶, la zona GK en
  rojo y GK-DOWNGRADE van a la caja como rango (punto 2; Albania 1528963,
  Chequia 1528985, Inglaterra 1528984).
- **Dash-2. La palanca del reloj** (PASO 6, línea 242) sale de `bancoProbable`
  de `GET …/f1/{id}` (punto 4), condicionada al once con la rama abierta.
- **Dash-3. Descripción:** «EFE v1.11 (skill v1.14)». La banda de goleada
  sigue sin números.

---

## 13. Qué NO se propone y por qué

- **Ningún número** (×1,5, GK-DOWNGRADE, el 3 del recómputo, cortes de zona,
  B5 🔶, brecha): van como candidatos (§8).
- **EFE-EMPATE-TECNICO y COLAPSO EN CASCADA** no cambian de forma; el primero
  espera A6.
- **Once tardío** (7 lecciones, todas insumo): la regla está; falta
  `onceTardio` en la app.
- **Repetir la F1 con más fuerza**: la v1.10 ya lo mandaba y no cambió la
  conducta; el arreglo fue de la app. Esta versión solo saca la contradicción
  del 3. Tampoco que el recibo frene el depósito (§9.1).
- **Los sueltos** del §7 y la F3 leída con H.

---

## 14. Decisiones del usuario

1. **Punto 1, el recómputo debajo de 3.** ¿El skill dice que con el once B y
   F se recomputan **siempre** (lo que ya dice la v1.10, «haya rotado o no»)
   y la app solo lo exige desde 3, **(a)** recomendado; o el skill baja a «se
   recomputa desde 3 o con el arquero» y lo de abajo es opcional, **(b)**?
   La (b) contradice la v1.10 y Montenegro 1528979 (un solo jugador, la prosa
   quedó vieja).
2. **Punto 6.** ¿Entra como aclaración (3 casos, uno de una regla ya
   escrita), **(a)** recomendado; o queda como nota hasta otra tanda,
   **(b)**?
3. **COLAPSO + AGRAVANTE con su 4.º caso** (San Marino, con μ de por medio).
   ¿Sigue candidato hasta tener el denominador (A7), **(a)** recomendado; o
   pasa a regla declarativa («con D3 ❌, R-KT.2 de visita o F3 rojo en DEF,
   la ruptura es posible»), **(b)**?

Lo demás, como recomienda cada punto.

---

## 15. Cómo se aplica si se aprueba

1. El núcleo (§11) sobre la v1.10, con `test_nucleo_skills` y el `diff` de
   control; después los puntos 1-6, el changelog v1.11 en el historial y el
   dashboard v1.14; la línea de `ONCE-SIN-FILA-F1` (§9.1) en la misma tanda.
2. `CORTE_VERSION` y `SUBIDA_VERSION` al subir; las lecciones tocadas, a
   `aplicada` o `descartada`.
3. **Se reabre** si en la próxima tanda siguen titulares sin fila con la
   alerta sonando (1), el suplente sin GK-FALLA-ACTIVA concede por error en
   3+ partidos (2), o A6 / A7 dan resultados.
