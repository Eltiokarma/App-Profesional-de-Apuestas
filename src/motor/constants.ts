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
  vic1: 0, vic1Local: 0, vic1Visita: 0,
  vic2: 0, vic2Local: 0, vic2Visita: 0,
  vic3: 0, vic3Local: 0, vic3Visita: 0,
  der1: 0, der1Local: 0, der1Visita: 0,
  der2: 0, der2Local: 0, der2Visita: 0,
  der3: 0, der3Local: 0, der3Visita: 0,
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

  // Márgenes (§3.7): aporte plano nivel; solo el bucket del margen EXACTO del
  // signo de este partido acumula; los demás (mismo o distinto signo) resetean.
  // El empate deja gv = gd = 0 → resetea ambos signos.
  const gv = gf > ga ? Math.min(gf - ga, 3) : 0 // bucket ganado (1/2/3+); 0 si no ganó
  const gd = perdio ? Math.min(ga - gf, 3) : 0 // bucket perdido (1/2/3+); 0 si no perdió
  k.vic1 = gv === 1 ? prev.vic1 + nivel : 0
  k.vic2 = gv === 2 ? prev.vic2 + nivel : 0
  k.vic3 = gv === 3 ? prev.vic3 + nivel : 0
  k.der1 = gd === 1 ? prev.der1 + nivel : 0
  k.der2 = gd === 2 ? prev.der2 + nivel : 0
  k.der3 = gd === 3 ? prev.der3 + nivel : 0
  if (isLocal) {
    k.vic1Local = gv === 1 ? prev.vic1Local + nivel : 0
    k.vic2Local = gv === 2 ? prev.vic2Local + nivel : 0
    k.vic3Local = gv === 3 ? prev.vic3Local + nivel : 0
    k.der1Local = gd === 1 ? prev.der1Local + nivel : 0
    k.der2Local = gd === 2 ? prev.der2Local + nivel : 0
    k.der3Local = gd === 3 ? prev.der3Local + nivel : 0
  } // en visita conservan (ya copiados de prev)
  if (!isLocal) {
    k.vic1Visita = gv === 1 ? prev.vic1Visita + nivel : 0
    k.vic2Visita = gv === 2 ? prev.vic2Visita + nivel : 0
    k.vic3Visita = gv === 3 ? prev.vic3Visita + nivel : 0
    k.der1Visita = gd === 1 ? prev.der1Visita + nivel : 0
    k.der2Visita = gd === 2 ? prev.der2Visita + nivel : 0
    k.der3Visita = gd === 3 ? prev.der3Visita + nivel : 0
  }

  return { q, k }
}
