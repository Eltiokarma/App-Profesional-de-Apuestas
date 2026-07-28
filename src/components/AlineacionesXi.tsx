// Alineaciones confirmadas del partido — la ingesta en vivo las captura sola
// (~1 h antes del saque, backend/ingesta/en_vivo.py) y aquí se muestran en
// cuanto existen. Es el MISMO dato que reciben el EFE/DTP y los skills vía
// /fixtures/{id}/ficha: si esta tarjeta muestra el XI, el análisis ya puede
// completarse con la alineación real — regenerarlo con su botón de recarga.
// Regla "real o nada": sin XI publicado se dice eso, no se inventa un once.
import type { AlineacionDTO } from '../api/types'

const POS_LABEL: Record<string, string> = { G: 'POR', D: 'DEF', M: 'MED', F: 'DEL' }

function LadoXi({ ali, nombre }: { ali: AlineacionDTO; nombre: string }) {
  return (
    <div style={{ minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
        <span style={{ font: '700 13px var(--sans)', color: 'var(--t1)' }}>{nombre}</span>
        {ali.formacion && (
          <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--accent-soft)', color: 'var(--accent)', font: '700 10px var(--mono)', letterSpacing: '.3px' }}>{ali.formacion}</span>
        )}
        {ali.entrenador && <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>DT {ali.entrenador}</span>}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {ali.titulares.map((j) => (
          <div key={j.jugadorId} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t3)', width: 18, textAlign: 'right', flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>{j.numero ?? '–'}</span>
            <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', width: 26, flexShrink: 0, letterSpacing: '.3px' }}>{j.posicion ? POS_LABEL[j.posicion] ?? j.posicion : ''}</span>
            <span style={{ font: '500 12px var(--sans)', color: 'var(--t1)', minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.nombre ?? '—'}</span>
          </div>
        ))}
      </div>
      {ali.suplentes.length > 0 && (
        <div style={{ marginTop: 8, font: '500 10.5px var(--sans)', color: 'var(--t3)', lineHeight: 1.5 }}>
          Banco: {ali.suplentes.map((j) => j.nombre).filter(Boolean).join(', ')}
        </div>
      )}
      {!ali.conGrid && (
        <div style={{ marginTop: 6, font: '500 10px var(--mono)', color: 'var(--t3)' }}>sin grid de la API: el mapa de carriles del DTP no está disponible</div>
      )}
    </div>
  )
}

interface Props {
  local?: AlineacionDTO | null
  visitante?: AlineacionDTO | null
  localNombre: string
  visitanteNombre: string
  loading?: boolean
  error?: string | null
  /** Recarga la ficha del backend: el XI aparece solo al confirmarse (~1 h antes). */
  onReload: () => void
  isMobile: boolean
}

export function AlineacionesXi({ local, visitante, localNombre, visitanteNombre, loading, error, onReload, isMobile }: Props) {
  const hayXi = !!(local?.titulares.length || visitante?.titulares.length)
  return (
    <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: hayXi ? 14 : 8 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ font: '700 12px var(--sans)' }}>Alineaciones confirmadas</div>
          <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginTop: 2 }}>
            La ingesta las captura sola al publicarse (~1 h antes del saque) · son las que alimentan el análisis EFE/DTP y los skills
          </div>
        </div>
        <button
          onClick={onReload}
          disabled={loading}
          title="Volver a consultar la ficha del partido"
          style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 13px', borderRadius: 8, border: '1px solid var(--line2)', background: 'var(--bg3)', color: 'var(--t1)', cursor: loading ? 'default' : 'pointer', font: '600 11.5px var(--sans)', flexShrink: 0, opacity: loading ? 0.6 : 1 }}
        >
          <span style={{ display: 'inline-block', ...(loading ? { animation: 'sadspin .7s linear infinite' } : {}) }}>↻</span>
          Actualizar
        </button>
      </div>

      {error && (
        <div style={{ font: '500 11.5px var(--sans)', color: 'var(--down)' }}>No se pudo cargar la ficha: {error}</div>
      )}
      {!error && loading && !hayXi && <div className="sad-sk" style={{ height: 90 }} />}
      {!error && !loading && !hayXi && (
        <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', lineHeight: 1.5 }}>
          Aún sin XI publicado por la API. En cuanto exista se carga solo (y con ↻ lo traes al momento); entonces el análisis puede completarse con la alineación real.
        </div>
      )}
      {hayXi && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: isMobile ? 18 : 24 }}>
          {local && local.titulares.length > 0 && <LadoXi ali={local} nombre={localNombre} />}
          {visitante && visitante.titulares.length > 0 && <LadoXi ali={visitante} nombre={visitanteNombre} />}
        </div>
      )}
    </section>
  )
}
