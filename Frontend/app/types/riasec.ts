export interface RiasecOption {
  opcionId: number
  texto: string
}

export interface RiasecAnswer {
  opcionIds: number[]
  respuestaAbierta: string
}

export interface RiasecDimension {
  name: string
  tagline: string
  icon: string[]
}

export interface RiasecProgress {
  currentQuestion: number
  totalQuestions: number
  answeredCount: number
  percentage: number
}
