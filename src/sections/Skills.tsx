import { SKILL_DEFS, TEAMS } from '../data'
import type { Match } from '../data/types'
import type { GapEquipoDTO } from '../api/types'
import { loadAnalisis } from '../services/appdata'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  m: Match
  isMobile: boolean
}

interface TextReport {
  abbr: string
  title: string
  iconBg: string
  iconColor: string
  sections: { h: string; body: string; tags: string[] }[]
}

export function Skills({ store, m, isMobile }: Props) {
  const { s } = store
  const H = TEAMS[m.home]
  const A = TEAMS[m.away]
  const gridSkills = isMobile ? '1fr' : 'minmax(0,1fr) 290px'
  const gridSkillCards = isMobile ? '1fr' : '1fr 1fr'

  const skills = SKILL_DEFS.map((d) => {
    const st = s.skillStatus[d.key]
    return {
      key: d.key, abbr: d.abbr, name: d.name, desc: d.desc, iconBg: d.iconBg, iconColor: d.iconColor,
      isIdle: st === 'idle', isGen: st === 'gen', isDone: st === 'done', canGen: st === 'idle',
      time: s.skillTime[d.key] || '',
      border: s.openReport === d.key ? 'var(--accent)' : 'var(--line)',
    }
  })

  const op = s.openReport
  const reportEFE = op === 'efe'
  const efeTime = s.skillTime.efe || ''

  const mkArc = (p: number) => {
    const a = Math.PI * (1 - p)
    const x = 52 + 44 * Math.cos(a)
    const y = 56 - 44 * Math.sin(a)
    return `M8 56 A44 44 0 0 1 ${x.toFixed(1)} ${y.toFixed(1)}`
  }
  const efeGauges = [
    { label: 'Estabilidad global', val: '78', p: 0.78, color: 'var(--up)' },
    { label: 'Cohesión de bloques', val: '71', p: 0.71, color: 'var(--accent)' },
    { label: 'Riesgo de rotación', val: '34', p: 0.34, color: 'var(--mark)' },
  ].map((g) => ({ label: g.label, val: g.val, arc: mkArc(g.p), color: g.color }))
  const efeBlocks = [
    { name: 'A · Portería', val: '92', pct: '92%', color: 'var(--up)' },
    { name: 'B · Defensa', val: '74', pct: '74%', color: 'var(--up)' },
    { name: 'C · Pivotes', val: '63', pct: '63%', color: 'var(--mark)' },
    { name: 'D · Bandas', val: '58', pct: '58%', color: 'var(--mark)' },
    { name: 'E · Ataque', val: '81', pct: '81%', color: 'var(--accent)' },
  ]
  const efeAlerts = [
    { text: 'Bloque D con 3 cambios en 5 jornadas — banda derecha inestable.', color: 'var(--down)', soft: 'var(--down-soft)', line: 'color-mix(in oklch,var(--down),transparent 60%)' },
    { text: 'Pivote titular en duda — impacto medio en cohesión C.', color: 'var(--mark)', soft: 'var(--mark-soft)', line: 'color-mix(in oklch,var(--mark),transparent 60%)' },
  ]

  // reporte SAD alimentado por el contrato (/analisis-prepartido)
  const analisis = useAsync(() => loadAnalisis(m.id), m.id)
  const fmtGap = (g: GapEquipoDTO) =>
    g.gap == null ? 'sin datos de forma' : `gap ${g.gap > 0 ? '+' : ''}${g.gap.toFixed(2)} (${g.senal}, ${g.tendencia === 'mejora' ? 'tiende a mejorar' : 'tiende a empeorar'})`
  const ad = analisis.data
  const sadReport: TextReport = ad
    ? {
        abbr: 'SAD', title: 'Análisis Pre-Partido', iconBg: 'var(--up-soft)', iconColor: 'var(--up)',
        sections: [
          {
            h: 'Resumen ejecutivo · Motor SAD',
            body: ad.resumen,
            tags: [`${H.short} ${ad.niveles.local.nivel.toFixed(2)} · ${ad.niveles.local.binEtiqueta}`, `${A.short} ${ad.niveles.visitante.nivel.toFixed(2)} · ${ad.niveles.visitante.binEtiqueta}`],
          },
          {
            h: 'Momentum · constantes K',
            body:
              `${H.name}: K ${ad.constantes.local ? ad.constantes.local.fusion.k.toFixed(1) : '—'} · ` +
              `${A.name}: K ${ad.constantes.visitante ? ad.constantes.visitante.fusion.k.toFixed(1) : '—'}. ` +
              'K > 0 racha positiva activa; K = 0 recién reseteada; K < 0 mala racha.',
            tags: [
              `K local ${ad.constantes.local ? ad.constantes.local.fusion.kLocal.toFixed(1) : '—'}`,
              `K visita ${ad.constantes.visitante ? ad.constantes.visitante.fusion.kVisita.toFixed(1) : '—'}`,
            ],
          },
          {
            h: 'Regresión al nivel (§5)',
            body:
              `${H.name}: ${fmtGap(ad.prediccion.local)}. ${A.name}: ${fmtGap(ad.prediccion.visitante)}.` +
              (ad.prediccion.local.senal === 'fuerte' || ad.prediccion.visitante.senal === 'fuerte'
                ? ' Señal fuerte: el value no cura el reset — no ir contra la regresión por cuota.'
                : ''),
            tags: ad.prediccion.gapDiff == null ? [] : [`gap diferencial ${ad.prediccion.gapDiff > 0 ? '+' : ''}${ad.prediccion.gapDiff.toFixed(2)}`],
          },
        ],
      }
    : {
        abbr: 'SAD', title: 'Análisis Pre-Partido', iconBg: 'var(--up-soft)', iconColor: 'var(--up)',
        sections: [{ h: 'Resumen ejecutivo', body: analisis.error ? `No se pudo cargar el análisis: ${analisis.error}` : 'Cargando análisis del motor…', tags: [] }],
      }

  const textReports: Record<string, TextReport> = {
    sad: sadReport,
    tac: {
      abbr: 'DT', title: 'Diagnóstico Táctico', iconBg: 'var(--mark-soft)', iconColor: 'var(--mark)',
      sections: [
        { h: 'Sistema esperado', body: H.name + ' en 4-2-3-1 con laterales profundos; ' + A.name + ' responde en 4-3-3 buscando amplitud.', tags: ['4-2-3-1', '4-3-3'] },
        { h: 'Fortalezas', body: 'Solidez defensiva local y juego asociativo por dentro. Visitante peligroso a la contra.', tags: ['Defensa sólida', 'Contraataque'] },
        { h: 'Debilidades a explotar', body: 'Espacios a la espalda del lateral derecho local; lentitud en repliegue visitante tras pérdida.', tags: ['Banda derecha', 'Repliegue'] },
      ],
    },
    tl: {
      abbr: 'TL', title: 'Timeline', iconBg: 'var(--down-soft)', iconColor: 'var(--down)',
      sections: [
        { h: '0–15’ · Tanteo', body: 'Inicio cauto, local con la posesión y visitante replegado en bloque medio.', tags: [] },
        { h: '15–60’ · Control local', body: 'Mayor volumen ofensivo local; ventana de gol entre el 30’ y 50’ según el modelo.', tags: ['Pico de xG 30-50’'] },
        { h: '60–90’ · Apertura', body: 'El visitante adelanta líneas buscando el empate; aumenta la probabilidad de gol en transición.', tags: ['Riesgo a la contra'] },
      ],
    },
  }
  const rt = op ? textReports[op] : undefined
  const reportText = !!rt
  const noReport = !op

  const history = s.history.map((h) => {
    const d = SKILL_DEFS.find((x) => x.key === h.key)!
    return { key: h.key, abbr: d.abbr, name: d.name, time: 'Hoy · ' + h.time, iconBg: d.iconBg, iconColor: d.iconColor, bg: s.openReport === h.key ? 'var(--accent-soft)' : 'transparent' }
  })

  return (
    <div>
      <div style={{ marginBottom: 18 }}>
        <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Skills de Claude</h1>
        <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>Genera reportes de IA sobre {H.name} vs {A.name}</p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: gridSkills, gap: 16 }}>
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: gridSkillCards, gap: 12, marginBottom: 14 }}>
            {skills.map((sk) => (
              <section key={sk.key} style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: `1px solid ${sk.border}`, display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 11 }}>
                  <div style={{ width: 38, height: 38, borderRadius: 10, background: sk.iconBg, color: sk.iconColor, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '800 13px var(--mono)', flexShrink: 0 }}>{sk.abbr}</div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ font: '700 14px var(--sans)' }}>{sk.name}</div>
                    <div style={{ font: '500 11px var(--sans)', color: 'var(--t2)', lineHeight: 1.4, marginTop: 2 }}>{sk.desc}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto' }}>
                  {sk.isIdle && <span style={{ display: 'flex', alignItems: 'center', gap: 6, font: '500 11px var(--mono)', color: 'var(--t3)' }}><span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--t3)' }}></span>Listo</span>}
                  {sk.isGen && <span style={{ display: 'flex', alignItems: 'center', gap: 7, font: '500 11px var(--mono)', color: 'var(--accent)' }}><span style={{ width: 13, height: 13, border: '2px solid var(--accent-soft)', borderTopColor: 'var(--accent)', borderRadius: '50%', animation: 'sadspin .7s linear infinite' }}></span>Generando…</span>}
                  {sk.isDone && <span style={{ display: 'flex', alignItems: 'center', gap: 6, font: '500 11px var(--mono)', color: 'var(--up)' }}><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--up)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6L9 17l-5-5" /></svg>{sk.time}</span>}
                  {sk.isDone && <button onClick={store.openReport(sk.key)} style={{ padding: '7px 13px', borderRadius: 8, border: '1px solid var(--line2)', background: 'var(--bg3)', color: 'var(--t1)', cursor: 'pointer', font: '600 11.5px var(--sans)' }}>Abrir</button>}
                  {sk.canGen && <button onClick={store.generate(sk.key)} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--accent)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)' }}>Generar reporte</button>}
                </div>
              </section>
            ))}
          </div>

          {/* REPORT VIEWER */}
          {reportEFE && (
            <section style={{ padding: 20, borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)', animation: 'sadup .2s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
                <div style={{ width: 34, height: 34, borderRadius: 9, background: 'var(--accent-soft)', color: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '800 12px var(--mono)' }}>EFE</div>
                <div>
                  <div style={{ font: '700 16px var(--sans)' }}>Estabilidad de Formación</div>
                  <div style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>Dashboard · generado {efeTime}</div>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 16 }}>
                {efeGauges.map((g, i) => (
                  <div key={i} style={{ padding: 14, borderRadius: 12, background: 'var(--bg)', border: '1px solid var(--line)', textAlign: 'center' }}>
                    <div style={{ position: 'relative', width: 104, height: 60, margin: '0 auto 8px' }}>
                      <svg width="104" height="60" viewBox="0 0 104 60">
                        <path d="M8 56 A44 44 0 0 1 96 56" fill="none" stroke="var(--line2)" strokeWidth="9" strokeLinecap="round" />
                        <path d={g.arc} fill="none" stroke={g.color} strokeWidth="9" strokeLinecap="round" />
                      </svg>
                      <div style={{ position: 'absolute', left: 0, right: 0, bottom: 2, font: '700 22px var(--mono)', color: 'var(--t1)' }}>{g.val}</div>
                    </div>
                    <div style={{ font: '600 11px var(--sans)', color: 'var(--t2)' }}>{g.label}</div>
                  </div>
                ))}
              </div>
              <div style={{ font: '700 12px var(--sans)', marginBottom: 10 }}>Bloques A–E · estabilidad por línea</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 9, marginBottom: 16 }}>
                {efeBlocks.map((bl, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ font: '700 11px var(--mono)', color: 'var(--t2)', width: 90 }}>{bl.name}</span>
                    <div style={{ flex: 1, height: 10, borderRadius: 6, background: 'var(--bg3)', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: bl.pct, background: bl.color, borderRadius: 6 }}></div>
                    </div>
                    <span style={{ font: '600 11px var(--mono)', color: 'var(--t1)', width: 34, textAlign: 'right' }}>{bl.val}</span>
                  </div>
                ))}
              </div>
              <div style={{ font: '700 12px var(--sans)', marginBottom: 10 }}>Alertas</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {efeAlerts.map((al, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderRadius: 10, background: al.soft, border: `1px solid ${al.line}` }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: al.color, flexShrink: 0 }}></span>
                    <span style={{ font: '500 12px var(--sans)', color: 'var(--t1)' }}>{al.text}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {reportText && rt && (
            <section style={{ padding: 22, borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)', animation: 'sadup .2s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
                <div style={{ width: 34, height: 34, borderRadius: 9, background: rt.iconBg, color: rt.iconColor, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '800 12px var(--mono)' }}>{rt.abbr}</div>
                <div>
                  <div style={{ font: '700 16px var(--sans)' }}>{rt.title}</div>
                  <div style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>Reporte estructurado · {op ? s.skillTime[op] || '' : ''}</div>
                </div>
              </div>
              {rt.sections.map((rs, i) => (
                <div key={i} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 7 }}>
                    <span style={{ width: 3, height: 14, borderRadius: 2, background: 'var(--accent)' }}></span>
                    <span style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)' }}>{rs.h}</span>
                  </div>
                  <p style={{ margin: '0 0 0 11px', font: '500 12.5px var(--sans)', color: 'var(--t2)', lineHeight: 1.6 }}>{rs.body}</p>
                  {rs.tags.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, margin: '9px 0 0 11px' }}>
                      {rs.tags.map((tg, ti) => (
                        <span key={ti} style={{ padding: '4px 10px', borderRadius: 7, background: 'var(--bg3)', border: '1px solid var(--line)', font: '600 10.5px var(--mono)', color: 'var(--t2)' }}>{tg}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </section>
          )}

          {noReport && (
            <section style={{ padding: 40, borderRadius: 16, background: 'var(--bg2)', border: '1px dashed var(--line2)', textAlign: 'center' }}>
              <div style={{ font: '600 13px var(--sans)', color: 'var(--t2)' }}>Genera o abre un reporte para verlo aquí</div>
              <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', marginTop: 4 }}>El EFE se muestra como dashboard; los demás como reporte por secciones.</div>
            </section>
          )}
        </div>

        <aside>
          <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 12 }}>Historial de reportes</div>
            {history.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {history.map((h, i) => (
                  <button key={i} onClick={store.openReport(h.key)} style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: 10, borderRadius: 10, border: '1px solid var(--line)', background: h.bg, cursor: 'pointer', textAlign: 'left' }}>
                    <div style={{ width: 28, height: 28, borderRadius: 8, background: h.iconBg, color: h.iconColor, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '800 9.5px var(--mono)', flexShrink: 0 }}>{h.abbr}</div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ font: '600 12px var(--sans)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{h.name}</div>
                      <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>{h.time}</div>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: '8px 0', lineHeight: 1.5 }}>Aún no has generado reportes para este partido.</div>
            )}
          </section>
        </aside>
      </div>
    </div>
  )
}
