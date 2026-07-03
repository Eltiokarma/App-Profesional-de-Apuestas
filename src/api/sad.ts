// Endpoints del backend SAD (contrato: docs/openapi.yaml).
import { apiGet, qs } from './client'
import type {
  AnalisisPrepartidoDTO,
  ConstantesDTO,
  CuotaDTO,
  EquipoStatsDTO,
  EstadoFixture,
  FixtureDTO,
  HealthDTO,
  NivelDTO,
  PrediccionDTO,
  StandingRowDTO,
} from './types'

export const SadApi = {
  health: () => apiGet<HealthDTO>('/health', { timeoutMs: 5_000 }),

  fixtures: (params: { fecha?: string; estado?: EstadoFixture; ligaId?: number } = {}) =>
    apiGet<FixtureDTO[]>('/fixtures' + qs(params)),

  fixture: (id: number) => apiGet<FixtureDTO>(`/fixtures/${id}`),

  /** Historia de niveles de un equipo (desc por fecha; limit opcional). */
  niveles: (equipoId: number, limit?: number) =>
    apiGet<NivelDTO[]>(`/niveles/${equipoId}` + qs({ limit })),

  /** Historia de constantes K de un equipo (desc por fecha; limit opcional). */
  constantes: (equipoId: number, limit?: number) =>
    apiGet<ConstantesDTO[]>(`/constantes/${equipoId}` + qs({ limit })),

  prediccion: (fixtureId: number) => apiGet<PrediccionDTO>(`/predicciones/${fixtureId}`),

  analisisPrepartido: (fixtureId: number) =>
    apiGet<AnalisisPrepartidoDTO>(`/analisis-prepartido/${fixtureId}`),

  cuotas: (fixtureId: number) => apiGet<CuotaDTO[]>(`/cuotas/${fixtureId}`),

  equipoStats: (equipoId: number) => apiGet<EquipoStatsDTO>(`/equipos/${equipoId}/stats`),

  standings: (ligaId: number, temporada?: number) =>
    apiGet<StandingRowDTO[]>(`/ligas/${ligaId}/standings` + qs({ temporada })),
}
