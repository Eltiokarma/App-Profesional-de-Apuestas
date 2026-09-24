import type { ReactNode } from 'react'
import type { ConstanteCuotaDTO } from '../api/types'
import { KBarChart, type CuotaBar } from './KBarChart'
import type { Cond } from '../lib/kview'
import { loadConstantesCuota } from '../services/appdata'
import { useAsync } from '../services/useAsync'

export type CuotaCond = 'TODOS' | 'LOCAL' | 'VISITA'
/** Mercado a la vista: el 1X2 exacto, la doble oportunidad, o los dos. */
export type CuotaMercado = '1X2' | 'DC' | 'AMBOS' | 'FAV'

/** Estado de la vista de las gráficas de cuotas (lo controlan los botones). */
export interface CuotaVista {
  cond: CuotaCond
  mercado: CuotaMercado
  /** Últimos N partidos a dibujar (Infinity = toda la historia con cuota). */
  ventana: number
}

export const CUOTA_VISTA0: CuotaVista = { cond: 'TODOS', mercado: '1X2', ventana: Infinity }

/** Ventanas del selector VER de las cuotas (Infinity = toda la historia). */
export const CUOTA_VENTANAS: [number, string][] = [[8, '8'], [15, '15'], [30, '30'], [50, '50'], [Infinity, 'Todo']]

const MERCADOS: [CuotaMercado, string][] = [['1X2', '1X2'], ['DC', 'Doble op.'], ['AMBOS', 'Ambos'], ['FAV', 'Favorito']]

type FamKey = 'victoria' | 'empate' | 'derrota' | 'dc1x' | 'dc12' | 'dcX2' | 'favorito' | 'tapado'

interface Familia {
  key: FamKey
  label: string
  color: string
  soft: string
}

/** 1X2: el evento exacto. Una racha se rompe apenas cambia el resultado. */
const FAMILIAS_1X2: Familia[] = [
  { key: 'victoria', label: 'Racha de victorias', color: 'var(--up)', soft: 'var(--up-soft)' },
  { key: 'empate', label: 'Racha de empates', color: 'var(--mark)', soft: 'var(--mark-soft)' },
  { key: 'derrota', label: 'Racha de derrotas', color: 'var(--down)', soft: 'var(--down-soft)' },
]

/** Doble oportunidad: el evento acopla dos resultados, así que las rachas
 *  aguantan más y las burbujas se ven mejor. Siempre en la perspectiva del
 *  equipo (para el visitante, "1" es su victoria). */
const FAMILIAS_DC: Familia[] = [
  { key: 'dc1x', label: 'Racha 1X · no pierde', color: 'var(--up)', soft: 'var(--up-soft)' },
  { key: 'dc12', label: 'Racha 12 · no empata', color: 'var(--accent)', soft: 'var(--accent-soft)' },
  { key: 'dcX2', label: 'Racha X2 · no gana', color: 'var(--down)', soft: 'var(--down-soft)' },
]

/** Favorito y tapado (ROADMAP_BURBUJAS §3): la racha de victorias cerrando
 *  como favorito ((1/cuota)·nivel del rival) y la de victorias cerrando como
 *  NO favorito (cuota·nivel del rival). Cada una dibuja solo los partidos con
 *  ESE rol; revienta cuando, con ese rol, no gana. */
const FAMILIAS_FAV: Familia[] = [
  { key: 'favorito', label: 'Gana siendo favorito', color: 'var(--up)', soft: 'var(--up-soft)' },
  { key: 'tapado', label: 'Gana siendo tapado', color: 'var(--accent)', soft: 'var(--accent-soft)' },
]

export const familiasDe = (mercado: CuotaMercado): Familia[] =>
  mercado === '1X2' ? FAMILIAS_1X2 : mercado === 'DC' ? FAMILIAS_DC : mercado === 'FAV' ? FAMILIAS_FAV : [...FAMILIAS_1X2, ...FAMILIAS_DC]

/** Etiqueta del mercado para los títulos de las tarjetas. */
export const tituloMercado = (mercado: CuotaMercado) =>
  mercado === '1X2' ? 'rachas 1X2' : mercado === 'DC' ? 'rachas doble oportunidad' : mercado === 'FAV' ? 'rachas de favorito y tapado' : 'rachas 1X2 y doble oportunidad'

/** Cuotas K (§3.8): rachas 1X2 y de doble oportunidad de un equipo, con carga
 *  propia; los botones de vista viven fuera (compartibles entre dos instancias). */
export function RachasCuotas({ teamKey, vista, rol }: { teamKey: string; vista: CuotaVista; rol?: Cond }) {
  const cuota = useAsync(() => loadConstantesCuota(teamKey), teamKey)
  const { cond, mercado, ventana } = vista
  const condSuffix = cond === 'LOCAL' ? 'Local' : cond === 'VISITA' ? 'Visita' : ''
  const filas = (cuota.data ?? []).filter((r) => cond === 'TODOS' || (cond === 'LOCAL') === r.esLocal)
  // cada mercado tiene sus propios huecos: el partido sin cuota de ESE mercado
  // no entra en su gráfica (la racha lo saltó, dibujarlo mentiría)
  const barsFor = (fam: FamKey): CuotaBar[] => {
    const kk = (fam + condSuffix) as keyof ConstanteCuotaDTO['k']
    // favorito / tapado: solo las filas con ESE rol (y con nivel del rival);
    // la cuota que se muestra es la de victoria del equipo
    if (fam === 'favorito' || fam === 'tapado') {
      const rol = fam === 'favorito'
      return filas
        .filter((r) => r.favorito === rol && r.nivelRival != null)
        .map((r) => ({ fecha: r.fecha, value: r.k[kk], burst: r.k[kk] === 0, cuota: r.cuota.victoria, res: r.resultado, esLocal: r.esLocal }))
        .slice(-ventana)
    }
    return filas
      .filter((r) => r.cuota[fam] != null)
      .map((r) => ({ fecha: r.fecha, value: r.k[kk], burst: r.k[kk] === 0, cuota: r.cuota[fam], res: r.resultado, esLocal: r.esLocal }))
      .slice(-ventana)
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
      {familiasDe(mercado).map((f) => (
        <KBarChart key={f.key} bars={barsFor(f.key)} color={f.color} soft={f.soft} title={f.label} rol={rol} cond={cond} />
      ))}
    </div>
  )
}

const BTN = { padding: '5px 10px', border: 0, borderRadius: 6, cursor: 'pointer', font: '600 10.5px var(--sans)' } as const

/** Botonera de la vista de las cuotas K: condición · mercado · ventana. La
 *  usan igual la página de Equipo y Burbujas (un solo estado por pantalla). */
export function ControlesCuotas({ vista, onChange }: { vista: CuotaVista; onChange: (v: CuotaVista) => void }) {
  const grupo = (hijos: ReactNode) => (
    <div style={{ display: 'flex', padding: 3, borderRadius: 9, background: 'var(--bg3)', border: '1px solid var(--line)' }}>{hijos}</div>
  )
  const btn = (activo: boolean, label: string, onClick: () => void, key: string) => (
    <button key={key} onClick={onClick} style={{ ...BTN, background: activo ? 'var(--bg)' : 'transparent', color: activo ? 'var(--t1)' : 'var(--t2)' }}>{label}</button>
  )
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
      {grupo((['TODOS', 'LOCAL', 'VISITA'] as CuotaCond[]).map((c) => btn(vista.cond === c, c, () => onChange({ ...vista, cond: c }), c)))}
      {grupo(MERCADOS.map(([m, l]) => btn(vista.mercado === m, l, () => onChange({ ...vista, mercado: m }), m)))}
      <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', textTransform: 'uppercase', letterSpacing: '.4px' }}>Ver</span>
      {grupo(CUOTA_VENTANAS.map(([n, l]) => btn(vista.ventana === n, l, () => onChange({ ...vista, ventana: n }), String(n))))}
    </div>
  )
}
