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

  // Whether the user has already rated at least one objective in the current
  // block. Used only to decide which message the avatar companion shows.
  const hasStartedCurrentBlock = computed<boolean>(() => {
    const block = currentBlockData.value
    if (!block) return false
    return block.objectives.some((objective) => getAnswer(objective.carreraId).valoracion !== null)
  })

  type PendingReason = 'rating' | 'justification'

  const getPendingReason = (carreraId: number): PendingReason | null => {
    const answer = getAnswer(carreraId)
    if (answer.valoracion === null) return 'rating'
    if (answer.valoracion === 5 && answer.justificacion.trim().length === 0) return 'justification'
    return null
  }

  const joinNumbers = (numbers: number[]) =>
    numbers.length > 1 ? `${numbers.slice(0, -1).join(', ')} y ${numbers[numbers.length - 1]}` : String(numbers[0])

  const pendingNumbers = (ids?: number[]) => {
    const objectives = currentBlockData.value?.objectives ?? []
    const result: Record<PendingReason, number[]> = { rating: [], justification: [] }
    objectives.forEach((objective, index) => {
      if (ids && !ids.includes(objective.carreraId)) return
      const reason = getPendingReason(objective.carreraId)
      if (reason) result[reason].push(index + 1)
    })
    return result
  }

  const buildMessage = (
    pending: Record<PendingReason, number[]>,
    rating: (numbers: string, plural: boolean) => string,
    justification: (numbers: string, plural: boolean) => string
  ) => {
    const parts: string[] = []
    if (pending.rating.length) parts.push(rating(joinNumbers(pending.rating), pending.rating.length > 1))
    if (pending.justification.length) parts.push(justification(joinNumbers(pending.justification), pending.justification.length > 1))
    return parts.join(' ')
  }

  const pendingMessage = computed(() => buildMessage(
    pendingNumbers(),
    (numbers, plural) => plural ? `Te faltan las preguntas ${numbers}.` : `Te falta la pregunta ${numbers}.`,
    (numbers, plural) => plural
      ? `Las preguntas ${numbers} son de explicación y falta tu justificación.`
      : `La pregunta ${numbers} es de explicación y falta tu justificación.`
  ))

  const describeSkipped = (ids: number[]) => buildMessage(
    pendingNumbers(ids),
    (numbers, plural) => plural ? `Pasaste las preguntas ${numbers}.` : `Pasaste la pregunta ${numbers}.`,
    (numbers, plural) => plural
      ? `Pasaste las preguntas ${numbers}, que son de explicación.`
      : `Pasaste la pregunta ${numbers}, que es de explicación.`
  )

  const isPending = (carreraId: number) => getPendingReason(carreraId) !== null
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
    hasStartedCurrentBlock,
    pendingMessage,
    describeSkipped,
    isPending,
    isLastBlock,
    isAllCompleted,
    getAnswer,
    setRating,
    setJustification,
    handleNext,
    handleBack
  }
}
