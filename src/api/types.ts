// DTOs del contrato con el backend SAD (FastAPI + PostgreSQL).
// Fuente de verdad: docs/openapi.yaml. Estos tipos son el espejo TypeScript
// de las tablas del pipeline (levels.db → team_levels, constants.db →
// constants, discreto.db → processed_matches) ya en la nube.

export interface HealthDTO {
  status: 'ok' | 'degraded'
  version: string
  dbOk: boolean
  /** ISO-8601 del último ciclo completo del pipeline (null si nunca corrió). */
  lastPipelineRun: string | null
}

export interface EquipoDTO {
  id: number
  nombre: string
  abreviatura: string
  pais?: string
}

export type EstadoFixture = 'programado' | 'en_vivo' | 'finalizado'

export interface FixtureDTO {
  id: number
  fecha: string // ISO-8601 (timestamptz en Postgres)
  ligaId: number
  liga: string
  temporada: number
  estado: EstadoFixture
  minuto: number | null
  local: EquipoDTO
  visitante: EquipoDTO
  golesLocal: number | null
  golesVisitante: number | null
}

/** Fila de team_levels + discretización (§2 y §4.1 del motor). */
export interface NivelDTO {
  equipoId: number
  fixtureId: number
  fecha: string
  nivel: number // continuo ~0.5–3.5
  bin: number // 0–9 (bins fijos v6)
  binEtiqueta: string // 'Sin datos' … 'Élite'
}

/** Fila de constants + fusión (§3 y §4.2): la foto completa tras un partido. */
export interface ConstantesDTO {
  equipoId: number
  fixtureId: number
  fecha: string
  condicion: 'Local' | 'Visita'
  rivalId: number
  nivelRival: number
  q: {
    local: number | null
    visita: number | null
    negativo: number
    golesAnotado: number
    golesRecibido: number
  }
  k: {
    positivo: number
    negativo: number
    positivoLocal: number
    negativoLocal: number
    positivoVisita: number
    negativoVisita: number
    golesAnotado: number
    golesRecibido: number
    golesLocalAnotado: number
    golesLocalRecibido: number
    golesVisitaAnotado: number
    golesVisitaRecibido: number
  }
  fusion: {
    k: number
    kLocal: number
    kVisita: number
    golesAnotado: number
    golesRecibido: number
    golesLocalAnotado: number
    golesLocalRecibido: number
    golesVisitaAnotado: number
    golesVisitaRecibido: number
  }
}

export type SenalGap = 'fuerte' | 'leve' | 'equilibrio'

/** Ley de la Regresión al Nivel (§5) para un equipo dentro de un fixture. */
export interface GapEquipoDTO {
  equipoId: number
  nivel: number
  /** Promedio de puntos en los últimos 5 (null si no hay 5 partidos). */
  ptsRecientes: number | null
  /** μ con rival promedio (2.0) y 50 % de localía, recortado a [0, 3]. */
  ptsEsperados: number
  /** gap = esperados − recientes. >0 subrinde (tiende a mejorar). */
  gap: number | null
  senal: SenalGap | null
  tendencia: 'mejora' | 'empeora' | null
}

export interface PrediccionDTO {
  fixtureId: number
  local: GapEquipoDTO
  visitante: GapEquipoDTO
  /** gap_local − gap_visitante. */
  gapDiff: number | null
  generadoEn: string
}

/** Reporte integral pre-partido (endpoint /analisis-prepartido). */
export interface AnalisisPrepartidoDTO {
  fixtureId: number
  niveles: { local: NivelDTO; visitante: NivelDTO }
  constantes: { local: ConstantesDTO | null; visitante: ConstantesDTO | null }
  prediccion: PrediccionDTO
  resumen: string
}

export interface CuotaDTO {
  fixtureId: number
  mercado: string // '1x2' | 'dc' | 'ou' | 'ah' | 'btts'
  seleccion: string // '1' | 'X' | '2' | 'O' | 'U' | …
  cuota: number
  actualizadoEn: string
}
