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

## Fase 3 · En vivo de verdad — HECHA

- **`backend/ingesta/en_vivo.py`** (un ciclo por invocación): busca fixtures
  nuestros en ventana de juego en sad.db (0 requests si no hay);
  `GET /fixtures?live=<ids de LIGAS>` actualiza marcador/minuto/estado
  (via guardar_fixtures); `GET /odds/live?league=<id>` **por cada liga con
  partido nuestro en juego** → tabla `odds_live` (con `suspendida` y
  `minuto`), retención 30 días. Activa WAL en sad.db
  (requisito: escrituras por minuto conviviendo con lecturas).
- **Por qué por liga y no el feed global** (bug 26/07/2026, Melgar–Cristal en
  Perú - Primera División sin cuotas en juego pese a ser liga importante):
  `/odds/live` viene **paginado a ~10 fixtures por página**, igual que el
  `/odds` prepartido. Pedirlo sin filtro traía solo la página 1 — los 10
  primeros partidos vivos DEL MUNDO — así que nuestras ligas casi nunca
  aparecían y la UI mostraba "sin cobertura de cuotas en vivo en esta liga",
  que era mentira: nunca se preguntó por ellas. Con `?league=` el feed llega
  completo y una sola request cubre todos los partidos simultáneos de esa
  liga. Topes: `SAD_LIVE_ODDS_LIGAS` (6 ligas/ciclo, rotando por captura más
  vieja primero: ninguna se queda sin curva) y `SAD_LIVE_ODDS_PAGINAS` (3).
  Test offline: `python -m backend.test_en_vivo`.
- **Las otras tres puertas** que dejaban partidos sin curva (26/07/2026, UTC
  Cajamarca–UCV Moquegua):
  1. **`TBD` no era candidato.** La ventana solo aceptaba `NS`, pero en esta DB
     `TBD` es un estado real y frecuente (toda la maquinaria de zombis de
     `diagnostico.py` va sobre NS/TBD). Un partido con hora por confirmar
     jamás entraba al ciclo. Ahora entran `NS` y `TBD`.
  2. **Solo se miraba hacia atrás.** La ventana era `[saque−0, saque+3h30]`:
     si la API adelanta el saque o nuestra hora va unos minutos tarde, el
     partido ya se juega mientras su `date` sigue en el futuro y el ciclo
     salía con "sin partidos en ventana · 0 requests" sin preguntar nada.
     Ahora arranca 15 min antes (`VENTANA_PREVIA_MIN`).
  3. **`live=<37 ligas>`.** El parámetro hermano `ids` está documentado con
     tope de 20 y de `live` no hay tope publicado; si recortara, se caerían
     justo las ligas de id alto — Perú (281), Venezuela (299), Bolivia (344).
     Pasado `TOPE_LIGAS_LIVE` (20) se pide `live=all` y filtramos nosotros:
     mismo coste, cero dependencia de lo que haga el filtro del servidor.
  Y lo más importante: **las cuotas ya no dependen de ese feed**. El universo
  de ligas a pedir sale del feed live **más** nuestros candidatos locales, así
  que un partido que el feed se deje igual recibe su `/odds/live?league=`.
- **`python -m backend.ingesta.diag_vivo --fixture N [--api]`**: dice cuál de
  las puertas se cerró para un partido concreto — liga fuera de lista o marcada
  menor, ventana, si el ciclo corrió esa franja, filas en `odds_live`, si
  `cuota_key` las mapea (hay datos pero la ficha se ve vacía), prepartido y
  presupuesto del día. Con `--api` (2 requests) responde lo único que no está
  en la DB: si la API ofrece odds live de esa liga.
- **`SAD_LIVE_SEGUNDOS=60`** (env, vacía = apagado, piso 30): hilo en
  `backend/app.py` que corre el ciclo.
- **Backend**: `GET /fixtures/{id}/live` → estado/minuto/marcador reales +
  `cuotas` (última captura, con suspendidas) + `serie` (movimiento del
  partido). `cuota_key` ganó el alias "Fulltime Result" (catálogo live).
- **Frontend**: en http, con el partido en juego, polling silencioso cada
  `VITE_POLL_LIVE_MS` (default 60 s): banner EN DIRECTO real (marcador,
  minuto, hora de captura) + sección "Cuotas en juego" del mercado activo
  (suspendidas atenuadas). Sin cobertura de odds live: solo marcador/minuto,
  nada inventado.
- **Gráfica**: la `serie` live se pinta como tramo en vivo REAL de la
  gráfica grande (prepartido 0→KO con el historial, KO→90' con odds_live,
  marcador de minuto actual). Si la liga no tiene cobertura de odds live,
  el tramo simplemente no aparece — regla "real o nada". Pendiente menor:
  el catálogo de bets de /odds/live puede necesitar más aliases en
  `cuota_key` según lo que llegue el primer día real de partidos (hoy
  mapea "Fulltime Result"/1X2 y los mercados clásicos).
- **Presupuesto**: 1 req/min de marcador + 1 por liga con partido vivo (tope 6)
  × ~6 h de ventana con partidos. En la práctica 2-4 ligas nuestras coinciden
  en juego → ≈ **1.100-1.800/día** en los días cargados. Total fases 1+2+3
  ≈ 2.500/día en el peor día — cabe en Pro (7.500) con la reserva de backfill
  intacta. Si aprieta: bajar `SAD_LIVE_ODDS_LIGAS` o subir `SAD_LIVE_SEGUNDOS`.

## Fase 4 · Solo si hace falta

Postgres gestionado (`docs/SERVICIOS_EXTERNOS.md`) si el volumen de
`odds_history`/`odds_live` o la concurrencia superan a SQLite+WAL. No antes.

## Decisiones abiertas

1. Cobertura real de `/odds/live` por liga: ya no se confunde con el bug de
   paginación (ver fase 3), pero sigue pendiente medir en qué ligas la API
   de verdad no ofrece odds live. Los logs del ciclo lo dicen liga por liga
   ("ligas sin odds en el feed live"); si alguna sale vacía siempre, vale la
   pena dejar de preguntarle y ahorrarse la request.
2. Retención de `odds_live` y de snapshots viejos de `odds_history`.
3. Si el poll en vivo vive en el mismo servicio Railway (hilo como el
   scheduler actual) o en un worker separado — empezar en el mismo, separar
   solo si compite con el backend.

Orden: 1 → 2 → 3. La fase 1 es la única que toca el contrato web↔backend;
las demás suman sobre ella.
