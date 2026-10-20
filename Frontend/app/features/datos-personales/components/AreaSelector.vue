<template>
  <div class="area-selection-block">
    <div class="area-block-titles">
      <h3 class="area-block-heading">¿Qué área te gustaría explorar?</h3>
      <p class="area-block-subheading">Selecciona una opción para comenzar.</p>
    </div>

    <!-- Error state if areas fetch failed -->
    <ErrorMessage
      v-if="apiError"
      :message="apiError"
      :retryable="true"
      @retry="$emit('retry')"
    />

    <!-- Loading state -->
    <LoadingState v-else-if="loading" message="Cargando áreas de estudio..." />

    <!-- 3 Area Cards Grid -->
    <div v-else class="areas-grid" role="radiogroup" aria-label="Selección de área académica">
      <AreaCard
        v-for="area in areas"
        :key="area.id"
        :area="area"
        :is-selected="area.id === selectedId"
        @select="$emit('select', $event)"
      />
    </div>

    <span v-if="error" class="input-error" role="alert">
      {{ error }}
    </span>
  </div>
</template>

<script setup lang="ts">
import type { Area } from '../../../types/area'
import AreaCard from './AreaCard.vue'
import LoadingState from '../../../components/ui/LoadingState.vue'
import ErrorMessage from '../../../components/ui/ErrorMessage.vue'

defineProps<{
  areas: Area[]
  selectedId: number | null
  loading?: boolean
  apiError?: string | null
  error?: string
}>()

defineEmits<{
  select: [id: number]
  retry: []
}>()
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
