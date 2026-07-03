# Servicios externos — arquitectura objetivo e integración del frontend

Este documento fija el plan de servicios para llevar el SAD de app de escritorio a
servicio en la nube, y documenta **qué parte ya está lista en este repositorio**
(el frontend web) para trabajar contra esos servicios.

## 1. Arquitectura objetivo (3 piezas)

```
API-Football ──polling──►  BACKEND (FastAPI + motor_sad)  ──SQL──►  PostgreSQL
                                    │  API REST (docs/openapi.yaml)
                     ┌──────────────┼──────────────┐
                 Web SAD (este repo)          UI PyQt existente
```

- **Backend: monolito modular en FastAPI (Python)** — vive en el repo del motor
  (`Eltiokarma/Professional-Player`). Un solo servicio con el paquete `motor_sad`
  dentro, que expone la API y corre el pipeline programado
  (extracción → `calculate_missing_levels()` → `batch_calculate_teams(incremental=True)`
  → `process_all_teams()`). Nada de microservicios a esta escala.
- **Base de datos: PostgreSQL gestionado** (Neon o Supabase) — las 4 SQLite
  (`sad`, `levels`, `constants`, `discreto`) pasan a 4 esquemas del mismo Postgres.
  Cambios técnicos al migrar: fechas como `timestamptz` y `executemany` → `COPY`.
- **Ingesta: polling disciplinado con APScheduler** — API-Football no tiene webhooks.
  Frecuencias: 1–2 min fixtures en vivo · 1 h resultados del día · diario backfill.
  Plan Pro (~$39/mes, 7 500 req/día) presupuestando requests por liga.
- **ML**: entrenamiento offline/nocturno; artefactos (`.joblib`, `model_exports/`)
  en almacenamiento de objetos (Cloudflare R2); el backend solo hace inferencia.

### Presupuesto de arranque

| Rubro | Opción | Costo/mes |
|---|---|---|
| API de datos | API-Football Pro | $39 |
| Servidor backend | Hetzner VPS (CX22) o Railway/Fly.io | €5–10 / $10–30 |
| PostgreSQL | Neon o Supabase | $0–25 |
| Storage modelos | Cloudflare R2 | ~$0 |
| Monitoreo | Sentry free + logs del host | $0 |
| Frontend web (este repo) | Vercel / Netlify / Cloudflare Pages | $0 |

**Total realista: $50–100/mes.** Innegociables desde el día 1: migraciones con
Alembic, backups automáticos y un entorno de staging para probar recálculos
completos antes de producción. Evitar por ahora: Kubernetes, colas distribuidas,
multi-región.

## 2. Lo que este repo ya tiene listo

### El contrato: `docs/openapi.yaml`

Especificación OpenAPI 3 de la API que el backend debe implementar y que este
frontend ya consume. Endpoints: `/health`, `/fixtures`, `/fixtures/{id}`,
`/niveles/{equipoId}`, `/constantes/{equipoId}`, `/predicciones/{fixtureId}`,
`/analisis-prepartido/{fixtureId}`, `/cuotas/{fixtureId}`. Los esquemas espejan
el pipeline del motor (niveles continuos + bins v6, los 12 acumuladores k*, las
K fusionadas, el gap de regresión al nivel §5).

En FastAPI, los modelos Pydantic deben producir exactamente estos JSON; la spec
se puede validar contra la implementación con `schemathesis` en CI del backend.

### La capa de datos conmutable: `src/services/datasource.ts`

La app habla **siempre** el contrato del openapi:

- `MockDataSource` (default) — el Motor SAD local (`src/motor/`) sirviendo ese
  mismo contrato con datos deterministas. Incluye `/predicciones` real: la Ley de
  la Regresión al Nivel (§5) está implementada en `src/motor/regression.ts`
  (μ = 1.110 + 0.686·nivel − 0.669·nivel_rival + 0.422·localía, recorte [0,3],
  forma reciente de 5, umbrales de señal 0.3/0.5).
- `HttpDataSource` — cliente del backend real (`src/api/`): fetch con timeout,
  `ApiError` tipado y bearer token opcional.

Conmutación por entorno, sin tocar código:

```bash
cp .env.example .env
# VITE_DATA_SOURCE=http
# VITE_API_BASE_URL=https://api.tu-dominio.com/api/v1
```

El indicador del sidebar ya es real: en modo demo muestra `MOTOR LOCAL · DEMO`;
en modo http hace health-check periódico (`VITE_POLL_HEALTH_MS`) y muestra
latencia o `SIN CONEXIÓN`.

### CI: `.github/workflows/ci.yml`

Cada push/PR corre `npm run test:motor` (el motor verificado contra el doc de
extracción) y el build de producción.

## 3. Requisitos que el backend debe cumplir para este frontend

1. **CORS**: permitir el origen del frontend (`Access-Control-Allow-Origin`).
2. **Ids numéricos estables** para equipos y fixtures (los de API-Football sirven).
3. **`/health`** barato y sin auth: `{status, version, dbOk, lastPipelineRun}`.
4. **Fechas ISO-8601 UTC** (`timestamptz`).
5. **Auth**: bearer para staging; en producción, sesión gestionada por el backend.
   ⚠ Nada `VITE_*` es secreto (queda en el bundle); la clave de API-Football
   jamás debe llegar al frontend.

## 4. Hoja de ruta de integración

Hecho (las secciones ya consumen `getDataSource()` con estados de carga/error):

- ✅ Selector de partidos y header ← `fixtures()` (mapeo DTO→UI en
  `src/services/appdata.ts`, registro dinámico de equipos desconocidos)
- ✅ Cuotas ← `cuotas()` (las series de movimiento se construyen alrededor de la
  cuota real; el histórico intradía sigue siendo sintético hasta que exista un
  endpoint de historial de cuotas)
- ✅ Burbujas ← `constantes()` + `niveles()` (reconstrucción de snapshots desde DTOs)
- ✅ Skills: el reporte SAD ← `analisisPrepartido()` (resumen, niveles, K, gap)
- ✅ Estadísticas: panel "Regresión al nivel · Ley §5" ← `prediccion()`

- ✅ Estadísticas: forma, promedios de goles, puntos y tabla de posiciones ←
  `equipoStats()` + `standings()` (calculados de fixtures por el backend; las
  filas de xG/posesión/tiros/córners aparecen solo cuando el backend las sirva)

Pendiente:

1. Backend: derivar xG/posesión/tiros/córners de las estadísticas por partido
   de API-Football; endpoint de enfrentamientos directos (H2H — la card sigue
   siendo demo).
2. Historial de cuotas (`/cuotas/{fixtureId}/historial`) para que la gráfica de
   movimiento sea 100 % real.
3. Polling de cuotas en vivo con `VITE_POLL_LIVE_MS`.
4. Cache ligera con revalidación (SWR casero o TanStack Query si crece).
5. Deploy del frontend (Vercel/Netlify/Cloudflare Pages) apuntando a staging.
