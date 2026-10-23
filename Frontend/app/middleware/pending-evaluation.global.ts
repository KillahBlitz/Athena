import { getEvaluationUuid } from '../utils/evaluationStorage'

export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return

  const uuid = getEvaluationUuid()
  if (uuid && to.path !== '/espera') {
    return navigateTo('/espera', { replace: true })
  }
  if (!uuid && to.path === '/espera') {
    return navigateTo('/riasec', { replace: true })
  }
})
