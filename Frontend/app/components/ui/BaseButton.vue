<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="base-button"
    :class="[`btn-${variant}`, `btn-${size}`, { 'is-loading': loading }]"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner" aria-hidden="true" />
    <slot name="prefix" />
    <span class="btn-label"><slot /></span>
    <slot name="suffix" />
  </button>
</template>

<script setup lang="ts">
withDefaults(
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
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 600;
  border-radius: var(--radius-md);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  user-select: none;
}

.base-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.base-button:active:not(:disabled) {
  transform: translateY(0);
}

/* Sizes */
.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.btn-md {
  padding: 0.65rem 1.4rem;
  font-size: 0.92rem;
  min-height: 44px;
}

.btn-lg {
  padding: 0.85rem 1.8rem;
  font-size: 1rem;
  min-height: 50px;
}

/* Variants */
.btn-primary {
  background-color: var(--color-primary);
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.25);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  box-shadow: 0 6px 16px rgba(var(--color-primary-rgb), 0.35);
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
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.btn-outline:hover:not(:disabled) {
  background-color: var(--color-primary-light);
}

.base-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
