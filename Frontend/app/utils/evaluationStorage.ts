export const EVALUATION_UUID_KEY = 'athena_user_uuid'

export function getEvaluationUuid(): string | null {
  if (typeof window === 'undefined') return null
  try {
    return localStorage.getItem(EVALUATION_UUID_KEY)?.trim() || null
  } catch {
    return null
  }
}

const ATHENA_STORAGE_PREFIX = 'athena_'

export function clearAthenaStorage(): void {
  if (typeof window === 'undefined') return
  try {
    const keys = Array.from({ length: localStorage.length }, (_, i) => localStorage.key(i))
    for (const key of keys) {
      if (key?.startsWith(ATHENA_STORAGE_PREFIX)) localStorage.removeItem(key)
    }
  } catch {
  }
}

export function saveEvaluationUuid(uuid: string): void {
  try {
    localStorage.setItem(EVALUATION_UUID_KEY, uuid)
  } catch {
    throw new Error('No fue posible guardar el identificador de tu evaluación en este navegador.')
  }
}
