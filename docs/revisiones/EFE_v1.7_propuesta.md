# Propuesta de revisión · `efe-clasificador` v1.6 → v1.7

**Estado:** APROBADA por el usuario entera (25/10/2026), umbral del cambio 6
incluido. Redactada en `docs/skills/efe-clasificador/` (v1.7; la rúbrica pasa
a `references/rubrica-efe-v1.7.md`) y `efe-dashboard` v1.10 (F6 con el umbral
nuevo). En la app: `CORTE_VERSION` con la v1.7 y `dtp_cowork.parejas_nuevas_de`
con ≤ 1 vez juntos (test en `test_dtp`). Falta que el usuario suba los dos zips.
Redactada desde las **168 lecciones pendientes** del skill en la cohorte
`c3-2026-09-23`: todas de partidos del 21 al 24/10, posteriores al corte de la
v1.6. La base es la v1.6 vigente (`docs/skills/efe-clasificador/`,
`references/rubrica-efe-v1.6.md`).

## De dónde sale

- **168 lecciones**: 71 aciertos, 38 parciales y 59 fallos. Las 168 son
  ciegas PRE (acreditables).
- **Ninguna pide mover un número.** Jev no etiquetó ninguna con
  `proponeMoverNumero`. Por eso esta versión no toca ningún peso, máximo
  ponderado ni corte de la tabla de puntuación. El único umbral que se toca es
  el de una alerta declarativa sin peso (cambio 6), y se marca aparte.
- **Sesgo de atribución, igual que en la v1.6.** Muchos «fallos» del lado son
  del 1X2, con la regla del EFE confirmada en la misma lección. FACTOR-X y
  T.54 son el caso más claro: casi todas sus lecciones dicen «declarado y
  cumplido».

## Lo que la v1.6 acertó y no hay que tocar

Estas reglas se confirmaron en esta tanda; se dejan como están:

- **FACTOR-X amplía el rango, no mueve el centro.** Confirmada en unos 20
  cierres: Club América, Orense, Vitória, Mirisola en Leuven, Paredes en Boca,
  Wesley Natã en Fluminense, Yang en Westerlo, Sequeira en Casa Pia, Rojo en
  Estudiantes, entre otros.
  - Matiz que ya cubre el texto («en cualquier dirección»): el rango se abre
    también **hacia abajo por disciplina** (Elliott, Valencia: entró al 70 y
    fue expulsado al 89).
  - Y **hacia la derrota cuando el FACTOR-X es el arquero en duda** (Özer,
    Lille).
- **El barrido fijo de F5, lista 3** (titular del once oficial fuera de la
  tabla F1 = candidato FACTOR-X). Aston Villa: Alysson Edward, suplente con 0
  de 8 en la F1, fue el decisivo.
- **T.54 respeta la serie del DT nuevo** y **descuenta la serie, no el
  partido**. Lo confirman:
  - Santos Laguna (sexta victoria con Paiva) y Torino (Abate).
  - Real Potosí y Union Berlin.
  - Gladbach: dejar sin dato el D3 del DT anterior evitó un error.
  - Fluminense, Atlante y Blooming.
- **T.54-B** (Arouca: mismo once heredado, 3 de 3 sin perder).
- **El umbral de GK-FALLA-ACTIVA (≥ 2 errores) se sostuvo en cinco casos.**
  Gimnasia LP, Libertad, Deportivo La Coruña, Vasco y Sarmiento: con un solo
  error el arquero fue figura o neutro. Nice (Diouf) cumplió la condición con
  el segundo error.
- **B6 con el once oficial y caja de sensibilidad** (Huachipato, Rubio Ñu).
- **G-SORPRESA amplía el rango** (Aston Villa–Viking, Monterrey, Charleroi).
- **COLAPSO EN CASCADA sin predicción de goleada.** El escenario se dio y no
  hubo goleada en Necaxa (por autogol al 77), UTC Cajamarca (1-2), Juárez
  (0-1), Deportivo Recoleta y Central Español (margen 2). Las dos rupturas
  tienen explicación aparte (cambio 3).
- **B5 «por lo que entra»** (Inter, Cruz Azul, Porto, Tachira, Platense,
  Always Ready, Albion).

## Los siete cambios propuestos

### 1. La reducción por zona se lee por la zona que genera y por quién la reemplaza

**Lo medido.** El F3 y la reducción por zona fallaron casi siempre por lo
mismo: el porcentaje no distingue **qué hace la zona ni quién entra**.

- **La etiqueta de zona engaña**:
  - Como: ATK en rojo (66,7 %) y la producción no cayó, porque el generador
    jugaba en MID (Paz, Baturina).
  - Schalke: F3 cumplida en el ataque (un remate al arco) y no en la defensa.
- **El recambio de oficio absorbe**:
  - Deportivo Cali: DEF reducida un 37,5 % con recambio de oficio, 0,62 xG en
    contra y ningún gol.
  - Casa Pia: zona GK en rojo, y atajó un arquero de nivel probado.
  - Oriente Petrolero: GK ×1.5 por un suplente con cinco titularidades; los
    goles no pasaron por él.
- **El reconvertido no absorbe**:
  - Tigres: un lateral de rotación metido de central, y el gol salió por ahí.
  - Mainz: un central reconvertido de la pareja nueva cometió penal.
  - Club Queretaro: la línea rearmada concedió los dos goles.
- **El descanso planificado no es una baja.** Nacional (Colombia): IP 16 rojo
  armado casi entero con no convocados por descanso; el once que volvió no
  concedió nada (xG 0,15).
- **Una zona > 40 % pesa aunque el IP no pase de 7.** Bayern (MID 41,7 % con
  IP 5, empate de local), Puebla (MID 50 %, tres goles en 17 minutos) y Lens
  (DEF 41,7 %, concedió tres).

**Propuesta (sin tocar el cálculo del IP ni de la reducción):**

1. **F3 por zona.** Una zona en 🔴 (> 40 %) activa F3 aunque el IP global no
   pase de 7. La nota de F2a ya lo permitía («el criterio cualitativo puede
   anular el cuantitativo»); se vuelve explícito y la alerta **nombra la
   zona**.
2. **La F3 se lee por la zona que pierde y por la que genera**, no como equipo
   entero. Si el generador del equipo juega en otra zona (un ATK sin
   delanteros con el creador en MID), se dice.
3. **Cada ausencia de una zona en 🟡/🔴 declara quién entra: «de oficio» o
   «reconvertido».** El número no cambia. La lectura sí:
   - Con recambio de oficio de rol 🟠 o mayor (o un GK de nivel probado en la
     categoría), la zona se describe como **«cubierta»**.
   - Con un reconvertido, se señala como **la vía de gol del rival** que baja
     al DTP.
4. **El no convocado por descanso, con el titular disponible para el
   siguiente partido, va en F4 (rotación voluntaria), no en F2.** No suma al
   IP como una lesión.

### 2. Las fuentes de bajas tienen jerarquía; la previa de un agregador es duda, no baja

**Lo medido.** Siete casos en que el bloque F dio de baja a quien jugó, o no
vio a quien faltó:

- **Bajas que jugaron:**
  - Leipzig: Baumgartner, «baja» en dos previas (Sports Mole, Khel Now), entró
    al 78 y asistió.
  - Beveren: Jans y Boone, de la lista de un agregador, fueron titulares.
  - Flamengo: Arrascaeta, dado «sin» por fractura, entró al 64.
  - Casa Pia: contradicción entre Sports Mole y A Bola, y acertó A Bola (la
    fuente local).
- **Racing Montevideo:** la ficha traía 10 titulares, S. Da Silva entró como
  baja (IP ATK en rojo) y convirtió el penal.
- **Ausencias que nadie vio:**
  - Nacional Potosí: atajó un arquero que ninguna previa anunció.
  - Levante: el central titular fijo no figuró en la hoja sin noticia previa.

**Propuesta:**

1. **Jerarquía de fuentes para el estado del F1:**
   1. Convocatoria o parte médico del club.
   2. Prensa local del club.
   3. Prensa nacional.
   4. Previas de agregador (Sports Mole, Khel Now y similares).

   Una baja que solo sostiene el nivel 4 va **⚠️ Duda**, nunca ❌ Baja. Con
   dos fuentes en contra, manda la de nivel más alto.
2. **Una hoja de partido incompleta** (menos de 11 titulares en la ficha) no
   cierra el bloque F ni se lee como zona crítica. Se espera la hoja completa
   o el once de prensa.
3. **El titular fijo que falta de la hoja sin noticia** se declara en la caja
   de sensibilidad («TF fuera sin parte»), no se ignora.

### 3. D3 se declara con su contexto: condición, competición y escala

**Lo medido.** Las lecciones del D3 dicen lo mismo de cinco maneras: el D3
**viaja mal** fuera del contexto donde se midió.

- **Condición:**
  - Delfín: D3 ✅ por dos remontadas de local, y perdió 0-4 de visita sin
    reaccionar.
  - Leipzig: «tras cada derrota gana el siguiente en casa», confirmado por
    tercera vez, porque se leyó por sede.
  - Racing de Santander: la respuesta previa en la misma sede volvió a
    responder.
- **Competición:** Zulte Waregem tenía un D3 🔶 apoyado en un 3-0 de copa
  ante un rival de segunda, y sumó la cuarta derrota seguida de liga.
- **Escala:**
  - LASK: «se rompe al recibir», importado de un 3-6 ante Liverpool; contra
    Sporting recibió al 5 y empató al 15.
  - Galatasaray: la racha de derrotas europeas se leyó como inestabilidad del
    bloque D, y remontó en cinco minutos.
- **Qué mide cada nivel** (Chico, UTC, Lommel, LDU, Monagas, 2 de Mayo,
  Macará):
  - ❌ mide **no recuperar**. No mide «no reaccionar» (UTC reaccionó con
    volumen) ni cuidar una ventaja propia (Chico sostuvo el 1-0).
  - 🔶 es **reaccionar sin sostener**: empata y no remonta, o pierde la
    ventaja.
  - ✅ es **recuperar**.

**Propuesta:**

1. **D3 se escribe con su contexto:** condición (L/V), competición y escala
   del rival de la serie que lo sostiene.
   - Un D3 medido en una sola condición se lee **una franja abajo en la otra**
     (✅ → 🔶, 🔶 → `sin dato`).
   - Un D3 medido en otra competición o contra otra escala (copa ante una
     división inferior, Champions contra la liga local) va **`sin dato`** para
     esta fecha.

   Esto generaliza el candidato **D3-DEGRADADO** de la v1.6, que pasa de
   candidato a regla en su forma de contexto, con cinco casos.
2. **La semántica de los tres niveles queda escrita** en la tabla del bloque
   D, como arriba: ✅ recupera · 🔶 reacciona sin sostener · ❌ no recupera.
   Ninguno predice goleada.
3. **El tope del bloque D por D3 ❌ no se toca:** es un número.

**COLAPSO EN CASCADA, matices que no cambian la regla de la v1.6:**

- **Solo se evalúa si el equipo con D3 ❌ recibe primero.** Si abre él o el
  rival del D3 ✅, la alerta queda «no testeada» (Charleroi, Chico).
- **Si el que abre el marcador se queda con 10, la alerta se desactiva**
  (ADT: uno más desde el minuto siguiente).
- **Candidato declarado y NO aplicado: COLAPSO + agravante → ruptura
  posible.** Las dos rupturas de la tanda tuvieron un agravante:
  - Marítimo (5-0): recién ascendido de visita, R-KT.2.
  - Manchester United (4-1): zaga de urgencia, con F3 en DEF y De Ligt tras
    once meses.

  Con dos casos queda candidato.

### 4. Rotación por calendario: el EFE se lee condicionado al once, con una rama alternativa

**Lo medido:**

- **Seis rotaciones de seis titulares o más** decidieron partidos que el EFE
  leyó con el XI de referencia:
  - Independiente del Valle: semifinal de copa a cinco días; rotó seis y no
    ganó.
  - Stuttgart: quinto partido en 14 días; seis cambios, tres titulares de la
    cadena en el banco. «La rotación no funcionó» (Hoeneß).
  - Athletic: tercer partido en ocho días; rotó seis y el XI de referencia
    falló en tres puestos.
  - Zulte Waregem: cuatro titulares fijos al banco; el núcleo «10 de 10» que
    sostenía el 52,8 % no fue el que jugó.
- **Al revés, la rotación de un banco profundo no bajó al equipo:**
  - Leipzig (los cuatro que entraron intervinieron en los cuatro goles).
  - Monterrey (rotó tres y goleó).
  - Libertad (con tres al banco, el gol salió de dos que entraron).
  - Puerto Cabello.
- **Y el que tiene que ganar no rota** (Atlético Tucumán, con semifinal
  continental viva: salió el once tipo).
- **Dortmund:** la dependencia se mide en los **rotados de inicio**, no en el
  banco de impacto que entra con el partido en marcha.

**Propuesta:**

1. **Cuándo se abre la rama alternativa.** Con una **eliminatoria (copa o
   continental) a ≤ 5 días**, o con el **3.º partido en 8 días** o más, la
   caja de sensibilidad abre una **rama «once alternativo»**. Es la misma
   regla de exigencia que el F2 del TDE ya usa. En esa rama:
   - quién rotaría, según el patrón de rotación del DT en la temporada;
   - cómo queda el bloque B (B3, B5);
   - y la reducción por zona.

   El porcentaje del EFE se declara **«condicionado al once oficial»**.
2. **Con el once oficial, si rotaron ≥ 3 titulares fijos** respecto del
   XI-referencia, el bloque B y el F se **recomputan antes de cargar**. Es lo
   mismo que el DTP ya hace con `DTP-REHACER`.
3. **F4 mide dependencia con los rotados de inicio.** El banco de impacto es
   B5, y no se mezclan.

### 5. El porcentaje del EFE no se compara entre bases distintas

**Lo medido.** La brecha de porcentaje entre los dos equipos apuntó bien
cuando los dos estaban en la misma base. Sin las alertas que se nombran abajo,
el lado con más EFE ganó en Cuenca (59 contra 45), Villarreal (51 contra 27),
Nacional Asunción (83 contra 77), Betis y Pachuca.

Falló en todos los casos en que un lado era de otra base:

- Elversberg, ascendido: 64 contra 49, sin traducción en cancha.
- Viking: el bloque E medido en la Eliteserien no se traslada a la Champions
  contra la Premier.
- Coventry–Fulham: R-KT.2 de un lado y T.54 del otro, con xG parejo.
- Vitória–Marítimo: un 32 % goleó a un ascendido.

Además, el **bloque E puntúa resultados, no juego**:

- Nottingham Forest dominó de visita con E en 0.
- Fulham con E en 0 ganó a un colista ascendido.
- RAAL La Louvière hizo su E en 0 contra los de arriba y ganó 3-0 al de su
  franja.

**Propuesta:**

1. **La brecha de porcentaje solo se lee entre equipos de la misma base** (la
   regla `misma_base` de la alerta ESCALA-LIGAS de la app) y sin R-KT.2 ni
   T.54 en un lado. Con cualquiera de esas, la diferencia se declara
   **«empate técnico de formación»**: no ordena el partido.
2. **El EFE dice cuánto creerle a la K de cada equipo, no quién gana.** Va al
   diagnóstico narrativo como frase fija cuando se comparen dos porcentajes.
3. **Bloque E con contexto de calendario.** Si las derrotas del E3 fueron
   contra los de arriba de la tabla, se dice («E en 0 hecho contra el top 4»).
   El número no cambia; la lectura del partido ante un rival de su franja,
   sí. C4 ya tenía «explicables por calendario»; el E no lo tenía.

### 6. EJE-DEBUTANTE entra a la rúbrica del clasificador, con la pareja de un solo partido

**Lo medido.** La alerta existe en `efe-dashboard` v1.9 (F6: ≥ 2 titulares de
la misma línea con **0 minutos juntos**) y en el DTP, pero **no en la
rúbrica del clasificador**, que es la que puntúa. En esta tanda la grieta de
las parejas nuevas se cumplió en seis casos:

- **Mainz:** la línea de tres con parejas que arrancaron juntas **una sola
  vez**; los dos penales los cometieron los de la pareja nueva.
- **Bolívar:** una línea de fondo con **un solo partido** junta pesó más que
  los bloques B y C altos.
- **Hamburgo:** el medio de parejas nuevas no sostuvo la salida.
- **Peñarol:** el medio rearmado no generó un remate al arco en el primer
  tiempo.
- **Club Queretaro:** la línea rearmada concedió por balón al área.
- **Manchester United:** zaga de urgencia.

Mainz y Bolívar **no habrían activado** la alerta con el umbral de 0 minutos.

**Propuesta:**

1. **Alta de EJE-DEBUTANTE en las alertas por fecha del clasificador.** Es
   declarativa y sin peso, como GK-FALLA-ACTIVA: amplía el rango y baja al DTP
   como vía del rival. Se activa con ≥ 2 titulares de la misma línea (pareja
   central, dupla de pivotes o línea de fondo) que **no compartieron más de
   un partido como titulares** en la competición.
2. ⚠️ **Esto mueve un umbral** (de 0 a ≤ 1 partido juntos). Es el de una
   alerta sin peso, que no toca el porcentaje. Si se aprueba, la app lo
   acompaña: `dtp_cowork._parejas_nuevas` pasa de «nunca juntos» a «≤ 1 vez
   juntos», con su test.
3. **Las posiciones de la línea se leen del grid del once**, no de la
   posición de la plantilla. Caracas: el EFE llamó «eje central» a dos
   defensas que en el once jugaron de laterales, y el gol entró por la espalda
   de uno de ellos.

### 7. T.54 con interino que repite el once, y el C4 por condición

**Lo medido:**

- **Defensor Sporting:** el C4 y el D3 del DT cesado se dejaron sin dato por
  T.54, y el patrón de perder ventajas se repitió con el interino (3-1 → 3-3)
  con **10 de 11 del once**. El cierre de partidos era del plantel.
- **Antwerp:** la serie de cinco derrotas con el DT de agosto se leyó como
  señal del equipo actual y se cortó 3-0. Con pocos partidos, la serie del DT
  nuevo amplía el rango.
  - Santos Laguna (seis victorias) y Blooming (siete sin ganar) sí la
    sostuvieron, porque eran series más largas.
- **Mainz:** el 69 % contra el 61 % no veía que en casa recibió 3, 4 y 3 con
  cero victorias de local.
- **Toluca:** perdió la ventaja a los 6 y 10 minutos de ponerse arriba en dos
  partidos seguidos, y el C4 seguía en «ocasionales».

**Propuesta:**

1. **T.54, matiz al punto 1** (todo lo heredado va `sin dato`). Si el DT
   nuevo o el interino **repite ≥ 9 de 11** del once del DT anterior, el C4 y
   el D3 heredados **no se borran**: van a la caja de sensibilidad como
   patrón del plantel («el cierre de partidos es de los jugadores»). El
   número sigue en `sin dato`.
2. **T.54, matiz al punto 2** (la serie del DT nuevo es la señal). Con
   **menos partidos que la ventana de validación de T.54-B (6-8)**, la serie
   del DT nuevo **amplía el rango en las dos direcciones** y no fija la
   dirección. Desde la ventana, es la señal del equipo. No es un número
   nuevo: es la ventana que la rúbrica ya tiene.
3. **C4 se puede declarar por condición** cuando la asimetría local/visita es
   clara (Mainz). **Dos pérdidas de ventaja seguidas** pasan el C4 de
   «ocasionales» a patrón (Toluca).

## Lo que NO se propone

- **Ningún peso, máximo ni corte de clasificación.** Ninguna lección lo pide.
- **El tope del bloque D por D3 ❌** se revisa con el backtest, no con esta
  tanda.
- **Patrón disciplinario como vulnerabilidad** (Pumas: cinco rojas en 12
  fechas, sin casillero en el EFE). Un caso, más el de Elliott. Queda anotado
  como candidato para la próxima.
- **G-BLOQUE condicionado al dibujo del once.** Se emitió dos veces sobre un
  bloque bajo que no salió (Remo, Juventud), y D1 ya pide declarar el sistema
  en las dos fases (Elche). Dos casos. Queda candidato: «G-BLOQUE se emite
  condicional hasta el once».
- **GK-DOWNGRADE contra élite con un solo precedente** (Feyenoord: Ernst fue
  la figura). El criterio 3 («evidencia de degradación») ya no se cumple con
  un partido. Se agrega la aclaración en el texto, sin regla nueva.

## Cómo se aplica si se aprueba

1. Se redacta `references/rubrica-efe-v1.7.md` con el changelog, y se
   actualiza el `SKILL.md` a v1.7.
2. **App:**
   - `lecciones.CORTE_VERSION["efe-clasificador"]` suma `("v1.7",
     "2026-10-25")`, para que el botón «Cerrar las anteriores» cierre estas
     168 en v1.7.
   - Si se aprueba el umbral del cambio 6, `_parejas_nuevas` pasa a ≤ 1 vez
     juntos, con su test.
3. **`efe-dashboard`**: su F6 cita la regla del clasificador (≤ 1 partido
   juntos) para que los dos digan lo mismo.
4. **`docs/COWORK.md`**: el prompt suma tres líneas.
   - La jerarquía de fuentes del F1.
   - La rama «once alternativo» con calendario exigente.
   - Que la brecha de porcentaje no se lee entre bases distintas.
5. Zip para subir a la cuenta.
