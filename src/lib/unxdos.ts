// El 1X2 del motor desde μ_partido: espejo de backend/analisis/unxdos_motor.py.
// μ son PUNTOS esperados, no goles: no va en un Poisson. Logística calibrada
// sobre 51.254 partidos (MOTOR_SAD_EXTRACCION.md §5.6). Los dos lados corren
// contra scripts/casos_unxdos.json: cambiar un coeficiente en uno solo tumba
// el test.
import type { UnXDosMotorDTO } from '../api/types'

// [intercepto, d, d²] por clase, contra el empate
export const COEF_UNXDOS = {
  local: [0.29851, 0.44446, 0.03539],
  visita: [0.18515, -0.48092, 0.04911],
} as const

export const CALIBRACION_UNXDOS = {
  fecha: '2026-10-21',
  partidos: 51254,
  equipos: 707,
  desde: '2019-02-17',
  hasta: '2026-10-21',
  logLoss: 1.0512,
  logLossFrecuencia: 1.0707,
  logLossPoissonSobreMu: 1.059,
  acierto: 0.4647,
}

export const NOTA_UNXDOS =
  'probabilidades del MOTOR solo (nivel, rival y localía, μ v2): logística calibrada ' +
  'sobre 51.254 partidos del padrón 2019-2026. Es una de las tres fuentes del pronóstico, ' +
  'no el pronóstico: no ve once, forma, K ni mercado'

// round half-even como Python, para que los dos lados den el mismo decimal
function round1(v: number): number {
  const x = v * 10
  const f = Math.floor(x)
  const diff = x - f
  const r = Math.abs(diff - 0.5) < 1e-9 ? (f % 2 === 0 ? f : f + 1) : Math.round(x)
  return r / 10
}

export function probabilidadesUnXDos(
  muLocal: number | null,
  muVisita: number | null,
): { local: number; empate: number; visita: number } | null {
  if (muLocal == null || muVisita == null) return null
  const d = muLocal - muVisita
  const x = [1, d, d * d]
  const z = (b: readonly number[]) => Math.max(-30, Math.min(30, b.reduce((s, bi, i) => s + bi * x[i], 0)))
  const el = Math.exp(z(COEF_UNXDOS.local))
  const ev = Math.exp(z(COEF_UNXDOS.visita))
  const s = 1 + el + ev
  const local = round1((100 * el) / s)
  const empate = round1(100 / s)
  return { local, empate, visita: round1(100 - local - empate) }
}

export function unXDosDelPartido(muLocal: number | null, muVisita: number | null): UnXDosMotorDTO | null {
  const p = probabilidadesUnXDos(muLocal, muVisita)
  if (!p || muLocal == null || muVisita == null) return null
  return {
    ...p,
    d: Math.round((muLocal - muVisita) * 1e4) / 1e4,
    modelo: 'logistica-mu-v1',
    calibracion: CALIBRACION_UNXDOS,
    nota: NOTA_UNXDOS,
  }
}
