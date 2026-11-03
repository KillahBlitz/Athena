import type { GetResultsCareerDTO } from '../types/api'

/**
 * Caché del resultado final de la evaluación.
 *
 * Una vez que la API devuelve `status_id === 4` con los resultados, estos ya no
 * cambian. Guardarlos evita volver a mostrar la pantalla de espera o reconsultar
 * la API cuando el usuario cierra y vuelve a abrir la ventana.
 *
 * Usa el prefijo `athena_` para que `clearAthenaStorage()` / `startOver()` lo
 * eliminen junto con el resto del estado de la sesión.
 */
export const RESULTS_READY_KEY = 'athena_results_v1'

interface CachedResults {
  user_uuid: string
  results: GetResultsCareerDTO[]
}

/** Devuelve los resultados cacheados solo si corresponden al `userUuid` indicado. */
export function getCachedResults(userUuid: string): GetResultsCareerDTO[] | null {
  if (typeof window === 'undefined' || !userUuid) return null
  try {
    const raw = localStorage.getItem(RESULTS_READY_KEY)
    if (!raw) return null
    const data = JSON.parse(raw) as CachedResults
    if (data?.user_uuid !== userUuid || !Array.isArray(data.results)) return null
    return data.results
  } catch {
    return null
  }
}

/** True si ya hay resultados finales guardados para el `userUuid` indicado. */
export function hasCachedResults(userUuid: string): boolean {
  return getCachedResults(userUuid) !== null
}

/** Guarda los resultados finales (`status_id === 4`) asociados a un `userUuid`. */
export function saveCachedResults(userUuid: string, results: GetResultsCareerDTO[]): void {
  if (typeof window === 'undefined' || !userUuid) return
  try {
    const payload: CachedResults = { user_uuid: userUuid, results: results ?? [] }
    localStorage.setItem(RESULTS_READY_KEY, JSON.stringify(payload))
  } catch {
  }
}
