<template>
  <div class="intro-page">
    <IntroductionHero />
    <ApplicationDetails />
  </div>
</template>

<script setup lang="ts">
import IntroductionHero from '../features/introduccion/components/IntroductionHero.vue'
import ApplicationDetails from '../features/introduccion/components/ApplicationDetails.vue'

useHead({
  title: 'ATHENA | Sistema Inteligente de Orientación Vocacional'
})
</script>

<style scoped>
.intro-page {
  display: flex;
  flex-direction: column;
}
</style>
