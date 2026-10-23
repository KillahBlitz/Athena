<template>
  <header class="athena-header">
    <div class="header-container">
      <NuxtLink to="/" class="brand-link" aria-label="ATHENA Inicio" @click.capture="session.reset()">
        <div class="brand-logo">
          <img src="/icons/athena-star.svg" alt="" width="36" height="36">
        </div>
        <span class="brand-text">ATHENA</span>
      </NuxtLink>

      <AthenaStepper />
    </div>
  </header>
</template>

<script setup lang="ts">
import AthenaStepper from './AthenaStepper.vue'
import { useAthenaSessionStore } from '../../stores/athenaSession'

const session = useAthenaSessionStore()
</script>

<style scoped>
.athena-header {
  position: sticky;
  top: 0;
  z-index: 50;
  width: 100%;
  height: var(--header-height);
  background-color: var(--surface-glass);
  backdrop-filter: saturate(1.6) blur(14px);
  -webkit-backdrop-filter: saturate(1.6) blur(14px);
  border-bottom: 1px solid var(--color-border);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  max-width: var(--desktop-max-width);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--space-page-x);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-height: var(--tap-target);
  user-select: none;
  flex-shrink: 0;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-logo img {
  width: clamp(28px, 6vw, 36px);
  height: auto;
}

.brand-text {
  font-family: var(--font-display);
  font-size: clamp(1.05rem, 0.95rem + 0.5vw, 1.3rem);
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--athena-dark-blue);
}
</style>
