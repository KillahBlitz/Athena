<template>
  <article class="riasec-card" :aria-labelledby="`riasec-title-${question.riasec_id}`">
    <div class="riasec-card-header">
      <span class="riasec-dimension-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path v-for="d in dimension.icon" :key="d" :d="d" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </span>
      <h2 class="riasec-dimension-name">{{ dimension.name }}</h2>
      <span class="riasec-dimension-tagline">{{ dimension.tagline }}</span>
    </div>

    <h3 :id="`riasec-title-${question.riasec_id}`" class="riasec-question-text">
      {{ question.texto_pregunta }}
    </h3>

    <div
      class="riasec-options-grid"
      role="group"
      :aria-labelledby="`riasec-title-${question.riasec_id}`"
    >
      <Motion
        v-for="(option, index) in options"
        :key="option.opcionId"
        as="button"
        type="button"
        class="riasec-option reveal"
        :class="{ 'is-selected': isSelected(option.opcionId), 'is-disabled': isDisabled(option.opcionId) }"
        :style="{ '--reveal-index': index }"
        :disabled="isDisabled(option.opcionId)"
        :aria-pressed="isSelected(option.opcionId)"
        :aria-disabled="isDisabled(option.opcionId)"
        :animate="isSelected(option.opcionId) ? presets.select.animate : {}"
        :transition="presets.select.transition"
        :while-press="presets.press.whilePress"
        @click="!isDisabled(option.opcionId) && $emit('toggle', option.opcionId)"
      >
        <span class="riasec-option-top">
          <svg class="riasec-option-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path v-for="d in dimension.icon" :key="d" :d="d" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg
            v-if="isSelected(option.opcionId)"
            class="riasec-option-check"
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            aria-hidden="true"
          >
            <circle cx="10" cy="10" r="7.5" stroke-width="1.6" />
            <path d="M6.8 10.2 L9 12.4 L13.2 8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </span>
        <span class="riasec-option-text">{{ option.texto }}</span>
      </Motion>
    </div>

    <p class="riasec-selection-count" aria-live="polite">
      <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" aria-hidden="true">
        <path d="M2 10.5 L5.5 14 L12 7" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        <path d="M9 13 L10 14 L17 7" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <strong>{{ selectionLabel }}</strong>
      <span v-if="isSelectionLimitReached">· Alcanzaste el máximo de {{ selectionLimit }} habilidades.</span>
      <span v-else>· Puedes elegir varias opciones (máx. {{ selectionLimit }}).</span>
    </p>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BackendPreguntaDTO } from '../../../types/area'
import type { RiasecAnswer, RiasecDimension, RiasecOption } from '../../../types/riasec'
import { useMotionPresets } from '../../../composables/useMotionPresets'

const props = defineProps<{
  question: BackendPreguntaDTO
  dimension: RiasecDimension
  options: RiasecOption[]
  answer: RiasecAnswer
  selectionLimit: number
  isSelectionLimitReached: boolean
}>()

defineEmits<{
  toggle: [opcionId: number]
}>()

const presets = useMotionPresets()

const isSelected = (opcionId: number) => props.answer.opcionIds.includes(opcionId)
const isDisabled = (opcionId: number) => props.isSelectionLimitReached && !isSelected(opcionId)

const selectionLabel = computed(() => {
  const count = props.answer.opcionIds.length
  if (count === 0) return 'Ninguna habilidad seleccionada'
  return count === 1
    ? `1/${props.selectionLimit} habilidad seleccionada`
    : `${count}/${props.selectionLimit} habilidades seleccionadas`
})
</script>

<style scoped>
@import '../styles/riasec.css';
</style>
