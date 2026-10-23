// Reventón de la burbuja — espejo TS de backend/analisis/burbuja.py.
// El dueño de la matemática es el backend (el http la lee por
// GET /equipos/{id}/burbujas); este espejo alimenta el mock y los tests.
// Las reglas están documentadas en docs/REVENTON.md; cambiar una aquí sin
// cambiarla allá rompe scripts/casos_burbuja.json (test dorado de paridad).
import type {
  BurbujasEquipoDTO,
  ConstantesDTO,
  DistribucionDTO,
  EspinaTarjetaDTO,
  EstabilidadEquipoDTO,
  FamiliaBurbuja,
  FamiliaBurbujaDTO,
  HistorialPeriodoDTO,
  PeriodoBurbujaDTO,
  HistorialSignoDTO,
  ExtremoBurbujaDTO,
  PlantillaDTO,
  ReventonDTO,
  SignoBurbuja,
} from '../api/types'

/** Lo que el análisis necesita de cada fila de constantes (subconjunto del DTO). */
export type FilaK = Pick<
  ConstantesDTO,
  'fixtureId' | 'fecha' | 'condicion' | 'rivalId' | 'rivalNombre' | 'nivelRival' | 'golesFavor' | 'golesContra' | 'esInternacional'
> & { fusion: Pick<ConstantesDTO['fusion'], 'k' | 'kLocal' | 'kVisita'>; temporada?: number | null; ligaId?: number }

export type ProximoBurbuja = NonNullable<BurbujasEquipoDTO['proximo']>

/** Lo que el análisis lee de la plantilla (subconjunto del DTO). */
export type PlantillaBurbuja = Pick<PlantillaDTO, 'actualizadoEn' | 'entrenador' | 'revolucion'> & {
  jugadores: { baja?: { lectura?: string } | null }[]
}

export const FAMILIAS: FamiliaBurbuja[] = ['total', 'local', 'visita']
const CLAVE_FUSION: Record<FamiliaBurbuja, 'k' | 'kLocal' | 'kVisita'> = { total: 'k', local: 'kLocal', visita: 'kVisita' }

export const BIN_GLOBALES_ALTO = 7
export const BIN_GLOBALES_BAJO = 2
// rival frente a la mediana con la que suele reventar, en la dirección del
// riesgo: lejos (< −0.15) · zona (±0.15) · fuerte (≥ 0.15) · muy fuerte (≥ 0.45).
// Puntos calibrados con el backtest real del 16/09/2026 (docs/REVENTON.md §8).
export const ZONA_TOLERANCIA = 0.15
export const RIVAL_FUERTE = 0.45
// corrida limpia del 14/10/2026 (espejo de burbuja.py, REVENTON §13.2): antes 2 · 3 · 5 con la fuga
export const PUNTOS_RIVAL: Record<TramoRival, number> = { lejos: 0, zona: 0, fuerte: 1, 'muy fuerte': 2 }
export const PUNTOS_RACHA = 1
/** Las dos señales del backtest de las lecciones (espejo de burbuja.py, REVENTON §12). */
export const PUNTOS_CONTRAMANO = 1
export const PUNTOS_FAVOR: Record<'no' | 'favorito' | 'muy favorito', number> = { no: 0, favorito: -1, 'muy favorito': -3 }
export const FAVORITO = 0.5
export const MUY_FAVORITO = 1.0
export type TramoRival = 'lejos' | 'zona' | 'fuerte' | 'muy fuerte'
export const MUESTRA_BAJA = 3
export const MUESTRA_ALTA = 6
export const DT_ASENTADO_DIAS = 90
/** Movimientos CON MINUTOS de la ventana (incidencia 43, usuario 23/10/2026: 10 y 20, primer corte). */
export const MOVIMIENTOS_TRANSICION = 10
export const MOVIMIENTOS_INESTABLE = 20
export const BAJAS_TRANSICION = 5
export const PLANTILLA_VIEJA_DIAS = 30
const MAX_REVENTONES_SALIDA = 40

export const AVISO_REVENTON =
  'Guía, no probabilidad: compara la burbuja abierta con lo que este equipo aguantó ' +
  'antes de reventar (K, partidos y nivel del rival). Sirve para saber cuándo NO apostar.'

// ── utilidades numéricas (idénticas al backend) ─────────────────────────────

const r2 = (x: number) => Math.floor(x * 100 + 0.5) / 100
const redondear = (v: number, escala: number) => Math.floor(v * escala + 0.5) / escala

function dist(vals: number[], escalaModa: number): DistribucionDTO | null {
  const n = vals.length
  if (!n) return null
  const s = vals.slice().sort((a, b) => a - b)
  const media = s.reduce((a, b) => a + b, 0) / n
  const mediana = n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2
  const conteo = new Map<number, number>()
  for (const v of vals) {
    const b = redondear(v, escalaModa)
    conteo.set(b, (conteo.get(b) ?? 0) + 1)
  }
  let mx = 0
  for (const c of conteo.values()) mx = Math.max(mx, c)
  let moda: number | null = null
  if (mx >= 2) {
    for (const [b, c] of conteo) if (c === mx && (moda == null || b < moda)) moda = b
  }
  return { media: r2(media), mediana: r2(mediana), moda: moda == null ? null : r2(moda), min: r2(s[0]), max: r2(s[n - 1]) }
}

const signoDe = (v: number) => (v > 0 ? 1 : v < 0 ? -1 : 0)

function diasEntre(desde: string | null | undefined, hoy: string): number | null {
  if (!desde) return null
  const a = Date.parse(String(desde).slice(0, 10) + 'T00:00:00Z')
  const b = Date.parse(String(hoy).slice(0, 10) + 'T00:00:00Z')
  if (isNaN(a) || isNaN(b)) return null
  return Math.round((b - a) / 86_400_000)
}

// ── episodios ───────────────────────────────────────────────────────────────

interface Episodio {
  signo: 1 | -1
  partidos: number
  kPico: number
  k: number
  desde: string
  amistosos: number
}

function reventonDe(ep: Episodio, fila: FilaK, termina: 'cero' | 'cambio'): ReventonDTO {
  return {
    signo: ep.signo > 0 ? '+' : '-',
    partidos: ep.partidos,
    kPico: r2(ep.kPico),
    fixtureId: fila.fixtureId,
    fecha: fila.fecha,
    rivalId: fila.rivalId,
    rival: fila.rivalNombre,
    nivelRival: r2(fila.nivelRival),
    condicion: fila.condicion === 'Local' ? 'L' : 'V',
    resultado: `${fila.golesFavor}-${fila.golesContra}`,
    esInternacional: !!fila.esInternacional,
    // cómo se cortó: a 0 (empate) o al otro signo (espejo de _reventon)
    termina,
  }
}

/** Recorre la K fusionada de la familia: reventones cerrados, burbuja abierta y partidos en condición. */
export function episodios(filas: FilaK[], familia: FamiliaBurbuja): { cerrados: ReventonDTO[]; abierta: Episodio | null; nCond: number } {
  const clave = CLAVE_FUSION[familia]
  const cerrados: ReventonDTO[] = []
  let ep: Episodio | null = null
  let nCond = 0
  for (const fila of filas) {
    if (familia === 'local' && fila.condicion !== 'Local') continue
    if (familia === 'visita' && fila.condicion !== 'Visita') continue
    nCond++
    const v = fila.fusion[clave]
    const s = signoDe(v)
    if (s === 0) {
      if (ep) {
        cerrados.push(reventonDe(ep, fila, 'cero'))
        ep = null
      }
      continue
    }
    const amistoso = fila.ligaId != null && AMISTOSOS.has(fila.ligaId) ? 1 : 0
    if (ep && ep.signo === s) {
      ep.partidos++
      ep.amistosos += amistoso
      ep.kPico = Math.max(ep.kPico, Math.abs(v))
      ep.k = v
      continue
    }
    if (ep) cerrados.push(reventonDe(ep, fila, 'cambio')) // cambio de signo en el mismo partido
    ep = { signo: s, partidos: 1, kPico: Math.abs(v), k: v, desde: fila.fecha, amistosos: amistoso }
  }
  return { cerrados, abierta: ep, nCond }
}

function historialDe(cerrados: ReventonDTO[]): FamiliaBurbujaDTO['historial'] {
  const de = (signo: SignoBurbuja): HistorialSignoDTO | null => {
    const rs = cerrados.filter((r) => r.signo === signo)
    if (!rs.length) return null
    return {
      n: rs.length,
      kPico: dist(rs.map((r) => r.kPico), 1)!,
      partidos: dist(rs.map((r) => r.partidos), 1)!,
      nivelRival: dist(rs.map((r) => r.nivelRival), 10)!,
      termina: { cero: rs.filter((r) => r.termina === 'cero').length, cambio: rs.filter((r) => r.termina === 'cambio').length },
    }
  }
  return { positivo: de('+'), negativo: de('-') }
}

// ── riesgo ──────────────────────────────────────────────────────────────────

/** Cómo se mueve la K total en el partido siguiente por signo y riesgo (espejo de MOVIMIENTO_BACKTEST). */
export const MOVIMIENTO_BACKTEST: Record<SignoBurbuja, Record<'bajo' | 'medio' | 'alto' | 'muy alto', [number, number, number]>> = {
  '+': { bajo: [0.539, 0.247, 0.213], medio: [0.459, 0.264, 0.276], alto: [0.352, 0.277, 0.371], 'muy alto': [0.272, 0.269, 0.459] },
  '-': { bajo: [0.523, 0.25, 0.227], medio: [0.462, 0.272, 0.266], alto: [0.354, 0.269, 0.378], 'muy alto': [0.28, 0.273, 0.446] },
}

/** Lo mismo para las K de la condición, en su próximo partido de esa condición (espejo de MOVIMIENTO_CONDICION). */
export const MOVIMIENTO_CONDICION: Record<'local' | 'visita', typeof MOVIMIENTO_BACKTEST> = {
  local: {
    '+': { bajo: [0.627, 0.219, 0.154], medio: [0.5, 0.262, 0.238], alto: [0.426, 0.275, 0.299], 'muy alto': [0.346, 0.288, 0.366] },
    '-': { bajo: [0.454, 0.266, 0.28], medio: [0.346, 0.292, 0.363], alto: [0.267, 0.27, 0.463], 'muy alto': [0.214, 0.255, 0.53] },
  },
  visita: {
    '+': { bajo: [0.468, 0.261, 0.272], medio: [0.331, 0.289, 0.379], alto: [0.273, 0.271, 0.456], 'muy alto': [0.197, 0.256, 0.546] },
    '-': { bajo: [0.607, 0.227, 0.166], medio: [0.509, 0.257, 0.234], alto: [0.418, 0.285, 0.297], 'muy alto': [0.355, 0.276, 0.37] },
  },
}

function movimientoEsperado(familia: FamiliaBurbuja, signo: SignoBurbuja, nivel: 'bajo' | 'medio' | 'alto' | 'muy alto'): { sigue: number; cero: number; cambio: number } | null {
  const m = (familia === 'total' ? MOVIMIENTO_BACKTEST : MOVIMIENTO_CONDICION[familia])[signo][nivel]
  return { sigue: m[0], cero: m[1], cambio: m[2] }
}

// cortes de la recalibración del 14/10/2026 (espejo de _nivel_riesgo): el puntaje puede ser negativo
const nivelRiesgo = (p: number): 'bajo' | 'medio' | 'alto' | 'muy alto' => (p >= 3 ? 'muy alto' : p >= 1 ? 'alto' : p >= 0 ? 'medio' : 'bajo')

function confianzaDe(n: number, estabilidad: EstabilidadEquipoDTO): [RiesgoConfianza, string[]] {
  const orden: RiesgoConfianza[] = ['baja', 'media', 'alta']
  const motivos: string[] = []
  let c: RiesgoConfianza
  if (n < MUESTRA_BAJA) {
    c = 'baja'
    motivos.push(`solo ${n} ${n === 1 ? 'reventón' : 'reventones'} de este signo en la historia`)
  } else if (n < MUESTRA_ALTA) {
    c = 'media'
    motivos.push(`${n} reventones de este signo: muestra corta`)
  } else {
    c = 'alta'
    motivos.push(`${n} reventones de este signo`)
  }
  const grado = estabilidad.grado
  const tope: RiesgoConfianza = { estable: 'alta', 'en transición': 'media', inestable: 'baja', 'sin dato': 'media' }[grado] as RiesgoConfianza
  if (orden.indexOf(tope) < orden.indexOf(c)) {
    c = tope
    motivos.push(`estabilidad ${grado}: el patrón histórico puede ser de otro equipo`)
  } else if (grado !== 'estable') {
    motivos.push(`estabilidad ${grado}`)
  }
  return [c, motivos]
}
type RiesgoConfianza = 'baja' | 'media' | 'alta'

/** Franja alta (espejo de CERCA_PCT): sin récord, la K o la racha ya superan
 *  a este % de los reventones del signo. Mismo principio que el extremo, un
 *  escalón más suave: no puntúa, dice cuánto se carga (docs/REVENTON.md §10). */
export const CERCA_PCT = 90
/** Récord de racha: SUPERAR el máximo y con 3+ partidos (espejo de RACHA_RECORD_MIN, incidencia 67). */
export const RACHA_RECORD_MIN = 3

/** Amistosos de clubes (espejo de AMISTOSOS): cuentan en la burbuja, pero un
 *  extremo hecho con la mitad o más de amistosos se marca INFLADO (Lazio,
 *  Real Madrid; docs/REVENTON.md §10.2). No apaga la alerta ni mueve el riesgo. */
export const AMISTOSOS = new Set([667])

const conSigno = (v: number, signo: SignoBurbuja) => `${signo === '+' ? '+' : '-'}${r2(Math.abs(v))}`

/** ALERTA DE EXTREMO: prudencia, no probabilidad. Una K récord no revienta
 *  más que otra (por eso no puntúa), pero es terreno sin precedente para este
 *  equipo y ahí no se carga la apuesta a que siga. Aparte del riesgo.
 *  `cerca` es el escalón de abajo; `activo` sigue siendo solo el récord. */
export function extremoDe(kAbs: number, partidos: number, base: HistorialSignoDTO, nCond: number, signo: SignoBurbuja, de: ReventonDTO[] = [], amistosos = 0): ExtremoBurbujaDTO {
  const kRecord = kAbs >= base.kPico.max
  const rachaRecord = partidos > base.partidos.max && partidos >= RACHA_RECORD_MIN
  const n = de.length
  const pctK = n ? Math.floor((100 * de.filter((r) => r.kPico < kAbs).length) / n + 0.5) : 0
  const pctR = n ? Math.floor((100 * de.filter((r) => r.partidos < partidos).length) / n + 0.5) : 0
  const kCerca = !kRecord && pctK >= CERCA_PCT
  const rCerca = !rachaRecord && partidos >= RACHA_RECORD_MIN && pctR >= CERCA_PCT
  const cerca = !(kRecord || rachaRecord) && (kCerca || rCerca)
  const motivos: string[] = []
  const lado = signo === '+' ? 'alta' : 'baja'
  const kTxt = conSigno(kAbs, signo)
  const maxTxt = conSigno(base.kPico.max, signo)
  if (kRecord) motivos.push(`K ${kTxt}: la más ${lado} de los ${nCond} partidos que hay en la base (récord previo ${maxTxt})`)
  if (rachaRecord) motivos.push(`${partidos} partidos seguidos: la racha más larga de los ${nCond} partidos que hay en la base (máximo previo ${base.partidos.max})`)
  if (cerca && kCerca) motivos.push(`K ${kTxt}: más ${lado} que el ${pctK} % de las ${n} burbujas ${signo} que reventaron (récord previo ${maxTxt}, a ${r2(base.kPico.max - kAbs)})`)
  if (cerca && rCerca) motivos.push(`${partidos} partidos seguidos: más que el ${pctR} % de las ${n} burbujas ${signo} que reventaron (máximo previo ${base.partidos.max})`)
  const texto = kRecord || rachaRecord
    ? 'EXTREMO: la burbuja está en su máximo histórico. El modelo no lo puntúa como riesgo (la tasa de reventón no sube con la K), pero es terreno sin precedente para este equipo: no cargar la apuesta a que la racha siga'
    : cerca
      ? `CERCA DEL EXTREMO: la burbuja está en la franja más alta de su historia (por encima del ${CERCA_PCT} % de las que reventaron). El modelo no lo puntúa como riesgo, pero queda poco margen antes del récord: no cargar fuerte a que la racha siga`
      : ''
  let inflada: ExtremoBurbujaDTO['inflada'] = null
  // o la racha récord solo es récord contando los amistosos (Saint-Étienne 2 de 7, Elversberg 1 de 3)
  const sinAm = partidos - amistosos
  const soloPorAmistosos = rachaRecord && !kRecord && amistosos > 0 && (sinAm <= base.partidos.max || sinAm < RACHA_RECORD_MIN)
  // la marca va en CUALQUIER racha abierta, no solo en el récord (incidencia 311, Stuttgart)
  if (amistosos > 0 && (amistosos * 2 >= partidos || soloPorAmistosos)) {
    const alerta = kRecord || rachaRecord || cerca
    inflada = {
      amistosos,
      partidos,
      texto: `INFLADA: ${amistosos} de los ${partidos} partidos de la racha son amistosos${soloPorAmistosos ? ` y sin ellos la racha (${sinAm}) no sería récord (máximo previo ${base.partidos.max})` : ''}${alerta ? '. Cuentan (la racha es del equipo), pero el récord se armó en buena parte fuera de la competición: leer la alerta con eso a la vista' : '. Cuentan (la racha es del equipo), pero se armó en buena parte fuera de la competición: el último partido oficial puede contar otra historia'}`,
    }
    if (alerta) motivos.push(`inflada: ${amistosos} de ${partidos} partidos de la racha son amistosos`)
  }
  return {
    activo: kRecord || rachaRecord,
    kRecord,
    rachaRecord,
    cerca,
    partidosHistoria: nCond,
    maximoPrevio: { kPico: base.kPico.max, partidos: base.partidos.max },
    motivos,
    texto,
    inflada,
  }
}

/** Los mismos reventones, acotados en el tiempo (espejo de `periodos_de`): la
 *  referencia global manda en el riesgo; estas son referencia para el que lee.
 *  Se filtra por la fecha en la que reventó, nunca se recortan episodios. */
export const ULTIMOS_N = 20

export function periodosDe(filas: FilaK[], plantilla: PlantillaBurbuja | null | undefined): PeriodoBurbujaDTO[] {
  const out: PeriodoBurbujaDTO[] = []
  if (!filas.length) return out
  const fecha = (f: FilaK) => String(f.fecha ?? '').slice(0, 10)
  const ultima = filas[filas.length - 1]
  const fechaUltima = fecha(ultima)
  const temporadas = [...new Set(filas.map((f) => f.temporada).filter((t): t is number => t != null))].sort((x, y) => x - y)
  if (temporadas.length) {
    const inicio = new Map<number, string>()
    for (const f of filas) if (f.temporada != null && !inicio.has(f.temporada)) inicio.set(f.temporada, fecha(f))
    temporadas.forEach((t, i) => {
      const sig = i + 1 < temporadas.length ? temporadas[i + 1] : null
      out.push({ clave: `temporada:${t}`, etiqueta: `temporada ${t}`, desde: inicio.get(t)!, hasta: sig != null ? inicio.get(sig)! : '', vigente: t === ultima.temporada, sinDato: '' })
    })
  } else {
    out.push({ clave: 'temporada', etiqueta: 'esta temporada', desde: '', hasta: '', vigente: true, sinDato: 'las filas no traen la temporada del torneo' })
  }
  const anios = [...new Set(filas.map(fecha).filter(Boolean).map((f) => f.slice(0, 4)))].sort()
  for (const a of anios) {
    out.push({ clave: `anio:${a}`, etiqueta: `año ${a}`, desde: `${a}-01-01`, hasta: `${Number(a) + 1}-01-01`, vigente: a === fechaUltima.slice(0, 4), sinDato: '' })
  }
  const ent = plantilla?.entrenador
  const desdeDt = String(ent?.desde ?? '').slice(0, 10)
  if (ent?.nombre && desdeDt.length === 10) {
    out.push({ clave: 'dt', etiqueta: `con ${ent.nombre} (desde ${desdeDt})`, desde: desdeDt, hasta: '', vigente: true, sinDato: '' })
  } else {
    out.push({ clave: 'dt', etiqueta: 'con el DT actual', desde: '', hasta: '', vigente: true, sinDato: 'sin DT con fecha de asunción en la plantilla' })
  }
  const corte = filas.length >= ULTIMOS_N ? filas[filas.length - ULTIMOS_N] : filas[0]
  out.push({ clave: `ultimos${ULTIMOS_N}`, etiqueta: `últimos ${Math.min(ULTIMOS_N, filas.length)} partidos`, desde: fecha(corte), hasta: '', vigente: true, sinDato: '' })
  return out
}

function enPeriodo(fecha: string | undefined, per: PeriodoBurbujaDTO): boolean {
  const f = String(fecha ?? '').slice(0, 10)
  return f >= per.desde && (!per.hasta || f < per.hasta)
}

function historialPorPeriodo(filas: FilaK[], cerrados: ReventonDTO[], periodos: PeriodoBurbujaDTO[], familia: FamiliaBurbuja): HistorialPeriodoDTO[] {
  return periodos.map((per) => {
    if (per.sinDato || !per.desde) return { ...per, partidos: 0, reventones: 0, positivo: null, negativo: null }
    const de = cerrados.filter((r) => enPeriodo(r.fecha, per))
    const partidos = filas.filter((f) => enPeriodo(f.fecha, per)
      && (familia === 'total' || f.condicion === (familia === 'local' ? 'Local' : 'Visita'))).length
    const hist = historialDe(de)
    return { ...per, partidos, reventones: de.length, positivo: hist.positivo, negativo: hist.negativo }
  })
}

function analizarFamilia(filas: FilaK[], familia: FamiliaBurbuja, proximo: ProximoBurbuja | null, estabilidad: EstabilidadEquipoDTO, periodos: PeriodoBurbujaDTO[] = [], nivelEquipo: number | null = null): FamiliaBurbujaDTO {
  const { cerrados, abierta: ep, nCond } = episodios(filas, familia)
  const hist = historialDe(cerrados)
  const aplica = !proximo ? null : familia === 'total' ? true : proximo.condicion === (familia === 'local' ? 'L' : 'V')
  const out: FamiliaBurbujaDTO = {
    familia,
    partidosEnCondicion: nCond,
    actual: null,
    reventones: cerrados.slice(-MAX_REVENTONES_SALIDA),
    historial: hist,
    historialPorPeriodo: historialPorPeriodo(filas, cerrados, periodos, familia),
    posicion: null,
    rival: null,
    riesgo: null,
    extremo: null,
  }
  if (!ep) return out
  const signo: SignoBurbuja = ep.signo > 0 ? '+' : '-'
  const kAbs = Math.abs(ep.k)
  out.actual = { signo, k: r2(ep.k), partidos: ep.partidos, kPico: r2(ep.kPico), desde: ep.desde, amistosos: ep.amistosos, aplicaAlProximo: aplica }
  const base = signo === '+' ? hist.positivo : hist.negativo
  if (!base) {
    out.riesgo = {
      nivel: 'sin base', puntos: 0,
      motivos: ['sin reventones previos de este signo: no hay con qué comparar'],
      confianza: 'baja', confianzaMotivos: ['sin historia del signo'],
    }
    return out
  }
  const de = cerrados.filter((r) => r.signo === signo)
  const n = de.length
  const pctK = Math.floor((100 * de.filter((r) => r.kPico <= kAbs).length) / n + 0.5)
  const pctR = Math.floor((100 * de.filter((r) => r.partidos <= ep.partidos).length) / n + 0.5)
  const medK = base.kPico.mediana
  out.posicion = { percentilK: pctK, percentilRacha: pctR, kSobreMediana: medK <= 0 ? null : r2(kAbs / medK) }
  out.extremo = extremoDe(kAbs, ep.partidos, base, nCond, signo, de, ep.amistosos)

  let puntos = 0
  const motivos: string[] = []
  // La K NO puntúa: el backtest real (docs/REVENTON.md §8) mostró que estar
  // por encima de la K con la que suele reventar no adelanta el reventón.
  if (kAbs >= base.kPico.max) {
    motivos.push(`K ${r2(kAbs)}: nunca aguantó tanta (máximo previo ${base.kPico.max}) · informativo, la K no puntúa`)
  } else if (kAbs >= medK) {
    motivos.push(`K ${r2(kAbs)} por encima de la mediana de reventón (${medK}) · informativo, la K no puntúa`)
  } else {
    motivos.push(`K ${r2(kAbs)} por debajo de la mediana de reventón (${medK}) · informativo, la K no puntúa`)
  }
  const medP = base.partidos.mediana
  if (ep.partidos >= medP) {
    puntos += PUNTOS_RACHA
    motivos.push(`${ep.partidos} partidos: en la mediana de racha (${medP}) o más (+${PUNTOS_RACHA})`)
  } else {
    motivos.push(`${ep.partidos} partidos: por debajo de la mediana de racha (${medP})`)
  }

  if (proximo && aplica) {
    const medN = base.nivelRival.mediana
    const nivelProx = proximo.nivelRival
    // distancia en la dirección del riesgo: la burbuja + revienta ante rivales
    // más fuertes que la mediana; la − se corta ante rivales más flojos
    const d = r2(signo === '+' ? nivelProx - medN : medN - nivelProx)
    const tramo: TramoRival = d < -ZONA_TOLERANCIA ? 'lejos' : d < ZONA_TOLERANCIA ? 'zona' : d < RIVAL_FUERTE ? 'fuerte' : 'muy fuerte'
    const pts = PUNTOS_RIVAL[tramo]
    puntos += pts
    out.rival = { nivelProximo: r2(nivelProx), medianaReventon: medN, distancia: r2(nivelProx - medN), enZona: tramo !== 'lejos', tramo }
    const quien = `el próximo rival (${proximo.rival}, nivel ${r2(nivelProx)})`
    const verbo = signo === '+' ? 'reventar' : 'cortarse la racha'
    const lado = signo === '+' ? 'fuerte' : 'flojo'
    if (tramo === 'lejos') motivos.push(`${quien} queda lejos del nivel con el que suele ${verbo} (mediana ${medN})`)
    else if (tramo === 'zona') motivos.push(`${quien} está en la zona donde suele ${verbo} (mediana ${medN})` + (pts ? ` (+${pts})` : ''))
    else if (tramo === 'fuerte') motivos.push(`${quien} es más ${lado} que los rivales con los que suele ${verbo} (mediana ${medN})` + (pts ? ` (+${pts})` : ''))
    else motivos.push(`${quien} es mucho más ${lado} que los rivales con los que suele ${verbo} (mediana ${medN})` + (pts ? ` (+${pts})` : ''))
    // a favor de que la racha siga: el favorito con racha +, el débil con racha −
    if (nivelEquipo != null) {
      const g = r2(signo === '+' ? nivelEquipo - nivelProx : nivelProx - nivelEquipo)
      const fav = g >= MUY_FAVORITO ? 'muy favorito' : g >= FAVORITO ? 'favorito' : 'no'
      out.rival.aFavor = g
      out.rival.favorito = fav
      const pf = PUNTOS_FAVOR[fav]
      puntos += pf
      if (fav !== 'no') {
        // dicho desde el lado de la racha: con racha − el favorito es el RIVAL
        const mucho = fav === 'muy favorito'
        const quienF = signo === '+'
          ? `el equipo es ${mucho ? 'muy ' : ''}favorito: ${Math.abs(g)} de nivel sobre el rival`
          : `el rival es ${mucho ? 'mucho ' : ''}más fuerte: ${Math.abs(g)} de nivel sobre el equipo`
        motivos.push(`${quienF}, a favor de que la racha siga` + (pf ? ` (${pf > 0 ? '+' : ''}${pf})` : ''))
      }
    }
    // la racha hecha en la condición CONTRARIA a la del próximo partido
    const racha = filas.filter((f) => familia === 'total' || f.condicion === (familia === 'local' ? 'Local' : 'Visita')).slice(-ep.partidos)
    const condProx = proximo.condicion === 'L' ? 'Local' : 'Visita'
    const contra = racha.filter((f) => f.condicion !== condProx).length
    if (racha.length && contra * 3 >= 2 * racha.length) {
      out.actual!.contramano = true
      puntos += PUNTOS_CONTRAMANO
      motivos.push(`${contra} de ${racha.length} partidos de la racha en la otra condición: el próximo es de ${condProx === 'Local' ? 'local' : 'visita'}` + (PUNTOS_CONTRAMANO ? ` (+${PUNTOS_CONTRAMANO})` : ''))
    } else {
      out.actual!.contramano = false
    }
  } else if (proximo) {
    motivos.push('la familia no se mueve en el próximo partido (otra condición): el rival no puntúa')
  } else {
    motivos.push('sin próximo partido programado: el rival no puntúa')
  }

  const [confianza, confianzaMotivos] = confianzaDe(n, estabilidad)
  const nivel = nivelRiesgo(puntos)
  out.riesgo = { nivel, puntos, motivos, confianza, confianzaMotivos, movimiento: aplica === false ? null : movimientoEsperado(familia, signo, nivel) }
  return out
}

/** Umbral de la espina FUERTE (espejo de `burbuja.ESPINA_FUERTE`). */
export const ESPINA_FUERTE = 0.5

/** La espina de la tarjeta: el movimiento más probable de la guía calibrada
 *  dicho como resultado del equipo (espejo de `burbuja.espina_tarjeta`). */
export function espinaTarjeta(signo: string | null | undefined, movimiento: { sigue: number; cero: number; cambio: number } | null | undefined): EspinaTarjetaDTO | null {
  if ((signo !== '+' && signo !== '-') || !movimiento) return null
  let mov: 'sigue' | 'cero' | 'cambio' = 'sigue'
  let prob = Number(movimiento.sigue) || 0
  for (const k of ['cero', 'cambio'] as const) {
    const p = Number(movimiento[k]) || 0
    if (p > prob) { mov = k; prob = p }
  }
  const lectura = mov === 'cero' ? 'cero' : (mov === 'sigue') === (signo === '+') ? 'positiva' : 'negativa'
  return { lectura, movimiento: mov, prob: Math.round(prob * 1000) / 1000, fuerza: prob >= ESPINA_FUERTE ? 'fuerte' : 'debil' }
}

// ── estabilidad ─────────────────────────────────────────────────────────────

export function estabilidadDe(plantilla: PlantillaBurbuja | null | undefined, hoy: string): EstabilidadEquipoDTO {
  const sinDato = ['dueños / organización que maneja el club: sin fuente en la base']
  if (!plantilla || !plantilla.jugadores.length) {
    return {
      grado: 'sin dato',
      motivos: ['plantilla sin capturar: la ingesta de jugadores no corrió para este equipo'],
      sinDato: [...sinDato, 'cuerpo técnico', 'plantel', 'bajas'],
      dt: null, movimientos: null, bajas: null, actualizadoEn: null,
    }
  }
  const motivos: string[] = []
  const peor = { estable: 0, 'en transición': 1, inestable: 2 } as const
  let grado: 'estable' | 'en transición' | 'inestable' = 'estable'
  const subir = (g: 'en transición' | 'inestable') => { if (peor[g] > peor[grado]) grado = g }

  const ent = plantilla.entrenador
  let dt: EstabilidadEquipoDTO['dt'] = null
  if (ent && ent.nombre) {
    const dias = diasEntre(ent.desde, hoy)
    dt = { nombre: ent.nombre, desde: ent.desde, dias }
    if (dias == null) {
      sinDato.push('fecha de asunción del DT')
      motivos.push(`DT ${ent.nombre} sin fecha de asunción`)
    } else if (dias < DT_ASENTADO_DIAS && ent.fuente === 'coachs') {
      // la llegada de /coachs es aproximada: no mueve la estabilidad (incidencia 186)
      sinDato.push('fecha de asunción del DT confirmada')
      motivos.push(`DT ${ent.nombre}: la base dice ${dias} días, pero la llegada es la aproximada de la ` +
        'carrera de la API; no mueve la estabilidad hasta confirmarla en prensa')
    } else if (dias < DT_ASENTADO_DIAS) {
      subir('inestable')
      motivos.push(`DT ${ent.nombre} lleva ${dias} días: la historia de K es de otro cuerpo técnico`)
    } else if (ent.fuente === 'coachs') {
      // asentado igual, pero los días de /coachs no son dato (incidencia 385)
      sinDato.push('fecha de asunción del DT confirmada')
      motivos.push(`DT ${ent.nombre} asentado (unos ${dias} días según la carrera de la API, ` +
        'aproximado: confirmar en prensa)')
    } else {
      motivos.push(`DT ${ent.nombre} asentado (${dias} días)`)
    }
  } else {
    sinDato.push('cuerpo técnico')
    motivos.push('sin DT registrado')
  }

  const rev = plantilla.revolucion ?? { llegadas: 0, salidas: 0, ventanaDias: 0 }
  const movimientos = { llegadas: rev.llegadas, salidas: rev.salidas, ventanaDias: rev.ventanaDias }
  const mov = rev.llegadas + rev.salidas
  const pap = rev.enPapeles
  // con minutos en el primer equipo (incidencia 43): el total en papeles, al lado
  const pal = (mov === 1 ? 'movimiento' : 'movimientos') + (pap ? ` con minutos (de ${pap.llegadas + pap.salidas} en papeles)` : '')
  if (mov >= MOVIMIENTOS_INESTABLE) {
    subir('inestable')
    motivos.push(`${mov} ${pal} en ${rev.ventanaDias} días: plantel en obra`)
  } else if (mov >= MOVIMIENTOS_TRANSICION) {
    subir('en transición')
    motivos.push(`${mov} ${pal} en ${rev.ventanaDias} días`)
  } else {
    motivos.push(`${mov} ${pal} en ${rev.ventanaDias} días: plantel quieto`)
  }

  // un flag «Missing Fixture» leído como ruido (media plantilla marcada) no
  // es una baja, ni una que el once desmintió: no mueven la estabilidad
  // (docs/JUGADORES.md)
  const bajas = plantilla.jugadores.filter((j) => !!j.baja && j.baja.lectura !== 'ruido' && j.baja.lectura !== 'desmentida').length
  if (bajas >= BAJAS_TRANSICION) {
    subir('en transición')
    motivos.push(`${bajas} bajas en la plantilla`)
  }

  const act = plantilla.actualizadoEn
  const edad = act ? diasEntre(act, hoy) : null
  if (edad != null && edad >= PLANTILLA_VIEJA_DIAS) motivos.push(`plantilla de hace ${edad} días: el DT y las bajas pueden estar viejos`)

  return { grado, motivos, sinDato, dt, movimientos, bajas, actualizadoEn: act }
}

// ── entrada ─────────────────────────────────────────────────────────────────

/** La hipótesis del nivel (alto o bajo → globales; medio → la condición del
 *  próximo). Viaja como dato porque el backtest real NO la confirmó. */
export function reglaNivel(bin: number, proximo: ProximoBurbuja | null): BurbujasEquipoDTO['mandan']['reglaNivel'] {
  if (bin >= BIN_GLOBALES_ALTO || bin <= BIN_GLOBALES_BAJO) {
    return {
      tipo: 'globales',
      familias: ['total'],
      motivo: `nivel ${bin >= BIN_GLOBALES_ALTO ? 'alto' : 'bajo'} (bin ${bin}): pesarían más las globales`,
      confirmada: false,
    }
  }
  const familias: FamiliaBurbuja[] = !proximo ? ['local', 'visita'] : [proximo.condicion === 'L' ? 'local' : 'visita']
  return {
    tipo: 'especificas',
    familias,
    motivo:
      `nivel medio (bin ${bin}): pesarían más las de la condición` +
      (!proximo ? '' : ` — el próximo es de ${proximo.condicion === 'L' ? 'local' : 'visita'}`),
    confirmada: false,
  }
}

/** Qué familia pesa: la TOTAL, siempre (en el backtest real separa más que
 *  local/visita en todos los niveles). La regla del nivel va en reglaNivel. */
export function mandanDe(bin: number, proximo: ProximoBurbuja | null): BurbujasEquipoDTO['mandan'] {
  return {
    tipo: 'globales',
    familias: ['total'],
    motivo: 'la familia total es la que más separa en el backtest (todos los niveles); local y visita quedan como detalle',
    reglaNivel: reglaNivel(bin, proximo),
  }
}

export interface ContextoBurbuja {
  equipoId: number
  nombre?: string | null
  nivel: number
  bin: number
  proximo: ProximoBurbuja | null
  plantilla: PlantillaBurbuja | null
  /** 'YYYY-MM-DD' — se pasa para que el análisis sea determinista. */
  hoy: string
}

/** `filas` en orden CRONOLÓGICO (el contrato /constantes entrega desc: invertir antes). */
export function analizarBurbujas(filas: FilaK[], ctx: ContextoBurbuja): BurbujasEquipoDTO {
  const estabilidad = estabilidadDe(ctx.plantilla, ctx.hoy)
  const periodos = periodosDe(filas, ctx.plantilla)
  const familias = {} as Record<FamiliaBurbuja, FamiliaBurbujaDTO>
  for (const f of FAMILIAS) familias[f] = analizarFamilia(filas, f, ctx.proximo, estabilidad, periodos, ctx.nivel)
  return {
    equipoId: ctx.equipoId,
    nombre: ctx.nombre ?? null,
    nivel: r2(ctx.nivel),
    bin: Math.trunc(ctx.bin),
    partidos: filas.length,
    mandan: mandanDe(Math.trunc(ctx.bin), ctx.proximo),
    proximo: ctx.proximo ? { ...ctx.proximo, nivelRival: r2(ctx.proximo.nivelRival) } : null,
    estabilidad,
    familias,
    periodos,
    aviso: AVISO_REVENTON,
  }
}

