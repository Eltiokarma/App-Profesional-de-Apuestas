import type { FamiliaBurbujaDTO, HistorialPeriodoDTO } from '../api/types'

/** La referencia de reventón que se dibuja sobre la gráfica de K, según el
 *  período elegido. 'historia' = toda la historia (la calibrada con el
 *  backtest, la que manda en el riesgo); cualquier otra clave toma las mismas
 *  medidas acotadas de `historialPorPeriodo`. Sin base en el período se dice,
 *  no se rellena con la global. */
export interface ReferenciaReventon {
  pos: number | null
  neg: number | null
  /** Texto corto para la etiqueta de la línea ('' para toda la historia). */
  etiqueta: string
  /** Desde dónde corre el período (YYYY-MM-DD) para marcarlo en la gráfica. */
  desde: string
  /** Por qué no hay línea para este período, o ''. */
  sinBase: string
  n: { pos: number; neg: number }
}

export const PERIODO_HISTORIA = 'historia'

export function periodosDisponibles(fam: FamiliaBurbujaDTO | null | undefined): { clave: string; etiqueta: string; sinDato: string }[] {
  const base = [{ clave: PERIODO_HISTORIA, etiqueta: 'toda la historia', sinDato: '' }]
  if (!fam?.historialPorPeriodo) return base
  return base.concat(fam.historialPorPeriodo.map((p) => ({ clave: p.clave, etiqueta: etiquetaCorta(p), sinDato: p.sinDato })))
}

export function etiquetaCorta(p: HistorialPeriodoDTO | { clave: string; etiqueta: string }): string {
  if (p.clave === 'temporada') return p.etiqueta.replace('temporada ', 'temp. ')
  if (p.clave === 'anio') return p.etiqueta
  if (p.clave === 'dt') {
    if (p.etiqueta === 'con el DT actual') return 'DT actual'
    return p.etiqueta.startsWith('con ') ? `DT ${p.etiqueta.slice(4).replace(/ \(desde .*\)$/, '')}` : p.etiqueta
  }
  if (p.clave.startsWith('ultimos')) return p.etiqueta.replace(' partidos', '')
  return p.etiqueta
}

export function referenciaReventon(fam: FamiliaBurbujaDTO | null | undefined, periodo: string): ReferenciaReventon | null {
  if (!fam) return null
  if (periodo === PERIODO_HISTORIA || !fam.historialPorPeriodo) {
    return {
      pos: fam.historial.positivo?.kPico.mediana ?? null,
      neg: fam.historial.negativo?.kPico.mediana ?? null,
      etiqueta: '', desde: '', sinBase: '',
      n: { pos: fam.historial.positivo?.n ?? 0, neg: fam.historial.negativo?.n ?? 0 },
    }
  }
  const per = fam.historialPorPeriodo.find((p) => p.clave === periodo)
  if (!per) return null
  const etiqueta = etiquetaCorta(per)
  if (per.sinDato) return { pos: null, neg: null, etiqueta, desde: '', sinBase: per.sinDato, n: { pos: 0, neg: 0 } }
  const sinBase = !per.positivo && !per.negativo ? `sin reventones en ${etiqueta}` : ''
  return {
    pos: per.positivo?.kPico.mediana ?? null,
    neg: per.negativo?.kPico.mediana ?? null,
    etiqueta, desde: per.desde, sinBase,
    n: { pos: per.positivo?.n ?? 0, neg: per.negativo?.n ?? 0 },
  }
}
