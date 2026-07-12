import { useRef, useState } from 'react'
import { TEAMS } from '../data'
import type { Match, MatchStatus } from '../data/types'
import { TeamBadge } from '../components/TeamBadge'
import { TeamSearch } from '../components/TeamSearch'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  matches: Match[]
  loading: boolean
  error: string | null
  reload: () => void
  isMobile: boolean
}

type Filtro = 'todos' | MatchStatus

const DIAS = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB']
const dd = (n: number) => String(n).padStart(2, '0')
const isoDia = (d: Date) => `${d.getFullYear()}-${dd(d.getMonth() + 1)}-${dd(d.getDate())}`

/** Chips de día estilo BeSoccer: hoy ± 3 con AYER/HOY/MAÑANA. */
function diasBarra(fechaSel: string): { value: string; label: string }[] {
  const hoy = new Date()
  const chips = []
  for (let rel = -3; rel <= 3; rel++) {
    const d = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() + rel)
    const label = rel === 0 ? 'HOY' : rel === -1 ? 'AYER' : rel === 1 ? 'MAÑANA' : `${DIAS[d.getDay()]} ${dd(d.getDate())}`
    chips.push({ value: isoDia(d), label })
  }
  if (!chips.some((c) => c.value === fechaSel)) {
    const d = new Date(fechaSel + 'T12:00:00')
    const chip = { value: fechaSel, label: `${DIAS[d.getDay()]} ${dd(d.getDate())}/${dd(d.getMonth() + 1)}` }
    if (fechaSel < chips[0].value) chips.unshift(chip)
    else chips.push(chip)
  }
  return chips
}

/** Pantalla inicial: los partidos del día elegido, agrupados por competición. */
export function Partidos({ store, matches, loading, error, reload, isMobile }: Props) {
  const { s } = store
  const [filtro, setFiltro] = useState<Filtro>('todos')
  const [texto, setTexto] = useState('')
  const dateRef = useRef<HTMLInputElement>(null)

  const norm = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  const t = norm(texto.trim())
  const visibles = matches.filter((m) => {
    if (filtro !== 'todos' && m.status !== filtro) return false
    if (!t) return true
    const H = TEAMS[m.home]
    const A = TEAMS[m.away]
    return norm(H?.name ?? '').includes(t) || norm(A?.name ?? '').includes(t)
  })

  // agrupado por ID de liga, no por nombre: la API llama "Copa de la Liga"
  // tanto a la de Perú como a la de Chile y por nombre se mezclaban
  const grupos: { comp: string; pais: string | null; ligaId?: number; img?: string | null; rows: Match[] }[] = []
  for (const m of visibles) {
    const g = grupos.find((x) => (x.ligaId != null && m.ligaId != null ? x.ligaId === m.ligaId : x.comp === m.comp))
    if (g) g.rows.push(m)
    // bandera del país; en copas internacionales (sin bandera) cae al logo del torneo
    else grupos.push({ comp: m.comp, pais: m.ligaPais ?? null, ligaId: m.ligaId, img: m.ligaBandera ?? m.ligaLogo, rows: [m] })
  }
  // torneos homónimos de países distintos: se distinguen con " · País"
  const repetidos = new Set(grupos.filter((g) => grupos.some((o) => o !== g && o.comp === g.comp)).map((g) => g.comp))
  for (const g of grupos) if (repetidos.has(g.comp) && g.pais) g.comp = `${g.comp} · ${g.pais}`

  const chips: { k: Filtro; label: string }[] = [
    { k: 'todos', label: 'Todos' },
    { k: 'live', label: 'En vivo' },
    { k: 'sched', label: 'Próximos' },
    { k: 'fin', label: 'Pasados' },
  ]
  const nLive = matches.filter((m) => m.status === 'live').length

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Partidos</h1>
          <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>
            Elige un día y un partido para analizarlo
            {nLive > 0 && <span style={{ color: 'var(--down)', font: '600 12px var(--mono)' }}> · {nLive} en vivo</span>}
          </p>
        </div>
        <TeamSearch store={store} width={isMobile ? '100%' : 260} />
      </div>

      {/* barra de fechas estilo BeSoccer */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <div className="sad-scroll" style={{ display: 'flex', gap: 4, padding: 4, borderRadius: 11, background: 'var(--bg2)', border: '1px solid var(--line)', overflowX: 'auto', flex: isMobile ? 1 : 'initial' }}>
          {diasBarra(s.fecha).map((c) => {
            const activo = c.value === s.fecha
            return (
              <button
                key={c.value}
                onClick={() => store.setFecha(c.value)}
                style={{ padding: '8px 13px', border: 0, borderRadius: 8, cursor: 'pointer', background: activo ? 'var(--accent-soft)' : 'transparent', color: activo ? 'var(--accent)' : c.label === 'HOY' ? 'var(--t1)' : 'var(--t2)', font: `700 11px var(--mono)`, letterSpacing: '.4px', whiteSpace: 'nowrap', flexShrink: 0 }}
              >
                {c.label}
              </button>
            )
          })}
        </div>
        <button
          onClick={() => dateRef.current?.showPicker?.()}
          style={{ display: 'flex', alignItems: 'center', padding: '9px 11px', borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)', cursor: 'pointer', flexShrink: 0, position: 'relative' }}
          title="Ir a una fecha"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--t2)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
          </svg>
          <input
            ref={dateRef}
            type="date"
            value={s.fecha}
            onChange={(e) => e.target.value && store.setFecha(e.target.value)}
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0, border: 0, padding: 0, pointerEvents: 'none' }}
            tabIndex={-1}
          />
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
          {chips.map((c) => (
            <button key={c.k} onClick={() => setFiltro(c.k)} style={{ padding: '7px 13px', border: 0, borderRadius: 7, cursor: 'pointer', background: filtro === c.k ? 'var(--bg3)' : 'transparent', color: filtro === c.k ? 'var(--t1)' : 'var(--t2)', font: '600 11.5px var(--sans)' }}>
              {c.label}
            </button>
          ))}
        </div>
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Filtrar por equipo…"
          style={{ flex: 1, minWidth: 160, maxWidth: 280, padding: '9px 12px', borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg2)', color: 'var(--t1)', font: '600 12px var(--sans)', outline: 'none' }}
        />
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudieron cargar los partidos: {error}</span>
          <button onClick={reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)' }}>Reintentar</button>
        </div>
      )}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div className="sad-sk" style={{ height: 64 }}></div>
          <div className="sad-sk" style={{ height: 64 }}></div>
          <div className="sad-sk" style={{ height: 64 }}></div>
          <div className="sad-sk" style={{ height: 64 }}></div>
        </div>
      )}

      {!loading &&
        grupos.map((grp) => (
          <section key={grp.ligaId ?? grp.comp} style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 2px 8px' }}>
              <span style={{ width: 5, height: 15, borderRadius: 2, background: 'var(--accent)' }}></span>
              {grp.ligaId != null ? (
                <button className="sad-hover" onClick={() => store.openLiga(grp.ligaId!)} title={`Ver información de ${grp.comp}`} style={{ display: 'flex', alignItems: 'center', gap: 7, background: 'transparent', border: 0, cursor: 'pointer', padding: '3px 7px', margin: '-3px -7px', borderRadius: 7, textAlign: 'left', flex: 1, minWidth: 0 }}>
                  {grp.img && <img src={grp.img} alt="" width={16} height={12} style={{ objectFit: 'cover', borderRadius: 2, flexShrink: 0 }} />}
                  <span style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{grp.comp}</span>
                </button>
              ) : (
                <span style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>{grp.comp}</span>
              )}
              <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>{grp.rows.length}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {grp.rows.map((m) => {
                const H = TEAMS[m.home]
                const A = TEAMS[m.away]
                const live = m.status === 'live'
                const fin = m.status === 'fin'
                const activo = store.s.matchId === m.id
                return (
                  <button
                    key={m.id}
                    onClick={store.selectMatch(m)}
                    style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '13px 16px', borderRadius: 13, cursor: 'pointer', textAlign: 'left', background: activo ? 'var(--accent-soft)' : 'var(--bg2)', border: `1px solid ${activo ? 'color-mix(in oklch,var(--accent),transparent 55%)' : 'var(--line)'}` }}
                  >
                    <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 10 }}>
                      <span style={{ font: '600 13px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', textAlign: 'right' }}>{H?.name ?? m.home}</span>
                      <TeamBadge logo={H?.logo} short={H?.short ?? '?'} color={H?.color ?? 'var(--bg3)'} fg={H?.fg ?? 'var(--t2)'} size={28} />
                    </span>
                    <span style={{ width: 74, flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
                      <span style={{ font: '700 16px var(--mono)', color: m.status === 'sched' ? 'var(--t2)' : 'var(--t1)', fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>
                        {m.status === 'sched' ? m.min : m.score}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4, font: '700 9px var(--mono)', color: live ? 'var(--down)' : fin ? 'var(--t3)' : 'var(--accent)', letterSpacing: '.3px' }}>
                        {live && <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--down)', animation: 'sadpulse 1.1s infinite' }}></span>}
                        {live ? m.min : fin ? 'FIN' : 'PROX'}
                      </span>
                    </span>
                    <span style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
                      <TeamBadge logo={A?.logo} short={A?.short ?? '?'} color={A?.color ?? 'var(--bg3)'} fg={A?.fg ?? 'var(--t2)'} size={28} />
                      <span style={{ font: '600 13px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{A?.name ?? m.away}</span>
                    </span>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M9 6l6 6-6 6" /></svg>
                  </button>
                )
              })}
            </div>
          </section>
        ))}
      {!loading && !error && visibles.length === 0 && (
        <div style={{ font: '500 12.5px var(--sans)', color: 'var(--t3)', padding: 24, textAlign: 'center' }}>
          {matches.length === 0 ? 'Sin partidos este día.' : 'Sin partidos para este filtro.'}
        </div>
      )}
    </div>
  )
}
