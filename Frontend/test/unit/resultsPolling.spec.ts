import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import WaitingPage from '../../app/pages/espera.vue'
import { EVALUATION_UUID_KEY } from '../../app/utils/evaluationStorage'
import type { GetResultsResponseDTO } from '../../app/types/api'

const { router } = vi.hoisted(() => ({ router: { replace: vi.fn() } }))
vi.mock('vue-router', () => ({ useRouter: () => router }))
vi.mock('../../app/composables/useMotionPresets', () => ({
  useMotionPresets: () => ({ breathe: { animate: {}, transition: {} } })
}))

const UUID = 'USER-evaluation-test'
const fetchMock = vi.fn()
let wrapper: VueWrapper | undefined

function mountPage() {
  wrapper = mount(WaitingPage, {
    global: {
      stubs: {
        Motion: { template: '<div><slot /></div>' },
        TrackingAvatar: true,
        AvatarCompanion: true
      }
    }
  })
  return wrapper
}

beforeEach(() => {
  vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
  setActivePinia(createPinia())
  localStorage.clear()
  localStorage.setItem(EVALUATION_UUID_KEY, UUID)
  fetchMock.mockReset()
  router.replace.mockReset()
  vi.stubGlobal('$fetch', fetchMock)
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { apiBase: 'http://localhost:8000' } }))
  vi.stubGlobal('useHead', vi.fn())
})

afterEach(() => {
  wrapper?.unmount()
  wrapper = undefined
  localStorage.clear()
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

describe('estado de la evaluación en /espera', () => {
  it.each([
    [1, 'Conociendo tus intereses'],
    [2, 'Buscando carreras afines a ti'],
    [3, 'Preparando tu recomendación']
  ])('muestra el estado %s recibido al entrar', async (statusId, label) => {
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: statusId })
    const page = mountPage()
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith(`http://localhost:8000/get-results/${UUID}`, expect.objectContaining({ method: 'GET' }))
    expect(page.get('.waiting-step.is-active').text()).toBe(label)
    expect(page.get('[aria-current="step"]').text()).toBe(label)
    expect(page.findAll('.waiting-step.is-done')).toHaveLength(Number(statusId) - 1)
    expect(router.replace).not.toHaveBeenCalled()
  })

  it('consulta cada 5 segundos, conserva la etapa hasta que cambie y termina con estado 4', async () => {
    for (const statusId of [1, 1, 2, 3, 4]) {
      fetchMock.mockResolvedValueOnce({ user_uuid: UUID, status_id: statusId })
    }
    const page = mountPage()
    await flushPromises()

    await vi.advanceTimersByTimeAsync(4999)
    expect(fetchMock).toHaveBeenCalledTimes(1)
    await vi.advanceTimersByTimeAsync(1)
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(page.get('.waiting-step.is-active').text()).toBe('Conociendo tus intereses')

    await vi.advanceTimersByTimeAsync(5000)
    expect(page.get('.waiting-step.is-active').text()).toBe('Buscando carreras afines a ti')
    await vi.advanceTimersByTimeAsync(5000)
    expect(page.get('.waiting-step.is-active').text()).toBe('Preparando tu recomendación')
    expect(router.replace).not.toHaveBeenCalled()
    await vi.advanceTimersByTimeAsync(5000)
    expect(router.replace).toHaveBeenCalledExactlyOnceWith('/resultados')
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)

    await vi.advanceTimersByTimeAsync(15000)
    expect(fetchMock).toHaveBeenCalledTimes(5)
    expect(vi.getTimerCount()).toBe(0)
  })

  it('abre resultados cuando el proceso ya terminó antes de entrar', async () => {
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 4 })
    mountPage()
    await flushPromises()

    expect(router.replace).toHaveBeenCalledExactlyOnceWith('/resultados')
    expect(vi.getTimerCount()).toBe(0)
  })

  it('conserva el último estado y vuelve a consultar después de un error', async () => {
    fetchMock.mockResolvedValueOnce({ user_uuid: UUID, status_id: 2 })
      .mockRejectedValueOnce(new Error('Sin conexión'))
      .mockResolvedValueOnce({ user_uuid: UUID, status_id: 3 })
    const page = mountPage()
    await flushPromises()

    await vi.advanceTimersByTimeAsync(5000)
    expect(page.get('.waiting-step.is-active').text()).toBe('Buscando carreras afines a ti')
    expect(page.text()).toContain('Volveremos a intentarlo')
    expect(router.replace).not.toHaveBeenCalled()

    await vi.advanceTimersByTimeAsync(5000)
    expect(page.get('.waiting-step.is-active').text()).toBe('Preparando tu recomendación')
    expect(page.text()).not.toContain('Volveremos a intentarlo')
  })

  it('evita solicitudes simultáneas y cancela la consulta al salir sin navegar con una respuesta tardía', async () => {
    let resolve!: (result: GetResultsResponseDTO) => void
    fetchMock.mockReturnValue(new Promise<GetResultsResponseDTO>((done) => { resolve = done }))
    mountPage()
    const signal = fetchMock.mock.calls[0]![1].signal as AbortSignal

    await vi.advanceTimersByTimeAsync(10000)
    expect(fetchMock).toHaveBeenCalledTimes(1)
    wrapper!.unmount()
    wrapper = undefined
    expect(signal.aborted).toBe(true)
    expect(vi.getTimerCount()).toBe(0)

    resolve({ user_uuid: UUID, status_id: 4 })
    await flushPromises()
    expect(router.replace).not.toHaveBeenCalled()
  })

  it('detiene las consultas si se elimina el UUID desde otra pestaña', async () => {
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 1 })
    mountPage()
    await flushPromises()
    localStorage.removeItem(EVALUATION_UUID_KEY)
    window.dispatchEvent(new StorageEvent('storage', { key: EVALUATION_UUID_KEY, newValue: null }))

    await vi.advanceTimersByTimeAsync(10000)
    expect(router.replace).toHaveBeenCalledExactlyOnceWith('/riasec')
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(vi.getTimerCount()).toBe(0)
  })

  it('no consulta sin un UUID guardado', () => {
    localStorage.removeItem(EVALUATION_UUID_KEY)
    mountPage()

    expect(fetchMock).not.toHaveBeenCalled()
    expect(router.replace).toHaveBeenCalledExactlyOnceWith('/riasec')
    expect(vi.getTimerCount()).toBe(0)
  })

  it.each([
    { user_uuid: 'USER-otra-evaluacion', status_id: 4 },
    { user_uuid: UUID, status_id: 5 },
    null
  ])('no avanza con una respuesta inválida: %j', async (response) => {
    fetchMock.mockResolvedValue(response)
    const page = mountPage()
    await flushPromises()

    expect(page.find('.waiting-step.is-active').exists()).toBe(false)
    expect(page.text()).toContain('Volveremos a intentarlo')
    expect(router.replace).not.toHaveBeenCalled()
  })
})
