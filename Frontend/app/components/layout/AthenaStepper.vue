<template>
  <nav class="athena-stepper" aria-label="Progreso del recorrido">
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
        <!-- Step connector line -->
        <span v-if="index > 0" class="step-connector" aria-hidden="true" />

        <!-- Functional navigable step -->
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

        <!-- Active or Non-clickable future step -->
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
  return 1 // default '/'
})
</script>

<style scoped>
.athena-stepper {
  display: flex;
  align-items: center;
}

.stepper-list {
  display: flex;
  align-items: center;
  list-style: none;
  gap: 0;
}

.step-item {
  display: flex;
  align-items: center;
}

.step-connector {
  width: 2.5rem;
  height: 1px;
  background-color: var(--color-border);
  margin: 0 0.6rem;
  flex-shrink: 0;
}

.step-item.is-completed .step-connector {
  background-color: var(--color-primary-border);
}

.step-link,
.step-content {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  user-select: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.step-badge {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface);
  color: var(--color-text-muted);
  transition: all 0.2s ease;
}

.step-label {
  color: var(--color-text-muted);
  transition: color 0.2s ease;
}

/* Active Step: Solid Purple Circle with white number */
.step-item.is-active .step-badge {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: #FFFFFF;
  box-shadow: 0 0 0 4px var(--color-primary-light);
}

.step-item.is-active .step-label {
  color: var(--color-primary);
  font-weight: 700;
}

/* Completed Step: Soft purple checked */
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
}

/* Future Step */
.step-item.is-future .step-badge {
  border-color: var(--color-border);
  background-color: #F8FAFC;
  color: var(--color-text-light);
}

.step-item.is-future .step-label {
  color: var(--color-text-light);
}

.check-icon {
  stroke: var(--color-primary);
}
</style>
