import type { SadStore } from '../store'
import type { SectionKey } from '../data/types'
import { CONFIG } from '../config'
import { useFeedStatus } from '../services/useFeedStatus'

export function Sidebar({ store }: { store: SadStore }) {
  const { s } = store
  const isDark = s.theme === 'dark'
  const navB = (k: SectionKey) => (s.section === k ? 'var(--accent-soft)' : 'transparent')
  const navF = (k: SectionKey) => (s.section === k ? 'var(--t1)' : 'var(--t2)')
  const skillsBadge = s.history.length || ''
  const feed = useFeedStatus()
  const feedColor = feed.checking ? 'var(--mark)' : feed.ok ? 'var(--up)' : 'var(--down)'
  const feedLabel = feed.mode === 'mock' ? 'MOTOR LOCAL · DEMO' : feed.checking ? 'CONECTANDO…' : feed.ok ? 'FEED CONECTADO' : 'SIN CONEXIÓN'
  const feedDetail =
    feed.mode === 'mock'
      ? 'fuente simulada · sin API externa'
      : feed.ok
        ? `API · ${feed.latencyMs ?? '—'}ms · ${feed.detail}`
        : CONFIG.apiBaseUrl.replace(/^https?:\/\//, '')

  return (
    <aside style={{ width: 228, flexShrink: 0, background: 'var(--bg1)', borderRight: '1px solid var(--line)', display: 'flex', flexDirection: 'column', padding: '18px 14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '4px 8px 20px' }}>
        <div style={{ width: 36, height: 36, borderRadius: 9, background: 'linear-gradient(135deg,var(--accent),color-mix(in oklch,var(--accent),#000 22%))', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '800 16px var(--sans)', color: '#fff', letterSpacing: '-.5px' }}>S</div>
        <div style={{ lineHeight: 1.05 }}>
          <div style={{ font: '800 16px var(--sans)', letterSpacing: '.5px' }}>SAD</div>
          <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px', marginTop: 2 }}>ANÁLISIS PRE-PARTIDO</div>
        </div>
      </div>

      <div style={{ font: '600 10px var(--mono)', color: 'var(--t3)', letterSpacing: '1px', padding: '6px 10px 8px' }}>MÓDULOS</div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <button onClick={store.go('partidos')} style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '11px 12px', border: 0, borderRadius: 10, cursor: 'pointer', background: navB('partidos'), color: navF('partidos'), font: '600 13.5px var(--sans)', textAlign: 'left', transition: 'background .14s,color .14s' }}>
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M8 3v4M16 3v4M3 11h18" /></svg>
          <span>Partidos</span>
        </button>
        <button onClick={store.go('cuotas')} style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '11px 12px', border: 0, borderRadius: 10, cursor: 'pointer', background: navB('cuotas'), color: navF('cuotas'), font: '600 13.5px var(--sans)', textAlign: 'left', transition: 'background .14s,color .14s' }}>
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 17l6-6 4 4 8-8" /><path d="M16 7h5v5" /></svg>
          <span>Cuotas</span>
          <span style={{ marginLeft: 'auto', width: 6, height: 6, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.4s infinite' }}></span>
        </button>
        <button onClick={store.go('burbujas')} style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '11px 12px', border: 0, borderRadius: 10, cursor: 'pointer', background: navB('burbujas'), color: navF('burbujas'), font: '600 13.5px var(--sans)', textAlign: 'left', transition: 'background .14s,color .14s' }}>
          <svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><circle cx="7.5" cy="9" r="3.4" opacity=".9" /><circle cx="16.5" cy="7.5" r="2.2" opacity=".55" /><circle cx="14.5" cy="16" r="4" opacity=".8" /></svg>
          <span>Burbujas</span>
          <span style={{ marginLeft: 'auto', font: '600 9px var(--mono)', color: 'var(--t3)' }}>K</span>
        </button>
        <button onClick={store.go('skills')} style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '11px 12px', border: 0, borderRadius: 10, cursor: 'pointer', background: navB('skills'), color: navF('skills'), font: '600 13.5px var(--sans)', textAlign: 'left', transition: 'background .14s,color .14s' }}>
          <svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5l1.7 4.6 4.6 1.7-4.6 1.7L12 15.1l-1.7-4.6L5.7 8.8l4.6-1.7z" /><path d="M18.5 14l.9 2.4 2.4.9-2.4.9-.9 2.4-.9-2.4-2.4-.9 2.4-.9z" opacity=".7" /></svg>
          <span>Skills</span>
          {skillsBadge !== '' && (
            <span style={{ marginLeft: 'auto', minWidth: 17, height: 17, padding: '0 5px', borderRadius: 9, background: 'var(--accent)', color: '#fff', font: '700 10px var(--mono)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{skillsBadge}</span>
          )}
        </button>
        <button onClick={store.go('estadisticas')} style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '11px 12px', border: 0, borderRadius: 10, cursor: 'pointer', background: navB('estadisticas'), color: navF('estadisticas'), font: '600 13.5px var(--sans)', textAlign: 'left', transition: 'background .14s,color .14s' }}>
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M5 21V11M12 21V4M19 21v-8" /><path d="M3 21h18" /></svg>
          <span>Estadísticas</span>
        </button>
      </nav>

      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div style={{ padding: 12, borderRadius: 11, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: feedColor, boxShadow: `0 0 8px ${feedColor}` }}></span>
            <span style={{ font: '600 11px var(--mono)', color: 'var(--t2)', letterSpacing: '.4px' }}>{feedLabel}</span>
          </div>
          <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', lineHeight: 1.5, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={feedDetail}>{feedDetail}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
          <button onClick={store.toggleTheme} title="Cambiar tema" style={{ width: 38, height: 38, flexShrink: 0, borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg2)', color: 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
            {isDark ? (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.8A9 9 0 1111.2 3 7 7 0 0021 12.8z" /></svg>
            ) : (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4.2" /><path d="M12 2.5v2.5M12 19v2.5M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M2.5 12H5M19 12h2.5M4.6 19.4l1.8-1.8M17.6 6.4l1.8-1.8" /></svg>
            )}
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, flex: 1, padding: '6px 8px', borderRadius: 10 }}>
            <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'var(--bg3)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 11px var(--mono)', color: 'var(--t2)' }}>MR</div>
            <div style={{ lineHeight: 1.15, minWidth: 0 }}>
              <div style={{ font: '600 12px var(--sans)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>M. Ríos</div>
              <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>Analista</div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
