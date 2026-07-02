// Ley de la Regresión al Nivel (§5) — consumidor directo de levels.db.
// Signo según el CÓDIGO (discrepancia 3 resuelta a su favor):
// gap = pts_esperados(μ) − pts_recientes; gap > 0 → rinde POR DEBAJO de su
// nivel (tiende a mejorar); gap < 0 → por encima (tiende a empeorar).
// Principio rector: "el value no cura el reset".
import { teamEngine } from './engine'
import type { TeamMatch } from './types'

/** Coeficientes de la regresión lineal calibrada de μ. */
export const MU = { intercept: 1.11, nivel: 0.686, rival: -0.669, localia: 0.422 } as const

/** Ventana de forma reciente. */
export const RECENT_WINDOW = 5

/** Rival promedio y localía neutra para pts_esperados. */
export const RIVAL_PROMEDIO = 2.0
export const LOCALIA_NEUTRA = 0.5

const clamp03 = (v: number) => Math.max(0, Math.min(3, v))

/** μ (puntos esperados) recortado a [0, 3]. `localia` ∈ [0, 1]. */
export function mu(nivelEquipo: number, nivelRival: number, localia: number): number {
  return clamp03(MU.intercept + MU.nivel * nivelEquipo + MU.rival * nivelRival + MU.localia * localia)
}

/** Promedio de puntos en los últimos 5 partidos; null si no hay 5 (WINDOW = 5). */
export function ptsRecent(hist: TeamMatch[]): number | null {
  if (hist.length < RECENT_WINDOW) return null
  let pts = 0
  for (let i = hist.length - RECENT_WINDOW; i < hist.length; i++) {
    const h = hist[i]
    pts += h.gf > h.ga ? 3 : h.gf === h.ga ? 1 : 0
  }
  return pts / RECENT_WINDOW
}

export type SenalGap = 'fuerte' | 'leve' | 'equilibrio'

/** Umbrales de señal: |gap| > 0.5 fuerte, 0.3–0.5 leve, < 0.3 equilibrio. */
export function senalDe(gap: number): SenalGap {
  const a = Math.abs(gap)
  return a > 0.5 ? 'fuerte' : a >= 0.3 ? 'leve' : 'equilibrio'
}

export interface GapResult {
  nivel: number
  ptsRecientes: number | null
  ptsEsperados: number
  gap: number | null
  senal: SenalGap | null
  tendencia: 'mejora' | 'empeora' | null
}

/** Gap de un equipo: expectativa μ con rival promedio (2.0) y 50 % de localía. */
export function gapFor(teamId: string): GapResult | null {
  const eng = teamEngine(teamId)
  if (!eng) return null
  const esperados = mu(eng.level, RIVAL_PROMEDIO, LOCALIA_NEUTRA)
  const recientes = ptsRecent(eng.snaps)
  const gap = recientes == null ? null : esperados - recientes
  return {
    nivel: eng.level,
    ptsRecientes: recientes,
    ptsEsperados: esperados,
    gap,
    senal: gap == null ? null : senalDe(gap),
    tendencia: gap == null || gap === 0 ? null : gap > 0 ? 'mejora' : 'empeora',
  }
}

/** Gap diferencial del fixture: gap_local − gap_visitante. */
export function gapDiff(homeId: string, awayId: string): number | null {
  const h = gapFor(homeId)
  const a = gapFor(awayId)
  if (!h || !a || h.gap == null || a.gap == null) return null
  return h.gap - a.gap
}
