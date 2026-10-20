<template>
  <header class="athena-header">
    <div class="header-container">
      <!-- Brand Logo -->
      <NuxtLink to="/" class="brand-link" aria-label="ATHENA Inicio">
        <div class="brand-logo">
          <img src="/icons/athena-star.svg" alt="" width="36" height="36">
        </div>
        <span class="brand-text">ATHENA</span>
      </NuxtLink>

      <!-- Stepper Indicator -->
      <AthenaStepper />
    </div>
  </header>
</template>

<script setup lang="ts">
import AthenaStepper from './AthenaStepper.vue'
</script>

<style scoped>
.athena-header {
  position: sticky;
  top: 0;
  z-index: 50;
  width: 100%;
  height: var(--header-height);
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: var(--desktop-max-width);
  min-width: var(--desktop-min-width);
  height: 100%;
  margin: 0 auto;
  padding: 0 3rem;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  user-select: none;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 850;
  letter-spacing: 0.05em;
  color: var(--athena-dark-blue);
}
</style>
