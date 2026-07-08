import { TEAMS } from '../data'
import type { Match } from '../data/types'

export interface MatchView {
  homeKey: string
  homeName: string
  homeShort: string
  homeColor: string
  homeFg: string
  homeLogo?: string | null
  awayKey: string
  awayName: string
  awayShort: string
  awayColor: string
  awayFg: string
  awayLogo?: string | null
  league: string
  ligaId?: number
  date: string
  venue: string
}

export function matchView(m: Match): MatchView {
  const H = TEAMS[m.home]
  const A = TEAMS[m.away]
  return {
    homeKey: m.home,
    homeName: H.name,
    homeShort: H.short,
    homeColor: H.color,
    homeFg: H.fg,
    homeLogo: H.logo,
    awayKey: m.away,
    awayName: A.name,
    awayShort: A.short,
    awayColor: A.color,
    awayFg: A.fg,
    awayLogo: A.logo,
    league: m.league,
    ligaId: m.ligaId,
    date: m.date,
    venue: m.venue,
  }
}
