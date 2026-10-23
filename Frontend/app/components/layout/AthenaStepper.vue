<template>
  <nav class="athena-stepper" aria-label="Progreso del recorrido">
    <div class="stepper-compact">
      <div class="compact-labels">
        <span class="compact-count">Paso {{ activeStepNumber }} de {{ steps.length }}</span>
        <span class="compact-current">{{ activeStep?.label }}</span>
      </div>
      <div
        class="compact-track"
        role="progressbar"
        :aria-valuenow="progressPercentage"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-label="`Paso ${activeStepNumber} de ${steps.length}`"
      >
        <span class="compact-fill" :style="{ width: `${progressPercentage}%` }" />
      </div>
    </div>

    <ol class="stepper-list">
      <li
        v-for="(step, index) in steps"
        :key="step.number"
        class="step-item"
        :class="{
          'is-active': activeStepNumber === step.number,
          'is-completed': activeStepNumber > step.number,
          'is-future': activeStepNumber < step.number
        }"
      >
        <span v-if="index > 0" class="step-connector" aria-hidden="true" />

        <NuxtLink
          v-if="step.isFunctional && activeStepNumber > step.number"
          :to="step.path"
          class="step-link"
          :title="`Volver a ${step.label}`"
        >
          <span class="step-badge">
            <svg class="check-icon" viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor">
              <path d="M3.5 8.5 L6.5 11.5 L12.5 4.5" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <span class="step-label">{{ step.label }}</span>
        </NuxtLink>

        <div
          v-else
          class="step-content"
          :aria-current="activeStepNumber === step.number ? 'step' : undefined"
        >
          <span class="step-badge">
            <span v-if="activeStepNumber > step.number">✓</span>
            <span v-else>{{ step.number }}</span>
          </span>
          <span class="step-label">{{ step.label }}</span>
        </div>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { athenaSteps } from '../../config/steps'

const route = useRoute()
const steps = athenaSteps

const activeStepNumber = computed(() => {
  const path = route.path
  if (path.startsWith('/datos-personales')) return 2
  if (path.startsWith('/objetivos')) return 3
  if (path.startsWith('/riasec')) return 4
  if (path.startsWith('/espera')) return 5
  return 1
})

const activeStep = computed(() => steps.find(step => step.number === activeStepNumber.value))
const progressPercentage = computed(() => Math.round((activeStepNumber.value / steps.length) * 100))
</script>

<style scoped>
.athena-stepper {
  display: flex;
  align-items: center;
  min-width: 0;
}

.stepper-compact {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  width: min(11rem, 46vw);
}

.compact-labels {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.compact-current {
  color: var(--color-primary);
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
}

.compact-track {
  height: 6px;
  border-radius: var(--radius-full);
  background-color: var(--color-primary-light);
  overflow: hidden;
}

.compact-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--gradient-brand);
  transition: width var(--motion-slow) var(--ease-out);
}

.stepper-list {
  display: none;
  align-items: center;
  list-style: none;
  gap: 0;
}

@media (min-width: 1024px) {
  .stepper-compact {
    display: none;
  }

  .stepper-list {
    display: flex;
  }
}

.step-item {
  display: flex;
  align-items: center;
}

.step-connector {
  width: clamp(1rem, 2vw, 2.5rem);
  height: 2px;
  border-radius: var(--radius-full);
  background-color: var(--color-border);
  margin: 0 0.6rem;
  flex-shrink: 0;
}

.step-item.is-completed .step-connector,
.step-item.is-active .step-connector {
  background: var(--gradient-brand);
}

.step-link,
.step-content {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: var(--tap-target);
  user-select: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: color var(--motion-base) ease;
}

.step-badge {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface);
  color: var(--color-text-muted);
  transition: transform var(--motion-base) var(--ease-spring), background-color var(--motion-base) ease, border-color var(--motion-base) ease;
}

.step-label {
  color: var(--color-text-muted);
  transition: color var(--motion-base) ease;
}

.step-item.is-active .step-badge {
  background: var(--gradient-primary);
  border-color: var(--color-primary);
  color: var(--color-on-primary);
  box-shadow: 0 0 0 4px var(--color-primary-light);
}

.step-item.is-active .step-label {
  color: var(--color-primary);
  font-weight: 700;
}

.step-item.is-completed .step-badge {
  border-color: var(--color-primary-border);
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.step-item.is-completed .step-label {
  color: var(--color-text-secondary);
}

.step-link:hover .step-label {
  color: var(--color-primary);
}

.step-link:hover .step-badge {
  border-color: var(--color-primary);
  transform: scale(1.08);
}

.step-item.is-future .step-badge {
  border-color: var(--color-border);
  background-color: var(--color-surface-hover);
  color: var(--color-text-muted);
}

.step-item.is-future .step-label {
  color: var(--color-text-muted);
}

.check-icon {
  stroke: var(--color-primary);
}

@media (prefers-reduced-motion: reduce) {
  .step-link:hover .step-badge {
    transform: none;
  }
}
</style>
