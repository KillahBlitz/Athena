import { defineStore } from 'pinia'
import type { BackendPreguntaDTO, BackendQuestionaryResponseDTO } from '../types/area'
import type { NormalizedObjective, ObjectiveBlock, RatingValue, ObjectivesProgress } from '../types/objective'
import type { PersonalData } from '../types/session'
import type { Avatar } from '../types/avatar'
import type { RiasecAnswer, RiasecProgress } from '../types/riasec'
import type { SaveUserRequestDTO } from '../types/api'
import { AVATARS, DEFAULT_AVATAR } from '../config/avatars'
import { createObjectiveBlocks, normalizeObjectives } from '../features/objetivos/utils/createObjectiveBlocks'
import { OBJECTIVES_PER_BLOCK } from '../config/objectives'
import { getEvaluationUuid } from '../utils/evaluationStorage'

const STORAGE_KEY = 'athena_session_v2'

export const useAthenaSessionStore = defineStore('athena-session', {
  state: () => ({
    name: '',
    email: '',
    age: null as number | null,
    termsAccepted: false,
    selectedAvatarId: DEFAULT_AVATAR.id,
    selectedAreaId: null as number | null,
    selectedAreaName: null as string | null,
    areaData: null as BackendQuestionaryResponseDTO | null,
    objectives: [] as NormalizedObjective[],
    answers: {} as Record<number, { valoracion: RatingValue | null; justificacion: string }>,
    currentBlock: 1,
    riasecAnswers: {} as Record<number, RiasecAnswer>,
    currentRiasecIndex: 0,
    status: 'idle' as 'idle' | 'in-progress' | 'objectives-completed' | 'riasec-completed'
  }),

  getters: {
    personalData: (state): PersonalData => ({
      name: state.name,
      email: state.email,
      age: state.age,
      termsAccepted: state.termsAccepted
    }),

    selectedAvatar: (state): Avatar => {
      return AVATARS.find(a => a.id === state.selectedAvatarId) || DEFAULT_AVATAR
    },

    isPersonalDataValid: (state): boolean => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      const ageNum = Number(state.age)
      return (
        state.name.trim().length > 0 &&
        emailRegex.test(state.email.trim()) &&
        !Number.isNaN(ageNum) &&
        ageNum >= 12 &&
        ageNum <= 100 &&
        Boolean(state.selectedAvatarId) &&
        state.selectedAreaId !== null &&
        state.termsAccepted === true
      )
    },

    blocks: (state): ObjectiveBlock[] => {
      return createObjectiveBlocks(state.objectives, OBJECTIVES_PER_BLOCK)
    },

    totalBlocks: (state): number => {
      return Math.ceil(state.objectives.length / OBJECTIVES_PER_BLOCK)
    },

    currentBlockData: (state): ObjectiveBlock | null => {
      const allBlocks = createObjectiveBlocks(state.objectives, OBJECTIVES_PER_BLOCK)
      if (allBlocks.length === 0) return null
      const idx = Math.max(1, Math.min(state.currentBlock, allBlocks.length))
      return allBlocks[idx - 1] || null
    },

    progress(state): ObjectivesProgress {
      const total = state.objectives.length
      const totalBlocks = this.totalBlocks
      if (total === 0) {
        return {
          currentBlock: state.currentBlock,
          totalBlocks: 0,
          answeredCount: 0,
          totalObjectives: 0,
          percentage: 0
        }
      }

      let answeredCount = 0
      for (const obj of state.objectives) {
        const ans = state.answers[obj.carreraId]
        if (ans && ans.valoracion !== null && ans.valoracion >= 1 && ans.valoracion <= 5) {
          answeredCount++
        }
      }

      const percentage = Math.min(100, Math.round((answeredCount / total) * 100))

      return {
        currentBlock: Math.max(1, Math.min(state.currentBlock, totalBlocks)),
        totalBlocks,
        answeredCount,
        totalObjectives: total,
        percentage
      }
    },

    isCurrentBlockComplete: (state): boolean => {
      const allBlocks = createObjectiveBlocks(state.objectives, OBJECTIVES_PER_BLOCK)
      if (allBlocks.length === 0) return false
      const idx = Math.max(1, Math.min(state.currentBlock, allBlocks.length))
      const currentBlockData = allBlocks[idx - 1]
      if (!currentBlockData || currentBlockData.objectives.length === 0) return false

      return currentBlockData.objectives.every((obj: NormalizedObjective) => {
        const ans = state.answers[obj.carreraId]
        if (!ans || ans.valoracion === null || ans.valoracion < 1 || ans.valoracion > 5) {
          return false
        }
        if (ans.valoracion === 5 && ans.justificacion.trim().length === 0) {
          return false
        }
        return true
      })
    },

    riasecQuestions: (state): BackendPreguntaDTO[] => {
      return state.areaData?.preguntas ?? []
    },

    riasecProgress: (state): RiasecProgress => {
      const preguntas = state.areaData?.preguntas ?? []
      const total = preguntas.length
      const answeredCount = preguntas.filter(p => {
        const answer = state.riasecAnswers[p.riasec_id]
        return (answer?.opcionIds?.length ?? 0) > 0 && (answer?.respuestaAbierta?.trim().length ?? 0) > 0
      }).length
      return {
        currentQuestion: Math.min(state.currentRiasecIndex + 1, total),
        totalQuestions: total,
        answeredCount,
        percentage: total === 0 ? 0 : Math.round((Math.min(state.currentRiasecIndex + 1, total) / total) * 100)
      }
    },

    saveUserPayload: (state): SaveUserRequestDTO => ({
      username: state.name,
      email: state.email,
      age: Number(state.age),
      area_id: state.selectedAreaId ?? 0,
      objetives: state.objectives.map(obj => ({
        id_objetive: obj.carreraId,
        puntuation: state.answers[obj.carreraId]?.valoracion ?? 0,
        description: state.answers[obj.carreraId]?.justificacion.trim() ?? ''
      })),
      risec_questions: (state.areaData?.preguntas ?? []).map(q => ({
        risec_id: q.riasec_id,
        criteria_id_list: state.riasecAnswers[q.riasec_id]?.opcionIds ?? [],
        open_question: state.riasecAnswers[q.riasec_id]?.respuestaAbierta.trim() ?? ''
      }))
    })
  },

  actions: {
    setPersonalData(data: { name: string; email: string; age: number | null; termsAccepted: boolean }) {
      this.name = data.name.trim()
      this.email = data.email.trim()
      this.age = data.age
      this.termsAccepted = data.termsAccepted
      this.persist()
    },

    selectAvatar(avatarId: string) {
      this.selectedAvatarId = avatarId
      this.persist()
    },

    selectArea(areaId: number, areaName: string) {
      if (this.selectedAreaId !== areaId) {
        this.selectedAreaId = areaId
        this.selectedAreaName = areaName
        this.areaData = null
        this.objectives = []
        this.answers = {}
        this.currentBlock = 1
        this.riasecAnswers = {}
        this.currentRiasecIndex = 0
        this.status = 'in-progress'
        this.persist()
      }
    },

    setAreaData(areaData: BackendQuestionaryResponseDTO) {
      this.areaData = areaData
      this.objectives = normalizeObjectives(areaData.objetivos)
      this.currentBlock = 1
      this.riasecAnswers = {}
      this.currentRiasecIndex = 0
      this.status = 'in-progress'
      this.persist()
    },

    setAnswer(carreraId: number, rating?: RatingValue | null, justificacion?: string) {
      const existing = this.answers[carreraId] || { valoracion: null, justificacion: '' }
      this.answers[carreraId] = {
        valoracion: rating !== undefined ? rating : existing.valoracion,
        justificacion: justificacion !== undefined ? justificacion : existing.justificacion
      }
      this.persist()
    },

    toggleRiasecOption(riasecId: number, opcionId: number) {
      const existing = this.riasecAnswers[riasecId] || { opcionIds: [], respuestaAbierta: '' }
      const opcionIds = existing.opcionIds ?? []
      this.riasecAnswers[riasecId] = {
        ...existing,
        opcionIds: opcionIds.includes(opcionId)
          ? opcionIds.filter(id => id !== opcionId)
          : [...opcionIds, opcionId]
      }
      this.persist()
    },

    setRiasecOpenAnswer(riasecId: number, respuestaAbierta: string) {
      const existing = this.riasecAnswers[riasecId] || { opcionIds: [], respuestaAbierta: '' }
      this.riasecAnswers[riasecId] = { ...existing, respuestaAbierta }
      this.persist()
    },

    goToRiasecQuestion(index: number) {
      const total = this.areaData?.preguntas?.length ?? 0
      if (index >= 0 && index < total) {
        this.currentRiasecIndex = index
        if (this.status === 'riasec-completed') this.status = 'objectives-completed'
        this.persist()
      }
    },

    nextRiasecQuestion() {
      const total = this.areaData?.preguntas?.length ?? 0
      if (this.currentRiasecIndex < total - 1) {
        this.currentRiasecIndex++
      } else {
        this.status = 'riasec-completed'
      }
      this.persist()
    },

    prevRiasecQuestion() {
      if (this.currentRiasecIndex > 0) {
        this.currentRiasecIndex--
        this.persist()
      }
    },

    goToBlock(blockNumber: number) {
      if (blockNumber >= 1 && blockNumber <= this.totalBlocks) {
        this.currentBlock = blockNumber
        this.persist()
      }
    },

    nextBlock() {
      if (this.currentBlock < this.totalBlocks) {
        this.currentBlock++
        this.persist()
      } else {
        this.status = 'objectives-completed'
        this.persist()
      }
    },

    prevBlock() {
      if (this.currentBlock > 1) {
        this.currentBlock--
        this.persist()
      }
    },

    persist() {
      if (import.meta.client) {
        try {
          const snapshot = {
            name: this.name,
            email: this.email,
            age: this.age,
            termsAccepted: this.termsAccepted,
            selectedAvatarId: this.selectedAvatarId,
            selectedAreaId: this.selectedAreaId,
            selectedAreaName: this.selectedAreaName,
            areaData: this.areaData,
            objectives: this.objectives,
            answers: this.answers,
            currentBlock: this.currentBlock,
            riasecAnswers: this.riasecAnswers,
            currentRiasecIndex: this.currentRiasecIndex,
            status: this.status
          }
          localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot))
        } catch {
        }
      }
    },

    restore() {
      if (import.meta.client) {
        try {
          const raw = localStorage.getItem(STORAGE_KEY)
          if (raw) {
            const data = JSON.parse(raw)
            this.$patch(data)
            this.clampCurrentBlock()
          }
        } catch {
          localStorage.removeItem(STORAGE_KEY)
        }
      }
    },

    clampCurrentBlock() {
      const block = Number(this.currentBlock)
      const isValid = Number.isInteger(block) && block >= 1
      this.currentBlock = isValid ? Math.min(block, Math.max(1, this.totalBlocks)) : 1
    },

    reset() {
      if (getEvaluationUuid()) return
      if (import.meta.client) {
        localStorage.removeItem(STORAGE_KEY)
        localStorage.removeItem('athena_test_submitted')
      }
      this.$reset()
    }
  }
})
