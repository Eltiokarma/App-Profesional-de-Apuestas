---
name: corrida-sad
description: Corrida del pipeline SAD con Claude Code (reemplaza a Cowork desde el 13/10/2026). Modo `partes` analiza los partidos de la agenda con los skills (EFE, Teorema del Echado, DTP, sad-analysis) y deposita un parte por partido; modo `veredictos` cierra con autopsia por skill los partidos jugados; modo `reventones` estudia hacia atrás burbujas que reventaron (TDE de los dos equipos, DTP, EFE de ese día). Usar cuando una rutina programada o el usuario pida «la corrida», «los partes de hoy», «validar lo de ayer» o «los veredictos».
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
2. `GET $B/analisis/cowork/agenda?desdeAhora=true&horas=N&limite=20` con
   el TRAMO de esta corrida, que termina donde empieza la siguiente (cada
   tramo cae en su propia ventana de 5 h del plan; un fin de semana trae
   15-23 partidos por tramo y la meta es el 80 % del padrón). N lo fija la
   HORA DE LIMA a la que corrés, aunque el disparo diga «24 h»:

   | Corrés entre (Lima) | Tramo | `horas` |
   |---|---|---|
   | 03:00 y 08:59 | 1 (hasta ~11:45) | 7 |
   | 09:00 y 13:59 | 2 (hasta ~16:00) | 6 |
   | 14:00 y 02:59 | 3 (hasta la madrugada) | 14 |

   Si el mensaje del disparo trae otros parámetros de agenda, mandan esos.
   Usá la misma consulta en el paso 4 → la lista de trabajo es
   `porHacer` (lo ya depositado está en `yaHechos`: no se rehace). Descartá
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
5. Respuesta final, tres líneas: partes depositados (fixtureId y partido),
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
>   faltar) → `equipos/{id}/burbujas?proximo={id}` de los dos → `cuotas/{id}`
>   → prensa (DT de ESTA semana, bajas, once probable) → el JSON del parte
>   EXACTO al punto 7 (a = local).
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
> - **Alertas: solo códigos que existen en los skills** (T.54, T.54-B,
>   R-KT.2, GK-DOWNGRADE, FACTOR-X, G-BLOQUE, G-SORPRESA, COLAPSO EN
>   CASCADA… los que nombra la rúbrica). Una observación que no tiene código
>   (un DT suspendido, un plantel desarmado, una trampa del mercado) va en
>   `notas` del bloque o en la lectura, NO como alerta con un código inventado:
>   un código nuevo no lo cuenta nadie y ensucia la tira. En la corrida del
>   13/10 aparecieron cuatro (DT-SUSPENDIDO, PLANTEL-DESMANTELADO, DC-TRAMPA,
>   BAJA-ORGANIZADOR).
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

## Modo `veredictos` (después del partido)

1. `GET $B/analisis/cowork/veredictos/pendientes?limite=30` → los partes
   jugados sin veredicto (lo que no entra queda para la próxima corrida, los
   más viejos primero: un fin de semana deja ~55 y en una sola ventana de 5 h
   no caben; si el disparo trae otro `limite`, manda ese). Si no hay, decilo en una
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
> `seleccion`: `ciega` si el partido salió de la agenda; `modoEvaluacion`:
> `PRE` si terminó. Con duda entre ciega y post_resultado, es post_resultado.
> `POST $B/analisis/cowork/{id}/veredicto` y leé `rechazos`. Respuesta final:
> marcador, veredicto por lado y la lista de lecciones (skill · regla).

3. Respuesta final, tres líneas: veredictos cerrados, lecciones por skill, y
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

## Al terminar cualquier modo: avisá al celular

Las rutinas corren solas y el usuario no mira la sesión. Mandá las tres
líneas finales al celular con la herramienta **PushNotification** (cargala con
ToolSearch `select:PushNotification`), también si la corrida falló o no tenía
nada que hacer. Sin el token, sin datos sensibles.

## Lo que NO hace esta corrida

- No levanta cuarentenas, no desmiente bancos, no abre revisiones ni marca
  lecciones `aplicada`: es del usuario, con la llave maestra.
- No commitea ni toca el código. Si encuentra un bug de la app, lo describe
  en la respuesta final (qué, dónde, con qué fixture) y nada más.
