// Verificación del Motor SAD contra MOTOR_SAD_EXTRACCION.md
// Ejecutar: npm run test:motor
import { K0, qValues, stepK } from '../src/motor/constants'
import { fuse, levelBin } from '../src/motor/discretizer'
import { teamEngine } from '../src/motor/engine'
import { computeTeamLevels } from '../src/motor/levels'
import { gapFor, mu, ptsRecent, senalDe } from '../src/motor/regression'
import type { TeamMatch } from '../src/motor/types'

let failed = 0
function check(name: string, got: unknown, want: unknown) {
  const ok =
    typeof got === 'number' && typeof want === 'number'
      ? Math.abs(got - want) < 1e-9
      : JSON.stringify(got) === JSON.stringify(want)
  if (!ok) failed++
  console.log(`${ok ? '✓' : '✗ FALLA'} ${name}: got=${JSON.stringify(got)} want=${JSON.stringify(want)}`)
}

// ---- §3.5 Ejemplo numérico oficial ----
// Equipo A (LOCAL) gana 3–1 a un rival de nivel 4, con estado previo
// k_positivo_local=5.0, k_negativo_local=−6.0, k_goles_anotado=8.0
console.log('— §3.5 ejemplo oficial —')
const prev = { ...K0, posLocal: 5.0, negLocal: -6.0, gA: 8.0 }
const { q, k } = stepK(prev, true, 3, 1, 4)
check('q_local = +8', q.local, 8)
check('q_negativo = 0', q.negativo, 0)
check('q_goles_anotado = +12', q.golesAnotado, 12)
check('q_goles_recibido = −4', q.golesRecibido, -4)
check('k_positivo_local 5→13', k.posLocal, 13)
check('k_negativo_local −6→0 (RESET)', k.negLocal, 0)
check('k_goles_anotado 8→20', k.gA, 20)
check('fusión k_local = +13', fuse(k).kLocal, 13)

// ---- §3.2 multiplicador visitante y q_negativo ----
console.log('— §3.2 visitante / derrota —')
const qv = qValues(false, 0, 2, 3) // visita, pierde 0-2 vs nivel 3
check('q_visita = 1.4·2·(−1)·3 = −8.4', qv.visita, -8.4)
check('q_negativo = 2·(−1)·3 = −6', qv.negativo, -6)
check('q_local = null (no aplica)', qv.local, null)
// k_goles_recibido acumula valor absoluto
const st2 = stepK({ ...K0, gR: 5 }, false, 0, 2, 3)
check('k_goles_recibido 5→11 (|−6|)', st2.k.gR, 11)
// empate resetea k_positivo y k_negativo
const st3 = stepK({ ...K0, pos: 9, neg: 0 }, true, 1, 1, 2)
check('empate resetea k_positivo', st3.k.pos, 0)
// visita: los k locales conservan valor
const st4 = stepK({ ...K0, posLocal: 7 }, false, 2, 0, 2)
check('k_positivo_local se conserva en visita', st4.k.posLocal, 7)
check('k_positivo_visita acumula 1.4·2·1·2=5.6', st4.k.posVisita, 5.6)

// ---- §3.6 Doble Oportunidad (k_dc): racha "sin perder" (1X) ----
console.log('— §3.6 doble oportunidad (k_dc) —')
// victoria local 2-0 vs nivel 3: q_dc = max(2·3, 0.5·3) = 6
const dc1 = stepK(K0, true, 2, 0, 3)
check('q_dc victoria 2-0 vs nivel 3 = 6', dc1.q.dc, 6)
check('k_dc 0→6', dc1.k.dc, 6)
check('k_dc_local 0→6', dc1.k.dcLocal, 6)
check('k_dc_visita se conserva (0) en local', dc1.k.dcVisita, 0)
// empate NO resetea: aporta el mínimo 0.5·nivel (dif=0)
const dc2 = stepK({ ...K0, dc: 6, dcLocal: 6 }, true, 1, 1, 2)
check('q_dc empate 1-1 vs nivel 2 = 0.5·2 = 1', dc2.q.dc, 1)
check('k_dc empate acumula 6→7', dc2.k.dc, 7)
check('k_dc_local empate acumula 6→7', dc2.k.dcLocal, 7)
// derrota resetea a 0 (aporte 0)
const dc3 = stepK({ ...K0, dc: 7, dcLocal: 7 }, true, 0, 1, 2.5)
check('q_dc derrota = 0', dc3.q.dc, 0)
check('k_dc derrota RESET → 0', dc3.k.dc, 0)
check('k_dc_local derrota RESET → 0', dc3.k.dcLocal, 0)
// visita: SIN multiplicador ×1.4 (roadmap: q_dc = dif·nivel). dcLocal se conserva.
const dc4 = stepK({ ...K0, dcLocal: 5 }, false, 1, 0, 2)
check('q_dc visita 1-0 vs nivel 2 = 2 (sin ×1.4)', dc4.q.dc, 2)
check('k_dc_visita 0→2', dc4.k.dcVisita, 2)
check('k_dc_local se conserva (5) en visita', dc4.k.dcLocal, 5)
check('fusión k_dc = acumulador tal cual', fuse(dc4.k).kDc, 2)
// empate de visita: mínimo 0.5·nivel, tampoco lleva ×1.4
const dc5 = stepK(K0, false, 2, 2, 4)
check('q_dc empate visita vs nivel 4 = 0.5·4 = 2', dc5.q.dc, 2)

// ---- §2 niveles: regla retroactiva y fórmula ----
console.log('— §2 niveles —')
const mk = (i: number, gf: number, ga: number): TeamMatch => ({ fixtureId: i, t: i, rival: 'x', isLocal: true, gf, ga })
const shortHist = Array.from({ length: 7 }, (_, i) => mk(i, 1, 0))
check('con <20 partidos todos 0.5', computeTeamLevels(shortHist).map((r) => r.level), Array(7).fill(0.5))
// 20 victorias 2-0: P=3, últimos 5: G=(5·2)/(5·2)=1 → nivel=5? no: G=dg/tg=10/10=1 → 3+1+1=5
// rango doc 0.5–3.5 es "típico", la fórmula no recorta. Verificamos la fórmula exacta:
const h20 = Array.from({ length: 20 }, (_, i) => mk(i, 2, 0))
const lv20 = computeTeamLevels(h20)
check('20 victorias 2-0 → nivel P+G+1 = 3+1+1 = 5 en todas (retroactivo)', [lv20[0].level, lv20[19].level], [5, 5])
const hMix = [...Array.from({ length: 20 }, (_, i) => mk(i, 1, 1)), mk(20, 0, 3)]
const lvMix = computeTeamLevels(hMix)
// partido 21: ventana = 19 empates + 1 derrota → P=19/20=0.95; u5: 4 empates+derrota dg=−3 tg=4+3+...
// u5 goles: 4×(1+1)=8 +3 =11? gf-ga: 4×0 + (0-3)=−3; gf+ga: 4×2+3=11 → G=−3/11
check('nivel partido 21 = 0.95 − 3/11 + 1', lvMix[20].level.toFixed(4), (0.95 - 3 / 11 + 1).toFixed(4))

// ---- §4.1 bins fijos v6 ----
console.log('— §4.1 bins —')
check('0.5 → bin 0 Sin datos', levelBin(0.5), { bin: 0, label: 'Sin datos' })
check('2.2 → bin 5 Promedio', levelBin(2.2), { bin: 5, label: 'Promedio' })
check('2.7 → bin 7 Fuerte', levelBin(2.7), { bin: 7, label: 'Fuerte' })
check('3.3 → bin 9 Élite', levelBin(3.3), { bin: 9, label: 'Élite' })

// ---- §5 Ley de la Regresión al Nivel ----
console.log('— §5 regresión al nivel —')
check('μ(2, 2, 1) = 1.110+1.372−1.338+0.422', mu(2, 2, 1), 1.11 + 0.686 * 2 - 0.669 * 2 + 0.422)
check('μ recorta a [0,3] por arriba', mu(3.8, 0.5, 1), 3)
check('μ recorta a [0,3] por abajo', mu(0.5, 3.5, 0), 0)
check('forma reciente: 5 victorias → 3.0', ptsRecent(Array.from({ length: 5 }, (_, i) => mk(i, 2, 0))), 3)
check('forma reciente: <5 partidos → null', ptsRecent([mk(0, 1, 0)]), null)
check('señal |gap|>0.5 → fuerte', senalDe(0.61), 'fuerte')
check('señal 0.3–0.5 → leve', senalDe(-0.4), 'leve')
check('señal <0.3 → equilibrio', senalDe(0.1), 'equilibrio')
const gBet = gapFor('bet')!
console.log(`  bet: nivel=${gBet.nivel.toFixed(2)} recientes=${gBet.ptsRecientes} esperados=${gBet.ptsEsperados.toFixed(2)} gap=${gBet.gap?.toFixed(2)} (${gBet.senal}/${gBet.tendencia})`)
if (gBet.gap == null || !['fuerte', 'leve', 'equilibrio'].includes(gBet.senal!)) {
  failed++
  console.log('  ✗ gap incompleto')
}

// ---- pipeline completo: sanidad sobre datos sintéticos ----
console.log('— pipeline sintético —')
for (const id of ['bet', 'sev', 'rma', 'liv', 'int']) {
  const e = teamEngine(id)!
  const last = e.snaps[e.snaps.length - 1]
  const inv = e.snaps.some((s) => (s.k.pos !== 0 && s.k.neg !== 0) || s.k.gR < 0)
  console.log(
    `  ${id}: ${e.snaps.length} partidos · nivel=${e.level.toFixed(2)} (${e.binLabel}, bin ${e.bin}) · ` +
      `K=${last.fused.k.toFixed(1)} K_local=${last.fused.kLocal.toFixed(1)} K_gA=${last.fused.golesAnotado.toFixed(1)} K_gR=${last.fused.golesRecibido.toFixed(1)}` +
      (inv ? '  ⚠ INVARIANTE VIOLADA' : ''),
  )
  if (inv) failed++
  if (e.snaps.length < 20) {
    failed++
    console.log('  ✗ historia insuficiente')
  }
}
// determinismo
const a = teamEngine('bet')!.snaps[30].fused.k
const b = teamEngine('bet')!.snaps[30].fused.k
check('determinista (memo)', a, b)

console.log(failed ? `\n${failed} FALLAS` : '\nTODO OK')
process.exit(failed ? 1 : 0)
