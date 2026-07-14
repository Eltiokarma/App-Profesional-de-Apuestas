export type FormResult = 'W' | 'D' | 'L'

export interface Team {
  name: string
  short: string
  color: string
  fg: string
  /** URL del escudo (contrato Equipo.logo); ausente → iniciales de color. */
  logo?: string | null
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
  /** Id numérico de la liga en el contrato (140 LaLiga, 39 Premier, 135 Serie A…). */
  ligaId?: number
  /** URL del logo del torneo (null/ausente → sin imagen). */
  ligaLogo?: string | null
  /** URL de la bandera del país (null en copas internacionales). */
  ligaBandera?: string | null
  /** País del torneo: desambigua homónimos (Copa de la Liga de Perú vs Chile). */
  ligaPais?: string | null
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

/** Tipo de constante K fusionada del Motor SAD: resultado / goles anotados /
 *  goles recibidos / doble oportunidad (§3.6) / márgenes por N goles (§3.7). */
export type KTypeKey =
  | 'res' | 'ga' | 'gr' | 'dc'
  | 'vic1' | 'vic2' | 'vic3' | 'der1' | 'der2' | 'der3'
/** Condición de la K: total, solo local o solo visita. */
export type KCondKey = 'total' | 'local' | 'visita'
export type SectionKey = 'partidos' | 'cuotas' | 'burbujas' | 'analisis' | 'skills' | 'estadisticas' | 'equipo' | 'liga'
export type OddsMode = 'prematch' | 'live'
export type SkillState = 'idle' | 'gen' | 'done'
