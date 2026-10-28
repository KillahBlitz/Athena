export const OBJECTIVES_PER_BLOCK = 6

/** Valoración que exige escribir una justificación. */
export const REQUIRED_JUSTIFICATION_RATING = 5

export function isJustificationRequired(rating: number | null | undefined): boolean {
    return rating === REQUIRED_JUSTIFICATION_RATING
}
