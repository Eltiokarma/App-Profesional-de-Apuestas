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

# backend (junto a las 4 .db en la raíz, o SAD_DATA_DIR)
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --port 8000
python -m backend.test_api        # verificaciones del contrato (265 checks)
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
src/sections/      Partidos (inicio) · Cuotas · Burbujas · Skills · Estadísticas · Equipo
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
  se devuelve el conflicto en vez de un IP inventado. Cada skill del pipeline
  tiene su sitio en la pantalla (tabla en `docs/COWORK.md`): bloque G desde
  `backend/calendario.py`, timeline fundido con `backend/cronologia.py` y
  pintado con `TimelineComparativo`, TDE estructurado con sus niveles venidos
  del skill (el backend no le pone umbrales a esa escala), y el pronóstico por
  equipo foco entra en `cadena_dtp` como apertura —el veredicto lo emite quien
  cierre el eslabón—. Un bloque nuevo del prompt necesita sitio en el parte:
  si no lo tiene, se pierde.
- **Dos tokens** (`backend/app.py`): `SAD_API_TOKEN` es la llave maestra —abre
  también lo que gasta créditos de Claude y cuota de API-Football— y
  `SAD_TOKEN_COWORK` es el acotado que se le da a Cowork: solo
  `/analisis/cowork/*` (sin DELETE) y los GET del pipeline, por LISTA DE
  PERMITIDOS. Un endpoint nuevo nace denegado para Cowork; abrirlo es
  deliberado. Nunca le des el maestro a un agente que lee contenido de fuera.
- Costo de la IA: `docs/efe-dtp/COSTO_IA.md`. Lo que está en nuestra base se
  calcula, no se le pregunta al modelo — y lo calculado no se le hace copiar a
  la salida. Los dos bloques calculados hoy: el mapa de rivales del EFE
  (`backend/calendario.py`) y los partidos del timeline (`backend/cronologia.py`).
- Gráficas de K: tres valores a la vista (último · últimos dos de la condición
  que se analiza, saltando los que repiten valor) vía `puntosEtiquetados` de
  `src/lib/kview.ts`. Una gráfica nueva usa ese helper, no su propia regla.
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
   pronóstico declarado ni borra el veredicto escrito. Faltan las fases C
   (lecciones por skill), D (dossier cada 4 fallos, que ABRE la revisión pero
   no autoriza mover nada) y A (antecedentes). La app nunca mueve un peso de
   un skill por su cuenta. Snapshot de los skills en `docs/skills/`.
7. Fase nube completa cuando toque: `docs/SERVICIOS_EXTERNOS.md` (Postgres).
