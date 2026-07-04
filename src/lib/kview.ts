// Helpers compartidos para visualizar las constantes K (Burbujas y página de Equipo).
import type { KCondKey, KTypeKey } from '../data/types'
import type { FusedK, KSnapshot } from '../motor/types'

export const FUSED_KEY: Record<KTypeKey, Record<KCondKey, keyof FusedK>> = {
  res: { total: 'k', local: 'kLocal', visita: 'kVisita' },
  ga: { total: 'golesAnotado', local: 'golesLocalAnotado', visita: 'golesVisitaAnotado' },
  gr: { total: 'golesRecibido', local: 'golesLocalRecibido', visita: 'golesVisitaRecibido' },
  dc: { total: 'kDc', local: 'kDcLocal', visita: 'kDcVisita' },
}

/** Valor con signo de display: para goles recibidos la racha alta es desfavorable. */
export const signedVal = (kType: KTypeKey, v: number) => (kType === 'gr' ? -v : v)

export const fmtK = (v: number) => (Math.abs(v) >= 20 ? v.toFixed(0) : v.toFixed(1))
export const signFmt = (v: number) => (v > 0 ? '+' + fmtK(v) : fmtK(v))

export function binBadge(bin: number): { color: string; soft: string } {
  if (bin >= 8) return { color: 'var(--up)', soft: 'var(--up-soft)' }
  if (bin >= 6) return { color: 'var(--accent)', soft: 'var(--accent-soft)' }
  if (bin >= 4) return { color: 'var(--mark)', soft: 'var(--mark-soft)' }
  if (bin >= 1) return { color: 'var(--down)', soft: 'var(--down-soft)' }
  return { color: 'var(--t3)', soft: 'var(--bg3)' }
}

/** Racha activa: partidos desde el último reseteo de la K seleccionada. */
export function streakLen(snaps: KSnapshot[], key: keyof FusedK): number {
  let n = 0
  for (let i = snaps.length - 1; i >= 0 && snaps[i].fused[key] !== 0; i--) n++
  return n
}

/** Último aporte q a la K seleccionada (último partido de la condición). */
export function lastQ(snaps: KSnapshot[], kType: KTypeKey, kCond: KCondKey): number | null {
  for (let i = snaps.length - 1; i >= 0; i--) {
    const s = snaps[i]
    if (kCond === 'local' && !s.isLocal) continue
    if (kCond === 'visita' && s.isLocal) continue
    if (kType === 'ga') return s.q.golesAnotado
    if (kType === 'gr') return s.q.golesRecibido
    if (kType === 'dc') return s.q.dc
    return s.isLocal ? s.q.local : s.q.visita
  }
  return null
}
