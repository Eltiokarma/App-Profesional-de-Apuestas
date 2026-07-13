import type { Chart } from '../lib/chart'

const tf: React.CSSProperties = { fill: 'var(--t3)', fontFamily: 'var(--mono)' }

/** Self-contained SVG chart — grid, KO/now markers, lines, dots and axis labels
 *  as native <text> nodes so nothing depends on HTML overlay positioning. */
export function ChartSvg({ chart, liveMin }: { chart: Chart; liveMin: number }) {
  return (
    <svg
      viewBox="0 0 1000 300"
      preserveAspectRatio="xMidYMid meet"
      style={{ width: '100%', height: 'auto', display: 'block' }}
    >
      {chart.grid.map((g, i) => (
        <g key={'g' + i}>
          <line x1={56} x2={984} y1={g.y} y2={g.y} stroke="var(--grid)" strokeWidth={1} vectorEffect="non-scaling-stroke" />
          <text x={48} y={g.y} textAnchor="end" dominantBaseline="middle" fontSize={13} fontWeight={600} style={tf}>
            {g.label}
          </text>
        </g>
      ))}

      {chart.showKO && (
        <>
          <line x1={chart.koX} x2={chart.koX} y1={16} y2={258} stroke="var(--line2)" strokeWidth={1.3} strokeDasharray="5 5" vectorEffect="non-scaling-stroke" />
          <text x={chart.koX} y={13} textAnchor="middle" fontSize={12} fontWeight={700} style={tf}>
            KO
          </text>
        </>
      )}

      {chart.showNow && (
        <>
          <line x1={chart.nowX} x2={chart.nowX} y1={16} y2={258} stroke="var(--down)" strokeWidth={1.3} strokeDasharray="3 4" vectorEffect="non-scaling-stroke" />
          <text x={chart.nowX} y={13} textAnchor="middle" fontSize={12} fontWeight={700} style={{ fill: 'var(--down)', fontFamily: 'var(--mono)' }}>
            {liveMin + "'"}
          </text>
        </>
      )}

      {/* eventos del partido: gol (punto verde) · amarilla/roja (rectángulo) */}
      {chart.eventos.map((ev, i) => {
        const yTop = 26 + (i % 2) * 15 // alterna altura para que no se pisen
        return (
          <g key={'ev' + i}>
            <title>{ev.label}</title>
            <line x1={ev.x} x2={ev.x} y1={yTop + 12} y2={258} stroke="var(--line2)" strokeWidth={1} strokeDasharray="2 6" opacity={0.55} vectorEffect="non-scaling-stroke" />
            {ev.tipo === 'gol' ? (
              <circle cx={ev.x} cy={yTop + 5} r={5.5} fill="var(--up)" stroke="var(--bg)" strokeWidth={1.6} />
            ) : (
              <rect x={ev.x - 3.5} y={yTop - 1} width={7} height={11} rx={1.5} fill={ev.tipo === 'roja' ? 'var(--down)' : '#eab308'} stroke="var(--bg)" strokeWidth={1} />
            )}
          </g>
        )
      })}

      {chart.lines.map((ln, i) => (
        <path key={'ln' + i} d={ln.d} fill="none" stroke={ln.color} strokeWidth={2.4} strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
      ))}
      {chart.lines.map((ln, i) => (
        <circle key={'dt' + i} cx={ln.dotX} cy={ln.dotY} r={4.2} fill={ln.color} stroke="var(--bg)" strokeWidth={2.5} />
      ))}
      {chart.xLabels.map((xl, i) => (
        <text key={'xl' + i} x={xl.x} y={280} textAnchor={xl.anchor} fontSize={13} fontWeight={600} style={tf}>
          {xl.label}
        </text>
      ))}
    </svg>
  )
}
