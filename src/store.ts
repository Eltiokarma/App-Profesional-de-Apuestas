import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  KCondKey,
  KTypeKey,
  Match,
  ModelKey,
  OddsMode,
  SectionKey,
  SkillState,
} from './data/types'

export interface HistoryEntry {
  key: string
  time: string
  id: string
}

export interface SadState {
  theme: 'dark' | 'light'
  section: SectionKey
  matchId: string | null
  /** Equipo abierto en la página de equipo (clave interna). */
  teamKey: string | null
  loading: boolean
  vw: number
  forceMobile: boolean
  oddsMode: OddsMode
  marked: Record<string, boolean>
  now: number
  liveMin: number
  kType: KTypeKey
  kCond: KCondKey
  /** Ventana de la gráfica de K: nº de partidos (Infinity = toda la historia). */
  kWindow: number
  model: ModelKey
  chartMarket: string
  skillStatus: Record<string, SkillState>
  skillTime: Record<string, string>
  openReport: string | null
  history: HistoryEntry[]
}

const initialState: SadState = {
  theme: 'dark',
  section: 'partidos',
  matchId: 'm1',
  teamKey: null,
  loading: false,
  vw: typeof window !== 'undefined' ? window.innerWidth : 1280,
  forceMobile: false,
  oddsMode: 'prematch',
  marked: {},
  now: Date.now(),
  liveMin: 63,
  kType: 'res',
  kCond: 'total',
  kWindow: Infinity, // por defecto: toda la historia
  model: 'auto',
  chartMarket: '1x2',
  skillStatus: { efe: 'idle', sad: 'idle', tac: 'idle', tl: 'idle' },
  skillTime: {},
  openReport: null,
  history: [],
}

function nowText(): string {
  const d = new Date()
  return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2)
}

export interface SadStore {
  s: SadState
  toggleTheme: () => void
  go: (sec: SectionKey) => () => void
  openTeam: (teamKey: string) => void
  selectMatch: (mt: Match) => () => void
  clearMatch: () => void
  setMode: (mode: OddsMode) => () => void
  toggleMark: (id: string) => void
  setKType: (c: KTypeKey) => () => void
  setKCond: (c: KCondKey) => () => void
  setWindow: (n: number) => () => void
  setModel: (m: ModelKey) => () => void
  setChartMarket: (key: string) => void
  generate: (key: string) => () => void
  openReport: (key: string) => () => void
  toggleMobile: () => void
}

export function useSad(): SadStore {
  const [s, setS] = useState<SadState>(initialState)

  const patch = useCallback((p: Partial<SadState>) => setS((prev) => ({ ...prev, ...p })), [])
  const patchFn = useCallback((fn: (prev: SadState) => Partial<SadState>) => setS((prev) => ({ ...prev, ...fn(prev) })), [])

  // keep a live ref of state for the interval callback
  const stateRef = useRef(s)
  stateRef.current = s
  const tickRef = useRef(0)

  useEffect(() => {
    const onResize = () => patch({ vw: window.innerWidth })
    window.addEventListener('resize', onResize)
    const iv = setInterval(() => {
      const st = stateRef.current
      if (st.section !== 'cuotas' || st.oddsMode !== 'live') return // only re-render while live
      tickRef.current++
      const p: Partial<SadState> = { now: Date.now() }
      if (tickRef.current % 2 === 0 && st.liveMin < 90) p.liveMin = st.liveMin + 1
      patch(p)
    }, 1000)
    return () => {
      clearInterval(iv)
      window.removeEventListener('resize', onResize)
    }
  }, [patch])

  const toggleTheme = useCallback(() => patchFn((prev) => ({ theme: prev.theme === 'dark' ? 'light' : 'dark' })), [patchFn])
  const go = useCallback((sec: SectionKey) => () => patch({ section: sec }), [patch])
  const openTeam = useCallback((teamKey: string) => patch({ teamKey, section: 'equipo' }), [patch])

  const selectMatch = useCallback(
    (mt: Match) => () => {
      const live = mt.status === 'live'
      const lm = live ? parseInt(mt.min) || 60 : 63
      // seleccionar un partido lleva directo a Cuotas
      patch({ matchId: mt.id, section: 'cuotas', loading: true, oddsMode: live ? 'live' : 'prematch', liveMin: lm })
      setTimeout(() => patch({ loading: false }), 720)
    },
    [patch],
  )

  const clearMatch = useCallback(() => patch({ matchId: null }), [patch])
  const setMode = useCallback((mode: OddsMode) => () => patch({ oddsMode: mode }), [patch])
  const toggleMark = useCallback(
    (id: string) =>
      patchFn((prev) => {
        const m = { ...prev.marked }
        if (m[id]) delete m[id]
        else m[id] = true
        return { marked: m }
      }),
    [patchFn],
  )
  const setKType = useCallback((c: KTypeKey) => () => patch({ kType: c }), [patch])
  const setKCond = useCallback((c: KCondKey) => () => patch({ kCond: c }), [patch])
  const setWindow = useCallback((n: number) => () => patch({ kWindow: n }), [patch])
  const setModel = useCallback((m: ModelKey) => () => patch({ model: m }), [patch])
  const setChartMarket = useCallback((key: string) => patch({ chartMarket: key }), [patch])

  const generate = useCallback(
    (key: string) => () => {
      patchFn((prev) => ({ skillStatus: { ...prev.skillStatus, [key]: 'gen' } }))
      setTimeout(() => {
        const t = nowText()
        patchFn((prev) => {
          const hist = [{ key, time: t, id: key + '-' + Date.now() }, ...prev.history.filter((h) => h.key !== key)]
          return {
            skillStatus: { ...prev.skillStatus, [key]: 'done' },
            skillTime: { ...prev.skillTime, [key]: t },
            openReport: key,
            history: hist,
          }
        })
      }, 1700)
    },
    [patchFn],
  )

  const openReport = useCallback((key: string) => () => patch({ openReport: key }), [patch])
  const toggleMobile = useCallback(() => patchFn((prev) => ({ forceMobile: !prev.forceMobile })), [patchFn])

  return {
    s,
    toggleTheme,
    go,
    openTeam,
    selectMatch,
    clearMatch,
    setMode,
    toggleMark,
    setKType,
    setKCond,
    setWindow,
    setModel,
    setChartMarket,
    generate,
    openReport,
    toggleMobile,
  }
}
