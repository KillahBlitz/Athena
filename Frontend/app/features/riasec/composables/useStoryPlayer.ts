import { computed, onScopeDispose, ref, watch } from 'vue'
import type { Ref } from 'vue'

interface StoryPlayerOptions {
  sceneCount: number
  intervalMs?: number
  canAutoplay: Ref<boolean>
  loop?: boolean
}

export function useStoryPlayer({ sceneCount, intervalMs = 6000, canAutoplay, loop = false }: StoryPlayerOptions) {
  const scene = ref(0)
  const isLast = computed(() => scene.value >= sceneCount - 1)
  let timer: ReturnType<typeof setTimeout> | null = null

  const clear = () => {
    if (timer !== null) clearTimeout(timer)
    timer = null
  }

  const schedule = () => {
    clear()
    if (!canAutoplay.value || (isLast.value && !loop)) return
    timer = setTimeout(() => {
      timer = null
      scene.value = isLast.value ? 0 : scene.value + 1
    }, intervalMs)
  }

  const goTo = (index: number) => {
    const target = Math.max(0, Math.min(index, sceneCount - 1))
    if (target === scene.value) schedule()
    else scene.value = target
  }

  watch([scene, canAutoplay], schedule, { immediate: true, flush: 'sync' })
  onScopeDispose(clear)

  return {
    scene,
    isLast,
    next: () => goTo(scene.value + 1),
    prev: () => goTo(scene.value - 1),
    react: () => goTo(scene.value + 1)
  }
}
