// Prompt reusable de barrido de liga para el Claude de escritorio
// (docs/DESPENSA_DESKTOP.md). Lo genera el botón de la página de Liga con los
// nombres EXACTOS de la app; el backend además canoniza variantes.

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
