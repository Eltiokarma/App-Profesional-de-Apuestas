import { useState } from 'react'
import type { InventarioLecciones, LeccionItem, SkillAprendizaje } from '../api/types'
import { getDataSource } from '../services/datasource'
import { useAsync } from '../services/useAsync'

/** Fase C del bucle de aprendizaje (docs/APRENDIZAJE.md).
 *
 *  Lo que esta pantalla NO hace, y es la mitad del diseño: no promedia
 *  poblaciones, no publica una tasa sin su `n`, no muestra un Brier sin su
 *  línea de base, y no deja que una lección de un caso contaminado parezca que
 *  puede mover un peso. La app tampoco mueve nada sola: abrir la revisión es
 *  abrirla, no autorizarla. */

const COLOR_VER: Record<string, string> = {
  acierto: 'var(--up)', parcial: 'var(--mark)', fallo: 'var(--down)',
}
const SUAVE_VER: Record<string, string> = {
  acierto: 'var(--up-soft)', parcial: 'var(--mark-soft)', fallo: 'var(--down-soft)',
}
const ETIQUETA_ESTADO: Record<string, string> = {
  pendiente: 'PENDIENTE', en_revision: 'EN REVISIÓN', aplicada: 'APLICADA', descartada: 'DESCARTADA',
}

export function Aprendizaje({ isMobile }: { isMobile: boolean }) {
  const [estado, setEstado] = useState('')
  const [recarga, setRecarga] = useState(0)
  const inv = useAsync<InventarioLecciones>(
    () => getDataSource().lecciones(estado ? { estado } : undefined), `${estado}|${recarga}`)

  if (inv.loading && !inv.data) {
    return <Marco><span style={{ font: '500 12px var(--sans)', color: 'var(--t3)' }}>Cargando lo aprendido…</span></Marco>
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
  const a = d.acreditables
  const vacio = d.items.length === 0 && d.porSkill.length === 0

  return (
    <div style={{ padding: isMobile ? '16px 14px 40px' : '22px 26px 48px', maxWidth: 1080 }}>
      <h1 style={{ font: '800 26px var(--sans)', color: 'var(--t1)', margin: '0 0 4px' }}>Aprendizaje</h1>
      <div style={{ font: '500 12px var(--sans)', color: 'var(--t3)', marginBottom: 18 }}>
        Lo que el bucle aprendió, por skill · las lecciones salen de los veredictos y se
        recalculan al leer
      </div>

      {/* LA POBLACIÓN VA ANTES QUE CUALQUIER NÚMERO. Un porcentaje que mezcla
          casos ciegos con casos sembrados no es una métrica pesimista ni
          optimista: es otra cosa con el mismo nombre. */}
      <Seccion titulo="LA POBLACIÓN MANDA" >
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 8 }}>
          {(['ciega', 'por_resultado', 'post_resultado'] as const).map((k) => {
            const p = d.poblacion[k]
            const n = typeof p === 'object' ? p : { casos: 0, lados: 0 }
            const ciega = k === 'ciega'
            return (
              <div key={k} style={{ flex: 1, minWidth: 140, padding: '11px 13px', borderRadius: 11, background: ciega ? 'var(--up-soft)' : 'var(--bg3)' }}>
                <div style={{ font: '700 9.5px var(--mono)', color: ciega ? 'var(--up)' : 'var(--t3)', letterSpacing: '.4px' }}>
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
              <div key={nivel} style={{ display: 'flex', alignItems: 'center', gap: 10, font: '500 11px var(--mono)', color: 'var(--t2)', fontVariantNumeric: 'tabular-nums' }}>
                <span style={{ width: 70, color: 'var(--t1)', fontWeight: 700 }}>{nivel}</span>
                <span>{c.reventadas}/{c.observadas}{c.tasa !== null ? ` · ${Math.round(c.tasa * 100)}%` : ''}</span>
                <span style={{ color: 'var(--t3)' }}>
                  {c.esperadoBacktest ? `backtest ${Math.round(c.esperadoBacktest[0] * 100)}–${Math.round(c.esperadoBacktest[1] * 100)}%` : 'sin base en el backtest'}
                </span>
                <span style={{ color: c.dentroDelBacktest === null ? 'var(--t3)' : c.dentroDelBacktest ? 'var(--up)' : 'var(--down)', fontWeight: 700 }}>
                  {c.dentroDelBacktest === null ? `n < ${c.nMinimo}: no se compara` : c.dentroDelBacktest ? 'dentro' : 'FUERA'}
                </span>
              </div>
            ))}
            {a.reventon.extremo.observadas > 0 && (
              <div style={{ font: '500 10.5px var(--sans)', color: 'var(--t3)' }} title={a.reventon.extremo.nota}>
                con alerta K-EXTREMO: {a.reventon.extremo.reventadas}/{a.reventon.extremo.observadas} reventaron
              </div>
            )}
            {a.reventon.revisionAbierta && (
              <div style={{ marginTop: 4, padding: '9px 12px', borderRadius: 10, background: 'var(--down-soft)', font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
                Nivel{a.reventon.fueraDelBacktest.length > 1 ? 'es' : ''} <b>{a.reventon.fueraDelBacktest.join(', ')}</b> fuera del rango del backtest con n suficiente:
                esto ABRE la revisión de los puntos del riesgo (docs/REVENTON.md §5); no los mueve.
              </div>
            )}
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

      {vacio && (
        <Seccion titulo="TODAVÍA NO HAY NADA">
          <div style={{ font: '500 12px var(--sans)', color: 'var(--t2)' }}>
            Ningún veredicto dejó lección todavía. Esto se llena solo: cada caso que se cierra
            con una lección por lado aparece acá con su partido.
          </div>
        </Seccion>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '20px 0 10px', flexWrap: 'wrap' }}>
        <span style={{ font: '700 10px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>LECCIONES</span>
        <div style={{ display: 'flex', padding: 3, borderRadius: 9, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
          {[['', 'todas'], ...d.estados.map((e) => [e, ETIQUETA_ESTADO[e]?.toLowerCase() ?? e])].map(([k, label]) => (
            <button key={k} onClick={() => setEstado(k)}
              style={{ padding: '5px 10px', border: 0, borderRadius: 7, cursor: 'pointer', background: estado === k ? 'var(--bg3)' : 'transparent', color: estado === k ? 'var(--t1)' : 'var(--t2)', font: '600 10.5px var(--sans)' }}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {d.porSkill.map((sk) => (
        <PanelSkill key={sk.skill} sk={sk} onCambio={() => setRecarga((n) => n + 1)} />
      ))}

      {d.sinSkill.cuantas > 0 && (
        <Seccion titulo={`SIN SKILL DECLARADO · ${d.sinSkill.cuantas}`}>
          <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t2)', marginBottom: 9 }}>{d.sinSkill.porque}</div>
          {d.sinSkill.items.map((i) => <Leccion key={i.clave} it={i} onCambio={() => setRecarga((n) => n + 1)} />)}
        </Seccion>
      )}
    </div>
  )
}

function PanelSkill({ sk, onCambio }: { sk: SkillAprendizaje; onCambio: () => void }) {
  return (
    <section style={{ marginBottom: 14, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '13px 16px', flexWrap: 'wrap' }}>
        <span style={{ font: '700 13px var(--sans)', color: 'var(--t1)' }}>{sk.skill}</span>
        {(['acierto', 'parcial', 'fallo'] as const).map((v) => (
          (sk.atribuidos[v] ?? 0) > 0 && (
            <span key={v} style={{ padding: '2px 8px', borderRadius: 6, background: SUAVE_VER[v], color: COLOR_VER[v], font: '700 9.5px var(--mono)' }}>
              {sk.atribuidos[v]} {v}
            </span>
          )
        ))}
        <span style={{ marginLeft: 'auto', font: '600 10.5px var(--mono)', color: 'var(--t3)' }}>
          {sk.lecciones.pendiente ?? 0} pendiente{(sk.lecciones.pendiente ?? 0) === 1 ? '' : 's'} ·
          {' '}{sk.lecciones.aplicada ?? 0} aplicada{(sk.lecciones.aplicada ?? 0) === 1 ? '' : 's'}
        </span>
      </div>

      {/* EL SESGO SE LEE ANTES QUE LOS CONTEOS, NO DESPUÉS. */}
      <div style={{ padding: '0 16px 10px', font: '500 10.5px var(--sans)', color: 'var(--t3)' }}>
        {sk.sesgoDeAtribucion}
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

      <div style={{ padding: '0 16px 14px' }}>
        {sk.items.length === 0
          ? <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)' }}>Ninguna lección con este filtro.</div>
          : sk.items.map((i) => <Leccion key={i.clave} it={i} onCambio={onCambio} />)}
      </div>
    </section>
  )
}

function Leccion({ it, onCambio }: { it: LeccionItem; onCambio: () => void }) {
  const [abierto, setAbierto] = useState(false)
  const [version, setVersion] = useState(it.aplicadaEn)
  const [error, setError] = useState('')
  const [yendo, setYendo] = useState('')

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

  return (
    <div style={{ padding: '10px 0', borderTop: '1px solid var(--line)' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 9, flexWrap: 'wrap' }}>
        <span style={{ font: '700 10px var(--mono)', color: COLOR_VER[it.veredicto], textTransform: 'uppercase' }}>{it.veredicto}</span>
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

      {/* LO CONTAMINADO ENSEÑA, PERO NO MUEVE UN NÚMERO. Esto va pegado a la
          lección, no en una nota al pie de la sección: quien lee el dossier
          seis meses después no va a recordar la distinción de memoria. */}
      <div style={{ display: 'inline-block', marginTop: 6, padding: '3px 9px', borderRadius: 7, background: it.puedeMoverNumeros ? 'var(--up-soft)' : 'var(--bg3)', color: it.puedeMoverNumeros ? 'var(--up)' : 'var(--t2)', font: '600 10px var(--sans)' }}>
        {it.seleccion} · {it.modoEvaluacion} — {it.queAutoriza}
      </div>
      {it.mancha && (
        <div style={{ font: '500 10.5px var(--sans)', color: 'var(--mark)', marginTop: 4 }}>salvedad declarada: {it.mancha}</div>
      )}

      <div style={{ marginTop: 7 }}>
        <button onClick={() => setAbierto(!abierto)}
          style={{ padding: '4px 10px', borderRadius: 7, border: '1px solid var(--line)', background: 'transparent', color: 'var(--t2)', cursor: 'pointer', font: '600 10px var(--sans)' }}>
          {abierto ? 'Cerrar' : 'Mover de estado'}
        </button>
      </div>
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
