<template>
  <div class="avatar-selector-section" :class="{ 'needs-attention': !selectedId }">
    <div class="companion-selector-header">
      <span class="companion-selector-title">Elige a tu acompañero</span>
      <span v-if="selectedAvatar" class="companion-active-note">{{ selectedAvatar.name }}</span>
      <span v-else class="companion-prompt-badge">
        <span class="prompt-dot" aria-hidden="true" />
        <span>Elige uno primero</span>
      </span>
    </div>

    <div class="avatars-grid" role="radiogroup" aria-label="Selección de avatar acompañante">
      <div
        v-for="(avatar, index) in avatars"
        :key="avatar.id"
        class="selection-slot reveal"
        :style="{ '--reveal-index': index }"
      >
        <AvatarCard
          :avatar="avatar"
          :is-selected="avatar.id === selectedId"
          @select="$emit('select', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Avatar } from '../../../types/avatar'
import AvatarCard from './AvatarCard.vue'

defineProps<{
  avatars: Avatar[]
  selectedId: string | null
  selectedAvatar: Avatar | null
}>()

defineEmits<{
  select: [id: string]
}>()
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
