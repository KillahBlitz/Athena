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

          <!-- Prev/next controls live on the active card itself, not in a
               separate row below the deck. -->
          <div v-if="index === activeIndex && block.objectives.length > 1" class="objective-card-nav">
            <button
              type="button"
              class="stack-nav-btn"
              :disabled="activeIndex === 0"
              aria-label="Pregunta anterior"
              @click.stop="goPrev"
            >
              <span aria-hidden="true">‹</span>
            </button>

            <span class="stack-nav-counter" aria-live="polite">
              {{ activeIndex + 1 }} / {{ block.objectives.length }}
            </span>

            <button
              type="button"
              class="stack-nav-btn"
              :disabled="activeIndex === block.objectives.length - 1"
              aria-label="Siguiente pregunta"
              @click.stop="goNext"
            >
              <span aria-hidden="true">›</span>
            </button>
          </div>
        </Motion>
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
  rating: [carreraId: number, value: RatingValue]
  justification: [carreraId: number, text: string]
}>()

const presets = useMotionPresets()

// --- Visual-only "card stack" navigation state ---
// This index only controls which card sits at the front of the deck. It never
// touches answers, validation or the block-level progress used by the form.
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

// Direction of the last navigation. Advancing and going back are two
// genuinely different animations, not mirror images of each other: an
// answered card that's left behind exits to the right, while going back
// always reveals the previous card coming in from the left.
const direction = ref<1 | -1>(1)

// Index of the card that's about to be revealed by "Atrás". While set, that
// card is snapped instantly (no animation) to its "parked on the left"
// position, so the *next* render can animate it smoothly from there into
// place — instead of animating from wherever it happened to exit to.
const forcedEntryIndex = ref<number | null>(null)

function goPrev() {
  if (activeIndex.value === 0) return
  const revealIndex = activeIndex.value - 1
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

// Motion-driven position/scale/rotation for each card in the stack. Using
// motion-v's spring transition (instead of a plain CSS transition) keeps the
// deck feeling fluid and physical rather than a flat, linear slide.
function cardTransform(index: number): CardTransform {
  // Still waiting to be revealed by "Atrás": hold it parked on the left,
  // instantly (see cardTransitionFor), until activeIndex catches up.
  if (forcedEntryIndex.value === index && index !== activeIndex.value) {
    return { x: '-140%', y: 6, scale: 0.9, rotate: -6, opacity: 0 }
  }

  const relativeIndex = index - activeIndex.value

  // Active card: front of the deck, full scale.
  if (relativeIndex === 0) {
    return { x: 0, y: 0, scale: 1, rotate: 0, opacity: 1 }
  }

  // Cards still ahead in the deck: stacked behind, shrinking and tilting with depth
  // so the pile reads as a physical stack instead of flat, parallel copies.
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

  // Cards already answered and left behind: parked off to whichever side
  // matches the last navigation, so advancing exits right and the next
  // "Atrás" has a real left-parked starting point to animate in from.
  const toRight = direction.value > 0
  return {
    x: toRight ? '140%' : '-140%',
    y: 6,
    scale: 0.9,
    rotate: toRight ? 6 : -6,
    opacity: 0
  }
}

// Transitions are instant (no tween) only while a card is being force-parked
// ahead of a "reveal from the left" animation; everything else uses the
// normal fluid spring.
function cardTransitionFor(index: number) {
  if (forcedEntryIndex.value === index && index !== activeIndex.value) {
    return { duration: 0 }
  }
  return presets.value.cardStack.transition
}

// Non-animatable visuals (z-index, shadow, pointer handling) switch instantly
// rather than tweening, since interpolating them doesn't read as "fluid".
function cardVisual(index: number): CSSProperties {
  const relativeIndex = index - activeIndex.value

  if (relativeIndex === 0) {
    return { zIndex: 40, boxShadow: 'var(--shadow-card-hover)', pointerEvents: 'auto' }
  }
  if (relativeIndex > 0) {
    const depth = Math.min(relativeIndex, MAX_STACK_DEPTH)
    return {
      zIndex: 40 - depth,
      boxShadow: depth === 1 ? 'var(--shadow-sm)' : 'none',
      pointerEvents: 'none'
    }
  }
  return { zIndex: 10, boxShadow: 'none', pointerEvents: 'none' }
}
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
