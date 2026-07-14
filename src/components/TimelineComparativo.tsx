import { useMemo, useState } from 'react'
import type { TimelineData, TlEvento, TlTipoEvento } from '../api/types'

// Reglas de diseño del skill futbol-timeline (prompts/TIMELINE_prompt.md):
// fondo oscuro SIEMPRE (nunca blanco, también en modo día), eje temporal
// vertical central, equipo A a la izquierda / B a la derecha, eventos
// "ambos" centrados, pills por mes, badges por tipo, filtros locales.

const BADGE: Record<TlTipoEvento, { color: string; label: string }> = {
  resultado: { color: '#34C759', label: 'Victoria' },
  derrota: { color: '#E5484D', label: 'Derrota' },
  empate: { color: '#F2C744', label: 'Empate' },
  institucional: { color: '#A855F7', label: 'Institucional' },
  tecnico: { color: '#5B8DEF', label: 'Técnico' },
  sancion: { color: '#F2913D', label: 'Sanción' },
  hito: { color: '#22D3EE', label: 'Hito' },
}

const MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

function mesDe(fecha: string): string {
  // "2026-03-15" | "~2026-03" → "Mar 2026"
  const m = fecha.match(/(\d{4})-(\d{2})/)
  if (!m) return fecha
  const mes = MESES[parseInt(m[2], 10) - 1] ?? m[2]
  return `${mes} ${m[1]}`
}

function trimestreDe(fecha: string): string {
  const m = fecha.match(/(\d{4})-(\d{2})/)
  if (!m) return fecha
  return `T${Math.floor((parseInt(m[2], 10) - 1) / 3) + 1} ${m[1]}`
}

type Filtro = 'todo' | 'eq0' | 'eq1' | 'institucional' | 'partidos'

export function TimelineComparativo({ data, isMobile }: { data: TimelineData; isMobile: boolean }) {
  const [filtro, setFiltro] = useState<Filtro>('todo')
  const eqA = data.equipos[0]
  const eqB = data.equipos[1] ?? null
  const unSolo = !eqB

  const visibles = useMemo(() => {
    const esPartido = (t: TlTipoEvento) => t === 'resultado' || t === 'derrota' || t === 'empate'
    return data.eventos.filter((ev) => {
      if (filtro === 'todo') return true
      if (filtro === 'eq0') return ev.equipo === eqA?.nombre || ev.equipo === 'ambos'
      if (filtro === 'eq1') return ev.equipo === eqB?.nombre || ev.equipo === 'ambos'
      if (filtro === 'institucional') return !esPartido(ev.tipo)
      return esPartido(ev.tipo)
    })
  }, [data.eventos, filtro, eqA?.nombre, eqB?.nombre])

  // agrupación por mes (o trimestre) manteniendo el orden cronológico
  const grupos = useMemo(() => {
    const agrupa = data.agrupacion === 'trimestre' ? trimestreDe : mesDe
    const out: { etiqueta: string; eventos: TlEvento[] }[] = []
    for (const ev of visibles) {
      const et = agrupa(ev.fecha)
      const g = out[out.length - 1]
      if (g && g.etiqueta === et) g.eventos.push(ev)
      else out.push({ etiqueta: et, eventos: [ev] })
    }
    return out
  }, [visibles, data.agrupacion])

  const colorDe = (nombre: string) => (nombre === eqA?.nombre ? eqA?.color : nombre === eqB?.nombre ? eqB?.color : '#8b93a7')
  // eje: centrado con 2 equipos; a ~20% con uno solo (regla del skill)
  const ejeX = unSolo ? '20%' : '50%'
  const T = { t1: '#e8ecf4', t2: '#aab3c5', t3: '#717a8e', line: '#23283a' }

  const filtros: { k: Filtro; label: string }[] = [
    { k: 'todo', label: 'Todo' },
    { k: 'eq0', label: eqA?.nombre ?? 'Equipo A' },
    ...(eqB ? [{ k: 'eq1' as Filtro, label: eqB.nombre }] : []),
    { k: 'institucional', label: 'Institucional' },
    { k: 'partidos', label: 'Partidos' },
  ]

  const statsDe = (eq: typeof eqA) => {
    if (!eq) return []
    const s = eq.stats
    return [
      s.posicion > 0 ? `#${s.posicion} en la tabla` : '',
      s.puntos > 0 ? `${s.puntos} pts` : '',
      s.ultima_victoria ? `última victoria ${s.ultima_victoria}` : '',
      ...s.otros,
    ].filter(Boolean)
  }

  return (
    <div style={{ borderRadius: 16, background: '#0a0a0f', border: '1px solid #1c2130', padding: isMobile ? '16px 12px' : '20px 22px', color: T.t1 }}>
      {/* título + período */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ font: '800 15px var(--sans)', color: T.t1 }}>{data.titulo}</div>
        <div style={{ font: '500 10.5px var(--mono)', color: T.t3, marginTop: 3 }}>
          {data.periodo.desde} → {data.periodo.hasta} · agrupado por {data.agrupacion}
        </div>
      </div>

      {/* barra de stats por equipo */}
      <div style={{ display: 'grid', gridTemplateColumns: unSolo || isMobile ? '1fr' : '1fr 1fr', gap: 8, marginBottom: 12 }}>
        {[eqA, eqB].filter(Boolean).map((eq) => (
          <div key={eq!.nombre} style={{ padding: '8px 12px', borderRadius: 10, background: '#11141f', border: `1px solid ${eq!.color}44` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{ width: 9, height: 9, borderRadius: 3, background: eq!.color, flexShrink: 0 }}></span>
              <span style={{ font: '700 12px var(--sans)', color: T.t1 }}>{eq!.nombre}</span>
            </div>
            {statsDe(eq).length > 0 && (
              <div style={{ font: '500 10px var(--mono)', color: T.t2, marginTop: 4 }}>{statsDe(eq).join(' · ')}</div>
            )}
          </div>
        ))}
      </div>

      {/* narrativa del arco */}
      {data.narrativa && (
        <p style={{ margin: '0 0 12px', font: '500 12px var(--sans)', color: T.t2, lineHeight: 1.55 }}>{data.narrativa}</p>
      )}

      {/* filtros (estado local, sin re-fetch) */}
      <div className="sad-scroll" style={{ display: 'flex', gap: 6, marginBottom: 6, overflowX: 'auto', paddingBottom: 2 }}>
        {filtros.map((f) => (
          <button key={f.k} onClick={() => setFiltro(f.k)} style={{ flexShrink: 0, padding: '6px 12px', border: `1px solid ${filtro === f.k ? '#5B8DEF88' : T.line}`, borderRadius: 8, cursor: 'pointer', background: filtro === f.k ? '#5B8DEF22' : 'transparent', color: filtro === f.k ? '#9db9f5' : T.t2, font: '600 11px var(--sans)', whiteSpace: 'nowrap' }}>
            {f.label}
          </button>
        ))}
      </div>

      {/* leyenda */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 14 }}>
        {Object.entries(BADGE).map(([k, b]) => (
          <span key={k} style={{ display: 'flex', alignItems: 'center', gap: 5, font: '500 9.5px var(--mono)', color: T.t3 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: b.color }}></span>{b.label}
          </span>
        ))}
      </div>

      {/* eje temporal */}
      <div style={{ position: 'relative', paddingBottom: 6 }}>
        <div style={{ position: 'absolute', left: isMobile ? 14 : ejeX, top: 0, bottom: 0, width: 2, background: T.line, transform: isMobile ? 'none' : 'translateX(-1px)' }}></div>
        {grupos.map((g) => (
          <div key={g.etiqueta}>
            {/* pill del mes/trimestre */}
            <div style={{ display: 'flex', justifyContent: isMobile ? 'flex-start' : unSolo ? 'flex-start' : 'center', margin: '14px 0 10px', paddingLeft: isMobile ? 30 : unSolo ? 'calc(20% + 16px)' : 0 }}>
              <span style={{ position: 'relative', zIndex: 1, padding: '4px 12px', borderRadius: 999, background: '#181d2c', border: `1px solid ${T.line}`, font: '700 10px var(--mono)', color: T.t2, letterSpacing: '.5px' }}>
                {g.etiqueta.toUpperCase()}
              </span>
            </div>
            {g.eventos.map((ev, i) => {
              const badge = BADGE[ev.tipo]
              const ambos = ev.equipo === 'ambos'
              const izquierda = !ambos && (unSolo || ev.equipo === eqA?.nombre)
              const color = ambos ? '#8b93a7' : colorDe(ev.equipo)
              const card = (
                <div style={{
                  width: isMobile ? 'auto' : ambos ? '62%' : unSolo ? '72%' : '44%',
                  marginLeft: isMobile ? 30 : ambos ? 'auto' : izquierda && !unSolo ? 0 : unSolo ? 'calc(20% + 16px)' : 'auto',
                  marginRight: isMobile ? 0 : ambos ? 'auto' : izquierda && !unSolo ? 'auto' : 0,
                  padding: '10px 13px', borderRadius: 12, background: '#11141f',
                  border: `1px solid ${ev.destacado ? color : T.line}`,
                  boxShadow: ev.destacado ? `0 0 14px ${color}55` : 'none',
                  marginBottom: 10, position: 'relative', zIndex: 1,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7, flexWrap: 'wrap', marginBottom: 4 }}>
                    <span style={{ padding: '2px 8px', borderRadius: 6, background: badge.color + '26', color: badge.color, font: '700 9px var(--mono)', letterSpacing: '.4px' }}>{badge.label.toUpperCase()}</span>
                    <span style={{ font: '600 9.5px var(--mono)', color: T.t3 }}>
                      {ev.fecha.replace('~', '≈ ')}{ev.jornada > 0 ? ` · J${ev.jornada}` : ''}
                    </span>
                    {!ambos && !unSolo && (
                      <span style={{ font: '600 9.5px var(--mono)', color }}>{ev.equipo}</span>
                    )}
                    {ev.destacado && ev.alerta_relacionada && (
                      <span style={{ padding: '2px 7px', borderRadius: 6, background: color + '26', color, font: '700 9px var(--mono)' }}>{ev.alerta_relacionada}</span>
                    )}
                    {ev.marcador && <span style={{ marginLeft: 'auto', font: '700 12px var(--mono)', color: T.t1, fontVariantNumeric: 'tabular-nums' }}>{ev.marcador}</span>}
                  </div>
                  <div style={{ font: '700 12px var(--sans)', color: T.t1 }}>{ev.titulo}</div>
                  {ev.detalle && <div style={{ font: '500 11px var(--sans)', color: T.t2, marginTop: 3, lineHeight: 1.5 }}>{ev.detalle}</div>}
                </div>
              )
              return (
                <div key={ev.fecha + ev.titulo + i} style={{ position: 'relative' }}>
                  {/* dot en el eje, color del equipo */}
                  <span style={{ position: 'absolute', left: isMobile ? 14 : ejeX, top: 16, width: 10, height: 10, borderRadius: '50%', background: color, border: '2px solid #0a0a0f', transform: 'translateX(-5px)', zIndex: 2 }}></span>
                  {card}
                </div>
              )
            })}
          </div>
        ))}
        {visibles.length === 0 && (
          <div style={{ font: '500 12px var(--sans)', color: T.t3, padding: '18px 30px' }}>Sin eventos para este filtro.</div>
        )}
      </div>

      {/* pies: datos faltantes + fuentes */}
      {data.datos_faltantes.length > 0 && (
        <div style={{ font: '500 10px var(--mono)', color: T.t3, marginTop: 10, lineHeight: 1.6 }}>
          Datos faltantes: {data.datos_faltantes.join(' · ')}
        </div>
      )}
      {data.fuentes.length > 0 && (
        <div style={{ font: '500 9.5px var(--mono)', color: T.t3, marginTop: 6, lineHeight: 1.6, overflowWrap: 'anywhere' }}>
          Fuentes: {data.fuentes.join(' · ')}
        </div>
      )}
    </div>
  )
}
