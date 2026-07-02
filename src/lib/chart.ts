import { LINE_COLORS, MARKET_DEFS, MATCHES } from '../data'
import { seriesFor, type Series } from './odds'

export interface ChartLine {
  key: string
  label: string
  color: string
  d: string
  dotX: string
  dotY: string
  curOdd: string
  openOdd: string
  deltaText: string
  deltaColor: string
  deltaPct: string
  pctBg: string
  id: string
  marked: boolean
  chipBg: string
  chipBorder: string
  starFill: string
  starStroke: string
}

export interface ChartGrid {
  y: string
  label: string
}

export interface ChartXLabel {
  x: string
  label: string
  anchor: 'start' | 'middle' | 'end'
}

export interface Chart {
  lines: ChartLine[]
  grid: ChartGrid[]
  xLabels: ChartXLabel[]
  title: string
  sub: string
  showKO: boolean
  koX: string
  showNow: boolean
  nowX: string
}

export function buildChart(
  mId: string,
  mk: string,
  isLive: boolean,
  liveMin: number,
  marked: Record<string, boolean>,
): Chart {
  const def = MARKET_DEFS.find((d) => d.key === mk)!
  const m = MATCHES.find((x) => x.id === mId)!
  const sels = def.sels(m)
  const koFrac = 0.46
  const series = sels.map((sd) => {
    const S = seriesFor(mId, mk, sd.k)
    const PRE = S.pre.length
    const pts: { t: number; odd: number }[] = []
    for (let i = 0; i < PRE; i++) {
      const t = isLive ? (i / (PRE - 1)) * koFrac : i / (PRE - 1)
      pts.push({ t, odd: S.pre[i] })
    }
    if (isLive) {
      const ci = Math.max(0, Math.min(S.IN - 1, Math.round((liveMin / 90) * (S.IN - 1))))
      for (let i = 0; i <= ci; i++) {
        const t = koFrac + (i / (S.IN - 1)) * (1 - koFrac)
        pts.push({ t, odd: S.inp[i] })
      }
    }
    return { sd, S, pts }
  })
  let ymin = Infinity
  let ymax = -Infinity
  series.forEach((x) =>
    x.pts.forEach((p) => {
      if (p.odd < ymin) ymin = p.odd
      if (p.odd > ymax) ymax = p.odd
    }),
  )
  if (!isFinite(ymin)) {
    ymin = 1
    ymax = 3
  }
  const pd = (ymax - ymin) * 0.14 || 0.2
  ymin = Math.max(1, ymin - pd)
  ymax += pd
  const plotL = 56
  const plotR = 984
  const plotT = 20
  const plotB = 252
  const px = (t: number) => plotL + t * (plotR - plotL)
  const py = (v: number) => plotT + (1 - (v - ymin) / (ymax - ymin)) * (plotB - plotT)
  const lines: ChartLine[] = series.map(({ sd, S, pts }) => {
    let d = ''
    pts.forEach((p, i) => {
      d += (i ? 'L' : 'M') + px(p.t).toFixed(1) + ' ' + py(p.odd).toFixed(1) + ' '
    })
    const last = pts[pts.length - 1]
    const cur = last.odd
    const open = S.open
    const dlt = cur - open
    const id = mId + ':' + mk + ':' + sd.k
    const mkd = !!marked[id]
    return {
      key: sd.k,
      label: sd.label,
      color: LINE_COLORS[mk][sd.k],
      d,
      dotX: px(last.t).toFixed(1),
      dotY: py(cur).toFixed(1),
      curOdd: cur.toFixed(2),
      openOdd: open.toFixed(2),
      deltaText: (dlt > 0 ? '+' : '') + dlt.toFixed(2),
      deltaColor: dlt > 0 ? 'var(--up)' : dlt < 0 ? 'var(--down)' : 'var(--t3)',
      deltaPct: (dlt > 0 ? '+' : '') + ((dlt / open) * 100).toFixed(1) + '%',
      pctBg: dlt > 0 ? 'var(--up-soft)' : dlt < 0 ? 'var(--down-soft)' : 'var(--bg3)',
      id,
      marked: mkd,
      chipBg: mkd ? 'var(--mark-soft)' : 'var(--bg3)',
      chipBorder: mkd ? 'var(--mark)' : 'var(--line)',
      starFill: mkd ? 'var(--mark)' : 'none',
      starStroke: mkd ? 'var(--mark)' : 'var(--t3)',
    }
  })
  const grid: ChartGrid[] = []
  for (let i = 0; i <= 4; i++) {
    const v = ymin + (i / 4) * (ymax - ymin)
    grid.push({ y: py(v).toFixed(1), label: v.toFixed(2) })
  }
  let xL: [number, string][]
  if (isLive) {
    xL = [
      [0, 'Apertura'],
      [koFrac, 'KO'],
      [koFrac + (15 / 90) * (1 - koFrac), "15'"],
      [koFrac + (45 / 90) * (1 - koFrac), "45'"],
      [koFrac + (75 / 90) * (1 - koFrac), "75'"],
      [1, "90'"],
    ]
  } else {
    xL = [
      [0, 'Apertura'],
      [0.34, '-2 días'],
      [0.67, '-6 h'],
      [1, 'KO'],
    ]
  }
  const xLabels: ChartXLabel[] = xL.map(([t, label], i) => ({
    x: px(t).toFixed(1),
    label,
    anchor: i === 0 ? 'start' : i === xL.length - 1 ? 'end' : 'middle',
  }))
  const nowT = isLive ? koFrac + (Math.min(liveMin, 90) / 90) * (1 - koFrac) : null
  return {
    lines,
    grid,
    xLabels,
    title: def.title,
    sub: def.sub,
    showKO: isLive,
    koX: px(koFrac).toFixed(1),
    showNow: isLive,
    nowX: nowT != null ? px(nowT).toFixed(1) : '0',
  }
}

export interface Spark {
  d: string
  dotX: string
  dotY: string
}

export function buildSpark(mId: string, mk: string, selK: string, isLive: boolean, liveMin: number): Spark {
  const S: Series = seriesFor(mId, mk, selK)
  const koFrac = 0.5
  const PRE = S.pre.length
  const pts: { t: number; odd: number }[] = []
  for (let i = 0; i < PRE; i++) {
    pts.push({ t: isLive ? (i / (PRE - 1)) * koFrac : i / (PRE - 1), odd: S.pre[i] })
  }
  if (isLive) {
    const ci = Math.max(0, Math.min(S.IN - 1, Math.round((liveMin / 90) * (S.IN - 1))))
    for (let i = 0; i <= ci; i++) {
      pts.push({ t: koFrac + (i / (S.IN - 1)) * (1 - koFrac), odd: S.inp[i] })
    }
  }
  let mn = Infinity
  let mx = -Infinity
  pts.forEach((p) => {
    if (p.odd < mn) mn = p.odd
    if (p.odd > mx) mx = p.odd
  })
  const rr = mx - mn || 1
  const px = (t: number) => 2 + t * 76
  const py = (v: number) => 3 + (1 - (v - mn) / rr) * 22
  let d = ''
  pts.forEach((p, i) => {
    d += (i ? 'L' : 'M') + px(p.t).toFixed(1) + ' ' + py(p.odd).toFixed(1) + ' '
  })
  const last = pts[pts.length - 1]
  return { d, dotX: px(last.t).toFixed(1), dotY: py(last.odd).toFixed(1) }
}
