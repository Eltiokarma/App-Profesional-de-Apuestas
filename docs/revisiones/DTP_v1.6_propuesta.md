# Propuesta de revisión · `diagnostico-tactico` v1.5 → v1.6

**Estado:** PROPUESTA, sin aprobar. Redactada el 26/10/2026 a partir del
dossier (`GET /analisis/cowork/revision/diagnostico-tactico`, cohorte
`c3-2026-09-23`) y de las lecciones abiertas del skill. Parte de la v1.5
vigente (25/10), que está en `docs/skills/diagnostico-tactico/SKILL.md`. No se
tocaron el skill ni el estado de ninguna lección.

## De dónde sale

- **Ventana:** las 123 lecciones abiertas, todas de partidos del 25/10/2026.
  Vienen de 30 partidos y se reparten así:
  - 45 fallos;
  - 32 parciales;
  - 46 aciertos, que también son lecciones: confirman reglas.
- **Población:** las 123 son `ciega` + `PRE` y acreditan.
  - En el dossier, el skill suma 85 casos ciegos.
  - El 1X2 acertó 39 de 83 (47 %).
  - El Brier es 0,615 y la línea de base, 0,653.
- **Ninguna lección pide mover un número.** Jev no marcó ninguna con
  `proponeMoverNumero`. Igual que la v1.4 y la v1.5, esta revisión fija
  rúbrica.
- **Versión que leyó cada parte.** Los tres partes de la noche del 24/10
  (Pereira, Monterrey y Pumas) se escribieron con la v1.4. El resto se
  depositó el 25/10 entre las 10:00 y las 15:46 de Lima, el mismo día en que
  se subió la v1.5. Las lecciones citan la v1.5 en 14 casos y la v1.4 en 5.
  Algunos incumplimientos de reglas que la v1.5 ya tenía pueden venir de
  partes escritos con la v1.4. Lo marco donde importa (cambio 4).
- **Fuente:** el texto entero de las 123, agrupado por la regla que tocan:

  | Regla | Lecciones |
  |---|---|
  | M2 (vías de gol, carriles, dos capas, veredicto) | 56 |
  | Checklist del bloque (casi todo la pregunta 6) | 27 |
  | Regla del estado de marcador | 10 |
  | M1 | 10 |
  | MECANISMO-ABIERTO | 9 |
  | Otras: M3, M4, DTP-REHACER, candidatos | 11 |

### Primero, una corrección: «DTP-REHACER sonó y no se rehízo»

Doce lecciones dicen «sonó DTP-REHACER y no se rehízo». Pertenecen a Boston
River, Torque–Cerro, Aurora, Leones del Norte, Rennes, Marsella, Le Mans,
Monterrey, Pereira, Toulouse, Sunderland y Gent.

**En la mayoría no es así.** El 25/10 la rutina de rehacer rehízo 18 partes
antes del pitazo, entre ellos Torque–Cerro. La alerta que vio el veredicto
apareció **después del último disparo** de la rutina. El once se vuelve a
pedir a 15 minutos del pitazo, y en ese pedido la API corrigió la formación
(Cerro: 4-2-3-1 → 4-3-1-2) o trajo una que antes no tenía (Marsella: «la
ficha no trae la formación»).

Esto se arregló en el backend (PR #244, 26/10):
- Cada versión del once queda con su hora.
- Jugado el partido, DTP-REHACER trae `momento`: `tardio`, `sinRehacer` o
  `conocido`.
- Los partidos con parte vuelven a pedir el once a 40 minutos del saque.
- El skill de la corrida ya no carga un `tardio` como lección.

Esas doce lecciones **no piden nada a esta capa**. Lo que sí muestran, y
coincide en todas, es que **la capa estructural sobrevivió** (carril, centro,
pelota parada) y **la capa de nombres cayó**. Es exactamente lo que dice la
regla de las dos capas de la v1.4. Cuentan como confirmación.

## Lo que esta capa acierta (no tocar)

- **El banco ofensivo, vía de los dos lados (v1.5).** Se confirmó en unos
  diez partidos:
  - Always Ready: el 3-1 y el 5-1 los hicieron suplentes.
  - Rio Ave–Famalicão: Aranda y Pedro Santos.
  - Aucas–Barcelona SC: los tres goles del 82' en adelante.
  - Atlas–Puebla: un juvenil que entró al 67' e hizo dos.
  - Marsella–Le Havre, Sunderland–Leeds, Freiburg–Bayern, Cerro Largo,
    San Lorenzo–Cerro y Once Caldas.
  - Un caso a favor del matiz de la v1.5: Torque–Cerro, donde el banco
    también lo usó el favorito.
- **La quinta línea (v1.5), el error en la salida bajo presión:**
  - Marsella: el 4-0 nació de un mal despeje.
  - Monterrey–Chivas: el robo en la salida de un central.
  - El contraste es Barcelona–Real Madrid: el Madrid salió en largo a Mbappé y
    la línea no aplicaba. La condición de la v1.5 («el equipo sale jugando
    desde atrás») ya lo cubre.
- **El carril escrito en las dos direcciones (v1.4/v1.5):**
  - Freiburg–Bayern: la ida dio el 0-2 y la vuelta, el 1-2.
  - Lecce–Juventus: la vuelta del carril izquierdo dio el 0-2.
  - Udinese–Milan, Auxerre–Le Mans y Real Sociedad–Levante: la zona se
    sostiene aunque cambie quién la ataca.
- **MECANISMO-ABIERTO con régimen (v1.5):**
  - El de Sporting, heredado de LASK y condicional a «persiguiendo», se puso
    a prueba y se cumplió (el 1-2 del 74').
  - Gent, Rio Ave y Aucas lo declararon bien en el cierre.
  - `sin mecánica` se aplicó tal cual en Torque, Leones y Atlas.
- **`sostuvoArquero` en el caso de la 6 (v1.5).** Separó el bloque del
  arquero en Leones (7 atajadas), Guayaquil City (9), Bayern (Urbig),
  Chivas (penal atajado) y Pereira (11). Ninguno se promovió a «probado».
- **La vida útil del improvisado como techo (v1.4)** se volvió a ver:
  - San Lorenzo cayó al 5'.
  - Strasbourg cayó al 34'.

## Los cambios propuestos

### 1. El veredicto del M2 se escribe en las dos ramas

La v1.5 pidió que el veredicto **dijera** en qué rama se apoya. En la
práctica se escribe un solo veredicto, el de la rama «igualado o arriba». El
partido se jugó en la otra rama en seis casos:

- **Sporting–Viseu:** FAVORABLE apoyado en «igualado o arriba»; Sporting
  persiguió desde el 24'. Tuvo 28 remates contra un bloque bajo de plan
  (29 % de pelota) y la vía del rival siguió viva.
- **Rio Ave–Famalicão:** NEUTRO apoyado en «si Famalicão se vuelca, manda la
  transición local». Se jugó la rama inversa: el local persiguió desde el 48'
  y decidió la transición del rival.
- **Nacional–Braga:** el FAVORABLE del Braga se apoyaba en «igualado o
  arriba» y se jugaron 71 minutos persiguiendo contra un bloque de cinco.
  La posesión persiguiendo estaba bien declarada (65-70 %, terminó 71 %),
  pero el veredicto no decía qué ganaba en esa rama, y ahí no tuvo vía (dos
  remates a puerta).
- **Toulouse–Troyes:** el FAVORABLE dependía de que Troyes saliera. No salió
  (37 %) y el 2v2 dio 0,7 de xG.
- **Auxerre–Le Mans:** «el local cede y ataca en transición». El ascendido
  cedió (40 %) y al local le tocó atacar en posicional, con 0,82 de xG.
- **Barcelona–Real Madrid:** «que el Madrid ceda la pelota» se cumplió (38 %)
  y el Barça igual concedió 2,01 de xG.

**Regla propuesta.** El M2 escribe **dos veredictos**: uno para «igualado o
arriba» y otro para «persiguiendo», cada uno con su razón táctica y la vía
que tendría el foco en esa rama. El campo `veredicto` de siempre queda como
el de la rama más probable. El chequeo de régimen del M5 juzga **el de la
rama que se jugó**.

Dos precisiones:
- **Que el rival ceda la pelota no es una señal a favor del foco.** Puede ser
  su plan. Toulouse, Auxerre y Barça lo trataron como señal favorable y
  fue lo contrario. Si el rival puede administrar con un bloque bajo, el
  veredicto «persiguiendo» dice con qué vía se ataca ese bloque, o dice que
  no la hay.
- **Un veredicto con condición** («si Troyes sale») escribe también qué pasa
  si la condición no se cumple.

En el parte: `m2.veredictoRamas = {igualadoOArriba: {veredicto, razon},
persiguiendo: {veredicto, razon}}`. Es la misma forma de dos ramas que ya
tienen `posesion` y `restDefense`. Es el mismo problema que corrigió el TDE
v0.1.24 con el `desenlace` de las ramas del que persigue: el primer gol
decide en qué rama se juega, y las dos ramas tienen que estar escritas.

### 2. El área se ataca también desde el lado débil y desde la segunda línea

La línea 2 de vías de gol (v1.4) cuenta «a todos los que atacan el área,
centrales incluidos». En cinco partidos el gol lo hizo **el que llega al
segundo palo desde el lado débil** o **el que llega de segunda línea**, y no
la referencia ni los centrales que se habían nombrado:

- **Nacional–Liverpool:** el duelo escrito era Coates contra Martínez. El
  cabezazo cayó en el segundo palo sobre el carrilero del lado débil
  (Martirena). En un espejo 3-4-1-2, el segundo palo lo defiende ese
  carrilero.
- **Sporting–Viseu:** los dos goles los hizo el extremo del lado débil
  cerrando en el segundo palo, a la espalda del carril derecho. La vía estaba
  escrita con Clóvis (la referencia) como destinatario.
- **Real Sociedad–Levante:**
  - El 1-1 llegó por la vuelta escrita y lo remató el **lateral contrario**
    (Nacho Pérez) llegando al segundo palo.
  - El 2-1 lo definió el **pivote que llega de segunda línea** (Turrientes),
    una vía que no figuraba.
- **Lecce–Juventus:** en un tiro libre ensayado, el que atacó el área fue el
  **interior que llega** (McKennie), no los centrales nombrados.
- **Pumas–Tigres:** la vía de los centros con Morales llegando se cumplió,
  pero el centro fue raso desde la izquierda, no aéreo.

**Regla propuesta.** La línea 2 se amplía:
1. Se escribe **quién llega al segundo palo desde el lado débil** (carrilero,
   extremo o lateral contrario) y **quién lo defiende**.
2. Se escribe **la llegada de segunda línea** del interior o del pivote,
   cuando el rival deja espacio entre medios y centrales. Esto vale también
   en pelota parada.
3. **El centro se nombra por su zona de origen y por su altura** (raso o
   aéreo), no solo por el rematador.

### 3. M1: el sistema y los carriles salen del último once oficial y su grid

Los insumos del DTP (`GET /analisis/cowork/dtp/{id}`, `partidoAnterior.xi`)
ya traen la formación del último once oficial y el carril de cada titular.
Aun así, la apertura tomó el sistema de la previa o del dibujo habitual en
cuatro casos:

- **Emelec–Guayaquil City:** la apertura leyó un 3-4-2-1 con línea de tres a
  partir de un once cuyo grid trae cuatro en la línea de fondo y 4-3-1-2.
  Todos los duelos se escribieron contra carrileros que no había.
- **Aucas–Barcelona SC:** el mapa puso a Wila y Castillo en el mismo carril.
  En el once oficial jugaban en bandas opuestas, y Castillo asistió el 0-1.
- **Torque–Cerro:** el lateral derecho (grid 2:4) aparecía en el carril
  izquierdo, y un duelo nombraba a un jugador que no estaba en la hoja.
- **Rennes–Strasbourg:** después de recibir cuatro goles, el DT pasó a línea
  de tres y la mantuvo. La apertura tomó el 4-3-3 habitual de liga y no el
  5-3-2 del último once.

Y dos casos en el sentido contrario, donde el último once no debía mandar
solo:

- **Pumas–Tigres:** la apertura adoptó un 5-4-1 que había nacido de jugar
  con diez desde el 2'. El DT volvió al 4-4-2.
- **Nacional–Braga y Angers–Lorient:** el EFE traía la línea de cinco del
  interino en su caja de sensibilidad (Nacional), o la señal del once
  anunciaba la vuelta de tres titulares de la línea de fondo (Angers). El
  mapa se escribió sobre una sola versión y describió un partido que no se
  jugó.

**Regla propuesta.**
- El sistema de M1 y los carriles de los duelos se toman del **último once
  oficial con su grid**, el que dan los insumos.
- Apartarse de él es una decisión que se escribe, con su fuente: «el DT
  anunció…», «la previa del club…».
- Dos excepciones:
  - **Un sistema nacido de una expulsión temprana** no fija el del partido
    siguiente. Manda el anterior a la roja y se declaran las dos variantes.
  - **Cuando el EFE trae otra línea en su caja de sensibilidad, o la señal
    del once anuncia regresos en una línea**, M1 escribe la forma sin balón
    en las dos variantes. Es la misma regla de las dos versiones que la v1.5
    aplicó a la rotación en M6.

En el backend: el recibo **avisa** cuando `m1.sistema` es distinto de la
formación del último once oficial y el parte no dice por qué. Es un aviso,
no un rechazo, porque el DT puede cambiar. Va en el recibo con el código
`M1-VS-ULTIMO-ONCE`.

### 4. El ejecutor de penales sale de la base

La v1.5 ya pide nombrar al ejecutor en las dos direcciones y nunca «sin
dato». Aun así faltó en seis partidos, y en cinco de ellos el penal se pateó:

| Partido | Qué se escribió | Quién pateó |
|---|---|---|
| Portuguesa–Carabobo | «sin fuente» | E. Ramírez, el 9 en racha |
| Torque–Cerro | sin nombrar | el 9, que lo erró |
| Always Ready–Real Oruro | «Bravo por jerarquía» | el central Corulo |
| Union SG–Cercle | «sin fuente» | Ngoura, el 9 de referencia |
| Marsella–Le Havre | sin nombrar | Maja |
| Monterrey–Chivas | «sin dato» en los dos lados | Ocampos, y Rangel lo atajó |

Solo Monterrey–Chivas se escribió con la v1.4 (noche del 24/10). Los otros
cinco son del 25/10. Es incumplimiento, y se repite porque el dato **hay que
salir a buscarlo**, aunque **está en nuestra base**: los goles de penal y los
penales errados de la temporada están en los eventos.

**Regla propuesta.**
- El ejecutor sale de los insumos: el que más penales tiró en la temporada,
  con sus convertidos y errados.
- «Por jerarquía» no es una fuente.
- Si el arquero rival atajó penales en la temporada, se anota al lado del
  ejecutor (Monterrey–Chivas).

En el backend:
- Los insumos del DTP traen `penales` por equipo (ejecutores de la temporada,
  convertidos y errados, desde los eventos).
- El recibo avisa si `viasGol` no nombra al ejecutor de los dos lados.

Es lo mismo que pide la nota de costo de la IA: lo que está en la base se
calcula, no se le pregunta al modelo.

### 5. La pregunta 6 lleva la sede y la competición; y dos precisiones a la 1 y la 5

**La sede.** Desde la v1.4 la pregunta 6 exige un caso «en sede y
competición comparables». En dos partidos se respondió con un caso de la
otra sede:

- **Leones del Norte–Libertad:** el bloque de cinco de Libertad se clasificó
  «estructural y probado» con el 4-0 a Guayaquil City de **local**, en Loja.
  Hoy jugaba de visita: debió quedar «estructural no probado», con la alerta
  de degradación. Concedió tres entre el 58' y el 90+6'.
- **Lecce–Juventus:** la 6 se respondió con un caso de visita en Udine,
  aunque la nota decía «hoy es local».

El caso del cierre (`cierre.casoBloque`) no trae ni la sede ni la
competición, así que la apertura siguiente no puede comprobarlo.

**Regla propuesta.**
- `casoBloque` suma `sede` (`local`, `visita` o `neutral`) y `competicion`.
- Al leer, la app compara el caso que se cita con la sede y la competición
  de hoy.
- Si la 6 se respondió del lado estructural con un caso de la otra sede, el
  recibo lo avisa.
- La regla no cambia; lo que se agrega es la comprobación.

**Las dos precisiones**, un caso cada una, que encajan en reglas que ya
existen:

- **La pregunta 1 mide el modelo, no al DT** (Rio Ave–Famalicão). El bloque
  de Famalicão se clasificó improvisado porque el interino llevaba seis días,
  pero el 4-2-3-1 venía heredado y el D1 del EFE estaba en ✅. Sostuvo el
  0-1 durante 42 minutos con 0,66 de xG del rival. Un interino que no toca
  el modelo no reinicia la 1. Es la trampa frecuente que el skill ya
  describe («el dibujo cambió pero el modelo no»), aplicada al banco.
- **Un repliegue anunciado por el DT es plan** (Nacional–Braga). La pregunta
  5 se respondió «reacción» cuando el interino había declarado el plan
  («vamos ter de sofrer»). Nacional sostuvo 71 minutos sin depender del
  arquero. Un plan de repliegue anunciado por el DT, sea interino o no, va
  en la columna del plan.

### 6. Tres candidatos que ya juntaron sus casos

- **(a) El costo de rearmar la línea. Tercer caso: se propone como regla.**
  - Casos:
    - Sarmiento (v1.4).
    - Manta–Cuenca (v1.5): el 0-2 llegó dos minutos después del doble
      cambio.
    - Nacional–Liverpool (25/10): la línea de tres se rearmó tras la lesión
      de un central, el cambio se demoró, y concedió por el segundo palo
      mientras duraba el rearme.
  - Regla, en M3, tramo 65-80'+:
    - Un cambio obligado que rearma la línea (lesión de un central, doble
      cambio en la defensa) abre un tramo en el que la línea concede.
    - El plan dice quién entra y cómo se reordena.
    - El cierre lo anota como vía del rival en ese tramo.
- **(b) El rol reasignado con carga de tarjetas. Segundo caso: se propone
  como precisión de M1.**
  - Casos:
    - Grau–ADT (v1.5).
    - Aucas–Barcelona SC (25/10): R. Quiñónez, central adelantado a interior,
      llevaba amarilla desde el 40' y vio la segunda al 70' por una falta
      sobre Wila, la pieza de transición que nombraba el M2.
  - Precisión: un reasignado que persigue al velocista rival es **vía de
    expulsión**. Se nombra junto con sus amarillas recientes.
- **(c) El remate de media distancia contra un bloque estructural. Segundo
  caso: se propone como precisión de vías de gol.**
  - Casos:
    - LDU–Macará (v1.5).
    - Once Caldas–Pereira (25/10): contra un bloque que no concede
      transiciones, el rival marcó con un remate de más de 30 metros de un
      suplente.
  - Precisión: cuando el bloque del foco es estructural, entre las vías del
    rival va el remate de media distancia, con su ejecutor.

Con dos casos, (b) y (c) pueden quedar como candidatos si el usuario
prefiere el corte en tres que tuvo (a). Se aprueban por separado.

### 7. M5 separa volumen de conversión

En tres cierres, el mapa produjo lo que decía y el marcador no lo reflejó, y
el veredicto contó como fallo del M2 lo que fue definición o un arquero:

- **Emelec–Guayaquil City:** el FAVORABLE se cumplió en el juego (30 remates
  y 2,35 de xG contra una línea rearmada). Falló en el marcador por la
  definición y por las 9 atajadas de Napa.
- **Sunderland–Leeds:** el «golpear temprano» del 0-25 se dio. Brobbey quedó
  dos veces solo ante Trafford y las cerró el arquero, no el plan.
- **Sporting–Viseu:** 28 remates sin convertir en la rama «persiguiendo».
  Este caso pertenece también al cambio 1.

**Regla propuesta.**
- El chequeo de régimen del M5 juzga el veredicto por **lo que generó la rama
  que se jugó**: remates, xG y ocasiones claras.
- La conversión y el arquero rival se anotan aparte, como varianza, con el
  mismo criterio de `sostuvoArquero` de la pregunta 6 pero del otro lado.
- Así un M2 que acertó el partido no se carga como fallo.

## Lo que NO se propone

- **Ningún número:**
  - la vida útil (55-65 y 80-90 minutos);
  - el ≥ 80 % de intérpretes de las parejas;
  - el ≥ 2 errores del arquero;
  - el umbral de ≥ 2 goles en ≤ 15 minutos.
- **La magnitud de la posesión por rama.** Hay cuatro casos y apuntan a
  lados distintos:
  - Gent y Cerro Porteño, que ganaban temprano, cedieron mucho más pelota de
    lo declarado (37 % y 47 %).
  - El Milan, ganando desde el 6', no la cedió: Udinese, persiguiendo, tuvo
    40 %.
  - San Lorenzo, colista y perdiendo contra el favorito, tuvo más pelota de
    la declarada (53 % contra 42 %).
  - La regla de las dos ramas acertó la **dirección**. Calibrar la
    **magnitud** pide más casos.
- **La quinta línea cuando el rival sale en largo** (Barcelona–Real Madrid).
  La condición de la v1.5 ya lo excluye.
- **DTP-REHACER:** se resolvió en el backend (PR #244). No pide nada al
  skill.
- **La herencia del SOB2 desde la rama «persiguiendo»** sigue siendo una
  decisión pendiente del usuario, como en la v1.5.
- **La incidencia 634, del modo `rehacer`.** Cuando el once cambia quién
  sostiene el rest defense, cambiar el nivel en el DTP dispara HERENCIA-DTP
  contra el TDE. A minutos del pitazo el TDE no se rehace, así que los
  subagentes dejaron el nivel viejo (Portuguesa–Carabobo, Central
  Córdoba–Vélez). Es del pipeline (`corrida-sad` y el backend), no de esta
  capa. Hay dos salidas posibles:
  - que el modo `rehacer` corrija también el SOB2 del TDE heredado;
  - que la alerta diga que el TDE quedó atrás del once.

## Lo que va al código si se aprueba

| Cambio | Parte y backend | Tipo |
|---|---|---|
| 1 | `m2.veredictoRamas {igualadoOArriba, persiguiendo}` con `{veredicto, razon}`; el veredicto lee la rama jugada | campo nuevo |
| 3 | aviso `M1-VS-ULTIMO-ONCE` en el recibo (sistema distinto del último once sin motivo escrito) | aviso |
| 4 | `penales` en los insumos del DTP (desde los eventos) y aviso si `viasGol` no nombra al ejecutor de los dos lados | insumo calculado + aviso |
| 5 | `casoBloque.sede` y `casoBloque.competicion`; aviso si la 6 cita un caso de otra sede | campo nuevo + aviso |

Los cambios 2, 6 y 7 son de rúbrica pura y no tocan el parte.

## Cómo se aplica si se aprueba

1. El usuario aprueba o corrige punto por punto. En el 6, (b) y (c) se
   aprueban por separado.
2. Se redacta la v1.6 en `docs/skills/diagnostico-tactico/SKILL.md`, con su
   entrada en el encabezado.
3. Se da sitio en el parte a lo de la tabla de arriba, con
   `docs/openapi.yaml`, los tipos, los tests y el prompt de `docs/COWORK.md`.
4. Se suma `("v1.6", fecha)` a `lecciones.CORTE_VERSION`.
5. Se entrega el `.zip` para subir a la cuenta.
6. Se cierran con 🔑 las lecciones anteriores a la v1.6. Ojo: las doce de
   DTP-REHACER no son lecciones del skill (ver la corrección del principio).
