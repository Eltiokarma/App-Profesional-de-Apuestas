/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Fuente de datos de la app: 'mock' (motor local demo) | 'http' (backend FastAPI). */
  readonly VITE_DATA_SOURCE?: string
  /** URL base del backend, p. ej. https://api.midominio.com/api/v1 */
  readonly VITE_API_BASE_URL?: string
  /** Token bearer de desarrollo (⚠ visible en el bundle; solo para entornos de prueba). */
  readonly VITE_API_KEY?: string
  /** Intervalo del health-check del feed (ms). */
  readonly VITE_POLL_HEALTH_MS?: string
  /** Intervalo de refresco de cuotas en vivo (ms). */
  readonly VITE_POLL_LIVE_MS?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
