# Propuesta de revisión · `teorema-del-echado` v0.1.26 → v0.1.27

**Estado: PROPUESTA (17/11/2026), para aprobar punto por punto.** No se tocó
el skill, ni el código, ni otros docs. Se aplica **con el núcleo**
(`NUCLEO_SKILLS_propuesta.md`, aprobado con las cinco recomendaciones de
`RESUMEN_GENERACION_2026-11.md` §«El núcleo de los skills»): el changelog y los
casos pasan a `references/HISTORIAL.md`.

Fuentes:

- el estudio de las lecciones del 17/11 (`estudio_lecciones_2026-11-17/`:
  `README.md`, `estudio_teorema-del-echado.md`, `clasif_teorema-del-echado.json`);
- la prosa de las 276 lecciones `pendiente` (81 fixtures, partidos del 10 al
  16/11, todas ciegas PRE y escritas con la v0.1.26);
- lo aprobado el 10/11 para esta versión (`PENDIENTES.md`,
  `DESCONFIAR_propuesta.md`, puntos 4 y 5);
- el skill vigente (`SKILL.md` v0.1.26, 781 líneas, y `references/INDICE_IE.md`).

Las líneas citadas son las del `SKILL.md` vigente. Al insertar de abajo hacia
arriba no se corren.

## Resumen

- **Las reglas vigentes se sostienen.** 198 de 276 lecciones dicen que la
  regla se cumplió, aunque en 54 de ellas el lado falló. La 61 da 47 de 47,
  la 65 da 29 de 29 y la 44 (b) da 39 de 41.
- **La falla más repetida es de ejecución:** el banco escrito de memoria y no
  de la hoja (16 lecciones mal aplicadas y 6 de once tardío). La app ya lo
  resolvió hoy con `bancoProbable`. El texto solo tiene que nombrar esa
  fuente.
- **Entra lo aprobado el 10/11:** `ventajaPorFuerza` y «el desenlace de la
  rama de ventaja lo pone la fuerza; la tipología describe la vía». Las
  lecciones lo apoyan en lo cualitativo y no lo miden.
- **Del estudio entran tres textos:**
  - la plantilla completa de `siExpulsion` (4 partidos);
  - la pieza del seguro también en las ramas que no persiguen (3 partidos
    firmes, más 2 de la v0.1.26);
  - `SOB1` dice la necesidad, no el régimen (5 partidos).
- **Ningún número se mueve:** ni pesos, ni la fórmula del IE, del ISE ni del
  ISE de rama, ni compuertas, bandas o ventanas.
- **Seis candidatos siguen a medir.** Son los que tocan un número o tienen
  n chico: el peso de `SOB1`, la superioridad y la roja propia según el
  marcador, la ventana desde el cambio ofensivo y los huecos de `S1`.
- **El núcleo baja el `SKILL.md` de ≈ 54 K a ≈ 28 K tokens.** Hay tres
  contradicciones viejas del núcleo para resolver (punto 9).

## Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos que lo sostienen | Recomendación |
|---|---|---|---|---|
| 1 | El banco sale de `bancoProbable`, la lista entera, en cada rama donde entra (66) | aclaración (app hecha) | 16 mal aplicadas en 16 partidos + 6 de once tardío | aprobar · **D1** |
| 2 | La rama de ventaja cita `ventajaPorFuerza` además de `ventajaPorMinuto` (66) | aprobado antes (10/11) + app | estudio de 53.108 partidos; 15 lecciones citan la del minuto, todas por el lado de «no gana» | aprobar · **D2** |
| 3 | El desenlace de la ventaja lo pone la fuerza; la tipología describe la vía (66, 44 (b)) | aprobado antes (10/11) | 37 contra 157 (01-09/11); acá, sin contraejemplos | aprobar |
| 4 | Plantilla de `siExpulsion` para los dos lados: tres cuentas del marcador, ventana en su campo y vía propia o seguro (16) | aclaración | 4 partidos (+1 de amenaza) | aprobar |
| 5 | La pieza del seguro se nombra también en las ramas que no persiguen (63) | candidato v0.1.26 → texto | 3 firmes + 2 de la v0.1.26; solo 1 de ventaja pura | aprobar · **D3** |
| 6 | `SOB1` = 1 por la tabla dice la necesidad, no el régimen: la nota se escribe condicionada al once y al sistema (18) | aclaración (el peso, candidato) | 5 partidos | aprobar |
| 7 | 63: se borra «mientras la app no lo haga» (la herencia del `sob2` de rama ya está hecha) | aclaración (app hecha) | — | aprobar |
| 8 | Núcleo: el changelog y el registro pasan al historial, y las disciplinas 34-39 suben al cuerpo | aprobado antes (03/11 + 10/11) | — | aprobar · **D4** |
| 9 | Tres frases del núcleo contradichas por reglas posteriores: la localía (774), LA TESIS (335) y el mapeo IE→P de `INDICE_IE.md` | aclaración | — | aprobar · **D5** |
| C1-C6 | Candidatos a medir (ver su sección) | candidato a medir | n de 1 a 6 | no entran |
| A1-A7 | Para la app | app | — | después de aprobar |

---

## Lo que ya hizo la app hoy (17/11) y no se pide de nuevo

- **`bancoProbable`** está en `GET /analisis/cowork/tde/{id}`, `dtp/{id}` y
  `f1/{id}` (`backend/analisis/banco.py`). Es una sola lista:
  - con el once y la banca completa, `fuente: hoja`: todos los suplentes
    publicados, sin ningún titular;
  - antes, `fuente: probable`: los que entraron seguido o hicieron goles o
    asistencias entrando en los últimos 10.

  Cada jugador lleva su `posicion`, `lateral`, `golesDesdeBanco`,
  `asistenciasDesdeBanco` y `titularHabitual`.
- **El rehacer** (`parte.REHACER_POR`) ahora también entra con:
  - **FUERA-EN-LA-HOJA**, que incluye una rama del TDE que nombra de banco a
    un titular (`dtpBanco`) o a un no convocado (`noConvocado`);
  - **ONCE-SIN-FILA-F1**;
  - **EFE-RECOMPUTO-PENDIENTE**.
- **Jev:** la etiqueta `lectura_efe` pasa a `lectura` del skill del dossier
  (PR #562). En el TDE era la «regla del propio skill mal aplicada»: 7 de 107
  hablaban del EFE.
- **La ventana de una rama escrita en la nota y no en `ventana`** ya tiene
  aviso en el recibo (`parte.ramas_con_ventana_en_la_nota`, incidencia 1420).

---

## 1. El banco sale de `bancoProbable` (disciplina 66) — ACLARACIÓN

**Qué dice hoy (línea 667).**

- Que llevar los goles y las asistencias de los suplentes como insumo está
  «aprobado y pendiente de la app; hasta entonces sale de la investigacion».
- Que antes del once la lista es «probable» y «si el EFE trae el banco por rol
  en B5, es esa lista».
- Que con el once se reescribe y que un titular deja de ser banco.

**Qué pasó.**

- **(a) Un titular nombrado como banco, con el once ya capturado (10 partidos):**
  - Lithuania–Liechtenstein 1528989;
  - Estonia–Bulgaria 1528988: Kovachev, «banco», hizo el 1-1;
  - Faroe–Moldova 1528987;
  - Kazakhstan–Slovakia 1528986: Kenzhebek, «banco», asistió los dos goles;
  - France–Türkiye 1528982;
  - N. Ireland–Ukraine 1528975;
  - Norway–Wales 1528972: Moore, fuera de la hoja;
  - Mirassol–Atlético-MG 1492455;
  - Chapecoense–Vasco 1492312;
  - Albania–Finland 1528963.
- **(b) La lista era una selección, y decidió el que faltaba (6 partidos):**
  - Croatia–Czech 1528985: Majer, que no estaba en la rama, hizo el 2-1;
  - Belarus–Albania 1528980: un nombre contra 12 suplentes;
  - Nacional–Albion 1649060: el que tiró el córner del 1-1 no estaba nombrado;
  - JPII–Garcilaso 1549559;
  - Montenegro–Latvia 1545613: faltaba en la rama de sostener;
  - Italy–France 1528960: faltaba en `siLeEmpatan`.
- **(c) Once tardío, que no se cobra (6 partidos):** Wanderers 1649063,
  Millonarios 1549871, Llaneros 1549870, Cerro Largo 1649056, Tarancón 1644379
  y Amorebieta 1644335. Piden escribir «probable».

Repetir la regla en la v0.1.26 no cambió la conducta. La fuente ya existe:
falta que el texto la nombre y deje de remitir al B5 del EFE.

**T1 · 66, línea 667. Dos reemplazos.**

Donde dice:

> «Llevar como insumo del TDE los goles y asistencias de suplentes en la
> temporada y los delanteros del banco del ultimo once esta aprobado y
> pendiente de la app; hasta entonces sale de la investigacion, con fuente.»

va:

> **La lista es `bancoProbable` *(v0.1.27)*:** `GET …/tde/{id}` →
> `bancoProbable.{a|b}`, la misma que leen el B5 del EFE y el `bancoOfensivo`
> del DTP. No se arma de memoria ni de la previa. Un nombre que no está en la
> lista entra solo con fuente y declarado como agregado.

Y donde dice:

> «Antes del once oficial es «probable» y se escribe asi (si el EFE trae el
> banco por rol en B5, es esa lista); con el once, se reescribe en el modo
> `rehacer` con los suplentes reales, y **un nombre que sale titular deja de
> ser banco**»

va:

> Con `fuente: probable` la rama la escribe «probable»; con `fuente: hoja` es
> la hoja. **La rama copia la lista entera, por rol y sin el arquero
> suplente**, en una línea, no una selección *(D1)*: decide el que no se
> nombró. Va en cada rama donde ese banco puede entrar:
>
> - el del rival en `siMarcaPrimero`, `siLeEmpatan`, `siIguala` y
>   `siExpulsion.propia`;
> - el propio en las ramas que persiguen.
>
> Con el once, el `rehacer` reescribe la lista, y **un nombre que sale
> titular deja de ser banco**.

Los casos entre paréntesis que siguen en la línea se conservan.

- **Historial:** los 22 partidos de arriba.
- **Lo tumbaría:** que en la próxima cohorte siga apareciendo un titular como
  banco con `fuente: hoja` a la vista. Eso ya no sería un problema de texto:
  lo frena FUERA-EN-LA-HOJA y el rehacer. O que copiar la lista entera no
  baje los casos (b), es decir, que siga decidiendo un suplente que la rama no
  nombraba.

## 2. `ventajaPorFuerza` en la rama de ventaja (66) — APROBADO EL 10/11

**Qué dice hoy.**

- La 66 manda leer `referencias.ventajaPorMinuto` completa: «no pierde nueve
  de cada diez, no gana uno de cada cuatro».
- La fuerza previa no aparece en ningún lado.

**Qué pasó.**

- **El estudio del 10/11 (A, firme):** con 1 de ventaja al descanso, no gana
  el 47 % de los que tenían < 35 % de probabilidad previa y el 9 % de los que
  tenían 75 %+. Son 53.108 partidos, con el mismo resultado de local y de
  visita y en las dos mitades de la serie.
- **Esta semana:** 15 lecciones citan la referencia del minuto y se cumple,
  siempre por el lado de «no gana». Ejemplos: Defensor–Peñarol 1649062,
  Cerro Largo 1649056, Once Caldas–Nacional 1648691 y Tarancón 1644379.
- **Lo que no se puede hacer con la prosa:** partir por la probabilidad
  previa.

**Dónde está el dato hoy.** `ventajaPorFuerza` existe en el bloque
`desconfianza` del parte (`backend/analisis/desconfianza.py`). Ese bloque se
calcula al leer el parte, o sea **después** de depositar. En
`GET …/tde/{id}`, que es lo que lee quien escribe la rama, no está (A1).

**T2 · 66, sub-ítem nuevo después de la línea 665 («La referencia se lee completa…»):**

> - **La referencia también se parte por la fuerza *(v0.1.27, aprobado el
>   10/11/2026)*.** `GET …/tde/{id}` → `referencias.ventajaPorFuerza.{a|b}`
>   da cuánto **no gana** el que marca primero con uno y con dos de ventaja,
>   según su probabilidad previa sin margen. Son cinco tramos: < 35 ·
>   35-48 · 48-60 · 60-75 · 75+ %.
>   - La nota de `siMarcaPrimero` cita las dos referencias, cada una con su
>     fuente: el **minuto** (`ventajaPorMinuto`, de nuestra base) y la
>     **fuerza** (`ventajaPorFuerza`, la ventaja al descanso en ligas
>     europeas).
>   - No se multiplican ni se promedian: son dos cortes de la misma pregunta.
>   - No se copian a mano ni se recalculan (punto de arriba).
>   - Con cualquiera de las dos, la línea del empate se escribe igual (44 (a)).

- **Historial:** la tabla A de `ESTUDIO_ECHADOS_2026-11.md` §9 y las 15
  lecciones.
- **Lo tumbaría:** que con 100+ ventajas cerradas, el «no gana» observado por
  tramo de fuerza en nuestra base no siga el orden de la tabla. La app lo
  puede medir cuando la tenga por minuto (A1).

## 3. El desenlace de la ventaja lo pone la fuerza; la tipología describe la vía (66 y 44 (b)) — APROBADO EL 10/11

**Qué dice hoy.**

- La línea 669 prohíbe condicionar la referencia a la tipología: «es
  selección: el favorito escribe SOB».
- No dice qué **sí** dice la tipología en la rama de ventaja.

**Qué pasó.**

- **Estudio E del 10/11:** la tipología de la rama no separó quién pierde la
  ventaja (17,6 % contra 17,5 %, con 37 perdidas y 157 sostenidas).
- **Esta semana, la tipología tampoco separa dentro de la muestra:**
  - sostuvieron con `ECHADA-VOL` o «en su plan»: Real Potosí 1649149,
    N. Ireland 1528975, Amorebieta 1644335, Juventud 1649433, Albania 1528980
    y Medellín 1549863;
  - con esa misma tipología perdió la ventaja Cyprus 1528959;
  - con «sigue atacando» la perdieron Torque 1649057 (de 2-0 a 2-2) y
    France 1528960 (de 1-0 a 1-3).
- **Ninguna lección lo contradice.**

**T3 · 66, sub-ítem nuevo después de T2:**

> - **El desenlace de la rama de ventaja lo pone la fuerza; la tipología
>   describe la vía *(v0.1.27, aprobado el 10/11/2026)*.**
>   - `ECHADA-VOL`, «en su plan» y «sigue atacando» dicen **por dónde**
>     llegaría el empate: el banco del rival, la contra o la pelota parada.
>   - **Cuánto** se escapa lo dicen las dos referencias.
>   - La nota no escribe «administra, así que no se lo empatan» ni «sigue
>     atacando, así que amplía» como lectura del desenlace.
>   - La tipología se sigue eligiendo con su motivo (44 (b)): esto no la
>     afloja.

Y en la 44 (b), línea 576, al final («…no la echada.»):

> El desenlace de esa rama no lo da la tipología: lo dan las referencias de
> la 66.

- **Historial:** el estudio E y los 9 partidos de arriba.
- **Lo tumbaría:** que con la fuerza previa fija, la tipología separe en una
  medición con n ≥ 30 por tipología. Hoy no separa.

## 4. La plantilla de `siExpulsion`, para los dos lados (disciplina 16 y 44 (d)) — ACLARACIÓN

**Qué dice hoy.**

- La 16 pide `propia` y `rival` (línea 518).
- Para `propia` pide la ventana desde la roja y el régimen hasta el final
  (línea 519) y la vía de gol propia (línea 520).
- Para `rival` no dice nada de eso, y ningún punto exige las tres cuentas del
  marcador.

**Qué pasó (4 partidos, `mal_aplicada`).**

- **Spain–England 1528984 (England).** La línea traía empatando y perdiendo,
  pero no ganando, y fue la que se dio: roja de Anderson al 63' con 3-0 y dos
  goles concedidos en 12'.
- **Montenegro–Latvia 1545613 (Montenegro).** Con diez desde el 57' y 0-0, el
  obligado siguió cargando y metió dos. La línea no traía la vía de gol propia.
- **Pereira–América 1549872 (Pereira).** Sin ventana desde la roja: con
  «roja +15» el gol del 60' caía adentro.
- **Danubio–Liverpool 1649061 (Danubio).** La ventana de `rival` iba en la
  nota y la app no la pudo medir. Los goles llegaron a los 17 y 19 minutos,
  dentro del régimen.
- **Se suma Kosovo–Israel 1528971 (Israel), de otro tipo.** Con uno más,
  «no administra» se cumplió en los cambios, pero no en la amenaza: 6 remates
  y 0,35 de xG. Es la 44 (b) («se lee por la amenaza») aplicada a `rival`.

**T4 · 16, sub-ítem nuevo después de la línea 518 («`siExpulsion` declara los dos lados…»):**

> - **La plantilla de `siExpulsion` *(v0.1.27)*.** `propia` y `rival` llevan
>   lo mismo:
>   1. **Las tres cuentas del marcador** en la nota: ganando, empatando y
>      perdiendo, una línea cada una, aunque alguna parezca improbable.
>   2. **La ventana en su campo** (`ventana`: «desde la roja +15»), no en la
>      nota, y el régimen hasta el final (hasta el 120 con prórroga).
>   3. **En `propia`, la vía de gol propia** del que queda con diez (contra,
>      pelota parada, o que siga cargando si necesita ganar). **En `rival`,
>      quién queda de seguro** con el equipo volcado (63). Además, «no
>      administra» se comprueba por la amenaza, no por los cambios ni por lo
>      que declara el DT (44 (b)).
>
>   La v0.1.26 lo pedía solo para `propia`.

- **Historial:** los cinco partidos.
- **Lo tumbaría:** que con la plantilla completa sigan apareciendo ramas de
  expulsión que no describen el tramo jugado. Eso ya sería regla, no
  cumplimiento.

## 5. La pieza del seguro en las ramas que no persiguen (63) — CANDIDATO DE LA v0.1.26 → TEXTO

**Qué dice hoy (línea 635).** Nombra la pieza del `sob2` en la rama que
persigue y en la base `SOB`. La rama de ventaja quedó como candidato con dos
casos: Barcelona–Atlético y Alianza Lima–Los Chankas.

**Qué pasó.** La 63 dentro de las ramas que persiguen se sostiene: 12 de 15.

- **Ventaja con superioridad, Danubio–Liverpool 1649061:a.** Millán, «solo
  delante de los centrales», salió al 68' por Rossi. Con 1-0 y uno más,
  Danubio cargó y concedió dos en 82'-84'.
- **Superioridad empatado, Deportivo Cali–Tolima 1549867:a.** Con uno más
  desde el 58', cargó como decía la rama y concedió el 1-2 a los 4 minutos.
  La rama no nombraba quién quedaba de seguro.
- **`siLeEmpatan` tras ventaja temprana, Belgium–Italy 1528983:b.** La rama
  iba «en su plan» con `sob2` = 1 («Tonali solo») y concedió a 7 minutos del
  empate: «pesa aunque no persiga».
- **Sin fuente, Lithuania–Liechtenstein 1528989:a:5.** Con 2-0, dos piezas
  del seguro llegaron amonestadas y concedió a 3 minutos del doble cambio
  rival. Se anota y no se cuenta.
- **Y un aviso, Estonia–Bulgaria 1528988:a:2:** la pieza nombrada (Palumets)
  era suplente en la hoja.

**Honestidad con el tamaño:**

- de ventaja pura hay 1 caso firme (Danubio), más los 2 de la v0.1.26;
- contando las tres ramas que no persiguen, son 3 firmes ahora y 5 en total.

Es nombrar, no puntuar. Por eso alcanza para texto, pero D3 deja elegir.

**T5 · 63, sub-ítem nuevo después de la línea 635 («La pieza que sostiene el seguro se nombra…»):**

> - **También en las ramas que no persiguen *(v0.1.27)*.** La pieza del
>   seguro se nombra también en tres ramas:
>   - la de ventaja, con `sob2` ≥ 0.5 o «sigue atacando»;
>   - `siLeEmpatan`;
>   - `siExpulsion.rival`, el que carga con uno más.
>
>   El cierre anota su salida igual que arriba: el que no persigue también
>   se expone si el seguro se va. No cambia el `sob2` ni el cobro. **Con el
>   once oficial, la pieza está en el once**; si la hoja la pone en el banco,
>   se nombra otra o se declara la rama sin pieza.

- **Historial:** Danubio, Cali, Italy y Lithuania; Barcelona–Atlético y
  Alianza Lima–Los Chankas (de la v0.1.26); Estonia.
- **Lo tumbaría:** que la salida de la pieza no se asocie con concesión en
  las ramas que no persiguen. Se puede medir cuando la pieza viaje en un
  campo (A4). También, que nadie la use en el cierre (regla muerta).

## 6. `SOB1` dice la necesidad, no el régimen (disciplina 18) — ACLARACIÓN (el peso, candidato C1)

**Qué dice hoy.**

- `SOB1` sale de la tabla (18). Con `SOB1` = 1, el régimen arranca en el 0
  (56).
- La nota de la base `SOB` del obligado se escribe como régimen firme, sin
  mirar el sistema del once ni quién tendrá la pelota.

**Qué pasó (5 partidos, `regla_fallo` del régimen; ninguno pide cambiar el
cobro).**

- **Iceland–Luxembourg 1545617:b.** Perdiendo desde el 25', 0 remates en el
  área; los primeros cambios fueron al 66', lateral por lateral.
- **Croatia–Czech 1528985:b.** Con 0-1 desde el 2', defendió hondo con el
  40 % de la pelota y 8 remates.
- **Belarus–Albania 1528980:a.** La pelota y las ocasiones fueron del rival.
- **Central Español–Boston River 1649058:a.** El DT salió 5-4-1 y Boston hizo
  4 remates en 90'.
- **Serbia–Germany 1528965:a.** Con 20 % de pelota y 5 remates.
- **Lo empujó el rival:** England–Croatia 1528962:b. El ISE máximo de la rama
  necesita que el rival siga cargando, y el favorito administró.
- **Ojo con lo que NO dicen:** cuatro de los cinco concedieron igual, por
  otra vía (desborde, pelota parada, autogol). La aclaración no es «el
  obligado no se expone»: es que la nota no afirma un régimen que depende
  del once.

**T6 · 18, línea 528, al final («…fue leer **otro** relato y llamarlo corrección.»):**

> **`SOB1` dice la necesidad, no el régimen *(v0.1.27)*.** `SOB1` = 1 por la
> tabla queda como está: el número no se toca y el inicio sigue la 56. Lo que
> cambia es cómo se escribe la nota de la base `SOB` y de la rama del
> obligado: **el régimen va condicionado al sistema del once y a quién tendrá
> la pelota (52)**.
>
> - Con línea de cinco, bloque bajo de plan o un rival que le quita la
>   pelota, la necesidad puede no producir exposición. La nota lo dice con el
>   hecho que la activaría («se expone si mete el segundo 9 o sube a los dos
>   laterales»).
> - Si el sistema sale del once oficial, se revisa al rehacer (65).
> - El cierre ya separa la necesidad del régimen observado (61).

- **Historial:** los cinco partidos y England–Croatia.
- **Lo tumbaría:** que los obligados por tabla con línea de cinco, o con un
  rival que domina la pelota, se expongan como el resto. Hace falta el
  sistema del once (grid) y el volumen por tramo, que hoy la ficha no parte.

## 7. Disciplina 63: la herencia del `sob2` de rama ya está hecha — ACLARACIÓN

**Qué dice hoy (línea 636):** «Mientras la app no lo haga, lo copia el
analista *(cuando el mantenimiento lo implemente, esta ultima oracion se
borra)*.»

**Qué hay en el código:**

- `dtp_cowork.herencia_tde` da `SOB2persiguiendo`;
- `parte.heredar_ramas` lo aplica a las ramas que empujan (`rama_empuja`);
- `HERENCIA-DTP` nombra la rama (DEUDA 28).

**T7 · 63, línea 636, reemplazo** de esa oración por:

> La app lo aplica al depositar y `HERENCIA-DTP` nombra la rama si el
> declarado difiere.

## 8. Núcleo — APROBADO (03/11 y 10/11), medido sobre la v0.1.26 de hoy

**Cuánto pesa hoy.** El `SKILL.md` tiene 216 KB, unos 54 K tokens contando
caracteres / 4; la v0.1.25 que midió la propuesta tenía 50,9 K.

**Qué pasa a `references/HISTORIAL.md`, tal cual y sin editar:**

| Archivo · líneas | Qué es | Tokens |
|---|---|---:|
| `SKILL.md` 8-15 | «Dónde vive el registro canónico» (lo operativo queda en el PASO 0, abajo) | 0,3 K |
| `SKILL.md` 16-303 | notas de versión v0.1.26 … v0.1.1 (26 bloques) | 24,2 K |
| `SKILL.md` 671-768 | EL REGISTRO: esquema de 51 columnas, `pre_rubrica`, la trampa de `IE_recomputado_esquema6`, numeraciones ausentes, filtro de frecuencia, TDE-026 | 3,0 K |
| `INDICE_IE.md` 3-27 | sus notas de versión v0.1.19 … v0.1.1 | 1,9 K |
| esta propuesta | la nota de la v0.1.27 (T0) y los casos de T1-T7 | — |

Después del traslado, el `SKILL.md` queda en ≈ 26,5 K, más ≈ 1,5 K de los
textos nuevos: **≈ 28 K**.

**Qué queda arriba (línea 8, en lugar de las líneas 8-303):**

> Versión vigente: **v0.1.27 (<fecha de subida>)**. Las notas de cada
> versión, los casos que motivaron cada regla y el esquema del registro están
> en `references/HISTORIAL.md`: **no hace falta leerlo para analizar un
> partido**; se lee al revisar el skill.

**Las reglas que hoy viven solo en el historial y suben al cuerpo.** Son las
T1-T10 de `NUCLEO_SKILLS_propuesta.md` §2.1, con lo decidido el 10/11.

**N1 · PASO 0, punto 4 (línea 347), reemplazo** (T10 y la duda 3, aprobada):

> 4. `assets/casos/registro.csv` — **no se lee entero**: para `F3` y los
>    antecedentes, buscar con Grep el nombre de los dos equipos. La copia
>    empaquetada es una instantánea: antes de usarla se compara su sha256 con
>    el fijado en `scripts/calibrar-tde.py` y, si difieren, manda la del repo
>    y se dice.

**N2 · línea 563 («Desfase de documentacion declarado…»), reemplazo por las
disciplinas 34-39 en su hueco numerado** *(D4 (a))*. Los textos son literales
del changelog, salvo los marcados:

> 34. **Con dos o más indicadores abiertos, la caja publica el rango
>     conjunto** (mínimo y máximo combinatorios de todos los abiertos a la
>     vez), no un rango por indicador *(v0.1.13; vigente, decisión del
>     10/11)*.
> 35. *Derogada por la 55 (decisión del 10/11):* sin XI confirmado, `F1` es
>     nivel de dato C, no `sin dato`. El texto de la v0.1.13 está en el
>     historial.
> 36. **Cuando `F1 = 0` por rotación de 3 o más titulares, el output declara
>     que el descuento físico se está pagando en coordinación** y que el
>     módulo no lo representa *(v0.1.14)*.
> 37. **La ventana modal se declara para la vía del índice que manda**
>     (PASO 3: ISE > IE → `SOB`), no para el tipo que sugiera la rúbrica de
>     tipos. La doble ventana `SOB` sigue su propio criterio (`INDICE_IE.md`,
>     v0.1.15) *(v0.1.14, reescrita en v0.1.27 sin el riesgo compuesto,
>     suspendido en v0.1.20; ver D4 (b))*.
> 38. **El sesgo tardío es una propiedad de la serie:** su corrección solo
>     entra como cambio de regla autorizado al alcanzar el umbral, nunca como
>     ajuste de una fila *(v0.1.14)*.
> 39. **Todo caso `RETRO` declara su traza `PRE`:** los indicadores que no
>     habrían sido puntuables antes del partido y con qué valor entraron
>     *(v0.1.15)*.

**N3 · otros ajustes que trae el traslado:**

- **`INDICE_IE.md`, fila `F3` (línea 120):** se agrega «sin datos de impacto
  de banco en la temporada, `F3` es `sin dato` y entra en la caja conjunta,
  también fuera de la fecha 1» (T8).
- **`INDICE_IE.md` línea 472:** «mismo criterio que la disciplina 37» pasa a
  «(v0.1.15)», porque la 37 reescrita ya no habla de cercanía.
- **T7 de la propuesta del núcleo** («no bajar `P(gol)` con ejecutor de
  penales»): **se declara caída** con la suspensión de la v0.1.20 (decisión
  del 10/11) y queda solo en el historial.
- **T9** («apartarse… solo hacia más medición»): **no se copia**. Ya está en
  la última frase de la disciplina 27 (línea 549: «se admite hacia más
  exposición, nunca hacia menos»), y la propuesta del núcleo no lo vio.

**Guardia (de la propuesta del núcleo, §5):** `backend/test_nucleo_skills.py`
con su frase ancla por regla. No es parte del skill y va con el traslado.

## 9. Tres frases del núcleo contradichas por reglas posteriores — ACLARACIÓN

La propuesta del núcleo las dejó a la vista y no las tocó, porque eran cambios
de reglas. Esta es la próxima revisión. **Ninguna regla vigente cambia:** se
alinea el texto viejo con la regla que ya manda *(D5)*.

- **N4 · Integración, línea 774.** «corregir la localía hacia arriba en
  Sudamérica antes de comparar μ» choca con la disciplina 47 y la FICHA
  MÍNIMA («se publica como sale del motor»; derogada desde la v0.1.18). Se
  borra la cláusula, y «Tres cuidados» pasa a «Dos cuidados».
- **N5 · LA TESIS, línea 335.** «La lectura que se comunica es el riesgo
  compuesto» pasa a:

  > La lectura que se comunica es el IE y el ISE con sus bandas ordinales y
  > el mecanismo: el riesgo compuesto está suspendido desde la v0.1.20
  > (PASO 2).

- **N6 · `INDICE_IE.md`, «Mapeo de IE a probabilidad» (líneas 355-364).**
  Encima de la tabla:

  > 🚫 SUSPENDIDO en v0.1.20 — no se emite; se conserva como historia de la
  > escala.

  Es la misma marca que ya llevan `P(sobreexposición)` y `P(gol | …)` en el
  mismo archivo.

---

## Candidatos a medir (no entran)

| N.º | Qué | n de esta semana | Qué medición haría falta |
|---|---|---|---|
| C1 | **El peso de `SOB1` por la tabla sin un hecho de hoy** (punto 6) | 5 partidos con el régimen no visto; 4 de ellos concedieron igual | Ramas `SOB` del obligado por tabla, partidas por sistema del once (línea de 5 o no, desde el grid) y por posesión prevista, contra la concesión en el régimen; n ≥ 30 por lado. Es peso: backtest y vectores, nunca a mano |
| C2 | **Superioridad numérica según el marcador:** desdoblar `siExpulsion.rival` como se hizo con la propia en la v0.1.21 | **Ganando:** cargaron 3 (Danubio 1649061, España 1528961, América 1549872) y administraron 2 (Cerro 1649059 y Monterrey 1550951, con cambio de delantero por medio). **Perdiendo o empatado:** cargaron 4 de 4 (España 1528984, ADT 1549558, América 1648690, Cali 1549867). Israel 1528971: cambios sin amenaza | Tramos con uno más por marcador y minuto de la roja: goles a favor y en contra, y cambios ofensivos o defensivos por la posición del que entra y del que sale (A2); n ≥ 30 ganando |
| C3 | **Roja propia ganando: tampoco es un punto asegurado** | Concedieron 3 con la roja yendo ganando: Juventud 1649433 (a 3' de la roja del 78'), Inter Bogotá 1648690 (roja al 11', se lo dieron vuelta) e England 1528984 (de 3-0 a 3-2, ganó). Cusco 1549558 se puso adelante ya con diez y lo empataron al 87'. Sostuvo Junior 1549868, contra un rival sin banco. La referencia de la v0.1.25 (11 de 12) es **empatando** | La tabla de concesión tras roja propia por marcador y minuto, aprobada en la v0.1.25 y pendiente (A2). La tasa ganando se escribe al lado de la de empatando, como referencia y no como peso |
| C4 | **Ventana desde el cambio ofensivo** (candidato de la v0.1.26, «medir primero») | 4 casos explícitos: Cali 1549867, Cúcuta–Jaguares 1549866, Lithuania 1528989 e England 1528962 (sin gol). 5 implícitos: Georgia 1528973, Cerro Largo 1649056, Millonarios 1549871, Norway 1528972 y Mijas 1644362. **Sin denominador:** solo se anotan los cambios seguidos de gol | Todos los cambios ofensivos de la base con su minuto, y la tasa de gol en los N' siguientes contra la del mismo reloj sin cambio (A3); n ≥ 30 por reloj |
| C5 | **Huecos de `S1`** | Suplente que entra y ve la roja: 2 (Serbia 1528965, Juventud 1649433). El estudio contaba 3 con Pereira, pero Mosquera era titular fuera del once de referencia. Una sola vez cada uno: roja al arquero titular (Querétaro 1550951), conducta violenta sin pelota (Maldonado 1649059) y roja del DT (Pereira 1549872) | Un casillero nuevo es número. Primero, el insumo: las rojas del equipo y de los suplentes en `tde/{id}` (A5). El hueco del suplente ya está declarado en la 16 |
| C6 | **Matices de un caso, o de dos** | La vía del empate también son los titulares del rival que domina: 2 (Wanderers 1649063, Armenia–Cyprus 1528959). Con doble pivote se nombran las dos piezas: 1 (Chapecoense 1492312). Con `sob2` = 1 heredado, el seguro está roto desde el gol: 1 (Portugal 1528974). Tras ventaja de 2-0 temprana, el favorito obligado administró con cambios defensivos y perdió el 2-0: 1 (Torque 1649057) | Esperar el tercer caso ciego de cada uno |

**Siguen sin material** (vienen de candidatos anteriores):

- **La SOB de la hora con 0-0 y el empate útil.** El único caso nuevo,
  Maldonado 1649059, es un favorito expuesto antes del 75. Va en la dirección
  contraria al criterio de entrada, que pide un visitante con 0-0 que no
  empujó.
- **La lista de la 44 (f) en `siLeEmpatan`.** Tarancón 1644379, más
  Millonarios–Tolima de la v0.1.26: son 2.
- **El ISE agravado con roja propia perdiendo:** queda 2 a 2.
  - A favor: Liverpool 1649061 y Pereira 1549872.
  - En contra: Comerciantes 1549557 y Finland 1528963.
- **El defecto por quien persigue.** Hay un solo caso explícito, Anaitasuna
  1644336, y falta `μ_partido` por tramo (A6).
- **El «doble golpe».** Danubio 1649061 suma un caso, sin medición.

## Confirmaciones que se cierran sin texto

| Regla | Lo que dicen las lecciones |
|---|---|
| 61 (salidas y vía del gol en el cierre) | 47 de 47. Las 3 que figuran como `regla_fallo` son del `SOB1` de la base (punto 6) |
| 65 (`abierto` por defecto) | 29 de 29. Con `abierto` se observó sobre todo `se_rompe`; el conteo sale de la prosa, sin `μ_partido` por tramo |
| 66 (referencia del minuto completa) | 15 de 15 cuando se cita |
| 44 (b) («sigue atacando» por la amenaza) | 39 de 41, casi todos de favoritos claros (margen de μ entre 0,66 y 1,82): es el sesgo de selección ya declarado |
| 44 (b) y 6 (la tipología no sale de la identidad ni de un antecedente que no coincide) | 4 incumplimientos de regla escrita: UTC 1549556, Faroe 1528987, Central Español 1649058 y Slovenia 1545654. Lo confirman al revés Chico 1549870 y Andorra 1545615 |
| 16 (paridad restablecida) | Once Caldas–Nacional 1648691 |

---

## Para la app (solo lo que falta)

Verificado en `backend/` el 17/11. Nada mueve un número calibrado.

- **A1 · `referencias.ventajaPorFuerza` en `GET …/tde/{id}`.**
  - Hoy está solo en el bloque `desconfianza` del parte, que se calcula al
    leer, después del depósito.
  - Reusa `desconfianza.ventaja_por_fuerza` con el 1X2 sin margen del
    fixture.
  - Contrato primero (`docs/openapi.yaml`), y su test.
  - Bloquea a T2 (ver D2).
  - Lo que sigue pendiente aparte: la tabla A por minuto con los eventos de
    `sad.db` (`DESCONFIAR_propuesta.md`).
- **A2 · Referencia de expulsiones por marcador y minuto, por los dos lados.**
  - Del lado propio, la tabla de concesión tras roja propia: aprobada en la
    v0.1.25 y anotada como pendiente en la línea 522 de la 16.
  - Del lado rival, los tramos con uno más, con goles a favor y en contra y
    los cambios por la posición de quien entra y de quien sale.
  - Va en `referencias` de `tde/{id}`.
  - Mide C2, C3 y el ISE agravado.
- **A3 · Minutos desde el último cambio ofensivo de cada lado, por gol
  concedido, con denominador.**
  - Es el punto 10 de «Para la app» de la v0.1.26, sin hacer.
  - Mide C4.
- **A4 · La pieza del seguro en un campo.**
  - Un `piezaSeguro` opcional en `RamaReasignacion` y en la base.
  - El veredicto marca el minuto en que salió (cambio o roja), cruzando con
    `backend/identidad.py`.
  - Es el punto 4 de la v0.1.26, sin hacer.
  - Mide T5 y C6.
- **A5 · Los insumos de `S1` en `tde/{id}`.**
  - Las rojas del equipo en la temporada y en los últimos partidos.
  - Las amarillas de zaga, pivote y 9.
  - Las rojas de los suplentes de `bancoProbable`.
  - Es el punto 11 de la v0.1.26, sin hacer: hoy `S1` sigue en
    `noCalculables`.
  - Czech–Spain 1528961 dejó `S1` sin dato con dos rojas checas en la
    competición.
- **A6 · Quién persigue por `μ_partido` en cada tramo.**
  - Es el requisito del candidato del defecto por quien persigue.
  - Viene pendiente de la v0.1.25.
- **A7 · Textos viejos y la subida.**
  - `tde.f2.puedeSubir` todavía dice «súbelo a mano», contra la 21 decidida
    el 10/11.
  - La nota de `desenlaceTde` en `backend/analisis/lecciones.py` (línea 890)
    todavía dice «ISE de rama ≥ 7 → se_rompe».
  - Al subir la v0.1.27, anotar la hora en `SUBIDA_VERSION`.

**No se pide:** un aviso del recibo para las tres cuentas de `siExpulsion`.
Habría que leer la prosa, y el aviso de la ventana en la nota (1420) ya cubre
lo medible.

## Coherencia entre skills

| Cambio | Depende de | Qué hacer al redactar |
|---|---|---|
| 1 (banco) | **DTP v1.9** (`bancoOfensivo`) y **EFE v1.11** (B5, F1 «banco probable»): leen la misma `bancoProbable` | Que las tres propuestas nombren el mismo campo. La fila `F3` de `INDICE_IE.md` sigue heredando B5 del EFE: con los dos sobre la misma lista no hay conflicto, pero conviene que B5 diga que puntúa sobre `bancoProbable` |
| 1 (rehacer) | `corrida-sad`, modo `rehacer`: ya entra con FUERA-EN-LA-HOJA, ONCE-SIN-FILA-F1 y EFE-RECOMPUTO-PENDIENTE | Nada en el skill; el modo ya reescribe `tde.bloques[]` |
| 2 y 3 (fuerza) | **sad-analysis v4.6**: alerta DESCONFIAR, el descarte, y `ventajaPorFuerza` que ya sale en `desconfianza` del parte | El TDE no nombra la alerta: es de la síntesis. Que la v4.6 no pida a la rama del TDE un número que el TDE no escribe. Subir las dos juntas |
| 4 (`siExpulsion`) | **sad-analysis** lee la vía de gol propia de `siExpulsion.propia` para el 1X2 | Sin cambio para la síntesis: la línea sigue en el mismo campo |
| 5 (pieza del seguro) | **DTP v1.9**, M3 («quién queda atrás» en todas las ramas, v1.8 cambio 8) y la 44 (b) T13 («la rama y el DTP del mismo equipo dicen lo mismo») | Si el DTP v1.9 nombra al que queda atrás en la rama de ventaja, que sea la misma pieza. Si no, manda el DTP y se dice (T13 vigente) |
| 6 (`SOB1` y el sistema) | **DTP v1.9**: posesión por rama (12 de 12 mal aplicadas, «rama arriba» separada) y el sistema del M1 sobre el once | T6 se apoya en «quién tendrá la pelota»: si el DTP v1.9 escribe la posesión por rama, el TDE la toma de ahí. **SOB2 y C1 siguen heredados del DTP** sin cambio |
| 7 (herencia) | DTP: `nivelFocoPersiguiendo` (v1.5) y la 1056 | Nada: ya está en la app |
| 8 (núcleo) | Las cuatro versiones se suben con el núcleo y la misma guardia | La línea «Versión vigente» igual en los cuatro skills; `docs/skills/README.md` está viejo (dice TDE v0.1.22) |
| Jev | `lectura` (PR #562) | Nada en el texto: el TDE no nombra etiquetas de Jev |

**Bloqueos para redactar: uno.** T2 necesita A1 (D2). Lo demás no depende de
otra propuesta. Si el DTP v1.9 no escribe la posesión por rama, T6 se lee con
la 52 sola, como hoy.

## Qué NO se propone

- **Ningún número:**
  - el peso de `SOB1` (C1);
  - un casillero nuevo de `S1` (C5);
  - el desdoble numérico de la superioridad o de la roja ganando (C2 y C3);
  - el inicio de la ventana desde el cambio (C4);
  - el corte del 30' de la 66;
  - los tramos de `ventajaPorFuerza`, que son los del estudio y no se tocan.
- **La alerta DESCONFIAR en el TDE:** es de sad-analysis.
- **Ninguna regla que se afloje.** T3 no le quita a la 44 (b) la obligación
  de nombrar por qué administra.
- **Los candidatos de 1-2 casos** (C6 y «Siguen sin material»).
- **Reetiquetar con Jev** lo ya sellado.

## Decisiones del usuario

- **D1 · El banco en la rama (punto 1).**
  - (a) La lista entera de `bancoProbable`, sin el arquero suplente, en una
    línea por rama.
  - (b) Solo los ofensivos por rol (delanteros, `lateral: true`, los que
    tienen goles o asistencias desde el banco), más «resto: bancoProbable».

  **Recomiendo (a).** Los que decidieron sin estar nombrados fueron un medio
  (Majer), el que tiró un córner (S. Costa) y un lateral (Dimarco). La API
  solo da G, D, M y F, y un filtro por rol los habría dejado afuera.
- **D2 · `ventajaPorFuerza` (punto 2).**
  - (a) La v0.1.27 sube cuando `tde/{id}` la tenga (A1), y el texto cita
    solo el campo.
  - (b) Sube ya, con la tabla del descanso en una línea, hasta que esté.

  **Recomiendo (a).** El cambio de la app es chico, y la regla de la 66 es
  no copiar números que la app da.
- **D3 · La pieza del seguro en las ramas que no persiguen (punto 5).**
  - (a) Entra como texto (nombrar, sin número).
  - (b) Sigue candidato hasta tener 5 casos de rama de ventaja pura.

  **Recomiendo (a).** Hay 5 casos entre las tres ramas y no mueve ningún
  número.
- **D4 · Disciplinas 34-39 (punto 8).**
  - (a) En su hueco numerado, como en N2, lo que también resuelve las citas
    huérfanas.
  - (b) Repartidas donde decía la propuesta del núcleo §3.3 (fila `F1`,
    PASO 3, disciplina 19).

  **Recomiendo (a).** Además, **D4 (b′)**: la 37 reescrita **sin** la
  cláusula de cercanía. «A menos de 5 puntos» era de riesgo compuesto, en %,
  y no tiene traducción a IE/ISE sin inventar un umbral.
- **D5 · Las tres frases contradichas (punto 9).**
  - (a) Se corrigen ahora: la localía, LA TESIS y la marca de suspendido.
  - (b) Se dejan con una nota.

  **Recomiendo (a).** Ninguna cambia una regla vigente: alinean el texto con
  la 47 y con la v0.1.20.

## T0 · nota de versión (va directo a `references/HISTORIAL.md`)

> **v0.1.27 · <fecha de subida> — la rama toma el banco de la app y la
> ventaja de la fuerza.** Revisión desde el estudio de las lecciones del
> 17/11/2026: 276 lecciones `pendiente` de 81 partidos del 10 al 16/11,
> ciegas `PRE`, escritas con la v0.1.26, en una semana con mayoría de
> selecciones. Ningún número se mueve. Primera versión con núcleo e
> historial.
>
> - **66:** el banco es `bancoProbable`, la lista entera, en cada rama
>   donde entra; la rama de ventaja cita también `ventajaPorFuerza`; el
>   desenlace lo pone la fuerza y la tipología describe la vía (aprobado el
>   10/11).
> - **16:** la plantilla de `siExpulsion` para los dos lados. **63:** la
>   pieza del seguro también en las ramas que no persiguen; la herencia del
>   `sob2` de rama ya la hace la app. **18:** `SOB1` dice la necesidad, no
>   el régimen.
> - **Núcleo:** las disciplinas 34-39 en su hueco (la 35, derogada por la
>   55); el registro se busca por equipo; se alinean con la 47 y la v0.1.20
>   la localía, LA TESIS y el mapeo.
> - **Candidatos, no aplicados:** el peso de `SOB1`, la superioridad y la
>   roja propia según el marcador, la ventana desde el cambio ofensivo, los
>   huecos de `S1` y los matices de un caso.

## Sesgos y límites

- **Una semana, mayoría de fecha FIFA.** Selecciones con onces tardíos y
  muchos favoritos claros: eso infla la 44 (b) y el problema del banco.
- **Conteos de lecciones, no tasas.** Quien cierra nombra el skill sobre
  todo cuando algo falla. La clasificación es del estudio, hecha leyendo la
  prosa; no usa `modoFallo`.
- **Los casos de la pieza del seguro y de la superioridad son de 3 a 5 por
  lado.** Ninguno sostiene un número, y por eso todo lo numérico quedó en C1-C6.
