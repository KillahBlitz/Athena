<template>
  <section class="avatar-story" :aria-label="`Historia de ${avatar.name}`">
    <p class="visually-hidden" role="status">{{ announcement }}</p>

    <div class="story-header">
      <span class="story-eyebrow">
        <span aria-hidden="true">✦</span>
        <span>HISTORIA · {{ dimension.name.toUpperCase() }}</span>
      </span>
      <span class="story-indicator">
        <span class="story-dots" aria-hidden="true">
          <span
            v-for="index in STORY_SCENE_COUNT"
            :key="index"
            class="story-dot"
            :class="{ 'is-active': index - 1 === player.scene.value }"
          />
        </span>
        <span>Escena {{ player.scene.value + 1 }} de {{ STORY_SCENE_COUNT }}</span>
      </span>
    </div>

    <div ref="stageRef" class="story-stage">
      <Motion
        class="story-avatar"
        :animate="canAutoplay ? presets.breathe.animate : {}"
        :transition="presets.breathe.transition"
      >
        <Motion
          :key="`enter-${player.scene.value}`"
          as="span"
          class="story-avatar-enter"
          :initial="presets.celebrate.initial"
          :animate="presets.celebrate.animate"
          :transition="presets.celebrate.transition"
        >
          <Motion
            :key="reactionKey"
            as="span"
            class="story-avatar-face"
            :animate="reactionKey > 0 ? presets.react.animate : {}"
            :transition="presets.react.transition"
          >
            <img :src="avatar.image" alt="">
          </Motion>
        </Motion>
      </Motion>

      <Motion
        :key="`prop-${player.scene.value}`"
        as="span"
        class="story-prop"
        aria-hidden="true"
        :initial="presets.sparkle.initial"
        :animate="propEntrance"
        :transition="presets.celebrate.transition"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path v-for="d in dimension.icon" :key="d" :d="d" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </Motion>

      <AnimatePresence mode="wait" :initial="false">
        <Motion
          :key="player.scene.value"
          class="story-bubble"
          :initial="presets.swap.initial"
          :animate="presets.swap.animate"
          :exit="presets.swap.exit"
          :transition="presets.swap.transition"
        >
          <span class="story-scene-title">{{ currentScene.title }}</span>
          <p class="story-line">{{ currentScene.line }}</p>
        </Motion>
      </AnimatePresence>

      <AnimatePresence>
        <Motion
          v-if="reaction"
          :key="reactionKey"
          class="story-reaction"
          :initial="presets.celebrate.initial"
          :animate="presets.celebrate.animate"
          :exit="presets.swap.exit"
          :transition="presets.celebrate.transition"
        >
          {{ reaction }}
        </Motion>
      </AnimatePresence>
    </div>

    <div class="story-controls">
      <button
        type="button"
        class="story-control"
        aria-label="Escena anterior"
        :disabled="player.scene.value === 0"
        @click="goManual(player.prev)"
      >
        <span aria-hidden="true">←</span>
      </button>
      <button
        type="button"
        class="story-control story-control-pause"
        aria-label="Pausar historia"
        :aria-pressed="paused"
        @click="paused = !paused"
      >
        <span aria-hidden="true">{{ paused ? '▶' : '❚❚' }}</span>
        <span class="story-control-text">Pausar</span>
      </button>
      <button
        type="button"
        class="story-control"
        aria-label="Escena siguiente"
        :disabled="player.isLast.value"
        @click="goManual(player.next)"
      >
        <span aria-hidden="true">→</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onScopeDispose, ref, watch } from 'vue'
import { useInView, usePageInView, useReducedMotion } from 'motion-v'
import type { Avatar } from '../../../types/avatar'
import { getRiasecDimension } from '../config/riasecDimensions'
import { reactionFor, storyFor, STORY_SCENE_COUNT } from '../config/riasecStories'
import { useStoryPlayer } from '../composables/useStoryPlayer'
import { useMotionPresets } from '../../../composables/useMotionPresets'

const REACTION_MS = 1500

const props = defineProps<{
  avatar: Avatar
  riasecId: number
  selectedCount: number
}>()

const presets = useMotionPresets()
const reduced = useReducedMotion()
const stageRef = ref<HTMLElement | null>(null)
const inView = useInView(stageRef)
const pageVisible = usePageInView()
const paused = ref(false)

const canAutoplay = computed(() => !paused.value && !reduced.value && inView.value && pageVisible.value)
const player = useStoryPlayer({ sceneCount: STORY_SCENE_COUNT, canAutoplay })

const dimension = computed(() => getRiasecDimension(props.riasecId))
const propEntrance = computed(() => ({ ...presets.value.celebrate.animate, opacity: 1 }))
const scenes = computed(() => storyFor(props.riasecId, props.avatar.name))
const currentScene = computed(() => scenes.value[player.scene.value] ?? scenes.value[0]!)

const announcement = ref('')
const goManual = (move: () => void) => {
  move()
  announcement.value = `Escena ${player.scene.value + 1} de ${STORY_SCENE_COUNT}: ${currentScene.value.line}`
}

const reaction = ref('')
const reactionKey = ref(0)
let reactionTimer: ReturnType<typeof setTimeout> | null = null

watch(() => props.selectedCount, (count, previous) => {
  if (count <= previous) return
  reaction.value = reactionFor(count)
  reactionKey.value++
  player.react()
  if (reactionTimer !== null) clearTimeout(reactionTimer)
  reactionTimer = setTimeout(() => {
    reaction.value = ''
  }, REACTION_MS)
})

onScopeDispose(() => {
  if (reactionTimer !== null) clearTimeout(reactionTimer)
})
</script>

<style scoped>
.avatar-story {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem 1.5rem 1.5rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-primary-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-card);
}

.story-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.story-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--color-primary);
}

.story-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.story-dots {
  display: inline-flex;
  gap: 0.3rem;
}

.story-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background-color: var(--color-primary-border);
  transition: width var(--motion-base) var(--ease-out), background-color var(--motion-base) ease;
}

.story-dot.is-active {
  width: 18px;
  background-color: var(--color-primary);
}

.story-stage {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  grid-template-areas:
    "avatar bubble"
    "prop bubble";
  gap: 0.5rem 1rem;
  align-items: center;
  min-height: 9.5rem;
  padding: 2.5rem 1rem 1rem;
  border-radius: var(--radius-xl);
  background: var(--gradient-brand-soft);
  overflow: hidden;
}

.story-avatar {
  grid-area: avatar;
  display: grid;
  place-items: center;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background-color: var(--color-surface);
  box-shadow: var(--shadow-glow);
}

.story-avatar-enter {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
}

.story-avatar-face {
  display: grid;
  place-items: center;
  width: 80%;
  height: 80%;
}

.story-avatar-face img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.story-prop {
  grid-area: prop;
  justify-self: center;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background-color: var(--color-surface);
  color: var(--color-primary);
}

.story-prop svg {
  width: 20px;
  height: 20px;
}

.story-bubble {
  grid-area: bubble;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 0.85rem 1rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.story-scene-title {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.story-line {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--color-text-main);
  text-wrap: pretty;
}

.story-reaction {
  position: absolute;
  top: 0.5rem;
  right: 0.6rem;
  padding: 0.3rem 0.7rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--color-on-primary);
  background: var(--gradient-primary);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-glow);
}

.story-controls {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
}

.story-control {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  min-width: var(--tap-target);
  min-height: var(--tap-target);
  padding: 0 0.9rem;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-primary);
  background-color: var(--color-primary-light);
  border: 1px solid var(--color-primary-border);
  border-radius: var(--radius-full);
  transition: background-color var(--motion-base) ease, border-color var(--motion-base) ease;
}

.story-control:hover:not(:disabled) {
  border-color: var(--color-primary);
}

.story-control:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.story-control-pause[aria-pressed="true"] {
  color: var(--color-on-primary);
  background: var(--gradient-primary);
  border-color: var(--color-primary);
}
</style>
