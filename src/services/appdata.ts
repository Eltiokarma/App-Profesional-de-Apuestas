// Adaptadores DTO → formas internas de la UI. Las pantallas consumen SIEMPRE
// estas funciones (que hablan el contrato de docs/openapi.yaml vía
// getDataSource()); en modo mock los datos salen del motor local y son
// idénticos a los de antes, en modo http salen del backend real.
import type {
  AnalisisPrepartidoDTO,
  ConstantesDTO,
  EquipoDTO,
  EquipoStatsDTO,
  FixtureDTO,
  PrediccionDTO,
  StandingRowDTO,
} from '../api/types'
import { TEAMS } from '../data'
import type { Match, Team } from '../data/types'
import type { KSnapshot } from '../motor/types'
import { getDataSource, NUM_TEAM, TEAM_NUM } from './datasource'

// ── registro dinámico de equipos ───────────────────────────────────────────
// La estética (color del escudo) y las stats de temporada no viajan en el
// contrato: para equipos desconocidos (modo http) se registra una entrada
// visual con color determinista y stats neutras hasta que exista un endpoint
// /equipos/{id}/stats en el backend.
const PALETTE = ['#5B8DEF', '#2FBE6E', '#E6B450', '#E5484D', '#8E6FE0', '#00954C', '#D9001B', '#132257', '#8E1F2F', '#034694']

function hashCode(s: string): number {
  let h = 0
  for (const c of s) h = (Math.imul(h, 31) + c.charCodeAt(0)) | 0
  return Math.abs(h)
}

/** Garantiza que el equipo del DTO existe en el registro visual; devuelve su clave interna. */
export function ensureTeam(dto: EquipoDTO): string {
  const known = NUM_TEAM[dto.id]
  if (known) return known
  const key = 't' + dto.id
  if (!TEAMS[key]) {
    const neutral: Team = {
      name: dto.nombre,
      short: dto.abreviatura || dto.nombre.slice(0, 3).toUpperCase(),
      color: PALETTE[hashCode(dto.nombre) % PALETTE.length],
      fg: '#fff',
      pts: 50,
      pos: 10,
      form: ['D', 'D', 'D', 'D', 'D'],
      gf: 1.4,
      gc: 1.4,
      xg: 1.4,
      poss: 50,
      sot: 4.5,
      corn: 5,
    }
    TEAMS[key] = neutral
    TEAM_NUM[key] = dto.id
    NUM_TEAM[dto.id] = key
  }
  return key
}

const LK_BY_LIGA_ID: Record<number, string> = { 140: 'laliga', 39: 'premier', 135: 'seriea' }

// ── fixtures ────────────────────────────────────────────────────────────────
export function fixtureToMatch(f: FixtureDTO): Match {
  const home = ensureTeam(f.local)
  const away = ensureTeam(f.visitante)
  const hora = f.fecha.slice(11, 16)
  const live = f.estado === 'en_vivo'
  const fin = f.estado === 'finalizado'
  return {
    id: 'm' + f.id,
    home,
    away,
    comp: f.liga.split(' · ')[0],
    league: f.liga,
    date: live ? 'Hoy · en juego' : fin ? 'Hoy' : `Hoy · ${hora}`,
    venue: f.estadio ?? '',
    lk: LK_BY_LIGA_ID[f.ligaId] ?? String(f.ligaId),
    ligaId: f.ligaId,
    score: f.golesLocal == null ? '0 - 0' : `${f.golesLocal} - ${f.golesVisitante}`,
    status: live ? 'live' : fin ? 'fin' : 'sched',
    min: live ? `${f.minuto ?? ''}'` : fin ? '' : hora,
  }
}

export async function loadMatches(): Promise<Match[]> {
  const fx = await getDataSource().fixtures()
  return fx.map(fixtureToMatch)
}

export const fixtureNum = (matchId: string) => parseInt(matchId.slice(1), 10)

// ── burbujas: constantes + niveles → snapshots del motor ───────────────────
export interface BurbujasData {
  snaps: KSnapshot[]
  level: number
  bin: number
  binLabel: string
}

function constantesToSnap(c: ConstantesDTO, idx: number): KSnapshot {
  const rivalKey =
    NUM_TEAM[c.rivalId] ??
    ensureTeam({ id: c.rivalId, nombre: c.rivalNombre, abreviatura: c.rivalNombre.slice(0, 3).toUpperCase() })
  return {
    fixtureId: c.fixtureId,
    t: idx,
    rival: rivalKey,
    isLocal: c.condicion === 'Local',
    gf: c.golesFavor,
    ga: c.golesContra,
    rivalLevel: c.nivelRival,
    q: { ...c.q },
    k: {
      pos: c.k.positivo,
      neg: c.k.negativo,
      posLocal: c.k.positivoLocal,
      negLocal: c.k.negativoLocal,
      posVisita: c.k.positivoVisita,
      negVisita: c.k.negativoVisita,
      gA: c.k.golesAnotado,
      gR: c.k.golesRecibido,
      gLA: c.k.golesLocalAnotado,
      gLR: c.k.golesLocalRecibido,
      gVA: c.k.golesVisitaAnotado,
      gVR: c.k.golesVisitaRecibido,
      dc: c.k.dc,
      dcLocal: c.k.dcLocal,
      dcVisita: c.k.dcVisita,
    },
    esInternacional: c.esInternacional,
    fused: { ...c.fusion },
  }
}

export async function loadBurbujas(teamKey: string): Promise<BurbujasData | null> {
  const equipoId = TEAM_NUM[teamKey]
  if (equipoId == null) return null
  const ds = getDataSource()
  const [constantes, niveles] = await Promise.all([ds.constantes(equipoId, 50), ds.niveles(equipoId, 1)])
  const snaps = constantes
    .slice()
    .reverse() // el contrato entrega desc por fecha; la UI trabaja cronológico
    .map((c, i) => constantesToSnap(c, i))
  const nv = niveles[0]
  return {
    snaps,
    level: nv ? nv.nivel : 0.5,
    bin: nv ? nv.bin : 0,
    binLabel: nv ? nv.binEtiqueta : 'Sin datos',
  }
}

// ── cuotas: tabla base { mercado → { selección → cuota } } ──────────────────
export type OddsTable = Record<string, Record<string, number>>

export async function loadCuotasBase(matchId: string): Promise<OddsTable> {
  const rows = await getDataSource().cuotas(fixtureNum(matchId))
  const out: OddsTable = {}
  for (const r of rows) {
    ;(out[r.mercado] = out[r.mercado] ?? {})[r.seleccion] = r.cuota
  }
  return out
}

// ── predicción (§5) y análisis pre-partido ──────────────────────────────────
export function loadPrediccion(matchId: string): Promise<PrediccionDTO> {
  return getDataSource().prediccion(fixtureNum(matchId))
}

export function loadAnalisis(matchId: string): Promise<AnalisisPrepartidoDTO> {
  return getDataSource().analisisPrepartido(fixtureNum(matchId))
}

// ── buscador de equipos y página de equipo ──────────────────────────────────
export async function searchTeams(q: string): Promise<EquipoDTO[]> {
  return getDataSource().buscarEquipos(q)
}

/** Historia de fixtures de un equipo mapeada a Match internos. */
export async function loadTeamFixtures(teamKey: string): Promise<Match[]> {
  const equipoId = TEAM_NUM[teamKey]
  if (equipoId == null) return []
  const fx = await getDataSource().fixtures({ equipoId, limit: 60 })
  return fx.map(fixtureToMatch)
}

export async function loadTeamStats(teamKey: string): Promise<EquipoStatsDTO | null> {
  const equipoId = TEAM_NUM[teamKey]
  if (equipoId == null) return null
  return getDataSource().equipoStats(equipoId)
}

// ── estadísticas de temporada + tabla de posiciones ─────────────────────────
export interface EstadisticasData {
  home: EquipoStatsDTO
  away: EquipoStatsDTO
  tabla: StandingRowDTO[]
}

export async function loadEstadisticas(m: Match): Promise<EstadisticasData> {
  const ds = getDataSource()
  const homeId = TEAM_NUM[m.home]
  const awayId = TEAM_NUM[m.away]
  const [home, away, tabla] = await Promise.all([
    ds.equipoStats(homeId),
    ds.equipoStats(awayId),
    m.ligaId != null ? ds.standings(m.ligaId) : Promise.resolve([]),
  ])
  return { home, away, tabla }
}
