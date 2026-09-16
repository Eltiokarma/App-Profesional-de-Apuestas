// Reventón de la burbuja — espejo TS de backend/analisis/burbuja.py.
// El dueño de la matemática es el backend (el http la lee por
// GET /equipos/{id}/burbujas); este espejo alimenta el mock y los tests.
// Las reglas están documentadas en docs/REVENTON.md; cambiar una aquí sin
// cambiarla allá rompe scripts/casos_burbuja.json (test dorado de paridad).
import type {
  BurbujasEquipoDTO,
  ConstantesDTO,
  DistribucionDTO,
  EstabilidadEquipoDTO,
  FamiliaBurbuja,
  FamiliaBurbujaDTO,
  HistorialSignoDTO,
  PlantillaDTO,
  ReventonDTO,
  SignoBurbuja,
} from '../api/types'

/** Lo que el análisis necesita de cada fila de constantes (subconjunto del DTO). */
export type FilaK = Pick<
  ConstantesDTO,
  'fixtureId' | 'fecha' | 'condicion' | 'rivalId' | 'rivalNombre' | 'nivelRival' | 'golesFavor' | 'golesContra' | 'esInternacional'
> & { fusion: Pick<ConstantesDTO['fusion'], 'k' | 'kLocal' | 'kVisita'> }

export type ProximoBurbuja = NonNullable<BurbujasEquipoDTO['proximo']>

/** Lo que el análisis lee de la plantilla (subconjunto del DTO). */
export type PlantillaBurbuja = Pick<PlantillaDTO, 'actualizadoEn' | 'entrenador' | 'revolucion'> & {
  jugadores: { baja?: unknown }[]
}

export const FAMILIAS: FamiliaBurbuja[] = ['total', 'local', 'visita']
const CLAVE_FUSION: Record<FamiliaBurbuja, 'k' | 'kLocal' | 'kVisita'> = { total: 'k', local: 'kLocal', visita: 'kVisita' }

export const BIN_GLOBALES_ALTO = 7
export const BIN_GLOBALES_BAJO = 2
export const ZONA_TOLERANCIA = 0.15
export const MUESTRA_BAJA = 3
export const MUESTRA_ALTA = 6
export const DT_ASENTADO_DIAS = 90
export const MOVIMIENTOS_TRANSICION = 3
export const MOVIMIENTOS_INESTABLE = 6
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
}

function reventonDe(ep: Episodio, fila: FilaK): ReventonDTO {
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
        cerrados.push(reventonDe(ep, fila))
        ep = null
      }
      continue
    }
    if (ep && ep.signo === s) {
      ep.partidos++
      ep.kPico = Math.max(ep.kPico, Math.abs(v))
      ep.k = v
      continue
    }
    if (ep) cerrados.push(reventonDe(ep, fila)) // cambio de signo en el mismo partido
    ep = { signo: s, partidos: 1, kPico: Math.abs(v), k: v, desde: fila.fecha }
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
    }
  }
  return { positivo: de('+'), negativo: de('-') }
}

// ── riesgo ──────────────────────────────────────────────────────────────────

const nivelRiesgo = (p: number): 'bajo' | 'medio' | 'alto' | 'muy alto' => (p >= 6 ? 'muy alto' : p >= 4 ? 'alto' : p >= 2 ? 'medio' : 'bajo')

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

function analizarFamilia(filas: FilaK[], familia: FamiliaBurbuja, proximo: ProximoBurbuja | null, estabilidad: EstabilidadEquipoDTO): FamiliaBurbujaDTO {
  const { cerrados, abierta: ep, nCond } = episodios(filas, familia)
  const hist = historialDe(cerrados)
  const aplica = !proximo ? null : familia === 'total' ? true : proximo.condicion === (familia === 'local' ? 'L' : 'V')
  const out: FamiliaBurbujaDTO = {
    familia,
    partidosEnCondicion: nCond,
    actual: null,
    reventones: cerrados.slice(-MAX_REVENTONES_SALIDA),
    historial: hist,
    posicion: null,
    rival: null,
    riesgo: null,
  }
  if (!ep) return out
  const signo: SignoBurbuja = ep.signo > 0 ? '+' : '-'
  const kAbs = Math.abs(ep.k)
  out.actual = { signo, k: r2(ep.k), partidos: ep.partidos, kPico: r2(ep.kPico), desde: ep.desde, aplicaAlProximo: aplica }
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

  let puntos = 0
  const motivos: string[] = []
  if (kAbs >= medK) {
    puntos += 2
    motivos.push(`K ${r2(kAbs)} ya está en la mediana con la que revienta (${medK})`)
  } else if (kAbs >= base.kPico.min) {
    puntos += 1
    motivos.push(`ya reventó con menos K que la actual (mínimo ${base.kPico.min})`)
  } else {
    motivos.push(`K ${r2(kAbs)} por debajo de todo reventón previo (mínimo ${base.kPico.min})`)
  }
  if (kAbs >= base.kPico.max) {
    puntos += 1
    motivos.push(`nunca aguantó tanta K (máximo previo ${base.kPico.max})`)
  }
  const medP = base.partidos.mediana
  if (ep.partidos >= medP) {
    puntos += 1
    motivos.push(`${ep.partidos} partidos: en la mediana de racha (${medP}) o más`)
  } else {
    motivos.push(`${ep.partidos} partidos: por debajo de la mediana de racha (${medP})`)
  }
  if (ep.partidos >= base.partidos.max) {
    puntos += 1
    motivos.push(`nunca sostuvo una racha más larga (máximo previo ${Math.trunc(base.partidos.max)})`)
  }

  if (proximo && aplica) {
    const medN = base.nivelRival.mediana
    const nivelProx = proximo.nivelRival
    const enZona = signo === '+' ? nivelProx >= medN - ZONA_TOLERANCIA : nivelProx <= medN + ZONA_TOLERANCIA
    out.rival = { nivelProximo: r2(nivelProx), medianaReventon: medN, distancia: r2(nivelProx - medN), enZona }
    if (enZona) {
      puntos += 2
      motivos.push(
        `el próximo rival (${proximo.rival}, nivel ${r2(nivelProx)}) está en la zona donde suele ${signo === '+' ? 'reventar' : 'cortarse la racha'} (mediana ${medN})`,
      )
    } else {
      motivos.push(
        `el próximo rival (${proximo.rival}, nivel ${r2(nivelProx)}) queda ${signo === '+' ? 'por debajo' : 'por encima'} de la zona de reventón (mediana ${medN})`,
      )
    }
  } else if (proximo) {
    motivos.push('la familia no se mueve en el próximo partido (otra condición): el rival no puntúa')
  } else {
    motivos.push('sin próximo partido programado: el rival no puntúa')
  }

  const [confianza, confianzaMotivos] = confianzaDe(n, estabilidad)
  out.riesgo = { nivel: nivelRiesgo(puntos), puntos, motivos, confianza, confianzaMotivos }
  return out
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
    } else if (dias < DT_ASENTADO_DIAS) {
      subir('inestable')
      motivos.push(`DT ${ent.nombre} lleva ${dias} días: la historia de K es de otro cuerpo técnico`)
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
  const pal = mov === 1 ? 'movimiento' : 'movimientos'
  if (mov >= MOVIMIENTOS_INESTABLE) {
    subir('inestable')
    motivos.push(`${mov} ${pal} en ${rev.ventanaDias} días: plantel en obra`)
  } else if (mov >= MOVIMIENTOS_TRANSICION) {
    subir('en transición')
    motivos.push(`${mov} ${pal} en ${rev.ventanaDias} días`)
  } else {
    motivos.push(`${mov} ${pal} en ${rev.ventanaDias} días: plantel quieto`)
  }

  const bajas = plantilla.jugadores.filter((j) => !!j.baja).length
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

export function mandanDe(bin: number, proximo: ProximoBurbuja | null): BurbujasEquipoDTO['mandan'] {
  if (bin >= BIN_GLOBALES_ALTO || bin <= BIN_GLOBALES_BAJO) {
    return {
      tipo: 'globales',
      familias: ['total'],
      motivo: `nivel ${bin >= BIN_GLOBALES_ALTO ? 'alto' : 'bajo'} (bin ${bin}): pesan más las constantes globales`,
    }
  }
  const familias: FamiliaBurbuja[] = !proximo ? ['local', 'visita'] : [proximo.condicion === 'L' ? 'local' : 'visita']
  return {
    tipo: 'especificas',
    familias,
    motivo:
      `nivel medio (bin ${bin}): pesan más las constantes de la condición` +
      (!proximo ? '' : ` — el próximo es de ${proximo.condicion === 'L' ? 'local' : 'visita'}`),
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
  const familias = {} as Record<FamiliaBurbuja, FamiliaBurbujaDTO>
  for (const f of FAMILIAS) familias[f] = analizarFamilia(filas, f, ctx.proximo, estabilidad)
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
    aviso: AVISO_REVENTON,
  }
}
