import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAthenaSessionStore } from '../../../stores/athenaSession'
import type { BackendPreguntaDTO } from '../../../types/area'
import type { Avatar } from '../../../types/avatar'
import type { RiasecAnswer, RiasecDimension, RiasecOption, RiasecProgress } from '../../../types/riasec'
import { getRiasecDimension } from '../config/riasecDimensions'
import { MAX_CRITERIOS_POR_DIMENSION } from '../../../config/riasec'
import { useSaveUserApi } from '../../../composables/useSaveUserApi'
import { getEvaluationUuid, saveEvaluationUuid } from '../../../utils/evaluationStorage'

const BLOCKED_OPTIONS_AREA_ID = 1
const OPTION_BLOCK_SIZE = 9
const OPTION_BLOCK_COLUMNS = 3

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
  const { saveUser } = useSaveUserApi()
  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)

  onMounted(() => {
    session.restore()
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
  const isSelectionLimitReached = computed<boolean>(
    () => currentAnswer.value.opcionIds.length >= MAX_CRITERIOS_POR_DIMENSION
  )

  const tabs = computed<RiasecTab[]>(() => {
    let reachable = true
    return questions.value.map((q, index) => {
      const answer = getAnswerFor(q.riasec_id)
      const isAnswered = answer.opcionIds.length > 0 && answer.respuestaAbierta.trim().length > 0
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
  const optionBlockSize = computed<number>(() => session.selectedAreaId === BLOCKED_OPTIONS_AREA_ID ? OPTION_BLOCK_SIZE : 0)
  const optionBlockColumns = computed<number>(() => session.selectedAreaId === BLOCKED_OPTIONS_AREA_ID ? OPTION_BLOCK_COLUMNS : 0)
  const progress = computed<RiasecProgress>(() => session.riasecProgress)
  const isCurrentComplete = computed<boolean>(() =>
    currentAnswer.value.opcionIds.length > 0 && currentAnswer.value.respuestaAbierta.trim().length > 0
  )
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
    if (isLastQuestion.value) {
      handleFinish()
      return
    }
    session.nextRiasecQuestion()
    scrollTop()
  }

  const findMissingData = (): string | null => {
    const payload = session.saveUserPayload
    if (!payload.username || !payload.email || !Number.isInteger(payload.age) || !payload.area_id) {
      return 'Faltan tus datos personales (nombre, correo, edad o área). Complétalos en "Datos personales".'
    }
    const unrated = payload.objetives.filter(obj => obj.puntuation < 1 || obj.puntuation > 5).length
    if (unrated > 0) {
      return `Tienes ${unrated} objetivo${unrated === 1 ? '' : 's'} sin valorar. Complétalos en "Objetivos".`
    }
    const riasecQuestions = Object.values(payload.risec_questions)
    if (riasecQuestions.some(q => q.criteria_list.length === 0)) {
      return 'Hay dimensiones RISEC sin ninguna habilidad seleccionada.'
    }
    if (riasecQuestions.some(q => !q.open_question.trim())) {
      return 'Responde la pregunta abierta de cada dimensión RISEC antes de finalizar.'
    }
    return null
  }

  const handleFinish = async () => {
    if (isSubmitting.value) return
    if (getEvaluationUuid()) {
      await router.replace('/espera')
      return
    }
    submitError.value = findMissingData()
    if (submitError.value) return
    isSubmitting.value = true
    try {
      const uuid = await saveUser(session.saveUserPayload)
      saveEvaluationUuid(uuid)
      await router.push('/espera')
    } catch (err) {
      submitError.value = (err as { message?: string }).message ?? 'No fue posible guardar tus resultados.'
    } finally {
      isSubmitting.value = false
    }
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
    selectionLimit: MAX_CRITERIOS_POR_DIMENSION,
    isSelectionLimitReached,
    selectedAvatar,
    optionBlockSize,
    optionBlockColumns,
    progress,
    isCurrentComplete,
    isLastQuestion,
    isCompleted,
    isSubmitting,
    submitError,
    toggleOption,
    setOpenAnswer,
    goToDimension,
    handleNext,
    handleFinish,
    handleBack
  }
}
