import { useMemo } from 'react'
import { LINE_COLORS, MARKET_DEFS } from '../data'
import type { Match } from '../data/types'
import { buildChart, buildSpark } from '../lib/chart'
import { curOddOf, seriesFor } from '../lib/odds'
import { ChartSvg } from '../components/ChartSvg'
import { matchView } from '../lib/view'
import { loadCuotasBase, loadCuotasCasas, loadCuotasHistorial } from '../services/appdata'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  m: Match
  isMobile: boolean
}

export function Cuotas({ store, m, isMobile }: Props) {
  const { s } = store
  const isLive = s.oddsMode === 'live'
  const mv = matchView(m)
  const cmk = s.chartMarket || '1x2'
  const gridCuotasCards = isMobile ? '1fr' : '1fr 1fr 1fr'
  // cuotas base (/cuotas) + historial (/historial: tramo prepartido real con
  // >=2 snapshots) + comparador por casa (/casas: dónde paga más)
  const cuotas = useAsync(
    () => Promise.all([loadCuotasBase(m.id), loadCuotasHistorial(m.id), loadCuotasCasas(m.id)]),
    m.id,
  )
  const base = cuotas.data?.[0] ?? undefined
  const hist = cuotas.data?.[1] ?? undefined
  const casas = cuotas.data?.[2] ?? undefined

  const preBg = !isLive ? 'var(--bg3)' : 'transparent'
  const preFg = !isLive ? 'var(--t1)' : 'var(--t2)'
  const liveBg = isLive ? 'var(--down-soft)' : 'transparent'
  const liveFg = isLive ? 'var(--down)' : 'var(--t2)'

  const marketTabs = MARKET_DEFS.map((d) => ({
    key: d.key,
    label: d.title,
    active: d.key === cmk,
    bg: d.key === cmk ? 'var(--accent-soft)' : 'transparent',
    line: d.key === cmk ? 'color-mix(in oklch,var(--accent),transparent 55%)' : 'var(--line)',
    fg: d.key === cmk ? 'var(--accent)' : 'var(--t2)',
  }))

  // memoizadas contra el tick de 1s del store (s.now): solo se reconstruyen
  // cuando cambia algo que de verdad afecta a las series
  const chart = useMemo(() => buildChart(m, cmk, isLive, s.liveMin, s.marked, base, hist), [m, cmk, isLive, s.liveMin, s.marked, base, hist])
  const chartXfromOpen = isLive ? 'apertura → ' + s.liveMin + '’ en vivo' : 'apertura → cierre prepartido'

  const marketCards = useMemo(() => MARKET_DEFS.map((def) => {
    const sels = def.sels(m).map((sd) => {
      const sp = buildSpark(m, def.key, sd.k, isLive, s.liveMin, base, hist)
      const S = seriesFor(m, def.key, sd.k, base?.[def.key]?.[sd.k], hist?.[def.key]?.[sd.k])
      const cur = curOddOf(S, isLive, s.liveMin)
      const dlt = cur - S.open
      const id = m.id + ':' + def.key + ':' + sd.k
      const mkd = !!s.marked[id]
      return {
        key: sd.k, label: sd.label, oddText: cur.toFixed(2),
        sparkD: sp.d, sparkDotX: sp.dotX, sparkDotY: sp.dotY, sparkColor: LINE_COLORS[def.key][sd.k],
        trend: Math.abs(dlt) >= 0.01, trendGlyph: dlt > 0 ? '▲' : '▼', trendColor: dlt > 0 ? 'var(--up)' : 'var(--down)',
        showPct: isLive && Math.abs(dlt) >= 0.01, pctText: (dlt > 0 ? '+' : '') + ((dlt / S.open) * 100).toFixed(1) + '%', pctBg: dlt > 0 ? 'var(--up-soft)' : 'var(--down-soft)',
        marked: mkd, starFill: mkd ? 'var(--mark)' : 'none', starStroke: mkd ? 'var(--mark)' : 'var(--t3)',
        rowBg: mkd ? 'var(--mark-soft)' : 'transparent',
        id,
      }
    })
    return {
      key: def.key, title: def.title, sub: def.sub, active: def.key === cmk,
      cardBorder: def.key === cmk ? 'var(--accent)' : 'var(--line)',
      sels,
    }
  }), [m, cmk, isLive, s.liveMin, s.marked, base, hist])

  // comparador de casas del mercado activo: mejor cuota primero + ventaja vs media
  const casasRows = useMemo(() => {
    const def = MARKET_DEFS.find((d) => d.key === cmk)
    if (!def || !casas?.[cmk]) return []
    return def.sels(m).map((sd) => {
      const filas = casas[cmk][sd.k] ?? []
      const media = filas.length ? filas.reduce((a, f) => a + f.cuota, 0) / filas.length : 0
      const mejor = filas[0]
      const ventaja = mejor && media ? ((mejor.cuota - media) / media) * 100 : 0
      return { k: sd.k, label: sd.label, filas, ventajaText: ventaja >= 0.05 ? '+' + ventaja.toFixed(1) + '% vs media' : '' }
    }).filter((r) => r.filas.length > 1)
  }, [m, cmk, casas])

  const markedCount = Object.keys(s.marked).filter((k) => k.indexOf(m.id + ':') === 0 && s.marked[k]).length

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, marginBottom: 20, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Cuotas del partido</h1>
          <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>Movimiento de cada cuota desde su apertura hasta el final · marca las que veas con valor</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {markedCount > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '8px 12px', borderRadius: 9, background: 'var(--mark-soft)', border: '1px solid color-mix(in oklch,var(--mark),transparent 55%)' }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="var(--mark)"><path d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 18.6 6.1 20.5l1.2-6.5L2.5 9.4l6.6-.9z" /></svg>
              <span style={{ font: '600 12px var(--mono)', color: 'var(--mark)' }}>{markedCount} marcadas</span>
            </div>
          )}
          <div style={{ display: 'flex', padding: 4, borderRadius: 11, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <button onClick={store.setMode('prematch')} style={{ padding: '8px 16px', border: 0, borderRadius: 8, cursor: 'pointer', background: preBg, color: preFg, font: '600 12.5px var(--sans)' }}>Prepartido</button>
            <button onClick={store.setMode('live')} style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '8px 16px', border: 0, borderRadius: 8, cursor: 'pointer', background: liveBg, color: liveFg, font: '600 12.5px var(--sans)' }}>
              {isLive && <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>}En vivo
            </button>
          </div>
        </div>
      </div>

      {isLive && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', marginBottom: 16, borderRadius: 12, background: 'var(--bg1)', border: '1px solid var(--line)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 7, font: '700 11px var(--mono)', color: 'var(--down)', letterSpacing: '.6px' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>EN DIRECTO
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flexShrink: 0 }}>
            <button className="sad-hover" onClick={() => store.openTeam(mv.homeKey)} title={'Ver página de ' + mv.homeName} style={{ background: 'transparent', border: 0, cursor: 'pointer', padding: '2px 5px', borderRadius: 7, font: '700 18px var(--mono)', color: 'var(--t1)' }}>{mv.homeShort}</button>
            <span style={{ font: '700 18px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{m.score}</span>
            <button className="sad-hover" onClick={() => store.openTeam(mv.awayKey)} title={'Ver página de ' + mv.awayName} style={{ background: 'transparent', border: 0, cursor: 'pointer', padding: '2px 5px', borderRadius: 7, font: '700 18px var(--mono)', color: 'var(--t1)' }}>{mv.awayShort}</button>
          </span>
          <span style={{ font: '600 12px var(--mono)', color: 'var(--t2)' }}>{s.liveMin}'</span>
          <span style={{ marginLeft: 'auto', font: '500 11px var(--mono)', color: 'var(--t3)' }}>media entre casas capturadas</span>
        </div>
      )}

      {/* MARKET TABS */}
      <div className="sad-scroll" style={{ display: 'flex', gap: 6, marginBottom: 14, overflowX: 'auto', paddingBottom: 2 }}>
        {marketTabs.map((t) => (
          <button key={t.key} onClick={() => store.setChartMarket(t.key)} style={{ flexShrink: 0, padding: '8px 15px', border: `1px solid ${t.line}`, borderRadius: 9, cursor: 'pointer', background: t.bg, color: t.fg, font: '600 12px var(--sans)', whiteSpace: 'nowrap' }}>{t.label}</button>
        ))}
      </div>

      {cuotas.error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--down)', flexShrink: 0 }}></span>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudieron cargar las cuotas: {cuotas.error}</span>
          <button onClick={cuotas.reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)', flexShrink: 0 }}>Reintentar</button>
        </div>
      )}
      {cuotas.loading && (
        <div>
          <div className="sad-sk" style={{ height: 380, marginBottom: 14 }}></div>
          <div style={{ display: 'grid', gridTemplateColumns: gridCuotasCards, gap: 14 }}>
            <div className="sad-sk" style={{ height: 150 }}></div>
            <div className="sad-sk" style={{ height: 150 }}></div>
            <div className="sad-sk" style={{ height: 150 }}></div>
          </div>
        </div>
      )}
      {!cuotas.loading && !cuotas.error && (
        <>
      {/* BIG MOVEMENT CHART */}
      <section style={{ marginBottom: 14, padding: '18px 18px 14px', borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 14, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
            <h3 style={{ margin: 0, font: '700 15px var(--sans)' }}>{chart.title}</h3>
            <span style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>Movimiento de cuota · {chartXfromOpen}</span>
          </div>
          <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>media entre casas capturadas</span>
        </div>

        {/* legend */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 14 }}>
          {chart.lines.map((ln) => (
            <button key={ln.key} onClick={() => store.toggleMark(ln.id)} style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '9px 13px 9px 11px', borderRadius: 11, border: `1px solid ${ln.chipBorder}`, background: ln.chipBg, cursor: 'pointer', textAlign: 'left', transition: 'border-color .14s,background .14s' }}>
              <span style={{ width: 11, height: 11, borderRadius: 3, background: ln.color, flexShrink: 0 }}></span>
              <span style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)' }}>{ln.label}</span>
                <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>apertura {ln.openOdd}</span>
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 4 }}>
                <span style={{ font: '600 21px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>{ln.curOdd}</span>
                <span style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 2 }}>
                  <span style={{ padding: '2px 6px', borderRadius: 6, background: ln.pctBg, color: ln.deltaColor, font: '700 11px var(--mono)', lineHeight: 1 }}>{ln.deltaPct}</span>
                  <span style={{ font: '500 9px var(--mono)', color: 'var(--t3)' }}>{ln.deltaText}</span>
                </span>
              </span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill={ln.starFill} stroke={ln.starStroke} strokeWidth="1.7" style={{ flexShrink: 0, marginLeft: 2 }}><path d="M12 3l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 17.2 6.5 19.9l1.1-6.1L3.1 9.4l6.1-.8z" /></svg>
            </button>
          ))}
        </div>

        {/* plot */}
        <div style={{ borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)', overflow: 'hidden', padding: 4 }}>
          <ChartSvg chart={chart} liveMin={s.liveMin} />
        </div>
      </section>

      {/* COMPARADOR DE CASAS (mercado activo) */}
      {casasRows.length > 0 && (
        <section style={{ marginBottom: 14, padding: '16px 18px 14px', borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
              <h3 style={{ margin: 0, font: '700 15px var(--sans)' }}>Mejor casa por selección</h3>
              <span style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>{chart.title} · última captura</span>
            </div>
            <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>la cuota más alta paga más ese acierto</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {casasRows.map((row) => (
              <div key={row.k} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 10px', borderRadius: 10, background: 'var(--bg)' }}>
                <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', width: 130, flexShrink: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{row.label}</span>
                <div className="sad-scroll" style={{ display: 'flex', gap: 6, overflowX: 'auto', flex: 1, paddingBottom: 2 }}>
                  {row.filas.map((f, i) => (
                    <span key={f.casa + i} title={f.mejor ? 'mejor cuota' : undefined} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '5px 9px', borderRadius: 8, flexShrink: 0, border: `1px solid ${f.mejor ? 'color-mix(in oklch,var(--up),transparent 45%)' : 'var(--line)'}`, background: f.mejor ? 'var(--up-soft)' : 'var(--bg2)' }}>
                      <span style={{ font: '500 10px var(--sans)', color: f.mejor ? 'var(--up)' : 'var(--t3)' }}>{f.casa}</span>
                      <span style={{ font: '700 13px var(--mono)', color: f.mejor ? 'var(--up)' : 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{f.cuota.toFixed(2)}</span>
                    </span>
                  ))}
                </div>
                {row.ventajaText && (
                  <span style={{ font: '600 10px var(--mono)', color: 'var(--up)', flexShrink: 0 }}>{row.ventajaText}</span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* MARKET CARDS WITH SPARKLINES */}
      <div style={{ display: 'grid', gridTemplateColumns: gridCuotasCards, gap: 14 }}>
        {marketCards.map((mk) => (
          <div key={mk.key} onClick={() => store.setChartMarket(mk.key)} style={{ padding: 15, borderRadius: 14, background: 'var(--bg2)', border: `1px solid ${mk.cardBorder}`, cursor: 'pointer', transition: 'border-color .14s' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 11 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <h3 style={{ margin: 0, font: '700 12.5px var(--sans)' }}>{mk.title}</h3>
                <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>{mk.sub}</span>
              </div>
              {mk.active && <span style={{ font: '600 9px var(--mono)', color: 'var(--accent)', letterSpacing: '.4px' }}>EN GRÁFICA</span>}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
              {mk.sels.map((sel) => (
                <div key={sel.key} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 8px', borderRadius: 9, background: sel.rowBg }}>
                  <button onClick={(e) => { e.stopPropagation(); store.toggleMark(sel.id) }} style={{ background: 'none', border: 0, padding: 0, cursor: 'pointer', flexShrink: 0, display: 'flex' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill={sel.starFill} stroke={sel.starStroke} strokeWidth="1.8"><path d="M12 3l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 17.2 6.5 19.9l1.1-6.1L3.1 9.4l6.1-.8z" /></svg>
                  </button>
                  <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{sel.label}</span>
                  <svg viewBox="0 0 80 28" preserveAspectRatio="none" style={{ width: 58, height: 22, flexShrink: 0 }}>
                    <path d={sel.sparkD} fill="none" stroke={sel.sparkColor} strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke"></path>
                    <circle cx={sel.sparkDotX} cy={sel.sparkDotY} r="2" fill={sel.sparkColor}></circle>
                  </svg>
                  {sel.showPct && <span style={{ padding: '2px 6px', borderRadius: 6, background: sel.pctBg, color: sel.trendColor, font: '700 9.5px var(--mono)', flexShrink: 0 }}>{sel.pctText}</span>}
                  {sel.trend && <span style={{ font: '600 10px var(--mono)', color: sel.trendColor, width: 12 }}>{sel.trendGlyph}</span>}
                  <span style={{ font: '600 15px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums', minWidth: 42, textAlign: 'right' }}>{sel.oddText}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
        </>
      )}
    </div>
  )
}
