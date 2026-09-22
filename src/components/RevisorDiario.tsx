import { useEffect, useState } from 'react'
import { CONFIG } from '../config'
import { SadApi } from '../api/sad'
import type { RevisorDiarioDTO } from '../api/types'

/** El reporte del día del revisor de coherencia (Jev, docs/JEV.md).
 *
 *  Para quien deja a Cowork solo y mira al final del día: qué encontró el
 *  revisor, qué hizo Cowork con eso y cuánto costó. Solo se pinta cuando hubo
 *  evaluaciones reales en la ventana: sin clave de Jev, o sin depósitos, no
 *  ocupa lugar. Lo que pide atención va primero (sin reacción · sostuvo). */
const REACCION: Record<RevisorDiarioDTO['partes'][number]['reaccion'], { texto: string; color: string }> = {
  sinReaccion: { texto: 'sin reacción', color: 'var(--down)' },
  sostuvo: { texto: 'sostuvo', color: 'var(--mark)' },
  corrigioParte: { texto: 'corrigió en parte', color: 'var(--mark)' },
  corrigio: { texto: 'corrigió', color: 'var(--up)' },
  limpio: { texto: 'limpio', color: 'var(--t3)' },
  noEvaluado: { texto: 'no evaluado', color: 'var(--t3)' },
}

export function RevisorDiario({ isMobile }: { isMobile: boolean }) {
  const [d, setD] = useState<RevisorDiarioDTO | null>(null)
  const [abierto, setAbierto] = useState(false)
  useEffect(() => {
    if (CONFIG.dataSource !== 'http') return
    let vivo = true
    SadApi.coworkRevisor().then((x: RevisorDiarioDTO) => { if (vivo) setD(x) }).catch(() => { /* el reporte no rompe la pantalla */ })
    return () => { vivo = false }
  }, [])
  if (!d || d.modo === 'off' || d.totales.partesEvaluados === 0) return null

  const t = d.totales
  const pendientes = t.sinReaccion + t.sostuvo
  const color = pendientes ? 'var(--mark)' : 'var(--up)'
  const conHallazgos = d.partes.filter((p) => p.reaccion !== 'limpio' && p.reaccion !== 'noEvaluado')
  return (
    <section style={{ padding: isMobile ? '11px 13px' : '13px 16px', marginBottom: 14, borderRadius: 13, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px 10px', flexWrap: 'wrap' }}>
        <span style={{ font: '700 9.5px var(--mono)', color, letterSpacing: '.6px' }}>
          REVISOR · ÚLTIMAS {d.ventana.horas ?? 24} H{d.modo === 'sombra' ? ' · EN SOMBRA' : ''}
        </span>
        <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          {t.partesEvaluados} partes · {t.conHallazgos} con hallazgos
        </span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
          corrigió {t.corrigio + t.corrigioParte} · sostuvo {t.sostuvo} · sin reacción {t.sinReaccion}
        </span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
          ${t.costoUsd.toFixed(4)}{t.errores ? ` · ${t.errores} errores` : ''}
        </span>
        {conHallazgos.length > 0 && (
          <button onClick={() => setAbierto((v) => !v)} style={{ marginLeft: 'auto', padding: '3px 9px', border: '1px solid var(--line)', borderRadius: 7, background: 'var(--bg)', color: 'var(--t2)', font: '600 10px var(--sans)', cursor: 'pointer' }}>
            {abierto ? 'ocultar' : 'ver partes'}
          </button>
        )}
      </div>
      {abierto && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr)', gap: 5, marginTop: 8 }}>
          {conHallazgos.map((p) => (
            <div key={p.fixtureId} style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', gap: '3px 8px', font: '500 11px var(--sans)', color: 'var(--t1)', minWidth: 0 }}>
              <span style={{ font: '700 9px var(--mono)', color: REACCION[p.reaccion].color, flexShrink: 0 }}>{REACCION[p.reaccion].texto.toUpperCase()}</span>
              <span style={{ minWidth: 0, overflowWrap: 'anywhere' }}>{p.partido}</span>
              <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', overflowWrap: 'anywhere' }}>
                {p.hallazgosEncontrados.join(' · ')}{p.hallazgosAhora.length === 0 && p.hallazgosEncontrados.length > 0 ? ' → limpio' : ''}
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
