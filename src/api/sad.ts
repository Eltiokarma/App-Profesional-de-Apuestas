// Endpoints del backend SAD (contrato: docs/openapi.yaml).
import { apiGet, apiPost, qs } from './client'
import type {
  AnalisisPrepartidoDTO,
  AnalisisRegistroDTO,
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
  FixtureLiveDTO,
  GeneracionEfeDTO,
  HealthDTO,
  LigaDTO,
  NivelDTO,
  PlantillaDTO,
  PrediccionDTO,
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

  /** Historia de niveles de un equipo (desc por fecha; limit opcional). */
  niveles: (equipoId: number, limit?: number) =>
    apiGet<NivelDTO[]>(`/niveles/${equipoId}` + qs({ limit })),

  /** Historia de constantes K de un equipo (desc por fecha; limit opcional). */
  constantes: (equipoId: number, limit?: number) =>
    apiGet<ConstantesDTO[]>(`/constantes/${equipoId}` + qs({ limit })),

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
  generarEfe: (fixtureId: number, forzar = false) =>
    apiPost<GeneracionEfeDTO>('/analisis/efe', { fixtureId, forzar }, { timeoutMs: 30_000 }),

  /** Sondeo del trabajo de análisis EFE. */
  estadoEfe: (fixtureId: number) => apiGet<GeneracionEfeDTO>(`/analisis/efe/estado/${fixtureId}`),

  /** Lanza el timeline comparativo (mismo patrón asíncrono que el EFE). */
  generarTimeline: (fixtureId: number, forzar = false) =>
    apiPost<GeneracionEfeDTO>('/analisis/timeline', { fixtureId, forzar }, { timeoutMs: 30_000 }),

  /** Sondeo del trabajo de timeline. */
  estadoTimeline: (fixtureId: number) => apiGet<GeneracionEfeDTO>(`/analisis/timeline/estado/${fixtureId}`),

  /** Metadatos de la liga (nombre, país, logo, bandera). */
  liga: (ligaId: number) => apiGet<LigaDTO>(`/ligas/${ligaId}`),

  standings: (ligaId: number, temporada?: number) =>
    apiGet<StandingRowDTO[]>(`/ligas/${ligaId}/standings` + qs({ temporada })),
}
