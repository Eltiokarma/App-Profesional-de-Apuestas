import type { FamiliaBurbujaDTO } from '../api/types'
import { PERIODO_HISTORIA, periodosDisponibles, referenciaReventon } from '../lib/reventonRef'

/** Qué referencia de reventón se dibuja en la gráfica: toda la historia (la
 *  que manda en el riesgo) o la misma medida acotada a un período. Un período
 *  sin base se puede elegir igual y la gráfica dice por qué no hay línea. */
export function PeriodoReventon({ fam, periodo, onPeriodo }: { fam: FamiliaBurbujaDTO | null | undefined; periodo: string; onPeriodo: (p: string) => () => void }) {
  if (!fam) return null
  const opciones = periodosDisponibles(fam)
  const ref = referenciaReventon(fam, periodo)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', marginTop: 6 }}>
      <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>referencia:</span>
      <div style={{ display: 'flex', flexWrap: 'wrap', padding: 2, borderRadius: 8, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
        {opciones.map((o) => {
          const sel = (periodo || PERIODO_HISTORIA) === o.clave
          return (
            <button key={o.clave} onClick={onPeriodo(o.clave)} title={o.sinDato || (o.clave === PERIODO_HISTORIA ? 'la calibrada con el backtest: la que manda en el riesgo' : 'las mismas medidas, acotadas a este período')}
              style={{ padding: '3px 8px', border: 0, borderRadius: 6, cursor: 'pointer', background: sel ? 'var(--bg1)' : 'transparent', color: sel ? 'var(--t1)' : o.sinDato ? 'var(--t3)' : 'var(--t2)', font: '600 9.5px var(--sans)' }}>
              {o.etiqueta}
            </button>
          )
        })}
      </div>
      {ref && (ref.sinBase
        ? <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>{ref.sinBase}: sin línea</span>
        : periodo !== PERIODO_HISTORIA && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>n {ref.n.pos}+ · {ref.n.neg}−{ref.n.pos + ref.n.neg < 3 ? ' · muestra corta' : ''}</span>)}
    </div>
  )
}
