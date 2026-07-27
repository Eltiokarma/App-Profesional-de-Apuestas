import type { EslabonDtpDTO } from '../api/types'

/** Pizarra del DTP (docs/efe-dtp/DTP_DISENO.md §4): CIERRE del partido
 *  anterior arriba (autopsia de goles con responsables) y APERTURA del próximo
 *  abajo (duelos por carril, plan por tramos). Regla "real o nada": cada bloque
 *  solo se pinta si el análisis lo trae — un DTP sin cierre es lo normal
 *  cuando no había pronóstico previo, y se dice en vez de disimularlo. */

const NIVEL = {
  principal: { label: 'PRINCIPAL', color: 'var(--down)', soft: 'var(--down-soft)' },
  secundario: { label: 'SECUNDARIO', color: 'var(--mark)', soft: 'var(--mark-soft)' },
  estructural: { label: 'ESTRUCTURAL', color: 'var(--t2)', soft: 'var(--bg3)' },
} as const

const VIA = {
  pelota_parada: 'Pelota parada',
  transicion: 'Transición',
  juego_abierto: 'Juego abierto',
} as const

const VEREDICTO = {
  acierto: { label: 'ACIERTO', color: 'var(--up)', soft: 'var(--up-soft)' },
  parcial: { label: 'PARCIAL', color: 'var(--mark)', soft: 'var(--mark-soft)' },
  fallo: { label: 'FALLO', color: 'var(--down)', soft: 'var(--down-soft)' },
} as const

// el orden del campo, no el alfabético: así se lee como se ve la cancha
const CARRILES = ['izquierda', 'centro', 'derecha'] as const

const card: React.CSSProperties = {
  padding: 16, borderRadius: 14, background: 'var(--bg2)', border: '1px solid var(--line)',
}
const titulo: React.CSSProperties = { font: '700 12px var(--sans)', color: 'var(--t1)' }
const sub: React.CSSProperties = { font: '500 10px var(--mono)', color: 'var(--t3)' }
const etiqueta: React.CSSProperties = {
  font: '600 8.5px var(--mono)', color: 'var(--t3)', letterSpacing: '.5px', textTransform: 'uppercase',
}
const texto: React.CSSProperties = { font: '500 12px var(--sans)', color: 'var(--t1)', lineHeight: 1.45 }

function Chip({ children, color = 'var(--t2)', soft = 'var(--bg3)' }: { children: React.ReactNode; color?: string; soft?: string }) {
  return (
    <span style={{ padding: '3px 9px', borderRadius: 6, background: soft, color, font: '600 10px var(--mono)', whiteSpace: 'nowrap' }}>
      {children}
    </span>
  )
}

function Campo({ label, children }: { label: string; children: React.ReactNode }) {
  if (!children) return null
  return (
    <div style={{ marginTop: 10 }}>
      <div style={etiqueta}>{label}</div>
      <div style={{ ...texto, marginTop: 3 }}>{children}</div>
    </div>
  )
}

export function DtpPizarra({ eslabon, isMobile }: { eslabon: EslabonDtpDTO; isMobile: boolean }) {
  const { apertura, cierre, registro } = eslabon
  const dosCol = isMobile ? '1fr' : '1fr 1fr'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* ── CIERRE del partido anterior ─────────────────────────────────── */}
      {cierre && (cierre.m4_goles?.length > 0 || cierre.m5?.peligro_real) && (
        <section style={card}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap', marginBottom: 4 }}>
            <span style={titulo}>Cierre del partido anterior</span>
            <span style={sub}>M4 autopsia de goles · M5 contraste con el pronóstico</span>
          </div>

          {/* M4: DISPARADOR → SECUENCIA → DEFINICIÓN, gol por gol */}
          {cierre.m4_goles?.map((g, i) => (
            <div key={i} style={{ marginTop: 12, padding: 14, borderRadius: 11, background: 'var(--bg)', border: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap' }}>
                <span style={{ font: '700 16px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>{g.gol}</span>
                <span style={{ font: '600 11px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>{g.minuto}&#39;</span>
                {g.via && <Chip color="var(--accent)" soft="var(--accent-soft)">{VIA[g.via] ?? g.via}</Chip>}
              </div>
              {/* la cadena del gol: se lee de un vistazo, en orden */}
              <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', gap: 10, marginTop: 11 }}>
                {([['Disparador', g.disparador], ['Secuencia', g.secuencia], ['Definición', g.definicion]] as const).map(
                  ([lab, val]) => val ? (
                    <div key={lab}>
                      <div style={etiqueta}>{lab}</div>
                      <div style={{ ...texto, marginTop: 3, fontSize: 11.5 }}>{val}</div>
                    </div>
                  ) : null,
                )}
              </div>
              {/* responsables: el método del protocolo, con su jerarquía */}
              {(g.responsables_error?.length > 0 || g.responsables_merito?.length > 0 || g.absolucion) && (
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 11, paddingTop: 10, borderTop: '1px solid var(--line)' }}>
                  {g.responsables_merito?.map((r, j) => (
                    <Chip key={`m${j}`} color="var(--up)" soft="var(--up-soft)">✓ {r}</Chip>
                  ))}
                  {g.responsables_error?.map((r, j) => (
                    <span key={`e${j}`} title={r.detalle} style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 9px', borderRadius: 6, background: NIVEL[r.nivel]?.soft ?? 'var(--bg3)' }}>
                      <span style={{ font: '600 10px var(--mono)', color: NIVEL[r.nivel]?.color ?? 'var(--t2)' }}>{r.jugador}</span>
                      <span style={{ font: '700 7.5px var(--mono)', color: NIVEL[r.nivel]?.color ?? 'var(--t3)', letterSpacing: '.4px' }}>
                        {NIVEL[r.nivel]?.label ?? r.nivel}
                      </span>
                    </span>
                  ))}
                  {g.absolucion && <Chip>⊘ {g.absolucion}</Chip>}
                </div>
              )}
            </div>
          ))}

          {/* M5 */}
          {cierre.m5 && (
            <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14, marginTop: 14 }}>
              <div>
                {cierre.m5.plan_funciono_hasta_min > 0 && (
                  <Campo label="El plan funcionó hasta">
                    <span style={{ font: '700 13px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
                      {cierre.m5.plan_funciono_hasta_min}&#39;
                    </span>
                  </Campo>
                )}
                <Campo label="Peligro real">{cierre.m5.peligro_real}</Campo>
                <Campo label="Cronología del giro">{cierre.m5.cronologia_giro}</Campo>
              </div>
              <div>
                {(cierre.m5.contraste_pronostico?.aciertos?.length > 0 || cierre.m5.contraste_pronostico?.fallos?.length > 0) ? (
                  <>
                    <div style={etiqueta}>Contraste con el pronóstico</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginTop: 5 }}>
                      {cierre.m5.contraste_pronostico.aciertos?.map((a, i) => (
                        <div key={`a${i}`} style={{ display: 'flex', gap: 7, font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
                          <span style={{ color: 'var(--up)', fontWeight: 700 }}>✓</span>{a}
                        </div>
                      ))}
                      {cierre.m5.contraste_pronostico.fallos?.map((f, i) => (
                        <div key={`f${i}`} style={{ display: 'flex', gap: 7, font: '500 11.5px var(--sans)', color: 'var(--t1)' }}>
                          <span style={{ color: 'var(--down)', fontWeight: 700 }}>✗</span>{f}
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  // anti-hindsight: sin pronóstico escrito antes NO se contrasta
                  <div style={{ ...sub, padding: '10px 12px', borderRadius: 9, background: 'var(--bg3)', lineHeight: 1.5 }}>
                    Sin pronóstico escrito antes de ese partido: no hay contraste ni veredicto.
                    El primer DTP de un equipo siempre es así — la cadena empieza a valer desde el siguiente.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* el registro: lo que queda para la próxima */}
          {registro && (registro.leccion || registro.que_paso) && (
            <div style={{ marginTop: 14, padding: 13, borderRadius: 11, background: 'var(--bg)', border: '1px solid var(--line)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap' }}>
                <span style={etiqueta}>Registro</span>
                {registro.veredicto && (
                  <Chip color={VEREDICTO[registro.veredicto]?.color} soft={VEREDICTO[registro.veredicto]?.soft}>
                    {VEREDICTO[registro.veredicto]?.label ?? registro.veredicto}
                  </Chip>
                )}
              </div>
              {registro.pronostico_clave && <Campo label="Se dijo">{registro.pronostico_clave}</Campo>}
              {registro.que_paso && <Campo label="Qué pasó">{registro.que_paso}</Campo>}
              {registro.leccion && (
                <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--line)' }}>
                  <div style={etiqueta}>Lección</div>
                  <div style={{ font: '600 12.5px var(--sans)', color: 'var(--accent)', marginTop: 3, lineHeight: 1.45 }}>{registro.leccion}</div>
                </div>
              )}
            </div>
          )}
        </section>
      )}

      {/* ── APERTURA del próximo ────────────────────────────────────────── */}
      {apertura && (
        <>
          <section style={card}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
              <span style={titulo}>Apertura · {eslabon.equipoFoco}</span>
              <span style={sub}>M1 el XI como declaración de intenciones</span>
            </div>
            {apertura.m1?.sistema && (
              <div style={{ font: '800 22px var(--mono)', color: 'var(--t1)', letterSpacing: '1px', margin: '8px 0 2px' }}>
                {apertura.m1.sistema}
              </div>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14 }}>
              <div>
                <Campo label="Señal del XI">{apertura.m1?.senal_del_xi}</Campo>
                <Campo label="Forma sin balón">{apertura.m1?.forma_sin_balon}</Campo>
                {apertura.m1?.cambios_vs_anterior?.length > 0 && (
                  <div style={{ marginTop: 10 }}>
                    <div style={etiqueta}>Cambios vs el partido anterior</div>
                    <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginTop: 5 }}>
                      {apertura.m1.cambios_vs_anterior.map((c, i) => <Chip key={i}>{c}</Chip>)}
                    </div>
                  </div>
                )}
              </div>
              <div>
                {apertura.m1?.roles_reasignados?.length > 0 && (
                  <div>
                    <div style={etiqueta}>Roles reasignados <span style={{ color: 'var(--mark)' }}>= la grieta</span></div>
                    <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginTop: 5 }}>
                      {apertura.m1.roles_reasignados.map((r, i) => (
                        <Chip key={i} color="var(--mark)" soft="var(--mark-soft)">{r}</Chip>
                      ))}
                    </div>
                  </div>
                )}
                {apertura.m1?.vulnerabilidad_propia && (
                  <div style={{ marginTop: 10, padding: '10px 12px', borderRadius: 9, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 65%)' }}>
                    <div style={etiqueta}>Vulnerabilidad que introduce este XI</div>
                    <div style={{ ...texto, marginTop: 3 }}>{apertura.m1.vulnerabilidad_propia}</div>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* M2: el mapa de carriles, en el orden de la cancha */}
          <section style={card}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
              <span style={titulo}>Mapa de duelos por carril</span>
              <span style={sub}>M2 · {apertura.m2?.choque_sistemas}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', gap: 10, marginTop: 12 }}>
              {CARRILES.map((c) => {
                const d = apertura.m2?.duelos_carril?.find((x) => (x.carril || '').toLowerCase().includes(c))
                return (
                  <div key={c} style={{ padding: 13, borderRadius: 11, background: 'var(--bg)', border: '1px solid var(--line)', opacity: d ? 1 : 0.5 }}>
                    <div style={{ ...etiqueta, color: 'var(--accent)' }}>{c}</div>
                    {d ? (
                      <>
                        <div style={{ ...texto, marginTop: 5, fontWeight: 600 }}>{d.duelo}</div>
                        {d.mismatch && (
                          <div style={{ marginTop: 7, font: '500 11px var(--sans)', color: 'var(--mark)', lineHeight: 1.4 }}>
                            ▸ {d.mismatch}
                          </div>
                        )}
                      </>
                    ) : (
                      <div style={{ ...sub, marginTop: 5 }}>sin duelo destacado</div>
                    )}
                  </div>
                )
              })}
            </div>
            {/* los duelos que no encajan en los tres carriles no se pierden */}
            {apertura.m2?.duelos_carril
              ?.filter((x) => !CARRILES.some((c) => (x.carril || '').toLowerCase().includes(c)))
              .map((d, i) => (
                <div key={i} style={{ marginTop: 8, ...texto }}>
                  <b>{d.carril}:</b> {d.duelo}{d.mismatch ? ` · ${d.mismatch}` : ''}
                </div>
              ))}

            <div style={{ display: 'grid', gridTemplateColumns: dosCol, gap: 14, marginTop: 14 }}>
              <div>
                {apertura.m2?.vida_util_rival?.minutos && (
                  <div>
                    <div style={etiqueta}>Vida útil del planteo rival</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 5 }}>
                      <span style={{ font: '700 15px var(--mono)', color: 'var(--t1)', fontVariantNumeric: 'tabular-nums' }}>
                        {apertura.m2.vida_util_rival.minutos}
                      </span>
                      <Chip color={apertura.m2.vida_util_rival.tipo === 'improvisado' ? 'var(--down)' : 'var(--t2)'}
                            soft={apertura.m2.vida_util_rival.tipo === 'improvisado' ? 'var(--down-soft)' : 'var(--bg3)'}>
                        {apertura.m2.vida_util_rival.tipo}
                      </Chip>
                    </div>
                  </div>
                )}
                <Campo label="Veredicto">{apertura.m2?.veredicto}</Campo>
                <Campo label="Razón táctica">{apertura.m2?.razon}</Campo>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {([['Vías de gol propias', apertura.m2?.vias_gol?.foco, 'var(--up)'],
                   ['Vías de gol del rival', apertura.m2?.vias_gol?.rival, 'var(--down)']] as const).map(
                  ([lab, lista, col]) => (lista?.length ?? 0) > 0 ? (
                    <div key={lab}>
                      <div style={{ ...etiqueta, color: col }}>{lab}</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 5 }}>
                        {lista!.map((v, i) => (
                          <div key={i} style={{ font: '500 11.5px var(--sans)', color: 'var(--t1)', lineHeight: 1.35 }}>· {v}</div>
                        ))}
                      </div>
                    </div>
                  ) : null,
                )}
              </div>
            </div>
          </section>

          {/* M3: el plan por tramos, como una línea de tiempo */}
          {apertura.m3_fases?.length > 0 && (
            <section style={card}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap', marginBottom: 12 }}>
                <span style={titulo}>Plan por fases</span>
                <span style={sub}>M3 · palancas concretas por tramo</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : `repeat(${apertura.m3_fases.length}, 1fr)`, gap: 10 }}>
                {apertura.m3_fases.map((f, i) => (
                  <div key={i} style={{ padding: 13, borderRadius: 11, background: 'var(--bg)', border: '1px solid var(--line)' }}>
                    <div style={{ font: '700 12px var(--mono)', color: 'var(--accent)', fontVariantNumeric: 'tabular-nums' }}>{f.tramo}&#39;</div>
                    <div style={{ ...texto, marginTop: 6, fontSize: 11.5 }}>{f.plan}</div>
                    {f.palancas?.length > 0 && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 9, paddingTop: 9, borderTop: '1px solid var(--line)' }}>
                        {f.palancas.map((p, j) => (
                          <div key={j} style={{ font: '500 11px var(--sans)', color: 'var(--t2)', lineHeight: 1.35 }}>▸ {p}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* M6: contexto */}
          {apertura.m6 && (apertura.m6.rotacion || apertura.m6.fatiga || apertura.m6.ausencias_clave) && (
            <section style={card}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap', marginBottom: 10 }}>
                <span style={titulo}>Contexto del partido</span>
                <span style={sub}>M6</span>
                <Chip color={apertura.m6.competitivo ? 'var(--up)' : 'var(--t2)'}
                      soft={apertura.m6.competitivo ? 'var(--up-soft)' : 'var(--bg3)'}>
                  {apertura.m6.competitivo ? 'competitivo' : 'amistoso'}
                </Chip>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(4, 1fr)', gap: 12 }}>
                {([['Rotación', apertura.m6.rotacion], ['Fatiga', apertura.m6.fatiga],
                   ['Ausencias clave', apertura.m6.ausencias_clave], ['Otros', apertura.m6.otros]] as const).map(
                  ([lab, val]) => val ? (
                    <div key={lab}>
                      <div style={etiqueta}>{lab}</div>
                      <div style={{ ...texto, marginTop: 3, fontSize: 11.5 }}>{val}</div>
                    </div>
                  ) : null,
                )}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}

/** La cadena del equipo (página de Equipo): pronóstico → qué pasó → lección.
 *  Es el activo que se acumula partido a partido. */
export function CadenaDtp({ eslabones }: { eslabones: EslabonDtpDTO[] }) {
  if (!eslabones.length) {
    return (
      <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: '10px 0' }}>
        Sin DTP generados todavía. Cada uno cierra el partido anterior y abre el siguiente.
      </div>
    )
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {eslabones.map((e) => (
        <div key={e.partidoN} style={{ padding: '10px 12px', borderRadius: 10, background: 'var(--bg)', border: '1px solid var(--line)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ font: '700 11px var(--mono)', color: 'var(--t3)', fontVariantNumeric: 'tabular-nums' }}>N{e.partidoN}</span>
            <span style={{ font: '600 12px var(--sans)', color: 'var(--t1)', flex: 1, minWidth: 0 }}>{e.rival ?? '—'}</span>
            {e.fecha && <span style={{ font: '500 10px var(--mono)', color: 'var(--t3)' }}>{e.fecha}</span>}
            {e.registro?.veredicto && (
              <Chip color={VEREDICTO[e.registro.veredicto]?.color} soft={VEREDICTO[e.registro.veredicto]?.soft}>
                {VEREDICTO[e.registro.veredicto]?.label}
              </Chip>
            )}
            {/* un eslabón sin cierre es un partido aún por jugar (o sin cerrar) */}
            {!e.cierre && <Chip>abierto</Chip>}
          </div>
          {e.registro?.leccion && (
            <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t2)', marginTop: 5, lineHeight: 1.4 }}>
              {e.registro.leccion}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
