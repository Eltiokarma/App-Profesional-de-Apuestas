import { MATCHES } from './data'
import { useSad } from './store'
import { matchView } from './lib/view'
import { Sidebar } from './components/Sidebar'
import { DesktopHeader } from './components/DesktopHeader'
import { MobileHeader } from './components/MobileHeader'
import { MatchPicker } from './components/MatchPicker'
import { BottomNav } from './components/BottomNav'
import { EmptyState, Skeleton } from './components/EmptyState'
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
  const m = MATCHES.find((x) => x.id === s.matchId)

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

  const pickerStyle: Style = {
    ...(isMobile
      ? { position: 'absolute', left: 10, right: 10, top: 8, zIndex: 41, maxHeight: '84%', overflowY: 'auto', overflowX: 'hidden' }
      : { position: 'absolute', top: 78, right: 22, width: 380, zIndex: 41 }),
    background: 'var(--bg1)',
    border: '1px solid var(--line2)',
    borderRadius: 14,
    boxShadow: 'var(--shadow)',
    padding: 10,
  }

  const isLive = s.section === 'cuotas' && s.oddsMode === 'live'
  const liveBadge = !!m && isLive
  const mv = m ? matchView(m) : null

  const showEmpty = !m
  const showSkeleton = !!m && s.loading
  const showContent = !!m && !s.loading

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

          {s.pickerOpen && <MatchPicker store={store} current={m} pickerStyle={pickerStyle} />}

          <main className="sad-scroll" style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: contentPad }}>
            {showEmpty && <EmptyState store={store} />}
            {showSkeleton && <Skeleton />}
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
