import { LINE_COLORS, MARKET_DEFS } from '../data'
import type { Match } from '../data/types'
import { seriesFor, type Series } from './odds'

/** Tabla base { mercado → { selección → cuota } } servida por el contrato /cuotas. */
export type BaseOddsTable = Record<string, Record<string, number>>
const baseOf = (base: BaseOddsTable | undefined, mk: string, selK: string) => base?.[mk]?.[selK]

/** Historial { mercado → { selección → [cuotas asc] } } de /cuotas/{id}/historial. */
export type HistOddsTable = Record<string, Record<string, number[]>>
const histOf = (hist: HistOddsTable | undefined, mk: string, selK: string) => hist?.[mk]?.[selK]

/** Serie EN VIVO real (contrato /fixtures/{id}/live): puntos por minuto del partido. */
export interface LiveRealSerie {
  minuto: number
  pts: Record<string, Record<string, { min: number; odd: number }[]>>
}

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
  m: Match,
  mk: string,
  isLive: boolean,
  liveMin: number,
  marked: Record<string, boolean>,
  base?: BaseOddsTable,
  hist?: HistOddsTable,
  soloCapturas?: boolean, // true (http): el eje X son capturas reales de la ingesta, sin tiempos inventados
  liveReal?: LiveRealSerie, // http + partido en juego: tramo en vivo con la serie REAL de odds_live
): Chart {
  const def = MARKET_DEFS.find((d) => d.key === mk)!
  const mId = m.id
  const sels = def.sels(m)
  const koFrac = 0.46
  // tiempo extra: el eje llega hasta el último minuto real (91-120), no se
  // clava en 90 apilando los puntos nuevos en el borde
  const maxMin = liveReal
    ? Math.max(90, liveReal.minuto, ...Object.values(liveReal.pts[mk] ?? {}).flat().map((p) => p.min))
    : 90
  const series = liveReal
    ? sels.flatMap((sd) => {
        // solo datos reales: prepartido si hay >=2 capturas, en vivo si hay serie
        const h = histOf(hist, mk, sd.k) ?? []
        const lv = liveReal.pts[mk]?.[sd.k] ?? []
        const pts: { t: number; odd: number }[] = []
        if (h.length >= 2) h.forEach((odd, i) => pts.push({ t: (i / (h.length - 1)) * koFrac, odd }))
        lv.forEach((p) => pts.push({ t: koFrac + (Math.min(p.min, maxMin) / maxMin) * (1 - koFrac), odd: p.odd }))
        if (!pts.length) return []
        const S: Series = {
          open: h.length >= 2 ? h[0] : lv[0].odd,
          pre: h, inp: [], base: pts[pts.length - 1].odd, IN: 0,
        }
        return [{ sd, S, pts }]
      })
    : sels.map((sd) => {
        const S = seriesFor(m, mk, sd.k, baseOf(base, mk, sd.k), histOf(hist, mk, sd.k))
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
  if (isLive || liveReal) {
    const marcas = maxMin > 90 ? [45, 90] : [15, 45, 75]
    xL = [
      [0, 'Apertura'],
      [koFrac, 'KO'],
      ...marcas.map((mn) => [koFrac + (mn / maxMin) * (1 - koFrac), mn + "'"] as [number, string]),
      [1, maxMin + "'"],
    ]
  } else if (soloCapturas) {
    xL = [
      [0, 'Apertura'],
      [1, 'Última captura'],
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
  const minutoNow = isLive ? liveMin : liveReal ? liveReal.minuto : null
  const nowT = minutoNow != null ? koFrac + (Math.min(minutoNow, maxMin) / maxMin) * (1 - koFrac) : null
  return {
    lines,
    grid,
    xLabels,
    title: def.title,
    sub: def.sub,
    showKO: isLive || !!liveReal,
    koX: px(koFrac).toFixed(1),
    showNow: isLive || !!liveReal,
    nowX: nowT != null ? px(nowT).toFixed(1) : '0',
  }
}

export interface Spark {
  d: string
  dotX: string
  dotY: string
}

export function buildSpark(m: Match, mk: string, selK: string, isLive: boolean, liveMin: number, base?: BaseOddsTable, hist?: HistOddsTable): Spark {
  const S: Series = seriesFor(m, mk, selK, baseOf(base, mk, selK), histOf(hist, mk, selK))
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
