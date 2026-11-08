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
python -m backend.contacto        # criterio de contacto (acierto tras 3 fallos seguidos) desde la API con el token de Cowork; lo corre la rutina del lunes (docs/METODO_APUESTA.md)
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
  sola desde el 14/10/2026— · resto de primeras. **Desde el 29/10/2026** (fase
  0 de ligas, REVENTON §16) entran Eredivisie, Grecia y Süper Lig (con sus copas
  como menores), y las segundas de Europa y la Liga de Expansión MX pasan a
  MENORES: el reventón separa poco en ellas y gastaban cuotas en vivo. Las
  **copas nacionales medidas** (REVENTON §16.1) entran a la agenda AL FINAL
  (prioridad 8) sin ser del padrón: Taça, Coupe de France, Copa del Rey y DFB
  Pokal en cualquier ronda, FA Cup y Coppa Italia desde cuartos, la EFL Cup
  nunca (`separacion_liga.copa_en_agenda`); su 1X2 sale del mercado, no del
  motor (localía negativa en copas). La fase de grupos / fase liga
  de los demás torneos internacionales y las segundas divisiones quedan FUERA por defecto
  (`grupos=true` / `segundas=true` las meten, al final): un jueves de Europa
  League llenaba los cupos con partidos de relleno. Sin `fecha` la agenda es
  «desde ahora y por 24 h», a la hora que se corra (no «mañana en UTC»), y
  `liga=<texto>` acota por país o nombre. Las demás copas nacionales quedan fuera a
  propósito. El clásico se evalúa DESPUÉS del padrón: mirarlo antes hacía que
  un mismo torneo entrara o no según se activara el etiquetador de derbis. Un
  descarte viaja SIEMPRE con su motivo y el id de la liga, y la respuesta trae
  `corte` con lo que quedó fuera SOLO por el `limite` —que es lo que hace que
  una jornada entera de LaLiga no aparezca sin que nadie entienda por qué—.
  Un equipo que figura en DOS partidos a menos de 24 h viaja con `conflicto`
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
  arregla con un test —AGRUPADAS POR CAUSA, todos los grupos de código (sin
  tope desde el 31/10/2026) y un PR por grupo; lo que no es código se
  clasifica entero en la misma corrida (22/10/2026: la cola llegó a 88
  arreglando de a 8 sueltas)—,
  valida TODO y mergea solo en verde y fuera de las zonas
  sagradas (motor, números calibrados, skills, tokens, datos, cuarentenas,
  Railway): eso va a `usuario` con la propuesta. El latido cuenta las
  abiertas (`incidencias`) y pasa a ámbar con alguna que bloquea.
  **Con memoria** (27/10/2026, pedido del usuario): la misma causa escrita
  con otras palabras forma una FAMILIA (`incidencias.causas`, `GET
  …/incidencias/causas`; 3+ palabras compartidas y 60 % del título más
  corto). Cada abierta trae su `conocida` (la última cerrada de la familia) y
  no se re-investiga; un `dato_api` visto en 3+ partidos sin decisión sale
  `recurrente` y sube al usuario con una regla de código propuesta; lo que
  vuelve después de un PR sale `reaparece`. Las `usuario` se deciden en la
  tarjeta **Decisiones pendientes** de Partidos (agrupadas por causa, 🔑:
  `POST …/{id}/decision` → `aprobada`, que la próxima pasada implementa
  primero, o `por_diseno`). Y **resuelta es en producción**: `/health` trae el
  `commit` que corre (`RAILWAY_GIT_COMMIT_SHA`); un PR mergeado que todavía no
  está ahí queda `por_desplegar` hasta que la pasada siguiente lo confirma.
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
- **Quién no puede jugar sale de la base, no solo de la API** (30/10/2026,
  incidencias 772, 778 y 835: Neymar con la roja encima, disponible y primer
  ejecutor de penales). `backend/sanciones.py` lee las tarjetas de la ficha:
  roja (directa o doble amarilla) en el último partido terminado de la MISMA
  competición → se pierde este (la de la liga no suspende en la copa); el
  ciclo de amarillas solo con la regla conocida (`UMBRALES`) y con los eventos
  de todos los partidos de la competición (si no, `conteoParcial`, no se
  afirma). Quien está en la hoja de este partido juega: la hoja manda. Viaja en
  `f1/{id}` (`sancionados`, `sancion` por fila, `amarillasEnLaCompeticion`),
  baja al ejecutor de penales del DTP y suena `SANCION-SIN-DECLARAR` (calculada)
  si el parte no lo tiene en `fuera`. Y `ONCE-SIN-FILA-F1` (743): titulares del
  once oficial sin fila en la tabla F1, que no pesan en el IP.
- **De qué está hecho el nivel del motor** (30/10/2026, incidencia 860, usuario:
  «al analista le funciona bien»): Konyaspor 0-4 Galatasaray, el motor dio 41 %
  al 14.º y la ventana de 20 del líder traía 6 amistosos de pretemporada y
  3 de Champions (1,65 pts/p en la ventana, 2,44 en la liga). `/predicciones`
  trae por lado `ventanaNivel` (`backend/analisis/ventana_nivel.py`, el mismo
  filtro y deduplicación del pipeline) y con 3+ amistosos en un lado
  `fiabilidadMu` baja a «media» (`porVentana`); el escaneo lo marca como chequeo
  INFORMATIVO (no se deposita). **Medido el mismo día** (`backtest_nivel_ventana`,
  9.191 partidos de prueba): sacar los amistosos del nivel NO mejora el 1X2 y
  sacar también los internacionales lo empeora donde hay amistosos; en el caso,
  sin amistosos el local queda en 40,8 %. El 41 % sale de un nivel que separaba
  al líder del 14.º por solo 0,26, menos de lo que vale jugar en casa (0,382 de
  μ = 0,55 de nivel); la localía de la Süper Lig no está inflada (0,479, medida
  por liga) y la forma no entra al 1X2. **La localía por liga** (`backtest_localia_liga`,
  mismo día) mejora el 1X2 en todos por 0,0017 de log-loss y en los partidos
  con cuota en nada; el mercado le gana al motor por 0,061 igual: no se cambia.
  La fórmula NO se toca. El aviso se queda porque con 3+ amistosos el motor
  queda el doble de lejos del mercado (0,084 de log-loss contra 0,041).
- **Quién es quién vive en UN archivo** (30/10/2026, usuario): `backend/identidad.py`
  decide si dos nombres son la misma persona —tokens, pila, apellido escrito
  distinto (seseo, ß, una letra cambiada, de más o de menos, doble, en otro
  orden), mismo jugador, la hoja contra la tabla y el DT (laxo a propósito)—.
  `bloque_f`, `f1_base`, `dtp_cowork`, `parte` e `ingesta/jugadores` la importan
  (sus nombres viejos son alias): un caso de nombres nuevo se arregla ahí, con
  su test en `backend/test_identidad.py`, y vale para todos. Antes eran cinco
  copias y cuatro versiones de «una letra»: la identidad se parchó ocho veces
  en un mes y la 724 volvió 11 veces.
- **El escaneo preventivo del CÓDIGO** (30/10/2026, usuario: «escaneo preventivo
  sobre nuestro código o en general todo lo que falla»): `docs/FALLAS.md` es el
  catálogo de las clases de falla de las 859 incidencias (identidad, DT, once
  tarde, quién no juega, falla callada, regla del skill incumplida, regla del
  fútbol leída del marcador, fuga, contrato, rutas inventadas, datos sucios,
  costo, métrica contaminada, automatización) con la GUARDIA de cada una, y
  `backend/test_arquitectura.py` (en CI) verifica leyendo el código las que se
  pueden: la identidad solo en `identidad.py`, cada test en CI, cada endpoint y
  alerta calculada en `openapi.yaml`, cada `except Exception` con su motivo y
  cada ruta que citan los skills existe. El mantenimiento deja la guardia de
  cada grupo que arregla. Lo encontró al nacer: 7 tests que CI no corría, un
  endpoint y 7 alertas sin documentar, 28 `except` mudos.
- **El escaneo preventivo** (30/10/2026, usuario: «no esperar a que salten estas
  cosas»; `backend/analisis/escaneo.py`, `GET /analisis/cowork/escaneo`): la
  agenda de las próximas 36 h y las partes jugadas en 48 h contra los chequeos
  de lo básico (`CHEQUEOS`: sancionados y partes que los tienen disponibles, el
  mismo jugador dos veces en la F1, sin plantel, DT sin confirmar, dos partidos
  el mismo día, sin cuotas, once tarde, ficha sin eventos), agrupado por
  chequeo. El mantenimiento lo corre en su paso 0-bis y deposita UNA incidencia
  por chequeo (`origen: escaneo`); lo que un parte reporta y el escaneo no vio es
  un chequeo que falta. **El mantenimiento arregla la CLASE, no el caso** (la
  identidad del jugador se parchó 8 veces en un mes, cada vez en un módulo),
  en tres pasadas (12:23, 17:41 y 21:47 de Lima). **La cola no puede crecer**
  (31/10/2026, usuario: «el mantenimiento tiene que cerrar todo, optimizar
  todo hasta casi quedarse sin chamba»): sin tope de grupos, la meta de cada
  pasada es la cola en CERO, la familia más grande va primero («grande» se
  parte en sub-causas, nunca se deja para después) y, con la cola vacía, la
  prevención (paso 7-bis del skill: la guardia de las familias que más entran
  y la lista «No se reporta» de lo que se cierra siempre igual). El informe
  dice la cola al empezar → al terminar y cuántas entraron.
- **Quién pasó una llave sale de la base, nunca del marcador** (29/10/2026,
  incidencia 774: Palmeiras pasó a la final de la Libertadores por penales y un
  parte lo dio por eliminado). `backend/eliminatoria.py` lo calcula de la tanda
  (`penalty_*` o los `Shootout` convertidos), del global con la ida o de la
  prórroga; sin eso, `avanza` null, nunca adivinado (la ida de una llave no
  cierra nada). Viaja en la ficha (`eliminatoria`), en el título del evento del
  timeline y en `objetivo.eliminatoria` del veredicto (el 1X2 y `ganador`
  siguen a 90'). Un parte que lo contradice suena `ELIMINATORIA-AL-REVES` (tipo
  `dato`, calculada) en `faltan` al depositar y en la tira al leer.
- **Las copas nacionales no entran a las tablas** (29/10/2026, usuario, al
  entrar 22 partidos de la Copa del Rey en un día): se analizan y sus lecciones
  fijan rúbrica, pero quedan fuera de toda métrica de Aprendizaje (población
  `copa`, como la cuarentena que enseña, sin mover números), del historial de
  valor contra el mercado, del resumen de derrotas del favorito y de la
  simulación (`excluidos`). Un favorito al 90 % contra uno de quinta a cuota
  1.02 inflaba el tramo de 60 %+ y la simulación. La marca sale de
  `escala.copas_nacionales` (lista `COPAS` o el nombre; los torneos
  internacionales de clubes no son copa aunque digan «Cup»).
- **El rol contra el grid, en sombra** (29/10/2026, incidencia 646):
  `contraElOnce.rolesVsGrid` compara el rol que `m1.rolesReasignados` le da a
  un titular con su casilla del grid oficial (línea, y banda de laterales,
  carrileros y centrales; un 9 en la fila de la mediapunta no cuenta). Medido
  sobre 315 partes: 13 con hallazgo, casi todos reales (Gray, Castillo,
  Velasco). NO pide rehacer (`dtp_cowork.ROLES_GRID_REHACE = False`) hasta que
  los veredictos de una semana digan cuántos fueron reales; la caja del DTP lo
  muestra «en observación».
- **Simulación de apuesta** (28/10/2026, pedido del usuario;
  `backend/analisis/simulacion.py`, `GET /analisis/simulacion`, sección
  **Simulación**): una banca de 100 unidades sobre los 1X2 declarados en los
  partes. **EL MÉTODO va primero** (`proporcional`, 03/11/2026, usuario:
  «investiguemos el método definitivo»; `docs/METODO_APUESTA.md`): el 1 % de
  la banca a nuestro elegido, con un freno que pausa el tramo de confianza que
  en sus últimos 50 partidos acertó menos de lo que pedía la cuota (z < −0,5,
  15+ partidos) y sigue anotando hasta que se recupera. No busca valor contra
  el mercado: lo que se mide es el win rate contra lo que pide la cuota, y
  Kelly queda como alarma, no como meta (usuario, 03/11). El **criterio de contacto** (`trasFallos`, 04/11/2026): el acierto tras k fallos seguidos, que es lo que la martingala cobra; se toma en serio con 100+ casos tras 3 fallos, 65 %+ y el intervalo sobre el promedio, regla fija, medida cada lunes. Las otras series —plana (control, 1 u al elegido), plana solo con el
  elegido a 60 %+ (`plana60`, 29/10/2026, usuario: el tramo alto de confianza,
  ¿además de acertar gana a su cuota?), Kelly entero, ½ y
  ¼ (f* = (p·c − 1)/(c − 1) sobre NUESTRAS probabilidades, a la selección con
  más ventaja; sin ventaja no apuesta) y martingala POR LÍNEAS (29/10/2026,
  usuario: cada línea es una martingala de 1 u que se duplica tras perder;
  una apuesta toma la línea libre más antigua y, con todas en juego, abre
  otra) y la misma martingala solo con el elegido a 60 %+ (`martingala60`,
  29/10/2026, usuario)—. El tiempo es el real: se apuesta en el pitazo y se cobra
  `DURACION` (2 h) después, los simultáneos usan la banca de antes y ninguna
  apuesta pasa de la plata libre (banca − lo comprometido). Cuenta SOLO desde los partidos del 28/10/2026 (`DESDE`, 00:00
  de Lima); entra el parte depositado antes del pitazo, sin cuarentena, con el
  1X2 completo y las tres cuotas (media de las casas de la última captura
  prepartido, con margen); lo que no entra viaja en `excluidos` con su motivo.
  Se recalcula al leer. Cada apuesta lleva la VERSIÓN de cada skill vigente al depositar
  (`version_al`: `CORTE_VERSION` por día y, si se sabe, la hora en que el zip
  llegó a la cuenta en `SUBIDA_VERSION` —con cada versión nueva subida, anotar
  la hora ahí—) y la tabla «por versión de sad-analysis» separa lo que ganó
  cada una. La demo (`src/data/simulacionDemo.ts`) se GENERA con `simular` del
  backend: no hay copia de la cuenta en TS. No es una recomendación de apuesta
  y no se abre al token de Cowork.
- **Separación del riesgo por liga** (29/10/2026, usuario; REVENTON §16,
  `backend/analisis/separacion_liga.py`): el AUC del riesgo del reventón medido
  liga por liga sube con la jerarquía de la liga (r = 0,89 con el peso del
  nivel en la μ). `/burbujas` trae `separacionLiga` (alta ≥ 0,64 · media ≥ 0,60 ·
  baja) y la tarjeta lo pinta; NO mueve puntos ni cortes, dice cuánto pesar la
  guía (el prompt lo pide en ligas de paridad). Tabla fechada: rehacerla con
  cada backtest liga por liga.
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
  `K-EXTREMO-CONDICION` (tipo `dato`, 20/10/2026; en la franja alta sin récord,
  `K-CERCA-EXTREMO-CONDICION`, 25/10/2026);
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

## Deuda, historia y pendientes → `docs/DEUDA.md`

Lo que se sabe roto o pendiente, la historia de cada decisión (puntos 1 a 19:
DT de la base, cuotas, plan de API-Football, sesiones fijas y rutinas con sus
ids, revisiones de skills, decisiones del usuario) y los siguientes pasos
viven en `docs/DEUDA.md`. Se sacó de acá el 03/11/2026 porque este archivo se
carga en cada paso de cada agente y la historia no hace falta para analizar un
partido. **Leelo antes de** clasificar una incidencia del mantenimiento,
revisar un skill, tocar las rutinas o retomar un pendiente del usuario; y un
pendiente nuevo se anota allá, no acá.
