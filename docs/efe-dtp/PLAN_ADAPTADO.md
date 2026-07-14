# EFE + DTP en la webapp — plan adaptado a este repo

Adaptación de `ARQUITECTURA_ORIGINAL.md` (diseñada en claude.ai) al stack real
de este proyecto. La idea central se mantiene intacta: **el modelo devuelve
JSON, el frontend renderiza con componentes fijos, y una capa de caché evita
re-investigar y re-analizar** (ahorro 70-80% en salida + 90% en system con
prompt caching). Lo que cambia es el encaje.

## Diferencias con el diseño original (y por qué)

| Original | Aquí | Razón |
|---|---|---|
| Postgres en Railway | **SQLite `efe.db` en el volumen** (junto a sad.db) | Cero infra nueva; mismo patrón WAL que ya usamos; Postgres queda para la fase nube (`docs/SERVICIOS_EXTERNOS.md`) |
| Backend Node/Express o FastAPI nuevo | **Módulo `backend/analisis/` en el FastAPI existente** | Un solo servicio = un solo volumen (regla de Railway). La regla del repo "el HTTP es de solo lectura" aplica a las DBs del SAD; `efe.db` es de esta capa y la escribe solo `backend/analisis/` |
| Frontend Next.js aparte | **Sección nueva en la SPA existente** (React+Vite) | Los componentes fijos (`GaugeRing`, `PizarraGol`, `MapaDuelos`…) se portan como componentes de `src/components/efe/` |
| `claude-sonnet-4-6` | **`claude-sonnet-5`** | Más nuevo y mejor en razonamiento; precio intro $2/$10 por MTok hasta 2026-08-31 (luego $3/$15, igual que 4.6). En Sonnet 5 el thinking adaptativo viene activo por defecto y NO se aceptan `temperature`/`top_p` |
| `claude-haiku-4-5-20251001` (extracción) | `claude-haiku-4-5` (alias) | Mismo modelo, alias estable ($1/$5) |
| `web_search_20250305` | **`web_search_20260209`** | Versión vigente en Sonnet 5, con filtrado dinámico integrado (filtra resultados antes de que entren al contexto → menos tokens). ~$10/1000 búsquedas + tokens |
| "salida exclusivamente JSON por disciplina de prompt" | **Structured outputs** (`output_config.format` con `json_schema`) | La API ya GARANTIZA JSON válido contra el esquema — se acabó el "sin preámbulo, sin backticks" frágil. Los esquemas EFE_COMPARATIVO / DTP / MATRIZ_V2 del system prompt pasan a JSON Schema formales |
| fetch crudo a api.anthropic.com | **SDK oficial `anthropic` (Python)** | Reintentos 429/5xx automáticos, tipos, streaming. `pip install anthropic` |

El prompt caching queda igual que en el diseño original (dos bloques system con
`cache_control: {type: "ephemeral"}`; lecturas a 0.1× del precio de input,
escritura 1.25×; TTL ~5 min renovado con cada uso). Verificar con
`response.usage.cache_read_input_tokens`.

## Esquema SQLite (equivalente del Postgres original)

```sql
-- investigación con TTL por tipo (dt/plantel 14d · tabla/resultados 24h ·
-- fixture 7d · xi/bajas 48h y SIEMPRE refrescar el día del partido)
CREATE TABLE IF NOT EXISTS investigacion (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  equipo TEXT NOT NULL, tipo TEXT NOT NULL,
  contenido TEXT NOT NULL,          -- JSON
  fuentes TEXT,                     -- JSON array
  capturado_en TEXT NOT NULL,
  UNIQUE (equipo, tipo)
);
CREATE TABLE IF NOT EXISTS analisis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL,               -- efe | dtp | matriz
  equipo_a TEXT, equipo_b TEXT, fecha_partido TEXT,
  resultado_json TEXT NOT NULL, version_efe TEXT DEFAULT '1.5',
  creado_en TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cadena_dtp (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  equipo_foco TEXT NOT NULL, partido_n INTEGER NOT NULL,
  rival TEXT, fecha TEXT,
  apertura_json TEXT, cierre_json TEXT, registro TEXT,
  UNIQUE (equipo_foco, partido_n)
);
CREATE TABLE IF NOT EXISTS casos_validacion (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  caso_num INTEGER, partido TEXT, fecha TEXT,
  que_acerto TEXT, que_fallo TEXT, correccion_derivada TEXT
);
```

## Endpoints (módulo `backend/analisis/`)

| Endpoint | Modo API | Nota |
|---|---|---|
| `POST /api/efe` | `efe` | consulta caché → `campos_faltantes` → web search solo si falta |
| `POST /api/dtp` | `dtp_apertura` / `dtp_completo` | según haya N−1 en `cadena_dtp` |
| `POST /api/cierre` | `dtp_completo` + resultado real | valida el pronóstico, escribe registro |
| `POST /api/matriz` | `matriz` | input = JSON del EFE guardado, **sin** web search |
| `GET /api/partido/{id}` | — | lee de `analisis`, cero créditos |

Los POST van protegidos con `SAD_API_TOKEN` (ya existe) — cada llamada cuesta
dinero real, nadie sin token debe poder dispararlas.

## Costo por análisis (Sonnet 5, precio intro, caché caliente)

| Componente | Aprox |
|---|---|
| System ~14k en cache read | ~$0.003 |
| Datos cacheados + request ~4k input | ~$0.008 |
| Salida JSON ~2.5k | ~$0.025 |
| **EFE con datos frescos en DB** | **~$0.04** |
| **EFE con web search (4-6 búsquedas)** | **~$0.10-0.20** |

La Matriz sale casi gratis (~$0.03): sin investigación, solo el JSON del EFE
como input. 150 partidos/mes con mezcla realista ≈ **$10-25/mes**.

## Cómo se organiza la información

### Tres niveles, del más crudo al más elaborado

```
NIVEL 1 · investigacion   hechos por equipo, con fecha y fuente (reutilizables)
NIVEL 2 · analisis        veredictos por partido (inmutables, con versión EFE)
NIVEL 3 · cadena_dtp      la historia por equipo foco (pronóstico → validación → lección)
```

**Nivel 1 — `investigacion` (hechos).** Una fila por (equipo, tipo): `dt`,
`plantel`, `xi_reciente`, `resultados`, `tabla`, `fixture`, `bajas`. Cada fila
guarda el JSON normalizado, sus fuentes y `capturado_en`. Es la despensa: el
EFE de Universitario y el de Alianza del mismo fin de semana comparten la
misma investigación de tabla/resultados sin repetir búsquedas. La frescura la
decide el TTL por tipo (dt/plantel 14 días, tabla/resultados 24 h, fixture 7
días, xi/bajas 48 h y SIEMPRE refresco el día del partido). Lo vencido se
marca como `campos_faltantes` y solo ESO habilita web search en la llamada.

**Nivel 2 — `analisis` (veredictos).** Una fila por análisis emitido: tipo
(`efe`/`dtp`/`matriz`), equipos, `fecha_partido`, el JSON completo del esquema
y `version_efe`. Inmutable: lo emitido con v1.5 queda como v1.5 para siempre
(auditoría de calibración). Se enlaza con la app por el **fixture_id de
sad.db**: la página del partido pregunta `GET /api/partido/{fixtureId}` y si
ya hay análisis lo pinta gratis, cero créditos.

**Nivel 3 — `cadena_dtp` (la película).** Una fila por (equipo_foco, N):
`apertura_json` (M1-M3+M6 pre-partido), `cierre_json` (M4+M5 post),
`registro` {pronóstico, qué pasó, veredicto, lección}. El endpoint `/api/dtp`
mira aquí si existe N−1 con cierre pendiente para armar la cadena rodante; el
`/api/cierre` completa la fila y su lección alimenta el siguiente M3.
`casos_validacion` guarda los casos numerados (1, 2, …) que calibran versiones.

### Los prompts viven en el repo, no en la DB

`EFE_v1_5_prompt.md` (protocolo, bloque 1 del system) y
`SYSTEM_PROMPT_SAD_API.md` (instrucciones API, bloque 2) se leen del disco al
arrancar y van con `cache_control` — versionados con git, un solo archivo por
versión, la caché se regenera sola al cambiar. Los esquemas JSON
(EFE_COMPARATIVO, DTP, MATRIZ_V2) van como JSON Schema en
`backend/analisis/esquemas.py` y se pasan como structured output.

### Flujo de una llamada a POST /api/efe {fixtureId}

```
1. ¿ya hay analisis para ese fixture?  → devolver (0 créditos)
2. leer investigacion de ambos equipos → separar fresco / vencido / ausente
3. armar request: system cacheado + user {modo, partido, datos_cacheados,
   campos_faltantes} · web_search SOLO si hay faltantes (max_uses 6)
4. structured output contra el esquema → JSON válido garantizado
5. guardar: datos nuevos → investigacion (UPSERT) · veredicto → analisis
6. devolver el JSON al frontend
```

### En la pantalla (diseño propio, tema Quipu)

Sección **"Análisis"** en la página del partido, junto a Cuotas/Burbujas:

- **Cabecera comparativa**: dos anillos (gauge) con % y clasificación
  🟢/🟡/🔴, uno por equipo, con los colores del club.
- **Pestañas**: Bloques (A-H expandibles con ✅/🔶/❌ y justificación+fuente) ·
  Disponibilidad (tabla F1, barras de reducción por zona, badge IP, F4/F5) ·
  Matchup (H1-H3) · Lectura SAD (4 cajas + Paradoja + alertas con su código) ·
  Calendario (G1 con etiquetas).
- **DTP debajo**: CIERRE del partido anterior (pizarra de goles
  disparador→secuencia→definición + responsables) y APERTURA (mapa de duelos
  por carril, plan por fases). **Matriz** bajo demanda.
- **Estado vacío honesto** (regla "real o nada"): sin análisis no se pinta
  nada inventado — botón "Generar análisis EFE" (POST protegido con
  SAD_API_TOKEN) con el costo estimado visible. En modo demo, un análisis de
  muestra fijo para desarrollo de UI.

## Lo que falta para poder construir (lo aporta el usuario)

1. **`EFE_v1_5_prompt.md`** — el protocolo completo (bloques, pesos, alertas,
   casos). Es el bloque 1 del system prompt y NO vino en la entrega; sin él el
   backend no puede analizar. Va al repo como `docs/efe-dtp/EFE_v1_5_prompt.md`
   (fuente única, se copia desde el proyecto de claude.ai en cada versión).
2. **Los últimos `efe_dashboard.jsx` y `dtp_*.jsx`** generados en claude.ai —
   base para portar los componentes fijos al frontend.
3. **`ANTHROPIC_API_KEY`** como variable en Railway (de console.anthropic.com,
   con presupuesto/límite mensual puesto en la consola). Jamás con prefijo
   VITE_ ni en el repo — misma regla que API_FOOTBALL_KEY.

## Orden de construcción propuesto

1. `backend/analisis/`: DB + cliente Anthropic (SDK, caching, structured
   outputs) + `POST /api/efe` con modo mock si no hay API key (para test_api).
2. Contrato en `docs/openapi.yaml` (sección análisis) + tipos del front.
3. Port de componentes fijos a `src/components/efe/` + sección "Análisis" en
   la página del partido.
4. Cadena DTP (`/api/dtp`, `/api/cierre`) + registro.
5. Matriz v2.0 y migración de `casos_validacion`.
