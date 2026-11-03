<template>
  <section class="riasec-reflection" :class="{ 'is-locked': locked }" aria-label="Reflexión abierta">
    <div class="riasec-reflection-header">
      <span class="riasec-reflection-icon" aria-hidden="true">
        <svg v-if="locked" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="5" y="11" width="14" height="9" rx="2" stroke-width="1.8" />
          <path d="M8 11V8a4 4 0 0 1 8 0v3" stroke-width="1.8" stroke-linecap="round" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M4 20h4L19 9l-4-4L4 16z" stroke-width="1.8" stroke-linejoin="round" />
          <path d="M13.5 6.5l4 4" stroke-width="1.8" />
        </svg>
      </span>
      <div class="riasec-reflection-copy">
        <label :for="`riasec-open-${riasecId}`" class="riasec-reflection-question">
          {{ question }} (obligatoria)
        </label>
        <span class="riasec-reflection-caption">
          <template v-if="locked">Selecciona al menos una habilidad para continuar</template>
          <template v-else><span class="riasec-reflection-caption-accent">Reflexión</span> · {{ dimensionName }}</template>
        </span>
      </div>
      <span v-if="locked" class="riasec-reflection-status">Aún no disponible</span>
    </div>

    <textarea
      v-if="!locked"
      :id="`riasec-open-${riasecId}`"
      :value="modelValue"
      ref="textarea"
      class="justification-textarea riasec-reflection-textarea"
      placeholder="Cuéntanos con tus propias palabras..."
      rows="2"
      required
      @input="onInput"
    />
  </section>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'

const props = defineProps<{
  riasecId: number
  dimensionName: string
  question: string
  modelValue: string
  locked: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [text: string]
}>()

// Starts short and grows with the text (capped in CSS by max-height).
const textarea = ref<HTMLTextAreaElement | null>(null)

function autoGrow() {
  const el = textarea.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight + 2}px`
}

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value)
  autoGrow()
}

// Fit saved answers when the field appears or the dimension changes.
watch(() => [props.locked, props.riasecId], () => nextTick(autoGrow), { immediate: true })
</script>

<style scoped>
@import '../../objetivos/styles/objectives.css';
@import '../styles/riasec.css';
</style>
