// Espejo TS de backend/analisis/familias.py (+ perfil_dc de backend/backtest_familias.py):
// las OTRAS burbujas —doble oportunidad, márgenes y goles— contadas para la
// narrativa. Los dos lados corren sobre scripts/casos_familias.json (vectores
// dorados generados por el Python): un texto que cambia en un lado sin el
// otro tumba `npm run test:familias`. Descripción, no riesgo (REVENTON §15);
// el perfil de doble oportunidad por condición sí agrega al 1X2 (§15.1).

import type { BurbujaFamiliaDTO, FilaFamilia, OtrasFamiliasDTO, PerfilDcDTO } from '../api/types'

const MIN_RACHAS_RECORD = 3
const DESTACADA_DESDE = 3
const CUIDADO_DESDE = 5
// ...y rara para ese equipo (usuario, 24/10/2026): probRacha < 5 % (ver familias.py)
const IMPROBABLE_BAJO = 0.05
const AMBITO: Record<string, string> = { local: 'de local', visita: 'de visita', total: 'en total' }

const FAMILIAS: Record<string, (gf: number, gc: number) => boolean> = {
  noPierde: (gf, gc) => gf >= gc,
  noGana: (gf, gc) => gf <= gc,
  'gana2+': (gf, gc) => gf - gc >= 2,
  'gana3+': (gf, gc) => gf - gc >= 3,
  'pierde2+': (gf, gc) => gc - gf >= 2,
  anota: (gf) => gf >= 1,
  recibe: (_gf, gc) => gc >= 1,
  ambosMarcan: (gf, gc) => gf >= 1 && gc >= 1,
  'mas2.5': (gf, gc) => gf + gc >= 3,
}

const NARRADAS: [string, string, string][] = [
  // el NO de estas dos es el resultado: «perdiendo» se leía al revés (incidencia 578)
  ['noPierde', 'sin perder', 'con derrota'],
  ['noGana', 'sin ganar', 'con victoria'],
  ['gana2+', 'ganando por 2 o más', 'sin ganar por 2 o más'],
  ['gana3+', 'ganando por 3 o más', 'sin ganar por 3 o más'],
  ['pierde2+', 'perdiendo por 2 o más', 'sin perder por 2 o más'],
  ['anota', 'anotando', 'sin anotar'],
  ['recibe', 'recibiendo gol', 'con la valla invicta'],
  ['ambosMarcan', 'con goles de los dos', 'sin que marquen los dos'],
  ['mas2.5', 'con más de 2,5 goles', 'con 2 goles o menos'],
]

/** Igual que `redondear` del Python: hacia arriba en el .5. */
export function redondear(x: number, decimales = 0): number {
  const f = 10 ** decimales
  return Math.floor(x * f + 0.5) / f
}

function validas(filas: FilaFamilia[]): FilaFamilia[] {
  return filas
    .filter((f) => f.golesFavor != null && f.golesContra != null)
    .sort((a, b) => (String(a.fecha ?? '') < String(b.fecha ?? '') ? -1 : String(a.fecha ?? '') > String(b.fecha ?? '') ? 1 : 0))
}

function recorrer(serie: boolean[]) {
  let largo = 0
  const maximos = { true: 0, false: 0 } as Record<string, number>
  const cortadas = { true: 0, false: 0 } as Record<string, number>
  serie.forEach((x, t) => {
    if (t > 0 && x !== serie[t - 1]) {
      const prev = String(serie[t - 1])
      maximos[prev] = Math.max(maximos[prev], largo)
      cortadas[prev] += 1
      largo = 1
    } else {
      largo += 1
    }
  })
  return { largo, maximos, cortadas }
}

export function perfilDc(prefijo: FilaFamilia[], localHoy: boolean): Omit<PerfilDcDTO, 'texto'> {
  const cond = localHoy ? 'Local' : 'Visita'
  const sub = validas(prefijo).filter((f) => f.condicion === cond)
  const n = sub.length
  const serie = sub.map((f) => Number(f.golesFavor) >= Number(f.golesContra))
  const np = serie.filter(Boolean).length
  const ng = sub.filter((f) => Number(f.golesFavor) <= Number(f.golesContra)).length
  const { largo, maximos, cortadas } = recorrer(serie)
  const v = serie.length ? serie[serie.length - 1] : null
  let rec = 0
  if (v !== null && cortadas[String(v)] >= MIN_RACHAS_RECORD) {
    const m = maximos[String(v)]
    rec = largo > m ? 2 : largo === m ? 1 : 0
  }
  return {
    condicion: cond, partidos: n,
    noPierde: redondear((np + 1) / (n + 2), 4), noGana: redondear((ng + 1) / (n + 2), 4),
    burbuja: v === null ? 0 : v ? largo : -largo,
    maximoPrevio: v === null ? 0 : maximos[String(v)],
    record: rec,
  }
}

function burbuja(filas: FilaFamilia[], clave: string) {
  const pred = FAMILIAS[clave]
  const serie = filas.map((f) => pred(Number(f.golesFavor), Number(f.golesContra)))
  if (!serie.length) return null
  const { largo, maximos, cortadas } = recorrer(serie)
  const v = serie[serie.length - 1]
  const k = String(v)
  let record: BurbujaFamiliaDTO['record'] = null
  if (cortadas[k] >= MIN_RACHAS_RECORD) record = largo > maximos[k] ? 'supera' : largo === maximos[k] ? 'iguala' : 'no'
  const frecuencia = redondear(serie.filter(Boolean).length / serie.length, 3)
  const probRacha = redondear((v ? frecuencia : 1 - frecuencia) ** largo, 4)
  return {
    valor: v, partidos: largo, maximoPrevio: cortadas[k] ? maximos[k] : null, burbujasPrevias: cortadas[k], record,
    frecuencia, n: serie.length, probRacha, improbable: probRacha < IMPROBABLE_BAJO,
  }
}

function esCuidado(b: { record: BurbujaFamiliaDTO['record']; partidos: number; improbable: boolean }): boolean {
  return (b.record === 'supera' || b.record === 'iguala') && b.partidos >= CUIDADO_DESDE && b.improbable
}

function pct(p: number): string {
  const x = redondear(p * 100)
  return x >= 1 ? `${x} %` : 'menos del 1 %'
}

function texto(nombre: string, ambito: string, b: NonNullable<ReturnType<typeof burbuja>>, si: string, no: string): string {
  let t = `${nombre} lleva ${b.partidos} ${b.partidos === 1 ? 'partido' : 'partidos'} ${AMBITO[ambito]} ${b.valor ? si : no}`
  if (b.maximoPrevio !== null) t += ` (su máximo previo era ${b.maximoPrevio})`
  if (b.record === 'supera' || b.record === 'iguala') {
    t += b.record === 'supera' ? ': está en terreno nuevo, por encima de su récord' : ': iguala su récord'
    if (esCuidado(b))
      t += ' — CUIDADO con cargar a que siga: no hay precedente. El backtest no dice que se corte más ' +
        '(§15), así que si se corta hay una causa que buscar'
    else if (b.partidos >= CUIDADO_DESDE)
      t += ` — pero con su frecuencia una racha así es esperable (sale el ${pct(b.probRacha)} de las ` +
        'veces): no es terreno raro'
  }
  // la frecuencia del ESTADO en que está hoy, para que la línea no se contradiga
  const frec = b.valor ? b.frecuencia : 1 - b.frecuencia
  t += `. En ${b.n} partidos ${AMBITO[ambito]} va ${b.valor ? si : no} el ${redondear(frec * 100)} %.`
  return t
}

export function describirFamilias(filasIn: FilaFamilia[], condicion: 'L' | 'V' | null | undefined, nombre = 'El equipo'): OtrasFamiliasDTO {
  const filas = validas(filasIn)
  const cond = condicion === 'L' ? 'local' : condicion === 'V' ? 'visita' : null
  const ambitos: ('total' | 'local' | 'visita')[] = cond ? [cond, 'total'] : ['total']
  const out: OtrasFamiliasDTO = {
    nota: 'descripción, no riesgo: el largo y el récord de estas burbujas no predicen el partido ' +
      'siguiente mejor que la frecuencia del equipo, y en su récord se sostienen algo más, no ' +
      'revientan (REVENTON §15). El PERFIL de doble oportunidad por condición sí agrega al 1X2 ' +
      'del motor (§15.1)',
    condicion: cond, familias: [], lineas: [],
  }
  if (cond) {
    const p = perfilDc(filas, condicion === 'L')
    if (p.partidos) {
      // el texto cuenta lo observado; noPierde/noGana van suavizados para el modelo (§15.1)
      const sub = filas.filter((f) => f.condicion === p.condicion)
      const nNp = sub.filter((f) => Number(f.golesFavor) >= Number(f.golesContra)).length
      const nNg = sub.filter((f) => Number(f.golesFavor) <= Number(f.golesContra)).length
      const n = p.partidos
      const t = `Perfil de doble oportunidad ${AMBITO[cond]}: no pierde ${nNp} de ${n} ` +
        `(${redondear((nNp / n) * 100)} %) y no gana ${nNg} de ${n} (${redondear((nNg / n) * 100)} %). Este perfil SÍ agrega al 1X2 del motor (REVENTON §15.1): un equipo que ` +
        `${AMBITO[cond]} empata mucho o se planta a no perder no está del todo en el nivel`
      out.perfilDc = { ...p, texto: t }
      out.lineas.push(t)
    }
  }
  for (const ambito of ambitos) {
    const sub = ambito === 'total' ? filas : filas.filter((f) => f.condicion === (ambito === 'local' ? 'Local' : 'Visita'))
    for (const [clave, si, no] of NARRADAS) {
      const b = burbuja(sub, clave)
      if (!b) continue
      const t = texto(nombre, ambito, b, si, no)
      const destacada = b.partidos >= DESTACADA_DESDE || b.record === 'supera' || b.record === 'iguala'
      out.familias.push({ familia: clave, ambito, ...b, destacada, cuidado: esCuidado(b), texto: t })
      if (destacada) out.lineas.push(t)
    }
  }
  return out
}
