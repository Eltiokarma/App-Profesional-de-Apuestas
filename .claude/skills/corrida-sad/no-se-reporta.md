<!-- La lista «No se reporta»: lo decidido que se cierra siempre igual. La lee quien va a depositar incidencias (incidencias.md) y el mantenimiento cuando la amplía (paso 7-bis). -->

# No se reporta

- **No se reporta** (lo decidido; el mantenimiento suma acá lo que se cierra
  siempre igual, 31/10/2026): una liga que no publica onces (`nuncaVaALlegar`,
  deuda 5 de `docs/DEUDA.md`); un amistoso o una copa de categorías bajas sin
  ficha; un 502 pasajero del servidor durante un despliegue. Y desde la pasada
  del 31/10 (noche), cerradas siempre con la misma causa conocida: el `desde`
  de /coachs que es el mes de la carrera (482, 949: `desdeConfirmar` ya lo
  marca y la prensa manda); el gol o la tarjeta que la API acredita a otro
  jugador o equipo (642, 896, 910: el marcador manda); el /coachs atrasado con
  el DT que se fue (766, 880, 903: DT-DISCREPANCIA ya avisa); la sede o la
  fecha que la API no actualizó (814, 871, 882, 902); la sanción «probable»
  que la prensa corrige (877, 921: el detalle ya dice «confirmar en prensa»);
  y los campos que viajan en otro lugar del GET (`calculado.sinS`,
  `otrasFamilias.perfilDc`, `calculado.contraElOnce`: 678, 900, 944) —leé el
  contrato antes de reportar un campo ausente. Y desde la pasada del 31/10
  (mediodía): la roja que vale más de una fecha o el ciclo de amarillas con
  `conteoParcial` (993, 1007, 1012: la base solo infiere el partido siguiente
  y lo dice; la prensa manda); «sin ejecutor de penales» con menos de
  `PENALES_MUESTRA_MIN` partidos con eventos (995: la nota ya manda a la
  prensa; pasa en las ligas recién sumadas); el hándicap asiático −0,5 con la
  misma cuota que el 1 del 1X2 (1009: son la misma apuesta); el titular
  habitual contado sobre los onces en que estaba disponible (1013, 398/509);
  y un `contraElOnce` de ANTES de un rehacer: el rehacer pisa la apertura, así
  que reportá con el `xiReferencia` y la `senalXi` originales copiados en el
  detalle, o no se puede verificar (1021; la PRIMERA apertura queda en
  `GET /equipos/{id}/cadena`, que es contra la que el mantenimiento reproduce). Y desde la pasada del 31/10
  (tarde): el nombre del DT de /coachs en otro orden («Dario Insua Ruben»,
  1033: la comparación del DT no depende del orden); la primera captura del
  once sin formación, sin grid o con 10 titulares (1045, 988: el refresco a
  40 min la corrige si la API la publica); el orden de /constantes, que va del
  más nuevo al más viejo (1044, 782); la `zona` de la tabla F1, que es la de
  los onces recientes y no la del último grid (1042); y dos filas F1 con el
  mismo nombre que compartieron una hoja: son dos personas (1039). Y desde la
  pasada del 01/11 (noche): DTP-REHACER `tardio` con el once ya en el último
  depósito y la formación corregida DESPUÉS del pitazo (1053, 848: el detalle
  lo dice); la salida «pelota parada» del TDE (1058, 744: espera la v0.1.25);
  el bloque F cerrado con la ficha después del partido (1061: lo sellado
  antes del pitazo no se toca); la etiqueta `lectura_efe` (hoy `lectura`, 17/11/2026) del modo de fallo
  de Jev (1062, 794: insumo de la fase D, no juez); y un once que la API
  publica con 10 titulares (1060, 1045). Y desde la pasada del 02/11 (noche):
  el ONCE-SIN-FILA-F1 de un debut o recambio fuera de los últimos 3 onces
  (1069, 1118: con el once capturado la F1 ya lo suma como `delOnceOficial`, #1068); el once que la API publica
  después del pitazo (1072, 1081, 1145: la cola ya prioriza los partidos con
  parte); las capturas de «ambos marcan» anteriores al 27/10 (776, 1099); el
  límite del plan de Claude (1132: el latido ya lo pone en ámbar); y el «sin
  penales» o «sin otro ejecutor» con muestra corta o plantilla incompleta
  (1064, 1085, 1089, 1097). Y desde la pasada del 03/11 (mediodía): el
  ejecutor de penales que se fue del club y sigue en la lista con
  `enPlantilla: false` (718, 1154: va al final, la nota dice «ya no están en
  el plantel» y no cuenta como ejecutor vivo); el DT que vuelve al club y
  /coachs no registra la segunda etapa (1152: es el `desde` de la carrera,
  482/949, y /burbujas ya dice «aproximado: confirmar en prensa»); el
  sancionado por ciclo de amarillas que aparece en la hoja oficial (1156: la
  hoja manda y la F1 ya dice `cicloAmarillas: enLaHoja`); y la grafía rota del
  DT en la ficha que `identidad.mismo_dt` casa («S. Hoeneb» por Hoeneß, 1158:
  si no suena DT-VS-BANCO, el cruce ya la absorbió). Y desde la pasada del
  03/11 (tarde): el titular que la `senalXi` ANUNCIA y contraElOnce no cuenta
  como nuevo (1162: anunciado es referencia); la pieza del M2 —propia o
  rival— que pide rehacer aunque M1 y los duelos ya estén reescritos (1161,
  1163: DTP v1.5, el motivo dice «pieza del M2»); los titulares que la F1 trae
  con `fueraDePlantilla: true` (1167: la plantilla de la API no los tiene y la
  tabla los suma desde los onces); el ejecutor de penales con un id distinto
  del de su fila F1 (1168: dos ids de la API); y la fila F1 con nombre que no
  es el de su id, que el recibo ya avisa en `faltan` (1160, 938). Y desde la
  pasada del 03/11 (noche): el `desde` del DT vacío con fuente alineación
  (1184: a propósito, la prensa lo llena); ESPINA-SIGUE-EN-EXTREMO callada
  porque el `porque` nombra el extremo (1185, 874: la regla pide decirlo);
  el mismo jugador con dos ids o dos nombres entre la hoja, los eventos y la
  plantilla (1174, 1186, 1191: la app casa por id); la ficha de Venezuela o
  de la copa de Bolivia sin alineaciones, estadísticas o tarjetas (1176,
  1183, 1192); y la formación 4-1-4-1 contra 4-2-3-1 que no pide rehacer
  (1181: misma línea de atrás y un solo punta). Y desde la pasada del 04/11
  (mediodía): el lesionado largo o el que no sumó minutos y que la plantilla
  de la API no lista (1195: va en `fuera` sin `jugadorId`, el bloque F casa
  por nombre; la F1 lo suma recién con el once oficial, #1068); y el cierre del
  DTP contra un partido anterior al último, que viaja en
  `aperturaPrevia.cierreContra` de `GET /analisis/cowork/dtp/{id}` (1196: leé
  esa clave antes de reportarlo ausente). Y desde la pasada del 04/11
  (tarde): el id de la API que comparten dos jugadores de clubes distintos y
  saca a uno en `jueganEnOtroEquipo` (1208, misma clase que la 961: se carga
  sin `jugadorId`); el lateral con el carril cruzado en el grid de la ficha
  (1205, 987: es la columna que publicó la API); y 4-1-4-1 contra 4-2-3-1 sin
  rehacer (1203, ya decidido en la 1181). Y desde la pasada del 05/11
  (tarde): el `desde` del DT por el primer banco visto que la prensa adelanta
  (786, 1234: `_llegada_vista` solo lo da por confirmado si la hoja anterior
  trae a OTRO DT; si la API dejó al saliente en esa hoja, la prensa manda);
  el evento del tiempo añadido que la API guarda con el minuto ya sumado
  (1082, 1216: la ventana se ancla al reloj del gol); y la ficha de un partido
  con las estadísticas vacías (12 casos, todos `dato_api`: la API no las
  publica para esa liga). Y desde la pasada del 06/11 (mediodía): la etiqueta
  EN_CRISIS de un equipo que gana (1252: el criterio G2 es «3 derrotas
  seguidas O DT nuevo en 4 semanas», `calendario.CRISIS_DT_DIAS`, y viaja con
  su `dato`); el titular de la temporada que no fue titular en los últimos 10
  onces y no está en la F1 (1253, 809: el probable de la prensa lo suma con su
  `jugadorId`); y una liga sin regla de amarillas en `sanciones.UMBRALES`
  (1254, 1373: decidido con la #1067, PR #475 —una competición entra a
  `UMBRALES` solo con su reglamento—; la prensa manda). Y desde la
  pasada del 06/11 (tarde): el rehacer que no rehízo el EFE, el B6 del arquero
  nuevo ni la tabla F1 (1257, 1265: el paso 4 del modo `rehacer` los deja como
  estaban; el veredicto lo lee); el once que la API publica a minutos del
  pitazo (1264, familia de la 1072); y la sanción que la prensa dio y la base
  no (1263: si `f1/{id}` no la tiene en `sancionados` ni en `baja`, la fuente
  fue la prensa y la hoja manda). Y desde la pasada del 07/11 (noche): el
  banco de la API con el DT que se fue y que la prensa desmiente (1268, 1153:
  DT-VS-BANCO ya avisa; se corrige con la llave en `bancoDesmentido`); las
  tarjetas de las ESTADÍSTICAS de la ficha que no cuadran con los eventos
  (1274: nada las lee, manda `fixture_eventos`); y la fila F1 del parte sin
  `jugadorId` que no casa con un apodo de la hoja (1272, 1242: copiá el id de
  `f1/{id}`, es el cruce exacto). Y desde la pasada del 07/11 (mediodía): la
  lesión de esta semana que la API no lista o deja «Questionable» (1279:
  `jugador_bajas` es lo que da /injuries, la prensa del parte manda); una
  burbuja de otras familias larga y sin `cuidado` cuando su estado es banal
  (90 %+) o tiene menos de 3 burbujas previas (`record: null`; 1289, 834); la
  plantilla de `/equipos/{id}/plantilla` más corta que la F1 (1291, 1167: es
  la de la API, la F1 suma los onces); y la `linea` o el `caso` de
  `casosBloque` con nombres de otro partido (1293: es prosa del cierre que lo
  escribió, la `fecha` es la calculada). Y desde la pasada del 07/11
  (tarde): DT-DISCREPANCIA que sigue sonando con `dt.banco` declarado con
  fuente (1296, 1302: DT-VS-BANCO se apaga a propósito, 1103; la que queda
  avisa de /coachs atrasado, 766/880/903); la hoja de la API sin entrenador
  (1301: sin nombre no hay cruce, se declara `dt.banco` si hace falta); el F2
  del TDE en 1 con 3 días de descanso o menos (1300: es el tramo alto de la
  rúbrica, moverlo es revisión del TDE); y una «posible identidad» entre dos
  nombres sin efecto en el parte (1303): corré
  `identidad.mismo_jugador(a, b)` antes; si da False son dos personas y la
  app los trata así. Y desde la pasada del 07/11 (noche): la «Red Card»
  después de una amarilla sin el detalle «Second Yellow card» (1309: puede ser
  directa, el detalle ya pide confirmar en prensa); el `5-3-2` del `xi` con un
  `capturadoEn` anterior a la formación (1315: `formacionAlCerrar` vacío dice
  que la formación llegó en un refresco); el mismo jugador con dos registros de
  la API y nombres distintos («M. Ubandoma» / «M. Isah», 1314: sin nombre ni id
  común no hay regla); 5-4-1 contra 3-4-1-2 o 3-5-2 contra 3-4-2-1 sin rehacer
  (1311: misma línea de tres con carrileros, 734/1240); y un DTP-REHACER
  `sinRehacer` con el once a tiempo sin más dato (1305, 1270, 1401: la #1052
  se cerró rotando la sesión; reportalo SOLO con la respuesta de `/rehacer` del
  disparo que no lo trajo o el GET del parte antes del pitazo, que es lo único
  que deja ver la causa). Y desde la pasada del 08/11 (mediodía): el F2 o los
  `diasDescanso` «un día corto» (1322: son días ENTEROS por las horas entre
  saques, 769); `cierreContra` null del lado cuya apertura previa ES el último
  partido (1319, 1196: solo viaja cuando no lo es); la roja UEFA `senal` en
  `/equipos/{id}/plantilla` y `ruido` en `f1/{id}` (1327: la plantilla no sabe
  de qué partido se trata, 1178/1193); el `rolSugerido` del arquero sobre
  todos los onces y el de campo sobre los onces en que estaba en la hoja
  (1334, 879 y 398/509); RECIÉN ASCENDIDO durante toda la primera temporada
  (1335: se verifica con `/ligas/{id}/standings?temporada=<anterior>`); un
  falso positivo de COHERENCIA-* que se arregla reescribiendo la prosa (1336:
  Jev no es determinista y el revisor lo cuenta); y el titular de la temporada
  sin fila porque no jugó los últimos 10 onces (1318, 1253: el probable de la
  prensa lo suma con su `jugadorId`). Y desde la pasada del 08/11 (tarde): la
  tabla de un torneo corto que «no sale» con la temporada del año (1340: la
  temporada es la de la API; en la Liga MX el Clausura 2026 es la temporada
  2025: pedila con `temporada=<año−1>&fase=Clausura`); 4-1-4-1 contra
  4-2-3-1 que no suena DTP-REHACER aunque el otro lado sí haya sonado y falte
  un titular de la referencia (1342, 1343: el umbral es 3 ausentes, 1181); el
  titular de la hoja sin `jugadorId` (1354: lo publica así la API, el bloque F
  lo casa por nombre); el evento VAR «Penalty confirmed» que no terminó en
  penal (1355: es el evento de la API, se cobran el marcador y los goles); y ONCE-SIN-FILA-F1
  con 1, 2 o 3 titulares que el rehacer no rehízo en la F1 (1339: sumalo a la
  #1068, que espera la decisión; 1265). Y desde la pasada del 10/11
  (mediodía): la sede de la ficha con el local nominal que juega en la cancha
  del visitante (1361, 832, 814: la API no publica el traslado; la sede real va
  en el parte); la cuota extrema o sin línea visible del mercado de goles en un
  cruce de categorías muy distintas (1363, 831: llega así de la casa); el IE
  null cuando falta el F2 del motor (1358, 433: Disciplina 21, el ISE sale
  igual); y el equipo de categoría no ingestada sin plantilla ni calendario en
  una copa (1356, 1147: desde el 10/11 el descanso, el P1a y la cancha neutral
  de ese equipo ya salen «sin dato», #1357/#1366/#1360). La ONCE-SIN-FILA-F1
  de un titular del once oficial ya no va a la #1068: desde el 10/11 la F1 lo
  suma como `delOnceOficial` (PR #487); en un parte depositado ANTES del once
  sigue sonando hasta el rehacer (por diseño), pero si suena en uno depositado
  con el once ya capturado, es código otra vez. Y desde la pasada del 11/11
  (mediodía): la apertura del DTP sin XI que un segundo depósito «sin dato:
  no hay once» no reemplaza (1365, 617/581: solo la pisa UNA vez una apertura
  CON XI, decisión del usuario del 25/10, PR #236); el reventón del veredicto
  que se cobra sobre la familia TOTAL aunque la de la condición haya cortado
  (1375: manda la total, REVENTON §13; la de la condición viaja como dato);
  y el partido de un homónimo de otro país en la base de un equipo de interés
  (1371, 1378: `backend/partido_ajeno.py` ya lo saca de la historia, el nivel y
  el calendario; el escaneo lo marca a propósito). Y desde la pasada del 11/11
  (noche): el parte de una copa sin alineaciones que queda en `pendiente_xi`
  al cerrar el veredicto (1380, 941: con la ficha sellada sin once va a
  `nuncaVaALlegar` mientras no hay veredicto; después ese estado es la
  constancia de que el bloque F no cerró). Y desde la pasada del 14/11
  (mediodía): la prosa de `documentos[]` que un rehacer tomado a menos de
  20 min del pitazo no alcanzó a reescribir con el rol del que entró (1407,
  1219: la regla está en el paso 4 de `modos/rehacer.md` y no hay código
  que arreglar; si no llegás, decí en `notas` del parte qué prosa quedó con
  el once viejo, así el veredicto no la lee como análisis); y la tabla de posiciones sin los puntos que
  quitó un fallo administrativo (1405, 694: la tabla se calcula de los
  resultados de la base y no tiene fuente para una deducción; el dato de la
  prensa va en `notas` del parte).
  Y desde la pasada del 14/11 (tarde): el `aperturaNoGuardada` del recibo de
  un rehacer con una apertura con XI ya en la cadena (1409, 749: manda la
  primera; el DTP del parte sí se rehízo); «X y Y desde el banco» con X
  titular, que suena FUERA-EN-LA-HOJA (1410: por el texto no se distingue de
  los dos en el banco; escribí cada uno con su lugar); y el mismo jugador
  con otro apellido en la API y en la prensa («Alberto Baio» / «Alberto
  Costa», 1412: poné el `jugadorId` de la hoja en la fila de la prensa; por
  nombre no se casa una pila sola, 1386).
  Y desde la pasada del 15/11 (noche): el DT suspendido que la base no
  marca porque la API no publicó la roja (1424, Di Noia en Maldonado: la
  ficha del partido anterior trae 0 rojas; cuando la API la publica, la
  agenda trae `dt.expulsado`, 919/920): la prensa manda y va en `dt.banco`.
  Y desde la pasada del 15/11 (mediodía): el `actualizadoEn` del parte que
  se mueve cuando `xi/auto` recaptura el once después del final (1221, 1394:
  es informativo; el orden parte/pitazo, la simulación y el filtro «depositado
  antes del pitazo» leen `deposito_previo_en`, que sella solo el POST de la
  corrida); y el `dos-partidos` de un equipo con liga y copa a 24 h justas
  (1398, 1399: Alianza Atlético y Cristal, Liga 1 el 14/11 y Copa de la Liga
  el 15/11: es la fecha de la API, la agenda ya lo marca en `conflicto` y el
  parte confirma la fecha en prensa). Si la fecha resulta ser un aplazado sin
  marcar (un partido que ya no se juega ese día), eso sí se reporta, con la
  fuente.
  Y desde la pasada del 16/11 (tarde): el partido de la fecha que pasó y
  sigue «programado» sin marcador (1429, 1433: Alianza Lima–Cajamarca y dos
  más de la Liga 1 del 14/11, aplazados por la fecha FIFA que la API no
  marca; el extractor re-pide por fecha hoy−3d..+10d en cada corrida y
  `sanar_fechas` después, así que la base trae lo que da la API): el parte los
  trata como no jugados y no se reporta mientras la API no cambie. Se
  reporta si la prensa da el RESULTADO y la base sigue sin él después de una
  corrida. Y la hoja de la API de una selección con el DT anterior en el
  banco (1431: Nagelsmann y Stojković en las hojas de octubre de la Liga de
  las Naciones, Klopp y Paunović según la prensa): la disciplina 30 lee la
  hoja y DT-DISCREPANCIA ya avisa; la prensa manda y va en notas.
  Y desde la pasada del 18/11 (mediodía): el banco probable (sin el once)
  con alguien que hoy no puede estar porque murió, se retiró o se lesionó
  hace días, cuando la base NO capturó la hoja del último partido del equipo
  (1443: De Miguel, del Tenerife, fallecido el 03/11; la hoja del 15/11
  contra el Ceuta sin capturar). Desde el PR #575 el banco probable deja
  fuera a quien no está en ninguna de las 2 últimas hojas CAPTURADAS
  (`banco.CONVOCATORIAS`), y la API no marca a un jugador fallecido: el parte
  lo saca a mano y lo dice en notas. Se reporta si el jugador sigue en la
  lista con 2 hojas capturadas posteriores a su ausencia en las que no
  figura.
  Y desde la pasada del 20/11 (noche): el lado que queda en `dtEquivocado`
  con `disputado: true` después de declarar `dt.banco` con fuente (1450:
  Alcoyano–Mallorca, la hoja con «Luis Garrido» y la crónica con Fran
  Alcoy). Es por diseño (`parte.MOTIVOS_BANCO` y `dt_equivocado`): queda a
  la vista, pero NO aparta el caso, porque `lecciones._casos` pone en
  cuarentena solo los lados no disputados. No hace falta desmentir el banco.
  `dtEquivocado` sale vacío solo cuando el nombre declarado casa con el banco
  de la hoja o cuando la hoja no trae entrenador. Se reporta si un lado
  `disputado` aparece igual en una cuarentena automática.
  Y desde la pasada del 20/11 (mediodía): la coherencia (Jev) sin evaluar
  por timeout o falta de red (1451, 894: con varios depósitos a la vez Jev
  puede no contestar en `jev.TIMEOUT` × 3 intentos; el parte se deposita
  igual, el recibo trae `coherencia.error` y el revisor lo cuenta en
  `noEvaluados`). Si querés el guardrail en ese parte, re-depositalo igual
  al final de la corrida, de a uno, y vuelve a evaluar; no se reporta. Se
  reporta si `GET /analisis/cowork/revisor` da errores en más de la mitad
  de los partes de una corrida (Jev caído, no saturado). Y el partido de la
  agenda sin cuotas prepartido en la app (1453, 1261, 1267: decidido por el
  usuario en la #1379, dato de la API sin regla nueva): el escaneo del
  mantenimiento ya lo deposita con su chequeo `sin-cuotas` y el parte usa
  la casa de la web con fuente y hora. Y el ciclo de amarillas que la prensa
  da y la base cuenta más corto en una liga con `amarillasSinRegla` (1452,
  Primera de Uruguay: Queiroz con 5 según la prensa y 2 en la base): sin
  la regla la base no afirma el ciclo y la prensa manda (1254, 1373, 1263).
  Se reporta, con el reglamento citado, si conseguís la regla de esa
  competición: entra a `sanciones.UMBRALES`.
  Y desde la pasada del 21/11 (mediodía): la coherencia (Jev) con **402
  «Insufficient credits»** (1468, 1471: la cuenta de Jev sin saldo; no es
  timeout ni saturación, 1451). Es del usuario (recargar) y ya espera en
  «Decisiones pendientes» como #1468: mientras esa siga en `usuario`, no se
  reporta otra vez; el parte se deposita igual y el error queda sellado en
  `coherencia`. Se reporta si el 402 sigue después de que #1468 pasó a
  `resuelta` (la recarga no alcanzó o la clave es otra).
  Y desde la pasada del 22/11 (noche): **la ficha incompleta o incoherente que
  trae la API** —eventos cortados o sin cambios, ficha sin eventos de un
  partido demorado o suspendido, posesión invertida respecto de los pases, la
  plantilla con el jugador en otro club— (1481-1484, 1490; familias #27, #94,
  #447 y #2, decididas por el usuario en la #1379: dato de la API, cubierto
  por su alerta o por la prensa, sin regla nueva). El veredicto se cierra con
  la prensa y lo dice en `notas`; no se reporta. Se reporta si la app CALCULA
  algo mal con esa ficha (un `avanza`, una ventana del TDE, una sanción) o si
  la misma ficha sigue incompleta 48 h después del partido.
  Y desde la pasada del 25/11 (mediodía): **el aplazado que la API todavía
  da en la fecha vieja** (1505, Clausura de Paraguay: 1632068, 1632069 y
  1632071 «NS» el 25/11 21:00Z, y la programación oficial los da el 29/11).
  Es la misma causa que la #1429 (la API publica tarde la postergación; el
  extractor re-pide por fecha hoy−3d..+10d y la base la sigue), que espera la
  decisión del usuario en «Decisiones pendientes»: mientras esa siga en
  `usuario`, un partido YA reportado no se reporta otra vez. Sin ciego ni
  parte, una línea en el resumen con la fuente; el escaneo ya lo marca
  `sin-cuotas`. Se reporta, con la fuente, un partido NUEVO aplazado sin
  marcar (entra a la misma familia), o el ya reportado si la API lo movió y la
  base sigue con la fecha vieja después de una corrida del extractor.
  Y desde la pasada del 26/11 (mediodía): **EFE-RECOMPUTO-PENDIENTE que no
  suena** con un once rotado (1503 Como–AEK, 1511 Brujas–Liverpool y
  Atlético–Viking; las dos por diseño en 48 h). La regla es la de
  `parte.alerta_recomputo_efe` (1068 paso 2, aprobada con la EFE v1.10): cuenta
  SOLO los titulares fijos (🔴 TF de la tabla F1) que el parte no declaró, y
  suena con `RECOMPUTO_MIN_TITULARES` = 3 o con el arquero TF en el banco; un
  TH o un ROT (el arquero que alterna incluido) no cuenta, y la nota del bloque
  B «recomputado con el once» con los puntajes A–E movidos la calla (1467).
  Antes de reportar, contá en `GET $B/analisis/cowork/f1/{fixtureId}` cuántos TF sin declarar
  arrancaron afuera; se reporta solo si son 3+ (o el arquero TF) y la alerta no
  está en el parte. Y la **cuarentena por DT equivocado que no aparece en el
  campo `cuarentena` del parte** (1497): ese campo es el de la llave maestra;
  la automática la calcula Aprendizaje al leer (`lecciones.py`, desde
  `dt_original_json`, 712), así que corregir el DT con `POST …/dt` basta. Se
  reporta si el caso con `dtEquivocado` sin `disputado` sigue contando en las
  métricas de Aprendizaje.
