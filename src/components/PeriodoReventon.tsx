import type { FamiliaBurbujaDTO } from '../api/types'
import { ETIQUETA_GRUPO, PERIODO_HISTORIA, grupoDe, periodosDisponibles, referenciaReventon, type GrupoPeriodo } from '../lib/reventonRef'

/** Qué referencia de reventón se dibuja en la gráfica: toda la historia (la
 *  que manda en el riesgo) o la misma medida acotada a un período. Un chip por
 *  grupo; temporada y año abren una segunda fila con todos los que hay en la
 *  historia (el vigente marcado). Un período sin base se puede elegir y la
 *  gráfica dice por qué no hay línea. */
export function PeriodoReventon({ fam, periodo, onPeriodo }: { fam: FamiliaBurbujaDTO | null | undefined; periodo: string; onPeriodo: (p: string) => () => void }) {
  if (!fam) return null
  const opciones = periodosDisponibles(fam)
  const actual = periodo || PERIODO_HISTORIA
  const grupoSel = grupoDe(actual)
  const grupos = (['historia', 'temporada', 'anio', 'dt', 'ultimos'] as GrupoPeriodo[]).filter((g) => opciones.some((o) => o.grupo === g))
  const delGrupo = (g: GrupoPeriodo) => opciones.filter((o) => o.grupo === g)
  // al tocar un grupo se elige su período vigente (la temporada / el año en curso)
  const claveInicial = (g: GrupoPeriodo) => (delGrupo(g).find((o) => o.vigente) ?? delGrupo(g)[0]).clave
  const anios = grupoSel === 'temporada' || grupoSel === 'anio' ? delGrupo(grupoSel) : []
  const ref = referenciaReventon(fam, actual)
  const chip = (sel: boolean, apagado: boolean): React.CSSProperties => ({
    padding: '3px 8px', border: 0, borderRadius: 6, cursor: 'pointer',
    background: sel ? 'var(--bg1)' : 'transparent', color: sel ? 'var(--t1)' : apagado ? 'var(--t3)' : 'var(--t2)', font: '600 9.5px var(--sans)',
  })
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 6 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
        <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>referencia:</span>
        <div style={{ display: 'flex', flexWrap: 'wrap', padding: 2, borderRadius: 8, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
          {grupos.map((g) => {
            const sel = grupoSel === g
            const sinDato = delGrupo(g).every((o) => o.sinDato)
            return (
              <button key={g} onClick={onPeriodo(claveInicial(g))}
                title={g === 'historia' ? 'la calibrada con el backtest: la que manda en el riesgo' : sinDato ? delGrupo(g)[0].sinDato : 'las mismas medidas, acotadas a este período'}
                style={chip(sel, sinDato)}>
                {ETIQUETA_GRUPO[g]}
              </button>
            )
          })}
        </div>
        {ref && (ref.sinBase
          ? <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>{ref.sinBase}: sin línea</span>
          : actual !== PERIODO_HISTORIA && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>{ref.etiqueta} · n {ref.n.pos}+ · {ref.n.neg}−{ref.n.pos + ref.n.neg < 3 ? ' · muestra corta' : ''}</span>)}
      </div>
      {anios.length > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>{grupoSel === 'temporada' ? 'temporada:' : 'año:'}</span>
          <div style={{ display: 'flex', flexWrap: 'wrap', padding: 2, borderRadius: 8, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
            {anios.map((o) => (
              <button key={o.clave} onClick={onPeriodo(o.clave)} title={o.vigente ? 'en curso' : undefined} style={chip(actual === o.clave, false)}>
                {o.etiqueta.replace(/^(temp\. |año )/, '')}{o.vigente ? ' ·' : ''}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
