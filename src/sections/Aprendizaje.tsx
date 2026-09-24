import { useState } from 'react'
import type { InventarioLecciones, LeccionItem, ModoFalloEtiqueta, RevisionSkillDTO, SkillAprendizaje } from '../api/types'
import { getDataSource } from '../services/datasource'
import { useAsync } from '../services/useAsync'

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

export function Aprendizaje({ isMobile }: { isMobile: boolean }) {
  const [estado, setEstado] = useState('')
  // LA COHORTE VIGENTE ES LA VISTA POR DEFECTO. Los casos de la primera semana
  // se hicieron con el DT viejo y el TDE sin nivel: la etiqueta de población
  // dice «ciega» y el insumo estaba roto. Se ven, pero aparte.
  const [cohorte, setCohorte] = useState('vigente')
  const [recarga, setRecarga] = useState(0)
  const inv = useAsync<InventarioLecciones>(
    () => getDataSource().lecciones({ ...(estado ? { estado } : {}), ...(cohorte ? { cohorte } : {}) }),
    `${estado}|${cohorte}|${recarga}`)

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

      {/* LA COHORTE: de qué época del proceso son los casos que se están
          mirando. Se sella al depositar y no cambia con un re-depósito. */}
      {d.cohortes && d.cohortes.length > 0 && (
        <Seccion titulo="LA COHORTE" nota={d.notaCohortes}>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
            {[{ clave: '', etiqueta: 'todas', casos: d.cohortes.reduce((a, c) => a + c.casos, 0), cuarentena: 0, descripcion: 'todas las épocas juntas: sirve para contar, no para calibrar' },
              ...d.cohortes.map((c) => ({ clave: c.vigente ? 'vigente' : c.clave, etiqueta: c.vigente ? `vigente · ${c.clave}` : c.clave, casos: c.casos, cuarentena: c.enCuarentena, descripcion: c.descripcion }))]
              .map((c) => {
                const sel = cohorte === c.clave
                return (
                  <button key={c.clave || 'todas'} onClick={() => setCohorte(c.clave)} title={c.descripcion}
                    style={{ padding: '6px 11px', borderRadius: 8, border: `1px solid ${sel ? 'var(--accent)' : 'var(--line)'}`, background: sel ? 'var(--bg3)' : 'transparent', color: sel ? 'var(--t1)' : 'var(--t2)', cursor: 'pointer', font: '600 10.5px var(--sans)' }}>
                    {c.etiqueta} <span style={{ font: '600 10px var(--mono)', color: 'var(--t3)' }}>· {c.casos} {c.casos === 1 ? 'caso' : 'casos'}{c.cuarentena ? ` · ${c.cuarentena} en cuarentena` : ''}</span>
                  </button>
                )
              })}
          </div>
          {(() => {
            const sel = d.cohortes.find((c) => (cohorte === 'vigente' ? c.vigente : c.clave === cohorte))
            return sel ? <div style={{ font: '500 11px var(--sans)', color: 'var(--t2)', marginTop: 8 }}>{sel.descripcion}</div> : null
          })()}
        </Seccion>
      )}

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

      {/* LO APARTADO SE VE, PARA QUE NADIE LO OLVIDE NI LO DISIMULE. */}
      {d.enCuarentena && d.enCuarentena.cuantas > 0 && (
        <Seccion titulo={`EN CUARENTENA · ${d.enCuarentena.cuantas}`} nota={d.enCuarentena.porque}>
          {d.enCuarentena.items.map((i) => <Leccion key={i.clave} it={i} onCambio={() => setRecarga((n) => n + 1)} />)}
        </Seccion>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '20px 0 10px', flexWrap: 'wrap' }}>
        <span style={{ font: '700 10px var(--mono)', color: 'var(--t3)', letterSpacing: '.6px' }}>LECCIONES</span>
        {/* flexWrap: cinco estados no entran en una fila de teléfono (360 px) */}
        <div style={{ display: 'flex', flexWrap: 'wrap', padding: 3, borderRadius: 9, background: 'var(--bg2)', border: '1px solid var(--line)' }}>
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

      <div style={{ padding: '0 16px 14px' }}>
        {sk.items.length === 0
          ? <div style={{ font: '500 11px var(--sans)', color: 'var(--t3)' }}>Ninguna lección con este filtro.</div>
          : sk.items.map((i) => <Leccion key={i.clave} it={i} onCambio={onCambio} />)}
      </div>
    </section>
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

function Leccion({ it, onCambio }: { it: LeccionItem; onCambio: () => void }) {
  const [abierto, setAbierto] = useState(false)
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
        {it.cuarentena && it.cuarentenaAutomatica ? (
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
