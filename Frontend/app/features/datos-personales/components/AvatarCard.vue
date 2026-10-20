<template>
  <button
    type="button"
    class="avatar-card"
    :class="{ 'is-selected': isSelected }"
    :aria-pressed="isSelected"
    :aria-label="`Seleccionar avatar ${avatar.name}, ${avatar.role}`"
    @click="$emit('select', avatar.id)"
  >
    <span v-if="isSelected" class="avatar-check-badge" aria-hidden="true">✓</span>
    <div class="avatar-card-image">
      <img :src="avatar.image" :alt="avatar.name" width="44" height="44">
    </div>
    <span class="avatar-card-name">{{ avatar.name }}</span>
  </button>
</template>

<script setup lang="ts">
import type { Avatar } from '../../../types/avatar'

defineProps<{
  avatar: Avatar
  isSelected: boolean
}>()

defineEmits<{
  select: [id: string]
}>()
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
