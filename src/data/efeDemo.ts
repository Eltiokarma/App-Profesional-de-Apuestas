// Análisis EFE y timeline de muestra para el modo demo (espejo de
// backend/analisis/demo.py): permiten desarrollar y probar la sección
// Análisis sin API ni créditos. Regla del proyecto: la simulación vive SOLO en demo.
import type { EfeBloque, EfeComparativo, EfeEquipo, TimelineData, TlEvento } from '../api/types'

export function timelineDemo(equipoA: string, equipoB: string): TimelineData {
  const ev = (fecha: string, equipo: string, tipo: TlEvento['tipo'], titulo: string, detalle: string, marcador = '', jornada = 0, destacado = false): TlEvento => ({
    fecha, aproximada: false, equipo, tipo, titulo, detalle, jornada, marcador, destacado, alerta_relacionada: '', fuente: 'demo',
  })
  return {
    titulo: `${equipoA} vs ${equipoB} — Feb-Jul 2026`,
    periodo: { desde: '2026-02-01', hasta: '2026-07-14' },
    equipos: [
      { nombre: equipoA, lado: 'izquierda', color: '#5B8DEF', color_secundario: '#C7D0EC', stats: { posicion: 2, puntos: 38, ultima_victoria: '2026-07-06 2-0', otros: [] } },
      { nombre: equipoB, lado: 'derecha', color: '#E5484D', color_secundario: '#F2C1C3', stats: { posicion: 7, puntos: 27, ultima_victoria: '2026-06-21 1-0', otros: [] } },
    ],
    eventos: [
      ev('2026-02-09', equipoA, 'resultado', 'Victoria 2-0 en el debut', 'Arranque sólido con doblete del 9.', '2-0', 1),
      ev('2026-03-02', equipoB, 'tecnico', 'Cambio de DT', 'Sale el técnico tras 4 fechas sin ganar; asume el interino.', '', 0, true),
      ev('2026-04-12', 'ambos', 'resultado', 'Clásico 1-1', "Enfrentamiento directo parejo, con expulsión al 80'.", '1-1', 9),
      ev('2026-05-17', equipoB, 'derrota', 'Caída 0-3 como local', 'Peor derrota del semestre; crisis en la interna.', '0-3', 14),
      ev('2026-06-28', equipoA, 'hito', 'Clasificación a la final', 'Cierra la fase como líder e instala la final del Apertura.', '', 0, true),
    ],
    agrupacion: 'mes',
    narrativa: `${equipoA} llega en curva ascendente y con final asegurada; ${equipoB} cambió de DT a mitad del semestre y alterna resultados. El precedente directo del período terminó igualado.`,
    datos_faltantes: [],
    fuentes: ['demo'],
  }
}

function bloque(score: number, max: number, inds: [string, 'verde' | 'ambar' | 'rojo', string][], ponderado?: number, ppp = 0): EfeBloque {
  return {
    score, max, ponderado: ponderado ?? score, excluido: false, motivo_exclusion: '', d3_cap_aplicado: false, ppp,
    indicadores: inds.map(([id, estado, justificacion]) => ({ id, estado, justificacion, fuente: 'demo' })),
  }
}

function equipo(nombre: string, color: string, porcentaje: number, clasificacion: EfeEquipo['clasificacion']): EfeEquipo {
  return {
    color, color_light: color + '33', color_mid: color + '88',
    bloques: {
      A: bloque(3, 4, [
        ['A1', 'verde', `DT de ${nombre} cumple 14 meses en el cargo`],
        ['A2', 'verde', 'Cero cambios de DT en 12 meses'],
        ['A3', 'ambar', 'Contrato con 5 meses restantes'],
      ]),
      B: bloque(4.5, 6, [
        ['B1', 'verde', '78% de titulares con ≥9 meses en el club'],
        ['B5', 'verde', 'Dos suplentes con goles entrando desde el banco'],
        ['B6', 'ambar', 'GK nuevo con 22 partidos en la categoría'],
      ], 6.75),
      C: bloque(3, 4, [['C1', 'verde', 'Ciclos limpios en las K, sin picos anómalos']]),
      D: bloque(3, 4, [['D3', 'ambar', 'Respuesta parcial a rachas negativas']]),
      E: bloque(2, 3, [['E2', 'ambar', '1.55 puntos por partido en la temporada']], 4, 1.55),
    },
    total: 21.25, maximo_alcanzable: 27, porcentaje, clasificacion,
    disponibilidad: {
      jugadores: [
        { nombre: 'Portero Uno', posicion: 'GK', zona: 'GK', rol: 'TF', apps: '11/12', estado: 'disponible', motivo: '' },
        { nombre: 'Central Dos', posicion: 'DFC', zona: 'DEF', rol: 'TF', apps: '12/12', estado: 'disponible', motivo: '' },
        { nombre: 'Volante Cinco', posicion: 'MCD', zona: 'MID', rol: 'TH', apps: '8/12', estado: 'baja', motivo: 'Sanción (acumulación)' },
        { nombre: 'Delantero Diez', posicion: 'DC', zona: 'ATK', rol: 'TF', apps: '10/12', estado: 'duda', motivo: 'Sobrecarga muscular' },
      ],
      ip: 3.5, ip_nivel: 'ambar', multiplicador_gk_aplicado: false,
      reduccion_zonas: { GK: 0, DEF: 0, MID: 33, ATK: 25 },
      f4: { rotados: 1, diagnostico: 'Rotación puntual sin caída de nivel — refuerza B5' },
      f5_factor_x: [{ nombre: 'Juvenil Once', contexto: 'Fichaje reciente sin minutos, goleador en su club anterior' }],
    },
    dt: { nombre: `DT de ${nombre}`, asuncion: '2025-05-01', meses: 14 },
    calendario: [
      { rival: 'Rival Uno', fecha: '2026-07-20', condicion: 'L', etiquetas: ['🏠 LOCAL FUERTE'], posicion: 4, nota: '' },
      { rival: 'Rival Dos', fecha: '2026-07-27', condicion: 'V', etiquetas: ['⚔️ CLÁSICO'], posicion: 2, nota: 'Derby regional' },
      { rival: 'Rival Tres', fecha: '2026-08-03', condicion: 'L', etiquetas: [], posicion: 11, nota: '' },
      { rival: 'Rival Cuatro', fecha: '2026-08-10', condicion: 'V', etiquetas: ['🆕 RECIÉN ASCENDIDO'], posicion: 16, nota: '' },
    ],
  }
}

export function efeDemo(equipoA: string, equipoB: string, torneo: string | null, fecha: string | null): EfeComparativo {
  return {
    version_efe: '1.5',
    partido: {
      equipo_a: equipoA, equipo_b: equipoB, torneo: torneo ?? '', fase: '', estadio: '',
      fecha: fecha ?? '', hora: '', condicion: { a: 'L', b: 'V' },
    },
    equipos: {
      a: equipo(equipoA, '#5B8DEF', 79, 'FORMADO'),
      b: equipo(equipoB, '#E5484D', 58, 'EN_FORMACION'),
    },
    matchup_h: {
      perfil_a: { sistema: '4-3-3', estilo: 'posesión con presión alta', fortaleza: 'juego aéreo', vulnerabilidad: 'espaldas de los laterales' },
      perfil_b: { sistema: '5-3-2', estilo: 'bloque bajo y contraataque', fortaleza: 'solidez defensiva', vulnerabilidad: 'centrales lentos en centros' },
      h2a: 'verde', h2b: 'ambar', h2c: 'verde',
      diagnostico: 'FAVORABLE',
      razon: 'El juego aéreo del local explota la debilidad del bloque bajo visitante en centros',
    },
    alertas: [
      { codigo: 'G-BLOQUE', tipo: 'fecha', equipo: 'b', detalle: 'Bloque bajo con vida útil táctica de 55-65 minutos: si el local no convierte en el 1er tiempo, la probabilidad de gol sube en el tramo 60-80\'' },
      { codigo: 'FACTOR-X', tipo: 'fecha', equipo: 'a', detalle: 'Juvenil Once no está reflejado en las K históricas: ampliar rango de confianza ±10%, no mover el centro' },
    ],
    lectura_sad: {
      modulo_operativo: 'Módulos de goles por franja 60-80\' especialmente relevantes por G-BLOQUE',
      un_x_dos: { texto: 'Ligero favoritismo local; el empate al descanso no invalida la ventaja, la posterga', rango_ampliado: true },
      contexto_emocional: 'Sin carga emocional extra: partido de liga estándar',
      dato_estructural: 'El local absorbe rotaciones sin caída de nivel (F4 refuerza B5)',
      paradoja: '',
    },
    datos_faltantes: ['xi_confirmado_a', 'xi_confirmado_b'],
    fuentes: ['demo'],
  }
}
