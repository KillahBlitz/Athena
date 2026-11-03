<template>
  <Motion
    as="button"
    type="button"
    class="avatar-card"
    :class="{ 'is-selected': isSelected }"
    :aria-pressed="isSelected"
    :aria-label="`Seleccionar avatar ${avatar.name}, ${avatar.role}`"
    :animate="isSelected ? presets.select.animate : {}"
    :transition="presets.select.transition"
    :while-hover="presets.press.whileHover"
    :while-press="presets.press.whilePress"
    @click="$emit('select', avatar.id)"
  >
    <span v-if="isSelected" class="avatar-check-badge" aria-hidden="true">✓</span>
    <div class="avatar-card-image">
      <img :src="avatar.image" :alt="avatar.name" width="84" height="84">
    </div>
    <span class="avatar-card-name">{{ avatar.name }}</span>
  </Motion>
</template>

<script setup lang="ts">
import type { Avatar } from '../../../types/avatar'
import { useMotionPresets } from '../../../composables/useMotionPresets'

defineProps<{
  avatar: Avatar
  isSelected: boolean
}>()

defineEmits<{
  select: [id: string]
}>()

const presets = useMotionPresets()
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
