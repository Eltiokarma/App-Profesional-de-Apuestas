import { useState } from 'react'
import { CONFIG } from '../config'
import { getDataSource } from '../services/datasource'
import { llaveAdmin } from '../lib/admin'

/** LA CUARENTENA EN UN PASO (10/11/2026, usuario: «poner algo en cuarentena es
 *  un dolor de huevos»). Antes había que buscar el caso en Aprendizaje, abrir
 *  una lección y recién ahí ponerla. Este formulario la pone por PARTIDO —uno o
 *  varios fixtures, motivo y «que siga enseñando»— y lo usan la tarjeta
 *  Decisiones pendientes (ya escrito con la propuesta del mantenimiento) y la
 *  pestaña «Buscar caso» de Aprendizaje (vacío). La regla no cambia: por
 *  criterio, nunca por resultado, motivo de 12+ caracteres y llave maestra. */
export const MOTIVO_MIN = 12

export function leerFixtures(texto: string): number[] {
  return [...new Set(texto.split(/[\s,;]+/).filter((w) => /^\d+$/.test(w)).map(Number).filter((n) => n > 0))]
}

export function FormCuarentena({ fixtures = [], motivo = '', ensena = false, textoBoton = 'Poner en cuarentena', onHecho, onCancelar }: {
  fixtures?: number[]
  motivo?: string
  ensena?: boolean
  textoBoton?: string
  /** con los partidos que quedaron en cuarentena (todos los pedidos: si uno falla, no se llama) */
  onHecho?: (r: { fixtures: number[]; motivo: string; ensena: boolean }) => void | Promise<void>
  onCancelar?: () => void
}) {
  const [fx, setFx] = useState(fixtures.join(' '))
  const [mot, setMot] = useState(motivo)
  const [ens, setEns] = useState(ensena)
  const [yendo, setYendo] = useState(false)
  const [error, setError] = useState('')
  const [hechos, setHechos] = useState<number[]>([])
  const ids = leerFixtures(fx)
  const listo = ids.length > 0 && mot.trim().length >= MOTIVO_MIN
  const sinLlave = CONFIG.dataSource === 'http' && !llaveAdmin()

  async function poner() {
    setYendo(true)
    setError('')
    const ok: number[] = []
    try {
      for (const id of ids) {
        await getDataSource().cuarentena(id, mot.trim(), ens)
        ok.push(id)
      }
      setHechos(ok)
      await onHecho?.({ fixtures: ok, motivo: mot.trim(), ensena: ens })
    } catch (e) {
      const m = e instanceof Error ? e.message : 'no se pudo poner la cuarentena'
      setError(ok.length ? `${ok.join(', ')} quedó en cuarentena; ${ids[ok.length]}: ${m}` : `${ids[0]}: ${m}`)
      setHechos(ok)
    } finally {
      setYendo(false)
    }
  }

  const campo = { padding: '6px 9px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '500 11px var(--mono)', minWidth: 0, boxSizing: 'border-box' as const }
  return (
    <div style={{ padding: '10px 12px', borderRadius: 10, background: 'var(--down-soft)', minWidth: 0 }}>
      <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t1)', marginBottom: 7 }}>
        Motivo: qué le faltaba a ESTE parte antes del pitazo («DT viejo», «insumo falso», «rodaje: primera semana»).
        Un fallo no es motivo. Se guarda el veredicto que tenía cada caso al ponerla.
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr)', gap: 6 }}>
        <input value={fx} onChange={(e) => setFx(e.target.value)} placeholder="partido(s): p. ej. 1639824 1639827"
          inputMode="numeric" aria-label="partidos (fixture)" style={campo} />
        <textarea value={mot} onChange={(e) => setMot(e.target.value)} placeholder={`motivo (mínimo ${MOTIVO_MIN} caracteres)`}
          rows={2} aria-label="motivo" style={{ ...campo, resize: 'vertical', font: '500 11px var(--sans)' }} />
      </div>
      <label style={{ display: 'flex', gap: 6, alignItems: 'flex-start', marginTop: 7, font: '500 10.5px var(--sans)', color: 'var(--t1)', cursor: 'pointer' }}>
        <input type="checkbox" checked={ens} onChange={(e) => setEns(e.target.checked)} style={{ marginTop: 2 }} />
        <span>Que siga enseñando: el caso sale de toda métrica, pero sus lecciones quedan con las del skill y fijan rúbrica (nunca mueven un número).</span>
      </label>
      {sinLlave ? (
        <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)', marginTop: 7 }}>Para ponerla, entra en modo administrador (🔑).</div>
      ) : (
        <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap', marginTop: 8, alignItems: 'center' }}>
          <button onClick={poner} disabled={yendo || !listo}
            style={{ padding: '6px 12px', borderRadius: 8, border: 0, cursor: listo ? 'pointer' : 'default', background: 'var(--down)', color: '#fff', font: '600 10.5px var(--sans)', opacity: listo ? 1 : 0.5 }}>
            {yendo ? '…' : `${textoBoton}${ids.length > 1 ? ` (${ids.length})` : ''}`}
          </button>
          {onCancelar && (
            <button onClick={onCancelar} disabled={yendo}
              style={{ padding: '6px 11px', borderRadius: 8, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', font: '600 10.5px var(--sans)', cursor: 'pointer' }}>
              Cancelar
            </button>
          )}
          {!listo && (
            <span style={{ font: '500 10px var(--sans)', color: 'var(--t3)' }}>
              {ids.length === 0 ? 'falta el número de partido' : `al motivo le faltan ${MOTIVO_MIN - mot.trim().length} caracteres`}
            </span>
          )}
        </div>
      )}
      {hechos.length > 0 && !error && (
        <div style={{ font: '600 10.5px var(--sans)', color: 'var(--up)', marginTop: 6 }}>
          En cuarentena{ens ? ' (enseña)' : ''}: {hechos.join(', ')}.
        </div>
      )}
      {error && <div style={{ font: '600 10.5px var(--sans)', color: 'var(--down)', marginTop: 6, overflowWrap: 'anywhere' }}>{error}</div>}
    </div>
  )
}
