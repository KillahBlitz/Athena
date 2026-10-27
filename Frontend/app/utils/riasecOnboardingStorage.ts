export const RIASEC_ONBOARDING_KEY = 'athena_riasec_onboarding_seen'

export function hasSeenRiasecOnboarding(): boolean {
  if (typeof window === 'undefined') return true
  try {
    return localStorage.getItem(RIASEC_ONBOARDING_KEY) === '1'
  } catch {
    return true
  }
}

export function markRiasecOnboardingSeen(): void {
  try {
    localStorage.setItem(RIASEC_ONBOARDING_KEY, '1')
  } catch {
  }
}
