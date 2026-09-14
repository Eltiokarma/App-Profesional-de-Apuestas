// El parte de Cowork en pantalla (docs/COWORK.md).
//
// Lo que se pinta aquí no costó créditos: lo escribió Cowork con la
// suscripción y lo depositó, y todo lo que es número —total, porcentaje, IP,
// reducción por zona, ramas— lo calculó el backend con las fórmulas del
// protocolo. Esta pantalla NO recalcula nada: si un número está mal, está mal
// en el backend, y hay un test que lo dice.
//
// La pieza central es el bloque F. De noche llega CONGELADO (ninguna fuente
// publica el once a esa hora) y se muestra como dos ramas: el piso y el techo
// razonable del impacto. Cuando el once aparece —de la ficha ya ingestada o
// del pantallazo que el usuario pega aquí— el bloque se cierra al instante.
import { useEffect, useMemo, useState } from 'react'
import type {
  DisponibilidadParte, DocumentoParte, EquipoParte, JugadorParte, ParteCoworkDTO, RamaF, Semaforo, TdeParte,
  VeredictoParte, ZonaF,
} from '../api/types'
import { parsearMd, type MdBloque, type MdInline } from '../lib/md'
import { parsearOnce } from '../lib/once'
import { loadCalendarioSad, resolverXiParte, type PartidoCalendarioUI } from '../services/appdata'
import { CalendarioSad } from './CalendarioSad'
import { TimelineComparativo } from './TimelineComparativo'

const COLOR: Record<Semaforo, string> = { verde: 'var(--up)', ambar: 'var(--mark)', rojo: 'var(--down)' }
const SUAVE: Record<Semaforo, string> = { verde: 'var(--up-soft)', ambar: 'var(--mark-soft)', rojo: 'var(--down-soft)' }
const CLASIF = {
  FORMADO: { label: 'FORMADO', sem: 'verde' as Semaforo },
  EN_FORMACION: { label: 'EN FORMACIÓN', sem: 'ambar' as Semaforo },
  SIN_FORMACION: { label: 'SIN FORMACIÓN', sem: 'rojo' as Semaforo },
}
const BLOQUE_NOMBRE = { A: 'Cuerpo técnico', B: 'Plantel', C: 'Constantes K', D: 'Coherencia táctica', E: 'Rendimiento' } as const
const ROL_LABEL: Record<string, string> = { TF: '🔴 Titular fijo', TH: '🟠 Titular habitual', ROT: '🟡 Rotación', SUP: '⚪ Suplente' }
const ZONAS: ZonaF[] = ['GK', 'DEF', 'MID', 'ATK']

// ── markdown ────────────────────────────────────────────────────────────────

function Inline({ hijos }: { hijos: MdInline[] }) {
  return (
    <>
      {hijos.map((h, i) =>
        h.t === 'b' ? <b key={i} style={{ color: 'var(--t1)' }}>{h.v}</b>
          : h.t === 'i' ? <i key={i}>{h.v}</i>
            : h.t === 'code' ? <code key={i} style={{ padding: '1px 5px', borderRadius: 5, background: 'var(--bg3)', font: '600 11px var(--mono)' }}>{h.v}</code>
              : <span key={i}>{h.v}</span>)}
    </>
  )
}

function Markdown({ texto }: { texto: string }) {
  const bloques = useMemo(() => parsearMd(texto), [texto])
  const tam = { 1: 16, 2: 14, 3: 12.5 } as const
  return (
    <div style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', lineHeight: 1.6 }}>
      {bloques.map((b: MdBloque, i) => {
        if (b.tipo === 'h') {
          return <div key={i} style={{ margin: i ? '14px 0 6px' : '0 0 6px', font: `800 ${tam[b.nivel]}px var(--sans)`, color: 'var(--t1)', letterSpacing: '-.2px' }}><Inline hijos={b.hijos} /></div>
        }
        if (b.tipo === 'p') return <p key={i} style={{ margin: '0 0 9px' }}><Inline hijos={b.hijos} /></p>
        if (b.tipo === 'lista') {
          const Tag = b.ordenada ? 'ol' : 'ul'
          return <Tag key={i} style={{ margin: '0 0 9px', paddingLeft: 20 }}>{b.items.map((it, j) => <li key={j} style={{ marginBottom: 3 }}><Inline hijos={it} /></li>)}</Tag>
        }
        if (b.tipo === 'cita') {
          return <blockquote key={i} style={{ margin: '0 0 9px', padding: '7px 12px', borderLeft: '3px solid var(--accent)', background: 'var(--bg3)', borderRadius: '0 8px 8px 0', color: 'var(--t2)' }}><Inline hijos={b.hijos} /></blockquote>
        }
        if (b.tipo === 'codigo') {
          return <pre key={i} className="sad-scroll" style={{ margin: '0 0 9px', padding: 10, borderRadius: 9, background: 'var(--bg3)', overflowX: 'auto', font: '500 11px var(--mono)' }}>{b.texto}</pre>
        }
        if (b.tipo === 'tabla') {
          return (
            <div key={i} className="sad-scroll" style={{ overflowX: 'auto', margin: '0 0 10px' }}>
              <table style={{ borderCollapse: 'collapse', width: '100%', font: '500 11.5px var(--sans)' }}>
                <thead><tr>{b.cabecera.map((c, j) => <th key={j} style={{ padding: '6px 9px', textAlign: 'left', borderBottom: '1px solid var(--line)', font: '700 10px var(--mono)', color: 'var(--t3)', whiteSpace: 'nowrap' }}>{c}</th>)}</tr></thead>
                <tbody>{b.filas.map((f, j) => <tr key={j}>{f.map((c, k) => <td key={k} style={{ padding: '6px 9px', borderBottom: '1px solid var(--line)', color: 'var(--t1)' }}><Inline hijos={[{ t: 'txt', v: c }]} /></td>)}</tr>)}</tbody>
              </table>
            </div>
          )
        }
        return <hr key={i} style={{ margin: '12px 0', border: 0, borderTop: '1px solid var(--line)' }} />
      })}
    </div>
  )
}

/** Un documento del parte. El HTML va en iframe aislado: el timeline que manda
 *  Cowork es una página entera y no tiene por qué compartir DOM con la app. */
function Documento({ d }: { d: DocumentoParte }) {
  const [abierto, setAbierto] = useState(d.id === 'ensayo')
  return (
    <section style={{ borderRadius: 12, background: 'var(--bg2)', border: '1px solid var(--line)', marginBottom: 10 }}>
      <button onClick={() => setAbierto(!abierto)} style={{ display: 'flex', alignItems: 'center', gap: 9, width: '100%', padding: '10px 14px', background: 'transparent', border: 0, cursor: 'pointer', textAlign: 'left' }}>
        <span style={{ font: '700 9.5px var(--mono)', color: 'var(--accent)', letterSpacing: '.5px', textTransform: 'uppercase' }}>{d.id}</span>
        <span style={{ font: '600 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>{d.titulo}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2.4" strokeLinecap="round" style={{ transform: abierto ? 'rotate(90deg)' : 'none', transition: 'transform .12s' }}><path d="M9 6l6 6-6 6" /></svg>
      </button>
      {abierto && (
        <div style={{ padding: '0 14px 14px' }}>
          {d.formato === 'html'
            ? <iframe title={d.titulo} srcDoc={d.cuerpo} sandbox="" style={{ width: '100%', height: 520, border: '1px solid var(--line)', borderRadius: 10, background: '#fff' }} />
            : d.formato === 'texto'
              ? <pre className="sad-scroll" style={{ margin: 0, whiteSpace: 'pre-wrap', font: '500 12px var(--mono)', color: 'var(--t1)' }}>{d.cuerpo}</pre>
              : <Markdown texto={d.cuerpo} />}
        </div>
      )}
    </section>
  )
}

// ── piezas del EFE ──────────────────────────────────────────────────────────

function Anillo({ eq }: { eq: EquipoParte }) {
  const cl = CLASIF[eq.clasificacion]
  const R = 52
  const C = 2 * Math.PI * R
  const frac = Math.max(0, Math.min(1, eq.porcentaje / 100))
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
      <svg width="132" height="132" viewBox="0 0 132 132">
        <circle cx="66" cy="66" r={R} fill="none" stroke="var(--bg3)" strokeWidth="11" />
        <circle cx="66" cy="66" r={R} fill="none" stroke={COLOR[cl.sem]} strokeWidth="11" strokeLinecap="round"
          strokeDasharray={`${(frac * C).toFixed(1)} ${C.toFixed(1)}`} transform="rotate(-90 66 66)" />
        <text x="66" y="62" textAnchor="middle" style={{ font: '800 26px var(--mono)', fill: 'var(--t1)' }}>{Math.round(eq.porcentaje)}%</text>
        <text x="66" y="80" textAnchor="middle" style={{ font: '600 9px var(--mono)', fill: 'var(--t3)' }}>{eq.total.toFixed(1)} / {eq.maximoAlcanzable}</text>
      </svg>
      <div style={{ font: '700 13px var(--sans)', color: 'var(--t1)', textAlign: 'center', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{eq.nombre}</div>
      <span style={{ padding: '3px 10px', borderRadius: 7, background: SUAVE[cl.sem], color: COLOR[cl.sem], font: '700 10px var(--mono)', letterSpacing: '.4px' }}>{cl.label}</span>
      {eq.dt.nombre && (
        <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', textAlign: 'center' }}>
          DT {eq.dt.nombre}{eq.dt.meses > 0 ? ` · ${Math.round(eq.dt.meses)} meses` : ''}
        </div>
      )}
    </div>
  )
}

function Bloques({ eq }: { eq: EquipoParte }) {
  return (
    <div>
      {(['A', 'B', 'C', 'D', 'E'] as const).map((letra) => {
        const b = eq.bloques[letra]
        const frac = b.excluido ? 0 : b.topePonderado ? b.ponderado / b.topePonderado : 0
        const sem: Semaforo = frac >= 0.7 ? 'verde' : frac >= 0.4 ? 'ambar' : 'rojo'
        return (
          <div key={letra} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 2px', borderBottom: '1px solid var(--line)' }}>
            <span style={{ width: 20, height: 20, borderRadius: 6, background: 'var(--bg3)', color: 'var(--t2)', font: '700 11px var(--mono)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{letra}</span>
            <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)', width: 118, flexShrink: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={b.nota || BLOQUE_NOMBRE[letra]}>{BLOQUE_NOMBRE[letra]}</span>
            {b.excluido ? (
              <span style={{ flex: 1, font: '600 10px var(--mono)', color: 'var(--t3)', minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={b.motivoExclusion}>N/A · {b.motivoExclusion || 'excluido'}</span>
            ) : (
              <span style={{ flex: 1, height: 7, borderRadius: 4, background: 'var(--bg3)', overflow: 'hidden' }}>
                <span style={{ display: 'block', width: `${frac * 100}%`, height: '100%', borderRadius: 4, background: COLOR[sem] }}></span>
              </span>
            )}
            <span style={{ font: '700 11.5px var(--mono)', color: 'var(--t1)', width: 62, textAlign: 'right', fontVariantNumeric: 'tabular-nums', flexShrink: 0 }}>
              {b.excluido ? '—' : `${b.ponderado.toFixed(1)}/${b.topePonderado}`}
            </span>
          </div>
        )
      })}
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 2px 2px', font: '700 12px var(--mono)', color: 'var(--t1)' }}>
        <span style={{ color: 'var(--t3)' }}>TOTAL</span>
        <span>{eq.total.toFixed(2)} / {eq.maximoAlcanzable} · {Math.round(eq.porcentaje)}%</span>
      </div>
    </div>
  )
}

function BarrasZona({ reduccion, nivel }: { reduccion: Record<ZonaF, number>; nivel: Record<ZonaF, Semaforo> }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
      {ZONAS.map((z) => (
        <div key={z} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 30, font: '700 10px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>{z}</span>
          <span style={{ flex: 1, height: 6, borderRadius: 3, background: 'var(--bg3)', overflow: 'hidden' }}>
            <span style={{ display: 'block', width: `${Math.min(100, reduccion[z])}%`, height: '100%', borderRadius: 3, background: COLOR[nivel[z]] }}></span>
          </span>
          <span style={{ width: 46, textAlign: 'right', font: '600 10px var(--mono)', color: COLOR[nivel[z]], fontVariantNumeric: 'tabular-nums', flexShrink: 0 }}>{reduccion[z].toFixed(0)}%</span>
        </div>
      ))}
    </div>
  )
}

function Rama({ letra, r, titulo }: { letra: string; r: RamaF; titulo: string }) {
  return (
    <div style={{ flex: 1, minWidth: 0, padding: '11px 13px', borderRadius: 11, background: 'var(--bg3)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
        <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--bg)', font: '700 9.5px var(--mono)', color: 'var(--t2)' }}>RAMA {letra}</span>
        <span style={{ font: '700 13px var(--mono)', color: COLOR[r.ipNivel] }}>IP {r.ip.toFixed(1)}</span>
        {r.multiplicadorGk && <span style={{ padding: '2px 7px', borderRadius: 6, background: SUAVE.rojo, color: COLOR.rojo, font: '700 9px var(--mono)' }}>🧤 ×1.5</span>}
      </div>
      <div style={{ font: '500 11px var(--sans)', color: 'var(--t2)', marginBottom: 8 }}>{titulo}</div>
      <BarrasZona reduccion={r.reduccion} nivel={r.reduccionNivel} />
    </div>
  )
}

function TablaPlantel({ jugadores }: { jugadores: JugadorParte[] }) {
  const [abierto, setAbierto] = useState(false)
  if (!jugadores.length) return null
  return (
    <div style={{ marginTop: 10 }}>
      <button onClick={() => setAbierto(!abierto)} style={{ display: 'flex', alignItems: 'center', gap: 7, padding: 0, background: 'transparent', border: 0, cursor: 'pointer', font: '600 11px var(--sans)', color: 'var(--t2)' }}>
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" style={{ transform: abierto ? 'rotate(90deg)' : 'none', transition: 'transform .12s' }}><path d="M9 6l6 6-6 6" /></svg>
        Tabla F1 · {jugadores.length} jugadores
      </button>
      {abierto && (
        <div className="sad-scroll" style={{ overflowX: 'auto', marginTop: 8 }}>
          <table style={{ borderCollapse: 'collapse', width: '100%', font: '500 11px var(--sans)' }}>
            <thead>
              <tr>{['Jugador', 'Zona', 'Rol', 'Apps', 'Estado'].map((h) => (
                <th key={h} style={{ padding: '5px 8px', textAlign: 'left', borderBottom: '1px solid var(--line)', font: '700 9.5px var(--mono)', color: 'var(--t3)', whiteSpace: 'nowrap' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {jugadores.map((j, i) => {
                const sem: Semaforo | null = j.estado === 'baja' ? 'rojo' : j.estado === 'duda' ? 'ambar' : j.estado === 'disponible' ? 'verde' : null
                return (
                  <tr key={i}>
                    <td style={{ padding: '5px 8px', borderBottom: '1px solid var(--line)', color: 'var(--t1)', whiteSpace: 'nowrap' }}>
                      {j.nombre}
                      {j.soloBaja && (
                        <span title="no venía en la tabla F1: entró por ser baja, para que pese en el IP"
                          style={{ marginLeft: 6, font: '600 9px var(--mono)', color: 'var(--t3)' }}>solo baja</span>
                      )}
                    </td>
                    <td style={{ padding: '5px 8px', borderBottom: '1px solid var(--line)', font: '700 10px var(--mono)', color: 'var(--t3)' }}>{j.zona}</td>
                    <td style={{ padding: '5px 8px', borderBottom: '1px solid var(--line)', color: 'var(--t2)', whiteSpace: 'nowrap' }}>{ROL_LABEL[j.rol] ?? j.rol}</td>
                    <td style={{ padding: '5px 8px', borderBottom: '1px solid var(--line)', font: '500 10px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>{j.apps || '—'}</td>
                    <td style={{ padding: '5px 8px', borderBottom: '1px solid var(--line)', whiteSpace: 'nowrap' }}>
                      {sem
                        ? <span style={{ padding: '1px 7px', borderRadius: 5, background: SUAVE[sem], color: COLOR[sem], font: '700 9.5px var(--mono)' }}>{j.hoja === 'banca' ? 'banca' : j.estado}</span>
                        : <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>— pendiente del once</span>}
                      {j.motivo ? <span style={{ font: '500 10px var(--sans)', color: 'var(--t3)', marginLeft: 6 }}>{j.motivo}</span> : null}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function PanelF({ eq }: { eq: EquipoParte }) {
  const d: DisponibilidadParte = eq.disponibilidad
  if (d.sinTabla) {
    return <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)' }}>{d.nota}</div>
  }
  return (
    <div>
      {d.conflicto && (
        <div style={{ padding: '9px 12px', marginBottom: 10, borderRadius: 10, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
          <div style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)' }}>{d.conflicto}</div>
          {!!d.noReconocidos?.length && (
            <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)', marginTop: 5, wordBreak: 'break-word' }}>sin casar: {d.noReconocidos.join(' · ')}</div>
          )}
        </div>
      )}
      {d.resuelto ? (
        <>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap', marginBottom: 10 }}>
            <span style={{ padding: '5px 11px', borderRadius: 8, background: SUAVE[d.ipNivel ?? 'verde'], color: COLOR[d.ipNivel ?? 'verde'], font: '700 12px var(--mono)' }}>IP {(d.ip ?? 0).toFixed(1)}</span>
            {d.multiplicadorGk && <span style={{ padding: '4px 9px', borderRadius: 7, background: SUAVE.rojo, color: COLOR.rojo, font: '700 10px var(--mono)' }}>🧤 GK ×1.5</span>}
            {d.formacion && <span style={{ font: '700 11px var(--mono)', color: 'var(--t2)' }}>{d.formacion}</span>}
            <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)', flex: 1, minWidth: 120 }}>once: {d.fuente}</span>
          </div>
          {d.reduccion && d.reduccionNivel && <BarrasZona reduccion={d.reduccion} nivel={d.reduccionNivel} />}
          {d.f4 && (
            <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', marginTop: 9 }}>
              F4 · {d.f4.rotados} rotados — {d.f4.diagnostico}
            </div>
          )}
          {!!d.fuera?.length && (
            <div style={{ marginTop: 9, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {d.fuera.map((f, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
                  <span style={{ width: 30, font: '700 9.5px var(--mono)', color: 'var(--t3)', flexShrink: 0 }}>{f.zona}</span>
                  <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.nombre}</span>
                  <span style={{ font: '500 10px var(--sans)', color: 'var(--t3)' }}>{f.motivo}</span>
                  <span style={{ font: '700 10.5px var(--mono)', color: 'var(--down)', flexShrink: 0 }}>+{f.impacto.toFixed(1)}</span>
                </div>
              ))}
            </div>
          )}
          {!!d.dudas?.length && (
            <div style={{ marginTop: 9, font: '500 10.5px var(--sans)', color: 'var(--mark)' }}>
              {d.dudas.map((x, i) => <div key={i}>⚠️ {x}</div>)}
            </div>
          )}
        </>
      ) : d.ramas ? (
        <>
          <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)', marginBottom: 9 }}>{d.nota}</div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <Rama letra="A" r={d.ramas.a} titulo={d.ramas.a.supuesto} />
            <Rama letra="B" r={d.ramas.b} titulo={d.ramas.b.supuesto} />
          </div>
        </>
      ) : null}
      <TablaPlantel jugadores={d.jugadores ?? eq.plantel} />
    </div>
  )
}

// ── caja del once ───────────────────────────────────────────────────────────

function CajaOnce({ parte, matchId, onParte }: { parte: ParteCoworkDTO; matchId: string; onParte: (p: ParteCoworkDTO) => void }) {
  const [lado, setLado] = useState<'a' | 'b'>(parte.equipos.a.disponibilidad.resuelto ? 'b' : 'a')
  const [texto, setTexto] = useState('')
  const [fuente, setFuente] = useState('pantallazo')
  const [cargando, setCargando] = useState<'' | 'ficha' | 'manual'>('')
  const [error, setError] = useState<string | null>(null)
  const previo = useMemo(() => parsearOnce(texto), [texto])

  const mandar = async (desdeFicha: boolean) => {
    setCargando(desdeFicha ? 'ficha' : 'manual')
    setError(null)
    try {
      const cuerpo = desdeFicha
        ? { desdeFicha: true }
        : { [lado]: { once: previo.once, banca: previo.banca, fuente } }
      onParte(await resolverXiParte(matchId, cuerpo))
      if (!desdeFicha) setTexto('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'no se pudo cargar el once')
    } finally {
      setCargando('')
    }
  }

  return (
    <section style={{ marginBottom: 14, padding: '12px 14px', borderRadius: 12, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap', marginBottom: 9 }}>
        <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)' }}>Cargar el once</span>
        <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', flex: 1, minWidth: 180 }}>
          cierra el bloque F en el servidor con las fórmulas del protocolo · cero créditos
        </span>
        <button onClick={() => mandar(true)} disabled={!!cargando}
          title="Usa las alineaciones que ya capturó la ingesta de API-Football"
          style={{ padding: '6px 12px', borderRadius: 8, border: '1px solid var(--line)', cursor: cargando ? 'wait' : 'pointer', background: 'var(--bg3)', color: 'var(--t1)', font: '600 11px var(--sans)' }}>
          {cargando === 'ficha' ? 'Buscando…' : 'Traer de la ficha'}
        </button>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', padding: 3, borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--line)' }}>
          {(['a', 'b'] as const).map((l) => (
            <button key={l} onClick={() => setLado(l)}
              style={{ padding: '5px 11px', border: 0, borderRadius: 7, cursor: 'pointer', background: lado === l ? 'var(--bg3)' : 'transparent', color: lado === l ? 'var(--t1)' : 'var(--t2)', font: '600 11px var(--sans)' }}>
              {l === 'a' ? parte.partido.equipoA : parte.partido.equipoB}
              {parte.equipos[l].disponibilidad.resuelto ? ' ✓' : ''}
            </button>
          ))}
        </div>
        <input value={fuente} onChange={(e) => setFuente(e.target.value)} placeholder="fuente (BeSoccer, cuenta oficial…)"
          style={{ flex: 1, minWidth: 160, padding: '7px 10px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '500 11px var(--sans)' }} />
      </div>
      <textarea value={texto} onChange={(e) => setTexto(e.target.value)} spellCheck={false}
        placeholder={'Pega el once tal cual (uno por línea o separados por coma).\nUna línea "Suplentes:" abre la banca.'}
        style={{ width: '100%', minHeight: 96, padding: 10, borderRadius: 9, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t1)', font: '500 11px var(--mono)', resize: 'vertical', boxSizing: 'border-box' }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 8, flexWrap: 'wrap' }}>
        <button onClick={() => mandar(false)} disabled={!!cargando || previo.once.length === 0}
          style={{ padding: '8px 16px', borderRadius: 9, border: 0, cursor: cargando || !previo.once.length ? 'default' : 'pointer', background: cargando || !previo.once.length ? 'var(--bg3)' : 'var(--accent)', color: cargando || !previo.once.length ? 'var(--t3)' : '#fff', font: '700 12px var(--sans)' }}>
          {cargando === 'manual' ? 'Cerrando bloque F…' : 'Cerrar el bloque F'}
        </button>
        {texto.trim() && (
          <span style={{ font: '500 10.5px var(--mono)', color: previo.once.length === 11 ? 'var(--up)' : 'var(--mark)' }}>
            {previo.once.length} titulares{previo.banca.length ? ` · ${previo.banca.length} en banca` : ''}
            {previo.once.length !== 11 ? ' (se esperan 11)' : ''}
          </span>
        )}
        {error && <span style={{ font: '600 11px var(--sans)', color: 'var(--down)', flex: 1, minWidth: 200 }}>{error}</span>}
      </div>
    </section>
  )
}

function Indice({ etiqueta, valor, nivel, nota }: { etiqueta: string; valor: number; nivel?: Semaforo | ''; nota: string }) {
  // sin nivel del skill se pinta en neutro: el backend no inventa umbrales
  const col = nivel ? COLOR[nivel] : 'var(--t1)'
  const fondo = nivel ? SUAVE[nivel] : 'var(--bg3)'
  return (
    <div style={{ flex: 1, minWidth: 120, padding: '11px 13px', borderRadius: 11, background: fondo, textAlign: 'center' }}>
      <div style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px' }}>{etiqueta}</div>
      <div style={{ font: '800 22px var(--mono)', color: col, fontVariantNumeric: 'tabular-nums' }}>{valor}</div>
      <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)' }}>{nota}</div>
    </div>
  )
}

/** Teorema del Echado: los dos índices opuestos con su ventana y su causa. */
function PanelTde({ tde, nombreDe }: { tde: TdeParte; nombreDe: (l: 'a' | 'b') => string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <section style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap', marginBottom: 11 }}>
          <span style={{ font: '700 10px var(--mono)', color: 'var(--accent)', letterSpacing: '.6px', textTransform: 'uppercase' }}>Teorema del Echado</span>
          {tde.equipo && <span style={{ font: '600 11.5px var(--sans)', color: 'var(--t1)' }}>{nombreDe(tde.equipo as 'a' | 'b')}</span>}
          {tde.disciplina43 && (
            <span style={{ padding: '3px 9px', borderRadius: 7, background: 'var(--mark-soft)', color: 'var(--mark)', font: '700 9.5px var(--mono)' }}>
              DISCIPLINA 43 · dos vías declaradas
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 11 }}>
          <Indice etiqueta="IE · ECHADA" valor={tde.ie ?? 0} nivel={tde.ieNivel} nota="repliegue sin control" />
          <Indice etiqueta="ISE · SOBREEXPOSICIÓN" valor={tde.ise ?? 0} nivel={tde.iseNivel} nota="no replegar a tiempo" />
          {tde.ventana && (
            <div style={{ flex: 1, minWidth: 120, padding: '11px 13px', borderRadius: 11, background: 'var(--accent-soft)', textAlign: 'center' }}>
              <div style={{ font: '700 9.5px var(--mono)', color: 'var(--accent)', letterSpacing: '.5px' }}>VENTANA</div>
              <div style={{ font: '800 22px var(--mono)', color: 'var(--accent)' }}>{tde.ventana}</div>
              <div style={{ font: '500 10px var(--sans)', color: 'var(--t3)' }}>tramo de riesgo</div>
            </div>
          )}
        </div>
        {tde.tipologia && (
          <div style={{ display: 'flex', gap: 10, padding: '5px 0', borderBottom: '1px solid var(--line)' }}>
            <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 96, flexShrink: 0, textTransform: 'uppercase', letterSpacing: '.3px' }}>Causa modal</span>
            <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{tde.tipologia}</span>
          </div>
        )}
        {(tde.vias ?? []).map((v, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '7px 0', borderBottom: '1px solid var(--line)' }}>
            <span style={{ font: '700 10px var(--mono)', color: 'var(--t2)', width: 96, flexShrink: 0 }}>{v.nombre}</span>
            <span style={{ font: '700 11px var(--mono)', color: 'var(--t1)', width: 42, flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>{v.indice}</span>
            <span style={{ font: '600 10.5px var(--mono)', color: 'var(--t3)', width: 70, flexShrink: 0 }}>{v.ventana}</span>
            <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0 }}>{v.detalle}</span>
          </div>
        ))}
        {tde.falsador && (
          <div style={{ marginTop: 10, padding: '9px 12px', borderRadius: 10, background: 'var(--bg3)' }}>
            <span style={{ font: '700 9.5px var(--mono)', color: 'var(--mark)', letterSpacing: '.5px' }}>FALSADOR · </span>
            <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{tde.falsador}</span>
          </div>
        )}
      </section>
    </div>
  )
}

/** El cierre del caso: qué pasó de verdad (fase B de docs/APRENDIZAJE.md).
 *
 *  Todo lo que se pinta aquí en números lo calculó el backend contra la
 *  ingesta; lo que está en prosa lo escribió Cowork. La distinción importa
 *  porque es lo que hace auditable el pronóstico: nadie puede ajustar el
 *  marcador a la explicación después. */
function BandaVeredicto({ v, nombreDe }: { v: VeredictoParte; nombreDe: (l: 'a' | 'b') => string }) {
  const [abierto, setAbierto] = useState(false)
  const o = v.objetivo
  const m = o.marcador
  const ok = (x: boolean | null | undefined) => (x === null || x === undefined ? 'var(--t3)' : x ? 'var(--up)' : 'var(--down)')
  const marca = (x: boolean | null | undefined) => (x === null || x === undefined ? '—' : x ? '✓' : '✗')
  const VER = {
    acierto: { color: 'var(--up)', soft: 'var(--up-soft)', label: 'ACIERTO' },
    parcial: { color: 'var(--mark)', soft: 'var(--mark-soft)', label: 'PARCIAL' },
    fallo: { color: 'var(--down)', soft: 'var(--down-soft)', label: 'FALLO' },
  } as const

  if (!o.jugado) {
    return (
      <section style={{ padding: '11px 15px', marginBottom: 12, borderRadius: 12, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
        <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)' }}>
          Caso cerrado, pero el marcador todavía no está en nuestra base: {o.motivo}
        </span>
      </section>
    )
  }

  return (
    <section style={{ marginBottom: 12, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 15px', flexWrap: 'wrap' }}>
        <span style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>VEREDICTO</span>
        <span style={{ font: '800 20px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{m?.texto}</span>
        {m && !m.terminado && (
          <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--mark-soft)', color: 'var(--mark)', font: '700 9px var(--mono)' }}>EN CURSO</span>
        )}
        <span style={{ font: '600 11.5px var(--mono)', color: ok(o.unXDos?.acerto) }}>
          {marca(o.unXDos?.acerto)} 1X2
        </span>
        <span style={{ font: '600 11.5px var(--mono)', color: ok(o.marcadorExacto?.acerto) }}>
          {marca(o.marcadorExacto?.acerto)} marcador
        </span>
        {o.tde && (
          <span style={{ font: '600 11.5px var(--mono)', color: ok(o.tde.golEnVentana) }}
            title={o.tde.nota || `ventana ${o.tde.ventana}`}>
            {marca(o.tde.golEnVentana)} ventana TDE
          </span>
        )}
        {o.brier?.valor !== null && o.brier?.valor !== undefined && (
          <span style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)' }} title={o.brier.escala}>
            Brier {o.brier.valor.toFixed(3)}
          </span>
        )}
        <span style={{ flex: 1 }}></span>
        {/* la población del caso: lo que decide si esto cuenta o solo ilustra */}
        <span
          title={v.acredita
            ? 'caso ciego y puntuado antes: acredita validación predictiva'
            : 'el caso fija rúbrica pero NO acredita (docs/APRENDIZAJE.md)'}
          style={{ padding: '3px 9px', borderRadius: 7, font: '700 9.5px var(--mono)', letterSpacing: '.3px', background: v.acredita ? 'var(--up-soft)' : 'var(--bg3)', color: v.acredita ? 'var(--up)' : 'var(--t3)' }}>
          {v.seleccion.toUpperCase().replace('_', ' ')} · {v.modoEvaluacion} · {v.acredita ? 'ACREDITA' : 'NO ACREDITA'}
        </span>
        <button onClick={() => setAbierto(!abierto)} style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '4px 9px', borderRadius: 8, border: '1px solid var(--line)', background: 'var(--bg)', color: 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
          {abierto ? 'Menos' : 'Detalle'}
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" style={{ transform: abierto ? 'rotate(90deg)' : 'none', transition: 'transform .12s' }}><path d="M9 6l6 6-6 6" /></svg>
        </button>
      </div>

      {abierto && (
        <div style={{ padding: '0 15px 14px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(['a', 'b'] as const).map((lado) => {
            const l = v.porLado[lado]
            if (!l) return null
            const est = VER[l.veredicto]
            return (
              <div key={lado} style={{ padding: '10px 12px', borderRadius: 11, background: est.soft }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap', marginBottom: l.queP || l.leccion ? 6 : 0 }}>
                  <span style={{ font: '700 9.5px var(--mono)', color: est.color, letterSpacing: '.4px' }}>{est.label}</span>
                  <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)' }}>{nombreDe(lado)}</span>
                  {l.skill && (
                    <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--bg)', font: '600 9.5px var(--mono)', color: 'var(--t2)' }}>{l.skill}</span>
                  )}
                </div>
                {l.queP && <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{l.queP}</div>}
                {l.leccion && (
                  <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t2)', marginTop: 4 }}>
                    <b style={{ color: 'var(--t3)', font: '700 9.5px var(--mono)' }}>LECCIÓN · </b>{l.leccion}
                  </div>
                )}
              </div>
            )
          })}

          {v.falsador.texto && (
            <div style={{ padding: '9px 12px', borderRadius: 10, background: 'var(--bg3)' }}>
              <span style={{ font: '700 9.5px var(--mono)', color: ok(v.falsador.cumplido), letterSpacing: '.4px' }}>
                FALSADOR {marca(v.falsador.cumplido)} ·{' '}
              </span>
              <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{v.falsador.texto}</span>
            </div>
          )}

          {/* la evidencia con la que se comprueba todo lo de arriba */}
          {!!o.evidencia?.goles?.length && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px' }}>GOLES</span>
              {o.evidencia.goles.map((g, i) => (
                <span key={i} style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--bg3)', font: '600 10px var(--mono)', color: 'var(--t2)' }}>
                  {g.minuto}&apos; {nombreDe(g.lado)}{g.jugador ? ` · ${g.jugador}` : ''}{g.autogol ? ' (ag)' : ''}
                </span>
              ))}
            </div>
          )}
          {o.evidencia?.nota && (
            <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>{o.evidencia.nota}</div>
          )}
          {!!v.sinPronosticoPrevio?.length && (
            <div style={{ font: '500 10.5px var(--sans)', color: 'var(--mark)' }}>
              Sin pronóstico previo declarado, la cadena no recibe veredicto: {v.sinPronosticoPrevio.join(' · ')}
            </div>
          )}
          <div style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>
            {o.brier?.escala} · cerrado {v.cerradoEn}
          </div>
        </div>
      )}
    </section>
  )
}

// ── la sección entera ───────────────────────────────────────────────────────

interface Props {
  parte: ParteCoworkDTO
  matchId: string
  /** claves internas de los equipos: el calendario del bloque G se pide por ahí */
  equipoAKey: string
  equipoBKey: string
  onParte: (p: ParteCoworkDTO) => void
  isMobile: boolean
}

type Tab = 'bloques' | 'f' | 'matchup' | 'lectura' | 'tde' | 'calendario' | 'timeline' | 'documentos'

export function ParteCowork({ parte, matchId, equipoAKey, equipoBKey, onParte, isMobile }: Props) {
  const [tab, setTab] = useState<Tab>('bloques')

  // el calendario (bloque G) se pide SOLO al abrir su pestaña: ya está
  // calculado y es gratis, pero son dos requests que nadie pidió si el
  // usuario no entra ahí
  const [cal, setCal] = useState<Record<string, PartidoCalendarioUI[]>>({})
  useEffect(() => {
    if (tab !== 'calendario') return
    for (const k of [equipoAKey, equipoBKey]) {
      if (cal[k]) continue
      loadCalendarioSad(k).then((ps) => setCal((prev) => ({ ...prev, [k]: ps }))).catch(() => { /* el calendario es una ayuda */ })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, equipoAKey, equipoBKey])
  const dosCol = isMobile ? '1fr' : '1fr 1fr'
  const pendienteXi = parte.estado !== 'confirmado'
  // qué lado sigue congelado: el once del local suele llegar antes que el del
  // visitante, y un aviso que dice "los dos" cuando ya hay uno cerrado se lee
  // como que no sirvió de nada cargarlo
  const faltan = (['a', 'b'] as const).filter((l) => !parte.equipos[l].disponibilidad.resuelto)
  const nombreDe = (l: 'a' | 'b') => (l === 'a' ? parte.partido.equipoA : parte.partido.equipoB)
  const p = parte.pronostico
  const ls = parte.lecturaSad
  const conTde = !!(parte.tde && (parte.tde.tipologia || parte.tde.ie || parte.tde.ise || parte.tde.vias?.length))
  const tabs: { k: Tab; label: string }[] = [
    { k: 'bloques', label: 'Bloques EFE' },
    { k: 'f', label: pendienteXi ? 'Bloque F · congelado' : 'Bloque F' },
    { k: 'matchup', label: 'Matchup' },
    { k: 'lectura', label: 'Lectura SAD' },
    ...(conTde ? [{ k: 'tde' as Tab, label: 'Teorema del Echado' }] : []),
    { k: 'calendario', label: 'Calendario' },
    ...(parte.timeline ? [{ k: 'timeline' as Tab, label: 'Timeline' }] : []),
    { k: 'documentos', label: `Documentos (${parte.documentos.length})` },
  ]

  return (
    <div>
      {parte.veredicto && <BandaVeredicto v={parte.veredicto} nombreDe={nombreDe} />}

      {/* la marca visible: que nadie lea esto creyendo que el once está cerrado */}
      {pendienteXi && !parte.veredicto && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 15px', marginBottom: 12, borderRadius: 12, background: 'var(--mark-soft)', border: '1px solid color-mix(in oklch,var(--mark),transparent 50%)' }}>
          <span style={{ font: '800 12px var(--mono)', color: 'var(--mark)', letterSpacing: '.4px', flexShrink: 0 }}>
            {faltan.length === 2 ? '⚠️ XI NO CONFIRMADO' : '⚠️ FALTA UN XI'}
          </span>
          <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>
            {faltan.length === 2
              ? 'Bloque F congelado en los dos: el impacto va en dos ramas hasta que llegue el once. Todo lo demás ya está cerrado.'
              : `Bloque F cerrado en ${nombreDe(faltan[0] === 'a' ? 'b' : 'a')}; falta el once de ${nombreDe(faltan[0])}, que sigue en dos ramas.`}
          </span>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12, flexWrap: 'wrap' }}>
        <span style={{ padding: '5px 11px', borderRadius: 8, font: '700 10px var(--mono)', letterSpacing: '.4px', background: pendienteXi ? 'var(--bg3)' : 'var(--up-soft)', color: pendienteXi ? 'var(--t2)' : 'var(--up)' }}>
          {pendienteXi ? 'PENDIENTE DE ONCE' : 'XI CONFIRMADO'}
        </span>
        <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>
          parte {parte.version} · depositado {new Date(parte.creadoEn.replace(' ', 'T') + (parte.creadoEn.endsWith('Z') ? '' : 'Z')).toLocaleString()}
        </span>
      </div>

      <CajaOnce parte={parte} matchId={matchId} onParte={onParte} />

      <section style={{ display: 'flex', gap: 12, padding: '20px 16px', marginBottom: 14, borderRadius: 16, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
        <Anillo eq={parte.equipos.a} />
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 6, flexShrink: 0 }}>
          <span style={{ font: '800 13px var(--mono)', color: 'var(--t3)' }}>VS</span>
          {parte.partido.fecha && <span style={{ font: '500 9.5px var(--mono)', color: 'var(--t3)' }}>{parte.partido.fecha}</span>}
        </div>
        <Anillo eq={parte.equipos.b} />
      </section>

      {parte.alertas.length > 0 && (
        <section style={{ display: 'flex', flexDirection: 'column', gap: 7, marginBottom: 14 }}>
          {parte.alertas.map((a, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '9px 13px', borderRadius: 11, background: a.tipo === 'estructural' ? 'var(--down-soft)' : 'var(--mark-soft)', border: `1px solid color-mix(in oklch,${a.tipo === 'estructural' ? 'var(--down)' : 'var(--mark)'},transparent 60%)` }}>
              <span style={{ padding: '2px 8px', borderRadius: 6, background: 'var(--bg)', font: '700 9.5px var(--mono)', color: a.tipo === 'estructural' ? 'var(--down)' : 'var(--mark)', flexShrink: 0, whiteSpace: 'nowrap' }}>{a.codigo}</span>
              <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
                {a.equipo !== 'global' && (
                  <b style={{ color: 'var(--t2)' }}>
                    [{a.equipo === 'a' ? parte.partido.equipoA
                      : a.equipo === 'b' ? parte.partido.equipoB : 'Ambos'}]{' '}
                  </b>
                )}
                {a.detalle}
              </span>
            </div>
          ))}
        </section>
      )}

      <div className="sad-scroll" style={{ display: 'flex', gap: 6, marginBottom: 14, overflowX: 'auto', paddingBottom: 2 }}>
        {tabs.map((t) => (
          <button key={t.k} onClick={() => setTab(t.k)} style={{ flexShrink: 0, padding: '8px 15px', border: `1px solid ${tab === t.k ? 'color-mix(in oklch,var(--accent),transparent 55%)' : 'var(--line)'}`, borderRadius: 9, cursor: 'pointer', background: tab === t.k ? 'var(--accent-soft)' : 'var(--bg)', color: tab === t.k ? 'var(--accent)' : 'var(--t2)', font: '600 12px var(--sans)', whiteSpace: 'nowrap' }}>{t.label}</button>
        ))}
      </div>

      {tab === 'bloques' && (
        <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
          {(['a', 'b'] as const).map((lado) => (
            <section key={lado} style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ font: '700 12.5px var(--sans)', marginBottom: 6 }}>{parte.equipos[lado].nombre}</div>
              <Bloques eq={parte.equipos[lado]} />
            </section>
          ))}
        </div>
      )}

      {tab === 'f' && (
        <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
          {(['a', 'b'] as const).map((lado) => (
            <section key={lado} style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
              <div style={{ font: '700 12.5px var(--sans)', marginBottom: 10 }}>{parte.equipos[lado].nombre}</div>
              <PanelF eq={parte.equipos[lado]} />
            </section>
          ))}
        </div>
      )}

      {tab === 'matchup' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <section style={{ padding: '13px 16px', borderRadius: 14, textAlign: 'center', background: parte.matchup.diagnostico === 'FAVORABLE' ? 'var(--up-soft)' : parte.matchup.diagnostico === 'DESFAVORABLE' ? 'var(--down-soft)' : 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '800 14px var(--mono)', letterSpacing: '.5px', color: parte.matchup.diagnostico === 'FAVORABLE' ? 'var(--up)' : parte.matchup.diagnostico === 'DESFAVORABLE' ? 'var(--down)' : 'var(--t1)' }}>
              MATCHUP {parte.matchup.diagnostico}
              {parte.matchup.favorece && ` · ${nombreDe(parte.matchup.favorece as 'a' | 'b')}`}
            </div>
            <div style={{ font: '500 12px var(--sans)', color: 'var(--t1)', marginTop: 5 }}>{parte.matchup.razon}</div>
            {/* los tres indicadores que SOSTIENEN el diagnóstico: sin ellos la
                etiqueta de arriba no se puede discutir */}
            <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 9, flexWrap: 'wrap' }}>
              {([['h2a', 'explota la vulnerabilidad'], ['h2b', 'asimetría por zonas'], ['h2c', 'vida útil del planteo']] as const).map(([k, ayuda]) => {
                const v = parte.matchup[k]
                if (!v || v === 'na') return null
                return (
                  <span key={k} title={ayuda} style={{ padding: '3px 9px', borderRadius: 6, background: 'var(--bg)', font: '700 10px var(--mono)', color: COLOR[v as Semaforo] }}>
                    {k.toUpperCase()} · {v}
                  </span>
                )
              })}
            </div>
          </section>

          <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
            {(['a', 'b'] as const).map((lado) => {
              const perfil = parte.equipos[lado].perfil
              return (
                <section key={lado} style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                  <div style={{ font: '700 12.5px var(--sans)', marginBottom: 9 }}>{parte.equipos[lado].nombre}</div>
                  {([['Sistema', perfil.sistema], ['Estilo', perfil.estilo], ['Fortaleza', perfil.fortaleza], ['Vulnerabilidad', perfil.vulnerabilidad]] as const).map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', gap: 10, padding: '5px 0', borderBottom: '1px solid var(--line)' }}>
                      <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 96, flexShrink: 0, textTransform: 'uppercase', letterSpacing: '.3px' }}>{k}</span>
                      <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{v || '—'}</span>
                    </div>
                  ))}
                  {parte.equipos[lado].factorX.length > 0 && (
                    <div style={{ marginTop: 10 }}>
                      <div style={{ font: '700 9.5px var(--mono)', color: 'var(--mark)', letterSpacing: '.5px', marginBottom: 5 }}>FACTOR-X</div>
                      {parte.equipos[lado].factorX.map((f, i) => (
                        <div key={i} style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', marginBottom: 3 }}>
                          <b style={{ color: 'var(--t2)' }}>{f.nombre}</b> — {f.contexto}
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              )
            })}
          </div>
        </div>
      )}

      {tab === 'lectura' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* LA LECTURA SAD: el juicio que cierra el EFE. No se puede calcular
              y por eso tiene sitio propio en vez de diluirse en el ensayo. */}
          <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
            {([
              ['Módulo operativo', ls.moduloOperativo],
              ['1X2', ls.unXDos.texto + (ls.unXDos.rangoAmpliado ? ' · rango ampliado ±10% (FACTOR-X)' : '')],
              ['Contexto emocional', ls.contextoEmocional],
              ['Dato estructural', ls.datoEstructural],
            ] as const).map(([titulo, texto]) => (
              <section key={titulo} style={{ padding: '13px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
                <div style={{ font: '700 10px var(--mono)', color: 'var(--accent)', letterSpacing: '.6px', textTransform: 'uppercase', marginBottom: 6 }}>{titulo}</div>
                <div style={{ font: '500 12.5px var(--sans)', color: texto.trim() ? 'var(--t1)' : 'var(--t3)', lineHeight: 1.5 }}>
                  {texto.trim() || 'sin dato — el parte llegó sin esta lectura'}
                </div>
              </section>
            ))}
          </div>
          {ls.paradoja && (
            <section style={{ padding: '13px 16px', borderRadius: 14, background: 'var(--mark-soft)', border: '1px solid color-mix(in oklch,var(--mark),transparent 55%)' }}>
              <div style={{ font: '700 10px var(--mono)', color: 'var(--mark)', letterSpacing: '.6px', marginBottom: 6 }}>⚖️ PARADOJA DEL PARTIDO</div>
              <div style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', lineHeight: 1.5 }}>{ls.paradoja}</div>
            </section>
          )}

          <section style={{ padding: '14px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
            <div style={{ font: '700 10px var(--mono)', color: 'var(--accent)', letterSpacing: '.6px', textTransform: 'uppercase', marginBottom: 9 }}>Pronóstico · tres fuentes declaradas</div>
            <div style={{ display: 'flex', gap: 10, marginBottom: 11, flexWrap: 'wrap' }}>
              {([['Local', p.probabilidades.local], ['Empate', p.probabilidades.empate], ['Visita', p.probabilidades.visita]] as const).map(([k, v]) => (
                <div key={k} style={{ flex: 1, minWidth: 88, padding: '9px 11px', borderRadius: 10, background: 'var(--bg3)', textAlign: 'center' }}>
                  <div style={{ font: '700 9.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.4px' }}>{k.toUpperCase()}</div>
                  <div style={{ font: '800 18px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{v}%</div>
                </div>
              ))}
              {p.marcador && (
                <div style={{ flex: 1, minWidth: 88, padding: '9px 11px', borderRadius: 10, background: 'var(--accent-soft)', textAlign: 'center' }}>
                  <div style={{ font: '700 9.5px var(--mono)', color: 'var(--accent)', letterSpacing: '.4px' }}>MARCADOR</div>
                  <div style={{ font: '800 18px var(--mono)', color: 'var(--accent)' }}>{p.marcador}</div>
                </div>
              )}
            </div>
            {([['Motor de regresión', p.motor], ['Matriz manual', p.matriz], ['Mercado', p.mercado]] as const).map(([k, v]) => (
              <div key={k} style={{ display: 'flex', gap: 10, padding: '5px 0', borderBottom: '1px solid var(--line)' }}>
                <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)', width: 128, flexShrink: 0, textTransform: 'uppercase', letterSpacing: '.3px' }}>{k}</span>
                <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{v || '— no se pudo correr (y no se reemplaza por estimación)'}</span>
              </div>
            ))}
            {p.falsador && (
              <div style={{ marginTop: 10, padding: '9px 12px', borderRadius: 10, background: 'var(--bg3)' }}>
                <span style={{ font: '700 9.5px var(--mono)', color: 'var(--mark)', letterSpacing: '.5px' }}>FALSADOR · </span>
                <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>{p.falsador}</span>
              </div>
            )}
          </section>

          {/* CAJA DE SENSIBILIDAD: el hueco declarado, con cuánto movería */}
          {(['a', 'b'] as const).some((l) => parte.equipos[l].sensibilidad?.length > 0) && (
            <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
              {(['a', 'b'] as const).map((lado) => (
                <section key={lado} style={{ padding: '13px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px dashed var(--line)' }}>
                  <div style={{ font: '700 10px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px', marginBottom: 7 }}>
                    CAJA DE SENSIBILIDAD · {parte.equipos[lado].nombre}
                  </div>
                  {(parte.equipos[lado].sensibilidad ?? []).length === 0
                    ? <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)' }}>sin huecos declarados</div>
                    : (parte.equipos[lado].sensibilidad ?? []).map((x, i) => (
                      <div key={i} style={{ display: 'flex', gap: 10, padding: '5px 0', borderBottom: '1px solid var(--line)' }}>
                        <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t2)', flex: 1, minWidth: 0 }}>si {x.supuesto}</span>
                        <span style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0 }}>→ {x.efecto}</span>
                      </div>
                    ))}
                </section>
              ))}
            </div>
          )}

          {parte.pendientes.length > 0 && (
            <section style={{ padding: '13px 16px', borderRadius: 14, background: 'var(--bg2)', border: '1px dashed var(--line)' }}>
              <div style={{ font: '700 10px var(--mono)', color: 'var(--mark)', letterSpacing: '.6px', marginBottom: 7 }}>QUÉ FALTA CERRAR</div>
              <ul style={{ margin: 0, paddingLeft: 18, font: '500 12px var(--sans)', color: 'var(--t1)' }}>
                {parte.pendientes.map((x, i) => <li key={i} style={{ marginBottom: 3 }}>{x}</li>)}
              </ul>
            </section>
          )}

          {parte.fuentes.length > 0 && (
            <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', wordBreak: 'break-word' }}>Fuentes: {parte.fuentes.join(' · ')}</div>
          )}
        </div>
      )}

      {tab === 'tde' && <PanelTde tde={parte.tde} nombreDe={nombreDe} />}

      {/* BLOQUE G: el calendario NO viene en el parte — se calcula de nuestra
          base y se pinta con la misma pieza que el resto de la app */}
      {tab === 'calendario' && (
        <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
          {([[equipoAKey, parte.partido.equipoA], [equipoBKey, parte.partido.equipoB]] as const).map(([key, nombre]) => (
            <CalendarioSad key={key} titulo={nombre} partidos={cal[key] ?? []} loading={!cal[key]} />
          ))}
        </div>
      )}

      {tab === 'timeline' && parte.timeline && (
        <>
          <div style={{ font: '500 10.5px var(--mono)', color: 'var(--t3)', marginBottom: 10 }}>
            Lo institucional lo escribió Cowork; los partidos, la jornada y el marcador los calcula el backend de nuestra base.
          </div>
          <TimelineComparativo data={parte.timeline} isMobile={isMobile} />
        </>
      )}

      {tab === 'documentos' && (
        <div>
          {parte.documentos.length === 0
            ? <div style={{ padding: '22px 18px', borderRadius: 14, background: 'var(--bg2)', border: '1px dashed var(--line)', textAlign: 'center', font: '500 12px var(--sans)', color: 'var(--t3)' }}>El parte llegó sin documentos en prosa.</div>
            : parte.documentos.map((d) => <Documento key={d.id} d={d} />)}
        </div>
      )}
    </div>
  )
}
