// Helpers compartidos para visualizar las constantes K (Burbujas y página de Equipo).
import type { KCondKey, KTypeKey } from '../data/types'
import type { FusedK, KSnapshot } from '../motor/types'

/** Opciones del selector de ventana de la gráfica (Infinity = toda la historia). */
export const K_WINDOW_OPTS: [number, string][] = [[8, '8'], [15, '15'], [30, '30'], [50, '50'], [100, '100'], [Infinity, 'Todo']]

/** Grupos del selector de tipo de K (Resultado · Goles · Mercados · Márgenes),
 *  compartidos por Burbujas y la página de Equipo. */
export const K_TYPE_GROUPS: { label: string; opts: [KTypeKey, string][] }[] = [
  { label: 'Resultado', opts: [['res', 'K']] },
  { label: 'Goles', opts: [['ga', 'Anotados'], ['gr', 'Recibidos']] },
  { label: 'Mercados', opts: [['dc', 'Doble op.']] },
  {
    // burbujas de SEQUÍA por margen: crecen mientras no pasa, revientan el
    // día que el equipo gana (o pierde) por N o más (ver sequiaMargen)
    label: 'Margen · hasta que pasa',
    opts: [['vic1', 'Gana 1+'], ['vic2', 'Gana 2+'], ['vic3', 'Gana 3+'], ['der1', 'Pierde 1+'], ['der2', 'Pierde 2+'], ['der3', 'Pierde 3+']],
  },
]

export const FUSED_KEY: Record<KTypeKey, Record<KCondKey, keyof FusedK>> = {
  res: { total: 'k', local: 'kLocal', visita: 'kVisita' },
  ga: { total: 'golesAnotado', local: 'golesLocalAnotado', visita: 'golesVisitaAnotado' },
  gr: { total: 'golesRecibido', local: 'golesLocalRecibido', visita: 'golesVisitaRecibido' },
  dc: { total: 'kDc', local: 'kDcLocal', visita: 'kDcVisita' },
  vic1: { total: 'kVic1', local: 'kVic1Local', visita: 'kVic1Visita' },
  vic2: { total: 'kVic2', local: 'kVic2Local', visita: 'kVic2Visita' },
  vic3: { total: 'kVic3', local: 'kVic3Local', visita: 'kVic3Visita' },
  der1: { total: 'kDer1', local: 'kDer1Local', visita: 'kDer1Visita' },
  der2: { total: 'kDer2', local: 'kDer2Local', visita: 'kDer2Visita' },
  der3: { total: 'kDer3', local: 'kDer3Local', visita: 'kDer3Visita' },
}

/** Tipos "hacia abajo": la racha alta es desfavorable (goles recibidos, y las
 *  sequías de victoria: «sin ganar por N+» es mala señal; «sin perder por N+»
 *  va hacia arriba). */
const DOWN_TYPES = new Set<KTypeKey>(['gr', 'vic1', 'vic2', 'vic3'])

/** Valor con signo de display: los tipos desfavorables se pintan en negativo. */
export const signedVal = (kType: KTypeKey, v: number) => (DOWN_TYPES.has(kType) ? -v : v)

/** Umbral de margen de cada familia: gana/pierde por N o más. */
const MARGEN: Record<string, { signo: 1 | -1; n: number }> = {
  vic1: { signo: 1, n: 1 }, vic2: { signo: 1, n: 2 }, vic3: { signo: 1, n: 3 },
  der1: { signo: -1, n: 1 }, der2: { signo: -1, n: 2 }, der3: { signo: -1, n: 3 },
}

/** ¿Este marcador revienta la burbuja de la familia? (ganó / perdió por N o más) */
export function margenPasa(kType: KTypeKey, gf: number, ga: number): boolean {
  const m = MARGEN[kType]
  return !!m && m.signo * (gf - ga) >= m.n
}

/** Aporte q por partido de las burbujas de margen: el nivel del rival si la
 *  burbuja crece (el margen NO pasó), 0 si revienta. Con signo de display:
 *  «hasta ganar por N+» va hacia abajo, «hasta perder por N+» hacia arriba. */
export function marginQ(kType: KTypeKey, gf: number, ga: number, rivalLevel: number): number {
  if (!MARGEN[kType] || margenPasa(kType, gf, ga)) return 0
  return MARGEN[kType].signo === 1 ? -rivalLevel : rivalLevel
}

/**
 * Las familias de margen como BURBUJAS DE SEQUÍA (pedido del usuario, 23/09):
 * la de «Gana 2+» crece con el nivel del rival cada partido en que el equipo NO
 * gana por 2 o más goles y revienta (vuelve a 0) el día que lo hace; «Pierde
 * 2+» igual con las derrotas. Las variantes local/visita solo se mueven en su
 * condición. Reemplaza en la vista los kVic/kDer del motor (rachas de margen
 * EXACTO repetido, que casi nunca pasan de un partido y se leían como picos
 * sueltos); el motor y el contrato no cambian, esto se deriva de los goles y
 * del nivel del rival de cada fila. La historia arranca en 0 en la primera
 * fila cargada.
 */
export function sequiaMargen(snaps: KSnapshot[]): KSnapshot[] {
  const acc: Record<string, number> = {}
  return snaps.map((s) => {
    const fused = { ...s.fused }
    for (const kType of Object.keys(MARGEN) as KTypeKey[]) {
      const pasa = margenPasa(kType, s.gf, s.ga)
      const claves = FUSED_KEY[kType]
      for (const cond of ['total', 'local', 'visita'] as KCondKey[]) {
        const k = claves[cond]
        const mueve = cond === 'total' || (cond === 'local') === s.isLocal
        if (mueve) acc[k] = pasa ? 0 : (acc[k] ?? 0) + s.rivalLevel
        ;(fused as Record<string, number>)[k] = acc[k] ?? 0
      }
    }
    return { ...s, fused }
  })
}

/** true para las 6 familias de márgenes (§3.7). */
export const isMargin = (kType: KTypeKey) => kType.startsWith('vic') || kType.startsWith('der')

export const fmtK = (v: number) => (Math.abs(v) >= 20 ? v.toFixed(0) : v.toFixed(1))
export const signFmt = (v: number) => (v > 0 ? '+' + fmtK(v) : fmtK(v))

export function binBadge(bin: number): { color: string; soft: string } {
  if (bin >= 8) return { color: 'var(--up)', soft: 'var(--up-soft)' }
  if (bin >= 6) return { color: 'var(--accent)', soft: 'var(--accent-soft)' }
  if (bin >= 4) return { color: 'var(--mark)', soft: 'var(--mark-soft)' }
  if (bin >= 1) return { color: 'var(--down)', soft: 'var(--down-soft)' }
  return { color: 'var(--t3)', soft: 'var(--bg3)' }
}

/** Racha activa: partidos desde el último reseteo de la K seleccionada. */
export function streakLen(snaps: KSnapshot[], key: keyof FusedK): number {
  let n = 0
  for (let i = snaps.length - 1; i >= 0 && snaps[i].fused[key] !== 0; i--) n++
  return n
}

/** Condición de referencia de las etiquetas de una gráfica: manda el toggle
 *  cuando es específico (la serie solo se mueve en esa condición, y etiquetar
 *  puntos atenuados confunde); en 'total' manda el rol del equipo que se
 *  analiza (Local/Visitante del partido) y, sin él, la del último partido. */
export function condEtiquetas(
  kCond: KCondKey | 'TODOS' | 'LOCAL' | 'VISITA',
  rol: Cond | undefined,
  ultimoEsLocal: boolean,
): Cond {
  const c = kCond.toLowerCase()
  if (c === 'local') return 'local'
  if (c === 'visita') return 'visita'
  return rol ?? (ultimoEsLocal ? 'local' : 'visita')
}

export type Cond = 'local' | 'visita'

/**
 * Los puntos que llevan VALOR VISIBLE en las gráficas (índices, en orden):
 *   1. el último partido,
 *   2. el último de la condición que se analiza (local o visitante),
 *   3. el penúltimo de esa condición.
 * Si el valor de un candidato repite uno ya elegido —empezando por el caso
 * típico: el último partido ya era de esa condición— se recorre un punto hacia
 * atrás hasta dar con uno distinto: tres etiquetas iguales apiladas no dicen
 * nada. Devuelve entre 1 y 3 índices (menos si la historia no da para más).
 */
export function puntosEtiquetados(
  n: number,
  esCond: (i: number) => boolean,
  etiqueta: (i: number) => string,
): number[] {
  if (n <= 0) return []
  const elegidos = [n - 1]
  for (let i = n - 1; i >= 0 && elegidos.length < 3; i--) {
    if (!esCond(i)) continue
    if (elegidos.some((j) => etiqueta(j) === etiqueta(i))) continue
    elegidos.push(i)
  }
  return elegidos
}

/** Último aporte q a la K seleccionada (último partido de la condición). */
export function lastQ(snaps: KSnapshot[], kType: KTypeKey, kCond: KCondKey): number | null {
  for (let i = snaps.length - 1; i >= 0; i--) {
    const s = snaps[i]
    if (kCond === 'local' && !s.isLocal) continue
    if (kCond === 'visita' && s.isLocal) continue
    if (kType === 'ga') return s.q.golesAnotado
    if (kType === 'gr') return s.q.golesRecibido
    if (kType === 'dc') return s.q.dc
    if (isMargin(kType)) return marginQ(kType, s.gf, s.ga, s.rivalLevel)
    return s.isLocal ? s.q.local : s.q.visita
  }
  return null
}
