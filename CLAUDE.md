# SAD · Análisis pre-partido — guía para el agente

App **autocontenida** de análisis pre-partido de fútbol y apuestas:
web (React + Vite + TS) + backend (FastAPI, solo lectura) + Motor SAD.
Todo en español (UI, commits, docs).

## Comandos

```bash
# web
npm install && npm run dev        # http://localhost:5173
npm run build                     # typecheck + build (SIEMPRE antes de commitear)
npm run test:motor                # motor TS verificado contra docs/MOTOR_SAD_EXTRACCION.md

# backend (junto a las 4 .db en la raíz, o SAD_DATA_DIR)
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --port 8000
python -m backend.test_api        # 60 verificaciones del contrato
python -m backend.seed_demo       # DBs demo con esquemas reales (./demo_data)

# ingesta (dueña de los datos; el backend HTTP sigue siendo de solo lectura)
python -m backend.ingesta.extractor --probar    # 1 request de prueba (API_FOOTBALL_KEY en .env)
python -m backend.ingesta.extractor             # fixtures hoy−3d..+10d + cuotas NS (tope 95/día)
python -m backend.ingesta.pipeline --out .      # regenera levels/constants/discreto desde sad.db
python -m backend.ingesta.test_paridad          # test dorado vs DBs del pipeline viejo
```

Modo de datos por `.env`: `VITE_DATA_SOURCE=mock` (motor local demo) o
`http` + `VITE_API_BASE_URL` (backend real). Ver `.env.example`.

## Arquitectura (contract-first)

```
docs/openapi.yaml  ←── FUENTE DE VERDAD del contrato web↔backend
src/api/           DTOs + cliente fetch tipado
src/services/      datasource.ts (Mock/Http, MISMO contrato) · appdata.ts (DTO→UI)
src/motor/         Motor SAD en TS: niveles ventana-20, q*/k* con reseteo,
                   fusión k = k⁺+k⁻, bins v6, regresión §5 — VERIFICADO contra
                   docs/MOTOR_SAD_EXTRACCION.md; no tocar fórmulas sin ese doc
src/sections/      Partidos (inicio) · Cuotas · Burbujas · Skills · Estadísticas · Equipo
src/components/    KLineChart (picos K), TeamSearch, shell
backend/           FastAPI de SOLO LECTURA sobre sad/levels/constants/discreto.db
```

## Reglas del proyecto

- **Las `.db` jamás se commitean** (ya están en .gitignore). `backend/ingesta/`
  es la única capa que escribe datos: extractor → sad.db, pipeline → derivadas.
  El repo viejo (Professional-Player / D:/SAD_Replica) queda solo como referencia.
- La clave de API-Football vive en `.env` (API_FOOTBALL_KEY, git-ignorada) o en
  env vars; jamás hardcodeada ni con prefijo VITE_.
- Cambios de API: primero `docs/openapi.yaml`, luego backend + `src/api/types.ts`
  + ambos datasources (mock y http) + tests (`backend/test_api.py`).
- La matemática del motor es sagrada: cualquier cambio se valida contra
  `docs/MOTOR_SAD_EXTRACCION.md` y sus tests (`scripts/test-motor.ts`).
- Estilo UI: inline styles con las variables CSS del tema (`--bg`, `--t1`,
  `--up/--down`, fuentes `--sans`/`--mono`), números tabulares, todo en español.
- Git: trabajar en rama + merge; push a GitHub solo como respaldo (no editar
  "en la nube"). Respaldo alternativo: `git bundle create respaldo.bundle --all`.

## Estado actual

Hecho: 4 secciones + Partidos (pantalla inicial) + página de Equipo + buscador
inteligente; burbujas = gráfica de líneas de picos K con distinción de torneos
internacionales; gap §5 en Estadísticas; backend completo (38 tests verdes);
CI con dos jobs. Probado end-to-end con datos reales del usuario.

## Siguientes pasos (en orden)

1. **Familias nuevas de burbujas** — spec completa en `docs/ROADMAP_BURBUJAS.md`:
   empezar por `k_dc` (Doble Oportunidad), luego márgenes (±1/2/3+ goles),
   luego k_cuota_* sobre cuotas prepartido (regla de huecos ya definida).
2. Backend: xG/posesión desde estadísticas por partido; endpoint H2H
   (la card de Estadísticas sigue siendo demo).
3. Historial de cuotas por fixture para que la gráfica de movimiento sea real.
4. Fase nube cuando toque: `docs/SERVICIOS_EXTERNOS.md` (Postgres, ingesta, deploy).
