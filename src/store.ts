import { useCallback, useEffect, useRef, useState } from 'react'
import { CONFIG } from './config'
import type {
  KCondKey,
  KTypeKey,
  Match,
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
  /** Partido seleccionado (objeto completo: no depende de la lista del día visible). */
  match: Match | null
  /** Día visible en Partidos (yyyy-mm-dd, local). */
  fecha: string
  /** Equipo abierto en la página de equipo (clave interna). */
  teamKey: string | null
  /** Liga abierta en la página de liga (id del contrato). */
  ligaId: number | null
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
  chartMarket: string
  skillStatus: Record<string, SkillState>
  skillTime: Record<string, string>
  openReport: string | null
  history: HistoryEntry[]
}

export function hoyStr(): string {
  const d = new Date()
  return `${d.getFullYear()}-${('0' + (d.getMonth() + 1)).slice(-2)}-${('0' + d.getDate()).slice(-2)}`
}

const initialState: SadState = {
  theme: 'dark',
  section: 'partidos',
  matchId: null,
  match: null,
  fecha: hoyStr(),
  teamKey: null,
  ligaId: null,
  vw: typeof window !== 'undefined' ? window.innerWidth : 1280,
  forceMobile: false,
  oddsMode: 'prematch',
  marked: {},
  now: Date.now(),
  liveMin: 63,
  kType: 'res',
  kCond: 'total',
  kWindow: Infinity, // por defecto: toda la historia
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
  openLiga: (ligaId: number) => void
  selectMatch: (mt: Match) => () => void
  clearMatch: () => void
  setFecha: (fecha: string) => void
  setMode: (mode: OddsMode) => () => void
  toggleMark: (id: string) => void
  setKType: (c: KTypeKey) => () => void
  setKCond: (c: KCondKey) => () => void
  setWindow: (n: number) => () => void
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
    let raf = 0
    const onResize = () => {
      // throttle a un frame: resize dispara decenas de eventos por segundo
      if (raf) return
      raf = requestAnimationFrame(() => {
        raf = 0
        patch({ vw: window.innerWidth })
      })
    }
    window.addEventListener('resize', onResize)
    const iv = setInterval(() => {
      if (CONFIG.dataSource === 'http') return // el minuto real viene de la ingesta; el reloj simulado es solo demo
      const st = stateRef.current
      if (st.section !== 'cuotas' || st.oddsMode !== 'live') return // only re-render while live
      tickRef.current++
      const p: Partial<SadState> = { now: Date.now() }
      if (tickRef.current % 2 === 0 && st.liveMin < 90) p.liveMin = st.liveMin + 1
      patch(p)
    }, 1000)
    return () => {
      clearInterval(iv)
      if (raf) cancelAnimationFrame(raf)
      window.removeEventListener('resize', onResize)
    }
  }, [patch])

  const toggleTheme = useCallback(() => patchFn((prev) => ({ theme: prev.theme === 'dark' ? 'light' : 'dark' })), [patchFn])
  const go = useCallback((sec: SectionKey) => () => patch({ section: sec }), [patch])
  const openTeam = useCallback((teamKey: string) => patch({ teamKey, section: 'equipo' }), [patch])
  const openLiga = useCallback((ligaId: number) => patch({ ligaId, section: 'liga' }), [patch])

  const selectMatch = useCallback(
    (mt: Match) => () => {
      const live = mt.status === 'live'
      const lm = live ? parseInt(mt.min) || 60 : 63
      // seleccionar un partido lleva directo a Cuotas; los reportes de skills
      // son por partido, así que se resetean al cambiar de selección
      patchFn((prev) => (prev.matchId === mt.id ? { section: 'cuotas' } : {
        matchId: mt.id,
        match: mt,
        section: 'cuotas',
        oddsMode: live ? 'live' : 'prematch',
        liveMin: lm,
        skillStatus: { efe: 'idle', sad: 'idle', tac: 'idle', tl: 'idle' },
        skillTime: {},
        openReport: null,
      }))
    },
    [patchFn],
  )

  const clearMatch = useCallback(() => patch({ matchId: null, match: null }), [patch])
  const setFecha = useCallback((fecha: string) => patch({ fecha }), [patch])
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
    openLiga,
    selectMatch,
    clearMatch,
    setFecha,
    setMode,
    toggleMark,
    setKType,
    setKCond,
    setWindow,
    setChartMarket,
    generate,
    openReport,
    toggleMobile,
  }
}
