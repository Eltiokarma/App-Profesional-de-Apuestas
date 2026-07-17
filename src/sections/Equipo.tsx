import { useState } from 'react'
import { TEAMS } from '../data'
import type { KCondKey, KTypeKey } from '../data/types'
import { ApuestasSalidas } from '../components/ApuestasSalidas'
import { KLineChart, KLineLegend } from '../components/KLineChart'
import { RachasCuotas, type CuotaCond } from '../components/RachasCuotas'
import { TeamBadge } from '../components/TeamBadge'
import { binBadge, FUSED_KEY, K_TYPE_GROUPS, K_WINDOW_OPTS, lastQ, signedVal, signFmt, streakLen } from '../lib/kview'
import type { FusedK } from '../motor/types'
import { loadBurbujas, loadTeamFixtures, loadTeamStats } from '../services/appdata'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  teamKey: string
  isMobile: boolean
}

/** Página de equipo tipo Sofascore: identidad, nivel, momentum K e historial. */
export function Equipo({ store, teamKey, isMobile }: Props) {
  const { s } = store
  const T = TEAMS[teamKey]
  const stats = useAsync(() => loadTeamStats(teamKey), teamKey)
  const bur = useAsync(() => loadBurbujas(teamKey), teamKey)
  const fx = useAsync(() => loadTeamFixtures(teamKey), teamKey)

  const kType: KTypeKey = s.kType
  const kCond: KCondKey = s.kCond
  const key = FUSED_KEY[kType][kCond]
  const snaps = bur.data?.snaps ?? []
  let maxAbs = 0.001
  for (const sn of snaps.slice(-s.kWindow)) maxAbs = Math.max(maxAbs, Math.abs(sn.fused[key]))

  const kv = (kk: keyof FusedK) => (snaps.length ? snaps[snaps.length - 1].fused[kk] : 0)
  const kColor = (v: number) => (v === 0 ? 'var(--t3)' : v > 0 ? 'var(--up)' : 'var(--down)')
  const bb = bur.data ? binBadge(bur.data.bin) : null

  const cur = snaps.length ? snaps[snaps.length - 1].fused[key] : 0
  const sv = signedVal(kType, cur)
  const racha = streakLen(snaps, key)
  const q = lastQ(snaps, kType, kCond)

  const partidos = fx.data ?? []
  const cargando = stats.loading || bur.loading || fx.loading
  const error = stats.error || bur.error || fx.error

  const condOpts = ([['total', 'Total'], ['local', 'Local'], ['visita', 'Visita']] as [KCondKey, string][])

  // Cuotas K (§3.8): toggle TODOS/LOCAL/VISITA; las barras viven en RachasCuotas
  const [cuotaCond, setCuotaCond] = useState<CuotaCond>('TODOS')

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16, flexWrap: 'wrap' }}>
        <TeamBadge logo={T.logo} short={T.short} color={T.color} fg={T.fg} size={52} ring />
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>{T.name}</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 5, flexWrap: 'wrap' }}>
            {bur.data && bb && (
              <span style={{ padding: '4px 10px', borderRadius: 7, background: bb.soft, color: bb.color, font: '700 10.5px var(--mono)', letterSpacing: '.3px' }}>
                Nivel {bur.data.level.toFixed(2)} · {bur.data.binLabel} · bin {bur.data.bin}
              </span>
            )}
            {stats.data && (
              <span style={{ font: '500 11px var(--mono)', color: 'var(--t3)' }}>{stats.data.partidosJugados} PJ · {stats.data.puntos} pts · GF {stats.data.golesFavorProm.toFixed(2)} · GC {stats.data.golesContraProm.toFixed(2)}</span>
            )}
          </div>
        </div>
        {stats.data && (
          <div style={{ display: 'flex', gap: 5 }}>
            {stats.data.forma.map((r, i) => (
              <span key={i} style={{ width: 24, height: 24, borderRadius: 6, background: r === 'W' ? 'var(--up)' : r === 'D' ? 'var(--t3)' : 'var(--down)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 10px var(--mono)' }}>{r}</span>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudo cargar el equipo: {error}</span>
          <button onClick={() => { stats.reload(); bur.reload(); fx.reload() }} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)' }}>Reintentar</button>
        </div>
      )}
      {cargando && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'minmax(0,1fr) 320px', gap: 14 }}>
          <div className="sad-sk" style={{ height: 420 }}></div>
          <div className="sad-sk" style={{ height: 420 }}></div>
        </div>
      )}

      {!cargando && !error && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'minmax(0,1fr) 320px', gap: 14 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* MOMENTUM K */}
            <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 12, flexWrap: 'wrap' }}>
                <div style={{ font: '700 12px var(--sans)' }}>Momentum · Constantes K</div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 3, padding: 5, borderRadius: 9, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
                    {K_TYPE_GROUPS.map((g) => (
                      <div key={g.label} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                        <span style={{ font: '600 8px var(--mono)', color: 'var(--t3)', width: 52, textTransform: 'uppercase', letterSpacing: '.4px', flexShrink: 0 }}>{g.label}</span>
                        <div style={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                          {g.opts.map(([k, l]) => (
                            <button key={k} onClick={store.setKType(k)} style={{ padding: '4px 7px', border: 0, borderRadius: 6, cursor: 'pointer', background: s.kType === k ? 'var(--bg1)' : 'transparent', color: s.kType === k ? 'var(--t1)' : 'var(--t2)', font: '600 10px var(--sans)' }}>{l}</button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ display: 'flex', padding: 3, borderRadius: 9, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
                      {condOpts.map(([k, l]) => (
                        <button key={k} onClick={store.setKCond(k)} style={{ padding: '5px 10px', border: 0, borderRadius: 6, cursor: 'pointer', background: s.kCond === k ? 'var(--bg1)' : 'transparent', color: s.kCond === k ? 'var(--t1)' : 'var(--t2)', font: '600 10.5px var(--sans)' }}>{l}</button>
                      ))}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                      <span style={{ font: '600 8px var(--mono)', color: 'var(--t3)', textTransform: 'uppercase', letterSpacing: '.4px' }}>Ver</span>
                      <div style={{ display: 'flex', padding: 3, borderRadius: 9, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
                        {K_WINDOW_OPTS.map(([n, l]) => (
                          <button key={n} onClick={store.setWindow(n)} style={{ padding: '5px 10px', border: 0, borderRadius: 6, cursor: 'pointer', background: s.kWindow === n ? 'var(--bg1)' : 'transparent', color: s.kWindow === n ? 'var(--t1)' : 'var(--t2)', font: '600 10.5px var(--sans)' }}>{l}</button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div style={{ borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)', padding: 6 }}>
                <KLineChart snaps={snaps} kType={kType} kCond={kCond} maxAbs={maxAbs} window={s.kWindow} />
              </div>
              <KLineLegend />
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <div style={{ flex: 1, padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
                  <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)', marginBottom: 2 }}>K ACTUAL</div>
                  <div style={{ font: '700 16px var(--mono)', color: kColor(sv), fontVariantNumeric: 'tabular-nums' }}>{signFmt(sv)}</div>
                </div>
                <div style={{ flex: 1, padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
                  <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)', marginBottom: 2 }}>RACHA</div>
                  <div style={{ font: '700 16px var(--mono)', color: 'var(--t1)' }}>{racha} <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>partidos</span></div>
                </div>
                <div style={{ flex: 1, padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
                  <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)', marginBottom: 2 }}>ÚLTIMO q</div>
                  <div style={{ font: '700 16px var(--mono)', color: q == null ? 'var(--t3)' : q > 0 ? 'var(--up)' : q < 0 ? 'var(--down)' : 'var(--t2)' }}>{q == null ? '—' : signFmt(q)}</div>
                </div>
              </div>
            </section>

            {/* CUOTAS K (§3.8) — barras de rachas de suma de cuota 1X2 */}
            <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 4, flexWrap: 'wrap' }}>
                <div>
                  <div style={{ font: '700 12px var(--sans)' }}>Cuotas K · rachas 1X2</div>
                  <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>Suma acumulada de la cuota; la barra cae a 0 al romperse la racha · solo 2026</div>
                </div>
                <div style={{ display: 'flex', padding: 3, borderRadius: 9, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
                  {(['TODOS', 'LOCAL', 'VISITA'] as const).map((c) => (
                    <button key={c} onClick={() => setCuotaCond(c)} style={{ padding: '5px 12px', border: 0, borderRadius: 6, cursor: 'pointer', background: cuotaCond === c ? 'var(--bg1)' : 'transparent', color: cuotaCond === c ? 'var(--t1)' : 'var(--t2)', font: '600 10.5px var(--sans)' }}>{c}</button>
                  ))}
                </div>
              </div>
              <RachasCuotas teamKey={teamKey} cond={cuotaCond} />
            </section>

            {/* APUESTAS QUE SALIERON — cuota que pagó el 1X2 de los últimos partidos */}
            <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ font: '700 12px var(--sans)', marginBottom: 2 }}>Apuestas que salieron</div>
              <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 12 }}>Últimos 3 partidos · cuota prepartido del 1X2 que ocurrió (rentabilidad reciente)</div>
              <ApuestasSalidas teamKey={teamKey} nombre={T?.name ?? teamKey} />
            </section>

            {/* HISTORIAL DE PARTIDOS */}
            <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ font: '700 12px var(--sans)', marginBottom: 2 }}>Partidos</div>
              <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 12 }}>Toda la historia capturada · clic para analizar (cuotas guardadas incluidas)</div>
              <div className="sad-scroll" style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 420, overflowY: 'auto', paddingRight: 4 }}>
                {partidos.map((m) => {
                  const esLocal = m.home === teamKey
                  const rivalKey = esLocal ? m.away : m.home
                  const RV = TEAMS[rivalKey]
                  const goles = m.score.split('-').map((x) => parseInt(x.trim()) || 0)
                  const gf = esLocal ? goles[0] : goles[1]
                  const ga = esLocal ? goles[1] : goles[0]
                  const res = m.status !== 'fin' ? null : gf > ga ? 'W' : gf === ga ? 'D' : 'L'
                  const live = m.status === 'live'
                  return (
                    <button key={m.id} onClick={store.selectMatch(m)} style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '9px 11px', borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg)', cursor: 'pointer', textAlign: 'left' }}>
                      {res ? (
                        <span style={{ width: 22, height: 22, borderRadius: 6, background: res === 'W' ? 'var(--up)' : res === 'D' ? 'var(--t3)' : 'var(--down)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 10px var(--mono)', flexShrink: 0 }}>{res}</span>
                      ) : (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4, width: 34, font: '700 8.5px var(--mono)', color: live ? 'var(--down)' : 'var(--accent)', flexShrink: 0 }}>
                          {live && <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>}
                          {live ? m.min : 'PROX'}
                        </span>
                      )}
                      <span style={{ font: '600 11px var(--mono)', color: 'var(--t3)', width: 22, flexShrink: 0 }}>{esLocal ? 'vs' : 'en'}</span>
                      <TeamBadge logo={RV?.logo} short={RV?.short ?? '?'} color={RV?.color ?? 'var(--bg3)'} fg={RV?.fg ?? 'var(--t2)'} size={22} />
                      <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{RV?.name ?? rivalKey}</span>
                      <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>{m.comp}</span>
                      <span style={{ font: '700 13px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums', minWidth: 44, textAlign: 'right', flexShrink: 0 }}>
                        {m.status === 'sched' ? m.min : m.score}
                      </span>
                    </button>
                  )
                })}
                {partidos.length === 0 && <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: 12 }}>Sin partidos capturados para este equipo.</div>}
              </div>
            </section>
          </div>

          <aside style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ font: '700 12px var(--sans)', marginBottom: 10 }}>Constantes K actuales</div>
              {([['K resultado', 'k', false], ['K local', 'kLocal', false], ['K visita', 'kVisita', false], ['K goles anot.', 'golesAnotado', false], ['K goles rec.', 'golesRecibido', true]] as [string, keyof FusedK, boolean][]).map(
                ([label, kk, inv]) => {
                  const v = kv(kk)
                  const disp = inv ? (v === 0 ? '0.0' : '−' + Math.abs(v).toFixed(1)) : signFmt(v)
                  return (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', borderBottom: '1px solid var(--line)' }}>
                      <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t2)', flex: 1 }}>{label}</span>
                      <span style={{ font: '600 12.5px var(--mono)', color: kColor(inv ? -v : v), fontVariantNumeric: 'tabular-nums' }}>{disp}</span>
                    </div>
                  )
                },
              )}
              {bur.data && (
                <div style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', marginTop: 10 }}>{snaps.length} partidos procesados por el motor</div>
              )}
            </section>
            {stats.data && (
              <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                <div style={{ font: '700 12px var(--sans)', marginBottom: 10 }}>Temporada</div>
                {([['Partidos jugados', String(stats.data.partidosJugados)], ['Puntos', String(stats.data.puntos)], ['Goles a favor / P', stats.data.golesFavorProm.toFixed(2)], ['Goles en contra / P', stats.data.golesContraProm.toFixed(2)]] as [string, string][]).map(([l, v]) => (
                  <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', borderBottom: '1px solid var(--line)' }}>
                    <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t2)', flex: 1 }}>{l}</span>
                    <span style={{ font: '600 12.5px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{v}</span>
                  </div>
                ))}
                {stats.data.xgProm != null && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0' }}>
                    <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t2)', flex: 1 }}>xG por partido</span>
                    <span style={{ font: '600 12.5px var(--mono)', color: 'var(--t1)' }}>{stats.data.xgProm.toFixed(2)}</span>
                  </div>
                )}
              </section>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}
