<template>
  <div class="avatar-selector-section">
    <div class="companion-selector-header">
      <span>Elige a tu acompañero</span>
      <span class="companion-active-note">{{ selectedAvatar.name }}</span>
    </div>

    <!-- 4 Avatars Grid -->
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
  selectedId: string
  selectedAvatar: Avatar
}>()

defineEmits<{
  select: [id: string]
}>()
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
