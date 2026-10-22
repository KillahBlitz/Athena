import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAthenaSessionStore } from '../../../stores/athenaSession'
import type { RatingValue, ObjectiveBlock, ObjectivesProgress } from '../../../types/objective'
import type { Avatar } from '../../../types/avatar'

export function useObjectivesForm() {
  const router = useRouter()
  const session = useAthenaSessionStore()

  onMounted(() => {
    session.restore()
    if (session.objectives.length === 0) {
      router.replace('/datos-personales')
    }
  })

  const currentBlock = computed<number>(() => session.currentBlock)
  const totalBlocks = computed<number>(() => session.totalBlocks)
  const currentBlockData = computed<ObjectiveBlock | null>(() => session.currentBlockData)
  const selectedAvatar = computed<Avatar>(() => session.selectedAvatar)
  const progress = computed<ObjectivesProgress>(() => session.progress)
  const isCurrentBlockComplete = computed<boolean>(() => session.isCurrentBlockComplete)
  const isLastBlock = computed<boolean>(() => session.currentBlock === session.totalBlocks)
  const isAllCompleted = computed<boolean>(() => session.progress.answeredCount === session.objectives.length && session.objectives.length > 0)

  const getAnswer = (carreraId: number) => {
    return session.answers[carreraId] || { valoracion: null, justificacion: '' }
  }

  const setRating = (carreraId: number, rating: RatingValue) => {
    session.setAnswer(carreraId, rating)
  }

  const setJustification = (carreraId: number, text: string) => {
    session.setAnswer(carreraId, undefined, text)
  }

  const handleNext = () => {
    if (!isCurrentBlockComplete.value) return

    if (currentBlock.value < totalBlocks.value) {
      session.nextBlock()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      session.status = 'objectives-completed'
      session.persist()
      router.push('/riasec')
    }
  }

  const handleBack = () => {
    if (currentBlock.value > 1) {
      session.prevBlock()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      router.push('/datos-personales')
    }
  }

  return {
    currentBlock,
    totalBlocks,
    currentBlockData,
    selectedAvatar,
    progress,
    isCurrentBlockComplete,
    isLastBlock,
    isAllCompleted,
    getAnswer,
    setRating,
    setJustification,
    handleNext,
    handleBack
  }
}
