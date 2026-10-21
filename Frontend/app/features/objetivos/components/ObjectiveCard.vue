<template>
  <article class="objective-card" :aria-labelledby="`obj-title-${objective.carreraId}`">
    <div class="objective-card-header">
      <span class="objective-category">
        <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
        </svg>
        <span>¿Qué tanto te identificas con este objetivo?</span>
      </span>

      <h2 :id="`obj-title-${objective.carreraId}`" class="objective-statement">
        {{ objective.pregunta }}
      </h2>
    </div>

    <!-- Rating Scale -->
    <RatingScale
      :carrera-id="objective.carreraId"
      :model-value="answer.valoracion"
      @update:model-value="$emit('update:rating', $event)"
    />

    <!-- Justification -->
    <div class="justification-section">
      <label :for="`justification-${objective.carreraId}`" class="justification-label">
        ¿Por qué seleccionaste esta valoración?
        <span v-if="isRequired" class="justification-required">· Obligatorio contestar</span>
      </label>
      <textarea
        :id="`justification-${objective.carreraId}`"
        :value="answer.justificacion"
        class="justification-textarea"
        :class="{ 'is-disabled': isDisabled, 'is-required': isRequired }"
        :disabled="isDisabled"
        :required="isRequired"
        :aria-required="isRequired"
        :placeholder="placeholderText"
        rows="3"
        @input="$emit('update:justification', ($event.target as HTMLTextAreaElement).value)"
      />
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NormalizedObjective, RatingValue } from '../../../types/objective'
import RatingScale from './RatingScale.vue'

const props = defineProps<{
  objective: NormalizedObjective
  answer: { valoracion: RatingValue | null; justificacion: string }
}>()

defineEmits<{
  'update:rating': [value: RatingValue]
  'update:justification': [text: string]
}>()

// Rating 1: justification disabled (not needed)
const isDisabled = computed(() => props.answer.valoracion === 1)
// Rating 5: justification is mandatory
const isRequired = computed(() => props.answer.valoracion === 5)

const placeholderText = computed(() => {
  if (isDisabled.value) {
    return 'No es necesario justificar esta valoración.'
  }
  if (isRequired.value) {
    return 'Cuéntanos a detalle por qué te identificas plenamente con este objetivo...'
  }
  return 'Comparte una reflexión detallada sobre qué te motiva o distancia de este objetivo...'
})
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
