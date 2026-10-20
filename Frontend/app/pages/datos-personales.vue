<template>
  <div class="datos-personales-page">
    <div class="page-heading">
      <span class="eyebrow">
        <span>✦</span>
        <span>CONOCERTE ES EL PRIMER PASO</span>
      </span>
      <h1 class="page-title">Empecemos por ti.</h1>
      <p class="page-description">
        Cuéntanos un poco de ti y elige el área académica que te interesa explorar.
      </p>
    </div>

    <PersonalDataForm />
  </div>
</template>

<script setup lang="ts">
import PersonalDataForm from '../features/datos-personales/components/PersonalDataForm.vue'

useHead({
  title: 'ATHENA | Datos personales y selección de área'
})
</script>

<style scoped>
.datos-personales-page {
  display: flex;
  flex-direction: column;
}

.page-heading {
  margin-bottom: 2rem;
}
</style>
