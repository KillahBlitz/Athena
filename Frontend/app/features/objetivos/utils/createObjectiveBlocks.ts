import type { NormalizedObjective, ObjectiveBlock } from '../../../types/objective'
import { OBJECTIVES_PER_BLOCK } from '../../../config/objectives'


export function normalizeObjectives(rawObjetivos: Record<string, string | null>): NormalizedObjective[] {
  if (!rawObjetivos || typeof rawObjetivos !== 'object') {
    return []
  }

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
 * Dynamically partitions normalized objectives into blocks of blockSize (default OBJECTIVES_PER_BLOCK).
 * Preserves order, handles incomplete last blocks, never mutates original array.
 */
export function createObjectiveBlocks(
  objectives: readonly NormalizedObjective[],
  blockSize = OBJECTIVES_PER_BLOCK
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
