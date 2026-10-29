<template>
  <div class="riasec-page">
    <div class="objectives-header-row">
      <div class="objectives-title-group">
        <span class="eyebrow">
          <span>✦</span>
          <span>EXPLORA TUS HABILIDADES · RISEC</span>
        </span>
        <h1 class="page-title">Tu curiosidad también es una señal.</h1>
        <p class="page-description">
          Explora una dimensión a la vez y reconoce lo que se te da bien.
        </p>
      </div>

      <div class="riasec-progress" role="region" aria-label="Progreso RISEC">
        <div class="progress-labels-row">
          <span>Dimensión {{ progress.currentQuestion }} de {{ progress.totalQuestions }}</span>
          <span class="riasec-progress-dimension">{{ currentDimension.name }}</span>
        </div>
        <div
          class="progress-track"
          role="progressbar"
          :aria-valuenow="progress.percentage"
          aria-valuemin="0"
          aria-valuemax="100"
          :aria-label="`Progreso: ${progress.percentage}%`"
        >
          <div class="progress-fill" :style="{ width: `${progress.percentage}%` }" />
        </div>
      </div>
    </div>

    <Transition name="onboarding-backdrop-fade">
      <div v-if="showOnboarding" class="onboarding-backdrop" @click="dismissOnboarding" />
    </Transition>

    <RiasecDimensionTabs :tabs="tabs" @select="goToDimension" />

    <!--
    <StageCelebration
      :show="isCompleted"
      title="¡Has explorado todas las dimensiones!"
      message="Tus habilidades y reflexiones están listas. Revísalas o finaliza el test para enviar tus resultados."
    >
      <BaseButton variant="outline" size="sm" :disabled="isSubmitting" @click="handleBack">
        Revisar respuestas
      </BaseButton>
      <BaseButton variant="primary" size="sm" :loading="isSubmitting" @click="handleFinish">
        <span>{{ isSubmitting ? 'Guardando...' : 'Finalizar' }}</span>
        <template v-if="!isSubmitting" #suffix>
          <span aria-hidden="true">→</span>
        </template>
      </BaseButton>
    </StageCelebration>
    -->

    <ErrorMessage
      v-if="submitError"
      class="riasec-submit-error"
      :message="submitError"
      retryable
      @retry="handleFinish"
    />

    <template v-if="currentQuestion">
      <AnimatePresence mode="wait" :initial="false">
        <Motion
          :key="currentQuestion.riasec_id"
          class="riasec-dimension"
          :initial="presets.swap.initial"
          :animate="presets.swap.animate"
          :exit="presets.swap.exit"
          :transition="presets.swap.transition"
        >
          <div class="riasec-main-grid">
            <RiasecQuestionCard
              :question="currentQuestion"
              :dimension="currentDimension"
              :options="currentOptions"
              :answer="currentAnswer"
              :selection-limit="selectionLimit"
              :is-selection-limit-reached="isSelectionLimitReached"
              :block-size="optionBlockSize"
              :block-columns="optionBlockColumns"
              @toggle="toggleOption"
            >
              <RiasecReflection
                :riasec-id="currentQuestion.riasec_id"
                :dimension-name="currentDimension.name"
                :question="currentQuestion.pregunta_abierta"
                :model-value="currentAnswer.respuestaAbierta"
                :locked="currentAnswer.opcionIds.length === 0"
                @update:model-value="setOpenAnswer"
              />

              <template #footer>
                <div class="objectives-block-nav riasec-dimension-nav">
                  <button type="button" class="block-nav-btn is-back" :class="{ 'is-attention': confirmingFinish }" @click="handleBack">
                    <span aria-hidden="true">←</span>
                    <span>Atrás</span>
                  </button>
                  <span class="objectives-block-nav-hint">
                    {{ nextDimension ? `A continuación: ${nextDimension.name}` : 'Última dimensión' }}
                  </span>
                  <button
                    type="button"
                    class="block-nav-btn is-next"
                    :class="{ 'is-soft-disabled': !isCurrentComplete || isSubmitting, 'is-celebrating': isCurrentComplete && !isSubmitting, 'is-finish': isLastQuestion }"
                    :aria-disabled="!isCurrentComplete || isSubmitting"
                    :aria-busy="isSubmitting"
                    @click="onNextDimension"
                  >
                    <span v-if="isCurrentComplete && !isSubmitting" class="block-nav-sparkles" aria-hidden="true">
                      <span v-for="n in 5" :key="n" class="block-nav-sparkle" :style="{ '--i': n }">✦</span>
                    </span>
                    <span>{{ isSubmitting ? 'Guardando...' : isLastQuestion ? (confirmingFinish ? 'Sí, quiero finalizar' : 'Finalizar etapa') : 'Siguiente' }}</span>
                    <span v-if="!isSubmitting" aria-hidden="true">→</span>
                  </button>
                </div>
              </template>
            </RiasecQuestionCard>

            <div class="riasec-side">
              <RiasecConnectionsPanel
                :options="currentOptions"
                :selected-ids="currentAnswer.opcionIds"
              />
              <AvatarStoryCard
                ref="storyCard"
                :avatar="selectedAvatar"
                :riasec-id="currentQuestion.riasec_id"
                :selected-count="currentAnswer.opcionIds.length"
                :selection-limit="selectionLimit"
                :stage-complete="isLastQuestion && isCurrentComplete"
                :is-last-dimension="isLastQuestion"
                :confirming-finish="confirmingFinish"
              />
            </div>
          </div>
        </Motion>
      </AnimatePresence>

      <AvatarCompanion
        v-if="showOnboarding"
        :avatar="selectedAvatar"
        stage="riasec"
        :complete="isCurrentComplete"
        :onboarding="showOnboarding"
        @dismiss-onboarding="dismissOnboarding"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import AvatarCompanion from '../components/avatar/AvatarCompanion.vue'
import { useRiasecForm } from '../features/riasec/composables/useRiasecForm'
import RiasecDimensionTabs from '../features/riasec/components/RiasecDimensionTabs.vue'
import RiasecQuestionCard from '../features/riasec/components/RiasecQuestionCard.vue'
import RiasecConnectionsPanel from '../features/riasec/components/RiasecConnectionsPanel.vue'
import RiasecReflection from '../features/riasec/components/RiasecReflection.vue'
import AvatarStoryCard from '../features/riasec/components/AvatarStoryCard.vue'
// import BaseButton from '../components/ui/BaseButton.vue'
// import StageCelebration from '../components/ui/StageCelebration.vue'
import ErrorMessage from '../components/ui/ErrorMessage.vue'
import { useMotionPresets } from '../composables/useMotionPresets'
import { hasSeenRiasecOnboarding, markRiasecOnboardingSeen } from '../utils/riasecOnboardingStorage'

useHead({
  title: 'ATHENA | Perfil RISEC'
})

const {
  tabs,
  currentQuestion,
  currentDimension,
  nextDimension,
  currentOptions,
  currentAnswer,
  selectionLimit,
  isSelectionLimitReached,
  selectedAvatar,
  optionBlockSize,
  optionBlockColumns,
  progress,
  isCurrentComplete,
  isLastQuestion,
  isSubmitting,
  submitError,
  toggleOption,
  setOpenAnswer,
  goToDimension,
  handleNext,
  handleFinish,
  handleBack
} = useRiasecForm()

const presets = useMotionPresets()

const storyCard = ref<InstanceType<typeof AvatarStoryCard> | null>(null)

const confirmingFinish = ref(false)

watch(() => [currentQuestion.value?.riasec_id, isCurrentComplete.value], () => {
  confirmingFinish.value = false
})

function onNextDimension() {
  if (isSubmitting.value) return
  if (isCurrentComplete.value && isLastQuestion.value && !confirmingFinish.value) {
    confirmingFinish.value = true
    return
  }
  if (isCurrentComplete.value) {
    handleNext()
    return
  }
  storyCard.value?.remind(currentAnswer.value.opcionIds.length === 0 ? 'skills' : 'reflection')
}

const showOnboarding = ref(false)

onMounted(() => {
  showOnboarding.value = !hasSeenRiasecOnboarding()
})

function dismissOnboarding() {
  showOnboarding.value = false
  markRiasecOnboardingSeen()
}
</script>

<style scoped>
@import '../features/objetivos/styles/objectives.css';
@import '../features/riasec/styles/riasec.css';

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
