---
name: corrida-sad
description: Corrida del pipeline SAD con Claude Code (reemplaza a Cowork desde el 13/10/2026). Modo `partes` analiza los partidos de la agenda con los skills (EFE, Teorema del Echado, DTP, sad-analysis) y deposita un parte por partido; modo `veredictos` cierra con autopsia por skill los partidos jugados; modo `reventones` estudia hacia atrás burbujas que reventaron (TDE de los dos equipos, DTP, EFE de ese día); modo `rehacer` rehace el DTP (y lo que el once cambie) de los partes con DTP-REHACER cuando sale el once oficial, antes del pitazo; modo `mantenimiento` lee las incidencias que dejaron las corridas, las verifica y arregla con tests lo que es código. Usar cuando una rutina programada o el usuario pida «la corrida», «los partes de hoy», «validar lo de ayer», «los veredictos» o «el mantenimiento».
---

# Corrida SAD con Claude Code

Desde el 13/10/2026 el análisis lo hace **Claude Code** en sesiones de la nube
lanzadas por rutinas, no Cowork. El contrato y el prompt de siempre siguen
mandando: `docs/COWORK.md` (el nombre del archivo quedó; «Cowork» ahí = quien
escribe el parte, hoy vos). Esta guía dice cómo correrlo desde Code.

## Credenciales (antes de nada)

- `SAD_API_BASE` = la base de la API, terminada en `/api/v1`.
- `SAD_TOKEN_COWORK` = el token ACOTADO (lista de permitidos). Viven en las
  variables del entorno de la nube.
- `export B="$SAD_API_BASE" T="$SAD_TOKEN_COWORK"` y siempre
  `curl -sS -H "Authorization: Bearer $T" "$B/…"`.
- **Nunca** imprimas, escribas en un archivo del repo ni repitas el token. Si
  un endpoint responde 403, NO busques otro token: ese endpoint no es tuyo,
  anotalo y seguí. El token maestro no se usa jamás desde una sesión.
- Si falta alguna de las dos variables: no hay corrida. Terminá diciendo cuál
  falta (sin inventar resultados) — se agrega en la configuración del entorno.

Hora: `TZ=America/Lima date` (la referencia del proyecto es Lima). Archivos de
trabajo en el scratchpad de la sesión, nunca en el repo: esta corrida NO
commitea nada. **Una carpeta por subagente** (`<scratchpad>/<fixtureId>/`),
y se lo decís en el encargo: los subagentes corren en paralelo y, con la misma
carpeta, uno leía el JSON que el otro acababa de escribir (15/10/2026: el de
Boca–Vasco recibió el veredicto y la ficha de Bucaramanga–Águilas en sus dos
primeras consultas). Nunca un nombre de archivo fijo como `ficha.json` fuera
de esa carpeta.
Usá SIEMPRE rutas absolutas (`-o <scratchpad>/<fixtureId>/x.json`): un `-o get.json` relativo
cae en la raíz del repo (17/10/2026).

## Modo `partes` (antes del partido)

1. `GET $B/analisis/cowork/contrato` (manda sobre cualquier ejemplo) y
   `GET $B/analisis/cowork/latido` (qué quedó roto de ayer: decilo al final).
2. `GET $B/analisis/cowork/agenda?desdeAhora=true&horas=N&limite=30` con
   el TRAMO de esta corrida, que termina donde empieza la siguiente (cada
   tramo cae en su propia ventana de 5 h del plan; un fin de semana trae
   15-23 partidos por tramo y la meta es el 80 % del padrón). **El tope es
   30 por tramo desde el 25/10/2026** (el usuario subió el plan): un
   `limite` MENOR en el mensaje del disparo es de antes de esa fecha y se
   ignora —el texto de una rutina solo se cambia desde su propia
   conversación, y el del tramo 3 todavía dice `limite=20`—. N lo fija la
   HORA DE LIMA a la que corrés, aunque el disparo diga «24 h»:

   | Corrés entre (Lima) | Tramo | `horas` |
   |---|---|---|
   | 03:00 y 08:59 | 1 (hasta ~11:45) | 7 |
   | 09:00 y 13:59 | 2 (hasta ~16:00) | 6 |
   | 14:00 y 02:59 | 3 (hasta la madrugada) | 14 |

   Si el mensaje del disparo trae otros parámetros de agenda, mandan esos,
   salvo un `limite` menor que 30 (ver arriba).
   Usá la misma consulta en el paso 4 → la lista de trabajo es
   `porHacer` (lo ya depositado está en `yaHechos`: no se rehace). Un partido
   en `aRehacer` tiene un parte de OTRA fecha (aplazado o movido): va en
   `porHacer` y se rehace ENTERO, con la semana nueva —sin rehacerlo, el caso
   cae en cuarentena automática al cerrar el veredicto—. Descartá
   los que arrancan en menos de 60 minutos: un parte no se escribe con el
   pitazo encima y JAMÁS después del pitazo.
3. **Un subagente por partido, en paralelo** (herramienta Agent, tipo
   `general-purpose`, todos en el mismo mensaje). Es la «sesión limpia por
   partido» del punto 3 del prompt: el contexto de un partido no contamina al
   otro. A cada uno le pasás el `fixtureId`, los dos equipos, la hora de
   inicio en Lima, la **hora tope** (inicio − 45 min), su fila de la agenda y
   las instrucciones de la sección «Encargo de un partido» de abajo, entera.
4. Al volver todos: `POST $B/analisis/cowork/xi/auto` (cierra los onces que
   ya estén; el ciclo en vivo del backend lo vuelve a hacer solo cuando salen
   las alineaciones). `GET …/agenda` de nuevo: `porHacer` tiene que
   haber quedado vacío salvo lo que se descartó a propósito.
5. Depositá lo roto como incidencias (sección de abajo). Respuesta final,
   tres líneas: partes depositados (fixtureId y partido),
   cuáles no y por qué, y qué se rompió (incluido lo que dijo el latido).

### Encargo de un partido (copiar entero al subagente)

> Sos el analista SAD de UN partido, en modo batch desatendido. Tus archivos
> de trabajo van SOLO en `<scratchpad>/<fixtureId>/` (otros subagentes corren
> en paralelo: no uses otra carpeta ni nombres de archivo compartidos). Nadie te va
> a contestar: toda duda se declara en el parte, nunca se inventa.
>
> - Leé `docs/COWORK.md` desde «# PROMPT COWORK — SAD BATCH NOCTURNO» hasta
>   «# PROMPT CORTO — "LLEGÓ EL ONCE"»: es el prompt y manda en todo. Ignorá
>   su punto 2 (la selección ya está hecha: tu partido es este) y el bloque
>   de credenciales (usá `$SAD_API_BASE` y `$SAD_TOKEN_COWORK`, nunca los
>   imprimas). Si dudás de una forma del contrato, mirá `backend/analisis/
>   parte.py` (solo lectura; no modifiques el repo).
> - Skills (herramienta Skill), cargalos ANTES de puntuar:
>   `anthropic-skills:efe-clasificador`, `anthropic-skills:teorema-del-echado`,
>   `anthropic-skills:diagnostico-tactico`, `anthropic-skills:sad-analysis`.
>   Prensa con WebSearch/WebFetch (cargalos con ToolSearch
>   `select:WebSearch,WebFetch`).
> - Orden: `GET antecedentes/{id}` → `fixtures/{id}` → `analisis/cowork/
>   tde/{id}` → `analisis/cowork/dtp/{id}` → **`analisis/cowork/f1/{id}`**
>   (la tabla F1 sale de acá, con `jugadorId`; los `decisivo` no pueden
>   faltar; los `sancionados` —roja o amarillas en el último partido de esta
>   competición, calculados de la base— van en `fuera` con estado baja y
>   motivo «sanción» salvo que la prensa diga que juega, y entonces la nota del
>   equipo lo dice con la fuente: si no, SANCION-SIN-DECLARAR) →
>   `equipos/{id}/burbujas?proximo={id}` de los dos → `cuotas/{id}`
>   → prensa (DT de ESTA semana, bajas, once probable) → el JSON del parte
>   EXACTO al punto 7 (a = local).
>   El gap, la μ y el 1X2 del motor (`unXDos`) están en `GET predicciones/{id}`
>   (no existe `/estadisticas/gap`; μ son puntos: nunca un Poisson sobre μ;
>   si el servidor todavía no trae `unXDos`, se calcula con
>   `backend/analisis/unxdos_motor.probabilidades(μ_local, μ_visita)` —la misma
>   función— y se dice en `pronostico.motor`); P1a del TDE ya viene calculado en `tde/{id}`. El
>   `desde` del DT con `desdeConfirmar: true` NO es dato: la llegada sale de
>   prensa o va vacía. Una ventana del TDE que cambia según quién marque va
>   en la rama: `reasignacion.siMarcaPrimero.ventana`, RELATIVA al gol que la
>   abre como pide el TDE v0.1.21 («desde el gol +15»: el veredicto la cobra
>   desde el minuto de ese gol) o en minutos de reloj («60-75'»); una ventana
>   relativa sin «+N» no se puede cobrar. La apertura del DTP entra
>   a la cadena UNA vez: re-depositar no la pisa (anti-hindsight). Las bajas
>   de la base (`jugador_bajas`) pueden ser viejas: manda el parte médico de
>   esta semana.
> - Lo que dejaron las autopsias del 11/10 y ya es campo: `reasignacion` en
>   CADA bloque del TDE con las dos ramas (`siMarcaPrimero`,
>   `siRecibePrimero`); la ventana de una echada condicionada a ir ganando se
>   ancla al minuto de la ventaja, no al reloj; COLAPSO EN CASCADA solo si el
>   rival con D3 superior va a seguir atacando; la posesión y el rest defense
>   valen contra ESTE rival y con ESTE once.
> - **La espina de la burbuja** (`lecturaSad.espina`, desde el 14/10): por
>   equipo, adónde va su K TOTAL después de este partido —`positiva` (crece:
>   gana) · `cero` (se reinicia: empata) · `negativa` (pierde) · `neutra`—, con
>   `porque`, leyendo su gráfica de K y cómo se le cortan las burbujas
>   (`historial.*.termina` en `/burbujas`). No la acomodes a tu 1X2: lo que se
>   mide es si acierta sola. Y el ENSAYO la cuenta en un párrafo de las
>   burbujas (si no, el recibo avisa `ensayo.espina`). Si el equipo es otro en casa que afuera, leé la K
>   de la condición de hoy (`familias.local` / `familias.visita`) y declaralo
>   con `"guia": "condicion"`.
> - **La espina empieza en la tarjeta** (desde el 19/10): cada familia de
>   `/burbujas` trae `espinaTarjeta` (la espina que da la tarjeta sola, `fuerte`
>   o `debil`) y `GET /analisis/cowork/espina/calibracion` dice cuánto acierta y
>   quién gana cuando el analista la contradice. Leé la calibración UNA vez al
>   empezar la corrida. Con tarjeta FUERTE, la espina la sigue salvo que un
>   skill (EFE, TDE, DTP, matriz) traiga un hecho de ESTE partido que la
>   contradiga, y entonces el `porque` dice «contra la tarjeta porque…» (si no,
>   el recibo lo cobra). Con tarjeta DÉBIL deciden los skills. El ensayo junta
>   las dos lecturas en una: qué dice la historia de las burbujas y qué le
>   agregan los skills de este partido.
> - **La espina contra el riesgo se dice**: si leés la espina contra el riesgo
>   calculado (alto y la dejás neutra o siguiendo la racha; bajo y la cortás),
>   el `porque` empieza «contra el riesgo X porque…» y el ensayo lo nombra.
>   El riesgo es de la burbuja: con racha negativa, ALTO = que reviente,
>   o sea que el equipo deje de perder.
> - **Las otras burbujas** (`otrasFamilias` en `/burbujas`, desde el 17/10):
>   doble oportunidad, márgenes y goles ya contados en `lineas[]`. Narrativa:
>   su largo y su récord NO predicen el partido siguiente y en el récord se
>   sostienen, no revientan (REVENTON §15). Pero una GRANDE en su récord
>   (`cuidado`, alerta FAMILIA-RECORD) es CUIDADO con la carga, como K-EXTREMO:
>   nombrala en el ensayo y en el falsador. El
>   `perfilDc` (no pierde / no gana en la condición de hoy) SÍ agrega al 1X2
>   del motor (§15.1): miralo antes de fijar las probabilidades y contalo en el
>   párrafo de las burbujas del ensayo. Sin copiar números.
> - **La matriz de escenarios va estructurada en `matriz`** (desde el 15/10):
>   por equipo, `ganar` / `empatar` / `perder` con las filas del skill y la
>   `probabilidad` estimada de cada escenario, que tiene que cuadrar con tu 1X2
>   de `pronostico.probabilidades` (el recibo avisa en `matrizVsPronostico`).
>   Es cómo puede darse el partido: no olvides la pelota parada ni el gatillo
>   del que pierde. Ya no va como documento.
> - **Goles acotados antes del marcador** (30/10/2026): `golesAcotados` de
>   `/burbujas?proximo={id}` de los dos equipos da el intervalo de dos goles de
>   cada uno y el marcador acotado (REVENTON §17, acierta lo que promete). El
>   marcador declarado va dentro, o la lectura dice qué hecho de este partido
>   lo saca, y entonces el falsador nombra la vía de gol que lo saca (sad-analysis
>   v4.3, 3.5 y 6-C). No mueve el 1X2. Es lectura, no apuesta.
> - **Quién pasó una llave NO se deduce del marcador** (29/10/2026, incidencia
>   774: Palmeiras pasó a la final de la Libertadores por penales y un parte lo
>   dio por eliminado, con el D3, el C4 y el ensayo encima). Un partido de
>   copa que se fue a penales o a la vuelta de una llave: lo dice `eliminatoria`
>   de `GET fixtures/{id}/ficha` (`avanzaLado`, `penales`, `global`) y el
>   título del evento del timeline («Derrota 0-1 ante X · PASA por penales
>   (5-3) tras 2-2 en el global»). El marcador es a 90' y NO dice quién pasó;
>   los `Shootout` no se cuentan a mano. Sin `eliminatoria` (o con `avanza`
>   null), la prensa confirma o se escribe «sin confirmar». Si el recibo trae
>   `ELIMINATORIA-AL-REVES`, se corrige antes de cerrar.
> - **Alertas: solo códigos que existen en los skills** (T.54, T.54-B,
>   R-KT.2, GK-DOWNGRADE, GK-FALLA-ACTIVA, FACTOR-X, G-BLOQUE, G-SORPRESA,
>   COLAPSO EN CASCADA del EFE; DIV-MOTOR-MERCADO de `sad-analysis`, con tipo
>   `fecha` y las dos cifras… los que nombra la rúbrica). Una observación que no tiene código
>   (un DT suspendido, un plantel desarmado, una trampa del mercado) va en
>   `notas` del bloque o en la lectura, NO como alerta con un código inventado:
>   un código nuevo no lo cuenta nadie y ensucia la tira. En la corrida del
>   13/10 aparecieron cuatro (DT-SUSPENDIDO, PLANTEL-DESMANTELADO, DC-TRAMPA,
>   BAJA-ORGANIZADOR). Un DT suspendido o ausente, además, va en
>   `dt.banco` con su fuente (ver `docs/COWORK.md`): sin eso el caso cae en
>   cuarentena automática cuando la ficha trae al reemplazo en el banco.
> - `POST $B/analisis/cowork` y LEÉ EL RECIBO ENTERO: `rechazos`, `faltan`,
>   `perdido`, `ladosTde`, `discrepancias`. Con algo ahí: `GET` → corregir →
>   `POST` del cuerpo entero (el POST reemplaza). La `cadena` se conserva del
>   PRIMER depósito: el primero ya lleva la definitiva.
> - Reloj: `TZ=America/Lima date` seguido. Depositá antes de la hora tope; si
>   15 minutos antes no está completo, depositá lo que tengas con lo faltante
>   en `pendientes`. Después del pitazo NO deposites: decilo.
> - Respuesta final breve (sin el token): hora del depósito; recibo
>   (rechazos, faltan, aviso/perdido); EFE % de cada lado según el GET; 1X2 y
>   marcador; alertas (tuyas y del backend); DT de cada lado y si hubo
>   DT-DISCREPANCIA; qué quedó pendiente o roto.

## Modo `rehacer` (cuando sale el once, antes del pitazo)

Pedido del usuario (22/10/2026), tras Sporting 2-3 LASK: DTP-REHACER sonó
(3-4-3 en vez del 3-5-2 de la apertura) y nadie lo rehízo, como en 9 de 24
partidos del 11/10. La app cierra el bloque F sola con la alineación, pero el
mapa de duelos y el 1X2 quedan escritos sobre otro equipo. Esta corrida corre
cada 30 minutos y es CORTA: casi siempre no hay nada que hacer.

1. **UNA sola llamada, antes de nada** (22/10/2026: cada disparo vacío
   costaba ~0,25 USD por leer la agenda y cada parte):
   `curl -sS -H "Authorization: Bearer $SAD_TOKEN_COWORK" "$SAD_API_BASE/analisis/cowork/rehacer"`.
   Trae los partes que arrancan entre **15 y 80 minutos** (`enVentana`; el piso
   bajó de 30 a 15 el 24/10/2026: la API publica el once ~27 min antes) y, de
   esos, los que tienen **DTP-REHACER** (`pendientes`: el once oficial
   contradice la apertura del DTP) o **PARTE-OTRA-FECHA** (el parte se
   escribió para la fecha vieja de un partido reprogramado: ese se rehace
   ENTERO, con el modo `partes`, no solo el DTP; desde el 25/10/2026,
   incidencia 395) o **DT-VS-BANCO** (el once oficial sienta a otro DT que el
   del parte: confirmalo en prensa y corregí SOLO el DT con `POST
   /analisis/cowork/{id}/dt`, o declará `dt.banco` si el titular no se sienta;
   desde el 27/10/2026, incidencia 711). Con `pendientes` vacío: terminá YA en una
   línea («Nada que rehacer a las HH:MM de Lima»), sin `git pull`, sin leer
   el resto de este skill, sin otra llamada y **sin avisar al celular** (corre
   cada media hora: un aviso vacío cada vez se deja de leer).
2. Con algún pendiente, recién ahí: `TZ=America/Lima date` y seguí.
3. Como mucho **6** partidos. Un subagente por partido, en paralelo, con este
   encargo:

> Tus archivos van SOLO en `<scratchpad>/rehacer-{id}/`. El partido {id}
> arranca a las {hora Lima}; hora tope de depósito: el pitazo − 10 minutos.
> Credenciales en `$SAD_API_BASE`/`$SAD_TOKEN_COWORK` (nunca las imprimas).
> Cargá `anthropic-skills:diagnostico-tactico` y `anthropic-skills:sad-analysis`.
>
> 1. `GET $B/analisis/cowork/{id}` (el parte entero: lo vas a devolver
>    ENTERO), `GET $B/fixtures/{id}/ficha` (el once oficial, con grid) y
>    `GET $B/analisis/cowork/dtp/{id}`. El motivo está en el detalle de la
>    alerta DTP-REHACER y en `dtp.bloques[].calculado.contraElOnce`.
> 2. En el bloque del DTP marcado —y SIEMPRE también en el bloque del rival,
>    porque su M2 nombra como rivales a los jugadores que cambiaron (incidencia
>    525, DTP v1.5)—: rehacé **M1** con el once oficial
>    (`sistema` y `xiReferencia` = los once titulares de la ficha) y **M2** en
>    sus dos capas (DTP v1.4): lo estructural (carriles, zonas, mecanismos)
>    se revisa; los duelos con nombre propio se reescriben con ESTE once, en
>    las dos direcciones del carril. Una vía de gol que dependía de un
>    jugador que no está, se saca; la del que entró, se escribe.
> 3. **El sistema sale del grid** (incidencia 849): `m1.sistema` es la
>    formación de la ficha oficial (o la del grid si la API la corrigió), no
>    la que traía la apertura; actualizar solo `xiReferencia` deja la alerta
>    sonando.
> 4. **Todo lo que NOMBRA al once viejo se reescribe** (incidencia 850, La
>    Guaira y Vasco: se rehízo el DTP y el TDE, la matriz, el falsador y el
>    ensayo siguieron con la línea de cinco y con un titular que arrancó en el
>    banco). Buscá en el parte ENTERO cada jugador que salió del once y cada
>    mención del sistema viejo —`tde.bloques[]` (indicadores, ramas,
>    reasignación, tipología), `matriz`, el falsador del pronóstico,
>    EJE-DEBUTANTE y las alertas declaradas, la prosa del DTP, el ensayo y las
>    notas del EFE— y reescribí esas frases con el once oficial. Lo demás no
>    se toca: una baja decisiva que no juega, un arquero distinto (EFE v1.6,
>    B6), la rama del TDE que dependía de un intérprete. Si el 1X2 se mueve,
>    movelo con su porqué en la lectura del 1X2 (disciplina 33); si no, no.
>    Antes de depositar, listá en tu respuesta los nombres que salieron y
>    confirmá que ninguno queda en el texto como titular.
> 5. `POST $B/analisis/cowork` con el cuerpo ENTERO (el POST reemplaza; la
>    cadena conserva la primera apertura, eso no se toca). Leé el recibo:
>    DTP-REHACER tiene que haber desaparecido de `alertas` en el GET
>    siguiente; si sigue, decí por qué (`contraElOnce.motivos`).
> 6. Después del pitazo NO deposites: decilo. Respuesta final: qué cambió
>    en M1/M2, qué otras secciones reescribiste por el once (paso 4), si se
>    movió el 1X2 (de cuánto a cuánto) y si la alerta se fue.

4. Depositá lo roto como incidencias (`origen: "partes"`, `corrida: "rehacer
   <fecha hora>"`). Respuesta final, tres líneas: partidos rehechos, los que
   no (y por qué) y qué se rompió. Al celular SOLO si se rehízo algo o algo
   falló.

## Modo `veredictos` (después del partido)

1. `GET $B/analisis/cowork/veredictos/pendientes?limite=45` → los partes
   jugados sin veredicto (lo que no entra queda para la próxima corrida, los
   más viejos primero; 45 desde el 27/10/2026: con 30 la cola llegó a 40
   vencidos tras un fin de semana; si el disparo trae otro `limite`, manda ese). Si no hay, decilo en una
   línea y terminá.
2. Un subagente por partido, en paralelo, con este encargo:

> Tus archivos de trabajo van SOLO en `<scratchpad>/{id}/` (otros subagentes
> corren en paralelo). Cerrá el caso del fixture {id} con el prompt «# PROMPT CORTO — "VALIDAR LO
> DE AYER"» de `docs/COWORK.md` (leelo entero). Lo objetivo (marcador, 1X2,
> Brier, ventana del TDE, rama de la reasignación, reventón) lo calcula la
> app: leelo de `GET $B/analisis/cowork/{id}/veredicto` y de la ficha
> (`GET $B/fixtures/{id}/ficha`), no lo escribas.
>
> La autopsia es POR SKILL, no por el 1X2: cargá
> `anthropic-skills:teorema-del-echado`, `anthropic-skills:efe-clasificador`
> y `anthropic-skills:diagnostico-tactico` y seguí su procedimiento de
> cierre de caso (en el TDE, «Cómo se cierra un caso» de CALIBRACION; en el
> DTP, la autopsia de goles con responsables y MECANISMO-ABIERTO). Cada
> hallazgo que toca una regla es UNA lección con `skill` y `reglaTocada`: la
> primera en `leccion`, las demás en `otrasLecciones` (hasta 6). Una
> confirmación de una regla también es lección («disciplina 44 declarada y
> cumplida»): es lo que cuenta casos a favor.
>
> **DTP-REHACER en el cierre: leé su `momento`** (26/10/2026: el 25/10 doce
> lecciones dijeron «sonó y no se rehízo» y la rutina había rehecho 18 partes;
> la API corrigió la formación cuando ya no quedaba disparo). `tardio` = la
> versión final del once llegó a menos de 15 min del pitazo: es apertura caída
> por un once TARDÍO, no un aviso ignorado — no escribas «no se rehízo» ni lo
> cargues como fallo del skill. `sinRehacer` = llegó a tiempo y nadie rehízo:
> anotalo en «Roto o a mirar» (falla de la corrida de rehacer), no como
> lección del DTP. `conocido` = el once ya estaba al depositar y la apertura
> igual lo contradice: ahí sí es lección. Sin `momento` (partes viejos), decí
> que no se sabe cuándo llegó el once.
>
> **Una regla no se cobra hacia atrás** (27/10/2026): una alerta con
> `posteriorAlParte` (ESPINA-SIGUE-EN-EXTREMO, EFE-EMPATE-TECNICO en partes
> anteriores al 26/10) y un desenlace del TDE con `noEvaluable` son reglas que
> el parte no podía conocer: no escribas «la incumplió» ni la cargues como
> fallo. Si el caso enseña algo sobre esa regla, va como confirmación o
> contraejemplo, no como incumplimiento.
>
> La matriz: `GET $B/analisis/cowork/{id}/objetivo` (antes del veredicto; el
> GET de `…/veredicto` da 404 hasta el primer POST) trae en `objetivo.matriz`
> qué escenario jugó cada equipo y qué se había escrito para él. Con
> `sinMatriz` el parte es anterior a la matriz estructurada: juzgá el
> escenario contra la prosa de `documentos[id=matriz]`. Por lado, `escenario: {aparecio: si|parcial|no,
> que}`: si la palanca o el gatillo escrito fue lo que pasó (sin tasa).
>
> Las otras burbujas cortadas: `objetivo.otrasFamilias` lista, por lado, las
> burbujas de doble oportunidad, márgenes y goles que el marcador cortó. Por
> cada una con `porExplicar` (grande o en su récord), escribí en
> `porLado.<lado>.cortes` `{familia, ambito, mecanismo, porque}`, con el
> mecanismo de la lista del estudio de reventones y el HECHO que lo prueba
> (ficha, once, DT, pelota parada). Un 0-2 de local del que siempre marca en
> casa tiene que quedar explicado (REVENTON §15.2); sin hecho, `varianza`.
>
> El banco: si la ficha trae en el banco a alguien que NO es el DT del parte
> y la prensa del partido explica por qué (DT suspendido o ausente, o la
> alineación de la API está mal: Juárez 18/10 con «T. Campos» y Lema en el
> banco), declaralo con `POST $B/analisis/cowork/{id}/dt` mandando el DT del
> parte con `banco: {motivo: suspendido|ausente|api_errada, nombre, fuente}`
> —el `dt` se reemplaza entero, así que va también `nombre` y `desde`—.
> Sin eso el caso cae en cuarentena automática por DT equivocado. Si el DT
> del parte ERA el equivocado, no lo tapes: corregí `nombre` y que entre en
> cuarentena, que para eso está.
>
> Lo que la app ya NO cobra, y no hace falta pelearlo: la ventana del TDE de
> un equipo que ya recibió 3 antes de ella (`clase: roto`, disciplina 3) o
> con el marcador 3 arriba (`rama_abandonada`, 24), una ventana relativa al
> gol y la de una rama declarada con su propia `ventana` (se mide esa). Y si
> la prosa del reventón de un parte de antes del 14/10 (tarde) no coincide
> con `reventonCalculado`, es la recalibración de los puntos (REVENTON
> §13.2): la prosa dice lo que la tarjeta mostraba ese día.
>
> `seleccion`: `ciega` si el partido salió de la agenda; `modoEvaluacion`:
> `PRE` si terminó. Con duda entre ciega y post_resultado, es post_resultado.
> `POST $B/analisis/cowork/{id}/veredicto` y leé `rechazos`. Respuesta final:
> marcador, veredicto por lado y la lista de lecciones (skill · regla).

3. Depositá lo roto como incidencias (sección de abajo). Respuesta final,
   tres líneas: veredictos cerrados, lecciones por skill, y
   qué no se pudo cerrar y por qué.

## Modo `reventones` (estudio hacia atrás)

Una burbuja que revienta es donde el partido dejó de parecerse a la racha. Si
era de victorias, el Teorema del Echado del que ganaba suele explicarlo; si
era de derrotas y el equipo la cortó, hay que mirar con el TDE **al rival**:
alguien con tan bajo rendimiento no gana solo. De esos estudios salen
nuestras probabilidades, no de la casa.

1. `GET $B/analisis/cowork/reventones?liga=<id>&meses=6&conFicha=true` (Liga 1
   Perú = 281). La lista ya viene ordenada: primero los que tienen ficha y no
   están estudiados, y dentro AL AZAR (no por tamaño: eso sesgó los primeros
   52 estudios hacia el récord). Tomá los primeros, sin elegir los «grandes». Tomá hasta **8** con `estudiado: false` (o los que pida
   quien te disparó), mezclando los dos tipos si los hay.
2. Un subagente por caso, en paralelo, con este encargo:

> Tus archivos de trabajo van SOLO en `<scratchpad>/{fixtureId}-{equipoId}/`.
> Estudiá el reventón del equipo {equipoId} en el fixture {fixtureId}
> ({partido}, {fecha}): {tipo}, racha de {partidos} partidos, K pico {kPico}.
> Credenciales en `$SAD_API_BASE` / `$SAD_TOKEN_COWORK` (nunca las imprimas).
>
> 1. `GET $B/analisis/cowork/reventones/{fixtureId}/{equipoId}`: la burbuja y el
>    nivel de los DOS equipos AL DÍA del partido (lo que se veía antes), la ficha
>    táctica (once, goles con minuto, rojas, stats), el DT de cada banco y las
>    listas cerradas de `mecanismos` y `senales`. Prensa de ESA fecha con
>    WebSearch/WebFetch (cargalos con ToolSearch `select:WebSearch,WebFetch`):
>    previa y crónica, DT, bajas, contexto (eliminatoria, descenso, altura).
> 2. Cargá `anthropic-skills:teorema-del-echado`, `anthropic-skills:diagnostico-tactico`
>    y `anthropic-skills:efe-clasificador`. Aplicá:
>    - **TDE a los DOS equipos**, con lo que se sabía antes (IE/ISE por bloques,
>      tipología, ventana) y contra lo que pasó (¿quién se echó, quién se
>      sobreexpuso, en qué minuto, qué rama de la reasignación jugó?). Si la
>      racha era negativa y se cortó, el foco es el rival: ¿qué hizo para perder
>      con alguien así?
>    - **DTP**: autopsia de cada gol con responsables y si hubo MECANISMO-ABIERTO.
>    - **EFE de ese día**: DT, bajas, rotación, lo que pesaba.
> 3. `POST $B/analisis/cowork/reventones/{fixtureId}/{equipoId}/estudio` con:
>    `mecanismo` (uno de la lista; el que MÁS explica el reventón),
>    `mecanismoSecundario` opcional, `senales` (de la lista: SOLO lo que era
>    visible ANTES del pitazo; si no había nada, `ninguna_visible`),
>    `senalPrevia` (una frase), `queP` (qué pasó, una frase), `tde.equipo` y
>    `tde.rival` (IE, ISE, tipología, ventana, qué rama jugó), `dtp`, `efe`,
>    `fuentes`, y `lecciones` [{skill, reglaTocada, leccion}]: una por hallazgo
>    que toque una regla, también las confirmaciones. Leé `rechazos`.
> 4. Respuesta final: mecanismo, señales, y las lecciones (skill · regla).
>
> Notas de la primera tanda (Perú, 13/10/2026):
> - **No uses `GET …/analisis/cowork/tde/{id}` para un partido jugado**: mete ese
>   mismo partido en el F1 (no es anti-hindsight). El TDE del estudio se puntúa
>   a mano con lo que había antes, y se dice que es aproximado.
> - Las reglas del reventón (docs/REVENTON.md) son de `sad-analysis`: no existe
>   un skill «reventon» (la app lo corrige sola, pero escribilo bien).
> - `altura`, `racha_de_otra_competicion`, `regresion_al_nivel`,
>   `bloque_bajo_del_rival` (repliegue por PLAN, no echada), `arquero_rival`,
>   `arquero_propio`, `doble_golpe` y `cambio_masivo` son mecanismos: no los
>   mandes como `otro`. `clasico`, `rival_directo`, `sin_nada_en_juego`,
>   `rival_con_once_alternativo` y `plantel_renovado` son señales a declarar. Las señales marcadas CALCULADA en la
>   lista (`racha_en_otra_competicion`, `condicion_a_contramano`,
>   `rival_tambien_en_burbuja`, `racha_concediendo`,
>   `derrota_internacional_reciente`, `once_distinto`, `rival_de_otra_base`,
>   `dt_distinto_al_de_la_racha`, `arquero_suplente`, `arquero_suplente_rival`)
>   las pone la app: no las declares.
> - **El arquero** (14/10/2026: apareció en 10 de 43 estudios y no tiene
>   casillero en ningún skill). La ficha trae `arqueros` de los dos lados AL
>   DÍA: habitual, el de hoy y si es suplente, goles recibidos contra el xG en
>   contra (`evitados`, con su n) y atajadas por partido. En el POST va
>   `arquero.equipo` y `arquero.rival` con: `nombre`, `queHizo` (atajadas
>   decisivas, error, nada relevante), `decisivo` (sí/no: ¿cambió el
>   resultado?), `formaPrevia` (lo que se sabía ANTES: errores recientes,
>   racha de vallas, lesión, recién llegado, suplente), `visibleAntes` (sí/no)
>   y `fuente`. Sin prensa sobre el arquero, se dice; no se rellena.
> - **Cargar los tres skills con la herramienta Skill es obligatorio**, no
>   copiar el formato de otro estudio: la autopsia sale de la rúbrica del skill.
> - Máximo **8 lecciones**: fundí las confirmaciones del mismo skill en una.
> - Confirmá en la ficha quién fue LOCAL: la lista dice «equipo vs rival», no
>   «local vs visita».
>
> Es un estudio CON el resultado a la vista: la población es `post_resultado`,
> lo pone la app. No disfraces de «se veía venir» lo que solo se ve después:
> una señal es previa si estaba en la prensa o en la base antes del partido.

3. Respuesta final, tres líneas: estudios guardados (por tipo), los
   mecanismos que más se repitieron (`GET …/reventones/resumen?liga=<id>`), y
   qué no se pudo estudiar y por qué.

## Al terminar partes, veredictos o reventones: depositá lo roto

Tu «Roto o a mirar» NO se queda en el chat: nadie lo lee ahí. Antes de avisar
al celular, mandalo como incidencias (una por hallazgo, aunque sea chico):

```
POST $B/analisis/cowork/incidencias
{"origen": "partes" | "veredictos" | "reventones",
 "corrida": "18/10 tramo 1",
 "items": [{"titulo": "DT de Bournemouth: la base dice Tindall y dirige Rose",
            "area": "dt", "severidad": "error", "fixtureId": 1557427,
            "detalle": "qué viste, dónde, con qué dato; qué hiciste en el parte"}]}
```

- `area`: dt · once · ficha · tde · dtp · f1 · timeline · reventon · burbujas
  · agenda · latido · cuotas · api · contrato · skill · aprendizaje · otro.
- `severidad`: `bloquea` (no se pudo depositar o cerrar, o el número que
  manda está mal) · `error` (la app dijo algo falso, y lo corregiste a mano o
  quedó así) · `aviso` (raro, a mirar).
- **El título nombra la CAUSA, no el caso** (20/10/2026: la cola llegó a 254
  porque cada partido abría la suya). Sin equipos ni jugadores en el título:
  «Titular de la ficha sin jugadorId», no «Titular de Rayo sin jugadorId»; el
  partido va en `fixtureId` y el caso concreto en `detalle`. Lo que va entre
  paréntesis o después de «:» no cuenta para agrupar. La misma causa abierta
  suma `veces` y junta los partidos en `fixtures`: que se repita es la señal de
  que el parche no alcanzó. Antes de depositar, mirá las abiertas
  (`GET …/incidencias`) y reusá su título si es la misma causa.
- Lo que es tuyo de corregir en el parte (un DT mal escrito) no es incidencia;
  lo que la APP hizo mal, sí, aunque lo hayas sorteado.

## Modo `mantenimiento` (los parches, automáticos)

La rutina diaria que arregla lo que las corridas vieron roto (pedido del
usuario, 18/10/2026: la API siempre puede fallar y van a aparecer errores
nuevos). Acá SÍ se toca el código, con las reglas del repo (`CLAUDE.md` manda)
y con freno.

0. **Primero lo que quedó a medias y lo que decidió el usuario** (27/10/2026):
   - `GET $B/health` → `commit` (lo que corre en producción) y
     `GET $B/analisis/cowork/incidencias?estado=por_desplegar`: cada una cuyo
     merge YA está en ese commit (`git merge-base --is-ancestor <merge> <commit>`
     tras `git fetch origin main`) pasa a `resuelta`. Si lleva más de 24 h sin
     desplegarse, deposita UNA incidencia `bloquea` «despliegue atascado» con
     el PR y pasala a `usuario`.
   - `GET …/incidencias?estado=aprobada`: el usuario aprobó la propuesta desde
     la app. Van ANTES que las abiertas y cuentan como grupos de código del
     paso 3. Si la propuesta era una acción suya (una cuarentena, un
     desmentido, una variable), aprobar significa «hecho»: verificá con los
     GET que esté hecho y cerrala `resuelta`; si no, devolvela a `usuario`
     diciendo qué falta. Aprobar NO abre las zonas del paso 4 (motor, skills,
     tokens, datos, Railway): esas siguen siendo del usuario.
   - `GET …/incidencias?estado=usuario` + `GET …/incidencias/causas`: **limpiá
     la cola del usuario**. La que ya resolvió un PR mergeado después de que
     se derivó, cerrala `resuelta` con ese PR; las de la misma familia de
     causa (`causas[].ids`) déjalas en UNA: las demás pasan a `descartada`
     con «agrupada en #N». Al usuario le llega una decisión por causa, en la
     tarjeta «Decisiones pendientes» de Partidos, con la `resolucion` como
     propuesta: escribila para que se pueda aprobar sin abrir otra cosa (qué
     cambia, dónde, qué se pierde).
0-bis. **El escaneo preventivo** (30/10/2026, pedido del usuario: «no esperar
   a que salten estas cosas»): `GET $B/analisis/cowork/escaneo` recorre la
   agenda de las próximas 36 h y las partes jugadas en las últimas 48 h con los
   chequeos de lo básico (sancionados, el mismo jugador dos veces en la F1,
   DT sin confirmar, dos partidos el mismo día, sin cuotas, once tarde, ficha
   sin eventos). Por CADA chequeo con hallazgos depositá UNA incidencia
   (`POST …/incidencias`, `origen: "escaneo"`, el `area` y la `severidad` del
   chequeo, `titulo` = el del chequeo, `detalle` = los partidos y hallazgos,
   `fixtureId` = el primero): la misma abierta suma `veces`, no se duplica. Desde
   ahí entran al paso 1 como las demás. Un dato que un parte o un veredicto
   reporta y que el escaneo NO vio es un chequeo que falta: sumalo a
   `backend/analisis/escaneo.py` (`CHEQUEOS`, con la regla que cuida y su
   test en `backend/test_sanciones.py`) como parte del grupo que lo arregla.
1. `git fetch origin main`; trabajá en la rama designada de la sesión
   recreada desde `origin/main` (`git checkout -B <rama> origin/main`: su PR
   anterior ya se mergeó o no existe). `GET $B/analisis/cowork/incidencias`
   (abiertas, graves y repetidas primero) y `GET $B/analisis/cowork/latido`.
   Sin incidencias abiertas ni aprobadas: avisá «nada que arreglar» y terminá.
   **Causa conocida, no se re-investiga** (27/10/2026): cada abierta trae
   `conocida` (la última cerrada de su familia, con la resolución). Si es
   `dato_api` · `por_diseno` · `descartada` y la nueva no trae nada que la
   resolución no cubra, cerrala igual remitiendo a ella («misma causa que
   #N: …») sin volver a verificar contra la base. Si la conocida es
   `resuelta` y la causa volvió, el parche no alcanzó: es código otra vez.
   **Lo que se repite sube al usuario**: `GET …/incidencias/causas?recurrentes=true`
   lista los `dato_api` vistos en 3+ partidos distintos sin decisión
   (`recurrente`) y lo que volvió después de un PR (`reaparece`). Por cada
   recurrente, pasá UNA incidencia de la familia a `usuario` con la regla de
   código que taparía el dato (como 381 y 673, que pasaron a código cuando el
   usuario las vio): qué se calcularía, con qué fuente, y qué caso lo pide.
   **Agrupá por CAUSA antes de tocar nada** (pedido del usuario, 22/10/2026:
   la cola llegó a 88 arreglando de a una). Varias incidencias suelen ser la
   misma raíz —el cruce de nombres de `contraElOnce`, la identidad del jugador
   en la ficha, la tabla F1, las ventanas del TDE, la escala entre ligas, las
   bajas de la API—: se arregla la raíz y se cierran todas las que cubre. Armá
   la lista de grupos (área + causa + ids) y ordenala por gravedad y `veces`.
2. **Verificá cada una contra los datos antes de tocar nada** (los GET de la
   API, el código, los tests): una incidencia es un reporte, no una orden.
   Clasificala:
   - `por_diseno`: la app hace lo que se decidió (está en `CLAUDE.md` o en el
     doc del área). Resolución: la regla y dónde está escrita.
   - `dato_api`: la API trajo algo malo y no hay regla razonable que lo
     evite. Resolución: qué dato, de dónde, y qué alerta ya lo cubre.
   - `usuario`: le toca a una persona (una variable de Railway, una
     cuarentena o un desmentido con la llave maestra, una decisión).
     Resolución: qué hacer, exacto.
   - `descartada`: no se reproduce. Resolución: qué miraste.
   - código: marcala `en_curso` y arreglala (paso 3).
3. **El parche**: el cambio mínimo que lo arregla, con un test que falla sin
   él (en el `test_*.py` del área o en `backend/test_cowork.py`) y un
   comentario con el caso real que lo motivó, como el resto del repo. Cambios
   de contrato: primero `docs/openapi.yaml`, después backend, `src/api/
   types.ts`, los dos datasources y tests. **La CLASE, no el caso** (30/10/2026:
   la identidad del jugador se parchó 8 veces en un mes, cada vez en un
   módulo): antes de parchar, buscá la MISMA regla en los otros módulos
   (`grep` de la función o del criterio: el cruce de nombres vive en
   `bloque_f`, `f1_base`, `dtp_cowork`, `parte` y `ingesta/jugadores`) y
   arreglala en todos los que la usan, con un test por cada uno. **Cada grupo
   deja su guardia** (30/10/2026, usuario: «escaneo preventivo sobre nuestro
   código»): decí a qué clase de `docs/FALLAS.md` pertenece y, si la clase es
   nueva, sumala ahí con su guardia; si la regla se puede verificar leyendo el
   código, va a `backend/test_arquitectura.py`; si se ve en los datos, a
   `CHEQUEOS` del escaneo; si se ve en un parte, es una alerta calculada. La
   identidad de un jugador o un DT se arregla SOLO en `backend/identidad.py`
   (con su caso en `backend/test_identidad.py`). **Hasta 6
   GRUPOS de código por corrida (desde el 30/10/2026; antes 3), un PR por
   grupo** (cada uno con su batería del paso 5 en verde y
   su merge antes del siguiente): un grupo cierra todas sus incidencias de
   una vez. Las que NO son código (`dato_api` · `por_diseno` · `descartada` ·
   `usuario`) no cuentan para ese tope: verificadas, se clasifican TODAS en la
   misma corrida. Los grupos de código que no entren quedan abiertos para la
   siguiente, y la respuesta final dice cuáles.
4. **Lo que NO se toca solo** (va a `usuario` con la propuesta escrita en
   `resolucion`, sin commit):
   - la matemática del motor (`src/motor/`, `backend/analisis/motor.py`,
     `docs/MOTOR_SAD_EXTRACCION.md`) y cualquier número calibrado
     (`PUNTOS_*`, `TASA_BACKTEST`, `MOVIMIENTO*` en `burbuja.py`/`burbuja.ts`,
     los pesos de un skill, umbrales del TDE/EFE);
   - los skills (`docs/skills/`) y lo que puntúan;
   - la autenticación y los tokens (`_COWORK_PERMITIDO`, `SAD_TOKEN_*`):
     abrir un endpoint es una decisión;
   - borrar datos, levantar o poner cuarentenas, el presupuesto de la API
     (`SAD_*` de cuota) y las variables de Railway;
   - un grupo cuyo arreglo pase de 10 archivos o ~400 líneas: es un
     rediseño, no un parche.
5. **Validá todo**: `npm run build`, `npm run test:motor`, `test:kview`,
   `test:burbuja`, `test:familias` y TODOS los `python -m backend.test_*` de
   `CLAUDE.md` (test_api, test_cowork, test_jugadores, test_ficha,
   test_en_vivo, test_dtp, test_calendario, test_cronologia, test_preflight,
   test_burbuja, test_familias, test_coherencia, test_modo_fallo, test_jev,
   test_backtest_burbuja, test_backtest_1x2, test_backtest_familias,
   test_cuotas_lote, test_despensa); si tocaste pantalla,
   `scripts/audit-movil.mjs` a 360 y 390. Un test que falla y no es tuyo
   (rojo en main también) se anota como incidencia nueva, no se tapa.
6. Commit (en español, qué y por qué, con las líneas de atribución que dé el
   entorno), push a la rama, PR a `main` con la lista de incidencias (id,
   qué era, qué se hizo). **Merge solo si** todo el paso 5 dio verde Y el
   diff respeta el paso 4; si no, el PR queda abierto y las incidencias en
   `usuario` con el enlace.
7. Cerrá cada incidencia: `POST $B/analisis/cowork/incidencias/{id}/estado`
   con `{"estado": …, "resolucion": "…", "pr": "#N"}` (cerrar exige
   resolución). **Resuelta es resuelta EN PRODUCCIÓN**: tras el merge, mirá
   `GET $B/health` → `commit`. Si ya contiene el merge, `resuelta`; si no
   (Railway tarda o está caído), `por_desplegar` con el PR, y la próxima
   pasada la confirma (paso 0). Con `commit` vacío (no se sabe) queda
   `resuelta` con «despliegue sin confirmar» en la resolución.
8. Respuesta final, tres líneas: grupos e incidencias resueltas (con PR y si
   ya están en producción), derivadas (dato_api · por_diseno · cuántas
   cerradas por causa conocida · cuántas causas nuevas esperan al usuario en
   «Decisiones pendientes») y los grupos que quedan abiertos para la próxima.

## Al terminar cualquier modo: avisá al celular

Las rutinas corren solas y el usuario no mira la sesión. Mandá las tres
líneas finales al celular con la herramienta **PushNotification** (cargala con
ToolSearch `select:PushNotification`), también si la corrida falló o no tenía
nada que hacer. Sin el token, sin datos sensibles.

Excepción: el modo `rehacer` corre cada 30 minutos y avisa SOLO si rehízo
algo o algo falló.

## Lo que NO hace esta corrida

- No levanta cuarentenas, no desmiente bancos, no abre revisiones ni marca
  lecciones `aplicada`: es del usuario, con la llave maestra.
- En partes, veredictos y reventones no commitea ni toca el código: un bug de
  la app va como incidencia (qué, dónde, con qué fixture). El código lo toca
  SOLO el modo `mantenimiento`, con sus reglas.
