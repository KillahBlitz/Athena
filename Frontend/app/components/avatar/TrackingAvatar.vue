<template>
  <span ref="root" class="tracking-avatar" role="img" :aria-label="name" :style="layerStyle">
    <span ref="stage" class="avatar-stage">
      <img class="avatar-body" :src="source" alt="" draggable="false" width="1254" height="1254">
      <span ref="head" class="avatar-head">
        <img class="avatar-head-img" :src="source" alt="" draggable="false" width="1254" height="1254">
        <template v-if="eyeLayers">
          <span
            v-for="(eye, i) in eyeLayers"
            :key="`${avatarId}-eye-${i}`"
            class="avatar-eye"
            :style="{ clipPath: eye.clip }"
          >
            <img data-eye-img :src="source" alt="" draggable="false" :style="eye.imgStyle">
          </span>
          <span
            v-for="(eye, i) in eyeLayers"
            :key="`${avatarId}-lid-${i}`"
            v-show="eye.lidStyle"
            data-lid
            class="avatar-lid"
            :style="eye.lidStyle"
          />
        </template>
      </span>
    </span>
  </span>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ avatarId: string; name: string }>()
const root = ref<HTMLElement | null>(null)
const stage = ref<HTMLElement | null>(null)
const head = ref<HTMLElement | null>(null)
const source = computed(() => `/avatars/${props.avatarId}-full.webp`)

const CANVAS = 1254
const pct = (px: number) => (px / CANVAS) * 100
const necklines: Record<string, number> = { atlas: 49, nova: 57, pixel: 51, orion: 56 }
const layerStyle = computed(() => ({ '--neck': `${necklines[props.avatarId] ?? 55}%` }))

interface EyeDef {
  x: number
  y: number
  rx: number
  ry: number
  lid?: { x: number; y: number; rx: number; ry: number; color: string }
}
interface EyeConfig {
  eyes: EyeDef[]
  zoom: number
  range: number
  squashBlink?: boolean
}

const EYES: Record<string, EyeConfig> = {
  atlas: {
    zoom: 1.2,
    range: 16,
    eyes: [
      { x: 490, y: 452, rx: 82, ry: 82, lid: { x: 490, y: 452, rx: 89, ry: 89, color: '#f5e9d4' } },
      { x: 755, y: 455, rx: 84, ry: 84, lid: { x: 755, y: 455, rx: 91, ry: 91, color: '#f5e9d4' } }
    ]
  },
  nova: {
    zoom: 1,
    range: 14,
    eyes: [
      { x: 442, y: 412, rx: 70, ry: 70, lid: { x: 442, y: 412, rx: 66, ry: 66, color: '#f9a2c1' } },
      { x: 785, y: 452, rx: 70, ry: 70, lid: { x: 785, y: 452, rx: 67, ry: 67, color: '#f9a2c1' } }
    ]
  },
  pixel: {
    zoom: 1.3,
    range: 9,
    eyes: [
      { x: 583, y: 393, rx: 38, ry: 38, lid: { x: 572, y: 388, rx: 58, ry: 52, color: '#ee7a23' } },
      { x: 782, y: 420, rx: 38, ry: 38, lid: { x: 793, y: 421, rx: 58, ry: 52, color: '#ee7a23' } }
    ]
  },
  orion: {
    zoom: 1,
    range: 24,
    squashBlink: true,
    eyes: [
      { x: 531, y: 472, rx: 90, ry: 55 },
      { x: 798, y: 452, rx: 90, ry: 55 }
    ]
  }
}

const eyeConfig = computed(() => EYES[props.avatarId])

const eyeLayers = computed(() => {
  const config = eyeConfig.value
  if (!config) return null
  return config.eyes.map((eye) => {
    const at = `${pct(eye.x)}% ${pct(eye.y)}%`
    const clip = eye.rx === eye.ry
      ? `circle(${pct(eye.rx)}% at ${at})`
      : `ellipse(${pct(eye.rx)}% ${pct(eye.ry)}% at ${at})`
    return {
      clip,
      imgStyle: { transformOrigin: at, scale: String(config.zoom) },
      lidStyle: eye.lid
        ? {
            left: `${pct(eye.lid.x)}%`,
            top: `${pct(eye.lid.y)}%`,
            width: `${pct(eye.lid.rx * 2)}%`,
            height: `${pct(eye.lid.ry * 2)}%`,
            background: eye.lid.color
          }
        : null
    }
  })
})

interface Idle { ty: number; rot: number; sx: number; sy: number; hr: number; hp: number; hy: number; hty: number }
interface Profile { yaw: number; pitch: number; roll: number; shift: number; speed: number; idle: (t: number) => Idle }
const { sin, abs } = Math

const PROFILES: Record<string, Profile> = {
  atlas: {
    yaw: 16, pitch: 8, roll: 4, shift: 1.2, speed: 5,
    idle: (t) => ({
      ty: 0, rot: 0, sx: 1 + 0.008 * sin(t * 1.1), sy: 1 + 0.014 * sin(t * 1.1),
      hr: 2.8 * sin(t * 0.9), hp: 1.5 * sin(t * 0.55), hy: 3 * sin(t * 0.4), hty: 0
    })
  },
  orion: {
    yaw: 20, pitch: 9, roll: 3, shift: 1.2, speed: 8,
    idle: (t) => ({
      ty: -1.8 * sin(t * 1.9) - 0.8, rot: 1.4 * sin(t * 0.95), sx: 1, sy: 1,
      hr: 2 * sin(t * 1.9 + 1), hp: 2 * sin(t * 1.9 + 0.6), hy: 4 * sin(t * 0.7), hty: -0.5 * sin(t * 1.9 + 1)
    })
  },
  pixel: {
    yaw: 20, pitch: 10, roll: 4, shift: 1.2, speed: 12,
    idle: (t) => {
      const b = abs(sin(t * 2.75))
      return {
        ty: -b * 2.4, rot: 1.6 * sin(t * 2.75), sx: 1 - 0.02 * b, sy: 1 + 0.03 * b,
        hr: 4 * sin(t * 2.75 + 0.8), hp: 3 * sin(t * 5.5 + 0.5), hy: 5 * sin(t * 1.4), hty: -0.6 * b
      }
    }
  },
  nova: {
    yaw: 18, pitch: 9, roll: 4, shift: 1.2, speed: 7,
    idle: (t) => ({
      ty: 0, rot: 0, sx: 1 + 0.006 * sin(t * 1.4), sy: 1 + 0.012 * sin(t * 1.4),
      hr: 3 * sin(t * 0.7) + 1 * sin(t * 1.9), hp: 3 * sin(t * 1.3 + 1), hy: 6 * sin(t * 0.55), hty: 0.3 * sin(t * 1.4)
    })
  }
}
const FALLBACK_PROFILE = PROFILES.nova as Profile

let frame = 0
let lastTime = 0
let pointer: { x: number; y: number } | null = null
let motionQuery: MediaQueryList | undefined
let mouseQuery: MediaQueryList | undefined
let blinkTimer = 0
let blinkTimer2 = 0

const cur = { hx: 0, hy: 0, ex: 0, ey: 0, idle: 1 }
const glance = { x: 0, y: 0, until: 0 }

const clamp = (value: number, limit = 1) => Math.max(-limit, Math.min(limit, value))
const ease = (rate: number, dt: number) => 1 - Math.exp(-rate * dt)

function applyNeutral() {
  stage.value?.style.setProperty('transform', 'none')
  head.value?.style.setProperty('transform', 'none')
  head.value?.style.setProperty('--ex', '0')
  head.value?.style.setProperty('--ey', '0')
}

function tick(now: number) {
  frame = requestAnimationFrame(tick)
  const stageEl = stage.value
  const headEl = head.value
  const rootEl = root.value
  if (!stageEl || !headEl || !rootEl) return
  const dt = Math.min(0.05, (now - lastTime) / 1000 || 0.016)
  lastTime = now
  const t = now / 1000
  const profile = PROFILES[props.avatarId] ?? FALLBACK_PROFILE
  const config = eyeConfig.value

  let gazeX = 0
  let gazeY = 0
  let headX = 0
  let headY = 0
  if (pointer) {
    const b = rootEl.getBoundingClientRect()
    if (b.width && b.height) {
      gazeX = clamp((pointer.x - b.left - b.width / 2) / 260)
      gazeY = clamp((pointer.y - b.top - b.height * 0.33) / 260)
      headX = gazeX
      headY = gazeY
    }
  } else {
    if (now > glance.until) {
      const centre = Math.random() < 0.35
      glance.x = centre ? 0 : (Math.random() * 2 - 1) * 0.9
      glance.y = centre ? 0 : (Math.random() * 2 - 1) * 0.5
      glance.until = now + 1200 + Math.random() * 2600
    }
    gazeX = glance.x
    gazeY = glance.y
    headX = glance.x * 0.35
    headY = glance.y * 0.35
  }

  cur.ex += (gazeX - cur.ex) * ease(22, dt)
  cur.ey += (gazeY - cur.ey) * ease(22, dt)
  cur.hx += (headX - cur.hx) * ease(profile.speed, dt)
  cur.hy += (headY - cur.hy) * ease(profile.speed, dt)
  cur.idle += ((pointer ? 0.45 : 1) - cur.idle) * ease(3, dt)

  const idle = profile.idle(t)
  const k = cur.idle
  stageEl.style.transform =
    `translateY(${idle.ty * k}%) rotate(${idle.rot * k}deg) scale(${1 + (idle.sx - 1) * k}, ${1 + (idle.sy - 1) * k})`
  headEl.style.transform =
    `perspective(500px) translate3d(${cur.hx * profile.shift}%, ${idle.hty * k - cur.hy * 0.6}%, 0) ` +
    `rotateX(${-cur.hy * profile.pitch + idle.hp * k}deg) ` +
    `rotateY(${cur.hx * profile.yaw + idle.hy * k}deg) ` +
    `rotateZ(${cur.hx * profile.roll + idle.hr * k}deg)`

  if (config) {
    headEl.style.setProperty('--ex', String(pct(cur.ex * config.range)))
    headEl.style.setProperty('--ey', String(pct(cur.ey * config.range * 0.7)))
  }
}

function startLoop() {
  if (frame || motionQuery?.matches || document.hidden) return
  lastTime = performance.now()
  frame = requestAnimationFrame(tick)
}

function stopLoop() {
  cancelAnimationFrame(frame)
  frame = 0
}

function reset() {
  pointer = null
}

function syncMotionPreference() {
  reset()
  stopLoop()
  clearTimeout(blinkTimer)
  clearTimeout(blinkTimer2)
  if (motionQuery?.matches) {
    applyNeutral()
  } else {
    startLoop()
    scheduleBlink()
  }
}

function follow(event: PointerEvent) {
  if (event.pointerType !== 'mouse' || motionQuery?.matches || !mouseQuery?.matches) return
  pointer = { x: event.clientX, y: event.clientY }
}

function handleVisibility() {
  if (document.hidden) {
    reset()
    stopLoop()
  } else {
    startLoop()
  }
}

function blink() {
  const el = root.value
  if (!el || motionQuery?.matches || document.hidden) return
  const timing: KeyframeAnimationOptions = { duration: 210, easing: 'ease-in-out' }
  el.querySelectorAll<HTMLElement>('[data-lid]').forEach((lid) => {
    lid.animate(
      [
        { clipPath: 'inset(0 0 100% 0)' },
        { clipPath: 'inset(0 0 0% 0)', offset: 0.4 },
        { clipPath: 'inset(0 0 100% 0)' }
      ],
      timing
    )
  })
  if (eyeConfig.value?.squashBlink) {
    el.querySelectorAll<HTMLElement>('[data-eye-img]').forEach((img) => {
      img.animate(
        [{ scale: '1 1' }, { scale: '1 0.06', offset: 0.4 }, { scale: '1 1' }],
        timing
      )
    })
  }
}

function scheduleBlink() {
  clearTimeout(blinkTimer)
  blinkTimer = window.setTimeout(() => {
    blink()
    if (Math.random() < 0.18) blinkTimer2 = window.setTimeout(blink, 280)
    scheduleBlink()
  }, 2200 + Math.random() * 3800)
}

watch(() => props.avatarId, reset)

onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  mouseQuery = window.matchMedia('(any-hover: hover) and (any-pointer: fine)')
  motionQuery.addEventListener('change', syncMotionPreference)
  mouseQuery.addEventListener('change', reset)
  window.addEventListener('pointermove', follow, { passive: true })
  window.addEventListener('blur', reset)
  window.addEventListener('scroll', reset, { passive: true })
  document.documentElement.addEventListener('pointerleave', reset)
  document.addEventListener('visibilitychange', handleVisibility)
  syncMotionPreference()
})

onBeforeUnmount(() => {
  reset()
  stopLoop()
  clearTimeout(blinkTimer)
  clearTimeout(blinkTimer2)
  motionQuery?.removeEventListener('change', syncMotionPreference)
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
  pointer-events: none;
}
.avatar-stage,
.avatar-head,
.avatar-eye {
  position: absolute;
  inset: 0;
  display: block;
}
.avatar-stage {
  transform-origin: 50% 92%;
  will-change: transform;
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
  mask-image: linear-gradient(to bottom, transparent calc(var(--neck) - 6%), #000 calc(var(--neck) - 6%));
}
.avatar-head {
  transform-origin: 50% var(--neck);
  will-change: transform;
}
.avatar-head-img {
  mask-image: linear-gradient(to bottom, #000 calc(var(--neck) - 1%), transparent calc(var(--neck) + 1%));
}
.avatar-eye img {
  translate: calc(var(--ex, 0) * 1%) calc(var(--ey, 0) * 1%);
}
.avatar-lid {
  position: absolute;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  clip-path: inset(0 0 100% 0);
  box-shadow: inset 0 -0.35em 0 -0.15em rgba(60, 30, 20, 0.35);
}
@media (prefers-reduced-motion: reduce) {
  .avatar-stage,
  .avatar-head { transform: none; }
  .avatar-eye,
  .avatar-lid { display: none; }
}
</style>
