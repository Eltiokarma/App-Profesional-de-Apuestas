import { LEVELS, TEAMS } from '../data'
import type { ConstKey, Match, ModelKey } from '../data/types'
import { buildBubbles, kData } from '../lib/bubbles'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  m: Match
  isMobile: boolean
}

export function Burbujas({ store, m, isMobile }: Props) {
  const { s } = store
  const H = TEAMS[m.home]
  const A = TEAMS[m.away]
  const gridBurbujas = isMobile ? '1fr' : '1fr 1fr 280px'

  const constLabel = { dif: 'Dif. de goles', gf: 'Goles a favor', gc: 'Goles en contra' }[s.constante]
  const constOpts = ([['dif', 'Dif. goles'], ['gf', 'Goles a favor'], ['gc', 'Goles en contra']] as [ConstKey, string][]).map(([k, l]) => ({
    key: k, label: l, bg: s.constante === k ? 'var(--bg3)' : 'transparent', fg: s.constante === k ? 'var(--t1)' : 'var(--t2)',
  }))
  const modelOpts = ([['auto', 'Auto'], ['global', 'Global'], ['liga', 'Liga']] as [ModelKey, string][]).map(([k, l]) => ({
    key: k, label: l, bg: s.model === k ? 'var(--accent-soft)' : 'transparent', fg: s.model === k ? 'var(--accent)' : 'var(--t2)',
  }))

  const bubblePanels = [
    { short: H.short, name: H.name, role: 'Local · modelo ' + s.model, color: H.color, fg: H.fg, bubbles: buildBubbles(m.home, s.constante) },
    { short: A.short, name: A.name, role: 'Visitante · modelo ' + s.model, color: A.color, fg: A.fg, bubbles: buildBubbles(m.away, s.constante) },
  ]

  const legendRows = LEVELS.map((lv) => {
    const hv = kData(m.home, s.constante, lv.k)
    const av = kData(m.away, s.constante, lv.k)
    const fmt = (v: number) => (s.constante === 'dif' && v >= 0 ? '+' : '') + v.toFixed(1)
    const col = (v: number) => (s.constante === 'gc' ? (v <= 1.2 ? 'var(--up)' : 'var(--down)') : v >= 0 ? 'var(--up)' : 'var(--down)')
    return { level: lv.label, color: lv.color, homeVal: fmt(hv), awayVal: fmt(av), homeColor: col(hv), awayColor: col(av) }
  })

  const nx = [
    { when: 'J33', name: 'Getafe', lv: 'medio' },
    { when: 'J34', name: 'Real Madrid', lv: 'elite' },
    { when: 'J35', name: 'Las Palmas', lv: 'bajo' },
  ]
  const nextThree = nx.map((n) => {
    const lv = LEVELS.find((l) => l.k === n.lv)!
    return { when: n.when, name: n.name, lvLabel: lv.label, lvColor: lv.color, lvSoft: lv.soft }
  })

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, marginBottom: 18, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Burbujas · Constantes K</h1>
          <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>Tamaño = magnitud · color = nivel del rival · metodología Dixon-Coles</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            {constOpts.map((c) => (
              <button key={c.key} onClick={store.setConst(c.key)} style={{ padding: '7px 13px', border: 0, borderRadius: 7, cursor: 'pointer', background: c.bg, color: c.fg, font: '600 11.5px var(--sans)' }}>{c.label}</button>
            ))}
          </div>
          <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            {modelOpts.map((md) => (
              <button key={md.key} onClick={store.setModel(md.key)} style={{ padding: '7px 11px', border: 0, borderRadius: 7, cursor: 'pointer', background: md.bg, color: md.fg, font: '600 11.5px var(--mono)' }}>{md.label}</button>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: gridBurbujas, gap: 14 }}>
        {bubblePanels.map((bp, pi) => (
          <section key={pi} style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span style={{ width: 28, height: 28, borderRadius: '50%', background: bp.color, color: bp.fg, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 10px var(--mono)' }}>{bp.short}</span>
              <div>
                <div style={{ font: '700 13.5px var(--sans)' }}>{bp.name}</div>
                <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>{bp.role}</div>
              </div>
            </div>
            <div style={{ position: 'relative', height: 210, marginTop: 6, borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', left: 0, right: 0, top: '50%', height: 1, background: 'var(--line)' }}></div>
              <div style={{ position: 'absolute', left: 8, top: 8, font: '500 9px var(--mono)', color: 'var(--up)' }}>+ favorable</div>
              <div style={{ position: 'absolute', left: 8, bottom: 8, font: '500 9px var(--mono)', color: 'var(--down)' }}>− desfavorable</div>
              {bp.bubbles.map((b, bi) => (
                <div key={bi} title={b.title} style={b.style}>{b.valueText}</div>
              ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: 8 }}>
              {bp.bubbles.map((b, bi) => (
                <div key={bi} style={{ font: '600 9.5px var(--mono)', color: 'var(--t3)', textAlign: 'center' }}>{b.level}</div>
              ))}
            </div>
          </section>
        ))}

        <aside style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 12 }}>Valores · {constLabel}</div>
            {legendRows.map((lg, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', borderBottom: '1px solid var(--line)' }}>
                <span style={{ width: 11, height: 11, borderRadius: '50%', background: lg.color }}></span>
                <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t2)', flex: 1 }}>{lg.level}</span>
                <span style={{ font: '600 12px var(--mono)', color: lg.homeColor, minWidth: 40, textAlign: 'right' }}>{lg.homeVal}</span>
                <span style={{ font: '600 12px var(--mono)', color: lg.awayColor, minWidth: 40, textAlign: 'right' }}>{lg.awayVal}</span>
              </div>
            ))}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 0, marginTop: 8 }}>
              <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', minWidth: 61, textAlign: 'right' }}>{H.short}</span>
              <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', minWidth: 40, textAlign: 'right' }}>{A.short}</span>
            </div>
          </section>
          <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 4 }}>Próximos 3 · {H.name}</div>
            <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 12 }}>Calendario por nivel</div>
            {nextThree.map((n, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 0', borderBottom: '1px solid var(--line)' }}>
                <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 36 }}>{n.when}</span>
                <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1 }}>{n.name}</span>
                <span style={{ padding: '3px 9px', borderRadius: 6, background: n.lvSoft, color: n.lvColor, font: '700 9.5px var(--mono)', letterSpacing: '.3px' }}>{n.lvLabel}</span>
              </div>
            ))}
          </section>
        </aside>
      </div>
    </div>
  )
}
