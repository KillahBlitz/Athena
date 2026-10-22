<template>
  <Motion
    as="button"
    :type="type"
    :disabled="disabled || loading"
    class="base-button"
    :class="[`btn-${variant}`, `btn-${size}`, { 'is-loading': loading }]"
    :while-hover="isInteractive ? presets.press.whileHover : undefined"
    :while-press="isInteractive ? presets.press.whilePress : undefined"
    :transition="presets.press.transition"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner" aria-hidden="true" />
    <slot name="prefix" />
    <span class="btn-label"><slot /></span>
    <slot name="suffix" />
  </Motion>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMotionPresets } from '../../composables/useMotionPresets'

const props = withDefaults(
  defineProps<{
    type?: 'button' | 'submit' | 'reset'
    variant?: 'primary' | 'secondary' | 'ghost' | 'outline'
    size?: 'sm' | 'md' | 'lg'
    disabled?: boolean
    loading?: boolean
  }>(),
  {
    type: 'button',
    variant: 'primary',
    size: 'md',
    disabled: false,
    loading: false
  }
)

defineEmits<{
  click: [event: MouseEvent]
}>()

const presets = useMotionPresets()
const isInteractive = computed(() => !props.disabled && !props.loading)
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 700;
  border-radius: var(--radius-full);
  transition: background-color var(--motion-base) ease, box-shadow var(--motion-base) ease, border-color var(--motion-base) ease, color var(--motion-base) ease;
  text-align: center;
  user-select: none;
}

@media (min-width: 768px) {
  .base-button {
    white-space: nowrap;
  }
}

/* Sizes */
.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.82rem;
  min-height: var(--tap-target);
}

.btn-md {
  padding: 0.65rem 1.5rem;
  font-size: 0.95rem;
  min-height: var(--tap-target);
}

.btn-lg {
  padding: 0.85rem 2rem;
  font-size: 1rem;
  min-height: 52px;
}

/* Variants */
.btn-primary {
  background: var(--gradient-primary);
  color: var(--color-on-primary);
  box-shadow: var(--shadow-glow);
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 16px 36px -12px rgba(var(--color-primary-rgb), 0.65);
}

.btn-secondary {
  background-color: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-surface-hover);
  border-color: var(--color-border-hover);
}

.btn-ghost {
  background-color: transparent;
  color: var(--color-text-muted);
}

.btn-ghost:hover:not(:disabled) {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.btn-outline {
  background-color: var(--color-surface);
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
}

.btn-outline:hover:not(:disabled) {
  background-color: var(--color-primary-light);
}

.base-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--color-on-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
