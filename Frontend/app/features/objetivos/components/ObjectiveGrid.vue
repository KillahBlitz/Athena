<template>
  <AnimatePresence mode="wait" :initial="false">
    <Motion
      :key="block.blockIndex"
      class="objectives-cards-grid"
      :initial="presets.swap.initial"
      :animate="presets.swap.animate"
      :exit="presets.swap.exit"
      :transition="presets.swap.transition"
    >
      <ObjectiveCard
        v-for="(objective, index) in block.objectives"
        :key="objective.carreraId"
        class="reveal"
        :style="{ '--reveal-index': index }"
        :objective="objective"
        :answer="getAnswer(objective.carreraId)"
        @update:rating="$emit('rating', objective.carreraId, $event)"
        @update:justification="$emit('justification', objective.carreraId, $event)"
      />
    </Motion>
  </AnimatePresence>
</template>

<script setup lang="ts">
import type { ObjectiveBlock, RatingValue } from '../../../types/objective'
import ObjectiveCard from './ObjectiveCard.vue'
import { useMotionPresets } from '../../../composables/useMotionPresets'

defineProps<{
  block: ObjectiveBlock
  getAnswer: (carreraId: number) => { valoracion: RatingValue | null; justificacion: string }
}>()

defineEmits<{
  rating: [carreraId: number, value: RatingValue]
  justification: [carreraId: number, text: string]
}>()

const presets = useMotionPresets()
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
