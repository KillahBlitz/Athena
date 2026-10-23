<template>
  <div class="error-message-banner" role="alert" aria-live="assertive">
    <div class="error-icon" aria-hidden="true">
      <svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="error-content">
      <p class="error-text">{{ message }}</p>
      <slot />
    </div>
    <button v-if="retryable" type="button" class="retry-btn" @click="$emit('retry')">
      Reintentar
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    message: string
    retryable?: boolean
  }>(),
  {
    retryable: false
  }
)

defineEmits<{
  retry: []
}>()
</script>

<style scoped>
.error-message-banner {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
  padding: 0.9rem 1.2rem;
  background-color: var(--color-error-bg);
  border: 1px solid var(--color-error-border);
  border-radius: var(--radius-lg);
  color: var(--color-error-text);
}

.error-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.error-content {
  flex: 1;
  font-size: 0.88rem;
  font-weight: 500;
}

.retry-btn {
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: underline;
  color: var(--color-error-text);
  cursor: pointer;
  min-height: var(--tap-target);
  padding: 0.2rem 0.75rem;
}
</style>
