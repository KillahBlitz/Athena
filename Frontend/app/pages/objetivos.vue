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

    <ObjectiveGrid
      v-if="currentBlockData"
      :block="currentBlockData"
      :get-answer="getAnswer"
      @rating="setRating"
      @justification="setJustification"
    />

    <StageCelebration
      :show="isLastBlock && isCurrentBlockComplete"
      title="¡Has valorado todos los objetivos de esta área!"
      message="Tus respuestas han sido registradas. Puedes revisarlas o modificar cualquier valoración antes de la siguiente fase (RISEC)."
    >
      <BaseButton variant="outline" size="sm" @click="handleBack">
        Revisar bloques anteriores
      </BaseButton>
    </StageCelebration>

    <AvatarCompanion
      :key="currentBlockData?.blockIndex"
      :avatar="selectedAvatar"
      stage="objectives"
      :complete="isCurrentBlockComplete"
    />

    <div class="objectives-bottom-bar">
      <div class="bottom-actions-group">
        <button type="button" class="back-text-btn" @click="handleBack">
          <span aria-hidden="true">←</span>
          <span>Atrás</span>
        </button>

        <BaseButton
          variant="primary"
          size="md"
          :disabled="!isCurrentBlockComplete"
          @click="handleNext"
        >
          <span>{{ isLastBlock ? 'Finalizar etapa' : 'Siguiente' }}</span>
          <template #suffix>
            <span aria-hidden="true">→</span>
          </template>
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AvatarCompanion from '../components/avatar/AvatarCompanion.vue'
import { useObjectivesForm } from '../features/objetivos/composables/useObjectivesForm'
import ObjectiveProgress from '../features/objetivos/components/ObjectiveProgress.vue'
import ObjectiveGrid from '../features/objetivos/components/ObjectiveGrid.vue'
import BaseButton from '../components/ui/BaseButton.vue'
import StageCelebration from '../components/ui/StageCelebration.vue'

useHead({
  title: 'ATHENA | Valoración de objetivos vocacionales'
})

const {
  currentBlockData,
  selectedAvatar,
  progress,
  isCurrentBlockComplete,
  isLastBlock,
  getAnswer,
  setRating,
  setJustification,
  handleNext,
  handleBack
} = useObjectivesForm()
</script>

<style scoped>
@import '../features/objetivos/styles/objectives.css';

.bottom-actions-group {
  width: 100%;
}
</style>
