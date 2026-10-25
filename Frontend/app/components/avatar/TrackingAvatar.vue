<template>
  <span ref="root" class="tracking-avatar" role="img" :aria-label="name" :style="layerStyle">
    <img class="avatar-body" :src="source" alt="" draggable="false" width="1254" height="1254">
    <img class="avatar-head" :src="source" alt="" draggable="false" width="1254" height="1254">
  </span>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ avatarId: string; name: string }>()
const root = ref<HTMLElement | null>(null)
const source = computed(() => `/avatars/${props.avatarId}-full.webp`)
// The PNGs share a square canvas; each character has a different neckline.
const necklines: Record<string, number> = { atlas: 49, nova: 57, pixel: 51, orion: 56 }
const layerStyle = computed(() => ({ '--neck': `${necklines[props.avatarId] ?? 55}%` }))
let frame = 0
let pointer: { x: number; y: number } | null = null
let motionQuery: MediaQueryList | undefined
let mouseQuery: MediaQueryList | undefined

function reset() {
  pointer = null
  cancelAnimationFrame(frame)
  frame = 0
  root.value?.style.setProperty('--head-transform', 'rotateX(0deg) rotateY(0deg) rotateZ(0deg)')
}

function update() {
  frame = 0
  const element = root.value
  if (!element || !pointer) return
  const bounds = element.getBoundingClientRect()
  if (!bounds.width || !bounds.height) return
  const clamp = (value: number) => Math.max(-1, Math.min(1, value))
  const x = clamp((pointer.x - bounds.left - bounds.width / 2) / 320)
  const y = clamp((pointer.y - bounds.top - bounds.height * 0.3) / 320)
  element.style.setProperty('--head-transform', `rotateX(${-y * 5}deg) rotateY(${x * 9}deg) rotateZ(${x * 3}deg)`)
}

function follow(event: PointerEvent) {
  if (event.pointerType !== 'mouse' || motionQuery?.matches || !mouseQuery?.matches) return
  pointer = { x: event.clientX, y: event.clientY }
  if (!frame) frame = requestAnimationFrame(update)
}

function handleVisibility() {
  if (document.hidden) reset()
}

watch(() => props.avatarId, reset)

onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  mouseQuery = window.matchMedia('(any-hover: hover) and (any-pointer: fine)')
  motionQuery.addEventListener('change', reset)
  mouseQuery.addEventListener('change', reset)
  window.addEventListener('pointermove', follow, { passive: true })
  window.addEventListener('blur', reset)
  window.addEventListener('scroll', reset, { passive: true })
  document.documentElement.addEventListener('pointerleave', reset)
  document.addEventListener('visibilitychange', handleVisibility)
})

onBeforeUnmount(() => {
  reset()
  motionQuery?.removeEventListener('change', reset)
  mouseQuery?.removeEventListener('change', reset)
  window.removeEventListener('pointermove', follow)
  window.removeEventListener('blur', reset)
  window.removeEventListener('scroll', reset)
  document.documentElement.removeEventListener('pointerleave', reset)
  document.removeEventListener('visibilitychange', handleVisibility)
})
</script>

<style scoped>
.tracking-avatar {
  position: relative;
  display: block;
  width: 100%;
  aspect-ratio: 1;
  perspective: 500px;
  pointer-events: none;
}
.tracking-avatar img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  user-select: none;
}
.avatar-body {
  mask-image: linear-gradient(to bottom, transparent calc(var(--neck) - 1%), #000 calc(var(--neck) - 1%));
}
.avatar-head {
  mask-image: linear-gradient(to bottom, #000 calc(var(--neck) - 1%), transparent calc(var(--neck) + 1%));
  transform-origin: 50% var(--neck);
  transform: var(--head-transform, rotateX(0deg) rotateY(0deg) rotateZ(0deg));
  transition: transform 180ms ease-out;
}
@media (prefers-reduced-motion: reduce) {
  .avatar-head { transform: none; transition: none; }
}
</style>
