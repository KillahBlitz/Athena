import type { SaveUserRequestDTO } from '../types/api'
import { createApiError } from '../utils/apiError'

interface ValidationIssue {
  loc: (string | number)[]
  msg: string
}

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

  const saveUser = async (payload: SaveUserRequestDTO): Promise<string> => {
    try {
      const response = await $fetch<string>(`${apiBase}/save-user`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json'
        },
        body: payload
      })
      if (typeof response !== 'string' || !response.trim()) {
        throw new Error('El servidor no devolvió el identificador de tu evaluación. Inténtalo de nuevo.')
      }
      return response.trim()
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
