import type { Level, MarketDef, Match, SkillDef, Team } from './types'

export const TEAMS: Record<string, Team> = {
  bet: { name: 'Real Betis', short: 'BET', color: '#00954C', fg: '#fff', pts: 52, pos: 6, form: ['W', 'D', 'W', 'W', 'L'], gf: 1.8, gc: 1.1, xg: 1.62, poss: 54, sot: 5.4, corn: 5.8 },
  sev: { name: 'Sevilla FC', short: 'SEV', color: '#D9001B', fg: '#fff', pts: 41, pos: 11, form: ['L', 'W', 'D', 'L', 'W'], gf: 1.3, gc: 1.4, xg: 1.21, poss: 48, sot: 4.2, corn: 4.9 },
  atm: { name: 'Atlético', short: 'ATM', color: '#C8102E', fg: '#fff', pts: 67, pos: 3, form: ['W', 'W', 'W', 'D', 'W'], gf: 2.0, gc: 0.8, xg: 1.9, poss: 56, sot: 6.1, corn: 6.2 },
  vil: { name: 'Villarreal', short: 'VIL', color: '#FFE667', fg: '#1A1A1A', pts: 49, pos: 7, form: ['D', 'L', 'W', 'W', 'D'], gf: 1.6, gc: 1.5, xg: 1.5, poss: 52, sot: 4.8, corn: 5.1 },
  ars: { name: 'Arsenal', short: 'ARS', color: '#EF0107', fg: '#fff', pts: 71, pos: 2, form: ['W', 'W', 'D', 'W', 'W'], gf: 2.1, gc: 0.9, xg: 1.95, poss: 58, sot: 6.4, corn: 6.6 },
  tot: { name: 'Tottenham', short: 'TOT', color: '#132257', fg: '#fff', pts: 48, pos: 9, form: ['L', 'W', 'L', 'D', 'W'], gf: 1.7, gc: 1.6, xg: 1.6, poss: 53, sot: 5.2, corn: 5.4 },
  int: { name: 'Inter', short: 'INT', color: '#0A2D8C', fg: '#fff', pts: 78, pos: 1, form: ['W', 'D', 'W', 'W', 'W'], gf: 2.2, gc: 0.9, xg: 2.0, poss: 55, sot: 6.6, corn: 6.0 },
  mil: { name: 'Milan', short: 'MIL', color: '#FB090B', fg: '#fff', pts: 54, pos: 6, form: ['W', 'L', 'D', 'W', 'L'], gf: 1.5, gc: 1.3, xg: 1.45, poss: 51, sot: 5.0, corn: 5.3 },
  rma: { name: 'Real Madrid', short: 'RMA', color: '#FEBE10', fg: '#1A1A1A', pts: 82, pos: 1, form: ['W', 'W', 'W', 'W', 'D'], gf: 2.4, gc: 0.7, xg: 2.2, poss: 60, sot: 7.0, corn: 6.8 },
  bar: { name: 'Barcelona', short: 'BAR', color: '#A50044', fg: '#fff', pts: 78, pos: 2, form: ['W', 'W', 'D', 'W', 'W'], gf: 2.3, gc: 0.9, xg: 2.1, poss: 62, sot: 6.9, corn: 6.5 },
  liv: { name: 'Liverpool', short: 'LIV', color: '#C8102E', fg: '#fff', pts: 84, pos: 1, form: ['W', 'W', 'W', 'D', 'W'], gf: 2.3, gc: 0.8, xg: 2.1, poss: 59, sot: 6.8, corn: 6.4 },
  che: { name: 'Chelsea', short: 'CHE', color: '#034694', fg: '#fff', pts: 52, pos: 7, form: ['D', 'W', 'L', 'W', 'D'], gf: 1.6, gc: 1.3, xg: 1.55, poss: 54, sot: 5.1, corn: 5.3 },
  juv: { name: 'Juventus', short: 'JUV', color: '#0B0B0B', fg: '#fff', pts: 70, pos: 2, form: ['W', 'D', 'W', 'L', 'W'], gf: 1.8, gc: 0.9, xg: 1.7, poss: 53, sot: 5.6, corn: 5.5 },
  rom: { name: 'Roma', short: 'ROM', color: '#8E1F2F', fg: '#fff', pts: 57, pos: 5, form: ['L', 'W', 'D', 'W', 'W'], gf: 1.7, gc: 1.2, xg: 1.6, poss: 52, sot: 5.2, corn: 5.4 },
}

export const MATCHES: Match[] = [
  { id: 'm1', home: 'bet', away: 'sev', comp: 'LaLiga', league: 'LaLiga · J32', date: 'Hoy · 21:00', venue: 'Benito Villamarín', lk: 'laliga', score: '1 - 0', status: 'live', min: "67'" },
  { id: 'm5', home: 'rma', away: 'bar', comp: 'LaLiga', league: 'LaLiga · J32', date: 'Hoy · 21:00', venue: 'Bernabéu', lk: 'laliga', score: '0 - 0', status: 'sched', min: '21:00' },
  { id: 'm2', home: 'atm', away: 'vil', comp: 'LaLiga', league: 'LaLiga · J32', date: 'Hoy', venue: 'Metropolitano', lk: 'laliga', score: '2 - 1', status: 'fin', min: '' },
  { id: 'm3', home: 'ars', away: 'tot', comp: 'Premier League', league: 'Premier League · J34', date: 'Hoy · 18:30', venue: 'Emirates', lk: 'premier', score: '0 - 0', status: 'sched', min: '18:30' },
  { id: 'm6', home: 'liv', away: 'che', comp: 'Premier League', league: 'Premier League · J34', date: 'Hoy', venue: 'Anfield', lk: 'premier', score: '2 - 1', status: 'fin', min: '' },
  { id: 'm4', home: 'int', away: 'mil', comp: 'Serie A', league: 'Serie A · J35', date: 'Hoy · en juego', venue: 'San Siro', lk: 'seriea', score: '1 - 1', status: 'live', min: "38'" },
  { id: 'm7', home: 'juv', away: 'rom', comp: 'Serie A', league: 'Serie A · J35', date: 'Hoy', venue: 'Allianz Stadium', lk: 'seriea', score: '1 - 1', status: 'fin', min: '' },
]

export const STANDINGS: Record<string, [string, number][]> = {
  laliga: [['Real Madrid', 82], ['Barcelona', 78], ['Atlético', 67], ['Athletic', 60], ['Villarreal', 49], ['Real Betis', 52], ['Girona', 47], ['Sevilla', 41]],
  premier: [['Liverpool', 84], ['Arsenal', 71], ['Man City', 69], ['Aston Villa', 64], ['Tottenham', 48], ['Newcastle', 55], ['Chelsea', 52]],
  seriea: [['Inter', 78], ['Juventus', 70], ['Atalanta', 66], ['Bologna', 58], ['Milan', 54], ['Roma', 57]],
}

export const MARKET_DEFS: MarketDef[] = [
  {
    key: '1x2', title: '1X2', sub: 'Resultado final', featured: true, base: { '1': 2.4, X: 3.3, '2': 2.95 },
    sels: (m) => [
      { k: '1', tag: '1', label: TEAMS[m.home].name },
      { k: 'X', tag: 'X', label: 'Empate' },
      { k: '2', tag: '2', label: TEAMS[m.away].name },
    ],
  },
  {
    key: 'dc', title: 'Doble oportunidad', sub: '1X / 12 / X2', base: { '1X': 1.38, '12': 1.3, X2: 1.55 },
    sels: () => [
      { k: '1X', label: 'Local o empate' },
      { k: '12', label: 'Local o visitante' },
      { k: 'X2', label: 'Empate o visitante' },
    ],
  },
  {
    key: 'ou', title: 'Más / Menos 2.5', sub: 'Total de goles', base: { O: 2.02, U: 1.8 },
    sels: () => [
      { k: 'O', label: 'Más de 2.5' },
      { k: 'U', label: 'Menos de 2.5' },
    ],
  },
  {
    key: 'ah', title: 'Hándicap asiático', sub: 'Línea −0.5', base: { H1: 1.96, H2: 1.86 },
    sels: (m) => [
      { k: 'H1', label: TEAMS[m.home].short + ' −0.5' },
      { k: 'H2', label: TEAMS[m.away].short + ' +0.5' },
    ],
  },
  {
    key: 'btts', title: 'Ambos marcan', sub: 'BTTS', base: { Y: 1.74, N: 2.06 },
    sels: () => [
      { k: 'Y', label: 'Sí' },
      { k: 'N', label: 'No' },
    ],
  },
]

export const SKILL_DEFS: SkillDef[] = [
  { key: 'efe', abbr: 'EFE', name: 'Estabilidad de Formación', desc: 'Consistencia táctica por bloques A–E y alertas.', iconBg: 'var(--accent-soft)', iconColor: 'var(--accent)' },
  { key: 'sad', abbr: 'SAD', name: 'Análisis Pre-Partido', desc: 'Lectura integral del partido y pronóstico.', iconBg: 'var(--up-soft)', iconColor: 'var(--up)' },
  { key: 'tac', abbr: 'DT', name: 'Diagnóstico Táctico', desc: 'Fortalezas, debilidades y plan de juego.', iconBg: 'var(--mark-soft)', iconColor: 'var(--mark)' },
  { key: 'tl', abbr: 'TL', name: 'Timeline', desc: 'Cronología de momentos clave esperados.', iconBg: 'var(--down-soft)', iconColor: 'var(--down)' },
]

export const LEVELS: Level[] = [
  { k: 'elite', label: 'Élite', color: 'var(--lv-elite)', soft: 'rgba(229,72,77,.16)' },
  { k: 'alto', label: 'Alto', color: 'var(--lv-alto)', soft: 'rgba(242,145,61,.16)' },
  { k: 'medio', label: 'Medio', color: 'var(--lv-medio)', soft: 'rgba(242,199,68,.16)' },
  { k: 'bajo', label: 'Bajo', color: 'var(--lv-bajo)', soft: 'rgba(52,199,89,.16)' },
]

export const LINE_COLORS: Record<string, Record<string, string>> = {
  '1x2': { '1': '#5B8DEF', X: '#E6B450', '2': '#2FBE6E' },
  dc: { '1X': '#5B8DEF', '12': '#E6B450', X2: '#2FBE6E' },
  ou: { O: '#5B8DEF', U: '#E6B450' },
  ah: { H1: '#5B8DEF', H2: '#E6B450' },
  btts: { Y: '#5B8DEF', N: '#E6B450' },
}
