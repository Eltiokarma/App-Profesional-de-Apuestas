// Reventón de la burbuja (docs/REVENTON.md): la guía calculada de cuándo la K
// de resultado del equipo suele volver a cero, tal como llega del contrato
// (GET /equipos/{id}/burbujas). La pantalla no calcula nada: pinta los números
// y los motivos que vienen con ellos. No es una probabilidad y se dice.
import type { BurbujasEquipoDTO, DistribucionDTO, FamiliaBurbuja, FamiliaBurbujaDTO, HistorialPeriodoDTO, HistorialSignoDTO, ReventonDTO } from '../api/types'
import type { KCondKey } from '../data/types'
import { fmtK, signFmt } from '../lib/kview'

interface Props {
  data: BurbujasEquipoDTO | null
  loading?: boolean
  error?: string | null
  /** Familia que se muestra: sigue al toggle Total/Local/Visita de las K. */
  familia: KCondKey
  onFamilia?: (f: FamiliaBurbuja) => void
  compact?: boolean
}

const RIESGO_COLOR: Record<string, string> = {
  bajo: 'var(--up)', medio: 'var(--mark)', alto: 'var(--down)', 'muy alto': 'var(--down)', 'sin base': 'var(--t3)',
}
const GRADO_COLOR: Record<string, string> = {
  estable: 'var(--up)', 'en transición': 'var(--mark)', inestable: 'var(--down)', 'sin dato': 'var(--t3)',
}
const FAMILIA_LABEL: Record<FamiliaBurbuja, string> = { total: 'Total', local: 'Local', visita: 'Visita' }

const MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
const fmtFecha = (iso?: string | null): string => {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso.slice(0, 10)
  return `${d.getDate()} ${MES[d.getMonth()]} ${String(d.getFullYear()).slice(2)}`
}
const num = (v: number | null | undefined, dec = 1) => (v == null ? '—' : v.toFixed(dec))

const caja: React.CSSProperties = { flex: 1, minWidth: 0, padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }
const rotulo: React.CSSProperties = { font: '500 9px var(--mono)', color: 'var(--t3)', marginBottom: 2, letterSpacing: '.3px' }
const mono = (color = 'var(--t1)', size = 15): React.CSSProperties => ({ font: `700 ${size}px var(--mono)`, color, fontVariantNumeric: 'tabular-nums' })

function Chip({ texto, color, title }: { texto: string; color: string; title?: string }) {
  return (
    <span title={title} style={{ padding: '3px 8px', borderRadius: 6, background: `color-mix(in oklch, ${color}, transparent 84%)`, color, font: '700 9.5px var(--mono)', letterSpacing: '.3px', whiteSpace: 'nowrap' }}>
      {texto}
    </span>
  )
}

/** Tabla media · mediana · moda · mín–máx de las tres cosas que definen un reventón. */
function PorPeriodo({ periodos, signo, global, compact }: { periodos: HistorialPeriodoDTO[]; signo: '+' | '-'; global: HistorialSignoDTO | null; compact?: boolean }) {
  const de = (p: HistorialPeriodoDTO) => (signo === '+' ? p.positivo : p.negativo)
  // en la tarjeta van los períodos EN CURSO; las temporadas y años pasados se
  // eligen en la gráfica, donde se ven sobre la K
  const vigentes = periodos.filter((p) => p.vigente)
  const filas = compact ? vigentes.filter((p) => p.clave.startsWith('temporada') || p.clave === 'dt') : vigentes
  return (
    <div style={{ padding: '7px 10px 5px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>
        REVENTÓN TÍPICO {signo === '+' ? '+' : '−'} POR PERÍODO · <span style={{ color: 'var(--t3)' }}>la global manda en el riesgo; esto es referencia</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: compact ? 'minmax(0,1fr)' : 'minmax(0,1.6fr) repeat(4, minmax(0,1fr))', gap: compact ? 3 : '2px 8px', font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
        {!compact && (
          <>
            <span style={{ color: 'var(--t3)' }}>período</span>
            <span style={{ color: 'var(--t3)' }}>n</span>
            <span style={{ color: 'var(--t3)' }}>K pico med.</span>
            <span style={{ color: 'var(--t3)' }}>racha med.</span>
            <span style={{ color: 'var(--t3)' }}>rival med.</span>
          </>
        )}
        {global && (
          <Linea compact={compact} etiqueta="toda la historia" h={global} destacada />
        )}
        {filas.map((p) => {
          const h = de(p)
          if (p.sinDato) return <Linea key={p.clave} compact={compact} etiqueta={p.etiqueta} h={null} nota={p.sinDato} />
          return <Linea key={p.clave} compact={compact} etiqueta={`${p.etiqueta} · ${p.partidos} pj`} h={h} nota={h ? (h.n < 3 ? 'muestra corta' : '') : 'sin reventones de este signo'} />
        })}
      </div>
    </div>
  )
}

function Linea({ etiqueta, h, nota, destacada, compact }: { etiqueta: string; h: HistorialSignoDTO | null; nota?: string; destacada?: boolean; compact?: boolean }) {
  const color = destacada ? 'var(--t1)' : 'var(--t2)'
  if (compact) {
    return (
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', color }}>
        <span style={{ fontWeight: destacada ? 700 : 500 }}>{etiqueta}:</span>
        {h ? <span>n {h.n} · K {num(h.kPico.mediana, 1)} · {num(h.partidos.mediana, 1)} pj · rival {num(h.nivelRival.mediana, 2)}{nota ? ` · ${nota}` : ''}</span>
          : <span style={{ color: 'var(--t3)' }}>{nota}</span>}
      </div>
    )
  }
  return (
    <>
      <span style={{ color, fontWeight: destacada ? 700 : 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={etiqueta}>{etiqueta}</span>
      {h ? (
        <>
          <span style={{ color }}>{h.n}{nota ? <span style={{ color: 'var(--t3)' }}> · {nota}</span> : null}</span>
          <span style={{ color }}>{num(h.kPico.mediana, 1)}</span>
          <span style={{ color }}>{num(h.partidos.mediana, 1)}</span>
          <span style={{ color }}>{num(h.nivelRival.mediana, 2)}</span>
        </>
      ) : (
        <span style={{ gridColumn: 'span 4', color: 'var(--t3)' }}>{nota}</span>
      )}
    </>
  )
}

function TablaHistorial({ h, signo }: { h: NonNullable<FamiliaBurbujaDTO['historial']['positivo']>; signo: '+' | '-' }) {
  const filas: [string, (d: DistribucionDTO) => string][] = [
    ['Media', (d) => num(d.media, 2)],
    ['Mediana', (d) => num(d.mediana, 2)],
    ['Moda', (d) => (d.moda == null ? 'sin moda' : num(d.moda, 1))],
    ['Mín – máx', (d) => `${num(d.min, 1)} – ${num(d.max, 1)}`],
  ]
  const th: React.CSSProperties = { font: '600 8.5px var(--mono)', color: 'var(--t3)', textAlign: 'right', padding: '0 0 4px 0', letterSpacing: '.4px' }
  const td: React.CSSProperties = { font: '600 11px var(--mono)', color: 'var(--t1)', textAlign: 'right', padding: '4px 0', borderTop: '1px solid var(--line)', fontVariantNumeric: 'tabular-nums' }
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          <th style={{ ...th, textAlign: 'left' }}>{h.n} REVENTÓN{h.n === 1 ? '' : 'ES'} {signo === '+' ? '+' : '−'}</th>
          <th style={th}>K PICO</th>
          <th style={th}>PARTIDOS</th>
          <th style={th}>NIVEL RIVAL</th>
        </tr>
      </thead>
      <tbody>
        {filas.map(([l, f]) => (
          <tr key={l}>
            <td style={{ ...td, textAlign: 'left', color: 'var(--t2)', font: '600 10.5px var(--sans)' }}>{l}</td>
            <td style={td}>{f(h.kPico)}</td>
            <td style={td}>{f(h.partidos)}</td>
            <td style={td}>{f(h.nivelRival)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function FilaReventon({ r }: { r: ReventonDTO }) {
  const color = r.signo === '+' ? 'var(--up)' : 'var(--down)'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '5px 0', borderTop: '1px solid var(--line)', font: '500 10.5px var(--mono)', color: 'var(--t2)' }}>
      <span style={{ width: 8, height: 8, borderRadius: r.esInternacional ? 2 : '50%', background: color, transform: r.esInternacional ? 'rotate(45deg)' : 'none', flexShrink: 0 }} title={r.esInternacional ? 'torneo internacional' : 'liga'}></span>
      <span style={{ color: 'var(--t3)', width: 58, flexShrink: 0 }}>{fmtFecha(r.fecha)}</span>
      <span style={{ flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--t1)' }}>
        {r.condicion === 'L' ? 'vs' : 'en'} {r.rival} {r.resultado}
      </span>
      <span title="nivel del rival que la reventó" style={{ color: 'var(--t3)' }}>rival {num(r.nivelRival, 2)}</span>
      <span title="K pico antes de reventar" style={{ color, fontWeight: 700 }}>{r.signo === '+' ? '+' : '−'}{fmtK(r.kPico)}</span>
      <span title="partidos que duró" style={{ color: 'var(--t3)', width: 28, textAlign: 'right' }}>{r.partidos} pj</span>
    </div>
  )
}

export function ReventonBurbuja({ data, loading, error, familia, onFamilia, compact }: Props) {
  if (loading) return <div className="sad-sk" style={{ height: 200, borderRadius: 12 }}></div>
  if (error) return <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: '8px 0' }}>No se pudo calcular el reventón: {error}</div>
  if (!data) return null

  const fam = data.familias[familia]
  const actual = fam.actual
  const riesgo = fam.riesgo
  const signo = actual?.signo ?? '+'
  const base = signo === '+' ? fam.historial.positivo : fam.historial.negativo
  const manda = data.mandan.familias.includes(familia)
  const ultimos = fam.reventones.slice(-(compact ? 3 : 5)).reverse()
  const est = data.estabilidad
  const extremo = fam.extremo?.activo ? fam.extremo : null
  const cerca = !extremo && fam.extremo?.cerca ? fam.extremo : null

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {/* cabecera: riesgo de la familia elegida + las otras dos de un vistazo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 160 }}>
          <div style={{ font: '700 12px var(--sans)' }}>Reventón · guía</div>
          <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>cuándo esta K suele volver a cero · calculado de su historia · no es una probabilidad</div>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {(['total', 'local', 'visita'] as FamiliaBurbuja[]).map((f) => {
            const rf = data.familias[f].riesgo
            const sel = f === familia
            const mandaF = data.mandan.familias.includes(f)
            const color = rf ? RIESGO_COLOR[rf.nivel] : 'var(--t3)'
            return (
              <button
                key={f}
                onClick={onFamilia ? () => onFamilia(f) : undefined}
                title={`${FAMILIA_LABEL[f]}: ${rf ? 'riesgo ' + rf.nivel : 'sin burbuja abierta'}${mandaF ? ' · esta constante manda por el nivel del equipo' : ''}`}
                style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, padding: '5px 9px', borderRadius: 8, cursor: onFamilia ? 'pointer' : 'default', background: sel ? 'var(--bg3)' : 'transparent', border: `1px solid ${mandaF ? color : 'var(--line)'}`, color: sel ? 'var(--t1)' : 'var(--t2)' }}
              >
                <span style={{ font: '600 9.5px var(--sans)' }}>{mandaF ? '★ ' : ''}{FAMILIA_LABEL[f]}</span>
                <span style={{ font: '700 9px var(--mono)', color, textTransform: 'uppercase', letterSpacing: '.3px' }}>{rf ? rf.nivel : '—'}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* qué constante manda para este equipo */}
      <div style={{ font: '500 11px var(--sans)', color: manda ? 'var(--t1)' : 'var(--t2)', padding: '7px 10px', borderRadius: 8, background: 'var(--bg)', border: '1px solid var(--line)' }}>
        <span style={{ font: '700 9px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px', marginRight: 6 }}>MANDAN {data.mandan.tipo === 'globales' ? 'LAS GLOBALES' : 'LAS ESPECÍFICAS'}</span>
        {data.mandan.motivo}
        {!manda && <span style={{ color: 'var(--t3)' }}> · la familia que ves no es la que manda</span>}
      </div>

      {!actual && (
        <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t2)', padding: '8px 10px', borderRadius: 8, background: 'var(--bg)', border: '1px solid var(--line)' }}>
          Sin burbuja abierta: la K de esta familia está en 0
          {fam.reventones.length > 0 && (
            <> · la última reventó {fmtFecha(fam.reventones[fam.reventones.length - 1].fecha)} con K {signFmt((fam.reventones[fam.reventones.length - 1].signo === '+' ? 1 : -1) * fam.reventones[fam.reventones.length - 1].kPico)} tras {fam.reventones[fam.reventones.length - 1].partidos} partido{fam.reventones[fam.reventones.length - 1].partidos === 1 ? '' : 's'}</>
          )}
          {fam.partidosEnCondicion === 0 && ' · sin partidos de esta condición'}
        </div>
      )}

      {/* ALERTA DE EXTREMO: aparte del riesgo y ANTES que él. La K no puntúa
          (el backtest lo dice), pero una burbuja en su máximo histórico es
          terreno sin precedente y ahí no se carga la apuesta a que siga. */}
      {actual && extremo && (
        <div role="alert" style={{ padding: '10px 12px', borderRadius: 9, background: 'color-mix(in oklch, var(--down), transparent 82%)', border: '2px solid var(--down)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
            <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--down)', color: 'var(--bg)', font: '800 10px var(--mono)', letterSpacing: '.6px' }}>⚠ EXTREMO</span>
            <span style={{ font: '800 12px var(--sans)', color: 'var(--down)', textTransform: 'uppercase', letterSpacing: '.3px' }}>
              {extremo.kRecord ? `K ${actual.k > 0 ? '+' : ''}${actual.k.toFixed(1)}: la más ${signo === '+' ? 'alta' : 'baja'} en ${extremo.partidosHistoria} partidos` : `racha récord en ${extremo.partidosHistoria} partidos`}
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: 16, font: '600 11px var(--sans)', color: 'var(--t1)', lineHeight: 1.45 }}>
            {extremo.motivos.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
          <div style={{ font: '600 11px var(--sans)', color: 'var(--down)', marginTop: 5, lineHeight: 1.4 }}>
            No cargar la apuesta a que la racha siga. El riesgo de abajo no lo cuenta: la tasa de reventón no sube con la K, pero si revienta, revienta desde lo más alto.
          </div>
        </div>
      )}

      {/* CERCA DEL EXTREMO: el escalón de abajo, en ámbar. Sin récord, pero
          la K o la racha ya pasaron al 90 % de sus reventones: un «riesgo
          bajo» a secas se leía como luz verde (ADT −17.9 con récord −19.5). */}
      {actual && cerca && (
        <div role="alert" style={{ padding: '10px 12px', borderRadius: 9, background: 'color-mix(in oklch, var(--mark), transparent 82%)', border: '2px solid var(--mark)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
            <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--mark)', color: 'var(--bg)', font: '800 10px var(--mono)', letterSpacing: '.6px' }}>⚠ CERCA DEL EXTREMO</span>
            <span style={{ font: '800 12px var(--sans)', color: 'var(--mark)', textTransform: 'uppercase', letterSpacing: '.3px' }}>
              K {actual.k > 0 ? '+' : ''}{actual.k.toFixed(1)} · récord {signo === '+' ? '+' : '-'}{cerca.maximoPrevio.kPico.toFixed(1)}
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: 16, font: '600 11px var(--sans)', color: 'var(--t1)', lineHeight: 1.45 }}>
            {cerca.motivos.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
          <div style={{ font: '600 11px var(--sans)', color: 'var(--mark)', marginTop: 5, lineHeight: 1.4 }}>
            No cargar fuerte a que la racha siga. El riesgo de abajo no lo cuenta: la K no puntúa, pero la burbuja ya está en la franja más alta de su historia.
          </div>
        </div>
      )}

      {actual && riesgo && (
        <>
          {/* la burbuja de hoy contra el reventón típico y el rival que viene */}
          <div style={{ display: 'flex', gap: 8, flexWrap: compact ? 'wrap' : 'nowrap' }}>
            <div style={caja}>
              <div style={rotulo}>BURBUJA ABIERTA</div>
              <div style={mono(signo === '+' ? 'var(--up)' : 'var(--down)')}>{signFmt(actual.k)}</div>
              <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>
                {actual.partidos} partido{actual.partidos === 1 ? '' : 's'}{familia === 'total' ? '' : ` de ${familia}`} desde {fmtFecha(actual.desde)}
                {fam.posicion && <> · percentil K {fam.posicion.percentilK} · racha {fam.posicion.percentilRacha}</>}
              </div>
            </div>
            <div style={caja}>
              <div style={rotulo}>REVENTÓN TÍPICO {signo === '+' ? '+' : '−'}</div>
              {base ? (
                <>
                  <div style={mono()}>K {num(base.kPico.mediana, 1)} <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>mediana</span></div>
                  <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>
                    a los {num(base.partidos.mediana, 1)} partidos · rival {num(base.nivelRival.mediana, 2)}
                    {fam.posicion?.kSobreMediana != null && <> · hoy ×{num(fam.posicion.kSobreMediana, 2)}</>}
                  </div>
                </>
              ) : (
                <div style={{ font: '600 11px var(--sans)', color: 'var(--t3)' }}>sin reventones previos de este signo</div>
              )}
            </div>
            <div style={caja}>
              <div style={rotulo}>PRÓXIMO RIVAL</div>
              {fam.rival ? (
                <>
                  <div style={mono(fam.rival.tramo === 'lejos' ? 'var(--up)' : fam.rival.tramo === 'zona' ? 'var(--mark)' : 'var(--down)')}>
                    {{ lejos: 'LEJOS DE LA ZONA', zona: 'EN ZONA', fuerte: signo === '+' ? 'MÁS FUERTE' : 'MÁS FLOJO', 'muy fuerte': signo === '+' ? 'MUCHO MÁS FUERTE' : 'MUCHO MÁS FLOJO' }[fam.rival.tramo]}
                  </div>
                  <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>
                    {data.proximo?.rival} · nivel {num(fam.rival.nivelProximo, 2)} vs mediana {num(fam.rival.medianaReventon, 2)} ({fam.rival.distancia > 0 ? '+' : ''}{num(fam.rival.distancia, 2)})
                  </div>
                </>
              ) : (
                <div style={{ font: '600 11px var(--sans)', color: 'var(--t3)' }}>
                  {!data.proximo ? 'sin próximo partido' : actual.aplicaAlProximo === false ? `no se mueve: el próximo es de ${data.proximo.condicion === 'L' ? 'local' : 'visita'}` : 'sin base para comparar'}
                </div>
              )}
            </div>
          </div>

          {/* el veredicto con sus motivos, uno por punto */}
          <div style={{ padding: '9px 11px', borderRadius: 9, background: `color-mix(in oklch, ${RIESGO_COLOR[riesgo.nivel]}, transparent 90%)`, border: `1px solid color-mix(in oklch, ${RIESGO_COLOR[riesgo.nivel]}, transparent 60%)` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 5 }}>
              <span style={{ font: '800 12px var(--sans)', color: RIESGO_COLOR[riesgo.nivel], textTransform: 'uppercase', letterSpacing: '.3px' }}>Riesgo de reventón {riesgo.nivel}</span>
              <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>{riesgo.puntos} pts</span>
              <Chip texto={`confianza ${riesgo.confianza}`} color={riesgo.confianza === 'alta' ? 'var(--up)' : riesgo.confianza === 'media' ? 'var(--mark)' : 'var(--t3)'} title={riesgo.confianzaMotivos.join(' · ')} />
            </div>
            <ul style={{ margin: 0, paddingLeft: 16, font: '500 11px var(--sans)', color: 'var(--t1)', lineHeight: 1.45 }}>
              {riesgo.motivos.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
            <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginTop: 5 }}>confianza: {riesgo.confianzaMotivos.join(' · ')}</div>
          </div>

          {base && !compact && (
            <div style={{ padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
              <TablaHistorial h={base} signo={signo} />
            </div>
          )}
        </>
      )}

      {/* LA MISMA REFERENCIA, ACOTADA EN EL TIEMPO. El Universitario de hoy no es
          el de Fossati, ni el City de ahora el del primer Guardiola: la global
          (toda la historia) sigue mandando en el riesgo porque es la calibrada
          con el backtest, pero al lado van las mismas medidas de esta temporada,
          este año, con el DT actual y los últimos 20. Con n chico dicen n y no
          dicen más. */}
      {fam.historialPorPeriodo && fam.historialPorPeriodo.length > 0 && (
        <PorPeriodo periodos={fam.historialPorPeriodo} signo={signo} global={base} compact={compact} />
      )}

      {/* estabilidad: sube o baja la confianza, nunca el riesgo */}
      <div style={{ padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={rotulo}>ESTABILIDAD</span>
          <Chip texto={est.grado} color={GRADO_COLOR[est.grado]} />
          {est.dt && <span style={{ font: '500 10px var(--mono)', color: 'var(--t2)' }}>DT {est.dt.nombre}{est.dt.dias != null ? ` · ${est.dt.dias} d` : ''}</span>}
          {est.movimientos && <span style={{ font: '500 10px var(--mono)', color: 'var(--t2)' }}>ventana +{est.movimientos.llegadas} / −{est.movimientos.salidas}</span>}
          {est.bajas != null && <span style={{ font: '500 10px var(--mono)', color: 'var(--t2)' }}>{est.bajas} baja{est.bajas === 1 ? '' : 's'}</span>}
        </div>
        <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t2)', marginTop: 4, lineHeight: 1.4 }}>{est.motivos.join(' · ')}</div>
        <div style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', marginTop: 3 }}>sin dato (no se rellena): {est.sinDato.join(' · ')}</div>
      </div>

      {ultimos.length > 0 && (
        <div style={{ padding: '6px 10px 2px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
          <div style={{ ...rotulo, marginBottom: 4 }}>ÚLTIMOS REVENTONES · {FAMILIA_LABEL[familia].toUpperCase()}</div>
          {ultimos.map((r) => <FilaReventon key={r.fixtureId + r.signo} r={r} />)}
        </div>
      )}

      <div style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', lineHeight: 1.4 }}>{data.aviso}</div>
    </div>
  )
}
