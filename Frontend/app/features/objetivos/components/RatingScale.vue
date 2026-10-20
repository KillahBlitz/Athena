<template>
  <div class="rating-section">
    <span :id="`rating-label-${carreraId}`" class="rating-question-label">
      ¿Qué tanto te identificas con este objetivo?
    </span>

    <div
      class="rating-buttons-row"
      role="radiogroup"
      :aria-labelledby="`rating-label-${carreraId}`"
    >
      <button
        v-for="val in 5"
        :key="val"
        type="button"
        role="radio"
        class="rating-btn"
        :class="{ 'is-selected': modelValue === val }"
        :aria-checked="modelValue === val"
        :aria-label="`Valoración ${val} de 5`"
        @click="$emit('update:modelValue', val as RatingValue)"
      >
        <span v-if="modelValue === val" class="rating-star-icon" aria-hidden="true">✦</span>
        <span>{{ val }}</span>
      </button>
    </div>

    <div class="rating-legend-row" aria-hidden="true">
      <span>1 · Totalmente en desacuerdo</span>
      <span>5 · Totalmente de acuerdo</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RatingValue } from '../../../types/objective'

defineProps<{
  carreraId: number
  modelValue: RatingValue | null
}>()

defineEmits<{
  'update:modelValue': [value: RatingValue]
}>()
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
