// Fuente de fixtures del motor (equivale a sad.db, §1).
// La app es un prototipo sin backend: se sintetiza una historia determinista
// de ~40 partidos terminados por equipo (round-robin doble repetido) con
// marcadores plausibles sesgados por la fuerza real del equipo, para que
// niveles y constantes K salgan del pipeline auténtico.
import { TEAMS } from '../data'
import { rng } from '../lib/odds'
import type { Fixture, TeamMatch } from './types'

export const LEAGUE_TEAMS: Record<string, string[]> = {
  laliga: ['bet', 'sev', 'atm', 'vil', 'rma', 'bar'],
  premier: ['ars', 'tot', 'liv', 'che'],
  seriea: ['int', 'mil', 'juv', 'rom'],
}

// ciclos de round-robin doble → ~40 partidos por equipo (ventana 20 cómoda)
const CYCLES: Record<string, number> = { laliga: 4, premier: 7, seriea: 7 }
const ID_OFFSET: Record<string, number> = { laliga: 10000, premier: 20000, seriea: 30000 }

const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v))
const strength = (id: string) => (TEAMS[id].pts - 40) / 44

/** Muestra Poisson con el PRNG determinista (método de Knuth, cap 7 goles). */
function pois(r: () => number, lambda: number): number {
  const L = Math.exp(-lambda)
  let k = 0
  let p = 1
  do {
    k++
    p *= r()
  } while (p > L && k < 8)
  return k - 1
}

/** Calendario round-robin (método del círculo) para n par. */
function roundRobinRounds(teams: string[]): [string, string][][] {
  const n = teams.length
  const arr = teams.slice()
  const rounds: [string, string][][] = []
  for (let r = 0; r < n - 1; r++) {
    const pairs: [string, string][] = []
    for (let i = 0; i < n / 2; i++) {
      const a = arr[i]
      const b = arr[n - 1 - i]
      pairs.push(r % 2 ? [b, a] : [a, b])
    }
    rounds.push(pairs)
    arr.splice(1, 0, arr.pop()!)
  }
  return rounds
}

const _fx: Record<string, Fixture[]> = {}

export function leagueFixtures(lk: string): Fixture[] {
  if (_fx[lk]) return _fx[lk]
  const teams = LEAGUE_TEAMS[lk]
  if (!teams) return (_fx[lk] = [])
  const single = roundRobinRounds(teams)
  const dbl = [...single, ...single.map((rd) => rd.map(([h, a]) => [a, h] as [string, string]))]
  const out: Fixture[] = []
  let t = 0
  let id = ID_OFFSET[lk] ?? 90000
  for (let c = 0; c < (CYCLES[lk] ?? 4); c++) {
    for (const rd of dbl) {
      for (const [home, away] of rd) {
        const r = rng('fx|' + lk + '|' + id)
        const sh = strength(home)
        const sa = strength(away)
        const lh = clamp(TEAMS[home].gf * (1 + 0.5 * (sh - sa)) + 0.2, 0.2, 3.4)
        const la = clamp(TEAMS[away].gf * (1 + 0.5 * (sa - sh)) * 0.85, 0.15, 3.0)
        out.push({ id, t, home, away, gh: pois(r, lh), ga: pois(r, la) })
        id++
      }
      t++ // el orden cronológico gobierna los acumuladores (§1.2)
    }
  }
  return (_fx[lk] = out)
}

/** Doble fila por partido (§1.2): la historia desde la perspectiva del equipo. */
export function teamHistory(lk: string, teamId: string): TeamMatch[] {
  return leagueFixtures(lk)
    .filter((f) => f.home === teamId || f.away === teamId)
    .map((f) => {
      const isLocal = f.home === teamId
      return {
        fixtureId: f.id,
        t: f.t,
        rival: isLocal ? f.away : f.home,
        isLocal,
        gf: isLocal ? f.gh : f.ga,
        ga: isLocal ? f.ga : f.gh,
        // cada ~9ª jornada simula un torneo internacional (espejo del seed del backend)
        esInternacional: f.t % 9 === 4,
      }
    })
}

export function leagueOf(teamId: string): string | null {
  for (const lk of Object.keys(LEAGUE_TEAMS)) if (LEAGUE_TEAMS[lk].includes(teamId)) return lk
  return null
}
