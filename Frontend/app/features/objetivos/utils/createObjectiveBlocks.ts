import type { NormalizedObjective, ObjectiveBlock } from '../../../types/objective'
import type { BackendObjetivoDTO } from '../../../types/area'
import { OBJECTIVES_PER_BLOCK } from '../../../config/objectives'

type LegacyObjectives = Record<string, { id_carrera: number; pregunta_objetivo: string | null } | string | null>

export function normalizeObjectives(
  rawObjetivos: BackendObjetivoDTO[] | LegacyObjectives
): NormalizedObjective[] {
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

  const objetivos: BackendObjetivoDTO[] = Array.isArray(rawObjetivos)
    ? rawObjetivos
    : Object.entries(rawObjetivos).map(([id, objetivo]) => ({
      id_objetivo: Number(id),
      id_carrera: typeof objetivo === 'string' ? Number(id) : objetivo?.id_carrera ?? Number.NaN,
      pregunta: typeof objetivo === 'string' ? objetivo : objetivo?.pregunta_objetivo ?? null
    }))

  return objetivos
    .flatMap((objetivo, index) => {
      const { id_objetivo: objectiveId, id_carrera: carreraId, pregunta } = objetivo
      if (!pregunta?.trim() || !Number.isInteger(objectiveId)
        || typeof carreraId !== 'number' || !Number.isInteger(carreraId)) {
        return []
      }
      const categoryName = CATEGORIES[index % CATEGORIES.length] ?? 'General'
      return [{
        objectiveId,
        carreraId,
        pregunta: pregunta.trim(),
        category: categoryName,
        valoracion: null,
        justificacion: ''
      }]
    })
}

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
