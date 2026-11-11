import { useEffect, useRef, useState } from 'react'
import type { ApuestaSimulada, EstrategiaClave, EstrategiaSimulada, FrenoTramo, GrupoAlerta, GrupoSemaforo, Resultado1x2, ResumenAlerta, ResumenSemaforo, SimulacionApuesta, TrasFallos } from '../api/types'
import { SemaforoChip } from '../components/SemaforoChip'
import { getDataSource } from '../services/datasource'
import { useAsync } from '../services/useAsync'

/** SIMULACIÓN DE APUESTA (28/10/2026, pedido del usuario): qué habría pasado
 *  con una banca apostando con nuestros 1X2 desde los partidos de ese día. La
 *  cuenta la hace el backend (`backend/analisis/simulacion.py`) y se rehace al
 *  leer; la pantalla solo elige qué fracción de Kelly mirar. Cada apuesta trae
 *  la versión de los skills con la que se escribió su parte.
 *  EL MÉTODO (03/11/2026, docs/METODO_APUESTA.md) va primero: 1 % de la banca
 *  al elegido con un freno por tramo de confianza; su tarjeta dice cómo está
 *  hoy cada tramo. */

type Kelly = 'kelly' | 'kellyMedio' | 'kellyCuarto'
const KELLY_OPC: [Kelly, string][] = [['kelly', 'entero'], ['kellyMedio', '½'], ['kellyCuarto', '¼']]
const COLOR: Record<'proporcional' | 'metodoVerde' | 'plana' | 'plana60' | 'kelly' | 'martingala' | 'martingala60', string> = {
  proporcional: 'var(--sim-proporcional)', metodoVerde: 'var(--sim-metodo-verde)', plana: 'var(--sim-plana)', plana60: 'var(--sim-plana60)', kelly: 'var(--sim-kelly)', martingala: 'var(--sim-martingala)',
  martingala60: 'var(--sim-martingala60)',
}
const RES: Record<Resultado1x2, string> = { local: 'Local', empate: 'Empate', visita: 'Visita' }
const SKILL_CORTO: [string, string][] = [
  ['sad-analysis', 'sad'], ['efe-clasificador', 'EFE'], ['teorema-del-echado', 'TDE'], ['diagnostico-tactico', 'DTP'],
]
const CORTO: Record<EstrategiaClave, string> = {
  proporcional: 'Método', metodoVerde: 'Método 🟢', plana: 'Plana', plana60: 'Plana 60 %+', kelly: 'Kelly', kellyMedio: 'Kelly ½', kellyCuarto: 'Kelly ¼', martingala: 'Martingala', martingala60: 'Martin. 60 %+',
}
const MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

/** «2026-10-28 20:00:00» (UTC) → «28 oct 15:00» en hora local del navegador */
function fecha(utc: string | null): string {
  if (!utc) return ''
  const d = new Date(utc.replace(' ', 'T') + 'Z')
  if (isNaN(d.getTime())) return utc
  return `${d.getDate()} ${MES[d.getMonth()]} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
const num = (x: number, d = 2) => x.toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
// el signo sale del número YA redondeado: −0,004 no se escribe «−0.00»
const signo = (x: number, d = 2) => {
  const r = Number(x.toFixed(d))
  return (r > 0 ? '+' : r < 0 ? '−' : '') + num(Math.abs(r), d)
}
const pct = (x: number | null, d = 1) => (x == null ? '—' : signo(100 * x, d) + ' %')
const colorDe = (x: number | null) => (x == null || x === 0 ? 'var(--t2)' : x > 0 ? 'var(--up)' : 'var(--down)')

const tarjeta: React.CSSProperties = { background: 'var(--bg2)', border: '1px solid var(--line)', borderRadius: 12, padding: '13px 14px', minWidth: 0 }
const rotulo: React.CSSProperties = { font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px', textTransform: 'uppercase' }

export function Simulacion({ isMobile }: { isMobile: boolean }) {
  const sim = useAsync<SimulacionApuesta>(() => getDataSource().simulacion(), 'simulacion')
  const [kelly, setKelly] = useState<Kelly>('kelly')

  const pad = isMobile ? '16px 14px 40px' : '22px 26px 48px'
  if (sim.loading && !sim.data) return <div style={{ padding: pad, font: '500 12px var(--sans)', color: 'var(--t3)' }}>Simulando…</div>
  if (sim.error || !sim.data) {
    return (
      <div style={{ padding: pad, display: 'flex', gap: 10, alignItems: 'center' }}>
        <span style={{ font: '500 12px var(--sans)', color: 'var(--down)' }}>No se pudo leer la simulación: {sim.error ?? 'sin datos'}</span>
        <button onClick={sim.reload} style={{ padding: '4px 10px', border: '1px solid var(--line)', borderRadius: 7, cursor: 'pointer', background: 'var(--bg3)', color: 'var(--t1)', font: '600 10.5px var(--sans)' }}>Reintentar</button>
      </div>
    )
  }
  const d = sim.data
  const est = (c: EstrategiaClave) => d.estrategias.find((e) => e.clave === c)!
  const visibles: { clave: EstrategiaClave; color: string }[] = [
    { clave: 'proporcional', color: COLOR.proporcional },
    // el método solo en verde (11/11/2026): en papel, para medir el semáforo
    ...(d.estrategias.some((e) => e.clave === 'metodoVerde') ? [{ clave: 'metodoVerde' as EstrategiaClave, color: COLOR.metodoVerde }] : []),
    { clave: 'plana', color: COLOR.plana }, { clave: 'plana60', color: COLOR.plana60 }, { clave: kelly, color: COLOR.kelly }, { clave: 'martingala', color: COLOR.martingala },
    { clave: 'martingala60', color: COLOR.martingala60 },
  ]
  const cerradas = [...d.apuestas].reverse().filter((a) => a.estado === 'cerrada')

  return (
    <div style={{ padding: pad, maxWidth: 1080 }}>
      <h1 style={{ font: '800 26px var(--sans)', color: 'var(--t1)', margin: '0 0 4px' }}>Simulación de apuesta</h1>
      <div style={{ font: '500 12px var(--sans)', color: 'var(--t3)', marginBottom: 12, lineHeight: 1.45 }}>
        Banca de {num(d.bancaInicial, 0)} unidades sobre nuestros 1X2 desde los partidos del {fecha(d.desde).split(' ').slice(0, 2).join(' ')} ·{' '}
        {d.cerradas} cerradas ({d.aciertos} aciertos del elegido) · {d.pendientes} por jugarse
      </div>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center', marginBottom: 12 }}>
        <span style={{ ...rotulo, marginRight: 2 }}>Kelly</span>
        {KELLY_OPC.map(([k, et]) => {
          const on = kelly === k
          return (
            <button key={k} onClick={() => setKelly(k)}
              style={{ padding: '5px 11px', borderRadius: 8, border: `1px solid ${on ? 'var(--accent)' : 'var(--line)'}`, background: on ? 'var(--bg3)' : 'transparent', color: on ? 'var(--t1)' : 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
              {et}
            </button>
          )
        })}
        {sim.loading && <span style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>actualizando…</span>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: isMobile ? 'minmax(0,1fr)' : 'repeat(3, minmax(0,1fr))', gap: 10, marginBottom: 12 }}>
        {visibles.map((v) => <TarjetaEstrategia key={v.clave} e={est(v.clave)} color={v.color} />)}
      </div>

      <div style={{ ...tarjeta, marginBottom: 12 }}>
        <div style={{ ...rotulo, marginBottom: 8 }}>Evolución de la banca · partido a partido</div>
        {cerradas.length ? (
          <GraficaBanca cerradas={cerradas} series={visibles.map((v) => ({ ...v, nombre: est(v.clave).nombre }))} inicial={d.bancaInicial} />
        ) : (
          <div style={{ padding: '26px 8px', textAlign: 'center', font: '500 12px var(--sans)', color: 'var(--t3)' }}>
            Todavía no hay partidos cerrados desde el inicio de la simulación: la curva aparece con el primer resultado.
          </div>
        )}
      </div>

      {d.porVersion.length > 0 && <PorVersion d={d} visibles={visibles.map((v) => v.clave)} isMobile={isMobile} />}

      {d.trasFallos && d.trasFallos.base.n > 0 && <TablaTrasFallos t={d.trasFallos} isMobile={isMobile} />}

      {d.semaforo && <TablaSemaforo r={d.semaforo} isMobile={isMobile} />}

      {d.alertaConfianza && <TablaAlerta r={d.alertaConfianza} isMobile={isMobile} />}

      <div style={{ ...rotulo, margin: '18px 0 8px' }}>Apuestas · la más nueva primero</div>
      {d.apuestas.length ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {d.apuestas.map((a) => <FilaApuesta key={a.fixtureId} a={a} visibles={visibles} />)}
        </div>
      ) : (
        <div style={{ ...tarjeta, textAlign: 'center', font: '500 12px var(--sans)', color: 'var(--t3)' }}>
          Sin partes con 1X2 y cuotas desde el inicio de la simulación.
        </div>
      )}

      {d.excluidos.length > 0 && (
        <details style={{ marginTop: 14 }}>
          <summary style={{ cursor: 'pointer', font: '600 11.5px var(--sans)', color: 'var(--t2)' }}>
            {d.excluidos.length} partido{d.excluidos.length === 1 ? '' : 's'} con parte que no entra{d.excluidos.length === 1 ? '' : 'n'} a la simulación
          </summary>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 8 }}>
            {d.excluidos.map((x) => (
              <div key={x.fixtureId} style={{ font: '500 11px var(--sans)', color: 'var(--t2)' }}>
                <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>{fecha(x.pitazo)}</span> · {x.partido.local} – {x.partido.visita}: <span style={{ color: 'var(--t3)' }}>{x.motivo}</span>
              </div>
            ))}
          </div>
        </details>
      )}

      <div style={{ marginTop: 16, font: '500 11px var(--sans)', color: 'var(--t3)', lineHeight: 1.5 }}>
        {d.estrategias.filter((e) => ['proporcional', 'metodoVerde', 'plana', 'plana60', kelly, 'martingala', 'martingala60'].includes(e.clave)).map((e) => (
          <div key={e.clave}><b style={{ color: 'var(--t2)' }}>{e.nombre}</b>: {e.descripcion}.</div>
        ))}
        <div style={{ marginTop: 6 }}>{d.nota}.</div>
      </div>
    </div>
  )
}

function TarjetaEstrategia({ e, color }: { e: EstrategiaSimulada; color: string }) {
  const metodo = e.clave === 'proporcional'
  return (
    <div style={{ ...tarjeta, ...(metodo ? { borderColor: color, boxShadow: `inset 3px 0 0 ${color}` } : {}) }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 6, flexWrap: 'wrap' }}>
        <span style={{ width: 10, height: 3, borderRadius: 2, background: color, flexShrink: 0 }} />
        <span style={{ font: '700 12px var(--sans)', color: 'var(--t1)' }}>{e.nombre}</span>
        {metodo && <span style={{ ...rotulo, color, marginLeft: 'auto' }}>el método</span>}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
        <span style={{ font: '800 24px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{num(e.banca)}</span>
        <span style={{ font: '700 12px var(--mono)', color: colorDe(e.ganancia), fontVariantNumeric: 'tabular-nums' }}>{signo(e.ganancia)} u</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: '4px 10px', marginTop: 8, font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
        <span>ROI <b style={{ color: colorDe(e.roi) }}>{pct(e.roi)}</b></span>
        <span>apuestas {e.apuestas} · ganó {e.ganadas}</span>
        <span>apostado {num(e.apostado)}</span>
        <span>caída máx. {num(100 * e.caidaMaxima, 1)} %</span>
        <span title="lo más que estuvo en juego a la vez">en juego máx. {num(e.exposicionMaxima)}</span>
        <span>apuesta máx. {num(e.montoMaximo)}</span>
      </div>
      {e.quebro != null && <div style={{ marginTop: 6, font: '700 10.5px var(--sans)', color: 'var(--down)' }}>La banca quebró (partido {e.quebro}).</div>}
      {e.lineas && e.lineas.abiertas > 0 && e.quebro == null && (
        <div style={{ marginTop: 6, font: '500 10.5px var(--sans)', color: 'var(--t2)' }}>
          {e.lineas.abiertas} línea{e.lineas.abiertas === 1 ? '' : 's'} abierta{e.lineas.abiertas === 1 ? '' : 's'}
          {e.lineas.perdiendo > 0
            ? ` · ${e.lineas.perdiendo} viene${e.lineas.perdiendo === 1 ? '' : 'n'} de perder (la más cargada va por ${num(e.lineas.proximoMayor)} u)`
            : ' · todas en 1 u'}
        </div>
      )}
      {e.tramos && <FrenoTramos tramos={e.tramos} />}
      {e.apuestas === 0 && e.clave.startsWith('kelly') && (
        <div style={{ marginTop: 6, font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>Sin apuestas: en ningún partido nuestra probabilidad superó lo que paga la cuota.</div>
      )}
    </div>
  )
}

/** El freno del método por tramo: cuánto acertó en sus últimos 50 contra lo que pedía la cuota */
function FrenoTramos({ tramos }: { tramos: FrenoTramo[] }) {
  return (
    <div style={{ marginTop: 9, paddingTop: 8, borderTop: '1px solid var(--line)' }}>
      <div style={{ ...rotulo, marginBottom: 5 }}>Freno por tramo · acierta / pide la cuota</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: '3px 10px', font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
        {tramos.map((t) => (
          <span key={t.tramo} title={t.n ? `${t.aciertos} de ${t.n}${t.z != null ? ` · z ${signo(t.z, 1)}` : ''}` : 'sin partidos cerrados'}>
            <b style={{ color: 'var(--t1)' }}>{t.tramo}</b>{' '}
            {t.n && t.tasa != null && t.pide != null ? (
              <>
                <span style={{ color: t.tasa >= t.pide ? 'var(--up)' : 'var(--down)' }}>{num(100 * t.tasa, 0)}</span>/{num(100 * t.pide, 0)} %
                {t.pausado ? <b style={{ color: 'var(--down)' }}> · pausa</b> : <span style={{ color: 'var(--t3)' }}> · n {t.n}</span>}
              </>
            ) : <span style={{ color: 'var(--t3)' }}>sin datos</span>}
          </span>
        ))}
      </div>
    </div>
  )
}

function GraficaBanca({ cerradas, series, inicial }: {
  cerradas: ApuestaSimulada[]; series: { clave: EstrategiaClave; color: string; nombre: string }[]; inicial: number
}) {
  const caja = useRef<HTMLDivElement>(null)
  const [ancho, setAncho] = useState(600)
  const [hover, setHover] = useState<number | null>(null)
  useEffect(() => {
    const el = caja.current
    if (!el) return
    const ro = new ResizeObserver(() => setAncho(el.clientWidth || 600))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  const H = 220
  const m = { t: 10, r: 12, b: 22, l: 44 }
  const n = cerradas.length
  const valores = series.map((s) => [inicial, ...cerradas.map((a) => a.porEstrategia[s.clave]?.banca ?? inicial)])
  const todos = valores.flat()
  let lo = Math.min(...todos, inicial)
  let hi = Math.max(...todos, inicial)
  if (hi - lo < 4) { lo -= 2; hi += 2 }
  const margen = (hi - lo) * 0.08
  lo -= margen; hi += margen
  const x = (i: number) => m.l + (n ? (i / n) * (ancho - m.l - m.r) : 0)
  const y = (v: number) => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b)
  const ticks = [lo + margen, inicial, hi - margen].filter((v, i, arr) => arr.findIndex((w) => Math.abs(w - v) < (hi - lo) * 0.08) === i)

  const mover = (e: React.PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    const i = Math.round(((e.clientX - r.left - m.l) / (ancho - m.l - m.r)) * n)
    setHover(Math.max(0, Math.min(n, i)))
  }
  const a = hover != null && hover > 0 ? cerradas[hover - 1] : null

  return (
    <div ref={caja} style={{ position: 'relative' }}>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 6 }}>
        {series.map((s) => (
          <span key={s.clave} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, font: '600 10.5px var(--sans)', color: 'var(--t2)' }}>
            <span style={{ width: 14, height: 2, borderRadius: 1, background: s.color }} />{s.nombre}
          </span>
        ))}
      </div>
      <svg width={ancho} height={H} style={{ display: 'block', touchAction: 'pan-y' }}
        onPointerMove={mover} onPointerDown={mover} onPointerLeave={() => setHover(null)}>
        {ticks.map((v) => (
          <g key={v}>
            <line x1={m.l} x2={ancho - m.r} y1={y(v)} y2={y(v)} stroke="var(--grid)" strokeWidth={1}
              strokeDasharray={Math.abs(v - inicial) < 1e-9 ? '4 4' : undefined} />
            <text x={m.l - 6} y={y(v) + 3.5} textAnchor="end" style={{ fill: 'var(--t3)', font: '500 10px var(--mono)' }}>{num(v, 0)}</text>
          </g>
        ))}
        <text x={m.l} y={H - 6} style={{ fill: 'var(--t3)', font: '500 10px var(--mono)' }}>inicio</text>
        <text x={ancho - m.r} y={H - 6} textAnchor="end" style={{ fill: 'var(--t3)', font: '500 10px var(--mono)' }}>{n} partido{n === 1 ? '' : 's'}</text>
        {series.map((s, si) => (
          <polyline key={s.clave} fill="none" stroke={s.color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round"
            points={valores[si].map((v, i) => `${x(i)},${y(v)}`).join(' ')} />
        ))}
        {hover != null && (
          <g>
            <line x1={x(hover)} x2={x(hover)} y1={m.t} y2={H - m.b} stroke="var(--t3)" strokeWidth={1} />
            {series.map((s, si) => (
              <circle key={s.clave} cx={x(hover)} cy={y(valores[si][hover])} r={4.5} fill={s.color} stroke="var(--bg2)" strokeWidth={2} />
            ))}
          </g>
        )}
      </svg>
      {hover != null && (
        <div style={{
          position: 'absolute', top: 24, [x(hover) > ancho / 2 ? 'right' : 'left']: x(hover) > ancho / 2 ? ancho - x(hover) + 10 : x(hover) + 10,
          background: 'var(--bg1)', border: '1px solid var(--line2)', borderRadius: 9, padding: '8px 10px', boxShadow: 'var(--shadow)',
          pointerEvents: 'none', maxWidth: 230, font: '500 10.5px var(--sans)', color: 'var(--t2)',
        }}>
          <div style={{ font: '700 11px var(--sans)', color: 'var(--t1)', marginBottom: 4 }}>
            {a ? `${a.partido.local} – ${a.partido.visita}` : 'Banca inicial'}
          </div>
          {a && <div style={{ marginBottom: 4 }}>{fecha(a.pitazo)} · salió {a.resultado ? RES[a.resultado] : '—'} · sad {a.versiones['sad-analysis'] || '—'}</div>}
          {series.map((s, si) => (
            <div key={s.clave} style={{ display: 'flex', alignItems: 'center', gap: 6, fontVariantNumeric: 'tabular-nums' }}>
              <span style={{ width: 8, height: 2, background: s.color }} />
              <span style={{ flex: 1 }}>{s.nombre}</span>
              <b style={{ color: 'var(--t1)', font: '700 10.5px var(--mono)' }}>{num(valores[si][hover])}</b>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/** CRITERIO DE CONTACTO (04/11/2026): ¿después de varios fallos seguidos acertamos más? Es lo que
 *  la martingala cobra. La regla para tomarlo en serio está fijada de antemano y no se mueve. */
function TablaTrasFallos({ t, isMobile }: { t: TrasFallos; isMobile: boolean }) {
  const c = t.contacto
  const ic = (i: [number, number] | null) => (i ? `${num(100 * i[0], 0)}-${num(100 * i[1], 0)} %` : '—')
  const tasa = (x: number | null) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const color = c.estado === 'contacto' ? 'var(--up)' : c.estado === 'sin_contacto' ? 'var(--t2)' : 'var(--mark)'
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>Criterio de contacto · acierto tras fallos seguidos</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        Es lo que la martingala cobra: si después de varios fallos acertamos más que el promedio. Se toma en serio con{' '}
        {c.nMinimo}+ casos tras {c.k} fallos, {num(100 * c.tasaMinima, 0)} %+ de acierto y el intervalo entero sobre el promedio.
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)' }}>
              <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}>después de</th>
              <th style={{ ...celda, fontWeight: 600 }}>casos</th>
              <th style={{ ...celda, fontWeight: 600 }}>acierta</th>
              <th style={{ ...celda, fontWeight: 600 }}>IC 95 %</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderTop: '1px solid var(--line)' }}>
              <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700 }}>promedio</td>
              <td style={celda}>{t.base.n}</td>
              <td style={{ ...celda, color: 'var(--t1)', fontWeight: 700 }}>{tasa(t.base.tasa)}</td>
              <td style={celda}>{ic(t.base.intervalo)}</td>
            </tr>
            {t.porK.map((f) => {
              const arriba = f.tasa != null && t.base.tasa != null && f.tasa > t.base.tasa
              return (
                <tr key={f.k} style={{ borderTop: '1px solid var(--line)', background: f.k === c.k ? 'var(--bg3)' : undefined }}>
                  <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: f.k === c.k ? 700 : 500 }}>
                    {f.k} fallo{f.k === 1 ? '' : 's'}
                  </td>
                  <td style={celda}>{f.n}</td>
                  <td style={{ ...celda, fontWeight: 700, color: f.tasa == null ? 'var(--t3)' : arriba ? 'var(--up)' : 'var(--down)' }}>{tasa(f.tasa)}</td>
                  <td style={celda}>{ic(f.intervalo)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 8, font: '600 11px var(--sans)', color, lineHeight: 1.45 }}>
        {c.estado === 'en_observacion' ? `En observación: ${c.n} de ${c.nMinimo} casos tras ${c.k} fallos (faltan ${c.faltan}).`
          : c.estado === 'contacto' ? 'Contacto: el criterio se cumple. Tomarlo en serio.' : 'Sin contacto: con los casos suficientes, el criterio no se cumple.'}
      </div>
    </div>
  )
}

// el estado del criterio por escalones (11/11/2026), cada uno con su color
const ESTADO_SEMAFORO: Record<ResumenSemaforo['criterio']['estado'], { etiqueta: string; color: string; fondo: string }> = {
  en_observacion: { etiqueta: 'EN OBSERVACIÓN', color: 'var(--t2)', fondo: 'var(--bg3)' },
  prometedor: { etiqueta: 'PROMETEDOR', color: 'color-mix(in oklch, var(--up) 55%, var(--mark))', fondo: 'color-mix(in oklch, color-mix(in oklch, var(--up) 55%, var(--mark)), transparent 84%)' },
  confirmado: { etiqueta: 'CONFIRMADO', color: 'var(--up)', fondo: 'color-mix(in oklch, var(--up), transparent 84%)' },
  no_se_sostiene: { etiqueta: 'NO SE SOSTIENE', color: 'var(--down)', fondo: 'color-mix(in oklch, var(--down), transparent 84%)' },
  sin_contacto: { etiqueta: 'SIN CONTACTO', color: 'var(--t2)', fondo: 'var(--bg3)' },
}

/** EL SEMÁFORO DEL ELEGIDO (11/11/2026): verdes contra amarillos, contra lo que pedía la
 *  cuota. Cuenta para el criterio SOLO lo nuevo (desde el 11/11); la regla está fijada. */
function TablaSemaforo({ r, isMobile }: { r: ResumenSemaforo; isMobile: boolean }) {
  const tasa = (x: number | null | undefined) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const ic = (i: [number, number] | null) => (i ? `${num(100 * i[0], 0)}-${num(100 * i[1], 0)} %` : '—')
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  const c = r.criterio
  const est = ESTADO_SEMAFORO[c.estado] ?? ESTADO_SEMAFORO.en_observacion
  const bloques: [string, ResumenSemaforo['nuevo']][] = [[`desde el ${fecha(r.desde).split(' ').slice(0, 2).join(' ')} (cuenta)`, r.nuevo], ['todo lo simulado', r.todo]]
  const filas: [string, keyof ResumenSemaforo['nuevo']][] = [['🟢 verde', 'verde'], ['🟡 amarillo', 'amarillo'], ['⚪ sin dato', 'sinDato']]
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>Semáforo del elegido · verdes contra amarillos</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        Verde: nuestro 1X2 a ≤ {num(r.umbral, 0)} pts de la casa en los tres resultados y el marcador declarado con el elegido.
        Por escalones de verdes nuevos ({c.escalones.join(' · ')}): en {c.escalones.slice(0, -1).join(' y ')}, prometedor si el
        intervalo queda entero sobre lo que pedía la cuota; en {c.nMinimo}, confirmado con el elegido {num(100 * c.ventajaMinima, 0)}+ pts
        sobre lo que pedía, el intervalo encima y los amarillos por debajo. En cualquier escalón, no se sostiene si acierta menos de lo que pedía.
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: 'var(--bg3)', font: '700 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          {c.escalon ? `escalón ${c.escalon}` : 'antes del escalón 70'}
        </span>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: est.fondo, font: '700 10.5px var(--mono)', color: est.color, letterSpacing: '.3px' }}>
          {est.etiqueta}
        </span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
          {c.n} verdes{c.proximoEscalon ? ` · faltan ${c.faltan} para el ${c.proximoEscalon}` : ''}
        </span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)' }}>
              <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}></th>
              <th style={{ ...celda, fontWeight: 600 }}>casos</th>
              <th style={{ ...celda, fontWeight: 600 }}>acierta</th>
              <th style={{ ...celda, fontWeight: 600 }}>pedía</th>
              <th style={{ ...celda, fontWeight: 600 }}>±</th>
              <th style={{ ...celda, fontWeight: 600 }}>IC 95 %</th>
              <th style={{ ...celda, fontWeight: 600 }}>1 u plano</th>
            </tr>
          </thead>
          {bloques.map(([titulo, g]) => (
            <tbody key={titulo}>
              <tr><td colSpan={7} style={{ ...celda, textAlign: 'left', paddingTop: 9, font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px' }}>{titulo.toUpperCase()}</td></tr>
              {filas.map(([nombre, k]) => {
                const x: GrupoSemaforo = g[k]
                return (
                  <tr key={k} style={{ borderTop: '1px solid var(--line)' }}>
                    <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700, fontFamily: 'var(--sans)', whiteSpace: 'nowrap' }}>{nombre}</td>
                    <td style={celda}>{x.n}</td>
                    <td style={{ ...celda, color: 'var(--t1)', fontWeight: 700 }}>{tasa(x.tasa)}</td>
                    <td style={celda}>{tasa(x.pide)}</td>
                    <td style={{ ...celda, color: colorDe(x.ventaja), fontWeight: 700 }}>{x.ventaja == null ? '—' : `${signo(100 * x.ventaja, 1)} pts`}</td>
                    <td style={celda}>{ic(x.intervalo)}</td>
                    <td style={{ ...celda, color: colorDe(x.roiPlano) }}>{pct(x.roiPlano)}</td>
                  </tr>
                )
              })}
            </tbody>
          ))}
        </table>
      </div>
      <div style={{ marginTop: 8, font: '600 11px var(--sans)', color: est.color, lineHeight: 1.45, overflowWrap: 'anywhere' }}>
        {c.texto}
      </div>
    </div>
  )
}

// EN QUIÉN DESCONFIAR (10/11/2026, usuario): la alerta no cambia el elegido;
// esto mide, hacia adelante, si con alerta acertamos menos que sin ella
function TablaAlerta({ r, isMobile }: { r: ResumenAlerta; isMobile: boolean }) {
  const tasa = (x: number | null | undefined) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  const filas: [string, GrupoAlerta][] = [['con alerta', r.conAlerta], ['sin alerta', r.sinAlerta]]
  const total = r.conAlerta.n + r.sinAlerta.n
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>En quién desconfiar · alerta de confianza</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        Alerta si le damos al elegido {num(r.sobreCasa, 0)}+ puntos más que la casa, o si su racha es de un solo partido con
        riesgo alto. No cambia el elegido: se registra desde el {fecha(r.desde).split(' ')[0]} y se mide hacia adelante.
      </div>
      {total === 0 ? (
        <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)' }}>Todavía no hay partidos cerrados con la alerta registrada.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
            <thead>
              <tr style={{ color: 'var(--t3)' }}>
                <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}></th>
                <th style={{ ...celda, fontWeight: 600 }}>casos</th>
                <th style={{ ...celda, fontWeight: 600 }}>acierta</th>
                <th style={{ ...celda, fontWeight: 600 }}>pedía</th>
                <th style={{ ...celda, fontWeight: 600 }}>1 u plano</th>
                <th style={{ ...celda, fontWeight: 600 }}>elegido o empate</th>
              </tr>
            </thead>
            <tbody>
              {filas.map(([nombre, g]) => (
                <tr key={nombre} style={{ borderTop: '1px solid var(--line)' }}>
                  <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700 }}>{nombre}</td>
                  <td style={celda}>{g.n}</td>
                  <td style={{ ...celda, color: 'var(--t1)', fontWeight: 700 }}>{tasa(g.tasa)}</td>
                  <td style={celda}>{tasa(g.pide)}</td>
                  <td style={{ ...celda, color: colorDe(g.roiPlano) }}>{pct(g.roiPlano)}</td>
                  <td style={celda}>{g.dobleOportunidad ? `${tasa(g.dobleOportunidad.tasa)} (pedía ${tasa(g.dobleOportunidad.pide)})` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {r.descarte && (
        <div style={{ marginTop: 8, font: '500 11px var(--sans)', color: 'var(--t2)', lineHeight: 1.45 }}>
          <b style={{ color: 'var(--t1)' }}>El descarte</b> (lo que menos probable le dimos): salió {tasa(r.descarte.tasa)} de {r.descarte.n} partidos;
          la casa le daba {tasa(r.descarte.casaLeDaba)}.
        </div>
      )}
    </div>
  )
}

function PorVersion({ d, visibles, isMobile }: { d: SimulacionApuesta; visibles: EstrategiaClave[]; isMobile: boolean }) {
  return (
    <div style={{ ...tarjeta }}>
      <div style={{ ...rotulo, marginBottom: 8 }}>Por versión de sad-analysis (la del 1X2)</div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)', textAlign: 'right' }}>
              <th style={{ textAlign: 'left', padding: '4px 6px', fontWeight: 600 }}>versión</th>
              <th style={{ padding: '4px 6px', fontWeight: 600 }}>partidos</th>
              <th style={{ padding: '4px 6px', fontWeight: 600 }}>aciertos</th>
              {visibles.map((c) => <th key={c} style={{ padding: '4px 6px', fontWeight: 600 }}>{CORTO[c]}</th>)}
            </tr>
          </thead>
          <tbody>
            {d.porVersion.map((v) => (
              <tr key={v.version} style={{ borderTop: '1px solid var(--line)', textAlign: 'right' }}>
                <td style={{ textAlign: 'left', padding: '5px 6px', color: 'var(--t1)', fontWeight: 700 }}>{v.version}</td>
                <td style={{ padding: '5px 6px' }}>{v.partidos}</td>
                <td style={{ padding: '5px 6px' }}>{v.aciertos}</td>
                {visibles.map((c) => {
                  const e = v.estrategias[c]
                  return (
                    <td key={c} style={{ padding: '5px 6px' }}>
                      {e && e.apuestas ? (
                        <><b style={{ color: colorDe(e.ganancia) }}>{signo(e.ganancia)}</b> <span style={{ color: 'var(--t3)' }}>({pct(e.roi, 0)})</span></>
                      ) : <span style={{ color: 'var(--t3)' }}>sin apuestas</span>}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function FilaApuesta({ a, visibles }: { a: ApuestaSimulada; visibles: { clave: EstrategiaClave; color: string }[] }) {
  const cerrada = a.estado === 'cerrada'
  const acierto = cerrada && a.resultado === a.elegido
  return (
    <div style={{ ...tarjeta, padding: '11px 13px' }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>{fecha(a.pitazo)}</span>
        <span style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)' }}>{a.partido.local} – {a.partido.visita}</span>
        {a.partido.liga && <span style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>{a.partido.liga}</span>}
        {a.alerta?.activa && (
          <span title={a.alerta.motivos.map((m) => m.detalle).join(' · ')}
            style={{ padding: '1px 6px', borderRadius: 5, font: '700 9.5px var(--sans)', background: 'var(--down-soft)', color: 'var(--down)' }}>
            ⚠ desconfiar
          </span>
        )}
        <span style={{
          marginLeft: 'auto', padding: '2px 8px', borderRadius: 6, font: '700 10px var(--sans)',
          background: !cerrada ? 'var(--bg3)' : acierto ? 'var(--up-soft)' : 'var(--down-soft)',
          color: !cerrada ? 'var(--t2)' : acierto ? 'var(--up)' : 'var(--down)',
        }}>
          {!cerrada ? 'por jugarse' : `${acierto ? '✓' : '✗'} salió ${RES[a.resultado!]}`}
        </span>
      </div>

      {/* LA VERSIÓN DE CADA SKILL con la que se escribió el parte */}
      <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginTop: 6 }} title={`parte depositado ${fecha(a.depositadoEn)} · prompt ${a.versionPrompt}`}>
        {SKILL_CORTO.map(([s, c]) => a.versiones[s] ? (
          <span key={s} style={{ padding: '1px 6px', borderRadius: 5, border: '1px solid var(--line)', font: '600 9.5px var(--mono)', color: s === 'sad-analysis' ? 'var(--t1)' : 'var(--t2)' }}>
            {c} {a.versiones[s]}
          </span>
        ) : null)}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 6, marginTop: 8 }}>
        {(['local', 'empate', 'visita'] as Resultado1x2[]).map((k) => {
          const elegido = a.elegido === k
          const salio = a.resultado === k
          return (
            <div key={k} style={{ padding: '5px 7px', borderRadius: 8, background: salio ? 'var(--bg3)' : 'transparent', border: `1px solid ${elegido ? 'var(--accent)' : 'var(--line)'}`, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap', font: '600 9.5px var(--sans)', color: 'var(--t3)' }}>
                {RES[k]}{elegido ? ' · elegido' : ''}{elegido && <SemaforoChip s={a.semaforo} corta />}
              </div>
              <div style={{ font: '700 12px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
                {num(a.probabilidades[k], 0)} % <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>@ {num(a.cuotas[k])}</span>
              </div>
              <div style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>mercado {num(a.mercado[k], 0)} %</div>
            </div>
          )
        })}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 3, marginTop: 8 }}>
        {visibles.map((v) => {
          const r = a.porEstrategia[v.clave]
          if (!r) return null
          return (
            <div key={v.clave} style={{ display: 'grid', gridTemplateColumns: '10px 76px minmax(0,1fr)', alignItems: 'baseline', columnGap: 7, font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
              <span style={{ width: 10, height: 2, background: v.color, alignSelf: 'center' }} />
              <span style={{ color: 'var(--t2)', fontFamily: 'var(--sans)', fontWeight: 600 }}>{CORTO[v.clave]}</span>
              {r.seleccion ? (
                <span style={{ minWidth: 0 }}>
                  {num(r.monto)} u a {RES[r.seleccion]}{r.linea ? <span style={{ color: 'var(--t3)' }}> (línea {r.linea})</span> : null}
                  {r.ganancia != null && <> · <b style={{ color: colorDe(r.ganancia) }}>{signo(r.ganancia)}</b></>}
                  {r.banca != null && <span style={{ color: 'var(--t3)' }}> · banca {num(r.banca)}</span>}
                </span>
              ) : (
                <span style={{ color: 'var(--t3)', minWidth: 0 }}>
                  {r.motivo === 'sin plata libre'
                    ? 'no apuesta: toda la banca está en juego en otros partidos'
                    : v.clave === 'proporcional' || v.clave === 'metodoVerde' ? `no apuesta: ${r.motivo}`
                    : v.clave === 'plana60' || v.clave === 'martingala60' ? `no apuesta: el elegido tiene ${num(a.probabilidades[a.elegido], 0)} %, bajo el 60 %`
                    : v.clave.startsWith('kelly') ? `no apuesta: sin ventaja (mejor f* ${signo(100 * a.kelly.fraccion, 1)} % en ${RES[a.kelly.seleccion]})` : 'no apuesta: banca en cero'}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
