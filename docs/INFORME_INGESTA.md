# INFORME TÉCNICO DE INGESTA — Proyecto SAD

> **Objetivo:** documentar el pipeline de ingesta (extracción API-Football + cadena de cálculo hasta `discreto.db`) para portarlo a otro repositorio (app web con backend FastAPI que ya trae el motor de lectura).
>
> **Alcance:** SOLO prepartido + resultados finales. Se ignora deliberadamente todo lo relativo a partidos en vivo / minuto a minuto.
>
> **Método:** cada afirmación lleva referencia `archivo:línea` sobre el snapshot recibido. Cuando algo **no existe** en el snapshot, se indica de forma explícita en lugar de suponerlo.
>
> **Nota de rutas:** en el snapshot los archivos aparecen aplanados en un solo directorio, pero por los encabezados de cada archivo (p. ej. `# src/data/api_fetcher.py`) y por `proyecto_sad_memoria.txt` el layout real es: raíz del proyecto con `sad.db`, `constants.db`, `levels.db`, `discreto.db`, `model_exports/`, `leagues2024.csv` **junto a** `src/`, y el código en `src/{config,data,ui,utils}`. Las rutas de este informe usan esa convención.

---

## 0. Mapa rápido de módulos de ingesta

Hay **tres rutas de extracción** distintas conviviendo en el repo (importante para el port: elegir una como canónica):

| Ruta | Archivo | Naturaleza | Recomendación para el port |
|------|---------|-----------|----------------------------|
| A | `src/data/auto_extractor_v5.py` | Script CLI standalone (sqlite3 puro, `argparse`, cron-friendly) | **Base ideal para el port.** Es la más limpia y autónoma; baja odds de TODOS los bookmakers en 1 request |
| B | `src/ui/extraction_window.py` | GUI PySide6 (manual, botones) | Lógica de parseo reutilizable, pero acoplada a Qt |
| C | `src/ui/data_sync_dialog.py` | GUI PySide6 "Verificación de datos pendientes" | Contiene la lógica de *detección* de qué falta (odds prepartido, resultados desactualizados) |

Rutas B y C comparten cliente `APIFetcher` (`src/data/api_fetcher.py`) y guardado `save_*` (`src/data/api_database_manager.py`). Ruta A reimplementa cliente y DB por su cuenta.

**Cadena de cálculo** (independiente de la extracción):
`sad.db` → `levels.db` (`levels_calculator.py`) → `constants.db` (`constants_calculator.py`) → `discreto.db` (`discretizer_db.py`).

---

## 1. EXTRACTOR API-FOOTBALL

### 1.1 Endpoints exactos (rutas, parámetros, archivos)

**Base URL y host** (RapidAPI):
- `BASE_URL = 'https://api-football-v1.p.rapidapi.com/v3'` — `src/config/api_config.py:11`
- Host `api-football-v1.p.rapidapi.com` — `api_config.py:14`, headers en `get_api_headers()` `api_config.py:59-69`
- En `auto_extractor_v5.py` el mismo base/host está duplicado — `auto_extractor_v5.py:155,161-164`

> **Ojo:** el proyecto usa el gateway **RapidAPI**. La "memoria" del proyecto menciona un setup dual-gateway (api-sports.io directo + RapidAPI) pero **en este snapshot solo hay RapidAPI**; no encontré cliente ni failover a `api-sports.io`. (Indicado explícitamente para no suponerlo.)

Endpoints invocados por `APIFetcher` (`src/data/api_fetcher.py`), todos vía `_make_request(endpoint, params)` (`api_fetcher.py:41`):

| Endpoint | Método/función | Línea | Parámetros |
|----------|----------------|-------|-----------|
| `GET /fixtures` | `get_fixtures(league_ids, season, from_date, to_date, status)` | `api_fetcher.py:99-146` | `league`, `season`, `from`, `to`, `status` (una liga por llamada, itera la lista) |
| `GET /fixtures` | `get_fixtures_by_date(date, league_id, timezone)` | `api_fetcher.py:148-178` | `date`, `timezone` (default `America/Lima`), `league` |
| `GET /fixtures` | `get_fixture_by_id(fixture_id)` | `api_fetcher.py:180-196` | `id` |
| `GET /odds` | `get_odds(fixture_id, bookmaker_id)` | `api_fetcher.py:202-227` | `fixture`, `bookmaker` (opcional) |
| `GET /odds` | `get_odds_with_fallback(fixture_id, primary_bookmaker=26, fallback_bookmakers)` | `api_fetcher.py:229-266` | `fixture` + `bookmaker` (uno por intento) |
| `GET /players` | `get_players_stats(...)` / `get_all_players_stats(...)` | `api_fetcher.py:272-353` | `league`, `season`, `page`, `team` (paginación auto) |
| `GET /teams/statistics` | `get_team_statistics(league_id, season, team_id)` | `api_fetcher.py:359-387` | `league`, `season`, `team` |
| `GET /leagues` | `get_leagues(country, season)` | `api_fetcher.py:393-420` | `country`, `season` |
| `GET /teams` | `get_teams(league_id, season)` / `get_team_by_id(id)` | `api_fetcher.py:426-469` | `league`, `season` / `id` |

En `auto_extractor_v5.py` (ruta A) solo se usan dos endpoints:
- `GET /fixtures` — `get_fixtures(league_id, season, from, to)` `auto_extractor_v5.py:208-217`
- `GET /odds` — `get_odds(fixture_id)` con **solo** `fixture` (⇒ devuelve TODOS los bookmakers) `auto_extractor_v5.py:219-223`

> Para el port **solo necesitas `/fixtures` y `/odds`**. `/players`, `/teams/statistics`, `/teams`, `/leagues` son accesorios (team/player stats) y no forman parte del núcleo prepartido+resultado.

### 1.2 Orden de llamadas

**Ruta A (`auto_extractor_v5.py`), la más clara — `main()` `auto_extractor_v5.py:592-650`:**
1. FASE 1 `extraer_fixtures(todas_ligas)` (`:505-534`): itera ligas de `LIGAS_CONFIG`; por cada liga 1 request `/fixtures` con ventana `from=hoy-3d`, `to=hoy+10d` (`DIAS_ATRAS=3`, `DIAS_ADELANTE=10`, `:99-100`, `:511-512`); guarda con `save_fixture` (`INSERT OR REPLACE`).
2. FASE 2 `extraer_odds()` (`:536-568`): calcula fixtures `NS` sin odds en los próximos `DIAS_ADELANTE` días (`get_fixtures_sin_odds` `:448-467`), y por cada uno 1 request `/odds` (todos los bookmakers) → `save_odds`.
- Se puede correr solo fixtures (`--fixtures`) o solo odds (`--odds`) `:594-595,635-643`.

**Ruta B (GUI `extraction_window.py`) — `ExtractionWorker` `extraction_window.py:610`:**
- `_extract_fixtures` (`:648-696`): por liga → `get_fixtures([lid], season, from, to)` → `process_fixtures` → `save_fixtures_wrapper`; al terminar, **auto-cálculo de constantes** de los equipos tocados (`:690-693` → `_auto_calculate_constants` `:834`).
- Odds es **manual y aparte**: el usuario selecciona fixtures y dispara `_extract_odds` (`:698-729`) / `_extract_odds_single` (`:731-759`) / `_extract_odds_auto` (`:2248-2276`, detecta filas "sin ODDS").

**Ruta C (GUI `data_sync_dialog.py`) — `DataSyncWorker` `data_sync_dialog.py:398`:**
- `_sync_results` (`:428`): re-descarga `/fixtures` agrupando por `(league_id, season)` en la ventana de fechas de los fixtures pendientes, y hace `UPDATE` de goles/estado.
- `_sync_odds` (`:562-607`): `get_odds_with_fallback` + `save_odds` para los fixtures elegidos.
- `_sync_historical` (`:609-666`): backfill masivo `ligas × temporadas` (`/fixtures` sin ventana de fecha) → `process_fixtures` → `save_fixtures`.

### 1.3 Descarga de fixtures, resultados y CUOTAS PREPARTIDO

**Fixtures y resultados** se obtienen del **mismo** endpoint `/fixtures`. El JSON trae `fixture`, `league`, `teams`, `goals`, `score`. Parseo canónico:
- `process_fixtures` GUI — `extraction_window.py:105-185` (mapea a modelo `Fixture`, incluye `status_long/short`, `goals_home/away`, `score.halftime/fulltime`).
- `process_fixtures` backend — `src/data/data_processing.py:27-141` (equivalente, misma estructura).
- `save_fixture` ruta A — `auto_extractor_v5.py:319-395` (`INSERT OR REPLACE` por PK `id`).

**Cuándo se capturan las cuotas (cuánto antes del partido):** NO hay un "X horas antes" fijo ni un scheduler. Las cuotas son un **snapshot prepartido** que se baja cuando corre el extractor, para partidos `NS` (Not Started) dentro de una **ventana hacia adelante**:
- Ruta C detecta odds faltantes para partidos en las **próximas 72 h** (`3 días`): `_check_missing_odds` `data_sync_dialog.py:214-303`. Filtros: `f.date > now`, `f.date < now+3d`, `status_short='NS'`, `NOT EXISTS odds` (`:247-250`). Calcula `hours_remaining` por fixture (`:280-281`) solo para mostrar, no para decidir.
- Ruta A baja odds de partidos `NS` en los próximos **10 días** (`DIAS_ADELANTE`): `get_fixtures_sin_odds` `auto_extractor_v5.py:448-467` (`status_short='NS'`, `date BETWEEN hoy AND hoy+10d`, `o.id IS NULL`).
- Como el guardado es **upsert**, si el extractor corre varias veces, una corrida más cercana al kickoff **sobrescribe** la cuota anterior (no se guarda histórico de cómo se movió la línea). Ver 1.4.

> **Implicación para el port:** si la app web necesita la cuota "a T-h del partido", hoy NO existe ese dato temporal; solo la última foto guardada. Habría que añadir timestamp de captura si se quiere versionar líneas.

**Qué bookmakers y mercados se guardan:**
- Ruta A (`/odds` sin `bookmaker`) devuelve y guarda **TODOS los bookmakers y TODOS los mercados** que retorna la API (1X2, Over/Under, BTTS, hándicaps, etc.). `save_odds` recorre `response → bookmakers → bets → values` y guarda cada combinación (`auto_extractor_v5.py:396-446`). Upsert por `(fixture_id, bookmaker_id, bet_id, value)` (`:420-437`).
- Rutas B/C usan `get_odds_with_fallback` (`api_fetcher.py:229-266`), que pide **un bookmaker por vez**: primero `26`, luego `PREFERRED_BOOKMAKERS[1:]`. **Devuelve el primer bookmaker con datos y para** ⇒ en la práctica guarda **un solo bookmaker por fixture**. `PREFERRED_BOOKMAKERS = [26, 11, 20, 24, 1, 10, 5]` (`api_config.py:21`, comentario dice `26=bet365`).
- El parseo de odds (todas las rutas) guarda literalmente `bet_name` (p. ej. `'Match Winner'`) y `value` (`'Home'/'Draw'/'Away'/'Over 2.5'/...`) tal cual vienen de la API: `process_odds` `extraction_window.py:188-231`, `data_processing.py:393-449`, `data_sync_dialog.py:668-703`.

**Cómo se promedian o seleccionan las cuotas:** en la **ingesta NO hay promedio ni selección** — se guarda todo crudo. La agregación ocurre en la **capa de consumo/predicción**:
- Motor Anticulebra (Tensión del Favorito): filtra `o.bet_name = 'Match Winner'` y toma **el MÁXIMO** por resultado entre bookmakers: `MAX(CASE WHEN o.value='Home' THEN o.odd END)` etc., `GROUP BY f.id` — `anticulebra_engine.py:543,572-574,580`. Es decir, "mejor cuota disponible", **no promedio**.
- `database_queries.get_1x2_odds` (`database_queries.py:304-331`): filtra `bet_name LIKE '%winner%'/'%1x2%'/'%match result%'` y se queda con el último valor por resultado (sin promediar).

> **Discrepancia con la "memoria":** ésta menciona "promediar entre bookmakers" y un marcador `bookmaker_name='SYNTHETIC'` para rellenar huecos, además de nuevas K de cuota (`k_cuota_*`, tabla `constants_cuota`). **Nada de eso existe en el snapshot** (verificado: sin coincidencias de `k_cuota`, `constants_cuota`, `SYNTHETIC`). Es trabajo planificado, no implementado. La selección real hoy es **MAX (mejor cuota)** en el path ML.

### 1.4 Idempotencia del guardado de odds

- Ruta A: `SELECT ... WHERE fixture_id=? AND bookmaker_id=? AND bet_id=? AND value=?` → si existe `UPDATE odd`, si no `INSERT` (`auto_extractor_v5.py:420-437`).
- `api_database_manager.save_odds`: mismo criterio `(fixture_id, bookmaker_id, bet_id, value)` → actualiza `existing.odd` (`api_database_manager.py:220-235`).
- **No hay UNIQUE constraint a nivel DB en `odds`**; la deduplicación es solo por lógica de app. Si mezclas rutas o insertas por fuera, puedes duplicar.

### 1.5 Dónde está la API key, ligas seguidas y temporadas

**API key:**
- Canónico: variable de entorno `API_KEY` — `api_config.py:8` (`os.getenv('API_KEY')`), validada en `get_api_headers` (`:61-65`).
- ⚠️ **Riesgo de seguridad:** `auto_extractor_v5.py:28` tiene una **API key hardcodeada como fallback** (`os.getenv('API_KEY', '<clave_real_expuesta>')`). Está en texto plano en el repo. **Rotar esa clave y quitar el fallback antes de portar.**

**Ligas seguidas (ids):** hay **tres listas distintas** (fuente de deriva, ver riesgos):
- `api_config.LEAGUE_REGIONS` (amplia, por regiones) — `api_config.py:24-57`.
- `data_sync_dialog.LIGAS_CONFIG` (curada, ~40 ligas con nombres) — `data_sync_dialog.py:25-80`; helper `get_all_configured_league_ids()` `:86-91`.
- `auto_extractor_v5.LIGAS_CONFIG` (su propia copia) — `auto_extractor_v5.py:53+`.
- `leagues2024.csv` (raíz): **catálogo** de 1160 ligas (`League ID, League Name, Country ID, Country Name`), no es la lista "seguida".
- ❗ **No existe** `config/season_mapping.py` en el snapshot (la memoria lo menciona; indicado explícitamente).

**Temporadas:**
- GUI: `QSpinBox` rango `2015-2030`, default **2024** — `extraction_window.py:1170-1172`; workers usan `season=2024` por defecto (`:650,763,792`).
- Ruta A: constante `SEASON = 2025` — `auto_extractor_v5.py:30`.
- Ruta C `_sync_results`: usa la `league_season` guardada del fixture, con fallback `2024` (`data_sync_dialog.py:456`).
- La temporada es **un entero único** por llamada. ⚠️ Para ligas europeas de año cruzado (2025 = 2025/26) vs sudamericanas de año natural, un solo número falla para parte de las ligas (coincide con lo anotado en la memoria). El código NO resuelve esto automáticamente.

### 1.6 Manejo de límites de requests (pausas, reintentos, presupuesto)

**Cliente `APIFetcher` (rutas B/C)** — `api_fetcher.py:41-93`:
- `MAX_RETRIES = 3`, `RATE_LIMIT_DELAY = 60` — `api_config.py:17-18`.
- En HTTP 429: `sleep(60)` y reintenta (`:59-62`). Timeout de 30 s por request (`:56`); en timeout `sleep(5)` (`:81`); en error de conexión `sleep(5)` (`:86`).
- Paginación de players: `sleep(0.5)` entre páginas (`:350`).
- **No hay presupuesto por liga** ni contador de cuota en esta ruta.

**Ruta A `auto_extractor_v5.py`** (pensada para cuota diaria):
- `RequestCounter(limit=DEFAULT_REQUEST_LIMIT=95)` — `:34,128-148`; se comprueba `hay_espacio()` antes de cada liga y de cada odds (`:519,556`).
- `DELAY_ENTRE_REQUESTS = 1.5` s tras cada request OK — `:35,194-195`.
- En 429: `sleep(60)` (`:182-184`); reintentos con `sleep(5)`/`sleep(3)` (`:200,204`).
- Presupuesto **global** (no por liga); cuando se acaba, "continúa mañana" (`:557`). Estrategia declarada: fixtures primero, odds después (`:8-11`).

### 1.7 Lo que se IGNORA (en vivo)

- Se capturan `status_short`, `status_long`, `elapsed` (`process_fixtures`), pero el pipeline de cálculo **solo consume partidos terminados** (`status_long='Match Finished'`, ver §2) y la ingesta de odds solo mira `status_short='NS'`. No hay polling minuto a minuto ni uso de `elapsed`. **Para el port: puedes descartar `elapsed` y cualquier lógica "en vivo".**

---

## 2. PIPELINE DE CÁLCULO (`sad.db` → `levels.db` → `constants.db` → `discreto.db`)

### 2.1 `levels_calculator.py` — niveles de equipo

**Archivo:** `src/utils/levels_calculator.py` · Clase `LevelsCalculator`.
- **Lee:** `sad.db` (`fixtures` con `status_long == 'Match Finished'`, `teams`). Sesión propia `create_engine('sqlite:///sad.db')` (`:39-41`).
- **Escribe:** `levels.db`, tabla `team_levels` (`:44-47`).
- **Detección de cambios** `detect_changes()` (`:69-115`): "nuevos" = fixtures terminados en `sad.db` cuyo `fixture_id` **no aparece** en `team_levels`. Marca `teams_affected` (ambos equipos). No usa `processed_at`; se basa en presencia del `fixture_id`. Los fixtures modificados **no se detectan** (`:104-106` lo dice: "asumimos que fixtures procesados no cambian").
- **Fórmula de nivel** `_calculate_team_levels_complete` (`:170-251`):
  - Requiere ≥20 partidos terminados; si hay menos → `level = 0.5` para todos (`:198-205`).
  - `points_component` = promedio de puntos (3/1/0) de los últimos 20 (`:216`).
  - `goals_component` = Σ(dif. de gol últimos 5) / Σ(goles totales últimos 5) (`:218-230`); 0 si no hubo goles.
  - **`level = points_component + goals_component + 1`** (`:233`). Rango típico ~[0.5 … ~4-5] (float continuo).
  - En el partido 20 (índice 19) asigna ese nivel retroactivamente a los primeros 20 (`:236-242`).
- **Escritura** `update_team_levels` (`:253-297`): **DELETE** de todo el equipo y **recálculo completo** + `bulk_save_objects`. ⇒ idempotente por equipo (no duplica).
- **Incremental** `calculate_missing_levels` (`:299-339`): solo procesa `teams_affected`, pero **cada equipo se recalcula entero**. `force_recalculate_all` (`:341-383`) borra toda la tabla y recomputa todos.

> **Nota:** la memoria dice "niveles 1-10". Ese `level` continuo NO es 1-10; la escala 0-9 aparece recién en la **discretización** (§2.3). Aquí es un float.

### 2.2 `constants_calculator.py` — constantes q_* / k_*

**Archivo:** `src/utils/constants_calculator.py` · Clase `ConstantsCalculator`.
- **Lee:** `sad.db` (fixtures terminados, `FINISHED_STATUS='Match Finished'` `:75`) + `levels.db` (nivel del **rival** a la fecha del partido, vía `LevelsCalculator.get_team_level_at_date`, envuelto en `get_team_level_safe` `:141-173`).
- **Escribe:** `constants.db`, tabla `constants` (modelo `ConstantResult` `:23-59`), con `CONST_ENGINE` de `database_manager`.
- **Auto-sync de niveles al iniciar:** `_ensure_levels_synced` (`:115-139`) sincroniza `levels.db` antes de calcular ⇒ el orden `levels → constants` queda garantizado internamente.
- **Fórmulas q_*** (`calculate_constants` `:194-295`, réplica en incremental `:578-692`):
  - `nivel` = nivel del rival a la fecha (`:257-260`).
  - `dif = |gf - ga|`; `res = 1/0/-1` (`:262-265`).
  - `q_local = dif*res*nivel` (si juega de local); `q_visita = 1.4*dif*res*nivel` (si visita) (`:268-269`) — factor visitante **1.4** (coincide con `settings.CalculationSettings.visitor_multiplier=1.4`).
  - `q_negativo = dif*res*nivel` si derrota, si no 0 (`:270`).
  - `q_goles_anotado = gf*nivel`; `q_goles_recibido = -ga*nivel`; y sus variantes local/visita (`:273-278`).
- **Acumulación k_*** con **reset a 0 al romperse la racha** (`:297-388` y `:604-666`): p. ej. `if q_any>0: k_p += q_any else: k_p = 0`. Igual para `k_negativo` (acumula si `q_neg<0`), `k_*_local`, `k_*_visita`, `k_goles_*`. Los k local/visita solo se tocan cuando el partido fue en esa condición (`if q_loc is not None:` / `if q_vis is not None:`), evitando contaminación de falsos ceros.
- **Escritura total** `calculate_and_store` (`:389-450`): DELETE de todo el equipo + recompute + insert (idempotente, completo).
- **Escritura incremental** `incremental_calculate_and_store` (`:464-762`):
  - Toma la **última fecha** registrada del equipo (`:478-484`) y **continúa** los acumuladores desde esa última fila (`:492-503`).
  - Procesa solo fixtures con `Fixture.date > start_date` (`:535-541`) e inserta los nuevos (`:699-739`).
  - Si no hay historial → borra y recomputa completo (`:504-514`).

### 2.3 `discretizer_db.py` — matriz discreta final

**Archivo:** `src/data/discretizer_db.py` · Clase `DiscreteDBProcessor`.
- **Lee:** `sad.db` (fixtures terminados por equipo, `_read_matches_for_team` `:123-161`), `constants.db` (k_* por fixture, `_read_constants_for_fixtures` `:175-193`), `levels.db` (nivel por equipo/fixture, `_read_level_single` `:195-217`).
- **Escribe:** `discreto.db`, tabla `processed_matches` (modelo `:21-60`).
- **Discretizador:** `KBinsDiscretizer(n_bins=10, encode='ordinal', strategy='uniform')` ajustado sobre **todos** los `level` de `levels.db` (`create_discretizer` `:101-106`). Salida **0-9** (ordinal), aplicada a `nivel_equipo` y `nivel_rival` (`:252-257`).
- **Fusión de K antes del consumo ML** (`:259-267`): `k = k_positivo + k_negativo` (NaN→0), y análogo `k_local`, `k_visita`. También persiste `k_goles_*` directos.
- **Inserción idempotente:** `INSERT ... ON CONFLICT(fixture_id, equipo_id) DO NOTHING` (`:270-287`), respaldado por `UniqueConstraint('fixture_id','equipo_id')` (`:59`).
- **PRAGMA:** `journal_mode=WAL` en las 4 conexiones (`:81-83`).

> ⚠️ **Quirk crítico:** `process_team_data` **hardcodea `last_date = None`** (`:221`). Existe `get_last_processed_date` (`:85-90`) pero **no se usa**. ⇒ **cada corrida re-lee y re-procesa TODOS los partidos terminados** de cada equipo (barrido completo), y la idempotencia depende solo del `ON CONFLICT DO NOTHING`. No es incremental pese a tener `processed_at` y helper de última fecha. Consecuencia adicional: si un partido ya insertado **cambia** (resultado/fecha corregidos), el `DO NOTHING` **no actualiza** la fila → queda desactualizada.

### 2.4 `database_manager.py` — motores y rutas

**Archivo:** `src/data/database_manager.py`.
- `BASE_DIR = 3 niveles arriba de src/data` (`:18`).
- `ORIG_ENGINE` → `sad.db` (`:21-22`); `CONST_ENGINE` → `constants.db` (`:25-26`).
- `levels.db` y `discreto.db` **no** se definen aquí: se crean ad-hoc en sus módulos usando `BASE_DIR` (`discretizer_db.py:68-69`) o rutas relativas (`levels_calculator` default `'levels.db'`, `constants_calculator.py:105`).
- Sesiones `SessionOrig`, `SessionConst` (`:41-42`).

### 2.5 `regresion_nivel_engine` (Ley de la Regresión al Nivel)

- **No está en el snapshot.** Se **importa** en `pre_match_analysis_window.py:741` (`from regresion_nivel_engine import RegresionNivelEngine`) y se instancia con `sad_db_path` (`:747`), pero **el archivo `regresion_nivel_engine.py` no existe** aquí (verificado). Es un módulo de **consumo/predicción** (lee `sad.db`), fuera del alcance de ingesta. Indicado explícitamente para que otro agente no lo dé por presente.

### 2.6 Orden de ejecución de la cadena completa

Flujo documentado en `proyecto_sad_memoria.txt` (pasos 1-7) y confirmado en código:
1. Extracción fixtures/odds → `sad.db` (§1).
2. `levels_calculator` (auto-sincronizado por `ConstantsCalculator`).
3. `constants_calculator` (incremental por equipo).
4. `discretizer_db` (barrido completo, manual).

**Quién dispara cada etapa:**
- Constantes tras extracción GUI: `extraction_window._auto_calculate_constants` (incremental) `:834-896`.
- Botón "Sincronizar constantes": `data_sync`/`sync_constants` (`extraction_window.py:898`) y `SyncAllTeamsWorker` (`simplified_database_management_dialog.py:21-90`, incremental o `--force`).
- CLI constantes: `calculate_all_constants.py` (menú interactivo, `batch_calculate_teams`).
- Discretizer: **solo** `python discretizer_db.py` (`update_discrete_db` `:365-370`). **No está cableado a ninguna UI** (verificado). Es el eslabón más frágil del pipeline automatizado.

### 2.7 ¿Incremental o total? ¿Idempotente o duplica?

| Etapa | Detección de pendientes | Modo | Idempotencia |
|-------|-------------------------|------|--------------|
| `levels.db` | `fixture_id` ausente en `team_levels` (`detect_changes`) | Incremental por equipo, pero **recalcula todo el historial del equipo** | ✅ DELETE+INSERT por equipo, no duplica |
| `constants.db` | Última `date` registrada del equipo | **Incremental real** (procesa `date > last_date`) | ✅ No duplica en uso normal. ⚠️ 2 aristas: (a) fixtures con **misma fecha-hora exacta** que la última almacenada se saltan por el `>` estricto; (b) resultados corregidos en el **pasado** no se recapturan (solo avanza) |
| `discreto.db` | **Ninguna** (`last_date=None` hardcodeado) | **Total** cada corrida | ✅ `ON CONFLICT DO NOTHING`, no duplica, pero **no actualiza** filas cambiadas y es costoso |

Ninguna etapa produce filas duplicadas en operación normal; el punto débil es la **actualización retroactiva** (resultados que se corrigen después de haber sido procesados) y el barrido completo del discretizer.

---

## 3. ESQUEMAS COMPLETOS DE LAS 4 DBs

> Los esquemas reales se crean con `Base.metadata.create_all(...)` (SQLAlchemy) salvo `auto_extractor_v5.py` que usa DDL sqlite3 directo. SQLite aplica *type affinity*; abajo se da el `CREATE TABLE` canónico equivalente. Índices y PRAGMA incluidos.

### 3.1 `sad.db`

**`teams`** — `src/data/data_models/teams.py:5-13`
```sql
CREATE TABLE teams (
    id      INTEGER PRIMARY KEY,
    name    VARCHAR,
    country VARCHAR,
    founded INTEGER,
    logo    VARCHAR
);
```

**`fixtures`** — `src/data/data_models/fixtures.py:6-41`
```sql
CREATE TABLE fixtures (
    id                INTEGER PRIMARY KEY,
    referee           VARCHAR,
    timezone          VARCHAR,
    date              DATETIME,
    timestamp         INTEGER,
    first_half_start  INTEGER,
    second_half_start INTEGER,
    venue_id          INTEGER,
    venue_name        VARCHAR,
    venue_city        VARCHAR,
    status_long       VARCHAR,
    status_short      VARCHAR,
    elapsed           INTEGER,
    league_id         INTEGER,
    league_season     INTEGER,
    league_round      VARCHAR,
    home_team_id      INTEGER REFERENCES teams(id),
    away_team_id      INTEGER REFERENCES teams(id),
    goals_home        INTEGER,
    goals_away        INTEGER,
    halftime_home     INTEGER,
    halftime_away     INTEGER,
    fulltime_home     INTEGER,
    fulltime_away     INTEGER,
    extratime_home    INTEGER,
    extratime_away    INTEGER,
    penalty_home      INTEGER,
    penalty_away      INTEGER
);
```
> El DDL sqlite3 de `auto_extractor_v5.py:248-296` es equivalente pero **sin** `referee`, y añade índices `idx_fixtures_league(league_id)`, `idx_fixtures_date(date)`. `first_half_start/second_half_start/extratime_*/penalty_*` existen en el modelo pero **no** los rellena `process_fixtures` (quedan NULL).

**`odds`** — `src/data/data_models/odds.py:8-21`
```sql
CREATE TABLE odds (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id     INTEGER NOT NULL REFERENCES fixtures(id),
    league_id      INTEGER,
    bookmaker_id   INTEGER,
    bookmaker_name VARCHAR,
    bet_id         INTEGER,
    bet_name       VARCHAR,
    value          VARCHAR,   -- "Home","Draw","Away","Over 2.5",...
    odd            FLOAT
);
CREATE INDEX ix_odds_fixture_id ON odds (fixture_id);  -- index=True en el modelo
-- auto_extractor_v5 crea además: CREATE INDEX idx_odds_fixture ON odds(fixture_id)
```
> **No hay UNIQUE constraint**; la unicidad `(fixture_id, bookmaker_id, bet_id, value)` es solo lógica de app (§1.4).

**`leagues`** — `src/data/data_models/leagues.py:8-19`
```sql
CREATE TABLE leagues (
    id      INTEGER PRIMARY KEY,
    name    VARCHAR,
    country VARCHAR,
    logo    VARCHAR,
    flag    VARCHAR,
    season  INTEGER
);
```

**`players`** — `src/data/data_models/players.py:5-23`
```sql
CREATE TABLE players (
    id          INTEGER PRIMARY KEY,
    name        VARCHAR, firstname VARCHAR, lastname VARCHAR,
    age         INTEGER,
    birth_date  VARCHAR, birth_place VARCHAR, nationality VARCHAR,
    height      VARCHAR, weight VARCHAR,
    injured     BOOLEAN,
    photo       VARCHAR,
    team_id     INTEGER REFERENCES teams(id)
);
```

**`player_statistics`** — `src/data/data_models/player_statistics.py:6-53` (36+ columnas)
```sql
CREATE TABLE player_statistics (
    id INTEGER PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    team_id   INTEGER REFERENCES teams(id),
    league_id INTEGER, season INTEGER,
    games_appearences INTEGER, games_lineups INTEGER, games_minutes INTEGER,
    games_number INTEGER, games_position VARCHAR, games_rating FLOAT, games_captain BOOLEAN,
    substitutes_in INTEGER, substitutes_out INTEGER, substitutes_bench INTEGER,
    shots_total INTEGER, shots_on INTEGER,
    goals_total INTEGER, goals_conceded INTEGER, goals_assists INTEGER, goals_saves INTEGER,
    passes_total INTEGER, passes_key INTEGER, passes_accuracy VARCHAR,
    tackles_total INTEGER, tackles_blocks INTEGER, tackles_interceptions INTEGER,
    duels_total INTEGER, duels_won INTEGER,
    dribbles_attempts INTEGER, dribbles_success INTEGER, dribbles_past INTEGER,
    fouls_drawn INTEGER, fouls_committed INTEGER,
    cards_yellow INTEGER, cards_yellowred INTEGER, cards_red INTEGER,
    penalty_won INTEGER, penalty_committed INTEGER, penalty_scored INTEGER,
    penalty_missed INTEGER, penalty_saved INTEGER
);
```

**`team_statistics`** — `src/data/data_models/statistics.py:9-63`
```sql
CREATE TABLE team_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    league_id INTEGER, season INTEGER,
    form VARCHAR,
    played_home INTEGER, played_away INTEGER, played_total INTEGER,
    wins_home INTEGER, wins_away INTEGER, wins_total INTEGER,
    draws_home INTEGER, draws_away INTEGER, draws_total INTEGER,
    loses_home INTEGER, loses_away INTEGER, loses_total INTEGER,
    goals_for_home INTEGER, goals_for_away INTEGER, goals_for_total INTEGER,
    goals_against_home INTEGER, goals_against_away INTEGER, goals_against_total INTEGER,
    clean_sheet_home INTEGER, clean_sheet_away INTEGER, clean_sheet_total INTEGER,
    failed_to_score_home INTEGER, failed_to_score_away INTEGER, failed_to_score_total INTEGER
);
CREATE INDEX ix_team_statistics_team_id ON team_statistics (team_id);
```

> **Aviso sobre `team_levels` y `sad.db`:** el modelo `team_levels.py` usa el **mismo `Base`** que `teams`/`fixtures`. Como `database_manager.py:11` importa `team_levels` y `init_db('orig')` haría `create_all(ORIG_ENGINE)`, la tabla `team_levels` **podría** crearse también dentro de `sad.db`. Sin embargo, los niveles **reales** viven en `levels.db` (los escribe `LevelsCalculator`). En el port, dejar `team_levels` únicamente en `levels.db`.

### 3.2 `levels.db`

**`team_levels`** — `src/data/data_models/team_levels.py:8-15`
```sql
CREATE TABLE team_levels (
    id         INTEGER PRIMARY KEY,
    team_id    INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    date       DATETIME NOT NULL,
    level      FLOAT NOT NULL
);
```
Creada con `LevelBase.metadata.create_all(levels_engine, checkfirst=True)` (`levels_calculator.py:45`). Sin índices explícitos ni PRAGMA definidos en el módulo.

### 3.3 `constants.db`

**`constants`** — `constants_calculator.py:23-59`
```sql
CREATE TABLE constants (
    id         INTEGER PRIMARY KEY,
    team_id    INTEGER NOT NULL,
    fixture_id INTEGER NOT NULL,
    date       DATETIME NOT NULL,
    -- valores q (instantáneos, por partido)
    q_local FLOAT, q_visita FLOAT, q_negativo FLOAT,
    q_goles_anotado FLOAT, q_goles_recibido FLOAT,
    q_goles_local_anotado FLOAT, q_goles_local_recibido FLOAT,
    q_goles_visita_anotado FLOAT, q_goles_visita_recibido FLOAT,
    -- constantes k (acumuladas con reset)
    k_positivo FLOAT, k_negativo FLOAT,
    k_positivo_local FLOAT, k_negativo_local FLOAT,
    k_positivo_visita FLOAT, k_negativo_visita FLOAT,
    k_goles_anotado FLOAT, k_goles_recibido FLOAT,
    k_goles_local_anotado FLOAT, k_goles_local_recibido FLOAT,
    k_goles_visita_anotado FLOAT, k_goles_visita_recibido FLOAT
);
CREATE INDEX ix_constants_team_id ON constants (team_id);
CREATE INDEX ix_constants_fixture_id ON constants (fixture_id);
CREATE INDEX ix_constants_date ON constants (date);
CREATE INDEX ix_constants_team_date    ON constants (team_id, date);
CREATE INDEX ix_constants_fixture_team ON constants (fixture_id, team_id);
```
(Índices compuestos en `:56-59`; los simples por `index=True` en `:27-29`.) Columnas esperadas confirmadas por `migrate_constants_db.py:28-49` (herramienta de migración/diagnóstico con `--diagnose/--migrate/--recalc-all/--recalc-team`).

### 3.4 `discreto.db`

**`processed_matches`** — `discretizer_db.py:21-60`
```sql
CREATE TABLE processed_matches (
    id INTEGER PRIMARY KEY,
    fecha DATETIME NOT NULL,
    fixture_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    equipo_nombre VARCHAR NOT NULL,
    rival_id INTEGER NOT NULL,
    rival_nombre VARCHAR NOT NULL,
    condicion VARCHAR,            -- 'Local' | 'Visita'
    status_long VARCHAR,
    league_id INTEGER,
    league_season VARCHAR,
    goals_home INTEGER,
    goals_away INTEGER,
    nivel_equipo INTEGER,         -- discretizado 0-9
    nivel_rival INTEGER,          -- discretizado 0-9
    k FLOAT, k_local FLOAT, k_visita FLOAT,  -- k_positivo + k_negativo (fusionadas)
    k_goles_anotado FLOAT, k_goles_recibido FLOAT,
    k_goles_local_anotado FLOAT, k_goles_local_recibido FLOAT,
    k_goles_visita_anotado FLOAT, k_goles_visita_recibido FLOAT,
    processed_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    CONSTRAINT uq_fixture_equipo UNIQUE (fixture_id, equipo_id)
);
CREATE INDEX idx_fecha_equipo ON processed_matches (fecha, equipo_id);
CREATE INDEX idx_status       ON processed_matches (status_long);
CREATE INDEX idx_fixture      ON processed_matches (fixture_id);
CREATE INDEX idx_league       ON processed_matches (league_id);
-- PRAGMA aplicado en runtime a las 4 conexiones:
PRAGMA journal_mode=WAL;
```

---

## 4. CASOS BORDE Y LIMPIEZA DE DATOS

### 4.1 Dos convenciones de "terminado" (¡importante!)

- **Pipeline de cálculo** (levels, constants, discretizer): filtra por **`status_long == 'Match Finished'`** (`constants_calculator.py:75,234`, `levels_calculator.py:83,126`, `discretizer_db.py:144,342`).
- **Sync de resultados** (ruta C): considera pendiente lo que **NO** está en `status_short IN ('FT','AET','PEN')` (`data_sync_dialog.py:178`).
- **Consumo ML Anticulebra:** `status_short = 'FT'` (`anticulebra_engine.py:543`).
- Consecuencia: partidos resueltos en prórroga/penales (AET/PEN) igualmente tienen `status_long='Match Finished'` en la API, así que el pipeline los toma. Pero la mezcla de criterios puede causar desajustes si la API entrega combinaciones raras.

### 4.2 Aplazados / suspendidos / AWD / WO

- **No hay tratamiento explícito** de `PST` (postponed), `SUSP`, `CANC`, `ABD`, `AWD` (awarded), `WO` (walkover). Simplemente **no cumplen `status_long='Match Finished'`** y quedan **excluidos** de levels/constants/discretizer. (Verificado: no hay ramas que los nombren.)
- ⚠️ En ruta C, un partido `PST/AWD/WO` cae en `status_short NOT IN ('FT','AET','PEN')` y se marca como "resultado desactualizado" (`data_sync_dialog.py:146-212`), por lo que el sync intentará **re-descargarlo indefinidamente** hasta que la API lo cierre. No es un bug fatal, pero genera gasto de requests.
- AWD/WO pueden traer goles adjudicados; como no se procesan, **no impactan** las K (lo cual puede ser deseable o no según metodología — no está decidido en código).

### 4.3 Duplicados

- `fixtures`, `teams`, `leagues`, `players`: `session.merge` por PK (`api_database_manager.py:53-63,101-107,273-277`) o `INSERT OR REPLACE` (ruta A) ⇒ sin duplicados; el `id` de API es la clave.
- `odds`: dedup **solo lógica** por `(fixture_id, bookmaker_id, bet_id, value)` (§1.4). Sin UNIQUE en DB ⇒ riesgo de duplicado si se inserta por fuera de esas funciones.
- `player_statistics` / `team_statistics`: upsert manual por `(player/team, league, season)` (`api_database_manager.py:112-129,171-186`).

### 4.4 Equipos renombrados

- Los equipos se identifican por `id`; un cambio de nombre solo actualiza `name` vía merge/REPLACE. El historial (fixtures, levels, constants) se mantiene ligado por `id`. No rompe nada.

### 4.5 Fixtures que cambian de fecha

- **constants incremental:** clave por `date > last_date`. Si un fixture ya procesado **cambia a una fecha anterior**, no se recaptura (el acumulador no se rehace). Si cambia a fecha posterior y ya estaba insertado, podría reprocesarse como "nuevo" (posible inconsistencia de racha).
- **levels:** solo se rehace el equipo si un fixture **nuevo** (id no visto) lo marca; un mero cambio de fecha de un fixture ya conocido no dispara recálculo.
- **discreto:** reprocesa todo pero `ON CONFLICT DO NOTHING` ⇒ **no** actualiza la fila existente con la nueva fecha (queda stale).
- **Recomendación port:** añadir detección por "firma" del fixture (fecha+goles+status) —ya hay un esbozo sin usar en `levels_calculator.get_fixture_signature` `:51-67`— y hacer los upserts `DO UPDATE` en lugar de `DO NOTHING`.

### 4.6 Fechas / zonas horarias

- Fixtures se guardan parseando el string ISO de la API con `datetime.fromisoformat(date.replace('Z','+00:00'))` (`extraction_window.py:145-151`, `data_processing.py`), es decir se conserva el offset original de la API (normalmente UTC). SQLite almacena como texto.
- `get_fixtures_by_date` fuerza `timezone='America/Lima'` (`api_fetcher.py:152`); `get_fixtures` (el usado en el pipeline) **no** pasa `timezone`.
- Ruta C construye ventanas en **Lima (UTC-5)** y las convierte a UTC para comparar contra `f.date` (`data_sync_dialog.py:222-233`) — asume que `f.date` está en UTC.
- El discretizer parsea `'%Y-%m-%d %H:%M:%S'` recortando fracciones de segundo, con fallback `fromisoformat` (`discretizer_db.py:108-121`).
- ⚠️ **Riesgo:** manejo mixto de tz (algunas rutas asumen UTC naive, otras aware). Al portar a FastAPI conviene **normalizar todo a UTC aware** en la ingesta y guardar timestamps ISO consistentes.

---

## 5. CONFIGURACIÓN Y DEPENDENCIAS

### 5.1 Dependencias

**No hay `requirements.txt`, `pyproject.toml` ni `setup.py` en el snapshot** (verificado). Las versiones **no están fijadas** en ningún sitio; hay que inferirlas. Paquetes de terceros efectivamente importados (conteo de imports):

- `PySide6` (GUI; la memoria dice "PyQt6" pero **el código usa PySide6** — corregir el dato).
- `SQLAlchemy` (usa `sqlalchemy.ext.declarative.declarative_base` —legacy, válido en 1.4 y 2.0 con deprecación— y `create_engine(..., future=True)` en el discretizer ⇒ requiere **SQLAlchemy ≥ 1.4**).
- `scikit-learn` (`KBinsDiscretizer(encode='ordinal', strategy='uniform')`, `GradientBoosting*`, etc.).
- `pandas`, `numpy`, `scipy`.
- `joblib` (carga de modelos `.joblib` en la capa de predicción).
- `requests` (cliente HTTP de ingesta).
- `matplotlib`, `pyqtgraph` (gráficos GUI — no necesarios para ingesta).
- `python-dateutil` (`dateutil`).

`requirements.txt` sugerido para **solo el port de ingesta + cálculo** (sin GUI):
```
requests>=2.31
SQLAlchemy>=1.4,<3
pandas>=1.5
numpy>=1.23
scikit-learn>=1.1     # necesario solo para discretizer_db.py (KBinsDiscretizer)
python-dateutil>=2.8
```
> `PySide6`, `matplotlib`, `pyqtgraph`, `joblib`, `scipy` NO hacen falta para ingesta+cálculo puros. Verificar la versión de sklearn contra la usada para entrenar los modelos si además se porta la predicción.

### 5.2 Variables de entorno / config

- **`API_KEY`** (obligatoria) — `api_config.py:8`. Sin ella, `get_api_headers` lanza `ValueError` (`:61-65`).
- **`DATABASE_PATH`** (opcional, default `sad.db`) — `auto_extractor_v5.py:30`.
- `settings.py` lee opcionalmente: `TEAMS_PER_PAGE`, `SEARCH_DEBOUNCE_MS`, `MAX_CACHE_SIZE`, `DB_BATCH_SIZE`, `DB_TIMEOUT`, `DB_LOGGING`, `DEFAULT_LEVEL`, `VISITOR_MULTIPLIER` (default **1.4**), `PARALLEL_WORKERS` (`settings.py:44-59`). Para ingesta casi ninguna es crítica salvo, quizá, `VISITOR_MULTIPLIER` (aunque el `1.4` está **hardcodeado** en `constants_calculator.py:269,594`, no leído de settings).
- Constantes de cuota/reintentos: `MAX_RETRIES=3`, `RATE_LIMIT_DELAY=60`, `PREFERRED_BOOKMAKERS` (`api_config.py:17-21`); `DEFAULT_REQUEST_LIMIT=95`, `DELAY_ENTRE_REQUESTS=1.5`, `SEASON=2025`, `DIAS_ATRAS=3`, `DIAS_ADELANTE=10` (`auto_extractor_v5.py:30-100`).

### 5.3 Cómo se lanza hoy el pipeline (comando/botón exacto)

**No existe un único orquestador end-to-end.** Se ejecuta por partes:

1. **App GUI completa:** `python src/updated_main.py` (entry `if __name__=='__main__': sys.exit(main())` `updated_main.py:653+`; agrega `src` al path `:33`). Menú principal → botón **"Extracción"** (`open_extraction` → `ExtractionWindow` `:434-442`) o **"Gestión BD"** (`open_database_management` `:457-464`). Desde ahí, extracción de fixtures dispara auto-constantes; odds es manual.
2. **Ingesta automática (recomendada para cron/port):**
   - `python src/data/auto_extractor_v5.py` → fixtures + odds.
   - `python src/data/auto_extractor_v5.py --fixtures` (solo fixtures) / `--odds` (solo odds) / `--limit N` / `--db ruta` / `--dry-run` (`:592-600`).
3. **Constantes (masivo):** `python calculate_all_constants.py` (menú interactivo 1-4 `calculate_all_constants.py:69-134`).
4. **Niveles:** se auto-sincronizan al instanciar `ConstantsCalculator`; standalone `python src/utils/levels_calculator.py` (`quick_update_levels` `:557-579`).
5. **Discretización:** `python src/data/discretizer_db.py` (`update_discrete_db` `:373-374`). **Paso manual, no cableado a UI.**
6. Verificación/backfill dirigido: diálogo "Verificación de Datos Pendientes" (`DataSyncDialog`, `data_sync_dialog.py:710`).

**Secuencia mínima reproducible para el port** (equivalente a "correr todo"):
```
export API_KEY=...            # NO uses el fallback hardcodeado
python src/data/auto_extractor_v5.py          # sad.db: fixtures + odds
python calculate_all_constants.py             # levels.db (auto) + constants.db  (opción 1 o 2)
python src/data/discretizer_db.py             # discreto.db
```

---

## 6. LO QUE NO ESTÁ EN EL CÓDIGO

### 6.1 Documentos referenciados por el usuario

- **`formula_constantes_SAD_v2.docx`** y **`ley_regresion_nivel.docx`**: **no están en el snapshot** (verificado: no hay `.docx`/`.doc`/`.md`). No puedo resumir su contenido; habría que aportarlos por separado. Lo relevante para la ingesta que sí pude derivar del código está en §2.1-§2.3 (fórmulas de nivel, q_* y k_*).
- **SAD Manual** (`reglas_core.md`, `checklist.md`, etc. según la memoria): **no presentes**. Son metodología de análisis/apuestas, no de ingesta.
- **`proyecto_sad_memoria.txt`** (sí presente): resume el flujo típico (extracción → almacenamiento → constantes → discretización → entrenamiento → predicción → simulación) y describe las DBs. Confirma el layout de raíz (`sad.db`, `constants.db`, `levels.db`, `model_exports/`, `leagues2024.csv` junto a `src/`). Útil como índice, no aporta fórmulas nuevas de ingesta.

### 6.2 Archivos importados pero ausentes / referenciados fuera del código

- **`regresion_nivel_engine.py`**: importado (`pre_match_analysis_window.py:741`), **no existe** en el snapshot. Módulo de predicción, no de ingesta.
- **`config/season_mapping.py`**: mencionado en la memoria, **no existe** aquí. Si el port necesita mapeo año-natural vs año-cruzado por liga, hay que crearlo (hoy no hay lógica que lo resuelva).
- **`model_exports/`** (`level_discretizer.joblib`, modelos `.joblib`, params `.json`): referenciado por `global_constant_predictor.py:101,122-172`, **no incluido** en el snapshot. Necesario para predicción, **no** para ingesta. Nota: el discretizer de niveles se recrea desde `levels.db` si el `.joblib` no existe (`global_constant_predictor.py:135-172`), replicando exactamente los parámetros de `discretizer_db.py` (10 bins, uniform).

### 6.3 Riesgos y rarezas que quien porte esto DEBE saber

1. **🔴 API key hardcodeada** en `auto_extractor_v5.py:28` (fallback en texto plano). Rotar la clave y eliminar el fallback.
2. **🔴 Discretizer no incremental y no automatizado:** `last_date=None` hardcodeado (`discretizer_db.py:221`) ⇒ barrido completo cada vez; y no está cableado a ninguna UI (solo `__main__`). En una app web hay que reescribir esto como paso incremental y programado, y cambiar `ON CONFLICT DO NOTHING` por `DO UPDATE` si se quieren reflejar correcciones.
3. **🟠 Odds: dos comportamientos incompatibles.** `auto_extractor_v5` guarda **todos** los bookmakers (1 request); `get_odds_with_fallback` (GUI/sync) guarda **un solo** bookmaker por fixture (secuencial, gasta cuota y empobrece datos). Unificar en el port hacia el modelo "todos los bookmakers en 1 request".
4. **🟠 Sin promedio de cuotas en ingesta.** La agregación real es **MAX (mejor cuota)** filtrando `bet_name='Match Winner'` en la capa de consumo (`anticulebra_engine.py:572-574`). Si la app web espera "promedio de casas", hay que implementarlo (no existe).
5. **🟠 Tres listas de ligas divergentes** (`api_config.LEAGUE_REGIONS`, `data_sync_dialog.LIGAS_CONFIG`, `auto_extractor_v5.LIGAS_CONFIG`) + etiquetas de bookmaker inconsistentes (`26` = "bet365" en `api_config.py:21` pero "Betsson" en `auto_extractor_v5.py:42`). Consolidar en una sola fuente de verdad.
6. **🟠 Temporada como entero único** no resuelve ligas de año cruzado (europeas 2025/26) vs año natural (Sudamérica). Añadir mapeo por liga.
7. **🟠 Actualizaciones retroactivas no propagadas:** constants incremental solo avanza por `date >`; discretizer no actualiza; levels solo se rehace con fixtures nuevos. Un resultado corregido a posteriori puede dejar K/discreto desactualizados. Aristas adicionales: fixtures con **misma fecha-hora exacta** que el último procesado se saltan (`>` estricto en `constants_calculator.py:537`).
8. **🟡 Zonas horarias mixtas** (UTC naive vs Lima UTC-5, ver §4.6). Normalizar a UTC aware.
9. **🟡 Estados no-terminados sin manejo** (PST/SUSP/AWD/WO): excluidos del cálculo y potencialmente reintentados en bucle por el sync (§4.2).
10. **🟡 `odds` sin UNIQUE constraint** en DB (dedup solo lógica). Añadir índice único `(fixture_id, bookmaker_id, bet_id, value)` en el port para robustez.
11. **🟡 Modelo `team_levels` comparte `Base` con `sad.db`** y podría materializarse en `sad.db` además de en `levels.db` (§3.1). Mantenerlo solo en `levels.db`.
12. **🟡 Doc vs código:** la memoria dice PyQt6; el código es **PySide6**. Y "niveles 1-10" en realidad es `level` float en `levels.db` y **0-9 ordinal** solo tras el discretizer.
13. **🟡 `_make_request` trata cualquier `data['errors']` no vacío como fallo y retorna `None`** (`api_fetcher.py:68-75`); útil, pero conviene loguear el motivo (cuota agotada vs restricción de plan) para el failover que la memoria describe pero que aquí no existe.

---

### Anexo — Trazabilidad de afirmaciones clave

| Afirmación | Referencia |
|-----------|-----------|
| Base URL / host RapidAPI | `api_config.py:11,14` |
| API key por env (canónico) | `api_config.py:8`, `get_api_headers` `:59-69` |
| API key hardcodeada (riesgo) | `auto_extractor_v5.py:28` |
| `/fixtures` con `league,season,from,to` | `api_fetcher.py:125-137`, `auto_extractor_v5.py:208-217` |
| `/odds` todos los bookmakers (1 req) | `auto_extractor_v5.py:219-223` |
| `/odds` un bookmaker con fallback | `api_fetcher.py:229-266`, `PREFERRED_BOOKMAKERS` `api_config.py:21` |
| Odds prepartido: NS + ventana 72h / 10d | `data_sync_dialog.py:216-250`, `auto_extractor_v5.py:448-467,542` |
| Selección de cuota = MAX (no promedio) | `anticulebra_engine.py:543,572-574` |
| Fórmula de nivel | `levels_calculator.py:216-233` |
| Fórmulas q_* / k_* con reset | `constants_calculator.py:268-388` |
| Incremental constants por fecha | `constants_calculator.py:478-541` |
| Discretizer 10 bins + fusión k | `discretizer_db.py:104,259-267` |
| Discretizer `last_date=None` (no incremental) | `discretizer_db.py:221` |
| ON CONFLICT DO NOTHING | `discretizer_db.py:286` |
| Rutas de DB (BASE_DIR 3 niveles) | `database_manager.py:18-26`, `discretizer_db.py:68-69` |
| `regresion_nivel_engine` ausente | import en `pre_match_analysis_window.py:741`, archivo inexistente |
| Sin requirements.txt | verificado (no hay `require*/pyproject/setup`) |
