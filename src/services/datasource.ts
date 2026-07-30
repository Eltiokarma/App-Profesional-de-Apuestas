// Fuente de datos conmutable: la app habla SIEMPRE el contrato de docs/openapi.yaml.
// - MockDataSource: el motor local (src/motor) sirviendo ese contrato (demo, default).
// - HttpDataSource: el backend FastAPI real (VITE_DATA_SOURCE=http).
// Migrar una pantalla a datos reales = consumirla vía getDataSource(); nada más.
import { SadApi } from '../api/sad'
import type {
  AnalisisPrepartidoDTO,
  AnalisisRegistroDTO,
  CargaDespensaDTO,
  CargaDespensaResultadoDTO,
  GeneracionEfeDTO,
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
  FichaEquipoDTO,
  FichaPartidoDTO,
  FixtureDTO,
  FixtureLiveDTO,
  VipEstadoDTO,
  GapEquipoDTO,
  JugadorDTO,
  AlineacionDTO,
  JugadorAlineadoDTO,
  EslabonDtpDTO,
  EtiquetaRivalDTO,
  FichaTacticaDTO,
  LigaDTO,
  NivelDTO,
  PartidoCalendarioDTO,
  PlantillaDTO,
  PreflightEfeDTO,
  PrediccionDTO,
  PuntoLiveDTO,
  StandingRowDTO,
} from '../api/types'
import { CONFIG, type DataSourceMode } from '../config'
import { MARKET_DEFS, MATCHES, STANDINGS, TEAMS } from '../data'
import { dtpDemo, efeDemo, timelineDemo } from '../data/efeDemo'
import { oddsFor, rng } from '../lib/odds'
import { levelBin } from '../motor/discretizer'
import { teamEngine } from '../motor/engine'
import { leagueOf } from '../motor/history'
import {
  gapDiff, gapDiffAjustado, gapFor, LOCALIA_NEUTRA, mu, recuperabilidad,
  RIVAL_PROMEDIO, senalCalendario, TRAMPA_DELTA_NIVEL,
} from '../motor/regression'
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
  /** Marca/desmarca un partido VIP (mock: en memoria; http: POST real). */
  marcarVip(fixtureId: number, activo: boolean): Promise<VipEstadoDTO>
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
  /** Plantilla con indicadores de jugadores (docs/JUGADORES.md); jugadores=[] sin ingesta. */
  plantilla(equipoId: number): Promise<PlantillaDTO>
  /** Ficha de partido: plantillas + congestión de ambos equipos (puente con los skills). */
  fichaPartido(fixtureId: number): Promise<FichaPartidoDTO>
  liga(ligaId: number, temporada?: number): Promise<LigaDTO>
  standings(ligaId: number, temporada?: number, fase?: string): Promise<StandingRowDTO[]>
  /** Análisis EFE+DTP emitidos para un fixture ([] si no hay). */
  analisisPartido(fixtureId: number): Promise<AnalisisRegistroDTO[]>
  /** Lanza el análisis EFE (respuesta inmediata: listo/generando/error).
   *  `forzar` = regenerar; `permitirFrio` = opt-in a pagar el análisis sin
   *  despensa (~$0.6-1.2) — por defecto el backend lo bloquea antes de gastar. */
  generarEfe(fixtureId: number, forzar?: boolean, permitirFrio?: boolean): Promise<GeneracionEfeDTO>
  /** Sondeo del trabajo de análisis EFE. */
  estadoEfe(fixtureId: number): Promise<GeneracionEfeDTO>
  /** Qué va a costar el EFE ANTES de generarlo (no gasta nada). */
  preflightEfe(fixtureId: number): Promise<PreflightEfeDTO>
  /** Carga manual de la despensa (investigación del Claude de escritorio). */
  cargarDespensa(payload: CargaDespensaDTO): Promise<CargaDespensaResultadoDTO>
  /** Lanza el timeline comparativo (mismo patrón asíncrono que el EFE). */
  generarTimeline(fixtureId: number, forzar?: boolean): Promise<GeneracionEfeDTO>
  /** Sondeo del trabajo de timeline. */
  estadoTimeline(fixtureId: number): Promise<GeneracionEfeDTO>
  /** Lanza el DTP desde un equipo foco (docs/efe-dtp/DTP_DISENO.md). */
  generarDtp(fixtureId: number, equipoFoco: number, forzar?: boolean): Promise<GeneracionEfeDTO>
  /** Sondeo del trabajo de DTP. */
  estadoDtp(fixtureId: number, equipoFoco: number): Promise<GeneracionEfeDTO>
  /** La película del equipo: cadena de pronóstico → veredicto → lección. */
  cadena(equipoId: number, limit?: number): Promise<EslabonDtpDTO[]>
  /** Calendario SAD: próximos partidos con el mapa de rivales (bloque G del EFE)
   *  ya calculado — la misma lectura en todas las pantallas, sin IA. */
  calendario(equipoId: number, n?: number): Promise<PartidoCalendarioDTO[]>
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
  140: { id: 140, nombre: 'LaLiga', pais: 'Spain', logo: 'https://media.api-sports.io/football/leagues/140.png', bandera: 'https://media.api-sports.io/flags/es.svg', temporada: 2026, temporadas: [2026], fases: [] },
  39: { id: 39, nombre: 'Premier League', pais: 'England', logo: 'https://media.api-sports.io/football/leagues/39.png', bandera: 'https://media.api-sports.io/flags/gb-eng.svg', temporada: 2026, temporadas: [2026], fases: [] },
  135: { id: 135, nombre: 'Serie A', pais: 'Italy', logo: 'https://media.api-sports.io/football/leagues/135.png', bandera: 'https://media.api-sports.io/flags/it.svg', temporada: 2026, temporadas: [2026], fases: [] },
}

// fecha sintética determinista para el historial del motor (t = jornada)
const tToIso = (t: number) => {
  const d = new Date(Date.UTC(2025, 7, 1) + t * 4 * 86_400_000)
  return d.toISOString()
}
const MOCK_NOW = '2026-07-02T21:00:00.000Z'
// marcas VIP de la demo: solo en memoria (el real vive en .vip_fixtures.json)
const MOCK_VIP = new Set<number>()

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

const esIntMatch = (m: (typeof MATCHES)[number]) => /(champions|europa|libertadores|sudamericana)/i.test(m.comp)

// Confianza en μ v2 por liga (calibración por liga 2026-07 — doc §5, misma regla que el backend)
const CONMEBOL = ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Paraguay', 'Peru', 'Uruguay', 'Venezuela']
function fiabilidadMuDe(m: (typeof MATCHES)[number]): { nivel: 'alta' | 'media' | 'baja'; nota: string } {
  const nombre = (m.league || m.comp || '').toLowerCase()
  const pais = LIGA_META[LIGA_NUM[m.lk] ?? 0]?.pais ?? ''
  if (nombre.includes('friendl') || nombre.includes('amistoso'))
    return { nivel: 'baja', nota: 'Amistosos: nivel y localía pesan mucho menos de lo que μ asume (rotaciones, sedes neutras) — señales de gap poco fiables.' }
  if (pais === 'Argentina')
    return { nivel: 'media', nota: 'Liga de paridad: la diferencia de niveles predice ~la mitad de lo que μ asume — desconfiar de favoritismos claros.' }
  if (CONMEBOL.includes(pais) || nombre.includes('libertadores') || nombre.includes('sudamericana'))
    return { nivel: 'media', nota: 'Sudamérica: la localía real (~+0.5–0.7) casi dobla la de μ (+0.38) — el local vale más de lo que μ dice.' }
  return { nivel: 'alta', nota: 'Sin desviaciones detectadas para esta liga en la calibración por liga (2026-07).' }
}

/** Contexto §5 v2 del fixture: μ del partido, camino de recuperación y trampa. */
function contextoCalendario(teamKey: string, m: (typeof MATCHES)[number]) {
  const eng = teamEngine(teamKey)!
  const esLocal = m.home === teamKey
  const rivalKey = esLocal ? m.away : m.home
  const nivelRivalHoy = teamEngine(rivalKey)?.level ?? 1
  // la demo vive en un solo día: "próximos" = programados posteriores del equipo
  const futuros = MATCHES.filter((x) => x.id !== m.id && x.status === 'sched' && (x.home === teamKey || x.away === teamKey)).slice(0, 3)
  const proximos = futuros.map((x) => {
    const esL = x.home === teamKey
    const rk = esL ? x.away : x.home
    const nr = teamEngine(rk)?.level ?? 1
    return {
      fixtureId: FIXTURE_NUM(x.id),
      fecha: MOCK_NOW,
      rival: equipoDTO(rk),
      esLocal: esL,
      nivelRival: nr,
      muEsperado: mu(eng.level, nr, esL ? 1 : 0),
      esInternacional: esIntMatch(x),
      diasDescanso: 0,
    }
  })
  const recup = recuperabilidad(proximos.map((p) => p.muEsperado))
  const grandeCerca = MATCHES.some(
    (x) => x.id !== m.id && (x.home === teamKey || x.away === teamKey) &&
      (esIntMatch(x) || (teamEngine(x.home === teamKey ? x.away : x.home)?.level ?? 1) >= eng.level),
  )
  return {
    muPartido: mu(eng.level, nivelRivalHoy, esLocal ? 1 : 0),
    proximos,
    recuperabilidad: recup,
    senalCalendario: senalCalendario(recup, mu(eng.level, RIVAL_PROMEDIO, LOCALIA_NEUTRA)),
    partidoTrampa: nivelRivalHoy <= eng.level - TRAMPA_DELTA_NIVEL && grandeCerca,
  }
}

function gapEquipoDTO(teamKey: string, m: (typeof MATCHES)[number]): GapEquipoDTO {
  const g = gapFor(teamKey)!
  return { equipoId: TEAM_NUM[teamKey], ...g, ...contextoCalendario(teamKey, m) }
}

// ── plantilla demo (capa de jugadores, docs/JUGADORES.md) ───────────────────
// Plantel determinista por equipo con la MISMA forma e indicadores que sirve
// el backend real (por-90 encogido, HHI, confianza, flags).
const DEMO_NOMBRES = ['R. Ferreyra', 'M. Ordóñez', 'L. Cabral', 'D. Peralta', 'J. Villalba', 'S. Quintero',
  'A. Bustos', 'T. Herrera', 'E. Saravia', 'N. Ríos', 'G. Ledesma', 'F. Aguirre', 'C. Montoya', 'I. Zárate',
  'P. Cáceres', 'B. Funes', 'O. Medrano', 'K. Ibáñez']
const DEMO_POS = ['Portero', 'Portero', 'Defensa', 'Defensa', 'Defensa', 'Defensa', 'Defensa',
  'Centrocampista', 'Centrocampista', 'Centrocampista', 'Centrocampista', 'Centrocampista',
  'Delantero', 'Delantero', 'Delantero', 'Delantero', 'Defensa', 'Centrocampista']

function plantillaDemo(teamKey: string): PlantillaDTO {
  const T = TEAMS[teamKey]
  const r = rng(teamKey + '|plantilla')
  const M = 900 // misma constante de encogimiento que el backend
  const PRIOR: Record<string, number> = { Portero: 0.01, Defensa: 0.08, Centrocampista: 0.22, Delantero: 0.45 }
  const base = DEMO_NOMBRES.map((nombre, i) => {
    const posicion = DEMO_POS[i]
    const titular = i % 2 === 0 || r() > 0.35
    const minutos = Math.round((titular ? 1700 : 450) * (0.55 + r() * 0.7))
    const partidos = Math.min(38, Math.round(minutos / 70))
    const esGK = posicion === 'Portero'
    const esDel = posicion === 'Delantero'
    const goles = esGK ? 0 : Math.round(minutos / 90 * (esDel ? 0.45 : posicion === 'Centrocampista' ? 0.15 : 0.04) * (0.5 + r()))
    const asistencias = esGK ? 0 : Math.round(minutos / 90 * 0.12 * (0.4 + r() * 1.2))
    const amarillas = Math.round(r() * 6)
    return { nombre, posicion, minutos, partidos, goles, asistencias, amarillas, i, rating: Math.round((6.4 + r() * 1.2) * 100) / 100 }
  })
  const maxMin = Math.max(...base.map((b) => b.minutos)) || 1
  const gaEquipo = base.reduce((s, b) => s + b.goles + b.asistencias, 0)
  const golesEquipo = base.reduce((s, b) => s + b.goles, 0)
  const jugadores: JugadorDTO[] = base.map((b) => {
    const esGK = b.posicion === 'Portero'
    const ga90 = b.minutos ? ((b.goles + b.asistencias) / b.minutos) * 90 : 0
    const conBaja = b.i === 12 // el primer delantero está de baja en la demo
    return {
      id: TEAM_NUM[teamKey] * 100 + b.i,
      nombre: b.nombre,
      edad: 21 + (b.i % 14),
      foto: null,
      posicion: b.posicion,
      partidos: b.partidos,
      titularidades: Math.round(b.partidos * 0.8),
      minutos: b.minutos,
      pctMinutos: Math.round((b.minutos / maxMin) * 1000) / 1000,
      rating: b.rating,
      confianza: (b.minutos >= 1800 ? 'A' : b.minutos >= 600 ? 'B' : 'C') as JugadorDTO['confianza'],
      goles: b.goles,
      asistencias: b.asistencias,
      golesP90: b.minutos ? Math.round((b.goles / b.minutos) * 90 * 1000) / 1000 : null,
      asistenciasP90: b.minutos ? Math.round((b.asistencias / b.minutos) * 90 * 1000) / 1000 : null,
      gaP90Ajustado: Math.round(((b.minutos * ga90 + M * (PRIOR[b.posicion] ?? 0.2)) / (b.minutos + M)) * 1000) / 1000,
      participacionOfensiva: gaEquipo ? Math.round(((b.goles + b.asistencias) / gaEquipo) * 1000) / 1000 : 0,
      amarillas: b.amarillas,
      rojas: 0,
      enCapilla: b.amarillas >= 4,
      paradasP90: esGK ? Math.round((2.4 + rng(b.nombre)() * 1.5) * 1000) / 1000 : null,
      golesEncajadosP90: esGK ? Math.round((0.8 + rng(b.nombre + 'gc')() * 0.7) * 1000) / 1000 : null,
      baja: conBaja ? { tipo: 'Missing Fixture', detalle: 'Lesión muscular' } : null,
      recienLlegado: b.i === 15 ? { desde: 'Deportivo Demo', fecha: '2026-06-30' } : null,
    }
  }).sort((a, b) => b.minutos - a.minutos)
  const shares = jugadores.filter((j) => j.goles + j.asistencias > 0).map((j) => (j.goles + j.asistencias) / (gaEquipo || 1))
  const top = [...jugadores].filter((j) => j.participacionOfensiva > 0).sort((a, b) => b.participacionOfensiva - a.participacionOfensiva).slice(0, 3)
  return {
    equipoId: TEAM_NUM[teamKey],
    nombre: T.name,
    temporada: 2026,
    actualizadoEn: MOCK_NOW,
    entrenador: { nombre: 'E. Domínguez', desde: '2025-12-01' },
    dependencia: {
      hhi: shares.length ? Math.round(shares.reduce((s, x) => s + x * x, 0) * 1000) / 1000 : null,
      top: top.map((j) => ({ jugadorId: j.id, nombre: j.nombre, participacion: j.participacionOfensiva })),
    },
    revolucion: { llegadas: 2, salidas: 1, ventanaDias: 120 },
    golesPlantilla: golesEquipo,
    jugadores,
  }
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
      .slice(0, Math.min(Math.max(params.limit ?? 50, 1), 500)) // mismo tope que el backend
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
      local: gapEquipoDTO(m.home, m),
      visitante: gapEquipoDTO(m.away, m),
      gapDiff: gapDiff(m.home, m.away),
      gapDiffAjustado: gapDiffAjustado(m.home, m.away),
      fiabilidadMu: fiabilidadMuDe(m),
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

  async marcarVip(fixtureId: number, activo: boolean): Promise<VipEstadoDTO> {
    if (activo) MOCK_VIP.add(fixtureId)
    else MOCK_VIP.delete(fixtureId)
    return { fixtureId, vip: activo }
  }

  async fixtureLive(fixtureId: number): Promise<FixtureLiveDTO> {
    // Demo: serie 1X2 determinista del segundo tiempo, con una suspendida al
    // final — misma forma que sirve el backend real desde odds_live.
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) throw new Error(`fixture ${fixtureId} no existe`)
    const estado = m.status === 'live' ? 'en_vivo' : m.status === 'fin' ? 'finalizado' : 'programado'
    const p = (m.score || '0 - 0').split('-').map((x) => parseInt(x.trim()) || 0)
    if (estado !== 'en_vivo') {
      return { fixtureId, estado, minuto: null, golesLocal: p[0] ?? null, golesVisitante: p[1] ?? null, cuotas: [], serie: [], eventos: [], actualizadoEn: null, coberturaLive: 'sin_consultar', coberturaConsultadaEn: null, vip: MOCK_VIP.has(fixtureId) }
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
    return { fixtureId, estado, minuto, golesLocal: p[0] ?? null, golesVisitante: p[1] ?? null, cuotas, serie, eventos, actualizadoEn: MOCK_NOW, coberturaLive: 'con_datos', coberturaConsultadaEn: MOCK_NOW, vip: MOCK_VIP.has(fixtureId) }
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

  // análisis EFE/timeline demo: se "generan" en memoria con una demora realista
  private _analisis = new Map<number, AnalisisRegistroDTO>()
  private _timelines = new Map<number, AnalisisRegistroDTO>()

  async analisisPartido(fixtureId: number): Promise<AnalisisRegistroDTO[]> {
    const out: AnalisisRegistroDTO[] = []
    const efe = this._analisis.get(fixtureId)
    if (efe) out.push(efe)
    const tl = this._timelines.get(fixtureId)
    if (tl) out.push(tl)
    return out
  }

  async generarTimeline(fixtureId: number, forzar = false): Promise<GeneracionEfeDTO> {
    const previo = this._timelines.get(fixtureId)
    if (previo && !forzar) return { estado: 'listo', registro: previo }
    if (forzar) this._timelines.delete(fixtureId)
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) return { estado: 'error', detalle: `fixture ${fixtureId} no existe` }
    await new Promise((r) => setTimeout(r, 1200))
    const reg: AnalisisRegistroDTO = {
      tipo: 'timeline',
      fixtureId,
      estado: 'preliminar',
      versionEfe: '1.5',
      creadoEn: new Date(MOCK_NOW).toISOString(),
      resultado: timelineDemo(TEAMS[m.home].name, TEAMS[m.away].name),
    }
    this._timelines.set(fixtureId, reg)
    return { estado: 'listo', registro: reg }
  }

  async estadoTimeline(fixtureId: number): Promise<GeneracionEfeDTO> {
    const reg = this._timelines.get(fixtureId)
    return reg ? { estado: 'listo', registro: reg } : { estado: 'nada' }
  }

  // DTP demo: la cadena vive en memoria, una entrada por (fixture, equipo foco)
  private _dtp = new Map<string, AnalisisRegistroDTO>()

  async generarDtp(fixtureId: number, equipoFoco: number, forzar = false): Promise<GeneracionEfeDTO> {
    const clave = `${fixtureId}:${equipoFoco}`
    const previo = this._dtp.get(clave)
    if (previo && !forzar) return { estado: 'listo', registro: previo }
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) return { estado: 'error', detalle: `fixture ${fixtureId} no existe` }
    const foco = NUM_TEAM[equipoFoco]
    if (foco !== m.home && foco !== m.away) {
      return { estado: 'error', detalle: `el equipo ${equipoFoco} no juega el fixture ${fixtureId}` }
    }
    await new Promise((r) => setTimeout(r, 1200))
    const rival = foco === m.home ? m.away : m.home
    const reg: AnalisisRegistroDTO = {
      tipo: 'dtp', fixtureId, estado: 'preliminar', versionEfe: '1.5',
      creadoEn: new Date(MOCK_NOW).toISOString(),
      resultado: dtpDemo(TEAMS[foco].name, TEAMS[rival].name),
    }
    this._dtp.set(clave, reg)
    return { estado: 'listo', registro: reg }
  }

  async estadoDtp(fixtureId: number, equipoFoco: number): Promise<GeneracionEfeDTO> {
    const reg = this._dtp.get(`${fixtureId}:${equipoFoco}`)
    return reg ? { estado: 'listo', registro: reg } : { estado: 'nada' }
  }

  async calendario(equipoId: number, n = 4): Promise<PartidoCalendarioDTO[]> {
    const key = NUM_TEAM[equipoId]
    if (!key || !TEAMS[key]) return []
    // la demo vive en un solo día: "próximos" = los programados del equipo
    const futuros = MATCHES.filter((x) => x.status === 'sched' && (x.home === key || x.away === key)).slice(0, n)
    const tabla = STANDINGS[TEAMS[key] && futuros[0] ? futuros[0].lk : 'laliga'] ?? []
    return futuros.map((x, i) => {
      const esLocal = x.home === key
      const rk = esLocal ? x.away : x.home
      const rival = TEAMS[rk]
      // solo las etiquetas que los datos de la demo sostienen, con su dato:
      // inventar las otras aquí enseñaría a la UI a confiar en humo
      const etiquetas: EtiquetaRivalDTO[] = []
      const derrotas = (() => {
        let c = 0
        for (const r of rival.form) { if (r === 'L') c++; else break }
        return c
      })()
      if (derrotas >= 3) {
        etiquetas.push({
          codigo: 'EN_CRISIS', label: 'EN CRISIS', dato: `${derrotas} derrotas seguidas`,
          nota: 'posible efecto rebote, en cualquiera de los dos sentidos',
        })
      }
      const g = gapFor(rk)
      if (g && g.gap != null && g.gap <= -0.35) {
        etiquetas.push({
          codigo: 'EQUIPO_SORPRESA', label: 'EQUIPO SORPRESA',
          dato: `rinde ${Math.abs(g.gap).toFixed(2)} pts/partido por encima de su nivel`,
          nota: 'candidato a regresión: la ventaja puede no sostenerse',
        })
      }
      return {
        fixtureId: FIXTURE_NUM(x.id),
        fecha: MOCK_NOW.slice(0, 10),
        rivalId: TEAM_NUM[rk],
        rival: rival.name,
        condicion: esLocal ? 'L' : 'V',
        torneo: x.comp,
        ronda: x.league,
        posicionRival: rival.pos,
        equiposEnLaTabla: tabla.length || null,
        zonaRival: !tabla.length ? null : rival.pos <= 4 ? 'alta' : rival.pos > tabla.length - 3 ? 'descenso' : 'media',
        diasDescanso: i === 0 ? null : 0,
        etiquetas,
      }
    })
  }

  async cadena(equipoId: number): Promise<EslabonDtpDTO[]> {
    const nombre = TEAMS[NUM_TEAM[equipoId]]?.name
    if (!nombre) return []
    return [...this._dtp.values()]
      .map((r) => r.resultado as unknown as EslabonDtpDTO)
      .filter((e) => e && e.equipoFoco === nombre)
  }

  async generarEfe(fixtureId: number, forzar = false): Promise<GeneracionEfeDTO> {
    const previo = this._analisis.get(fixtureId)
    if (previo && !forzar) return { estado: 'listo', registro: previo }
    if (forzar) this._analisis.delete(fixtureId) // regenerar: descartar y emitir de nuevo
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) return { estado: 'error', detalle: `fixture ${fixtureId} no existe` }
    await new Promise((r) => setTimeout(r, 1200)) // demora de "análisis"
    const reg: AnalisisRegistroDTO = {
      tipo: 'efe',
      fixtureId,
      estado: 'preliminar',
      versionEfe: '1.5',
      creadoEn: new Date(MOCK_NOW).toISOString(),
      resultado: efeDemo(TEAMS[m.home].name, TEAMS[m.away].name, m.league, ''),
    }
    this._analisis.set(fixtureId, reg)
    return { estado: 'listo', registro: reg }
  }

  async estadoEfe(fixtureId: number): Promise<GeneracionEfeDTO> {
    const reg = this._analisis.get(fixtureId)
    return reg ? { estado: 'listo', registro: reg } : { estado: 'nada' }
  }

  async preflightEfe(fixtureId: number): Promise<PreflightEfeDTO> {
    // demo: el motor local no gasta nada, y decirlo es más honesto que
    // simular un semáforo tibio que aquí nunca se cumpliría
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    const nombres = m ? [TEAMS[m.home]?.name ?? m.home, TEAMS[m.away]?.name ?? m.away] : []
    return {
      fixtureId,
      nivel: 'caliente',
      faltantes: 0,
      dudosos: 0,
      busquedasPrevistas: 0,
      bloqueado: false,
      umbralFrio: 6,
      costo: { min: 0, max: 0, medido: false, muestra: 0 },
      yaExiste: this._analisis.has(fixtureId),
      demo: true,
      equipos: nombres.map((equipo) => ({
        equipo,
        enDespensa: true,
        datos: ['dt', 'plantel', 'tabla', 'resultados', 'fixture', 'xi_reciente', 'bajas'].map((tipo) => ({
          tipo, origen: 'local' as const, detalle: 'modo demo: motor local, sin costo', edadDias: null,
        })),
      })),
      recomendaciones: ['Modo demo: el análisis es de muestra y no gasta nada.'],
    }
  }

  async cargarDespensa(payload: CargaDespensaDTO): Promise<CargaDespensaResultadoDTO> {
    // demo: se "acepta" sin almacenar (la despensa real vive en efe.db del backend)
    const depositados = payload.equipos.reduce(
      (s, e) => s + Object.values(e.datos).filter((v) => (typeof v === 'string' ? v.trim() : v.length > 0)).length, 0)
    return { depositados, equipos: payload.equipos.map((e) => e.equipo) }
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

  async plantilla(equipoId: number): Promise<PlantillaDTO> {
    const key = NUM_TEAM[equipoId]
    if (!key || !TEAMS[key]) throw new Error(`equipo ${equipoId} no existe`)
    return plantillaDemo(key)
  }

  async fichaPartido(fixtureId: number): Promise<FichaPartidoDTO> {
    const m = MATCHES.find((x) => FIXTURE_NUM(x.id) === fixtureId)
    if (!m) throw new Error(`fixture ${fixtureId} no existe`)
    const lado = (key: string, dias: number): FichaEquipoDTO => ({
      ...plantillaDemo(key),
      congestion: { diasDescanso: dias, partidos21d: 7 - dias },
    })
    // ficha táctica demo: solo el partido en juego la tiene, para que la UI
    // pueda desarrollarse sin backend. El resto va vacío — "real o nada".
    // El XI sale de la MISMA plantilla demo (ids incluidos): así el cruce de
    // scores por jugadorId funciona igual que con los datos reales.
    const enJuego = m.status === 'live'
    const xi = (key: string, formacion: string): AlineacionDTO => {
      const p = plantillaDemo(key)
      const orden: Record<string, number> = { Portero: 0, Defensa: 1, Centrocampista: 2, Delantero: 3 }
      const ordenados = [...p.jugadores].sort((a, b) => (orden[a.posicion] ?? 2) - (orden[b.posicion] ?? 2) || b.minutos - a.minutos)
      // UN portero al arco; el suplente de arco va al banco, no de lateral
      const gks = ordenados.filter((j) => j.posicion === 'Portero')
      const campo = ordenados.filter((j) => j.posicion !== 'Portero')
      const js = [...gks.slice(0, 1), ...campo.slice(0, 10), ...gks.slice(1, 2), ...campo.slice(10, 12)]
      const alinear = (j: JugadorDTO, i: number, titular: boolean): JugadorAlineadoDTO => ({
        jugadorId: j.id, nombre: j.nombre, numero: (titular ? 1 : 12) + i,
        posicion: j.posicion === 'Portero' ? 'G' : j.posicion === 'Defensa' ? 'D' : j.posicion === 'Delantero' ? 'F' : 'M',
        grid: titular ? `${i === 0 ? 1 : i < 5 ? 2 : i < 9 ? 3 : 4}:${(i % 4) + 1}` : null,
        carril: titular ? (['centro', 'izquierda', 'centro', 'derecha'] as const)[i % 4] : null,
      })
      return {
        equipoId: TEAM_NUM[key] ?? 1, formacion, entrenador: p.entrenador?.nombre ?? null, conGrid: true,
        titulares: js.slice(0, 11).map((j, i) => alinear(j, i, true)),
        suplentes: js.slice(11, 14).map((j, i) => alinear(j, i, false)),
      }
    }
    const xiL = xi(m.home, '4-4-2')
    const xiV = xi(m.away, '4-3-3')
    const ev = (j: JugadorAlineadoDTO) => ({ jugador: j.nombre, jugadorId: j.jugadorId })
    const tactica: FichaTacticaDTO = enJuego
      ? {
          capturada: true,
          alineaciones: { local: xiL, visitante: xiV },
          eventos: [
            { minuto: 34, extra: 0, tipo: 'Goal', detalle: 'Normal Goal', equipoId: xiL.equipoId, ...ev(xiL.titulares[9]), asistente: xiL.titulares[7].nombre, asistenteId: xiL.titulares[7].jugadorId },
            { minuto: 51, extra: 0, tipo: 'Goal', detalle: 'Penalty', equipoId: xiV.equipoId, ...ev(xiV.titulares[10]), asistente: null, asistenteId: null },
            // cambios: el segundo lleva jugador/asistente INVERTIDOS a
            // propósito — la API real también los confunde y la UI tiene que
            // decidir por membresía (quién estaba en cancha sale)
            { minuto: 58, extra: 0, tipo: 'subst', detalle: 'Substitution 1', equipoId: xiL.equipoId, ...ev(xiL.titulares[6]), asistente: xiL.suplentes[0].nombre, asistenteId: xiL.suplentes[0].jugadorId },
            { minuto: 65, extra: 0, tipo: 'subst', detalle: 'Substitution 1', equipoId: xiV.equipoId, ...ev(xiV.suplentes[1]), asistente: xiV.titulares[8].nombre, asistenteId: xiV.titulares[8].jugadorId },
          ],
          estadisticas: { local: { 'Ball Possession': '58%' }, visitante: { 'Ball Possession': '42%' } },
        }
      : { capturada: false, alineaciones: null, eventos: [], estadisticas: null }
    return {
      fixtureId,
      generadoEn: MOCK_NOW,
      local: lado(m.home, 3),
      visitante: lado(m.away, 5),
      tactica,
    }
  }

  async liga(ligaId: number, _temporada?: number): Promise<LigaDTO> {
    const meta = LIGA_META[ligaId]
    if (!meta) throw new Error(`liga ${ligaId} no existe`)
    return meta // las ligas demo son europeas: sin Apertura/Clausura (fases: [])
  }

  async standings(ligaId: number, temporada?: number, _fase?: string): Promise<StandingRowDTO[]> {
    if (temporada != null && temporada !== 2026) return [] // la demo solo tiene la 2026
    // las ligas demo no parten el año: `_fase` no aplica, siempre la tabla del año
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
  marcarVip = (fixtureId: number, activo: boolean) => SadApi.marcarVip(fixtureId, activo)
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
  analisisPartido = (fixtureId: number) => SadApi.analisisPartido(fixtureId)
  generarEfe = (fixtureId: number, forzar?: boolean, permitirFrio?: boolean) => SadApi.generarEfe(fixtureId, forzar, permitirFrio)
  estadoEfe = (fixtureId: number) => SadApi.estadoEfe(fixtureId)
  preflightEfe = (fixtureId: number) => SadApi.preflightEfe(fixtureId)
  cargarDespensa = (payload: CargaDespensaDTO) => SadApi.cargarDespensa(payload)
  generarTimeline = (fixtureId: number, forzar?: boolean) => SadApi.generarTimeline(fixtureId, forzar)
  estadoTimeline = (fixtureId: number) => SadApi.estadoTimeline(fixtureId)
  generarDtp = (fixtureId: number, equipoFoco: number, forzar?: boolean) => SadApi.generarDtp(fixtureId, equipoFoco, forzar)
  estadoDtp = (fixtureId: number, equipoFoco: number) => SadApi.estadoDtp(fixtureId, equipoFoco)
  cadena = (equipoId: number, limit?: number) => SadApi.cadena(equipoId, limit)
  calendario = (equipoId: number, n?: number) => SadApi.calendario(equipoId, n)
  equipoStats = (equipoId: number) => SadApi.equipoStats(equipoId)
  plantilla = (equipoId: number) => SadApi.plantilla(equipoId)
  fichaPartido = (fixtureId: number) => SadApi.fichaPartido(fixtureId)
  liga = (ligaId: number, temporada?: number) => SadApi.liga(ligaId, temporada)
  standings = (ligaId: number, temporada?: number, fase?: string) => SadApi.standings(ligaId, temporada, fase)
}

let _ds: SadDataSource | null = null

export function getDataSource(): SadDataSource {
  if (!_ds) _ds = CONFIG.dataSource === 'http' ? new HttpDataSource() : new MockDataSource()
  return _ds
}
