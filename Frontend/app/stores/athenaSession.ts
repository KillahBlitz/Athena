import { defineStore } from 'pinia'
import type { BackendQuestionaryResponseDTO } from '../types/area'
import type { NormalizedObjective, ObjectiveBlock, RatingValue, ObjectivesProgress } from '../types/objective'
import type { PersonalData } from '../types/session'
import type { Avatar } from '../types/avatar'
import { AVATARS, DEFAULT_AVATAR } from '../config/avatars'
import { createObjectiveBlocks, normalizeObjectives } from '../features/objetivos/utils/createObjectiveBlocks'

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
    status: 'idle' as 'idle' | 'in-progress' | 'objectives-completed'
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
      return createObjectiveBlocks(state.objectives, 4)
    },

    totalBlocks: (state): number => {
      return Math.ceil(state.objectives.length / 4)
    },

    currentBlockData: (state): ObjectiveBlock | null => {
      const allBlocks = createObjectiveBlocks(state.objectives, 4)
      if (allBlocks.length === 0) return null
      const idx = Math.max(1, Math.min(state.currentBlock, allBlocks.length))
      return allBlocks[idx - 1] || null
    },

    progress: (state): ObjectivesProgress => {
      const total = state.objectives.length
      const totalBlocks = Math.ceil(total / 4)
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
        currentBlock: state.currentBlock,
        totalBlocks,
        answeredCount,
        totalObjectives: total,
        percentage
      }
    },

    isCurrentBlockComplete: (state): boolean => {
      const allBlocks = createObjectiveBlocks(state.objectives, 4)
      if (allBlocks.length === 0) return false
      const idx = Math.max(1, Math.min(state.currentBlock, allBlocks.length))
      const currentBlockData = allBlocks[idx - 1]
      if (!currentBlockData || currentBlockData.objectives.length === 0) return false

      return currentBlockData.objectives.every((obj: NormalizedObjective) => {
        const ans = state.answers[obj.carreraId]
        return ans && ans.valoracion !== null && ans.valoracion >= 1 && ans.valoracion <= 5
      })
    }
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
        // Changing area: discard previous area objectives and answers
        this.selectedAreaId = areaId
        this.selectedAreaName = areaName
        this.areaData = null
        this.objectives = []
        this.answers = {}
        this.currentBlock = 1
        this.status = 'in-progress'
        this.persist()
      }
    },

    setAreaData(areaData: BackendQuestionaryResponseDTO) {
      this.areaData = areaData
      this.objectives = normalizeObjectives(areaData.objetivos)
      this.currentBlock = 1
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

    goToBlock(blockNumber: number) {
      const total = Math.ceil(this.objectives.length / 4)
      if (blockNumber >= 1 && blockNumber <= total) {
        this.currentBlock = blockNumber
        this.persist()
      }
    },

    nextBlock() {
      const total = Math.ceil(this.objectives.length / 4)
      if (this.currentBlock < total) {
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
            status: this.status
          }
          localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot))
        } catch {
          // ignore storage quota issues
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
          }
        } catch {
          localStorage.removeItem(STORAGE_KEY)
        }
      }
    },

    reset() {
      if (import.meta.client) {
        localStorage.removeItem(STORAGE_KEY)
      }
      this.$reset()
    }
  }
})
