// Verificación de la capa de visualización de las K (src/lib/kview.ts).
// Ejecutar: npm run test:kview
import { condEtiquetas, puntosEtiquetados } from '../src/lib/kview'

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

console.log(failed ? `\n${failed} FALLAS` : '\nTODO OK')
process.exit(failed ? 1 : 0)
