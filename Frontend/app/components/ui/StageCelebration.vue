<template>
  <p class="visually-hidden" role="status">{{ show ? `${title} ${message}` : '' }}</p>
  <AnimatePresence :initial="false">
    <Motion
      v-if="show"
      class="stage-celebration"
      :class="{ 'is-compact': compact }"
      :initial="presets.celebrate.initial"
      :animate="presets.celebrate.animate"
      :transition="presets.celebrate.transition"
    >
      <span class="celebration-sparkles" aria-hidden="true">
        <Motion
          v-for="(sparkle, index) in SPARKLES"
          :key="index"
          as="span"
          class="celebration-sparkle"
          :style="{ left: sparkle.left, top: sparkle.top }"
          :initial="presets.sparkle.initial"
          :animate="presets.sparkle.animate"
          :transition="{ ...presets.sparkle.transition, delay: index * 0.08 }"
        >✦</Motion>
      </span>

      <span class="celebration-badge" aria-hidden="true">✦</span>
      <div class="celebration-text">
        <h3 class="celebration-title">{{ title }}</h3>
        <p class="celebration-message">{{ message }}</p>
      </div>
      <div class="celebration-actions">
        <slot />
      </div>
    </Motion>
  </AnimatePresence>
</template>

<script setup lang="ts">
import { useMotionPresets } from '../../composables/useMotionPresets'

defineProps<{
  show: boolean
  title: string
  message: string
  compact?: boolean
}>()

const SPARKLES = [
  { left: '6%', top: '70%' },
  { left: '18%', top: '18%' },
  { left: '42%', top: '80%' },
  { left: '64%', top: '12%' },
  { left: '82%', top: '64%' },
  { left: '94%', top: '24%' }
]

const presets = useMotionPresets()
</script>

<style scoped>
.stage-celebration {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.6rem 1.25rem;
  align-items: center;
  width: 100%;
  padding: 0.85rem clamp(1.25rem, 4vw, 2.25rem);
  margin-top: 0.5rem;
  background: var(--gradient-brand-soft);
  border: 1.5px solid var(--color-primary-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-pop);
  overflow: hidden;
}

.celebration-sparkles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.celebration-sparkle {
  position: absolute;
  font-size: 1rem;
  color: var(--color-accent);
}

.celebration-badge {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: var(--color-on-primary);
  font-size: 1.1rem;
  box-shadow: var(--shadow-glow);
}

.celebration-title {
  font-family: var(--font-display);
  font-size: var(--text-subtitle);
  font-weight: 800;
  color: var(--color-primary);
  margin-bottom: 0.25rem;
}

.celebration-message {
  font-size: 0.92rem;
  color: var(--color-text-secondary);
  text-wrap: pretty;
}

.celebration-actions {
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

@media (min-width: 768px) {
  .stage-celebration:not(.is-compact) {
    grid-template-columns: auto 1fr auto;
  }

  .stage-celebration:not(.is-compact) .celebration-actions {
    grid-column: auto;
  }
}

.stage-celebration.is-compact {
  padding: 0.85rem 1rem;
  margin-top: 0.75rem;
  box-shadow: none;
}

.stage-celebration.is-compact .celebration-title {
  font-size: 1rem;
}

.stage-celebration.is-compact .celebration-message {
  font-size: 0.85rem;
}
</style>
