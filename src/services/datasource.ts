// Fuente de datos conmutable: la app habla SIEMPRE el contrato de docs/openapi.yaml.
// - MockDataSource: el motor local (src/motor) sirviendo ese contrato (demo, default).
// - HttpDataSource: el backend FastAPI real (VITE_DATA_SOURCE=http).
// Migrar una pantalla a datos reales = consumirla vía getDataSource(); nada más.
import { SadApi } from '../api/sad'
import type {
  AnalisisPrepartidoDTO,
  ConstantesDTO,
  CuotaDTO,
  FixtureDTO,
  GapEquipoDTO,
  NivelDTO,
  PrediccionDTO,
} from '../api/types'
import { CONFIG, type DataSourceMode } from '../config'
import { MARKET_DEFS, MATCHES, TEAMS } from '../data'
import { oddsFor } from '../lib/odds'
import { levelBin } from '../motor/discretizer'
import { teamEngine } from '../motor/engine'
import { gapDiff, gapFor } from '../motor/regression'
import type { KSnapshot } from '../motor/types'

export interface FeedHealth {
  ok: boolean
  latencyMs: number | null
  detail: string
}

export interface SadDataSource {
  readonly mode: DataSourceMode
  health(): Promise<FeedHealth>
  fixtures(): Promise<FixtureDTO[]>
  niveles(equipoId: number, limit?: number): Promise<NivelDTO[]>
  constantes(equipoId: number, limit?: number): Promise<ConstantesDTO[]>
  prediccion(fixtureId: number): Promise<PrediccionDTO>
  analisisPrepartido(fixtureId: number): Promise<AnalisisPrepartidoDTO>
  cuotas(fixtureId: number): Promise<CuotaDTO[]>
}

// ---------- mapeo de ids internos (strings) ↔ contrato (números) ----------
const TEAM_KEYS = Object.keys(TEAMS)
export const TEAM_NUM: Record<string, number> = Object.fromEntries(TEAM_KEYS.map((k, i) => [k, 100 + i]))
export const NUM_TEAM: Record<number, string> = Object.fromEntries(TEAM_KEYS.map((k, i) => [100 + i, k]))
export const FIXTURE_NUM = (matchId: string) => parseInt(matchId.slice(1), 10)

const LIGA_NUM: Record<string, number> = { laliga: 140, premier: 39, seriea: 135 }

// fecha sintética determinista para el historial del motor (t = jornada)
const tToIso = (t: number) => {
  const d = new Date(Date.UTC(2025, 7, 1) + t * 4 * 86_400_000)
  return d.toISOString()
}
const MOCK_NOW = '2026-07-02T21:00:00.000Z'

function equipoDTO(key: string) {
  const T = TEAMS[key]
  return { id: TEAM_NUM[key], nombre: T.name, abreviatura: T.short }
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
    q: {
      local: s.q.local,
      visita: s.q.visita,
      negativo: s.q.negativo,
      golesAnotado: s.q.golesAnotado,
      golesRecibido: s.q.golesRecibido,
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

  async fixtures(): Promise<FixtureDTO[]> {
    return MATCHES.map((m) => {
      const goles = (m.score || '0 - 0').split('-').map((x) => parseInt(x.trim()) || 0)
      const enJuego = m.status === 'live'
      const hora = m.status === 'sched' && /^\d{2}:\d{2}$/.test(m.min) ? m.min : '21:00'
      return {
        id: FIXTURE_NUM(m.id),
        fecha: `2026-07-02T${hora}:00.000Z`,
        ligaId: LIGA_NUM[m.lk] ?? 0,
        liga: m.league,
        temporada: 2026,
        estado: enJuego ? 'en_vivo' : m.status === 'fin' ? 'finalizado' : 'programado',
        minuto: enJuego ? parseInt(m.min) || null : null,
        estadio: m.venue,
        local: equipoDTO(m.home),
        visitante: equipoDTO(m.away),
        golesLocal: m.status === 'sched' ? null : goles[0],
        golesVisitante: m.status === 'sched' ? null : goles[1],
      }
    })
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

  fixtures = () => SadApi.fixtures()
  niveles = (equipoId: number, limit?: number) => SadApi.niveles(equipoId, limit)
  constantes = (equipoId: number, limit?: number) => SadApi.constantes(equipoId, limit)
  prediccion = (fixtureId: number) => SadApi.prediccion(fixtureId)
  analisisPrepartido = (fixtureId: number) => SadApi.analisisPrepartido(fixtureId)
  cuotas = (fixtureId: number) => SadApi.cuotas(fixtureId)
}

let _ds: SadDataSource | null = null

export function getDataSource(): SadDataSource {
  if (!_ds) _ds = CONFIG.dataSource === 'http' ? new HttpDataSource() : new MockDataSource()
  return _ds
}
