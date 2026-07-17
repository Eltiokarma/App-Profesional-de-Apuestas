import { loadApuestasSalidas } from '../services/appdata'
import { useAsync } from '../services/useAsync'

const MES_CORTO = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
const fmtFecha = (iso: string): string => {
  const d = new Date(iso)
  return isNaN(d.getTime()) ? '' : `${d.getDate()} ${MES_CORTO[d.getMonth()]}`
}

const RES = {
  1: { label: 'Ganó', color: 'var(--up)', soft: 'var(--up-soft)' },
  0: { label: 'Empató', color: 'var(--mark)', soft: 'var(--mark-soft)' },
  [-1]: { label: 'Perdió', color: 'var(--down)', soft: 'var(--down-soft)' },
} as const

/** Apuestas que SALIERON en los últimos partidos del equipo: qué 1X2 ocurrió
 *  y la cuota prepartido que lo pagaba — para leer la rentabilidad reciente.
 *  Solo datos reales de la ingesta: sin cuota capturada se dice "sin cuota
 *  registrada"; sin historial, un vacío honesto. Nada inventado. */
export function ApuestasSalidas({ teamKey, nombre, n = 3 }: { teamKey: string; nombre: string; n?: number }) {
  const apuestas = useAsync(() => loadApuestasSalidas(teamKey, n), teamKey + '|' + n)

  if (apuestas.loading) return <div className="sad-sk" style={{ height: 118 }} />
  if (apuestas.error)
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 4px' }}>
        <span style={{ font: '500 11px var(--mono)', color: 'var(--down)', flex: 1 }}>No se pudieron cargar las apuestas pasadas: {apuestas.error}</span>
        <button onClick={apuestas.reload} style={{ padding: '4px 10px', border: '1px solid var(--line)', borderRadius: 7, cursor: 'pointer', background: 'var(--bg3)', color: 'var(--t1)', font: '600 10.5px var(--sans)', flexShrink: 0 }}>Reintentar</button>
      </div>
    )
  const filas = apuestas.data ?? []
  if (!filas.length)
    return (
      <div style={{ padding: '14px 8px', textAlign: 'center', font: '500 11.5px var(--mono)', color: 'var(--t3)' }}>
        No se tiene ese dato: sin partidos pasados con cuota en la ingesta para {nombre}.
      </div>
    )
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
      {filas.map((a) => {
        const r = RES[a.resultado]
        return (
          <div key={a.fixtureId} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)', flexWrap: 'wrap' }}>
            <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', width: 46, flexShrink: 0 }}>{fmtFecha(a.fecha)}</span>
            <span style={{ padding: '2px 7px', borderRadius: 6, background: r.soft, color: r.color, font: '700 10.5px var(--mono)', flexShrink: 0 }}>{r.label}</span>
            <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 120, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {a.rival ? `vs ${a.rival}` : 'rival sin registrar'}
              <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginLeft: 6 }}>
                {a.condicion === 'Local' ? 'LOC' : 'VIS'}{a.marcador ? ' · ' + a.marcador : ''}
              </span>
            </span>
            {a.cuotaSalida != null ? (
              <span style={{ display: 'flex', alignItems: 'baseline', gap: 6, flexShrink: 0 }}>
                <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>pagó</span>
                <span style={{ font: '700 15px var(--mono)', color: r.color, fontVariantNumeric: 'tabular-nums' }}>{a.cuotaSalida.toFixed(2)}</span>
              </span>
            ) : (
              <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>sin cuota registrada</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
