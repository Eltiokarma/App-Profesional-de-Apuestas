import { LINE_COLORS, MARKET_DEFS } from '../data'
import type { Match } from '../data/types'
import { seriesFor, type Series } from './odds'

/** Tabla base { mercado → { selección → cuota } } servida por el contrato /cuotas. */
export type BaseOddsTable = Record<string, Record<string, number>>
const baseOf = (base: BaseOddsTable | undefined, mk: string, selK: string) => base?.[mk]?.[selK]

/** Historial { mercado → { selección → [cuotas asc] } } de /cuotas/{id}/historial. */
export type HistOddsTable = Record<string, Record<string, number[]>>
const histOf = (hist: HistOddsTable | undefined, mk: string, selK: string) => hist?.[mk]?.[selK]

/** Fechas de captura alineadas índice a índice con el historial. */
export type HistFechasTable = Record<string, Record<string, string[]>>

const MES_CORTO = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
const fmtFecha = (iso: string): string => {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return ''
  const p2 = (n: number) => String(n).padStart(2, '0')
  return `${d.getDate()} ${MES_CORTO[d.getMonth()]} ${p2(d.getHours())}:${p2(d.getMinutes())}`
}

/** Serie EN VIVO real (contrato /fixtures/{id}/live): puntos por minuto del partido. */
export interface LiveRealSerie {
  minuto: number
  pts: Record<string, Record<string, { min: number; odd: number }[]>>
  /** Goles y tarjetas para anclar el movimiento a su causa. */
  eventos: { min: number; tipo: 'gol' | 'amarilla' | 'roja'; label: string }[]
}

export interface ChartEvento {
  x: number
  tipo: 'gol' | 'amarilla' | 'roja'
  label: string
}

/** Punto tocable de la gráfica: al pulsarlo se abre la burbuja con su valor. */
export interface ChartPunto {
  x: string
  y: string
  label: string
}

export interface ChartLine {
  key: string
  label: string
  color: string
  d: string
  pts: ChartPunto[]
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
  eventos: ChartEvento[]
  escalaLog: boolean
  /** Referencia de la cuota inicial en la leyenda: 'apertura' (fase pre) o 'KO' (fase vivo). */
  refLabel: string
}

/** Fase de la gráfica cuando el partido tiene tramo en vivo: 'pre' pinta solo
 *  apertura → KO y 'vivo' solo KO → final, cada una con SU escala. Juntas en un
 *  solo lienzo, las cuotas en vivo (1.01 ↔ 500) aplastaban el movimiento
 *  prepartido hasta hacerlo ilegible incluso en escala log. */
export type ChartFase = 'pre' | 'vivo'

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
  escala: 'auto' | 'lineal' | 'log' = 'auto', // log: las cuotas bajas no se aplastan cuando alguna se dispara
  fechas?: HistFechasTable, // fechas de captura: el tooltip de cada punto muestra cuándo se tomó
  fase: ChartFase = 'pre', // con tramo en vivo: qué mitad pintar (cada una con su escala)
): Chart {
  const def = MARKET_DEFS.find((d) => d.key === mk)!
  const mId = m.id
  const sels = def.sels(m)
  const hayVivo = isLive || !!liveReal
  const enVivo = hayVivo && fase === 'vivo'
  // tiempo extra: el eje llega hasta el último minuto real (91-120), no se
  // clava en 90 apilando los puntos nuevos en el borde
  const maxMin = liveReal
    ? Math.max(90, liveReal.minuto, ...Object.values(liveReal.pts[mk] ?? {}).flat().map((p) => p.min))
    : 90
  type Punto = { t: number; odd: number; fecha?: string; min?: number }
  const series = enVivo && liveReal
    ? sels.flatMap((sd) => {
        // FASE VIVO (http): solo la serie real de odds_live, KO → final
        const lv = liveReal.pts[mk]?.[sd.k] ?? []
        if (!lv.length) return []
        const pts: Punto[] = lv.map((p) => ({ t: Math.min(p.min, maxMin) / maxMin, odd: p.odd, min: p.min }))
        const S: Series = { open: lv[0].odd, pre: [], inp: [], base: pts[pts.length - 1].odd, IN: 0 }
        return [{ sd, S, pts }]
      })
    : enVivo
      ? sels.map((sd) => {
          // FASE VIVO (demo): tramo simulado KO → minuto actual
          const S = seriesFor(m, mk, sd.k, baseOf(base, mk, sd.k), histOf(hist, mk, sd.k))
          const ci = Math.max(0, Math.min(S.IN - 1, Math.round((liveMin / 90) * (S.IN - 1))))
          const pts: Punto[] = []
          for (let i = 0; i <= ci; i++) {
            pts.push({ t: S.IN > 1 ? i / (S.IN - 1) : 0, odd: S.inp[i], min: Math.round((i / (S.IN - 1)) * 90) })
          }
          return { sd, S: { ...S, open: S.inp[0] }, pts }
        })
      : sels.flatMap((sd) => {
          // FASE PRE (o partido sin tramo vivo): historial apertura → KO a todo
          // el ancho; solo capturas reales en http (>=2 por selección)
          const h = histOf(hist, mk, sd.k)
          if (liveReal && (h?.length ?? 0) < 2) return [] // sin prepartido real: nada inventado
          const S = seriesFor(m, mk, sd.k, baseOf(base, mk, sd.k), h)
          // las fechas solo aplican si la serie prepartido ES el historial real
          const fh = h && h.length >= 2 ? fechas?.[mk]?.[sd.k] : undefined
          const PRE = S.pre.length
          const pts: Punto[] = []
          for (let i = 0; i < PRE; i++) {
            pts.push({ t: PRE > 1 ? i / (PRE - 1) : 0, odd: S.pre[i], fecha: fh?.[i] })
          }
          if (!pts.length) return []
          return [{ sd, S, pts }]
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
  // rango mínimo del eje (mismo criterio que buildSpark): variaciones de
  // centavos no se estiran a sierra; el movimiento real conserva su drama
  const minRango = Math.max(ymax * 0.05, 0.08)
  if (ymax - ymin < minRango) {
    const centro = (ymax + ymin) / 2
    ymin = centro - minRango / 2
    ymax = centro + minRango / 2
    if (ymin < 1) {
      ymax += 1 - ymin
      ymin = 1
    }
  }
  const pd = (ymax - ymin) * 0.14 || 0.2
  ymin = Math.max(1, ymin - pd)
  ymax += pd
  // escala log automática cuando el rango se estira (una cuota en 50 no debe
  // aplastar contra el piso a las que viven entre 1.0 y 3.0)
  const escalaLog = escala === 'log' || (escala === 'auto' && ymax / ymin > 6)
  const plotL = 56
  const plotR = 984
  const plotT = 20
  const plotB = 252
  const px = (t: number) => plotL + t * (plotR - plotL)
  const lymin = Math.log(ymin)
  const lymax = Math.log(ymax)
  const py = escalaLog
    ? (v: number) => plotT + (1 - (Math.log(Math.max(v, ymin)) - lymin) / (lymax - lymin)) * (plotB - plotT)
    : (v: number) => plotT + (1 - (v - ymin) / (ymax - ymin)) * (plotB - plotT)
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
      // puntos tocables: cuota + cuándo (fecha de captura o minuto de juego)
      pts: pts.map((p) => ({
        x: px(p.t).toFixed(1),
        y: py(p.odd).toFixed(1),
        label:
          `${sd.label} · ${p.odd.toFixed(2)}` +
          (p.fecha ? ` · ${fmtFecha(p.fecha)}` : p.min != null ? ` · ${p.min}’` : ''),
      })),
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
    // en log las líneas de la grilla van en pasos geométricos, no aritméticos
    const v = escalaLog ? ymin * Math.pow(ymax / ymin, i / 4) : ymin + (i / 4) * (ymax - ymin)
    grid.push({ y: py(v).toFixed(1), label: v.toFixed(2) })
  }
  let xL: [number, string][]
  if (enVivo) {
    // fase vivo: el eje ES el partido, KO → último minuto real
    const marcas = maxMin > 90 ? [45, 90] : [15, 45, 75]
    xL = [
      [0, 'KO'],
      ...marcas.map((mn) => [mn / maxMin, mn + "'"] as [number, string]),
      [1, maxMin + "'"],
    ]
  } else if (soloCapturas) {
    // con tramo vivo, la última captura prepartido ES el KO
    xL = [
      [0, 'Apertura'],
      [1, hayVivo ? 'KO' : 'Última captura'],
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
  const minutoNow = !enVivo ? null : isLive ? liveMin : liveReal ? liveReal.minuto : null
  const nowT = minutoNow != null ? Math.min(minutoNow, maxMin) / maxMin : null
  // goles y tarjetas anclados a su minuto (solo tienen sentido en la fase vivo)
  const eventos: ChartEvento[] = enVivo
    ? (liveReal?.eventos ?? []).map((ev) => ({
        x: Number(px(Math.min(ev.min, maxMin) / maxMin).toFixed(1)),
        tipo: ev.tipo,
        label: ev.label,
      }))
    : []
  return {
    lines,
    grid,
    xLabels,
    title: def.title,
    sub: def.sub,
    showKO: false, // cada fase vive en su propio lienzo: el KO es un borde, no una línea
    koX: '0',
    showNow: enVivo,
    nowX: nowT != null ? px(nowT).toFixed(1) : '0',
    eventos,
    escalaLog,
    refLabel: enVivo ? 'KO' : 'apertura',
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
  // rango mínimo del eje: el ruido de ±0.01 de la media entre casas se
  // autoescalaba a pantalla completa y pintaba una sierra dramática — con
  // piso de rango, lo casi-plano SE VE casi plano y el movimiento real resalta
  const minRango = Math.max(mx * 0.06, 0.1)
  if (mx - mn < minRango) {
    const extra = (minRango - (mx - mn)) / 2
    mn -= extra
    mx += extra
  }
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
