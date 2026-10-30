// Goles acotados (REVENTON §17): el intervalo de goles de cada lado y el
// marcador acotado, tal como llegan del backend (backend/analisis/goles.py).
// La pantalla no calcula nada. Es lectura del marcador, no señal de apuesta:
// contra el mercado de goles no hay ventaja, y se dice.
import type { GolesAcotadosDTO, GolesAcotadosEquipoDTO, GolesLadoDTO, IntervaloGolesDTO } from '../api/types'

const pct = (x: number | undefined | null) => (x == null ? '—' : `${Math.round(100 * x)} %`)
const rango = (i: IntervaloGolesDTO) => (i.desde === i.hasta ? `${i.desde}` : `${i.desde}-${i.hasta}`)

function Fila({ etiqueta, l }: { etiqueta: string; l: GolesLadoDTO }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) auto', gap: '2px 10px', alignItems: 'baseline' }}>
      <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', minWidth: 0, overflowWrap: 'anywhere' }}>{etiqueta}</span>
      <span style={{ font: '700 12px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
        {rango(l.intervalo)} <span style={{ color: 'var(--t3)', fontWeight: 500 }}>({pct(l.intervalo.prob)})</span>
      </span>
      <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
        esperados {l.esperados.toFixed(2)} · 0: {pct(l.distribucion['0'])} · 3+: {pct(l.distribucion['3+'])}
      </span>
      <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }} title="el intervalo de tres goles: más ancho, más seguro">
        {rango(l.intervaloAmplio)} ({pct(l.intervaloAmplio.prob)})
      </span>
    </div>
  )
}

function Pie({ g }: { g: GolesAcotadosDTO | GolesAcotadosEquipoDTO }) {
  const m = g.modelo
  return (
    <>
      {g.marcadorAcotado && (
        <div style={{ font: '600 11px var(--sans)', color: 'var(--t2)' }}>
          Marcador acotado: <b style={{ font: '700 11.5px var(--mono)', color: 'var(--t1)' }}>{g.marcadorAcotado.marcadores.join(' · ')}</b>{' '}
          <span style={{ color: 'var(--t3)' }}>({pct(g.marcadorAcotado.prob)})</span>
        </div>
      )}
      {g.masProbables && (
        <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums', overflowWrap: 'anywhere' }}>
          más probables: {g.masProbables.map((x) => `${x.marcador} ${pct(x.prob)}`).join(' · ')} · más de 2,5: {pct(g.masDe2_5)} · ambos marcan: {pct(g.ambosMarcan)}
        </div>
      )}
      <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)', lineHeight: 1.45 }}>
        {m?.intervaloAcierta != null && <>Medido en el padrón: el intervalo acertó {pct(m.intervaloAcierta)} y el marcador acotado {pct(m.marcadorAcotadoAcierta)}. </>}
        Lectura del marcador, no señal de apuesta: contra el mercado de goles no hay ventaja.
      </div>
    </>
  )
}

const caja: React.CSSProperties = { display: 'flex', flexDirection: 'column', gap: 6, padding: '9px 11px', borderRadius: 9, background: 'var(--bg2)', border: '1px solid var(--line)', minWidth: 0 }
const titulo: React.CSSProperties = { font: '700 9.5px var(--mono)', color: 'var(--accent)', letterSpacing: '.5px', textTransform: 'uppercase' }

/** En la tarjeta de burbujas: cuánto mete y cuánto recibe contra su próximo rival. */
export function GolesAcotadosEquipo({ g, equipo }: { g: GolesAcotadosEquipoDTO; equipo: string }) {
  if (g.sinDato || !g.mete || !g.recibe) return null
  return (
    <div style={caja}>
      <div style={titulo}>Goles acotados · contra {g.recibe.equipo}</div>
      <Fila etiqueta={`${equipo} mete`} l={g.mete} />
      <Fila etiqueta={`${equipo} recibe`} l={g.recibe} />
      <Pie g={g} />
    </div>
  )
}

/** En la lectura del parte: los dos lados y el marcador acotado. */
export function GolesAcotadosPartido({ g }: { g: GolesAcotadosDTO }) {
  if (g.sinDato || !g.local || !g.visita) return null
  return (
    <section style={{ ...caja, padding: '13px 16px', borderRadius: 14 }}>
      <div style={titulo}>Goles acotados · calculado al leer · intervalo de dos goles (y de tres)</div>
      <Fila etiqueta={`${g.local.equipo} mete`} l={g.local} />
      <Fila etiqueta={`${g.visita.equipo} mete`} l={g.visita} />
      <Pie g={g} />
    </section>
  )
}
