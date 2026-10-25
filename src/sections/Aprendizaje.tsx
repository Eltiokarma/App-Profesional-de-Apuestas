import { useEffect, useRef, useState } from 'react'
import type { TablaConfianzaDTO, DerrotaFavorito, DerrotasFavoritoDTO, ExplicacionDerrota, InventarioLecciones, LeccionItem, ModoFalloEtiqueta, RevisionSkillDTO, SkillAprendizaje } from '../api/types'
import { getDataSource } from '../services/datasource'
import { useAsync } from '../services/useAsync'
import { COLOR_TRAMO } from '../lib/confianza'

/** Fase C del bucle de aprendizaje (docs/APRENDIZAJE.md).
 *
 *  Lo que esta pantalla NO hace, y es la mitad del diseño: no promedia
 *  poblaciones, no publica una tasa sin su `n`, no muestra un Brier sin su
 *  línea de base, y no deja que una lección de un caso contaminado parezca que
 *  puede mover un peso. La app tampoco mueve nada sola: abrir la revisión es
 *  abrirla, no autorizarla. */

const MODO_FALLO_NOMBRE: Record<ModoFalloEtiqueta, string> = {
  insumo: 'insumo', lectura_efe: 'lectura EFE', tde: 'TDE', reventon: 'reventón',
  mercado: 'mercado', imprevisto: 'imprevisto', varianza: 'varianza', no_lo_dice: 'no lo dice',
}
const COLOR_VER: Record<string, string> = {
  acierto: 'var(--up)', parcial: 'var(--mark)', fallo: 'var(--down)',
}
const SUAVE_VER: Record<string, string> = {
  acierto: 'var(--up-soft)', parcial: 'var(--mark-soft)', fallo: 'var(--down-soft)',
}
const ETIQUETA_ESTADO: Record<string, string> = {
  pendiente: 'PENDIENTE', en_revision: 'EN REVISIÓN', aplicada: 'APLICADA', descartada: 'DESCARTADA',
}

type Pestana = 'skills' | 'metricas' | 'derrotas' | 'cuarentena' | 'sinSkill'
const POR_PAGINA = 20

/** REORDENADA EL 25/10/2026 (usuario: «no encuentro nada, todo se ve
 *  desordenado y lento»). Con 2.886 lecciones la pantalla bajaba todo de una
 *  vez (46 s, 6,3 MB) y las apilaba en una sola columna: lo que había que hacer
 *  —cerrar lo que la versión vigente ya leyó— quedaba enterrado. Ahora abre con
 *  un RESUMEN (sin lecciones), una pestaña por cosa, las acciones del skill
 *  ARRIBA de su lista y las lecciones de a 20. */
export function Aprendizaje({ isMobile }: { isMobile: boolean }) {
  // LA COHORTE VIGENTE ES LA VISTA POR DEFECTO. Los casos de la primera semana
  // se hicieron con el DT viejo y el TDE sin nivel: la etiqueta de población
  // dice «ciega» y el insumo estaba roto. Se ven, pero aparte.
  const [cohorte, setCohorte] = useState('vigente')
  const [recarga, setRecarga] = useState(0)
  const [pestana, setPestana] = useState<Pestana>('skills')
  const [skillSel, setSkillSel] = useState('')
  const inv = useAsync<InventarioLecciones>(
    () => getDataSource().lecciones({ cohorte, resumen: true }),
    cohorte)
  // reload (no un key nuevo): el resumen se rehace sin desmontar la pantalla
  const recargar = () => { inv.reload(); setRecarga((n) => n + 1) }

  if (inv.loading && !inv.data) {
    return <Marco><span style={{ font: '500 12px var(--sans)', color: 'var(--t3)' }}>Cargando lo aprendido… (la primera lectura del día tarda: recalcula cada veredicto)</span></Marco>
  }
  if (inv.error || !inv.data) {
    return (
      <Marco>
        <span style={{ font: '500 12px var(--sans)', color: 'var(--down)' }}>
          No se pudo leer el inventario de lecciones: {inv.error ?? 'sin datos'}
        </span>
      </Marco>
    )
  }
  const d = inv.data
  const skills = d.porSkill
  const sel = skills.find((s) => s.skill === skillSel)
    ?? [...skills].sort((x, y) => (y.lecciones.pendiente ?? 0) - (x.lecciones.pendiente ?? 0))[0]
  const pendientesTotal = skills.reduce((s, x) => s + (x.lecciones.pendiente ?? 0), 0)
  const cerrablesTotal = skills.reduce((s, x) => s + (x.anterioresAlCorte ?? 0), 0)
  const cuar = d.enCuarentena?.cuantas ?? 0
  const pestanas: [Pestana, string][] = [
    ['skills', `Lecciones por skill · ${pendientesTotal} pend.`],
    ['metricas', 'Métricas · confianza'],
    ['derrotas', 'Derrotas del favorito'],
    ...(cuar ? [['cuarentena', `Cuarentena · ${cuar}`] as [Pestana, string]] : []),
    ...(d.sinSkill.cuantas ? [['sinSkill', `Sin skill · ${d.sinSkill.cuantas}`] as [Pestana, string]] : []),
  ]

  return (
    <div style={{ padding: isMobile ? '16px 14px 40px' : '22px 26px 48px', maxWidth: 1080 }}>
      <h1 style={{ font: '800 26px var(--sans)', color: 'var(--t1)', margin: '0 0 4px' }}>Aprendizaje</h1>
      <div style={{ font: '500 12px var(--sans)', color: 'var(--t3)', marginBottom: 14 }}>
        Lo que el bucle aprendió, por skill · las lecciones salen de los veredictos y se
        recalculan al leer
      </div>

      {/* LA COHORTE: de qué época del proceso son los casos que se están
          mirando. Se sella al depositar y no cambia con un re-depósito. */}
      {d.cohortes && d.cohortes.length > 0 && (
        <div style={{ marginBottom: 12 }} title={d.notaCohortes}>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px', marginRight: 2 }}>COHORTE</span>
            {[{ clave: '', etiqueta: 'todas', casos: d.cohortes.reduce((a, c) => a + c.casos, 0), descripcion: 'todas las épocas juntas: sirve para contar, no para calibrar' },
              ...d.cohortes.map((c) => ({ clave: c.vigente ? 'vigente' : c.clave, etiqueta: c.vigente ? `vigente · ${c.clave}` : c.clave, casos: c.casos, descripcion: c.descripcion }))]
              .map((c) => {
                const on = cohorte === c.clave
                return (
                  <button key={c.clave || 'todas'} onClick={() => setCohorte(c.clave)} title={c.descripcion}
                    style={{ padding: '5px 10px', borderRadius: 8, border: `1px solid ${on ? 'var(--accent)' : 'var(--line)'}`, background: on ? 'var(--bg3)' : 'transparent', color: on ? 'var(--t1)' : 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
                    {c.etiqueta} <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>· {c.casos}</span>
                  </button>
                )
              })}
            {inv.loading && <span style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>actualizando…</span>}
          </div>
          {cohorte && cohorte !== 'vigente' && (
            <DescartarCohorte cohorte={cohorte}
              pendientes={pendientesTotal + (d.sinSkill.cuantas ?? 0)}
              onHecho={recargar} />
          )}
        </div>
      )}

      {/* LO QUE HAY QUE HACER, ARRIBA: con versiones nuevas subidas, lo que su
          dossier ya leyó se cierra en bloque. Un aviso, no un listado. */}
      {cerrablesTotal > 0 && (
        <div style={{ marginBottom: 12, padding: '10px 13px', borderRadius: 11, background: 'var(--mark-soft)', font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
          <b>{cerrablesTotal}</b> lecciones pendientes son de partidos anteriores a la versión vigente de su skill: esa versión ya las leyó.
          Se cierran por skill con <b>«Cerrar las anteriores»</b> (modo administrador 🔑):{' '}
          {skills.filter((s) => (s.anterioresAlCorte ?? 0) > 0).map((s, i, arr) => (
            <span key={s.skill}>
              <button onClick={() => { setPestana('skills'); setSkillSel(s.skill) }}
                style={{ padding: 0, border: 0, background: 'none', color: 'var(--accent)', cursor: 'pointer', font: '600 11.5px var(--sans)', textDecoration: 'underline' }}>
                {s.skill} ({s.anterioresAlCorte})
              </button>{i < arr.length - 1 ? ' · ' : ''}
            </span>
          ))}
        </div>
      )}

      {/* flexWrap: cinco pestañas no entran en una fila de teléfono */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 2, padding: 3, borderRadius: 10, background: 'var(--bg2)', border: '1px solid var(--line)', marginBottom: 14 }}>
        {pestanas.map(([k, label]) => (
          <button key={k} onClick={() => setPestana(k)}
            style={{ padding: '7px 12px', border: 0, borderRadius: 8, cursor: 'pointer', background: pestana === k ? 'var(--bg3)' : 'transparent', color: pestana === k ? 'var(--t1)' : 'var(--t2)', font: `${pestana === k ? 700 : 600} 11.5px var(--sans)` }}>
            {label}
          </button>
        ))}
      </div>

      {pestana === 'skills' && (
        skills.length === 0
          ? (
            <Seccion titulo="TODAVÍA NO HAY NADA">
              <div style={{ font: '500 12px var(--sans)', color: 'var(--t2)' }}>
                Ningún veredicto dejó lección todavía. Esto se llena solo: cada caso que se cierra
                con una lección por lado aparece acá con su partido.
              </div>
            </Seccion>
          )
          : (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: isMobile ? 'minmax(0,1fr) minmax(0,1fr)' : `repeat(${Math.min(skills.length, 5)}, minmax(0,1fr))`, gap: 8, marginBottom: 12 }}>
                {skills.map((s) => (
                  <TarjetaSkill key={s.skill} sk={s} activa={sel?.skill === s.skill} onClick={() => setSkillSel(s.skill)} />
                ))}
              </div>
              {sel && <PanelSkill key={`${sel.skill}|${cohorte}`} sk={sel} cohorte={cohorte} recarga={recarga} onCambio={recargar} />}
            </>
          )
      )}

      {pestana === 'metricas' && <Metricas d={d} />}

      {pestana === 'derrotas' && <DerrotasDelFavorito cohorte={cohorte} />}

      {/* LO APARTADO SE VE, PARA QUE NADIE LO OLVIDE NI LO DISIMULE. */}
      {pestana === 'cuarentena' && d.enCuarentena && (
        <Seccion titulo={`EN CUARENTENA · ${d.enCuarentena.cuantas}`} nota={d.enCuarentena.porque}>
          <ListaLecciones cohorte={cohorte} de="cuarentena" recarga={recarga} onCambio={recargar} />
        </Seccion>
      )}

      {pestana === 'sinSkill' && (
        <Seccion titulo={`SIN SKILL DECLARADO · ${d.sinSkill.cuantas}`} nota={d.sinSkill.porque}>
          <ListaLecciones cohorte={cohorte} de="sinSkill" recarga={recarga} onCambio={recargar} />
        </Seccion>
      )}
    </div>
  )
}

function TarjetaSkill({ sk, activa, onClick }: { sk: SkillAprendizaje; activa: boolean; onClick: () => void }) {
  const pend = sk.lecciones.pendiente ?? 0
  const cerr = sk.anterioresAlCorte ?? 0
  return (
    <button onClick={onClick}
      style={{ textAlign: 'left', minWidth: 0, padding: '10px 12px', borderRadius: 12, cursor: 'pointer', background: activa ? 'var(--bg3)' : 'var(--bg2)', border: `1px solid ${activa ? 'var(--accent)' : 'var(--line)'}` }}>
      <div style={{ font: '700 11.5px var(--sans)', color: 'var(--t1)', overflowWrap: 'anywhere' }}>{sk.skill}</div>
      <div style={{ font: '600 9.5px var(--mono)', color: 'var(--t3)', marginTop: 1 }}>{sk.versionVigente || 'sin versión'}</div>
      <div style={{ font: '800 20px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums', marginTop: 4 }}>{pend}</div>
      <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)' }}>pendiente{pend === 1 ? '' : 's'} · {sk.lecciones.aplicada ?? 0} aplicada{(sk.lecciones.aplicada ?? 0) === 1 ? '' : 's'}</div>
      {cerr > 0 && <div style={{ font: '700 9.5px var(--mono)', color: 'var(--mark)', marginTop: 4 }}>{cerr} para cerrar</div>}
      {sk.revisionAbierta && <div style={{ font: '700 9.5px var(--mono)', color: 'var(--mark)', marginTop: 2 }}>REVISIÓN ABIERTA</div>}
    </button>
  )
}

/** Las lecciones de a 20: un filtro (skill · estado · cuarentena) pide su
 *  página al backend, «ver más» trae la siguiente. */
function ListaLecciones({ cohorte, skill, de, estado, recarga, onCambio }: {
  cohorte: string; skill?: string; de?: 'cuarentena' | 'sinSkill'; estado?: string; recarga: number; onCambio: () => void
}) {
  const [items, setItems] = useState<LeccionItem[]>([])
  const [total, setTotal] = useState(0)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const filtro = `${cohorte}|${skill ?? ''}|${de ?? ''}|${estado ?? ''}`
  const pedir = (desde: number, cuantas: number) =>
    getDataSource().lecciones({ cohorte, skill, de, estado, desde, cuantas })
  // un cambio de filtro empieza de cero; una recarga (lección movida) rehace
  // lo que ya estaba a la vista, sin volver a la primera página
  const visibles = useRef(POR_PAGINA)
  const filtroPrevio = useRef(filtro)
  useEffect(() => {
    let vivo = true
    if (filtroPrevio.current !== filtro) {
      filtroPrevio.current = filtro
      visibles.current = POR_PAGINA
      setItems([])
    }
    setCargando(true)
    setError('')
    pedir(0, Math.min(500, visibles.current))
      .then((r) => { if (vivo) { setItems(r.items); setTotal(r.total ?? r.items.length) } })
      .catch((e) => { if (vivo) setError(e instanceof Error ? e.message : 'no se pudieron leer') })
      .finally(() => { if (vivo) setCargando(false) })
    return () => { vivo = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtro, recarga])
  async function verMas() {
    setCargando(true)
    try {
      const r = await pedir(items.length, POR_PAGINA)
      visibles.current = items.length + r.items.length
      setItems((xs) => [...xs, ...r.items])
      setTotal(r.total ?? total)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudieron leer')
    } finally {
      setCargando(false)
    }
  }
  if (cargando && items.length === 0) return <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', padding: '6px 0' }}>Cargando lecciones…</div>
  return (
    <div>
      {error && <div style={{ font: '500 11px var(--sans)', color: 'var(--down)', marginBottom: 6 }}>No se pudieron leer: {error}</div>}
      {items.length === 0
        ? <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', padding: '6px 0' }}>Ninguna lección con este filtro.</div>
        : items.map((i) => <Leccion key={i.clave} it={i} onCambio={onCambio} />)}
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', paddingTop: 10, borderTop: items.length ? '1px solid var(--line)' : 0 }}>
        <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t3)' }}>{items.length} de {total}</span>
        {items.length < total && (
          <button onClick={verMas} disabled={cargando}
            style={{ padding: '6px 11px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '600 11px var(--sans)', cursor: 'pointer' }}>
            {cargando ? 'Cargando…' : `Ver ${Math.min(POR_PAGINA, total - items.length)} más`}
          </button>
        )}
      </div>
    </div>
  )
}

/** LA CONFIANZA DEL 1X2 POR TRAMO (25/10/2026, pedido del usuario): lo que
 *  dijimos del elegido contra lo que salió y lo que le daba el mercado, por
 *  versión de sad-analysis. Un tramo que acierta menos de lo que dice está
 *  sobreconfiado; con n chico el intervalo manda, no el punto. */
function TablaConfianza({ t }: { t: TablaConfianzaDTO }) {
  const [todas, setTodas] = useState(false)
  const bloques = todas
    ? [{ version: 'todas las versiones', desde: '', hasta: '', n: t.todas.reduce((s, x) => s + x.n, 0), aciertos: t.todas.reduce((s, x) => s + x.aciertos, 0), tramos: t.todas }]
    : t.porVersion
  const celda: React.CSSProperties = { font: '600 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums', textAlign: 'right', whiteSpace: 'nowrap' }
  const cab: React.CSSProperties = { font: '700 9px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px', textAlign: 'right' }
  const columnas = 'minmax(0,1.1fr) minmax(0,.6fr) minmax(0,.9fr) minmax(0,1.7fr) minmax(0,.9fr)'
  return (
    <Seccion titulo="CONFIANZA DEL 1X2 · POR TRAMO" nota={t.nota}>
      <div style={{ display: 'flex', gap: 6, marginBottom: 10, flexWrap: 'wrap' }}>
        {[['por versión', false], ['todas juntas', true]].map(([label, v]) => (
          <button key={String(label)} onClick={() => setTodas(v as boolean)}
            style={{ padding: '5px 10px', borderRadius: 8, border: `1px solid ${todas === v ? 'var(--accent)' : 'var(--line)'}`, background: todas === v ? 'var(--bg3)' : 'transparent', color: todas === v ? 'var(--t1)' : 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
            {label as string}
          </button>
        ))}
      </div>
      {bloques.length === 0 && <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)' }}>Sin casos ciegos con 1X2 declarado en esta cohorte.</div>}
      {bloques.map((b) => (
        <div key={b.version} style={{ marginBottom: 14 }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap', marginBottom: 6 }}>
            <span style={{ font: '700 12.5px var(--sans)', color: 'var(--t1)' }}>sad-analysis {b.version}</span>
            {b.desde && <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>{b.desde} → {b.hasta}</span>}
            <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t2)' }}>
              acertó {b.aciertos}/{b.n}{b.n ? ` · ${Math.round((100 * b.aciertos) / b.n)}%` : ''}
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: columnas, gap: '6px 8px', alignItems: 'center' }}>
            <span style={{ ...cab, textAlign: 'left' }}>TRAMO</span>
            <span style={cab}>N</span>
            <span style={cab}>DIJIMOS</span>
            <span style={cab}>ACERTÓ</span>
            <span style={cab}>MERCADO</span>
            {b.tramos.map((x) => {
              const color = COLOR_TRAMO[x.tramo]
              // sobreconfiado de verdad: ni el techo del intervalo llega a lo dicho
              const sobre = x.intervalo && x.dijimos !== null && x.intervalo[1] * 100 < x.dijimos
              const bajo = x.intervalo && x.dijimos !== null && x.intervalo[0] * 100 > x.dijimos
              return [
                <span key={x.tramo + 't'} style={{ justifySelf: 'start', padding: '2px 7px', borderRadius: 6, background: `color-mix(in oklch, ${color}, transparent 84%)`, font: '700 10.5px var(--mono)', color }}>{x.tramo}</span>,
                <span key={x.tramo + 'n'} style={celda}>{x.n}</span>,
                <span key={x.tramo + 'd'} style={celda}>{x.dijimos === null ? '—' : `${Math.round(x.dijimos)}%`}</span>,
                <span key={x.tramo + 'a'} style={{ ...celda, color: sobre ? 'var(--down)' : bajo ? 'var(--up)' : 'var(--t1)' }}
                  title={x.intervalo ? `intervalo de Wilson al 95 %: ${Math.round(x.intervalo[0] * 100)}–${Math.round(x.intervalo[1] * 100)}%` : undefined}>
                  <b>{x.aciertos}/{x.n}</b> · {x.tasa === null ? '—' : `${Math.round(x.tasa * 100)}%`}
                  {/* el intervalo debajo: en una línea no entra a 360 px */}
                  {x.intervalo && <span style={{ display: 'block', color: 'var(--t3)', fontWeight: 500, fontSize: 9.5 }}>[{Math.round(x.intervalo[0] * 100)}–{Math.round(x.intervalo[1] * 100)}%]</span>}
                </span>,
                <span key={x.tramo + 'm'} style={celda} title={x.nMercado < x.n ? `con cuotas ${x.nMercado} de ${x.n}` : undefined}>{x.mercado === null ? '—' : `${Math.round(x.mercado)}%`}</span>,
              ]
            })}
          </div>
        </div>
      ))}
      <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>
        <b style={{ color: 'var(--down)' }}>Rojo</b>: el intervalo entero queda por debajo de lo que dijimos (sobreconfiado) ·{' '}
        <b style={{ color: 'var(--up)' }}>verde</b>: por encima (subconfiado). Los colores del tramo son los de la marca en Partidos.
      </div>
    </Seccion>
  )
}

/** Población y lo medible: lo que antes abría la pantalla, ahora en su pestaña. */
function Metricas({ d }: { d: InventarioLecciones }) {
  const a = d.acreditables
  return (
    <>
      {a.confianza && <TablaConfianza t={a.confianza} />}
      {/* LA POBLACIÓN VA ANTES QUE CUALQUIER NÚMERO. Un porcentaje que mezcla
          casos ciegos con casos sembrados no es una métrica pesimista ni
          optimista: es otra cosa con el mismo nombre. */}
      <Seccion titulo="LA POBLACIÓN MANDA" >
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 8 }}>
          {(['ciega', 'por_resultado', 'post_resultado', 'cuarentena'] as const).map((k) => {
            const p = d.poblacion[k]
            const n = typeof p === 'object' ? p : { casos: 0, lados: 0 }
            const ciega = k === 'ciega'
            const cuar = k === 'cuarentena'
            return (
              <div key={k} title={cuar ? 'apartados por criterio (qué le faltaba al parte antes del pitazo), nunca por resultado: no cuentan ni fijan rúbrica' : undefined}
                style={{ flex: 1, minWidth: 140, padding: '11px 13px', borderRadius: 11, background: ciega ? 'var(--up-soft)' : cuar ? 'var(--down-soft)' : 'var(--bg3)' }}>
                <div style={{ font: '700 9.5px var(--mono)', color: ciega ? 'var(--up)' : cuar ? 'var(--down)' : 'var(--t3)', letterSpacing: '.4px' }}>
                  {k.replace('_', ' ').toUpperCase()}
                </div>
                <div style={{ font: '800 21px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{n.casos}</div>
                <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)' }}>
                  {n.casos === 1 ? 'caso' : 'casos'} · {n.lados} {n.lados === 1 ? 'lado' : 'lados'}
                </div>
              </div>
            )
          })}
        </div>
        <div style={{ font: '500 11px var(--sans)', color: 'var(--t2)' }}>{String(d.poblacion.nota ?? '')}</div>
      </Seccion>

      <Seccion titulo="LO MEDIBLE" nota={a.criterio}>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <Cifra etiqueta="TASA DE ACIERTO" valor={a.tasaAcierto === null ? '—' : `${Math.round(a.tasaAcierto * 100)}%`}
            pie={a.tasaAcierto === null ? (a.tasaNota || 'sin n') : `n = ${a.lados} lados · ${a.casos} casos`} />
          <Cifra etiqueta="1X2" valor={a.unXDos.tasa === null ? '—' : `${a.unXDos.aciertos}/${a.unXDos.de}`}
            pie={a.unXDos.de ? 'aciertos sobre casos con reparto declarado' : 'sin reparto declarado'} />
          <Cifra etiqueta="BRIER" valor={a.brier.media === null ? '—' : a.brier.media.toFixed(3)}
            pie={a.brier.lineaBase === null ? a.brier.nota
              : `línea de base ${a.brier.lineaBase.toFixed(3)} · n = ${a.brier.n}`}
            color={a.brier.media === null ? undefined : a.brier.mejorQueLaBase ? 'var(--up)' : 'var(--down)'} />
          <Cifra etiqueta="VENTANA TDE" valor={`${a.ventanaTde.conGol}/${a.ventanaTde.observadas}`}
            pie={a.ventanaTde.sinFicha ? `${a.ventanaTde.sinFicha} sin ficha: no comprobable` : 'comprobadas contra los goles recibidos'} />
          {a.reventon && (
            <Cifra etiqueta="REVENTÓN" valor={`${a.reventon.reventadas}/${a.reventon.observadas}`}
              pie={a.reventon.observadas ? `burbujas que reventaron · tasa base del backtest ${Math.round(a.reventon.tasaBaseBacktest * 100)}%` : 'sin burbujas comprobadas en población ciega'}
              color={a.reventon.revisionAbierta ? 'var(--down)' : undefined} />
          )}
        </div>
        {a.reventon && a.reventon.observadas > 0 && (
          <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 5 }}>
            <div style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px' }}>REVENTÓN POR NIVEL DE RIESGO · observado vs backtest</div>
            {Object.entries(a.reventon.porNivel).filter(([, c]) => c.observadas > 0).map(([nivel, c]) => (
              <div key={nivel} style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', font: '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
                <span style={{ width: 70, color: 'var(--t1)', fontWeight: 700 }}>{nivel}</span>
                <span>{c.reventadas}/{c.observadas}{c.tasa !== null ? ` · ${Math.round(c.tasa * 100)}%` : ''}</span>
                {/* EL INTERVALO, NO EL PUNTO. 6 de 21 (29 %) contra 42–47 % parece
                    fuera; el intervalo [14 %, 50 %] dice que es ruido. */}
                {c.intervalo && (
                  <span style={{ color: 'var(--t3)' }} title="intervalo de Wilson al 95 % de la tasa observada">
                    [{Math.round(c.intervalo[0] * 100)}–{Math.round(c.intervalo[1] * 100)}%]
                  </span>
                )}
                <span style={{ color: 'var(--t3)' }}>
                  {c.esperadoBacktest ? `backtest ${Math.round(c.esperadoBacktest[0] * 100)}–${Math.round(c.esperadoBacktest[1] * 100)}%` : 'sin base en el backtest'}
                </span>
                <span style={{ color: c.dentroDelBacktest === null ? 'var(--t3)' : c.dentroDelBacktest ? 'var(--up)' : 'var(--down)', fontWeight: 700 }}>
                  {c.dentroDelBacktest === null ? `n < ${c.nMinimo}: no se compara` : c.dentroDelBacktest ? 'compatible' : 'FUERA'}
                </span>
              </div>
            ))}
            {/* ¿EL 1X2 RESPETÓ LA BURBUJA? Solo lados con riesgo alto: si el
                pronóstico siguió la racha o no, y cómo le fue a cada grupo. Un
                Brier peor en «a favor» es la evidencia de que el riesgo vale. */}
            {a.reventon.respetoRiesgo && (['aFavor', 'enContra', 'neutro'] as const).some((g) => (a.reventon!.respetoRiesgo![g].lados > 0)) && (
              <div style={{ marginTop: 6, display: 'flex', flexDirection: 'column', gap: 4 }}>
                <div style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px' }}>CON RIESGO ALTO · ¿EL 1X2 SIGUIÓ LA RACHA?</div>
                {(['aFavor', 'enContra', 'neutro'] as const).map((g) => {
                  const c = a.reventon!.respetoRiesgo![g]
                  if (!c.lados) return null
                  return (
                    <div key={g} style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', font: '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
                      <span style={{ width: 70, color: 'var(--t1)', fontWeight: 700 }}>{g === 'aFavor' ? 'a favor' : g === 'enContra' ? 'en contra' : 'empate'}</span>
                      <span>{c.lados} {c.lados === 1 ? 'lado' : 'lados'}</span>
                      <span style={{ color: 'var(--t3)' }}>1X2 {c.aciertos1x2}/{c.lados}{c.tasa1x2 !== null ? ` · ${Math.round(c.tasa1x2 * 100)}%` : ''}</span>
                      <span style={{ color: 'var(--t3)' }}>{c.brierMedio !== null ? `Brier ${c.brierMedio.toFixed(3)}` : 'sin Brier'}</span>
                      <span style={{ color: 'var(--t3)' }}>reventó {c.reventadas}/{c.lados}</span>
                    </div>
                  )
                })}
              </div>
            )}
            {a.reventon.extremo.observadas > 0 && (
              <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }} title={a.reventon.extremo.nota}>
                con alerta K-EXTREMO: {a.reventon.extremo.reventadas}/{a.reventon.extremo.observadas} reventaron
              </div>
            )}
            {a.reventon.revisionAbierta && (
              <div style={{ marginTop: 4, padding: '9px 12px', borderRadius: 10, background: 'var(--down-soft)', font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
                Nivel{a.reventon.fueraDelBacktest.length > 1 ? 'es' : ''} <b>{a.reventon.fueraDelBacktest.join(', ')}</b>: el rango del backtest no toca el intervalo observado, con n suficiente.
                Esto ABRE la revisión de los puntos del riesgo (docs/REVENTON.md §11); no los mueve.
              </div>
            )}
          </div>
        )}
        {/* ¿LA ESPINA DE LA BURBUJA ACIERTA? Adónde dijo el analista que iba la K
            de cada equipo contra adónde fue, frente a la frecuencia de cada movimiento */}
        {a.espina && a.espina.lados > 0 && (
          <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 4 }} title={a.espina.nota}>
            <div style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px' }}>ESPINA DE LA BURBUJA · ¿adónde fue la K?</div>
            {(['positiva', 'cero', 'negativa'] as const).map((k) => {
              const c = a.espina![k]
              if (!c.lados) return null
              return (
                <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', font: '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
                  <span style={{ width: 70, color: k === 'positiva' ? 'var(--up)' : k === 'negativa' ? 'var(--down)' : 'var(--mark)', fontWeight: 700 }}>{k}</span>
                  <span>acertó {c.aciertos}/{c.lados}{c.tasa !== null ? ` · ${Math.round(c.tasa * 100)}%` : ''}</span>
                  {c.intervalo && <span style={{ color: 'var(--t3)' }}>[{Math.round(c.intervalo[0] * 100)}–{Math.round(c.intervalo[1] * 100)}%]</span>}
                  {c.frecuenciaDelMovimiento !== null && <span style={{ color: 'var(--t3)' }}>frecuencia {Math.round(c.frecuenciaDelMovimiento * 100)}%</span>}
                  {c.sobreLaFrecuencia !== null && <span style={{ color: c.sobreLaFrecuencia ? 'var(--up)' : 'var(--t3)', fontWeight: 700 }}>{c.sobreLaFrecuencia ? 'SOBRE LA FRECUENCIA' : 'no la supera'}</span>}
                </div>
              )
            })}
            <div style={{ font: '600 10.5px var(--mono)', color: a.espina.lectura === 'acierta más que la frecuencia' ? 'var(--up)' : 'var(--t3)' }}>
              {a.espina.lectura === 'sin n' ? `menos de ${a.espina.nMinimo} lados por lectura: todavía no se compara` : a.espina.lectura}
            </div>
            {/* ¿qué burbuja lee mejor: la total o la de la condición (local/visita)? */}
            {a.espina.porGuia && (['total', 'condicion'] as const).map((g) => {
              const m = a.espina!.porGuia![g]
              if (!m || !m.lados) return null
              const juzg = (['positiva', 'cero', 'negativa'] as const).map((k) => m[k])
              const ac = juzg.reduce((s, c) => s + c.aciertos, 0)
              const n = juzg.reduce((s, c) => s + c.lados, 0)
              return (
                <div key={g} style={{ font: '500 10.5px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
                  {g === 'total' ? 'con la K total' : 'con la K de la condición'}: acertó {ac}/{n}
                  {n ? ` · ${Math.round((ac / n) * 100)}%` : ''} · {m.lectura === 'sin n' ? 'sin n todavía' : m.lectura}
                </div>
              )
            })}
          </div>
        )}
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 10, font: '600 10.5px var(--mono)', color: 'var(--t3)' }}>
          {(['acierto', 'parcial', 'fallo'] as const).map((v) => (
            <span key={v} style={{ color: COLOR_VER[v] }}>{a.veredictos[v] ?? 0} {v}</span>
          ))}
        </div>
        {a.brier.media !== null && !a.brier.mejorQueLaBase && (
          <div style={{ marginTop: 9, padding: '9px 12px', borderRadius: 10, background: 'var(--down-soft)', font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
            El Brier está por encima de su línea de base: en esta muestra el reparto declarado
            todavía no le gana a predecir la frecuencia observada.
          </div>
        )}
        <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)', marginTop: 8 }}>{a.brier.escala}</div>
      </Seccion>

    </>
  )
}

function PanelSkill({ sk, cohorte, recarga, onCambio }: { sk: SkillAprendizaje; cohorte: string; recarga: number; onCambio: () => void }) {
  const [estado, setEstado] = useState('pendiente')
  const [verMas, setVerMas] = useState(false)
  return (
    <section style={{ marginBottom: 14, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '13px 16px 8px', flexWrap: 'wrap' }}>
        <span style={{ font: '700 14px var(--sans)', color: 'var(--t1)' }}>{sk.skill}</span>
        {sk.versionVigente && <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t3)' }}>vigente {sk.versionVigente}</span>}
        {(['acierto', 'parcial', 'fallo'] as const).map((v) => (
          (sk.atribuidos[v] ?? 0) > 0 && (
            <span key={v} style={{ padding: '2px 8px', borderRadius: 6, background: SUAVE_VER[v], color: COLOR_VER[v], font: '700 9.5px var(--mono)' }}>
              {sk.atribuidos[v]} {v}
            </span>
          )
        ))}
      </div>

      {/* LA ACCIÓN, ARRIBA DE LA LISTA (25/10/2026): antes vivía dentro del
          dossier, que había que abrir, al final de cada tarjeta */}
      <CerrarAnteriores sk={sk} onCambio={onCambio} />

      <div style={{ padding: '0 16px 10px' }}>
        <button onClick={() => setVerMas(!verMas)}
          style={{ padding: 0, border: 0, background: 'none', color: 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
          {verMas ? '▾' : '▸'} Revisión, listón y fallos por causa
          <span style={{ color: sk.revisionAbierta ? 'var(--mark)' : 'var(--t3)', fontWeight: 700 }}>
            {' '}· {sk.revisionAbierta ? 'REVISIÓN ABIERTA' : `faltan ${sk.faltanParaDisparar} fallo${sk.faltanParaDisparar === 1 ? '' : 's'} para abrirla`}
          </span>
        </button>
      </div>
      {verMas && (
        <>
          {/* EL SESGO SE LEE ANTES QUE LOS CONTEOS, NO DESPUÉS. */}
          <div style={{ padding: '0 16px 10px', font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>
            {sk.sesgoDeAtribucion}
            {sk.porModoFallo && sk.porModoFallo.fallos > 0 && (
              <span style={{ display: 'block', marginTop: 4, font: '500 10.5px var(--mono)', color: 'var(--t2)' }}>
                fallos por causa: {Object.entries(sk.porModoFallo.porModo).map(([m, n]) => `${MODO_FALLO_NOMBRE[m as ModoFalloEtiqueta] ?? m} ${n}`).join(' · ') || '—'}
                {sk.porModoFallo.sinEtiqueta ? ` · sin etiqueta ${sk.porModoFallo.sinEtiqueta}` : ''}
                {sk.porModoFallo.pidenMoverSinPoder.length ? <b style={{ color: 'var(--down)' }}> · {sk.porModoFallo.pidenMoverSinPoder.length} piden mover un número sin poder sostenerlo</b> : null}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', gap: 10, padding: '0 16px 12px', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: 210, padding: '10px 12px', borderRadius: 11, background: sk.revisionAbierta ? 'var(--mark-soft)' : 'var(--bg3)' }}>
              <div style={{ font: '700 9.5px var(--mono)', color: sk.revisionAbierta ? 'var(--mark)' : 'var(--t3)', letterSpacing: '.4px' }}>
                {sk.revisionAbierta ? 'REVISIÓN ABIERTA' : 'REVISIÓN NO DISPARADA'}
              </div>
              <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', marginTop: 3 }}>
                {sk.revisionAbierta
                  ? `${sk.fallosPendientes} fallos con lección pendiente`
                  : `faltan ${sk.faltanParaDisparar} fallo${sk.faltanParaDisparar === 1 ? '' : 's'} con lección pendiente`}
              </div>
              <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)', marginTop: 3 }}>{sk.disparador}</div>
            </div>
            {sk.liston && (
              <div style={{ flex: 1, minWidth: 210, padding: '10px 12px', borderRadius: 11, background: sk.liston.cumple ? 'var(--up-soft)' : 'var(--bg3)' }}>
                <div style={{ font: '700 9.5px var(--mono)', color: sk.liston.cumple ? 'var(--up)' : 'var(--t3)', letterSpacing: '.4px' }}>
                  EL LISTÓN DEL PROPIO SKILL
                </div>
                <div style={{ font: '600 12px var(--mono)', color: 'var(--t1)', marginTop: 3 }}>{sk.liston.semaforo}</div>
                <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)', marginTop: 3 }}>{sk.liston.nota}</div>
              </div>
            )}
          </div>
          <Dossier skill={sk.skill} abierta={sk.revisionAbierta} onCambio={onCambio} />
        </>
      )}

      <div style={{ padding: '4px 16px 14px', borderTop: '1px solid var(--line)' }}>
        {/* flexWrap: cinco estados no entran en una fila de teléfono (360 px) */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '10px 0 4px', flexWrap: 'wrap' }}>
          <span style={{ font: '700 10px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>LECCIONES</span>
          <div style={{ display: 'flex', flexWrap: 'wrap', padding: 3, borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
            {([...ESTADOS_ORDEN.map((e) => [e, `${ETIQUETA_ESTADO[e]?.toLowerCase() ?? e} · ${sk.lecciones[e] ?? 0}`]), ['', 'todas']] as [string, string][]).map(([k, label]) => (
              <button key={k || 'todas'} onClick={() => setEstado(k)}
                style={{ padding: '5px 10px', border: 0, borderRadius: 7, cursor: 'pointer', background: estado === k ? 'var(--bg3)' : 'transparent', color: estado === k ? 'var(--t1)' : 'var(--t2)', font: '600 10.5px var(--sans)' }}>
                {label}
              </button>
            ))}
          </div>
        </div>
        <ListaLecciones cohorte={cohorte} skill={sk.skill} estado={estado} recarga={recarga} onCambio={onCambio} />
      </div>
    </section>
  )
}

const ESTADOS_ORDEN = ['pendiente', 'en_revision', 'aplicada', 'descartada']

/** Cerrar en bloque lo que la versión vigente ya leyó (25/10/2026): con
 *  cuatro versiones salidas de los dossiers, nada estaba marcado aplicada. El
 *  número sale del resumen; el cierre lo hace el backend con la misma regla. */
function CerrarAnteriores({ sk, onCambio }: { sk: SkillAprendizaje; onCambio: () => void }) {
  const [paso, setPaso] = useState<'' | 'confirmar' | 'yendo'>('')
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  const n = sk.anterioresAlCorte
  if (n === undefined || n === null || !sk.versionVigente) return null
  async function cerrar() {
    setError('')
    setPaso('yendo')
    try {
      const r = await getDataSource().cerrarAnteriores(sk.skill)
      setMsg(`${r.cerradas} lecciones cerradas (${Object.entries(r.porVersion ?? { [r.version]: r.cerradas }).map(([v, k]) => `${k} en ${v}`).join(' · ')}); quedan ${r.quedanPendientes} pendientes`)
      onCambio()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudieron cerrar')
    } finally {
      setPaso('')
    }
  }
  const boton: React.CSSProperties = { padding: '7px 12px', borderRadius: 8, border: 0, cursor: 'pointer', font: '700 11px var(--sans)' }
  return (
    <div style={{ margin: '0 16px 10px', padding: '10px 12px', borderRadius: 11, background: n > 0 ? 'var(--mark-soft)' : 'var(--bg3)', display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
      {n > 0 ? (
        <>
          <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 200 }}>
            <b>{n}</b> pendiente{n === 1 ? '' : 's'} de partidos anteriores a <b>{sk.versionVigente}</b>: esa versión ya las leyó.
            {paso !== '' && ' Quedan como aplicadas en la versión que las leyó; las posteriores siguen para el próximo dossier.'}
          </span>
          {paso === '' && (
            <button onClick={() => setPaso('confirmar')} style={{ ...boton, background: 'var(--accent)', color: '#fff' }}
              title="modo administrador (🔑)">
              Cerrar las {n} anteriores a {sk.versionVigente}
            </button>
          )}
          {paso !== '' && (
            <>
              <button onClick={cerrar} disabled={paso === 'yendo'} style={{ ...boton, background: 'var(--accent)', color: '#fff' }}>
                {paso === 'yendo' ? 'Cerrando…' : 'Sí, cerrar'}
              </button>
              <button onClick={() => setPaso('')} disabled={paso === 'yendo'}
                style={{ ...boton, background: 'transparent', color: 'var(--t2)', border: '1px solid var(--line)' }}>Cancelar</button>
            </>
          )}
        </>
      ) : (
        <span style={{ font: '500 11px var(--sans)', color: 'var(--t2)' }}>
          Al día con <b>{sk.versionVigente}</b>: lo pendiente es de partidos posteriores, para el próximo dossier.
        </span>
      )}
      {msg && <span style={{ flexBasis: '100%', font: '600 11px var(--sans)', color: 'var(--up)' }}>{msg}</span>}
      {error && <span style={{ flexBasis: '100%', font: '600 11px var(--sans)', color: 'var(--down)' }}>{error}{/permiso|401|403|token/i.test(error) ? ' — activá el modo administrador (🔑) con la llave maestra' : ''}</span>}
    </div>
  )
}

/** Fase D: el dossier de revisión del skill. Se pide al abrirlo (no en cada
 *  carga) y dice, calculado, qué puede y qué no puede salir de la revisión.
 *  «Abrir la revisión» pasa las lecciones a EN REVISIÓN: no aplica nada. */
function Dossier({ skill, abierta, onCambio }: { skill: string; abierta: boolean; onCambio: () => void }) {
  const [ver, setVer] = useState(false)
  const [d, setD] = useState<RevisionSkillDTO | null>(null)
  const [error, setError] = useState('')
  const [yendo, setYendo] = useState(false)

  async function cargar() {
    setError('')
    try {
      setD(await getDataSource().revisionSkill(skill))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudo leer el dossier')
    }
  }
  async function abrir() {
    setError('')
    setYendo(true)
    try {
      await getDataSource().abrirRevision(skill)
      await cargar()
      onCambio()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudo abrir la revisión')
    } finally {
      setYendo(false)
    }
  }

  const boton: React.CSSProperties = { padding: '6px 11px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '600 11px var(--sans)', cursor: 'pointer' }
  return (
    <div style={{ padding: '0 16px 12px' }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <button style={{ ...boton, borderColor: abierta ? 'var(--mark)' : 'var(--line)' }}
          onClick={() => { const v = !ver; setVer(v); if (v && !d) cargar() }}>
          {ver ? 'Cerrar dossier' : abierta ? 'Ver dossier de la revisión' : 'Ver dossier'}
        </button>
        {ver && d?.abierta && d.lecciones.some((i) => i.estado === 'pendiente') && (
          <button style={boton} disabled={yendo} onClick={abrir}>
            {yendo ? 'Abriendo…' : `Abrir la revisión (${d.lecciones.filter((i) => i.estado === 'pendiente').length} a en revisión)`}
          </button>
        )}
      </div>
      {error && <div style={{ font: '500 11px var(--sans)', color: 'var(--down)', marginTop: 6 }}>{error}</div>}
      {ver && d && (
        <div style={{ marginTop: 10, padding: '12px 14px', borderRadius: 11, background: 'var(--bg)', border: '1px solid var(--line)', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'baseline' }}>
            <span style={{ font: '700 9.5px var(--mono)', color: d.abierta ? 'var(--mark)' : 'var(--t3)', letterSpacing: '.4px' }}>
              DOSSIER · {d.abierta ? 'REVISIÓN ABIERTA' : 'NO DISPARADA'}
            </span>
            {d.versionVigente && <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>versión vigente {d.versionVigente}</span>}
            {!!d.enRevision && <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>{d.enRevision} en revisión</span>}
          </div>
          <div style={{ font: '600 12px var(--sans)', color: 'var(--t1)', lineHeight: 1.45 }}>{d.lectura}</div>

          {d.porRegla.length > 0 && (
            <div>
              <div style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px', marginBottom: 5 }}>POR REGLA DEL SKILL</div>
              {d.porRegla.map((r) => (
                <div key={r.regla} style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'baseline', padding: '5px 0', borderTop: '1px solid var(--line)' }}>
                  <span style={{ font: '700 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 120 }}>{r.regla}</span>
                  <span style={{ font: '600 10px var(--mono)', color: 'var(--t2)' }}>
                    {r.lecciones} lección{r.lecciones === 1 ? '' : 'es'} · {r.fallos} fallo{r.fallos === 1 ? '' : 's'}
                    {r.parciales ? ` · ${r.parciales} parcial${r.parciales === 1 ? '' : 'es'}` : ''}
                  </span>
                  <span style={{ font: '700 10px var(--mono)', color: r.acreditables ? 'var(--up)' : 'var(--t3)' }}>
                    {r.acreditables ? `${r.acreditables} acreditable${r.acreditables === 1 ? '' : 's'}` : 'solo rúbrica'}
                  </span>
                  {r.pidenMoverNumero > 0 && (
                    <span style={{ font: '700 10px var(--mono)', color: r.pidenMoverYPueden ? 'var(--mark)' : 'var(--down)' }}>
                      {r.pidenMoverNumero} piden mover un número{r.pidenMoverYPueden < r.pidenMoverNumero ? ` (${r.pidenMoverNumero - r.pidenMoverYPueden} sin poder)` : ''}
                    </span>
                  )}
                  {Object.keys(r.porModoFallo).length > 0 && (
                    <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', flexBasis: '100%' }}>
                      causa: {Object.entries(r.porModoFallo).map(([m, n]) => `${MODO_FALLO_NOMBRE[m as ModoFalloEtiqueta] ?? m} ${n}`).join(' · ')}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}

          {d.liston && (
            <div style={{ font: '500 11px var(--sans)', color: 'var(--t2)' }}>
              <b style={{ color: d.liston.cumple ? 'var(--up)' : 'var(--t1)' }}>Listón del skill:</b> {d.liston.semaforo}
            </div>
          )}
          {d.sesgoDeAtribucion && <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>{d.sesgoDeAtribucion}</div>}

          <ol style={{ margin: 0, paddingLeft: 18, font: '500 10.5px var(--sans)', color: 'var(--t3)', lineHeight: 1.5 }}>
            {d.flujo.map((f, i) => <li key={i}>{f}</li>)}
          </ol>
        </div>
      )}
    </div>
  )
}

/** Las cohortes viejas (rodaje, c2) no calibran: sus pendientes se descartan
 *  de una vez en vez de una por una. La vigente no tiene este botón. */
function DescartarCohorte({ cohorte, pendientes, onHecho }: { cohorte: string; pendientes: number; onHecho: () => void }) {
  const [confirmar, setConfirmar] = useState(false)
  const [yendo, setYendo] = useState(false)
  const [msg, setMsg] = useState('')
  if (!pendientes && !msg) return null
  async function descartar() {
    setYendo(true)
    setMsg('')
    try {
      const r = await getDataSource().descartarCohorte(cohorte, `descarte en bloque de la cohorte ${cohorte}: no calibra`)
      setMsg(`${r.descartadas} lecciones pasaron a descartada`)
      setConfirmar(false)
      onHecho()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'no se pudo descartar')
    } finally {
      setYendo(false)
    }
  }
  return (
    <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
      {pendientes > 0 && !confirmar && (
        <button onClick={() => setConfirmar(true)}
          title="esta cohorte no calibra nada: sus lecciones pendientes pasan a descartada de una vez (modo administrador)"
          style={{ padding: '6px 11px', borderRadius: 8, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
          Descartar las {pendientes} pendientes de {cohorte}
        </button>
      )}
      {confirmar && (
        <>
          <span style={{ font: '500 11px var(--sans)', color: 'var(--t1)' }}>
            ¿Pasar las {pendientes} pendientes de {cohorte} a descartada? Se puede deshacer una por una.
          </span>
          <button onClick={descartar} disabled={yendo}
            style={{ padding: '6px 11px', borderRadius: 8, border: 0, cursor: 'pointer', background: 'var(--down)', color: '#fff', font: '600 10.5px var(--sans)' }}>
            {yendo ? '…' : 'Sí, descartar'}
          </button>
          <button onClick={() => setConfirmar(false)} disabled={yendo}
            style={{ padding: '6px 11px', borderRadius: 8, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
            Cancelar
          </button>
        </>
      )}
      {msg && <span style={{ font: '600 11px var(--sans)', color: 'var(--t2)' }}>{msg}</span>}
    </div>
  )
}

function Leccion({ it, onCambio }: { it: LeccionItem; onCambio: () => void }) {
  const [abierto, setAbierto] = useState(false)
  const [desmAbierto, setDesmAbierto] = useState(false)
  const [fuente, setFuente] = useState('')
  const [version, setVersion] = useState(it.aplicadaEn)
  const [error, setError] = useState('')
  const [yendo, setYendo] = useState('')
  const [cuarAbierta, setCuarAbierta] = useState(false)
  const [motivo, setMotivo] = useState('')

  async function mover(estado: string) {
    setError('')
    setYendo(estado)
    try {
      await getDataSource().moverLeccion(it.clave, { estado, aplicadaEn: version })
      onCambio()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudo mover')
    } finally {
      setYendo('')
    }
  }

  // EL BANCO DE LA API TAMBIÉN SE EQUIVOCA: la automática por DT equivocado le
  // cree a la alineación de API-Football, que a veces trae a un DT que ya se
  // fue. Se desmiente por lado y con la fuente que lo prueba; el parte no se toca.
  async function desmentir(lado: 'a' | 'b') {
    setError('')
    setYendo('desmentir')
    try {
      await getDataSource().desmentirBanco(it.fixtureId, { lado, fuente })
      setDesmAbierto(false)
      onCambio()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudo desmentir el banco')
    } finally {
      setYendo('')
    }
  }

  // CUARENTENA POR CRITERIO, NUNCA POR RESULTADO: el motivo es qué le faltaba
  // al parte antes del pitazo. Es del caso entero (los dos lados), y la pone
  // el usuario con el token maestro.
  async function cuarentena(poner: boolean) {
    setError('')
    setYendo('cuarentena')
    try {
      if (poner) await getDataSource().cuarentena(it.fixtureId, motivo)
      else await getDataSource().quitarCuarentena(it.fixtureId)
      setCuarAbierta(false)
      onCambio()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudo cambiar la cuarentena')
    } finally {
      setYendo('')
    }
  }

  // LO DE CADA LECCIÓN, PLEGADO (25/10/2026): con cientos en la lista, ocho
  // chips y tres botones por lección no dejaban leer ninguna
  const [det, setDet] = useState(false)
  return (
    <div style={{ padding: '10px 0', borderTop: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 9, flexWrap: 'wrap' }}>
        {it.origen === 'reventon'
          ? <span title={`estudio de un reventón hacia atrás · mecanismo: ${it.mecanismo ?? ''}`}
              style={{ font: '700 10px var(--mono)', color: 'var(--accent)', textTransform: 'uppercase' }}>
              reventón{it.mecanismo ? ` · ${it.mecanismo.replace(/_/g, ' ')}` : ''}
            </span>
          : <span style={{ font: '700 10px var(--mono)', color: COLOR_VER[it.veredicto as 'acierto'], textTransform: 'uppercase' }}>{it.veredicto}</span>}
        <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)' }}>{it.equipo}</span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }}>{it.partido} · {it.fecha}</span>
        <span style={{ marginLeft: 'auto', padding: '2px 8px', borderRadius: 6, background: 'var(--bg3)', color: 'var(--t2)', font: '700 9px var(--mono)' }}>
          {ETIQUETA_ESTADO[it.estado] ?? it.estado}{it.aplicadaEn ? ` · ${it.aplicadaEn}` : ''}
        </span>
      </div>
      <div style={{ font: '500 12px var(--sans)', color: 'var(--t1)', marginTop: 5 }}>{it.leccion}</div>
      {it.reglaTocada && (
        <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', marginTop: 3 }}>regla tocada: {it.reglaTocada}</div>
      )}
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', marginTop: 5 }}>
        <button onClick={() => setDet(!det)}
          style={{ padding: 0, border: 0, background: 'none', color: 'var(--t2)', cursor: 'pointer', font: '600 10px var(--sans)' }}>
          {det ? '▾ ocultar' : '▸ detalles y acciones'}
        </button>
        <span style={{ font: '600 9.5px var(--mono)', color: it.puedeMoverNumeros ? 'var(--up)' : 'var(--t3)' }}>
          {it.seleccion} · {it.modoEvaluacion}{it.puedeMoverNumeros ? ' · acredita' : ''}
        </span>
        {it.proponeMoverNumero === true && !it.puedeMoverNumeros && (
          <span style={{ font: '700 9px var(--mono)', color: 'var(--down)' }}>PIDE MOVER UN NÚMERO SIN PODER</span>
        )}
        {it.cuarentena && <span style={{ font: '600 9.5px var(--mono)', color: 'var(--down)' }}>en cuarentena: {it.cuarentena}</span>}
      </div>
      {det && <>
      {/* LA ETIQUETA DE JEV: de qué naturaleza fue el fallo y si la lección pide
          mover un número. Agrupa para el dossier, no puntúa nada. La alarma es
          «pide mover un número» sobre un caso que no puede sostenerlo. */}
      {(it.modoFallo || it.proponeMoverNumero !== undefined) && (it.modoFallo || it.proponeMoverNumero !== null) && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 5 }}>
          {it.modoFallo && (
            <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--bg3)', color: 'var(--t2)', font: '700 9px var(--mono)' }}>
              {MODO_FALLO_NOMBRE[it.modoFallo] ?? it.modoFallo}{it.modoFalloConfianza != null ? ` · ${Math.round(it.modoFalloConfianza * 100)}%` : ''}
            </span>
          )}
          {it.proponeMoverNumero === true && (
            <span style={{ padding: '2px 8px', borderRadius: 6, background: it.puedeMoverNumeros ? 'var(--up-soft)' : 'var(--down-soft)', color: it.puedeMoverNumeros ? 'var(--up)' : 'var(--down)', font: '700 9px var(--mono)' }}>
              {it.puedeMoverNumeros ? 'PIDE MOVER UN NÚMERO' : 'PIDE MOVER UN NÚMERO · NO PUEDE SOSTENERLO'}
            </span>
          )}
        </div>
      )}

      {/* LO CONTAMINADO ENSEÑA, PERO NO MUEVE UN NÚMERO. Esto va pegado a la
          lección, no en una nota al pie de la sección: quien lee el dossier
          seis meses después no va a recordar la distinción de memoria. */}
      <div style={{ display: 'inline-block', marginTop: 6, padding: '3px 9px', borderRadius: 7, background: it.puedeMoverNumeros ? 'var(--up-soft)' : 'var(--bg3)', color: it.puedeMoverNumeros ? 'var(--up)' : 'var(--t2)', font: '600 10px var(--sans)' }}>
        {it.seleccion} · {it.modoEvaluacion} — {it.queAutoriza}
      </div>
      {it.mancha && (
        <div style={{ font: '500 10.5px var(--sans)', color: 'var(--mark)', marginTop: 4 }}>salvedad declarada: {it.mancha}</div>
      )}
      {(it.cohorte || it.cuarentena) && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 5 }}>
          {it.cohorte && <span style={{ font: '600 9.5px var(--mono)', color: 'var(--t3)', padding: '2px 7px', borderRadius: 6, border: '1px solid var(--line)' }}>cohorte {it.cohorte}</span>}
          {it.cuarentena && <span style={{ font: '600 9.5px var(--mono)', color: 'var(--down)', padding: '2px 7px', borderRadius: 6, background: 'var(--down-soft)' }}>en cuarentena: {it.cuarentena}</span>}
        </div>
      )}

      <div style={{ marginTop: 7, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        <button onClick={() => setAbierto(!abierto)}
          style={{ padding: '4px 10px', borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', cursor: 'pointer', font: '600 10px var(--sans)' }}>
          {abierto ? 'Cerrar' : 'Mover de estado'}
        </button>
        {it.cuarentena && it.cuarentenaAutomatica && (it.dtEquivocado ?? []).length > 0 ? (
          <button onClick={() => setDesmAbierto(!desmAbierto)}
            title="la puso la app porque el DT del parte no es el del banco de la API. Si el que está mal es el banco (un DT que ya se fue), se desmiente con la fuente"
            style={{ padding: '4px 10px', borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', cursor: 'pointer', font: '600 10px var(--sans)' }}>
            {desmAbierto ? 'Cancelar' : 'El banco de la API está mal…'}
          </button>
        ) : it.cuarentena && it.cuarentenaAutomatica ? (
          <span title="la puso la app: el parte no declara DT en un lado. Se levanta re-depositando el parte con el DT"
            style={{ padding: '4px 10px', borderRadius: 7, border: '1px solid var(--line)', color: 'var(--t3)', font: '600 10px var(--sans)' }}>
            automática · se levanta con el DT en el parte
          </span>
        ) : it.cuarentena ? (
          <button onClick={() => cuarentena(false)} disabled={!!yendo}
            style={{ padding: '4px 10px', borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', cursor: 'pointer', font: '600 10px var(--sans)' }}>
            {yendo === 'cuarentena' ? '…' : 'Quitar la cuarentena'}
          </button>
        ) : (
          <button onClick={() => setCuarAbierta(!cuarAbierta)}
            title="aparta el caso entero del aprendizaje, por lo que le faltaba al parte antes del pitazo; nunca porque falló"
            style={{ padding: '4px 10px', borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t3)', cursor: 'pointer', font: '600 10px var(--sans)' }}>
            {cuarAbierta ? 'Cancelar' : 'Cuarentena…'}
          </button>
        )}
      </div>
      {desmAbierto && (
        <div style={{ marginTop: 8, padding: '10px 12px', borderRadius: 10, background: 'var(--bg3)' }}>
          <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t1)', marginBottom: 6 }}>
            Fuente que prueba que ese DT NO dirigió el partido (su salida anunciada antes, la crónica con el banco real).
            El DT del parte no se cambia; ese lado deja de compararse contra la alineación de la API.
          </div>
          <input value={fuente} onChange={(e) => setFuente(e.target.value)} placeholder="link o nota de prensa (mínimo 8 caracteres)"
            style={{ width: '100%', boxSizing: 'border-box', padding: '6px 9px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '500 11px var(--mono)', marginBottom: 7 }} />
          <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
            {(it.dtEquivocado ?? []).map((m) => (
              <button key={m.lado} onClick={() => desmentir(m.lado)} disabled={!!yendo || fuente.trim().length < 8}
                style={{ padding: '6px 11px', borderRadius: 8, border: 0, cursor: 'pointer', background: 'var(--accent)', color: '#fff', font: '600 10.5px var(--sans)', opacity: fuente.trim().length < 8 ? 0.5 : 1, overflowWrap: 'anywhere', textAlign: 'left' }}>
                {yendo === 'desmentir' ? '…' : `Lado ${m.lado}: el banco «${m.banco}» está mal (el parte dice «${m.parte}»)`}
              </button>
            ))}
          </div>
          {error && <div style={{ font: '600 11px var(--sans)', color: 'var(--down)', marginTop: 5 }}>{error}</div>}
        </div>
      )}
      {cuarAbierta && !it.cuarentena && (
        <div style={{ marginTop: 8, padding: '10px 12px', borderRadius: 10, background: 'var(--down-soft)' }}>
          <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t1)', marginBottom: 6 }}>
            Motivo: qué le faltaba a ESTE parte antes del pitazo («DT viejo», «TDE sin nivel», «rodaje: primera semana»).
            Un fallo no es motivo. Se guarda el veredicto que tenía el caso al ponerla.
          </div>
          <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
            <input value={motivo} onChange={(e) => setMotivo(e.target.value)} placeholder="motivo (mínimo 12 caracteres)"
              style={{ flex: 1, minWidth: 190, padding: '6px 9px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '500 11px var(--mono)' }} />
            <button onClick={() => cuarentena(true)} disabled={!!yendo || motivo.trim().length < 12}
              style={{ padding: '6px 11px', borderRadius: 8, border: 0, cursor: 'pointer', background: 'var(--down)', color: '#fff', font: '600 10.5px var(--sans)', opacity: motivo.trim().length < 12 ? 0.5 : 1 }}>
              {yendo === 'cuarentena' ? '…' : 'Poner en cuarentena'}
            </button>
          </div>
        </div>
      )}
      {abierto && (
        <div style={{ marginTop: 8, padding: '10px 12px', borderRadius: 10, background: 'var(--bg3)' }}>
          <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap', alignItems: 'center' }}>
            <input value={version} onChange={(e) => setVersion(e.target.value)}
              placeholder="versión del skill (obligatoria para aplicada)"
              style={{ flex: 1, minWidth: 190, padding: '6px 9px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '500 11px var(--mono)' }} />
            {(['en_revision', 'aplicada', 'descartada', 'pendiente'] as const).map((e) => (
              <button key={e} onClick={() => mover(e)} disabled={!!yendo}
                style={{ padding: '6px 11px', borderRadius: 8, border: 0, cursor: yendo ? 'wait' : 'pointer', background: e === 'aplicada' ? 'var(--accent)' : 'var(--bg2)', color: e === 'aplicada' ? '#fff' : 'var(--t1)', font: '600 10.5px var(--sans)' }}>
                {yendo === e ? '…' : ETIQUETA_ESTADO[e].toLowerCase()}
              </button>
            ))}
          </div>
          <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)', marginTop: 6 }}>
            Marcar «aplicada» exige la versión donde entró: sin eso el cambio no se puede
            auditar después.
          </div>
          {error && <div style={{ font: '600 11px var(--sans)', color: 'var(--down)', marginTop: 5 }}>{error}</div>}
        </div>
      )}
      </>}
    </div>
  )
}

/** LAS DERROTAS DEL FAVORITO (21/10/2026, pedido del usuario: «las derrotas no
 *  esperadas las podremos justificar con eso»). Por cada una, lo que el TDE y
 *  el DTP habían escrito ANTES del pitazo. La disciplina 9 del TDE manda la
 *  lectura: una rama escrita que describe cómo se perdió es evidencia; una
 *  explicación armada después de ver el gol, no. Se carga a pedido: recalcula
 *  el objetivo de cada veredicto y no hace falta en cada visita. */
const EXPLICACION: Record<ExplicacionDerrota, [string, string, string]> = {
  rama_escrita: ['RAMA ESCRITA', 'var(--up)', 'el escenario que se jugó estaba descrito antes'],
  rama_sin_escribir: ['SIN ESCRIBIR', 'var(--down)', 'la rama que se jugó no estaba declarada'],
  sin_ficha: ['SIN FICHA', 'var(--t3)', 'sin eventos no se sabe quién marcó primero'],
  sin_goles: ['SIN GOLES', 'var(--t3)', 'sin goles no hay rama'],
}
const RAMA_NOMBRE: Record<string, string> = {
  siMarcaPrimero: 'marcó primero', siRecibePrimero: 'recibió primero', siLeEmpatan: 'le empataron', sinGoles: 'sin goles',
}
const SALIDA: Record<string, string> = { concedio: 'volvió a conceder', marco: 'marcó él', sinMasGoles: 'sin más goles' }

function DerrotasDelFavorito({ cohorte }: { cohorte: string }) {
  // tiene su pestaña: abrirla ya es pedirla
  const [ver, setVer] = useState(true)
  const [d, setD] = useState<DerrotasFavoritoDTO | null>(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)
  const [de, setDe] = useState('')
  async function cargar() {
    setError('')
    setCargando(true)
    try {
      setD(await getDataSource().derrotasFavorito(cohorte))
      setDe(cohorte)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudieron leer las derrotas')
    } finally {
      setCargando(false)
    }
  }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { cargar() }, [cohorte])
  const vieja = d !== null && de !== cohorte
  return (
    <Seccion titulo="DERROTAS DEL FAVORITO" nota="el equipo que el 1X2 declarado daba ganador y perdió, con lo que el TDE y el DTP habían escrito ANTES del pitazo: solo cuenta lo declarado">
      <button onClick={() => { const v = !ver; setVer(v); if (v && (!d || vieja)) cargar() }}
        style={{ padding: '6px 11px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '600 11px var(--sans)', cursor: 'pointer' }}>
        {ver ? 'Ocultar' : 'Ver las derrotas del favorito'}
      </button>
      {cargando && <span style={{ marginLeft: 8, font: '500 11px var(--sans)', color: 'var(--t3)' }}>Cargando…</span>}
      {error && <div style={{ font: '500 11px var(--sans)', color: 'var(--down)', marginTop: 6 }}>{error}</div>}
      {ver && d && !vieja && (
        <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {(Object.keys(EXPLICACION) as ExplicacionDerrota[]).map((k) => (
              <span key={k} title={EXPLICACION[k][2]}
                style={{ padding: '4px 9px', borderRadius: 7, background: 'var(--bg3)', font: '700 10px var(--mono)', color: EXPLICACION[k][1] }}>
                {EXPLICACION[k][0]} · {d.resumen[k] ?? 0}
              </span>
            ))}
          </div>
          <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>{d.nota}</div>
          {d.derrotas.length === 0 && (
            <div style={{ font: '500 12px var(--sans)', color: 'var(--t2)' }}>Ninguna derrota del favorito declarado en esta cohorte.</div>
          )}
          {d.derrotas.map((x) => <TarjetaDerrota key={x.fixtureId} x={x} />)}
        </div>
      )}
    </Seccion>
  )
}

function TarjetaDerrota({ x }: { x: DerrotaFavorito }) {
  const [etq, color] = EXPLICACION[x.explicacion]
  const lo = x.tde.loDeclarado
  const linea = (r?: { sob1?: number | null; tipologia?: string; nota?: string; ventana?: string } | null) =>
    r ? [r.sob1 != null ? `SOB1 ${r.sob1}` : '', r.tipologia, r.nota, r.ventana ? `ventana ${r.ventana}` : ''].filter(Boolean).join(' · ') : ''
  const goles = x.goles.map((g) => `${g.minuto}' ${g.lado === x.favorito.lado ? x.favorito.equipo : 'rival'}`).join(' · ')
  return (
    <div style={{ padding: '10px 12px', borderRadius: 11, background: 'var(--bg)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'baseline' }}>
        <span style={{ font: '700 12px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0 }}>{x.partido}</span>
        <span style={{ font: '700 12px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{x.marcador}</span>
        <span style={{ font: '700 9.5px var(--mono)', color }}>{etq}</span>
      </div>
      <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)', marginTop: 2 }}>
        {x.fecha} · favorito {x.favorito.equipo}{x.favorito.probabilidad != null ? ` (${x.favorito.probabilidad}%)` : ''} · {x.seleccion || 'sin población'}{x.cuarentena ? ' · en cuarentena' : ''}
        {goles ? ` · goles: ${goles}` : ''}
      </div>
      <div style={{ marginTop: 6, font: '500 11.5px var(--sans)', color: 'var(--t1)', lineHeight: 1.45 }}>
        <b>TDE del favorito:</b> {x.tde.ramaJugada ? `${RAMA_NOMBRE[x.tde.ramaJugada] ?? x.tde.ramaJugada}${x.tde.minuto != null ? ` (${x.tde.minuto}')` : ''}` : 'rama desconocida'}
        {lo ? ` → escrito: ${linea(lo)}` : x.tde.ramaJugada && x.tde.ramaJugada !== 'sinGoles' ? ' → nada escrito para esa rama' : ''}
        {x.tde.segundoGiro && ` · le empataron al ${x.tde.segundoGiro.minuto}'${x.tde.segundoGiro.loDeclarado ? ` → escrito: ${linea(x.tde.segundoGiro.loDeclarado)}` : x.tde.segundoGiro.noEvaluable ? ' (línea del empate no evaluable: el servidor la rechazaba)' : ' (línea del empate sin escribir)'}`}
        {x.tde.salida && ` · después: ${SALIDA[x.tde.salida] ?? x.tde.salida}`}
      </div>
      {x.dtpViasRival.length > 0 && (
        <div style={{ marginTop: 4, font: '500 11.5px var(--sans)', color: 'var(--t2)' }}>
          <b>DTP · vías de gol del rival escritas:</b> {x.dtpViasRival.join(' · ')}
        </div>
      )}
      {x.leccion && (
        <div style={{ marginTop: 4, font: '500 11.5px var(--sans)', color: 'var(--t2)' }}>
          <b>Autopsia:</b> {x.leccion}
        </div>
      )}
    </div>
  )
}

function Seccion({ titulo, nota, children }: { titulo: string; nota?: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 14, padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ font: '700 10px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px', marginBottom: 4 }}>{titulo}</div>
      {nota && <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)', marginBottom: 9 }}>{nota}</div>}
      {children}
    </section>
  )
}

function Cifra({ etiqueta, valor, pie, color }: { etiqueta: string; valor: string; pie: string; color?: string }) {
  return (
    <div style={{ flex: 1, minWidth: 150, padding: '11px 13px', borderRadius: 11, background: 'var(--bg3)' }}>
      <div style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px' }}>{etiqueta}</div>
      <div style={{ font: '800 22px var(--mono)', color: color ?? 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{valor}</div>
      <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)' }}>{pie}</div>
    </div>
  )
}

function Marco({ children }: { children: React.ReactNode }) {
  return <div style={{ padding: '22px 26px' }}>{children}</div>
}
