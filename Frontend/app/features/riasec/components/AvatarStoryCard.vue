<template>
  <section class="avatar-story" :class="{ 'is-finish': stageComplete }" :aria-label="`Historia de ${avatar.name}`">
    <p class="visually-hidden" role="status">{{ announcement }}</p>

    <div class="story-header">
      <span class="story-eyebrow">
        <span aria-hidden="true">✦</span>
        <span>HISTORIA · {{ dimension.name.toUpperCase() }}</span>
      </span>
      <span class="story-indicator">
        <span class="story-dots" aria-hidden="true">
          <span
            v-for="index in scenes.length"
            :key="index"
            class="story-dot"
            :class="{ 'is-active': index - 1 === player.scene.value }"
          />
        </span>
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
            <TrackingAvatar class="selected-avatar-tracking" :avatar-id="avatar.id" :name="avatar.name" />
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
          :key="bubbleKey"
          class="story-bubble"
          :initial="presets.swap.initial"
          :animate="presets.swap.animate"
          :exit="presets.swap.exit"
          :transition="presets.swap.transition"
        >
          <span class="story-scene-title">{{ bubble.title }}</span>
          <p class="story-line">{{ bubble.line }}</p>
          <p v-if="'note' in bubble && bubble.note" class="story-line story-line-note">{{ bubble.note }}</p>
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

    <div v-if="!isLastDimension" class="story-controls">
      <button type="button" class="story-control" @click="showMessage('tip')">
        Dame un consejo
      </button>
      <button type="button" class="story-control" @click="showMessage('cheer')">
        Necesito ánimo <span aria-hidden="true">✦</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import TrackingAvatar from '../../../components/avatar/TrackingAvatar.vue'
import { computed, onScopeDispose, ref, watch } from 'vue'
import { useInView, usePageInView, useReducedMotion } from 'motion-v'
import type { Avatar } from '../../../types/avatar'
import { getRiasecDimension } from '../config/riasecDimensions'
import { reactionFor, storyFor } from '../config/riasecStories'
import { useStoryPlayer } from '../composables/useStoryPlayer'
import { useMotionPresets } from '../../../composables/useMotionPresets'
import { AVATAR_CHEERS, RIASEC_TIPS } from '../../../config/avatarMessages'

const REACTION_MS = 1500

const props = defineProps<{
  avatar: Avatar
  riasecId: number
  selectedCount: number
  selectionLimit: number
  stageComplete?: boolean
  isLastDimension?: boolean
  confirmingFinish?: boolean
}>()

const presets = useMotionPresets()
const reduced = useReducedMotion()
const stageRef = ref<HTMLElement | null>(null)
const inView = useInView(stageRef)
const pageVisible = usePageInView()
const MAX_PART_CHARS = 60
const PART_MS = 3500
const LAST_PART_MS = 5000

const message = ref<{ title: string, line: string } | null>(null)
const messageKey = ref(0)
const tipIndex = ref(0)
const cheerIndex = ref(0)
let messageTimer: ReturnType<typeof setTimeout> | null = null

const canAutoplay = computed(() => !props.stageComplete && !message.value && !reduced.value && inView.value && pageVisible.value)
const scenes = computed(() => storyFor(props.riasecId, props.avatar.name))
const player = useStoryPlayer({ sceneCount: scenes.value.length, canAutoplay, loop: true })

const dimension = computed(() => getRiasecDimension(props.riasecId))
const propEntrance = computed(() => ({ ...presets.value.celebrate.animate, opacity: 1 }))
const currentScene = computed(() => scenes.value[player.scene.value] ?? scenes.value[0]!)

const DONE_MESSAGE = { title: '¡Terminaste!', line: 'Puedes revisar tus respuestas si gustas.' }
const CONFIRM_MESSAGE = { title: 'Antes de enviar', line: '¿Estás seguro de que quieres finalizar?', note: 'Si quieres revisar, toca «Atrás».' }
const finalMessage = computed(() => props.confirmingFinish ? CONFIRM_MESSAGE : DONE_MESSAGE)

const bubble = computed(() => props.stageComplete ? finalMessage.value : message.value ?? currentScene.value)
const bubbleKey = computed(() => {
  if (props.stageComplete) return props.confirmingFinish ? 'final-confirm' : 'final-done'
  return message.value ? `message-${messageKey.value}` : `scene-${player.scene.value}`
})

const announcement = ref('')

function remind(missing: 'skills' | 'reflection') {
  const line = missing === 'skills'
    ? 'Elige al menos una habilidad para continuar.'
    : 'Te falta responder la pregunta abierta para continuar.'
  announcement.value = line
  playParts('Antes de seguir', [line])
}

defineExpose({ remind })

watch(() => props.stageComplete, (complete) => {
  if (!complete) return
  if (messageTimer !== null) clearTimeout(messageTimer)
  message.value = null
  announcement.value = DONE_MESSAGE.line
})

watch(() => props.confirmingFinish, (confirming) => {
  if (confirming) announcement.value = `${CONFIRM_MESSAGE.line} ${CONFIRM_MESSAGE.note}`
})

function showMessage(kind: 'tip' | 'cheer' | 'limit') {
  if (kind === 'tip') {
    message.value = { title: 'Consejo', line: RIASEC_TIPS[tipIndex.value++ % RIASEC_TIPS.length]! }
  } else if (kind === 'limit') {
    message.value = { title: 'Máximo alcanzado', line: `Ya elegiste ${props.selectionLimit} habilidades, el máximo. Si quieres otra, primero quita una de las que marcaste.` }
  } else {
    const options = AVATAR_CHEERS[props.avatar.id] ?? [props.avatar.encouragement]
    message.value = { title: 'Ánimo', line: options[cheerIndex.value++ % options.length]! }
  }
  announcement.value = message.value.line
  playParts(message.value.title, splitMessage(message.value.line))
}

function splitMessage(line: string): string[] {
  if (line.length <= MAX_PART_CHARS) return [line]
  const sentences = line.split(/(?<=[.!?])\s+/).filter(Boolean)
  const parts: string[] = []
  for (const sentence of sentences) {
    const last = parts[parts.length - 1]
    if (last && last.length + sentence.length + 1 <= MAX_PART_CHARS) parts[parts.length - 1] = `${last} ${sentence}`
    else parts.push(sentence)
  }
  return parts
}

function playParts(title: string, parts: string[], index = 0) {
  if (messageTimer !== null) clearTimeout(messageTimer)
  const line = parts[index]
  if (line === undefined) {
    message.value = null
    return
  }
  message.value = { title, line }
  messageKey.value++
  const isLast = index === parts.length - 1
  messageTimer = setTimeout(() => playParts(title, parts, index + 1), isLast ? LAST_PART_MS : PART_MS)
}

const reaction = ref('')
const reactionKey = ref(0)
let reactionTimer: ReturnType<typeof setTimeout> | null = null

watch(() => props.selectedCount, (count, previous) => {
  if (count <= previous) return
  if (count >= props.selectionLimit) showMessage('limit')
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
  if (messageTimer !== null) clearTimeout(messageTimer)
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

.avatar-story.is-finish {
  position: relative;
  overflow: hidden;
  background: var(--gradient-brand-soft, var(--color-primary-light));
  border: 1.5px solid var(--color-primary);
  animation: story-finish-pop 700ms cubic-bezier(0.16, 1, 0.3, 1) both, story-finish-halo 2s ease-in-out 700ms 2;
}

.avatar-story.is-finish::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 30%, rgba(255, 255, 255, 0.6) 50%, transparent 70%);
  transform: translateX(-100%);
  animation: story-finish-sweep 1.8s ease-in-out 400ms 1 both;
  pointer-events: none;
}

@keyframes story-finish-pop {
  0% { transform: scale(0.97); }
  60% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

@keyframes story-finish-halo {
  0%, 100% { box-shadow: 0 10px 34px -6px rgba(var(--color-primary-rgb), 0.75), 0 0 0 0 rgba(var(--color-primary-rgb), 0.55); }
  50% { box-shadow: 0 14px 40px -6px rgba(var(--color-primary-rgb), 0.9), 0 0 0 14px rgba(var(--color-primary-rgb), 0); }
}

@keyframes story-finish-sweep {
  0% { transform: translateX(-100%); }
  60%, 100% { transform: translateX(100%); }
}

@media (prefers-reduced-motion: reduce) {
  .avatar-story.is-finish {
    animation: none;
  }

  .avatar-story.is-finish::after {
    display: none;
  }
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
  gap: 0.5rem 0.6rem;
  align-items: center;
  min-height: 9.5rem;
  padding: 2.5rem 0.6rem 1rem;
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

.story-avatar-face .selected-avatar-tracking {
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
  padding: 0.85rem 1.1rem;
  margin-right: -0.25rem;
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

.story-line-note {
  margin-top: 0.5rem;
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

</style>
