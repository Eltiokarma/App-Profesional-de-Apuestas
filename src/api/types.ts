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
  /** URL del escudo (teams.logo de sad.db); null/ausente → iniciales de color. */
  logo?: string | null
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
  estadio?: string
  local: EquipoDTO
  visitante: EquipoDTO
  golesLocal: number | null
  golesVisitante: number | null
  /** URL del logo del torneo (leagues.logo). */
  ligaLogo?: string | null
  /** URL de la bandera del país (leagues.flag; null en copas internacionales). */
  ligaBandera?: string | null
  /** País del torneo: desambigua homónimos (Copa de la Liga de Perú vs Chile). */
  ligaPais?: string | null
}

/** Metadatos de una liga (GET /ligas/{ligaId}). */
export interface LigaDTO {
  id: number
  nombre: string
  pais: string | null
  logo: string | null
  bandera: string | null
  /** Última temporada conocida. */
  temporada: number | null
  /** Temporadas con fixtures capturados, descendente. */
  temporadas: number[]
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

/** Fila de constants + fusión (§3 y §4.2): la foto completa tras un partido.
 *  rivalNombre y goles vienen de processed_matches (rival_nombre, goals_*). */
export interface ConstantesDTO {
  equipoId: number
  fixtureId: number
  fecha: string
  condicion: 'Local' | 'Visita'
  rivalId: number
  rivalNombre: string
  nivelRival: number
  golesFavor: number
  golesContra: number
  ligaId: number
  /** true si el partido fue de torneo internacional (UCL, UEL, Libertadores…). */
  esInternacional: boolean
  q: {
    local: number | null
    visita: number | null
    negativo: number
    golesAnotado: number
    golesRecibido: number
    /** Aporte Doble Oportunidad (§3.6): 0 si perdió, si no max(dif·nivelRival, 0.5·nivelRival). */
    dc: number
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
    /** Doble Oportunidad (§3.6): racha "sin perder" (1X), no-negativa, resetea solo al perder. */
    dc: number
    dcLocal: number
    dcVisita: number
    /** Márgenes (§3.7): rachas por margen exacto de goles (1/2/3+), aporte plano nivelRival. */
    vic1: number; vic1Local: number; vic1Visita: number
    vic2: number; vic2Local: number; vic2Visita: number
    vic3: number; vic3Local: number; vic3Visita: number
    der1: number; der1Local: number; der1Visita: number
    der2: number; der2Local: number; der2Visita: number
    der3: number; der3Local: number; der3Visita: number
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
    kDc: number
    kDcLocal: number
    kDcVisita: number
    kVic1: number; kVic1Local: number; kVic1Visita: number
    kVic2: number; kVic2Local: number; kVic2Visita: number
    kVic3: number; kVic3Local: number; kVic3Visita: number
    kDer1: number; kDer1Local: number; kDer1Visita: number
    kDer2: number; kDer2Local: number; kDer2Visita: number
    kDer3: number; kDer3Local: number; kDer3Visita: number
  }
}

/** Fila de constants_cuota (k_cuota, §3.8): rachas de SUMA de cuota 1X2 prepartido,
 *  solo partidos de 2026. cuota.* = null si el partido no tenía cuota capturada. */
export interface ConstanteCuotaDTO {
  equipoId: number
  fixtureId: number
  fecha: string
  /** 1 gana · 0 empata · -1 pierde. */
  resultado: 1 | 0 | -1
  /** true si el equipo jugó de local ese partido (para el toggle LOCAL/VISITA). */
  esLocal: boolean
  cuota: { victoria: number | null; empate: number | null; derrota: number | null }
  k: {
    victoria: number; victoriaLocal: number; victoriaVisita: number
    empate: number; empateLocal: number; empateVisita: number
    derrota: number; derrotaLocal: number; derrotaVisita: number
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

/** Stats de temporada calculadas de los fixtures terminados (endpoint /equipos/{id}/stats).
 *  Los promedios avanzados son null hasta que el backend los derive (v0). */
export interface EquipoStatsDTO {
  equipoId: number
  nombre: string
  partidosJugados: number
  puntos: number
  /** Últimos 5 resultados, más reciente primero. */
  forma: ('W' | 'D' | 'L')[]
  golesFavorProm: number
  golesContraProm: number
  xgProm: number | null
  posesionProm: number | null
  tirosPuertaProm: number | null
  cornersProm: number | null
}

/** Fila de /ligas/{id}/standings (calculada de fixtures). */
export interface StandingRowDTO {
  posicion: number
  equipoId: number
  nombre: string
  puntos: number
  partidosJugados: number
  golesFavor: number
  golesContra: number
}

export interface CuotaDTO {
  fixtureId: number
  mercado: string // '1x2' | 'dc' | 'ou' | 'ah' | 'btts'
  seleccion: string // '1' | 'X' | '2' | 'O' | 'U' | …
  cuota: number
  actualizadoEn: string
}

/** Cuota en juego (última captura live). suspendida=true: la casa no la acepta ahora. */
export interface CuotaLiveDTO {
  mercado: string
  seleccion: string
  cuota: number
  suspendida: boolean
}

/** Un punto del movimiento en vivo (sin suspendidas), asc por captura. */
export interface PuntoLiveDTO {
  minuto: number | null
  mercado: string
  seleccion: string
  cuota: number
}

/** Evento del partido (gol, tarjeta) para anclar el movimiento de la gráfica. */
export interface EventoLiveDTO {
  minuto: number | null
  tipo: 'gol' | 'amarilla' | 'roja'
  equipoId: number | null
  jugador: string | null
  detalle: string | null
}

/** Estado en vivo real del fixture (ingesta SAD_LIVE_SEGUNDOS). */
export interface FixtureLiveDTO {
  fixtureId: number
  estado: EstadoFixture
  minuto: number | null
  golesLocal: number | null
  golesVisitante: number | null
  cuotas: CuotaLiveDTO[]
  serie: PuntoLiveDTO[]
  eventos: EventoLiveDTO[]
  /** null si la liga no tiene cobertura de odds live o la ingesta está apagada. */
  actualizadoEn: string | null
}

/** Cuota de UNA casa para una selección (última foto). mejor=true: la más alta. */
export interface CuotaCasaDTO {
  fixtureId: number
  mercado: string
  seleccion: string
  casaId: number
  casa: string
  cuota: number
  mejor: boolean
}

/** Un punto del movimiento prepartido: media entre casas en esa captura de la ingesta. */
export interface CuotaSnapshotDTO {
  fixtureId: number
  mercado: string
  seleccion: string
  cuota: number
  /** Nº de bookmakers promediados en la captura. */
  casas?: number
  capturadoEn: string
}

// ── análisis EFE+DTP (backend/analisis/, docs/efe-dtp/PLAN_ADAPTADO.md) ─────

export type EfeEstadoIndicador = 'verde' | 'ambar' | 'rojo'
export type EfeClasificacion = 'FORMADO' | 'EN_FORMACION' | 'SIN_FORMACION'

export interface EfeIndicador {
  id: string
  estado: EfeEstadoIndicador
  justificacion: string
  fuente: string | null
}

export interface EfeBloque {
  score: number
  max: number
  ponderado: number | null
  excluido: boolean | null
  motivo_exclusion: string | null
  d3_cap_aplicado: boolean | null
  ppp: number | null
  indicadores: EfeIndicador[]
}

export interface EfeJugador {
  nombre: string
  posicion: string
  zona: 'GK' | 'DEF' | 'MID' | 'ATK'
  rol: 'TF' | 'TH' | 'ROT' | 'SUP'
  apps: string | null
  estado: 'disponible' | 'baja' | 'duda'
  motivo: string | null
}

export interface EfeEquipo {
  color: string
  color_light: string
  color_mid: string
  bloques: Record<'A' | 'B' | 'C' | 'D' | 'E', EfeBloque>
  total: number
  maximo_alcanzable: number
  porcentaje: number
  clasificacion: EfeClasificacion
  disponibilidad: {
    jugadores: EfeJugador[]
    ip: number
    ip_nivel: EfeEstadoIndicador
    multiplicador_gk_aplicado: boolean
    reduccion_zonas: Record<'GK' | 'DEF' | 'MID' | 'ATK', number>
    f4: { rotados: number; diagnostico: string }
    f5_factor_x: { nombre: string; contexto: string }[]
  }
  dt: { nombre: string; asuncion: string | null; meses: number | null }
  calendario: {
    rival: string
    fecha: string | null
    condicion: 'L' | 'V'
    etiquetas: string[]
    posicion: number | null
    nota: string | null
  }[]
}

export interface EfeComparativo {
  version_efe: string
  partido: {
    equipo_a: string
    equipo_b: string
    torneo: string | null
    fase: string | null
    estadio: string | null
    fecha: string | null
    hora: string | null
    condicion: { a: 'L' | 'V'; b: 'L' | 'V' }
  }
  equipos: { a: EfeEquipo; b: EfeEquipo }
  matchup_h: {
    perfil_a: { sistema: string | null; estilo: string | null; fortaleza: string | null; vulnerabilidad: string | null }
    perfil_b: { sistema: string | null; estilo: string | null; fortaleza: string | null; vulnerabilidad: string | null }
    h2a: string | null
    h2b: string | null
    h2c: string | null
    diagnostico: 'FAVORABLE' | 'NEUTRO' | 'DESFAVORABLE'
    razon: string
  }
  alertas: { codigo: string; tipo: 'estructural' | 'fecha'; equipo: string | null; detalle: string }[]
  lectura_sad: {
    modulo_operativo: string
    un_x_dos: { texto: string; rango_ampliado: boolean }
    contexto_emocional: string
    dato_estructural: string
    paradoja: string | null
  }
  datos_faltantes: string[]
  fuentes: string[]
}

/** Registro de un análisis emitido (GET /analisis/partido/{id}, POST /analisis/efe). */
export interface AnalisisRegistroDTO {
  tipo: 'efe' | 'dtp' | 'matriz'
  fixtureId: number
  /** preliminar = XI provisional (T−24h) · confirmado = XI oficial (T−40min). */
  estado: 'preliminar' | 'confirmado'
  versionEfe: string
  creadoEn: string
  resultado: EfeComparativo
}
