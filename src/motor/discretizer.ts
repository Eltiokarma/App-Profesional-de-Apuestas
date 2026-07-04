// Fusión y discretización (§4) — port de discretizer_db.py.
import type { FusedK, KState } from './types'

/**
 * Fusión de constantes (§4.2): como k⁺ ≥ 0 y k⁻ ≤ 0 se resetean mutuamente,
 * la suma neta captura la dirección del momentum sin ambigüedad.
 * k > 0 racha positiva activa · k = 0 recién reseteado · k < 0 mala racha.
 */
export function fuse(k: KState): FusedK {
  return {
    k: k.pos + k.neg,
    kLocal: k.posLocal + k.negLocal,
    kVisita: k.posVisita + k.negVisita,
    golesAnotado: k.gA,
    golesRecibido: k.gR,
    golesLocalAnotado: k.gLA,
    golesLocalRecibido: k.gLR,
    golesVisitaAnotado: k.gVA,
    golesVisitaRecibido: k.gVR,
    kDc: k.dc,
    kDcLocal: k.dcLocal,
    kDcVisita: k.dcVisita,
    kVic1: k.vic1, kVic1Local: k.vic1Local, kVic1Visita: k.vic1Visita,
    kVic2: k.vic2, kVic2Local: k.vic2Local, kVic2Visita: k.vic2Visita,
    kVic3: k.vic3, kVic3Local: k.vic3Local, kVic3Visita: k.vic3Visita,
    kDer1: k.der1, kDer1Local: k.der1Local, kDer1Visita: k.der1Visita,
    kDer2: k.der2, kDer2Local: k.der2Local, kDer2Visita: k.der2Visita,
    kDer3: k.der3, kDer3Local: k.der3Local, kDer3Visita: k.der3Visita,
  }
}

/** Método B — bins fijos calibrados (Ley del Marcador v6, §4.1). */
const BIN_EDGES: { max: number; label: string }[] = [
  { max: 0.6, label: 'Sin datos' },
  { max: 1.3, label: 'Muy débil' },
  { max: 1.6, label: 'Débil' },
  { max: 1.9, label: 'Regular bajo' },
  { max: 2.1, label: 'Promedio bajo' },
  { max: 2.35, label: 'Promedio' },
  { max: 2.55, label: 'Promedio alto' },
  { max: 2.85, label: 'Fuerte' },
  { max: 3.2, label: 'Muy fuerte' },
  { max: Infinity, label: 'Élite' },
]

export function levelBin(level: number): { bin: number; label: string } {
  for (let i = 0; i < BIN_EDGES.length; i++) {
    if (level < BIN_EDGES[i].max) return { bin: i, label: BIN_EDGES[i].label }
  }
  return { bin: 9, label: 'Élite' }
}

/** Fallback lineal del método A (sin discretizer calibrado): (nivel−0.5)/3 × 9. */
export function levelBinUniform(level: number): number {
  const b = Math.round(((level - 0.5) / (3.5 - 0.5)) * 9)
  return Math.max(0, Math.min(9, b))
}
