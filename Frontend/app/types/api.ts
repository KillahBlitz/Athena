export interface ApiError {
  statusCode: number
  message: string
  details?: unknown
}

export interface ApiResponse<T> {
  data: T | null
  error: ApiError | null
  loading: boolean
}

export interface SaveUserObjectiveDTO {
  id_objetive: number
  puntuation: number
  description: string
}

export interface SaveUserRiasecDTO {
  risec_id: number
  criteria_id_list: number[]
  open_question: string
}

export interface SaveUserRequestDTO {
  username: string
  email: string
  age: number
  area_id: number
  objetives: SaveUserObjectiveDTO[]
  risec_questions: SaveUserRiasecDTO[]
}
