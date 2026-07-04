# SAD API — backend FastAPI (v0)

Servicio de **solo lectura** sobre las 4 SQLite del pipeline SAD
(`sad.db → levels.db → constants.db → discreto.db`), implementando el contrato
`docs/openapi.yaml`. La web de este mismo repo lo consume con
`VITE_DATA_SOURCE=http`. No escribe nada: el pipeline de extracción (repo
`Professional-Player`, usado como referencia) sigue siendo el dueño de los datos.

## Puesta en marcha (todo en este repo)

1. **Pega tus 4 bases** en la **raíz de este repo** (junto a `package.json`):
   `sad.db`, `levels.db`, `constants.db`, `discreto.db`.
   Están ignoradas por git — nunca se subirán.

2. **Terminal 1 — backend:**

   ```bash
   pip install -r backend/requirements.txt
   python -m uvicorn backend.app:app --port 8000
   ```

   Comprueba `http://localhost:8000/api/v1/health` → `"dbOk": true`
   (y `http://localhost:8000/docs` para la API navegable).

3. **Terminal 2 — web:**

   ```bash
   npm install
   cp .env.example .env   # VITE_DATA_SOURCE=http · VITE_API_BASE_URL=http://localhost:8000/api/v1
   npm run dev            # → http://localhost:5173
   ```

¿Las `.db` en otra carpeta? `SAD_DATA_DIR=/ruta/a/las/dbs python -m uvicorn backend.app:app --port 8000`
(en Windows PowerShell: `$env:SAD_DATA_DIR="C:\ruta"` antes del comando).

## Sin bases reales: modo demo

```bash
python -m backend.seed_demo                          # genera ./demo_data con esquemas reales
SAD_DATA_DIR=demo_data python -m uvicorn backend.app:app --port 8000
python -m backend.test_api                           # 33 verificaciones del contrato
```

## Endpoints

| Endpoint | Fuente |
|---|---|
| `GET /api/v1/health` | existencia/lectura de las 4 DBs + `MAX(processed_at)` |
| `GET /api/v1/fixtures[?fecha&estado&ligaId&limit]` | `sad.db` (fixtures + teams + leagues) |
| `GET /api/v1/fixtures/{id}` | ídem |
| `GET /api/v1/niveles/{equipoId}` | `levels.db` + bins fijos v6 |
| `GET /api/v1/constantes/{equipoId}` | `constants.db` + rival/goles de `discreto.db` + fusión k = k⁺ + k⁻ |
| `GET /api/v1/predicciones/{fixtureId}` | Ley de Regresión al Nivel §5 (μ = 1.110 + 0.686·nivel − 0.669·rival + 0.422·localía) |
| `GET /api/v1/analisis-prepartido/{fixtureId}` | composición de todo lo anterior |
| `GET /api/v1/cuotas/{fixtureId}` | tabla `odds` de `sad.db`, mapeada al contrato y promediada entre bookmakers |
| `GET /api/v1/equipos/{equipoId}/stats` | forma (últ. 5), PJ, puntos y promedios de goles de fixtures; xG/posesión `null` en v0 |
| `GET /api/v1/ligas/{ligaId}/standings[?temporada]` | tabla de posiciones calculada de fixtures |

## Configuración

| Variable | Default | Uso |
|---|---|---|
| `SAD_DATA_DIR` | raíz del repo | carpeta con las 4 SQLite |
| `SAD_CORS_ORIGINS` | `*` | orígenes permitidos (coma-separados) |

## Fase 2 (pendiente)

Ingesta propia (API-Football + APScheduler), PostgreSQL gestionado con Alembic,
xG/posesión desde estadísticas por partido, endpoint H2H, auth de sesión y
despliegue 24/7 — ver `docs/SERVICIOS_EXTERNOS.md`.
