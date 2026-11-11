import type { SemaforoElegido } from '../api/types'

/** EL SEMÁFORO DEL ELEGIDO (11/11/2026, usuario: «me apoyaré de ese semáforo»).
 *  Va al lado de la etiqueta del elegido: 🟢 nuestro 1X2 pegado a la casa (≤ 2
 *  pts en los tres) y el marcador declarado con el elegido · 🟡 falla una (el
 *  motivo en el title) · ⚪ sin cuotas o sin marcador. Calculado en el backend
 *  (`backend/analisis/semaforo.py`); el analista NO lo ve, a propósito. */
const ESTILO: Record<SemaforoElegido['estado'], { punto: string; color: string; texto: string }> = {
  confirma: { punto: '🟢', color: 'var(--up)', texto: 'confirma' },
  duda: { punto: '🟡', color: 'var(--mark)', texto: 'duda' },
  sinDato: { punto: '⚪', color: 'var(--t3)', texto: 'sin dato' },
}

export function titleSemaforo(s: SemaforoElegido): string {
  if (s.estado === 'confirma') {
    return `Semáforo verde: nuestro 1X2 a ≤ ${s.umbral} pts de la casa en los tres resultados${s.distancia != null ? ` (la mayor diferencia, ${s.distancia} pts)` : ''} y el marcador declarado con el elegido`
  }
  return `Semáforo ${s.estado === 'duda' ? 'amarillo' : 'sin dato'}: ${s.motivos.map((m) => m.detalle).join(' · ')}`
}

export function SemaforoChip({ s, corta = false }: { s?: SemaforoElegido | null; corta?: boolean }) {
  if (!s) return null
  const e = ESTILO[s.estado]
  return (
    <span title={titleSemaforo(s)} aria-label={titleSemaforo(s)}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: corta ? '1px 4px' : '1px 6px', borderRadius: 6, border: `1px solid color-mix(in oklch, ${e.color}, transparent 55%)`, font: `700 ${corta ? 8.5 : 9.5}px var(--sans)`, color: e.color, whiteSpace: 'nowrap', lineHeight: 1.3 }}>
      <span style={{ fontSize: corta ? 8 : 9 }}>{e.punto}</span>{!corta && e.texto}
    </span>
  )
}
