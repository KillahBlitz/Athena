export type Medal = 'oro' | 'plata' | 'bronce'

export interface DimensionScore {
  riasecId: number
  /** Puntaje normalizado entre 0 y 1. */
  score: number
}

export interface CareerMatch {
  rank: 1 | 2 | 3
  name: string
  schools: string[]
  /** Porcentaje de coincidencia entre 0 y 100. */
  match: number
}

export interface VocationalProfile {
  dominantRiasecId: number
  title: string
  tagline: string
  summary: string
  traits: string[]
  scores: DimensionScore[]
  careers: CareerMatch[]
}
