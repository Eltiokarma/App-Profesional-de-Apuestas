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

function baseTexto(s: SemaforoElegido, estado: SemaforoElegido['estado']): string {
  if (estado === 'confirma') {
    return `la espina del elegido dice ${s.espinaElegido ?? 'que gana'}${s.espinaRival ? ` y la del rival ${s.espinaRival}` : ''}`
  }
  return s.motivos.map((m) => m.detalle).join(' · ')
}

/** El porqué del color, en palabras. CALIBRADO POR RAZONES (25/11/2026): cuando
 *  el backend tiene el parte enriquecido, las razones previas del parte pesan
 *  (las que más se repetían en los verdes que perdimos) y pueden bajar un verde
 *  a amarillo o subir un amarillo que no confirman; el rojo se queda. */
export function titleSemaforo(s: SemaforoElegido): string {
  const base = s.estadoBase ?? s.estado
  const c = s.calibrado
  const partes = [`Semáforo ${NOMBRE[s.estado]}`]
  if (c?.cambio) {
    partes.push(s.estado === 'duda'
      ? `las espinas lo daban verde, pero pesan las razones en contra (${c.puntaje.toFixed(1)} sobre un corte de ${c.corte.toFixed(1)})`
      : `las espinas lo daban amarillo (${baseTexto(s, base)}), pero ninguna razón lo confirma`)
  } else {
    partes.push(baseTexto(s, base))
    if (c && base === 'noApostar') partes.push(c.confirmado ? 'las razones lo confirman' : 'las razones no lo confirman')
  }
  if (c?.contra.length) partes.push(`en contra: ${c.contra.map((r) => r.texto).join('; ')}`)
  if (c?.aFavor.length) partes.push(`a favor: ${c.aFavor.map((r) => r.texto).join('; ')}`)
  return partes.join(' · ')
}

export function SemaforoChip({ s, corta = false }: { s?: SemaforoElegido | null; corta?: boolean }) {
  if (!s) return null
  const e = ESTILO[s.estado] ?? ESTILO.sinDato
  return (
    <span title={titleSemaforo(s)} aria-label={titleSemaforo(s)}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: corta ? '1px 4px' : '1px 6px', borderRadius: 6, border: `1px solid color-mix(in oklch, ${e.color}, transparent 55%)`, font: `700 ${corta ? 8.5 : 9.5}px var(--sans)`, color: e.color, whiteSpace: 'nowrap', lineHeight: 1.3 }}>
      <span style={{ fontSize: corta ? 8 : 9 }}>{e.punto}</span>{!corta && e.texto}{s.calibrado?.cambio && <span aria-hidden>*</span>}
    </span>
  )
}
