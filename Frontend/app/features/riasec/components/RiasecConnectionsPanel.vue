<template>
  <aside class="riasec-connections" aria-label="Nuevas conexiones">
    <span class="riasec-connections-eyebrow">
      <span aria-hidden="true">✦</span>
      <span>NUEVAS CONEXIONES</span>
    </span>

    <svg class="riasec-constellation" viewBox="0 0 240 190" fill="none" aria-hidden="true">
      <ellipse cx="120" cy="95" rx="104" ry="78" class="constellation-orbit" />
      <polyline
        v-if="selectedPoints.length > 1"
        :points="polylinePoints"
        class="constellation-line"
      />
      <circle
        v-for="node in nodes"
        :key="node.id"
        :cx="node.x"
        :cy="node.y"
        :r="node.selected ? 4.5 : 3"
        class="constellation-node"
        :class="{ 'is-selected': node.selected }"
      />
    </svg>

    <div class="riasec-connections-message">
      <span class="riasec-connections-avatar" aria-hidden="true">
        <img :src="avatar.image" alt="">
      </span>
      <strong>Cada habilidad revela algo único de ti.</strong>
    </div>
    <p class="riasec-connections-note">
      No necesitas dominarlo todo. Elige lo que reconoces en ti, dentro y fuera del aula.
    </p>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Avatar } from '../../../types/avatar'
import type { RiasecOption } from '../../../types/riasec'

const props = defineProps<{
  options: RiasecOption[]
  selectedIds: number[]
  avatar: Avatar
}>()

const nodes = computed(() => {
  const total = props.options.length || 1
  return props.options.map((option, index) => {
    const angle = (index / total) * Math.PI * 2 - Math.PI / 2
    const jitter = 0.62 + ((index * 37) % 38) / 100
    return {
      id: option.opcionId,
      x: Math.round(120 + Math.cos(angle) * 104 * jitter),
      y: Math.round(95 + Math.sin(angle) * 78 * jitter),
      selected: props.selectedIds.includes(option.opcionId)
    }
  })
})

const selectedPoints = computed(() =>
  props.selectedIds
    .map(id => nodes.value.find(n => n.id === id))
    .filter((n): n is NonNullable<typeof n> => Boolean(n))
)

const polylinePoints = computed(() => {
  const points = selectedPoints.value.map(n => `${n.x},${n.y}`)
  if (selectedPoints.value.length > 2) points.push(points[0] as string)
  return points.join(' ')
})
</script>

<style scoped>
@import '../styles/riasec.css';
</style>
