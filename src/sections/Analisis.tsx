import { useMemo, useState } from 'react'
import type { AnalisisRegistroDTO, EfeBloque, EfeComparativo, EfeEquipo } from '../api/types'
import { CONFIG } from '../config'
import type { Match } from '../data/types'
import { generarAnalisisEfe, loadAnalisisPartido } from '../services/appdata'
import { useAsync } from '../services/useAsync'

interface Props {
  m: Match
  isMobile: boolean
}

// colores por estado de indicador / clasificación
const IND_COLOR = { verde: 'var(--up)', ambar: 'var(--mark)', rojo: 'var(--down)' } as const
const CLASIF = {
  FORMADO: { label: 'FORMADO', color: 'var(--up)', soft: 'var(--up-soft)' },
  EN_FORMACION: { label: 'EN FORMACIÓN', color: 'var(--mark)', soft: 'var(--mark-soft)' },
  SIN_FORMACION: { label: 'SIN FORMACIÓN', color: 'var(--down)', soft: 'var(--down-soft)' },
} as const
const ROL = { TF: 'Titular fijo', TH: 'Titular habitual', ROT: 'Rotación', SUP: 'Suplente' } as const
const BLOQUE_NOMBRE = { A: 'Cuerpo técnico', B: 'Plantel', C: 'K Constants', D: 'Coherencia táctica', E: 'Rendimiento' } as const

/** Anillo (gauge) con el % del EFE y su clasificación. */
function GaugeRing({ eq, nombre }: { eq: EfeEquipo; nombre: string }) {
  const cl = CLASIF[eq.clasificacion]
  const R = 52
  const C = 2 * Math.PI * R
  const frac = Math.max(0, Math.min(1, eq.porcentaje / 100))
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
      <svg width="132" height="132" viewBox="0 0 132 132">
        <circle cx="66" cy="66" r={R} fill="none" stroke="var(--bg3)" strokeWidth="11" />
        <circle
          cx="66" cy="66" r={R} fill="none" stroke={cl.color} strokeWidth="11" strokeLinecap="round"
          strokeDasharray={`${(frac * C).toFixed(1)} ${C.toFixed(1)}`} transform="rotate(-90 66 66)"
        />
        <text x="66" y="62" textAnchor="middle" style={{ font: '800 26px var(--mono)', fill: 'var(--t1)' }}>{Math.round(eq.porcentaje)}%</text>
        <text x="66" y="80" textAnchor="middle" style={{ font: '600 9px var(--mono)', fill: 'var(--t3)' }}>{eq.total.toFixed(1)} / {eq.maximo_alcanzable}</text>
      </svg>
      <div style={{ font: '700 13px var(--sans)', color: 'var(--t1)', textAlign: 'center', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{nombre}</div>
      <span style={{ padding: '3px 10px', borderRadius: 7, background: cl.soft, color: cl.color, font: '700 10px var(--mono)', letterSpacing: '.4px' }}>{cl.label}</span>
      <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', textAlign: 'center' }}>
        DT {eq.dt.nombre}{eq.dt.meses != null ? ` · ${Math.round(eq.dt.meses)} meses` : ''}
      </div>
    </div>
  )
}

/** Fila de un bloque A-E con barra y detalle expandible de indicadores. */
function BloqueRow({ letra, b }: { letra: 'A' | 'B' | 'C' | 'D' | 'E'; b: EfeBloque }) {
  const [abierto, setAbierto] = useState(false)
  const usado = b.ponderado ?? b.score
  const tope = letra === 'B' ? 9 : letra === 'E' ? 6 : b.max
  const frac = b.excluido ? 0 : Math.max(0, Math.min(1, tope ? usado / tope : 0))
  return (
    <div style={{ borderBottom: '1px solid var(--line)' }}>
      <button onClick={() => setAbierto(!abierto)} style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '9px 2px', background: 'transparent', border: 0, cursor: 'pointer', textAlign: 'left' }}>
        <span style={{ width: 20, height: 20, borderRadius: 6, background: 'var(--bg3)', color: 'var(--t2)', font: '700 11px var(--mono)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{letra}</span>
        <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', width: 110, flexShrink: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{BLOQUE_NOMBRE[letra]}</span>
        {b.excluido ? (
          <span style={{ flex: 1, font: '600 10px var(--mono)', color: 'var(--t3)' }}>N/A · {b.motivo_exclusion ?? 'excluido'}</span>
        ) : (
          <span style={{ flex: 1, height: 7, borderRadius: 4, background: 'var(--bg3)', overflow: 'hidden' }}>
            <span style={{ display: 'block', width: `${frac * 100}%`, height: '100%', borderRadius: 4, background: frac >= 0.7 ? 'var(--up)' : frac >= 0.4 ? 'var(--mark)' : 'var(--down)' }}></span>
          </span>
        )}
        <span style={{ font: '700 11.5px var(--mono)', color: 'var(--t1)', width: 58, textAlign: 'right', fontVariantNumeric: 'tabular-nums', flexShrink: 0 }}>
          {b.excluido ? '—' : `${usado.toFixed(1)}/${tope}`}
        </span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2.4" strokeLinecap="round" style={{ transform: abierto ? 'rotate(90deg)' : 'none', transition: 'transform .12s', flexShrink: 0 }}><path d="M9 6l6 6-6 6" /></svg>
      </button>
      {abierto && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 7, padding: '2px 2px 11px 30px' }}>
          {b.ppp != null && <div style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>PPP actual: {b.ppp.toFixed(2)}</div>}
          {b.d3_cap_aplicado && <div style={{ font: '600 10px var(--mono)', color: 'var(--down)' }}>D3 ❌ — tope del bloque reducido a 2.5/4 (indicador de colapso)</div>}
          {b.indicadores.map((ind) => (
            <div key={ind.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: IND_COLOR[ind.estado], marginTop: 3, flexShrink: 0 }}></span>
              <div style={{ minWidth: 0 }}>
                <span style={{ font: '700 10.5px var(--mono)', color: 'var(--t2)', marginRight: 6 }}>{ind.id}</span>
                <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{ind.justificacion}</span>
                {ind.fuente && ind.fuente !== 'demo' && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', marginLeft: 6 }}>({ind.fuente})</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/** Panel de disponibilidad (Bloque F) de un equipo. */
function Disponibilidad({ eq }: { eq: EfeEquipo }) {
  const d = eq.disponibilidad
  const nivel = IND_COLOR[d.ip_nivel]
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <span style={{ padding: '5px 11px', borderRadius: 8, background: 'var(--bg3)', font: '700 12px var(--mono)', color: nivel }}>
          IP {d.ip.toFixed(1)}
        </span>
        {d.multiplicador_gk_aplicado && (
          <span style={{ padding: '4px 9px', borderRadius: 7, background: 'var(--down-soft)', color: 'var(--down)', font: '700 10px var(--mono)' }}>🧤 GK ×1.5</span>
        )}
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>F4: {d.f4.rotados} rotados · {d.f4.diagnostico}</span>
      </div>

      {/* reducción por zona */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {(['GK', 'DEF', 'MID', 'ATK'] as const).map((z) => {
          const red = d.reduccion_zonas[z]
          const col = red > 40 ? 'var(--down)' : red >= 20 ? 'var(--mark)' : 'var(--up)'
          return (
            <div key={z} style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
              <span style={{ font: '700 10px var(--mono)', color: 'var(--t3)', width: 30 }}>{z}</span>
              <span style={{ flex: 1, height: 7, borderRadius: 4, background: 'var(--bg3)', overflow: 'hidden' }}>
                <span style={{ display: 'block', width: `${Math.min(100, red)}%`, height: '100%', borderRadius: 4, background: col }}></span>
              </span>
              <span style={{ font: '600 10.5px var(--mono)', color: col, width: 40, textAlign: 'right' }}>−{Math.round(red)}%</span>
            </div>
          )
        })}
      </div>

      {/* plantilla clave */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        {d.jugadores.map((j, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '5px 8px', borderRadius: 8, background: 'var(--bg)', opacity: j.estado === 'baja' ? 0.75 : 1 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', flexShrink: 0, background: j.estado === 'disponible' ? 'var(--up)' : j.estado === 'duda' ? 'var(--mark)' : 'var(--down)' }}></span>
            <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{j.nombre}</span>
            <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>{j.zona}</span>
            <span title={ROL[j.rol]} style={{ padding: '2px 6px', borderRadius: 5, background: 'var(--bg3)', font: '700 9px var(--mono)', color: j.rol === 'TF' ? 'var(--down)' : j.rol === 'TH' ? 'var(--mark)' : 'var(--t3)', flexShrink: 0 }}>{j.rol}</span>
            {j.apps && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>{j.apps}</span>}
            {j.motivo && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t2)', flexShrink: 0, maxWidth: 110, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={j.motivo}>{j.motivo}</span>}
          </div>
        ))}
      </div>

      {d.f5_factor_x.length > 0 && (
        <div style={{ padding: '9px 11px', borderRadius: 9, background: 'var(--accent-soft)', border: '1px solid color-mix(in oklch,var(--accent),transparent 55%)' }}>
          <div style={{ font: '700 10px var(--mono)', color: 'var(--accent)', marginBottom: 4 }}>🔮 FACTOR X (F5)</div>
          {d.f5_factor_x.map((f, i) => (
            <div key={i} style={{ font: '500 11px var(--sans)', color: 'var(--t1)' }}>
              <b>{f.nombre}</b> · {f.contexto}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function Analisis({ m, isMobile }: Props) {
  const esDemo = CONFIG.dataSource === 'mock'
  const registros = useAsync(() => loadAnalisisPartido(m.id), m.id)
  const [generando, setGenerando] = useState(false)
  const [errorGen, setErrorGen] = useState<string | null>(null)
  const [tab, setTab] = useState<'bloques' | 'disponibilidad' | 'matchup' | 'lectura' | 'calendario'>('bloques')

  // el confirmado (XI oficial) manda sobre el preliminar
  const efe: AnalisisRegistroDTO | null = useMemo(() => {
    const efes = (registros.data ?? []).filter((r) => r.tipo === 'efe')
    return efes.find((r) => r.estado === 'confirmado') ?? efes[efes.length - 1] ?? null
  }, [registros.data])
  const r: EfeComparativo | null = efe?.resultado ?? null

  const generar = () => {
    setGenerando(true)
    setErrorGen(null)
    generarAnalisisEfe(m.id)
      .then(() => registros.reload())
      .catch((e: unknown) => setErrorGen(e instanceof Error ? e.message : 'error del análisis'))
      .finally(() => setGenerando(false))
  }

  const tabs: { k: typeof tab; label: string }[] = [
    { k: 'bloques', label: 'Bloques EFE' },
    { k: 'disponibilidad', label: 'Disponibilidad' },
    { k: 'matchup', label: 'Matchup' },
    { k: 'lectura', label: 'Lectura SAD' },
    { k: 'calendario', label: 'Calendario' },
  ]
  const dosCol = isMobile ? '1fr' : '1fr 1fr'

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, marginBottom: 18, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Análisis EFE</h1>
          <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>
            Estado de Formación de Equipo · comparativa estructural pre-partido
          </p>
        </div>
        {efe && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ padding: '5px 11px', borderRadius: 8, font: '700 10px var(--mono)', letterSpacing: '.4px', background: efe.estado === 'confirmado' ? 'var(--up-soft)' : 'var(--mark-soft)', color: efe.estado === 'confirmado' ? 'var(--up)' : 'var(--mark)' }}>
              {efe.estado === 'confirmado' ? 'XI OFICIAL' : 'XI PROVISIONAL'}
            </span>
            <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>
              EFE v{efe.versionEfe} · {new Date(efe.creadoEn).toLocaleString()}
            </span>
          </div>
        )}
      </div>

      {registros.loading && <div className="sad-sk" style={{ height: 320 }}></div>}
      {registros.error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudieron cargar los análisis: {registros.error}</span>
          <button onClick={registros.reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)' }}>Reintentar</button>
        </div>
      )}

      {/* estado vacío honesto: nada inventado — el análisis se genera bajo demanda */}
      {!registros.loading && !registros.error && !efe && (
        <section style={{ padding: '34px 22px', borderRadius: 16, background: 'var(--bg2)', border: '1px dashed var(--line)', textAlign: 'center' }}>
          <h3 style={{ margin: 0, font: '700 15px var(--sans)', color: 'var(--t1)' }}>Este partido aún no tiene análisis EFE</h3>
          <p style={{ margin: '8px auto 16px', maxWidth: 480, font: '500 12px var(--sans)', color: 'var(--t3)' }}>
            El clasificador investiga a ambos equipos (DT, plantel, K, táctica, disponibilidad)
            y emite el dashboard comparativo con alertas.
            {esDemo ? ' Modo demo: análisis de muestra, sin costo.' : ' Tarda 1-3 minutos y consume créditos de la API (~$0.10-0.20).'}
          </p>
          {errorGen && (
            <p style={{ margin: '0 auto 12px', maxWidth: 480, font: '600 11.5px var(--sans)', color: 'var(--down)' }}>{errorGen}</p>
          )}
          <button onClick={generar} disabled={generando} style={{ padding: '11px 22px', borderRadius: 10, border: 0, cursor: generando ? 'wait' : 'pointer', background: generando ? 'var(--bg3)' : 'var(--accent)', color: generando ? 'var(--t2)' : '#fff', font: '700 13px var(--sans)' }}>
            {generando ? 'Analizando… (1-3 min)' : 'Generar análisis EFE'}
          </button>
        </section>
      )}

      {r && (
        <>
          {/* panel central: anillos comparativos */}
          <section style={{ display: 'flex', gap: 12, padding: '20px 16px', marginBottom: 14, borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <GaugeRing eq={r.equipos.a} nombre={r.partido.equipo_a} />
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 6, flexShrink: 0 }}>
              <span style={{ font: '800 13px var(--mono)', color: 'var(--t3)' }}>VS</span>
              {r.partido.torneo && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', textAlign: 'center', maxWidth: 90 }}>{r.partido.torneo}</span>}
            </div>
            <GaugeRing eq={r.equipos.b} nombre={r.partido.equipo_b} />
          </section>

          {/* alertas siempre visibles: son lo que modifica la confianza */}
          {r.alertas.length > 0 && (
            <section style={{ display: 'flex', flexDirection: 'column', gap: 7, marginBottom: 14 }}>
              {r.alertas.map((a, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '9px 13px', borderRadius: 11, background: a.tipo === 'estructural' ? 'var(--down-soft)' : 'var(--mark-soft)', border: `1px solid color-mix(in oklch,${a.tipo === 'estructural' ? 'var(--down)' : 'var(--mark)'},transparent 60%)` }}>
                  <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--bg)', font: '700 9.5px var(--mono)', color: a.tipo === 'estructural' ? 'var(--down)' : 'var(--mark)', flexShrink: 0, whiteSpace: 'nowrap' }}>{a.codigo}</span>
                  <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
                    {a.equipo && <b style={{ color: 'var(--t2)' }}>[{a.equipo === 'a' ? r.partido.equipo_a : a.equipo === 'b' ? r.partido.equipo_b : a.equipo}] </b>}
                    {a.detalle}
                  </span>
                </div>
              ))}
            </section>
          )}

          {/* pestañas */}
          <div className="sad-scroll" style={{ display: 'flex', gap: 6, marginBottom: 14, overflowX: 'auto', paddingBottom: 2 }}>
            {tabs.map((t) => (
              <button key={t.k} onClick={() => setTab(t.k)} style={{ flexShrink: 0, padding: '8px 15px', border: `1px solid ${tab === t.k ? 'color-mix(in oklch,var(--accent),transparent 55%)' : 'var(--line)'}`, borderRadius: 9, cursor: 'pointer', background: tab === t.k ? 'var(--accent-soft)' : 'transparent', color: tab === t.k ? 'var(--accent)' : 'var(--t2)', font: '600 12px var(--sans)', whiteSpace: 'nowrap' }}>{t.label}</button>
            ))}
          </div>

          {tab === 'bloques' && (
            <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
              {(['a', 'b'] as const).map((lado) => (
                <section key={lado} style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                  <div style={{ font: '700 12.5px var(--sans)', marginBottom: 6 }}>{lado === 'a' ? r.partido.equipo_a : r.partido.equipo_b}</div>
                  {(['A', 'B', 'C', 'D', 'E'] as const).map((letra) => (
                    <BloqueRow key={letra} letra={letra} b={r.equipos[lado].bloques[letra]} />
                  ))}
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 2px 2px', font: '700 12px var(--mono)', color: 'var(--t1)' }}>
                    <span style={{ color: 'var(--t3)' }}>TOTAL</span>
                    <span>{r.equipos[lado].total.toFixed(2)} / {r.equipos[lado].maximo_alcanzable} · {Math.round(r.equipos[lado].porcentaje)}%</span>
                  </div>
                </section>
              ))}
            </div>
          )}

          {tab === 'disponibilidad' && (
            <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
              {(['a', 'b'] as const).map((lado) => (
                <section key={lado} style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                  <div style={{ font: '700 12.5px var(--sans)', marginBottom: 10 }}>{lado === 'a' ? r.partido.equipo_a : r.partido.equipo_b}</div>
                  <Disponibilidad eq={r.equipos[lado]} />
                </section>
              ))}
            </div>
          )}

          {tab === 'matchup' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <section style={{ padding: '13px 16px', borderRadius: 14, textAlign: 'center', background: r.matchup_h.diagnostico === 'FAVORABLE' ? 'var(--up-soft)' : r.matchup_h.diagnostico === 'DESFAVORABLE' ? 'var(--down-soft)' : 'var(--bg2)', border: '1px solid var(--line)' }}>
                <div style={{ font: '800 14px var(--mono)', color: r.matchup_h.diagnostico === 'FAVORABLE' ? 'var(--up)' : r.matchup_h.diagnostico === 'DESFAVORABLE' ? 'var(--down)' : 'var(--t1)', letterSpacing: '.5px' }}>
                  MATCHUP {r.matchup_h.diagnostico}
                </div>
                <div style={{ font: '500 12px var(--sans)', color: 'var(--t1)', marginTop: 5 }}>{r.matchup_h.razon}</div>
                <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 9, flexWrap: 'wrap' }}>
                  {(['h2a', 'h2b', 'h2c'] as const).map((h) => {
                    const v = r.matchup_h[h]
                    const col = v === 'verde' ? 'var(--up)' : v === 'rojo' ? 'var(--down)' : 'var(--mark)'
                    return v ? <span key={h} style={{ padding: '3px 9px', borderRadius: 6, background: 'var(--bg)', font: '700 10px var(--mono)', color: col }}>{h.toUpperCase()} · {v}</span> : null
                  })}
                </div>
              </section>
              <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
                {(['perfil_a', 'perfil_b'] as const).map((p) => {
                  const perfil = r.matchup_h[p]
                  return (
                    <section key={p} style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                      <div style={{ font: '700 12.5px var(--sans)', marginBottom: 9 }}>{p === 'perfil_a' ? r.partido.equipo_a : r.partido.equipo_b}</div>
                      {([['Sistema', perfil.sistema], ['Estilo', perfil.estilo], ['Fortaleza', perfil.fortaleza], ['Vulnerabilidad', perfil.vulnerabilidad]] as const).map(([k2, v]) => (
                        <div key={k2} style={{ display: 'flex', gap: 10, padding: '5px 0', borderBottom: '1px solid var(--line)' }}>
                          <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 96, flexShrink: 0, textTransform: 'uppercase', letterSpacing: '.3px' }}>{k2}</span>
                          <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{v ?? '—'}</span>
                        </div>
                      ))}
                    </section>
                  )
                })}
              </div>
            </div>
          )}

          {tab === 'lectura' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
                {([['Módulo operativo', r.lectura_sad.modulo_operativo], ['1X2', r.lectura_sad.un_x_dos.texto + (r.lectura_sad.un_x_dos.rango_ampliado ? ' · rango ampliado ±10% (FACTOR-X)' : '')], ['Contexto emocional', r.lectura_sad.contexto_emocional], ['Dato estructural', r.lectura_sad.dato_estructural]] as const).map(([titulo, texto]) => (
                  <section key={titulo} style={{ padding: '13px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                    <div style={{ font: '700 10px var(--mono)', color: 'var(--accent)', letterSpacing: '.6px', textTransform: 'uppercase', marginBottom: 6 }}>{titulo}</div>
                    <div style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', lineHeight: 1.5 }}>{texto}</div>
                  </section>
                ))}
              </div>
              {r.lectura_sad.paradoja && (
                <section style={{ padding: '13px 16px', borderRadius: 14, background: 'var(--mark-soft)', border: '1px solid color-mix(in oklch,var(--mark),transparent 55%)' }}>
                  <div style={{ font: '700 10px var(--mono)', color: 'var(--mark)', letterSpacing: '.6px', marginBottom: 6 }}>⚖️ PARADOJA DEL PARTIDO</div>
                  <div style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', lineHeight: 1.5 }}>{r.lectura_sad.paradoja}</div>
                </section>
              )}
              {r.datos_faltantes.length > 0 && (
                <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>Datos faltantes: {r.datos_faltantes.join(' · ')}</div>
              )}
              {r.fuentes.length > 0 && r.fuentes[0] !== 'demo' && (
                <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', wordBreak: 'break-word' }}>Fuentes: {r.fuentes.join(' · ')}</div>
              )}
            </div>
          )}

          {tab === 'calendario' && (
            <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
              {(['a', 'b'] as const).map((lado) => (
                <section key={lado} style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                  <div style={{ font: '700 12.5px var(--sans)', marginBottom: 8 }}>{lado === 'a' ? r.partido.equipo_a : r.partido.equipo_b} · próximos 4</div>
                  {r.equipos[lado].calendario.map((c2, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '8px 0', borderBottom: '1px solid var(--line)' }}>
                      <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 66, flexShrink: 0 }}>{c2.fecha ?? '—'}</span>
                      <span style={{ font: '700 10px var(--mono)', color: 'var(--t3)', width: 14, flexShrink: 0 }}>{c2.condicion}</span>
                      <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c2.rival}</span>
                      {c2.posicion != null && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>#{c2.posicion}</span>}
                      {c2.etiquetas.map((e2, j) => (
                        <span key={j} style={{ padding: '2px 7px', borderRadius: 6, background: 'var(--bg3)', font: '600 9px var(--mono)', color: 'var(--t2)', flexShrink: 0, whiteSpace: 'nowrap' }}>{e2}</span>
                      ))}
                    </div>
                  ))}
                </section>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
