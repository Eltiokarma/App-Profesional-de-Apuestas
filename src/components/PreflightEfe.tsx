import type { OrigenDato, PreflightEfeDTO } from '../api/types'

// El chequeo previo del EFE: qué datos hay cargados y qué va a costar la
// corrida, ANTES de pulsar el botón. El candado de análisis frío ya evitaba la
// catástrofe (>6 faltantes); esto cubre el caso intermedio —4 faltantes son 11
// búsquedas y ~medio dólar— que hasta ahora se descubría con la factura.
//
// Regla de la pantalla: cada casilla dice de DÓNDE sale el dato, no si "está
// bien". Un rojo aquí no es un error: es una búsqueda web que se va a pagar.

const ORIGEN: Record<OrigenDato, { label: string; color: string; soft: string }> = {
  local: { label: 'base', color: 'var(--up)', soft: 'var(--up-soft)' },
  despensa: { label: 'despensa', color: 'var(--up)', soft: 'var(--up-soft)' },
  anejo: { label: 'añejo', color: 'var(--mark)', soft: 'var(--mark-soft)' },
  api: { label: 'API', color: 'var(--accent)', soft: 'color-mix(in oklch, var(--accent), transparent 88%)' },
  falta: { label: 'web $', color: 'var(--down)', soft: 'var(--down-soft)' },
}

// nombres legibles de los siete tipos del protocolo
const TIPO_LABEL: Record<string, string> = {
  dt: 'DT',
  plantel: 'Plantel',
  tabla: 'Tabla',
  resultados: 'Resultados',
  fixture: 'Calendario',
  xi_reciente: 'XI',
  bajas: 'Bajas',
}

const NIVEL = {
  caliente: { color: 'var(--up)', soft: 'var(--up-soft)', label: 'TODO CARGADO' },
  tibio: { color: 'var(--mark)', soft: 'var(--mark-soft)', label: 'FALTAN DATOS' },
  frio: { color: 'var(--down)', soft: 'var(--down-soft)', label: 'ANÁLISIS FRÍO' },
} as const

function dinero(n: number): string {
  return n < 0.01 ? '$0.00' : `$${n.toFixed(2)}`
}

export function PreflightEfe({ pf, onRecargar }: {
  pf: PreflightEfeDTO
  onRecargar?: () => void
}) {
  const n = NIVEL[pf.nivel]
  const gasto = pf.gasto
  const rango = pf.costo.max > pf.costo.min
    ? `${dinero(pf.costo.min)}–${dinero(pf.costo.max)}`
    : dinero(pf.costo.min)

  const titular = pf.demo
    ? 'Modo demo: el análisis es de muestra y no gasta nada'
    : pf.faltantes === 0
      ? 'Nada que buscar en la web: la corrida más barata posible'
      : `Va a buscar ${pf.faltantes} dato${pf.faltantes === 1 ? '' : 's'} en la web · ${pf.busquedasPrevistas} búsqueda${pf.busquedasPrevistas === 1 ? '' : 's'}`

  return (
    <section style={{ marginBottom: 14, borderRadius: 12, background: 'var(--bg2)', border: `1px solid color-mix(in oklch, ${n.color}, transparent 65%)`, overflow: 'hidden' }}>
      {/* cabecera: semáforo + veredicto + precio */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', background: n.soft, flexWrap: 'wrap' }}>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: 'var(--bg)', color: n.color, font: '700 9.5px var(--mono)', letterSpacing: '.4px', flexShrink: 0 }}>
          {n.label}
        </span>
        <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 180 }}>{titular}</span>
        {!pf.demo && (
          <span style={{ display: 'flex', alignItems: 'baseline', gap: 6, flexShrink: 0 }}>
            <span style={{ font: '800 14px var(--mono)', color: n.color, fontVariantNumeric: 'tabular-nums' }}>{rango}</span>
            <span
              title={pf.costo.medido
                ? `Rango de ${pf.costo.muestra} corridas reales de tamaño parecido`
                : 'Estimación por fórmula: todavía no hay corridas medidas de este tamaño'}
              style={{ font: '600 9px var(--mono)', color: pf.costo.medido ? 'var(--up)' : 'var(--t3)', letterSpacing: '.3px' }}
            >
              {pf.costo.medido ? `MEDIDO ×${pf.costo.muestra}` : 'ESTIMADO'}
            </span>
          </span>
        )}
        {onRecargar && (
          <button onClick={onRecargar} title="Volver a comprobar (no gasta nada)" style={{ display: 'flex', alignItems: 'center', padding: 5, borderRadius: 7, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t2)', cursor: 'pointer', flexShrink: 0 }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 11-2.64-6.36M21 3v6h-6" /></svg>
          </button>
        )}
      </div>

      <div style={{ padding: '12px 14px' }}>
        {/* una fila por equipo con sus siete casillas */}
        <div style={{ display: 'grid', gap: 10 }}>
          {pf.equipos.map((eq) => (
            <div key={eq.equipo}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 5 }}>
                <span style={{ font: '700 11.5px var(--sans)', color: 'var(--t1)' }}>{eq.equipo}</span>
                {!eq.enDespensa && !pf.demo && (
                  <span title="No hay ningún dato guardado bajo este nombre exacto" style={{ padding: '1px 7px', borderRadius: 5, background: 'var(--mark-soft)', color: 'var(--mark)', font: '600 9px var(--mono)' }}>
                    sin despensa
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
                {eq.datos.map((d) => {
                  const o = ORIGEN[d.origen]
                  return (
                    <span
                      key={d.tipo}
                      title={`${d.tipo}: ${d.detalle}`}
                      style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '4px 8px', borderRadius: 7, background: o.soft, border: `1px solid color-mix(in oklch, ${o.color}, transparent 70%)` }}
                    >
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: o.color, flexShrink: 0 }}></span>
                      <span style={{ font: '600 10px var(--sans)', color: 'var(--t1)' }}>{TIPO_LABEL[d.tipo] ?? d.tipo}</span>
                      <span style={{ font: '600 9px var(--mono)', color: o.color }}>
                        {o.label}{d.origen === 'anejo' && d.edadDias ? ` ${d.edadDias}d` : ''}
                      </span>
                    </span>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        {/* leyenda: sin esto, los colores son adorno */}
        {!pf.demo && (
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 11, paddingTop: 9, borderTop: '1px solid var(--line)' }}>
            {([
              ['base', 'var(--up)', 'de sad.db o la capa de jugadores — gratis'],
              ['despensa', 'var(--up)', 'investigado antes y todavía fresco'],
              ['añejo', 'var(--mark)', 'vencido pero servible: se usa declarando su edad'],
              ['API', 'var(--accent)', 'API-Football al generar: cuota del plan, no dólares'],
              ['web $', 'var(--down)', 'no lo tenemos: búsqueda web — esto es lo que cuesta'],
            ] as [string, string, string][]).map(([label, color, ayuda]) => (
              <span key={label} title={ayuda} style={{ display: 'flex', alignItems: 'center', gap: 5, font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: color }}></span>{label}
              </span>
            ))}
          </div>
        )}

        {/* GASTO REAL: lo de arriba es una estimación y se puede equivocar
            (se equivocó); esto es el cargo que existió. El desglose
            json/pensamiento es lo que dice dónde se va el dinero cuando no hay
            ni una búsqueda web. */}
        {gasto && gasto.corridas > 0 && (
          <div style={{ marginTop: 11, paddingTop: 10, borderTop: '1px solid var(--line)' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>
              <span style={{ font: '700 11px var(--sans)', color: 'var(--t1)' }}>Ya gastado en este partido</span>
              <span style={{ font: '800 13px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
                {dinero(gasto.total)}
              </span>
              <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>
                {gasto.corridas} corrida{gasto.corridas === 1 ? '' : 's'} ·{' '}
                {gasto.porTipo.map((t) => `${t.tipo} ${dinero(t.costo)}${t.corridas > 1 ? ` ×${t.corridas}` : ''}`).join(' · ')}
              </span>
            </div>
            <div style={{ display: 'grid', gap: 3 }}>
              {gasto.ultimas.map((c, i) => {
                const pens = c.tokensPensamiento ?? 0
                const json = c.tokensJson ?? 0
                const out = c.tokensOut || pens + json || 1
                const pctPens = Math.round((pens / out) * 100)
                return (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, font: '500 9.5px var(--mono)', color: 'var(--t2)', flexWrap: 'wrap' }}>
                    <span style={{ minWidth: 54, color: 'var(--t1)', fontWeight: 700 }}>{c.tipo}</span>
                    <span style={{ minWidth: 46, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{dinero(c.costo)}</span>
                    <span style={{ color: 'var(--t3)' }}>
                      {(c.busquedas ?? 0) > 0 ? `${c.busquedas} búsq · ` : 'sin búsquedas · '}
                      out {out.toLocaleString('es')}
                    </span>
                    {/* barra: cuánto del output fue razonamiento y cuánto JSON */}
                    <span title={`razonamiento ${pens.toLocaleString('es')} · JSON ${json.toLocaleString('es')}`}
                      style={{ display: 'flex', width: 90, height: 6, borderRadius: 3, overflow: 'hidden', background: 'var(--bg3)' }}>
                      <span style={{ width: `${pctPens}%`, background: 'var(--mark)' }}></span>
                      <span style={{ flex: 1, background: 'var(--accent)' }}></span>
                    </span>
                    <span style={{ color: 'var(--t3)' }}>{pctPens}% razonamiento</span>
                  </div>
                )
              })}
            </div>
            <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)', marginTop: 5 }}>
              El razonamiento se cobra a precio de salida igual que el JSON. Si esa barra
              va casi toda ámbar, el gasto no está en lo que se escribe sino en lo que se
              piensa: se baja con <b>SAD_EFE_EFFORT</b>, no con más despensa.
            </div>
          </div>
        )}

        {/* qué hacer para que salga más barato */}
        {pf.recomendaciones.length > 0 && (
          <ul style={{ margin: '10px 0 0', paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
            {pf.recomendaciones.map((r, i) => (
              <li key={i} style={{ font: '500 11px var(--sans)', color: 'var(--t2)', lineHeight: 1.5 }}>{r}</li>
            ))}
          </ul>
        )}

        {pf.bloqueado && (
          <p style={{ margin: '10px 0 0', font: '600 11px var(--sans)', color: 'var(--down)' }}>
            Con {pf.faltantes} faltantes (umbral {pf.umbralFrio}) el backend va a bloquear el análisis
            antes de gastar: hace falta «Generar igual (frío)» para pagarlo.
          </p>
        )}
      </div>
    </section>
  )
}
