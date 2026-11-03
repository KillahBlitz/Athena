export const OBJECTIVES_PER_BLOCK = 6

export const MIN_REQUIRED_JUSTIFICATION_RATING = 4

export function isJustificationRequired(rating: number | null | undefined): boolean {
    return rating != null && rating >= MIN_REQUIRED_JUSTIFICATION_RATING
}
