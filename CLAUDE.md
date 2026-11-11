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
npm run test:familias             # otras burbujas (DC, márgenes, goles): espejo TS vs vectores dorados (python -m backend.test_familias)
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
python -m backend.test_eliminatoria # quién pasó una llave (penales, global, prórroga): ficha, timeline, veredicto y ELIMINATORIA-AL-REVES
python -m backend.test_sanciones  # sancionados de la base (roja, doble amarilla, ciclo de amarillas) y el escaneo preventivo
python -m backend.test_ventana_nivel # de qué partidos está hecho el nivel del motor (amistosos, internacionales) y la fiabilidad de μ que baja con 3+ amistosos (860)
python -m backend.test_identidad  # quién es quién (jugador y DT): la regla única de backend/identidad.py, con cada caso real
python -m backend.test_arquitectura # el escaneo preventivo del CÓDIGO: cada clase de falla de docs/FALLAS.md con su guardia (identidad en un lugar, tests en CI, contrato, excepts con motivo, rutas que existen)
python -m backend.test_preflight  # chequeo previo del EFE: qué va a costar antes de gastar
python -m backend.test_cowork    # parte de Cowork: bloque F calculado y cruce del once
python -m backend.test_burbuja   # reventón de burbuja: mismos vectores dorados que el TS
python -m backend.test_jev       # adaptador de Jev (System One): sin clave corre simulado y no decide
python -m backend.test_coherencia # guardrail semántico del parte (Jev): etiqueta la prosa, el código compara con el número
python -m backend.test_simulacion # simulación de apuesta: plana (control), Kelly entero/½/¼ y martingala desde el 28/10/2026, con la versión de cada skill
python -m backend.test_semaforo   # una marca de la pantalla de Simulación para el usuario (11/11/2026; la regla vive en docs/METODO_APUESTA.md y no entra al parte)
python -m backend.contacto        # criterio de contacto (acierto tras 3 fallos seguidos) desde la API con el token de Cowork; lo corre la rutina del lunes (docs/METODO_APUESTA.md)
python -m backend.test_velocidad   # Aprendizaje y Simulación con caché: mismos números que sin caché, y solo se rehace lo que cambió (10/11/2026)
python -m backend.test_modo_fallo # modo de fallo del veredicto (Jev): etiqueta para el dossier, no toca población ni métricas
python -m backend.backtest_burbuja --padron --calibrar # backtest del reventón en las ligas importantes: tasa por riesgo, lift por señal, regla del nivel, por liga, y la logística que propone los puntos (--horizonte/--liga/--muestra/--json; en el servidor: GET /analisis/burbujas/backtest?calibrar=true, maestro)
python -m backend.test_backtest_burbuja # anti-fuga y conteos del backtest, sobre la demo
python -m backend.backtest_burbuja_1x2 --padron # ¿la burbuja / las K mejoran el 1X2 del motor? M0-M6, corte temporal 80/20 y bootstrap, y el MERCADO sobre los mismos partidos (REVENTON §13; guarda .backtest_1x2.json)
python -m backend.test_backtest_1x2  # el método detecta un efecto real y no inventa uno (sintéticos + demo)
python -m backend.backtest_familias --padron # ¿las burbujas de doble oportunidad, márgenes (1+…4+) y goles predicen el partido siguiente mejor que la frecuencia del equipo? (REVENTON §15; --desde-json para historias bajadas de /constantes)
python -m backend.test_backtest_familias  # detecta un reventón plantado y no inventa uno
python -m backend.backtest_unxdos_motor --padron # el 1X2 del motor desde μ: logística calibrada contra frecuencia y contra el Poisson sobre μ (MOTOR §5.6; --desde-dir para historias bajadas de /constantes y /niveles)
python -m backend.seed_demo       # DBs demo con esquemas reales (./demo_data)
python -m backend.backtest_gap    # backtest §5 muestreado (--muestra/--liga/--horizonte/--calibrar/--por-liga)
python -m backend.fase0_ligas      # ¿qué ligas sumar? inventario de datos, μ por liga y reventón por liga, solo lee (29/10/2026; en Railway: nohup … > $SAD_DATA_DIR/fase0.log 2>&1 &, resumen en $SAD_DATA_DIR/fase0/resumen.txt; va en backend/ porque la imagen solo copia esa carpeta)
python -m backend.backtest_goles --padron # ¿las constantes de goles ACOTAN los goles? intervalo de dos goles, marcador acotado, mercado de más/menos 2,5 y ambos marcan, y si el marcador se repite (REVENTON §17, 30/10/2026) · test_backtest_goles
python -m backend.backtest_nivel_ventana --padron --fixture 1584455 # ¿el 1X2 del motor mejora con el nivel SIN amistosos o sin internacionales? actual vs variantes, por subconjunto y contra el mercado (860; --json; medido 30/10: no) · test_backtest_nivel_ventana
python -m backend.backtest_localia_liga --padron --fixture 1584455 # ¿el 1X2 del motor mejora con la LOCALÍA POR LIGA (encogida a la de todas) en vez de la global 0,382? todos, por liga y contra el mercado, y la tabla lista para copiar (860; --json; medido 30/10: −0,0017 en todos, nada con cuota: no) · test_backtest_localia_liga
python -m backend.backtest_forma --desde-dir carpeta  # ¿la forma de 5 SIN amistosos mejora el gap? (MOTOR §5; medido 26/10: no) · test_backtest_forma
python -m backend.backtest_culebra --api --cache carpeta # ley anticulebras: ¿tras locales/favoritos ganadores de la misma liga-día, el siguiente empata o cae más? (DEUDA 24; medido 07/11: no; --api baja con el token de Cowork, sin --api rehace lo bajado) · test_backtest_culebra

# ingesta (dueña de los datos; el backend HTTP sigue siendo de solo lectura)
python -m backend.ingesta.extractor --probar    # 1 request de prueba (API_FOOTBALL_KEY en .env)
python -m backend.ingesta.extractor --buscar "Copa Chile"  # descubrir IDs de torneos nuevos
python -m backend.ingesta.extractor             # fixtures hoy−3d..+10d (por FECHA, todas las temporadas) + cuotas NS (tope auto por plan)
python -m backend.ingesta.diagnostico --dia 2026-05-31 --api  # auditar huecos (NS/TBD vencidos) y contrastar un día con la API
python -m backend.ingesta.extractor --ventana-horas 6  # refresco ligero: solo cuotas de NS próximos
python -m backend.ingesta.jugadores             # plantillas/bajas/traspasos/DT de equipos con NS próximos (docs/JUGADORES.md)
python -m backend.ingesta.jugadores --solo-dt   # rehacer SOLO el DT vigente (1 request/equipo, sin TTL); en Railway: SAD_JUGADORES_SOLO_DT=1 una corrida
python -m backend.ingesta.jugadores --reintentar-vacios # re-pide YA los equipos sellados «sin datos» (antes del 24/09 un error de la API se sellaba así 30 días)
python -m backend.ingesta.jugadores --sondear 566 # qué devuelve la API de jugadores para un equipo (vigente, anterior, squads; 3 requests, no guarda)
python -m backend.ingesta.jugadores --dt-agenda # DT fresco de los que juegan en <= 2 días: alineación del último partido + /coachs si está viejo (corre en la corrida diaria)
python -m backend.ingesta.en_vivo               # 1 ciclo en vivo: marcador/minuto + odds_live (WAL)
python -m backend.ingesta.diag_vivo --hoy       # por qué un partido no tiene cuotas en juego (--fixture N, --api)
python -m backend.ingesta.diag_vivo --cobertura # qué ligas NO dan cuotas en vivo: capturados/jugados por liga, últimos 21 días (0 requests)
python -m backend.ingesta.diagnostico --interes # equipos de interés (torneos internacionales): ¿calendario, plantel y DT? (0 requests)
python -m backend.ingesta.ficha_partido        # alineaciones+eventos+stats de los partidos anteriores (3 req c/u)
python -m backend.ingesta.ficha_partido --estado  # qué ficha hay capturada y si trae grid/xG (0 requests)
python -m backend.analisis.despensa_bulk --listar  # despensa del repo: qué hay y qué edad tiene
python -m backend.ingesta.adelgazar [--aplicar]  # sad.db ($SAD_DATA_DIR o --db): borra mercados que nadie lee + retención + VACUUM (sin --aplicar solo mide); en Railway con SAD_ADELGAZAR=1 (la consola web mata el proceso)
python -m backend.ingesta.pipeline --out .      # regenera levels/constants/discreto desde sad.db (el mismo partido con dos ids entra una vez; --duplicados los lista)
python -m backend.ingesta.test_paridad          # test dorado vs DBs del pipeline viejo
python -m backend.ingesta.test_pipeline         # el pipeline rehace las derivadas en UNA transacción: quien lee nunca ve «no such table»
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

## Reglas del proyecto (resumen operativo)

**El texto entero de cada regla, con su caso y sus mediciones, está en
`docs/REGLAS.md`** (sacado de acá el 11/11/2026, incidencia 1377: este archivo
se carga en cada paso de cada agente). Leé la sección del área en
`docs/REGLAS.md` ANTES de tocar ese código, clasificar una incidencia de esa
área o revisar un skill. Acá queda lo que hay que hacer.

- **Las `.db` jamás se commitean**. `backend/ingesta/` es la única capa que
  escribe datos (extractor → sad.db, pipeline → derivadas). La clave de
  API-Football vive en `.env`/env vars, jamás hardcodeada ni con prefijo VITE_.
- **Contrato primero**: un cambio de API va a `docs/openapi.yaml`, luego
  backend + `src/api/types.ts` + ambos datasources (mock y http) + tests.
- **La matemática del motor es sagrada**: se valida contra
  `docs/MOTOR_SAD_EXTRACCION.md` y `scripts/test-motor.ts`. Números calibrados
  (puntos del reventón, umbrales, pesos de skills) solo con el backtest a la
  vista, en los dos lados (Python y TS) y en los vectores dorados.
- **Despensa del EFE**: campo sin fuente va VACÍO; `investigado_en` es la fecha
  real (`docs/DESPENSA_DESKTOP.md`).
- **UI**: inline styles con las variables del tema, números tabulares, todo en
  español. Teléfono: grilla de una columna = `minmax(0,1fr)`, botonera con
  `flexWrap`, y `scripts/audit-movil.mjs` a 360 y 390 px antes de dar por bueno
  un layout. Componentes ÚNICOS: `TablaPosiciones` (tabla con sus fases),
  `CalendarioSad` sobre `/equipos/{id}/calendario` (etiquetas desde
  `backend/calendario.py`), `RachasCuotas` + `ControlesCuotas` (sin cuota, la
  gráfica sale vacía), `puntosEtiquetados` de `src/lib/kview.ts` para toda
  gráfica de K, márgenes = sequía (`sequiaMargen`).
- **Parte de Cowork** (`docs/COWORK.md`, hoy lo escribe la corrida de Claude
  Code): el parte NO trae nada calculable —se recalcula en
  `backend/analisis/parte.py`/`bloque_f.py` y se ignora si llega—. Un bloque
  sin puntuar no es un cero (`declarado`; sin sub-scores, `porcentaje: null`).
  El POST reemplaza el parte entero y lo perdido sale en `perdido`; el
  veredicto acepta el eco de su GET y `cerradoEn` no se re-sella. Bloque F:
  `POST …/xi` o `xi/auto` (un once con < 7 nombres casados no cierra; no pisa un
  lado sin `reemplazar`). TDE uno por equipo, índice número / nivel etiqueta.
  `dt` = `{nombre, desde|meses}` (nunca 0; `dt.banco` para un DT ausente).
  Un bloque nuevo del prompt necesita su sitio en el parte.
- **Equipos de interés**: quien juega un torneo internacional de clubes se
  sigue entero (todos sus partidos y plantel) aunque su liga no esté en `LIGAS`.
- **Agenda**: el padrón es UNO, `extractor.ligas_vivo()` (vía `_padron()`); el
  orden, las copas medidas (prioridad 8), lo que queda fuera por defecto, el
  `corte` por `limite` y los descartes con motivo están en `docs/REGLAS.md`.
- **Vigilancia**: `latido` (el silencio cuenta como fallo; cobertura contra lo
  que la agenda habría elegido), incidencias depositadas por cada corrida y el
  mantenimiento que las verifica, agrupa por CAUSA y arregla la CLASE con un PR
  por grupo, fuera de las zonas sagradas. Resuelta = en producción (`/health` →
  `commit`).
- **`sad.db` es la factura de Railway**: la ingesta guarda solo los mercados de
  `backend/cuota_mercados.py`; retención por fixture con índice, una vez al
  día; lo pesado en SUBPROCESOS y con `SAD_SIN_HILOS=1` si importa `backend.app`.
- **Tres tokens**: `SAD_API_TOKEN` (maestra, nunca a un agente),
  `SAD_TOKEN_COWORK` (lista de permitidos: un endpoint nuevo nace denegado) y
  `SAD_TOKEN_WEB` (solo lee; lo que escribe va en modo administrador 🔑).
- **Jev** (`docs/JEV.md`): clasificador de TEXTO, nunca pronosticador ni juez de
  números; el texto de fuera va en `estado`; sin clave responde simulado con
  confianza 0; lo que responde se guarda SELLADO. Usos: coherencia del parte
  (`SAD_JEV_COHERENCIA`) y modo de fallo del veredicto (no toca métricas).
- **Skills**: dan narrativa y números (EFE %, IE/ISE, matriz); no se los juzga
  por ganarle al mercado (el 1X2 se mide aparte). La matriz va estructurada y
  el recibo avisa si se aparta > 5 puntos del 1X2.
- **Costo de la IA** (`docs/efe-dtp/COSTO_IA.md`): lo que está en la base se
  calcula (calendario, cronología, insumos del TDE), no se le pregunta al
  modelo, y lo que no se puede calcular se declara en `noCalculables`.
- **Lo que sale de la base, no del marcador ni de la API sola**: sancionados
  (`backend/sanciones.py`, la hoja manda), quién pasó una llave
  (`backend/eliminatoria.py`, `avanza` null antes que adivinado), de qué está
  hecho el nivel (`ventanaNivel`, `fiabilidadMu`; la fórmula NO se toca).
- **Identidad en UN archivo**: `backend/identidad.py` decide si dos nombres son
  la misma persona; un caso nuevo se arregla ahí con su test en
  `backend/test_identidad.py`.
- **Escaneo preventivo**: del código (`docs/FALLAS.md` +
  `backend/test_arquitectura.py`, en CI) y de los datos
  (`backend/analisis/escaneo.py`, `CHEQUEOS`). El mantenimiento arregla la
  clase y deja la guardia; la cola de incidencias no puede crecer.
- **Copas nacionales**: se analizan pero quedan fuera de toda métrica de
  Aprendizaje, del valor contra el mercado y de la simulación
  (`escala.copas_nacionales`).
- **Rol contra el grid y duelos del M2** piden rehacer el DTP
  (`dtp_cowork.ROLES_GRID_REHACE`).
- **Simulación de apuesta** (`backend/analisis/simulacion.py`,
  `docs/METODO_APUESTA.md`): el método proporcional va primero; cuenta desde el
  28/10/2026; con cada versión nueva de un skill, anotar la hora en
  `SUBIDA_VERSION`. La demo se GENERA del backend. No se abre al token de Cowork.
- **Reventón de la burbuja** (`docs/REVENTON.md`): `backend/analisis/burbuja.py`
  con espejo `src/lib/burbuja.ts` sobre `scripts/casos_burbuja.json` (una regla
  cambiada en un solo lado tumba un test); GUÍA, no probabilidad; puntos
  calibrados; extremo y cerca-de-extremo se gritan aparte; los amistosos
  cuentan; las otras familias (`familias.py`/`familias.ts`) son narrativa.
  `separacionLiga` dice cuánto pesar la guía; no mueve puntos.
- **DTP por Cowork** (`backend/analisis/dtp_cowork.py`): insumos de la ficha,
  `dtp.bloques[]` estructurado; la clase y `c1Tde` las calcula el backend; la
  apertura entra a la cadena una vez; el TDE hereda del DTP.
- **Git**: trabajar en rama + merge; push solo como respaldo.

## Estado actual

Lo hecho, sección por sección: `docs/REGLAS.md` (al final).

## Deuda, historia y pendientes → `docs/DEUDA.md`

Lo que se sabe roto o pendiente, la historia de cada decisión (puntos 1 a 19:
DT de la base, cuotas, plan de API-Football, sesiones fijas y rutinas con sus
ids, revisiones de skills, decisiones del usuario) y los siguientes pasos
viven en `docs/DEUDA.md`. Se sacó de acá el 03/11/2026 porque este archivo se
carga en cada paso de cada agente y la historia no hace falta para analizar un
partido. **Leelo antes de** clasificar una incidencia del mantenimiento,
revisar un skill, tocar las rutinas o retomar un pendiente del usuario; y un
pendiente nuevo se anota allá, no acá.
