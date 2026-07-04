import { useState } from 'react'
import { TEAMS } from '../data'
import type { Match, MatchStatus } from '../data/types'
import { TeamSearch } from '../components/TeamSearch'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  matches: Match[]
  loading: boolean
  error: string | null
  reload: () => void
  isMobile: boolean
}

type Filtro = 'todos' | MatchStatus

/** Pantalla inicial: todos los partidos capturados, agrupados por competición. */
export function Partidos({ store, matches, loading, error, reload, isMobile }: Props) {
  const [filtro, setFiltro] = useState<Filtro>('todos')
  const [texto, setTexto] = useState('')

  const norm = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  const t = norm(texto.trim())
  const visibles = matches.filter((m) => {
    if (filtro !== 'todos' && m.status !== filtro) return false
    if (!t) return true
    const H = TEAMS[m.home]
    const A = TEAMS[m.away]
    return norm(H?.name ?? '').includes(t) || norm(A?.name ?? '').includes(t)
  })

  const grupos: { comp: string; rows: Match[] }[] = []
  for (const m of visibles) {
    const g = grupos.find((x) => x.comp === m.comp)
    if (g) g.rows.push(m)
    else grupos.push({ comp: m.comp, rows: [m] })
  }

  const chips: { k: Filtro; label: string }[] = [
    { k: 'todos', label: 'Todos' },
    { k: 'live', label: 'En vivo' },
    { k: 'sched', label: 'Próximos' },
    { k: 'fin', label: 'Pasados' },
  ]
  const nLive = matches.filter((m) => m.status === 'live').length

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Partidos</h1>
          <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>
            Todos los partidos capturados · elige uno para analizarlo
            {nLive > 0 && <span style={{ color: 'var(--down)', font: '600 12px var(--mono)' }}> · {nLive} en vivo</span>}
          </p>
        </div>
        <TeamSearch store={store} width={isMobile ? '100%' : 260} />
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
          {chips.map((c) => (
            <button key={c.k} onClick={() => setFiltro(c.k)} style={{ padding: '7px 13px', border: 0, borderRadius: 7, cursor: 'pointer', background: filtro === c.k ? 'var(--bg3)' : 'transparent', color: filtro === c.k ? 'var(--t1)' : 'var(--t2)', font: '600 11.5px var(--sans)' }}>
              {c.label}
            </button>
          ))}
        </div>
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Filtrar por equipo…"
          style={{ flex: 1, minWidth: 160, maxWidth: 280, padding: '9px 12px', borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg2)', color: 'var(--t1)', font: '600 12px var(--sans)', outline: 'none' }}
        />
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudieron cargar los partidos: {error}</span>
          <button onClick={reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)' }}>Reintentar</button>
        </div>
      )}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div className="sad-sk" style={{ height: 64 }}></div>
          <div className="sad-sk" style={{ height: 64 }}></div>
          <div className="sad-sk" style={{ height: 64 }}></div>
          <div className="sad-sk" style={{ height: 64 }}></div>
        </div>
      )}

      {!loading &&
        grupos.map((grp) => (
          <section key={grp.comp} style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 2px 8px' }}>
              <span style={{ width: 5, height: 15, borderRadius: 2, background: 'var(--accent)' }}></span>
              <span style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>{grp.comp}</span>
              <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>{grp.rows.length}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {grp.rows.map((m) => {
                const H = TEAMS[m.home]
                const A = TEAMS[m.away]
                const live = m.status === 'live'
                const fin = m.status === 'fin'
                const activo = store.s.matchId === m.id
                return (
                  <button
                    key={m.id}
                    onClick={store.selectMatch(m)}
                    style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '13px 16px', borderRadius: 13, cursor: 'pointer', textAlign: 'left', background: activo ? 'var(--accent-soft)' : 'var(--bg2)', border: `1px solid ${activo ? 'color-mix(in oklch,var(--accent),transparent 55%)' : 'var(--line)'}` }}
                  >
                    <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 10 }}>
                      <span style={{ font: '600 13px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', textAlign: 'right' }}>{H?.name ?? m.home}</span>
                      <span style={{ width: 28, height: 28, borderRadius: '50%', background: H?.color ?? 'var(--bg3)', color: H?.fg ?? 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 9px var(--mono)', flexShrink: 0 }}>{H?.short ?? '?'}</span>
                    </span>
                    <span style={{ width: 74, flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
                      <span style={{ font: '700 16px var(--mono)', color: m.status === 'sched' ? 'var(--t2)' : 'var(--t1)', fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>
                        {m.status === 'sched' ? m.min : m.score}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4, font: '700 9px var(--mono)', color: live ? 'var(--down)' : fin ? 'var(--t3)' : 'var(--accent)', letterSpacing: '.3px' }}>
                        {live && <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>}
                        {live ? m.min : fin ? 'FIN' : 'PROX'}
                      </span>
                    </span>
                    <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ width: 28, height: 28, borderRadius: '50%', background: A?.color ?? 'var(--bg3)', color: A?.fg ?? 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 9px var(--mono)', flexShrink: 0 }}>{A?.short ?? '?'}</span>
                      <span style={{ font: '600 13px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{A?.name ?? m.away}</span>
                    </span>
                    {!isMobile && <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>{m.date}</span>}
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M9 6l6 6-6 6" /></svg>
                  </button>
                )
              })}
            </div>
          </section>
        ))}
      {!loading && !error && visibles.length === 0 && (
        <div style={{ font: '500 12.5px var(--sans)', color: 'var(--t3)', padding: 24, textAlign: 'center' }}>Sin partidos para este filtro.</div>
      )}
    </div>
  )
}
