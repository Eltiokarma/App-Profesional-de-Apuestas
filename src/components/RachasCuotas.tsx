import type { ConstanteCuotaDTO } from '../api/types'
import { KBarChart, type CuotaBar } from './KBarChart'
import { loadConstantesCuota } from '../services/appdata'
import { useAsync } from '../services/useAsync'

export type CuotaCond = 'TODOS' | 'LOCAL' | 'VISITA'

const CUOTA_FAMILIES = [
  { key: 'victoria', label: 'victorias', color: 'var(--up)', soft: 'var(--up-soft)' },
  { key: 'empate', label: 'empates', color: 'var(--mark)', soft: 'var(--mark-soft)' },
  { key: 'derrota', label: 'derrotas', color: 'var(--down)', soft: 'var(--down-soft)' },
] as const

/** Cuotas K (§3.8): rachas 1X2 de un equipo con carga propia; el toggle
 *  TODOS/LOCAL/VISITA vive fuera (compartible entre dos instancias). */
export function RachasCuotas({ teamKey, cond }: { teamKey: string; cond: CuotaCond }) {
  const cuota = useAsync(() => loadConstantesCuota(teamKey), teamKey)
  const condSuffix = cond === 'LOCAL' ? 'Local' : cond === 'VISITA' ? 'Visita' : ''
  const cuotaRows = (cuota.data ?? []).filter(
    (r) => r.cuota.victoria != null && (cond === 'TODOS' || (cond === 'LOCAL') === r.esLocal),
  )
  const barsFor = (fam: 'victoria' | 'empate' | 'derrota'): CuotaBar[] => {
    const kk = (fam + condSuffix) as keyof ConstanteCuotaDTO['k']
    return cuotaRows.map((r) => ({ fecha: r.fecha, value: r.k[kk], burst: r.k[kk] === 0, cuota: r.cuota[fam], res: r.resultado }))
  }

  if (cuota.loading) return <div className="sad-sk" style={{ height: 150, marginTop: 10 }} />
  if (cuota.error)
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '18px 0' }}>
        <span style={{ font: '500 11px var(--mono)', color: 'var(--down)' }}>No se pudieron cargar las cuotas: {cuota.error}</span>
        <button onClick={cuota.reload} style={{ padding: '4px 10px', border: '1px solid var(--line)', borderRadius: 7, cursor: 'pointer', background: 'var(--bg3)', color: 'var(--t1)', font: '600 10.5px var(--sans)' }}>Reintentar</button>
      </div>
    )
  if (!cuota.data || !cuota.data.length)
    return (
      <div style={{ font: '500 11px var(--mono)', color: 'var(--t3)', padding: '18px 0', textAlign: 'center' }}>
        Sin datos de cuotas 2026 para este equipo (o modo mock).
      </div>
    )
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
      {CUOTA_FAMILIES.map((f) => (
        <KBarChart key={f.key} bars={barsFor(f.key)} color={f.color} soft={f.soft} title={`Racha de ${f.label}`} />
      ))}
    </div>
  )
}
