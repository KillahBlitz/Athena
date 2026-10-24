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
  id_carrera: number
  puntuation: number
  description: string
}

export interface SaveUserRiasecDTO {
  risec_id: number
  criteria_list: Record<number, string>[]
  open_question: string
}

export interface SaveUserRequestDTO {
  username: string
  email: string
  age: number
  area_id: number
  objetives: SaveUserObjectiveDTO[]
  risec_questions: Record<number, SaveUserRiasecDTO>
}
