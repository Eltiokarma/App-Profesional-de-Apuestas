// Helpers compartidos para visualizar las constantes K (Burbujas y página de Equipo).
import type { KCondKey, KTypeKey } from '../data/types'
import type { FusedK, KSnapshot } from '../motor/types'

/** Opciones del selector de ventana de la gráfica (Infinity = toda la historia). */
export const K_WINDOW_OPTS: [number, string][] = [[8, '8'], [15, '15'], [30, '30'], [50, '50'], [100, '100'], [Infinity, 'Todo']]

/** Grupos del selector de tipo de K (Resultado · Goles · Mercados · Márgenes),
 *  compartidos por Burbujas y la página de Equipo. */
export const K_TYPE_GROUPS: { label: string; opts: [KTypeKey, string][] }[] = [
  { label: 'Resultado', opts: [['res', 'K']] },
  { label: 'Goles', opts: [['ga', 'Anotados'], ['gr', 'Recibidos']] },
  { label: 'Mercados', opts: [['dc', 'Doble op.']] },
  {
    label: 'Márgenes',
    opts: [['vic1', 'V·1'], ['vic2', 'V·2'], ['vic3', 'V·3+'], ['der1', 'D·1'], ['der2', 'D·2'], ['der3', 'D·3+']],
  },
]

export const FUSED_KEY: Record<KTypeKey, Record<KCondKey, keyof FusedK>> = {
  res: { total: 'k', local: 'kLocal', visita: 'kVisita' },
  ga: { total: 'golesAnotado', local: 'golesLocalAnotado', visita: 'golesVisitaAnotado' },
  gr: { total: 'golesRecibido', local: 'golesLocalRecibido', visita: 'golesVisitaRecibido' },
  dc: { total: 'kDc', local: 'kDcLocal', visita: 'kDcVisita' },
  vic1: { total: 'kVic1', local: 'kVic1Local', visita: 'kVic1Visita' },
  vic2: { total: 'kVic2', local: 'kVic2Local', visita: 'kVic2Visita' },
  vic3: { total: 'kVic3', local: 'kVic3Local', visita: 'kVic3Visita' },
  der1: { total: 'kDer1', local: 'kDer1Local', visita: 'kDer1Visita' },
  der2: { total: 'kDer2', local: 'kDer2Local', visita: 'kDer2Visita' },
  der3: { total: 'kDer3', local: 'kDer3Local', visita: 'kDer3Visita' },
}

/** Tipos "hacia abajo": la racha alta es desfavorable (goles recibidos, derrotas). */
const DOWN_TYPES = new Set<KTypeKey>(['gr', 'der1', 'der2', 'der3'])

/** Valor con signo de display: los tipos desfavorables se pintan en negativo. */
export const signedVal = (kType: KTypeKey, v: number) => (DOWN_TYPES.has(kType) ? -v : v)

/** Aporte q por partido de las familias de márgenes (§3.7): nivel_rival si el
 *  partido casa con el signo+margen de la familia, si no 0. Se calcula inline
 *  (no viaja en el contrato) desde los goles y el nivel del rival del snapshot. */
export function marginQ(kType: KTypeKey, gf: number, ga: number, rivalLevel: number): number {
  const bucket = Math.min(Math.abs(gf - ga), 3)
  const win = gf > ga
  const loss = gf < ga
  switch (kType) {
    case 'vic1': return win && bucket === 1 ? rivalLevel : 0
    case 'vic2': return win && bucket === 2 ? rivalLevel : 0
    case 'vic3': return win && bucket === 3 ? rivalLevel : 0
    case 'der1': return loss && bucket === 1 ? rivalLevel : 0
    case 'der2': return loss && bucket === 2 ? rivalLevel : 0
    case 'der3': return loss && bucket === 3 ? rivalLevel : 0
    default: return 0
  }
}

/** true para las 6 familias de márgenes (§3.7). */
export const isMargin = (kType: KTypeKey) => kType.startsWith('vic') || kType.startsWith('der')

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
    if (isMargin(kType)) return marginQ(kType, s.gf, s.ga, s.rivalLevel)
    return s.isLocal ? s.q.local : s.q.visita
  }
  return null
}
