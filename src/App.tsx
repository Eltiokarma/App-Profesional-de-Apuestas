import { useSad } from './store'
import { CONFIG } from './config'
import { matchView } from './lib/view'
import { loadMatches } from './services/appdata'
import { useAsync } from './services/useAsync'
import { Sidebar } from './components/Sidebar'
import { DesktopHeader } from './components/DesktopHeader'
import { MobileHeader } from './components/MobileHeader'
import { BottomNav } from './components/BottomNav'
import { EmptyState } from './components/EmptyState'
import { Partidos } from './sections/Partidos'
import { Equipo } from './sections/Equipo'
import { Liga } from './sections/Liga'
import { Cuotas } from './sections/Cuotas'
import { Burbujas } from './sections/Burbujas'
import { Skills } from './sections/Skills'
import { Estadisticas } from './sections/Estadisticas'

const PAD = '16px'

type Style = React.CSSProperties

export function App() {
  const store = useSad()
  const { s } = store
  // en http la lista del día se refresca sola (marcadores/estados de la
  // ingesta en vivo llegan sin recargar la página); en mock no hace falta
  const fixtures = useAsync(
    () => loadMatches(s.fecha),
    s.fecha,
    CONFIG.dataSource === 'http' ? { refreshMs: CONFIG.pollLiveMs } : undefined,
  )
  const matches = fixtures.data ?? []
  const m = s.match ?? undefined

  const isMobile = s.forceMobile || s.vw < 760
  const isDesktop = !isMobile
  const phonePreview = s.forceMobile && s.vw >= 760

  const rootStyle: Style = {
    ['--pad' as string]: PAD,
    height: '100vh',
    width: '100%',
    color: 'var(--t1)',
    fontFamily: 'var(--sans)',
    overflow: 'hidden',
    fontFeatureSettings: "'tnum' 1",
    ...(phonePreview
      ? { display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#06090D', padding: 20 }
      : { display: 'block', background: 'var(--bg)' }),
  }

  const shellStyle: Style = phonePreview
    ? { display: 'flex', flexDirection: 'column', width: 404, height: 874, maxHeight: '94vh', background: 'var(--bg)', borderRadius: 36, overflow: 'hidden', border: '2px solid #1b2230', boxShadow: '0 30px 90px rgba(0,0,0,.6)', position: 'relative' }
    : isMobile
      ? { display: 'flex', flexDirection: 'column', width: '100%', height: '100%', background: 'var(--bg)', overflow: 'hidden', position: 'relative' }
      : { display: 'flex', flexDirection: 'row', width: '100%', height: '100%', background: 'var(--bg)', overflow: 'hidden', position: 'relative' }

  const colStyle: Style = { flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, minHeight: 0, position: 'relative' }
  const contentPad = isMobile ? '14px 14px 22px' : '24px'

  const isLive = s.section === 'cuotas' && s.oddsMode === 'live'
  const liveBadge = !!m && isLive
  const mv = m ? matchView(m) : null

  // Partidos y Equipo no requieren partido seleccionado
  const needsMatch = s.section === 'cuotas' || s.section === 'burbujas' || s.section === 'skills' || s.section === 'estadisticas'
  // la selección vive en el store: las secciones ya no dependen de la lista del día
  const showEmpty = needsMatch && !m
  const showContent = !!m

  return (
    <div data-theme={s.theme} style={rootStyle}>
      <div style={shellStyle}>
        {isDesktop && <Sidebar store={store} />}

        <div style={colStyle}>
          {isMobile && (
            <MobileHeader store={store} mv={mv} phonePreview={phonePreview} liveBadge={liveBadge} liveMinute={s.liveMin} />
          )}
          {isDesktop && (
            <DesktopHeader store={store} mv={mv} liveBadge={liveBadge} liveMinute={s.liveMin} liveScore={m ? m.score : ''} />
          )}

          <main className="sad-scroll" style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: contentPad }}>
            {showEmpty && <EmptyState store={store} />}
            {s.section === 'partidos' && (
              <Partidos store={store} matches={matches} loading={fixtures.loading} error={fixtures.error} reload={fixtures.reload} isMobile={isMobile} />
            )}
            {s.section === 'equipo' && s.teamKey && <Equipo store={store} teamKey={s.teamKey} isMobile={isMobile} />}
            {s.section === 'equipo' && !s.teamKey && <EmptyState store={store} />}
            {s.section === 'liga' && s.ligaId != null && <Liga store={store} ligaId={s.ligaId} isMobile={isMobile} />}
            {s.section === 'liga' && s.ligaId == null && <EmptyState store={store} />}
            {showContent && m && s.section === 'cuotas' && <Cuotas store={store} m={m} isMobile={isMobile} />}
            {showContent && m && s.section === 'burbujas' && <Burbujas store={store} m={m} isMobile={isMobile} />}
            {showContent && m && s.section === 'skills' && <Skills store={store} m={m} isMobile={isMobile} />}
            {showContent && m && s.section === 'estadisticas' && <Estadisticas store={store} m={m} isMobile={isMobile} />}
          </main>

          {isMobile && <BottomNav store={store} />}
        </div>
      </div>
    </div>
  )
}
