import { useEffect, useRef, useState } from 'react'
import type { Chart } from '../lib/chart'

const tf: React.CSSProperties = { fill: 'var(--t3)', fontFamily: 'var(--mono)' }

interface Tip {
  x: number
  y: number
  label: string
  color: string
}

/** Self-contained SVG chart — grid, KO/now markers, lines, dots and axis labels
 *  as native <text> nodes so nothing depends on HTML overlay positioning.
 *  Cada punto de las series es tocable (móvil) o clicable (PC): abre una
 *  burbuja propia con selección · cuota · fecha de captura o minuto. */
export function ChartSvg({ chart, liveMin }: { chart: Chart; liveMin: number }) {
  const [tip, setTip] = useState<Tip | null>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  // al cambiar de mercado/partido la gráfica es otra: la burbuja abierta caduca
  useEffect(() => setTip(null), [chart])

  // el toque en CUALQUIER parte de la gráfica elige el punto más cercano: en
  // el celular el lienzo de 1000 unidades se comprime a ~370px y un objetivo
  // por punto quedaría de ~4px — imposible de acertar con el dedo
  const onTap = (e: React.MouseEvent<SVGSVGElement>) => {
    const svg = svgRef.current
    if (!svg) return
    const r = svg.getBoundingClientRect()
    if (!r.width) return
    const esc = 1000 / r.width // aspecto preservado: misma escala en x e y
    const x = (e.clientX - r.left) * esc
    const y = (e.clientY - r.top) * esc
    let mejor: { p: { x: string; y: string; label: string }; color: string } | null = null
    let mejorD = Infinity
    for (const ln of chart.lines) {
      for (const p of ln.pts) {
        const d = (Number(p.x) - x) ** 2 + (Number(p.y) - y) ** 2
        if (d < mejorD) {
          mejorD = d
          mejor = { p, color: ln.color }
        }
      }
    }
    // umbral generoso (~55 unidades ≈ 20px en pantalla de celular)
    if (!mejor || mejorD > 55 ** 2) {
      setTip(null)
      return
    }
    const nuevo = { x: Number(mejor.p.x), y: Number(mejor.p.y), label: mejor.p.label, color: mejor.color }
    setTip(tip && tip.x === nuevo.x && tip.y === nuevo.y && tip.label === nuevo.label ? null : nuevo)
  }

  // caja del tooltip: ancho por longitud del texto, sin salirse del lienzo
  const tipW = tip ? Math.min(tip.label.length * 7.6 + 20, 460) : 0
  const tipX = tip ? Math.min(Math.max(tip.x - tipW / 2, 58), 984 - tipW) : 0
  const tipArriba = tip ? tip.y > 60 : true
  const tipY = tip ? (tipArriba ? tip.y - 42 : tip.y + 14) : 0

  return (
    <svg
      ref={svgRef}
      viewBox="0 0 1000 300"
      preserveAspectRatio="xMidYMid meet"
      style={{ width: '100%', height: 'auto', display: 'block', cursor: 'pointer', touchAction: 'manipulation' }}
      onClick={onTap}
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

      {/* marcas de captura: el toque lo resuelve onTap por cercanía */}
      {chart.lines.map((ln, i) =>
        ln.pts.map((p, j) => <circle key={'pt' + i + '_' + j} cx={p.x} cy={p.y} r={2.4} fill={ln.color} opacity={0.65} />),
      )}

      {chart.lines.map((ln, i) => (
        <circle key={'dt' + i} cx={ln.dotX} cy={ln.dotY} r={4.2} fill={ln.color} stroke="var(--bg)" strokeWidth={2.5} />
      ))}
      {chart.xLabels.map((xl, i) => (
        <text key={'xl' + i} x={xl.x} y={280} textAnchor={xl.anchor} fontSize={13} fontWeight={600} style={tf}>
          {xl.label}
        </text>
      ))}

      {/* burbuja del punto elegido (reemplaza al <title> nativo del navegador) */}
      {tip && (
        <g style={{ pointerEvents: 'none' }}>
          <circle cx={tip.x} cy={tip.y} r={5} fill={tip.color} stroke="var(--bg)" strokeWidth={2} />
          <rect x={tipX} y={tipY} width={tipW} height={28} rx={7} fill="var(--bg3)" stroke={tip.color} strokeWidth={1.2} />
          <text x={tipX + tipW / 2} y={tipY + 18.5} textAnchor="middle" fontSize={13} fontWeight={700} style={{ fill: 'var(--t1)', fontFamily: 'var(--mono)' }}>
            {tip.label}
          </text>
        </g>
      )}
    </svg>
  )
}
