// Análisis EFE y timeline de muestra para el modo demo (espejo de
// backend/analisis/demo.py): permiten desarrollar y probar la sección
// Análisis sin API ni créditos. Regla del proyecto: la simulación vive SOLO en demo.
import type { InventarioLecciones, LeccionItem, BloqueParte, VeredictoParte, EfeBloque, EfeComparativo, EfeEquipo, EquipoParte, EslabonDtpDTO, JugadorParte, ParteCoworkDTO, RamaF, RolF, TimelineData, TlEvento, ZonaF } from '../api/types'

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


/** DTP de muestra (modo demo): misma forma que sirve el backend — el registro
 *  del DTP es el ESLABÓN de la cadena, no el JSON pelado del modelo. */
export function dtpDemo(foco: string, rival: string): EslabonDtpDTO {
  return {
    equipoFoco: foco,
    partidoN: 12,
    rival,
    fecha: '2026-07-02',
    fixtureId: null,
    apertura: {
      m1: {
        sistema: '4-2-3-1 (demo)',
        cambios_vs_anterior: ['Vuelve el lateral titular'],
        roles_reasignados: ['El interior derecho cae a construir'],
        senal_del_xi: 'XI de control con doble pivote',
        vulnerabilidad_propia: 'Espalda de los laterales en transición',
        forma_sin_balon: '4-4-2 en bloque medio',
      },
      m2: {
        choque_sistemas: `4-2-3-1 de ${foco} contra el 3-5-2 de ${rival} (demo)`,
        duelos_carril: [
          { carril: 'izquierda', duelo: 'Lateral vs extremo', mismatch: 'Ventaja en velocidad' },
          { carril: 'centro', duelo: 'Doble pivote vs enganche', mismatch: 'Superioridad numérica' },
        ],
        vida_util_rival: { tipo: 'estructural' as const, minutos: '75-85' },
        vias_gol: { foco: ['Segunda jugada tras córner'], rival: ['Contra por izquierda'] },
        veredicto: 'Equilibrado con leve ventaja del foco',
        razon: 'El doble pivote neutraliza al enganche rival (demo)',
      },
      m3_fases: [
        { tramo: '0-25', plan: 'Bloque medio y salida limpia', palancas: ['Cambiar de banda al tercer pase'] },
        { tramo: '25-65', plan: 'Fijar por dentro para abrir el carril', palancas: ['Interior entre líneas'] },
        { tramo: '65-80+', plan: 'Sostener con frescura por fuera', palancas: ['Extremo de refresco al carril débil'] },
      ],
      m6: { competitivo: true, rotacion: 'Sin rotación relevante (demo)', fatiga: '6 días de descanso',
            ausencias_clave: 'Ninguna', otros: 'modo demo' },
    },
    cierre: {
      m4_goles: [{
        gol: '0-1', minuto: 34, via: 'transicion',
        disparador: 'Pérdida en salida bajo presión (demo)',
        secuencia: 'Recuperación en campo rival y conducción por el carril izquierdo',
        definicion: 'Centro raso al segundo palo',
        responsables_merito: ['Extremo rival'],
        responsables_error: [{ jugador: 'Volante central', nivel: 'principal' as const, detalle: 'Pierde la marca (demo)' }],
        absolucion: 'El portero no tiene responsabilidad en el gol',
      }],
      m5: {
        plan_funciono_hasta_min: 30,
        peligro_real: 'Dos llegadas claras antes del gol (demo)',
        cronologia_giro: 'El gol adelanta al rival y obliga a arriesgar la línea',
        contraste_pronostico: { aciertos: ['El carril izquierdo era la vía'], fallos: ['Se esperaba más control inicial'] },
      },
    },
    registro: {
      pronostico_clave: 'Duelo por izquierda decisivo (demo)',
      que_paso: 'Por ahí llegó el gol',
      veredicto: 'parcial' as const,
      leccion: 'La cobertura del carril débil manda sobre la posesión',
    },
  }
}

/** Parte de Cowork de muestra (espejo de lo que deposita el batch nocturno).
 *  Llega con el bloque F congelado y las dos ramas, que es el estado normal
 *  la noche anterior: ninguna fuente publica el once a esa hora. */
export function parteCoworkDemo(fixtureId: number, equipoA: string, equipoB: string, marcador?: string): ParteCoworkDTO {
  const bloque = (score: number, max: number, peso: number, nota: string, excluido = false, motivo = ''): BloqueParte => ({
    score: excluido ? 0 : score, max, peso,
    ponderado: excluido ? 0 : +(score * peso).toFixed(2), topePonderado: +(max * peso).toFixed(2),
    excluido, motivoExclusion: motivo, nota,
  })
  const jug = (nombre: string, zona: ZonaF, rol: RolF, posicion: string, apps: string): JugadorParte =>
    ({ nombre, zona, rol, posicion, apps, estado: '', motivo: '' })
  const plantel = (p: string): JugadorParte[] => [
    jug(`${p} · Arquero`, 'GK', 'TF', 'Portero', '18/18'),
    jug(`${p} · Arquero suplente`, 'GK', 'SUP', 'Portero', '0/18'),
    jug(`${p} · Lateral derecho`, 'DEF', 'TF', 'Lateral', '16/18'),
    jug(`${p} · Central 1`, 'DEF', 'TF', 'Central', '17/18'),
    jug(`${p} · Central 2`, 'DEF', 'TH', 'Central', '11/18'),
    jug(`${p} · Lateral izquierdo`, 'DEF', 'TH', 'Lateral', '12/18'),
    jug(`${p} · Pivote`, 'MID', 'TF', 'Volante', '17/18'),
    jug(`${p} · Interior`, 'MID', 'TH', 'Volante', '13/18'),
    jug(`${p} · Enganche`, 'MID', 'ROT', 'Mediapunta', '7/18'),
    jug(`${p} · Extremo derecho`, 'ATK', 'TF', 'Extremo', '15/18'),
    jug(`${p} · Extremo izquierdo`, 'ATK', 'ROT', 'Extremo', '8/18'),
    jug(`${p} · Delantero`, 'ATK', 'TF', 'Delantero', '16/18'),
    jug(`${p} · Recambio ofensivo`, 'ATK', 'SUP', 'Delantero', '2/18'),
    jug(`${p} · Recambio de medio`, 'MID', 'SUP', 'Volante', '3/18'),
  ]
  // las ramas se calculan en el backend; en demo se dan ya hechas con los
  // mismos pesos del protocolo (TF ×3, TH ×2, ROT ×1, SUP ×0.5; GK ×1.5)
  const rama = (ip: number, red: Record<ZonaF, number>, supuesto: string, gk = false, ausente = ''): RamaF => ({
    ip, ipNivel: ip <= 3 ? 'verde' : ip <= 7 ? 'ambar' : 'rojo',
    reduccion: red,
    reduccionNivel: { GK: red.GK < 20 ? 'verde' : red.GK <= 40 ? 'ambar' : 'rojo', DEF: red.DEF < 20 ? 'verde' : red.DEF <= 40 ? 'ambar' : 'rojo', MID: red.MID < 20 ? 'verde' : red.MID <= 40 ? 'ambar' : 'rojo', ATK: red.ATK < 20 ? 'verde' : red.ATK <= 40 ? 'ambar' : 'rojo' },
    multiplicadorGk: gk, zonasCriticas: (Object.keys(red) as ZonaF[]).filter((z) => red[z] > 40),
    fuera: [], supuesto, ausenteHipotetico: ausente,
  })
  const equipo = (nombre: string, prefijo: string, scores: [number, number, number, number, number], clas: EquipoParte['clasificacion'], dt: string, meses: number, perfil: EquipoParte['perfil']): EquipoParte => {
    const bloques = {
      A: bloque(scores[0], 4, 1, 'continuidad del cuerpo técnico'),
      B: bloque(scores[1], 6, 1.5, 'núcleo del plantel y banco'),
      C: bloque(scores[2], 4, 1, 'ciclos de las K'),
      D: bloque(scores[3], 4, 1, 'coherencia del sistema'),
      E: bloque(scores[4], 3, 2, 'rendimiento en cancha'),
    }
    const total = +Object.values(bloques).reduce((s, b) => s + b.ponderado, 0).toFixed(2)
    return {
      nombre, bloques, total, maximoAlcanzable: 27,
      porcentaje: +((total / 27) * 100).toFixed(1), clasificacion: clas,
      dt: { nombre: dt, meses }, perfil,
      plantel: plantel(prefijo), fuera: [], factorX: [],
      sensibilidad: [{ supuesto: 'el central 2 no llega', efecto: 'la reducción en DEF pasa a zona debilitada y el matchup deja de ser claro' }],
      disponibilidad: {
        resuelto: false, sinTabla: false, fuente: '',
        nota: 'bloque F congelado: sin once confirmado no se puntúa (Disciplina 35)',
        jugadores: plantel(prefijo),
        ramas: {
          a: rama(0, { GK: 0, DEF: 0, MID: 0, ATK: 0 }, 'juegan todos los disponibles conocidos'),
          b: rama(4.5, { GK: 100, DEF: 0, MID: 0, ATK: 0 }, `además falta ${prefijo} · Arquero`, true, `${prefijo} · Arquero`),
        },
      },
    }
  }
  return {
    fixtureId, estado: 'pendiente_xi', version: 'cowork/1',
    partido: { equipoA, equipoB, fecha: '2026-07-20', equipoAId: 0, equipoBId: 0 },
    equipos: {
      a: equipo(equipoA, 'A', [4, 5, 3, 4, 3], 'FORMADO', 'A. Ruiz (muestra)', 19,
        { sistema: '4-3-3', estilo: 'presión alta y salida limpia', fortaleza: 'juego asociado por dentro', vulnerabilidad: 'espalda de los laterales' }),
      b: equipo(equipoB, 'B', [2, 3, 2, 2, 1], 'EN_FORMACION', 'J. Prieto (interino)', 2,
        { sistema: '5-3-2', estilo: 'bloque bajo y contragolpe', fortaleza: 'orden defensivo', vulnerabilidad: 'generación con la pelota' }),
    },
    alertas: [
      { codigo: 'T.54', equipo: 'b', tipo: 'estructural', detalle: 'DT interino con menos de 6 meses: las K del equipo pierden línea base.' },
      { codigo: 'DEMO', equipo: 'global', tipo: 'fecha', detalle: 'Parte de muestra: el modo demo no habla con Cowork ni con ninguna API.' },
      // un código largo como los que escribe Cowork en producción: la tira de
      // alertas tiene que aguantarlo en teléfono sin aplastar el detalle
      { codigo: 'EL-EFE-VUELVE-A-QUEDAR-CORTO-CONTRA-EL-MOTOR', equipo: 'global', tipo: 'fecha', detalle: 'Cuarta corrida consecutiva con la misma tensión: el bloque A en cero de los dos lados aplana la comparación y el EFE se está calculando sobre dos bloques que no separan mucho.' },
    ],
    matchup: {
      diagnostico: 'FAVORABLE', favorece: 'a',
      razon: 'bloque bajo del rival con vida útil corta contra un ataque que llega por fuera.',
      h2a: 'verde', h2b: 'verde', h2c: 'ambar',
    },
    lecturaSad: {
      moduloOperativo: 'Regresión al Nivel con gap favorable al local; módulo de goles habilitado.',
      unXDos: { texto: 'Local con ventaja estructural; el empate es el escenario de cobertura.', rangoAmpliado: false },
      contextoEmocional: 'El visitante llega de dos derrotas y con el interino sin margen: la presión externa empuja a un planteo conservador.',
      datoEstructural: 'Núcleo del local intacto desde hace tres temporadas; el visitante renovó seis titulares en el último mercado.',
      paradoja: 'El equipo con mejor EFE es el que más depende de un solo hombre: si falta el arquero titular, la ventaja estructural se estrecha.',
      reventon: 'Local: riesgo alto, el visitante entra en la zona donde suele reventar su racha → no apoyar el 1X2 solo en la racha; Visitante: bajo, sin señal.',
    },
    // DTP estructurado (demo): un bloque, con la clase del bloque rival ya
    // calculada como la devuelve el backend al leer
    dtp: {
      bloques: [{
        equipo: 'a',
        apertura: {
          m1: { sistema: '4-3-3', xiReferencia: 'XI de la última fecha', senalXi: 'plan de presión alta', rolesReasignados: ['lateral derecho de central'], vulnerabilidad: 'espalda del lateral reconvertido', formaSinBalon: '4-5-1 medio', minutosCompartidos: 'la pareja de centrales nunca arrancó junta' },
          m2: {
            choqueSistemas: '4-3-3 contra 5-3-2: superioridad por fuera',
            duelosCarril: [{ carril: 'derecha', duelo: 'extremo vs carrilero', mismatch: 'velocidad a la espalda' }],
            checklistBloqueRival: { p1: 'der', p2: 'der', p3: 'der', p4: 'der', p5: 'der', p6: 'izq', casoP6: '', notas: 'vallas invictas sin presión real' },
            viasGol: { foco: ['desborde por derecha', 'pelota parada'], rival: ['transición por el carril del lateral reconvertido'] },
            restDefense: { foco: 'dos centrales y pivote', rival: 'sin seguro tras la pérdida', nivelFoco: 'fijo', nivelRival: 'sin' },
            posesion: { valor: '58%', contraQuien: 'rival que cede el balón', marcador: 'empatado la mayor parte', sede: 'local' },
            veredicto: 'FAVORABLE', razon: 'superioridad por fuera contra un bloque no probado',
          },
          m3Fases: [
            { tramo: '0-25', plan: 'golpear si el rival arranca frío', palancas: ['presión tras pérdida'] },
            { tramo: '25-65', plan: 'cargar el carril derecho', palancas: ['lateral alto', 'pivote de seguro'] },
            { tramo: '65-80+', plan: 'piernas frescas por fuera', palancas: ['córner con dos centrales altos'] },
          ],
          m6: { competitivo: true, rotacion: 'sin rotación', fatiga: 'tres días de descanso', ausencias: 'baja del central titular', otros: '' },
        },
        cierre: {
          sinAnterior: false,
          m4Goles: [{ gol: '0-1', minuto: 17, via: 'pelota_parada', disparador: 'córner', secuencia: 'rechace no atacado', definicion: 'remate de segunda jugada', responsablesMerito: ['el 9 rival'], responsablesError: [{ jugador: 'el 6', nivel: 'principal', detalle: 'no atacó el rechace' }], absolucion: '' }],
          m5: { planFuncionoHastaMin: 60, peligroReal: 'pelota parada', cronologiaGiro: 'el gol del 17 cambió el plan', contraste: { aciertos: ['la vía de pelota parada'], fallos: ['el bloque aguantó menos'] }, preguntaChecklistFallida: 'la 6: el bloque nunca había sido probado' },
          mecanismoAbierto: { activo: false, mecanismo: '', lineaRepite: null, correccionEnVivo: null },
        },
        calculado: { bloqueRival: { clase: 'estructural no probado', vidaUtilMin: '80-90', alertaDegradacion: true, c1Tde: 0.5, equipoDelBloque: 'b', motivo: '5 de 5 insumos del lado estructural, pero la pregunta 6 dice que nunca sostuvo un resultado contra un rival obligado', conteo: { izquierda: 0, derecha: 5, sinDato: 0 }, respuestas: { p1: 'der', p2: 'der', p3: 'der', p4: 'der', p5: 'der', p6: 'izq' } } },
      }],
    },
    // EL ÍNDICE ES POR EQUIPO: caben los dos, y la demo enseña los dos
    tde: {
      bloques: [
        {
          ie: 58, ieNivel: 'ambar', ise: 31, iseNivel: 'verde', equipo: 'b',
          tipologia: 'repliegue por agotamiento', ventana: "75-90'", disciplina43: false,
          vias: [{ nombre: 'echada', indice: 58, ventana: "75-90'", detalle: 'el bloque baja diez metros tras el primer gol en contra' }],
          falsador: "si el visitante mantiene la línea por encima de su área tras el 75', el índice está mal calculado.",
        },
        {
          ie: 24, ieNivel: 'verde', ise: 47, iseNivel: 'ambar', equipo: 'a',
          tipologia: 'sobreexposición por urgencia de resultado', ventana: "60-75'", disciplina43: false,
          vias: [{ nombre: 'sobreexposicion', indice: 47, ventana: "60-75'", detalle: 'adelanta los laterales si el marcador sigue abierto' }],
          falsador: 'si el local conserva los dos laterales por detrás de la línea de balón con el partido empatado, el índice está mal calculado.',
        },
      ],
    },
    timeline: timelineDemo(equipoA, equipoB),
    pronostico: {
      motor: 'gap §5 a favor del local (+0.34)', matriz: '54 / 26 / 20', mercado: '1.80 / 3.50 / 4.40',
      probabilidades: { local: 54, empate: 26, visita: 20 }, marcador: '2-1',
      falsador: 'si el visitante abre el marcador antes del minuto 20, la lectura de bloque bajo queda fallada.',
    },
    documentos: [
      { id: 'ensayo', titulo: 'Cómo puede darse el partido', formato: 'md', cuerpo: '## La lectura\n\nEl local llega con el bloque intacto y el rival con un interino de dos meses. La pregunta no es quién es mejor, sino **cuánto aguanta** el planteo defensivo del visitante.\n\n- Primer tramo: el local acumula por fuera y el visitante se ordena.\n- Entre el 55′ y el 70′ aparece la grieta, cuando el bloque baja diez metros.\n\n> Modo demo: texto de muestra, sin fuentes reales.' },
      { id: 'tde', titulo: 'Teorema del Echado', formato: 'md', cuerpo: '**IE 58** · tipología: repliegue por agotamiento.\n\nVentana de riesgo: **75-90′**. Falsador: si el visitante mantiene la línea por encima de su propio área tras el 75′, el índice está mal calculado.' },
    ],
    pendientes: ['XI de los dos equipos', 'confirmar si el central 2 llega'],
    fuentes: ['demo'],
    notas: 'Parte de muestra del modo demo.',
    xi: { a: {}, b: {} },
    // el caso se cierra 12 h después del partido: sin marcador, sigue abierto
    veredicto: marcador ? veredictoDemo(fixtureId, marcador) : null,
    creadoEn: '2026-07-19T04:10:00Z', actualizadoEn: '2026-07-19T04:10:00Z',
  }
}

/** Veredicto de muestra: el cierre del caso con lo objetivo ya calculado.
 *  En la app real estos números los saca el backend de la ingesta; aquí se
 *  derivan del marcador de la demo para que la banda se pueda ver. */
function veredictoDemo(fixtureId: number, marcador: string): VeredictoParte {
  const [gl, gv] = marcador.split('-').map((x) => parseInt(x.trim(), 10))
  const real = gl > gv ? 'local' : gv > gl ? 'visita' : 'empate'
  const reparto = { local: 54, empate: 26, visita: 20 }
  const brier = +(['local', 'empate', 'visita'] as const)
    .reduce((s2, k) => s2 + ((reparto[k] / 100) - (k === real ? 1 : 0)) ** 2, 0).toFixed(4)
  return {
    fixtureId, seleccion: 'ciega', modoEvaluacion: 'PRE', acredita: true, mancha: '',
    falsador: { texto: 'si el visitante abre el marcador antes del minuto 20, la lectura de bloque bajo queda fallada.', cumplido: false },
    porLado: {
      a: { veredicto: real === 'local' ? 'acierto' : 'fallo',
           queP: real === 'local' ? 'ganó por fuera, como se anticipó' : 'no encontró el camino por fuera',
           leccion: real === 'local' ? '' : 'el bloque bajo entrenado sostiene los 90: no asumir vida útil corta sin dato',
           skill: real === 'local' ? '' : 'diagnostico-tactico', reglaTocada: '' },
      b: { veredicto: real === 'local' ? 'fallo' : 'acierto',
           queP: real === 'local' ? 'no aguantó el tramo final como se le suponía' : 'aguantó el tramo final, como se dijo',
           leccion: real === 'local' ? 'el interino no sostiene el bloque sin el 5 titular' : '',
           skill: real === 'local' ? 'teorema-del-echado' : '', reglaTocada: '' },
    },
    notas: 'Modo demo: veredicto de muestra.',
    cerradoEn: '2026-07-21 09:00:00',
    objetivo: {
      jugado: true,
      marcador: { local: gl, visitante: gv, texto: `${gl}-${gv}`,
                  ganador: real === 'local' ? 'a' : real === 'visita' ? 'b' : 'empate', terminado: true },
      unXDos: { declarado: 'local', real, acerto: real === 'local', probabilidadDeclarada: 54,
                reparto, nota: '' },
      marcadorExacto: { declarado: '2-1', real: `${gl}-${gv}`, acerto: `${gl}-${gv}` === '2-1' },
      brier: { valor: brier, escala: '0 perfecto · 2 máximo · tres resultados (NO comparable con un Brier binario)' },
      tde: { bloques: [
        { ventana: "75-90'", desde: 75, hasta: 90, equipo: 'b', comprobable: true,
          golEnVentana: false, goles: [], nota: '' },
        { ventana: "60-75'", desde: 60, hasta: 75, equipo: 'a', comprobable: true,
          golEnVentana: gl + gv >= 2, goles: [], nota: '' },
      ] },
      evidencia: {
        goles: [
          { minuto: 23, lado: 'a' as const, jugador: 'Jugador de muestra', autogol: false },
          { minuto: 58, lado: 'b' as const, jugador: 'Jugador de muestra', autogol: false },
          { minuto: 71, lado: 'a' as const, jugador: 'Jugador de muestra', autogol: false },
        ].slice(0, gl + gv),
        primerGol: { minuto: 23, lado: 'a' as const, jugador: 'Jugador de muestra' },
        conFicha: true, nota: '',
      },
      // el reventón, comprobado: la burbuja de cada lado antes del partido y si
      // este partido la cerró (observación, no veredicto)
      reventon: {
        nota: 'declarado = la burbuja total con la historia anterior al partido; observado = si la K de ESTE partido cerró la burbuja. Es observación, no veredicto',
        a: { comprobable: true, sinBurbuja: false,
             declarado: { signo: '+', k: 14.2, partidos: 4, riesgo: { nivel: 'alto', puntos: 5 }, rivalTramo: 'fuerte', extremo: false },
             observado: real === 'local' ? { revento: false, kDespues: 18.9, signoDespues: '+', kPico: null, partidos: 5 }
               : { revento: true, kDespues: real === 'empate' ? 0 : -2.4, signoDespues: real === 'empate' ? '0' : '-', kPico: 14.2, partidos: 4 },
             nota: real === 'local' ? 'siguió: la burbuja + llega a 5 partidos (K +18.90)' : 'reventó: la burbuja + de 4 partidos (K +14.20) cerró con este partido' },
        b: { comprobable: false, sinBurbuja: true, declarado: null, observado: null,
             nota: 'sin burbuja abierta antes del partido: no había nada que reventar' },
      },
    },
  }
}

/** Inventario de lecciones de muestra (fase C de docs/APRENDIZAJE.md).
 *
 *  Espejo de `backend/analisis/lecciones.py`: la demo trae a propósito un caso
 *  ciego y uno contaminado, para que se vea en pantalla la distinción que el
 *  dossier no puede dejar al criterio del día — solo lo acreditable puede mover
 *  un número; lo demás fija rúbrica. */
export function leccionesDemo(skill: string, estado: string, cohorte = ''): InventarioLecciones {
  const base = (x: Partial<LeccionItem> & { clave: string }): LeccionItem => ({
    fixtureId: 9001, lado: 'b', equipo: 'Villarreal', rival: 'Atlético',
    partido: 'Atlético vs Villarreal', fecha: '2026-07-20',
    skill: 'teorema-del-echado', veredicto: 'fallo', queP: '', leccion: '',
    reglaTocada: '', seleccion: 'ciega', modoEvaluacion: 'PRE', acredita: true,
    mancha: '', puedeMoverNumeros: true,
    queAutoriza: 'puede sostener un cambio de peso',
    estado: 'pendiente', aplicadaEn: '', nota: '', actualizadoEn: '2026-07-21 09:00:00',
    ...x,
  })
  const items: LeccionItem[] = [
    base({
      clave: '9001:b', queP: 'no aguantó el tramo final como se le suponía',
      leccion: 'el interino no sostiene el bloque sin el 5 titular: F2 no puede ir en 0.5 con el mediocentro fuera',
      reglaTocada: 'bloque F · indicador F2',
    }),
    base({
      clave: '9002:a', fixtureId: 9002, lado: 'a', equipo: 'Real Madrid', rival: 'Barcelona',
      partido: 'Real Madrid vs Barcelona', fecha: '2026-07-19', veredicto: 'parcial',
      queP: 'ganó por fuera pero sufrió el tramo final',
      leccion: 'la ventana declarada empezó diez minutos tarde: con dos cambios ofensivos antes del 65 el tramo se adelanta',
      reglaTocada: 'ventana de 15 minutos',
      seleccion: 'post_resultado', acredita: false, puedeMoverNumeros: false,
      queAutoriza: 'solo fija rúbrica: aclara cómo se aplica una regla, no mueve ningún número',
    }),
    base({
      clave: '9003:a', fixtureId: 9003, lado: 'a', equipo: 'Liverpool', rival: 'Chelsea',
      partido: 'Liverpool vs Chelsea', fecha: '2026-07-12', skill: 'efe-clasificador',
      veredicto: 'fallo', queP: 'el EFE lo daba formado y se desarmó en 20 minutos',
      leccion: 'tres titulares con menos de seis meses juntos no es "núcleo intacto" aunque el DT lleve dos años',
      reglaTocada: 'bloque B · minutos compartidos', estado: 'aplicada', aplicadaEn: 'efe/v1.5',
    }),
  ]
  const filtrados = items.filter((i) => (!skill || i.skill === skill) && (!estado || i.estado === estado))
  const porSkill = [...new Set(items.map((i) => i.skill))].sort().map((nombre) => {
    const suyas = items.filter((i) => i.skill === nombre)
    const pend = suyas.filter((i) => i.veredicto === 'fallo' && i.estado === 'pendiente').length
    return {
      skill: nombre,
      lecciones: Object.fromEntries(['pendiente', 'en_revision', 'aplicada', 'descartada']
        .map((e) => [e, suyas.filter((i) => i.estado === e).length])),
      atribuidos: Object.fromEntries(['acierto', 'parcial', 'fallo']
        .map((v) => [v, suyas.filter((i) => i.veredicto === v).length])),
      sesgoDeAtribucion: 'quien cierra el caso nombra el skill sobre todo cuando algo falla: estos conteos NO son una tasa de acierto del skill',
      acreditables: suyas.filter((i) => i.puedeMoverNumeros).length,
      soloRubrica: suyas.filter((i) => !i.puedeMoverNumeros).length,
      revisionAbierta: pend >= 4,
      fallosPendientes: pend,
      faltanParaDisparar: Math.max(0, 4 - pend),
      disparador: '4 fallos con lección pendiente del mismo skill ABREN la revisión; no autorizan ningún cambio',
      liston: nombre === 'teorema-del-echado'
        ? {
          de: 'el skill teorema-del-echado (ALTA_DEL_SEMAFORO)',
          condiciones: { a: 'N ≥ 5 echadas observadas con selección ciega en el esquema vigente' },
          observadoAca: '1 ventana con gol de 2 comprobadas en población ciega',
          semaforo: '1 echada(s) observada(s) en ciego · el skill pide 5',
          cumple: false,
          nota: 'modo demo: números de muestra',
        }
        : null,
      items: filtrados.filter((i) => i.skill === nombre),
    }
  })
  return {
    generadoEn: '2026-07-21 09:05:00',
    filtro: { skill, estado, cohorte },
    cohortes: [
      { clave: 'rodaje', vigente: false, descripcion: 'partes anteriores al 19/09/2026: DT viejo, TDE sin nivel. Enseñan, no calibran', casos: 1, enCuarentena: 1 },
      { clave: 'c3-2026-09-23', vigente: true, descripcion: 'desde el 23/09/2026: DT de la alineación solo si es reciente, cuarentena automática si el DT del parte no es el del banco', casos: 3, enCuarentena: 0 },
    ],
    cohorteVigente: 'c3-2026-09-23',
    notaCohortes: 'la cohorte se sella al depositar y no cambia con un re-depósito; las métricas de arriba son SOLO de la cohorte elegida (vacío = todas)',
    enCuarentena: {
      cuantas: 1,
      automaticas: 0,
      porque: 'casos apartados por criterio (qué le faltaba al parte antes del pitazo), nunca por resultado: no cuentan ni fijan rúbrica',
      items: [base({ clave: '8990:a', fixtureId: 8990, lado: 'a', equipo: 'Girona', rival: 'Sevilla', partido: 'Girona vs Sevilla', fecha: '2026-07-12', veredicto: 'fallo', leccion: 'rodaje: DT viejo en la ficha', cohorte: 'rodaje', cuarentena: 'rodaje: DT viejo en 17 de 22 equipos', puedeMoverNumeros: false, queAutoriza: 'en cuarentena: no cuenta ni fija rúbrica' })],
    },
    poblacion: {
      ciega: { casos: 2, lados: 3 },
      por_resultado: { casos: 0, lados: 0 },
      post_resultado: { casos: 1, lados: 1 },
      cuarentena: { casos: 1, lados: 1 },
      nota: 'las poblaciones no se suman entre sí: solo `ciega` + `PRE` acredita, las demás fijan rúbrica; `cuarentena` no cuenta en nada',
    },
    acreditables: {
      criterio: 'ciega + PRE: la única combinación que acredita validación predictiva',
      casos: 2, lados: 3,
      veredictos: { acierto: 1, parcial: 0, fallo: 2 },
      tasaAcierto: 0.333, tasaNota: '',
      unXDos: { aciertos: 1, de: 2, tasa: 0.5 },
      brier: {
        media: 0.4712, n: 2, lineaBase: 0.4444, mejorQueLaBase: false,
        nota: 'la línea de base es el reparto constante con la frecuencia observada de esta misma muestra: lo que sacaría quien no mira el partido',
        escala: '0 perfecto · 2 máximo · TRES resultados (no comparable con un Brier binario)',
      },
      ventanaTde: {
        observadas: 2, conGol: 1, sinFicha: 0,
        nota: 'ventanas del TDE comprobadas contra los goles recibidos, en población ciega. `sinFicha` no cuenta como no ocurrido: no se pudo comprobar',
      },
      reventon: {
        observadas: 3, reventadas: 2, tasa: 0.667, tasaBaseBacktest: 0.6,
        porNivel: {
          'bajo': { observadas: 0, reventadas: 0, tasa: null, intervalo: null, esperadoBacktest: [0.421, 0.473], dentroDelBacktest: null, lectura: 'sin n', nMinimo: 10 },
          'medio': { observadas: 1, reventadas: 0, tasa: 0, intervalo: [0, 0.793], esperadoBacktest: [0.608, 0.608], dentroDelBacktest: null, lectura: 'sin n', nMinimo: 10 },
          'alto': { observadas: 2, reventadas: 2, tasa: 1, intervalo: [0.342, 1], esperadoBacktest: [0.672, 0.692], dentroDelBacktest: null, lectura: 'sin n', nMinimo: 10 },
          'muy alto': { observadas: 0, reventadas: 0, tasa: null, intervalo: null, esperadoBacktest: [0.747, 0.854], dentroDelBacktest: null, lectura: 'sin n', nMinimo: 10 },
          'sin base': { observadas: 0, reventadas: 0, tasa: null, intervalo: null, esperadoBacktest: null, dentroDelBacktest: null, lectura: 'sin n', nMinimo: 10 },
        },
        extremo: { observadas: 1, reventadas: 1, nota: 'burbujas con alerta K-EXTREMO declarada antes del partido: el backtest dice que la K no adelanta el reventón; esto lo mira en producción' },
        sinBurbuja: 1, noComprobables: 0, fueraDelBacktest: [], revisionAbierta: false,
        nota: 'por lado, en población ciega: la burbuja total tal como estaba antes del partido y si ese partido la reventó. La tasa por nivel se compara con la del backtest (docs/REVENTON.md §8) solo con n ≥ 10; un nivel fuera del rango ABRE la revisión de los puntos, no los mueve',
      },
    },
    porSkill,
    sinSkill: { cuantas: 0, porque: 'la lección no declaró de qué skill es: no se reparte a ojo', items: [] },
    estados: ['pendiente', 'en_revision', 'aplicada', 'descartada'],
    items: filtrados,
  }
}
