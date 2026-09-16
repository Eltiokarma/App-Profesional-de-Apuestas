// Verificación del espejo TS del reventón de burbuja (src/lib/burbuja.ts)
// contra los MISMOS vectores dorados que backend/test_burbuja.py.
// Ejecutar: npm run test:burbuja
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { analizarBurbujas, type ContextoBurbuja, type FilaK } from '../src/lib/burbuja'

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
check('nivel medio (bin 5) → mandan las específicas de la condición del próximo (visita)', out.mandan.tipo === 'especificas' && eq(out.mandan.familias, ['visita']), out.mandan)
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
check('K pico +: media 8.77 · mediana 7.5 · sin moda · min 5.5 · max 13.3', eq(hp.kPico, { media: 8.77, mediana: 7.5, moda: null, min: 5.5, max: 13.3 }), hp.kPico)
check('partidos +: media 2.33 · mediana 2 · moda 2', eq([hp.partidos.media, hp.partidos.mediana, hp.partidos.moda], [2.33, 2, 2]), hp.partidos)
check('nivel del rival que revienta +: media 2.33 · mediana 2.0 · moda 2.0', eq([hp.nivelRival.media, hp.nivelRival.mediana, hp.nivelRival.moda], [2.33, 2, 2]), hp.nivelRival)
const hn = t.historial.negativo!
check('historial −: n=2, K pico media 8 sin moda, nivel rival media 1.25', hn.n === 2 && hn.kPico.media === 8 && hn.kPico.moda === null && hn.nivelRival.media === 1.25, hn)
const a = t.actual!
check('burbuja abierta: + · K 22.1 · 6 partidos · aplica al próximo', eq([a.signo, a.k, a.partidos, a.aplicaAlProximo], ['+', 22.1, 6, true]), a)
check('posición: percentil 100 en K y en racha, K = 2.95× la mediana', eq(t.posicion, { percentilK: 100, percentilRacha: 100, kSobreMediana: 2.95 }), t.posicion)
check('rival próximo (2.6) en zona de reventón (mediana 2.0, distancia +0.6)', eq(t.rival, { nivelProximo: 2.6, medianaReventon: 2, distancia: 0.6, enZona: true }), t.rival)
const rg = t.riesgo!
check('riesgo MUY ALTO con 7 puntos y 5 motivos', rg.nivel === 'muy alto' && rg.puntos === 7 && rg.motivos.length === 5, rg)
check('confianza BAJA: muestra corta (3) y estabilidad inestable', rg.confianza === 'baja' && rg.confianzaMotivos.some((m) => m.includes('inestable')), rg.confianzaMotivos)

console.log('\n— familia local —')
const lo = out.familias.local
check('11 partidos de local', lo.partidosEnCondicion === 11)
check('burbuja abierta + K 9.5, 3 partidos, NO aplica al próximo', eq([lo.actual!.k, lo.actual!.partidos, lo.actual!.aplicaAlProximo], [9.5, 3, false]), lo.actual)
check('sin rival evaluado (otra condición) y motivo explícito', lo.rival === null && lo.riesgo!.motivos.some((m) => m.includes('otra condición')), lo.riesgo)
check('riesgo MEDIO con 2 puntos', lo.riesgo!.nivel === 'medio' && lo.riesgo!.puntos === 2, lo.riesgo)
check('historial − local: K pico 3.0 repetida → moda 3.0', lo.historial.negativo!.kPico.moda === 3)
check('percentil K 50', lo.posicion!.percentilK === 50, lo.posicion)

console.log('\n— familia visita —')
const vi = out.familias.visita
check('9 partidos de visita', vi.partidosEnCondicion === 9)
check('burbuja abierta + K 12.6 · 3 partidos', eq([vi.actual!.k, vi.actual!.partidos], [12.6, 3]))
check('riesgo MUY ALTO (7) y moda de partidos 1', vi.riesgo!.nivel === 'muy alto' && vi.historial.positivo!.partidos.moda === 1, vi.riesgo)

console.log('\n— estabilidad —')
const e = out.estabilidad
check('DT de 40 días + 7 movimientos → INESTABLE', e.grado === 'inestable', e)
check('dt.dias 40 · bajas 2 · movimientos 4+3', e.dt!.dias === 40 && e.bajas === 2 && eq(e.movimientos, { llegadas: 4, salidas: 3, ventanaDias: 120 }), e)
check('dueños/organización declarado SIN DATO', e.sinDato.some((s) => s.includes('dueños')))
const pl = ctx.plantilla!
const est = analizar(filas, { plantilla: { ...pl, entrenador: { nombre: 'Viejo', desde: '2024-01-01' }, revolucion: { llegadas: 1, salidas: 0, ventanaDias: 120 } } })
check('DT asentado + 1 movimiento → ESTABLE, confianza MEDIA (n=3)', est.estabilidad.grado === 'estable' && est.familias.total.riesgo!.confianza === 'media', est.estabilidad)
const trans = analizar(filas, { plantilla: { ...pl, entrenador: { nombre: 'Viejo', desde: '2024-01-01' }, revolucion: { llegadas: 2, salidas: 1, ventanaDias: 120 } } })
check('3 movimientos → EN TRANSICIÓN', trans.estabilidad.grado === 'en transición')
const vieja = analizar(filas, { plantilla: { ...pl, actualizadoEn: '2026-07-01T00:00:00Z' } })
check('plantilla de hace 77 días: aviso', vieja.estabilidad.motivos.some((m) => m.includes('77 días')), vieja.estabilidad.motivos)
const sd = analizar(filas, { plantilla: null })
check('sin plantilla → SIN DATO y confianza no pasa de MEDIA', sd.estabilidad.grado === 'sin dato' && sd.familias.total.riesgo!.confianza === 'media', sd.estabilidad)

console.log('\n— qué constante manda —')
check('bin 8 → globales', eq(analizar(filas, { bin: 8 }).mandan, { tipo: 'globales', familias: ['total'], motivo: 'nivel alto (bin 8): pesan más las constantes globales' }))
check('bin 1 → globales (nivel bajo)', analizar(filas, { bin: 1 }).mandan.tipo === 'globales')
const sp = analizar(filas, { proximo: null })
check('sin próximo y nivel medio → las dos específicas', eq(sp.mandan.familias, ['local', 'visita']))
check('sin próximo: el rival no puntúa y se dice', sp.familias.total.rival === null && sp.familias.total.riesgo!.motivos.some((m) => m.includes('sin próximo')))
const lejos = analizar(filas, { proximo: { ...ctx.proximo!, nivelRival: 1.5 } })
check('rival 1.5 fuera de zona → riesgo ALTO (5)', lejos.familias.total.rival!.enZona === false && lejos.familias.total.riesgo!.nivel === 'alto' && lejos.familias.total.riesgo!.puntos === 5, lejos.familias.total.riesgo)
const borde = analizar(filas, { proximo: { ...ctx.proximo!, nivelRival: 1.85 } })
check('tolerancia 0.15: rival 1.85 sigue en zona', borde.familias.total.rival!.enZona === true)

console.log('\n— bordes —')
const vacio = analizar([])
check('sin historia: nada abierto, sin reventones, sin riesgo', vacio.familias.total.actual === null && vacio.familias.total.reventones.length === 0 && vacio.familias.total.riesgo === null)
const cero = analizar([...filas, fila(0, 'Local', 1, 1, 2.0, 0, 0, 12.6)])
check('último partido en 0 → sin burbuja abierta, reventón registrado (6)', cero.familias.total.actual === null && cero.familias.total.reventones.length === 6)
const sinbase = analizar([fila(0, 'Local', 2, 0, 2.0, 4, 4, 0), fila(1, 'Visita', 1, 0, 2.0, 6.8, 4, 2.8)])
check('burbuja abierta sin reventones previos → SIN BASE', sinbase.familias.total.riesgo!.nivel === 'sin base' && sinbase.familias.total.posicion === null)
const neg = analizar(
  [fila(0, 'Local', 0, 1, 1.5, -1.5, -1.5, 0), fila(1, 'Visita', 1, 1, 1.5, 0, -1.5, 0), fila(2, 'Local', 0, 2, 2.0, -4, -4, 0), fila(3, 'Visita', 0, 1, 2.0, -6, -4, -2)],
  { proximo: { ...ctx.proximo!, nivelRival: 1.2 }, bin: 8 },
)
const tn = neg.familias.total
check('burbuja NEGATIVA: signo −, K −6, 2 partidos', eq([tn.actual!.signo, tn.actual!.k, tn.actual!.partidos], ['-', -6, 2]))
check('racha de derrotas: rival 1.2 ≤ mediana 1.5 → en zona, «cortarse»', tn.rival!.enZona === true && tn.riesgo!.motivos.some((m) => m.includes('cortarse')), tn)
check('K −6 supera la única K pico previa → 7 puntos, MUY ALTO', tn.riesgo!.puntos === 7 && tn.riesgo!.nivel === 'muy alto', tn.riesgo)

console.log(failed ? `\n${failed} FALLAS` : '\nTODO OK')
process.exit(failed ? 1 : 0)
