# Extracción en tiempo real — plan por fases

Objetivo: pasar de la foto diaria actual a datos frescos en tres saltos
controlados, sin romper la regla de oro (el backend HTTP es de solo lectura;
solo `backend/ingesta/` escribe). Presupuesto: plan pago de API-Football,
tope y ritmo autoajustados por cabeceras `x-ratelimit-*` (ya hecho).

## Estado actual (fase 0)

Una corrida diaria (`SAD_INGESTA_HORA`): fixtures hoy−3d..+10d + **una sola
foto** de cuotas por fixture NS (los que ya tienen odds se saltan). La gráfica
de movimiento de Cuotas es simulación del frontend anclada a esa foto
(`src/lib/odds.ts: seriesFor`), y el minuto/marcador en vivo también son
simulados (`src/store.ts`).

## Fase 1 · Historial de cuotas prepartido (= punto 4 del roadmap) — HECHA

La que da valor de apuestas real: movimiento de la cuota **antes** del partido.

- **sad.db**: tabla `odds_history(fixture_id, league_id, bet_id, bet_name,
  value, odd, casas, captured_at)` — un punto por selección y captura con la
  **media entre casas** (más compacta que guardar cada bookmaker; `casas`
  registra cuántos promedió). La tabla `odds` queda como "última foto"
  (compatibilidad con el pipeline y la regla de huecos de
  `docs/ROADMAP_BURBUJAS.md`). El extractor crea la tabla si no existe.
- **Extractor**: `fixtures_para_cuotas` — primero los NS sin cuotas de toda
  la ventana (primera captura), después re-captura de los NS que empiezan en
  <= 2 días aunque ya tengan (snapshot nuevo).
- **Scheduler**: `SAD_INGESTA_HORA` acepta lista `"06:30,12:30,18:30"`.
  Tres snapshots al día ya dibujan una curva prepartido honesta.
- **Contrato**: `GET /cuotas/{fixtureId}/historial` → `CuotaSnapshot[]`
  (asc por captura; `[]` en DBs anteriores a esta fase).
- **Frontend — regla de datos**: en producción (`http`) NO se pinta nada
  inventado. Con >=2 capturas reales por selección, la curva es real
  (apertura = primer snapshot, eje X = capturas); con menos, placeholder
  honesto y solo las cuotas actuales (reales). El toggle "En vivo" y toda
  la simulación quedan confinados al modo demo (`mock`, "MOTOR LOCAL ·
  DEMO") hasta la fase 3.

Presupuesto fase 1: 3 corridas × ~150 req ≈ **450/día** (Pro: 7.500).

## Fase 2 · Día de partido — HECHA

- `extractor --ventana-horas 6`: corrida ligera SOLO de cuotas para los NS
  que empiezan en <= 6 h (snapshot directo a `odds_history`; sin fixtures
  próximos sale con 0 requests).
- `SAD_REFRESCO_MIN=30` (env, vacía = apagado): hilo propio en
  `backend/app.py` que corre ese refresco cada N minutos (piso 10; la
  ventana se ajusta con `SAD_REFRESCO_VENTANA_HORAS`, default 6).
- Escritura con `busy_timeout` para convivir con las lecturas del backend
  (el paso a WAL sigue reservado para la fase 3).
- Cierra la curva prepartido con densidad donde importa (las últimas horas
  son las de más movimiento).
- Presupuesto: ~20 fixtures/día × 8-48 refrescos ≈ **160-960/día** extra —
  **siempre que se pida por fixture**. La lección del 29/07/2026: al pasar
  las cuotas a "lote por fecha", cada refresco pagaba el feed mundial de
  `/odds?date=` (40-90 páginas) para re-capturar 5-15 partidos nuestros, 48
  veces al día ≈ 2.000-4.300 requests — y el plan de 7.500 amaneció muerto
  (`7496/7495`) con las copas paradas a mitad de partido. Desde entonces
  `capturar_cuotas_lote` elige POR FECHA: pocos pendientes
  (`SAD_CUOTAS_LOTE_UMBRAL`, 12) → `/odds?fixture=` exacto; muchos → lote.
  El consumo del día queda auditado por endpoint en `.extractor_cuota.json`
  (lo imprimen cada ciclo y `diag_vivo`): la próxima vez que el plan
  aparezca vacío, el culpable tiene nombre.

## Fase 3 · En vivo de verdad — HECHA

- **`backend/ingesta/en_vivo.py`** (un ciclo por invocación): busca fixtures
  nuestros en ventana de juego en sad.db (0 requests si no hay);
  `GET /fixtures?live=<ids de LIGAS>` actualiza marcador/minuto/estado
  (via guardar_fixtures); `GET /odds/live?league=<id>` **por cada liga con
  partido nuestro en juego** → tabla `odds_live` (con `suspendida` y
  `minuto`), retención 30 días. Activa WAL en sad.db
  (requisito: escrituras por minuto conviviendo con lecturas).
- **Por qué por liga y no el feed global** (bug 26/07/2026, Melgar–Cristal en
  Perú - Primera División sin cuotas en juego pese a ser liga importante):
  `/odds/live` viene **paginado a ~10 fixtures por página**, igual que el
  `/odds` prepartido. Pedirlo sin filtro traía solo la página 1 — los 10
  primeros partidos vivos DEL MUNDO — así que nuestras ligas casi nunca
  aparecían y la UI mostraba "sin cobertura de cuotas en vivo en esta liga",
  que era mentira: nunca se preguntó por ellas. Con `?league=` el feed llega
  completo y una sola request cubre todos los partidos simultáneos de esa
  liga. Topes: `SAD_LIVE_ODDS_LIGAS` (6 ligas/ciclo, EN JUEGO primero y luego
  por CONSULTA más vieja: ninguna se queda sin turno) y
  `SAD_LIVE_ODDS_PAGINAS` (3).
  Test offline: `python -m backend.test_en_vivo`.
- **Por qué la rotación va por consulta y no por captura** (bug 27/07/2026,
  Guayaquil City–U. Católica en Ecuador - Liga Pro sin cuotas en juego): el
  orden era por la última captura en `odds_live`, y una liga donde la API no
  devuelve odds live nunca captura nada — quedaba pegada al frente de la cola
  para siempre y, con el tope de 6 ligas/ciclo, varias así acaparaban todos
  los cupos: a las ligas CON cobertura ni se les preguntaba y la UI volvía a
  decir "sin cobertura de cuotas en vivo en esta liga" siendo mentira. Ahora
  cada consulta (traiga datos o no) se registra en `odds_live_consultas` y la
  cola rota por esa marca: la liga vacía también gasta su turno.
  `diag_vivo` la lee para distinguir "nunca le tocó turno" de "se preguntó y
  la API no dio nada".
- **Por qué la cola pone EN JUEGO primero** (bug 29/07/2026, Gimnasia LP–River
  Plate en Argentina - Liga Profesional, minuto 3 sin cuotas): el universo de
  ligas a pedir mezcla dos cosas muy distintas — las del feed live, con partido
  realmente en marcha, y las que solo tienen un NS/TBD dentro de una ventana de
  3h45 — y la cola las trataba igual. Con tope por ciclo, una liga sin nadie
  jugando le ganaba el turno a otra con el partido corriendo, y el partido se
  termina mientras la ventana no. Ahora `orden_por_antiguedad` recibe el set de
  ligas en juego y ordena `(no está en juego, consulta más vieja, id)`. Además:
  el tope pasó de 6 a 12 —y **volvió a 6 el mismo día**: ver el freno de
  presupuesto más abajo—, los **Amistosos de Clubes (667)** salieron del ciclo en
  vivo — es la liga que más NS zombis produce, ya marcada en `LIGAS_RUIDO`, y
  gastaba turnos sin partido real que cubrir — y **Argentina Primera Nacional
  (129)** se marcó como menor: era la única 2ª división sin marcar. Si el tope
  vuelve a quedar corto, el log lo grita: `ATENCIÓN: N de ellas tienen partido
  EN JUEGO`.
- **Por qué `con_datos` no bastaba** (29/07/2026, Gimnasia LP–River Plate y
  Mirassol–Remo: la pantalla decía *"la API no cubre cuotas en vivo de esta
  liga"* en ligas con cobertura de sobra). El booleano se ponía a 0 en **cuatro
  situaciones distintas** y la UI las presentaba como una: el feed vino vacío;
  el feed trajo partidos pero ninguno nuestro (el filtro `?league=` no
  devolvió lo pedido); la request se cayó (red, HTTP, `errors` de la API,
  presupuesto agotado — `get()` devuelve `None` en todas y `paginado()` lo
  convierte en `[]`, idéntico a un feed vacío); o el turno se lo llevó otra
  liga. Ahora `odds_live_consultas` guarda `estado` (`ok` · `vacia` · `ajena` ·
  `fallo`) más `items`/`nuestros`/`ajenos`, y `Cliente.fallos` es lo que
  distingue una caída de una respuesta legítimamente vacía. **Solo `vacia` se
  acerca a "falta de cobertura", y ni ese lo prueba.**
- **Rescate por fixture** (`SAD_LIVE_ODDS_FIXTURES`, 4 por ciclo; 0 = apagado):
  la vía por liga sigue siendo la primera porque es la barata — 1 request cubre
  todos los simultáneos — pero cuando no trae un partido que SÍ se está
  jugando, se le pregunta directo con `/odds/live?fixture=`. Eso no depende de
  que el filtro por liga se porte bien, y es lo que salva la curva en las tres
  causas de fallo de arriba.
- **FRENO DE PRESUPUESTO** (`SAD_LIVE_RESERVA`, 1500) — la lección más cara del
  29/07/2026. Con el tope en 12, el ciclo por minuto podía pedir >30 requests
  (12 ligas × hasta 3 páginas, + XI, + rescate) y **agotó el plan del día**:
  `presupuesto diario agotado (7496/7495, respaldo 95/95)`, cero requests, cero
  cuotas, cero marcador — y las copas que sí funcionaban se pararon a mitad de
  partido. El tope volvió a **6**, y ahora `cupo_del_ciclo` calcula cuántas
  ligas caben sin tocar la reserva: con margen de sobra sirve el tope entero,
  al acercarse encoge, y al llegar deja de pedir cuotas pero **sigue pidiendo
  marcador y minuto** (1 request, lo más barato y lo más valioso). El rescate
  por fixture pasa por el mismo freno. Un tope alto ya no puede vaciar el plan.
- **Partidos VIP y modo emergencia** (`SAD_EMERGENCIA_KEY` · `_TOPE` ·
  `_LIGAS`): "este partido lo quiero sí o sí, aunque cueste". Se marca desde
  la app (botón en Cuotas → `POST /fixtures/{id}/vip` → `.vip_fixtures.json`
  en la raíz de datos, NO las .db; caduca a las 8 h) o por liga con
  `SAD_EMERGENCIA_LIGAS`. Con plan sano, el VIP entra al rescate por fixture
  aunque su liga sea menor (la marca manda sobre `LIGAS_MENORES` para ESE
  partido). Con el plan y el respaldo muertos —la noche del 29/07— la clave
  de emergencia (un 2º account de api-sports con el Basic "soft limit"
  deprecated, que nunca corta y factura el excedente a $0.005) les mantiene
  marcador y cuotas: 1 request de `/fixtures?ids=` compartida + 1 de
  `/odds/live?fixture=` por VIP **confirmado en juego** (a un NS solo se le
  paga el marcador). Techo diario propio (`SAD_EMERGENCIA_TOPE`, 300 ≈ $1):
  el candado contra la factura sorpresa. Nunca la toca el flujo normal.
- **Refresco forzado de liga** (el botón ⟳ junto al nombre de la liga en
  Partidos → `POST /ligas/{id}/refrescar` → `.refresco_ligas.json`): el
  próximo ciclo actualiza el MARCADOR de los partidos SIN RESULTADO de esa liga
  por `/fixtures?ids=` — presupuesto normal si queda, emergencia si el plan está
  muerto (el caso real: Bragantino–Sporting Cristal ya jugándose con el estado
  congelado en NS). Solo marcador; las cuotas siguen sus reglas (VIP para
  pagarlas).
  Dos cosas que lo tenían **inservible** en su primera versión (30/07/2026: el ⟳
  daba el ✓ y no pasaba nada):
  1. **Usaba la ventana de juego** (−210 min/+15 min), la misma del ciclo
     normal. El botón existe para arreglar lo que esa ventana se dejó fuera, así
     que con ella no arreglaba nada: los NS congelados de hace horas y los
     partidos que arrancan más tarde quedaban excluidos — exactamente el motivo
     del click. Ahora tiene ventana propia y ancha (`REFRESCO_ATRAS_H` 12 h /
     `REFRESCO_ADELANTE_H` 6 h) y entra cualquier estado que no sea final.
  2. **El pedido se consumía siempre**, incluso sin presupuesto ni clave de
     emergencia: el click se evaporaba en silencio y el usuario esperaba de
     balde. Ahora solo se consume si se pudo atender (o si de verdad no había
     nada que refrescar); si no, sobrevive a los ciclos hasta que haya con qué
     servirlo, y caduca solo a los `REFRESCO_CADUCIDAD_MIN` (30).
  Y el POST devuelve `fixtures`: cuántos partidos va a tocar. Con 0 la app dice
  *"nada que refrescar"* en vez de pintar un ✓ que no significa nada.
- **LAS DOS RESERVAS TIENEN QUE SER DISTINTAS** (30/07/2026: 309 ciclos con las
  cuotas en juego `EN PAUSA`, de 18:33 a 00:01 — 5 h 30 min del prime time
  sudamericano, con partidos de Sudamericana sin curva). Y el plan **ni se
  agotó**: 6.670/7.495. El fallo era de prioridades, no de volumen. La ingesta
  en bloque paraba al dejar `SAD_BACKFILL_RESERVA` (1500) y el ciclo en vivo se
  apaga por debajo de `SAD_LIVE_RESERVA` (1500): **el margen real del vivo era
  CERO** — el bloque gastaba exactamente hasta el punto donde el vivo se apaga.
  El desglose del día lo dejó a la vista: ficha de partido 2.569 + jugadores
  1.656 = **63 % del plan** gastado en cosas que se pueden bajar mañana sin
  perder nada, mientras la curva de un partido en juego pasa UNA vez y no
  vuelve. Ahora `reserva_del_dia(limite, con)` mira el CALENDARIO (no el reloj,
  que depende del huso): con fútbol nuestro en juego o a menos de
  `SAD_BLOQUE_VENTANA_HORAS` (14 h), la reserva del bloque sube a
  `SAD_BLOQUE_RESERVA_PARTIDOS` (3500) y el bloque cede el paso. Sin fútbol
  cerca vuelve a 1500 y avanza a fondo con el backlog.
- **Backoff por liga** (`SAD_LIVE_BACKOFF_PASO_MIN`/`_TOPE`, 3 min × rondas,
  tope 10 MIN). Auditoría de la noche del 31/07/2026: **796 requests
  tiradas, el 11 % del plan** — 506 rondas por liga que volvieron vacías y 290
  rescates por fixture con **cero** aciertos. El detalle por liga: Bolivia 115
  ciclos preguntando lo mismo, Ecuador 84, Chile 84, Venezuela 78, Perú 44,
  Colombia 30, México 55. Preguntar una vez está bien; insistir cada minuto es
  quitarle presupuesto a las ligas que SÍ dan cuotas. Ahora cada ronda seguida
  sin datos aleja la siguiente, una ronda con datos resetea el contador, y un
  `fallo` de red no castiga (no dice nada sobre la cobertura). El rescate por
  fixture tampoco insiste en una liga dormida — eso era el 100 % de esos 290.
  **Por qué el tope es bajo (10 min) y no 30**: Los Chankas–Comerciantes Unidos
  de esa misma noche. La liga 281 devolvió vacío **44 rondas seguidas, 45
  minutos**, y a las 20:30:59 abrió de golpe con 619 valores y siguió con 227
  capturas sin fallar. Un feed vacío casi nunca significa "esta liga no tiene
  cobertura": significa que la casa aún no abrió el mercado en vivo. Esperar de
  más no ahorra (en esos 45 min: 5 consultas con tope 30 vs 6 con tope 10) y
  llega tarde justo al tramo que falta al principio de la curva. Y el contador
  **caduca** a las `SAD_LIVE_BACKOFF_OLVIDO_H` (8 h): el castigo no es eterno,
  cada jornada empieza limpia, y como es por `league_id`, añadir ligas al
  catálogo no desarma lo aprendido de las demás.
- **`database is locked` no puede tumbar el ciclo** (01/08/2026: tres caídas
  en una noche —23:53, 00:23, 00:54— en `capturar_xi`, `guardar_fixtures` y el
  DELETE de retención). En WAL hay **un solo escritor**, y el refresco de
  cuotas retiene el lock ~20 s: con `busy_timeout=15000` el ciclo se rendía y
  moría con traceback, perdiendo la vuelta ENTERA, marcador incluido. Ahora
  todos los escritores (extractor, ficha, jugadores, en vivo) declaran
  `journal_mode=WAL` y `busy_timeout=30000`, y `main_tolerante()` convierte un
  lock en "este ciclo se salta, el siguiente reintenta" — es contención normal
  entre procesos, no un error del que haya que morir.
- **El rescate por fixture ROTA** (01/08/2026, México): era
  `sorted(faltan)[:TOPE]`, o sea siempre los mismos ids bajos. Con 6 partidos
  en juego y tope 4, los dos de id más alto **no se rescataban nunca** — el
  mismo error que ya habíamos arreglado para las ligas, sin aplicarlo a los
  fixtures. Ahora `orden_rescate` ordena por intento más viejo
  (`odds_live_rescates`) y el turno se gasta aunque el feed venga vacío: si no,
  el mismo fixture volvería a encabezar la cola cada ciclo.
- **Por qué la pantalla ya no miente.** Los tres bugs anteriores compartían
  síntoma — "sin cobertura de cuotas en vivo en esta liga" — porque la UI solo
  sabía que este fixture no tenía filas en `odds_live`, y de ahí deducía falta
  de cobertura. `GET /fixtures/{id}/live` ahora devuelve `coberturaLive`
  (`con_datos` · `sin_datos` · `feed_ajeno` · `fallo` · `sin_consultar`) y
  `coberturaConsultadaEn`, leídos de `odds_live_consultas` para la liga del
  fixture, y la sección Cuotas dice **solo lo observado**: *"aún sin turno del
  ciclo en vivo"*, *"la última consulta de esta liga vino vacía"*, *"el feed de
  la liga no trajo este partido"*, *"la última consulta de cuotas falló"*.
  Ninguna de esas frases concluye nada sobre la cobertura de la API — esa
  conclusión es la que estuvo mal tres veces seguidas.
- **Las otras tres puertas** que dejaban partidos sin curva (26/07/2026, UTC
  Cajamarca–UCV Moquegua):
  1. **`TBD` no era candidato.** La ventana solo aceptaba `NS`, pero en esta DB
     `TBD` es un estado real y frecuente (toda la maquinaria de zombis de
     `diagnostico.py` va sobre NS/TBD). Un partido con hora por confirmar
     jamás entraba al ciclo. Ahora entran `NS` y `TBD`.
  2. **Solo se miraba hacia atrás.** La ventana era `[saque−0, saque+3h30]`:
     si la API adelanta el saque o nuestra hora va unos minutos tarde, el
     partido ya se juega mientras su `date` sigue en el futuro y el ciclo
     salía con "sin partidos en ventana · 0 requests" sin preguntar nada.
     Ahora arranca 15 min antes (`VENTANA_PREVIA_MIN`).
  3. **`live=<37 ligas>`.** El parámetro hermano `ids` está documentado con
     tope de 20 y de `live` no hay tope publicado; si recortara, se caerían
     justo las ligas de id alto — Perú (281), Venezuela (299), Bolivia (344).
     Pasado `TOPE_LIGAS_LIVE` (20) se pide `live=all` y filtramos nosotros:
     mismo coste, cero dependencia de lo que haga el filtro del servidor.
  Y lo más importante: **las cuotas ya no dependen de ese feed**. El universo
  de ligas a pedir sale del feed live **más** nuestros candidatos locales, así
  que un partido que el feed se deje igual recibe su `/odds/live?league=`.
- **`python -m backend.ingesta.diag_vivo --fixture N [--api]`**: dice cuál de
  las puertas se cerró para un partido concreto — liga fuera de lista o marcada
  menor, ventana, si el ciclo corrió esa franja, filas en `odds_live`, si
  `cuota_key` las mapea (hay datos pero la ficha se ve vacía), prepartido y
  presupuesto del día. Con `--api` (2 requests) responde lo único que no está
  en la DB: si la API ofrece odds live de esa liga.
- **Alineaciones prepartido** (27/07/2026): el ciclo también pide
  `fixtures/lineups` de los partidos de las ligas en vivo entre 75 min antes
  y 45 min después del saque, hasta capturarlas — la ficha post-partido
  (`ficha_partido.py`) solo baja partidos terminados, así que el XI
  confirmado no llegaba nunca ANTES del pitazo, que es cuando el análisis lo
  necesita. Reintento cada 5 min (tabla `xi_intentos`, mismo patrón que
  `odds_live_consultas`), tope `SAD_LIVE_XI` (4 fixtures/ciclo, 0 = apagado).
  Van a la tabla `alineaciones` de siempre: `/fixtures/{id}/ficha` las sirve
  al instante (sin sello), los skills/EFE/DTP las reciben por esa vía, y la
  tarjeta "Alineaciones confirmadas" de Burbujas las muestra con refresco
  automático y botón ↻.
- **Cambios de formación** (28/07/2026): un XI capturado más de 30 min antes
  del saque se refresca UNA vez al entrar en los últimos 15 min
  (`XI_CAPTURA_VIEJA_MIN`/`XI_REFRESCO_ANTES_MIN`), por si el DT lo corrigió;
  tras ese intento la condición se apaga sola, y una respuesta vacía nunca
  pisa el XI ya capturado. Los cambios DURANTE el partido no tocan
  `alineaciones`: son eventos `subst` que el ciclo ya captura, y la tarjeta
  los cruza con el once — la cancha CONSERVA el once inicial (el sustituido
  se queda con sus estadísticas y su ▼min'; quitarlo perdía sus scores),
  el que entra vive en el banco con su ▲min' y sus propios scores, y la
  tira de cambios cuenta la historia completa; como la API confunde quién
  viaja como jugador/asistente en un cambio, la UI decide por membresía
  (el que está en cancha es el que sale).
- **`SAD_LIVE_SEGUNDOS=60`** (env, vacía = apagado, piso 30): hilo en
  `backend/app.py` que corre el ciclo.
- **Backend**: `GET /fixtures/{id}/live` → estado/minuto/marcador reales +
  `cuotas` (última captura, con suspendidas) + `serie` (movimiento del
  partido). `cuota_key` ganó el alias "Fulltime Result" (catálogo live).
- **Frontend**: en http, con el partido en juego, polling silencioso cada
  `VITE_POLL_LIVE_MS` (default 60 s): banner EN DIRECTO real (marcador,
  minuto, hora de captura) + sección "Cuotas en juego" del mercado activo
  (suspendidas atenuadas). Sin cobertura de odds live: solo marcador/minuto,
  nada inventado.
- **Gráfica**: la `serie` live se pinta como tramo en vivo REAL de la
  gráfica grande (prepartido 0→KO con el historial, KO→90' con odds_live,
  marcador de minuto actual). Si la liga no tiene cobertura de odds live,
  el tramo simplemente no aparece — regla "real o nada". Pendiente menor:
  el catálogo de bets de /odds/live puede necesitar más aliases en
  `cuota_key` según lo que llegue el primer día real de partidos (hoy
  mapea "Fulltime Result"/1X2 y los mercados clásicos).
- **Presupuesto**: 1 req/min de marcador + 1 por liga con partido vivo (tope
  12) × ~6 h de ventana con partidos. El tope es el techo, no el gasto: solo se
  pide a las ligas que tienen candidato, y en la práctica 2-4 ligas nuestras
  coinciden en juego → ≈ **1.100-1.800/día** en los días cargados. Total fases
  1+2+3 ≈ 2.500/día en el peor día — cabe en Pro (7.500) con la reserva de
  backfill intacta. Si aprieta: bajar `SAD_LIVE_ODDS_LIGAS` o subir
  `SAD_LIVE_SEGUNDOS`. Si sobra (el caso real: el plan sin tocarse mientras
  ligas con partido esperaban turno), subirlo o ponerlo en `0`.

## Fase 4 · Solo si hace falta

Postgres gestionado (`docs/SERVICIOS_EXTERNOS.md`) si el volumen de
`odds_history`/`odds_live` o la concurrencia superan a SQLite+WAL. No antes.

## Decisiones abiertas

1. Cobertura real de `/odds/live` por liga: ya no se confunde con el bug de
   paginación ni con el de rotación (ver fase 3), pero sigue pendiente medir
   en qué ligas la API de verdad no ofrece odds live. Los logs del ciclo lo
   dicen liga por liga ("ligas sin odds en el feed live") y
   `odds_live_consultas.con_datos` guarda el resultado de la última consulta;
   si alguna sale vacía siempre, vale la pena dejar de preguntarle y
   ahorrarse la request.
2. Retención de `odds_live` y de snapshots viejos de `odds_history`.
3. Si el poll en vivo vive en el mismo servicio Railway (hilo como el
   scheduler actual) o en un worker separado — empezar en el mismo, separar
   solo si compite con el backend.

Orden: 1 → 2 → 3. La fase 1 es la única que toca el contrato web↔backend;
las demás suman sobre ella.
