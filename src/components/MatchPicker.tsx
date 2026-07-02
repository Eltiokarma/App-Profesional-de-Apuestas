import { TEAMS } from '../data'
import type { Match } from '../data/types'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  matches: Match[]
  current: Match | undefined
  pickerStyle: React.CSSProperties
}

export function MatchPicker({ store, matches, current, pickerStyle }: Props) {
  const groupMap: Record<string, Match[]> = {}
  matches.forEach((x) => {
    ;(groupMap[x.comp] = groupMap[x.comp] || []).push(x)
  })
  const matchGroups = Object.keys(groupMap).map((comp) => ({
    comp,
    count: groupMap[comp].length,
    rows: groupMap[comp].map((x) => {
      const HT = TEAMS[x.home]
      const AT = TEAMS[x.away]
      const live = x.status === 'live'
      const fin = x.status === 'fin'
      const sched = x.status === 'sched'
      const active = !!current && x.id === current.id
      return {
        id: x.id,
        match: x,
        homeName: HT.name, homeShort: HT.short, homeColor: HT.color, homeFg: HT.fg,
        awayName: AT.name, awayShort: AT.short, awayColor: AT.color, awayFg: AT.fg,
        centerTop: sched ? x.min : x.score,
        centerColor: sched ? 'var(--t2)' : 'var(--t1)',
        isLive: live,
        statusText: live ? x.min : fin ? 'FIN' : 'HOY',
        statusColor: live ? 'var(--down)' : fin ? 'var(--t3)' : 'var(--accent)',
        active,
        bg: active ? 'var(--accent-soft)' : 'transparent',
      }
    }),
  }))

  return (
    <>
      <div onClick={store.togglePicker} style={{ position: 'fixed', inset: 0, zIndex: 40 }}></div>
      <div style={pickerStyle}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 10px 10px' }}>
          <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', letterSpacing: '1px' }}>PARTIDOS · HOY</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, font: '600 10px var(--mono)', color: 'var(--down)' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>EN DIRECTO
          </span>
        </div>
        <div className="sad-scroll" style={{ display: 'flex', flexDirection: 'column', gap: 12, maxHeight: '62vh', overflowY: 'auto', paddingRight: 2 }}>
          {matchGroups.map((grp) => (
            <div key={grp.comp}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 8px 7px' }}>
                <span style={{ width: 5, height: 14, borderRadius: 2, background: 'var(--accent)' }}></span>
                <span style={{ font: '700 11px var(--sans)', color: 'var(--t1)', letterSpacing: '.2px', flex: 1 }}>{grp.comp}</span>
                <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>{grp.count}</span>
              </div>
              {grp.rows.map((row) => (
                <button key={row.id} onClick={store.selectMatch(row.match)} style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '9px 8px', border: 0, borderRadius: 9, cursor: 'pointer', background: row.bg, marginBottom: 1 }}>
                  <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8 }}>
                    <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', textAlign: 'right' }}>{row.homeName}</span>
                    <span style={{ width: 22, height: 22, borderRadius: '50%', background: row.homeColor, color: row.homeFg, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 8px var(--mono)', flexShrink: 0 }}>{row.homeShort}</span>
                  </span>
                  <span style={{ width: 58, flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                    <span style={{ font: '700 14px var(--mono)', color: row.centerColor, fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>{row.centerTop}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, font: '700 8.5px var(--mono)', color: row.statusColor, letterSpacing: '.3px' }}>
                      {row.isLive && <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>}
                      {row.statusText}
                    </span>
                  </span>
                  <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ width: 22, height: 22, borderRadius: '50%', background: row.awayColor, color: row.awayFg, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 8px var(--mono)', flexShrink: 0 }}>{row.awayShort}</span>
                    <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{row.awayName}</span>
                  </span>
                  {row.active && (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M20 6L9 17l-5-5" /></svg>
                  )}
                </button>
              ))}
            </div>
          ))}
        </div>
        <div style={{ borderTop: '1px solid var(--line)', marginTop: 8, paddingTop: 6 }}>
          <button onClick={store.clearMatch} style={{ display: 'flex', alignItems: 'center', gap: 9, width: '100%', padding: 10, border: 0, borderRadius: 10, cursor: 'pointer', background: 'transparent', color: 'var(--t3)', font: '600 12px var(--sans)', textAlign: 'left' }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
            Ver estado vacío (sin selección)
          </button>
        </div>
      </div>
    </>
  )
}
