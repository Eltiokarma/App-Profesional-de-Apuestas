import type { SadStore } from '../store'
import type { MatchView } from '../lib/view'
import { TeamSearch } from './TeamSearch'

interface Props {
  store: SadStore
  mv: MatchView | null
  liveBadge: boolean
  liveMinute: number
  liveScore: string
}

export function DesktopHeader({ store, mv, liveBadge, liveMinute, liveScore }: Props) {
  return (
    <header style={{ height: 74, flexShrink: 0, background: 'var(--bg1)', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', padding: '0 22px', gap: 18, position: 'relative', zIndex: 30 }}>
      {mv ? (
        <button onClick={store.go('partidos')} title="Ver partidos" style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'transparent', border: 0, cursor: 'pointer', padding: '6px 8px', borderRadius: 12, textAlign: 'left' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ width: 32, height: 32, borderRadius: '50%', background: mv.homeColor, color: mv.homeFg, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 12px var(--mono)', boxShadow: '0 0 0 2px var(--bg1),0 0 0 3px var(--line)' }}>{mv.homeShort}</span>
            <span style={{ font: '700 15px var(--sans)', color: 'var(--t1)' }}>{mv.homeName}</span>
          </div>
          <span style={{ font: '600 12px var(--mono)', color: 'var(--t3)' }}>vs</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ font: '700 15px var(--sans)', color: 'var(--t1)' }}>{mv.awayName}</span>
            <span style={{ width: 32, height: 32, borderRadius: '50%', background: mv.awayColor, color: mv.awayFg, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 12px var(--mono)', boxShadow: '0 0 0 2px var(--bg1),0 0 0 3px var(--line)' }}>{mv.awayShort}</span>
          </div>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: 2 }}><path d="M6 9l6 6 6-6" /></svg>
        </button>
      ) : null}
      {mv && (
        <>
          <div style={{ height: 34, width: 1, background: 'var(--line)' }}></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ font: '600 11px var(--mono)', color: 'var(--accent)', letterSpacing: '.4px' }}>{mv.league}</span>
            </div>
            <div style={{ font: '500 11.5px var(--mono)', color: 'var(--t3)' }}>{mv.date} · {mv.venue}</div>
          </div>
          {liveBadge && (
            <div style={{ marginLeft: 6, display: 'flex', alignItems: 'center', gap: 8, padding: '6px 11px', borderRadius: 8, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)', whiteSpace: 'nowrap', flexShrink: 0 }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite', flexShrink: 0 }}></span>
              <span style={{ font: '700 11px var(--mono)', color: 'var(--down)', letterSpacing: '.6px' }}>LIVE {liveMinute}'</span>
              <span style={{ font: '700 13px var(--mono)', color: 'var(--t1)' }}>{liveScore}</span>
            </div>
          )}
        </>
      )}
      {!mv && <div style={{ font: '600 14px var(--sans)', color: 'var(--t2)' }}>Ningún partido seleccionado</div>}

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 10 }}>
        <button onClick={store.toggleMobile} title="Vista móvil" style={{ width: 40, height: 40, borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg2)', color: 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="6.5" y="2.5" width="11" height="19" rx="2.5" /><path d="M11 18.5h2" /></svg>
        </button>
        <TeamSearch store={store} width={250} />
      </div>
    </header>
  )
}
