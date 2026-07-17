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

/** Símbolo de condición: casa = jugó de local · avión = jugó de visitante. */
function CondIcon({ local }: { local: boolean }) {
  return (
    <span title={local ? 'Jugó de local' : 'Jugó de visitante'} style={{ display: 'inline-flex', verticalAlign: '-2px', marginRight: 5 }}>
      {local ? (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="var(--accent)"><path d="M3 11.2 12 3l9 8.2v9.3a1 1 0 0 1-1 1h-5.5v-6h-5v6H4a1 1 0 0 1-1-1z" /></svg>
      ) : (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="var(--t3)"><path d="M2.5 19.5 21.5 12 2.5 4.5l.01 5.83L15.5 12 2.51 13.67z" /></svg>
      )}
    </span>
  )
}

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
        // mercados extra que salieron: O/U 2.5 y Ambos marcan (BTTS)
        const extras = [
          { titulo: 'O/U 2.5', m: a.ou },
          { titulo: 'Ambos marcan', m: a.btts },
        ]
        return (
          <div key={a.fixtureId} style={{ display: 'flex', flexDirection: 'column', gap: 6, padding: '8px 10px', borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', width: 46, flexShrink: 0 }}>{fmtFecha(a.fecha)}</span>
              <span style={{ padding: '2px 7px', borderRadius: 6, background: r.soft, color: r.color, font: '700 10.5px var(--mono)', flexShrink: 0 }}>{r.label}</span>
              <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 120, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                <CondIcon local={a.condicion === 'Local'} />
                {a.rival ? `vs ${a.rival}` : 'rival sin registrar'}
                {a.marcador && <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginLeft: 6 }}>{a.marcador}</span>}
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
            {/* segunda línea: qué salió en O/U 2.5, BTTS y doble oportunidad con su cuota */}
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {extras.map((ex) => (
                <span key={ex.titulo} style={{ display: 'flex', alignItems: 'baseline', gap: 6, padding: '3px 8px', borderRadius: 7, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                  <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>{ex.titulo}</span>
                  {ex.m.salida == null ? (
                    <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>sin marcador registrado</span>
                  ) : (
                    <>
                      <span style={{ font: '600 10.5px var(--sans)', color: 'var(--t1)' }}>{ex.m.salida}</span>
                      {ex.m.cuota != null ? (
                        <span style={{ font: '700 12px var(--mono)', color: 'var(--accent)', fontVariantNumeric: 'tabular-nums' }}>{ex.m.cuota.toFixed(2)}</span>
                      ) : (
                        <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>sin cuota registrada</span>
                      )}
                    </>
                  )}
                </span>
              ))}
              {/* doble oportunidad: las DOS combinaciones que salieron */}
              <span style={{ display: 'flex', alignItems: 'baseline', gap: 6, padding: '3px 8px', borderRadius: 7, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>Doble op.</span>
                {a.dc.map((d, j) => (
                  <span key={d.sel} style={{ display: 'inline-flex', alignItems: 'baseline', gap: 4 }}>
                    {j > 0 && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>·</span>}
                    <span style={{ font: '600 10.5px var(--sans)', color: 'var(--t1)' }}>{d.sel}</span>
                    {d.cuota != null ? (
                      <span style={{ font: '700 12px var(--mono)', color: 'var(--accent)', fontVariantNumeric: 'tabular-nums' }}>{d.cuota.toFixed(2)}</span>
                    ) : (
                      <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>sin cuota</span>
                    )}
                  </span>
                ))}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
