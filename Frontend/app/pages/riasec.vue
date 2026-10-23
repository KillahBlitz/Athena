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

    <RiasecDimensionTabs :tabs="tabs" @select="goToDimension" />

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

    <ErrorMessage
      v-if="isCompleted && submitError"
      class="riasec-submit-error"
      :message="submitError"
      retryable
      @retry="handleFinish"
    />

    <template v-if="!isCompleted && currentQuestion">
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
              @toggle="toggleOption"
            />

            <div class="riasec-side">
              <RiasecConnectionsPanel
                :options="currentOptions"
                :selected-ids="currentAnswer.opcionIds"
                :avatar="selectedAvatar"
              />
              <AvatarStoryCard
                :avatar="selectedAvatar"
                :riasec-id="currentQuestion.riasec_id"
                :selected-count="currentAnswer.opcionIds.length"
              />
            </div>
          </div>

          <RiasecReflection
            :riasec-id="currentQuestion.riasec_id"
            :dimension-name="currentDimension.name"
            :question="currentQuestion.pregunta_abierta"
            :model-value="currentAnswer.respuestaAbierta"
            :locked="currentAnswer.opcionIds.length === 0"
            @update:model-value="setOpenAnswer"
          />
          <AvatarCompanion :avatar="selectedAvatar" stage="riasec" :complete="isCurrentComplete" />
        </Motion>
      </AnimatePresence>
    </template>

    <div v-if="!isCompleted" class="riasec-bottom-bar">
      <button type="button" class="back-text-btn" @click="handleBack">
        <span aria-hidden="true">←</span>
        <span>Atrás</span>
      </button>

      <span class="riasec-next-hint">
        {{ nextDimension ? `A continuación: ${nextDimension.name}` : 'Última dimensión' }}
      </span>

      <BaseButton
        variant="primary"
        size="lg"
        :disabled="!isCurrentComplete"
        @click="handleNext"
      >
        <span>{{ isLastQuestion ? 'Finalizar etapa' : 'Siguiente' }}</span>
        <template #suffix>
          <span aria-hidden="true">→</span>
        </template>
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import AvatarCompanion from '../components/avatar/AvatarCompanion.vue'
import { useRiasecForm } from '../features/riasec/composables/useRiasecForm'
import RiasecDimensionTabs from '../features/riasec/components/RiasecDimensionTabs.vue'
import RiasecQuestionCard from '../features/riasec/components/RiasecQuestionCard.vue'
import RiasecConnectionsPanel from '../features/riasec/components/RiasecConnectionsPanel.vue'
import RiasecReflection from '../features/riasec/components/RiasecReflection.vue'
import AvatarStoryCard from '../features/riasec/components/AvatarStoryCard.vue'
import BaseButton from '../components/ui/BaseButton.vue'
import StageCelebration from '../components/ui/StageCelebration.vue'
import ErrorMessage from '../components/ui/ErrorMessage.vue'
import { useMotionPresets } from '../composables/useMotionPresets'

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
  selectedAvatar,
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
} = useRiasecForm()

const presets = useMotionPresets()
</script>

<style scoped>
@import '../features/objetivos/styles/objectives.css';
@import '../features/riasec/styles/riasec.css';
</style>
