// Cliente HTTP mínimo del backend SAD: fetch + timeout + errores tipados.
import { CONFIG } from '../config'
import { llaveAdmin } from '../lib/admin'

/** La llave de administrador (si el dueño la pegó en este navegador) manda
 *  sobre el token de lectura del bundle. */
const token = () => llaveAdmin() || CONFIG.apiKey

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
    if (token()) headers.Authorization = `Bearer ${token()}`
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

/** POST JSON. El análisis EFE puede tardar 1-3 min: pasar timeoutMs generoso. */
export async function apiPost<T>(path: string, body: unknown, opts: RequestOpts = {}): Promise<T> {
  return apiEnviar<T>('POST', path, body, opts)
}

export async function apiDelete<T>(path: string, opts: RequestOpts = {}): Promise<T> {
  return apiEnviar<T>('DELETE', path, undefined, opts)
}

async function apiEnviar<T>(method: 'POST' | 'DELETE', path: string, body: unknown, opts: RequestOpts = {}): Promise<T> {
  const ctrl = new AbortController()
  const timeout = setTimeout(() => ctrl.abort(), opts.timeoutMs ?? 30_000)
  opts.signal?.addEventListener('abort', () => ctrl.abort(), { once: true })
  try {
    const headers: Record<string, string> = { Accept: 'application/json' }
    if (body !== undefined) headers['Content-Type'] = 'application/json'
    if (token()) headers.Authorization = `Bearer ${token()}`
    const res = await fetch(CONFIG.apiBaseUrl + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), signal: ctrl.signal })
    if (!res.ok) {
      let resBody: unknown
      try {
        resBody = await res.json()
      } catch {
        /* cuerpo no-JSON */
      }
      const detalle = (resBody as { detail?: string } | undefined)?.detail
      throw new ApiError(res.status, detalle || `${method} ${path} → ${res.status} ${res.statusText}`, resBody)
    }
    return (await res.json()) as T
  } finally {
    clearTimeout(timeout)
  }
}
