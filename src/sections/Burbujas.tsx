import { LEVELS, TEAMS } from '../data'
import type { KCondKey, KTypeKey, Match } from '../data/types'
import type { FusedK, KSnapshot } from '../motor/types'
import { loadBurbujas, type BurbujasData } from '../services/appdata'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  m: Match
  isMobile: boolean
}

const WINDOW = 12 // últimos N partidos visibles en el timeline

const FUSED_KEY: Record<KTypeKey, Record<KCondKey, keyof FusedK>> = {
  res: { total: 'k', local: 'kLocal', visita: 'kVisita' },
  ga: { total: 'golesAnotado', local: 'golesLocalAnotado', visita: 'golesVisitaAnotado' },
  gr: { total: 'golesRecibido', local: 'golesLocalRecibido', visita: 'golesVisitaRecibido' },
}

/** Valor con signo de display: para goles recibidos la racha alta es desfavorable (abajo, rojo). */
const signedVal = (kType: KTypeKey, v: number) => (kType === 'gr' ? -v : v)

const fmtK = (v: number) => (Math.abs(v) >= 20 ? v.toFixed(0) : v.toFixed(1))
const signFmt = (v: number) => (v > 0 ? '+' + fmtK(v) : fmtK(v))

function binBadge(bin: number): { color: string; soft: string } {
  if (bin >= 8) return { color: 'var(--up)', soft: 'var(--up-soft)' }
  if (bin >= 6) return { color: 'var(--accent)', soft: 'var(--accent-soft)' }
  if (bin >= 4) return { color: 'var(--mark)', soft: 'var(--mark-soft)' }
  if (bin >= 1) return { color: 'var(--down)', soft: 'var(--down-soft)' }
  return { color: 'var(--t3)', soft: 'var(--bg3)' }
}

/** Racha activa: partidos desde el último reseteo de la K seleccionada. */
function streakLen(snaps: KSnapshot[], key: keyof FusedK): number {
  let n = 0
  for (let i = snaps.length - 1; i >= 0 && snaps[i].fused[key] !== 0; i--) n++
  return n
}

/** Último aporte q a la K seleccionada (último partido de la condición). */
function lastQ(snaps: KSnapshot[], kType: KTypeKey, kCond: KCondKey): number | null {
  for (let i = snaps.length - 1; i >= 0; i--) {
    const s = snaps[i]
    if (kCond === 'local' && !s.isLocal) continue
    if (kCond === 'visita' && s.isLocal) continue
    if (kType === 'ga') return s.q.golesAnotado
    if (kType === 'gr') return s.q.golesRecibido
    return s.isLocal ? s.q.local : s.q.visita
  }
  return null
}

interface Bubble {
  x: number
  y: number
  r: number
  color: string
  filled: boolean
  dim: boolean
  isLast: boolean
  text: string
  title: string
}

function buildBubbles(snaps: KSnapshot[], kType: KTypeKey, kCond: KCondKey, maxAbs: number): Bubble[] {
  const key = FUSED_KEY[kType][kCond]
  const win = snaps.slice(-WINDOW)
  const total = snaps.length
  return win.map((s, i) => {
    const v = s.fused[key]
    const sv = signedVal(kType, v)
    const reset = v === 0
    const inCond = kCond === 'total' || (kCond === 'local') === s.isLocal
    const r = reset ? 4.5 : 8 + 20 * Math.sqrt(Math.abs(sv) / maxAbs)
    const qc = kType === 'ga' ? s.q.golesAnotado : kType === 'gr' ? s.q.golesRecibido : s.isLocal ? s.q.local : s.q.visita
    const rv = TEAMS[s.rival]
    return {
      x: 7 + (win.length === 1 ? 43 : (i / (win.length - 1)) * 86),
      y: 50 - (sv / maxAbs) * 32,
      r,
      color: reset ? 'var(--t3)' : sv > 0 ? 'var(--up)' : 'var(--down)',
      filled: !reset,
      dim: !inCond && !reset,
      isLast: i === win.length - 1,
      text: !reset && r >= 13 ? signFmt(sv) : '',
      title:
        `#${total - win.length + i + 1} · ${s.isLocal ? 'vs' : 'en'} ${rv ? rv.short : s.rival} ${s.gf}-${s.ga}` +
        ` · rival nivel ${s.rivalLevel.toFixed(2)}` +
        (inCond ? ` · q ${qc == null ? '—' : signFmt(qc)}` : ' · no actualiza (otra condición)') +
        ` · K ${fmtK(v)}${reset ? ' (reset)' : ''}`,
    }
  })
}

function TeamPanel({ eng, teamId, role, kType, kCond, maxAbs }: { eng: BurbujasData; teamId: string; role: string; kType: KTypeKey; kCond: KCondKey; maxAbs: number }) {
  const T = TEAMS[teamId]
  const key = FUSED_KEY[kType][kCond]
  const bubbles = buildBubbles(eng.snaps, kType, kCond, maxAbs)
  const cur = eng.snaps.length ? eng.snaps[eng.snaps.length - 1].fused[key] : 0
  const sv = signedVal(kType, cur)
  const racha = streakLen(eng.snaps, key)
  const q = lastQ(eng.snaps, kType, kCond)
  const bb = binBadge(eng.bin)
  const curColor = cur === 0 ? 'var(--t3)' : sv > 0 ? 'var(--up)' : 'var(--down)'

  return (
    <section style={{ padding: 18, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
        <span style={{ width: 28, height: 28, borderRadius: '50%', background: T.color, color: T.fg, display: 'flex', alignItems: 'center', justifyContent: 'center', font: '700 10px var(--mono)' }}>{T.short}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ font: '700 13.5px var(--sans)' }}>{T.name}</div>
          <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>{role} · nivel {eng.level.toFixed(2)}</div>
        </div>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: bb.soft, color: bb.color, font: '700 9.5px var(--mono)', letterSpacing: '.3px', flexShrink: 0 }}>{eng.binLabel} · {eng.bin}</span>
      </div>
      <div style={{ position: 'relative', height: 210, marginTop: 6, borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', left: 0, right: 0, top: '50%', height: 1, background: 'var(--line)' }}></div>
        <div style={{ position: 'absolute', left: 8, top: 8, font: '500 9px var(--mono)', color: 'var(--up)' }}>+ favorable</div>
        <div style={{ position: 'absolute', left: 8, bottom: 8, font: '500 9px var(--mono)', color: 'var(--down)' }}>− desfavorable</div>
        {bubbles.map((b, i) => (
          <div
            key={i}
            title={b.title}
            style={{
              position: 'absolute',
              left: `${b.x}%`,
              top: `${b.y}%`,
              width: b.r * 2,
              height: b.r * 2,
              marginLeft: -b.r,
              marginTop: -b.r,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              font: `700 ${Math.max(8, b.r * 0.55)}px var(--mono)`,
              color: '#fff',
              background: b.filled ? b.color : 'transparent',
              border: `2px solid ${b.color}`,
              opacity: b.dim ? 0.35 : 1,
              boxShadow: b.isLast && b.filled ? `0 0 0 3px color-mix(in oklch,${b.color},transparent 72%)` : 'none',
              transition: 'all .25s',
              zIndex: b.isLast ? 2 : 1,
            }}
          >
            {b.text}
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5, font: '500 9px var(--mono)', color: 'var(--t3)' }}>
        <span>hace {Math.min(WINDOW, eng.snaps.length)} partidos</span>
        <span>último</span>
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
        <div style={{ flex: 1, padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
          <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)', marginBottom: 2 }}>K ACTUAL</div>
          <div style={{ font: '700 16px var(--mono)', color: curColor, fontVariantNumeric: 'tabular-nums' }}>{signFmt(sv)}</div>
        </div>
        <div style={{ flex: 1, padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
          <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)', marginBottom: 2 }}>RACHA</div>
          <div style={{ font: '700 16px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{racha} <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>partidos</span></div>
        </div>
        <div style={{ flex: 1, padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
          <div style={{ font: '500 9px var(--mono)', color: 'var(--t3)', marginBottom: 2 }}>ÚLTIMO q</div>
          <div style={{ font: '700 16px var(--mono)', color: q == null ? 'var(--t3)' : q > 0 ? 'var(--up)' : q < 0 ? 'var(--down)' : 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>{q == null ? '—' : signFmt(q)}</div>
        </div>
      </div>
    </section>
  )
}

export function Burbujas({ store, m, isMobile }: Props) {
  const { s } = store
  const H = TEAMS[m.home]
  const A = TEAMS[m.away]
  const gridBurbujas = isMobile ? '1fr' : '1fr 1fr 280px'

  // constantes K + niveles vía el contrato (/constantes, /niveles)
  const engData = useAsync(async () => {
    const [h, a] = await Promise.all([loadBurbujas(m.home), loadBurbujas(m.away)])
    return { h, a }
  }, m.id)
  const engH = engData.data?.h ?? null
  const engA = engData.data?.a ?? null

  const typeOpts = ([['res', 'Resultado'], ['ga', 'Goles anotados'], ['gr', 'Goles recibidos']] as [KTypeKey, string][]).map(([k, l]) => ({
    key: k, label: l, bg: s.kType === k ? 'var(--bg3)' : 'transparent', fg: s.kType === k ? 'var(--t1)' : 'var(--t2)',
  }))
  const condOpts = ([['total', 'Total'], ['local', 'Local'], ['visita', 'Visita']] as [KCondKey, string][]).map(([k, l]) => ({
    key: k, label: l, bg: s.kCond === k ? 'var(--bg3)' : 'transparent', fg: s.kCond === k ? 'var(--t1)' : 'var(--t2)',
  }))
  const modelOpts = (['auto', 'global', 'liga'] as const).map((k) => ({
    key: k, label: k === 'auto' ? 'Auto' : k === 'global' ? 'Global' : 'Liga',
    bg: s.model === k ? 'var(--accent-soft)' : 'transparent', fg: s.model === k ? 'var(--accent)' : 'var(--t2)',
  }))

  // escala común para comparar local vs visitante de un vistazo
  const key = FUSED_KEY[s.kType][s.kCond]
  let maxAbs = 0.001
  for (const eng of [engH, engA]) {
    if (!eng) continue
    for (const sn of eng.snaps.slice(-WINDOW)) maxAbs = Math.max(maxAbs, Math.abs(sn.fused[key]))
  }

  // tabla del panel lateral: toda la foto del motor para ambos equipos
  const kv = (eng: BurbujasData | null, kk: keyof FusedK) => (eng && eng.snaps.length ? eng.snaps[eng.snaps.length - 1].fused[kk] : 0)
  const kColor = (v: number, inverse: boolean) => (v === 0 ? 'var(--t3)' : (inverse ? v < 0 : v > 0) ? 'var(--up)' : 'var(--down)')
  const valueRows: { label: string; hv: string; av: string; hc: string; ac: string }[] = [
    { label: 'Nivel (continuo)', hv: engH ? engH.level.toFixed(2) : '—', av: engA ? engA.level.toFixed(2) : '—', hc: 'var(--t1)', ac: 'var(--t1)' },
    ...([['K resultado', 'k', false], ['K local', 'kLocal', false], ['K visita', 'kVisita', false], ['K goles anot.', 'golesAnotado', false], ['K goles rec.', 'golesRecibido', true]] as [string, keyof FusedK, boolean][]).map(
      ([label, kk, inv]) => {
        const hvN = kv(engH, kk)
        const avN = kv(engA, kk)
        const disp = (v: number) => (inv ? (v === 0 ? '0.0' : '−' + fmtK(v)) : signFmt(v))
        return { label, hv: disp(hvN), av: disp(avN), hc: kColor(inv ? -hvN : hvN, false), ac: kColor(inv ? -avN : avN, false) }
      },
    ),
  ]

  const nx = [
    { when: 'J33', name: 'Getafe', lv: 'medio' },
    { when: 'J34', name: 'Real Madrid', lv: 'elite' },
    { when: 'J35', name: 'Las Palmas', lv: 'bajo' },
  ]
  const nextThree = nx.map((n) => {
    const lv = LEVELS.find((l) => l.k === n.lv)!
    return { when: n.when, name: n.name, lvLabel: lv.label, lvColor: lv.color, lvSoft: lv.soft }
  })

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, marginBottom: 18, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ margin: 0, font: '800 22px var(--sans)', letterSpacing: '-.3px' }}>Burbujas · Constantes K</h1>
          <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>Motor SAD · q = dif × res × nivel del rival · la K crece con la racha y se resetea al cambiar el signo</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            {typeOpts.map((c) => (
              <button key={c.key} onClick={store.setKType(c.key)} style={{ padding: '7px 13px', border: 0, borderRadius: 7, cursor: 'pointer', background: c.bg, color: c.fg, font: '600 11.5px var(--sans)' }}>{c.label}</button>
            ))}
          </div>
          <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            {condOpts.map((c) => (
              <button key={c.key} onClick={store.setKCond(c.key)} style={{ padding: '7px 13px', border: 0, borderRadius: 7, cursor: 'pointer', background: c.bg, color: c.fg, font: '600 11.5px var(--sans)' }}>{c.label}</button>
            ))}
          </div>
          <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            {modelOpts.map((md) => (
              <button key={md.key} onClick={store.setModel(md.key)} style={{ padding: '7px 11px', border: 0, borderRadius: 7, cursor: 'pointer', background: md.bg, color: md.fg, font: '600 11.5px var(--mono)' }}>{md.label}</button>
            ))}
          </div>
        </div>
      </div>

      {engData.error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--down)', flexShrink: 0 }}></span>
          <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudieron cargar las constantes K: {engData.error}</span>
          <button onClick={engData.reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)', flexShrink: 0 }}>Reintentar</button>
        </div>
      )}
      {engData.loading && (
        <div style={{ display: 'grid', gridTemplateColumns: gridBurbujas, gap: 14 }}>
          <div className="sad-sk" style={{ height: 360 }}></div>
          <div className="sad-sk" style={{ height: 360 }}></div>
          <div className="sad-sk" style={{ height: 360 }}></div>
        </div>
      )}
      {!engData.loading && !engData.error && (
      <div style={{ display: 'grid', gridTemplateColumns: gridBurbujas, gap: 14 }}>
        {engH && <TeamPanel eng={engH} teamId={m.home} role={'Local · modelo ' + s.model} kType={s.kType} kCond={s.kCond} maxAbs={maxAbs} />}
        {engA && <TeamPanel eng={engA} teamId={m.away} role={'Visitante · modelo ' + s.model} kType={s.kType} kCond={s.kCond} maxAbs={maxAbs} />}

        <aside style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 2 }}>Valores · Motor SAD</div>
            <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 10 }}>K fusionadas (k⁺ + k⁻) tras el último partido</div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 0, marginBottom: 2 }}>
              <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', minWidth: 52, textAlign: 'right' }}>{H.short}</span>
              <span style={{ font: '600 9px var(--mono)', color: 'var(--t3)', minWidth: 52, textAlign: 'right' }}>{A.short}</span>
            </div>
            {valueRows.map((r, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', borderBottom: '1px solid var(--line)' }}>
                <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t2)', flex: 1 }}>{r.label}</span>
                <span style={{ font: '600 12px var(--mono)', color: r.hc, minWidth: 52, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{r.hv}</span>
                <span style={{ font: '600 12px var(--mono)', color: r.ac, minWidth: 52, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{r.av}</span>
              </div>
            ))}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginTop: 10 }}>
              {[{ id: m.home, eng: engH }, { id: m.away, eng: engA }].map(({ id, eng }) =>
                eng ? (
                  <div key={id} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 32 }}>{TEAMS[id].short}</span>
                    <span style={{ padding: '3px 9px', borderRadius: 6, background: binBadge(eng.bin).soft, color: binBadge(eng.bin).color, font: '700 9.5px var(--mono)', letterSpacing: '.3px' }}>
                      {eng.binLabel} · bin {eng.bin}
                    </span>
                    <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>{eng.snaps.length} partidos</span>
                  </div>
                ) : null,
              )}
            </div>
          </section>
          <section style={{ padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 12px var(--sans)', marginBottom: 4 }}>Próximos 3 · {H.name}</div>
            <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginBottom: 12 }}>Calendario por nivel</div>
            {nextThree.map((n, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 0', borderBottom: '1px solid var(--line)' }}>
                <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 36 }}>{n.when}</span>
                <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1 }}>{n.name}</span>
                <span style={{ padding: '3px 9px', borderRadius: 6, background: n.lvSoft, color: n.lvColor, font: '700 9.5px var(--mono)', letterSpacing: '.3px' }}>{n.lvLabel}</span>
              </div>
            ))}
          </section>
        </aside>
      </div>
      )}
    </div>
  )
}
