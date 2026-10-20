<template>
  <button
    type="button"
    class="area-card"
    :class="{ 'is-selected': isSelected }"
    :aria-pressed="isSelected"
    :aria-label="`Seleccionar área: ${area.name}`"
    @click="$emit('select', area.id)"
  >
    <div class="area-card-top">
      <div class="area-card-icon" aria-hidden="true">
        <img :src="area.icon" alt="" width="40" height="40">
      </div>
      <div class="area-radio-indicator" aria-hidden="true">
        <span v-if="isSelected" class="area-radio-check">✓</span>
      </div>
    </div>
    <div class="area-card-body">
      <h3 class="area-card-name">{{ area.name }}</h3>
      <p class="area-card-tagline">{{ area.tagline }}</p>
    </div>
  </button>
</template>

<script setup lang="ts">
import type { Area } from '../../../types/area'

defineProps<{
  area: Area
  isSelected: boolean
}>()

defineEmits<{
  select: [id: number]
}>()
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
