<template>
  <div class="rating-section">
    <div
      class="rating-buttons-row"
      role="radiogroup"
      aria-label="¿Qué tanto te identificas con este objetivo?"
    >
      <Motion
        v-for="val in 5"
        :key="val"
        as="button"
        type="button"
        role="radio"
        class="rating-btn"
        :class="{ 'is-selected': modelValue === val }"
        :aria-checked="modelValue === val"
        :aria-label="`Valoración ${val} de 5`"
        :animate="modelValue === val ? presets.select.animate : {}"
        :transition="presets.select.transition"
        :while-press="presets.press.whilePress"
        @click="$emit('update:modelValue', val as RatingValue)"
      >
        <span v-if="modelValue === val" class="rating-star-icon" aria-hidden="true">✦</span>
        <span>{{ val }}</span>
      </Motion>
    </div>

    <div class="rating-legend-row" aria-hidden="true">
      <span>1 · Totalmente en desacuerdo</span>
      <span>5 · Totalmente de acuerdo</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RatingValue } from '../../../types/objective'
import { useMotionPresets } from '../../../composables/useMotionPresets'

defineProps<{
  carreraId: number
  modelValue: RatingValue | null
}>()

defineEmits<{
  'update:modelValue': [value: RatingValue]
}>()

const presets = useMotionPresets()
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
