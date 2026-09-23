import { useState } from 'react'
import { CONFIG } from '../config'
import { guardarLlaveAdmin, llaveAdmin } from '../lib/admin'

/** 🔑 Modo administrador: pegar la llave maestra una vez (queda solo en este
 *  navegador) o borrarla. Sin ella la web lee todo y no escribe ni gasta nada. */
export function BotonAdmin({ size = 34 }: { size?: number }) {
  const [activo, setActivo] = useState(() => !!llaveAdmin())
  if (CONFIG.dataSource !== 'http') return null // la demo no habla con el backend

  async function alternar() {
    if (activo) {
      if (!window.confirm('¿Salir del modo administrador? Se borra la llave de este navegador.')) return
      guardarLlaveAdmin('')
      setActivo(false)
      window.location.reload()
      return
    }
    const llave = (window.prompt('Llave maestra (SAD_API_TOKEN). Queda guardada SOLO en este navegador; nunca en el código de la web.') ?? '').trim()
    if (!llave) return
    // se prueba antes de guardarla: una llave mal pegada no debe dejar la web
    // «en modo admin» sin serlo
    try {
      const r = await fetch(CONFIG.apiBaseUrl + '/fixtures?limit=1', { headers: { Authorization: `Bearer ${llave}` } })
      if (r.status === 401) {
        window.alert('Esa llave no es válida para el backend.')
        return
      }
    } catch {
      window.alert('No se pudo comprobar la llave (sin conexión con el backend). No se guardó.')
      return
    }
    if (!guardarLlaveAdmin(llave)) {
      window.alert('Este navegador no deja guardar datos (¿navegación privada?).')
      return
    }
    setActivo(true)
    window.location.reload()
  }

  return (
    <button onClick={alternar}
      title={activo ? 'Modo administrador activo: tocá para salir' : 'Modo lectura: tocá para activar el modo administrador'}
      style={{ width: size, height: size, flexShrink: 0, borderRadius: size > 35 ? 10 : 9, border: `1px solid ${activo ? 'var(--accent)' : 'var(--line)'}`, background: activo ? 'var(--accent-soft)' : 'var(--bg2)', color: activo ? 'var(--accent)' : 'var(--t3)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="7.5" cy="15.5" r="4.5" /><path d="M10.7 12.3L21 2M16 7l3 3M14 9l2 2" />
      </svg>
    </button>
  )
}
