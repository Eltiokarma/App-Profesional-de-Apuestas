# ARQUITECTURA — SAD Webapp (Railway + Vercel + Anthropic API)

Objetivo: llevar EFE+DTP a la webapp existente, minimizando gasto de créditos con caché de prompts, persistencia de datos y salida JSON (no JSX).

---

## 1. Principio central de ahorro: el modelo NO genera código

En Claude.ai, cada dashboard JSX cuesta ~8-12k tokens de salida (lo más caro). En la webapp eso desaparece:

- **Frontend Vercel:** componentes React FIJOS ya desplegados — `<GaugeRing>`, `<BlockCard>`, `<ZoneBars>`, `<PizarraGol>`, `<MapaDuelos>`, `<PlanFases>`, `<MatrizV2>`. Se portan UNA vez desde los JSX que ya generamos en Claude.ai (reutilizar el último `efe_dashboard.jsx` y `dtp_*.jsx` como base).
- **API:** devuelve solo JSON de datos (~2-3k tokens de salida). El frontend lo renderiza.

**Ahorro estimado en salida: 70-80% por análisis.**

---

## 2. Stack

```
Vercel (frontend Next.js)          Railway (backend + Postgres)
┌────────────────────────┐        ┌──────────────────────────────┐
│ /partido/[id]          │  HTTPS │ API Node/Express o FastAPI    │
│  Dashboard EFE (fijo)  │◄──────►│  /api/efe   /api/dtp          │
│  DTP + Matriz (fijo)   │        │  /api/matriz /api/cierre      │
│  Historial de cadena   │        │        │                      │
└────────────────────────┘        │        ▼                      │
                                  │  Capa de caché (Postgres)     │
                                  │        │ solo lo faltante     │
                                  │        ▼                      │
                                  │  Anthropic API                │
                                  │  (system con prompt caching)  │
                                  └──────────────────────────────┘
```

---

## 3. Llamada a la API con prompt caching

El system prompt son dos bloques grandes y estables → **cache_control ephemeral**. En cache hit, la lectura cuesta **10% del precio de input** (90% de descuento).

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: {
    "content-type": "application/json",
    "x-api-key": process.env.ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01"
  },
  body: JSON.stringify({
    model: "claude-sonnet-4-6",
    max_tokens: 8000,
    system: [
      { type: "text", text: EFE_V15_PROMPT,        cache_control: { type: "ephemeral" } },
      { type: "text", text: SAD_API_INSTRUCTIONS,  cache_control: { type: "ephemeral" } }
    ],
    tools: webSearchNecesario ? [{ type: "web_search_20250305", name: "web_search", max_uses: 6 }] : [],
    messages: [{
      role: "user",
      content: JSON.stringify({
        modo: "efe",
        partido: { equipo_a: "Universitario", equipo_b: "Alianza Lima", fecha: "2026-07-19" },
        datos_cacheados: datosDesdePostgres,   // ← la clave del ahorro
        campos_faltantes: ["xi_confirmado_b", "bajas_b"]
      })
    }]
  })
});
```

Notas:
- La caché ephemeral dura ~5 min y se renueva con cada uso → en una sesión de trabajo (EFE → DTP → Matriz) solo la PRIMERA llamada paga el system completo.
- Verificar el uso real en `response.usage` (`cache_creation_input_tokens` vs `cache_read_input_tokens`).
- Cuando salga EFE v1.6, se actualiza el bloque 1 y la caché se regenera sola.

---

## 4. Esquema Postgres (Railway) — la segunda palanca de ahorro

```sql
-- Datos de investigación con TTL por tipo
CREATE TABLE investigacion (
  id SERIAL PRIMARY KEY,
  equipo TEXT NOT NULL,
  tipo TEXT NOT NULL,          -- 'dt', 'plantel', 'xi_reciente', 'resultados', 'tabla', 'fixture', 'bajas'
  contenido JSONB NOT NULL,
  fuentes TEXT[],
  capturado_en TIMESTAMPTZ DEFAULT now(),
  UNIQUE (equipo, tipo)
);

-- Análisis completos (nunca regenerar lo ya hecho)
CREATE TABLE analisis (
  id SERIAL PRIMARY KEY,
  tipo TEXT NOT NULL,          -- 'efe', 'dtp', 'matriz'
  equipo_a TEXT, equipo_b TEXT,
  fecha_partido DATE,
  resultado_json JSONB NOT NULL,
  version_efe TEXT DEFAULT '1.5',
  creado_en TIMESTAMPTZ DEFAULT now()
);

-- Cadena rodante DTP por equipo foco
CREATE TABLE cadena_dtp (
  id SERIAL PRIMARY KEY,
  equipo_foco TEXT NOT NULL,
  partido_n INT NOT NULL,
  rival TEXT, fecha DATE,
  apertura_json JSONB,         -- pronóstico (M1-M3, M6)
  cierre_json JSONB,           -- validación (M4-M5) — se llena post-partido
  registro JSONB,              -- {pronostico_clave, que_paso, veredicto, leccion}
  UNIQUE (equipo_foco, partido_n)
);

-- Registro de validación (Casos 1, 2, ...) para calibración
CREATE TABLE casos_validacion (
  id SERIAL PRIMARY KEY,
  caso_num INT, partido TEXT, fecha DATE,
  que_acerto JSONB, que_fallo JSONB, correccion_derivada TEXT
);
```

**TTL sugeridos por tipo de dato:**

| Tipo | TTL | Razón |
|------|-----|-------|
| `dt`, `plantel` | 14 días | Cambian por mercado/crisis |
| `tabla`, `resultados` | 24 h (o tras cada jornada) | |
| `fixture` | 7 días | |
| `xi_reciente`, `bajas` | 48 h → **siempre refrescar el día del partido** | Regla del 11 confirmado |
| `analisis` (EFE/DTP) | Permanente | Histórico de validación |

**Flujo del backend antes de llamar a la API:**
1. Consultar `investigacion` para ambos equipos
2. Marcar campos vencidos/ausentes como `campos_faltantes`
3. Si TODO está fresco → llamada SIN web search tool (más barato: web search cuesta $10/1000 búsquedas además de los tokens)
4. Si faltan campos → habilitar web search con `max_uses` acotado (4-6)
5. Al recibir respuesta, hacer UPSERT de los datos nuevos en `investigacion` (el modo `extraccion` con Haiku puede normalizarlos) y guardar el análisis en `analisis`

---

## 5. Modelo por tarea (tercera palanca)

| Tarea | Modelo | Por qué |
|-------|--------|---------|
| EFE completo, DTP, Matriz | `claude-sonnet-4-6` | Razonamiento del protocolo |
| Modo `extraccion` (normalizar noticias a JSON para caché) | `claude-haiku-4-5-20251001` | ~1/3 del costo, tarea mecánica |
| Recalibración de skill / cambios de versión | Claude.ai (aquí) | Sin costo de API, con acceso a los skills |

---

## 6. Endpoints sugeridos

| Endpoint | Modo API | Cachea |
|----------|----------|--------|
| `POST /api/efe` | `efe` | análisis + investigación |
| `POST /api/dtp` | `dtp_apertura` o `dtp_completo` (si hay N-1 en `cadena_dtp`) | apertura en `cadena_dtp` |
| `POST /api/cierre` | `dtp_completo` con resultado real | cierre + registro |
| `POST /api/matriz` | `matriz` — **input: el JSON del EFE ya guardado, sin web search** | matriz |
| `GET /api/partido/:id` | — | lee de `analisis`, cero créditos |

La Matriz es el caso perfecto de ahorro: no necesita investigación nueva, solo el JSON del EFE previo como input.

---

## 7. División de trabajo Claude.ai vs webapp

| Queda en Claude.ai (skill `efe-dtp`) | Va a la webapp |
|--------------------------------------|----------------|
| Desarrollo y calibración del modelo | Ejecución rutinaria de análisis |
| Casos de validación nuevos → versión v1.6 | Consumo del prompt versionado |
| Diseño/iteración de componentes visuales | Componentes fijos desplegados |
| Timeline (`futbol-timeline`) por ahora | (portable después con el mismo patrón JSON) |

**Sincronización de versiones:** `EFE_v1_X_prompt.md` es la fuente única. Cuando se actualiza en el proyecto de Claude.ai, se copia al repo del backend (variable/archivo `EFE_V15_PROMPT`). Un solo archivo, dos consumidores.

---

## 8. Estimación de costo por análisis (Sonnet 4.6, con caché caliente)

| Componente | Tokens aprox | Costo aprox |
|-----------|--------------|-------------|
| System (cache read, ~14k tokens) | 14k × 10% | ~$0.004 |
| Datos cacheados + request (~4k input) | 4k | ~$0.012 |
| Web search (solo si falta data, 4 búsquedas) | — | ~$0.04 + tokens |
| Salida JSON (~2.5k) | 2.5k | ~$0.038 |
| **Total EFE con datos frescos en DB** | | **~$0.05-0.06** |
| **Total EFE con web search completo** | | **~$0.15-0.25** |

(Precios de referencia; verificar los vigentes en docs.claude.com. La diferencia muestra por qué la tabla `investigacion` es la palanca #1 después del JSON output.)

---

## 9. Próximos pasos

1. ☐ Subir `efe-dtp.skill` a Claude.ai y desactivar/eliminar `efe-dashboard` y `diagnostico-tactico` (evitar triggers duplicados)
2. ☐ Crear las tablas en Postgres de Railway
3. ☐ Portar el último dashboard JSX a componentes fijos en el frontend Vercel (yo puedo generar ese port cuando quieras)
4. ☐ Implementar el endpoint `/api/efe` con prompt caching y probarlo con un partido ya validado (comparar contra el análisis de Claude.ai)
5. ☐ Conectar la cadena DTP: `apertura` al analizar, `cierre` al cargar el resultado
6. ☐ Migrar el registro de casos de validación existente a `casos_validacion`
