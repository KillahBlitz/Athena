<template>
  <div class="objectives-progress-widget" role="region" aria-label="Progreso de objetivos">
    <!-- Original fixed constellation artwork. Which stars/segments are lit
         is driven by progress (currentBlock/totalBlocks), not the shape
         itself, which stays exactly as it was. No text on the graphic. -->
    <svg class="constellation-art" viewBox="0 0 140 48" fill="none" aria-hidden="true">
      <line class="constellation-line" :class="lineClass(0)" x1="12" y1="36" x2="42" y2="20" stroke-width="1.5" :stroke-dasharray="lineDash(0)" />
      <line class="constellation-line" :class="lineClass(1)" x1="42" y1="20" x2="84" y2="8" stroke-width="1.8" />
      <line class="constellation-line" :class="lineClass(2)" x1="84" y1="8" x2="128" y2="16" stroke-width="1.8" />
      <line class="constellation-line" :class="lineClass(3)" x1="128" y1="16" x2="110" y2="38" stroke-width="1.5" />
      <line class="constellation-line" :class="lineClass(3)" x1="110" y1="38" x2="84" y2="8" stroke-width="1.5" :stroke-dasharray="lineDash(3)" />

      <circle class="constellation-star" :class="starClass(0)" cx="12" cy="36" r="3" />
      <circle class="constellation-star" :class="starClass(1)" cx="42" cy="20" r="3.5" />
      <circle class="constellation-star" :class="starClass(2)" cx="84" cy="8" r="4.5" />
      <circle class="constellation-star" :class="starClass(3)" cx="128" cy="16" r="4" />
      <circle class="constellation-star" :class="starClass(4)" cx="110" cy="38" r="3.5" />

      <!-- Exact marker for every real block, placed along the same fixed
           path (shape untouched), so each block has its own precise point. -->
      <circle
        v-for="point in blockPoints"
        :key="`block-${point.block}`"
        class="constellation-block-marker"
        :class="{ 'is-done': point.isDone, 'is-current': point.isCurrent }"
        :cx="point.x"
        :cy="point.y"
        r="2"
      />
    </svg>

    <div class="progress-labels-row">
      <span>Bloque {{ progress.currentBlock }} de {{ progress.totalBlocks }}</span>
      <span>{{ progress.percentage }} % completado</span>
    </div>

    <div
      class="progress-track"
      role="progressbar"
      :aria-valuenow="progress.percentage"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`Progreso: ${progress.percentage}% completado`"
    >
      <div class="progress-fill" :style="{ width: `${progress.percentage}%` }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ObjectivesProgress } from '../../../types/objective'

const props = defineProps<{
  progress: ObjectivesProgress
}>()

const STAR_COUNT = 5

// Map the actual block progress (which can have any number of blocks) onto
// the artwork's fixed 5 stars, so the shape never changes but it still
// visually tracks how far along the user is and which part is still pending.
const litIndex = computed(() => {
  const total = Math.max(props.progress.totalBlocks, 1)
  const ratio = (props.progress.currentBlock - 1) / total
  return Math.min(STAR_COUNT - 1, Math.floor(ratio * STAR_COUNT))
})

function starClass(index: number) {
  return {
    'is-done': index < litIndex.value,
    'is-current': index === litIndex.value
  }
}

function lineClass(fromIndex: number) {
  return { 'is-lit': fromIndex < litIndex.value }
}

function lineDash(fromIndex: number) {
  return fromIndex < litIndex.value ? undefined : '2 2'
}

// The constellation's fixed path (same coordinates as the artwork above),
// used only to place one exact marker per real block along it.
const PATH_POINTS = [
  { x: 12, y: 36 },
  { x: 42, y: 20 },
  { x: 84, y: 8 },
  { x: 128, y: 16 },
  { x: 110, y: 38 }
]

const PATH_SEGMENT_LENGTHS = (() => {
  const lengths = [0]
  let total = 0
  for (let i = 1; i < PATH_POINTS.length; i++) {
    total += Math.hypot(PATH_POINTS[i]!.x - PATH_POINTS[i - 1]!.x, PATH_POINTS[i]!.y - PATH_POINTS[i - 1]!.y)
    lengths.push(total)
  }
  return lengths
})()
const PATH_TOTAL_LENGTH = PATH_SEGMENT_LENGTHS[PATH_SEGMENT_LENGTHS.length - 1]!

function pointAtFraction(fraction: number): { x: number; y: number } {
  const target = fraction * PATH_TOTAL_LENGTH
  for (let i = 1; i < PATH_POINTS.length; i++) {
    const segStart = PATH_SEGMENT_LENGTHS[i - 1]!
    const segEnd = PATH_SEGMENT_LENGTHS[i]!
    if (target <= segEnd || i === PATH_POINTS.length - 1) {
      const segLen = segEnd - segStart
      const t = segLen === 0 ? 0 : Math.min(1, Math.max(0, (target - segStart) / segLen))
      const a = PATH_POINTS[i - 1]!
      const b = PATH_POINTS[i]!
      return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t }
    }
  }
  return PATH_POINTS[0]!
}

const blockPoints = computed(() => {
  const total = Math.max(props.progress.totalBlocks, 1)
  return Array.from({ length: total }, (_, i) => {
    const fraction = total === 1 ? 0.5 : i / (total - 1)
    const { x, y } = pointAtFraction(fraction)
    const block = i + 1
    return {
      block,
      x,
      y,
      isDone: block < props.progress.currentBlock,
      isCurrent: block === props.progress.currentBlock
    }
  })
})
</script>

<style scoped>
@import '../styles/objectives.css';
</style>
