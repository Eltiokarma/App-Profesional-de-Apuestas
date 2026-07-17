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
  /** Fecha del partido (solo informativa, para tooltips; el motor no la usa). */
  fecha?: string
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
  /** Aporte de Doble Oportunidad (§3.6 / ROADMAP §1): 0 si perdió, si no
   *  max(dif·nivel_rival, 0.5·nivel_rival). Alimenta los acumuladores k_dc. */
  dc: number
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
  // Doble Oportunidad (§3.6): racha "sin perder" (1X). No-negativos, resetean
  // solo al perder. dc = total, dcLocal/dcVisita solo en su condición.
  dc: number
  dcLocal: number
  dcVisita: number
  // Márgenes (§3.7): rachas por margen EXACTO de goles (1, 2, 3+). Aporte plano
  // nivel_rival; solo un bucket del mismo signo ≠ 0 a la vez; el empate resetea
  // ambos signos. Local/visita solo se tocan en su condición.
  vic1: number; vic1Local: number; vic1Visita: number
  vic2: number; vic2Local: number; vic2Visita: number
  vic3: number; vic3Local: number; vic3Visita: number
  der1: number; der1Local: number; der1Visita: number
  der2: number; der2Local: number; der2Visita: number
  der3: number; der3Local: number; der3Visita: number
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
  // Doble Oportunidad: k_dc es un único acumulador no-negativo → sin fusión ±,
  // el valor fusionado es el propio acumulador (§3.6).
  kDc: number
  kDcLocal: number
  kDcVisita: number
  // Márgenes (§3.7): acumuladores no-negativos → sin fusión ±, pasan tal cual.
  kVic1: number; kVic1Local: number; kVic1Visita: number
  kVic2: number; kVic2Local: number; kVic2Visita: number
  kVic3: number; kVic3Local: number; kVic3Visita: number
  kDer1: number; kDer1Local: number; kDer1Visita: number
  kDer2: number; kDer2Local: number; kDer2Visita: number
  kDer3: number; kDer3Local: number; kDer3Visita: number
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
