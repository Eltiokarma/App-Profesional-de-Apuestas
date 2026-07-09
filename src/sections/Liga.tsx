import { useRef, useState } from 'react'
import { TEAMS } from '../data'
import type { Match } from '../data/types'
import type { LigaDTO } from '../api/types'
import { TeamBadge } from '../components/TeamBadge'
import { loadLiga } from '../services/appdata'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  ligaId: number
  isMobile: boolean
}

/** Página de liga: identidad (bandera/logo), clasificación y partidos, con temporadas pasadas. */
export function Liga({ store, ligaId, isMobile }: Props) {
  // selección de temporada ligada a la liga: al cambiar de liga vuelve a la más reciente
  const [sel, setSel] = useState<{ liga: number; temporada: number } | null>(null)
  const temporada = sel && sel.liga === ligaId ? sel.temporada : null
  const liga = useAsync(() => loadLiga(ligaId, temporada ?? undefined), `${ligaId}:${temporada ?? ''}`)
  const d = liga.data

  // la cabecera no debe parpadear al cambiar de temporada: conservar el último meta de esta liga
  const metaRef = useRef<LigaDTO | null>(null)
  if (d?.meta) metaRef.current = d.meta
  const meta = d?.meta ?? (metaRef.current?.id === ligaId ? metaRef.current : null)

  const nombre = meta?.nombre ?? `Liga ${ligaId}`
  const img = meta ? (meta.bandera ?? meta.logo) : null
  const temporadas = meta?.temporadas ?? []

  const filaPartido = (m: Match) => {
    const H = TEAMS[m.home]
    const A = TEAMS[m.away]
    const live = m.status === 'live'
    return (
      <button key={m.id} onClick={store.selectMatch(m)} style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '8px 10px', borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg)', cursor: 'pointer', textAlign: 'left' }}>
        <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 6 }}>
          <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', textAlign: 'right' }}>{H?.short ?? m.home}</span>
          <TeamBadge logo={H?.logo} short={H?.short ?? '?'} color={H?.color ?? 'var(--bg3)'} fg={H?.fg ?? 'var(--t2)'} size={20} />
        </span>
        <span style={{ width: 52, flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <span style={{ font: '700 12.5px var(--mono)', color: m.status === 'sched' ? 'var(--t2)' : 'var(--t1)', fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>
            {m.status === 'sched' ? m.min : m.score}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 3, font: '700 8px var(--mono)', color: live ? 'var(--down)' : 'var(--t3)', letterSpacing: '.3px' }}>
            {live && <span style={{ width: 4, height: 4, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>}
            {live ? m.min : m.date}
          </span>
        </span>
        <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
          <TeamBadge logo={A?.logo} short={A?.short ?? '?'} color={A?.color ?? 'var(--bg3)'} fg={A?.fg ?? 'var(--t2)'} size={20} />
          <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{A?.short ?? m.away}</span>
        </span>
      </button>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16, flexWrap: 'wrap' }}>
        {img ? (
          <img src={img} alt="" width={52} height={40} style={{ objectFit: 'contain', borderRadius: 6, flexShrink: 0 }} />
        ) : (
          <span style={{ width: 52, height: 40, borderRadius: 6, background: 'var(--bg3)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 13px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>⚽</span>
        )}
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>{nombre}</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 5, flexWrap: 'wrap' }}>
            {meta?.pais && (
              <span style={{ padding: '4px 10px', borderRadius: 7, background: 'var(--accent-soft)', color: 'var(--accent)', font: '700 10.5px var(--mono)', letterSpacing: '.3px' }}>{meta.pais}</span>
            )}
            {temporadas.length > 1 ? (
              <select
                value={temporada ?? temporadas[0]}
                onChange={(e) => setSel({ liga: ligaId, temporada: Number(e.target.value) })}
                title="Ver otra temporada"
                style={{ padding: '4px 8px', borderRadius: 7, border: '1px solid var(--line2)', background: 'var(--bg2)', color: 'var(--t1)', font: '600 11px var(--mono)', cursor: 'pointer' }}
              >
                {temporadas.map((t) => (
                  <option key={t} value={t}>Temporada {t}</option>
                ))}
              </select>
            ) : (
              meta?.temporada != null && (
                <span style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>Temporada {meta.temporada}</span>
              )
            )}
          </div>
        </div>
      </div>

      {liga.error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudo cargar la liga: {liga.error}</span>
          <button onClick={liga.reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)' }}>Reintentar</button>
        </div>
      )}
      {liga.loading && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'minmax(0,1fr) 320px', gap: 14 }}>
          <div className="sad-sk" style={{ height: 420 }}></div>
          <div className="sad-sk" style={{ height: 420 }}></div>
        </div>
      )}

      {!liga.loading && !liga.error && d && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'minmax(0,1fr) 320px', gap: 14 }}>
          {/* CLASIFICACIÓN */}
          <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)', alignSelf: 'start' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 2 }}>Clasificación</div>
            <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 12 }}>Calculada con los fixtures finalizados capturados</div>
            {d.tabla.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: '26px minmax(0,1fr) 34px 34px 34px 40px', gap: '0 6px', fontVariantNumeric: 'tabular-nums' }}>
                {(['#', 'Equipo', 'PJ', 'GF', 'GC', 'Pts'] as const).map((h, i) => (
                  <span key={h} style={{ font: '600 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px', padding: '2px 0 8px', textAlign: i >= 2 ? 'right' : 'left' }}>{h}</span>
                ))}
                {d.tabla.map((r) => (
                  <div key={r.equipoId} style={{ display: 'contents' }}>
                    <span style={{ font: '600 11.5px var(--mono)', color: r.posicion <= 4 ? 'var(--accent)' : 'var(--t3)', padding: '7px 0', borderTop: '1px solid var(--line)' }}>{r.posicion}</span>
                    <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', padding: '7px 0', borderTop: '1px solid var(--line)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.nombre}</span>
                    <span style={{ font: '500 11.5px var(--mono)', color: 'var(--t2)', padding: '7px 0', borderTop: '1px solid var(--line)', textAlign: 'right' }}>{r.partidosJugados}</span>
                    <span style={{ font: '500 11.5px var(--mono)', color: 'var(--t2)', padding: '7px 0', borderTop: '1px solid var(--line)', textAlign: 'right' }}>{r.golesFavor}</span>
                    <span style={{ font: '500 11.5px var(--mono)', color: 'var(--t2)', padding: '7px 0', borderTop: '1px solid var(--line)', textAlign: 'right' }}>{r.golesContra}</span>
                    <span style={{ font: '700 12px var(--mono)', color: 'var(--t1)', padding: '7px 0', borderTop: '1px solid var(--line)', textAlign: 'right' }}>{r.puntos}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: 12 }}>Sin fixtures finalizados capturados para calcular la tabla.</div>
            )}
          </section>

          <aside style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ font: '700 12px var(--sans)', marginBottom: 10 }}>Próximos partidos</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {d.proximos.map(filaPartido)}
                {d.proximos.length === 0 && <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: 8 }}>Sin partidos programados capturados.</div>}
              </div>
            </section>
            <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ font: '700 12px var(--sans)', marginBottom: 10 }}>Resultados recientes</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {d.recientes.map(filaPartido)}
                {d.recientes.length === 0 && <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: 8 }}>Sin resultados capturados.</div>}
              </div>
            </section>
          </aside>
        </div>
      )}
    </div>
  )
}
