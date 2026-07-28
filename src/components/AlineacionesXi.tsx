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
import { useEffect, useState } from 'react'
import type { AlineacionDTO, EventoPartidoDTO, JugadorDTO, JugadorAlineadoDTO } from '../api/types'

const POS_LABEL: Record<string, string> = { G: 'POR', D: 'DEF', M: 'MED', F: 'DEL' }

// ── indicadores de la capa de jugadores (docs/JUGADORES.md) ─────────────────
// La ficha ya trae la plantilla con sus indicadores calculados: aquí solo se
// cruzan por jugadorId con el once. Mismos criterios de color que la sección
// Plantilla — un score no puede significar una cosa en cada pantalla.

const AMBAR = '#B98A1D'

const ratEstilo = (rating: number | null | undefined) => ({
  bg: rating == null ? 'var(--bg3)' : rating >= 7 ? 'color-mix(in oklch, var(--up), transparent 82%)' : rating < 6.5 ? 'color-mix(in oklch, var(--down), transparent 84%)' : 'var(--bg3)',
  fg: rating == null ? 'var(--t3)' : rating >= 7 ? 'var(--up)' : rating < 6.5 ? 'var(--down)' : 'var(--t2)',
})
const confColor = (c?: string) => (c === 'A' ? 'var(--up)' : c === 'B' ? 'var(--t2)' : 'var(--t3)')
const produccion = (j: JugadorDTO) =>
  j.paradasP90 != null ? `${j.paradasP90.toFixed(1)}🧤 ${j.golesEncajadosP90?.toFixed(1)}GC` : `${j.goles}G+${j.asistencias}A`

const indice = (jugadores?: JugadorDTO[]) => new Map((jugadores ?? []).map((j) => [j.id, j]))

/** Bandera de estado del jugador (baja > capilla > recién llegado): un punto
 *  de color en el chip de la cancha, con su explicación en el tooltip. */
function bandera(j?: JugadorDTO): { color: string; nota: string } | null {
  if (!j) return null
  if (j.baja) return { color: 'var(--down)', nota: `BAJA${j.baja.detalle ? ` · ${j.baja.detalle}` : ''}` }
  if (j.enCapilla) return { color: AMBAR, nota: `en capilla (${j.amarillas} amarillas)` }
  if (j.recienLlegado) return { color: 'var(--accent)', nota: `recién llegado${j.recienLlegado.desde ? ` de ${j.recienLlegado.desde}` : ''}` }
  return null
}

const statsTip = (j?: JugadorDTO) =>
  j
    ? ` · ${Math.round(j.pctMinutos * 100)}% min · ${produccion(j)} · rating ${j.rating != null ? j.rating.toFixed(1) : '—'} · confianza ${j.confianza}`
    : ''

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

function CanchaXi({ local, visitante, localNombre, visitanteNombre, eventos, jugadoresLocal, jugadoresVisitante, isMobile }: { local?: AlineacionDTO | null; visitante?: AlineacionDTO | null; localNombre: string; visitanteNombre: string; eventos: EventoPartidoDTO[]; jugadoresLocal?: JugadorDTO[]; jugadoresVisitante?: JugadorDTO[]; isMobile: boolean }) {
  const lados = [
    local && local.titulares.length > 0 ? { ali: local, lado: 'local' as const, color: 'var(--accent)', nombre: localNombre, plantilla: indice(jugadoresLocal) } : null,
    visitante && visitante.titulares.length > 0 ? { ali: visitante, lado: 'visita' as const, color: 'var(--down)', nombre: visitanteNombre, plantilla: indice(jugadoresVisitante) } : null,
  ].filter((l): l is NonNullable<typeof l> => l !== null)
  const calculados = lados.map((l) => {
    const cambios = cambiosDelLado(l.ali, eventos)
    return { ...l, ...puntosXi(l.ali, l.lado), cambios, porPuesto: ocupantes(l.ali, cambios) }
  })
  const aproximada = calculados.some((l) => !l.exacta)
  const hayCambios = calculados.some((l) => l.cambios.length > 0)
  const hayBanderas = calculados.some((l) =>
    l.puntos.some((p) => bandera(l.plantilla.get(l.porPuesto.get(p.key)?.id ?? p.key))))
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
            // los scores son del que está EN cancha (si entró un cambio, del que entró)
            const jug = l.plantilla.get(occ?.id ?? p.key)
            const flag = bandera(jug)
            const rat = ratEstilo(jug?.rating)
            const titulo =
              (occ ? `${numero} · ${suplente?.nombre ?? occ.nombre} · entró al ${occ.minuto}' por ${p.nombre}` : `${p.numero} · ${p.nombre}`) +
              statsTip(jug) + (flag ? ` · ${flag.nota}` : '')
            return (
              <div key={`${l.lado}-${p.key}`} title={titulo} style={{ position: 'absolute', left: `${p.x}%`, top: `${p.y}%`, transform: 'translate(-50%, -50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', animation: 'sadup .35s ease both' }}>
                <div style={{ position: 'relative', width: dCirculo, height: dCirculo }}>
                  <div style={{ width: dCirculo, height: dCirculo, borderRadius: '50%', background: l.color, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `700 ${isMobile ? 10.5 : 12}px var(--mono)`, boxShadow: '0 2px 6px rgba(0,0,0,.2), 0 0 0 2px var(--bg2)', fontVariantNumeric: 'tabular-nums' }}>{numero}</div>
                  {occ && (
                    <span style={{ position: 'absolute', top: -6, right: -12, padding: '1px 4px', borderRadius: 5, background: 'var(--up)', color: '#fff', font: '700 8px var(--mono)', whiteSpace: 'nowrap', boxShadow: '0 0 0 1.5px var(--bg2)' }}>▲{occ.minuto}'</span>
                  )}
                  {flag && (
                    <span style={{ position: 'absolute', top: -2, left: -3, width: isMobile ? 9 : 11, height: isMobile ? 9 : 11, borderRadius: '50%', background: flag.color, boxShadow: '0 0 0 2px var(--bg2)' }}></span>
                  )}
                </div>
                {!isMobile && (
                  <>
                    <div style={{ marginTop: 3, font: '600 9.5px var(--sans)', color: 'var(--t1)', whiteSpace: 'nowrap', textShadow: '0 1px 0 var(--bg), 0 0 4px var(--bg)' }}>{nombre}</div>
                    {jug && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 3, marginTop: 2 }}>
                        <span style={{ padding: '1px 5px', borderRadius: 5, background: rat.bg, color: rat.fg, font: '700 8.5px var(--mono)', fontVariantNumeric: 'tabular-nums', textShadow: 'none' }}>{jug.rating != null ? jug.rating.toFixed(1) : '—'}</span>
                        <span style={{ font: '700 8.5px var(--mono)', color: confColor(jug.confianza), textShadow: '0 1px 0 var(--bg), 0 0 4px var(--bg)' }}>{jug.confianza}</span>
                      </div>
                    )}
                  </>
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
      {hayBanderas && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8, font: '500 9.5px var(--mono)', color: 'var(--t3)', flexWrap: 'wrap' }}>
          {([['var(--down)', 'baja / duda'], [AMBAR, 'en capilla'], ['var(--accent)', 'recién llegado']] as const).map(([c, l]) => (
            <span key={l} style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: c }}></span>{l}
            </span>
          ))}
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
      {/* banco con las mismas estadísticas que los de la cancha: dorsal,
          rating con sus umbrales de color y confianza A/B/C */}
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginTop: 10, flexWrap: 'wrap' }}>
        {calculados.map((l) => {
          if (l.ali.suplentes.length === 0) return null
          const entraron = new Map(l.cambios.map((c) => [c.entraId, c.minuto]))
          const alDerecha = l.lado === 'visita' && !isMobile
          return (
            <div key={l.lado} style={{ flex: 1, minWidth: isMobile ? '100%' : 220, display: 'flex', flexDirection: 'column', gap: 3, alignItems: alDerecha ? 'flex-end' : 'flex-start' }}>
              <div style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px' }}>BANCO · {l.nombre}</div>
              {l.ali.suplentes
                .filter((j) => j.nombre)
                .map((j) => {
                  const jug = l.plantilla.get(j.jugadorId)
                  const flag = bandera(jug)
                  const rat = ratEstilo(jug?.rating)
                  const min = entraron.get(j.jugadorId)
                  return (
                    <div key={j.jugadorId} title={`${j.nombre}${statsTip(jug)}${flag ? ` · ${flag.nota}` : ''}`} style={{ display: 'flex', flexDirection: alDerecha ? 'row-reverse' : 'row', alignItems: 'center', gap: 6, maxWidth: '100%' }}>
                      <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 18, textAlign: alDerecha ? 'left' : 'right', flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>{j.numero ?? '–'}</span>
                      {flag && <span style={{ width: 7, height: 7, borderRadius: '50%', background: flag.color, flexShrink: 0 }}></span>}
                      <span style={{ font: '500 11px var(--sans)', color: 'var(--t2)', minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.nombre}</span>
                      {min != null && <span title="Entró al partido" style={{ font: '600 9.5px var(--mono)', color: 'var(--up)', flexShrink: 0 }}>▲{min}'</span>}
                      {jug && (
                        <>
                          <span title="Rating medio ponderado por minutos" style={{ padding: '1px 6px', borderRadius: 5, background: rat.bg, color: rat.fg, font: '700 9.5px var(--mono)', fontVariantNumeric: 'tabular-nums', flexShrink: 0 }}>{jug.rating != null ? jug.rating.toFixed(1) : '—'}</span>
                          <span title={`Confianza estadística por minutos jugados (${jug.minutos} min)`} style={{ font: '700 9.5px var(--mono)', color: confColor(jug.confianza), flexShrink: 0 }}>{jug.confianza}</span>
                        </>
                      )}
                    </div>
                  )
                })}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function LadoXi({ ali, nombre, eventos, jugadores, isMobile }: { ali: AlineacionDTO; nombre: string; eventos: EventoPartidoDTO[]; jugadores: Map<number, JugadorDTO>; isMobile: boolean }) {
  const cambios = cambiosDelLado(ali, eventos)
  const salieron = new Map(cambios.map((c) => [c.saleId, c.minuto]))
  const entraron = new Map(cambios.map((c) => [c.entraId, c.minuto]))
  // en móvil la columna POS se sacrifica y PRODUCCIÓN se estrecha: el nombre
  // necesita espacio real, no puntos suspensivos en cada fila
  const wProd = isMobile ? 64 : 92
  const hayScores = ali.titulares.some((j) => jugadores.has(j.jugadorId))
  const cab = (t: string, w: number, align: 'right' | 'center' = 'right') => (
    <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', width: w, textAlign: align, flexShrink: 0, letterSpacing: '.4px' }}>{t}</span>
  )
  return (
    <div style={{ minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
        <span style={{ font: '700 13px var(--sans)', color: 'var(--t1)' }}>{nombre}</span>
        {ali.formacion && (
          <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--accent-soft)', color: 'var(--accent)', font: '700 10px var(--mono)', letterSpacing: '.3px' }}>{ali.formacion}</span>
        )}
        {ali.entrenador && <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>DT {ali.entrenador}</span>}
      </div>
      {hayScores && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 0 5px' }}>
          <span style={{ width: 18, flexShrink: 0 }}></span>
          {!isMobile && <span style={{ width: 26, flexShrink: 0 }}></span>}
          <span style={{ flex: 1, minWidth: 0 }}></span>
          {cab('MIN', 34)}
          {cab('PRODUCCIÓN', wProd)}
          {cab('RAT', 34, 'center')}
          {cab('±', 18, 'center')}
        </div>
      )}
      {(() => {
        // misma fila para once y banco: el suplente merece las mismas
        // estadísticas que el que está en cancha (su letra y su puntaje)
        const fila = (j: JugadorAlineadoDTO, enBanco: boolean) => {
          const jug = jugadores.get(j.jugadorId)
          const rat = ratEstilo(jug?.rating)
          return (
            <div key={j.jugadorId} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t3)', width: 18, textAlign: 'right', flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>{j.numero ?? '–'}</span>
              {!isMobile && (
                <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', width: 26, flexShrink: 0, letterSpacing: '.3px' }}>{j.posicion ? POS_LABEL[j.posicion] ?? j.posicion : ''}</span>
              )}
              <span title={jug ? `${j.nombre}${statsTip(jug)}` : undefined} style={{ font: '500 12px var(--sans)', color: enBanco ? 'var(--t2)' : 'var(--t1)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {j.nombre ?? '—'}
                {!enBanco && salieron.has(j.jugadorId) && (
                  <span title="Sustituido" style={{ marginLeft: 6, font: '600 9.5px var(--mono)', color: 'var(--down)' }}>▼{salieron.get(j.jugadorId)}'</span>
                )}
                {enBanco && entraron.has(j.jugadorId) && (
                  <span title="Entró al partido" style={{ marginLeft: 6, font: '600 9.5px var(--mono)', color: 'var(--up)' }}>▲{entraron.get(j.jugadorId)}'</span>
                )}
              </span>
              {hayScores && (
                <>
                  <span title={jug ? `${jug.minutos} minutos` : undefined} style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)', width: 34, textAlign: 'right', flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>{jug ? `${Math.round(jug.pctMinutos * 100)}%` : '—'}</span>
                  <span title={jug?.paradasP90 != null ? 'Paradas y goles encajados por 90 minutos' : jug ? `${jug.goles} goles + ${jug.asistencias} asistencias` : undefined} style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)', width: wProd, textAlign: 'right', flexShrink: 0, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>{jug ? produccion(jug) : '—'}</span>
                  <span title="Rating medio ponderado por minutos" style={{ padding: '3px 0', borderRadius: 6, background: rat.bg, color: rat.fg, width: 34, textAlign: 'center', flexShrink: 0, font: '700 10.5px var(--mono)', fontVariantNumeric: 'tabular-nums' }}>{jug?.rating != null ? jug.rating.toFixed(1) : '—'}</span>
                  <span title={jug ? `Confianza estadística por minutos jugados (${jug.minutos} min)` : undefined} style={{ width: 18, height: 18, borderRadius: 5, background: 'var(--bg3)', color: confColor(jug?.confianza), display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 9.5px var(--mono)', flexShrink: 0 }}>{jug?.confianza ?? '—'}</span>
                </>
              )}
            </div>
          )
        }
        return (
          <>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {ali.titulares.map((j) => fila(j, false))}
            </div>
            {ali.suplentes.length > 0 && (
              <>
                <div style={{ margin: '10px 0 4px', font: '600 8.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px' }}>BANCO</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {ali.suplentes.map((j) => fila(j, true))}
                </div>
              </>
            )}
          </>
        )
      })()}
      {!ali.conGrid && (
        <div style={{ marginTop: 6, font: '500 10px var(--mono)', color: 'var(--t3)' }}>sin grid de la API: el mapa de carriles del DTP no está disponible</div>
      )}
    </div>
  )
}

/** Vacío honesto CON reloj (regla "real o nada" + cuándo se vuelve a mirar):
 *  la cuenta atrás del próximo sondeo automático evita el ↻ compulsivo. */
function VacioXi({ refreshMs }: { refreshMs?: number }) {
  const [restante, setRestante] = useState(refreshMs ?? 0)
  useEffect(() => {
    if (!refreshMs) return
    const t0 = Date.now()
    const iv = setInterval(() => setRestante(refreshMs - ((Date.now() - t0) % refreshMs)), 1000)
    return () => clearInterval(iv)
  }, [refreshMs])
  const mm = Math.floor(restante / 60000)
  const ss = Math.floor((restante % 60000) / 1000)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
      <div style={{ width: 34, height: 34, borderRadius: 10, background: 'var(--bg3)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--t3)', flexShrink: 0 }}>
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" /></svg>
      </div>
      <div style={{ flex: 1, minWidth: 180 }}>
        <div style={{ font: '600 12px var(--sans)', color: 'var(--t1)' }}>Aún sin XI publicado por la API</div>
        <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', marginTop: 2 }}>
          se suele publicar ~1 h antes del saque
          {refreshMs ? ` · próximo sondeo automático en ${mm}:${String(ss).padStart(2, '0')}` : ''} · con ↻ lo traes al momento
        </div>
      </div>
      {refreshMs ? (
        <div style={{ height: 4, width: 120, borderRadius: 3, background: 'var(--bg3)', overflow: 'hidden', flexShrink: 0 }}>
          <div style={{ height: '100%', width: `${Math.round((1 - restante / refreshMs) * 100)}%`, background: 'var(--accent)', borderRadius: 3 }}></div>
        </div>
      ) : null}
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
  /** Plantillas con indicadores (la ficha ya las trae): scores junto al once. */
  jugadoresLocal?: JugadorDTO[]
  jugadoresVisitante?: JugadorDTO[]
  /** Intervalo del refresco silencioso de la ficha: alimenta la cuenta atrás del vacío. */
  refreshMs?: number
  loading?: boolean
  error?: string | null
  /** Recarga la ficha del backend: el XI aparece solo al confirmarse (~1 h antes). */
  onReload: () => void
  isMobile: boolean
}

export function AlineacionesXi({ local, visitante, localNombre, visitanteNombre, eventos = [], jugadoresLocal, jugadoresVisitante, refreshMs, loading, error, onReload, isMobile }: Props) {
  const hayXi = !!(local?.titulares.length || visitante?.titulares.length)
  const [vista, setVista] = useState<'cancha' | 'lista'>('cancha')
  const tab = (activo: boolean) => ({
    padding: '5px 12px', borderRadius: 7, border: 0, cursor: 'pointer', font: '600 11px var(--sans)',
    background: activo ? 'var(--bg)' : 'transparent', color: activo ? 'var(--accent)' : 'var(--t2)',
  })
  return (
    <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      {/* en móvil el título ocupa su propia línea: los controles no pueden
          aplastar el subtítulo a una palabra por renglón */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: hayXi ? 14 : 8, flexWrap: 'wrap' }}>
        <div style={{ flex: isMobile ? '1 1 100%' : 1, minWidth: 0 }}>
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
      {!error && !loading && !hayXi && <VacioXi refreshMs={refreshMs} />}
      {hayXi && vista === 'cancha' && (
        <CanchaXi local={local} visitante={visitante} localNombre={localNombre} visitanteNombre={visitanteNombre} eventos={eventos} jugadoresLocal={jugadoresLocal} jugadoresVisitante={jugadoresVisitante} isMobile={isMobile} />
      )}
      {hayXi && vista === 'lista' && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: isMobile ? 18 : 24 }}>
          {local && local.titulares.length > 0 && <LadoXi ali={local} nombre={localNombre} eventos={eventos} jugadores={indice(jugadoresLocal)} isMobile={isMobile} />}
          {visitante && visitante.titulares.length > 0 && <LadoXi ali={visitante} nombre={visitanteNombre} eventos={eventos} jugadores={indice(jugadoresVisitante)} isMobile={isMobile} />}
        </div>
      )}
    </section>
  )
}
