// Auditoría de la vista de teléfono: recorre TODAS las pantallas de la app en
// modo demo a un ancho dado, guarda una captura de cada una y delata cualquier
// elemento que se salga del ancho de la pantalla (desborde horizontal), salvo
// los que scrollean a propósito. Un cambio de layout que rompa el móvil se ve
// acá antes que en el teléfono de alguien.
//
//   npm run build && VITE_DATA_SOURCE=mock npx vite preview --port 4173 &
//   npm i --no-save playwright@1.56.0     # sin tocar package.json; los browsers
//                                         # ya están en PLAYWRIGHT_BROWSERS_PATH
//   node scripts/audit-movil.mjs /tmp/capturas 360 2400   # (carpeta, ancho, alto)
//   node scripts/audit-movil.mjs /tmp/capturas 390 844
//
// Imprime un JSON por pantalla: `overflow` (la página scrollea de lado) y `bad`
// (los elementos que se pasan). Alto grande = captura de la pantalla entera.
import { chromium } from 'playwright'
const OUT = process.argv[2]
const W = parseInt(process.argv[3] || '390', 10), H = parseInt(process.argv[4] || '844', 10)
const b = await chromium.launch()
const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2, isMobile: true, hasTouch: true })
const p = await ctx.newPage()
const report = []
async function medir(nombre, full = true) {
  await p.waitForTimeout(700)
  const r = await p.evaluate(() => {
    const iw = window.innerWidth
    const sw = document.documentElement.scrollWidth
    const bad = []
    for (const el of document.querySelectorAll('body *')) {
      const rc = el.getBoundingClientRect()
      if (rc.width === 0) continue
      if (rc.right > iw + 1 || rc.left < -1) {
        const cs = getComputedStyle(el)
        if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') continue
        // ignorar hijos de contenedores que scrollean horizontalmente a propósito
        let q = el.parentElement, dentro = false
        while (q) { const c = getComputedStyle(q); if (c.overflowX === 'auto' || c.overflowX === 'scroll') { dentro = true; break } q = q.parentElement }
        if (dentro) continue
        bad.push({ tag: el.tagName, txt: (el.textContent || '').trim().slice(0, 40), left: Math.round(rc.left), right: Math.round(rc.right), w: Math.round(rc.width) })
        if (bad.length >= 6) break
      }
    }
    return { iw, sw, overflow: sw > iw, bad }
  })
  report.push({ nombre, ...r })
  await p.screenshot({ path: `${OUT}/${nombre}.png`, fullPage: full })
}
async function nav(label) {
  await p.locator('nav button', { hasText: label }).first().click()
}
await p.goto('http://localhost:4173/', { waitUntil: 'networkidle' })
await medir('01-partidos')
// seleccionar el partido terminado (Liverpool - Chelsea)
await p.locator('button', { hasText: 'Liverpool' }).first().click()
await medir('02-partidos-seleccionado', false)
await nav('Cuotas'); await medir('03-cuotas')
await nav('Burbujas'); await medir('04-burbujas')
await nav('Análisis'); await medir('05-analisis-bloques')
for (const t of ['Bloque F', 'Matchup', 'Lectura SAD', 'Teorema del Echado', 'Calendario', 'Timeline', 'Documentos']) {
  const btn = p.locator('button:not([disabled])', { hasText: t }).first()
  if (await btn.count()) { await btn.click({ timeout: 5000 }).catch(() => {}); await medir('05-analisis-' + t.toLowerCase().replace(/[^a-z]/g, '')) }
}
// el detalle del veredicto
const det = p.locator('button', { hasText: 'Detalle' }).first()
if (await det.count()) { await det.click({ timeout: 5000 }).catch(() => {}); await medir('05-analisis-veredicto') }
await nav('Skills'); await medir('06-skills')
await nav('Stats'); await medir('07-stats')
await nav('Aprende'); await medir('08-aprende')
// página de equipo vía buscador
await nav('Partidos')
const buscador = p.locator('input[placeholder*="Buscar equipo"]').first()
await buscador.fill('Betis'); await p.waitForTimeout(500)
const res = p.locator('text=Real Betis').first()
if (await res.count()) { await res.click(); await medir('09-equipo') }
// página de liga: el nombre de la liga en la cabecera de cada grupo de Partidos
await nav('Partidos')
const liga = p.locator('button[title^="Ver información"]').first()
if (await liga.count()) { await liga.click({ timeout: 5000 }).catch(() => {}); await medir('10-liga') }
console.log(JSON.stringify(report, null, 1))
await b.close()
