import type { BackendAreaDTO, BackendQuestionaryResponseDTO } from '../types/area'
import { createApiError } from '../utils/apiError'
import { OFFICIAL_AREAS_FALLBACK, OFFICIAL_QUESTIONARY_FALLBACK } from '../features/datos-personales/data/officialAreasData'

export function useAreasApi() {
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'

  const fetchAreas = async (): Promise<BackendAreaDTO[]> => {
    try {
      const response = await $fetch<BackendAreaDTO[]>(`${apiBase}/get_areas`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      })
      if (Array.isArray(response) && response.length > 0) {
        return response
      }
      return OFFICIAL_AREAS_FALLBACK
    } catch (err) {
      console.warn('[useAreasApi] Endpoint /get_areas no disponible, utilizando dataset oficial verificado.', err)
      return OFFICIAL_AREAS_FALLBACK
    }
  }

  const fetchAreaData = async (areaId: number): Promise<BackendQuestionaryResponseDTO> => {
    try {
      const response = await $fetch<BackendQuestionaryResponseDTO>(`${apiBase}/${areaId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      })
      if (response && response.objetivos && Object.keys(response.objetivos).length > 0) {
        return response
      }
      const fallback = OFFICIAL_QUESTIONARY_FALLBACK[areaId]
      if (fallback) return fallback
      throw new Error(`Área ${areaId} no contiene datos válidos.`)
    } catch (err) {
      console.warn(`[useAreasApi] Endpoint /${areaId} no disponible, utilizando dataset oficial verificado.`, err)
      const fallback = OFFICIAL_QUESTIONARY_FALLBACK[areaId]
      if (fallback) return fallback
      throw createApiError(err, `No fue posible cargar los datos del área ${areaId}`)
    }
  }

  return {
    fetchAreas,
    fetchAreaData
  }
}
