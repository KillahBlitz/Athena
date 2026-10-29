<template>
  <div class="objectives-page">
    <div class="objectives-header-row">
      <div class="objectives-title-group">
        <span class="eyebrow">
          <span>✦</span>
          <span>CADA RESPUESTA CONECTA UNA ESTRELLA</span>
        </span>
        <h1 class="page-title">¿Qué quieres para tu futuro?</h1>
        <p class="page-description">
          Valora cada objetivo y cuéntanos qué hay detrás de tu respuesta.
        </p>
      </div>

      <ObjectiveProgress :progress="progress" />
    </div>

    <!--
    <StageCelebration
      :show="isLastBlock && isCurrentBlockComplete"
      title="¡Has valorado todos los objetivos de esta área!"
      message="Tus respuestas han sido registradas. Puedes revisarlas o modificar cualquier valoración antes de la siguiente fase (RISEC)."
    >
      <BaseButton variant="outline" size="sm" @click="handleBack">
        Revisar bloques anteriores
      </BaseButton>
    </StageCelebration>
    -->

    <Transition name="onboarding-backdrop-fade">
      <div v-if="showOnboarding" class="onboarding-backdrop" @click="dismissOnboarding" />
    </Transition>

    <div class="objectives-main-row">
      <div class="objectives-cards-column">
        <!--
        <div class="objectives-block-nav">
          <button v-if="currentBlock > 1" type="button" class="block-nav-btn is-back" @click="handleBack">
            <span aria-hidden="true">←</span>
            <span>Bloque anterior</span>
          </button>
          <span class="objectives-block-nav-hint">
            Bloque {{ currentBlock }} de {{ totalBlocks }}
          </span>
          <button
            type="button"
            class="block-nav-btn is-next"
            :class="{ 'is-soft-disabled': !isCurrentBlockComplete, 'is-celebrating': isCurrentBlockComplete, 'is-finish': isLastBlock }"
            :aria-disabled="!isCurrentBlockComplete"
            @click="onNextBlock"
          >
            <span v-if="isCurrentBlockComplete" class="block-nav-sparkles" aria-hidden="true">
              <span v-for="n in 5" :key="n" class="block-nav-sparkle" :style="{ '--i': n }">✦</span>
            </span>
            <span>{{ isLastBlock ? 'Finalizar etapa' : 'Siguiente bloque' }}</span>
            <span aria-hidden="true">→</span>
          </button>
        </div>
        -->

        <ObjectiveGrid
          v-if="currentBlockData"
          :block="currentBlockData"
          :get-answer="getAnswer"
          :midpoint-pulse="midpointPulse"
          :is-first-block="currentBlock === 1"
          :is-last-block="isLastBlock"
          :block-complete="isCurrentBlockComplete"
          :confirming-finish="confirmingFinish"
          @next-block="onNextBlock"
          @prev-block="handleBack"
          @review="handleReview"
          @rating="setRating"
          @justification="setJustification"
          @leave="handleLeave"
          @revisit="handleRevisit"
        />
      </div>

      <AvatarCompanion
        ref="companion"
        class="objectives-companion"
        :avatar="selectedAvatar"
        stage="objectives"
        :complete="isCurrentBlockComplete"
        :onboarding="showOnboarding"
        :notice="notice"
        :reminder="pendingMessage"
        :answer-event="answerEvent"
        :revisit-event="revisitEvent"
        :is-last-block="isLastBlock"
        :block="currentBlock"
        :total-blocks="totalBlocks"
        :midpoint-pulse="midpointPulse"
        :confirming-finish="confirmingFinish"
        @dismiss-onboarding="dismissOnboarding"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import AvatarCompanion from '../components/avatar/AvatarCompanion.vue'
import { useObjectivesForm } from '../features/objetivos/composables/useObjectivesForm'
import ObjectiveProgress from '../features/objetivos/components/ObjectiveProgress.vue'
import ObjectiveGrid from '../features/objetivos/components/ObjectiveGrid.vue'
// import BaseButton from '../components/ui/BaseButton.vue'
// import StageCelebration from '../components/ui/StageCelebration.vue'
import { hasSeenObjectivesOnboarding, markObjectivesOnboardingSeen } from '../utils/objectivesOnboardingStorage'

useHead({
  title: 'ATHENA | Valoración de objetivos vocacionales'
})

const {
  currentBlock,
  totalBlocks,
  currentBlockData,
  selectedAvatar,
  progress,
  isCurrentBlockComplete,
  isLastBlock,
  selectedAreaId,
  getAnswer,
  setRating,
  setJustification,
  pendingMessage,
  describeSkipped,
  isPending,
  handleNext,
  handleBack,
  goToFirstBlock
} = useObjectivesForm()

const companion = ref<InstanceType<typeof AvatarCompanion> | null>(null)

const answerEvent = ref<{ rating: number, id: number } | null>(null)
let answerCount = 0

const confirmingFinish = ref(false)

watch([currentBlock, isCurrentBlockComplete], () => {
  confirmingFinish.value = false
})

function onNextBlock() {
  if (!isCurrentBlockComplete.value) {
    companion.value?.remind()
    return
  }
  if (isLastBlock.value && !confirmingFinish.value) {
    confirmingFinish.value = true
    return
  }
  handleNext()
}

function handleReview() {
  confirmingFinish.value = false
  goToFirstBlock()
}

const MIDPOINT_AREA_ID = 1

const midpointBlock = computed(() => {
  if (selectedAreaId.value !== MIDPOINT_AREA_ID || totalBlocks.value < 3) return null
  return Math.floor(totalBlocks.value / 2) + 1
})

const midpointPulse = ref(0)

watch(currentBlock, (block, previous) => {
  if (previous !== undefined && block > previous && block === midpointBlock.value) {
    midpointPulse.value++
  }
})

const skippedIds = ref<number[]>([])
const notice = computed(() => describeSkipped(skippedIds.value))

const revisitEvent = ref<{ kind: 'answered' | 'rating' | 'justification', id: number } | null>(null)

function handleRevisit(carreraId: number) {
  const answer = getAnswer(carreraId)
  const kind = answer.valoracion === null
    ? 'rating'
    : isPending(carreraId) ? 'justification' : 'answered'
  revisitEvent.value = { kind, id: ++answerCount }
}

function handleLeave(carreraId: number) {
  if (isPending(carreraId)) {
    if (!skippedIds.value.includes(carreraId)) {
      skippedIds.value = [...skippedIds.value, carreraId]
    }
    return
  }
  const rating = getAnswer(carreraId).valoracion
  if (rating !== null) answerEvent.value = { rating, id: ++answerCount }
}

const showOnboarding = ref(false)

onMounted(() => {
  showOnboarding.value = !hasSeenObjectivesOnboarding()
})

function dismissOnboarding() {
  showOnboarding.value = false
  markObjectivesOnboardingSeen()
}
</script>

<style scoped>
@import '../features/objetivos/styles/objectives.css';

.onboarding-backdrop {
  position: fixed;
  inset: 0;
  z-index: 55;
  background: rgba(15, 15, 25, 0.45);
}

.onboarding-backdrop-fade-enter-active,
.onboarding-backdrop-fade-leave-active {
  transition: opacity 220ms ease;
}
.onboarding-backdrop-fade-enter-from,
.onboarding-backdrop-fade-leave-to {
  opacity: 0;
}
</style>
