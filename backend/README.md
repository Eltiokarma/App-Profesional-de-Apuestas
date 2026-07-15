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
python -m backend.test_api                           # verificaciones del contrato (165 checks)
```

## Endpoints

| Endpoint | Fuente |
|---|---|
| `GET /api/v1/health` | existencia/lectura de las 4 DBs + `MAX(processed_at)` |
| `GET /api/v1/fixtures[?fecha&estado&ligaId&limit]` | `sad.db` (fixtures + teams + leagues) |
| `GET /api/v1/fixtures/{id}` | ídem |
| `GET /api/v1/niveles/{equipoId}` | `levels.db` + bins fijos v6 |
| `GET /api/v1/constantes/{equipoId}` | `constants.db` + rival/goles de `discreto.db` + fusión k = k⁺ + k⁻ |
| `GET /api/v1/predicciones/{fixtureId}` | Ley de Regresión al Nivel §5 (μ v2 = 1.241 + 0.334·nivel − 0.357·rival + 0.382·localía) |
| `GET /api/v1/analisis-prepartido/{fixtureId}` | composición de todo lo anterior |
| `GET /api/v1/cuotas/{fixtureId}` | tabla `odds` de `sad.db`, mapeada al contrato y promediada entre bookmakers |
| `GET /api/v1/equipos/{equipoId}/stats` | forma (últ. 5), PJ, puntos y promedios de goles de fixtures; xG/posesión `null` en v0 |
| `GET /api/v1/ligas/{ligaId}/standings[?temporada]` | tabla de posiciones calculada de fixtures |

## Configuración

| Variable | Default | Uso |
|---|---|---|
| `SAD_DATA_DIR` | raíz del repo | carpeta con las 4 SQLite |
| `SAD_CORS_ORIGINS` | localhost/127.0.0.1:5173 | orígenes permitidos (coma-separados); en despliegue, el dominio real del frontend |
| `SAD_API_TOKEN` | *(vacío = abierta)* | con valor, todo salvo `/health` exige `Authorization: Bearer <token>` (el frontend lo manda con `VITE_API_KEY`) |
| `SAD_RATE_LIMIT` | `120` | requests por minuto por IP (429 al exceder); `0` lo apaga |
| `SAD_DOCS` | `1` sin token, `0` con token | expone `/docs`, `/redoc` y `/openapi.json` |
| `SAD_INGESTA_HORA` | *(vacía = apagada)* | `HH:MM` UTC: corre `backend.ingesta.corrida_diaria` a diario en subproceso (despliegue de un solo servicio) |
| `SAD_BOOTSTRAP_URL` | *(vacía)* | zip con las 4 DBs: se descarga a `SAD_DATA_DIR` en el arranque si falta sad.db (carga inicial del volumen) |

Nota despliegue: el rate limit ve la IP del cliente directo — detrás de un
proxy inverso esa IP es la del proxy, así que en producción conviene limitar
también en el proxy (o propagar la IP real). Guía completa Railway + Vercel:
`docs/DESPLIEGUE.md`.

## Fase 2 (pendiente)

PostgreSQL gestionado con Alembic, xG/posesión desde estadísticas por partido
y historial de cuotas — ver `docs/SERVICIOS_EXTERNOS.md`.
