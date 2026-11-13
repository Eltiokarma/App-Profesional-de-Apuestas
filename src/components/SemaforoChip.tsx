import type { SemaforoElegido } from '../api/types'

/** EL SEMÁFORO DEL ELEGIDO, POR LAS ESPINAS (13/11/2026; antes 11/11/2026).
 *  Dice dónde NO meter plata, no si hay value en la cuota: 🟢 la espina del
 *  elegido lo acompaña · 🟡 dice empate, o la del rival dice que sigue · 🔴 la
 *  espina del elegido dice que pierde: no apostar · ⚪ sin 1X2 o sin espina. El
 *  motivo va en el title. Calculado en el backend (`backend/analisis/semaforo.py`)
 *  con las espinas del parte; el analista NO lo ve, a propósito. */
const ESTILO: Record<SemaforoElegido['estado'], { punto: string; color: string; texto: string }> = {
  confirma: { punto: '🟢', color: 'var(--up)', texto: 'confirma' },
  duda: { punto: '🟡', color: 'var(--mark)', texto: 'duda' },
  noApostar: { punto: '🔴', color: 'var(--down)', texto: 'no apostar' },
  sinDato: { punto: '⚪', color: 'var(--t3)', texto: 'sin dato' },
}

const NOMBRE: Record<SemaforoElegido['estado'], string> = {
  confirma: 'verde', duda: 'amarillo', noApostar: 'rojo', sinDato: 'sin dato',
}

export function titleSemaforo(s: SemaforoElegido): string {
  if (s.estado === 'confirma') {
    return `Semáforo verde: la espina del elegido dice ${s.espinaElegido ?? 'que gana'}${s.espinaRival ? ` y la del rival ${s.espinaRival}` : ''}`
  }
  return `Semáforo ${NOMBRE[s.estado]}: ${s.motivos.map((m) => m.detalle).join(' · ')}`
}

export function SemaforoChip({ s, corta = false }: { s?: SemaforoElegido | null; corta?: boolean }) {
  if (!s) return null
  const e = ESTILO[s.estado] ?? ESTILO.sinDato
  return (
    <span title={titleSemaforo(s)} aria-label={titleSemaforo(s)}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: corta ? '1px 4px' : '1px 6px', borderRadius: 6, border: `1px solid color-mix(in oklch, ${e.color}, transparent 55%)`, font: `700 ${corta ? 8.5 : 9.5}px var(--sans)`, color: e.color, whiteSpace: 'nowrap', lineHeight: 1.3 }}>
      <span style={{ fontSize: corta ? 8 : 9 }}>{e.punto}</span>{!corta && e.texto}
    </span>
  )
}
