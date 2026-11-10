# Deuda declarada, historia y siguientes pasos

Salió de `CLAUDE.md` el 03/11/2026 (pedido del usuario, para bajar el costo de
tokens): `CLAUDE.md` se carga solo en CADA paso de CADA agente que trabaja en
el repo —las rutinas de partes, veredictos, rehacer y mantenimiento y cada
subagente por partido— y esta historia (14 mil tokens) no le sirve a quien
analiza un partido. Acá está entera, sin cambios: se lee cuando hace falta
(el mantenimiento al clasificar una incidencia, quien revisa un skill, quien
retoma un pendiente del usuario). Lo NUEVO que se sabe roto o pendiente se
anota acá, no en `CLAUDE.md`.

## Deuda declarada (lo que se sabe roto o pendiente)

Está acá y no en la cabeza de nadie porque un pendiente que solo existe en una
conversación se pierde en la siguiente.

1. **El frontend recibía la llave maestra.** CERRADA (24/09/2026): la web
   lleva `SAD_TOKEN_WEB` (solo lectura) en `VITE_API_KEY` —en Vercel va como
   tipo **Config**: un Secret con prefijo `VITE_` no se puede guardar—, la
   maestra se rotó (se había filtrado en un chat el 23/09) y vive solo en el
   🔑 del navegador del dueño. Verificado por el usuario: la web carga y el
   modo administrador escribe. Queda, a conciencia: cualquiera con el link
   LEE los datos (no modifica ni gasta); cerrarlo del todo pide un login.
2. **Los DT de la ficha estaban viejos.** En la corrida del 16/09, 17 de 22
   entrenadores eran el SALIENTE (Bucaramanga con un DT de 2019). Causa
   encontrada: `/coachs?team=` devuelve a todos los que pasaron por el club
   y deja etapas viejas sin `end`; la ingesta tomaba la PRIMERA etapa abierta,
   que es la más antigua. Arreglado en `elegir_entrenador`
   (`backend/ingesta/jugadores.py`): manda la última alineación capturada y,
   si no, la etapa abierta con el `start` más reciente. Lo guardado con la
   regla vieja se rehace con `SAD_JUGADORES_SOLO_DT=1` durante UNA corrida
   programada (o `--solo-dt` a mano): 1 request por equipo. El `desde` trae
   el día 01 porque la API conoce el mes, no el día. El prompt (v2.5) sigue
   obligando a confirmar el DT en prensa antes de puntuar el bloque A.
   **Pendiente del usuario (16/09/2026, 18:00 Lima):** la variable ya está
   puesta en Railway; tras la primera corrida programada hay que QUITARLA,
   y la siguiente corrida de Cowork dirá si los DT ya salen bien. Desde el
   19/09 el refresco diario de `--dt-agenda` (punto 6) hace este trabajo
   solo para los equipos que juegan; la variable sobra.
3. **Colisión de nombres F3/F4.** RESUELTA sin renombrar (24/09): cada mención
   dice de qué skill habla. «No mandes F3 ni F4» es la alerta F3 y la
   rotación F4 DEL EFE (las calcula `bloque_f.py`); los indicadores F3/F4 del
   TDE SÍ van en `tde.bloques[].indicadores`. Lo dicen el prompt
   (`docs/COWORK.md`, con un recuadro) y el contrato que devuelve el backend
   (`loQueNoSeManda`). Renombrar habría desalineado los skills.
4. **Bucle de aprendizaje COMPLETO** (24/09): A (antecedentes,
   `GET /analisis/cowork/antecedentes/{id}`, solo partidos anteriores), B, C y
   D (dossier, `GET /analisis/cowork/revision/{skill}` + «Ver dossier»). Lo que
   falta es USO: casos ciegos en la cohorte vigente.
5. **Onces de ligas sin cobertura.** Medido el 24/09 con `ficha_partido
   --estado` (6.651 fichas, 44 % sin once): NUNCA dan alineaciones Paraguay
   División Intermedia (251), Venezuela Segunda (300), Bolivia Nacional B
   (710), Uruguay Segunda (269), Ecuador Serie B (243) y Copa Colombia (241);
   la mitad de las veces, Primera B de Chile (266) y de Colombia (240). Para
   esas el pantallazo a mano es el procedimiento (`nuncaVaALlegar`). La
   ingesta ya no paga por ellas: aprende la cobertura por liga (≥ 10 fichas
   sin un endpoint → no se pide; 1 de cada 20 sondea por si empieza a darlo)
   y no pide fichas de amistosos (`LIGAS_RUIDO`).
6. **Lo que la corrida de Cowork del 16/09 vio** (23 partes verificados
   contra prensa). Lo del DT, la agenda, el timeline, el contrato y
   `proximo=` se arregló en su momento; los cuatro puntos que quedaban
   anotados están hechos y quedan así:
   - **Calendarios y planteles vacíos en equipos que entran por el torneo**
     (Beşiktaş, NEC, Marsella, Crystal Palace, Torreense, Bournemouth).
     HECHO: `extractor.equipos_de_interes()` = los equipos de la edición
     vigente de un torneo internacional de clubes (`LIGAS_INTERNACIONALES`,
     una sola lista que la agenda importa); del feed por fecha se guardan
     TODOS sus partidos, estén en la liga que estén (0 requests), la purga
     de NS los respeta, `sanar_equipos_interes` les pide UNA vez la
     temporada doméstica entera (1 request por equipo, marcador en
     `.sanar_equipos.json`, tope `SAD_SANAR_EQUIPOS_MAX`) y la ingesta de
     jugadores los toma aunque su NS próximo sea fuera del padrón (su rival
     de esa liga no). Pendiente de ver en la próxima corrida real: que a
     esos equipos les aparezca el calendario y el plantel
     (`diagnostico --interes` lo lista). **Medido el 24/09**: 328 equipos de
     interés (entran los de las previas de UEFA), 84 con < 10 domésticos en
     el año —la temporada europea arrancó en agosto y solo estaba la
     vigente— y 67 sin plantel. Desde entonces `sanar_equipos_interes` pide
     también la temporada ANTERIOR (una vez, después de las vigentes de todos)
     para que el nivel tenga sus 20 partidos, y el diagnóstico mide la
     historia con los internacionales y dice por qué falta un plantel
     (`nunca pedido` · `API vacía`). La segunda medición dio 65 «API vacía»
     casi todos del MISMO día (17/09), Rennes y Shakhtar incluidos: un
     `/players` que FALLABA (red, límite) devolvía `[]` y se sellaba como
     «sin cobertura» por 30 días. Ya no se sella un fallo, y
     `jugadores --reintentar-vacios` re-pide los sellados así (dice cuántos
     eran error y cuántos siguen vacíos de verdad). Corrido el 24/09: 415
     sellados vacíos, 84 volvieron CON jugadores (eran error), 331 siguen
     vacíos —incluidos Ludogorets y Spartak Trnava, que la API sí cubre—:
     `jugadores --sondear <id>` dice si es la temporada (vigente vacía,
     anterior con datos) o que la liga no tiene cobertura. **Sondeado el
     25/09**: era la temporada —Ludogorets y Spartak Trnava con 0 jugadores en
     2026, 20 en 2025 y 27-31 en `/players/squads`—. HECHO: con la vigente
     vacía de verdad, la ingesta pide la lista actual (`plantel_actual`) y la
     temporada ANTERIOR filtrada a los que siguen en el club, y lo marca
     (`plantillas_meta.origen` = `anterior` · `plantel`); la plantilla viaja
     con `origenTemporada` y `plantelSinStats` (los que llegaron después), la
     pantalla de Equipo lo dice y el resumen para el EFE también. Cuando la
     API publica la vigente, el TTL normal (7 días) la toma sola. **Resultado
     (25/09)**: de los 331 que seguían vacíos, 307 quedaron con plantel
     (temporada anterior o solo la lista) y 24 son vacíos de verdad (la API no
     tiene ni lista). Un proceso largo desde la consola de Railway se corre
     con `nohup … > /data/x.log 2>&1 &`: la consola web lo corta.
   - **Nivel 3.2833 exacto en tres equipos**: NO es un tope ni un bug. El
     nivel vive en una retícula (~10.500 valores; ese tiene 24 combinaciones
     de puntos y goles). `docs/MOTOR_SAD_EXTRACCION.md` §2.5; `/niveles`
     trae `desglose` (P y G, verificado contra el nivel guardado) para que
     se vea de un vistazo. La fórmula no se tocó.
   - **Escala entre ligas**: HECHO. El parte agrega la alerta `ESCALA-LIGAS`
     (tipo `dato`, global) cuando la liga doméstica de cada lado —la más
     frecuente en su último año fuera de internacionales y amistosos— no es
     la misma base (`parte.misma_base`: mismo id, o mismo país en la misma
     categoría; Apertura/Clausura de Uruguay son la misma base).
     **Copas y divisiones (13/10/2026, Cristal–Bentín)**: una copa NO es una
     base (`backend/analisis/escala.py`, por lista o por nombre: FA Cup,
     Copa del Rey…); un equipo con solo partidos de copa en la base es
     `fuera del padrón` (casi siempre de abajo), no «primera». La alerta dice
     la relación (rival de categoría inferior · superior · fuera del padrón ·
     otra liga) y que el RIESGO DEL REVENTÓN también va con reserva: compara
     el nivel del rival con los que reventaron las burbujas en SU liga.
     `GET /equipos/{id}/burbujas` trae `escala` (las dos bases, la nota y el
     historial del equipo en copas contra otra base, con sus reventones) y la
     tarjeta lo pinta; los puntos calibrados no se mueven. En el estudio de
     reventones, `rival_de_otra_base` es señal CALCULADA; un amistoso que
     cierra la burbuja sigue siendo candidato (`enAmistoso`).
   - **El flag `Missing Fixture`** (acertó 10 de 23, separado por densidad):
     HECHO como señal con umbral. `PlantillaDTO.missingFixture` y
     `baja.lectura` (`senal`/`ruido`, umbral 25 % de la plantilla,
     `backend/jugadores.py`); una de ruido no cuenta en el resumen del
     skill, en la estabilidad de la burbuja (los dos lados) ni en las
     pantallas. El umbral es el primer corte: recalibrar con casos.
   - **El DT de la base, de nuevo (18/09, 4 de 19 con el saliente, de 3 a 27
     meses)**: la carrera de `/coachs` no lista al que llega. HECHO: la
     última alineación manda aunque no case con la carrera (`fuente`
     `alineacion`, `desde` = su primer partido en el banco), el nombre se
     arma con `firstname`/`lastname` (Tigres devolvía «Manuel Vucetich Rojas
     Victor») y `PlantillaDTO.entrenador` trae `fuente` y `actualizadoEn`.
     Lo guardado con la regla vieja se rehace en la próxima corrida de
     jugadores de cada equipo (TTL lento) o de una vez con `--solo-dt`.
     Y desde el 19/09 **el DT de la agenda se refresca cada día**
     (`jugadores --dt-agenda`, en la corrida diaria: alineación del último
     partido + `/coachs` si el registro tiene > 7 días o lo contradice; ≤ 2
     requests por equipo). La agenda lleva `dt.a/b` con `fuente`, `edadDias`
     y `fiable`; el parte avisa `DT-DISCREPANCIA` (la prensa manda, la base
     es alarma) y `DT-SIN-DT`; un parte con «sin establecer» en un lado va a
     cuarentena automática en el aprendizaje. Las alertas calculadas
     (`_ALERTAS_CALCULADAS`) no se depositan: el eco del GET las descarta.
   - **El DT de la base, tercera vez (22/09, Santa Fe–Cali con los dos DT
     cruzados; la Roma el sábado)**: NO era un cruce de equipos en la ficha
     —la alineación guarda al DT con el `team.id` de la API—. Era una
     ALINEACIÓN RANCIA: `dt_de_alineaciones` tomaba la última capturada sin
     mirar de cuándo era, y la liga colombiana dejó de publicar onces, así que
     «la última» era de meses atrás (Repetto sí dirigía a Santa Fe entonces)
     y le ganaba por regla a `/coachs`; el Cali salía con Dudamel por su
     etapa vieja abierta en la carrera. HECHO: la alineación cuenta solo si
     es de uno de los últimos `DT_ALINEACION_PARTIDOS` (3) partidos
     terminados del equipo; si no, manda la carrera. Y `dt_agenda` rehace
     con `/coachs` un registro `alineacion` que ninguna alineación fresca
     sostenga (`rancio`), aunque sea de ayer. `necesita_lentas` usa la misma
     regla. En la próxima corrida de `--dt-agenda` Santa Fe y Cali salen con
     `fuente: coachs` — y si `/coachs` también está atrasado, DT-DISCREPANCIA
     y la prensa mandan, como ya dice el prompt.
   - **`timelineEventos` válidos entran** pero Cowork reportó
     `eventosTimeline: 0` cuando mandaba tipos fuera de la lista; ahora se
     rechaza con motivo. Si vuelve a salir 0 con tipos válidos, mirar
     `timeline_del_parte`.
7. **Cierre de la sesión del 18-19/09/2026** (PR #66 a #75): `sad.db` de 30 GB
   a 0,54 GB (`adelgazar`, solo mercados del contrato, retención por fixture);
   los seis reportes de Cowork (niveles del TDE, `dt {nombre, desde}`, «sin
   establecer», DT desde la alineación, nombre del DT, procedencia del once);
   cuarentena, cohortes e intervalo de Wilson en Aprendizaje; reventón por
   período (todas las temporadas y años, DT, últimos 20) en la tarjeta y en la
   gráfica; DT fresco de la agenda cada día con alertas `DT-DISCREPANCIA` /
   `DT-SIN-DT` y cuarentena automática sin DT. **Lo que queda en manos del
   usuario, en orden:**
   - **Railway**: quitar `SAD_ADELGAZAR` (ya corrió; el marcador
     `.adelgazar_hecho.json` impide que se repita) y `SAD_JUGADORES_SOLO_DT`
     (punto 2); poner `Settings → Resource Limits` en 2 GB; mirar
     `Metrics → Memory` unos días: tiene que quedar plana por debajo de 1 GB.
     La factura del 08/10 todavía trae los días caros; la de noviembre es la
     primera limpia.
   - **Primera corrida con `--dt-agenda`** (06:30 del 20/09): en Deploy Logs la
     línea «DT de la agenda: N equipos · … · X DT cambiados» y que Sassuolo,
     Aucas, Comerciantes Unidos y ADT salgan con el DT vigente y `fuente`
     `alineacion`. Si un equipo sigue viejo, `ficha_partido --estado` dice si
     su liga da alineaciones; sin alineaciones la regla del banco no tiene de
     dónde sacar el DT y manda `/coachs` (que llega tarde): ahí la prensa es
     la única fuente y el prompt ya lo dice.
   - **Cowork**: los nueve partes con el índice en `ieNivel` (1550133,
     1557408, 1549491, 1549492, 1493146, 1493147, 1550967, 1639788, 1639849)
     se re-depositan con el nivel en la etiqueta y el número en `ie`; una
     pasada de `xi/auto` devuelve la procedencia del 1549492 a la ficha; el
     prompt vigente es el de `docs/COWORK.md` (dt con `desde`, la red manda
     sobre el DT de la base, `rechazos` se leen en cada depósito). Los partes
     de rodaje con `dt` vacío ya están en cuarentena automática.
   - **Aprendizaje** (actualizado 23/09): la cohorte vigente es ahora
     `c3-2026-09-23` (la `c2` tenía la alineación rancia del DT: referencia) y
     arranca vacía; un parte con el DT distinto del que se sentó en el banco va
     a cuarentena automática (`parte.dt_equivocado`, APRENDIZAJE.md C-bis; el
     apellido se compara tolerando la ß y una letra corrupta de la base). Un DT
     se corrige SOLO con `POST /analisis/cowork/{id}/dt` (abierto a Cowork;
     no toca nada más del parte), nunca re-depositando el parte entero. En
     la `c2`: la cohorte anterior (`c2-2026-09-19`) arrancó vacía; los
     42 casos de rodaje se miran con el selector y calibran nada. La
     cuarentena a mano queda para el caso puntual con motivo. Fases D y A
     hechas el 24/09 (punto 4).
   - **Reventón**: no hay backtest por período (la global sigue mandando en
     el riesgo, a propósito); «fase» (Apertura/Clausura) no está como período
     porque no vive en las filas del motor; las K de goles siguen fuera. Con
     datos reales, `temporada` en Europa es la 2025/26 entera y en Sudamérica
     el año natural: por eso viajan las dos.
   - **Sin cambios y aún abiertos**:
     deuda 5 (onces de ligas sin cobertura), el umbral de `Missing Fixture` a
     recalibrar con casos, y ver en la próxima corrida real que a los equipos
     de interés (Beşiktaş y compañía) les aparezcan calendario y plantel.
8. **Tres semanas sin cuotas prepartido** (18/09 → 11/10/2026). El filtro
   de mercados del 18/09 (`cuota_key`) hacía `.strip()` sobre el valor y el
   feed trae valores numéricos («Exact Goals Number»): el extractor se caía
   en la fase de cuotas con `AttributeError` en CADA corrida y refresco, sin
   guardar nada y quemando ~1.500 requests/día de `/odds`; los fixtures sí
   entraban (fase anterior) y el en vivo también (otro camino), por eso nadie
   lo vio. Arreglado en `cuota_key` (cualquier tipo) y `capturar_cuotas_lote`
   (un partido que falla al guardar no corta la corrida). Lección: una fase
   que no guarda NADA tres semanas seguidas tiene que verse — se notó porque
   los partes de LaLiga salieron con el mercado vacío. HECHO: el latido
   mira las cuotas prepartido (`cuotasPrepartido`: de los NS de las próximas
   48 h cuántos tienen captura y cuándo fue la última; con ≥ 10 y ninguno,
   ámbar con el motivo), por fixture contra el índice. El mismo día: el DT
   con dos apellidos no casaba (`mismo_nombre_dt`) y `xi/auto` mandaba a
   `nuncaVaALlegar` un once de la ficha en conflicto.

9. **El plan de API-Football se agotó al mediodía** (11/10/2026, 12:40 de
   Lima). El en vivo servía cuotas a quien llegara primero: el fútbol europeo
   de la mañana se comió el plan y la tarde sudamericana —Liga 1 incluida—
   quedó sin una cuota en juego hasta el reset (19:00 Lima). HECHO: reparto
   en el tiempo (`backend/ingesta/en_vivo.py`): una consulta por liga cada
   `SAD_LIVE_ODDS_INTERVALO_MIN` (2) minutos, cola por rango del padrón
   (Perú · internacionales · resto, `rango_liga`) y un ritmo que compara lo
   que queda del plan con lo que cuesta cubrir lo que falta hasta el reset
   (de igual o mejor rango) y, si no alcanza, ESTIRA el intervalo en
   proporción (tope `SAD_LIVE_ODDS_INTERVALO_MAX_MIN`, 15) en vez de dejar a
   alguien en cero. Y se ve: el marcador de la ingesta guarda el consumo por
   hora, la hora de agotado y el resumen de ayer; el latido lo trae en
   `presupuestoApi` y pasa a ámbar si el plan se agotó antes de las 22:00 UTC.

10. **Las autopsias del 11/10/2026** (`docs/autopsias/2026-10-11.md`, 24
   partidos cerrados con los skills) dejaron tres huecos de FORMATO, no de
   juicio, y ahora son campos que se cobran solos: la reasignación por primer
   gol del TDE (disciplina 44) va en `tde.bloques[].reasignacion` —el recibo
   avisa si falta y el veredicto dice qué rama jugó el partido—; la tabla F1
   se arma desde la base (`GET /analisis/cowork/f1/{id}`, `f1_base.py`) y un
   decisivo que falta grita `F1-DECISIVO-FUERA`; y el once oficial contra la
   apertura del DTP marca el bloque a rehacer (`contraElOnce`, `DTP-REHACER`).
   Un lado del veredicto lleva varias lecciones (`otrasLecciones`, items
   `fixture:lado:N`). Pendiente: cargar las lecciones de las autopsias en los
   veredictos del 11/10 y que el usuario abra la revisión de cada skill.

11. **Cowork queda sustituido por Claude Code** (13/10/2026; el 12/10 Cowork
   dejó sin parte 6 de los 8 partidos de la agenda). La corrida la hace una
   sesión de Code en la nube lanzada por rutinas, con el skill del repo
   `.claude/skills/corrida-sad/SKILL.md` (modos `partes` y `veredictos`, un
   subagente por partido) sobre el mismo contrato y prompt de
   `docs/COWORK.md`. Credenciales en las variables del entorno de la nube:
   `SAD_API_BASE` y `SAD_TOKEN_COWORK` (el acotado; el maestro nunca). El
   once ya no espera a nadie: el ciclo en vivo, al capturar alineaciones
   prepartido, corre `parte.cerrar_onces_pendientes` (lo mismo que
   `xi/auto`). **Las variables viven en DOS sitios**: Railway (el servidor
   que valida el token) y el entorno de Claude Code (las rutinas que lo
   usan); rotar el token o cambiar la URL es hacerlo en los dos. En el
   entorno de Code van en formato `.env` y un `#` abre un comentario: el
   token lleva uno, así que va ENTRE COMILLAS DOBLES (sin comillas se
   guardaba cortado en 11 de 20 caracteres y respondía 401). Ese campo es
   visible para quien use el entorno: vale para la fase de prueba con el
   token ACOTADO; al salir de prueba, rotarlo (9 de sus 20 caracteres se
   pegaron en un chat el 13/10) y pasarlo a una sección de secretos si el
   producto la ofrece. Rutinas (hora de Lima, desde el 17/10/2026): partes en TRES tramos, cada
   uno en su propia ventana de 5 h del plan y con los partidos que arrancan
   antes del siguiente —04:47 (`desdeAhora&horas=7`), 09:52 (`horas=6`) y
   14:56 (`horas=14`), `limite=30` desde el 25/10/2026 (antes 20; el usuario
   subió el plan, y un `limite` menor en el texto de una rutina se ignora);
   el tramo lo fija el SKILL por la hora de
   Lima, porque el texto de una rutina solo se cambia desde su propia
   conversación— en la sesión «SAD · corrida de partes
   (rutina)»; veredictos 20:12 (`limite=45` desde el 27/10/2026: con 30 la cola llegó a
   40 vencidos) en «SAD · corrida de veredictos (rutina, v3)»
   (`session_01WwsfbT7QwmMGN9rpzPDcW6`, rutina «SAD · veredictos (v3)»
   `trig_01MnCrTQMjsWo64rWVqoEsv7`, desde el 30/10/2026: la v2,
   `session_01WwsfbUiB1MkP3VjjniTpvR`, llegó a 692.000 tokens sin compactar y
   212 USD en tres días, y su rutina `trig_018kTWHJsh8y2evXLMySfJcF` quedó
   desactivada; la v1, `session_01BG2WdPWLP7jrAqFiDCC26P`,
   llegó a 571.000 tokens y se había usado para otra conversación: una sesión
   fija es SOLO de su rutina); **mantenimiento** 12:23 y 21:47 en «SAD · mantenimiento
   (rutina)» (desde el 22/10, deuda 17); **rehacer** cada 20 min desde el
   31/10/2026 (:02, :22 y :42, de 05 a 23 de Lima; antes cada 30, :07 y :37) en
   «SAD · rehacer DTP con el once (rutina)», desde el 22/10/2026: modo `rehacer`
   de `corrida-sad`, los partes con DTP-REHACER a 5-80 min del pitazo (antes
   15-80; depósito hasta el pitazo − 5), avisa solo si hizo algo. El once llega
   ~25 min antes y caía entre dos disparos (incidencia 636): `parte.REHACER_GRILLAS`
   juzga cada parte con la grilla de SU día. Un fin de semana trae 50-65 candidatos del padrón (15-23 por
   tramo) y la meta es el 80 % (`COBERTURA_META`, latido); medido el 17/10:
   ~5 dólares por parte y ~2,7 por veredicto a precio de lista, y una ventana
   de 5 h da ~150-200. Corren en sesiones FIJAS con el repo
   (cada disparo es un mensaje nuevo que hace `git pull` de main): una
   rutina de sesión nueva arrancaba sin el repo, sin `add_repo` y con otro
   modelo, y no pudo leer el skill (13/10, 12:48).
   **Disparar la rutina a mano** («ejecutar ahora», `fire_trigger`) tampoco
   sirve: abre una sesión NUEVA sin repo y con otro modelo, que termina sin
   hacer nada (17/10, 06:09). Una corrida fuera de horario se lanza mandando
   el mismo mensaje de la rutina a la sesión fija (`send_message`).

12. **El estudio de los reventones hacia atrás** (13/10/2026,
   `backend/analisis/reventones.py`, modo `reventones` de `corrida-sad`).
   Las probabilidades propias salen de entender POR QUÉ revienta una burbuja,
   no de la cuota: `GET /analisis/cowork/reventones?liga=` lista las burbujas
   significativas (≥ 3 partidos, o 2 sobre la mediana de la K pico) que
   reventaron —racha positiva que revienta / racha negativa que se corta—;
   `GET …/reventones/{fx}/{equipo}` las da «al día del partido» (burbuja y
   nivel de los dos con `antesDe`, ficha táctica, DT del banco); el estudio
   (`POST …/estudio`) aplica el TDE a LOS DOS equipos, el DTP y el EFE de ese
   día y guarda el MECANISMO y las SEÑALES PREVIAS de listas cerradas más
   lecciones por skill, que entran a Aprendizaje (`rev:…`). Población siempre
   `post_resultado`: fija rúbrica, no mueve números; el resumen por mecanismo
   es frecuencia entre estudiados, no probabilidad (falta el denominador de
   las burbujas que no reventaron). Primera tanda: Liga 1 Perú, 6 meses.

13. **Fuga del resultado en los backtests del reventón** (14/10/2026,
   `docs/REVENTON.md` §13.1). El «próximo rival» de los backtests salía de
   `fila["nivelRival"]`, que se escribe DESPUÉS del partido y ya trae el
   marcador; lo destapó el backtest del 1X2 (47 % → 54 % de acierto, demasiado
   bueno). Arreglado con `backtest_burbuja.nivel_rival_previo` y su test. La
   app no la tenía, pero los puntos de §12.2 (favorito −2/−4, tramo del rival)
   se calibraron con ella. Re-corrido limpio el mismo día (§13.2): AUC 0.715 →
   0.615, puntos nuevos (rival 0·1·2, favorito −1/−3, cortes 0/1/3) y
   `TASA_BACKTEST` rehecha; contramano y favorito siguen siendo reales, más
   chicos. Y el 1X2 limpio (§13.3): la burbuja NO mejora
   el pronóstico del motor (log-loss idéntico, IC cruzando cero, también con
   riesgo alto o extremo): no entra a la fórmula, queda como freno de la carga. Las K mismas tampoco (§13.4: resultado y goles,
   totales y por condición, cruzadas local × visita: Δ log-loss < 0.001 con
   IC cruzando cero): el nivel del motor ya contiene esa historia. Dos tropiezos
   del mismo día, con su guardia: una K con clave `ga` pisó el marcador (7 %
   de empates; ahora aborta fuera de 15-35 %) y el pipeline dejaba «no such
   table» mientras rehacía las derivadas (ahora en una transacción).
   **Las K se quedan en la LECTURA** (decisión del usuario, 14/10/2026): cada
   parte declara la **espina de la burbuja** por equipo (`lecturaSad.espina`:
   adónde va su K total después del partido —`positiva` crece/gana · `cero`
   se reinicia/empata · `negativa` pierde · `neutra`—, con `porque`), el
   veredicto la compara con lo que hizo la K (`objetivo.espina`) y Aprendizaje
   mide cada lectura contra la frecuencia de ese movimiento
   (`acreditables.espina`, Wilson, n ≥ 10). La tarjeta de burbujas dice cómo
   se le cortan al equipo (`historial.*.termina`: a cero o al otro signo) y
   el backtest da la guía calibrada por signo y riesgo (`movimiento`,
   REVENTON §14). Una lectura fuera de las cuatro se rechaza con motivo.
   **La espina puede leerse con la K de la condición** (15/10/2026, pedido del
   usuario: hay equipos que en casa ganan siempre y afuera no): `guia: total |
   condicion` por lado (la K local si juega de local, la de visita si es
   visitante); el movimiento se juzga con el mismo marcador y Aprendizaje mide
   cada guía aparte (`acreditables.espina.porGuia`). La guía de movimiento por
   condición sale del backtest (`movimientoCondicion` en `--calibrar`,
   `MOVIMIENTO_CONDICION` en `burbuja.py` y su espejo TS, REVENTON §14.1) y
   viaja en `riesgo.movimiento` de `familias.local`/`visita` solo si esa
   familia se mueve en el próximo partido. La + de local aguanta más que la
   total y la + de visita menos; la − de visita es la que más se sostiene.
   **La espina empieza en la tarjeta** (19/10/2026, pedido del usuario: «tiene
   una base más sólida y estadística; hay que juntarlo con los skills»):
   `espinaTarjeta` (el movimiento más probable de `riesgo.movimiento` como
   positiva · cero · negativa, `fuerte` ≥ 50 %, `burbuja.espina_tarjeta` y
   espejo TS, vectores `scripts/casos_espina_tarjeta.json`) viaja en cada
   familia de `/burbujas` y en `reventonCalculado`; el parte la sigue o dice
   «contra la tarjeta porque…» (si no, `faltan`; la débil no se cobra), el
   veredicto guarda las dos (`objetivo.espina.*.tarjeta`/`vsTarjeta`) y
   `GET /analisis/cowork/espina/calibracion` dice quién gana cuando el
   analista la contradice (REVENTON §14.2). Con guía de la condición, el
   veredicto mide la tarjeta de la condición (Monza 4-0 Cagliari: la total del
   Cagliari estaba en 0); y `objetivo.tarjetas` lee las DOS tarjetas del
   partido como un 1X2 —concuerdan · discrepan · una sola— para medir si dos
   tarjetas débiles que coinciden aciertan más que una sola
   (`acreditables.espina.tarjeta.partido`): medición, no regla todavía.

14. **Integridad del partido: solo ANOTACIÓN** (15/10/2026, decisión del
   usuario tras el Roma 3-4 Real Madrid de la Champions: un gol de pelota
   parada con dos defensores que saltan y el rematador solo). El sistema NO
   juzga amaño, ni de jugadores ni de árbitros, y nada de esto entra a la base,
   al parte ni a una métrica: con un video no alcanza y una etiqueta así sobre
   un partido o un jugador no se pone sin pruebas. El usuario irá contando
   estos casos en la conversación. Pendiente de RASTREAR, sin construir:
   si algún indicador medible podría alertar —el candidato es un movimiento
   anómalo de las cuotas en vivo (`odds_live`) contra el marcador, que es lo
   que usan los servicios de integridad—. Una remontada sola NO es señal: lo
   que se predice es el resultado final.

15. **Cierre de la sesión del 14-15/10/2026** (PR #120 a #142). Hecho: el
   backtest del reventón y del 1X2 limpios de fuga (deuda 13), la espina de la
   burbuja con guía total o de la condición y su guía de movimiento calibrada
   (REVENTON §14-14.1), la matriz estructurada por equipo con su probabilidad
   por escenario, el reventón calculado con la K de la condición al lado de la
   total, `DTP-REHACER` con varios sistemas y una carpeta por subagente en
   `corrida-sad`. **Para revisar en la próxima sesión, en orden:**
   - **Partes con la matriz nueva** (primeros: corrida del 15/10, 12:48 Lima):
     que traigan los escenarios por equipo con sus filas y su probabilidad, si
     el recibo avisó `matrizVsPronostico` y cómo se ve el cuadro en Lectura.
   - **Espina**: primeros veredictos que la miden el 16/10 (06:52 Lima);
     cuántos partes usaron `guia: condicion` y cuántos la total. Aprendizaje
     compara recién con n ≥ 10 por lectura.
   - **Reventón con la K de la condición**: que `reventonCalculado.*.condicion`
     salga con número en partes como Boca–Vasco (1639863: total en 0 tras un
     2-2, K local de Boca +18 y de visita de Vasco +6, las dos muy alto) y que
     la guía de movimiento por condición aparezca en la tarjeta.
   - **Fichas**: que la corrida de fichas complete las stats del 1549745
     (Bucaramanga–Águilas, `capturada` con stats vacías: alineación y eventos
     venían del ciclo en vivo); su falsador quedó sin evaluar y el veredicto
     ya está cerrado. El once de Águilas trae a «Eduar Arízalas» titular sin
     id (id negativo nuestro) y además entrando al 86': es dato de la API; si
     se repite, marcar como anomalía al titular que también entra de cambio.
   - **Skill `efe-dashboard`** (fuera del repo, del usuario): decidir si dice
     que la matriz es narrativa con números y si se escriben o se quitan el
     «checklist de 9 puntos» y la «Ficha de Mecanismo», que no existen.
   - **Ideas propuestas, NO pedidas**: medir en Aprendizaje la estimación
     propia contra el mercado y el motor (las cuotas ya están en la base);
     juntar el marcador exacto (19 de 46 partes dieron 1-1, 6 exactos); espina
     de goles (las K de goles siguen fuera del reventón por decisión).
   - **Del usuario, sin cambios**: levantar con 🔑 las cuarentenas falsas,
     abrir la revisión del TDE, decidir Jev y rotar el token acotado al salir
     de prueba (deuda 11).

16. **La Ley 5 del skill `sad-analysis` (Tensión del Favorito / culebra) sale
   del skill** (19/10/2026). REDACTADO el 21/10 en `sad-analysis` v4.0
   (`docs/revisiones/SAD_v4.0_propuesta.md`): la Ley 5, la Fe Perdida, el
   Poisson v6 y la Ley 8 quedan suspendidos —el skill era del sistema viejo y
   78 de 209 partes armaron el 1X2 con un Poisson sobre μ—, el skill pasa a ser
   el de la síntesis y las K pesan el 60 % de la LECTURA (decisión del usuario).
   Pendiente del usuario: subir el zip a su cuenta. Hoy es «filtro obligatorio» y parte
   de la «convergencia crítica» (K techo + DC trampa + tensión → el favorito
   no gana). Lo medido: el estudio de ML de feb/2026 dejó `ml_break_score`
   roto (42,9 % en cero, sin relación con resultados) y el ICF con r = 0,10;
   y el backtest del 19/10 (63.475 partidos del padrón 2019-2026, 43.118
   favoritos por nivel previo + 2.088 por cuota prepartido real) no encontró
   culebra: con la jornada «intacta» el siguiente favorito gana igual o algo
   MÁS de lo esperado (+0 a +4 pts, IC cruzando cero), en el día entero y en
   la jornada de una liga. La combinada de los k favoritos del día sale lo que
   da el producto de sus probabilidades (4 favoritos: 14,3 % contra 13,0 %):
   que «alguno no gana» es multiplicación, y lo que la hace perder es el
   margen de la casa cobrado una vez por partido (favorito suelto −4 %). Lo
   que queda en pie para reescribirla: «la combinada de favoritos tiene poca
   probabilidad y paga el margen k veces», sin «el siguiente favorito va a
   caer». Las K (Ley 1) son la teoría central y NO se tocan. Pista sin prueba
   (71 días con cuotas): la combinada de los favoritos MÁS fuertes del día
   salió más de lo que pagaba el mercado (+48 %, IC −9 % a +116 %); seguir
   midiéndolo con más días antes de creerlo.

17. **Cierre de la sesión del 21-22/10/2026** (PR #173 a #193). Hecho:
   1X2 del motor desde μ (`unXDos`, logística calibrada), `sad-analysis` v4.0 y
   `efe-dashboard` v1.9 (en la cuenta), EFE v1.6, DTP v1.4, TDE v0.1.22 (ramas
   con su número, redactada), doble oportunidad incoherente fuera, aviso del
   1X2 sobre el motor (`pronosticoVsMotor`), rutina de rehacer DTP cada 30 min,
   veredicto del TDE tramo por tramo con la ventana del reloj aparte, y la cola
   de incidencias vaciada (88 → 0; casi todas eran pocas causas repetidas:
   `contraElOnce`, identidad del jugador, tabla F1, bajas, duplicados). Railway
   estuvo caído el 21-22/10 y producción quedó en el PR #171: un push durante
   la caída se pierde (`docs/DESPLIEGUE.md`); desplegado el 22/10 con el #185.
   **El mantenimiento corre en su propia sesión fija** desde el 22/10, 12:23 y
   21:47 de Lima, POR GRUPOS de causa (hasta 3 grupos de código por pasada, un
   PR por grupo). Desde el 27/10 en «SAD · mantenimiento (rutina, v2)»
   (`session_01WwsfbSrNaKynS84SUXEwvA`, con el paso 0 de aprobadas, por
   desplegar y cola del usuario). **Desde el 30/10/2026** (usuario: «sube el
   mantenimiento»), tres pasadas con el escaneo preventivo. **Desde el
   31/10/2026, sin tope y con la cola en cero como meta**: «mediodía, v4»
   `trig_015duhSraveED4viUq6nFXkL` (12:23), «tarde, v4»
   `trig_01FM66KeT2BUGgcdRJhCCBnw` (17:41) y «noche, v4»
   `trig_01QVZvEiqDoHi33Y6KRFZCev` (21:47), con un texto que NO lleva números
   («manda el skill, no este texto»): las v3 (`trig_014bHDmKimigTHfUyw7NxqjJ`,
   `trig_01UptRFtNs3mW8sXUGzmg2ju`, `trig_01GF5XY1GyyskhDNBe496hDG`) y las v2
   (`trig_01L7qjpE7b5BRCH5DRbQLyPz`, `trig_01AJ8oSr5jAadzyq6ZN6rgid`) quedaron
   desactivadas porque su texto decía «hasta 6» o «hasta 3» y solo se edita
   desde su propia conversación. Con tres pasadas la sesión engorda más rápido: revisar su
   tamaño cada dos o tres días; la v1
   (`session_018rYwkkxMKQpJpfTdkxScvd`) llegó a 341.000 tokens y 69 USD en
   cinco días y sus rutinas quedaron desactivadas. Las dos rutinas viejas, que disparaban en la sesión de trabajo,
   quedaron DESACTIVADAS (no borradas). **Pendiente, en orden:**
   - **Del usuario**: subir `teorema-del-echado` v0.1.22 a la cuenta (zip de
     `docs/skills/teorema-del-echado/`) y verificar que cargue; marcar con 🔑
     las lecciones de Sporting–LASK y de las ramas como `aplicada` en v0.1.22;
     desmentir el banco de Juárez si quedó en cuarentena (incidencia 356);
     levantar las cuarentenas falsas; rotar el token acotado (deuda 11).
   - **Verificar**: el primer disparo de la sesión nueva de mantenimiento
     (23/10, 12:23 Lima) — que tenga el repo, las credenciales y agrupe; la
     próxima corrida del pipeline saca los duplicados (Rayo Zuliano 16/09 y
     11/06/2025, Portuguesa 16/09: su K deja de sumar el partido dos veces;
     `pipeline --duplicados` los lista); las bajas `desmentida` en Equipo.
   - **Rutina de rehacer**: desde el 27/10 en la sesión
     `session_01WwsfbTrhC56SCybz9zK3CQ`; desde el 31/10/2026 con las rutinas
     `:02, v5` `trig_01Gv8F164s7s6aYVMRXyD5Lr`, `:22, v5`
     `trig_01HaXT3mjisnuqwhoC7LnuAy` y `:42, v5` `trig_01M8XfUko8f6H4r26HYm14Rr`
     (las `:07, v4` y `:37, v4` quedaron desactivadas), más `:12, v5`
     `trig_01Lo32FnwNkLfNc4RcBYPRma` de 10 a 23 desde el 01/11/2026 (989); al rehacer, el SOB2 y el
     C1 del TDE se reescriben con el DTP rehecho, nunca el DTP vuelve atrás para
     callar HERENCIA-DTP (634). Los pendientes ya aprobados para la próxima
     revisión de cada skill viven en `docs/revisiones/PENDIENTES.md`. La v3
     (`session_01RrrZSSk2eoz89TzKFput5q`) llegó a 660.000 tokens y 30 USD en dos
     días. Del 26/10 al 27/10 en la v3 (la v2,
     `session_01X5KodpKV93A7bBePdiczAZ`, llegó a 570.000 tokens en dos días y
     ~0,36 USD por disparo vacío: con los rehaceres el historial crece rápido,
     rehacerla cada pocos días). Antes, desde el 24/10, en la v2 (el
     texto llama a `GET /analisis/cowork/rehacer` ANTES de cualquier git); la
     vieja (`session_01V3tPBuV4pgvD7rMF39twu9`, rutinas desactivadas) releía
     ~490.000 tokens de historial en cada disparo vacío (~0,33 USD, ~12 al
     día). Una sesión fija de rutina se rehace cuando su historial engorda. Medido el
     22/10, ~0,25 USD por disparo vacío (crece con el contexto de la sesión) y
     ninguno rehízo nada por la tarde. Decidido (usuario, 22/10): comprobación
     barata `GET /analisis/cowork/rehacer` (los partes con DTP-REHACER a 15-80
     min); el skill la llama primero y el mensaje de las rutinas v2 también.
   - **Hechos el 22/10** (usuario): COLAPSO EN CASCADA calculada (162:
     `equipos.{lado}.d3` ✅/🔶/❌, o leído de la nota del bloque D;
     alerta `COLAPSO-EN-CASCADA`, escenario de perder la ventaja, sin goleada);
     Jev pregunta el reventón de la total y el de la condición por separado
     (160); F2 del TDE a 1 con un clásico o una eliminatoria internacional de
     octavos en adelante a ≤ 5 días (339, `f2.exigenciaProxima`: la rúbrica ya
     lo decía, faltaba el cálculo; Estambul entra a los clásicos documentados).
   - **Hechos el 23/10** (usuario, tras ver los casos): récord de racha solo si
     SUPERA el máximo y con 3+ partidos (67; igualar con 3+ queda en ámbar;
     REVENTON §10.3: Cusco, Medellín, Juan Pablo II y Leones del Norte dejan de
     gritar, el Leipzig con 11 sobre 9 sigue); INFLADA en cualquier racha
     abierta con la mitad o más de amistosos (311, Stuttgart); y la
     estabilidad cuenta llegadas y salidas CON MINUTOS en el primer equipo
     (43, `jugadores.revolucion_de`, `revolucion.enPapeles` con el total: 58 de
     60 equipos de la agenda salían «inestables», la Juventus por 85 traspasos
     de los que 7 jugaron); la llegada cuenta si jugó DESPUÉS de llegar (#201)
     y los cortes pasan de 3/6 a **10/20** (usuario: con minutos, 82 de 82
     seguían sin salir estables; primer corte sin backtest, revisar con casos). Lo de otra categoría (el ascendido juega distinto)
     lo considera el analista con `escala`; el cálculo no se corta.
   - **Mantenimiento del 23/10, revisado** (#196-198 bien hechos): la 44a NO se
     cobra a los partes creados en la caída de Railway (21/10 09:28 → 22/10
     14:00 UTC, `veredicto.SIN_RAMAS_SERVIDOR`: el servidor rechazaba
     `siLeEmpatan`; sale «no evaluable», 393); y dos «dato de la API» pasan a
     código (usuario): el mismo jugador con dos ids y minutos en los dos se
     funde en la tabla F1 si el nombre completo coincide y nunca estuvieron en
     la misma hoja (381, `idsAlternos`, el bloque F casa con cualquiera), y el
     titular habitual solo por minutos es decisivo hoy si fue titular en la
     mitad de los últimos onces (387, `f1_base.decisivo_hoy`).
   - **Copas nacionales de Europa a la base** (406, usuario 23/10): FA Cup,
     EFL Cup, Copa del Rey, Coppa Italia, DFB-Pokal, Coupe de France y Taça
     de Portugal entran a `LIGAS` como MENORES —la misma regla que las copas de
     Sudamérica, que ya entraban al motor—: salen gratis del feed por fecha, el
     backfill baja sus temporadas, no van a la agenda ni al en vivo, y
     `extractor.COPAS_EUROPA` no elige equipos para fichas ni cuenta como liga
     doméstica (el de quinta división de la FA Cup no gasta requests). Las K
     de los equipos europeos pasan a contar sus partidos de copa. La copa de
     Bélgica (147) entró el mismo día, con el id confirmado en Railway.
   - **Missing Fixture, 24/10** (usuario, 415 con 71 y 312): la densidad cuenta
     solo las marcas VIGENTES —las que el once ya desmintió inflaban el 25 %:
     Real Madrid 10 de 30 (ruido) eran 3 vigentes (señal)— y una SANCIÓN (roja,
     amarillas, suspensión) es señal aunque el equipo esté en ruido
     (`jugadores.es_sancion`). El umbral del 25 % no se movió. La 408 (punto
     por racha ≥ mediana con mediana 1) quedó por diseño: separa equipos.
   - **Decisiones del 24/10** (usuario, tras el mantenimiento): FAMILIA-RECORD y
     `porExplicar` solo con la racha RARA para el equipo (420, 450:
     `probRacha` = frecuencia propia ^ largo < 5 %, REVENTON §15.2); la rutina
     de rehacer mira desde 15 min (444, 451, 454: el once llega ~27 min antes;
     depósito hasta el pitazo − 10); semifinal y final de copa nacional suben
     el F2 del TDE a 1 a ≤ 5 días (435; cuartos y antes no).
   - **Documentos del parte** (usuario, 24/10): el ensayo es la PRIMERA pestaña
     y el parte abre en ella; la prosa del TDE, del DTP y la matriz va debajo
     de su pestaña y «Documentos» queda para otros ids (desaparece si no hay).
     Al depositar, un documento sin `id` se rechaza con motivo (los 17 partes
     del 16/09 tenían 4-5 «nota» sin nombre: se titulan con su primer
     encabezado) y dos con el mismo id dejan el último. El veredicto muestra
     la confianza del 1X2 («Dijimos LOCAL 54 % (54/26/20) · tramo 50-59 …»),
     también arriba del ensayo. Arriba quedan el veredicto y los anillos del
     EFE; la carga del once y «Alertas y revisor» van PLEGADAS debajo de las
     pestañas (con su resumen: cuántas alertas, cuántas estructurales).
   - **25/10** (usuario): la cola de onces del ciclo en vivo pide PRIMERO los
     partidos con parte, después los que no empezaron y al final los en juego
     (`en_vivo.fixtures_para_xi`: Leipzig, Coventry y Antwerp llegaron al
     pitazo sin once capturado; 444/451/454/562/564/567/570 son esa causa). Y
     el botón 🔑 «Cerrar las anteriores a vX» del dossier pasa a `aplicada` las
     lecciones de partidos anteriores al corte de la versión vigente
     (`lecciones.CORTE_VERSION`: actualizarlo con cada versión nueva).
   - **Skills, 25/10** (usuario aprobó): **DTP v1.5** (`docs/revisiones/DTP_v1.5_propuesta.md`:
     quinta vía de gol, caso de la pregunta 6 completo, dos ramas por marcador,
     MECANISMO-ABIERTO con régimen, dos carriles con vuelta, `m2.piezas` contra
     el once —una pieza en el banco pide rehacer, incidencia 525— y
     `xiReferencia` vacío rechazado) y **sad-analysis v4.1** (calibración del
     1X2: el empate parte del mercado, el favorito ≥ 50 % no se recorta bajo el
     mercado sin dato propio; bajas del ataque rival por zona). El SOB2 del TDE
     sigue heredando el nivel de hoy, no la rama persiguiendo (pendiente del
     usuario). Y **TDE v0.1.23** (aprobada entera, incluye la v0.1.22 que nunca
     se subió): `siIguala`, `siExpulsion {propia, rival}` (→ `siExpulsionRival`),
     la línea del empate y de la expulsión exigidas en el recibo, la cuenta de
     jugadores manda en la disciplina 16, `salida: otra_via` (penal o autogol)
     y la casilla `anadido` del cierre; el IE no lleva color (una banda en
     `ieNivel` ya no se rechaza, 533) y `TIPOLOGIA-VS-INDICES` avisa la
     tipología que contradice IE contra ISE (538). Los tres subidos el 25/10.
     Y **EFE v1.7** + `efe-dashboard` v1.10 (aprobada entera el 25/10, desde
     las 168 lecciones del 21-24/10, `docs/revisiones/EFE_v1.7_propuesta.md`):
     F3 por zona y recambio de oficio/reconvertido, jerarquía de fuentes del F1
     (agregador = duda), D3 con contexto, rama «once alternativo» con
     calendario exigente, brecha de porcentaje solo en la misma base,
     EJE-DEBUTANTE en el clasificador con ≤ 1 partido juntos
     (`dtp_cowork.parejas_nuevas_de`) y T.54 con interino que repite el once.
     Pendiente del usuario: subir los dos zips y cerrar con 🔑 las anteriores.
   - **DTP-REHACER con su hora (26/10)**: el veredicto del 25/10 dio 12
     lecciones «sonó y no se rehízo» y la rutina había rehecho 18 partes: la API
     corrige la formación en el refresco de los últimos 15 min, cuando ya no
     queda disparo. Cada versión del once queda con su hora
     (`alineaciones_versiones` en sad.db), el parte sella su último depósito
     antes del pitazo (`deposito_previo_en`) y, jugado el partido, la alerta
     trae `momento` (`tardio` · `sinRehacer` · `conocido`, `parte.momento_rehacer`);
     el veredicto no carga un `tardio` al skill. Y los partidos CON parte
     piden el once otra vez a 40 min del saque (`en_vivo._refresco_temprano`)
     para que el disparo de :07/:37 vea la versión corregida.
   - **DTP v1.6 (26/10, usuario aprobó entera)**, desde las 123 lecciones del
     25/10 (`docs/revisiones/DTP_v1.6_propuesta.md`): `m2.veredictoRamas` (un
     veredicto por rama; `objetivo.dtp.porBloque[].ramaJugada` dice cuál se
     jugó, por minutos), el área desde el lado débil y la segunda línea, M1
     desde el último once y su grid (aviso `M1-VS-ULTIMO-ONCE`), el ejecutor
     de penales de la base (`penales` en los insumos del DTP, aviso
     `DTP-PENAL-SIN-EJECUTOR`), `casoBloque.sede`/`competicion` (calculadas si
     faltan; aviso `P6-OTRA-SEDE`), el costo de rearmar la línea, el
     reasignado con tarjetas, la media distancia contra el estructural y M5
     con volumen y conversión aparte. Pendiente del usuario: subir el zip y
     cerrar con 🔑 las anteriores a v1.6.
   - **EFE y sad, reglas que se incumplían, calculadas (26/10, usuario)**: de
     las lecciones del 25/10, `EFE-EMPATE-TECNICO` (brecha del EFE ≥ 5 con T.54 /
     R-KT.2 en un lado o ESCALA-LIGAS: no ordena el partido; el recibo lo avisa
     si el parte no dice «empate técnico») y `ESPINA-SIGUE-EN-EXTREMO` (la
     espina «sigue» con K-EXTREMO o K-CERCA-EXTREMO, total o de la condición).
     Las revisiones EFE v1.8 y sad v4.2 quedan para el 28-29/10, con partes
     escritos de punta a punta con v1.7 y v4.1.
   - **Ventaja sobre el mercado (26/10, usuario, tras PSG–Lyon 70 % contra 71 %)**:
     `vsMercado` del GET del parte (`parte.ventaja_mercado`, al leer, contra la
     última captura prepartido): por selección, nuestra contra el mercado sin
     margen, la cuota media (con margen), la justa y el valor esperado; estado
     `con valor` (valor ≥ 3 % Y ≥ 3 pts sobre el mercado) · `sin ventaja` ·
     `sobre`/`bajo el mercado`. Caja «Contra el mercado» en el pronóstico del
     parte. Seguir al mercado (sad v4.1) es el mejor pronóstico, no una apuesta.
     **Corregido el mismo día** (usuario, Santa Clara–Benfica: «valor» de 14 %
     contra 10 % a cuota 9 en verde, nacido de recortar al favorito): sin
     historial el estado es `valor en el papel` (ámbar); `naceDeRecorte` lo
     dice cuando sale de dejar al favorito del mercado (50 %+) 3 pts abajo sin
     «−N puntos al favorito por <dato>» escrito (6-B). `con valor` vuelve solo
     con `parte.historial_valor` confirmado: apostar 1 unidad a cada selección
     con valor, a su cuota, en los partes que acreditan, n ≥ 50 y el intervalo
     de la ganancia sobre cero; la tabla «Valor contra el mercado · ¿ganó?» de
     Aprendizaje lo muestra (con recorte, sin recorte y siempre a nuestro
     elegido de referencia).
   - **Mantenimiento del 27/10, decisiones del usuario**: (712) el DT corregido
     DESPUÉS del pitazo con `POST …/dt` no saca el caso de la cuarentena: se sella
     el original (`dt_original_json`, una vez por lado) y `dt_equivocado` compara
     con ese; antes del pitazo la corrección manda. (673, con 619 y 667) el mismo
     jugador con iniciales distintas («J. Bisanz» / «F. Bisanz») se funde en la
     tabla F1 con el mismo apellido, nunca juntos en una hoja y, además, sucesión
     (uno deja de aparecer cuando aparece el otro) o los mismos goles y
     asistencias (no cero); sin pedir la posición, y la fila queda marcada
     `fundidoPorInicial`. Dos pilas enteras distintas siguen siendo dos personas.
     Y la **cuarentena que enseña** (usuario, por Comerciantes–Cienciano):
     `POST …/cuarentena` con `ensena: true` saca el caso de toda métrica pero
     deja sus lecciones con las del skill y en el dossier, fijando rúbrica
     (`cuarentenaEnsena`, casilla marcada por defecto en Aprendizaje). La
     automática por DT EQUIVOCADO también enseña (usuario, mismo día); la de
     parte sin DT y la de parte de otra fecha no.
     **Una regla no se cobra hacia atrás** (usuario, 28/10): el desenlace por
     defecto del TDE v0.1.24 sale `noEvaluable` en un parte creado antes del
     26/10 04:00 UTC (`veredicto.DESENLACE_DEFECTO_DESDE`; lo declarado se mide
     siempre) y ESPINA-SIGUE-EN-EXTREMO / EFE-EMPATE-TECNICO en un parte
     anterior al 26/10 05:00 UTC viajan con `posteriorAlParte`
     (`parte.REGLAS_CALCULADAS_DESDE`): se muestran, no se cobran.
   - **EFE v1.8 y sad-analysis v4.2 (28/10, usuario aprobó enteras)**, desde
     las 179 y 165 lecciones de los partes del 25-27/10
     (`docs/revisiones/EFE_v1.8_propuesta.md`, `SAD_v4.2_propuesta.md`). EFE:
     T.54 en los dos lados con la fecha del DT (alerta calculada
     `T.54-SIN-DECLARAR`, que cuenta para `EFE-EMPATE-TECNICO`), arquero
     suplente con rodaje y arco sin dueño, la zona del ausente por su rol en el
     once y el eje del medio, fuentes del F1 con fecha y la caja de
     sensibilidad que baja al matchup; `efe-dashboard` v1.11. sad: el delta de
     la cuota y la razón que cae (6-A), los dos perfiles DC alineados como
     hecho (6-B), la tarjeta débil de la condición no se sigue por defecto y
     la lista de lo que no es un hecho (1.6), falsador sobre conversión o vía
     y marcador con el volumen de los dos lados. La v4.1 acertó 44 de 67 (66 %)
     y la v4.2 no afloja ninguna de sus reglas. Pendiente del usuario: subir
     los tres zips y cerrar con 🔑 las anteriores a v1.8 y a v4.2.
   - **Aprendizaje reordenado (25/10)**: resumen sin lecciones, pestañas, el
     cierre en bloque arriba de cada skill, lecciones de a 20 y el inventario
     guardado por huella (`SAD_CACHE_INVENTARIO_S`; antes 46 s y 6,3 MB). La
     versión vigente sale de `CORTE_VERSION` (en Railway no hay `docs/`): con
     cada versión nueva se suma ahí, y un test exige que coincida con el
     snapshot. **Confianza del 1X2**: tabla por tramo y versión en «Métricas ·
     confianza» y marca de color en Partidos (`src/lib/confianza.ts`).
   - **Escala entre ligas** (300, 309, 294, 79): decidido «solo marcar» (22/10):
     rival (`escalaComparable`), tarjeta de la espina, perfil DC y P1a llevan la
     marca y su nota; ningún número calibrado se mueve.
   - **Decisiones del usuario** (incidencias en `usuario`, con su propuesta
     escrita): escala entre ligas en el reventón, la espina y el P1a (300,
     309, 294, 79: el rival no suma con `ESCALA-LIGAS` y la espina no sale
     «fuerte» — números calibrados, con el backtest a la vista); derbi a ≤ 5
     días en el F2 del TDE (339, regla del skill); COLAPSO EN CASCADA
     calculada desde los D3 del EFE (162); dos falsos positivos de Jev (160,
     338); estabilidad inflada por cesiones (43); marca INFLADA en la K de la
     condición (311); racha récord con mínimo 3 partidos (67). Y recalibrar
     el umbral del 25 % de `Missing Fixture` con 28, 71 y 312 (ruido que era
     baja real; la API que no marca una lesión publicada).
   - **TDE v0.1.24 (26/10, usuario aprobó)**, desde la medición sobre los 253
     casos ciegos de la cohorte c3 (`docs/revisiones/TDE_v0.1.24_propuesta.md`):
     disciplina 65, las ramas del que persigue declaran `desenlace` (`se_rompe`
     · `rescata` · `abierto`; con ISE de rama ≥ 7 el defecto es `se_rompe`:
     remontó 2 de 38 contra 7 de 33 con < 7), el recibo lo pide, el veredicto lo
     mide por tramo (`tramos[].desenlace`) y Aprendizaje lo cuenta
     (`acreditables.desenlaceTde`, tasa con n ≥ 10; el corte en 7 se revisa con
     n ≥ 30); disciplina 66, con la ventaja manda el minuto del gol y no el IE
     (`GET /analisis/cowork/tde/{id}` → `referencias.ventajaPorMinuto`, de la
     base y anterior al partido). Lo medido que NO se sostuvo y no se escribe:
     las dos espinas en «cero» no anuncian el empate, la espina contra la
     tarjeta acierta igual que la que la sigue, la brecha del EFE con T.54 y la
     rama «persiguiendo» del DTP no separaron; EFE v1.7, DTP v1.5 y sad v4.1 se
     miden antes de proponerles nada. Pendiente del usuario: subir el zip del
     TDE v0.1.24 a la cuenta.
   - **Ideas, no pedidas**: pintar los `tramos` del veredicto en Aprendizaje y
     en la vista de derrotas del favorito (12 de 44 tuvieron segundo giro);
     el 1X2 de la cohorte sale SUBCONFIADO (60 %+ acertó 18 de 18, 40-49 %
     → 54 %): medir con más n antes de tocar nada; archivar la sesión
     temporal `session_01NuzvTgFR41DgJsU122s6EE`.

18. **Ideas del usuario por hacer** (30/10/2026), sin construir todavía:
   - **El gol temprano cierra una cuota interesante** (lo vio el usuario con su
     hermano, y él lo miraba hace tiempo): muchas veces una apuesta a buena
     cuota se resuelve TEMPRANO —el gol llega pronto y la deja encaminada o
     cerrada—, no por valor ni por rareza del mercado, sino como un patrón que
     se repite («funciona como que está amañado o tilt o como sea»). Acotar por
     ahí: medir con `fixture_eventos` (minuto del primer gol) y las cuotas
     prepartido y en vivo (`odds_history`, `odds_live`) en qué partidos y a qué
     cuota el primer gol cae antes del 15-20', y si eso se anticipa (tramo de
     cuota, liga, burbuja de goles, TDE). Aclarar con el usuario qué apuesta
     «se cierra» antes de diseñar el backtest. Se ANOTA, no se juzga
     integridad (deuda 14).
   - **Las constantes de goles ACOTAN, no adivinan el 1X2**: goles anotados y
     recibidos por condición (local del local × visita del visitante) dan un
     intervalo («mete 1 o 2») y un marcador acotado, que puede definir al
     ganador sin acertarlo siempre. Lo que se midió (§13.4: las K de goles no
     mejoran el 1X2; §15: la burbuja de goles no predice mejor que la
     frecuencia propia) NO es esta pregunta. Y el marcador no se repite tanto:
     un equipo que empata mucho empata con marcadores distintos. Backtest en
     `backend/backtest_goles.py` (REVENTON §17). **Medido el 30/10**: el cruce
     local × visita acota de verdad (−0,051 de log-loss), las constantes
     agregan poco (−0,002), el intervalo de dos goles acierta 64 % (promete 65 %)
     y el marcador acotado 41 %; contra el mercado de goles NO hay ventaja (el
     +17 % de «ambos marcan» era el artefacto de Marathonbet) y el marcador se
     repite lo que da el azar. **HECHO el mismo día**: `backend/analisis/goles.py`
     (las mismas variables que el backtest) da `golesAcotados` en `/burbujas`
     (tarjeta), en `lecturaSad` del parte (al leer) y en `objetivo` del
     veredicto, y Aprendizaje lo mide (`acreditables.golesAcotados`). El modelo
     calibrado se pega en `goles.MODELO_GOLES` desde `backtest_goles --padron
     --modelo` (pegado el 30/10: 50.823 partidos). **`sad-analysis` v4.3**
     (30/10, `docs/revisiones/SAD_v4.3_propuesta.md`, UN solo punto): el
     marcador declarado va dentro del acotado salvo un hecho de este partido, y
     entonces el falsador nombra la vía que lo saca (3.5, 6-C); el acotado no
     mueve el 1X2. NO integra las lecciones del 28-30/10: el botón «Cerrar las
     anteriores a v4.3» NO se pulsa para sad (esas lecciones esperan a la
     revisión siguiente). Subida a la cuenta el 30/10 a las 05:47 de Lima
     (`SUBIDA_VERSION`).

19. **Cuatro skills redactados el 01/11/2026** (usuario aprobó las propuestas
   de `docs/revisiones/`): **TDE v0.1.25** (el defecto del desenlace pasa a
   `abierto` con cualquier ISE de rama —el corte en 7 no separó: 39 % contra
   41 %—, `se_rompe`/`rescata` piden `porqueDesenlace`, la pelota parada va a
   `otra_via` (744); la app cobra los partes de la v0.1.24 con su regla,
   `veredicto.regimen_desenlace`), **sad-analysis v4.4** (sale la espina
   `neutra` —0 de 17—, entra `guia: pronostico`: sin lectura propia la espina
   sigue al 1X2; un depósito con `neutra` se rechaza; el favorito con el número
   del mercado), **DTP v1.7** y **EFE v1.9** + `efe-dashboard` v1.12.
   `CORTE_VERSION` con fecha 01/11. Lo que los skills marcan «pendiente de la
   app» está en `docs/revisiones/PENDIENTES.md`. Los cinco zips se
   subieron el 01/11 hacia las 08:00 de Lima (anotado en `SUBIDA_VERSION`, 1143;
   el tramo de las 04:47 de ese día corrió con la versión anterior).
   **Pendiente del usuario**: cerrar con 🔑 las anteriores de cada skill.

20. **Sesiones fijas que no engordan** (03/11/2026, usuario; el límite
   semanal se agotó el 02/11 y las rutinas quedaron paradas hasta las 20:00 de
   Lima). Una sesión fija relee su historial ENTERO en cada paso: la de
   veredictos llegó a 708 mil tokens en tres días (~14 USD por corrida solo en
   releer), la de partes a 389 mil y 2.715 USD acumulados, y rehacer gastaba
   ~0,30 USD por cada uno de sus 71 disparos diarios vacíos. Se rotaron las
   cuatro el 03/11 y desde entonces una rutina de esta sesión de trabajo
   («SAD · rotar sesiones fijas de las rutinas (v4)», `trig_01B32EgEm2JFkY4qm2sf5gGz`,
   03:17 de Lima TODOS los días, en su PROPIA sesión fija
   `session_01WwsfbSgbhYqpciGfAgwWzK` desde el 08/11 —la v3,
   `trig_018m2iN31i2MzFrwmd4HaZse` en `session_01WwsfbVj9a5d89k8KamHAGw`, quedó
   desactivada al rotarse a sí misma; la v2,
   `trig_015FqQ7fuvPtKmJfqmB1aL1E` en `session_01WwsfbVU6T15uLMLwCcCFfe`, quedó
   desactivada al pasar de 228 mil; antes disparaba en la conversación de
   trabajo, ya cerrada: `trig_0156fv2ZZpxW5z1rgo3pbeXN` desactivada—; la
   medición de `rolesVsGrid` del 05/11 (`trig_01Hvq4UW8N1xCCLSXDwDkhHF`) ya
   corrió: 9 reales y 0 falsos, propuesta en la incidencia 1232) rota la que pase de 150 mil tokens. Medido en
   la primera noche: una sesión nueva arranca en ~90 mil tokens (sistema,
   herramientas, CLAUDE.md); rehacer suma ~3.500 por disparo vacío (~250 mil
   por día) y cada disparo vacío costó ~0,10 USD con la sesión chica (antes
   ~0,30); una pasada de mantenimiento suma ~200 mil y costó 40 USD. **Sesiones y rutinas vigentes** (08/11 03:17 de Lima: rotadas las cuatro —partes
   598 mil, veredictos 369 mil, mantenimiento 370 mil y rehacer 660 mil—; 09/11
   20:16 de Lima: rotada rehacer, 199 mil —la v10
   `session_01WwsfbW3rDrNNPSRQRreSo9`—, y quedaron sin rotar por estar
   corriendo partes 522 mil, veredictos 253 mil y mantenimiento 324 mil; las
   reemplazadas quedan desactivadas):
   - partes: `session_01WwsfbVjuUEGrhsxEn3ZSTR` · 04:47
     `trig_016UweWHSiQBgaQWyfFWgJ3L`, 09:52 `trig_01S9eerQzGVgcfaVXmHQpmJ7`,
     14:56 `trig_01AgoQStdaf7VUcheZFq7def`;
   - veredictos: `session_01WwsfbWfsf7Lgu4mFUDSe6a` · 20:12
     `trig_017RyR1c82XWvEeoVBXj7YEx`;
   - mantenimiento: `session_01WwsfbWSj8bE9Vik4tFfKRS` · 12:23
     `trig_01Sz53iURZvTRDESSAfeeTCd`, 17:41 `trig_01B1whXaR3kdDdgdxWQH3cHu`,
     21:47 `trig_0137AUDgyroagZVXkPMAeAWR`;
   - rehacer (v11, desde el 09/11): `session_01WwsfbT6DGRqbnucNnMpzNm` · :02
     `trig_015zPxoMQ983jhfQPAupZ7Th`, :12 `trig_01GC4xcgtmRQD76f7M3uPc18`,
     :22 `trig_01XSx1Cnqt1opXNgMSr8X4od`, :42 `trig_01QMUAih5QATCw7njnXjboqq`.
   Medido el 03/11 con las sesiones nuevas: partes 117 USD (8 partes en el tramo
   3), veredictos 50 USD (18 veredictos), mantenimiento 29 USD por pasada,
   rehacer 41 USD en el día (hubo rehaceres reales). Las rutinas viejas quedaron desactivadas, no borradas. **Probado el mismo
   día**: una rutina con sesión NUEVA por disparo sigue arrancando sin el repo
   (en `/home/user`, sin `git`) y con otro modelo; las credenciales sí están.
   Sirve solo para un `curl`, y aun así cuesta más que una sesión fija chica
   (escribe en caché el prompt de sistema cada vez): no se usa. Y `CLAUDE.md`
   pasó de 27 mil a 12 mil tokens (esta deuda vive acá desde ese día), porque
   se carga en cada paso de cada agente. Pendientes del mismo estudio, sin
   aprobar todavía: separar el núcleo de cada skill de su historial (el TDE
   lleva 24 mil tokens de registro de cambios) y traer los insumos de un parte
   en un solo paso.

21. **Pendientes al cerrar la conversación del 03/11/2026** (se retoman en
   una conversación nueva: esta llegó a 545 mil tokens y cada paso la releía).
   - **Punto 3 del ahorro, propuesta lista para decidir**:
     `docs/revisiones/NUCLEO_SKILLS_propuesta.md`. Pasar el registro de cambios
     de cada skill a `references/HISTORIAL.md` baja lo que carga cada
     subagente de partes de 142,8 mil a 106,7 mil tokens (−25 %, ~0,65 USD por
     parte). Hay **13 reglas que hoy viven SOLO en un historial** (10 del TDE,
     entre ellas las disciplinas 34 a 39, que el núcleo cita; 1 del DTP; 2 de
     efe-dashboard) y se copian literales al núcleo antes de mover. **Dudas
     del usuario antes de aplicar**: (1) disciplina 35 del TDE («sin XI, F1 sin
     dato») contra la 55 («once probable = nivel C»): ¿cuál vale?; (2) ¿siguen
     vigentes la 34, la 37 y «no bajar P(gol) con ejecutor de penales» tras la
     suspensión del riesgo compuesto en v0.1.20?; (3) ¿`registro.csv` (16,5 mil
     tokens) se busca con Grep por equipo en vez de leerse entero en el PASO 0?;
     (4) ¿el FACTOR-X del suplente con impacto desde el banco entra también en
     la rúbrica del EFE?; (5) ¿el encargo dice si se carga efe-dashboard?
     Contradicciones que el traslado deja a la vista (sin corregir: serían
     cambios de reglas): LA TESIS del TDE todavía pide el riesgo compuesto, la
     tabla IE→probabilidad de INDICE_IE no dice que está suspendida, la rúbrica
     v1.9 se presenta como «EFE v1.7» y `docs/skills/README.md` dice TDE
     v0.1.22.
   - **Punto 4 del ahorro (sin empezar)**: los insumos de un parte en UN paso
     (`scripts/insumos_parte.sh <fixture>`) y una vista corta del parte para
     veredictos (el GET del parte pesa ~27 mil tokens).
   - **Palancas de volumen, para que decida el usuario** (medido 03/11, a
     precio de lista; el límite semanal ronda los 2.000 USD): los veredictos
     cuestan ~3,3 USD cada uno (45 por noche ≈ 50 % del límite) y una pasada
     de mantenimiento ~40 USD (tres por día ≈ 40 %). Opciones: mantenimiento en
     1-2 pasadas por día y/o tope de veredictos por noche en ~25.
   - **Verificar mañana**: el gasto de un día entero con las sesiones nuevas
     (`get_session` de las cuatro, `usage.cost_usd`) contra estos números, y
     que la rotación de las 03:17 haya corrido.
   - **Ya anotados en otros puntos y siguen**: medir `rolesVsGrid` (rutina del
     05/11, 646); cerrar con 🔑 las lecciones anteriores a las versiones
     subidas el 01/11 (TDE v0.1.25, sad v4.4, DTP v1.7, EFE v1.9); lo que los
     skills marcan «pendiente de la app» en `docs/revisiones/PENDIENTES.md`.

22. **El método de apuesta** (03/11/2026, usuario): el win rate es lo que se
   mejora y Kelly sobre nuestras probabilidades queda como alarma (con que no
   baje mucho alcanza), no como meta: la cuota la pone la casa. Investigado el
   mismo día sobre 374 partes (15/09-01/11) con remuestreo por días y con los
   resultados sorteados según el mercado (sin ventaja): el elegido es el
   **proporcional al 1 % con freno por tramo** (`docs/METODO_APUESTA.md`), en
   la simulación como serie `proporcional`. Martingala, Fibonacci y
   D'Alembert no agregan ventaja y sin ella quiebran la mitad de las veces o
   más. **Pendiente**: volver a medir con un mes sin huecos (los datos del
   domingo 01/11 desde las 17:00 al lunes 02/11 a las 12:00 se perdieron).

23. **El criterio de contacto de la martingala** (04/11/2026, usuario: «las
   gráficas son muy reveladoras… hay que medirlo cada fin de semana»). En
   nuestros partes, tras 3 fallos seguidos se acertó 20 de 30; en la base, no.
   Regla fija (100+ casos tras 3 fallos, 65 %+, intervalo sobre el promedio):
   `trasFallos` en la simulación y la rutina «SAD · criterio de contacto
   (semanal)» `trig_011ha3sLwm2qqjCpfpHLmFYx`, lunes 07:43 de Lima, en la sesión
   de trabajo `session_01WwsfbUajmjoAmjLG4pPY2i`. Si esa sesión se archiva, la
   rutina se rehace en otra con el repo. `docs/METODO_APUESTA.md`.

24. **La ley anticulebras del usuario, medida** (07/11/2026, usuario: «no
   pueden ser los siete locales… si no, cualquier pastrulo gana»; el empate
   de la U contra Sport Boys). `backend/backtest_culebra.py` (test:
   `test_backtest_culebra`): por LIGA-DÍA (misma liga, mismo día de Lima, 3+
   partidos), el partido siguiente según lo que ya terminó 2 h antes. Medido
   sobre 34.970 partidos de las ligas nacionales del padrón (2022-2026) y
   1.221 con cuota en 324 liga-días (jul-nov 2026): **sin culebra**. Tras
   locales ganadores el empate del siguiente NO sube (+0,7 · −1,1 · −1,9 pts
   con 1 · 2 · 3+ previos) y el local gana igual o algo más; los días con
   todos los locales ganando salen MÁS que la permutación (405 contra 376,
   z +1,9): los días van en racha. La combinada pierde por el margen cobrado
   una vez por partido, no por culebras. **Pistas abiertas, con pocos casos**
   (rehacer con más meses de cuotas: `--api` y `--cache`):
   - **Empate tras 2+ locales ganadores**: 1 u al empate con la cuota real dio
     ROI +5,9 % (n = 50; tras 1+, +0,8 % con n = 201) contra −12,3 % a ciegas.
     La frecuencia de empate en la muestra grande no sube: probablemente suerte.
   - **Favorito VISITANTE tras un día en que ganaron todos los favoritos**:
     ganó 39,7 % contra 46,6 % de su cuota (n = 68; con 2+ previos, 31,8 %
     contra 45,6 %, n = 22). Lo único con forma de culebra.
   - La **combinada de los favoritos más fuertes** del día (punto 16) sigue
     abierta.
   Falta medirla con NUESTROS elegidos (días en que los elegidos de una liga
   van todos al mismo lado): los datos de la simulación no están abiertos al
   token de Cowork; iría en `backend/analisis/simulacion.py`. Unas 30
   comparaciones: una o dos «significativas» son lo esperable por azar.

25. **La resaca del clásico, PISTA** (07/11/2026, usuario: «tras ganar el
   clásico iba con cuidado; el siguiente gana, el otro rompe»; Cristal le
   ganó a Alianza y empató 1-1 en Tarma con ADT). Medido el mismo día sobre
   35 mil partidos de las ligas nacionales del padrón (2023-2026; 2022 de
   calentamiento): fuerza Elo secuencial (solo partidos anteriores, K 20,
   localía 60) y lo esperado por liga y tramo de diferencia de Elo; el
   ganador en su partido siguiente y subsiguiente (≤ 14 días por paso).
   Clásicos: `calendario.clasico_documentado` + `clasico_nacional` + derbis
   de ciudad puestos a mano para la prueba (Manchester, Merseyside, Milán,
   Roma, Madrid, Rosario, Avellaneda…): 417 en 69 rivalidades. **En todas
   las ligas, no hay resaca**: tras ganar un clásico el siguiente sale +3,3 ±
   4,5 pts sobre lo esperado y el subsiguiente +1,0 ± 4,7; grande le gana a
   grande (ambos Elo 1600+), +3,3 y −1,4. Por país, mitad y mitad. **La
   pista**: en el SUBSIGUIENTE, las grandes ligas europeas van todas abajo
   —Inglaterra −8 (n 34), Turquía −16 (24), España −7 (20), Portugal −8
   (13), Italia −3 (21)—, juntas unos −9 ± 9; y grande le gana a grande,
   Italia −16, Turquía −28, Alemania −12. Encontrada MIRANDO la tabla
   (selección después de ver; ~70 comparaciones, 5 cruzan su margen, 3 hacia
   arriba). Brasil, Grecia, Colombia y Paraguay van al revés. **Regla fija
   para medirla** sin volver a elegir el grupo: desde el 08/11/2026, los
   clásicos ganados en Inglaterra, España, Italia, Portugal y Turquía; el
   subsiguiente partido de liga del ganador contra lo esperado por Elo (o por
   la cuota sin margen, cuando haya). Se toma en serio si con 60+ casos nuevos
   sigue por debajo con el intervalo entero bajo cero. Aparte, sin clásico:
   tras CUALQUIER victoria el siguiente rinde −2,7 ± 3,0 en Perú y −2,3 ±
   3,4 en Bolivia; es la altura (una sola localía por liga subestima la de
   Tarma o La Paz), no una resaca, y el mercado ya la paga.

26. **Burbuja inflada contra burbuja construida, CONTRA LA CASA** (08/11/2026,
   usuario: «si el Real Madrid le gana por accidente al PSG, en el siguiente
   grande se va a la mierda»). Fuente nueva: **football-data.co.uk** (CSV
   públicos, cuota de CIERRE de Pinnacle y promedio de casas), 62.320
   partidos 2012-2026 de Inglaterra, España, Italia, Alemania, Francia,
   Países Bajos, Portugal, Bélgica, Grecia, Turquía, Argentina, Brasil y
   México; sin Perú, Colombia ni Chile. Cada señal partida en 2012-18 y
   2019-26: lo real sale en las DOS mitades. Resultado:
   - **Muerto con esta muestra**: la anticulebra por liga-día (empate tras
     favoritos ganadores +0,6 · +0,9 · +0,1 pts con 1 · 2 · 3+ previos, las
     mitades no coinciden), los partidos a la MISMA hora (todos los favoritos:
     154 de 1.687 tandas contra 146,5 esperados) y el amaño contra el grande
     (los favoritos ganan +0,8 sobre su cuota en los 62 mil).
   - **Señal 1, el batacazo** (burbuja INFLADA por un golpe): el que ganó con
     ≤ 25 % rinde bajo su cuota en el siguiente (−1,4 ± 1,2; mitades −1,0 y
     −1,8) y el subsiguiente (−2,1 ± 1,2; −2,1 y −2,0), y contra rival fuerte
     −2,6 ± 1,6. La casa lo sobrevalora.
   - **Señal 2, el invicto largo** (burbuja CONSTRUIDA): 10+ sin perder gana
     +1,8 ± 1,3 sobre su cuota y 15+ +2,6 ± 2,1, las dos mitades igual. La
     casa lo subestima.
   - Ninguna gana sola al margen del promedio de casas (−1 a −8 %); con
     Pinnacle quedan en cero. Casi todo es Europa (Américas: pocos casos, no
     se ve). Son AJUSTES de confianza dentro del método, no apuestas.
   **Medido en NUESTRAS elecciones el mismo día** (269 cerradas desde el 28/10,
   historia del elegido por `/fixtures?equipoId` y la cuota del partido previo
   por `/cuotas`): todas +8,9 ± 5,8 sobre la cuota; elegido tras batacazo
   +10,5 ± 25,5 (n = 14); invicto 5+ +21,0 ± 13,7 (n = 46), 10+ +10,5 ± 25,5
   (n = 13), 15+ n = 3. Sin muestra para decidir. **Pendiente**: rehacerlo con
   100+ apuestas por grupo; si el batacazo resta y el invicto suma sobre
   NUESTRO acierto, avisos en el parte (como K-EXTREMO) que muevan la
   confianza, no el 1X2. Los scripts de esta medición no quedaron en el repo:
   el método es este texto.

27. **Aprendizaje y Simulación rápidos, cuarentena en un paso** (09-10/11/2026,
   usuario: «la sección Aprendizaje carga mucho y es bien lenta, igual
   Simulación. Poner algo en cuarentena es un dolor de huevos»). Ningún número
   cambió: cada cambio se probó contra la salida de antes byte a byte y queda
   `backend/test_velocidad.py` en CI.
   - **Dónde se iba el tiempo**: el 95 % del inventario era rehacer el
     objetivo de cada veredicto (~1 s por caso en producción), que vencía a los
     10 minutos aunque nada hubiera cambiado, y otra vez tras cada deploy. La
     historia del mismo equipo a la misma fecha se pedía tres veces por caso.
   - **PR #453**: el objetivo se guarda con la HUELLA de sus insumos (parte,
     fila del partido + eventos + alineación, derivadas; si el pipeline las
     reescribió, una firma estrecha de la historia de los dos equipos hasta ese
     día decide si el caso cambió); `historias_compartidas()` dentro de cada
     caso; hilo `calentar-aprendizaje` (`SAD_CALENTAR_S`, 300 s). **PR #456**:
     un candado por clave (una cohorte lista esperaba detrás del buscador) y el
     buscador (límite 2000) también caliente.
   - **PR #454**: `cuotas_mercado` pide a SQL solo 1X2 y doble oportunidad (era
     el 85 % de la simulación) y `simulacion()` se rehace solo si cambia su
     huella (partes desde el 28/10, partidos con su liga, cuotas).
   - **Medido** (token de Cowork; `/analisis/simulacion` no se abre a ese
     token, así que Simulación se midió en un banco local con volumen de
     producción). Aprendizaje, `resumen=true` en frío: ANTES 502 a los 300 s y
     115 s al reintentar; DESPUÉS 71 s una vez tras el deploy (lo calcula el
     hilo en el fondo) y 3,5-3,9 s con veredictos entrando; el buscador pasó de
     60 s (esperando el candado) a lo que dice la medición de #456 abajo.
     Banco local: visita a los 31 min 3,5 s → 0,2 s; pipeline sin cambios de
     historia 3,5 s → 0,3 s. Simulación (banco): 180-236 ms → 24 ms desde la
     segunda lectura.
   - **PR #455, la cuarentena en un paso**: la incidencia trae
     `propuestaCuarentena` (declarada por el mantenimiento en `POST …/estado`
     con `cuarentena: {fixtures, motivo, ensena}`, o leída del texto de las
     propuestas viejas: la 7, la 774 y la 1153 salen bien); la tarjeta
     Decisiones pendientes la pone con un botón (formulario ya escrito,
     editable) y la incidencia queda `resuelta` (`hecha: true` en
     `…/decision`); en Aprendizaje, «Buscar caso · cuarentena» la pone por
     partido sin abrir una lección. La regla no cambió: por criterio, motivo
     de 12+ y llave maestra. El skill `corrida-sad` dice cómo mandarla.
   - **Pendiente**: tras cada deploy el primer cálculo sigue costando ~1 min de
     CPU en el fondo (el caché vive en memoria; guardarlo en disco exige saber
     qué código lo produjo, y casi todo PR toca `app.py` o `parte.py`).

## Siguientes pasos (en orden)

1. **Desplegar**: Railway (backend + volumen + ingesta programada) y Vercel
   (frontend) — guía paso a paso en `docs/DESPLIEGUE.md`.
2. **Familias nuevas de burbujas** — spec completa en `docs/ROADMAP_BURBUJAS.md`:
   `k_dc`, márgenes (±1/2/3+ goles) y k_cuota_* sobre cuotas prepartido (1X2 y
   doble oportunidad, con su regla de huecos) hechos, y `favorito`/`tapado`
   (24/09, derivados al leer en `/constantes-cuota` con el nivel del rival;
   botón «Favorito» en `ControlesCuotas`). La familia está completa.
3. **xG/posesión desde estadísticas por partido**: HECHO (24/09).
   `/equipos/{id}/stats` promedia xG (a favor y en contra), posesión, tiros a
   puerta y córners de `fixture_stats` (`ficha_tactica.promedios_avanzados`,
   últimos 10 terminados con ficha) y cada promedio viaja con su muestra en
   `avanzadas.n`: la ingesta de fichas solo cubre los últimos partidos de
   equipos con un NS próximo, y un null de la API es «sin dato», no cero. Se
   ve en Estadísticas (comparativa) y en Equipo (Temporada). El gap §5 NO
   los usa: la matemática del motor no se tocó.
4. **Historial de cuotas por fixture**: HECHO (fases 1-3 de
   `docs/EXTRACCION_TIEMPO_REAL.md`). `odds_history` con 3 fotos al día +
   refresco de las últimas 6 h (`SAD_REFRESCO_MIN`) y `odds_live` en juego;
   `GET /cuotas/{id}/historial` dibuja la curva real en Cuotas (apertura →
   pitazo, y el tramo en vivo con su escala), solo con ≥ 2 capturas por
   selección: con menos, la pantalla lo dice y muestra la cuota actual a
   secas. Retención: `SAD_ODDS_HISTORY_DIAS` (90) y `odds_live` por fixture.
   Qué ligas dan cuotas en vivo (fase 3, decisión 1): `diag_vivo
   --cobertura` lo mide contra los partidos jugados. **24/09** (21 días, 30
   ligas): ninguna en cero; Liga MX en 4 % (1 de 25, 46 rondas vacías
   seguidas) es la única sospechosa; el resto entre 40 y 100 %.
5. **DTP** (Diagnóstico Táctico de Partido) — diseño en
   `docs/efe-dtp/DTP_DISENO.md`. **Fases A y B hechas**: ficha de partido
   (alineaciones con `grid`→carriles, eventos con asistente y stats en
   `/fixtures/{id}/ficha.tactica`) y motor (`POST /analisis/dtp` por equipo
   foco, cadena rodante en `cadena_dtp`, `GET /equipos/{id}/cadena`). Queda la
   fase C **también hecha**: pizarra en la sección Análisis (toggle de equipo
   foco) y cadena en la página de Equipo. **Grid medido (24/09)**: 63 % de
   los onces trae el grid completo (carriles reales); sin grid —Primera
   Nacional de Argentina, Liga de Expansión MX, Segunda de Perú, las Primera
   B, Copa del Rey— el XI viaja con `sinCarriles`: la posición da la línea,
   no el lado, y M2 va por línea o con fuente externa citada. xG en el 48 %
   de las fichas con stats.
6. **Bucle de aprendizaje** — `docs/APRENDIZAJE.md`. **Fase B hecha**: el
   veredicto a las 12 h (`POST /analisis/cowork/{id}/veredicto`,
   `backend/analisis/veredicto.py`). Lo objetivo lo calcula el backend
   —marcador, acierto del 1X2, Brier de tres resultados, si cayó gol en la
   ventana del TDE, los goles con su minuto, y el **reventón** de cada lado:
   la burbuja declarada antes del partido (vista «al día del partido») y si
   ese partido la reventó, como observación sin acierto ni fallo— y se
   RECALCULA al leer; Cowork
   solo escribe el juicio y, sobre todo, la POBLACIÓN del caso (`ciega` /
   `por_resultado` / `post_resultado`), que no se puede deducir y que decide
   si acredita. Solo `ciega` + `PRE` acredita: los contaminados fijan rúbrica
   pero NO acreditan, y ninguna métrica puede mezclarlos. Sin pronóstico
   previo la cadena no recibe veredicto, y re-depositar el parte no pisa el
   pronóstico declarado ni borra el veredicto escrito. **Fase C hecha**: las
   lecciones acumuladas por skill (`backend/analisis/lecciones.py`,
   `GET /analisis/cowork/lecciones`, sección **Aprendizaje**). El CONTENIDO de
   cada lección se DERIVA del veredicto al leer —no hay copia que se quede
   vieja cuando alguien corrige un caso—; aparte solo se guarda el ESTADO
   (`leccion_estado`), que es lo que corta el bucle infinito. Marcar `aplicada`
   EXIGE la versión del skill donde entró; cada lección viaja con
   `puedeMoverNumeros` (solo `ciega`+`PRE` sostiene un cambio de peso, el resto
   fija rúbrica); el sesgo de atribución se declara antes de los conteos; la
   tasa de reventón por nivel de riesgo se compara con la del backtest
   (`acreditables.reventon`, `TASA_BACKTEST` en `burbuja.py`, solo con n ≥ 10
   por nivel) y un nivel fuera del rango ABRE la revisión de los puntos sin
   moverlos (`docs/REVENTON.md` §11); **¿el 1X2 respetó la burbuja?** —por
   lado, `pronosticoVsRacha` (aFavor · enContra · neutro: si el 1X2 declarado
   apostó a que la racha sigue o se corta) y `respetoRiesgo` (SOLO con riesgo
   alto/muy alto; `null` es «no aplica», nunca un fallo), calculados en
   `veredicto.pronostico_vs_racha`; las lecciones cruzan cada grupo con su
   1X2 y su Brier (`acreditables.reventon.respetoRiesgo`): un Brier peor en
   «a favor» es la evidencia de que el riesgo vale para el pronóstico—; y
   mover estados NO está abierto al token de Cowork: el agente lee sus
   lecciones, declarar aplicada la suya es del usuario. **Cuarentena y
   cohortes** (C-bis, hechas): la cuarentena es POR CRITERIO y NUNCA POR
   RESULTADO (motivo obligatorio, `veredictoAlPoner` como evidencia, token
   maestro), saca el caso de toda métrica; la cohorte se sella AL DEPOSITAR
   (`parte.COHORTE`, lo anterior es `rodaje`), un re-depósito no la cambia,
   y las métricas se leen por cohorte (`?cohorte=vigente`, la vista por
   defecto). El reventón por nivel se compara con el backtest por INTERVALO
   (Wilson 95 %), no por el punto. **Fase D hecha**: el dossier
   (`lecciones.revision`, `GET /analisis/cowork/revision/{skill}`, botón «Ver
   dossier»): lecciones abiertas por regla, acreditables vs. solo rúbrica,
   métricas ciegas del skill contra su listón, versión vigente del snapshot y
   una lectura calculada de lo que la revisión puede concluir; `POST …/abrir`
   (maestro) las pasa a `en_revision`. **Fase A hecha**: los antecedentes
   (`backend/analisis/antecedentes.py`, `GET /analisis/cowork/antecedentes/{id}`):
   por equipo, lo dicho en partidos ANTERIORES y cómo salió, acierto a ciegas
   y lecciones abiertas; Cowork los lee antes de investigar y el caso nuevo
   sigue siendo ciego. La app nunca mueve un peso de un skill por su cuenta.
   Snapshot de los skills en `docs/skills/`.
7. Fase nube completa cuando toque: `docs/SERVICIOS_EXTERNOS.md` (Postgres).
