import type { SadStore } from '../store'

export function EmptyState({ store }: { store: SadStore }) {
  return (
    <div style={{ height: '100%', minHeight: 440, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 6 }}>
      <div style={{ width: 78, height: 78, borderRadius: 20, background: 'var(--bg2)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" /></svg>
      </div>
      <div style={{ font: '700 19px var(--sans)' }}>Selecciona un partido</div>
      <div style={{ font: '500 13px var(--sans)', color: 'var(--t2)', maxWidth: 340, lineHeight: 1.5 }}>Elige un fixture para cargar cuotas, constantes K, reportes y estadísticas del análisis pre-partido.</div>
      <button onClick={store.togglePicker} style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 8, padding: '11px 18px', borderRadius: 11, border: 0, cursor: 'pointer', background: 'var(--accent)', color: '#fff', font: '600 13px var(--sans)' }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14" /></svg>
        Elegir partido
      </button>
    </div>
  )
}

export function Skeleton() {
  return (
    <div>
      <div className="sad-sk" style={{ width: 240, height: 26, marginBottom: 20 }}></div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14, marginBottom: 18 }}>
        <div className="sad-sk" style={{ height: 118 }}></div>
        <div className="sad-sk" style={{ height: 118 }}></div>
        <div className="sad-sk" style={{ height: 118 }}></div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        <div className="sad-sk" style={{ height: 150 }}></div>
        <div className="sad-sk" style={{ height: 150 }}></div>
        <div className="sad-sk" style={{ height: 150 }}></div>
        <div className="sad-sk" style={{ height: 150 }}></div>
      </div>
    </div>
  )
}
