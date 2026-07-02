export type FormResult = 'W' | 'D' | 'L'

export interface Team {
  name: string
  short: string
  color: string
  fg: string
  pts: number
  pos: number
  form: FormResult[]
  gf: number
  gc: number
  xg: number
  poss: number
  sot: number
  corn: number
}

export type MatchStatus = 'live' | 'sched' | 'fin'

export interface Match {
  id: string
  home: string
  away: string
  comp: string
  league: string
  date: string
  venue: string
  lk: string
  score: string
  status: MatchStatus
  min: string
}

export interface MarketSel {
  k: string
  tag?: string
  label: string
}

export interface MarketDef {
  key: string
  title: string
  sub: string
  featured?: boolean
  base: Record<string, number>
  sels: (m: Match) => MarketSel[]
}

export interface SkillDef {
  key: string
  abbr: string
  name: string
  desc: string
  iconBg: string
  iconColor: string
}

export type LevelKey = 'elite' | 'alto' | 'medio' | 'bajo'

export interface Level {
  k: LevelKey
  label: string
  color: string
  soft: string
}

/** Tipo de constante K fusionada del Motor SAD: resultado / goles anotados / goles recibidos. */
export type KTypeKey = 'res' | 'ga' | 'gr'
/** Condición de la K: total, solo local o solo visita. */
export type KCondKey = 'total' | 'local' | 'visita'
export type ModelKey = 'auto' | 'global' | 'liga'
export type SectionKey = 'cuotas' | 'burbujas' | 'skills' | 'estadisticas'
export type OddsMode = 'prematch' | 'live'
export type SkillState = 'idle' | 'gen' | 'done'
