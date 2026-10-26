// Tracks whether the user has already seen the one-time "how to answer"
// onboarding card the first time they land on /objetivos. Stored globally
// (not per block) so it only ever appears once per browser.
export const OBJECTIVES_ONBOARDING_KEY = 'athena_objectives_onboarding_seen'

export function hasSeenObjectivesOnboarding(): boolean {
  if (typeof window === 'undefined') return true
  try {
    return localStorage.getItem(OBJECTIVES_ONBOARDING_KEY) === '1'
  } catch {
    // If storage is unavailable, default to "already seen" so the overlay
    // never gets stuck blocking the page.
    return true
  }
}

export function markObjectivesOnboardingSeen(): void {
  try {
    localStorage.setItem(OBJECTIVES_ONBOARDING_KEY, '1')
  } catch {
    // Non-critical: worst case the onboarding card reappears next visit.
  }
}
