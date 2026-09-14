import { useEffect, useState } from 'react'
import { CONFIG } from '../config'
import { SadApi } from '../api/sad'
import type { LatidoCoworkDTO } from '../api/types'

/** ¿Está corriendo el pipeline, o lleva dos días muerto y nadie se enteró?
 *
 *  Una tubería automática sin vigilancia no falla con ruido: falla callada, y
 *  se descubre semanas después cuando alguien va a mirar una métrica y no hay
 *  casos. Por eso esto vive en la pantalla donde uno aterriza y no en una
 *  pestaña que hay que ir a buscar.
 *
 *  Y por eso mismo **es invisible cuando todo está bien**: un aviso que sale
 *  siempre se deja de leer a la semana. Solo aparece cuando hay algo que
 *  hacer.
 */
export function LatidoCowork({ isMobile }: { isMobile: boolean }) {
  const [d, setD] = useState<LatidoCoworkDTO | null>(null)
  useEffect(() => {
    if (CONFIG.dataSource !== 'http') return
    let vivo = true
    SadApi.coworkLatido().then((x: LatidoCoworkDTO) => { if (vivo) setD(x) }).catch(() => { /* el latido no rompe la pantalla */ })
    return () => { vivo = false }
  }, [])
  if (!d || d.estado === 'verde') return null

  const rojo = d.estado === 'rojo'
  const color = rojo ? 'var(--down)' : 'var(--mark)'
  const fondo = rojo ? 'var(--down-soft)' : 'var(--mark-soft)'
  const faltaron = d.coberturaDeAyer?.faltaron ?? []
  return (
    <section style={{
      padding: isMobile ? '11px 13px' : '13px 16px', marginBottom: 14, borderRadius: 13,
      background: fondo, border: `1px solid color-mix(in oklch,${color},transparent 55%)`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap', marginBottom: 6 }}>
        <span style={{ font: '700 9.5px var(--mono)', color, letterSpacing: '.6px' }}>
          {rojo ? '⚠️ EL PIPELINE NO ESTÁ CORRIENDO' : 'PIPELINE CON PENDIENTES'}
        </span>
        {d.horasDesdeElUltimo !== null && d.horasDesdeElUltimo !== undefined && (
          <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)' }}>
            último parte hace {d.horasDesdeElUltimo} h
          </span>
        )}
        <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t3)' }}>
          {d.depositadosEnLaVentana} en {d.ventanaHoras} h
        </span>
      </div>
      {d.porque.map((x, i) => (
        <div key={i} style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', paddingLeft: 10, borderLeft: `2px solid ${color}`, marginBottom: 3 }}>{x}</div>
      ))}
      {faltaron.length > 0 && (
        <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t2)', marginTop: 6 }}>
          Sin parte: {faltaron.slice(0, 4).map((f) => f.partido || f.fixtureId).join(' · ')}
          {faltaron.length > 4 && ` y ${faltaron.length - 4} más`}
        </div>
      )}
      {(d.veredictosVencidos ?? []).length > 0 && (
        <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t2)', marginTop: 4 }}>
          Esperan veredicto: {d.veredictosVencidos.map((v) => `${v.partido} (${v.marcador})`).join(' · ')}
        </div>
      )}
    </section>
  )
}
