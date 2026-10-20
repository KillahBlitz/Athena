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
