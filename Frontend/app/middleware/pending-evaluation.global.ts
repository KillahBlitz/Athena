import { getEvaluationUuid } from '../utils/evaluationStorage'

export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return

  const uuid = getEvaluationUuid()
  if (uuid && !['/', '/espera', '/resultados'].includes(to.path)) {
    return navigateTo('/espera', { replace: true })
  }
  if (!uuid && ['/espera', '/resultados'].includes(to.path)) {
    return navigateTo('/riasec', { replace: true })
  }
})
