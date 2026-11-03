<template>
  <figure class="constellation">
    <svg
      class="constellation-svg"
      :viewBox="`0 0 ${WIDTH} ${HEIGHT}`"
      role="img"
      :aria-labelledby="`${uid}-title ${uid}-desc`"
    >
      <title :id="`${uid}-title`">Constelación vocacional</title>
      <desc :id="`${uid}-desc`">{{ description }}</desc>

      <defs>
        <radialGradient :id="`${uid}-glow`">
          <stop offset="0%" stop-color="var(--results-violet)" stop-opacity="0.4" />
          <stop offset="100%" stop-color="var(--results-violet)" stop-opacity="0" />
        </radialGradient>
      </defs>

      <!-- Órbita de referencia -->
      <circle :cx="CX" :cy="CY" :r="MAX_R" class="constellation-orbit" />

      <!-- Estrellas de fondo -->
      <circle v-for="(dot, i) in DUST" :key="`dust-${i}`" :cx="dot.x" :cy="dot.y" :r="dot.r" class="constellation-dust" :class="dot.tone" />

      <!-- Brillo de la dimensión dominante -->
      <circle v-if="dominant" :cx="dominant.x" :cy="dominant.y" r="48" :fill="`url(#${uid}-glow)`" />

      <!-- Conexiones internas -->
      <line
        v-for="(link, i) in innerLinks"
        :key="`inner-${i}`"
        :x1="link.from.x" :y1="link.from.y" :x2="link.to.x" :y2="link.to.y"
        class="constellation-inner"
      />

      <!-- Contorno del perfil -->
      <polygon :points="polygonPoints" class="constellation-shape" />

      <!-- Nodos y etiquetas -->
      <g v-for="node in nodes" :key="node.riasecId" :class="{ 'is-dominant': node.isDominant }">
        <path :d="starPath(node.x, node.y, node.isDominant ? 9 : 7)" class="constellation-node" />
        <text
          :x="node.labelX"
          :y="node.labelY"
          :text-anchor="node.anchor"
          dominant-baseline="middle"
          class="constellation-label"
        >{{ node.name }}</text>
      </g>
    </svg>
  </figure>
</template>

<script setup lang="ts">
import { computed, useId } from 'vue'
import { getRiasecDimension } from '../../riasec/config/riasecDimensions'
import type { DimensionScore } from '../types'

const props = defineProps<{
  scores: DimensionScore[]
  dominantRiasecId: number
}>()

const uid = useId()

const WIDTH = 420
const HEIGHT = 340
const CX = 210
const CY = 170
const MAX_R = 120
// Orden clásico del hexágono RIASEC, empezando por Investigador arriba.
const ORDER = [2, 3, 4, 5, 6, 1]

const DUST = [
  { x: 40, y: 30, r: 1.4, tone: '' },
  { x: 380, y: 26, r: 1.6, tone: 'is-cyan' },
  { x: 330, y: 60, r: 1.2, tone: 'is-cyan' },
  { x: 396, y: 250, r: 1.2, tone: '' },
  { x: 30, y: 300, r: 1.4, tone: '' },
  { x: 150, y: 330, r: 1.4, tone: 'is-cyan' }
]

const clamp = (n: number) => Math.min(1, Math.max(0, n))

const nodes = computed(() => ORDER.map((riasecId, i) => {
  const angle = (-90 + i * 60) * (Math.PI / 180)
  const score = clamp(props.scores.find(s => s.riasecId === riasecId)?.score ?? 0)
  const r = MAX_R * (0.3 + 0.7 * score)
  const cos = Math.cos(angle)
  const sin = Math.sin(angle)
  const x = CX + r * cos
  const y = CY + r * sin
  const vertical = Math.abs(cos) < 0.2
  // Arriba: etiqueta a la derecha del nodo. Abajo: centrada debajo. Laterales: hacia afuera.
  let anchor: 'start' | 'middle' | 'end' = cos > 0 ? 'start' : 'end'
  let labelX = x + cos * 16
  let labelY = y + sin * 10
  if (vertical && sin < 0) {
    anchor = 'start'
    labelX = x + 14
    labelY = y
  } else if (vertical) {
    anchor = 'middle'
    labelX = x
    labelY = y + 20
  }
  return {
    riasecId,
    name: getRiasecDimension(riasecId).name,
    score,
    isDominant: riasecId === props.dominantRiasecId,
    x,
    y,
    labelX,
    labelY,
    anchor
  }
}))

const dominant = computed(() => nodes.value.find(n => n.isDominant) ?? null)

const polygonPoints = computed(() => nodes.value.map(n => `${n.x.toFixed(1)},${n.y.toFixed(1)}`).join(' '))

// Diagonales tenues entre dimensiones opuestas, como en el mockup.
const innerLinks = computed(() => {
  const list = nodes.value
  return [[0, 3], [1, 4], [2, 5]]
    .map(([a, b]) => ({ from: list[a!]!, to: list[b!]! }))
})

const description = computed(() => {
  const ranked = [...nodes.value].sort((a, b) => b.score - a.score)
  return `Puntajes por dimensión: ${ranked.map(n => `${n.name} ${Math.round(n.score * 100)}%`).join(', ')}.`
})

function starPath(x: number, y: number, size: number) {
  const s = size
  const k = s * 0.28
  return `M${x} ${y - s} L${x + k} ${y - k} L${x + s} ${y} L${x + k} ${y + k} L${x} ${y + s} L${x - k} ${y + k} L${x - s} ${y} L${x - k} ${y - k} Z`
}
</script>

<style scoped>
.constellation {
  margin: 0;
  width: 100%;
}

.constellation-svg {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
}

.constellation-orbit {
  fill: rgba(255, 255, 255, 0.18);
  stroke: rgba(var(--color-primary-rgb), 0.14);
  stroke-width: 1;
}

.constellation-dust {
  fill: var(--results-violet);
  opacity: 0.6;
}

.constellation-dust.is-cyan {
  fill: var(--results-cyan);
}

.constellation-inner {
  stroke: rgba(var(--color-primary-rgb), 0.16);
  stroke-width: 1;
}

.constellation-shape {
  fill: rgba(var(--color-primary-rgb), 0.04);
  stroke: var(--results-violet);
  stroke-width: 1.6;
  stroke-linejoin: round;
}

.constellation-node {
  fill: var(--results-violet);
  stroke: #FFFFFF;
  stroke-width: 0.8;
}

.is-dominant .constellation-node {
  fill: var(--color-primary);
}

.constellation-label {
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 500;
  fill: var(--color-text-secondary);
}

.is-dominant .constellation-label {
  font-size: 13px;
  font-weight: 700;
  fill: var(--color-primary);
}
</style>
