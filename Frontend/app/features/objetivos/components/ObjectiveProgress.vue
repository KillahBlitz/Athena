<template>
  <div class="objectives-progress-widget" role="region" aria-label="Progreso de objetivos">
    <!-- Constellation lines art -->
    <svg class="constellation-art" viewBox="0 0 140 48" fill="none" aria-hidden="true">
      <line class="constellation-line is-soft" x1="12" y1="36" x2="42" y2="20" stroke-width="1.5" stroke-dasharray="2 2" />
      <line class="constellation-line" x1="42" y1="20" x2="84" y2="8" stroke-width="1.8" />
      <line class="constellation-line" x1="84" y1="8" x2="128" y2="16" stroke-width="1.8" />
      <line class="constellation-line is-soft" x1="128" y1="16" x2="110" y2="38" stroke-width="1.5" />
      <line class="constellation-line is-soft" x1="110" y1="38" x2="84" y2="8" stroke-width="1.5" stroke-dasharray="2 2" />

      <circle class="constellation-star is-soft" cx="12" cy="36" r="3" />
      <circle class="constellation-star" cx="42" cy="20" r="3.5" />
      <circle class="constellation-star is-bright" cx="84" cy="8" r="4.5" />
      <circle class="constellation-star is-bright" cx="128" cy="16" r="4" />
      <circle class="constellation-star" cx="110" cy="38" r="3.5" />
    </svg>

    <div class="progress-labels-row">
      <span>Bloque {{ progress.currentBlock }} de {{ progress.totalBlocks }}</span>
      <span>{{ progress.percentage }} % completado</span>
    </div>

    <div
      class="progress-track"
      role="progressbar"
      :aria-valuenow="progress.percentage"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`Progreso: ${progress.percentage}% completado`"
    >
      <div class="progress-fill" :style="{ width: `${progress.percentage}%` }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ObjectivesProgress } from '../../../types/objective'

defineProps<{
  progress: ObjectivesProgress
}>()
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
