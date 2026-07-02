import { LEVELS, TEAMS } from '../data'
import type { ConstKey, LevelKey } from '../data/types'

export function kData(teamKey: string, metric: ConstKey, lvl: LevelKey): number {
  const t = TEAMS[teamKey]
  const s = (t.pts - 40) / 40
  const ld = { elite: 0.9, alto: 0.55, medio: 0.3, bajo: 0.05 }[lvl]
  if (metric === 'dif') return Math.round((s * 1.7 - ld * 2.3 + 1.05) * 10) / 10
  if (metric === 'gf') return Math.round((2.0 + s * 0.8 - ld * 1.2) * 10) / 10
  return Math.round((1.4 - s * 0.7 + ld * 1.5) * 10) / 10
}

export interface Bubble {
  level: string
  color: string
  valueText: string
  style: React.CSSProperties
  title: string
}

export function buildBubbles(teamKey: string, metric: ConstKey): Bubble[] {
  const cols = LEVELS.length
  return LEVELS.map((lv, i) => {
    const v = kData(teamKey, metric, lv.k)
    const goodHigh = metric !== 'gc'
    const norm = Math.max(-2.5, Math.min(2.5, goodHigh ? v : -(v - 1.4) * 1.4))
    const r = Math.round(15 + Math.min(Math.abs(v), 3) * 8.5)
    const x = ((i + 0.5) / cols) * 100
    const y = 50 - (norm / 2.5) * 36
    const filled = goodHigh ? v >= 0.6 : v <= 1.2
    const txt = (metric === 'dif' ? (v >= 0 ? '+' : '') : '') + v.toFixed(1)
    const style: React.CSSProperties = {
      position: 'absolute',
      left: `${x}%`,
      top: `${y}%`,
      width: `${r * 2}px`,
      height: `${r * 2}px`,
      marginLeft: `${-r}px`,
      marginTop: `${-r}px`,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      font: `700 ${Math.max(9, r * 0.42)}px var(--mono)`,
      color: filled ? '#fff' : lv.color,
      background: filled ? lv.color : 'transparent',
      border: `2px solid ${lv.color}`,
      boxShadow: filled ? '0 4px 14px ' + lv.soft : 'none',
      transition: 'all .25s',
    }
    return { level: lv.label, color: lv.color, valueText: txt, style, title: lv.label + ': ' + txt }
  })
}
