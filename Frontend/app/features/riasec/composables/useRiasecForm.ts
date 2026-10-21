import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAthenaSessionStore } from '../../../stores/athenaSession'
import type { BackendPreguntaDTO } from '../../../types/area'
import type { Avatar } from '../../../types/avatar'
import type { RiasecAnswer, RiasecDimension, RiasecOption, RiasecProgress } from '../../../types/riasec'
import { getRiasecDimension } from '../config/riasecDimensions'

export interface RiasecTab {
  index: number
  dimension: RiasecDimension
  isCurrent: boolean
  isAnswered: boolean
  isReachable: boolean
}

export function useRiasecForm() {
  const router = useRouter()
  const session = useAthenaSessionStore()

  onMounted(() => {
    session.restore()
    // Without questionary data the user skipped the previous steps
    if (session.objectives.length === 0 || session.riasecQuestions.length === 0) {
      router.replace('/datos-personales')
    }
  })

  const getAnswerFor = (riasecId: number): RiasecAnswer => {
    const ans = session.riasecAnswers[riasecId]
    return { opcionIds: ans?.opcionIds ?? [], respuestaAbierta: ans?.respuestaAbierta ?? '' }
  }

  const questions = computed<BackendPreguntaDTO[]>(() => session.riasecQuestions)
  const currentIndex = computed<number>(() => session.currentRiasecIndex)
  const currentQuestion = computed<BackendPreguntaDTO | null>(() => questions.value[currentIndex.value] ?? null)
  const currentDimension = computed<RiasecDimension>(() => getRiasecDimension(currentQuestion.value?.riasec_id ?? 0))
  const nextDimension = computed<RiasecDimension | null>(() => {
    const next = questions.value[currentIndex.value + 1]
    return next ? getRiasecDimension(next.riasec_id) : null
  })
  const currentOptions = computed<RiasecOption[]>(() => {
    if (!currentQuestion.value) return []
    return Object.entries(currentQuestion.value.opciones).map(([id, texto]) => ({
      opcionId: Number(id),
      texto
    }))
  })
  const currentAnswer = computed<RiasecAnswer>(() => getAnswerFor(currentQuestion.value?.riasec_id ?? -1))

  // A dimension is reachable once every previous one has at least one selection
  const tabs = computed<RiasecTab[]>(() => {
    let reachable = true
    return questions.value.map((q, index) => {
      const isAnswered = getAnswerFor(q.riasec_id).opcionIds.length > 0
      const tab = {
        index,
        dimension: getRiasecDimension(q.riasec_id),
        isCurrent: index === currentIndex.value,
        isAnswered,
        isReachable: reachable
      }
      reachable = reachable && isAnswered
      return tab
    })
  })

  const selectedAvatar = computed<Avatar>(() => session.selectedAvatar)
  const progress = computed<RiasecProgress>(() => session.riasecProgress)
  const isCurrentComplete = computed<boolean>(() => currentAnswer.value.opcionIds.length > 0)
  const isLastQuestion = computed<boolean>(() => currentIndex.value === questions.value.length - 1)
  const isCompleted = computed<boolean>(() => session.status === 'riasec-completed')

  const scrollTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

  const toggleOption = (opcionId: number) => {
    if (!currentQuestion.value) return
    session.toggleRiasecOption(currentQuestion.value.riasec_id, opcionId)
  }

  const setOpenAnswer = (text: string) => {
    if (!currentQuestion.value) return
    session.setRiasecOpenAnswer(currentQuestion.value.riasec_id, text)
  }

  const goToDimension = (index: number) => {
    if (!tabs.value[index]?.isReachable) return
    session.goToRiasecQuestion(index)
  }

  const handleNext = () => {
    if (!isCurrentComplete.value) return
    session.nextRiasecQuestion()
    scrollTop()
  }

  const handleBack = () => {
    if (isCompleted.value) {
      session.goToRiasecQuestion(currentIndex.value)
      return
    }
    if (currentIndex.value > 0) {
      session.prevRiasecQuestion()
      scrollTop()
    } else {
      router.push('/objetivos')
    }
  }

  return {
    tabs,
    currentQuestion,
    currentDimension,
    nextDimension,
    currentOptions,
    currentAnswer,
    selectedAvatar,
    progress,
    isCurrentComplete,
    isLastQuestion,
    isCompleted,
    toggleOption,
    setOpenAnswer,
    goToDimension,
    handleNext,
    handleBack
  }
}
