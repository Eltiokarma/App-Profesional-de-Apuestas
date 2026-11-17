# Propuesta de revisión · `teorema-del-echado` v0.1.26 → v0.1.27

**Estado: PROPUESTA (17/11/2026), para aprobar punto por punto.** No se tocó
el skill, ni el código, ni otros docs. Se aplica **con el núcleo**
(`NUCLEO_SKILLS_propuesta.md`, aprobado con las cinco recomendaciones de
`RESUMEN_GENERACION_2026-11.md`): el changelog y los casos pasan a
`references/HISTORIAL.md`.

**Fuentes:** el estudio del 17/11 (`estudio_lecciones_2026-11-17/`: `README.md`,
`estudio_teorema-del-echado.md`, `clasif_teorema-del-echado.json`); la prosa de
las 276 lecciones `pendiente` (81 fixtures del 10 al 16/11, ciegas PRE,
escritas con la v0.1.26); lo aprobado el 10/11 (`PENDIENTES.md`,
`DESCONFIAR_propuesta.md` puntos 4 y 5); el skill vigente (`SKILL.md` v0.1.26,
781 líneas, y `references/INDICE_IE.md`).

Las líneas citadas son las del `SKILL.md` vigente. Al insertar de abajo hacia
arriba, no se corren.

## Resumen

Las reglas vigentes se sostienen: 198 de 276 lecciones dicen que se cumplió
(54 de ellas con el lado fallado); la 61 da 47 de 47, la 65 29 de 29 y la
44 (b) 39 de 41. La falla más repetida es de ejecución: el banco escrito de
memoria (16 mal aplicadas y 6 de once tardío), que la app ya resolvió con
`bancoProbable`. Entra lo aprobado el 10/11 (`ventajaPorFuerza`; el desenlace
de la ventaja lo pone la fuerza y la tipología describe la vía) y tres textos
del estudio: la plantilla de `siExpulsion`, la pieza del seguro en las ramas
que no persiguen y «`SOB1` dice la necesidad, no el régimen». **Ningún número
se mueve**; seis candidatos siguen a medir. El núcleo baja el `SKILL.md` de
≈ 54 K a ≈ 28 K tokens y resuelve tres contradicciones viejas.

## Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos | Recomendación |
|---|---|---|---|---|
| 1 | El banco sale de `bancoProbable`, la lista entera, en cada rama donde entra (66) | aclaración (app hecha) | 16 mal aplicadas en 16 partidos + 6 de once tardío | aprobar · **D1** |
| 2 | La rama de ventaja cita `ventajaPorFuerza` además de `ventajaPorMinuto` (66) | aprobado antes (10/11) + app | 53.108 partidos del estudio; 15 lecciones con la referencia del minuto | aprobar · **D2** |
| 3 | El desenlace de la ventaja lo pone la fuerza; la tipología describe la vía (66, 44 (b)) | aprobado antes (10/11) | 37 contra 157 (01-09/11); acá, 9 partidos y ningún contraejemplo | aprobar |
| 4 | Plantilla de `siExpulsion` para los dos lados: tres cuentas del marcador, ventana en su campo, vía propia o seguro (16) | aclaración | 4 partidos (+1) | aprobar |
| 5 | Pieza del seguro también en las ramas que no persiguen (63) | candidato v0.1.26 → texto | 3 firmes + 2 de la v0.1.26 (de ventaja pura, 1) | aprobar · **D3** |
| 6 | `SOB1` = 1 por la tabla dice la necesidad, no el régimen: la nota va condicionada al once y al sistema (18) | aclaración (el peso, a C1) | 5 partidos | aprobar |
| 7 | 63: se borra «mientras la app no lo haga» (la herencia del `sob2` de rama ya está hecha) | aclaración (app hecha) | — | aprobar |
| 8 | Núcleo: changelog y registro al historial; las disciplinas 34-39 suben al cuerpo | aprobado antes (03/11 y 10/11) | — | aprobar · **D4** |
| 9 | Tres frases del núcleo contradichas por reglas posteriores: localía, LA TESIS y el mapeo IE→P | aclaración | — | aprobar · **D5** |
| C1-C6 | Candidatos a medir | candidato a medir | n de 1 a 6 | no entran |
| A1-A7 | Para la app | app | — | después de aprobar |

**Ya hecho por la app hoy (17/11), no se pide de nuevo:** `bancoProbable` en
`GET /analisis/cowork/tde/{id}`, `dtp/{id}` y `f1/{id}` (`backend/analisis/banco.py`;
`fuente: hoja` = los suplentes publicados sin ningún titular, `fuente: probable`
= los que entraron seguido o hicieron goles o asistencias entrando en los
últimos 10; con `posicion`, `lateral`, `golesDesdeBanco`, `titularHabitual`);
el rehacer que entra también con FUERA-EN-LA-HOJA (incluye una rama del TDE que
nombra de banco a un titular o a un no convocado), ONCE-SIN-FILA-F1 y
EFE-RECOMPUTO-PENDIENTE; Jev `lectura_efe` → `lectura` (PR #562; en el TDE solo
7 de 107 hablaban del EFE). Y ya existía el aviso del recibo para la ventana de
una rama escrita en la nota (`parte.ramas_con_ventana_en_la_nota`, 1420).

---

## 1. El banco sale de `bancoProbable` (disciplina 66) — ACLARACIÓN

**Qué dice hoy (línea 667):** el insumo de goles y asistencias de suplentes
está «aprobado y pendiente de la app; hasta entonces sale de la
investigacion»; antes del once la lista es «probable» y, «si el EFE trae el
banco por rol en B5, es esa lista»; con el once, un titular deja de ser banco.

**Qué pasó.** **(a) Titular nombrado como banco con el once ya capturado, 10
partidos:** Lithuania–Liechtenstein 1528989, Estonia–Bulgaria 1528988
(Kovachev, «banco», hizo el 1-1), Faroe–Moldova 1528987, Kazakhstan–Slovakia
1528986 (Kenzhebek, «banco», asistió los dos goles), France–Türkiye 1528982,
N. Ireland–Ukraine 1528975, Norway–Wales 1528972 (Moore, fuera de la hoja),
Mirassol–Atlético-MG 1492455, Chapecoense–Vasco 1492312 y Albania–Finland
1528963. **(b) Lista parcial y decidió el que faltaba, 6:** Croatia–Czech
1528985 (Majer hizo el 2-1), Belarus–Albania 1528980 (1 nombre contra 12
suplentes), Nacional–Albion 1649060 (el que tiró el córner del 1-1),
JPII–Garcilaso 1549559, Montenegro–Latvia 1545613 (rama de sostener) e
Italy–France 1528960 (`siLeEmpatan`). **(c) Once tardío, 6, no se cobran:**
Wanderers 1649063, Millonarios 1549871, Llaneros 1549870, Cerro Largo 1649056,
Tarancón 1644379 y Amorebieta 1644335; piden escribir «probable». La regla
estaba escrita y no cambió la conducta: falta que el texto nombre la fuente.

**T1 · 66, línea 667. Dos reemplazos.**

Primer reemplazo. Donde dice «Llevar como insumo del TDE los goles y
asistencias de suplentes en la temporada y los delanteros del banco del ultimo
once esta aprobado y pendiente de la app; hasta entonces sale de la
investigacion, con fuente.», va:

> **La lista es `bancoProbable` *(v0.1.27)*:** `GET …/tde/{id}` →
> `bancoProbable.{a|b}`, la misma que leen el B5 del EFE y el `bancoOfensivo`
> del DTP. No se arma de memoria ni de la previa. Un nombre que no esté en la
> lista entra solo con fuente y declarado como agregado.

Segundo reemplazo. Donde dice «Antes del once oficial es «probable» y se
escribe asi (si el EFE trae el banco por rol en B5, es esa lista); con el
once, se reescribe en el modo `rehacer` con los suplentes reales, y **un
nombre que sale titular deja de ser banco**», va:

> Con `fuente: probable` la rama la escribe «probable»; con `fuente: hoja`
> es la hoja. **La rama copia la lista entera, en una línea, por rol y sin el
> arquero suplente**, no una selección: decide el que no se nombró *(D1)*.
> Va en cada rama donde ese banco puede entrar: el del rival en
> `siMarcaPrimero`, `siLeEmpatan`, `siIguala` y `siExpulsion.propia`; el
> propio en las ramas que persiguen. Con el once, el `rehacer` reescribe la
> lista y **un nombre que sale titular deja de ser banco**.

Los casos entre paréntesis que siguen en esa línea se conservan.

- **Historial:** los 22 partidos de arriba.
- **Lo tumbaría:** que, con la lista entera, siga decidiendo un suplente que
  la rama no nombraba.

## 2. `ventajaPorFuerza` en la rama de ventaja (66) — APROBADO EL 10/11

**Qué dice hoy.** La 66 manda leer `referencias.ventajaPorMinuto` completa.
La fuerza previa no aparece.

**Qué pasó.** Estudio A del 10/11 (firme): con 1 de ventaja al descanso no
gana el 47 % de los que tenían < 35 % de probabilidad previa y el 9 % de los
de 75 %+ (53.108 partidos, igual de local o de visita). Esta semana, 15
lecciones citan la referencia del minuto y se cumple siempre por el lado de
«no gana» (Defensor–Peñarol 1649062, Cerro Largo 1649056, Once Caldas–Nacional
1648691, Tarancón 1644379…). La partición por fuerza no se puede hacer con la
prosa.

**Dónde está el dato.** `ventajaPorFuerza` existe en el bloque `desconfianza`
del parte (`backend/analisis/desconfianza.py`), que se calcula al leer el
parte, **después** de depositar. No está en `GET …/tde/{id}`, que es lo que
lee quien escribe la rama (A1).

**T2 · 66, sub-ítem nuevo después de la línea 665 («La referencia se lee completa…»):**

> - **La referencia también se parte por la fuerza *(v0.1.27, aprobado el
>   10/11/2026)*.** `GET …/tde/{id}` → `referencias.ventajaPorFuerza.{a|b}`
>   da cuánto **no gana** el que marca primero con uno y con dos de ventaja,
>   según su probabilidad previa sin margen. Los tramos son cinco: < 35 ·
>   35-48 · 48-60 · 60-75 · 75+ %.
>
>   La nota de `siMarcaPrimero` cita las dos referencias, cada una con su
>   fuente: el **minuto** (`ventajaPorMinuto`, nuestra base) y la **fuerza**
>   (`ventajaPorFuerza`, ventaja al descanso en ligas europeas). No se
>   multiplican ni se promedian: son dos cortes de la misma pregunta. No se
>   copian a mano ni se recalculan. La línea del empate va igual (44 (a)).

- **Historial:** la tabla A (`ESTUDIO_ECHADOS_2026-11.md` §9) y las 15
  lecciones.
- **Lo tumbaría:** que, con 100+ ventajas de nuestra base, el «no gana»
  observado por tramo de fuerza no siga el orden de la tabla.

## 3. El desenlace de la ventaja lo pone la fuerza; la tipología describe la vía (66, 44 (b)) — APROBADO EL 10/11

**Qué dice hoy.** La línea 669 prohíbe condicionar la referencia a la
tipología. No dice qué **sí** dice la tipología.

**Qué pasó.** Estudio E del 10/11: la tipología de la rama no separó quién
pierde la ventaja (17,6 % contra 17,5 %; 37 perdidas, 157 sostenidas). Esta
semana tampoco: sostuvieron con `ECHADA-VOL` o «en su plan» Real Potosí
1649149, N. Ireland 1528975, Amorebieta 1644335, Juventud 1649433, Albania
1528980 y Medellín 1549863; con la misma tipología la perdió Cyprus 1528959, y
con «sigue atacando» Torque 1649057 (2-0 a 2-2) y France 1528960 (1-0 a 1-3).
Ninguna lección lo contradice.

**T3 · 66, sub-ítem nuevo después de T2:**

> - **El desenlace de la rama de ventaja lo pone la fuerza; la tipología
>   describe la vía *(v0.1.27, aprobado el 10/11/2026)*.**
>   `ECHADA-VOL`, «en su plan» y «sigue atacando» dicen **por dónde** llegaría
>   el empate (el banco del rival, la contra, la pelota parada); **cuánto**
>   lo dicen las dos referencias. La nota no escribe «administra, así que no
>   se lo empatan» ni «sigue atacando, así que amplía». La tipología se sigue
>   eligiendo con su motivo (44 (b)).

Y en la **44 (b), línea 576**, al final («…no la echada.»):

> El desenlace de esa rama lo dan las referencias de la 66, no la tipología.

- **Historial:** el estudio E y los 9 partidos de arriba.
- **Lo tumbaría:** que, con la fuerza fija, la tipología separe en una
  medición con n ≥ 30 por tipología.

## 4. La plantilla de `siExpulsion`, para los dos lados (16, 44 (d)) — ACLARACIÓN

**Qué dice hoy.** La 16 pide `propia` y `rival` (línea 518); para `propia`,
la ventana desde la roja y el régimen hasta el final (519) y la vía de gol
propia (520). Para `rival`, nada de eso, y en ningún lado las tres cuentas del
marcador.

**Qué pasó (4 partidos, `mal_aplicada`).** Spain–England 1528984 (England):
sin la línea «ganando», que fue la que se dio (roja al 63' con 3-0, dos goles
en 12'). Montenegro–Latvia 1545613 (Montenegro): sin la vía de gol propia; con
diez desde el 57' y 0-0 siguió cargando y metió dos. Pereira–América 1549872
(Pereira): sin ventana desde la roja; con «roja +15» el gol del 60' caía
adentro. Danubio–Liverpool 1649061 (Danubio): la ventana de `rival` en la
nota; los goles, a los 17 y 19 minutos, dentro del régimen. Se suma
Kosovo–Israel 1528971 (Israel): con uno más, «no administra» se cumplió en los
cambios y no en la amenaza (6 remates, 0,35 de xG).

**T4 · 16, sub-ítem nuevo después de la línea 518 («`siExpulsion` declara los dos lados…»):**

> - **La plantilla de `siExpulsion` *(v0.1.27)*.** `propia` y `rival` llevan
>   lo mismo:
>   1. **las tres cuentas del marcador** en la nota (ganando, empatando y
>      perdiendo), una línea cada una aunque alguna parezca improbable;
>   2. **la ventana en su campo** (`ventana`: «desde la roja +15») y el
>      régimen hasta el final, o hasta el 120 si hay prórroga;
>   3. en `propia`, **la vía de gol propia** del que queda con diez: contra,
>      pelota parada, o seguir cargando si necesita ganar;
>   4. en `rival`, **quién queda de seguro** con el equipo volcado (63).
>
>   En `rival`, «no administra» se comprueba por la amenaza, no por los
>   cambios ni por lo que declara el DT (44 (b)). La v0.1.26 lo pedía solo
>   para `propia`.

- **Historial:** los cinco partidos.
- **Lo tumbaría:** que, con la plantilla completa, las ramas de expulsión
  sigan sin describir el tramo jugado. Ahí ya sería un problema de regla.

## 5. La pieza del seguro en las ramas que no persiguen (63) — CANDIDATO DE LA v0.1.26 → TEXTO

**Qué dice hoy (línea 635).** La pieza del `sob2` se nombra en la rama que
persigue y en la base `SOB`. La rama de ventaja quedó como candidato, con
Barcelona–Atlético y Alianza Lima–Los Chankas.

**Qué pasó.** Dentro de las ramas que persiguen, la 63 se sostiene 12 de 15.
Fuera de ellas: **Danubio–Liverpool 1649061:a** (ventaja con superioridad):
Millán, «solo delante de los centrales», salió al 68' y con 1-0 y uno más
concedió dos en 82'-84'. **Deportivo Cali–Tolima 1549867:a** (superioridad,
empatado): cargó como decía la rama y concedió el 1-2 a los 4', sin seguro
nombrado. **Belgium–Italy 1528983:b** (`siLeEmpatan` tras ventaja temprana,
`sob2` = 1, «Tonali solo»): concedió a 7' del empate, «pesa aunque no
persiga». Lithuania 1528989:a:5 (2-0, piezas amonestadas) no tiene fuente: se
anota y no se cuenta. Estonia 1528988:a:2: la pieza nombrada era suplente en
la hoja. **Tamaño, con honestidad:** de rama de ventaja pura hay 1 firme
(Danubio) más los 2 de la v0.1.26; en las tres ramas que no persiguen, 3
firmes ahora y 5 en total. Es nombrar, no puntuar: D3 deja elegir.

**T5 · 63, sub-ítem nuevo después de la línea 635 («La pieza que sostiene el seguro se nombra…»):**

> - **También en las ramas que no persiguen *(v0.1.27)*.** La pieza que
>   sostiene el seguro se nombra también en la rama de ventaja (con `sob2` ≥
>   0.5 o «sigue atacando»), en `siLeEmpatan` y en `siExpulsion.rival` (el
>   que carga con uno más). El cierre anota su salida igual que arriba. No cambia el `sob2` ni el
>   cobro. **Con el once oficial, la pieza está en el once**: si la hoja la
>   pone en el banco, se nombra otra o se declara la rama sin pieza.

- **Historial:** Danubio, Cali, Italy, Lithuania, Estonia y los dos de la
  v0.1.26.
- **Lo tumbaría:** que la salida de la pieza no se asocie con concesión en
  estas ramas (se mide con A4), o que nadie la use en el cierre.

## 6. `SOB1` dice la necesidad, no el régimen (18) — ACLARACIÓN (el peso, a C1)

**Qué dice hoy.** `SOB1` sale de la tabla (18). Con `SOB1` = 1, el régimen
arranca en el minuto 0 (56). La nota de la base `SOB` del obligado se escribe
como régimen firme.

**Qué pasó (5 partidos, `regla_fallo` del régimen).** Iceland–Luxembourg
1545617:b: perdiendo desde el 25', 0 remates en el área y el primer cambio al
66', lateral por lateral. Croatia–Czech 1528985:b: con 0-1 desde el 2', hondo,
40 % de pelota y 8 remates. Belarus–Albania 1528980:a: la pelota y las
ocasiones fueron del rival. Central Español 1649058:a: salió 5-4-1 y Boston
River remató 4 veces en 90'. Serbia–Germany 1528965:a: 20 % de pelota y 5
remates. Además England–Croatia 1528962:b: el rival le apagó el régimen
administrando. **Ojo:** 4 de los 5 concedieron igual, por otra vía. No dice
«el obligado no se expone»: dice que la nota no afirma un régimen que depende
del once. El cobro no cambia (61).

**T6 · 18, línea 528, al final («…fue leer **otro** relato y llamarlo corrección.»):**

> **`SOB1` dice la necesidad, no el régimen *(v0.1.27)*.** `SOB1` = 1 por la
> tabla no se toca, y el inicio sigue la 56. La nota de la base `SOB` y de la
> rama del obligado escribe el régimen **condicionado al sistema del once y a
> quién tendrá la pelota** (52).
>
> - Con línea de cinco, bloque bajo de plan o un rival que le quita la
>   pelota, la necesidad puede no producir exposición. La nota lo dice con el
>   hecho que la activaría: «se expone si entra el segundo 9 o suben los dos
>   laterales».
> - Si el sistema sale del once oficial, se revisa al rehacer (65).

- **Historial:** los seis partidos.
- **Lo tumbaría:** que los obligados por tabla con línea de cinco, o con un
  rival que domina la pelota, se expongan como el resto. Para medirlo hace
  falta el grid y el volumen por tramo.

## 7. Disciplina 63: la herencia del `sob2` de rama ya está hecha — ACLARACIÓN

**Qué dice hoy (línea 636):** «Mientras la app no lo haga, lo copia el
analista *(cuando el mantenimiento lo implemente, esta ultima oracion se
borra)*.»

**Qué hay en el código (DEUDA 28):** `dtp_cowork.herencia_tde` da
`SOB2persiguiendo`, `parte.heredar_ramas` lo aplica a las ramas que empujan y
`HERENCIA-DTP` nombra la rama.

**T7 · reemplazo de esa oración:**

> La app lo aplica al depositar y `HERENCIA-DTP` nombra la rama si el
> declarado difiere.

## 8. Núcleo — APROBADO (03/11 y 10/11), medido sobre la v0.1.26 de hoy

**Tamaño.** El `SKILL.md` pesa 216 KB, ≈ 54 K tokens (caracteres / 4). La
propuesta del núcleo midió 50,9 K sobre la v0.1.25.

**Pasa a `references/HISTORIAL.md`, tal cual:**

| Archivo · líneas | Qué es | Tokens |
|---|---|---:|
| `SKILL.md` 8-15 | «Dónde vive el registro canónico» (lo operativo queda en el PASO 0: N1) | 0,3 K |
| `SKILL.md` 16-303 | notas de versión v0.1.26 … v0.1.1 (26 bloques) | 24,2 K |
| `SKILL.md` 671-768 | EL REGISTRO: esquema de 51 columnas, `pre_rubrica`, la trampa de `IE_recomputado_esquema6`, numeraciones ausentes, filtro de frecuencia y TDE-026 | 3,0 K |
| `INDICE_IE.md` 3-27 | sus notas de versión v0.1.19 … v0.1.1 | 1,9 K |
| esta propuesta | la nota T0 y los casos de T1-T7 | — |

Resultado: el `SKILL.md` queda en ≈ 26,5 K, más ≈ 1,5 K de textos nuevos,
**≈ 28 K**.

**Arriba, en lugar de las líneas 8-303:**

> Versión vigente: **v0.1.27 (<fecha de subida>)**. Las notas de cada
> versión, los casos que motivaron cada regla y el esquema del registro están
> en `references/HISTORIAL.md`: **no hace falta leerlo para analizar un
> partido**; se lee al revisar el skill.

**Lo que vive solo en el historial y sube al cuerpo** (`NUCLEO_SKILLS_propuesta.md`
§2.1, con lo que se decidió el 10/11):

**N1 · PASO 0, punto 4 (línea 347), reemplazo.** Es T10 y la duda 3, ya
aprobada:

> 4. `assets/casos/registro.csv` — **no se lee entero**: para `F3` y los
>    antecedentes, buscar con Grep el nombre de los dos equipos. La copia
>    empaquetada es una instantánea: antes de usarla se compara su sha256 con
>    el fijado en `scripts/calibrar-tde.py` y, si difieren, manda la del repo
>    y se dice.

**N2 · línea 563 («Desfase de documentacion declarado…»): se reemplaza por
las disciplinas 34-39 en su hueco** *(D4)*. Los textos son literales del
changelog salvo donde se marca:

> 34. **Con dos o más indicadores abiertos, la caja publica el rango
>     conjunto** (mínimo y máximo combinatorios de todos los abiertos a la
>     vez), no un rango por indicador *(v0.1.13; vigente por decisión del
>     10/11)*.
> 35. *Derogada por la 55 (decisión del 10/11):* sin XI confirmado, `F1` es
>     nivel de dato C, no `sin dato`. El texto de la v0.1.13 queda en el
>     historial.
> 36. **Cuando `F1 = 0` por rotación de 3 o más titulares, el output declara
>     que el descuento físico se está pagando en coordinación** y que el
>     módulo no lo representa *(v0.1.14)*.
> 37. **La ventana modal se declara para la vía del índice que manda**
>     (PASO 3: ISE > IE → `SOB`), no para el tipo que sugiera la rúbrica de
>     tipos. La doble ventana `SOB` sigue su propio criterio (`INDICE_IE.md`,
>     v0.1.15) *(v0.1.14, reescrita en la v0.1.27 sin el riesgo compuesto,
>     suspendido en la v0.1.20; D4 (b′))*.
> 38. **El sesgo tardío es una propiedad de la serie:** su corrección solo
>     entra como cambio de regla autorizado al alcanzar el umbral, nunca como
>     ajuste de una fila *(v0.1.14)*.
> 39. **Todo caso `RETRO` declara su traza `PRE`:** los indicadores que no
>     habrían sido puntuables antes del partido y con qué valor entraron
>     *(v0.1.15)*.

**N3 · lo demás.** Fila `F3` de `INDICE_IE.md` (línea 120): se agrega «sin
datos de impacto de banco en la temporada, `F3` es `sin dato` y entra en la
caja conjunta, también fuera de la fecha 1» (T8). Línea 472 de `INDICE_IE.md`:
«mismo criterio que la disciplina 37» pasa a «(v0.1.15)». «No bajar `P(gol)`
con ejecutor de penales» (T7 del núcleo): caída con la v0.1.20 (decisión del
10/11), solo en el historial. T9 del núcleo («solo hacia más medición») no se
copia: ya está en la última frase de la 27 (línea 549, «hacia más exposición,
nunca hacia menos»). La guardia `backend/test_nucleo_skills.py` (§5 del
núcleo) va con el traslado, fuera del skill.

## 9. Tres frases del núcleo contradichas por reglas posteriores — ACLARACIÓN

La propuesta del núcleo las dejó a la vista sin tocarlas. Corregirlas no
cambia ninguna regla vigente *(D5)*: alinea texto viejo con la regla que
manda.

- **N4 · Integración, línea 774.** Se borra «corregir la localía hacia arriba
  en Sudamérica antes de comparar μ», porque la 47 y la FICHA MÍNIMA lo
  prohíben desde la v0.1.18. «Tres cuidados» pasa a «Dos cuidados».
- **N5 · LA TESIS, línea 335.** «La lectura que se comunica es el riesgo
  compuesto» pasa a: «La lectura que se comunica es el IE y el ISE con sus
  bandas ordinales y el mecanismo; el riesgo compuesto está suspendido desde
  la v0.1.20 (PASO 2)».
- **N6 · «Mapeo de IE a probabilidad» de `INDICE_IE.md` (líneas 355-364).**
  Arriba de la tabla va la misma marca que ya tiene `P(sobreexposición)`:
  «SUSPENDIDO en v0.1.20: no se emite; queda como historia de la escala».

---

## Candidatos a medir (no entran)

| N.º | Qué | n de esta semana | Qué haría falta |
|---|---|---|---|
| C1 | **Peso de `SOB1` de tabla sin un hecho de hoy** (punto 6) | 5 partidos sin el régimen; 4 concedieron igual | ramas `SOB` del obligado por tabla, partidas por sistema del once (línea de 5 o no, desde el grid) y posesión prevista, contra la concesión; n ≥ 30 por lado. Es un peso: backtest y vectores, nunca a mano |
| C2 | **Superioridad según el marcador:** desdoblar `siExpulsion.rival` como se hizo con la propia en la v0.1.21 | **Ganando:** 3 cargaron (Danubio 1649061, España 1528961, América 1549872) y 2 administraron cambiando delantero por medio (Cerro 1649059, Monterrey 1550951). **Perdiendo o empatado:** cargaron los 4 (España 1528984, ADT 1549558, América 1648690, Cali 1549867). Israel 1528971: hizo los cambios sin generar amenaza | tramos con uno más por marcador y minuto: goles a favor y en contra, y cambios por posición de quien entra y sale (A2); n ≥ 30 ganando |
| C3 | **Roja propia ganando: tampoco asegura el punto** | Concedieron 3 de los que tenían la roja yendo ganando: Juventud 1649433 (a 3' de la roja del 78'), Inter Bogotá 1648690 (roja al 11', se lo dieron vuelta) y England 1528984 (3-0 → 3-2). También concedió Cusco 1549558, que se puso adelante ya con diez (87'). Sostuvo Junior 1549868, contra un rival sin banco. La referencia 11 de 12 de la v0.1.25 es **empatando** | la tabla de concesión tras roja propia por marcador y minuto, aprobada en la v0.1.25 y pendiente (A2). La tasa ganando va al lado como referencia, no como peso |
| C4 | **Ventana desde el cambio ofensivo** (candidato de la v0.1.26) | 4 explícitos: Cali 1549867, Cúcuta–Jaguares 1549866, Lithuania 1528989 y England 1528962 (sin gol). 5 implícitos: Georgia 1528973, Cerro Largo 1649056, Millonarios 1549871, Norway 1528972 y Mijas 1644362. **Sin denominador:** solo se anotan los cambios seguidos de gol | todos los cambios ofensivos con su minuto, y la tasa de gol en los N' siguientes contra la del mismo reloj sin cambio (A3); n ≥ 30 por reloj |
| C5 | **Huecos de `S1`** | Suplente que entra y ve la roja: 2 (Serbia 1528965, Juventud 1649433). El estudio contaba 3, pero en Pereira Mosquera era titular fuera del once de referencia. Uno cada uno: roja al arquero titular (Querétaro 1550951), conducta violenta sin pelota (Maldonado 1649059), roja del DT (Pereira 1549872) | un casillero nuevo es un número: primero el insumo (A5). El hueco del suplente ya está declarado en la 16 |
| C6 | **Matices de 1-2 casos** | La vía del empate también son los titulares del rival que domina: 2 (Wanderers 1649063, Armenia–Cyprus 1528959). Doble pivote, se nombran las dos piezas: 1 (Chapecoense 1492312). Con `sob2` = 1 heredado, el seguro está roto desde el gol: 1 (Portugal 1528974). El obligado con 2-0 temprano administró con cambios defensivos y lo empataron: 1 (Torque 1649057) | el tercer caso ciego de cada uno |

**Siguen sin material:** la SOB de la hora con 0-0 y el empate útil (el único
caso nuevo, Maldonado 1649059, va en la dirección contraria al criterio de
entrada); la lista de la 44 (f) en `siLeEmpatan` (2: Tarancón 1644379 y
Millonarios–Tolima); el ISE agravado con roja propia perdiendo (2 a 2:
Liverpool 1649061 y Pereira a favor, Comerciantes 1549557 y Finland 1528963 en
contra); el defecto por quien persigue (1 explícito, Anaitasuna 1644336, y
requiere A6); el «doble golpe» (Danubio 1649061 suma uno, sin medición).

**Se cierran sin texto:** 61 (47 de 47), 65 (`abierto` por defecto, 29 de 29),
la referencia de la 66 cuando se cita (15 de 15), 44 (b) (39 de 41, casi todos
favoritos claros: sesgo de selección ya declarado), la tipología apoyada en la
identidad o en un antecedente que no coincide (4 incumplimientos de regla ya
escrita: UTC 1549556, Faroe 1528987, Central Español 1649058, Slovenia 1545654)
y la paridad restablecida de la 16 (Once Caldas–Nacional 1648691).

## Para la app (solo lo que falta; verificado en `backend/` el 17/11)

| N.º | Qué | Por qué |
|---|---|---|
| A1 | `referencias.ventajaPorFuerza` en `GET …/tde/{id}`, reusando `desconfianza.ventaja_por_fuerza` con el 1X2 sin margen del fixture. Contrato primero y su test | Hoy solo está en el bloque `desconfianza` del parte, que se calcula después del depósito. Bloquea T2 (D2). Aparte sigue pendiente la tabla A por minuto con `sad.db` |
| A2 | Referencia de expulsiones por marcador y minuto, de los dos lados. Lado propio: concesión tras la roja (aprobada en la v0.1.25, línea 522). Lado rival: goles y cambios con uno más | Mide C2, C3 y el ISE agravado |
| A3 | Por gol concedido, los minutos desde el último cambio ofensivo de cada lado, con denominador | Punto 10 de la v0.1.26, sin hacer. Mide C4 |
| A4 | `piezaSeguro` opcional en `RamaReasignacion` y en la base. El veredicto marca el minuto en que salió (cambio o roja), con `backend/identidad.py` | Punto 4 de la v0.1.26, sin hacer. Mide T5 y C6 |
| A5 | Insumos de `S1` en `tde/{id}`: rojas del equipo en la temporada, amarillas de zaga, pivote y 9, y rojas de los suplentes de `bancoProbable` | Punto 11 de la v0.1.26, sin hacer (`S1` sigue en `noCalculables`). Czech–Spain 1528961 quedó sin dato con dos rojas checas en la base |
| A6 | Quién persigue por `μ_partido` en cada tramo | Requisito del defecto por quien persigue; pendiente desde la v0.1.25 |
| A7 | Textos viejos: `tde.f2.puedeSubir` dice «súbelo a mano», contra la 21 decidida el 10/11; `lecciones.py` (línea 890) dice «ISE de rama ≥ 7 → se_rompe». Y anotar la v0.1.27 en `SUBIDA_VERSION` | Sigue de la v0.1.26 |

**No se pide** un aviso del recibo por las tres cuentas de `siExpulsion`:
habría que leer la prosa, y lo medible (la ventana) ya tiene aviso (1420).
**Opcional:** si el mantenimiento hace el aviso «ningún nombre de
`bancoProbable`» que pide el DTP v1.9 para sus `viasGol`, extenderlo a
`siMarcaPrimero`, `siLeEmpatan` y `siIguala`.

## Coherencia entre skills

Revisadas contra las propuestas de DTP v1.9, EFE v1.11 y sad-analysis v4.6
que ya están en `docs/revisiones/`.

| Cambio | Depende de | Qué hacer |
|---|---|---|
| 1 (banco) | **DTP v1.9** (`bancoOfensivo`, punto 7) y **EFE v1.11** (B5, punto 4): la misma `bancoProbable` | Las dos ya la nombran igual. `F3` hereda B5 (`INDICE_IE.md` l. 120): sin conflicto |
| 2 y 3 (fuerza) | **sad-analysis v4.6**: DESCONFIAR, el descarte y `ventajaPorFuerza` en `desconfianza` | La v4.6 dice que en `tde/{id}` «es del TDE»: es A1. El TDE no nombra la alerta. Subir juntas |
| 4 (`siExpulsion`) | **sad-analysis** lee la vía de gol propia de `siExpulsion.propia` | Mismo campo: sin cambio |
| 5 (pieza del seguro) | **DTP v1.9**, M3 («quién queda atrás» en todas las ramas), y 44 (b) T13 | Si el DTP nombra al que queda atrás en la rama de ventaja, es la misma pieza; si no coincide, manda el DTP y se dice |
| 6 (`SOB1` y el sistema) | **DTP v1.9**: posesión por rama, con la rama «arriba» separada | T6 toma de ahí «quién tendrá la pelota». **SOB2 y C1 siguen heredados del DTP** sin cambio; la clase y `c1Tde` las calcula el backend |
| 7 | 1056, ya en la app | Nada |
| 8 (núcleo) | Las cuatro versiones con núcleo y la misma guardia | La línea «Versión vigente» igual en las cuatro; `docs/skills/README.md` dice TDE v0.1.22 |

**Bloqueos para redactar: uno.** T2 necesita A1 (D2). Lo demás no depende de
otra propuesta.

## Qué NO se propone

- **Ningún número:** el peso de `SOB1` (C1), un casillero de `S1` (C5), el
  desdoble numérico de la superioridad y de la roja ganando (C2, C3), el
  inicio de la ventana desde el cambio (C4), el corte del 30' de la 66 ni los
  tramos de `ventajaPorFuerza`.
- **La alerta DESCONFIAR en el TDE:** es de sad-analysis.
- **Ninguna regla se afloja:** T3 no le quita a la 44 (b) la obligación de
  nombrar por qué un equipo administra.
- **Ni los candidatos de 1-2 casos, ni reetiquetar con Jev lo ya sellado.**

## Decisiones del usuario

| | Pregunta | (a) | (b) | Recomiendo |
|---|---|---|---|---|
| **D1** | El banco en la rama (punto 1) | la lista entera de `bancoProbable`, sin el arquero suplente, una línea por rama | solo los ofensivos por rol (delanteros, `lateral: true`, goles o asistencias desde el banco) + «resto: bancoProbable» | **(a)**: decidieron sin estar nombrados un medio (Majer), el que tiró un córner (S. Costa) y un lateral (Dimarco), y la API solo da G/D/M/F |
| **D2** | `ventajaPorFuerza` (punto 2) | la v0.1.27 sube cuando `tde/{id}` la traiga (A1) y el texto cita solo el campo | sube ya, con la tabla del descanso en una línea hasta que esté | **(a)**: el cambio es chico y la 66 pide no copiar números que da la app |
| **D3** | Pieza del seguro en las ramas que no persiguen (punto 5) | entra como texto | sigue candidato hasta 5 casos de rama de ventaja pura | **(a)**: 5 casos entre las tres ramas, no mueve números |
| **D4** | Disciplinas 34-39 (punto 8) | en su hueco numerado (N2), que resuelve las citas huérfanas | repartidas como decía el §3.3 del núcleo | **(a)**. Y **(b′)**: ¿la 37 reescrita **sin** la cláusula de cercanía? «A menos de 5 puntos» era de riesgo compuesto en % y no se traduce a IE/ISE sin inventar un umbral: **sí** |
| **D5** | Las tres frases contradichas (punto 9) | se corrigen ahora | se dejan con una nota | **(a)**: ninguna cambia una regla vigente |

## T0 · nota de versión (va directo a `references/HISTORIAL.md`)

> **v0.1.27 · <fecha de subida> — la rama toma el banco de la app y la
> ventaja de la fuerza.**
>
> Revisión desde el estudio del 17/11/2026: 276 lecciones `pendiente` de 81
> partidos del 10 al 16/11, ciegas `PRE` y escritas con la v0.1.26, en una
> semana con mayoría de selecciones. Ningún número se mueve. Primera versión
> con núcleo e historial.
>
> - **66:** el banco es `bancoProbable`, la lista entera, en cada rama donde
>   entra. La rama de ventaja cita también `ventajaPorFuerza`. El desenlace
>   lo pone la fuerza y la tipología describe la vía (aprobado el 10/11).
> - **16:** plantilla de `siExpulsion` para los dos lados.
> - **63:** la pieza del seguro también en las ramas que no persiguen, y la
>   herencia del `sob2` de rama ya la hace la app.
> - **18:** `SOB1` dice la necesidad, no el régimen.
> - **Núcleo:**
>   las disciplinas 34-39 en su hueco (la 35, derogada por la 55); el
>   registro se busca por equipo; la localía, LA TESIS y el mapeo, alineados
>   con la 47 y la v0.1.20.
> - **Candidatos, no aplicados:** el peso de `SOB1`, la superioridad y la
>   roja propia según el marcador, la ventana desde el cambio ofensivo, los
>   huecos de `S1` y los matices de un caso.

## Sesgos y límites

- **Una semana, en su mayoría de fecha FIFA.** Hubo onces tardíos y muchos
  favoritos claros, lo que infla los números de la 44 (b) y del banco.
- **Son conteos de lecciones, no tasas.** Quien cierra un partido nombra el
  skill sobre todo cuando algo falla. La clasificación sale de leer la prosa,
  no de `modoFallo`.
- **Los casos de la pieza del seguro y de la superioridad son 3-5 por
  lado.** Ninguno sostiene un número, y por eso lo numérico está todo en
  C1-C6.
