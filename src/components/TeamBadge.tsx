import { useState } from 'react'
import type { CSSProperties } from 'react'

interface Props {
  logo?: string | null
  short: string
  color: string
  fg: string
  size: number
  /** Anillo exterior (headers): boxShadow doble sobre el fondo indicado. */
  ring?: boolean
  style?: CSSProperties
}

/** Escudo del equipo: imagen del contrato (Equipo.logo) con fallback a las
 *  iniciales de color si no hay URL o la imagen falla al cargar. */
export function TeamBadge({ logo, short, color, fg, size, ring, style }: Props) {
  const [roto, setRoto] = useState(false)
  const base: CSSProperties = {
    width: size,
    height: size,
    borderRadius: '50%',
    flexShrink: 0,
    boxShadow: ring ? '0 0 0 2px var(--bg1),0 0 0 3px var(--line)' : undefined,
    ...style,
  }
  if (logo && !roto) {
    return (
      <span style={{ ...base, background: 'var(--bg3)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
        <img
          src={logo}
          alt={short}
          loading="lazy"
          onError={() => setRoto(true)}
          style={{ width: '78%', height: '78%', objectFit: 'contain', display: 'block' }}
        />
      </span>
    )
  }
  return (
    <span style={{ ...base, background: color, color: fg, display: 'flex', alignItems: 'center', justifyContent: 'center', font: `700 ${Math.round(size * 0.37)}px var(--mono)` }}>
      {short}
    </span>
  )
}
