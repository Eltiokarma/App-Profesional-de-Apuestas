// Cliente HTTP mínimo del backend SAD: fetch + timeout + errores tipados.
import { CONFIG } from '../config'

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public body?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export interface RequestOpts {
  signal?: AbortSignal
  timeoutMs?: number
}

export async function apiGet<T>(path: string, opts: RequestOpts = {}): Promise<T> {
  const ctrl = new AbortController()
  const timeout = setTimeout(() => ctrl.abort(), opts.timeoutMs ?? 10_000)
  opts.signal?.addEventListener('abort', () => ctrl.abort(), { once: true })
  try {
    const headers: Record<string, string> = { Accept: 'application/json' }
    if (CONFIG.apiKey) headers.Authorization = `Bearer ${CONFIG.apiKey}`
    const res = await fetch(CONFIG.apiBaseUrl + path, { headers, signal: ctrl.signal })
    if (!res.ok) {
      let body: unknown
      try {
        body = await res.json()
      } catch {
        /* cuerpo no-JSON */
      }
      throw new ApiError(res.status, `GET ${path} → ${res.status} ${res.statusText}`, body)
    }
    return (await res.json()) as T
  } finally {
    clearTimeout(timeout)
  }
}

const qs = (params: Record<string, string | number | undefined>) => {
  const p = Object.entries(params).filter(([, v]) => v !== undefined && v !== '')
  return p.length ? '?' + p.map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`).join('&') : ''
}

export { qs }
