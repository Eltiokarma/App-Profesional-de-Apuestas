import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')
  // En producción, modo http sin URL del backend produce un bundle roto
  // (caería al fallback localhost): mejor fallar el build aquí.
  if (mode === 'production' && env.VITE_DATA_SOURCE === 'http' && !env.VITE_API_BASE_URL) {
    throw new Error('VITE_DATA_SOURCE=http requiere VITE_API_BASE_URL en el build de producción (ver .env.example)')
  }
  return { plugins: [react()] }
})
