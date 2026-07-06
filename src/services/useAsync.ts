import { useCallback, useEffect, useRef, useState } from 'react'

export interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
  reload: () => void
}

/**
 * Carga async con estados de loading/error y recarga manual.
 * `key` reinicia la carga cuando cambia (p. ej. el id del partido).
 */
export function useAsync<T>(fn: () => Promise<T>, key: unknown): AsyncState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)
  const fnRef = useRef(fn)
  fnRef.current = fn
  const prevKey = useRef(key)

  useEffect(() => {
    let alive = true
    if (prevKey.current !== key) {
      // al cambiar de key no puede quedar visible el dato del key anterior
      prevKey.current = key
      setData(null)
    }
    setLoading(true)
    setError(null)
    fnRef
      .current()
      .then((d) => {
        if (alive) {
          setData(d)
          setLoading(false)
        }
      })
      .catch((e: unknown) => {
        if (alive) {
          setError(e instanceof Error ? e.message : 'error de datos')
          setLoading(false)
        }
      })
    return () => {
      alive = false
    }
  }, [key, tick])

  const reload = useCallback(() => setTick((t) => t + 1), [])
  return { data, loading, error, reload }
}
