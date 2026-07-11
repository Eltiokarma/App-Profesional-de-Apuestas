// Adaptadores DTO → formas internas de la UI. Las pantallas consumen SIEMPRE
// estas funciones (que hablan el contrato de docs/openapi.yaml vía
// getDataSource()); en modo mock los datos salen del motor local y son
// idénticos a los de antes, en modo http salen del backend real.
import type {
  AnalisisPrepartidoDTO,
  ConstanteCuotaDTO,
  ConstantesDTO,
  EquipoDTO,
  EquipoStatsDTO,
  FixtureDTO,
  FixtureLiveDTO,
  LigaDTO,
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
  if (known) {
    if (dto.logo && !TEAMS[known].logo) TEAMS[known].logo = dto.logo
    return known
  }
  const key = 't' + dto.id
  if (!TEAMS[key]) {
    const neutral: Team = {
      name: dto.nombre,
      short: dto.abreviatura || dto.nombre.slice(0, 3).toUpperCase(),
      color: PALETTE[hashCode(dto.nombre) % PALETTE.length],
      fg: '#fff',
      logo: dto.logo ?? null,
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
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
const pad2 = (n: number) => String(n).padStart(2, '0')

/** Etiqueta relativa del día en hora local: Hoy / Ayer / Mañana / "5 jul" / "5 jul 2025". */
export function etiquetaFecha(d: Date, hoy = new Date()): string {
  const dias = Math.round(
    (new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() -
      new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate()).getTime()) /
      86_400_000,
  )
  if (dias === 0) return 'Hoy'
  if (dias === -1) return 'Ayer'
  if (dias === 1) return 'Mañana'
  const base = `${d.getDate()} ${MESES[d.getMonth()]}`
  return d.getFullYear() === hoy.getFullYear() ? base : `${base} ${d.getFullYear()}`
}

export function fixtureToMatch(f: FixtureDTO): Match {
  const home = ensureTeam(f.local)
  const away = ensureTeam(f.visitante)
  // el contrato entrega fecha ISO-8601 UTC (Z); la UI muestra hora local
  const fecha = new Date(f.fecha)
  const hora = `${pad2(fecha.getHours())}:${pad2(fecha.getMinutes())}`
  const dia = etiquetaFecha(fecha)
  const live = f.estado === 'en_vivo'
  const fin = f.estado === 'finalizado'
  return {
    id: 'm' + f.id,
    home,
    away,
    comp: f.liga.split(' · ')[0],
    league: f.liga,
    date: live ? `${dia} · en juego` : fin ? dia : `${dia} · ${hora}`,
    venue: f.estadio ?? '',
    lk: LK_BY_LIGA_ID[f.ligaId] ?? String(f.ligaId),
    ligaId: f.ligaId,
    ligaLogo: f.ligaLogo ?? null,
    ligaBandera: f.ligaBandera ?? null,
    // finalizado sin goles = walkover/adjudicado (AWD/WO): no inventar un 0-0
    score: f.golesLocal == null || f.golesVisitante == null ? (fin ? '—' : '0 - 0') : `${f.golesLocal} - ${f.golesVisitante}`,
    status: live ? 'live' : fin ? 'fin' : 'sched',
    min: live ? `${f.minuto ?? ''}'` : fin ? '' : hora,
  }
}

const localDateStr = (d: Date) => `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`

/** Partidos de un día LOCAL (yyyy-mm-dd) en orden cronológico.
 *  El backend filtra por día UTC, así que un día local abarca dos días UTC
 *  (p. ej. en UTC-5 un partido a las 21:00 cae en el día UTC siguiente):
 *  se pide también el día vecino y se recorta por fecha local. */
export async function loadMatches(fecha: string): Promise<Match[]> {
  const ds = getDataSource()
  const base = new Date(fecha + 'T12:00:00')
  const offMin = base.getTimezoneOffset() // >0 al oeste de UTC, <0 al este
  const pedidos = [ds.fixtures({ fecha, limit: 200 })]
  if (offMin !== 0) {
    const vecino = new Date(base)
    vecino.setDate(base.getDate() + (offMin > 0 ? 1 : -1))
    pedidos.push(ds.fixtures({ fecha: localDateStr(vecino), limit: 200 }))
  }
  const lotes = await Promise.all(pedidos)
  const vistos = new Set<number>()
  return lotes
    .flat()
    .filter((f) => !vistos.has(f.id) && vistos.add(f.id) && localDateStr(new Date(f.fecha)) === fecha)
    .sort((a, b) => a.fecha.localeCompare(b.fecha))
    .map(fixtureToMatch)
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
      vic1: c.k.vic1, vic1Local: c.k.vic1Local, vic1Visita: c.k.vic1Visita,
      vic2: c.k.vic2, vic2Local: c.k.vic2Local, vic2Visita: c.k.vic2Visita,
      vic3: c.k.vic3, vic3Local: c.k.vic3Local, vic3Visita: c.k.vic3Visita,
      der1: c.k.der1, der1Local: c.k.der1Local, der1Visita: c.k.der1Visita,
      der2: c.k.der2, der2Local: c.k.der2Local, der2Visita: c.k.der2Visita,
      der3: c.k.der3, der3Local: c.k.der3Local, der3Visita: c.k.der3Visita,
    },
    esInternacional: c.esInternacional,
    fused: { ...c.fusion },
  }
}

export async function loadBurbujas(teamKey: string): Promise<BurbujasData | null> {
  const equipoId = TEAM_NUM[teamKey]
  if (equipoId == null) return null
  const ds = getDataSource()
  // 500 = tope del contrato; cubre la historia completa de prácticamente todos
  // los equipos. La ventana visible (20/50/Todo) se recorta luego en la gráfica.
  const [constantes, niveles] = await Promise.all([ds.constantes(equipoId, 500), ds.niveles(equipoId, 1)])
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

/** k_cuota (§3.8): rachas de suma de cuota 1X2 (solo 2026, datos reales). */
export async function loadConstantesCuota(teamKey: string): Promise<ConstanteCuotaDTO[]> {
  const equipoId = TEAM_NUM[teamKey]
  if (equipoId == null) return []
  return getDataSource().constantesCuota(equipoId)
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

/** Comparador { mercado → { selección → [{casa, cuota, mejor}] cuota desc } }.
 *  La diferencia de decimales entre casas dice dónde paga más ese acierto.
 *  Falla suave: sin datos devuelve {} y la sección no se pinta. */
export interface CuotaCasaUI {
  casa: string
  cuota: number
  mejor: boolean
}
export type OddsCasasTable = Record<string, Record<string, CuotaCasaUI[]>>

export async function loadCuotasCasas(matchId: string): Promise<OddsCasasTable> {
  const out: OddsCasasTable = {}
  try {
    const rows = await getDataSource().cuotasCasas(fixtureNum(matchId))
    for (const r of rows) {
      const mk = (out[r.mercado] = out[r.mercado] ?? {})
      ;(mk[r.seleccion] = mk[r.seleccion] ?? []).push({ casa: r.casa, cuota: r.cuota, mejor: r.mejor })
    }
  } catch {
    /* opcional para pintar: los errores reales ya los reporta /cuotas */
  }
  return out
}

/** Historial prepartido { mercado → { selección → [cuotas asc por captura] } }.
 *  Falla suave: sin historial (DB vieja o error) devuelve {} y la gráfica cae
 *  a la deriva sintética de siempre. */
export type OddsHistTable = Record<string, Record<string, number[]>>

export async function loadCuotasHistorial(matchId: string): Promise<OddsHistTable> {
  const out: OddsHistTable = {}
  try {
    const rows = await getDataSource().cuotasHistorial(fixtureNum(matchId))
    for (const r of rows) {
      const mk = (out[r.mercado] = out[r.mercado] ?? {})
      ;(mk[r.seleccion] = mk[r.seleccion] ?? []).push(r.cuota)
    }
  } catch {
    /* opcional para pintar: los errores reales ya los reporta /cuotas */
  }
  return out
}

/** En vivo real (fase 3): marcador, minuto y cuotas en juego del backend. */
export function loadFixtureLive(matchId: string): Promise<FixtureLiveDTO> {
  return getDataSource().fixtureLive(fixtureNum(matchId))
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

// ── próximos partidos con nivel del rival (card de Burbujas) ────────────────
export interface ProximoRival {
  fecha: string // dd/mm
  rivalNombre: string
  bin: number
  binEtiqueta: string
}

export async function loadProximos(teamKey: string, n = 3): Promise<ProximoRival[]> {
  const equipoId = TEAM_NUM[teamKey]
  if (equipoId == null) return []
  const ds = getDataSource()
  // desde hoy y asc: excluye programados con fecha pasada (aplazados sin jugar)
  const prox = await ds.fixtures({ equipoId, estado: 'programado', desde: localDateStr(new Date()), orden: 'asc', limit: n })
  return Promise.all(
    prox.map(async (f) => {
      const rival = f.local.id === equipoId ? f.visitante : f.local
      const nv = (await ds.niveles(rival.id, 1))[0]
      const d = new Date(f.fecha)
      return {
        fecha: `${pad2(d.getDate())}/${pad2(d.getMonth() + 1)}`,
        rivalNombre: rival.nombre,
        bin: nv ? nv.bin : 0,
        binEtiqueta: nv ? nv.binEtiqueta : 'Sin datos',
      }
    }),
  )
}

// ── enfrentamientos directos (card H2H de Estadísticas) ─────────────────────
export interface H2HData {
  home: number
  draw: number
  away: number
  last: { when: string; match: string; score: string; color: string }[]
}

/** H2H real vía /fixtures?equipoId&rivalId; contadores desde la perspectiva
 *  del local del partido actual. null si algún equipo no está en el contrato. */
export async function loadH2H(m: Match): Promise<H2HData | null> {
  const homeId = TEAM_NUM[m.home]
  const awayId = TEAM_NUM[m.away]
  if (homeId == null || awayId == null) return null
  const fx = await getDataSource().fixtures({ equipoId: homeId, rivalId: awayId, estado: 'finalizado', limit: 12 })
  // finalizado sin goles = walkover/adjudicado: fuera del H2H (mismo criterio que fixtureToMatch)
  const jugados = fx.filter((f) => f.golesLocal != null && f.golesVisitante != null).slice(0, 6)
  const out: H2HData = { home: 0, draw: 0, away: 0, last: [] }
  for (const f of jugados) {
    const gHome = f.local.id === homeId ? f.golesLocal! : f.golesVisitante!
    const gAway = f.local.id === homeId ? f.golesVisitante! : f.golesLocal!
    if (gHome > gAway) out.home++
    else if (gHome < gAway) out.away++
    else out.draw++
    const d = new Date(f.fecha)
    out.last.push({
      when: `${d.getDate()} ${MESES[d.getMonth()]} ${String(d.getFullYear()).slice(2)}`,
      match: `${f.local.abreviatura} vs ${f.visitante.abreviatura}`,
      score: `${f.golesLocal} - ${f.golesVisitante}`,
      color: gHome > gAway ? 'var(--up)' : gHome < gAway ? 'var(--down)' : 'var(--t2)',
    })
  }
  return out
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

// ── página de liga: metadatos + clasificación + partidos ────────────────────
export interface LigaData {
  meta: LigaDTO | null
  tabla: StandingRowDTO[]
  proximos: Match[]
  recientes: Match[]
}

/** `temporada` opcional: sin ella, la más reciente (una pasada no tendrá próximos). */
export async function loadLiga(ligaId: number, temporada?: number): Promise<LigaData> {
  const ds = getDataSource()
  const hoy = localDateStr(new Date())
  const [meta, tabla, prog, fin] = await Promise.all([
    ds.liga(ligaId).catch(() => null), // liga sin metadatos (404) no bloquea la página
    ds.standings(ligaId, temporada),
    ds.fixtures({ ligaId, temporada, estado: 'programado', desde: hoy, orden: 'asc', limit: 10 }),
    ds.fixtures({ ligaId, temporada, estado: 'finalizado', limit: 10 }),
  ])
  return {
    meta,
    tabla,
    proximos: prog.map(fixtureToMatch),
    recientes: fin.map(fixtureToMatch), // el contrato entrega desc: más reciente primero
  }
}
