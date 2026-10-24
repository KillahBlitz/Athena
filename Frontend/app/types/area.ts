export interface BackendAreaDTO {
  area_id: number
  nom_area: string
}

export interface BackendPreguntaDTO {
  riasec_id: number
  texto_pregunta: string
  pregunta_abierta: string
  opciones: Record<string, string>
}

export interface BackendObjetivoDTO {
  id_carrera: number
  id_objetivo: number
  pregunta: string | null
}

export interface BackendQuestionaryResponseDTO {
  area_id: number
  nom_area: string
  objetivos: BackendObjetivoDTO[]
  preguntas: BackendPreguntaDTO[]
}

export interface Area {
  id: number
  name: string
  tagline: string
  icon: string
}
