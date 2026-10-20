<template>
  <div class="app-container">
    <AthenaHeader />
    <main class="main-content">
      <slot />
    </main>
    <footer class="app-footer">
      <span>ATHENA · Un universo de posibilidades, un camino propio.</span>
      <span class="app-footer-protected">
        <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor">
          <path d="M10 2 L4 4.5 V9.5 C4 13.8 6.6 17.1 10 18.2 C13.4 17.1 16 13.8 16 9.5 V4.5 L10 2 Z" stroke-width="1.6" stroke-linejoin="round"/>
          <path d="M7.5 10 L9.2 11.7 L12.5 8.3" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>Tu información, siempre protegida</span>
      </span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import AthenaHeader from '../components/layout/AthenaHeader.vue'
</script>
