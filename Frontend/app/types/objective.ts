export type RatingValue = 1 | 2 | 3 | 4 | 5

export interface NormalizedObjective {
  objectiveId: number
  carreraId: number
  pregunta: string
  category: string
  valoracion: RatingValue | null
  justificacion: string
}

export interface ObjectiveAnswer {
  carreraId: number
  valoracion: RatingValue | null
  justificacion: string
}

export interface ObjectiveBlock {
  blockIndex: number
  totalBlocks: number
  objectives: NormalizedObjective[]
}

export interface ObjectivesProgress {
  currentBlock: number
  totalBlocks: number
  answeredCount: number
  totalObjectives: number
  percentage: number
}
