import { LEVELS, TEAMS } from '../data'
import type { KCondKey, KTypeKey, Match } from '../data/types'
import { KLineChart, KLineLegend } from '../components/KLineChart'
import { binBadge, FUSED_KEY, K_TYPE_GROUPS, K_WINDOW_OPTS, lastQ, signedVal, signFmt, streakLen } from '../lib/kview'
import type { FusedK } from '../motor/types'
import { loadBurbujas, type BurbujasData } from '../services/appdata'
import { useAsync } from '../services/useAsync'
import type { SadStore } from '../store'

interface Props {
  store: SadStore
  m: Match
  isMobile: boolean
}

function TeamPanel({ eng, teamId, role, kType, kCond, maxAbs, chartWindow }: { eng: BurbujasData; teamId: string; role: string; kType: KTypeKey; kCond: KCondKey; maxAbs: number; chartWindow: number }) {
  const T = TEAMS[teamId]
  const key = FUSED_KEY[kType][kCond]
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

      {/* picos acumulados: la K crece con la racha y cae a cero al resetearse */}
      <div style={{ marginTop: 6, borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)', padding: 6 }}>
        <KLineChart snaps={eng.snaps} kType={kType} kCond={kCond} maxAbs={maxAbs} window={chartWindow} />
      </div>
      <KLineLegend />

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

  const condOpts = ([['total', 'Total'], ['local', 'Local'], ['visita', 'Visita']] as [KCondKey, string][]).map(([k, l]) => ({
    key: k, label: l, bg: s.kCond === k ? 'var(--bg3)' : 'transparent', fg: s.kCond === k ? 'var(--t1)' : 'var(--t2)',
  }))
  const windowOpts = K_WINDOW_OPTS.map(([n, l]) => ({
    key: n, label: l, bg: s.kWindow === n ? 'var(--bg3)' : 'transparent', fg: s.kWindow === n ? 'var(--t1)' : 'var(--t2)',
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
    for (const sn of eng.snaps.slice(-s.kWindow)) maxAbs = Math.max(maxAbs, Math.abs(sn.fused[key]))
  }

  // tabla del panel lateral: toda la foto del motor para ambos equipos
  const kv = (eng: BurbujasData | null, kk: keyof FusedK) => (eng && eng.snaps.length ? eng.snaps[eng.snaps.length - 1].fused[kk] : 0)
  const kColor = (v: number) => (v === 0 ? 'var(--t3)' : v > 0 ? 'var(--up)' : 'var(--down)')
  const fmt = (v: number) => signFmt(v)
  const valueRows: { label: string; hv: string; av: string; hc: string; ac: string }[] = [
    { label: 'Nivel (continuo)', hv: engH ? engH.level.toFixed(2) : '—', av: engA ? engA.level.toFixed(2) : '—', hc: 'var(--t1)', ac: 'var(--t1)' },
    ...([['K resultado', 'k', false], ['K local', 'kLocal', false], ['K visita', 'kVisita', false], ['K goles anot.', 'golesAnotado', false], ['K goles rec.', 'golesRecibido', true], ['K doble op.', 'kDc', false]] as [string, keyof FusedK, boolean][]).map(
      ([label, kk, inv]) => {
        const hvN = kv(engH, kk)
        const avN = kv(engA, kk)
        const disp = (v: number) => (inv ? (v === 0 ? '0.0' : '−' + Math.abs(v).toFixed(1)) : fmt(v))
        return { label, hv: disp(hvN), av: disp(avN), hc: kColor(inv ? -hvN : hvN), ac: kColor(inv ? -avN : avN) }
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
          <p style={{ margin: '5px 0 0', font: '500 12.5px var(--sans)', color: 'var(--t2)' }}>Motor SAD · picos acumulados: la K crece con la racha y se resetea al cambiar el signo</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap' }}>
          {/* tipo de K: agrupado (Resultado · Goles · Mercados · Márgenes) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3, padding: 6, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            {K_TYPE_GROUPS.map((g) => (
              <div key={g.label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', width: 56, textTransform: 'uppercase', letterSpacing: '.4px', flexShrink: 0 }}>{g.label}</span>
                <div style={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  {g.opts.map(([k, l]) => (
                    <button key={k} onClick={store.setKType(k)} style={{ padding: '4px 8px', border: 0, borderRadius: 6, cursor: 'pointer', background: s.kType === k ? 'var(--bg3)' : 'transparent', color: s.kType === k ? 'var(--t1)' : 'var(--t2)', font: '600 10.5px var(--sans)' }}>{l}</button>
                  ))}
                </div>
              </div>
            ))}
          </div>
          {/* condición · ventana · modelo */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              {condOpts.map((c) => (
                <button key={c.key} onClick={store.setKCond(c.key)} style={{ padding: '6px 12px', border: 0, borderRadius: 7, cursor: 'pointer', background: c.bg, color: c.fg, font: '600 11px var(--sans)' }}>{c.label}</button>
              ))}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
              <span style={{ font: '600 8.5px var(--mono)', color: 'var(--t3)', textTransform: 'uppercase', letterSpacing: '.4px' }}>Ver</span>
              <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                {windowOpts.map((c) => (
                  <button key={c.key} onClick={store.setWindow(c.key)} style={{ padding: '6px 12px', border: 0, borderRadius: 7, cursor: 'pointer', background: c.bg, color: c.fg, font: '600 11px var(--sans)' }}>{c.label}</button>
                ))}
              </div>
              <div style={{ display: 'flex', padding: 4, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                {modelOpts.map((md) => (
                  <button key={md.key} onClick={store.setModel(md.key)} style={{ padding: '6px 10px', border: 0, borderRadius: 7, cursor: 'pointer', background: md.bg, color: md.fg, font: '600 11px var(--mono)' }}>{md.label}</button>
                ))}
              </div>
            </div>
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
          <div className="sad-sk" style={{ height: 380 }}></div>
          <div className="sad-sk" style={{ height: 380 }}></div>
          <div className="sad-sk" style={{ height: 380 }}></div>
        </div>
      )}
      {!engData.loading && !engData.error && (
      <div style={{ display: 'grid', gridTemplateColumns: gridBurbujas, gap: 14 }}>
        {engH && <TeamPanel eng={engH} teamId={m.home} role={'Local · modelo ' + s.model} kType={s.kType} kCond={s.kCond} maxAbs={maxAbs} chartWindow={s.kWindow} />}
        {engA && <TeamPanel eng={engA} teamId={m.away} role={'Visitante · modelo ' + s.model} kType={s.kType} kCond={s.kCond} maxAbs={maxAbs} chartWindow={s.kWindow} />}

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
                    <button onClick={() => store.openTeam(id)} style={{ marginLeft: 'auto', padding: '3px 9px', borderRadius: 6, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', cursor: 'pointer', font: '600 9.5px var(--sans)' }}>Ver equipo</button>
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
