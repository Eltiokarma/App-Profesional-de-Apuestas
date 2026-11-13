import type { LecturaListaPartido } from '../api/types'

/** LA LECTURA EN LA TARJETA DE PARTIDOS (13/11/2026, usuario: «tendría que estar
 *  al costado del semáforo… y los dos marcadores más probables, tres si nos da el
 *  tamaño»). Calculado en el backend (`backend/analisis/lista_partidos.py`):
 *  - ⚠ desconfiar: la alerta del elegido con la MISMA regla que la tira del parte
 *    y la Simulación (SOBRE-LA-CASA, BURBUJA-DE-UN-PARTIDO). No mueve el 1X2 y no es
 *    el semáforo: el semáforo mira las espinas; esta, la casa y la racha.
 *  - los marcadores más probables del modelo de goles (REVENTON §17): lectura del
 *    marcador, no una señal de apuesta. */

export function titleDesconfiar(d: NonNullable<LecturaListaPartido['desconfiar']>): string {
  return `Desconfiar del elegido: ${d.motivos.map((m) => m.detalle).join(' · ')}`
    + (d.lectura ? `. La lectura que restringe: ${d.lectura}` : '')
    + '. No mueve el 1X2 (se mide en la Simulación).'
}

export function DesconfiarChip({ l, corta = false }: { l?: LecturaListaPartido | null; corta?: boolean }) {
  const d = l?.desconfiar
  if (!d?.activa) return null
  const t = titleDesconfiar(d)
  return (
    <span title={t} aria-label={t}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: corta ? '1px 4px' : '1px 6px', borderRadius: 6, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch, var(--down), transparent 55%)', font: `700 ${corta ? 8.5 : 9.5}px var(--sans)`, color: 'var(--down)', whiteSpace: 'nowrap', lineHeight: 1.3 }}>
      ⚠{!corta && ' desconfiar'}
    </span>
  )
}

export function MarcadoresProbables({ l, n = 3, corta = false }: { l?: LecturaListaPartido | null; n?: number; corta?: boolean }) {
  const m = l?.marcadores
  if (!m || !m.masProbables.length) return null
  const lista = m.masProbables.slice(0, n)
  const t = 'Marcadores más probables (modelo de goles, REVENTON §17): '
    + m.masProbables.map((x) => `${x.marcador} ${Math.round(100 * x.prob)} %`).join(' · ')
    + '. Lectura del marcador, no señal de apuesta.'
    + (m.porVentana ? ' ⚠ el nivel que entra a los goles sale de una ventana poco fiable.' : '')
  return (
    <span title={t} aria-label={t}
      style={{ display: 'inline-flex', alignItems: 'baseline', gap: corta ? 3 : 5, font: `600 ${corta ? 8.5 : 9.5}px var(--mono)`, color: 'var(--t2)', whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums', lineHeight: 1.3 }}>
      {lista.map((x, i) => (
        <span key={x.marcador}>
          {i > 0 && <span style={{ color: 'var(--t3)', marginRight: corta ? 3 : 5 }}>·</span>}
          <b style={{ color: i === 0 ? 'var(--t1)' : 'var(--t2)' }}>{x.marcador}</b>
          {!corta && <span style={{ color: 'var(--t3)' }}> {Math.round(100 * x.prob)}%</span>}
        </span>
      ))}
      {m.porVentana && <span style={{ color: 'var(--mark)' }}>*</span>}
    </span>
  )
}
