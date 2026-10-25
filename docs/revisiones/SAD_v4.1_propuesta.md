# Propuesta de revisión · `sad-analysis` v4.0 → v4.1

**Estado:** PROPUESTA, pendiente de aprobación del usuario. Redactada el
25/10/2026. Parte de la v4.0 vigente (`docs/skills/sad-analysis/SKILL.md`,
21/10). Toca **solo el paso 6** (la síntesis: cómo salen las probabilidades
1X2) y agrega una regla de lectura en la Ley 4. No toca la Ley 1, la espina, el
reventón ni ningún número calibrado de la app.

## De dónde sale

El eje es la **calibración del 1X2 declarado** (`pronostico.probabilidades`).
El 1X2 es lo único del skill que se mide contra el resultado (Brier de tres
resultados), y esta revisión toca solo eso. Los skills no se juzgan por
ganarle al mercado, pero el mercado sirve de referencia para saber de dónde
sale el error.

- **Datos.** Se leyeron todos los partes con veredicto por la API: la lista
  salió de `GET /analisis/cowork/revisor?horas=336` y de
  `GET /analisis/cowork/lecciones?limite=2000`, y cada parte de
  `GET /analisis/cowork/{id}`. De ahí salen 295 veredictos jugados y
  **260 de población `ciega`** (los 260 son PRE): 236 de la cohorte vigente
  `c3-2026-09-23`, 22 de rodaje y 2 de `c2`. Van del 14/09 al 24/10/2026.
  - Se usa solo la población ciega. Los 35 por/post resultado quedan fuera.
  - El usuario contó 317. La diferencia son 42 fixtures de lecciones que
    responden 404, casi todos estudios de reventones (`rev:`) sin parte.
  - Probabilidad declarada: `veredicto.objetivo.unXDos.reparto`.
- **Mercado.** Sale de `GET /cuotas/{id}/historial`: el último 1X2 capturado
  **antes de que se depositara el parte** (`creadoEn`), sin margen. Hay 231
  de 260 partes con captura. `pronostico.mercado` es texto, así que no se usó
  como número.
- **Motor.** Se tomó el `unXDos` escrito en el texto de `pronostico.motor`.
  Hay 66 partes desde el 11/10 que traen el motor y el mercado a la vez.
- **Método.**
  - Brier de tres resultados: 0 es perfecto y 2 el peor.
  - Intervalos de Wilson al 95 % para el acierto.
  - Bootstrap pareado (4.000 remuestreos) para las diferencias de Brier.
  - **Validación honesta**: se ordenan los partes por fecha, se ajusta en la
    primera mitad (130 partes, 14/09 → 18/10) y se mide en la segunda (130
    partes, 18/10 → 24/10).
  - Las reglas que no tienen ningún parámetro ajustado se miden además en la
    muestra entera.

## Lo medido

### El empate: lo decimos de más y no lo distinguimos

| | dicho (media) | pasó | en los empates reales | en los no-empates |
|---|---|---|---|---|
| Nuestro 1X2 (260 ciegas) | **27,1 %** | **20,4 %** (IC 15,9-25,7) | 28,3 % | 26,8 % |
| Cohorte c3 (236) | 27,5 % | 22,0 % (IC 17,2-27,7) | 28,4 % | 27,3 % |
| Mercado sin margen (231, mismos partes) | 25,0 % | 19,9 % | 26,3 % | 24,6 % |

- **El empate fue pick 1 vez en 260.** El mercado no lo eligió ninguna. Esto
  no es un defecto: el empate casi nunca es el resultado más probable.
- **Ninguno de los dos distingue el empate.** En los empates reales nosotros
  le dimos 1,5 puntos más que al resto y el mercado 1,7. Ninguna regla escrita
  va a separar los empates con este n.
- **El exceso sí es nuestro.** Ponemos el empate **2 puntos por encima del
  mercado** (+2,2 en c3), en el mismo partido.
- **La frecuencia observada es baja también por azar.** Fue 17,7 % en la
  primera mitad y 23,1 % en la segunda. El motor da ~28 % de empate a un
  partido parejo (la logística de §5.6 con d = 0). Por eso **no se propone
  bajar el empate a la frecuencia de la cohorte**: se propone dejar de ponerle
  encima del mercado.

### El pick, por tramo: subconfiados arriba, porque recortamos al favorito por debajo del mercado

Las 260 ciegas, con el acierto del pick e IC de Wilson al 95 %:

| tramo del pick | n | decimos | acierta | IC 95 % | el mercado, en esos mismos partes |
|---|---|---|---|---|---|
| < 40 | 55 | 37,5 | 34,5 % | 23-48 | 39 |
| 40-49 | 117 | 43,9 | 47,9 % | 39-57 | 45 |
| 50-59 | 59 | 53,8 | **61,0 %** | **48-72** | **59** |
| 60+ | 29 | 66,9 | **89,7 %** | **74-96** | **72** |

En la c3 sola: 50-59, 33 de 54 = 61,1 % (IC 48-73); 60+, 19 de 21 = 90,5 %
(IC 71-97).

- **De los 78 picks de 50 % o más, 66 quedaron por debajo del mercado** en el
  mismo lado, 7,4 puntos de media. Esos 66 acertaron 45 veces (68 %).
- **La subconfianza no es del método; es el recorte.** Donde decimos 54, el
  mercado decía 59, y donde decimos 67, decía 72.
- **Pero el tramo 50-59 no se repitió en la segunda mitad.** Acertó 21 de 31
  (68 %) en la primera y 15 de 28 (54 %, dicho 54) en la segunda; en la c3,
  72 % y luego 48 %.
- **El 60+ sí se sostuvo**, con n chico: 15 de 16 en la primera mitad y 11 de
  13 en la segunda.

### Brier: nuestro, el motor y el mercado

| sobre | n | nuestro | mercado | motor (`unXDos`) |
|---|---|---|---|---|
| ciegas con mercado | 231 | 0,5848 | **0,5765** | — |
| con los tres a la vista (desde el 11/10) | 66 | 0,6318 | **0,6266** | 0,6664 |

- **Nuestro contra el mercado:** el intervalo cruza el cero. Es
  [−0,013 ; +0,023] en la segunda mitad y [−0,019 ; +0,028] en los 66.
- **Nuestro contra el motor:** le ganamos con claridad, −0,035
  [−0,060 ; −0,009].
- **La síntesis ya mejora al motor.** Lo que pierde contra el mercado es
  sobre todo el empate de más y el favorito recortado.

### Correcciones aplicadas hacia atrás (validación honesta)

**Ajustadas en la primera mitad, medidas en la segunda** (130 partes; el
Brier de lo declarado es 0,6065):

| corrección | parámetro ajustado | Brier 2.ª mitad | Δ [IC 95 %] |
|---|---|---|---|
| empate × 0,66 (a la frecuencia), repartido proporcional | s = 0,66 | 0,6083 | [−0,019 ; +0,023] |
| empate × 0,66, lo sacado al pick si ≥ 50 | s = 0,66 | 0,6083 | [−0,020 ; +0,024] |
| temperatura (estirar en logit) | T = 1,86 | **0,6172** | [−0,017 ; +0,040] |
| temperatura + sesgo del empate | T = 1,65, c = −0,24 | 0,6152 | [−0,019 ; +0,039] |
| empate tope 22 y pick ≥ 50 × 1,10 | a mano | 0,6087 | [−0,017 ; +0,023] |
| pick ≥ 60 +8 puntos | a mano | 0,6028 | [−0,008 ; +0,001] |

- **Todo lo que se ajusta a la cohorte empeora fuera de la muestra.** La
  temperatura es la peor: en la segunda mitad mete 47 picks al tramo 60+
  diciendo 73 % y aciertan el 55 %.
- **El estiramiento es sobreajuste a la primera mitad**, donde el 50-59 dio
  68 %.

**Sin parámetros** (el mercado del mismo parte como ancla, nada ajustado):

| regla | muestra entera (231) | 1.ª mitad (115) | 2.ª mitad (116) |
|---|---|---|---|
| declarado | 0,5848 | 0,5493 | 0,6198 |
| **empate = el del mercado** (lo sacado, proporcional a 1 y 2) | 0,5801 [−0,0093 ; +0,0002] | 0,5439 | 0,6161 [−0,0100 ; +0,0033] |
| **pick ≥ 60 no por debajo del mercado** | 0,5809 [−0,0074 ; 0,0000] | 0,5446 [−0,0078 ; −0,0021] | 0,6169 [−0,0094 ; +0,0044] |
| pick ≥ 50 no por debajo del mercado | 0,5815 [−0,011 ; +0,005] | 0,5427 | 0,6199 [−0,011 ; +0,012] |
| **empate = mercado + pick ≥ 50 no por debajo** | **0,5780** [−0,016 ; +0,003] | 0,5392 | **0,6164** [−0,016 ; +0,010] |

- **En la cohorte c3** (208), «empate = mercado» pasa de 0,5944 a 0,5887 con
  el intervalo **bajo cero**: [−0,0106 ; −0,0005].
- **Las reglas sin parámetro mejoran en las dos mitades**, poco y con
  intervalos que en la segunda mitad cruzan el cero. Es lo honesto con 116
  partes.
- **Con la combinada, los tramos quedan así** (231): <40 dicho 38 · pasa 39;
  40-49 dicho 44 · pasa 48; 50-59 dicho 56 · pasa 45; 60+ dicho 71 · pasa 82.
  El empate medio queda en 24,3 contra 19,9 observado.

## Lo que no se toca

- **La Ley 1, la espina (1.6) y el reventón (1.7)**: las K pesan el 60 % de la
  LECTURA y no entran al número.
- **Las tres fuentes a la vista y la disciplina 33.** Esta revisión las hace
  operativas, no las cambia.
- **El 1X2 del motor (`unXDos`) se sigue copiando tal cual** como fuente. Es
  la peor de las tres en Brier, pero es lo que la base calcula, y la síntesis
  ya lo mejora.
- **El mínimo del underdog** (paso 4: 5 / 10 / 15 %) y la Auditoría 1.
- **Ningún número de la app**: ni puntos del reventón, ni la guía de
  movimiento, ni el umbral 0,30.

## Los cambios propuestos

### 1. El empate parte del mercado y se aparta solo con un hecho del partido

**Lo medido:**

- Ponemos el empate 2 puntos por encima del mercado: 27,1 contra 25,0, y pasó
  el 20,4 %.
- Igualarlo al del mercado mejora el Brier sin ajustar nada. En la muestra
  entera, de 0,5848 a 0,5801; en la c3, de 0,5944 a 0,5887 con el IC bajo
  cero; en la segunda mitad, de 0,6198 a 0,6161.
- Ni nosotros ni el mercado distinguimos los empates (+1,5 y +1,7 puntos en
  los empates reales).

**Casos donde el empate SÍ pesaba más y se acertó leyéndolo, o se falló por no
leerlo:**

- **Flamengo–Estudiantes** (vuelta igualada, el empate de los 90 manda a
  penales). Le dimos 26 % y fue 0-0 con 76 % de pelota.
- **Köln–Schalke.** Ver el cambio 4: fue 0-0 con dos burbujas negativas cortas
  y la guía del cero en 0,27.
- **Lo que la v4.0 ya nombra en 1.6 (a):** dos perfiles DC apuntando al
  empate, dos burbujas negativas enfrentadas, un rival que empata la mitad de
  sus partidos.

**Redacción propuesta** (paso 6-B, nuevo inciso):

> **El empate parte del mercado** *(v4.1)*. El empate de `pronostico.probabilidades` arranca en el empate sin margen del mercado (sin mercado, en el de `unXDos`) y se aparta **más de 2 puntos** solo con un **hecho de ESTE partido** que empuje al empate o lo saque, nombrado en la lectura del 1X2: una eliminatoria donde el empate de los 90 tiene premio (penales, la ida a favor), un rival que defiende en bloque probado sin su ataque (cambio 4), los dos perfiles DC apuntando al empate, dos burbujas negativas enfrentadas. Un «partido parejo» o un margen de μ bajo 0,30 **no** son un hecho: el mercado ya los tiene. Medido en 231 partes ciegos (14/09-24/10/2026): decíamos el empate 2 puntos sobre el mercado (27 contra 25) y pasó el 20 %; igualarlo al mercado bajó el Brier de 0,585 a 0,580 sin ajustar nada. Ni nosotros ni el mercado distinguimos qué partido termina empatado: no se inventa un empate alto sin un hecho.

### 2. Un favorito de 50 % o más no se recorta por debajo del mercado sin dato propio

**Lo medido:**

- De 78 picks de 50 % o más, 66 quedaron por debajo del mercado del mismo
  lado, 7,4 puntos de media.
- En el 60+ decíamos 67, el mercado 72, y acertó el 89,7 % (26 de 29,
  IC 74-96).
- Subir el pick de 60+ al mercado mejora en las dos mitades. En la primera,
  0,5493 → 0,5446 con el IC bajo cero; en la segunda, 0,6198 → 0,6169.
- Con el piso desde 50 el efecto se diluye: el 50-59 no se repitió en la
  segunda mitad.
- Por eso la regla **es de procedimiento** (declarar el recorte y su dato) y no
  un número fijo.

**Casos de la cohorte:**

- **Recortes que fallaron:**
  - Rayo–Elche: 48 contra 54 del mercado, perdió 0-3.
  - Alavés–Málaga: 53 contra 55-58, empató 1-1.
- **Recortes con dato que el mercado no tenía, y valieron:**
  - Stuttgart–Gladbach: 70 → 60 por la rotación anunciada de 5+, perdió 2-3.
    La lección dice que el recorte fue en la dirección correcta y no alcanzó.
  - Betis–Feyenoord: 58 → 46 siguiendo un μ entre bases. Este falló; ganó el
    local. Es el contraejemplo: el dato era el motor con ESCALA-LIGAS, que no
    es un dato que el mercado no tenga.
- **La v4.0 ya lo dice para el descuento contra el mercado** (6-A: «pide un
  dato que el mercado no tenga»). La cohorte muestra que no se cumple: el
  recorte se hace por costumbre, no por dato.

**Redacción propuesta** (paso 6-B, nuevo inciso):

> **El favorito no se recorta por costumbre** *(v4.1)*. Cuando el mercado da al favorito 50 % o más y nuestro pick va al mismo lado, el número no queda por debajo del mercado salvo con un **dato que el mercado no tenga**, escrito con su cifra en la lectura del 1X2: «−N puntos al favorito por <el dato>». Valen el once oficial o la rotación confirmada después de la última captura, una baja estructural que salió después de la cuota y la Ley 3 confirmada. No valen el riesgo del reventón (1.7 a: frena la carga, no elige el lado), la espina contra el favorito, la localía cualitativa ni un μ con ESCALA-LIGAS. Medido en 231 partes ciegos: 66 de 78 picks de 50 %+ quedaron 7,4 puntos bajo el mercado; en el tramo 60+ dijimos 67 y acertó el 90 % (26 de 29, IC 74-96). La Auditoría 1 y el mínimo del underdog siguen valiendo: si los gatillos K piden no-victoria, se publican los dos números (disciplina 33), no se recorta en silencio.

Y una sexta pregunta en la **Auditoría 2**:

> 6. *(v4.1)* ¿El empate y el favorito están donde los pone el mercado? Si no, ¿qué dato de ESTE partido, que el mercado no tenga, los movió? Escribirlo con la cifra.

### 3. La tabla de calibración se lee, no se aplica como fórmula

**Lo medido:**

- Toda corrección ajustada a la cohorte empeoró en la segunda mitad:
  - temperatura: 0,6065 → 0,6172;
  - empate a la frecuencia: 0,6083;
  - pick ≥ 50 estirado: 0,6087.
- La tentación de «estamos subconfiados arriba, estiremos todo» es el
  sobreajuste: la primera mitad dio 68 % en el 50-59 y la segunda 54 %.

**Redacción propuesta** (paso 6-B, nota):

> **Calibración de la cohorte** *(v4.1)*. Las tablas de acierto por tramo del dossier son para leer de dónde sale el error, no para multiplicar el número. Estirar las probabilidades con un factor sacado de la cohorte (temperatura, «+N al favorito», «empate a la frecuencia») empeoró el Brier fuera de la muestra (validación por fecha, 25/10/2026). El 1X2 se corrige con las reglas del empate y del favorito (incisos v4.1), que no tienen ningún número ajustado.

### 4. Bajas del ataque rival: le quitan goles al rival, no le suman puntos al otro (Köln–Schalke)

**La lección** (`1575201:a`, ciega, c3, `fallo`, sad-analysis):

- Dice: «subir 8 puntos al local sobre el motor por las bajas del ATAQUE rival
  no paga cuando el rival defiende en bloque probado: las bajas ofensivas le
  quitan goles al rival, no puntos al local; con μ empatado (margen 0.01) el
  número se queda cerca del motor».
- Jev la etiqueta `lectura_efe` (0,76) con `proponeMoverNumero: true`. El
  0,81 que se citó no viaja en el GET de lecciones.
- El lado de Schalke (`1575201:b:4`, parcial) dice lo mismo desde la espina.

**Lo que pasó:**

- Köln dominó (62 % de pelota, 14 remates, xG 1,28) sin un 9 de área, Karius
  atajó tres claras y terminó 0-0.
- Declaramos 46 / 27 / 27. El motor daba 38 / 28 / 34 (con fiabilidad baja por
  ESCALA-LIGAS: Schalke recién ascendido) y el mercado 46 / 25 / 29.
- **Los +8 sobre el motor fueron, de hecho, ir al mercado.**

**Qué se sostiene y qué no:**

- **Se sostiene el mecanismo:**
  - Una baja ofensiva del rival baja SUS goles. Empuja al 0-0, al 1-0 y al
    empate, no a la victoria del otro, sobre todo si el rival es un bloque
    estructural probado (clase del DTP).
  - Va en la misma dirección que el cambio 1: es un hecho que sube el empate.
- **No se sostiene «el número se queda cerca del motor»:**
  - En los 66 partes con los tres a la vista, el motor fue la peor fuente
    (Brier 0,666 contra 0,632 nuestro y 0,627 del mercado). Nuestro contra el
    motor da −0,035 [−0,060 ; −0,009].
  - Con ESCALA-LIGAS, otras cuatro lecciones de la misma semana piden lo
    contrario, el mercado de ancla: Ipswich–Forest, Coventry–Fulham,
    Lille–Galatasaray y Betis–Feyenoord.
  - La v4.0 ya dice que con ESCALA-LIGAS μ «ni gobierna el 1X2».

**Otros casos del mismo tipo desde el 21/10** (lecciones de `sad-analysis` con
bajas o rotación en el porqué):

| caso | qué bajas | cómo se usaron | salió | ¿sostiene la regla? |
|---|---|---|---|---|
| Köln–Schalke (24/10) | ataque del rival | +8 al local | 0-0 | sí |
| Rayo–Elche (24/10) | Aguado, mediocampista del rival | espina positiva del local contra riesgo alto | 0-3 | sí: la baja del rival no sostuvo la racha |
| Alavés–Málaga (23/10) | las del propio Málaga | 1X2 y espina a que la racha negativa siguiera, con riesgo muy alto | 1-1 | sí: las bajas no alcanzaron contra el riesgo |
| Pachuca–Cruz Azul (22/10) | propias, defensivas (TF suspendido, EFE 38 contra 74) | espina negativa del local | 1-2, acierto | es el otro lado: las bajas **propias de la zona defensiva** sí mueven |
| Tigres–León (21/10) | propias, defensivas (IP > 7, zona rota) | espina «cero» | 0-2, fallo por quedarse corta | igual: las defensivas propias pesaron **más** de lo leído |
| Stuttgart–Gladbach (23/10) | rotación propia de 5+ | −10 bajo el mercado | 2-3 | rotación, no bajas sueltas: dirección correcta |

Son 6 casos. El patrón es coherente: **las bajas del ataque del rival no
suman, las defensivas propias sí restan**. Es un patrón, no una tasa.

**Redacción propuesta** (Paso 0.5, Ley 4, debajo de la tabla de escenarios):

> **Bajas del rival, por zona** *(v4.1)*. Una baja **ofensiva** del rival le quita goles al rival: sube el empate y las celdas bajas (0-0, 1-0), **no** le suma puntos de victoria al otro equipo, y menos si el rival es un bloque estructural probado (clase del DTP). Una baja **defensiva** (o del arquero, o una zona rota con IP alto) del propio equipo sí le resta, y suele pesar más de lo que se lee (Tigres–León, Pachuca–Cruz Azul). Köln–Schalke (24/10/2026): +8 al local por el ataque diezmado de Schalke, 0-0 con 14 remates de Köln contra un bloque probado. El mercado ya conoce las bajas publicadas (6-A): el ajuste propio por bajas se escribe con la zona y va al empate o al marcador, no al favorito.

**No se adopta** la frase «el número se queda cerca del motor». Contradice lo
medido en los 66 partes y las lecciones de ESCALA-LIGAS. La lección se marca
`aplicada` en v4.1 por el mecanismo, con esa reserva en la nota.

## Lo que NO se propone (n chico o sin base)

- **Ningún factor de estiramiento** (temperatura, «+N al favorito», tabla de
  corrección por tramo). Empeoran fuera de la muestra (cambio 3).
- **Bajar el empate a la frecuencia de la cohorte** (20-22 %). El IC de la
  frecuencia (15,9-25,7) contiene al mercado, las dos mitades difieren 5
  puntos y el motor da ~28 % a un partido parejo. Se ancla al mercado, no a la
  cohorte.
- **Un número para el piso del favorito desde 50 %.** El 50-59 acertó el 68 %
  en la primera mitad y el 54 % en la segunda (dicho 54). Con 59 partes el
  intervalo va de 48 a 72: no hay subconfianza demostrada en ese tramo.
- **Conclusiones del tramo 60+ más allá del procedimiento.** Son 29 partes (21
  en c3). El 89,7 % tiene un intervalo de 74 a 96 y el mercado, en sus 50
  partes de 60 %+, acertó el 82 %.
- **Mezclar con el mercado por un peso fijo.** El peso propio que mejor ajusta
  en la primera mitad es 0,15 (0 en la c3), es decir, copiar el mercado. El
  pronóstico es la síntesis del analista, y el skill no se juzga por ganarle
  al mercado. Las reglas 1 y 2 usan el mercado como **punto de partida que se
  mueve con dato**, no como respuesta.
- **Una regla para distinguir los empates.** Nadie lo hace con este n, tampoco
  el mercado.
- **El mínimo del underdog** (paso 4). Podría estar empujando el recorte del
  favorito, pero no se puede medir con los campos actuales: el parte no dice
  qué factores contó.
- **Mover un número por la lección de Köln–Schalke.** Es n = 1 en lo numérico,
  y los +8 coincidían con el mercado.

## Cómo seguirlo

- **El recibo del parte podría avisar** cuando el empate se aparte del
  mercado más de 2 puntos, o el pick de 50 %+ quede debajo, sin una frase
  «por <dato>». Sería como `matrizVsPronostico`, y para eso el mercado tendría
  que viajar como número en el parte. **No se propone ahora**: primero el
  texto del skill.
- **Re-medir con la cohorte** cuando haya 150 partes ciegos depositados con la
  v4.1. Es la misma tabla (tramo, empate, Brier contra el mercado del mismo
  parte), con la validación por fecha.

## Cómo se aplica si se aprueba

1. Apruebas o corriges los cambios 1 a 4. El 4 sin la frase del motor.
2. Redacto `sad-analysis` v4.1 en `docs/skills/sad-analysis/SKILL.md`. Son
   tres incisos en 6-B, la pregunta 6 de la Auditoría 2 y la regla de bajas en
   la Ley 4, con la cabecera de versión.
3. El prompt (`docs/COWORK.md`) apunta al skill donde repite el armado del 1X2.
   No hay ningún campo nuevo en el parte.
4. Te entrego el `.zip` y marcas con 🔑 la lección `1575201:a` (y
   `1575201:b:4`) como `aplicada` en v4.1.
