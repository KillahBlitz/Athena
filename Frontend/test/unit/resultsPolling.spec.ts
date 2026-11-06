import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import WaitingPage from '../../app/pages/espera.vue'
import { EVALUATION_UUID_KEY } from '../../app/utils/evaluationStorage'
import type { GetResultsResponseDTO } from '../../app/types/api'
import { useAthenaSessionStore } from '../../app/stores/athenaSession'
import { useRiasecForm } from '../../app/features/riasec/composables/useRiasecForm'

const { router } = vi.hoisted(() => ({ router: { replace: vi.fn(), push: vi.fn() } }))
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
        AvatarCompanion: true,
        BaseButton: {
          props: ['loading'],
          template: '<button :disabled="loading"><slot /></button>'
        }
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
  router.push.mockReset()
  vi.stubGlobal('$fetch', fetchMock)
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { apiBase: 'http://localhost:8000' } }))
  vi.stubGlobal('useHead', vi.fn())
})

afterEach(() => {
  wrapper?.unmount()
  wrapper = undefined
  localStorage.clear()
  vi.useRealTimers()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('estado de la evaluación en /espera', () => {
  it.each(['pending', 'error'])('ofrece reintentar después de 20 consultas terminadas: %s', async (mode) => {
    if (mode === 'error') fetchMock.mockRejectedValue(new Error('Sin conexión'))
    else fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 1 })
    const page = mountPage()
    await flushPromises()
    await vi.advanceTimersByTimeAsync(18 * 5000)
    expect(fetchMock).toHaveBeenCalledTimes(19)
    expect(page.find('.waiting-retry').exists()).toBe(false)

    await vi.advanceTimersByTimeAsync(5000)
    expect(fetchMock).toHaveBeenCalledTimes(20)
    expect(page.get('.waiting-retry button').text()).toBe('Reintentar evaluación')
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
    await vi.advanceTimersByTimeAsync(5000)
    expect(fetchMock).toHaveBeenCalledTimes(21)
  })

  it('conserva las respuestas tras reintentar y permite reenviarlas después de recargar', async () => {
    const session = useAthenaSessionStore()
    session.setAreaData({
      area_id: 1, nom_area: 'Área de prueba',
      objetivos: [{ id_objetivo: 101, id_carrera: 101, pregunta: 'Construir soluciones' }],
      preguntas: [1, 2].map(id => ({
        riasec_id: id, texto_pregunta: '¿Qué disfrutas?', pregunta_abierta: 'Cuéntanos',
        opciones: { [id * 10]: 'Reparar' }
      }))
    })
    session.$patch({
      name: 'Prueba', email: 'test@example.com', age: 20, selectedAreaId: 1,
      answers: { 101: { valoracion: 4, justificacion: 'Me interesa' } },
      riasecAnswers: {
        1: { opcionIds: [10], respuestaAbierta: 'Reparo aparatos' },
        2: { opcionIds: [20], respuestaAbierta: 'Investigo fallas' }
      }
    })
    session.persist()
    const originalPayload = structuredClone(session.saveUserPayload)
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 1 })
    const page = mountPage()
    await flushPromises()
    await vi.advanceTimersByTimeAsync(19 * 5000)

    // Una respuesta tardía de la consulta 21 no debe recuperar la evaluación anterior.
    let resolve!: (result: GetResultsResponseDTO) => void
    fetchMock.mockImplementationOnce(() => new Promise<GetResultsResponseDTO>(done => { resolve = done }))
    await vi.advanceTimersByTimeAsync(5000)
    const signal = fetchMock.mock.calls[20]![1].signal as AbortSignal
    await page.get('.waiting-retry button').trigger('click')
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBeNull()
    expect(session.saveUserPayload).toEqual(originalPayload)
    expect(signal.aborted).toBe(true)
    expect(vi.getTimerCount()).toBe(0)
    expect(router.replace).toHaveBeenCalledExactlyOnceWith('/riasec')
    resolve({ user_uuid: UUID, status_id: 4, results: [] })
    await flushPromises()
    expect(router.replace).toHaveBeenCalledTimes(1)

    page.unmount()
    wrapper = undefined
    setActivePinia(createPinia())
    let form!: ReturnType<typeof useRiasecForm>
    wrapper = mount({ setup() { form = useRiasecForm(); return () => null } })
    expect(useAthenaSessionStore().saveUserPayload).toEqual(originalPayload)
    expect(form.isLastQuestion.value).toBe(true)
    expect(form.isCurrentComplete.value).toBe(true)
    fetchMock.mockResolvedValueOnce('USER-retry')
    await form.handleFinish()
    expect(fetchMock).toHaveBeenLastCalledWith('http://localhost:8000/save-user', expect.objectContaining({
      method: 'POST', body: originalPayload
    }))
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe('USER-retry')
    expect(router.push).toHaveBeenCalledWith('/espera')
  })

  it('conserva el UUID y las consultas si no puede persistir las respuestas', async () => {
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 1 })
    const page = mountPage()
    await flushPromises()
    await vi.advanceTimersByTimeAsync(19 * 5000)
    const storage = localStorage
    vi.stubGlobal('localStorage', {
      getItem: storage.getItem.bind(storage),
      removeItem: storage.removeItem.bind(storage),
      clear: storage.clear.bind(storage),
      setItem: () => { throw new Error('Quota exceeded') }
    })
    await page.get('.waiting-retry button').trigger('click')
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
    expect(page.get('[role="alert"]').text()).toContain('No pudimos guardar tus respuestas')
    expect(router.replace).not.toHaveBeenCalled()
    await vi.advanceTimersByTimeAsync(5000)
    expect(fetchMock).toHaveBeenCalledTimes(21)
  })

  it('abre resultados sin ofrecer reintentar si la consulta 20 termina la evaluación', async () => {
    for (let i = 0; i < 19; i++) fetchMock.mockResolvedValueOnce({ user_uuid: UUID, status_id: 1 })
    fetchMock.mockResolvedValueOnce({ user_uuid: UUID, status_id: 4, results: [] })
    const page = mountPage()
    await flushPromises()
    await vi.advanceTimersByTimeAsync(19 * 5000)
    expect(page.find('.waiting-retry').exists()).toBe(false)
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
    expect(router.replace).toHaveBeenCalledExactlyOnceWith('/resultados')
  })

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

  it('guarda los resultados al llegar al estado 4 para no volver a esperar', async () => {
    const results = [{ top: 1, carrera_id: 10, carrera: 'Ingeniería', puntaje: 0.9, escuelas: ['ESCOM'] }]
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 4, results })
    mountPage()
    await flushPromises()

    expect(router.replace).toHaveBeenCalledExactlyOnceWith('/resultados')
    expect(JSON.parse(localStorage.getItem('athena_results_v1')!)).toEqual({ user_uuid: UUID, results })
  })

  it('no consulta la API si ya hay resultados cacheados y va directo a resultados', async () => {
    localStorage.setItem('athena_results_v1', JSON.stringify({
      user_uuid: UUID,
      results: [{ top: 1, carrera_id: 10, carrera: 'Ingeniería', puntaje: 0.9, escuelas: ['ESCOM'] }]
    }))
    mountPage()
    await flushPromises()

    expect(fetchMock).not.toHaveBeenCalled()
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
