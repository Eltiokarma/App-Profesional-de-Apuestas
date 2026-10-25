import type { TramoConfianza } from '../api/types'

/** El tramo de confianza del 1X2 (la probabilidad que el parte le dio a su
 *  elegido). La MISMA regla que `lecciones.tramo_confianza` del backend: la
 *  tabla de Aprendizaje, la marca de Partidos y el veredicto del parte hablan
 *  de los mismos cuatro tramos. */
export function tramoConfianza(pct: number): TramoConfianza {
  return pct >= 60 ? '60+' : pct >= 50 ? '50-59' : pct >= 40 ? '40-49' : '<40'
}

/** Un color por tramo, de más a menos confianza: verde · azul · ámbar · gris. */
export const COLOR_TRAMO: Record<TramoConfianza, string> = {
  '60+': 'var(--up)',
  '50-59': 'var(--accent)',
  '40-49': 'var(--mark)',
  '<40': 'var(--t3)',
}

export const SEL_CORTA: Record<string, string> = { local: 'L', empate: 'E', visita: 'V' }
export const SEL_LARGA: Record<string, string> = { local: 'LOCAL', empate: 'EMPATE', visita: 'VISITA' }
