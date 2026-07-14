import type { SadStore } from '../store'
import type { SectionKey } from '../data/types'
import { CONFIG } from '../config'

export function BottomNav({ store }: { store: SadStore }) {
  const { s } = store
  const navF = (k: SectionKey) => (s.section === k ? 'var(--t1)' : 'var(--t2)')
  const skillsBadge = s.history.length || ''
  // Skills es contenido simulado: solo tiene sentido en la demo local — en
  // producción quedaba un botón "vacío" que confundía (el EFE va en Análisis)
  const conSkills = CONFIG.dataSource === 'mock'
  const btn: React.CSSProperties = { flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, border: 0, background: 'transparent', cursor: 'pointer', padding: '4px 0' }

  return (
    // safe-area: en iPhone la franja del gesto de inicio tapaba los botones
    <nav style={{ flexShrink: 0, display: 'flex', background: 'var(--bg1)', borderTop: '1px solid var(--line)', padding: '7px 6px calc(10px + env(safe-area-inset-bottom, 0px))' }}>
      <button onClick={store.go('partidos')} style={{ ...btn, color: navF('partidos') }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M8 3v4M16 3v4M3 11h18" /></svg>
        <span style={{ font: '600 10px var(--sans)' }}>Partidos</span>
      </button>
      <button onClick={store.go('cuotas')} style={{ ...btn, color: navF('cuotas') }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 17l6-6 4 4 8-8" /><path d="M16 7h5v5" /></svg>
        <span style={{ font: '600 10px var(--sans)' }}>Cuotas</span>
      </button>
      <button onClick={store.go('burbujas')} style={{ ...btn, color: navF('burbujas') }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="7.5" cy="9" r="3.4" opacity=".9" /><circle cx="16.5" cy="7.5" r="2.2" opacity=".55" /><circle cx="14.5" cy="16" r="4" opacity=".8" /></svg>
        <span style={{ font: '600 10px var(--sans)' }}>Burbujas</span>
      </button>
      <button onClick={store.go('analisis')} style={{ ...btn, color: navF('analisis') }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" opacity=".55" /><path d="M12 3v2M21 12h-2M12 21v-2M3 12h2" /></svg>
        <span style={{ font: '600 10px var(--sans)' }}>Análisis</span>
      </button>
      {conSkills && (
        <button onClick={store.go('skills')} style={{ ...btn, color: navF('skills'), position: 'relative' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5l1.7 4.6 4.6 1.7-4.6 1.7L12 15.1l-1.7-4.6L5.7 8.8l4.6-1.7z" /><path d="M18.5 14l.9 2.4 2.4.9-2.4.9-.9 2.4-.9-2.4-2.4-.9 2.4-.9z" opacity=".7" /></svg>
          <span style={{ font: '600 10px var(--sans)' }}>Skills</span>
          {skillsBadge !== '' && (
            <span style={{ position: 'absolute', top: -1, left: '50%', marginLeft: 6, minWidth: 15, height: 15, padding: '0 4px', borderRadius: 8, background: 'var(--accent)', color: '#fff', font: '700 9px var(--mono)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{skillsBadge}</span>
          )}
        </button>
      )}
      <button onClick={store.go('estadisticas')} style={{ ...btn, color: navF('estadisticas') }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M5 21V11M12 21V4M19 21v-8" /><path d="M3 21h18" /></svg>
        <span style={{ font: '600 10px var(--sans)' }}>Stats</span>
      </button>
    </nav>
  )
}
