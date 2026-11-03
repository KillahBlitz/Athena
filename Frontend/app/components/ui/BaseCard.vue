<template>
  <div
    class="base-card card-base"
    :class="{
      'is-selected': selected,
      'is-interactive': interactive
    }"
    @click="interactive && $emit('click', $event)"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    selected?: boolean
    interactive?: boolean
  }>(),
  {
    selected: false,
    interactive: false
  }
)

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.base-card {
  position: relative;
  border-radius: var(--radius-xl);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: transform var(--motion-base) var(--ease-out), box-shadow var(--motion-base) ease, border-color var(--motion-base) ease, background-color var(--motion-base) ease;
}

.is-interactive {
  cursor: pointer;
}

.is-interactive:hover {
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-3px);
}

@media (prefers-reduced-motion: reduce) {
  .is-interactive:hover {
    transform: none;
  }
}

.is-selected {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
  box-shadow: 0 0 0 1px var(--color-primary), var(--shadow-sm);
}
</style>
