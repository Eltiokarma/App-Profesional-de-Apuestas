// Orquestador del pipeline (§6): historia → niveles → constantes → fusión.
// Regla de oro: nunca calcular constantes sin niveles al día (el q* de hoy
// pondera con el nivel del rival de hoy). Todo memoizado y determinista.
import { CONSTANTS_LEVEL_FALLBACK, K0, stepK } from './constants'
import { fuse, levelBin } from './discretizer'
import { LEAGUE_TEAMS, leagueOf, teamHistory } from './history'
import { computeTeamLevels, DEFAULT_LEVEL, levelAt } from './levels'
import type { KSnapshot, LevelRow, TeamEngine } from './types'

const _levels: Record<string, Record<string, LevelRow[]>> = {}

/** Niveles de TODA la liga (equivale a levels.db al día). */
function leagueLevels(lk: string): Record<string, LevelRow[]> {
  if (_levels[lk]) return _levels[lk]
  const map: Record<string, LevelRow[]> = {}
  for (const tm of LEAGUE_TEAMS[lk]) map[tm] = computeTeamLevels(teamHistory(lk, tm))
  return (_levels[lk] = map)
}

const _engine: Record<string, TeamEngine> = {}

export function teamEngine(teamId: string): TeamEngine | null {
  if (_engine[teamId]) return _engine[teamId]
  const lk = leagueOf(teamId)
  if (!lk) return null
  const levelsMap = leagueLevels(lk)
  const hist = teamHistory(lk, teamId)

  let k = { ...K0 }
  const snaps: KSnapshot[] = hist.map((h) => {
    // nivel continuo del RIVAL a la fecha del partido; fallback 1.0 (§3.1)
    const rivalLevel = levelAt(levelsMap[h.rival] ?? [], h.t, CONSTANTS_LEVEL_FALLBACK)
    const { q, k: nk } = stepK(k, h.isLocal, h.gf, h.ga, rivalLevel)
    k = nk
    return { ...h, rivalLevel, q, k: nk, fused: fuse(nk) }
  })

  const levels = levelsMap[teamId] ?? []
  const level = levels.length ? levels[levels.length - 1].level : DEFAULT_LEVEL
  const { bin, label } = levelBin(level)
  return (_engine[teamId] = { levels, snaps, level, bin, binLabel: label })
}
