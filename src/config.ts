// Configuración por entorno (Vite). Ver .env.example y docs/SERVICIOS_EXTERNOS.md.
export type DataSourceMode = 'mock' | 'http'

const env = import.meta.env

export const CONFIG = {
  /** 'mock': motor local determinista (demo) · 'http': backend FastAPI real. */
  dataSource: (env.VITE_DATA_SOURCE === 'http' ? 'http' : 'mock') as DataSourceMode,
  apiBaseUrl: (env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1').replace(/\/+$/, ''),
  apiKey: env.VITE_API_KEY ?? '',
  pollHealthMs: Math.max(5_000, Number(env.VITE_POLL_HEALTH_MS ?? 30_000) || 30_000),
  pollLiveMs: Math.max(10_000, Number(env.VITE_POLL_LIVE_MS ?? 60_000) || 60_000),
} as const
