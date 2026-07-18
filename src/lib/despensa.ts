// Prompt reusable de barrido de liga para el Claude de escritorio
// (docs/DESPENSA_DESKTOP.md). Lo genera el botón de la página de Liga con los
// nombres EXACTOS de la app; el backend además canoniza variantes.

export function promptDespensaLiga(liga: string, equipos: string[]): string {
  const lista = equipos.map((e) => `- ${e}`).join('\n')
  return `Investiga en la web, con fuentes de hoy, a TODOS estos equipos de ${liga}:

${lista}

Para CADA equipo produce resúmenes TEXTUALES densos y autocontenidos
(nombres, fechas, cifras, fuente) de estos campos:

- dt: entrenador actual, fecha de asunción, contexto (interino, cuestionado…).
- plantel: jugadores clave con posición y rendimiento, fichajes/salidas recientes, dependencias ofensivas.
- bajas: lesionados, sancionados y dudas para el próximo partido, con motivo.
- xi_reciente: el once más reciente y la formación utilizada.
- fixture: sus próximos 3-5 partidos con fechas y torneos.

ENTREGA POR TANDAS: un bloque de código JSON por cada 6 equipos (así ninguna
respuesta se corta). Cada bloque con esta forma exacta, sin texto fuera del
bloque:

{
  "equipos": [
    {
      "equipo": "<nombre EXACTAMENTE como te lo di>",
      "datos": { "dt": "…", "plantel": "…", "bajas": "…", "xi_reciente": "…", "fixture": "…" }
    }
  ],
  "fuentes": ["url1", "url2"]
}

Máximo ~120 palabras por campo; si algo no lo encontraste, pon "" en ese
campo. Cuando termines una tanda, sigue con la siguiente hasta cubrir todos.`
}
