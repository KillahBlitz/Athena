// Tracks whether the user has already seen the one-time "how this section
// works" onboarding card the first time they land on /riasec. Stored
// globally so it only ever appears once per browser.
export const RIASEC_ONBOARDING_KEY = 'athena_riasec_onboarding_seen'

export function hasSeenRiasecOnboarding(): boolean {
  if (typeof window === 'undefined') return true
  try {
    return localStorage.getItem(RIASEC_ONBOARDING_KEY) === '1'
  } catch {
    // If storage is unavailable, default to "already seen" so the overlay
    // never gets stuck blocking the page.
    return true
  }
}

export function markRiasecOnboardingSeen(): void {
  try {
    localStorage.setItem(RIASEC_ONBOARDING_KEY, '1')
  } catch {
    // Non-critical: worst case the onboarding card reappears next visit.
  }
}
