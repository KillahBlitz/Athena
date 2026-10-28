<template>
  <div class="waiting-page">
    <section class="waiting-card" aria-labelledby="waiting-title">
      <div class="waiting-orbit" aria-hidden="true">
        <span class="waiting-ring" />
        <span class="waiting-ring waiting-ring-outer" />
        <span
          v-for="(star, index) in STARS"
          :key="index"
          class="waiting-star"
          :style="{ left: star.left, top: star.top, animationDelay: `${index * 0.35}s` }"
        >✦</span>
        <Motion
          class="waiting-avatar"
          :animate="presets.breathe.animate"
          :transition="presets.breathe.transition"
        >
          <TrackingAvatar class="waiting-avatar-tracking" :avatar-id="selectedAvatar.id" :name="selectedAvatar.name" />
        </Motion>
      </div>

      <span class="eyebrow">
        <span>✦</span>
        <span>TEST COMPLETADO</span>
      </span>
      <h1 id="waiting-title" class="page-title">Estamos conectando tus estrellas.</h1>
      <p class="page-description waiting-description">
        Guardamos tus respuestas{{ firstName ? `, ${firstName}` : '' }}. ATHENA está analizando tus objetivos y
        habilidades para preparar tu recomendación vocacional.
      </p>

      <ol class="waiting-steps" role="status" aria-live="polite">
        <li
          v-for="step in STEPS"
          :key="step.statusId"
          class="waiting-step"
          :class="{ 'is-done': statusId !== null && step.statusId < statusId, 'is-active': step.statusId === statusId }"
          :aria-current="step.statusId === statusId ? 'step' : undefined"
        >
          <span class="waiting-step-dot" aria-hidden="true">
            <svg v-if="statusId !== null && step.statusId < statusId" viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor">
              <path d="M3.5 8.5 L6.5 11.5 L12.5 4.5" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <span>{{ step.label }}</span>
        </li>
      </ol>

      <p v-if="statusError" class="waiting-hint" role="status">{{ statusError }}</p>
      <p class="waiting-hint">
        <span class="waiting-avatar-name">{{ selectedAvatar.name }} · </span>
        <span>Esto puede tardar unos momentos. Puedes dejar esta pantalla abierta.</span>
      </p>
      <AvatarCompanion :avatar="selectedAvatar" :name="firstName" stage="waiting" />
    </section>
  </div>
</template>

<script setup lang="ts">
import TrackingAvatar from '../components/avatar/TrackingAvatar.vue'
import AvatarCompanion from '../components/avatar/AvatarCompanion.vue'
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAthenaSessionStore } from '../stores/athenaSession'
import { EVALUATION_UUID_KEY, getEvaluationUuid } from '../utils/evaluationStorage'
import { useMotionPresets } from '../composables/useMotionPresets'
import { useResultsApi } from '../composables/useResultsApi'
import type { GetResultsResponseDTO } from '../types/api'

useHead({
  title: 'ATHENA | Preparando tus resultados'
})

const STEPS = [
  { statusId: 1, label: 'Conociendo tus intereses' },
  { statusId: 2, label: 'Buscando carreras afines a ti' },
  { statusId: 3, label: 'Preparando tu recomendación' }
]

const STARS = [
  { left: '8%', top: '30%' },
  { left: '22%', top: '6%' },
  { left: '78%', top: '10%' },
  { left: '92%', top: '58%' },
  { left: '70%', top: '90%' },
  { left: '14%', top: '80%' }
]

const router = useRouter()
const session = useAthenaSessionStore()
const presets = useMotionPresets()
const { fetchResults } = useResultsApi()

const selectedAvatar = computed(() => session.selectedAvatar)
const firstName = computed(() => session.name.split(' ')[0] ?? '')

const statusId = ref<GetResultsResponseDTO['status_id'] | null>(null)
const statusError = ref<string | null>(null)
let timer: ReturnType<typeof setInterval> | null = null
let pendingRequest: AbortController | null = null

const stopPolling = () => {
  if (timer !== null) clearInterval(timer)
  timer = null
  pendingRequest?.abort()
}

const refreshStatus = async () => {
  const uuid = getEvaluationUuid()
  if (!uuid) {
    stopPolling()
    await router.replace('/riasec')
    return
  }
  if (pendingRequest) return

  const request = new AbortController()
  pendingRequest = request
  try {
    const result = await fetchResults(uuid, request.signal)
    if (request.signal.aborted || getEvaluationUuid() !== uuid) return
    statusId.value = result.status_id
    statusError.value = null
    if (result.status_id === 4) {
      stopPolling()
      await router.replace('/resultados')
    }
  } catch {
    if (!request.signal.aborted && getEvaluationUuid() === uuid) {
      statusError.value = 'No pudimos consultar el estado de tu evaluación. Volveremos a intentarlo en unos segundos.'
    }
  } finally {
    pendingRequest = null
  }
}

const handleStorageChange = (event: StorageEvent) => {
  if ((event.key === EVALUATION_UUID_KEY || event.key === null) && !getEvaluationUuid()) {
    stopPolling()
    router.replace('/riasec')
  }
}

onMounted(() => {
  if (!getEvaluationUuid()) {
    router.replace('/riasec')
    return
  }
  session.restore()
  window.addEventListener('storage', handleStorageChange)
  timer = setInterval(() => { void refreshStatus() }, 5000)
  void refreshStatus()
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', handleStorageChange)
  stopPolling()
})
</script>

<style scoped>
.waiting-page {
  display: grid;
  place-items: center;
  min-height: calc(100dvh - var(--header-height) - 10rem);
}

.waiting-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: min(100%, 640px);
  padding: clamp(1.75rem, 5vw, 3rem) clamp(1.25rem, 5vw, 3rem);
  text-align: center;
  background: var(--gradient-brand-soft);
  border: 1.5px solid var(--color-primary-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-pop);
}

.waiting-orbit {
  position: relative;
  display: grid;
  place-items: center;
  width: 180px;
  height: 180px;
  margin-bottom: 1.5rem;
}

.waiting-ring {
  position: absolute;
  inset: 18px;
  border: 2px dashed var(--color-primary-border);
  border-radius: 50%;
  animation: waiting-spin 14s linear infinite;
}

.waiting-ring-outer {
  inset: 0;
  border-style: solid;
  border-color: transparent;
  border-top-color: var(--color-primary);
  border-right-color: var(--athena-cyan);
  animation-duration: 2.4s;
}

.waiting-star {
  position: absolute;
  font-size: 0.85rem;
  color: var(--color-accent);
  animation: waiting-twinkle 2.1s ease-in-out infinite;
}

.waiting-avatar {
  display: grid;
  place-items: center;
  width: 108px;
  height: 108px;
  border-radius: 50%;
  background: var(--color-surface);
  box-shadow: var(--shadow-glow);
  overflow: hidden;
}

.waiting-avatar .waiting-avatar-tracking {
  width: 82%;
  height: 82%;
  object-fit: contain;
}

.waiting-description {
  max-width: 46ch;
  margin-bottom: 1.75rem;
}

.waiting-steps {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  width: min(100%, 360px);
  margin-bottom: 1.75rem;
  text-align: left;
}

.waiting-step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text-light);
  transition: color var(--motion-base) ease;
}

.waiting-step.is-active {
  color: var(--color-text-main);
  font-weight: 700;
}

.waiting-step.is-done {
  color: var(--color-text-secondary);
}

.waiting-step-dot {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border: 2px solid var(--color-border-hover);
  border-radius: 50%;
  background: var(--color-surface);
  transition: background var(--motion-base) ease, border-color var(--motion-base) ease;
}

.is-active .waiting-step-dot {
  border-color: var(--color-primary);
  border-top-color: transparent;
  animation: waiting-spin 0.9s linear infinite;
}

.is-done .waiting-step-dot {
  border-color: transparent;
  background: var(--gradient-primary);
  color: var(--color-on-primary);
}

.waiting-hint {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-wrap: pretty;
}

.waiting-avatar-name {
  font-weight: 700;
  color: var(--color-primary);
}

@keyframes waiting-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes waiting-twinkle {
  0%, 100% {
    opacity: 0.2;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.15);
  }
}

@media (prefers-reduced-motion: reduce) {
  .waiting-ring,
  .waiting-star,
  .is-active .waiting-step-dot {
    animation: none;
  }
}
</style>
