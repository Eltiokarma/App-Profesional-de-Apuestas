import { useState } from 'react'
import type { StandingRowDTO } from '../api/types'
import { getDataSource } from '../services/datasource'
import { useAsync } from '../services/useAsync'

interface Props {
  ligaId: number
  /** Temporada a mostrar; sin ella, la más reciente. Al cambiarla vuelve al año. */
  temporada?: number
  /** Fases del torneo (Apertura/Clausura/…) de `Liga.fases`; [] = liga que no
   *  parte el año, y entonces no se pintan botones. */
  fases: string[]
  /** equipoIds a resaltar (los del partido que se analiza). */
  destacar?: number[]
  /** Nombres de respaldo: el motor demo no numera todos los equipos de la
   *  tabla, así que sin esto el resaltado se perdería en modo mock. */
  destacarNombres?: string[]
  /** Acciones a la derecha del título (los prompts de la página de liga);
   *  recibe la tabla ya cargada para no volver a pedirla. */
  acciones?: (tabla: StandingRowDTO[]) => React.ReactNode
}

const COLS = '24px minmax(0,1fr) 28px 30px 30px 34px'
const CABECERAS = ['#', 'Equipo', 'PJ', 'GF', 'GC', 'Pts'] as const

/**
 * Clasificación de una liga — ÚNICA tabla de posiciones de la app (página de
 * liga y panel de Estadísticas usan esta misma). Trae sus botones de fase
 * (Año · Apertura · Clausura · …) siempre que la liga parta la temporada, y
 * carga la tabla ella misma: cada torneo corto arranca de cero, así que la
 * fase es parte de la consulta, no un filtro local.
 */
export function TablaPosiciones({ ligaId, temporada, fases, destacar = [], destacarNombres = [], acciones }: Props) {
  // la fase va atada a liga+temporada: al cambiar cualquiera de las dos se
  // vuelve a la tabla del año (la fase anterior puede no existir en la nueva)
  const [sel, setSel] = useState<{ clave: string; fase: string | null } | null>(null)
  const clave = `${ligaId}:${temporada ?? ''}`
  const fase = sel && sel.clave === clave ? sel.fase : null
  const req = useAsync(
    () => getDataSource().standings(ligaId, temporada, fase ?? undefined),
    `${clave}:${fase ?? ''}`,
  )
  const tabla = req.data ?? []
  const resaltados = new Set(destacar)
  const resaltadosNombre = new Set(destacarNombres)

  const celda: React.CSSProperties = { padding: '7px 0', borderTop: '1px solid var(--line)' }
  const num: React.CSSProperties = { ...celda, font: '500 11px var(--mono)', color: 'var(--t2)', textAlign: 'right' }

  return (
    <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)', alignSelf: 'start' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 2 }}>
        <div style={{ font: '700 12px var(--sans)' }}>Clasificación</div>
        {acciones?.(tabla)}
      </div>

      {/* FASES: Apertura / Clausura / … según lo nombre la región. Solo
          aparecen cuando la liga parte el año (fases no vacío). */}
      {fases.length > 0 && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', margin: '10px 0 4px' }}>
          {[null, ...fases].map((f) => {
            const activa = fase === f
            return (
              <button
                key={f ?? '__año__'}
                onClick={() => setSel({ clave, fase: f })}
                title={f ? `Tabla de la fase ${f}` : 'Tabla acumulada de todo el año'}
                style={{ padding: '5px 12px', borderRadius: 999, border: activa ? '1px solid var(--accent)' : '1px solid var(--line)', background: activa ? 'var(--accent-soft)' : 'var(--bg3)', color: activa ? 'var(--accent)' : 'var(--t2)', font: '700 10.5px var(--sans)', cursor: 'pointer', letterSpacing: '.2px' }}
              >
                {f ?? 'Año'}
              </button>
            )
          })}
        </div>
      )}
      <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 12 }}>
        {fase ? `Fase ${fase} · ` : fases.length > 0 ? 'Tabla del año · ' : ''}Calculada con los fixtures finalizados capturados
      </div>

      {req.loading && <div className="sad-sk" style={{ height: 220 }}></div>}
      {req.error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', flex: 1 }}>No se pudo cargar la tabla: {req.error}</span>
          <button onClick={req.reload} style={{ padding: '5px 11px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg3)', color: 'var(--t1)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>Reintentar</button>
        </div>
      )}
      {!req.loading && !req.error && (tabla.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: COLS, gap: '0 5px', fontVariantNumeric: 'tabular-nums' }}>
          {CABECERAS.map((h, i) => (
            <span key={h} style={{ font: '600 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px', padding: '2px 0 8px', textAlign: i >= 2 ? 'right' : 'left' }}>{h}</span>
          ))}
          {tabla.map((r) => {
            const hl = resaltados.has(r.equipoId) || resaltadosNombre.has(r.nombre)
            return (
              <div key={r.equipoId} style={{ display: 'contents' }}>
                <span style={{ ...celda, font: '600 11px var(--mono)', color: hl ? 'var(--accent)' : r.posicion <= 4 ? 'var(--accent)' : 'var(--t3)' }}>{r.posicion}</span>
                <span style={{ ...celda, font: hl ? '700 11.5px var(--sans)' : '600 11.5px var(--sans)', color: hl ? 'var(--accent)' : 'var(--t1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.nombre}</span>
                <span style={num}>{r.partidosJugados}</span>
                <span style={num}>{r.golesFavor}</span>
                <span style={num}>{r.golesContra}</span>
                <span style={{ ...num, font: '700 11.5px var(--mono)', color: hl ? 'var(--accent)' : 'var(--t1)' }}>{r.puntos}</span>
              </div>
            )
          })}
        </div>
      ) : (
        <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: 12 }}>
          {fase ? `Sin fixtures finalizados de la fase ${fase}.` : 'Sin fixtures finalizados capturados para calcular la tabla.'}
        </div>
      ))}
    </section>
  )
}
