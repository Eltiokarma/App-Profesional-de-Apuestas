// Fuente de datos conmutable: la app habla SIEMPRE el contrato de docs/openapi.yaml.
// - MockDataSource: el motor local (src/motor) sirviendo ese contrato (demo, default).
// - HttpDataSource: el backend FastAPI real (VITE_DATA_SOURCE=http).
// Migrar una pantalla a datos reales = consumirla vía getDataSource(); nada más.
import { SadApi } from '../api/sad'
import type {
  AnalisisPrepartidoDTO,
  ConstanteCuotaDTO,
  ConstantesDTO,
  CuotaCasaDTO,
  CuotaDTO,
  CuotaLiveDTO,
  CuotaSnapshotDTO,
  EquipoDTO,
  EventoLiveDTO,
  EquipoStatsDTO,
  EstadoFixture,
  FixtureDTO,
  FixtureLiveDTO,
  GapEquipoDTO,
  LigaDTO,
  NivelDTO,
  PrediccionDTO,
  PuntoLiveDTO,
  StandingRowDTO,
} from '../api/types'
import { CONFIG, type DataSourceMode } from '../config'
import { MARKET_DEFS, MATCHES, STANDINGS, TEAMS } from '../data'
import { oddsFor, rng } from '../lib/odds'
import { levelBin } from '../motor/discretizer'
import { teamEngine } from '../motor/engine'
import { leagueOf } from '../motor/history'
import { gapDiff, gapFor } from '../motor/regression'
import type { KSnapshot } from '../motor/types'

export interface FeedHealth {
  ok: boolean
  latencyMs: number | null
  detail: string
}

/** Filtros de /fixtures del contrato (docs/openapi.yaml). */
export interface FixturesParams {
  fecha?: string
  /** Solo fixtures con fecha >= desde (yyyy-mm-dd). */
  desde?: string
  estado?: EstadoFixture
  /** Orden por fecha (default desc). */
  orden?: 'asc' | 'desc'
  ligaId?: number
  /** Solo fixtures de esta temporada de la liga. */
  temporada?: number
  equipoId?: number
  /** Con equipoId: solo enfrentamientos directos entre ambos (H2H). */
  rivalId?: number
  limit?: number
}

export interface SadDataSource {
  readonly mode: DataSourceMode
  health(): Promise<FeedHealth>
  fixtures(params?: FixturesParams): Promise<FixtureDTO[]>
  /** En vivo real: marcador, minuto y cuotas en juego (vacías sin cobertura). */
  fixtureLive(fixtureId: number): Promise<FixtureLiveDTO>
  buscarEquipos(buscar: string, limit?: number): Promise<EquipoDTO[]>
  niveles(equipoId: number, limit?: number): Promise<NivelDTO[]>
  constantes(equipoId: number, limit?: number): Promise<ConstantesDTO[]>
  /** k_cuota (§3.8): solo datos reales; en mock devuelve []. */
  constantesCuota(equipoId: number): Promise<ConstanteCuotaDTO[]>
  prediccion(fixtureId: number): Promise<PrediccionDTO>
  analisisPrepartido(fixtureId: number): Promise<AnalisisPrepartidoDTO>
  cuotas(fixtureId: number): Promise<CuotaDTO[]>
  /** Cuota de cada casa por selección, la mejor marcada (orden cuota desc). */
  cuotasCasas(fixtureId: number): Promise<CuotaCasaDTO[]>
  /** Snapshots prepartido de la ingesta (asc por captura; [] si aún no hay).
   *  Sin `casa`: media; con `casa`: el crudo de esa casa de referencia. */
  cuotasHistorial(fixtureId: number, casa?: string | null): Promise<CuotaSnapshotDTO[]>
  /** Casas de referencia con historial propio para el fixture. */
  cuotasHistorialFuentes(fixtureId: number): Promise<string[]>
  equipoStats(equipoId: number): Promise<EquipoStatsDTO>
  liga(ligaId: number): Promise<LigaDTO>
  standings(ligaId: number, temporada?: number): Promise<StandingRowDTO[]>
}

// ---------- mapeo de ids internos (strings) ↔ contrato (números) ----------
const TEAM_KEYS = Object.keys(TEAMS)
export const TEAM_NUM: Record<string, number> = Object.fromEntries(TEAM_KEYS.map((k, i) => [k, 100 + i]))
export const NUM_TEAM: Record<number, string> = Object.fromEntries(TEAM_KEYS.map((k, i) => [100 + i, k]))
export const FIXTURE_NUM = (matchId: string) => parseInt(matchId.slice(1), 10)

const LIGA_NUM: Record<string, number> = { laliga: 140, premier: 39, seriea: 135 }
const LK_BY_NUM: Record<number, string> = Object.fromEntries(Object.entries(LIGA_NUM).map(([lk, n]) => [n, lk]))

// metadatos demo de las ligas mock (mismo CDN que el backend real)
const LIGA_META: Record<number, LigaDTO> = {
  140: { id: 140, nombre: 'LaLiga', pais: 'Spain', logo: 'https://media.api-sports.io/football/leagues/140.png', bandera: 'https://media.api-sports.io/flags/es.svg', temporada: 2026, temporadas: [2026] },
  39: { id: 39, nombre: 'Premier League', pais: 'England', logo: 'https://media.api-sports.io/football/leagues/39.png', bandera: 'https://media.api-sports.io/flags/gb-eng.svg', temporada: 2026, temporadas: [2026] },
  135: { id: 135, nombre: 'Serie A', pais: 'Italy', logo: 'https://media.api-sports.io/football/leagues/135.png', bandera: 'https://media.api-sports.io/flags/it.svg', temporada: 2026, temporadas: [2026] },
}

// fecha sintética determinista para el historial del motor (t = jornada)
const tToIso = (t: number) => {
  const d = new Date(Date.UTC(2025, 7, 1) + t * 4 * 86_400_000)
  return d.toISOString()
}
const MOCK_NOW = '2026-07-02T21:00:00.000Z'

function equipoDTO(key: string) {
  const T = TEAMS[key]
  return { id: TEAM_NUM[key], nombre: T.name, abreviatura: T.short, logo: T.logo ?? null }
}

function nivelDTO(teamKey: string): NivelDTO {
  const eng = teamEngine(teamKey)!
  const last = eng.levels[eng.levels.length - 1]
  return {
    equipoId: TEAM_NUM[teamKey],
    fixtureId: last ? last.fixtureId : 0,
    fecha: tToIso(last ? last.t : 0),
    nivel: eng.level,
    bin: eng.bin,
    binEtiqueta: eng.binLabel,
  }
}

function constantesDTO(teamKey: string, s: KSnapshot): ConstantesDTO {
  const lk = leagueOf(teamKey)
  return {
    equipoId: TEAM_NUM[teamKey],
    fixtureId: s.fixtureId,
    fecha: tToIso(s.t),
    condicion: s.isLocal ? 'Local' : 'Visita',
    rivalId: TEAM_NUM[s.rival],
    rivalNombre: TEAMS[s.rival].name,
    nivelRival: s.rivalLevel,
    golesFavor: s.gf,
    golesContra: s.ga,
    ligaId: s.esInternacional ? 2 : (lk ? LIGA_NUM[lk] : 0),
    esInternacional: !!s.esInternacional,
    q: {
      local: s.q.local,
      visita: s.q.visita,
      negativo: s.q.negativo,
      golesAnotado: s.q.golesAnotado,
      golesRecibido: s.q.golesRecibido,
      dc: s.q.dc,
    },
    k: {
      positivo: s.k.pos,
      negativo: s.k.neg,
      positivoLocal: s.k.posLocal,
      negativoLocal: s.k.negLocal,
      positivoVisita: s.k.posVisita,
      negativoVisita: s.k.negVisita,
      golesAnotado: s.k.gA,
      golesRecibido: s.k.gR,
      golesLocalAnotado: s.k.gLA,
      golesLocalRecibido: s.k.gLR,
      golesVisitaAnotado: s.k.gVA,
      golesVisitaRecibido: s.k.gVR,
      dc: s.k.dc,
      dcLocal: s.k.dcLocal,
      dcVisita: s.k.dcVisita,
      vic1: s.k.vic1, vic1Local: s.k.vic1Local, vic1Visita: s.k.vic1Visita,
      vic2: s.k.vic2, vic2Local: s.k.vic2Local, vic2Visita: s.k.vic2Visita,
      vic3: s.k.vic3, vic3Local: s.k.vic3Local, vic3Visita: s.k.vic3Visita,
      der1: s.k.der1, der1Local: s.k.der1Local, der1Visita: s.k.der1Visita,
      der2: s.k.der2, der2Local: s.k.der2Local, der2Visita: s.k.der2Visita,
      der3: s.k.der3, der3Local: s.k.der3Local, der3Visita: s.k.der3Visita,
    },
    fusion: { ...s.fused },
  }
}

function gapEquipoDTO(teamKey: string): GapEquipoDTO {
  const g = gapFor(teamKey)!
  return { equipoId: TEAM_NUM[teamKey], ...g }
}

class MockDataSource implements SadDataSource {
  readonly mode = 'mock' as const

  async health(): Promise<FeedHealth> {
    return { ok: true, latencyMs: null, detail: 'motor local (demo)' }
  }

  async buscarEquipos(buscar: string, limit = 10) {
    const norm = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    const q = norm(buscar)
    if (q.length < 2) return []
    return TEAM_KEYS.map((k) => ({ k, n: norm(TEAMS[k].name) }))
      .filter((e) => e.n.includes(q))
      .map((e) => ({
        rank: e.n.startsWith(q) ? 0 : e.n.split(' ').some((w) => w.startsWith(q)) ? 1 : 2,
        dto: equipoDTO(e.k),
      }))
      .sort((a, b) => a.rank - b.rank || a.dto.nombre.length - b.dto.nombre.length)
      .slice(0, Math.min(Math.max(limit, 1), 25)) // mismo tope que el backend
      .map((e) => e.dto)
  }

  async fixtures(params: FixturesParams = {}): Promise<FixtureDTO[]> {
    const teamKey = params.equipoId != null ? NUM_TEAM[params.equipoId] : undefined
    const rivalKey = params.rivalId != null ? NUM_TEAM[params.rivalId] : undefined
    // los partidos demo viven en el día de hoy (hora local) para que la
    // barra de fechas funcione igual que con el backend real
    const hoy = new Date()
    const hoyStr = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
    if (params.fecha && params.fecha !== hoyStr) return []
    const estadoDe = (m: (typeof MATCHES)[number]): EstadoFixture =>
      m.status === 'live' ? 'en_vivo' : m.status === 'fin' ? 'finalizado' : 'programado'
    return MATCHES.filter(
      (m) =>
        (!teamKey || m.home === teamKey || m.away === teamKey) &&
        (!teamKey || !rivalKey || (m.home === teamKey && m.away === rivalKey) || (m.home === rivalKey && m.away === teamKey)) &&
        (!params.estado || estadoDe(m) === params.estado) &&
        (params.ligaId == null || (LIGA_NUM[m.lk] ?? 0) === params.ligaId) &&
        (params.temporada == null || params.temporada === 2026), // la demo solo tiene la 2026
    )
      .map((m) => {
        const goles = (m.score || '0 - 0').split('-').map((x) => parseInt(x.trim()) || 0)
        const enJuego = m.status === 'live'
        const hora = m.status === 'sched' && /^\d{2}:\d{2}$/.test(m.min) ? m.min : '21:00'
        const [hh, mm] = hora.split(':').map(Number)
        return {
          id: FIXTURE_NUM(m.id),
          fecha: new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate(), hh, mm).toISOString(),
          ligaId: LIGA_NUM[m.lk] ?? 0,
          liga: m.league,
          temporada: 2026,
          estado: estadoDe(m),
          minuto: enJuego ? parseInt(m.min) || null : null,
          estadio: m.venue,
          local: equipoDTO(m.home),
          visitante: equipoDTO(m.away),
          golesLocal: m.status === 'sched' ? null : goles[0],
          golesVisitante: m.status === 'sched' ? null : goles[1],
          ligaLogo: LIGA_META[LIGA_NUM[m.lk] ?? 0]?.logo ?? null,
          ligaBandera: LIGA_META[LIGA_NUM[m.lk] ?? 0]?.bandera ?? null,
          ligaPais: LIGA_META[LIGA_NUM[m.lk] ?? 0]?.pais ?? null,
        }
      })
      .filter((f) => !params.desde || f.fecha >= new Date(params.desde + 'T00:00:00').toISOString())
      .sort((a, b) => (params.orden === 'asc' ? a.fecha.localeCompare(b.fecha) : b.fecha.localeCompare(a.fecha)))
      .slice(0, Math.min(Math.max(params.limit ?? 50, 1), 200)) // mismo tope que el backend
  }

  async niveles(equipoId: number, limit = 50): Promise<NivelDTO[]> {
    const key = NUM_TEAM[equipoId]
    const eng = key ? teamEngine(key) : null
    if (!eng) return []
    return eng.levels
      .slice(-limit)
      .reverse()
      .map((r) => {
        const { bin, label } = levelBin(r.level)
        return { equipoId, fixtureId: r.fixtureId, fecha: tToIso(r.t), nivel: r.level, bin, binEtiqueta: label }
      })
  }

  async constantes(equipoId: number, limit = 50): Promise<ConstantesDTO[]> {
    const key = NUM_TEAM[equipoId]
    const eng = key ? teamEngine(key) : null
    if (!eng) return []
    return eng.snaps
      .slice(-limit)
      .reverse()
      .map((s) => constantesDTO(key, s))
  }

  async constantesCuota(): Promise<ConstanteCuotaDTO[]> {
    return [] // el motor demo no tiene cuotas históricas: k_cuota solo con datos reales
  }

  async prediccion(fixtureId: number): Promise<PrediccionDTO> {
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) throw new Error(`fixture ${fixtureId} no existe`)
    return {
      fixtureId,
      local: gapEquipoDTO(m.home),
      visitante: gapEquipoDTO(m.away),
      gapDiff: gapDiff(m.home, m.away),
      generadoEn: MOCK_NOW,
    }
  }

  async analisisPrepartido(fixtureId: number): Promise<AnalisisPrepartidoDTO> {
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) throw new Error(`fixture ${fixtureId} no existe`)
    const engH = teamEngine(m.home)!
    const engA = teamEngine(m.away)!
    const pred = await this.prediccion(fixtureId)
    const dir = (g: GapEquipoDTO) => (g.tendencia === 'mejora' ? 'tiende a mejorar' : g.tendencia === 'empeora' ? 'tiende a empeorar' : 'en equilibrio')
    return {
      fixtureId,
      niveles: { local: nivelDTO(m.home), visitante: nivelDTO(m.away) },
      constantes: {
        local: engH.snaps.length ? constantesDTO(m.home, engH.snaps[engH.snaps.length - 1]) : null,
        visitante: engA.snaps.length ? constantesDTO(m.away, engA.snaps[engA.snaps.length - 1]) : null,
      },
      prediccion: pred,
      resumen:
        `${TEAMS[m.home].name} (nivel ${engH.level.toFixed(2)}, ${engH.binLabel}) recibe a ` +
        `${TEAMS[m.away].name} (nivel ${engA.level.toFixed(2)}, ${engA.binLabel}). ` +
        `Regresión al nivel: local ${dir(pred.local)}, visitante ${dir(pred.visitante)}.`,
    }
  }

  async cuotas(fixtureId: number): Promise<CuotaDTO[]> {
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) return []
    const table = oddsFor(m.id)
    const out: CuotaDTO[] = []
    for (const def of MARKET_DEFS) {
      for (const k in table[def.key]) {
        out.push({ fixtureId, mercado: def.key, seleccion: k, cuota: table[def.key][k], actualizadoEn: MOCK_NOW })
      }
    }
    return out
  }

  async fixtureLive(fixtureId: number): Promise<FixtureLiveDTO> {
    // Demo: serie 1X2 determinista del segundo tiempo, con una suspendida al
    // final — misma forma que sirve el backend real desde odds_live.
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) throw new Error(`fixture ${fixtureId} no existe`)
    const estado = m.status === 'live' ? 'en_vivo' : m.status === 'fin' ? 'finalizado' : 'programado'
    const p = (m.score || '0 - 0').split('-').map((x) => parseInt(x.trim()) || 0)
    if (estado !== 'en_vivo') {
      return { fixtureId, estado, minuto: null, golesLocal: p[0] ?? null, golesVisitante: p[1] ?? null, cuotas: [], serie: [], eventos: [], actualizadoEn: null }
    }
    const minuto = parseInt(m.min) || 63
    const r = rng(m.id + '|live')
    const BASES: [string, number][] = [['1', 1.65], ['X', 3.9], ['2', 5.2]]
    const serie: PuntoLiveDTO[] = []
    for (let min = 46; min <= minuto; min += 3) {
      for (const [sel, base] of BASES) {
        serie.push({ minuto: min, mercado: '1x2', seleccion: sel, cuota: Math.round(base * (0.94 + r() * 0.12) * 100) / 100 })
      }
    }
    const ultimos = serie.slice(-BASES.length)
    const cuotas: CuotaLiveDTO[] = ultimos.map((pt, i) => ({
      mercado: pt.mercado, seleccion: pt.seleccion, cuota: pt.cuota, suspendida: i === BASES.length - 1,
    }))
    const eventos: EventoLiveDTO[] = [
      { minuto: 23, tipo: 'amarilla', equipoId: null, jugador: 'J. Demo', detalle: 'Yellow Card' },
      { minuto: 49, tipo: 'gol', equipoId: null, jugador: 'L. Demo', detalle: 'Normal Goal' },
    ]
    return { fixtureId, estado, minuto, golesLocal: p[0] ?? null, golesVisitante: p[1] ?? null, cuotas, serie, eventos, actualizadoEn: MOCK_NOW }
  }

  async cuotasCasas(fixtureId: number): Promise<CuotaCasaDTO[]> {
    // Demo: 6 casas deterministas alrededor de la cuota base — misma forma
    // (y mismo orden cuota desc + mejor marcada) que el backend real.
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) return []
    const table = oddsFor(m.id)
    const CASAS: [number, string][] = [[8, 'Bet365'], [11, '1xBet'], [32, 'Pinnacle'], [2, 'Betfair'], [6, 'Bwin'], [16, 'William Hill']]
    const out: CuotaCasaDTO[] = []
    for (const def of MARKET_DEFS) {
      for (const k in table[def.key]) {
        const base = table[def.key][k]
        const r = rng(m.id + '|' + def.key + '|' + k + '|casas')
        const filas = CASAS.map(([casaId, casa]) => ({
          fixtureId, mercado: def.key, seleccion: k, casaId, casa,
          cuota: Math.max(1.04, Math.round(base * (0.95 + r() * 0.1) * 100) / 100),
          mejor: false,
        })).sort((a, b) => b.cuota - a.cuota)
        for (const f of filas) f.mejor = f.cuota >= filas[0].cuota - 1e-9
        out.push(...filas)
      }
    }
    return out
  }

  async cuotasHistorialFuentes(): Promise<string[]> {
    return ['1xBet', 'Bet365', 'Betano', 'Pinnacle']
  }

  async cuotasHistorial(fixtureId: number, casa?: string | null): Promise<CuotaSnapshotDTO[]> {
    // Demo: 6 snapshots deterministas que derivan hacia la cuota base — misma
    // forma que servirá el backend real desde odds_history. Con `casa`, otra
    // semilla: cada fuente tiene su propio movimiento.
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) return []
    const table = oddsFor(m.id)
    const N = 6
    const t0 = new Date(MOCK_NOW).getTime() - (N - 1) * 6 * 3600_000
    const out: CuotaSnapshotDTO[] = []
    for (const def of MARKET_DEFS) {
      for (const k in table[def.key]) {
        const base = table[def.key][k]
        const r = rng(m.id + '|' + def.key + '|' + k + '|hist' + (casa ? '|' + casa : ''))
        const inicio = base * (0.92 + r() * 0.16)
        for (let i = 0; i < N; i++) {
          const f = i / (N - 1)
          const v = i === N - 1 ? base : inicio * (1 - f) + base * f + (r() - 0.5) * 0.04 * base
          out.push({
            fixtureId, mercado: def.key, seleccion: k,
            cuota: Math.max(1.04, Math.round(v * 100) / 100),
            casas: 12,
            capturadoEn: new Date(t0 + i * 6 * 3600_000).toISOString(),
          })
        }
      }
    }
    // asc por captura, como el backend real
    return out.sort((a, b) => a.capturadoEn.localeCompare(b.capturadoEn))
  }

  async equipoStats(equipoId: number): Promise<EquipoStatsDTO> {
    const key = NUM_TEAM[equipoId]
    const T = key ? TEAMS[key] : undefined
    if (!T) throw new Error(`equipo ${equipoId} no existe`)
    return {
      equipoId,
      nombre: T.name,
      partidosJugados: 38,
      puntos: T.pts,
      forma: T.form,
      golesFavorProm: T.gf,
      golesContraProm: T.gc,
      // igual que el backend v0: los promedios avanzados aún no se derivan
      xgProm: null,
      posesionProm: null,
      tirosPuertaProm: null,
      cornersProm: null,
    }
  }

  async liga(ligaId: number): Promise<LigaDTO> {
    const meta = LIGA_META[ligaId]
    if (!meta) throw new Error(`liga ${ligaId} no existe`)
    return meta
  }

  async standings(ligaId: number, temporada?: number): Promise<StandingRowDTO[]> {
    if (temporada != null && temporada !== 2026) return [] // la demo solo tiene la 2026
    const lk = LK_BY_NUM[ligaId]
    const rows = (lk && STANDINGS[lk]) || []
    const keyByName = (name: string) => TEAM_KEYS.find((k) => TEAMS[k].name === name)
    return rows
      .map(([nombre, puntos]) => ({ nombre, puntos }))
      .sort((a, b) => b.puntos - a.puntos)
      .map((e, i) => {
        const k = keyByName(e.nombre)
        const T = k ? TEAMS[k] : undefined
        return {
          posicion: i + 1,
          equipoId: k ? TEAM_NUM[k] : 0,
          nombre: e.nombre,
          puntos: e.puntos,
          partidosJugados: 38,
          golesFavor: T ? Math.round(T.gf * 38) : 0,
          golesContra: T ? Math.round(T.gc * 38) : 0,
        }
      })
  }
}

class HttpDataSource implements SadDataSource {
  readonly mode = 'http' as const

  async health(): Promise<FeedHealth> {
    const t0 = performance.now()
    try {
      const h = await SadApi.health()
      return {
        ok: h.status === 'ok' && h.dbOk,
        latencyMs: Math.round(performance.now() - t0),
        detail: h.lastPipelineRun ? `pipeline ${h.lastPipelineRun}` : `v${h.version}`,
      }
    } catch (e) {
      return { ok: false, latencyMs: null, detail: e instanceof Error ? e.message : 'error de red' }
    }
  }

  fixtures = (params?: FixturesParams) => SadApi.fixtures(params)
  fixtureLive = (fixtureId: number) => SadApi.fixtureLive(fixtureId)
  buscarEquipos = (buscar: string, limit?: number) => SadApi.buscarEquipos(buscar, limit)
  niveles = (equipoId: number, limit?: number) => SadApi.niveles(equipoId, limit)
  constantes = (equipoId: number, limit?: number) => SadApi.constantes(equipoId, limit)
  constantesCuota = (equipoId: number) => SadApi.constantesCuota(equipoId)
  prediccion = (fixtureId: number) => SadApi.prediccion(fixtureId)
  analisisPrepartido = (fixtureId: number) => SadApi.analisisPrepartido(fixtureId)
  cuotas = (fixtureId: number) => SadApi.cuotas(fixtureId)
  cuotasCasas = (fixtureId: number) => SadApi.cuotasCasas(fixtureId)
  cuotasHistorial = (fixtureId: number, casa?: string | null) => SadApi.cuotasHistorial(fixtureId, casa)
  cuotasHistorialFuentes = (fixtureId: number) => SadApi.cuotasHistorialFuentes(fixtureId)
  equipoStats = (equipoId: number) => SadApi.equipoStats(equipoId)
  liga = (ligaId: number) => SadApi.liga(ligaId)
  standings = (ligaId: number, temporada?: number) => SadApi.standings(ligaId, temporada)
}

let _ds: SadDataSource | null = null

export function getDataSource(): SadDataSource {
  if (!_ds) _ds = CONFIG.dataSource === 'http' ? new HttpDataSource() : new MockDataSource()
  return _ds
}
