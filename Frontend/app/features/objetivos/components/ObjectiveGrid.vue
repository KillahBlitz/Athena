<template>
  <div class="objectives-cards-grid">
    <ObjectiveCard
      v-for="objective in block.objectives"
      :key="objective.carreraId"
      :objective="objective"
      :answer="getAnswer(objective.carreraId)"
      @update:rating="$emit('rating', objective.carreraId, $event)"
      @update:justification="$emit('justification', objective.carreraId, $event)"
    />
  </div>
</template>

<script setup lang="ts">
import type { ObjectiveBlock, RatingValue } from '../../../types/objective'
import ObjectiveCard from './ObjectiveCard.vue'

defineProps<{
  block: ObjectiveBlock
  getAnswer: (carreraId: number) => { valoracion: RatingValue | null; justificacion: string }
}>()

defineEmits<{
  rating: [carreraId: number, value: RatingValue]
  justification: [carreraId: number, text: string]
}>()
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
