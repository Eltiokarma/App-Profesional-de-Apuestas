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
  antes del pitazo no se toca); la etiqueta `lectura_efe` del modo de fallo
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
  (1254: espera la decisión de la 1067; sumá el caso a esa). Y desde la
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
  `sinRehacer` con el once a tiempo (1305: sumalo a la #1052, que espera la
  decisión). Y desde la pasada del 08/11 (mediodía): el F2 o los
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
  con el once ya capturado, es código otra vez.
