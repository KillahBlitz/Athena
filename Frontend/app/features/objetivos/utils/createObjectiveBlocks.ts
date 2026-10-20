import type { NormalizedObjective, ObjectiveBlock } from '../../../types/objective'

/**
 * Normalizes the raw backend dictionary of objectives into typed NormalizedObjective array
 */
export function normalizeObjectives(rawObjetivos: Record<string, string | null>): NormalizedObjective[] {
  if (!rawObjetivos || typeof rawObjetivos !== 'object') {
    return []
  }

  // Predefined category rotation for clean visual tags matching the design references
  const CATEGORIES = [
    'Curiosidad y Exploración',
    'Aprendizaje y Propósito',
    'Innovación y Tecnología',
    'Impacto y Desarrollo',
    'Creatividad y Solución',
    'Compromiso y Sociedad'
  ]

  return Object.entries(rawObjetivos)
    .filter(([_, pregunta]) => Boolean(pregunta && pregunta.trim()))
    .map(([carreraIdStr, pregunta], index) => {
      const carreraId = Number(carreraIdStr)
      const categoryName = CATEGORIES[index % CATEGORIES.length] ?? 'General'
      return {
        carreraId: Number.isNaN(carreraId) ? index + 1 : carreraId,
        pregunta: (pregunta as string).trim(),
        category: categoryName,
        valoracion: null,
        justificacion: ''
      }
    })
}

/**
 * Dynamically partitions normalized objectives into blocks of blockSize (default 4).
 * Preserves order, handles incomplete last blocks, never mutates original array.
 */
export function createObjectiveBlocks(
  objectives: readonly NormalizedObjective[],
  blockSize = 4
): ObjectiveBlock[] {
  if (!Array.isArray(objectives) || objectives.length === 0 || blockSize <= 0) {
    return []
  }

  const totalBlocks = Math.ceil(objectives.length / blockSize)
  const blocks: ObjectiveBlock[] = []

  for (let i = 0; i < totalBlocks; i++) {
    const start = i * blockSize
    const end = start + blockSize
    const blockObjectives = objectives.slice(start, end).map(obj => ({ ...obj }))

    blocks.push({
      blockIndex: i + 1,
      totalBlocks,
      objectives: blockObjectives
    })
  }

  return blocks
}
