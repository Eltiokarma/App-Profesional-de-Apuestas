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
   | `SAD_INGESTA_HORA` | `06:30,12:30,18:30` | horas de corrida (UTC, lista = varios snapshots de cuotas/día); vacía = sin ingesta |
   | `SAD_REFRESCO_MIN` | `30` | fase 2: cada N min refresca cuotas de NS que empiezan en <6 h (0 requests si no hay); vacía = apagado |
   | `SAD_LIVE_SEGUNDOS` | `60` | fase 3: ciclo en vivo (marcador/minuto + odds live) mientras haya partidos en juego; vacía = apagado |
   | `SAD_LIGAS_EXTRA` | `414:Copa Chile,999:Copa de la Liga Perú` | torneos extra sin tocar código; IDs con `--buscar` |
   | `SAD_CASAS_REFERENCIA` | `bet365,pinnacle,1xbet,betano` | casas cuyo historial crudo se guarda aparte (selector Media/casa en la gráfica); ese es el default — solo definirla para cambiar la lista |
   | `SAD_BACKFILL_DESDE` | `2020` | backfill: fixtures de TODAS las ligas de la lista desde esa temporada **hasta la vigente incluida** (la vigente se re-barre cada 30 días; lo demás una sola vez). Corre al arrancar y tras cada corrida diaria, con progreso reanudable en el volumen (`.backfill_hist.json`); al día = 0 requests, puede quedarse puesta |
   | `SAD_INGESTA_AL_ARRANCAR` | `1` | (opcional, one-shot) dispara una corrida diaria completa (ventana por fecha + cuotas + `sanar_fechas` + purga de ligas no seguidas) a los ~40 s del arranque, **sin esperar a `SAD_INGESTA_HORA`**. Para aplicar un parche de ingesta lo antes posible tras un deploy; quitarla después |
   | `SAD_LIGAS_RUIDO` | `667` | (opcional) ligas de "ruido": amistosos cuyos NS la API casi nunca resuelve. No se re-barren ni se persiguen por fecha (se bajan solo en la primera pasada del backfill). Ese es el default; `667` = Amistosos de Clubes. NO afecta a temporadas pasadas de ligas reales, que se curan igual |
   | `SAD_LIGAS_MENORES` | `282,130,73,241` | (opcional) ligas "menores" (segundas divisiones, copas nacionales donde juegan equipos de otras categorías): se ingestan IGUAL que las demás — fixtures, histórico y cuotas **prepartido**, para tener TODOS los partidos de un equipo (constantes/burbujas) — pero quedan FUERA del ciclo **en vivo** (odds live solo en las importantes). Ese es el default (Perú Liga 2, Copa Argentina, Copa do Brasil, Copa Colombia); define la variable para ampliar/cambiar la lista, o vacíala para tratarlas a todas como importantes |
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
