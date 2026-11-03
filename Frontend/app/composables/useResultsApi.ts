import type { GetResultsResponseDTO } from '../types/api'

export function useResultsApi() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const fetchResults = async (userUuid: string, signal?: AbortSignal): Promise<GetResultsResponseDTO> => {
    const response = await $fetch<GetResultsResponseDTO>(`${apiBase}/get-results/${encodeURIComponent(userUuid)}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal,
      timeout: 10000,
      retry: 0
    })
    if (response?.user_uuid !== userUuid || ![1, 2, 3, 4].includes(response.status_id)) {
      throw new Error('El servidor no devolvió un estado válido para tu evaluación.')
    }
    return response
  }

  return { fetchResults }
}
