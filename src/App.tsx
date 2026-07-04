import { useSad } from './store'
import { matchView } from './lib/view'
import { loadMatches } from './services/appdata'
import { useAsync } from './services/useAsync'
import { Sidebar } from './components/Sidebar'
import { DesktopHeader } from './components/DesktopHeader'
import { MobileHeader } from './components/MobileHeader'
import { BottomNav } from './components/BottomNav'
import { EmptyState, Skeleton } from './components/EmptyState'
import { Partidos } from './sections/Partidos'
import { Equipo } from './sections/Equipo'
import { Cuotas } from './sections/Cuotas'
import { Burbujas } from './sections/Burbujas'
import { Skills } from './sections/Skills'
import { Estadisticas } from './sections/Estadisticas'

const ACCENT = '#5B8DEF'
const PAD = '16px'

type Style = React.CSSProperties

export function App() {
  const store = useSad()
  const { s } = store
  const fixtures = useAsync(loadMatches, 'fixtures')
  const matches = fixtures.data ?? []
  const m = matches.find((x) => x.id === s.matchId)

  const isMobile = s.forceMobile || s.vw < 760
  const isDesktop = !isMobile
  const phonePreview = s.forceMobile && s.vw >= 760

  const rootStyle: Style = {
    ['--accent' as string]: ACCENT,
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
  const showEmpty = needsMatch && !m && !fixtures.loading && !fixtures.error
  const showSkeleton = needsMatch && ((!!m && s.loading) || fixtures.loading)
  const showContent = !!m && !s.loading && !fixtures.loading

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
            {fixtures.error && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', marginBottom: 14, borderRadius: 12, background: 'var(--down-soft)', border: '1px solid color-mix(in oklch,var(--down),transparent 55%)' }}>
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--down)', flexShrink: 0 }}></span>
                <span style={{ font: '500 12.5px var(--sans)', color: 'var(--t1)', flex: 1 }}>No se pudieron cargar los partidos: {fixtures.error}</span>
                <button onClick={fixtures.reload} style={{ padding: '7px 13px', borderRadius: 8, border: 0, background: 'var(--down)', color: '#fff', cursor: 'pointer', font: '600 11.5px var(--sans)', flexShrink: 0 }}>Reintentar</button>
              </div>
            )}
            {showEmpty && <EmptyState store={store} />}
            {showSkeleton && <Skeleton />}
            {s.section === 'partidos' && (
              <Partidos store={store} matches={matches} loading={fixtures.loading} error={fixtures.error} reload={fixtures.reload} isMobile={isMobile} />
            )}
            {s.section === 'equipo' && s.teamKey && <Equipo store={store} teamKey={s.teamKey} isMobile={isMobile} />}
            {s.section === 'equipo' && !s.teamKey && <EmptyState store={store} />}
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
