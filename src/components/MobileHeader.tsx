import type { SadStore } from '../store'
import type { MatchView } from '../lib/view'
import { TeamBadge } from './TeamBadge'

interface Props {
  store: SadStore
  mv: MatchView | null
  phonePreview: boolean
  liveBadge: boolean
  liveMinute: number
}

export function MobileHeader({ store, mv, phonePreview, liveBadge, liveMinute }: Props) {
  const isDark = store.s.theme === 'dark'
  return (
    <header style={{ flexShrink: 0, background: 'var(--bg1)', borderBottom: '1px solid var(--line)', padding: '10px 14px', display: 'flex', flexDirection: 'column', gap: 9, zIndex: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 30, height: 30, borderRadius: 8, background: 'linear-gradient(135deg,var(--accent),color-mix(in oklch,var(--accent),#000 22%))', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '800 14px var(--sans)', color: '#fff' }}>S</div>
        <div style={{ lineHeight: 1.05, flex: 1 }}>
          <div style={{ font: '800 14px var(--sans)', letterSpacing: '.5px' }}>SAD</div>
          <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)' }}>ANÁLISIS PRE-PARTIDO</div>
        </div>
        {phonePreview && (
          <button onClick={store.toggleMobile} title="Salir de vista móvil" style={{ width: 34, height: 34, borderRadius: 9, border: '1px solid var(--line)', background: 'var(--bg2)', color: 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="4" width="20" height="13" rx="2" /><path d="M8 21h8M12 17v4" /></svg>
          </button>
        )}
        <button onClick={store.toggleTheme} title="Tema" style={{ width: 34, height: 34, borderRadius: 9, border: '1px solid var(--line)', background: 'var(--bg2)', color: 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          {isDark ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.8A9 9 0 1111.2 3 7 7 0 0021 12.8z" /></svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4.2" /><path d="M12 2.5v2.5M12 19v2.5M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M2.5 12H5M19 12h2.5M4.6 19.4l1.8-1.8M17.6 6.4l1.8-1.8" /></svg>
          )}
        </button>
      </div>
      {mv ? (
        <button onClick={store.go('partidos')} style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '9px 11px', border: '1px solid var(--line)', borderRadius: 11, background: 'var(--bg2)', cursor: 'pointer', textAlign: 'left' }}>
          <TeamBadge logo={mv.homeLogo} short={mv.homeShort} color={mv.homeColor} fg={mv.homeFg} size={26} />
          <TeamBadge logo={mv.awayLogo} short={mv.awayShort} color={mv.awayColor} fg={mv.awayFg} size={26} style={{ marginLeft: -12, boxShadow: '0 0 0 2px var(--bg2)' }} />
          <span style={{ flex: 1, minWidth: 0 }}>
            <span style={{ display: 'block', font: '700 12.5px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{mv.homeName} vs {mv.awayName}</span>
            <span style={{ display: 'block', font: '500 10px var(--mono)', color: 'var(--t3)' }}>{mv.league} · {mv.date}</span>
          </span>
          {liveBadge && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '4px 8px', borderRadius: 7, background: 'var(--down-soft)', flexShrink: 0 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>
              <span style={{ font: '700 10px var(--mono)', color: 'var(--down)' }}>{liveMinute}'</span>
            </span>
          )}
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M6 9l6 6 6-6" /></svg>
        </button>
      ) : (
        <div style={{ font: '600 13px var(--sans)', color: 'var(--t2)', padding: '4px 2px' }}>Ningún partido seleccionado</div>
      )}
    </header>
  )
}
