<template>
  <div class="base-input-group" :class="{ 'has-error': Boolean(error) }">
    <label v-if="label" :for="id" class="input-label">
      {{ label }}
      <span v-if="required" class="required-indicator" aria-hidden="true">*</span>
    </label>
    <div class="input-wrapper">
      <input
        :id="id"
        :name="name || id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :autocomplete="autocomplete"
        :min="min"
        :max="max"
        :aria-invalid="Boolean(error)"
        :aria-describedby="error ? `${id}-error` : undefined"
        class="input-control"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
    </div>
    <span v-if="error" :id="`${id}-error`" class="input-error" role="alert">
      {{ error }}
    </span>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    id: string
    name?: string
    label?: string
    type?: string
    modelValue?: string | number | null
    placeholder?: string
    error?: string
    required?: boolean
    disabled?: boolean
    autocomplete?: string
    min?: number | string
    max?: number | string
  }>(),
  {
    type: 'text',
    modelValue: '',
    placeholder: '',
    error: '',
    required: false,
    disabled: false,
    autocomplete: 'off'
  }
)

defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()
</script>

<style scoped>
.base-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  width: 100%;
}

.input-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-main);
}

.required-indicator {
  color: var(--color-error);
  margin-left: 0.2rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-control {
  width: 100%;
  height: 46px;
  padding: 0 1rem;
  font-size: 0.95rem;
  color: var(--color-text-main);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  outline: none;
  transition: all 0.2s ease;
}

.input-control::placeholder {
  color: var(--color-text-light);
}

.input-control:hover:not(:disabled) {
  border-color: var(--color-border-hover);
}

.input-control:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.15);
}

.has-error .input-control {
  border-color: var(--color-error);
}

.has-error .input-control:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.input-error {
  font-size: 0.76rem;
  color: var(--color-error);
  font-weight: 500;
  margin-top: 0.2rem;
}
</style>
