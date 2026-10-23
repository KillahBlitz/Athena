<template>
  <nav class="riasec-tabs" aria-label="Dimensiones RISEC">
    <button
      v-for="tab in tabs"
      :key="tab.index"
      type="button"
      class="riasec-tab"
      :class="{
        'is-current': tab.isCurrent,
        'is-answered': tab.isAnswered && !tab.isCurrent
      }"
      :disabled="!tab.isReachable"
      :aria-current="tab.isCurrent ? 'step' : undefined"
      @click="$emit('select', tab.index)"
    >
      <svg
        v-if="tab.isAnswered && !tab.isCurrent"
        class="riasec-tab-check"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path d="M3.5 8.5 L6.5 11.5 L12.5 4.5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span v-else class="riasec-tab-number">{{ tab.index + 1 }}</span>
      <span>{{ tab.dimension.name }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import type { RiasecTab } from '../composables/useRiasecForm'

defineProps<{
  tabs: RiasecTab[]
}>()

defineEmits<{
  select: [index: number]
}>()
</script>

<style scoped>
@import '../styles/riasec.css';
</style>
