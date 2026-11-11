<!-- Modo `partes` de la corrida SAD. Lo carga SOLO la corrida de este modo (SKILL.md dice cuándo). Credenciales y reglas comunes: SKILL.md. -->

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

   Leé también `GET $B/analisis/cowork/espina/calibracion` UNA vez acá y
   pasale el resultado a cada subagente en su encargo: que no la pida cada uno
   (incidencia 1206, cinco subagentes colgados de la misma llamada).
   Si el mensaje del disparo trae otros parámetros de agenda, mandan esos,
   salvo un `limite` menor que 30 (ver arriba).
   Usá la misma consulta en el paso 4 → la lista de trabajo es
   `porHacer` (lo ya depositado está en `yaHechos`: no se rehace). Un partido
   en `aRehacer` tiene un parte de OTRA fecha (aplazado o movido): va en
   `porHacer` y se rehace ENTERO, con la semana nueva —sin rehacerlo, el caso
   cae en cuarentena automática al cerrar el veredicto—. La `hora` de la
   fila es UTC: la de Lima viaja en `horaLima`/`fechaLima` (incidencia 1230),
   y con esa se fija la hora tope del encargo. Descartá
   los que arrancan en menos de 60 minutos: un parte no se escribe con el
   pitazo encima y JAMÁS después del pitazo.
3. **Un subagente por partido, en paralelo** (herramienta Agent, tipo
   `general-purpose`), **en tandas de a 8 como mucho** (decisión del usuario,
   10/11/2026, incidencia 1353: con ~20 subagentes leyendo a la vez el servidor
   respondió 502 durante 20-40 s; la tanda siguiente sale cuando vuelve la
   anterior; un POST que dio 502 puede haber guardado: GET antes de reintentar). Es la «sesión limpia por
   partido» del punto 3 del prompt: el contexto de un partido no contamina al
   otro. A cada uno le pasás el `fixtureId`, los dos equipos, la hora de
   inicio en Lima, la **hora tope** (inicio − 45 min), su fila de la agenda y
   las instrucciones de la sección «Encargo de un partido» de abajo, entera.
4. Al volver todos: `POST $B/analisis/cowork/xi/auto` (cierra los onces que
   ya estén; el ciclo en vivo del backend lo vuelve a hacer solo cuando salen
   las alineaciones). `GET …/agenda` de nuevo: `porHacer` tiene que
   haber quedado vacío salvo lo que se descartó a propósito.
5. Depositá lo roto como incidencias (`.claude/skills/corrida-sad/incidencias.md`). Respuesta final,
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
> - Orden: `GET analisis/cowork/antecedentes/{id}` (con ese prefijo; sin él da 403 al
>   token acotado, incidencia 1177) → `fixtures/{id}` → `analisis/cowork/
>   tde/{id}` → `analisis/cowork/dtp/{id}` → **`analisis/cowork/f1/{id}`**
>   (la tabla F1 sale de acá, con `jugadorId`; los `decisivo` no pueden
>   faltar; los `sancionados` —roja o amarillas en el último partido de esta
>   competición, calculados de la base— van en `fuera` con estado baja y
>   motivo «sanción» salvo que la prensa diga que juega, y entonces la nota del
>   equipo lo dice con la fuente —en una nota de bloque A-E, nunca `notas.F`,
>   que se rechaza (1276)—: si no, SANCION-SIN-DECLARAR) →
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
>   gana) · `cero` (se reinicia: empata) · `negativa` (pierde); sin lectura
>   propia, la del 1X2 con `"guia": "pronostico"` (sad v4.4: `neutra` salió)—, con
>   `porque`, leyendo su gráfica de K y cómo se le cortan las burbujas
>   (`historial.*.termina` en `/burbujas`). No la acomodes a tu 1X2: lo que se
>   mide es si acierta sola. Y el ENSAYO la cuenta en un párrafo de las
>   burbujas (si no, el recibo avisa `ensayo.espina`). Si el equipo es otro en casa que afuera, leé la K
>   de la condición de hoy (`familias.local` / `familias.visita`) y declaralo
>   con `"guia": "condicion"`.
> - **La espina empieza en la tarjeta** (desde el 19/10): cada familia de
>   `/burbujas` trae `espinaTarjeta` (la espina que da la tarjeta sola, `fuerte`
>   o `debil`) y `GET /analisis/cowork/espina/calibracion` dice cuánto acierta y
>   quién gana cuando el analista la contradice. La calibración te llega en el
>   encargo (la lee el orquestador); pedila solo si no vino. Con tarjeta FUERTE, la espina la sigue salvo que un
>   skill (EFE, TDE, DTP, matriz) traiga un hecho de ESTE partido que la
>   contradiga, y entonces el `porque` dice «contra la tarjeta porque…» (si no,
>   el recibo lo cobra). Con tarjeta DÉBIL deciden los skills. El ensayo junta
>   las dos lecturas en una: qué dice la historia de las burbujas y qué le
>   agregan los skills de este partido.
> - **La espina contra el riesgo se dice**: si leés la espina contra el riesgo
>   calculado (alto y la dejás siguiendo la racha; bajo y la cortás),
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
