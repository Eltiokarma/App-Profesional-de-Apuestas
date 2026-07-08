import { TEAMS } from '../data'
import type { Match } from '../data/types'
import type { GapEquipoDTO } from '../api/types'
import { TeamBadge } from '../components/TeamBadge'
import { rng } from '../lib/odds'
import { loadEstadisticas, loadPrediccion } from '../services/appdata'
import { TEAM_NUM } from '../services/datasource'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  m: Match
  isMobile: boolean
}

function GapCard({ g, name, align }: { g: GapEquipoDTO; name: string; align: 'left' | 'right' }) {
  const color = g.gap == null ? 'var(--t3)' : g.tendencia === 'mejora' ? 'var(--up)' : 'var(--down)'
  const soft = g.gap == null ? 'var(--bg3)' : g.tendencia === 'mejora' ? 'var(--up-soft)' : 'var(--down-soft)'
  return (
    <div style={{ padding: '12px 14px', borderRadius: 12, background: 'var(--bg)', border: '1px solid var(--line)', textAlign: align }}>
      <div style={{ font: '600 11px var(--sans)', color: 'var(--t2)', marginBottom: 6 }}>{name}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, justifyContent: align === 'right' ? 'flex-end' : 'flex-start' }}>
        <span style={{ font: '700 24px var(--mono)', color, fontVariantNumeric: 'tabular-nums' }}>
          {g.gap == null ? '—' : (g.gap > 0 ? '+' : '') + g.gap.toFixed(2)}
        </span>
        {g.senal && (
          <span style={{ padding: '3px 9px', borderRadius: 6, background: soft, color, font: '700 9.5px var(--mono)', letterSpacing: '.3px' }}>
            {g.senal.toUpperCase()}{g.tendencia ? ` · ${g.tendencia === 'mejora' ? 'TIENDE A MEJORAR' : 'TIENDE A EMPEORAR'}` : ''}
          </span>
        )}
      </div>
      <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginTop: 6 }}>
        forma últ. 5: {g.ptsRecientes == null ? '—' : g.ptsRecientes.toFixed(2)} pts · esperado μ: {g.ptsEsperados.toFixed(2)} pts · nivel {g.nivel.toFixed(2)}
      </div>
    </div>
  )
}

export function Estadisticas({ store, m, isMobile }: Props) {
  void store
  const pred = useAsync(() => loadPrediccion(m.id), m.id)
  const est = useAsync(() => loadEstadisticas(m), m.id)
  const H = TEAMS[m.home]
  const A = TEAMS[m.away]
  const gridStats = isMobile ? '1fr' : 'minmax(0,1fr) 320px'

  const formChip = (arr: string[]) => arr.map((r) => ({ r, bg: r === 'W' ? 'var(--up)' : r === 'D' ? 'var(--t3)' : 'var(--down)' }))

  // filas de comparativa desde el contrato; las avanzadas solo si el backend las sirve
  const row = (label: string, hv: number, av: number) => {
    const tot = hv + av || 1
    const fmt = (v: number) => (v % 1 ? v.toFixed(2) : String(v)) + (label.includes('%') ? '%' : '')
    return {
      label,
      homeVal: fmt(hv),
      awayVal: fmt(av),
      homePct: Math.round((hv / tot) * 100),
      awayPct: Math.round((av / tot) * 100),
      homeStrong: hv >= av ? 'var(--t1)' : 'var(--t3)',
      awayStrong: av >= hv ? 'var(--t1)' : 'var(--t3)',
    }
  }
  const d = est.data
  const compareRows = d
    ? ([
        ['GOLES A FAVOR / P', d.home.golesFavorProm, d.away.golesFavorProm],
        ['GOLES EN CONTRA / P', d.home.golesContraProm, d.away.golesContraProm],
        ['xG POR PARTIDO', d.home.xgProm, d.away.xgProm],
        ['POSESIÓN %', d.home.posesionProm, d.away.posesionProm],
        ['TIROS A PUERTA', d.home.tirosPuertaProm, d.away.tirosPuertaProm],
        ['CÓRNERS / P', d.home.cornersProm, d.away.cornersProm],
        ['PUNTOS', d.home.puntos, d.away.puntos],
      ] as [string, number | null, number | null][])
        .filter(([, hv, av]) => hv != null && av != null)
        .map(([label, hv, av]) => row(label, hv!, av!))
    : []

  // posiciones desde la tabla del contrato (por id; nombre como fallback)
  const posOf = (teamKey: string): number | null => {
    if (!d) return null
    const id = TEAM_NUM[teamKey]
    const r = d.tabla.find((x) => (id != null && x.equipoId === id) || x.nombre === TEAMS[teamKey].name)
    return r ? r.posicion : null
  }
  const homePos = posOf(m.home)
  const awayPos = posOf(m.away)

  const standings = d
    ? d.tabla.map((s) => {
        const hl = (TEAM_NUM[m.home] != null && s.equipoId === TEAM_NUM[m.home]) || (TEAM_NUM[m.away] != null && s.equipoId === TEAM_NUM[m.away]) || s.nombre === H.name || s.nombre === A.name
        return { pos: s.posicion, name: s.nombre, pts: s.puntos, bg: hl ? 'var(--accent-soft)' : 'transparent', posColor: hl ? 'var(--accent)' : 'var(--t3)', nameColor: hl ? 'var(--t1)' : 'var(--t2)' }
      })
    : []

  // H2H sigue siendo demo local: el contrato aún no tiene endpoint de enfrentamientos
  const r2 = rng(m.id + 'h2h')
  const hw = 2 + ((r2() * 5) | 0)
  const aw = 2 + ((r2() * 4) | 0)
  const dr = 1 + ((r2() * 3) | 0)
  const h2h = {
    home: hw, draw: dr, away: aw,
    last: [
      { when: '2024', match: H.short + ' vs ' + A.short, score: '1-2', color: 'var(--down)' },
      { when: '2024', match: A.short + ' vs ' + H.short, score: '0-0', color: 'var(--t2)' },
      { when: '2023', match: H.short + ' vs ' + A.short, score: '2-1', color: 'var(--up)' },
      { when: '2023', match: A.short + ' vs ' + H.short, score: '1-1', color: 'var(--t2)' },
    ],
  }

  return (
    <div>
      <div style={{ marginBottom: 18 }}>
        <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Estadísticas del equipo</h1>
        <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>Comparativa temporada · {H.name} vs {A.name}</p>
      </div>

      {est.error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--down)', flexShrink: 0 }}></span>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudieron cargar las estadísticas: {est.error}</span>
          <button onClick={est.reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)', flexShrink: 0 }}>Reintentar</button>
        </div>
      )}
      {est.loading && (
        <div>
          <div className="sad-sk" style={{ height: 132, marginBottom: 14 }}></div>
          <div className="sad-sk" style={{ height: 150, marginBottom: 14 }}></div>
          <div style={{ display: 'grid', gridTemplateColumns: gridStats, gap: 14 }}>
            <div className="sad-sk" style={{ height: 330 }}></div>
            <div className="sad-sk" style={{ height: 330 }}></div>
          </div>
        </div>
      )}
      {d && (
        <>
      <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)', marginBottom: 14 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: 14, marginBottom: 18 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
            <TeamBadge logo={H.logo} short={H.short} color={H.color} fg={H.fg} size={34} />
            <div>
              <div style={{ font: '700 14px var(--sans)' }}>{H.name}</div>
              <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>Local{homePos != null ? ` · ${homePos}º` : ''} · {d.home.partidosJugados} PJ</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', letterSpacing: '1px' }}>FORMA · ÚLT. 5</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 11, justifyContent: 'flex-end' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ font: '700 14px var(--sans)' }}>{A.name}</div>
              <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>Visitante{awayPos != null ? ` · ${awayPos}º` : ''} · {d.away.partidosJugados} PJ</div>
            </div>
            <TeamBadge logo={A.logo} short={A.short} color={A.color} fg={A.fg} size={34} />
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: 14 }}>
          <div style={{ display: 'flex', gap: 5 }}>
            {formChip(d.home.forma).map((f, i) => (
              <span key={i} style={{ width: 24, height: 24, borderRadius: 6, background: f.bg, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 10px var(--mono)' }}>{f.r}</span>
            ))}
          </div>
          <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>W · D · L</span>
          <div style={{ display: 'flex', gap: 5, justifyContent: 'flex-end' }}>
            {formChip(d.away.forma).map((f, i) => (
              <span key={i} style={{ width: 24, height: 24, borderRadius: 6, background: f.bg, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 10px var(--mono)' }}>{f.r}</span>
            ))}
          </div>
        </div>
      </section>

      {/* REGRESIÓN AL NIVEL (§5) */}
      <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 10, marginBottom: 12, flexWrap: 'wrap' }}>
          <div style={{ font: '700 12px var(--sans)' }}>Regresión al nivel · Ley §5</div>
          <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>gap = μ esperado − forma últ. 5 · gap &gt; 0 subrinde (tiende a mejorar)</div>
        </div>
        {pred.loading && <div className="sad-sk" style={{ height: 96 }}></div>}
        {pred.error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderRadius: 10, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
            <span style={{ font: '500 12px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudo cargar la predicción: {pred.error}</span>
            <button onClick={pred.reload} style={{ padding: '6px 11px', borderRadius: 7, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11px var(--sans)' }}>Reintentar</button>
          </div>
        )}
        {pred.data && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr auto 1fr', alignItems: 'stretch', gap: 14 }}>
              <GapCard g={pred.data.local} name={H.name} align="left" />
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 4, padding: '0 6px' }}>
                <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', letterSpacing: '1px' }}>GAP DIFERENCIAL</span>
                <span style={{ font: '700 20px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
                  {pred.data.gapDiff == null ? '—' : (pred.data.gapDiff > 0 ? '+' : '') + pred.data.gapDiff.toFixed(2)}
                </span>
                <span style={{ font: '500 9px var(--mono)', color: 'var(--t3)' }}>local − visitante</span>
              </div>
              <GapCard g={pred.data.visitante} name={A.name} align="right" />
            </div>
            {(pred.data.local.senal === 'fuerte' || pred.data.visitante.senal === 'fuerte') && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', marginTop: 12, borderRadius: 10, background: 'var(--mark-soft)', border: '1px solid color-mix(in oklch,var(--mark),transparent 60%)' }}>
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--mark)', flexShrink: 0 }}></span>
                <span style={{ font: '500 12px var(--sans)', color: 'var(--t1)' }}>Señal fuerte de regresión: <strong>el value no cura el reset</strong> — con señal clara, la cuota no justifica ir en contra.</span>
              </div>
            )}
          </>
        )}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: gridStats, gap: 14 }}>
        <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
          <div style={{ font: '700 12px var(--sans)', marginBottom: 14 }}>Comparativa de rendimiento</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {compareRows.map((rw, i) => (
              <div key={i}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ font: '600 13px var(--mono)', color: rw.homeStrong }}>{rw.homeVal}</span>
                  <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px' }}>{rw.label}</span>
                  <span style={{ font: '600 13px var(--mono)', color: rw.awayStrong }}>{rw.awayVal}</span>
                </div>
                <div style={{ display: 'flex', gap: 4, height: 8 }}>
                  <div style={{ flex: rw.homePct, background: 'var(--accent)', borderRadius: 5, opacity: 0.85 }}></div>
                  <div style={{ flex: rw.awayPct, background: 'var(--t3)', borderRadius: 5, opacity: 0.5 }}></div>
                </div>
              </div>
            ))}
          </div>
          {d.home.xgProm == null && (
            <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginTop: 12 }}>xG, posesión, tiros y córners llegarán cuando el backend los derive de las estadísticas por partido.</div>
          )}
        </section>

        <aside style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 12 }}>Enfrentamientos directos <span style={{ font: '500 9px var(--mono)', color: 'var(--t3)' }}>· demo</span></div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <div style={{ flex: 1, textAlign: 'center' }}>
                <div style={{ font: '700 20px var(--mono)', color: 'var(--accent)' }}>{h2h.home}</div>
                <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)' }}>{H.short}</div>
              </div>
              <div style={{ flex: 1, textAlign: 'center' }}>
                <div style={{ font: '700 20px var(--mono)', color: 'var(--t2)' }}>{h2h.draw}</div>
                <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)' }}>EMPATES</div>
              </div>
              <div style={{ flex: 1, textAlign: 'center' }}>
                <div style={{ font: '700 20px var(--mono)', color: 'var(--t1)' }}>{h2h.away}</div>
                <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)' }}>{A.short}</div>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {h2h.last.map((l, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 9px', borderRadius: 8, background: 'var(--bg)' }}>
                  <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', width: 54 }}>{l.when}</span>
                  <span style={{ font: '600 11px var(--sans)', color: 'var(--t2)', flex: 1 }}>{l.match}</span>
                  <span style={{ font: '700 11px var(--mono)', color: l.color }}>{l.score}</span>
                </div>
              ))}
            </div>
          </section>
          <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 10 }}>Tabla de posiciones</div>
            {standings.map((st, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 8px', borderRadius: 7, background: st.bg }}>
                <span style={{ font: '600 11px var(--mono)', color: st.posColor, width: 18 }}>{st.pos}</span>
                <span style={{ font: '600 12px var(--sans)', color: st.nameColor, flex: 1 }}>{st.name}</span>
                <span style={{ font: '600 11px var(--mono)', color: 'var(--t2)' }}>{st.pts}</span>
              </div>
            ))}
            {standings.length === 0 && <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)' }}>Sin tabla para esta liga.</div>}
          </section>
        </aside>
      </div>
        </>
      )}
    </div>
  )
}
