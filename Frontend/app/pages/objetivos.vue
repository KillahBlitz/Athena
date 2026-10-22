<template>
  <div class="objectives-page">
    <!-- Header Row -->
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

      <!-- Progress Tracker -->
      <ObjectiveProgress :progress="progress" />
    </div>

    <!-- Active Block Grid (up to OBJECTIVES_PER_BLOCK questions) -->
    <ObjectiveGrid
      v-if="currentBlockData"
      :block="currentBlockData"
      :get-answer="getAnswer"
      @rating="setRating"
      @justification="setJustification"
    />

    <!-- Informative completion banner when all blocks are finished -->
    <StageCelebration
      :show="isLastBlock && isCurrentBlockComplete"
      title="¡Has valorado todos los objetivos de esta área!"
      message="Tus respuestas han sido registradas. Puedes revisarlas o modificar cualquier valoración antes de la siguiente fase (RISEC)."
    >
      <BaseButton variant="outline" size="sm" @click="handleBack">
        Revisar bloques anteriores
      </BaseButton>
    </StageCelebration>

    <!-- Bottom Navigation Bar matching Image 3 -->
    <div class="objectives-bottom-bar">
      <!-- Left: Companion Avatar Guidance -->
      <div class="bottom-avatar-speech" role="note">
        <div class="bottom-avatar-img" aria-hidden="true">
          <img :src="selectedAvatar.image" alt="">
        </div>
        <div class="bottom-avatar-text">
          <span class="bottom-avatar-name">{{ selectedAvatar.name }} · </span>
          <span>{{ selectedAvatar.encouragement }}</span>
        </div>
      </div>

      <!-- Right: Navigation Buttons -->
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
</style>
