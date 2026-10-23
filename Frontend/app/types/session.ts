import type { NormalizedObjective, RatingValue } from './objective'
import type { BackendQuestionaryResponseDTO } from './area'

export interface PersonalData {
  name: string
  email: string
  age: number | null
  termsAccepted: boolean
}

export interface UserSessionState {
  personalData: PersonalData
  selectedAvatarId: string
  selectedAreaId: number | null
  selectedAreaName: string | null
  areaData: BackendQuestionaryResponseDTO | null
  objectives: NormalizedObjective[]
  answers: Record<number, { valoracion: RatingValue | null; justificacion: string }>
  currentBlock: number
  status: 'idle' | 'in-progress' | 'objectives-completed'
}
