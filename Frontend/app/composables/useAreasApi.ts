import type { BackendAreaDTO, BackendQuestionaryResponseDTO } from '../types/area'
import { createApiError } from '../utils/apiError'

export function useAreasApi() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const fetchAreas = async (): Promise<BackendAreaDTO[]> => {
    try {
      const response = await $fetch<BackendAreaDTO[]>(`${apiBase}/get_areas`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      })
      if (!Array.isArray(response) || response.length === 0) {
        throw new Error('El servidor no devolvió áreas disponibles.')
      }
      return response
    } catch (err) {
      throw createApiError(err, 'No fue posible cargar las áreas disponibles desde el servidor.')
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
      if (!response || !response.objetivos || Object.keys(response.objetivos).length === 0) {
        throw new Error(`El área ${areaId} no contiene datos válidos.`)
      }
      return response
    } catch (err) {
      throw createApiError(err, `No fue posible cargar los datos del área ${areaId}.`)
    }
  }

  return {
    fetchAreas,
    fetchAreaData
  }
}
