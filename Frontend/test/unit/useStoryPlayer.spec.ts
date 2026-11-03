import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { effectScope, nextTick, ref } from 'vue'
import { useStoryPlayer } from '../../app/features/riasec/composables/useStoryPlayer'

function setup(canAutoplayInitial = true) {
  const canAutoplay = ref(canAutoplayInitial)
  const scope = effectScope()
  const player = scope.run(() => useStoryPlayer({ sceneCount: 3, intervalMs: 6000, canAutoplay }))!
  return { player, canAutoplay, scope }
}

describe('useStoryPlayer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('avanza a los 6000 ms y no antes', async () => {
    const { player } = setup()

    vi.advanceTimersByTime(5999)
    expect(player.scene.value).toBe(0)
    vi.advanceTimersByTime(1)

    expect(player.scene.value).toBe(1)
  })

  it('se detiene en la última escena sin volver a empezar', async () => {
    const { player } = setup()

    vi.advanceTimersByTime(6000)
    await nextTick()
    vi.advanceTimersByTime(6000)
    await nextTick()
    vi.advanceTimersByTime(60000)

    expect(player.scene.value).toBe(2)
    expect(player.isLast.value).toBe(true)
    expect(vi.getTimerCount()).toBe(0)
  })

  it('no avanza mientras no se pueda reproducir y continúa al permitirlo', async () => {
    const { player, canAutoplay } = setup(false)

    vi.advanceTimersByTime(20000)
    expect(player.scene.value).toBe(0)

    canAutoplay.value = true
    await nextTick()
    vi.advanceTimersByTime(6000)

    expect(player.scene.value).toBe(1)
  })

  it('pausar a mitad de intervalo cancela el avance pendiente', async () => {
    const { player, canAutoplay } = setup()

    vi.advanceTimersByTime(4000)
    canAutoplay.value = false
    await nextTick()
    vi.advanceTimersByTime(10000)

    expect(player.scene.value).toBe(0)
  })

  it('react avanza una escena y reinicia el temporizador', async () => {
    const { player } = setup()

    vi.advanceTimersByTime(5000)
    player.react()
    await nextTick()
    expect(player.scene.value).toBe(1)

    vi.advanceTimersByTime(5999)
    expect(player.scene.value).toBe(1)
    vi.advanceTimersByTime(1)
    expect(player.scene.value).toBe(2)
  })

  it('react y next no pasan de la última escena; prev no baja de la primera', async () => {
    const { player } = setup(false)

    player.prev()
    expect(player.scene.value).toBe(0)
    player.next()
    player.react()
    player.react()
    player.next()

    expect(player.scene.value).toBe(2)
  })

  it('no deja temporizadores al desmontar', () => {
    const { scope } = setup()
    expect(vi.getTimerCount()).toBe(1)

    scope.stop()

    expect(vi.getTimerCount()).toBe(0)
  })
})
