<template>
  <div class="riasec-page">
    <!-- Header Row -->
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

    <div v-if="isCompleted" class="stage-completion-box" role="status">
      <div class="stage-completion-text">
        <h3>✦ ¡Has explorado todas las dimensiones!</h3>
        <p>Tus habilidades y reflexiones han sido registradas. Puedes revisarlas antes de ver tus resultados.</p>
      </div>
      <BaseButton variant="outline" size="sm" @click="handleBack">
        Revisar respuestas
      </BaseButton>
    </div>

    <template v-else-if="currentQuestion">
      <div class="riasec-main-grid">
        <RiasecQuestionCard
          :key="currentQuestion.riasec_id"
          :question="currentQuestion"
          :dimension="currentDimension"
          :options="currentOptions"
          :answer="currentAnswer"
          @toggle="toggleOption"
        />

        <RiasecConnectionsPanel
          :options="currentOptions"
          :selected-ids="currentAnswer.opcionIds"
          :avatar="selectedAvatar"
        />
      </div>

      <RiasecReflection
        :key="`reflection-${currentQuestion.riasec_id}`"
        :riasec-id="currentQuestion.riasec_id"
        :dimension-name="currentDimension.name"
        :question="currentQuestion.pregunta_abierta"
        :model-value="currentAnswer.respuestaAbierta"
        :locked="!isCurrentComplete"
        @update:model-value="setOpenAnswer"
      />
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
import { useRiasecForm } from '../features/riasec/composables/useRiasecForm'
import RiasecDimensionTabs from '../features/riasec/components/RiasecDimensionTabs.vue'
import RiasecQuestionCard from '../features/riasec/components/RiasecQuestionCard.vue'
import RiasecConnectionsPanel from '../features/riasec/components/RiasecConnectionsPanel.vue'
import RiasecReflection from '../features/riasec/components/RiasecReflection.vue'
import BaseButton from '../components/ui/BaseButton.vue'

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
  toggleOption,
  setOpenAnswer,
  goToDimension,
  handleNext,
  handleBack
} = useRiasecForm()
</script>

<style scoped>
@import '../features/objetivos/styles/objectives.css';
@import '../features/riasec/styles/riasec.css';
</style>
