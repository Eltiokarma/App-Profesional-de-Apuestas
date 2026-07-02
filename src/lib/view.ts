import { TEAMS } from '../data'
import type { Match } from '../data/types'

export interface MatchView {
  homeName: string
  homeShort: string
  homeColor: string
  homeFg: string
  awayName: string
  awayShort: string
  awayColor: string
  awayFg: string
  league: string
  date: string
  venue: string
}

export function matchView(m: Match): MatchView {
  const H = TEAMS[m.home]
  const A = TEAMS[m.away]
  return {
    homeName: H.name,
    homeShort: H.short,
    homeColor: H.color,
    homeFg: H.fg,
    awayName: A.name,
    awayShort: A.short,
    awayColor: A.color,
    awayFg: A.fg,
    league: m.league,
    date: m.date,
    venue: m.venue,
  }
}
