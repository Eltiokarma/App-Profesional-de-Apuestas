// Verificación de la capa de visualización de las K (src/lib/kview.ts).
// Ejecutar: npm run test:kview
import { condEtiquetas, FUSED_KEY, marginQ, puntosEtiquetados, sequiaMargen, signedVal } from '../src/lib/kview'
import type { KSnapshot } from '../src/motor/types'

let failed = 0
function check(name: string, got: unknown, want: unknown) {
  const ok = JSON.stringify(got) === JSON.stringify(want)
  if (!ok) failed++
  console.log(`${ok ? '✓' : '✗ FALLA'} ${name}: got=${JSON.stringify(got)} want=${JSON.stringify(want)}`)
}

// ---- condición de referencia de las etiquetas ----
console.log('— condición de referencia —')
check('toggle Local manda sobre el rol', condEtiquetas('local', 'visita', false), 'local')
check('toggle Visita manda sobre el rol', condEtiquetas('visita', 'local', true), 'visita')
check('en Total manda el rol analizado', condEtiquetas('total', 'visita', true), 'visita')
check('sin rol, la del último partido', condEtiquetas('total', undefined, true), 'local')
check('toggle de cuotas en mayúsculas', condEtiquetas('LOCAL', 'visita', false), 'local')

// ---- los tres valores a la vista ----
// L V L V L  ·  índices 0..4, el último (4) es LOCAL
console.log('\n— tres puntos etiquetados —')
const esLocal = [true, false, true, false, true]
const local = (i: number) => esLocal[i]
const visita = (i: number) => !esLocal[i]

// valores todos distintos: último + los dos últimos de la condición
check(
  'condición visita: último (4) + visitas 3 y 1',
  puntosEtiquetados(5, visita, (i) => String(i)),
  [4, 3, 1],
)
// el último ya es de la condición → su valor se repetiría: se recorre atrás
check(
  'condición local: el último ya es local → toma 2 y 0',
  puntosEtiquetados(5, local, (i) => String(i)),
  [4, 2, 0],
)
// valores repetidos: se salta el que muestra el mismo número
check(
  'salta el punto cuyo valor repite uno ya elegido',
  puntosEtiquetados(5, visita, (i) => (i === 3 ? '4' : String(i))), // el 3 muestra lo mismo que el 4
  [4, 1],
)
// historia corta: devuelve lo que haya, sin inventar
check('un solo partido → una etiqueta', puntosEtiquetados(1, local, (i) => String(i)), [0])
check('sin partidos → sin etiquetas', puntosEtiquetados(0, local, (i) => String(i)), [])
check(
  'todos con el mismo valor → solo el último',
  puntosEtiquetados(5, local, () => '+5.0'),
  [4],
)

// ---- burbujas de sequía por margen ----
console.log('\n— margen: crece hasta que pasa —')
// L 1-0 (niv 2) · V 0-0 (niv 1) · L 2-1 (niv 3) · V 3-1 (niv 2) · L 0-2 (niv 1)
const partidos: [boolean, number, number, number][] = [[true, 1, 0, 2], [false, 0, 0, 1], [true, 2, 1, 3], [false, 3, 1, 2], [true, 0, 2, 1]]
const snapsM = partidos.map(([isLocal, gf, ga, rivalLevel]) => ({ isLocal, gf, ga, rivalLevel, fused: {} } as unknown as KSnapshot))
const sq = sequiaMargen(snapsM)
const serie = (t: 'vic1' | 'vic2' | 'der1' | 'der2', c: 'total' | 'local' | 'visita') => sq.map((s) => s.fused[FUSED_KEY[t][c]])
check('Gana 2+ total: crece 2→3→6, revienta con el 3-1, vuelve a crecer', serie('vic2', 'total'), [2, 3, 6, 0, 1])
check('Gana 1+ total: cada victoria revienta, el 0-0 y el 0-2 suman', serie('vic1', 'total'), [0, 1, 0, 0, 1])
check('Pierde 2+ total: crece hasta el 0-2 y ahí revienta', serie('der2', 'total'), [2, 3, 6, 8, 0])
check('Gana 2+ LOCAL: solo se mueve de local, conserva en visita', serie('vic2', 'local'), [2, 2, 5, 5, 6])
check('Pierde 1+ VISITA: los partidos de local no la tocan', serie('der1', 'visita'), [0, 1, 1, 3, 3])
check('q: «Gana 2+» crece hacia abajo, «Pierde 2+» hacia arriba, 0 si revienta',
  [marginQ('vic2', 1, 0, 2), marginQ('der2', 1, 0, 2), marginQ('vic2', 3, 1, 2), marginQ('der2', 0, 2, 1)], [-2, 2, 0, 0])
check('display: la sequía de victoria va negativa, la de derrota positiva', [signedVal('vic2', 6), signedVal('der2', 6)], [-6, 6])

console.log(failed ? `\n${failed} FALLAS` : '\nTODO OK')
process.exit(failed ? 1 : 0)
