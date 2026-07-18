import { useEffect, useState } from 'react'
import { TEAMS } from '../data'
import type { KCondKey, KTypeKey } from '../data/types'
import { ApuestasSalidas } from '../components/ApuestasSalidas'
import { KLineChart, KLineLegend } from '../components/KLineChart'
import { RachasCuotas, type CuotaCond } from '../components/RachasCuotas'
import { TeamBadge } from '../components/TeamBadge'
import { binBadge, FUSED_KEY, K_TYPE_GROUPS, K_WINDOW_OPTS, lastQ, signedVal, signFmt, streakLen } from '../lib/kview'
import type { FusedK } from '../motor/types'
import type { JugadorDTO } from '../api/types'
import { loadBurbujas, loadPlantilla, loadTeamFixtures, loadTeamStats } from '../services/appdata'
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
  const plant = useAsync(() => loadPlantilla(teamKey), teamKey)

  // ingesta on-demand: si el backend la lanzó (plantilla vacía), sondear
  // hasta que llegue (~5-6 requests del lado del servidor, unos segundos)
  const [sondeos, setSondeos] = useState(0)
  useEffect(() => setSondeos(0), [teamKey])
  useEffect(() => {
    const d = plant.data
    if (!plant.loading && !plant.error && d && d.jugadores.length === 0 && d.ingestaLanzada && sondeos < 8) {
      const t = setTimeout(() => {
        setSondeos((n) => n + 1)
        plant.reload()
      }, 8000)
      return () => clearTimeout(t)
    }
  }, [plant.loading, plant.error, plant.data, sondeos]) // eslint-disable-line react-hooks/exhaustive-deps

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

            {/* PLANTILLA — indicadores de jugadores (docs/JUGADORES.md) */}
            <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 4, flexWrap: 'wrap' }}>
                <div>
                  <div style={{ font: '700 12px var(--sans)' }}>Plantilla · indicadores</div>
                  <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>Por 90&apos; con encogimiento a la media de la posición · confianza A/B/C por minutos</div>
                </div>
                {plant.data && plant.data.jugadores.length > 0 && (
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {plant.data.entrenador?.nombre && (
                      <span style={{ padding: '4px 9px', borderRadius: 7, background: 'var(--bg3)', border: '1px solid var(--line)', font: '600 10px var(--mono)', color: 'var(--t2)' }}>DT {plant.data.entrenador.nombre}</span>
                    )}
                    {plant.data.dependencia.hhi != null && (
                      <span style={{ padding: '4px 9px', borderRadius: 7, background: 'var(--bg3)', border: '1px solid var(--line)', font: '600 10px var(--mono)', color: plant.data.dependencia.hhi >= 0.18 ? 'var(--down)' : 'var(--t2)' }}>
                        Dependencia {plant.data.dependencia.hhi >= 0.18 ? 'ALTA' : 'repartida'} · HHI {plant.data.dependencia.hhi.toFixed(2)}
                      </span>
                    )}
                    {(plant.data.revolucion.llegadas > 0 || plant.data.revolucion.salidas > 0) && (
                      <span style={{ padding: '4px 9px', borderRadius: 7, background: 'var(--bg3)', border: '1px solid var(--line)', font: '600 10px var(--mono)', color: 'var(--t2)' }}>
                        Ventana: +{plant.data.revolucion.llegadas} / −{plant.data.revolucion.salidas}
                      </span>
                    )}
                  </div>
                )}
              </div>
              {plant.loading && <div className="sad-sk" style={{ height: 160, marginTop: 10 }}></div>}
              {!plant.loading && plant.error && (
                <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: '10px 0' }}>No se pudo cargar la plantilla: {plant.error}</div>
              )}
              {!plant.loading && !plant.error && (!plant.data || plant.data.jugadores.length === 0) && (
                plant.data?.ingestaLanzada ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, font: '500 11.5px var(--sans)', color: 'var(--t2)', padding: '10px 0' }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)', animation: 'sadpulse 1.1s infinite' }}></span>
                    Trayendo la plantilla de la API — se actualiza sola en unos segundos…
                  </div>
                ) : (
                  <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: '10px 0' }}>
                    Plantilla sin capturar todavía — la ingesta de jugadores (python -m backend.ingesta.jugadores) la trae para los equipos con partidos próximos.
                  </div>
                )
              )}
              {!plant.loading && !plant.error && plant.data && plant.data.jugadores.length > 0 && (
                <div className="sad-scroll" style={{ display: 'flex', flexDirection: 'column', gap: 3, maxHeight: 440, overflowY: 'auto', paddingRight: 4, marginTop: 10 }}>
                  {/* cabecera de columnas */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 10px 4px 10px' }}>
                    <span style={{ width: 26 + 8 + 26, flexShrink: 0 }}></span>
                    <span style={{ flex: 1 }}></span>
                    <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', width: isMobile ? 34 : 74, textAlign: 'right', flexShrink: 0, letterSpacing: '.4px' }}>MIN</span>
                    <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', width: 92, textAlign: 'right', flexShrink: 0, letterSpacing: '.4px' }}>PRODUCCIÓN</span>
                    <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', width: 34, textAlign: 'center', flexShrink: 0, letterSpacing: '.4px' }}>RAT</span>
                    <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', width: 18, textAlign: 'center', flexShrink: 0, letterSpacing: '.4px' }}>±</span>
                  </div>
                  {([['Portero', 'PORTEROS', '#E6B450'], ['Defensa', 'DEFENSAS', '#5B8DEF'], ['Centrocampista', 'MEDIOCAMPO', '#2FBE6E'], ['Delantero', 'DELANTEROS', '#E5484D'], ['', 'OTROS', 'var(--t3)']] as [string, string, string][]).map(([pos, titulo, color]) => {
                    const grupo = plant.data!.jugadores.filter((j: JugadorDTO) => (pos ? j.posicion === pos : !['Portero', 'Defensa', 'Centrocampista', 'Delantero'].includes(j.posicion)))
                    if (grupo.length === 0) return null
                    return (
                      <div key={titulo}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '7px 2px 4px 2px' }}>
                          <span style={{ width: 8, height: 8, borderRadius: 3, background: color, flexShrink: 0 }}></span>
                          <span style={{ font: '700 9px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>{titulo}</span>
                          <span style={{ flex: 1, height: 1, background: 'var(--line)' }}></span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                          {grupo.map((j: JugadorDTO) => {
                            const esGK = j.posicion === 'Portero'
                            const confColor = j.confianza === 'A' ? 'var(--up)' : j.confianza === 'B' ? 'var(--t2)' : 'var(--t3)'
                            const ratBg = j.rating == null ? 'var(--bg3)' : j.rating >= 7 ? 'color-mix(in oklch, var(--up), transparent 82%)' : j.rating < 6.5 ? 'color-mix(in oklch, var(--down), transparent 84%)' : 'var(--bg3)'
                            const ratFg = j.rating == null ? 'var(--t3)' : j.rating >= 7 ? 'var(--up)' : j.rating < 6.5 ? 'var(--down)' : 'var(--t2)'
                            const pct = Math.round(j.pctMinutos * 100)
                            return (
                              <div key={j.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', borderRadius: 9, border: '1px solid var(--line)', background: 'var(--bg)', opacity: j.baja ? 0.72 : 1 }}>
                                {/* foto (de la API) o iniciales con el color de la posición */}
                                {j.foto ? (
                                  <img src={j.foto} alt="" loading="lazy" style={{ width: 26, height: 26, borderRadius: '50%', objectFit: 'cover', flexShrink: 0, background: 'var(--bg3)' }} />
                                ) : (
                                  <span style={{ width: 26, height: 26, borderRadius: '50%', background: `color-mix(in oklch, ${color}, transparent 80%)`, color, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 10px var(--sans)', flexShrink: 0 }}>{j.nombre.replace(/[^A-Za-zÁ-ÿ]/g, '').slice(0, 1) || '?'}</span>
                                )}
                                <span title={j.posicion || 'posición desconocida'} style={{ font: '700 8px var(--mono)', color, width: 26, flexShrink: 0, textTransform: 'uppercase' }}>{j.posicion ? j.posicion.slice(0, 3) : '?'}</span>
                                <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                  {j.nombre}
                                  {j.baja && <span title={j.baja.detalle ?? undefined} style={{ marginLeft: 6, padding: '2px 6px', borderRadius: 5, background: 'var(--down-soft)', color: 'var(--down)', font: '700 8.5px var(--mono)' }}>BAJA{j.baja.detalle ? ` · ${j.baja.detalle}` : ''}</span>}
                                  {j.enCapilla && !j.baja && <span title="Riesgo de sanción por acumulación de amarillas" style={{ marginLeft: 6, padding: '2px 6px', borderRadius: 5, background: 'color-mix(in oklch, #E6B450, transparent 82%)', color: '#B98A1D', font: '700 8.5px var(--mono)' }}>CAPILLA · {j.amarillas}🟨</span>}
                                  {j.recienLlegado && <span style={{ marginLeft: 6, padding: '2px 6px', borderRadius: 5, background: 'color-mix(in oklch, var(--accent), transparent 84%)', color: 'var(--accent)', font: '700 8.5px var(--mono)' }}>NUEVO{j.recienLlegado.desde ? ` · ${j.recienLlegado.desde}` : ''}</span>}
                                </span>
                                {/* minutos: barra + % */}
                                <span title={`${j.minutos} minutos · ${pct}% del más usado de la plantilla`} style={{ display: 'flex', alignItems: 'center', gap: 6, width: isMobile ? 34 : 74, flexShrink: 0, justifyContent: 'flex-end' }}>
                                  {!isMobile && (
                                    <span style={{ width: 34, height: 4, borderRadius: 2, background: 'var(--bg3)', overflow: 'hidden', flexShrink: 0 }}>
                                      <span style={{ display: 'block', width: `${pct}%`, height: '100%', borderRadius: 2, background: pct >= 70 ? 'var(--up)' : pct >= 35 ? color : 'var(--t3)' }}></span>
                                    </span>
                                  )}
                                  <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)', width: 30, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{pct}%</span>
                                </span>
                                {/* producción: G+A (con % del equipo) o métricas de portero */}
                                {esGK ? (
                                  <span title="Paradas y goles encajados por 90 minutos" style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)', width: 92, textAlign: 'right', flexShrink: 0, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>
                                    {j.paradasP90 != null ? `${j.paradasP90.toFixed(1)}🧤 ${j.golesEncajadosP90?.toFixed(1)}GC` : '—'}
                                  </span>
                                ) : (
                                  <span title={`${j.goles} goles + ${j.asistencias} asistencias · ${Math.round(j.participacionOfensiva * 100)}% de la producción del equipo`} style={{ display: 'flex', alignItems: 'center', gap: 5, width: 92, flexShrink: 0, justifyContent: 'flex-end' }}>
                                    <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>{j.goles}G+{j.asistencias}A</span>
                                    {j.participacionOfensiva >= 0.1 && (
                                      <span style={{ padding: '1px 5px', borderRadius: 4, background: 'color-mix(in oklch, var(--up), transparent 82%)', color: 'var(--up)', font: '700 9.5px var(--mono)', fontVariantNumeric: 'tabular-nums' }}>{Math.round(j.participacionOfensiva * 100)}%</span>
                                    )}
                                  </span>
                                )}
                                <span title="Rating medio ponderado por minutos" style={{ padding: '3px 0', borderRadius: 6, background: ratBg, color: ratFg, width: 34, textAlign: 'center', flexShrink: 0, font: '700 10.5px var(--mono)', fontVariantNumeric: 'tabular-nums' }}>{j.rating != null ? j.rating.toFixed(1) : '—'}</span>
                                <span title={`Confianza estadística por minutos jugados (${j.minutos} min)${j.recienLlegado ? ' · recién llegado: baja un grado' : ''}`} style={{ width: 18, height: 18, borderRadius: 5, background: 'var(--bg3)', color: confColor, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 9.5px var(--mono)', flexShrink: 0 }}>{j.confianza}</span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
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
