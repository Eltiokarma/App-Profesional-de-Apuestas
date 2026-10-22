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
python -m backend.test_preflight  # chequeo previo del EFE: qué va a costar antes de gastar
python -m backend.test_cowork    # parte de Cowork: bloque F calculado y cruce del once
python -m backend.test_burbuja   # reventón de burbuja: mismos vectores dorados que el TS
python -m backend.test_jev       # adaptador de Jev (System One): sin clave corre simulado y no decide
python -m backend.test_coherencia # guardrail semántico del parte (Jev): etiqueta la prosa, el código compara con el número
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
  nombre se rechaza. Un DT suspendido o ausente, o un banco de la API que la
  prensa desmiente, va en `dt.banco` `{motivo, nombre, fuente}` (20/10/2026):
  ese lado no cae en cuarentena automática por DT equivocado. La procedencia del once es dato: `POST …/xi` no pisa un
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
  liga con equipo top 6 o en crisis —y la fase liga de la CHAMPIONS, que entra
  sola desde el 14/10/2026— · resto de primeras. La fase de grupos / fase liga
  de los demás torneos internacionales y las segundas divisiones quedan FUERA por defecto
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
  **Lo roto se deposita y se arregla solo** (18/10/2026, pedido del usuario:
  la API siempre puede fallar y aparecen errores nuevos): cada corrida manda
  su «Roto o a mirar» a `POST /analisis/cowork/incidencias`
  (`backend/analisis/incidencias.py`; la misma abierta suma `veces`, una
  resuelta que reaparece entra nueva) y la rutina de **mantenimiento**
  (`corrida-sad`, modo `mantenimiento`) las verifica contra los datos, las
  clasifica (`dato_api` · `por_diseno` · `usuario` · `descartada`) o las
  arregla con un test —AGRUPADAS POR CAUSA, hasta 3 grupos de código por
  corrida y un PR por grupo; lo que no es código se clasifica entero en la
  misma corrida (22/10/2026: la cola llegó a 88 arreglando de a 8 sueltas)—,
  valida TODO y mergea solo en verde y fuera de las zonas
  sagradas (motor, números calibrados, skills, tokens, datos, cuarentenas,
  Railway): eso va a `usuario` con la propuesta. El latido cuenta las
  abiertas (`incidencias`) y pasa a ámbar con alguna que bloquea.
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
- **Tres tokens** (`backend/app.py`): `SAD_API_TOKEN` es la llave maestra —abre
  también lo que gasta créditos de Claude y cuota de API-Football— y
  `SAD_TOKEN_COWORK` es el acotado que se le da a Cowork: solo
  `/analisis/cowork/*` (sin DELETE) y los GET del pipeline, por LISTA DE
  PERMITIDOS. Un endpoint nuevo nace denegado para Cowork; abrirlo es
  deliberado. Nunca le des el maestro a un agente que lee contenido de fuera.
  `SAD_TOKEN_WEB` es el de la web (`VITE_API_KEY`, viaja en el bundle): SOLO
  LEE (todo GET menos el backtest; la plantilla no lanza ingesta con él). Lo
  que escribe o gasta lo hace la web en **modo administrador** (🔑,
  `src/lib/admin.ts` + `BotonAdmin`): la maestra se pega una vez y queda solo
  en ese navegador, y el cliente la usa en vez del token de lectura.
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
- **Los skills dan narrativa y analítica, números incluidos** (usuario,
  15/10/2026, corregido el mismo día para que no fuera tajante). EFE, TDE, DTP,
  la matriz y la lectura SAD cuentan CÓMO puede darse el partido y alimentan el
  análisis posterior con IA (autopsias, lecciones, antecedentes), y sus números
  —porcentaje del EFE, IE/ISE, riesgo, probabilidades de la matriz— se quedan y
  se muestran. Lo que NO se hace es juzgar a un skill por si su número le gana
  al mercado: el 1X2 se mide aparte (`pronostico.probabilidades`, Brier). La
  **matriz de escenarios** va estructurada en el parte (`matriz`: por equipo,
  `ganar`/`empatar`/`perder` con las filas del skill v2.0 y la `probabilidad`
  estimada de cada escenario); si esa probabilidad se aparta más de 5 puntos del
  1X2 del pronóstico el recibo lo AVISA (`matrizVsPronostico`), no la rechaza.
  Se pinta en Lectura (`MatrizEscenarios`) y el veredicto dice qué escenario
  jugó cada lado (`objetivo.matriz`) y si lo escrito apareció
  (`porLado.*.escenario`), como observación sin tasa. Auditoría del 15/10: en la
  corrida se había achatado a tres filas con porcentajes; sobre 36 casos ciegos
  la estimación quedó a la par del mercado (Brier 0,589 contra 0,603, n chico).
  El «checklist de 9 puntos» y la «Ficha de Mecanismo» que cita el skill no
  existen en disco.
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
  recalibrados el 14/10/2026 con 173.615 observaciones y el rival medido
  ANTES del partido, §13.2 del doc): la K
  NO puntúa —estar por encima de la K con la que suele reventar no adelanta
  el reventón—, la racha ≥ mediana suma 1, el rival frente a la mediana con
  la que revienta suma 0 · 1 · 2 (zona · fuerte · muy fuerte, en la dirección
  del riesgo), la racha hecha en la condición CONTRARIA a la del próximo suma
  1 (`actual.contramano`), y la diferencia de nivel A FAVOR de que la racha
  siga —el favorito con racha +, el débil con racha −— RESTA 1 · 3 (≥ 0.5 ·
  ≥ 1.0, `rival.aFavor`/`rival.favorito`). Cortes: bajo < 0 · medio 0 ·
  alto 1-2 · muy alto ≥ 3 (AUC 0.615: guía, separa ~45 % de ~72 %). Lo que los 52 estudios de reventones creyeron ver
  y el backtest de las lecciones (`--lecciones`, §12) NO sostuvo —récord,
  inflada, parón, burbujas enfrentadas, forma del arquero— no puntúa; los
  candidatos a estudiar salen AL AZAR, no por tamaño. Manda la familia total: la regla
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
  la K de la CONDICIÓN de hoy en su extremo, con la total sin él, da
  `K-EXTREMO-CONDICION` (tipo `dato`, 20/10/2026);
  `activo` sigue siendo solo el récord. **Los amistosos CUENTAN** (decisión
  del usuario, 14/10/2026: el espectáculo se arma para el hincha, y una burbuja
  se arma y se rompe ahí con causas que interesan); un extremo hecho con la
  mitad o más de amistosos se marca `extremo.inflada` (§10.2, chip «INFLADA»)
  sin apagar la alerta ni mover el riesgo. Las K de goles quedan fuera
  a propósito hasta que se decida sumarlas. **Las otras familias** (doble
  oportunidad, márgenes 1+…4+, goles; §15, 17/10/2026, 518 equipos): ni el
  largo ni el récord predicen el partido siguiente mejor que la frecuencia
  propia (1 de 48 combinaciones, lo esperable por azar), y el récord se
  SOSTIENE algo más, no revienta: entran al análisis como descripción, sin
  puntos. Lo que SÍ agrega al 1X2 es el PERFIL de doble oportunidad
  por condición (§15.1: con qué frecuencia el local no pierde / no gana de
  local y el visitante de visita; M7 − motor −0.011 de log-loss con el
  intervalo bajo cero): falta medirlo contra el mercado antes de la fórmula. La narrativa viaja en `otrasFamilias` (`backend/analisis/familias.py`, espejo `src/lib/familias.ts`, vectores `scripts/casos_familias.json`) de `/burbujas` y de `reventonCalculado`, con la tarjeta «Otras burbujas» y el prompt (v. COWORK.md) que pide el perfil DC antes del 1X2. **No se
  corre el backtest contra el mercado** (usuario, 17/10/2026: lo que importa es la narrativa). Una
  de estas burbujas GRANDE en su récord (`cuidado`, 5+) es CUIDADO con la carga —ámbar, alerta
  `FAMILIA-RECORD` tipo `dato`—, y el veredicto lista en `objetivo.otrasFamilias` las que el
  marcador cortó: las `porExplicar` llevan su causa en `porLado.*.cortes` con un mecanismo de
  `reventones.MECANISMOS` (§15.2, el Everton 0-2 Chelsea). **Por período** (§10-bis):
  `historialPorPeriodo` repite las medidas acotadas a temporada · año · DT
  vigente · últimos 20, filtrando por la fecha del reventón sobre los mismos
  episodios; la global sigue mandando en el riesgo (es la calibrada) y un
  período sin corte viaja con `sinDato`. Espejo TS y vectores dorados. En la
  gráfica de K la referencia punteada es elegible por período (`kPeriodo`,
  `PeriodoReventon`, `src/lib/reventonRef.ts`) con una línea vertical donde
  arranca el período; sin base se dice, no se vuelve a la global callado.
- Márgenes en la pantalla = burbujas de SEQUÍA (`sequiaMargen`,
  `src/lib/kview.ts`, aplicada en `loadBurbujas`): «Gana N+» crece con el nivel
  del rival mientras no gana por N o más y revienta cuando lo hace; «Pierde
  N+» igual. Vista derivada de goles y nivel del rival: el motor y el contrato
  (`kVic/kDer`, margen exacto) no se tocaron (ROADMAP_BURBUJAS §2).
- **DTP por Cowork** (`backend/analisis/dtp_cowork.py`, DTP_DISENO §7): los
  insumos salen de la ficha (`GET /analisis/cowork/dtp/{id}`, con la
  `aperturaPrevia` contra la que se cierra) y el DTP va ESTRUCTURADO en
  `dtp.bloques[]` (uno por equipo foco). Cowork responde las 6 preguntas del
  checklist del bloque rival; la CLASE (improvisado · estructural ·
  estructural no probado · ambiguo) y `c1Tde` las calcula el backend al leer.
  La apertura entra a `cadena_dtp` solo antes del pitazo y sin pisar la
  primera. El TDE HEREDA del DTP (C1 de la clase del bloque, SOB2 del nivel
  del rest defense; manda el DTP, alerta `HERENCIA-DTP` si difiere) y la
  pestaña **DTP** del parte lo dibuja (`PanelDtpCowork`).
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
   14:56 (`horas=14`), `limite=20`; el tramo lo fija el SKILL por la hora de
   Lima, porque el texto de una rutina solo se cambia desde su propia
   conversación— en la sesión «SAD · corrida de partes
   (rutina)»; veredictos 20:12 (`limite=30`) en «SAD · corrida de veredictos
   (rutina)»; **mantenimiento** 12:23 y 21:47 en «SAD · mantenimiento
   (rutina)» (desde el 22/10, deuda 17); **rehacer** cada 30 min (05:07 a 23:37 Lima, dos disparos :07 y
   :37) en «SAD · rehacer DTP con el once (rutina)», desde el 22/10/2026:
   modo `rehacer` de `corrida-sad`, los partes con DTP-REHACER a 30-80 min del
   pitazo, avisa solo si hizo algo. Un fin de semana trae 50-65 candidatos del padrón (15-23 por
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
   **El mantenimiento corre en su propia sesión fija** desde el 22/10: «SAD ·
   mantenimiento (rutina)» (`session_018rYwkkxMKQpJpfTdkxScvd`), 12:23 y 21:47
   de Lima, POR GRUPOS de causa (hasta 3 grupos de código por pasada, un PR
   por grupo). Las dos rutinas viejas, que disparaban en la sesión de trabajo,
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
   - **Rutina de rehacer** (`session_01V3tPBuV4pgvD7rMF39twu9`): medido el
     22/10, ~0,25 USD por disparo vacío (crece con el contexto de la sesión) y
     ninguno rehízo nada por la tarde. Decidido (usuario, 22/10): comprobación
     barata `GET /analisis/cowork/rehacer` (los partes con DTP-REHACER a 30-80
     min); el skill la llama primero. Falta que el mensaje de las dos rutinas
     (:07 y :37) la llame ANTES del `git pull`: solo se cambia desde esa sesión.
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
   - **Ideas, no pedidas**: pintar los `tramos` del veredicto en Aprendizaje y
     en la vista de derrotas del favorito (12 de 44 tuvieron segundo giro);
     el 1X2 de la cohorte sale SUBCONFIADO (60 %+ acertó 18 de 18, 40-49 %
     → 54 %): medir con más n antes de tocar nada; archivar la sesión
     temporal `session_01NuzvTgFR41DgJsU122s6EE`.

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
