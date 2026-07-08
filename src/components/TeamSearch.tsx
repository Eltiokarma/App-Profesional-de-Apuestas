import { useEffect, useRef, useState } from 'react'
import type { EquipoDTO } from '../api/types'
import { ensureTeam, searchTeams } from '../services/appdata'
import type { SadStore } from '../store'
import { TeamBadge } from './TeamBadge'

/** Buscador inteligente de equipos (sin tildes, ranking por prefijo). */
export function TeamSearch({ store, width = 240 }: { store: SadStore; width?: number | string }) {
  const [q, setQ] = useState('')
  const [res, setRes] = useState<EquipoDTO[]>([])
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(false)
  const boxRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const t = q.trim()
    if (t.length < 2) {
      setRes([])
      setBusy(false)
      setErr(false)
      return
    }
    setBusy(true)
    setErr(false)
    let alive = true // descarta respuestas de consultas ya reemplazadas
    const timer = setTimeout(() => {
      searchTeams(t)
        .then((r) => {
          if (!alive) return
          setRes(r)
          setBusy(false)
        })
        .catch(() => {
          if (!alive) return
          setRes([])
          setErr(true)
          setBusy(false)
        })
    }, 250)
    return () => {
      alive = false
      clearTimeout(timer)
    }
  }, [q])

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const pick = (dto: EquipoDTO) => {
    const key = ensureTeam(dto)
    setQ('')
    setRes([])
    setOpen(false)
    store.openTeam(key)
  }

  return (
    <div ref={boxRef} style={{ position: 'relative', width }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '9px 12px', borderRadius: 10, border: '1px solid var(--line)', background: 'var(--bg2)' }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
          <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" />
        </svg>
        <input
          value={q}
          onChange={(e) => {
            setQ(e.target.value)
            setOpen(true)
          }}
          onFocus={() => setOpen(true)}
          placeholder="Buscar equipo…"
          style={{ flex: 1, minWidth: 0, border: 0, outline: 'none', background: 'transparent', color: 'var(--t1)', font: '600 12.5px var(--sans)' }}
        />
        {busy && <span style={{ width: 12, height: 12, border: '2px solid var(--accent-soft)', borderTopColor: 'var(--accent)', borderRadius: '50%', animation: 'sadspin .7s linear infinite', flexShrink: 0 }}></span>}
      </div>
      {open && q.trim().length >= 2 && (
        <div style={{ position: 'absolute', top: 'calc(100% + 6px)', left: 0, right: 0, zIndex: 45, background: 'var(--bg1)', border: '1px solid var(--line2)', borderRadius: 12, boxShadow: 'var(--shadow)', padding: 6, maxHeight: 320, overflowY: 'auto' }} className="sad-scroll">
          {res.map((r) => (
            <button key={r.id} className="sad-hover" onClick={() => pick(r)} style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '9px 10px', border: 0, borderRadius: 9, cursor: 'pointer', background: 'transparent', textAlign: 'left' }}>
              <TeamBadge logo={r.logo} short={r.abreviatura} color="var(--bg3)" fg="var(--t2)" size={26} style={{ border: '1px solid var(--line)' }} />
              <span style={{ font: '600 12.5px var(--sans)', color: 'var(--t1)', flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.nombre}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--t3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M9 6l6 6-6 6" /></svg>
            </button>
          ))}
          {!busy && err && (
            <div style={{ font: '500 11.5px var(--sans)', color: 'var(--down)', padding: '10px 12px' }}>Error de red al buscar · revisa la conexión con el servidor</div>
          )}
          {!busy && !err && res.length === 0 && (
            <div style={{ font: '500 11.5px var(--sans)', color: 'var(--t3)', padding: '10px 12px' }}>Sin resultados para "{q.trim()}"</div>
          )}
        </div>
      )}
    </div>
  )
}
