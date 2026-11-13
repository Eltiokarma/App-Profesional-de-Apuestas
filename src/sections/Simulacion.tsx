import { useEffect, useRef, useState } from 'react'
import type { ApuestaSimulada, EstrategiaClave, EstrategiaSimulada, FrenoTramo, GrupoAlerta, GrupoSemaforo, Resultado1x2, ResumenAlerta, ResumenMarcador, ResumenMedio, ResumenSemaforo, SimulacionApuesta, TrasFallos } from '../api/types'
import { SemaforoChip } from '../components/SemaforoChip'
import { getDataSource } from '../services/datasource'
import { useAsync } from '../services/useAsync'

/** SIMULACIÓN DE APUESTA (28/10/2026, pedido del usuario): qué habría pasado
 *  con una banca apostando con nuestros 1X2 desde los partidos de ese día. La
 *  cuenta la hace el backend (`backend/analisis/simulacion.py`) y se rehace al
 *  leer; la pantalla solo elige qué fracción de Kelly mirar. Cada apuesta trae
 *  la versión de los skills con la que se escribió su parte.
 *  EL MÉTODO (03/11/2026, docs/METODO_APUESTA.md) va primero: 1 % de la banca
 *  al elegido con un freno por tramo de confianza; su tarjeta dice cómo está
 *  hoy cada tramo. */

type Kelly = 'kelly' | 'kellyMedio' | 'kellyCuarto'
const KELLY_OPC: [Kelly, string][] = [['kelly', 'entero'], ['kellyMedio', '½'], ['kellyCuarto', '¼']]
const COLOR: Record<'proporcional' | 'metodoVerde' | 'metodoFueraMedio' | 'plana' | 'plana60' | 'kelly' | 'martingala' | 'martingala60' | 'martingala60Ajustada' | 'martingalaFueraMedio' | 'martingalaFueraMedioTope', string> = {
  proporcional: 'var(--sim-proporcional)', metodoVerde: 'var(--sim-metodo-verde)', plana: 'var(--sim-plana)', plana60: 'var(--sim-plana60)', kelly: 'var(--sim-kelly)', martingala: 'var(--sim-martingala)',
  martingala60: 'var(--sim-martingala60)',
  // el método fuera del medio (13/11/2026) y la martingala de 60 %+ ajustada a la cuota
  metodoFueraMedio: 'var(--sim-metodo-marcador)', martingala60Ajustada: 'var(--sim-martingala60-ajustada)',
  martingalaFueraMedio: 'var(--sim-martingala-fuera-medio)', martingalaFueraMedioTope: 'var(--sim-martingala-fuera-medio-tope)',
}
const RES: Record<Resultado1x2, string> = { local: 'Local', empate: 'Empate', visita: 'Visita' }
const SKILL_CORTO: [string, string][] = [
  ['sad-analysis', 'sad'], ['efe-clasificador', 'EFE'], ['teorema-del-echado', 'TDE'], ['diagnostico-tactico', 'DTP'],
]
const CORTO: Record<EstrategiaClave, string> = {
  proporcional: 'Método', metodoVerde: 'Método 🟢', metodoFueraMedio: 'Método sin medio', martingala60Ajustada: 'Martin. 60 %+ aj.', martingalaFueraMedio: 'Martin. sin medio', martingalaFueraMedioTope: 'Martin. sin medio tope', plana: 'Plana', plana60: 'Plana 60 %+', kelly: 'Kelly', kellyMedio: 'Kelly ½', kellyCuarto: 'Kelly ¼', martingala: 'Martingala', martingala60: 'Martin. 60 %+',
}
const MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

/** «2026-10-28 20:00:00» (UTC) → «28 oct 15:00» en hora local del navegador */
function fecha(utc: string | null): string {
  if (!utc) return ''
  const d = new Date(utc.replace(' ', 'T') + 'Z')
  if (isNaN(d.getTime())) return utc
  return `${d.getDate()} ${MES[d.getMonth()]} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
const num = (x: number, d = 2) => x.toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
// el signo sale del número YA redondeado: −0,004 no se escribe «−0.00»
const signo = (x: number, d = 2) => {
  const r = Number(x.toFixed(d))
  return (r > 0 ? '+' : r < 0 ? '−' : '') + num(Math.abs(r), d)
}
const pct = (x: number | null, d = 1) => (x == null ? '—' : signo(100 * x, d) + ' %')
const colorDe = (x: number | null) => (x == null || x === 0 ? 'var(--t2)' : x > 0 ? 'var(--up)' : 'var(--down)')

const tarjeta: React.CSSProperties = { background: 'var(--bg2)', border: '1px solid var(--line)', borderRadius: 12, padding: '13px 14px', minWidth: 0 }
const rotulo: React.CSSProperties = { font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px', textTransform: 'uppercase' }

// LA LISTA DE APUESTAS PAGINADA (13/11/2026, usuario: «esa página demora mucho
// en cargarse, se cargan muchos partidos… poner # de páginas»): el backend manda
// una página y la gráfica sale de `linea` + `estrategias[].serie`
const POR_PAGINA = 20

export function Simulacion({ isMobile }: { isMobile: boolean }) {
  const sim = useAsync<SimulacionApuesta>(() => getDataSource().simulacion(1, POR_PAGINA), 'simulacion')
  const [kelly, setKelly] = useState<Kelly>('kelly')
  const [pagina, setPagina] = useState(1)
  // la página 1 ya vino con la carga principal; las otras se piden al cambiar
  const pag = useAsync<SimulacionApuesta | null>(
    () => (pagina === 1 ? Promise.resolve(null) : getDataSource().simulacion(pagina, POR_PAGINA)), 'sim-pagina-' + pagina)
  const lista = useRef<HTMLDivElement>(null)

  const pad = isMobile ? '16px 14px 40px' : '22px 26px 48px'
  if (sim.loading && !sim.data) return <div style={{ padding: pad, font: '500 12px var(--sans)', color: 'var(--t3)' }}>Simulando…</div>
  if (sim.error || !sim.data) {
    return (
      <div style={{ padding: pad, display: 'flex', gap: 10, alignItems: 'center' }}>
        <span style={{ font: '500 12px var(--sans)', color: 'var(--down)' }}>No se pudo leer la simulación: {sim.error ?? 'sin datos'}</span>
        <button onClick={sim.reload} style={{ padding: '4px 10px', border: '1px solid var(--line)', borderRadius: 7, cursor: 'pointer', background: 'var(--bg3)', color: 'var(--t1)', font: '600 10.5px var(--sans)' }}>Reintentar</button>
      </div>
    )
  }
  const d = sim.data
  const est = (c: EstrategiaClave) => d.estrategias.find((e) => e.clave === c)!
  const visibles: { clave: EstrategiaClave; color: string }[] = [
    { clave: 'proporcional', color: COLOR.proporcional },
    // el método solo en verde (11/11/2026): en papel, para medir el semáforo
    ...(d.estrategias.some((e) => e.clave === 'metodoVerde') ? [{ clave: 'metodoVerde' as EstrategiaClave, color: COLOR.metodoVerde }] : []),
    // el método fuera del medio (13/11/2026): en papel, sin el 45-60 % de la casa
    ...(d.estrategias.some((e) => e.clave === 'metodoFueraMedio') ? [{ clave: 'metodoFueraMedio' as EstrategiaClave, color: COLOR.metodoFueraMedio }] : []),
    { clave: 'plana', color: COLOR.plana }, { clave: 'plana60', color: COLOR.plana60 }, { clave: kelly, color: COLOR.kelly }, { clave: 'martingala', color: COLOR.martingala },
    { clave: 'martingala60', color: COLOR.martingala60 },
    // la martingala de 60 %+ ajustada a la cuota (13/11/2026): recupera con cualquier cuota
    ...(d.estrategias.some((e) => e.clave === 'martingala60Ajustada') ? [{ clave: 'martingala60Ajustada' as EstrategiaClave, color: COLOR.martingala60Ajustada }] : []),
    // las martingalas ajustadas fuera del medio (13/11/2026), sin tope y con tope del 25 % de la banca
    ...(['martingalaFueraMedio', 'martingalaFueraMedioTope'] as const).filter((c) => d.estrategias.some((e) => e.clave === c)).map((c) => ({ clave: c as EstrategiaClave, color: COLOR[c] })),
  ]
  // la gráfica: lo mínimo de cada cerrada (`linea`) y la banca de cada serie; sin
  // `linea` (respuesta sin paginar) se arma de las apuestas, como antes
  const linea = d.linea ?? [...d.apuestas].reverse().filter((a) => a.estado === 'cerrada').map((a) => ({
    fixtureId: a.fixtureId, pitazo: a.pitazo, local: a.partido.local, visita: a.partido.visita,
    resultado: a.resultado as Resultado1x2, sad: a.versiones['sad-analysis'] ?? '' }))
  const paginacion = d.paginacion
  const deLaPagina = pagina === 1 ? d.apuestas : pag.data?.apuestas ?? null
  const irA = (p: number) => {
    setPagina(p)
    lista.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div style={{ padding: pad, maxWidth: 1080 }}>
      <h1 style={{ font: '800 26px var(--sans)', color: 'var(--t1)', margin: '0 0 4px' }}>Simulación de apuesta</h1>
      <div style={{ font: '500 12px var(--sans)', color: 'var(--t3)', marginBottom: 12, lineHeight: 1.45 }}>
        Banca de {num(d.bancaInicial, 0)} unidades sobre nuestros 1X2 desde los partidos del {fecha(d.desde).split(' ').slice(0, 2).join(' ')} ·{' '}
        {d.cerradas} cerradas ({d.aciertos} aciertos del elegido) · {d.pendientes} por jugarse
      </div>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center', marginBottom: 12 }}>
        <span style={{ ...rotulo, marginRight: 2 }}>Kelly</span>
        {KELLY_OPC.map(([k, et]) => {
          const on = kelly === k
          return (
            <button key={k} onClick={() => setKelly(k)}
              style={{ padding: '5px 11px', borderRadius: 8, border: `1px solid ${on ? 'var(--accent)' : 'var(--line)'}`, background: on ? 'var(--bg3)' : 'transparent', color: on ? 'var(--t1)' : 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
              {et}
            </button>
          )
        })}
        {sim.loading && <span style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>actualizando…</span>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: isMobile ? 'minmax(0,1fr)' : 'repeat(3, minmax(0,1fr))', gap: 10, marginBottom: 12 }}>
        {visibles.map((v) => <TarjetaEstrategia key={v.clave} e={est(v.clave)} color={v.color} />)}
      </div>

      <div style={{ ...tarjeta, marginBottom: 12 }}>
        <div style={{ ...rotulo, marginBottom: 8 }}>Evolución de la banca · partido a partido</div>
        {linea.length ? (
          <GraficaBanca linea={linea} series={visibles.map((v) => ({ ...v, nombre: est(v.clave).nombre, serie: est(v.clave).serie }))} inicial={d.bancaInicial} />
        ) : (
          <div style={{ padding: '26px 8px', textAlign: 'center', font: '500 12px var(--sans)', color: 'var(--t3)' }}>
            Todavía no hay partidos cerrados desde el inicio de la simulación: la curva aparece con el primer resultado.
          </div>
        )}
      </div>

      {d.porVersion.length > 0 && <PorVersion d={d} visibles={visibles.map((v) => v.clave)} isMobile={isMobile} />}

      {d.trasFallos && d.trasFallos.base.n > 0 && <TablaTrasFallos t={d.trasFallos} isMobile={isMobile} />}

      {d.semaforo && <TablaSemaforo r={d.semaforo} isMobile={isMobile} />}

      {d.medio && <TablaMedio r={d.medio} isMobile={isMobile} />}

      {d.marcador && <TablaMarcador r={d.marcador} isMobile={isMobile} />}

      {d.alertaConfianza && <TablaAlerta r={d.alertaConfianza} isMobile={isMobile} />}

      <div ref={lista} style={{ ...rotulo, margin: '18px 0 8px', scrollMarginTop: 12 }}>
        Apuestas · la más nueva primero{paginacion ? ` · ${paginacion.total} en total` : ''}
      </div>
      {paginacion && paginacion.paginas > 1 && <Paginador pagina={pagina} paginas={paginacion.paginas} irA={irA} />}
      {pag.error && pagina !== 1 ? (
        <div style={{ ...tarjeta, font: '500 12px var(--sans)', color: 'var(--down)' }}>No se pudo leer la página {pagina}: {pag.error}</div>
      ) : !deLaPagina ? (
        <div style={{ ...tarjeta, font: '500 12px var(--sans)', color: 'var(--t3)' }}>Cargando la página {pagina}…</div>
      ) : deLaPagina.length ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {deLaPagina.map((a) => <FilaApuesta key={a.fixtureId} a={a} visibles={visibles} />)}
        </div>
      ) : (
        <div style={{ ...tarjeta, textAlign: 'center', font: '500 12px var(--sans)', color: 'var(--t3)' }}>
          Sin partes con 1X2 y cuotas desde el inicio de la simulación.
        </div>
      )}

      {paginacion && paginacion.paginas > 1 && deLaPagina && deLaPagina.length > 0 && (
        <div style={{ marginTop: 10 }}><Paginador pagina={pagina} paginas={paginacion.paginas} irA={irA} /></div>
      )}

      {d.excluidos.length > 0 && (
        <details style={{ marginTop: 14 }}>
          <summary style={{ cursor: 'pointer', font: '600 11.5px var(--sans)', color: 'var(--t2)' }}>
            {d.excluidos.length} partido{d.excluidos.length === 1 ? '' : 's'} con parte que no entra{d.excluidos.length === 1 ? '' : 'n'} a la simulación
          </summary>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 8 }}>
            {d.excluidos.map((x) => (
              <div key={x.fixtureId} style={{ font: '500 11px var(--sans)', color: 'var(--t2)' }}>
                <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>{fecha(x.pitazo)}</span> · {x.partido.local} – {x.partido.visita}: <span style={{ color: 'var(--t3)' }}>{x.motivo}</span>
              </div>
            ))}
          </div>
        </details>
      )}

      <div style={{ marginTop: 16, font: '500 11px var(--sans)', color: 'var(--t3)', lineHeight: 1.5 }}>
        {d.estrategias.filter((e) => visibles.some((v) => v.clave === e.clave)).map((e) => (
          <div key={e.clave}><b style={{ color: 'var(--t2)' }}>{e.nombre}</b>: {e.descripcion}.</div>
        ))}
        <div style={{ marginTop: 6 }}>{d.nota}.</div>
      </div>
    </div>
  )
}

function TarjetaEstrategia({ e, color }: { e: EstrategiaSimulada; color: string }) {
  const metodo = e.clave === 'proporcional'
  return (
    <div style={{ ...tarjeta, ...(metodo ? { borderColor: color, boxShadow: `inset 3px 0 0 ${color}` } : {}) }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 6, flexWrap: 'wrap' }}>
        <span style={{ width: 10, height: 3, borderRadius: 2, background: color, flexShrink: 0 }} />
        <span style={{ font: '700 12px var(--sans)', color: 'var(--t1)' }}>{e.nombre}</span>
        {metodo && <span style={{ ...rotulo, color, marginLeft: 'auto' }}>el método</span>}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
        <span style={{ font: '800 24px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{num(e.banca)}</span>
        <span style={{ font: '700 12px var(--mono)', color: colorDe(e.ganancia), fontVariantNumeric: 'tabular-nums' }}>{signo(e.ganancia)} u</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: '4px 10px', marginTop: 8, font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
        <span>ROI <b style={{ color: colorDe(e.roi) }}>{pct(e.roi)}</b></span>
        <span>apuestas {e.apuestas} · ganó {e.ganadas}</span>
        <span>apostado {num(e.apostado)}</span>
        <span>caída máx. {num(100 * e.caidaMaxima, 1)} %</span>
        <span title="lo más que estuvo en juego a la vez">en juego máx. {num(e.exposicionMaxima)}</span>
        <span>apuesta máx. {num(e.montoMaximo)}</span>
      </div>
      {e.quebro != null && <div style={{ marginTop: 6, font: '700 10.5px var(--sans)', color: 'var(--down)' }}>La banca quebró (partido {e.quebro}).</div>}
      {e.lineas && e.lineas.abiertas > 0 && e.quebro == null && (
        <div style={{ marginTop: 6, font: '500 10.5px var(--sans)', color: 'var(--t2)' }}>
          {e.lineas.abiertas} línea{e.lineas.abiertas === 1 ? '' : 's'} abierta{e.lineas.abiertas === 1 ? '' : 's'}
          {e.lineas.perdiendo > 0 && e.lineas.perdidaMayor != null
            ? ` · ${e.lineas.perdiendo} viene${e.lineas.perdiendo === 1 ? '' : 'n'} de perder (la más cargada lleva ${num(e.lineas.perdidaMayor)} u perdidas; la próxima apuesta las recupera según la cuota)`
            : e.lineas.perdiendo > 0
            ? ` · ${e.lineas.perdiendo} viene${e.lineas.perdiendo === 1 ? '' : 'n'} de perder (la más cargada va por ${num(e.lineas.proximoMayor)} u)`
            : ' · todas en 1 u'}
        </div>
      )}
      {e.tramos && <FrenoTramos tramos={e.tramos} />}
      {e.apuestas === 0 && e.clave.startsWith('kelly') && (
        <div style={{ marginTop: 6, font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>Sin apuestas: en ningún partido nuestra probabilidad superó lo que paga la cuota.</div>
      )}
    </div>
  )
}

/** El freno del método por tramo: cuánto acertó en sus últimos 50 contra lo que pedía la cuota */
function FrenoTramos({ tramos }: { tramos: FrenoTramo[] }) {
  return (
    <div style={{ marginTop: 9, paddingTop: 8, borderTop: '1px solid var(--line)' }}>
      <div style={{ ...rotulo, marginBottom: 5 }}>Freno por tramo · acierta / pide la cuota</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: '3px 10px', font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
        {tramos.map((t) => (
          <span key={t.tramo} title={t.n ? `${t.aciertos} de ${t.n}${t.z != null ? ` · z ${signo(t.z, 1)}` : ''}` : 'sin partidos cerrados'}>
            <b style={{ color: 'var(--t1)' }}>{t.tramo}</b>{' '}
            {t.n && t.tasa != null && t.pide != null ? (
              <>
                <span style={{ color: t.tasa >= t.pide ? 'var(--up)' : 'var(--down)' }}>{num(100 * t.tasa, 0)}</span>/{num(100 * t.pide, 0)} %
                {t.pausado ? <b style={{ color: 'var(--down)' }}> · pausa</b> : <span style={{ color: 'var(--t3)' }}> · n {t.n}</span>}
              </>
            ) : <span style={{ color: 'var(--t3)' }}>sin datos</span>}
          </span>
        ))}
      </div>
    </div>
  )
}

type PuntoLinea = NonNullable<SimulacionApuesta['linea']>[number]

/** Los números de página: 1 … p−1 p p+1 … N, con anterior y siguiente. */
function Paginador({ pagina, paginas, irA }: { pagina: number; paginas: number; irA: (p: number) => void }) {
  const nums = [...new Set([1, pagina - 1, pagina, pagina + 1, paginas])].filter((p) => p >= 1 && p <= paginas).sort((a, b) => a - b)
  const boton = (activo: boolean): React.CSSProperties => ({
    minWidth: 30, height: 30, padding: '0 8px', borderRadius: 8, cursor: activo ? 'default' : 'pointer',
    border: `1px solid ${activo ? 'var(--accent)' : 'var(--line)'}`, background: activo ? 'var(--bg3)' : 'var(--bg2)',
    color: activo ? 'var(--t1)' : 'var(--t2)', font: '700 11px var(--mono)', fontVariantNumeric: 'tabular-nums',
  })
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, alignItems: 'center', marginBottom: 8 }}>
      <button disabled={pagina === 1} onClick={() => irA(pagina - 1)} style={{ ...boton(false), opacity: pagina === 1 ? 0.4 : 1 }} aria-label="Página anterior">‹</button>
      {nums.map((p, i) => (
        <span key={p} style={{ display: 'inline-flex', gap: 5, alignItems: 'center' }}>
          {i > 0 && p - nums[i - 1] > 1 && <span style={{ color: 'var(--t3)', font: '600 11px var(--mono)' }}>…</span>}
          <button onClick={() => p !== pagina && irA(p)} style={boton(p === pagina)} aria-current={p === pagina ? 'page' : undefined}>{p}</button>
        </span>
      ))}
      <button disabled={pagina === paginas} onClick={() => irA(pagina + 1)} style={{ ...boton(false), opacity: pagina === paginas ? 0.4 : 1 }} aria-label="Página siguiente">›</button>
    </div>
  )
}

// LA GRÁFICA NAVEGABLE (13/11/2026, usuario: «hay que hacer que este gráfico sea
// más navegable, está muy apretado»): cada serie se prende o apaga desde la
// leyenda (se recuerda en este navegador), pasar por su nombre la resalta, el
// rango elige los últimos partidos y el eje Y se ajusta a lo que se ve
type Rango = 'todo' | 100 | 50
const RANGOS: [Rango, string][] = [['todo', 'todo'], [100, 'últimos 100'], [50, 'últimos 50']]
const LS_OCULTAS = 'sad-sim-ocultas'

function GraficaBanca({ linea, series, inicial }: {
  linea: PuntoLinea[]
  series: { clave: EstrategiaClave; color: string; nombre: string; serie: EstrategiaSimulada['serie'] }[]
  inicial: number
}) {
  const caja = useRef<HTMLDivElement>(null)
  const [ancho, setAncho] = useState(600)
  const [hover, setHover] = useState<number | null>(null)
  const [foco, setFoco] = useState<string | null>(null)
  const [rango, setRango] = useState<Rango>('todo')
  const [ocultas, setOcultas] = useState<string[]>(() => {
    try {
      const v = JSON.parse(localStorage.getItem(LS_OCULTAS) ?? '[]')
      return Array.isArray(v) ? v.map(String) : []
    } catch {
      return []
    }
  })
  const guardar = (v: string[]) => {
    setOcultas(v)
    try { localStorage.setItem(LS_OCULTAS, JSON.stringify(v)) } catch { /* modo privado: la elección dura la visita */ }
  }
  const alternar = (c: string) => guardar(ocultas.includes(c) ? ocultas.filter((x) => x !== c) : [...ocultas, c])
  useEffect(() => {
    const el = caja.current
    if (!el) return
    const ro = new ResizeObserver(() => setAncho(el.clientWidth || 600))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  const H = ancho < 520 ? 260 : 320
  const m = { t: 10, r: 12, b: 22, l: 44 }
  const n = linea.length
  const desde = rango === 'todo' ? 0 : Math.max(0, n - rango)
  const tramo = Math.max(1, n - desde)
  // la banca de cada serie tras cada cerrada: `serie` empieza en la banca inicial
  const valores = series.map((s) => Array.from({ length: n + 1 }, (_, i) => s.serie[i]?.banca ?? s.serie[s.serie.length - 1]?.banca ?? inicial))
  const vis = series.map((s, si) => ({ s, si })).filter(({ s }) => !ocultas.includes(s.clave))
  // el eje Y con lo que se ve: las series prendidas en el rango elegido
  const enRango = vis.flatMap(({ si }) => valores[si].slice(desde))
  let lo = Math.min(...(enRango.length ? enRango : [inicial]), desde === 0 ? inicial : Infinity)
  let hi = Math.max(...(enRango.length ? enRango : [inicial]), desde === 0 ? inicial : -Infinity)
  if (hi - lo < 4) { lo -= 2; hi += 2 }
  const margen = (hi - lo) * 0.08
  lo -= margen; hi += margen
  const x = (i: number) => m.l + ((i - desde) / tramo) * (ancho - m.l - m.r)
  const y = (v: number) => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b)
  const ticks = [lo + margen, (lo + hi) / 2, hi - margen, ...(inicial > lo && inicial < hi ? [inicial] : [])]
    .filter((v, i, arr) => arr.findIndex((w) => Math.abs(w - v) < (hi - lo) * 0.08) === i)

  const mover = (e: React.PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    const i = desde + Math.round(((e.clientX - r.left - m.l) / (ancho - m.l - m.r)) * tramo)
    setHover(Math.max(desde, Math.min(n, i)))
  }
  const h = hover != null && hover >= desde ? hover : null
  const a = h != null && h > 0 ? linea[h - 1] : null
  // en el tooltip, de la banca más alta a la más baja
  const orden = h != null ? [...vis].sort((p, q) => valores[q.si][h] - valores[p.si][h]) : []
  const chip: React.CSSProperties = { padding: '3px 8px', borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', cursor: 'pointer', font: '600 10px var(--sans)', color: 'var(--t2)' }

  return (
    <div ref={caja} style={{ position: 'relative' }}>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center', marginBottom: 8 }}>
        {RANGOS.map(([r, et]) => (
          <button key={String(r)} onClick={() => { setRango(r); setHover(null) }}
            style={{ ...chip, ...(rango === r ? { borderColor: 'var(--accent)', background: 'var(--bg3)', color: 'var(--t1)' } : {}) }}>
            {et}
          </button>
        ))}
        <span style={{ flex: 1 }} />
        <button onClick={() => guardar([])} style={chip}>mostrar todas</button>
        <button onClick={() => guardar(series.map((s) => s.clave))} style={chip}>ocultar todas</button>
      </div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}>
        {series.map((s) => {
          const off = ocultas.includes(s.clave)
          return (
            <button key={s.clave} onClick={() => alternar(s.clave)}
              onPointerEnter={() => !off && setFoco(s.clave)} onPointerLeave={() => setFoco(null)}
              title={off ? 'Mostrar esta serie' : 'Ocultar esta serie'} aria-pressed={!off}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '3px 8px', borderRadius: 7, cursor: 'pointer',
                border: `1px solid ${off ? 'var(--line)' : 'color-mix(in oklch, ' + s.color + ', transparent 55%)'}`,
                background: off ? 'transparent' : 'var(--bg2)', opacity: off ? 0.45 : 1,
                font: '600 10.5px var(--sans)', color: off ? 'var(--t3)' : 'var(--t2)', textDecoration: off ? 'line-through' : 'none' }}>
              <span style={{ width: 14, height: 3, borderRadius: 1, background: s.color }} />{s.nombre}
            </button>
          )
        })}
      </div>
      <svg width={ancho} height={H} style={{ display: 'block', touchAction: 'pan-y' }}
        onPointerMove={mover} onPointerDown={mover} onPointerLeave={() => setHover(null)}>
        {ticks.map((v) => (
          <g key={v}>
            <line x1={m.l} x2={ancho - m.r} y1={y(v)} y2={y(v)} stroke="var(--grid)" strokeWidth={1}
              strokeDasharray={Math.abs(v - inicial) < 1e-9 ? '4 4' : undefined} />
            <text x={m.l - 6} y={y(v) + 3.5} textAnchor="end" style={{ fill: 'var(--t3)', font: '500 10px var(--mono)' }}>{num(v, 0)}</text>
          </g>
        ))}
        <text x={m.l} y={H - 6} style={{ fill: 'var(--t3)', font: '500 10px var(--mono)' }}>{desde === 0 ? 'inicio' : `partido ${desde}`}</text>
        <text x={ancho - m.r} y={H - 6} textAnchor="end" style={{ fill: 'var(--t3)', font: '500 10px var(--mono)' }}>{n} partido{n === 1 ? '' : 's'}</text>
        {vis.map(({ s, si }) => (
          <polyline key={s.clave} fill="none" stroke={s.color} strokeLinejoin="round" strokeLinecap="round"
            strokeWidth={foco === s.clave ? 3 : 2} opacity={foco && foco !== s.clave ? 0.18 : 1}
            points={valores[si].slice(desde).map((v, i) => `${x(desde + i)},${y(v)}`).join(' ')} />
        ))}
        {h != null && (
          <g>
            <line x1={x(h)} x2={x(h)} y1={m.t} y2={H - m.b} stroke="var(--t3)" strokeWidth={1} />
            {vis.map(({ s, si }) => (
              <circle key={s.clave} cx={x(h)} cy={y(valores[si][h])} r={4.5} fill={s.color} stroke="var(--bg2)" strokeWidth={2} />
            ))}
          </g>
        )}
      </svg>
      {!vis.length && (
        <div style={{ position: 'absolute', left: 0, right: 0, top: '55%', textAlign: 'center', font: '500 12px var(--sans)', color: 'var(--t3)' }}>
          Todas las series están ocultas: tocá una en la leyenda para verla.
        </div>
      )}
      {h != null && vis.length > 0 && (
        <div style={{
          position: 'absolute', top: 70, [x(h) > ancho / 2 ? 'right' : 'left']: x(h) > ancho / 2 ? ancho - x(h) + 10 : x(h) + 10,
          background: 'var(--bg1)', border: '1px solid var(--line2)', borderRadius: 9, padding: '8px 10px', boxShadow: 'var(--shadow)',
          pointerEvents: 'none', maxWidth: 250, font: '500 10.5px var(--sans)', color: 'var(--t2)',
        }}>
          <div style={{ font: '700 11px var(--sans)', color: 'var(--t1)', marginBottom: 4 }}>
            {a ? `${a.local} – ${a.visita}` : 'Banca inicial'}
          </div>
          {a && <div style={{ marginBottom: 4 }}>{fecha(a.pitazo)} · salió {a.resultado ? RES[a.resultado] : '—'} · sad {a.sad || '—'}</div>}
          {orden.map(({ s, si }) => (
            <div key={s.clave} style={{ display: 'flex', alignItems: 'center', gap: 6, fontVariantNumeric: 'tabular-nums' }}>
              <span style={{ width: 8, height: 2, background: s.color }} />
              <span style={{ flex: 1 }}>{s.nombre}</span>
              <b style={{ color: 'var(--t1)', font: '700 10.5px var(--mono)' }}>{num(valores[si][h])}</b>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/** CRITERIO DE CONTACTO (04/11/2026): ¿después de varios fallos seguidos acertamos más? Es lo que
 *  la martingala cobra. La regla para tomarlo en serio está fijada de antemano y no se mueve. */
function TablaTrasFallos({ t, isMobile }: { t: TrasFallos; isMobile: boolean }) {
  const c = t.contacto
  const ic = (i: [number, number] | null) => (i ? `${num(100 * i[0], 0)}-${num(100 * i[1], 0)} %` : '—')
  const tasa = (x: number | null) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const color = c.estado === 'contacto' ? 'var(--up)' : c.estado === 'sin_contacto' ? 'var(--t2)' : 'var(--mark)'
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>Criterio de contacto · acierto tras fallos seguidos</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        Es lo que la martingala cobra: si después de varios fallos acertamos más que el promedio. Se toma en serio con{' '}
        {c.nMinimo}+ casos tras {c.k} fallos, {num(100 * c.tasaMinima, 0)} %+ de acierto y el intervalo entero sobre el promedio.
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)' }}>
              <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}>después de</th>
              <th style={{ ...celda, fontWeight: 600 }}>casos</th>
              <th style={{ ...celda, fontWeight: 600 }}>acierta</th>
              <th style={{ ...celda, fontWeight: 600 }}>IC 95 %</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderTop: '1px solid var(--line)' }}>
              <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700 }}>promedio</td>
              <td style={celda}>{t.base.n}</td>
              <td style={{ ...celda, color: 'var(--t1)', fontWeight: 700 }}>{tasa(t.base.tasa)}</td>
              <td style={celda}>{ic(t.base.intervalo)}</td>
            </tr>
            {t.porK.map((f) => {
              const arriba = f.tasa != null && t.base.tasa != null && f.tasa > t.base.tasa
              return (
                <tr key={f.k} style={{ borderTop: '1px solid var(--line)', background: f.k === c.k ? 'var(--bg3)' : undefined }}>
                  <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: f.k === c.k ? 700 : 500 }}>
                    {f.k} fallo{f.k === 1 ? '' : 's'}
                  </td>
                  <td style={celda}>{f.n}</td>
                  <td style={{ ...celda, fontWeight: 700, color: f.tasa == null ? 'var(--t3)' : arriba ? 'var(--up)' : 'var(--down)' }}>{tasa(f.tasa)}</td>
                  <td style={celda}>{ic(f.intervalo)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 8, font: '600 11px var(--sans)', color, lineHeight: 1.45 }}>
        {c.estado === 'en_observacion' ? `En observación: ${c.n} de ${c.nMinimo} casos tras ${c.k} fallos (faltan ${c.faltan}).`
          : c.estado === 'contacto' ? 'Contacto: el criterio se cumple. Tomarlo en serio.' : 'Sin contacto: con los casos suficientes, el criterio no se cumple.'}
      </div>
    </div>
  )
}

// el estado del criterio por escalones (11/11/2026), cada uno con su color
const ESTADO_SEMAFORO: Record<ResumenSemaforo['criterio']['estado'], { etiqueta: string; color: string; fondo: string }> = {
  en_observacion: { etiqueta: 'EN OBSERVACIÓN', color: 'var(--t2)', fondo: 'var(--bg3)' },
  prometedor: { etiqueta: 'PROMETEDOR', color: 'color-mix(in oklch, var(--up) 55%, var(--mark))', fondo: 'color-mix(in oklch, color-mix(in oklch, var(--up) 55%, var(--mark)), transparent 84%)' },
  confirmado: { etiqueta: 'CONFIRMADO', color: 'var(--up)', fondo: 'color-mix(in oklch, var(--up), transparent 84%)' },
  no_se_sostiene: { etiqueta: 'NO SE SOSTIENE', color: 'var(--down)', fondo: 'color-mix(in oklch, var(--down), transparent 84%)' },
  sin_contacto: { etiqueta: 'SIN CONTACTO', color: 'var(--t2)', fondo: 'var(--bg3)' },
}

/** EL SEMÁFORO DEL ELEGIDO, POR LAS ESPINAS (13/11/2026): verdes contra amarillos y rojos. Lo que se
 *  juzga es la desconfianza: el amarillo y el rojo tienen que acertar MENOS que el verde. La cuota va
 *  como información. Cuenta para el criterio SOLO lo nuevo (desde el 13/11); la regla está fijada. */
function TablaSemaforo({ r, isMobile }: { r: ResumenSemaforo; isMobile: boolean }) {
  const tasa = (x: number | null | undefined) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const ic = (i: [number, number] | null) => (i ? `${num(100 * i[0], 0)}-${num(100 * i[1], 0)} %` : '—')
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  const c = r.criterio
  const est = ESTADO_SEMAFORO[c.estado] ?? ESTADO_SEMAFORO.en_observacion
  const bloques: [string, ResumenSemaforo['nuevo']][] = [[`desde el ${fecha(r.desde).split(' ').slice(0, 2).join(' ')} (cuenta)`, r.nuevo], ['todo lo simulado', r.todo]]
  const filas: [string, keyof ResumenSemaforo['nuevo']][] = [['🟢 verde', 'verde'], ['🟡 amarillo', 'amarillo'], ['🔴 rojo', 'rojo'], ['⚪ sin dato', 'sinDato']]
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>Semáforo del elegido · por las espinas</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        Sale de las espinas del parte, no de la cuota. Verde: la espina del elegido lo acompaña. Amarillo: dice empate, o la del
        rival dice que sigue. Rojo: la espina del elegido dice que pierde, no apostar. Por escalones de amarillos y rojos nuevos
        ({c.escalones.join(' · ')}): en {c.escalones.slice(0, -1).join(' y ')}, prometedor si el verde acierta {num(100 * c.separacionMinima, 0)}+ pts más;
        en {c.nMinimo}, confirmado con esos puntos y el intervalo de los amarillos y rojos entero por debajo del verde. En cualquier
        escalón, no se sostiene si el amarillo y el rojo no aciertan menos que el verde.
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: 'var(--bg3)', font: '700 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          {c.escalon ? `escalón ${c.escalon}` : `antes del escalón ${c.escalones[0]}`}
        </span>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: est.fondo, font: '700 10.5px var(--mono)', color: est.color, letterSpacing: '.3px' }}>
          {est.etiqueta}
        </span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
          {c.n} amarillos o rojos{c.proximoEscalon ? ` · faltan ${c.faltan} para el ${c.proximoEscalon}` : ''}
        </span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)' }}>
              <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}></th>
              <th style={{ ...celda, fontWeight: 600 }}>casos</th>
              <th style={{ ...celda, fontWeight: 600 }}>acierta</th>
              <th style={{ ...celda, fontWeight: 600 }}>pedía</th>
              <th style={{ ...celda, fontWeight: 600 }}>±</th>
              <th style={{ ...celda, fontWeight: 600 }}>IC 95 %</th>
              <th style={{ ...celda, fontWeight: 600 }}>1 u plano</th>
            </tr>
          </thead>
          {bloques.map(([titulo, g]) => (
            <tbody key={titulo}>
              <tr><td colSpan={7} style={{ ...celda, textAlign: 'left', paddingTop: 9, font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px' }}>{titulo.toUpperCase()}</td></tr>
              {filas.map(([nombre, k]) => {
                const x: GrupoSemaforo = g[k]
                return (
                  <tr key={k} style={{ borderTop: '1px solid var(--line)' }}>
                    <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700, fontFamily: 'var(--sans)', whiteSpace: 'nowrap' }}>{nombre}</td>
                    <td style={celda}>{x.n}</td>
                    <td style={{ ...celda, color: 'var(--t1)', fontWeight: 700 }}>{tasa(x.tasa)}</td>
                    <td style={celda}>{tasa(x.pide)}</td>
                    <td style={{ ...celda, color: colorDe(x.ventaja), fontWeight: 700 }}>{x.ventaja == null ? '—' : `${signo(100 * x.ventaja, 1)} pts`}</td>
                    <td style={celda}>{ic(x.intervalo)}</td>
                    <td style={{ ...celda, color: colorDe(x.roiPlano) }}>{pct(x.roiPlano)}</td>
                  </tr>
                )
              })}
            </tbody>
          ))}
        </table>
      </div>
      <div style={{ marginTop: 8, font: '600 11px var(--sans)', color: est.color, lineHeight: 1.45, overflowWrap: 'anywhere' }}>
        {c.texto}
      </div>
    </div>
  )
}

// LAS PUNTAS CONTRA EL MEDIO (13/11/2026, usuario: «siento que hay una forma
// correcta de apostar»): según lo que la casa le da al elegido, dónde le sacamos
// algo a la cuota. Acá sí se mira la ventaja contra la cuota
function TablaMedio({ r, isMobile }: { r: ResumenMedio; isMobile: boolean }) {
  const tasa = (x: number | null | undefined) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  const c = r.criterio
  const est = ESTADO_SEMAFORO[c.estado] ?? ESTADO_SEMAFORO.en_observacion
  const [lo, hi] = r.medio
  const bloques: [string, ResumenMedio['nuevo']][] = [[`desde el ${fecha(r.desde).split(' ').slice(0, 2).join(' ')} (cuenta)`, r.nuevo], ['todo lo simulado', r.todo]]
  const filas: [string, keyof ResumenMedio['nuevo']][] = [[`punta baja · casa < ${num(lo, 0)} %`, 'puntaBaja'], [`medio · casa ${num(lo, 0)}-${num(hi, 0)} %`, 'medio'], [`punta alta · casa ${num(hi, 0)} %+`, 'puntaAlta'], ['las dos puntas', 'puntas']]
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>Las puntas contra el medio · lo que la casa le da al elegido</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        La plata no sale del win rate solo: sale de la ventaja, lo que acertamos por encima de lo que pide la cuota. Medido el 13/11,
        la ventaja está en las dos puntas (el favorito claro y el partido donde la casa no cree en nuestro elegido) y en el medio no hay.
        Por escalones de partidos nuevos del medio ({c.escalones.join(' · ')}): en {c.escalones.slice(0, -1).join(' y ')}, prometedor si
        las puntas le sacan {num(100 * c.separacionMinima, 0)}+ pts de ventaja al medio; en {c.nMinimo}, confirmado con esos puntos y la plana
        de las puntas en positivo y sobre la del medio.
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: 'var(--bg3)', font: '700 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          {c.escalon ? `escalón ${c.escalon}` : `antes del escalón ${c.escalones[0]}`}
        </span>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: est.fondo, font: '700 10.5px var(--mono)', color: est.color, letterSpacing: '.3px' }}>
          {est.etiqueta}
        </span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
          {c.n} del medio{c.proximoEscalon ? ` · faltan ${c.faltan} para el ${c.proximoEscalon}` : ''}
        </span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)' }}>
              <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}></th>
              <th style={{ ...celda, fontWeight: 600 }}>casos</th>
              <th style={{ ...celda, fontWeight: 600 }}>acierta</th>
              <th style={{ ...celda, fontWeight: 600 }}>pedía</th>
              <th style={{ ...celda, fontWeight: 600 }}>ventaja</th>
              <th style={{ ...celda, fontWeight: 600 }}>1 u plano</th>
            </tr>
          </thead>
          {bloques.map(([titulo, g]) => (
            <tbody key={titulo}>
              <tr><td colSpan={6} style={{ ...celda, textAlign: 'left', paddingTop: 9, font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px' }}>{titulo.toUpperCase()}</td></tr>
              {filas.map(([nombre, k]) => {
                const x: GrupoSemaforo = g[k]
                return (
                  <tr key={k} style={{ borderTop: '1px solid var(--line)' }}>
                    <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700, fontFamily: 'var(--sans)', whiteSpace: 'nowrap' }}>{nombre}</td>
                    <td style={celda}>{x.n}</td>
                    <td style={celda}>{tasa(x.tasa)}</td>
                    <td style={celda}>{tasa(x.pide)}</td>
                    <td style={{ ...celda, color: colorDe(x.ventaja), fontWeight: 700 }}>{x.ventaja == null ? '—' : `${signo(100 * x.ventaja, 1)} pts`}</td>
                    <td style={{ ...celda, color: colorDe(x.roiPlano), fontWeight: 700 }}>{pct(x.roiPlano)}</td>
                  </tr>
                )
              })}
            </tbody>
          ))}
        </table>
      </div>
      <div style={{ marginTop: 8, font: '600 11px var(--sans)', color: est.color, lineHeight: 1.45, overflowWrap: 'anywhere' }}>
        {c.texto}
      </div>
    </div>
  )
}

// EL MARCADOR MÁS PROBABLE CON EL ELEGIDO (13/11/2026, usuario: «no era medir
// contra la cuota, era medir si nuestro win rate mejoraba»): alineados contra el
// resto, con el criterio por escalones fijado antes de los partidos nuevos
function TablaMarcador({ r, isMobile }: { r: ResumenMarcador; isMobile: boolean }) {
  const tasa = (x: number | null | undefined) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const ic = (i: [number, number] | null) => (i ? `${num(100 * i[0], 0)}-${num(100 * i[1], 0)} %` : '—')
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  const c = r.criterio
  const est = ESTADO_SEMAFORO[c.estado] ?? ESTADO_SEMAFORO.en_observacion
  const bloques: [string, ResumenMarcador['nuevo']][] = [[`desde el ${fecha(r.desde).split(' ').slice(0, 2).join(' ')} (cuenta)`, r.nuevo], ['todo lo simulado', r.todo]]
  const filas: [string, keyof ResumenMarcador['nuevo']][] = [['⚽ con el elegido', 'alineado'], ['1-1, 0-0 o contrario', 'resto'], ['🟢⚽ verde y con el elegido', 'verdeAlineado'], ['sin marcador', 'sinMarcador']]
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>Marcador más probable · con el elegido</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        El más probable del modelo de goles (el de la lista de Partidos), con la historia anterior al partido: el mismo al minuto 0.
        Se juzga el win rate del elegido, no la cuota. Por escalones de partidos con el marcador alineado ({c.escalones.join(' · ')}):
        en {c.escalones.slice(0, -1).join(' y ')}, prometedor si ganan {num(100 * c.separacionMinima, 0)}+ pts más que el resto; en {c.nMinimo},
        confirmado con esos puntos y el intervalo de los alineados entero por encima. En cualquier escalón, no se sostiene si no ganan más.
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: 'var(--bg3)', font: '700 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          {c.escalon ? `escalón ${c.escalon}` : `antes del escalón ${c.escalones[0]}`}
        </span>
        <span style={{ padding: '3px 9px', borderRadius: 6, background: est.fondo, font: '700 10.5px var(--mono)', color: est.color, letterSpacing: '.3px' }}>
          {est.etiqueta}
        </span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>
          {c.n} alineados{c.proximoEscalon ? ` · faltan ${c.faltan} para el ${c.proximoEscalon}` : ''}
        </span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)' }}>
              <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}></th>
              <th style={{ ...celda, fontWeight: 600 }}>casos</th>
              <th style={{ ...celda, fontWeight: 600 }}>win rate</th>
              <th style={{ ...celda, fontWeight: 600 }}>IC 95 %</th>
              <th style={{ ...celda, fontWeight: 600 }}>pedía</th>
              <th style={{ ...celda, fontWeight: 600 }}>1 u plano</th>
            </tr>
          </thead>
          {bloques.map(([titulo, g]) => (
            <tbody key={titulo}>
              <tr><td colSpan={6} style={{ ...celda, textAlign: 'left', paddingTop: 9, font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px' }}>{titulo.toUpperCase()}</td></tr>
              {filas.map(([nombre, k]) => {
                const x: GrupoSemaforo = g[k]
                return (
                  <tr key={k} style={{ borderTop: '1px solid var(--line)' }}>
                    <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700, fontFamily: 'var(--sans)', whiteSpace: 'nowrap' }}>{nombre}</td>
                    <td style={celda}>{x.n}</td>
                    <td style={{ ...celda, color: 'var(--t1)', fontWeight: 700 }}>{tasa(x.tasa)}</td>
                    <td style={celda}>{ic(x.intervalo)}</td>
                    <td style={celda}>{tasa(x.pide)}</td>
                    <td style={{ ...celda, color: colorDe(x.roiPlano) }}>{pct(x.roiPlano)}</td>
                  </tr>
                )
              })}
            </tbody>
          ))}
        </table>
      </div>
      <div style={{ marginTop: 8, font: '600 11px var(--sans)', color: est.color, lineHeight: 1.45, overflowWrap: 'anywhere' }}>
        {c.texto}
      </div>
    </div>
  )
}

// EN QUIÉN DESCONFIAR (10/11/2026, usuario): la alerta no cambia el elegido;
// esto mide, hacia adelante, si con alerta acertamos menos que sin ella
function TablaAlerta({ r, isMobile }: { r: ResumenAlerta; isMobile: boolean }) {
  const tasa = (x: number | null | undefined) => (x == null ? '—' : `${num(100 * x, 1)} %`)
  const celda: React.CSSProperties = { padding: '5px 6px', textAlign: 'right' }
  const filas: [string, GrupoAlerta][] = [['con alerta', r.conAlerta], ['sin alerta', r.sinAlerta]]
  const total = r.conAlerta.n + r.sinAlerta.n
  return (
    <div style={{ ...tarjeta, marginTop: 12 }}>
      <div style={{ ...rotulo, marginBottom: 4 }}>En quién desconfiar · alerta de confianza</div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 8, lineHeight: 1.45 }}>
        Alerta si le damos al elegido {num(r.sobreCasa, 0)}+ puntos más que la casa, o si su racha es de un solo partido con
        riesgo alto. No cambia el elegido: se registra desde el {fecha(r.desde).split(' ')[0]} y se mide hacia adelante.
      </div>
      {total === 0 ? (
        <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)' }}>Todavía no hay partidos cerrados con la alerta registrada.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
            <thead>
              <tr style={{ color: 'var(--t3)' }}>
                <th style={{ ...celda, textAlign: 'left', fontWeight: 600 }}></th>
                <th style={{ ...celda, fontWeight: 600 }}>casos</th>
                <th style={{ ...celda, fontWeight: 600 }}>acierta</th>
                <th style={{ ...celda, fontWeight: 600 }}>pedía</th>
                <th style={{ ...celda, fontWeight: 600 }}>1 u plano</th>
                <th style={{ ...celda, fontWeight: 600 }}>elegido o empate</th>
              </tr>
            </thead>
            <tbody>
              {filas.map(([nombre, g]) => (
                <tr key={nombre} style={{ borderTop: '1px solid var(--line)' }}>
                  <td style={{ ...celda, textAlign: 'left', color: 'var(--t1)', fontWeight: 700 }}>{nombre}</td>
                  <td style={celda}>{g.n}</td>
                  <td style={{ ...celda, color: 'var(--t1)', fontWeight: 700 }}>{tasa(g.tasa)}</td>
                  <td style={celda}>{tasa(g.pide)}</td>
                  <td style={{ ...celda, color: colorDe(g.roiPlano) }}>{pct(g.roiPlano)}</td>
                  <td style={celda}>{g.dobleOportunidad ? `${tasa(g.dobleOportunidad.tasa)} (pedía ${tasa(g.dobleOportunidad.pide)})` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {r.descarte && (
        <div style={{ marginTop: 8, font: '500 11px var(--sans)', color: 'var(--t2)', lineHeight: 1.45 }}>
          <b style={{ color: 'var(--t1)' }}>El descarte</b> (lo que menos probable le dimos): salió {tasa(r.descarte.tasa)} de {r.descarte.n} partidos;
          la casa le daba {tasa(r.descarte.casaLeDaba)}.
        </div>
      )}
    </div>
  )
}

function PorVersion({ d, visibles, isMobile }: { d: SimulacionApuesta; visibles: EstrategiaClave[]; isMobile: boolean }) {
  return (
    <div style={{ ...tarjeta }}>
      <div style={{ ...rotulo, marginBottom: 8 }}>Por versión de sad-analysis (la del 1X2)</div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', font: isMobile ? '500 10px var(--mono)' : '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
          <thead>
            <tr style={{ color: 'var(--t3)', textAlign: 'right' }}>
              <th style={{ textAlign: 'left', padding: '4px 6px', fontWeight: 600 }}>versión</th>
              <th style={{ padding: '4px 6px', fontWeight: 600 }}>partidos</th>
              <th style={{ padding: '4px 6px', fontWeight: 600 }}>aciertos</th>
              {visibles.map((c) => <th key={c} style={{ padding: '4px 6px', fontWeight: 600 }}>{CORTO[c]}</th>)}
            </tr>
          </thead>
          <tbody>
            {d.porVersion.map((v) => (
              <tr key={v.version} style={{ borderTop: '1px solid var(--line)', textAlign: 'right' }}>
                <td style={{ textAlign: 'left', padding: '5px 6px', color: 'var(--t1)', fontWeight: 700 }}>{v.version}</td>
                <td style={{ padding: '5px 6px' }}>{v.partidos}</td>
                <td style={{ padding: '5px 6px' }}>{v.aciertos}</td>
                {visibles.map((c) => {
                  const e = v.estrategias[c]
                  return (
                    <td key={c} style={{ padding: '5px 6px' }}>
                      {e && e.apuestas ? (
                        <><b style={{ color: colorDe(e.ganancia) }}>{signo(e.ganancia)}</b> <span style={{ color: 'var(--t3)' }}>({pct(e.roi, 0)})</span></>
                      ) : <span style={{ color: 'var(--t3)' }}>sin apuestas</span>}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function FilaApuesta({ a, visibles }: { a: ApuestaSimulada; visibles: { clave: EstrategiaClave; color: string }[] }) {
  const cerrada = a.estado === 'cerrada'
  const acierto = cerrada && a.resultado === a.elegido
  return (
    <div style={{ ...tarjeta, padding: '11px 13px' }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>{fecha(a.pitazo)}</span>
        <span style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)' }}>{a.partido.local} – {a.partido.visita}</span>
        {a.partido.liga && <span style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>{a.partido.liga}</span>}
        {a.alerta?.activa && (
          <span title={a.alerta.motivos.map((m) => m.detalle).join(' · ')}
            style={{ padding: '1px 6px', borderRadius: 5, font: '700 9.5px var(--sans)', background: 'var(--down-soft)', color: 'var(--down)' }}>
            ⚠ desconfiar
          </span>
        )}
        {a.marcador && (
          <span title={`Marcador más probable del modelo de goles: ${a.marcador.masProbable} (${num(100 * a.marcador.prob, 0)} %) · ${a.marcador.alineado ? 'va con el elegido' : 'no va con el elegido'}`}
            style={{ padding: '1px 6px', borderRadius: 5, font: '700 9.5px var(--mono)', fontVariantNumeric: 'tabular-nums', border: `1px solid ${a.marcador.alineado ? 'var(--sim-metodo-marcador)' : 'var(--line)'}`, color: a.marcador.alineado ? 'var(--sim-metodo-marcador)' : 'var(--t3)' }}>
            ⚽ {a.marcador.masProbable}
          </span>
        )}
        <span style={{
          marginLeft: 'auto', padding: '2px 8px', borderRadius: 6, font: '700 10px var(--sans)',
          background: !cerrada ? 'var(--bg3)' : acierto ? 'var(--up-soft)' : 'var(--down-soft)',
          color: !cerrada ? 'var(--t2)' : acierto ? 'var(--up)' : 'var(--down)',
        }}>
          {!cerrada ? 'por jugarse' : `${acierto ? '✓' : '✗'} salió ${RES[a.resultado!]}`}
        </span>
      </div>

      {/* LA VERSIÓN DE CADA SKILL con la que se escribió el parte */}
      <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginTop: 6 }} title={`parte depositado ${fecha(a.depositadoEn)} · prompt ${a.versionPrompt}`}>
        {SKILL_CORTO.map(([s, c]) => a.versiones[s] ? (
          <span key={s} style={{ padding: '1px 6px', borderRadius: 5, border: '1px solid var(--line)', font: '600 9.5px var(--mono)', color: s === 'sad-analysis' ? 'var(--t1)' : 'var(--t2)' }}>
            {c} {a.versiones[s]}
          </span>
        ) : null)}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 6, marginTop: 8 }}>
        {(['local', 'empate', 'visita'] as Resultado1x2[]).map((k) => {
          const elegido = a.elegido === k
          const salio = a.resultado === k
          return (
            <div key={k} style={{ padding: '5px 7px', borderRadius: 8, background: salio ? 'var(--bg3)' : 'transparent', border: `1px solid ${elegido ? 'var(--accent)' : 'var(--line)'}`, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap', font: '600 9.5px var(--sans)', color: 'var(--t3)' }}>
                {RES[k]}{elegido ? ' · elegido' : ''}{elegido && <SemaforoChip s={a.semaforo} corta />}
              </div>
              <div style={{ font: '700 12px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
                {num(a.probabilidades[k], 0)} % <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>@ {num(a.cuotas[k])}</span>
              </div>
              <div style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>mercado {num(a.mercado[k], 0)} %</div>
            </div>
          )
        })}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 3, marginTop: 8 }}>
        {visibles.map((v) => {
          const r = a.porEstrategia[v.clave]
          if (!r) return null
          return (
            <div key={v.clave} style={{ display: 'grid', gridTemplateColumns: '10px 76px minmax(0,1fr)', alignItems: 'baseline', columnGap: 7, font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
              <span style={{ width: 10, height: 2, background: v.color, alignSelf: 'center' }} />
              <span style={{ color: 'var(--t2)', fontFamily: 'var(--sans)', fontWeight: 600 }}>{CORTO[v.clave]}</span>
              {r.seleccion ? (
                <span style={{ minWidth: 0 }}>
                  {num(r.monto)} u a {RES[r.seleccion]}{r.linea ? <span style={{ color: 'var(--t3)' }}> (línea {r.linea})</span> : null}
                  {r.ganancia != null && <> · <b style={{ color: colorDe(r.ganancia) }}>{signo(r.ganancia)}</b></>}
                  {r.banca != null && <span style={{ color: 'var(--t3)' }}> · banca {num(r.banca)}</span>}
                </span>
              ) : (
                <span style={{ color: 'var(--t3)', minWidth: 0 }}>
                  {r.motivo === 'sin plata libre'
                    ? 'no apuesta: toda la banca está en juego en otros partidos'
                    : ['proporcional', 'metodoVerde', 'metodoFueraMedio', 'martingalaFueraMedio', 'martingalaFueraMedioTope'].includes(v.clave) ? `no apuesta: ${r.motivo}`
                    : v.clave === 'plana60' || v.clave === 'martingala60' || v.clave === 'martingala60Ajustada' ? `no apuesta: el elegido tiene ${num(a.probabilidades[a.elegido], 0)} %, bajo el 60 %`
                    : v.clave.startsWith('kelly') ? `no apuesta: sin ventaja (mejor f* ${signo(100 * a.kelly.fraccion, 1)} % en ${RES[a.kelly.seleccion]})` : 'no apuesta: banca en cero'}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
