// Calendario SAD — los próximos partidos con el mapa de rivales del bloque G
// del protocolo EFE, calculado por el backend de nuestra propia base.
//
// Es UNA sola pieza para toda la app: donde antes cada pantalla dibujaba su
// propia lista de "próximos", ahora todas leen el mismo calendario y ven las
// mismas etiquetas. Cada etiqueta se muestra CON su dato ("3 derrotas
// seguidas"): un cartel sin cifra detrás es una opinión disfrazada de análisis.
import { binBadge } from '../lib/kview'
import type { CodigoEtiquetaRival, EtiquetaRivalDTO } from '../api/types'
import type { PartidoCalendarioUI } from '../services/appdata'

/** Color por etiqueta: lo que ayuda al foco en verde, lo que le pone freno en
 *  rojo, y en ámbar lo que solo avisa de que la lectura es frágil. */
const TONO: Record<CodigoEtiquetaRival, 'up' | 'down' | 'warn'> = {
  RECIEN_ASCENDIDO: 'warn',
  EN_CRISIS: 'up',
  LOCAL_FUERTE: 'down',
  VISITA_DEBIL: 'up',
  EQUIPO_SORPRESA: 'warn',
  BLOQUE_BAJO: 'down',
  CLASICO: 'warn',
}

const COLORES = {
  up: { fg: 'var(--up)', bg: 'color-mix(in oklch, var(--up), transparent 86%)' },
  down: { fg: 'var(--down)', bg: 'color-mix(in oklch, var(--down), transparent 86%)' },
  warn: { fg: '#B98A1D', bg: 'color-mix(in oklch, #E6B450, transparent 82%)' },
}

export function ChipEtiqueta({ e }: { e: EtiquetaRivalDTO }) {
  const c = COLORES[TONO[e.codigo] ?? 'warn']
  return (
    <span
      title={[e.dato, e.nota, e.parcial ? 'Criterio cubierto solo en parte: su ausencia no prueba nada' : null].filter(Boolean).join(' · ')}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 7px', borderRadius: 6, background: c.bg, color: c.fg, font: '700 8.5px var(--mono)', letterSpacing: '.3px', whiteSpace: 'nowrap' }}
    >
      {e.label}
      {e.parcial && <span style={{ opacity: 0.7 }}>·parcial</span>}
      <span style={{ font: '500 8.5px var(--mono)', opacity: 0.85 }}>{e.dato}</span>
    </span>
  )
}

interface Props {
  partidos: PartidoCalendarioUI[]
  loading?: boolean
  /** Título de la tarjeta (normalmente el nombre del equipo). */
  titulo: string
  /** Clic en una fila (p. ej. abrir el partido). Sin él, las filas no son botones. */
  onPartido?: (fixtureId: number) => void
}

export function CalendarioSad({ partidos, loading, titulo, onPartido }: Props) {
  return (
    <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ font: '700 12px var(--sans)', marginBottom: 4 }}>Calendario SAD · {titulo}</div>
      <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 12 }}>
        Próximos partidos · nivel del rival y contexto del bloque G, calculado de la base (sin IA)
      </div>
      {loading && <div className="sad-sk" style={{ height: 90 }} />}
      {!loading && partidos.length === 0 && (
        <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: '6px 0' }}>Sin partidos programados en los datos</div>
      )}
      {!loading &&
        partidos.map((p) => {
          const bb = binBadge(p.bin)
          const pos = p.posicionRival != null ? `${p.posicionRival}º` : null
          const zona = p.zonaRival === 'alta' ? 'var(--up)' : p.zonaRival === 'descenso' ? 'var(--down)' : 'var(--t3)'
          const fila = (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 40, flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>{p.fechaCorta}</span>
                <span title={p.condicion === 'L' ? 'De local' : 'De visitante'} style={{ font: '700 9px var(--mono)', color: 'var(--t2)', width: 12, flexShrink: 0 }}>{p.condicion}</span>
                <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', textAlign: 'left' }}>{p.rival}</span>
                {pos && (
                  <span title={p.equiposEnLaTabla ? `${pos} de ${p.equiposEnLaTabla} en la tabla` : undefined} style={{ font: '600 10px var(--mono)', color: zona, flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>{pos}</span>
                )}
                {p.diasDescanso != null && (
                  <span title="Días desde el partido anterior" style={{ font: '500 9.5px var(--mono)', color: p.diasDescanso <= 3 ? 'var(--down)' : 'var(--t3)', flexShrink: 0 }}>{p.diasDescanso}d</span>
                )}
                <span style={{ padding: '3px 9px', borderRadius: 6, background: bb.soft, color: bb.color, font: '700 9.5px var(--mono)', letterSpacing: '.3px', flexShrink: 0 }}>{p.binEtiqueta}</span>
              </div>
              {p.etiquetas.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, margin: '6px 0 0 52px' }}>
                  {p.etiquetas.map((e) => (
                    <ChipEtiqueta key={e.codigo} e={e} />
                  ))}
                </div>
              )}
            </>
          )
          const estilo = { padding: '9px 0', borderBottom: '1px solid var(--line)' }
          return onPartido ? (
            <button key={p.fixtureId} onClick={() => onPartido(p.fixtureId)} style={{ ...estilo, display: 'block', width: '100%', border: 0, borderBottom: '1px solid var(--line)', background: 'transparent', color: 'inherit', cursor: 'pointer', textAlign: 'left' }}>
              {fila}
            </button>
          ) : (
            <div key={p.fixtureId} style={estilo}>
              {fila}
            </div>
          )
        })}
    </section>
  )
}
