// Verificación del espejo TS del reventón de burbuja (src/lib/burbuja.ts)
// contra los MISMOS vectores dorados que backend/test_burbuja.py.
// Ejecutar: npm run test:burbuja
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { analizarBurbujas, espinaTarjeta, extremoDe, type ContextoBurbuja, type FilaK } from '../src/lib/burbuja'
import type { HistorialSignoDTO, ReventonDTO } from '../src/api/types'

let failed = 0
function check(name: string, cond: boolean, detalle?: unknown) {
  if (!cond) failed++
  console.log(`${cond ? '✓' : '✗ FALLA'} ${name}` + (!cond && detalle !== undefined ? ` → ${JSON.stringify(detalle)}` : ''))
}
const eq = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b)

const aqui = dirname(fileURLToPath(import.meta.url))
const casos = JSON.parse(readFileSync(join(aqui, 'casos_burbuja.json'), 'utf8')) as { filas: FilaK[]; ctx: ContextoBurbuja }
const { filas, ctx } = casos
const analizar = (f: FilaK[], cambios: Partial<ContextoBurbuja> = {}) => analizarBurbujas(f, { ...ctx, ...cambios })

const fila = (i: number, cond: 'Local' | 'Visita', gf: number, ga: number, nivel: number, k: number, kl: number, kv: number): FilaK => ({
  fixtureId: 5000 + i, fecha: `2026-02-${String(i + 1).padStart(2, '0')}T20:00:00Z`, condicion: cond,
  rivalId: 900 + i, rivalNombre: `R${i}`, nivelRival: nivel, golesFavor: gf, golesContra: ga, esInternacional: false,
  fusion: { k, kLocal: kl, kVisita: kv },
})

const out = analizar(filas)

console.log('— cabecera —')
check('20 partidos procesados', out.partidos === 20)
check('manda la familia total; la regla del nivel viaja como dato sin confirmar', out.mandan.tipo === 'globales' && eq(out.mandan.familias, ['total']) && eq(out.mandan.reglaNivel.familias, ['visita']) && out.mandan.reglaNivel.confirmada === false, out.mandan)
check('el aviso dice que es guía, no probabilidad', out.aviso.includes('no probabilidad'))

console.log('\n— familia total —')
const t = out.familias.total
check('20 partidos en condición', t.partidosEnCondicion === 20)
check('5 reventones cerrados', t.reventones.length === 5, t.reventones.length)
const r0 = t.reventones[0]
check('1er reventón: + de 2 partidos, K pico 7.5, lo reventó C (3.0) de local 0-1',
  eq([r0.signo, r0.partidos, r0.kPico, r0.rival, r0.nivelRival, r0.condicion, r0.resultado], ['+', 2, 7.5, 'C', 3.0, 'L', '0-1']), r0)
const r2 = t.reventones[2]
check('3er reventón: + de 3 partidos, K pico 13.3, empate con H', eq([r2.signo, r2.partidos, r2.kPico, r2.rival, r2.resultado], ['+', 3, 13.3, 'H', '1-1']), r2)
check('un cambio de signo en el mismo partido cierra la burbuja y abre la contraria', t.reventones[0].fixtureId === 1002 && t.reventones[1].signo === '-')
const hp = t.historial.positivo!
check('historial +: n=3', hp.n === 3, hp)
check('cómo terminan: + 1 a cero y 2 al otro signo; − 2 a cero (los empates reinician)', eq(hp.termina, { cero: 1, cambio: 2 }) && eq(t.historial.negativo!.termina, { cero: 2, cambio: 0 }), [hp.termina, t.historial.negativo!.termina])
check('K pico +: media 8.77 · mediana 7.5 · sin moda · min 5.5 · max 13.3', eq(hp.kPico, { media: 8.77, mediana: 7.5, moda: null, min: 5.5, max: 13.3 }), hp.kPico)
check('partidos +: media 2.33 · mediana 2 · moda 2', eq([hp.partidos.media, hp.partidos.mediana, hp.partidos.moda], [2.33, 2, 2]), hp.partidos)
check('nivel del rival que revienta +: media 2.33 · mediana 2.0 · moda 2.0', eq([hp.nivelRival.media, hp.nivelRival.mediana, hp.nivelRival.moda], [2.33, 2, 2]), hp.nivelRival)
const hn = t.historial.negativo!
check('historial −: n=2, K pico media 8 sin moda, nivel rival media 1.25', hn.n === 2 && hn.kPico.media === 8 && hn.kPico.moda === null && hn.nivelRival.media === 1.25, hn)
const a = t.actual!
check('burbuja abierta: + · K 22.1 · 6 partidos · aplica al próximo', eq([a.signo, a.k, a.partidos, a.aplicaAlProximo], ['+', 22.1, 6, true]), a)
check('posición: percentil 100 en K y en racha, K = 2.95× la mediana', eq(t.posicion, { percentilK: 100, percentilRacha: 100, kSobreMediana: 2.95 }), t.posicion)
check('rival próximo (2.6) mucho más fuerte que la mediana (2.0) → tramo muy fuerte', eq(t.rival, { nivelProximo: 2.6, medianaReventon: 2, distancia: 0.6, enZona: true, tramo: 'muy fuerte', aFavor: -0.2, favorito: 'no' }), t.rival)
const rg = t.riesgo!
check('riesgo MUY ALTO con 3 puntos (racha +1, rival muy fuerte +2) y 3 motivos', rg.nivel === 'muy alto' && rg.puntos === 3 && rg.motivos.length === 3, rg)
check('la K se describe pero no puntúa', rg.motivos.some((m) => m.includes('la K no puntúa') && m.includes('22.1')), rg.motivos)
check('confianza BAJA: muestra corta (3) y estabilidad inestable', rg.confianza === 'baja' && rg.confianzaMotivos.some((m) => m.includes('inestable')), rg.confianzaMotivos)
console.log('\n— por período —')
const per = t.historialPorPeriodo
check('sin temporada en las filas: temporada (sin dato) · año 2026 · dt · últimos 20', eq(per.map((p) => p.clave), ['temporada', 'anio:2026', 'dt', 'ultimos20']), per.map((p) => p.clave))
check('el período sin dato viaja con sinDato, no con un corte inventado', per[0].sinDato !== '' && per[0].positivo === null, per[0])
check('año 2026: desde el 1 de enero hasta el 1 de enero siguiente, vigente, los 5 reventones y los 20 partidos', per[1].desde === '2026-01-01' && per[1].hasta === '2027-01-01' && per[1].vigente && per[1].reventones === 5 && per[1].partidos === 20 && eq(per[1].positivo, t.historial.positivo), per[1])
check('con el DT actual (desde 2026-08-07): ningún reventón, referencia vacía con su n', per[2].desde === '2026-08-07' && per[2].reventones === 0 && per[2].positivo === null && per[2].negativo === null, per[2])
check('últimos 20 partidos = toda la muestra de 20', per[3].partidos === 20 && per[3].reventones === 5, per[3])
const conTemporada = analizar(filas.map((f, i) => ({ ...f, temporada: i < 8 ? 2025 : 2026 })))
const pts = conTemporada.familias.total.historialPorPeriodo
const corte = filas[8].fecha.slice(0, 10)
check('con temporada en las filas hay UNA por temporada, en orden: 2025 (cerrada en el 1.º de 2026) y 2026 (vigente, abierta)',
  pts[0].clave === 'temporada:2025' && pts[0].desde === filas[0].fecha.slice(0, 10) && pts[0].hasta === corte && !pts[0].vigente
  && pts[1].clave === 'temporada:2026' && pts[1].desde === corte && pts[1].hasta === '' && pts[1].vigente, pts.slice(0, 2))
check('cada temporada cuenta solo lo que reventó dentro de sus fechas, y entre las dos suman la historia',
  pts[0].partidos === 8 && pts[1].partidos === 12 && pts[0].reventones + pts[1].reventones === 5
  && pts[1].reventones === t.reventones.filter((r) => r.fecha.slice(0, 10) >= corte).length, pts.slice(0, 2))
check('los períodos viajan también en la cabecera', eq(out.periodos.map((p) => p.clave), per.map((p) => p.clave)))

const ex = t.extremo!
check('ALERTA DE EXTREMO activa: K 22.1 ≥ máximo previo 13.3 y racha 6 ≥ 3, sobre 20 partidos', ex.activo && ex.kRecord && ex.rachaRecord && ex.partidosHistoria === 20 && eq(ex.maximoPrevio, { kPico: 13.3, partidos: 3 }), ex)
check('extremo: dos motivos con el N de partidos y texto que pide no cargar la apuesta', ex.motivos.length === 2 && ex.motivos.every((m) => m.includes('20 partidos')) && ex.texto.includes('no cargar la apuesta'), ex.motivos)
check('el extremo NO mueve el riesgo: sigue en 3 puntos', rg.puntos === 3)
check('la guía calibrada de adónde va la K: muy alto + → 27 · 27 · 46 %', eq(rg.movimiento, { sigue: 0.272, cero: 0.269, cambio: 0.459 }), rg.movimiento)

console.log('\n— familia local —')
const lo = out.familias.local
check('11 partidos de local', lo.partidosEnCondicion === 11)
check('burbuja abierta + K 9.5, 3 partidos, NO aplica al próximo', eq([lo.actual!.k, lo.actual!.partidos, lo.actual!.aplicaAlProximo], [9.5, 3, false]), lo.actual)
check('sin rival evaluado (otra condición) y motivo explícito', lo.rival === null && lo.riesgo!.motivos.some((m) => m.includes('otra condición')), lo.riesgo)
check('riesgo ALTO con 1 punto (solo la racha; cortes limpios del 14/10)', lo.riesgo!.nivel === 'alto' && lo.riesgo!.puntos === 1, lo.riesgo)
check('la K local no se mueve en el próximo (es de visita): sin guía de movimiento', lo.riesgo!.movimiento === null)
check('historial − local: K pico 3.0 repetida → moda 3.0', lo.historial.negativo!.kPico.moda === 3)
check('percentil K 50', lo.posicion!.percentilK === 50, lo.posicion)
check('local: K 9.5 < máximo 16 y racha 3 < 4 → extremo INACTIVO', eq(lo.extremo, { activo: false, kRecord: false, rachaRecord: false, cerca: false, partidosHistoria: 11, maximoPrevio: { kPico: 16, partidos: 4 }, motivos: [], texto: '', inflada: null }), lo.extremo)
// AMISTOSOS: cuentan, pero el extremo hecho con la mitad o más se marca inflado (mismo vector que el Python)
const conAm = analizar(filas.map((f, i) => (i >= filas.length - 3 ? { ...f, ligaId: 667 } : f)))
const exAm = conAm.familias.total.extremo!
check('3 de 6 de la racha en amistosos → extremo INFLADO, sigue activo y el riesgo no se mueve', exAm.activo && exAm.inflada?.amistosos === 3 && exAm.inflada?.partidos === 6 && conAm.familias.total.riesgo!.puntos === t.riesgo!.puntos && conAm.familias.total.actual!.amistosos === 3, exAm)
const dosAm = analizar(filas.map((f, i) => (i >= filas.length - 2 ? { ...f, ligaId: 667 } : f)))
check('2 de 6 → no está inflado', dosAm.familias.total.extremo!.inflada === null)
const baseRec = { kPico: { max: 30 }, partidos: { max: 5 } } as unknown as Parameters<typeof extremoDe>[2]
const exRec = extremoDe(20, 6, baseRec, 100, '+', [], 2)
check('racha récord de 6 sobre un máximo de 5 con 2 amistosos: sin ellos no sería récord → INFLADA', exRec.rachaRecord && !exRec.kRecord && !!exRec.inflada && exRec.inflada.texto.includes('no sería récord'), exRec)
check('con 1 amistoso (6 − 1 = 5) sin él solo IGUALARÍA el máximo de 5: ya no es récord → INFLADA (67)', extremoDe(20, 6, baseRec, 100, '+', [], 1).inflada !== null)
check('con 0 amistosos y 7 sobre 5 → récord limpio, sin marca', extremoDe(20, 7, baseRec, 100, '+', [], 0).inflada === null)
// RÉCORD DE RACHA: superar y con 3+ (incidencia 67)
{
  const b1 = { kPico: { max: 30 }, partidos: { max: 1 } } as unknown as Parameters<typeof extremoDe>[2]
  const b2 = { kPico: { max: 30 }, partidos: { max: 2 } } as unknown as Parameters<typeof extremoDe>[2]
  check('67: 2 seguidos sobre un máximo de 1 (Leones del Norte) → NO es récord: menos de 3', !extremoDe(5, 2, b1, 55, '-', [], 0).activo)
  const deK10 = Array.from({ length: 10 }, () => ({ kPico: 10, partidos: 1 })) as unknown as Parameters<typeof extremoDe>[5]
  const cu = extremoDe(5, 2, b2, 113, '-', deK10, 0)
  check('67: 2 que IGUALAN un máximo de 2 (Cusco, Medellín) → no es récord ni «cerca»', !cu.activo && !cu.cerca, cu)
  check('67: 3 sobre un máximo de 2 → récord', extremoDe(5, 3, b2, 113, '-', [], 0).rachaRecord)
  const ig = extremoDe(5, 5, baseRec, 172, '+', deK10, 0)
  check('67: 5 que IGUALAN un máximo de 5 (Aston Villa) → no es rojo; queda en ámbar (cerca)', !ig.activo && ig.cerca, ig)
  const st = extremoDe(5, 2, { kPico: { max: 30 }, partidos: { max: 4 } } as unknown as Parameters<typeof extremoDe>[2], 40, '+', [], 2)
  check('311: 2 de 2 amistosos sin récord ni cerca (Stuttgart) → INFLADA igual, sin motivos de alerta', !st.activo && !st.cerca && !!st.inflada && st.motivos.length === 0 && st.inflada.texto.includes('último partido oficial'), st)
}

// CERCA DEL EXTREMO (§10): el caso ADT sintético, el mismo que en Python
{
  const deC = [2, 3, 4, 5, 6, 7, 8, 9, 10, 19.54].map((k, i) => ({ kPico: k, partidos: [1, 1, 1, 1, 1, 2, 2, 2, 1, 4][i] })) as ReventonDTO[]
  const baseC = { kPico: { max: 19.54 }, partidos: { max: 4 } } as HistorialSignoDTO
  const ce = extremoDe(17.93, 3, baseC, 280, '-', deC)
  check('CERCA: K −17.93 sobre récord −19.54 y racha 3 sobre 4 → cerca, NO activo', ce.cerca && !ce.activo && !ce.kRecord && !ce.rachaRecord, ce)
  check('cerca: los mismos dos motivos que en Python y texto que pide no cargar fuerte',
    eq(ce.motivos, ['K -17.93: más baja que el 90 % de las 10 burbujas - que reventaron (récord previo -19.54, a 1.61)',
      '3 partidos seguidos: más que el 90 % de las 10 burbujas - que reventaron (máximo previo 4)'])
    && ce.texto.startsWith('CERCA DEL EXTREMO') && ce.texto.includes('no cargar fuerte'), ce.motivos)
  const rec = extremoDe(26.04, 1, baseC, 280, '-', deC)
  check('récord negativo: el motivo lleva el signo y cerca queda en false', rec.activo && !rec.cerca && rec.motivos[0].startsWith('K -26.04: la más baja') && rec.motivos[0].includes('récord previo -19.54'), rec)
  const lejos = extremoDe(9.5, 1, baseC, 280, '-', deC)
  check('K −9.5 (80 %) y racha 1 → ni extremo ni cerca', !lejos.activo && !lejos.cerca && lejos.motivos.length === 0 && lejos.texto === '', lejos)
}

console.log('\n— familia visita —')
const vi = out.familias.visita
check('9 partidos de visita', vi.partidosEnCondicion === 9)
check('burbuja abierta + K 12.6 · 3 partidos', eq([vi.actual!.k, vi.actual!.partidos], [12.6, 3]))
check('riesgo MUY ALTO (8) y moda de partidos 1', vi.riesgo!.nivel === 'muy alto' && vi.historial.positivo!.partidos.moda === 1, vi.riesgo)
check('la K de visita SÍ se mueve en el próximo: su guía (muy alto +) → 20 · 26 · 55 %', eq(vi.riesgo!.movimiento, { sigue: 0.197, cero: 0.256, cambio: 0.546 }), vi.riesgo!.movimiento)

console.log('\n— estabilidad —')
const e = out.estabilidad
check('DT de 40 días + 7 movimientos → INESTABLE', e.grado === 'inestable', e)
check('dt.dias 40 · bajas 3 (las 3 de Missing Fixture con lectura ruido NO cuentan) · movimientos 4+3', e.dt!.dias === 40 && e.bajas === 3 && eq(e.movimientos, { llegadas: 4, salidas: 3, ventanaDias: 120 }), e)
check('dueños/organización declarado SIN DATO', e.sinDato.some((s) => s.includes('dueños')))
const pl = ctx.plantilla!
const est = analizar(filas, { plantilla: { ...pl, entrenador: { nombre: 'Viejo', desde: '2024-01-01' }, revolucion: { llegadas: 1, salidas: 0, ventanaDias: 120 } } })
check('DT asentado + 1 movimiento → ESTABLE, confianza MEDIA (n=3)', est.estabilidad.grado === 'estable' && est.familias.total.riesgo!.confianza === 'media', est.estabilidad)
// incidencia 186: la llegada aproximada de /coachs no vuelve inestable al equipo
const apx = analizar(filas, { plantilla: { ...pl, entrenador: { nombre: 'Pérez', desde: '2026-08-07', fuente: 'coachs' }, revolucion: { llegadas: 1, salidas: 0, ventanaDias: 120 } } })
check('DT con llegada de /coachs y 40 días: no sube a inestable, se declara sin dato', apx.estabilidad.grado === 'estable' && apx.estabilidad.sinDato.some((s) => s.includes('confirmada')), apx.estabilidad)
// umbrales 10 y 20 sobre los movimientos CON MINUTOS (usuario, 23/10/2026)
const grado = (llegadas: number, salidas: number) => analizar(filas, { plantilla: { ...pl, entrenador: { nombre: 'Viejo', desde: '2024-01-01' }, revolucion: { llegadas, salidas, ventanaDias: 120 } } }).estabilidad.grado
check('9 movimientos con minutos → ESTABLE (Arsenal); 10 → EN TRANSICIÓN; 20 → INESTABLE', eq([grado(5, 4), grado(6, 4), grado(12, 8)], ['estable', 'en transición', 'inestable']), [grado(5, 4), grado(6, 4), grado(12, 8)])
// incidencia 43: cuentan los que jugaron; los de papel se dicen al lado
const juve = analizar(filas, { plantilla: { ...pl, entrenador: { nombre: 'Viejo', desde: '2024-01-01' }, revolucion: { llegadas: 2, salidas: 0, ventanaDias: 120, enPapeles: { llegadas: 41, salidas: 44 } } } })
check('43: 2 con minutos de 85 en papeles → ESTABLE y el motivo dice las dos cifras', juve.estabilidad.grado === 'estable' && juve.estabilidad.motivos.some((m) => m.includes('2 movimientos con minutos (de 85 en papeles)')), juve.estabilidad.motivos)
const vieja = analizar(filas, { plantilla: { ...pl, actualizadoEn: '2026-07-01T00:00:00Z' } })
check('plantilla de hace 77 días: aviso', vieja.estabilidad.motivos.some((m) => m.includes('77 días')), vieja.estabilidad.motivos)
const sd = analizar(filas, { plantilla: null })
check('sin plantilla → SIN DATO y confianza no pasa de MEDIA', sd.estabilidad.grado === 'sin dato' && sd.familias.total.riesgo!.confianza === 'media', sd.estabilidad)

console.log('\n— qué constante manda —')
const r8 = analizar(filas, { bin: 8 }).mandan.reglaNivel
check('regla del nivel, bin 8 → globales (dato, no confirmada)', r8.tipo === 'globales' && eq(r8.familias, ['total']) && r8.confirmada === false, r8)
check('regla del nivel, bin 1 → globales', analizar(filas, { bin: 1 }).mandan.reglaNivel.tipo === 'globales')
const sp = analizar(filas, { proximo: null })
check('sin próximo: la regla diría las dos específicas; manda igual la total', eq(sp.mandan.reglaNivel.familias, ['local', 'visita']) && eq(sp.mandan.familias, ['total']))
check('sin próximo: el rival no puntúa y se dice', sp.familias.total.rival === null && sp.familias.total.riesgo!.motivos.some((m) => m.includes('sin próximo')))
const lejos = analizar(filas, { proximo: { ...ctx.proximo!, nivelRival: 1.5 } })
check('rival 1.5 → lejos (0) y favorito por 0.9 (−1): racha +1 → 0, MEDIO', lejos.familias.total.rival!.tramo === 'lejos' && lejos.familias.total.rival!.enZona === false && lejos.familias.total.rival!.favorito === 'favorito' && lejos.familias.total.riesgo!.nivel === 'medio' && lejos.familias.total.riesgo!.puntos === 0, lejos.familias.total.riesgo)
const muy = analizar(filas, { proximo: { ...ctx.proximo!, nivelRival: 1.2 } })
check('rival 1.2: MUY favorito (1.2 a favor, −3) → −2, BAJO', muy.familias.total.rival!.favorito === 'muy favorito' && muy.familias.total.riesgo!.puntos === -2 && muy.familias.total.riesgo!.nivel === 'bajo', muy.familias.total.riesgo)
check('el motivo del favorito se dice desde la racha (Albion, 18/10)', lejos.familias.total.riesgo!.motivos.includes('el equipo es favorito: 0.9 de nivel sobre el rival, a favor de que la racha siga (-1)') && muy.familias.total.riesgo!.motivos.some((m) => m.startsWith('el equipo es muy favorito: 1.2 de nivel')), lejos.familias.total.riesgo!.motivos)
const cm = analizar(filas.map((f, i) => (i >= filas.length - 6 ? { ...f, condicion: 'Local' as const } : f)))
check('racha de 6 toda de local y el próximo de visita → contramano (+1): 4, MUY ALTO', cm.familias.total.actual!.contramano === true && cm.familias.total.riesgo!.puntos === 4 && cm.familias.total.riesgo!.motivos.some((m) => m.includes('otra condición') && m.includes('visita')), cm.familias.total.riesgo)
const borde = analizar(filas, { proximo: { ...ctx.proximo!, nivelRival: 1.85 } })
check('tolerancia 0.15: rival 1.85 en zona (+0) y favorito por 0.55 (−1): 0, MEDIO', borde.familias.total.rival!.tramo === 'zona' && borde.familias.total.riesgo!.puntos === 0 && borde.familias.total.riesgo!.nivel === 'medio', borde.familias.total.riesgo)
const fuerte = analizar(filas, { proximo: { ...ctx.proximo!, nivelRival: 2.3 } })
check('rival 2.3 (+0.3) → tramo fuerte (+1 → 2, ALTO)', fuerte.familias.total.rival!.tramo === 'fuerte' && fuerte.familias.total.riesgo!.puntos === 2 && fuerte.familias.total.riesgo!.nivel === 'alto', fuerte.familias.total.riesgo)

console.log('\n— bordes —')
const vacio = analizar([])
check('sin historia: nada abierto, sin reventones, sin riesgo', vacio.familias.total.actual === null && vacio.familias.total.reventones.length === 0 && vacio.familias.total.riesgo === null)
const cero = analizar([...filas, fila(0, 'Local', 1, 1, 2.0, 0, 0, 12.6)])
check('último partido en 0 → sin burbuja abierta, reventón registrado (6)', cero.familias.total.actual === null && cero.familias.total.reventones.length === 6)
const sinbase = analizar([fila(0, 'Local', 2, 0, 2.0, 4, 4, 0), fila(1, 'Visita', 1, 0, 2.0, 6.8, 4, 2.8)])
check('burbuja abierta sin reventones previos → SIN BASE', sinbase.familias.total.riesgo!.nivel === 'sin base' && sinbase.familias.total.posicion === null && sinbase.familias.total.extremo === null)
const neg = analizar(
  [fila(0, 'Local', 0, 1, 1.5, -1.5, -1.5, 0), fila(1, 'Visita', 1, 1, 1.5, 0, -1.5, 0), fila(2, 'Local', 0, 2, 2.0, -4, -4, 0), fila(3, 'Visita', 0, 1, 2.0, -6, -4, -2)],
  { proximo: { ...ctx.proximo!, nivelRival: 1.2 }, bin: 8 },
)
const tn = neg.familias.total
check('burbuja NEGATIVA: signo −, K −6, 2 partidos', eq([tn.actual!.signo, tn.actual!.k, tn.actual!.partidos], ['-', -6, 2]))
check('racha de derrotas: rival 1.2 ≤ mediana 1.5 → en zona, «cortarse»', tn.rival!.enZona === true && tn.riesgo!.motivos.some((m) => m.includes('cortarse')), tn)
check('burbuja −: rival 0.3 más flojo → tramo fuerte (+1) + racha (+1) = 2, ALTO', tn.rival!.tramo === 'fuerte' && tn.riesgo!.puntos === 2 && tn.riesgo!.nivel === 'alto', tn.riesgo)

console.log('\n— espina de la tarjeta (vectores en scripts/casos_espina_tarjeta.json) —')
const casosEspina = JSON.parse(readFileSync(join(aqui, 'casos_espina_tarjeta.json'), 'utf8')) as { signo: string; movimiento: { sigue: number; cero: number; cambio: number }; esperado: unknown }[]
for (const c of casosEspina) {
  const r = espinaTarjeta(c.signo, c.movimiento)
  check(`espina ${c.signo} ${JSON.stringify(c.movimiento)}`, JSON.stringify(r) === JSON.stringify(c.esperado), r)
}
check('sin burbuja o sin guía no hay espina de tarjeta', espinaTarjeta(null, { sigue: 1, cero: 0, cambio: 0 }) === null && espinaTarjeta('+', null) === null)

console.log(failed ? `\n${failed} FALLAS` : '\nTODO OK')
process.exit(failed ? 1 : 0)
