// Espejo TS de las otras burbujas: tiene que dar EXACTAMENTE lo que el Python
// (backend/analisis/familias.py) dejó en scripts/casos_familias.json.
import { readFileSync } from 'node:fs'
import { describirFamilias } from '../src/lib/familias'

const casos = JSON.parse(readFileSync(new URL('./casos_familias.json', import.meta.url), 'utf8'))
let fallos = 0
const ordenar = (x: unknown): unknown =>
  Array.isArray(x) ? x.map(ordenar)
    : x && typeof x === 'object' ? Object.fromEntries(Object.keys(x as object).sort().map((k) => [k, ordenar((x as Record<string, unknown>)[k])]))
    : x
for (const c of casos) {
  const got = JSON.stringify(ordenar(describirFamilias(c.filas, c.condicion, c.nombre)))
  const exp = JSON.stringify(ordenar(c.esperado))
  if (got !== exp) {
    fallos++
    console.log(`FALLA ${c.nombre}\n  TS:     ${got.slice(0, 600)}\n  Python: ${exp.slice(0, 600)}`)
  } else console.log(`OK  ${c.nombre}`)
}
console.log(fallos ? `\n${fallos} FALLAS` : '\nTODO OK')
process.exit(fallos ? 1 : 0)
