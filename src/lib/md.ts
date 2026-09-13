// Markdown mínimo para los documentos del parte de Cowork.
//
// Por qué a mano y no una librería: la app no tiene dependencias de runtime
// más allá de React, y lo que hay que pintar es lo que un analista escribe —
// títulos, listas, negritas, citas y alguna tabla. Un parser de 120 líneas que
// entendemos entero es preferible a arrastrar una dependencia (y su superficie
// de HTML inyectado) por cuatro marcas.
//
// Devuelve DATOS, no JSX: quien pinta decide los estilos del tema.

export type MdInline =
  | { t: 'txt'; v: string }
  | { t: 'b'; v: string }
  | { t: 'i'; v: string }
  | { t: 'code'; v: string }

export type MdBloque =
  | { tipo: 'h'; nivel: 1 | 2 | 3; hijos: MdInline[] }
  | { tipo: 'p'; hijos: MdInline[] }
  | { tipo: 'lista'; ordenada: boolean; items: MdInline[][] }
  | { tipo: 'cita'; hijos: MdInline[] }
  | { tipo: 'codigo'; texto: string }
  | { tipo: 'tabla'; cabecera: string[]; filas: string[][] }
  | { tipo: 'regla' }

/** `**negrita**`, `*cursiva*`, `` `código` `` — en un solo barrido. */
export function parsearInline(texto: string): MdInline[] {
  const out: MdInline[] = []
  const re = /(\*\*[^*]+\*\*|__[^_]+__|\*[^*\n]+\*|`[^`]+`)/g
  let ultimo = 0
  let m: RegExpExecArray | null
  while ((m = re.exec(texto)) !== null) {
    if (m.index > ultimo) out.push({ t: 'txt', v: texto.slice(ultimo, m.index) })
    const trozo = m[0]
    if (trozo.startsWith('**') || trozo.startsWith('__')) out.push({ t: 'b', v: trozo.slice(2, -2) })
    else if (trozo.startsWith('`')) out.push({ t: 'code', v: trozo.slice(1, -1) })
    else out.push({ t: 'i', v: trozo.slice(1, -1) })
    ultimo = m.index + trozo.length
  }
  if (ultimo < texto.length) out.push({ t: 'txt', v: texto.slice(ultimo) })
  return out.length ? out : [{ t: 'txt', v: texto }]
}

const esFilaTabla = (l: string) => l.trim().startsWith('|') && l.trim().endsWith('|')
const celdas = (l: string) => l.trim().slice(1, -1).split('|').map((c) => c.trim())

export function parsearMd(texto: string): MdBloque[] {
  const lineas = (texto || '').replace(/\r\n/g, '\n').split('\n')
  const out: MdBloque[] = []
  let parrafo: string[] = []

  const cerrarParrafo = () => {
    if (!parrafo.length) return
    out.push({ tipo: 'p', hijos: parsearInline(parrafo.join(' ').trim()) })
    parrafo = []
  }

  for (let i = 0; i < lineas.length; i++) {
    const linea = lineas[i]
    const limpia = linea.trim()

    if (!limpia) { cerrarParrafo(); continue }

    if (limpia.startsWith('```')) {
      cerrarParrafo()
      const cuerpo: string[] = []
      i++
      while (i < lineas.length && !lineas[i].trim().startsWith('```')) cuerpo.push(lineas[i++])
      out.push({ tipo: 'codigo', texto: cuerpo.join('\n') })
      continue
    }

    if (/^(-{3,}|\*{3,}|_{3,})$/.test(limpia)) { cerrarParrafo(); out.push({ tipo: 'regla' }); continue }

    const h = /^(#{1,6})\s+(.*)$/.exec(limpia)
    if (h) {
      cerrarParrafo()
      out.push({ tipo: 'h', nivel: Math.min(3, h[1].length) as 1 | 2 | 3, hijos: parsearInline(h[2]) })
      continue
    }

    if (limpia.startsWith('>')) {
      cerrarParrafo()
      const cita: string[] = []
      while (i < lineas.length && lineas[i].trim().startsWith('>')) cita.push(lineas[i++].trim().replace(/^>\s?/, ''))
      i--
      out.push({ tipo: 'cita', hijos: parsearInline(cita.join(' ')) })
      continue
    }

    // tabla: cabecera + separador |---|---| + filas
    if (esFilaTabla(limpia) && i + 1 < lineas.length && /^\|[\s:|-]+\|$/.test(lineas[i + 1].trim())) {
      cerrarParrafo()
      const cabecera = celdas(limpia)
      const filas: string[][] = []
      i += 2
      while (i < lineas.length && esFilaTabla(lineas[i])) filas.push(celdas(lineas[i++]))
      i--
      out.push({ tipo: 'tabla', cabecera, filas })
      continue
    }

    const vinieta = /^[-*+]\s+(.*)$/.exec(limpia)
    const numerada = /^\d+[.)]\s+(.*)$/.exec(limpia)
    if (vinieta || numerada) {
      cerrarParrafo()
      const ordenada = !!numerada
      const items: MdInline[][] = []
      while (i < lineas.length) {
        const l = lineas[i].trim()
        const v = /^[-*+]\s+(.*)$/.exec(l)
        const n = /^\d+[.)]\s+(.*)$/.exec(l)
        if ((ordenada && !n) || (!ordenada && !v)) break
        items.push(parsearInline((n ? n[1] : v![1])))
        i++
      }
      i--
      out.push({ tipo: 'lista', ordenada, items })
      continue
    }

    parrafo.push(limpia)
  }
  cerrarParrafo()
  return out
}
