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
      <div class="objectives-stack-deck" :style="{ '--deck-count': block.objectives.length }">
        <Motion
          v-for="(objective, index) in block.objectives"
          :key="objective.carreraId"
          as="div"
          class="objective-card-stacked"
          :class="{
            'is-active': index === activeIndex,
            'is-exited': index < activeIndex
          }"
          :style="cardVisual(index)"
          :animate="cardTransform(index)"
          :transition="cardTransitionFor(index)"
          :while-hover="index === activeIndex ? { y: -4 } : {}"
        >
          <ObjectiveCard
            :objective="objective"
            :answer="getAnswer(objective.carreraId)"
            @update:rating="$emit('rating', objective.carreraId, $event)"
            @update:justification="$emit('justification', objective.carreraId, $event)"
          />
        </Motion>
      </div>

      <div v-if="block.objectives.length > 1" class="objective-card-nav" role="group" aria-label="Cambiar de pregunta">
        <button
          type="button"
          class="stack-nav-btn is-prev"
          :disabled="activeIndex === 0"
          aria-label="Pregunta anterior"
          @click="goPrev"
        >
          <span aria-hidden="true">‹</span>
          <span class="stack-nav-text">Anterior</span>
        </button>

        <span class="stack-nav-progress">
          <span class="stack-nav-counter" aria-live="polite">
            Pregunta {{ activeIndex + 1 }} de {{ block.objectives.length }}
          </span>
          <span class="stack-nav-dots" aria-hidden="true">
            <span
              v-for="(objective, i) in block.objectives"
              :key="objective.carreraId"
              class="stack-nav-dot"
              :class="{ 'is-active': i === activeIndex, 'is-past': i < activeIndex }"
            />
          </span>
        </span>

        <button
          type="button"
          class="stack-nav-btn is-next"
          :class="{ 'is-ready': isActiveAnswered }"
          :disabled="activeIndex === block.objectives.length - 1"
          aria-label="Siguiente pregunta"
          @click="goNext"
        >
          <span class="stack-nav-text">Siguiente</span>
          <span aria-hidden="true">›</span>
        </button>
      </div>
    </Motion>
  </AnimatePresence>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch, type CSSProperties } from 'vue'
import type { ObjectiveBlock, RatingValue } from '../../../types/objective'
import ObjectiveCard from './ObjectiveCard.vue'
import { useMotionPresets } from '../../../composables/useMotionPresets'

const props = defineProps<{
  block: ObjectiveBlock
  getAnswer: (carreraId: number) => { valoracion: RatingValue | null; justificacion: string }
}>()

const emit = defineEmits<{
  leave: [carreraId: number]
  revisit: [carreraId: number]
  rating: [carreraId: number, value: RatingValue]
  justification: [carreraId: number, text: string]
}>()

const presets = useMotionPresets()

const activeIndex = ref(0)

watch(
  () => props.block.blockIndex,
  () => {
    activeIndex.value = 0
    direction.value = 1
    forcedEntryIndex.value = null
  }
)

const cardCount = computed(() => props.block.objectives.length)

const isActiveAnswered = computed(() => {
  const objective = props.block.objectives[activeIndex.value]
  if (!objective) return false
  const answer = props.getAnswer(objective.carreraId)
  if (answer.valoracion === null) return false
  return answer.valoracion !== 5 || answer.justificacion.trim().length > 0
})

const direction = ref<1 | -1>(1)

const forcedEntryIndex = ref<number | null>(null)

function goPrev() {
  if (activeIndex.value === 0) return
  const revealIndex = activeIndex.value - 1
  const revealed = props.block.objectives[revealIndex]
  if (revealed) emit('revisit', revealed.carreraId)
  direction.value = -1
  forcedEntryIndex.value = revealIndex
  nextTick(() => {
    activeIndex.value = revealIndex
    requestAnimationFrame(() => {
      if (forcedEntryIndex.value === revealIndex) forcedEntryIndex.value = null
    })
  })
}

function goNext() {
  if (activeIndex.value >= cardCount.value - 1) return
  const leaving = props.block.objectives[activeIndex.value]
  if (leaving) emit('leave', leaving.carreraId)
  direction.value = 1
  activeIndex.value += 1
}

const MAX_STACK_DEPTH = 3

interface CardTransform {
  x: number | string
  y: number | string
  scale: number
  rotate: number
  opacity: number
  [key: string]: number | string
}

function cardTransform(index: number): CardTransform {
  if (forcedEntryIndex.value === index && index !== activeIndex.value) {
    return { x: '-140%', y: 6, scale: 0.9, rotate: -6, opacity: 0 }
  }

  const relativeIndex = index - activeIndex.value

  if (relativeIndex === 0) {
    return { x: 0, y: 0, scale: 1, rotate: 0, opacity: 1 }
  }

  if (relativeIndex > 0) {
    const depth = Math.min(relativeIndex, MAX_STACK_DEPTH)
    const scale = 1 - depth * 0.05
    const offsetY = depth * 16
    const offsetX = depth * 9
    const tilt = depth * 2.25 * (depth % 2 === 0 ? 1 : -1)

    return {
      x: offsetX,
      y: offsetY,
      scale,
      rotate: tilt,
      opacity: relativeIndex > MAX_STACK_DEPTH ? 0 : 1
    }
  }

  const toRight = direction.value > 0
  return {
    x: toRight ? '140%' : '-140%',
    y: 6,
    scale: 0.9,
    rotate: toRight ? 6 : -6,
    opacity: 0
  }
}

function cardTransitionFor(index: number) {
  if (forcedEntryIndex.value === index && index !== activeIndex.value) {
    return { duration: 0 }
  }
  return presets.value.cardStack.transition
}

function cardVisual(index: number): CSSProperties {
  const relativeIndex = index - activeIndex.value

  if (relativeIndex === 0) {
    return { zIndex: 40, boxShadow: 'none', pointerEvents: 'auto' }
  }
  if (relativeIndex > 0) {
    const depth = Math.min(relativeIndex, MAX_STACK_DEPTH)
    return {
      zIndex: 40 - depth,
      boxShadow: 'none',
      filter: `brightness(${1 - depth * 0.014})`,
      pointerEvents: 'none'
    }
  }
  return { zIndex: 10, boxShadow: 'none', pointerEvents: 'none' }
}
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
