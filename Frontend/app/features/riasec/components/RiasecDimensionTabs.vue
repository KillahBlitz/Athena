<template>
  <nav class="riasec-tabs" aria-label="Dimensiones RISEC">
    <div class="riasec-tabs-labels">
      <span>Dimensión {{ current }} de {{ total }}</span>
    </div>
    <div class="riasec-tabs-list">
      <button
        v-for="tab in tabs"
        :key="tab.index"
        type="button"
        class="riasec-tab"
        :class="{
          'is-current': tab.isCurrent,
          'is-answered': tab.isAnswered && !tab.isCurrent
        }"
        :disabled="!tab.isReachable"
        :aria-current="tab.isCurrent ? 'step' : undefined"
        @click="$emit('select', tab.index)"
      >
        <svg
          v-if="tab.isAnswered && !tab.isCurrent"
          class="riasec-tab-check"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path d="M3.5 8.5 L6.5 11.5 L12.5 4.5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span v-else class="riasec-tab-number">{{ tab.index + 1 }}</span>
        <span>{{ tab.dimension.name }}</span>
      </button>
    </div>
    <div
      ref="track"
      class="riasec-tabs-progress"
      :style="{ '--dot-start': `${Math.max(0, trackWidth - DOT_SIZE)}px` }"
      role="progressbar"
      :aria-valuenow="percentage"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`Progreso: ${percentage}%`"
    >
      <TransitionGroup name="riasec-dot" @before-leave="setLeaveDelay">
        <span
          v-for="i in filledDots"
          :key="i"
          class="riasec-progress-dot"
          :data-index="i - 1"
          :style="{
            '--x': `${dotLeft(i - 1)}px`,
            '--enter-delay': `${dotDelays[i - 1] ?? 0}ms`
          }"
          aria-hidden="true"
        />
      </TransitionGroup>
      <span
        v-if="filledDots < totalDots"
        :key="`next-${filledDots}`"
        class="riasec-progress-dot is-next"
        :style="{
          '--x': `${dotLeft(filledDots)}px`,
          animationDelay: `${nextDotDelay}ms`
        }"
        aria-hidden="true"
      />
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { RiasecTab } from '../composables/useRiasecForm'

const props = defineProps<{
  tabs: RiasecTab[]
  percentage: number
  current: number
  total: number
}>()

// Each dot is as tall as the bar. Dots overlap (step < size) so the stack reads as a
// solid bar with no gaps; new dots come in from the right end and pile up at the front.
const DOT_SIZE = 8
const DOT_STEP = 3
const DOT_STAGGER_MS = 25
const MAX_STREAM_MS = 1200

const track = ref<HTMLElement | null>(null)
const trackWidth = ref(0)

const totalDots = computed(() =>
  trackWidth.value >= DOT_SIZE ? Math.floor((trackWidth.value - DOT_SIZE) / DOT_STEP) + 1 : 0
)

const filledDots = computed(() => {
  const pct = Math.min(100, Math.max(0, props.percentage))
  return Math.round((totalDots.value * pct) / 100)
})

// Spread the dots so the last one sits exactly at the right end.
function dotLeft(index: number): number {
  if (totalDots.value <= 1) return 0
  return (index * (trackWidth.value - DOT_SIZE)) / (totalDots.value - 1)
}

const DOT_TRAVEL_MS = 450

// Delay is fixed when a dot is created, so only new dots animate and they enter in sequence.
const dotDelays = ref<number[]>([])
// Pulse on the front starts once the dots finish arriving (or leaving).
const nextDotDelay = ref(0)
// Data for dots leaving when progress goes back: they return to the right end, front first.
let leaveFrom = 0
let leaveStagger = 0

watch(filledDots, (next, prev = 0) => {
  const count = Math.abs(next - prev)
  if (count === 0) return
  // Cap the whole stream so big jumps still finish quickly.
  const stagger = Math.min(DOT_STAGGER_MS, MAX_STREAM_MS / count)
  if (next > prev) {
    for (let i = prev; i < next; i++) {
      dotDelays.value[i] = (i - prev) * stagger
    }
  } else {
    leaveFrom = prev
    leaveStagger = stagger
  }
  nextDotDelay.value = (count - 1) * stagger + DOT_TRAVEL_MS
}, { immediate: true, flush: 'pre' })

function setLeaveDelay(el: Element) {
  const node = el as HTMLElement
  const index = Number(node.dataset.index ?? 0)
  // The dot at the front (highest index) leaves first.
  const order = Math.max(0, leaveFrom - 1 - index)
  node.style.setProperty('--leave-delay', `${order * leaveStagger}ms`)
}

let observer: ResizeObserver | null = null

onMounted(() => {
  if (!track.value) return
  trackWidth.value = track.value.clientWidth
  observer = new ResizeObserver(([entry]) => {
    if (entry) trackWidth.value = entry.contentRect.width
  })
  observer.observe(track.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

defineEmits<{
  select: [index: number]
}>()
</script>

<style scoped>
@import '../styles/riasec.css';
</style>
