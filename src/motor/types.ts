// Motor SAD — tipos del pipeline niveles → constantes K → fusión.
// Port fiel de MOTOR_SAD_EXTRACCION.md (SAD v3.4): misma semántica que
// levels_calculator / constants_calculator / discretizer_db.

/** Un partido terminado (equivale a una fila de `fixtures` en sad.db). */
export interface Fixture {
  id: number
  /** Orden cronológico (equivale a `date`; los acumuladores K dependen de él). */
  t: number
  home: string
  away: string
  gh: number
  ga: number
}

/** El mismo partido desde la perspectiva de UN equipo (doble fila por fixture). */
export interface TeamMatch {
  fixtureId: number
  t: number
  rival: string
  isLocal: boolean
  gf: number
  ga: number
  /** true si fue partido de torneo internacional (UCL, UEL, Libertadores…). */
  esInternacional?: boolean
}

/** Fila de `team_levels`: nivel continuo (~0.5–3.5) por (equipo, fixture). */
export interface LevelRow {
  fixtureId: number
  t: number
  level: number
}

/** Valores instantáneos q* de un partido (§3.2). null = condición no aplica. */
export interface QVals {
  local: number | null
  visita: number | null
  negativo: number
  golesAnotado: number
  golesRecibido: number
}

/** Los 12 acumuladores de racha k* (§3.3). Solo un lado ≠ 0 a la vez. */
export interface KState {
  pos: number
  neg: number
  posLocal: number
  negLocal: number
  posVisita: number
  negVisita: number
  gA: number // k_goles_anotado
  gR: number // k_goles_recibido (acumula VALOR ABSOLUTO)
  gLA: number
  gLR: number
  gVA: number
  gVR: number
}

/** K fusionadas (§4.2): k = k_positivo + k_negativo; los k_goles pasan tal cual. */
export interface FusedK {
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

/** Foto completa tras cada partido (fila de `constants` + fusión). */
export interface KSnapshot extends TeamMatch {
  rivalLevel: number
  q: QVals
  k: KState
  fused: FusedK
}

export interface TeamEngine {
  levels: LevelRow[]
  snaps: KSnapshot[]
  /** Nivel continuo actual (último registro; 0.5 si no hay). */
  level: number
  bin: number
  binLabel: string
}
