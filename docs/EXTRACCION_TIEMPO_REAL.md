# Extracción en tiempo real — plan por fases

Objetivo: pasar de la foto diaria actual a datos frescos en tres saltos
controlados, sin romper la regla de oro (el backend HTTP es de solo lectura;
solo `backend/ingesta/` escribe). Presupuesto: plan pago de API-Football,
tope y ritmo autoajustados por cabeceras `x-ratelimit-*` (ya hecho).

## Estado actual (fase 0)

Una corrida diaria (`SAD_INGESTA_HORA`): fixtures hoy−3d..+10d + **una sola
foto** de cuotas por fixture NS (los que ya tienen odds se saltan). La gráfica
de movimiento de Cuotas es simulación del frontend anclada a esa foto
(`src/lib/odds.ts: seriesFor`), y el minuto/marcador en vivo también son
simulados (`src/store.ts`).

## Fase 1 · Historial de cuotas prepartido (= punto 4 del roadmap) — HECHA

La que da valor de apuestas real: movimiento de la cuota **antes** del partido.

- **sad.db**: tabla `odds_history(fixture_id, league_id, bet_id, bet_name,
  value, odd, casas, captured_at)` — un punto por selección y captura con la
  **media entre casas** (más compacta que guardar cada bookmaker; `casas`
  registra cuántos promedió). La tabla `odds` queda como "última foto"
  (compatibilidad con el pipeline y la regla de huecos de
  `docs/ROADMAP_BURBUJAS.md`). El extractor crea la tabla si no existe.
- **Extractor**: `fixtures_para_cuotas` — primero los NS sin cuotas de toda
  la ventana (primera captura), después re-captura de los NS que empiezan en
  <= 2 días aunque ya tengan (snapshot nuevo).
- **Scheduler**: `SAD_INGESTA_HORA` acepta lista `"06:30,12:30,18:30"`.
  Tres snapshots al día ya dibujan una curva prepartido honesta.
- **Contrato**: `GET /cuotas/{fixtureId}/historial` → `CuotaSnapshot[]`
  (asc por captura; `[]` en DBs anteriores a esta fase).
- **Frontend — regla de datos**: en producción (`http`) NO se pinta nada
  inventado. Con >=2 capturas reales por selección, la curva es real
  (apertura = primer snapshot, eje X = capturas); con menos, placeholder
  honesto y solo las cuotas actuales (reales). El toggle "En vivo" y toda
  la simulación quedan confinados al modo demo (`mock`, "MOTOR LOCAL ·
  DEMO") hasta la fase 3.

Presupuesto fase 1: 3 corridas × ~150 req ≈ **450/día** (Pro: 7.500).

## Fase 2 · Día de partido — HECHA

- `extractor --ventana-horas 6`: corrida ligera SOLO de cuotas para los NS
  que empiezan en <= 6 h (snapshot directo a `odds_history`; sin fixtures
  próximos sale con 0 requests).
- `SAD_REFRESCO_MIN=30` (env, vacía = apagado): hilo propio en
  `backend/app.py` que corre ese refresco cada N minutos (piso 10; la
  ventana se ajusta con `SAD_REFRESCO_VENTANA_HORAS`, default 6).
- Escritura con `busy_timeout` para convivir con las lecturas del backend
  (el paso a WAL sigue reservado para la fase 3).
- Cierra la curva prepartido con densidad donde importa (las últimas horas
  son las de más movimiento).
- Presupuesto: ~20 fixtures/día × 8 refrescos ≈ **160/día** extra.

## Fase 3 · En vivo de verdad

- **Marcador y minuto**: `GET /fixtures?live=<ids de LIGAS>` — 1 request trae
  todos los partidos en juego de nuestras ligas. Poll cada 60–90 s **solo**
  mientras haya partidos vivos; actualiza `fixtures` (status, elapsed, goles).
- **Cuotas en juego**: `GET /odds/live` (cobertura por liga a verificar con
  el plan; no todas las ligas tienen odds live). Tabla separada
  `odds_live(fixture_id, ..., minuto, captured_at)` con retención corta
  (p. ej. 7 días) para no engordar sad.db.
- **SQLite**: activar `PRAGMA journal_mode=WAL` en sad.db antes de esto —
  con escrituras cada minuto y el backend leyendo, el modo journal por
  defecto daría `database is locked`.
- **Backend**: `GET /fixtures/{id}/live` (marcador, minuto, cuotas live).
  El frontend reemplaza el simulador: `liveMin` del tick del store →
  polling del endpoint cada 10–15 s; `inplayInfluence`/tramo `inp` de
  `seriesFor` → puntos reales.
- **Presupuesto**: 2 req/min × ~6 h de ventana con partidos ≈ **700/día**.
  Total fases 1+2+3 ≈ 1.300/día — holgado incluso en Pro.

## Fase 4 · Solo si hace falta

Postgres gestionado (`docs/SERVICIOS_EXTERNOS.md`) si el volumen de
`odds_history`/`odds_live` o la concurrencia superan a SQLite+WAL. No antes.

## Decisiones abiertas

1. Cobertura real de `/odds/live` por liga (verificar con `--probar` extendido
   o 1 request manual cuando haya partidos vivos de nuestras ligas).
2. Retención de `odds_live` y de snapshots viejos de `odds_history`.
3. Si el poll en vivo vive en el mismo servicio Railway (hilo como el
   scheduler actual) o en un worker separado — empezar en el mismo, separar
   solo si compite con el backend.

Orden: 1 → 2 → 3. La fase 1 es la única que toca el contrato web↔backend;
las demás suman sobre ella.
