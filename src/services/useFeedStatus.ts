import { useEffect, useState } from 'react'
import { CONFIG, type DataSourceMode } from '../config'
import { getDataSource, type FeedHealth } from './datasource'

export interface FeedStatus extends FeedHealth {
  mode: DataSourceMode
  checking: boolean
}

/**
 * Estado real de la fuente de datos. En modo http hace health-check periódico
 * al backend (latencia incluida); en modo mock informa una sola vez.
 */
export function useFeedStatus(): FeedStatus {
  const [st, setSt] = useState<FeedStatus>({
    mode: CONFIG.dataSource,
    ok: CONFIG.dataSource === 'mock',
    latencyMs: null,
    detail: '',
    checking: true,
  })

  useEffect(() => {
    const ds = getDataSource()
    let alive = true
    const run = async () => {
      const h = await ds.health()
      if (alive) setSt({ mode: ds.mode, ...h, checking: false })
    }
    run()
    if (ds.mode !== 'http') return
    const iv = setInterval(run, CONFIG.pollHealthMs)
    return () => {
      alive = false
      clearInterval(iv)
    }
  }, [])

  return st
}
