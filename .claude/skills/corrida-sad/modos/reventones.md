<!-- Modo `reventones` de la corrida SAD. Lo carga SOLO la corrida de este modo (SKILL.md dice cuándo). Credenciales y reglas comunes: SKILL.md. -->

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
