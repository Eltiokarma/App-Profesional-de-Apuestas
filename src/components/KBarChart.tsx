// Gráfica de BARRAS de una racha de k_cuota (§3.8). Eje X = fecha del partido,
// eje Y = suma acumulada de la cuota. El partido que revienta la racha (valor 0)
// se dibuja como un "muñón" en la base para marcar dónde estalló.
export interface CuotaBar {
  fecha: string
  value: number
  /** true si la racha valía 0 tras ese partido (reventón / sin racha). */
  burst: boolean
  /** cuota que aplicó a ese partido (para el tooltip). */
  cuota: number | null
  /** 1 gana · 0 empata · -1 pierde. */
  res: number
}

interface Props {
  bars: CuotaBar[]
  color: string
  soft: string
  title: string
}

const W = 460
const H = 150
const PAD_L = 8
const PAD_R = 8
const PLOT_TOP = 24
const BASE = 128 // línea base (y de valor 0)

const RES_TXT: Record<number, string> = { 1: 'ganó', 0: 'empató', [-1]: 'perdió' }

export function KBarChart({ bars, color, soft, title }: Props) {
  if (!bars.length) {
    return (
      <div style={{ padding: '10px 12px', borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)' }}>
        <div style={{ font: '700 11px var(--sans)', color: 'var(--t2)', marginBottom: 4 }}>{title}</div>
        <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', padding: '14px 0', textAlign: 'center' }}>Sin partidos con cuota</div>
      </div>
    )
  }
  const n = bars.length
  const maxY = Math.max(...bars.map((b) => b.value), 0.001)
  const plotH = BASE - PLOT_TOP
  const bw = (W - PAD_L - PAD_R) / n
  const barW = Math.max(1.5, Math.min(bw * 0.72, 22))
  const cx = (i: number) => PAD_L + bw * (i + 0.5)
  const cur = bars[n - 1].value

  return (
    <div style={{ padding: '10px 12px', borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 2 }}>
        <span style={{ font: '700 11px var(--sans)', color: 'var(--t1)' }}>{title}</span>
        <span style={{ font: '700 13px var(--mono)', color: cur > 0 ? color : 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>{cur.toFixed(2)}</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" style={{ width: '100%', height: 'auto', display: 'block' }}>
        <line x1={PAD_L} x2={W - PAD_R} y1={BASE} y2={BASE} stroke="var(--line)" strokeWidth={1} />
        <text x={PAD_L} y={PLOT_TOP - 8} fontSize={9.5} fontWeight={600} style={{ fill: 'var(--t3)', fontFamily: 'var(--mono)' }}>máx {maxY.toFixed(1)}</text>
        {bars.map((b, i) => {
          const h = b.burst ? 2.5 : Math.max(2.5, (b.value / maxY) * plotH)
          const x = cx(i) - barW / 2
          const tip = `${b.fecha.slice(0, 10)} · ${RES_TXT[b.res]}${b.cuota != null ? ` · cuota ${b.cuota.toFixed(2)}` : ''} · racha ${b.value.toFixed(2)}${b.burst ? ' (reventón)' : ''}`
          return (
            <rect key={i} x={x} y={BASE - h} width={barW} height={h} rx={1.5} fill={b.burst ? 'var(--t3)' : color} opacity={b.burst ? 0.5 : 0.92}>
              <title>{tip}</title>
            </rect>
          )
        })}
        <text x={PAD_L} y={H - 3} fontSize={9} fontWeight={600} style={{ fill: 'var(--t3)', fontFamily: 'var(--mono)' }}>{bars[0].fecha.slice(0, 10)}</text>
        <text x={W - PAD_R} y={H - 3} textAnchor="end" fontSize={9} fontWeight={600} style={{ fill: 'var(--t3)', fontFamily: 'var(--mono)' }}>{bars[n - 1].fecha.slice(0, 10)}</text>
      </svg>
      <div style={{ height: 3, borderRadius: 2, background: soft, marginTop: 2 }} />
    </div>
  )
}
