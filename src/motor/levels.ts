// Motor de Niveles (§2) — port de levels_calculator.py.
// Nivel = P + G + 1, con P = puntos/20 en ventana móvil de 20 partidos
// y G = balance de goles de los últimos 5 de esa ventana.
import type { LevelRow, TeamMatch } from './types'

export const DEFAULT_LEVEL = 0.5

const points = (m: TeamMatch) => (m.gf > m.ga ? 3 : m.gf === m.ga ? 1 : 0)

/**
 * Historia completa de un equipo (ordenada por t) → una fila de nivel por partido.
 * Regla retroactiva (§2.2): con <20 partidos todos valen 0.5; en el partido nº 20
 * se calcula el primer nivel real y se asigna a los 20 primeros.
 */
export function computeTeamLevels(hist: TeamMatch[]): LevelRow[] {
  const n = hist.length
  if (n === 0) return []
  if (n < 20) return hist.map((h) => ({ fixtureId: h.fixtureId, t: h.t, level: DEFAULT_LEVEL }))
  const levels = new Array<number>(n)
  for (let i = 19; i < n; i++) {
    let pts = 0
    for (let j = i - 19; j <= i; j++) pts += points(hist[j])
    const P = pts / 20
    let dg = 0
    let tg = 0
    for (let j = i - 4; j <= i; j++) {
      dg += hist[j].gf - hist[j].ga
      tg += hist[j].gf + hist[j].ga
    }
    const G = tg === 0 ? 0 : dg / tg
    levels[i] = P + G + 1
  }
  for (let i = 0; i < 19; i++) levels[i] = levels[19]
  return hist.map((h, i) => ({ fixtureId: h.fixtureId, t: h.t, level: levels[i] }))
}

/** Las dos piezas del nivel (§2.1) del partido `i`: P = puntos/20 y G = balance de
 *  goles de los últimos 5. null con <20 partidos; con i < 19 rige la regla
 *  retroactiva (las piezas del partido nº 20). Espejo de `desglose_nivel`
 *  (backend/ingesta/niveles.py): el nivel vive en una retícula y la misma suma
 *  sale de muchas combinaciones — con el desglose a la vista se ve cuál. */
export function levelBreakdown(hist: TeamMatch[], i: number): NivelDesglose | null {
  const n = hist.length
  if (n < 20) return null
  i = Math.max(i, 19)
  if (i >= n) return null
  const ventana = hist.slice(i - 19, i + 1)
  const pts = ventana.reduce((s, m) => s + points(m), 0)
  const u5 = ventana.slice(-5)
  const gf5 = u5.reduce((s, m) => s + m.gf, 0)
  const ga5 = u5.reduce((s, m) => s + m.ga, 0)
  const tg = gf5 + ga5
  const g = tg === 0 ? 0 : (gf5 - ga5) / tg
  return {
    puntos: Math.round((pts / 20) * 10000) / 10000,
    goles: Math.round(g * 10000) / 10000,
    puntosVentana: pts,
    partidosVentana: ventana.length,
    golesFavor5: gf5,
    golesContra5: ga5,
  }
}

export interface NivelDesglose {
  puntos: number
  goles: number
  puntosVentana: number
  partidosVentana: number
  golesFavor5: number
  golesContra5: number
}

/**
 * Nivel a fecha (§2.3): último level con t <= consulta (bisect, como el cache
 * en memoria del original). `fallback` es 0.5 para consumo general y 1.0
 * cuando pondera constantes (§5, discrepancia 2 — resuelta a favor del código).
 */
export function levelAt(rows: LevelRow[], t: number, fallback: number): number {
  let lo = 0
  let hi = rows.length - 1
  let ans = -1
  while (lo <= hi) {
    const mid = (lo + hi) >> 1
    if (rows[mid].t <= t) {
      ans = mid
      lo = mid + 1
    } else hi = mid - 1
  }
  return ans < 0 ? fallback : rows[ans].level
}
