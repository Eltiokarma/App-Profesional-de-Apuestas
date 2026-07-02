import { MARKET_DEFS, MATCHES } from '../data'
import type { Match } from '../data/types'

// Deterministic FNV-1a seed + xorshift PRNG, keyed by a string id.
export function rng(id: string): () => number {
  let h = 2166136261
  for (const c of id) {
    h ^= c.charCodeAt(0)
    h = Math.imul(h, 16777619)
  }
  return () => {
    h ^= h << 13
    h ^= h >>> 17
    h ^= h << 5
    return (h >>> 0) / 4294967296
  }
}

type OddsTable = Record<string, Record<string, number>>
const _odds: Record<string, OddsTable> = {}

export function oddsFor(id: string): OddsTable {
  if (_odds[id]) return _odds[id]
  const r = rng(id)
  const o: OddsTable = {}
  for (const d of MARKET_DEFS) {
    o[d.key] = {}
    for (const k in d.base) {
      o[d.key][k] = Math.round(d.base[k] * (0.9 + r() * 0.2) * 100) / 100
    }
  }
  _odds[id] = o
  return o
}

export function inplayInfluence(m: Match, mk: string, selK: string): number {
  const p = (m.score || '0 - 0').split('-').map((x) => parseInt(x.trim()) || 0)
  const h = p[0] || 0
  const a = p[1] || 0
  const diff = h - a
  const tot = h + a
  const F: Record<string, Record<string, number>> = {
    '1x2': { '1': diff > 0 ? 0.32 : diff < 0 ? 2.7 : 1.5, X: diff === 0 ? 0.55 : 2.3, '2': diff < 0 ? 0.32 : diff > 0 ? 2.9 : 1.5 },
    dc: { '1X': diff >= 0 ? 0.42 : 1.95, '12': diff !== 0 ? 0.5 : 1.7, X2: diff <= 0 ? 0.42 : 1.95 },
    ou: { O: tot >= 3 ? 1.04 : tot === 2 ? 0.62 : tot === 1 ? 1.5 : 2.2, U: tot >= 3 ? 6.5 : tot === 2 ? 1.45 : tot === 1 ? 0.7 : 0.42 },
    ah: { H1: diff > 0 ? 0.4 : diff < 0 ? 3 : 1.7, H2: diff <= 0 ? 0.5 : 2.9 },
    btts: { Y: h > 0 && a > 0 ? 1.03 : h > 0 || a > 0 ? 1.85 : 2.5, N: h > 0 && a > 0 ? 6.5 : h > 0 || a > 0 ? 1.4 : 0.62 },
  }
  return (F[mk] && F[mk][selK]) || 1
}

export interface Series {
  open: number
  pre: number[]
  inp: number[]
  base: number
  IN: number
}

const _series: Record<string, Series> = {}

export function seriesFor(mId: string, mk: string, selK: string): Series {
  const key = mId + '|' + mk + '|' + selK
  if (_series[key]) return _series[key]
  const base = oddsFor(mId)[mk][selK]
  const r = rng(key + '#')
  const PRE = 14
  const IN = 19
  const open = Math.max(1.05, Math.round(base * (0.9 + r() * 0.2) * 100) / 100)
  const pre: number[] = []
  for (let i = 0; i < PRE; i++) {
    const f = i / (PRE - 1)
    const v = open * (1 - f) + base * f + (r() - 0.5) * 0.05 * base * (1 - f * 0.6)
    pre.push(Math.max(1.04, Math.round(v * 100) / 100))
  }
  pre[0] = open
  pre[PRE - 1] = base
  const m = MATCHES.find((x) => x.id === mId)!
  const endVal = Math.max(1.02, Math.round(base * inplayInfluence(m, mk, selK) * 100) / 100)
  const inp: number[] = []
  for (let i = 0; i < IN; i++) {
    const f = i / (IN - 1)
    const v = base * (1 - f) + endVal * f + (r() - 0.5) * 0.05 * base * Math.sin(f * 3.2)
    inp.push(Math.max(1.02, Math.round(v * 100) / 100))
  }
  inp[0] = base
  inp[IN - 1] = endVal
  const o: Series = { open, pre, inp, base, IN }
  _series[key] = o
  return o
}

export function curOddOf(S: Series, isLive: boolean, liveMin: number): number {
  return isLive ? S.inp[Math.max(0, Math.min(S.IN - 1, Math.round((liveMin / 90) * (S.IN - 1))))] : S.base
}
