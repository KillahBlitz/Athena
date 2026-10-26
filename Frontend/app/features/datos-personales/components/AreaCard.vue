<template>
  <Motion
    as="button"
    type="button"
    class="area-card"
    :data-area-id="area.id"
    :class="{ 'is-selected': isSelected }"
    :aria-pressed="isSelected"
    :aria-label="`Seleccionar área: ${area.name}`"
    :animate="isSelected ? presets.select.animate : {}"
    :transition="presets.select.transition"
    :while-hover="presets.press.whileHover"
    :while-press="presets.press.whilePress"
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
  </Motion>
</template>

<script setup lang="ts">
import type { Area } from '../../../types/area'
import { useMotionPresets } from '../../../composables/useMotionPresets'

defineProps<{
  area: Area
  isSelected: boolean
}>()

defineEmits<{
  select: [id: number]
}>()

const presets = useMotionPresets()
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
