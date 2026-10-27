export const OBJECTIVES_ONBOARDING_KEY = 'athena_objectives_onboarding_seen'

export function hasSeenObjectivesOnboarding(): boolean {
  if (typeof window === 'undefined') return true
  try {
    return localStorage.getItem(OBJECTIVES_ONBOARDING_KEY) === '1'
  } catch {
    return true
  }
}

export function markObjectivesOnboardingSeen(): void {
  try {
    localStorage.setItem(OBJECTIVES_ONBOARDING_KEY, '1')
  } catch {
  }
}
