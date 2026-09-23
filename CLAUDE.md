# SAD · Análisis pre-partido — guía para el agente

App **autocontenida** de análisis pre-partido de fútbol y apuestas:
web (React + Vite + TS) + backend (FastAPI, solo lectura) + Motor SAD.
Todo en español (UI, commits, docs).

## Comandos

```bash
# web
npm install && npm run dev        # http://localhost:5173
npm run build                     # typecheck + build (SIEMPRE antes de commitear)
npm run test:motor                # motor TS verificado contra docs/MOTOR_SAD_EXTRACCION.md
npm run test:kview                # capa de visualización de las K (3 valores por gráfica)
npm run test:burbuja              # reventón de burbuja: espejo TS vs vectores dorados (docs/REVENTON.md)
node scripts/audit-movil.mjs /tmp/capturas 360 2400  # vista de teléfono: captura de cada pantalla + desbordes (instrucciones en el script)

# backend (junto a las 4 .db en la raíz, o SAD_DATA_DIR)
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --port 8000
python -m backend.test_api        # verificaciones del contrato (305 checks)
python -m backend.test_en_vivo    # ciclo en vivo: cuotas en juego por liga (sin red)
python -m backend.test_cuotas_lote # cuotas prepartido: lote por fecha vs por fixture (presupuesto)
python -m backend.test_jugadores  # presupuesto de jugadores: TTL separado y padrón de ligas
python -m backend.test_despensa   # despensa en bloque: TTL honesto y canonización
python -m backend.test_ficha      # ficha de partido (alineaciones/eventos/stats, fase A del DTP)
python -m backend.test_dtp        # DTP: cadena rodante, anti-hindsight y sin búsqueda web
python -m backend.test_calendario # calendario SAD: bloque G del EFE calculado (sin IA)
python -m backend.test_cronologia  # cronología SAD: los partidos del timeline, calculados
python -m backend.test_preflight  # chequeo previo del EFE: qué va a costar antes de gastar
python -m backend.test_cowork    # parte de Cowork: bloque F calculado y cruce del once
python -m backend.test_burbuja   # reventón de burbuja: mismos vectores dorados que el TS
python -m backend.test_jev       # adaptador de Jev (System One): sin clave corre simulado y no decide
python -m backend.test_coherencia # guardrail semántico del parte (Jev): etiqueta la prosa, el código compara con el número
python -m backend.test_modo_fallo # modo de fallo del veredicto (Jev): etiqueta para el dossier, no toca población ni métricas
python -m backend.backtest_burbuja --padron --calibrar # backtest del reventón en las ligas importantes: tasa por riesgo, lift por señal, regla del nivel, por liga, y la logística que propone los puntos (--horizonte/--liga/--muestra/--json; en el servidor: GET /analisis/burbujas/backtest?calibrar=true, maestro)
python -m backend.test_backtest_burbuja # anti-fuga y conteos del backtest, sobre la demo
python -m backend.seed_demo       # DBs demo con esquemas reales (./demo_data)
python -m backend.backtest_gap    # backtest §5 muestreado (--muestra/--liga/--horizonte/--calibrar/--por-liga)

# ingesta (dueña de los datos; el backend HTTP sigue siendo de solo lectura)
python -m backend.ingesta.extractor --probar    # 1 request de prueba (API_FOOTBALL_KEY en .env)
python -m backend.ingesta.extractor --buscar "Copa Chile"  # descubrir IDs de torneos nuevos
python -m backend.ingesta.extractor             # fixtures hoy−3d..+10d (por FECHA, todas las temporadas) + cuotas NS (tope auto por plan)
python -m backend.ingesta.diagnostico --dia 2026-05-31 --api  # auditar huecos (NS/TBD vencidos) y contrastar un día con la API
python -m backend.ingesta.extractor --ventana-horas 6  # refresco ligero: solo cuotas de NS próximos
python -m backend.ingesta.jugadores             # plantillas/bajas/traspasos/DT de equipos con NS próximos (docs/JUGADORES.md)
python -m backend.ingesta.jugadores --solo-dt   # rehacer SOLO el DT vigente (1 request/equipo, sin TTL); en Railway: SAD_JUGADORES_SOLO_DT=1 una corrida
python -m backend.ingesta.jugadores --dt-agenda # DT fresco de los que juegan en <= 2 días: alineación del último partido + /coachs si está viejo (corre en la corrida diaria)
python -m backend.ingesta.en_vivo               # 1 ciclo en vivo: marcador/minuto + odds_live (WAL)
python -m backend.ingesta.diag_vivo --hoy       # por qué un partido no tiene cuotas en juego (--fixture N, --api)
python -m backend.ingesta.ficha_partido        # alineaciones+eventos+stats de los partidos anteriores (3 req c/u)
python -m backend.ingesta.ficha_partido --estado  # qué ficha hay capturada y si trae grid/xG (0 requests)
python -m backend.analisis.despensa_bulk --listar  # despensa del repo: qué hay y qué edad tiene
python -m backend.ingesta.adelgazar [--aplicar]  # sad.db ($SAD_DATA_DIR o --db): borra mercados que nadie lee + retención + VACUUM (sin --aplicar solo mide); en Railway con SAD_ADELGAZAR=1 (la consola web mata el proceso)
python -m backend.ingesta.pipeline --out .      # regenera levels/constants/discreto desde sad.db
python -m backend.ingesta.test_paridad          # test dorado vs DBs del pipeline viejo
```

Modo de datos por `.env`: `VITE_DATA_SOURCE=mock` (motor local demo) o
`http` + `VITE_API_BASE_URL` (backend real). Ver `.env.example`.

## Arquitectura (contract-first)

```
docs/openapi.yaml  ←── FUENTE DE VERDAD del contrato web↔backend
src/api/           DTOs + cliente fetch tipado
src/services/      datasource.ts (Mock/Http, MISMO contrato) · appdata.ts (DTO→UI)
src/motor/         Motor SAD en TS: niveles ventana-20, q*/k* con reseteo,
                   fusión k = k⁺+k⁻, bins v6, regresión §5 — VERIFICADO contra
                   docs/MOTOR_SAD_EXTRACCION.md; no tocar fórmulas sin ese doc
src/sections/      Partidos (inicio) · Cuotas · Burbujas · Skills · Estadísticas ·
                   Aprendizaje (lecciones por skill) · Equipo
src/components/    KLineChart (picos K) · KBarChart (rachas de cuota) ·
                   TablaPosiciones (ÚNICA clasificación, con sus fases) ·
                   DtpPizarra (cierre+apertura del DTP y cadena) ·
                   ParteCowork (el parte depositado + caja del once) ·
                   TeamSearch, shell
backend/           FastAPI de SOLO LECTURA sobre sad/levels/constants/discreto.db
```

## Reglas del proyecto

- **Las `.db` jamás se commitean** (ya están en .gitignore). `backend/ingesta/`
  es la única capa que escribe datos: extractor → sad.db, pipeline → derivadas.
  El repo viejo (Professional-Player / D:/SAD_Replica) queda solo como referencia.
- La clave de API-Football vive en `.env` (API_FOOTBALL_KEY, git-ignorada) o en
  env vars; jamás hardcodeada ni con prefijo VITE_.
- Cambios de API: primero `docs/openapi.yaml`, luego backend + `src/api/types.ts`
  + ambos datasources (mock y http) + tests (`backend/test_api.py`).
- La matemática del motor es sagrada: cualquier cambio se valida contra
  `docs/MOTOR_SAD_EXTRACCION.md` y sus tests (`scripts/test-motor.ts`).
- Despensa del EFE (`backend/analisis/despensa/*.json`, barrido quincenal):
  campo sin fuente va VACÍO, nunca rellenado a ojo; `investigado_en` es la
  fecha real de la investigación. Ver `docs/DESPENSA_DESKTOP.md`.
- Estilo UI: inline styles con las variables CSS del tema (`--bg`, `--t1`,
  `--up/--down`, fuentes `--sans`/`--mono`), números tabulares, todo en español.
  **Teléfono**: una grilla de una columna en móvil es `minmax(0,1fr)`, nunca
  `1fr` a secas (con `1fr` la columna toma el ancho mínimo del hijo más ancho y
  las tarjetas se salen de la pantalla: pasó en Equipo con la botonera de las
  K); una botonera que puede no entrar lleva `flexWrap`; y antes de dar por
  bueno un cambio de layout se corre `scripts/audit-movil.mjs` a 360 y 390 px.
- Tabla de posiciones: SIEMPRE `src/components/TablaPosiciones.tsx` (trae sus
  botones de fase Año/Apertura/Clausura). No duplicar tablas por sección.
- Calendario: SIEMPRE `src/components/CalendarioSad.tsx` sobre
  `loadCalendarioSad` (contrato `/equipos/{id}/calendario`). Las etiquetas del
  rival salen de `backend/calendario.py` con el criterio numérico del protocolo
  y viajan CON su dato; ninguna pantalla dibuja su propia lista de próximos.
- **Parte de Cowork** (`docs/COWORK.md`): el análisis lo escribe Cowork con la
  suscripción y lo deposita en `POST /analisis/cowork`; el motor por API de
  Claude queda de emergencia (plegado en la sección Análisis). El parte NO
  trae nada calculable —total, porcentaje, clasificación, IP, reducción por
  zona, ramas A/B, F3, F4, ni los nombres del partido—: eso sale de
  `backend/analisis/parte.py` y `backend/analisis/bloque_f.py`, y se ignora si
  llega. El bloque F viaja congelado y se cierra con `POST
  /analisis/cowork/{id}/xi` (ficha de API-Football o once pegado a mano); un
  once que casa con menos de 7 nombres de la tabla F1 NO cierra el bloque:
  se devuelve el conflicto en vez de un IP inventado. **Un bloque sin puntuar
  no es un cero**: cada uno viaja con `declarado`, y un parte sin ni un
  sub-score da `porcentaje: null` y `clasificacion: ""` —la pantalla dice SIN
  BLOQUES DECLARADOS, nunca «0% · SIN FORMACIÓN», que es inventar el peor
  juicio de la rúbrica sobre algo que nadie evaluó—. `perdido` mira los
  sub-scores, el TDE, la cadena, el 1X2 y la lectura SAD: el POST reemplaza el
  parte entero y lo que un cuerpo recortado borre tiene que salir en el recibo.
  El veredicto TAMBIÉN acepta el eco de su propio GET, una clave ausente
  conserva lo guardado (`falsadorCumplido` que no viaja no borra el `false`), y
  `cerradoEn` NO se re-sella: es la evidencia de cuándo se cerró el caso, y una
  corrección posterior va aparte en `actualizadoEn`. Cada skill del pipeline
  tiene su sitio en la pantalla (tabla en `docs/COWORK.md`): bloque G desde
  `backend/calendario.py`, timeline fundido con `backend/cronologia.py` y
  pintado con `TimelineComparativo`, TDE estructurado en `tde.bloques[]`
  —**uno por equipo**: el índice es de un equipo, no del partido— con sus
  niveles venidos del skill (el backend no le pone umbrales a esa escala), y el
  pronóstico por equipo foco entra en `cadena_dtp` como apertura —el veredicto
  lo emite quien cierre el eslabón—. Un bloque nuevo del prompt necesita sitio en el parte:
  si no lo tiene, se pierde. El **reventón de la burbuja** tiene el suyo:
  Cowork lee `GET /equipos/{id}/burbujas` de los dos equipos ANTES del 1X2
  (prompt v2.5) y escribe UNA línea por equipo en `lecturaSad.reventon`; los
  números no se copian, `parte.py` los recalcula al leer en
  `lecturaSad.reventonCalculado` (familia total, uno por lado). En el TDE
  **el índice es un número (`ie`/`ise`) y el nivel una etiqueta
  (`ieNivel`/`iseNivel`)**: un número en el nivel se RECHAZA y se rescata en
  `ie`, no se tira en silencio (pasó en diez partes). El `dt` del parte es
  `{nombre, desde|meses}`: la antigüedad la calcula `parte._dt_equipo`
  (declarado → `desde` → DT de la base con el mismo apellido → `null`, NUNCA
  0), «sin establecer» es el canónico de DT desconocido y una oración como
  nombre se rechaza. La procedencia del once es dato: `POST …/xi` no pisa un
  lado de la ficha sin `reemplazar: true` (vuelve en `xiConservados`) y
  `xi/auto` reemplaza lo manual cuando la ficha llega (`reemplazados`).
- **Los equipos de interés se siguen enteros**: quien juega la edición
  vigente de un torneo internacional de clubes (`extractor.equipos_de_interes`)
  tiene TODOS sus partidos en la base aunque su liga no esté en `LIGAS`, y su
  plantel se ingesta igual. Un equipo con calendario vacío en un parte es una
  falla de esto, no «cobertura».
- **El padrón de la agenda es el de las cuotas en vivo**
  (`extractor.ligas_vivo()`, vía `_padron()` en `backend/analisis/parte.py`):
  UNA sola fuente, porque dos listas de «ligas importantes» en dos archivos se
  separan solas —y ya se separaron—. Orden: Liga 1 Perú · internacional en fase
  decisiva (de octavos, leída de `league_round`) · clásico DENTRO del padrón ·
  liga con equipo top 6 o en crisis · resto de primeras. La fase de grupos /
  fase liga internacional y las segundas divisiones quedan FUERA por defecto
  (`grupos=true` / `segundas=true` las meten, al final): un jueves de Europa
  League llenaba los cupos con partidos de relleno. Sin `fecha` la agenda es
  «desde ahora y por 24 h», a la hora que se corra (no «mañana en UTC»), y
  `liga=<texto>` acota por país o nombre. Las copas nacionales quedan fuera a
  propósito. El clásico se evalúa DESPUÉS del padrón: mirarlo antes hacía que
  un mismo torneo entrara o no según se activara el etiquetador de derbis. Un
  descarte viaja SIEMPRE con su motivo y el id de la liga, y la respuesta trae
  `corte` con lo que quedó fuera SOLO por el `limite` —que es lo que hace que
  una jornada entera de LaLiga no aparezca sin que nadie entienda por qué—.
  Un equipo que figura en DOS partidos a menos de 20 h viaja con `conflicto`
  (uno de los dos fixtures es un aplazado sin marcar o un duplicado); si
  chocan los dos equipos del fixture, se descarta con ese motivo. Un
  aplazado/cancelado (`PST`/`CANC`/`ABD`) se descarta como tal. La tanda de
  penales se guarda con tipo `Shootout`, nunca como `Goal`.
- **El once se cierra solo** (`POST /analisis/cowork/xi/auto`): cerrar el
  bloque F es cruzar listas de nombres y aplicar pesos de rol, no un análisis.
  Seis partidos que arrancan juntos son seis cierres de milisegundos, no una
  carrera de 30 minutos. Idempotente, sin tokens ni cuota; `sinFichaTodavia`
  son los del pantallazo a mano y `conConflicto` los que NO se fuerzan;
  `nuncaVaALlegar` son partidos YA TERMINADOS cuya liga no da alineaciones
  —ahí reintentar no sirve y el pantallazo es el procedimiento, no la
  excepción—. La
  agenda trae `porHacer`/`yaHechos` para **retomar donde se cortó** una corrida
  que se quedó sin tokens.
- **Vigilancia del pipeline**: `GET /analisis/cowork/latido` +
  `LatidoCowork` en la pantalla de Partidos. Una tubería automática sin
  vigilancia no falla con ruido, falla callada. El **silencio cuenta como
  fallo** (cero partes en la ventana = rojo) y la cobertura se mide **contra lo
  que la agenda habría elegido**, no contra lo depositado. La banda no se pinta
  cuando todo está verde: un aviso permanente se deja de leer.
- **El tamaño de `sad.db` es la factura de Railway.** Cobra la RAM por hora
  y cuenta la caché de archivos: cada página de la base que algo lee queda en
  memoria facturada. En 09/2026 la base llegó a 30 GB y costó 61 dólares con
  la CPU en cero (`docs/DESPLIEGUE.md`). Reglas: la ingesta guarda SOLO los
  mercados que `backend/cuota_mercados.py` mapea (leer y escribir con la
  misma tabla); un `DELETE` de retención va por fixture con índice y una vez
  al día, nunca por fecha sin índice en un ciclo de un minuto; una tabla que
  crece necesita retención (`SAD_ODDS_HISTORY_DIAS`, `RETENCION_DIAS`) y
  `backend/ingesta/adelgazar.py` compacta lo acumulado. Lo pesado —ingesta,
  pipeline, backfill, backtest— corre en SUBPROCESOS para que su memoria
  vuelva al terminar; un subproceso o CLI que importe `backend.app` lleva
  `SAD_SIN_HILOS=1` para no arrancar hilos de fondo.
- **Dos tokens** (`backend/app.py`): `SAD_API_TOKEN` es la llave maestra —abre
  también lo que gasta créditos de Claude y cuota de API-Football— y
  `SAD_TOKEN_COWORK` es el acotado que se le da a Cowork: solo
  `/analisis/cowork/*` (sin DELETE) y los GET del pipeline, por LISTA DE
  PERMITIDOS. Un endpoint nuevo nace denegado para Cowork; abrirlo es
  deliberado. Nunca le des el maestro a un agente que lee contenido de fuera.
- **Jev** (`docs/JEV.md`, `backend/analisis/jev.py`): modelo System One de
  TypeSafe que devuelve valores TIPADOS (elección · puntaje · sí/no) con
  confianza, no texto. Es un CLASIFICADOR DE TEXTO, no un pronosticador: está
  calibrado contra LLMs, no contra resultados, así que no toca el motor ni nada
  calculable, y jamás el 1X2, el pronóstico ni un peso del skill. Declara que
  cuenta mal, que lee las fechas como texto y que **no trata el estado como
  hostil**: el texto de fuera viaja en `estado` y NUNCA en las instrucciones ni
  en los criterios, y su salida no dispara acciones con efectos —solo alertas
  de tipo `dato`—. Sin `TYPESAFE_API_KEY` responde simulado con confianza 0:
  el código corre pero no decide, que es lo que impide que un simulado se cuele
  como juicio en un parte. **No es determinista**: lo que responda se guarda
  SELLADO con la versión del modelo y no se rehace al leer (al revés que todo lo
  derivado). Primer uso, HECHO en sombra: el **guardrail de coherencia del
  parte** (`backend/analisis/coherencia.py`): Jev etiqueta la PROSA —notas por
  bloque, lectura del 1X2, razón del matchup, texto de reventón— y el código la
  compara con el número que Cowork declaró; se evalúa AL DEPOSITAR y viaja en
  `coherencia` del GET y en el recibo. `SAD_JEV_COHERENCIA`: `alertas` (defecto
  desde el 22/09: COHERENCIA-* a la tira con `origen: jev`, el detalle y
  `queHacer` en el recibo para que Cowork corrija o sostenga en `notas`) ·
  `sombra` (evalúa y guarda, Cowork ve solo conteos, nada a la tira: para medir
  sin sesgar) · `off`. Los códigos COHERENCIA-* son la TERCERA clase de alerta
  (`_ALERTAS_CAPTURADAS`): se descartan del depósito como las calculadas pero
  al leer se LEEN, no se recalculan. **Vigilancia**: cada evaluación queda en
  `coherencia_log` y `GET /analisis/cowork/revisor` (`parte.revisor`, tarjeta
  `RevisorDiario` en Partidos) dice, por parte, qué encontró y qué hizo Cowork
  —`corrigio` · `corrigioParte` · `sostuvo` · `sinReaccion` · `limpio` ·
  `noEvaluado`— más el costo del día; `paraMirar` son los que Cowork no
  corrigió. Sin apuestas de por medio, Cowork queda solo y el reporte del día
  es la medición; a la primera apuesta real, se re-evalúa esa decisión.
  **Segundo uso, el aprendizaje** (`backend/analisis/modo_fallo.py`): al
  cerrar un veredicto, Jev lee la prosa del lado fallado o parcial (`queP`,
  `leccion`, `reglaTocada`) y la ubica en una taxonomía CERRADA —insumo ·
  lectura_efe · tde · reventon · mercado · imprevisto · varianza · no_lo_dice—
  y dice si la lección PIDE MOVER UN NÚMERO del skill (noul: sí ≥ 0.70, no ≤
  0.30, en medio `null`). Sellado en `modo_fallo_json` al cerrar, viaja en
  `veredicto.modoFallo` (eco aceptado) y en cada `LeccionItem` (`modoFallo`,
  `proponeMoverNumero`); `porModoFallo` agrupa los fallos por causa, global y
  por skill, y `pidenMoverSinPoder` es la alarma del dossier: una lección de
  caso contaminado o en cuarentena que propone mover un peso. **No toca la
  población, ninguna métrica, el estado de la lección ni la cuarentena**: es
  el insumo de la fase D, no un juez.
- Costo de la IA: `docs/efe-dtp/COSTO_IA.md`. Lo que está en nuestra base se
  calcula, no se le pregunta al modelo — y lo calculado no se le hace copiar a
  la salida. Los bloques calculados hoy: el mapa de rivales del EFE
  (`backend/calendario.py`), los partidos del timeline (`backend/cronologia.py`)
  y los insumos del TDE que el propio skill manda tomar del motor
  (`backend/analisis/tde.py`, `GET /analisis/cowork/tde/{id}`): P1a por
  `μ_partido` contra el umbral 0.30 —es «input inviolable» y el skill prohíbe
  derivarlo del gap—, F2 por días de descanso y señal de calendario —«dato del
  motor o no es dato»— y F1 por las alineaciones ya ingestadas. Los 16
  indicadores que siguen siendo juicio viajan en `noCalculables` con su motivo;
  lo que no se puede calcular se declara, no se rellena.
- Gráficas de K: tres valores a la vista (último · últimos dos de la condición
  que se analiza, saltando los que repiten valor) vía `puntosEtiquetados` de
  `src/lib/kview.ts`. Una gráfica nueva usa ese helper, no su propia regla.
- **Reventón de la burbuja** (`docs/REVENTON.md`): cuándo la K de resultado
  suele volver a cero, calculado de la historia del equipo en
  `backend/analisis/burbuja.py` (`GET /equipos/{id}/burbujas`, abierto a
  Cowork, 0 tokens) con espejo TS en `src/lib/burbuja.ts` para el mock; los
  dos corren sobre `scripts/casos_burbuja.json`, y una regla que cambia en un
  lado sin el otro tumba un test. Es GUÍA, no probabilidad: por signo, media ·
  mediana · moda de la K pico, los partidos y el nivel del rival que reventó
  cada burbuja; la abierta hoy se compara con eso y con el próximo rival. Los
  puntos del riesgo están CALIBRADOS con el backtest real (`--calibrar`,
  §8 del doc, 171k burbujas): la K NO puntúa —estar por encima de la K con la
  que suele reventar no adelanta el reventón—, la racha ≥ mediana suma 1 y el
  rival frente a la mediana con la que revienta suma 3 · 5 · 7 (zona · fuerte
  · muy fuerte, en la dirección del riesgo). Manda la familia total: la regla
  del nivel (alto/bajo → globales, medio → específicas) no se confirmó y viaja
  en `mandan.reglaNivel` como dato. Mover un peso se hace con el backtest a la
  vista, en los dos lados y en los vectores dorados. OJO: `/constantes` sirve
  el nivel del rival CONTINUO recuperado de las q (`_nivel_rival_exacto`);
  `processed_matches.nivel_rival` es el bin de ML y no es ese campo. Vista
  «al día del partido»: `antesDe=<fixtureId>` en `/constantes`, `/niveles` y
  `/burbujas` corta la historia ESTRICTAMENTE antes de ese partido y lo usa
  como próximo (§9 del doc); la sección Burbujas lo hace sola para todo
  partido finalizado, sin plantilla de hoy (estabilidad sin dato). La
  estabilidad (DT, ventana, bajas) mueve la CONFIANZA, nunca el riesgo;
  dueños/organización van en `sinDato`. Sin reventones previos del signo →
  `sin base`, jamás un número. **Alerta de extremo** (`familia.extremo`,
  §10 del doc): la burbuja en su máximo histórico (K o racha récord sobre N
  partidos) se grita APARTE del riesgo —en rojo en la tarjeta, como alerta
  `K-EXTREMO` en la tira del parte y como regla dura del prompt—; no mueve
  los puntos (la K no puntúa) pero sí cuánto se carga: es prudencia, no
  probabilidad, y Cowork no se la puede saltar. Un escalón más abajo,
  `extremo.cerca` (§10.1): sin récord pero por encima del 90 % de sus
  reventones del signo → caja ámbar y alerta `K-CERCA-EXTREMO` (tipo `dato`);
  `activo` sigue siendo solo el récord. Las K de goles quedan fuera
  a propósito hasta que se decida sumarlas. **Por período** (§10-bis):
  `historialPorPeriodo` repite las medidas acotadas a temporada · año · DT
  vigente · últimos 20, filtrando por la fecha del reventón sobre los mismos
  episodios; la global sigue mandando en el riesgo (es la calibrada) y un
  período sin corte viaja con `sinDato`. Espejo TS y vectores dorados. En la
  gráfica de K la referencia punteada es elegible por período (`kPeriodo`,
  `PeriodoReventon`, `src/lib/reventonRef.ts`) con una línea vertical donde
  arranca el período; sin base se dice, no se vuelve a la global callado.
- Cuotas K (§3.8): las barras SIEMPRE vía `RachasCuotas` y su botonera
  `ControlesCuotas` (condición · mercado 1X2/Doble op./Ambos · ventana); cada
  mercado dibuja solo los partidos con SU cuota capturada — sin dato, la
  gráfica sale vacía, nunca rellenada.
- Git: trabajar en rama + merge; push a GitHub solo como respaldo (no editar
  "en la nube"). Respaldo alternativo: `git bundle create respaldo.bundle --all`.

## Estado actual

Hecho: 4 secciones + Partidos (pantalla inicial) + páginas de Equipo y de Liga
(con temporadas pasadas y tabla por fase —Apertura/Clausura/… derivada de
`league_round`, cada torneo corto arranca de cero, más la tabla del año) +
buscador inteligente; H2H real en Estadísticas;
burbujas = gráfica de líneas de picos K con distinción de torneos
internacionales; gap §5 en Estadísticas con μ v2 recalibrada contra datos
reales (backtest muestreado, ver MOTOR_SAD_EXTRACCION.md §5); backend
completo; CI con dos jobs. Probado end-to-end con datos reales del usuario
(Mundial 2026 incluido). Capa de jugadores (docs/JUGADORES.md, capa 1):
ingesta de plantillas/bajas/traspasos/DT, indicadores por-90 con shrinkage +
HHI + confianza A/B/C, sección Plantilla en Equipo, ficha de partido
(/fixtures/{id}/ficha) y cruce con los análisis EFE/timeline del backend.
Camino Cowork (docs/COWORK.md): agenda priorizada del día, depósito del parte,
bloque F calculado en local y cierre del once desde la ficha o a mano.

## Deuda declarada (lo que se sabe roto o pendiente)

Está acá y no en la cabeza de nadie porque un pendiente que solo existe en una
conversación se pierde en la siguiente.

1. **El frontend recibe un token de API.** `VITE_API_KEY` viaja al bundle del
   navegador, así que cualquiera que abra la web tiene la llave que usa la app.
   Arreglo: rotar `SAD_API_TOKEN`, sacar `VITE_API_KEY` de Vercel y dejar de
   mandarle cualquier token al cliente — un proxy en el frontend, o un tercer
   token de SOLO LECTURA que no abra nada que gaste. Aplazado a conciencia por
   el usuario mientras se probaba la tubería; ya está probada.
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
3. **Colisión de nombres F3/F4.** El bloque F del EFE tiene F3 y F4, y el TDE
   tiene los suyos. La instrucción «no mandes F3 ni F4» (que habla del EFE) se
   puede leer al revés. Renombrar desalinea el prompt del skill, así que por
   ahora está declarado y no tocado.
4. **Fases D y A del bucle de aprendizaje**, en `docs/APRENDIZAJE.md`: el
   dossier de revisión y los antecedentes. La C ya está.
5. **Onces de ligas sin cobertura.** Primera B de Colombia y Primera de Uruguay
   no dan alineaciones por API-Football: para esas, el pantallazo a mano es el
   procedimiento. Salen en `nuncaVaALlegar` con su liga.
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
     esos equipos les aparezca el calendario y el plantel.
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
     siguen pendientes.
   - **Reventón**: no hay backtest por período (la global sigue mandando en
     el riesgo, a propósito); «fase» (Apertura/Clausura) no está como período
     porque no vive en las filas del motor; las K de goles siguen fuera. Con
     datos reales, `temporada` en Europa es la 2025/26 entera y en Sudamérica
     el año natural: por eso viajan las dos.
   - **Sin cambios y aún abiertos**: deuda 1 (token en el bundle), 3 (F3/F4),
     5 (onces de ligas sin cobertura), el umbral de `Missing Fixture` a
     recalibrar con casos, y ver en la próxima corrida real que a los equipos
     de interés (Beşiktaş y compañía) les aparezcan calendario y plantel.

## Siguientes pasos (en orden)

1. **Desplegar**: Railway (backend + volumen + ingesta programada) y Vercel
   (frontend) — guía paso a paso en `docs/DESPLIEGUE.md`.
2. **Familias nuevas de burbujas** — spec completa en `docs/ROADMAP_BURBUJAS.md`:
   `k_dc`, márgenes (±1/2/3+ goles) y k_cuota_* sobre cuotas prepartido (1X2 y
   doble oportunidad, con su regla de huecos) hechos; siguen
   `k_cuota_favorito`/`k_cuota_tapado`.
3. Backend: xG/posesión desde estadísticas por partido.
4. Historial de cuotas por fixture para que la gráfica de movimiento sea real —
   plan completo por fases (historial → día de partido → en vivo) en
   `docs/EXTRACCION_TIEMPO_REAL.md`.
5. **DTP** (Diagnóstico Táctico de Partido) — diseño en
   `docs/efe-dtp/DTP_DISENO.md`. **Fases A y B hechas**: ficha de partido
   (alineaciones con `grid`→carriles, eventos con asistente y stats en
   `/fixtures/{id}/ficha.tactica`) y motor (`POST /analisis/dtp` por equipo
   foco, cadena rodante en `cadena_dtp`, `GET /equipos/{id}/cadena`). Queda la
   fase C **también hecha**: pizarra en la sección Análisis (toggle de equipo
   foco) y cadena en la página de Equipo. Queda correr
   `ficha_partido --estado` tras la primera corrida real: de si el plan sirve
   `grid` depende que M2 hable de carriles reales.
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
   (Wilson 95 %), no por el punto. Faltan D (dossier cada
   4 fallos, que ABRE la revisión pero no autoriza mover nada) y A
   (antecedentes). La app nunca mueve un peso de un skill por su cuenta.
   Snapshot de los skills en `docs/skills/`.
7. Fase nube completa cuando toque: `docs/SERVICIOS_EXTERNOS.md` (Postgres).
