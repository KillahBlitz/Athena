import type { SaveUserRequestDTO } from '../types/api'
import { createApiError } from '../utils/apiError'

export const TEST_SUBMITTED_KEY = 'athena_test_submitted'

interface ValidationIssue {
  loc: (string | number)[]
  msg: string
}

// Turns a FastAPI 422 body into a readable list like "objetives.3.puntuation: ..."
function describeValidationError(err: unknown): string | null {
  const detail = (err as { data?: { detail?: unknown } })?.data?.detail
  if (!Array.isArray(detail) || detail.length === 0) return null
  const issues = (detail as ValidationIssue[])
    .map(issue => `${issue.loc.filter(part => part !== 'body').join('.')}: ${issue.msg}`)
  return `El servidor rechazó los datos (${issues.join('; ')}).`
}

export function useSaveUserApi() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const saveUser = async (payload: SaveUserRequestDTO): Promise<boolean> => {
    try {
      const response = await $fetch<boolean>(`${apiBase}/save-user`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json'
        },
        body: payload
      })
      return response === true
    } catch (err) {
      const validationMessage = describeValidationError(err)
      if (validationMessage) throw { ...createApiError(err), statusCode: 422, message: validationMessage }
      throw createApiError(err, 'No fue posible guardar tus resultados. Inténtalo de nuevo.')
    }
  }

  return {
    saveUser
  }
}
