<template>
  <AnimatePresence :initial="false">
    <div v-if="show" class="confirm-dialog-root">
      <Motion
        class="confirm-dialog-backdrop"
        :initial="{ opacity: 0 }"
        :animate="{ opacity: 1 }"
        :exit="{ opacity: 0 }"
        :transition="{ duration: 0.2, ease: 'easeOut' }"
        @click="$emit('cancel')"
      />
      <Motion
        class="confirm-dialog-panel"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        :aria-describedby="messageId"
        :initial="presets.celebrate.initial"
        :animate="presets.celebrate.animate"
        :exit="{ opacity: 0, scale: 0.92, y: 16 }"
        :transition="presets.celebrate.transition"
      >
        <span class="confirm-dialog-sparkles" aria-hidden="true">
          <Motion
            v-for="(sparkle, index) in SPARKLES"
            :key="index"
            as="span"
            class="confirm-dialog-sparkle"
            :style="{ left: sparkle.left, top: sparkle.top }"
            :initial="presets.sparkle.initial"
            :animate="presets.sparkle.animate"
            :transition="{ ...presets.sparkle.transition, delay: index * 0.08 }"
          >✦</Motion>
        </span>

        <img
          v-if="avatar"
          class="confirm-dialog-avatar"
          :src="avatar.image"
          :alt="avatar.name"
          width="72"
          height="72"
        >
        <span v-else class="confirm-dialog-badge" aria-hidden="true">✦</span>

        <h2 :id="titleId" class="confirm-dialog-title">{{ title }}</h2>
        <p :id="messageId" class="confirm-dialog-message">{{ message }}</p>

        <div class="confirm-dialog-actions">
          <BaseButton variant="outline" size="md" @click="$emit('cancel')">
            {{ cancelLabel }}
          </BaseButton>
          <button
            type="button"
            class="confirm-finish-btn is-celebrating is-finish"
            @click="$emit('confirm')"
          >
            <span class="confirm-finish-sparkles" aria-hidden="true">
              <span v-for="n in 5" :key="n" class="confirm-finish-sparkle" :style="{ '--i': n }">✦</span>
            </span>
            <span class="confirm-finish-text">{{ confirmLabel }}</span>
            <span aria-hidden="true">›</span>
          </button>
        </div>
      </Motion>
    </div>
  </AnimatePresence>
</template>

<script setup lang="ts">
import { computed, useId } from 'vue'
import type { Avatar } from '../../types/avatar'
import { useMotionPresets } from '../../composables/useMotionPresets'
import BaseButton from './BaseButton.vue'

withDefaults(
  defineProps<{
    show: boolean
    title: string
    message: string
    confirmLabel?: string
    cancelLabel?: string
    avatar?: Avatar | null
  }>(),
  {
    confirmLabel: 'Confirmar',
    cancelLabel: 'Cancelar',
    avatar: null
  }
)

defineEmits<{
  confirm: []
  cancel: []
}>()

const presets = useMotionPresets()

const uid = useId()
const titleId = computed(() => `confirm-dialog-title-${uid}`)
const messageId = computed(() => `confirm-dialog-message-${uid}`)

const SPARKLES = [
  { left: '10%', top: '22%' },
  { left: '28%', top: '74%' },
  { left: '52%', top: '14%' },
  { left: '74%', top: '70%' },
  { left: '90%', top: '30%' }
]
</script>

<style scoped>
.confirm-dialog-root {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 1.25rem;
}

.confirm-dialog-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(15, 15, 25, 0.5);
  backdrop-filter: blur(2px);
}

.confirm-dialog-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.5rem;
  width: min(420px, 100%);
  padding: clamp(1.5rem, 4vw, 2.25rem);
  background: var(--gradient-brand-soft, var(--color-surface));
  border: 1.5px solid var(--color-primary-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-pop);
  overflow: hidden;
}

.confirm-dialog-sparkles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.confirm-dialog-sparkle {
  position: absolute;
  font-size: 1rem;
  color: var(--color-accent);
}

.confirm-dialog-avatar {
  width: 72px;
  height: 72px;
  margin-bottom: 0.25rem;
  object-fit: contain;
  filter: drop-shadow(0 6px 14px rgba(var(--color-primary-rgb), 0.3));
}

.confirm-dialog-badge {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin-bottom: 0.25rem;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: var(--color-on-primary);
  font-size: 1.2rem;
  box-shadow: var(--shadow-glow);
}

.confirm-dialog-title {
  font-family: var(--font-display);
  font-size: var(--text-subtitle, 1.25rem);
  font-weight: 800;
  color: var(--color-primary);
}

.confirm-dialog-message {
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text-secondary);
  text-wrap: pretty;
}

.confirm-dialog-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

/* --- Botón "Sí, quiero finalizar": misma animación que "Finalizar etapa" --- */
.confirm-finish-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  overflow: hidden;
  min-height: 56px;
  padding: 0 1.9rem;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  border-radius: var(--radius-full);
  background: var(--gradient-brand-soft, var(--color-primary-light));
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
  transition: transform var(--motion-base) ease, box-shadow var(--motion-base) ease, filter var(--motion-base) ease;
}

.confirm-finish-btn.is-celebrating.is-finish {
  animation: confirm-finish-pop 700ms cubic-bezier(0.16, 1, 0.3, 1) both, confirm-finish-halo 2s ease-in-out 700ms infinite;
}

.confirm-finish-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.04);
}

.confirm-finish-btn:active {
  transform: translateY(0) scale(0.97);
}

.confirm-finish-btn:focus-visible {
  outline: 3px solid var(--color-primary);
  outline-offset: 3px;
}

.confirm-finish-btn span[aria-hidden='true'] {
  font-size: 1.3rem;
  transition: transform var(--motion-base) ease;
}

.confirm-finish-btn:hover > span[aria-hidden='true'] {
  transform: translateX(4px);
}

.confirm-finish-btn.is-celebrating.is-finish::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 30%, rgba(255, 255, 255, 0.75) 50%, transparent 70%);
  transform: translateX(-100%);
  animation: confirm-finish-sweep 3s ease-in-out infinite;
  pointer-events: none;
}

.confirm-finish-sparkles {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border-radius: inherit;
  pointer-events: none;
}

.confirm-finish-sparkle {
  position: absolute;
  left: calc(var(--i) * 20% - 10%);
  top: 50%;
  font-size: 0.9rem;
  color: var(--color-primary);
  opacity: 0;
  animation: confirm-finish-sparkle 2.2s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.3s);
}

.confirm-finish-sparkle:nth-child(odd) {
  top: 6px;
}

.confirm-finish-sparkle:nth-child(even) {
  top: calc(100% - 20px);
}

@keyframes confirm-finish-pop {
  0% {
    transform: scale(0.94);
  }

  60% {
    transform: scale(1.06);
  }

  100% {
    transform: scale(1);
  }
}

@keyframes confirm-finish-halo {

  0%,
  100% {
    box-shadow: 0 10px 34px -6px rgba(var(--color-primary-rgb), 0.75), 0 0 0 0 rgba(var(--color-primary-rgb), 0.55);
  }

  50% {
    box-shadow: 0 14px 40px -6px rgba(var(--color-primary-rgb), 0.9), 0 0 0 14px rgba(var(--color-primary-rgb), 0);
  }
}

@keyframes confirm-finish-sweep {
  0% {
    transform: translateX(-100%);
  }

  60%,
  100% {
    transform: translateX(100%);
  }
}

@keyframes confirm-finish-sparkle {

  0%,
  100% {
    opacity: 0;
    transform: translateY(4px) scale(0.6);
  }

  50% {
    opacity: 1;
    transform: translateY(-6px) scale(1.15);
  }
}

@media (prefers-reduced-motion: reduce) {
  .confirm-finish-btn.is-celebrating.is-finish {
    animation: none;
    box-shadow: 0 10px 34px -6px rgba(var(--color-primary-rgb), 0.75);
  }

  .confirm-finish-btn.is-celebrating.is-finish::after {
    animation: none;
    display: none;
  }

  .confirm-finish-sparkle {
    animation: none;
    opacity: 0.8;
  }

  .confirm-finish-btn:hover,
  .confirm-finish-btn:hover > span[aria-hidden='true'] {
    transform: none;
  }
}
</style>
