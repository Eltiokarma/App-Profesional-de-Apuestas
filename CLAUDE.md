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
python -m backend.ingesta.en_vivo               # 1 ciclo en vivo: marcador/minuto + odds_live (WAL)
python -m backend.ingesta.diag_vivo --hoy       # por qué un partido no tiene cuotas en juego (--fixture N, --api)
python -m backend.ingesta.ficha_partido        # alineaciones+eventos+stats de los partidos anteriores (3 req c/u)
python -m backend.ingesta.ficha_partido --estado  # qué ficha hay capturada y si trae grid/xG (0 requests)
python -m backend.analisis.despensa_bulk --listar  # despensa del repo: qué hay y qué edad tiene
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
  (prompt v2.4) y escribe UNA línea por equipo en `lecturaSad.reventon`; los
  números no se copian, `parte.py` los recalcula al leer en
  `lecturaSad.reventonCalculado` (familia total, uno por lado).
- **El padrón de la agenda es el de las cuotas en vivo**
  (`extractor.ligas_vivo()`, vía `_padron()` en `backend/analisis/parte.py`):
  UNA sola fuente, porque dos listas de «ligas importantes» en dos archivos se
  separan solas —y ya se separaron—. Orden: Liga 1 Perú · internacional en fase
  decisiva (de octavos, leída de `league_round`) · clásico DENTRO del padrón ·
  liga con equipo top 6 o en crisis · internacional en grupos · resto de
  primeras · segundas divisiones. Las copas nacionales quedan fuera a
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
- **Dos tokens** (`backend/app.py`): `SAD_API_TOKEN` es la llave maestra —abre
  también lo que gasta créditos de Claude y cuota de API-Football— y
  `SAD_TOKEN_COWORK` es el acotado que se le da a Cowork: solo
  `/analisis/cowork/*` (sin DELETE) y los GET del pipeline, por LISTA DE
  PERMITIDOS. Un endpoint nuevo nace denegado para Cowork; abrirlo es
  deliberado. Nunca le des el maestro a un agente que lee contenido de fuera.
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
  `sin base`, jamás un número. Las K de goles quedan fuera a propósito hasta
  que se decida sumarlas.
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
2. **Los DT de la ficha están viejos.** En la corrida del 15/09, seis de ocho
   entrenadores no coincidían con la realidad (un DT figuraba dirigiendo al
   equipo que enfrenta). Eso decide el bloque A y dispara o no T.54. Se arregla
   corriendo `python -m backend.ingesta.jugadores`, que gasta cuota de
   API-Football: no se puede hacer desde una sesión de análisis. Mientras
   tanto el prompt (v2.4) obliga a confirmar el DT en prensa antes de puntuar
   el bloque A, y a dejar A fuera si no se puede establecer.
3. **Colisión de nombres F3/F4.** El bloque F del EFE tiene F3 y F4, y el TDE
   tiene los suyos. La instrucción «no mandes F3 ni F4» (que habla del EFE) se
   puede leer al revés. Renombrar desalinea el prompt del skill, así que por
   ahora está declarado y no tocado.
4. **Fases D y A del bucle de aprendizaje**, en `docs/APRENDIZAJE.md`: el
   dossier de revisión y los antecedentes. La C ya está.
5. **Onces de ligas sin cobertura.** Primera B de Colombia y Primera de Uruguay
   no dan alineaciones por API-Football: para esas, el pantallazo a mano es el
   procedimiento. Salen en `nuncaVaALlegar` con su liga.

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
   ventana del TDE, los goles con su minuto— y se RECALCULA al leer; Cowork
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
   fija rúbrica); el sesgo de atribución se declara antes de los conteos; y
   mover estados NO está abierto al token de Cowork: el agente lee sus
   lecciones, declarar aplicada la suya es del usuario. Faltan D (dossier cada
   4 fallos, que ABRE la revisión pero no autoriza mover nada) y A
   (antecedentes). La app nunca mueve un peso de un skill por su cuenta.
   Snapshot de los skills en `docs/skills/`.
7. Fase nube completa cuando toque: `docs/SERVICIOS_EXTERNOS.md` (Postgres).
