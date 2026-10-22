import { computed, onScopeDispose, ref, watch } from 'vue'
import type { Ref } from 'vue'

interface StoryPlayerOptions {
  sceneCount: number
  intervalMs?: number
  canAutoplay: Ref<boolean>
}

export function useStoryPlayer({ sceneCount, intervalMs = 6000, canAutoplay }: StoryPlayerOptions) {
  const scene = ref(0)
  const isLast = computed(() => scene.value >= sceneCount - 1)
  let timer: ReturnType<typeof setTimeout> | null = null

  const clear = () => {
    if (timer !== null) clearTimeout(timer)
    timer = null
  }

  const schedule = () => {
    clear()
    if (!canAutoplay.value || isLast.value) return
    timer = setTimeout(() => {
      timer = null
      scene.value = Math.min(scene.value + 1, sceneCount - 1)
    }, intervalMs)
  }

  const goTo = (index: number) => {
    scene.value = Math.max(0, Math.min(index, sceneCount - 1))
    schedule()
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
