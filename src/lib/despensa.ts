// Prompt reusable de barrido de liga para el Claude de escritorio
// (docs/DESPENSA_DESKTOP.md). Lo genera el botón de la página de Liga con los
// nombres EXACTOS de la app; el backend además canoniza variantes.
import type { CargaDespensaDTO } from '../api/types'

/** Extrae TODOS los bloques JSON de la despensa de un texto pegado (las
 *  tandas del barrido, aunque vengan con texto o ```json entre medio) y los
 *  funde en un solo payload — la liga entera se sube de una pegada. */
export function extraerBloquesDespensa(texto: string): CargaDespensaDTO {
  const objetos: CargaDespensaDTO[] = []
  let depth = 0
  let start = -1
  let inStr = false
  let esc = false
  for (let i = 0; i < texto.length; i++) {
    const ch = texto[i]
    if (inStr) {
      if (esc) esc = false
      else if (ch === '\\') esc = true
      else if (ch === '"') inStr = false
      continue
    }
    if (ch === '"') {
      if (depth > 0) inStr = true
      continue
    }
    if (ch === '{') {
      if (depth === 0) start = i
      depth++
    } else if (ch === '}') {
      depth = Math.max(0, depth - 1)
      if (depth === 0 && start >= 0) {
        try {
          const o = JSON.parse(texto.slice(start, i + 1)) as CargaDespensaDTO
          if (o && Array.isArray(o.equipos) && o.equipos.length) objetos.push(o)
        } catch {
          /* bloque que no es JSON válido: se ignora */
        }
        start = -1
      }
    }
  }
  return {
    equipos: objetos.flatMap((o) => o.equipos),
    fuentes: [...new Set(objetos.flatMap((o) => o.fuentes ?? []))],
  }
}

export function promptDespensaLiga(liga: string, equipos: string[]): string {
  const lista = equipos.map((e) => `- ${e}`).join('\n')
  return `Investiga en la web, con fuentes de hoy, a TODOS estos equipos de ${liga}:

${lista}

SOLO estos tres campos por equipo — NO investigues tabla, resultados,
calendario, alineaciones, formaciones ni estadísticas de jugadores: la app ya
los saca de su propia base y de su API de datos. Interesa lo que las webs de
datos NO listan:

- dt: contexto del entrenador — fecha de asunción, interino o confirmado, cuestionamiento en prensa, relación con el vestuario.
- plantel: lectura CUALITATIVA — jerarquías reales, quién está en forma o caído, fichajes/salidas recientes y cómo encajan, conflictos o líos internos.
- bajas: dudas y novedades de PRENSA para el próximo partido — las lesiones confirmadas ya las tiene la app; interesan las dudas, sanciones internas, regresos y rumores de rotación.

ENTREGA POR TANDAS: un bloque de código JSON por cada 6 equipos (así ninguna
respuesta se corta). Cada bloque con esta forma exacta, sin texto fuera del
bloque:

{
  "equipos": [
    {
      "equipo": "<nombre EXACTAMENTE como te lo di>",
      "datos": { "dt": "…", "plantel": "…", "bajas": "…" }
    }
  ],
  "fuentes": ["url1", "url2"]
}

Máximo ~120 palabras por campo; si algo no lo encontraste, pon "" en ese
campo. Cuando termines una tanda, sigue con la siguiente hasta cubrir todos.`
}
