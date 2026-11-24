import { useState } from 'react'
import type { JevPingDTO, JevReetiquetarDTO } from '../api/types'
import { getDataSource } from '../services/datasource'
import { llaveAdmin } from '../lib/admin'

/** Jev desde la app (24/11/2026, usuario: «haz el botón en la app»). Los tres
 *  pasos que antes pedían una terminal con la llave maestra: probar la clave,
 *  contar los veredictos cuyo modo de fallo quedó sellado con un error de Jev
 *  (402 sin crédito desde el 22/11) y volver a preguntarlos. Todo con el modo
 *  administrador (🔑): la llave nunca viaja en el código de la web.
 *  El re-etiquetado va por tandas de TANDA: cada una es una llamada a Jev por
 *  veredicto y una sola de cientos pasaría el tiempo de espera del servidor. */
const TANDA = 40

type Paso = '' | 'ping' | 'contar' | 'aplicar'

export function PanelJev() {
  const [abierto, setAbierto] = useState(false)
  const [yendo, setYendo] = useState<Paso>('')
  const [ping, setPing] = useState<JevPingDTO | null>(null)
  const [cuenta, setCuenta] = useState<JevReetiquetarDTO | null>(null)
  const [hechos, setHechos] = useState(0)
  const [ultimo, setUltimo] = useState<JevReetiquetarDTO | null>(null)
  const [error, setError] = useState('')
  const admin = !!llaveAdmin()

  async function correr(paso: Paso, f: () => Promise<void>) {
    setError('')
    setYendo(paso)
    try {
      await f()
    } catch (e) {
      const m = e instanceof Error ? e.message : 'no respondió'
      setError(/401|403|permiso|token/i.test(m) ? `${m} — activá el modo administrador (🔑) con la llave maestra` : m)
    } finally {
      setYendo('')
    }
  }
  const probar = () => correr('ping', async () => setPing(await getDataSource().jevPing()))
  const contar = () => correr('contar', async () => setCuenta(await getDataSource().jevReetiquetar(false)))
  const aplicar = () => correr('aplicar', async () => {
    const r = await getDataSource().jevReetiquetar(true, TANDA)
    setUltimo(r)
    setHechos((n) => n + r.reetiquetados.length)
    setCuenta({ ...r, pendientes: r.quedan ?? Math.max(0, r.pendientes - r.reetiquetados.length) })
  })

  const boton = (activo: boolean): React.CSSProperties => ({
    padding: '7px 12px', borderRadius: 8, border: 0, cursor: activo ? 'pointer' : 'default',
    background: activo ? 'var(--accent)' : 'var(--bg3)', color: activo ? '#fff' : 'var(--t3)', font: '700 11px var(--sans)',
  })
  const linea: React.CSSProperties = { font: '500 11px var(--sans)', color: 'var(--t2)', flexBasis: '100%' }
  const pendientes = cuenta?.pendientes ?? null

  return (
    <div style={{ marginBottom: 12, borderRadius: 11, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <button onClick={() => setAbierto(!abierto)}
        style={{ width: '100%', textAlign: 'left', padding: '9px 13px', border: 0, background: 'none', cursor: 'pointer', font: '600 11px var(--sans)', color: 'var(--t2)' }}>
        {abierto ? '▾' : '▸'} Jev · probar la clave y re-etiquetar los fallos que quedaron sin etiqueta
        {!admin && <span style={{ color: 'var(--t3)' }}> (modo administrador 🔑)</span>}
      </button>
      {abierto && (
        <div style={{ padding: '0 13px 12px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>
            Jev etiqueta de qué fue cada fallo de un veredicto y revisa la coherencia de los partes. Si responde con error
            (sin crédito, clave mala), el veredicto se guarda igual pero sin etiqueta: estos tres pasos lo arreglan.
          </div>

          {/* 1 · la clave */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', minWidth: 18 }}>1</span>
            <button onClick={probar} disabled={yendo !== ''} style={boton(yendo === '')}>
              {yendo === 'ping' ? 'Probando…' : 'Probar la clave'}
            </button>
            {ping && (
              <span style={{ font: '600 11px var(--sans)', color: ping.ok ? 'var(--up)' : 'var(--down)' }}>
                {ping.ok
                  ? `funciona · ${ping.modelo ?? 'modelo ?'} · ${ping.oficial ? 'API oficial' : `intermediario (${ping.via})`}${ping.ms ? ` · ${ping.ms} ms` : ''}`
                  : `no funciona: ${ping.error ?? 'sin detalle'}`}
              </span>
            )}
          </div>

          {/* 2 · contar */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', minWidth: 18 }}>2</span>
            <button onClick={contar} disabled={yendo !== ''} style={boton(yendo === '')}>
              {yendo === 'contar' ? 'Contando…' : 'Contar los sin etiqueta'}
            </button>
            {pendientes !== null && (
              <span style={{ font: '600 11px var(--sans)', color: 'var(--t1)' }}>
                <span style={{ fontVariantNumeric: 'tabular-nums' }}>{pendientes}</span> veredicto{pendientes === 1 ? '' : 's'} con el sello de Jev en error
              </span>
            )}
            {cuenta && Object.keys(cuenta.erroresSellados).length > 0 && !ultimo && (
              <span style={linea}>
                {Object.entries(cuenta.erroresSellados).map(([e, n]) => `${n} × ${e}`).join(' · ')}
              </span>
            )}
          </div>

          {/* 3 · re-etiquetar, por tandas */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', minWidth: 18 }}>3</span>
            <button onClick={aplicar} disabled={yendo !== '' || pendientes === 0}
              style={boton(yendo === '' && pendientes !== 0)}
              title={`de a ${TANDA} por vez: cada uno es una pregunta a Jev`}>
              {yendo === 'aplicar' ? `Re-etiquetando (hasta ${TANDA})…` : hechos > 0 ? `Seguir: ${TANDA} más` : `Re-etiquetar (de a ${TANDA})`}
            </button>
            {hechos > 0 && (
              <span style={{ font: '600 11px var(--sans)', color: 'var(--up)' }}>
                <span style={{ fontVariantNumeric: 'tabular-nums' }}>{hechos}</span> re-etiquetado{hechos === 1 ? '' : 's'}
                {pendientes !== null && <> · quedan <span style={{ fontVariantNumeric: 'tabular-nums' }}>{pendientes}</span></>}
              </span>
            )}
            {ultimo?.cortadoPor && (
              <span style={{ ...linea, color: 'var(--down)' }}>se detuvo: {ultimo.cortadoPor}</span>
            )}
            {ultimo && ultimo.sinCambio.length > 0 && (
              <span style={linea}>{ultimo.sinCambio.length} quedaron igual (Jev respondió simulado)</span>
            )}
          </div>

          {error && <div style={{ font: '600 11px var(--sans)', color: 'var(--down)' }}>{error}</div>}
        </div>
      )}
    </div>
  )
}
