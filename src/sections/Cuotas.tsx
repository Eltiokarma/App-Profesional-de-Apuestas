import { useEffect, useMemo, useState } from 'react'
import type { FixtureLiveDTO } from '../api/types'
import { CONFIG } from '../config'
import { LINE_COLORS, MARKET_DEFS } from '../data'
import type { Match } from '../data/types'
import { buildChart, buildSpark, type LiveRealSerie } from '../lib/chart'
import { curOddOf, seriesFor } from '../lib/odds'
import { ChartSvg } from '../components/ChartSvg'
import { matchView } from '../lib/view'
import { loadCuotasBase, loadCuotasCasas, loadCuotasHistorial, loadFuentesHistorial } from '../services/appdata'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  m: Match
  isMobile: boolean
  /** En vivo real compartido: App hace el polling y header + banner beben de aquí. */
  live: FixtureLiveDTO | null
}

export function Cuotas({ store, m, isMobile, live }: Props) {
  const { s } = store
  // Regla de datos: en http (producción) NO se pinta nada inventado — sin
  // >=2 capturas reales no hay curva, y el modo "En vivo" (simulado) queda
  // solo para la demo local hasta la fase 3 de docs/EXTRACCION_TIEMPO_REAL.md.
  const esDemo = CONFIG.dataSource === 'mock'
  const isLive = esDemo && s.oddsMode === 'live'
  const mv = matchView(m)
  const cmk = s.chartMarket || '1x2'
  const gridCuotasCards = isMobile ? '1fr' : '1fr 1fr 1fr'
  // fuente del historial: null = media entre casas; o una casa de referencia
  // (Bet365, Pinnacle…) con su curva cruda, que no se suaviza al promediar
  const [fuente, setFuente] = useState<string | null>(null)
  useEffect(() => setFuente(null), [m.id])
  const fuentes = useAsync(() => loadFuentesHistorial(m.id), m.id)
  // cuotas base (/cuotas) + historial (/historial: tramo prepartido real con
  // >=2 snapshots, de la fuente elegida) + comparador por casa (/casas)
  const cuotas = useAsync(
    () => Promise.all([loadCuotasBase(m.id), loadCuotasHistorial(m.id, fuente), loadCuotasCasas(m.id)]),
    m.id + '|' + (fuente ?? 'media'),
  )
  const base = cuotas.data?.[0] ?? undefined
  const hist = cuotas.data?.[1]?.cuotas ?? undefined
  const histFechas = cuotas.data?.[1]?.fechas ?? undefined
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

  // serie en vivo REAL agrupada para la gráfica { mercado → { sel → [{min, odd}] } }
  const livePts = useMemo<LiveRealSerie | null>(() => {
    if (esDemo || !live?.serie.length) return null
    const pts: LiveRealSerie['pts'] = {}
    for (const p of live.serie) {
      const mkT = (pts[p.mercado] = pts[p.mercado] ?? {})
      ;(mkT[p.seleccion] = mkT[p.seleccion] ?? []).push({ min: p.minuto ?? 0, odd: p.cuota })
    }
    const NOMBRE = { gol: 'Gol', amarilla: 'Amarilla', roja: 'Roja' } as const
    const eventos = live.eventos.map((e2) => ({
      min: e2.minuto ?? 0,
      tipo: e2.tipo,
      label: `${e2.minuto ?? '?'}' ${NOMBRE[e2.tipo]}${e2.jugador ? ' · ' + e2.jugador : ''}`,
    }))
    return { minuto: live.minuto ?? 90, pts, eventos }
  }, [esDemo, live])

  // en http la gráfica existe si hay prepartido real completo (>=2 capturas en
  // todas las selecciones) O serie en vivo real del mercado; si no, placeholder
  const defActivo = MARKET_DEFS.find((d) => d.key === cmk)!
  const histCompleto = defActivo.sels(m).every((sd) => (hist?.[cmk]?.[sd.k]?.length ?? 0) >= 2)
  const hayCurva = esDemo || histCompleto || !!livePts?.pts[cmk]

  // escala del eje Y: 'auto' pasa a log cuando el rango se estira (cuota >10
  // aplastaría a las de 1.x); el usuario puede forzarla con los chips
  const [escala, setEscala] = useState<'auto' | 'lineal' | 'log'>('auto')

  // memoizadas contra el tick de 1s del store (s.now): solo se reconstruyen
  // cuando cambia algo que de verdad afecta a las series
  const chart = useMemo(
    () => (hayCurva ? buildChart(m, cmk, isLive, s.liveMin, s.marked, base, hist, !esDemo, livePts ?? undefined, escala, histFechas) : null),
    [m, cmk, isLive, s.liveMin, s.marked, base, hist, histFechas, hayCurva, esDemo, livePts, escala],
  )
  const chartXfromOpen = isLive
    ? 'apertura → ' + s.liveMin + '’ en vivo'
    : livePts?.pts[cmk]
      ? live?.estado === 'en_vivo'
        ? 'apertura → ' + (live.minuto ?? '?') + '’ en vivo'
        : 'apertura → final del partido'
      : esDemo ? 'apertura → cierre prepartido' : 'apertura → última captura de la ingesta'

  const marketCards = useMemo(() => MARKET_DEFS.map((def) => {
    const sels = def.sels(m).map((sd) => {
      const baseSel = base?.[def.key]?.[sd.k]
      const h = hist?.[def.key]?.[sd.k]
      // en http, sparkline y deltas solo con >=2 capturas reales; si no,
      // se muestra la cuota real a secas (sin movimiento inventado)
      const conMovimiento = esDemo || (h?.length ?? 0) >= 2
      const sp = conMovimiento ? buildSpark(m, def.key, sd.k, isLive, s.liveMin, base, hist) : null
      const S = conMovimiento ? seriesFor(m, def.key, sd.k, baseSel, h) : null
      const cur = S ? curOddOf(S, isLive, s.liveMin) : baseSel ?? 0
      const dlt = S ? cur - S.open : 0
      const id = m.id + ':' + def.key + ':' + sd.k
      const mkd = !!s.marked[id]
      return {
        key: sd.k, label: sd.label, oddText: cur ? cur.toFixed(2) : '—',
        sparkD: sp?.d ?? '', sparkDotX: sp?.dotX ?? '0', sparkDotY: sp?.dotY ?? '0', sparkColor: LINE_COLORS[def.key][sd.k],
        trend: !!S && Math.abs(dlt) >= 0.01, trendGlyph: dlt > 0 ? '▲' : '▼', trendColor: dlt > 0 ? 'var(--up)' : 'var(--down)',
        showPct: isLive && !!S && Math.abs(dlt) >= 0.01,
        pctText: S ? (dlt > 0 ? '+' : '') + ((dlt / S.open) * 100).toFixed(1) + '%' : '',
        pctBg: dlt > 0 ? 'var(--up-soft)' : 'var(--down-soft)',
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
  }), [m, cmk, isLive, s.liveMin, s.marked, base, hist, esDemo])

  // cuotas en juego reales del mercado activo (http + partido vivo + cobertura);
  // en partidos terminados no aplican — la serie queda solo en la gráfica
  const cuotasJuego = useMemo(() => {
    if (!live || live.estado !== 'en_vivo' || !live.cuotas.length) return []
    const etiquetas = Object.fromEntries(defActivo.sels(m).map((sd) => [sd.k, sd.label]))
    return live.cuotas
      .filter((c2) => c2.mercado === cmk)
      .map((c2) => ({ ...c2, label: etiquetas[c2.seleccion] ?? c2.seleccion }))
  }, [live, cmk, defActivo, m])

  // comparador de casas del mercado activo: mejor cuota primero + ventaja vs media
  const casasRows = useMemo(() => {
    const def = MARKET_DEFS.find((d) => d.key === cmk)
    if (!def || !casas?.[cmk]) return []
    return def.sels(m).map((sd) => {
      const filas = casas[cmk][sd.k] ?? []
      const media = filas.length ? filas.reduce((a, f) => a + f.cuota, 0) / filas.length : 0
      const mejor = filas[0]
      const ventaja = mejor && media ? ((mejor.cuota - media) / media) * 100 : 0
      // variación entre la mejor y la peor oferta: cuánto pierdes apostando en la casa equivocada
      const peorCuota = filas.length ? Math.min(...filas.map((f) => f.cuota)) : 0
      const mejorCuota = filas.length ? Math.max(...filas.map((f) => f.cuota)) : 0
      const spread = mejorCuota - peorCuota
      const spreadText = spread >= 0.01 && peorCuota > 0
        ? `Δ ${spread.toFixed(2)} (${((spread / peorCuota) * 100).toFixed(1)}% mejor–peor)`
        : ''
      return { k: sd.k, label: sd.label, filas, ventajaText: ventaja >= 0.05 ? '+' + ventaja.toFixed(1) + '% vs media' : '', spreadText }
    }).filter((r) => r.filas.length > 1)
  }, [m, cmk, casas])

  const markedCount = Object.keys(s.marked).filter((k) => k.indexOf(m.id + ':') === 0 && s.marked[k]).length

  // chips MEDIA / casa de referencia: se pintan también en el placeholder para
  // poder volver a la media si la casa elegida aún no tiene capturas
  const fuentesList = fuentes.data ?? []
  const fuenteChips = fuentesList.length > 0 ? (
    <div style={{ display: 'flex', padding: 3, borderRadius: 8, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
      {[null, ...fuentesList].map((f) => {
        const activa = fuente === f
        return (
          <button
            key={f ?? 'media'}
            onClick={() => setFuente(f)}
            title={f ? 'Curva cruda de ' + f + ' (sin promediar)' : 'Media entre todas las casas capturadas'}
            style={{ padding: '4px 10px', border: 0, borderRadius: 6, cursor: 'pointer', background: activa ? 'var(--accent-soft)' : 'transparent', color: activa ? 'var(--accent)' : 'var(--t3)', font: '600 10.5px var(--mono)', whiteSpace: 'nowrap' }}
          >
            {f ?? 'MEDIA'}
          </button>
        )
      })}
    </div>
  ) : null

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
          {esDemo && (
            <div style={{ display: 'flex', padding: 4, borderRadius: 11, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <button onClick={store.setMode('prematch')} style={{ padding: '8px 16px', border: 0, borderRadius: 8, cursor: 'pointer', background: preBg, color: preFg, font: '600 12.5px var(--sans)' }}>Prepartido</button>
              <button onClick={store.setMode('live')} style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '8px 16px', border: 0, borderRadius: 8, cursor: 'pointer', background: liveBg, color: liveFg, font: '600 12.5px var(--sans)' }}>
                {isLive && <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>}En vivo
              </button>
            </div>
          )}
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

      {/* EN DIRECTO REAL (http): solo mientras el partido está en juego */}
      {live && live.estado === 'en_vivo' && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', marginBottom: 16, borderRadius: 12, background: 'var(--bg1)', border: '1px solid var(--line)', flexWrap: 'wrap' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 7, font: '700 11px var(--mono)', color: 'var(--down)', letterSpacing: '.6px' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>EN DIRECTO
          </span>
          <span style={{ font: '700 18px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
            {mv.homeShort} {live.golesLocal ?? '–'} - {live.golesVisitante ?? '–'} {mv.awayShort}
          </span>
          {live.minuto != null && <span style={{ font: '600 12px var(--mono)', color: 'var(--t2)' }}>{live.minuto}'</span>}
          <span style={{ marginLeft: 'auto', font: '500 11px var(--mono)', color: 'var(--t3)' }}>
            {live.actualizadoEn
              ? (() => {
                  // frescura visible: si la casa cerró el mercado, aquí se nota
                  const edadMin = Math.max(0, Math.round((Date.now() - new Date(live.actualizadoEn).getTime()) / 60000))
                  return edadMin < 2
                    ? 'cuotas en juego · al minuto'
                    : `cuotas en juego · última captura hace ${edadMin} min`
                })()
              : 'sin cobertura de cuotas en vivo en esta liga'}
          </span>
        </div>
      )}

      {/* MARKET TABS — en móvil quedan pegados arriba al hacer scroll: cambiar
          de mercado sin volver a subir por toda la página */}
      <div
        className="sad-scroll"
        style={{
          display: 'flex', gap: 6, marginBottom: 14, overflowX: 'auto', paddingBottom: 2,
          ...(isMobile ? { position: 'sticky' as const, top: -14, zIndex: 10, background: 'var(--bg)', paddingTop: 8, marginTop: -8 } : {}),
        }}
      >
        {marketTabs.map((t) => (
          <button key={t.key} onClick={() => store.setChartMarket(t.key)} style={{ flexShrink: 0, padding: '8px 15px', border: `1px solid ${t.line}`, borderRadius: 9, cursor: 'pointer', background: t.active ? t.bg : 'var(--bg)', color: t.fg, font: '600 12px var(--sans)', whiteSpace: 'nowrap' }}>{t.label}</button>
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
      {/* BIG MOVEMENT CHART — o placeholder honesto si aún no hay capturas */}
      {!chart && (
        <section style={{ marginBottom: 14, padding: '26px 22px', borderRadius: 16, background: 'var(--bg2)', border: '1px dashed var(--line)', textAlign: 'center' }}>
          <h3 style={{ margin: 0, font: '700 14px var(--sans)', color: 'var(--t2)' }}>{defActivo.title}: aún sin historial de movimiento{fuente ? ' de ' + fuente : ''}</h3>
          <p style={{ margin: '7px auto 0', maxWidth: 520, font: '500 12px var(--sans)', color: 'var(--t3)' }}>
            La curva se dibuja solo con capturas reales de la ingesta (mínimo 2 por selección).
            Cada corrida suma un punto; las cuotas actuales de abajo sí son reales.
          </p>
          {fuenteChips && <div style={{ display: 'flex', justifyContent: 'center', marginTop: 12 }}>{fuenteChips}</div>}
        </section>
      )}
      {chart && (
      <section style={{ marginBottom: 14, padding: '18px 18px 14px', borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 14, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
            <h3 style={{ margin: 0, font: '700 15px var(--sans)' }}>{chart.title}</h3>
            <span style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>Movimiento de cuota · {chartXfromOpen}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            {fuenteChips}
            <div style={{ display: 'flex', padding: 3, borderRadius: 8, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
              {(['lineal', 'log'] as const).map((e2) => {
                const activa = chart.escalaLog ? e2 === 'log' : e2 === 'lineal'
                return (
                  <button key={e2} onClick={() => setEscala(e2)} title={e2 === 'log' ? 'Escala logarítmica: las cuotas bajas no se aplastan' : 'Escala lineal'} style={{ padding: '4px 10px', border: 0, borderRadius: 6, cursor: 'pointer', background: activa ? 'var(--accent-soft)' : 'transparent', color: activa ? 'var(--accent)' : 'var(--t3)', font: '600 10.5px var(--mono)' }}>
                    {e2 === 'log' ? 'LOG' : 'LINEAL'}
                  </button>
                )
              })}
            </div>
            <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>{fuente ? 'cuota de ' + fuente : 'media entre casas capturadas'}</span>
          </div>
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
          <ChartSvg chart={chart} liveMin={esDemo ? s.liveMin : live?.minuto ?? 0} />
        </div>
      </section>
      )}

      {/* CUOTAS EN JUEGO REALES (mercado activo) */}
      {cuotasJuego.length > 0 && (
        <section style={{ marginBottom: 14, padding: '16px 18px 14px', borderRadius: 16, background: 'var(--bg2)', border: '1px solid color-mix(in oklch,var(--down),transparent 65%)' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
              <h3 style={{ margin: 0, font: '700 15px var(--sans)' }}>Cuotas en juego</h3>
              <span style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>{defActivo.title} · última captura de la ingesta en vivo</span>
            </div>
            {live?.minuto != null && <span style={{ font: '600 10px var(--mono)', color: 'var(--down)' }}>minuto {live.minuto}'</span>}
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {cuotasJuego.map((c2) => (
              <span key={c2.seleccion} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '8px 12px', borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg)', opacity: c2.suspendida ? 0.45 : 1 }}>
                <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)' }}>{c2.label}</span>
                <span style={{ font: '700 16px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{c2.cuota.toFixed(2)}</span>
                {c2.suspendida && <span style={{ font: '700 9px var(--mono)', color: 'var(--down)', letterSpacing: '.5px' }}>SUSP</span>}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* COMPARADOR DE CASAS (mercado activo) */}
      {casasRows.length > 0 && (
        <section style={{ marginBottom: 14, padding: '16px 18px 14px', borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
              <h3 style={{ margin: 0, font: '700 15px var(--sans)' }}>Mejor casa por selección</h3>
              <span style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>{defActivo.title} · última captura</span>
            </div>
            <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>la cuota más alta paga más ese acierto</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {casasRows.map((row) => (
              // móvil: etiqueta y ventaja arriba, chips a TODO lo ancho abajo —
              // con la etiqueta al lado la fila de casas quedaba aplastada y cortada
              <div key={row.k} style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'stretch' : 'center', gap: isMobile ? 7 : 12, padding: '8px 10px', borderRadius: 10, background: 'var(--bg)' }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, width: isMobile ? 'auto' : 130, flexShrink: 0, minWidth: 0 }}>
                  <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{row.label}</span>
                  {isMobile && (row.spreadText || row.ventajaText) && (
                    <span style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginLeft: 'auto', flexShrink: 0 }}>
                      {row.spreadText && <span style={{ font: '600 10px var(--mono)', color: 'var(--accent)' }}>{row.spreadText}</span>}
                      {row.ventajaText && <span style={{ font: '600 10px var(--mono)', color: 'var(--up)' }}>{row.ventajaText}</span>}
                    </span>
                  )}
                </div>
                <div className="sad-scroll" style={{ display: 'flex', gap: 6, overflowX: 'auto', flex: 1, minWidth: 0, paddingBottom: 2 }}>
                  {row.filas.map((f, i) => (
                    <span key={f.casa + i} title={f.mejor ? 'mejor cuota' : undefined} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '5px 9px', borderRadius: 8, flexShrink: 0, border: `1px solid ${f.mejor ? 'color-mix(in oklch,var(--up),transparent 45%)' : 'var(--line)'}`, background: f.mejor ? 'var(--up-soft)' : 'var(--bg2)' }}>
                      <span style={{ font: '500 10px var(--sans)', color: f.mejor ? 'var(--up)' : 'var(--t3)' }}>{f.casa}</span>
                      <span style={{ font: '700 13px var(--mono)', color: f.mejor ? 'var(--up)' : 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{f.cuota.toFixed(2)}</span>
                    </span>
                  ))}
                </div>
                {!isMobile && (row.spreadText || row.ventajaText) && (
                  <span style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 2, flexShrink: 0 }}>
                    {row.ventajaText && <span style={{ font: '600 10px var(--mono)', color: 'var(--up)' }}>{row.ventajaText}</span>}
                    {row.spreadText && <span style={{ font: '600 10px var(--mono)', color: 'var(--accent)' }}>{row.spreadText}</span>}
                  </span>
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
                  {sel.sparkD ? (
                    <svg viewBox="0 0 80 28" preserveAspectRatio="none" style={{ width: 58, height: 22, flexShrink: 0 }}>
                      <path d={sel.sparkD} fill="none" stroke={sel.sparkColor} strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke"></path>
                      <circle cx={sel.sparkDotX} cy={sel.sparkDotY} r="2" fill={sel.sparkColor}></circle>
                    </svg>
                  ) : (
                    <span style={{ width: 58, flexShrink: 0, textAlign: 'center', font: '500 10px var(--mono)', color: 'var(--t3)' }}>—</span>
                  )}
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
