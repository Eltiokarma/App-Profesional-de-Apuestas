// Motor de Constantes K (§3) — port de constants_calculator.py.
// Paso 1: valores instantáneos q* (materia prima).
// Paso 2: acumuladores de racha k* con reseteo al cambiar el signo.
import type { KState, QVals } from './types'

/** Multiplicador visitante (CalculationSettings.visitor_multiplier). */
export const VISITOR_MULTIPLIER = 1.4

/** Fallback de nivel del rival al ponderar q* (settings.py: default_level = 1.0). */
export const CONSTANTS_LEVEL_FALLBACK = 1.0

export const K0: KState = {
  pos: 0, neg: 0,
  posLocal: 0, negLocal: 0,
  posVisita: 0, negVisita: 0,
  gA: 0, gR: 0, gLA: 0, gLR: 0, gVA: 0, gVR: 0,
  dc: 0, dcLocal: 0, dcVisita: 0,
}

/** Valores instantáneos q* de un partido (§3.2). */
export function qValues(isLocal: boolean, gf: number, ga: number, nivel: number): QVals {
  const dif = Math.abs(gf - ga)
  const res = gf > ga ? 1 : gf === ga ? 0 : -1
  return {
    local: isLocal ? dif * res * nivel : null,
    visita: !isLocal ? VISITOR_MULTIPLIER * dif * res * nivel : null,
    negativo: res === -1 ? dif * res * nivel : 0,
    golesAnotado: gf * nivel,
    golesRecibido: -ga * nivel,
    // Doble Oportunidad (§3.6): 0 si perdió; empate aporta el mínimo 0.5·nivel
    // para que la racha "sin perder" crezca aunque no haya diferencia de goles.
    // Sin multiplicador visitante: la fórmula del roadmap es dif·nivel sin ×1.4.
    dc: res === -1 ? 0 : Math.max(dif * nivel, 0.5 * nivel),
  }
}

/**
 * Un partido de avance de los 12 acumuladores (§3.3). Regla general: acumulan
 * mientras el signo se mantiene y se resetean a 0 al cambiar (o en empate).
 * Los k local/visita SOLO se actualizan en su condición (si no, conservan valor);
 * k_goles_recibido acumula valor absoluto.
 */
export function stepK(prev: KState, isLocal: boolean, gf: number, ga: number, nivel: number): { q: QVals; k: KState } {
  const q = qValues(isLocal, gf, ga, nivel)
  const qAny = isLocal ? q.local : q.visita
  const k: KState = { ...prev }

  // k_positivo: también se resetea si q_any es null (goles nulos)
  k.pos = qAny != null && qAny > 0 ? prev.pos + qAny : 0
  k.neg = q.negativo < 0 ? prev.neg + q.negativo : 0

  if (isLocal) {
    k.posLocal = q.local != null && q.local > 0 ? prev.posLocal + q.local : 0
    k.negLocal = q.local != null && q.local < 0 ? prev.negLocal + q.local : 0
    k.gLA = q.golesAnotado > 0 ? prev.gLA + q.golesAnotado : 0
    k.gLR = q.golesRecibido < 0 ? prev.gLR + Math.abs(q.golesRecibido) : 0
  } // en partidos de visita conservan su valor anterior

  if (!isLocal) {
    k.posVisita = q.visita != null && q.visita > 0 ? prev.posVisita + q.visita : 0
    k.negVisita = q.visita != null && q.visita < 0 ? prev.negVisita + q.visita : 0
    k.gVA = q.golesAnotado > 0 ? prev.gVA + q.golesAnotado : 0
    k.gVR = q.golesRecibido < 0 ? prev.gVR + Math.abs(q.golesRecibido) : 0
  }

  k.gA = q.golesAnotado > 0 ? prev.gA + q.golesAnotado : 0
  k.gR = q.golesRecibido < 0 ? prev.gR + Math.abs(q.golesRecibido) : 0

  // Doble Oportunidad (§3.6): acumula mientras NO pierde (victoria/empate);
  // la derrota resetea. dcLocal/dcVisita solo se tocan en su condición (si no,
  // conservan valor), igual que los k local/visita de resultado.
  const perdio = gf < ga
  k.dc = perdio ? 0 : prev.dc + q.dc
  if (isLocal) k.dcLocal = perdio ? 0 : prev.dcLocal + q.dc
  if (!isLocal) k.dcVisita = perdio ? 0 : prev.dcVisita + q.dc

  return { q, k }
}
