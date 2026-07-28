// Alineaciones confirmadas del partido — la ingesta en vivo las captura sola
// (~1 h antes del saque, backend/ingesta/en_vivo.py) y aquí se muestran en
// cuanto existen. Es el MISMO dato que reciben el EFE/DTP y los skills vía
// /fixtures/{id}/ficha: si esta tarjeta muestra el XI, el análisis ya puede
// completarse con la alineación real — regenerarlo con su botón de recarga.
// Regla "real o nada": sin XI publicado se dice eso, no se inventa un once.
//
// Vista Cancha: la posición sale del `grid` real de la API ("fila:columna");
// sin grid se reparte por la formación y se marca como aproximada. Las bandas
// punteadas son los mismos carriles (izquierda/centro/derecha) que usa el
// mapa de duelos del DTP — la cancha y el M2 hablan el mismo idioma, pero la
// pizarra del DTP no se toca: su contrato es texto por carril.
import { useState } from 'react'
import type { AlineacionDTO, EventoPartidoDTO, JugadorAlineadoDTO } from '../api/types'

const POS_LABEL: Record<string, string> = { G: 'POR', D: 'DEF', M: 'MED', F: 'DEL' }

interface CambioXi {
  minuto: number
  saleId: number
  saleNombre: string
  entraId: number
  entraNombre: string
}

/** Sustituciones de un equipo a partir de los eventos de la ficha (los mismos
 *  que captura el ciclo en vivo). La API no siempre respeta quién viaja como
 *  jugador y quién como asistente en un cambio, así que aquí decide la
 *  membresía: el que ESTÁ en cancha sale, el otro entra — y el once en cancha
 *  se va actualizando para que las ventanas encadenadas (entra y luego sale)
 *  también cuadren. */
function cambiosDelLado(ali: AlineacionDTO, eventos: EventoPartidoDTO[]): CambioXi[] {
  const enCancha = new Set(ali.titulares.map((j) => j.jugadorId))
  const subs = eventos
    .filter((e) => e.equipoId === ali.equipoId && (e.tipo ?? '').toLowerCase().startsWith('subst'))
    .sort((a, b) => a.minuto - b.minuto)
  const cambios: CambioXi[] = []
  for (const e of subs) {
    if (e.jugadorId == null || e.asistenteId == null) continue
    const primeroSale = enCancha.has(e.jugadorId)
    if (!primeroSale && !enCancha.has(e.asistenteId)) continue // ninguno en cancha: dato roto
    const sale = primeroSale
      ? { id: e.jugadorId, nombre: e.jugador }
      : { id: e.asistenteId, nombre: e.asistente }
    const entra = primeroSale
      ? { id: e.asistenteId, nombre: e.asistente }
      : { id: e.jugadorId, nombre: e.jugador }
    enCancha.delete(sale.id)
    enCancha.add(entra.id)
    cambios.push({ minuto: e.minuto, saleId: sale.id, saleNombre: sale.nombre ?? '—', entraId: entra.id, entraNombre: entra.nombre ?? '—' })
  }
  return cambios
}

/** Quién ocupa HOY el puesto de cada titular original: con los cambios
 *  aplicados en orden, cada sustitución hereda el punto del jugador al que
 *  reemplazó (también en cadenas: entró y después salió). */
function ocupantes(ali: AlineacionDTO, cambios: CambioXi[]): Map<number, { id: number; nombre: string; minuto: number }> {
  const porPuesto = new Map<number, { id: number; nombre: string; minuto: number }>()
  for (const c of cambios) {
    const puesto = ali.titulares.find((t) => (porPuesto.get(t.jugadorId)?.id ?? t.jugadorId) === c.saleId)
    if (puesto) porPuesto.set(puesto.jugadorId, { id: c.entraId, nombre: c.entraNombre, minuto: c.minuto })
  }
  return porPuesto
}

function apellido(nombre: string | null | undefined): string {
  if (!nombre) return '—'
  const partes = nombre.trim().split(/\s+/)
  return partes.length > 1 ? partes.slice(1).join(' ') : partes[0]
}

interface PuntoXi {
  key: number
  x: number
  y: number
  numero: string
  nombre: string
  apellido: string
}

/** Puntos (x, y en %) de un XI sobre la cancha horizontal. Con `grid` de la
 *  API la posición es real (fila = línea desde el arquero, columna = de
 *  izquierda a derecha DEL EQUIPO); sin él se reparte por la formación y la
 *  vista queda marcada como aproximada. La visita se espeja entera. */
function puntosXi(ali: AlineacionDTO, lado: 'local' | 'visita'): { puntos: PuntoXi[]; exacta: boolean } {
  const espejo = (p: { x: number; y: number }) => (lado === 'local' ? p : { x: 100 - p.x, y: 100 - p.y })
  const punto = (j: JugadorAlineadoDTO, x: number, y: number): PuntoXi => {
    const p = espejo({ x, y })
    return { key: j.jugadorId, x: p.x, y: p.y, numero: j.numero != null ? String(j.numero) : '–', nombre: j.nombre ?? '—', apellido: apellido(j.nombre) }
  }

  const conGrid = ali.titulares.filter((j) => j.grid && /^\d+:\d+$/.test(j.grid))
  if (conGrid.length > 0 && conGrid.length === ali.titulares.length) {
    const porFila = new Map<number, { col: number; j: JugadorAlineadoDTO }[]>()
    for (const j of conGrid) {
      const [f, c] = (j.grid as string).split(':').map(Number)
      if (!porFila.has(f)) porFila.set(f, [])
      porFila.get(f)!.push({ col: c, j })
    }
    const filas = [...porFila.keys()].sort((a, b) => a - b)
    const maxFila = filas[filas.length - 1]
    const puntos: PuntoXi[] = []
    for (const f of filas) {
      const linea = porFila.get(f)!.sort((a, b) => a.col - b.col)
      const x = f === 1 ? 5.5 : 14 + ((f - 2) * 32) / Math.max(maxFila - 2, 1)
      linea.forEach(({ j }, i) => puntos.push(punto(j, x, 11 + ((i + 0.5) * 78) / linea.length)))
    }
    return { puntos, exacta: true }
  }

  // fallback sin grid (o con grid a medias): arquero al arco y el resto en
  // las líneas de la formación, ordenado defensa → ataque por posición
  const gi = ali.titulares.findIndex((j) => j.posicion === 'G')
  const gk = ali.titulares[gi >= 0 ? gi : 0]
  const resto = ali.titulares.filter((j) => j !== gk)
  const peso: Record<string, number> = { D: 0, M: 1, F: 2 }
  resto.sort((a, b) => (peso[a.posicion ?? ''] ?? 1) - (peso[b.posicion ?? ''] ?? 1))
  let lineas = (ali.formacion ?? '').split('-').map(Number).filter((n) => Number.isFinite(n) && n > 0)
  if (lineas.reduce((s, n) => s + n, 0) !== resto.length) {
    const nD = resto.filter((j) => j.posicion === 'D').length
    const nM = resto.filter((j) => j.posicion === 'M').length
    lineas = [nD, nM, resto.length - nD - nM].filter((n) => n > 0)
  }
  const puntos: PuntoXi[] = []
  if (gk) puntos.push(punto(gk, 5.5, 50))
  let i = 0
  lineas.forEach((k, li) => {
    const x = lineas.length > 1 ? 14 + (li * 32) / (lineas.length - 1) : 30
    for (let c = 0; c < k; c++) {
      const j = resto[i++]
      if (j) puntos.push(punto(j, x, 11 + ((c + 0.5) * 78) / k))
    }
  })
  return { puntos, exacta: false }
}

function EncabezadoEquipo({ ali, nombre, color, alDerecha }: { ali: AlineacionDTO; nombre: string; color: string; alDerecha?: boolean }) {
  const piezas = [
    <span key="p" style={{ width: 10, height: 10, borderRadius: 3, background: color, display: 'inline-block', flexShrink: 0 }}></span>,
    <span key="n" style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)' }}>{nombre}</span>,
    ali.formacion ? (
      <span key="f" style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--accent-soft)', color: 'var(--accent)', font: '700 10px var(--mono)', letterSpacing: '.3px' }}>{ali.formacion}</span>
    ) : null,
    ali.entrenador ? <span key="d" style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>DT {ali.entrenador}</span> : null,
  ].filter(Boolean)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 9, minWidth: 0, flexWrap: 'wrap', justifyContent: alDerecha ? 'flex-end' : 'flex-start' }}>
      {alDerecha ? piezas.reverse() : piezas}
    </div>
  )
}

function CanchaXi({ local, visitante, localNombre, visitanteNombre, eventos, isMobile }: { local?: AlineacionDTO | null; visitante?: AlineacionDTO | null; localNombre: string; visitanteNombre: string; eventos: EventoPartidoDTO[]; isMobile: boolean }) {
  const lados = [
    local && local.titulares.length > 0 ? { ali: local, lado: 'local' as const, color: 'var(--accent)', nombre: localNombre } : null,
    visitante && visitante.titulares.length > 0 ? { ali: visitante, lado: 'visita' as const, color: 'var(--down)', nombre: visitanteNombre } : null,
  ].filter((l): l is NonNullable<typeof l> => l !== null)
  const calculados = lados.map((l) => {
    const cambios = cambiosDelLado(l.ali, eventos)
    return { ...l, ...puntosXi(l.ali, l.lado), cambios, porPuesto: ocupantes(l.ali, cambios) }
  })
  const aproximada = calculados.some((l) => !l.exacta)
  const hayCambios = calculados.some((l) => l.cambios.length > 0)
  const linea = 'var(--line2)'
  const dCirculo = isMobile ? 24 : 32

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 10, flexWrap: 'wrap' }}>
        {calculados.map((l) => (
          <EncabezadoEquipo key={l.lado} ali={l.ali} nombre={l.nombre} color={l.color} alDerecha={l.lado === 'visita'} />
        ))}
      </div>

      <div style={{ position: 'relative', width: '100%', aspectRatio: '16 / 9.2', borderRadius: 12, border: '1px solid var(--line)', background: 'var(--bg)', overflow: 'hidden' }}>
        {/* carriles: el mismo idioma (izquierda/centro/derecha) que el M2 del DTP */}
        <div style={{ position: 'absolute', left: 0, right: 0, top: '33.33%', borderTop: `1px dashed ${linea}` }}></div>
        <div style={{ position: 'absolute', left: 0, right: 0, top: '66.66%', borderTop: `1px dashed ${linea}` }}></div>
        <div style={{ position: 'absolute', left: 8, top: 6, font: '600 8.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>IZQ</div>
        <div style={{ position: 'absolute', left: 8, top: '35%', font: '600 8.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>CENTRO</div>
        <div style={{ position: 'absolute', left: 8, top: '68%', font: '600 8.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>DER</div>

        {/* rayado de la cancha */}
        <div style={{ position: 'absolute', inset: '3.2% 2.2%', border: `1.5px solid ${linea}`, borderRadius: 4 }}></div>
        <div style={{ position: 'absolute', top: '3.2%', bottom: '3.2%', left: '50%', width: 1.5, background: linea }}></div>
        <div style={{ position: 'absolute', left: '50%', top: '50%', width: '15%', aspectRatio: '1', transform: 'translate(-50%, -50%)', border: `1.5px solid ${linea}`, borderRadius: '50%' }}></div>
        <div style={{ position: 'absolute', left: '50%', top: '50%', width: 7, height: 7, transform: 'translate(-50%, -50%)', borderRadius: '50%', background: linea }}></div>
        <div style={{ position: 'absolute', left: '2.2%', top: '21%', bottom: '21%', width: '15%', border: `1.5px solid ${linea}`, borderLeft: 'none' }}></div>
        <div style={{ position: 'absolute', left: '2.2%', top: '35%', bottom: '35%', width: '6%', border: `1.5px solid ${linea}`, borderLeft: 'none' }}></div>
        <div style={{ position: 'absolute', right: '2.2%', top: '21%', bottom: '21%', width: '15%', border: `1.5px solid ${linea}`, borderRight: 'none' }}></div>
        <div style={{ position: 'absolute', right: '2.2%', top: '35%', bottom: '35%', width: '6%', border: `1.5px solid ${linea}`, borderRight: 'none' }}></div>
        <div style={{ position: 'absolute', left: 0, top: '44%', bottom: '44%', width: '2.2%', background: 'color-mix(in oklch, var(--accent), transparent 82%)', borderRadius: '3px 0 0 3px' }}></div>
        <div style={{ position: 'absolute', right: 0, top: '44%', bottom: '44%', width: '2.2%', background: 'color-mix(in oklch, var(--down), transparent 82%)', borderRadius: '0 3px 3px 0' }}></div>

        {calculados.map((l) =>
          l.puntos.map((p) => {
            // si a este puesto ya le entró un cambio, en la cancha está el que
            // juega AHORA — el titular original queda en el tooltip y en la
            // tira de cambios de abajo
            const occ = l.porPuesto.get(p.key)
            const suplente = occ ? l.ali.suplentes.find((j) => j.jugadorId === occ.id) : undefined
            const numero = occ ? (suplente?.numero != null ? String(suplente.numero) : '–') : p.numero
            const nombre = occ ? apellido(suplente?.nombre ?? occ.nombre) : p.apellido
            const titulo = occ ? `${numero} · ${suplente?.nombre ?? occ.nombre} · entró al ${occ.minuto}' por ${p.nombre}` : `${p.numero} · ${p.nombre}`
            return (
              <div key={`${l.lado}-${p.key}`} title={titulo} style={{ position: 'absolute', left: `${p.x}%`, top: `${p.y}%`, transform: 'translate(-50%, -50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', animation: 'sadup .35s ease both' }}>
                <div style={{ position: 'relative', width: dCirculo, height: dCirculo }}>
                  <div style={{ width: dCirculo, height: dCirculo, borderRadius: '50%', background: l.color, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `700 ${isMobile ? 10.5 : 12}px var(--mono)`, boxShadow: '0 2px 6px rgba(0,0,0,.2), 0 0 0 2px var(--bg2)', fontVariantNumeric: 'tabular-nums' }}>{numero}</div>
                  {occ && (
                    <span style={{ position: 'absolute', top: -6, right: -12, padding: '1px 4px', borderRadius: 5, background: 'var(--up)', color: '#fff', font: '700 8px var(--mono)', whiteSpace: 'nowrap', boxShadow: '0 0 0 1.5px var(--bg2)' }}>▲{occ.minuto}'</span>
                  )}
                </div>
                {!isMobile && (
                  <div style={{ marginTop: 3, font: '600 9.5px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', textShadow: '0 1px 0 var(--bg), 0 0 4px var(--bg)' }}>{nombre}</div>
                )}
              </div>
            )
          }),
        )}
      </div>

      {aproximada && (
        <div style={{ marginTop: 8, font: '500 10px var(--mono)', color: 'var(--t3)' }}>
          posiciones aproximadas por formación (sin grid de la API): el mapa de carriles del DTP tampoco está disponible
        </div>
      )}
      {hayCambios && (
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginTop: 10, flexWrap: 'wrap' }}>
          {calculados.map((l) =>
            l.cambios.length > 0 ? (
              <div key={l.lado} style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 3, alignItems: l.lado === 'visita' ? 'flex-end' : 'flex-start' }}>
                {l.cambios.map((c, i) => (
                  <div key={i} style={{ font: '500 10.5px var(--mono)', color: 'var(--t2)', display: 'flex', alignItems: 'center', gap: 5, flexWrap: 'wrap', justifyContent: l.lado === 'visita' ? 'flex-end' : 'flex-start' }}>
                    <span style={{ color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>{c.minuto}'</span>
                    <span style={{ color: 'var(--down)' }}>▼ {apellido(c.saleNombre)}</span>
                    <span style={{ color: 'var(--up)' }}>▲ {apellido(c.entraNombre)}</span>
                  </div>
                ))}
              </div>
            ) : null,
          )}
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginTop: 10, font: '500 10.5px var(--sans)', color: 'var(--t3)', lineHeight: 1.5, flexWrap: 'wrap' }}>
        {calculados.map((l) => {
          if (l.ali.suplentes.length === 0) return null
          const entraron = new Map(l.cambios.map((c) => [c.entraId, c.minuto]))
          return (
            <div key={l.lado} style={{ flex: 1, minWidth: 0, textAlign: l.lado === 'visita' ? 'right' : 'left' }}>
              Banco:{' '}
              {l.ali.suplentes
                .filter((j) => j.nombre)
                .map((j, i) => (
                  <span key={j.jugadorId}>
                    {i > 0 && ', '}
                    {j.nombre}
                    {entraron.has(j.jugadorId) && <span style={{ color: 'var(--up)', font: '600 9.5px var(--mono)' }}> ▲{entraron.get(j.jugadorId)}'</span>}
                  </span>
                ))}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function LadoXi({ ali, nombre, eventos }: { ali: AlineacionDTO; nombre: string; eventos: EventoPartidoDTO[] }) {
  const cambios = cambiosDelLado(ali, eventos)
  const salieron = new Map(cambios.map((c) => [c.saleId, c.minuto]))
  const entraron = new Map(cambios.map((c) => [c.entraId, c.minuto]))
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
            {salieron.has(j.jugadorId) && (
              <span title="Sustituido" style={{ font: '600 9.5px var(--mono)', color: 'var(--down)', flexShrink: 0 }}>▼ {salieron.get(j.jugadorId)}'</span>
            )}
          </div>
        ))}
      </div>
      {ali.suplentes.length > 0 && (
        <div style={{ marginTop: 8, font: '500 10.5px var(--sans)', color: 'var(--t3)', lineHeight: 1.5 }}>
          Banco:{' '}
          {ali.suplentes
            .filter((j) => j.nombre)
            .map((j, i) => (
              <span key={j.jugadorId}>
                {i > 0 && ', '}
                {j.nombre}
                {entraron.has(j.jugadorId) && <span style={{ color: 'var(--up)', font: '600 9.5px var(--mono)' }}> ▲{entraron.get(j.jugadorId)}'</span>}
              </span>
            ))}
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
  /** Eventos de la ficha: de aquí salen los cambios (sustituciones) del partido. */
  eventos?: EventoPartidoDTO[]
  loading?: boolean
  error?: string | null
  /** Recarga la ficha del backend: el XI aparece solo al confirmarse (~1 h antes). */
  onReload: () => void
  isMobile: boolean
}

export function AlineacionesXi({ local, visitante, localNombre, visitanteNombre, eventos = [], loading, error, onReload, isMobile }: Props) {
  const hayXi = !!(local?.titulares.length || visitante?.titulares.length)
  const [vista, setVista] = useState<'cancha' | 'lista'>('cancha')
  const tab = (activo: boolean) => ({
    padding: '5px 12px', borderRadius: 7, border: 0, cursor: 'pointer', font: '600 11px var(--sans)',
    background: activo ? 'var(--bg)' : 'transparent', color: activo ? 'var(--accent)' : 'var(--t2)',
  })
  return (
    <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: hayXi ? 14 : 8, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ font: '700 12px var(--sans)' }}>Alineaciones confirmadas</div>
          <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginTop: 2 }}>
            La ingesta las captura sola al publicarse (~1 h antes del saque) · son las que alimentan el análisis EFE/DTP y los skills
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          {hayXi && (
            <div style={{ display: 'flex', gap: 2, padding: 2, borderRadius: 9, border: '1px solid var(--line)', background: 'var(--bg3)' }}>
              <button onClick={() => setVista('cancha')} style={tab(vista === 'cancha')}>Cancha</button>
              <button onClick={() => setVista('lista')} style={tab(vista === 'lista')}>Lista</button>
            </div>
          )}
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
      {hayXi && vista === 'cancha' && (
        <CanchaXi local={local} visitante={visitante} localNombre={localNombre} visitanteNombre={visitanteNombre} eventos={eventos} isMobile={isMobile} />
      )}
      {hayXi && vista === 'lista' && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: isMobile ? 18 : 24 }}>
          {local && local.titulares.length > 0 && <LadoXi ali={local} nombre={localNombre} eventos={eventos} />}
          {visitante && visitante.titulares.length > 0 && <LadoXi ali={visitante} nombre={visitanteNombre} eventos={eventos} />}
        </div>
      )}
    </section>
  )
}
