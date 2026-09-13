// De un texto pegado a un once — la puerta por la que entra el pantallazo.
//
// El usuario copia la alineación de donde la tenga (BeSoccer, la cuenta del
// club, lo que Cowork le devolvió al leerle el pantallazo) y la pega tal cual.
// Aquí se limpia: números de camiseta, viñetas, la posición entre paréntesis y
// la línea "Suplentes:" que parte la lista en dos.
//
// Lo que NO hace: adivinar. Si de un pegado salen 4 nombres, salen 4 — el
// backend dirá que no puede cerrar el bloque F con eso, y eso es correcto.

const MARCAS_BANCA = /^(suplentes?|banca|banquillo|sustitutos?|relevos?|bench|convocados?)\s*:?\s*$/i
const MARCAS_ONCE = /^(titulares?|once|alineaci[oó]n|xi)\s*:?\s*$/i

/** Un nombre por línea o separados por coma; "Suplentes:" abre la banca. */
export function parsearOnce(texto: string): { once: string[]; banca: string[] } {
  const once: string[] = []
  const banca: string[] = []
  let destino = once
  for (const crudo of (texto || '').split(/\r?\n/)) {
    const linea = crudo.trim()
    if (!linea) continue
    if (MARCAS_BANCA.test(linea)) { destino = banca; continue }
    if (MARCAS_ONCE.test(linea)) { destino = once; continue }
    // una línea puede traer varios nombres separados por coma o punto y coma
    for (const trozo of linea.split(/[,;]/)) {
      const nombre = limpiarNombre(trozo)
      if (nombre) destino.push(nombre)
    }
  }
  return { once, banca }
}

/** Quita dorsal, viñeta, posición entre paréntesis y minutaje. */
export function limpiarNombre(crudo: string): string {
  let s = (crudo || '').trim()
  s = s.replace(/^[-*•·–—•]+\s*/, '')          // viñetas
  s = s.replace(/^\(?\d{1,2}\)?[.)\-:]?\s+/, '')     // "9. ", "(9) ", "23 - "
  s = s.replace(/\([^)]*\)/g, ' ')                   // "(POR)", "(45')"
  s = s.replace(/\[[^\]]*\]/g, ' ')
  s = s.replace(/\b\d{1,3}'\b/g, ' ')                // minutos sueltos
  s = s.replace(/\s{2,}/g, ' ').trim()
  s = s.replace(/[.,;:]+$/, '').trim()
  // una línea de una sola palabra corta (un dorsal huérfano, "GK") no es nadie
  if (s.length < 3 || /^\d+$/.test(s)) return ''
  return s
}
