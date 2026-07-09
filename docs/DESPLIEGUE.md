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
   | `API_FOOTBALL_KEY` | *(la clave RapidAPI)* | solo la usa la ingesta |
   | `SAD_CORS_ORIGINS` | `https://<tu-app>.vercel.app` | el dominio real del frontend |
   | `SAD_API_TOKEN` | *(token largo aleatorio)* | apaga `/docs` y protege la API |
   | `SAD_INGESTA_HORA` | `06:30` | corrida diaria (UTC); vacía = sin ingesta |
   | `SAD_BOOTSTRAP_URL` | *(URL del zip, solo la primera vez)* | ver carga inicial |

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
los datos nuevos sin reiniciar.

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
