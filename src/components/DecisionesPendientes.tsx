import { useEffect, useState } from 'react'
import { CONFIG } from '../config'
import { SadApi } from '../api/sad'
import { llaveAdmin } from '../lib/admin'
import type { CausaIncidencia, IncidenciaDTO } from '../api/types'

/** Lo que el mantenimiento no decide solo (27/10/2026, pedido del usuario).
 *
 *  Antes llegaba como un informe largo que había que pegar en una conversación.
 *  Acá están las incidencias en `usuario` AGRUPADAS POR CAUSA (seis «once entre
 *  dos disparos» son una sola decisión), con la propuesta del mantenimiento, y
 *  en modo administrador (🔑) se aprueban o rechazan: aprobada, la implementa
 *  la próxima pasada; rechazada, queda «por diseño» con la nota. Sin nada que
 *  decidir no ocupa lugar. */
type Grupo = { clave: number; titulo: string; items: IncidenciaDTO[] }

function agrupar(items: IncidenciaDTO[], causas: CausaIncidencia[]): Grupo[] {
  const raizDe = new Map<number, CausaIncidencia>()
  for (const c of causas) for (const id of c.ids) raizDe.set(id, c)
  const grupos = new Map<number, Grupo>()
  for (const it of items) {
    const c = raizDe.get(it.id)
    const clave = c?.raiz ?? it.id
    const g = grupos.get(clave) ?? { clave, titulo: it.titulo, items: [] }
    g.items.push(it)
    grupos.set(clave, g)
  }
  // la más vieja primero: es la que más espera
  return [...grupos.values()].sort((a, b) => Math.min(...a.items.map((i) => i.id)) - Math.min(...b.items.map((i) => i.id)))
}

export function DecisionesPendientes({ isMobile }: { isMobile: boolean }) {
  const [grupos, setGrupos] = useState<Grupo[] | null>(null)
  const [aprobadas, setAprobadas] = useState(0)
  const [abierto, setAbierto] = useState(false)
  const [recarga, setRecarga] = useState(0)
  useEffect(() => {
    if (CONFIG.dataSource !== 'http') return
    let vivo = true
    // sin las familias (o sin las aprobadas) se pinta igual: cada incidencia, su grupo
    Promise.allSettled([SadApi.incidencias('usuario', 300), SadApi.causasIncidencias(), SadApi.incidencias('aprobada', 300)])
      .then(([u, c, a]) => {
        if (!vivo || u.status !== 'fulfilled') return
        setGrupos(agrupar(u.value.incidencias, c.status === 'fulfilled' ? c.value.causas : []))
        setAprobadas(a.status === 'fulfilled' ? a.value.incidencias.length : 0)
      })
    return () => { vivo = false }
  }, [recarga])
  if (!grupos || (grupos.length === 0 && aprobadas === 0)) return null

  const nInc = grupos.reduce((s, g) => s + g.items.length, 0)
  return (
    <section style={{ padding: isMobile ? '11px 13px' : '13px 16px', marginBottom: 14, borderRadius: 13, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px 10px', flexWrap: 'wrap' }}>
        <span style={{ font: '700 9.5px var(--mono)', color: grupos.length ? 'var(--mark)' : 'var(--t3)', letterSpacing: '.6px' }}>
          DECISIONES PENDIENTES
        </span>
        <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          {grupos.length} {grupos.length === 1 ? 'causa' : 'causas'} · {nInc} {nInc === 1 ? 'incidencia' : 'incidencias'}
        </span>
        {aprobadas > 0 && (
          <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
            {aprobadas} aprobada{aprobadas === 1 ? '' : 's'} esperando al mantenimiento
          </span>
        )}
        {grupos.length > 0 && (
          <button onClick={() => setAbierto((v) => !v)} style={{ marginLeft: 'auto', padding: '3px 9px', border: '1px solid var(--line)', borderRadius: 7, background: 'var(--bg)', color: 'var(--t2)', font: '600 10px var(--sans)', cursor: 'pointer' }}>
            {abierto ? 'ocultar' : 'ver'}
          </button>
        )}
      </div>
      {abierto && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr)', gap: 8, marginTop: 9 }}>
          {grupos.map((g) => <GrupoDecision key={g.clave} g={g} onHecho={() => setRecarga((n) => n + 1)} />)}
        </div>
      )}
    </section>
  )
}

function GrupoDecision({ g, onHecho }: { g: Grupo; onHecho: () => void }) {
  const [nota, setNota] = useState('')
  const [yendo, setYendo] = useState(false)
  const [error, setError] = useState('')
  const admin = !!llaveAdmin()
  // la propuesta más reciente del grupo es la que se decide
  const ultima = [...g.items].sort((a, b) => b.id - a.id)[0]
  const desde = g.items.map((i) => i.creadoEn).sort()[0]?.slice(0, 10)
  async function decidir(aprobar: boolean) {
    setYendo(true)
    setError('')
    try {
      for (const it of g.items) await SadApi.decidirIncidencia(it.id, aprobar, nota)
      onHecho()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudo guardar la decisión')
    } finally {
      setYendo(false)
    }
  }
  return (
    <div style={{ padding: '9px 11px', borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)', minWidth: 0 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', gap: '3px 8px' }}>
        <span style={{ font: '700 9px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>{ultima.area.toUpperCase()}</span>
        <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', minWidth: 0, overflowWrap: 'anywhere' }}>{g.titulo}</span>
        <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
          {g.items.map((i) => `#${i.id}`).join(' ')} · desde {desde}
        </span>
      </div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t2)', marginTop: 5, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
        {ultima.resolucion || 'sin propuesta escrita'}
      </div>
      {admin ? (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 7 }}>
          <input value={nota} onChange={(e) => setNota(e.target.value)} placeholder="nota (opcional)"
            style={{ flex: 1, minWidth: 150, padding: '5px 8px', borderRadius: 7, border: '1px solid var(--line)', background: 'var(--bg2)', color: 'var(--t1)', font: '500 11px var(--mono)' }} />
          <button onClick={() => decidir(true)} disabled={yendo}
            style={{ padding: '5px 11px', borderRadius: 7, border: 0, background: 'var(--up)', color: '#fff', font: '600 10.5px var(--sans)', cursor: 'pointer' }}>
            {yendo ? '…' : 'Aprobar'}
          </button>
          <button onClick={() => decidir(false)} disabled={yendo}
            style={{ padding: '5px 11px', borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', font: '600 10.5px var(--sans)', cursor: 'pointer' }}>
            Rechazar
          </button>
        </div>
      ) : (
        <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)', marginTop: 6 }}>Para decidir, entra en modo administrador (🔑).</div>
      )}
      {error && <div style={{ font: '600 10.5px var(--sans)', color: 'var(--down)', marginTop: 5 }}>{error}</div>}
    </div>
  )
}
