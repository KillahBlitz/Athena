export const EVALUATION_UUID_KEY = 'athena_user_uuid'

export function getEvaluationUuid(): string | null {
  if (typeof window === 'undefined') return null
  try {
    return localStorage.getItem(EVALUATION_UUID_KEY)?.trim() || null
  } catch {
    return null
  }
}

export function saveEvaluationUuid(uuid: string): void {
  try {
    localStorage.setItem(EVALUATION_UUID_KEY, uuid)
  } catch {
    throw new Error('No fue posible guardar el identificador de tu evaluación en este navegador.')
  }
}
