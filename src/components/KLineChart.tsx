import { useEffect, useState } from 'react'
import type { KCondKey, KTypeKey } from '../data/types'
import { TEAMS } from '../data'
import { FUSED_KEY, fmtK, isMargin, marginQ, signFmt, signedVal } from '../lib/kview'
import type { KSnapshot } from '../motor/types'

interface Props {
  snaps: KSnapshot[]
  kType: KTypeKey
  kCond: KCondKey
  /** Escala compartida entre paneles para comparar de un vistazo. */
  maxAbs: number
  window?: number
}

const W = 460
const H = 216
const L = 16
const R = 448
const MID = 104
const AMP = 84 // px de amplitud vertical para |sv| = maxAbs

/**
 * K acumulada como gráfica de líneas: los "picos acumulados" crecen con la
 * racha y caen a cero en el reseteo. Los partidos de torneos internacionales
 * se marcan con rombo ámbar; los que no actualizan la condición van atenuados.
 */
export function KLineChart({ snaps, kType, kCond, maxAbs, window = 20 }: Props) {
  const key = FUSED_KEY[kType][kCond]
  const win = snaps.slice(-window)
  const n = win.length
  // punto elegido con un toque/clic: burbuja propia (el <title> nativo solo
  // funciona con hover de ratón y en el celular no existe)
  const [sel, setSel] = useState<number | null>(null)
  useEffect(() => setSel(null), [kType, kCond, window, snaps])
  if (!n) return <div style={{ font: '500 11px var(--mono)', color: 'var(--t3)', padding: 20 }}>Sin historia disponible.</div>

  const total = snaps.length
  const x = (i: number) => (n === 1 ? (L + R) / 2 : L + (i / (n - 1)) * (R - L))
  const y = (sv: number) => MID - (sv / maxAbs) * AMP

  const pts = win.map((s, i) => {
    const v = s.fused[key]
    const sv = signedVal(kType, v)
    const inCond = kCond === 'total' || (kCond === 'local') === s.isLocal
    const qc =
      kType === 'ga' ? s.q.golesAnotado
      : kType === 'gr' ? s.q.golesRecibido
      : kType === 'dc' ? s.q.dc
      : isMargin(kType) ? marginQ(kType, s.gf, s.ga, s.rivalLevel)
      : s.isLocal ? s.q.local : s.q.visita
    const rv = TEAMS[s.rival]
    return {
      x: x(i),
      y: y(sv),
      sv,
      reset: v === 0,
      intl: !!s.esInternacional,
      dim: !inCond,
      title:
        `#${total - n + i + 1} · ${s.isLocal ? 'vs' : 'en'} ${rv ? rv.short : s.rival} ${s.gf}-${s.ga}` +
        (s.esInternacional ? ' · internacional' : ' · liga') +
        ` · rival nivel ${s.rivalLevel.toFixed(2)}` +
        (inCond ? ` · q ${qc == null ? '—' : signFmt(qc)}` : ' · no actualiza (otra condición)') +
        ` · K ${fmtK(v)}${v === 0 ? ' (reset)' : ''}`,
      // dos renglones cortos para la burbuja al tocar el punto
      t1:
        `#${total - n + i + 1} · ${s.isLocal ? 'vs' : 'en'} ${rv ? rv.short : s.rival} ${s.gf}-${s.ga}` +
        (s.esInternacional ? ' · internacional' : ''),
      t2:
        `K ${fmtK(v)}${v === 0 ? ' (reset)' : ''}` +
        (inCond ? ` · q ${qc == null ? '—' : signFmt(qc)}` : ' · no actualiza') +
        ` · rival ${s.rivalLevel.toFixed(2)}`,
    }
  })

  const path = pts.map((p, i) => (i ? 'L' : 'M') + p.x.toFixed(1) + ' ' + p.y.toFixed(1)).join(' ')
  const last = pts[n - 1]
  const tf: React.CSSProperties = { fill: 'var(--t3)', fontFamily: 'var(--mono)' }

  const tip = sel != null && sel < n ? pts[sel] : null
  const tipW = tip ? Math.min(Math.max(tip.t1.length, tip.t2.length) * 5.4 + 16, W - 2 * L) : 0
  const tipX = tip ? Math.min(Math.max(tip.x - tipW / 2, L), R - tipW) : 0
  const tipY = tip ? (tip.y > 56 ? tip.y - 42 : tip.y + 12) : 0

  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" style={{ width: '100%', height: 'auto', display: 'block' }} onClick={() => setSel(null)}>
      {/* guías */}
      <line x1={L} x2={R} y1={MID} y2={MID} stroke="var(--grid)" strokeWidth={1} />
      <line x1={L} x2={R} y1={MID - AMP} y2={MID - AMP} stroke="var(--grid)" strokeWidth={0.6} strokeDasharray="3 5" />
      <line x1={L} x2={R} y1={MID + AMP} y2={MID + AMP} stroke="var(--grid)" strokeWidth={0.6} strokeDasharray="3 5" />
      <text x={L} y={MID - AMP - 5} fontSize={10} fontWeight={600} style={{ fill: 'var(--up)', fontFamily: 'var(--mono)' }}>+{fmtK(maxAbs)}</text>
      <text x={L} y={MID + AMP + 13} fontSize={10} fontWeight={600} style={{ fill: 'var(--down)', fontFamily: 'var(--mono)' }}>−{fmtK(maxAbs)}</text>

      {/* línea de picos acumulados */}
      <path d={path} fill="none" stroke="var(--accent)" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" opacity={0.9} />

      {/* puntos por partido (tocables: abren la burbuja con su detalle) */}
      {pts.map((p, i) => {
        const color = p.reset ? 'var(--t3)' : p.sv > 0 ? 'var(--up)' : 'var(--down)'
        const r = p.reset ? 3 : i === n - 1 ? 5.5 : 4
        return (
          <g
            key={i}
            opacity={p.dim ? 0.35 : 1}
            style={{ cursor: 'pointer' }}
            onClick={(e) => {
              e.stopPropagation()
              setSel(sel === i ? null : i)
            }}
          >
            <circle cx={p.x} cy={p.y} r={11} fill="transparent" />
            {p.intl ? (
              // internacional: rombo ámbar SÓLIDO — punto de otro color, no
              // solo otro borde; la racha +/− queda en el tooltip
              <rect
                x={p.x - r} y={p.y - r} width={r * 2} height={r * 2}
                transform={`rotate(45 ${p.x} ${p.y})`}
                fill={p.reset ? 'var(--bg)' : 'var(--mark)'}
                stroke="var(--mark)" strokeWidth={1.8}
              >
                <title>{p.title}</title>
              </rect>
            ) : (
              <circle cx={p.x} cy={p.y} r={r} fill={p.reset ? 'var(--bg)' : color} stroke={p.reset ? 'var(--t3)' : 'var(--bg)'} strokeWidth={p.reset ? 1.5 : 1.5}>
                <title>{p.title}</title>
              </circle>
            )}
          </g>
        )
      })}

      {/* valor actual */}
      <text
        x={Math.min(last.x, R - 4)} y={last.y + (last.sv >= 0 ? -10 : 18)}
        textAnchor="end" fontSize={13} fontWeight={700}
        style={{ fill: last.reset ? 'var(--t3)' : last.sv > 0 ? 'var(--up)' : 'var(--down)', fontFamily: 'var(--mono)' }}
      >
        {signFmt(last.sv)}
      </text>

      {/* eje x */}
      <text x={L} y={H - 2} fontSize={10} fontWeight={600} style={tf}>hace {n} partidos</text>
      <text x={R} y={H - 2} textAnchor="end" fontSize={10} fontWeight={600} style={tf}>último</text>

      {/* burbuja del punto elegido */}
      {tip && (
        <g style={{ pointerEvents: 'none' }}>
          <circle cx={tip.x} cy={tip.y} r={7} fill="none" stroke={tip.intl ? 'var(--mark)' : 'var(--accent)'} strokeWidth={1.6} />
          <rect x={tipX} y={tipY} width={tipW} height={30} rx={6} fill="var(--bg3)" stroke={tip.intl ? 'var(--mark)' : 'var(--accent)'} strokeWidth={1.1} />
          <text x={tipX + tipW / 2} y={tipY + 12.5} textAnchor="middle" fontSize={9.5} fontWeight={700} style={{ fill: 'var(--t1)', fontFamily: 'var(--mono)' }}>{tip.t1}</text>
          <text x={tipX + tipW / 2} y={tipY + 24} textAnchor="middle" fontSize={9.5} fontWeight={600} style={{ fill: 'var(--t2)', fontFamily: 'var(--mono)' }}>{tip.t2}</text>
        </g>
      )}
    </svg>
  )
}

export function KLineLegend() {
  const item: React.CSSProperties = { display: 'flex', alignItems: 'center', gap: 5, font: '500 9.5px var(--mono)', color: 'var(--t3)' }
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 6 }}>
      <span style={item}><span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--up)' }}></span>racha +</span>
      <span style={item}><span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--down)' }}></span>racha −</span>
      <span style={item}><span style={{ width: 8, height: 8, borderRadius: '50%', border: '1.5px solid var(--t3)' }}></span>reset</span>
      <span style={item}><span style={{ width: 8, height: 8, background: 'var(--mark)', transform: 'rotate(45deg)' }}></span>torneo internacional</span>
    </div>
  )
}
