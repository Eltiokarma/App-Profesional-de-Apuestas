import { useEffect, useRef, useState } from 'react'
import type { KCondKey, KTypeKey } from '../data/types'
import { TEAMS } from '../data'
import { type Cond, condEtiquetas, FUSED_KEY, fmtK, isMargin, marginQ, puntosEtiquetados, signFmt, signedVal } from '../lib/kview'
import type { KSnapshot } from '../motor/types'

interface Props {
  snaps: KSnapshot[]
  kType: KTypeKey
  kCond: KCondKey
  /** Escala compartida entre paneles para comparar de un vistazo. */
  maxAbs: number
  window?: number
  /** Condición del equipo que se analiza (Local/Visitante del partido). Fija
   *  cuáles son los dos puntos extra con valor visible; con el toggle en Local
   *  o Visita manda el toggle (ver condEtiquetas). */
  rol?: Cond
}

const W = 460
const H = 216
const L = 16
const R = 448
const MID = 104
const AMP = 84 // px de amplitud vertical para |sv| = maxAbs

const MES_CORTO = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
/** '12 abr 26' — cuándo ocurrió el punto; '' si el dato no existe (demo). */
const fmtFecha = (iso?: string): string => {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return ''
  return `${d.getDate()} ${MES_CORTO[d.getMonth()]} ${String(d.getFullYear()).slice(2)}`
}

/**
 * K acumulada como gráfica de líneas: los "picos acumulados" crecen con la
 * racha y caen a cero en el reseteo. Los partidos de torneos internacionales
 * se marcan con rombo ámbar; los que no actualizan la condición van atenuados.
 */
export function KLineChart({ snaps, kType, kCond, maxAbs, window = 20, rol }: Props) {
  const key = FUSED_KEY[kType][kCond]
  const win = snaps.slice(-window)
  const n = win.length
  // punto elegido con un toque/clic: burbuja propia (el <title> nativo solo
  // funciona con hover de ratón y en el celular no existe)
  const [sel, setSel] = useState<number | null>(null)
  const svgRef = useRef<SVGSVGElement>(null)
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
    const fch = fmtFecha(s.fecha)
    return {
      x: x(i),
      y: y(sv),
      sv,
      reset: v === 0,
      intl: !!s.esInternacional,
      dim: !inCond,
      title:
        `#${total - n + i + 1} · ${s.isLocal ? 'vs' : 'en'} ${rv ? rv.short : s.rival} ${s.gf}-${s.ga}` +
        (fch ? ` · ${fch}` : '') +
        (s.esInternacional ? ' · internacional' : ' · liga') +
        ` · rival nivel ${s.rivalLevel.toFixed(2)}` +
        (inCond ? ` · q ${qc == null ? '—' : signFmt(qc)}` : ' · no actualiza (otra condición)') +
        ` · K ${fmtK(v)}${v === 0 ? ' (reset)' : ''}`,
      // dos renglones cortos para la burbuja al tocar el punto: el primero
      // lleva la FECHA para ubicar cuándo ocurrió el evento
      t1:
        `#${total - n + i + 1} · ${s.isLocal ? 'vs' : 'en'} ${rv ? rv.short : s.rival} ${s.gf}-${s.ga}` +
        (fch ? ` · ${fch}` : '') +
        (s.esInternacional ? ' · internacional' : ''),
      t2:
        `K ${fmtK(v)}${v === 0 ? ' (reset)' : ''}` +
        (inCond ? ` · q ${qc == null ? '—' : signFmt(qc)}` : ' · no actualiza') +
        ` · rival ${s.rivalLevel.toFixed(2)}`,
    }
  })

  const path = pts.map((p, i) => (i ? 'L' : 'M') + p.x.toFixed(1) + ' ' + p.y.toFixed(1)).join(' ')
  const tf: React.CSSProperties = { fill: 'var(--t3)', fontFamily: 'var(--mono)' }

  // TRES valores a la vista, no solo el último: el último partido y los dos
  // últimos de la condición que se analiza (de local o de visitante). El del
  // último partido va grande a la derecha; los otros dos, con anillo sobre su
  // punto y prefijo L/V para saber de qué condición hablan.
  const cond = condEtiquetas(kCond, rol, win[n - 1].isLocal)
  const marca = cond === 'local' ? 'L' : 'V'
  const colorDe = (p: (typeof pts)[number]) => (p.reset ? 'var(--t3)' : p.sv > 0 ? 'var(--up)' : 'var(--down)')
  const puestas: { x: number; y: number }[] = []
  const etiquetas = puntosEtiquetados(
    n,
    (i) => win[i].isLocal === (cond === 'local'),
    (i) => signFmt(pts[i].sv),
  ).map((i, orden) => {
    const p = pts[i]
    const principal = orden === 0
    const ancho = principal ? 34 : 44 // px aprox. del texto, para no solaparlos
    const x = principal ? Math.min(p.x, R - 4) : Math.min(Math.max(p.x, L + ancho / 2), R - ancho / 2)
    // arriba si la racha es positiva (el hueco está de ese lado); si el sitio
    // ya está ocupado por otra etiqueta, se prueba el lado contrario
    let arriba = p.sv >= 0
    const alto = principal ? 10 : 13 // hueco sobre el punto (el anillo mide 7.5)
    let y = p.y + (arriba ? -alto : alto + 8)
    const choca = (yy: number) => puestas.some((q) => Math.abs(q.x - x) < ancho && Math.abs(q.y - yy) < 11)
    if (choca(y)) {
      arriba = !arriba
      y = p.y + (arriba ? -alto : alto + 8)
      while (choca(y)) y += arriba ? -12 : 12
    }
    y = Math.min(Math.max(y, 11), H - 16)
    puestas.push({ x, y })
    return { i, x, y, principal, texto: (principal ? '' : marca + ' ') + signFmt(p.sv), color: colorDe(p), px: p.x, py: p.y }
  })

  const tip = sel != null && sel < n ? pts[sel] : null
  const tipW = tip ? Math.min(Math.max(tip.t1.length, tip.t2.length) * 5.4 + 16, W - 2 * L) : 0
  const tipX = tip ? Math.min(Math.max(tip.x - tipW / 2, L), R - tipW) : 0
  const tipY = tip ? (tip.y > 56 ? tip.y - 42 : tip.y + 12) : 0

  // toque en cualquier parte → punto más cercano (en celular el lienzo se
  // comprime y un objetivo por punto sería demasiado pequeño para el dedo)
  const onTap = (e: React.MouseEvent<SVGSVGElement>) => {
    const svg = svgRef.current
    if (!svg) return
    const r = svg.getBoundingClientRect()
    if (!r.width) return
    const esc = W / r.width
    const x = (e.clientX - r.left) * esc
    const y = (e.clientY - r.top) * esc
    let mejor = -1
    let mejorD = Infinity
    pts.forEach((p, i) => {
      const d = (p.x - x) ** 2 + (p.y - y) ** 2
      if (d < mejorD) {
        mejorD = d
        mejor = i
      }
    })
    // umbral ~28 unidades ≈ 22px en pantalla de celular
    if (mejor < 0 || mejorD > 28 ** 2) setSel(null)
    else setSel(sel === mejor ? null : mejor)
  }

  return (
    <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" style={{ width: '100%', height: 'auto', display: 'block', cursor: 'pointer', touchAction: 'manipulation' }} onClick={onTap}>
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
          <g key={i} opacity={p.dim ? 0.35 : 1}>
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

      {/* valores a la vista: último · último y penúltimo de la condición */}
      {etiquetas.map((e) => (
        <g key={e.i}>
          {!e.principal && <circle cx={e.px} cy={e.py} r={7.5} fill="none" stroke={e.color} strokeWidth={1.2} opacity={0.6} />}
          <text
            x={e.x} y={e.y}
            textAnchor={e.principal ? 'end' : 'middle'} fontSize={e.principal ? 13 : 10.5} fontWeight={700}
            // halo del color del lienzo: el número se lee aunque caiga sobre la línea
            style={{ fill: e.color, fontFamily: 'var(--mono)', stroke: 'var(--bg)', strokeWidth: 3, paintOrder: 'stroke', strokeLinejoin: 'round' }}
          >
            {e.texto}
          </text>
        </g>
      ))}

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
      <span style={item}><span style={{ width: 9, height: 9, borderRadius: '50%', border: '1.2px solid var(--t2)' }}></span>L/V = últimos dos de local (o de visita)</span>
    </div>
  )
}
