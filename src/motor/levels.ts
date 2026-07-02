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
