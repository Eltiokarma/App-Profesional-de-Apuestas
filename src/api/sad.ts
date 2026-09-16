// Endpoints del backend SAD (contrato: docs/openapi.yaml).
import type { BurbujasEquipoDTO } from './types'
import { apiGet, apiPost, qs } from './client'
import type {
  AgendaCoworkDTO,
  AnalisisPrepartidoDTO,
  AnalisisRegistroDTO,
  CargaDespensaDTO,
  CargaDespensaResultadoDTO,
  ConstanteCuotaDTO,
  ConstantesDTO,
  CuotaCasaDTO,
  CuotaDTO,
  CuotaSnapshotDTO,
  EquipoDTO,
  EquipoStatsDTO,
  EstadoFixture,
  FichaPartidoDTO,
  FixtureDTO,
  InventarioLecciones,
  LeccionItem,
  FixtureLiveDTO,
  RefrescoLigaDTO,
  VipEstadoDTO,
  GeneracionEfeDTO,
  HealthDTO,
  EslabonDtpDTO,
  LigaDTO,
  NivelDTO,
  PartidoCalendarioDTO,
  PlantillaDTO,
  ParteCoworkDTO,
  PartePendienteDTO,
  LatidoCoworkDTO,
  SobrePendientesDTO,
  PreflightEfeDTO,
  PrediccionDTO,
  XiLadoDTO,
  StandingRowDTO,
} from './types'

export const SadApi = {
  health: () => apiGet<HealthDTO>('/health', { timeoutMs: 5_000 }),

  fixtures: (params: { fecha?: string; desde?: string; estado?: EstadoFixture; orden?: 'asc' | 'desc'; ligaId?: number; temporada?: number; equipoId?: number; rivalId?: number; limit?: number } = {}) =>
    apiGet<FixtureDTO[]>('/fixtures' + qs(params)),

  /** Búsqueda inteligente de equipos (sin tildes, ranking por prefijo). */
  buscarEquipos: (buscar: string, limit = 10) => apiGet<EquipoDTO[]>('/equipos' + qs({ buscar, limit })),

  fixture: (id: number) => apiGet<FixtureDTO>(`/fixtures/${id}`),

  /** En vivo real: marcador, minuto y cuotas en juego (vacías si no hay cobertura). */
  fixtureLive: (id: number) => apiGet<FixtureLiveDTO>(`/fixtures/${id}/live`),

  /** Marca/desmarca el partido como VIP ("sí o sí, aunque cueste"). */
  marcarVip: (id: number, activo: boolean) =>
    apiPost<VipEstadoDTO>(`/fixtures/${id}/vip`, { activo }),

  /** Refresco forzado del marcador de la liga (lo atiende el próximo ciclo en vivo). */
  refrescarLiga: (ligaId: number) =>
    apiPost<RefrescoLigaDTO>(`/ligas/${ligaId}/refrescar`, {}),

  /** Historia de niveles de un equipo (desc por fecha; limit opcional). */
  niveles: (equipoId: number, limit?: number, antesDe?: number) =>
    apiGet<NivelDTO[]>(`/niveles/${equipoId}` + qs({ limit, antesDe })),

  /** Historia de constantes K de un equipo (desc por fecha; limit opcional). */
  /** `antesDe` = id de fixture: solo lo anterior a ese partido (vista al día del partido). */
  constantes: (equipoId: number, limit?: number, antesDe?: number) =>
    apiGet<ConstantesDTO[]>(`/constantes/${equipoId}` + qs({ limit, antesDe })),

  /** k_cuota (§3.8): rachas de suma de cuota 1X2, solo 2026 (asc por fecha). */
  constantesCuota: (equipoId: number) =>
    apiGet<ConstanteCuotaDTO[]>(`/constantes-cuota/${equipoId}`),

  prediccion: (fixtureId: number) => apiGet<PrediccionDTO>(`/predicciones/${fixtureId}`),

  analisisPrepartido: (fixtureId: number) =>
    apiGet<AnalisisPrepartidoDTO>(`/analisis-prepartido/${fixtureId}`),

  cuotas: (fixtureId: number) => apiGet<CuotaDTO[]>(`/cuotas/${fixtureId}`),

  /** Cuota de cada casa por selección, la mejor marcada (orden cuota desc). */
  cuotasCasas: (fixtureId: number) => apiGet<CuotaCasaDTO[]>(`/cuotas/${fixtureId}/casas`),

  /** Historial de snapshots prepartido (asc por captura; [] si aún no hay).
   *  Sin `casa`: media entre casas; con `casa`: el crudo de esa referencia. */
  cuotasHistorial: (fixtureId: number, casa?: string | null) =>
    apiGet<CuotaSnapshotDTO[]>(`/cuotas/${fixtureId}/historial` + qs({ casa: casa ?? undefined })),

  /** Casas de referencia con historial propio para el fixture. */
  cuotasHistorialFuentes: (fixtureId: number) =>
    apiGet<string[]>(`/cuotas/${fixtureId}/historial/fuentes`),

  equipoStats: (equipoId: number) => apiGet<EquipoStatsDTO>(`/equipos/${equipoId}/stats`),

  /** Plantilla con indicadores de jugadores (docs/JUGADORES.md). */
  plantilla: (equipoId: number) => apiGet<PlantillaDTO>(`/equipos/${equipoId}/plantilla`),

  /** Ficha de partido: plantillas + congestión de ambos equipos. */
  fichaPartido: (fixtureId: number) => apiGet<FichaPartidoDTO>(`/fixtures/${fixtureId}/ficha`),

  /** Análisis emitidos para un fixture (lectura pura, cero créditos). */
  analisisPartido: (fixtureId: number) => apiGet<AnalisisRegistroDTO[]>(`/analisis/partido/${fixtureId}`),

  /** Lanza el análisis EFE (respuesta inmediata: listo/generando/error);
   *  el trabajo corre en el servidor y se sondea con estadoEfe.
   *  `forzar` = regenerar: descarta el guardado y emite uno nuevo. */
  generarEfe: (fixtureId: number, forzar = false, permitirFrio = false) =>
    apiPost<GeneracionEfeDTO>('/analisis/efe', { fixtureId, forzar, permitirFrio }, { timeoutMs: 30_000 }),

  /** Sondeo del trabajo de análisis EFE. */
  estadoEfe: (fixtureId: number) => apiGet<GeneracionEfeDTO>(`/analisis/efe/estado/${fixtureId}`),

  /** Qué va a costar el EFE ANTES de generarlo (costo cero: no llama al modelo
   *  ni gasta cuota de API-Football). */
  preflightEfe: (fixtureId: number) => apiGet<PreflightEfeDTO>(`/analisis/efe/preflight/${fixtureId}`),

  /** Carga manual de la despensa: investigación del Claude de escritorio
   *  (docs/DESPENSA_DESKTOP.md) — el próximo EFE no busca en la web. */
  cargarDespensa: (payload: CargaDespensaDTO) =>
    apiPost<CargaDespensaResultadoDTO>('/analisis/despensa', payload, { timeoutMs: 15_000 }),

  /** Lanza el timeline comparativo (mismo patrón asíncrono que el EFE). */
  generarTimeline: (fixtureId: number, forzar = false) =>
    apiPost<GeneracionEfeDTO>('/analisis/timeline', { fixtureId, forzar }, { timeoutMs: 30_000 }),

  /** Sondeo del trabajo de timeline. */
  estadoTimeline: (fixtureId: number) => apiGet<GeneracionEfeDTO>(`/analisis/timeline/estado/${fixtureId}`),

  /** Lanza el DTP desde un equipo foco (la cadena es la película de UN equipo). */
  generarDtp: (fixtureId: number, equipoFoco: number, forzar = false) =>
    apiPost<GeneracionEfeDTO>('/analisis/dtp', { fixtureId, equipoFoco, forzar }, { timeoutMs: 30_000 }),

  /** Sondeo del trabajo de DTP. */
  estadoDtp: (fixtureId: number, equipoFoco: number) =>
    apiGet<GeneracionEfeDTO>(`/analisis/dtp/estado/${fixtureId}` + qs({ equipoFoco })),

  /** Calendario SAD: próximos partidos con el mapa de rivales del bloque G
   *  ya calculado de nuestra base (0 tokens). */
  calendario: (equipoId: number, n?: number) =>
    apiGet<PartidoCalendarioDTO[]>(`/equipos/${equipoId}/calendario` + qs({ n })),
  /** Reventón de la burbuja (docs/REVENTON.md): guía calculada, 0 tokens. */
  burbujas: (equipoId: number, antesDe?: number, proximo?: number) => apiGet<BurbujasEquipoDTO>(`/equipos/${equipoId}/burbujas` + qs({ antesDe, proximo })),

  /** La película del equipo: pronóstico → qué pasó → veredicto → lección. */
  cadena: (equipoId: number, limit?: number) =>
    apiGet<EslabonDtpDTO[]>(`/equipos/${equipoId}/cadena` + qs({ limit })),

  /** Metadatos de la liga (nombre, país, logo, bandera, fases de la temporada). */
  liga: (ligaId: number, temporada?: number) => apiGet<LigaDTO>(`/ligas/${ligaId}` + qs({ temporada })),

  // ── parte de Cowork: el análisis escrito con la suscripción ──────────────

  /** El parte del partido con lo calculable ya calculado. null si no hay. */
  parteCowork: (fixtureId: number) => apiGet<ParteCoworkDTO>(`/analisis/cowork/${fixtureId}`),

  /** Llega el once y el bloque F se cierra en el backend: gratis y al instante.
   *  Sin onces, se intenta con la ficha que ya capturó la ingesta. */
  resolverXi: (fixtureId: number, body: { a?: XiLadoDTO; b?: XiLadoDTO; desdeFicha?: boolean }) =>
    apiPost<ParteCoworkDTO>(`/analisis/cowork/${fixtureId}/xi`, body, { timeoutMs: 20_000 }),

  /** Lo que el bucle aprendió, por skill (fase C de docs/APRENDIZAJE.md). */
  lecciones: (params?: { skill?: string; estado?: string }) =>
    apiGet<InventarioLecciones>('/analisis/cowork/lecciones' + qs(params ?? {})),

  /** Mueve una lección de estado. `aplicada` exige la versión del skill. */
  moverLeccion: (clave: string, body: { estado: string; aplicadaEn?: string; nota?: string }) =>
    apiPost<LeccionItem>(`/analisis/cowork/lecciones/${encodeURIComponent(clave)}`, body),

  /** Los partidos del día ordenados por prioridad (paso 1 del batch nocturno). */
  agendaCowork: (fecha?: string, limite?: number) =>
    apiGet<AgendaCoworkDTO>('/analisis/cowork/agenda' + qs({ fecha, limite })),

  /** Partes de partidos ya jugados y sin veredicto (fase B). */
  coworkLatido: (horas?: number) =>
    apiGet<LatidoCoworkDTO>('/analisis/cowork/latido' + qs({ horas })),
  veredictosPendientes: (horas?: number, limite?: number) =>
    apiGet<SobrePendientesDTO>('/analisis/cowork/veredictos/pendientes' + qs({ horas, limite })),

  /** Partes que todavía esperan once. */
  partesPendientes: (limite?: number) =>
    apiGet<PartePendienteDTO[]>('/analisis/cowork/pendientes' + qs({ limite })),

  standings: (ligaId: number, temporada?: number, fase?: string) =>
    apiGet<StandingRowDTO[]>(`/ligas/${ligaId}/standings` + qs({ temporada, fase })),
}
