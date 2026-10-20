import type { ApiError } from '../types/api'

export function createApiError(error: unknown, fallbackMessage = 'Ha ocurrido un error inesperado al conectar con el servidor.'): ApiError {
  if (error && typeof error === 'object' && 'statusCode' in error) {
    const err = error as { statusCode: number; statusMessage?: string; message?: string }
    return {
      statusCode: err.statusCode || 500,
      message: err.statusMessage || err.message || fallbackMessage,
      details: error
    }
  }

  if (error instanceof Error) {
    return {
      statusCode: 500,
      message: error.message || fallbackMessage,
      details: error
    }
  }

  return {
    statusCode: 500,
    message: fallbackMessage,
    details: error
  }
}
