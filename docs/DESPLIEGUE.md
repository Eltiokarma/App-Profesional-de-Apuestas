# Despliegue — Railway (backend) + Vercel (frontend)

Fase intermedia entre "todo local" y la arquitectura objetivo de
`SERVICIOS_EXTERNOS.md` (Postgres, etc.): un solo servicio en Railway con las
4 SQLite en un volumen, y el frontend estático en Vercel. Sin cambios de
código al volver a local — todo se controla por variables de entorno.

```
Vercel (web estática)  ──HTTPS──►  Railway (FastAPI + ingesta diaria)
                                        │
                                   volumen /data: sad.db · levels.db
                                   constants.db · discreto.db
```

Restricción que dicta el diseño: **un volumen de Railway solo se monta en un
servicio**, así que la ingesta diaria no es un cron aparte sino un hilo dentro
del backend (`SAD_INGESTA_HORA`) que lanza `backend.ingesta.corrida_diaria`
en subproceso. El backend HTTP sigue siendo de solo lectura.

## 1. Backend en Railway

1. **Nuevo proyecto → Deploy from GitHub repo.** Railway detecta el
   `Dockerfile` de la raíz (solo empaqueta `backend/`; las DBs quedan fuera
   por `.dockerignore`).
2. **Volumen**: en el servicio, `Settings → Volumes → Add volume`, mount path
   `/data` (5 GB dan de sobra: hoy las 4 DBs pesan ~1.3 GB).
3. **Variables** (`Settings → Variables`):

   | Variable | Valor | Nota |
   |---|---|---|
   | `API_FOOTBALL_KEY` | *(clave de dashboard.api-football.com)* | solo la usa la ingesta |
   | `SAD_CORS_ORIGINS` | `https://<tu-app>.vercel.app` | el dominio real del frontend |
   | `SAD_API_TOKEN` | *(token largo aleatorio)* | apaga `/docs` y protege la API |
   | `SAD_INGESTA_HORA` | `06:30,12:30,18:30` | horas de corrida (UTC, lista = varios snapshots de cuotas/día); vacía = sin ingesta. **Costo**: cada corrida completa gasta cientos de requests (extractor + jugadores + ficha); con un backlog grande de plantillas/fichas, dos corridas el mismo día pueden pasar de 3 000. La reserva del día (`SAD_BACKFILL_RESERVA`) frena la parte en bloque antes de dejar sin presupuesto al ciclo en vivo |
   | `SAD_REFRESCO_MIN` | `30` | fase 2: cada N min refresca cuotas de NS que empiezan en <6 h (0 requests si no hay); vacía = apagado. Con pocos pendientes pide `/odds?fixture=` (1 request por partido); el lote por fecha —que paga el feed MUNDIAL, 40-90 páginas— solo se usa con más de `SAD_CUOTAS_LOTE_UMBRAL` pendientes ese día. Antes de esa regla, este refresco solo quemaba 2.000-4.300 requests/día y fue lo que agotó el plan el 29/07/2026 |
   | `SAD_CUOTAS_LOTE_UMBRAL` | `12` | (opcional) pendientes de cuotas por FECHA a partir de los cuales conviene el lote `/odds?date=` (feed mundial) en vez de `/odds?fixture=` uno a uno. `0` = siempre lote (comportamiento anterior) |
   | `SAD_LIVE_SEGUNDOS` | `60` | fase 3: ciclo en vivo (marcador/minuto + odds live) mientras haya partidos en juego; vacía = apagado |
   | `SAD_LIVE_ODDS_LIGAS` | `6` | (opcional) ligas por ciclo en vivo a las que se les piden cuotas (`/odds/live?league=`, 1 request cubre todos sus partidos simultáneos). Ese es el default; `0` = sin tope. Las que no entran no se pierden: primero van las que tienen un partido EN JUEGO y dentro de cada grupo la de consulta más vieja, así que rotan y entran en el ciclo siguiente. Si en los logs aparece `ATENCIÓN: … tienen partido EN JUEGO`, el tope se está quedando corto — pero **antes de subirlo mira el presupuesto**: estuvo en 12 unas horas y agotó el plan del día (7496/7495), dejando sin datos hasta a las copas que funcionaban |
   | `SAD_BLOQUE_RESERVA_PARTIDOS` | `3500` | (opcional) reserva de la ingesta EN BLOQUE (backfill, jugadores, ficha) **cuando hay fútbol nuestro cerca**. Es lo que el bloque deja sin gastar PARA el ciclo en vivo — y desde el 01/08/2026 el vivo sí puede gastarlo (antes tenía además su propio suelo fijo de 1500 y esas requests no las tocaba nadie). El refresco de cuotas prepartido (`--ventana-horas`) también la respeta: era el único camino que se colaba dentro |
   | `SAD_BLOQUE_VENTANA_HORAS` | `14` | (opcional) cuánto se mira hacia adelante para decidir que "hay fútbol cerca". 14 h y no 6 porque los partidos de la noche se conocen desde la mañana: con una ventana corta, la corrida del mediodía no los ve y gasta el plan igual |
   | `SAD_LIVE_RESERVA` | `1500` | (opcional) **techo** de lo que el ciclo en vivo aparta para sí mismo. Lo que se reserva de verdad es mantener el MARCADOR vivo hasta el reset UTC: 1 request por ciclo × ciclos que quedan del día, acotado por este valor. Encoge solo según avanza la noche (a las 21:51 son ~129, no 1500), así que el vivo puede gastar el plan casi entero justo cuando hay fútbol. Al llegar a la reserva el ciclo sigue pidiendo marcador y minuto pero deja de pedir cuotas. **Era un suelo fijo y ese fue el bug del 01/08/2026**: pausa a las 21:51 con 1473 libres, 80 min con 12 partidos en juego y cero cuotas, y 1269 requests vencidas sin gastar |
   | `SAD_LIVE_BACKOFF_PASO_MIN` / `_MAX_MIN` / `_OLVIDO_H` | `3` / `10` / `8` | (opcional) backoff por liga: cada ronda SEGUIDA sin datos aleja la siguiente consulta `paso × rondas` minutos, con tope. El tope está en MINUTOS y es BAJO a propósito: un feed vacío casi siempre es temporal (Los Chankas–Comerciantes: 44 rondas vacías, 45 min, y luego 227 capturas seguidas), así que esperar de más no ahorra casi nada y llega tarde a la apertura del mercado — con tope 30 serían 5 consultas en esos 45 min y hasta 30 min de retraso; con tope 10, 6 consultas y 10 min. El contador CADUCA a las `_OLVIDO_H` horas: cada jornada empieza sin prejuicios y añadir ligas nuevas no toca el de las demás (es por league_id). La auditoría del 31/07/2026: 506 rondas vacías + 290 rescates con CERO aciertos = 796 requests tiradas (11% del plan) en confirmar 115 veces la misma noche que no hay cobertura de Bolivia. Una ronda con datos resetea el contador; un `fallo` de red NO castiga |
   | `SAD_LIVE_ODDS_PAGINAS` | `3` | (opcional) tope de páginas por liga en `/odds/live` (~10 fixtures por página). Ese es el default; sube solo si una liga tiene más de 30 partidos a la vez |
   | `SAD_EMERGENCIA_KEY` | *(clave del 2º account de api-sports)* | (opcional) partidos VIP con el plan Y el respaldo agotados: esta clave les mantiene marcador y cuotas. El plan correcto para ella es el Basic "soft limit" **deprecated** (nunca corta: factura el excedente a $0.005/request — un partido entero ≈ 220 requests ≈ $0.60); el Basic nuevo y el free de RapidAPI cortan en seco a los 100 y no sirven de emergencia. Sin la variable, el modo emergencia queda apagado |
   | `SAD_EMERGENCIA_TOPE` | `300` | (opcional) techo diario de la clave de emergencia (≈ un partido y medio ≈ $1). Es el candado contra la factura sorpresa: por muy VIP que sea todo, más de esto no se gasta |
   | `SAD_EMERGENCIA_LIGAS` | *(vacía)* | (opcional) ligas cuyos partidos en ventana son VIP automáticamente, p. ej. `13,11` en semanas de Libertadores/Sudamericana. Lo manual va por el botón "Seguir sí o sí" de la app (marca con caducidad de 8 h) |
   | `SAD_LIVE_ODDS_FIXTURES` | `4` | (opcional) rescate por partido: cuando la ronda `?league=` no trae un partido que SÍ se está jugando, se le pregunta directo con `/odds/live?fixture=`. Tope de partidos rescatados por ciclo; `0` lo apaga. Es el seguro contra las tres formas en que la vía por liga puede fallar sin que falte cobertura (feed vacío, filtro que no filtra, request caída) |
   | `SAD_FICHA_PARTIDOS` | `3` | (opcional) partidos terminados por equipo a los que se les captura ficha (alineaciones/eventos/stats) en cada corrida; 3 requests por partido. Ese es el default: para la cadena del DTP basta 1, los otros dos dan el contraste de M1/M6 |
   | `SAD_DESPENSA_CADENCIA_DIAS` | `15` | (opcional) cada cuántos días se corre el barrido de la despensa. El TTL de `dt`/`plantel` se DERIVA de aquí (+2 de margen) y hay un ciclo extra de gracia, así que la vieja "ventana cara" no existe aunque un barrido se atrase (`docs/DESPENSA_DESKTOP.md`) |
   | `SAD_DESPENSA_TTL_DIAS` | — | (opcional) fija el TTL a mano y anula el derivado. No hace falta tocarlo |
   | `SAD_DESPENSA_BULK` | `1` | (opcional) carga al arrancar la despensa versionada en el repo (`backend/analisis/despensa/*.json`). Es local, idempotente y no gasta tokens; `0` la apaga. Ese es el default |
   | `SAD_LIGAS_EXTRA` | `414:Copa Chile,999:Copa de la Liga Perú` | torneos extra sin tocar código; IDs con `--buscar` |
   | `SAD_CASAS_REFERENCIA` | `bet365,pinnacle,1xbet,betano` | casas cuyo historial crudo se guarda aparte (selector Media/casa en la gráfica); ese es el default — solo definirla para cambiar la lista |
   | `SAD_JUGADORES_TTL_LENTO` | `720` | (opcional) TTL en horas de los dos datos LENTOS de jugadores: **traspasos y DT**. Los cuatro endpoints iban con el TTL de la plantilla (7 días) y eso era la mitad del gasto tirada: las bajas y las stats cambian cada semana, pero los traspasos solo se mueven en ventana de mercado y un DT dura meses. No se pierde el cambio de DT — cada alineación capturada trae el nombre del entrenador y, si no coincide con el guardado, se refresca el mismo día. En ventana de mercado, bájalo a `24` |
   | `SAD_JUGADORES_TODAS_LIGAS` | *(vacía)* | (opcional) `1` devuelve el padrón de jugadores a las 56 ligas de `LIGAS`. Por defecto sigue solo las **importantes**: las copas nacionales meten cientos de equipos de ascenso y los Amistosos de Clubes (667) equipos de todo el mundo, cuyas plantillas casi no alimentan el análisis. Un equipo de 1ª que juega copa sigue entrando por SU liga |
   | `SAD_JUGADORES_TTL_SIN_DATOS` | `720` | (opcional) horas de sellado de los equipos que la API no cubre (plantilla vacía) antes de repreguntar. Ese es el default (30 días); el TTL normal de 7 días solo aplica a equipos CON datos. Sin este sellado largo, ~78% del gasto de jugadores eran equipos sin cobertura repreguntados cada semana |
   | `SAD_BACKFILL_RESERVA` | `1500` | (opcional) requests del día que la ingesta EN BLOQUE (backfill histórico, jugadores, ficha de partido) deja SIN gastar, para que las cuotas live y los XI de la noche nunca se queden sin presupuesto. Ese es el default (acotado a la mitad del tope en planes chicos); lo que no entra hoy se reanuda solo en la próxima corrida |
   | `SAD_BACKFILL_DESDE` | `2020` | backfill: fixtures de TODAS las ligas de la lista desde esa temporada **hasta la vigente incluida** (la vigente se re-barre cada 30 días; lo demás una sola vez). Corre al arrancar y tras cada corrida diaria, con progreso reanudable en el volumen (`.backfill_hist.json`); al día = 0 requests, puede quedarse puesta |
   | `SAD_INGESTA_AL_ARRANCAR` | `1` | (opcional, one-shot) dispara una corrida diaria completa (ventana por fecha + cuotas + `sanar_fechas` + purga de ligas no seguidas) a los ~40 s del arranque, **sin esperar a `SAD_INGESTA_HORA`**. Para aplicar un parche de ingesta lo antes posible tras un deploy; quitarla después |
   | `SAD_LIGAS_RUIDO` | `667` | (opcional) ligas de "ruido": amistosos cuyos NS la API casi nunca resuelve. No se re-barren ni se persiguen por fecha (se bajan solo en la primera pasada del backfill). Ese es el default; `667` = Amistosos de Clubes. NO afecta a temporadas pasadas de ligas reales, que se curan igual |
   | `SAD_LIGAS_MENORES` | *(2ª divisiones y copas nacionales de Sudamérica)* | (opcional) ligas "menores": se ingestan IGUAL que las demás — fixtures, histórico y cuotas **prepartido**, para tener TODOS los partidos de un equipo (constantes/burbujas) — pero quedan FUERA del ciclo **en vivo** (odds live solo en las importantes). El default trae las 2ª divisiones (Argentina Primera Nacional, Perú Liga 2, Colombia Primera B, Chile Primera B, Ecuador Serie B, Uruguay Segunda), las copas nacionales (Copa Argentina, Copa do Brasil, Copa Colombia, Copa Chile, Copa Bicentenario, Copa Uruguay, Copa Ecuador) y los Amistosos de Clubes (667, la liga que más NS zombis produce: comían turnos del ciclo en vivo sin partido real que cubrir); define la variable para ampliar/cambiar la lista, o vacíala para tratarlas a todas como importantes |
   | `SAD_RELLENO_FECHAS` | `2026-05-31` o `2026-05-01:2026-06-05` | (opcional, one-shot) al arrancar re-pide `/fixtures` POR FECHA en ese día/rango (todas las temporadas, filtrado a las ligas de la lista) y regenera el pipeline. Palanca para **tapar a mano un hueco y verlo en los logs sin esperar** a la corrida programada. Gasta requests en cada arranque → quitarla cuando el hueco quede tapado. Diagnóstico previo: `python -m backend.ingesta.diagnostico` |
   | `SAD_REBARRIDO_DIAS` | `30` | (opcional) cada cuántos días el backfill re-barre la temporada VIGENTE y las pasadas que sigan ABIERTAS en la DB (NS/TBD con fecha vencida — año cruzado). Ponerla en `1` temporalmente fuerza el re-barrido completo en el próximo arranque (p. ej. tras detectar fixtures faltantes: ventana diaria que no corrió); después devolverla a `30` |
   | `ANTHROPIC_API_KEY` | *(clave de console.anthropic.com)* | capa de análisis EFE+DTP (`POST /api/v1/analisis/efe`). Ponerle límite mensual de gasto en la consola de Anthropic. Sin ella, el endpoint responde 503 y el resto de la API funciona igual |
   | `SAD_EFE_MODELO` | `claude-sonnet-5` | (opcional) modelo para el análisis EFE; ese es el default |
   | `SAD_BOOTSTRAP_URL` | *(URL del zip, solo la primera vez)* | ver carga inicial |

   Para descubrir el ID de un torneo nuevo (p. ej. una copa recién creada),
   con la clave en el entorno: `python -m backend.ingesta.extractor --buscar "Copa Chile"`
   (imprime id, país y temporadas leídos de la API; 1 request).

4. **Carga inicial de las DBs** (una sola vez). El volumen recién creado está
   vacío y no se puede subir archivos directo, por eso el bootstrap:
   - En local: `zip dbs.zip sad.db levels.db constants.db discreto.db`.
   - Súbelo a cualquier sitio con enlace de descarga directa (R2, Backblaze,
     Drive con enlace directo…).
   - Pon esa URL en `SAD_BOOTSTRAP_URL` y redespliega: al arrancar,
     `backend.bootstrap_datos` la descarga a `/data` (solo si falta `sad.db`).
   - Cuando `/api/v1/health` dé `dbOk: true`, borra `SAD_BOOTSTRAP_URL` y el
     zip remoto.
5. **Dominio**: `Settings → Networking → Generate domain` (o dominio propio).
   Verificar: `https://<backend>/api/v1/health` → `{"status":"ok",…}`.

Con `SAD_INGESTA_HORA` puesta, cada día el extractor actualiza sad.db
(ventana hoy−3d..+10d + cuotas, tope 95 req/día) y el pipeline regenera las
derivadas en `/data`. El backend abre conexión por consulta, así que sirve
los datos nuevos sin reiniciar. La ventana pide `/fixtures` **por fecha**
(no por liga+temporada): el feed del día trae todas las temporadas a la vez,
así que las ligas de año cruzado (Premier, Champions, Liga MX… que en mayo de
2026 iban por la temporada API 2025) ya no desaparecen de la ventana — ese
desfase fue el origen del hueco del 31/05/2026 en muchas ligas.

Cada corrida además **se cura sola**, dos pasadas automáticas:

- **Regla de los 90'**: detecta torneos con partidos AET/PEN sin `fulltime_*`
  (guardados por versiones viejas — el motor los contaba con el marcador de
  los 120') y los re-barre (máx. 5 torneos/corrida, marcador `.sanar90.json`
  en el volumen). Auditoría manual:
  `python -m backend.ingesta.pipeline --diagnostico-90`.
- **Sanar fechas**: detecta días PASADOS que quedaron con partidos NS/TBD
  (la firma de un hueco de ingesta) y re-pide cada día con `/fixtures?date=`,
  que también trae los partidos que ni existían al barrer el torneo (finales
  y liguillas creadas tarde). Máx. 10 fechas/corrida (`SAD_SANAR_FECHAS_MAX`),
  horizonte 180 días (`SAD_SANAR_FECHAS_DIAS`), marcador `.sanar_fechas.json`
  en el volumen (una fecha incurable se reintenta a los 7 días). Una fecha que
  solo tiene amistosos (`SAD_LIGAS_RUIDO`) sin resultado NO se persigue: es
  ruido que la API no resuelve.

El backfill (`SAD_BACKFILL_DESDE`) también re-barre cada 30 días los torneos
de temporadas **pasadas que sigan abiertos** en la DB (con NS/TBD de fecha
vencida), no solo la vigente: así el tramo final de una temporada cruzada no
queda congelado en el estado del primer barrido. Los amistosos
(`SAD_LIGAS_RUIDO`) se excluyen de ese re-barrido (se bajan solo la primera vez).

**Importante sobre el "cuándo":** el backfill corre en un hilo **al ARRANCAR**
(~30 s tras el boot), no a la hora de `SAD_INGESTA_HORA`. Así que un redeploy
ya descongela las temporadas pasadas reales de inmediato. Para que la curación
por fecha (`sanar_fechas`) y la purga también corran al arrancar sin esperar a
la hora, poner `SAD_INGESTA_AL_ARRANCAR=1`.

Auditoría de huecos (sin gastar requests, o con `--api` contrastando 1 día
contra el feed real):

```bash
python -m backend.ingesta.diagnostico                    # resumen de zombis
python -m backend.ingesta.diagnostico --dia 2026-05-31 --api
python -m backend.ingesta.extractor --desde 2026-05-31 --hasta 2026-05-31 --solo fixtures  # rellenar un día a mano
```

## 2. Frontend en Vercel

1. **Add New → Project → importar el repo.** Framework: Vite (build
   `npm run build`, output `dist` — Vercel lo autodetecta).
2. **Environment Variables**:

   | Variable | Valor |
   |---|---|
   | `VITE_DATA_SOURCE` | `http` |
   | `VITE_API_BASE_URL` | `https://<backend>/api/v1` |
   | `VITE_API_KEY` | el mismo valor que `SAD_API_TOKEN` |

   ⚠ Todo `VITE_*` queda visible en el bundle: el token bearer es de
   staging/uso personal, no un secreto fuerte (la clave de API-Football jamás
   va aquí).
3. Deploy y luego confirmar que `SAD_CORS_ORIGINS` en Railway coincide con el
   dominio final (incluido `https://`).

## 3. Checklist de verificación

- [ ] `GET /api/v1/health` responde `ok` con `lastPipelineRun` reciente.
- [ ] La web en Vercel muestra `FEED CONECTADO` con latencia (health-check).
- [ ] Sin `Authorization` la API responde 401 (token activo) y `/docs` está apagado.
- [ ] Partidos del día visibles; página de liga con temporadas.
- [ ] Al día siguiente de activar `SAD_INGESTA_HORA`: `lastPipelineRun` avanzó
      y los logs de Railway muestran `[ingesta] corrida diaria …`.

## 4. Costos y límites

- Railway: ~$5/mes del plan Hobby cubre este servicio + volumen a este tamaño.
- Vercel: plan free (build estático).
- La cuota free de API-Football (95 req/día efectivos) la administra el
  extractor con `.extractor_cuota.json`, que persiste en el volumen.
- Cuando duela SQLite (tamaño del volumen, más escrituras, varios servicios),
  el salto es a la fase de `SERVICIOS_EXTERNOS.md`: Postgres gestionado.
